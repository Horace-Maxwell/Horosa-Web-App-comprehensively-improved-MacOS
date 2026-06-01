#!/usr/bin/env bash
# 把当前版本同步到 GitCode 国内镜像（方案乙：自动化能自动的，手动步骤给清单）。
#
# 背景（实测）：GitCode 仓库是只读 Pull 镜像 →
#   - 源码/tags：不能 push，靠 GitCode「仓库镜像」每天自动同步，或在镜像设置页点「更新」立即同步（≤5min）。
#   - 发行版条目+说明：可用 API 创建（private-token 头），但无法改/删（API 不返回 release id）。
#   - 二进制附件：无上传 API（≤2G 限制），只能网页手动上传。
# 因此本脚本：①确认 tag 已同步到 GitCode；②用 API 创建该版本发行版并写入真实说明（已存在则跳过）；
#            ③打印「源码同步 + 二进制手动上传」清单。
#
# 用法：Horosa_Desktop_Installer/scripts/mirror_to_gitcode.sh
# token：取自 env GITCODE_TOKEN，否则 .claude/settings.local.json 的 env.GITCODE_TOKEN。
# 可选 env：GITCODE_OWNER（默认 HoraceDong_C137）、GITCODE_REPO（默认同 release_config.repoName）。
set -uo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "${INSTALLER_ROOT}/.." && pwd)"
DIST="${INSTALLER_ROOT}/dist"

read -r VERSION RUNTIME_VERSION REPO_NAME GH_OWNER <<EOF
$(python3 - "$INSTALLER_ROOT" <<'PY'
import json, os, sys
root = sys.argv[1]
cfg = json.load(open(os.path.join(root, 'config/release_config.json')))
ver = json.load(open(os.path.join(root, 'package.json')))['version']
rv = str(cfg.get('runtimeVersion') or ver).strip() or ver
print(ver, rv, cfg['repoName'], cfg['repoOwner'])
PY
)
EOF

TAG="v${VERSION}"
RUNTIME_TAG="v${RUNTIME_VERSION}"
GITCODE_OWNER="${GITCODE_OWNER:-HoraceDong_C137}"
GITCODE_REPO="${GITCODE_REPO:-${REPO_NAME}}"
API="https://api.gitcode.com/api/v5/repos/${GITCODE_OWNER}/${GITCODE_REPO}"
GITCODE_URL="https://gitcode.com/${GITCODE_OWNER}/${GITCODE_REPO}"
GH_TAG_URL="https://github.com/${GH_OWNER}/${REPO_NAME}/releases/tag/${TAG}"

TOKEN="${GITCODE_TOKEN:-}"
if [ -z "${TOKEN}" ] && [ -f "${REPO_ROOT}/.claude/settings.local.json" ]; then
  TOKEN="$(python3 -c "import json;print(json.load(open('${REPO_ROOT}/.claude/settings.local.json')).get('env',{}).get('GITCODE_TOKEN',''))" 2>/dev/null || true)"
fi
[ -n "${TOKEN}" ] || { echo "缺 GITCODE_TOKEN（设到 env 或 .claude/settings.local.json 的 env 里）" >&2; exit 1; }

echo "== GitCode 镜像同步：${GITCODE_OWNER}/${GITCODE_REPO}  版本 ${TAG} =="

# ① 确认 tag 已被 GitCode 镜像同步过来（GitCode 只读，发行版必须挂在已存在的 tag 上）
if ! GIT_TERMINAL_PROMPT=0 git ls-remote --tags "${GITCODE_URL}.git" "${TAG}" 2>/dev/null | grep -q "refs/tags/${TAG}$"; then
  echo ""
  echo "⚠️ GitCode 上还没有 ${TAG} 标签——镜像尚未同步。"
  echo "   先到 ${GITCODE_URL}  →  仓库设置 → 仓库镜像，点「更新」立即同步（≤5min）；"
  echo "   等 ${TAG} 出现后再重跑本脚本即可创建发行版。"
  exit 0
fi

# ② 创建发行版 + 真实说明（已存在则跳过，因为 API 改不了）
create_release() {
  local tag="$1" notes_file="$2"
  local body payload code
  body="$( { [ -f "${notes_file}" ] && cat "${notes_file}"; printf '\n完整说明与校验和见 GitHub Release：%s\n' "${GH_TAG_URL}"; } )"
  payload="$(BODY="${body}" TAG="${tag}" python3 -c "import json,os;print(json.dumps({'tag_name':os.environ['TAG'],'name':os.environ['TAG']+' Beta','body':os.environ['BODY'],'target_commitish':'main','prerelease':False}))")"
  code="$(curl -s -o /tmp/gc_mirror.json -w '%{http_code}' -m 30 -X POST "${API}/releases" \
    -H 'Content-Type: application/json' -H "private-token: ${TOKEN}" -d "${payload}")"
  case "${code}" in
    200|201) echo "  ✅ 已创建 GitCode 发行版 ${tag}（含真实说明）";;
    400|409)
      if grep -q "already exists" /tmp/gc_mirror.json 2>/dev/null; then
        echo "  ⏭️  ${tag} 发行版已存在，跳过（API 无法更新；如需改说明请到 GitCode 网页编辑）"
      else
        echo "  ❌ ${tag} 创建失败（${code}）：$(sed "s|${TOKEN}|***|g" /tmp/gc_mirror.json | head -c 200)"
      fi;;
    *) echo "  ❌ ${tag} 创建失败（${code}）：$(sed "s|${TOKEN}|***|g" /tmp/gc_mirror.json | head -c 200)";;
  esac
  rm -f /tmp/gc_mirror.json
}

echo "[1/2] 创建发行版条目 + 写入真实说明"
create_release "${TAG}" "${INSTALLER_ROOT}/config/release_notes/${VERSION}.md"
if GIT_TERMINAL_PROMPT=0 git ls-remote --tags "${GITCODE_URL}.git" "${RUNTIME_TAG}" 2>/dev/null | grep -q "refs/tags/${RUNTIME_TAG}$"; then
  create_release "${RUNTIME_TAG}" "/dev/null"
fi

# ③ 需要手动的两步
echo ""
echo "[2/2] 还需手动两步（GitCode 只读镜像 + 无附件上传 API）："
echo "  (a) 源码同步：${GITCODE_URL} → 仓库设置 → 仓库镜像 → 点「更新」（确保 main 也追上 GitHub）。"
echo "  (b) 上传安装包到发行版附件（≤2G）：打开 ${GITCODE_URL}/releases/tag/${TAG} ，把以下文件拖进附件："
for f in "Horosa-Installer-macos-arm64-offline.pkg" "Horosa-Desktop-macos-arm64.zip" "horosa-latest.json"; do
  [ -f "${DIST}/${f}" ] && echo "        ${DIST}/${f}"
done
if [ -f "${DIST}/horosa-runtime-macos-arm64.tar.gz" ]; then
  echo "      （runtime 包如需镜像：${DIST}/horosa-runtime-macos-arm64.tar.gz → 传到 ${GITCODE_URL}/releases/tag/${RUNTIME_TAG}）"
fi
echo "完成。"
