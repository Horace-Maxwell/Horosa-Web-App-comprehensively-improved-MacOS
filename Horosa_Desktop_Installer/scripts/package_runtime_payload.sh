#!/usr/bin/env bash
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "${INSTALLER_ROOT}/.." && pwd)"
BUILD_ROOT="${INSTALLER_ROOT}/build/runtime"
STAGE_ROOT="${BUILD_ROOT}/runtime-payload"
DIST_ROOT="${INSTALLER_ROOT}/dist"
RSYNC_FILTERS=(
  "--exclude=.DS_Store"
  "--exclude=._*"
)
read -r VERSION ARCHIVE_NAME <<EOF
$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PY'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
print(config['runtimeVersion'], config['runtimeAssetName'])
PY
)
EOF
ARCHIVE_PATH="${DIST_ROOT}/${ARCHIVE_NAME}"
BUILT_AT="$(date '+%Y-%m-%d %H:%M:%S')"

rm -rf "${BUILD_ROOT}"
mkdir -p "${STAGE_ROOT}/Horosa-Web/astrostudyui/scripts"
mkdir -p "${STAGE_ROOT}/runtime/mac"
mkdir -p "${DIST_ROOT}"

rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" "${STAGE_ROOT}/Horosa-Web/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" "${STAGE_ROOT}/Horosa-Web/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/astropy" "${STAGE_ROOT}/Horosa-Web/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/flatlib-ctrad2" "${STAGE_ROOT}/Horosa-Web/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file" "${STAGE_ROOT}/Horosa-Web/astrostudyui/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/astrostudyui/scripts/warmHorosaRuntime.js" "${STAGE_ROOT}/Horosa-Web/astrostudyui/scripts/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/runtime/mac/java" "${STAGE_ROOT}/runtime/mac/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/runtime/mac/python" "${STAGE_ROOT}/runtime/mac/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/runtime/mac/bundle" "${STAGE_ROOT}/runtime/mac/"
rm -rf "${STAGE_ROOT}/runtime/mac/python/Resources/Python.app"
find "${STAGE_ROOT}" \( -name '._*' -o -name '.DS_Store' \) -exec rm -rf {} + 2>/dev/null || true

python3 - <<INNERPY
import json, pathlib
manifest = {"version": "${VERSION}", "built_at": "${BUILT_AT}"}
path = pathlib.Path(r"${STAGE_ROOT}/runtime-manifest.json")
path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
INNERPY

(
  cd "${BUILD_ROOT}"
  tar -czf "${ARCHIVE_PATH}" runtime-payload
)

echo "runtime payload ready: ${ARCHIVE_PATH}"
