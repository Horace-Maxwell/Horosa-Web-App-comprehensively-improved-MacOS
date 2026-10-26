#!/usr/bin/env bash
# ============================================================================
# refresh_boot_exploded.sh —— dev 机重建 Java exploded 快启布局。
#
# 背景:start_horosa_local.sh 有保鲜守卫「target jar 比 boot-exploded 新 → 回退
# fat-jar 路径(绝不跑旧代码)」。dev 机每次重编后端(聚合 pom)后 target jar 变新,exploded
# 即 stale → 之后所有本机启动/ladder 测量都静默落在 fat-jar 回退档(Java 段 ~7.0s,
# 而 exploded+CDS 档 ~2.6s),测出来的数并不代表装机后的真实启动。
#
# 本脚本 = 守卫的配套修复工具:从当前 target jar 重建 exploded(与打包期
# package_runtime_payload.sh 同款步骤,字节同源),旧 .app-cds.jsa 随目录删除,
# 下次启动由 maybe_train_cds_background 自训链在最终路径重新生成。
#
# 用法: bash Horosa_Desktop_Installer/scripts/refresh_boot_exploded.sh [--force]
#   --force  即使 exploded 不比 target jar 旧也强制重建
# ============================================================================
set -euo pipefail
# [exit-guard] bash 3.2:set -u 因未赋值变量中止时,EXIT trap 里拿到的 $? 是 0(失败会被报成成功)。显式 exit 都经下面的
#   exit 记一笔;进 EXIT 时没记过 = 中止,按失败计。EXIT trap 一律写成 trap 'hx_on_exit <原处理>' EXIT(处理函数里读到的 $?
#   已是改判后的值);脚本末尾必须显式 exit。检查器 check_shell_exit_guard.py 机检。
HX_EXITED=0; exit(){ local _hx_s=$?; HX_EXITED=1; if [ "$#" -eq 0 ]; then builtin exit "${_hx_s}"; fi; builtin exit "$@"; }
hx_status(){ return "$1"; }
hx_on_exit(){ local _hx_r=$?; if [ "${_hx_r}" = "0" ] && [ "${HX_EXITED}" != "1" ]; then _hx_r=1; fi; set +e; hx_status "${_hx_r}"; "$@"; builtin exit "${_hx_r}"; }

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
JAR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
BUNDLE_DIR="${REPO_ROOT}/runtime/mac/bundle"
EXPLODED="${BUNDLE_DIR}/boot-exploded"
FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

if [ ! -f "${JAR}" ]; then
  echo "ERROR: target jar 不存在: ${JAR}" >&2
  echo "先构建后端(聚合 pom,按依赖序构建全部模块): mvn -f Horosa-Web/astrostudysrv/pom.xml clean install -DskipTests" >&2
  exit 1
fi

if [ "${FORCE}" != "1" ] && [ -f "${EXPLODED}/META-INF/MANIFEST.MF" ] \
  && [ ! "${JAR}" -nt "${EXPLODED}/META-INF/MANIFEST.MF" ]; then
  echo "boot-exploded 已新鲜(不比 target jar 旧),无需重建。强制重建用 --force。"
  exit 0
fi

echo "重建 boot-exploded ← $(basename "${JAR}") ($(du -h "${JAR}" | cut -f1))"
mkdir -p "${BUNDLE_DIR}"
TMP_JAR="${BUNDLE_DIR}/.refresh-jar.$$"
NEW_DIR="${EXPLODED}.new.$$"
cleanup_tmp() { rm -rf "${TMP_JAR}" "${NEW_DIR}" 2>/dev/null || true; }
trap 'hx_on_exit cleanup_tmp' EXIT

cp -f "${JAR}" "${TMP_JAR}"
# 与打包期一致:剔除 x86_64 原生 netty(Apple Silicon 无用,少载两个嵌套 jar)
zip -q -d "${TMP_JAR}" \
  'BOOT-INF/lib/netty-transport-native-kqueue-*-osx-x86_64.jar' \
  'BOOT-INF/lib/netty-resolver-dns-native-macos-*-osx-x86_64.jar' >/dev/null 2>&1 || true

mkdir -p "${NEW_DIR}"
if ! unzip -q "${TMP_JAR}" -d "${NEW_DIR}"; then
  echo "ERROR: unzip 失败(磁盘满?)" >&2
  exit 1
fi
if [ ! -f "${NEW_DIR}/org/springframework/boot/loader/JarLauncher.class" ]; then
  echo "ERROR: exploded 布局缺 JarLauncher(jar 结构异常)" >&2
  exit 1
fi
shasum -a 256 "${JAR}" | awk '{print $1}' > "${NEW_DIR}/.source-jar.sha256"
rm -f "${TMP_JAR}"

# 原子换:旧目录(连同已失配的旧 .app-cds.jsa)整体退场。CDS 档案与类文件强绑定,
# 换类后旧 .jsa 本就会被 JVM 忽略——干脆删净,下次启动自训链(maybe_train_cds_background)
# 在最终路径重训(注意:.jsa 生成约需服务就绪后 ~60-120s 后台跑完,期间启动无 CDS 增益)。
rm -rf "${EXPLODED}"
mv "${NEW_DIR}" "${EXPLODED}"
trap - EXIT

# ⚠️ unzip 恢复的是归档内条目的打包时刻 mtime(比 jar 文件本身的 mtime 旧)——不 touch
# 的话保鲜守卫 [ jar -nt MANIFEST ] 依然为真,重建了个寂寞照样回退。守卫只看 MANIFEST,
# touch 它一个即可(整树 touch 80k 文件反而制造无谓 IO)。
touch "${EXPLODED}/META-INF/MANIFEST.MF"
if [ "${JAR}" -nt "${EXPLODED}/META-INF/MANIFEST.MF" ]; then
  echo "ERROR: touch 后 MANIFEST 仍比 target jar 旧(时钟异常?)——守卫仍会回退 fat-jar" >&2
  exit 1
fi

echo "✓ boot-exploded 重建完成: ${EXPLODED}"
echo "  - MANIFEST mtime: $(stat -f '%Sm' "${EXPLODED}/META-INF/MANIFEST.MF")"
echo "  - .app-cds.jsa 已清(下次启动服务就绪后自训重生成)"
echo "  - 生效方式:重启本地服务(stop_horosa_local.sh && start_horosa_local.sh)"
exit 0
