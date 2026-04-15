#!/usr/bin/env bash
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "${INSTALLER_ROOT}/.." && pwd)"
BUILD_ROOT="${INSTALLER_ROOT}/build/runtime"
STAGE_ROOT="${BUILD_ROOT}/runtime-payload"
DIST_ROOT="${INSTALLER_ROOT}/dist"
APPLE_SIGNING_IDENTITY="${APPLE_SIGNING_IDENTITY:-}"
APPLE_SIGNING_KEYCHAIN="${APPLE_SIGNING_KEYCHAIN:-${HOME}/Library/Keychains/login.keychain-db}"
HOROSA_PUBLIC_DISTRIBUTION_RAW="${HOROSA_PUBLIC_DISTRIBUTION:-auto}"
HOROSA_PUBLIC_DISTRIBUTION="${HOROSA_PUBLIC_DISTRIBUTION_RAW}"
BOOT_JAR_SOURCE="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
BUNDLE_SOURCE_DIR="${REPO_ROOT}/runtime/mac/bundle"
BUNDLE_JAR_FALLBACK="${BUNDLE_SOURCE_DIR}/astrostudyboot.jar"
JAVA_SOURCE_DIR="${REPO_ROOT}/runtime/mac/java"
JAVA_JLINK_MODULES="java.base,java.desktop,java.instrument,java.logging,java.management,java.naming,java.net.http,java.prefs,java.scripting,java.security.jgss,java.sql,java.xml,jdk.charsets,jdk.crypto.ec,jdk.management,jdk.unsupported,jdk.zipfs"
RSYNC_FILTERS=(
  "--exclude=.DS_Store"
  "--exclude=._*"
  "--exclude=_CodeSignature"
  "--exclude=*/_CodeSignature"
  '--exclude=${env:HOME}'
  '--exclude=*/${env:HOME}'
  "--exclude=.horosa-logs"
  "--exclude=*/.horosa-logs"
  "--exclude=.pytest_cache"
  "--exclude=*/.pytest_cache"
  "--exclude=.cache"
  "--exclude=*/.cache"
  "--exclude=__pycache__"
  "--exclude=*/__pycache__"
  "--exclude=*.pyc"
  "--exclude=*.pyo"
  "--exclude=*.map"
  "--exclude=*.tmp"
  "--exclude=*.temp"
  "--exclude=*.pid"
)
read -r VERSION ARCHIVE_NAME <<EOF
$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PY'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
version = json.loads((root / 'package.json').read_text())['version']
runtime_version = str(config.get('runtimeVersion') or '').strip()
if runtime_version.lower() in ('', 'auto', 'same-as-app'):
    runtime_version = version
print(runtime_version, config['runtimeAssetName'])
PY
)
EOF
ARCHIVE_PATH="${DIST_ROOT}/${ARCHIVE_NAME}"
BUILT_AT="$(date '+%Y-%m-%d %H:%M:%S')"

if [ "${HOROSA_PUBLIC_DISTRIBUTION_RAW}" = "auto" ]; then
  if [ -n "${APPLE_SIGNING_IDENTITY}" ]; then
    HOROSA_PUBLIC_DISTRIBUTION=1
  else
    HOROSA_PUBLIC_DISTRIBUTION=0
  fi
fi

build_embedded_java_runtime() {
  local src_java="$1"
  local dest_java="$2"
  local jlink_bin="${src_java}/bin/jlink"
  local jmods_dir="${src_java}/jmods"

  if [ -x "${jlink_bin}" ] && [ -d "${jmods_dir}" ]; then
    "${jlink_bin}" \
      --module-path "${jmods_dir}" \
      --add-modules "${JAVA_JLINK_MODULES}" \
      --strip-debug \
      --no-header-files \
      --no-man-pages \
      --output "${dest_java}"
    return 0
  fi

  rsync -a "${RSYNC_FILTERS[@]}" "${src_java}" "$(dirname "${dest_java}")/"
}

rm -rf "${BUILD_ROOT}"
mkdir -p "${STAGE_ROOT}/Horosa-Web/astrostudyui/scripts"
mkdir -p "${STAGE_ROOT}/Horosa-Web/scripts"
mkdir -p "${STAGE_ROOT}/Horosa-Web/astropy"
mkdir -p "${STAGE_ROOT}/Horosa-Web/flatlib-ctrad2"
mkdir -p "${STAGE_ROOT}/runtime/mac"
mkdir -p "${STAGE_ROOT}/runtime/mac/bundle"
mkdir -p "${DIST_ROOT}"

rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" "${STAGE_ROOT}/Horosa-Web/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" "${STAGE_ROOT}/Horosa-Web/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/astropy/__init__.py" "${STAGE_ROOT}/Horosa-Web/astropy/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/astropy/astrostudy" "${STAGE_ROOT}/Horosa-Web/astropy/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/astropy/websrv" "${STAGE_ROOT}/Horosa-Web/astropy/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/flatlib-ctrad2/flatlib" "${STAGE_ROOT}/Horosa-Web/flatlib-ctrad2/"
if [ -f "${REPO_ROOT}/Horosa-Web/flatlib-ctrad2/LICENSE" ]; then
  rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/flatlib-ctrad2/LICENSE" "${STAGE_ROOT}/Horosa-Web/flatlib-ctrad2/"
fi
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file" "${STAGE_ROOT}/Horosa-Web/astrostudyui/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/astrostudyui/scripts/warmHorosaRuntime.js" "${STAGE_ROOT}/Horosa-Web/astrostudyui/scripts/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/scripts/repairEmbeddedPythonRuntime.py" "${STAGE_ROOT}/Horosa-Web/scripts/"
build_embedded_java_runtime "${JAVA_SOURCE_DIR}" "${STAGE_ROOT}/runtime/mac/java"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/runtime/mac/python" "${STAGE_ROOT}/runtime/mac/"
if [ -f "${BOOT_JAR_SOURCE}" ]; then
  cp -f "${BOOT_JAR_SOURCE}" "${STAGE_ROOT}/runtime/mac/bundle/astrostudyboot.jar"
elif [ -f "${BUNDLE_JAR_FALLBACK}" ]; then
  cp -f "${BUNDLE_JAR_FALLBACK}" "${STAGE_ROOT}/runtime/mac/bundle/astrostudyboot.jar"
else
  echo "missing astrostudyboot.jar in build output and runtime bundle fallback" >&2
  exit 1
fi
zip -q -d "${STAGE_ROOT}/runtime/mac/bundle/astrostudyboot.jar" \
  'BOOT-INF/lib/netty-transport-native-kqueue-*-osx-x86_64.jar' \
  'BOOT-INF/lib/netty-resolver-dns-native-macos-*-osx-x86_64.jar' >/dev/null 2>&1 || true
rm -rf \
  "${STAGE_ROOT}/runtime/mac/python/lib/python3.12/ensurepip" \
  "${STAGE_ROOT}/runtime/mac/python/include" \
  "${STAGE_ROOT}/runtime/mac/python/share" \
  "${STAGE_ROOT}/runtime/mac/python/Resources/English.lproj/Documentation" \
  "${STAGE_ROOT}/runtime/mac/python/lib/python3.12/config-3.12-darwin"
find "${STAGE_ROOT}/runtime/mac/python/lib" -type d \( -name 'test' -o -name 'tests' -o -name '__pycache__' -o -name 'idlelib' -o -name 'turtledemo' \) -prune -exec rm -rf {} + 2>/dev/null || true
find "${STAGE_ROOT}" -type d \( -name '.horosa-logs' -o -name '.pytest_cache' -o -name '.cache' -o -name '__pycache__' \) -prune -exec rm -rf {} + 2>/dev/null || true
find "${STAGE_ROOT}" -type d -name '_CodeSignature' -prune -exec rm -rf {} + 2>/dev/null || true
find "${STAGE_ROOT}" \( -name '._*' -o -name '.DS_Store' \) -exec rm -rf {} + 2>/dev/null || true
find "${STAGE_ROOT}" \( -name '*.pyc' -o -name '*.pyo' -o -name '*.map' -o -name '*.tmp' -o -name '*.temp' -o -name '*.pid' \) -delete 2>/dev/null || true
find "${STAGE_ROOT}/runtime/mac/python/lib" -type f \( -name '*.a' -o -name '*.o' \) -delete 2>/dev/null || true
/usr/bin/python3 "${STAGE_ROOT}/Horosa-Web/scripts/repairEmbeddedPythonRuntime.py" --repair "${STAGE_ROOT}/runtime/mac/python"
if [ "${HOROSA_PUBLIC_DISTRIBUTION}" = "1" ] && [ -n "${APPLE_SIGNING_IDENTITY}" ]; then
  /usr/bin/python3 "${INSTALLER_ROOT}/scripts/sign_runtime_payload.py" \
    "${STAGE_ROOT}/runtime/mac" \
    --identity "${APPLE_SIGNING_IDENTITY}" \
    --keychain "${APPLE_SIGNING_KEYCHAIN}"
fi

python3 - <<INNERPY
import json, pathlib
manifest = {"version": "${VERSION}", "built_at": "${BUILT_AT}"}
path = pathlib.Path(r"${STAGE_ROOT}/runtime-manifest.json")
path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
INNERPY

(
  cd "${BUILD_ROOT}"
  COPYFILE_DISABLE=1 COPY_EXTENDED_ATTRIBUTES_DISABLE=1 /usr/bin/tar --disable-copyfile -czf "${ARCHIVE_PATH}" runtime-payload
)

python3 - <<'PYVERIFY' "${ARCHIVE_PATH}"
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

archive = pathlib.Path(sys.argv[1])
root = pathlib.Path(tempfile.mkdtemp(prefix="horosa-runtime-verify-"))
try:
    subprocess.run(
        ["/usr/bin/tar", "-xzf", str(archive), "-C", str(root)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    java_bin = root / "runtime-payload/runtime/mac/java/bin/java"
    python_bin = root / "runtime-payload/runtime/mac/python/bin/python3"
    subprocess.run(
        [str(java_bin), "-version"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [
            str(python_bin),
            "-c",
            "import cherrypy, jsonpickle, swisseph; print('ok')",
        ],
        check=True,
        env={
            **os.environ,
            "PYTHONNOUSERSITE": "1",
        },
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
finally:
    shutil.rmtree(root, ignore_errors=True)
PYVERIFY

echo "runtime payload ready: ${ARCHIVE_PATH}"
