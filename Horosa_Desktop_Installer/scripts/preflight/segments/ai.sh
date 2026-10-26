#!/usr/bin/env bash
# 发布前自检 · AI(分析 / 导出 / 助手 / 本机接口 / 无头)
# 由 preflight/lib.sh 按登记表装载;只定义函数 seg_<id>(),不直接执行。段号用 ${PF_NO}(登记表第二列)。

seg_7() {
# 7. Issue #8(AI 分析 SSE)修复哨兵:catch 必须先记原始异常,SSE 流必须心跳。
#    Windows 端 v2.2.1 调试复盘:Ollama 慢首 token 时空闲断连,catch 块 sendEvent 撞 ClientAbort
#    把 RuntimeException 抛回 ai-analysis-chat-stream 线程,且原始一级异常被 safeErrorMessage
#    吞掉没记日志。本检查保证两个修复都不会被回退。
echo "[7] Issue #8(AI 分析 SSE)修复哨兵"
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
}

seg_8() {
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
}

seg_10() {
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
}

seg_24() {
# 本段自己取(与前段同值;段与段之间不靠函数体里赋的变量传值,--only 单跑也成立)
LR_AICTX="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js")"
# 24. AI 分析页 v2.5.1 复审整改不变量（起课兜底 / 卜卦择日挂载 / 六爻护栏 / 数算流年 / 导出注册 + 自检 / 城市库）
echo "[24] AI 分析页 v2.5.1 复审整改哨兵"
AIEXPORT_JS="$(pf_src_set "${UISRC}/utils/aiExport.js")"
PRECISE_JS="${UISRC}/utils/preciseCalcBridge.js"
HELUO_JS="${UISRC}/utils/heluoLocal.js"
AIEXPORT_TEST_JS="${UISRC}/utils/__tests__/aiExport.test.js"
# B1：fetchPreciseNongli 本地兜底须对软失败(!result)生效(出现≥2次=try+catch),不能只在 catch → 否则奇门/太乙离线缺失
precise_fb_cnt=$(awk '/export async function fetchPreciseNongli/,/^}/' "${PRECISE_JS}" 2>/dev/null | grep -c "buildLocalNongliFallback")
if [ "${precise_fb_cnt:-0}" -ge 2 ]; then ok "[24] fetchPreciseNongli 软失败也走本地兜底(B1:奇门/太乙离线不缺失)"; else bad "[24] fetchPreciseNongli 兜底疑似仍只在 catch(B1 回退风险)"; fi
# New3：卜卦盘/择日盘进白名单
if awk '/TIME_CASTABLE_DIVINATION =/' "${LR_AICTX}" 2>/dev/null | pipe_has "horary" && awk '/TIME_CASTABLE_DIVINATION =/' "${LR_AICTX}" 2>/dev/null | pipe_has "election"; then ok "[24] 卜卦盘/择日盘已入 TIME_CASTABLE_DIVINATION"; else bad "[24] TIME_CASTABLE_DIVINATION 缺 horary/election"; fi
# 🔒 铁律：六爻永不入时间确定白名单(否则按时间伪造卦象)
if awk '/TIME_CASTABLE_DIVINATION =/' "${LR_AICTX}" 2>/dev/null | pipe_has "sixyao"; then bad "[24] 🔒 铁律破:六爻进了 TIME_CASTABLE_DIVINATION"; else ok "[24] 🔒 六爻未入时间确定白名单(护栏在)"; fi
# F：河洛快照出流年卦(调 liuNian)
if awk '/export function buildSnapshotText/,/return lines.join/' "${HELUO_JS}" 2>/dev/null | pipe_has "liuNian("; then ok "[24] 河洛 buildSnapshotText 已出流年卦(调 liuNian)"; else bad "[24] 河洛快照未调 liuNian —— 仍缺整层流年卦"; fi
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
if awk '/AI_EXPORT_SECTION_MIGRATION_KEYS = \[/,/\];/' "${AIEXPORT_JS}" 2>/dev/null | pipe_has "'astrochart'" \
  && awk '/AI_EXPORT_SECTION_MIGRATION_KEYS = \[/,/\];/' "${AIEXPORT_JS}" 2>/dev/null | pipe_has "'primarydirect'" \
  && awk '/AI_EXPORT_SECTION_MIGRATION_KEYS = \[/,/\];/' "${AIEXPORT_JS}" 2>/dev/null | pipe_has "'firdaria'"; then
  ok "[24] AI导出 migration 覆盖占星/星运核心(astrochart/primarydirect/firdaria)"
else
  bad "[24] AI导出 migration 漏占星/星运核心 → 预设新段升级不入老用户设置(补进 AI_EXPORT_SECTION_MIGRATION_KEYS)"
fi
# 四同步跨系统自检断言须在(任何技法漏接 导出/设置/挂载/储存 其一即在 jest 红)
if grep -q "四同步跨系统一致性" "${AIEXPORT_TEST_JS}" 2>/dev/null; then ok "[24] AI 四同步跨系统自检断言在(导出/设置/挂载/储存)"; else bad "[24] 缺 AI 四同步跨系统自检断言"; fi
}

seg_30() {
# 30. Windows #15：Ollama 走原生 /api/chat（num_ctx 才生效）。Java 改需重编 jar 同步 Win。
echo "[30] Ollama num_ctx：原生 /api/chat 分支(修 Windows #15)"
if [ -f "${AIPROXY}" ]; then
  if grep -q "streamOllamaNative" "${AIPROXY}" && grep -q "/api/chat" "${AIPROXY}" && grep -q "ollamaNativeBase" "${AIPROXY}"; then
    ok "[30] Ollama 聊天走原生 /api/chat + options 嵌套(num_ctx 生效);其它 provider 不变"
  else
    bad "[30] AIAnalysisProxyService 缺 Ollama 原生 /api/chat 分支 —— num_ctx 会被 OpenAI 兼容口忽略、回退 4096 截断(Win #15 复发)"
  fi
else
  warn "[30] 未找到 AIAnalysisProxyService.java(结构变动?手动核实 Ollama 原生分支仍在)"
fi
}

seg_31() {
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
  # ③ 地点覆盖:renderLocOverride / transitLat 两件齐全(太阳弧是地心黄经,不设地点)。
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
}

seg_129() {
# ---- seg_129 可选中文字 PDF 矢量字体必须 TrueType(glyf) 整嵌 —— 防 CJK 乱码回归(2026-07-14 FL) ----
#   血泪根因:内嵌 .otf(CFF)经 pdf-lib 产出结构非法内嵌字体文件 → macOS Preview/poppler 拒渲染 =
#   整份中文乱码(pdffonts 报 "Embedded font file may be invalid");且 fontkit subset:true 静默丢字形。
#   修法=字体 CFF→TrueType(glyf,cu2qu)+ embedFont subset:false 整嵌。守卫与 aiExportPdfVector.test.js 双护。
S129_BAD=0
S129_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S129_ENGINE="${S129_UI}/src/utils/aiExportPdfVector.js"
S129_FONT="${S129_UI}/public/fonts/HorosaCJK-subset.ttf"
echo "[${PF_NO}] 矢量 PDF 字体 TrueType 整嵌(防 CJK 乱码回归)"
if [ -f "${S129_ENGINE}" ]; then
  if [ ! -f "${S129_FONT}" ]; then
    bad "[${PF_NO}] 缺 TrueType 字体 HorosaCJK-subset.ttf(引擎取不到→矢量 PDF 失败)"; S129_BAD=1
  else
    S129_TAG="$(python3 -c "import sys;sys.stdout.write(open('${S129_FONT}','rb').read(4).decode('latin1'))" 2>/dev/null || echo '??')"
    [ "${S129_TAG}" = "OTTO" ] && { bad "[${PF_NO}] 字体是 CFF/OTF('OTTO')→pdf-lib 产非法内嵌=乱码;须转 TrueType(glyf)"; S129_BAD=1; }
  fi
  grep -q "HorosaCJK-subset.ttf" "${S129_ENGINE}" || { bad "[${PF_NO}] 引擎 FONT_URLS 未指向 .ttf"; S129_BAD=1; }
  grep -q "subset: false" "${S129_ENGINE}" || { bad "[${PF_NO}] 引擎 embedFont 未用 subset:false(subset:true 会静默丢字形)"; S129_BAD=1; }
  grep -q "embedFont(fontBytes, { subset: true })" "${S129_ENGINE}" && { bad "[${PF_NO}] 引擎仍试 subset:true(丢字形回潮)"; S129_BAD=1; }
  [ -f "${S129_UI}/public/fonts/HorosaCJK-subset.otf" ] && { bad "[${PF_NO}] 旧 CFF 字体 .otf 仍在(乱码源,应删)"; S129_BAD=1; }
  grep -q "fontSfntKind" "${S129_UI}/src/utils/__tests__/aiExportPdfVector.test.js" 2>/dev/null || { bad "[${PF_NO}] aiExportPdfVector.test 缺字体乱码守卫(fontSfntKind 双锚)"; S129_BAD=1; }
fi
[ "${S129_BAD}" = "0" ] && ok "[${PF_NO}] 矢量 PDF 字体 TrueType(glyf)整嵌 + 旧 .otf 已除 + jest 双锚守卫在位"
}

seg_130() {
# ---- seg_130 导出截图星符号字体内嵌 —— 防「A/B/C/D 裸字母不成 glyph」回归(2026-07-14 FL) ----
#   血泪根因:PDF/Word 导出的图盘截图走 html-to-image,旧代码 skipFonts:true 跳过所有 @font-face →
#   星符号字体(字母→glyph 映射)不内嵌 → canvas 回退裸字母 A/B/C/D…。
#   修法:buildScreenshotFontEmbedCSS 预取同源小字体 base64 内联成 fontEmbedCSS(避 WKWebView 全量扫 hang),
#   URL 必经 new URL(raw, sheet.href) 相对样式表解析(相对页面会取 SPA 兜底 index.html→字体损坏),
#   magic-byte 挡 HTML 兜底。守卫与 pageScreenshot.test.js 双护。
S130_BAD=0
S130_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S130_PS="${S130_UI}/src/utils/pageScreenshot.js"
echo "[${PF_NO}] 导出截图星符号字体内嵌(防裸字母回归)"
if [ -f "${S130_PS}" ]; then
  grep -q "buildScreenshotFontEmbedCSS" "${S130_PS}" || { bad "[${PF_NO}] 缺 buildScreenshotFontEmbedCSS(截图不内嵌符号字体=裸字母)"; S130_BAD=1; }
  grep -q "fontEmbedCSS" "${S130_PS}" || { bad "[${PF_NO}] toCanvas 未用 fontEmbedCSS(回到 skipFonts=裸字母)"; S130_BAD=1; }
  grep -q "new URL(m\[1\], sheets\[s\].href" "${S130_PS}" || { bad "[${PF_NO}] 字体 URL 未相对样式表解析(相对页面会取 SPA 兜底 HTML→字体损坏)"; S130_BAD=1; }
  grep -q "wOF2" "${S130_PS}" || { bad "[${PF_NO}] 缺 magic-byte 校验(不挡 HTML 兜底=把 index.html 当字体)"; S130_BAD=1; }
  grep -q "buildScreenshotFontEmbedCSS" "${S130_UI}/src/utils/__tests__/pageScreenshot.test.js" 2>/dev/null || { bad "[${PF_NO}] pageScreenshot.test 缺截图字体守卫"; S130_BAD=1; }
fi
[ "${S130_BAD}" = "0" ] && ok "[${PF_NO}] 截图 fontEmbedCSS 内嵌(符号字体成 glyph)+ URL 相对样式表解析 + magic 挡兜底 + jest 守卫在位"
}

seg_236() {
# seg_236 AI 助手行动能力·运行时门控锁(2026-09-01):总开关默认关(仅 '1' 为开)=完全现状路径;
#   SSE 事件名前后端互锚;AIAnalysisMain 插座在位;jest 判别向量在位;看门狗续命含工具帧。
echo "[${PF_NO}] AI 助手运行时门控(总开关默认关/事件互锚/插座在位)"
S236_BAD=0
S236_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S236_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service"
grep -aq "safeLocalStorageGet(AGENT_ENABLED_KEY) === '1'" "${S236_UI}/src/utils/aiAgent/prefs.js" || { bad "[${PF_NO}] prefs.js 总开关判据不是「仅 '1' 为开」(默认关被改)"; S236_BAD=1; }
grep -aq "if(!enabled){ return NULL_AGENT; }" "${S236_UI}/src/utils/aiAgent/runtime.js" || { bad "[${PF_NO}] runtime.js 关闭态未返回 NULL_AGENT"; S236_BAD=1; }
for ev in tool_call_start tool_call; do
  grep -aq "case '${ev}'" "${S236_UI}/src/utils/aiAgent/runtime.js" || { bad "[${PF_NO}] runtime.js 未消费 SSE 事件 ${ev}"; S236_BAD=1; }
  grep -aq "\"${ev}\"" "${S236_JAVA}/AIToolCallSupport.java" || { bad "[${PF_NO}] AIToolCallSupport.java 未发出 SSE 事件 ${ev}"; S236_BAD=1; }
done
grep -aq "event.type === 'tool_call'" "${S236_UI}/src/services/aianalysis.js" || { bad "[${PF_NO}] aianalysis.js 看门狗未把 tool_call 计为真产出"; S236_BAD=1; }
S236_MAIN="$(pf_src_set "${S236_UI}/src/components/aianalysis/AIAnalysisMain.js")"
for anchor in "createAgentTurn({" "while(await agent.settleRound())" "agent.onEvent(event);" "agentTrace: agent.trace() || undefined" "<AgentActionBar " "<AgentAbilityPanel />" "tools: agent.toolDefs()"; do
  grep -aqF "${anchor}" "${S236_MAIN}" || { bad "[${PF_NO}] AIAnalysisMain.js 插座缺失: ${anchor}"; S236_BAD=1; }
done
[ "$(grep -ac "agentTrace: item.agentTrace," "${S236_MAIN}")" = "4" ] || { bad "[${PF_NO}] AIAnalysisMain.js 四处消息 map 未全带 agentTrace"; S236_BAD=1; }
# 流式合帧锁:delta/reasoning 只登记不逐条提交(schedule 恰 2 处)、末帧 flush、catch/finally 双 cancel、助手正文经记忆化组件渲染。
# 任一缺失=高吞吐模型长回复期主线程被逐 delta 全量 markdown 重渲染打满(实测 35 气泡会话 144s 内阻塞 140s)。
grep -aq "createStreamFlusher(()=>{" "${S236_MAIN}" || { bad "[${PF_NO}] AIAnalysisMain.js 流式合帧器未创建"; S236_BAD=1; }
[ "$(grep -ac "streamFlusher.schedule();" "${S236_MAIN}")" = "2" ] || { bad "[${PF_NO}] AIAnalysisMain.js delta/reasoning 未各经 streamFlusher.schedule()"; S236_BAD=1; }
grep -aq "streamFlusher.flush();" "${S236_MAIN}" || { bad "[${PF_NO}] AIAnalysisMain.js 末帧 flush 缺失"; S236_BAD=1; }
[ "$(grep -ac "streamFlusher.cancel();" "${S236_MAIN}")" = "2" ] || { bad "[${PF_NO}] AIAnalysisMain.js catch/finally 未双 cancel 合帧器"; S236_BAD=1; }
grep -aq "<AssistantMarkdown className={styles.markdownBody}" "${S236_MAIN}" || { bad "[${PF_NO}] AIAnalysisMain.js 助手正文未经 AssistantMarkdown 记忆化组件渲染"; S236_BAD=1; }
grep -aqF "content: streamBufferRef.current," "${S236_MAIN}" && { bad "[${PF_NO}] AIAnalysisMain.js 逐 delta 直接 setMessages 复活(合帧被绕过)"; S236_BAD=1; }
[ -f "${S236_UI}/src/utils/aiStreamFlush.js" ] && [ -f "${S236_UI}/src/utils/__tests__/aiStreamFlush.test.js" ] || { bad "[${PF_NO}] aiStreamFlush.js 或其单测缺失"; S236_BAD=1; }
# 本机 IP 探测整体移除锁:request.js/helper.js 去注释后不得再出现 LocalIp/getUserIP/RTCPeerConnection
# (每请求 new RTCPeerConnection 且不关=~500 次后全部后端请求静默失败;Java 侧该头只作日志兜底,无业务消费)。
if [ "$(sed -E 's#//.*$##' "${S236_UI}/src/utils/request.js" "${S236_UI}/src/utils/helper.js" | grep -acE '\bLocalIp\b|getUserIP|RTCPeerConnection')" != "0" ]; then bad "[${PF_NO}] request.js/helper.js 复活了 LocalIp/getUserIP/RTCPeerConnection"; S236_BAD=1; fi
[ -f "${S236_UI}/src/utils/__tests__/requestHeaders.noLocalIp.test.js" ] || { bad "[${PF_NO}] requestHeaders.noLocalIp.test.js 缺失"; S236_BAD=1; }
grep -aq "silent failure" "${S236_UI}/src/utils/request.js" || { bad "[${PF_NO}] request.js 静默失败留痕缺失(吞错零日志=排障盲区)"; S236_BAD=1; }
for t in aiAgentRuntime aiAgentProtocol aiToolsCatalog.contract aiToolsAdditiveGuard aiToolsRecords aiToolsSettings aiToolsCast; do
  [ -f "${S236_UI}/src/utils/__tests__/${t}.test.js" ] || { bad "[${PF_NO}] jest 哨兵缺失 ${t}.test.js"; S236_BAD=1; }
done
for k in horosa.ai.agent.enabled horosa.ai.agent.approval horosa.ai.agent.caps.v1 horosa.ai.agent.ledger.v1; do
  grep -aq "'${k}'" "${S236_UI}/src/utils/storageKeyRegistry.js" || { bad "[${PF_NO}] storageKeyRegistry 未登记 ${k}"; S236_BAD=1; }
  grep -aq "'${k}'" "${S236_UI}/src/utils/techniqueOnboardingContract.js" || { bad "[${PF_NO}] onboarding contract 未登记 ${k}"; S236_BAD=1; }
done
grep -aq "AGENT_SYSTEM_RULES" "${S236_UI}/src/utils/aiAgent/protocol.js" || { bad "[${PF_NO}] protocol.js 守则块缺失"; S236_BAD=1; }
RT_SRC="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAgent/runtime.js"
MAIN_SRC="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/aianalysis/AIAnalysisMain.js")"
[ "$(sed 's#//.*$##' "${RT_SRC}" | grep -ac "failRound(message)")" != "0" ] || { bad "[${PF_NO}] 运行时缺流层抛错的失败收口 failRound"; S236_BAD=1; }
[ "$(sed 's#//.*$##' "${MAIN_SRC}" | grep -ac "agent.failRound(failMessage)")" != "0" ] || { bad "[${PF_NO}] 页面 catch 未调 failRound(抛错轮不归档 → trace 停止原因恒空)"; S236_BAD=1; }
[ "${S236_BAD}" = "0" ] && ok "[${PF_NO}] 运行时门控/事件互锚/插座/注册表/哨兵全在位"
}

seg_241() {
# seg_241 AI 规模面锁(IDB 索引读/上下文缓存自裁/源列表缓存/批量选源/写放大)
echo "[${PF_NO}] AI 规模面锁(IDB 索引读/上下文缓存自裁/源列表缓存/批量选源/写放大)"
S241_BAD=0
S241_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
grep -aq "\['conversationId', 'conversationId'\]" "${S241_UI}/src/utils/aiAnalysisStore.js" || { bad "[${PF_NO}] aiAnalysisStore 缺 messages.conversationId 索引声明"; S241_BAD=1; }
grep -aq "export async function readByIndex" "${S241_UI}/src/utils/aiAnalysisStore.js" || { bad "[${PF_NO}] aiAnalysisStore 缺 readByIndex"; S241_BAD=1; }
awk '/^export async function listConversationMessages/,/^}/' "${S241_UI}/src/utils/aiAnalysisStore.js" | pipe_has "listStoreRecords(AI_ANALYSIS_STORES.messages)" && { bad "[${PF_NO}] listConversationMessages 退回全表 getAll"; S241_BAD=1; }
grep -aq "CONTEXT_CACHE_MAX_ENTRIES = 300" "${S241_UI}/src/utils/aiAnalysisStore.js" || { bad "[${PF_NO}] context_cache 条数上限常量缺失/被改"; S241_BAD=1; }
grep -aq "schedulePruneContextCache()" "$(pf_src_set "${S241_UI}/src/utils/aiAnalysisContext.js")" || { bad "[${PF_NO}] getAnalysisSourceContext 写后未调度裁剪"; S241_BAD=1; }
grep -aq "export function findAnalysisSourceById" "${S241_UI}/src/utils/aiAnalysisSources.js" || { bad "[${PF_NO}] aiAnalysisSources 缺 findAnalysisSourceById"; S241_BAD=1; }
grep -aq "findAnalysisSourceById(" "${S241_UI}/src/utils/aiTools/tools/castTechnique.js" || { bad "[${PF_NO}] castTechnique 记录源未走直查"; S241_BAD=1; }
grep -aq "listAnalysisSources().find" "${S241_UI}/src/utils/aiTools/tools/castTechnique.js" && { bad "[${PF_NO}] castTechnique 又为找一条解析全库"; S241_BAD=1; }
grep -aq "getByCid" "${S241_UI}/src/utils/localRecordStore.js" || { bad "[${PF_NO}] localRecordStore 缺 getByCid"; S241_BAD=1; }
grep -aq "__serializeListForTests" "${S241_UI}/src/utils/localRecordStore.js" || { bad "[${PF_NO}] localRecordStore 写放大优化(serializeList)缺失"; S241_BAD=1; }
for f in runtime.js mcpBridge.js; do grep -aq "deferSelect" "${S241_UI}/src/utils/aiAgent/$f" || { bad "[${PF_NO}] aiAgent/$f 缺批量选源合并(deferSelect)"; S241_BAD=1; }; done
for f in createChartRecord.js createCaseRecord.js; do grep -aq "deferSelect" "${S241_UI}/src/utils/aiTools/tools/$f" || { bad "[${PF_NO}] aiTools/$f 缺 deferSelect 分支"; S241_BAD=1; }; done
for t in aiAnalysisStoreIndexes contextCachePrune aiAnalysisSourcesCache localRecordStoreWriteAmp aiAgentBatchSelect; do [ -f "${S241_UI}/src/utils/__tests__/$t.test.js" ] || { bad "[${PF_NO}] 回归测试 $t.test.js 缺失"; S241_BAD=1; }; done
grep -aq '"fake-indexeddb"' "${S241_UI}/package.json" || { bad "[${PF_NO}] fake-indexeddb devDependency 缺失(IDB 真径测试跑不了)"; S241_BAD=1; }
CAST_SRC="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiTools/tools/castTechnique.js"
[ "$(sed 's#//.*$##' "${CAST_SRC}" | grep -ac "clipContentToBudget(picked")" != "0" ] || { bad "[${PF_NO}] cast_technique 截断未段对齐(会把快照砍在表中间)"; S241_BAD=1; }
[ "$(sed 's#//.*$##' "${CAST_SRC}" | grep -ac "E_SECTION_NOT_FOUND")" != "0" ] || { bad "[${PF_NO}] cast_technique 缺按段取的空命中报错"; S241_BAD=1; }
[ "${S241_BAD}" = "0" ] && ok "[${PF_NO}] AI 规模面锁(IDB 索引读/上下文缓存自裁/源列表缓存/批量选源/写放大)"
}

seg_242() {
# seg_242 请求失败分类留痕 + 诊断账本(吞错必留痕)
echo "[${PF_NO}] 请求失败分类留痕 + 诊断账本(吞错必留痕)"
S242_BAD=0
S242_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
[ -f "${S242_UI}/src/utils/requestFailure.js" ] && [ -f "${S242_UI}/src/utils/requestTelemetry.js" ] && [ -f "${S242_UI}/src/utils/backendDiagText.js" ] || { bad "[${PF_NO}] requestFailure/requestTelemetry/backendDiagText 缺失"; S242_BAD=1; }
[ "$(grep -ac 'classifyRequestFailure(' "${S242_UI}/src/utils/request.js")" -ge 3 ] || { bad "[${PF_NO}] request.js 三条失败分支未全经 classifyRequestFailure"; S242_BAD=1; }
[ "$(grep -ac 'recordRequestFailure(' "${S242_UI}/src/utils/request.js")" -ge 3 ] || { bad "[${PF_NO}] request.js 三条失败分支未全留痕"; S242_BAD=1; }
grep -aq "recordRequestFailure(" "${S242_UI}/src/utils/chartFetch.js" || { bad "[${PF_NO}] chartFetch.js 失败未留痕"; S242_BAD=1; }
grep -aq "buildBackendDiagText" "${S242_UI}/src/components/common/BackendStatusDot.js" || { bad "[${PF_NO}] 复制信息未接诊断文本"; S242_BAD=1; }
grep -aq "page_telemetry" "${S242_UI}/src/utils/desktopBridgeDiag.js" || { bad "[${PF_NO}] 页面留痕未上报壳账本(page_telemetry)"; S242_BAD=1; }
grep -aq "reportPageTelemetry" "${S242_UI}/src/layouts/app.js" || { bad "[${PF_NO}] layouts/app.js 未挂离线跳变/周期上报"; S242_BAD=1; }
for t in requestFailure requestTelemetry requestSilentTrace backendDiagText; do [ -f "${S242_UI}/src/utils/__tests__/$t.test.js" ] || { bad "[${PF_NO}] 回归测试 $t.test.js 缺失"; S242_BAD=1; }; done
[ "${S242_BAD}" = "0" ] && ok "[${PF_NO}] 请求失败分类留痕 + 诊断账本(吞错必留痕)"
}

seg_245() {
# seg_245 AI 工具错误码单一真源(码表/文案/信封 retryable+cause;三集合恒等)
echo "[${PF_NO}] AI 工具错误码单一真源(码表/文案/信封 retryable+cause)"
S245_BAD=0
S245_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S245_TBL="${S245_UI}/src/utils/aiTools/errorCodes.js"
S245_CAST="${S245_UI}/src/utils/aiTools/tools/castTechnique.js"
S245_PROTO="${S245_UI}/src/utils/aiAgent/protocol.js"
S245_REG="${S245_UI}/src/utils/aiTools/registry.js"
S245_DOC="${REPO_ROOT}/docs/AI_AGENT_RUNTIME.md"
# 剥单行注释再 grep:注释里复写同一字面量会让肯定式哨兵假绿、否定式假红(字面量哨兵×注释双向陷阱)。
if [ ! -f "${S245_TBL}" ]; then
	bad "[${PF_NO}] aiTools/errorCodes.js 缺失(错误码没有单一真源)"; S245_BAD=1
else
	for sym in "export const TOOL_ERROR_CODES" "export const TOOL_ERROR_CODE_LIST" "export const TOOL_ERROR_LAYERS" "export const ERROR_CAUSE_KEYS" "export function getErrorMeta" "export function isRetryable" "export function sanitizeErrorCause"; do
		pf_code "${S245_TBL}" | pipe_has -F "${sym}" || { bad "[${PF_NO}] errorCodes.js 缺导出:${sym}"; S245_BAD=1; }
	done
	# 三集合恒等:源码里出现的 'E_*' 字面量 == 冻结表键 == 文档表首列。任一漂移=有码没落表/表里有死码/文档没跟。
	S245_SCAN="$(find "${S245_UI}/src/utils/aiTools" "${S245_UI}/src/utils/aiAgent" "${S245_UI}/src/integrations" -name '*.js' ! -name 'errorCodes.js' ! -name '*.test.js' -exec sed -E 's#//.*$##' {} + | grep -aoE "'E_[A-Z0-9_]+'" | tr -d "'" | sort -u)"
	S245_KEYS="$(pf_code "${S245_TBL}" | grep -aoE '^[[:space:]]+E_[A-Z0-9_]+: def\(' | grep -aoE 'E_[A-Z0-9_]+' | sort -u)"
	S245_DOCK="$(grep -aoE '^\| `E_[A-Z0-9_]+` \|' "${S245_DOC}" | grep -aoE 'E_[A-Z0-9_]+' | sort -u)"
	S245_N="$(printf '%s\n' "${S245_KEYS}" | grep -ac 'E_')"
	[ "${S245_N}" -ge 40 ] || { bad "[${PF_NO}] 码表只有 ${S245_N} 条(应 ≥40,少了说明有码没落表)"; S245_BAD=1; }
	[ "${S245_SCAN}" = "${S245_KEYS}" ] || { bad "[${PF_NO}] 源码扫描集 ≠ 冻结表(差集: $(comm -3 <(printf '%s\n' "${S245_SCAN}") <(printf '%s\n' "${S245_KEYS}") | tr -d '\t' | tr '\n' ' '))"; S245_BAD=1; }
	[ "${S245_DOCK}" = "${S245_KEYS}" ] || { bad "[${PF_NO}] 文档错误码表 ≠ 冻结表(差集: $(comm -3 <(printf '%s\n' "${S245_DOCK}") <(printf '%s\n' "${S245_KEYS}") | tr -d '\t' | tr '\n' ' '))"; S245_BAD=1; }
	# 可重试只给「同参机械重试有望成功」的后端不可达一类;多标一个=让模型在必败路径上空转。
	[ "$(pf_code "${S245_TBL}" | grep -acE "def\('[a-z]+', true,")" = "1" ] || { bad "[${PF_NO}] 可重试码不是恰好一枚(判据:同参重试有望成功)"; S245_BAD=1; }
	pf_code "${S245_TBL}" | pipe_has -E "^[[:space:]]+E_CAST_BACKEND_FAILED: def\('backend', true," || { bad "[${PF_NO}] E_CAST_BACKEND_FAILED 不是 backend 层可重试码"; S245_BAD=1; }
	pf_code "${S245_TBL}" | pipe_has -F "该技法未产出内容" || { bad "[${PF_NO}] E_SNAPSHOT_MISSING 文案未落表(文案须单源)"; S245_BAD=1; }
fi
grep -aqF '| 码 | 层 | 可重试 | 产出方 | 用户可做 |' "${S245_DOC}" || { bad "[${PF_NO}] 文档缺错误码表(表头须逐列固定)"; S245_BAD=1; }
# 信封:失败才带 retryable/cause;retryable 缺省查表;cause 过白名单(绝不带请求体/响应头/令牌)。
pf_code "${S245_PROTO}" | pipe_has -F "isRetryable(r.code)" || { bad "[${PF_NO}] 信封 retryable 未查错误码表"; S245_BAD=1; }
pf_code "${S245_PROTO}" | pipe_has -F "sanitizeErrorCause(r.cause)" || { bad "[${PF_NO}] 信封 cause 未过白名单过滤"; S245_BAD=1; }
pf_code "${S245_PROTO}" | pipe_has -E "failure \?[^\n]*retryable" || { bad "[${PF_NO}] 信封 ok:true 也带 retryable(须只在失败信封带)"; S245_BAD=1; }
# 起盘失败三路各出各码;负锚:那句把请求层故障说成计算服务离线的旧文案不得回潮。
for c in E_CAST_FAILED E_CAST_BACKEND_FAILED E_SNAPSHOT_MISSING; do
	pf_code "${S245_CAST}" | pipe_has -F "'${c}'" || { bad "[${PF_NO}] castTechnique 失败三路缺 ${c}"; S245_BAD=1; }
done
pf_code "${S245_CAST}" | pipe_has -F "需本机计算服务在线" && { bad "[${PF_NO}] castTechnique 旧误导文案回潮(纯本地技法照它去查服务=白查)"; S245_BAD=1; }
pf_code "${S245_CAST}" | pipe_has -F "sanitizeErrorCause(" || { bad "[${PF_NO}] castTechnique 的 cause 未过白名单"; S245_BAD=1; }
pf_code "${S245_CAST}" | pipe_has -F "lastFor(" || { bad "[${PF_NO}] castTechnique 未取 /chart 失败留痕作 cause"; S245_BAD=1; }
# 写前快照失败是工具层的事,不再借用取值类码(借用会让模型反复去改本来没错的参数)。
pf_code "${S245_REG}" | pipe_has -F "'E_SETTING_SNAPSHOT_FAILED'" || { bad "[${PF_NO}] registry 写前快照失败未用 E_SETTING_SNAPSHOT_FAILED"; S245_BAD=1; }
[ "$(pf_code "${S245_REG}" | grep -aF "写前快照失败" | grep -acF "E_SETTING_VALUE_INVALID")" = "0" ] || { bad "[${PF_NO}] registry 写前快照仍借用取值类码"; S245_BAD=1; }
[ -f "${S245_UI}/src/utils/__tests__/aiToolsErrorCodes.contract.test.js" ] || { bad "[${PF_NO}] 合同测试 aiToolsErrorCodes.contract.test.js 缺失"; S245_BAD=1; }
[ "${S245_BAD}" = "0" ] && ok "[${PF_NO}] AI 工具错误码单一真源(${S245_N} 码;三集合恒等/文案单源/信封 retryable+cause)"
}

seg_254() {
# seg_254 压测二轮·稳健性债收口锁(2026-09-06):账本写前预留=拒绝执行 / 注册幂等 / 资源面只认自有键 / 桥限流按会话分桶+资源面受限+桶表有界 /
#       外部 schema 消毒 / 自动化引擎链深度·每秒闸·尝试即冷却·deps 真接线 / 通知横幅节流+索引游标 / 任务 CAS·裁剪·预热 /
#       调度一跳超时·信号·租约 / 审批超时撤台 / 目标任务幂等闸·孤儿过滤·判官 signal / 起盘链解锁 / 短调用 signal 直达请求层 /
#       检索面板换引擎不沿用 Key / 技能包劫持三防 / Java 出站守卫·不跟随重定向·有界读·根因 / Rust 会话 TTL·有界读·子进程随连接退出
echo "[${PF_NO}] 压测二轮·稳健性债收口锁"
S254_BAD=0
S254_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S254_T="${S254_UI}/utils/__tests__"
S254_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service"
S254_RS="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src"
# 剥单行注释再 grep 字面(注释复写字面=假绿);pipefail 下一律排空计数,不用 grep -q
# ① 账本:预留失败拒绝执行(零写入),裁半重试;错误码三集合同步
pf_need "${S254_UI}/utils/aiTools/ledger.js" "export function reserveAction" "ledger 缺写前预留 reserveAction"
pf_need "${S254_UI}/utils/aiTools/ledger.js" "LEDGER_HALVING_MAX_ROUNDS" "ledger 缺配额裁半重试"
pf_need "${S254_UI}/utils/aiTools/registry.js" "reserveAction({ id: actionId" "registry 跑 additive 工具前未预留账本位"
pf_need "${S254_UI}/utils/aiTools/registry.js" "E_LEDGER_UNAVAILABLE" "registry 预留失败未回 E_LEDGER_UNAVAILABLE"
pf_need "${S254_UI}/utils/aiTools/errorCodes.js" "E_LEDGER_UNAVAILABLE: def(" "errorCodes 缺 E_LEDGER_UNAVAILABLE"
[ "$(grep -acF 'E_LEDGER_UNAVAILABLE' "${REPO_ROOT}/docs/AI_AGENT_RUNTIME.md")" != "0" ] || { bad "[${PF_NO}] 手册 §8 缺 E_LEDGER_UNAVAILABLE 行"; S254_BAD=1; }
# ② 注册幂等:同一份定义再注册短路(零 warn、不清 Ajv 缓存)
pf_need "${S254_UI}/utils/aiTools/registry.js" "sources.get(name) === def" "registry 缺同定义幂等短路"
# ③ 资源面:只认自有键、坏编码不抛、id 封长
pf_need "${S254_UI}/utils/aiTools/resources.js" "hasOwnProperty.call(KIND_READERS, kind)" "resources 类别判定仍走原型链"
pf_need "${S254_UI}/utils/aiTools/resources.js" "RESOURCE_ID_MAX" "resources 缺 id 上限"
# ④ 外部桥:桶键按会话、桶表 LRU、资源/提示分支受限流、坏 URI 回 -32602
pf_need "${S254_UI}/utils/aiAgent/mcpBridge.js" "function bucketKeyOf" "mcpBridge 限流桶仍按客户端自报名分"
pf_need "${S254_UI}/utils/aiAgent/mcpBridge.js" "export const BUCKET_MAX" "mcpBridge 桶表无上限"
pf_need "${S254_UI}/utils/aiAgent/mcpBridge.js" "if(READ_FACE_METHODS.indexOf(method) >= 0){" "mcpBridge 资源/提示分支未过限流"
pf_need "${S254_RS}/mcp_server.rs" "pub fn handle_rpc_with_session" "mcp_server 未把会话身份注入页面分发"
# ⑤ 外部 schema 消毒
pf_need "${S254_UI}/integrations/mcpClient.js" "function sanitizeExternalSchemaNode" "mcpClient 外部 schema 未消毒"
pf_need "${S254_UI}/integrations/mcpClient.js" "EXTERNAL_SCHEMA_MAX_DEPTH" "mcpClient 外部 schema 深度不封"
# ⑥ 自动化引擎:链深度 / 每秒闸 / 尝试即冷却 / deps 真接线
pf_need "${S254_UI}/utils/aiAgent/automation/engine.js" "export const MAX_CHAIN_DEPTH" "engine 缺链深度上限"
pf_need "${S254_UI}/utils/aiAgent/automation/engine.js" "export const MAX_EVENTS_PER_SEC" "engine 缺每秒事件闸"
[ -f "${S254_UI}/utils/aiAgent/automation/deps.js" ] || { bad "[${PF_NO}] automation/deps.js 缺失(三件动作恒不可用)"; S254_BAD=1; }
pf_need "${S254_UI}/layouts/app.js" "buildDefaultAutomationDeps()" "app.js 仍裸调 bindAutomationEngine"
pf_need "${S254_UI}/utils/aiAgent/bgSink.js" "export function reportBackgroundFailure" "bgSink 缺后台链留痕"
# ⑦ 通知:横幅令牌桶+同文去重;listNotices 走索引游标
pf_need "${S254_UI}/utils/aiAgent/tasks/noticeStore.js" "export function allowDesktopBanner" "noticeStore 缺横幅节流"
pf_need "${S254_UI}/utils/aiAgent/tasks/noticeStore.js" "listStoreRecordsByIndexCursor(AI_ANALYSIS_STORES.agentNotices, 'createdAt'" "listNotices 未走 createdAt 索引游标"
pf_need "${S254_UI}/utils/aiAnalysisStore.js" "export async function listStoreRecordsByIndexCursor" "aiAnalysisStore 缺索引游标读原语"
# ⑧ 任务:CAS / 裁剪 / 预热
pf_need "${S254_UI}/utils/aiAnalysisStore.js" "export async function updateStoreRecordIf" "aiAnalysisStore 缺单事务 CAS 原语"
pf_need "${S254_UI}/utils/aiAgent/tasks/taskStore.js" "export async function patchTaskIf" "taskStore 缺 patchTaskIf"
pf_need "${S254_UI}/utils/aiAgent/tasks/taskStore.js" "export async function pruneTasks" "taskStore 缺 pruneTasks"
pf_need "${S254_UI}/utils/aiAgent/tasks/taskStore.js" "export const TASK_KEEP_MAX" "taskStore 缺 TASK_KEEP_MAX"
pf_need "${S254_UI}/utils/aiAgent/tasks/taskStore.js" "export async function warmTaskCache" "taskStore 缺 warmTaskCache"
pf_need "${S254_UI}/utils/aiAgent/tasks/index.js" "settle" "撤销处理器未附 settle 承诺(账本会被标成已撤销)"
# ⑨ 调度:CAS 抢跑 / 一跳超时 / 信号 / 租约键登记
pf_need "${S254_UI}/utils/aiAgent/tasks/scheduler.js" "patchTaskIf(task.id, { status: 'running'" "scheduler 抢跑未走 CAS"
pf_need "${S254_UI}/utils/aiAgent/tasks/scheduler.js" "function hopTimeoutOf" "scheduler 一跳无超时"
pf_need "${S254_UI}/utils/aiAgent/tasks/scheduler.js" "signal: ac.signal" "scheduler 执行体 ctx 无 signal"
pf_need "${S254_UI}/utils/aiAgent/tasks/scheduler.js" "export const SCHEDULER_LEASE_KEY" "scheduler 缺租约键"
pf_need "${S254_UI}/utils/storageKeyRegistry.js" "horosa.ai.tasks.scheduler.lease" "租约键未登记注册表"
pf_need "${S254_UI}/utils/aiAgent/tasks/taskKinds.js" "signal: c.signal" "taskKinds 未透传 signal 给无头轮"
# ⑩ 审批超时撤台;目标任务幂等闸/孤儿过滤/判官 signal
pf_need "${S254_UI}/utils/aiAgent/approvals.js" "entry.timer = setTimeout" "approvals 无超时撤台"
pf_need "${S254_UI}/utils/aiAgent/goalRunner.js" "if(runningLoops.has(taskId)){ return task; }" "goalRunner 缺幂等闸"
pf_need "${S254_UI}/utils/aiAgent/goalRunner.js" "!== ORPHAN_STREAMING_CONTENT" "goalRunner 历史未过滤孤儿正文"
pf_need "${S254_UI}/utils/aiAgent/goalRunner.js" "timeoutMs: GOAL_APPROVAL_TIMEOUT_MS" "goalRunner 审批未走等待台超时"
# ⑪ 起盘链解锁;短调用 signal 直达请求层
pf_need "${S254_UI}/utils/aiTools/tools/castTechnique.js" "function castAbortPromise" "castTechnique 起盘链无中止解锁"
pf_need "${S254_UI}/services/aianalysis.js" "export function requestAIAnalysisChat(values, options)" "services.requestAIAnalysisChat 不收 signal"
pf_need "${S254_UI}/services/aianalysis.js" "export function requestWebSearch(values, options)" "services.requestWebSearch 不收 signal"
pf_need "${S254_UI}/integrations/webSearch.js" "}, { signal });" "runWebSearch 未把 signal 交给 requestWebSearch"
# ⑫ 检索面板换引擎;技能包劫持三防
pf_need "${S254_UI}/components/aianalysis/WebSearchPanel.js" "export function mergeSearchProfileForm" "WebSearchPanel 换引擎仍沿用旧 Key"
pf_need "${S254_UI}/utils/aiChat/skillLimits.js" "export const SKILL_MAX_SYSTEM_PROMPT" "skills 缺系统指令上限(单源 skillLimits.js)"
pf_need "${S254_UI}/utils/aiChat/skills.js" "const conflicts = triggerConflicts(skill.triggers)" "planSkillImport 未检触发词冲突"
pf_need "${S254_UI}/components/aianalysis/chat/SkillPackPanel.js" "plan.conflicts && plan.conflicts.length" "技能包面板未拒冲突导入"
# ⑬ Java 出站守卫;Rust 会话 TTL 与有界读
[ -f "${S254_JAVA}/OutboundUrlGuard.java" ] || { bad "[${PF_NO}] OutboundUrlGuard.java 缺失"; S254_BAD=1; }
pf_need "${S254_JAVA}/AIWebSearchService.java" "HttpClient.Redirect.NEVER" "检索服务仍跟随重定向"
pf_need "${S254_JAVA}/AIWebSearchService.java" "MAX_RESPONSE_BYTES = 2L * 1024 * 1024" "检索服务回体无上限"
pf_need "${S254_JAVA}/AIWebSearchService.java" "return OutboundUrlGuard.validate(url)" "检索服务出站地址未过守卫"
pf_need "${S254_RS}/mcp_server.rs" "const SESSION_TTL" "mcp_server 会话无时效"
pf_need "${S254_RS}/mcp_client.rs" "fn read_line_bounded" "mcp_client stdio 行读无上限"
pf_need "${S254_RS}/mcp_client.rs" "take(MAX_RESPONSE_BYTES as u64 + 1)" "mcp_client HTTP 回体先全读后判上限"
pf_need "${S254_RS}/mcp_client.rs" "impl Drop for Conn" "mcp_client 连接丢弃不杀子进程"
# ⑭ 先红后绿的回归锁全部在位
for f in aiAgentGoalRunnerStress agentSchedulerConcurrency webSearchPanel aiChatShortCallSignal mcpResourcesHostile mcpBridgeLimits aiToolsExternalSchemaBomb aiToolsRegistryIdempotent aiAgentInjectionGuard aiChatContextPolicySnapshot aiAgentAutomationStress agentNoticeFlood aiToolsLedgerQuota agentTaskPrune aiUsageNormalize; do
  [ -f "${S254_T}/${f}.test.js" ] || { bad "[${PF_NO}] 回归锁 ${f}.test.js 缺失"; S254_BAD=1; }
done
[ -f "${S254_T}/helpers/agentFakes.js" ] || { bad "[${PF_NO}] 夹具 helpers/agentFakes.js 缺失"; S254_BAD=1; }
[ -f "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/test/java/spacex/astrostudy/service/AIWebSearchServiceHostileTest.java" ] || { bad "[${PF_NO}] AIWebSearchServiceHostileTest 缺失"; S254_BAD=1; }
[ "${S254_BAD}" = "0" ] && ok "[${PF_NO}] 压测二轮·稳健性债收口锁"
}

seg_255() {
# seg_255 行动能力扩展二(十二项)收口锁(2026-09-06):①标签单源+死代码清除 ②按工具名 allow/deny(deny 任何档位都拒且不进目录) ③写前 diff 预览随审批
#       ④tool.before 同步否决(E_HOOK_DENIED 零写入) ⑤流中途插话(下一轮工具回合附 [用户插话]) ⑥note_progress 进度清单(零落库)
#       ⑦/plan 先计划后执行(规划短调用只看目录摘要;三档字面锚不动) ⑧/compact <指令> + 阈值提醒(只提醒不自动压缩) ⑨分层口径(全局→命主→技法→会话)
#       ⑩按槽思考档(槽档优先) ⑪会话 resume(缺省关) ⑫/doctor(脱敏一屏诊断);三把新键登记两表;十二套回归锁在位
echo "[${PF_NO}] 行动能力扩展二(十二项)收口锁"
S255_BAD=0
S255_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S255_T="${S255_UI}/utils/__tests__"
S255_C="${S255_UI}/components/aianalysis"
S255_MAIN="$(pf_src_set "${S255_C}/AIAnalysisMain.js")"
# ① 标签单源;命令表无「待实装」死支
pf_need "${S255_UI}/utils/aiTools/labels.js" "export function toolLabel(" "labels.js 缺 toolLabel 单源"
pf_need "${S255_C}/AgentActionBar.js" "from '../../utils/aiTools/labels'" "动作条未从 labels 单源取标签"
pf_none "${S255_UI}/utils/aiChat/commands.js" "kind === 'later'" "commands.js 仍有 later 死支"
# ② 按工具名策略:键 + 判定优先级 + 目录过滤 + 面板
pf_need "${S255_UI}/utils/aiAgent/prefs.js" "export const AGENT_TOOL_POLICY_KEY = 'horosa.ai.agent.toolPolicy.v1';" "prefs 缺 toolPolicy 键"
pf_need "${S255_UI}/utils/aiAgent/prefs.js" "export const AGENT_APPROVAL_CATEGORIES = TOOL_CATEGORIES.slice();" "审批类别未取自目录类别单源(interactive 分叉)"
pf_need "${S255_UI}/utils/aiAgent/approvalPolicy.js" "export function isToolDenied(" "approvalPolicy 缺 isToolDenied"
pf_need "${S255_UI}/utils/aiAgent/runtime.js" "toolPolicy.deny.indexOf(t.name) < 0" "runtime manifest 未剔 deny 工具"
pf_need "${S255_UI}/utils/aiAgent/runtime.js" "已被用户禁用,未执行" "runtime deny 拒绝文案缺失"
pf_need "${S255_C}/AgentAbilityPanel.js" 'data-tool-policy="deny"' "能力面板缺按工具名禁用多选"
# ③ diff 预览:纯 diff + 预览组件 + 运行时超时随审批 + 三件工具 preview
pf_need "${S255_UI}/utils/aiChat/textDiff.js" "export function diffHunks(" "textDiff 缺 diffHunks"
pf_need "${S255_C}/AgentDiffPreview.js" 'data-agent-diff="1"' "AgentDiffPreview 缺机读锚"
pf_need "${S255_UI}/utils/aiAgent/runtime.js" "export const PREVIEW_TIMEOUT_MS" "runtime 预览无超时"
pf_need "${S255_UI}/utils/aiAgent/approvals.js" "preview: p.preview || null" "approvals 未把预览随待审项外露"
pf_need "${S255_UI}/utils/aiTools/registry.js" "typeof def.preview !== 'function'" "registry 未校验 preview 形状"
for t in setSettings createChartRecord createCaseRecord; do pf_need "${S255_UI}/utils/aiTools/tools/${t}.js" "preview(args" "${t} 缺 preview"; done
pf_need "${S255_C}/AgentActionBar.js" "<AgentDiffPreview" "动作条未渲染 diff 预览"
# ④ tool.before 同步否决
pf_need "${S255_UI}/utils/aiAgent/automation/events.js" "'tool.before'" "事件表缺 tool.before"
pf_need "${S255_UI}/utils/aiAgent/automation/events.js" "export function emitAutomationEventSync(" "events 缺同步通道"
pf_need "${S255_UI}/utils/aiAgent/automation/engine.js" "export function vetoDecision(" "engine 缺否决判定"
pf_need "${S255_UI}/utils/aiAgent/automation/actions.js" "'deny'" "动作表缺 deny"
pf_need "${S255_UI}/utils/aiTools/registry.js" "emitAutomationEventSync('tool.before'" "registry 执行前未发 tool.before"
pf_need "${S255_UI}/utils/aiTools/registry.js" "'E_HOOK_DENIED'" "registry 否决未回 E_HOOK_DENIED"
pf_need "${S255_UI}/utils/aiTools/errorCodes.js" "E_HOOK_DENIED" "错误码表缺 E_HOOK_DENIED"
# ⑤ 插话:队列模块 + 运行时每轮取一次 + Main 插座 + 芯片
pf_need "${S255_UI}/utils/aiAgent/steer.js" "export const STEER_PREFIX = '[用户插话]';" "steer 缺前缀常量"
pf_need "${S255_UI}/utils/aiAgent/steer.js" "export const STEER_MAX_PER_TURN = 3;" "steer 缺每轮上限"
pf_need "${S255_UI}/utils/aiAgent/runtime.js" "steerLine(" "runtime 未把插话附到请求末尾"
[ "$(pf_code -q "${S255_MAIN}" | grep -acF "steer: ()=>chatAssist.takeSteer(assistantMessage.id),")" = "1" ] || { bad "[${PF_NO}] Main createAgentTurn 插话插座不是恰一处"; S255_BAD=1; }
[ "$(pf_code -q "${S255_MAIN}" | grep -acF "}else if(chatAssist.canSteer){")" = "1" ] || { bad "[${PF_NO}] Main 回车插话分支不是恰一处"; S255_BAD=1; }
pf_need "${S255_C}/chat/ComposerAssist.js" 'data-composer-steer="1"' "ComposerAssist 缺插话芯片"
# ⑥ 进度清单
pf_need "${S255_UI}/utils/aiTools/tools/noteProgress.js" "name: 'note_progress'," "note_progress 工具缺失"
pf_need "${S255_UI}/utils/aiTools/index.js" "noteProgress" "note_progress 未进内置目录"
pf_need "${S255_UI}/utils/aiAgent/runtime.js" "state.todos = result.data.items.slice(0, 20)" "runtime 未落进度清单"
pf_need "${S255_C}/AgentActionBar.js" 'data-agent-todos="1"' "动作条缺进度清单"
pf_need "${S255_UI}/utils/aiAgent/protocol.js" "note_progress 列出步骤" "守则缺进度清单条款"
# ⑦ /plan
pf_need "${S255_UI}/utils/aiAgent/planMode.js" "export function parseActionPlan(" "planMode 缺解析"
pf_need "${S255_UI}/utils/aiAgent/planMode.js" "export const ACTION_PLAN_SCHEMA" "planMode 缺 schema"
pf_need "${S255_C}/chat/PlanCard.js" 'data-plan-approve="1"' "PlanCard 缺批准锚"
pf_need "${S255_UI}/utils/aiChat/shortCall.js" "plan: '【行动计划】'" "短调用标记缺 plan"
pf_need "${S255_UI}/utils/aiChat/commands.js" "name: 'plan'," "命令表缺 /plan"
pf_need "${S255_C}/chat/useChatAssist.js" "plan: (x)=>runPlan(x.argsText)," "useChatAssist 处理器表未分发 /plan"
# ⑧ /compact <指令> + 阈值提醒
pf_need "${S255_UI}/utils/aiChat/compact.js" "export function buildCompactSystem(" "compact 缺带指令 system"
pf_need "${S255_UI}/utils/aiChat/compactPrefs.js" "export function writeCompactAutoTokens(" "compactPrefs 缺阈值写入"
pf_need "${S255_C}/chat/useChatAssist.js" "compact: (x)=>runCompact(x.parsed.argsText)," "/compact 未传指令"
pf_need "${S255_C}/chat/ChatStatusBar.js" "'data-suggest-compact': '1'" "状态栏缺压缩提醒芯片"
pf_need "${S255_C}/chat/ChatContextPolicyPanel.js" 'data-policy-field="compactAutoTokens"' "策略卡缺阈值框"
# ⑨ 分层口径
pf_need "${S255_UI}/utils/aiChat/personaLayers.js" "export const PERSONA_LAYERS_KEY = 'horosa.ai.persona.layers.v1';" "personaLayers 缺键"
pf_need "${S255_UI}/utils/aiChat/personaLayers.js" "export function composePersonaText(" "personaLayers 缺合成"
pf_need "${S255_UI}/utils/aiChat/persona.js" "composePersonaText(p.text, ctx.layers, ctx)" "persona 层未走分层合成"
pf_need "${S255_C}/chat/PersonaMemoryPanel.js" 'data-persona-tabs="1"' "口径面板缺四页签"
pf_need "${S255_C}/chat/useChatAssist.js" "sessionText: convP ? convP.persona : ''" "useChatAssist 未接会话层"
# ⑩ 按槽思考档
pf_need "${S255_UI}/utils/aiModelRouting.js" "export const ROUTE_OPTIONS_KEY = 'horosa.ai.chat.routeOptions.v1';" "aiModelRouting 缺 routeOptions 键"
pf_need "${S255_UI}/utils/aiModelRouting.js" "export function stripThinkingOptions(" "aiModelRouting 缺剥思考键"
pf_need "${S255_C}/chat/useChatModels.js" "readRouteOptions()" "useChatModels 每轮未读槽档"
pf_need "${S255_C}/chat/ChatModelRoutesPanel.js" "data-route-thinking" "路由卡缺思考下拉"
# ⑪ resume
pf_need "${S255_UI}/utils/aiChat/resume.js" "export function pickResumeConversation(" "resume 缺挑选"
pf_need "${S255_UI}/utils/aiChat/commands.js" "name: 'resume'," "命令表缺 /resume"
pf_need "${S255_C}/chat/ChatAssistOverlays.js" 'data-resume-pref="1"' "resume 浮层缺开关"
pf_need "${S255_C}/chat/useChatAssist.js" "rememberLastConversation(convIdForResume)" "useChatAssist 未记上次对话"
# ⑫ /doctor
pf_need "${S255_UI}/utils/aiChat/doctor.js" "export function buildDoctorReport(" "doctor 缺报告"
pf_need "${S255_UI}/utils/aiChat/doctor.js" "export function redactSecrets(" "doctor 缺脱敏"
pf_need "${S255_C}/chat/DoctorPanel.js" 'data-doctor-copy="1"' "DoctorPanel 缺复制"
pf_need "${S255_C}/chat/DoctorPanel.js" "copyTextSmart" "DoctorPanel 复制未走 copyTextSmart"
pf_need "${S255_UI}/utils/aiChat/commands.js" "name: 'doctor'," "命令表缺 /doctor"
# 三把新键两表登记
for k in horosa.ai.agent.toolPolicy.v1 horosa.ai.persona.layers.v1 horosa.ai.chat.routeOptions.v1; do
  pf_need "${S255_UI}/utils/storageKeyRegistry.js" "key: '${k}'" "注册表缺 ${k}"
  pf_need "${S255_UI}/utils/techniqueOnboardingContract.js" "'${k}'" "上手合同缺 ${k}"
done
# 回归锁十二套
for f in aiAgentToolLabels aiAgentToolPolicy aiAgentDiffPreview aiAgentHookDeny aiAgentSteer aiToolsNoteProgress aiAgentPlanMode aiChatCompactInstruction aiChatPersonaLayers aiModelRoutingOptions aiChatResume aiChatDoctor; do
  [ -f "${S255_T}/${f}.test.js" ] || { bad "[${PF_NO}] 回归锁 ${f}.test.js 缺失"; S255_BAD=1; }
done
[ "${S255_BAD}" = "0" ] && ok "[${PF_NO}] 行动能力扩展二(十二项)收口锁"
}

seg_256() {
# seg_256 行动能力扩展三(六项)收口锁(2026-09-06):①web_fetch 读整页(Java 严格档守卫逐跳校验/有界/四类内容/HTML→文本/段对齐;子开关缺省关;两码)
#       ②按槽 reasoning/温度/输出上限 + 具名方案(/profile)③无头 JSON 出口 run_analysis(origins:['mcp'] 合同;只读注册表视图;内存 deps 零落库;在途 1;子开关缺省关)
#       ④stdio 本机 MCP 代理(--horosa-mcp-stdio;端点文件取令牌;有界行;-32001)+ Claude Desktop command/args 形态 ⑤并行目标任务(缺省 0=现状)⑥通知外部脚本钩(壳侧六道门/零 shell/10s/限流/HOROSA_NOTIFY_HOOK)
echo "[${PF_NO}] 行动能力扩展三(六项)收口锁"
S256_BAD=0
S256_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S256_T="${S256_UI}/utils/__tests__"
S256_C="${S256_UI}/components/aianalysis"
S256_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy"
S256_RS="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src"
# ① web_fetch:Java 严格档 + 端点 + 零日志 + 前端零直连 + 子开关 + 两码
[ -s "${S256_JAVA}/service/AIWebFetchService.java" ] || { bad "[${PF_NO}] AIWebFetchService.java 缺失"; S256_BAD=1; }
pf_need "${S256_JAVA}/service/OutboundUrlGuard.java" "public static String validateStrict(String url, boolean allowLoopback)" "守卫缺严格档"
pf_need "${S256_JAVA}/service/OutboundUrlGuard.java" 'System.getenv("HOROSA_WEBFETCH_ALLOW_LOOPBACK")' "严格档放行开关未读环境变量"
pf_need "${S256_JAVA}/service/AIWebFetchService.java" "current = OutboundUrlGuard.validateStrict(next, allowLoopback);" "重定向二跳未过严格档"
pf_need "${S256_JAVA}/service/AIWebFetchService.java" ".followRedirects(HttpClient.Redirect.NEVER)" "网页读取仍跟随重定向"
pf_need "${S256_JAVA}/service/AIWebFetchService.java" "MAX_RESPONSE_BYTES = 2L * 1024 * 1024" "网页回体无上限"
pf_need "${S256_JAVA}/service/AIWebFetchService.java" "static Truncated truncateAtParagraph(" "缺段落对齐截断"
[ "$(grep -acE 'Logger|log\.(info|debug|warn|error)' "${S256_JAVA}/service/AIWebFetchService.java")" = "0" ] || { bad "[${PF_NO}] 网页读取服务出现日志调用(地址与正文绝不落日志)"; S256_BAD=1; }
[ "$(grep -acF '"/webfetch"' "${S256_JAVA}/controller/AIAnalysisController.java")" = "1" ] || { bad "[${PF_NO}] 缺 /webfetch 端点"; S256_BAD=1; }
[ -f "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/test/java/spacex/astrostudy/service/AIWebFetchServiceTest.java" ] || { bad "[${PF_NO}] AIWebFetchServiceTest 缺失"; S256_BAD=1; }
pf_need "${S256_UI}/utils/aiTools/tools/webFetch.js" "name: 'web_fetch'," "web_fetch 工具缺失"
pf_need "${S256_UI}/utils/aiTools/tools/webFetch.js" "enabled: ()=>isWebFetchEnabled()," "web_fetch 未受子开关约束"
pf_need "${S256_UI}/utils/aiTools/tools/webFetch.js" "level: 'read'," "web_fetch 须 read 级"
[ "$(pf_code -q "${S256_UI}/integrations/webFetch.js" | grep -acE 'fetch\(|XMLHttpRequest')" = "0" ] || { bad "[${PF_NO}] 网页读取前端不得直连(一律经 Java 端点)"; S256_BAD=1; }
pf_need "${S256_UI}/services/aianalysis.js" "export function requestWebFetch(values, options)" "services 缺 requestWebFetch"
pf_need "${S256_UI}/utils/aiAgent/prefs.js" "return safeLocalStorageGet(AGENT_WEB_FETCH_KEY) === '1';" "prefs 缺网页读取开关"
pf_need "${S256_C}/WebSearchPanel.js" 'data-web-fetch-switch="1"' "面板缺网页读取开关"
for c in E_WEB_FETCH_BLOCKED E_WEB_FETCH_FAILED E_HEADLESS_UNAVAILABLE; do pf_need "${S256_UI}/utils/aiTools/errorCodes.js" "${c}" "错误码表缺 ${c}"; done
# ② 槽参数 + 具名方案
pf_need "${S256_UI}/utils/aiModelRouting.js" "export const ROUTE_SLOT_OPTION_KEYS = ['thinking', 'reasoningEffort', 'temperature', 'maxTokens'];" "槽参数四键缺失"
pf_need "${S256_UI}/utils/aiModelRouting.js" "export function applySlotParams(" "缺槽参数施加"
pf_need "${S256_UI}/utils/aiModelRouting.js" "export const ROUTE_PROFILES_KEY = 'horosa.ai.chat.routeProfiles.v1';" "缺具名方案键"
pf_need "${S256_UI}/utils/aiModelRouting.js" "export function applyRouteProfile(" "缺方案切换"
pf_need "${S256_C}/chat/ChatModelRoutesPanel.js" 'data-route-profile-save="1"' "路由卡缺另存为"
pf_need "${S256_C}/chat/ChatModelRoutesPanel.js" "data-route-max-tokens" "路由卡缺输出上限框"
pf_need "${S256_UI}/utils/aiChat/commands.js" "name: 'profile'," "命令表缺 /profile"
# ③ 无头出口
pf_need "${S256_UI}/utils/aiTools/catalog.js" "export const TOOL_CALL_ORIGINS = ['in-app', 'mcp', 'goal', 'automation', 'scheduled', 'orchestrate'];" "catalog 缺来源值域(2026-09-08 起含 orchestrate)"
pf_need "${S256_UI}/utils/aiTools/registry.js" "function originAllowed(def, origin){" "registry 缺 origins 判定"
pf_need "${S256_UI}/utils/aiTools/registry.js" "if(!originAllowed(def, ctx.origin)){" "runTool 未按 origins 拒"
pf_need "${S256_UI}/utils/aiTools/tools/runAnalysis.js" "origins: ['mcp']," "run_analysis 未限定 mcp 来源"
pf_need "${S256_UI}/utils/aiTools/tools/runAnalysis.js" "export function readOnlyRegistryView(" "无头出口缺只读注册表视图"
pf_need "${S256_UI}/utils/aiTools/tools/runAnalysis.js" "export const HEADLESS_INFLIGHT_MAX = 1;" "无头出口在途上限不是 1"
pf_none "${S256_UI}/utils/aiTools/tools/runAnalysis.js" "cid:" "run_analysis schema 不得用禁键 cid"
pf_need "${S256_UI}/utils/aiAgent/mcpBridge.js" "d.exportToolManifest({ includeExternal: false, origin: 'mcp' })" "桥 tools/list 未带 origin"
pf_need "${S256_UI}/utils/aiAgent/goalRunner.js" "...(registry ? { registry } : {})," "runHeadlessTurn 未收 registry"
pf_need "${S256_C}/ExternalAgentPanel.js" 'data-headless-switch="1"' "缺无头出口开关"
# ④ stdio 代理
[ -s "${S256_RS}/mcp_stdio.rs" ] || { bad "[${PF_NO}] mcp_stdio.rs 缺失"; S256_BAD=1; }
pf_need "${S256_RS}/mcp_stdio.rs" "pub const STDIO_LINE_MAX: usize = 1024 * 1024;" "stdio 代理行无上限"
pf_need "${S256_RS}/mcp_stdio.rs" "pub const ERR_NOT_RUNNING: i64 = -32001;" "stdio 代理缺 -32001"
pf_need "${S256_RS}/mcp_stdio.rs" "pub fn read_line_bounded" "stdio 代理缺有界行读"
pf_need "$(pf_shell_rs_prod)" "mod mcp_stdio;" "main.rs 未挂 mcp_stdio"
pf_need "$(pf_shell_rs_prod)" "args[1] == mcp_stdio::MCP_STDIO_FLAG" "main.rs 缺 stdio 旗标分派"
pf_need "${S256_RS}/mcp_server.rs" '"binaryPath": std::env::current_exe()' "status_json 缺 binaryPath"
pf_need "${S256_C}/ExternalAgentPanel.js" "args: ['--horosa-mcp-stdio', st.endpointFile]" "Claude Desktop 配置未用 stdio 形态"
pf_need "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_mcp_smoke.sh" "--horosa-mcp-stdio" "冒烟脚本缺 --stdio"
# ⑤ 并行目标
pf_need "${S256_UI}/utils/aiAgent/prefs.js" "export const AGENT_GOAL_PARALLEL_KEY = 'horosa.ai.tasks.goal.parallel';" "缺并行上限键"
pf_need "${S256_UI}/utils/aiAgent/goalRunner.js" "if(parallelLimit > 0 && runningLoops.size >= parallelLimit){" "startGoalTask 缺并行闸"
pf_need "${S256_UI}/utils/aiAgent/goalRunner.js" "export async function startNextQueuedGoal(" "缺接力起跑"
pf_need "${S256_C}/TaskCenterPanel.js" 'data-goal-start-all="1"' "任务中心缺全部开始"
# ⑥ 通知脚本钩
pf_need "$(pf_shell_rs_prod)" "fn validate_notify_hook_path_with_roots(" "壳缺脚本路径六道门"
pf_need "$(pf_shell_rs_prod)" 'std::env::var("HOROSA_NOTIFY_HOOK")' "缺 HOROSA_NOTIFY_HOOK 否决"
pf_need "$(pf_shell_rs_prod)" "Command::new(path)" "通知脚本须零 shell 直起"
pf_need "$(pf_shell_rs_prod)" "pub const NOTIFY_HOOK_TIMEOUT_MS: u64 = 10_000;" "通知脚本超时不是 10s"
pf_need "$(pf_shell_rs_prod)" "notify_hook_run_command," "main.rs 未登记通知脚本命令"
pf_need "${S256_UI}/utils/aiAgent/automation/actions.js" "'notify-script'" "动作表缺 notify-script"
pf_need "${S256_C}/ExternalAgentPanel.js" "Modal.confirm({ title: '启用通知脚本钩?'" "通知脚本钩首次启用缺确认"
# 四把新键两表登记
for k in horosa.ai.tools.webFetch.enabled horosa.ai.tools.headless.enabled horosa.ai.tasks.goal.parallel horosa.ai.chat.routeProfiles.v1; do
  pf_need "${S256_UI}/utils/storageKeyRegistry.js" "key: '${k}'" "注册表缺 ${k}"
  pf_need "${S256_UI}/utils/techniqueOnboardingContract.js" "'${k}'" "上手合同缺 ${k}"
done
# 回归锁
for f in aiToolsWebFetch aiModelRoutingProfiles aiToolsHeadless aiAgentGoalParallel aiAgentNotifyHook; do
  [ -f "${S256_T}/${f}.test.js" ] || { bad "[${PF_NO}] 回归锁 ${f}.test.js 缺失"; S256_BAD=1; }
done
[ "${S256_BAD}" = "0" ] && ok "[${PF_NO}] 行动能力扩展三(六项)收口锁"
}

seg_310() {
echo "[${PF_NO}] AI 对话双盘挂载(本人 + 合盘对方):分层与归属 / 公平裁剪 / @ 第二张命盘 / 检查点 / /合盘 / 编排子回合 / 页面接线 / 起盘签名日期归一 / 测试在位"
S310_BAD=0
S310_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
# 判据 = 「文件|必含字面量」(grep -F);任何一处被拆,对方的盘就会静默不挂、只挂一半或挂成本人的盘。
s310_scan(){
  pf_scan_table "$1" <<'S310_EOF'
utils/aiAnalysisContext.js|export function pairDisplayName(title, fallback){
utils/aiAnalysisContext.js|key: 'pair-rule',
utils/aiAnalysisContext.js|key: 'partner-source',
utils/aiAnalysisContext.js|key: `technique:${item.key || idx}@partner`,
utils/aiAnalysisContext.js|const PAIR_SOURCE_KEYS = { source: 1, 'partner-source': 1 };
utils/aiAnalysisContext.js|.replace('T', ' ').replace(/\//g, '-')
utils/aiChat/mentions.js|plan.partnerSource = r.hit;
utils/aiChat/checkpoint.js|'chatTopP', 'partnerSourceId'];
utils/aiChat/checkpoint.js|call(s.setPartnerSourceId,
utils/aiChat/skills.js|export function shouldAttachWesternSynastry(techniqueKeys){
utils/aiChat/commands.js|(c.argsText || c.partnerSource)
components/aianalysis/AIAnalysisMain.js|partnerForPrompt.synastry = await getPairSynastryText(currentSource.record, pairSource.record, { optionsA: optsThisTurn, optionsB: pairOpts });
utils/aiAgent/goalRunner.js|if(shouldAttachWesternSynastry(keys)){ partner.synastry = await getPairSynastryText(source.record, partnerSource.record, { optionsA: techniqueOptions, optionsB: popts }); }
utils/aiAnalysisContext.js|key: 'pair:synastry',
utils/aiAnalysisContext.js|const pairDataInSourceSplit = !hasTechnique && nonEmpty.some((item)=>item.key === 'partner-source');
utils/aiAnalysisContext.js|export async function getPairSynastryText(recordA0, recordB0, opts = {}){
utils/pairChineseData.js|export function buildBaziHehunText(selfParams, otherParams, { selfName = '本人', otherName = '对方' } = {}){
utils/pairChineseData.js|export function buildZiweiPairText(self, other, { selfName = '本人', otherName = '对方' } = {}){
utils/aiAnalysisContext.js|export function getPairChineseTexts(recordA, recordB, techniqueKeys, names = {}, pairOpts = {}){
utils/aiAnalysisContext.js|key: 'pair:bazi-hehun',
components/aianalysis/AIAnalysisMain.js|if(chinese.bazi || chinese.ziwei){ partnerForPrompt.chinese = chinese; }
utils/aiAgent/goalRunner.js|if(chinese.bazi || chinese.ziwei){ partner.chinese = chinese; }
utils/__tests__/aiPairChineseData.test.js|年命 / 日柱夫妻宫 / 喜忌互补三段齐
utils/pairChineseData.js|export function ganRelations(a, b){
utils/pairChineseData.js|lines.push(palaceInto(b, a, '对方', '本人'));
utils/pairChineseData.js|const forms = crossBranchFormations(branchItemsOf(a), branchItemsOf(b));
utils/baziLunarLocal.js|export function pairBranchRelations(a, b){
utils/baziLunarLocal.js|export function crossBranchFormations(listA, listB){
utils/__tests__/aiPairChineseData.test.js|地支 12×12 逐对:六冲 / 六合 / 三合 / 相刑 / 自刑 / 六害 与古法表一致
utils/__tests__/aiPairChineseData.test.js|样例三 壬申 癸卯 壬午 甲辰 × 丙子 庚子 壬午 庚子
utils/__tests__/aiPairChinesePalaceByBranch.test.js|宫位数组整体转个位置(命宫 / 身宫下标随之),四化入宫与命身互落逐字不变
utils/__tests__/aiChatPairMount.test.js|按「这一对」缓存:同一对只算一次;并发两次合成一次;换人重算;空结果不缓存
components/aianalysis/chat/useChatAssist.js|d.setPartnerSourceId(plan.partnerSource.id);
components/aianalysis/chat/useChatAssist.js|const st = requirementState(cmd.requires, { activeSource: effSource, argsText, partnerSource: effPartner });
components/aianalysis/chat/useChatOrchestrate.js|partnerSource: d.partnerSource });
utils/aiAgent/goalRunner.js|partner = { title: partnerSource.title, sourceContext: pctx, techniqueContexts: ptechs };
components/aianalysis/AIAnalysisMain.js|const [partnerSourceId, setPartnerSourceId] = React.useState('');
components/aianalysis/AIAnalysisMain.js|partner: partnerForPrompt,
components/aianalysis/AIAnalysisMain.js|partnerRef: pairForRecord ? {
components/aianalysis/AIAnalysisMain.js|data-pair-mount-section="1"
components/aianalysis/AIAnalysisMain.js|data-pair-chip="1"
components/aianalysis/AIAnalysisMain.js|snapshotSourceMismatch(item.meta, (item.partner ?
utils/__tests__/aiChatPairMount.test.js|不给对方 / 对方为空 → 与此前单盘逐字节相同
utils/__tests__/aiChatPairMount.test.js|对方技法层算技法层:预算紧时两人一起按水位裁,不会只丢对方
utils/__tests__/aiChatPairMountHeadless.test.js|给合盘对方 → 两人的技法层都在且注明归属;不给 / 本人 / 事盘 → 单盘逐字节相同
utils/__tests__/aiMountHealth.test.js|起盘签名的「1990/05/18」与记录的「1990-05-18」是同一天
S310_EOF
}
S310_MISS="$(s310_scan "${S310_UI}")"
[ -z "${S310_MISS}" ] || { printf '%s\n' "${S310_MISS}" | head -6 | sed 's/^/    缺 /'; bad "[${PF_NO}]① 双盘挂载接线被拆($(printf '%s\n' "${S310_MISS}" | wc -l | tr -d ' ') 处)"; S310_BAD=1; }
# ② 判别力自证:拷一份判据涉及的文件,原样必须全过,拆掉检查点字段 / 对方案例前提层后必须各自报出
s310_tmp="$(mktemp -d "${PF_TMP}/s310_tmp.XXXXXX")"
for s310_f in $(s310_scan /nonexistent | sed 's/「.*$//' | sort -u); do
  mkdir -p "${s310_tmp}/$(dirname "${s310_f}")" && cp "$(pf_src_set "${S310_UI}/${s310_f}")" "${s310_tmp}/${s310_f}" 2>/dev/null
done
s310_ok=1
[ -z "$(s310_scan "${s310_tmp}")" ] || s310_ok=0
sed -i '' "s/'chatTopP', 'partnerSourceId'\]/'chatTopP']/" "${s310_tmp}/utils/aiChat/checkpoint.js" 2>/dev/null
s310_scan "${s310_tmp}" | pipe_has -F 'utils/aiChat/checkpoint.js' || s310_ok=0
sed -i '' "s/key: 'partner-source',/key: 'source-b',/" "${s310_tmp}/utils/aiAnalysisContext.js" 2>/dev/null
s310_scan "${s310_tmp}" | pipe_has -F "key: 'partner-source'," || s310_ok=0
rm -rf "${s310_tmp}"
[ "${s310_ok}" = "1" ] || { bad "[${PF_NO}]② 判别力自证失败(原样不全过,或拆掉检查点字段 / 对方案例前提层后没报出)"; S310_BAD=1; }
[ "${S310_BAD}" = "0" ] && ok "[${PF_NO}] AI 对话双盘挂载:分层归属 / 公平裁剪 / @ 第二张命盘 / 检查点 / /合盘 / 编排子回合 / 页面接线 / 签名日期归一 / 测试在位;判别力自证"
}

seg_311() {
echo "[${PF_NO}] AI 对话斜杠命令:参数里的 @ 同一解析器 / 找人单源 / 年份规整 / /help / 命令表即处理器表 / 本轮请求(技能技法只作用本轮)/ 参数补全 / 命令芯片"
S311_BAD=0
S311_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
# 判据 = 「文件|必含字面量」(grep -F):任何一处被拆,技能又会把会话挂载整个换掉、/流年 @张三 的标记进提示词、/合盘 找人与 @ 分叉、命令名单又分三处手抄。
s311_scan(){
  pf_scan_table "$1" <<'S311_EOF'
utils/aiChat/mentions.js|export function resolveSourceByName(sources, name, suffix){
utils/aiChat/mentions.js|const partnerOnly = !!(opts && opts.twoCharts)
utils/aiChat/skills.js|export function normalizeYearArg(value, now){
utils/aiChat/skills.js|default: '今年', type: 'year' }],
utils/aiChat/commands.js|{ name: 'help', aliases: ['帮助', '?', '？'],
utils/aiChat/commands.js|export const COMMANDS_ALLOWED_WHILE_SENDING = BUILTIN_COMMANDS.filter((c)=>c.allowWhileSending).map((c)=>c.name);
utils/aiChat/commands.js|export function listCommandArgItems({ cmd, argsText, ctx } = {}){
utils/aiChat/turnRequest.js|export function normalizeTurnRequest(raw){
utils/aiChat/turnRequest.js|export function turnTechniqueKeysFor(turn, sessionKeys, allowedKeys){
components/aianalysis/chat/useChatAssist.js|const planMentions = React.useCallback((mentions, opts = {})=>{
components/aianalysis/chat/useChatAssist.js|if((cmd.mentions || cmd.kind === 'skill') && argsText){
components/aianalysis/chat/useChatAssist.js|const r = resolveSourceByName(pool, q, '');
components/aianalysis/chat/useChatAssist.js|const handler = commandHandlersRef.current[cmd.name];
components/aianalysis/chat/useChatAssist.js|help: (x)=>{ setHelpState({ open: true, focus: x.argsText }); return true; },
components/aianalysis/chat/useChatAssist.js|d.applyBundle(bundle, { skipTechniques: true })
components/aianalysis/chat/useChatAssist.js|await send(promptText, extra || undefined, turn || undefined);
components/aianalysis/chat/useChatAssist.js|commandHandlerNames: Object.keys(commandHandlersRef.current),
components/aianalysis/chat/ChatAssistOverlays.js|function HelpPanel({ help }){
components/aianalysis/chat/ComposerAssist.js|data-composer-assist="args"
components/aianalysis/chat/UserTurnBody.js|data-turn-keep="1"
components/aianalysis/AIAnalysisMain.js|const turnScope = turnTechniqueKeysFor(turn, activeTechniqueKeys,
components/aianalysis/AIAnalysisMain.js|turn: turn || undefined,
components/aianalysis/AIAnalysisMain.js|{chatAssist.userTurnContent(item)}
components/aianalysis/AIAnalysisMain.js|if(!(opts && opts.skipTechniques) && Array.isArray(bundle.defaultTechniqueKeys)
utils/aiConversationBranch.js|function editedTurnOf(targetUser, content){
utils/__tests__/aiChatCommandArgs.test.js|/流年 @[命盘:李四] 2027年 → 切到李四、模板里是「李四在 2027 年」,不含原始标记
utils/__tests__/aiChatCommandArgs.test.js|命令表即处理器表:非技能内置命令都有处理器、处理器没有多余的
utils/__tests__/aiChatTurnRequest.test.js|编辑过正文的命令轮去掉命令芯片、保留本轮技法
utils/__tests__/aiChatComposer.test.js|技法 bazi+ziwei 只作用本轮(本轮请求,不改会话挂载)
S311_EOF
}
S311_MISS="$(s311_scan "${S311_UI}")"
[ -z "${S311_MISS}" ] || { printf '%s\n' "${S311_MISS}" | head -6 | sed 's/^/    缺 /'; bad "[${PF_NO}]① 斜杠命令接线被拆($(printf '%s\n' "${S311_MISS}" | wc -l | tr -d ' ') 处)"; S311_BAD=1; }
# ② 判别力自证:拷判据涉及的文件,原样全过;拆掉本轮请求规整 / 套组合跳过技法后各自报出
s311_tmp="$(mktemp -d "${PF_TMP}/s311_tmp.XXXXXX")"
for s311_f in $(s311_scan /nonexistent | sed 's/「.*$//' | sort -u); do
  mkdir -p "${s311_tmp}/$(dirname "${s311_f}")" && cp "$(pf_src_set "${S311_UI}/${s311_f}")" "${s311_tmp}/${s311_f}" 2>/dev/null
done
s311_ok=1
[ -z "$(s311_scan "${s311_tmp}")" ] || s311_ok=0
sed -i '' "s/export function normalizeTurnRequest(raw){/function normalizeTurnRequestX(raw){/" "${s311_tmp}/utils/aiChat/turnRequest.js" 2>/dev/null
s311_scan "${s311_tmp}" | pipe_has -F 'export function normalizeTurnRequest(raw){' || s311_ok=0
sed -i '' "s/d.applyBundle(bundle, { skipTechniques: true })/d.applyBundle(bundle)/" "${s311_tmp}/components/aianalysis/chat/useChatAssist.js" 2>/dev/null
s311_scan "${s311_tmp}" | pipe_has -F 'd.applyBundle(bundle, { skipTechniques: true })' || s311_ok=0
rm -rf "${s311_tmp}"
[ "${s311_ok}" = "1" ] || { bad "[${PF_NO}]② 判别力自证失败(原样不全过,或拆掉本轮请求规整 / 套组合跳过技法后没报出)"; S311_BAD=1; }
[ "${S311_BAD}" = "0" ] && ok "[${PF_NO}] AI 对话斜杠命令:@ 同一解析器 / 找人单源 / 年份规整 / /help / 处理器表 / 本轮请求 / 参数补全 / 命令芯片;判别力自证"
}

seg_312() {
echo "[${PF_NO}] AI 调用链:系统提示词拼装单源(对话页 + 无头)/ 辅助短调用走「辅助」槽 / 双盘快照重算缓存 / 单例覆盖类技法排队"
S312_BAD=0
S312_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
# 判据 = 「文件|必含字面量」(grep -F):拆掉任一处,无头与页面的 system 又会各写一份而漂移、压缩 / 起标题又按最贵的主模型算、
#   双盘时两人轮流重算快照、紫微 / 七政的临时全局覆盖在两次构造之间交错。
s312_scan(){
  pf_scan_table "$1" <<'S312_EOF'
utils/aiPromptAssembly.js|export function assembleSystemPrompt({ layers, maxChars, providerType, breakpointWhenNoVolatile = false, tailInstruction = '' } = {}){
utils/aiPromptAssembly.js|clip.kept.filter((item)=>!VOLATILE_LAYER_KEYS[item.key])
components/aianalysis/AIAnalysisMain.js|const assembled = assembleSystemPrompt({ layers, maxChars: ctxCharBudget,
utils/aiAgent/goalRunner.js|const assembled = assembleSystemPrompt({ layers,
utils/aiModelRouting.js|export const ROUTE_SLOTS = ['toolRounds', 'final', 'judge', 'review', 'planner', 'subagent', 'utility'];
utils/aiChat/shortCall.js|export async function requestShortCompletion({ profile, model, kind, system, user, timeoutMs, signal, slot, providerProfiles }){
components/aianalysis/chat/useChatAssist.js|kind: 'compact', system: buildCompactSystem(instruction), user: input.text, timeoutMs: 60000, slot: 'utility',
components/aianalysis/AIAnalysisMain.js|const titleRoute = resolveRoute('utility', { routes: readModelRoutes(), providerProfiles, profile, model });
utils/aiAnalysisContext.js|const regenKey = regeneratedSnapshotKey(key, record);
utils/aiAnalysisContext.js|export function withSerialTechniqueBuild(key, fn){
utils/aiAnalysisContext.js|context = await withSerialTechniqueBuild(k, ()=>(overrideOpts
components/ziwei/ZiWeiMain.js|const run = zwSnapshotChain.then(()=>buildZiweiSnapshotForParamsSerial(params));
utils/__tests__/aiPromptAssembly.test.js|对话页:家族 × 历史模式 × 层组合 × 预算(含丢层)× JSON 尾句
utils/__tests__/aiPairSnapshotCache.test.js|本人 / 对方轮流取八字:各自只重算一次,内容各是各的;换了记录(改生辰)就重算
utils/__tests__/aiSerialTechniqueBuild.test.js|紫微快照构造器排队:两次并发构造各自用自己的四化流派发请求,结束后全局流派复原
utils/__tests__/aiChatShortCall.test.js|「辅助」槽:槽空 = 用传入的档案 / 模型、选项逐字节同不给槽
S312_EOF
}
S312_MISS="$(s312_scan "${S312_UI}")"
[ -z "${S312_MISS}" ] || { printf '%s\n' "${S312_MISS}" | head -6 | sed 's/^/    缺 /'; bad "[${PF_NO}]① AI 调用链接线被拆($(printf '%s\n' "${S312_MISS}" | wc -l | tr -d ' ') 处)"; S312_BAD=1; }
# ② 判别力自证:拷判据涉及的文件,原样全过;拆掉无头接拼装单源 / 紫微构造器排队后各自报出
s312_tmp="$(mktemp -d "${PF_TMP}/s312_tmp.XXXXXX")"
for s312_f in $(s312_scan /nonexistent | sed 's/「.*$//' | sort -u); do
  mkdir -p "${s312_tmp}/$(dirname "${s312_f}")" && cp "$(pf_src_set "${S312_UI}/${s312_f}")" "${s312_tmp}/${s312_f}" 2>/dev/null
done
s312_ok=1
[ -z "$(s312_scan "${s312_tmp}")" ] || s312_ok=0
sed -i '' "s/const assembled = assembleSystemPrompt({ layers,/const assembled = assembleSystemPromptX({ layers,/" "${s312_tmp}/utils/aiAgent/goalRunner.js" 2>/dev/null
s312_scan "${s312_tmp}" | pipe_has -F 'utils/aiAgent/goalRunner.js' || s312_ok=0
sed -i '' "s/zwSnapshotChain.then(()=>buildZiweiSnapshotForParamsSerial(params))/Promise.resolve().then(()=>buildZiweiSnapshotForParamsSerial(params))/" "${s312_tmp}/components/ziwei/ZiWeiMain.js" 2>/dev/null
s312_scan "${s312_tmp}" | pipe_has -F 'components/ziwei/ZiWeiMain.js' || s312_ok=0
rm -rf "${s312_tmp}"
[ "${s312_ok}" = "1" ] || { bad "[${PF_NO}]② 判别力自证失败(原样不全过,或拆掉无头拼装单源 / 紫微构造器排队后没报出)"; S312_BAD=1; }
[ "${S312_BAD}" = "0" ] && ok "[${PF_NO}] AI 调用链:拼装单源(页面 + 无头)/ 辅助槽 / 双盘快照重算缓存 / 单例覆盖技法排队;判别力自证"
}

seg_317() {
echo "[${PF_NO}] 本机 REST 接口 /api/v1:同一服务同一令牌同一道门(门先于子开关)/ 子开关缺省关(壳偏好 + 面板首开确认)/ 调用方名 rest / 事件流进度 / OpenAPI 现生成"
S317_BAD=0
# 判据 = 「仓内路径|必含字面量」(grep -F):拆掉任一处,REST 要么缺省就开着(装上即可被本机任意持令牌程序按 HTTP 调写入工具)、
#   要么绕过了 MCP 那一道门 / 页面策略(调用方名丢了 = 审批与限流桶串到别的客户端),要么面板开关成了死开关(偏好不落 / 启动不回灌)。
s317_scan(){
  pf_scan_table "$1" <<'S317_EOF'
Horosa_Desktop_Installer/src-tauri/src/rest_api.rs|pub const REST_PREFIX: &str = "/api/v1";
Horosa_Desktop_Installer/src-tauri/src/rest_api.rs|pub const REST_CLIENT_NAME: &str = "rest";
Horosa_Desktop_Installer/src-tauri/src/rest_api.rs|if let Err((status, msg)) = core.gate(
Horosa_Desktop_Installer/src-tauri/src/rest_api.rs|if !core.rest_enabled() {
Horosa_Desktop_Installer/src-tauri/src/rest_api.rs|let mut meta = json!({ "clientName": REST_CLIENT_NAME });
Horosa_Desktop_Installer/src-tauri/src/rest_api.rs|cancel_on_disconnect: true,
Horosa_Desktop_Installer/src-tauri/src/rest_api.rs|"openapi": "3.1.0",
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|rest_enabled: AtomicBool::new(false),
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|crate::rest_api::handle(core, dispatcher, request);
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|core.set_rest_enabled(inner.rest_enabled);
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|"restEnabled": inner.as_ref().map(|i| i.rest_enabled).unwrap_or(false),
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|fn rest_api_end_to_end_gate_switch_routes_and_shapes()
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|fn rest_api_tool_call_streams_progress_then_result()
Horosa_Desktop_Installer/src-tauri/src/main.rs|mod rest_api;
Horosa_Desktop_Installer/src-tauri/src/config.rs|mcp_rest_enabled: false,
Horosa_Desktop_Installer/src-tauri/src/config.rs|next.mcp_rest_enabled = current.mcp_rest_enabled;
Horosa_Desktop_Installer/src-tauri/src/main.rs|mcp_server::apply_rest_enabled(&state, prefs.mcp_rest_enabled);
Horosa_Desktop_Installer/src-tauri/src/main.rs|mcp_server_set_rest_enabled_command,
Horosa-Web/astrostudyui/src/utils/aiAnalysisDesktop.js|invokeOptional('mcp_server_set_rest_enabled_command', { enabled: !!enabled })
Horosa-Web/astrostudyui/src/components/aianalysis/ExternalAgentPanel.js|data-mcp-rest-switch="1"
Horosa-Web/astrostudyui/src/components/aianalysis/ExternalAgentPanel.js|disabled={!status.available || !enabled || busy} loading={busy} onChange={onToggleRest}
Horosa-Web/astrostudyui/src/components/aianalysis/ExternalAgentPanel.js|Modal.confirm({ title: '开启本机 REST 接口?'
Horosa-Web/astrostudyui/src/utils/__tests__/aiToolsRestPanel.test.js|点开先弹确认;确认后才调壳命令
S317_EOF
}
# 门先于子开关:handle() 里 core.gate( 必须出现在 core.rest_enabled() 之前(否则无令牌方能从 403 / 401 之差探出开关状态)
s317_order(){
  local f="$1/Horosa_Desktop_Installer/src-tauri/src/rest_api.rs" g r
  g="$(grep -nF 'if let Err((status, msg)) = core.gate(' "${f}" 2>/dev/null | head -1 | cut -d: -f1)"
  r="$(grep -nF 'if !core.rest_enabled() {' "${f}" 2>/dev/null | head -1 | cut -d: -f1)"
  { [ -n "${g}" ] && [ -n "${r}" ] && [ "${g}" -lt "${r}" ]; } || echo "rest_api.rs「门须先于子开关判定」"
}
S317_MISS="$(s317_scan "${REPO_ROOT}"; s317_order "${REPO_ROOT}")"
[ -z "${S317_MISS}" ] || { printf '%s\n' "${S317_MISS}" | head -6 | sed 's/^/    缺 /'; bad "[${PF_NO}]① 本机 REST 接口接线被拆($(printf '%s\n' "${S317_MISS}" | wc -l | tr -d ' ') 处)"; S317_BAD=1; }
# ② 判别力自证:拷判据涉及的文件,原样全过;缺省翻开 / 去掉开关判定 / 调换门与开关先后 / 拆掉转入各自报出
s317_tmp="$(mktemp -d "${PF_TMP}/s317_tmp.XXXXXX")"
for s317_f in $(s317_scan /nonexistent | sed 's/「.*$//' | sort -u); do
  mkdir -p "${s317_tmp}/$(dirname "${s317_f}")" && cp "$(pf_src_set "${REPO_ROOT}/${s317_f}")" "${s317_tmp}/${s317_f}" 2>/dev/null
done
s317_ok=1
[ -z "$(s317_scan "${s317_tmp}"; s317_order "${s317_tmp}")" ] || s317_ok=0
sed -i '' 's/rest_enabled: AtomicBool::new(false),/rest_enabled: AtomicBool::new(true),/' "${s317_tmp}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs" 2>/dev/null
s317_scan "${s317_tmp}" | pipe_has -F 'mcp_server.rs「rest_enabled: AtomicBool::new(false)' || s317_ok=0
sed -i '' 's/    if !core.rest_enabled() {/    if false {/' "${s317_tmp}/Horosa_Desktop_Installer/src-tauri/src/rest_api.rs" 2>/dev/null
s317_scan "${s317_tmp}" | pipe_has -F 'rest_api.rs「if !core.rest_enabled() {' || s317_ok=0
{ echo '    if !core.rest_enabled() {'; cat "${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/rest_api.rs"; } > "${s317_tmp}/Horosa_Desktop_Installer/src-tauri/src/rest_api.rs"
s317_order "${s317_tmp}" | pipe_has -F '门须先于子开关判定' || s317_ok=0
sed -i '' 's/crate::rest_api::handle(core, dispatcher, request);/let _ = request;/' "${s317_tmp}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs" 2>/dev/null
s317_scan "${s317_tmp}" | pipe_has -F 'mcp_server.rs「crate::rest_api::handle' || s317_ok=0
rm -rf "${s317_tmp}"
[ "${s317_ok}" = "1" ] || { bad "[${PF_NO}]② 判别力自证失败(原样不全过,或缺省翻开 / 去掉开关判定 / 门与开关调换先后 / 拆掉转入后没报出)"; S317_BAD=1; }
[ "${S317_BAD}" = "0" ] && ok "[${PF_NO}] 本机 REST 接口:同一道门且门先于子开关 / 子开关缺省关(偏好落盘 + 启动回灌 + 首开确认)/ 调用方名 rest / 事件流可取消;判别力自证"
}

seg_318() {
echo "[${PF_NO}] 终端命令 --horosa-cli:建窗口之前分流且恒退出(绝不拉起界面)/ 调用方名 cli / Ctrl-C 发取消通知 / 终端命令垫片只碰自己写的文件"
S318_BAD=0
# 判据 = 「仓内路径|必含字面量」(grep -F):拆掉任一处,终端命令要么落到拉起界面(屏幕上出窗口)、要么审批与限流串到别的客户端、
#   要么 Ctrl-C 只停了终端而星阙里的调用照跑、要么「安装终端命令」覆盖 / 删除用户自己的同名文件。
s318_scan(){
  pf_scan_table "$1" <<'S318_EOF'
Horosa_Desktop_Installer/src-tauri/src/main.rs|mod horosa_cli;
Horosa_Desktop_Installer/src-tauri/src/main.rs|if args.len() >= 2 && args[1] == horosa_cli::CLI_FLAG {
Horosa_Desktop_Installer/src-tauri/src/main.rs|std::process::exit(horosa_cli::run_cli(&args[2..]));
Horosa_Desktop_Installer/src-tauri/src/main.rs|cli_shim_install_command,
Horosa_Desktop_Installer/src-tauri/src/horosa_cli.rs|pub const CLI_CLIENT_NAME: &str = "cli";
Horosa_Desktop_Installer/src-tauri/src/horosa_cli.rs|let mut meta = json!({ "clientName": CLI_CLIENT_NAME });
Horosa_Desktop_Installer/src-tauri/src/horosa_cli.rs|"method": "notifications/cancelled"
Horosa_Desktop_Installer/src-tauri/src/horosa_cli.rs|conn.cancel(&id);
Horosa_Desktop_Installer/src-tauri/src/horosa_cli.rs|INTERRUPTED.store(true, Ordering::SeqCst);
Horosa_Desktop_Installer/src-tauri/src/horosa_cli.rs|已存在且不是星阙写的,不覆盖
Horosa_Desktop_Installer/src-tauri/src/horosa_cli.rs|不是星阙写的,不删
Horosa_Desktop_Installer/src-tauri/src/horosa_cli.rs|fn shim_install_refuses_foreign_and_round_trips()
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|fn cli_progress_lines_and_ctrl_c_cancels_the_call_in_the_page()
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|fn cli_end_to_end_status_tools_call_read_prompts_and_bad_token()
Horosa-Web/astrostudyui/src/utils/aiAnalysisDesktop.js|invokeOptional('cli_shim_install_command')
Horosa-Web/astrostudyui/src/components/aianalysis/ExternalAgentPanel.js|data-cli-shim="install"
Horosa-Web/astrostudyui/src/components/aianalysis/ExternalAgentPanel.js|Modal.confirm({ title: '安装终端命令 horosa?'
Horosa-Web/astrostudyui/src/utils/__tests__/aiToolsCliPanel.test.js|安装先弹确认(写明路径),确认后才调壳
S318_EOF
}
# 分流必须在建窗口之前:main.rs 里 CLI 分支所在行须早于 tauri::Builder::default()
s318_order(){
  local f="$1/Horosa_Desktop_Installer/src-tauri/src/main.rs" c b
  c="$(grep -nF 'args[1] == horosa_cli::CLI_FLAG' "${f}" 2>/dev/null | head -1 | cut -d: -f1)"
  b="$(grep -nF 'tauri::Builder::default()' "${f}" 2>/dev/null | head -1 | cut -d: -f1)"
  { [ -n "${c}" ] && [ -n "${b}" ] && [ "${c}" -lt "${b}" ]; } || echo "main.rs「终端命令分流须在建窗口之前」"
}
S318_MISS="$(s318_scan "${REPO_ROOT}"; s318_order "${REPO_ROOT}")"
[ -z "${S318_MISS}" ] || { printf '%s\n' "${S318_MISS}" | head -6 | sed 's/^/    缺 /'; bad "[${PF_NO}]① 终端命令接线被拆($(printf '%s\n' "${S318_MISS}" | wc -l | tr -d ' ') 处)"; S318_BAD=1; }
# ② 判别力自证:拷判据涉及的文件,原样全过;分流挪到建窗口之后 / 去掉取消通知 / 垫片去掉拒外来各自报出
s318_tmp="$(mktemp -d "${PF_TMP}/s318_tmp.XXXXXX")"
for s318_f in $(s318_scan /nonexistent | sed 's/「.*$//' | sort -u); do
  mkdir -p "${s318_tmp}/$(dirname "${s318_f}")" && cp "$(pf_src_set "${REPO_ROOT}/${s318_f}")" "${s318_tmp}/${s318_f}" 2>/dev/null
done
s318_ok=1
[ -z "$(s318_scan "${s318_tmp}"; s318_order "${s318_tmp}")" ] || s318_ok=0
{ echo '    tauri::Builder::default()'; cat "${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"; } > "${s318_tmp}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
s318_order "${s318_tmp}" | pipe_has -F '终端命令分流须在建窗口之前' || s318_ok=0
sed -i '' 's/            conn.cancel(&id);/            let _ = \&id;/' "${s318_tmp}/Horosa_Desktop_Installer/src-tauri/src/horosa_cli.rs" 2>/dev/null
s318_scan "${s318_tmp}" | pipe_has -F 'horosa_cli.rs「conn.cancel(&id);' || s318_ok=0
sed -i '' 's/已存在且不是星阙写的,不覆盖/已存在/' "${s318_tmp}/Horosa_Desktop_Installer/src-tauri/src/horosa_cli.rs" 2>/dev/null
s318_scan "${s318_tmp}" | pipe_has -F '已存在且不是星阙写的' || s318_ok=0
rm -rf "${s318_tmp}"
[ "${s318_ok}" = "1" ] || { bad "[${PF_NO}]② 判别力自证失败(原样不全过,或分流挪到建窗口之后 / 去掉取消通知 / 垫片去掉拒外来后没报出)"; S318_BAD=1; }
[ "${S318_BAD}" = "0" ] && ok "[${PF_NO}] 终端命令:建窗口之前分流且恒退出 / 调用方名 cli / Ctrl-C 取消到页面 / 垫片只碰自己写的文件;判别力自证"
}

seg_319() {
echo "[${PF_NO}] 无头模式(不开 App):工具层同源打包 / 浏览器路径零影响的落盘钩子 / 界面类不进无头目录 / 门与令牌 / AI 直接接入(.mcp.json · ./horosa)/ 批量验证与单例同一函数 / 合同与真栈自测"
S319_BAD=0
# 判据 = 「仓内路径|必含字面量」(grep -F):拆掉任一处,要么无头工具层与桌面分叉(另写一套 = 两边漂移),要么浏览器 / 桌面被落盘钩子带偏,
#   要么界面类工具在无头下挂着等不来的界面,要么本机服务不设门,要么 AI 拿到仓库接不上。
s319_scan(){
  pf_scan_table "$1" <<'S319_EOF'
Horosa-Web/astrostudyui/headless/entry.js|export { handleAgentToolRequest } from '../src/utils/aiAgent/mcpBridge';
Horosa-Web/astrostudyui/headless/runtime.js|const HEADLESS_UNAVAILABLE_NAMES = ['read_current_page', 'load_record_into_workspace', 'ask_user', 'set_chat_mount'];
Horosa-Web/astrostudyui/headless/runtime.js|const unavailable = (t)=>!!t && (t.category === 'ui' || HEADLESS_UNAVAILABLE_NAMES.indexOf(t.name) >= 0);
Horosa-Web/astrostudyui/headless/runtime.js|return lib.handleAgentToolRequest(req, undefined, extra && extra.ctx ? extra.ctx : undefined);
Horosa-Web/astrostudyui/headless/runtime.js|globalThis.__HOROSA_HEADLESS_STORE__ = {
Horosa-Web/astrostudyui/src/utils/aiAnalysisStore.js|if(!hook || typeof hook.load !== 'function' || typeof hook.save !== 'function'){ return new Map(); }
Horosa-Web/astrostudyui/headless/server.js|if(!m || !constantTimeEq(m[1].trim(), token)){ return [401, 'missing or invalid bearer token']; }
Horosa-Web/astrostudyui/headless/server.js|if(req.headers.host !== undefined && !isLoopbackAuthority(req.headers.host)){ return [403, 'forbidden host']; }
Horosa-Web/astrostudyui/headless/server.js|server.listen(port, '127.0.0.1');
Horosa-Web/astrostudyui/headless/protocol.js|const DENIED_NAME_WORDS = ['delete', 'remove', 'purge', 'clear', 'reset', 'overwrite', 'update', 'rename', 'import', 'export', 'restore', 'undo'];
Horosa-Web/astrostudyui/headless/cli.js|method: 'notifications/cancelled', params: { requestId: id, reason: '用户在终端按了 Ctrl-C' }
Horosa-Web/astrostudyui/headless/cli.js|if(!(await humanConfirm(opts, `确认${verb}提案 ${id}?`))){ return EXIT.USAGE; }
Horosa-Web/astrostudyui/headless/cli.js|if(opts.yes && process.env[UNATTENDED_ENV] === '1'){ return true; }
Horosa-Web/astrostudyui/headless/cli.js|fs.linkSync(tmp, file);
Horosa-Web/astrostudyui/src/utils/__tests__/headlessApi.test.js|与桌面壳逐项对拍
Horosa-Web/astrostudyui/headless/test/server.test.js|Ctrl-C:在途调用 → 发取消通知 → 服务端中止 → 回 130
Horosa-Web/astrostudyui/headless/selftest.js|check('界面类工具不进无头目录'
Horosa-Web/astrostudyui/headless/build.js|b.onResolve({ filter: /^opencc-js\/dist\/umd\/[a-z0-9]+\.js$/ }, (a)=>({ path: path.join(UI, 'node_modules', a.path) }));
Horosa-Web/astrostudyui/headless/runtime.js|lib.setKentangRootOverride(chartRoot);
Horosa-Web/astrostudyui/headless/ports.js|function backendPorts(opts, env){
Horosa-Web/astrostudyui/headless/cli.js|...require('./ports').backendPortEnv(backendPorts()) };
Horosa-Web/astropy/astrostudy/xuanshi/textquery.py|alts = script_variants(head) + alts
horosa|exec "${NODE_BIN}" "${CLI}" "$@"
.mcp.json|"command": "./horosa"
.mcp.json|"args": ["mcp"]
Horosa-Web/astrostudyui/.gitignore|/headless/dist
docs/HEADLESS.md|./horosa mcp
Horosa-Web/astrostudyui/headless/batch.js|r = await lib.runTool(TOOL, args, { origin: 'mcp', clientName: 'batch', requestId: `batch-${task.key}-${tech}`, signal: ac.signal });
Horosa-Web/astrostudyui/headless/batch.js|const MAX_CHARS_CAP = 60000;
Horosa-Web/astrostudyui/headless/batch.js|if(which === 'java' && init.pythonOnly){
Horosa-Web/astrostudyui/headless/runtime.js|storage.__setOverlay('horosaBackendIdentityOff', { read: ()=>'1', write: (v)=>v });
Horosa-Web/astrostudyui/headless/runtime.js|if(!fs.existsSync(path.join(UI_ROOT, 'src'))){ return !fs.existsSync(BUNDLE); }
Horosa-Web/astrostudyui/headless/cli.js|main(process.argv.slice(2)).then((code)=>require('./exit').exitAfterFlush(code));
Horosa-Web/astrostudyui/headless/exit.js|try{ process.stdout.write('', done); }catch(e){ done(); }
Horosa-Web/astrostudyui/src/utils/aiAnalysisContext/recordFields.js|export function canonicalSnapshotText(content){
Horosa-Web/astrostudyui/headless/test/batch.test.js|批量每例每技法的 data == 单例 tools/call cast_technique 的 structuredContent(逐值)
Horosa-Web/astrostudyui/headless/test/batchParity.test.js|② 批量 == 名人库建档后按档案起盘
scripts/linux/backends.sh|--astrosrv="http://127.0.0.1:${CHART_PORT}"
docs/HEADLESS.md|## 批量验证
S319_EOF
}
S319_MISS="$(s319_scan "${REPO_ROOT}")"
[ -z "${S319_MISS}" ] || { printf '%s\n' "${S319_MISS}" | head -6 | sed 's/^/    缺 /'; bad "[${PF_NO}]① 无头模式接线被拆($(printf '%s\n' "${S319_MISS}" | wc -l | tr -d ' ') 处)"; S319_BAD=1; }
# ①b 无头打包不许把简繁转换器换成原样返回的空壳(会让检索词的简繁写法在无头里全部空转);
#     端口环境变量只许在 ports.js 里解析(cli / runtime / selftest 各自解析 = 探测、起服务、发请求三处各认各的口)
s319_hl="${REPO_ROOT}/Horosa-Web/astrostudyui/headless"
[ "$(grep -acE 'hantConverter|toHant\(s\)\{ *return s; *\}' "${s319_hl}/build.js")" = "0" ] || { bad "[${PF_NO}]①b 无头打包把简繁转换器替成了空壳(build.js)"; S319_BAD=1; }
s319_pe="$(grep -alE 'process\.env\.HOROSA_(SERVER_PORT|CHART_PORT|SERVER_ROOT)' "${s319_hl}"/*.js | sed 's#.*/##' | grep -vx 'ports.js' | tr '\n' ' ')"
[ -z "${s319_pe}" ] || { bad "[${PF_NO}]①b 端口环境变量在 ports.js 之外另行解析:${s319_pe}"; S319_BAD=1; }
# ② 判别力自证:拷判据涉及的文件,原样全过;去掉界面类过滤 / 落盘钩子不再先判钩子 / 去掉令牌门 / .mcp.json 改了命令 各自报出
s319_tmp="$(mktemp -d "${PF_TMP}/s319_tmp.XXXXXX")"
for s319_f in $(s319_scan /nonexistent | sed 's/「.*$//' | sort -u); do
  mkdir -p "${s319_tmp}/$(dirname "${s319_f}")" && cp "$(pf_src_set "${REPO_ROOT}/${s319_f}")" "${s319_tmp}/${s319_f}" 2>/dev/null
done
s319_ok=1
[ -z "$(s319_scan "${s319_tmp}")" ] || s319_ok=0
sed -i '' "s/(t.category === 'ui' || HEADLESS_UNAVAILABLE_NAMES/(HEADLESS_UNAVAILABLE_NAMES/" "${s319_tmp}/Horosa-Web/astrostudyui/headless/runtime.js" 2>/dev/null
s319_scan "${s319_tmp}" | pipe_has -F "runtime.js「const unavailable" || s319_ok=0
sed -i '' "s/if(!hook || typeof hook.load !== 'function' || typeof hook.save !== 'function'){ return new Map(); }/if(false){ return new Map(); }/" "${s319_tmp}/Horosa-Web/astrostudyui/src/utils/aiAnalysisStore.js" 2>/dev/null
s319_scan "${s319_tmp}" | pipe_has -F "aiAnalysisStore.js「if(!hook" || s319_ok=0
sed -i '' "s/if(!m || !constantTimeEq(m\[1\].trim(), token)){ return \[401, 'missing or invalid bearer token'\]; }//" "${s319_tmp}/Horosa-Web/astrostudyui/headless/server.js" 2>/dev/null
s319_scan "${s319_tmp}" | pipe_has -F "server.js「if(!m || !constantTimeEq" || s319_ok=0
sed -i '' 's#"args": \["mcp"\]#"args": ["serve"]#' "${s319_tmp}/.mcp.json" 2>/dev/null
s319_scan "${s319_tmp}" | pipe_has -F '.mcp.json「"args": ["mcp"]' || s319_ok=0
# 批量另写一套起盘(不再调 cast_technique 的 runTool)/ 无头恢复「连不上就换根」→ 必须报出
sed -i '' "s/r = await lib.runTool(TOOL, args,/r = await castOwn(TOOL, args,/" "${s319_tmp}/Horosa-Web/astrostudyui/headless/batch.js" 2>/dev/null
s319_scan "${s319_tmp}" | pipe_has -F "batch.js「r = await lib.runTool(TOOL" || s319_ok=0
sed -i '' "s/storage.__setOverlay('horosaBackendIdentityOff'/void('horosaBackendIdentityOff'/" "${s319_tmp}/Horosa-Web/astrostudyui/headless/runtime.js" 2>/dev/null
s319_scan "${s319_tmp}" | pipe_has -F "runtime.js「storage.__setOverlay('horosaBackendIdentityOff'" || s319_ok=0
rm -rf "${s319_tmp}"
[ "${s319_ok}" = "1" ] || { bad "[${PF_NO}]② 判别力自证失败(原样不全过,或去掉界面类过滤 / 落盘钩子先判 / 令牌门 / .mcp.json 命令 / 批量不调 cast_technique / 无头换根 被改后没报出)"; S319_BAD=1; }
# ③ 合同真跑:假运行时真 HTTP(门 / MCP / 事件流 / 取消 / REST / 管理口 / 终端命令 / Ctrl-C)
if command -v node >/dev/null 2>&1 && [ -d "${REPO_ROOT}/Horosa-Web/astrostudyui/node_modules" ]; then
  # 合同(假运行时)+ 落盘层与会话生命周期(真运行时、临时数据目录、零窗口)
  S319_T="$(node --test "${REPO_ROOT}/Horosa-Web/astrostudyui/headless/test/server.test.js" "${REPO_ROOT}/Horosa-Web/astrostudyui/headless/test/runtime.test.js" "${REPO_ROOT}/Horosa-Web/astrostudyui/headless/test/version.test.js" 2>&1)" || { printf '%s\n' "${S319_T}" | grep -aE '✖|not ok' | head -4 | sed 's/^/    /'; bad "[${PF_NO}]③ 无头服务 / 终端命令 / 落盘层合同(node --test)不过"; S319_BAD=1; }
  # 批量验证(约 30 秒;不要计算服务:假 Python 服务 + 关着的 Java 口):输入归一 / 一行一例 / 坏行 / 续跑与半行 / 补技法 / 本地技法批量 == 单例逐值 /
  #   单技法超时只落一格 / 只用 Python 时要 Java 的就地失败 / Ctrl-C 后续跑 / 入口等输出写完再退。要真计算服务的逐值对拍(batchParity)不在这里跑
  S319_B="$(node --test "${REPO_ROOT}/Horosa-Web/astrostudyui/headless/test/batch.test.js" 2>&1)" || { printf '%s\n' "${S319_B}" | grep -aE '✖|not ok' | head -4 | sed 's/^/    /'; bad "[${PF_NO}]③ 批量验证合同(node --test headless/test/batch.test.js)不过"; S319_BAD=1; }
  # 写入面三入口矩阵(真运行时子进程、临时数据目录、回环随机端口、后端根指向已关的随机口;约 2 分钟):写入工具 × MCP / REST / 终端命令,
  #   审批(只读 / 每次确认)/ 账本 / 撤销还原 / 幂等键回放与冲突 / 管理口提案采纳·拒绝·撤销采纳;行由工具目录生成,新写入工具没配样例即红
  S319_W="$(node --test "${REPO_ROOT}/Horosa-Web/astrostudyui/headless/test/writeMatrix.test.js" 2>&1)" || { printf '%s\n' "${S319_W}" | grep -aE '✖|not ok|^\s+\+ ' | head -8 | sed 's/^/    /'; bad "[${PF_NO}]③ 无头写入面三入口矩阵(node --test headless/test/writeMatrix.test.js)不过"; S319_BAD=1; }
else
  warn "[${PF_NO}]③ 本机没有 node 或前端依赖,跳过无头合同真跑(只做了静态锚)"
fi
[ "${S319_BAD}" = "0" ] && ok "[${PF_NO}] 无头模式:工具层同源 / 浏览器路径零影响 / 界面类不进无头 / 门与令牌 / AI 直接接入;判别力自证 + 合同真跑"
}

seg_320() {
echo "[${PF_NO}] 名人库开放给 AI(检索 / 分类 / 详情 / 存成命盘)+ 奇门择日对外开放(口径 = 奇门页排盘设置;三式仍不开放)"
S320_BAD=0
# 判据 = 「仓内路径|必含字面量」(grep -F):拆掉任一处,名人库查询拼接用户输入(注入)、建档不查重 / 不可撤销、
#   奇门择日口径与奇门页分叉,或三式被悄悄放开。
s320_scan(){
  pf_scan_table "$1" <<'S320_EOF'
Horosa-Web/astrostudyui/src/utils/astrodata/celebrityDb.js|if(params && params.length){ stmt.bind(params); }
Horosa-Web/astrostudyui/src/utils/astrodata/celebrityDb.js|const hook = typeof globalThis !== 'undefined' ? globalThis.__HOROSA_ASTRODATA_LOADER__ : null;
Horosa-Web/astrostudyui/src/utils/astrodata/celebrityDb.js|Astro-Databank(Astrodienst AG),仅供非商业占星研究
Horosa-Web/astrostudyui/src/utils/aiTools/tools/celebrities.js|const dup = findCelebrityChart(
Horosa-Web/astrostudyui/src/utils/astrodata/celebrityDedupe.js|export function findCelebrityChart(
Horosa-Web/astrostudyui/src/components/astrodata/AstrodataPage.js|const existing = findCelebrityChart({ id: d.chart.cid, name: d.chart.name, birth: d.chart.birth });
Horosa-Web/astrostudyui/src/utils/aiTools/tools/celebrities.js|undo: { kind: 'trash-record', payload: { store: 'chart', cid: saved.cid } },
Horosa-Web/astrostudyui/src/utils/aiTools/index.js|searchCelebritiesTool, listCelebrityCategoriesTool, getCelebrityTool, createCelebrityChartTool,
Horosa-Web/astrostudyui/src/utils/aiTools/errorCodes.js|E_CELEBRITY_NOT_FOUND: def(
Horosa-Web/astrostudyui/src/utils/aiTools/errorCodes.js|E_CELEBRITY_DB_UNAVAILABLE: def(
Horosa-Web/astrostudyui/src/utils/aiTools/zeriSchools.js|export const ZERI_SCHOOLS = ['huangli', 'bazi', 'ziwei', 'liureng', 'taiyi', 'qimen', 'qizheng', 'india'];
Horosa-Web/astrostudyui/src/utils/aiTools/zeriSchools.js|defaults: page.dunjiaZeriOptions
Horosa-Web/astrostudyui/src/utils/aiTools/zeriSchools.js|	sanshi: '三式择日每个样本同时排六壬 / 奇门 / 太乙三盘
Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js|return normalizeKenQimenOptions(DUNJIA_PAGE_SETTINGS.loadSaved());
Horosa-Web/astrostudyui/headless/runtime.js|globalThis.__HOROSA_ASTRODATA_LOADER__ = async ()=>{
Horosa-Web/astrostudyui/src/utils/__tests__/aiToolsCelebrities.test.js|存成命盘:出生资料原样 + 来源备注 + 分组;同名同生辰不重复;撤销 = 移入回收站
Horosa-Web/astrostudyui/src/utils/__tests__/aiToolsExternalZeri.test.js|奇门:一个月里「开门落离九宫」的时段
S320_EOF
}
S320_MISS="$(s320_scan "${REPO_ROOT}")"
[ -z "${S320_MISS}" ] || { printf '%s\n' "${S320_MISS}" | head -6 | sed 's/^/    缺 /'; bad "[${PF_NO}]① 名人库 / 奇门择日开放接线被拆($(printf '%s\n' "${S320_MISS}" | wc -l | tr -d ' ') 处)"; S320_BAD=1; }
# ② 判别力自证:去掉参数绑定 / 建档不查重 / 奇门口径换成空对象 / 放开三式 各自报出
s320_tmp="$(mktemp -d "${PF_TMP}/s320_tmp.XXXXXX")"
for s320_f in $(s320_scan /nonexistent | sed 's/「.*$//' | sort -u); do
  mkdir -p "${s320_tmp}/$(dirname "${s320_f}")" && cp "$(pf_src_set "${REPO_ROOT}/${s320_f}")" "${s320_tmp}/${s320_f}" 2>/dev/null
done
s320_ok=1
[ -z "$(s320_scan "${s320_tmp}")" ] || s320_ok=0
sed -i '' 's/if(params \&\& params.length){ stmt.bind(params); }//' "${s320_tmp}/Horosa-Web/astrostudyui/src/utils/astrodata/celebrityDb.js" 2>/dev/null
s320_scan "${s320_tmp}" | pipe_has -F 'celebrityDb.js「if(params' || s320_ok=0
sed -i '' 's/const dup = findCelebrityChart(/const dup = null \&\& (/' "${s320_tmp}/Horosa-Web/astrostudyui/src/utils/aiTools/tools/celebrities.js" 2>/dev/null
s320_scan "${s320_tmp}" | pipe_has -F 'celebrities.js「const dup' || s320_ok=0
sed -i '' 's/defaults: page.dunjiaZeriOptions/defaults: ()=>({})/' "${s320_tmp}/Horosa-Web/astrostudyui/src/utils/aiTools/zeriSchools.js" 2>/dev/null
s320_scan "${s320_tmp}" | pipe_has -F 'zeriSchools.js「defaults: page.dunjiaZeriOptions' || s320_ok=0
sed -i '' "/^	sanshi: '三式择日每个样本/d" "${s320_tmp}/Horosa-Web/astrostudyui/src/utils/aiTools/zeriSchools.js" 2>/dev/null
s320_scan "${s320_tmp}" | pipe_has -F "zeriSchools.js「	sanshi:" || s320_ok=0
rm -rf "${s320_tmp}"
[ "${s320_ok}" = "1" ] || { bad "[${PF_NO}]② 判别力自证失败(原样不全过,或去掉参数绑定 / 建档查重 / 奇门口径 / 三式仍关 被改后没报出)"; S320_BAD=1; }
[ "${S320_BAD}" = "0" ] && ok "[${PF_NO}] 名人库开放给 AI(参数化查询 / 建档查重可撤销 / 署名)+ 奇门择日口径 = 奇门页、三式仍关;判别力自证"
}

seg_127() {
# ---- [${PF_NO}] AI段勾选「所见即所得」(四症=清空按钮死/勾了不纳入/挂载与导出分叉/五技法强推段
#      取消不掉。根因:①空数组被当「未自定义」→ effective 回 preset 全勾;②导出主链运行时强推段
#      而挂载封装不强推 → 两链分叉;③事盘/命盘源上下文(full 模式)全文裸发不过段;④planetInfo
#      开关仅导出消费。防线:v45 语义(空数组=显式全清)+迁移(尸块删键+强推 union 显式化)+
#      源层读出后过滤+planetInfo 挂载消费+金标。铁律:「设置面显示什么,导出与挂载就吃什么」。) ----
S127_BAD=0
S127_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
echo "[${PF_NO}] AI段勾选所见即所得(空数组=显式全清+强推迁移+源层过滤)"
grep -q "hasCustom" "$(pf_src_set "${S127_UI}/src/utils/aiExport.js")" 2>/dev/null || { bad "[${PF_NO}] effective 缺 hasCustom 空数组语义(清空按钮回潮死)"; S127_BAD=1; }
grep -q "AI_EXPORT_FORCED_INCLUDE_SECTIONS" "$(pf_src_set "${S127_UI}/src/utils/aiExport.js")" 2>/dev/null || { bad "[${PF_NO}] 缺强推段迁移表(老用户强推段将静默丢失)"; S127_BAD=1; }
grep -q "picked.push('六壬大格'" "$(pf_src_set "${S127_UI}/src/utils/aiExport.js")" 2>/dev/null && { bad "[${PF_NO}] 导出主链运行时强推段回潮(用户取消不掉=三式合一事故复发)"; S127_BAD=1; }
grep -q "filterSourceContextBySections" "$(pf_src_set "${S127_UI}/src/utils/aiAnalysisContext.js")" 2>/dev/null || { bad "[${PF_NO}] 源上下文段过滤缺失(事盘全文裸发回潮)"; S127_BAD=1; }
grep -q "exportSettingKeyForSnapshotModule" "$(pf_src_set "${S127_UI}/src/utils/aiAnalysisContext.js")" 2>/dev/null || { bad "[${PF_NO}] 源层缺 module→设置键反查(六爻 guazhan 打不中设置)"; S127_BAD=1; }
grep -q "applyPlanetInfoFilterByContext" "$(pf_src_set "${S127_UI}/src/utils/aiAnalysisContext.js")" 2>/dev/null || { bad "[${PF_NO}] 挂载链缺星曜后天信息消费(开关静默失效回潮)"; S127_BAD=1; }
[ -f "${S127_UI}/src/utils/__tests__/aiExportSectionSemantics.test.js" ] || { bad "[${PF_NO}] 缺段勾选语义金标"; S127_BAD=1; }
[ "${S127_BAD}" = "0" ] && ok "[${PF_NO}] v45 空数组语义+强推迁移+源层过滤+planetInfo 挂载消费+金标 全在位"
}

seg_314() {
echo "[${PF_NO}] 本机 MCP 读面补齐:后台任务 / 无头合盘取数 / 天星择日三件 / 玄学史两件 / 当前页正文 / 私人内容三件(子开关缺省关、只经 MCP)/ 资源加任务与操作手册 / 技能包与使用指南提示 / 无头分析带合盘对方与技能包"
S314_BAD=0
# 判据 = 「仓内路径|必含字面量」(grep -F):拆掉任一处,外部客户端又只能读档案列表与单技法快照(任务、合盘、择日、史料、
#   当前页、操作手册全看不到);私人内容子开关缺省值翻成开 = 对话记录与断事日志不经用户同意就对外可读。
s314_scan(){
  pf_scan_table "$1" <<'S314_EOF'
Horosa-Web/astrostudyui/src/utils/aiTools/index.js|listTasksTool, getTaskTool, castRelative, listElectionConditionsTool, searchElectionTool, explainElectionTool,
Horosa-Web/astrostudyui/src/utils/aiTools/index.js|searchXuanshiTool, getXuanshiItemTool, readCurrentPage, listConversationsTool, getConversationTool, getRecordDetailTool,
Horosa-Web/astrostudyui/src/utils/aiAgent/prefs.js|export const AGENT_PRIVATE_READ_KEY = 'horosa.ai.tools.privateRead.enabled';
Horosa-Web/astrostudyui/src/utils/aiAgent/prefs.js|return safeLocalStorageGet(AGENT_PRIVATE_READ_KEY) === '1';
Horosa-Web/astrostudyui/src/utils/aiTools/tools/privateRead.js|const PRIVATE_GATE = ()=>isPrivateReadEnabled();
Horosa-Web/astrostudyui/src/components/aianalysis/ExternalAgentPanel.js|data-private-read-switch="1"
Horosa-Web/astrostudyui/src/utils/storageKeyRegistry.js|{ key: 'horosa.ai.tools.privateRead.enabled', kind: 'settings', backup: true,
Horosa-Web/astrostudyui/src/utils/aiTools/resources.js|export const RESOURCE_KINDS = ['chart', 'case', 'material', 'task', 'help'];
Horosa-Web/astrostudyui/src/utils/aiTools/resources.js|return t ? fmt.taskDetailText(fmt.detailOfTask(t, { logLines: 50, resultChars: 20000 })) : null;
Horosa-Web/astrostudyui/src/utils/aiTools/helpText.js|if(!Object.prototype.hasOwnProperty.call(TECHNIQUE_HELP_DOCS, key)){ return ''; }
Horosa-Web/astrostudyui/src/utils/aiTools/completions.js|if(kind === 'task' && argName === 'id'){ return rankCandidates(await taskRows(), value); }
Horosa-Web/astrostudyui/src/utils/aiTools/completions.js|if(kind === 'help' && argName === 'tab'){ return rankCandidates(await helpRows(), value); }
Horosa-Web/astrostudyui/src/utils/aiTools/prompts.js|export const PROMPT_SKILL_PREFIX = 'skill:';
Horosa-Web/astrostudyui/src/utils/aiTools/prompts.js|export const PROMPT_GUIDE_NAME = 'guide:horosa';
Horosa-Web/astrostudyui/src/utils/aiTools/tools/runAnalysis.js|if(!question && !args.skill){ return { ok: false, code: 'E_ARGS_INVALID', message: 'question 与 skill 至少给一个' }; }
Horosa-Web/astrostudyui/src/utils/aiTools/tools/runAnalysis.js|...(partnerSource ? { partnerSource } : {}),
Horosa-Web/astrostudyui/src/utils/aiAgent/goalRunner.js|conversation, ...(partnerSource ? { partnerSource } : {}) });
Horosa-Web/astrostudyui/src/utils/aiExport.js|export async function buildCurrentPageExportForTool(){
Horosa-Web/astrostudyui/src/utils/aiTools/tools/readCurrentPage.js|try{ p = await mod.buildCurrentPageExportForTool(); }
Horosa-Web/astrostudyui/src/utils/aiTools/tools/castRelative.js|import { getPairSynastryText, getPairChineseTexts, clipContentToBudget } from '../../aiAnalysisContext';
Horosa-Web/astrostudyui/src/utils/aiTools/tools/searchElection.js|import { runScan, MAX_SPAN_DAYS_TOTAL } from '../../../divination/zeri/scanOrchestrator';
Horosa-Web/astrostudyui/src/utils/aiTools/tools/listTasks.js|export function taskDetailText(d){
Horosa-Web/astrostudyui/src/utils/__tests__/aiToolsExternalRead.test.js|关 ⇒ 三件不进 MCP 目录、直呼其名 E_TOOL_DISABLED
Horosa-Web/astrostudyui/src/utils/__tests__/mcpHelpSkillsPrompts.test.js|两层页签的惰性项全部展开
Horosa-Web/astrostudyui/src/utils/__tests__/aiToolsCatalog.contract.test.js|判别向量:顶层禁键 / 写类嵌套 cid / 读类嵌套其它禁键 一律判红
S314_EOF
}
# 私人内容三件每件都必须挂子开关、且只对 mcp 来源开放(恰 3 处)
s314_counts(){
  s314_pr="$1/Horosa-Web/astrostudyui/src/utils/aiTools/tools/privateRead.js"
  s314_n1="$(grep -cF -- "enabled: PRIVATE_GATE," "${s314_pr}" 2>/dev/null)"
  s314_n2="$(grep -cF -- "origins: ['mcp']," "${s314_pr}" 2>/dev/null)"
  [ "${s314_n1:-0}" = "3" ] || printf 'privateRead.js「enabled: PRIVATE_GATE,」应 3 处,实 %s\n' "${s314_n1:-0}"
  [ "${s314_n2:-0}" = "3" ] || printf "privateRead.js「origins: ['mcp'],」应 3 处,实 %s\n" "${s314_n2:-0}"
}
S314_MISS="$(s314_scan "${REPO_ROOT}"; s314_counts "${REPO_ROOT}")"
[ -z "${S314_MISS}" ] || { printf '%s\n' "${S314_MISS}" | head -6 | sed 's/^/    缺 /'; bad "[${PF_NO}]① 本机 MCP 读面接线被拆($(printf '%s\n' "${S314_MISS}" | wc -l | tr -d ' ') 处)"; S314_BAD=1; }
# ② 判别力自证:拷判据涉及的文件,原样全过;子开关缺省改成开 / 私人工具摘掉一处开关后各自报出
s314_tmp="$(mktemp -d "${PF_TMP}/s314_tmp.XXXXXX")"
for s314_f in $(s314_scan /nonexistent | sed 's/「.*$//' | sort -u); do
  mkdir -p "${s314_tmp}/$(dirname "${s314_f}")" && cp "$(pf_src_set "${REPO_ROOT}/${s314_f}")" "${s314_tmp}/${s314_f}" 2>/dev/null
done
s314_ok=1
[ -z "$(s314_scan "${s314_tmp}"; s314_counts "${s314_tmp}")" ] || s314_ok=0
sed -i '' "s/return safeLocalStorageGet(AGENT_PRIVATE_READ_KEY) === '1';/return safeLocalStorageGet(AGENT_PRIVATE_READ_KEY) !== '0';/" "${s314_tmp}/Horosa-Web/astrostudyui/src/utils/aiAgent/prefs.js" 2>/dev/null
s314_scan "${s314_tmp}" | pipe_has -F "prefs.js「return safeLocalStorageGet(AGENT_PRIVATE_READ_KEY) === '1';」" || s314_ok=0
s314_pf="${s314_tmp}/Horosa-Web/astrostudyui/src/utils/aiTools/tools/privateRead.js"
awk '!d && index($0, "enabled: PRIVATE_GATE,") { sub(/enabled: PRIVATE_GATE,/, ""); d = 1 } { print }' "${s314_pf}" > "${s314_pf}.x" 2>/dev/null && mv "${s314_pf}.x" "${s314_pf}"
s314_counts "${s314_tmp}" | pipe_has -F '「enabled: PRIVATE_GATE,」应 3 处,实 2' || s314_ok=0
rm -rf "${s314_tmp}"
[ "${s314_ok}" = "1" ] || { bad "[${PF_NO}]② 判别力自证失败(原样不全过,或子开关缺省翻开 / 摘掉一处开关后没报出)"; S314_BAD=1; }
[ "${S314_BAD}" = "0" ] && ok "[${PF_NO}] 本机 MCP 读面:任务 / 合盘 / 择日 / 史料 / 当前页 / 私人内容(缺省关、只经 MCP)/ 任务与手册资源 / 技能包与指南提示 / 无头分析合盘与技能包;判别力自证"
}

seg_313() {
echo "[${PF_NO}] 本机 MCP 协议层:工具全字段透传 / 输出结构 / 补全 / 分页 / 进度帧走本请求响应流 / 取消(两纪元 + stdio)/ 页面桥两道调度 / 预算透传"
S313_BAD=0
# 判据 = 「仓内路径|必含字面量」(grep -F):拆掉任一处,外部客户端又看不到中文标题与输出结构、长起盘重新堵死只读查询、
#   取消通知石沉大海(工具照跑完、写入在客户端放弃后落地)、进度回不去、响应流又只能靠关连接收尾(每次调用漏一条半开连接)。
s313_scan(){
  pf_scan_table "$1" <<'S313_EOF'
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|pub fn project_tool(t: &Value) -> Value {
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|out.insert("outputSchema".into(), os.clone());
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|["2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"];
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|"completion/complete" => {
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|"completions": {},
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|if method == "notifications/cancelled" {
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|pub fn cancel_call(&self, key: &str, client: Option<&str>) -> bool {
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|const CANCEL_TOMBSTONE_TTL: Duration = Duration::from_secs(5);
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|pub fn progress_frame(token: &Value, v: &Value, last: &mut Option<f64>) -> Option<Value> {
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|let writer = request.into_writer();
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|Transfer-Encoding: chunked
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|cancel_on_disconnect: true,
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|"_meta": { "timeoutMs": timeout.as_millis() as u64 }
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|const WORKERS: usize = 8;
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|struct InflightSlot<'a>(&'a AtomicUsize);
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|pub fn cancel_script(id: u64) -> String {
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|Ok(BridgeMsg::Progress(v)) => ctl.progress(&v),
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|fn legacy_cancel_notification_stops_inflight_call_and_tombstone_precancels(
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|fn legacy_progress_streams_monotonic_frames_then_result_and_connection_is_reusable(
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|fn legacy_stream_disconnect_is_not_cancellation_but_modern_disconnect_is(
Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs|fn tools_list_projects_title_meta_output_schema_and_drops_internal_fields(
Horosa_Desktop_Installer/src-tauri/src/mcp_stdio.rs|pub const MAX_CONCURRENT: usize = 8;
Horosa_Desktop_Installer/src-tauri/src/mcp_stdio.rs|std::thread::scope(|scope| loop {
Horosa_Desktop_Installer/src-tauri/src/mcp_stdio.rs|fn forward_notification(
Horosa_Desktop_Installer/src-tauri/src/mcp_stdio.rs|pub fn request_timeout_for(parsed: &Value) -> Duration {
Horosa_Desktop_Installer/src-tauri/src/mcp_stdio.rs|fn serve_routes_cancel_to_the_original_lane_and_never_writes_the_cancelled_answer(
Horosa_Desktop_Installer/src-tauri/src/mcp_stdio.rs|fn serve_runs_requests_concurrently_slow_call_does_not_block_fast_one(
Horosa_Desktop_Installer/src-tauri/src/agent_bridge.rs|fn agent_tool_progress_command(
Horosa_Desktop_Installer/src-tauri/src/main.rs|            agent_tool_progress_command,
Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js|export const SHARED_CONCURRENCY = 3;
Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js|if(def.level === 'additive' || def.category === 'ui'){ return { lane: 'exclusive', name }; }
Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js|window.__horosaAgentToolCancel = (id)=>cancelAgentToolRequest(id);
Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js|invokeDesktopCommand('agent_tool_progress_command', { id, ...v })
Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js|r = await raceCancel(withTimeout(d.runTool(name, args, ctx)
Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js|const structured = hasData && r.ok && (declaredOutput || !text.truncated) ? r.data : undefined;
Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js|if(method === 'completion/complete'){
Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js|return pagedResult('resources', { ...page, items: visible(page && page.items, (x)=>x.uri) });
Horosa-Web/astrostudyui/src/utils/aiTools/catalog.js|...(d.outputSchema ? { outputSchema: JSON.parse(JSON.stringify(d.outputSchema)) } : {}),
Horosa-Web/astrostudyui/src/utils/aiTools/registry.js|def.outputSchema.type !== 'object'
Horosa-Web/astrostudyui/src/utils/aiTools/resources.js|export async function listResourcesPage(opts){
Horosa-Web/astrostudyui/src/utils/aiTools/prompts.js|export async function listPromptsPage(opts){
Horosa-Web/astrostudyui/src/utils/aiTools/completions.js|export async function completeArgument(ref, argument){
Horosa-Web/astrostudyui/src/utils/aiTools/errorCodes.js|E_CANCELLED: def(
Horosa-Web/astrostudyui/src/utils/aiTools/tools/castTechnique.js|const runP = runCast(args, report);
Horosa-Web/astrostudyui/src/utils/aiTools/tools/runAnalysis.js|...(onTrace ? { onTrace } : {}),
Horosa-Web/astrostudyui/src/utils/__tests__/mcpBridgeSchedule.test.js|只读并发到上限 3、第 4 条排队
Horosa-Web/astrostudyui/src/utils/__tests__/aiToolsOutputSchema.contract.test.js|真跑:建档(新建 / 已存在)
Horosa-Web/astrostudyui/src/utils/__tests__/mcpCompletionsPaging.test.js|资源 250 条(命盘)+ 2 份资料
Horosa_Desktop_Installer/scripts/verify_mcp_smoke.sh|notifications/progress
S313_EOF
}
S313_MISS="$(s313_scan "${REPO_ROOT}")"
[ -z "${S313_MISS}" ] || { printf '%s\n' "${S313_MISS}" | head -6 | sed 's/^/    缺 /'; bad "[${PF_NO}]① 本机 MCP 协议层接线被拆($(printf '%s\n' "${S313_MISS}" | wc -l | tr -d ' ') 处)"; S313_BAD=1; }
# ② 判别力自证:拷判据涉及的文件,原样全过;响应流改回 upgrade / 共享道并发降回 1 后各自报出
s313_tmp="$(mktemp -d "${PF_TMP}/s313_tmp.XXXXXX")"
for s313_f in $(s313_scan /nonexistent | sed 's/「.*$//' | sort -u); do
  mkdir -p "${s313_tmp}/$(dirname "${s313_f}")" && cp "$(pf_src_set "${REPO_ROOT}/${s313_f}")" "${s313_tmp}/${s313_f}" 2>/dev/null
done
s313_ok=1
[ -z "$(s313_scan "${s313_tmp}")" ] || s313_ok=0
sed -i '' 's/let writer = request.into_writer();/let writer = request.upgrade("sse", Response::empty(StatusCode(200)));/' "${s313_tmp}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs" 2>/dev/null
s313_scan "${s313_tmp}" | pipe_has -F 'mcp_server.rs「let writer = request.into_writer();」' || s313_ok=0
sed -i '' 's/export const SHARED_CONCURRENCY = 3;/export const SHARED_CONCURRENCY = 1;/' "${s313_tmp}/Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js" 2>/dev/null
s313_scan "${s313_tmp}" | pipe_has -F 'mcpBridge.js「export const SHARED_CONCURRENCY = 3;」' || s313_ok=0
rm -rf "${s313_tmp}"
[ "${s313_ok}" = "1" ] || { bad "[${PF_NO}]② 判别力自证失败(原样不全过,或响应流改回 upgrade / 共享道并发降回 1 后没报出)"; S313_BAD=1; }
[ "${S313_BAD}" = "0" ] && ok "[${PF_NO}] 本机 MCP 协议层:全字段透传 / 输出结构 / 补全 / 分页 / 进度帧 / 取消(两纪元 + stdio)/ 两道调度 / 预算透传;判别力自证"
}

seg_315() {
echo "[${PF_NO}] 本机 MCP 写入面与界面:断事日志追加 / 档案关系边(只增、不刷新更新时间、两张一起撤销)/ 对话挂载 / AI 分析页页内页签 / 按用户起卦结果建事盘(快照正文必存)/ 设置页面面(该页校验、整份原文撤销)/ 各流派择日搜索(工作台缺省单源)"
S315_BAD=0
# 判据 = 「仓内路径|必含字面量」(grep -F):拆掉任一处,AI 追加的日志 / 关系会刷新更新时间(之后撤销建档被误判「手工改过」)、
#   撤销关系边只还原一张(留下单向边)、挂载技法不经可挂键校验、AI 分析页的页签切不过去。
s315_scan(){
  pf_scan_table "$1" <<'S315_EOF'
Horosa-Web/astrostudyui/src/utils/aiTools/recordFlags.js|if(field === 'journal' || field === 'relations'){ return Array.isArray(rec && rec[field]) ? JSON.parse(JSON.stringify(rec[field])) : []; }
Horosa-Web/astrostudyui/src/utils/aiTools/recordFlags.js|return upsert({ cid, [field]: Array.isArray(value) ? value : [], preserveUpdateTime: true, updateTime: rec.updateTime });
Horosa-Web/astrostudyui/src/utils/aiTools/recordFlags.js|if(found.some(({ it, f })=>!sameValue(readFlag(f.store, f.rec, it.field), it.after))){
Horosa-Web/astrostudyui/src/utils/aiTools/tools/recordJournal.js|undo: flagUndo(f.store, args.recordId, 'journal', before, after),
Horosa-Web/astrostudyui/src/utils/aiTools/tools/recordJournal.js|undo: flagUndoMulti([
Horosa-Web/astrostudyui/src/utils/aiTools/tools/recordJournal.js|relation: { type: 'string', enum: RELATION_TYPES.map((r)=>r.value),
Horosa-Web/astrostudyui/src/utils/aiTools/tools/setChatMount.js|if(bad.length){ return { result: { ok: false, code: 'E_TECHNIQUE_NOT_ALLOWED',
Horosa-Web/astrostudyui/src/utils/aiTools/tools/setChatMount.js|undo: { kind: CHAT_MOUNT_UNDO_KIND, payload: { before:
Horosa-Web/astrostudyui/src/utils/aiTools/tools/navigateToTechnique.js|if(args.technique === AI_PAGE_KEY && args.subTab){ return switchAiInnerTab(args, ui, ctx, label); }
Horosa-Web/astrostudyui/src/utils/aiTools/index.js|appendRecordJournalTool, linkRecordsTool, setChatMount,
Horosa-Web/astrostudyui/src/components/aianalysis/chat/useChatAssist.js|getChatMount: ()=>{
Horosa-Web/astrostudyui/src/components/aianalysis/chat/useChatAssist.js|setChatTechniques: (keys)=>{
Horosa-Web/astrostudyui/src/components/aianalysis/AIAnalysisMain.js|const SECONDARY_TAB_ITEMS = SECONDARY_TABS.map((t)=>({ key: t.key, label: t.label }));
Horosa-Web/astrostudyui/src/components/aianalysis/AIAnalysisMain.js|innerTab, innerTabs: SECONDARY_TAB_ITEMS,
Horosa-Web/astrostudyui/src/utils/__tests__/aiToolsExternalRecords.test.js|任一张写后被改过 → 一张都不还原
Horosa-Web/astrostudyui/src/utils/aiTools/divinationCast.js|export const INPUT_CASTABLE = ['liuyao', 'xiaoliuren', 'lingqi', 'tongshefa', 'xiaochengtu', 'feigong'];
Horosa-Web/astrostudyui/src/utils/aiTools/divinationCast.js|if(typeof r.snapshot !== 'string' || !r.snapshot.trim()){ return { ok: false, code: 'E_CAST_FAILED', message: '成卦了但没产出快照正文,未建事盘' }; }
Horosa-Web/astrostudyui/src/utils/aiTools/tools/castDivinationCase.js|const payload = { module: spec.module, version: spec.version, savedAt: new Date().toISOString(), fieldSnapshot: caseFieldSnapshot(fieldsLike), createdBy: 'ai-assistant', ...built.body, snapshot: built.snapshot };
Horosa-Web/astrostudyui/src/utils/aiTools/tools/castDivinationCase.js|undo: { kind: 'trash-record', payload: { store: 'case', cid: saved.cid } },
Horosa-Web/astrostudyui/src/utils/aiTools/tools/createCaseRecord.js|export async function resolveCaseTimePlace(args, assumptions){
Horosa-Web/astrostudyui/src/utils/aiTools/tools/createCaseRecord.js|export function persistCaseRecord(toolName, values, args, ctx, assumptions){
Horosa-Web/astrostudyui/src/components/guazhan/GuaZhanMain.js|export function buildLinesGua(lines, moving, nongli){
Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js|export async function buildSixyaoCaseFromLines(record, lines, moving){
Horosa-Web/astrostudyui/src/utils/aiTools/index.js|listDivinationCastsTool, castDivinationCaseTool,
Horosa-Web/astrostudyui/src/utils/__tests__/aiToolsExternalCast.test.js|cast_technique 读回的就是这份快照
Horosa-Web/astrostudyui/src/utils/aiTools/settingsFacets.js|export const SETTING_FACETS = ['chart', 'mount', 'app', 'classical', 'technique', 'page'];
Horosa-Web/astrostudyui/src/utils/aiTools/settingsFacets.js|export const PAGE_FACET_EXCLUDED = {
Horosa-Web/astrostudyui/src/utils/aiTools/settingsFacets.js|if(!page || keys.some((k)=>page.fields.indexOf(k) < 0)){ return { ok: false, code: 'E_UNDO_NOT_APPLICABLE' }; }
Horosa-Web/astrostudyui/src/utils/aiTools/settingsFacets.js|const moved = keys.filter((k)=>!storedSettingValueSame(facet, k, cur[k], written[k]));
Horosa-Web/astrostudyui/src/utils/aiTools/tools/setSettings.js|if(args.facet === 'page'){ await preparePageFacet(args.technique); }
Horosa-Web/astrostudyui/src/utils/__tests__/aiToolsExternalPageSettings.test.js|载入表 ∪ 排除表 = 登记表
Horosa-Web/astrostudyui/src/utils/aiTools/zeriSchools.js|export const ZERI_SCHOOLS = ['huangli', 'bazi', 'ziwei', 'liureng', 'taiyi', 'qimen', 'qizheng', 'india'];
Horosa-Web/astrostudyui/src/utils/aiTools/zeriSchools.js|export const ZERI_AI_MAX_SPAN_DAYS = {
Horosa-Web/astrostudyui/src/utils/aiTools/tools/searchZeri.js|({ ui, compiled } = compileAgentTreeWith(sch.registry, sch.compile, args.conditions, 'list_zeri_conditions'));
Horosa-Web/astrostudyui/src/utils/aiTools/tools/searchElection.js|export function compileAgentTreeWith(registry, compileFn, tree, listHint){
Horosa-Web/astrostudyui/src/components/zeri/BaziZeriMain.js|options: baziZeriFullDefaultOptions(),
Horosa-Web/astrostudyui/src/components/zeri/ZiweiZeriMain.js|options: ziweiZeriFullDefaultOptions(),
Horosa-Web/astrostudyui/src/components/zeri/LiurengZeriMain.js|options: liurengZeriFullDefaultOptions(),
Horosa-Web/astrostudyui/src/components/zeri/TaiyiZeriMain.js|options: taiyiZeriFullDefaultOptions(),
Horosa-Web/astrostudyui/src/utils/__tests__/aiToolsExternalZeri.test.js|每个区间的 pick 经 explain_zeri 判读成立
S315_EOF
}
S315_MISS="$(s315_scan "${REPO_ROOT}")"
[ -z "${S315_MISS}" ] || { printf '%s\n' "${S315_MISS}" | head -6 | sed 's/^/    缺 /'; bad "[${PF_NO}]① 本机 MCP 写入面接线被拆($(printf '%s\n' "${S315_MISS}" | wc -l | tr -d ' ') 处)"; S315_BAD=1; }
# ② 判别力自证:拷判据涉及的文件,原样全过;列表字段写入去掉保留更新时间 / 撤销改成不先全量比对后各自报出
s315_tmp="$(mktemp -d "${PF_TMP}/s315_tmp.XXXXXX")"
for s315_f in $(s315_scan /nonexistent | sed 's/「.*$//' | sort -u); do
  mkdir -p "${s315_tmp}/$(dirname "${s315_f}")" && cp "$(pf_src_set "${REPO_ROOT}/${s315_f}")" "${s315_tmp}/${s315_f}" 2>/dev/null
done
s315_ok=1
[ -z "$(s315_scan "${s315_tmp}")" ] || s315_ok=0
s315_rf="${s315_tmp}/Horosa-Web/astrostudyui/src/utils/aiTools/recordFlags.js"
sed -i '' 's/, preserveUpdateTime: true, updateTime: rec.updateTime });/ });/' "${s315_rf}" 2>/dev/null
s315_scan "${s315_tmp}" | pipe_has -F 'recordFlags.js「return upsert({ cid, [field]: Array.isArray(value) ? value : [], preserveUpdateTime: true, updateTime: rec.updateTime });」' || s315_ok=0
sed -i '' 's/if(found.some(({ it, f })=>!sameValue(/if(found.every(({ it, f })=>!sameValue(/' "${s315_rf}" 2>/dev/null
s315_scan "${s315_tmp}" | pipe_has -F 'recordFlags.js「if(found.some(({ it, f })=>!sameValue(readFlag(f.store, f.rec, it.field), it.after))){」' || s315_ok=0
sed -i '' "s/if(typeof r.snapshot !== 'string' || !r.snapshot.trim()){/if(false){/" "${s315_tmp}/Horosa-Web/astrostudyui/src/utils/aiTools/divinationCast.js" 2>/dev/null
s315_scan "${s315_tmp}" | pipe_has -F 'divinationCast.js「if(typeof r.snapshot' || s315_ok=0
rm -rf "${s315_tmp}"
[ "${s315_ok}" = "1" ] || { bad "[${PF_NO}]② 判别力自证失败(原样不全过,或去掉保留更新时间 / 撤销不先全量比对 / 拆掉快照正文守卫后没报出)"; S315_BAD=1; }
[ "${S315_BAD}" = "0" ] && ok "[${PF_NO}] 本机 MCP 写入面:日志 / 关系边只增且不刷新更新时间、两张一起撤销 / 对话挂载校验可挂键 / AI 页页内页签 / 按起卦结果建事盘 / 页面设置面 / 各派择日;判别力自证"
}

seg_316() {
echo "[${PF_NO}] 本机 MCP 提案与连接:外部「界面类也要确认」(缺省关)/ 档案提案(采纳才落库、冲突不落库、可撤销采纳、工具零落库)"
S316_BAD=0
# 判据 = 「仓内路径|必含字面量」(grep -F):拆掉任一处,外部客户端的界面类动作(切页 / 合盘配对 / 设对话挂载)在用户打开「界面类也要确认」后仍直接执行,
#   或缺省值翻成开(外部调用全部卡在审批台)。
s316_scan(){
  pf_scan_table "$1" <<'S316_EOF'
Horosa-Web/astrostudyui/src/utils/aiAgent/prefs.js|export const DEFAULT_EXTERNAL_POLICY = Object.freeze({ approval: 'auto', maxCallsPerMinute: 60, maxAdditivePerHour: 100, uiConfirm: false });
Horosa-Web/astrostudyui/src/utils/aiAgent/prefs.js|uiConfirm: r.uiConfirm === true,
Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js|const needUiConfirm = def.category === 'ui' && policy.uiConfirm === true;
Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js|if((level === 'additive' && policy.approval === 'on-request') || needUiConfirm){
Horosa-Web/astrostudyui/src/components/aianalysis/ExternalAgentPanel.js|data-external-ui-confirm-switch="1"
Horosa-Web/astrostudyui/src/utils/__tests__/aiToolsExternalProposals.test.js|开:界面类动作挂审批台
Horosa-Web/astrostudyui/src/utils/aiAgent/proposals.js|export const PROPOSALS_PENDING_MAX = 50;
Horosa-Web/astrostudyui/src/utils/aiAgent/proposals.js|const conflictFields = Object.keys(p.before).filter(
Horosa-Web/astrostudyui/src/utils/aiAgent/proposals.js|if(moved.length){ return { ok: false, code: 'E_UNDO_RECORD_CHANGED',
Horosa-Web/astrostudyui/src/utils/aiTools/tools/proposeRecord.js|const r = addProposal({ kind: 'record-edit',
Horosa-Web/astrostudyui/src/utils/aiTools/catalog.js|propose_record_edit: '只挂提案、不改档案;
Horosa-Web/astrostudyui/src/utils/aiTools/index.js|proposeRecordEditTool, proposeRecordArchiveTool, listProposalsTool,
Horosa-Web/astrostudyui/src/components/aianalysis/TaskCenterPanel.js|data-proposal-accept="1"
Horosa-Web/astrostudyui/src/components/aianalysis/TaskCenterPanel.js|data-proposal-revert="1"
Horosa-Web/astrostudyui/src/components/aianalysis/TaskCenterBell.js|+ pendingProposalCount();
Horosa-Web/astrostudyui/src/utils/storageKeyRegistry.js|{ key: 'horosa.ai.agent.proposals.v1', kind: 'device-local', backup: false,
Horosa-Web/astrostudyui/src/utils/__tests__/aiToolsExternalProposals.test.js|静态守卫:工具目录零 import 采纳 / 拒绝 / 撤销采纳
S316_EOF
}
# 采纳 / 拒绝 / 撤销采纳只由用户在任务中心触发:工具目录里出现这三个函数名 = 工具能自己落库
s316_guard(){ pf_prod_hits -E "(acceptProposal|rejectProposal|revertProposal)" "$1/Horosa-Web/astrostudyui/src/utils/aiTools" | sed "s#^$1/##"; }
S316_MISS="$(s316_scan "${REPO_ROOT}"; s316_guard "${REPO_ROOT}" | sed 's/$/「工具目录引用了提案落库函数」/')"
[ -z "${S316_MISS}" ] || { printf '%s\n' "${S316_MISS}" | head -6 | sed 's/^/    缺 /'; bad "[${PF_NO}]① 本机 MCP 提案与连接接线被拆($(printf '%s\n' "${S316_MISS}" | wc -l | tr -d ' ') 处)"; S316_BAD=1; }
# ② 判别力自证:拷判据涉及的文件,原样全过;缺省翻开 / 去掉界面类审批分支后各自报出
s316_tmp="$(mktemp -d "${PF_TMP}/s316_tmp.XXXXXX")"
for s316_f in $(s316_scan /nonexistent | sed 's/「.*$//' | sort -u); do
  mkdir -p "${s316_tmp}/$(dirname "${s316_f}")" && cp "$(pf_src_set "${REPO_ROOT}/${s316_f}")" "${s316_tmp}/${s316_f}" 2>/dev/null
done
s316_ok=1
[ -z "$(s316_scan "${s316_tmp}")" ] || s316_ok=0
sed -i '' 's/maxAdditivePerHour: 100, uiConfirm: false });/maxAdditivePerHour: 100, uiConfirm: true });/' "${s316_tmp}/Horosa-Web/astrostudyui/src/utils/aiAgent/prefs.js" 2>/dev/null
s316_scan "${s316_tmp}" | pipe_has -F 'prefs.js「export const DEFAULT_EXTERNAL_POLICY' || s316_ok=0
sed -i '' "s/ || needUiConfirm){/){/" "${s316_tmp}/Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js" 2>/dev/null
s316_scan "${s316_tmp}" | pipe_has -F "mcpBridge.js「if((level === 'additive'" || s316_ok=0
printf '\nacceptProposal(\n' >> "${s316_tmp}/Horosa-Web/astrostudyui/src/utils/aiTools/tools/proposeRecord.js"
s316_guard "${s316_tmp}" | pipe_has -F 'proposeRecord.js' || s316_ok=0
rm -rf "${s316_tmp}"
[ "${s316_ok}" = "1" ] || { bad "[${PF_NO}]② 判别力自证失败(原样不全过,或缺省翻开 / 去掉界面类审批分支 / 工具目录引用落库函数后没报出)"; S316_BAD=1; }
[ "${S316_BAD}" = "0" ] && ok "[${PF_NO}] 本机 MCP 提案与连接:外部界面类也要确认(缺省关)/ 档案提案(工具零落库);判别力自证"
}

seg_321() {
echo "[${PF_NO}] 无头模式:管理口单独令牌 / 模型接口(环境变量不落盘 · 存档密钥加密 · 命令行不收密钥)/ 整库导出导入(本机键不进包 · 导入前留快照)/ 开关翻转作废外部目录缓存 / 后端失败说明在源头解码"
S321_BAD=0
# 判据 = 「仓内路径|必含字面量」(grep -F):拆掉任一处,要么拿到接口令牌的客户端能改设置、采纳提案(只能人做的事),
#   要么环境变量里的密钥落盘 / 存档密钥明文落盘 / 密钥进 shell 历史,要么导出包把本机后端地址带进桌面,
#   要么开了「无头分析」等开关外部调用仍回「未知工具」,要么后端失败说明以 %XX 乱码到达用户与 AI,
#   要么全量 jest 把 node --test 用例捡进去必红,要么技能 / 命令只作用本轮时技法口径按会话挂载取(本轮的口径漏发)。
s321_scan(){
  pf_scan_table "$1" <<'S321_EOF'
Horosa-Web/astrostudyui/headless/server.js|const g = gate(req, adminToken, false);
Horosa-Web/astrostudyui/headless/server.js|writeAtomic(adminTokenFile(), `${adminToken}\n${process.pid}\n`, 0o600);
Horosa-Web/astrostudyui/headless/runtime.js|pending.set(name, name === PROVIDER_STORE ? entries.filter((e)=>e && e[0] !== ENV_PROFILE_ID) : entries);
Horosa-Web/astrostudyui/headless/runtime.js|const fd = fs.openSync(file, 'wx', 0o600);
Horosa-Web/astrostudyui/headless/runtime.js|HEADLESS_LOCAL_KEYS.forEach((k)=>{ delete manifest.raw[k]; });
Horosa-Web/astrostudyui/headless/runtime.js|const onDisk = storage.__rawGet(UI_PREF_KEY);
Horosa-Web/astrostudyui/headless/runtime.js|fs.cpSync(dataDir(), snap, { recursive: true, filter: (src)=>path.basename(src) !== '.lock' });
Horosa-Web/astrostudyui/headless/runtime.js|if(rec.apiKey){ await requireEncryption(); }
Horosa-Web/astrostudyui/src/utils/secureKeyStore.js|const hook = bridge ? null : headlessMasterKeyHook();
Horosa-Web/astrostudyui/headless/cli.js|case '--api-key': case '--key': throw new Error(
Horosa-Web/astrostudyui/headless/build.js|const HEADLESS_BUNDLED = ['entry.js', 'aiProfiles.js', 'react-shim.js', 'build.js'];
Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js|subscribeAgentPrefs(()=>{ catalogVersion += 1; });
Horosa-Web/astrostudyui/src/services/aianalysis.js|? decodeServiceErrorText(payload.ResultMessage || payload.Result || payload.message)
Horosa-Web/astrostudyui/src/utils/__tests__/aiServiceErrorDecode.test.js|网页读取:守卫拒绝的编码说明 → 解码后归为 E_WEB_FETCH_BLOCKED
Horosa-Web/astrostudyui/src/utils/__tests__/mcpBridge.test.js|开关翻转作废目录缓存
Horosa-Web/astrostudyui/src/utils/__tests__/aiSecureKeyStore.test.js|桥在 → 钩子不被调用(桌面永远走钥匙串桥)
Horosa-Web/astrostudyui/headless/test/server.test.js|管理口:只认管理令牌(接口令牌 401、管理令牌进不了接口)
Horosa-Web/astrostudyui/headless/selftest.js|check('环境变量档案优先且不落盘'
docs/HEADLESS.md|./horosa ai add
Horosa-Web/astrostudyui/jest.config.js|.concat(['<rootDir>/headless/'])
Horosa-Web/astrostudyui/src/components/aianalysis/chat/useChatAssist.js|const techKeys = opts && Array.isArray(opts.techniqueKeys) ? opts.techniqueKeys : depsRef.current.selectedTechniqueKeys;
S321_EOF
}
S321_MISS="$(s321_scan "${REPO_ROOT}")"
[ -z "${S321_MISS}" ] || { printf '%s\n' "${S321_MISS}" | head -6 | sed 's/^/    缺 /'; bad "[${PF_NO}]① 无头模式接线被拆($(printf '%s\n' "${S321_MISS}" | wc -l | tr -d ' ') 处)"; S321_BAD=1; }
# ② 判别力自证:原样全过;管理口改回接口令牌 / 环境变量档案不再剔除 / 桥优先变成钩子优先 / 解码去掉 各自报出
s321_tmp="$(mktemp -d "${PF_TMP}/s321_tmp.XXXXXX")"
for s321_f in $(s321_scan /nonexistent | sed 's/「.*$//' | sort -u); do
  mkdir -p "${s321_tmp}/$(dirname "${s321_f}")" && cp "$(pf_src_set "${REPO_ROOT}/${s321_f}")" "${s321_tmp}/${s321_f}" 2>/dev/null
done
s321_ok=1
[ -z "$(s321_scan "${s321_tmp}")" ] || s321_ok=0
sed -i '' 's/const g = gate(req, adminToken, false);/const g = gate(req, token, false);/' "${s321_tmp}/Horosa-Web/astrostudyui/headless/server.js" 2>/dev/null
s321_scan "${s321_tmp}" | pipe_has -F "server.js「const g = gate(req, adminToken" || s321_ok=0
sed -i '' 's/name === PROVIDER_STORE ? entries.filter((e)=>e \&\& e\[0\] !== ENV_PROFILE_ID) : entries/entries/' "${s321_tmp}/Horosa-Web/astrostudyui/headless/runtime.js" 2>/dev/null
s321_scan "${s321_tmp}" | pipe_has -F "runtime.js「pending.set(name, name === PROVIDER_STORE" || s321_ok=0
sed -i '' 's/const hook = bridge ? null : headlessMasterKeyHook();/const hook = headlessMasterKeyHook();/' "${s321_tmp}/Horosa-Web/astrostudyui/src/utils/secureKeyStore.js" 2>/dev/null
s321_scan "${s321_tmp}" | pipe_has -F "secureKeyStore.js「const hook = bridge" || s321_ok=0
sed -i '' 's/? decodeServiceErrorText(payload.ResultMessage/? (payload.ResultMessage/' "${s321_tmp}/Horosa-Web/astrostudyui/src/services/aianalysis.js" 2>/dev/null
s321_scan "${s321_tmp}" | pipe_has -F "aianalysis.js「? decodeServiceErrorText" || s321_ok=0
rm -rf "${s321_tmp}"
[ "${s321_ok}" = "1" ] || { bad "[${PF_NO}]② 判别力自证失败(原样不全过,或管理口改回接口令牌 / 环境变量档案不剔 / 钩子先于桥 / 去掉解码 被改后没报出)"; S321_BAD=1; }
# ③ 合同真跑(node --test 已由 seg_319 ③ 跑过同一文件;这里只验新增的管理令牌合同名在跑出的结果里)
if command -v node >/dev/null 2>&1 && [ -d "${REPO_ROOT}/Horosa-Web/astrostudyui/node_modules" ]; then
  S321_T="$(node --test --test-name-pattern='管理' "${REPO_ROOT}/Horosa-Web/astrostudyui/headless/test/server.test.js" 2>&1)" || { printf '%s\n' "${S321_T}" | grep -aE '✖|not ok' | head -4 | sed 's/^/    /'; bad "[${PF_NO}]③ 管理口 / 人工命令合同(node --test)不过"; S321_BAD=1; }
  S321_N="$(printf '%s\n' "${S321_T}" | grep -acE '^ℹ pass [1-9]')"
  [ "${S321_N}" -ge 1 ] || { bad "[${PF_NO}]③ 管理口合同一例都没跑到(名称过滤失配?)"; S321_BAD=1; }
else
  warn "[${PF_NO}]③ 本机没有 node 或前端依赖,跳过管理口合同真跑(只做了静态锚)"
fi
[ "${S321_BAD}" = "0" ] && ok "[${PF_NO}] 无头模式:管理令牌分离 / 环境变量档案不落盘 / 存档密钥加密 / 命令行不收密钥 / 导出不带本机键 · 导入前快照 / 开关翻转作废目录缓存 / 失败说明源头解码;判别力自证 + 合同真跑"
}

seg_237() {
# [${PF_NO}] 外部智能体连接(本机 MCP 服务)锁:只绑回环;三道门顺序;工具面只放行 read/additive;
#   偏好默认关;退出钩子;页面桥零数据层 import 且在途队列键在位;布局层挂桥;面板复制零裸 writeText。
echo "[${PF_NO}] 外部智能体连接(MCP)安全锁"
S237_BAD=0
S237_RS="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs"
S237_MAIN="$(pf_shell_rs_prod)"
[ -f "${S237_RS}" ] || { bad "[${PF_NO}] mcp_server.rs 缺失"; S237_BAD=1; }
grep -aqF "0.0.0.0" "$(pf_shell_rs_prod_all)" && { bad "[${PF_NO}] 产品代码出现 0.0.0.0(必须只绑回环)"; S237_BAD=1; }
[ "$(grep -ac "\[127, 0, 0, 1\]" "${S237_RS}")" -ge 2 ] || { bad "[${PF_NO}] mcp_server.rs 回环绑定锚缺失"; S237_BAD=1; }
S237_L_HOST="$(grep -an "!host_allowed(host)" "${S237_RS}" | head -1 | cut -d: -f1)"
S237_L_ORIG="$(grep -an "!origin_allowed(origin)" "${S237_RS}" | head -1 | cut -d: -f1)"
S237_L_AUTH="$(grep -an "!bearer_allowed(authorization" "${S237_RS}" | head -1 | cut -d: -f1)"
S237_L_DISP="$(grep -anE "core.handle_rpc(_with_session)?\(&parsed, dispatcher" "${S237_RS}" | head -1 | cut -d: -f1)"
{ [ -n "${S237_L_HOST}" ] && [ -n "${S237_L_ORIG}" ] && [ -n "${S237_L_AUTH}" ] && [ -n "${S237_L_DISP}" ] && [ "${S237_L_HOST}" -lt "${S237_L_ORIG}" ] && [ "${S237_L_ORIG}" -lt "${S237_L_AUTH}" ] && [ "${S237_L_AUTH}" -lt "${S237_L_DISP}" ]; } || { bad "[${PF_NO}] 三道门顺序(Host→Origin→Bearer→dispatch)行号锚不成立"; S237_BAD=1; }
grep -aq 'level == "read" || level == "additive"' "${S237_RS}" || { bad "[${PF_NO}] filter_tools 未限定 read/additive"; S237_BAD=1; }
grep -aqF "pub fn constant_time_eq(" "$(pf_rs_prod "${S237_RS}")" || { bad "[${PF_NO}] 令牌比较非常量时间"; S237_BAD=1; }
grep -aq "mcp_server_enabled: false," "${S237_MAIN}" || { bad "[${PF_NO}] main.rs 偏好默认 mcp_server_enabled 非 false"; S237_BAD=1; }
grep -aq "agent_enabled: false," "${S237_MAIN}" || { bad "[${PF_NO}] main.rs 偏好默认 agent_enabled 非 false"; S237_BAD=1; }
grep -aq "mcp_server::stop_on_exit(app);" "${S237_MAIN}" || { bad "[${PF_NO}] spawn_exit_cleanup 未调 mcp_server::stop_on_exit"; S237_BAD=1; }
grep -aq "next.mcp_server_enabled = current.mcp_server_enabled;" "${S237_MAIN}" || { bad "[${PF_NO}] 偏好窗保存会清掉 mcp_server_enabled(须保留现值)"; S237_BAD=1; }
S237_BR="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAgent/mcpBridge.js"
grep -aqE "from '[^']*(localcharts|localcases|localRecordStore|models/|dva)'" "${S237_BR}" && { bad "[${PF_NO}] mcpBridge.js 出现数据层 import"; S237_BAD=1; }
grep -aq "__horosaPendingAgentTools" "${S237_BR}" || { bad "[${PF_NO}] mcpBridge.js 缺在途队列键"; S237_BAD=1; }
grep -aq "bindMcpBridge();" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/layouts/app.js" || { bad "[${PF_NO}] layouts/app.js 未挂 bindMcpBridge"; S237_BAD=1; }
grep -aq "writeText(" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/aianalysis/ExternalAgentPanel.js" && { bad "[${PF_NO}] ExternalAgentPanel 出现裸 writeText(须走 copyTextSmart)"; S237_BAD=1; }
[ -f "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/mcpBridge.test.js" ] || { bad "[${PF_NO}] mcpBridge.test.js 缺失"; S237_BAD=1; }
grep -aq "fn http_transport_end_to_end_and_port_released_on_stop" "${S237_RS}" || { bad "[${PF_NO}] cargo 端到端单测缺失"; S237_BAD=1; }
[ -x "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_mcp_smoke.sh" ] || { bad "[${PF_NO}] verify_mcp_smoke.sh 缺失/不可执行"; S237_BAD=1; }
# 令牌暴露面:状态查询不携带令牌(恒空串),按需 reveal 命令单独取;面板复制走 reveal
grep -aqF '"token": String::new(),' "${S237_RS}" || { bad "[${PF_NO}] mcp_server.rs status_json 仍携带令牌(须恒空,按需 reveal)"; S237_BAD=1; }
grep -aq "pub fn reveal_token" "${S237_RS}" || { bad "[${PF_NO}] mcp_server.rs 缺 reveal_token"; S237_BAD=1; }
grep -aq "mcp_server_reveal_token_command," "${S237_MAIN}" || { bad "[${PF_NO}] main.rs 未注册 mcp_server_reveal_token_command"; S237_BAD=1; }
grep -aq "desktopMcpServerRevealToken" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/aianalysis/ExternalAgentPanel.js" || { bad "[${PF_NO}] ExternalAgentPanel 复制未走 reveal 按需取令牌"; S237_BAD=1; }
# 外部桥页面侧自带超时(挂死工具不得卡死整条串行队列)
grep -aq "withTimeout(d.runTool(" "${S237_BR}" || { bad "[${PF_NO}] mcpBridge.js runTool 未包超时(挂死工具会卡死整条队列)"; S237_BAD=1; }
[ "${S237_BAD}" = "0" ] && ok "[${PF_NO}] MCP 只绑回环/三道门有序/工具面收窄/默认关/退出钩子/桥零数据层/令牌按需/桥超时"
}

seg_238() {
# [${PF_NO}] AI 助手工具目录·只增不删四层锁:禁键表含 cid;目录零删改类工具名;守卫先于 Ajv;
#   mount 永不空写 token;removeLocal* 只在 ledger.js;哨兵在位;账本键登记(敏感词面由禁词扫描那一段统一看守)。
echo "[${PF_NO}] AI 助手工具目录只增不删四层锁"
S238_BAD=0
S238_T="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiTools"
grep -aq "'cid'," "${S238_T}/catalog.js" || { bad "[${PF_NO}] FORBIDDEN_ARG_KEYS 不含 cid"; S238_BAD=1; }
grep -aq "AGENT_TOOL_LEVELS = \['read', 'additive'\]" "${S238_T}/catalog.js" || { bad "[${PF_NO}] AGENT_TOOL_LEVELS 正向集合被改"; S238_BAD=1; }
S238_NAMES="$(grep -ahoE "name: '[a-z_]+'" "${S238_T}"/tools/*.js | sed -E "s/name: '([a-z_]+)'/\1/" | sort -u)"
S238_DENY="$(echo "${S238_NAMES}" | grep -ciE "delete|remove|purge|clear|reset|overwrite|update|rename|import|export|restore|backup|undo" || true)"
[ "${S238_DENY}" = "0" ] || { bad "[${PF_NO}] 工具目录出现删改类工具名 ×${S238_DENY}"; S238_BAD=1; }
S238_NTOOLS=51
[ "$(echo "${S238_NAMES}" | grep -c .)" = "${S238_NTOOLS}" ] || { bad "[${PF_NO}] 工具目录应恰 ${S238_NTOOLS} 件,现 $(echo "${S238_NAMES}" | grep -c .)"; S238_BAD=1; }
S238_L_G="$(grep -an "const guard = guardAdditive(def.name, args, def.referenceKeys);" "${S238_T}/registry.js" | head -1 | cut -d: -f1)"
S238_L_V="$(grep -an "const validated = validateArgs(def, args);" "${S238_T}/registry.js" | head -1 | cut -d: -f1)"
{ [ -n "${S238_L_G}" ] && [ -n "${S238_L_V}" ] && [ "${S238_L_G}" -lt "${S238_L_V}" ]; } || { bad "[${PF_NO}] registry.js 守卫未先于 Ajv(removeAdditional 会剥禁键=零判别力)"; S238_BAD=1; }
grep -aq "\[ai-tools:never-empty-mount-write\]" "${S238_T}/settingsFacets.js" || { bad "[${PF_NO}] settingsFacets.js 缺 never-empty-mount-write token"; S238_BAD=1; }
S238_RM="$(grep -alE "removeLocal(Chart|Case)\(" "${S238_T}" -r | grep -v "/ledger.js$" || true)"
[ -z "${S238_RM}" ] || { bad "[${PF_NO}] removeLocalChart/Case 出现在账本之外: ${S238_RM}"; S238_BAD=1; }
S238_SM="$(grep -alE "saveMountTechniqueDefaults\(" "${S238_T}" -r | grep -vE "/(settingsFacets|ledger)\.js$" || true)"
[ -z "${S238_SM}" ] || { bad "[${PF_NO}] saveMountTechniqueDefaults 出现在 settingsFacets/ledger 之外: ${S238_SM}"; S238_BAD=1; }
grep -aq "referenceKeys: \['cid'\]" "${S238_T}/tools/loadRecordIntoWorkspace.js" || { bad "[${PF_NO}] 载入工具引用键声明缺失"; S238_BAD=1; }
[ "$(pf_prod_hits -a "referenceKeys" "${S238_T}/tools" | wc -l | tr -d ' ')" = "1" ] || { bad "[${PF_NO}] referenceKeys 只允许载入工具声明"; S238_BAD=1; }
grep -aq "'horosa.ai.agent.ledger.v1'" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/storageKeyRegistry.js" || { bad "[${PF_NO}] 账本键未登记"; S238_BAD=1; }
[ -f "${REPO_ROOT}/docs/AI_AGENT_RUNTIME.md" ] || { bad "[${PF_NO}] docs/AI_AGENT_RUNTIME.md 缺失"; S238_BAD=1; }
[ "${S238_BAD}" = "0" ] && ok "[${PF_NO}] 只增不删四层(禁键/目录/守卫序/静态)+文档在位"
}

seg_246() {
# [${PF_NO}] AI 助手交互效率与记忆(对话交互增强插座;策略写入方;目录纪律)
echo "[${PF_NO}] AI 助手交互效率与记忆(插座/策略写入方/目录纪律)"
S246_BAD=0
S246_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S246_MAIN="$(pf_src_set "${S246_UI}/src/components/aianalysis/AIAnalysisMain.js")"
S246_HIST="${S246_UI}/src/utils/aiChatHistory.js"
# 插座:AIAnalysisMain 只经 ./chat 桶 import;唯一钩子 + 浮层宿主在位
pf_imports "${S246_MAIN}" "import { useChatAssist, ChatAssistOverlays } from './chat';" || { bad "[${PF_NO}] AIAnalysisMain 缺 ./chat 插座 import"; S246_BAD=1; }
[ "$(pf_code "${S246_MAIN}" | grep -acF "const chatAssist = useChatAssist({")" = "1" ] || { bad "[${PF_NO}] useChatAssist 插座不是恰好一处"; S246_BAD=1; }
[ "$(pf_code "${S246_MAIN}" | grep -acF "<ChatAssistOverlays {...chatAssist.overlays} />")" = "1" ] || { bad "[${PF_NO}] ChatAssistOverlays 浮层宿主不是恰好一处"; S246_BAD=1; }
# 既有计数锚不得被本轮改动碰到(hunk 只增插座,不动运行时插座)
[ "$(grep -ac 'agentTrace: item.agentTrace,' "${S246_MAIN}")" = "4" ] || { bad "[${PF_NO}] 四处消息 map 计数漂移(本轮不得触碰运行时插座)"; S246_BAD=1; }
# 策略写入方(此前只读没写=八档永远跑 legacy)
for sym in "export function writeContextPolicy" "export function clearContextPolicy" "export function subscribeContextPolicy" "export const CONTEXT_POLICY_PRESETS"; do
	[ "$(pf_code "${S246_HIST}" | grep -acF "${sym}")" != "0" ] || { bad "[${PF_NO}] aiChatHistory 缺 ${sym}"; S246_BAD=1; }
done
# 目录纪律:utils/aiChat + components/aianalysis/chat 零裸 localStorage 写、零工具注册、零注册表 import
S246_DIRS="${S246_UI}/src/utils/aiChat ${S246_UI}/src/components/aianalysis/chat"
[ -d "${S246_UI}/src/utils/aiChat" ] && [ -d "${S246_UI}/src/components/aianalysis/chat" ] || { bad "[${PF_NO}] 对话交互增强目录缺失"; S246_BAD=1; }
[ "$(cat $(find ${S246_DIRS} -name '*.js' 2>/dev/null) 2>/dev/null | sed -E 's#//.*$##' | grep -acE 'localStorage\.(setItem|removeItem)\(')" = "0" ] || { bad "[${PF_NO}] 对话交互增强目录出现裸 localStorage 写"; S246_BAD=1; }
[ "$(cat $(find ${S246_DIRS} -name '*.js' 2>/dev/null) 2>/dev/null | sed -E 's#//.*$##' | grep -acE 'registerTool\(|aiTools/registry')" = "0" ] || { bad "[${PF_NO}] 对话交互增强目录注册了工具/引了注册表(口径记忆检查点永远不是工具)"; S246_BAD=1; }
# A1a 策略设置卡:设置页插座恰 1;卡在位;打开不写键的判别向量在合同测试里
[ "$(pf_code "${S246_MAIN}" | grep -acF "{chatAssist.settingsPanels}")" = "1" ] || { bad "[${PF_NO}] 设置页插座 chatAssist.settingsPanels 不是恰好一处"; S246_BAD=1; }
# [进阶页] 两处插座整体迁到 renderAdvancedPane;设置页只剩接口配置与备份。三锚:渲染函数在位 / 页签在位 / 设置页体内不再渲染插座(排空计数形态,pipefail 下不吃 SIGPIPE)。
[ "$(pf_code "${S246_MAIN}" | grep -acF "function renderAdvancedPane(")" = "1" ] || { bad "[${PF_NO}] 进阶页渲染函数 renderAdvancedPane 缺失"; S246_BAD=1; }
[ "$(pf_code "${S246_MAIN}" | grep -acF "key=\"advanced\"")" = "1" ] || { bad "[${PF_NO}] 进阶页签 key=advanced 缺失"; S246_BAD=1; }
S246_SETTINGS_BODY="$(pf_code "${S246_MAIN}" | sed -n '/function renderSettingsPane(){/,/^\tfunction /p')"
[ "$(printf '%s\n' "${S246_SETTINGS_BODY}" | grep -acF "chatAssist.settingsPanels")" = "0" ] || { bad "[${PF_NO}] 设置页仍渲染 settingsPanels 插座(应已迁到进阶页)"; S246_BAD=1; }
[ -f "${S246_UI}/src/components/aianalysis/chat/AdvancedPane.js" ] && [ -f "${S246_UI}/src/components/aianalysis/chat/AdvCard.js" ] && [ -f "${S246_UI}/src/utils/__tests__/aiAdvancedPane.test.js" ] || { bad "[${PF_NO}] 进阶页组件/外壳/合同测试缺失"; S246_BAD=1; }
[ -f "${S246_UI}/src/components/aianalysis/chat/ChatContextPolicyPanel.js" ] && [ -f "${S246_UI}/src/utils/aiChat/policyPanel.js" ] || { bad "[${PF_NO}] 对话上下文策略设置卡缺失"; S246_BAD=1; }
# A2 状态栏:输入区插座恰 1;组件在位;纯展示零 localStorage 写(目录纪律已覆盖)
[ "$(pf_code "${S246_MAIN}" | grep -acF "{chatAssist.statusBarNode}")" = "1" ] || { bad "[${PF_NO}] 状态栏插座 chatAssist.statusBarNode 不是恰好一处"; S246_BAD=1; }
[ -f "${S246_UI}/src/components/aianalysis/chat/ChatStatusBar.js" ] || { bad "[${PF_NO}] ChatStatusBar 缺失"; S246_BAD=1; }
for t in aiChatPolicyWrite aiChatStatus aiChatShortCall aiChatPolicyPanel aiChatStatusBar; do
	[ -f "${S246_UI}/src/utils/__tests__/${t}.test.js" ] || { bad "[${PF_NO}] 合同测试 ${t}.test.js 缺失"; S246_BAD=1; }
done
# A1b 聊天 lane A/B 驱动器:驱动器多轮/臂展开;套件+分析器+自检在位;线束 --ab;Java DeepSeek 缓存命中映射
[ "$(grep -acF 'prompt_cache_hit_tokens' "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java")" != "0" ] || { bad "[${PF_NO}] Java 未映射 DeepSeek 顶层 prompt_cache_hit_tokens(A/B 缓存命中恒空)"; S246_BAD=1; }
# A3 斜杠命令 + 技能包:命令面板插座恰 1 + 发送口拦截恰 1(按钮/回车同一入口)+ 解析规则(首字符 / 且次字符非 /)+ capture 阶段 keydown + IME 不拦 + 内置技能 + 跨页跳转桥 + 合同
[ "$(pf_code "${S246_MAIN}" | grep -acF "<ComposerAssist {...chatAssist.composer} />")" = "1" ] && [ "$(pf_code "${S246_MAIN}" | grep -acF "chatAssist.interceptSend(trimmed)")" = "1" ] || { bad "[${PF_NO}] 命令面板插座/发送口拦截不是恰一处"; S246_BAD=1; }
S246_CMD="${S246_UI}/src/utils/aiChat/commands.js"
[ "$(pf_code "${S246_CMD}" | grep -acF "if(s.length < 2 || s[0] !== '/' || s[1] === '/'){ return null; }")" = "1" ] && [ "$(pf_code "${S246_CMD}" | grep -acF "export function listCommandItems(")" = "1" ] || { bad "[${PF_NO}] 斜杠解析规则锚缺失(// 与正文中的 / 不得成为命令)"; S246_BAD=1; }
S246_CA="${S246_UI}/src/components/aianalysis/chat/ComposerAssist.js"
[ "$(pf_code "${S246_CA}" | grep -acF "ta.addEventListener('keydown', onKey, true);")" = "1" ] && [ "$(pf_code "${S246_CA}" | grep -acF "if(e.isComposing || e.keyCode === 229){ return; }")" = "1" ] || { bad "[${PF_NO}] 命令面板须 capture 阶段拦键且 IME 组合期不拦"; S246_BAD=1; }
[ "$(pf_code "${S246_UI}/src/utils/aiChat/skills.js" | grep -acF "export const BUILTIN_SKILLS = [")" = "1" ] && [ "$(pf_code "${S246_UI}/src/utils/aiChat/skills.js" | grep -acF "export function planSkillImport(")" = "1" ] || { bad "[${PF_NO}] 技能包模块缺内置技能/导入判定"; S246_BAD=1; }
[ "$(pf_code "${S246_UI}/src/pages/index.js" | grep -acF "window.addEventListener('horosa:navigate', onNav);")" = "1" ] || { bad "[${PF_NO}] 跨页跳转桥 horosa:navigate 缺失(/择日 无处可去)"; S246_BAD=1; }
[ -f "${S246_UI}/src/components/aianalysis/chat/SkillPackPanel.js" ] || { bad "[${PF_NO}] 技能包设置卡缺失"; S246_BAD=1; }
for t in aiChatCommands aiChatSkills aiChatComposer; do [ -f "${S246_UI}/src/utils/__tests__/${t}.test.js" ] || { bad "[${PF_NO}] 合同测试 ${t}.test.js 缺失"; S246_BAD=1; }; done
# A4 @引用:候选/解析/挂载计划纯模块 + 技法段过滤复用导出段切分 + Main 技法段插座恰 1 + 邮箱/全角不算 @ 的合同
S246_MN="${S246_UI}/src/utils/aiChat/mentions.js"
[ -s "${S246_MN}" ] && [ "$(pf_code "${S246_MN}" | grep -acF "export function findMentionQuery(")" = "1" ] && [ "$(pf_code "${S246_MN}" | grep -acF "export function resolveMentions(")" = "1" ] || { bad "[${PF_NO}] mentions.js 缺 @查询定位/挂载计划"; S246_BAD=1; }
[ "$(pf_code "${S246_MN}" | grep -acF "if(i > 0 && isWordChar(s[i - 1])){ return null; }")" = "1" ] || { bad "[${PF_NO}] @ 前是邮箱字符须不算命令的判据缺失"; S246_BAD=1; }
[ "$(pf_code "${S246_UI}/src/utils/aiChat/sectionFilter.js" | grep -acF "export function filterContentSections(")" = "1" ] && [ "$(pf_code "${S246_UI}/src/utils/aiChat/sectionFilter.js" | grep -acF "filterContentByWantedSections(text, new Set(list))")" = "1" ] || { bad "[${PF_NO}] 技法段过滤须复用导出段切分器"; S246_BAD=1; }
[ "$(pf_code "${S246_MAIN}" | grep -acF "chatAssist.filterTechniqueSections(")" = "1" ] || { bad "[${PF_NO}] 技法段过滤插座不是恰一处"; S246_BAD=1; }
[ -f "${S246_UI}/src/utils/__tests__/aiChatMentions.test.js" ] || { bad "[${PF_NO}] 合同测试 aiChatMentions.test.js 缺失"; S246_BAD=1; }
# A5 压缩/旁问/回退:主线视图 mainline 恰 6(四发送口+历史层+Q-055① 模版变量 conversation_history 渲染)· 附加稳定层插座恰 1 · 检查点落库恰 1 · 回退按钮恰 1 · 摘要层 priority 88 · 旁问不落库不带工具 · checkpoint.js 零工具注册 · 合同
[ "$(pf_code "${S246_MAIN}" | grep -acF "chatAssist.mainline(")" = "6" ] && [ "$(pf_code "${S246_MAIN}" | grep -acF "extraLayers: chatAssist.promptLayerExtras(turnScope.turnOnly ? { techniqueKeys: keysThisTurn } : undefined),")" = "1" ] && [ "$(pf_code "${S246_MAIN}" | grep -acF "checkpoint: chatAssist.buildCheckpoint(),")" = "1" ] && [ "$(pf_code "${S246_MAIN}" | grep -acF "chatAssist.openRewind(item)")" = "1" ] || { bad "[${PF_NO}] 压缩/检查点/回退插座计数不对(mainline 5/extraLayers 1/checkpoint 1/openRewind 1)"; S246_BAD=1; }
[ "$(pf_code "${S246_UI}/src/utils/aiChat/compact.js" | grep -acF "export const COMPACT_LAYER_PRIORITY = 88;")" = "1" ] && [ "$(pf_code "${S246_UI}/src/utils/aiChat/compact.js" | grep -acF "export function applyCompact(")" = "1" ] || { bad "[${PF_NO}] compact.js 缺摘要层 88/主线视图"; S246_BAD=1; }
[ "$(pf_code "${S246_UI}/src/utils/aiAnalysisContext.js" | grep -acF "extraLayers,")" = "1" ] || { bad "[${PF_NO}] buildContextLayers 缺 extraLayers 参数(摘要/口径/记忆层无处可进)"; S246_BAD=1; }
[ "$(pf_code "${S246_UI}/src/utils/aiChat/checkpoint.js" | grep -acE 'registerTool\(|aiTools/registry|aiTools/ledger')" = "0" ] && [ "$(pf_code "${S246_UI}/src/utils/aiChat/checkpoint.js" | grep -acF "export function planRewind(")" = "1" ] || { bad "[${PF_NO}] checkpoint.js 须纯计划(零注册表/账本 import)且有 planRewind"; S246_BAD=1; }
[ "$(pf_code "${S246_UI}/src/components/aianalysis/chat/SideQuestionPanel.js" | grep -acE 'saveConversationMessage|tools:')" = "0" ] || { bad "[${PF_NO}] 旁问面板不得落库/不得带工具"; S246_BAD=1; }
[ "$(pf_code "${S246_UI}/src/components/aianalysis/chat/useChatAssist.js" | grep -acF "const r = undoAction(actionIds[i]);")" = "1" ] || { bad "[${PF_NO}] 回退须先逐条撤销再删消息"; S246_BAD=1; }
for t in aiChatCompact aiChatCheckpoint aiChatSide; do [ -f "${S246_UI}/src/utils/__tests__/${t}.test.js" ] || { bad "[${PF_NO}] 合同测试 ${t}.test.js 缺失"; S246_BAD=1; }; done
# A6 口径/记忆/命主工作区:键登记 + 口径层 102/记忆层 101 常量 + 缺省全关判据 + memory/persona 零工具面 + 记忆注入封顶 1500 + 设置卡/抽屉在位 + 合同
[ "$(grep -acF "'horosa.ai.persona.v1'" "${S246_UI}/src/utils/storageKeyRegistry.js")" != "0" ] && [ "$(grep -acF "'horosa.ai.persona.v1'" "${S246_UI}/src/utils/techniqueOnboardingContract.js")" != "0" ] || { bad "[${PF_NO}] horosa.ai.persona.v1 未登记"; S246_BAD=1; }
S246_PS="${S246_UI}/src/utils/aiChat/persona.js"; S246_MM="${S246_UI}/src/utils/aiChat/memory.js"
[ "$(pf_code "${S246_PS}" | grep -acF "export const PERSONA_LAYER_PRIORITY = 102;")" = "1" ] && [ "$(pf_code "${S246_PS}" | grep -acF "export const MEMORY_LAYER_PRIORITY = 101;")" = "1" ] && [ "$(pf_code "${S246_PS}" | grep -acF "enabled: r.enabled === true,")" = "1" ] || { bad "[${PF_NO}] 口径/记忆层优先级或缺省关判据锚缺失"; S246_BAD=1; }
[ "$(pf_code "${S246_MM}" | grep -acF "export const MEMORY_DIRECTIVE_MAX = 1500;")" = "1" ] && [ "$(pf_code "${S246_MM}" | grep -acF "export const MEMORY_CANDIDATE_MAX = 50;")" = "1" ] || { bad "[${PF_NO}] 记忆封顶常量锚缺失"; S246_BAD=1; }
[ "$(cat "${S246_PS}" "${S246_MM}" | sed -E 's#//.*$##' | grep -acE 'aiTools/|registerTool\(')" = "0" ] || { bad "[${PF_NO}] persona/memory 引了工具面(口径记忆不得成为工具)"; S246_BAD=1; }
[ -f "${S246_UI}/src/components/aianalysis/chat/PersonaMemoryPanel.js" ] && [ -f "${S246_UI}/src/components/aianalysis/chat/SubjectWorkspaceDrawer.js" ] || { bad "[${PF_NO}] 口径/记忆设置卡或命主工作区抽屉缺失"; S246_BAD=1; }
[ "$(pf_code "${S246_UI}/src/components/aianalysis/chat/useChatAssist.js" | grep -acF "if(!personaRef.current.memoryCapture){ return; }")" = "1" ] || { bad "[${PF_NO}] 自动沉淀候选缺缺省关门"; S246_BAD=1; }
for t in aiChatPersona aiChatMemory aiChatSubjectWorkspace; do [ -f "${S246_UI}/src/utils/__tests__/${t}.test.js" ] || { bad "[${PF_NO}] 合同测试 ${t}.test.js 缺失"; S246_BAD=1; }; done
[ "${S246_BAD}" = "0" ] && ok "[${PF_NO}] AI 助手交互效率与记忆(插座/策略写入方/目录纪律)"
}

seg_250() {
# [${PF_NO}] AI 多模型对比 / 审阅 / 编排(C5-C7):候选上限 4 单源;候选流不得带工具;历史只带采用稿(四处 map);成本确认;判官 strict;合同在位
echo "[${PF_NO}] AI 多模型对比/审阅/编排(候选 4/无工具/采用稿进历史/成本确认)"
S250_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S250_BAD=0
S250_BO="${S250_UI}/src/utils/aiBestOfN.js"; S250_HK="${S250_UI}/src/components/aianalysis/chat/useChatBestOf.js"; S250_MAIN="$(pf_src_set "${S250_UI}/src/components/aianalysis/AIAnalysisMain.js")"
[ -s "${S250_BO}" ] && [ "$(pf_code "${S250_BO}" | grep -acF "export const MAX_CANDIDATES = 4;")" = "1" ] && [ "$(pf_code "${S250_BO}" | grep -acF "export function estimateCandidatesCost(")" = "1" ] && [ "$(pf_code "${S250_BO}" | grep -acF "export function historyContentOf(")" = "1" ] || { bad "[${PF_NO}] aiBestOfN 缺候选上限/成本估算/采用稿取值单源"; S250_BAD=1; }
[ -s "${S250_HK}" ] && [ "$(pf_code "${S250_HK}" | grep -acE 'tools: |toolChoice: |toolDefs\(\)')" = "0" ] || { bad "[${PF_NO}] 候选流带了工具(对比模式只回答不执行动作)"; S250_BAD=1; }
[ "$(pf_code "${S250_HK}" | grep -acF "applyResponseSchema(opts, { name: 'bestof_judge', schema: JUDGE_SCHEMA })")" = "1" ] && [ "$(pf_code "${S250_HK}" | grep -acF "resolveRoute('judge'")" = "1" ] || { bad "[${PF_NO}] 判官须 strict schema 且走 judge 路由槽"; S250_BAD=1; }
S250_PAT_COST="if(typeof confirmCost === 'function'){ const ok = await confirmCost({ candidates, est });"  # 先赋值再引用:bash 3.2 会把 $( … ) 内紧贴括号的 { a, b } 花括号展开(见 seg_262 里同名注)
[ "$(pf_code "${S250_HK}" | grep -acF "${S250_PAT_COST}")" = "1" ] || { bad "[${PF_NO}] 发送前成本确认门缺失(2026-09-08 起无价档也弹「费用未知」确认)"; S250_BAD=1; }
[ "$(pf_code "${S250_MAIN}" | grep -acF "content: historyContentOf(item),")" = "4" ] && [ "$(pf_code "${S250_MAIN}" | grep -acF "{chatAssist.bestOfCards(item)}")" = "1" ] && [ "$(grep -ac 'agentTrace: item.agentTrace,' "${S250_MAIN}")" = "4" ] || { bad "[${PF_NO}] Main 四处 map 未改 historyContentOf / 卡片插座不是恰一处 / agentTrace 计数漂移"; S250_BAD=1; }
for t in aiBestOfN aiChatBestOf; do [ -f "${S250_UI}/src/utils/__tests__/${t}.test.js" ] || { bad "[${PF_NO}] 合同测试 ${t}.test.js 缺失"; S250_BAD=1; }; done
# C6 审阅:共享纯模块零生成管线/事实核对 import(负锚);schema strict 四类含 ungrounded;跨家族挑选单源;钩子零工具、strict 审阅、重写稿 rewriteOf/被替代稿 supersededBy;Main 两插座;主线剔除被替代稿
S250_RV="${S250_UI}/src/utils/aiReview.js"; S250_RH="${S250_UI}/src/components/aianalysis/chat/useChatReview.js"; S250_CA="${S250_UI}/src/components/aianalysis/chat/useChatAssist.js"
[ -s "${S250_RV}" ] && [ "$(pf_code "${S250_RV}" | grep -aE "^[[:space:]]*import[[:space:]]|require\(|import\(" | grep -avcF "'./aiAnalysisProviders'")" = "0" ] || { bad "[${PF_NO}] aiReview.js 引了模型档案解析以外的模块(生成管线 / 事实核对等确定性问题只许调用方注入)"; S250_BAD=1; }
[ "$(pf_code "${S250_RV}" | grep -acF "export const REVIEW_SCHEMA = {")" = "1" ] && [ "$(pf_code "${S250_RV}" | grep -acF "'ungrounded'")" -ge 1 ] && [ "$(pf_code "${S250_RV}" | grep -acF "export function pickReviewModel(")" = "1" ] || { bad "[${PF_NO}] aiReview 缺 REVIEW_SCHEMA/ungrounded 类/跨家族挑选单源"; S250_BAD=1; }
[ -s "${S250_RH}" ] && [ "$(pf_code "${S250_RH}" | grep -acE 'tools: |toolChoice: |toolDefs\(\)')" = "0" ] && [ "$(pf_code "${S250_RH}" | grep -acF "applyResponseSchema(opts, { name: 'answer_review', schema: REVIEW_SCHEMA })")" = "1" ] && [ "$(pf_code "${S250_RH}" | grep -acF "rewriteOf: cur.id")" = "1" ] && [ "$(pf_code "${S250_RH}" | grep -acF "supersededBy: placeholder.id")" = "1" ] || { bad "[${PF_NO}] 审阅钩子须零工具/strict 审阅/重写稿 rewriteOf/原稿 supersededBy"; S250_BAD=1; }
[ "$(pf_code "${S250_CA}" | grep -acF "const review = useChatReview(depsRef, { mainline });")" = "1" ] && [ "$(pf_code "${S250_CA}" | grep -acF "m.supersededBy || (m.role === 'assistant' && isPlaceholderAssistantContent(m.content))")" = "1" ] && [ "$(pf_code "${S250_CA}" | grep -acF "out.some(drop) ? out.filter((m)=>!drop(m)) : out")" = "1" ] || { bad "[${PF_NO}] useChatAssist 缺审阅插座或主线未剔除被替代稿"; S250_BAD=1; }
[ "$(pf_code "${S250_MAIN}" | grep -acF "{chatAssist.reviewNotes(item)}")" = "1" ] && [ "$(pf_code "${S250_MAIN}" | grep -acF "chatAssist.review.run(item)")" = "1" ] || { bad "[${PF_NO}] AIAnalysisMain 审阅插座(批注/按钮)缺失或重复"; S250_BAD=1; }
for t in aiReview aiChatReview; do [ -f "${S250_UI}/src/utils/__tests__/${t}.test.js" ] || { bad "[${PF_NO}] 合同测试 ${t}.test.js 缺失"; S250_BAD=1; }; done
# C7 编排:限额单源(子任务 4/子轮 3/零写入/并行 3;负锚:编排件不得出现非零 MAX_ADDITIVE_PER_TURN);只读注册表视图在位且钩子用它+限额常量;子开关 '1' 门;面板插座;键登记;合同测试
S250_OR="${S250_UI}/src/utils/aiAgent/orchestrator.js"; S250_OH="${S250_UI}/src/components/aianalysis/chat/useChatOrchestrate.js"; S250_PF="${S250_UI}/src/utils/aiAgent/prefs.js"
[ -s "${S250_OR}" ] && [ "$(pf_code "${S250_OR}" | grep -acF "MAX_SUBTASKS: 4, SUB_MAX_ROUNDS: 3, SUB_MAX_ADDITIVE: 0, PARALLEL: 3")" = "1" ] && [ "$(pf_code "${S250_OR}" | grep -acF "export function readOnlyRegistryView(")" = "1" ] || { bad "[${PF_NO}] orchestrator 缺限额单源(子任务 4/子轮 3/零写入/并行 3)或只读注册表视图"; S250_BAD=1; }
[ "$(cat "${S250_OR}" "${S250_OH}" | grep -acE 'MAX_ADDITIVE_PER_TURN: [1-9]')" = "0" ] || { bad "[${PF_NO}] 编排件出现非零 MAX_ADDITIVE_PER_TURN(子任务必须零写入)"; S250_BAD=1; }
[ -s "${S250_OH}" ] && [ "$(pf_code "${S250_OH}" | grep -acF "MAX_ROUNDS: ORCH_LIMITS.SUB_MAX_ROUNDS, MAX_ADDITIVE_PER_TURN: ORCH_LIMITS.SUB_MAX_ADDITIVE")" = "1" ] && [ "$(pf_code "${S250_OH}" | grep -acF "registry: defaultReadOnlyRegistry()")" = "1" ] && [ "$(pf_code "${S250_OH}" | grep -acF "!isOrchestrateEnabled()")" = "1" ] || { bad "[${PF_NO}] 编排钩子须用限额常量+只读注册表视图+子开关门"; S250_BAD=1; }
[ "$(pf_code "${S250_PF}" | grep -acF "export const AGENT_ORCH_ENABLED_KEY = 'horosa.ai.orchestrate.enabled';")" = "1" ] && [ "$(pf_code "${S250_PF}" | grep -acF "return safeLocalStorageGet(AGENT_ORCH_ENABLED_KEY) === '1';")" = "1" ] && [ "$(grep -acF "key: 'horosa.ai.orchestrate.enabled'" "${S250_UI}/src/utils/storageKeyRegistry.js")" = "1" ] || { bad "[${PF_NO}] 编排子开关键未登记或判据不是 === '1'"; S250_BAD=1; }
[ "$(pf_code "${S250_MAIN}" | grep -acF "{chatAssist.orchestrationPanel(item)}")" = "1" ] || { bad "[${PF_NO}] AIAnalysisMain 编排面板插座缺失或重复"; S250_BAD=1; }
for t in aiAgentOrchestrator aiChatOrchestrate; do [ -f "${S250_UI}/src/utils/__tests__/${t}.test.js" ] || { bad "[${PF_NO}] 合同测试 ${t}.test.js 缺失"; S250_BAD=1; }; done
[ "${S250_BAD}" = "0" ] && ok "[${PF_NO}] AI 多模型对比/审阅/编排(候选 4/无工具/采用稿进历史/成本确认)"
}

seg_247() {
# [${PF_NO}] AI 助手行动能力 v2·P0(审批三档/类别收紧/信任档案/反问等待台/账本面板/外部客户端档;三新工具)
echo "[${PF_NO}] AI 助手行动能力 v2·P0(审批三档/反问/账本面板/外部客户端档)"
S247_BAD=0
S247_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S247_AG="${S247_UI}/src/utils/aiAgent"
S247_T="${S247_UI}/src/utils/aiTools"
S247_C="${S247_UI}/src/components/aianalysis"
# ① 审批三档:值域含 read-only;运行时经纯函数判定(不再裸比 mode);deny → E_APPROVAL_DENIED
[ "$(pf_code "${S247_AG}/prefs.js" | grep -acF "AGENT_APPROVAL_MODES = ['never', 'on-request', 'read-only']")" = "1" ] || { bad "[${PF_NO}] prefs.js 审批档值域不是 never|on-request|read-only"; S247_BAD=1; }
[ "$(pf_code "${S247_AG}/runtime.js" | grep -acF "resolveApprovalDecision({")" != "0" ] || { bad "[${PF_NO}] runtime.js 未经 resolveApprovalDecision 判定审批"; S247_BAD=1; }
[ "$(pf_code "${S247_AG}/runtime.js" | grep -acF "'E_APPROVAL_DENIED'")" != "0" ] || { bad "[${PF_NO}] runtime.js 缺 E_APPROVAL_DENIED 拒绝支"; S247_BAD=1; }
# ② 信任档案只放行 workspace/query(建档/改设置永不因信任放行)
[ "$(pf_code "${S247_AG}/approvalPolicy.js" | grep -acF "const TRUST_CATEGORIES = ['workspace', 'query'];")" = "1" ] || { bad "[${PF_NO}] approvalPolicy 信任放行集合被改(只能 workspace/query)"; S247_BAD=1; }
# ③ 反问等待台:ask_user 在位、无通道回 E_ELICIT_UNAVAILABLE;AIAnalysisMain 插座恰 1;动作条渲染反问行;守则第 6 条
[ "$(grep -acF "name: 'ask_user'," "${S247_T}/tools/askUser.js")" = "1" ] || { bad "[${PF_NO}] ask_user 工具缺失"; S247_BAD=1; }
[ "$(pf_code "${S247_T}/tools/askUser.js" | grep -acF "'E_ELICIT_UNAVAILABLE'")" != "0" ] || { bad "[${PF_NO}] ask_user 无通道未回 E_ELICIT_UNAVAILABLE"; S247_BAD=1; }
[ "$(pf_code "${S247_C}/AIAnalysisMain.js" | grep -acF "requestElicitation: (q)=>requestAgentElicitation(assistantMessage.id, q),")" = "1" ] || { bad "[${PF_NO}] AIAnalysisMain 反问插座不是恰好一处"; S247_BAD=1; }
[ "$(grep -acF 'data-agent-elicitation="1"' "${S247_C}/AgentActionBar.js")" != "0" ] || { bad "[${PF_NO}] AgentActionBar 未渲染反问作答行"; S247_BAD=1; }
[ "$(pf_code "${S247_AG}/protocol.js" | grep -acF "ask_user")" != "0" ] || { bad "[${PF_NO}] AGENT_SYSTEM_RULES 缺 ask_user 守则"; S247_BAD=1; }
# ④ 账本面板:在位、挂在能力面板、订阅账本事件;list_actions/search_materials 工具在位
[ -f "${S247_C}/ActionLedgerPanel.js" ] || { bad "[${PF_NO}] ActionLedgerPanel.js 缺失(外部动作不可见不可撤)"; S247_BAD=1; }
[ "$(grep -acF "<ActionLedgerPanel />" "${S247_C}/AgentAbilityPanel.js")" = "1" ] || { bad "[${PF_NO}] AgentAbilityPanel 未挂账本面板"; S247_BAD=1; }
[ "$(pf_code "${S247_T}/ledger.js" | grep -acF "export function subscribeLedger")" = "1" ] || { bad "[${PF_NO}] ledger.js 缺 subscribeLedger"; S247_BAD=1; }
[ "$(grep -acF "name: 'list_actions'," "${S247_T}/tools/listActions.js")" = "1" ] || { bad "[${PF_NO}] list_actions 工具缺失"; S247_BAD=1; }
[ "$(grep -acF "name: 'search_materials'," "${S247_T}/tools/searchMaterials.js")" = "1" ] || { bad "[${PF_NO}] search_materials 工具缺失"; S247_BAD=1; }
# ⑤ 外部客户端档:桥不再导出外部工具(防回环)、读外部档、只读直拒、限流 E_LIMIT;注销只限 external;禁用判定在 getTool 后 guardAdditive 前
[ "$(pf_code "${S247_AG}/mcpBridge.js" | grep -acE "exportToolManifest\(\{ includeExternal: false, origin: .mcp. \}\)")" != "0" ] || { bad "[${PF_NO}] mcpBridge tools/list 未排除外部工具(再导出回环)"; S247_BAD=1; }
[ "$(pf_code "${S247_AG}/mcpBridge.js" | grep -acF "getExternalPolicy()")" != "0" ] || { bad "[${PF_NO}] mcpBridge 未读外部客户端档"; S247_BAD=1; }
[ "$(pf_code "${S247_AG}/mcpBridge.js" | grep -acF "'E_APPROVAL_DENIED'")" != "0" ] || { bad "[${PF_NO}] mcpBridge 只读档未直拒写入"; S247_BAD=1; }
[ "$(pf_code "${S247_AG}/mcpBridge.js" | grep -acF "code: 'E_LIMIT'")" != "0" ] || { bad "[${PF_NO}] mcpBridge 缺限流 E_LIMIT"; S247_BAD=1; }
[ "$(pf_code "${S247_T}/registry.js" | grep -acF "if(!def || def.origin !== 'external'){ return false; }")" = "1" ] || { bad "[${PF_NO}] registry.unregisterTool 未限定只注销 external(只增不删失守)"; S247_BAD=1; }
S247_L_GET="$(grep -an "const def = getTool(name);" "${S247_T}/registry.js" | head -1 | cut -d: -f1)"
S247_L_DIS="$(grep -an "if(!toolEnabled(def)){" "${S247_T}/registry.js" | head -1 | cut -d: -f1)"
S247_L_GRD="$(grep -an "const guard = guardAdditive(def.name, args, def.referenceKeys);" "${S247_T}/registry.js" | head -1 | cut -d: -f1)"
{ [ -n "${S247_L_GET}" ] && [ -n "${S247_L_DIS}" ] && [ -n "${S247_L_GRD}" ] && [ "${S247_L_GET}" -lt "${S247_L_DIS}" ] && [ "${S247_L_DIS}" -lt "${S247_L_GRD}" ]; } || { bad "[${PF_NO}] registry.js 禁用判定不在 getTool 之后、guardAdditive 之前"; S247_BAD=1; }
# ⑥ 三键登记(注册表 + 上线合同)+ 六码进冻结表与文档表
for k in horosa.ai.agent.approval.categories.v1 horosa.ai.agent.trust.records.v1 horosa.ai.agent.external.policy.v1; do
	[ "$(grep -acF "'${k}'" "${S247_UI}/src/utils/storageKeyRegistry.js")" != "0" ] || { bad "[${PF_NO}] storageKeyRegistry 未登记 ${k}"; S247_BAD=1; }
	[ "$(grep -acF "'${k}'" "${S247_UI}/src/utils/techniqueOnboardingContract.js")" != "0" ] || { bad "[${PF_NO}] techniqueOnboardingContract 未登记 ${k}"; S247_BAD=1; }
done
for c in E_APPROVAL_DENIED E_TOOL_DISABLED E_ELICIT_UNAVAILABLE E_ELICIT_TIMEOUT E_ELICIT_DECLINED E_MATERIAL_INDEX_EMPTY; do
	[ "$(grep -acF "${c}" "${S247_T}/errorCodes.js")" != "0" ] || { bad "[${PF_NO}] errorCodes.js 缺 ${c}"; S247_BAD=1; }
	[ "$(grep -acF "\`${c}\`" "${REPO_ROOT}/docs/AI_AGENT_RUNTIME.md")" != "0" ] || { bad "[${PF_NO}] AI_AGENT_RUNTIME §8 缺 ${c}"; S247_BAD=1; }
done
# ⑦ 合同测试在位
for t in aiAgentApprovalPolicy aiAgentElicitations aiToolsAskUser aiToolsListActions aiToolsSearchMaterials; do
	[ -f "${S247_UI}/src/utils/__tests__/${t}.test.js" ] || { bad "[${PF_NO}] 合同测试 ${t}.test.js 缺失"; S247_BAD=1; }
done
# ⑧ 任务中心:IDB 升版四 store;任务/通知模块;布局接线;桌面通知命令(偏好门+脱敏+限流,标题正文只经清洗);键登记;合同在位
S247_ST="${S247_UI}/src/utils/aiAnalysisStore.js"
S247_DBV=7
[ "$(pf_code "${S247_ST}" | grep -acF "const DB_VERSION = ${S247_DBV};")" = "1" ] || { bad "[${PF_NO}] aiAnalysisStore DB_VERSION ≠ ${S247_DBV}(任务中心四 store 需升版同车)"; S247_BAD=1; }
for st in agent_tasks agent_notices automation_rules integration_profiles; do [ "$(grep -acF "'${st}'" "${S247_ST}")" != "0" ] || { bad "[${PF_NO}] aiAnalysisStore 缺 store ${st}"; S247_BAD=1; }; done
[ "$(pf_code "${S247_ST}" | grep -acF "function isSecretStore(storeName)")" = "1" ] && [ "$(pf_code "${S247_ST}" | grep -acF "storeName === AI_ANALYSIS_STORES.providerProfiles")" = "0" ] || { bad "[${PF_NO}] 密钥钩未泛化到 integration_profiles(联网检索 key 将明文落库)"; S247_BAD=1; }
for f in taskStore.js noticeStore.js taskRegistry.js reconcile.js index.js; do [ -s "${S247_UI}/src/utils/aiAgent/tasks/$f" ] || { bad "[${PF_NO}] aiAgent/tasks/$f 缺失"; S247_BAD=1; }; done
[ "$(pf_code "${S247_UI}/src/layouts/app.js" | grep -acF "bindTaskCenter();")" = "1" ] && [ "$(pf_code "${S247_UI}/src/layouts/app.js" | grep -acF "<TaskCenterBell />")" = "1" ] || { bad "[${PF_NO}] app.js 未接任务中心(对账/铃铛)"; S247_BAD=1; }
[ "$(pf_code "${S247_UI}/src/utils/aiAgent/tasks/noticeStore.js" | grep -acF "safeLocalStorageGet(DESKTOP_NOTIFY_KEY) === '1'")" = "1" ] || { bad "[${PF_NO}] 桌面通知开关判据不是 === 1"; S247_BAD=1; }
[ "$(grep -acF "'horosa.notify.desktop'" "${S247_UI}/src/utils/storageKeyRegistry.js")" != "0" ] && [ "$(grep -acF "'horosa.notify.desktop'" "${S247_UI}/src/utils/techniqueOnboardingContract.js")" != "0" ] || { bad "[${PF_NO}] horosa.notify.desktop 未登记"; S247_BAD=1; }
S247_RS="$(pf_shell_rs_prod)"
[ "$(grep -acF "show_desktop_notification_command," "${S247_RS}")" = "1" ] && [ "$(grep -acF "fn sanitize_notification_text(" "${S247_RS}")" = "1" ] && [ "$(grep -acF "fn notify_limiter_decide(" "${S247_RS}")" = "1" ] || { bad "[${PF_NO}] main.rs 缺桌面通知命令/清洗/限流"; S247_BAD=1; }
[ "$(grep -acF "show_macos_notification(&t, &b);" "${S247_RS}")" = "1" ] && [ "$(grep -acF "show_macos_notification(&title" "$(pf_shell_rs_prod_all)")" = "0" ] || { bad "[${PF_NO}] 桌面通知命令把未清洗的标题/正文直传 osascript"; S247_BAD=1; }
[ "$(grep -acF "mod desktop_notify_tests" "$(pf_shell_rs_tests)")" = "1" ] || { bad "[${PF_NO}] 桌面通知 cargo 单测缺失"; S247_BAD=1; }
for t in agentTaskStore agentNoticeStore agentTaskReconcile taskCenterPanel; do [ -f "${S247_UI}/src/utils/__tests__/${t}.test.js" ] || { bad "[${PF_NO}] 合同测试 ${t}.test.js 缺失"; S247_BAD=1; }; done
# ⑨ 目标任务:运行器与工具;子开关缺省关(=== '1');autoStart 脱离当前调用栈;撤销支只许未开始;任务中心入口;合同在位
S247_GR="${S247_UI}/src/utils/aiAgent/goalRunner.js"
[ -s "${S247_GR}" ] && [ "$(pf_code "${S247_GR}" | grep -acF "export async function runHeadlessTurn(")" = "1" ] && [ "$(pf_code "${S247_GR}" | grep -acF "export async function startGoalTask(")" = "1" ] || { bad "[${PF_NO}] goalRunner 缺 runHeadlessTurn/startGoalTask"; S247_BAD=1; }
[ "$(pf_code "${S247_GR}" | grep -acF "setTimeout(()=>{ startGoalTask(task.id)")" = "1" ] || { bad "[${PF_NO}] createGoalTask autoStart 未脱离当前调用栈(工具执行中不得再起 Turn)"; S247_BAD=1; }
[ "$(pf_code "${S247_UI}/src/utils/aiAgent/prefs.js" | grep -acF "safeLocalStorageGet(AGENT_GOAL_ENABLED_KEY) === '1'")" = "1" ] || { bad "[${PF_NO}] 目标任务子开关判据不是 === 1"; S247_BAD=1; }
[ "$(grep -acF "enabled: ()=>isGoalEnabled()," "${S247_T}/tools/createGoalTask.js")" = "1" ] && [ "$(grep -acF "undoKind: 'cancel-task'," "${S247_T}/tools/createGoalTask.js")" = "1" ] || { bad "[${PF_NO}] create_goal_task 缺开关门/撤销支"; S247_BAD=1; }
[ "$(pf_code "${S247_UI}/src/utils/aiAgent/tasks/index.js" | grep -acF "registerUndoHandler('cancel-task', cancelTaskUndoHandler)")" = "1" ] && [ "$(pf_code "${S247_UI}/src/utils/aiAgent/tasks/index.js" | grep -acF "'E_UNDO_TASK_STARTED'")" != "0" ] || { bad "[${PF_NO}] 账本撤销支 cancel-task 未登记/未拦已开始任务"; S247_BAD=1; }
[ "$(grep -acF "'horosa.ai.tasks.goal.enabled'" "${S247_UI}/src/utils/storageKeyRegistry.js")" != "0" ] && [ "$(grep -acF "'horosa.ai.tasks.goal.enabled'" "${S247_UI}/src/utils/techniqueOnboardingContract.js")" != "0" ] || { bad "[${PF_NO}] horosa.ai.tasks.goal.enabled 未登记"; S247_BAD=1; }
[ -f "${S247_C}/GoalTaskModal.js" ] && [ "$(grep -acF "data-new-goal=\"1\"" "${S247_C}/TaskCenterPanel.js")" = "1" ] || { bad "[${PF_NO}] 任务中心缺新建目标入口"; S247_BAD=1; }
for t in aiAgentGoalRunner aiToolsTasks; do [ -f "${S247_UI}/src/utils/__tests__/${t}.test.js" ] || { bad "[${PF_NO}] 合同测试 ${t}.test.js 缺失"; S247_BAD=1; }; done
[ "$(grep -acF "scheduler_enabled: false," "${S247_RS}")" = "1" ] && [ "$(grep -acF "next.scheduler_enabled = current.scheduler_enabled;" "${S247_RS}")" = "1" ] || { bad "[${PF_NO}] main.rs 定时开关偏好缺省/保留现值锚缺失"; S247_BAD=1; }
[ "$(grep -acF "fn dispatch_scheduler_tick(" "${S247_RS}")" = "1" ] && [ "$(grep -acF "fn scheduler_tick_script(" "${S247_RS}")" = "1" ] && [ "$(grep -acF "fn scheduler_kill_switch(" "${S247_RS}")" = "1" ] || { bad "[${PF_NO}] main.rs 缺定时心跳投递/脚本/kill-switch"; S247_BAD=1; }
[ "$(grep -acF "set_scheduler_enabled_command," "${S247_RS}")" = "1" ] && [ "$(grep -acF "scheduler_status_command," "${S247_RS}")" = "1" ] || { bad "[${PF_NO}] 定时两命令未注册进 generate_handler"; S247_BAD=1; }
[ "$(grep -acF "q.length>1" "${S247_RS}")" != "0" ] && [ "$(grep -acF "fn scheduler_tick_script_calls_handler_or_queues" "$(pf_shell_rs_tests)")" = "1" ] || { bad "[${PF_NO}] 定时 pending 上限 1 / cargo 单测缺失"; S247_BAD=1; }
[ "$(pf_code "${S247_UI}/src/layouts/app.js" | grep -acF "bindSchedulerTicks();")" = "2" ] && [ "$(pf_code "${S247_UI}/src/layouts/app.js" | grep -acF "unbindSchedulerTicks();")" = "1" ] || { bad "[${PF_NO}] app.js 未接定时心跳或缺卸载解绑(绑 1 + 解绑 1;注意 unbindSchedulerTicks(); 含 bindSchedulerTicks(); 子串,故按总数 2 判)"; S247_BAD=1; }
[ "$(pf_code "${S247_UI}/src/utils/aiAgent/prefs.js" | grep -acF "safeLocalStorageGet(AGENT_SCHEDULER_ENABLED_KEY) === '1'")" = "1" ] || { bad "[${PF_NO}] 定时任务子开关判据不是 === 1"; S247_BAD=1; }
[ "$(pf_code "${S247_UI}/src/utils/aiAgent/tasks/scheduler.js" | grep -acF "if(!(o.force || schedulerGatesOpen())){ return out; }")" = "1" ] || { bad "[${PF_NO}] 调度一跳缺门(缺省关必须零执行)"; S247_BAD=1; }
[ "$(grep -acF "enabled: ()=>isSchedulerEnabled()," "${S247_T}/tools/scheduleTask.js")" = "1" ] && [ "$(grep -acF "undoKind: 'cancel-task'," "${S247_T}/tools/scheduleTask.js")" = "1" ] && [ "$(grep -acF "'E_SCHEDULE_INVALID'" "${S247_T}/tools/scheduleTask.js")" != "0" ] || { bad "[${PF_NO}] schedule_task 缺开关门/撤销支/排期错误码"; S247_BAD=1; }
[ "$(grep -acF "'horosa.ai.tasks.scheduler.enabled'" "${S247_UI}/src/utils/storageKeyRegistry.js")" != "0" ] && [ "$(grep -acF "'horosa.ai.tasks.scheduler.enabled'" "${S247_UI}/src/utils/techniqueOnboardingContract.js")" != "0" ] && [ "$(grep -acF "'horosa.ai.tasks.scheduler.lastTickAt'" "${S247_UI}/src/utils/storageKeyRegistry.js")" != "0" ] || { bad "[${PF_NO}] 定时任务两键未登记"; S247_BAD=1; }
[ -f "${S247_C}/ScheduledTaskModal.js" ] && [ "$(grep -acF "data-new-schedule=\"1\"" "${S247_C}/TaskCenterPanel.js")" = "1" ] && [ "$(grep -acF "data-scheduler-switch=\"1\"" "${S247_C}/AgentAbilityPanel.js")" = "1" ] || { bad "[${PF_NO}] 任务中心缺新建定时入口/面板缺定时开关"; S247_BAD=1; }
for t in agentScheduler aiToolsSchedule; do [ -f "${S247_UI}/src/utils/__tests__/${t}.test.js" ] || { bad "[${PF_NO}] 合同测试 ${t}.test.js 缺失"; S247_BAD=1; }; done

# [247b] 自动化规则 hooks(P4):默认关;事件层零 import;调用点五处恰一;深度守卫与上限在引擎;动作只做可撤销/无副作用的事
S247_AU="${S247_UI}/src/utils/aiAgent/automation"
[ -s "${S247_AU}/events.js" ] && [ "$(grep -acE '^import ' "${S247_AU}/events.js")" = "0" ] || { bad "[${PF_NO}] 自动化事件层必须零 import(调用点散在数据层,绝不能反向拖进引擎/存储)"; S247_BAD=1; }
[ "$(pf_code "${S247_AU}/engine.js" | grep -acF "if(!isAutomationEnabled()){ return { ...out, off: true }; }")" = "1" ] && [ "$(pf_code "${S247_AU}/engine.js" | grep -acF "if(origin === 'automation'){ return { ...out, depthGuard: true }; }")" = "1" ] || { bad "[${PF_NO}] 自动化引擎缺总开关门或深度守卫"; S247_BAD=1; }
[ "$(pf_code "${S247_AU}/engine.js" | grep -acF 'export const MAX_RULES_PER_EVENT = 3;')" = "1" ] && [ "$(pf_code "${S247_AU}/engine.js" | grep -acF 'isCoolingDown(rule, now)')" -ge "1" ] || { bad "[${PF_NO}] 自动化引擎缺每事件上限或冷却"; S247_BAD=1; }
[ "$(pf_code "${S247_UI}/src/utils/localcharts.js" | grep -acF "emitAutomationEvent('record.saved'")" = "1" ] && [ "$(pf_code "${S247_UI}/src/utils/localcases.js" | grep -acF "emitAutomationEvent('record.saved'")" = "1" ] || { bad "[${PF_NO}] 数据层两处 record.saved 调用点缺失或重复"; S247_BAD=1; }
[ "$(pf_code "${S247_UI}/src/utils/aiTools/registry.js" | grep -acF "emitAutomationEvent('tool.after'")" = "1" ] && [ "$(pf_code "${S247_UI}/src/utils/aiAgent/tasks/taskStore.js" | grep -acF "emitAutomationEvent('task.done'")" = "1" ] && [ "$(pf_code "${S247_UI}/src/layouts/app.js" | grep -acF "emitAutomationEvent('app.start'")" = "1" ] || { bad "[${PF_NO}] 工具面/任务层/启动 三处调用点缺失或重复"; S247_BAD=1; }
[ "$(pf_code "${S247_UI}/src/utils/aiAgent/prefs.js" | grep -acF "return safeLocalStorageGet(AGENT_AUTOMATION_KEY) === '1';")" = "1" ] && [ "$(grep -acF "key: 'horosa.ai.automation.enabled'" "${S247_UI}/src/utils/storageKeyRegistry.js")" = "1" ] || { bad "[${PF_NO}] 自动化开关判据非 === '1' 或键未登记"; S247_BAD=1; }
# 🔴 动作面永不引工具注册表:自动化只做「用户自己点也能做」的事,不得绕过审批去跑写入工具
[ "$(cat "${S247_AU}/actions.js" | sed -E 's#//.*$##' | grep -acE "aiTools/registry|runTool\(|registerTool\(")" = "0" ] || { bad "[${PF_NO}] 自动化动作面引了工具注册表(动作只能走注入的页面能力)"; S247_BAD=1; }
[ -f "${S247_UI}/src/utils/__tests__/automationEngine.test.js" ] || { bad "[${PF_NO}] 合同测试 automationEngine.test.js 缺失"; S247_BAD=1; }
[ -f "${S247_UI}/src/components/aianalysis/AutomationRulesPanel.js" ] || { bad "[${PF_NO}] 缺自动规则面板"; S247_BAD=1; }
[ "${S247_BAD}" = "0" ] && ok "[${PF_NO}] AI 助手行动能力 v2·P0(审批三档/反问/账本面板/外部客户端档)"
}

seg_249() {
# [${PF_NO}] AI 助手·出站①外部 MCP 客户端:默认关;只读准入;slug 双实现同算法;令牌只落壳侧 0600;注销只限 external;CSP 不放宽(负锚);kill switch
echo "[${PF_NO}] 外部 MCP 客户端(默认关/只读准入/令牌不出壳/CSP 不放宽)"
S249_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S249_RS="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/mcp_client.rs"
S249_MAIN_RS="$(pf_shell_rs_prod)"
S249_CONF="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/tauri.conf.json"
S249_JS="${S249_UI}/src/integrations/mcpClient.js"
S249_BAD=0
[ -s "${S249_RS}" ] && [ "$(pf_code "${S249_RS}" | grep -acF 'pub fn slug_tool_name(')" = "1" ] && [ "$(pf_code "${S249_RS}" | grep -acF 'pub fn redact_spec(')" = "1" ] && [ "$(pf_code "${S249_RS}" | grep -acF 'write_private_file(&path, &body)')" = "1" ] || { bad "[${PF_NO}] mcp_client 缺 slug/脱敏/0600 私有写"; S249_BAD=1; }
[ "$(pf_code "$(pf_rs_prod "${S249_RS}")" | grep -acF 'MCP_CLIENT_KILL_ENV')" -ge 3 ] && [ "$(pf_code "${S249_RS}" | grep -acF 'pub fn client_allowed()')" = "1" ] || { bad "[${PF_NO}] mcp_client 缺 HOROSA_MCP_CLIENT 一票否决"; S249_BAD=1; }
[ "$(pf_code "${S249_RS}" | grep -acF '.stderr(Stdio::null())')" = "1" ] || { bad "[${PF_NO}] stdio 传输须丢弃子进程 stderr(外部输出不得混进协议流)"; S249_BAD=1; }
[ "$(pf_code "${S249_MAIN_RS}" | grep -acF 'mcp_client::stop_on_exit(&state)')" = "1" ] && [ "$(pf_code "${S249_MAIN_RS}" | grep -acF 'mcp_client_call_command,')" = "1" ] || { bad "[${PF_NO}] main.rs 未登记客户端命令或退出未断连"; S249_BAD=1; }
[ -s "${S249_JS}" ] && [ "$(pf_code "${S249_JS}" | grep -acF "export const EXT_PREFIX = 'ext_';")" = "1" ] && [ "$(pf_code "${S249_JS}" | grep -acF 'export function admitExternalTool(')" = "1" ] || { bad "[${PF_NO}] 前端接入层缺 ext_ 前缀单源或准入判定"; S249_BAD=1; }
# 只读档只准入 readOnlyHint 工具(level read);按清单档里清单放行的写工具按 additive 注册(走写入级审批)。
# 判据随之改为:① 注册点的 level 走 verdict.level(不再硬编码 'read');② admitExternalTool 只会给 read/additive 两档,
# 绝不出现 destructive;③ 只读档下清单不放行写工具(页面与壳侧同规则)。
[ "$(pf_code "${S249_JS}" | grep -acF "level: verdict.level || 'read',")" = "1" ] && [ "$(pf_code "${S249_JS}" | grep -acE "level: '(destructive)'")" = "0" ] || { bad "[${PF_NO}] 外部工具注册级别须取 admitExternalTool 的 verdict.level(read/additive),且绝不注册 destructive"; S249_BAD=1; }
[ "$(pf_code "${S249_JS}" | grep -acF "level: readOnly ? 'read' : 'additive'")" = "1" ] || { bad "[${PF_NO}] admitExternalTool 须按 readOnlyHint 分级(只读=read,清单放行的写工具=additive)"; S249_BAD=1; }
[ "$(pf_code "${S249_JS}" | grep -acF "if(readOnlyOnly && !readOnly){")" = "1" ] || { bad "[${PF_NO}] 只读档必须直接拒未声明 readOnlyHint 的工具(允许清单不得在只读档放行写工具)"; S249_BAD=1; }
[ "$(pf_code "${S249_RS}" | grep -acF "if spec.read_only_only {")" = "1" ] || { bad "[${PF_NO}] 壳侧 admit_tool 须镜像只读档语义(清单不放行写工具)"; S249_BAD=1; }
[ "$(pf_code "${S249_JS}" | grep -acF 'isExternalToolsEnabled()')" -ge 1 ] && [ "$(pf_code "${S249_UI}/src/utils/aiAgent/prefs.js" | grep -acF "return safeLocalStorageGet(AGENT_EXTERNAL_TOOLS_KEY) === '1';")" = "1" ] || { bad "[${PF_NO}] 外部工具总开关缺失或判据不是 === '1'"; S249_BAD=1; }
[ "$(grep -acF "key: 'horosa.ai.tools.external.enabled'" "${S249_UI}/src/utils/storageKeyRegistry.js")" = "1" ] || { bad "[${PF_NO}] 外部工具开关键未登记注册表"; S249_BAD=1; }
[ "$(pf_code "${S249_UI}/src/utils/aiTools/registry.js" | grep -acF "if(!def || def.origin !== 'external'){ return false; }")" = "1" ] || { bad "[${PF_NO}] unregisterTool 未限定 origin external(内置目录只增不删)"; S249_BAD=1; }
# 🔴 出站不得放宽 CSP:connect-src 行与现值逐字相同(放宽即红)
[ "$(grep -acF "connect-src 'self' ipc: http://ipc.localhost http://127.0.0.1:* http://localhost:* https://*.amap.com https://*.autonavi.com" "${S249_CONF}")" = "1" ] || { bad "[${PF_NO}] tauri.conf.json 的 connect-src 被改动(外部 MCP 走壳侧 reqwest,页面出站权限不得放宽)"; S249_BAD=1; }
[ "$(pf_code "${S249_JS}" | grep -acE 'fetch\(|XMLHttpRequest|WebSocket\(')" = "0" ] || { bad "[${PF_NO}] 前端接入层出现直连(外部请求一律经壳命令)"; S249_BAD=1; }
[ -f "${S249_UI}/src/utils/__tests__/aiToolsExternal.test.js" ] || { bad "[${PF_NO}] 合同测试 aiToolsExternal.test.js 缺失"; S249_BAD=1; }
[ -f "${S249_UI}/src/components/aianalysis/ExternalServersPanel.js" ] || { bad "[${PF_NO}] 缺外部服务器面板"; S249_BAD=1; }
[ "$(pf_code "${S249_UI}/src/components/aianalysis/ExternalServersPanel.js" | grep -acF 'Input.Password')" = "1" ] || { bad "[${PF_NO}] 令牌输入须用密码框(界面不回显)"; S249_BAD=1; }

# [249b] 出站②联网检索(P7):默认关;Java 端点在位且错误文案不回显 Key;工具 read 级 + 子开关;两码入表
S249_WS_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIWebSearchService.java"
S249_WS_CTRL="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/AIAnalysisController.java"
S249_WS_TOOL="${S249_UI}/src/utils/aiTools/tools/webSearch.js"
[ -s "${S249_WS_JAVA}" ] && [ "$(grep -acF '"/websearch"' "${S249_WS_CTRL}")" = "1" ] || { bad "[${PF_NO}] 联网检索 Java 服务或端点缺失"; S249_BAD=1; }
[ "$(grep -acE 'Logger|log\.(info|debug|warn|error)' "${S249_WS_JAVA}")" = "0" ] || { bad "[${PF_NO}] 联网检索服务出现日志调用(Key 与检索词绝不落日志)"; S249_BAD=1; }
[ "$(grep -acF 'throw new ErrorCodeException(ERR_UPSTREAM, "检索服务返回 HTTP " + status)' "${S249_WS_JAVA}")" = "1" ] || { bad "[${PF_NO}] 上游错误须只回状态码(不回上游原文,可能含 Key 回显)"; S249_BAD=1; }
[ -s "${S249_WS_TOOL}" ] && [ "$(pf_code "${S249_WS_TOOL}" | grep -acF "level: 'read',")" = "1" ] && [ "$(pf_code "${S249_WS_TOOL}" | grep -acF 'isWebSearchEnabled()')" = "1" ] || { bad "[${PF_NO}] web_search 须 read 级且受子开关门控"; S249_BAD=1; }
[ "$(pf_code "${S249_UI}/src/utils/aiAgent/prefs.js" | grep -acF "return safeLocalStorageGet(AGENT_WEB_SEARCH_KEY) === '1';")" = "1" ] && [ "$(grep -acF "key: 'horosa.ai.tools.webSearch.enabled'" "${S249_UI}/src/utils/storageKeyRegistry.js")" = "1" ] || { bad "[${PF_NO}] 联网检索开关判据非 === '1' 或键未登记"; S249_BAD=1; }
[ "$(pf_code "${S249_UI}/src/integrations/webSearch.js" | grep -acE 'fetch\(|XMLHttpRequest')" = "0" ] || { bad "[${PF_NO}] 联网检索前端不得直连(一律经 Java 端点)"; S249_BAD=1; }
[ -f "${S249_UI}/src/utils/__tests__/aiToolsWebSearch.test.js" ] || { bad "[${PF_NO}] 合同测试 aiToolsWebSearch.test.js 缺失"; S249_BAD=1; }
[ -f "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/test/java/spacex/astrostudy/service/AIWebSearchServiceTest.java" ] || { bad "[${PF_NO}] Java 合同测试 AIWebSearchServiceTest 缺失"; S249_BAD=1; }
[ "${S249_BAD}" = "0" ] && ok "[${PF_NO}] 出站:外部 MCP 客户端 + 联网检索(默认关/只读准入/令牌不出壳/CSP 不放宽)"
}

seg_248() {
# [${PF_NO}] AI 助手·本机 MCP 服务 v2:能力位三面 listChanged;资源/提示方法转发页面;GET SSE 在三道门之后;通知广播;会话可选;ext_ 不再导出;冒烟覆盖
echo "[${PF_NO}] 本机 MCP 服务 v2(资源/提示/SSE/通知/会话)"
S248_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S248_RS="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs"
S248_MAIN_RS="$(pf_shell_rs_prod)"
S248_SMOKE="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_mcp_smoke.sh"
S248_BAD=0
[ -s "${S248_RS}" ] && [ "$(pf_code "${S248_RS}" | grep -acF '"tools": { "listChanged": true }')" = "1" ] && [ "$(pf_code "${S248_RS}" | grep -acF '"resources": { "subscribe": false, "listChanged": true }')" = "1" ] && [ "$(pf_code "${S248_RS}" | grep -acF '"prompts": { "listChanged": true }')" = "1" ] || { bad "[${PF_NO}] initialize 未宣告 tools/resources/prompts 的 listChanged"; S248_BAD=1; }
# 五个资源/提示方法必须走同一个传输透传函数(测试区的假页面实现也含同名字面,故锚带 self.page_passthrough)
# 锚改为去空白比对:rustfmt 会把短臂折成 `"m" => {\n self.page_passthrough("m", …)`、长臂折成 `"m" => self.page_passthrough(\n "m", …)`,
#   逐行字面锚在两种折法下各漏一种(cargo fmt 归一后实红);两种形态模式先赋值再引用(bash 3.2 花括号陷阱)。
for m in "resources/list" "resources/templates/list" "resources/read" "prompts/list" "prompts/get"; do S248_P1="\"${m}\"=>self.page_passthrough(\"${m}\","; S248_P2="\"${m}\"=>{self.page_passthrough(\"${m}\","; S248_N=$(( $(pf_code "${S248_RS}" | tr -d " \n\t" | grep -oF "${S248_P1}" | wc -l | tr -d " ") + $(pf_code "${S248_RS}" | tr -d " \n\t" | grep -oF "${S248_P2}" | wc -l | tr -d " ") )); [ "${S248_N}" = "1" ] || { bad "[${PF_NO}] mcp_server 缺方法 ${m}(须经 page_passthrough 转发页面)"; S248_BAD=1; }; done
[ "$(pf_code "${S248_RS}" | grep -acF '"logging/setLevel" =>')" = "1" ] || { bad "[${PF_NO}] mcp_server 缺 logging/setLevel"; S248_BAD=1; }
[ "$(pf_code "${S248_RS}" | grep -acF 'pub fn notify(')" = "1" ] && [ "$(pf_code "$(pf_rs_prod "${S248_RS}")" | grep -acF 'MAX_SSE_CLIENTS')" -ge 2 ] && [ "$(pf_code "${S248_RS}" | grep -acF 'pub fn sse_subscribe(')" = "1" ] || { bad "[${PF_NO}] SSE 通道/广播缺失(notify / sse_subscribe / 上限)"; S248_BAD=1; }
[ "$(pf_code "${S248_RS}" | grep -acF 'request.upgrade("sse", resp)')" = "1" ] || { bad "[${PF_NO}] SSE 须走 upgrade 裸 socket(tiny_http chunked 编码器有 8KB 缓冲,流式帧发不出去)"; S248_BAD=1; }
# 🔴 GET 分支必须在 core.gate( 之后:门(Host→Origin→Bearer→协议版本)永远先于语义
S248_GATE_LINE="$(grep -n 'if method == Method::Get || method == Method::Delete' "${S248_RS}" | head -1 | cut -d: -f1)"
S248_GATE_CALL="$(awk -v s="${S248_GATE_LINE}" 'NR>s && /core.gate\(/{print NR; exit}' "${S248_RS}")"
S248_ACCEPT="$(awk -v s="${S248_GATE_LINE}" 'NR>s && /text\/event-stream/{print NR; exit}' "${S248_RS}")"
[ -n "${S248_GATE_LINE}" ] && [ -n "${S248_GATE_CALL}" ] && [ -n "${S248_ACCEPT}" ] && [ "${S248_GATE_CALL}" -lt "${S248_ACCEPT}" ] || { bad "[${PF_NO}] GET/DELETE 分支未先过 core.gate( 再判 Accept(门必须在语义之前)"; S248_BAD=1; }
[ "$(pf_code "${S248_RS}" | grep -acF 'starts_with("ext_")')" = "1" ] || { bad "[${PF_NO}] tool_name_ok 未拒 ext_ 前缀(外部工具不得再导出)"; S248_BAD=1; }
[ "$(pf_code "${S248_RS}" | grep -acF 'pub fn session_allowed(')" = "1" ] && [ "$(pf_code "$(pf_rs_prod "${S248_RS}")" | grep -acF 'MAX_SESSIONS')" -ge 2 ] || { bad "[${PF_NO}] 可选会话(session_allowed/容量)缺失"; S248_BAD=1; }
[ "$(pf_code "${S248_MAIN_RS}" | grep -acF 'agent_notify_command,')" = "1" ] && [ "$(pf_code "${S248_MAIN_RS}" | grep -acF 'notifications/tools/list_changed')" -ge 1 ] || { bad "[${PF_NO}] main.rs 未登记 agent_notify_command 或桥就绪不推 list_changed"; S248_BAD=1; }
for f in resources.js prompts.js; do [ -s "${S248_UI}/src/utils/aiTools/${f}" ] || { bad "[${PF_NO}] 缺 aiTools/${f}"; S248_BAD=1; }; done
# 资源/提示面只出内容:零注册表、零运行时、零工具执行
[ "$(cat "${S248_UI}/src/utils/aiTools/resources.js" "${S248_UI}/src/utils/aiTools/prompts.js" | sed -E 's#//.*$##' | grep -acE "from '\./registry'|from '\.\./aiAgent/|registerTool\(|runTool\(")" = "0" ] || { bad "[${PF_NO}] 资源/提示面引了注册表或运行时(只许出内容)"; S248_BAD=1; }
[ "$(pf_code "${S248_UI}/src/utils/aiAgent/mcpBridge.js" | grep -acE "method === 'resources/(list|read)'|method === 'prompts/(list|get)'")" = "4" ] || { bad "[${PF_NO}] mcpBridge 缺资源/提示四分支"; S248_BAD=1; }
[ "$(pf_code "${S248_UI}/src/utils/aiAgent/mcpBridge.js" | grep -acE "from '\.\./(localcharts|localcases|aiAnalysisStore)'")" = "0" ] || { bad "[${PF_NO}] 桥引了数据层(资源内容必须经惰性 loadTools 拿)"; S248_BAD=1; }
[ -s "${S248_SMOKE}" ] && [ "$(grep -acF 'text/event-stream' "${S248_SMOKE}")" -ge 1 ] && [ "$(grep -acF 'Mcp-Session-Id' "${S248_SMOKE}")" -ge 1 ] && [ "$(grep -acF 'resources/read' "${S248_SMOKE}")" -ge 1 ] || { bad "[${PF_NO}] 冒烟脚本未覆盖 SSE/会话/资源读"; S248_BAD=1; }
[ -f "${S248_UI}/src/utils/__tests__/mcpResources.test.js" ] || { bad "[${PF_NO}] 合同测试 mcpResources.test.js 缺失"; S248_BAD=1; }
[ "$(grep -acF -- '--log' "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_mcp_smoke.sh")" -ge "1" ] || { bad "[${PF_NO}] 冒烟脚本缺 --log 留档开关"; S248_BAD=1; }
[ "${S248_BAD}" = "0" ] && ok "[${PF_NO}] 本机 MCP 服务 v2(资源/提示/SSE/通知/会话)"
}

seg_257() {
# [${PF_NO}] 进阶页重排(版式件/四枚版式锚/LESS 纪律/子面板去内联/回归锁)+ 操控软件工具集锚在本段末追加
echo "[${PF_NO}] 进阶页重排 + 操控软件工具集收口锁"
S257_BAD=0
S257_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S257_T="${S257_UI}/utils/__tests__"
S257_C="${S257_UI}/components/aianalysis"
# ① 版式件在位 + 四枚版式锚各恰一 + 导轨不是链接(hash 路由)+ 宽度档走 ResizeObserver + 分区锚表
for f in AdvSectionNav.js useElementWidth.js AdvancedPane.js AdvCard.js; do [ -f "${S257_C}/chat/${f}" ] || { bad "[${PF_NO}] 进阶页版式件 ${f} 缺失"; S257_BAD=1; }; done
pf_once "${S257_C}/chat/AdvancedPane.js" 'data-advanced-grid="1"' "进阶页网格锚不是恰一处"
pf_once "${S257_C}/chat/AdvSectionNav.js" 'data-advanced-nav="1"' "导轨锚不是恰一处"
pf_once "${S257_C}/chat/ChatModelRoutesPanel.js" 'data-route-grid-head="1"' "路由表表头锚不是恰一处"
pf_once "${S257_C}/AgentAbilityPanel.js" 'data-agent-collapse="1"' "行动能力折叠区锚不是恰一处"
[ "$(pf_code -q "${S257_C}/AgentAbilityPanel.js" | grep -acF -- "<Collapse.Panel forceRender key=")" = "5" ] || { bad "[${PF_NO}] 折叠区五子面板须全部 forceRender(锚点常驻)"; S257_BAD=1; }
pf_none "${S257_C}/chat/AdvSectionNav.js" "<a " "导轨不得用 <a>(桌面构建走 hash 路由,href=# 会改写路由)"
pf_need "${S257_C}/chat/AdvancedPane.js" "useElementWidth(rootRef)" "宽度档未走 ResizeObserver 量根节点"
pf_need "${S257_C}/chat/AdvCard.js" "export const ADV_SECTION_IDS" "AdvCard 缺分区锚 id 表"
# ② LESS 纪律:含 / 的 grid 值必须转义(LESS 会算成除法);零半像素字号;零 container-type(Tahoe 浮层事故)
# (剥 // 注释再查:注释里提到规则名不算违规——字面量哨兵×注释双向陷阱)
[ "$(pf_code -q "${S257_C}/chat/advanced.less" | grep -acE 'grid-(column|row|area):[[:space:]]*[^~;]*/')" = "0" ] || { bad "[${PF_NO}] advanced.less 有未转义的 grid 除号值"; S257_BAD=1; }
[ "$(pf_code -q "${S257_C}/chat/advanced.less" | grep -acE 'font-size:[[:space:]]*[0-9]+\.5px')" = "0" ] || { bad "[${PF_NO}] advanced.less 出现半像素字号"; S257_BAD=1; }
[ "$(pf_code -q "${S257_C}/chat/advanced.less" | grep -acE '^[[:space:]]*container-type[[:space:]]*:')" = "0" ] || { bad "[${PF_NO}] advanced.less 不得用 container-type"; S257_BAD=1; }
# CSS 覆盖权重机械网:模块类覆盖 antd 一旦与竞争者【打平】,赢家就随分包落地序摇摆(本仓 CSS
# 分散在十几个运行时追加的分包里,源码序没有定义)。曾一次抓到五处。
S257_SPEC="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/check_css_specificity.js"
if [ -f "${S257_SPEC}" ] && command -v node >/dev/null 2>&1; then
  node "${S257_SPEC}" --self-test >/dev/null 2>&1 || { bad "[${PF_NO}] CSS 权重网判别向量自证失败(网本身坏了,结论不作数)"; S257_BAD=1; }
  S257_SPEC_OUT="$(node "${S257_SPEC}" "${S257_C}/chat/advanced.less" 2>&1)" \
    || { bad "[${PF_NO}] advanced.less 有与 antd 打平的覆盖: $(echo "${S257_SPEC_OUT}" | grep -c '^❌') 处"; S257_BAD=1; }
else
  bad "[${PF_NO}] 缺 check_css_specificity.js 或 node(CSS 权重网跑不了)"; S257_BAD=1
fi
# ③ 五子面板去内联外壳,统一走 advanced.less 类
for f in ExternalAgentPanel ExternalServersPanel WebSearchPanel AutomationRulesPanel ActionLedgerPanel; do
  pf_none "${S257_C}/${f}.js" "1px dashed var(--horosa-border" "${f} 仍有内联虚线外壳(须走 advanced.less 类)"
  pf_need "${S257_C}/${f}.js" "advStyles as styles" "${f} 未接统一外壳类"
done
# ④ 回归锁在位
for f in aiAdvancedLayout chatModelRoutesPanel agentAbilityPanel automationRulesPanel skillPackImport; do
  [ -f "${S257_T}/${f}.test.js" ] || { bad "[${PF_NO}] 回归锁 ${f}.test.js 缺失"; S257_BAD=1; }
done
# ⑥ 操控软件工具集:桥 ui 面登记 API 与三处登记方 / 五件工具在目录且 ui 类只 read 且只对 in-app+mcp / 运行时封顶 / 轨迹与高亮零落库、高亮有总开关门 / 合盘页注销 / 记录标签内核
pf_need "${S257_UI}/utils/aiTools/workspaceBridge.js" "export function registerWorkspaceUi(" "工作区桥缺 registerWorkspaceUi"
pf_need "${S257_UI}/utils/aiTools/workspaceBridge.js" "export function waitForWorkspaceUi(" "工作区桥缺 waitForWorkspaceUi"
pf_once "${S257_C}/chat/useChatAssist.js" "registerWorkspaceUi({" "AI 分析页未登记 ui 面(或登记不止一处)"
pf_once "${S257_UI}/pages/index.js" "registerWorkspaceUi({" "主页未登记导航面(或登记不止一处)"
pf_once "${S257_UI}/components/astro/AstroRelative.js" "this._unregisterAgentUi = registerWorkspaceUi({" "合盘页未登记配对面"
pf_need "${S257_UI}/components/astro/AstroRelative.js" "if(typeof this._unregisterAgentUi === 'function'){ try{ this._unregisterAgentUi(); }catch(e){ /* noop */ } this._unregisterAgentUi = null; }" "合盘页卸载未注销配对面"
pf_need "${S257_UI}/utils/aiTools/tools/_shared.js" "return { ...(getWorkspaceUi() || {}), ...((ctx && ctx.ui) || {}) };" "ctxUi 未改读登记的 ui 面"
pf_need "${S257_UI}/utils/aiAgent/automation/deps.js" "const ui = getWorkspaceUi();" "自动化 selectSource 未改读登记的 ui 面"
pf_need "${S257_UI}/utils/aiAgent/mcpBridge.js" "workspaceUi: ()=>{ const ui = typeof index.getWorkspaceUi === 'function' ? index.getWorkspaceUi() : null;" "MCP 桥批尾选中未改读登记的 ui 面"
pf_need "${S257_UI}/utils/aiTools/ledger.js" "const ui = getWorkspaceUi() || {};" "账本撤销后刷源未改读登记的 ui 面"
pf_none "${S257_UI}/utils/aiTools/ledger.js" "b.refreshSources" "账本仍留 b.refreshSources 死分支"
for f in navigateToTechnique compareRecords starRecord pinRecord addRecordTag; do [ -f "${S257_UI}/utils/aiTools/tools/${f}.js" ] || { bad "[${PF_NO}] 工具 ${f}.js 缺失"; S257_BAD=1; }; done
for f in navigateToTechnique compareRecords; do
  pf_need "${S257_UI}/utils/aiTools/tools/${f}.js" "level: 'read'," "${f} 须 read 级"
  pf_need "${S257_UI}/utils/aiTools/tools/${f}.js" "category: 'ui'," "${f} 须 ui 类别"
  pf_need "${S257_UI}/utils/aiTools/tools/${f}.js" "origins: ['in-app', 'mcp']," "${f} 未限定 in-app/mcp 来源(目标任务/自动化不得导航)"
done
for f in starRecord pinRecord addRecordTag; do
  pf_need "${S257_UI}/utils/aiTools/tools/${f}.js" "undoKind: 'restore-record-flag'," "${f} 撤销类型不对"
  pf_need "${S257_UI}/utils/aiTools/tools/${f}.js" "preview(args){" "${f} 缺写前预览"
done
pf_need "${S257_UI}/utils/aiTools/catalog.js" "'interactive', 'ui'];" "目录类别表缺 ui"
pf_need "${S257_UI}/utils/aiTools/catalog.js" "readOnlyHint: d.level === 'read' && category !== 'ui'," "manifest 对 ui 类仍标 readOnly"
pf_need "${S257_UI}/utils/aiAgent/runtime.js" "MAX_UI_PER_TURN: 2," "运行时缺界面动作每 Turn 上限"
pf_need "${S257_UI}/utils/aiAgent/runtime.js" "const uiCalls = accepted.filter((x)=>x.ui);" "运行时未把 ui 类排在末尾串行"
pf_need "${S257_UI}/utils/aiAgent/protocol.js" "'9) 界面动作(navigate_to_technique / compare_records)" "守则缺第 9 条"
pf_none "${S257_UI}/utils/aiAgent/uiTrail.js" "localStorage" "界面轨迹不得落 localStorage"
pf_need "${S257_UI}/utils/aiAgent/agentSpotlight.js" "if(typeof document === 'undefined' || !isAgentEnabled()){ return false; }" "高亮缺总开关门(缺省必须零 DOM 改动)"
pf_once "${S257_C}/AgentActionBar.js" 'data-agent-ui-trail="1"' "动作条缺界面操作轨迹行"
pf_need "${S257_UI}/utils/localRecordStore.js" "export function parseGroupTags(group){" "记录内核缺标签解析"
pf_need "${S257_UI}/utils/localRecordStore.js" "function setTags(cid, tags){" "记录内核缺 setTags"
pf_need "${S257_UI}/utils/localcharts.js" "export function setLocalChartTags(cid, tags){" "命盘库缺 setLocalChartTags"
pf_need "${S257_UI}/utils/localcases.js" "export function setLocalCaseTags(cid, tags){" "事盘库缺 setLocalCaseTags"
pf_need "${S257_UI}/utils/aiTools/labels.js" "navigate_to_technique: '切换技法页'," "标签单源缺五件"
for f in aiToolsGetCurrentContext aiAgentAutomationDeps mcpBridgeDeferredSelect aiToolsLedgerRefresh aiToolsUiTools aiAgentUiTrail aiAgentSpotlight aiToolsResolvePlace; do
  [ -f "${S257_T}/${f}.test.js" ] || { bad "[${PF_NO}] 回归锁 ${f}.test.js 缺失"; S257_BAD=1; }
done
# 发送前「需要先挂载案例」闸单源:行动能力开启即不拦(AI 自己按名字找记录);两处调用点都走 needsMountBeforeSend
pf_need "${S257_UI}/utils/aiAnalysisStarterPrompts.js" "export function needsMountBeforeSend(" "挂载前置闸单源缺失"
pf_need "${S257_UI}/utils/aiAnalysisStarterPrompts.js" "if(agentEnabled){ return false; }" "挂载前置闸未给行动能力让路"
pf_once "${S257_C}/AIAnalysisMain.js" "needsMountBeforeSend({ text: trimmed" "发送路径未走挂载前置闸单源"
pf_none "${S257_C}/AIAnalysisMain.js" "referencesSpecificCase(trimmed)" "发送路径仍直调 referencesSpecificCase(绕过单源)"
[ -f "${S257_T}/aiAnalysisSendGuard.test.js" ] || { bad "[${PF_NO}] 回归锁 aiAnalysisSendGuard.test.js 缺失"; S257_BAD=1; }
# 上下文策略缺省=窗口(legacy 预设必须显式写 legacy,否则缺省翻转后预设被带成 window)
pf_need "${S257_UI}/utils/aiChatHistory.js" "historyMode: 'window'," "上下文策略缺省不是 window"
pf_need "${S257_UI}/utils/aiChatHistory.js" "legacy: Object.freeze({ ...DEFAULT_CONTEXT_POLICY, historyMode: 'legacy' })" "legacy 预设未显式写 legacy"
[ "${S257_BAD}" = "0" ] && ok "[${PF_NO}] 进阶页重排 + 操控软件工具集收口锁"
}

seg_251() {
# [${PF_NO}] AI 结构化输出:json_schema strict 单一构造点在位且缺省路径零变化(消费方一律显式旗标;任何一处把 json_schema 变成无条件默认 = 请求字节变化 = 红)
echo "[${PF_NO}] AI 结构化输出(json_schema strict 单源/现状路径不变)"
S251_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S251_BAD=0
S251_SO="${S251_UI}/src/utils/aiStructuredOutput.js"
# ① 单一构造点:模块在位、OpenAI 形 json_schema、strict 硬约束(additionalProperties:false + required 全列)、深度上限 5、宽松解析、指纹
[ -s "${S251_SO}" ] && [ "$(pf_code "${S251_SO}" | grep -acF "export const STRUCTURED_FORMAT_TYPE = 'json_schema';")" = "1" ] && [ "$(pf_code "${S251_SO}" | grep -acF "export function applyResponseSchema(")" = "1" ] || { bad "[${PF_NO}] aiStructuredOutput 缺单一构造点"; S251_BAD=1; }
[ "$(pf_code "${S251_SO}" | grep -acF "if(strict){ out.additionalProperties = false; out.required = Object.keys(props); }")" = "1" ] && [ "$(pf_code "${S251_SO}" | grep -acF "export const SCHEMA_MAX_DEPTH = 5;")" = "1" ] || { bad "[${PF_NO}] strict 硬约束/深度上限锚缺失(OpenAI strict 必 additionalProperties:false+required 全列)"; S251_BAD=1; }
[ "$(pf_code "${S251_SO}" | grep -acF "export function parseStructuredJson(")" = "1" ] && [ "$(pf_code "${S251_SO}" | grep -acF "export function schemaFingerprint(")" = "1" ] || { bad "[${PF_NO}] 宽松解析/指纹缺失"; S251_BAD=1; }
[ -f "${S251_UI}/src/utils/__tests__/aiStructuredOutput.test.js" ] || { bad "[${PF_NO}] 合同测试 aiStructuredOutput.test.js 缺失"; S251_BAD=1; }
# ② 现状路径不变:聊天/目标判官仍 json_object(未接 schema),未开旗标的请求体零字节变化
[ "$(pf_code "${S251_UI}/src/utils/aiAgent/goalRunner.js" | grep -acF "opts.response_format = { type: 'json_object' };")" = "1" ] || { bad "[${PF_NO}] 目标判官 json_object 现状锚变了(接 schema 须走显式旗标)"; S251_BAD=1; }
# 聊天侧五类浮层参数(温度 / top_p / 停止序列 / 两惩罚 / JSON 模式)已收敛到单源 applyChatParams —— 锚随之迁到那里。
#   锚的用意不变:聊天路径的 JSON 模式仍只发 json_object(未接 json_schema),且只对 OpenAI 兼容与 Gemini 下发。
[ "$(pf_code "${S251_UI}/src/utils/aiAnalysisProviders.js" | grep -acF "o.response_format = { type: 'json_object' };")" = "1" ] || { bad "[${PF_NO}] 聊天 JSON 模式现状锚变了(applyChatParams 单源)"; S251_BAD=1; }
[ "$(pf_code "${S251_UI}/src/utils/aiAnalysisProviders.js" | grep -acF "if(p.jsonMode && p.withJsonMode !== false && (isOpenAiFamily(family) || family === 'gemini')){")" = "1" ] || { bad "[${PF_NO}] 聊天 JSON 模式家族门控锚变了"; S251_BAD=1; }
[ "$(pf_code "${S251_UI}/src/components/aianalysis/AIAnalysisMain.js" | grep -acF "Object.assign(chatProviderOptions, applyChatParams(chatProviderOptions, {")" = "1" ] || { bad "[${PF_NO}] 聊天发送侧未走 applyChatParams 单源"; S251_BAD=1; }
# ⑤ Java 四家翻译(c19):OpenAI 透传 + 自愈两级降级;Anthropic 非流式强制 schema 工具(tool_use.input 回读);Gemini responseSchema(清洗);Ollama format=schema;
#    负锚:Anthropic/Ollama 分支里「无条件丢 response_format」的裸语句回潮即红(翻译被绕过=结构化输出静默失效)
S251_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java"
[ "$(grep -acF "static Map<String, Object> responseFormatSpec(" "${S251_JAVA}")" = "1" ] && [ "$(grep -acF "static Map<String, Object> anthropicForcedSchemaTool(" "${S251_JAVA}")" = "1" ] && [ "$(grep -acF "static boolean degradeResponseFormat(" "${S251_JAVA}")" = "1" ] || { bad "[${PF_NO}] Java 结构化输出翻译助手缺失"; S251_BAD=1; }
[ "$(grep -acF 'generationConfig.put("responseSchema", geminiResponseSchema(' "${S251_JAVA}")" = "1" ] && [ "$(grep -acF 'applyOllamaResponseFormat(body, prov.remove("response_format"));' "${S251_JAVA}")" = "1" ] && [ "$(grep -acF 'if(degradeResponseFormat(body, msg)) { changed = true; }' "${S251_JAVA}")" = "1" ] || { bad "[${PF_NO}] Gemini/Ollama/自愈三处接线缺失"; S251_BAD=1; }
[ "$(grep -acE '^[[:space:]]*aprov\.remove\("response_format"\);' "${S251_JAVA}")" = "0" ] && [ "$(grep -acE '^[[:space:]]*prov\.remove\("response_format"\);' "${S251_JAVA}")" = "0" ] || { bad "[${PF_NO}] Anthropic/Ollama 无条件丢 response_format 回潮(翻译被绕过)"; S251_BAD=1; }
[ "$(grep -acF 'return JsonUtility.encode(((Map)part).get("input"));' "${S251_JAVA}")" = "1" ] || { bad "[${PF_NO}] Anthropic 强制工具 tool_use.input 回读缺失(非流式结构化输出会拿到空正文)"; S251_BAD=1; }
S251_JT="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/test/java/spacex/astrostudy/service/AIAnalysisProxyServiceTest.java"
for t in buildAnthropicBodyNonStreamJsonSchemaBecomesForcedTool buildGeminiBodyJsonSchemaSetsResponseSchema applyOllamaResponseFormatOnlyTranslatesJsonSchema healUpstreamRequestBodyDegradesResponseFormatTwoLevels extractAnthropicContentReturnsForcedToolInputAsJson; do [ "$(grep -acF "public void ${t}()" "${S251_JT}")" = "1" ] || { bad "[${PF_NO}] Java 合同 ${t} 缺失"; S251_BAD=1; }; done
# ⑥-⑧ 按任务用模型:六槽键单源(全空=现状)+ 运行时每轮 model 进 trace / requestClose 恰一轮收口 / NULL_AGENT 空钩 + 页面插座恰一处 + 键登记 + 设置卡 + 合同
S251_MR="${S251_UI}/src/utils/aiModelRouting.js"
[ -s "${S251_MR}" ] && [ "$(pf_code "${S251_MR}" | grep -acF "export const MODEL_ROUTES_KEY = 'horosa.ai.chat.modelRoutes.v1';")" = "1" ] && [ "$(pf_code "${S251_MR}" | grep -acF "export const ROUTE_SLOTS = ['toolRounds', 'final', 'judge', 'review', 'planner', 'subagent', 'utility'];")" = "1" ] || { bad "[${PF_NO}] aiModelRouting 七槽键单源缺失(第七槽 utility = 辅助短调用)"; S251_BAD=1; }
[ "$(pf_code "${S251_MR}" | grep -acF "export function shouldRequestClose(")" = "1" ] && [ "$(pf_code "${S251_MR}" | grep -acF "export function providerOptionsForRoute(")" = "1" ] || { bad "[${PF_NO}] 路由纯函数缺失"; S251_BAD=1; }
S251_RT="${S251_UI}/src/utils/aiAgent/runtime.js"
[ "$(pf_code "${S251_RT}" | grep -acF "requestClose(){ if(!state.closing){ state.closeRequested = true; } },")" = "1" ] && [ "$(pf_code "${S251_RT}" | grep -acF "requestClose(){},")" = "1" ] && [ "$(pf_code "${S251_RT}" | grep -acF "model: r.model || undefined,")" = "1" ] || { bad "[${PF_NO}] 运行时 requestClose/NULL_AGENT 空钩/trace 每轮 model 锚缺失"; S251_BAD=1; }
[ "$(pf_code "${S251_RT}" | grep -acF "if(!calls.length && state.closeRequested && !state.closing){")" = "1" ] || { bad "[${PF_NO}] 收口一轮分支缺失(终稿模型永远轮不到)"; S251_BAD=1; }
S251_MAIN="$(pf_src_set "${S251_UI}/src/components/aianalysis/AIAnalysisMain.js")"
[ "$(pf_code "${S251_MAIN}" | grep -acF "const chatModels = useChatModels({")" = "1" ] && [ "$(pf_code "${S251_MAIN}" | grep -acF "chatModels.pickRound({")" = "1" ] && [ "$(pf_code "${S251_MAIN}" | grep -acF "chatModels.afterRound({")" = "1" ] && [ "$(pf_code "${S251_MAIN}" | grep -acF "chatModels.pickTool({")" = "1" ] || { bad "[${PF_NO}] AIAnalysisMain 模型路由插座不是恰一处"; S251_BAD=1; }
[ -f "${S251_UI}/src/components/aianalysis/chat/useChatModels.js" ] && [ -f "${S251_UI}/src/components/aianalysis/chat/ChatModelRoutesPanel.js" ] || { bad "[${PF_NO}] useChatModels 钩子/设置卡缺失"; S251_BAD=1; }
[ "$(grep -acF "'horosa.ai.chat.modelRoutes.v1'" "${S251_UI}/src/utils/storageKeyRegistry.js")" != "0" ] && [ "$(grep -acF "'horosa.ai.chat.modelRoutes.v1'" "${S251_UI}/src/utils/techniqueOnboardingContract.js")" != "0" ] || { bad "[${PF_NO}] horosa.ai.chat.modelRoutes.v1 未登记"; S251_BAD=1; }
for t in aiModelRouting aiAgentRuntimeRouting; do [ -f "${S251_UI}/src/utils/__tests__/${t}.test.js" ] || { bad "[${PF_NO}] 合同测试 ${t}.test.js 缺失"; S251_BAD=1; }; done
[ "${S251_BAD}" = "0" ] && ok "[${PF_NO}] AI 结构化输出(json_schema strict 单源/现状路径不变)"
}

seg_262() {
# [${PF_NO}] 行动能力策略双路径同源网(2026-09-08 进阶复查 D12–D19;「只有对话路径消费了键/函数」一族+「读级类别档无消费方」):
#   死导出检查器(写了函数没人调)+ 桌面桥合同三向对拍(壳 Vec ↔ 页面读 .value ↔ 桌面 mock 同形)各自 --self-test 后全检;
#   D12–D18 负锚:读级类别档进判定 / 目录按来源列 / 桥侧 deny·目录外名字·审批超时撤台 / ask 无通道 fail-closed / 被拒计额 / ledgerLost 可见 / list_changed 发射器;五测在位。
echo "[${PF_NO}] 行动能力策略双路径同源网:死导出 / 桥合同 / D12–D18 负锚 / 五测"
S262_BAD=0
S262_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
for S262_JS in check_dead_exports.js check_desktop_bridge_contract.js; do
  S262_P="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/${S262_JS}"
  [ -f "${S262_P}" ] || { bad "[${PF_NO}] 缺 ${S262_JS}"; S262_BAD=1; continue; }
  S262_ARG="${S262_UI}"; [ "${S262_JS}" = "check_desktop_bridge_contract.js" ] && S262_ARG="${REPO_ROOT}"
  S262_ST="$(node "${S262_P}" "${S262_ARG}" --self-test 2>&1)" || { echo "${S262_ST}" | tail -4 | sed 's/^/    /'; bad "[${PF_NO}] ${S262_JS} 判别向量自证失败"; S262_BAD=1; }
  S262_OUT="$(node "${S262_P}" "${S262_ARG}" 2>&1)" || { echo "${S262_OUT}" | tail -12 | sed 's/^/    /'; bad "[${PF_NO}] ${S262_JS} 有违反(新增死导出 / 桥合同不齐)"; S262_BAD=1; }
done
[ "$(grep -acF "PURE_READ_CATEGORIES" "${S262_UI}/src/utils/aiAgent/approvalPolicy.js")" != "0" ] || { bad "[${PF_NO}] 读级类别档未进审批判定(D12)"; S262_BAD=1; }
[ "$(grep -acF "exportToolManifest({ origin })" "${S262_UI}/src/utils/aiAgent/runtime.js")" != "0" ] || { bad "[${PF_NO}] 运行时目录未按来源列(D14)"; S262_BAD=1; }
[ "$(grep -acF "isToolDenied(" "${S262_UI}/src/utils/aiAgent/mcpBridge.js")" -ge 1 ] || { bad "[${PF_NO}] 桥未消费按工具名禁用(D13a)"; S262_BAD=1; }
[ "$(grep -acF "'E_TOOL_NOT_FOUND'" "${S262_UI}/src/utils/aiAgent/mcpBridge.js")" != "0" ] || { bad "[${PF_NO}] 桥未在限流前拒目录外名字(D13b)"; S262_BAD=1; }
[ "$(grep -acF "{ timeoutMs: ms }" "${S262_UI}/src/utils/aiAgent/mcpBridge.js")" != "0" ] || { bad "[${PF_NO}] 桥审批等待未带 timeoutMs 撤台(D13c)"; S262_BAD=1; }
[ "$(grep -acF "no-approval-channel" "${S262_UI}/src/utils/aiAgent/runtime.js")" != "0" ] || { bad "[${PF_NO}] ask 无审批通道未 fail-closed(D15)"; S262_BAD=1; }
[ "$(grep -acF "ledgerLost" "${S262_UI}/src/components/aianalysis/AgentActionBar.js")" != "0" ] || { bad "[${PF_NO}] 账本丢失未在动作条可见(D17)"; S262_BAD=1; }
[ "$(grep -acF "agent_notify_command" "${S262_UI}/src/utils/aiAnalysisDesktop.js")" != "0" ] || { bad "[${PF_NO}] 页面侧无 list_changed 发射器(D18)"; S262_BAD=1; }
[ "$(grep -acF "data-approval-scope=\"session\"" "${S262_UI}/src/components/aianalysis/AgentActionBar.js")" != "0" ] || { bad "[${PF_NO}] 审批行缺「本会话不再问」(P1)"; S262_BAD=1; }
[ "$(grep -acF "<TabPane tab=\"进阶\"" "${S262_UI}/src/components/help/AIAnalysisHelpDoc.js")" != "0" ] || { bad "[${PF_NO}] 操作手册缺「进阶」页签(P2)"; S262_BAD=1; }
for S262_T in aiToolsManifestOrigins.contract aiAgentPolicyParity agentActionBarLedgerLost aiAgentNotify aiAgentSessionAllow; do [ -f "${S262_UI}/src/utils/__tests__/${S262_T}.test.js" ] || { bad "[${PF_NO}] 缺 ${S262_T}.test.js"; S262_BAD=1; }; done
[ "$(grep -acF "checkResolvedAddresses" "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/OutboundUrlGuard.java")" -ge 2 ] || { bad "[${PF_NO}] 出站守卫未按解析结果再判(D21)"; S262_BAD=1; }
[ "${S262_BAD}" = "0" ] && ok "[${PF_NO}] 策略双路径同源网:死导出零新增 / 桥合同齐 / D12–D18 负锚 / P1 P2 在位 / 五测在位 / 出站解析后判"
}

seg_263() {
# ---- [${PF_NO}] preflight 自身 bash 3.2 花括号展开陷阱(2026-09-08「发送前成本确认门」哨兵假红根因:
#      macOS /bin/bash 3.2 的花括号展开扫描器不认识 $( … ),朴素数引号后把 `confirmCost({ candidates, est })`
#      当成未加引号的 {a,b} 展开成两个词 → grep 各数 0 → 哨兵在 zsh/bash4 下绿、在真跑的 bash 3.2 下恒红。
#      修法=模式先赋值再引用(赋值右侧不做花括号展开)。本块用检查器逐词模拟 bash 3.2 规则扫全部 .sh,
#      命中即红;--self-test 十一向量自证(必红/必绿各半)。) ----
echo "[${PF_NO}] bash 3.2 花括号展开陷阱(检查器自证 + 全部 .sh 逐词扫描)"
S263_BAD=0
S263_CHK="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/check_bash32_brace_trap.py"
if [ ! -s "${S263_CHK}" ]; then
  bad "[${PF_NO}] 缺 check_bash32_brace_trap.py(bash 3.2 花括号陷阱检查器丢失)"; S263_BAD=1
else
  S263_ST="$(python3 "${S263_CHK}" --self-test 2>&1)" || { bad "[${PF_NO}] 检查器自证失败(判别向量不全红全绿,结论不可信): $(echo "${S263_ST}" | grep -a 'BAD' | head -3 | tr '\n' ' ')"; S263_BAD=1; }
  S263_OUT="$(python3 "${S263_CHK}" "${REPO_ROOT}"/Horosa_Desktop_Installer/scripts/*.sh "${REPO_ROOT}"/Horosa_Desktop_Installer/scripts/preflight/*.sh "${REPO_ROOT}"/Horosa_Desktop_Installer/scripts/preflight/*/*.sh "${REPO_ROOT}"/Horosa-Web/*.sh 2>&1)" || { bad "[${PF_NO}] 脚本里存在 bash 3.2 花括号展开陷阱(把模式先赋给变量再引用): $(echo "${S263_OUT}" | grep -a '陷阱' | head -3 | tr '\n' ' ')"; S263_BAD=1; }
fi
[ "${S263_BAD}" = "0" ] && ok "[${PF_NO}] bash 3.2 花括号展开陷阱零命中(检查器自证 + 全部 .sh 逐词扫描)"
}

seg_265() {
# ---- [${PF_NO}] AI 分析机械网 ①(2026-09-08;审批台按消息键建表 / 桥单预算按原因出码 / 非对话来源读级放行 / 会话放行只对对话 /
#      任务创建快照模型 / 库批量事件一发 / 账本丢失监听可拆 —— 负锚 + 十测在位;写法纪律:模式含 {…,…} 先赋值再引用,管道禁 grep -q) ----
echo "[${PF_NO}] AI 分析机械网 ①:审批台 / 桥预算 / 来源读级放行 / 任务快照模型 / 密钥面 / 手册真话"
S265_BAD=0
S265_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S265_APV="${S265_UI}/src/utils/aiAgent/approvals.js"; S265_ELI="${S265_UI}/src/utils/aiAgent/elicitations.js"
[ "$(pf_code "${S265_APV}" | grep -acF "function keyOf(messageKey, callId)")" = "1" ] && [ "$(pf_code "${S265_ELI}" | grep -acF "function keyOf(messageKey, callId)")" = "1" ] || { bad "[${PF_NO}] 待审/反问表未按 messageKey::callId 建键(并发轮同 id 互相顶掉)"; S265_BAD=1; }
[ "$(pf_code "${S265_APV}" | grep -acF "export function resolveApprovalsByName(name, allowed, messageKey)")" = "1" ] || { bad "[${PF_NO}] 按名落定未限定 messageKey(会话钮跨作用域批准后台任务)"; S265_BAD=1; }
[ "$(pf_code "${S265_APV}" | grep -acF "export function approvalReasonOf(")" = "1" ] || { bad "[${PF_NO}] 审批落定未回传原因"; S265_BAD=1; }
[ "$(pf_code "${S265_UI}/src/components/aianalysis/AgentActionBar.js" | grep -acF "resolveApprovalsByName(x.name, true, messageId)")" = "2" ] || { bad "[${PF_NO}] 动作条两钮未按本消息键落定"; S265_BAD=1; }
S265_BR="${S265_UI}/src/utils/aiAgent/mcpBridge.js"
S265_P_BUD='const remainMs = ms - spentMs;'
[ "$(pf_code "${S265_BR}" | grep -acF "${S265_P_BUD}")" = "1" ] || { bad "[${PF_NO}] 桥执行预算未减去审批已耗(最坏 2×预算)"; S265_BAD=1; }
[ "$(pf_code "${S265_BR}" | grep -acF "timedOut = !allowed")" = "0" ] || { bad "[${PF_NO}] 桥仍用耗时启发式判超时(回潮)"; S265_BAD=1; }
[ "$(pf_code "${S265_BR}" | grep -acF "approvalReasonOf(")" != "0" ] || { bad "[${PF_NO}] 桥未按落定原因出码"; S265_BAD=1; }
[ "$(pf_code "${S265_BR}" | grep -acF "'rejected'")" != "0" ] && [ "$(pf_code "${S265_BR}" | grep -acF "REJECT_MAX_PER_MINUTE")" != "0" ] || { bad "[${PF_NO}] 桥拒绝未走独立 rejected 桶"; S265_BAD=1; }
[ "$(pf_code "${S265_BR}" | grep -acF "manifestCache")" != "0" ] || { bad "[${PF_NO}] 桥目录未按策略/目录版本缓存"; S265_BAD=1; }
[ "$(pf_code "${S265_BR}" | grep -acF "notifier !== mine")" != "0" ] || { bad "[${PF_NO}] 通知器订阅未校验同一性"; S265_BAD=1; }
[ "$(pf_code "${S265_UI}/src/utils/aiAgent/tasks/index.js" | grep -acF "removeEventListener('horosa:agent-ledger-lost'")" != "0" ] || { bad "[${PF_NO}] 账本丢失监听无拆除"; S265_BAD=1; }
S265_RT="${S265_UI}/src/utils/aiAgent/runtime.js"
[ "$(pf_code "${S265_RT}" | grep -acF "autoAllowReadLevel(origin, level)")" = "1" ] || { bad "[${PF_NO}] 运行时未对非对话来源读级「询问」自动放行"; S265_BAD=1; }
[ "$(pf_code "${S265_RT}" | grep -acF "origin === 'in-app' ? isToolSessionAllowed")" = "1" ] || { bad "[${PF_NO}] 会话放行集未限定对话来源(泄漏进后台任务)"; S265_BAD=1; }
[ "$(grep -acF "禁用名的分支不可达(manifest 已剥、executeCalls 先拒)" "${S265_RT}")" = "1" ] || { bad "[${PF_NO}] 运行时禁用名死分支未清"; S265_BAD=1; }
[ "$(pf_code "${S265_UI}/src/utils/aiAgent/approvalPolicy.js" | grep -acF "export function autoAllowReadLevel(")" = "1" ] || { bad "[${PF_NO}] 策略层缺 autoAllowReadLevel 单源"; S265_BAD=1; }
for S265_F in aiAgent/goalRunner.js aiAgent/tasks/taskKinds.js; do
  [ "$(pf_code "${S265_UI}/src/utils/${S265_F}" | grep -acF "\${call.name} 请求写入")" = "0" ] || { bad "[${PF_NO}] ${S265_F} 审批文案仍硬写「请求写入」"; S265_BAD=1; }
  [ "$(pf_code "${S265_UI}/src/utils/${S265_F}" | grep -acF "approvalVerb(call)")" != "0" ] || { bad "[${PF_NO}] ${S265_F} 审批文案未按级别"; S265_BAD=1; }
done
[ -s "${S265_UI}/src/utils/aiAgent/tasks/modelSnapshot.js" ] || { bad "[${PF_NO}] 缺 tasks/modelSnapshot.js(任务创建快照模型单源)"; S265_BAD=1; }
for S265_F in utils/aiAgent/goalRunner.js utils/aiTools/tools/scheduleTask.js components/aianalysis/ScheduledTaskModal.js; do
  [ "$(pf_code "${S265_UI}/src/${S265_F}" | grep -acF "snapshotModelSelection(")" != "0" ] || { bad "[${PF_NO}] ${S265_F} 创建任务未快照 modelSelection"; S265_BAD=1; }
done
S265_ST="${S265_UI}/src/utils/aiAnalysisStore.js"
for S265_OP in "'bulk'" "'clear'" "'deleteMany'"; do [ "$(pf_code "${S265_ST}" | grep -acF "${S265_OP}")" != "0" ] || { bad "[${PF_NO}] 库 ${S265_OP} 变更事件缺(bulkPut/clear/批删各派一次)"; S265_BAD=1; }; done
for S265_T in aiAgentApprovals aiAnalysisStoreEvents agentTaskModelSnapshot; do [ -f "${S265_UI}/src/utils/__tests__/${S265_T}.test.js" ] || { bad "[${PF_NO}] 缺 ${S265_T}.test.js"; S265_BAD=1; }; done
for S265_TG in "mcpBridge.test.js:执行预算 = 客户端预算 − 审批已耗" "mcpBridge.test.js:到点前点「跳过」⇒ E_USER_SKIPPED" "mcpBridge.test.js:目录外名字洪水" "mcpBridge.test.js:通知器同 tick 关-开" "aiAgentApprovalPolicy.test.js:读级「询问」在非对话来源自动放行" "aiAgentRuntime.test.js:「本会话不再问」只对对话来源" "aiAgentGoalRunner.test.js:后台任务审批文案按级别" "taskCenterPanel.test.js:账本丢失监听可拆除"; do
  S265_TF="${S265_TG%%:*}"; S265_TT="${S265_TG#*:}"
  [ "$(grep -acF "${S265_TT}" "${S265_UI}/src/utils/__tests__/${S265_TF}")" != "0" ] || { bad "[${PF_NO}] ${S265_TF} 缺 ${S265_TT} 用例"; S265_BAD=1; }
done
S265_JG="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/OutboundUrlGuard.java"
S265_JF="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIWebFetchService.java"
[ "$(grep -acF "isDottedQuad(h)" "${S265_JG}")" -ge 3 ] || { bad "[${PF_NO}] 私网前缀判定未限定点分十进制字面量(10.gov 被当内网)"; S265_BAD=1; }
[ "$(grep -acF "allowLoopback && isLoopbackLiteral(h0)" "${S265_JG}")" = "1" ] || { bad "[${PF_NO}] ALLOW_LOOPBACK 未收窄为只放回环字面量(名字主机跳过解析判定)"; S265_BAD=1; }
[ "$(grep -acF "64:ff9b:" "${S265_JG}")" != "0" ] || { bad "[${PF_NO}] 出站守卫缺 NAT64/文档段判定"; S265_BAD=1; }
[ "$(grep -acF "String url = UpstreamUrlText.clean(rawUrl);" "${S265_JG}")" = "1" ] && [ "$(grep -acF "return url;" "${S265_JG}")" = "1" ] || { bad "[${PF_NO}] 守卫未按接口地址同一口径清理后再判、回清理后的地址(首尾空格 / 全角空格 / 零宽字符穿到 URI.create)"; S265_BAD=1; }
[ "$(grep -acF "target = URI.create(current);" "${S265_JF}")" = "1" ] || { bad "[${PF_NO}] 逐跳 URI.create 仍在 try 之外"; S265_BAD=1; }
[ "$(grep -acF "strictGuardDottedQuadOnlyTrimAndReservedRanges" "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/test/java/spacex/astrostudy/service/AIWebFetchServiceTest.java")" = "1" ] || { bad "[${PF_NO}] 缺出站守卫点分十进制/trim/保留段 JUnit"; S265_BAD=1; }
# ⑥ 密钥面:诊断包脱敏 / 令牌轮换失效测 / 备份按单源密钥店剥密穷举 / 桌面 mock 主密钥档
S265_MR="$(pf_shell_rs_prod)"
[ "$(grep -acF "redact_lines(" "${S265_MR}")" -ge 4 ] || { bad "[${PF_NO}] 诊断包三段未经 redact_lines 脱敏"; S265_BAD=1; }
[ "$(grep -acF "fn diagnostics_redacts_secrets" "$(pf_shell_rs_tests)")" = "1" ] || { bad "[${PF_NO}] 缺诊断脱敏 Rust 测"; S265_BAD=1; }
[ "$(grep -acF "fn rotate_token_invalidates_old_bearer" "${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs")" = "1" ] || { bad "[${PF_NO}] 缺轮换令牌旧令牌失效测"; S265_BAD=1; }
[ -s "${S265_UI}/src/utils/aiSecretStores.js" ] && [ "$(pf_code "${S265_UI}/src/utils/unifiedBackup.js" | grep -acF "isSecretStore(name)")" = "1" ] || { bad "[${PF_NO}] 备份剥密未走 aiSecretStores 单源"; S265_BAD=1; }
[ -f "${S265_UI}/src/utils/__tests__/aiSecretStores.test.js" ] || { bad "[${PF_NO}] 缺 [G7] 备份剥密穷举向量"; S265_BAD=1; }
# ⑦ 手册真话:看门狗/技能上限/网页读取/规则链深 数字全部常量插值;能力卡文案由目录生成;撤销豁免显式登记;JSX 文本零 markdown 加粗;手册旧口径归零;五合同在位
S265_HELP="${S265_UI}/src/components/help/AIAnalysisHelpDoc.js"
[ "$(grep -acE '自动转正|完全一样|90 秒内|最多 5 分钟|超长或触发词冲突会被拒绝' "${S265_HELP}")" = "0" ] || { bad "[${PF_NO}]⑦ 应用内手册旧假话回潮(沉淀转正/完全一样/90 秒/5 分钟/超长拒绝)"; S265_BAD=1; }
[ "$(grep -acF 'DEFAULT_STREAM_STALL_MS / 1000' "${S265_HELP}")" = "1" ] && [ "$(grep -acF 'DEFAULT_STREAM_MAX_MS / 60000' "${S265_HELP}")" = "1" ] && [ "$(grep -acF '${SKILL_MAX_TEMPLATE} 字按上限截断' "${S265_HELP}")" = "1" ] || { bad "[${PF_NO}]⑦ 手册数字未走常量插值(看门狗/技能上限)"; S265_BAD=1; }
[ "$(sed -E 's#//.*$##' "${S265_UI}/src/services/aianalysis.js" | grep -acF 'DEFAULT_STREAM_STALL_MS)')" = "1" ] && [ "$(sed -E 's#//.*$##' "${S265_UI}/src/services/aianalysis.js" | grep -acF 'DEFAULT_STREAM_MAX_MS)')" = "1" ] || { bad "[${PF_NO}]⑦ 服务层看门狗缺省未走 aiStreamLimits 单源"; S265_BAD=1; }
[ "$(grep -acF 'export const UNDO_EXEMPT' "${S265_UI}/src/utils/aiTools/catalog.js")" = "1" ] && [ "$(grep -acF 'agentAbilityCopyText()' "${S265_UI}/src/components/aianalysis/AgentAbilityPanel.js")" != "0" ] && [ "$(grep -acF 'AGENT_ABILITY_COPY' "${S265_UI}/src/components/aianalysis/AgentAbilityPanel.js")" = "0" ] || { bad "[${PF_NO}]⑦ 能力卡文案未由目录生成 / 撤销豁免表缺"; S265_BAD=1; }
[ "$(grep -acF '${MAX_CHAIN_DEPTH}' "${S265_UI}/src/components/aianalysis/AutomationRulesPanel.js")" = "1" ] && [ "$(grep -acF '${WEB_FETCH_MAX_CHARS} 字' "${S265_UI}/src/components/aianalysis/WebSearchPanel.js")" = "1" ] || { bad "[${PF_NO}]⑦ 规则链深 / 网页读取上限 文案未与常量同源"; S265_BAD=1; }
[ "$(grep -acE '\*\*只读\*\*|\*\*你的检索词\*\*' "${S265_UI}/src/components/aianalysis/ExternalServersPanel.js" "${S265_UI}/src/components/aianalysis/WebSearchPanel.js" | awk -F: '{s+=$2} END{print s+0}')" = "0" ] || { bad "[${PF_NO}]⑦ 面板 JSX 文本 markdown 加粗回潮"; S265_BAD=1; }
S265_NTOOLS=51
[ "$(grep -acE '六类 records|\*\*三个动作\*\*' "${REPO_ROOT}/docs/AI_AGENT_RUNTIME.md")" = "0" ] && [ "$(grep -acF "共 **${S265_NTOOLS} 件**" "${REPO_ROOT}/docs/AI_AGENT_RUNTIME.md")" = "1" ] || { bad "[${PF_NO}]⑦ 手册旧口径回潮或总数句缺"; S265_BAD=1; }
for S265_T in aiAgentRuntimeDoc.contract aiAdvancedHelpCards.contract aiPanelCopyNoMarkdown aiToolsUndoContract agentAbilityCopy.contract; do
  [ -f "${S265_UI}/src/utils/__tests__/${S265_T}.test.js" ] || { bad "[${PF_NO}]⑦ 缺 ${S265_T}.test.js"; S265_BAD=1; }
done
# ⑧ 官方 schema 网实抓两处 Java 根修:代理自用键 maxRetries 不进上游请求体 · Gemini Schema.type 按官方枚举名(大写)下发 + JUnit 两锁
S265_PROXY="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java"
S265_TCS="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIToolCallSupport.java"
[ "$(grep -acF '|| "maxRetries".equals(key)' "${S265_PROXY}")" = "1" ] || { bad "[${PF_NO}]⑧ 代理未剥 maxRetries(自用键进上游请求体)"; S265_BAD=1; }
[ "$(grep -acF 'static String geminiTypeName(String t)' "${S265_TCS}")" = "1" ] && [ "$(grep -acF 'geminiTypeName(' "${S265_TCS}")" -ge 3 ] || { bad "[${PF_NO}]⑧ Gemini Schema.type 未按官方枚举名归一"; S265_BAD=1; }
[ "$(grep -acF 'assertFalse(bodyOptions.containsKey("maxRetries"));' "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/test/java/spacex/astrostudy/service/AIAnalysisProxyServiceTest.java")" = "1" ] && [ "$(grep -acF 'geminiSchemaTypesAreUppercasedRecursively' "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/test/java/spacex/astrostudy/service/AIToolCallSupportTest.java")" != "0" ] || { bad "[${PF_NO}]⑧ 缺 JUnit 锁"; S265_BAD=1; }
[ "${S265_BAD}" = "0" ] && ok "[${PF_NO}] 机械网 ①:审批台按消息键 / 桥单预算按原因 / 来源读级放行 / 会话放行限对话 / 任务快照模型 / 库批量事件 / 十测在位"
}

seg_266() {
# ---- [${PF_NO}] 死开关/死导出清零锁(2026-09-08:导出「图例」全家桶死开关填首批并缺省关;LEGACY 11 条 9 删 2 接线,棘轮归零;
#      死导出扫描面扩到 report*/aiExport*/aiAnalysis*/services;「清空全部口径」钮接线两件 API) ----
echo "[${PF_NO}] 死开关 / 死导出清零锁"
S266_BAD=0
S266_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S266_LG="${S266_UI}/src/utils/aiExportLegend.js"
S266_AWK_LG='/^const LEGEND_BY_TECHNIQUE/,/^};/'
[ "$(awk "${S266_AWK_LG}" "${S266_LG}" | grep -acE "^\s+[a-z_]+: \[")" -ge 3 ] || { bad "[${PF_NO}] 图例注册表不足 3 个技法(死开关全家桶)"; S266_BAD=1; }
[ "$(awk "${S266_AWK_LG}" "${S266_LG}" | grep -acE "^\s+'.+',?$")" -ge 15 ] || { bad "[${PF_NO}] 图例条目总数 <15"; S266_BAD=1; }
[ "$(pf_code "${S266_UI}/src/utils/aiExport.js" | grep -acF "legend: src.legend === true")" = "1" ] || { bad "[${PF_NO}] 图例偏好缺省未翻为关(填表即改缺省导出字节)"; S266_BAD=1; }
[ "$(pf_code "${S266_UI}/src/utils/aiExport.js" | grep -acF "prefs.legend === true")" != "0" ] || { bad "[${PF_NO}] isAIExportLegendEnabled 未按显式 true 判"; S266_BAD=1; }
[ "$(grep -acF 'data-ai-export-legend="1"' "${S266_UI}/src/components/homepage/PageHeader.js")" = "1" ] || { bad "[${PF_NO}] 设置面缺图例勾选"; S266_BAD=1; }
[ -f "${S266_UI}/src/utils/__tests__/aiExportLegend.test.js" ] || { bad "[${PF_NO}] 缺 aiExportLegend.test.js(缺省关 + 首批判据)"; S266_BAD=1; }
S266_DE="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/check_dead_exports.js"
[ "$(grep -acF "SCAN_FILE_RES" "${S266_DE}")" -ge 2 ] || { bad "[${PF_NO}] 死导出扫描面未扩到 report*/aiExport*/aiAnalysis*/services"; S266_BAD=1; }
S266_LEG="$(awk '/^const LEGACY = new Set\(\[/,/^\]\);/' "${S266_DE}" | grep -acE "^\s+'")"
[ "${S266_LEG}" = "0" ] || { bad "[${PF_NO}] 死导出 LEGACY 棘轮表未归零(仍有 ${S266_LEG} 条逃生口)"; S266_BAD=1; }
[ "$(grep -acF "data-persona-clear-all" "${S266_UI}/src/components/aianalysis/chat/PersonaMemoryPanel.js")" != "0" ] && [ "$(grep -acF '"persona.clearAll"' "${S266_UI}/src/components/aianalysis/chat/advancedControls.registry.json")" = "1" ] || { bad "[${PF_NO}] 「清空全部口径」钮未接线/未登记"; S266_BAD=1; }
for S266_SYM in "goalRunner.js:pauseGoalTask" "goalRunner.js:resumeGoalTask" "goalRunner.js:runningGoalCount" "textProtocol.js:isToolResultsEnvelope"; do
  S266_F="${S266_SYM%%:*}"; S266_N="${S266_SYM#*:}"
  [ "$(pf_code "${S266_UI}/src/utils/aiAgent/${S266_F}" | grep -acF "export function ${S266_N}(")" = "0" ] || { bad "[${PF_NO}] 死导出 ${S266_N} 回潮"; S266_BAD=1; }
done
[ "${S266_BAD}" = "0" ] && ok "[${PF_NO}] 死开关/死导出清零:图例首批(缺省关)+ 勾选 / 扫描面扩 / 棘轮归零 / 清空口径钮接线"
}

seg_267() {
# ---- [${PF_NO}] AI 分析主页/存储根修(2026-09-08:D53 发送门闩 try/finally · D54 恢复只替换包内数据集+快照回滚+未来版拒+体积上限 · D55 渲染器单源 ·
#      D61 库健康态横幅 · D67 正文后 error 帧不吞;写法纪律:模式含 {…,…} 先赋值再引用) ----
echo "[${PF_NO}] AI 分析主页 / 存储根修:门闩 / 恢复 / 渲染器单源 / 数据围栏 / 错误帧"
S267_BAD=0
S267_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S267_MAIN="$(pf_src_set "${S267_UI}/src/components/aianalysis/AIAnalysisMain.js")"
# ① 门闩:复位只在 finally;早退不复位形态归零;置 true 后下一非空行是 try{
[ "$(pf_code --fullline "${S267_MAIN}" | grep -acF 'sendingRef.current = false; return;')" = "0" ] || { bad "[${PF_NO}]① 发送门闩早退行内复位回潮(应整段 try/finally)"; S267_BAD=1; }
S267_RESET_PAT='sendingRef.current = false'
S267_FINALLY_PAT='}finally{'
S267_RESET_N="$(pf_code --fullline "${S267_MAIN}" | grep -acF "${S267_RESET_PAT}")"
S267_RESET_OK="$(pf_code --fullline "${S267_MAIN}" | grep -A1 -F "${S267_FINALLY_PAT}" | grep -acF "${S267_RESET_PAT}")"
[ "${S267_RESET_N}" -ge 1 ] && [ "${S267_RESET_N}" = "${S267_RESET_OK}" ] || { bad "[${PF_NO}]① sendingRef 复位须全部落在 finally(实测 ${S267_RESET_N} 处,其中 finally 内 ${S267_RESET_OK} 处)"; S267_BAD=1; }
S267_NEXT="$(pf_code --fullline "${S267_MAIN}" | awk 'f && NF {print; exit} /sendingRef.current = true;/{f=1}' | tr -d '[:space:]')"
[ "${S267_NEXT}" = "try{" ] || { bad "[${PF_NO}]① sendingRef 置 true 后下一行不是 try{(得到:${S267_NEXT})"; S267_BAD=1; }
# ② 恢复:走 aiWorkspaceRestore;旧循环归零;体积上限进解析
S267_RESTORE_CALL='restoreWorkspaceStores(plan, { clearStore, bulkPutStoreRecords, listStoreRecords, putStoreRecord'
S267_PARSE_CALL='parseWorkspaceBackupBlob(blob, { maxBytes: AI_BACKUP_MAX_ZIP_BYTES })'
[ "$(pf_code --fullline "${S267_MAIN}" | grep -acF "${S267_RESTORE_CALL}")" = "1" ] && [ "$(pf_code --fullline "${S267_MAIN}" | grep -acF 'planWorkspaceRestore(payload, storeKeys)')" = "1" ] || { bad "[${PF_NO}]② 主页恢复未走 aiWorkspaceRestore 单源"; S267_BAD=1; }
[ "$(pf_code --fullline "${S267_MAIN}" | grep -acF "${S267_PARSE_CALL}")" = "1" ] || { bad "[${PF_NO}]② 备份解析未带体积上限"; S267_BAD=1; }
[ "$(pf_code --fullline "${S267_MAIN}" | grep -acF 'await clearStore(storeName);')" = "0" ] || { bad "[${PF_NO}]② 旧「对每个已知店一律清」循环回潮"; S267_BAD=1; }
S267_WR="${S267_UI}/src/utils/aiWorkspaceRestore.js"
[ -f "${S267_WR}" ] && [ "$(grep -acF "backup.version.future" "${S267_WR}")" != "0" ] && [ "$(grep -acF "'rolled-back'" "${S267_WR}")" != "0" ] && [ "$(grep -acF 'export const AI_BACKUP_MAX_ZIP_BYTES' "${S267_WR}")" = "1" ] || { bad "[${PF_NO}]② aiWorkspaceRestore.js 缺未来版拒/回滚句柄/体积上限"; S267_BAD=1; }
# ③ 渲染器单源(此前内联 DOMPurify 少硬化)
[ "$(pf_code --fullline "${S267_MAIN}" | grep -acF "from '../../utils/aiMarkdownRender'")" = "1" ] && [ "$(pf_code --fullline "${S267_MAIN}" | grep -acF 'DOMPurify.sanitize(')" = "0" ] && [ "$(pf_code --fullline "${S267_MAIN}" | grep -acF 'marked.setOptions(')" = "0" ] || { bad "[${PF_NO}]③ 主页渲染器未走共享 aiMarkdownRender / 内联净化回潮"; S267_BAD=1; }
# ④ 资料/检索数据围栏 + 默认路径错误可见 + RAG 索引读
S267_CTX="$(pf_src_set "${S267_UI}/src/utils/aiAnalysisContext.js")"; S267_RAG="${S267_UI}/src/utils/aiAnalysisRag.js"
[ "$(pf_code --fullline "${S267_CTX}" | grep -acF 'wrapUntrustedData(')" -ge 1 ] && [ "$(grep -acF "export const UNTRUSTED_DATA_BEGIN" "${S267_RAG}")" = "1" ] && [ "$(grep -acF 'export function neutralizeActionFences' "${S267_RAG}")" = "1" ] || { bad "[${PF_NO}]④ 资料/检索正文未带数据围栏"; S267_BAD=1; }
[ "$(grep -acF 'HOROSA_DATA_BEGIN' "${S267_UI}/src/utils/aiAgent/protocol.js")" != "0" ] || { bad "[${PF_NO}]④ 守则第 2 条未写哨兵语义"; S267_BAD=1; }
[ "$(pf_code --fullline "${S267_CTX}" | grep -acF 'regenerateChartTechniqueSnapshot(record, key, { throwOnError: true })')" = "1" ] && [ "$(pf_code --fullline "${S267_CTX}" | grep -acF "(genError ? 'error' : 'missing')")" = "1" ] || { bad "[${PF_NO}]④ 默认路径重算失败仍静默成 missing"; S267_BAD=1; }
[ "$(pf_code --fullline "${S267_RAG}" | grep -acF "readByIndex(AI_ANALYSIS_STORES.materialChunks, 'materialId'")" = "1" ] && [ "$(pf_code --fullline "${S267_RAG}" | grep -acF "readByIndex(AI_ANALYSIS_STORES.materialEmbeddings, 'materialId'")" = "1" ] || { bad "[${PF_NO}]④ RAG 切块/向量仍整店 getAll"; S267_BAD=1; }
# ⑤ 资料抽取上限 / 流池饱和即拒 / Retry-After 两形态
S267_MAT="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisMaterialService.java"
for S267_K in MAX_DECODED_BYTES MAX_BASE64_CHARS MAX_PDF_PAGES MAX_TEXT_CHARS 'ZipSecureFile.setMinInflateRatio'; do
  [ "$(grep -acF "${S267_K}" "${S267_MAT}")" != "0" ] || { bad "[${PF_NO}]⑤ 资料抽取缺上限 ${S267_K}"; S267_BAD=1; }
done
S267_PROXY="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java"
[ "$(grep -acF 'ThreadPoolExecutor.AbortPolicy()' "${S267_PROXY}")" = "1" ] && [ "$(grep -acF 'CallerRunsPolicy()' "${S267_PROXY}")" = "0" ] && [ "$(grep -acF 'static long retryAfterMs(String header, long nowMillis)' "${S267_PROXY}")" = "1" ] || { bad "[${PF_NO}]⑤ 流池仍 CallerRunsPolicy / Retry-After 未支持日期形态"; S267_BAD=1; }
[ "$(grep -acF '580050' "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/AIAnalysisController.java")" != "0" ] || { bad "[${PF_NO}]⑤ controller 未把池饱和翻成 503(580050)"; S267_BAD=1; }
for S267_T in aiUntrustedDataFence aiAnalysisRagIndex aiAnalysisContextErrors aiProvidersPresets.contract; do
  [ -f "${S267_UI}/src/utils/__tests__/${S267_T}.test.js" ] || { bad "[${PF_NO}]⑤ 缺 ${S267_T}.test.js"; S267_BAD=1; }
done
[ "$(grep -acF 'retryAfterHeaderParsesSecondsAndHttpDate' "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/test/java/spacex/astrostudy/service/AIAnalysisProxyServiceTest.java")" != "0" ] && [ "$(grep -acF 'oversizedBase64IsRejectedFastWith580103' "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/test/java/spacex/astrostudy/service/AIAnalysisMaterialServiceTest.java")" != "0" ] || { bad "[${PF_NO}]⑤ 缺 D58/D60 JUnit"; S267_BAD=1; }
# ⑥ 健康态:store 记 + 主页横幅
[ "$(grep -acF 'export function getAiStoreHealth()' "${S267_UI}/src/utils/aiAnalysisStore.js")" = "1" ] && [ "$(grep -acF 'data-ai-store-degraded=' "${S267_MAIN}")" = "1" ] || { bad "[${PF_NO}]⑥ 库健康态未接(store getAiStoreHealth / 主页 data-ai-store-degraded)"; S267_BAD=1; }
# ⑦ 正文后 error 帧:errorInfo 恒记 + partial;Java 四条中继转发流中错误帧
[ "$(pf_code --fullline "${S267_MAIN}" | grep -acF 'const errorInfo = streamError ? classifyStreamError(streamError) : null;')" = "1" ] && [ "$(pf_code --fullline "${S267_MAIN}" | grep -acF 'partial: partialAfterError || undefined,')" = "1" ] || { bad "[${PF_NO}]⑦ 正文后 error 帧仍被吞(errorInfo 只在正文为空时才记)"; S267_BAD=1; }
S267_PROXY="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java"
[ "$(grep -acF 'emitMidStreamUpstreamError(channel,' "${S267_PROXY}")" -ge 4 ] || { bad "[${PF_NO}]⑦ Java 四条中继未转发流中错误帧"; S267_BAD=1; }
# ⑧ 测试在位
for S267_T in aiAnalysisSendLatch aiWorkspaceRestore aiChatRendererShared aiChatStreamErrorPartial aiAdvancedKeysMigration; do
  [ -f "${S267_UI}/src/utils/__tests__/${S267_T}.test.js" ] || { bad "[${PF_NO}]⑧ 缺 ${S267_T}.test.js"; S267_BAD=1; }
done
[ "$(grep -acF 'midStreamUpstreamErrorFramesAreForwardedAsErrorEvents' "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/test/java/spacex/astrostudy/service/AIAnalysisProxyServiceTest.java")" != "0" ] || { bad "[${PF_NO}]⑧ 缺 Java 流中错误帧 JUnit"; S267_BAD=1; }
[ "${S267_BAD}" = "0" ] && ok "[${PF_NO}] 主页/存储根修:门闩 try/finally / 恢复只动包内店+回滚 / 渲染器单源 / 健康态横幅 / 正文后 error 帧不吞 + 测试在位"
}

seg_268() {
# ---- [${PF_NO}] AI 助手行动能力 行动能力机械网(2026-09-09:D70 动作条四钮以本气泡 messageId 落定(此前 x.messageKey=undefined 跨键落定,
#      哨兵锚住不存在的字段名假绿)· D71 待审条目带 level · D72 桥超时必带取消 + 声明预算取小 · D73 读面超时 · D77 运行时注入 modelSelection · D78 载入预览 ·
#      D79 只读视图单源 · D80/D81 后台吞错留痕 + 调度兜底解绑 · D89 注解只在 MCP 面;写法纪律:模式含 {…,…} 先赋值再引用) ----
echo "[${PF_NO}] AI 助手行动能力机械网:审批到组件层 / 桥超时取消 / 只读视图 / 吞错留痕 / 注解 / 壳限流 / MCP 双纪元"
S268_BAD=0
S268_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S268_AGENT="${S268_UI}/src/utils/aiAgent"
S268_BAR="${S268_UI}/src/components/aianalysis/AgentActionBar.js"
S268_RS="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src"
# ① 审批落定到组件层:x.messageKey 归零;四钮与 Enter 一律带本键;待审条目带 level;任务中心用 approvalVerb
[ "$(pf_code --fullline "${S268_BAR}" | grep -acF 'x.messageKey')" = "0" ] || { bad "[${PF_NO}]① 动作条仍用 trace 条目上不存在的 x.messageKey(跨消息键落定回潮)"; S268_BAD=1; }
[ "$(pf_code --fullline "${S268_BAR}" | grep -acF 'resolveApprovalsByName(x.name, true, messageId)')" = "2" ] && [ "$(pf_code --fullline "${S268_BAR}" | grep -acF 'resolveApproval(x.callId, true, messageId)')" = "1" ] && [ "$(pf_code --fullline "${S268_BAR}" | grep -acF 'resolveApproval(x.callId, false, messageId)')" = "1" ] || { bad "[${PF_NO}]① 动作条四钮未按本气泡 messageId 落定"; S268_BAD=1; }
S268_ENTER='resolveElicitation(elicit.callId, { answer: text.trim() }, elicit.messageKey)'
[ "$(pf_code --fullline "${S268_BAR}" | grep -acF "${S268_ENTER}")" = "2" ] || { bad "[${PF_NO}]① 反问行 Enter/提交未带消息键(应恰两处)"; S268_BAD=1; }
[ "$(grep -acF 'level: p.call.level' "${S268_AGENT}/approvals.js")" = "1" ] || { bad "[${PF_NO}]① listPendingApprovals 条目缺 level(任务中心文案死路径)"; S268_BAD=1; }
[ "$(grep -acF 'approvalVerb(a)' "${S268_UI}/src/components/aianalysis/TaskCenterPanel.js")" = "1" ] || { bad "[${PF_NO}]① 任务中心待办文案未走 approvalVerb"; S268_BAD=1; }
# ② 桥:超时必带取消 + 声明预算取小 + 读面超时;withTimeout 带 onTimeout
S268_BRIDGE="${S268_AGENT}/mcpBridge.js"
S268_SIG='...(ac ? { signal: ac.signal } : {}),'
[ "$(pf_code --fullline "${S268_BRIDGE}" | grep -acF 'new AbortController()')" != "0" ] && [ "$(pf_code --fullline "${S268_BRIDGE}" | grep -acF "${S268_SIG}")" = "1" ] && [ "$(pf_code --fullline "${S268_BRIDGE}" | grep -acF 'onTimeout: ()=>{ if(ac){')" = "1" ] || { bad "[${PF_NO}]② 桥超时未带取消信号(工具在后台跑完=客户端重试即重复写入)"; S268_BAD=1; }
[ "$(pf_code --fullline "${S268_BRIDGE}" | grep -acF 'Math.min(remainMs, declared)')" = "1" ] || { bad "[${PF_NO}]② 桥执行预算未与工具声明 timeoutMs 取小"; S268_BAD=1; }
[ "$(grep -acF 'export const READ_FACE_TIMEOUT_MS = 17000' "${S268_BRIDGE}")" = "1" ] && [ "$(pf_code --fullline "${S268_BRIDGE}" | grep -acF 'readFace(')" -ge 5 ] || { bad "[${PF_NO}]② 读面五方法未带页面侧超时"; S268_BAD=1; }
[ "$(pf_code --fullline "${S268_AGENT}/withTimeout.js" | grep -acF 'onTimeout')" -ge 2 ] || { bad "[${PF_NO}]② withTimeout 缺 onTimeout 取消回调"; S268_BAD=1; }
# ③ 运行时注入 modelSelection;两建任务工具消费;载入工具带 preview;只读视图单源
[ "$(pf_code --fullline "${S268_AGENT}/runtime.js" | grep -acF 'modelSelection: profileId && model ?')" = "1" ] || { bad "[${PF_NO}]③ 运行时未注入 ctx.modelSelection(schedule_task 读的是死参数)"; S268_BAD=1; }
[ "$(pf_code --fullline "${S268_UI}/src/utils/aiTools/tools/createGoalTask.js" | grep -acF 'modelSelection: ctx && ctx.modelSelection')" = "1" ] && [ "$(pf_code --fullline "${S268_UI}/src/utils/aiTools/tools/scheduleTask.js" | grep -acF 'snapshotModelSelection(ctx && ctx.modelSelection)')" = "1" ] || { bad "[${PF_NO}]③ 建任务工具未消费 ctx.modelSelection"; S268_BAD=1; }
[ "$(pf_code --fullline "${S268_UI}/src/utils/aiTools/tools/loadRecordIntoWorkspace.js" | grep -acF 'preview(args){')" = "1" ] || { bad "[${PF_NO}]③ load_record_into_workspace 缺写前预览"; S268_BAD=1; }
[ -f "${S268_AGENT}/readOnlyRegistry.js" ] && [ "$(grep -acF "from './readOnlyRegistry'" "${S268_AGENT}/orchestrator.js")" = "1" ] && [ "$(grep -acF "from '../../aiAgent/readOnlyRegistry'" "${S268_UI}/src/utils/aiTools/tools/runAnalysis.js")" = "1" ] && [ "$(pf_code --fullline "${S268_AGENT}/orchestrator.js" | grep -acF 'const readDef = ')" = "0" ] || { bad "[${PF_NO}]③ 只读注册表视图未单源(orchestrator / runAnalysis 各一份)"; S268_BAD=1; }
# ③ MCP 2026-07-28 双纪元服务端 + stdio 代理注头 + 冒烟 --modern(D88):服务同时服务旧握手纪元与现代无状态纪元
S268_MCP="${S268_RS}/mcp_server.rs"
[ "$(grep -acF 'pub const MCP_MODERN_VERSIONS: [&str; 1] = ["2026-07-28"];' "${S268_MCP}")" = "1" ] && [ "$(grep -acF 'pub fn detect_era(' "${S268_MCP}")" = "1" ] && [ "$(grep -acF 'pub fn validate_modern_request(' "${S268_MCP}")" = "1" ] && [ "$(grep -acF 'pub fn handle_modern(' "${S268_MCP}")" = "1" ] || { bad "[${PF_NO}]③ 本机 MCP 服务缺现代纪元核(版本表 / 纪元判定 / 头体校验 / 现代入口)"; S268_BAD=1; }
[ "$(grep -acF '"server/discover"' "${S268_MCP}")" -ge 2 ] && [ "$(grep -acF '"subscriptions/listen"' "${S268_MCP}")" -ge 2 ] && [ "$(grep -acF 'pub const ERR_HEADER_MISMATCH: i64 = -32020;' "${S268_MCP}")" = "1" ] && [ "$(grep -acF 'pub const ERR_UNSUPPORTED_VERSION: i64 = -32022;' "${S268_MCP}")" = "1" ] || { bad "[${PF_NO}]③ 缺 server/discover / subscriptions/listen / 规范错误码"; S268_BAD=1; }
[ "$(grep -acF 'fn stream_sse(' "${S268_MCP}")" = "1" ] && [ "$(grep -acF 'request.upgrade("sse", resp)' "${S268_MCP}")" = "1" ] && [ "$(grep -acF 'pub fn listen_subscribe(' "${S268_MCP}")" = "1" ] && [ "$(grep -acF 'fn dispatch_method(' "${S268_MCP}")" = "1" ] || { bad "[${PF_NO}]③ SSE 写流 / 长流订阅 / 单一分发表未单源"; S268_BAD=1; }
[ "$(grep -acF 'HOROSA_MCP_MODERN' "${S268_MCP}")" != "0" ] || { bad "[${PF_NO}]③ 现代纪元开关 HOROSA_MCP_MODERN 未在 mcp_server.rs 出现"; S268_BAD=1; }
[ "$(grep -acF 'pub fn modern_line_headers(' "${S268_RS}/mcp_stdio.rs")" = "1" ] && [ "$(grep -acF '"Mcp-Method"' "$(pf_rs_prod "${S268_RS}/mcp_stdio.rs")")" != "0" ] && [ "$(grep -acF 'subscriptions/listen is not available through the stdio proxy' "${S268_RS}/mcp_stdio.rs")" = "1" ] || { bad "[${PF_NO}]③ stdio 代理未按行体注现代三头 / 未本地拒 listen"; S268_BAD=1; }
for S268_T in claude_code_v2_fallback_sequence_against_legacy_only_server modern_discover_returns_versions_capabilities_and_cache_hints modern_header_mismatch_returns_400_minus_32020 modern_unsupported_version_returns_400_minus_32022_with_supported_list modern_mcp_name_base64_sentinel_decoded_before_compare subscriptions_listen_acks_then_delivers_tagged_tools_list_changed_and_legacy_get_concurrently listen_streams_capped_separately_from_legacy_get dual_era_probe_goes_modern_when_enabled_and_legacy_still_served modern_ignores_session_header_and_never_mints_one; do
  [ "$(grep -acF "fn ${S268_T}(" "${S268_MCP}")" = "1" ] || { bad "[${PF_NO}]③ 缺 cargo 测 ${S268_T}"; S268_BAD=1; }
done
for S268_T in serve_forwards_server_discover_and_injects_modern_headers serve_passes_modern_json_errors_through_verbatim serve_answers_subscriptions_listen_locally_without_forwarding; do
  [ "$(grep -acF "fn ${S268_T}(" "${S268_RS}/mcp_stdio.rs")" = "1" ] || { bad "[${PF_NO}]③ 缺 stdio 代理 cargo 测 ${S268_T}"; S268_BAD=1; }
done
S268_SMOKE="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_mcp_smoke.sh"
[ "$(grep -acF -- '--modern' "${S268_SMOKE}")" != "0" ] && [ "$(grep -acF 'Mcp-Method' "${S268_SMOKE}")" != "0" ] && [ "$(grep -acF 'server/discover' "${S268_SMOKE}")" != "0" ] && [ "$(grep -acF 'subscriptions/listen' "${S268_SMOKE}")" != "0" ] || { bad "[${PF_NO}]③ 冒烟脚本缺 --modern 腿"; S268_BAD=1; }
# ④ 后台链吞错留痕:各模块经 bgSink;调度兜底定时器有解绑出口
for S268_M in goalRunner.js:5 tasks/index.js:5 tasks/reconcile.js:2 tasks/scheduler.js:3 automation/engine.js:4 tasks/noticeStore.js:2 tasks/taskStore.js:1 automation/actions.js:1 tasks/taskKinds.js:1; do
  S268_F="${S268_M%%:*}"; S268_N="${S268_M##*:}"
  [ "$(pf_code --fullline "${S268_AGENT}/${S268_F}" | grep -acF 'reportBackgroundFailure(')" -ge "${S268_N}" ] || { bad "[${PF_NO}]④ ${S268_F} 后台 catch 未经 bgSink 留痕(应 ≥${S268_N})"; S268_BAD=1; }
done
[ "$(grep -acF 'export function unbindSchedulerTicks' "${S268_AGENT}/tasks/scheduler.js")" = "1" ] && [ "$(grep -acF 'unbindSchedulerTicks()' "${S268_UI}/src/layouts/app.js")" != "0" ] || { bad "[${PF_NO}]④ 调度兜底定时器无解绑出口"; S268_BAD=1; }
# ⑤ 注解只在 MCP 面:openWorldHint 出网真话 / title / requiresUserInteraction;运行时 toolDefs 不带注解
S268_CAT="${S268_UI}/src/utils/aiTools/catalog.js"
[ "$(pf_code --fullline "${S268_CAT}" | grep -acF "openWorldHint: category === 'external' || origin === 'external'")" = "1" ] && [ "$(pf_code --fullline "${S268_CAT}" | grep -acF 'title: toolLabel(d.name)')" = "1" ] && [ "$(pf_code --fullline "${S268_CAT}" | grep -acF 'requiresUserInteraction')" = "1" ] || { bad "[${PF_NO}]⑤ 工具注解未改真话(openWorldHint / title / requiresUserInteraction)"; S268_BAD=1; }
S268_DEFS='return manifest().map((t)=>({ name: t.name, description: t.description, inputSchema: t.inputSchema }));'
[ "$(pf_code --fullline "${S268_AGENT}/runtime.js" | grep -acF "${S268_DEFS}")" = "1" ] || { bad "[${PF_NO}]⑤ 运行时 toolDefs 形状变了(注解不得进模型请求体)"; S268_BAD=1; }
# ⑥ 测试在位
for S268_T in agentActionBarApprovalScope aiAgentApprovalCallSites.contract aiAgentBackgroundCatch.contract mcpBridgeAbort aiToolsReadOnlyRegistry.contract aiToolsManifestAnnotations.contract; do
  [ -f "${S268_UI}/src/utils/__tests__/${S268_T}.test.js" ] || { bad "[${PF_NO}]⑥ 缺 ${S268_T}.test.js"; S268_BAD=1; }
done
# ⑦ 壳层限流跟随页面策略(D74)+ 桌面桥合同三形态(D84)+ 壳侧零测试面(D86)
[ "$(grep -acF 'rate_per_minute: f64' "${S268_RS}/mcp_server.rs")" != "0" ] && [ "$(grep -acF 'pub fn apply_limits(state: &McpState, calls_per_minute: u32)' "${S268_RS}/mcp_server.rs")" = "1" ] && [ "$(grep -acF 'core.set_calls_per_minute(inner.calls_per_minute);' "${S268_RS}/mcp_server.rs")" = "1" ] || { bad "[${PF_NO}]⑦ 壳令牌桶速率未可配 / 服务重建未重施"; S268_BAD=1; }
[ "$(grep -acF 'fn mcp_server_set_limits_command(' "$(pf_shell_rs_prod)")" = "1" ] && [ "$(grep -acF 'mcp_server_set_limits_command,' "$(pf_shell_rs_prod)")" = "1" ] && [ "$(grep -acF 'mcp_calls_per_minute' "$(pf_shell_rs_prod)")" -ge 5 ] && [ "$(grep -acF 'mcp_server::apply_limits(&state, prefs.mcp_calls_per_minute)' "$(pf_shell_rs_prod)")" = "1" ] || { bad "[${PF_NO}]⑦ 壳缺 set_limits 命令 / 偏好镜像 / 启动重施"; S268_BAD=1; }
[ "$(grep -acF "invokeOptional('mcp_server_set_limits_command'" "${S268_UI}/src/utils/aiAnalysisDesktop.js")" = "1" ] && [ "$(pf_code --fullline "${S268_AGENT}/mcpBridge.js" | grep -acF 'function syncShellLimits()')" = "1" ] && [ "$(pf_code --fullline "${S268_AGENT}/mcpBridge.js" | grep -acF 'if(on){ syncShellLimits(); }')" = "1" ] || { bad "[${PF_NO}]⑦ 页面策略未同步给壳(绑桥 + 策略改动)"; S268_BAD=1; }
S268_DBC="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/check_desktop_bridge_contract.js"
[ "$(grep -acF '|auto_export_|' "${S268_DBC}")" = "1" ] && [ "$(grep -acF "真壳返回 ()" "${S268_DBC}")" != "0" ] && [ "$(grep -acF "真壳返回标量" "${S268_DBC}")" != "0" ] || { bad "[${PF_NO}]⑦ 桌面桥合同检查器未扩到三形态 / 未收编 auto_export_"; S268_BAD=1; }
for S268_T in rate_bucket_follows_configured_limit shadow_keys_whitelist_only_four_record_stores backup_file_name_validation_vectors preferences_default_calls_per_minute_and_roundtrip master_key_runner_hit_miss_and_add_failure run_notify_hook_process_with_timeout; do
  [ "$(grep -acF "${S268_T}" "$(pf_shell_rs_tests)")" != "0" ] || { bad "[${PF_NO}]⑦ 缺 cargo 测 ${S268_T}"; S268_BAD=1; }
done
[ -f "${S268_UI}/src/utils/__tests__/mcpBridgeLimitsSync.test.js" ] || { bad "[${PF_NO}]⑦ 缺 mcpBridgeLimitsSync.test.js"; S268_BAD=1; }
# ⑧ 外部 MCP 客户端双纪元探测回退(D88 客户端侧)+ 壳侧准入(D83):连接先 server/discover,现代服务器按每请求 _meta + 三头、永不 initialize / 会话头;
#    旧服务器(400 纯文本 / -32601 / 探测超时)回退 initialize(线上字节同今日);-32022 无共同版本 ⇒ 报错不回退;input_required 拒收;call 只放行服务器宣告且(readOnlyHint 或允许清单)的工具
S268_CLI="${S268_RS}/mcp_client.rs"
[ "$(grep -acF 'pub const MODERN_PROTOCOL_VERSION: &str = "2026-07-28";' "${S268_CLI}")" = "1" ] && [ "$(grep -acF 'pub enum Era' "${S268_CLI}")" = "1" ] && [ "$(grep -acF 'fn probe_era(' "${S268_CLI}")" = "1" ] && [ "$(grep -acF 'pub fn classify_discover(' "${S268_CLI}")" = "1" ] || { bad "[${PF_NO}]⑧ 外部客户端缺双纪元探测(MODERN_PROTOCOL_VERSION / Era / probe_era / classify_discover)"; S268_BAD=1; }
[ "$(grep -acF 'fn admit_tool(' "${S268_CLI}")" = "1" ] && [ "$(grep -acF 'admit_tool(&spec, &guard.tools, tool)?;' "${S268_CLI}")" = "1" ] && [ "$(grep -acF 'spec.allow_tools.iter().any(' "${S268_CLI}")" = "1" ] && [ "$(grep -acF '"readOnlyHint"' "${S268_CLI}")" != "0" ] || { bad "[${PF_NO}]⑧ 外部客户端 call 缺壳侧准入(admit_tool 在 tools/call 之前;allow_tools / readOnlyHint)"; S268_BAD=1; }
[ "$(grep -acF '("Mcp-Method", method.to_string())' "${S268_CLI}")" = "1" ] && [ "$(grep -acF '("Mcp-Name", encode_header_value(n))' "${S268_CLI}")" = "1" ] && [ "$(grep -acF 'Some("input_required")' "${S268_CLI}")" = "2" ] && [ "$(grep -acF 'fn http_exchange(' "${S268_CLI}")" = "1" ] || { bad "[${PF_NO}]⑧ 外部客户端现代纪元缺三头注入 / input_required 拒收(list+call)/ 单一 HTTP 往返"; S268_BAD=1; }
[ "$(grep -acF '("MCP-Protocol-Version", PROTOCOL_VERSION.to_string())' "${S268_CLI}")" = "1" ] || { bad "[${PF_NO}]⑧ 旧纪元请求头形态变了(必须仍是 2025-06-18 + 会话头,线上字节同今日)"; S268_BAD=1; }
for S268_T in http_probe_modern_server_uses_per_request_meta_and_headers http_probe_legacy_server_falls_back_to_initialize http_probe_modern_error_minus_32022_does_not_fall_back stdio_probe_modern_and_legacy_scripts modern_input_required_result_is_rejected call_admission_mirrors_page_rule; do
  [ "$(grep -acF "fn ${S268_T}(" "${S268_CLI}")" = "1" ] || { bad "[${PF_NO}]⑧ 缺 cargo 测 ${S268_T}"; S268_BAD=1; }
done
# ⑨ Java 工具调用翻译残余(D75 Ollama 收口轮不带 tools / D76 Gemini const 推断类型走枚举名)+ 零测试分支七例 + 出站守卫直测
S268_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src"
[ "$(grep -acF 'boolean ollamaClosing = "none".equals(AIToolCallSupport.toolChoiceNorm(params.get("toolChoice")));' "${S268_JAVA}/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java")" = "1" ] && [ "$(grep -acF 'if(!ollamaTools.isEmpty() && !ollamaClosing) { body.put("tools", ollamaTools); }' "${S268_JAVA}/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java")" = "1" ] || { bad "[${PF_NO}]⑨ Ollama 收口轮仍带 tools(toolChoice=none 应不带)"; S268_BAD=1; }
[ "$(grep -acF 'out.put("type", geminiTypeName(constVal instanceof Number' "${S268_JAVA}/main/java/spacex/astrostudy/service/AIToolCallSupport.java")" = "1" ] && [ "$(grep -acF 'geminiTypeName(' "${S268_JAVA}/main/java/spacex/astrostudy/service/AIToolCallSupport.java")" -ge 4 ] || { bad "[${PF_NO}]⑨ Gemini const 推断类型未走 geminiTypeName(小写不合枚举)"; S268_BAD=1; }
for S268_T in ollamaBodyOmitsToolsWhenToolChoiceNone geminiConstEnumInfersUppercaseType anthropicAndGeminiToolChoiceNoneShapes openAIToolChoiceKeyPresentOnlyWhenTools toolCallDeltaKeepAliveEmittedWhileArgumentsStream redactedThinkingBlocksCollected normalizeToolCallsBadJsonBecomesEmptyObject; do
  [ "$(grep -acF "public void ${S268_T}()" "${S268_JAVA}/test/java/spacex/astrostudy/service/AIToolCallSupportTest.java")" = "1" ] || { bad "[${PF_NO}]⑨ 缺 JUnit ${S268_T}"; S268_BAD=1; }
done
[ -f "${S268_JAVA}/test/java/spacex/astrostudy/service/OutboundUrlGuardTest.java" ] && [ "$(grep -acF 'public void ' "${S268_JAVA}/test/java/spacex/astrostudy/service/OutboundUrlGuardTest.java")" -ge 4 ] || { bad "[${PF_NO}]⑨ 缺 OutboundUrlGuardTest(≥4 例)"; S268_BAD=1; }
# ⑧ 外部客户端起本机命令前的用户确认闸;确认框只因用户点「连接」而起(AI 间接调用的自动重连不弹框);显示层转义不可见字符;改传输即断开旧连接
S268_CLIP="$(pf_rs_prod "${S268_CLI}")"
[ "$(grep -acF 'self.ensure_stdio_approved(&spec, allow_prompt)?;' "${S268_CLIP}")" = "1" ] && [ "$(grep -acF 'fn stdio_spawn_requires_confirmation_and_rechecks_on_change' "${S268_CLI}")" = "1" ] || { bad "[${PF_NO}]⑧ 外部客户端起本机命令前缺用户确认闸(指纹 / 原生确认 / 回归测试)"; S268_BAD=1; }
[ "$(grep -acF 'self.connect_inner(id, false)?;' "${S268_CLIP}")" = "1" ] && [ "$(grep -acF 'self.connect_inner(id, true)' "${S268_CLIP}")" = "1" ] \
  && [ "$(grep -acF '.map(display_field)' "${S268_CLIP}")" = "1" ] && [ "$(grep -acF 'let disconnected = transport_changed && self.disconnect(&spec.id);' "${S268_CLIP}")" = "1" ] \
  && [ "$(grep -acE 'fn (stdio_display_escapes_hidden_chars_and_flags_env_payloads|ai_call_never_prompts_for_unapproved_stdio|upsert_changing_command_disconnects_old_connection)\(' "${S268_CLI}")" = "3" ] \
  || { bad "[${PF_NO}]⑧ 外部 stdio 命令确认框可被 AI 调用间接弹出 / 显示没转义不可见字符 / 改命令不断开旧连接(或回归测试缺)"; S268_BAD=1; }
[ "${S268_BAD}" = "0" ] && ok "[${PF_NO}] 行动能力机械网①–⑨:审批到组件层 / 桥超时取消 / 模型快照注入 / 只读视图单源 / 吞错留痕 / 注解真话 / 壳限流跟随页面 / MCP 双纪元(服务端 + stdio 代理 + 外部客户端探测回退 + 壳侧准入)/ Java 翻译残余 + 测试在位"
}

seg_269() {
# [${PF_NO}] AI 挂载「逐技法 × 挂载内容 × 挂载设置」自检机械网(2026-09-10):①全技法表驱动差分闸(设置→请求体/入参/全局键→正文,候选值×盘变体×上下文,离线不假绿)
#   ②快照段⊆导出预设⊆纳入内容候选 合同 ③残余死齿轮修复的判别向量各在位(奇门中门 0≡false / 盘类进 pan.options / 紫微太岁关系人数组 / 正传心易缺省 /
#   八字起运行 / 巴比伦纪元 / 皇极心易后端键 / 印占三旗问事 / 大定所推之年 / 地占无头不读页面事盘)④jest 后端请求 shim(js-rsa 严格模式)在位;负锚:旧死形态回潮即红。
echo "[${PF_NO}] AI 挂载「逐技法 × 挂载内容 × 挂载设置」自检网"
S269_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"; S269_BAD=0
for S269_T in mountSettingsDiffAll mountSectionOptionsContract mountAuditResiduals mountAuditIndiaPrashna mountAuditZhengchuanDading mountAuditBuFixes mountAuditCaseBaselines mountAuditWiring mountAuditGuolaoSu28 mountAuditGuolaoNodeMode mountAuditHeluoHuagong mountAuditZhengchuanGender mountAuditIndiaCalibre mountAuditJieqiStale mountAuditAstroLike mountAuditRelativeParties mountAuditLiurengHeadless mountAuditZeriSave mountAuditZiweiDayBoundary mountAuditLabels mountAuditJinkouSuzhan pdSphereStamp; do
  [ -f "${S269_UI}/src/utils/__tests__/${S269_T}.test.js" ] || { bad "[${PF_NO}]① 缺挂载自检测试 ${S269_T}.test.js"; S269_BAD=1; }
done
S269_DN="${S269_UI}/src/utils/__tests__/mountSettingsDiffAll.test.js"
pf_test_disabled "${S269_DN}" && { bad "[${PF_NO}]① 差分闸含被跳过 / 被独占的用例(闸门被关)"; S269_BAD=1; }
S269_P_DE="const DEAD_EXEMPT = {"; S269_P_PR="pruneOptionsToNonDefault(key, { [field.name]: v }, baseline)"
[ "$(grep -acF "${S269_P_DE}" "${S269_DN}")" = "1" ] && [ "$(grep -acF "${S269_P_PR}" "${S269_DN}")" = "1" ] && [ "$(grep -acF "HOROSA_DIFFNET_OFFLINE" "${S269_DN}")" -ge 1 ] || { bad "[${PF_NO}]① 差分闸三锚(豁免表/覆盖判据同源/离线不假绿)缺失"; S269_BAD=1; }
[ "$(grep -acF "'^js-rsa$'" "${S269_UI}/jest.config.js")" = "1" ] && [ -f "${S269_UI}/test/jsRsaJestShim.js" ] || { bad "[${PF_NO}]④ jest js-rsa shim 未接(后端请求在 jest 内静默失败=在线判据全成假绿)"; S269_BAD=1; }
S269_DJ="${S269_UI}/src/components/dunjia/DunJiaCalc.js"
[ "$(grep -acF "feiMenZhongCan: opts.feiMenZhongCan !== false," "${S269_DJ}")" = "0" ] && [ "$(grep -acF "opts.feiMenZhongCan === 0 || opts.feiMenZhongCan === '0'" "${S269_DJ}")" -ge 2 ] || { bad "[${PF_NO}]③ 奇门中门参与 0/'0' 判关回潮(挂载 select 0 被当参与)"; S269_BAD=1; }
S269_P_CC="? { chartCategory: opts.chartCategory } : {}),"
[ "$(grep -acF "${S269_P_CC}" "${S269_DJ}")" = "1" ] || { bad "[${PF_NO}]③ 奇门盘类未随 opts 进 pan.options"; S269_BAD=1; }
S269_CTX="$(pf_src_set "${S269_UI}/src/utils/aiAnalysisContext.js")"
[ "$(grep -acF "noPageFallback: true" "${S269_CTX}")" -ge 2 ] || { bad "[${PF_NO}]③ 塔罗/地占无头「不读页面当前事盘」旗少于 2 处"; S269_BAD=1; }
S269_P_TS="if(record && Array.isArray(record.taiSuiRelatives)){"
[ "$(grep -acF "${S269_P_TS}" "${S269_CTX}")" = "1" ] || { bad "[${PF_NO}]③ 紫微太岁关系人数组形态处理缺失(挂载覆盖路径串化剪空回潮)"; S269_BAD=1; }
[ "$(grep -acF "item: record.zcItem || '父母', sound: record.zcSound || '日'" "${S269_CTX}")" = "1" ] || { bad "[${PF_NO}]③ 正传心易缺省未落地(无声音=查询段整段不产)"; S269_BAD=1; }
[ "$(grep -acF "deriveDadingYearPillars: dd.deriveDadingYearPillars," "${S269_CTX}")" = "1" ] && [ "$(grep -acF "export function deriveDadingYearPillars(" "${S269_UI}/src/utils/zhengchuanDadingLocal.js")" = "1" ] || { bad "[${PF_NO}]③ 大定所推之年派生未接无头"; S269_BAD=1; }
S269_P_IT="indiaTripataki: { value: (record.indiaTripataki === 1"
[ "$(grep -acF "${S269_P_IT}" "${S269_CTX}")" = "1" ] && [ "$(grep -acF "name: 'indiaPrashnaTime'" "${S269_UI}/src/utils/techniqueMountSettings.js")" = "1" ] || { bad "[${PF_NO}]③ 印占三旗/问事挂载链缺失"; S269_BAD=1; }
S269_TMS="${S269_UI}/src/utils/techniqueMountSettings.js"
# 花括号内含逗号的字面锚必须先赋值再引用(bash 3.2 花括号展开陷阱)
S269_P_OLD="{ value: 'strokes'"; S269_P_NEW="{ value: 'character'"   # 锚只咬值域(后端只认 character/direction);标签随页面文案
[ "$(grep -acF "${S269_P_OLD}" "${S269_TMS}")" = "0" ] && [ "$(grep -acF "${S269_P_NEW}" "${S269_TMS}")" = "1" ] || { bad "[${PF_NO}]③ 皇极心易起卦法值域回潮(strokes/object 后端不识)"; S269_BAD=1; }
[ "$(grep -acF "name: 'babylonEphemerisSource'" "${S269_TMS}")" = "0" ] || { bad "[${PF_NO}]③ 巴比伦位置源死齿轮回潮(无头无消费点)"; S269_BAD=1; }
S269_P_QY='lines.push(`起运：${bazi.directInfo}`)'
[ "$(grep -acF "${S269_P_QY}" "${S269_UI}/src/components/cntradition/BaZi.js")" = "1" ] || { bad "[${PF_NO}]③ 八字 [大运] 起运行缺失(起运精度齿轮无处落地)"; S269_BAD=1; }
[ "$(grep -acF "安息纪元" "${S269_UI}/src/utils/babylonAiSnapshot.js")" = "1" ] || { bad "[${PF_NO}]③ 巴比伦纪元行缺失"; S269_BAD=1; }
[ "$(grep -acF "wuxingOfMansion(me, s.qinWuxing)" "${S269_UI}/src/components/yanqin/yanqinSnapshot.js")" = "1" ] || { bad "[${PF_NO}]③ 演禽演法·占卜五行口径未随流派"; S269_BAD=1; }
[ "${S269_BAD}" = "0" ] && ok "[${PF_NO}] AI 挂载逐技法自检机械网①–④:差分闸/段合同/残余修复判别向量/js-rsa shim 全在位"
}
