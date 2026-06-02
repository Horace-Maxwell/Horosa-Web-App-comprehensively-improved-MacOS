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

VERSION="$(python3 -c "import json,os;print(json.load(open(os.path.join('${INSTALLER_ROOT}','package.json')))['version'])" 2>/dev/null || echo "")"
RUNTIME_VERSION="$(python3 -c "import json,os;print(json.load(open(os.path.join('${INSTALLER_ROOT}','config','release_config.json'))).get('runtimeVersion',''))" 2>/dev/null || echo "")"
[ -n "${VERSION}" ] || { echo "无法读取 package.json version,终止" >&2; exit 2; }
echo "== Release pre-flight: version ${VERSION} / runtime ${RUNTIME_VERSION} =="

# 1. 版本号 lockstep:所有该带版本号的文件都必须含当前 VERSION
echo "[1] 版本号一致性"
grep -q "\"version\": \"${VERSION}\"" "${INSTALLER_ROOT}/package.json"            && ok "package.json"        || bad "package.json version != ${VERSION}"
grep -q "^version = \"${VERSION}\"" "${INSTALLER_ROOT}/src-tauri/Cargo.toml"       && ok "Cargo.toml"          || bad "Cargo.toml version != ${VERSION}"
grep -q "\"version\": \"${VERSION}\"" "${INSTALLER_ROOT}/src-tauri/tauri.conf.json" && ok "tauri.conf.json"     || bad "tauri.conf.json version != ${VERSION}"
grep -q "version: \"${VERSION}\"" "${REPO_ROOT}/CITATION.cff"                       && ok "CITATION.cff"        || bad "CITATION.cff version != ${VERSION}"
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

# 3b. Windows 同步台账必须有本版条目(每个 Mac 修复都要让 Windows 端能读到 —— 流程硬性要求)
echo "[3b] Windows 同步条目"
grep -q "${VERSION}" "${REPO_ROOT}/docs/windows-sync-handoff.md" && ok "windows-sync-handoff 提及 ${VERSION}" || bad "docs/windows-sync-handoff.md 没有 ${VERSION} 条目 —— Windows 端无法同步本次修复(每个修复须随附技术文档+同步条目)"

# 4. settings.local.json 绝不可被 git 跟踪(里面有 token / 机器路径 —— 本次复盘的泄露风险)
echo "[4] 机密文件未入库"
if git -C "${REPO_ROOT}" ls-files --error-unmatch .claude/settings.local.json >/dev/null 2>&1; then bad ".claude/settings.local.json 被 git 跟踪了(含 token,有泄露风险!)"; else ok ".claude/settings.local.json 未被跟踪"; fi
# harness JSON 必须可解析(本次有人加 token 时漏逗号弄坏过)
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


echo "== 结果 =="
if [ "${fail}" -ne 0 ]; then echo "pre-flight 有 ❌,先修再发。" >&2; exit 1; fi
echo "pre-flight 全部通过 ✅(注意:功能层 e2e 仍需另测,如 AI 用真 key、八字切换显示)。"
