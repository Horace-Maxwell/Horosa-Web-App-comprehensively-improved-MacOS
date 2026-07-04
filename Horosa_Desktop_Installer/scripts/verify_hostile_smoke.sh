#!/usr/bin/env bash
#
# verify_hostile_smoke.sh — 敌意环境冒烟门。
#
# 在「被污染的用户环境」下对打包产物起真实服务并跑全路由探针,证明发布物在
# 脏机器上仍全绿:
#   ① 恶意 PYTHONPATH:指向含 `streamlit.py`(import 即炸)与同名假模块的 scratch 目录
#      —— 验「内嵌解释器 PYTHONNOUSERSITE/路径隔离」与桩优先级不被外部同名模块劫持;
#   ② 代理黑洞:HTTP(S)_PROXY/ALL_PROXY 全指向不可达地址 —— 验「本地探测禁代理」
#      铁律(脚本 curl --noproxy / urllib ProxyHandler({}) / Rust spawn 前剥代理)真生效;
#   ③ 奇异 locale:LC_ALL=C —— 验中文路径/文案处理不炸;
#   ④ 只读 HOME:HOME 指向只读目录 —— 验运行时不依赖可写 HOME。
#
# 跑点:publish 前(verify_desktop_packaging 之后)手动/编排调用;逃生阀
# HOROSA_SKIP_HOSTILE=1。结果追加 SELFCHECK_LOG.md。
# 退出码:0 全过 / 非 0 = 底层 verify_runtime_backend_boot.sh 的对应码。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALLER_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SELFCHECK_LOG="${INSTALLER_ROOT}/SELFCHECK_LOG.md"
PROBE_SCRIPT="${SCRIPT_DIR}/verify_full_route_smoke.py"

log()  { printf '[hostile-smoke] %s\n' "$1"; }

if [ "${HOROSA_SKIP_HOSTILE:-0}" = "1" ]; then
  log "HOROSA_SKIP_HOSTILE=1:按要求跳过。"
  exit 0
fi

INPUT_PATH="${1:-}"

# ── 构造污染环境 ────────────────────────────────────────────────────────────────
HOSTILE_TMP="$(mktemp -d -t horosa-hostile)"
trap 'chmod -R u+w "${HOSTILE_TMP}" >/dev/null 2>&1 || true; rm -rf "${HOSTILE_TMP}" >/dev/null 2>&1 || true' EXIT

# 恶意 PYTHONPATH:同名毒模块(被 import 即炸;正确的隔离下它们根本不会被看见)
mkdir -p "${HOSTILE_TMP}/poison"
for mod in streamlit numpy cherrypy jsonpickle; do
  printf 'raise RuntimeError("hostile poison module %s was imported — runtime isolation broken")\n' "${mod}" \
    >"${HOSTILE_TMP}/poison/${mod}.py"
done

# 只读 HOME
mkdir -p "${HOSTILE_TMP}/rohome"
chmod 555 "${HOSTILE_TMP}/rohome"

log "污染环境:PYTHONPATH 毒模块×4 / 代理黑洞 / LC_ALL=C / 只读 HOME"

rc=0
env \
  PYTHONPATH="${HOSTILE_TMP}/poison" \
  HTTP_PROXY="http://10.255.255.1:9" \
  HTTPS_PROXY="http://10.255.255.1:9" \
  ALL_PROXY="http://10.255.255.1:9" \
  http_proxy="http://10.255.255.1:9" \
  https_proxy="http://10.255.255.1:9" \
  all_proxy="http://10.255.255.1:9" \
  LC_ALL=C \
  HOME="${HOSTILE_TMP}/rohome" \
  HOROSA_PROBE_SCRIPT="${PROBE_SCRIPT}" \
  /bin/bash "${SCRIPT_DIR}/verify_runtime_backend_boot.sh" ${INPUT_PATH:+"${INPUT_PATH}"} || rc=$?

GIT_HEAD="$(git -C "${INSTALLER_ROOT}" rev-parse --short HEAD 2>/dev/null || echo unknown)"
{
  printf '| %s | %s | %s | hostile-smoke | %s |\n' \
    "$(date '+%Y-%m-%d %H:%M')" "${GIT_HEAD}" \
    "$([ "${rc}" -eq 0 ] && echo PASS || echo FAIL)" \
    "poisoned-env"
} >>"${SELFCHECK_LOG}" 2>/dev/null || true

if [ "${rc}" -ne 0 ]; then
  log "FAIL(rc=${rc}):产物在敌意环境下未能全绿。"
  exit "${rc}"
fi
log "全部通过:产物在敌意环境下仍全绿。"
exit 0
