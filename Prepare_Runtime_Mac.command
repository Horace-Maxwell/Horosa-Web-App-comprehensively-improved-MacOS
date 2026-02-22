#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="${ROOT}/Horosa-Web"
RUNTIME_DIR="${ROOT}/runtime/mac"
JAVA_DST="${RUNTIME_DIR}/java"
PY_DST="${RUNTIME_DIR}/python"
BUNDLE_DIR="${RUNTIME_DIR}/bundle"
BOOTSTRAP_SH="${ROOT}/scripts/mac/bootstrap_and_run.sh"
REQ_FILE="${ROOT}/scripts/requirements/mac-python.txt"

UI_DIR="${PROJECT_DIR}/astrostudyui"
IMAGE_DIR="${PROJECT_DIR}/astrostudysrv/image"
BOOT_DIR="${PROJECT_DIR}/astrostudysrv/astrostudyboot"
JAR_PATH="${BOOT_DIR}/target/astrostudyboot.jar"

mkdir -p "${RUNTIME_DIR}" "${BUNDLE_DIR}"

echo "== Horosa Mac 运行时准备 =="

detect_java_src() {
  if [ -n "${HOROSA_JAVA_HOME:-}" ] && [ -x "${HOROSA_JAVA_HOME}/bin/java" ]; then
    echo "${HOROSA_JAVA_HOME}"
    return 0
  fi
  if command -v /usr/libexec/java_home >/dev/null 2>&1; then
    local jh
    jh="$(/usr/libexec/java_home -v 17 2>/dev/null || true)"
    if [ -n "${jh}" ] && [ -x "${jh}/bin/java" ]; then
      echo "${jh}"
      return 0
    fi
    jh="$(/usr/libexec/java_home -v 1.8 2>/dev/null || true)"
    if [ -n "${jh}" ] && [ -x "${jh}/bin/java" ]; then
      echo "${jh}"
      return 0
    fi
  fi
  for cand in \
    "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home" \
    "/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home" \
    "/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home" \
    "/usr/local/opt/openjdk/libexec/openjdk.jdk/Contents/Home" \
    "/Library/Java/JavaVirtualMachines/jdk-1.8.jdk/Contents/Home" \
    "/Library/Java/JavaVirtualMachines/zulu-17.jdk/Contents/Home" \
    "/Library/Java/JavaVirtualMachines/jdk-22.jdk/Contents/Home"; do
    if [ -x "${cand}/bin/java" ]; then
      echo "${cand}"
      return 0
    fi
  done
  return 1
}

prepare_java_runtime() {
  if [ -x "${JAVA_DST}/bin/java" ] && "${JAVA_DST}/bin/java" -version >/dev/null 2>&1; then
    echo "[Java] 已存在：${JAVA_DST}"
    return 0
  fi

  local java_src=""
  if java_src="$(detect_java_src 2>/dev/null)"; then
    echo "[Java] 复制 runtime: ${java_src} -> ${JAVA_DST}"
    rm -rf "${JAVA_DST}"
    rsync -a "${java_src}/" "${JAVA_DST}/"
    return 0
  fi

  if [ -x "${BOOTSTRAP_SH}" ]; then
    echo "[Java] 未找到可复制 Java，尝试自动执行一键部署补齐..."
    HOROSA_SKIP_TOOLCHAIN_INSTALL=0 HOROSA_SKIP_BUILD=1 HOROSA_SKIP_DB_SETUP=1 HOROSA_SKIP_LAUNCH=1 "${BOOTSTRAP_SH}" || true
    if java_src="$(detect_java_src 2>/dev/null)"; then
      echo "[Java] 补齐后复制 runtime: ${java_src} -> ${JAVA_DST}"
      rm -rf "${JAVA_DST}"
      rsync -a "${java_src}/" "${JAVA_DST}/"
      return 0
    fi
  fi

  echo "[Java] 未找到可复制的 Java 运行时。"
  echo "[Java] 请先安装 JDK（建议 17）或设置 HOROSA_JAVA_HOME 后重试。"
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

ensure_python_runtime_deps() {
  if python_runtime_ready "${PY_DST}/bin/python3"; then
    return 0
  fi

  if [ -f "${REQ_FILE}" ]; then
    echo "[Python] 缺少依赖，尝试安装: $(basename "${REQ_FILE}")"
    "${PY_DST}/bin/python3" -m ensurepip --upgrade >/dev/null 2>&1 || true
    "${PY_DST}/bin/python3" -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1 || true
    "${PY_DST}/bin/python3" -m pip install -r "${REQ_FILE}" || true
  fi

  python_runtime_ready "${PY_DST}/bin/python3"
}

prepare_python_runtime() {
  if [ -x "${PY_DST}/bin/python3" ]; then
    if ensure_python_runtime_deps; then
      echo "[Python] 已存在：${PY_DST}"
      return 0
    fi
    echo "[Python] 已存在但缺少运行依赖，将重新复制。"
  fi

  local py_exe="${HOROSA_PYTHON:-python3}"
  if ! command -v "${py_exe}" >/dev/null 2>&1; then
    echo "[Python] 未找到解释器：${py_exe}"
    return 1
  fi

  local py_prefix
  py_prefix="$(${py_exe} - <<'PY'
import sys
print(sys.prefix)
PY
)"

  local py_minor
  py_minor="$(${py_exe} - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)"

  if [ ! -d "${py_prefix}" ]; then
    echo "[Python] Python prefix 不存在: ${py_prefix}"
    return 1
  fi

  echo "[Python] 复制 runtime(可能较大): ${py_prefix} -> ${PY_DST}"
  rm -rf "${PY_DST}"
  rsync -a --delete \
    --exclude 'pkgs' \
    --exclude 'conda-bld' \
    --exclude '.conda' \
    --exclude 'share/jupyter' \
    --exclude '_CodeSignature' \
    --exclude '*/_CodeSignature' \
    "${py_prefix}/" "${PY_DST}/"

  local extra_site="$HOME/Library/Python/${py_minor}/lib/python/site-packages"
  if [ -d "${extra_site}" ]; then
    mkdir -p "${PY_DST}/lib/python${py_minor}/site-packages"
    echo "[Python] 复制额外 site-packages: ${extra_site}"
    rsync -a "${extra_site}/" "${PY_DST}/lib/python${py_minor}/site-packages/"
  fi

  if ! ensure_python_runtime_deps; then
    echo "[Python] 警告：runtime 中未检测到 cherrypy。"
    echo "[Python] 启动时若报错，请在可联网环境执行：${PY_DST}/bin/python3 -m pip install -r ${REQ_FILE}"
  fi

  return 0
}

prepare_frontend_bundle() {
  if [ ! -d "${UI_DIR}" ]; then
    echo "[前端] 目录不存在：${UI_DIR}"
    return 1
  fi

  if command -v npm >/dev/null 2>&1; then
    echo "[前端] 检查依赖并构建 dist-file..."
    (
      cd "${UI_DIR}"
      if [ ! -d "node_modules" ]; then
        npm install --legacy-peer-deps
      fi
      npm run build:file
    )
  else
    echo "[前端] 未检测到 npm，跳过构建，尝试复用现有 dist。"
  fi

  if [ -f "${UI_DIR}/dist-file/index.html" ]; then
    mkdir -p "${BUNDLE_DIR}/dist-file"
    rsync -a --delete "${UI_DIR}/dist-file/" "${BUNDLE_DIR}/dist-file/"
    echo "[前端] 已打包 dist-file 到 ${BUNDLE_DIR}/dist-file"
    return 0
  fi

  if [ -f "${UI_DIR}/dist/index.html" ]; then
    mkdir -p "${BUNDLE_DIR}/dist"
    rsync -a --delete "${UI_DIR}/dist/" "${BUNDLE_DIR}/dist/"
    echo "[前端] 已打包 dist 到 ${BUNDLE_DIR}/dist"
    return 0
  fi

  echo "[前端] 未找到可用 dist 输出。"
  return 1
}

prepare_backend_bundle() {
  if [ -d "${IMAGE_DIR}" ] && [ -d "${BOOT_DIR}" ] && command -v mvn >/dev/null 2>&1; then
    echo "[后端] 使用 Maven 构建 jar..."
    (
      cd "${IMAGE_DIR}"
      mvn -DskipTests install
      cd "${BOOT_DIR}"
      mvn -DskipTests clean install
    )
  else
    echo "[后端] 未检测到 mvn 或目录不完整，跳过构建，尝试复用现有 jar。"
  fi

  if [ -f "${JAR_PATH}" ]; then
    cp -f "${JAR_PATH}" "${BUNDLE_DIR}/astrostudyboot.jar"
    echo "[后端] 已打包 jar 到 ${BUNDLE_DIR}/astrostudyboot.jar"
    return 0
  fi

  echo "[后端] 未找到可用 jar：${JAR_PATH}"
  return 1
}

set +e
prepare_java_runtime
JAVA_RC=$?
prepare_python_runtime
PY_RC=$?
prepare_frontend_bundle
FE_RC=$?
prepare_backend_bundle
BE_RC=$?
set -e

echo ""
echo "== 准备结果 =="
[ ${JAVA_RC} -eq 0 ] && echo "Java runtime: OK" || echo "Java runtime: FAILED"
[ ${PY_RC} -eq 0 ] && echo "Python runtime: OK" || echo "Python runtime: FAILED"
[ ${FE_RC} -eq 0 ] && echo "Frontend bundle: OK" || echo "Frontend bundle: FAILED"
[ ${BE_RC} -eq 0 ] && echo "Backend bundle: OK" || echo "Backend bundle: FAILED"

echo ""
echo "runtime 目录体积："
du -sh "${ROOT}/runtime" || true

echo ""
if [ ${JAVA_RC} -eq 0 ] && [ ${PY_RC} -eq 0 ]; then
  echo "下一步：双击 Horosa_Local.command 直接启动。"
else
  echo "下一步：双击 Horosa_OneClick_Mac.command 自动补齐缺失依赖后再启动。"
fi
read -r -p "按回车退出..." _
