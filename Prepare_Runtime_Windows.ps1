Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$RuntimeRoot = Join-Path $Root 'runtime\\windows'
$JavaDst = Join-Path $RuntimeRoot 'java'
$PyDst = Join-Path $RuntimeRoot 'python'

New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null

$JavaSrc = $env:HOROSA_JAVA_HOME
if (-not $JavaSrc) {
  if ($env:JAVA_HOME) {
    $JavaSrc = $env:JAVA_HOME
  }
}
if (-not $JavaSrc) {
  $javaCmd = Get-Command java -ErrorAction SilentlyContinue
  if ($javaCmd -and $javaCmd.Source) {
    $javaBinDir = Split-Path -Parent $javaCmd.Source
    $JavaSrc = Split-Path -Parent $javaBinDir
  }
}
if (-not $JavaSrc) {
  $javaCandidates = @(
    "$env:ProgramFiles\Java",
    "$env:ProgramFiles\Eclipse Adoptium",
    "$env:ProgramFiles\Zulu",
    "$env:ProgramFiles\Amazon Corretto",
    "$env:ProgramFiles(x86)\Java",
    "$env:ProgramFiles(x86)\Eclipse Adoptium"
  )
  foreach ($base in $javaCandidates) {
    if (-not (Test-Path $base)) { continue }
    $found = Get-ChildItem -Path $base -Directory -ErrorAction SilentlyContinue |
      Sort-Object LastWriteTime -Descending |
      Where-Object { Test-Path (Join-Path $_.FullName 'bin\java.exe') } |
      Select-Object -First 1
    if ($found) {
      $JavaSrc = $found.FullName
      break
    }
  }
}

if ($JavaSrc -and (Test-Path (Join-Path $JavaSrc 'bin\\java.exe'))) {
  Write-Host "Copy Java runtime: $JavaSrc -> $JavaDst"
  if (Test-Path $JavaDst) { Remove-Item -Recurse -Force $JavaDst }
  New-Item -ItemType Directory -Force -Path $JavaDst | Out-Null
  robocopy $JavaSrc $JavaDst /E /NFL /NDL /NJH /NJS /NP | Out-Null
} else {
  Write-Host 'Java runtime not found. Set HOROSA_JAVA_HOME (or JAVA_HOME) then rerun.'
}

$PySrc = $env:HOROSA_PYTHON_HOME
if (-not $PySrc) {
  $cand = @(
    "$env:LocalAppData\\Programs\\Python\\Python312",
    "$env:LocalAppData\\Programs\\Python\\Python311",
    "$env:ProgramFiles\\Python312",
    "$env:ProgramFiles\\Python311"
  )
  foreach ($c in $cand) {
    if (Test-Path (Join-Path $c 'python.exe')) {
      $PySrc = $c
      break
    }
  }
}
if (-not $PySrc) {
  $pyCmd = Get-Command python -ErrorAction SilentlyContinue
  if ($pyCmd -and $pyCmd.Source) {
    $PySrc = Split-Path -Parent $pyCmd.Source
  }
}

if ($PySrc -and (Test-Path (Join-Path $PySrc 'python.exe'))) {
  Write-Host "Copy Python runtime: $PySrc -> $PyDst"
  if (Test-Path $PyDst) { Remove-Item -Recurse -Force $PyDst }
  New-Item -ItemType Directory -Force -Path $PyDst | Out-Null
  robocopy $PySrc $PyDst /E /NFL /NDL /NJH /NJS /NP | Out-Null
} else {
  Write-Host 'Python runtime not found. Set HOROSA_PYTHON_HOME then rerun.'
}

Write-Host 'Done. Runtime folder:'
Get-ChildItem -Force $RuntimeRoot | Format-Table Name, LastWriteTime
Write-Host ''
if (Test-Path (Join-Path $JavaDst 'bin\\java.exe')) {
  Write-Host '[OK] Java runtime ready.'
} else {
  Write-Host '[MISSING] runtime\\windows\\java\\bin\\java.exe'
}
if (Test-Path (Join-Path $PyDst 'python.exe')) {
  Write-Host '[OK] Python runtime ready.'
} else {
  Write-Host '[MISSING] runtime\\windows\\python\\python.exe'
}
Read-Host 'Press Enter to exit'
