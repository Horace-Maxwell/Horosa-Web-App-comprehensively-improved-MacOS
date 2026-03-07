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

if has_frontend_artifact && has_backend_artifact && [ -x "${LOCAL_CMD}" ]; then
  echo "[Horosa] 检测到已有构建产物，直接启动本地应用..."
  exec "${LOCAL_CMD}" "$@"
fi

echo "[Horosa] 首次运行或构建产物缺失，开始自动部署并启动..."
exec "${BOOTSTRAP_SH}" "$@"
