#!/usr/bin/env bash
# verify_offline_pkg_install_e2e.sh —— 离线 .pkg 真装 e2e 门([FL-20260720] 制度化)。
#
# 背景(v3.5.0 双仓离线包真机翻车,同日两案):
#   ① public:模板占位符 __OFFLINE_RUNTIME_ASSET__ 渲染表漏键 → postinstall 找不到内嵌档 → 降级;
#   ② private:内嵌 .tar.zst,而 macOS 系统 tar(libarchive 无 zstd)在 PKInstallSandbox 净化
#      PATH 下无第三方 zstd 兜底 → 解压必败 → 降级;App 首启读到旧版缓存报「版本不符」。
#   两案共同盲区:全链自检只测过「runtime 归档能启动服务」,从未测过「成品 .pkg 里的
#   postinstall 在安装沙盒等价环境下真装成功」。本脚本补上这最后一段,并写 stamp 供
#   preflight 哨兵绑定成品 pkg 校验(哈希不符/缺 stamp = 发布拦截)。
#
# 用法: verify_offline_pkg_install_e2e.sh <offline.pkg> <expected-runtime-version>
# 行为: pkgutil --expand-full 展开成品包 → 净化 PATH + HOROSA_RUNTIME_SHARED_ROOT 重定向
#       临时目录 真跑 Scripts/postinstall → 断言:无 pending 降级、runtime/current 落位、
#       runtime-manifest.json 版本 == 期望、install-source.json 写入。
set -euo pipefail

PKG="${1:?用法: $0 <offline.pkg> <expected-runtime-version>}"
EXPECTED="${2:?缺 expected-runtime-version}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALLER_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
STAMP_PATH="${INSTALLER_ROOT}/build/offline-pkg-e2e.stamp"

[ -s "${PKG}" ] || { echo "e2e ERROR: pkg 不存在或为空: ${PKG}" >&2; exit 1; }

WORK="$(mktemp -d /tmp/horosa-pkg-e2e.XXXXXX)"
cleanup() { rm -rf "${WORK}"; }
trap cleanup EXIT

echo "[pkg-e2e] expanding ${PKG} …"
/usr/sbin/pkgutil --expand-full "${PKG}" "${WORK}/expanded"

POSTINSTALL="$(/usr/bin/find "${WORK}/expanded" -maxdepth 3 -type f -path '*Scripts/postinstall' | head -n 1)"
[ -n "${POSTINSTALL}" ] || { echo "e2e ERROR: 展开包内找不到 Scripts/postinstall" >&2; exit 1; }
PKG_SCRIPTS_DIR="$(dirname "${POSTINSTALL}")"

# 展开包内层面再验一次占位符/内嵌档(防 build 内联断言被绕过后仍出包)
if grep -nE '__[A-Z_]+__' "${POSTINSTALL}"; then
  echo "e2e ERROR: 成品包 postinstall 残留未替换占位符(见上行)" >&2; exit 1
fi
EMBED_NAME="$(sed -n 's/^ARCHIVE_NAME="\(.*\)"$/\1/p' "${POSTINSTALL}" | head -n 1)"
[ -n "${EMBED_NAME}" ] && [ -s "${PKG_SCRIPTS_DIR}/${EMBED_NAME}" ] \
  || { echo "e2e ERROR: 成品包 Scripts 缺内嵌档 ${EMBED_NAME:-<空>}" >&2; exit 1; }

SHARED="${WORK}/shared"
APP_IN_PAYLOAD="$(/usr/bin/find "${WORK}/expanded" -maxdepth 4 -type d -name '*.app' | head -n 1)"

echo "[pkg-e2e] running postinstall under sanitized PATH (shared→${SHARED}) …"
set +e
env -i \
  PATH=/usr/bin:/bin:/usr/sbin:/sbin \
  HOME="${WORK}" \
  HOROSA_RUNTIME_SHARED_ROOT="${SHARED}" \
  HOROSA_APP_PATH="${APP_IN_PAYLOAD:-${WORK}/no-app.app}" \
  /bin/bash "${POSTINSTALL}" "${PKG}" "/Applications" "/" > "${WORK}/postinstall.out" 2>&1
PI_RC=$?
set -e

tail -n 12 "${WORK}/postinstall.out" 2>/dev/null | sed 's/^/[pkg-e2e][postinstall] /'
[ -f "${SHARED}/installer.log" ] && tail -n 8 "${SHARED}/installer.log" | sed 's/^/[pkg-e2e][installer.log] /'

FAIL=""
[ ${PI_RC} -eq 0 ] || FAIL="postinstall 退出码 ${PI_RC}"
if [ -z "${FAIL}" ] && [ -f "${SHARED}/runtime-install-pending.txt" ]; then
  FAIL="安装降级 pending: $(cat "${SHARED}/runtime-install-pending.txt" 2>/dev/null | head -n 1)"
fi
if [ -z "${FAIL}" ]; then
  GOT_VER="$(/usr/bin/plutil -extract version raw -o - "${SHARED}/runtime/current/runtime-manifest.json" 2>/dev/null || true)"
  [ "${GOT_VER}" = "${EXPECTED}" ] || FAIL="runtime 版本 ${GOT_VER:-<无 manifest>} ≠ 期望 ${EXPECTED}"
fi
if [ -z "${FAIL}" ] && [ ! -s "${SHARED}/install-source.json" ]; then
  FAIL="install-source.json 未写入"
fi

PKG_SHA="$(/usr/bin/shasum -a 256 "${PKG}" | awk '{print $1}')"
mkdir -p "$(dirname "${STAMP_PATH}")"
if [ -n "${FAIL}" ]; then
  printf 'FAIL\t%s\t%s\t%s\n' "${PKG_SHA}" "${EXPECTED}" "${FAIL}" > "${STAMP_PATH}"
  echo "e2e FAIL: ${FAIL}" >&2
  exit 1
fi
printf 'OK\t%s\t%s\n' "${PKG_SHA}" "${EXPECTED}" > "${STAMP_PATH}"
echo "[pkg-e2e] OK: 离线包净化环境真装通过,runtime ${EXPECTED} 落位(stamp → ${STAMP_PATH})"
