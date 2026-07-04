#!/usr/bin/env bash
# Release pre-flight self-check —— 在发布前运行,把历次流程复盘发现的漏洞编码成可执行检查。
# 任何一项失败即 exit 1。新发现的检查项请持续追加到这里(见 skill「Pre-flight self-check」)。
#
#   用法:  Horosa_Desktop_Installer/scripts/release_preflight.sh
#   跳过某项:对应 env(见各检查),仅在你确认无误时用。
#
# 设计原则:能强制的就强制(脚本),不要只写在文档里靠自觉。
set -uo pipefail   # 故意不开 -e:要跑完所有检查再汇总

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "${INSTALLER_ROOT}/.." && pwd)"
fail=0
ok()   { printf '  \033[32m✅\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m❌\033[0m %s\n' "$1" >&2; fail=1; }
warn() { printf '  \033[33m⚠️\033[0m  %s\n' "$1"; }

# keg-only node@22 不在默认 PATH 的终端会让 node -e 检查假阳性失败、误拦 pre-push;缺 node 则自动补常见位置的 node。
if ! command -v node >/dev/null 2>&1; then
	for _nd in /opt/homebrew/opt/node@22/bin /opt/homebrew/bin /usr/local/opt/node@22/bin /usr/local/bin; do
		[ -x "${_nd}/node" ] && { PATH="${_nd}:${PATH}"; export PATH; break; }
	done
fi

VERSION="$(python3 -c "import json,os;print(json.load(open(os.path.join('${INSTALLER_ROOT}','package.json')))['version'])" 2>/dev/null || echo "")"
RUNTIME_VERSION="$(python3 -c "import json,os;print(json.load(open(os.path.join('${INSTALLER_ROOT}','config','release_config.json'))).get('runtimeVersion',''))" 2>/dev/null || echo "")"
[ -n "${VERSION}" ] || { echo "无法读取 package.json version,终止" >&2; exit 2; }
echo "== Release pre-flight: version ${VERSION} / runtime ${RUNTIME_VERSION} =="

# 1. 版本号 lockstep:所有该带版本号的文件都必须含当前 VERSION
echo "[1] 版本号一致性"
grep -q "\"version\": \"${VERSION}\"" "${INSTALLER_ROOT}/package.json"            && ok "package.json"        || bad "package.json version != ${VERSION}"
grep -q "^version = \"${VERSION}\"" "${INSTALLER_ROOT}/src-tauri/Cargo.toml"       && ok "Cargo.toml"          || bad "Cargo.toml version != ${VERSION}"
grep -q "\"version\": \"${VERSION}\"" "${INSTALLER_ROOT}/src-tauri/tauri.conf.json" && ok "tauri.conf.json"     || bad "tauri.conf.json version != ${VERSION}"
# CITATION.cff 须对版本（缺席即跳过，不误报）。
if [ -f "${REPO_ROOT}/CITATION.cff" ]; then
  grep -q "version: \"${VERSION}\"" "${REPO_ROOT}/CITATION.cff"                     && ok "CITATION.cff"        || bad "CITATION.cff version != ${VERSION}"
else
  ok "CITATION.cff(本仓无此文件，跳过)"
fi
grep -q "APP_VERSION = '${VERSION}'" "${INSTALLER_ROOT}/web/app.js"                 && ok "web/app.js"          || bad "web/app.js APP_VERSION != ${VERSION}"
# Cargo.lock: 本项目包的版本
if awk '/^name = "horosa-desktop-installer"$/{getline; print}' "${INSTALLER_ROOT}/src-tauri/Cargo.lock" | grep -q "version = \"${VERSION}\""; then ok "Cargo.lock"; else bad "Cargo.lock horosa-desktop-installer version != ${VERSION}"; fi
# runtimeVersion 必须是 {VERSION}-runtimeN
case "${RUNTIME_VERSION}" in "${VERSION}-runtime"*) ok "release_config runtimeVersion (${RUNTIME_VERSION})";; *) bad "runtimeVersion '${RUNTIME_VERSION}' 不是 ${VERSION}-runtimeN";; esac
# verify_launcher_console_states.py 硬编码 launcher 的 "来源 pkg <VERSION>" 断言(launcher 用 APP_VERSION 渲染该行)——
# 每版必须同步,否则 verify_desktop_packaging 在「编译+签名+公证」之后才报 ready-state 失败(v2.1.8 复盘:白白跑完一次签名公证)。
grep -q "来源 pkg ${VERSION}" "${INSTALLER_ROOT}/scripts/verify_launcher_console_states.py" && ok "verify_launcher_console_states.py(launcher 版本断言)" || bad "verify_launcher_console_states.py 仍断言旧版本 —— 改 '来源 pkg ${VERSION}' 及注入 detail 的 '本机组件版本 ${VERSION}'"

# 2. 本版 release notes 文件必须存在且非空(否则发布页只剩通用模板 —— v2.1.4 复盘 #1)
echo "[2] 本版发布说明"
[ -s "${INSTALLER_ROOT}/config/release_notes/${VERSION}.md" ] && ok "config/release_notes/${VERSION}.md 存在" || bad "缺 config/release_notes/${VERSION}.md —— 发布页会只显示通用说明"

# 3. UPGRADE_LOG 有本版条目
echo "[3] UPGRADE_LOG 条目"
grep -q "${VERSION}" "${REPO_ROOT}/UPGRADE_LOG.md" && ok "UPGRADE_LOG 提及 ${VERSION}" || bad "UPGRADE_LOG.md 没有 ${VERSION} 条目"


# 4. settings.local.json 绝不可被 git 跟踪(里面有 token / 机器路径 —— 本次复盘的泄露风险)
echo "[4] 机密文件未入库"
if git -C "${REPO_ROOT}" ls-files --error-unmatch .claude/settings.local.json >/dev/null 2>&1; then bad ".claude/settings.local.json 被 git 跟踪了(含 token,有泄露风险!)"; else ok ".claude/settings.local.json 未被跟踪"; fi
# .claude 配置 JSON 必须可解析(曾有加 token 时漏逗号弄坏过)
for f in settings.json settings.local.json launch.json; do
  p="${REPO_ROOT}/.claude/${f}"
  [ -f "${p}" ] || continue
  python3 -m json.tool "${p}" >/dev/null 2>&1 && ok ".claude/${f} 可解析" || bad ".claude/${f} JSON 解析失败"
done

# 5. 编译产物新鲜度(后端 jar / 前端 dist-file 不能比源码旧 —— 复盘 #2;打包时也会再拦一次)
echo "[5] 编译产物新鲜度"
JAR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
DIST="${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file/index.html"
if [ -f "${JAR}" ]; then
  if [ -n "$(find "${REPO_ROOT}"/Horosa-Web/astrostudysrv/*/src/main -type f -newer "${JAR}" -print -quit 2>/dev/null || true)" ]; then bad "astrostudyboot.jar 比后端源码旧 —— 需 mvn clean package 重建"; else ok "astrostudyboot.jar 比源码新"; fi
else warn "astrostudyboot.jar 不存在(发布会回退到 runtime bundle 旧 jar —— 后端有改动务必先重建)"; fi
if [ -f "${DIST}" ]; then
  if [ -n "$(find "${REPO_ROOT}/Horosa-Web/astrostudyui/src" -type f -newer "${DIST}" -print -quit 2>/dev/null || true)" ]; then bad "dist-file 比前端源码旧 —— 需 npm run build && build:file"; else ok "dist-file 比源码新"; fi
else bad "dist-file 不存在 —— 需 npm run build:file"; fi

# 6. CI 必须对当前 HEAD 通过(功能回归靠 CI 兜 —— 复盘 #3)。需要 gh。
echo "[6] CI 状态(当前 HEAD)"
if command -v gh >/dev/null 2>&1; then
  HEAD_SHA="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
  CI_JSON="$(gh run list --repo Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS --branch main --limit 10 --json headSha,status,conclusion,workflowName 2>/dev/null || echo '[]')"
  CONCL="$(printf '%s' "${CI_JSON}" | python3 -c "import sys,json;sha='${HEAD_SHA}';rs=[r for r in json.load(sys.stdin) if r.get('headSha')==sha];print((rs[0].get('conclusion') or rs[0].get('status')) if rs else 'none')" 2>/dev/null || echo 'err')"
  case "${CONCL}" in
    success) ok "CI 对 HEAD(${HEAD_SHA:0:7})成功";;
    none)    warn "CI 还没有 HEAD(${HEAD_SHA:0:7})的运行记录 —— 先 push 并等 CI 跑完";;
    *)       bad "CI 对 HEAD(${HEAD_SHA:0:7})状态=${CONCL}(需 success 才发)";;
  esac
else warn "未装 gh,跳过 CI 检查 —— 请手动确认 CI 绿"; fi

# 7. Issue #8(AI 分析 SSE)修复哨兵:catch 必须先记原始异常,SSE 流必须心跳。
#    Windows 端 v2.2.1 调试复盘:Ollama 慢首 token 时空闲断连,catch 块 sendEvent 撞 ClientAbort
#    把 RuntimeException 抛回 ai-analysis-chat-stream 线程,且原始一级异常被 safeErrorMessage
#    吞掉没记日志。本检查保证两个修复都不会被回退。
echo "[7] Issue #8(AI 分析 SSE)修复哨兵"
AIPROXY="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java"
if [ -f "${AIPROXY}" ]; then
  grep -q "QueueLog.error(AppLoggers.ErrorLogger" "${AIPROXY}" \
    && ok "AIAnalysisProxyService catch 已记原始异常(Fix 1)" \
    || bad "AIAnalysisProxyService catch 缺 QueueLog.error 记日志 —— Issue #8 一级异常会被吞掉"
  grep -q "keep-alive" "${AIPROXY}" \
    && ok "AIAnalysisProxyService SSE 心跳在位(Fix 2)" \
    || bad "AIAnalysisProxyService 缺 SSE 心跳 keep-alive —— Issue #8 Ollama 慢首 token 会触发 ClientAbort"
else
  warn "AIAnalysisProxyService.java 不存在,跳过 #8 哨兵"
fi

# 8. v2.2.1 收尾哨兵:(a) Anthropic content 块必须带 type(否则对话/测试连接 503);
#    (b) 晚子时时柱 (1,0) 对称分支必须在(否则 Java 系技法 (1,0) 回退到 庚子,与钉定 戊子 不一致)。
echo "[8] v2.2.1 收尾修复哨兵(Anthropic type + 晚子时对称分支)"
if [ -f "${AIPROXY}" ]; then
  grep -q "buildAnthropicTextPart" "${AIPROXY}" \
    && ok "Anthropic content 块带 type(buildAnthropicTextPart)" \
    || bad "AIAnalysisProxyService 缺 buildAnthropicTextPart —— Anthropic content 会漏 type 触发 503(Mac #9)"
fi
BZHELPER="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/helper/BaZiHelper.java"
if [ -f "${BZHELPER}" ]; then
  grep -q "after23NewDay && !lateZiHourUseNextDay" "${BZHELPER}" \
    && ok "晚子时时柱 (1,0) 对称分支在位(BaZiHelper)" \
    || bad "BaZiHelper 缺 (after23 && !lateZi) 对称分支 —— (1,0) 边界会回退 庚子,跨技法不一致"
else
  warn "BaZiHelper.java 不存在,跳过 (1,0) 对称分支哨兵"
fi

# 9. 更新后启动卡顿修复哨兵(本次复盘):防「更新后重启卡在 100% / 反复走 300s 全量慢路径」回归。
#    根因复盘见 docs/更新后启动卡顿修复-v2.3.1.md:① 标记仅成功时消费→失败残留致次次慢;
#    ② pid 仅判存在→残留死 pid 误拦截;③ 首启进度停住无反馈像死机;④ warmup 同步阻塞启动。
echo "[9] 更新后启动卡顿修复哨兵"
MAINRS="${INSTALLER_ROOT}/src-tauri/src/main.rs"
STARTSH="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
if [ -f "${MAINRS}" ]; then
  if grep -q "fn consume_update_complete_marker_into_state" "${MAINRS}" \
     && grep -q "consume_update_complete_marker_into_state(&app)" "${MAINRS}"; then
    ok "C① 更新标记读取即消费(consume_update_complete_marker_into_state)"
  else
    bad "main.rs 缺 consume_update_complete_marker_into_state 或未在 runtime_bootstrap 调用 —— 首启失败会残留标记致次次走 300s 慢路径"
  fi
  # 注:emit_indeterminate_progress 调用会被 cargo fmt 拆成多行(`(` 后换行),故不能 grep `(&window`(会漏报);
  # 用「函数名存在」+「首启提示文案存在」双重确认 —— 两者 cargo fmt 都不会拆。(2.3.1 踩过此误报)
  # (v2.3.2 文案已从「需完整校验 30-60 秒」改为快路径版「正在恢复启动」,哨兵同步跟改。)
  if grep -q "emit_indeterminate_progress" "${MAINRS}" \
     && grep -q "正在恢复启动" "${MAINRS}"; then
    ok "A 首启 indeterminate 等待提示在位"
  else
    bad "main.rs 首启缺 emit_indeterminate_progress 调用或提示文案 —— 更新后首启进度停住会被当成卡死"
  fi
  # D (v2.3.2):更新后首启「预写 fast-path 标记 + 不再强制全量」修复哨兵。
  # 根因:runtime 安装前已 sha256 验签,首启再走 300s 全量属冗余;且 fast-path 标记仅在「整轮成功」
  # 后才写,用户把冷首启当卡死强退 → 标记没写 → 下次又全量 → 反复重启(实测 18:23/18:26/18:28 三启)。
  # 修法:对已验签 runtime 在 start_runtime 之前预写标记,首启即走快路径,强退也不回退全量。
  # 详见 docs/更新后自启修复-v2.3.2.md。哨兵 grep 注释 sentinel(comment,cargo fmt 不拆)。
  if grep -q "需重启两三次" "${MAINRS}"; then
    ok "D 更新后首启预写 fast-path 标记(已验签 runtime 不再 300s 全量)"
  else
    bad "main.rs 缺 v2.3.2 预写 fast-path 标记修复 —— 更新后首启回到冷全量、强退反复(见 docs/更新后自启修复-v2.3.2.md)"
  fi
  # E (2.4.0 重发·真因哨兵):首启分支**删掉 cleanup_state** —— 它会 `web_shutdown.store(true)` 关掉本次刚
  # `start_static_server` 起的静态服务器(web_port)→ `emit_ready` 导航的 `frontend_url` 连不上 → 卡启动页/
  # 进不了主界面/按钮死(真机实测真因,前两次误诊弹框/慢校验都没修好)。grep 修复说明注释(cargo fmt 不拆)。
  # 真因详见 docs/更新后卡启动页-真因cleanup_state误杀静态服务器-v2.4.0.md。**铁律:首启 start_static_server 后绝不调会触发 web_shutdown 的清理。**
  if grep -q "误杀静态服务器" "${MAINRS}"; then
    ok "E 首启分支不调 cleanup_state(真因修复·静态服务器不被误杀)"
  else
    bad "main.rs 缺「误杀静态服务器」修复说明/铁律 —— 首启分支若(再)调 cleanup_state 会关掉静态服务器致更新后卡启动页(见 docs/更新后卡启动页-真因cleanup_state误杀静态服务器-v2.4.0.md)"
  fi
  # F:快路径回退从静默一行升级为醒目说明(属正常保护)+账本留痕。
  if grep -q "已自动切换完整校验" "${MAINRS}" && grep -q "rust.fast_path_fallback" "${MAINRS}"; then
    ok "F 快速启动回退醒目说明+账本留痕在位"
  else
    bad "main.rs 缺快速启动回退醒目说明(已自动切换完整校验)或账本留痕(rust.fast_path_fallback)—— 回退退化回静默一行,用户又会把回退当卡死"
  fi
else
  warn "main.rs 不存在,跳过更新卡顿哨兵(C①/A/D/E)"
fi
if [ -f "${STARTSH}" ]; then
  grep -q "reclaim_or_block_pid_file" "${STARTSH}" \
    && ok "C② pid 判存活 + 精准回收自家残留(reclaim_or_block_pid_file,取代 prune_stale_pid_file)" \
    || bad "start_horosa_local.sh 缺 reclaim_or_block_pid_file —— 残留死 pid / 卡死自家后端会误拦截启动(修法3)"
  grep -q "runtime warmup begin (background)" "${STARTSH}" \
    && ok "B warmup 后台非阻塞" \
    || bad "start_horosa_local.sh warmup 未后台化 —— 更新后首启会多等预热阻塞"
else
  warn "start_horosa_local.sh 不存在,跳过更新卡顿哨兵(C②/B)"
fi

# 10. Issue #10「服务不稳定」修复哨兵(SSE 并发竞态 + SSE 标志跨请求污染)。
#     根因复盘见 docs/服务不稳定-SSE并发与签名污染修复-v2.3.1.md:① 心跳/读流并发写非线程安全 SseEmitter→AI 断流;
#     ② __sse__ 标志(绑 request 对象)被 Tomcat 复用残留→污染排盘/predict→间歇 signature.error。
echo "[10] Issue #10(SSE 并发 + SSE 标志污染)修复哨兵"
if [ -f "${AIPROXY}" ]; then
  grep -q "class SseChannel" "${AIPROXY}" \
    && ok "A SseChannel 线程安全收口 emitter" \
    || bad "AIAnalysisProxyService 缺 SseChannel —— SSE 心跳/读流并发写 race 会让 AI 几句话后断流(#10)"
else
  warn "AIAnalysisProxyService.java 不存在,跳过 #10(A)哨兵"
fi
RHINTERCEPTOR="${REPO_ROOT}/Horosa-Web/astrostudysrv/boundless/src/main/java/boundless/spring/help/interceptor/RequestHeaderInterceptor.java"
if [ -f "${RHINTERCEPTOR}" ]; then
  if grep -q "getDispatcherType() != DispatcherType.REQUEST" "${RHINTERCEPTOR}" \
     && grep -q "TransData.setSSE(false)" "${RHINTERCEPTOR}"; then
    ok "B preHandle async 早返回 + setSSE(false) 归零(SSE 标志跨请求污染防护)"
  else
    bad "RequestHeaderInterceptor.preHandle 缺 async 早返回 或 setSSE(false) 归零 —— SSE 标志会污染排盘/predict 致间歇 signature.error(#10)"
  fi
else
  warn "RequestHeaderInterceptor.java 不存在,跳过 #10(B)哨兵"
fi

echo "[11] 西占推运 + 宫制修复哨兵(v2.5.0)"
PERCHART="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perchart.py"
ASTROCONST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/constants/AstroConst.js"
PERSIAN="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/astro/AstroPersianDirected.js"
BALB="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/balbillus.js"
# A. 宫制数量前后端同步(后端 hsys[] vs 前端 HOUSE_SYSTEM_OPTIONS):改一处必改另一处,否则 index 错位读错宫制
if [ -f "${PERCHART}" ] && [ -f "${ASTROCONST}" ]; then
  HSYS_BE="$(python3 -c "import re;t=open('${PERCHART}').read();m=re.search(r'hsys=\[(.*?)\]',t,re.S);print(len([x for x in m.group(1).split(',') if x.strip()]) if m else -1)" 2>/dev/null || echo -2)"
  HSYS_FE="$(python3 -c "import re;t=open('${ASTROCONST}').read();m=re.search(r'HOUSE_SYSTEM_OPTIONS = \[(.*?)\];',t,re.S);print(len(re.findall(r'value:',m.group(1))) if m else -1)" 2>/dev/null || echo -3)"
  if [ "${HSYS_BE}" = "${HSYS_FE}" ] && [ "${HSYS_BE}" -gt 0 ] 2>/dev/null; then
    ok "A 宫制数量前后端同步(${HSYS_BE})"
  else
    bad "A 宫制数量不同步:后端 hsys[]=${HSYS_BE} vs 前端 HOUSE_SYSTEM_OPTIONS=${HSYS_FE} —— index 错位会读错宫制"
  fi
else
  warn "perchart.py / AstroConst.js 不存在,跳过宫制同步哨兵"
fi
# B. 福点整宫制:自定义整宫制宫头必须 house.hsys=const.HOUSES_WHOLE_SIGN,否则 flatlib inHouse 加 -5° 偏移致落宫差一宫
if [ -f "${PERCHART}" ] && grep -q "custHouse_Fortuna_Whole" "${PERCHART}"; then
  if grep -q "house.hsys = const.HOUSES_WHOLE_SIGN" "${PERCHART}" && ! grep -q "house.hsys = custHouse_Fortuna_Whole" "${PERCHART}"; then
    ok "B 福点整宫制宫头走 HOUSES_WHOLE_SIGN(inHouse 无 -5° 偏移)"
  else
    bad "B 福点整宫制宫头未设 const.HOUSES_WHOLE_SIGN(或回退自定义标记) —— inHouse -5° 偏移致落宫 off-by-one"
  fi
fi
# C. 双圈盘内圈本命冻结修复:AstroPersianDirected.requestData 每次从 props.value 重算 natalParams
if [ -f "${PERSIAN}" ]; then
  grep -q "natalParams(this.props.value)" "${PERSIAN}" \
    && ok "C 波斯向运 requestData 重算 natalParams(内圈本命不冻结)" \
    || bad "C AstroPersianDirected 未从 props.value 重算 natalParams —— 换盘后内圈本命会冻结成旧盘"
fi
# D. Balbillus 旺距削减公式 N×(1−d/360) + 七星小年表(独立引擎,勿退回 k 标度实验版)
if [ -f "${BALB}" ]; then
  grep -q "1 - d / 360" "${BALB}" && grep -q "BALBILLUS_YEARS" "${BALB}" \
    && ok "D Balbillus 旺距削减公式在位" \
    || bad "D balbillus.js 缺 N×(1−d/360) 削减公式 或 BALBILLUS_YEARS"
fi

echo "[12] 本地服务端口健壮性哨兵(v2.5.0)"
WEBCHART="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
STARTSH="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
if [ -f "${WEBCHART}" ]; then
  if grep -q "def ensure_chart_port_free" "${WEBCHART}" && grep -q "ensure_chart_port_free('127.0.0.1', chart_port)" "${WEBCHART}"; then
    ok "A webchartsrv.py 绑定前回收僵尸端口(ensure_chart_port_free)"
  else
    bad "A webchartsrv.py 缺 ensure_chart_port_free —— 僵尸占 8899 会让排盘服务起不来(portend code 70)"
  fi
else
  warn "webchartsrv.py 不存在,跳过端口健壮性哨兵"
fi
if [ -f "${STARTSH}" ]; then
  grep -q "reclaim_stale_port" "${STARTSH}" \
    && ok "B start_horosa_local.sh 回收自己的僵尸端口(reclaim_stale_port)" \
    || bad "B start_horosa_local.sh 缺 reclaim_stale_port —— 端口被自己僵尸占住会阻死启动"
fi

echo "[13] 时区/夏令时(DST)自动校正哨兵(v2.5.0)"
UI_SRC="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
UI_PKG="${REPO_ROOT}/Horosa-Web/astrostudyui/package.json"
TZUTIL="${UI_SRC}/utils/timezone.js"
DSTIND="${UI_SRC}/components/comp/DstZoneIndicator.js"
if [ -f "${UI_PKG}" ]; then
  grep -q '"tz-lookup"' "${UI_PKG}" \
    && ok "A package.json 含 tz-lookup 依赖(经纬度→IANA 时区,离线)" \
    || bad "A package.json 缺 tz-lookup —— DST 自动校正无法离线求时区"
fi
if [ -f "${TZUTIL}" ]; then
  grep -q "applyDstToFields" "${TZUTIL}" && grep -q "dstAwareZoneAt" "${TZUTIL}" && grep -q "longOffset" "${TZUTIL}" \
    && ok "B timezone.js 在位(applyDstToFields + dstAwareZoneAt + Intl longOffset)" \
    || bad "B timezone.js 缺 applyDstToFields/dstAwareZoneAt/longOffset —— DST 引擎不完整"
else
  bad "B timezone.js 不存在 —— DST 自动校正引擎缺失"
fi
[ -f "${DSTIND}" ] \
  && ok "C DstZoneIndicator.js 共享指示器组件在位" \
  || bad "C DstZoneIndicator.js 不存在 —— 三表单 DST 指示器缺失"
dst_forms_ok=1
for f in "components/comp/ChartFormData.js" "components/user/ChartData.js" "components/user/CaseData.js"; do
  fp="${UI_SRC}/${f}"
  if [ -f "${fp}" ]; then
    grep -q "applyDstToFields" "${fp}" && grep -q "DstZoneIndicator" "${fp}" && grep -q "zoneManual" "${fp}" \
      || { bad "D ${f} 未接 DST(applyDstToFields/DstZoneIndicator/zoneManual) —— 该表单时区不自动校正"; dst_forms_ok=0; }
  else
    bad "D ${f} 不存在"; dst_forms_ok=0
  fi
done
[ "${dst_forms_ok}" -eq 1 ] && ok "D 三表单(ChartFormData/ChartData/CaseData)均接 DST 自动校正"

# 14-19. 启动机制稳健化哨兵(端口被占/后端未启动 根治,详见 docs/启动机制稳健化-端口与就绪.md)。
UISRC="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
WARMJS="${REPO_ROOT}/Horosa-Web/astrostudyui/scripts/warmHorosaRuntime.js"

echo "[14] 端口冲突重试哨兵(修法1:backend/chart 换口重试;web 不入环)"
if [ -f "${MAINRS}" ]; then
  if grep -q "fn start_runtime_with_port_retry" "${MAINRS}" \
     && grep -q "start_runtime_with_port_retry(" "${MAINRS}" \
     && grep -q "fn error_is_port_conflict" "${MAINRS}"; then
    ok "修法1 端口冲突重试封装在位(start_runtime_with_port_retry + error_is_port_conflict)"
  else
    bad "main.rs 缺端口冲突重试封装 —— 端口被瞬时抢走会一次失败即报死(修法1)"
  fi
  # 铁律(防 v2.4.0 [9]E 重演):重试环只重选 backend/chart,绝不读写 web_shutdown / 不重起静态服务器。
  grep -q "绝不在此被读写" "${MAINRS}" \
    && ok "修法1 铁律注释在位(web 端口/web_shutdown 不入重试环)" \
    || bad "main.rs 缺「web_shutdown 绝不在此被读写」铁律注释 —— 重试环若动 web_shutdown 会重演 [9]E 静态服务器误杀"
else
  warn "main.rs 不存在,跳过修法1 哨兵"
fi

echo "[15] 脚本端口冲突退出码哨兵(修法2:exit 3 + bind 错精确匹配)"
if [ -f "${STARTSH}" ]; then
  if grep -q "bind_err_re=" "${STARTSH}" \
     && grep -q "Address already in use" "${STARTSH}" \
     && grep -q "BindException" "${STARTSH}" \
     && grep -q "exit 3" "${STARTSH}"; then
    ok "修法2 端口冲突 exit 3 + bind 错精确匹配(Address already in use / BindException)"
  else
    bad "start_horosa_local.sh 缺 exit 3 / bind_err_re 精确 token —— 端口竞态无法被 Rust 识别重试(修法2)"
  fi
  # 防回归(红队 C2):bind 错正则绝不能含裸小写 'port' 分支(否则 Spring banner/--server.port= 会被误判)。
  if grep "bind_err_re=" "${STARTSH}" | grep -qF "|port"; then
    bad "bind_err_re 含裸 'port' 分支 —— 会把正常输出误判为端口冲突(红队 C2),请改回精确 token"
  else
    ok "修法2 bind_err_re 不含裸 port(精确匹配,无误判)"
  fi
else
  warn "start_horosa_local.sh 不存在,跳过修法2 哨兵"
fi

echo "[16] 卡死自家后端精准回收哨兵(修法3:仅杀签名核实的自家 PID)"
if [ -f "${STARTSH}" ]; then
  if grep -q "reclaim_or_block_pid_file" "${STARTSH}" \
     && grep -q "refuse to kill" "${STARTSH}" \
     && grep -q "horosa.runtime.owner" "${STARTSH}"; then
    ok "修法3 仅在 cmdline 签名核实为自家后端时 kill 续启,否则维持 exit 1(不误杀)"
  else
    bad "start_horosa_local.sh 缺修法3 精准回收(reclaim_or_block_pid_file + 签名核实 + refuse to kill)—— 可能误杀或拦死启动"
  fi
fi

echo "[17] 就绪前最小热身 + curl 兜底哨兵(修法4)"
if [ -f "${STARTSH}" ]; then
  if grep -q "warm_runtime_routes_min_sync" "${STARTSH}" \
     && grep -q "HOROSA_WARM_MINIMAL" "${STARTSH}"; then
    ok "修法4 就绪前最小同步热身在位(非致命有界,预热排盘冷 bean)"
  else
    bad "start_horosa_local.sh 缺 warm_runtime_routes_min_sync/HOROSA_WARM_MINIMAL —— 首次排盘会打到冷 bean 弹「未就绪」(修法4)"
  fi
  grep -q "urllib.request" "${STARTSH}" \
    && ok "修法4 curl 缺失时用内置 python urllib 探测(不静默放行)" \
    || bad "start_horosa_local.sh 缺 curl 缺失的 python urllib 兜底 —— 无 curl 时就绪判定会静默空转(红队 M5)"
fi
if [ -f "${WARMJS}" ]; then
  grep -q "HOROSA_WARM_MINIMAL" "${WARMJS}" \
    && ok "修法4 warmHorosaRuntime.js 支持最小热身模式(仅 /chart)" \
    || bad "warmHorosaRuntime.js 缺 HOROSA_WARM_MINIMAL 最小模式 —— 同步热身会跑全量拖慢启动(修法4)"
fi

echo "[18] 前端排盘透明重试哨兵(修法5:幂等 raw-fetch 重试,SSE/AI 排除)"
CHARTFETCH="${UISRC}/utils/chartFetch.js"
REQJS="${UISRC}/utils/request.js"
if [ -f "${CHARTFETCH}" ] && [ -f "${REQJS}" ]; then
  if grep -q "export async function fetchChartWithRetry" "${CHARTFETCH}" \
     && grep -q "fetchChartWithRetry" "${UISRC}/components/dunjia/DunJiaCalc.js" \
     && grep -q "fetchChartWithRetry" "${UISRC}/components/taiyi/TaiYiCalc.js" \
     && grep -q "fetchChartWithRetry" "${UISRC}/components/jinkou/JinKouCalc.js" \
     && grep -q "fetchChartWithRetry" "${UISRC}/services/qizheng.js"; then
    ok "修法5 fetchChartWithRetry 接入四引擎 raw-fetch 主路径"
  else
    bad "排盘 raw-fetch 站点未全部接入 fetchChartWithRetry —— 冷启动首个排盘无重试会弹「未就绪」(修法5)"
  fi
  # SSE 必须排除重试:requestStream 函数体内不得出现重试封装(防双发/重复计费)。
  if grep -q "export async function requestStream" "${REQJS}" \
     && ! awk '/export async function requestStream/,/^}/' "${REQJS}" | grep -q "fetchWithRetryConnRefused"; then
    ok "修法5 SSE(requestStream)未接入重试(防双发/重复计费)"
  else
    bad "requestStream 疑似接入重试封装 —— SSE/AI 流绝不可重试(会双发/重复计费,红队)"
  fi
else
  warn "chartFetch.js/request.js 不存在,跳过修法5 哨兵"
fi

echo "[19] 离线判定精准性哨兵(修法6:只认 TypeError,排除超时/签名/业务错误)"
SVCSTATUS="${UISRC}/utils/serviceStatus.js"
if [ -f "${SVCSTATUS}" ]; then
  if grep -q "isBackendUnreachableError" "${SVCSTATUS}" \
     && grep -q "instanceof TypeError" "${SVCSTATUS}" \
     && grep -q "err.headers" "${SVCSTATUS}" \
     && grep -q "TimeoutError" "${SVCSTATUS}"; then
    ok "修法6 离线判定只认网络级 TypeError,排除超时/带响应头业务错误(含 signature.error)"
  else
    bad "serviceStatus.isBackendUnreachableError 判定不严 —— 可能把超时/signature.error 误判离线乱弹横幅(红队 H2)"
  fi
else
  warn "serviceStatus.js 不存在,跳过修法6 哨兵"
fi
# 20. 紫微 运限(ZiWeiLuck)/格局(ZiWeiPattern) 深度增强完整性(v2.5.8)
echo "[20] 紫微 运限/格局深度增强"
ZW_HELPER_DIR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/helper"
ZW_MODEL_DIR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/model"
ZW_FAT_JAR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
ZW_MAIN="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/ziwei/ZiWeiMain.js"
zw_src_ok=1
for f in "${ZW_MODEL_DIR}/ZiWeiLuck.java" "${ZW_MODEL_DIR}/ZiWeiPattern.java" "${ZW_HELPER_DIR}/ziweige.json" "${ZW_HELPER_DIR}/ziweiliuchangqu.json"; do
  [ -f "$f" ] || { bad "[20] 缺文件 $(basename "$f")"; zw_src_ok=0; }
done
[ "$zw_src_ok" -eq 1 ] && ok "[20] ZiWeiLuck/ZiWeiPattern + ziweige/ziweiliuchangqu 源齐全"
if grep -q "startidx - idx" "${ZW_HELPER_DIR}/ZiWeiHelper.java" 2>/dev/null; then ok "[20] getSmallDirectioinHouse 女命分支已修正(startidx - idx)"; else bad "[20] getSmallDirectioinHouse 女命分支疑似未修正(应为 startidx - idx)"; fi
if grep -q "ZWLuckPanel" "${ZW_MAIN}" 2>/dev/null && grep -q "ZWPatternPanel" "${ZW_MAIN}" 2>/dev/null; then ok "[20] ZiWeiMain 已挂 ZWLuckPanel/ZWPatternPanel"; else bad "[20] ZiWeiMain 未挂 运限/格局 TabPane"; fi
if [ -f "${ZW_FAT_JAR}" ] && command -v unzip >/dev/null 2>&1; then
  zw_cn="$(unzip -Z1 "${ZW_FAT_JAR}" 'BOOT-INF/lib/astrostudycn-*.jar' 2>/dev/null | head -1)"
  if [ -n "${zw_cn}" ]; then
    zw_list="$(cd "$(mktemp -d)" && unzip -oq "${ZW_FAT_JAR}" "${zw_cn}" 2>/dev/null && unzip -Z1 "${zw_cn}" 2>/dev/null)"
    if echo "${zw_list}" | grep -q "ZiWeiLuck.class" && echo "${zw_list}" | grep -q "ZiWeiPattern.class" && echo "${zw_list}" | grep -q "ziweige.json" && echo "${zw_list}" | grep -q "ziweiliuchangqu.json"; then
      ok "[20] fat jar 已含 ZiWeiLuck/ZiWeiPattern + ziweige/ziweiliuchangqu(gotcha #10)"
    else
      bad "[20] fat jar 缺紫微运限/格局类或数据 —— 需 astrostudycn install + astrostudyboot clean package"
    fi
  else
    warn "[20] fat jar 内未找到 astrostudycn dep jar,跳过内容校验"
  fi
else
  warn "[20] 未找到 fat jar 或无 unzip,跳过 jar 内容校验"
fi

# 20b. 紫微 全面增强 P0–P2(杂曜显示/流派四化表/格局详情/天伤天使) 完整性
echo "[20b] 紫微 全面增强 P0–P2"
ZW_HOUSE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/ziwei/ZWHouse.js"
ZW_CONST_JS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/constants/ZWConst.js"
ZW_CHART_JAVA="${ZW_MODEL_DIR}/ZiWeiChart.java"
ZW_TEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/ziwei/__tests__/ziweiEnhance.test.js"
zw2_ok=1
grep -q "drawSihuaSmallStars" "${ZW_HOUSE}" 2>/dev/null || { bad "[20b] ZWHouse 缺 drawSihuaSmallStars(十二神角格)"; zw2_ok=0; }
grep -q "starsOthersGood" "${ZW_HOUSE}" 2>/dev/null || { bad "[20b] ZWHouse 主四化盘未补显杂曜(starsOthersGood)"; zw2_ok=0; }
{ grep -q "SiHuaTables" "${ZW_CONST_JS}" && grep -q "getActiveSiHuaGan" "${ZW_CONST_JS}"; } 2>/dev/null || { bad "[20b] ZWConst 缺多流派四化表(SiHuaTables/getActiveSiHuaGan)"; zw2_ok=0; }
grep -q "setupStarsTianShangShi" "${ZW_CHART_JAVA}" 2>/dev/null || { bad "[20b] ZiWeiChart 缺天伤天使安星"; zw2_ok=0; }
{ grep -q "inOpp" "${ZW_PATTERN_JAVA:-${ZW_MODEL_DIR}/ZiWeiPattern.java}" && grep -q "sandwichHua" "${ZW_MODEL_DIR}/ZiWeiPattern.java"; } 2>/dev/null || { bad "[20b] ZiWeiPattern 缺新 op inOpp/sandwichHua"; zw2_ok=0; }
[ -f "${ZW_TEST}" ] || { bad "[20b] 缺自检 ziweiEnhance.test.js"; zw2_ok=0; }
[ "$zw2_ok" -eq 1 ] && ok "[20b] 杂曜显示/流派四化表/天伤天使/新op/自检 源齐全"
if grep -q "school: 'beipai'" "${ZW_CONST_JS}" 2>/dev/null; then ok "[20b] 四化流派默认 beipai(=现状零回归)"; else bad "[20b] 四化流派默认非 beipai —— 恐改动存量盘四化(回归风险)"; fi
if [ -f "${ZW_FAT_JAR}" ] && command -v unzip >/dev/null 2>&1; then
  zw2_cn="$(unzip -Z1 "${ZW_FAT_JAR}" 'BOOT-INF/lib/astrostudycn-*.jar' 2>/dev/null | head -1)"
  if [ -n "${zw2_cn}" ]; then
    zw2_dir="$(mktemp -d)"; ( cd "${zw2_dir}" && unzip -oq "${ZW_FAT_JAR}" "${zw2_cn}" 2>/dev/null )
    if unzip -p "${zw2_dir}/${zw2_cn}" spacex/astrostudycn/model/ZiWeiPattern.class 2>/dev/null | strings | grep -q "inOpp"; then ok "[20b] fat jar ZiWeiPattern 含新 op(inOpp)"; else bad "[20b] fat jar 未含新 op —— 需 astrostudycn install + astrostudyboot clean package"; fi
    if unzip -p "${zw2_dir}/${zw2_cn}" spacex/astrostudycn/model/ZiWeiChart.class 2>/dev/null | grep -aq "setupStarsTianShangShi"; then ok "[20b] fat jar ZiWeiChart 含天伤天使"; else bad "[20b] fat jar 未含天伤天使 —— 需重编"; fi
  fi
fi

# 21. 六壬 起课法/换将/分昼夜(纯前端 castOverride 机制,不动 Java)
echo "[21] 六壬 起课法/换将/分昼夜哨兵"
LR_MAIN="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js"
LR_COMM="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRCommChart.js"
LR_AICTX="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js"
LR_CONST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRConst.js"
if grep -q "buildLiuRengCastOverride" "${LR_MAIN}" 2>/dev/null && grep -q "function computeQiXY" "${LR_MAIN}" 2>/dev/null; then ok "[21] LiuRengMain 含起课法引擎(buildLiuRengCastOverride/computeQiXY)"; else bad "[21] LiuRengMain 缺起课法引擎"; fi
if grep -q "castOverride" "${LR_COMM}" 2>/dev/null; then ok "[21] LRCommChart 渲染侧读 castOverride(中心盘随起课法,与右栏断辞同源)"; else bad "[21] LRCommChart 未读 castOverride —— 中心盘不随起课法变,会与右栏断辞不一致"; fi
if grep -q "isDiurnalOverride" "${LR_CONST}" 2>/dev/null; then ok "[21] LRConst.getGuiZi 接受昼夜覆盖(分昼夜法)"; else bad "[21] LRConst.getGuiZi 缺昼夜覆盖参 —— 分昼夜法失效"; fi
if grep -q "castMethod: this.state.castMethod" "${LR_MAIN}" 2>/dev/null && grep -q "fenZhouYe: this.state.fenZhouYe" "${LR_MAIN}" 2>/dev/null; then ok "[21] 占案 payload 含起课法/换将/分昼夜(储存可复现)"; else bad "[21] 占案 payload 缺起课法字段 —— 存档不可复现"; fi
if grep -q "yueJiangMethod: payload.yueJiangMethod" "${LR_AICTX}" 2>/dev/null; then ok "[21] AI挂载 事盘重建透传 castOpts(挂载与显示一致)"; else bad "[21] AI挂载 六壬事盘未透传 castOpts —— 八客/选时案例会挂成默认正时正将"; fi
if grep -q "'xuanshi'" "${LR_MAIN}" 2>/dev/null && grep -q "'yanshu'" "${LR_MAIN}" 2>/dev/null && grep -q "'alnr'" "${LR_MAIN}" 2>/dev/null; then ok "[21] 起课法含 选时/演数/四柱对齐"; else bad "[21] 起课法缺 选时/演数/对齐 选项"; fi
# 次客=筹支加时(重排天地盘),勿退回只改三传;月将高亮认真实月将 actualYue;ChuangChart 必无 applyCiChou。
LR_CHUANG="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/ChuangChart.js"
if grep -q "function liurengChouBranch" "${LR_MAIN}" 2>/dev/null && grep -q "case 'cike3':" "${LR_MAIN}" 2>/dev/null; then ok "[21] 次客=筹支加时(liurengChouBranch + computeQiXY cike 分支,重排天地盘)"; else bad "[21] 次客缺筹支加时引擎 —— 退回了「只改三传」的错误实现"; fi
if grep -q "actualYue" "${LR_MAIN}" 2>/dev/null; then ok "[21] 月将/盘式高亮认真实月将 actualYue(非起课法天盘起支 X)"; else bad "[21] 缺 actualYue —— 加时/次客法的月将高亮会错显为起课法 X"; fi
if grep -q "applyCiChou" "${LR_CHUANG}" 2>/dev/null; then bad "[21] ChuangChart 残留 applyCiChou —— 次客退回「只改三传」错误实现,必删"; else ok "[21] ChuangChart 无 applyCiChou(次客在新天盘正常发用三传)"; fi
# 天地盘月将/时辰可视高亮:必须认 actualYue/realTimeBranch,不能用起课法的 X(this.yue)/Y(this.timezi) 对齐支。
LR_COMM2="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRCommChart.js"
LR_CIRCLE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRCircleChart.js"
LR_SQUARE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRTextSquareChart.js"
if grep -q "this.actualYue" "${LR_COMM2}" 2>/dev/null && grep -q "this.realTimeBranch" "${LR_COMM2}" 2>/dev/null; then ok "[21] LRCommChart 暴露 actualYue/realTimeBranch(高亮真源)"; else bad "[21] LRCommChart 缺 actualYue/realTimeBranch —— 月将/时辰高亮会落到起课法对齐支"; fi
if grep -q "highLightData: \[this.actualYue\]" "${LR_CIRCLE}" 2>/dev/null && grep -q "highLightData: \[this.realTimeBranch\]" "${LR_CIRCLE}" 2>/dev/null; then ok "[21] 圆盘高亮=真实月将(天盘)+真实时支(地盘)"; else bad "[21] 圆盘高亮仍用 this.yue(X) —— 会高亮起课法对齐的两格而非月将/时辰"; fi
{ grep -q "upBranch === this.actualYue" "${LR_SQUARE}" 2>/dev/null && grep -q "downBranch === this.realTimeBranch" "${LR_SQUARE}" 2>/dev/null; } || { bad "[21] 方盘 drawHouse 高亮仍用 this.yue/this.timezi —— 应改 actualYue/realTimeBranch"; }
# 中间盘小屏可下滑:RengChart.draw 设模式最小高度 + inline !important 撑高 svg + 读 host 视口高度。
LR_RENG="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/lrzhan/RengChart.js"
if grep -q "minChartH" "${LR_RENG}" 2>/dev/null && grep -q "setProperty('height'" "${LR_RENG}" 2>/dev/null; then ok "[21] 中间盘按模式最小高度绘制 + 撑高 svg(小屏 overflow-y 可下滑)"; else bad "[21] RengChart 缺 minChartH/撑高 svg —— 小屏方盘会裁切且无法下滑"; fi

# 24. AI 分析页 v2.5.1 复审整改不变量（起课兜底 / 卜卦择日挂载 / 六爻护栏 / 数算流年 / 导出注册 + 自检 / 城市库）
echo "[24] AI 分析页 v2.5.1 复审整改哨兵"
AIEXPORT_JS="${UISRC}/utils/aiExport.js"
PRECISE_JS="${UISRC}/utils/preciseCalcBridge.js"
HELUO_JS="${UISRC}/utils/heluoLocal.js"
AIEXPORT_TEST_JS="${UISRC}/utils/__tests__/aiExport.test.js"
# B1：fetchPreciseNongli 本地兜底须对软失败(!result)生效(出现≥2次=try+catch),不能只在 catch → 否则奇门/太乙离线缺失
precise_fb_cnt=$(awk '/export async function fetchPreciseNongli/,/^}/' "${PRECISE_JS}" 2>/dev/null | grep -c "buildLocalNongliFallback")
if [ "${precise_fb_cnt:-0}" -ge 2 ]; then ok "[24] fetchPreciseNongli 软失败也走本地兜底(B1:奇门/太乙离线不缺失)"; else bad "[24] fetchPreciseNongli 兜底疑似仍只在 catch(B1 回退风险)"; fi
# New3：卜卦盘/择日盘进白名单
if awk '/TIME_CASTABLE_DIVINATION =/' "${LR_AICTX}" 2>/dev/null | grep -q "horary" && awk '/TIME_CASTABLE_DIVINATION =/' "${LR_AICTX}" 2>/dev/null | grep -q "election"; then ok "[24] 卜卦盘/择日盘已入 TIME_CASTABLE_DIVINATION"; else bad "[24] TIME_CASTABLE_DIVINATION 缺 horary/election"; fi
# 🔒 铁律：六爻永不入时间确定白名单(否则按时间伪造卦象)
if awk '/TIME_CASTABLE_DIVINATION =/' "${LR_AICTX}" 2>/dev/null | grep -q "sixyao"; then bad "[24] 🔒 铁律破:六爻进了 TIME_CASTABLE_DIVINATION"; else ok "[24] 🔒 六爻未入时间确定白名单(护栏在)"; fi
# F：河洛快照出流年卦(调 liuNian)
if awk '/export function buildSnapshotText/,/return lines.join/' "${HELUO_JS}" 2>/dev/null | grep -q "liuNian("; then ok "[24] 河洛 buildSnapshotText 已出流年卦(调 liuNian)"; else bad "[24] 河洛快照未调 liuNian —— 仍缺整层流年卦"; fi
# F：canping/heluo 进导出注册(否则导出设置隐身+免自检)
if grep -q "key: 'canping'" "${AIEXPORT_JS}" 2>/dev/null && grep -q "key: 'heluo'" "${AIEXPORT_JS}" 2>/dev/null; then ok "[24] canping/heluo 已进 AI_EXPORT_TECHNIQUES"; else bad "[24] canping/heluo 未进 AI_EXPORT_TECHNIQUES(导出设置隐身)"; fi
# F：preset⊆AI_EXPORT_TECHNIQUES 自检断言在(堵隐身回归)
if grep -q "getAIExportPresetKeys" "${AIEXPORT_JS}" 2>/dev/null && grep -q "getAIExportPresetKeys" "${AIEXPORT_TEST_JS}" 2>/dev/null; then ok "[24] preset⊆AI_EXPORT_TECHNIQUES 自检断言在"; else bad "[24] 缺 preset⊆techniques 自检断言(canping/heluo 隐身会复发)"; fi
# atlas：全量城市库存在
if [ -f "${UISRC}/data/citiesFull.json" ]; then ok "[24] atlas 全量城市库 citiesFull.json 存在"; else bad "[24] 缺 citiesFull.json(跑 scripts/build-cities.js 生成)"; fi
# 星运页每个 TabPane key 必须在 VALID_DIRECTION_SUB_TABS,否则点该 tab 会先被 normalize 重定向到主限法(点一次跳主限法、点两次才进)
ASTRODIR_JS="${UISRC}/components/direction/AstroDirectMain.js"
PDSYNC_JS="${UISRC}/utils/primaryDirectionSync.js"
dir_tab_miss=""
for k in $(grep -oE '<TabPane tab="[^"]*" key="[^"]*"' "${ASTRODIR_JS}" 2>/dev/null | grep -oE 'key="[^"]*"' | sed 's/key="//; s/"//'); do
  grep -q "'${k}'" "${PDSYNC_JS}" 2>/dev/null || dir_tab_miss="${dir_tab_miss} ${k}"
done
[ -z "${dir_tab_miss}" ] && ok "[24] 星运页所有 TabPane key 均在 VALID_DIRECTION_SUB_TABS(点 tab 不会先跳主限法)" || bad "[24] 星运 tab 不在白名单、点击会先跳主限法,补入 primaryDirectionSync VALID 表:${dir_tab_miss}"
# AI 四同步(导出/设置/挂载/储存)完备性:migration 必须覆盖占星/星运核心,否则预设新段升级后不入老用户设置(astrochart 的 12分度/主宰链/寿命格局曾受此坑)。
if awk '/AI_EXPORT_SECTION_MIGRATION_KEYS = \[/,/\];/' "${AIEXPORT_JS}" 2>/dev/null | grep -q "'astrochart'" \
  && awk '/AI_EXPORT_SECTION_MIGRATION_KEYS = \[/,/\];/' "${AIEXPORT_JS}" 2>/dev/null | grep -q "'primarydirect'" \
  && awk '/AI_EXPORT_SECTION_MIGRATION_KEYS = \[/,/\];/' "${AIEXPORT_JS}" 2>/dev/null | grep -q "'firdaria'"; then
  ok "[24] AI导出 migration 覆盖占星/星运核心(astrochart/primarydirect/firdaria)"
else
  bad "[24] AI导出 migration 漏占星/星运核心 → 预设新段升级不入老用户设置(补进 AI_EXPORT_SECTION_MIGRATION_KEYS)"
fi
# 四同步跨系统自检断言须在(任何技法漏接 导出/设置/挂载/储存 其一即在 jest 红)
if grep -q "四同步跨系统一致性" "${AIEXPORT_TEST_JS}" 2>/dev/null; then ok "[24] AI 四同步跨系统自检断言在(导出/设置/挂载/储存)"; else bad "[24] 缺 AI 四同步跨系统自检断言"; fi

# 26. 奇门法奇门叠加层(荀爽:化解/用神/取象;纯前端,无 jar)四同步 + 引擎自检
echo "[26] 奇门法奇门叠加层(化解/用神/取象)"
DUNJIA_FACALC="${UISRC}/components/dunjia/DunJiaFaCalc.js"
DUNJIA_FADOC="${UISRC}/components/dunjia/DunJiaFaDoc.js"
DUNJIA_CALC_JS="${UISRC}/components/dunjia/DunJiaCalc.js"
if [ -f "${DUNJIA_FACALC}" ] && [ -f "${DUNJIA_FADOC}" ]; then ok "[26] DunJiaFaCalc/DunJiaFaDoc 在"; else bad "[26] 法奇门叠加层文件缺失"; fi
# 快照 8 段必须在(漏接=AI 导出/挂载/储存看不到化解·用神)
if grep -q "\[六害总览\]" "${DUNJIA_CALC_JS}" 2>/dev/null && grep -q "\[化解方案\]" "${DUNJIA_CALC_JS}" 2>/dev/null && grep -q "\[用神分论\]" "${DUNJIA_CALC_JS}" 2>/dev/null; then ok "[26] buildDunJiaSnapshotText 含法奇门段(六害/化解/用神)"; else bad "[26] 快照漏法奇门段(AI 四同步看不到化解·用神)"; fi
# 导出段表同步(漏=导出设置隐身)
if grep -q "'六害总览', '化解方案'" "${AIEXPORT_JS}" 2>/dev/null; then ok "[26] aiExport.qimen 段表含法奇门段"; else bad "[26] aiExport.qimen 段表漏法奇门段(导出设置隐身)"; fi
# 八神勾雀→虎玄归一(白虎检测两遁通用)必在
if grep -q "replace(/勾/g" "${DUNJIA_CALC_JS}" 2>/dev/null; then ok "[26] 八神勾雀→虎玄归一在(白虎检测两遁通用)"; else bad "[26] 缺勾雀→虎玄归一(阳遁白虎检测会失效)"; fi
# 神煞判语全覆盖自检 + 法奇门引擎单测在
if grep -q "神煞判语全覆盖" "${UISRC}/components/dunjia/__tests__/DunJiaFaDoc.test.js" 2>/dev/null; then ok "[26] 神煞判语全覆盖自检在"; else bad "[26] 缺神煞判语全覆盖自检"; fi
# 相关人员→生年干→八门化气大阵(命盘库选人,捕获各人生年干喂保护清单;未选则不显示该类)
if grep -q "export function birthToYearGan" "${DUNJIA_CALC_JS}" 2>/dev/null && grep -q "CHART_CATEGORY_OPTIONS" "${DUNJIA_CALC_JS}" 2>/dev/null; then ok "[26] DunJiaCalc 含 birthToYearGan(生年干)+CHART_CATEGORY_OPTIONS(命盘/事盘)"; else bad "[26] 缺 birthToYearGan/CHART_CATEGORY_OPTIONS"; fi
if grep -q "faRelatedPeople" "${DUNJIA_FACALC}" 2>/dev/null && ! grep -q "示本盘年干" "${DUNJIA_FACALC}" 2>/dev/null; then ok "[26] computeProtect 生年干来自相关人员(占位『示本盘年干』已移除)"; else bad "[26] computeProtect 仍用本盘年干占位/未读 faRelatedPeople"; fi
if grep -q "onRelatedPeopleChange" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null && grep -q "applyFaRelatedToPan" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null; then ok "[26] 相关人员多选已接线(stamp pan.faRelatedPeople→AI 四同步单源)"; else bad "[26] 相关人员多选未接线/未 stamp pan"; fi
# 命盘/事盘双库:命盘复用命盘库(localCharts)、跨技法自用,奇门设置存 payload.qimen;新增命盘表单须透传 payload(否则丢)
if grep -q "saveAsMingChart" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null && grep -q "qimen: qimenSettings" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null; then ok "[26] 命盘存 payload.qimen(复用命盘库,跨技法可用)"; else bad "[26] 命盘保存未走 payload.qimen"; fi
if grep -q "this.props.fields.payload" "${UISRC}/components/user/ChartAddFormComp.js" 2>/dev/null; then ok "[26] ChartAddFormComp 新增命盘透传 payload(修『新增命盘丢 payload』漏洞)"; else bad "[26] ChartAddFormComp 未透传 payload(奇门命盘设置会丢)"; fi
# 命盘信息完整(命盘管理完整显示):注入性别/经纬度+newCurrentChart honor;命盘保存恒弹新增抽屉(不静默原地更新)
if grep -q "gender: this.state.options" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null && grep -q "values.gender" "${UISRC}/models/user.js" 2>/dev/null; then ok "[26] 奇门命盘信息完整(注入性别/经纬度+newCurrentChart honor)"; else bad "[26] 奇门命盘信息不全(命盘管理缺性别等)"; fi
if ! grep -q "已更新该命盘的奇门设置" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null; then ok "[26] 命盘保存恒弹新增星盘抽屉(无 cid 静默原地更新)"; else bad "[26] 命盘保存仍有 cid 静默原地更新(应恒弹新增抽屉)"; fi
# AI 四同步挂载无遗漏:重算 pan 路径补 faRelatedPeople(regenerate)+computeProtect 全局兜底
if grep -q "qs.faRelatedPeople" "${UISRC}/utils/aiAnalysisContext.js" 2>/dev/null; then ok "[26] AI 挂载 regenerateQimenSnapshot 补 faRelatedPeople(四同步无遗漏)"; else bad "[26] AI 挂载重算 pan 漏 faRelatedPeople(相关人员挂载缺失)"; fi
if grep -q "__horosa_qimen_related_people" "${DUNJIA_FACALC}" 2>/dev/null; then ok "[26] computeProtect 全局兜底相关人员(覆盖未 stamp 的重算路径)"; else bad "[26] computeProtect 缺全局兜底(部分挂载路径漏相关人员)"; fi

# 25. 经纬度/时区 全半球转换 + 真太阳时/直接时间(用户验收追加)
echo "[25] 经纬度/时区转换 + timeAlg 哨兵"
ASTROHELPER_JS="${UISRC}/components/astro/AstroHelper.js"
GEO_TEST_JS="${UISRC}/components/astro/__tests__/AstroHelperGeo.test.js"
# 正向规范转换器:方向按【原始值符号】判(非 deg[0]>=0,否则 |值|<1 小负值如伦敦会判错向)
if grep -q "? 's' : 'n'" "${ASTROHELPER_JS}" 2>/dev/null && grep -q "? 'w' : 'e'" "${ASTROHELPER_JS}" 2>/dev/null; then ok "[25] convertLat/LonToStr 方向按原始值符号(修 (-1,0) 判向)"; else bad "[25] convertLat/LonToStr 方向疑似仍用 deg[0]>=0(小负值判向错)"; fi
# 反向解析:min/60(非 1.0/min)
if grep -q "min / 60" "${ASTROHELPER_JS}" 2>/dev/null; then ok "[25] convertLat/LonStrToDegree 用 min/60(修 1.0/min 致 gpsLat 偏)"; else bad "[25] 反向解析疑似仍 1.0/min(手输经纬度算出 gpsLat 偏、地图/时区偏)"; fi
# 6 手抄坐标转换无「分取负」畸形残留(西经/南纬 param error 源)
GEO_MANUAL_FILES="${UISRC}/components/user/ChartData.js ${UISRC}/components/user/CaseData.js ${UISRC}/components/comp/ChartFormData.js ${UISRC}/components/dice/DiceMain.js ${UISRC}/components/commtools/Azimuth.js ${UISRC}/components/astro/AstroDirectionForm.js"
geo_bad=""
for gf in ${GEO_MANUAL_FILES}; do grep -q "deg\[1\] = -" "$gf" 2>/dev/null && geo_bad="${geo_bad} $(basename "$gf")"; done
[ -z "${geo_bad}" ] && ok "[25] 6 手抄坐标转换无「分取负」畸形残留(西经/南纬不产 121w0-44)" || bad "[25] 仍有「分取负」畸形:${geo_bad}"
# 🔒 buildFieldObject 读 record.timeAlg(真太阳时=0/直接时间=1 不写死),否则八字快照对直接时间盘错用真太阳时校正
if grep -q "timeAlg: { value: (record.timeAlg" "${LR_AICTX}" 2>/dev/null; then ok "[25] 🔒 buildFieldObject 透传 record.timeAlg(直接时间盘不被强施真太阳时)"; else bad "[25] 🔒 buildFieldObject 疑似写死 timeAlg(canping/heluo 等对直接时间盘会错用真太阳时)"; fi
# 坐标转换自检测试存在
if [ -f "${GEO_TEST_JS}" ]; then ok "[25] AstroHelperGeo.test 全半球坐标自检在(回归门禁)"; else bad "[25] 缺 AstroHelperGeo.test"; fi

# 26. 占卜/星盘各页 changeGeo 选地点 → 时区自动校正(resolveGeoZone 单一真源,11 时刻敏感页全接入)
echo "[26] 占卜/星盘选地点时区自动校正哨兵(resolveGeoZone)"
TZUTIL_JS="${UISRC}/utils/timezone.js"
RGZ_TEST_JS="${UISRC}/utils/__tests__/timezone.resolveGeoZone.test.js"
if grep -q "export function resolveGeoZone" "${TZUTIL_JS}" 2>/dev/null; then ok "[26] timezone.js 导出 resolveGeoZone(单一真源:手改优先/坐标推断/缺日期兜底今天)"; else bad "[26] timezone.js 缺 resolveGeoZone 导出"; fi
RGZ_PAGES="components/lrzhan/LiuRengInput.js components/lrzhan/LiuRengBirthInput.js components/suzhan/SuZhanInput.js components/guazhan/GuaZhanInput.js components/dunjia/DunJiaMain.js components/taiyi/TaiYiMain.js components/sanshi/SanShiUnitedMain.js components/divination/DivinationChartShell.js components/astro/IndiaChartMain.js components/astro3d/AstroChartMain3D.js components/dice/DiceMain.js"
rgz_miss=""
for pg in ${RGZ_PAGES}; do
  f="${UISRC}/${pg}"
  grep -q "resolveGeoZone" "$f" 2>/dev/null || rgz_miss="${rgz_miss} $(basename "$pg")"
done
[ -z "${rgz_miss}" ] && ok "[26] 11 时刻敏感页 changeGeo 均接入 resolveGeoZone(六壬/六壬命课/宿占/六爻/奇门/太乙/三式/卜卦择日/印度/3D/骰子)" || bad "[26] 以下页未接入 resolveGeoZone(选地点时区不校正):${rgz_miss}"
if [ -f "${RGZ_TEST_JS}" ]; then ok "[26] resolveGeoZone 全半球自检在(回归门禁)"; else bad "[26] 缺 timezone.resolveGeoZone.test"; fi
# 重锚 date/time:占卜 changeGeo 须 clone+setZone(z) 重锚(否则改时区只动字段、瞬时仍按旧时区→真太阳时/四柱错)
REANCHOR_PAGES="components/lrzhan/LiuRengInput.js components/suzhan/SuZhanInput.js components/guazhan/GuaZhanInput.js components/lrzhan/LiuRengBirthInput.js components/taiyi/TaiYiMain.js components/dunjia/DunJiaMain.js components/sanshi/SanShiUnitedMain.js components/kinastro/KinAstroMain.js"
reanchor_miss=""
for pg in ${REANCHOR_PAGES}; do
  grep -q "setZone(z)" "${UISRC}/${pg}" 2>/dev/null || reanchor_miss="${reanchor_miss} $(basename "$pg")"
done
[ -z "${reanchor_miss}" ] && ok "[26] 占卜各页 changeGeo 重锚 date/time(setZone(z)),改时区瞬时随之偏移、实时重算正确" || bad "[26] 以下页 changeGeo 未重锚 date/time(改时区真太阳时/四柱会错):${reanchor_miss}"
# 策天 KinAstroMain(cetian)选地点已接线(原 showLocation 但无 onGeoChange→选点失效)
if grep -q "onGeoChange={this.changeGeo}" "${UISRC}/components/kinastro/KinAstroMain.js" 2>/dev/null; then ok "[26] 策天 KinAstroMain 已接 onGeoChange+changeGeo(cetian 选点生效)"; else bad "[26] 策天 KinAstroMain 缺 onGeoChange(选地点失效)"; fi
# 奇门 changeGeo 延后 requestNongli 重排(避 hook 预取竞态以旧盘覆盖)
if grep -q "_geoRecalcTimer" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null; then ok "[26] 奇门 changeGeo 延后强制重排(避竞态、改地点实时重算)在"; else bad "[26] 奇门 changeGeo 缺延后重排(改地点不重算风险)"; fi
# 六壬中间盘头部默认显真太阳时(非公历钟表时)
if grep -q "formatTrueSolarTime" "${UISRC}/components/lrzhan/RengChart.js" 2>/dev/null; then ok "[26] 六壬头部显真太阳时(formatTrueSolarTime)在"; else bad "[26] 六壬头部缺真太阳时显示(应默认显真太阳时)"; fi

# 22. 发布范围完整性（防漏合本地分支）—— **铁律**：判断「发布收敛哪些分支 / 哪些 ready」时,绝不凭记忆或部分列表,
#     必枚举所有本地分支并逐个查领先 main 的提交。v2.5.0 险些漏合 feature/ziwei-depth(紫微运限深化 + 六壬Phase4)→ 差点发出残缺版本。
echo "[22] 发布范围完整性(本地分支全枚举,防漏合)"
AHEAD_FEAT=""
while read -r b; do
  [ -n "$b" ] || continue
  n="$(git -C "${REPO_ROOT}" rev-list --count "main..${b}" 2>/dev/null || echo 0)"
  [ "${n:-0}" -gt 0 ] && AHEAD_FEAT="${AHEAD_FEAT} ${b}(+${n})"
done < <(git -C "${REPO_ROOT}" for-each-ref --format='%(refname:short)' refs/heads/ | grep -E '^feature/' || true)
if [ -n "${AHEAD_FEAT}" ]; then
  if [ "${HOROSA_KNOWN_UNMERGED:-}" = "1" ]; then
    warn "feature/* 领先 main,但已 HOROSA_KNOWN_UNMERGED=1 确认非本版:${AHEAD_FEAT}"
  else
    bad "feature/* 分支领先 main,可能漏入本版:${AHEAD_FEAT} —— 必逐个确认应否合并(漏 ziwei-depth 教训);确属未来版本则 HOROSA_KNOWN_UNMERGED=1 跳过"
  fi
else
  ok "无 feature/* 分支领先 main(本地 feature 分支均已纳入/合并)"
fi


# 27. #14（跨平台）本地回环不走系统代理 —— Mac 与 Windows 同因：启动器设 -Djava.net.useSystemProxies=true,
#     开 Clash/v2ray 时 JVM 会把 127.0.0.1/localhost 出站也塞进代理 → 代理转发回环卡顿/超时 →「本地排盘服务未就绪」。
#     修法：doCmd 对回环目标 setProxy(null) 直连；外部请求(api.openai.com 等)仍 getHttpHost 走代理。
echo "[27] #14 本地回环不走系统代理哨兵(跨平台:Mac 同步 Windows)"
HYSTRIX_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/boundless/src/main/java/boundless/net/http/HttpUriRequestHystrixCommand.java"
if [ -f "${HYSTRIX_JAVA}" ]; then
  if grep -q "isLoopbackTarget" "${HYSTRIX_JAVA}" && grep -q "setProxy(isLoopbackTarget(request) ? null :" "${HYSTRIX_JAVA}"; then
    ok "[27] doCmd 回环目标直连(isLoopbackTarget→setProxy(null)),外部请求仍走 getHttpHost(开系统代理时本地排盘不再被代理转发卡顿)"
  else
    bad "[27] HttpUriRequestHystrixCommand 缺 isLoopbackTarget 回环旁路 —— 开 Clash/v2ray 时本地排盘会被代理转发超时(Win #14 同因,跨平台);务必先补回 doCmd"
  fi
else
  warn "[27] 未找到 HttpUriRequestHystrixCommand.java(boundless 结构变动?手动核实回环旁路仍在)"
fi


# 28. 主 README 版本一致性 —— 教训:v2.5.1 首发漏更三主 README(仍停在 2.5.0,下载链接指向旧 pkg →
#     用户点了拿不到新版)。[1] 只校验 package.json/Cargo/tauri 等,不含 README,故漏网。这里补门禁。
echo "[28] 主 README 版本一致性(徽章 + 下载链接随 app 版本 lockstep)"
README_BAD=0
for rf in README.md README_EN.md README_ZH.md; do
  rp="${REPO_ROOT}/${rf}"
  if [ ! -f "${rp}" ]; then warn "[28] 缺 ${rf}"; continue; fi
  if ! grep -q "version-${VERSION}-" "${rp}"; then bad "[28] ${rf} 版本徽章不是 ${VERSION}(README 漏跟随 app 版本)"; README_BAD=1; fi
  if grep -oE "releases/download/v[0-9]+\.[0-9]+\.[0-9]+/" "${rp}" 2>/dev/null | grep -qv "releases/download/v${VERSION}/"; then bad "[28] ${rf} 有指向非 v${VERSION} 的下载链接(陈旧,用户会下到旧包)"; README_BAD=1; fi
done
[ "${README_BAD}" = "0" ] && ok "[28] 三主 README 版本徽章 + 下载链接均为 v${VERSION}"


# 29. 汉堡中点盘(双技法)哨兵 —— 字形/AI 同步/param error 护栏(2026-06-01 大改)。
echo "[29] 汉堡中点盘 双技法 + AI 段同步 + param error 护栏"
DIAL29_BAD=0
grep -q "AstroText.AstroMsg\[s.rep\]" "${UISRC}/components/germany/UranianDial.js" 2>/dev/null || { bad "[29] 折叠盘扇区字形未用 AstroMsg[名](会渲染成 emoji 彩块,须配 AstroChartFont)"; DIAL29_BAD=1; }
[ -f "${UISRC}/components/germany/UranianModulusDial.js" ] || { bad "[29] 缺 UranianModulusDial.js(多环模数盘技法丢失,用户要求两种盘并存)"; DIAL29_BAD=1; }
grep -q "'90°中点盘'" "${UISRC}/utils/aiExport.js" 2>/dev/null || { bad "[29] aiExport germany 预设缺 '90°中点盘' 段"; DIAL29_BAD=1; }
grep -q "\[90°中点盘\]" "${UISRC}/components/germany/AstroMidpoint.js" 2>/dev/null || { bad "[29] buildGermanySnapshotText 缺 [90°中点盘] 段(AI 挂载/导出/储存漏盘)"; DIAL29_BAD=1; }
grep -q "invalid_date" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py" 2>/dev/null || { bad "[29] webchartsrv 缺 NaN 日期护栏(invalid_date,param error 会复发)"; DIAL29_BAD=1; }
[ "${DIAL29_BAD}" = "0" ] && ok "[29] 中点盘双技法/字形 AstroMsg/AI 段同步/webchartsrv NaN 护栏 均在"


# 30. Windows #15：Ollama 走原生 /api/chat（num_ctx 才生效）。Java 改需重编 jar 同步 Win。
echo "[30] Ollama num_ctx：原生 /api/chat 分支(修 Windows #15)"
AIPROXY="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java"
if [ -f "${AIPROXY}" ]; then
  if grep -q "streamOllamaNative" "${AIPROXY}" && grep -q "/api/chat" "${AIPROXY}" && grep -q "ollamaNativeBase" "${AIPROXY}"; then
    ok "[30] Ollama 聊天走原生 /api/chat + options 嵌套(num_ctx 生效);其它 provider 不变"
  else
    bad "[30] AIAnalysisProxyService 缺 Ollama 原生 /api/chat 分支 —— num_ctx 会被 OpenAI 兼容口忽略、回退 4096 截断(Win #15 复发)"
  fi
else
  warn "[30] 未找到 AIAnalysisProxyService.java(结构变动?手动核实 Ollama 原生分支仍在)"
fi


# 31. 中点盘 UI 验收口径 + Ollama 嵌入 num_ctx (2026-06-02)：
#  - Δ 三角形已替换为短横线("-",仅在读数+树前;Δ 似三角,用户口径)
#  - TNP 关 → 全链路过滤(filterByTnp 在 natalPoints/buildRings 出口,而非 request 入口)
#  - 行运/SA 地点可调(renderLocOverride)
#  - saKey 持久化(UranianDialStyle.DEFAULTS+读取)
#  - Ollama embedding 走原生 /api/embed + options.num_ctx
echo "[31] 中点盘 UI 收尾验收 + Ollama 嵌入 num_ctx"
DIAL31_BAD=0
DIALMAIN="${UISRC}/components/germany/UranianDialMain.js"
if [ -f "${DIALMAIN}" ]; then
  # ① Δ 已删:UranianDialMain 不能再出现「Δ」(指针读数+中点树前)。
  if grep -q "Δ" "${DIALMAIN}"; then bad "[31] UranianDialMain 仍含 Δ(三角形)字符,须用短横线 '-'(用户验收口径)"; DIAL31_BAD=1; fi
  # ② TNP 全链路过滤(filterByTnp 出现 ≥3 次:定义 + natalPoints 出口 + buildRings 行运入口)。
  if ! grep -q "filterByTnp" "${DIALMAIN}"; then bad "[31] UranianDialMain 缺 filterByTnp(TNP 关→读数/中点树不同步隐藏,Win #15 类问题再发)"; DIAL31_BAD=1; fi
  # ③ 地点覆盖:renderLocOverride / transitLat / saLat 三件齐全。
  if ! grep -q "renderLocOverride" "${DIALMAIN}"; then bad "[31] UranianDialMain 缺 renderLocOverride(行运/SA 地点不可调)"; DIAL31_BAD=1; fi
  if ! grep -q "transitLat" "${DIALMAIN}"; then bad "[31] UranianDialMain 缺 transitLat state(地点覆盖未接线)"; DIAL31_BAD=1; fi
  # ④ "拖动定向" 废话已删(防左栏被截断)。
  if grep -q "拖动定向" "${DIALMAIN}"; then bad "[31] UranianDialMain 仍含「拖动定向」废话字样(左栏会被截断,用户验收口径)"; DIAL31_BAD=1; fi
else
  bad "[31] 缺 UranianDialMain.js"
  DIAL31_BAD=1
fi
# ⑤ saKey 入 Style DEFAULTS(刷新页面持久)。
DIALSTYLE="${UISRC}/components/germany/UranianDialStyle.js"
if [ -f "${DIALSTYLE}" ] && ! grep -q "saKey" "${DIALSTYLE}"; then
  bad "[31] UranianDialStyle 缺 saKey 字段(Naibod/1°选择不持久化、刷新即丢)"
  DIAL31_BAD=1
fi
# ⑥ Ollama embedding 原生分支(修 Win #15 嵌入子项)。
if [ -f "${AIPROXY}" ]; then
  if grep -q "embeddingsOllamaNative" "${AIPROXY}" && grep -q "/api/embed" "${AIPROXY}" && grep -q "extractOllamaEmbedVectors" "${AIPROXY}"; then
    :
  else
    bad "[31] AIAnalysisProxyService 缺 Ollama 原生 /api/embed 分支 —— 嵌入仍走兼容口、num_ctx 被忽略(Win #15 嵌入子项复发)"
    DIAL31_BAD=1
  fi
fi
[ "${DIAL31_BAD}" = "0" ] && ok "[31] 中点盘 UI(Δ→短横线/TNP全链路/地点可调/拖动定向已删/saKey 持久) + Ollama 嵌入原生口 均在"


# [32] 主限法方位+时间补全·铁律①守卫
#  - perpredict.py: _byZCoreKernel 函数指针仍在(纯公式 Alcabitius 主路径不被改名/重排)
#  - perpredict.py: CORE_PD_VIRTUAL_BODY_CORR_MODELS(ΔT 取数映射) + ΔT 注入 + 显示窗 + 宿命点闭式 在位
#  - perpredict.py: STATIC_TIME_KEY_SCALES['Ptolemy'] 严格 == 1.0(必须是数值字面量,不接受公式)
#  - perpredict.py: _PD_METHOD_REGISTRY 含 'core_alchabitius' 且默认 fallback 路径正确
#  - 540 case byte-perfect 测试存在并能跑通
echo "[32] 主限法方位+时间补全·铁律①守卫(Alcabitius+Ptolemy 字节级一致)"
PD32_BAD=0
PERPREDICT="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perpredict.py"
if [ -f "${PERPREDICT}" ]; then
  if ! grep -q "def getPrimaryDirectionByZCoreKernel" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 getPrimaryDirectionByZCoreKernel —— Alcabitius+Ptolemy 纯公式主路径被改名/移除(540 case 字节级将失效)"
    PD32_BAD=1
  fi
  if ! grep -q "CORE_PD_VIRTUAL_BODY_CORR_MODELS" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 CORE_PD_VIRTUAL_BODY_CORR_MODELS —— ΔT 校准批量取数映射表不在(_corePdDeltaTPointMap 依赖)"
    PD32_BAD=1
  fi
  if ! grep -q "_corePdDeltaTPointMap" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _corePdDeltaTPointMap —— 未来盘 ΔT 注入失效"
    PD32_BAD=1
  fi
  if ! grep -q "def _passesCoreDisplayWindow" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _passesCoreDisplayWindow —— 行星对显示窗(pre-norm 原值,|Δ|<107.5)被移除"
    PD32_BAD=1
  fi
  if ! grep -q "def _coreVertexArc" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _coreVertexArc —— 宿命点(Vertex)应星闭式被移除"
    PD32_BAD=1
  fi
  if ! grep -q "def _extendCorePdRecurrences" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _extendCorePdRecurrences —— 整圈复发/互补统一扩展被移除(180+ 互补与 3000 年多圈直达都走它)"
    PD32_BAD=1
  fi
  if ! grep -q "min(3000, int(round(float(data\['pdYears'\])))" "${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perchart.py"; then
    bad "[32] perchart.py pdYears 上限不是 3000 —— 年数选择上限回退"
    PD32_BAD=1
  fi
  # 前端 pdYears clamp 必须四处全 3000(任一回落 360 → 选 3000 在该路径被截断,LIVE 实测真踩过):
  #   AstroPrimaryDirection.normalizePdYears(表格组件) / AstroDirectMain.normalizePdYears(主限tab容器·真fetch路径)
  #   / aiAnalysisContext.normalizePdYearsValue(AI挂载·buildFieldObject) / techniqueMountSettings pdYears max
  PD_CLAMP_360=$(grep -rIl "Math.min(360, n)" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/direction/AstroDirectMain.js" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js" 2>/dev/null | wc -l | tr -d ' ')
  PD_CLAMP_3000=$(grep -rl "Math.min(3000, n)" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/direction/AstroDirectMain.js" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js" 2>/dev/null | wc -l | tr -d ' ')
  if [ "${PD_CLAMP_360}" != "0" ] || [ "${PD_CLAMP_3000}" != "2" ]; then
    bad "[32] 前端 pdYears clamp 未全 3000(残留 Math.min(360,n)=${PD_CLAMP_360} 处 / 应为 0;3000 命中=${PD_CLAMP_3000} / 应为 2)—— LIVE 实测过:任一处回落会让 3000 年在该路径被截到 360"
    PD32_BAD=1
  fi
  if ! grep -q "Math.min(3000, n)" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js"; then
    bad "[32] aiAnalysisContext.normalizePdYearsValue 上限不是 3000 —— AI 挂载路径会把 3000 截到 360"
    PD32_BAD=1
  fi
  # STATIC_TIME_KEY_SCALES['Ptolemy'] 必须严格 == 1.0 (数值字面量)
  if ! grep -qE "['\"]Ptolemy['\"]\s*:\s*1\.0" "${PERPREDICT}"; then
    bad "[32] STATIC_TIME_KEY_SCALES['Ptolemy'] 必须 == 1.0(数值字面量),不能写成公式或近似值;否则 Ptolemy 默认路径将失去字节级一致"
    PD32_BAD=1
  fi
  if ! grep -q "_PD_METHOD_REGISTRY" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _PD_METHOD_REGISTRY —— strategy 分发被回退(P0 方位法补全失效)"
    PD32_BAD=1
  fi
else
  bad "[32] 缺 perpredict.py"
  PD32_BAD=1
fi
# byte-perfect 测试存在
PD_BYTEPERFECT="${REPO_ROOT}/Horosa-Web/astropy/tests/test_pd_alcabitius_byteperfect.py"
# 金标语料现为 gzip 压缩(.ndjson.gz,test_pd_alcabitius_byteperfect.py 用 gzip.open 读);兼容旧未压缩名。
PD_GOLDEN_GZ="${REPO_ROOT}/Horosa-Web/astropy/tests/data/pd_calibration_corpus/golden_alcabitius_ptolemy_v266.ndjson.gz"
PD_GOLDEN_RAW="${REPO_ROOT}/Horosa-Web/astropy/tests/data/pd_calibration_corpus/golden_alcabitius_ptolemy_v266.ndjson"
if [ ! -f "${PD_BYTEPERFECT}" ]; then
  bad "[32] 缺 tests/test_pd_alcabitius_byteperfect.py —— byte-perfect 守卫缺失,540 case 回归无法跑"
  PD32_BAD=1
fi
if [ ! -f "${PD_GOLDEN_GZ}" ] && [ ! -f "${PD_GOLDEN_RAW}" ]; then
  bad "[32] 缺 tests/data/pd_calibration_corpus/golden_alcabitius_ptolemy_v266.ndjson(.gz) —— byte-perfect 基线缺失"
  PD32_BAD=1
fi
# 实跑 byte-perfect 子集 —— 「golden 与代码脱节(stale fixture)」事故的根因守卫。
# 仅做结构 grep 无法发现 golden 过期(v2.5.4 即因 golden 由中间态生成、从未与代码一致而带病发布,
# 且本门只查文件存在故未拦住);必须实跑确认 golden == 当前 Alcabitius+Ptolemy 输出。
# 默认前 12 case(~20s);HOROSA_PD_BYTEPERFECT_LIMIT 可调,HOROSA_PD_PREFLIGHT_SKIP_BP=1 跳过实跑。
if [ -f "${PD_BYTEPERFECT}" ] && [ "${HOROSA_PD_PREFLIGHT_SKIP_BP:-0}" != "1" ] && command -v python3 >/dev/null 2>&1; then
  PD_BP_LIMIT="${HOROSA_PD_BYTEPERFECT_LIMIT:-12}"
  PD_BP_OUT="$(cd "${REPO_ROOT}/Horosa-Web/astropy" 2>/dev/null && HOROSA_PD_BYTEPERFECT_LIMIT="${PD_BP_LIMIT}" PYTHONPATH="../flatlib-ctrad2:." python3 -m pytest tests/test_pd_alcabitius_byteperfect.py -q 2>&1)"
  if printf '%s\n' "${PD_BP_OUT}" | grep -qE "[0-9]+ passed"; then
    ok "[32] byte-perfect 实跑前 ${PD_BP_LIMIT} case 通过 —— golden 与当前代码字节级一致(防 stale fixture)"
  elif printf '%s\n' "${PD_BP_OUT}" | grep -qE "[0-9]+ failed|Error|Traceback"; then
    bad "[32] byte-perfect 实跑失败 —— Alcabitius+Ptolemy 与 golden 不一致(代码漂移或 golden 过期);末行:$(printf '%s\n' "${PD_BP_OUT}" | tail -1)"
    PD32_BAD=1
  else
    warn "[32] byte-perfect 实跑无法判定(python/依赖?),仅结构校验;末行:$(printf '%s\n' "${PD_BP_OUT}" | tail -1)"
  fi
fi
[ "${PD32_BAD}" = "0" ] && ok "[32] 铁律① Alcabitius+Ptolemy 字节级守卫 + byte-perfect 测试基线 + 子集实跑 均通过"


# [33] 主限法方位+时间补全·strategy 分发完整性 + 前端选项扩 (含铺满/盘宫制/label 收口)
#  - perchart.py: pdMethod 白名单与本仓核验集一致 + pdDirect 解析
#  - 前端 primaryDirectionSync.js: PD_SYNC_REV = 'pd_method_sync_v12' + SUPPORTED_PD_METHODS(核验集)
#  - 后端 helper.py / webchartsrv.py: PD_SYNC_REV 对齐 v10(否则新盘恒误判重算)
#  - pd_engine.py: build_directions + solar_arc_for_years(真太阳弧动态钥匙逆函数)
#  - 表格工具栏单行(无 advanced 第二行,不遮表格);TabPane 名「主限法」
#  - AstroPrimaryDirectionChart.js getTablePdTimeKey 不再强制降级 Naibod
#  - aiAnalysisContext.js 主限法 case 不再硬编码覆盖 pdMethod/pdTimeKey
echo "[33] 主限法方位+时间补全·strategy 分发 + 前端选项扩 (v10+v11)"
PD33_BAD=0
PERCHART="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perchart.py"
# 本仓方位法以逐位核验白名单为准(Alchabitius/Meridian/Porphyry/Equal)。
PD_SYNC="${UISRC}/utils/primaryDirectionSync.js"
if [ -f "${PD_SYNC}" ]; then
  if ! grep -q "pd_method_sync_v12" "${PD_SYNC}"; then
    bad "[33] primaryDirectionSync.js PD_SYNC_REV 未升到 'pd_method_sync_v12' —— 旧缓存不重算,新 方位法/世俗/顺逆/真太阳弧 不生效"
    PD33_BAD=1
  fi
  if ! grep -q "SUPPORTED_PD_METHODS" "${PD_SYNC}"; then
    bad "[33] primaryDirectionSync.js 缺 SUPPORTED_PD_METHODS 白名单"
    PD33_BAD=1
  fi
  # 核方位法须在前端白名单(否则下拉选了被 normalize 回退默认)
  for m in meridian porphyry equal_ecliptic equal_hour_circle; do
    grep -q "'${m}'" "${PD_SYNC}" || { bad "[33] primaryDirectionSync.js SUPPORTED_PD_METHODS 缺 '${m}'"; PD33_BAD=1; }
  done
fi
# v10:后端 PD_SYNC_REV 必须与前端一致(均 v10),否则每张新盘首查都误判需重算
for f in "${REPO_ROOT}/Horosa-Web/astropy/astrostudy/helper.py" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"; do
  [ -f "$f" ] && { grep -q "pd_method_sync_v12" "$f" || { bad "[33] 后端 $(basename $f) PD_SYNC_REV 未对齐到 v11(与前端不一致→新盘恒误判重算)"; PD33_BAD=1; }; }
done
# perchart 白名单含核方位法 + pdDirect 解析存在(顺逆同选)
if [ -f "${PERCHART}" ]; then
  for m in meridian porphyry equal_ecliptic equal_hour_circle; do
    grep -q "'${m}'" "${PERCHART}" || { bad "[33] perchart.py pdMethod 白名单缺 '${m}'"; PD33_BAD=1; }
  done
  grep -q "pdDirect" "${PERCHART}" || { bad "[33] perchart.py 缺 pdDirect 解析(顺向 direct,顺逆同选的前提)"; PD33_BAD=1; }
fi
# v10:pd_engine 必备(动态真太阳弧逆函数 solar_arc_for_years + 世俗数值法)
PD_ENGINE="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/pd_engine.py"
if [ -f "${PD_ENGINE}" ]; then
  grep -q "def solar_arc_for_years" "${PD_ENGINE}" || { bad "[33] pd_engine.py 缺 solar_arc_for_years(盘的真太阳弧动态钥匙,否则盘把 TrueSolarArc 当 Ptolemy)"; PD33_BAD=1; }
else
  bad "[33] 缺 pd_engine.py —— 主限法时间钥匙引擎(真太阳弧/太阳弧动态钥匙)不存在"; PD33_BAD=1
fi
# v10:主限法表格工具栏须为单行(无第二行,否则遮挡表格);tab 名为「主限法」
PD_TABLE="${UISRC}/components/astro/AstroPrimaryDirection.js"
if [ -f "${PD_TABLE}" ]; then
  grep -q "horosa-primary-direction-toolbar-advanced" "${PD_TABLE}" && { bad "[33] AstroPrimaryDirection.js 仍有第二行工具栏(advanced)—— 会遮挡表格,须并回单行"; PD33_BAD=1; }
fi
DIRECT_MAIN="${UISRC}/components/direction/AstroDirectMain.js"
if [ -f "${DIRECT_MAIN}" ] && grep -q 'tab="主/界限法"' "${DIRECT_MAIN}"; then
  bad "[33] AstroDirectMain.js 主限法 TabPane 仍名「主/界限法」,应改为「主限法」"
  PD33_BAD=1
fi
# v10 真因守卫:Java getParams 必须透传 pdDirect/pdConverse/pdAntiscia/pdTerms,否则前端传了到不了 Python
#   (ParamHashCache 键=params,缺这些 → direct/converse 同哈希命中同缓存 → 「推运方向选了没用」)
PD_CTRL="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/PredictiveController.java"
if [ -f "${PD_CTRL}" ]; then
  for p in pdDirect pdConverse pdAntiscia pdTerms; do
    grep -q "\"${p}\"" "${PD_CTRL}" || { bad "[33] PredictiveController.java getParams 未透传 '${p}' —— 前端选项到不了 Python(ParamHashCache 还会致顺逆同缓存,选了没用),须补 params.put + 重编 jar"; PD33_BAD=1; }
  done
  grep -q "pd_method_sync_v12" "${PD_CTRL}" || { bad "[33] PredictiveController.java _wireRev 未升 v11 —— 旧 ParamHashCache 哈希不失效,新参可能读到旧缓存"; PD33_BAD=1; }
fi
PD_CHART="${UISRC}/components/astro/AstroPrimaryDirectionChart.js"
if [ -f "${PD_CHART}" ] && grep -qE "key === 'Naibod' \? DEFAULT_PD_TIME_KEY" "${PD_CHART}"; then
  bad "[33] AstroPrimaryDirectionChart.getTablePdTimeKey 仍强制把 Naibod 降级为 Ptolemy —— P0 起 Naibod 应直接进表格"
  PD33_BAD=1
fi
AIANALYSISCTX="${UISRC}/utils/aiAnalysisContext.js"
if [ -f "${AIANALYSISCTX}" ] && grep -qE "pdMethod: 'core_alchabitius'," "${AIANALYSISCTX}"; then
  bad "[33] aiAnalysisContext.js 主限法 case 仍硬编码 pdMethod='core_alchabitius' —— LLM 上下文永远显示 Alchabitius、与用户实选不符"
  PD33_BAD=1
fi
# v11:主限法盘宫制随方法(_PD_CHART_METHOD_HSYS)——盘的宫头随方位法变,缺则盘恒用本命宫制(方法选了盘不动)
PERPREDICT_V11="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perpredict.py"
if [ -f "${PERPREDICT_V11}" ]; then
  grep -q "_PD_CHART_METHOD_HSYS" "${PERPREDICT_V11}" || { bad "[33] perpredict.py 缺 _PD_CHART_METHOD_HSYS —— 主限法盘宫头不随方位法变"; PD33_BAD=1; }
  grep -q "def _pdChartHouseSystem" "${PERPREDICT_V11}" || { bad "[33] perpredict.py 缺 _pdChartHouseSystem 解析器(盘宫制 fallback 本命制的入口)"; PD33_BAD=1; }
fi
# v11:方位法白名单与时间钥匙铺满——少一处下拉选了被 normalize 回退
if [ -f "${PD_SYNC}" ]; then
  for m in meridian porphyry equal_ecliptic equal_hour_circle; do
    grep -q "'${m}'" "${PD_SYNC}" || { bad "[33] primaryDirectionSync.js SUPPORTED_PD_METHODS 缺 v11 方位法 '${m}'"; PD33_BAD=1; }
  done
  for k in Naibod Cardano SelfMeasure; do
    grep -q "'${k}'" "${PD_SYNC}" || { bad "[33] primaryDirectionSync.js SUPPORTED_PD_TIME_KEYS 缺 v11 时间钥匙 '${k}'"; PD33_BAD=1; }
  done
fi
# 铁律:方位法以逐位核验白名单为准——前端两份白名单(同步层/方法下拉)与 Python 注册表
#   集合必须精确等于 [43] 的核验集;pd_engine 只保留时间钥匙与共享量度原语。
PD_TABLE_OS="${UISRC}/components/astro/AstroPrimaryDirection.js"
PDENG_OS="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/pd_engine.py"
PD33_TABLE="$(python3 - "${REPO_ROOT}" <<'PY33'
import re, sys
src = open(sys.argv[1] + '/Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js', encoding='utf-8').read()
m = re.search(r"SUPPORTED_PD_METHODS\s*=\s*\[(.*?)\]", src, re.S)
methods = sorted(re.findall(r"'([a-z_]+)'", m.group(1))) if m else []
print(','.join(methods))
PY33
)"
[ "${PD33_TABLE}" = "core_alchabitius,equal_ecliptic,equal_hour_circle,horosa_legacy,meridian,porphyry" ] || { bad "[33] 方法下拉白名单与核验集不一致: ${PD33_TABLE}"; PD33_BAD=1; }
[ -f "${PDENG_OS}" ] && grep -qE "^def arc_" "${PDENG_OS}" && { bad "[33] pd_engine.py 出现方位法闭式引擎函数(本仓只留钥匙/共享原语)"; PD33_BAD=1; }
# v11:AI 导出/挂载快照方法名必走共享 label 字典——AstroDirectMain 的 method/timeKey 文本函数不能再有 'Alchabitius' 字面回退
if [ -f "${DIRECT_MAIN}" ]; then
  grep -q "getPdMethodLabel" "${DIRECT_MAIN}" || { bad "[33] AstroDirectMain.js 未 import/使用 getPdMethodLabel —— 非默认方位法/钥匙的快照名会回退误标 Alchabitius"; PD33_BAD=1; }
  # 旧 bug 模式:primaryDirectionMethodText 内 `return 'Alchabitius'` 字面回退(非 label 字典)
  if grep -A3 "function primaryDirectionMethodText" "${DIRECT_MAIN}" | grep -q "return 'Alchabitius'"; then
    bad "[33] AstroDirectMain.primaryDirectionMethodText 仍字面回退 'Alchabitius' —— 须 delegate 到 getPdMethodLabel(非默认选项导出/挂载会被误标)"
    PD33_BAD=1
  fi
fi
# v11:主限法盘宫制自检测试存在
PD_DIAL_TEST="${REPO_ROOT}/Horosa-Web/astropy/tests/test_pd_dial_house_system.py"
[ -f "${PD_DIAL_TEST}" ] || { bad "[33] 缺 tests/test_pd_dial_house_system.py —— 盘宫制随方法的自检守卫缺失"; PD33_BAD=1; }
[ "${PD33_BAD}" = "0" ] && ok "[33] strategy 分发 + 前端白名单精确集 + 盘宫制随方法 + 共享 label 字典 + AI 上下文实选透传 均到位"


# [34] 七政四余 二十八宿度·自有恒星案三制(回归今制活体距星 / 开禧+岁差 / 郑氏恒星基值)
#  - perchart.py: MOIRA_DISTAR_J2000 (28 距星) + _moira_distar_lon + _moira_ayanamsha 在
#  - perchart.py: setPlanetSu28 支持 byLon (黄道置宿)
#  - 回归今制不再直接用冻结 15.9 当今制(必经活体距星)
#  - 回归测试存在
echo "[34] 七政四余 二十八宿度·自有恒星案三制"
GUO34_BAD=0
if [ -f "${PERCHART}" ]; then
  grep -q "MOIRA_DISTAR_J2000" "${PERCHART}" || { bad "[34] perchart.py 缺 MOIRA_DISTAR_J2000(28 距星表)—— 回归今制活体距星失效"; GUO34_BAD=1; }
  grep -q "_moira_distar_lon" "${PERCHART}" || { bad "[34] perchart.py 缺 _moira_distar_lon(距星严格岁差投射)"; GUO34_BAD=1; }
  grep -q "_moira_ayanamsha" "${PERCHART}" || { bad "[34] perchart.py 缺 _moira_ayanamsha(开禧/恒星制基准)"; GUO34_BAD=1; }
  grep -q "byLon" "${PERCHART}" || { bad "[34] perchart.py setPlanetSu28 缺 byLon(自有恒星案三制须沿黄道置宿)"; GUO34_BAD=1; }
else
  bad "[34] 缺 perchart.py"; GUO34_BAD=1
fi
GUO_TEST="${REPO_ROOT}/Horosa-Web/astropy/tests/test_guolao_su28_moira.py"
[ -f "${GUO_TEST}" ] || { bad "[34] 缺 tests/test_guolao_su28_moira.py(七政四余宿度回归)"; GUO34_BAD=1; }
[ "${GUO34_BAD}" = "0" ] && ok "[34] 七政四余 28 距星表 + 严格岁差 + 黄道置宿 + 回归测试 均在"


# [35] 启动/运行稳健化(P0):白屏兜底 + 后端就绪契约 + Java 绑 127.0.0.1 + Windows 镜像清单
#  - 前端 StartupGate(白屏兜底覆盖层)存在且挂载到 layouts/app.js
#  - webchartsrv.py: /healthz 就绪探针 + HOROSA_READY stdout 握手
#  - start_horosa_local.sh: --server.address=127.0.0.1(根治 Windows 防火墙弹窗,镜像 Windows spec)
#  - docs/windows-启动稳健化-镜像清单.md 在(给 Windows Electron 壳的镜像 spec)
echo "[35] 启动/运行稳健化(P0)"
ST35_BAD=0
ST_GATE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/StartupGate.js"
ST_APP="${REPO_ROOT}/Horosa-Web/astrostudyui/src/layouts/app.js"
ST_CHART="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
ST_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
ST_WINDOC="${REPO_ROOT}/docs/windows-启动稳健化-镜像清单.md"
[ -f "${ST_GATE}" ] || { bad "[35] 缺 StartupGate.js(白屏兜底覆盖层)"; ST35_BAD=1; }
{ [ -f "${ST_APP}" ] && grep -q "StartupGate" "${ST_APP}"; } || { bad "[35] layouts/app.js 未挂载 StartupGate —— 白屏兜底失效"; ST35_BAD=1; }
{ [ -f "${ST_CHART}" ] && grep -q "def healthz" "${ST_CHART}"; } || { bad "[35] webchartsrv.py 缺 /healthz 就绪探针"; ST35_BAD=1; }
{ [ -f "${ST_CHART}" ] && grep -q "HOROSA_READY" "${ST_CHART}"; } || { bad "[35] webchartsrv.py 缺 HOROSA_READY stdout 握手"; ST35_BAD=1; }
{ [ -f "${ST_START}" ] && grep -q "server.address=127.0.0.1" "${ST_START}"; } || { bad "[35] start_horosa_local.sh 缺 --server.address=127.0.0.1(根治防火墙弹窗)"; ST35_BAD=1; }
[ -f "${ST_WINDOC}" ] || { bad "[35] 缺 docs/windows-启动稳健化-镜像清单.md(Windows 镜像 spec)"; ST35_BAD=1; }
[ "${ST35_BAD}" = "0" ] && ok "[35] StartupGate 挂载 + /healthz + HOROSA_READY + 127.0.0.1 绑定 + Windows 镜像清单 均在"


echo "[36] 城市搜索专业化(简体显示 + 拼音/首字母 + 繁简折叠;全技法经纬度共用 GeoCoordSelector)"
CITY_BAD=0
CM_JS="${UISRC}/components/amap/cityMatch.js"
CM_TEST="${UISRC}/components/amap/__tests__/cityMatch.test.js"
CITY_FULL="${UISRC}/data/citiesFull.json"
CITY_MAP="${UISRC}/data/cityTradSimpMap.json"
CITY_SEL="${UISRC}/components/amap/GeoCoordSelector.js"
[ -f "${CM_JS}" ] || { bad "[36] 缺 cityMatch.js(城市检索纯函数,简繁/拼音核心)"; CITY_BAD=1; }
[ -f "${CM_TEST}" ] || { bad "[36] 缺 cityMatch.test.js(城市检索自检)"; CITY_BAD=1; }
[ -f "${CITY_MAP}" ] || { bad "[36] 缺 cityTradSimpMap.json(繁→简折叠表;繁体查询会失效)"; CITY_BAD=1; }
{ [ -f "${CITY_SEL}" ] && grep -q "from './cityMatch'" "${CITY_SEL}"; } || { bad "[36] GeoCoordSelector 未委托 cityMatch(搜索退回旧逻辑)"; CITY_BAD=1; }
# citiesFull 必须带拼音字段 p(中国城市可拼音搜)且已转简体;抽查北京市 + 全表无残留繁体字。
if [ -f "${CITY_FULL}" ]; then
  node -e 'const a=require(process.argv[1]);const bj=a.find(c=>c.n==="北京市");if(!bj||!bj.p||bj.p.indexOf("bei jing")<0){console.error("NO_PINYIN");process.exit(2);}const trad=a.find(c=>/[門臺廣烏齊]/.test(c.n));if(trad){console.error("STILL_TRAD:"+trad.n);process.exit(3);}' "${CITY_FULL}" 2>/dev/null \
    || { bad "[36] citiesFull.json 缺拼音字段 p 或仍含繁体名(须 npm run build:cities 重建)"; CITY_BAD=1; }
else
  bad "[36] 缺 citiesFull.json"; CITY_BAD=1
fi
# 构建依赖只能在 devDependencies(不得进运行时 bundle)。
node -e 'const p=require(process.argv[1]);if((p.dependencies||{})["pinyin-pro"]||(p.dependencies||{})["opencc-js"]){console.error("IN_DEPS");process.exit(2);}if(!(p.devDependencies||{})["pinyin-pro"]||!(p.devDependencies||{})["opencc-js"]){console.error("MISSING_DEV");process.exit(3);}' "${UISRC}/../package.json" 2>/dev/null \
  || { bad "[36] pinyin-pro/opencc-js 必须在 devDependencies(build-only),不得进 dependencies/运行时"; CITY_BAD=1; }
[ "${CITY_BAD}" = "0" ] && ok "[36] cityMatch + 折叠表 + citiesFull(简体+拼音) + GeoCoordSelector 委托 + 构建依赖隔离 均在"


# [37] 起课时间挂载 13 技法 + 5 builder opts 透传 + buildFieldObject divTime 兜底 (2026-06-08)
echo "[37] 起课时间挂载 13 技法 + builder opts 透传 + divTime 兜底"
T37_BAD=0
T37_AICTX="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js"
T37_TMS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/techniqueMountSettings.js"
T37_TMS_TEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/techniqueMountSettings.test.js"
T37_AICTX_TEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/aiAnalysisContext.test.js"
T37_TAIXUAN="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/taixuan/TaiXuanMain.js"
T37_JINGJUE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/jingjue/JingJueMain.js"
T37_WUZHAO="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/wuzhao/WuZhaoMain.js"
T37_SHENYI="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/shenyishu/ShenYiShuMain.js"
if [ -f "${T37_AICTX}" ]; then
  for k in huangji taixuan jingjue wuzhao shenyishu; do
    awk '/TIMEPOINT_CASTABLE_SET =/' "${T37_AICTX}" | grep -q "${k}" || { bad "[37] TIMEPOINT_CASTABLE_SET 缺 ${k}(下拉能选但显「缺失」)"; T37_BAD=1; }
  done
  grep -q "record.birth || record.divTime" "${T37_AICTX}" || { bad "[37] buildFieldObject 未兜底 record.divTime → timepoint 源 5 法时间出 NaN-undefined"; T37_BAD=1; }
  for k in huangji taixuan jingjue wuzhao shenyishu; do
    grep -qE "case '${k}':" "${T37_AICTX}" || { bad "[37] regenerateCaseTechniqueSnapshot 缺 case '${k}'(改 settings 不重算)"; T37_BAD=1; }
  done
fi
{ [ -f "${T37_TAIXUAN}" ] && grep -q "buildTaiXuanSnapshotForFields(fields, opts)" "${T37_TAIXUAN}"; } || { bad "[37] TaiXuanMain 缺 buildTaiXuanSnapshotForFields(fields, opts)"; T37_BAD=1; }
{ [ -f "${T37_JINGJUE}" ] && grep -q "buildJingJueSnapshotForFields(fields, opts)" "${T37_JINGJUE}"; } || { bad "[37] JingJueMain 缺 buildJingJueSnapshotForFields(fields, opts)"; T37_BAD=1; }
{ [ -f "${T37_WUZHAO}" ] && grep -q "buildWuZhaoSnapshotForFields(fields, opts)" "${T37_WUZHAO}"; } || { bad "[37] WuZhaoMain 缺 buildWuZhaoSnapshotForFields(fields, opts)"; T37_BAD=1; }
{ [ -f "${T37_SHENYI}" ] && grep -q "buildShenYiShuSnapshotForFields(fields, opts)" "${T37_SHENYI}"; } || { bad "[37] ShenYiShuMain 缺 buildShenYiShuSnapshotForFields(fields, opts)"; T37_BAD=1; }
if [ -f "${T37_TMS}" ]; then
  for k in taixuan jingjue wuzhao shenyishu; do
    grep -qE "${k}: \{ kind: 'payload'" "${T37_TMS}" || { bad "[37] techniqueMountSettings ${k} 必 kind:'payload'(sectionsOnly 不调 regenerate)"; T37_BAD=1; }
  done
fi
if [ -f "${T37_TMS_TEST}" ]; then
  awk '/SECTIONS_ONLY =/' "${T37_TMS_TEST}" | grep -q "sixyao" || { bad "[37] SECTIONS_ONLY 常量被改"; T37_BAD=1; }
fi
[ -f "${T37_AICTX_TEST}" ] && grep -q "timepoint) 必含全 13 项" "${T37_AICTX_TEST}" || { bad "[37] aiAnalysisContext.test.js 缺 13 项 timepoint 锁定断言"; T37_BAD=1; }
[ "${T37_BAD}" = "0" ] && ok "[37] timepoint 13 技法 + 4 builder opts + divTime 兜底 + 5 switch case + 4 payload schema + 测试锁 均到位"


# [38] 合盘 (AstroRelative) 端点 :9999 + 子盘交互全链路 + 黄道 Select 局部定宽 (2026-06-08)
echo "[38] 合盘端点 + 子盘交互全链路 + 黄道 Select 定宽"
R38_BAD=0
R38_REL="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/astro/AstroRelative.js"
R38_LESS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/layouts/app.less"
R38_INDEX="${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/index.js"
if [ -f "${R38_REL}" ]; then
  grep -q "Constants.ServerRoot}/modern/relative" "${R38_REL}" || { bad "[38] AstroRelative 合盘端点必走 :9999 Java"; R38_BAD=1; }
  # 检查非注释行(忽略 // 开头的历史解释注释)
  grep -vE "^\s*//" "${R38_REL}" | grep -q "resolveKentangServiceRoot" && { bad "[38] AstroRelative 残留 resolveKentangServiceRoot active 代码(:8899 不解密)"; R38_BAD=1; }
  grep -q "handleRelativeOnChange" "${R38_REL}" || { bad "[38] AstroRelative 缺 handleRelativeOnChange"; R38_BAD=1; }
  grep -q "ResizeObserver" "${R38_REL}" || { bad "[38] AstroRelative 缺 ResizeObserver(子盘下端空白真因)"; R38_BAD=1; }
fi
if [ -f "${R38_INDEX}" ]; then
  awk '/<AstroRelative/,/\/>/' "${R38_INDEX}" | grep -q "chartStyle={chartStyle}" || { bad "[38] index.js AstroRelative 缺 chartStyle 透传"; R38_BAD=1; }
  awk '/<AstroRelative/,/\/>/' "${R38_INDEX}" | grep -q "onChange={changeCond}" || { bad "[38] index.js AstroRelative 缺 onChange"; R38_BAD=1; }
fi
for f in AstroSynastry AstroMarks AstroComposite AstroTimeSpace; do
  FP="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/relative/${f}.js"
  [ -f "${FP}" ] || continue
  grep -q "hidezodiacal={1}" "${FP}" && { bad "[38] ${f} 仍有 hidezodiacal={1}(popover 空白)"; R38_BAD=1; }
  grep -q "hidehsys={1}" "${FP}" && { bad "[38] ${f} 仍有 hidehsys={1}"; R38_BAD=1; }
  awk '/function paramsToFields/,/^}/' "${FP}" | grep -q "value: param.zodiacal" && { bad "[38] ${f} paramsToFields 仍覆盖 zodiacal(左栏改了显示不变)"; R38_BAD=1; }
done
if [ -f "${R38_LESS}" ]; then
  grep -q ".horosa-relative-page .horosa-field-block .ant-select-selector" "${R38_LESS}" || { bad "[38] app.less 缺合盘局部 Select CSS"; R38_BAD=1; }
fi
[ "${R38_BAD}" = "0" ] && ok "[38] 合盘 :9999 + 5 props 透传 + handleRelativeOnChange + ResizeObserver + paramsToFields 净化 + 黄道局部定宽 均到位"


# [39] Python helper 接受数值 geo (地图选点存浮点) (2026-06-08)
echo "[39] Python helper 接受数值 geo"
GE39_BAD=0
GE39_HELP="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/helper.py"
GE39_REAL="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/jieqi/realsuntime.py"
if [ -f "${GE39_HELP}" ]; then
  grep -q "isinstance(lon," "${GE39_HELP}" || { bad "[39] helper.py 缺 isinstance(lon, ...)"; GE39_BAD=1; }
  grep -q "isinstance(lat," "${GE39_HELP}" || { bad "[39] helper.py 缺 isinstance(lat, ...)"; GE39_BAD=1; }
fi
if [ -f "${GE39_REAL}" ]; then
  grep -q "isinstance(zone," "${GE39_REAL}" || { bad "[39] realsuntime.py 缺 isinstance(zone, ...)"; GE39_BAD=1; }
fi
[ "${GE39_BAD}" = "0" ] && ok "[39] helper.py + realsuntime.py 数值 geo 容错 均在"


# [40] 本地工作文件不入库
echo "[40] 本地工作文件未入库"
S40_BAD=0
for f in AGENTS.md CLAUDE.md Horosa-Web/AGENTS.md Horosa-Web/CLAUDE.md; do
  if git -C "${REPO_ROOT}" ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    bad "[40] ${f} 被 git 跟踪(应保持本地,见 .gitignore)"; S40_BAD=1
  fi
done
[ "${S40_BAD}" = "0" ] && ok "[40] 本地工作文件未入库"


# [41] 已修缺陷模式负向门禁 (2026-06-10 算法/设置/渲染扫雷批)
# 这批模式都是实战修掉的 bug 形态,任何一处再现 = 回归(grep -a:部分源码含 emoji 会被 grep 误判二进制)。
echo "[41] 已修缺陷模式负向门禁"
R41_BAD=0
R41_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
R41_PY="${REPO_ROOT}/Horosa-Web/astropy/astrostudy"
# ① antd 按钮直挂带参 handler:点击事件会被当首参串化成 "[object Object]" 发出
grep -ran "onClick={handleSend}" "${R41_UI}" --include="*.js" >/dev/null && { bad "[41] 发送按钮直挂 onClick={handleSend} 再现(事件对象会被当文本发出)"; R41_BAD=1; }
# ② 接口家族判定写死 'openai':预设实际值是 'openai-compatible',判定永假
grep -ran "protoFamily === 'openai'" "${R41_UI}" --include="*.js" >/dev/null && { bad "[41] protoFamily === 'openai' 死分支再现(应走 isOpenAiFamily)"; R41_BAD=1; }
# ③ 列表 key 用随机串(每次渲染重挂,丢焦点/白耗)。全仓存量待清(legacy 惯用法,百余处),
#    本门禁先钉「已修文件零回归」;新文件请直接用稳定 key。
for R41_F in components/calendar/NongLi.js components/calendar/NongLiMain.js components/ziwei/ZiWeiMain.js components/deeplearn/DLFeature.js components/germany/Midpoint.js components/reader/BookReader.js components/dice/DiceMain.js; do
  grep -an "key={randomStr(" "${R41_UI}/${R41_F}" >/dev/null 2>&1 && { bad "[41] ${R41_F} 的 randomStr key 回归"; R41_BAD=1; }
done
# ④ SVG 属性拼写:stroke-dashanray 会被静默忽略
grep -ran "stroke-dashanray" "${R41_UI}" --include="*.js" >/dev/null && { bad "[41] stroke-dashanray 拼写再现(应为 stroke-dasharray)"; R41_BAD=1; }
# ⑤ 经纬度分换算公式回退:deg + 1.0/min(应为 min/60)
grep -rn "(1.0 / min)" "${R41_PY}" --include="*.py" >/dev/null && { bad "[41] 经纬度 deg+(1.0/min) 公式回退"; R41_BAD=1; }
# ⑥ 圆周距离常量回退:delta = 360 - 180
grep -ran "delta = 360 - 180" "${R41_UI}" --include="*.js" >/dev/null && { bad "[41] distanceInCircleAbs 360-180 常量回退"; R41_BAD=1; }
# ⑦ absDistance 第二窗口符号回退
grep -rn "360 - ang2 - ang1" "${R41_PY}" --include="*.py" >/dev/null && { bad "[41] absDistance 360-ang2-ang1 符号回退"; R41_BAD=1; }
[ "${R41_BAD}" = "0" ] && ok "[41] 7 类已修缺陷模式零再现"

# [42] 发布脚本 config 交接必须 TAB 分隔 (appName 含空格时空格分词会整串右移,
#      RUNTIME_ASSET 变成名字后半截 → "missing runtime archive" 假报,打包中断)
echo "[42] 发布脚本 config 交接 TAB 安全"
S42_BAD=0
for S42_F in build_desktop_release.sh verify_github_release_end_to_end.sh verify_desktop_packaging.sh; do
  S42_P="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/${S42_F}"
  [ -f "${S42_P}" ] || continue
  grep -Eq "IFS=.+ read -r APP_NAME" "${S42_P}" || { bad "[42] ${S42_F} 的 APP_NAME read 缺 IFS 限定(空格 appName 会右移)"; S42_BAD=1; }
  grep -q "sep='\\\\t'" "${S42_P}" || { bad "[42] ${S42_F} 的 python 配置打印缺 sep='\\\\t'"; S42_BAD=1; }
done
[ "${S42_BAD}" = "0" ] && ok "[42] config 交接 TAB 分隔在位"

# [43] 更新通道隔离 (2026-06-10): 本仓 app 身份/更新源四件套必须自洽,且 publish 带产物身份硬闸。
#      防两类事故: ①壳层兜底配置漂移 → 装机用户的自动更新拉错源; ②误把别处构建的产物传进本仓 release。
echo "[43] 更新通道隔离(身份四件套 + publish 硬闸)"
U43_BAD=0
U43_TAURI="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/tauri.conf.json"
U43_RC="${REPO_ROOT}/Horosa_Desktop_Installer/config/release_config.json"
U43_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
U43_PUBSH="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/publish_github_release.sh"
U43_ID="$(python3 -c "import json;print(json.load(open('${U43_TAURI}'))['identifier'])" 2>/dev/null)"
U43_PN="$(python3 -c "import json;print(json.load(open('${U43_TAURI}'))['productName'])" 2>/dev/null)"
U43_AN="$(python3 -c "import json;print(json.load(open('${U43_RC}'))['appName'])" 2>/dev/null)"
U43_RN="$(python3 -c "import json;print(json.load(open('${U43_RC}'))['repoName'])" 2>/dev/null)"
[ "${U43_ID}" = "com.horacedong.horosa" ] || { bad "[43] tauri identifier=${U43_ID} ≠ com.horacedong.horosa"; U43_BAD=1; }
[ "${U43_PN}" = "星阙" ] || { bad "[43] tauri productName=${U43_PN} ≠ 星阙"; U43_BAD=1; }
[ "${U43_AN}" = "星阙" ] || { bad "[43] release_config appName=${U43_AN} ≠ 星阙"; U43_BAD=1; }
[ "${U43_RN}" = "Horosa-Web-App-comprehensively-improved-MacOS" ] || { bad "[43] release_config repoName=${U43_RN} ≠ Horosa-Web-App-comprehensively-improved-MacOS(更新会拉错源!)"; U43_BAD=1; }
grep -q 'const APP_NAME: &str = "星阙"' "${U43_MAIN}" || { bad "[43] main.rs APP_NAME 兜底 ≠ 星阙"; U43_BAD=1; }
grep -q 'const APP_IDENTIFIER: &str = "com.horacedong.horosa"' "${U43_MAIN}" || { bad "[43] main.rs APP_IDENTIFIER 兜底 ≠ com.horacedong.horosa"; U43_BAD=1; }
grep -q 'const DEFAULT_REPO_NAME: &str = "Horosa-Web-App-comprehensively-improved-MacOS"' "${U43_MAIN}" || { bad "[43] main.rs DEFAULT_REPO_NAME 兜底漂移(配置缺失时更新会拉错源)"; U43_BAD=1; }
grep -q "更新通道隔离硬闸" "${U43_PUBSH}" || { bad "[43] publish_github_release.sh 缺产物身份硬闸"; U43_BAD=1; }
# 共享目录单源化:安装器与壳层必须同目录;runtime 须带 appName 身份戳并在安装时验明
U43_SRN="$(python3 -c "import json;print(json.load(open('${U43_RC}')).get('sharedRootName',''))" 2>/dev/null)"
[ "${U43_SRN}" = "Horosa" ] || { bad "[43] release_config sharedRootName=${U43_SRN} ≠ Horosa"; U43_BAD=1; }
U43_TPL="${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template"
grep -q "__SHARED_ROOT_NAME__" "${U43_TPL}" || { bad "[43] postinstall 模板缺 __SHARED_ROOT_NAME__ 占位"; U43_BAD=1; }
grep -q 'manifest_app.*APP_NAME' "${U43_TPL}" || { bad "[43] postinstall 缺 runtime 身份验明"; U43_BAD=1; }
grep -q "__SHARED_ROOT_NAME__" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh" || { bad "[43] build 脚本未渲染 __SHARED_ROOT_NAME__"; U43_BAD=1; }
grep -q '"appName": "\${PAYLOAD_APP_NAME}"' "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh" || { bad "[43] runtime manifest 缺 appName 身份戳"; U43_BAD=1; }
# 主限法方位法白名单精确集合(本仓=逐位核验核集;白名单之外任何名字混入即红,无需枚举黑名单)
U43_PD="$(python3 - "${REPO_ROOT}" <<'PY43'
import re, sys
src = open(sys.argv[1] + '/Horosa-Web/astrostudyui/src/utils/primaryDirectionSync.js', encoding='utf-8').read()
m = re.search(r'SUPPORTED_PD_METHODS\s*=\s*\[(.*?)\]', src, re.S)
methods = sorted(re.findall(r"'([a-z_]+)'", m.group(1))) if m else []
print(','.join(methods))
PY43
)"
[ "${U43_PD}" = "core_alchabitius,equal_ecliptic,equal_hour_circle,horosa_legacy,meridian,porphyry" ] || { bad "[43] SUPPORTED_PD_METHODS 集合漂移: ${U43_PD}"; U43_BAD=1; }
U43_REG="$(cd "${REPO_ROOT}/Horosa-Web/astropy" && python3 -c "
import re
src = open('astrostudy/perpredict.py', encoding='utf-8').read()
m = re.search(r'_PD_METHOD_REGISTRY\s*=\s*\{(.*?)\n\}', src, re.S)
keys = sorted(set(re.findall(r\"'([a-z_]+)':\", m.group(1)))) if m else []
print(','.join(keys))" 2>/dev/null)"
case "${U43_REG}" in core_alchabitius,equal_ecliptic,equal_hour_circle,horosa_legacy,meridian,porphyry) : ;; *) bad "[43] Python _PD_METHOD_REGISTRY 集合漂移: ${U43_REG}"; U43_BAD=1 ;; esac
[ "${U43_BAD}" = "0" ] && ok "[43] 身份四件套 + publish 硬闸 + 共享目录单源 + 方位法白名单精确集 在位"

# [44] 远端隔离白名单 (2026-06-10): 本仓所有 git remote URL 只允许指向本仓自身,
#      杜绝接错远端互推;publish 的 runtime 内嵌前端一致性闸也必须在位。
echo "[44] 远端隔离白名单 + runtime 内嵌前端闸"
R44_BAD=0
while IFS= read -r R44_URL; do
  case "${R44_URL}" in
    *github.com[:/]Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS*) : ;;
    *) bad "[44] 远端 URL 不在本仓白名单: ${R44_URL}"; R44_BAD=1 ;;
  esac
done <<EOF44
$(git -C "${REPO_ROOT}" remote -v | awk '{print $2}' | sort -u)
EOF44
grep -q "runtime 包内嵌前端" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/publish_github_release.sh" || { bad "[44] publish 缺 runtime 内嵌前端一致性闸"; R44_BAD=1; }
[ "${R44_BAD}" = "0" ] && ok "[44] 远端全在白名单 + runtime 前端闸在位"

# [45] 发布敏感词扫描 (2026-06-11): 工作树全部 tracked 内容 + origin/main..HEAD 每个
#      commit 树 + 全部 commit message,逐一过本地敏感词模式表(token/调试标记/工作
#      笔记词汇等,表不入库)。模式表丢失 = 视为未审,直接红(fail-closed)。
echo "[45] 发布敏感词扫描(工作树 + 未推区间)"
S45_BAD=0
S45_PAT="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/.secrecy_patterns.sh"
if [ ! -f "${S45_PAT}" ]; then
  bad "[45] 本地敏感词模式表缺失(${S45_PAT} 不入库,换机/重 clone 后须先恢复) —— 缺表=未审,不放行"
else
  # shellcheck disable=SC1090
  . "${S45_PAT}"
  S45_A_ARGS=()
  for S45_P in "${HOROSA_FORBIDDEN_A[@]}"; do S45_A_ARGS+=(-e "${S45_P}"); done
  S45_VENDOR_EXCL=":(exclude)Horosa-Web/vendor/"
  # 玄学史(xuanshi)data 永久豁免本扫描(2026-06-28 用户拍板·制度化):公有古籍编纂模块,
  #   其历史名词经人工逐条核实纯属公有典籍引用、无任何受限内容 → 整 data 目录永不入扫描。
  #   (注:本注释刻意不写具体历史名词,以免本 preflight 文件自身命中扫描。)
  S45_XUANSHI_EXCL=":(exclude)Horosa-Web/astropy/astrostudy/xuanshi/data/"
  # -a 强制文本扫描(替换原 -I:它会静默跳过被判 binary 的 unicode 密集 JS,曾致盲漏过中文禁词);
  # 真二进制资产按扩展名排除,防随机字节伪命中。
  S45_BIN_EXCL=(":(exclude)*.png" ":(exclude)*.icns" ":(exclude)*.jar" ":(exclude)*.gz" ":(exclude)*.zip" ":(exclude)*.woff" ":(exclude)*.woff2" ":(exclude)*.ttf" ":(exclude)*.ico" ":(exclude)*.jpg" ":(exclude)*.dat")
  # ① 工作树 tracked 内容(含未提交修改)
  S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -E "${S45_A_ARGS[@]}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | head -5)"
  [ -n "${S45_HITS}" ] && { bad "[45] 工作树命中敏感词:"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
  for S45_ROW in "${HOROSA_FORBIDDEN_B[@]}"; do
    S45_P="${S45_ROW%%$'\t'*}"; S45_ALLOW="${S45_ROW#*$'\t'}"
    S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -E "${S45_P}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | grep -Ev "${S45_ALLOW}" | head -5)"
    [ -n "${S45_HITS}" ] && { bad "[45] 工作树命中敏感词(豁免外): ${S45_P}"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
  done
  # ①' W 组(机器路径/PII/内部代号):仅工作树查 —— 保证最新快照干净;旧历史 + tag
  #     已公开的同类痕迹归 filter-repo 全历史改写(碰 GitHub 决策),不在此误红历史。
  if [ "${#HOROSA_FORBIDDEN_W[@]}" -gt 0 ]; then
    S45_W_ARGS=()
    for S45_P in "${HOROSA_FORBIDDEN_W[@]}"; do S45_W_ARGS+=(-e "${S45_P}"); done
    S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -F "${S45_W_ARGS[@]}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | head -5)"
    [ -n "${S45_HITS}" ] && { bad "[45] 工作树命中机器路径/PII(W 组):"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
  fi
  # ② 未推区间每个 commit 的树(防「工作树已清但历史 blob 仍带」—— 推上去即留痕)
  for S45_C in $(git -C "${REPO_ROOT}" rev-list origin/main..HEAD 2>/dev/null); do
    S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -E "${S45_A_ARGS[@]}" "${S45_C}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | head -5)"
    [ -n "${S45_HITS}" ] && { bad "[45] 未推 commit ${S45_C:0:9} 树内命中敏感词:"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
    for S45_ROW in "${HOROSA_FORBIDDEN_B[@]}"; do
      S45_P="${S45_ROW%%$'\t'*}"; S45_ALLOW="${S45_ROW#*$'\t'}"
      S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -E "${S45_P}" "${S45_C}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | grep -Ev "${S45_ALLOW}" | head -5)"
      [ -n "${S45_HITS}" ] && { bad "[45] 未推 commit ${S45_C:0:9} 命中敏感词(豁免外): ${S45_P}"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
    done
  done
  # ③ 未推区间全部 commit message
  S45_HITS="$(git -C "${REPO_ROOT}" log --format='%h %B' origin/main..HEAD 2>/dev/null | grep -E "${S45_A_ARGS[@]}" | head -5)"
  [ -n "${S45_HITS}" ] && { bad "[45] 未推 commit message 命中敏感词:"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
  [ "${S45_BAD}" = "0" ] && ok "[45] 工作树 + $(git -C "${REPO_ROOT}" rev-list --count origin/main..HEAD 2>/dev/null) 个未推 commit + message 敏感词零命中"
fi

# [46] 后端只绑回环 (2026-06-12): :9999 默认 0.0.0.0 局域网可达(AI 代理持用户 key)。双保险。
echo "[46] 后端回环绑定双保险"
S46_BAD=0
grep -q "^server.address=127.0.0.1" "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/resources/application.properties" || { bad "[46] application.properties 缺 server.address=127.0.0.1"; S46_BAD=1; }
grep -q -- "--server.address=127.0.0.1" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" || { bad "[46] start 脚本缺 --server.address=127.0.0.1"; S46_BAD=1; }
[ "${S46_BAD}" = "0" ] && ok "[46] properties + start 脚本 双双只绑 127.0.0.1"

# [47] Java component-scan 集合不漂移 (2026-06-12): spring-mvc.xml base-package = 注册真相,
#      新增包须过可达性评审(遗留死模块绝不悄然激活)。
echo "[47] Java 扫描包集合"
S47_GOT="$(python3 -c "
import re
src = open('${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/resources/conf/spring-mvc.xml', encoding='utf-8').read()
m = re.search(r'base-package=\"(.*?)\"', src, re.S)
pkgs = sorted(p.strip() for p in m.group(1).split(',') if p.strip()) if m else []
print(','.join(pkgs))" 2>/dev/null)"
S47_WANT="boundless.spring.help.controller,boundless.spring.help.springcomp,spacex.astrodeeplearn.controller,spacex.astroesp.controller,spacex.astroreader.controller,spacex.astrostudy.controller,spacex.astrostudy.service,spacex.astrostudycn.controller,spacex.basecomm.controller"
[ "${S47_GOT}" = "${S47_WANT}" ] && ok "[47] component-scan 9 包精确不漂移" || bad "[47] 扫描包集合漂移: ${S47_GOT}"

# [48] didMount 副作用必须有清理 (2026-06-12): 持续副作用(listener/interval/observer)无
#      willUnmount = SPA 反复挂卸的累积泄漏。负向门禁,新增即红。
echo "[48] 前端挂载副作用清理"
S48_HITS="$(python3 - "${REPO_ROOT}/Horosa-Web/astrostudyui/src" <<'PY48'
import os, re, sys
root = sys.argv[1]
bad = []
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in ('__tests__', 'node_modules')]
    for fn in filenames:
        if not fn.endswith('.js') or fn.endswith('.test.js'):
            continue
        path = os.path.join(dirpath, fn)
        try:
            src = open(path, encoding='utf-8').read()
        except Exception:
            continue
        m = re.search(r'componentDidMount\s*\(', src)
        if not m:
            continue
        # didMount 起到下一个同级方法名的粗块
        block = src[m.start():m.start() + 4000]
        nxt = re.search(r'\n\t(?:async )?[a-zA-Z_$][\w$]*\s*\(', block[20:])
        if nxt:
            block = block[:20 + nxt.start()]
        if re.search(r'addEventListener|setInterval|new (Resize|Mutation|Intersection)Observer', block):
            if 'componentWillUnmount' not in src:
                bad.append(os.path.relpath(path, root))
print('\n'.join(sorted(bad)))
PY48
)"
[ -z "${S48_HITS}" ] && ok "[48] didMount 持续副作用均有 willUnmount" || { bad "[48] 以下组件 didMount 注册持续副作用但无 willUnmount:"; printf '%s\n' "${S48_HITS}" >&2; }

# [49] CSP 双表面在位 (2026-06-12): 主界面经 tiny_http(main.rs),launcher 经 tauri.conf。
echo "[49] CSP 双表面"
S49_BAD=0
grep -q "Content-Security-Policy" "${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs" || { bad "[49] main.rs 静态服务器缺 CSP 头"; S49_BAD=1; }
python3 -c "
import json
c = json.load(open('${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/tauri.conf.json'))
csp = c['app']['security'].get('csp')
raise SystemExit(0 if csp and 'default-src' in csp else 1)" || { bad "[49] tauri.conf launcher CSP 为空"; S49_BAD=1; }
[ "${S49_BAD}" = "0" ] && ok "[49] 主界面 + launcher CSP 均在位"

# [50] 安装分发守卫 (2026-06-12): arm64-only + macOS 12+ gate + entitlements,缺一不可
#      (productbuild 默认 Distribution 允许 x86_64,Intel/旧 OS 用户装完即崩)。
echo "[50] 安装分发守卫"
S50_BAD=0
S50_DIST="${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/distribution.xml.template"
[ -f "${S50_DIST}" ] || { bad "[50] distribution.xml.template 缺失"; S50_BAD=1; }
grep -q 'hostArchitectures="arm64"' "${S50_DIST}" 2>/dev/null || { bad "[50] Distribution 缺 arm64-only gate"; S50_BAD=1; }
grep -q 'os-version min="12.0"' "${S50_DIST}" 2>/dev/null || { bad "[50] Distribution 缺 macOS 12+ gate"; S50_BAD=1; }
grep -q -- "--distribution" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh" || { bad "[50] build 脚本未走 --distribution"; S50_BAD=1; }
grep -q 'uname -m' "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template" || { bad "[50] postinstall 缺 arch 兜底守卫"; S50_BAD=1; }
[ -f "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/horosa.entitlements" ] || { bad "[50] entitlements 文件缺失"; S50_BAD=1; }
grep -q "horosa.entitlements" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh" || { bad "[50] build 脚本未默认挂 entitlements"; S50_BAD=1; }
[ "${S50_BAD}" = "0" ] && ok "[50] arm64+12.0 gate / postinstall 兜底 / entitlements 全在位"

# [51] 退出不阻塞 + 启动不冻结 (2026-06-12):
#      ① 退出两臂(ExitRequested/Exit)禁同步 cleanup_state/.status()(macOS Quit=terminate: 只回调
#        Exit,同步子进程=主循环停摆=not responding),必须走 detached+去重的 spawn_exit_cleanup;
#      ② 运行时脚本端口检查禁 lsof(全进程 FD 扫描遇卡死进程单次 stall 30~100s,实测),必须 netstat;
#      ③ start_runtime 的全树元数据清理必须在 !trusted_runtime 守卫下(冷缓存下遍历数十秒=卡 36%),
#        且重活前必须先发 indeterminate 进度。
echo "[51] 退出不阻塞 + 启动不冻结"
S51_BAD=0
S51_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S51_EXIT_BLOCK="$(awk '/RunEvent::ExitRequested \{ .. \} =>/,/^            _ => \{\}/' "${S51_MAIN}")"
[ -n "${S51_EXIT_BLOCK}" ] || { bad "[51] 未能定位 run loop 退出两臂(结构变了?同步更新本哨兵)"; S51_BAD=1; }
printf '%s' "${S51_EXIT_BLOCK}" | grep -q "cleanup_state(" && { bad "[51] 退出臂回归了同步 cleanup_state(会阻塞主循环)"; S51_BAD=1; }
printf '%s' "${S51_EXIT_BLOCK}" | grep -q "\.status()" && { bad "[51] 退出臂出现同步 .status()"; S51_BAD=1; }
[ "$(printf '%s' "${S51_EXIT_BLOCK}" | grep -c "spawn_exit_cleanup(app)")" -ge 2 ] || { bad "[51] 退出两臂缺 spawn_exit_cleanup"; S51_BAD=1; }
for S51_SCRIPT in "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"; do
  if grep -v '^[[:space:]]*#' "${S51_SCRIPT}" | grep -q "lsof"; then
    bad "[51] $(basename "${S51_SCRIPT}") 非注释行出现 lsof(必须 netstat 读内核表)"; S51_BAD=1
  fi
done
grep -q "netstat -anv -p tcp" "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" || { bad "[51] stop 脚本缺 netstat 端口扫描"; S51_BAD=1; }
grep -Fq 'grep -Fq "${ROOT}"' "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" || { bad "[51] stop 脚本丢了工作区守卫(会误杀第二份 checkout)"; S51_BAD=1; }
grep -q "sleep 0.1" "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" || { bad "[51] stop 脚本 0.1s 轮询丢失"; S51_BAD=1; }
grep -v '^[[:space:]]*#' "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" | grep -Eq '^[[:space:]]*sleep 1([[:space:]]|$)' && { bad "[51] stop 脚本回归整秒 sleep"; S51_BAD=1; }
grep -A1 "if !trusted_runtime {" "${S51_MAIN}" | grep -q "prepare_runtime_dir" || { bad "[51] start_runtime 的 prepare_runtime_dir 失去 !trusted_runtime 守卫(冷缓存全树遍历会卡 36%)"; S51_BAD=1; }
grep -q '正在准备启动环境' "${S51_MAIN}" || { bad "[51] start_runtime 入口缺 indeterminate 进度(重活前进度会冻在 36%)"; S51_BAD=1; }
grep -q "'lsof', '-nP'" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py" || { bad "[51] webchartsrv.py 的 lsof 回退缺 -nP(DNS 反查会超 timeout 假阴性)"; S51_BAD=1; }
# 首启稳定性 (2026-06-12 安装包卡死根治后增):
S51_PROBE_NOPROXY="$(grep -cE "curl -s --noproxy '\\*'" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" || true)"
[ "${S51_PROBE_NOPROXY}" -ge 2 ] || { bad "[51] start 脚本探测 curl 缺 --noproxy '*'(代理环境会卡首启)"; S51_BAD=1; }
grep -q "ProxyHandler({})" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" || { bad "[51] start 脚本 urllib 回退缺禁代理 opener"; S51_BAD=1; }
grep -Eq 'port_listening "\$\{CHART_PORT\}" && port_listening "\$\{BACKEND_PORT\}" *; *then' "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" && { bad "[51] 等待循环回归 netstat 端口硬闸"; S51_BAD=1; }
grep -q 'command.env_remove(proxy_var)' "${S51_MAIN}" || { bad "[51] main.rs 未在 spawn 脚本前 env_remove 代理变量"; S51_BAD=1; }
grep -q 'chmod -R a+rwX "${SHARED_ROOT}"' "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template" || { bad "[51] postinstall 缺 a+rwX"; S51_BAD=1; }
grep -q 'chmod -R a+rX "${SHARED_ROOT}"' "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template" && { bad "[51] postinstall 回归只读 a+rX"; S51_BAD=1; }
[ "${S51_BAD}" = "0" ] && ok "[51] 退出 detached+去重 / 端口检查 netstat 化 / 探测防代理 / http 直判就绪 / 共享树可写 全在位"

# [52] 占星地图 ACG 全流派:引擎 golden(validate_acg 对 swisseph 独立反验,退0)+
#      三层透传(Java AcgController 白名单是唯一闸门,漏登=前端参数静默丢)+ 前端接线。
S52_BAD=0
S52_PY="${REPO_ROOT}/Horosa-Web/astropy"
S52_ENG="${S52_PY}/astrostudy/acg/ACGraph.py"
S52_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/AcgController.java"
S52_FE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/acg/AstroAcg.js"
S52_MAP="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/acg/AcgD3Map.js"
echo "[52] 占星地图 ACG 全流派(口径/线型/坐标系/CCG/关系盘/固定星/寻宝图)"
for fn in "_aspectLines" "_eastWestLines" "_antisciaLines" "_vertexLines" "_cuspLines" "_lotsLines" "_midpointLines" "_geodeticLines" "_crossings" "_starLines" "_starParans" "_ccgLines" "findMundaneEvent" "_lsRhumb"; do
  grep -q "${fn}" "${S52_ENG}" 2>/dev/null || { bad "[52] ACGraph 缺 ${fn}"; S52_BAD=1; }
done
for p in "mode" "lsMode" "geodetic" "cuspLines" "coord" "ayanamsa" "stars" "ccgDate" "ccgMix" "relMode" "relDate"; do
  grep -q "containsParam(\"${p}\")" "${S52_JAVA}" 2>/dev/null || { bad "[52] AcgController 白名单缺 ${p}"; S52_BAD=1; }
done
grep -q "drawTreasure" "${S52_MAP}" 2>/dev/null || { bad "[52] AcgD3Map 缺寻宝图热力层"; S52_BAD=1; }
grep -q "ayanamsa:" "${S52_FE}" 2>/dev/null || { bad "[52] AstroAcg 缺参数接线"; S52_BAD=1; }
if [ "${S52_BAD}" = "0" ] && command -v python3 >/dev/null 2>&1 && [ "${HOROSA_ACG_PREFLIGHT_SKIP:-0}" != "1" ]; then
  S52_OUT="$(cd "${S52_PY}" 2>/dev/null && PYTHONPATH="../flatlib-ctrad2:." python3 astrostudy/acg/validate_acg.py 2>&1)" || {
    bad "[52] 🔴 validate_acg golden 未退0: $(printf '%s' "${S52_OUT}" | tail -2 | head -1)"; S52_BAD=1; }
  printf '%s' "${S52_OUT}" | grep -q "ACG alignment PASS" || { bad "[52] validate_acg 输出无 PASS"; S52_BAD=1; }
fi
[ "${S52_BAD}" = "0" ] && ok "[52] 占星地图 引擎golden+白名单+前端接线 在位" || bad "[52] 占星地图 护栏 有缺失"

# [53] 性能资产护栏:exploded/CDS 启动、请求去重、前端分包、pyc 预编译、启动骨架、计算缓存面。
S53_BAD=0
S53_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
S53_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh"
S53_UMIRC="${REPO_ROOT}/Horosa-Web/astrostudyui/.umirc.js"
S53_DEDUPE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/requestDedupe.js"
S53_REQ="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/request.js"
S53_EJS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/document.ejs"
S53_HELPER="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/helper/AstroHelper.java"
echo "[53] 性能资产(exploded/CDS·分包·去重·pyc·骨架屏·计算缓存面)"
grep -q "JAVA_EXPLODED_MODE" "${S53_START}" 2>/dev/null || { bad "[53] start 脚本缺 exploded 启动分支"; S53_BAD=1; }
grep -q "maybe_train_cds_background" "${S53_START}" 2>/dev/null || { bad "[53] start 脚本缺 CDS 自训练"; S53_BAD=1; }
grep -q "boot-exploded" "${S53_PKG}" 2>/dev/null || { bad "[53] 打包脚本缺 exploded 布局"; S53_BAD=1; }
grep -q "compileall" "${S53_PKG}" 2>/dev/null || { bad "[53] 打包脚本缺 pyc 预编译"; S53_BAD=1; }
grep -q "astropy/__init__.py" "${S53_PKG}" 2>/dev/null && { bad "[53] 打包脚本引用已删除的 astropy/__init__.py"; S53_BAD=1; }
grep -q "splitChunks" "${S53_UMIRC}" 2>/dev/null || { bad "[53] .umirc 缺 splitChunks 分包"; S53_BAD=1; }
grep -q "ContextReplacementPlugin" "${S53_UMIRC}" 2>/dev/null || { bad "[53] .umirc 缺 moment locale 裁剪(须 ContextReplacement 保 zh-cn)"; S53_BAD=1; }
[ -f "${S53_DEDUPE}" ] || { bad "[53] 缺 requestDedupe.js"; S53_BAD=1; }
grep -q "dedupeEligible" "${S53_REQ}" 2>/dev/null || { bad "[53] request.js 未接去重层"; S53_BAD=1; }
grep -q "predict/dice" "${S53_DEDUPE}" 2>/dev/null || { bad "[53] 去重层缺 dice 随机排除"; S53_BAD=1; }
grep -q "horosa-boot-splash" "${S53_EJS}" 2>/dev/null || { bad "[53] document.ejs 缺启动骨架"; S53_BAD=1; }
grep -q "return request(Acg, params)" "${S53_HELPER}" 2>/dev/null || { bad "[53] getAcg 未走缓存"; S53_BAD=1; }
grep -q "return requestNoCache(Dice, params)" "${S53_HELPER}" 2>/dev/null || { bad "[53] 🔴 Dice 被缓存(随机端点缓存=功能错误)"; S53_BAD=1; }
grep -q "return requestNoCache(PlanetariumState, params)" "${S53_HELPER}" 2>/dev/null || { bad "[53] 🔴 PlanetariumState 被缓存(实时端点)"; S53_BAD=1; }
[ "${S53_BAD}" = "0" ] && ok "[53] 性能资产 全在位" || bad "[53] 性能资产 有缺失"

# ============================================================================
# [54] 择日西方深化:五档流派轴 + 默认档零回归守卫 + golden 锚 + 数据完整性
#   默认(现代主流)输出与 golden 逐字一致;modern_main extraWeights 必须为空
#   (空表 = 新增分析模块不进默认总分,评分构成与既往字节不变)。
# ============================================================================
S54_BAD=0
S54_DIR="${REPO_ROOT}/Horosa-Web/astrostudyui/src/divination"
S54_WS="${S54_DIR}/election/westernSchools.js"
S54_SNAP="${S54_DIR}/election/__tests__/__snapshots__/electionGolden.test.js.snap"
echo "[54] 择日西方深化(流派轴·golden·28宿·交映)"
[ -f "${S54_WS}" ] || { bad "[54] 缺 westernSchools.js 流派真值源"; S54_BAD=1; }
for s54k in modern_main hellenistic persian renaissance modern_revival; do
	grep -q "${s54k}: {" "${S54_WS}" 2>/dev/null || { bad "[54] 流派档缺失: ${s54k}"; S54_BAD=1; }
done
awk '/modern_main: \{/,/\},/' "${S54_WS}" 2>/dev/null | grep -q "extraWeights: {}," || { bad "[54] 🔴 modern_main extraWeights 非空(默认总分构成被改=零回归破坏)"; S54_BAD=1; }
awk '/modern_main: \{/,/\},/' "${S54_WS}" 2>/dev/null | grep -q "hsys: null" || { bad "[54] modern_main 宫制联动未保持 null(默认不得改用户宫制)"; S54_BAD=1; }
[ -f "${S54_SNAP}" ] || { bad "[54] 缺 electionGolden 快照(默认输出法律)"; S54_BAD=1; }
[ -f "${S54_DIR}/election/__tests__/electionFixture.js" ] || { bad "[54] 缺 golden 固定盘 fixture"; S54_BAD=1; }
S54_MANSIONS=$(grep -c "{ n: " "${S54_DIR}/data/lunarMansions.js" 2>/dev/null || echo 0)
[ "${S54_MANSIONS}" = "28" ] || { bad "[54] lunarMansions 应 28 条,实际 ${S54_MANSIONS}"; S54_BAD=1; }
grep -q "360 / 28" "${S54_DIR}/data/lunarMansions.js" 2>/dev/null || { bad "[54] 28 宿缺 Agrippa 均分锚"; S54_BAD=1; }
S54_EGY=$(grep -oE "\[[0-9]+, [0-9]+\]" "${S54_DIR}/data/egyptianDays.js" 2>/dev/null | wc -l | tr -d ' ')
[ "${S54_EGY}" = "12" ] || { bad "[54] 埃及凶日应 12 月×2 日,实际 ${S54_EGY} 组"; S54_BAD=1; }
grep -q "tanφ·tanδ" "${S54_DIR}/engine/paransLocal.js" 2>/dev/null || { bad "[54] paransLocal 缺公式口径注释"; S54_BAD=1; }
grep -q "riseHourAngle" "${S54_DIR}/engine/paransLocal.js" 2>/dev/null || { bad "[54] paransLocal 缺升落时角"; S54_BAD=1; }
grep -q "\['sun', 10\]" "${S54_DIR}/engine/timeLords.js" 2>/dev/null || { bad "[54] Firdaria 昼表缺日10"; S54_BAD=1; }
grep -q "capricorn: 27, aquarius: 30" "${S54_DIR}/engine/timeLords.js" 2>/dev/null || { bad "[54] ZR 小年表锚缺(摩羯27/水瓶30)"; S54_BAD=1; }
grep -q "§" "${S54_DIR}/election/electionSnapshot.js" 2>/dev/null && { bad "[54] 快照文本含 § 内部章节引用"; S54_BAD=1; }
[ "${S54_BAD}" = "0" ] && ok "[54] 择日西方深化 全在位" || bad "[54] 择日西方深化 有缺失"

# ============================================================================
# [55] 性能资产·第二轮(瘦身/启动门/恒星memo/连接池/3D动态化)
# ============================================================================
S55_BAD=0
S55_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh"
S55_CHARTSRV="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
S55_SWE="${REPO_ROOT}/Horosa-Web/flatlib-ctrad2/flatlib/ephem/swe.py"
S55_HTTP="${REPO_ROOT}/Horosa-Web/astrostudysrv/boundless/src/main/java/boundless/net/http/HttpUriRequestHystrixCommand.java"
S55_IDX="${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/index.js"
echo "[55] 性能资产R2(瘦身排除表·启动门·恒星memo·连接池·3D动态化)"
grep -q "site-packages 重依赖排除表" "${S55_PKG}" 2>/dev/null || { bad "[55] 打包脚本缺重依赖排除表"; S55_BAD=1; }
grep -q "for heavy in streamlit pyarrow plotly altair pydeck" "${S55_PKG}" 2>/dev/null || { bad "[55] 排除表重依赖清单漂移(pandas 属 chunzi 真依赖不得入表)"; S55_BAD=1; }
grep -q "_ensure_streamlit_stub" "${REPO_ROOT}/Horosa-Web/astropy/websrv/kentang/kinastro_common.py" 2>/dev/null || { bad "[55] kinastro_common 缺 streamlit 桩(kentang adapter 在瘦身 runtime 会挂)"; S55_BAD=1; }
grep -E "name '\*\.pyc'" "${S55_PKG}" 2>/dev/null | grep -q "delete" && { bad "[55] 打包清理行又包含 *.pyc -delete(会删光预编译产物)"; S55_BAD=1; }
[ -f "${REPO_ROOT}/Horosa-Web/astropy/tests/test_runtime_deps_slim.py" ] || { bad "[55] 缺瘦身哨兵测试"; S55_BAD=1; }
grep -q "STARTUP_GATE" "${S55_CHARTSRV}" 2>/dev/null || { bad "[55] webchartsrv 缺启动就绪门"; S55_BAD=1; }
grep -q "HOROSA_PY_WARMUP_SYNC" "${S55_CHARTSRV}" 2>/dev/null || { bad "[55] 启动门缺同步回退 kill-switch"; S55_BAD=1; }
grep -q "_fixstarUtCached" "${S55_SWE}" 2>/dev/null || { bad "[55] flatlib 缺恒星 memo"; S55_BAD=1; }
grep -q "_sidCtxKey" "${S55_SWE}" 2>/dev/null || { bad "[55] 恒星 memo 缓存键缺 sidereal 语境"; S55_BAD=1; }
grep -q "PoolingHttpClientConnectionManager" "${S55_HTTP}" 2>/dev/null || { bad "[55] Java 出站客户端缺连接池"; S55_BAD=1; }
grep -q "AstroChartMain3D = lazyPreloadable" "${S55_IDX}" 2>/dev/null || { bad "[55] 3D 星盘未动态化(回流主包)"; S55_BAD=1; }
[ "${S55_BAD}" = "0" ] && ok "[55] 性能资产R2 全在位" || bad "[55] 性能资产R2 有缺失"

# ============================================================================
# [56] 增量更新制度(部件切分/manifest v2/发布复用/客户端分支;边界三处 lockstep)
# ============================================================================
S56_BAD=0
S56_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh"
S56_BUILD="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh"
S56_PUB="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/publish_github_release.sh"
S56_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S56_LOCK="${REPO_ROOT}/Horosa_Desktop_Installer/dist/components/components-lock.json"
echo "[56] 增量更新制度(部件化 runtime)"
# 打包端:部件段结构 + 部件名单锚(改边界必须同步 SOP 文档与本哨兵)+ 内建校验 + lock 进全量 tar
grep -q "HOROSA_BUILD_COMPONENTS" "${S56_PKG}" 2>/dev/null || { bad "[56] 打包脚本缺部件切分段"; S56_BAD=1; }
for comp in "py-runtime" "jdk-runtime" "ephe-data" "xuanshi-data" "web-app" "java-lib" "java-app"; do
  grep -q "'${comp}'" "${S56_PKG}" 2>/dev/null || { bad "[56] 部件名单缺 ${comp}(边界漂移:脚本/SOP/哨兵三处须 lockstep)"; S56_BAD=1; }
done
grep -q "component split drift" "${S56_PKG}" 2>/dev/null || { bad "[56] 打包脚本缺零遗漏零重叠内建校验"; S56_BAD=1; }
grep -q "lock 同步进 stage 根" "${S56_PKG}" 2>/dev/null || { bad "[56] components-lock 未写入全量 tar(增量本地基准会缺失)"; S56_BAD=1; }
# 发布端:manifest v2 + asset 复用
grep -q "componentsLockUrl" "${S56_BUILD}" 2>/dev/null || { bad "[56] build 脚本缺 manifest v2 部件字段"; S56_BAD=1; }
grep -q "manifest_version = 2" "${S56_BUILD}" 2>/dev/null || { bad "[56] build 脚本缺 manifestVersion 2 升级"; S56_BAD=1; }
grep -q "PYCOMPREUSE" "${S56_PUB}" 2>/dev/null || { bad "[56] publish 脚本缺跨版本 asset 复用决策"; S56_BAD=1; }
# 客户端:diff/下载/应用/回退四件套 + kill-switch
for anchor in "plan_component_diff" "download_component_updates" "apply_component_updates" "HOROSA_UPDATE_FULL_ONLY" "staged_components"; do
  grep -q "${anchor}" "${S56_MAIN}" 2>/dev/null || { bad "[56] main.rs 缺增量客户端锚 ${anchor}"; S56_BAD=1; }
done
# 产物自洽(仅当本地已构建部件时;发版构建必产):lock 结构 + 部件文件在位 + sha 实测一致
if [ -f "${S56_LOCK}" ]; then
  S56_VERIFY="$(python3 - "${S56_LOCK}" 2>&1 <<'PY74'
import hashlib, json, pathlib, sys
lock_path = pathlib.Path(sys.argv[1])
lock = json.loads(lock_path.read_text())
names = sorted(c['name'] for c in lock['components'])
expect = sorted(['py-runtime', 'jdk-runtime', 'ephe-data', 'xuanshi-data', 'web-app', 'java-lib', 'java-app'])
if names != expect:
    raise SystemExit(f'部件集合漂移: {names}')
for c in lock['components']:
    f = lock_path.parent / c['file']
    if not f.is_file():
        raise SystemExit(f"部件文件缺失: {c['file']}")
    h = hashlib.sha256()
    with open(f, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    if h.hexdigest() != c['sha256']:
        raise SystemExit(f"部件 sha 不一致: {c['name']}(lock 与实物漂移,须重跑打包)")
    if c['type'] == 'tree' and not c.get('paths'):
        raise SystemExit(f"tree 部件缺 paths: {c['name']}")
    if c['type'] == 'files' and not c.get('files'):
        raise SystemExit(f"files 部件缺 files: {c['name']}")
print('OK')
PY74
)"
  if [ "${S56_VERIFY}" = "OK" ]; then
    ok "[56] 本地部件产物自洽(7 部件 sha 全核)"
  else
    bad "[56] 部件产物自检失败: ${S56_VERIFY}"; S56_BAD=1
  fi
fi
[ "${S56_BAD}" = "0" ] && ok "[56] 增量更新制度 全在位" || bad "[56] 增量更新制度 有缺失"

# ============================================================================
# [57] 法律文档与隐私声明一致性(协议说的必须就是代码做的)
# ============================================================================
S57_BAD=0
S57_LEGAL="${REPO_ROOT}/docs/legal"
S57_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
echo "[57] 法律文档随库完整 + 声明↔代码一致"
for doc in "最终用户许可协议与服务条款.md" "隐私政策.md" "安全说明.md" "网络与数据传输说明.md" "开源与第三方组件声明.md"; do
  [ -f "${S57_LEGAL}/${doc}" ] || { bad "[57] 缺法律文档 ${doc}"; S57_BAD=1; }
done
for doc in "Terms-of-Service-and-EULA.md" "Privacy-Policy.md" "Security-Statement.md" "Network-and-Data-Transmission-Statement.md" "Open-Source-and-Third-Party-Notices.md"; do
  [ -f "${S57_LEGAL}/en/${doc}" ] || { bad "[57] 缺英文法律文档 ${doc}"; S57_BAD=1; }
done
# 占位符必须清零(对外文档不得携带待填占位)
grep -rl "〔" "${S57_LEGAL}" --include='*.md' 2>/dev/null | grep -v "README.md" | while read -r f; do bad "[57] 法律文档残留占位符: ${f}"; done
[ "$(grep -rl '〔' "${S57_LEGAL}" --include='*.md' 2>/dev/null | grep -cv 'README.md')" = "0" ] || S57_BAD=1
# 关于对话框内嵌声明 + 官方链接接线
grep -q "aboutLegal" "${S57_UI}/components/homepage/PageHeader.js" 2>/dev/null || { bad "[57] 关于对话框缺法律声明区块"; S57_BAD=1; }
grep -q "HOROSA_OFFICIAL_REPO" "${S57_UI}/components/homepage/PageHeader.js" 2>/dev/null || { bad "[57] 关于对话框缺官方渠道链接常量"; S57_BAD=1; }
# 隐私声明↔代码一致性执行锚:
#   ① 在线地图须有一次性同意闸(隐私政策 5.3 的事实基础)
grep -q "hasMapConsent" "${S57_UI}/components/amap/MapV2.js" 2>/dev/null || { bad "[57] MapV2 缺地图加载同意闸(隐私政策 5.3 将失实)"; S57_BAD=1; }
#   ② 历史 3D 模型远端域名不得回流(网络说明「不连历史域名」的执行锚)
grep -rq "chart3d\.horosa\.com" "${S57_UI}" 2>/dev/null && { bad "[57] 前端出现 chart3d 历史域名回流(网络说明将失实)"; S57_BAD=1; }
[ "${S57_BAD}" = "0" ] && ok "[57] 法律文档与一致性 全在位" || bad "[57] 法律文档与一致性 有缺失"

# ============================================================================
# [61] 风水 十三派:理气六派(八宅/玄空/三合/金锁/乾坤/紫白)+ 水法(辅星/净阴净阳)+ 玄空大卦 + 形势 + 择日
#      纯计算引擎 + 流派选择器 UI + 户型图两法(纳气盘/八卦阳宅)画布引擎零回归
# ============================================================================
S61_BAD=0
S61_FS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/fengshui"
echo "[61] 风水 十三派 引擎+流派UI+玄空进阶(替卦/城门/打劫)+深化(黄泉/拨砂/线法/九水位/门主灶/日时紫白)+新派+户型图两法零回归"
for f in fengshuiData.js liqiCore.js xuankong.js sanhe.js zibai.js qiankun.js bazhai.js jinsuo.js LiqiWorkspace.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺风水理气 ${f}"; S61_BAD=1; }
done
# 新增五派引擎(辅星/净阴净阳/玄空大卦/形势/择日)
for f in fuxing.js jingyin.js dagua.js xingshi.js zeri.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺风水新派 ${f}"; S61_BAD=1; }
done
for f in charts/LuoshuGrid.js charts/TwentyFourShanRing.js charts/EightPalaceDisk.js charts/SixtyFourGuaRing.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺风水盘面 ${f}"; S61_BAD=1; }
done
# 六派深化 + 新派核心纯函数(仅核对导出符号在位)
grep -qE "export function sanheXiangFaAll" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺三合十二向 sanheXiangFaAll"; S61_BAD=1; }
grep -qE "export function boshaWuGe" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺拨砂五格 boshaWuGe"; S61_BAD=1; }
grep -qE "export function huangquanBaYao" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺黄泉八煞 huangquanBaYao"; S61_BAD=1; }
grep -qE "export function (chuanshanAt|toudiAt|fenjinAt)" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺线法穿山透地分金"; S61_BAD=1; }
grep -qE "export function qkgbFullPositions" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺乾坤九水位 qkgbFullPositions"; S61_BAD=1; }
grep -qE "export function jianXiangByDeg" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺玄空兼向度数判别 jianXiangByDeg"; S61_BAD=1; }
grep -qE "export function gua64Of" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺玄空大卦识卦 gua64Of"; S61_BAD=1; }
grep -qE "export function guaRelation" "${S61_FS}/bazhai.js" 2>/dev/null || { bad "[61] 缺八宅门主灶 guaRelation"; S61_BAD=1; }
grep -qE "export function dayCenter" "${S61_FS}/zibai.js" 2>/dev/null || { bad "[61] 缺日紫白 dayCenter"; S61_BAD=1; }
grep -qE "export function yearGods" "${S61_FS}/zeri.js" 2>/dev/null || { bad "[61] 缺择日年神 yearGods"; S61_BAD=1; }
# 数据底座(纳甲/纳音/64卦/黄泉/三煞)
grep -qE "NAJIA_GUA|NAYIN_60|GUA64_TABLE|BA_YAO_SHA|SANSHA_BY_JU" "${S61_FS}/fengshuiData.js" 2>/dev/null || { bad "[61] 缺数据底座(纳甲/纳音/64卦/黄泉/三煞)"; S61_BAD=1; }
# 玄空进阶:替卦/替星/城门/七星打劫
grep -qE "export function flyChartTi" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺替卦 flyChartTi"; S61_BAD=1; }
grep -qE "export function tixingOf" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺替星 tixingOf"; S61_BAD=1; }
grep -qE "TIXING_VARIANTS" "${S61_FS}/fengshuiData.js" 2>/dev/null || { bad "[61] 缺替星3方案"; S61_BAD=1; }
grep -qE "function cityGate" "${S61_FS}/xuankong.js" 2>/dev/null || { bad "[61] 缺城门诀 cityGate"; S61_BAD=1; }
grep -qE "function sevenStarRob" "${S61_FS}/xuankong.js" 2>/dev/null || { bad "[61] 缺七星打劫 sevenStarRob"; S61_BAD=1; }
# 下卦默认零回归:替卦必须 opt-in(默认走 flyChart 非 flyChartTi)
grep -qE "jian \? flyChartTi" "${S61_FS}/xuankong.js" 2>/dev/null || { bad "[61] xuankong 替卦未 opt-in(下卦零回归风险)"; S61_BAD=1; }
# FengShuiMain:流派选择器 + 户型图两法画布引擎保活(理气派 display:none 零回归)
grep -qE "import FengShuiEngine" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] FengShuiMain 丢画布引擎(户型图两法回归)"; S61_BAD=1; }
grep -qE "LIQI_SET|SCHOOL_GROUPS" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] FengShuiMain 缺流派选择器"; S61_BAD=1; }
grep -qE "canvas-body" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] FengShuiMain 缺 canvas 保活(零回归)"; S61_BAD=1; }
# onVm 守:理气/新派激活时画布引擎 vm 不得覆盖当前流派快照(否则 AI 导出取到纳气盘)
grep -qE "snapshotText && !LIQI_SET.has" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] FengShuiMain onVm 缺理气快照防覆盖守(AI导出会取错派)"; S61_BAD=1; }
# 测试在位(下卦 byte 守 + 深化/新派锚 + 压测)
for t in liqiCore.test.js xuankong.test.js schools.test.js xuankongAdvanced.test.js charts.test.js fengshuiOptionMatrix.test.js fengshuiQaRound2.test.js fengshuiManualAnchor.test.js \
         sanheAugment.test.js qiankunAugment.test.js bazhaiAugment.test.js xuankongAugment.test.js zibaiAugment.test.js newSchools.test.js fengshuiStress.test.js; do
  [ -f "${S61_FS}/__tests__/${t}" ] || { bad "[61] 缺风水测试 ${t}"; S61_BAD=1; }
done
# nav 可发现十三派(理气六派 + 新派关键词)
grep -qE "key: 'fengshui'.*金锁玉关.*乾坤国宝" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/index.js" 2>/dev/null || { bad "[61] nav 缺理气六派关键词"; S61_BAD=1; }
grep -qE "key: 'fengshui'.*玄空大卦.*形势.*择日" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/index.js" 2>/dev/null || { bad "[61] nav 缺新派关键词(大卦/形势/择日)"; S61_BAD=1; }
[ "${S61_BAD}" = "0" ] && ok "[61] 风水 十三派 引擎+玄空进阶(替卦/城门/打劫)+深化(黄泉/拨砂/线法/九水位/门主灶/日时紫白)+新派(辅星/净阴净阳/大卦/形势/择日)+盘面+测试+户型图两法零回归 在位" || bad "[61] 风水 有缺失"


# 79. 打包产物全路由冒烟已跑且绿(哈希绑定,防拿旧包结果充数)
echo "[79] 全路由真实冒烟 stamp(哈希绑定)"
S79_STAMP="${INSTALLER_ROOT}/build/runtime-smoke/last_smoke.json"
S79_ASSET="$(python3 -c "import json;print(json.load(open('${INSTALLER_ROOT}/config/release_config.json')).get('runtimeAssetName','horosa-runtime-macos-arm64.tar.gz'))" 2>/dev/null || echo horosa-runtime-macos-arm64.tar.gz)"
S79_ARCHIVE="${INSTALLER_ROOT}/dist/${S79_ASSET}"
if [ ! -f "${S79_ARCHIVE}" ]; then
  warn "[79] dist 无运行时归档(${S79_ASSET}),冒烟 stamp 校验跳过(构建后会强制)"
elif [ ! -f "${S79_STAMP}" ]; then
  bad "[79] 缺 build/runtime-smoke/last_smoke.json —— 先跑 scripts/verify_runtime_smoke.sh"
else
  S79_RES="$(python3 - "$S79_STAMP" "$S79_ARCHIVE" <<'PY'
import hashlib, json, sys
stamp = json.load(open(sys.argv[1], encoding="utf-8"))
sha = hashlib.sha256(open(sys.argv[2], "rb").read()).hexdigest()
if not stamp.get("pass"):
    print("stamp=FAIL")
elif stamp.get("runtimeSha256") != sha:
    print("sha-mismatch stamp=%s dist=%s" % (str(stamp.get("runtimeSha256"))[:16], sha[:16]))
else:
    print("ok")
PY
)"
  if [ "${S79_RES}" = "ok" ]; then
    ok "[79] 冒烟 stamp PASS 且 sha 与 dist 归档一致"
  else
    bad "[79] 冒烟 stamp 无效(${S79_RES}):对当前归档重跑 verify_runtime_smoke.sh"
  fi
fi
grep -q "runtime-smoke" "${INSTALLER_ROOT}/SELFCHECK_LOG.md" 2>/dev/null \
  && ok "[79] SELFCHECK_LOG 有冒烟留档行" \
  || warn "[79] SELFCHECK_LOG 尚无冒烟留档(首次构建后自动追加)"

# 80. 路由挂载 ↔ 冒烟探针清单 漂移=0(挂载无探针/探针无挂载 皆 FAIL)
echo "[80] 路由挂载↔探针清单漂移"
if python3 "${INSTALLER_ROOT}/scripts/check_route_probe_drift.py" >/dev/null 2>&1; then
  ok "[80] 挂载↔探针 双向一致(含 kinastro importer 覆盖名单)"
else
  python3 "${INSTALLER_ROOT}/scripts/check_route_probe_drift.py" 2>&1 | sed 's/^/    /' >&2 || true
  bad "[80] 挂载↔探针漂移:新增技法漏配探针或僵尸探针(详见上)"
fi

# 81. 太乙静默404三层守卫在位(FL-20260704-1;grep 特征串,不用文件存在性)
echo "[81] 太乙静默404三层守卫"
S81_BAD=0
S81_PY="${REPO_ROOT}/Horosa-Web/astropy"
grep -q "stub_dunder_guard_v1" "${S81_PY}/websrv/kentang/kinastro_common.py" 2>/dev/null || { bad "[81] 桩 dunder 守卫(stub_dunder_guard_v1)缺位"; S81_BAD=1; }
grep -q 'raise AttributeError(_name)' "${S81_PY}/websrv/kentang/kinastro_common.py" 2>/dev/null || { bad "[81] 桩 dunder 拒答语句缺位"; S81_BAD=1; }
[ "$(grep -c "__horosa_slim_stub__ = True" "${S81_PY}/websrv/kentang/kinastro_common.py" 2>/dev/null)" -ge 3 ] || { bad "[81] 子桩哨兵标记不足三处(顶桩+components+v1)"; S81_BAD=1; }
grep -q "class KentangServiceLoadError" "${S81_PY}/websrv/kentang/registry.py" 2>/dev/null || { bad "[81] registry 缺 KentangServiceLoadError 响亮失败类型"; S81_BAD=1; }
grep -q "KENTANG_LAZY_MOUNT_SELF_HEAL" "${S81_PY}/websrv/kentang/registry.py" 2>/dev/null || { bad "[81] registry 缺 sys.modules 自愈净化守卫"; S81_BAD=1; }
grep -q "_warm_real_astropy" "${S81_PY}/websrv/webchartsrv.py" 2>/dev/null || { bad "[81] webchartsrv 缺真 astropy 预热(顺序免疫层)"; S81_BAD=1; }
grep -q "stub_first" "${S81_PY}/tests/test_kentang_import_order.py" 2>/dev/null || { bad "[81] 双向导入门测试缺位/缺 stub_first 方向"; S81_BAD=1; }
[ "${S81_BAD}" = "0" ] && ok "[81] 三层守卫+双向导入门 全在位"

# 83. 更新链下载/解压核(WS-1b/1c):续传协议+原生流式解压+kill-switch+回归测试+Range 发布哨兵
echo "[83] 断点续传下载核+原生流式解压"
S83_BAD=0
S83_MAIN="${INSTALLER_ROOT}/src-tauri/src/main.rs"
grep -q "fn download_resumable_once" "${S83_MAIN}" 2>/dev/null || { bad "[83] 下载核 download_resumable_once 缺位"; S83_BAD=1; }
grep -q "HOROSA_DOWNLOAD_NO_RESUME" "${S83_MAIN}" 2>/dev/null || { bad "[83] kill-switch HOROSA_DOWNLOAD_NO_RESUME 缺位"; S83_BAD=1; }
grep -q "RESUME_MAX_ATTEMPTS" "${S83_MAIN}" 2>/dev/null || { bad "[83] 续传次数封顶 RESUME_MAX_ATTEMPTS 缺位"; S83_BAD=1; }
grep -q '\.part\.meta' "${S83_MAIN}" 2>/dev/null || { bad "[83] .part.meta 续传元数据协议缺位"; S83_BAD=1; }
grep -q "resume_completes_via_range_206" "${S83_MAIN}" 2>/dev/null || { bad "[83] 续传 206 回归测试缺位"; S83_BAD=1; }
grep -q 'r 0-1023' "${INSTALLER_ROOT}/scripts/verify_github_release_end_to_end.sh" 2>/dev/null || { bad "[83] e2e 缺 GitHub Range(206)发布实测哨兵"; S83_BAD=1; }
grep -q "fn extract_tar_gz_native_with" "${S83_MAIN}" 2>/dev/null || { bad "[83] 原生流式解压 extract_tar_gz_native_with 缺位"; S83_BAD=1; }
grep -q "HOROSA_EXTRACT_NATIVE" "${S83_MAIN}" 2>/dev/null || { bad "[83] kill-switch HOROSA_EXTRACT_NATIVE 缺位"; S83_BAD=1; }
grep -q "HOROSA_EXTRACT_CONCURRENCY" "${S83_MAIN}" 2>/dev/null || { bad "[83] 物化并发开关 HOROSA_EXTRACT_CONCURRENCY 缺位"; S83_BAD=1; }
grep -q "native_extract_parity_with_external_tar" "${S83_MAIN}" 2>/dev/null || { bad "[83] 解压 parity 回归测试缺位"; S83_BAD=1; }
grep -q "native_extract_rejects_path_escape" "${S83_MAIN}" 2>/dev/null || { bad "[83] 解压路径逃逸防护测试缺位"; S83_BAD=1; }
grep -q "tar_extract_external" "${S83_MAIN}" 2>/dev/null || { bad "[83] 外部 tar 回退路径缺位(native 出错须可退)"; S83_BAD=1; }
[ "${S83_BAD}" = "0" ] && ok "[83] 下载核+解压核 协议/开关/测试/发布哨兵 全在位"

echo "[84] 更新验证基建(事件镜像+假release隔离)"
# (manifest 分离签名机制已整体移除;本节保留事件镜像与假 release 入口隔离锚,
#  并以反向锚确保签名代码不以「半拆」状态残留。)
S84_BAD=0
S84_MAIN="${INSTALLER_ROOT}/src-tauri/src/main.rs"
grep -q "fn log_updater_event" "${S84_MAIN}" 2>/dev/null || { bad "[84] updater 事件镜像 log_updater_event 缺位(用户更新出问题拿不到证据)"; S84_BAD=1; }
grep -q "updater-events.log" "${S84_MAIN}" 2>/dev/null || { bad "[84] 事件镜像日志文件锚缺位"; S84_BAD=1; }
grep -q 'feature = "update-url-override"' "${S84_MAIN}" 2>/dev/null || { bad "[84] URL override 未按 feature 隔离"; S84_BAD=1; }
if grep -q "update-url-override" "${INSTALLER_ROOT}/scripts/build_desktop_release.sh" 2>/dev/null; then
  bad "[84] 发布构建脚本出现 update-url-override(假 release 入口绝不可进发布二进制)"; S84_BAD=1
fi
grep -q "manifest_fetch_three_outcomes" "${S84_MAIN}" 2>/dev/null || { bad "[84] manifest 获取三态回归测试缺位"; S84_BAD=1; }
# 反向锚:签名制度已取消,残留即「半拆」状态(比有或无都危险)
for zombie in "UPDATE_MANIFEST_PUBKEY_HEX" "verify_manifest_signature" "HOROSA_UPDATE_REQUIRE_SIG" "ed25519"; do
  if grep -qi "${zombie}" "${S84_MAIN}" 2>/dev/null; then
    bad "[84] 签名制度已取消但 main.rs 残留 ${zombie}(半拆状态,拆干净或整体恢复)"; S84_BAD=1
  fi
done
grep -q "horosa-update-manifest-sign" "${INSTALLER_ROOT}/scripts/build_desktop_release.sh" 2>/dev/null && { bad "[84] build 脚本残留签名段(制度已取消)"; S84_BAD=1; }
[ "${S84_BAD}" = "0" ] && ok "[84] 事件镜像+假release隔离 全在位(签名制度已取消且拆净)"

# 85. 启动健康看门狗(WS-1d,A/B 自愈):状态机/回滚/ready 确认/回归测试全在位
echo "[85] 启动健康看门狗"
S85_BAD=0
grep -q "WATCHDOG_ROLLBACK_THRESHOLD" "${S84_MAIN}" 2>/dev/null || { bad "[85] 看门狗阈值缺位"; S85_BAD=1; }
grep -q "fn rollback_runtime_to_previous" "${S84_MAIN}" 2>/dev/null || { bad "[85] previous 槽回滚函数缺位"; S85_BAD=1; }
grep -q "launch_health_confirm" "${S84_MAIN}" 2>/dev/null || { bad "[85] ready 确认(pending 归零)缺位"; S85_BAD=1; }
grep -q "cleanup_previous_slots" "${S84_MAIN}" 2>/dev/null || { bad "[85] previous 槽 ready 后回收缺位"; S85_BAD=1; }
grep -q "watchdog_health_state_machine_and_rollback" "${S84_MAIN}" 2>/dev/null || { bad "[85] 看门狗回归测试缺位"; S85_BAD=1; }
[ "${S85_BAD}" = "0" ] && ok "[85] 看门狗 状态机/回滚/确认/测试 全在位"

# 86. 增量八不变量(WS-1e):I3 三方 sha/I5 全量回退字段/I7 尺寸真值/I8 kill-switch 矩阵
#     (I1 合成校验+I2 边界 lockstep+I6 lock 进 tar 由[74]强制;I4 差分门在 publish 内)
echo "[86] 增量八不变量(I3/I5/I7/I8)"
S86_BAD=0
S86_MAIN="${INSTALLER_ROOT}/src-tauri/src/main.rs"
# I8:四个 kill-switch + I4 门锚静态在位
for anchor in "HOROSA_UPDATE_FULL_ONLY" "HOROSA_DOWNLOAD_NO_RESUME" "HOROSA_EXTRACT_NATIVE" "HOROSA_MENU_UPDATE_LEGACY"; do
  grep -q "${anchor}" "${S86_MAIN}" 2>/dev/null || { bad "[86·I8] kill-switch ${anchor} 缺位"; S86_BAD=1; }
done
grep -q "HOROSA_ALLOW_LARGE_DELTA" "${INSTALLER_ROOT}/scripts/publish_github_release.sh" 2>/dev/null || { bad "[86·I4] publish 缺差分效率门"; S86_BAD=1; }
grep -q "HOROSA_DELTA_BUDGET_MB" "${INSTALLER_ROOT}/scripts/publish_github_release.sh" 2>/dev/null || { bad "[86·I4] 差分门缺预算参数"; S86_BAD=1; }
# I3/I5/I7:dist manifest 已产时做真值核对(manifest↔lock 逐名 sha / v1 全字段 / 尺寸↔实物)
S86_MANIFEST="${INSTALLER_ROOT}/dist/horosa-latest.json"
if [ -f "${S86_MANIFEST}" ]; then
  S86_RES="$(python3 - "${S86_MANIFEST}" "${INSTALLER_ROOT}/dist" <<'PY86'
import json, pathlib, sys
manifest = json.loads(pathlib.Path(sys.argv[1]).read_text())
dist = pathlib.Path(sys.argv[2])
problems = []
for key, entry in (manifest.get('platforms') or {}).items():
    # I5:v2 必含 v1 全量回退字段(老壳/降级路径的生命线)
    for field in ('appUrl', 'appSha256', 'runtimeUrl', 'runtimeSha256', 'runtimeVersion'):
        if not entry.get(field):
            problems.append(f"I5:{key} 缺 {field}")
    # I7:尺寸字段完备且与 dist 实物一致(检查更新「要下多大」的真值)
    for field, fname in (
        ('appSizeBytes', entry.get('appUrl', '').rsplit('/', 1)[-1]),
        ('runtimeSizeBytes', entry.get('runtimeUrl', '').rsplit('/', 1)[-1]),
    ):
        declared = entry.get(field)
        if declared is None:
            problems.append(f"I7:{key} 缺 {field}")
            continue
        f = dist / fname
        if f.is_file() and f.stat().st_size != declared:
            problems.append(f"I7:{key} {field}={declared} 与实物 {f.stat().st_size} 不一致({fname})")
    # I3:manifest.components ↔ lock ↔ 实物 逐名 sha 三方核对
    comps = entry.get('components') or []
    if comps:
        lock_path = dist / 'components' / 'components-lock.json'
        if not lock_path.is_file():
            problems.append('I3:dist/components/components-lock.json 缺失')
        else:
            lock = json.loads(lock_path.read_text())
            lock_sha = {c['name']: c['sha256'] for c in lock.get('components') or []}
            man_sha = {c['name']: c['sha256'] for c in comps}
            if set(lock_sha) != set(man_sha):
                problems.append(f"I3:{key} manifest/lock 部件集合漂移")
            for name in set(lock_sha) & set(man_sha):
                if lock_sha[name] != man_sha[name]:
                    problems.append(f"I3:{key} 部件 {name} manifest/lock sha 漂移")
print('; '.join(problems) if problems else 'OK')
PY86
)"
  if [ "${S86_RES}" = "OK" ]; then
    ok "[86] dist manifest I3/I5/I7 真值核对通过"
  else
    bad "[86] 不变量违约: ${S86_RES}"; S86_BAD=1
  fi
else
  warn "[86] dist 未打包,跳过 I3/I5/I7 真值核对(I4/I8 静态锚已核)"
fi
[ "${S86_BAD}" = "0" ] && ok "[86] 增量八不变量 全在位"

# 87. kentang 懒挂载(WS-3d):代理/开关/预热/失败响亮/回归测试全在位
echo "[87] kentang 懒挂载"
S87_BAD=0
S87_REG="${REPO_ROOT}/Horosa-Web/astropy/websrv/kentang/registry.py"
grep -q "class _LazyMountedService" "${S87_REG}" 2>/dev/null || { bad "[87] 懒挂载代理缺位"; S87_BAD=1; }
grep -q "HOROSA_KENTANG_LAZY" "${S87_REG}" 2>/dev/null || { bad "[87] kill-switch HOROSA_KENTANG_LAZY 缺位"; S87_BAD=1; }
grep -q "def prewarm_kentang_services" "${S87_REG}" 2>/dev/null || { bad "[87] 空闲预热入口缺位(首点兜底)"; S87_BAD=1; }
grep -q "prewarm_kentang_services" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py" 2>/dev/null || { bad "[87] webchartsrv 未接预热(懒挂载首点无人兜)"; S87_BAD=1; }
grep -q "test_lazy_proxy_load_failure_is_loud_not_404" "${REPO_ROOT}/Horosa-Web/astropy/tests/test_kentang_lazy_mount.py" 2>/dev/null || { bad "[87] 失败响亮(非404)回归测试缺位"; S87_BAD=1; }
[ "${S87_BAD}" = "0" ] && ok "[87] 懒挂载 代理/开关/预热/测试 全在位"

# 88. AppCDS 链(WS-3e):base 再生+预训练+增量豁免 全在位;payload 已产则验实物
echo "[88] AppCDS base+预置链"
S88_BAD=0
S88_PKG="${INSTALLER_ROOT}/scripts/package_runtime_payload.sh"
grep -q "Xshare:dump" "${S88_PKG}" 2>/dev/null || { bad "[88] 打包缺 base CDS 再生(jlink 不产 classes.jsa=自训链静默死)"; S88_BAD=1; }
grep -q "HOROSA_SKIP_CDS_PRESEED" "${S88_PKG}" 2>/dev/null || { bad "[88] 打包缺 CDS 预训练段"; S88_BAD=1; }
grep -q "app-cds.jsa'" "${S88_PKG}" 2>/dev/null || grep -q "app-cds.jsa" "${S88_PKG}" 2>/dev/null || { bad "[88] 打包缺 .jsa 部件豁免"; S88_BAD=1; }
S88_STAGE="${INSTALLER_ROOT}/build/runtime-payload"
if [ -d "${S88_STAGE}" ]; then
  S88_BASE="${S88_STAGE}/runtime/mac/java/lib/server/classes.jsa"
  S88_SEED="${S88_STAGE}/runtime/mac/bundle/boot-exploded/.app-cds.jsa"
  if [ -s "${S88_BASE}" ]; then
    ok "[88] stage base classes.jsa 在位($(du -h "${S88_BASE}" | cut -f1))"
  else
    bad "[88] stage 缺 base classes.jsa(用户端动态 dump 必败)"; S88_BAD=1
  fi
  if [ -s "${S88_SEED}" ] && [ "$(stat -f%z "${S88_SEED}")" -gt 20000000 ]; then
    ok "[88] stage 预置 .app-cds.jsa 在位($(du -h "${S88_SEED}" | cut -f1))"
  else
    warn "[88] stage 无预置 .jsa(>20MB)——首启走自训兜底(非阻断,但失去首启即 CDS)"
  fi
else
  warn "[88] payload stage 未构建,跳过实物核(代码面锚已核)"
fi
[ "${S88_BAD}" = "0" ] && ok "[88] AppCDS 链 全在位"

# 89. 瞬时化性能资产(WS-3b/3c/3f):账本段名/缓存 flag/自热身/空闲预热/预算测试 全在位
echo "[89] 瞬时化性能资产"
S89_BAD=0
S89_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
grep -q "techniqueCacheEnabled" "${S89_UI}/utils/requestDedupe.js" 2>/dev/null || { bad "[89] L2 技法缓存缺位"; S89_BAD=1; }
grep -q "horosa.perf.techniqueCache" "${S89_UI}/utils/perfFlags.js" 2>/dev/null || { bad "[89] techniqueCache perfFlag 缺位"; S89_BAD=1; }
grep -q "startIdleWarmQueue" "${S89_UI}/utils/idleWarmQueue.js" 2>/dev/null || { bad "[89] 空闲预热队列缺位"; S89_BAD=1; }
grep -q "startIdleWarmQueue" "${S89_UI}/pages/index.js" 2>/dev/null || { bad "[89] 空闲预热未接线 pages/index"; S89_BAD=1; }
grep -q "order: opts.order" "${S89_UI}/pages/index.js" 2>/dev/null || { bad "[89] 预载概率序缺位"; S89_BAD=1; }
grep -q "preloadNavByLabel" "${S89_UI}/pages/index.js" 2>/dev/null || { bad "[89] 悬停预取缺位"; S89_BAD=1; }
grep -q "selfWarmupAsync" "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/java/spacex/astrostudyboot/StartupLedgerListener.java" 2>/dev/null || { bad "[89] Java 自热身缺位"; S89_BAD=1; }
[ -f "${S89_UI}/utils/__tests__/techniquePerfBudget.test.js" ] || { bad "[89] 性能预算测试缺位"; S89_BAD=1; }
for seg in "rust.bootstrap_begin" "rust.emit_ready"; do
  grep -q "${seg}" "${INSTALLER_ROOT}/src-tauri/src/main.rs" 2>/dev/null || { bad "[89] 账本段 ${seg} 缺位"; S89_BAD=1; }
done
grep -q "py.warmup_kentang" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py" 2>/dev/null || { bad "[89] 账本段 py.warmup_kentang 缺位"; S89_BAD=1; }
[ "${S89_BAD}" = "0" ] && ok "[89] 瞬时化资产 全在位"



echo "== 结果 =="
if [ "${fail}" -ne 0 ]; then echo "pre-flight 有 ❌,先修再发。" >&2; exit 1; fi
echo "pre-flight 全部通过 ✅(注意:功能层 e2e 仍需另测,如 AI 用真 key、八字切换显示)。"
