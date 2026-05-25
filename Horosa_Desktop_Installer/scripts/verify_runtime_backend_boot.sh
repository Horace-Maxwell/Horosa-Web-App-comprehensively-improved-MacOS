#!/usr/bin/env bash
#
# verify_runtime_backend_boot.sh — 发布前兜底自检（可选，不进入正常构建流程）
#
# 背景：现有的 package_runtime_payload.sh 与离线 postinstall 只跑 `java -version`
# 和 `python -c "import swisseph"`，从不真正启动 Spring Boot + Python 图表服务，
# 因此「启动后才暴露的问题」（如某个 JNI 原生库架构不符、依赖缺失、端口/配置回归）
# 在发布前不会被发现。本脚本用桌面壳完全一致的方式，把打好的运行时真正启动一次，
# 等待后端健康检查通过，再（可选）打一遍 kentang 引擎端点，最后干净退出。
#
# 这是一个独立、按需运行的脚本：
#   - 不会被 build_desktop_release.sh / package_runtime_payload.sh 自动调用；
#   - 默认对「运行时归档(.tar.gz)」解压到临时目录后启动，绝不触碰已安装的
#     /Users/Shared/Horosa 或正在运行的 app；
#   - 退出码：0 全部通过 / 1 后端未能启动并健康 / 2 端点冒烟失败 / 3 输入/环境错误。
#
# 用法：
#   scripts/verify_runtime_backend_boot.sh [运行时归档.tar.gz | 运行时目录]
#   # 不带参数时自动按顺序探测：dist/<runtimeAsset>.tar.gz → build/runtime/runtime-payload
#   选项：
#     --skip-endpoints   只验证后端启动+健康，跳过 kentang 引擎端点冒烟
#     --timeout <秒>     启动超时（默认 240；慢机首启可调大）
#     --keep-logs        保留临时日志目录（默认退出时清理）
#
# 建议接法（均为可选，不影响默认发布流程）：
#   - 发布前手动跑一次；或
#   - 在 verify_public_distribution_readiness.sh 末尾按需调用。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALLER_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
KENTANG_VERIFIER="${SCRIPT_DIR}/verify_kentang_runtime_endpoints.py"

SKIP_ENDPOINTS=0
STARTUP_TIMEOUT="${HOROSA_STARTUP_TIMEOUT:-240}"
KEEP_LOGS=0
INPUT_PATH="${HOROSA_SELFCHECK_RUNTIME:-}"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skip-endpoints) SKIP_ENDPOINTS=1; shift ;;
    --keep-logs) KEEP_LOGS=1; shift ;;
    --timeout) STARTUP_TIMEOUT="${2:-240}"; shift 2 ;;
    --timeout=*) STARTUP_TIMEOUT="${1#*=}"; shift ;;
    -h|--help) sed -n '2,40p' "$0"; exit 0 ;;
    *) INPUT_PATH="$1"; shift ;;
  esac
done

WORK_TMP=""
RUNTIME_DIR=""
WEB_ROOT=""
STARTED=0
CHART_PORT=""
BACKEND_PORT=""

log()  { printf '[selfcheck] %s\n' "$1"; }
fail() { printf '[selfcheck] FAIL: %s\n' "$1" >&2; }

cleanup() {
  local code=$?
  if [ "${STARTED}" = "1" ] && [ -n "${WEB_ROOT}" ] && [ -f "${WEB_ROOT}/stop_horosa_local.sh" ]; then
    HOROSA_CHART_PORT="${CHART_PORT}" HOROSA_SERVER_PORT="${BACKEND_PORT}" \
      /bin/bash "${WEB_ROOT}/stop_horosa_local.sh" >/dev/null 2>&1 || true
  fi
  if [ "${KEEP_LOGS}" != "1" ] && [ -n "${WORK_TMP}" ] && [ -d "${WORK_TMP}" ]; then
    rm -rf "${WORK_TMP}" >/dev/null 2>&1 || true
  elif [ -n "${WORK_TMP}" ]; then
    log "临时目录保留：${WORK_TMP}"
  fi
  exit "${code}"
}
trap cleanup EXIT INT TERM HUP

port_free() {
  ! lsof -tiTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

pick_free_port() {
  local p
  for p in $(seq "$1" "$2"); do
    if port_free "${p}"; then echo "${p}"; return 0; fi
  done
  return 1
}

# ---- 1. 解析运行时来源 -------------------------------------------------------
if [ -z "${INPUT_PATH}" ]; then
  ASSET="$(python3 - "${INSTALLER_ROOT}" <<'PY' 2>/dev/null || true
import json, os, sys, pathlib
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
  fail "找不到运行时归档或目录。传入一个 .tar.gz / 运行时目录，或先构建出 dist/<runtimeAsset>。"
  exit 3
fi

case "${INPUT_PATH}" in
  *.tar.gz|*.tgz)
    WORK_TMP="$(mktemp -d -t horosa-runtime-selfcheck)"
    log "解压运行时归档到临时目录：${INPUT_PATH}"
    if ! COPYFILE_DISABLE=1 COPY_EXTENDED_ATTRIBUTES_DISABLE=1 /usr/bin/tar -xzf "${INPUT_PATH}" -C "${WORK_TMP}"; then
      fail "运行时归档解压失败。"
      exit 3
    fi
    if [ -d "${WORK_TMP}/runtime-payload" ]; then
      RUNTIME_DIR="${WORK_TMP}/runtime-payload"
    else
      RUNTIME_DIR="${WORK_TMP}"
    fi
    ;;
  *)
    RUNTIME_DIR="$(cd "${INPUT_PATH}" && pwd)"
    ;;
esac

WEB_ROOT="${RUNTIME_DIR}/Horosa-Web"
PY_BIN="${RUNTIME_DIR}/runtime/mac/python/bin/python3"
JAVA_BIN="${RUNTIME_DIR}/runtime/mac/java/bin/java"
START_SH="${WEB_ROOT}/start_horosa_local.sh"

for required in "${START_SH}" "${PY_BIN}" "${JAVA_BIN}" "${WEB_ROOT}/astrostudyui/dist-file/index.html"; do
  if [ ! -e "${required}" ]; then
    fail "运行时不完整，缺少：${required}"
    exit 3
  fi
done
log "运行时目录：${RUNTIME_DIR}"
log "架构：本机 $(uname -m)；java=$(lipo -archs "${JAVA_BIN}" 2>/dev/null || echo '?')，python=$(lipo -archs "${PY_BIN}" 2>/dev/null || echo '?')"

# ---- 2. 选空闲端口并清理残留 -------------------------------------------------
CHART_PORT="$(pick_free_port 8890 8920)" || { fail "找不到空闲 chart 端口(8890-8920)。"; exit 3; }
BACKEND_PORT="$(pick_free_port 9970 9998)" || { fail "找不到空闲 backend 端口(9970-9998)。"; exit 3; }
log "使用端口：chart=${CHART_PORT} backend=${BACKEND_PORT} 启动超时=${STARTUP_TIMEOUT}s"

HOROSA_CHART_PORT="${CHART_PORT}" HOROSA_SERVER_PORT="${BACKEND_PORT}" \
  /bin/bash "${WEB_ROOT}/stop_horosa_local.sh" >/dev/null 2>&1 || true

# ---- 3. 用桌面壳一致的方式真正启动后端 --------------------------------------
# 关键：HOROSA_REQUIRE_EMBEDDED_RUNTIME=1 强制只用内置 python/java（与 app 一致），
# 不回退系统解释器——这正是要验证的对象。
LOG_ROOT="${WORK_TMP:-$(mktemp -d -t horosa-runtime-selfcheck)}/logs"
[ -n "${WORK_TMP}" ] || WORK_TMP="$(dirname "${LOG_ROOT}")"
mkdir -p "${LOG_ROOT}"

log "启动后端（Python 图表服务 + Java Spring Boot）…"
STARTED=1
start_rc=0
HOROSA_PYTHON="${PY_BIN}" \
HOROSA_JAVA_BIN="${JAVA_BIN}" \
HOROSA_REQUIRE_EMBEDDED_RUNTIME=1 \
HOROSA_SKIP_UI_BUILD=1 \
HOROSA_SKIP_RUNTIME_WARMUP=1 \
HOROSA_DESKTOP_MONGO_SKIP_PING=1 \
HOROSA_SERVER_PORT="${BACKEND_PORT}" \
HOROSA_CHART_PORT="${CHART_PORT}" \
HOROSA_LOG_ROOT="${LOG_ROOT}" \
HOROSA_DIAG_DIR="${LOG_ROOT}/diag" \
HOROSA_STARTUP_TIMEOUT="${STARTUP_TIMEOUT}" \
  /bin/bash "${START_SH}" || start_rc=$?

if [ "${start_rc}" -ne 0 ]; then
  fail "后端未能在 ${STARTUP_TIMEOUT}s 内启动并通过健康检查（这正是 'java -version' 抓不到的那类问题）。"
  exit 1
fi
log "OK：后端已启动，健康检查通过（chart / 与 backend /common/time 均可响应）。"

# ---- 4. 可选：kentang 引擎端点冒烟 ------------------------------------------
if [ "${SKIP_ENDPOINTS}" = "1" ]; then
  log "按要求跳过 kentang 引擎端点冒烟。"
elif [ -f "${KENTANG_VERIFIER}" ]; then
  log "运行 kentang 引擎端点冒烟…"
  if "${PY_BIN}" "${KENTANG_VERIFIER}" --root "http://127.0.0.1:${CHART_PORT}"; then
    log "OK：kentang 引擎端点全部通过。"
  else
    fail "kentang 引擎端点冒烟失败（详见上方逐项输出）。"
    exit 2
  fi
else
  log "未找到 ${KENTANG_VERIFIER}，跳过引擎端点冒烟。"
fi

log "全部通过：这份运行时可以在本机架构上真正启动并服务。"
exit 0
