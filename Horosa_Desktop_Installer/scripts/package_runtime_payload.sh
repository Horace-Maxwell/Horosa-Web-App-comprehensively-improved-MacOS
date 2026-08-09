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
  "--exclude=.git"
  "--exclude=*/.git"
  "--exclude=__pycache__"
  "--exclude=*/__pycache__"
  "--exclude=*.pyc"
  "--exclude=*.pyo"
  "--exclude=*.map"
  "--exclude=*.tmp"
  "--exclude=*.temp"
  "--exclude=*.pid"
)
# TAB 分隔(appName 可含空格)
IFS=$'\t' read -r VERSION ARCHIVE_NAME PAYLOAD_APP_NAME <<EOF
$(INSTALLER_ROOT_ENV="${INSTALLER_ROOT}" python3 - <<'PY'
import json, os, pathlib
root = pathlib.Path(os.environ['INSTALLER_ROOT_ENV'])
config = json.loads((root / 'config/release_config.json').read_text())
version = json.loads((root / 'package.json').read_text())['version']
runtime_version = str(config.get('runtimeVersion') or '').strip()
if runtime_version.lower() in ('', 'auto', 'same-as-app'):
    runtime_version = version
print(runtime_version, config['runtimeAssetName'], config['appName'], sep='\t')
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
    # [WS-3e·CDS修复] jlink 默认不生成 base CDS archive(lib/server/classes.jsa)——
    # 缺 base 时 -XX:ArchiveClassesAtExit 动态 dump 直接拒绝("base CDS archive is not
    # loaded"),首启后台自训链自上线以来一直静默失败、用户从未享受过 AppCDS。
    # 此处就地补 dump(~11MB,随 jdk-runtime 部件;实测 zulu17 一次 ~15s)。
    if ! "${dest_java}/bin/java" -Xshare:dump >/dev/null 2>&1; then
      echo "WARN: base CDS archive dump failed (jdk-runtime 将无 classes.jsa,自训/预置链退化为无 CDS)" >&2
    fi
    return 0
  fi

  rsync -a "${RSYNC_FILTERS[@]}" "${src_java}" "$(dirname "${dest_java}")/"
}

rm -rf "${BUILD_ROOT}"
mkdir -p "${STAGE_ROOT}/Horosa-Web/astrostudyui/scripts"
mkdir -p "${STAGE_ROOT}/Horosa-Web/scripts"
mkdir -p "${STAGE_ROOT}/Horosa-Web/astropy"
mkdir -p "${STAGE_ROOT}/Horosa-Web/flatlib-ctrad2"
mkdir -p "${STAGE_ROOT}/Horosa-Web/vendor"
mkdir -p "${STAGE_ROOT}/runtime/mac"
mkdir -p "${STAGE_ROOT}/runtime/mac/bundle"
mkdir -p "${DIST_ROOT}"

rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" "${STAGE_ROOT}/Horosa-Web/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" "${STAGE_ROOT}/Horosa-Web/"
# (astropy 仓根 __init__.py 已移除——它会让本仓目录遮蔽 PyPI 天文库 astropy,见 tests/test_pkg_hygiene.py)
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/astropy/astrostudy" "${STAGE_ROOT}/Horosa-Web/astropy/"
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/astropy/websrv" "${STAGE_ROOT}/Horosa-Web/astropy/"
if [ -d "${REPO_ROOT}/Horosa-Web/vendor" ]; then
  rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/vendor/" "${STAGE_ROOT}/Horosa-Web/vendor/"
fi
if [ -f "${REPO_ROOT}/THIRD_PARTY_NOTICES.md" ]; then
  rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/THIRD_PARTY_NOTICES.md" "${STAGE_ROOT}/"
fi
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/flatlib-ctrad2/flatlib" "${STAGE_ROOT}/Horosa-Web/flatlib-ctrad2/"
if [ -f "${REPO_ROOT}/Horosa-Web/flatlib-ctrad2/LICENSE" ]; then
  rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/flatlib-ctrad2/LICENSE" "${STAGE_ROOT}/Horosa-Web/flatlib-ctrad2/"
fi
# --- 新鲜度 guard（v2.1.4 教训）---------------------------------------------------
# 发布链路只 copy 预编译产物(dist-file / astrostudyboot.jar)、不重编。若源码比产物新，
# 说明很可能忘了重建，会静默发布陈旧代码。这里在打包前显式拦截。
# 确认确实无需重建(例如只动了文档/无关文件)可设 HOROSA_SKIP_FRESHNESS_GUARD=1 跳过。
DIST_INDEX="${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file/index.html"
if [ "${HOROSA_SKIP_FRESHNESS_GUARD:-0}" != "1" ] && [ -f "${DIST_INDEX}" ]; then
  # src/.umi* 是 umi 生成目录(dev 服务器运行中持续写入),不是源码——纳入比较会造成
  # 「只要 preview 开着就永远打不了包」的守卫误报;排除之(真源码新于产物仍照常拦)。
  if [ -n "$(find "${REPO_ROOT}/Horosa-Web/astrostudyui/src" -type f -not -path "*/src/.umi*" -newer "${DIST_INDEX}" -print -quit 2>/dev/null || true)" ]; then
    echo "ERROR: dist-file 比前端源码旧——很可能忘了重建前端包。" >&2
    echo "       cd Horosa-Web/astrostudyui && npm run build && npm run build:file" >&2
    echo "       (确认无需重建可设 HOROSA_SKIP_FRESHNESS_GUARD=1)" >&2
    exit 1
  fi
fi
if [ "${HOROSA_SKIP_FRESHNESS_GUARD:-0}" != "1" ] && [ -f "${BOOT_JAR_SOURCE}" ]; then
  if [ -n "$(find "${REPO_ROOT}"/Horosa-Web/astrostudysrv/*/src/main -type f -newer "${BOOT_JAR_SOURCE}" -print -quit 2>/dev/null || true)" ]; then
    echo "ERROR: astrostudyboot.jar 比后端源码旧——很可能忘了重建后端 fat jar。" >&2
    echo "       cd Horosa-Web/astrostudysrv && mvn -f boundless/pom.xml install -DskipTests && mvn -f astrostudy/pom.xml install -DskipTests && mvn -f astrostudyboot/pom.xml clean package -DskipTests" >&2
    echo "       (确认无需重建可设 HOROSA_SKIP_FRESHNESS_GUARD=1)" >&2
    exit 1
  fi
fi
# -----------------------------------------------------------------------------------
rsync -a "${RSYNC_FILTERS[@]}" "${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file" "${STAGE_ROOT}/Horosa-Web/astrostudyui/"
# ── [B2] 前端旁置预压缩:为可压缩产物生成 <file>.gz(-9,保留原件),壳内 tiny_http 按
# Accept-Encoding 供给(Content-Encoding: gzip)。仅压 >4KB 的 js/css/html/json/svg/map;
# 已存在且不比原件旧则跳过。首屏关键链 ~6.9MB 未压缩 → gzip 后约 1/4,温启配合
# immutable+ETag 进一步归零。失败不阻断打包(壳侧无旁件即回退原件,零功能差异)。
if command -v gzip >/dev/null 2>&1; then
  find "${STAGE_ROOT}/Horosa-Web/astrostudyui/dist-file" -type f \
    \( -name '*.js' -o -name '*.css' -o -name '*.html' -o -name '*.json' -o -name '*.svg' -o -name '*.map' \) \
    -size +4k -print0 2>/dev/null | while IFS= read -r -d '' f; do
      if [ ! -f "${f}.gz" ] || [ "${f}" -nt "${f}.gz" ]; then
        gzip -k -9 -f "${f}" 2>/dev/null || true
      fi
    done
  GZ_COUNT=$(find "${STAGE_ROOT}/Horosa-Web/astrostudyui/dist-file" -name '*.gz' | wc -l | tr -d ' ')
  echo "[payload] dist-file 预压缩旁件: ${GZ_COUNT} 个 .gz"
fi
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
# ── Java exploded 布局(性能):fat jar 原样解开为 bundle/boot-exploded,运行脚本优先以
# `-cp boot-exploded JarLauncher` 启动(嵌套 jar 读取是启动主开销,实测 7.0s→2.6s,-63%;
# AppCDS 首启后台自训练再 -0.3s,见 start_horosa_local.sh maybe_train_cds_background)。
# payload 只保留 exploded、不再重复携带 fat jar(体积约省 300MB 未压缩);字节同源零功能差异。
STAGE_BOOT_JAR="${STAGE_ROOT}/runtime/mac/bundle/astrostudyboot.jar"
STAGE_BOOT_EXPLODED="${STAGE_ROOT}/runtime/mac/bundle/boot-exploded"
rm -rf "${STAGE_BOOT_EXPLODED}"
mkdir -p "${STAGE_BOOT_EXPLODED}"
if ! unzip -q "${STAGE_BOOT_JAR}" -d "${STAGE_BOOT_EXPLODED}"; then
  echo "ERROR: failed to explode astrostudyboot.jar for fast-boot layout" >&2
  exit 1
fi
if [ ! -f "${STAGE_BOOT_EXPLODED}/org/springframework/boot/loader/JarLauncher.class" ]; then
  echo "ERROR: exploded boot layout missing JarLauncher (unexpected jar structure)" >&2
  exit 1
fi
shasum -a 256 "${STAGE_BOOT_JAR}" | awk '{print $1}' > "${STAGE_BOOT_EXPLODED}/.source-jar.sha256"
rm -f "${STAGE_BOOT_JAR}"

# ── [WS-3e] AppCDS 预训练进 payload:打包机在 stage exploded 上训练动态 .jsa(~42MB),
# 随【全量 tar】分发 → 用户首启即享 CDS(免首启训练副本 CPU 峰 + 温启 -0.3~0.4s)。
# 跨路径可用性已实证:训练/运行都是 `cd exploded && java -cp . JarLauncher`(相对
# classpath,CDS 豁免绝对路径校验;A 路径训练 → B 路径 -Xshare:on 强制加载存活)。
# 增量语义:.app-cds.jsa 不进任何部件清单(见下 java_app_files 排除)——增量更新后
# exploded 换新、旧 .jsa 失配被 JVM 自动忽略 → 首启后台自训重新生成(base 已随
# jdk-runtime 在位,自训链本轮起真实可用)。失败=警告继续(用户侧自训兜底)。
# 逃生阀:HOROSA_SKIP_CDS_PRESEED=1。
if [ "${HOROSA_SKIP_CDS_PRESEED:-0}" != "1" ]; then
  STAGE_JAVA="${STAGE_ROOT}/runtime/mac/java/bin/java"
  CDS_TRAIN_PORT=39993
  if [ -x "${STAGE_JAVA}" ] && [ -s "${STAGE_ROOT}/runtime/mac/java/lib/server/classes.jsa" ]; then
    echo "cds preseed: training dynamic archive (~40s)…"
    CDS_TMP_JSA="${STAGE_BOOT_EXPLODED}/.app-cds.jsa.train.$$"
    (
      cd "${STAGE_BOOT_EXPLODED}" && exec env         HOROSA_DESKTOP_MONGO_OPTIONAL=1 HOROSA_DESKTOP_MONGO_SKIP_PING=1         SPRING_MAIN_LAZY_INITIALIZATION=true         "${STAGE_JAVA}" -XX:ArchiveClassesAtExit="${CDS_TMP_JSA}"         -Dlog4j2.statusLevel=WARN -Djava.awt.headless=true         -Dspring.backgroundpreinitializer.ignore=true         -Dhorosa.runtime.owner=horosa-cds-preseed         -cp . org.springframework.boot.loader.JarLauncher         --server.port="${CDS_TRAIN_PORT}" --server.address=127.0.0.1         --astrosrv=http://127.0.0.1:39992 --mongodb.ip=127.0.0.1 --redis.ip=127.0.0.1
    ) >/dev/null 2>&1 &
    CDS_TRAIN_PID=$!
    CDS_WAITED=0
    while [ "${CDS_WAITED}" -lt 60 ]; do
      if curl -s -o /dev/null -m 1 "http://127.0.0.1:${CDS_TRAIN_PORT}/heartbeat" 2>/dev/null; then break; fi
      kill -0 "${CDS_TRAIN_PID}" 2>/dev/null || break
      CDS_WAITED=$((CDS_WAITED + 1)); sleep 1
    done
    # 触达补全:lazy-init 下 heartbeat 只初始化极小 bean 集;补发高频端点各一枪
    # (400/后端不可达均可——目的只是把 controller/service/序列化链的类拉进本次 dump 的档)。
    # [R3-B2] /chart 之外再触 常用时间/八字/六壬/紫微/节气 五链,扩类捕获(冷首点更少 JIT/加载)。
    # [R4-P4-2] +/rules/ziwei(紫微判读规则链——首次交互重链,类面独立于 /ziwei/birth)。
    # ⚠️ 两处训练清单(本文件+start_horosa_local.sh)必须逐字相同,preflight[199] lockstep 锁。
    for _cds_ep in "/chart" "/common/time" "/bazi/direct" "/liureng/gods" "/ziwei/birth" "/jieqi/year" "/rules/ziwei"; do
      curl -s -o /dev/null -m 3 -X POST -H 'Content-Type: application/json' -d '{}' \
        "http://127.0.0.1:${CDS_TRAIN_PORT}${_cds_ep}" 2>/dev/null || true
    done
    kill -TERM "${CDS_TRAIN_PID}" 2>/dev/null || true
    CDS_WAITED=0
    while [ "${CDS_WAITED}" -lt 90 ]; do
      [ -s "${CDS_TMP_JSA}" ] && ! kill -0 "${CDS_TRAIN_PID}" 2>/dev/null && break
      CDS_WAITED=$((CDS_WAITED + 1)); sleep 1
    done
    wait "${CDS_TRAIN_PID}" 2>/dev/null || true
    if [ -s "${CDS_TMP_JSA}" ]; then
      mv -f "${CDS_TMP_JSA}" "${STAGE_BOOT_EXPLODED}/.app-cds.jsa"
      echo "cds preseed ready: $(du -h "${STAGE_BOOT_EXPLODED}/.app-cds.jsa" | cut -f1)"
    else
      rm -f "${CDS_TMP_JSA}"
      echo "WARN: cds preseed 训练未产出 .jsa(payload 无预置,用户侧自训兜底)" >&2
    fi
  else
    echo "WARN: cds preseed 跳过(stage java 或 base classes.jsa 缺失)" >&2
  fi
fi
rm -rf \
  "${STAGE_ROOT}/runtime/mac/python/lib/python3.12/ensurepip" \
  "${STAGE_ROOT}/runtime/mac/python/include" \
  "${STAGE_ROOT}/runtime/mac/python/share" \
  "${STAGE_ROOT}/runtime/mac/python/Resources/English.lproj/Documentation" \
  "${STAGE_ROOT}/runtime/mac/python/lib/python3.12/config-3.12-darwin"
find "${STAGE_ROOT}/runtime/mac/python/lib/python3.12" \
  -path "${STAGE_ROOT}/runtime/mac/python/lib/python3.12/site-packages" -prune -o \
  -type d \( -name 'test' -o -name 'tests' -o -name '__pycache__' -o -name 'idlelib' -o -name 'turtledemo' \) \
  -prune -exec rm -rf {} + 2>/dev/null || true
# ── site-packages 重依赖排除表(体积/首启):UI 框架及其依赖树 ≈330MB,排盘计算零引用。
# 安全性三证:tests/test_runtime_deps_slim.py 哨兵(静态零顶层 import + meta_path 阻断下
# 全服务链可 import)+ 全量 pytest + 打包后启动冒烟。新增排除项须先过该哨兵。
# 注:astropy(pip 天文包)被太乙引擎真实使用(SkyCoord/FK5/Time)——不得排除。
# 注:pandas 被 kentang chunzi 计算路径真实使用(read_csv/DataFrame 过滤)——不得排除;
#    streamlit 顶层 import 由 websrv/kentang/kinastro_common.py 的 sys.modules 桩兜住。
SITE_PKGS="${STAGE_ROOT}/runtime/mac/python/lib/python3.12/site-packages"
for heavy in streamlit pyarrow plotly altair pydeck; do
  rm -rf "${SITE_PKGS}/${heavy}" "${SITE_PKGS}/${heavy}"-*.dist-info "${SITE_PKGS}/${heavy}"*.dist-info 2>/dev/null || true
done
echo "site-packages slimmed: $(du -sh "${SITE_PKGS}" 2>/dev/null | cut -f1)"
find "${STAGE_ROOT}/runtime/mac/python/lib/python3.12/site-packages" \
  -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
find "${STAGE_ROOT}" -type d \( -name '.horosa-logs' -o -name '.pytest_cache' -o -name '.cache' -o -name '__pycache__' \) -prune -exec rm -rf {} + 2>/dev/null || true
find "${STAGE_ROOT}" -type d -name '.git' -prune -exec rm -rf {} + 2>/dev/null || true
# ── 自包含净化(fail-closed):pip 的 editable 安装工件(__editable__*.pth/finder)与
# direct_url.json 内嵌构建机绝对路径——既不自包含也不该进发行包。先清后验,残留即中止。
find "${SITE_PKGS}" \( -name 'direct_url.json' -o -name '__editable__*' \) -exec rm -f {} + 2>/dev/null || true
SELFCONTAIN_LEFT="$(find "${SITE_PKGS}" \( -name 'direct_url.json' -o -name '__editable__*' \) 2>/dev/null | wc -l | tr -d ' ' || true)"
PTH_ABS_LEAK="$(grep -l '/Users/' "${SITE_PKGS}"/*.pth 2>/dev/null | wc -l | tr -d ' ' || true)"
if [ "${SELFCONTAIN_LEFT}" != "0" ] || [ "${PTH_ABS_LEAK}" != "0" ]; then
  echo "❌ site-packages 自包含净化未通过(editable/direct_url 残留 ${SELFCONTAIN_LEFT} 个;.pth 含绝对路径 ${PTH_ABS_LEAK} 个),打包中止" >&2
  find "${SITE_PKGS}" \( -name 'direct_url.json' -o -name '__editable__*' \) >&2 2>/dev/null || true
  grep -l '/Users/' "${SITE_PKGS}"/*.pth >&2 2>/dev/null || true
  exit 1
fi
# ── pyc 预编译(性能):用「内嵌 runtime 自己的 python」把 stdlib/site-packages/业务源码
# 预编译为 __pycache__(pyc magic 绑版本,必须自编自用),用户机首启 import 免逐文件编译
# (实测省 0.3-0.5s)。个别第三方文件语法不合本版本编不过属正常,|| true 容忍不阻断打包。
STAGE_PY_BIN="${STAGE_ROOT}/runtime/mac/python/bin/python3"
if [ -x "${STAGE_PY_BIN}" ]; then
  # [193b 2026-08-09] -f --invalidation-mode unchecked-hash:pyc 改嵌「源内容 hash」而非源 mtime
  # (timestamp 模式下任一源 mtime 扰动 → pyc 字节漂移 → 签名缓存键变 → 整部件 sha 翻转,
  #  实测 py-runtime 在 9b39↔fbb6 两态间翻转、每版全量重下)。-f 强制重编覆盖任何既有 pyc 态。
  # unchecked-hash=运行时信任 pyc 不校验(打包后源恒不变,恰为其设计场景),启动性能零损失。
  "${STAGE_PY_BIN}" -m compileall -q -j0 -f --invalidation-mode unchecked-hash \
    "${STAGE_ROOT}/runtime/mac/python/lib/python3.12" \
    "${STAGE_ROOT}/Horosa-Web/astropy" \
    "${STAGE_ROOT}/Horosa-Web/flatlib-ctrad2" \
    "${STAGE_ROOT}/Horosa-Web/vendor" >/dev/null 2>&1 || true
  echo "pyc precompiled ($(find "${STAGE_ROOT}" -name '*.pyc' 2>/dev/null | wc -l | tr -d ' ') files)"
fi
find "${STAGE_ROOT}" -type d -name '_CodeSignature' -prune -exec rm -rf {} + 2>/dev/null || true
find "${STAGE_ROOT}" \( -name '._*' -o -name '.DS_Store' \) -exec rm -rf {} + 2>/dev/null || true
# 注:此行曾含 '*.pyc' —— 会把上方 compileall 刚预编译的 pyc 全部删光(预编译白做,
# 首启回到逐文件编译)。pyc 属预期产物,只清其余临时物。
find "${STAGE_ROOT}" \( -name '*.pyo' -o -name '*.map' -o -name '*.tmp' -o -name '*.temp' -o -name '*.pid' \) -delete 2>/dev/null || true
find "${STAGE_ROOT}/runtime/mac/python/lib" -type f \( -name '*.a' -o -name '*.o' \) -delete 2>/dev/null || true
/usr/bin/python3 "${STAGE_ROOT}/Horosa-Web/scripts/repairEmbeddedPythonRuntime.py" --repair "${STAGE_ROOT}/runtime/mac/python"
PYTHONNOUSERSITE=1 PYTHONPATH="${STAGE_ROOT}/Horosa-Web/astropy" \
  "${STAGE_ROOT}/runtime/mac/python/bin/python3" - <<'PY'
import importlib

modules = [
    "websrv.webtaiyisrv",
    "websrv.webjinkousrv",
    "websrv.webqimensrv",
    "websrv.webwangjisrv",
    "websrv.webwuzhaosrv",
    "websrv.webtaixuansrv",
    "websrv.webjingjuesrv",
    "websrv.webshenyishusrv",
    "websrv.webshaozisrv",
    "websrv.webtiebansrv",
    "websrv.webfendjingsrv",
    "websrv.webbeijisrv",
    "websrv.webnanjisrv",
    "websrv.webchunzisrv",
    "websrv.webxianqinsrv",
    "websrv.webcetiansrv",
    "websrv.webqizhengkinsrv",
]
missing = []
for module_name in modules:
    try:
        importlib.import_module(module_name)
    except Exception as exc:
        missing.append(f"{module_name}: {exc!r}")
if missing:
    raise SystemExit("kentang runtime import check failed:\n" + "\n".join(missing))
print(f"kentang runtime import check OK: {len(modules)} adapters")
PY
if [ "${HOROSA_PUBLIC_DISTRIBUTION}" = "1" ] && [ -n "${APPLE_SIGNING_IDENTITY}" ]; then
  # [FL-20260804-1 修三] 经缓存层调用签名(horosa_repro_sign_cache_v1):codesign --timestamp
  # 每次向 Apple 请求时间戳 ⇒ 同字节同身份也签出不同结果 ⇒ py-runtime 113MB 每版必重下。
  # 缓存键含「待签树内容快照 + 身份 + 两个脚本自身 sha」,命中即复用上次签名产物(字节恒等)。
  # kill-switch:HOROSA_SIGN_CACHE=0 ⇒ 缓存层自旁路,退回每次真签。
  /usr/bin/python3 "${INSTALLER_ROOT}/scripts/sign_payload_cached.py" \
    "${INSTALLER_ROOT}/scripts/sign_runtime_payload.py" \
    "${STAGE_ROOT}/runtime/mac" \
    "${APPLE_SIGNING_IDENTITY}" \
    "${APPLE_SIGNING_KEYCHAIN}" \
    "${INSTALLER_ROOT}/build/.sign-cache"
fi

python3 - <<INNERPY
import json, pathlib
# appName 身份戳:安装器据此判断既有 runtime 是否属于本应用,异主一律重装(防止串目录后被「看似可用」跳过)
manifest = {"version": "${VERSION}", "built_at": "${BUILT_AT}", "appName": "${PAYLOAD_APP_NAME}"}
path = pathlib.Path(r"${STAGE_ROOT}/runtime-manifest.json")
path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
INNERPY

# ══════════════════════════════════════════════════════════════════════════
# 部件化产物(增量更新):在全量 tar 之外,把 stage 树按稳定性切 7 个部件 tar,
# 客户端只下载 sha 变化的部件(常规版本更新 ~350MB → ~70-90MB)。
# 制度:部件边界 = 本段 COMPONENT 定义(唯一真值源);SOP 文档与 preflight 哨兵
# 与之 lockstep(新增/调整部件须三处同改)。全量 tar 永远照旧产出(首装/离线/回退)。
# 类型:tree=整树替换(客户端先删 paths 再解压);files=文件级(files 清单入 lock,
#   客户端按「旧 files−新 files」删除消失文件后覆盖解压)。
# web-app 的 preserve:删 Horosa-Web 整树前把这些兄弟部件的路径 mv 暂存、解压后放回
#   (它们的 tar 不含这些子树;数据部件自身变化时由其部件重装,不 mv)。
if [ "${HOROSA_BUILD_COMPONENTS:-1}" = "1" ]; then
  COMP_DIST="${DIST_ROOT}/components"
  mkdir -p "${COMP_DIST}"
  python3 - "${BUILD_ROOT}" "${COMP_DIST}" "${VERSION}" "${PAYLOAD_APP_NAME}" "${BUILT_AT}" <<'PYCOMP'
import hashlib, json, os, pathlib, subprocess, sys

build_root = pathlib.Path(sys.argv[1])
comp_dist = pathlib.Path(sys.argv[2])
runtime_version = sys.argv[3]
app_name = sys.argv[4]
built_at = sys.argv[5]
stage = build_root / 'runtime-payload'

OWN_JAR_PREFIXES = ('astro', 'basecomm', 'boundless')  # 自家模块 jar(BOOT-INF/lib 内)
LIB_DIR = 'runtime/mac/bundle/boot-exploded/BOOT-INF/lib'

def rel_files(root: pathlib.Path):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort(); filenames.sort()
        for fn in filenames:
            out.append(str((pathlib.Path(dirpath) / fn).relative_to(stage)))
    return out

# ── 部件定义(唯一真值源;与 SOP / preflight 哨兵 lockstep)──
# [FL-20260804-1 修二] base CDS archive 豁免出增量部件(horosa_repro_jdk_cds_v1)。
# 🔴 实测定谳:jdk-runtime 两次打包 **85 个文件里只有 1 个变**,就是 lib/server/classes.jsa
# ——它由 build_embedded_java_runtime 的 `java -Xshare:dump` 生成,CDS dump 输出天然
# 不可复现(内含内存布局/指针),于是 28MB 部件每版必被判「变了」全量重下。
# 语义与既有 .app-cds.jsa 豁免完全同款:只随全量 tar 分发。JDK 树没变 ⇒ 用户本地旧
# classes.jsa 与新 JDK 完全匹配、继续可用(零感知);JDK 真升级 ⇒ jlink 输出变、本部件
# 本就要全量重下,而旧 jsa 失配会被 JVM 自行忽略,首启后台自训重建。
JDK_CDS_REL = 'runtime/mac/java/lib/server/classes.jsa'
_jdk_excludes = [] if os.environ.get('HOROSA_CDS_IN_COMPONENTS', '0') == '1' else [JDK_CDS_REL]

tree_components = [
    ('py-runtime',   ['runtime/mac/python'], []),
    ('jdk-runtime',  ['runtime/mac/java'], _jdk_excludes),
    ('ephe-data',    ['Horosa-Web/flatlib-ctrad2/flatlib/resources'], []),
    ('xuanshi-data', ['Horosa-Web/astropy/astrostudy/xuanshi'], []),
    # web-app:Horosa-Web 整树,但排除上面两个数据子树(应用时 preserve 放回)
    ('web-app',      ['Horosa-Web'], ['Horosa-Web/flatlib-ctrad2/flatlib/resources',
                                       'Horosa-Web/astropy/astrostudy/xuanshi']),
]

# 文件级部件:java-lib=三方 jar;java-app=bundle 其余 + stage 根散文件
lib_root = stage / LIB_DIR
lib_files = sorted(str((lib_root / f).relative_to(stage)) for f in os.listdir(lib_root)
                   if (lib_root / f).is_file())
java_lib_files = [f for f in lib_files
                  if not pathlib.Path(f).name.startswith(OWN_JAR_PREFIXES)]
bundle_all = rel_files(stage / 'runtime/mac/bundle')
# .app-cds.jsa 豁免出部件清单(WS-3e):只随全量 tar 分发;增量更新后旧档失配由
# JVM 忽略、首启自训再生——否则 42MB 预置档会把每版增量撑大 ~67%。
java_app_files = [f for f in bundle_all
                  if f not in set(java_lib_files)
                  and not f.endswith('/.app-cds.jsa')]
root_files = sorted(str(p.relative_to(stage)) for p in stage.iterdir() if p.is_file())
java_app_files += root_files

components = []

# ── 部件包必须【可复现】:内容不变 ⇒ sha 不变 ──────────────────────────────
# 🔴 2026-08-01 实测抓出:增量更新的复用判据是 `plan_component_diff` 里
# 「本地 components-lock 的部件 sha == 新 manifest 的部件 sha」。若打包不可复现,
# 内容一字未改的稳定部件也会 sha 漂移 → 判为「变了」→ 每版每个用户全量重下。
# 实锤:3.6.1 已装的 ephe-data 与 3.6.2 新包**逐文件内容完全一致**(158 档同摘要),
# 包 sha 却不同;七个部件无一复用,reusePct=0、downloadBytes=690MB。
# 两个与内容无关的漂移源:
#   ① gzip 头的 MTIME 字段 = 打包时刻(每次都变)      → 用 `gzip -n` 归零
#   ② **目录**条目 mtime 被 staging 拷贝刷新(文件自身 mtime 是保留的)
#                                                      → 打包前把目录 mtime 归一
# 只归一目录、不动文件:.pyc 的失效判据是所记录的 .py mtime+size,动文件 mtime 会让
# 全量 .pyc 失效、首启重编译(见踩坑「pyc 同秒同长脏缓存」)。目录 mtime 无语义。
# 这条同时是 I4 不变量(稳定部件不得变)能真正成立的前提。
EPOCH = 1700000000   # 固定基准(任意常量即可,只要跨构建恒定)

def normalize_dir_mtimes(root: pathlib.Path):
    n = 0
    for dirpath, dirnames, _ in os.walk(root):
        dirnames.sort()
        for d in [dirpath] + [os.path.join(dirpath, x) for x in dirnames]:
            try:
                os.utime(d, (EPOCH, EPOCH), follow_symlinks=False)
                n += 1
            except (OSError, NotImplementedError):
                pass
    return n

# [FL-20260804-1 修一] 文件 mtime 归一(horosa_repro_pyc_mtime_v1),**唯一例外是 .py**。
# 🔴 实测定谳(两类部件同一病根):
#   · xuanshi-data 两次打包**内容零差异**(21 文件逐一 sha 相同),sha 却变——变量是 .pyc
#     的 mtime(打包时 precompile 重生成 ⇒ 每次是当下时刻),它进 tar 头即改 sha;
#   · jdk-runtime 同理——jlink 现场生成整棵树,每个文件 mtime 都是当下时刻。
# tar 头记录每个文件的 mtime,所以「内容一字未改、sha 却变」的典型形状就是 mtime 漂移。
# 归一它是可复现构建的标准做法。
#
# 🔴 唯一不能碰的是 .py:CPython 的 pyc 失效判据 = **pyc 内部记录的 (源 .py mtime, size)**
# 与实际 .py 的 stat 比对(importlib._bootstrap_external._validate_timestamp_pyc)。动 .py 的
# mtime 会让全量 .pyc 失效、用户首启重编译(见踩坑「pyc 同秒同长脏缓存」)。
# 反过来,.pyc **自身**的 mtime 不参与任何判据,归一零语义影响。
# 其余文件类型(.so/.dylib/.jar/.jsa/数据档/脚本)均不以自身 mtime 为语义载体。
def normalize_file_mtimes(root: pathlib.Path):
    if os.environ.get('HOROSA_REPRO_PYC_MTIME', '1') != '1':
        return -1
    n = 0
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith('.py'):
                continue
            p = os.path.join(dirpath, fn)
            try:
                # 🔴 符号链接**必须**一并归一(follow_symlinks=False 即 lutimes,改的是链接
                # 自身而非目标)。实测踩过:首版跳过 symlink ⇒ jdk 树 57 个 legal/ 链接、
                # Python framework 大量链接的 mtime 每次仍是生成时刻 ⇒ 进 tar 头 ⇒ 部件照旧漂。
                os.utime(p, (EPOCH, EPOCH), follow_symlinks=False)
                n += 1
            except (OSError, NotImplementedError):
                pass
    return n

def _tar_gz(out, cmd_tail, env):
    """tar 出流 → gzip -n(不写文件名/时间戳)→ 落盘。-czf 会把打包时刻写进 gzip 头。"""
    with open(out, 'wb') as fh:
        tar = subprocess.Popen(['/usr/bin/tar', '--disable-copyfile', '-cf', '-'] + cmd_tail,
                               stdout=subprocess.PIPE, env=env)
        gz = subprocess.Popen(['/usr/bin/gzip', '-n', '-c'], stdin=tar.stdout, stdout=fh)
        tar.stdout.close()
        gz.communicate()
        if tar.wait() != 0 or gz.returncode != 0:
            raise SystemExit(f'部件打包失败: {out.name}')

def tar_from_list(name, file_list):
    lst = comp_dist / f'.{name}.list'
    lst.write_text('\n'.join(f'runtime-payload/{f}' for f in file_list) + '\n')
    out = comp_dist / f'horosa-comp-{name}-macos-arm64.tar.gz'
    env = dict(os.environ, COPYFILE_DISABLE='1', COPY_EXTENDED_ATTRIBUTES_DISABLE='1')
    _tar_gz(out, ['-C', str(build_root), '-T', str(lst)], env)
    lst.unlink()
    return out

def tar_tree(name, paths, excludes):
    out = comp_dist / f'horosa-comp-{name}-macos-arm64.tar.gz'
    env = dict(os.environ, COPYFILE_DISABLE='1', COPY_EXTENDED_ATTRIBUTES_DISABLE='1')
    tail = ['-C', str(build_root)]
    for ex in excludes:
        tail.append(f'--exclude=runtime-payload/{ex}')
    tail += [f'runtime-payload/{p}' for p in paths]
    _tar_gz(out, tail, env)
    return out

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

print(f'[components] 目录 mtime 归一 {normalize_dir_mtimes(stage)} 个(可复现打包前置)', flush=True)
_pycn = normalize_file_mtimes(stage)
print(f'[components] 文件 mtime 归一 {_pycn} 个(.py 除外;可复现打包前置)' if _pycn >= 0
      else '[components] 文件 mtime 归一已关闭(HOROSA_REPRO_PYC_MTIME=0)', flush=True)

for name, paths, excludes in tree_components:
    out = tar_tree(name, paths, excludes)
    entry = {'name': name, 'type': 'tree', 'paths': paths,
             'file': out.name, 'sha256': sha256(out), 'size': out.stat().st_size}
    if name == 'web-app':
        entry['preserve'] = ['Horosa-Web/flatlib-ctrad2/flatlib/resources',
                             'Horosa-Web/astropy/astrostudy/xuanshi']
    components.append(entry)

for name, files in (('java-lib', java_lib_files), ('java-app', java_app_files)):
    out = tar_from_list(name, files)
    components.append({'name': name, 'type': 'files', 'files': files,
                       'file': out.name, 'sha256': sha256(out), 'size': out.stat().st_size})

# 零遗漏/零重叠校验:全部部件覆盖面 = 全量 stage 文件集,且互不重叠
all_stage = set(rel_files(stage))
covered = []
for name, paths, excludes in tree_components:
    sub = set()
    for pth in paths:
        sub |= {f for f in all_stage if f == pth or f.startswith(pth + '/')}
    for ex in excludes:
        sub -= {f for f in sub if f == ex or f.startswith(ex + '/')}
    covered.append((name, sub))
covered.append(('java-lib', set(java_lib_files)))
covered.append(('java-app', set(java_app_files)))
union, overlap = set(), []
for name, sub in covered:
    dup = union & sub
    if dup:
        overlap.append((name, sorted(dup)[:5]))
    union |= sub
missing = all_stage - union
# 部件豁免文件(全量 tar 带、增量部件不带,语义见各自注释):
#   .app-cds.jsa  — 应用动态 CDS 预置档(WS-3e)
#   classes.jsa   — JDK base CDS archive(FL-20260804-1 修二;仅在豁免生效时才允许缺席)
missing = {f for f in missing if not f.endswith('/.app-cds.jsa')}
if _jdk_excludes:
    missing = {f for f in missing if f != JDK_CDS_REL}
extra = union - all_stage
if overlap or missing or extra:
    raise SystemExit(f'component split drift: overlap={overlap[:2]} missing={sorted(missing)[:5]} extra={sorted(extra)[:5]}')

lock = {'schemaVersion': 1, 'runtimeVersion': runtime_version, 'appName': app_name,
        'builtAt': built_at, 'components': components}
lock_text = json.dumps(lock, ensure_ascii=False, indent=2) + '\n'
(comp_dist / 'components-lock.json').write_text(lock_text)
# lock 同步进 stage 根:全量 tar 自带已装部件清单(客户端增量 diff 的本地基准;
# 切分枚举发生在写入前,故 lock 不属于任何部件——增量应用成功后由客户端写新 lock)
(stage / 'components-lock.json').write_text(lock_text)
total = sum(c['size'] for c in components)
print(f"components ready: {len(components)} parts, total {total/1048576:.0f}MB -> {comp_dist}")
for c in components:
    print(f"  {c['name']:14s} {c['size']/1048576:8.1f}MB  {c['sha256'][:12]}")
PYCOMP
fi

(
  cd "${BUILD_ROOT}"
  COPYFILE_DISABLE=1 COPY_EXTENDED_ATTRIBUTES_DISABLE=1 /usr/bin/tar --disable-copyfile -czf "${ARCHIVE_PATH}" runtime-payload
)

# [WP-I] zst 姊妹档:仅供离线 pkg 内嵌(在线更新链资产仍是 tar.gz,零波及)。
# zstd -T0 多线程压缩,安装侧解压比单线程 gunzip 快数倍且包体更小;构建机无 zstd 或
# 显式跳过(HOROSA_SKIP_ZSTD_ARCHIVE=1)则只出 gz,build_desktop_release 自动回退嵌 gz。
ARCHIVE_PATH_ZST="${ARCHIVE_PATH%.tar.gz}.tar.zst"
if [ "${HOROSA_SKIP_ZSTD_ARCHIVE:-0}" != "1" ] && command -v zstd >/dev/null 2>&1; then
  echo "packing zst sibling (zstd -T0 -15)…"
  (
    cd "${BUILD_ROOT}"
    COPYFILE_DISABLE=1 COPY_EXTENDED_ATTRIBUTES_DISABLE=1 /usr/bin/tar --disable-copyfile -cf - runtime-payload \
      | zstd -T0 -15 -f -q -o "${ARCHIVE_PATH_ZST}"
  )
  # 自检:系统 tar 必须能读(postinstall 解压走 /usr/bin/tar -xf 自动侦测)——读不了就删档回退 gz。
  if /usr/bin/tar -tf "${ARCHIVE_PATH_ZST}" >/dev/null 2>&1; then
    echo "zst sibling ready: $(du -h "${ARCHIVE_PATH_ZST}" | cut -f1) (gz: $(du -h "${ARCHIVE_PATH}" | cut -f1))"
  else
    echo "WARN: 系统 tar 读不了刚产出的 zst 档,删除之(离线 pkg 将回退内嵌 gz)" >&2
    rm -f "${ARCHIVE_PATH_ZST}"
  fi
else
  rm -f "${ARCHIVE_PATH_ZST}" 2>/dev/null || true
  echo "WARN: zstd 不可用或被跳过,未产出 zst 姊妹档(离线 pkg 将内嵌 gz)" >&2
fi

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
