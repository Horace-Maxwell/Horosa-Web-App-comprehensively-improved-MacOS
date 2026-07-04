#!/usr/bin/env bash
set -euo pipefail

# 发布硬闸(制度,2026-06-12):任何 release 发布前必须完成人工安装验收。
# 流程 = 打包 → 用户亲手安装 .pkg 实测 → 确认后 HOROSA_USER_TESTED=1 重跑本脚本。
if [ "${HOROSA_USER_TESTED:-0}" != "1" ]; then
  echo "⛔ 发布中止:本 release 尚未经人工安装验收。" >&2
  echo "   请先安装 dist/ 下的 .pkg 完整手测;确认无误后:HOROSA_USER_TESTED=1 bash $0" >&2
  exit 1
fi

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_ROOT="${INSTALLER_ROOT}/dist"
read -r REPO_OWNER REPO_NAME TAG_PREFIX VERSION TAG_NAME RUNTIME_TAG_NAME RUNTIME_ASSET DESKTOP_ASSET DESKTOP_PKG DESKTOP_PKG_ZIP DESKTOP_OFFLINE_PKG DESKTOP_OFFLINE_PKG_ZIP UPDATE_MANIFEST_NAME RUNTIME_VERSION PRIMARY_DOWNLOAD SUPPORTED_ARCH RELEASE_CHANNEL RELEASE_PRERELEASE_CONFIG RELEASE_MAKE_LATEST_CONFIG <<EOF
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
    config.get('primaryDownload', config['desktopOfflinePkgName']),
    config.get('supportedArch', 'arm64'),
    config.get('releaseChannel', 'stable'),
    str(config.get('releasePrerelease', 'auto')).lower(),
    str(config.get('releaseMakeLatest', 'auto')).lower(),
)
PY
)
EOF

RELEASE_CHANNEL="${HOROSA_RELEASE_CHANNEL:-${RELEASE_CHANNEL}}"
RELEASE_PRERELEASE="false"
APP_MAKE_LATEST="true"
RELEASE_CHANNEL_LABEL=""
case "$(printf '%s' "${RELEASE_CHANNEL}" | tr '[:upper:]' '[:lower:]')" in
  beta|preview|prerelease|pre-release)
    RELEASE_PRERELEASE="true"
    APP_MAKE_LATEST="${HOROSA_RELEASE_MAKE_LATEST:-false}"
    RELEASE_CHANNEL_LABEL="Beta"
    ;;
  *)
    APP_MAKE_LATEST="${HOROSA_RELEASE_MAKE_LATEST:-true}"
    ;;
esac
if [ "${RELEASE_PRERELEASE_CONFIG}" != "auto" ]; then
  RELEASE_PRERELEASE="${HOROSA_RELEASE_PRERELEASE:-${RELEASE_PRERELEASE_CONFIG}}"
else
  RELEASE_PRERELEASE="${HOROSA_RELEASE_PRERELEASE:-${RELEASE_PRERELEASE}}"
fi
if [ "${RELEASE_MAKE_LATEST_CONFIG}" != "auto" ]; then
  APP_MAKE_LATEST="${HOROSA_RELEASE_MAKE_LATEST:-${RELEASE_MAKE_LATEST_CONFIG}}"
fi
RELEASE_NAME="${TAG_NAME}${RELEASE_CHANNEL_LABEL:+ ${RELEASE_CHANNEL_LABEL}}"
API_ROOT="https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}"
README_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/blob/${TAG_NAME}/README.md"
README_EN_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/blob/${TAG_NAME}/README_EN.md"
README_ZH_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/blob/${TAG_NAME}/README_ZH.md"
INSTALLER_README_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/blob/${TAG_NAME}/Horosa_Desktop_Installer/README.md"
APP_ASSETS=(
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

# ── 更新通道隔离硬闸:待传产物的身份必须与「本仓自身配置」一致,防止把别处构建的产物
#    误传进本仓 release(用户的自动更新会原样吞下)。期望值全部派生自本仓 tauri.conf,
#    不写死任何外部值;任一不符立即中止,绝不带病上传。
EXPECTED_IDENTIFIER="$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 -c "import json,os;print(json.load(open(os.environ['INSTALLER_ROOT_ENV']+'/src-tauri/tauri.conf.json'))['identifier'])")"
EXPECTED_PRODUCT="$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 -c "import json,os;print(json.load(open(os.environ['INSTALLER_ROOT_ENV']+'/src-tauri/tauri.conf.json'))['productName'])")"
IDENTITY_TMP="$(mktemp -d /tmp/horosa-publish-identity.XXXXXX)"
trap 'rm -rf "${IDENTITY_TMP}"' EXIT
unzip -qq "${DIST_ROOT}/${DESKTOP_ASSET}" "*/Contents/Info.plist" -d "${IDENTITY_TMP}" 2>/dev/null || true
ACTUAL_PLIST="$(/usr/bin/find "${IDENTITY_TMP}" -name Info.plist -path "*/Contents/Info.plist" 2>/dev/null | head -1)"
if [ -z "${ACTUAL_PLIST}" ]; then
  echo "更新通道隔离硬闸: 无法从 ${DESKTOP_ASSET} 解出 Info.plist,拒绝发布" >&2
  exit 1
fi
ACTUAL_IDENTIFIER="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "${ACTUAL_PLIST}" 2>/dev/null || true)"
if [ "${ACTUAL_IDENTIFIER}" != "${EXPECTED_IDENTIFIER}" ]; then
  echo "更新通道隔离硬闸: 产物 bundle identifier(${ACTUAL_IDENTIFIER}) ≠ 本仓期望(${EXPECTED_IDENTIFIER}),拒绝发布" >&2
  exit 1
fi
case "${ACTUAL_PLIST}" in
  *"/${EXPECTED_PRODUCT}.app/Contents/Info.plist") : ;;
  *)
    echo "更新通道隔离硬闸: 产物 .app 名与本仓 productName(${EXPECTED_PRODUCT}) 不符: ${ACTUAL_PLIST}" >&2
    exit 1
    ;;
esac
if ! grep -qF "${REPO_OWNER}/${REPO_NAME}" "${DIST_ROOT}/${UPDATE_MANIFEST_NAME}"; then
  echo "更新通道隔离硬闸: 更新清单 ${UPDATE_MANIFEST_NAME} 不含本仓 ${REPO_OWNER}/${REPO_NAME} 下载源,拒绝发布" >&2
  exit 1
fi
# runtime 包内嵌整套前端(dist-file):必须与「本仓当前 dist-file」逐字节一致,
# 否则说明包来自别处构建(跨仓拷贝/陈旧产物),装机用户的运行时自动下载会吞下它。
RUNTIME_UMI_ENTRY="$(tar -tzf "${RUNTIME_ARCHIVE_PATH}" 2>/dev/null | grep -E 'runtime-payload/Horosa-Web/astrostudyui/dist-file/umi\.[0-9a-f]+\.js$' | head -1)"
if [ -z "${RUNTIME_UMI_ENTRY}" ]; then
  echo "更新通道隔离硬闸: runtime 包内未找到前端主 bundle(dist-file/umi.*.js),拒绝发布" >&2
  exit 1
fi
LOCAL_UMI="${INSTALLER_ROOT}/../Horosa-Web/astrostudyui/dist-file/$(basename "${RUNTIME_UMI_ENTRY}")"
if [ ! -f "${LOCAL_UMI}" ]; then
  echo "更新通道隔离硬闸: runtime 包内嵌前端 $(basename "${RUNTIME_UMI_ENTRY}") 在本仓 dist-file 不存在 —— 包非本仓当前构建,拒绝发布" >&2
  exit 1
fi
RUNTIME_UMI_SHA="$(tar -xOzf "${RUNTIME_ARCHIVE_PATH}" "${RUNTIME_UMI_ENTRY}" | shasum -a 256 | awk '{print $1}')"
LOCAL_UMI_SHA="$(shasum -a 256 "${LOCAL_UMI}" | awk '{print $1}')"
if [ "${RUNTIME_UMI_SHA}" != "${LOCAL_UMI_SHA}" ]; then
  echo "更新通道隔离硬闸: runtime 包内嵌前端与本仓 dist-file 内容不一致,拒绝发布(请在本仓重新完整构建)" >&2
  exit 1
fi
echo "更新通道隔离硬闸: identifier/产品名/清单源/runtime内嵌前端 四项一致(${EXPECTED_IDENTIFIER}) ✓"

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

# Pre-flight self-check: encodes the process-review findings (version lockstep, per-version
# release notes, secrets not tracked, config JSON valid, artifact freshness, CI green).
# HOROSA_SKIP_PREFLIGHT=1 overrides only when you are certain.
if [ "${HOROSA_SKIP_PREFLIGHT:-0}" != "1" ]; then
  "${INSTALLER_ROOT}/scripts/release_preflight.sh" || {
    echo "release_preflight 失败,发布中止。修复后重试,或确认无误时设 HOROSA_SKIP_PREFLIGHT=1。" >&2
    exit 1
  }
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
    if [ "${REMOTE_RUNTIME_SHA}" != "${EXPECTED_RUNTIME_SHA}" ]; then
      echo "runtime payload changed, but release_config.json still points to ${RUNTIME_TAG_NAME}." >&2
      echo "local runtime sha:  ${EXPECTED_RUNTIME_SHA}" >&2
      echo "remote runtime sha: ${REMOTE_RUNTIME_SHA}" >&2
      echo "bump runtimeVersion (or set HOROSA_FORCE_RUNTIME_UPLOAD=1) before publishing this release." >&2
      exit 1
    fi
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

python3 - <<'PY' "${DIST_ROOT}/${UPDATE_MANIFEST_NAME}" "${DIST_ROOT}/${DESKTOP_ASSET}" "${DIST_ROOT}/${DESKTOP_OFFLINE_PKG}" "${DESKTOP_ASSET}" "${DESKTOP_OFFLINE_PKG}" "${RUNTIME_ASSET}" "${TAG_NAME}" "${VERSION}" "${RUNTIME_VERSION}" "${RUNTIME_TAG_NAME}" "${EXPECTED_RUNTIME_SHA}"
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
  # Publishing must not rebuild public assets: build_desktop_release.sh is the
  # single place that signs, notarizes, and staples Apple distribution payloads.
  HOROSA_DESKTOP_SKIP_REBUILD=1 "${INSTALLER_ROOT}/scripts/verify_desktop_packaging.sh"
fi

if [ "${HOROSA_REQUIRE_SIGNED_PUBLIC_RELEASE:-${HOROSA_PUBLIC_DISTRIBUTION:-0}}" = "1" ]; then
  "${INSTALLER_ROOT}/scripts/verify_public_distribution_readiness.sh"
fi

RELEASE_BODY="$(
  PRIMARY_DOWNLOAD_ENV="${PRIMARY_DOWNLOAD}" \
  SUPPORTED_ARCH_ENV="${SUPPORTED_ARCH}" \
  VERSION_ENV="${VERSION}" \
  TAG_NAME_ENV="${TAG_NAME}" \
  README_URL_ENV="${README_URL}" \
  README_EN_URL_ENV="${README_EN_URL}" \
  README_ZH_URL_ENV="${README_ZH_URL}" \
  INSTALLER_README_URL_ENV="${INSTALLER_README_URL}" \
  RELEASE_CHANNEL_LABEL_ENV="${RELEASE_CHANNEL_LABEL}" \
  INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" \
  python3 - <<'PY'
import os

primary_download = os.environ["PRIMARY_DOWNLOAD_ENV"]
arch = os.environ["SUPPORTED_ARCH_ENV"]
version = os.environ["VERSION_ENV"]
tag_name = os.environ["TAG_NAME_ENV"]
readme_url = os.environ["README_URL_ENV"]
readme_en_url = os.environ["README_EN_URL_ENV"]
readme_zh_url = os.environ["README_ZH_URL_ENV"]
installer_readme_url = os.environ["INSTALLER_README_URL_ENV"]

# Per-version highlights: if config/release_notes/{version}.md exists, inject it as a
# "本版更新 / What's new" block so the release page reflects the ACTUAL changes,
# not just the generic product overview below. Absent file => unchanged behavior.
import pathlib
_notes_path = pathlib.Path(os.environ.get("INSTALLER_ROOT_ENV", ".")) / "config" / "release_notes" / f"{version}.md"
per_version_lines = []
if _notes_path.is_file():
    _notes_text = _notes_path.read_text(encoding="utf-8").strip()
    if _notes_text:
        per_version_lines = ["", "### 本版更新 / What's new in this release", *_notes_text.splitlines()]

sections = [
    f"# Horosa {version}{' Beta' if os.environ.get('RELEASE_CHANNEL_LABEL_ENV') == 'Beta' else ''}",
    "",
    "Beta release / Beta 测试版：this build is published for hands-on verification before it is promoted as the stable release." if os.environ.get("RELEASE_CHANNEL_LABEL_ENV") == "Beta" else "",
    "Beta 测试版：本构建用于稳定版前的真实安装与使用检查；安装包、runtime 与 manifest 已完成签名、公证和端到端验证。" if os.environ.get("RELEASE_CHANNEL_LABEL_ENV") == "Beta" else "",
    "",
    "Horosa is a local-first metaphysics workstation for Apple Silicon, spanning Western astrology, Chinese traditional systems, AI-assisted analysis, and a notarized desktop delivery stack.",
    "Horosa 是面向 Apple Silicon 的本地优先玄学工作站，覆盖西方占星、中国传统术数、AI 辅助分析，以及正式公证的桌面交付链路。",
    "",
    "## 当前版本亮点 / Release Highlights",
    f"- 当前发布版本 / Current release: `{tag_name}`{(' Beta' if os.environ.get('RELEASE_CHANNEL_LABEL_ENV') == 'Beta' else '')}",
    *per_version_lines,
    f"- `{tag_name}` 是桌面发布线的 beta 扩展版，重点覆盖新命法/卜法后端、本地数据管理、结构化 AI 导出、设置持久化与明暗主题。",
    f"- `{tag_name}` is a beta expansion of the desktop release train, focused on new traditional-method engines, local data management, structured AI export, persistent settings, and light/dark UI polish.",
    "- 新增并规范接入太乙、金口诀、皇极经世、五兆、太玄、荆诀、神易数、Kin Astro、七政四余、奇门等命法与卜法后端。",
    "- Added and normalized backend integrations for Taiyi, Jin Kou, Huangji/Wangji, Wuzhao, Taixuan, Jingjue, Shenyishu, Kin Astro, Qizheng, Qimen, and related specialty methods.",
    "- 三式合一中奇门与太乙固定走 kentang2017 后端口径，六壬保留现有本地六壬实现。",
    "- Sanshi United routes Qimen and Taiyi through the kentang2017 backend while LiuReng remains on the existing local LiuReng implementation.",
    "- 奇门和三式合一页面已移除后端不支持的月家奇门选项，不再静默回退到旧本地算法。",
    "- Unsupported Qimen month-chart selection was removed from Qimen and Sanshi surfaces instead of silently falling back to the old local calculation.",
    "- 管理命盘与管理事盘会保留新技法输入、标签、快照、后端原始结构化数据、JSON 导入导出与重开恢复行为。",
    "- Chart management and case management preserve new-method inputs, tags, snapshots, raw backend payloads, JSON import/export, and reopening behavior.",
    "- AI 导出直接读取结构化后端数据，并为每个支持技法、tab 与页面提供可勾选导出分段。",
    "- AI export reads structured backend data and exposes selectable export groups for each supported technique, tab, and page.",
    "- 用户设置、桌面窗口大小与必要 UI 选项会在关闭、重开和版本更新后继续沿用。",
    "- User settings, desktop window size, and necessary UI choices persist across close/reopen and app updates.",
    "- 启动控制台采用 Daily / Offline Ready / Failed 共用骨架，实时跟随后端进度，并统一使用新版星阙 icon。",
    "- The startup console now uses one shared Daily / Offline Ready / Failed skeleton, follows real backend progress, and consistently uses the new Xingque icon.",
    "- 窗口恢复已按首个可见帧验收，避免重开时先大后小或大小跳动。",
    "- Window restoration is verified from the first visible frame to prevent launch-size flashing or bouncing.",
    "- 全局明暗主题、下拉层、弹层、加载态、管理列表与导出控件已再次检查并打磨。",
    "- App-wide light/dark mode contrast, dropdowns, overlays, loading states, management lists, and export controls were audited and polished.",
    "- 保留此前奇门遁甲一致性与桌面交付修复。",
    "- Previous Qimen Dunjia parity and desktop delivery fixes remain preserved.",
    "",
    "## 下载 / Download",
    f"- 推荐安装包 / Recommended download: `{primary_download}`",
    "- 适合普通用户、中国大陆、弱网和离线转发场景。",
    "- Best for ordinary users, weak-network environments, and offline forwarding.",
    f"- 当前平台目标 / Platform target: Apple Silicon (`{arch}`)",
    "",
    "## 安装步骤 / Installation",
    f"1. 下载 / Download `{primary_download}`",
    "2. 双击 `.pkg` 开始安装 / Double-click the `.pkg` to start installation",
    "3. 安装完成后直接打开 `/Applications/星阙.app` / Open `/Applications/星阙.app` after install",
    "4. 如系统提示安全确认，请在“系统设置 -> 隐私与安全性”中放行 / If macOS asks for confirmation, allow it in System Settings -> Privacy & Security",
    "",
    "## 仓库入口 / Repository Entry Points",
    f"- [README portal]({readme_url})",
    f"- [README English]({readme_en_url})",
    f"- [README 中文]({readme_zh_url})",
    f"- [Installer README]({installer_readme_url})",
    "",
    "## 自动更新与桌面交付 / Auto-Update And Desktop Delivery",
    "- 自动更新继续依赖 `horosa-latest.json`、桌面安装包与独立 runtime 资产，不要求改变客户端协议。",
    "- Auto-update continues to rely on `horosa-latest.json`, desktop release assets, and the separate runtime artifact without changing the client protocol.",
    "",
    "## 已知限制 / Known Limitations",
    "- 仓库中的一部分 legacy 模块仍保留较强的本地运行和内部依赖假设。",
    "- Some legacy modules in the repository still assume a strongly local runtime environment and internal dependency chain.",
    "",
    "## 技术资产 / Technical Assets",
    "此 Release 中其余资产是安装器与自动更新器使用的内部支持文件，普通用户可以忽略。",
    "The remaining assets in this release are internal support files for the installer and auto-updater. Ordinary users should ignore them.",
]

print("\n".join(sections).replace("\n\n\n", "\n\n"))
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
  local prerelease="$5"
  local release_json=""
  if release_json="$(api_json "${API_ROOT}/releases/tags/${tag_name}" 2>/dev/null)"; then
    set_release_meta "${release_json}"
    curl -fsSL -X PATCH "${auth_header[@]}" -H 'Content-Type: application/json' \
      -d "$(RELEASE_BODY_ENV="${release_body}" RELEASE_NAME_ENV="${release_name}" TAG_NAME_ENV="${tag_name}" MAKE_LATEST_ENV="${make_latest}" PRERELEASE_ENV="${prerelease}" python3 - <<'PY'
import json, os
print(json.dumps({
  'name': os.environ['RELEASE_NAME_ENV'],
  'tag_name': os.environ['TAG_NAME_ENV'],
  'body': os.environ['RELEASE_BODY_ENV'],
  'draft': False,
  'prerelease': os.environ['PRERELEASE_ENV'] == 'true',
  'make_latest': os.environ['MAKE_LATEST_ENV'],
}))
PY
)" \
      "${API_ROOT}/releases/${ENSURE_RELEASE_ID}" >/dev/null
  else
    release_json="$(curl -fsSL -X POST "${auth_header[@]}" -H 'Content-Type: application/json' \
      -d "$(RELEASE_BODY_ENV="${release_body}" RELEASE_NAME_ENV="${release_name}" TAG_NAME_ENV="${tag_name}" MAKE_LATEST_ENV="${make_latest}" PRERELEASE_ENV="${prerelease}" python3 - <<'PY'
import json, os
print(json.dumps({
  'tag_name': os.environ['TAG_NAME_ENV'],
  'target_commitish': 'main',
  'name': os.environ['RELEASE_NAME_ENV'],
  'body': os.environ['RELEASE_BODY_ENV'],
  'draft': False,
  'prerelease': os.environ['PRERELEASE_ENV'] == 'true',
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

ensure_release "${TAG_NAME}" "${RELEASE_NAME}" "${RELEASE_BODY}" "${APP_MAKE_LATEST}" "${RELEASE_PRERELEASE}"
APP_RELEASE_ID="${ENSURE_RELEASE_ID}"
APP_UPLOAD_URL="${ENSURE_UPLOAD_URL}"

# ── 增量更新部件:跨版本 asset 复用决策(必须在 manifest 上传之前——会重写其 url)。
# 真值源=线上 latest manifest 的 components(用户正在用的部件 url/sha):
#   sha 相同 → 沿用旧 url,本次不上传该部件(省带宽,GitHub asset URL 永久有效);
#   sha 不同/线上无 v2 manifest/拉取失败 → 全部上传(复用只是优化,失败恒全传)。
# 决策结果写 ${COMP_UPLOAD_LIST}(待上传文件名,一行一个)并原地重写本地 manifest。
COMP_DIST="${DIST_ROOT}/components"
COMP_UPLOAD_LIST=""
if [ -f "${COMP_DIST}/components-lock.json" ] && [ -f "${DIST_ROOT}/${UPDATE_MANIFEST_NAME}" ]; then
  PREV_MANIFEST_JSON="$(curl -fsSL -H 'Cache-Control: no-cache' "https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/latest/download/${UPDATE_MANIFEST_NAME}" 2>/dev/null || true)"
  COMP_UPLOAD_LIST="$(MANIFEST_PATH="${DIST_ROOT}/${UPDATE_MANIFEST_NAME}" PREV_JSON="${PREV_MANIFEST_JSON}" python3 - <<'PYCOMPREUSE'
import json, os
manifest_path = os.environ['MANIFEST_PATH']
manifest = json.loads(open(manifest_path, encoding='utf-8').read())
try:
    prev = json.loads(os.environ.get('PREV_JSON') or '{}')
except Exception:
    prev = {}
prev_comps = {}
for entry in (prev.get('platforms') or {}).values():
    for c in entry.get('components') or []:
        prev_comps[c['name']] = c
upload = set()
for entry in (manifest.get('platforms') or {}).values():
    for c in entry.get('components') or []:
        old = prev_comps.get(c['name'])
        if old and old.get('sha256') == c['sha256'] and old.get('url'):
            c['url'] = old['url']  # 复用:指向该 sha 首次发布的 release asset
        else:
            upload.add(c['file'])
    if entry.get('components'):
        upload.add('components-lock.json')
open(manifest_path, 'w', encoding='utf-8').write(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print('\n'.join(sorted(upload)))
PYCOMPREUSE
)"

  # [WS-1e·I4] 差分效率下限门:增量制度的自动护栏——无论谁怎么改打包/部件边界,
  # 待上传部件总体积超预算(HOROSA_DELTA_BUDGET_MB,默认 200)或「稳定部件」
  # (py-runtime/jdk-runtime/ephe-data/xuanshi-data/java-lib)意外进上传名单,
  # 发布在此拦下并打印逐部件成因;确属预期(如 JDK/星历升级)用 HOROSA_ALLOW_LARGE_DELTA=1 放行。
  DELTA_GATE_OUT="$(COMP_DIST_ENV="${COMP_DIST}" UPLOAD_LIST_ENV="${COMP_UPLOAD_LIST}" PREV_JSON="${PREV_MANIFEST_JSON}" BUDGET_MB="${HOROSA_DELTA_BUDGET_MB:-200}" python3 - <<'PYDELTAGATE'
import json, os, pathlib
prev = {}
try:
    prev = json.loads(os.environ.get('PREV_JSON') or '{}')
except Exception:
    prev = {}
has_prev_comps = any(e.get('components') for e in (prev.get('platforms') or {}).values())
if not has_prev_comps:
    print('VERDICT=SKIP_NO_BASELINE')
    raise SystemExit(0)
comp_dist = pathlib.Path(os.environ['COMP_DIST_ENV'])
uploads = [l.strip() for l in os.environ['UPLOAD_LIST_ENV'].splitlines() if l.strip()]
budget_mb = int(os.environ['BUDGET_MB'])
stable = {'py-runtime', 'jdk-runtime', 'ephe-data', 'xuanshi-data', 'java-lib'}
lock = json.loads((comp_dist / 'components-lock.json').read_text())
by_file = {c['file']: c['name'] for c in lock['components']}
total = 0
stable_hit = []
for fname in uploads:
    if fname == 'components-lock.json':
        continue
    f = comp_dist / fname
    size = f.stat().st_size if f.is_file() else 0
    total += size
    cname = by_file.get(fname, fname)
    print(f"  - {cname}({fname}): {size/1048576:.1f} MB")
    if cname in stable:
        stable_hit.append(cname)
print(f"delta-upload total: {total/1048576:.1f} MB / budget {budget_mb} MB")
verdict = []
if total > budget_mb * 1048576:
    verdict.append(f"OVER_BUDGET:{total/1048576:.0f}MB>{budget_mb}MB")
if stable_hit:
    verdict.append('STABLE_CHANGED:' + ','.join(sorted(set(stable_hit))))
print('VERDICT=' + (';'.join(verdict) if verdict else 'OK'))
PYDELTAGATE
)"
  echo "${DELTA_GATE_OUT}"
  DELTA_VERDICT="$(printf '%s\n' "${DELTA_GATE_OUT}" | sed -n 's/^VERDICT=//p')"
  case "${DELTA_VERDICT}" in
    OK) : ;;
    SKIP_NO_BASELINE) echo "差分效率门(I4): 线上无 v2 部件基线(首发/拉取失败→全量上传属预期),放行" ;;
    *)
      if [ "${HOROSA_ALLOW_LARGE_DELTA:-0}" = "1" ]; then
        echo "差分效率门(I4): ${DELTA_VERDICT} —— 已按 HOROSA_ALLOW_LARGE_DELTA=1 显式放行" >&2
      else
        echo "差分效率门(I4)拦截: ${DELTA_VERDICT}" >&2
        echo "  · 稳定部件变更或增量总量超 ${HOROSA_DELTA_BUDGET_MB:-200}MB,通常意味着打包/部件边界被无意改动(用户将多下数百 MB)。" >&2
        echo "  · 逐部件成因见上;确属预期(如 JDK/星历升级),用 HOROSA_ALLOW_LARGE_DELTA=1 重跑放行。" >&2
        exit 1
      fi
      ;;
  esac
fi

delete_named_assets "${APP_RELEASE_ID}" "Horosa-Desktop-macos-arm64.dmg" "${DESKTOP_PKG_ZIP}" "${DESKTOP_PKG}" "${DESKTOP_OFFLINE_PKG_ZIP}" "${DESKTOP_OFFLINE_PKG}" "${DESKTOP_ASSET}" "${UPDATE_MANIFEST_NAME}" "${RUNTIME_ASSET}"

for asset in "${APP_ASSETS[@]}"; do
  upload_asset "${APP_UPLOAD_URL}" "${asset}"
done

if [ "${RUNTIME_TAG_NAME}" = "${TAG_NAME}" ]; then
  upload_asset "${APP_UPLOAD_URL}" "${RUNTIME_ARCHIVE_PATH}"
  RUNTIME_RELEASE_ID="${APP_RELEASE_ID}"
  RUNTIME_UPLOAD_URL="${APP_UPLOAD_URL}"
else
  ensure_release "${RUNTIME_TAG_NAME}" "${RUNTIME_TAG_NAME}${RELEASE_CHANNEL_LABEL:+ ${RELEASE_CHANNEL_LABEL}}" "${RUNTIME_RELEASE_BODY}" "false" "${RELEASE_PRERELEASE}"
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

# ── 增量更新部件上传(与 manifest 的部件 url 同归 runtime release):
# 幂等按 GitHub asset digest:同名同 sha=跳过;同名异 sha=产物漂移,删旧重传
# (manifest 的 sha 是本地新值,留旧 asset 会让客户端校验失败)。
if [ -n "${COMP_UPLOAD_LIST}" ]; then
  RUNTIME_ASSETS_JSON="$(api_json "${API_ROOT}/releases/${RUNTIME_RELEASE_ID}/assets?per_page=100")"
  while IFS= read -r comp_file; do
    [ -n "${comp_file}" ] || continue
    comp_path="${COMP_DIST}/${comp_file}"
    [ -f "${comp_path}" ] || { echo "missing component asset: ${comp_path}" >&2; exit 1; }
    local_sha="$(shasum -a 256 "${comp_path}" | awk '{print $1}')"
    remote_sha="$(python3 - <<'PYDIGEST' "${RUNTIME_ASSETS_JSON}" "${comp_file}"
import json, sys
for asset in json.loads(sys.argv[1]):
    if asset.get('name') == sys.argv[2]:
        digest = str(asset.get('digest') or '')
        if digest.startswith('sha256:'):
            print(digest.split(':', 1)[1])
        break
PYDIGEST
)"
    if [ "${remote_sha}" = "${local_sha}" ]; then
      echo "component ${comp_file} already present (sha match); skipping"
      continue
    fi
    if [ -n "${remote_sha}" ]; then
      delete_named_assets "${RUNTIME_RELEASE_ID}" "${comp_file}"
    fi
    upload_asset "${RUNTIME_UPLOAD_URL}" "${comp_path}"
  done <<< "${COMP_UPLOAD_LIST}"
  echo "components uploaded (incremental set): $(echo "${COMP_UPLOAD_LIST}" | tr '\n' ' ')"
fi

if [ "${RELEASE_PRERELEASE}" = "true" ]; then
  LATEST_MANIFEST_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/download/${TAG_NAME}/${UPDATE_MANIFEST_NAME}"
else
  LATEST_MANIFEST_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/latest/download/${UPDATE_MANIFEST_NAME}"
fi
LATEST_MANIFEST=""
for _ in $(seq 1 20); do
  LATEST_MANIFEST="$(curl -fsSL -H 'Cache-Control: no-cache' -H 'Pragma: no-cache' "${LATEST_MANIFEST_URL}" 2>/dev/null || true)"
  if [ -z "${LATEST_MANIFEST}" ]; then
    # 匿名 download URL 可能 404(CDN 未就绪或仓库可见性受限) —— 回退走带凭证的 API 资产端点。
    # 注意:python3 - 的脚本经 heredoc 走 stdin,release JSON 必须经 env 传入(管道会被 heredoc 抢占)。
    MANIFEST_RELEASE_JSON="$(api_json "${API_ROOT}/releases/tags/${TAG_NAME}" 2>/dev/null || true)"
    MANIFEST_ASSET_API_URL="$(RELEASE_JSON_ENV="${MANIFEST_RELEASE_JSON}" UPDATE_MANIFEST_NAME_ENV="${UPDATE_MANIFEST_NAME}" python3 - <<'PYURL' || true
import json, os
try:
    data = json.loads(os.environ.get('RELEASE_JSON_ENV') or '{}')
except Exception:
    data = {}
name = os.environ['UPDATE_MANIFEST_NAME_ENV']
for asset in data.get('assets', []):
    if asset.get('name') == name:
        print(asset.get('url') or '')
        break
PYURL
)"
    if [ -n "${MANIFEST_ASSET_API_URL}" ]; then
      LATEST_MANIFEST="$(curl -fsSL "${auth_header[@]}" -H 'Accept: application/octet-stream' "${MANIFEST_ASSET_API_URL}" 2>/dev/null || true)"
    fi
  fi
  if [ -n "${LATEST_MANIFEST}" ]; then
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
