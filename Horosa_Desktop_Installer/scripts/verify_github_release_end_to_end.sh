#!/usr/bin/env bash
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK_ROOT="${INSTALLER_ROOT}/build/github-release-e2e"
DOWNLOAD_ROOT="${WORK_ROOT}/downloads"
APP_UNZIP_ROOT="${WORK_ROOT}/app-unzip"
INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
read -r APP_NAME DESKTOP_OFFLINE_PKG DESKTOP_ASSET RUNTIME_ASSET TAG_NAME RELEASE_CHANNEL <<EOF
$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PYCONF'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
version = json.loads((root / 'package.json').read_text())['version']
print(
    config['appName'],
    config['desktopOfflinePkgName'],
    config['desktopAssetName'],
    config['runtimeAssetName'],
    f"{config['releaseTagPrefix']}{version}",
    config.get('releaseChannel', 'stable'),
)
PYCONF
)
EOF
RELEASE_API='https://api.github.com/repos/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest'
MANIFEST_URL='https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/horosa-latest.json'
case "$(printf '%s' "${HOROSA_RELEASE_CHANNEL:-${RELEASE_CHANNEL}}" | tr '[:upper:]' '[:lower:]')" in
  beta|preview|prerelease|pre-release)
    RELEASE_API="https://api.github.com/repos/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tags/${TAG_NAME}"
    MANIFEST_URL="https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/${TAG_NAME}/horosa-latest.json"
    ;;
esac

rm -rf "${WORK_ROOT}"
mkdir -p "${DOWNLOAD_ROOT}" "${APP_UNZIP_ROOT}"

fetch() {
  curl -fL --retry 5 --retry-delay 2 --retry-all-errors "$@"
}

signed_backend_code() {
  local url="$1"
  local sig="9947b25d6400dac3e74fea88ec1a2308a2c9abf5f3a0cda32b7655717fa86278"
  curl -s -o /dev/null --max-time 2 -w '%{http_code}' \
    -H "ClientChannel: 1" \
    -H "ClientApp: 1" \
    -H "ClientVer: 1.0" \
    -H "Signature: ${sig}" \
    "$url" || true
}

fetch "${RELEASE_API}" -o "${DOWNLOAD_ROOT}/release.json"
fetch -H 'Cache-Control: no-cache' -H 'Pragma: no-cache' "${MANIFEST_URL}" -o "${DOWNLOAD_ROOT}/horosa-latest.json"

DESKTOP_OFFLINE_PKG_ENV="${DESKTOP_OFFLINE_PKG}" \
DESKTOP_ASSET_ENV="${DESKTOP_ASSET}" \
python3 - <<'PY' "${DOWNLOAD_ROOT}/release.json" "${DOWNLOAD_ROOT}/horosa-latest.json" > "${WORK_ROOT}/release.env"
import json, os, pathlib, platform, shlex, sys
release = json.loads(pathlib.Path(sys.argv[1]).read_text())
manifest = json.loads(pathlib.Path(sys.argv[2]).read_text())
arch = platform.machine().lower()
platform_key = 'darwin-aarch64' if arch in ('arm64', 'aarch64') else 'darwin-x86_64'
platform = manifest['platforms'][platform_key]
required_assets = {
    os.environ['DESKTOP_OFFLINE_PKG_ENV'],
    os.environ['DESKTOP_ASSET_ENV'],
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

fetch -o "${DOWNLOAD_ROOT}/${DESKTOP_OFFLINE_PKG}" "https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/${TAG_NAME}/${DESKTOP_OFFLINE_PKG}"
fetch -o "${DOWNLOAD_ROOT}/${DESKTOP_ASSET}" "${APP_URL}"
fetch -o "${DOWNLOAD_ROOT}/${RUNTIME_ASSET}" "${RUNTIME_URL}"

python3 - <<'PY' "${DOWNLOAD_ROOT}/${DESKTOP_OFFLINE_PKG}" "${PKG_SHA256}" "${DOWNLOAD_ROOT}/${DESKTOP_ASSET}" "${APP_SHA256}" "${DOWNLOAD_ROOT}/${RUNTIME_ASSET}" "${RUNTIME_SHA256}"
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

ditto -x -k "${DOWNLOAD_ROOT}/${DESKTOP_ASSET}" "${APP_UNZIP_ROOT}"
APP_BUNDLE_PATH="$(find "${APP_UNZIP_ROOT}" -maxdepth 1 -type d -name "*.app" | head -n 1)"
[ -n "${APP_BUNDLE_PATH}" ]
plutil -extract CFBundleName raw -o - "${APP_BUNDLE_PATH}/Contents/Info.plist" | rg "^${APP_NAME}$"
python3 "${INSTALLER_ROOT}/scripts/verify_icon_alpha.py" \
  --paths "${APP_BUNDLE_PATH}/Contents/Resources/icon.icns"

TMP_INSTALL="$(mktemp -d "${TMPDIR:-/tmp}/horosa-github-release.XXXXXX")"
cleanup() {
  if [ -n "${CHART_PORT:-}" ] && [ -n "${BACKEND_PORT:-}" ] && [ -d "${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime/current/Horosa-Web" ]; then
    (
      cd "${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime/current/Horosa-Web"
      HOROSA_CHART_PORT="${CHART_PORT}" HOROSA_SERVER_PORT="${BACKEND_PORT}" /bin/bash ./stop_horosa_local.sh >/dev/null 2>&1 || true
    )
  fi
  rm -rf "${TMP_INSTALL}"
}
trap cleanup EXIT

pkgutil --expand-full "${DOWNLOAD_ROOT}/${DESKTOP_OFFLINE_PKG}" "${TMP_INSTALL}/expanded-offline" >/dev/null
OFFLINE_COMPONENT_SCRIPT="$(find "${TMP_INSTALL}/expanded-offline" -path '*/Scripts/postinstall' | head -n 1)"

mkdir -p "${TMP_INSTALL}/offline-target/Applications"
rsync -a "${APP_BUNDLE_PATH}/" "${TMP_INSTALL}/offline-target/Applications/${APP_NAME}.app/"
HOROSA_RUNTIME_URL="file:///definitely-missing-runtime.tar.gz" /bin/bash "${OFFLINE_COMPONENT_SCRIPT}" pkgid unused "${TMP_INSTALL}/offline-target"
[ -f "${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime/current/runtime-manifest.json" ]
[ ! -f "${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime-install-pending.txt" ]
[ -f "${TMP_INSTALL}/offline-target/Users/Shared/Horosa/installer.log" ]
[ -x "${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime/current/runtime/mac/python/Resources/Python.app/Contents/MacOS/Python" ]
/usr/bin/python3 "${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime/current/Horosa-Web/scripts/repairEmbeddedPythonRuntime.py" --check "${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime/current/runtime/mac/python"
PATH="/usr/bin:/bin:/usr/sbin:/sbin" "${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime/current/runtime/mac/python/bin/python3" -c 'import sys, ssl, hashlib; print(sys.executable); print("embedded-python-ok")' >/dev/null
PATH="/usr/bin:/bin:/usr/sbin:/sbin" "${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime/current/runtime/mac/java/bin/java" -version >/dev/null

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
  cd "${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime/current/Horosa-Web"
  PATH="/usr/bin:/bin:/usr/sbin:/sbin" \
  HOROSA_SKIP_UI_BUILD=1 \
  HOROSA_SKIP_RUNTIME_WARMUP=1 \
  HOROSA_REQUIRE_EMBEDDED_RUNTIME=1 \
  HOROSA_STARTUP_TIMEOUT=180 \
  HOROSA_CHART_PORT="${CHART_PORT}" \
  HOROSA_SERVER_PORT="${BACKEND_PORT}" \
  HOROSA_PYTHON="${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime/current/runtime/mac/python/bin/python3" \
  HOROSA_JAVA_BIN="${TMP_INSTALL}/offline-target/Users/Shared/Horosa/runtime/current/runtime/mac/java/bin/java" \
  HOROSA_LOG_ROOT="${TMP_INSTALL}/logs" \
  HOROSA_DIAG_DIR="${TMP_INSTALL}/diag" \
  /bin/bash ./start_horosa_local.sh
)

chart_ok=''
for _ in $(seq 1 120); do
  code="$(curl -s -o /dev/null --max-time 2 -w '%{http_code}' "http://127.0.0.1:${CHART_PORT}/" || true)"
  if [ -n "${code}" ] && [ "${code}" != '000' ] && [ "${code}" -lt 500 ]; then
    echo "http://127.0.0.1:${CHART_PORT}/ -> ${code}"
    chart_ok=1
    break
  fi
  sleep 1
done
[ -n "${chart_ok}" ] || {
  echo "endpoint not ready: http://127.0.0.1:${CHART_PORT}/" >&2
  exit 1
}
# Keep the technique smoke before the generic chart/backend smoke. This catches
# shared-process global state pollution, including Swiss Ephemeris path resets.
python3 "${INSTALLER_ROOT}/scripts/verify_kentang_runtime_endpoints.py" --root "http://127.0.0.1:${CHART_PORT}"

backend_ok=''
for _ in $(seq 1 120); do
  code="$(signed_backend_code "http://127.0.0.1:${BACKEND_PORT}/common/time")"
  if [ -n "${code}" ] && [ "${code}" != '000' ] && [ "${code}" -lt 500 ]; then
    echo "http://127.0.0.1:${BACKEND_PORT}/common/time -> ${code}"
    backend_ok=1
    break
  fi
  sleep 1
done
[ -n "${backend_ok}" ] || {
  echo "endpoint not ready: http://127.0.0.1:${BACKEND_PORT}/common/time" >&2
  exit 1
}

HOROSA_SERVER_ROOT="http://127.0.0.1:${BACKEND_PORT}" node "${INSTALLER_ROOT}/../Horosa-Web/astrostudyui/scripts/verifyHorosaRuntimeFull.js" >/dev/null
if rg -n "MongoTimeoutException|127\\.0\\.0\\.1:27017|Connection refused" "${TMP_INSTALL}/logs" "${TMP_INSTALL}/diag" >/dev/null 2>&1; then
  echo "github release smoke produced unexpected Mongo connection errors" >&2
  rg -n "MongoTimeoutException|127\\.0\\.0\\.1:27017|Connection refused" "${TMP_INSTALL}/logs" "${TMP_INSTALL}/diag" >&2 || true
  exit 1
fi

APP_VERSION="$(plutil -extract CFBundleShortVersionString raw -o - "${APP_BUNDLE_PATH}/Contents/Info.plist")"
echo "app_version=${APP_VERSION}"
echo "latest_manifest_version=${MANIFEST_VERSION}"
[ "${APP_VERSION}" = "${MANIFEST_VERSION}" ] || {
  echo "check-updates expectation failed: app ${APP_VERSION} != latest ${MANIFEST_VERSION}" >&2
  exit 1
}

echo "github release e2e passed for ${TAG_NAME}"
