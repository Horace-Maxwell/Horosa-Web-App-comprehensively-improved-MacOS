#!/usr/bin/env bash
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK_ROOT="${INSTALLER_ROOT}/build/github-release-e2e"
DOWNLOAD_ROOT="${WORK_ROOT}/downloads"
APP_UNZIP_ROOT="${WORK_ROOT}/app-unzip"
RELEASE_API='https://api.github.com/repos/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest'
MANIFEST_URL='https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/horosa-latest.json'
INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_NAME="$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PYCONF'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
print(config['appName'])
PYCONF
)"

rm -rf "${WORK_ROOT}"
mkdir -p "${DOWNLOAD_ROOT}" "${APP_UNZIP_ROOT}"

fetch() {
  curl -fL --retry 5 --retry-delay 2 --retry-all-errors "$@"
}

fetch "${RELEASE_API}" -o "${DOWNLOAD_ROOT}/release.json"
fetch -H 'Cache-Control: no-cache' -H 'Pragma: no-cache' "${MANIFEST_URL}" -o "${DOWNLOAD_ROOT}/horosa-latest.json"

python3 - <<'PY' "${DOWNLOAD_ROOT}/release.json" "${DOWNLOAD_ROOT}/horosa-latest.json" > "${WORK_ROOT}/release.env"
import json, pathlib, platform, shlex, sys
release = json.loads(pathlib.Path(sys.argv[1]).read_text())
manifest = json.loads(pathlib.Path(sys.argv[2]).read_text())
arch = platform.machine().lower()
platform_key = 'darwin-aarch64' if arch in ('arm64', 'aarch64') else 'darwin-x86_64'
platform = manifest['platforms'][platform_key]
required_assets = {
    'Horosa-Installer-macos-universal-pkg.zip',
    'Horosa-Installer-macos-universal.pkg',
    'Horosa-Installer-macos-universal-offline-pkg.zip',
    'Horosa-Installer-macos-universal-offline.pkg',
    'Horosa-Desktop-macos-universal.zip',
    'horosa-latest.json',
}
asset_names = {asset['name'] for asset in release['assets']}
missing = sorted(required_assets - asset_names)
if missing:
    raise SystemExit(f'missing release assets: {missing}')
for key in ('tag_name', 'name'):
    print(f'{key.upper()}={shlex.quote(release[key])}')
for key in ('version', 'tag'):
    print(f'MANIFEST_{key.upper()}={shlex.quote(manifest[key])}')
for key in ('pkgUrl', 'appUrl', 'runtimeUrl', 'pkgSha256', 'appSha256', 'runtimeSha256'):
    env = key.replace('Url', '_URL').replace('Sha256', '_SHA256').upper()
    print(f'{env}={shlex.quote(platform[key])}')
PY

source "${WORK_ROOT}/release.env"

fetch -o "${DOWNLOAD_ROOT}/Horosa-Installer-macos-universal-pkg.zip" "https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/${TAG_NAME}/Horosa-Installer-macos-universal-pkg.zip"
fetch -o "${DOWNLOAD_ROOT}/Horosa-Installer-macos-universal.pkg" "${PKG_URL}"
fetch -o "${DOWNLOAD_ROOT}/Horosa-Installer-macos-universal-offline-pkg.zip" "https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/${TAG_NAME}/Horosa-Installer-macos-universal-offline-pkg.zip"
fetch -o "${DOWNLOAD_ROOT}/Horosa-Installer-macos-universal-offline.pkg" "https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/${TAG_NAME}/Horosa-Installer-macos-universal-offline.pkg"
fetch -o "${DOWNLOAD_ROOT}/Horosa-Desktop-macos-universal.zip" "${APP_URL}"
fetch -o "${DOWNLOAD_ROOT}/horosa-runtime-macos-universal.tar.gz" "${RUNTIME_URL}"

python3 - <<'PY' "${DOWNLOAD_ROOT}/Horosa-Installer-macos-universal.pkg" "${PKG_SHA256}" "${DOWNLOAD_ROOT}/Horosa-Desktop-macos-universal.zip" "${APP_SHA256}" "${DOWNLOAD_ROOT}/horosa-runtime-macos-universal.tar.gz" "${RUNTIME_SHA256}"
import hashlib, pathlib, sys
checks = [
    ('pkg', pathlib.Path(sys.argv[1]), sys.argv[2]),
    ('appzip', pathlib.Path(sys.argv[3]), sys.argv[4]),
    ('runtime', pathlib.Path(sys.argv[5]), sys.argv[6]),
]
for label, path, expected in checks:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f'{label}_sha={actual}')
    if actual != expected:
        raise SystemExit(f'{label} checksum mismatch: {actual} != {expected}')
PY

mkdir -p "${DOWNLOAD_ROOT}/delivery-unzip"
ditto -x -k "${DOWNLOAD_ROOT}/Horosa-Installer-macos-universal-pkg.zip" "${DOWNLOAD_ROOT}/delivery-unzip"
[ -f "${DOWNLOAD_ROOT}/delivery-unzip/Horosa-Installer-macos-universal.pkg" ]
[ -f "${DOWNLOAD_ROOT}/delivery-unzip/Open-XingQue-Unsigned.command" ]
[ -f "${DOWNLOAD_ROOT}/delivery-unzip/UNSIGNED_INSTALL_GUIDE.txt" ]
bash -n "${DOWNLOAD_ROOT}/delivery-unzip/Open-XingQue-Unsigned.command"
HOROSA_DRY_RUN=1 HOROSA_SKIP_OPEN_SECURITY=1 /bin/bash "${DOWNLOAD_ROOT}/delivery-unzip/Open-XingQue-Unsigned.command" >/dev/null
mkdir -p "${DOWNLOAD_ROOT}/offline-delivery-unzip"
ditto -x -k "${DOWNLOAD_ROOT}/Horosa-Installer-macos-universal-offline-pkg.zip" "${DOWNLOAD_ROOT}/offline-delivery-unzip"
[ -f "${DOWNLOAD_ROOT}/offline-delivery-unzip/Horosa-Installer-macos-universal-offline.pkg" ]
[ -f "${DOWNLOAD_ROOT}/offline-delivery-unzip/Open-XingQue-Unsigned.command" ]
[ -f "${DOWNLOAD_ROOT}/offline-delivery-unzip/UNSIGNED_INSTALL_GUIDE.txt" ]
bash -n "${DOWNLOAD_ROOT}/offline-delivery-unzip/Open-XingQue-Unsigned.command"

ditto -x -k "${DOWNLOAD_ROOT}/Horosa-Desktop-macos-universal.zip" "${APP_UNZIP_ROOT}"
APP_BUNDLE_PATH="$(find "${APP_UNZIP_ROOT}" -maxdepth 1 -type d -name "*.app" | head -n 1)"
[ -n "${APP_BUNDLE_PATH}" ]
plutil -extract CFBundleName raw -o - "${APP_BUNDLE_PATH}/Contents/Info.plist" | rg "^${APP_NAME}$"

TMP_INSTALL="$(mktemp -d "${TMPDIR:-/tmp}/horosa-github-release.XXXXXX")"
cleanup() {
  if [ -n "${CHART_PORT:-}" ] && [ -n "${BACKEND_PORT:-}" ] && [ -d "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/current/Horosa-Web" ]; then
    (
      cd "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/current/Horosa-Web"
      HOROSA_CHART_PORT="${CHART_PORT}" HOROSA_SERVER_PORT="${BACKEND_PORT}" /bin/bash ./stop_horosa_local.sh >/dev/null 2>&1 || true
    )
  fi
  rm -rf "${TMP_INSTALL}"
}
trap cleanup EXIT

pkgutil --expand-full "${DOWNLOAD_ROOT}/Horosa-Installer-macos-universal.pkg" "${TMP_INSTALL}/expanded" >/dev/null
COMPONENT_SCRIPT="$(find "${TMP_INSTALL}/expanded" -path '*/Scripts/postinstall' | head -n 1)"
pkgutil --expand-full "${DOWNLOAD_ROOT}/Horosa-Installer-macos-universal-offline.pkg" "${TMP_INSTALL}/expanded-offline" >/dev/null
OFFLINE_COMPONENT_SCRIPT="$(find "${TMP_INSTALL}/expanded-offline" -path '*/Scripts/postinstall' | head -n 1)"
mkdir -p "${TMP_INSTALL}/target/Applications"
rsync -a "${APP_BUNDLE_PATH}/" "${TMP_INSTALL}/target/Applications/${APP_NAME}.app/"
/bin/bash "${COMPONENT_SCRIPT}" pkgid unused "${TMP_INSTALL}/target"

[ -f "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime-install-pending.txt" ]
[ ! -d "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/current" ]
mkdir -p "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/_bootstrap"
/usr/bin/tar -xzf "${DOWNLOAD_ROOT}/horosa-runtime-macos-universal.tar.gz" -C "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/_bootstrap"
[ -f "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/_bootstrap/runtime-payload/runtime-manifest.json" ]
mv "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/_bootstrap/runtime-payload" "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/current"
rm -rf "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/_bootstrap"
rm -f "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime-install-pending.txt"

[ -f "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/current/runtime-manifest.json" ]
[ -f "${TMP_INSTALL}/target/Users/Shared/Horosa/installer.log" ]
[ -x "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/current/runtime/mac/python/Resources/Python.app/Contents/MacOS/Python" ]
/usr/bin/python3 "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/current/Horosa-Web/scripts/repairEmbeddedPythonRuntime.py" --check "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/current/runtime/mac/python"
PATH="/usr/bin:/bin:/usr/sbin:/sbin" "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/current/runtime/mac/python/bin/python3" -c 'import sys, ssl, hashlib; print(sys.executable); print("embedded-python-ok")' >/dev/null

mkdir -p "${TMP_INSTALL}/offline-target/Applications"
rsync -a "${APP_BUNDLE_PATH}/" "${TMP_INSTALL}/offline-target/Applications/${APP_NAME}.app/"
HOROSA_RUNTIME_URL="file:///definitely-missing-runtime.tar.gz" /bin/bash "${OFFLINE_COMPONENT_SCRIPT}" pkgid unused "${TMP_INSTALL}/offline-target"
[ -f "${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime/current/runtime-manifest.json" ]
[ ! -f "${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime-install-pending.txt" ]

read -r CHART_PORT BACKEND_PORT <<EOF
$(python3 - <<'PY'
import socket
ports = []
for _ in range(2):
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    ports.append(str(s.getsockname()[1]))
    s.close()
print(*ports)
PY
)
EOF

(
  cd "${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/current/Horosa-Web"
  PATH="/usr/bin:/bin:/usr/sbin:/sbin" \
  HOROSA_SKIP_UI_BUILD=1 \
  HOROSA_SKIP_RUNTIME_WARMUP=1 \
  HOROSA_STARTUP_TIMEOUT=180 \
  HOROSA_CHART_PORT="${CHART_PORT}" \
  HOROSA_SERVER_PORT="${BACKEND_PORT}" \
  HOROSA_PYTHON="${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/current/runtime/mac/python/bin/python3" \
  HOROSA_JAVA_BIN="${TMP_INSTALL}/target/Users/Shared/Horosa/runtime/current/runtime/mac/java/bin/java" \
  HOROSA_LOG_ROOT="${TMP_INSTALL}/logs" \
  HOROSA_DIAG_DIR="${TMP_INSTALL}/diag" \
  /bin/bash ./start_horosa_local.sh
)

for url in "http://127.0.0.1:${BACKEND_PORT}/common/time" "http://127.0.0.1:${CHART_PORT}/"; do
  ok=''
  for _ in $(seq 1 120); do
    code="$(curl -s -o /dev/null --max-time 2 -w '%{http_code}' "$url" || true)"
    if [ -n "${code}" ] && [ "${code}" != '000' ]; then
      echo "$url -> ${code}"
      ok=1
      break
    fi
    sleep 1
  done
  [ -n "${ok}" ] || {
    echo "endpoint not ready: ${url}" >&2
    exit 1
  }
done

APP_VERSION="$(plutil -extract CFBundleShortVersionString raw -o - "${APP_BUNDLE_PATH}/Contents/Info.plist")"
echo "app_version=${APP_VERSION}"
echo "latest_manifest_version=${MANIFEST_VERSION}"
[ "${APP_VERSION}" = "${MANIFEST_VERSION}" ] || {
  echo "check-updates expectation failed: app ${APP_VERSION} != latest ${MANIFEST_VERSION}" >&2
  exit 1
}

echo "github release e2e passed for ${TAG_NAME}"
