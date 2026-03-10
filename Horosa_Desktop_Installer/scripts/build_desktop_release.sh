#!/usr/bin/env bash
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_ROOT="${INSTALLER_ROOT}/dist"
BUILD_ROOT="${INSTALLER_ROOT}/build"
TARGET_ROOT="${INSTALLER_ROOT}/src-tauri/target-user"
SCRIPTS_RENDERED_DIR="${BUILD_ROOT}/installer-scripts-rendered"
SUPPORT_RENDERED_DIR="${BUILD_ROOT}/distribution-support-rendered"
DELIVERY_ROOT="${BUILD_ROOT}/delivery-bundle"
POSTINSTALL_TEMPLATE="${INSTALLER_ROOT}/installer-scripts/postinstall.template"
UNSIGNED_HELPER_TEMPLATE="${INSTALLER_ROOT}/distribution-support/unsigned_install_helper.template"
UNSIGNED_GUIDE_TEMPLATE="${INSTALLER_ROOT}/distribution-support/UNSIGNED_INSTALL_GUIDE.template"
RELEASE_CONFIG="${INSTALLER_ROOT}/config/release_config.json"
APPLE_INSTALLER_IDENTITY="${APPLE_INSTALLER_IDENTITY:-}"
NOTARYTOOL_KEYCHAIN_PROFILE="${NOTARYTOOL_KEYCHAIN_PROFILE:-}"
UNSIGNED_HELPER_NAME="Open-XingQue-Unsigned.command"
UNSIGNED_GUIDE_NAME="UNSIGNED_INSTALL_GUIDE.txt"

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
TARGET_APP="${TARGET_ROOT}/release/bundle/macos/${APP_NAME}.app"
COMPONENT_PKG="${BUILD_ROOT}/pkg/desktop.component.pkg"
COMPONENT_PLIST="${BUILD_ROOT}/pkg/component.plist"
PKG_STAGE_ROOT="${BUILD_ROOT}/pkg-root"
APP_BUNDLE_ZIP="${DIST_ROOT}/${DESKTOP_ASSET}"
INSTALLER_PKG="${DIST_ROOT}/${DESKTOP_PKG}"
INSTALLER_PKG_ZIP="${DIST_ROOT}/${DESKTOP_PKG_ZIP}"
UPDATE_MANIFEST="${DIST_ROOT}/${UPDATE_MANIFEST_NAME}"
RUNTIME_ARCHIVE="${DIST_ROOT}/${RUNTIME_ASSET}"

mkdir -p "${DIST_ROOT}" "${BUILD_ROOT}/pkg" "${SCRIPTS_RENDERED_DIR}" "${SUPPORT_RENDERED_DIR}"
"${INSTALLER_ROOT}/scripts/generate_icon.sh"
"${INSTALLER_ROOT}/scripts/package_runtime_payload.sh"

if [ ! -f "${RUNTIME_ARCHIVE}" ]; then
  echo "missing runtime archive: ${RUNTIME_ARCHIVE}" >&2
  exit 1
fi

RUNTIME_SHA256="$(shasum -a 256 "${RUNTIME_ARCHIVE}" | awk '{print $1}')"

if [ ! -d "${INSTALLER_ROOT}/node_modules" ]; then
  (cd "${INSTALLER_ROOT}" && npm install)
fi

(cd "${INSTALLER_ROOT}" && CARGO_TARGET_DIR="${TARGET_ROOT}" npm run tauri:build)

if [ ! -d "${TARGET_APP}" ]; then
  echo "missing built app bundle: ${TARGET_APP}" >&2
  exit 1
fi

INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" RUNTIME_SHA256_ENV="${RUNTIME_SHA256}" python3 - <<'PYPOST'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
template = (root / 'installer-scripts/postinstall.template').read_text()
replacements = {
    '__APP_NAME__': config['appName'],
    '__REPO_OWNER__': config['repoOwner'],
    '__REPO_NAME__': config['repoName'],
    '__VERSION__': config['runtimeVersion'],
    '__RUNTIME_ASSET__': config['runtimeAssetName'],
    '__RUNTIME_SHA256__': os.environ['RUNTIME_SHA256_ENV'],
    '__TAG_PREFIX__': config['releaseTagPrefix'],
}
for key, value in replacements.items():
    template = template.replace(key, value)
out = root / 'build/installer-scripts-rendered/postinstall'
out.write_text(template)
out.chmod(0o755)

helper = (root / 'distribution-support/unsigned_install_helper.template').read_text()
guide = (root / 'distribution-support/UNSIGNED_INSTALL_GUIDE.template').read_text()
for key, value in {
    '__APP_NAME__': config['appName'],
    '__PKG_NAME__': config['desktopPkgName'],
}.items():
    helper = helper.replace(key, value)
    guide = guide.replace(key, value)
helper_out = root / 'build/distribution-support-rendered/Open-XingQue-Unsigned.command'
guide_out = root / 'build/distribution-support-rendered/UNSIGNED_INSTALL_GUIDE.txt'
helper_out.write_text(helper)
helper_out.chmod(0o755)
guide_out.write_text(guide)
guide_out.chmod(0o644)
PYPOST

"${INSTALLER_ROOT}/scripts/ad_hoc_sign_app.sh" "${TARGET_APP}"

if [ -n "${APPLE_SIGNING_IDENTITY:-}" ]; then
  /usr/bin/spctl -a -vv "${TARGET_APP}" || true
fi

rm -rf "${PKG_STAGE_ROOT}"
mkdir -p "${PKG_STAGE_ROOT}/Applications"
rsync -a "${TARGET_APP}/" "${PKG_STAGE_ROOT}/Applications/${APP_NAME}.app/"

APP_INFO_PLIST="${PKG_STAGE_ROOT}/Applications/${APP_NAME}.app/Contents/Info.plist"
BUNDLE_ID="$(plutil -extract CFBundleIdentifier raw -o - "${APP_INFO_PLIST}")"
APP_VERSION="$(plutil -extract CFBundleShortVersionString raw -o - "${APP_INFO_PLIST}")"

rm -f "${APP_BUNDLE_ZIP}" "${INSTALLER_PKG}" "${COMPONENT_PKG}" "${COMPONENT_PLIST}" "${UPDATE_MANIFEST}"
(
  cd "$(dirname "${TARGET_APP}")"
  COPYFILE_DISABLE=1 ditto -c -k --keepParent --norsrc "${APP_NAME}.app" "${APP_BUNDLE_ZIP}"
)

pkgbuild --analyze --root "${PKG_STAGE_ROOT}" "${COMPONENT_PLIST}"
COMPONENT_PLIST_ENV="${COMPONENT_PLIST}" APP_NAME_ENV="${APP_NAME}" python3 - <<'PYPLIST'
import os
import plistlib
from pathlib import Path
plist_path = Path(os.environ['COMPONENT_PLIST_ENV'])
app_name = os.environ['APP_NAME_ENV']
entries = plistlib.loads(plist_path.read_bytes())
expected = f'Applications/{app_name}.app'
for entry in entries:
    if entry.get('RootRelativeBundlePath') == expected:
        entry['BundleIsRelocatable'] = False
        entry['BundleHasStrictIdentifier'] = True
        entry['BundleIsVersionChecked'] = True
        entry['BundleOverwriteAction'] = 'upgrade'
        break
else:
    raise SystemExit(f'missing component plist entry for {expected}')
plist_path.write_bytes(plistlib.dumps(entries))
PYPLIST

pkgbuild \
  --root "${PKG_STAGE_ROOT}" \
  --component-plist "${COMPONENT_PLIST}" \
  --identifier "${BUNDLE_ID}" \
  --version "${APP_VERSION}" \
  --install-location / \
  --scripts "${SCRIPTS_RENDERED_DIR}" \
  "${COMPONENT_PKG}"

PRODUCTBUILD_ARGS=(--package "${COMPONENT_PKG}")
if [ -n "${APPLE_INSTALLER_IDENTITY}" ]; then
  PRODUCTBUILD_ARGS+=(--sign "${APPLE_INSTALLER_IDENTITY}")
fi
PRODUCTBUILD_ARGS+=("${INSTALLER_PKG}")
productbuild "${PRODUCTBUILD_ARGS[@]}"

if [ -n "${APPLE_SIGNING_IDENTITY:-}" ] && [ -n "${APPLE_INSTALLER_IDENTITY}" ] && [ -n "${NOTARYTOOL_KEYCHAIN_PROFILE}" ]; then
  xcrun notarytool submit "${TARGET_APP}" --keychain-profile "${NOTARYTOOL_KEYCHAIN_PROFILE}" --wait
  xcrun stapler staple "${TARGET_APP}"
  xcrun notarytool submit "${INSTALLER_PKG}" --keychain-profile "${NOTARYTOOL_KEYCHAIN_PROFILE}" --wait
  xcrun stapler staple "${INSTALLER_PKG}"
fi
rm -rf "${DELIVERY_ROOT}"
mkdir -p "${DELIVERY_ROOT}"
cp "${INSTALLER_PKG}" "${DELIVERY_ROOT}/$(basename "${INSTALLER_PKG}")"
cp "${SUPPORT_RENDERED_DIR}/${UNSIGNED_HELPER_NAME}" "${DELIVERY_ROOT}/${UNSIGNED_HELPER_NAME}"
cp "${SUPPORT_RENDERED_DIR}/${UNSIGNED_GUIDE_NAME}" "${DELIVERY_ROOT}/${UNSIGNED_GUIDE_NAME}"

rm -f "${INSTALLER_PKG_ZIP}"
(
  cd "${DELIVERY_ROOT}"
  /usr/bin/zip -qry "${INSTALLER_PKG_ZIP}" .
)

echo "desktop app bundle ready: ${APP_BUNDLE_ZIP}"
echo "installer package ready: ${INSTALLER_PKG}"
echo "installer delivery zip ready: ${INSTALLER_PKG_ZIP}"
echo "component plist ready: ${COMPONENT_PLIST}"

INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PYMANIFEST'
import hashlib, json, os, pathlib, platform
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
dist = root / 'dist'
arch = platform.machine().lower()
platform_key = 'darwin-aarch64' if arch in ('arm64', 'aarch64') else 'darwin-x86_64'
version = json.loads((root / 'package.json').read_text())['version']
tag = f"{config['releaseTagPrefix']}{version}"
base = f"https://github.com/{config['repoOwner']}/{config['repoName']}/releases/download/{tag}"
manifest = {
  'version': version,
  'tag': tag,
  'notes': 'See GitHub release notes.',
  'manifestVersion': 1,
  'platforms': {
    platform_key: {
      'appUrl': f"{base}/{config['desktopAssetName']}",
      'pkgUrl': f"{base}/{config['desktopPkgName']}",
      'runtimeUrl': f"{base}/{config['runtimeAssetName']}",
      'runtimeVersion': config['runtimeVersion'],
      'appSha256': hashlib.sha256((dist / config['desktopAssetName']).read_bytes()).hexdigest(),
      'pkgSha256': hashlib.sha256((dist / config['desktopPkgName']).read_bytes()).hexdigest(),
      'runtimeSha256': hashlib.sha256((dist / config['runtimeAssetName']).read_bytes()).hexdigest(),
    }
  }
}
(dist / config['updateManifestName']).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
PYMANIFEST

echo "update manifest ready: ${UPDATE_MANIFEST}"
