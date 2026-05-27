#!/usr/bin/env bash
# Release pre-flight self-check —— 在发布前运行,把历次流程复盘发现的漏洞编码成可执行检查。
# 任何一项失败即 exit 1。新发现的检查项请持续追加到这里(见 skill「Pre-flight self-check」)。
#
#   用法:  Horosa_Desktop_Installer/scripts/release_preflight.sh
#   跳过某项:对应 env(见各检查),仅在你确认无误时用。
#
# 设计原则:能强制的就强制(脚本),不要只写在文档里靠自觉。
set -uo pipefail   # 故意不开 -e:要跑完所有检查再汇总

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "${INSTALLER_ROOT}/.." && pwd)"
fail=0
ok()   { printf '  \033[32m✅\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m❌\033[0m %s\n' "$1" >&2; fail=1; }
warn() { printf '  \033[33m⚠️\033[0m  %s\n' "$1"; }

VERSION="$(python3 -c "import json,os;print(json.load(open(os.path.join('${INSTALLER_ROOT}','package.json')))['version'])" 2>/dev/null || echo "")"
RUNTIME_VERSION="$(python3 -c "import json,os;print(json.load(open(os.path.join('${INSTALLER_ROOT}','config','release_config.json'))).get('runtimeVersion',''))" 2>/dev/null || echo "")"
[ -n "${VERSION}" ] || { echo "无法读取 package.json version,终止" >&2; exit 2; }
echo "== Release pre-flight: version ${VERSION} / runtime ${RUNTIME_VERSION} =="

# 1. 版本号 lockstep:所有该带版本号的文件都必须含当前 VERSION
echo "[1] 版本号一致性"
grep -q "\"version\": \"${VERSION}\"" "${INSTALLER_ROOT}/package.json"            && ok "package.json"        || bad "package.json version != ${VERSION}"
grep -q "^version = \"${VERSION}\"" "${INSTALLER_ROOT}/src-tauri/Cargo.toml"       && ok "Cargo.toml"          || bad "Cargo.toml version != ${VERSION}"
grep -q "\"version\": \"${VERSION}\"" "${INSTALLER_ROOT}/src-tauri/tauri.conf.json" && ok "tauri.conf.json"     || bad "tauri.conf.json version != ${VERSION}"
grep -q "version: \"${VERSION}\"" "${REPO_ROOT}/CITATION.cff"                       && ok "CITATION.cff"        || bad "CITATION.cff version != ${VERSION}"
grep -q "APP_VERSION = '${VERSION}'" "${INSTALLER_ROOT}/web/app.js"                 && ok "web/app.js"          || bad "web/app.js APP_VERSION != ${VERSION}"
# Cargo.lock: 本项目包的版本
if awk '/^name = "horosa-desktop-installer"$/{getline; print}' "${INSTALLER_ROOT}/src-tauri/Cargo.lock" | grep -q "version = \"${VERSION}\""; then ok "Cargo.lock"; else bad "Cargo.lock horosa-desktop-installer version != ${VERSION}"; fi
# runtimeVersion 必须是 {VERSION}-runtimeN
case "${RUNTIME_VERSION}" in "${VERSION}-runtime"*) ok "release_config runtimeVersion (${RUNTIME_VERSION})";; *) bad "runtimeVersion '${RUNTIME_VERSION}' 不是 ${VERSION}-runtimeN";; esac

# 2. 本版 release notes 文件必须存在且非空(否则发布页只剩通用模板 —— v2.1.4 复盘 #1)
echo "[2] 本版发布说明"
[ -s "${INSTALLER_ROOT}/config/release_notes/${VERSION}.md" ] && ok "config/release_notes/${VERSION}.md 存在" || bad "缺 config/release_notes/${VERSION}.md —— 发布页会只显示通用说明"

# 3. UPGRADE_LOG 有本版条目
echo "[3] UPGRADE_LOG 条目"
grep -q "${VERSION}" "${REPO_ROOT}/UPGRADE_LOG.md" && ok "UPGRADE_LOG 提及 ${VERSION}" || bad "UPGRADE_LOG.md 没有 ${VERSION} 条目"

# 3b. Windows 同步台账必须有本版条目(每个 Mac 修复都要让 Windows 端能读到 —— 流程硬性要求)
echo "[3b] Windows 同步条目"
grep -q "${VERSION}" "${REPO_ROOT}/docs/windows-sync-handoff.md" && ok "windows-sync-handoff 提及 ${VERSION}" || bad "docs/windows-sync-handoff.md 没有 ${VERSION} 条目 —— Windows 端无法同步本次修复(每个修复须随附技术文档+同步条目)"

# 4. settings.local.json 绝不可被 git 跟踪(里面有 token / 机器路径 —— 本次复盘的泄露风险)
echo "[4] 机密文件未入库"
if git -C "${REPO_ROOT}" ls-files --error-unmatch .claude/settings.local.json >/dev/null 2>&1; then bad ".claude/settings.local.json 被 git 跟踪了(含 token,有泄露风险!)"; else ok ".claude/settings.local.json 未被跟踪"; fi
# harness JSON 必须可解析(本次有人加 token 时漏逗号弄坏过)
for f in settings.json settings.local.json launch.json; do
  p="${REPO_ROOT}/.claude/${f}"
  [ -f "${p}" ] || continue
  python3 -m json.tool "${p}" >/dev/null 2>&1 && ok ".claude/${f} 可解析" || bad ".claude/${f} JSON 解析失败"
done

# 5. 编译产物新鲜度(后端 jar / 前端 dist-file 不能比源码旧 —— 复盘 #2;打包时也会再拦一次)
echo "[5] 编译产物新鲜度"
JAR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
DIST="${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file/index.html"
if [ -f "${JAR}" ]; then
  if [ -n "$(find "${REPO_ROOT}"/Horosa-Web/astrostudysrv/*/src/main -type f -newer "${JAR}" -print -quit 2>/dev/null || true)" ]; then bad "astrostudyboot.jar 比后端源码旧 —— 需 mvn clean package 重建"; else ok "astrostudyboot.jar 比源码新"; fi
else warn "astrostudyboot.jar 不存在(发布会回退到 runtime bundle 旧 jar —— 后端有改动务必先重建)"; fi
if [ -f "${DIST}" ]; then
  if [ -n "$(find "${REPO_ROOT}/Horosa-Web/astrostudyui/src" -type f -newer "${DIST}" -print -quit 2>/dev/null || true)" ]; then bad "dist-file 比前端源码旧 —— 需 npm run build && build:file"; else ok "dist-file 比源码新"; fi
else bad "dist-file 不存在 —— 需 npm run build:file"; fi

# 6. CI 必须对当前 HEAD 通过(功能回归靠 CI 兜 —— 复盘 #3)。需要 gh。
echo "[6] CI 状态(当前 HEAD)"
if command -v gh >/dev/null 2>&1; then
  HEAD_SHA="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
  CI_JSON="$(gh run list --repo Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS --branch main --limit 10 --json headSha,status,conclusion,workflowName 2>/dev/null || echo '[]')"
  CONCL="$(printf '%s' "${CI_JSON}" | python3 -c "import sys,json;sha='${HEAD_SHA}';rs=[r for r in json.load(sys.stdin) if r.get('headSha')==sha];print((rs[0].get('conclusion') or rs[0].get('status')) if rs else 'none')" 2>/dev/null || echo 'err')"
  case "${CONCL}" in
    success) ok "CI 对 HEAD(${HEAD_SHA:0:7})成功";;
    none)    warn "CI 还没有 HEAD(${HEAD_SHA:0:7})的运行记录 —— 先 push 并等 CI 跑完";;
    *)       bad "CI 对 HEAD(${HEAD_SHA:0:7})状态=${CONCL}(需 success 才发)";;
  esac
else warn "未装 gh,跳过 CI 检查 —— 请手动确认 CI 绿"; fi

echo "== 结果 =="
if [ "${fail}" -ne 0 ]; then echo "pre-flight 有 ❌,先修再发。" >&2; exit 1; fi
echo "pre-flight 全部通过 ✅(注意:功能层 e2e 仍需另测,如 AI 用真 key、八字切换显示)。"
