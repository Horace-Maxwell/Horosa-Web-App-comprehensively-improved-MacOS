#!/usr/bin/env bash
# verify_postinstall_version_matrix.sh —— 安装器「同版本号 runtime」判别向量(四格 + 一格咬合)。
#
# 背景:postinstall 遇到已装 runtime 时,曾只比 runtime-manifest.json 的 version 字符串 —— 同版本号重打过的包
#   一个字节也装不进去,安装日志只有一句 keeping current runtime。现在同版本号再比一层「内容身份」
#   (components-lock.json 的 sha256;没有 lock 退到 built_at),不同就按「版本不同」同一条路径替换。
#
# 本测试台用成品离线包的内嵌档 + **当前仓里的模板**(重新渲染,占位符取值全从成品渲染版里抠)真跑 postinstall,
#   共享目录重定向到临时目录(HOROSA_RUNTIME_SHARED_ROOT),净化 PATH,全程不碰真 /Users/Shared、不碰正在跑的 App。
#   格① 空目录首装 → 落位、版本 == 期望(等价 e2e)
#   格② 同版本同内容 → 保留(标记文件仍在,日志 same content)
#   格③ 同版本不同内容 → 替换(标记消失,日志 different content,落地 lock 与包内逐字节相同)
#   咬合:把模板的内容比对改成恒真(= 旧行为)再跑格③ → 必须**保留**(旧病复现);否则本测试台没有判别力,判失败
#   格④ 已装版本更旧 → 替换
#   格⑤ 已装版本更新 → 保留(降级门,原逻辑不动)
#
# 用法: verify_postinstall_version_matrix.sh <offline.pkg> [--keep]
#   --keep 保留临时目录(排障用)。每格真解压一次内嵌档(约 2 GB),整套约 5–10 分钟;需要 ≥ 6 GB 临时空间。
set -euo pipefail

PKG="${1:?用法: $0 <offline.pkg> [--keep]}"
KEEP="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALLER_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMPLATE="${INSTALLER_ROOT}/installer-scripts/postinstall.template"
[ -s "${PKG}" ] || { echo "matrix ERROR: pkg 不存在或为空: ${PKG}" >&2; exit 1; }
[ -s "${TEMPLATE}" ] || { echo "matrix ERROR: 模板不存在: ${TEMPLATE}" >&2; exit 1; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/horosa-pi-matrix.XXXXXX")"
cleanup() { if [ "${KEEP}" = "--keep" ]; then echo "[matrix] 保留临时目录 ${WORK}"; else rm -rf "${WORK}"; fi; }
trap cleanup EXIT

echo "[matrix] expanding ${PKG} …"
/usr/sbin/pkgutil --expand-full "${PKG}" "${WORK}/expanded"
RENDERED="$(/usr/bin/find "${WORK}/expanded" -maxdepth 3 -type f -path '*Scripts/postinstall' | head -n 1)"
[ -n "${RENDERED}" ] || { echo "matrix ERROR: 展开包内找不到 Scripts/postinstall" >&2; exit 1; }
SCRIPTS_DIR="$(dirname "${RENDERED}")"
APP_IN_PAYLOAD="$(/usr/bin/find "${WORK}/expanded" -maxdepth 4 -type d -name '*.app' | head -n 1)"

# ── 用当前模板重新渲染:占位符取值全部从成品渲染版里抠(与 build 的渲染表同源同值)──
val() { sed -n "s/^$1=\"\(.*\)\"\$/\1/p" "${RENDERED}" | head -n 1; }
R_APP_NAME="$(val APP_NAME)"
R_ARCHIVE_NAME="$(val ARCHIVE_NAME)"
R_VERSION="$(val EXPECTED_VERSION)"
R_SHA="$(val EXPECTED_SHA256)"
R_MODE="$(val INSTALL_MODE)"
R_SHARED_NAME="$(sed -n 's#^SHARED_ROOT=.*/Users/Shared/\([^}"]*\)}".*#\1#p' "${RENDERED}" | head -n 1)"
R_RUNTIME_URL="$(sed -n 's#^RUNTIME_URL="${HOROSA_RUNTIME_URL:-\(.*\)}"$#\1#p' "${RENDERED}" | head -n 1)"
# https://github.com/<owner>/<repo>/releases/download/<tag>/<asset>
R_OWNER="$(printf '%s' "${R_RUNTIME_URL}" | awk -F/ '{print $4}')"
R_REPO="$(printf '%s' "${R_RUNTIME_URL}" | awk -F/ '{print $5}')"
R_TAG="$(printf '%s' "${R_RUNTIME_URL}" | awk -F/ '{print $8}')"
R_ASSET="$(printf '%s' "${R_RUNTIME_URL}" | awk -F/ '{print $9}')"
for v in R_APP_NAME R_ARCHIVE_NAME R_VERSION R_MODE R_SHARED_NAME R_OWNER R_REPO R_TAG R_ASSET; do
  [ -n "${!v}" ] || { echo "matrix ERROR: 从成品 postinstall 抠不出 ${v}" >&2; exit 1; }
done
[ -s "${SCRIPTS_DIR}/${R_ARCHIVE_NAME}" ] || { echo "matrix ERROR: 成品包 Scripts 缺内嵌档 ${R_ARCHIVE_NAME}" >&2; exit 1; }

FRESH="${SCRIPTS_DIR}/postinstall.matrix"
TEMPLATE_ENV="${TEMPLATE}" OUT_ENV="${FRESH}" A="${R_APP_NAME}" S="${R_SHARED_NAME}" O="${R_ARCHIVE_NAME}" RA="${R_ASSET}" OW="${R_OWNER}" RP="${R_REPO}" T="${R_TAG}" V="${R_VERSION}" H="${R_SHA}" M="${R_MODE}" python3 - <<'PY'
import os
t = open(os.environ['TEMPLATE_ENV'], encoding='utf-8').read()
for k, e in (('__APP_NAME__', 'A'), ('__SHARED_ROOT_NAME__', 'S'), ('__OFFLINE_RUNTIME_ASSET__', 'O'), ('__RUNTIME_ASSET__', 'RA'),
             ('__REPO_OWNER__', 'OW'), ('__REPO_NAME__', 'RP'), ('__RUNTIME_RELEASE_TAG__', 'T'), ('__VERSION__', 'V'),
             ('__RUNTIME_SHA256__', 'H'), ('__INSTALL_MODE__', 'M')):
    t = t.replace(k, os.environ[e])
open(os.environ['OUT_ENV'], 'w', encoding='utf-8').write(t)
PY
chmod 755 "${FRESH}"
if grep -nE '__[A-Z_]+__' "${FRESH}"; then echo "matrix ERROR: 重渲染的 postinstall 残留占位符(模板新增占位符须同步本脚本与 build 渲染表)" >&2; exit 1; fi

# 咬合变种 = 把内容比对改成恒真(旧行为:同版本号一律保留)
BUGGY="${SCRIPTS_DIR}/postinstall.buggy"
sed 's#if \[ -n "${EXISTING_IDENTITY}" \] && \[ "${EXISTING_IDENTITY}" = "${PAYLOAD_IDENTITY}" \]; then#if true; then#' "${FRESH}" > "${BUGGY}"
chmod 755 "${BUGGY}"
cmp -s "${FRESH}" "${BUGGY}" && { echo "matrix ERROR: 造不出咬合变种(模板里的内容比对行变了,请同步本脚本)" >&2; exit 1; }

SHARED="${WORK}/shared"
CUR="${SHARED}/runtime/current"
LOG="${SHARED}/installer.log"
MARK="${CUR}/.matrix-marker"

run_pi() {   # run_pi <postinstall> <标签>
  local script="$1" label="$2" before=0
  [ -f "${LOG}" ] && before="$(wc -l < "${LOG}" | tr -d ' ')"
  set +e
  env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin HOME="${WORK}" \
    HOROSA_RUNTIME_SHARED_ROOT="${SHARED}" HOROSA_APP_PATH="${APP_IN_PAYLOAD:-${WORK}/no-app.app}" \
    /bin/bash "${script}" "${PKG}" "/Applications" "/" > "${WORK}/${label}.out" 2>&1
  local rc=$?
  set -e
  LAST_LOG="$(tail -n +"$((before + 1))" "${LOG}" 2>/dev/null || true)"
  [ "${rc}" -eq 0 ] || { echo "matrix FAIL[${label}]: postinstall 退出码 ${rc}"; tail -n 8 "${WORK}/${label}.out"; return 1; }
  [ ! -f "${SHARED}/runtime-install-pending.txt" ] || { echo "matrix FAIL[${label}]: 安装降级 pending: $(head -n 1 "${SHARED}/runtime-install-pending.txt")"; return 1; }
  return 0
}
ver_now() { /usr/bin/plutil -extract version raw -o - "${CUR}/runtime-manifest.json" 2>/dev/null || true; }
set_ver() { /usr/bin/sed -i '' "s/\"version\": \"${1}\"/\"version\": \"${2}\"/" "${CUR}/runtime-manifest.json"; [ "$(ver_now)" = "$2" ] || { echo "matrix ERROR: 改不动 manifest 版本" >&2; exit 1; }; }
FAILS=0
step() { echo "[matrix] $1"; }

# 格①:空目录首装
step "格① 空目录首装"
run_pi "${FRESH}" g1 || FAILS=$((FAILS + 1))
[ "$(ver_now)" = "${R_VERSION}" ] || { echo "matrix FAIL[g1]: 版本 $(ver_now) ≠ 期望 ${R_VERSION}"; FAILS=$((FAILS + 1)); }
[ -f "${CUR}/components-lock.json" ] || { echo "matrix FAIL[g1]: 落地目录缺 components-lock.json(内容身份无从比起)"; FAILS=$((FAILS + 1)); }
/bin/cp -f "${CUR}/components-lock.json" "${WORK}/lock.from-payload.json"

# 格②:同版本同内容 → 保留
step "格② 同版本同内容 → 应保留"
touch "${MARK}"
run_pi "${FRESH}" g2 || FAILS=$((FAILS + 1))
[ -f "${MARK}" ] || { echo "matrix FAIL[g2]: 同版本同内容却被替换了"; FAILS=$((FAILS + 1)); }
printf '%s' "${LAST_LOG}" | grep -q "same content" || { echo "matrix FAIL[g2]: 日志缺 same content:${LAST_LOG}"; FAILS=$((FAILS + 1)); }

# 格③:同版本不同内容 → 替换
step "格③ 同版本不同内容 → 应替换"
printf '\n' >> "${CUR}/components-lock.json"    # 内容身份变、版本号不变
touch "${MARK}"
run_pi "${FRESH}" g3 || FAILS=$((FAILS + 1))
[ ! -f "${MARK}" ] || { echo "matrix FAIL[g3]: 同版本不同内容却被保留了(#同版本重打的包装不进去# 旧病)"; FAILS=$((FAILS + 1)); }
printf '%s' "${LAST_LOG}" | grep -q "different content" || { echo "matrix FAIL[g3]: 日志缺 different content:${LAST_LOG}"; FAILS=$((FAILS + 1)); }
cmp -s "${CUR}/components-lock.json" "${WORK}/lock.from-payload.json" || { echo "matrix FAIL[g3]: 替换后落地 lock 与包内不同"; FAILS=$((FAILS + 1)); }

# 咬合:旧行为变种跑格③ → 必须保留(证明本测试台判得出病)
step "咬合 用「恒保留」变种跑格③ → 旧病必须复现"
printf '\n' >> "${CUR}/components-lock.json"
touch "${MARK}"
run_pi "${BUGGY}" bite || FAILS=$((FAILS + 1))
[ -f "${MARK}" ] || { echo "matrix FAIL[bite]: 去掉内容比对的变种也替换了 → 本测试台对旧病没有判别力"; FAILS=$((FAILS + 1)); }
# 复位到与包内一致(格③ 的正版脚本再跑一次)
run_pi "${FRESH}" reset3 || FAILS=$((FAILS + 1))
cmp -s "${CUR}/components-lock.json" "${WORK}/lock.from-payload.json" || { echo "matrix FAIL[reset3]: 复位失败"; FAILS=$((FAILS + 1)); }

# 格④:已装更旧 → 替换
step "格④ 已装版本更旧 → 应替换"
set_ver "${R_VERSION}" "0.0.1-runtime1"
touch "${MARK}"
run_pi "${FRESH}" g4 || FAILS=$((FAILS + 1))
[ ! -f "${MARK}" ] || { echo "matrix FAIL[g4]: 旧版本却被保留"; FAILS=$((FAILS + 1)); }
[ "$(ver_now)" = "${R_VERSION}" ] || { echo "matrix FAIL[g4]: 替换后版本 $(ver_now) ≠ ${R_VERSION}"; FAILS=$((FAILS + 1)); }

# 格⑤:已装更新 → 保留(降级门)
step "格⑤ 已装版本更新 → 应保留(降级门)"
set_ver "${R_VERSION}" "999.0.0-runtime1"
touch "${MARK}"
run_pi "${FRESH}" g5 || FAILS=$((FAILS + 1))
[ -f "${MARK}" ] || { echo "matrix FAIL[g5]: 更新的已装版本被覆盖了(降级门失效)"; FAILS=$((FAILS + 1)); }
printf '%s' "${LAST_LOG}" | grep -q "downgrade guard" || { echo "matrix FAIL[g5]: 日志缺 downgrade guard:${LAST_LOG}"; FAILS=$((FAILS + 1)); }
set_ver "999.0.0-runtime1" "${R_VERSION}"

if [ "${FAILS}" -ne 0 ]; then
  echo "matrix FAIL: ${FAILS} 处不合(日志见 ${WORK}/*.out 与 ${LOG};加 --keep 可保留)" >&2
  [ "${KEEP}" = "--keep" ] || echo "(临时目录将被清理;要看现场重跑加 --keep)" >&2
  exit 1
fi
echo "[matrix] OK: 四格 + 咬合全部通过(runtime ${R_VERSION};同版本同内容保留 / 不同内容替换 / 旧版替换 / 新版保留 / 旧行为变种复现旧病)"
