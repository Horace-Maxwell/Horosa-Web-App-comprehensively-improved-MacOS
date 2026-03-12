#!/usr/bin/env bash
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_ROOT="${INSTALLER_ROOT}/dist"
BUILD_ROOT="${INSTALLER_ROOT}/build"
read -r APP_NAME RUNTIME_ASSET DESKTOP_ASSET DESKTOP_PKG DESKTOP_PKG_ZIP UPDATE_MANIFEST_NAME <<EOF
$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PYCONF'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
print(
    config['appName'],
    config['runtimeAssetName'],
    config['desktopAssetName'],
    config['desktopPkgName'],
    config['desktopPkgZipName'],
    config['updateManifestName'],
)
PYCONF
)
EOF
RUNTIME_ARCHIVE="${DIST_ROOT}/${RUNTIME_ASSET}"
DESKTOP_ZIP="${DIST_ROOT}/${DESKTOP_ASSET}"
INSTALLER_PKG="${DIST_ROOT}/${DESKTOP_PKG}"
INSTALLER_PKG_ZIP="${DIST_ROOT}/${DESKTOP_PKG_ZIP}"
UPDATE_MANIFEST="${DIST_ROOT}/${UPDATE_MANIFEST_NAME}"
TARGET_ROOT="${INSTALLER_ROOT}/src-tauri/target-user"
TARGET_APP="${TARGET_ROOT}/release/bundle/macos/${APP_NAME}.app"
POSTINSTALL_SCRIPT="${BUILD_ROOT}/installer-scripts-rendered/postinstall"
COMPONENT_PLIST="${BUILD_ROOT}/pkg/component.plist"
UNSIGNED_HELPER_NAME="Open-XingQue-Unsigned.command"
UNSIGNED_GUIDE_NAME="UNSIGNED_INSTALL_GUIDE.txt"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/horosa-desktop-e2e.XXXXXX")"
EXPANDED_PKG="${TMP_ROOT}/pkg-expanded"
INSTALL_TARGET="${TMP_ROOT}/install-target"
DELIVERY_UNZIP_ROOT="${TMP_ROOT}/delivery-unzip"
VERIFY_DMG="${TMP_ROOT}/verify.dmg"
VERIFY_MOUNT="${TMP_ROOT}/verify-volume"
CHART_PORT=""
BACKEND_PORT=""
DMG_ATTACHED=0

pick_ports() {
  python3 - <<'PYPORTS'
import socket
ports = []
for _ in range(2):
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    ports.append(s.getsockname()[1])
    s.close()
print(*ports)
PYPORTS
}

wait_http() {
  local url="$1"
  local timeout="${2:-120}"
  local i
  local code=""
  for i in $(seq 1 "${timeout}"); do
    code="$(curl -s -o /dev/null --max-time 2 -w '%{http_code}' "$url" || true)"
    if [ -n "${code}" ] && [ "${code}" != "000" ]; then
      return 0
    fi
    sleep 1
  done
  return 1
}

wait_port_gone() {
  local port="$1"
  local timeout="${2:-20}"
  local i
  for i in $(seq 1 "${timeout}"); do
    if ! lsof -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

cleanup() {
  local runtime_web="${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current/Horosa-Web"
  if [ -n "${CHART_PORT}" ] && [ -n "${BACKEND_PORT}" ] && [ -x "${runtime_web}/stop_horosa_local.sh" ]; then
    (
      cd "${runtime_web}"
      HOROSA_CHART_PORT="${CHART_PORT}" HOROSA_SERVER_PORT="${BACKEND_PORT}" /bin/bash ./stop_horosa_local.sh >/dev/null 2>&1 || true
    )
  fi
  if [ "${DMG_ATTACHED}" = "1" ]; then
    hdiutil detach "${VERIFY_MOUNT}" -force >/dev/null 2>&1 || true
  fi
  rm -rf "${TMP_ROOT}"
}
trap cleanup EXIT

if [ "${HOROSA_DESKTOP_SKIP_REBUILD:-0}" != "1" ]; then
  printf '[1/7] generate icon\n'
  "${INSTALLER_ROOT}/scripts/generate_icon.sh"

  printf '[2/7] cargo fmt --check\n'
  cargo fmt --manifest-path "${INSTALLER_ROOT}/src-tauri/Cargo.toml" --check

  printf '[3/7] cargo check\n'
  cargo check --manifest-path "${INSTALLER_ROOT}/src-tauri/Cargo.toml"

  printf '[4/7] build desktop release\n'
  "${INSTALLER_ROOT}/scripts/build_desktop_release.sh"
else
  printf '[1-4/7] skip rebuild, reuse existing assets\n'
fi

printf '[5/7] verify app/pkg artifacts\n'
[ -f "${RUNTIME_ARCHIVE}" ]
[ -f "${DESKTOP_ZIP}" ]
[ -f "${INSTALLER_PKG}" ]
[ -f "${INSTALLER_PKG_ZIP}" ]
[ -f "${UPDATE_MANIFEST}" ]
[ -x "${POSTINSTALL_SCRIPT}" ]
[ -f "${COMPONENT_PLIST}" ]
[ -d "${TARGET_APP}" ]
codesign --verify --deep --strict "${TARGET_APP}"
DESKTOP_ZIP_ENV="${DESKTOP_ZIP}" APP_NAME_ENV="${APP_NAME}" python3 - <<'PYZIP'
import os, plistlib, zipfile
zip_path = os.environ['DESKTOP_ZIP_ENV']
app_name = os.environ['APP_NAME_ENV']
with zipfile.ZipFile(zip_path) as archive:
    names = archive.namelist()
    if any(name.startswith('__MACOSX/') for name in names):
        raise SystemExit('unexpected __MACOSX entries in desktop zip')
    bundles = sorted({name.split('/', 1)[0] for name in names if '.app/' in name})
    if len(bundles) != 1:
        raise SystemExit(f'unexpected app bundle layout in desktop zip: {bundles}')
    info_plist = plistlib.loads(archive.read(f"{bundles[0]}/Contents/Info.plist"))
    if info_plist.get('CFBundleName') != app_name:
        raise SystemExit(f"desktop zip bundle name mismatch: {info_plist.get('CFBundleName')} != {app_name}")
PYZIP
mkdir -p "${DELIVERY_UNZIP_ROOT}"
unzip -q "${INSTALLER_PKG_ZIP}" -d "${DELIVERY_UNZIP_ROOT}"
[ -f "${DELIVERY_UNZIP_ROOT}/$(basename "${INSTALLER_PKG}")" ]
[ -f "${DELIVERY_UNZIP_ROOT}/${UNSIGNED_HELPER_NAME}" ]
[ -f "${DELIVERY_UNZIP_ROOT}/${UNSIGNED_GUIDE_NAME}" ]
bash -n "${DELIVERY_UNZIP_ROOT}/${UNSIGNED_HELPER_NAME}"
TMP_FAKE_APP="${TMP_ROOT}/fake-app/${APP_NAME}.app"
mkdir -p "${TMP_FAKE_APP}"
HOROSA_DRY_RUN=1 HOROSA_SKIP_OPEN_SECURITY=1 /bin/bash "${DELIVERY_UNZIP_ROOT}/${UNSIGNED_HELPER_NAME}" >/dev/null
HOROSA_DRY_RUN=1 HOROSA_SKIP_OPEN_SECURITY=1 HOROSA_APP_PATH_OVERRIDE="${TMP_FAKE_APP}" /bin/bash "${DELIVERY_UNZIP_ROOT}/${UNSIGNED_HELPER_NAME}" >/dev/null
INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" UPDATE_MANIFEST_ENV="${UPDATE_MANIFEST}" COMPONENT_PLIST_ENV="${COMPONENT_PLIST}" python3 - <<'PYVERIFY'
import json, os, pathlib, platform, plistlib, re

root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
manifest_path = pathlib.Path(os.environ['UPDATE_MANIFEST_ENV'])
component_plist_path = pathlib.Path(os.environ['COMPONENT_PLIST_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
package = json.loads((root / 'package.json').read_text())
tauri = json.loads((root / 'src-tauri/tauri.conf.json').read_text())
cargo_text = (root / 'src-tauri/Cargo.toml').read_text()
match = re.search(r'^version\s*=\s*"([^"]+)"', cargo_text, re.M)
if not match:
    raise SystemExit('Cargo.toml version missing')
cargo_version = match.group(1)
if len({package['version'], tauri['version'], cargo_version}) != 1:
    raise SystemExit('version mismatch across package.json / tauri.conf.json / Cargo.toml')
if tauri['productName'] != config['appName']:
    raise SystemExit('tauri productName does not match appName')
if tauri['app']['windows'][0]['title'] != config['appName']:
    raise SystemExit('window title does not match appName')

manifest = json.loads(manifest_path.read_text())
if manifest['version'] != package['version']:
    raise SystemExit('manifest version mismatch')
expected_tag = f"{config['releaseTagPrefix']}{package['version']}"
if manifest.get('tag') != expected_tag:
    raise SystemExit(f"manifest tag mismatch: {manifest.get('tag')} != {expected_tag}")
runtime_version = str(config.get('runtimeVersion') or '').strip()
if runtime_version.lower() in ('', 'auto', 'same-as-app'):
    runtime_version = package['version']
expected_runtime_tag = f"{config['releaseTagPrefix']}{runtime_version}"

arch = platform.machine().lower()
platform_key = 'darwin-aarch64' if arch in ('arm64', 'aarch64') else 'darwin-x86_64'
platform_manifest = manifest['platforms'].get(platform_key)
if not platform_manifest:
    raise SystemExit(f'manifest missing platform {platform_key}')

hex64 = re.compile(r'^[0-9a-f]{64}$')
for key in ('appSha256', 'pkgSha256', 'runtimeSha256'):
    if not hex64.fullmatch(platform_manifest.get(key, '')):
        raise SystemExit(f'invalid checksum for {key}')

if not platform_manifest['appUrl'].endswith('/' + config['desktopAssetName']):
    raise SystemExit('appUrl mismatch')
if not platform_manifest['pkgUrl'].endswith('/' + config['desktopPkgName']):
    raise SystemExit('pkgUrl mismatch')
if f"/releases/download/{expected_tag}/" not in platform_manifest['appUrl']:
    raise SystemExit('appUrl release tag mismatch')
if f"/releases/download/{expected_tag}/" not in platform_manifest['pkgUrl']:
    raise SystemExit('pkgUrl release tag mismatch')
if not platform_manifest['runtimeUrl'].endswith('/' + config['runtimeAssetName']):
    raise SystemExit('runtimeUrl mismatch')
if f"/releases/download/{expected_runtime_tag}/" not in platform_manifest['runtimeUrl']:
    raise SystemExit('runtimeUrl release tag mismatch')
if platform_manifest.get('runtimeVersion') != runtime_version:
    raise SystemExit('runtimeVersion mismatch')

entries = plistlib.loads(component_plist_path.read_bytes())
expected = f"Applications/{config['appName']}.app"
for entry in entries:
    if entry.get('RootRelativeBundlePath') == expected:
        if entry.get('BundleIsRelocatable') is not False:
            raise SystemExit('component plist still allows relocation')
        if entry.get('BundleHasStrictIdentifier') is not True:
            raise SystemExit('component plist missing strict identifier')
        if entry.get('BundleIsVersionChecked') is not True:
            raise SystemExit('component plist missing version check')
        break
else:
    raise SystemExit('component plist missing app bundle entry')
PYVERIFY
pkgutil --expand-full "${INSTALLER_PKG}" "${EXPANDED_PKG}"
find "${EXPANDED_PKG}" -type f | rg 'postinstall|PackageInfo|Distribution' >/dev/null

printf '[6/7] simulate pkg postinstall download and shared-runtime launch\n'
mkdir -p "${INSTALL_TARGET}/Applications"
rsync -a "${TARGET_APP}/" "${INSTALL_TARGET}/Applications/${APP_NAME}.app/"
HOROSA_RUNTIME_URL="file:///definitely-missing-runtime.tar.gz" HOROSA_RUNTIME_SHARED_ROOT="${INSTALL_TARGET}/Users/Shared/Horosa" HOROSA_APP_PATH="${INSTALL_TARGET}/Applications/${APP_NAME}.app" /bin/bash "${POSTINSTALL_SCRIPT}" pkgid unused "${INSTALL_TARGET}"
[ -f "${INSTALL_TARGET}/Users/Shared/Horosa/runtime-install-pending.txt" ]
[ ! -d "${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current" ]

RUNTIME_ARCHIVE_URI="$(RUNTIME_ARCHIVE="${RUNTIME_ARCHIVE}" python3 -c 'from pathlib import Path; import os; print(Path(os.environ["RUNTIME_ARCHIVE"]).resolve().as_uri())')"
HOROSA_RUNTIME_URL="${RUNTIME_ARCHIVE_URI}" HOROSA_RUNTIME_SHARED_ROOT="${INSTALL_TARGET}/Users/Shared/Horosa" HOROSA_APP_PATH="${INSTALL_TARGET}/Applications/${APP_NAME}.app" /bin/bash "${POSTINSTALL_SCRIPT}" pkgid unused "${INSTALL_TARGET}"

[ -f "${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current/runtime-manifest.json" ]
[ ! -f "${INSTALL_TARGET}/Users/Shared/Horosa/runtime-install-pending.txt" ]
[ -f "${INSTALL_TARGET}/Users/Shared/Horosa/installer.log" ]
[ -x "${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current/runtime/mac/java/bin/java" ]
[ -x "${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current/runtime/mac/python/bin/python3" ]
[ -x "${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current/runtime/mac/python/Resources/Python.app/Contents/MacOS/Python" ]
[ -f "${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current/Horosa-Web/start_horosa_local.sh" ]
/usr/bin/python3 "${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current/Horosa-Web/scripts/repairEmbeddedPythonRuntime.py" --check "${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current/runtime/mac/python"
PATH="/usr/bin:/bin:/usr/sbin:/sbin" "${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current/runtime/mac/python/bin/python3" -c 'import sys, ssl, hashlib; print(sys.executable); print("embedded-python-ok")' >/dev/null

read -r CHART_PORT BACKEND_PORT <<<"$(pick_ports)"
(
  cd "${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current/Horosa-Web"
  PATH="/usr/bin:/bin:/usr/sbin:/sbin" \
  HOROSA_SKIP_UI_BUILD=1 \
  HOROSA_SKIP_RUNTIME_WARMUP=1 \
  HOROSA_STARTUP_TIMEOUT=180 \
  HOROSA_CHART_PORT="${CHART_PORT}" \
  HOROSA_SERVER_PORT="${BACKEND_PORT}" \
  HOROSA_PYTHON="${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current/runtime/mac/python/bin/python3" \
  HOROSA_JAVA_BIN="${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current/runtime/mac/java/bin/java" \
  HOROSA_LOG_ROOT="${TMP_ROOT}/logs" \
  HOROSA_DIAG_DIR="${TMP_ROOT}/diag" \
  /bin/bash ./start_horosa_local.sh
)
wait_http "http://127.0.0.1:${BACKEND_PORT}/common/time" 120
wait_http "http://127.0.0.1:${CHART_PORT}/" 60
(
  cd "${INSTALL_TARGET}/Users/Shared/Horosa/runtime/current/Horosa-Web"
  HOROSA_CHART_PORT="${CHART_PORT}" HOROSA_SERVER_PORT="${BACKEND_PORT}" /bin/bash ./stop_horosa_local.sh
)
wait_port_gone "${CHART_PORT}" 20
wait_port_gone "${BACKEND_PORT}" 20
echo "installer flow passed for ports ${CHART_PORT}/${BACKEND_PORT}."
CHART_PORT=""
BACKEND_PORT=""

printf '[7/7] inspect expanded pkg payload path\n'
PAYLOAD_ROOT="$(find "${EXPANDED_PKG}" -path '*/Payload' -type d | head -n 1)"
PACKAGE_INFO="$(find "${EXPANDED_PKG}" -path '*/PackageInfo' | head -n 1)"
[ -n "${PAYLOAD_ROOT}" ]
[ -n "${PACKAGE_INFO}" ]
[ -d "${PAYLOAD_ROOT}/Applications/${APP_NAME}.app" ]
[ ! -d "${PAYLOAD_ROOT}/Applications/Horosa.app" ]
plutil -extract CFBundleName raw -o - "${PAYLOAD_ROOT}/Applications/${APP_NAME}.app/Contents/Info.plist" | rg "^${APP_NAME}$"
rg 'install-location="/"' "${PACKAGE_INFO}"
rg 'relocatable="false"' "${PACKAGE_INFO}"
rg "Applications/${APP_NAME}.app" "${PACKAGE_INFO}"
echo "expanded pkg payload passed: ${PAYLOAD_ROOT}/Applications/${APP_NAME}.app"
