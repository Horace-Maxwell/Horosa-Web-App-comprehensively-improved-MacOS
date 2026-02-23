#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

safe_rm() {
  local path="$1"
  if [ -e "${path}" ]; then
    rm -rf "${path}"
    echo "[clean] removed ${path#${ROOT}/}"
  fi
}

echo "[clean] preparing repository tree for GitHub upload..."

# Local runtime state
safe_rm "${ROOT}/Horosa-Web/.horosa-local-logs"
safe_rm "${ROOT}/Horosa-Web/.horosa-local-logs-win"
safe_rm "${ROOT}/Horosa-Web/.horosa-browser-profile"
safe_rm "${ROOT}/Horosa-Web/.horosa_java.pid"
safe_rm "${ROOT}/Horosa-Web/.horosa_py.pid"
safe_rm "${ROOT}/Horosa-Web/\${sys:user.home}"

# Frontend generated files
safe_rm "${ROOT}/Horosa-Web/astrostudyui/node_modules"
safe_rm "${ROOT}/Horosa-Web/astrostudyui/.umi"
safe_rm "${ROOT}/Horosa-Web/astrostudyui/.umi-production"
safe_rm "${ROOT}/Horosa-Web/astrostudyui/dist"
safe_rm "${ROOT}/Horosa-Web/astrostudyui/dist-file"
while IFS= read -r -d '' umi_dir; do
  safe_rm "${umi_dir}"
done < <(find "${ROOT}/Horosa-Web/astrostudyui" -type d \( -name .umi -o -name .umi-production \) -print0)

# Java generated files
while IFS= read -r -d '' target_dir; do
  safe_rm "${target_dir}"
done < <(find "${ROOT}/Horosa-Web/astrostudysrv" -type d -name target -print0)

# Optional offline runtime bundles (very large)
safe_rm "${ROOT}/runtime/mac/java"
safe_rm "${ROOT}/runtime/mac/python"
safe_rm "${ROOT}/runtime/mac/bundle/astrostudyboot.jar"
safe_rm "${ROOT}/runtime/mac/bundle/dist"
safe_rm "${ROOT}/runtime/mac/bundle/dist-file"
safe_rm "${ROOT}/runtime/windows"
safe_rm "${ROOT}/.runtime"

# macOS metadata noise
find "${ROOT}" -name ".DS_Store" -type f -delete

echo "[clean] done."
