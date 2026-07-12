#!/usr/bin/env bash
# 打包产物前端冒烟(制度化,v3.3.3 脏构建事故后新增;PLAYBOOK #48/#49/#50)。
#
# 干什么:对「会进 .pkg 的同一份 dist-file」做自动化健康检查——不等装机、不靠肉眼。
#   ①指纹可追溯:build-info.json 在位 + dirty=false + commit=当前 HEAD(与 preflight[122] 同判据);
#   ②产物完整性:index.html/umi 主 bundle 在位且 index 引用的 hash 文件真实存在(打包取的就是这套字节);
#   ③静态服务可起:python3 -m http.server 试起并 curl index(200)——PLAYBOOK#48 最廉判别的自动化前半;
#   ④防回归锚:dist-file 内含 A 系列关键修复的编译产物特征(会话投毒守卫/浮层不透明变量)。
# 后半(浏览器实点推运盘/紫微/择日/悬浮窗)仍需人or preview 驱动——本脚本把「能自动的」全自动。
#
# 用法: bash scripts/verify_packaged_frontend.sh   (仓根或 Installer 目录均可)
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DIST="${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file"
fail=0
ok(){ printf '  \033[32m✅\033[0m %s\n' "$1"; }
bad(){ printf '  \033[31m❌\033[0m %s\n' "$1"; fail=1; }

echo "== 打包产物前端冒烟(${DIST}) =="

# ① 指纹可追溯
INFO="${DIST}/build-info.json"
if [ ! -f "${INFO}" ]; then
  bad "缺 build-info.json —— 旧产物或构建链未挂指纹,npm run build:file 重建"
else
  COMMIT=$(python3 -c "import json;print(json.load(open('${INFO}')).get('commit',''))" 2>/dev/null || echo "")
  DIRTY=$(python3 -c "import json;print(1 if json.load(open('${INFO}')).get('dirty') else 0)" 2>/dev/null || echo "1")
  HEAD=$(git -C "${REPO_ROOT}" rev-parse HEAD 2>/dev/null || echo "")
  [ "${DIRTY}" = "0" ] && ok "指纹 dirty=false(干净树构建)" || bad "指纹 dirty=true —— 脏树构建,先 commit 再重 build"
  if [ -n "${COMMIT}" ] && [ "${COMMIT}" = "${HEAD}" ]; then ok "指纹 commit=当前 HEAD(${COMMIT:0:12})"; else bad "指纹 commit(${COMMIT:0:12}) ≠ HEAD(${HEAD:0:12}) —— 重 build:file"; fi
fi

# ② 产物完整性:index 引用的 umi hash bundle 真实存在
if [ ! -f "${DIST}/index.html" ]; then
  bad "缺 index.html"
else
  UMI_JS=$(grep -oE 'umi\.[0-9a-f]+\.js' "${DIST}/index.html" | head -1)
  UMI_CSS=$(grep -oE 'umi\.[0-9a-f]+\.css' "${DIST}/index.html" | head -1)
  [ -n "${UMI_JS}" ] && [ -f "${DIST}/${UMI_JS}" ] && ok "index 引用的主 bundle 在位(${UMI_JS})" || bad "index 引用的 umi js 缺失(${UMI_JS:-未引用})"
  [ -z "${UMI_CSS}" ] || [ -f "${DIST}/${UMI_CSS}" ] && true || bad "index 引用的 umi css 缺失(${UMI_CSS})"
fi

# ③ 静态服务可起(端口探测取空闲;PLAYBOOK#48 最廉判别自动化)
PORT=8019
while lsof -nP -iTCP:${PORT} -sTCP:LISTEN >/dev/null 2>&1 && [ ${PORT} -lt 8040 ]; do PORT=$((PORT+1)); done
( cd "${DIST}" && python3 -m http.server ${PORT} >/dev/null 2>&1 & echo $! > /tmp/vpf_httpd.pid )
sleep 1.2
CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:${PORT}/index.html" 2>/dev/null || echo "000")
kill "$(cat /tmp/vpf_httpd.pid 2>/dev/null)" >/dev/null 2>&1; rm -f /tmp/vpf_httpd.pid
[ "${CODE}" = "200" ] && ok "静态服务冒烟 index 200(:${PORT});需人工深验时 launch.json horosa-prod(:8011) 连 dev 后端实点四症状" || bad "静态服务 index 非 200(${CODE})"

# ④ 防回归锚:关键修复的编译产物特征(minify 后字符串字面量仍在)
BUNDLE="${DIST}/${UMI_JS:-}"
# ⚠️ 判据两坑(2026-07-12 实踩):①必须扫「全目录」——技法组件全走 React.lazy,守卫串在
#    *.async.js 懒 chunk、layouts 样式在 layouts__index.*.chunk.css,只查 umi.js/umi.css 恒伪红;
#    ②中文在压缩产物里可能是 \uXXXX 转义形态,grep 原文找不到 → 用 python 双形态检测。
if [ -n "${UMI_JS:-}" ] && [ -f "${BUNDLE}" ]; then
  GUARD_HIT=$(python3 - "${DIST}" <<'PYEOF'
import glob, sys
probe = '后端服务尚未就绪'
esc = ''.join('\\u%04x' % ord(c) for c in probe)
for f in glob.glob(sys.argv[1] + '/*.js'):
    s = open(f, encoding='utf-8', errors='ignore').read()
    if probe in s or esc in s:
        print('hit'); break
PYEOF
)
  [ "${GUARD_HIT}" = "hit" ] && ok "会话投毒守卫已入产物(空载荷人话提示)" || bad "产物缺会话投毒守卫特征——dist-file 陈旧?重 build:file"
  grep -alq -- "--horosa-surface-solid" "${DIST}"/*.css "${DIST}"/*.js 2>/dev/null && ok "浮层不透明变量已入产物" || bad "产物缺浮层不透明特征"
  grep -alq "horosa-floating-surface" "${DIST}"/*.css 2>/dev/null && ok "floating-surface 基类已入产物" || bad "产物缺 floating-surface 基类"
fi

echo "== 结果 =="
if [ "${fail}" -ne 0 ]; then echo "❌ 打包产物冒烟未过,禁止交付/发布。" >&2; exit 1; fi
echo "✅ 打包产物冒烟通过(自动面);人工面按 PLAYBOOK#48:horosa-prod 起 :8011 实点 推运盘星体/紫微选项/择日控件/悬浮窗底。"
