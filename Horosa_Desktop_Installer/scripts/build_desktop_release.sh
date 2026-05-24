#!/usr/bin/env bash
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_ROOT="${INSTALLER_ROOT}/dist"
BUILD_ROOT="${INSTALLER_ROOT}/build"
TARGET_ROOT="${INSTALLER_ROOT}/src-tauri/target-user"
OFFLINE_SCRIPTS_RENDERED_DIR="${BUILD_ROOT}/installer-scripts-rendered-offline"
NOTARY_BUILD_ROOT="${BUILD_ROOT}/notary"
POSTINSTALL_TEMPLATE="${INSTALLER_ROOT}/installer-scripts/postinstall.template"
RELEASE_CONFIG="${INSTALLER_ROOT}/config/release_config.json"
APPLE_SIGNING_IDENTITY="${APPLE_SIGNING_IDENTITY:-}"
APPLE_INSTALLER_IDENTITY="${APPLE_INSTALLER_IDENTITY:-}"
APPLE_ENTITLEMENTS_PATH="${APPLE_ENTITLEMENTS_PATH:-}"
APPLE_SIGNING_KEYCHAIN="${APPLE_SIGNING_KEYCHAIN:-${HOME}/Library/Keychains/login.keychain-db}"
NOTARYTOOL_KEYCHAIN_PROFILE="${NOTARYTOOL_KEYCHAIN_PROFILE:-horosa-notary}"
HOROSA_PUBLIC_DISTRIBUTION_RAW="${HOROSA_PUBLIC_DISTRIBUTION:-auto}"
HOROSA_PUBLIC_DISTRIBUTION="${HOROSA_PUBLIC_DISTRIBUTION_RAW}"

pick_single_identity_hash() {
  local profile="$1"
  local label="$2"
  local raw_matches unique_labels hashes
  raw_matches="$(security find-identity -v -p "${profile}" 2>/dev/null | rg "Developer ID ${label}: " || true)"
  unique_labels="$(printf '%s\n' "${raw_matches}" | sed -En 's/^ *[0-9]+\) [0-9A-F]+ "(.*)"$/\1/p' | sort -u)"
  hashes="$(printf '%s\n' "${raw_matches}" | sed -En 's/^ *[0-9]+\) ([0-9A-F]+) ".*$/\1/p')"
  local label_count hash_count
  label_count="$(printf '%s\n' "${unique_labels}" | sed '/^$/d' | wc -l | tr -d ' ')"
  hash_count="$(printf '%s\n' "${hashes}" | sed '/^$/d' | wc -l | tr -d ' ')"
  if [ "${label_count}" = "1" ] && [ "${hash_count}" -ge "1" ]; then
    printf '%s' "$(printf '%s\n' "${hashes}" | sed '/^$/d' | tail -n 1)"
    return 0
  fi
  return 1
}

if [ -z "${APPLE_SIGNING_IDENTITY:-}" ] && APPLE_SIGNING_IDENTITY_AUTO="$(pick_single_identity_hash codesigning Application)"; then
  APPLE_SIGNING_IDENTITY="${APPLE_SIGNING_IDENTITY_AUTO}"
fi
if [ -z "${APPLE_INSTALLER_IDENTITY:-}" ] && APPLE_INSTALLER_IDENTITY_AUTO="$(pick_single_identity_hash basic Installer)"; then
  APPLE_INSTALLER_IDENTITY="${APPLE_INSTALLER_IDENTITY_AUTO}"
fi

PUBLIC_SIGNING_INPUTS=0
if [ -n "${APPLE_SIGNING_IDENTITY:-}" ] || [ -n "${APPLE_INSTALLER_IDENTITY:-}" ] || [ -n "${NOTARYTOOL_KEYCHAIN_PROFILE:-}" ]; then
  PUBLIC_SIGNING_INPUTS=1
fi
PUBLIC_SIGNING_READY=0
if [ -n "${APPLE_SIGNING_IDENTITY:-}" ] && [ -n "${APPLE_INSTALLER_IDENTITY:-}" ] && [ -n "${NOTARYTOOL_KEYCHAIN_PROFILE:-}" ]; then
  PUBLIC_SIGNING_READY=1
fi

if [ "${PUBLIC_SIGNING_INPUTS}" = "1" ] && [ "${PUBLIC_SIGNING_READY}" != "1" ]; then
  echo "partial public distribution configuration detected." >&2
  echo "APPLE_SIGNING_IDENTITY=${APPLE_SIGNING_IDENTITY:-<missing>}" >&2
  echo "APPLE_INSTALLER_IDENTITY=${APPLE_INSTALLER_IDENTITY:-<missing>}" >&2
  echo "NOTARYTOOL_KEYCHAIN_PROFILE=${NOTARYTOOL_KEYCHAIN_PROFILE:-<missing>}" >&2
  echo "either provide all three values, or unset them for ad-hoc local builds." >&2
  exit 1
fi

if [ "${HOROSA_PUBLIC_DISTRIBUTION_RAW}" = "auto" ]; then
  if [ "${PUBLIC_SIGNING_READY}" = "1" ]; then
    HOROSA_PUBLIC_DISTRIBUTION=1
  else
    HOROSA_PUBLIC_DISTRIBUTION=0
  fi
fi

if [ "${HOROSA_PUBLIC_DISTRIBUTION}" = "1" ] && [ "${PUBLIC_SIGNING_READY}" != "1" ]; then
  echo "HOROSA_PUBLIC_DISTRIBUTION=1 requires Developer ID Application, Developer ID Installer, and a notarytool keychain profile." >&2
  exit 1
fi

if [ "${HOROSA_PUBLIC_DISTRIBUTION}" = "1" ] && [ "${PUBLIC_SIGNING_READY}" = "1" ] && ! xcrun notarytool history --keychain-profile "${NOTARYTOOL_KEYCHAIN_PROFILE}" >/dev/null 2>&1; then
  echo "notarytool keychain profile is unavailable: ${NOTARYTOOL_KEYCHAIN_PROFILE}" >&2
  exit 1
fi

read -r APP_NAME RUNTIME_ASSET DESKTOP_ASSET DESKTOP_PKG DESKTOP_PKG_ZIP DESKTOP_OFFLINE_PKG DESKTOP_OFFLINE_PKG_ZIP UPDATE_MANIFEST_NAME APP_RELEASE_TAG RUNTIME_VERSION RUNTIME_RELEASE_TAG SUPPORTED_ARCH <<EOF
$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PYCONF'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
version = json.loads((root / 'package.json').read_text())['version']
runtime_version = str(config.get('runtimeVersion') or '').strip()
if runtime_version.lower() in ('', 'auto', 'same-as-app'):
    runtime_version = version
print(
    config['appName'],
    config['runtimeAssetName'],
    config['desktopAssetName'],
    config['desktopPkgName'],
    config['desktopPkgZipName'],
    config['desktopOfflinePkgName'],
    config['desktopOfflinePkgZipName'],
    config['updateManifestName'],
    f"{config['releaseTagPrefix']}{version}",
    runtime_version,
    f"{config['releaseTagPrefix']}{runtime_version}",
    config.get('supportedArch', 'arm64'),
)
PYCONF
)
EOF
TARGET_APP="${TARGET_ROOT}/release/bundle/macos/${APP_NAME}.app"
COMPONENT_PKG="${BUILD_ROOT}/pkg/desktop.component.pkg"
OFFLINE_COMPONENT_PKG="${BUILD_ROOT}/pkg/desktop-offline.component.pkg"
COMPONENT_PLIST="${BUILD_ROOT}/pkg/component.plist"
PKG_STAGE_ROOT="${BUILD_ROOT}/pkg-root"
APP_BUNDLE_ZIP="${DIST_ROOT}/${DESKTOP_ASSET}"
INSTALLER_PKG="${DIST_ROOT}/${DESKTOP_PKG}"
INSTALLER_PKG_ZIP="${DIST_ROOT}/${DESKTOP_PKG_ZIP}"
OFFLINE_INSTALLER_PKG="${DIST_ROOT}/${DESKTOP_OFFLINE_PKG}"
OFFLINE_INSTALLER_PKG_ZIP="${DIST_ROOT}/${DESKTOP_OFFLINE_PKG_ZIP}"
UPDATE_MANIFEST="${DIST_ROOT}/${UPDATE_MANIFEST_NAME}"
RUNTIME_ARCHIVE="${DIST_ROOT}/${RUNTIME_ASSET}"
LEGACY_DMG="${DIST_ROOT}/Horosa-Desktop-macos-arm64.dmg"
NOTARY_APP_ZIP="${NOTARY_BUILD_ROOT}/${APP_NAME}.notary.zip"
REPO_SLUG="$(
INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PY'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
print(f"{config['repoOwner']}/{config['repoName']}")
PY
)"

mkdir -p "${DIST_ROOT}" "${BUILD_ROOT}/pkg" "${OFFLINE_SCRIPTS_RENDERED_DIR}" "${NOTARY_BUILD_ROOT}"
"${INSTALLER_ROOT}/scripts/generate_icon.sh"
if [ "${HOROSA_REUSE_REMOTE_RUNTIME:-0}" = "1" ] && [ "${RUNTIME_RELEASE_TAG}" != "${APP_RELEASE_TAG}" ]; then
  if ! command -v gh >/dev/null 2>&1; then
    echo "HOROSA_REUSE_REMOTE_RUNTIME=1 requires gh to download ${RUNTIME_ASSET} from ${RUNTIME_RELEASE_TAG}." >&2
    exit 1
  fi
  rm -f "${RUNTIME_ARCHIVE}"
  gh release download "${RUNTIME_RELEASE_TAG}" --repo "${REPO_SLUG}" --pattern "${RUNTIME_ASSET}" --dir "${DIST_ROOT}" --clobber
else
  APPLE_SIGNING_IDENTITY="${APPLE_SIGNING_IDENTITY}" APPLE_SIGNING_KEYCHAIN="${APPLE_SIGNING_KEYCHAIN}" HOROSA_PUBLIC_DISTRIBUTION="${HOROSA_PUBLIC_DISTRIBUTION}" "${INSTALLER_ROOT}/scripts/package_runtime_payload.sh"
fi

if [ ! -f "${RUNTIME_ARCHIVE}" ]; then
  echo "missing runtime archive: ${RUNTIME_ARCHIVE}" >&2
  exit 1
fi

LOCAL_RUNTIME_SHA256="$(shasum -a 256 "${RUNTIME_ARCHIVE}" | awk '{print $1}')"
RUNTIME_SHA256="${LOCAL_RUNTIME_SHA256}"
if [ "${RUNTIME_RELEASE_TAG}" != "${APP_RELEASE_TAG}" ] && [ "${HOROSA_FORCE_RUNTIME_UPLOAD:-0}" != "1" ] && command -v gh >/dev/null 2>&1; then
  REMOTE_RUNTIME_JSON="$(gh release view "${RUNTIME_RELEASE_TAG}" --repo "${REPO_SLUG}" --json assets 2>/dev/null || true)"
  REMOTE_RUNTIME_SHA="$(python3 - <<'PY' "${RUNTIME_ASSET}" "${REMOTE_RUNTIME_JSON}"
import json, sys
asset_name = sys.argv[1]
payload = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].strip() else {}
for asset in payload.get('assets', []):
    if asset.get('name') == asset_name:
        digest = str(asset.get('digest') or '')
        if digest.startswith('sha256:'):
            print(digest.split(':', 1)[1])
            break
PY
)"
  if [ -n "${REMOTE_RUNTIME_SHA}" ]; then
    if [ "${REMOTE_RUNTIME_SHA}" != "${LOCAL_RUNTIME_SHA256}" ]; then
      echo "runtime payload changed, but release_config.json still points to ${RUNTIME_RELEASE_TAG}." >&2
      echo "local runtime sha:  ${LOCAL_RUNTIME_SHA256}" >&2
      echo "remote runtime sha: ${REMOTE_RUNTIME_SHA}" >&2
      echo "bump runtimeVersion (or set HOROSA_FORCE_RUNTIME_UPLOAD=1) before publishing this release." >&2
      exit 1
    fi
    RUNTIME_SHA256="${REMOTE_RUNTIME_SHA}"
    echo "using remote runtime digest from ${RUNTIME_RELEASE_TAG}: ${RUNTIME_SHA256}"
  fi
fi

if [ ! -d "${INSTALLER_ROOT}/node_modules" ]; then
  (cd "${INSTALLER_ROOT}" && npm install)
fi

find "${TARGET_ROOT}/release/bundle" -type f -name '*.dmg' -delete 2>/dev/null || true
TAURI_BUILD_OK=1
if ! (cd "${INSTALLER_ROOT}" && CARGO_TARGET_DIR="${TARGET_ROOT}" npm run tauri:build -- --bundles app); then
  TAURI_BUILD_OK=0
  echo "tauri app bundling failed; checking for reusable app bundle..." >&2
fi

if [ ! -d "${TARGET_APP}" ]; then
  echo "missing built app bundle: ${TARGET_APP}" >&2
  exit 1
fi

CURRENT_ARCH="$(uname -m)"
if [ "${SUPPORTED_ARCH}" = "arm64" ] && [ "${CURRENT_ARCH}" != "arm64" ]; then
  echo "release_config.json is locked to arm64, but current builder is ${CURRENT_ARCH}" >&2
  exit 1
fi

if [ "${TAURI_BUILD_OK}" != "1" ]; then
  echo "tauri app bundling failed and no reusable app bundle fallback was requested" >&2
  exit 1
fi

INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" RUNTIME_SHA256_ENV="${RUNTIME_SHA256}" LOCAL_RUNTIME_SHA256_ENV="${LOCAL_RUNTIME_SHA256}" RUNTIME_VERSION_ENV="${RUNTIME_VERSION}" RUNTIME_RELEASE_TAG_ENV="${RUNTIME_RELEASE_TAG}" python3 - <<'PYPOST'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
template = (root / 'installer-scripts/postinstall.template').read_text()

base_replacements = {
    '__APP_NAME__': config['appName'],
    '__REPO_OWNER__': config['repoOwner'],
    '__REPO_NAME__': config['repoName'],
    '__VERSION__': os.environ['RUNTIME_VERSION_ENV'],
    '__RUNTIME_ASSET__': config['runtimeAssetName'],
    '__RUNTIME_RELEASE_TAG__': os.environ['RUNTIME_RELEASE_TAG_ENV'],
}
offline_scripts_dir = root / 'build/installer-scripts-rendered-offline'
offline_scripts_dir.mkdir(parents=True, exist_ok=True)

offline_template = template
for key, value in {
    **base_replacements,
    '__RUNTIME_SHA256__': os.environ['LOCAL_RUNTIME_SHA256_ENV'],
    '__INSTALL_MODE__': 'bootstrap-now',
}.items():
    offline_template = offline_template.replace(key, value)
offline_out = offline_scripts_dir / 'postinstall'
offline_out.write_text(offline_template)
offline_out.chmod(0o755)

PYPOST

cp -f "${RUNTIME_ARCHIVE}" "${OFFLINE_SCRIPTS_RENDERED_DIR}/${RUNTIME_ASSET}"

APPLE_SIGNING_IDENTITY="${APPLE_SIGNING_IDENTITY}" APPLE_ENTITLEMENTS_PATH="${APPLE_ENTITLEMENTS_PATH}" APPLE_SIGNING_KEYCHAIN="${APPLE_SIGNING_KEYCHAIN}" "${INSTALLER_ROOT}/scripts/ad_hoc_sign_app.sh" "${TARGET_APP}"

if [ -n "${APPLE_SIGNING_IDENTITY:-}" ]; then
  spctl -a -vv "${TARGET_APP}" || true
fi

rm -rf "${PKG_STAGE_ROOT}"
mkdir -p "${PKG_STAGE_ROOT}/Applications"
rsync -a "${TARGET_APP}/" "${PKG_STAGE_ROOT}/Applications/${APP_NAME}.app/"

APP_INFO_PLIST="${PKG_STAGE_ROOT}/Applications/${APP_NAME}.app/Contents/Info.plist"
BUNDLE_ID="$(plutil -extract CFBundleIdentifier raw -o - "${APP_INFO_PLIST}")"
APP_VERSION="$(plutil -extract CFBundleShortVersionString raw -o - "${APP_INFO_PLIST}")"

rm -f "${APP_BUNDLE_ZIP}" "${INSTALLER_PKG}" "${INSTALLER_PKG_ZIP}" "${OFFLINE_INSTALLER_PKG}" "${OFFLINE_INSTALLER_PKG_ZIP}" "${COMPONENT_PKG}" "${OFFLINE_COMPONENT_PKG}" "${COMPONENT_PLIST}" "${UPDATE_MANIFEST}" "${LEGACY_DMG}" "${NOTARY_APP_ZIP}"

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

build_component_pkg() {
  local scripts_dir="$1"
  local component_pkg="$2"
  pkgbuild \
    --root "${PKG_STAGE_ROOT}" \
    --component-plist "${COMPONENT_PLIST}" \
    --identifier "${BUNDLE_ID}" \
    --version "${APP_VERSION}" \
    --install-location / \
    --scripts "${scripts_dir}" \
    "${component_pkg}"
}

build_product_pkg() {
  local component_pkg="$1"
  local output_pkg="$2"
  PRODUCTBUILD_ARGS=(--package "${component_pkg}")
  if [ -n "${APPLE_INSTALLER_IDENTITY}" ]; then
    PRODUCTBUILD_ARGS+=(--sign "${APPLE_INSTALLER_IDENTITY}" --keychain "${APPLE_SIGNING_KEYCHAIN}")
  fi
  PRODUCTBUILD_ARGS+=("${output_pkg}")
  productbuild "${PRODUCTBUILD_ARGS[@]}"
}

build_component_pkg "${OFFLINE_SCRIPTS_RENDERED_DIR}" "${OFFLINE_COMPONENT_PKG}"
build_product_pkg "${OFFLINE_COMPONENT_PKG}" "${OFFLINE_INSTALLER_PKG}"

if [ "${HOROSA_PUBLIC_DISTRIBUTION}" = "1" ] && [ "${PUBLIC_SIGNING_READY}" = "1" ]; then
  (
    cd "$(dirname "${TARGET_APP}")"
    ditto -c -k --keepParent "${APP_NAME}.app" "${NOTARY_APP_ZIP}"
  )
  xcrun notarytool submit "${NOTARY_APP_ZIP}" --keychain-profile "${NOTARYTOOL_KEYCHAIN_PROFILE}" --wait
  xcrun stapler staple "${TARGET_APP}"
  xcrun notarytool submit "${OFFLINE_INSTALLER_PKG}" --keychain-profile "${NOTARYTOOL_KEYCHAIN_PROFILE}" --wait
  xcrun stapler staple "${OFFLINE_INSTALLER_PKG}"
fi
(
  cd "$(dirname "${TARGET_APP}")"
  COPYFILE_DISABLE=1 ditto -c -k --keepParent --norsrc "${APP_NAME}.app" "${APP_BUNDLE_ZIP}"
)
rm -f "${INSTALLER_PKG_ZIP}" "${OFFLINE_INSTALLER_PKG_ZIP}"

echo "desktop app bundle ready: ${APP_BUNDLE_ZIP}"
echo "offline installer package ready: ${OFFLINE_INSTALLER_PKG}"
echo "component plist ready: ${COMPONENT_PLIST}"

INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" APP_RELEASE_TAG_ENV="${APP_RELEASE_TAG}" RUNTIME_RELEASE_TAG_ENV="${RUNTIME_RELEASE_TAG}" RUNTIME_VERSION_ENV="${RUNTIME_VERSION}" RUNTIME_SHA256_ENV="${RUNTIME_SHA256}" python3 - <<'PYMANIFEST'
import hashlib, json, os, pathlib, platform
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
app_release_tag = os.environ['APP_RELEASE_TAG_ENV']
runtime_release_tag = os.environ['RUNTIME_RELEASE_TAG_ENV']
runtime_version = os.environ['RUNTIME_VERSION_ENV']
runtime_sha256 = os.environ['RUNTIME_SHA256_ENV']
config = json.loads((root / 'config/release_config.json').read_text())
dist = root / 'dist'
arch = platform.machine().lower()
platform_key = 'darwin-aarch64' if arch in ('arm64', 'aarch64') else 'darwin-x86_64'
version = json.loads((root / 'package.json').read_text())['version']
app_base = f"https://github.com/{config['repoOwner']}/{config['repoName']}/releases/download/{app_release_tag}"
runtime_base = f"https://github.com/{config['repoOwner']}/{config['repoName']}/releases/download/{runtime_release_tag}"
manifest = {
  'version': version,
  'tag': app_release_tag,
  'notes': 'See GitHub release notes.',
  'manifestVersion': 1,
  'platforms': {
    platform_key: {
      'appUrl': f"{app_base}/{config['desktopAssetName']}",
      'pkgUrl': f"{app_base}/{config['desktopOfflinePkgName']}",
      'runtimeUrl': f"{runtime_base}/{config['runtimeAssetName']}",
      'runtimeVersion': runtime_version,
      'appSha256': hashlib.sha256((dist / config['desktopAssetName']).read_bytes()).hexdigest(),
      'pkgSha256': hashlib.sha256((dist / config['desktopOfflinePkgName']).read_bytes()).hexdigest(),
      'runtimeSha256': runtime_sha256,
    }
  }
}
(dist / config['updateManifestName']).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
PYMANIFEST

echo "update manifest ready: ${UPDATE_MANIFEST}"
