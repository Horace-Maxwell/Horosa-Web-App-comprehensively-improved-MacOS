Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Join-Path $Root 'Horosa-Web'

$PyPidFile = Join-Path $ProjectDir '.horosa_win_py.pid'
$JavaPidFile = Join-Path $ProjectDir '.horosa_win_java.pid'
$WebPidFile = Join-Path $ProjectDir '.horosa_win_web.pid'

$LogRoot = Join-Path $ProjectDir '.horosa-local-logs-win'
$RunTag = Get-Date -Format 'yyyyMMdd_HHmmss'
$LogDir = Join-Path $LogRoot $RunTag
$PyLog = Join-Path $LogDir 'astropy.log'
$JavaLog = Join-Path $LogDir 'astrostudyboot.log'
$WebLog = Join-Path $LogDir 'web.log'
$BrowserProfile = Join-Path $ProjectDir '.horosa-browser-profile-win'

$DistDir = Join-Path $ProjectDir 'astrostudyui/dist-file'
if (-not (Test-Path (Join-Path $DistDir 'index.html'))) {
  $DistDir = Join-Path $ProjectDir 'astrostudyui/dist'
}

$JarPath = Join-Path $ProjectDir 'astrostudysrv/astrostudyboot/target/astrostudyboot.jar'
$PythonBin = $null
$JavaBin = $null
$WebPort = if ($env:HOROSA_WEB_PORT) { [int]$env:HOROSA_WEB_PORT } else { 8000 }
$BackendPort = 9999
$ChartPort = 8899

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
New-Item -ItemType Directory -Force -Path $BrowserProfile | Out-Null

function Test-PortOpen {
  param([int]$Port)
  $client = $null
  try {
    $client = New-Object System.Net.Sockets.TcpClient
    $iar = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
    $ok = $iar.AsyncWaitHandle.WaitOne(300)
    if (-not $ok) { return $false }
    $client.EndConnect($iar) | Out-Null
    return $true
  } catch {
    return $false
  } finally {
    if ($client) { $client.Dispose() }
  }
}

function Get-PidFromFile {
  param([string]$Path)
  if (-not (Test-Path $Path)) { return $null }
  $raw = (Get-Content -Path $Path -Raw).Trim()
  if (-not $raw) { return $null }
  try { return [int]$raw } catch { return $null }
}

function Stop-PidFile {
  param([string]$Name, [string]$Path)
  $procId = Get-PidFromFile -Path $Path
  if ($procId) {
    try {
      Stop-Process -Id $procId -Force -ErrorAction Stop
      Write-Host "$Name stopped pid $procId"
    } catch {
      Write-Host "$Name pid $procId not running"
    }
  }
  if (Test-Path $Path) { Remove-Item -Force $Path }
}

function Cleanup-All {
  Stop-PidFile -Name 'web' -Path $WebPidFile
  Stop-PidFile -Name 'java' -Path $JavaPidFile
  Stop-PidFile -Name 'python' -Path $PyPidFile
}

function Start-Background {
  param(
    [string]$FilePath,
    [string[]]$Arguments,
    [string]$LogPath,
    [string]$PidFile
  )

  $ErrPath = "$LogPath.err"
  $proc = Start-Process -FilePath $FilePath `
                        -ArgumentList $Arguments `
                        -PassThru `
                        -WindowStyle Hidden `
                        -RedirectStandardOutput $LogPath `
                        -RedirectStandardError $ErrPath
  Set-Content -Path $PidFile -Value $proc.Id -NoNewline
  return $proc
}

function Quote-Arg {
  param([string]$Value)
  if ($null -eq $Value) { return '""' }
  '"' + ($Value -replace '"', '\\"') + '"'
}

function Resolve-Browser {
  $candidates = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "$env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles(x86)\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\BraveSoftware\Brave-Browser\Application\brave.exe",
    "$env:ProgramFiles(x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
    "$env:LocalAppData\Chromium\Application\chrome.exe"
  )
  foreach ($p in $candidates) {
    if ($p -and (Test-Path $p)) { return $p }
  }
  return $null
}

function Test-JavaAtLeast17 {
  param([string]$JavaCmdOrPath)
  try {
    $out = & $JavaCmdOrPath -version 2>&1 | Out-String
    if (-not $out) { return $false }
    $m = [regex]::Match($out, 'version\s+"([^"]+)"')
    if (-not $m.Success) { return $false }
    $v = $m.Groups[1].Value
    if ($v.StartsWith('1.')) { return $false }
    $majorText = ($v -split '[\.\-_]')[0]
    $major = 0
    if (-not [int]::TryParse($majorText, [ref]$major)) { return $false }
    return ($major -ge 17)
  } catch {
    return $false
  }
}

function Test-PythonSupported {
  param([string]$PythonCmdOrPath)
  try {
    $out = & $PythonCmdOrPath -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
    if (-not $out) { return $false }
    $v = ($out | Select-Object -First 1).ToString().Trim()
    $parts = $v.Split('.')
    if ($parts.Length -lt 2) { return $false }
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    # Force Python 3.11 for best pyswisseph compatibility on Windows.
    return ($major -eq 3 -and $minor -eq 11)
  } catch {
    return $false
  }
}

function Resolve-Java {
  $runtimeJava = Join-Path $Root 'runtime/windows/java/bin/java.exe'
  if (Test-Path $runtimeJava) {
    return $runtimeJava
  }

  if ($env:HOROSA_JAVA -and (Test-Path $env:HOROSA_JAVA)) {
    if (Test-JavaAtLeast17 -JavaCmdOrPath $env:HOROSA_JAVA) { return $env:HOROSA_JAVA }
  }

  if ($env:JAVA_HOME) {
    $javaHomeBin = Join-Path $env:JAVA_HOME 'bin/java.exe'
    if (Test-Path $javaHomeBin) {
      if (Test-JavaAtLeast17 -JavaCmdOrPath $javaHomeBin) { return $javaHomeBin }
    }
  }

  $bundled = @(
    (Join-Path $Root 'runtime/windows/java/bin/java.exe'),
    (Join-Path $Root 'runtime/java/bin/java.exe'),
    (Join-Path $Root 'jre/bin/java.exe'),
    (Join-Path $ProjectDir 'runtime/windows/java/bin/java.exe'),
    (Join-Path $ProjectDir 'runtime/java/bin/java.exe'),
    (Join-Path $ProjectDir 'jre/bin/java.exe')
  )
  foreach ($p in $bundled) {
    if (Test-Path $p) {
      if (Test-JavaAtLeast17 -JavaCmdOrPath $p) { return $p }
    }
  }

  $inPath = Get-Command 'java' -ErrorAction SilentlyContinue
  if ($inPath) {
    if (Test-JavaAtLeast17 -JavaCmdOrPath 'java') { return 'java' }
  }

  $javaCandidates = @(
    "$env:ProgramFiles\Java",
    "$env:ProgramFiles\Eclipse Adoptium",
    "$env:ProgramFiles\Microsoft",
    "$env:ProgramFiles\Zulu",
    "$env:ProgramFiles\Amazon Corretto",
    "$env:ProgramFiles(x86)\Java",
    "$env:ProgramFiles(x86)\Eclipse Adoptium",
    "$env:LocalAppData\Programs\Eclipse Adoptium",
    "$env:LocalAppData\Programs\Microsoft"
  )
  foreach ($base in $javaCandidates) {
    if (-not (Test-Path $base)) { continue }
    $found = Get-ChildItem -Path $base -Directory -ErrorAction SilentlyContinue |
      Sort-Object LastWriteTime -Descending |
      Where-Object { Test-Path (Join-Path $_.FullName 'bin\java.exe') } |
      Select-Object -First 1
    if ($found) {
      $candidate = Join-Path $found.FullName 'bin\java.exe'
      if (Test-Path $candidate) {
        if (Test-JavaAtLeast17 -JavaCmdOrPath $candidate) { return $candidate }
      }
    }
  }

  $deepSearchRoots = @(
    "$env:LocalAppData\Microsoft\WinGet\Packages",
    "$env:ProgramFiles\Microsoft",
    "$env:ProgramFiles\Eclipse Adoptium"
  )
  foreach ($root in $deepSearchRoots) {
    if (-not (Test-Path $root)) { continue }
    $matches = Get-ChildItem -Path $root -Recurse -Filter java.exe -ErrorAction SilentlyContinue |
      Where-Object { $_.FullName -match 'jdk|jre|openjdk|temurin|corretto|zulu|microsoft' } |
      Select-Object -First 20
    foreach ($m in $matches) {
      if (Test-JavaAtLeast17 -JavaCmdOrPath $m.FullName) {
        return $m.FullName
      }
    }
  }

  return $null
}

function Resolve-Python {
  if ($env:HOROSA_PYTHON -and (Test-Path $env:HOROSA_PYTHON)) {
    if (Test-PythonSupported -PythonCmdOrPath $env:HOROSA_PYTHON) { return $env:HOROSA_PYTHON }
  }

  $bundled = @(
    (Join-Path $Root 'runtime/windows/python/python.exe'),
    (Join-Path $Root 'runtime/windows/python/python3.exe'),
    (Join-Path $Root 'runtime/python/python.exe'),
    (Join-Path $ProjectDir 'runtime/windows/python/python.exe'),
    (Join-Path $ProjectDir 'runtime/windows/python/python3.exe'),
    (Join-Path $ProjectDir 'runtime/python/python.exe')
  )
  foreach ($p in $bundled) {
    if (Test-Path $p) {
      if (Test-PythonSupported -PythonCmdOrPath $p) { return $p }
    }
  }

  $installed = @(
    "$env:LocalAppData\Programs\Python\Python311\python.exe",
    "$env:LocalAppData\Programs\Python\Python312\python.exe",
    "$env:ProgramFiles\Python312\python.exe",
    "$env:ProgramFiles\Python311\python.exe",
    'C:\Python311\python.exe',
    'C:\Python312\python.exe'
  )
  foreach ($p in $installed) {
    if (Test-Path $p) {
      if (Test-PythonSupported -PythonCmdOrPath $p) { return $p }
    }
  }

  $inPath = Get-Command 'python' -ErrorAction SilentlyContinue
  if ($inPath) {
    if (Test-PythonSupported -PythonCmdOrPath 'python') { return 'python' }
  }

  return $null
}

function Install-WithWinget {
  param(
    [string]$PackageId,
    [string]$DisplayName
  )
  $winget = Get-Command 'winget' -ErrorAction SilentlyContinue
  if (-not $winget) {
    Write-Host "winget not found, cannot auto-install $DisplayName."
    return $false
  }

  Write-Host "Auto installing $DisplayName via winget..."
  $attempts = @(
    @('install','-e','--id', $PackageId, '--scope','user','--source','winget','--accept-package-agreements','--accept-source-agreements','--silent'),
    @('install','-e','--id', $PackageId, '--accept-package-agreements','--accept-source-agreements','--silent')
  )
  foreach ($args in $attempts) {
    try {
      $p = Start-Process -FilePath $winget.Source -ArgumentList $args -Wait -PassThru
      if ($p.ExitCode -eq 0) { return $true }
      Write-Host ("winget install exit code for {0}: {1}" -f $DisplayName, $p.ExitCode)
    } catch {
      Write-Host ("Auto install failed for {0}: {1}" -f $DisplayName, $_.Exception.Message)
    }
  }
  return $false
}

function Install-Java17 {
  $candidates = @(
    @{ Id = 'EclipseAdoptium.Temurin.17.JDK'; Name = 'Java 17 (Temurin JDK)' },
    @{ Id = 'EclipseAdoptium.Temurin.17.JRE'; Name = 'Java 17 (Temurin JRE)' },
    @{ Id = 'Microsoft.OpenJDK.17'; Name = 'Java 17 (Microsoft OpenJDK)' }
  )
  foreach ($c in $candidates) {
    if (Install-WithWinget -PackageId $c.Id -DisplayName $c.Name) {
      Start-Sleep -Seconds 2
      $resolved = Resolve-Java
      if ($resolved) {
        Write-Host ("[OK] Java 17 detected: {0}" -f $resolved)
        return $true
      }
      Write-Host ("[WARN] {0} reported success but Java 17 was not detected. Trying next option..." -f $c.Name)
    }
  }
  if (Install-Java17Portable) {
    $resolvedPortable = Resolve-Java
    if ($resolvedPortable) {
      Write-Host ("[OK] Portable Java 17 ready: {0}" -f $resolvedPortable)
      return $true
    }
  }
  return $false
}

function Install-Java17Portable {
  try {
    Write-Host 'winget install failed, trying portable Java 17 download...'
    $portableRoot = Join-Path $Root 'runtime/windows'
    $javaTarget = Join-Path $portableRoot 'java'
    $tmpDir = Join-Path $env:TEMP ('horosa_java17_' + [DateTime]::Now.ToString('yyyyMMdd_HHmmss'))
    $zipPath = Join-Path $tmpDir 'java17.zip'
    New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null
    New-Item -ItemType Directory -Force -Path $portableRoot | Out-Null

    $url = 'https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jre/hotspot/normal/eclipse?project=jdk'
    Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing

    $extractDir = Join-Path $tmpDir 'extract'
    Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force

    # Robustly locate java.exe regardless of archive folder layout.
    $javaExe = Get-ChildItem -Path $extractDir -Recurse -Filter java.exe -File -ErrorAction SilentlyContinue |
      Where-Object { $_.FullName -match '\\bin\\java\.exe$' } |
      Select-Object -First 1
    if (-not $javaExe) {
      Write-Host '[WARN] Portable archive extracted but java.exe not found.'
      return $false
    }
    $javaHomePath = Split-Path -Parent (Split-Path -Parent $javaExe.FullName)

    if (Test-Path $javaTarget) { Remove-Item -Recurse -Force $javaTarget }
    New-Item -ItemType Directory -Force -Path $javaTarget | Out-Null
    robocopy $javaHomePath $javaTarget /E /NFL /NDL /NJH /NJS /NP | Out-Null

    $ok = Test-Path (Join-Path $javaTarget 'bin\java.exe')
    if (-not $ok) {
      Write-Host '[WARN] Portable Java copy finished but bin\java.exe is still missing.'
    }
    return $ok
  } catch {
    Write-Host ("Portable Java download failed: {0}" -f $_.Exception.Message)
    return $false
  }
}

function Get-ExePath {
  param([string]$CmdOrPath)
  if (-not $CmdOrPath) { return $null }
  if (Test-Path $CmdOrPath) { return (Resolve-Path $CmdOrPath).Path }
  $cmd = Get-Command $CmdOrPath -ErrorAction SilentlyContinue
  if ($cmd -and $cmd.Source) { return $cmd.Source }
  return $null
}

function Sync-RuntimeFromExe {
  param(
    [string]$ExeCmdOrPath,
    [string]$TargetDir,
    [int]$UpLevels = 1,
    [string]$CheckRelative = ''
  )
  $exe = Get-ExePath -CmdOrPath $ExeCmdOrPath
  if (-not $exe) { return $false }

  $src = Split-Path -Parent $exe
  for ($i = 0; $i -lt $UpLevels; $i++) {
    $src = Split-Path -Parent $src
  }
  if (-not (Test-Path $src)) { return $false }

  if (Test-Path $TargetDir) { Remove-Item -Recurse -Force $TargetDir }
  New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
  robocopy $src $TargetDir /E /NFL /NDL /NJH /NJS /NP | Out-Null

  if (-not $CheckRelative) { return $true }
  return (Test-Path (Join-Path $TargetDir $CheckRelative))
}

function Ensure-PythonRuntimeDeps {
  param(
    [string]$PythonExe,
    [string]$ProjectRoot
  )
  try {
    & $PythonExe -c "import cherrypy, jsonpickle, swisseph; print('ok')" *> $null
    if ($LASTEXITCODE -eq 0) {
      Write-Host 'Python dependencies already satisfied, skip install.'
      return $true
    }
  } catch {
    # continue to install
  }

  try {
    Write-Host 'Installing Python dependencies for local runtime...'
    & $PythonExe -m pip install --disable-pip-version-check --no-input cherrypy jsonpickle
    if ($LASTEXITCODE -ne 0) { return $false }
    & $PythonExe -m pip install --disable-pip-version-check --no-input --only-binary=:all: pyswisseph
    return ($LASTEXITCODE -eq 0)
  } catch {
    Write-Host ("Python dependency install failed: {0}" -f $_.Exception.Message)
    return $false
  }
}

if (-not (Test-Path $ProjectDir)) {
  Write-Host "Project folder not found: $ProjectDir"
  Read-Host 'Press Enter to exit'
  exit 1
}

if (-not (Test-Path (Join-Path $DistDir 'index.html'))) {
  Write-Host "Frontend static file missing: $DistDir\index.html"
  Write-Host "Build first: cd \"$ProjectDir\\astrostudyui\" && npm run build:file"
  Read-Host 'Press Enter to exit'
  exit 1
}

if (-not (Test-Path $JarPath)) {
  Write-Host "Backend jar missing: $JarPath"
  Write-Host 'Build backend jar first.'
  Read-Host 'Press Enter to exit'
  exit 1
}

$PythonBin = Resolve-Python
if (-not $PythonBin) {
  $installed = Install-WithWinget -PackageId 'Python.Python.3.11' -DisplayName 'Python 3.11'
  if ($installed) {
    $PythonBin = Resolve-Python
  }
  if (-not $PythonBin) {
    Write-Host 'Python 3.11 not found.'
    Write-Host 'Install Python 3.11, then rerun this launcher.'
    Read-Host 'Press Enter to exit'
    exit 1
  }
}

$PyRuntimeDir = Join-Path $Root 'runtime/windows/python'
if (-not (Test-Path (Join-Path $PyRuntimeDir 'python.exe'))) {
  Write-Host 'Preparing local Python runtime for offline use...'
  $pySynced = Sync-RuntimeFromExe -ExeCmdOrPath $PythonBin -TargetDir $PyRuntimeDir -UpLevels 1 -CheckRelative 'python.exe'
  if ($pySynced) {
    $PythonBin = Join-Path $PyRuntimeDir 'python.exe'
    Write-Host "[OK] Local Python runtime ready: $PythonBin"
  } else {
    Write-Host '[WARN] Could not sync local Python runtime, will continue with system Python.'
  }
}

if (-not (Ensure-PythonRuntimeDeps -PythonExe $PythonBin -ProjectRoot $ProjectDir)) {
  Write-Host 'Python dependencies are incomplete. Startup aborted.'
  Read-Host 'Press Enter to exit'
  exit 1
}

$JavaBin = Resolve-Java
if (-not $JavaBin) {
  $installed = Install-Java17
  if ($installed) {
    $JavaBin = Resolve-Java
  }
  if (-not $JavaBin) {
    Write-Host 'Java 17+ not found.'
    Write-Host 'Install Java 17+, then rerun this launcher.'
    Read-Host 'Press Enter to exit'
    exit 1
  }
}

Write-Host ("Using Python: {0}" -f $PythonBin)
Write-Host ("Using Java: {0}" -f $JavaBin)

Cleanup-All

$oldPythonPath = $env:PYTHONPATH
if ($oldPythonPath) {
  $env:PYTHONPATH = (Join-Path $ProjectDir 'astropy') + ';' + $oldPythonPath
} else {
  $env:PYTHONPATH = (Join-Path $ProjectDir 'astropy')
}

try {
  Write-Host '[1/4] Starting local backend services...'

  $pyScript = Join-Path $ProjectDir 'astropy/websrv/webchartsrv.py'
  $null = Start-Background -FilePath $PythonBin -Arguments @(Quote-Arg $pyScript) -LogPath $PyLog -PidFile $PyPidFile

  $null = Start-Background -FilePath $JavaBin -Arguments @('-jar', (Quote-Arg $JarPath), "--astrosrv=http://127.0.0.1:$ChartPort", '--mongodb.ip=127.0.0.1', '--redis.ip=127.0.0.1') -LogPath $JavaLog -PidFile $JavaPidFile

  $ready = $false
  for ($i = 0; $i -lt 90; $i++) {
    $pyPid = Get-PidFromFile -Path $PyPidFile
    $javaPid = Get-PidFromFile -Path $JavaPidFile
    if (-not $pyPid -or -not $javaPid) { break }

    $pyAlive = Get-Process -Id $pyPid -ErrorAction SilentlyContinue
    $javaAlive = Get-Process -Id $javaPid -ErrorAction SilentlyContinue
    if (-not $pyAlive -or -not $javaAlive) { break }

    if ((Test-PortOpen -Port $ChartPort) -and (Test-PortOpen -Port $BackendPort)) {
      $ready = $true
      break
    }
    Start-Sleep -Seconds 1
  }

  if (-not $ready) {
    Write-Host "Backend not ready in time, required ports: $ChartPort and $BackendPort"
    if (Test-Path $PyLog) {
      Write-Host '--- python log tail ---'
      Get-Content $PyLog -Tail 30
    }
    if (Test-Path "$PyLog.err") {
      Write-Host '--- python err tail ---'
      Get-Content "$PyLog.err" -Tail 30
    }
    if (Test-Path $JavaLog) {
      Write-Host '--- java log tail ---'
      Get-Content $JavaLog -Tail 30
    }
    if (Test-Path "$JavaLog.err") {
      Write-Host '--- java err tail ---'
      Get-Content "$JavaLog.err" -Tail 30
    }
    throw 'Backend failed to start'
  }

  Write-Host "backend: http://127.0.0.1:$BackendPort"
  Write-Host "chartpy: http://127.0.0.1:$ChartPort"

  Write-Host "[2/4] Starting local web service on 127.0.0.1:$WebPort ..."
  if (Test-PortOpen -Port $WebPort) {
    throw "Port $WebPort is already in use"
  }

  $null = Start-Background -FilePath $PythonBin -Arguments @('-m', 'http.server', "$WebPort", '--bind', '127.0.0.1', '--directory', (Quote-Arg $DistDir)) -LogPath $WebLog -PidFile $WebPidFile

  $webReady = $false
  for ($i = 0; $i -lt 30; $i++) {
    if (Test-PortOpen -Port $WebPort) {
      $webReady = $true
      break
    }
    Start-Sleep -Milliseconds 300
  }

  if (-not $webReady) {
    throw "Web service failed to start. Check log: $WebLog"
  }

  $url = "http://127.0.0.1:$WebPort/index.html"

  Write-Host '[3/4] Opening browser...'
  if ($env:HOROSA_NO_BROWSER -eq '1') {
    Write-Host "[4/4] Started (no-browser mode): $url"
    Write-Host 'Press Enter to stop local services.'
    Read-Host 'Press Enter to stop'
  } else {
    $browser = Resolve-Browser
    if ($browser) {
      $args = @(
        "--user-data-dir=$BrowserProfile",
        "--app=$url",
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-features=DialMediaRouteProvider'
      )
      $bp = Start-Process -FilePath $browser -ArgumentList $args -PassThru
      Write-Host "[4/4] Started: $url"
      Write-Host 'Close this app window to stop local services.'
      Wait-Process -Id $bp.Id
    } else {
      Start-Process $url | Out-Null
      Write-Host "[4/4] Started: $url"
      Write-Host 'No Chrome/Edge/Brave/Chromium found.'
      Write-Host 'Close browser, then come back here and press Enter to stop services.'
      Read-Host 'Press Enter to stop'
    }
  }

  Write-Host 'Browser closed, stopping local services...'
} catch {
  Write-Host "Startup failed: $($_.Exception.Message)"
  Write-Host "Log directory: $LogDir"
  Read-Host 'Press Enter to exit'
  exit 1
} finally {
  Cleanup-All
  $env:PYTHONPATH = $oldPythonPath
}
