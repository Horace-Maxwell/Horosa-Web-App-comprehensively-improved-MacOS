#!/usr/bin/env bash
# 发布前自检 · 桌面壳(启动 / 服务 / 缩放 / 性能)
# 由 preflight/lib.sh 按登记表装载;只定义函数 seg_<id>(),不直接执行。段号用 ${PF_NO}(登记表第二列)。

seg_12() {
echo "[12] 本地服务端口健壮性哨兵(v2.5.0)"
WEBCHART="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
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
}

seg_14() {
# 本段自己取(与前段同值;段与段之间不靠函数体里赋的变量传值,--only 单跑也成立)
MAINRS="$(pf_shell_rs_prod)"
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
}

seg_15() {
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
  if grep "bind_err_re=" "${STARTSH}" | pipe_has -F "|port"; then
    bad "bind_err_re 含裸 'port' 分支 —— 会把正常输出误判为端口冲突(红队 C2),请改回精确 token"
  else
    ok "修法2 bind_err_re 不含裸 port(精确匹配,无误判)"
  fi
else
  warn "start_horosa_local.sh 不存在,跳过修法2 哨兵"
fi
}

seg_16() {
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
}

seg_17() {
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
}

seg_18() {
echo "[18] 前端排盘透明重试哨兵(修法5:幂等 raw-fetch 重试,SSE/AI 排除)"
CHARTFETCH="${UISRC}/utils/chartFetch.js"
REQJS="${UISRC}/utils/request.js"
if [ -f "${CHARTFETCH}" ] && [ -f "${REQJS}" ]; then
  # 合法接入=cachedKentangFetch(缓存壳,内部走 fetchChartWithRetry,重试语义
  # 由调用方 cfg 控制:原四引擎保默认重试,原裸 fetch 站点传 {retries:0} 保旧单发)。
  # 四引擎现统一经 services/kentangPost.js 的 postKentang(单一来源,内部 = cachedKentangFetch;缺省 {retries:0}):
  #   引擎调用须显式 { cacheConfig: undefined } 才走缓存层缺省重试 —— 漏写 = 冷启动首个排盘单发、无重试(本段要抓的病)。
  #   接入判据:引擎直接用缓存壳,或经 postKentang 且带 cacheConfig: undefined。
  S18_ENGINES_OK=1
  for s18_spec in "components/dunjia/DunJiaCalc.js|qimen" "components/taiyi/TaiYiCalc.js|taiyi" "components/jinkou/JinKouCalc.js|jinkou" "services/qizheng.js|qizhengkin"; do
    s18_f="${UISRC}/${s18_spec%%|*}"; s18_m="${s18_spec##*|}"
    if grep -q "cachedKentangFetch(" "${s18_f}" 2>/dev/null; then continue; fi
    grep -qE "postKentang\('${s18_m}', '[a-z]+', [^;]*\{ cacheConfig: undefined \}\)" "${s18_f}" 2>/dev/null || { S18_ENGINES_OK=0; echo "    ${s18_spec%%|*}:${s18_m} 主路径没接缓存壳,或经 postKentang 却没带 { cacheConfig: undefined }(= 无重试)"; }
  done
  if grep -q "export async function fetchChartWithRetry" "${CHARTFETCH}" \
     && grep -q "fetchChartWithRetry(url, fetchOpts, cfg)" "${UISRC}/utils/kentangCache.js" \
     && grep -q "await cachedKentangFetch(buildKentangEndpoint(module, path)" "${UISRC}/services/kentangPost.js" \
     && [ "${S18_ENGINES_OK}" = "1" ]; then
    ok "修法5 缓存壳(内含 fetchChartWithRetry)接入四引擎 raw-fetch 主路径(经 postKentang 单源且保默认重试)"
  else
    bad "排盘 raw-fetch 站点未全部接入缓存壳/壳内失去重试 —— 冷启动首个排盘无重试会弹「未就绪」(修法5)"
  fi
  # SSE 必须排除重试:requestStream 函数体内不得出现重试封装(防双发/重复计费)。
  if grep -q "export async function requestStream" "${REQJS}" \
     && ! awk '/export async function requestStream/,/^}/' "${REQJS}" | pipe_has "fetchWithRetryConnRefused"; then
    ok "修法5 SSE(requestStream)未接入重试(防双发/重复计费)"
  else
    bad "requestStream 疑似接入重试封装 —— SSE/AI 流绝不可重试(会双发/重复计费,红队)"
  fi
else
  warn "chartFetch.js/request.js 不存在,跳过修法5 哨兵"
fi
}

seg_19() {
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
}

seg_27() {
# 27. 本机地址出站一律直连,不进系统代理(跨平台:Mac 与 Windows 同因)。
#     病史:启动器设 -Djava.net.useSystemProxies=true;开 Clash/v2ray/加速器时 JVM 把 127.0.0.1/localhost 出站也塞进代理。
#     ① HTTP 代理层:Apache 命令对任意目标裸 setProxy(getHttpHost()) → 代理转发回环卡顿/超时 →「本地排盘服务未就绪」。
#     ② SOCKS 层:Windows 系统代理只写「主机:端口」时 JDK 把同一个 HTTP 代理也报成 SOCKS,且走系统代理时
#        http.nonProxyHosts / socksNonProxyHosts 都不参与判定 → 每个裸 Socket 连本机都先做 SOCKS 握手 →
#        「Reply from SOCKS server has bad version」,排盘全线失败、界面空白。
#     修法:后端入口第一件事装 LoopbackDirectProxySelector(本机 → NO_PROXY,其余交原选择器);Apache 层代理一律经
#     getHttpHostFor(目标);JDK HttpClient 只吃装好的选择器;后端连不上引擎时回固定业务码,前端即使 silent 也可见。
echo "[27] 本机地址直连不进系统代理(代码层根修 + 引擎连不上可见)"
S27_BAD=0
S27_J="${REPO_ROOT}/Horosa-Web/astrostudysrv"
S27_SEL="${S27_J}/boundless/src/main/java/boundless/net/http/LoopbackDirectProxySelector.java"
S27_UTIL="${S27_J}/boundless/src/main/java/boundless/net/http/HttpClientUtility.java"
S27_MAIN="${S27_J}/astrostudyboot/src/main/java/spacex/astrostudyboot/AstroStudyProgram.java"
S27_AI="${S27_J}/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java"
S27_HELPER="${S27_J}/astrostudy/src/main/java/spacex/astrostudy/helper/AstroHelper.java"
S27_FE_FAIL="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/requestFailure.js"
S27_FE_REQ="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/request.js"
# ① 全局选择器:select 里本机目标直接 DIRECT(在交原选择器之前)
S27_SELBODY="$(awk '/public List<Proxy> select\(URI uri\)/{f=1} f{print} f&&/^\t}$/{exit}' "${S27_SEL}" 2>/dev/null)"
if [ -z "${S27_SELBODY}" ]; then
  bad "[27] 缺 LoopbackDirectProxySelector.select(全局本机直连选择器被删?)"; S27_BAD=1
else
  S27_LB_LINE="$(printf '%s\n' "${S27_SELBODY}" | grep -an 'if (isLoopbackTarget(uri))' | head -1 | cut -d: -f1)"
  S27_DG_LINE="$(printf '%s\n' "${S27_SELBODY}" | grep -an 'delegate.select(uri)' | head -1 | cut -d: -f1)"
  S27_RET_OK="$(printf '%s\n' "${S27_SELBODY}" | grep -A1 -a 'if (isLoopbackTarget(uri))' | grep -ac 'return DIRECT;' || true)"
  if [ -z "${S27_LB_LINE}" ] || [ -z "${S27_DG_LINE}" ] || [ "${S27_LB_LINE}" -ge "${S27_DG_LINE}" ] || [ "${S27_RET_OK:-0}" -lt 1 ]; then
    bad "[27] 选择器没有「本机目标先返回 DIRECT、再交原选择器」—— 开系统代理时裸 Socket 连本机会被送进 SOCKS"; S27_BAD=1
  fi
fi
# ② 主入口第一句装选择器(早于任何出站与客户端构造)
S27_FIRST="$(awk '/public static void main\(String\[\] args\)/{f=1;next} f && $0 !~ /^[[:space:]]*(\/\/.*)?$/ {print; exit}' "${S27_MAIN}" 2>/dev/null)"
printf '%s' "${S27_FIRST}" | pipe_has 'LoopbackDirectProxySelector.install()' || { bad "[27] AstroStudyProgram.main 第一句不是 LoopbackDirectProxySelector.install()(实得:${S27_FIRST})"; S27_BAD=1; }
grep -aq 'LoopbackDirectProxySelector.install();' "${S27_UTIL}" || { bad "[27] HttpClientUtility 静态初始化缺选择器兜底安装"; S27_BAD=1; }
# ③ 反锚:后端任何地方都不许对任意目标裸取代理(必须经 getHttpHostFor / getProxyFor 按目标判)
S27_RAW="$(pf_prod_grep -naE 'setProxy\(HttpClientUtility\.getHttpHost\(\)\)|HttpClientUtility\.getProxy\(\)|\.proxy\(ProxySelector\.getDefault\(\)\)' "${S27_J}" java)"
[ -z "${S27_RAW}" ] || { bad "[27] 仍有裸取代理的出站点(本机目标会进代理):$(printf '%s' "${S27_RAW}" | head -3 | tr '\n' ' ')"; S27_BAD=1; }
S27_FOR="$(pf_prod_hits -aE 'setProxy\(HttpClientUtility\.getHttpHostFor\(' "${S27_J}/boundless/src/main/java/boundless/net/http" java | wc -l | tr -d ' ')"
[ "${S27_FOR:-0}" -ge 10 ] || { bad "[27] 经 getHttpHostFor 按目标设代理的命令只有 ${S27_FOR} 个(< 10,被改回裸 getHttpHost?)"; S27_BAD=1; }
grep -aq 'setProxy(HttpClientUtility.getHttpHostFor(request == null ? null : request.getURI()))' "${S27_J}/boundless/src/main/java/boundless/net/http/HttpUriRequestHystrixCommand.java" || { bad "[27] 主出站命令 doCmd 未按目标取代理"; S27_BAD=1; }
grep -aq '.proxy(LoopbackDirectProxySelector.install())' "${S27_AI}" || { bad "[27] AI 流式客户端未用已装好的本机直连选择器(构造时定死,取到裸默认选择器则本机模型服务进代理)"; S27_BAD=1; }
# 后端每个 JDK HttpClient 构造都显式给已装好的选择器(不给 / 给裸默认 = 取构造那一刻的默认选择器,构造早于入口安装时本机进代理)
S27_JDK_BAD=""
S27_JDK_N=0
for S27_F in $(pf_prod_hits -a 'HttpClient.newBuilder()' "${S27_J}" java); do
  S27_NB="$(grep -ac 'HttpClient.newBuilder()' "${S27_F}" || true)"
  S27_NP="$(grep -ac '.proxy(LoopbackDirectProxySelector.install())' "${S27_F}" || true)"
  S27_JDK_N=$((S27_JDK_N + S27_NB))
  [ "${S27_NB}" = "${S27_NP}" ] || S27_JDK_BAD="${S27_JDK_BAD} $(basename "${S27_F}")(${S27_NB}/${S27_NP})"
done
[ -z "${S27_JDK_BAD}" ] || { bad "[27] JDK HttpClient 构造未给已装好的本机直连选择器(构造数/给选择器数):${S27_JDK_BAD}"; S27_BAD=1; }
[ "${S27_JDK_N}" -ge 3 ] || { bad "[27] 后端 JDK HttpClient 构造只找到 ${S27_JDK_N} 处(< 3:AI 流式 / 网页读取 / 联网检索,扫描面失效?)"; S27_BAD=1; }
[ -f "${S27_J}/astrostudy/src/test/java/spacex/astrostudy/service/AIWebOutboundProxyRouteTest.java" ] || { bad "[27] 缺网页读取 / 联网检索经代理路由与守卫的单测"; S27_BAD=1; }
# 壳层连本机 MCP 服务(HTTP 传输)同口径:本机回环一律 no_proxy
S27_MCP="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/mcp_client.rs"
if [ -f "${S27_MCP}" ]; then
  grep -A1 -a 'if crate::mcp_stdio::url_host_is_loopback(&parsed) {' "${S27_MCP}" | pipe_has 'builder = builder.no_proxy();' || { bad "[27] 壳层 MCP 客户端连本机服务未绕开环境代理"; S27_BAD=1; }
fi
# ④ 引擎连不上 → 固定业务码;前端同码同键 + silent 也可见
S27_JCODE="$(grep -aoE 'EngineLinkErrorCode = [0-9]+;' "${S27_HELPER}" 2>/dev/null | grep -aoE '[0-9]+' | head -1)"
S27_FCODE="$(grep -aoE 'ENGINE_LINK_ERROR_CODE = [0-9]+;' "${S27_FE_FAIL}" 2>/dev/null | grep -aoE '[0-9]+' | head -1)"
if [ -z "${S27_JCODE}" ] || [ "${S27_JCODE}" != "${S27_FCODE}" ]; then
  bad "[27] 引擎连不上业务码前后端不一致(后端='${S27_JCODE}' 前端='${S27_FCODE}')"; S27_BAD=1
fi
grep -A1 -a 'if(HttpClientUtility.isConnectFailure(e)){' "${S27_HELPER}" | pipe_has 'throw new ErrorCodeException(EngineLinkErrorCode, EngineLinkErrorKey, e);' || { bad "[27] AstroHelper 连不上引擎时不再抛固定业务码"; S27_BAD=1; }
S27_SURF="$(grep -ac '}else if(isEngineLinkFailure(e)){' "${S27_FE_REQ}" 2>/dev/null || true)"
[ "${S27_SURF:-0}" -ge 2 ] || { bad "[27] request / requestRaw 的 silent 分支不再把引擎连不上提示出来(${S27_SURF} < 2)——界面会空白却不报错"; S27_BAD=1; }
[ "${S27_BAD}" = "0" ] && ok "[27] 本机直连三层在位(全局选择器先判本机 / 主入口第一句安装 / 零裸取代理,按目标命令×${S27_FOR},JDK 客户端×${S27_JDK_N} 全给选择器)+ 引擎连不上码 ${S27_JCODE} 前后端同步且 silent 可见"
}

seg_46() {
# [46] 后端只绑回环 (2026-06-12): :9999 默认 0.0.0.0 局域网可达(AI 代理持用户 key)。双保险。
echo "[46] 后端回环绑定双保险"
S46_BAD=0
grep -q "^server.address=127.0.0.1" "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/resources/application.properties" || { bad "[46] application.properties 缺 server.address=127.0.0.1"; S46_BAD=1; }
grep -q -- "--server.address=127.0.0.1" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" || { bad "[46] start 脚本缺 --server.address=127.0.0.1"; S46_BAD=1; }
[ "${S46_BAD}" = "0" ] && ok "[46] properties + start 脚本 双双只绑 127.0.0.1"
}

seg_47() {
# [47] Java component-scan 集合不漂移 (2026-06-12): spring-mvc.xml base-package = 注册真相,
#      新增包须过可达性评审(遗留死模块绝不悄然激活)。
echo "[47] Java 扫描包集合"
S47_GOT="$(python3 -c "
import re
src = open('${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/resources/conf/spring-mvc.xml', encoding='utf-8').read()
m = re.search(r'base-package=\"(.*?)\"', src, re.S)
pkgs = sorted(p.strip() for p in m.group(1).split(',') if p.strip()) if m else []
print(','.join(pkgs))" 2>/dev/null)"
S47_WANT="boundless.spring.help.controller,boundless.spring.help.springcomp,spacex.astrostudy.controller,spacex.astrostudy.service,spacex.astrostudycn.controller,spacex.basecomm.controller"
[ "${S47_GOT}" = "${S47_WANT}" ] && ok "[47] component-scan 6 包精确不漂移" || bad "[47] 扫描包集合漂移: ${S47_GOT}"
}

seg_49() {
# [49] CSP 双表面在位 (2026-06-12): 主界面经 tiny_http(main.rs),launcher 经 tauri.conf。
echo "[49] CSP 双表面"
S49_BAD=0
grep -q "Content-Security-Policy" "$(pf_shell_rs_prod)" || { bad "[49] main.rs 静态服务器缺 CSP 头"; S49_BAD=1; }
python3 -c "
import json
c = json.load(open('${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/tauri.conf.json'))
csp = c['app']['security'].get('csp')
raise SystemExit(0 if csp and 'default-src' in csp else 1)" || { bad "[49] tauri.conf launcher CSP 为空"; S49_BAD=1; }
[ "${S49_BAD}" = "0" ] && ok "[49] 主界面 + launcher CSP 均在位"
}

seg_85() {
# 本段自己取(与前段同值;段与段之间不靠函数体里赋的变量传值,--only 单跑也成立)
S84_MAIN="$(pf_shell_rs_prod)"
# 85. 启动健康看门狗(WS-1d,A/B 自愈):状态机/回滚/ready 确认/回归测试全在位
echo "[85] 启动健康看门狗"
S85_BAD=0
grep -q "WATCHDOG_ROLLBACK_THRESHOLD" "${S84_MAIN}" 2>/dev/null || { bad "[85] 看门狗阈值缺位"; S85_BAD=1; }
grep -q "fn rollback_runtime_to_previous" "${S84_MAIN}" 2>/dev/null || { bad "[85] previous 槽回滚函数缺位"; S85_BAD=1; }
grep -q "launch_health_confirm" "${S84_MAIN}" 2>/dev/null || { bad "[85] ready 确认(pending 归零)缺位"; S85_BAD=1; }
grep -q "cleanup_previous_slots" "${S84_MAIN}" 2>/dev/null || { bad "[85] previous 槽 ready 后回收缺位"; S85_BAD=1; }
grep -q "watchdog_health_state_machine_and_rollback" "$(pf_shell_rs_tests)" 2>/dev/null || { bad "[85] 看门狗回归测试缺位"; S85_BAD=1; }
[ "${S85_BAD}" = "0" ] && ok "[85] 看门狗 状态机/回滚/确认/测试 全在位"
}

seg_87() {
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
}

seg_88() {
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
}

seg_89() {
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
  grep -q "${seg}" "$(pf_shell_rs_prod)" 2>/dev/null || { bad "[89] 账本段 ${seg} 缺位"; S89_BAD=1; }
done
grep -q "py.warmup_kentang" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py" 2>/dev/null || { bad "[89] 账本段 py.warmup_kentang 缺位"; S89_BAD=1; }
# 前端启动段进账本:上报单源 + 主页首盘段 + 壳命令(缺任一 = 前端段又回到黑箱)
grep -q "web_ledger_mark_command" "${S89_UI}/utils/startupLedger.js" 2>/dev/null || { bad "[89] 前端启动账本上报单源缺位(utils/startupLedger.js)"; S89_BAD=1; }
grep -q "web.first_chart_paint" "${S89_UI}/pages/index.js" 2>/dev/null || { bad "[89] 账本段 web.first_chart_paint 未接线 pages/index"; S89_BAD=1; }
grep -q "fn web_ledger_mark_command" "$(pf_shell_rs_prod)" 2>/dev/null || { bad "[89] 壳缺 web_ledger_mark_command(前端段无处落账)"; S89_BAD=1; }
# 就绪门事件化:壳同参确认必派事件,前端门必监听(缺任一 = 首盘回到「等下一次探活」)
grep -q "horosa:backend-confirmed" "$(pf_shell_rs_prod)" 2>/dev/null || { bad "[89] 壳 init 脚本未派 horosa:backend-confirmed"; S89_BAD=1; }
grep -q "BACKEND_CONFIRMED_EVENT" "${S89_UI}/utils/backendBootGate.js" 2>/dev/null || { bad "[89] 前端就绪门未监听壳确认事件"; S89_BAD=1; }
[ "${S89_BAD}" = "0" ] && ok "[89] 瞬时化资产 全在位"
}

seg_94() {
# 94. 会话自愈与停服安全(运行期可靠性):
#     ① 服务存活看门狗(启动看门狗管「起不来」,这管「跑着跑着死了」)+ 限频自动重启
#        + 菜单「重启本地服务」人工兜底;
#     ② 停服链跨实例安全:pid 文件端口后缀(双实例互覆→误杀/漏杀)+ 杀前进程指纹校验
#        (pid 复用防误杀无辜)+ stop_runtime 传真实端口(否则动态口会话停不干净)。
echo "[94] 会话自愈与停服安全"
S94_BAD=0
S94_RS="$(pf_shell_rs_prod)"
grep -q "fn start_service_supervisor" "${S94_RS}" || { bad "[94] 缺服务存活看门狗"; S94_BAD=1; }
grep -q "fn restart_local_services" "${S94_RS}" || { bad "[94] 缺服务重启例程"; S94_BAD=1; }
grep -q "MENU_RESTART_SERVICES" "${S94_RS}" || { bad "[94] 缺「重启本地服务」菜单"; S94_BAD=1; }
grep -q "struct BootstrapBusyGuard" "${S94_RS}" || { bad "[94] 缺引导互斥守卫(看门狗会与更新/修复抢跑)"; S94_BAD=1; }
grep -q "fn stop_runtime(paths: &RuntimePaths, ports: Option<(u16, u16)>)" "${S94_RS}" || { bad "[94] stop_runtime 缺端口参数"; S94_BAD=1; }
grep -q "指纹不符的进程绝不能被停服脚本误杀" "$(pf_shell_rs_tests)" || { bad "[94] 缺停服误杀回归测试"; S94_BAD=1; }
S94_STOP="${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh"
grep -q '\.horosa_py\.\${CHART_PORT}\.pid' "${S94_STOP}" || { bad "[94] stop 脚本 pid 文件缺端口后缀"; S94_BAD=1; }
grep -q 'expected_pattern' "${S94_STOP}" || { bad "[94] stop 脚本缺杀前指纹校验"; S94_BAD=1; }
grep -q '\.horosa_py\.\${CHART_PORT}\.pid' "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" || { bad "[94] start 脚本 pid 文件缺端口后缀"; S94_BAD=1; }
[ "${S94_BAD}" = "0" ] && ok "[94] 会话自愈与停服安全 全在位"
}

seg_95() {
# 95. 确定性运行环境(不因系统设置/其它软件/长期运行而变):JVM locale 钉死(泰语系统
#     默认佛历=年+543)/桌面 Redis 禁用(不触碰用户自装 :6379)/本地文档缓存每用户
#     (共享无锁 JSON 会互踩)/日志保留策略(防写满盘)/安装器拒绝文案双语。
echo "[95] 确定性运行环境"
S95_BAD=0
S95_SH="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
grep -q '\-Duser\.language=zh' "${S95_SH}" || { bad "[95] java 启动缺 locale 钉死"; S95_BAD=1; }
grep -q 'paramhash\.cache\.redis\.enable=false' "${S95_SH}" || { bad "[95] 桌面 redis 未禁用"; S95_BAD=1; }
grep -q '\${HOME}/\.horosa-cache/mongo-fallback' "${S95_SH}" || { bad "[95] 文档缓存默认未每用户化"; S95_BAD=1; }
grep -q 'HOROSA_MONGO_FALLBACK_DIR' "$(pf_shell_rs_prod)" || { bad "[95] 壳未传每用户缓存目录"; S95_BAD=1; }
grep -q 'fn prune_logs_dir_best_effort' "$(pf_shell_rs_prod)" || { bad "[95] 壳缺日志修剪"; S95_BAD=1; }
S95_LOG="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/resources/log4j2.xml"
grep -q '<Delete basePath' "${S95_LOG}" || { bad "[95] log4j2 缺 Delete 保留策略"; S95_BAD=1; }
grep -q 'SizeBasedTriggeringPolicy' "${S95_LOG}" || { bad "[95] log4j2 缺按量滚转"; S95_BAD=1; }
grep -q 'Apple Silicon Required' "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/distribution.xml.template" || { bad "[95] 安装器拒绝文案缺英文"; S95_BAD=1; }
grep -q 'pkgutil --forget' "${REPO_ROOT}/Horosa_Desktop_Installer/UNINSTALL.md" || { bad "[95] 卸载文档缺收据清除"; S95_BAD=1; }
[ "${S95_BAD}" = "0" ] && ok "[95] 确定性运行环境 全在位"
}

seg_103() {
# ── [103] 看门狗深探+越限UX+web 监督+横幅自愈(U-F) ────────────────────────
echo "[103] 看门狗深探链"
S103_BAD=0
S103_MAIN="$(pf_shell_rs_prod)"
S103_BANNER="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/ServiceStatusBanner.js"
S103_RECOVERY="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/serviceRecovery.js"
grep -q 'fn probe_identity' "${S103_MAIN}" || { bad "[103] 缺深度身份探针"; S103_BAD=1; }
grep -q 'fn supervisor_step' "${S103_MAIN}" || { bad "[103] 缺双 streak 状态机"; S103_BAD=1; }
grep -q 'SUPERVISOR_SILENT_ROUNDS' "${S103_MAIN}" || { bad "[103] 缺 HttpSilent 慢判常量"; S103_BAD=1; }
grep -q 'rust.web_server_restarted' "${S103_MAIN}" || { bad "[103] web 静态服务器未纳管"; S103_BAD=1; }
grep -q 'fn restart_local_services_command' "${S103_MAIN}" || { bad "[103] 缺轻量重启命令"; S103_BAD=1; }
# 命令必须注册进 generate_handler(定义了没注册=前端调不到)
awk '/generate_handler!\[/,/\]\)/' "${S103_MAIN}" | pipe_has 'restart_local_services_command' || { bad "[103] 轻量重启命令未注册"; S103_BAD=1; }
grep -q 'supervisor_gave_up' "${S103_MAIN}" || { bad "[103] 缺越限事件"; S103_BAD=1; }
grep -q 'gave_up_latched' "${S103_MAIN}" || { bad "[103] 越限未闩锁(账本刷屏回潮)"; S103_BAD=1; }
grep -q '__horosaServiceEvent' "${S103_MAIN}" || { bad "[103] 缺服务监督事件通道"; S103_BAD=1; }
# 前端:自动轮询+事件钩子+错线修复(反向锚:横幅不得再直调全量修复命令作首选)
[ -f "${S103_RECOVERY}" ] || { bad "[103] 缺 serviceRecovery.js"; S103_BAD=1; }
grep -q 'startRecoveryPolling' "${S103_BANNER}" || { bad "[103] 横幅缺自动恢复轮询"; S103_BAD=1; }
grep -q 'verifyBackendIdentity' "${S103_BANNER}" || { bad "[103] 横幅重试未走身份探测"; S103_BAD=1; }
grep -q '__horosaServiceEvent' "${S103_BANNER}" || { bad "[103] 横幅缺 gave_up 事件钩子"; S103_BAD=1; }
grep -qF 'invokeLightServiceRestart(api)' "${S103_BANNER}" || { bad "[103] 横幅重启按钮未换轻量命令"; S103_BAD=1; }
grep -qF "await api.invoke('restart_local_services_command');" "${S103_RECOVERY}" || { bad "[103] 统一重启入口未先调轻量命令"; S103_BAD=1; }
grep -q 'identity_probe_classifies_squatter_and_silence' "$(pf_shell_rs_tests)" || { bad "[103] 缺探针分类回归测试"; S103_BAD=1; }
grep -q 'supervisor_streak_state_machine' "$(pf_shell_rs_tests)" || { bad "[103] 缺状态机回归测试"; S103_BAD=1; }
[ -f "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/serviceRecovery.test.js" ] || { bad "[103] 缺 serviceRecovery jest"; S103_BAD=1; }
[ "${S103_BAD}" = "0" ] && ok "[103] 看门狗深探链在位(四分类+双streak+web纳管+横幅自愈)"
}

seg_110() {
# ── seg_110 就绪门 progress-aware 续命(进展指纹/续命/cap 夹钳/判死引用进展/壳脚同步) ──
echo "[${PF_NO}] 就绪门 progress-aware 续命"
S110_BAD=0
S110_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
S110_MAIN="$(pf_shell_rs_prod)"
grep -q '_progress_fingerprint()' "${S110_START}" || { bad "[${PF_NO}] 缺进展指纹函数"; S110_BAD=1; }
grep -q 'sh.ready_extend' "${S110_START}" || { bad "[${PF_NO}] 缺续命账本段"; S110_BAD=1; }
grep -q 'sh.ready_giveup' "${S110_START}" || { bad "[${PF_NO}] 缺判死账本段"; S110_BAD=1; }
grep -q 'HOROSA_READY_PROGRESS_EXTEND' "${S110_START}" || { bad "[${PF_NO}] 缺总开关"; S110_BAD=1; }
grep -q 'HOROSA_READY_TOTAL_CAP_SECS' "${S110_START}" || { bad "[${PF_NO}] 缺总 cap(无限等防线)"; S110_BAD=1; }
# 反锚①:判死分支必须引用 last_progress_epoch(续命被删回硬超时=红)
awk '/-ge "\$\{deadline_epoch\}"/{f=1} f' "${S110_START}" | head -30 | pipe_has 'last_progress_epoch' || { bad "[${PF_NO}] 判死分支未引用 last_progress_epoch(硬超时回潮)"; S110_BAD=1; }
# 反锚②:续命必须被 cap 夹钳(超冲 59s 病零回潮)
grep -q 'cap_epoch=' "${S110_START}" || { bad "[${PF_NO}] 续命缺 cap 夹钳"; S110_BAD=1; }
# 反锚③:指纹函数禁 lsof(慢探针拖死就绪门)
awk '/_progress_fingerprint\(\)/{f=1} f&&/^}$/{exit} f{print}' "${S110_START}" | pipe_has 'lsof' && { bad "[${PF_NO}] 指纹函数混入 lsof"; S110_BAD=1; }
# 壳脚同步:心跳读 ready_extend 段给续命可视文案
grep -q 'sh.ready_extend' "${S110_MAIN}" || { bad "[${PF_NO}] 壳心跳未接续命段(慢机用户会当卡死)"; S110_BAD=1; }
grep -q 'fn start_script_keeps_progress_extend_guard' "$(pf_shell_rs_tests)" || { bad "[${PF_NO}] 缺契约测试"; S110_BAD=1; }
[ "${S110_BAD}" = "0" ] && ok "[${PF_NO}] progress-aware 就绪门在位(指纹/续命/cap 夹钳/判死引用进展/壳脚同步/契约)"
}

seg_111() {
# ── seg_111 探针深化(OOM 转硬死/deep 真算双端 proto2 一致/壳 proto 门代数差免疫) ──
echo "[${PF_NO}] 探针深化(OOM+deep)"
S111_BAD=0
S111_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
S111_MAIN="$(pf_shell_rs_prod)"
S111_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/HorosaIdentityController.java"
S111_PY="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
# ① JVM OOM 旗:走集中变量(三启动分支共用)+ 开关
grep -q 'ExitOnOutOfMemoryError' "${S111_START}" || { bad "[${PF_NO}] 缺 ExitOnOutOfMemoryError(软 OOM 假活盲区回潮)"; S111_BAD=1; }
grep -q 'HOROSA_JAVA_EXIT_ON_OOM' "${S111_START}" || { bad "[${PF_NO}] 缺 OOM 旗开关"; S111_BAD=1; }
# ② 双端 proto 一致升 2(单边升协议=红)+ deep 实现 + dev 注错钩
grep -q '\\"proto\\":2' "${S111_JAVA}" || { bad "[${PF_NO}] Java 身份端 proto 未升 2"; S111_BAD=1; }
grep -q "'proto': 2" "${S111_PY}" || { bad "[${PF_NO}] Python 身份端 proto 未升 2"; S111_BAD=1; }
grep -q 'runDeepProbe' "${S111_JAVA}" || { bad "[${PF_NO}] Java 缺深探真算"; S111_BAD=1; }
grep -q '_identity_deep_ok' "${S111_PY}" || { bad "[${PF_NO}] Python 缺深探真算"; S111_BAD=1; }
grep -q 'HOROSA_IDENTITY_DEEP_FAIL' "${S111_JAVA}" || { bad "[${PF_NO}] Java 缺注错钩"; S111_BAD=1; }
grep -q 'HOROSA_IDENTITY_DEEP_FAIL' "${S111_PY}" || { bad "[${PF_NO}] Python 缺注错钩"; S111_BAD=1; }
# ③ 壳侧:DeepFail/DeepUnsupported 分类 + deep_step + 周期常量 + 开关 + proto 门包裹
grep -q 'DeepFail' "${S111_MAIN}" || { bad "[${PF_NO}] 缺 DeepFail 分类"; S111_BAD=1; }
grep -q 'DeepUnsupported' "${S111_MAIN}" || { bad "[${PF_NO}] 缺 DeepUnsupported(代数差免疫)"; S111_BAD=1; }
grep -q 'fn deep_step' "${S111_MAIN}" || { bad "[${PF_NO}] 缺 deep_step 状态机"; S111_BAD=1; }
grep -q 'SUPERVISOR_DEEP_EVERY_ROUNDS' "${S111_MAIN}" || { bad "[${PF_NO}] 缺深探周期常量"; S111_BAD=1; }
grep -q 'HOROSA_DEEP_PROBE' "${S111_MAIN}" || { bad "[${PF_NO}] 缺深探开关"; S111_BAD=1; }
# 反锚:probe_identity 内 deep 判定必须被 proto 门包裹(proto<2 直通,防误杀旧 runtime)
awk '/^(pub\(crate\) )?fn probe_identity\(/{f=1} f&&/^}$/{exit} f{print}' "${S111_MAIN}" | pipe_has 'proto < 2' || { bad "[${PF_NO}] deep 判定缺 proto 门(新壳×旧 runtime 会被误杀)"; S111_BAD=1; }
# ④ 账本段 + 回归测试
grep -q 'rust.deep_probe_fail' "${S111_MAIN}" || { bad "[${PF_NO}] 缺深探失败账本段"; S111_BAD=1; }
grep -q 'rust.deep_probe_unsupported' "${S111_MAIN}" || { bad "[${PF_NO}] 缺 unsupported 账本段"; S111_BAD=1; }
for t in deep_step_state_machine probe_identity_deep_unsupported_on_proto1 probe_identity_deep_fail_on_proto2 probe_identity_deep_ok_on_proto2; do
  grep -q "fn ${t}" "$(pf_shell_rs_tests)" || { bad "[${PF_NO}] 缺回归测试 ${t}"; S111_BAD=1; }
done
grep -q 'test_horosa_identity_deep_ok' "${REPO_ROOT}/Horosa-Web/astropy/tests/test_horosa_identity.py" || { bad "[${PF_NO}] 缺 Python 深探 pytest"; S111_BAD=1; }
[ "${S111_BAD}" = "0" ] && ok "[${PF_NO}] 探针深化在位(OOM 旗/双端 proto2/deep 真算/proto 门/账本/测试)"
}

seg_112() {
# ── seg_112 观测一致性(状态灯真话/三处重启统一轻量/诊断包收 Java 日志) ──
echo "[${PF_NO}] 观测一致性"
S112_BAD=0
S112_DOT="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/BackendStatusDot.js"
S112_MODAL="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/ChartServiceErrorModal.js"
S112_BANNER="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/ServiceStatusBanner.js"
S112_RECOVERY="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/serviceRecovery.js"
S112_GATE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/StartupGate.js"
S112_MAIN="$(pf_shell_rs_prod)"
# ① 真话灯:状态灯必须走身份握手;反锚 /heartbeat 裸 fetch 零回潮(404/毒200 点绿灯的病)
grep -q 'verifyBackendIdentity' "${S112_DOT}" || { bad "[${PF_NO}] 状态灯未走身份握手"; S112_BAD=1; }
grep -q '/heartbeat' "${S112_DOT}" && { bad "[${PF_NO}] 状态灯回潮 /heartbeat 裸探(主后端无此 HTTP 路由,灯会撒谎)"; S112_BAD=1; }
# ② 三处「重启后端」统一轻量入口(共享 util,禁再内联 trigger_runtime_repair_command 直连)
grep -q 'fn invokeLightServiceRestart\|function invokeLightServiceRestart\|invokeLightServiceRestart' "${S112_RECOVERY}" || { bad "[${PF_NO}] 缺共享轻量重启 util"; S112_BAD=1; }
for f in "${S112_DOT}" "${S112_MODAL}" "${S112_BANNER}"; do
  grep -q 'invokeLightServiceRestart' "${f}" || { bad "[${PF_NO}] $(basename "${f}") 未走统一重启入口"; S112_BAD=1; }
done
# 启动等待页的「重启后端」是第四处:同走统一入口,且不得再直调全量修复(引导在途时会被单飞闸拒、点了没反应)
grep -qF 'const mode = await invokeLightServiceRestart(api);' "${S112_GATE}" || { bad "[${PF_NO}] 启动等待页「重启后端」未走统一重启入口"; S112_BAD=1; }
grep -qF "'trigger_runtime_repair_command'" "${S112_GATE}" && { bad "[${PF_NO}] 启动等待页回潮全量修复直连"; S112_BAD=1; }
[ -f "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/__tests__/startupGateRestart.test.js" ] || { bad "[${PF_NO}] 缺启动等待页重启 jest"; S112_BAD=1; }
grep -q "onClick={() => tauriInvoke('trigger_runtime_repair_command'" "${S112_MODAL}" && { bad "[${PF_NO}] 弹窗回潮全量修复直连"; S112_BAD=1; }
grep -q "invoke('trigger_runtime_repair_command')" "${S112_DOT}" && { bad "[${PF_NO}] 状态灯回潮全量修复直连"; S112_BAD=1; }
# ③ 诊断包收 Java 结构化日志(选取器 + java-logs 目录 + 20MB cap)
grep -q 'fn select_recent_files_by_mtime' "${S112_MAIN}" || { bad "[${PF_NO}] 缺 Java 日志选取器"; S112_BAD=1; }
grep -q '"java-logs"' "${S112_MAIN}" || { bad "[${PF_NO}] 诊断包未收 java-logs"; S112_BAD=1; }
grep -q '.horosa-logs' "${S112_MAIN}" || { bad "[${PF_NO}] 诊断包未指向 log4j2 落点"; S112_BAD=1; }
# ④ 回归测试
grep -q 'fn select_recent_files_prefers_newest_within_cap' "$(pf_shell_rs_tests)" || { bad "[${PF_NO}] 缺选取器测试"; S112_BAD=1; }
grep -q 'invokeLightServiceRestart' "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/serviceRecovery.test.js" || { bad "[${PF_NO}] 缺轻量重启 jest"; S112_BAD=1; }
[ "${S112_BAD}" = "0" ] && ok "[${PF_NO}] 观测一致性在位(真话灯/三处统一轻量/诊断包 java-logs/测试)"
}

seg_113() {
# ── seg_113 运行期资源自感知(磁盘水位闩/权限写测定因/失败上浮) ──
echo "[${PF_NO}] 运行期资源自感知"
S113_BAD=0
S113_MAIN="$(pf_shell_rs_prod)"
S113_BANNER="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/ServiceStatusBanner.js"
grep -q 'fn disk_low_step' "${S113_MAIN}" || { bad "[${PF_NO}] 缺磁盘水位闩纯函数"; S113_BAD=1; }
grep -q 'HOROSA_DISK_WATCH' "${S113_MAIN}" || { bad "[${PF_NO}] 缺磁盘监控开关"; S113_BAD=1; }
grep -q 'HOROSA_DISK_MIN_MB' "${S113_MAIN}" || { bad "[${PF_NO}] 缺阈值参数"; S113_BAD=1; }
grep -q 'rust.disk_low' "${S113_MAIN}" || { bad "[${PF_NO}] 缺磁盘水位账本段"; S113_BAD=1; }
grep -q '"kind": "disk_low"' "${S113_MAIN}" || { bad "[${PF_NO}] 缺 disk_low 事件"; S113_BAD=1; }
grep -q "'disk_low'" "${S113_BANNER}" || { bad "[${PF_NO}] 前端横幅未接 disk_low"; S113_BAD=1; }
# 权限定因:写测函数 + 失败包装(restart 失败必须过定因)+ 账本
grep -q 'fn classify_permission_issue' "${S113_MAIN}" || { bad "[${PF_NO}] 缺权限写测定因"; S113_BAD=1; }
grep -q 'fn restart_local_services_inner' "${S113_MAIN}" || { bad "[${PF_NO}] restart 失败未过定因包装"; S113_BAD=1; }
grep -q 'rust.permission_probe_failed' "${S113_MAIN}" || { bad "[${PF_NO}] 缺权限定因账本段"; S113_BAD=1; }
# 解闩防抖反锚:disk_low_step 内必须有 2× 恢复阈值(防阈值附近抖动刷屏)
awk '/^(pub\(crate\) )?fn disk_low_step\(/{f=1} f&&/^}$/{exit} f{print}' "${S113_MAIN}" | pipe_has 'saturating_mul(2)' || { bad "[${PF_NO}] 缺 2× 解闩防抖"; S113_BAD=1; }
for t in disk_low_step_latch_and_recovery classify_permission_issue_detects_readonly_dir; do
  grep -q "fn ${t}" "$(pf_shell_rs_tests)" || { bad "[${PF_NO}] 缺回归测试 ${t}"; S113_BAD=1; }
done
[ "${S113_BAD}" = "0" ] && ok "[${PF_NO}] 资源自感知在位(水位闩/2×防抖/权限定因/失败上浮/测试×2)"
}

seg_123() {
# ---- [123] 会话投毒防线+全站防白屏+浮层不透明+产物冒烟脚本(根因:request() 吞错 resolve
#      undefined 被缓存层当成功缓存=会话投毒(紫微选项永远选不中/dedupe 同参 10min 无反应);
#      直接 import 技法页无 ErrorBoundary=单组件崩整页白屏;portal 浮层消费容器作用域
#      CSS 变量=断链透明底。四防线全为可执行护栏。) ----
S123_BAD=0
S123_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
echo "[123] 会话投毒/防白屏/浮层不透明/产物冒烟"
grep -q "响应为空" "${S123_UI}/src/services/rules.js" 2>/dev/null || { bad "[123] rules.js 缺空载荷剔缓存防线(会话投毒回潮)"; S123_BAD=1; }
grep -q "吞错型失败" "${S123_UI}/src/utils/__tests__/ziweiRulesCache.test.js" 2>/dev/null || { bad "[123] 缺 rules 投毒回归测试"; S123_BAD=1; }
# 判据收成单源 resultEnvelope.responseCacheable(空载荷 + 业务错误都不入缓存),去重层经它判
grep -qF '!responseCacheable(v)' "${S123_UI}/src/utils/requestDedupe.js" 2>/dev/null \
  && grep -qF 'rsp !== undefined && rsp !== null' "${S123_UI}/src/utils/resultEnvelope.js" 2>/dev/null \
  || { bad "[123] requestDedupe 缺空载荷防线(10min 投毒回潮;应经 resultEnvelope.responseCacheable 判)"; S123_BAD=1; }
grep -q "吞错型失败" "${S123_UI}/src/utils/__tests__/requestDedupe.test.js" 2>/dev/null || { bad "[123] 缺 dedupe 投毒回归测试"; S123_BAD=1; }
grep -q "TechniqueErrorBoundary" "${S123_UI}/src/components/comp/FreezeInactive.js" 2>/dev/null || { bad "[123] FreezeInactive 未集成 ErrorBoundary(直接 import 技法页白屏回潮)"; S123_BAD=1; }
[ -f "${S123_UI}/src/components/comp/__tests__/freezeInactiveBoundary.test.js" ] || { bad "[123] 缺防白屏接线测试"; S123_BAD=1; }
grep -q "horosa-floating-surface" "$(pf_src_set "${S123_UI}/src/layouts/app.less")" 2>/dev/null || { bad "[123] app.less 缺 floating-surface 基类"; S123_BAD=1; }
awk '/\.horosa-guolao-moira-tooltip \{/,/^\}/' "${S123_UI}/src/components/guolao/GuoLaoMoiraWheel.less" 2>/dev/null | pipe_has -- "--moira-tooltip-bg" || { bad "[123] moira tooltip 变量未自带(portal 断链透明回潮)"; S123_BAD=1; }
grep -q -- "--horosa-surface-solid" "${S123_UI}/src/utils/helper.js" 2>/dev/null || { bad "[123] setupFloatingTooltip 背景未用 surface-solid(浮层微透明回潮)"; S123_BAD=1; }
[ -x "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_packaged_frontend.sh" ] || { bad "[123] 缺 verify_packaged_frontend.sh(打包产物冒烟制度)"; S123_BAD=1; }
# ⑤b 构建指纹的「前端源面」三处必须同读单源清单(构建时判脏 / [122] / 产物冒烟),不许各写各的;产物冒烟脚本判据自证通过
for S123_C in "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_packaged_frontend.sh" "${REPO_ROOT}/Horosa-Web/astrostudyui/scripts/write-build-info.js"; do
  grep -qF "fe-source-paths.txt" "${S123_C}" 2>/dev/null || { bad "[123] ${S123_C##*/} 没有读单源清单 fe-source-paths.txt(前端源面各写各的 = 迟早漂移)"; S123_BAD=1; }
done
grep -aE "git status --porcelain -- \.\./src|FE_SRC_PATHS=\"Horosa-Web/astrostudyui/src " "${REPO_ROOT}/Horosa-Web/astrostudyui/scripts/write-build-info.js" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_packaged_frontend.sh" >/dev/null 2>&1 \
  && { bad "[123] 构建指纹消费方里又出现写死的前端源面清单(必须读 fe-source-paths.txt)"; S123_BAD=1; }
bash "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_packaged_frontend.sh" --self-test >/dev/null 2>&1 || { bad "[123] 产物冒烟脚本判据自证未过(verify_packaged_frontend.sh --self-test)"; S123_BAD=1; }
[ "${S123_BAD}" = "0" ] && ok "[123] 投毒防线×2+防白屏接线+浮层不透明+产物冒烟脚本 全在位"
}

seg_181() {
echo "[181] 重引擎按需加载锁(页面不得静态引 3D/图表引擎)"
# 病灶(2026-08-01 用户实报「进入星运台卡死」):页面组件**静态** import 了重可视化组件,
# webpack 遂把整个引擎变成该页 chunk 的**同步依赖** —— 用户只要进这个页,模块求值期就得先
# 解析完整个引擎,哪怕他从不打开那个 3D 子页签。实报那次星运页静态引 AstroPDSphere→
# PDSphereEngine→three(vendors-gl 862KB+引擎 90KB),而该页默认停在「主限法」表格、
# 二十多个子页签里只有一个用得着 3D;配置一般的机器足以让主线程长时间无响应。同族共三处
# (星运/节气/玄史),玄史那处引的是 echarts(1291KB,比 three 还大)。
# 四道判据:单一真值源在位 → 三处接线正确 → 主锁测试在位 → **直接扫产物**(不信源码,只认产物)。
S181_BAD=0
S181_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
# ① 懒边界单一真值源(空模块自愈住这里 —— 组件内各写一份必然丢掉它,那是 v3.6.0 的坑)
S181_LB="${S181_UI}/src/utils/lazyBoundary.js"
if [ ! -f "${S181_LB}" ]; then
  S181_BAD=1; bad "[181] 缺懒边界单一真值源 utils/lazyBoundary.js"
else
  grep -aq "export function makeLazyBoundary" "${S181_LB}" || { S181_BAD=1; bad "[181] lazyBoundary 未导出 makeLazyBoundary"; }
  grep -aq "Lazy chunk resolved empty" "${S181_LB}" || { S181_BAD=1; bad "[181] lazyBoundary 丢了空模块自愈(坏结果进 React.lazy 缓存会被永久钉死)"; }
fi
# ② 三处宿主页不得静态 import 重组件(剥注释后再判 —— 注释里提到不算)
S181_CHECK(){   # $1=文件 $2=被禁的静态 import 正则 $3=人话
  local F="${S181_UI}/src/components/$1"
  [ -f "${F}" ] || { S181_BAD=1; bad "[181] 缺文件 $1"; return; }
  local CODE; CODE=$(sed -E 's://.*$::' "${F}" 2>/dev/null)
  if printf '%s' "${CODE}" | pipe_has -E "$2"; then
    S181_BAD=1; bad "[181] $3 —— 静态 import 会把引擎拖回本页 chunk,进该页即须解析整个引擎"
  fi
}
S181_CHECK "direction/AstroDirectMain.js"   "^import AstroPDSphere from"    "星运页又静态引了主限天球"
S181_CHECK "jieqi/JieQiChartsMain.js"       "^import AstroChartMain3D from" "节气页又静态引了 3D 盘"
S181_CHECK "xuanshi/XuanShiMain.js"         "^import (XuanShiCelestial|XuanShiMap) from" "玄史页又静态引了 echarts 宿主"
S181_CHECK "astro3d/AstroChartMain3D.js"    "^import AstroPDSphere from"    "3D 星盘页又静态引了主限天球(那条分支恒 false,纯拖累)"
# ③ 主锁(AST import 图遍历)在位 —— 它才是覆盖「未来任意新增页面」的那一道
[ -f "${S181_UI}/src/utils/__tests__/heavyEngineImportGraph.test.js" ] \
  || { S181_BAD=1; bad "[181] 缺主锁 heavyEngineImportGraph.test.js(AST 图遍历,自动覆盖新增页面)"; }
grep -aq "重引擎不得与页面同 chunk" "${S181_UI}/scripts/check-chunk-dup.js" 2>/dev/null \
  || { S181_BAD=1; bad "[181] check-chunk-dup 缺产物层判据(锁 C)"; }
# ④ 终判据:直接扫产物 —— 任何 async chunk 不得同时含引擎标记与页面懒边界
#    (vendors 前缀是引擎独占 chunk,本就该含引擎,豁免)
for S181_D in dist dist-file; do
  [ -d "${S181_UI}/${S181_D}" ] || continue
  for S181_F in "${S181_UI}/${S181_D}"/*.async.js; do
    [ -f "${S181_F}" ] || continue
    case "$(basename "${S181_F}")" in vendors-*|vendors~*) continue ;; esac
    if grep -aq "WebGLRenderer" "${S181_F}" 2>/dev/null && grep -aq "LazyBoundary" "${S181_F}" 2>/dev/null; then
      S181_BAD=1; bad "[181] ${S181_D}/$(basename "${S181_F}") 同时含 three 与页面懒边界 —— 引擎被拖进页面 chunk"
    fi
  done
done
# ⑤ 首屏批次判据:引擎不得与「基础设施库」编在同一个 cacheGroup
#    ④ 只查「引擎与页面同 chunk」,查不到这条隐形通道:引擎跟一个首屏必需的基础设施库
#    (d3——星盘 SVG 绘制用,全仓 101 个文件在用)共处同一个 vendors chunk → 首屏把整包
#    拉走,引擎虽规规矩矩待在 vendors 里(④ 全绿)、页面也确实懒加载了(①②③ 全绿),
#    用户照样开机就得下载解析它。实锤:原 vendors-viz 1228KB 含 echarts,在首屏批次里。
#    拆成 vendors-d3(129KB 首屏)+ vendors-echarts(1132KB 只随玄史两子页)后首屏净省 1.1MB。
grep -aq "vendorsD3" "${S181_UI}/.umirc.js" 2>/dev/null \
  && grep -aq "name: 'vendors-echarts'" "${S181_UI}/.umirc.js" 2>/dev/null \
  || { S181_BAD=1; bad "[181] .umirc.js 的 echarts 与 d3 未分组 —— 图表引擎会被首屏必需的 d3 捎带下载,玄史页懒加载等于白做"; }
grep -aq "首屏批次不得含重引擎" "${S181_UI}/scripts/check-chunk-dup.js" 2>/dev/null \
  || { S181_BAD=1; bad "[181] check-chunk-dup 缺首屏批次判据(锁 E)"; }
#    终判据同样只认产物,但**不在这里重写一遍**:minify 后是单行巨串,shell 正则解析
#    极易错配成虚绿(本条初版就栽在这)。直接跑 check-chunk-dup.js 本体 —— 它已就
#    「首屏批次无引擎」做过正反双验(病态配置下 exit 1 实测),复用比重写可靠。
if command -v node >/dev/null 2>&1; then
  for S181_D in dist dist-file; do
    [ -d "${S181_UI}/${S181_D}" ] || continue
    S181_OUT="$(cd "${S181_UI}" && node scripts/check-chunk-dup.js "${S181_D}" 2>&1)" || {
      S181_BAD=1; bad "[181] ${S181_D}: check-chunk-dup 未过 —— $(printf '%s' "${S181_OUT}" | head -2 | tr '\n' ' ')"
    }
    printf '%s' "${S181_OUT}" | pipe_has "首屏批次\[" \
      || { S181_BAD=1; bad "[181] ${S181_D}: check-chunk-dup 没打出首屏批次 —— 该判据未真正执行(拒绝虚绿)"; }
  done
else
  S181_BAD=1; bad "[181] 找不到 node,首屏批次判据无法执行 —— 判据失效即红,不许静默放行"
fi
[ "${S181_BAD}" = "0" ] && ok "[181] 重引擎按需加载锁全绿(单源在位·四处接线·主锁与产物锁在位·产物零同居·首屏批次无引擎)"
}

seg_187() {
# ── [187] R4-B1 预取底座:运行时白名单闸+连点泵保底+组式数据预热+L1 真 LRU ──
# 病史:①白名单只是注释+jest 快照,运行时零拦截,且裸 '/pan' 条目匹配不到任何真实路径;
# ②连点时预取泵被「丢旧代耗整拍+rIC 长 timeout」饿死(实测 20 连点 0 派发);
# ③registerIdleWarmTask 启动瞬间快照一次,启动后登记永不执行(注册表空转);
# ④dedupe L1 是 FIFO 冒充 LRU(热条目被预取挤出,预取自己活着)。
# 本哨兵锁四件资产 + Mac 政策修正点(taixuan=seedInBody 绝不入预取白名单——Windows 版此处是漏洞)。
echo "== [187] R4-B1 预取底座(白名单闸+泵保底+组式预热+L1 LRU) =="
S187_BAD=0
S187_SP="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/stepPrefetch.js"
S187_REQ="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/request.js"
S187_CF="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/chartFetch.js"
S187_IWQ="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/idleWarmQueue.js"
S187_RD="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/requestDedupe.js"
S187_TEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/stepPrefetch.test.js"
grep -aq "export function guardPrefetchUrl(url){" "${S187_SP}" 2>/dev/null || { bad "[187] 🔴 运行时白名单闸函数缺失(guardPrefetchUrl)"; S187_BAD=1; }
grep -aq "'/qimen/pan'," "${S187_SP}" 2>/dev/null || { bad "[187] 🔴 kentang 逐条枚举缺失(白名单塌回通配即随机起卦可被预取)"; S187_BAD=1; }
grep -aqE "^	'/pan'," "${S187_SP}" 2>/dev/null && { bad "[187] 🔴 裸 '/pan' 条目回潮(形同虚设的假白名单)"; S187_BAD=1; }
grep -aq "'/taixuan/pan'" "${S187_SP}" 2>/dev/null && { bad "[187] 🔴 taixuan(seedInBody 蓍法种子)混入预取白名单——预取即钉死起课"; S187_BAD=1; }
grep -aq "'taixuan'," "${S187_SP}" 2>/dev/null || { bad "[187] 🔴 FORBIDDEN 缺 taixuan 禁词"; S187_BAD=1; }
grep -aq "guardPrefetchUrl(url)" "${S187_REQ}" 2>/dev/null || { bad "[187] 🔴 request.js 纵深闸未接线"; S187_BAD=1; }
grep -aq "guardPrefetchUrl(url)" "${S187_CF}" 2>/dev/null || { bad "[187] 🔴 chartFetch.js 纵深闸未接线(kentang 族裸 fetch 不经 request)"; S187_BAD=1; }
grep -aq "horosa_prefetch_pump_livelock_v1" "${S187_SP}" 2>/dev/null || { bad "[187] 🔴 连点泵保底改造缺失(20 连点将回到 0 派发)"; S187_BAD=1; }
grep -aq "export function scheduleDataWarmGroup(generationKey, tasks){" "${S187_IWQ}" 2>/dev/null || { bad "[187] 🔴 组式数据预热调度缺失(scheduleDataWarmGroup)"; S187_BAD=1; }
grep -aq "horosa_dedupe_l1_lru_v1" "${S187_RD}" 2>/dev/null || { bad "[187] 🔴 dedupe L1 真 LRU 命中重插缺失(FIFO 会把热条目挤给预取)"; S187_BAD=1; }
grep -aq "连点泵保底:20 次连点" "${S187_TEST}" 2>/dev/null || { bad "[187] 🔴 连点保底金标缺失(≥15/20 硬指标失守)"; S187_BAD=1; }
grep -aq "kentang 枚举 ≡ 政策表" "${S187_TEST}" 2>/dev/null || { bad "[187] 🔴 白名单↔政策表单一真值源对拍测试缺失"; S187_BAD=1; }
pf_test_disabled "${S187_TEST}" && { bad "[187] 🔴 stepPrefetch 测试被 skip / only 旁路"; S187_BAD=1; }
[ "${S187_BAD}" = "0" ] && ok "[187] R4-B1 预取底座(白名单闸+泵保底+组式预热+L1 LRU+政策修正)全在位"
}

seg_188() {
# ── [188] R4-B2 武装引擎:四时机武装+技法登记表复活+紫微空烧止血 ──
# 病史:①「选完步长第一下卡」——预取单位只来自上次步进 hint,选新档第一下必 miss;
# ②registerStepPrefetcher 注册表零组件登记(死表),且旧 builder 把【基准 fields】传给登记方
# (构出「此刻」参数,预取白打——死表期潜伏未爆);③紫微 chartFree 页选步长走全局 handler
# 空烧 4 个 /chart。武装=四时机(unit-select/settle 兜底/local-settle/tab-activate)按当前
# 档位 ±depth 预好;NO_ARM 含 zeri(Mac 差异化:择日 fields 自持+找局纯本地,全局武装错轴)。
echo "== [188] R4-B2 武装引擎(四时机+登记表+紫微止血) =="
S188_BAD=0
S188_ARM="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/stepPrefetchArm.js"
S188_AST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/models/astro.js"
S188_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
[ -f "${S188_ARM}" ] || { bad "[188] 🔴 武装引擎文件缺失(stepPrefetchArm.js)"; S188_BAD=1; }
grep -aq "'zeri'," "${S188_ARM}" 2>/dev/null || { bad "[188] 🔴 NO_ARM_TABS 缺 zeri(择日 fields 自持,全局武装=错轴白打)"; S188_BAD=1; }
grep -aq "'guazhan', 'planetarium', 'aianalysis'" "${S188_ARM}" 2>/dev/null || { bad "[188] 🔴 NO_ARM_TABS 随机/取现时/流式三禁缺失"; S188_BAD=1; }
grep -aq "registerArmPlanBuilder((fieldValues, hint, astroState)=>buildStepPrefetchTasks" "${S188_AST}" 2>/dev/null || { bad "[188] 🔴 构造器注入缺失(武装线拿不到 builder=全线哑火)"; S188_BAD=1; }
grep -aq "const more = extra(f2, stepHint);" "${S188_AST}" 2>/dev/null || { bad "[188] 🔴 f2 修正回退(登记方又拿基准 fields=预取白打)"; S188_BAD=1; }
S188_SETTLE=$(grep -ac "currentStepUnit(astroState.currentTab)" "${S188_AST}" 2>/dev/null)
S188_SETTLE=${S188_SETTLE:-0}
[ "${S188_SETTLE}" -ge 2 ] || { bad "[188] 🔴 settle 兜底武装不足(快车道+常规两分支须各一,现 ${S188_SETTLE})"; S188_BAD=1; }
S188_REG=$(pf_prod_hits -a "registerStepPrefetcher('" "${S188_UI}/src/components" | wc -l | tr -d ' ')
[ "${S188_REG}" -ge 4 ] || { bad "[188] 🔴 技法登记组件数不足(需≥4:ziwei/dunjia/taiyi/liureng,现 ${S188_REG})"; S188_BAD=1; }
S188_UNREG=$(pf_prod_hits -a "unregisterStepPrefetcher('" "${S188_UI}/src/components" | wc -l | tr -d ' ')
[ "${S188_UNREG}" -ge 4 ] || { bad "[188] 🔴 反注册配对不足(卸载后闭包吃死组件态,现 ${S188_UNREG})"; S188_BAD=1; }
grep -aq "armStepPrefetch('unit-select', { unit, skipChart: true })" "${S188_UI}/src/components/ziwei/ZiWeiInput.js" 2>/dev/null || { bad "[188] 🔴 紫微选步长止血缺失(chartFree 页又空烧 /chart)"; S188_BAD=1; }
grep -aq "armStepPrefetch('tab-activate'" "${S188_UI}/src/pages/index.js" 2>/dev/null || { bad "[188] 🔴 切页武装时机缺失(进页第一下步进恒冷)"; S188_BAD=1; }
grep -aq "armStepPrefetch('local-settle', { fieldsOverride: fields, skipChart: true })" "${S188_UI}/src/components/ziwei/ZiWeiMain.js" 2>/dev/null || { bad "[188] 🔴 紫微本地漏斗 settle 武装缺失"; S188_BAD=1; }
[ "${S188_BAD}" = "0" ] && ok "[188] R4-B2 武装引擎(四时机+登记 ${S188_REG} 件+f2 修正+紫微止血)全在位"
}

seg_189() {
# ── [189] R4 B3-B6/P1-P3a 综合资产锚(数据预热/三段链/错轴止血/缓存补全/静态供给/门观察位) ──
# 一段多锚:各批已由独立 commit+测试验收,此处锁「资产在位性」防未来无意识拆除;
# 逐行一罪,任一缺位即红。详细病史见各 perf(R4-*) commit 信息。
echo "== [189] R4 B3-B6/P1-P3a 综合资产锚 =="
S189_BAD=0
S189_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S189_DWT="${S189_UI}/src/utils/dataWarmTasks.js"
S189_OPT="${S189_UI}/src/utils/optionPrefetch.js"
S189_MAIN_RS="$(pf_shell_rs_prod)"
S189_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
S189_PYSRV="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
# B3:数据预热注册表(登记≥4)+pages 接线+七政三段链
S189_NWARM=$(grep -ac "^registerDataWarmTask('" "${S189_DWT}" 2>/dev/null); S189_NWARM=${S189_NWARM:-0}
[ "${S189_NWARM}" -ge 4 ] || { bad "[189] 🔴 dataWarmTasks 登记数不足(需≥4,现 ${S189_NWARM})"; S189_BAD=1; }
grep -aq "registry.buildDataWarmTasks(warmFields, warmChartObj)" "${S189_UI}/src/pages/index.js" 2>/dev/null || { bad "[189] 🔴 pages 数据预热接线缺失(注册表空转回潮)"; S189_BAD=1; }
S189_RULES=$(grep -ac "fetchMoiraQizhengRules({" "$(pf_src_set "${S189_UI}/src/components/guolao/GuoLaoChartMain.js")" 2>/dev/null); S189_RULES=${S189_RULES:-0}
[ "${S189_RULES}" -ge 3 ] || { bad "[189] 🔴 七政规则段调用不足(主链两路+预取链一处须≥3,现 ${S189_RULES}——三段链的第三段被拆即步进回到每步必付)"; S189_BAD=1; }
grep -aq "warmAllStages = transitTime !== null" "$(pf_src_set "${S189_UI}/src/components/guolao/GuoLaoChartMain.js")" 2>/dev/null || { bad "[189] 🔴 七政取现时红线守卫缺失(默认「现在」态后两段白打)"; S189_BAD=1; }
# B4:PD 正轴预取+错轴止血
grep -aq "prefetchPdStepSelect(unit){" "${S189_UI}/src/components/astro/AstroPrimaryDirectionChart.js" 2>/dev/null || { bad "[189] 🔴 主限法正轴预取器缺失"; S189_BAD=1; }
grep -aq "path: '/predict/pdchart'," "${S189_UI}/src/components/astro/AstroPrimaryDirectionChart.js" 2>/dev/null || { bad "[189] 🔴 PD 预取任务 path 契约缺失"; S189_BAD=1; }
grep -aq "R4-B4 错轴止血" "${S189_UI}/src/components/astro/AstroPersianDirected.js" 2>/dev/null || { bad "[189] 🔴 波斯向运错轴止血被拆(选步长回到空烧 natal /chart)"; S189_BAD=1; }
# B6:dedupe 精确条目+chartMem validOnly
grep -aq "'/bazi/birth'," "${S189_UI}/src/utils/requestDedupe.js" 2>/dev/null || { bad "[189] 🔴 dedupe 缺 /bazi/birth 精确条目"; S189_BAD=1; }
grep -aqE "^	'/bazi/'," "${S189_UI}/src/utils/requestDedupe.js" 2>/dev/null && { bad "[189] 🔴 /bazi/ 整前缀回潮(族内有写端点 pattern/update)"; S189_BAD=1; }
grep -aq "chartMem_valid_only_v1" "${S189_UI}/src/services/astro.js" 2>/dev/null || { bad "[189] 🔴 chartMem validOnly 被拆(错误信封会进缓存)"; S189_BAD=1; }
# B5a:FE-18+optionPrefetch
grep -aq "horosa_change_cond_no_mutate_v1" "${S189_UI}/src/pages/index.js" 2>/dev/null || { bad "[189] 🔴 changeCond 就地变异根治被拆(渲染 memo 全部白加)"; S189_BAD=1; }
S189_AXES=$(grep -ac "	{ key: '" "${S189_OPT}" 2>/dev/null); S189_AXES=${S189_AXES:-0}
[ "${S189_AXES}" = "4" ] || { bad "[189] 🔴 BINARY_CHART_AXES 非恰四轴(现 ${S189_AXES};多值轴须组件登记不许 util 臆造)"; S189_BAD=1; }
S189_SPEC=$(grep -ac "speculateChartOptions(fieldValues, astroState);" "${S189_UI}/src/models/astro.js" 2>/dev/null); S189_SPEC=${S189_SPEC:-0}
[ "${S189_SPEC}" -ge 2 ] || { bad "[189] 🔴 选项投机 settle 接线不足(快车道+常规两分支须各一,现 ${S189_SPEC})"; S189_BAD=1; }
# P1cd:preload 六前缀+对拍⑤段
grep -aq "'shared-technique', 'vendors-d3'" "${S189_UI}/scripts/inject-preload.js" 2>/dev/null || { bad "[189] 🔴 preload 清单缺 shared-technique/vendors-d3(首屏最大件回到串行瀑布)"; S189_BAD=1; }
grep -aq "check-chunk-dup ⑤" "${S189_UI}/scripts/check-chunk-dup.js" 2>/dev/null || { bad "[189] 🔴 preload↔首屏批次对拍⑤段缺失(清单漂移无人看守)"; S189_BAD=1; }
# P2c:latch 终确认+listen 观察位
grep -aq "sh.java_listen_ready" "${S189_START}" 2>/dev/null || { bad "[189] 🔴 sh.java_listen_ready 观察位缺失(P4-3 裁决数据断供)"; S189_BAD=1; }
grep -aq "HOROSA_READY_PROBE_LATCH" "${S189_START}" 2>/dev/null || { bad "[189] 🔴 就绪探测 latch 合并被拆(每轮回到 4 次 curl fork)"; S189_BAD=1; }
# P3a:PD 并行组+门观察位
grep -aq "HOROSA_PY_PD_PARALLEL" "${S189_PYSRV}" 2>/dev/null || { bad "[189] 🔴 PD 并行组开关缺失"; S189_BAD=1; }
grep -aq "ledger_mark('py.gate_open'" "${S189_PYSRV}" 2>/dev/null || { bad "[189] 🔴 py.gate_open 观察位缺失"; S189_BAD=1; }
grep -aq "py.gate_first_wait" "${S189_PYSRV}" 2>/dev/null || { bad "[189] 🔴 py.gate_first_wait 观察位缺失(P3-b 分级门裁决数据断供)"; S189_BAD=1; }
# P1ab+P2ab:Rust 静态供给+串行点
grep -aq "HOROSA_STATIC_POOL" "${S189_MAIN_RS}" 2>/dev/null || { bad "[189] 🔴 静态服务器线程池被拆(首屏回到单线程串行供给)"; S189_BAD=1; }
grep -aq "fn respond_static_from_ram(" "${S189_MAIN_RS}" 2>/dev/null || { bad "[189] 🔴 静态 RAM 缓存应答缺失"; S189_BAD=1; }
grep -aq "fn make_static_etag(" "${S189_MAIN_RS}" 2>/dev/null || { bad "[189] 🔴 ETag 公式单源定义缺失(fn make_static_etag)"; S189_BAD=1; }
S189_ETAG=$(grep -ac "make_static_etag(" "${S189_MAIN_RS}" 2>/dev/null); S189_ETAG=${S189_ETAG:-0}
[ "${S189_ETAG}" -ge 4 ] || { bad "[189] 🔴 ETag 公式单源共用不足(定义+RAM 两处+磁盘一处须≥4,现 ${S189_ETAG}——两路分叉即 304 连续性破)"; S189_BAD=1; }
grep -aq "rust.prestop_done" "${S189_MAIN_RS}" 2>/dev/null || { bad "[189] 🔴 stop 预检账本位缺失"; S189_BAD=1; }
grep -aq "HOROSA_PRUNE_LOGS_ASYNC" "${S189_MAIN_RS}" 2>/dev/null || { bad "[189] 🔴 日志清扫后台化被拆"; S189_BAD=1; }
[ "${S189_BAD}" = "0" ] && ok "[189] R4 B3-B6/P1-P3a 综合资产(预热 ${S189_NWARM} 条+三段链+止血+精确缓存+preload 对拍+门观察位+静态池/RAM)全在位"
}

seg_191() {
# ── [191] R4-B5b 选项防抖+主链 Abort 资产锚 ──
echo "== [191] R4-B5b 选项防抖+主链 Abort 资产锚 =="
S191_BAD=0
S191_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
# 选项通道:调度器在位+delta/fresh-base 形态+接线
grep -aq "horosa_option_debounce_v1" "${S191_UI}/src/utils/optionDispatchScheduler.js" 2>/dev/null || { bad "[191] 🔴 optionDispatchScheduler 缺失"; S191_BAD=1; }
grep -aq "pendingDelta = { ...(pendingDelta || {}), ...(delta || {}) };" "${S191_UI}/src/utils/optionDispatchScheduler.js" 2>/dev/null || { bad "[191] 🔴 delta 累积被拆(trailing 只发末次快照=陈旧时间键覆盖时间轴在途变更)"; S191_BAD=1; }
grep -aq "scheduleOptionDispatch((payload)=>{" "${S191_UI}/src/components/astro/ChartDisplaySelector.js" 2>/dev/null || { bad "[191] 🔴 古典参数选项通道接线缺失(连拨回到逐发全算)"; S191_BAD=1; }
# 主链 Abort 三防线:models 挂载+request 短路序+services 共享隔离
grep -aq "chartMainAbortCtl = new AbortController();" "${S191_UI}/src/models/astro.js" 2>/dev/null || { bad "[191] 🔴 主链 AbortController 挂载缺失"; S191_BAD=1; }
S191_GUARD=$(grep -ac "options.signal && options.signal.aborted" "${S191_UI}/src/utils/request.js" 2>/dev/null); S191_GUARD=${S191_GUARD:-0}
[ "${S191_GUARD}" -ge 2 ] || { bad "[191] 🔴 request 层 abort 短路不足两路(requestCore+requestRaw 须各一,现 ${S191_GUARD}——缺者 abort 触发身份再协商)"; S191_BAD=1; }
grep -aq "const shareKey = opts.signal ? '' : key;" "${S191_UI}/src/services/astro.js" 2>/dev/null || { bad "[191] 🔴 chartInflight signal 隔离被拆(A abort 连坐同参搭车 B)"; S191_BAD=1; }
grep -aq "err.name === 'TimeoutError' || err.name === 'AbortError'" "${S191_UI}/src/utils/serviceStatus.js" 2>/dev/null || { bad "[191] 🔴 AbortError 离线白名单被拆(abort 弹离线横幅/触发重试)"; S191_BAD=1; }
[ "${S191_BAD}" = "0" ] && ok "[191] R4-B5b 资产(选项通道 delta+fresh base/Abort 三防线 ${S191_GUARD} 路短路)全在位"
}

seg_199() {
# ── [199] CDS 两处训练端点清单 lockstep(打包预训 ↔ 用户侧自训) ──
# 病史:两处清单各自演化=预置 .jsa 与自训 .jsa 类面分叉,增量后回退自训档时首交互链覆盖骤缩。
echo "== [199] CDS 训练端点清单 lockstep =="
S199_A=$(grep -a 'for _cds_ep in ' "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh" 2>/dev/null | head -1 | sed 's/^[[:space:]]*//')
S199_B=$(grep -a 'for _cds_ep in ' "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" 2>/dev/null | head -1 | sed 's/^[[:space:]]*//')
if [ -z "${S199_A}" ] || [ -z "${S199_B}" ]; then
	bad "[199] 🔴 CDS 训练端点循环缺失(打包侧='${S199_A}' 自训侧='${S199_B}')"
elif [ "${S199_A}" != "${S199_B}" ]; then
	bad "[199] 🔴 两处 CDS 训练清单分叉——打包预训与用户侧自训类面不一致:打包=${S199_A} 自训=${S199_B}"
else
	if echo "${S199_A}" | pipe_has '"/rules/ziwei"'; then
		ok "[199] CDS 两处训练清单逐字一致(含 /rules/ziwei)"
	else
		bad "[199] 🔴 训练清单缺 /rules/ziwei(R4-P4-2 扩容被拆)"
	fi
fi
}

seg_192() {
# ── [192] 三式连续进退流畅度四资产(丢击根治/不等回流/快照idle/三pan预取+蒙层撤) ──
# 病史:用户实告「连续进退卡很久」——实测三因叠加:①loading 期点击被 clickPlot 静默丢弃
# ②每步硬等 /chart 回流的 1200ms 兜底 timer(回流常缺席=步步吃满)③快照 ~950ms 同步大构建
# 恰插进下一步 recalc timer 之前顶住。另:全屏 Spin 蒙层挡盘(用户圈报)。
echo "== [192] 三式连续进退流畅度四资产 =="
S192_BAD=0
S192_F="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js"
for S192_M in horosa_sanshi_no_drop_step_v1 horosa_sanshi_no_wait_chart_v1 horosa_sanshi_snapshot_idle_v1 horosa_sanshi_step_prefetch_v1; do
	grep -aq "${S192_M}" "${S192_F}" 2>/dev/null || { bad "[192] 🔴 资产标记缺失:${S192_M}"; S192_BAD=1; }
done
grep -aq "registerStepPrefetcher('sanshiunited'" "${S192_F}" 2>/dev/null || { bad "[192] 🔴 三式步进预取登记缺失(连击回到每步真发 HTTP)"; S192_BAD=1; }
grep -aq "unregisterStepPrefetcher('sanshiunited'" "${S192_F}" 2>/dev/null || { bad "[192] 🔴 预取反注册缺失(卸载后登记表泄漏)"; S192_BAD=1; }
grep -aqE "awaitingSyncTimer = setTimeout\(" "${S192_F}" 2>/dev/null && { bad "[192] 🔴 1200ms 兜底 timer 回潮(每步硬等回流)"; S192_BAD=1; }
grep -aq "horosa-workspace-updating horosa-sanshi-updating" "${S192_F}" 2>/dev/null || { bad "[192] 🔴 中栏小加载徽标缺失(或 Spin 蒙层回潮)"; S192_BAD=1; }
grep -aq "sanshiStepFluency" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/sanshi/__tests__/sanshiStepFluency.test.js" 2>/dev/null || { bad "[192] 🔴 流畅度金标文件缺失"; S192_BAD=1; }
[ "${S192_BAD}" = "0" ] && ok "[192] 三式连续进退四资产(四标记+登记配对+兜底负锚+徽标+金标)全在位"
}

seg_194() {
# ── [194] 时间即时传导 + 择日空闲预挂载 ──────────────────────────────────────
# 用户定版语义:未起盘=改时间只落草稿(首盘必须显式起盘);已起盘=改时间即刻重算中栏右栏。
# 旧病:onTimeChanged 只认 confirmed(Popover 改年月日时分秒带 false)⇒「时间改了盘不动」。
echo "== [194] 时间即时传导 + 择日空闲预挂载 =="
S194_BAD=0
S194_SS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js"
S194_DJ="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js"
S194_ZR="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/zeri/ZeriMain.js"
S194_T="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/sanshi/__tests__/liveTimePropagation.test.js"
grep -aq "horosa_live_time_propagation_v1" "${S194_SS}" 2>/dev/null || { bad "[194] 🔴 三式时间传导资产标记缺失"; S194_BAD=1; }
grep -aq "const liveReplot = !confirmed && !!this.state.hasPlotted;" "${S194_SS}" 2>/dev/null || { bad "[194] 🔴 三式 liveReplot 判据缺失(改时间盘不动会复发)"; S194_BAD=1; }
grep -aq "horosa_live_time_propagation_v1" "${S194_DJ}" 2>/dev/null || { bad "[194] 🔴 遁甲时间传导资产标记缺失"; S194_BAD=1; }
grep -aqE "if\(this\.state\.hasPlotted\)\{[[:space:]]*$" "${S194_DJ}" 2>/dev/null || grep -aq "this.requestNongli(localFields, true);" "${S194_DJ}" 2>/dev/null || { bad "[194] 🔴 遁甲已起盘重算接线缺失"; S194_BAD=1; }
# 反向锚:首盘显式门不得被抹掉(否则未起盘也自动出盘,违用户定版)
grep -aq "点击左侧“起盘”后显示三式合一盘" "${S194_SS}" 2>/dev/null || { bad "[194] 🔴 三式未起盘提示缺失(首盘显式门被抹)"; S194_BAD=1; }
grep -aq "点击左侧“起盘”后显示遁甲盘" "${S194_DJ}" 2>/dev/null || { bad "[194] 🔴 遁甲未起盘提示缺失(首盘显式门被抹)"; S194_BAD=1; }
# 择日空闲预挂载
grep -aq "horosa_zeri_idle_prerender_v1" "${S194_ZR}" 2>/dev/null || { bad "[194] 🔴 择日空闲预挂载资产标记缺失"; S194_BAD=1; }
grep -aq "forceRender={this.state.prerenderQimenZeri}" "${S194_ZR}" 2>/dev/null || { bad "[194] 🔴 择日 forceRender 未接线(首次点击回到冷态建树)"; S194_BAD=1; }
grep -aq "horosa.perf.zeriPrerender" "${S194_ZR}" 2>/dev/null || { bad "[194] 🔴 择日预挂载 kill-switch 缺失"; S194_BAD=1; }
[ -f "${S194_T}" ] || { bad "[194] 🔴 时间传导金标缺失"; S194_BAD=1; }
[ "${S194_BAD}" = "0" ] && ok "[194] 时间即时传导(三式/遁甲 liveReplot+首盘显式门)+择日空闲预挂载(forceRender+kill-switch)+金标 全在位"
}

seg_197() {
# ── [197] 调试插桩不得混进发布产物 ──────────────────────────────────────────
# 🔴 病史(v3.7.3 真机拆包抓出):排查「三式改时间盘不动」时往 SanShiUnitedMain / models/astro
# 临时插了 console.log 探针,收尾撤除用的正则只覆盖了「独占一行的 try{ console.log(...) }」形态,
# **漏掉了 `try{ if(cond) console.log(...) }catch(e){} ` 这种带条件的单行写法** ⇒ 一条 `[D] didUpdate`
# 探针随前端进了已公证的 public .pkg,是拆开 web-app 部件搜字符串才发现的(源码 grep 当时也能查到,
# 但收尾时只按自己记得的形态搜,没做全类扫)。
# 判据:src 全树不得出现本类调试标记(业务代码里作为**注释**说明日志门的 "[D] 调试日志门" 不算,
# 故只认 console.log 同行出现标记的真代码形态)。
echo "[197] 调试插桩零残留"
S197_BAD=0
S197_SRC="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S197_HITS="$(pf_prod_grep -nE "console\.(log|debug|info)\([^)]*\[(DBG|D|M)[0-9]*\]" "${S197_SRC}" | head -5)"
[ -n "${S197_HITS}" ] && { bad "[197] 🔴 发现调试插桩残留(会随前端进 .pkg):"; printf '%s\n' "${S197_HITS}" >&2; S197_BAD=1; }
S197_HITS2="$(pf_prod_grep -nE "window\.__(EPOCHLOG|MARK|probe|netProbe)" "${S197_SRC}" | head -5)"
[ -n "${S197_HITS2}" ] && { bad "[197] 🔴 发现挂在 window 上的临时探针残留:"; printf '%s\n' "${S197_HITS2}" >&2; S197_BAD=1; }
[ "${S197_BAD}" = "0" ] && ok "[197] src 全树无调试插桩残留"
}

seg_220() {
# seg_220 壳内页面版面体检(启动/诊断/偏好三页)。
#   3 页 × 多尺寸(含各自最小与极端宽高比) × 12 缩放档(0.7–1.8) × 明暗两态 = 384 组合,
#   七类判据(横向出界/纵向滚不到/被 hidden 切/卡片压盖/文本裁切/中文竖排/对比度 AA)。
#   跑之前先自证判别力(人为制造每类缺陷必须判红)——审查器自身出过多次误报漏报,
#   故把自证做成体检的前置步骤:自证不过 ⇒ 体检结论不作数。
echo "[${PF_NO}] 壳内页面版面体检(384 组合 × 七类判据)"
S220_AUDIT="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/audit_shell_pages.py"
if [ ! -f "${S220_AUDIT}" ]; then
    bad "[${PF_NO}] 缺 audit_shell_pages.py —— 门面体检闸门丢失"
elif ! python3 -c "import playwright" >/dev/null 2>&1; then
    warn "[${PF_NO}] 未装 playwright,跳过版面体检(装:python3 -m pip install playwright && python3 -m playwright install chromium)"
else
    S220_OUT="$(cd "${REPO_ROOT}/Horosa_Desktop_Installer" && python3 scripts/audit_shell_pages.py --self-test 2>&1)"
    if [ $? -ne 0 ]; then
        bad "[${PF_NO}] 判据自证失败(审查器自身漏检,结论不可信): $(printf '%s' "${S220_OUT}" | tail -3 | tr '\n' ' ')"
    else
        S220_OUT2="$(cd "${REPO_ROOT}/Horosa_Desktop_Installer" && python3 scripts/audit_shell_pages.py 2>&1)"
        if [ $? -ne 0 ]; then
            bad "[${PF_NO}] 壳内页面体检发现缺陷: $(printf '%s' "${S220_OUT2}" | tail -6 | tr '\n' ' ')"
        else
            ok "[${PF_NO}] $(printf '%s' "${S220_OUT2}" | tail -1)"
        fi
    fi
fi
}

seg_221() {
# seg_221 主应用版面体检 × 双引擎语义 —— 2026-08-27 缩放档底部死带事故。
#   为什么单有 seg_220 不够(两条都是这次踩出来的):
#     ① seg_220 只覆盖壳内三页,**主应用一页都没进闸门**;而 seg_177b 是结构锁(查代码形状),
#        不看渲染结果 —— 事故当天它们全绿,用户屏幕上却是一大条空白。
#     ② 所有护栏都只跑一种引擎语义。真机实测两台机器不同:
#          E3 画面缩放、rect 跟着缩放     E2 画面缩放、rect **不**反映
#        出事那段「clientHeight ÷ rect探针」在 E3 上恰好正确、E2 上算短 z 倍 ⇒ 单引擎必假绿。
#   judge 全在 scripts/audit_app_layout.py:尺寸 × 12 缩放档 × E2/E3 = 120 组合,
#   四类判据(内容纵向填充 FILL / 横向填充 WIDTH-FILL / 容器贴底 HOST-SHORT / 基线洁净)。
#   判别力已实证:同一闸门对**事故前产物**在 E2 下判红(填充 78%)、修复后判绿。
echo "[${PF_NO}] 主应用版面体检(120 组合 × 双引擎语义)"
S221_AUDIT="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/audit_app_layout.py"
S221_DIST="${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file/index.html"
if [ ! -f "${S221_AUDIT}" ]; then
    bad "[${PF_NO}] 缺 audit_app_layout.py —— 主应用版面闸门丢失"
elif [ ! -f "${S221_DIST}" ]; then
    warn "[${PF_NO}] 无前端产物(dist-file),跳过主应用版面体检 —— 打包前必然已构建,届时会真跑"
elif ! python3 -c "import playwright" >/dev/null 2>&1; then
    warn "[${PF_NO}] 未装 playwright,跳过(装:python3 -m pip install playwright && python3 -m playwright install chromium)"
else
    S221_OUT="$(cd "${REPO_ROOT}/Horosa_Desktop_Installer" && python3 scripts/audit_app_layout.py --self-test 2>&1)"
    if [ $? -ne 0 ]; then
        bad "[${PF_NO}] 判据自证失败(审查器自身漏检,结论不可信): $(printf '%s' "${S221_OUT}" | tail -3 | tr '\n' ' ')"
    else
        S221_OUT2="$(cd "${REPO_ROOT}/Horosa_Desktop_Installer" && python3 scripts/audit_app_layout.py 2>&1)"
        if [ $? -ne 0 ]; then
            bad "[${PF_NO}] 主应用版面体检发现缺陷: $(printf '%s' "${S221_OUT2}" | tail -6 | tr '\n' ' ')"
        else
            ok "[${PF_NO}] $(printf '%s' "${S221_OUT2}" | tail -1)"
        fi
    fi
fi
}

seg_234() {
# seg_234 Tahoe 版面根治锁(2026-09-01):四链修复(盘面域混/resize 事件链/缩放数值漂移/探针
#      多拍)的结构完整性。历史教训:audit 内嵌 APPLY 拷贝悄悄漂移成假「逐字对齐」,故
#      ③强制运行时抽取+零拷贝;紫微 rect→style 域混由 jest T4+此处双锁。
echo "[${PF_NO}] Tahoe 版面根治锁(域混/resize 桥/探针多拍/zoom-snap)"
S234_BAD=0
S234_MAIN="$(pf_shell_rs_prod)"
S234_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
# ① 壳侧四标记+多拍 token
for S234_TOK in "zoom-apply-fn:begin" "zoom-apply-fn:end" "tahoe-resize-bridge" "zoom-snap"; do
  grep -aq "\[${S234_TOK}\]" "${S234_MAIN}" || { bad "[${PF_NO}] main.rs 缺 [${S234_TOK}] 标记"; S234_BAD=1; }
done
grep -aq "__applyBodyComp('raf')" "${S234_MAIN}" || { bad "[${PF_NO}] main.rs 探针缺 rAF 重测拍"; S234_BAD=1; }
grep -aq "__applyBodyComp('load')" "${S234_MAIN}" || { bad "[${PF_NO}] main.rs 探针缺 load 重测拍"; S234_BAD=1; }
grep -aq "__applyBodyComp('resize')" "${S234_MAIN}" || { bad "[${PF_NO}] main.rs 探针缺 resize 重跑"; S234_BAD=1; }
grep -aq "(value \* 10.0).round() / 10.0" "${S234_MAIN}" || { bad "[${PF_NO}] main.rs zoom snap 归一被删"; S234_BAD=1; }
grep -aq "dispatchEvent(new Event('resize'))" "${S234_MAIN}" || { bad "[${PF_NO}] main.rs resize 桥派发被删"; S234_BAD=1; }
# ② global.js 同构 token+诊断出口
for S234_GT in "__applyBodyComp('raf')" "__applyBodyComp('load')" "__applyBodyComp('resize')" "__HOROSA_ZOOM_PROBE_LAST" "__HOROSA_ZOOM_REPROBE_ARMED" "horosa.compat.zoomReprobe"; do
  grep -aqF "${S234_GT}" "${S234_UI}/src/global.js" || { bad "[${PF_NO}] global.js 缺同构 token: ${S234_GT}"; S234_BAD=1; }
done
# ③ audit 运行时抽取+零内嵌 APPLY 拷贝(剥注释判,calc 补偿串只许活在 main.rs 抽取段)
grep -aq "extract_apply_zoom_js" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/audit_app_layout.py" \
  || { bad "[${PF_NO}] audit_app_layout.py 缺运行时抽取(测的≠跑的回潮)"; S234_BAD=1; }
S234_INLINE="$(sed 's/#.*$//' "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/audit_app_layout.py" | grep -ac "calc(100% / ")"
[ "${S234_INLINE}" = "0" ] || { bad "[${PF_NO}] audit_app_layout.py 又出现内嵌补偿拷贝 ×${S234_INLINE}(必须运行时抽取)"; S234_BAD=1; }
# ④ 四 jest 合同在位
for S234_T in \
  src/utils/__tests__/shellZoomProbeGuard.test.js \
  src/components/ziwei/__tests__/ziweiChartSurfaceDomain.test.js \
  src/components/graph/__tests__/graphTextFill.test.js; do
  [ -f "${S234_UI}/${S234_T}" ] || { bad "[${PF_NO}] jest 合同缺失: ${S234_T}"; S234_BAD=1; }
done
grep -aq "T4 rect→style 写回族" "${S234_UI}/src/utils/__tests__/layoutDomainStaticGuard.test.js" \
  || { bad "[${PF_NO}] layoutDomainStaticGuard 缺 T4 rect→style 写回族"; S234_BAD=1; }
# ⑤ 紫微主刀点零 gBCR(剥注释;修复注释点名旧 API 属正常)
S234_ZW="$(awk '/ensureChartSurfaceSize\(/{f=1} f&&/drawChart\(/{exit} f' "${S234_UI}/src/components/ziwei/ZiWeiChart.js" | grep -v '^\s*//' | grep -ac 'getBoundingClientRect')"
[ "${S234_ZW}" = "0" ] || { bad "[${PF_NO}] ZiWeiChart.ensureChartSurfaceSize 又吃 rect 域读数(域混回潮)"; S234_BAD=1; }
# ⑥ GraphHelper 文字填色渲染(4 个 text 分支 stroke=none)
S234_GH="$(grep -ac "\.attr('stroke', 'none')" "${S234_UI}/src/components/graph/GraphHelper.js")"
[ "${S234_GH}" -ge 4 ] || { bad "[${PF_NO}] GraphHelper 文字 stroke=none 不足 4 处(描边回潮,实测 ${S234_GH})"; S234_BAD=1; }
# ⑦ models/app.js visualViewport 对称挂/卸
grep -aq "window.visualViewport.addEventListener('resize', vvHandler)" "${S234_UI}/src/models/app.js" \
  || { bad "[${PF_NO}] models/app.js 缺 visualViewport 三保险挂载"; S234_BAD=1; }
grep -aq "window.visualViewport.removeEventListener('resize', vvHandler)" "${S234_UI}/src/models/app.js" \
  || { bad "[${PF_NO}] models/app.js visualViewport 卸载不对称"; S234_BAD=1; }
[ "${S234_BAD}" = "0" ] && ok "[${PF_NO}] Tahoe 四链根治结构全在位(壳桥+多拍探针+snap+域混锁+填色+vv 三保险)"
}

seg_239() {
# seg_239 壳→页面事件桥死开关锁:打包版无 window.__TAURI__(withGlobalTauri 缺省 false)且 capabilities 为空
#   (event.listen 无授权)→ 任何「只探 window.__TAURI__」的门控/`__TAURI__.event.listen` 在壳内恒死。锁:页面零单探门控、
#   自动备份 tick 走 eval 回调、壳侧不再 emit、桥自检上报在位、ACL 面不变(不开 withGlobalTauri/不加 capabilities)、双测在位。
echo "[${PF_NO}] 壳→页面事件桥(单探 __TAURI__ 门控/emit 死链)锁"
S239_BAD=0
S239_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S239_RS="$(pf_shell_rs_prod)"
S239_SINGLE="$(grep -rnE "!!window\.__TAURI__|!window\.__TAURI__\)|window\.__TAURI__\.event\.listen|window\.__TAURI__\) \? \(window\.__TAURI__" "${S239_UI}/src" --include='*.js' 2>/dev/null | grep -v "__tests__" | grep -vE "^[^:]+:[0-9]+:\s*//" || true)"
[ -z "${S239_SINGLE}" ] || { bad "[${PF_NO}] 页面出现只探 window.__TAURI__ 的门控/listen(打包版恒死):"; echo "${S239_SINGLE}" | head -5 | sed 's/^/      /'; S239_BAD=1; }
grep -aq "window.__horosaAutoBackupTick = " "${S239_UI}/src/utils/autoBackup.js" || { bad "[${PF_NO}] autoBackup.js 未挂 __horosaAutoBackupTick 回调"; S239_BAD=1; }
grep -aq "__horosaPendingAutoBackupTicks" "${S239_UI}/src/utils/autoBackup.js" || { bad "[${PF_NO}] autoBackup.js 缺 pending 补读"; S239_BAD=1; }
grep -aq "reportDesktopBridgeDiag()" "${S239_UI}/src/layouts/app.js" || { bad "[${PF_NO}] layouts/app.js 未挂桥自检上报"; S239_BAD=1; }
grep -aq "fn dispatch_auto_backup_tick" "${S239_RS}" || { bad "[${PF_NO}] main.rs 缺 dispatch_auto_backup_tick(eval 回调投递)"; S239_BAD=1; }
grep -aqF 'dispatch_auto_backup_tick(&backup_handle, seq);' "${S239_RS}" || { bad "[${PF_NO}] 壳 setup 的心跳线程不再调 dispatch_auto_backup_tick(只剩定义 = 自动备份 tick 无人投递)"; S239_BAD=1; }
grep -aqF 'emit("horosa://auto-backup-tick"' "$(pf_shell_rs_prod_all)" && { bad "[${PF_NO}] main.rs 仍用 emit 投递自动备份 tick(无人能收)"; S239_BAD=1; }
grep -aq "bridge_diag_report_command," "${S239_RS}" || { bad "[${PF_NO}] main.rs 未注册 bridge_diag_report_command"; S239_BAD=1; }
grep -aq "fn packaged_context_has_no_global_tauri_and_event_listen_is_acl_denied" "$(pf_shell_rs_tests)" || { bad "[${PF_NO}] cargo ACL/withGlobalTauri 自证测试缺失"; S239_BAD=1; }
grep -aq '"withGlobalTauri": *true' "${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/tauri.conf.json" && { bad "[${PF_NO}] tauri.conf.json 开了 withGlobalTauri(ACL 面扩大,与桥范式冲突;须评估后另立哨兵)"; S239_BAD=1; }
[ -d "${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/capabilities" ] && { bad "[${PF_NO}] 出现 capabilities 目录(ACL 面变化未经评估)"; S239_BAD=1; }
[ -f "${S239_UI}/src/utils/__tests__/autoBackupBridge.test.js" ] || { bad "[${PF_NO}] autoBackupBridge.test.js 缺失"; S239_BAD=1; }
[ -f "${S239_UI}/src/utils/desktopBridgeDiag.js" ] || { bad "[${PF_NO}] desktopBridgeDiag.js 缺失"; S239_BAD=1; }
# eval 回调范式的隐性前提:CSP 必须保留 'unsafe-eval'(收紧即整条壳→页面通道再死一次)
grep -aq "'unsafe-eval'" "${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/tauri.conf.json" || { bad "[${PF_NO}] tauri.conf.json CSP 丢了 'unsafe-eval'(壳→页面 eval 回调范式失效)"; S239_BAD=1; }
[ -f "${S239_UI}/src/utils/__tests__/desktopBridgeDiag.test.js" ] || { bad "[${PF_NO}] desktopBridgeDiag.test.js 缺失"; S239_BAD=1; }
[ "${S239_BAD}" = "0" ] && ok "[${PF_NO}] 事件桥:零单探门控/tick 走 eval 回调/壳零 emit/自检上报/ACL 面不变/双测在位/CSP unsafe-eval"
}

seg_283() {
# seg_283 后端请求记录不落明文密钥:① AI 分析端点整组排除出交易日志 ② 配置追加表在位
#   ③ 脱敏单源 SecretRedactor 的名字表 / 文字形态在位 ④ 每条写出路径(交易日志写入、请求元组、回落缓存写文件、错误日志请求数据 / 查询串、
#   出站请求头与网址日志)都经单源 ⑤ 不许再出现平行的字段表 / 正则 ⑥ 回落缓存:装请求记录的那张表开落盘脱敏、工厂处处带开关
#   ⑦ JUnit 判别向量在位(该掩的名字与形态 + 不该掩的业务字段;落盘文件不含原文、旧明文下一次写盘即脱敏、功能性缓存原样)。
#   本段只核源码与配置,不读任何缓存文件的内容。
echo "[${PF_NO}] 后端请求记录不落明文密钥:AI 分析端点整组排除 + 脱敏单源 + 写出路径全经单源 + 回落缓存落盘脱敏(#68)"
S283_BAD=0
S283_CTRL="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/AIAnalysisController.java"
S283_EXC="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/resources/conf/log/excludelogtrans.json"
S283_LOGP="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/resources/conf/properties/log.properties"
if [ -f "${S283_CTRL}" ] && [ -f "${S283_EXC}" ]; then
  S283_RES="$(python3 - "${S283_CTRL}" "${S283_EXC}" <<'PY'
import json, re, sys
ctrl = open(sys.argv[1], encoding='utf-8').read()
base = re.search(r'@RequestMapping\("(/[^"]*)"\)\s*\npublic class', ctrl)
base = base.group(1) if base else '/aianalysis'
body = ctrl.split('public class', 1)[1] if 'public class' in ctrl else ctrl
paths = set(base + p for p in re.findall(r'@(?:Post|Get|Request)Mapping\(\s*(?:value\s*=\s*)?"(/[^"]+)"', body))
excl = set(json.load(open(sys.argv[2], encoding='utf-8')))
missing = sorted(paths - excl)
print(('ok:%d' % len(paths)) if not missing else ('missing:' + ','.join(missing)))
PY
)"
  case "${S283_RES}" in
    ok:*) : ;;
    *) bad "[${PF_NO}] 🔴 AI 分析端点未整组排除出交易日志(一旦开日志会记对话与 key):${S283_RES}"; S283_BAD=1 ;;
  esac
else
  bad "[${PF_NO}] 🔴 缺控制器或排除表:${S283_CTRL#${REPO_ROOT}/} / ${S283_EXC#${REPO_ROOT}/}"; S283_BAD=1
fi
for S283_K in apiKey authorization Authorization extraHeaders token; do
  grep -aq "^remvedparams=.*\b${S283_K}\b" "${S283_LOGP}" 2>/dev/null || { bad "[${PF_NO}] 🔴 脱敏参数表 remvedparams 缺 ${S283_K}"; S283_BAD=1; }
done
S283_B="${REPO_ROOT}/Horosa-Web/astrostudysrv/boundless/src"
S283_R="${S283_B}/main/java/boundless/utility/SecretRedactor.java"
S283_C="${S283_B}/main/java/boundless/types/cache"
# ③ 单源名字表 / 文字形态
for S283_K in '"key", "apikey", "token", "secret", "password"' '"authorization"' '"bearer"' '"extraheaders", "rsaparam"' \
              '"apikey", "token", "secret", "password", "passwd", "authorization"' 'x-goog-api-key|x-api-key|api[_-]?key' \
              'Pattern JSON_PAIR = ' 'Pattern JSON_PAIR_ESCAPED = ' 'Pattern QUERY = ' 'Pattern HEADER_KEY = ' 'Pattern HEADER_AUTH = ' 'Pattern HEADER_COOKIE = ' 'Pattern BEARER = ' 'Pattern SHAPES = ' \
              'public static Map<String, Object> redactRecord(' 'public static String redactText(String text, String... literalSecrets)' \
              'out = replaceJsonPairs(JSON_PAIR, out);' 'out = replaceJsonPairs(JSON_PAIR_ESCAPED, out);' 'out = QUERY.matcher(out)' 'out = HEADER_KEY.matcher(out)' 'out = HEADER_AUTH.matcher(out)' 'out = HEADER_COOKIE.matcher(out)' \
              'return redactTextUnsafe(text, literalSecrets);' '}catch(StackOverflowError e) {' \
              'out = BEARER.matcher(out)' 'out = SHAPES.matcher(out)'; do
  pf_need "${S283_R}" "${S283_K}" "🔴 脱敏单源 SecretRedactor 缺「${S283_K}」"
done
# ④ 写出路径都经单源
pf_once "${S283_B}/main/java/boundless/spring/help/TransLogMongoHelper.java" 'cache.add(' "🔴 交易日志写入点不止一处(每处都要经脱敏单源)"
pf_need "${S283_B}/main/java/boundless/spring/help/TransLogMongoHelper.java" 'cache.add(SecretRedactor.redactRecord(map));' "🔴 交易日志写入前未整条脱敏"
pf_need "${S283_B}/main/java/boundless/spring/help/interceptor/TransData.java" 'head = SecretRedactor.redactRecord(head, RemovedParams);' "🔴 请求元组的请求头未经脱敏单源"
pf_need "${S283_B}/main/java/boundless/spring/help/interceptor/TransData.java" 'map = SecretRedactor.redactRecord(map, RemovedParams);' "🔴 请求元组的参数未经脱敏单源"
pf_once "${S283_C}/LocalDocumentCache.java" 'Files.writeString(' "🔴 回落缓存写文件点不止一处"
pf_need "${S283_C}/LocalDocumentCache.java" 'root.put("docs", persistDocsLocked());' "🔴 回落缓存写文件未经 persistDocsLocked"
pf_need "${S283_C}/LocalDocumentCache.java" 'SecretRedactor.redactRecord(doc, null, this.keyField)' "🔴 回落缓存落盘脱敏未经单源"
S283_W="$(grep -alE 'Files\.(write|writeString|newBufferedWriter|newOutputStream)\(|new FileWriter\(|new FileOutputStream\(' "${S283_C}"/*.java 2>/dev/null | sed 's#.*/##' | tr '\n' ' ')"
[ "${S283_W}" = "LocalDocumentCache.java " ] || pf_seg_bad "🔴 缓存包里写文件的类不止 LocalDocumentCache(新写盘点要经脱敏单源):${S283_W}"
pf_need "${S283_B}/main/java/boundless/spring/help/springcomp/RestResponseEntityExceptionHandler.java" 'SecretRedactor.redactValue(decoded)' "🔴 错误日志请求数据未经脱敏单源"
pf_need "${S283_B}/main/java/boundless/spring/help/springcomp/RestResponseEntityExceptionHandler.java" 'return SecretRedactor.redactText(queryString);' "🔴 错误日志查询串未经脱敏单源"
pf_need "${S283_B}/main/java/boundless/spring/help/interceptor/DebugTransParamsLogInterceptor.java" 'SecretRedactor.redactText(request.getQueryString())' "🔴 调试请求日志查询串未脱敏"
pf_need "${S283_B}/main/java/boundless/net/http/HttpUriRequestHystrixCommand.java" 'boundless.utility.SecretRedactor.redactHeaders(headers)' "🔴 出站请求头脱敏未经单源"
# 出站请求失败日志每行两个参数(网址 + 异常文字)都要过单源:一行少于两处 redactText 即漏
S283_U="$(cat "${S283_B}"/main/java/boundless/net/http/*.java 2>/dev/null | grep -aE '^[[:space:]]*(HttpClientUtility\.log\.error\(|log\.error\("fail, msg:|QueueLog\.error\(AppLoggers\.ErrorLogger, "请求\{\}失败)' | awk -F'SecretRedactor[.]redactText[(]' 'NF<3' | wc -l | tr -d ' ')"
[ "${S283_U:-0}" = "0" ] || pf_seg_bad "🔴 出站请求失败日志有 ${S283_U} 处网址 / 异常文字未经脱敏单源"
pf_need "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java" 'return SecretRedactor.redactText(text, secrets);' "🔴 AI 代理错误文字脱敏未委托单源"
# ⑤ 反锚:平行的字段表 / 正则不许回潮
pf_none "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java" 'SECRET_QUERY = Pattern.compile' "🔴 AI 代理又自带一套密钥正则(规则分叉)"
pf_none "${S283_B}/main/java/boundless/spring/help/springcomp/RestResponseEntityExceptionHandler.java" 'sensitiveLogFields' "🔴 异常处理器又自带一张字段表(规则分叉)"
pf_none "${S283_B}/main/java/boundless/net/http/HttpUriRequestHystrixCommand.java" 'key.equals("authorization")' "🔴 出站请求头又自带一张名字表(规则分叉)"
pf_none "${S283_B}/main/java/boundless/spring/help/interceptor/TransData.java" 'removeParamsIgnoreCase' "🔴 请求元组回到只删顶层同名参数(嵌套 / 请求头 / 网址里的密钥漏网)"
# ⑥ 回落缓存:装请求记录的表开落盘脱敏;工厂每处造回落缓存都带开关、派生工厂继承
grep -aqE '^fallback\.redactonpersist=true[[:space:]]*$' "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/resources/conf/properties/cache/mongotranslog.properties" 2>/dev/null \
  || pf_seg_bad "🔴 交易日志缓存未开回落缓存落盘脱敏(fallback.redactonpersist=true)"
S283_F="${S283_C}/MongoCacheFactory.java"
S283_NF="$(pf_code -q "${S283_F}" | grep -ac 'new LocalDocumentCache(' || true)"
S283_NFR="$(pf_code -q "${S283_F}" | grep -a 'new LocalDocumentCache(' | grep -ac 'redactOnPersist);' || true)"
[ "${S283_NF:-0}" -ge 3 ] && [ "${S283_NF}" = "${S283_NFR}" ] || pf_seg_bad "🔴 工厂造回落缓存有处没带落盘脱敏开关(${S283_NFR:-0}/${S283_NF:-0})"
pf_need "${S283_F}" 'p.get(RedactOnPersistKey)' "🔴 工厂未读 fallback.redactonpersist"
pf_need "${S283_F}" 'factory.redactOnPersist = this.redactOnPersist;' "🔴 派生工厂未继承落盘脱敏开关"
# ⑦ JUnit 判别向量在位
S283_T="${S283_B}/test/java/boundless"
for S283_K in '"apiKey", "APIKEY", "api_key", "api-key"' '"x-api-key", "X-Api-Key", "x-goog-api-key", "X-Goog-Api-Key"' '"authorization", "Authorization", "Proxy-Authorization", "bearer"' \
              '"password", "Password", "PASSWORD"' '"pdTimeKey", "rateKey"' '"maxTokens", "max_tokens"' '"providerType=deepseek&apiKey=***&token=***"' 'opaque/Key+1'; do
  pf_need "${S283_T}/utility/SecretRedactorTest.java" "${S283_K}" "🔴 脱敏判别向量缺「${S283_K}」"
done
for S283_K in 'public void requestRecordsAreMaskedOnDiskButNotInMemory()' 'public void legacyPlaintextFileIsScrubbedOnNextWriteAndStillReadable()' 'public void functionalCachesPersistVerbatim()'; do
  pf_need "${S283_T}/types/cache/LocalDocumentCacheRedactionTest.java" "${S283_K}" "🔴 回落缓存落盘脱敏测试缺「${S283_K}」"
done
[ -f "${S283_T}/spring/help/TransLogRedactionWiringTest.java" ] || pf_seg_bad "🔴 缺写出路径接线源码锁 TransLogRedactionWiringTest"
[ "${S283_BAD}" = "0" ] && ok "[${PF_NO}] AI 分析端点整组排除 + 脱敏单源 + 写出路径全经单源 + 回落缓存落盘脱敏 + 判别向量在位"
}

seg_288() {
# seg_288 玄学史天象库载入逐行解析年号:候选按首字分桶(桶内保持原表序),命中集与「等长先到先得」不变,
#       与全表线性扫逐值相同。锚住分桶与开关回退路 + 等价测试在位(2026-09-26)。
echo "[${PF_NO}] 玄学史年号首字分桶(逐值等价)"
S288_BAD=0
S288_P="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/xuanshi/period.py"
S288_T="${REPO_ROOT}/Horosa-Web/astropy/tests/test_xuanshi_era_index.py"
[ -s "${S288_T}" ] || { bad "[${PF_NO}] 🔴 缺等价测试 test_xuanshi_era_index.py"; S288_BAD=1; }
grep -q "HOROSA_XUANSHI_ERA_INDEX" "${S288_P}" 2>/dev/null && grep -q "_ERA_BY_FIRST.setdefault(_k\[0\], \[\]).append(_k)" "${S288_P}" 2>/dev/null \
  && grep -q "for cand in _era_candidates(s):" "${S288_P}" 2>/dev/null \
  && grep -q "for e in _era_candidates(_rest_emp)" "${S288_P}" 2>/dev/null || { bad "[${PF_NO}] 🔴 年号解析回到全表线性扫(或分桶 / 开关回退路缺一)"; S288_BAD=1; }
grep -q "test_era_index_matches_linear_scan" "${S288_T}" 2>/dev/null && grep -q "test_celestial_load_identical_both_modes" "${S288_T}" 2>/dev/null \
  || { bad "[${PF_NO}] 🔴 等价测试缺「逐值对全表扫」或「天象库整表两档相等」"; S288_BAD=1; }
[ "${S288_BAD}" = "0" ] && ok "[${PF_NO}] 年号首字分桶 + 开关回退路 + 等价测试在场"
}

seg_289() {
# seg_289 生辰节气(/jieqi/birth,每张新盘都会调)的节气牛顿求解与卯时基准盘原每步建整张默认盘,只读太阳经度 / 速度 / 赤经。
#       同 HOROSA_JIEQI_FAST_APPROACH 直取太阳位置 + 太阳瘦盘,两档逐字节相同;锚住防回潮(2026-09-26)。
echo "[${PF_NO}] 生辰节气快路径(节气求解直取太阳 + 卯时基准瘦盘)"
S289_BAD=0
S289_P="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/jieqi/BirthJieQi.py"
S289_T="${REPO_ROOT}/Horosa-Web/astropy/tests/test_birthjieqi_fast_approach.py"
[ -s "${S289_T}" ] || { bad "[${PF_NO}] 🔴 缺回归测试 test_birthjieqi_fast_approach.py"; S289_BAD=1; }
grep -q "from flatlib.ephem import swe" "${S289_P}" 2>/dev/null \
  && [ "$(grep -c "sun = swe.sweObject(const.SUN, " "${S289_P}" 2>/dev/null)" -ge 2 ] \
  && [ "$(grep -c "chart = self._ascChart(dateTime)" "${S289_P}" 2>/dev/null)" -ge 2 ] || { bad "[${PF_NO}] 🔴 生辰节气求解 / 卯时基准盘回到整张默认盘"; S289_BAD=1; }
grep -q "test_fast_path_builds_no_full_default_chart" "${S289_T}" 2>/dev/null && grep -q "test_fast_and_slow_paths_are_byte_identical" "${S289_T}" 2>/dev/null \
  || { bad "[${PF_NO}] 🔴 回归测试缺「两档逐字节同」或「快档零整盘」"; S289_BAD=1; }
[ "${S289_BAD}" = "0" ] && ok "[${PF_NO}] 生辰节气快路径 + 两档等价测试 + 零整盘结构断言在场"
}

seg_291() {
# seg_291 玄学史人物关系图节点表原按字符串集合迭代,顺序随进程哈希种子变(每次启动输出不同,力导向图初始布局也随之不同)。
#       固定为「共现权重降序、同权按人名」;锚住防回潮(2026-09-26)。
echo "[${PF_NO}] 玄学史人物关系图输出与进程哈希种子无关"
S291_BAD=0
S291_E="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/xuanshi/editorial.py"
S291_T="${REPO_ROOT}/Horosa-Web/astropy/tests/test_xuanshi_persons_graph_order.py"
[ -s "${S291_T}" ] || { bad "[${PF_NO}] 🔴 缺测试 test_xuanshi_persons_graph_order.py"; S291_BAD=1; }
grep -q 'for n in sorted(used, key=lambda n: (-deg\[n\], n))\]' "${S291_E}" 2>/dev/null || { bad "[${PF_NO}] 🔴 人物关系图节点表又按集合迭代(顺序随哈希种子变)"; S291_BAD=1; }
grep -q "PYTHONHASHSEED" "${S291_T}" 2>/dev/null || { bad "[${PF_NO}] 🔴 测试须跨哈希种子子进程比对"; S291_BAD=1; }
[ "${S291_BAD}" = "0" ] && ok "[${PF_NO}] 人物关系图节点固定序 + 跨哈希种子测试在场"
}

seg_293() {
# seg_293 铁板神数每次排盘新建计算器都重读诗词库与足本条文库、分类检索全表线性扫。按进程只载一次 + 载入时建
#       分类索引(HOROSA_TIEBAN_DB_MEMO);输出逐字节不变。锚住防回潮(2026-09-27)。
echo "[${PF_NO}] 铁板神数诗词库 / 足本条文库按进程只载一次 + 分类索引"
S293_BAD=0
S293_V="${REPO_ROOT}/Horosa-Web/vendor/kinastro/astro/tieban/tieban_calculator.py"
S293_T="${REPO_ROOT}/Horosa-Web/astropy/tests/test_tieban_db_memo.py"
[ -s "${S293_T}" ] || { bad "[${PF_NO}] 🔴 缺测试 test_tieban_db_memo.py"; S293_BAD=1; }
grep -q '_TIEBAN_DB_MEMO_ON = os.environ.get("HOROSA_TIEBAN_DB_MEMO"' "${S293_V}" 2>/dev/null \
  && grep -q "_TIEBAN_DB_MEMO.get(('verses', verses_path))" "${S293_V}" 2>/dev/null \
  && grep -q "_TIEBAN_DB_MEMO.get(('tiaowen', data_path))" "${S293_V}" 2>/dev/null \
  && grep -q "def _build_category_index(" "${S293_V}" 2>/dev/null || { bad "[${PF_NO}] 🔴 铁板神数又回到每次排盘重读两份库 / 分类全表扫"; S293_BAD=1; }
grep -q "test_pan_identical_memo_on_off_no_bleed_and_loaded_once" "${S293_T}" 2>/dev/null && grep -q "test_category_index_matches_linear_scan" "${S293_T}" 2>/dev/null \
  || { bad "[${PF_NO}] 🔴 测试缺「开关两档逐字节同 + 无串染 + 只载一次」或「分类索引 = 线性扫」"; S293_BAD=1; }
[ "${S293_BAD}" = "0" ] && ok "[${PF_NO}] 铁板神数库按进程只载一次 + 分类索引 + 测试在场"
}

seg_295() {
# seg_295 主排盘两处等价提速:恒星批 LRU 存入 / 命中由整批 deepcopy 改快克隆(可变属性仍深拷贝、共享关系保持)·
#       JSON 快径预扫由递归改迭代(逐节点判据不变)。锚住防回潮(2026-09-27)。
echo "[${PF_NO}] 恒星批快克隆 + JSON 快径迭代预扫"
S295_BAD=0
S295_E="${REPO_ROOT}/Horosa-Web/flatlib-ctrad2/flatlib/ephem/ephem.py"
S295_F="${REPO_ROOT}/Horosa-Web/astropy/websrv/fastjson.py"
S295_T="${REPO_ROOT}/Horosa-Web/astropy/tests/test_star_clone_and_iter_scan.py"
[ -s "${S295_T}" ] || { bad "[${PF_NO}] 🔴 缺测试 test_star_clone_and_iter_scan.py"; S295_BAD=1; }
grep -q "return key, _cloneStarList(hit)" "${S295_E}" 2>/dev/null && grep -q "pristine = _cloneStarList(starList)" "${S295_E}" 2>/dev/null \
  && grep -q "HOROSA_STAR_LRU_FASTCLONE" "${S295_E}" 2>/dev/null && grep -q "setattr(c, sk, copy.deepcopy(sv))" "${S295_E}" 2>/dev/null \
  || { bad "[${PF_NO}] 🔴 恒星批快克隆缺失 / 可变属性未深拷贝 / 缺开关"; S295_BAD=1; }
grep -q "def _fast_shape_ok_iter(obj, _depth=0):" "${S295_F}" 2>/dev/null && grep -q "def _fast_shape_ok_recursive(obj, _depth=0):" "${S295_F}" 2>/dev/null \
  && grep -q "HOROSA_FAST_JSON_ITER_SCAN" "${S295_F}" 2>/dev/null || { bad "[${PF_NO}] 🔴 迭代预扫 / 递归回退路 / 开关缺一"; S295_BAD=1; }
grep -q "test_iterative_scan_matches_recursive" "${S295_T}" 2>/dev/null && grep -q "test_star_clone_matches_deepcopy_and_isolates" "${S295_T}" 2>/dev/null \
  || { bad "[${PF_NO}] 🔴 测试缺「迭代 = 递归」或「快克隆 = deepcopy + 隔离」"; S295_BAD=1; }
[ "${S295_BAD}" = "0" ] && ok "[${PF_NO}] 恒星批快克隆 + 迭代预扫 + 测试在场"
}

seg_304() {
echo "[${PF_NO}] 升级后缓存版本闸与温启首批请求(早导航前记运行时版本 / 收尾比对 rv / 直连排盘服务过就绪门 / 预取优先级先于去重)"
S304_BAD=0
S304_RS="$(pf_shell_rs_prod)"
S304_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
# ① runtime_bootstrap 里「记运行时版本」先于「生成早导航 URL」:否则整个会话 URL 不带 rv,前端缓存信封恒为旧版本号,
#    升级后 24 h 内同参数的盘可能回放旧运行时的结果
s304_order="$(awk '/^(pub\(crate\) )?fn runtime_bootstrap\(/{f=1} f && !n && index($0,"note_runtime_version_for_url(&manifest.version);"){n=NR} f && !e && index($0,"let early_url = early_nav_url("){e=NR} END{ if(n && e && n<e) print "ok"; else print "bad" }' "${S304_RS}" 2>/dev/null)"
[ "${s304_order}" = "ok" ] || { bad "[${PF_NO}] 🔴 早导航 URL 不带 rv(运行时版本在早导航之后才记)"; S304_BAD=1; }
# ② 收尾 ready 的同参判定含 rv(不一致必须整页重载,不许沿用错误的缓存版本号)
grep -qF 'var keys = ["srv", "chartSrv", "kentangSrv", "rv"];' "${S304_RS}" 2>/dev/null || { bad "[${PF_NO}] 🔴 收尾 ready 不比对 rv"; S304_BAD=1; }
# ③ 直连排盘服务的公共入口先过就绪门(温启恢复到卜类 / 玄学史等页时,首批请求不打到尚未监听的端口)
grep -qF 'await waitForBackendBoot(url);' "${S304_UI}/utils/chartFetch.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 fetchChartWithRetry 未过就绪门"; S304_BAD=1; }
# ④ 预取优先级在 request() 入口、去重分流之前打头(去重层 runner 在 await 之后才调,放在那里判定永远读不到预取作用域)
s304_req="$(awk '/^export default async function request\(url, options\) \{/{f=1} /^async function requestCore\(url, options\) \{/{f=0} f && !t && index($0,"options = tagRequestPriority(options, isInPrefetchScope());"){t=NR} f && !d && index($0,"if (dedupeEligible(url, options)) {"){d=NR} END{ if(t && d && t<d) print "ok"; else print "bad" }' "${S304_UI}/utils/request.js" 2>/dev/null)"
[ "${s304_req}" = "ok" ] || { bad "[${PF_NO}] 🔴 预取优先级头未在去重分流之前打上(可去重端点永不带头)"; S304_BAD=1; }
# ⑤ 测试在位(壳源码顺序 / 直连就绪门 / 入口打头)
grep -qF 'fn runtime_version_noted_before_early_navigation()' "$(pf_shell_rs_tests)" 2>/dev/null \
  && grep -qF '排盘服务直连路径(fetchChartWithRetry)同样先过就绪门' "${S304_UI}/utils/__tests__/backendBootGate.test.js" 2>/dev/null \
  && grep -qF 'request() 入口在去重分流与任何 await 之前打头' "${S304_UI}/utils/__tests__/requestPriority.test.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 缺缓存版本闸 / 就绪门 / 优先级测试"; S304_BAD=1; }
[ "${S304_BAD}" = "0" ] && ok "[${PF_NO}] 早导航带 rv / 收尾比对 rv / 直连排盘服务过就绪门 / 预取优先级先于去重 / 测试在位"
}

seg_9() {
# 9. 更新后启动卡顿修复哨兵(本次复盘):防「更新后重启卡在 100% / 反复走 300s 全量慢路径」回归。
#    根因复盘(更新后启动卡顿修复-v2.3.1):① 标记仅成功时消费→失败残留致次次慢;
#    ② pid 仅判存在→残留死 pid 误拦截;③ 首启进度停住无反馈像死机;④ warmup 同步阻塞启动。
echo "[9] 更新后启动卡顿修复哨兵"
MAINRS="$(pf_shell_rs_prod)"
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
  # 根因复盘:更新后自启修复-v2.3.2。哨兵 grep 注释 sentinel(comment,cargo fmt 不拆)。
  if grep -q "需重启两三次" "${MAINRS}"; then
    ok "D 更新后首启预写 fast-path 标记(已验签 runtime 不再 300s 全量)"
  else
    bad "main.rs 缺 v2.3.2 预写 fast-path 标记修复 —— 更新后首启回到冷全量、强退反复(根因复盘:更新后自启修复-v2.3.2)"
  fi
  # E (2.4.0 重发·真因哨兵):首启分支**删掉 cleanup_state** —— 它会 `web_shutdown.store(true)` 关掉本次刚
  # `start_static_server` 起的静态服务器(web_port)→ `emit_ready` 导航的 `frontend_url` 连不上 → 卡启动页/
  # 进不了主界面/按钮死(真机实测真因,前两次误诊弹框/慢校验都没修好)。grep 修复说明注释(cargo fmt 不拆)。
  # 真因复盘:更新后卡启动页-真因cleanup_state误杀静态服务器-v2.4.0。**铁律:首启 start_static_server 后绝不调会触发 web_shutdown 的清理。**
  if grep -q "误杀静态服务器" "${MAINRS}"; then
    ok "E 首启分支不调 cleanup_state(真因修复·静态服务器不被误杀)"
  else
    bad "main.rs 缺「误杀静态服务器」修复说明/铁律 —— 首启分支若(再)调 cleanup_state 会关掉静态服务器致更新后卡启动页(根因复盘:更新后卡启动页-真因cleanup_state误杀静态服务器-v2.4.0)"
  fi
  # F:快路径回退从静默一行升级为醒目说明(属正常保护)+账本留痕。
  if grep -q "已自动切换完整校验" "${MAINRS}" && grep -q "rust.fast_path_fallback" "${MAINRS}"; then
    ok "F 快速启动回退醒目说明+账本留痕在位"
  else
    bad "main.rs 缺快速启动回退醒目说明(已自动切换完整校验)或账本留痕(rust.fast_path_fallback)—— 回退退化回静默一行,用户又会把回退当卡死"
  fi
else
  warn "main.rs 不存在,跳过更新卡顿哨兵(C①/A/D/E/F)"
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
}

seg_51() {
# [51] 退出不阻塞 + 启动不冻结 (2026-06-12):
#      ① 退出两臂(ExitRequested/Exit)禁同步 cleanup_state/.status()(macOS Quit=terminate: 只回调
#        Exit,同步子进程=主循环停摆=not responding),必须走 detached+去重的 spawn_exit_cleanup;
#      ② 运行时脚本端口检查禁 lsof(全进程 FD 扫描遇卡死进程单次 stall 30~100s,实测),必须 netstat;
#      ③ start_runtime 的全树元数据清理必须在 !trusted_runtime 守卫下(冷缓存下遍历数十秒=卡 36%),
#        且重活前必须先发 indeterminate 进度。
echo "[51] 退出不阻塞 + 启动不冻结"
S51_BAD=0
S51_MAIN="$(pf_shell_rs_prod)"
# 读面:产品正锚 / 计数 → 壳层模块产品代码;「产品代码里不许出现」→ 壳层模块 + 独立子模块的产品代码(测试会故意造对所有账户可写的夹具来验证检测器);用例在位 → 全部测试
S51_PRODALL="$(pf_shell_rs_prod_all)"
S51_TESTS="$(pf_shell_rs_tests)"
S51_EXIT_BLOCK="$(awk '/RunEvent::ExitRequested \{ .. \} =>/,/^            _ => \{\}/' "${S51_MAIN}")"
[ -n "${S51_EXIT_BLOCK}" ] || { bad "[51] 未能定位 run loop 退出两臂(结构变了?同步更新本哨兵)"; S51_BAD=1; }
printf '%s' "${S51_EXIT_BLOCK}" | pipe_has "cleanup_state(" && { bad "[51] 退出臂回归了同步 cleanup_state(会阻塞主循环)"; S51_BAD=1; }
printf '%s' "${S51_EXIT_BLOCK}" | pipe_has "\.status()" && { bad "[51] 退出臂出现同步 .status()"; S51_BAD=1; }
[ "$(printf '%s' "${S51_EXIT_BLOCK}" | grep -c "spawn_exit_cleanup(app)")" -ge 2 ] || { bad "[51] 退出两臂缺 spawn_exit_cleanup"; S51_BAD=1; }
for S51_SCRIPT in "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"; do
  if grep -v '^[[:space:]]*#' "${S51_SCRIPT}" | pipe_has "lsof"; then
    bad "[51] $(basename "${S51_SCRIPT}") 非注释行出现 lsof(必须 netstat 读内核表)"; S51_BAD=1
  fi
done
grep -q "netstat -anv -p tcp" "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" || { bad "[51] stop 脚本缺 netstat 端口扫描"; S51_BAD=1; }
# port_listening 的 awk 不得提前 exit:set -o pipefail 下早退令 netstat SIGPIPE(141) → 端口在听也判失败,
# 全新安装首启(untrusted)就绪门永不过 → 卡死「正在启动本地服务」。
grep -A12 "^port_listening()" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" | pipe_has "exit_found=1; exit }" && { bad "[51] port_listening awk 回归了提前 exit(pipefail 下 SIGPIPE 假失败)"; S51_BAD=1; }
grep -A12 "^port_listening()" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" | pipe_has "exit_found=1 }" || { bad "[51] port_listening awk 全量消费写法丢失"; S51_BAD=1; }
grep -Fq 'grep -Fq "${ROOT}"' "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" || { bad "[51] stop 脚本丢了工作区守卫(会误杀第二份 checkout)"; S51_BAD=1; }
grep -q "sleep 0.1" "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" || { bad "[51] stop 脚本 0.1s 轮询丢失"; S51_BAD=1; }
grep -v '^[[:space:]]*#' "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" | pipe_has -E '^[[:space:]]*sleep 1([[:space:]]|$)' && { bad "[51] stop 脚本回归整秒 sleep"; S51_BAD=1; }
grep -A1 "if !trusted_runtime {" "${S51_MAIN}" | pipe_has "prepare_runtime_dir" || { bad "[51] start_runtime 的 prepare_runtime_dir 失去 !trusted_runtime 守卫(冷缓存全树遍历会卡 36%)"; S51_BAD=1; }
grep -q '正在准备启动环境' "${S51_MAIN}" || { bad "[51] start_runtime 入口缺 indeterminate 进度(重活前进度会冻在 36%)"; S51_BAD=1; }
grep -q "'lsof', '-nP'" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py" || { bad "[51] webchartsrv.py 的 lsof 回退缺 -nP(DNS 反查会超 timeout 假阴性)"; S51_BAD=1; }
# 首启稳定性 (2026-06-12 安装包卡死根治后增):
S51_PROBE_NOPROXY="$(grep -cE "curl -s --noproxy '\\*'" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" || true)"
[ "${S51_PROBE_NOPROXY}" -ge 2 ] || { bad "[51] start 脚本探测 curl 缺 --noproxy '*'(应≥2 处:chart+backend,代理环境会卡首启)"; S51_BAD=1; }
grep -q "ProxyHandler({})" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" || { bad "[51] start 脚本 urllib 回退缺禁代理 opener(代理环境会卡首启)"; S51_BAD=1; }
grep -Eq 'port_listening "\$\{CHART_PORT\}" && port_listening "\$\{BACKEND_PORT\}" *; *then' "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" && { bad "[51] 等待循环回归 netstat 端口硬闸(解析失败会挡死已就绪服务)"; S51_BAD=1; }
grep -q 'command.env_remove(proxy_var)' "${S51_MAIN}" || { bad "[51] main.rs 未在 spawn 脚本前 env_remove 代理变量"; S51_BAD=1; }
# 共享运行环境只给安装者写:整树对所有账户可写 = 同机任一账户都能改启动脚本 / 引擎 / 页面,别的账户打开星阙就以他的身份执行。
#   postinstall 把共享树归还安装者并收 go-w;壳层新树落成后同样收 go-w;更新助手把根 chown 给发起更新的账户;
#   多账户机上的其他账户只读加载:pid 文件落各自缓存目录([pid-dir] 段,壳层预停检查同规则)、jar 用随包那份、要换版本改道到自己的用户目录。
S51_PI="${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template"
S51_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
S51_STOP="${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh"
grep -v '^[[:space:]]*#' "${S51_PI}" | pipe_has 'a+rw' && { bad "[51] postinstall 回归了把共享树放开给所有账户写(a+rw*)"; S51_BAD=1; }
grep -Fq '/bin/chmod -R u+rwX,go+rX,go-w "${SHARED_ROOT}"' "${S51_PI}" || { bad "[51] postinstall 缺 seal_shared_root 的收权限(u+rwX,go+rX,go-w)"; S51_BAD=1; }
grep -Fq '/usr/sbin/chown -R "${SHARED_OWNER_UID}" "${SHARED_ROOT}"' "${S51_PI}" || { bad "[51] postinstall 缺共享树归还安装者(chown)"; S51_BAD=1; }
[ "$(grep -c '^[[:space:]]*seal_shared_root[[:space:]]*$' "${S51_PI}")" -ge 6 ] || { bad "[51] postinstall 收尾路径少了 seal_shared_root(应 ≥6 处)"; S51_BAD=1; }
grep -v '^[[:space:]]*//' "${S51_PRODALL}" | pipe_has 'a+rwX' && { bad "[51] main.rs 回归了 a+rwX(新树落成 / 更新助手放开共享树)"; S51_BAD=1; }
grep -Fq 'const SHARED_TREE_CHMOD: &str = "u+rwX,go+rX,go-w";' "${S51_MAIN}" || { bad "[51] main.rs 缺 SHARED_TREE_CHMOD 收权限口径"; S51_BAD=1; }
grep -qF 'seal_shared_tree_permissions(&final_runtime);' "${S51_MAIN}" && grep -qF 'seal_shared_tree_permissions(&current);' "${S51_MAIN}" || { bad "[51] 全量解压 / 增量对换两处落树后缺 seal_shared_tree_permissions(两处调用点各一锚)"; S51_BAD=1; }
grep -Fq 'from_mode(0o666)' "${S51_PRODALL}" && { bad "[51] main.rs 出现 0o666(预检标记 / 手术锁不得对所有账户可写)"; S51_BAD=1; }
grep -Fq '.mode(0o666)' "${S51_PRODALL}" && { bad "[51] 手术锁文件回归 0o666"; S51_BAD=1; }
# 读面判别力自证:同文件测试模块里的 0o666 夹具读不到(不误红)、独立子模块产品代码里的 0o666 读得到(不漏扫)
s51_tmp="$(mktemp -d "${PF_TMP}/s51_tmp.XXXXXX")"; mkdir -p "${s51_tmp}/Horosa_Desktop_Installer/src-tauri/src"
printf 'fn real() {}\n#[cfg(test)]\nmod fixture_tests {\n    fn f() { let s = "}"; std::fs::Permissions::from_mode(0o666); }\n}\n' > "${s51_tmp}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
printf 'pub fn write_token() { std::fs::Permissions::from_mode(0o666); }\n' > "${s51_tmp}/Horosa_Desktop_Installer/src-tauri/src/mcp_server.rs"
[ "$(grep -cF 'fn f()' "$(pf_shell_rs_prod_all "${s51_tmp}")")" = "0" ] && [ "$(grep -cF 'from_mode(0o666)' "$(pf_shell_rs_prod_all "${s51_tmp}")")" = "1" ] \
  && [ "$(grep -cF 'from_mode(0o666)' "$(pf_shell_rs_tests "${s51_tmp}")")" = "1" ] && [ "$(grep -cF 'fn real()' "$(pf_shell_rs_prod "${s51_tmp}")")" = "1" ] \
  || { bad "[51] 壳源码产品 / 测试读面判别力自证失败(同文件测试夹具被算成产品,或独立子模块产品代码漏扫)"; S51_BAD=1; }
# 拆分器跑不起来时必须失败关闭:读面返回不存在的路径(正锚读不到 → 红)且记一笔失败(段收尾判红;反锚读空面会整类判绿)
S51_FAILREC="${s51_tmp}/rs_split.failed"
S51_FP="$(PF_RS_SPLIT="${s51_tmp}/no_such_splitter.py"; PF_RS_SPLIT_FAIL="${S51_FAILREC}"; pf_shell_rs_prod_all "${s51_tmp}")"
{ [ ! -e "${S51_FP}" ] && [ -s "${S51_FAILREC}" ]; } \
  || { bad "[51] 拆分器跑不起来时壳源码读面没有失败关闭(返回了可读的空面 / 没记失败):「产品代码里不许出现 X」的反锚会整类判绿"; S51_BAD=1; }
rm -rf "${s51_tmp}"
grep -q 'fn install_roots_for_decisions' "${S51_MAIN}" || { bad "[51] 只读账户「替换共享」改道到用户目录的判据丢失"; S51_BAD=1; }
grep -Fq 'exit 73\nfi\nseal_shared_runtime || true\nmark_update_complete' "${S51_MAIN}" || { bad "[51] 应用更新助手收尾不再收共享运行环境权限(早先安装包留下的 root 所有、所有账户可写的树没人收)"; S51_BAD=1; }
grep -v '^[[:space:]]*#' "${S51_START}" | pipe_has 'chmod a+rw' && { bad "[51] start 脚本回归 chmod a+rw(jar 对所有账户可写)"; S51_BAD=1; }
for S51_SH in "${S51_START}" "${S51_STOP}"; do
  grep -q '^# \[pid-dir:begin\]' "${S51_SH}" || { bad "[51] $(basename "${S51_SH}") 缺 [pid-dir] 段(只读账户的 pid 文件无处落)"; S51_BAD=1; }
done
grep -q 'fn runtime_pid_dir_for' "${S51_MAIN}" || { bad "[51] 壳层预停检查缺与脚本同规则的 pid 目录"; S51_BAD=1; }
for S51_T in postinstall_seals_shared_root_for_installing_user_only pid_dir_rule_matches_start_and_stop_scripts shared_tree_seal_leaves_write_to_owner_only update_helper_seals_shared_runtime_even_without_runtime_update; do
  grep -q "fn ${S51_T}" "${S51_TESTS}" || { bad "[51] 缺 cargo 用例 ${S51_T}"; S51_BAD=1; }
done
[ "${S51_BAD}" = "0" ] && ok "[51] 退出 detached+去重 / 端口检查 netstat 化 / 探测防代理 / http 直判就绪 / 共享树只属主可写 全在位"
}

seg_71() {
# [${PF_NO}] 性能资产护栏:exploded/CDS 启动、请求去重、前端分包、pyc 预编译、启动骨架、计算缓存面。
S71_BAD=0
S71_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
S71_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh"
S71_UMIRC="${REPO_ROOT}/Horosa-Web/astrostudyui/.umirc.js"
S71_DEDUPE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/requestDedupe.js"
S71_REQ="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/request.js"
S71_EJS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/document.ejs"
S71_HELPER="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/helper/AstroHelper.java"
echo "[${PF_NO}] 性能资产(exploded/CDS·分包·去重·pyc·骨架屏·计算缓存面)"
grep -q "JAVA_EXPLODED_MODE" "${S71_START}" 2>/dev/null || { bad "[${PF_NO}] start 脚本缺 exploded 启动分支"; S71_BAD=1; }
grep -q "maybe_train_cds_background" "${S71_START}" 2>/dev/null || { bad "[${PF_NO}] start 脚本缺 CDS 自训练"; S71_BAD=1; }
grep -q "boot-exploded" "${S71_PKG}" 2>/dev/null || { bad "[${PF_NO}] 打包脚本缺 exploded 布局"; S71_BAD=1; }
grep -q "compileall" "${S71_PKG}" 2>/dev/null || { bad "[${PF_NO}] 打包脚本缺 pyc 预编译"; S71_BAD=1; }
grep -q "astropy/__init__.py" "${S71_PKG}" 2>/dev/null && { bad "[${PF_NO}] 打包脚本引用已删除的 astropy/__init__.py(包名遮蔽)"; S71_BAD=1; }
grep -q "splitChunks" "${S71_UMIRC}" 2>/dev/null || { bad "[${PF_NO}] .umirc 缺 splitChunks 分包"; S71_BAD=1; }
grep -q "ContextReplacementPlugin" "${S71_UMIRC}" 2>/dev/null || { bad "[${PF_NO}] .umirc 缺 moment locale 裁剪(须 ContextReplacement 保 zh-cn,禁 IgnorePlugin)"; S71_BAD=1; }
[ -f "${S71_DEDUPE}" ] || { bad "[${PF_NO}] 缺 requestDedupe.js"; S71_BAD=1; }
grep -q "dedupeEligible" "${S71_REQ}" 2>/dev/null || { bad "[${PF_NO}] request.js 未接去重层"; S71_BAD=1; }
grep -q "predict/dice" "${S71_DEDUPE}" 2>/dev/null || { bad "[${PF_NO}] 去重层缺 dice 随机排除(缓存随机端点=功能错误)"; S71_BAD=1; }
grep -q "horosa-boot-splash" "${S71_EJS}" 2>/dev/null || { bad "[${PF_NO}] document.ejs 缺启动骨架"; S71_BAD=1; }
grep -q "return request(Acg, params)" "${S71_HELPER}" 2>/dev/null || { bad "[${PF_NO}] getAcg 未走缓存"; S71_BAD=1; }
grep -q "return requestNoCache(Dice, params)" "${S71_HELPER}" 2>/dev/null || { bad "[${PF_NO}] 🔴 Dice 被缓存(随机端点缓存=功能错误)"; S71_BAD=1; }
grep -q "return requestNoCache(PlanetariumState, params)" "${S71_HELPER}" 2>/dev/null || { bad "[${PF_NO}] 🔴 PlanetariumState 被缓存(实时端点)"; S71_BAD=1; }
[ "${S71_BAD}" = "0" ] && ok "[${PF_NO}] 性能资产 全在位" || bad "[${PF_NO}] 性能资产 有缺失"
}

seg_73() {
# ============================================================================
# [${PF_NO}] 性能资产·二批(瘦身/启动门/恒星memo/连接池/3D动态化)
# ============================================================================
S73_BAD=0
S73_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh"
S73_CHARTSRV="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
S73_SWE="${REPO_ROOT}/Horosa-Web/flatlib-ctrad2/flatlib/ephem/swe.py"
S73_HTTP="${REPO_ROOT}/Horosa-Web/astrostudysrv/boundless/src/main/java/boundless/net/http/HttpUriRequestHystrixCommand.java"
S73_IDX="${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/index.js"
echo "[${PF_NO}] 性能资产R2(瘦身排除表·启动门·恒星memo·连接池·3D动态化)"
grep -q "site-packages 重依赖排除表" "${S73_PKG}" 2>/dev/null || { bad "[${PF_NO}] 打包脚本缺重依赖排除表"; S73_BAD=1; }
grep -q "for heavy in streamlit pyarrow plotly altair pydeck" "${S73_PKG}" 2>/dev/null || { bad "[${PF_NO}] 排除表重依赖清单漂移(pandas 属 chunzi 真依赖不得入表)"; S73_BAD=1; }
grep -q "_ensure_streamlit_stub" "${REPO_ROOT}/Horosa-Web/astropy/websrv/kentang/kinastro_common.py" 2>/dev/null || { bad "[${PF_NO}] kinastro_common 缺 streamlit 桩(kentang adapter 在瘦身 runtime 会挂)"; S73_BAD=1; }
grep -E "name '\*\.pyc'" "${S73_PKG}" 2>/dev/null | pipe_has "delete" && { bad "[${PF_NO}] 打包清理行又包含 *.pyc -delete(会删光预编译产物)"; S73_BAD=1; }
[ -f "${REPO_ROOT}/Horosa-Web/astropy/tests/test_runtime_deps_slim.py" ] || { bad "[${PF_NO}] 缺瘦身哨兵测试"; S73_BAD=1; }
grep -q "STARTUP_GATE" "${S73_CHARTSRV}" 2>/dev/null || { bad "[${PF_NO}] webchartsrv 缺启动就绪门"; S73_BAD=1; }
grep -q "HOROSA_PY_WARMUP_SYNC" "${S73_CHARTSRV}" 2>/dev/null || { bad "[${PF_NO}] 启动门缺同步回退 kill-switch"; S73_BAD=1; }
grep -q "_fixstarUtCached" "${S73_SWE}" 2>/dev/null || { bad "[${PF_NO}] flatlib 缺恒星 memo"; S73_BAD=1; }
grep -q "_sidCtxKey" "${S73_SWE}" 2>/dev/null || { bad "[${PF_NO}] 恒星 memo 缓存键缺 sidereal 语境(跨制污染风险)"; S73_BAD=1; }
grep -q "PoolingHttpClientConnectionManager" "${S73_HTTP}" 2>/dev/null || { bad "[${PF_NO}] Java 出站客户端缺连接池"; S73_BAD=1; }
grep -q "AstroChartMain3D = lazyPreloadable" "${S73_IDX}" 2>/dev/null || { bad "[${PF_NO}] 3D 星盘未动态化(回流主包)"; S73_BAD=1; }
[ "${S73_BAD}" = "0" ] && ok "[${PF_NO}] 性能资产R2 全在位" || bad "[${PF_NO}] 性能资产R2 有缺失"
}

seg_92() {
# 92. runtime 自包含:pip editable/direct_url 工件内嵌构建机绝对路径,随 runtime tar 发出
#     即不自包含(import 链依赖 PYTHONPATH 先于 meta_path 末位 finder 才不炸)。四面锚:
#     staging 零残留 + .pth 零绝对路径 + 打包脚本 fail-closed 净化在位 + flatlib 导入源随包;
#     dist 已有 runtime/py-runtime tar 时清单亦须零残留(扫过且 tar 未变则记号免重扫)。
echo "[92] runtime 自包含(editable/direct_url 零残留)"
S92_BAD=0
S92_SP="${REPO_ROOT}/runtime/mac/python/lib/python3.12/site-packages"
if [ -d "${S92_SP}" ]; then
  S92_N="$(find "${S92_SP}" \( -name 'direct_url.json' -o -name '__editable__*' \) 2>/dev/null | wc -l | tr -d ' ' || true)"
  [ "${S92_N}" = "0" ] || { bad "[92] staging site-packages 残留 editable/direct_url ${S92_N} 个"; S92_BAD=1; }
  S92_P="$(grep -l '/Users/' "${S92_SP}"/*.pth 2>/dev/null | wc -l | tr -d ' ' || true)"
  [ "${S92_P}" = "0" ] || { bad "[92] staging .pth 含构建机绝对路径 ${S92_P} 个"; S92_BAD=1; }
else
  warn "[92] runtime staging 不在本机,跳过实物核(脚本面锚照核)"
fi
grep -q "自包含净化" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh" || { bad "[92] 打包脚本缺自包含净化守卫"; S92_BAD=1; }
[ -f "${REPO_ROOT}/Horosa-Web/flatlib-ctrad2/flatlib/__init__.py" ] || { bad "[92] flatlib 导入源(flatlib-ctrad2)缺失"; S92_BAD=1; }
for S92_T in "${REPO_ROOT}/Horosa_Desktop_Installer/dist/horosa-runtime-macos-arm64.tar.gz" \
             "${REPO_ROOT}/Horosa_Desktop_Installer/dist/components/horosa-comp-py-runtime-macos-arm64.tar.gz"; do
  [ -f "${S92_T}" ] || continue
  S92_MARK="${S92_T}.selfcontain-ok"
  if [ -f "${S92_MARK}" ] && [ "${S92_MARK}" -nt "${S92_T}" ]; then
    continue
  fi
  S92_TN="$(tar -tzf "${S92_T}" 2>/dev/null | grep -c -E '__editable__|direct_url\.json' || true)"
  if [ "${S92_TN}" = "0" ]; then
    touch "${S92_MARK}" 2>/dev/null || true
  else
    bad "[92] $(basename "${S92_T}") 清单含 editable/direct_url 残留 ${S92_TN} 条(守卫前的旧产物,须重打)"; S92_BAD=1
  fi
done
[ "${S92_BAD}" = "0" ] && ok "[92] runtime 自包含 全绿"
}

seg_93() {
# 93. 旧系统内核兼容(桌面包下限 macOS 12.0 = Safari 15.0)。下限表与判据的单一出处:astrostudyui/scripts/legacy-engine-floor.js
#     (脚本语法:正则后行断言 / v 标志 / 修饰组 / 类静态块 → 整份脚本解析失败;选择器::has / :focus-visible 与普通选择器同列 → 整条丢弃;
#      声明值:color-mix / overflow-wrap:anywhere … 无旧内核回退 → 整条丢弃;:has 每条规则须有回退类同义规则,类由兼容层维护)。
#     ① 兼容层在位且最先执行 ② 判据自证(每条判据一红一绿,含 :has 三个变异向量)③ 源码过下限(脚本 + 每个 .less 现编后的样式)
#     ④ 产物过下限(dist-file 在场时:全部脚本 + 全部样式,第三方包带进来的也抓)⑤ 构建脚本收尾跑产物判据 ⑥ 合同测试在位且没被关。
echo "[93] 旧系统内核兼容(下限表 + 产物判据)"
S93_BAD=0
S93_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S93_COMPAT="${S93_UI}/src/utils/legacyWebkitCompat.js"
S93_FLOOR="${S93_UI}/scripts/legacy-engine-floor.js"
S93_LOG="$(mktemp "${PF_TMP}/s93_log.XXXXXX")"
{ [ -f "${S93_COMPAT}" ] && grep -q "selector(:has(\*))" "${S93_COMPAT}"; } || { bad "[93] legacyWebkitCompat 缺失或缺 :has 探测"; S93_BAD=1; }
grep -q "legacyWebkitCompat" "${S93_UI}/src/global.js" || { bad "[93] global.js 未接线兼容层(必须最先执行)"; S93_BAD=1; }
if [ ! -f "${S93_FLOOR}" ]; then
  bad "[93] 缺下限表与判据 scripts/legacy-engine-floor.js"; S93_BAD=1
else
  for S93_MODE in --self-test --src; do
    if ! (cd "${S93_UI}" && node "${S93_FLOOR}" "${S93_MODE}") > "${S93_LOG}" 2>&1; then
      bad "[93] legacy-engine-floor ${S93_MODE} 不过:$(head -c 1500 "${S93_LOG}" | tr '\n' ' ')"; S93_BAD=1
    fi
  done
  if [ -d "${S93_UI}/dist-file" ]; then
    if ! (cd "${S93_UI}" && node "${S93_FLOOR}" --dist dist-file) > "${S93_LOG}" 2>&1; then
      bad "[93] dist-file 不过旧内核下限(重建前端或修源码):$(head -c 1500 "${S93_LOG}" | tr '\n' ' ')"; S93_BAD=1
    fi
  fi
fi
for S93_SCRIPT in build build:file; do
  S93_LINE="$(node -e 'const p=require(process.argv[1]);process.stdout.write(String((p.scripts||{})[process.argv[2]]||""))' "${S93_UI}/package.json" "${S93_SCRIPT}" 2>/dev/null || true)"
  case "${S93_LINE}" in
    *"legacy-engine-floor.js --dist"*) ;;
    *) bad "[93] package.json 的 ${S93_SCRIPT} 收尾没跑 legacy-engine-floor.js --dist(构建出不过下限的产物不会被当场拦下)"; S93_BAD=1 ;;
  esac
done
for S93_T in legacyEngineFloor legacyWebkitCompat splitAfterPunct; do
  S93_TF="${S93_UI}/src/utils/__tests__/${S93_T}.test.js"
  [ -f "${S93_TF}" ] || { bad "[93] 缺合同测试 ${S93_T}.test.js"; S93_BAD=1; continue; }
  pf_test_disabled "${S93_TF}" && { bad "[93] ${S93_T}.test.js 里有被跳过 / 独占的用例"; S93_BAD=1; }
done
[ "${S93_BAD}" = "0" ] && ok "[93] 旧系统内核兼容 全在位(判据自证 + 源码 + 产物)"
}

seg_96() {
# 96. web 一键启动链(OneClick 家族):启停约定散在多文件而此前零门覆盖,
#     单侧改动即会静默漂移(pid 命名断裂=停服漏杀)。守四面:全家族语法 / pid 约定跨文件互锚 /
#     历史断裂回归钉 / 入口健壮化与文档在位。动启停约定必须保本哨兵绿(AGENTS.md 铁律)。
echo "[96] web 一键启动链"
S96_BAD=0
for S96_F in \
  "${REPO_ROOT}/Horosa_OneClick_Mac.command" \
  "${REPO_ROOT}/Horosa_Stop_Mac.command" \
  "${REPO_ROOT}/tools/mac/Horosa_Local.command" \
  "${REPO_ROOT}/tools/mac/startup_ladder.sh" \
  "${REPO_ROOT}/scripts/mac/bootstrap_and_run.sh" \
  "${REPO_ROOT}/scripts/mac/self_check_horosa.sh" \
  "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" \
  "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh"; do
  if [ ! -f "${S96_F}" ]; then
    bad "[96] 家族文件缺失: ${S96_F#"${REPO_ROOT}"/}"; S96_BAD=1; continue
  fi
  bash -n "${S96_F}" 2>/dev/null || { bad "[96] 语法错误: ${S96_F#"${REPO_ROOT}"/}"; S96_BAD=1; }
done
S96_LOCAL="${REPO_ROOT}/tools/mac/Horosa_Local.command"
S96_STOP="${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh"
S96_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
grep -q '\.horosa_web\.\${WEB_PORT}\.pid' "${S96_LOCAL}" || { bad "[96] Local 缺 web pid 端口后缀"; S96_BAD=1; }
grep -q '\.horosa_web\.\${WEB_PORT}\.pid' "${S96_STOP}" || { bad "[96] stop 缺 web pid 端口后缀"; S96_BAD=1; }
grep -q '\.horosa_py\.\${CHART_PORT}\.pid' "${S96_START}" || { bad "[96] start 缺 py pid 端口后缀"; S96_BAD=1; }
grep -q '\.horosa_py\.\${CHART_PORT}\.pid' "${S96_STOP}" || { bad "[96] stop 缺 py pid 端口后缀"; S96_BAD=1; }
grep -q 'get_listener_pids' "${S96_LOCAL}" && { bad "[96] Local 回潮未定义函数 get_listener_pids"; S96_BAD=1; }
grep -q 'port_listener_pids' "${S96_LOCAL}" || { bad "[96] Local 缺 port_listener_pids"; S96_BAD=1; }
grep -q 'lsof -tiTCP' "${S96_LOCAL}" && { bad "[96] Local 回潮全表扫描 lsof(卡死类,已封杀)"; S96_BAD=1; }
grep -q '项目完整性检查' "${REPO_ROOT}/Horosa_OneClick_Mac.command" || { bad "[96] OneClick 缺完整性检查"; S96_BAD=1; }
grep -q 'HOROSA_STOP_ALL' "${REPO_ROOT}/Horosa_Stop_Mac.command" || { bad "[96] Stop 入口缺 STOP_ALL"; S96_BAD=1; }
grep -q 'HOROSA_STOP_ALL' "${S96_STOP}" || { bad "[96] stop 脚本缺 STOP_ALL 模式"; S96_BAD=1; }
grep -q 'download_with_fallback' "${REPO_ROOT}/scripts/mac/bootstrap_and_run.sh" || { bad "[96] bootstrap 缺镜像回退"; S96_BAD=1; }
grep -q 'HOROSA_SKIP_DB_SETUP:-1' "${REPO_ROOT}/scripts/mac/bootstrap_and_run.sh" || { bad "[96] bootstrap DB 默认未跳过"; S96_BAD=1; }
grep -q '网页版一键启动' "${REPO_ROOT}/README.md" || { bad "[96] README 缺一键启动教程"; S96_BAD=1; }
[ -f "${REPO_ROOT}/docs/WEB_LOCAL_LAUNCH.md" ] || { bad "[96] 缺 WEB_LOCAL_LAUNCH.md"; S96_BAD=1; }
[ "${S96_BAD}" = "0" ] && ok "[96] web 一键启动链 全在位"
}

seg_190() {
# ── [190] R4-B7 渲染批资产锚(convert memo/图守卫/双提交合一/弹窗短路/子页签冻结) ──
# 病史:R10 实测四靶点(三式闪帧/659 行弹窗白建/无关状态抖动)+ 同型「表新盘旧」。
echo "== [190] R4-B7 渲染批资产锚 =="
S190_BAD=0
S190_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
# C15:convertToArray memo(五处 useMemo,身份稳定供下游 memo)
grep -aq "horosa_convert_memo_v1" "${S190_UI}/src/pages/index.js" 2>/dev/null || { bad "[190] 🔴 convertToArray memo 标记缺失"; S190_BAD=1; }
S190_CM=$(grep -ac "React.useMemo(()=>convertToArray(" "${S190_UI}/src/pages/index.js" 2>/dev/null); S190_CM=${S190_CM:-0}
[ "${S190_CM}" -ge 5 ] || { bad "[190] 🔴 convertToArray useMemo 不足五处(现 ${S190_CM}——数组引用每 render 新建,下游 memo 全 miss)"; S190_BAD=1; }
# C17:七政盘 svg resize 守卫(隐藏期数据更新→切回表新盘旧)
grep -aq "watchChartSvgResize(this.state.chartid, this.drawChart)" "${S190_UI}/src/components/guolao/GuoLaoChart.js" 2>/dev/null || { bad "[190] 🔴 GuoLaoChart svg resize 守卫缺失(同型回潮)"; S190_BAD=1; }
# C16 靶①:三式重算双提交合一(盘结果与 loading:false 同帧)
grep -aq "payload.commitPatch" "${S190_UI}/src/components/sanshi/SanShiUnitedMain.js" 2>/dev/null || { bad "[190] 🔴 三式 commitPatch 防抖透传被拆"; S190_BAD=1; }
grep -aq '\.\.\.(commitPatch || null),' "${S190_UI}/src/components/sanshi/SanShiUnitedMain.js" 2>/dev/null || { bad "[190] 🔴 三式双提交合一被拆(新盘+转圈中间帧回潮)"; S190_BAD=1; }
# C16 靶②:择日两弹窗「从未打开过」粘性短路(~650 行元素树白建)
for S190_F in "src/components/zeri/ConditionBuilderModal.js" "src/components/zeri/QimenZeriWorkbench.js"; do
	grep -aq "if(!everOpenRef.current){ return null; }" "${S190_UI}/${S190_F}" 2>/dev/null || { bad "[190] 🔴 ${S190_F} 粘性短路缺失(弹窗关着每 render 白建元素树)"; S190_BAD=1; }
done
# C16-⑤:FreezeSubTab 三技法接线(六壬 8 面板/奇门 5 面板/七政 map 全面板)
S190_LR=$(grep -ac "<FreezeSubTab active={activeTabKey ===" "$(pf_src_set "${S190_UI}/src/components/lrzhan/LiuRengMain.js")" 2>/dev/null); S190_LR=${S190_LR:-0}
[ "${S190_LR}" -ge 8 ] || { bad "[190] 🔴 六壬右栏 FreezeSubTab 不足 8 面板(现 ${S190_LR})"; S190_BAD=1; }
S190_DJ=$(grep -ac "<FreezeSubTab active={panelTab ===" "${S190_UI}/src/components/dunjia/DunJiaMain.js" 2>/dev/null); S190_DJ=${S190_DJ:-0}
[ "${S190_DJ}" -ge 5 ] || { bad "[190] 🔴 奇门右栏 FreezeSubTab 不足 5 面板(现 ${S190_DJ})"; S190_BAD=1; }
grep -aq "<FreezeSubTab active={active === item.key}>" "$(pf_src_set "${S190_UI}/src/components/guolao/GuoLaoChartMain.js")" 2>/dev/null || { bad "[190] 🔴 七政右栏 FreezeSubTab map 接线缺失"; S190_BAD=1; }
for S190_F in "src/components/lrzhan/LiuRengMain.js" "src/components/dunjia/DunJiaMain.js" "src/components/guolao/GuoLaoChartMain.js"; do
	pf_imports "${S190_UI}/${S190_F}" "import { FreezeSubTab } from '../comp/FreezeInactive';" || { bad "[190] 🔴 ${S190_F} FreezeSubTab import 缺失"; S190_BAD=1; }
done
[ "${S190_BAD}" = "0" ] && ok "[190] R4-B7 渲染批资产(convert memo ${S190_CM} 处+七政守卫+三式同帧+双弹窗短路+子页签冻结 ${S190_LR}/${S190_DJ}/map)全在位"
}

seg_290() {
# [${PF_NO}] 响应 JSON 快径由两个服务扩到进程级(全部挂载服务共用真 jsonpickle 模块;同判据、同回退,逐字节相同),
#       蠢子数诗词库按进程只建一次。锚住安装点 / 原函数取回 / 缺省参数 / 缓存入口与测试(2026-09-26)。
echo "[${PF_NO}] 响应 JSON 快径进程级 + 蠢子数诗词库按进程只建一次"
S290_BAD=0
S290_W="${REPO_ROOT}/Horosa-Web/astropy"
for S290_F in tests/test_fastjson_global.py tests/test_chunzi_db_memo.py tests/test_perf_r5_batch1.py; do
  [ -s "${S290_W}/${S290_F}" ] || { bad "[${PF_NO}] 🔴 缺测试 ${S290_F}"; S290_BAD=1; }
done
grep -q "_install_fast_json_global(jsonpickle)" "${S290_W}/websrv/webchartsrv.py" 2>/dev/null \
  && grep -q "def install_global(jsonpickle_module):" "${S290_W}/websrv/fastjson.py" 2>/dev/null \
  && grep -q "encode._horosa_orig = orig" "${S290_W}/websrv/fastjson.py" 2>/dev/null \
  && grep -q "def original_encode(jsonpickle_module):" "${S290_W}/websrv/fastjson.py" 2>/dev/null || { bad "[${PF_NO}] 🔴 进程级 JSON 快径安装点 / 原函数取回口缺失"; S290_BAD=1; }
grep -q "def encode(self, obj, unpicklable=True, \*\*kw):" "${S290_W}/websrv/fastjson.py" 2>/dev/null || { bad "[${PF_NO}] 🔴 快径 shim 的 unpicklable 缺省须与真 jsonpickle 同为 True"; S290_BAD=1; }
grep -q "FJ.original_encode(shim)" "${S290_W}/tests/test_perf_r5_batch1.py" 2>/dev/null || { bad "[${PF_NO}] 🔴 快径对拍基准须取原 encode"; S290_BAD=1; }
grep -q "czs = _chunzi_db()" "${S290_W}/websrv/webchunzisrv.py" 2>/dev/null && grep -q "HOROSA_CHUNZI_DB_MEMO" "${S290_W}/websrv/webchunzisrv.py" 2>/dev/null \
  || { bad "[${PF_NO}] 🔴 蠢子数又回到每请求新建诗词库"; S290_BAD=1; }
[ "${S290_BAD}" = "0" ] && ok "[${PF_NO}] 进程级 JSON 快径(安装点 / 原函数 / 缺省参数)+ 蠢子数诗词库缓存 + 三份测试在场"
}

seg_292() {
# [${PF_NO}] 生辰节气卯时上升求解按黄经(byLon=1)在高纬可永不收敛(请求不返回、线程空转)。牛顿迭代设上限
#       (5 万步,约 1.4 s)+ 超限退到按赤经并在结果里注明 maoFallback;收敛的输入逐字节不变。锚住防回潮(2026-09-27)。
echo "[${PF_NO}] 卯时上升求解迭代上限 + 不收敛回退"
S292_BAD=0
S292_P="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/jieqi/BirthJieQi.py"
S292_T="${REPO_ROOT}/Horosa-Web/astropy/tests/test_birthjieqi_mao_fallback.py"
[ -s "${S292_T}" ] || { bad "[${PF_NO}] 🔴 缺回归测试 test_birthjieqi_mao_fallback.py"; S292_BAD=1; }
grep -qE "^_ASC_APPROACH_MAX_ITER = [0-9]+" "${S292_P}" 2>/dev/null \
  && [ "$(grep -c "if it > _ASC_APPROACH_MAX_ITER:" "${S292_P}" 2>/dev/null)" -ge 2 ] \
  && grep -q "self.maoFallback = 'byRA'" "${S292_P}" 2>/dev/null \
  && grep -q "res\['maoFallback'\] = self.maoFallback" "${S292_P}" 2>/dev/null || { bad "[${PF_NO}] 🔴 卯时上升求解又无迭代上限 / 缺不收敛回退(高纬黄经法会永久空转)"; S292_BAD=1; }
grep -q "test_previously_hanging_cases_return_and_fall_back_to_right_ascension" "${S292_T}" 2>/dev/null && grep -q "timeout=" "${S292_T}" 2>/dev/null \
  || { bad "[${PF_NO}] 🔴 回归测试须用子进程 + 超时跑此前不返回的用例"; S292_BAD=1; }
[ "${S292_BAD}" = "0" ] && ok "[${PF_NO}] 卯时上升求解迭代上限 + 按赤经回退 + 子进程限时回归测试在场"
}

seg_294() {
# [${PF_NO}] 星历表等端点同一请求里重复算同一 (天体, jd, 中心) 黄经。请求内 memo(astroextra.swe_lon;webchartsrv 请求工具
#       按服务前缀开启、请求结束清空),键含中心与站心坐标;输出逐字节不变。锚住防回潮(2026-09-27)。
echo "[${PF_NO}] 请求内黄经 memo"
S294_BAD=0
S294_A="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astropy/astrostudy/astroextra.py")"
S294_W="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
S294_T="${REPO_ROOT}/Horosa-Web/astropy/tests/test_swe_lon_memo.py"
[ -s "${S294_T}" ] || { bad "[${PF_NO}] 🔴 缺测试 test_swe_lon_memo.py"; S294_BAD=1; }
grep -q "key = (body, jd, c, topo)" "${S294_A}" 2>/dev/null && grep -q "memo = None   # 置点失败时" "${S294_A}" 2>/dev/null \
  && grep -q "HOROSA_SWE_LON_MEMO" "${S294_A}" 2>/dev/null || { bad "[${PF_NO}] 🔴 黄经 memo 键不全 / 站心置点失败未排除 / 缺开关"; S294_BAD=1; }
grep -q "cherrypy.tools.swe_lon_memo = cherrypy.Tool('before_handler', _swe_lon_memo_tool" "${S294_W}" 2>/dev/null \
  && grep -q "req.hooks.attach('on_end_request', ax.swe_lon_memo_end)" "${S294_W}" 2>/dev/null \
  && grep -q "ax.swe_lon_memo_end()   # 保险:非目标请求一律无 memo" "${S294_W}" 2>/dev/null || { bad "[${PF_NO}] 🔴 黄经 memo 请求工具未注册 / 未在请求结束清空"; S294_BAD=1; }
grep -q "test_memo_key_separates_center_and_topo_position" "${S294_T}" 2>/dev/null && grep -q "test_outputs_identical_memo_on_off_and_fewer_ephemeris_calls" "${S294_T}" 2>/dev/null \
  || { bad "[${PF_NO}] 🔴 测试缺「开关两档逐字节同 + 真少算」或「键分中心与站心坐标」"; S294_BAD=1; }
[ "${S294_BAD}" = "0" ] && ok "[${PF_NO}] 请求内黄经 memo(键 / 站心 / 请求工具 / 清空)+ 测试在场"
}

seg_83() {
# 83. 更新链下载/解压核(WS-1b/1c):续传协议+原生流式解压+kill-switch+回归测试+Range 发布哨兵
echo "[83] 断点续传下载核+原生流式解压"
S83_BAD=0
S83_MAIN="$(pf_shell_rs_prod)"
grep -q "fn download_resumable_once" "${S83_MAIN}" 2>/dev/null || { bad "[83] 下载核 download_resumable_once 缺位"; S83_BAD=1; }
grep -q "HOROSA_DOWNLOAD_NO_RESUME" "${S83_MAIN}" 2>/dev/null || { bad "[83] kill-switch HOROSA_DOWNLOAD_NO_RESUME 缺位"; S83_BAD=1; }
grep -q "RESUME_MAX_ATTEMPTS" "${S83_MAIN}" 2>/dev/null || { bad "[83] 续传次数封顶 RESUME_MAX_ATTEMPTS 缺位"; S83_BAD=1; }
grep -q '\.part\.meta' "${S83_MAIN}" 2>/dev/null || { bad "[83] .part.meta 续传元数据协议缺位"; S83_BAD=1; }
grep -q "resume_completes_via_range_206" "$(pf_shell_rs_tests)" 2>/dev/null || { bad "[83] 续传 206 回归测试缺位"; S83_BAD=1; }
grep -q 'r 0-1023' "${INSTALLER_ROOT}/scripts/verify_github_release_end_to_end.sh" 2>/dev/null || { bad "[83] e2e 缺 GitHub Range(206)发布实测哨兵"; S83_BAD=1; }
grep -q "fn extract_tar_gz_native_with" "${S83_MAIN}" 2>/dev/null || { bad "[83] 原生流式解压 extract_tar_gz_native_with 缺位"; S83_BAD=1; }
grep -q "HOROSA_EXTRACT_NATIVE" "${S83_MAIN}" 2>/dev/null || { bad "[83] kill-switch HOROSA_EXTRACT_NATIVE 缺位"; S83_BAD=1; }
grep -q "HOROSA_EXTRACT_CONCURRENCY" "${S83_MAIN}" 2>/dev/null || { bad "[83] 物化并发开关 HOROSA_EXTRACT_CONCURRENCY 缺位"; S83_BAD=1; }
grep -q "native_extract_parity_with_external_tar" "$(pf_shell_rs_tests)" 2>/dev/null || { bad "[83] 解压 parity 回归测试缺位"; S83_BAD=1; }
grep -q "native_extract_rejects_path_escape" "$(pf_shell_rs_tests)" 2>/dev/null || { bad "[83] 解压路径逃逸防护测试缺位"; S83_BAD=1; }
# 原生解压的符号链接逃逸防线(先建指向树外的链接、再经它写文件):链接目标按真实解析留在树内 / 写盘前父链无链接 / 收尾复核 /
#   不安全归档不回退外部 tar(外部 tar 照建指向树外的链接)
{ grep -qF 'if !symlink_target_within(dest, &rel, &target) {' "${S83_MAIN}" && grep -qF 'ensure_no_symlink_on_path(' "${S83_MAIN}" \
  && grep -qF 'for (rel, target) in &created_links {' "${S83_MAIN}" \
  && [ "$(grep -cF 'if is_archive_unsafe(&err) =>' "${S83_MAIN}")" -ge 2 ]; } || { bad "[83] 原生解压缺符号链接逃逸防线(链接目标 / 写盘父链 / 收尾复核 / 不安全不回退)"; S83_BAD=1; }
for S83_T in native_extract_rejects_write_through_symlink_to_outside_dir native_extract_rejects_symlink_targets_that_escape_dest native_extract_refuses_writes_through_in_tree_symlink_and_keeps_legit_links; do
  grep -q "fn ${S83_T}" "$(pf_shell_rs_tests)" 2>/dev/null || { bad "[83] 缺 cargo 用例 ${S83_T}"; S83_BAD=1; }
done
grep -q "tar_extract_external" "${S83_MAIN}" 2>/dev/null || { bad "[83] 外部 tar 回退路径缺位(native 出错须可退)"; S83_BAD=1; }
# 发布后端到端的安装根目录必须取自 release_config.sharedRootName(写死路径时,换了安装根的构建装到别处、脚本却去旧路径找 → 存在性判断静默失败)
S83_E2E="${INSTALLER_ROOT}/scripts/verify_github_release_end_to_end.sh"
if [ -f "${S83_E2E}" ]; then
  S83_N="$(grep -c "offline-target/Users/Shared/Horosa/" "${S83_E2E}" 2>/dev/null || true)"
  [ "${S83_N:-0}" -eq 0 ] || { bad "[83] e2e 又写死了安装根目录 /Users/Shared/Horosa(${S83_N} 处;安装根以 sharedRootName 为准)"; S83_BAD=1; }
  grep -qF "config.get('sharedRootName')" "${S83_E2E}" || { bad "[83] e2e 的安装根目录不再取自 release_config.sharedRootName"; S83_BAD=1; }
fi
[ "${S83_BAD}" = "0" ] && ok "[83] 下载核+解压核 协议/开关/测试/发布哨兵 全在位"
}

seg_284() {
echo "[${PF_NO}] 跨源请求头合同:前端 X-Horosa-* 请求头 ⊆ Java CORS 白名单(2026-09-25 真浏览器台架实抓)"
S284_BAD=0
S284_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/java/spacex/astrostudyboot/AstroStudyProgram.java"
S284_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S284_TEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/corsHeadersContract.test.js"
[ -f "${S284_TEST}" ] || { bad "[${PF_NO}] 合同测试缺席:corsHeadersContract.test.js"; S284_BAD=1; }
if [ -f "${S284_JAVA}" ] && [ -d "${S284_UI}" ]; then
  S284_RES="$(python3 - "${S284_JAVA}" "${S284_UI}" <<'PY284'
import os, re, sys
java = open(sys.argv[1], encoding='utf-8').read()
m = re.search(r'"cors\.supportedHeaders",\s*"([^"]+)"', java)
if not m:
    print('no-whitelist'); sys.exit(0)
allowed = set(h.strip().lower() for h in m.group(1).split(','))
used = set()
for root, dirs, files in os.walk(sys.argv[2]):
    dirs[:] = [d for d in dirs if d not in ('__tests__', 'node_modules') and not d.startswith('.umi')]
    for f in files:
        if not f.endswith(('.js', '.jsx', '.ts', '.tsx')):
            continue
        try:
            t = open(os.path.join(root, f), encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        q = chr(39) + chr(34) + chr(96)   # 三种引号;不写字面量,免 bash 3.2 在 $( ) 里数引号
        used |= set(re.findall('[' + q + '](X-Horosa-[A-Za-z0-9-]+)[' + q + ']', t))
missing = sorted(h for h in used if h.lower() not in allowed)
print(('ok:%d' % len(used)) if not missing else ('missing:' + ','.join(missing)))
PY284
)"
  case "${S284_RES}" in
    ok:*) : ;;
    *) bad "[${PF_NO}] 🔴 前端自定义请求头不在 CORS 白名单(桌面跨源预检 403 = 整站请求被浏览器拦下):${S284_RES}"; S284_BAD=1 ;;
  esac
else
  bad "[${PF_NO}] 🔴 缺 AstroStudyProgram.java 或前端 src"; S284_BAD=1
fi
[ "${S284_BAD}" = "0" ] && ok "[${PF_NO}] 前端 X-Horosa-* 请求头全部在 Java CORS 白名单(${S284_RES#ok:} 枚)+ 合同测试在场"
}

seg_285() {
echo "[${PF_NO}] 延迟初始化边界:XML 扫描组件里带静态初始化块的类必须显式 @Lazy(false) 或在已审白名单(2026-09-25 零降级自检实抓)"
S285_BAD=0
S285_SRV="${REPO_ROOT}/Horosa-Web/astrostudysrv"
S285_MVC="${S285_SRV}/astrostudyboot/src/main/resources/conf/spring-mvc.xml"
if [ -f "${S285_MVC}" ]; then
  S285_RES="$(python3 - "${S285_SRV}" "${S285_MVC}" <<'PY285'
import os, re, sys
srv, mvc = sys.argv[1], sys.argv[2]
xml = open(mvc, encoding="utf-8").read()
m = re.search(r"component-scan\s+base-package=\"([^\"]+)\"", xml)
if not m:
    print("no-scan-list"); raise SystemExit(0)
pkgs = [x.strip() for x in m.group(1).replace(chr(10), ",").split(",") if x.strip()]
# 已审白名单:静态块只填本类自己的静态状态、读启动后不变的属性(setAppServer 全仓零调用)
allow = {
    "boundless.spring.help.springcomp.RestResponseEntityExceptionHandler": "静态块只填本类两张日志过滤表",
    "spacex.astrostudy.controller.TokenController": "静态块只配置本类两个令牌管理器,静态方法调用即触发类初始化",
}
stereo = re.compile(r"^@(Controller|RestController|Service|Component|ControllerAdvice|RestControllerAdvice|Repository)\b", re.M)
bad, seen = [], 0
for mod in sorted(os.listdir(srv)):
    base = os.path.join(srv, mod, "src", "main", "java")
    if not os.path.isdir(base):
        continue
    for pkg in pkgs:
        root = os.path.join(base, *pkg.split("."))
        if not os.path.isdir(root):
            continue
        for dp, dn, fn in os.walk(root):
            for f in fn:
                if not f.endswith(".java"):
                    continue
                path = os.path.join(dp, f)
                src = open(path, encoding="utf-8", errors="replace").read()
                code = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
                code = re.sub(r"//[^\n]*", "", code)
                if not stereo.search(code):
                    continue
                if not re.search(r"\bstatic\s*\{", code):
                    continue
                seen += 1
                fqn = os.path.relpath(path, base)[:-5].replace(os.sep, ".")
                if "@Lazy(false)" in code or fqn in allow:
                    continue
                bad.append(fqn)
print(("ok:%d" % seen) if not bad else ("unreviewed:" + ",".join(sorted(set(bad)))))
PY285
)"
  case "${S285_RES}" in
    ok:*) : ;;
    *) bad "[${PF_NO}] 🔴 XML 扫描组件带静态初始化块却未审(桌面延迟初始化会把它挪到首次使用时;有进程级副作用的必须 @Lazy(false),自足的进白名单并写明理由):${S285_RES}"; S285_BAD=1 ;;
  esac
else
  bad "[${PF_NO}] 🔴 缺 spring-mvc.xml(组件扫描清单)"; S285_BAD=1
fi
grep -q "@Lazy(false)" "${S285_SRV}/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisMaterialService.java" 2>/dev/null || { bad "[${PF_NO}] 🔴 AIAnalysisMaterialService 缺 @Lazy(false)(静态块设置进程级表格解析阈值,Excel 导入依赖它在启动时生效)"; S285_BAD=1; }
[ "${S285_BAD}" = "0" ] && ok "[${PF_NO}] XML 扫描组件静态初始化块全部已审(${S285_RES#ok:} 个)+ AIAnalysisMaterialService 启动时创建"
}

seg_35() {
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
[ -f "${ST_WINDOC}" ] || { bad "[35] 缺 ${ST_WINDOC#"${REPO_ROOT}"/}(Windows 镜像 spec)"; ST35_BAD=1; }
# 前端静态服务器只服务前端目录之内的文件:请求行路径原样到达(不规范化),`..` / 编码点 / 符号链接出界都要拒
ST_MAIN="$(pf_shell_rs_prod)"
{ grep -qF 'if !static_rel_path_is_safe(&rel) {' "${ST_MAIN}" \
  && grep -qF 'let target = match resolve_static_target(&frontend_dir, canonical_root.as_deref(), &rel)' "${ST_MAIN}" \
  && grep -qF 'Ok(real) => real.starts_with(canonical_root),' "${ST_MAIN}" \
  && grep -qF 'fn static_server_refuses_traversal_requests()' "$(pf_shell_rs_tests)"; } \
  || { bad "[35] 🔴 前端静态服务器缺路径穿越防线(本机任意进程可经回环口读用户文件)"; ST35_BAD=1; }
[ "${ST35_BAD}" = "0" ] && ok "[35] StartupGate 挂载 + /healthz + HOROSA_READY + 127.0.0.1 绑定 + Windows 镜像清单 均在"
}

seg_177() {
# [${PF_NO}] 壳缩放链四层病理锁 —— 2026-07-31 真机彻查定案(主限天球时间轴被滚上去/底部露白):
#   ①layouts/app.js 内联 100vh 与 clientHeight 域劈叉(缩放≠1 差出可平移空间);
#   ②缩放注入走 localStorage 跨 origin 断链——唯一确定性通道=emit_ready 的 URL query
#     (shellZoom)+ init script 挂 __HOROSA_APPLY_SHELL_ZOOM(每 document 必挂);
#   ③取证探针(FORENSIC-TEMP)绝不入发版;④jest 守卫套件在位。
echo "[${PF_NO}] 壳缩放链四层病理锁(URL query 通道 + 100vh 禁令 + 探针剥离 + jest 守卫)"
S177_BAD=0
S177_MAIN_RS="$(pf_shell_rs_prod)"
S177_APP_JS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/layouts/app.js"
S177_GUARD="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/shellZoomGuard.test.js"
if grep -q "FORENSIC-TEMP" "${S177_MAIN_RS}"; then
    S177_BAD=1; bad "[${PF_NO}]③ main.rs 残留 FORENSIC-TEMP 取证探针 —— 硬编码缩放/采样代码禁入发版"
fi
if ! grep -q "shellZoom={zoom}" "${S177_MAIN_RS}"; then
    S177_BAD=1; bad "[${PF_NO}]② emit_ready 缺 shellZoom URL query 注入 —— 缩放回退到跨 origin 断链的 localStorage 通道"
fi
if ! grep -q "__HOROSA_APPLY_SHELL_ZOOM" "${S177_MAIN_RS}"; then
    S177_BAD=1; bad "[${PF_NO}]② init script 缺 __HOROSA_APPLY_SHELL_ZOOM —— 导航后缩放应用函数丢失"
fi
if [ "$(sed -e 's://.*$::' "${S177_APP_JS}" | grep -ac "100vh")" != "0" ]; then
    S177_BAD=1; bad "[${PF_NO}]① layouts/app.js 内联 100vh 回归 —— 域劈叉,缩放≠1 时底空+可平移空间复发"
fi
if [ ! -f "${S177_GUARD}" ]; then
    S177_BAD=1; bad "[${PF_NO}]④ jest 守卫 shellZoomGuard.test.js 缺失"
fi
# [${PF_NO}]⑤ 2026-09-17 用户实报(新机 Tahoe 缩放后天文馆底部大白边 / 预览左栏滚不到底):页面骨架 less 用 vh 定高 =
#   同一域劈叉的另一处漏网(layouts 早已禁,组件级没锁)。天文馆改 100% + grid-template-rows:minmax(0,1fr);此处锁住不回潮。
S177_PLAN_LESS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/planetarium/planetarium.less"
if [ -f "${S177_PLAN_LESS}" ]; then
    if [ "$(sed -e 's:/\*.*\*/::g' -e 's://.*$::' "${S177_PLAN_LESS}" | grep -acE '[0-9]+vh\b')" != "0" ]; then
        S177_BAD=1; bad "[${PF_NO}]⑤ planetarium.less 骨架高度回潮用 vh —— 壳缩放≠1 时底部白边 / 左栏滚不到底复发"
    fi
    if ! grep -q "grid-template-rows: minmax(0, 1fr)" "${S177_PLAN_LESS}"; then
        S177_BAD=1; bad "[${PF_NO}]⑤ planetarium.less 网格单行未钉死容器高(grid-template-rows: minmax(0, 1fr))—— 左栏内容长过容器即撑破行、栏内不可滚"
    fi
fi
# [${PF_NO}]⑥ 2026-09-17 用户在新机 Tahoe 的 APP 实报三族(天文馆底部白边 / 数据库页缩小留白放大被裁 / 合盘等放大后盘面被下端遮挡)定谳:
#   标准化 zoom 引擎下 vh/vw 按物理视口解析再被缩放、iframe 内页视口按物理尺寸计、getBoundingClientRect 已×z。
#   制度化:① src 全树(less/css/js,注释与测试除外)不得再出现裸 Nvh/Nvw,一律 calc(N * var(--horosa-lvh, 1vh));
#   ② 发布器 utils/layoutViewportVars.js 在位且 global.js 真调用 installLayoutViewportVars();
#   ③ 数据库内嵌页反缩放按实测决定(needsCounterZoom),不得按引擎/版本分支;④ jest 守卫两套在位。
S177_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S177_LVV="${S177_UI}/src/utils/layoutViewportVars.js"
S177_GLOBAL="${S177_UI}/src/global.js"
S177_ASTRODATA="${S177_UI}/src/components/astrodata/AstrodataPage.js"
if [ ! -f "${S177_LVV}" ]; then
    S177_BAD=1; bad "[${PF_NO}]⑥ 缺 utils/layoutViewportVars.js —— 全站 vh/vw 替身(布局视口 CSS 变量)发布器丢失"
fi
if [ -f "${S177_GLOBAL}" ] && [ "$(sed -e 's://.*$::' "${S177_GLOBAL}" | grep -ac "__installLayoutViewportVars();")" = "0" ]; then
    S177_BAD=1; bad "[${PF_NO}]⑥ global.js 未调用 installLayoutViewportVars() —— --horosa-lvw/--horosa-lvh 永不发布,全站 calc(N * var(--horosa-lvh, 1vh)) 退回 vh(缩放≠1 时留白/溢出复发)"
fi
if [ -d "${S177_UI}/src" ]; then
    # 整行匹配(不用 -o:要看到整行才能剔 var() 回落值与注释行);精判交给 jest viewportUnitsSourceGuard
    S177_RAW="$(grep -rnE '(^|[^A-Za-z0-9_.-])[0-9]+(\.[0-9]+)?(vh|vw)([^A-Za-z0-9_-]|$)' "${S177_UI}/src" --include='*.less' --include='*.css' --include='*.js' 2>/dev/null \
        | grep -v '__tests__' | grep -v 'var(--horosa-lv' | grep -v 'var(--lv' | grep -vE ':[0-9]+:[[:space:]]*(//|/\*|\*)' | wc -l | tr -d ' ')"
    if [ "${S177_RAW}" -gt 3 ]; then
        S177_BAD=1; bad "[${PF_NO}]⑥ src 里裸 vh/vw 命中 ${S177_RAW} 处(允许 ≤3 处行尾注释噪声)—— 有人把 vh/vw 写回骨架;跑 jest viewportUnitsSourceGuard 定位"
    fi
fi
if [ -f "${S177_ASTRODATA}" ] && ! grep -q "needsCounterZoom(" "${S177_ASTRODATA}"; then
    S177_BAD=1; bad "[${PF_NO}]⑥ AstrodataPage 缺 needsCounterZoom(实测判定 iframe 反缩放)—— 数据库页在标准化 zoom 引擎下缩小留白/放大被裁复发"
fi
for t in viewportUnitsSourceGuard layoutViewportVars; do
    [ -f "${S177_UI}/src/utils/__tests__/${t}.test.js" ] || { S177_BAD=1; bad "[${PF_NO}]⑥ jest 守卫 ${t}.test.js 缺失"; }
done
# [${PF_NO}]⑦ 2026-09-17 深夜 极档(0.7/1.8 + 页内换档)全页面巡检再抓七族的制度锁:
#   ① WebKit z≠1「内联盒按内容宽×z」缺陷的实测探针 utils/zoomInlineScaleBug.js 在位且 global.js 真调用 installZoomTextBugProbe();
#   ② app.less 有 html.horosa-zoom-textbug 的省略退 clip 规则 + textarea 关横滚;③ 盘面 CSS px 底线走 visualFloorPx(≥21 处,jest 站点表锁死);
#   ④ jest 守卫 visualFloorPx / zoomInlineScaleBug 在位;⑤ 页面主栅格不得把中列最小宽写回 minmax(≥480px,1fr)(1.8 档 960 布局宽必裁右栏)。
S177_ZTB="${S177_UI}/src/utils/zoomInlineScaleBug.js"
[ -f "${S177_ZTB}" ] || { S177_BAD=1; bad "[${PF_NO}]⑦ 缺 utils/zoomInlineScaleBug.js —— 省略号误判/占位符横滚的引擎缺陷探针丢失"; }
if [ -f "${S177_GLOBAL}" ] && [ "$(sed -e 's://.*$::' "${S177_GLOBAL}" | grep -ac "__installZoomTextBugProbe();")" = "0" ]; then
    S177_BAD=1; bad "[${PF_NO}]⑦ global.js 未调用 installZoomTextBugProbe() —— html.horosa-zoom-textbug 永不挂,1.8 档 \"2026\"→\"20…\" 复发"
fi
S177_LESS="$(pf_src_set "${S177_UI}/src/layouts/app.less")"
if [ -f "${S177_LESS}" ]; then
    grep -q "html.horosa-zoom-textbug" "${S177_LESS}" || { S177_BAD=1; bad "[${PF_NO}]⑦ app.less 缺 html.horosa-zoom-textbug 省略退 clip 规则"; }
    grep -q 'textarea:not(\[wrap="off"\])' "${S177_LESS}" || { S177_BAD=1; bad "[${PF_NO}]⑦ app.less 缺 textarea 关横滚规则(空输入框 1.8 档横向滚动条)"; }
    S177_GRIDMIN="$(grep -cE 'grid-template-columns:.*minmax\((4[89][0-9]|[5-9][0-9]{2})px, 1fr\)' "${S177_LESS}" | tr -d ' ')"
    if [ "${S177_GRIDMIN}" != "0" ]; then
        S177_BAD=1; bad "[${PF_NO}]⑦ app.less 有 ${S177_GRIDMIN} 条页面栅格把中列最小宽写回 ≥480px —— 1.8 档(960 布局宽)右栏必被裁,改 minmax(0, 1fr)"
    fi
fi
S177_VF="$(grep -rl 'visualFloorPx(' "${S177_UI}/src/components" --include='*.js' 2>/dev/null | grep -v __tests__ | wc -l | tr -d ' ')"
# 2026-09-18:三个推运页(赤纬 / 时段 / 主限表)改「100% 定高链」不再需要底线 → 21→18(与 visualFloorPx.test.js SITES 同源)
# 2026-10-24:金口诀盘改走设计盒(比设计尺寸小时整体等比缩小),撤掉 560 / 702 撑高底线 → 本仓 16 处
S177_VF_MIN=16
if [ "${S177_VF}" -lt "${S177_VF_MIN}" ]; then
    S177_BAD=1; bad "[${PF_NO}]⑦ 走 visualFloorPx 的盘面底线站点只剩 ${S177_VF} 个文件(应 ≥${S177_VF_MIN})—— 有人把底线改回裸 CSS px"
fi
for t in visualFloorPx zoomInlineScaleBug; do
    [ -f "${S177_UI}/src/utils/__tests__/${t}.test.js" ] || { S177_BAD=1; bad "[${PF_NO}]⑦ jest 守卫 ${t}.test.js 缺失"; }
done
# [${PF_NO}]⑧ 2026-09-18 起局/起盘后在极档下另查出三族:遁甲缩放系数下限 0.58 是 CSS px 口径(1.8 档撑出栏外被裁)、
#   八字盘头文案被定宽按钮组挤成逐字竖排、三式上盒压成 340px 干支叠成一团;数算「四柱」卡片省略号误判不在 antd 白名单里。
#   制度:① zoomDomain 导出比例版 visualFloorRatio 且遁甲 boardScale 下限经它;② 省略退 clip 规则扩到全元素(html.horosa-zoom-textbug *);
#   ③ 运行时巡检模板常驻 degenerate(逐字竖排)/ ellipsized(真省略)/ overlapPairs(文字盒互叠)三指标。
if [ -f "${S177_UI}/src/utils/zoomDomain.js" ] && ! grep -q "export function visualFloorRatio" "${S177_UI}/src/utils/zoomDomain.js"; then
    S177_BAD=1; bad "[${PF_NO}]⑧ zoomDomain 缺 visualFloorRatio —— 盘面缩放系数底线没有视觉口径版本"
fi
if [ -f "${S177_UI}/src/components/dunjia/DunJiaMain.js" ] && ! grep -q "visualFloorRatio(DUNJIA_SCALE_MIN)" "${S177_UI}/src/components/dunjia/DunJiaMain.js"; then
    S177_BAD=1; bad "[${PF_NO}]⑧ 遁甲 calcBoardScale 下限未经 visualFloorRatio —— 1.8 档九宫第三列被裁 / 表头顶出舞台复发"
fi
if [ -f "${S177_LESS}" ] && ! grep -q "html.horosa-zoom-textbug \*" "${S177_LESS}"; then
    S177_BAD=1; bad "[${PF_NO}]⑧ app.less 省略退 clip 规则未覆盖全元素(html.horosa-zoom-textbug *)—— 自定义卡片(数算四柱 \"丙..\")复发"
fi
[ "${S177_BAD}" = "0" ] && ok "[${PF_NO}] 壳缩放链病理锁全绿(结构四层 + 组件骨架 vh / 视口变量 / 内联盒缺陷探针 / 视觉底线)"
}

seg_128() {
# ---- [${PF_NO}] 在线地图(高德)CSP 白名单完整性(FL 装机专发类) ----
#   ★真表面 = main.rs 的 tiny_http 响应头 CSP,非 tauri.conf.json!主界面走本机静态服务器
#   (http://127.0.0.1:PORT)加载,不走 tauri:// 协议 → tauri.conf 的 csp 管不到主界面(地图在此)。
#   病根一(host)——main.rs CSP 的 script/style/img/connect 未放行 AMap 域(*.amap.com/*.autonavi.com)。
#   病根二(eval/wasm)——AMap 2.0 运行时用 eval()+WebAssembly.compile,须 script-src 含 'unsafe-eval'
#   (同时放行 eval 与 wasm)+ worker-src 含 blob:(瓦片解码走 blob worker)。
#   macOS WKWebView 严格执行响应头 CSP → 缺任一 = 地图白屏;preview 无 CSP、Windows WebView2 宽松
#   → dev/Win 假绿,唯 Mac 装机版暴露。iframe 实证:加齐后 map-COMPLETE 零违规。与 mapCsp.test.js 双护。
S128_BAD=0
S128_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S128_CONF="${INSTALLER_ROOT}/src-tauri/tauri.conf.json"
S128_MAINRS="$(pf_shell_rs_prod)"
echo "[${PF_NO}] 高德地图 CSP 白名单完整(真表面=main.rs tiny_http 响应头;code 用外部域 ⟹ 打包 CSP 必放行)"
# 仅当前端确实用 AMap 才要求(用了却没白名单=白屏);未用则本项 N/A。
if grep -q "amap-jsapi-loader" "${S128_UI}/src/components/amap/MapV2.js" 2>/dev/null \
   || grep -q "AMapKey" "${S128_UI}/src/utils/constants.js" 2>/dev/null; then
  S128_RES="$(python3 - "${S128_MAINRS}" "${S128_CONF}" <<'PY'
import json, re, sys
def parse(csp):
    dirs = {}
    for seg in csp.split(";"):
        seg = seg.strip()
        if seg:
            p = seg.split()
            dirs[p[0]] = p[1:]
    return dirs
def eff(dirs, d):
    return dirs.get(d, dirs.get("default-src", []))
def allows(sources, host):
    for s in sources:
        if s == "https://" + host:
            return True
        if s.startswith("https://*."):
            suf = s[len("https://*"):]           # ".amap.com"
            if host.endswith(suf) and host != suf[1:]:
                return True
    return False
def check(csp, label):
    dirs = parse(csp)
    probs = []
    # 实测 AMap JSAPI 2.0 用到的域(webapi=脚本/UI, restapi=地名/逆地理, jsapi/o4=瓦片资源)
    for h in ("webapi.amap.com", "restapi.amap.com", "jsapi.amap.com"):
        for d in ("script-src", "connect-src", "img-src"):
            if not allows(eff(dirs, d), h):
                probs.append("%s:%s 未放行 %s" % (label, d, h))
    if "blob:" not in eff(dirs, "worker-src"):
        probs.append("%s:worker-src 缺 blob:" % label)
    # AMap 2.0 运行时用 eval()+WebAssembly.compile;'unsafe-eval' 同时放行 eval 与 wasm。
    if "'unsafe-eval'" not in eff(dirs, "script-src"):
        probs.append("%s:script-src 缺 'unsafe-eval'(AMap 2.0 用 eval+wasm→白屏)" % label)
    return probs

problems = []
# ① 真表面:main.rs tiny_http 响应头 CSP(地图实际生效处;byte-string 里抽 CSP)
try:
    src = open(sys.argv[1], encoding="utf-8").read()
    m = re.search(r'&b"(default-src[^"]*)"', src)
    if not m:
        problems.append("main.rs 找不到 tiny_http CSP 字节串(地图真表面无法校验)")
    else:
        problems += check(m.group(1), "main.rs主界面")
except OSError:
    problems.append("main.rs 读取失败(地图真表面无法校验)")
# ② 次表面:tauri.conf.json launcher(无地图,但保持一致=纵深防御)
try:
    csp2 = json.load(open(sys.argv[2], encoding="utf-8")).get("app", {}).get("security", {}).get("csp", "")
    problems += check(csp2, "tauri.conf")
except OSError:
    problems.append("tauri.conf.json 读取失败")
if problems:
    sys.stdout.write("; ".join(problems))
PY
)"
  if [ -n "${S128_RES}" ]; then bad "[${PF_NO}] Mac 装机版地图将白屏 → CSP 缺放行: ${S128_RES}"; S128_BAD=1; fi
  # 同意闸仍在(放行≠自动加载,须用户先同意)
  grep -q "hasMapConsent" "${S128_UI}/src/components/amap/MapV2.js" 2>/dev/null || { bad "[${PF_NO}] 地图一次性同意闸丢失(放行外部域后须仍受同意 gate)"; S128_BAD=1; }
fi
[ "${S128_BAD}" = "0" ] && ok "[${PF_NO}] 高德地图 CSP(main.rs真表面+launcher:script/connect/img/worker-blob/unsafe-eval)白名单齐 + 同意闸在位"
}

seg_177b() {
# [${PF_NO}] CSS-zoom 域劈叉锁(全站浮层定位)。
#   病理:壳缩放走 documentElement.style.zoom ⇒ 页面存在两个坐标域——rect 域
#   (getBoundingClientRect,已缩放)与 CSS 域(style.left/top,未缩放)。dom-align@1.12.4 的
#   setLeftTop() 把 rect 域位移直写 CSS 域,z≠1 时全站浮层(下拉/提示/气泡/日期面板等)
#   系统性错位:Δ = (z−1)·(D−C) + z·(preset − floor(preset·z)),preset = −999(库内探针)。
#   z=1 时两项同时归零,故默认缩放档一直正常,问题只在非默认档暴露。
#   修法四件:①node_modules/dom-align 双产物补丁(写回除以实测有效缩放);②构建链三处挂载;
#   ③global.js 装运行时钩子;④手写 fixed 浮层经 clientToFixed 换算。
echo "[${PF_NO}] CSS-zoom 域劈叉锁(dom-align 补丁 + 构建挂载 + 运行时钩子 + 手写浮层)"
S177b_BAD=0
S177b_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S177b_ZD="${S177b_UI}/src/utils/zoomDomain.js"
S177b_PATCH="${S177b_UI}/scripts/patch-dom-align-zoom.js"
S177b_PKG="${S177b_UI}/package.json"
S177b_GLOBAL="${S177b_UI}/src/global.js"

for f in "${S177b_ZD}" "${S177b_PATCH}"; do
    [ -f "${f}" ] || { S177b_BAD=1; bad "[${PF_NO}]① 缺失 ${f##*/} —— 缩放域换算链断"; }
done
if [ -f "${S177b_ZD}" ]; then
    for fn in getEffectiveScale getFixedScale clientToFixed installAlignHooks; do
        grep -q "export function ${fn}" "${S177b_ZD}" || { S177b_BAD=1; bad "[${PF_NO}]① zoomDomain 缺导出 ${fn}"; }
    done
fi

for D in dist-node dist-web; do
    S177b_F="${S177b_UI}/node_modules/dom-align/${D}/index.js"
    if [ ! -f "${S177b_F}" ]; then
        S177b_BAD=1; bad "[${PF_NO}]② dom-align/${D}/index.js 缺失(npm install 未跑?)"
    else
        grep -q "horosa:dom-align-zoom" "${S177b_F}" || { S177b_BAD=1; bad "[${PF_NO}]② dom-align/${D} 未打补丁 —— 该份产物的浮层在缩放档全歪(测试走 dist-node、打包走 dist-web,两份都要打)"; }
        S177b_N1="$(grep -c 'off = off / __hz' "${S177b_F}" || true)"
        S177b_N2="$(grep -c '_off = _off / __hz' "${S177b_F}" || true)"
        [ "${S177b_N1}" = "1" ] || { S177b_BAD=1; bad "[${PF_NO}]② dom-align/${D} 首处写回补偿数=${S177b_N1}(应 1)—— 半修"; }
        [ "${S177b_N2}" = "1" ] || { S177b_BAD=1; bad "[${PF_NO}]② dom-align/${D} 次处写回补偿数=${S177b_N2}(应 1)—— 半修"; }
    fi
done
if [ -f "${S177b_UI}/node_modules/dom-align/package.json" ]; then
    S177b_VER="$(python3 -c "import json;print(json.load(open('${S177b_UI}/node_modules/dom-align/package.json'))['version'])" 2>/dev/null || echo '?')"
    [ "${S177b_VER}" = "1.12.4" ] || { S177b_BAD=1; bad "[${PF_NO}]② dom-align 版本变为 ${S177b_VER}(锚点按 1.12.4 核对过)—— 升级后必须重审补丁锚点再放行"; }
fi

if [ -f "${S177b_PKG}" ]; then
    for k in postinstall build "build:file"; do
        python3 - "${S177b_PKG}" "${k}" <<'PY' || { S177b_BAD=1; bad "[${PF_NO}]③ package.json 的 ${k} 未挂 patch-dom-align-zoom —— 构建产物会退回未补丁的 dom-align"; }
import json, sys
d = json.load(open(sys.argv[1]))
sys.exit(0 if 'patch-dom-align-zoom' in (d.get('scripts', {}).get(sys.argv[2]) or '') else 1)
PY
    done
fi

if [ -f "${S177b_GLOBAL}" ]; then
    [ "$(sed -e 's://.*$::' "${S177b_GLOBAL}" | grep -ac "installAlignHooks()")" != "0" ] \
        || { S177b_BAD=1; bad "[${PF_NO}]④ global.js 未调用 installAlignHooks() —— 钩子不装则补丁全程回落 1,等于没修"; }
fi

S177b_DF="${S177b_UI}/dist-file"
if [ -d "${S177b_DF}" ]; then
    # 全树:扫的是构建产物目录
    grep -rqa "__HOROSA_ALIGN_SCALE__" "${S177b_DF}" \
        || { S177b_BAD=1; bad "[${PF_NO}]⑤ dist-file 产物内找不到 __HOROSA_ALIGN_SCALE__ —— 打包用的前端是未补丁版本,装到机器上浮层照旧错位"; }
fi

for t in popupAlignZoomGuard popupAlignStaticGuard; do
    [ -f "${S177b_UI}/src/utils/__tests__/${t}.test.js" ] \
        || { S177b_BAD=1; bad "[${PF_NO}]⑥ 守卫套件 ${t}.test.js 缺失"; }
done

# ⑦ fixed 包含块残留不回归:container-type / contain:layout 会把中栏变成 fixed 后代的包含块
#    + stacking context,叠加 overflow:hidden 即裁剪悬浮窗。必须剥**跨行**块注释后再判——
#    修复注释本身就写着这两个词,单行剥法会假红。
S177b_CT="$(python3 - "$(pf_src_set "${S177b_UI}/src/layouts/app.less")" <<'PY'
import re, sys
src = open(sys.argv[1], encoding='utf-8').read()
src = re.sub(r'/\*.*?\*/', '', src, flags=re.S)
src = re.sub(r'(?m)^\s*//.*$', '', src)
# 白名单:三个盘面叶宿主(无 fixed 后代;antd 浮层挂 body)可作 inline-size 容器查询源(放大档中栏逐字竖排根治),
# 且全文件必有 @container 消费者;size 型 / contain:layout 一律禁(浮层裁剪事故根因 = block 轴 size 包含 + layout 包含
# = fixed 包含块)。白名单外出现 container-type = 红。
ALLOW = {'.horosa-workspace-shell .horosa-taixuan-board', '.horosa-workspace-shell .horosa-wuzhao-board', '.horosa-workspace-shell .horosa-cnx-board'}
bad = len(re.findall(r'contain:\s*[^;]*layout', src))
allowed_hits = 0
for m in re.finditer(r'container-type\s*:\s*([a-z-]+)', src):
    head = src[:m.start()]
    open_idx = head.rfind('{')
    pre = head[:open_idx] if open_idx >= 0 else ''
    start = max(pre.rfind('}'), pre.rfind('{'), pre.rfind(';'))
    sel = re.sub(r'\s+', ' ', pre[start + 1:].strip())
    if m.group(1) == 'inline-size' and sel in ALLOW:
        allowed_hits += 1
    else:
        bad += 1
if allowed_hits and not re.search(r'@container', src):
    bad += 1
print(bad)
PY
)"
if [ "${S177b_CT}" != "0" ]; then
    S177b_BAD=1; bad "[${PF_NO}]⑦ app.less 出现白名单外 container-type / contain:layout(${S177b_CT} 处)—— 会重新制造 fixed 包含块,悬浮窗被裁剪复发;全仓零 @container 消费者,不该有它"
fi

[ "${S177b_BAD}" = "0" ] && ok "[${PF_NO}] CSS-zoom 域劈叉锁全绿(双产物补丁/三处挂载/钩子/守卫/包含块)"
}

seg_274() {
# [${PF_NO}] 版面 / 指针换域第二批。每一条都是「100% 档两域重合看不出来、缩放档才现形」:
#   ① 折叠节行高:节体网格行写裸 1fr 时,系统浏览器内核在「占位式滚动条出现 → 面板变窄 → 节内控件折行变高」后不重算行高,
#      节内最后一行被内盒(overflow:hidden)裁掉且滚不到;写 minmax(0,1fr) 不裁(折叠态同写 minmax(0,0fr) 才能插值)。
#   ② 手写浮层 / 自绘画布的指针换域单源:fixedPopupFrame / pointerToLocal / pointerLocalRatio;只认命令式 style 写回的守卫
#      看不见 React 内联样式那条路 —— 新守卫盯读数端(clientX / window.inner*)。
#   ③ 内核契约垫片(按实测比值,一致的内核上自动不生效):SVG getScreenCTM 不反映 CSS zoom ⇒ d3.pointer / zoom / drag 整体错位;
#      MouseEvent.offsetX/Y 被报成视觉域 ⇒ 图表库 / 3D 惰性拾取偏 z 倍;对齐库「可见视口」系数改直接量。
#   ④ 叶子「工作区高 − 常数」定高第二批 + 八字盘槽 JS 配比与网格行两套算法。
#   ⑤ 裸 CSS px 底线(画布 320 / 页根 560)+ 黄历工作台隐式行 + 塔罗快捷栏被三栏挤出视口。
echo "[${PF_NO}] 折叠节行高 + 指针换域单源 + 内核契约垫片 + 叶子定高第二批"
S274_BAD=0
S274_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S274_SRC="${S274_UI}/src"
if ! python3 - "${S274_SRC}" "$(pf_src_set "${S274_SRC}/layouts/app.less")" <<'S274PY'
import os, re, sys
src = sys.argv[1]
SET = {'layouts/app.less': sys.argv[2]}   # 拆成区段的样式门面按全集读(pf_src_set 拼好的那份)
def rd(rel):
    p = SET.get(rel) or os.path.join(src, rel)
    return open(p, encoding='utf-8').read() if os.path.exists(p) else None
def strip(t): return re.sub(r'//[^\n]*', '', re.sub(r'/\*[\s\S]*?\*/', '', t))
bad = []
# ① 折叠节
t = rd('components/xq-ui/styles.less')
if t is None: bad.append('xq-ui/styles.less 缺失')
else:
    c = strip(t)
    m = re.search(r'\.xq-side-section-body\s*\{([^}]*)\}', c)
    if not m or 'grid-template-rows: minmax(0, 1fr)' not in m.group(1): bad.append('折叠节体行高不是 minmax(0, 1fr)(裸 1fr 折行后不重算 → 节内末行被裁)')
    m = re.search(r'\.xq-side-section-collapsed\s+\.xq-side-section-body\s*\{([^}]*)\}', c)
    if not m or 'grid-template-rows: minmax(0, 0fr)' not in m.group(1): bad.append('折叠态行高不是 minmax(0, 0fr)(与展开态不同型 → 过渡不插值)')
    m = re.search(r'\.xq-side-section\s*\{([^}]*)\}', c)
    if not m or 'flex-shrink: 0' not in m.group(1): bad.append('折叠节缺 flex-shrink: 0')
# ②③ 换域单源
t = rd('utils/zoomDomain.js')
if t is None: bad.append('utils/zoomDomain.js 缺失')
else:
    c = strip(t)
    for tok in ('export function fixedPopupFrame', 'export function pointerToLocal', 'export function pointerLocalRatio', 'export function installSvgCtmShim', 'export function getSvgCtmScale', 'export function installOffsetXYShim', 'export function getOffsetDomainScale'):
        if tok not in c: bad.append('zoomDomain 缺 ' + tok)
    m = re.search(r'export function installAlignHooks\(\)\{([\s\S]*?)\n\}', c)
    if not m or 'installSvgCtmShim()' not in m.group(1): bad.append('installAlignHooks 未安装 SVG 矩阵垫片(d3.pointer 全族在缩放档错位)')
    if not m or 'installOffsetXYShim()' not in m.group(1): bad.append('installAlignHooks 未安装 offsetX/Y 垫片(图表库 / 3D 惰性拾取在缩放档偏 z 倍)')
    m2 = re.search(r'export function getViewportScale\(\)\{([\s\S]*?)\n\}', c)
    if not m2 or 'getBoundingClientRect' not in m2.group(1) or 'getEffectiveScale() === 1' in m2.group(1).replace(' ', ' '): bad.append('对齐库视口系数不再直接量(rect 不反映缩放的引擎放大档下拉不翻转)')
# ④ 叶子定高:禁回「工作区高 − 常数」
LEAVES = [
    ('components/ruleziwei/ZWRuleMain.js', r'height\s*-\s*130', '紫微资料参考'),
    ('components/acg/AstroAcg.js', r'height\s*=\s*height\s*-\s*50', '占星地图'),
    ('components/tongshefa/TongSheFaMain.js', r'height\s*-\s*304', '统摄法'),
    ('components/tarot/TarotMain.js', r'height\s*-\s*8\b', '塔罗'),
    ('components/astro/AstroFirdaria.js', r'height\s*-\s*70', '法达星限'),
    ('components/astro/AstroYearSystem129.js', r'height\s*-\s*70', '129 年系统'),
    ('components/fengshui/fengshuiEngine.js', r'Math\.max\(\s*320\s*,\s*host\.client', '风水画布 320 裸底线'),
]
for rel, pat, name in LEAVES:
    t = rd(rel)
    if t is None: continue      # 文件不在则跳过
    if re.search(pat, strip(t)): bad.append('%s 改回「工作区高 − 常数 / 裸 px 底线」定高:%s' % (name, rel))
t = rd('components/cntradition/BaZi.js')
if t is not None and "height={isFineChart ? 'auto' : '100%'}" not in t: bad.append('八字盘滚动盒不再 100% 贴槽(JS 配比与网格行两套算法 → 择日八字盘底被槽裁掉)')
t = rd('components/zeri/HuangliZeriMain.js')
if t is not None and 'height="100%"' not in t: bad.append('择日黄历宿主改回传工作区 px 高(工作台比宿主高 → 详情滚动盒被裁)')
# ⑤ 样式
t = rd('layouts/app.less')
if t is not None:
    c = strip(t)
    if not re.search(r'\.horosa-tarot-page\s*\{[^}]*display:\s*flex;[^}]*flex-direction:\s*column', c): bad.append('塔罗页根不再是纵向 flex(三栏占满整页 → 快捷栏整条挤出视口)')
    m = re.search(r'\.horosa-calendar-workbench\s*\{([^}]*)\}', c)
    if not m or 'grid-template-rows: minmax(0, 1fr)' not in m.group(1): bad.append('黄历工作台隐式行未锁死')
t = rd('components/planetarium/planetarium.less')
if t is not None and re.search(r'min-height:\s*560px\s*;', strip(t)): bad.append('天文馆页根改回裸 560px 底线(放大档把整页撑出页签盒)')
for b in bad: print('    ' + b)
sys.exit(1 if bad else 0)
S274PY
then bad "[${PF_NO}] 折叠节行高 / 换域单源 / 叶子定高 回归"; S274_BAD=1; fi
S274_T="${S274_SRC}/utils/__tests__"
S274_P1='installSvgCtmShim · getScreenCTM 与 clientX 同域'
S274_P2='T6 指针 / 物理视口读数必须过换域件'
[ -f "${S274_T}/zoomDomainPointerHelpers.test.js" ] && [ "$(grep -acF "${S274_P1}" "${S274_T}/zoomDomainPointerHelpers.test.js")" -ge 1 ] || { bad "[${PF_NO}]③ 回归用例缺失:${S274_P1}"; S274_BAD=1; }
[ "$(grep -acF "${S274_P2}" "${S274_T}/popupAlignStaticGuard.test.js" 2>/dev/null)" -ge 1 ] || { bad "[${PF_NO}]② 静态守卫缺失:${S274_P2}"; S274_BAD=1; }
# ⑤ 三式中栏的内层盒不自己滚(滚动只交给外面的面板)。系统浏览器内核在合成层里画「定高百分比的滚动盒 + 首尾子元素 auto 外边距居中」时,
#    只画从盒顶起、内容自身那么高的一段,而内容被上外边距整体下推 ⇒ 起盘后盘底信息盒少画一截(浅色主题;版面读数全对,换一次缩放档才恢复)。
S274_SS="${S274_UI}/src/components/sanshi/SanShiUnitedMain.less"
if [ ! -f "${S274_SS}" ]; then bad "[${PF_NO}]⑤ 缺 SanShiUnitedMain.less"; S274_BAD=1
elif ! python3 - "${S274_SS}" <<'S274SSPY'
import re, sys
c = re.sub(r'/\*.*?\*/', '', open(sys.argv[1], encoding='utf-8').read(), flags=re.S)   # 注释里同样写着 overflow,不剥会误判
m = re.search(r'\.boardStack\s*\{([^}]*)\}', c)
bad = []
if not m: bad.append('找不到 .boardStack 规则')
else:
    if re.search(r'overflow(-y)?\s*:\s*(auto|scroll)', m.group(1)): bad.append('.boardStack 又自己滚了(overflow:auto/scroll)')
    if not re.search(r'overflow\s*:\s*visible', m.group(1)): bad.append('.boardStack 未显式 overflow:visible')
if bad:
    print('\n'.join('    ' + b for b in bad)); sys.exit(1)
S274SSPY
then bad "[${PF_NO}]⑤ 三式中栏内层盒保险失效(见上)"; S274_BAD=1; fi
# ⑥ 源码侧两道闸在位(内容由 jest 判;这里只锁「文件与锚还在」,防整份被删)
S274_P3='① src 里不出现容器查询 / container-type / cq 单位'
S274_P4='② 直接 new ResizeObserver 只在登记表里'
[ "$(grep -acF "${S274_P3}" "${S274_T}/zoomAdaptiveLayoutGuard.test.js" 2>/dev/null)" -ge 1 ] || { bad "[${PF_NO}]⑥ 源码闸缺失:${S274_P3}"; S274_BAD=1; }
[ "$(grep -acF "${S274_P4}" "${S274_T}/resizeObserverDeferred.test.js" 2>/dev/null)" -ge 1 ] || { bad "[${PF_NO}]⑥ 源码闸缺失:${S274_P4}"; S274_BAD=1; }
[ "${S274_BAD}" = "0" ] && ok "[${PF_NO}] 折叠节行高 minmax(0,1fr) + 指针换域单源与读数端守卫 + SVG 矩阵垫片 + 叶子定高第二批 + 三式中栏内层盒不自滚 + 源码闸"
}

seg_273() {
# [${PF_NO}] 缩放域「运行期真值」+ 版面容器定高锁。
#   ① 运行期「现在几档」只认文档根 inline zoom。URL query 与存储键是壳的启动传输层:运行时换档不改 URL,而壳调回 100% 时恰恰把 inline 清空
#      ⇒ 读回启动旧档:对齐库补偿除数用旧档(全站浮层错位 (1/z0−1)·(D+999))、布局视口缓存命中旧档、视觉底线按旧档折算。
#      只用 `__HOROSA_ALIGN_SCALE__ = () => z` 的桩测对齐,恰好绕开「声明值→缓存→除数」真链路 —— 行为用例必须装真钩子走完整生命周期。
#   ② 页面自刷新(reload)时 URL 仍是启动旧 query ⇒ 启动档位以键为准(壳每次换档都写键),单源 resolveBootstrapZoom。
#   ③ 坞行高 ≡ 坞盒高:行写裸 58px 装 64px 的坞,各缩放档坞下缘被窗口底边切掉一截。
#   ④ Tabs 内容链定高 + 叶子 fill(容器定高):叶子按「物理域窗口高 − 常数」写死 px 时,缩小档底部死带、放大档溢出被裁且滚不到。
#   ⑤ 物理域视口直读族静态守卫(只抓「÷」的旧 PATTERN 抓不到「− 常数 / > 断点」)。
#   ⑥ 行为闸:真页面 + 真对齐库产物 + 壳里抽取的真换档脚本,两种引擎语义都必须零错位;自证 = 注入旧档除数必红。
echo "[${PF_NO}] 缩放域运行期真值 + 版面容器定高锁"
S273_BAD=0
S273_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S273_ZD="${S273_UI}/src/utils/zoomDomain.js"
S273_SZ="${S273_UI}/src/utils/shellZoom.js"
S273_GJ="${S273_UI}/src/global.js"
S273_LESS="$(pf_src_set "${S273_UI}/src/layouts/app.less")"
S273_T="${S273_UI}/src/utils/__tests__"
for S273_F in "${S273_ZD}" "${S273_SZ}" "${S273_GJ}" "${S273_LESS}" "${S273_T}/popupAlignZoomGuard.test.js" "${S273_T}/shellZoomGuard.test.js" "${S273_T}/layoutDomainStaticGuard.test.js"; do
  [ -f "${S273_F}" ] || { bad "[${PF_NO}] 资产缺失:${S273_F#${REPO_ROOT}/}"; S273_BAD=1; }
done
if [ "${S273_BAD}" = "0" ]; then
  # ①②:剥注释后判(注释里同样写着这些字面量,不剥会假绿 / 假红)
  if ! python3 - "${S273_ZD}" "${S273_SZ}" "${S273_GJ}" <<'S273PY'
import re, sys
def strip(t): return re.sub(r'//[^\n]*', '', re.sub(r'/\*[\s\S]*?\*/', '', t))
zd, sz, gj = (strip(open(p, encoding='utf-8').read()) for p in sys.argv[1:4])
bad = []
if re.search(r"from\s+['\"]\./shellZoom['\"]", zd): bad.append('zoomDomain 仍 import shellZoom(运行期真值被启动传输层污染)')
if 'getShellZoom' in zd or 'location.search' in zd: bad.append('zoomDomain 仍读启动传输层(getShellZoom / location.search)')
m = re.search(r'export function getDeclaredZoom\(\)\{([\s\S]*?)\n\}', zd)
if not m or 'document.documentElement.style.zoom' not in m.group(1): bad.append('getDeclaredZoom 不再读 documentElement.style.zoom')
if m and ('localStorage' in m.group(1)): bad.append('getDeclaredZoom 体内出现 localStorage')
for tok in ('export function resolveBootstrapZoom', 'export function readBootstrapShellZoom', "'reload'"):
    if tok not in sz: bad.append('shellZoom.js 缺 ' + tok)
if 'readBootstrapShellZoom' not in gj: bad.append('global.js 未经 readBootstrapShellZoom 取启动档位')
if 'shellZoom=' in gj: bad.append('global.js 仍自带一份 query 读法(两份读法 = 漂移源)')
for b in bad: print('    ' + b)
sys.exit(1 if bad else 0)
S273PY
  then bad "[${PF_NO}]①② 缩放域运行期真值 / 启动档位单源 被改回"; S273_BAD=1; fi
  # 回归用例字面在位(真钩子全链 + 启动→调回 100% + reload 真值表)
  S273_P1='[运行期真值] 真钩子全链'
  S273_P2='[运行期真值] 0.8 档启动'
  S273_P3='resolveBootstrapZoom 真值表'
  [ "$(grep -acF "${S273_P1}" "${S273_T}/popupAlignZoomGuard.test.js")" -ge 1 ] || { bad "[${PF_NO}]① 回归用例缺失:${S273_P1}"; S273_BAD=1; }
  [ "$(grep -acF "${S273_P2}" "${S273_T}/popupAlignZoomGuard.test.js")" -ge 1 ] || { bad "[${PF_NO}]① 回归用例缺失:${S273_P2}"; S273_BAD=1; }
  [ "$(grep -acF "${S273_P3}" "${S273_T}/shellZoomGuard.test.js")" -ge 1 ] || { bad "[${PF_NO}]② 回归用例缺失:${S273_P3}"; S273_BAD=1; }
  # ③④:app.less(剥块注释后判)
  if ! python3 - "${S273_LESS}" <<'S273PY2'
import re, sys
t = re.sub(r'/\*[\s\S]*?\*/', '', open(sys.argv[1], encoding='utf-8').read())
bad = []
m = re.search(r'\.horosa-sanshi-redesign-layout\s*\{([^}]*)\}', t)
if not m or 'grid-template-rows: minmax(0, 1fr) var(--horosa-bottom-dock-height)' not in m.group(1): bad.append('三式坞行不再 ≡ 坞盒高单源变量')
m = re.search(r'\.horosa-sanshi-redesign-grid\s*\{([^}]*)\}', t)
if not m or 'grid-template-rows: minmax(0, 1fr)' not in m.group(1): bad.append('三式栅格隐式行未锁死')
chain = r'\.horosa-cntradition-page\s*>\s*\.ant-tabs-right\s*>\s*\.ant-tabs-content-holder\s*>\s*\.ant-tabs-content\s*>\s*\.ant-tabs-tabpane\s*\{[^}]*'
if not re.search(chain + r'height:\s*100%', t): bad.append('辅助页 Tabs 内容链未定高')
if not re.search(chain + r'overflow-y:\s*auto', t): bad.append('辅助页 pane 无纵滚出路')
if '.horosa-fill-tabs.ant-tabs' not in t: bad.append('fill 模式内层 Tabs 规则缺失')
if not re.search(r'\.horosa-content-tabs \.ant-tabs-tabpane > \.ant-spin-nested-loading > \.ant-spin-container > :only-child\s*\{[^}]*height:\s*100%\s*!important', t): bad.append('内容页签定高链在 Spin 处掐断(占星「格局」页签 100% 档少 36px 的病)')
rows = [x for x in re.findall(r'grid-template-rows:\s*minmax\(0,\s*1fr\)\s+(\d+)px', t) if x not in ('64', '138', '60')]
if rows: bad.append('出现与坞盒高不等的坞行:%s px' % ','.join(rows))
for b in bad: print('    ' + b)
sys.exit(1 if bad else 0)
S273PY2
  then bad "[${PF_NO}]③④ 坞行高 / 三式隐式行 / 辅助页定高链 回归"; S273_BAD=1; fi
  S273_CN="${S273_UI}/src/components/cntradition/CnTraditionMain.js"
  for S273_TOK in '<GuaSymDesc fill />' '<CuanGong12 fill />' '<BaziPithy fill />'; do
    [ "$(grep -acF "${S273_TOK}" "${S273_CN}")" -ge 1 ] || { bad "[${PF_NO}]④ 辅助页子 tab 未走 fill:${S273_TOK}"; S273_BAD=1; }
  done
  # ①b dom-align 补丁 v2:翻转 / 夹紧半程的祖先裁剪循环(rect 域 offset + 布局域 client* 直加 → 放大档滚动祖先可视区被算矮 →
  #     下半部的触发器被判不可见 → 整段跳过翻转,下拉伸出窗口底边)。两份产物各恰 1 处、未补形态零残留、回归用例在位。
  S273_PV='horosa:dom-align-zoom v3'
  S273_PD='documentHeight = win.innerHeight * __vs;'
  S273_PH='pos.top + el.clientHeight * __hzc);'
  S273_PO='pos.top + el.clientHeight);'
  for S273_D in dist-node dist-web; do
    S273_DF="${S273_UI}/node_modules/dom-align/${S273_D}/index.js"
    if [ -f "${S273_DF}" ]; then
      [ "$(grep -acF "${S273_PV}" "${S273_DF}")" = "1" ] || { bad "[${PF_NO}]①b dom-align/${S273_D} 不是 v3 补丁(构建前跑 node scripts/patch-dom-align-zoom.js)"; S273_BAD=1; }
      [ "$(grep -acF "${S273_PH}" "${S273_DF}")" = "1" ] || { bad "[${PF_NO}]①b dom-align/${S273_D} 祖先裁剪循环未换域"; S273_BAD=1; }
      [ "$(grep -acF "${S273_PO}" "${S273_DF}")" = "0" ] || { bad "[${PF_NO}]①b dom-align/${S273_D} 残留未补形态(半修)"; S273_BAD=1; }
      [ "$(grep -acF "${S273_PD}" "${S273_DF}")" = "1" ] || { bad "[${PF_NO}]①b dom-align/${S273_D} 「文档尺寸」读数未过视口系数(v3;rect 不反映缩放的引擎放大档下拉不翻转)"; S273_BAD=1; }
    fi
  done
  S273_P4='T3b 翻转半程'
  [ "$(grep -acF "${S273_P4}" "${S273_T}/popupAlignZoomGuard.test.js")" -ge 1 ] || { bad "[${PF_NO}]①b 回归用例缺失:${S273_P4}"; S273_BAD=1; }
  # ⑤ 静态守卫两族在位
  S273_P5='T5 物理域视口直读族'
  S273_P6='T6 底部快捷栏'
  [ "$(grep -acF "${S273_P5}" "${S273_T}/layoutDomainStaticGuard.test.js")" -ge 1 ] || { bad "[${PF_NO}]⑤ 静态守卫 T5 缺失"; S273_BAD=1; }
  [ "$(grep -acF "${S273_P6}" "${S273_T}/layoutDomainStaticGuard.test.js")" -ge 1 ] || { bad "[${PF_NO}]⑤ 静态守卫 T6 缺失"; S273_BAD=1; }
fi
# ⑥ 行为闸:真页面 + 真 antd + 真 dom-align 产物 + 壳里抽取的真换档脚本,走「非 1 档启动 → 页内调回 100%」等换档序列,
#    E2(旧 macOS:rect 不反映缩放)/ E3(Tahoe / Chromium)两种引擎语义都必须零错位;自证 = 注入旧档除数必红。
S273_AUDIT="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/audit_popup_geometry.py"
S273_DIST="${S273_UI}/dist-file/index.html"
if [ ! -f "${S273_AUDIT}" ]; then
  bad "[${PF_NO}]⑥ 缺 audit_popup_geometry.py —— 浮层几何行为闸丢失"; S273_BAD=1
elif [ ! -f "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/popup_geometry.tpl.js" ]; then
  bad "[${PF_NO}]⑥ 判据体 scripts/popup_geometry.tpl.js 缺失(双引擎行为闸的判据单源)"; S273_BAD=1
elif [ ! -f "${S273_DIST}" ]; then
  warn "[${PF_NO}]⑥ 无前端产物(dist-file),跳过浮层几何行为闸 —— 打包前必然已构建,届时会真跑"
elif ! python3 -c "import playwright" >/dev/null 2>&1; then
  warn "[${PF_NO}]⑥ 未装 playwright,跳过(装:python3 -m pip install playwright && python3 -m playwright install chromium)"
else
  S273_OUT="$(cd "${REPO_ROOT}/Horosa_Desktop_Installer" && python3 scripts/audit_popup_geometry.py --self-test 2>&1)"
  if [ $? -ne 0 ]; then
    bad "[${PF_NO}]⑥ 浮层判据自证失败(健康臂不绿或病灶臂不红,结论不可信): $(printf '%s' "${S273_OUT}" | tail -3 | tr '\n' ' ')"; S273_BAD=1
  else
    S273_OUT2="$(cd "${REPO_ROOT}/Horosa_Desktop_Installer" && python3 scripts/audit_popup_geometry.py --quick 2>&1)"
    if [ $? -ne 0 ]; then
      bad "[${PF_NO}]⑥ 浮层几何行为闸发现错位: $(printf '%s' "${S273_OUT2}" | tail -6 | tr '\n' ' ')"; S273_BAD=1
    fi
  fi
fi
[ "${S273_BAD}" = "0" ] && ok "[${PF_NO}] 缩放域运行期真值只读 inline + 启动档位单源(reload 以键为准)+ 坞行≡坞盒 + 辅助页定高链与 fill + 物理域直读守卫 + 浮层几何行为闸"
}

seg_287() {
# [${PF_NO}] 响应顶层键序 = 生产方顺序 · 黄历九星值日 / 时辰宜忌懒算 · 皇极经世典籍正文按需 · 天象微年表只取渲染行 ·
#       小限摘要粒度 / 起点挂载接线 + 挂载差分测试缺省钉住此刻。锚住修法与回归测试在位(2026-09-26)。
echo "[${PF_NO}] 响应保序 · 黄历懒算 · 皇极典籍按需 · 微年表截断 · 小限齿轮接线 + 差分测试钉此刻"
S287_BAD=0
S287_W="${REPO_ROOT}/Horosa-Web"
S287_UI="${S287_W}/astrostudyui/src"
S287_TD="${S287_W}/astrostudysrv/boundless/src/main/java/boundless/spring/help/interceptor/TransData.java"
for S287_F in \
  "astrostudysrv/boundless/src/test/java/boundless/spring/help/interceptor/TransDataOrderTest.java" \
  "astrostudyui/src/components/calendar/__tests__/huangliLazyDetail.test.js" \
  "astrostudyui/src/components/huangji/__tests__/huangjiClassicsOnDemand.test.js" \
  "astropy/tests/test_wangji_classics_ondemand.py" \
  "astropy/tests/test_xuanshi_micro_ondemand.py"; do
  [ -s "${S287_W}/${S287_F}" ] || { bad "[${PF_NO}] 🔴 缺回归测试 ${S287_F}"; S287_BAD=1; }
done
grep -q "new LinkedHashMap<String, Object>()" "${S287_TD}" 2>/dev/null && [ "$(grep -c 'newResponseMap()' "${S287_TD}" 2>/dev/null)" -ge 6 ] || { bad "[${PF_NO}] 🔴 响应主体表未保序"; S287_BAD=1; }
grep -q "get times() { return readTimes(); }" "${S287_UI}/components/calendar/huangliDay.js" 2>/dev/null \
  && grep -q "get nineStar() { return readNineStar(); }" "${S287_UI}/components/calendar/huangliDay.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 黄历九星值日 / 时辰宜忌未懒算"; S287_BAD=1; }
grep -q "def classic(self):" "${S287_W}/astropy/websrv/webwangjisrv.py" 2>/dev/null \
  && grep -q "ensurePanClassics(await postWangJi('pan', payload), payload)" "${S287_UI}/components/huangji/HuangJiMain.js" 2>/dev/null \
  && grep -q "ensurePanClassics(await postWangJi('pan', panPayload), panPayload)" "${S287_UI}/components/huangji/HuangJiMain.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 皇极典籍按需接线不全"; S287_BAD=1; }
grep -q "def _micro_texts(" "${S287_W}/astropy/astrostudy/xuanshi/celestial.py" 2>/dev/null \
  && grep -q "(sm.total || 0) > MICRO_RENDER_LIMIT" "${S287_UI}/components/xuanshi/XuanShiMicro.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 天象微年表截断接线不全"; S287_BAD=1; }
grep -q "profGrain: record.profGrain," "$(pf_src_set "${S287_UI}/utils/aiAnalysisContext.js")" 2>/dev/null && grep -q "profStart: record.profStart," "$(pf_src_set "${S287_UI}/utils/aiAnalysisContext.js")" 2>/dev/null \
  && grep -q "installFixedNow('2026-09-26T12:00:00+08:00');" "${S287_UI}/utils/__tests__/mountSettingsDiffAll.test.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 小限摘要粒度 / 起点挂载接线或差分测试钉此刻缺失"; S287_BAD=1; }
grep -q "horosa_response_order_v1" "${S287_TD}" 2>/dev/null && grep -q "new LinkedHashMap<String, Object>()" "${S287_TD}" 2>/dev/null \
  && [ "$(grep -c 'newResponseMap()' "${S287_TD}" 2>/dev/null)" -ge 6 ] || { bad "[${PF_NO}] 🔴 TransData 响应表未保序(线程本地 HashMap 扩容史决定顶层键序)"; S287_BAD=1; }
grep -q 'data.get("slimClassics")' "${S287_W}/astropy/websrv/webwangjisrv.py" 2>/dev/null || { bad "[${PF_NO}] 🔴 皇极典籍按需:服务端缺 slimClassics 开关"; S287_BAD=1; }
grep -q 'limit=_int(d, "limit")' "${S287_W}/astropy/websrv/webxuanshisrv.py" 2>/dev/null || { bad "[${PF_NO}] 🔴 微年表截断:服务端缺 limit 参数"; S287_BAD=1; }
grep -q "HOROSA_DIFFNET_DEAD_DUMP_DIR" "${S287_UI}/utils/__tests__/mountSettingsDiffAll.test.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 挂载差分测试缺判死落盘(HOROSA_DIFFNET_DEAD_DUMP_DIR)"; S287_BAD=1; }
[ "${S287_BAD}" = "0" ] && ok "[${PF_NO}] 响应保序 + 黄历懒算 + 皇极典籍按需 + 微年表截断 + 小限齿轮接线 + 差分测试钉此刻 + 回归测试在场"
}

seg_158() {
# ── [${PF_NO}] R3 性能宗师轮防回归(kentang 缓存/选步长预取/覆盖矩阵零 todo/预置信任/warmup 并行/惰性工厂/让路)──
echo "[${PF_NO}] R3 性能宗师轮防回归"
S158_BAD=0
S158_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
# ① kentang 缓存层四锚:文件在位/键去端口/坑49 载荷守卫/预取纪律(非确定性代码层拒绝)
S158_KC="${S158_UI}/utils/kentangCache.js"
[ -s "${S158_KC}" ] || { bad "[${PF_NO}] 缺 kentangCache.js —— C 型 20 模块回裸奔"; S158_BAD=1; }
grep -aq 'kt\.\${pathOf(url)}' "${S158_KC}" 2>/dev/null || { bad "[${PF_NO}] 🔴 kentangCache 键未去端口化(端口漂移将废缓存)"; S158_BAD=1; }
grep -aq "obj.ResultCode !== undefined && obj.ResultCode !== 0" "${S158_KC}" 2>/dev/null || { bad "[${PF_NO}] 🔴 kentangCache 坑49 载荷守卫(ResultCode)缺位"; S158_BAD=1; }
grep -aq "modulePolicy(moduleKey) !== 'deterministic'" "${S158_KC}" 2>/dev/null || { bad "[${PF_NO}] 🔴 prefetchKentang 预取纪律锚缺位(含种子模块可被预取=随机结果钉死)"; S158_BAD=1; }
[ -s "${S158_UI}/utils/__tests__/kentangCache.test.js" ] || { bad "[${PF_NO}] 缺 kentangCache.test.js 金标"; S158_BAD=1; }
# ② 调用面收口:fetchChartWithRetry 裸用归零(唯 kentangCache 内部与其自源文件可用)
S158_RAW="$(grep -rn "fetchChartWithRetry(" "${S158_UI}/components" "${S158_UI}/services" 2>/dev/null | grep -av "kentangCache" | grep -av "__tests__" || true)"
[ -z "${S158_RAW}" ] || { bad "[${PF_NO}] 🔴 存在绕过缓存壳的 fetchChartWithRetry 裸调用:"; printf '%s\n' "${S158_RAW}" | sed 's/^/    /' >&2; S158_BAD=1; }
# ③ 选步长即预取三锚:触发点/全链 prop/处理器注册 + 金标在位
grep -aq "fireStepSelectPrefetch(val)" "${S158_UI}/components/comp/DateTimeSelector.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 DateTimeSelector 选步长触发点缺位"; S158_BAD=1; }
grep -aq "stepSelectPrefetch=" "${S158_UI}/components/astro/PlusMinusTime.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 PlusMinusTime 未挂 stepSelectPrefetch(全链断)"; S158_BAD=1; }
grep -aq "registerStepSelectHandler((unit)" "${S158_UI}/models/astro.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 astro model 选步长处理器未注册"; S158_BAD=1; }
[ -s "${S158_UI}/utils/__tests__/stepSelectPrefetch.test.js" ] || { bad "[${PF_NO}] 缺 stepSelectPrefetch.test.js 金标"; S158_BAD=1; }
# ④ 覆盖矩阵零 todo(发版门;结构一致性由 perfCoverage.test.js 管)
S158_TODO="$(grep -ac ": 'todo'" "${S158_UI}/utils/perfCoverageManifest.js" 2>/dev/null || true)"
[ "${S158_TODO:-0}" = "0" ] || { bad "[${PF_NO}] 🔴 perfCoverage 矩阵仍有 ${S158_TODO} 个 todo —— 「所有技法」未收口"; S158_BAD=1; }
# ⑤ 预置信任三锚:子命令/模板调用/回验语义
S158_MAIN="$(pf_shell_rs_prod)"
grep -q -- "--horosa-preseed-health" "${S158_MAIN}" 2>/dev/null || { bad "[${PF_NO}] 🔴 main.rs 缺 --horosa-preseed-health 子命令"; S158_BAD=1; }
grep -q "fn run_preseed_health_cli" "${S158_MAIN}" 2>/dev/null || { bad "[${PF_NO}] 🔴 缺 run_preseed_health_cli 本体"; S158_BAD=1; }
grep -q -- "--horosa-preseed-health" "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template" 2>/dev/null || { bad "[${PF_NO}] 🔴 postinstall 未调用预置信任(首启回 untrusted 慢档)"; S158_BAD=1; }
grep -q "preseed_health_cli_enables_trusted_fast_path" "$(pf_shell_rs_tests)" 2>/dev/null || { bad "[${PF_NO}] 缺 preseed cargo 金标"; S158_BAD=1; }
# ⑥ Python warmup 并行三锚
S158_PY="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
grep -q "_warmup_stage_kentang" "${S158_PY}" 2>/dev/null || { bad "[${PF_NO}] 🔴 warmup 三段化缺位"; S158_BAD=1; }
grep -q "HOROSA_PY_WARMUP_PARALLEL" "${S158_PY}" 2>/dev/null || { bad "[${PF_NO}] 🔴 warmup 并行 kill-switch 缺位"; S158_BAD=1; }
[ -s "${REPO_ROOT}/Horosa-Web/astropy/tests/test_warmup_parallel.py" ] || { bad "[${PF_NO}] 缺 test_warmup_parallel.py(门时序钉)"; S158_BAD=1; }
# ⑦ 惰性缓存工厂三锚:代理类/门控/桌面三启动支注入
grep -q "class LazyCacheFactory" "${REPO_ROOT}/Horosa-Web/astrostudysrv/boundless/src/main/java/boundless/types/cache/LazyCacheFactory.java" 2>/dev/null || { bad "[${PF_NO}] 🔴 缺 LazyCacheFactory(refresh 回吃 490ms)"; S158_BAD=1; }
grep -q "lazyInitEnabled()" "${REPO_ROOT}/Horosa-Web/astrostudysrv/boundless/src/main/java/boundless/types/cache/CacheFactory.java" 2>/dev/null || { bad "[${PF_NO}] 🔴 CacheFactory 未接惰性门控"; S158_BAD=1; }
S158_LZ="$(grep -c -- "-Dhorosa.cache.lazyinit=true" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" 2>/dev/null || true)"
[ "${S158_LZ:-0}" = "3" ] || { bad "[${PF_NO}] 🔴 start 脚本惰性属性注入应恰 3 处(exploded/无CDS/fat-jar),现 ${S158_LZ}"; S158_BAD=1; }
# ⑧ min-warmup 让路锚(untrusted 后台化+trusted 保持同步)
grep -q "HOROSA_WARM_MIN_ASYNC" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" 2>/dev/null || { bad "[${PF_NO}] 🔴 min-warmup 让路开关缺位"; S158_BAD=1; }
[ "${S158_BAD}" = "0" ] && ok "[${PF_NO}] R3 性能宗师轮资产全在位"
}
