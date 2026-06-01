#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
LOCAL_CMD="${ROOT}/tools/mac/Horosa_Local.command"
BOOTSTRAP_SH="${ROOT}/scripts/mac/bootstrap_and_run.sh"

has_frontend_artifact() {
  local candidates=(
    "${ROOT}/Horosa-Web/astrostudyui/dist-file/index.html"
    "${ROOT}/Horosa-Web/astrostudyui/dist/index.html"
    "${ROOT}/runtime/mac/bundle/dist-file/index.html"
    "${ROOT}/runtime/mac/bundle/dist/index.html"
  )
  local candidate=""
  for candidate in "${candidates[@]}"; do
    if [ -f "${candidate}" ]; then
      return 0
    fi
  done
  return 1
}

has_backend_artifact() {
  [ -f "${ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar" ] || \
    [ -f "${ROOT}/runtime/mac/bundle/astrostudyboot.jar" ]
}

frontend_needs_rebuild() {
  local index="${ROOT}/Horosa-Web/astrostudyui/dist-file/index.html"
  local ui_dir="${ROOT}/Horosa-Web/astrostudyui"
  if [ ! -f "${index}" ]; then
    return 0
  fi
  if [ -n "$(find "${ui_dir}/src" -type f -newer "${index}" -print -quit 2>/dev/null)" ]; then
    return 0
  fi
  if [ -n "$(find "${ui_dir}/public" -type f -newer "${index}" -print -quit 2>/dev/null)" ]; then
    return 0
  fi
  if [ "${ui_dir}/package.json" -nt "${index}" ]; then
    return 0
  fi
  if [ -f "${ui_dir}/.umirc.js" ] && [ "${ui_dir}/.umirc.js" -nt "${index}" ]; then
    return 0
  fi
  if [ -f "${ui_dir}/.umirc.ts" ] && [ "${ui_dir}/.umirc.ts" -nt "${index}" ]; then
    return 0
  fi
  return 1
}

backend_needs_rebuild() {
  local jar="${ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
  local server_dir="${ROOT}/Horosa-Web/astrostudysrv"
  if [ ! -f "${jar}" ]; then
    return 0
  fi
  if [ -n "$(find "${server_dir}" -path '*/src/*' -type f -newer "${jar}" -print -quit 2>/dev/null)" ]; then
    return 0
  fi
  if [ -n "$(find "${server_dir}" -name 'pom.xml' -type f -newer "${jar}" -print -quit 2>/dev/null)" ]; then
    return 0
  fi
  return 1
}

if has_frontend_artifact && has_backend_artifact && [ -x "${LOCAL_CMD}" ] \
  && ! frontend_needs_rebuild && ! backend_needs_rebuild; then
  echo "[Horosa] 检测到已有构建产物，直接启动本地应用..."
  exec "${LOCAL_CMD}" "$@"
fi

echo "[Horosa] 检测到首次运行、构建产物缺失或源码已更新，开始自动部署并启动..."
exec "${BOOTSTRAP_SH}" "$@"
