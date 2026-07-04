#!/usr/bin/env bash
#
# verify_runtime_smoke.sh — 打包产物「全路由真实冒烟门」编排壳(发布强制门)。
#
# 流程:
#   ① 解析产物(参数 | dist/<runtimeAsset>.tar.gz | build/runtime/runtime-payload);
#   ② 闸前自证 slim:归档内 site-packages/streamlit/ 计数必为 0 —— 保证冒烟跑在
#      「兼容桩激活」的真实用户环境(有 streamlit 说明打包剥离段失效,直接 FAIL);
#   ③ 路由挂载↔探针清单漂移比对(check_route_probe_drift.py,秒级);
#   ④ 内嵌启动 + Python 面 31 挂载全路由真实请求断言(verify_full_route_smoke.py)
#      + Java 面 24 条(verifyHorosaRuntimeFull.js,构建机 node);
#   ⑤ 写 build/runtime-smoke/last_smoke.json{runtimeSha256,gitHead,pass,…}(哈希绑定,
#      preflight [79] 据此校验「跑过且对的就是这份归档」)+ SELFCHECK_LOG.md 落行。
#
# 跑点:build_desktop_release.sh 在归档就绪后、tauri build 之前强制调用(fail fast
# 于签名公证之前);逃生阀 HOROSA_SKIP_RUNTIME_SMOKE=1。
# 退出码:0 全过 / 1 启动失败 / 2 冒烟失败 / 3 输入错误 / 4 slim 自证失败 / 5 漂移。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALLER_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SMOKE_DIR="${INSTALLER_ROOT}/build/runtime-smoke"
STAMP="${SMOKE_DIR}/last_smoke.json"
SELFCHECK_LOG="${INSTALLER_ROOT}/SELFCHECK_LOG.md"
PROBE_SCRIPT="${SCRIPT_DIR}/verify_full_route_smoke.py"
DRIFT_SCRIPT="${SCRIPT_DIR}/check_route_probe_drift.py"

log()  { printf '[runtime-smoke] %s\n' "$1"; }
fail() { printf '[runtime-smoke] FAIL: %s\n' "$1" >&2; }

INPUT_PATH="${1:-}"
if [ -z "${INPUT_PATH}" ]; then
  ASSET="$(python3 - "${INSTALLER_ROOT}" <<'PY' 2>/dev/null || true
import json, sys, pathlib
root = pathlib.Path(sys.argv[1])
try:
    cfg = json.loads((root / 'config/release_config.json').read_text())
    print(cfg.get('runtimeAssetName', 'horosa-runtime-macos-arm64.tar.gz'))
except Exception:
    print('horosa-runtime-macos-arm64.tar.gz')
PY
)"
  if [ -f "${INSTALLER_ROOT}/dist/${ASSET}" ]; then
    INPUT_PATH="${INSTALLER_ROOT}/dist/${ASSET}"
  elif [ -d "${INSTALLER_ROOT}/build/runtime/runtime-payload" ]; then
    INPUT_PATH="${INSTALLER_ROOT}/build/runtime/runtime-payload"
  fi
fi
if [ -z "${INPUT_PATH}" ] || [ ! -e "${INPUT_PATH}" ]; then
  fail "找不到运行时归档/目录(先构建 dist/<runtimeAsset> 或传参)。"
  exit 3
fi
log "冒烟对象:${INPUT_PATH}"

# ── ② slim 自证 ────────────────────────────────────────────────────────────────
case "${INPUT_PATH}" in
  *.tar.gz|*.tgz)
    STREAMLIT_HITS="$(/usr/bin/tar -tzf "${INPUT_PATH}" 2>/dev/null | grep -c 'site-packages/streamlit/' || true)"
    ;;
  *)
    STREAMLIT_HITS="$(find "${INPUT_PATH}" -type d -path '*site-packages/streamlit' 2>/dev/null | wc -l | tr -d ' ')"
    ;;
esac
if [ "${STREAMLIT_HITS}" != "0" ]; then
  fail "产物内发现 streamlit(${STREAMLIT_HITS} 条)——打包剥离段失效,冒烟将不在「桩激活」的真实用户环境下进行。"
  exit 4
fi
log "slim 自证通过:产物无 streamlit(兼容桩将激活,与用户环境一致)。"

# ── ③ 漂移比对 ─────────────────────────────────────────────────────────────────
if ! python3 "${DRIFT_SCRIPT}"; then
  fail "路由挂载↔探针清单漂移(新增技法漏配探针 / 僵尸探针)。"
  exit 5
fi

# ── ④ 内嵌启动 + 全路由冒烟 ────────────────────────────────────────────────────
mkdir -p "${SMOKE_DIR}"
PROBE_OUT="${SMOKE_DIR}/python_routes.json"
JAVA_RUNNER="$(cd "${INSTALLER_ROOT}/.." && pwd)/Horosa-Web/astrostudyui/scripts/verifyHorosaRuntimeFull.js"
smoke_rc=0
HOROSA_PROBE_SCRIPT="${PROBE_SCRIPT}" \
HOROSA_PROBE_OUT="${PROBE_OUT}" \
HOROSA_JAVA_RUNNER="${JAVA_RUNNER}" \
  /bin/bash "${SCRIPT_DIR}/verify_runtime_backend_boot.sh" "${INPUT_PATH}" || smoke_rc=$?

# ── ⑤ 落 stamp + SELFCHECK_LOG ────────────────────────────────────────────────
RUNTIME_SHA=""
case "${INPUT_PATH}" in
  *.tar.gz|*.tgz) RUNTIME_SHA="$(shasum -a 256 "${INPUT_PATH}" | awk '{print $1}')" ;;
  *) RUNTIME_SHA="dir:$(cd "${INPUT_PATH}" && pwd)" ;;
esac
GIT_HEAD="$(git -C "${INSTALLER_ROOT}" rev-parse --short HEAD 2>/dev/null || echo unknown)"
PASS_TEXT="false"; [ "${smoke_rc}" -eq 0 ] && PASS_TEXT="true"
python3 - "$STAMP" "$RUNTIME_SHA" "$GIT_HEAD" "$PASS_TEXT" "$PROBE_OUT" <<'PY'
import json, sys, time, os
stamp, sha, head, passed, probe_out = sys.argv[1:6]
data = {
    "runtimeSha256": sha,
    "gitHead": head,
    "pass": passed == "true",
    "at": time.strftime("%Y-%m-%d %H:%M:%S"),
}
try:
    if os.path.isfile(probe_out):
        data["python"] = json.load(open(probe_out, encoding="utf-8"))
except Exception:
    pass
json.dump(data, open(stamp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
PY
{
  printf '| %s | %s | %s | runtime-smoke | %s |\n' \
    "$(date '+%Y-%m-%d %H:%M')" "${GIT_HEAD}" \
    "$([ "${smoke_rc}" -eq 0 ] && echo PASS || echo FAIL)" \
    "${RUNTIME_SHA:0:16}…"
} >>"${SELFCHECK_LOG}" 2>/dev/null || true

if [ "${smoke_rc}" -ne 0 ]; then
  fail "冒烟未通过(rc=${smoke_rc}),stamp 已记 FAIL。"
  exit "${smoke_rc}"
fi
log "全部通过:stamp=${STAMP}(sha 绑定 ${RUNTIME_SHA:0:16}…)。"
exit 0
