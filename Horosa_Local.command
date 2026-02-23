#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="${ROOT}/Horosa-Web"
START_SH="${PROJECT_DIR}/start_horosa_local.sh"
STOP_SH="${PROJECT_DIR}/stop_horosa_local.sh"
BOOTSTRAP_SH="${ROOT}/scripts/mac/bootstrap_and_run.sh"
PY_PID_FILE="${PROJECT_DIR}/.horosa_py.pid"
JAVA_PID_FILE="${PROJECT_DIR}/.horosa_java.pid"
UI_DIR="${PROJECT_DIR}/astrostudyui"

BUNDLED_RUNTIME_DIR="${ROOT}/runtime/mac"
BUNDLED_JAVA_HOME="${BUNDLED_RUNTIME_DIR}/java"
BUNDLED_PYTHON_BIN="${BUNDLED_RUNTIME_DIR}/python/bin/python3"
BOOTSTRAP_VENV_PY="${ROOT}/.runtime/mac/venv/bin/python3"
BUNDLE_DIR="${BUNDLED_RUNTIME_DIR}/bundle"
BUNDLE_JAR="${BUNDLE_DIR}/astrostudyboot.jar"
TARGET_JAR="${PROJECT_DIR}/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
BUNDLE_DIST_FILE="${BUNDLE_DIR}/dist-file"
BUNDLE_DIST="${BUNDLE_DIR}/dist"
BUNDLED_JAVA_CANDIDATES=(
  "${BUNDLED_JAVA_HOME}"
  "${ROOT}/.runtime/mac/java"
)

DIST_DIR="${PROJECT_DIR}/astrostudyui/dist-file"
DIAG_FILE="${HOROSA_DIAG_FILE:-${PROJECT_DIR}/.horosa-run-issues.log}"
DIAG_DIR="${HOROSA_DIAG_DIR:-${ROOT}/diagnostics}"
if [ -z "${HOROSA_DIAG_FILE:-}" ]; then
  DIAG_FILE="${DIAG_DIR}/horosa-run-issues.log"
fi
RUN_OK=0

mkdir -p "${DIAG_DIR}"
mkdir -p "$(dirname "${DIAG_FILE}")"
touch "${DIAG_FILE}" >/dev/null 2>&1 || true

diag_log() {
  local msg="$1"
  printf '[%s] [Horosa_Local] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "${msg}" >>"${DIAG_FILE}" 2>/dev/null || true
}

diag_tail() {
  local file="$1"
  local lines="${2:-80}"
  if [ ! -f "${file}" ]; then
    return
  fi
  diag_log "tail ${lines} lines: ${file}"
  while IFS= read -r line; do
    printf '[%s] [tail] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "${line}" >>"${DIAG_FILE}" 2>/dev/null || true
  done < <(tail -n "${lines}" "${file}" 2>/dev/null || true)
}

latest_service_log_dir() {
  ls -td "${PROJECT_DIR}/.horosa-local-logs"/* 2>/dev/null | head -n 1 || true
}

dump_runtime_diagnostics() {
  local latest_dir
  latest_dir="$(latest_service_log_dir)"
  if [ -n "${latest_dir}" ]; then
    diag_log "latest service log dir: ${latest_dir}"
    diag_tail "${latest_dir}/astrostudyboot.log" 120
    diag_tail "${latest_dir}/astropy.log" 120
  fi
  diag_tail "/tmp/horosa_local_web.log" 120
}

resolve_dist_dir() {
  if [ -f "${PROJECT_DIR}/astrostudyui/dist-file/index.html" ]; then
    DIST_DIR="${PROJECT_DIR}/astrostudyui/dist-file"
    return
  fi
  DIST_DIR="${PROJECT_DIR}/astrostudyui/dist"
}

load_brew_env() {
  if [ -x /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [ -x /usr/local/bin/brew ]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
}

set_java_runtime() {
  local java_home="$1"
  local source_label="$2"
  if [ ! -x "${java_home}/bin/java" ]; then
    return 1
  fi
  if ! "${java_home}/bin/java" -version >/dev/null 2>&1; then
    return 1
  fi
  export JAVA_HOME="${java_home}"
  export PATH="${JAVA_HOME}/bin:${PATH}"
  export HOROSA_JAVA_BIN="${JAVA_HOME}/bin/java"
  echo "[预检] ${source_label}: ${JAVA_HOME}"
  return 0
}

detect_brew_java_home() {
  local formula=""
  local prefix=""
  local candidate=""

  load_brew_env
  if command -v brew >/dev/null 2>&1; then
    for formula in openjdk@17 openjdk; do
      if brew list --formula "${formula}" >/dev/null 2>&1; then
        prefix="$(brew --prefix "${formula}" 2>/dev/null || true)"
        candidate="${prefix}/libexec/openjdk.jdk/Contents/Home"
        if [ -x "${candidate}/bin/java" ]; then
          echo "${candidate}"
          return 0
        fi
      fi
    done
  fi

  for candidate in \
    /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home \
    /usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home \
    /opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home \
    /usr/local/opt/openjdk/libexec/openjdk.jdk/Contents/Home; do
    if [ -x "${candidate}/bin/java" ]; then
      echo "${candidate}"
      return 0
    fi
  done

  return 1
}

detect_system_java_home() {
  local java_home=""

  if [ -n "${JAVA_HOME:-}" ] && [ -x "${JAVA_HOME}/bin/java" ]; then
    echo "${JAVA_HOME}"
    return 0
  fi

  if command -v /usr/libexec/java_home >/dev/null 2>&1; then
    java_home="$(/usr/libexec/java_home -v 17 2>/dev/null || true)"
    if [ -n "${java_home}" ] && [ -x "${java_home}/bin/java" ]; then
      echo "${java_home}"
      return 0
    fi
  fi

  java_home="$(detect_brew_java_home 2>/dev/null || true)"
  if [ -n "${java_home}" ] && [ -x "${java_home}/bin/java" ]; then
    echo "${java_home}"
    return 0
  fi

  return 1
}

python_runtime_ready() {
  local py_bin="$1"
  if [ ! -x "${py_bin}" ]; then
    return 1
  fi
  "${py_bin}" - <<'PY' >/dev/null 2>&1
import importlib.util as iu
mods = ("cherrypy", "jsonpickle", "swisseph")
missing = [m for m in mods if iu.find_spec(m) is None]
raise SystemExit(1 if missing else 0)
PY
}

set_python_runtime() {
  local py_bin="$1"
  local source_label="$2"
  if ! python_runtime_ready "${py_bin}"; then
    return 1
  fi
  export HOROSA_PYTHON="${py_bin}"
  echo "[预检] ${source_label}: ${HOROSA_PYTHON}"
  return 0
}

detect_system_python_bin() {
  local candidate=""
  for candidate in python3 python; do
    if command -v "${candidate}" >/dev/null 2>&1; then
      command -v "${candidate}"
      return 0
    fi
  done
  return 1
}

bootstrap_missing_runtime() {
  local reason="${1:-运行时依赖不可用}"
  if [ "${HOROSA_BOOTSTRAP_ON_MISSING_RUNTIME:-0}" = "1" ]; then
    return 1
  fi
  if [ ! -x "${BOOTSTRAP_SH}" ]; then
    return 1
  fi

  echo "[预检] ${reason}，自动执行一键部署脚本补齐依赖..."
  export HOROSA_BOOTSTRAP_ON_MISSING_RUNTIME=1
  export HOROSA_SKIP_TOOLCHAIN_INSTALL="${HOROSA_SKIP_TOOLCHAIN_INSTALL:-0}"
  export HOROSA_SKIP_DB_SETUP="${HOROSA_SKIP_DB_SETUP:-1}"
  export HOROSA_SKIP_BUILD="${HOROSA_SKIP_BUILD:-1}"
  exec "${BOOTSTRAP_SH}"
}

use_bundled_runtime() {
  local java_home=""
  local candidate=""

  for candidate in "${BUNDLED_JAVA_CANDIDATES[@]}"; do
    if set_java_runtime "${candidate}" "使用项目内 Java runtime"; then
      break
    fi
  done

  if [ -z "${HOROSA_JAVA_BIN:-}" ]; then
    java_home="$(detect_system_java_home 2>/dev/null || true)"
    if [ -n "${java_home}" ]; then
      set_java_runtime "${java_home}" "使用系统 Java runtime"
    fi
  fi

  if [ -z "${HOROSA_JAVA_BIN:-}" ] && command -v java >/dev/null 2>&1; then
    local fallback_java
    fallback_java="$(command -v java)"
    if "${fallback_java}" -version >/dev/null 2>&1; then
      export HOROSA_JAVA_BIN="${fallback_java}"
      echo "[预检] 未检测到项目内 Java runtime，回退系统 Java: ${HOROSA_JAVA_BIN}"
    fi
  fi

  if [ -z "${HOROSA_JAVA_BIN:-}" ]; then
    echo "[预检] 未检测到项目内 Java runtime，且系统 Java 不可用。"
    bootstrap_missing_runtime "未检测到可用 Java runtime" || true
  fi

  if [ -z "${HOROSA_JAVA_BIN:-}" ]; then
    echo "[预检] Java 仍不可用，请先双击 Horosa_OneClick_Mac.command 完成初始化。"
    exit 1
  fi

  local requested_python="${HOROSA_PYTHON:-}"
  local system_python=""
  unset HOROSA_PYTHON || true

  if [ -n "${requested_python}" ]; then
    if ! set_python_runtime "${requested_python}" "使用外部指定 Python runtime"; then
      echo "[预检] 外部指定 Python runtime 缺少依赖，继续探测: ${requested_python}"
    fi
  fi

  if [ -z "${HOROSA_PYTHON:-}" ] && [ -x "${BOOTSTRAP_VENV_PY}" ]; then
    if ! set_python_runtime "${BOOTSTRAP_VENV_PY}" "使用一键脚本生成 Python runtime"; then
      echo "[预检] 一键脚本生成 Python runtime 缺少依赖，继续探测。"
    fi
  fi

  if [ -z "${HOROSA_PYTHON:-}" ] && [ -x "${BUNDLED_PYTHON_BIN}" ]; then
    if ! set_python_runtime "${BUNDLED_PYTHON_BIN}" "使用项目内 Python runtime"; then
      echo "[预检] 项目内 Python runtime 缺少依赖，继续探测系统 Python。"
    fi
  fi

  if [ -z "${HOROSA_PYTHON:-}" ]; then
    system_python="$(detect_system_python_bin 2>/dev/null || true)"
    if [ -n "${system_python}" ]; then
      if ! set_python_runtime "${system_python}" "使用系统 Python runtime"; then
        echo "[预检] 系统 Python 缺少依赖: ${system_python}"
      fi
    fi
  fi

  if [ -z "${HOROSA_PYTHON:-}" ]; then
    bootstrap_missing_runtime "未检测到可用 Python runtime 或缺少依赖(cherrypy/jsonpickle/swisseph)" || true
  fi

  if [ -z "${HOROSA_PYTHON:-}" ] || ! python_runtime_ready "${HOROSA_PYTHON}"; then
    echo "[预检] Python 仍不可用，请先双击 Horosa_OneClick_Mac.command 完成初始化。"
    exit 1
  fi
}

ensure_backend_artifact() {
  if [ -f "${TARGET_JAR}" ]; then
    return
  fi
  if [ -f "${BUNDLE_JAR}" ]; then
    echo "[预检] 目标 jar 缺失，使用仓库内预打包 jar 回填。"
    mkdir -p "$(dirname "${TARGET_JAR}")"
    cp -f "${BUNDLE_JAR}" "${TARGET_JAR}"
    return
  fi

  if [ "${HOROSA_BOOTSTRAP_ON_MISSING_BACKEND:-0}" = "1" ]; then
    return
  fi

  if [ -x "${BOOTSTRAP_SH}" ]; then
    echo "[预检] 后端 jar 缺失，自动执行一键部署脚本构建后端..."
    export HOROSA_BOOTSTRAP_ON_MISSING_BACKEND=1
    HOROSA_SKIP_DB_SETUP="${HOROSA_SKIP_DB_SETUP:-1}" \
      HOROSA_SKIP_LAUNCH=1 \
      HOROSA_SKIP_BUILD=0 \
      HOROSA_SKIP_TOOLCHAIN_INSTALL="${HOROSA_SKIP_TOOLCHAIN_INSTALL:-0}" \
      "${BOOTSTRAP_SH}" || true
  fi

  if [ -f "${TARGET_JAR}" ]; then
    return
  fi
  if [ -f "${BUNDLE_JAR}" ]; then
    echo "[预检] 使用一键部署产出的 bundle jar 回填后端。"
    mkdir -p "$(dirname "${TARGET_JAR}")"
    cp -f "${BUNDLE_JAR}" "${TARGET_JAR}"
    return
  fi

  echo "[预检] 后端 jar 仍不可用，请先执行 Horosa_OneClick_Mac.command。"
  exit 1
}

ensure_frontend_artifact() {
  resolve_dist_dir
  if [ -f "${DIST_DIR}/index.html" ]; then
    return
  fi

  if [ -f "${BUNDLE_DIST_FILE}/index.html" ]; then
    echo "[预检] 前端 dist-file 缺失，使用仓库内预打包文件回填。"
    mkdir -p "${PROJECT_DIR}/astrostudyui/dist-file"
    rsync -a --delete "${BUNDLE_DIST_FILE}/" "${PROJECT_DIR}/astrostudyui/dist-file/"
  elif [ -f "${BUNDLE_DIST}/index.html" ]; then
    echo "[预检] 前端 dist 缺失，使用仓库内预打包文件回填。"
    mkdir -p "${PROJECT_DIR}/astrostudyui/dist"
    rsync -a --delete "${BUNDLE_DIST}/" "${PROJECT_DIR}/astrostudyui/dist/"
  fi
  resolve_dist_dir
}

repair_frontend_entry_assets() {
  local index_file="$1/index.html"
  local static_dir="$1/static"
  if [ ! -f "${index_file}" ]; then
    return
  fi
  if ! grep -qE '"/static/umi\.[^"]+\.(js|css)"' "${index_file}"; then
    return
  fi
  if ls "${static_dir}"/umi.*.js >/dev/null 2>&1 && ls "${static_dir}"/umi.*.css >/dev/null 2>&1; then
    return
  fi
  if ! ls "$1"/umi.*.js >/dev/null 2>&1 && ! ls "$1"/umi.*.css >/dev/null 2>&1; then
    return
  fi
  mkdir -p "${static_dir}"
  cp -f "$1"/umi.*.js "${static_dir}/" 2>/dev/null || true
  cp -f "$1"/umi.*.css "${static_dir}/" 2>/dev/null || true
}

if [ ! -x "${START_SH}" ] || [ ! -x "${STOP_SH}" ]; then
  echo "缺少可执行脚本：${START_SH} 或 ${STOP_SH}"
  read -r -p "按回车退出..." _
  exit 1
fi

ensure_frontend_build() {
  resolve_dist_dir
  local dist_index="${DIST_DIR}/index.html"
  local force_build="${HOROSA_FORCE_UI_BUILD:-0}"

  if [ "${force_build}" != "1" ] && [ -f "${dist_index}" ]; then
    echo "[0/4] 使用已打包前端文件（如需重建请设置 HOROSA_FORCE_UI_BUILD=1）。"
    return
  fi

  local should_build=0

  if [ ! -f "${dist_index}" ]; then
    should_build=1
  else
    if [ -n "$(find "${UI_DIR}/src" -type f -newer "${dist_index}" -print -quit 2>/dev/null)" ]; then
      should_build=1
    fi
    if [ -d "${UI_DIR}/public" ] && [ -n "$(find "${UI_DIR}/public" -type f -newer "${dist_index}" -print -quit 2>/dev/null)" ]; then
      should_build=1
    fi
    if [ -f "${UI_DIR}/package.json" ] && [ "${UI_DIR}/package.json" -nt "${dist_index}" ]; then
      should_build=1
    fi
    if [ -f "${UI_DIR}/.umirc.ts" ] && [ "${UI_DIR}/.umirc.ts" -nt "${dist_index}" ]; then
      should_build=1
    fi
    if [ -f "${UI_DIR}/.umirc.js" ] && [ "${UI_DIR}/.umirc.js" -nt "${dist_index}" ]; then
      should_build=1
    fi
  fi

  if [ "${should_build}" = "1" ]; then
    if command -v npm >/dev/null 2>&1; then
      echo "[0/4] 检测到前端有新改动，正在自动构建..."
      (
        cd "${UI_DIR}"
        if [ ! -d "node_modules" ]; then
          echo "[0/4] 未检测到 node_modules，先执行 npm install..."
          npm install --legacy-peer-deps
        fi
        npm run build:file
      )
      resolve_dist_dir
      dist_index="${DIST_DIR}/index.html"
      if [ ! -f "${dist_index}" ]; then
        echo "前端构建完成但未找到 ${dist_index}"
        exit 1
      fi
    elif [ -f "${dist_index}" ]; then
      echo "[0/4] 检测到前端源码有更新，但当前无 npm；使用现有静态文件继续启动。"
    else
      echo "前端静态文件缺失，且当前环境无 npm，无法自动构建。"
      echo "请先点击 Horosa_OneClick_Mac.command 自动安装并构建。"
      exit 1
    fi
  else
    echo "[0/4] 前端构建已是最新，跳过自动构建。"
  fi
}

WEB_PORT="${HOROSA_WEB_PORT:-8000}"
WEB_PID=""
BROWSER_PID=""
BACKEND_STARTED=0
BROWSER_PROFILE_DIR="${PROJECT_DIR}/.horosa-browser-profile"
NO_BROWSER="${HOROSA_NO_BROWSER:-0}"
mkdir -p "${BROWSER_PROFILE_DIR}"

port_listening() {
  local port="$1"
  lsof -tiTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1
}

pick_browser_bin() {
  local candidates=(
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    "/Applications/Chromium.app/Contents/MacOS/Chromium"
  )
  local bin
  for bin in "${candidates[@]}"; do
    if [ -x "${bin}" ]; then
      echo "${bin}"
      return 0
    fi
  done
  return 1
}

cleanup() {
  local code=$?
  set +e

  if [ "${RUN_OK}" != "1" ]; then
    diag_log "run failed or interrupted, exit_code=${code}"
    dump_runtime_diagnostics
    diag_log "===== run end (failed) ====="
    echo "[诊断] 已记录到：${DIAG_FILE}"
  fi

  if [ -n "${WEB_PID}" ] && kill -0 "${WEB_PID}" >/dev/null 2>&1; then
    kill "${WEB_PID}" >/dev/null 2>&1 || true
    sleep 1
    kill -9 "${WEB_PID}" >/dev/null 2>&1 || true
  fi

  if [ "${BACKEND_STARTED}" = "1" ]; then
    "${STOP_SH}" >/dev/null 2>&1 || true
  fi

  return "${code}"
}
trap cleanup EXIT INT TERM

echo "[诊断] 运行问题会记录到：${DIAG_FILE}"
diag_log "===== run begin pid=$$ cwd=${ROOT} ====="
diag_log "env HOROSA_STARTUP_TIMEOUT=${HOROSA_STARTUP_TIMEOUT:-} HOROSA_FORCE_UI_BUILD=${HOROSA_FORCE_UI_BUILD:-0} HOROSA_SKIP_UI_BUILD=${HOROSA_SKIP_UI_BUILD:-1}"

if [ -f "${PY_PID_FILE}" ] || [ -f "${JAVA_PID_FILE}" ]; then
  echo "检测到旧服务记录，先执行一次停止..."
  "${STOP_SH}" >/dev/null 2>&1 || true
  sleep 1
fi

use_bundled_runtime
ensure_backend_artifact
ensure_frontend_artifact
repair_frontend_entry_assets "${DIST_DIR}"

resolve_dist_dir
if [ ! -d "${DIST_DIR}" ] || [ ! -f "${DIST_DIR}/index.html" ]; then
  echo "前端静态文件不存在：${DIST_DIR}/index.html"
  echo "请先点击 Horosa_OneClick_Mac.command 自动安装并构建。"
  read -r -p "按回车退出..." _
  exit 1
fi

ensure_frontend_build
resolve_dist_dir
repair_frontend_entry_assets "${DIST_DIR}"

echo "[1/4] 启动本地后端服务..."
export HOROSA_SKIP_UI_BUILD="${HOROSA_SKIP_UI_BUILD:-1}"
export HOROSA_DIAG_FILE="${DIAG_FILE}"
export HOROSA_DIAG_DIR="${DIAG_DIR}"
if ! "${START_SH}"; then
  diag_log "start_horosa_local failed"
  exit 1
fi
BACKEND_STARTED=1

echo "[2/4] 启动本地网页服务 (127.0.0.1:${WEB_PORT})..."
if port_listening "${WEB_PORT}"; then
  echo "端口 ${WEB_PORT} 已被占用，请先释放后重试。"
  exit 1
fi

WEB_PY="${HOROSA_PYTHON:-python3}"
"${WEB_PY}" -m http.server "${WEB_PORT}" --bind 127.0.0.1 --directory "${DIST_DIR}" >/tmp/horosa_local_web.log 2>&1 &
WEB_PID="$!"

for _ in $(seq 1 20); do
  if port_listening "${WEB_PORT}"; then
    break
  fi
  sleep 0.2
done

if ! port_listening "${WEB_PORT}"; then
  echo "本地网页服务启动失败，日志：/tmp/horosa_local_web.log"
  exit 1
fi

URL="http://127.0.0.1:${WEB_PORT}/index.html?v=$(date +%s)"

echo "[3/4] 打开网页..."
BROWSER_BIN=""
if [ "${NO_BROWSER}" = "1" ]; then
  echo "HOROSA_NO_BROWSER=1，跳过打开浏览器（仅用于命令行自检）。"
  echo "访问地址：${URL}"
  echo "按回车后停止本地服务。"
  read -r _
elif command -v open >/dev/null 2>&1 && open -a "Safari" "${URL}" >/dev/null 2>&1; then
  echo "[4/4] 已使用 Safari 打开：${URL}"
  echo "关闭网页后按回车，将自动停止本地服务。"
  read -r _
elif BROWSER_BIN="$(pick_browser_bin)"; then
  "${BROWSER_BIN}" \
    --user-data-dir="${BROWSER_PROFILE_DIR}" \
    --app="${URL}" \
    --no-first-run \
    --no-default-browser-check \
    --disable-features=DialMediaRouteProvider >/dev/null 2>&1 &
  BROWSER_PID="$!"

  echo "[4/4] 已启动：${URL}"
  echo "关闭这个独立窗口后，将自动停止本地服务。"
  wait "${BROWSER_PID}" || true
else
  echo "未检测到 Chrome/Edge/Brave/Chromium，改用系统默认浏览器打开。"
  open "${URL}" || true
  echo "关闭网页后按回车，将自动停止本地服务。"
  read -r _
fi

echo "网页已关闭，正在停止本地服务..."
RUN_OK=1
diag_log "run success, web_url=${URL}"
diag_log "===== run end (success) ====="
