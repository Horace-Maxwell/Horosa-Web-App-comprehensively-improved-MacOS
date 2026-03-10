#!/usr/bin/env bash
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_ROOT="${INSTALLER_ROOT}/dist"

read -r REPO_OWNER REPO_NAME TAG_PREFIX VERSION RUNTIME_ASSET DESKTOP_ASSET DESKTOP_PKG DESKTOP_PKG_ZIP UPDATE_MANIFEST_NAME <<EOF
$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PY'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
version = json.loads((root / 'package.json').read_text())['version']
print(
    config['repoOwner'],
    config['repoName'],
    config['releaseTagPrefix'],
    version,
    config['runtimeAssetName'],
    config['desktopAssetName'],
    config['desktopPkgName'],
    config['desktopPkgZipName'],
    config['updateManifestName'],
)
PY
)
EOF

TAG_NAME="${TAG_PREFIX}${VERSION}"
RELEASE_NAME="Horosa ${TAG_NAME}"
API_ROOT="https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}"
PRIMARY_DOWNLOAD="${DESKTOP_PKG_ZIP}"
ASSETS=(
  "${DIST_ROOT}/${DESKTOP_PKG_ZIP}"
  "${DIST_ROOT}/${DESKTOP_PKG}"
  "${DIST_ROOT}/${DESKTOP_ASSET}"
  "${DIST_ROOT}/${RUNTIME_ASSET}"
  "${DIST_ROOT}/${UPDATE_MANIFEST_NAME}"
)

for asset in "${ASSETS[@]}"; do
  [ -f "${asset}" ] || {
    echo "missing asset: ${asset}" >&2
    exit 1
  }
done

if [ "${HOROSA_SKIP_VERIFY:-0}" != "1" ]; then
  "${INSTALLER_ROOT}/scripts/verify_desktop_packaging.sh"
fi

if [ "${HOROSA_REQUIRE_SIGNED_PUBLIC_RELEASE:-0}" = "1" ]; then
  "${INSTALLER_ROOT}/scripts/verify_public_distribution_readiness.sh"
fi

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

RELEASE_BODY="$(cat <<EOF
## 主下载 / Main Download

普通用户只需要下载这一个文件：

Ordinary users only need to download this file:

- [${PRIMARY_DOWNLOAD}](https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/download/${TAG_NAME}/${PRIMARY_DOWNLOAD})

## 使用范围 / Intended Use

这是一套未签名分发方案，仅适合开发者自用或少量熟人机器。

This is an unsigned distribution flow intended only for developer self-use or a small circle of trusted users.

- 仅支持 Apple Silicon Mac
- 需要 macOS 12 或更高版本
- 首次安装或打开时，可能需要右键打开、移除 quarantine，或在“系统设置 -> 隐私与安全性”里允许本次打开

- Apple Silicon Macs only
- Requires macOS 12 or later
- On first install/open, you may need to right-click Open, remove quarantine, or allow the blocked item in System Settings -> Privacy & Security

## 安装步骤（中文）

1. 解压 zip
2. 先双击里面的 Open-XingQue-Unsigned.command
3. 如果系统仍拦截，再对 .pkg 安装包点右键 -> 打开
4. 完成安装
5. 如果 /Applications/星阙.app 第一次被拦截，再次运行同一个 .command，或对 app 点右键 -> 打开

## Install Steps (English)

1. Unzip it
2. Run Open-XingQue-Unsigned.command first
3. If macOS still blocks it, right-click the .pkg installer and choose Open
4. Finish installation
5. If /Applications/星阙.app is blocked on first launch, run the same .command again, or right-click the app and choose Open

普通用户不需要手动下载任何其他文件。

No one else needs to manually download any other file.

## 技术资产 / Technical Assets

此 Release 中其余资产是安装器与自动更新器使用的内部支持文件，普通用户可以忽略。

The remaining assets in this release are internal support files for the installer and auto-updater. Ordinary users should ignore them.
EOF
)"
export RELEASE_BODY

api_json() {
  curl -fsSL "${auth_header[@]}" "$@"
}

release_json=""
if release_json="$(api_json "${API_ROOT}/releases/tags/${TAG_NAME}" 2>/dev/null)"; then
  RELEASE_ID="$(python3 - <<'PY' "${release_json}"
import json, sys
print(json.loads(sys.argv[1])['id'])
PY
)"
  upload_url="$(python3 - <<'PY' "${release_json}"
import json, sys
print(json.loads(sys.argv[1])['upload_url'].split('{', 1)[0])
PY
)"
  curl -fsSL -X PATCH "${auth_header[@]}" -H 'Content-Type: application/json' \
    -d "$(python3 - <<'PY' "${RELEASE_NAME}" "${TAG_NAME}"
import json, os, sys
print(json.dumps({
  'name': sys.argv[1],
  'tag_name': sys.argv[2],
  'body': os.environ['RELEASE_BODY'],
  'draft': False,
  'prerelease': False,
  'make_latest': 'true',
}))
PY
)" \
    "${API_ROOT}/releases/${RELEASE_ID}" >/dev/null
else
  create_payload="$(python3 - <<'PY' "${TAG_NAME}" "${RELEASE_NAME}"
import json, os, sys
print(json.dumps({
  'tag_name': sys.argv[1],
  'target_commitish': 'main',
  'name': sys.argv[2],
  'body': os.environ['RELEASE_BODY'],
  'draft': False,
  'prerelease': False,
  'make_latest': 'true',
}))
PY
)"
  release_json="$(curl -fsSL -X POST "${auth_header[@]}" -H 'Content-Type: application/json' -d "${create_payload}" "${API_ROOT}/releases")"
  RELEASE_ID="$(python3 - <<'PY' "${release_json}"
import json, sys
print(json.loads(sys.argv[1])['id'])
PY
)"
  upload_url="$(python3 - <<'PY' "${release_json}"
import json, sys
print(json.loads(sys.argv[1])['upload_url'].split('{', 1)[0])
PY
)"
fi

assets_json="$(api_json "${API_ROOT}/releases/${RELEASE_ID}/assets?per_page=100")"
python3 - <<'PY' "${assets_json}" "${API_ROOT}" "${GITHUB_TOKEN}" "${DESKTOP_PKG_ZIP}" "${DESKTOP_PKG}" "${DESKTOP_ASSET}" "${RUNTIME_ASSET}" "${UPDATE_MANIFEST_NAME}"
import json, sys, urllib.request
assets = json.loads(sys.argv[1])
api_root = sys.argv[2]
token = sys.argv[3]
targets = set(sys.argv[4:])
for asset in assets:
    if asset.get('name') in targets:
        req = urllib.request.Request(
            f"{api_root}/releases/assets/{asset['id']}",
            method='DELETE',
            headers={
                'Authorization': f'Bearer {token}',
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28',
            },
        )
        urllib.request.urlopen(req).read()
PY

for asset in "${ASSETS[@]}"; do
  asset_name="$(basename "${asset}")"
  echo "uploading ${asset_name}"
  curl -fsSL --progress-bar \
    -X POST \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H 'Accept: application/vnd.github+json' \
    -H 'X-GitHub-Api-Version: 2022-11-28' \
    -H 'Content-Type: application/octet-stream' \
    --data-binary @"${asset}" \
    "${upload_url}?name=${asset_name}" >/dev/null
done

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

python3 - <<'PY' "${LATEST_MANIFEST}" "${VERSION}" "${TAG_NAME}" "${DESKTOP_ASSET}" "${RUNTIME_ASSET}"
import json, sys
manifest = json.loads(sys.argv[1])
if manifest['version'] != sys.argv[2]:
    raise SystemExit(f"latest manifest version mismatch: {manifest['version']} != {sys.argv[2]}")
if manifest.get('tag') != sys.argv[3]:
    raise SystemExit(f"latest manifest tag mismatch: {manifest.get('tag')} != {sys.argv[3]}")
platform = next(iter(manifest['platforms'].values()))
if not platform['appUrl'].endswith('/' + sys.argv[4]):
    raise SystemExit('latest manifest appUrl mismatch')
if not platform['runtimeUrl'].endswith('/' + sys.argv[5]):
    raise SystemExit('latest manifest runtimeUrl mismatch')
PY

echo "release published: ${TAG_NAME}"
echo "latest manifest: ${LATEST_MANIFEST_URL}"
