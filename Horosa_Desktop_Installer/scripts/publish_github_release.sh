#!/usr/bin/env bash
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_ROOT="${INSTALLER_ROOT}/dist"
RELEASE_NOTES_FILE="${INSTALLER_ROOT}/config/release_notes.md"

read -r REPO_OWNER REPO_NAME TAG_PREFIX VERSION TAG_NAME RUNTIME_TAG_NAME RUNTIME_ASSET DESKTOP_ASSET DESKTOP_PKG DESKTOP_PKG_ZIP DESKTOP_OFFLINE_PKG DESKTOP_OFFLINE_PKG_ZIP UPDATE_MANIFEST_NAME RUNTIME_VERSION <<EOF
$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PY'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
version = json.loads((root / 'package.json').read_text())['version']
runtime_version = str(config.get('runtimeVersion') or '').strip()
if runtime_version.lower() in ('', 'auto', 'same-as-app'):
    runtime_version = version
print(
    config['repoOwner'],
    config['repoName'],
    config['releaseTagPrefix'],
    version,
    f"{config['releaseTagPrefix']}{version}",
    f"{config['releaseTagPrefix']}{runtime_version}",
    config['runtimeAssetName'],
    config['desktopAssetName'],
    config['desktopPkgName'],
    config['desktopPkgZipName'],
    config['desktopOfflinePkgName'],
    config['desktopOfflinePkgZipName'],
    config['updateManifestName'],
    runtime_version,
)
PY
)
EOF

RELEASE_NAME="${TAG_NAME}"
API_ROOT="https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}"
PRIMARY_DOWNLOAD="${DESKTOP_PKG_ZIP}"
APP_ASSETS=(
  "${DIST_ROOT}/${DESKTOP_PKG_ZIP}"
  "${DIST_ROOT}/${DESKTOP_PKG}"
  "${DIST_ROOT}/${DESKTOP_OFFLINE_PKG_ZIP}"
  "${DIST_ROOT}/${DESKTOP_OFFLINE_PKG}"
  "${DIST_ROOT}/${DESKTOP_ASSET}"
  "${DIST_ROOT}/${UPDATE_MANIFEST_NAME}"
)
RUNTIME_ARCHIVE_PATH="${DIST_ROOT}/${RUNTIME_ASSET}"

for asset in "${APP_ASSETS[@]}" "${RUNTIME_ARCHIVE_PATH}"; do
  [ -f "${asset}" ] || {
    echo "missing asset: ${asset}" >&2
    exit 1
  }
done

resolve_token() {
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    printf '%s' "${GITHUB_TOKEN}"
    return 0
  fi
  printf 'protocol=https\nhost=github.com\n\n' | git credential fill | awk -F= '/^password=/{print $2}'
}

GITHUB_TOKEN="$(resolve_token)"
if [ -z "${GITHUB_TOKEN}" ]; then
  echo 'missing GitHub token' >&2
  exit 1
fi

auth_header=( -H "Authorization: Bearer ${GITHUB_TOKEN}" -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2022-11-28' )

api_json() {
  curl -fsSL "${auth_header[@]}" "$@"
}

EXPECTED_RUNTIME_SHA="$(python3 - <<'PY' "${RUNTIME_ARCHIVE_PATH}"
import hashlib, pathlib, sys
path = pathlib.Path(sys.argv[1])
print(hashlib.sha256(path.read_bytes()).hexdigest())
PY
)"

if [ "${RUNTIME_TAG_NAME}" != "${TAG_NAME}" ] && [ "${HOROSA_FORCE_RUNTIME_UPLOAD:-0}" != "1" ]; then
  REMOTE_RUNTIME_SHA="$(python3 - <<'PY' "${RUNTIME_ASSET}" "$(api_json "${API_ROOT}/releases/tags/${RUNTIME_TAG_NAME}" 2>/dev/null || true)"
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
    EXPECTED_RUNTIME_SHA="${REMOTE_RUNTIME_SHA}"
    python3 - <<'PY' "${DIST_ROOT}/${UPDATE_MANIFEST_NAME}" "${EXPECTED_RUNTIME_SHA}"
import json, pathlib, sys
manifest_path = pathlib.Path(sys.argv[1])
expected_runtime_sha = sys.argv[2]
manifest = json.loads(manifest_path.read_text())
platforms = manifest.get('platforms', {})
for platform in platforms.values():
    if platform.get('runtimeSha256') != expected_runtime_sha:
        platform['runtimeSha256'] = expected_runtime_sha
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
PY
  fi
fi

python3 - <<'PY' "${DIST_ROOT}/${UPDATE_MANIFEST_NAME}" "${DIST_ROOT}/${DESKTOP_ASSET}" "${DIST_ROOT}/${DESKTOP_PKG}" "${DESKTOP_ASSET}" "${DESKTOP_PKG}" "${RUNTIME_ASSET}" "${TAG_NAME}" "${VERSION}" "${RUNTIME_VERSION}" "${RUNTIME_TAG_NAME}" "${EXPECTED_RUNTIME_SHA}"
import hashlib, json, pathlib, sys

manifest_path = pathlib.Path(sys.argv[1])
app_path = pathlib.Path(sys.argv[2])
pkg_path = pathlib.Path(sys.argv[3])
desktop_asset = sys.argv[4]
desktop_pkg = sys.argv[5]
runtime_asset = sys.argv[6]
tag_name = sys.argv[7]
version = sys.argv[8]
runtime_version = sys.argv[9]
runtime_tag_name = sys.argv[10]
expected_runtime_sha = sys.argv[11]
manifest = json.loads(manifest_path.read_text())

if manifest.get('version') != version:
    raise SystemExit(f"local manifest version mismatch: {manifest.get('version')} != {version}")
if manifest.get('tag') != tag_name:
    raise SystemExit(f"local manifest tag mismatch: {manifest.get('tag')} != {tag_name}")

platforms = manifest.get('platforms', {})
if not platforms:
    raise SystemExit('local manifest missing platforms')
platform = next(iter(platforms.values()))

expected_urls = {
    'appUrl': desktop_asset,
    'pkgUrl': desktop_pkg,
    'runtimeUrl': runtime_asset,
}
for key, suffix in expected_urls.items():
    if not platform.get(key, '').endswith('/' + suffix):
        raise SystemExit(f"local manifest {key} mismatch: {platform.get(key)}")
if f"/releases/download/{tag_name}/" not in platform.get('appUrl', ''):
    raise SystemExit(f"local manifest appUrl tag mismatch: {platform.get('appUrl')}")
if f"/releases/download/{tag_name}/" not in platform.get('pkgUrl', ''):
    raise SystemExit(f"local manifest pkgUrl tag mismatch: {platform.get('pkgUrl')}")
if f"/releases/download/{runtime_tag_name}/" not in platform.get('runtimeUrl', ''):
    raise SystemExit(f"local manifest runtimeUrl tag mismatch: {platform.get('runtimeUrl')}")

if platform.get('runtimeVersion') != runtime_version:
    raise SystemExit(
        f"local manifest runtimeVersion mismatch: {platform.get('runtimeVersion')} != {runtime_version}"
    )

checks = {
    'appSha256': app_path,
    'pkgSha256': pkg_path,
}
for key, path in checks.items():
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if platform.get(key) != actual:
        raise SystemExit(f"local manifest {key} mismatch: {platform.get(key)} != {actual}")
if platform.get('runtimeSha256') != expected_runtime_sha:
    raise SystemExit(f"local manifest runtimeSha256 mismatch: {platform.get('runtimeSha256')} != {expected_runtime_sha}")
PY

if [ "${HOROSA_SKIP_VERIFY:-0}" != "1" ]; then
  "${INSTALLER_ROOT}/scripts/verify_desktop_packaging.sh"
fi

if [ "${HOROSA_REQUIRE_SIGNED_PUBLIC_RELEASE:-0}" = "1" ]; then
  "${INSTALLER_ROOT}/scripts/verify_public_distribution_readiness.sh"
fi

RELEASE_NOTES_SECTION=""
if [ -f "${RELEASE_NOTES_FILE}" ]; then
  RELEASE_NOTES_SECTION="$(python3 - <<'PY' "${RELEASE_NOTES_FILE}"
from pathlib import Path
import sys
text = Path(sys.argv[1]).read_text().strip()
print(f"\n\n## 本次更新 / What's New\n\n{text}" if text else "", end="")
PY
)"
fi

RELEASE_BODY="$(
  PRIMARY_DOWNLOAD_ENV="${PRIMARY_DOWNLOAD}" \
  DESKTOP_OFFLINE_PKG_ZIP_ENV="${DESKTOP_OFFLINE_PKG_ZIP}" \
  RELEASE_NOTES_SECTION_ENV="${RELEASE_NOTES_SECTION}" \
  python3 - <<'PY'
import os

print(
    f"""## 安装包选择（中文）

- 轻量在线版：`{os.environ['PRIMARY_DOWNLOAD_ENV']}`，`.pkg` 只安装 app，首次启动时会按 manifest 下载并准备 runtime。
- 完整离线版：`{os.environ['DESKTOP_OFFLINE_PKG_ZIP_ENV']}`，runtime 已内置在安装包里，适合中国大陆或不方便联网的环境。

## 安装步骤（中文）

1. 下载 {os.environ['PRIMARY_DOWNLOAD_ENV']}
2. 解压 zip
3. 先双击里面的 Open-XingQue-Unsigned.command
4. 如果系统仍拦截，再对 .pkg 安装包点右键 -> 打开
5. 完成安装
6. 如果 /Applications/星阙.app 第一次被拦截，再次运行同一个 .command，或对 app 点右键 -> 打开

如果你下载的是完整离线版，则整个安装过程不再需要额外下载 runtime。

普通用户不需要手动下载任何其他文件。

## 技术资产 / Technical Assets

此 Release 中其余资产是安装器与自动更新器使用的内部支持文件，普通用户可以忽略。

The remaining assets in this release are internal support files for the installer and auto-updater. Ordinary users should ignore them.{os.environ['RELEASE_NOTES_SECTION_ENV']}"""
)
PY
)"
export RELEASE_BODY

set_release_meta() {
  local release_json="$1"
  read -r ENSURE_RELEASE_ID ENSURE_UPLOAD_URL <<EOF_META
$(python3 - <<'PY' "${release_json}"
import json, sys
payload = json.loads(sys.argv[1])
print(payload['id'], payload['upload_url'].split('{', 1)[0])
PY
)
EOF_META
}

ensure_release() {
  local tag_name="$1"
  local release_name="$2"
  local release_body="$3"
  local make_latest="$4"
  local release_json=""
  if release_json="$(api_json "${API_ROOT}/releases/tags/${tag_name}" 2>/dev/null)"; then
    set_release_meta "${release_json}"
    curl -fsSL -X PATCH "${auth_header[@]}" -H 'Content-Type: application/json' \
      -d "$(RELEASE_BODY_ENV="${release_body}" RELEASE_NAME_ENV="${release_name}" TAG_NAME_ENV="${tag_name}" MAKE_LATEST_ENV="${make_latest}" python3 - <<'PY'
import json, os
print(json.dumps({
  'name': os.environ['RELEASE_NAME_ENV'],
  'tag_name': os.environ['TAG_NAME_ENV'],
  'body': os.environ['RELEASE_BODY_ENV'],
  'draft': False,
  'prerelease': False,
  'make_latest': os.environ['MAKE_LATEST_ENV'],
}))
PY
)" \
      "${API_ROOT}/releases/${ENSURE_RELEASE_ID}" >/dev/null
  else
    release_json="$(curl -fsSL -X POST "${auth_header[@]}" -H 'Content-Type: application/json' \
      -d "$(RELEASE_BODY_ENV="${release_body}" RELEASE_NAME_ENV="${release_name}" TAG_NAME_ENV="${tag_name}" MAKE_LATEST_ENV="${make_latest}" python3 - <<'PY'
import json, os
print(json.dumps({
  'tag_name': os.environ['TAG_NAME_ENV'],
  'target_commitish': 'main',
  'name': os.environ['RELEASE_NAME_ENV'],
  'body': os.environ['RELEASE_BODY_ENV'],
  'draft': False,
  'prerelease': False,
  'make_latest': os.environ['MAKE_LATEST_ENV'],
}))
PY
)" "${API_ROOT}/releases")"
    set_release_meta "${release_json}"
  fi
}

delete_named_assets() {
  local release_id="$1"
  shift
  [ "$#" -gt 0 ] || return 0
  local assets_json
  assets_json="$(api_json "${API_ROOT}/releases/${release_id}/assets?per_page=100")"
  while IFS=$'\t' read -r asset_id asset_name; do
    [ -n "${asset_id}" ] || continue
    curl -fsSL -X DELETE "${auth_header[@]}" "${API_ROOT}/releases/assets/${asset_id}" >/dev/null
  done < <(
    python3 - <<'PY' "${assets_json}" "$@"
import json, sys
payload = json.loads(sys.argv[1])
names = set(sys.argv[2:])
for asset in payload:
    if asset.get('name') in names:
        print(f"{asset.get('id', '')}\t{asset.get('name', '')}")
PY
  )
}

release_has_asset() {
  local release_id="$1"
  local asset_name="$2"
  python3 - <<'PY' "$(api_json "${API_ROOT}/releases/${release_id}/assets?per_page=100")" "${asset_name}"
import json, sys
payload = json.loads(sys.argv[1])
target = sys.argv[2]
raise SystemExit(0 if any(asset.get('name') == target for asset in payload) else 1)
PY
}

upload_asset() {
  local upload_url="$1"
  local asset_path="$2"
  local asset_name
  asset_name="$(basename "${asset_path}")"
  echo "uploading ${asset_name}"
  curl -fL --http1.1 --retry 5 --retry-delay 2 --retry-all-errors --progress-bar \
    -X POST \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H 'Accept: application/vnd.github+json' \
    -H 'X-GitHub-Api-Version: 2022-11-28' \
    -H 'Content-Type: application/octet-stream' \
    --data-binary @"${asset_path}" \
    "${upload_url}?name=${asset_name}" >/dev/null
}

RUNTIME_RELEASE_BODY="$(cat <<EOF
Reusable runtime payload for Horosa desktop releases.

This release stores the shared runtime archive used by installer/bootstrap flows.
EOF
)"

ensure_release "${TAG_NAME}" "${RELEASE_NAME}" "${RELEASE_BODY}" "true"
APP_RELEASE_ID="${ENSURE_RELEASE_ID}"
APP_UPLOAD_URL="${ENSURE_UPLOAD_URL}"

delete_named_assets "${APP_RELEASE_ID}" "${DESKTOP_PKG_ZIP}" "${DESKTOP_PKG}" "${DESKTOP_ASSET}" "${UPDATE_MANIFEST_NAME}" "${RUNTIME_ASSET}"

for asset in "${APP_ASSETS[@]}"; do
  upload_asset "${APP_UPLOAD_URL}" "${asset}"
done

if [ "${RUNTIME_TAG_NAME}" = "${TAG_NAME}" ]; then
  upload_asset "${APP_UPLOAD_URL}" "${RUNTIME_ARCHIVE_PATH}"
  RUNTIME_RELEASE_ID="${APP_RELEASE_ID}"
else
  ensure_release "${RUNTIME_TAG_NAME}" "${RUNTIME_TAG_NAME}" "${RUNTIME_RELEASE_BODY}" "false"
  RUNTIME_RELEASE_ID="${ENSURE_RELEASE_ID}"
  RUNTIME_UPLOAD_URL="${ENSURE_UPLOAD_URL}"
  if [ "${HOROSA_FORCE_RUNTIME_UPLOAD:-0}" = "1" ]; then
    delete_named_assets "${RUNTIME_RELEASE_ID}" "${RUNTIME_ASSET}"
    upload_asset "${RUNTIME_UPLOAD_URL}" "${RUNTIME_ARCHIVE_PATH}"
  elif release_has_asset "${RUNTIME_RELEASE_ID}" "${RUNTIME_ASSET}"; then
    echo "runtime asset already present on ${RUNTIME_TAG_NAME}; skipping upload"
  else
    upload_asset "${RUNTIME_UPLOAD_URL}" "${RUNTIME_ARCHIVE_PATH}"
  fi
fi

LATEST_MANIFEST_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/latest/download/${UPDATE_MANIFEST_NAME}"
LATEST_MANIFEST=""
for _ in $(seq 1 20); do
  if LATEST_MANIFEST="$(curl -fsSL -H 'Cache-Control: no-cache' -H 'Pragma: no-cache' "${LATEST_MANIFEST_URL}" 2>/dev/null)"; then
    if python3 - <<'PY' "${LATEST_MANIFEST}" "${VERSION}" "${TAG_NAME}" >/dev/null 2>&1
import json, sys
manifest = json.loads(sys.argv[1])
raise SystemExit(0 if manifest.get('version') == sys.argv[2] and manifest.get('tag') == sys.argv[3] else 1)
PY
    then
      break
    fi
  fi
  sleep 3
done

if [ -z "${LATEST_MANIFEST}" ]; then
  echo "failed to fetch latest manifest after release publish" >&2
  exit 1
fi

python3 - <<'PY' "${LATEST_MANIFEST}" "${VERSION}" "${TAG_NAME}" "${RUNTIME_TAG_NAME}" "${DESKTOP_ASSET}" "${RUNTIME_ASSET}"
import json, sys
manifest = json.loads(sys.argv[1])
if manifest['version'] != sys.argv[2]:
    raise SystemExit(f"latest manifest version mismatch: {manifest['version']} != {sys.argv[2]}")
if manifest.get('tag') != sys.argv[3]:
    raise SystemExit(f"latest manifest tag mismatch: {manifest.get('tag')} != {sys.argv[3]}")
platform = next(iter(manifest['platforms'].values()))
if f"/releases/download/{sys.argv[3]}/" not in platform['appUrl']:
    raise SystemExit('latest manifest appUrl tag mismatch')
if not platform['appUrl'].endswith('/' + sys.argv[5]):
    raise SystemExit('latest manifest appUrl mismatch')
if f"/releases/download/{sys.argv[4]}/" not in platform['runtimeUrl']:
    raise SystemExit('latest manifest runtimeUrl tag mismatch')
if not platform['runtimeUrl'].endswith('/' + sys.argv[6]):
    raise SystemExit('latest manifest runtimeUrl mismatch')
PY

echo "release published: ${TAG_NAME}"
echo "latest manifest: ${LATEST_MANIFEST_URL}"
