# Horosa-Web · Agent Harness（坑点速查）

> 给后续 Claude Code / 自动化 agent：进入这个仓做改动之前，**先读这两份文档**——本文档 +
> `horosa-dev` skill（`.claude/skills/horosa-dev/SKILL.md`，dev / 构建 / 发布流程与坑）。
> **铁律：① 每次动手前先读这两份；② 解决任何新问题后立刻把根因 + 修法回写本文档（机制坑）或 skill（dev/release 坑），
> 优先在 `release_preflight.sh` 加 code guard——institutional memory 靠「每次回写」维持，不写就漂移。**
> 这里只记**会反复踩、文档没记会出错**的点。常规规范在
> [`../docs/windows-porting-and-release-checklist.md`](../docs/windows-porting-and-release-checklist.md)
> 和各版本 fix 文档（`Horosa-Web/docs/*.md`）。

---

## 日界点 + 晚子时·时柱起干（v2.2.1 起）

**两个独立全局开关**，请务必先理解再改任何 day/time pillar 相关代码：

| 全局偏好 | dva fields / 后端字段 | 默认值 | 作用范围 |
|---|---|---|---|
| `dayBoundary: 'after23' \| 'after24'` | `after23NewDay: 1 \| 0` | `1` | hour ∈ [23, 24): 控制**日柱**进位 |
| `lateZiHourMode: 'nextDay' \| 'today'` | `lateZiHourUseNextDay: 1 \| 0` | `1` | hour ∈ [23, 24): 控制**时干**起算用今日 vs 次日 |

**27日 23:30（直接时间）矩阵 — 跑 jest 必须命中这些**：

```
┌────────────────────────┬──────────────────┬──────────────────┐
│                        │ 时柱=1（默认）   │ 时柱=0           │
├────────────────────────┼──────────────────┼──────────────────┤
│ 日柱=1（默认）         │ 壬寅 庚子        │ 壬寅 庚子（等价）│
│ 日柱=0                 │ 辛丑 庚子        │ 辛丑 戊子 ← 新   │
└────────────────────────┴──────────────────┴──────────────────┘
```

详细见 [`docs/global-day-boundary-v2.2.1.md`](docs/global-day-boundary-v2.2.1.md)。

### 6 个坑（按踩过的顺序，请勿重蹈）

#### 1. Java ChartController.getParams() 是**白名单**
`ChartController.java:265 getParams()` 不会自动透传所有 TransData 字段。
任何 chart-flow 新参数（如 `after23NewDay`、`lateZiHourUseNextDay`）必须显式：
```java
if(TransData.containsParam("xxxNewParam")) {
    params.put("xxxNewParam", TransData.get("xxxNewParam"));
}
```
否则后端永远拿默认值，前端 dropdown 切换看似无效。**所有 `getParams()`-style controller 都要审计**：
`QueryChartController` / `IndiaChartController` / `JieQiController` / `LiuRengController` / `BaZiBirthController` / `PaiBaZiController` / `NongliController` / `ZiWeiController`。

#### 2. Java jar 重编 ≠ 进程更新
`mvn package` 替换 `runtime/mac/bundle/astrostudyboot.jar` 后，**进程不会自动重载**。
必须：
```bash
lsof -ti :9999          # 找 Java PID
ps -p <PID> -o lstart=  # 启动时间须 > jar mtime（否则是旧 class 残留在 JVM 内存）
./stop_horosa_local.sh && rm -f .horosa*.pid && ./start_horosa_local.sh
```
如果 launcher 残留进程占着 :9999，本地 dev 重启的 java 也不会绑上来，永远是 stale。

#### 3. lunar-javascript 时柱硬编码 Exact
`EightChar.getTimeGan()` 内部 `timeGanIndex = (dayGanIndexExact % 5 * 2 + timeZhiIndex) % 10`。
`setSect()` **只影响 day pillar，不影响 time pillar**。要自定义时干起算（如 v2.2.1 的 `lateZiHourUseNextDay=0`），必须绕开 `getTimeGan()`、用 `getDayGanIndexExact() / getDayGanIndexExact2() / getTimeZhiIndex()` 自算。前端 `utils/baziLunarLocal.js:computeOverrideTimeGan` 是参考实现。

#### 4. Java 后端 cache：内存 + Redis + 本地文件
`ParamHashCacheHelper`（`spacex/astrostudy/helper/`）三层 cache：
- JVM 内存：重编 jar/重启进程自动清
- Redis（`redis-cli ping` 验存活）：**不会自动清**，调试时 `redis-cli FLUSHALL` 或 `redis-cli KEYS "*chart*"`
- 本地文件：`.horosa-cache/paramhash/`，按 hash 分目录

新增 cache key 字段会自动 miss（key 不同），但改字段类型可能命中错误条目。**`keyparams` 包不包新字段决定是否能区分**——`ChartController:46 keyparams` 是 `params.putAll(params)` 然后 remove gps，所以新字段自动进 key。

#### 5. 客户端 fetchChart in-memory cache
`services/astro.js:5 chartMem` 用 `JSON.stringify(values)` 作 key。新增 values 字段自动 miss；要强制刷新 `requestOptions.cache = false`。

#### 6. AI 必须看到排盘规则 metadata
排盘规则不写进 AI snapshot，AI 模型会**按错误的默认语义**解读四柱。`utils/astroAiSnapshot.js:buildBaseInfoLines` 强制写一行：
```
排盘规则：日柱开关【...】+ 时柱开关【...】。本盘四柱按此规则计算。
```
任何新增的 chart-level 全局开关都要同样在这里加一行，否则 AI 分析结果会与 UI 显示对不上号。

### 工程师级再审计 checklist（任何 day/time pillar 改动后必跑）

```bash
# 1. 前后端字段名全栈一致
grep -rn "lateZiHourUseNextDay\|after23NewDay" Horosa-Web/astrostudyui/src/ Horosa-Web/astrostudysrv/ Horosa-Web/vendor/ Horosa-Web/astropy/

# 2. 所有 Java Controller getParams() 白名单
grep -rn "TransData.containsParam\|params.put" Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/controller/

# 3. 所有 if hour == 23 Python 是否含新开关
grep -rn "if hour == 23\|hour==23" Horosa-Web/vendor/ Horosa-Web/astropy/

# 4. AI snapshot 携带情况
grep -n "after23NewDay\|lateZiHourUseNextDay\|排盘规则" Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js Horosa-Web/astrostudyui/src/utils/astroAiSnapshot.js

# 5. 案例/命盘存储 schema
grep -n "after23NewDay\|lateZiHourUseNextDay" Horosa-Web/astrostudyui/src/utils/localcharts.js Horosa-Web/astrostudyui/src/utils/kentangCaseSave.js Horosa-Web/astrostudyui/src/models/user.js
```

### 跨组件覆盖审计(v2.2.1 学到的教训)

新增任何一个**全局开关**(类似 `dayBoundary` / `lateZiHourMode`)时,审计要点比修单个技法痛 — 必须**全栈对齐**才能"实时重算"真的生效:

1. **`utils/dayBoundary.js`** — 加 helper(常量 + `default<X>()` + `read<X>FromGlobal()` + `normalize<X>()` + `<X>ToBit()`)。
2. **`models/app.js`** — state 加字段 + `globalSetup` 序列化 + `normalizeGlobalSetup` 加规范化。
3. **`components/homepage/PageHeader.js`** — Modal 加单选 + `change<X>()` dispatch + `window.dispatchEvent(new CustomEvent('horosa:<x>-changed', {detail: ...}))`。
4. **`models/astro.js`** — fields schema + `fieldsToParams` 透传 + `sync<X>` reducer + `syncFromGlobal<X>` subscription。
5. **`utils/preciseCalcBridge.js`** + **`utils/localCalcCache.js`** — `NONG_LI_KEYS` / `JIE_QI_YEAR_KEYS` 加字段。
6. **`utils/localcharts.js`** + **`utils/kentangCaseSave.js`** + **`models/user.js`** — 命盘 / 案例 record 加字段。
7. **`utils/aiAnalysisContext.js`** + **`utils/astroAiSnapshot.js`** — AI snapshot 携带 + 显式排盘规则前置行。
8. **各技法组件**(grep `defaultAfter23NewDay` 找出全部 ~20 个):
   - Payload:每处 `after23NewDay: ...` 后**同处加一行** `lateZiHourUseNextDay: ...`。
   - 监听者(`grep horosa:day-boundary-changed`,大约 9 个 `<X>Main.js`):**镜像**写一份 `_<x>UserOverrode` flag + `_<x>Listener` + `addEventListener` + `componentWillUnmount` 解绑。**少一处都意味着该技法不会实时重算**。
9. **Java 后端**(`grep getValueAsInt("after23NewDay"` + `params.get("after23NewDay")`):每个**chart-flow controller** 的 `getParams()` 白名单加,handler 读 + 传给 Model 构造重载。**所有**这类 controller(8+ 个)都要审计 — v2.2.1 有过先漏 7 个的教训。
10. **Java Model**(`grep "boolean after23NewDay"`):BaZi / BaZiDirect / LiuReng / ZiWeiChart / OnlyFourColumns 等加新构造重载(保留旧签名默认值,向前兼容)。
11. **每个时刻都应生效**:核心计算的最里层(`baziLunarLocal.computeOverrideTimeGan` / `BaZiHelper.getTimeColumn`)**必须有 `hour == 23` 守卫**,确保 lateZi=0 时只在晚子时段(23:00–23:59)改时干,其他 22 小时**完全无副作用**。

工程师级 grep 自检命令:
```bash
# A. listener 对齐:after23 与 lateZi 监听者必须 1:1
diff <(grep -rln "horosa:day-boundary-changed" Horosa-Web/astrostudyui/src/ | sort) \
     <(grep -rln "horosa:late-zi-hour-mode-changed" Horosa-Web/astrostudyui/src/ | sort)

# B. default helper 调用者对齐:defaultAfter23NewDay 与 defaultLateZiHourUseNextDay 必须 1:1
diff <(grep -rln "defaultAfter23NewDay" Horosa-Web/astrostudyui/src/ | sort) \
     <(grep -rln "defaultLateZiHourUseNextDay" Horosa-Web/astrostudyui/src/ | sort)

# C. Java controller 白名单对齐
for f in Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/controller/*.java; do
  a=$(grep -c "after23NewDay" "$f")
  l=$(grep -c "lateZiHourUseNextDay" "$f")
  if [ "$a" != "0" ] && [ "$l" = "0" ]; then echo "MISSING lateZi: $f (after23 hits=$a)"; fi
done
```

### Preview 端到端验证模板

```javascript
// 在 preview MCP eval 内执行: 27日 23:30 直接时间 4 case 矩阵
const cases = [[1,1],[1,0],[0,1],[0,0]];
for(const [a23, lzh] of cases){
  fields.date.value.date = 27;
  fields.time.value.hour = 23;
  fields.time.value.minute = 30;
  fields.time.value.second = 20 + a23 * 2 + lzh; // 防 cache
  // ... dispatch fetchByFields with after23=a23, lateZi=lzh
  // 期望:
  //  [1,1] → 壬寅 庚子
  //  [1,0] → 壬寅 庚子（等价）
  //  [0,1] → 辛丑 庚子
  //  [0,0] → 辛丑 戊子 ← 核心新 case
}
```

---

## AI 分析 SSE 流 · Issue #8 双修复（v2.2.1）

**症状**：本地 Ollama 跑 AI 分析,"GPU 加载完后划水,然后停止"。`java.log` 只看到 `ClientAbortException`,看不到上游真正的失败 — 因为根因被 catch 吞了。

**两个独立的 bug,一起修才完整**：

### Trap 7. catch 块吞掉一级异常(可观测性灾难)
`AIAnalysisProxyService.chatStream` 的 catch 内,第一行就是 `sendEvent(emitter, "error", ...)`。一旦客户端已断,`sendEvent` 撞 `ClientAbortException` 并把它包成 `RuntimeException` 抛回 `ai-analysis-chat-stream` 线程 — **而原始一级异常 `e` 只通过 `safeErrorMessage(e)` 进了一个发不出去的 SSE 帧,从来没进日志**。修法:catch 第一步必须 `QueueLog.error(AppLoggers.ErrorLogger, e, "上下文")`,然后把 `sendEvent` / `completeWithError` 各自嵌套 `try`,任一抛出都不能再炸外层线程。

### Trap 8. SSE 流零心跳 → 慢首 token 必断
`streamOpenAICompatible` / `streamAnthropic` / `streamGemini` 顺序读上游 NDJSON,**首字节到达之前不向客户端写任何字节**。Ollama 本地慢模型首 token 要 10–60s,这段静默期 Electron/Chromium/中间件会按空闲门槛(常见 30–60s)切断 SSE socket。后端的 `SseEmitter(0L)`(v2.1.8)只是 server-side 上限,**不防 client 主动断**。修法:三个 `stream***` 方法全部包一层 `withHeartbeat`(本仓 `AIAnalysisProxyService.java` 内),每 15s 给 emitter 发 `: keep-alive` 注释帧;心跳本身 try-catch,撞到 ClientAbort 主动 `emitter.complete()` + 停 schedule。

**release_preflight.sh [7] 哨兵**:`AIAnalysisProxyService.java` 必须同时含 `QueueLog.error(AppLoggers.ErrorLogger` 和 `keep-alive`,任一缺失 → 阻断发布。任何后续 agent 改 AI 分析后端,**先读这两段** 再动手。

### Trap 9. SSE emitter 非线程安全 → 心跳/读流并发写 race(Issue #10,v2.3.1)
v2.2.1 给 #8 加的 keep-alive 心跳线程(每 15s `emitter.send(keep-alive)`,失败自行 `emitter.complete()`)与读流线程(`sendEvent→emitter.send(delta)`)**并发写非线程安全的 `SseEmitter`** → 撞 `ResponseBodyEmitter has already completed`(`sendEvent`)→ 断流(deepseek-reasoner「几句话后停止」)。修法:所有 emitter 写收口到线程安全 `SseChannel`(单锁串行化 + `closed` 幂等 + 关闭后 `send` 返回 false 不抛),**心跳不再自行 complete**(收尾统一在 `chatStream`)。保留 #8 的 `QueueLog.error` + `keep-alive`。

### Trap 10. SSE 标志 `__sse__` 跨请求污染 → 间歇 signature.error 打挂排盘/predict(Issue #10,v2.3.1)
`TransData.setSSE(true)` 实为 **`request.setAttribute("__sse__", true)`(绑 request 对象,不是 ThreadLocal)**,而 `pureClearTransData()` 只 `.clear()` 五个 ThreadLocal map、**碰不到 request attribute**。Tomcat 池化复用 `HttpServletRequest` 对象 → 上个 SSE 请求残留的 `__sse__=true` 被复用到排盘/`predict` 请求 → `RequestHeaderInterceptor.complete():595` / `afterCompletion:744` 的 `isSSE()` 误判(**且排在可靠的「handler 返回类型是否 `SseEmitter`」判定之前**)→ 响应被当 `text/event-stream` 返回、跳过正常 JSON → 前端 `signature.error`/「本地排盘服务未就绪」/`predict 200 报错`。间歇性取决于对象池复用(失败、一分钟后又成功)。修法:`preHandle` ① 非 `REQUEST` dispatch 早返回(免 async re-dispatch 用空 body 重复验签);② `REQUEST` 进来 `TransData.setSSE(false)` 归零。详见 [`../docs/服务不稳定-SSE并发与签名污染修复-v2.3.1.md`](../docs/服务不稳定-SSE并发与签名污染修复-v2.3.1.md)。

**release_preflight.sh [10] 哨兵**:`AIAnalysisProxyService.java` 必须含 `SseChannel`;`RequestHeaderInterceptor.java` 必须含 `getDispatcherType() != DispatcherType.REQUEST` 早返回 + `TransData.setSSE(false)` 归零。

---

## 其他长期注意（与日界点无关，但 agent 进来常错）

- **GitCode 镜像已停用**（2026-05-27 起），不要跑 `mirror_to_gitcode.sh`，发布只发 GitHub。
- **回复用简体中文**；代码/路径/命令保持原文。
- **不在代码/测试/文档里使用近现代政治人物**作为命例（用 `邵康節` 等古人或中性八字/卦）。
- **术数语义色**（格局/五行/天将/星曜）属用户拍板，不能因「夜间模式不一致」之类理由动；只能改结构/中性色。
- **每个 Mac 修复都要配技术文档**（`docs/<topic>-v<ver>.md`）+ `docs/windows-sync-handoff.md` 顶部条目；`release_preflight.sh` 应当门禁版本号 + 同步条目。
- **技法专属算法选项 → 放该技法左栏**（`KinAstroMain` per-技法 state + `<Select>` + prop，镜像参评数 `canpingMethod` / 河洛「取化工法」）；**全局设置 Modal 只放跨技法全局开关**（日界点 / 晚子时）。误放全局设置须回退（v2.3.0 河洛取化工法踩过）。
- **发布前做过 `git checkout`/`merge`（如 ff `main`）→ 必先重建 `dist-file` + touch/重编 jar，再 `build_desktop_release.sh`**：git 会把切换文件的 mtime 顶到「现在」，让 `package_runtime_payload.sh` 的 freshness guard 误报「dist-file/jar 比源旧」（内容其实是新的）。正确顺序：git branch 操作做完→重建 dist-file→`touch` 两个 jar（内容已确认当前时）。详见 `horosa-dev` skill「Safeguards」章。
- **改任何 runtime 端点的响应结构 → 必须同步更新 `astrostudyui/scripts/verifyHorosaRuntimeFull.js` 的对应检查**。

---

## 西占推运 + 宫制（v2.5.0 起）

- **双圈盘/推运组件「内圈本命冻结」坑（实测对不上选的盘）。** `AstroPersianDirected`/太阳弧族这类组件**构造时**用 `natalParams(props.value)` 把本命字段(date/time/lat/lon/zone)一次性写进 `state.params`，而 `componentDidUpdate` 换盘只重新**请求**、**不重算 natalParams** → app 初始默认盘是「now 盘」(birth=今天)，切到真盘后 `state.params.date` 冻结成今天 → 后端 `PerChart` 按 `data['date']` 把**内圈本命**按今天起盘。**修法=`requestData` 每次从当前 `props.value` 重算 `natalParams` 并 `{...state.params,...np}` 覆盖**(`AstroSolarArc` 靠 `props.hook.fun`/`genNatalParams` 避开)。**凡「构造时一次性 derive 本命 + update 不重 derive」的盘都会犯**，新增此类组件务必在 request 路径重算。React dev 会 shallow-freeze props，fiber 调试只能改 `props.value.params.xxx` 嵌套字段、不能整体替换 `props.value`。
- **自定义「整宫家族」宫制的 `inHouse` -5° 偏移坑（落宫 off-by-one）。** flatlib `House.inHouse` 只在 `self.hsys == const.HOUSES_WHOLE_SIGN` 时用 `distance(self.lon, lon)`；**否则**用 `distance(self.lon + House._OFFSET, lon)`(`_OFFSET=-5.0`)。所以「福点整宫制」这类自定义整宫制，重定位宫头后**每个 `house.hsys` 必须设成 `const.HOUSES_WHOLE_SIGN`**（不是自定义标记 `'Fortuna_Whole'`），否则福点/行星落宫整体差一宫。**盘级宫制中文名靠盘的 `hsys` 参数(24→福点整宫制)驱动，不靠逐宫 `house.hsys`**，所以这样设不影响显示。
- **新增 house system 三处同步（缺一即错位）。** ①后端 `astropy/astrostudy/perchart.py` 的 `hsys[]` 列表——**只能追加到末尾**(新 index)，**勿插中间**否则所有后续宫制 index 全错位、老盘读错宫制；自定义算法的再加 `custHouse_*` 常量 + `__init__` 里 `houseCust` 检测(底盘退化成某标准制) + `custHouse()` 分支重算 12 宫头。②前端 `constants/AstroConst.js` `HOUSE_SYSTEM_OPTIONS` 追加 `{value:<同后端index>, label}` + `HSYS_* ` 常量。③`constants/AstroText.js` 加 `AstroMsg[HSYS_*]` 标签。
- **改 `astropy/**/*.py` 后必须重启 Python chart 服务**(CherryPy 不热重载)：`./stop_horosa_local.sh && HOROSA_SKIP_UI_BUILD=1 ./start_horosa_local.sh`，否则 preview 仍跑旧码(直接 `python -c 'from astrostudy.perchart import PerChart'` 跑临时脚本验证逻辑则用的是新码——别被「脚本对、preview 错」误导)。注：curl 直打 `/predict/*` 会得 `no.register.app.in.sys.forapp:`(缺前端注册头)，**不代表后端坏**，要从前端 UI 验证。
- **Balbillus 算法口径**(还原自 129-year Balbillus 变体，独立 `utils/balbillus.js`，**不碰** decennials.js)：七星 Balbillus 小年(日19/月25/土30/木12/火15/金8/水20=129) → 主限长度 `= N×(1 − d/360)`，d=本命星黄经离其**擢升度**的角距(`nearest` 最近角距 / `forward` 顺黄道距，做成参数) → 主限序=七星按本命黄经升序、从**起始星**旋转 → 每主限再以该期主星为起点按 **129 权重**递归切子限(可 5 层) → 日期用 Hellenistic **360 日年**(可切 solar)。UI=antd `Tree` 懒加载(`loadData`)。起始星/年制/距离口径做成左栏选项；mode 默认 nearest，精校需对 同**本命**盘(其面板经度是 transit 盘、勿误用)。
- **行星 tab 底部空白 + 七政卡片矮**根因：`AstroPlanet`/`AstroLots` render 内部 `height-130` 过减 → `0.68t+0.32t` 只渲染 `t−202px` 内容、容器满高 `t` → 底部空白。**修法=`.horosa-planet-with-lots` 改 `display:flex;flex-direction:column`，`AstroPlanet` 加 `fill` 模式(`flex:1;height:100%`)撑满、`AstroLots` 加 `natural` 模式(内容高)**。别再用「固定百分比 height」拼两块。

---

## 本地服务端口健壮性（v2.5.0 起）

- **「排盘失败：本地排盘服务未就绪」/ Windows `portend.Timeout: Port 8899 not free`（code 70）反复起不来** → 根因 = 上次实例崩溃/强退后**僵尸 python 仍 LISTEN chart 端口**，新实例 CherryPy `portend` 直接「Port not free」退出。成熟修法在**共享** `astropy/websrv/webchartsrv.py`（Mac+Windows 同一份，桌面壳都 bundle 它）：`__main__` 里 `cherrypy.engine.start()` 前调 `ensure_chart_port_free('127.0.0.1', chart_port)` —— 探测端口 → 定位 LISTEN 该端口的 PID → **仅当命令行含 `python`+`webchartsrv`/`astropy`/`horosa`（即我们自己的僵尸）才 kill** → 轮询等 OS 释放后重试。跨平台（win=netstat/taskkill、posix=lsof/SIGKILL）。
- **dev 启动器 `start_horosa_local.sh` 同理**：旧逻辑端口被占就 `exit 1` 阻死；现 `reclaim_stale_port <port> <tag>`（tag=`webchartsrv`/`astrostudyboot`）只回收**自己的**僵尸再继续，非 Horosa 占用才报错退出。
- **铁律：回收必须靠命令行 tag 精确匹配「我们自己的进程」，绝不无差别 kill 端口占用者**（会误杀用户其他程序）。`release_preflight.sh [12]` 哨兵守 `ensure_chart_port_free` + `reclaim_stale_port` 在位。
- Windows 桌面壳是独立 repo，但 bundle 的就是这份共享 `webchartsrv.py` → 同步后端即获修复；桌面壳自身若再在 spawn python 前先清僵尸更稳（已记 handoff）。

---

## 时区 / 夏令时（DST）自动校正（v2.5.0 起）

> 背景：出生时间的时区原本是 `DateTimeSelector.genZone()` 的**手动固定偏移下拉**（东0区…），**全程零 DST**。夏令时地区的夏季/DST 出生盘若选了标准偏移，盘会差 1 小时（月亮 ~0.5°、ASC/宫位整体偏）。成熟方案 = 依出生地经纬度 + 日期自动求**含夏令时**的 UTC 偏移并回填。

- **方案 = `tz-lookup`(经纬度→IANA 时区名，离线 ~1.5MB) + 浏览器原生 `Intl.DateTimeFormat({timeZoneName:'longOffset'})`(IANA+日期→含夏令时偏移)。** 全离线、零网络（桌面断网可用）；`Intl` 内置完整 IANA 历史库（含 1918 等历史 DST 规则，Hamburg 1918-12 正确给 +01:00）。引擎在 `utils/timezone.js`：`ianaTimezoneAt` / `offsetForZoneAtDate` / `isDstActiveAt` / `dstAwareZoneAt`，外加**共享回填** `applyDstToFields(flds)` + 日期字段兼容取值 `dstDateField(flds)`。
- **🔴 三个表单共用一套，缺一即「在那个位置没啥用」。** 用户实测：只接 `ChartFormData`(星盘配置/query) 不够——真正建盘/改盘的是**命盘库表单 `user/ChartData.js`**(新增/编辑命盘 chartadd/chartedit，经 ChartAdd/ChartEditFormComp) 和**事盘库表单 `user/CaseData.js`**(添加/编辑起课 caseadd/caseedit，经 CaseAdd/CaseEditFormComp)。三者**日期字段名不同**：ChartFormData=`flds.date`(+`flds.time`)、ChartData=`flds.birth`、CaseData=`flds.divTime` → 故用共享 `dstDateField` 兼容、共享 `applyDstToFields` 回填、共享 `<DstZoneIndicator>` 渲染。新增任何带「时间+经纬度」的表单都照接这三件套。
- **回填三件套（每个表单都接）**：① `changeGeo`(地图选点，重置 `zoneManual=false`) / `changeLat` / `changeLon`(手填坐标，仅 `!zoneManual`) / `changeBirth`|`changeDivTime`(改日期，仅 `!zoneManual`) 调 `applyDstToFields(flds)` —— 算偏移 → 写 `flds.zone.value` + **克隆 DateTime 换新引用** `setZone()`(保留本地钟点、只改偏移)。**坑：必须换新 DateTime 引用**，否则 `DateTimeSelector.render()`(line 765-773「`this.changing===false` 时 `this.datetime=this.props.value`」) 不从 props 重同步、下拉时区不更新（实测「东1区→东8区」靠此生效）。② 渲染 `<DstZoneIndicator fields={flds} onApply={this.applySuggestedZone}/>` 紧贴时间行下。③ `applySuggestedZone()` = `zoneManual=false`+`applyDstToFields`+`setState`。
- **手动覆盖优先（防回归）**：`this.zoneManual`——`changeBirth/changeDivTime` 里 `newZone !== prevZone`（用户手动改时区下拉）置 `true`，此后日期变化**不再**自动覆盖；`changeGeo`(明确换地点)重置 `false`。**载入已存盘不触发自动**（只 user change 动作触发）→ 老盘时区零改动。
- **指示 UI = `components/comp/DstZoneIndicator.js`**（可复用，自带 `(lat|lon|date)` 缓存）：渲染 `.horosa-dst-indicator`（`app.less` 末尾 `:global` 段，结构/中性色走 token、明暗双适配）：`🌐 IANA名 · [夏令时/标准时 chip] · UTC±HH:mm · 已自动校正`；当前盘偏移 ≠ DST 正确值时显示「当前 X · **改用 Y**」可点 pill（opt-in 不强改）——专治已存的错时区老盘。
- **储存/AI 全链路同步是「天然」的（zone 一等公民）**：三表单保存都走 `for(key in flds){ params[key]=flds[key].value }`(ChartEdit/CaseEditFormComp 等) → 校正后的 `flds.zone.value` 直接存为 `record.zone`；AI 挂载重算读 `record.zone`（`aiAnalysisContext.js` `parseBirthString(record.birth, record.zone)` + 重算 fields `zone:record.zone`）；AI 导出快照含 `时区：${record.zone}`。**故无需为 DST 单独接导出/挂载——只要校正值落进 `flds.zone` 即全链路一致**（DST 非技法、不新增导出 section）。
- **Horosa 排盘引擎本身的 DST 处理是正确的**（zone 偏移直接进 jd），gap 只在「APP 让用户选了错 offset」；本方案补**输入端自动给对 offset**，不动任何排盘/已发推运算法。地点选择器仍是高德 amap（只给 lat/lng），DST 全由前端 `tz-lookup`+`Intl` 兜。事盘的中式技法(六爻/奇门…)干支按本地钟点算、`setZone` 保钟点 → 校正 zone 对其无副作用，对卜卦/世俗等占星事盘则更准。
- `release_preflight.sh [13]` 哨兵守 `tz-lookup` 依赖 + `timezone.js`(`applyDstToFields`) + `DstZoneIndicator.js` + 三表单(`ChartFormData`/`ChartData`/`CaseData`)均接 `applyDstToFields`+`DstZoneIndicator` 在位。

---

## 桌面外壳 · 更新后启动（v2.3.0 起）

> 机制细节 + 实测见 [`../docs/更新后启动卡顿修复-v2.3.1.md`](../docs/更新后启动卡顿修复-v2.3.0.md)。症状:更新后第一次重启「卡在 100% 很久才进」。

- **`start_horosa_local.sh` 的 pid 检查必须「判存活」不是「判存在」。** 旧逻辑只要 `.horosa_*.pid` 文件在就 `exit 1` —— 上次崩溃/强退留下的死 pid 会**永久误拦截**启动(即坑#2「launcher 残留进程占 :9999」的另一面)。现用 `prune_stale_pid_file`:`kill -0` 探测,死 pid 自动清除再继续。**别把它退回成纯文件存在判断。**
- **更新「首次启动」走一条故意放慢的全量校验路径**(Tauri `main.rs` `runtime_bootstrap`,由 `update-complete.txt` 标记触发):`trusted_runtime=0` + `fast_path=false` + 300s 超时。完整校验要留,但「等待提示 / warmup / mongo ping / 轮询粒度」是开销不是校验,可削:
  - warmup 在脚本内**后台非阻塞**(`( … ) >/dev/null 2>&1 &`)——外层必须重定向切断对脚本 stdout/stderr 的继承,否则后台进程持有 Rust `command.output()` 的 pipe,脚本永远「返回不了」。
  - 轮询 `poll_interval` 与 `trusted_runtime` **解耦**(非 trusted 也用 0.2s)。
- **更新标记必须「读取即消费」。** `update-complete.txt` 若只在启动**成功**时删,首启一失败就残留 → 下次仍走 300s 慢路径,反复卡。现 `main.rs` 一进 `runtime_bootstrap` 就 `consume_update_complete_marker_into_state`(缓存通知到 `AppState` 后立即删标记),成功后从内存弹「更新完成」窗。
- **更新后「首启」别再走「全量慢校验」——它是冗余的(v2.3.2 修)。** `apply_update` 装前已 `verify_sha256(runtime_sha256)`,装进去的 runtime 是逐字节验签过的;但 `runtime_bootstrap` 旧逻辑 `fast_path_enabled = !first_launch_after_update && …` **强制**首启全量,而让后续变快的 fast-path 标记**只在「整轮成功」后才写** → 冷首启 ~22s 像卡死被强退 → 标记没写 → 下次又全量 → **反复重启两三次才打开**(真机一次更新三启 trusted=0/0/1)。修法:对已验签 runtime 在 `start_runtime` **之前**就 `write_runtime_fast_path_marker` 预写标记 + 取消 `fast_path_enabled` 对首启的强制关闭 → 首启即快路径、强退也不回退全量。详见 [`../docs/更新后自启修复-v2.3.2.md`](../docs/更新后自启修复-v2.3.2.md)。**别把首启退回成无条件全量校验。** 注:`update-installer.log` 的 `[open] relaunch confirmed` 证明 helper 自动重开本身没坏,卡的一直是首启那段。
- 以上各点有 `release_preflight.sh` **[9] 哨兵(C①/A/C②/B/D)**兜底,别绕过。

---

## 金口诀解读层（jinkou 判语 / 四位生克 / 应期 / 神煞，本轮新增）

新增「解读层」：`components/jinkou/JinKouDoc.js`（判语库）+ `JinKouCalc.js`（`buildJinKouData` 解读层字段 + `normalizeKinjinkouData` 重算）+ `JinKouMain.js`（分析/辅助 Tab）+ `JinKouRelationMini.js`（刑冲合害破 SVG）+ `liureng/LRConst.js`（`ZiHai/ZiPo/TaiXuanNum/WuXingNum`）。**踩过的坑，勿重蹈：**

1. **`buildRow()` 不返回 `branch`**（只用 `option.branch` 算空亡）。任何「按行的地支」派生逻辑（地支关系/太玄数）必须用 `rowZhi(r)=r.branch||(ZiList 含 content?content:'')` 从 `content` 兜底，否则取不到支、永远空。
2. **本地 `buildJinKouData` 行 ≠ 后端 `kinjinkou` 行**（月将算法差一位 → 将神/贵神可能不同），而画面/三盘用后端行。**解读层必须在 `normalizeKinjinkouData` 用「显示行(后端 rows)」重算**（relations / branchRelations / taixuan / yongStrength / yingQi），**不能直接用本地 fallback**，否则判语跟画面对不上（no-串盘 invariant）。`buildJinKouData` 已 return `dayZi/yearZi` 供重算。
3. **`JINKOU_SHENSHA_DOC` 的键必须覆盖 `JinKouShenShaOrder` 全部起例名**，否则该神煞显示空判语 + 默认中性色（`天德合` 踩过）。已加 jest 守护（`JinKouCalc.test.js`「所有起例神煞都有判语」）——加新起例神煞时**同步加判语**。
4. **`LRConst` 本就有 `ZiXing`（刑，单向 `{支:支}`）和 `ZiCong`（六冲）**——别重声明（babel 会「重复声明」直接报错，jinkou 首次落地踩过）；`ZiHai/ZiPo` 才是本轮新增。刑是单向映射，判关系要**双向**查 `map[a]===b||map[b]===a`。
5. **jest 过 ≠ 能编译**：批量 Edit 误留 orphan 方法签名时 **jest 通过、`npm run build` 才报 `Missing semicolon`**。改完 jinkou（尤其大段 JSX）**必跑 `npm run build`** 再认定通过。
6. **全链路同步（缺一处就漏）**：解读层进 `buildJinKouSnapshotText` →`saveModuleAISnapshot('jinkou')`（**AI 分析挂载 + 命盘/事盘储存共用同一快照**）；导出再进 `utils/aiExport.js` `AI_EXPORT_PRESET_SECTIONS.jinkou`（**AI 导出 / 导出设置**，节名须与快照 `[段头]` 一致）。新增快照段必须**两处都加**，否则导出选不到。
7. **UI**：右栏 4 Tab（概览 / 神煞 / 分析 / 辅助）；概览合并「课情/四位/三盘/四位类象」；神煞子 Tab「支煞/年煞/长生/四煞」。神煞吉凶用 `jxColor(jx)`→语义色变量（`ji/xiong/zhong`），**勿写死 hex**。**判语来源不得留任何第三方 App 痕迹**（公版古籍 + 复用 `LRShenJiangDoc.js`，重编）。
8. **不臆造**：五动/三动规则、除「经营求财」外 12 类取用神、六壬合占 14 类——按门派分歧，字段/结构预留、留 `// TODO（待底本/实测）`，**别瞎填**。

---

## 七政四余 · Moira 模式（`components/guolao/`，对齐 Moira app）

**渲染时序、状态归属、命盘轮还原，踩过的坑勿重蹈：**

1. **一次性渲染（禁止分步跳出）**：起盘/重算必须经 `GuoLaoChartMain.requestGuolaoBundle`——本命盘 + 流年盘 `Promise.all` 并行取齐、Moira 规则取回后**单次 `setState` 全量提交**（唯一 `this.bundleSeq` 守竞态）。期间只显示骨架(`renderGuolaoChartSkeleton` / 面板 `horosa-guolao-moira-skeleton-row`)或保留旧盘，**绝不画半成品**。旧的多段链路 `applyChartObj→requestMoiraTransitChart→requestMoiraRules→commitMoiraPanel` 已废弃成死方法，**勿复活、勿再加中途 setState**。中栏 wheel 与右栏 panel 必须读**同一**已提交 `chartObj`（`moiraPanelChartObj===chartObj`）；`GuoLaoMoiraPanel` 在 `loading` 时**不得**预渲染 `buildPanelFallbackValue` 空壳（否则规则到达时二次跳变）。
2. **显示偏好 = 组件 state + localStorage（`GuoLaoChartStyle.getStoredGuolaoDisplay`），不进 fields**：相位多选/庙旺标注/本命神煞圈/限度年龄环切换 → **即时重绘 wheel、不触发后端重取**（props 传 `aspectSet/showDignity/showBirthGods/showAgeRing`）。只有**影响排盘的**选项（宿度制/命度/罗计/身度/昼夜/大限算法）才进 `fields` → 触发 bundle 重算。别把显示开关塞进 fields，否则每次切换都白跑一次 `/chart`+`/qizheng/moira`。
3. **本命神煞圈半径固定** `birthOuter = r(9)-8`（常量），**不可**随 `showMoiraTransitGods` 在 `r(9)-8`/`r(10)-12` 间变——否则取消流年神煞圈后本命圈外扩变形。
4. **紫炁在 Moira 链路本就正确**：喂 Moira 的 chartObj 由 astropy `perchart` 产出，紫炁(PURPLE_CLOUDS)是约 28 年匀速虚星（实测今日 168.3°，与 Moira 公式 `230.5+(JD−JD(1975-03-13 16:00 UT))/10227.1792×360` ≈168.8° 吻合，与月孛 258° 分明）。`紫氣=swe.OSCU_APOG` 的 bug **只在 kinastro**（`vendor/kinastro/.../qizheng/constants.py`，本轮不碰、也不喂 Moira）。**勿对 Moira 紫炁再加覆盖**（画蛇添足）。
5. **逐神煞悬浮判语**：`GuoLaoShenShaDoc.GUOLAO_SHENSHA_DOC`（公版古籍口径、自有重编、零第三方 App 痕迹）键名 = wheel 的 `BIRTH_GOD_ORDER`∪`TRANSIT_GOD_ORDER`。`renderGodRing` 给每个神煞单独热区 + `guolaoShenShaTip()` 判语（保留宫级 summary 作底层）。jest `__tests__/GuoLaoShenShaDoc.test.js` 守全覆盖——往 wheel god order 加神煞 → **同步加判语**否则测试红。
6. **`GuoLaoMoiraPickWheel`(天星择日动盘) 与命盘轮共用** wheel 的导出 helper（`moira*`）+ 同一 `GUOLAO_SHENSHA_DOC`；其 24 山环(`renderMountainRings`)是择日方位概念——**24 山只放 PickWheel、勿叠到本命黄道盘**（azimuth≠黄经，叠上去不还原）。
7. **24 山/择日自动搜时（太阳到山·日月蚀·评分排名）尚未实现**：PickWheel 现为「动盘 + 24 山 + 神煞」手动择时盘，自动搜时引擎是 TODO。
8. **右栏多 Tab**：`GuoLaoMoiraPanel` 内用 antd `Tabs items=[概览/星曜/宫限/神煞/格局]`，className **必须** `horosa-content-tabs horosa-guolao-tabs`（沿用原「Moira」单 tab 的样式，否则风格不一致）；`GuoLaoChartMain` 右栏**不再**包单 pane `<Tabs><TabPane tab="Moira">`（会变双层 tab）。卡片内距已收紧（section `7px 9px`、卡片 `5px 7px`、行 `min-height 22`），勿回退成 10px/8px 大留白。
   - **坑：卡片被撑满高（巨大留白）的真因**＝`app.less:5266` 的 `.horosa-workspace-shell .horosa-content-tabs .ant-tabs-tabpane > * { height:100% !important }`（为「单满高面板」设计，撑高所有 tabpane 直接子元素）。本面板每 tab 是多张卡 → 全被撑满。**必须用更高特异度覆盖**：`.horosa-workspace-shell .horosa-guolao-moira-tabs.ant-tabs .ant-tabs-tabpane > * { height:auto!important; max-height:none!important }`（`.x.ant-tabs` 凑 0,4,0 > app.less 0,3,0），并给 `.ant-tabs-tabpane` 加 `overflow-y:auto`（pane 满高自滚）。同特异度 + 同 `!important` 会输给加载顺序，务必抬特异度。
   - **坑：神煞卡字挤**＝曜名长串 + 全局 `line-height:18` 偏紧 → `.horosa-guolao-moira-gods .horosa-guolao-moira-god` 单独放宽 `line-height:20` + 宫名/支/曜 间 `margin`。
9. **中盘四柱（`renderSideText`）读 `bazi.year.stem.cell + bazi.year.branch.cell`**（结构非 `.text`！），与右栏 `baziText` 同源；`root.nongli` 常 undefined → 用 `chart.nongli.bazi`。原只读 `.text` → 月/日/时柱空、只剩年柱（踩过）。
10. **PickWheel 28 宿环＝逐像素照抄 Moira 命盘轮**（用户原话：「一个圆环里层外层都有刻度、刻度都贴在圆环上、中间红线不挨任一圆、刻度底端贴着两个圆」）。结构＝**两个边界圆 `r(4)`/`r(6)`（`PICK_RING_DRAW_TYPE` 均=1、已画）框住宿区**，内部用**计算半径**按 **20%/60%/20%** 切三带（`band=r(6)-r(4)`、`rA=r(4)+band*0.2`、`rB=r(6)-band*0.2`）：
    - `renderStellarTicks`：内带 `renderDegreeMarkBand(r(4), rA, {anchor:'inner'})` 底端贴 `r(4)` 向外伸 ＋ 外带 `renderDegreeMarkBand(rB, r(6))`（默认 anchor=outer）底端贴 `r(6)` 向内伸 → **里外各一条刻度带、各贴一个边界圆**（720 条＝360+360）。
    - `renderStellarRing`：宿名 `verticalText` 居中于 `(r(4)+r(6))/2`；红色宿界线 `radialLine(edgeTheta, rA+1, rB-1)` **只在中间空带、不挨 r(4)/r(6)**（对齐 Moira 的 `r(5)+1~r(6)-1` 做法）。
    - 几何自检（preview eval 实测）：R=560 → r(4)=285.6 / r(6)=336；宿名半径 310.8（正中）、刻度 285.6↔336（底端贴两圆）、红线 296.7↔324.9（距两圆各≈11px 浮空）。
    - **勿**回退成单刻度带（历史 bug：刻度只一圈 / 游离到 r(7)-r(8) / 与宿名重叠在 r(4)-r(5) → 「只有一圈、奇怪」，用户为此反复退回）。注意 PickWheel 版 `renderDegreeMarkBand` 签名是 `(inner, outer, keyPrefix, opt)`（**无** thetaForDegree 参，内部固定 `pickThetaFromDegree`；命盘轮版多一个 thetaForDegree 参，勿混用）。
11. **格局显示档位**：左栏「显示」分区底部按钮 + 底部快捷功能 dock **双入口**，均 `openMoiraQuickDialog('patterns')`（同一 styleLevel 模态）。
12. **时间组件全链路**：本命 `fields.date/time/zone → genParams → /chart + /qizheng/moira + saveGuolaoAISnapshot`；流年 `Moira流年时间 → paramsWithMoiraTransit → transitParams`。右栏「起盘与流年/真太阳与出没」+ 中盘 `renderSideText`（四柱/流年/时间）均取自此，改时间组件后这几处要一并核。
13. **AI 快照 4 段 + 大限同步**：`buildGuolaoSnapshotTextV2` 输出 `[起盘信息]/[七政四余宫位与二十八宿星曜]/[神煞]/[大限]` 四段。`[大限]` 由 `buildGuolaoLimitSection` 复用 wheel 导出的 `moiraLifeDegree(chart,fields)` + `moiraBuildLimitTable(life, birthYear)`，与盘面「命身与限度·大限」**同口径**（出生年取 `params.date` 前 4 位）。**新增/改快照段必同步 4 处**：① 快照 builder ② `aiExport.js` 段表 `guolao:[...]`（**line 359**，否则「AI导出设置」不识别该段、不可勾选）③ 挂载＝`aiAnalysisContext`→`buildGuolaoSnapshotForFields`→**同一 V2**（自动含新段、无需单独改）④ 命盘事盘储存只存 `fields`、快照/大限**读取时重算**（派生字段、不入 schema）。**勿**只改 builder 漏掉 ② → 导出设置与实际快照段不一致。
## 紫微 运限/格局深度增强（v2.5.8）— 5 个会反复踩的坑

紫微补「运限体系(八字式级联条) + 格局自动识别」时踩到的坑，逐条都做了 code guard / 自检：

1. **新后端路由必须重编 `astrostudyboot.jar`（gotcha #10）。** `/ziwei/luck` 与 `/ziwei/birth` 的 `patterns` 在 `astrostudycn`；本地/发布都不自动重编 fat jar。须 `mvn -o -f astrostudycn/pom.xml install -DskipTests && mvn -o -f astrostudyboot/pom.xml clean package -DskipTests`，`javap` 验 `ZiWeiController.luck()`/`ZiWeiLuck.build`/`ZiWeiPattern.detect` + `ziweige.json`/`ziweiliuchangqu.json` 进 jar，再 `stop+start` 重启。不重启 → /ziwei/luck 500。

2. **`ZiWeiHelper.getDouJun(month,timezi)` 后端是「月名」查表，传地支必 NPE**（`Cannot invoke "java.util.Map.get" because "map" is null`）。斗君宫 index = `(子斗支idx + 流年支idx)%12`（同 `ZiWeiChart` 构造法），用 `ZiWeiLuck.doujunIdx()`，勿调 `getDouJun(地支)`。⚠️ 前端 `ZiWeiHelper.getDouJun` 是 index-add 版（与后端同名不同义），勿混用。

3. **`getSmallDirectioinHouse` 女命分支历史 bug**：`(idx-startidx)` 应为 `(startidx-idx)`（女命亦从辰/戌/丑/未起再逆行）。小限无前端呈现故长期未暴露。

4. **紫微 `houses[]` 数组下标 ≠ 固定地支位置（最易翻车）。** `houses[0]` 地支随盘而变。任何「地支→houses 下标」必须按 `houses[].ganzi.charAt(1)` 搜索（前端 `houseIdxByBranch`），**绝不能用 `DIZI.indexOf`**，否则流命环/四化落宫/小限起宫全部差位。

5. **运限/格局面板在 ziwei tabpane 会被 flex 居中。** 新面板根需 `display:block; align-self:stretch; overflow-y:auto`，**不要**复用 `horosa-astro-content-scroll`（它是 grid 居中），否则卡片整体垂直居中而非顶部起排。

6. **运限层级结构（v3 定稿，勿改回单卡/单链）。** 层级 = 大限 → **流年/小限同一 tier（竖向双键 toggle `.horosa-ziwei-luck-annual-toggle` > `.horosa-ziwei-luck-toggle-btn`，占左侧层名列、互斥、只显其一，各 10 槽=该大限的 10 虚岁/年）** → 流月 → 流日 → 流时。**toggle 与级联 chip 必须同视觉语言**：选中态都用金渐变 `.is-on`/`.is-selected`（曾因 JSX/CSS 类名不一致导致 toggle 无样式、看不出选中——改 JSX class 必同步改 app.less，二者都用 `.horosa-ziwei-luck-toggle-btn`）。详情区是**多层四化卡叠加**：每个已选层级各一张卡（`render()` 里 `cards=[daxian, activeAnnual(), liuyue?, liuri?, liushi?].filter`），不是只显最深层。`activeAnnual()` 按 `state.annualMode` 取 `liunian`/`xiaoxian`；`deepest()` 仍驱动流命环。改运限时务必保持「流年/小限互斥同级」+「全选层级各出一卡」两条语义。

**自检（任何紫微运限/格局改动前后必跑）：** ① `npm test` 全绿（aiExport 9 / aiAnalysisContext 16 / 全 140）；② 预览董盘 `1985-02-13 22:38 女 +08:00 119e18 26n06`：运限 = 大限行 + 流年/小限 toggle 行 + 流月/日/时，逐层钻取；**选大限+流年+流月时详情区同时叠 3 张卡**（各带本层四化），切到流时时叠 5 张卡；toggle 切「小限」后年级行变虚岁链(女命逆行 12岁壬辰→13岁辛卯…)、卡片随之变小限；选中最深层流命环落位；格局命中「府相朝垣(富贵·破)」顶部起排；③ 本命/大限态盘面与改前像素级一致；④ 明暗双主题无重叠。完整记录见 `../docs/紫微斗数-深度增强-运限格局-v2.5.8.md`。

## 六壬 起课法/换将/分昼夜（纯前端 castOverride 机制，不动 Java）

**最关键认知：六壬天地盘/四课三传是前端算的，后端发三传休眠。** `LiuReng.calculate` 仅当传 `yue` 才算 `keCuang`，而前端不传（注释掉）→ 后端那条路是死代码。天地盘实由**两处前端**各自算（`delta=月将idx−时支idx`）：① 断辞侧 `LiuRengMain.buildLiuRengLayout`；② 渲染侧 `LRCommChart.genYueJiangIndex/genHouseTianJiang/getKe`（`RengChart` 经 LRTextSquareChart/LRCircleChart 用）。**故起课法/换将/分昼夜全前端、不动 Java、不重编 jar。**

**统一 castOverride（零回归）。** `buildLiuRengCastOverride(chartObj, state)→{yue(天盘起支),timeZhi(地盘临位),isDiurnal}`，全默认返 null＝正时正将＝逐字现状。同喂两处：断辞侧作 `buildLiuRengLayout/...ReferenceBundle/buildLiuRengSnapshotText` 末参；渲染侧走 prop 链 `LiuRengChart(prop)→RengChart(opt×3)→LRCommChart`，**完全仿 `guireng` 接法**（含 `componentDidUpdate` 比较触发重绘）。`LRConst.getGuiZi(chartObj,guirengType,isDiurnalOverride)` 加可选昼夜覆盖（断辞/渲染共用）。

**算法 `computeQiXY`（每法＝天盘起支 X 加 地盘临位 Y；天干用 `GanJiZi` 寄宫）。** 14 法：正时正将(默认)、八客①–⑧、四柱对齐(年日/年时/月日/月时＝直接对齐两柱地支)、选时(Y=所选时支，需 `xuanShiZhi` 输入)、演数(Y=正时宫±N 阳日顺/阴日逆，需 `yanShuNum` 输入)。换将：中气过宫(默认=`getSignZi(sun.sign)`)/节气换将(太阳黄经+15°取宫)。分昼夜：晨昏(默认=星历 isDiurnal)/卯酉/寅申。

**坑：**(a) **贵人起法早已实现**(`guireng` 选择器+`GuiRengs[3]`)，勿重做。(b) retrograde 取 `obj.lonspeed<0`，**非** `obj.retrograde`(那是 GuoLao 重塑字段)。(c) 起课法/换将/分昼夜是**显示层**参数(不动 /chart)，同 guireng：`setState` 即重排、**不进 localCalcCache 键、不重新起课**。(d) **需输入的起课法(选时/演数)在选中后才条件渲染对应输入框**(`castMethod==='xuanshi'/'yanshu'`)——新起课法若需额外输入，务必同时加条件输入控件。(e) antd 起课法 Select 14 项虚拟化，e2e 验证需滚 `.rc-virtual-list-holder` 才见底部 选时/演数。

**全链路(已接，改动须保持)：** 储存＝`clickSaveCase` payload 带 5 字段(castMethod/xuanShiZhi/yanShuNum/yueJiangMethod/fenZhouYe)；AI挂载＝`aiAnalysisContext.generateCaseTechniqueSnapshot('liureng')` 透传 castOpts(否则八客/选时案例挂成默认)+ `saveModuleAISnapshot` meta 记 5 字段；AI导出＝**自动**(同 `buildLiuRengSnapshotText`，已把起课法/换将/分昼夜记入起盘信息，无需改 aiExport)。七政＝右栏 TabPane，复用 `getPlanetObject`+`getSignZi`，顺逆 `lonspeed<0`。

**自检(preflight [14] 哨兵)：** ① `npm test` 全 140 绿；② 预览切 八客/年日对齐/演数/选时——**中心盘三传 == 右栏大格断辞**(同源)、日干支不变；默认正时正将逐字复原(零回归)；选时/演数选中后出现输入框。

## AI 分析页 大改(挂载正确性 / 技法全接入 / UI 重构 / 起课时间入口)

本轮把 AI 分析页系统性翻新。**改 `aiAnalysisContext.js` / `AIAnalysisMain.js` 前先读本节**，多处口径已变（含复活旧文档标注的"死代码"）：

### 1. 挂载"对不上"根因 + 修法（正确性，勿回退）
- **全局模块缓存**(`horosa.ai.snapshot.module.v1.<module>`)本质=「上次算过的那张盘/卦」，key 不含出生时间。原 `isSnapshotMetaCompatible`「任一方签名字段为空就判兼容」+ `buildCaseContext` 读全局缓存 → 换盘/事盘挂出旧内容。
- **修法**：① 新增 `isCacheSnapshotConfidentMatch`（**date 双方都有且相等**才复用缓存，缺签名一律 false→回退重算），`getTechniqueSnapshotFromCache` 改用它（**勿把它换回宽松的 `isSnapshotMetaCompatible`**——后者仍用于 payload 候选，payload 是源自身数据可宽松）。② `buildCaseContext` **移除全局缓存读取**，事盘源上下文只走 payload + `generateCaseTechniqueSnapshot`（遵 Part F）。③ `pickSnapshotCandidate` 的 `compatible!==false` 过滤是 A1 命脉，**勿动**。
- 自检：`aiAnalysisContext.test`「换盘后签名必匹配 / 缺签名不挂」；preview 两盘交替选同技法→签名各异(no-串盘)。

### 2. 「起课时间」入口 + 时间确定式法自动补算（复活了死代码！）
- `regenerateCaseTechniqueSnapshot`(619)+5 引擎曾被 `ai-analysis-context-and-markdown.md §F` 标为"死代码"，本轮**复活**：
  - **`TIME_CASTABLE_DIVINATION = ['liureng','jinkou','qimen','taiyi','sanshiunited']`**（时间完全确定的式法）。
  - 新增 `sourceType==='timepoint'` 分支：合成的「起课时间」源（`AIAnalysisMain` 的 `timepointDraft`，**不持久化**，默认此刻+`Constants.DefLon/Lat`），对白名单技法即时起盘。
  - 事盘分支(case)：payload 缺该技法且 **key∈白名单** 时，按本案例 `divTime`+默认 `await regenerateCaseTechniqueSnapshot` 补算（meta 带 `regeneratedFromCaseTime`）。
- **🔒 铁律：六爻 / 统摄法 / 宿占 不在白名单 → 永不按时间重算。** 六爻是摇钱/报数起卦，按时间重算 = 伪造一个不同的卦。`aiAnalysisContext.test` 有「never recasts 六爻」护栏断言，**勿删**。
- `listAnalysisTechniqueOptions` timepoint 分支只 offer 白名单 5 式法。

### 3. 命盘类技法全接入 AI 挂载（13 个新 builder，规律照抄）
`regenerateChartTechniqueSnapshot`(switch) 新增：
- **推运**：`primarydirect`+`primarydirchart`(同主限方向数据，fall-through)、`profection/solararc/solarreturn/lunarreturn/givenyear`(共享 `buildPredictivePeriodSnapshot(chartObj,key)`→`/predict/<key>`+`buildPredictiveSnapshotText`，**目标时刻默认「此刻」**)、`zodialrelease`(AstroZR 导出 `buildZodialReleaseSnapshotText`,福点基点+L1全列)、`decennials`(AstroDecennials 导出 `buildDecennialsSnapshotText`,纯前端默认设置+L1全列)。
- **数算**：`canping`/`heluo`——先 `buildLocalBaziResult(buildChartBaziParams(record))` 排四柱(镜像 `HeLuoMain.getModel` 取数:`gz=p.ganzi||p.ganZhi`、月/时支=`.charAt(1)`)，再喂 `canpingLocal`/`heluoLocal` 的 `calculate`+`buildSnapshotText`(import 须 **alias**,两库同名导出 `calculate`/`buildSnapshotText`)。
- **后端 ken**：`xianqin`(演禽)/`cetian`(策天飞星)——`KinAstroMain` 导出 `buildKinAstroSnapshotForFields(fields,serviceKey)`(`parseFieldsDateTime`+`postKinAstro`+`buildSnapshotText`)；`huangji`(皇极经世)——`HuangJiMain` 导出 `buildHuangJiSnapshotForFields(fields)`(`postWangJi('pan',{...dt,historyYear,classicKey:DEFAULT_CLASSIC})`)。
- **接入即检**：`aiExport.test getAIExportAuditMatrix` 强制「挂载已注册技法必须在 aiExport 段表+提取器有对应」。这 13 个的 `AI_EXPORT_PRESET_SECTIONS` 段+结构化键**早已存在**(技法各有独立页),故只补挂载侧；**新增其它技法务必两侧都补**否则审计红。**无数据一律返 ''**(挂载显「缺失」,勿返空段头/占位语)。
- **下拉清理**：`ANALYSIS_CHART_TECHNIQUES` 移除真空壳 `relative/jieqi×6/cntradition/otherbu/fengshui`(标签表保留)。

### 4. AI 页 UI 重构（面向用户）
- `renderAnalysisPane`：顶栏 `.topBar` 三组(配置→测试→对话)：模型 Select+`Dropdown`(配置当前接口/拉取模型/切换生效接口/管理全部接口)、连接 chip 四态(`.connChip` 读 `activeProviderProfile?.healthStatus`，**全程 `?.` 守空防白屏**，无接口显「未配置」)、案例 Select+`Badge`「挂载」。
- 对话**保留 chatCard 只居中**(`.chatStage .chatCard{max-width:960px;margin:0 auto}`)；技法/资料/系统提示/挂载预览迁入 `XQDrawer`「挂载设置」。**只增 `.less` 类**，未碰共享阴影组/暗色块/死规则。

### 5. 三个 UI bug
- 占星「收合」死占位符(`AstroChartMain.js` `renderInputPanel` 的无 onClick `XQIconButton tooltip="收合"`)→ **删除**。
- 天文馆全屏失效真因=进全屏未 `engine.resize()`：`PlanetariumBabylon` `componentDidMount` 加 `fullscreenchange`→`this.renderer.engine.resize()`(延一帧)，`componentWillUnmount` 解绑。
- 星运页右侧技法 tab(22个纵排)末尾被裁：`app.less` **仅** `.horosa-direction-page > .ant-tabs.ant-tabs-right > .ant-tabs-nav` 加 `.ant-tabs-nav-wrap{overflow-y:auto}` + 收紧 tab(`min-height:30/margin:1`)——**勿改多页共享的 `.ant-tabs-nav` 规则**。

**自检**：`npm run build` 绿 + `npm test` 146 绿；preview 起后端(`start_horosa_local.sh`)→ AI分析选盘+开挂载抽屉→各技法「已就绪」非空、签名对得上 birth(实测 13 技法含演禽/策天/皇极对 ken 后端均 OK)。**改大段 JSX 后必 `npm run build`**(jest 过≠能编译)。

### 6. v2.5.1 复审整改（第二轮，用户验收后追加；仍属 v2.5.1，不升版）
本轮 16 项整改,改 `aiAnalysisContext.js`/`AIAnalysisMain.js`/`aiExport.js`/atlas/紫微/天文馆前先读:
- **B1 起课「缺失」根因**：`preciseCalcBridge.fetchPreciseNongli` 的本地兜底 `buildLocalNongliFallback` 原**只写在 catch**,但 `request` 软失败(后端非0码/网络抖动)**返回 undefined 不抛异常** → catch 永不进 → 奇门/太乙离线即空(改经纬度=缓存未命中触发请求才暴露)。**修法**:try 内对 `!result` 也走一次兜底(与 `/liureng/gods` 行为对齐)。**勿把兜底搬回纯 catch**。
- **New3 卜卦盘/择日盘进事盘白名单**：`TIME_CASTABLE_DIVINATION` 追加 `'horary','election'`(+ `ANALYSIS_CASE_TECHNIQUES`/`ANALYSIS_TECHNIQUE_LABELS`)。`regenerateCaseTechniqueSnapshot` 新增两 case:`fetchChartResultForRecord` → `runHorary(chart,'general')`/`runElection(chart,'marriage')` → `buildHorarySnapshot/buildElectionSnapshot`。**坑**:起课/事盘记录用 `divTime` 无 `birth`,而 `fetchChartResultForRecord`→`buildFieldObject` 读 `record.birth` → 必须 `{...record, birth: record.divTime}` 映射,否则西洋盘起不出→缺失。护栏 test 已加 4 个 horary/election engine+snapshot mock。**六爻仍永不入白名单**。
- **B2/B3 命盘时间入口**：新增 `NATAL_SOURCE_ID='natal:current'` + `natalDraft`,合成 `sourceType:'chart'` 源(record 带 `birth`)→ 走命盘技法(`buildTechniqueContext` chart 分支,`buildFieldObject` 认 `record.birth`)。起课/命盘两抽屉入口共用一段:`DateTimeSelector` 文本时间 + `GeoCoordModal`(atlas,onOk 带 `zone`,`gpsToLonLatStrings` 把 gps→'NNeMM' 串)+ 命名 + 性别 + 时区 + **保存为命盘/事盘**(`upsertLocalChart`/`upsertLocalCase` 接纯对象、自动生成 cid、返回 record → `setSources(listAnalysisSources())`+`setSelectedSourceId(saved.cid)`)。
- **A 消息按钮**：每条 AI 气泡左下 `.messageActions` 复制全文(`navigator.clipboard`+`execCommand` 兜底)/重新生成。**坑**:`handleRegenerateMessage(item)` 必须**按 messageId 截断**(删该条及之后、以前一条 user 重答),**不能**像 `handleRegenerateLastReply` 那样硬 `pop()` 末条(点中间条会误删末条)。`xq-icons` 新增 `copy` 图标。
- **C 测试连接状态机**：新增 `connState={key,status}`,key=当前 `modelSelection` 指纹。chip **不再读 `profile.healthStatus`**(那是历史诊断会残留过期绿),只认 `connState.key===modelSelection` 时的 status;切模型/接口 → key 失配自动回灰「点击测试」;`testProfileChat` 成功置 `healthy`(绿「测试成功」)/失败 `error`。
- **F 导出/挂载完整性**：① `heluoLocal.buildSnapshotText` **本来从不调 liuNian** → 加 `[流年·岁运]`(全生涯,birthYear 由 `dy.all[0].yearStart` 反推);两个动态卦名头改固定名 `[先天卦·元堂爻辞]`/`[后天卦·元堂爻辞]`(否则 `normalizeSectionTitle` 命不中→导出设置勾不了)。② `canpingLocal.buildSnapshotText(result, opts)` 加 `opts.liunianRows` 出全表 `[流年·歲運]`,两调用方(`buildCanpingSnapshotForRecord`+`CanPingMain.saveSnap`)都喂 `liunianSeries(...).rows`。③ **canping/heluo 此前在 `AI_EXPORT_PRESET_SECTIONS` 有段却没进 `AI_EXPORT_TECHNIQUES` → 导出设置下拉隐身 + 不被 `getAIExportAuditMatrix` 自检**:补进 `AI_EXPORT_TECHNIQUES`+`AI_EXPORT_SECTION_MIGRATION_KEYS`+`getExtractorKindByExportKey`(module:)+`extractContentByKey`(`extractSimpleModuleContent`),版本 12→13。④ preset 段名全部对齐快照真实 `[段头]`(canping `大运·歲運`/`流年·歲運`、ziwei 补 `来因宫`/`命中格局`、primarydirchart 复用 primarydirect 头)。⑤ **新增自检** `aiExport.test`「preset key ⊆ AI_EXPORT_TECHNIQUES」(`getAIExportPresetKeys`)堵隐身回归。
- **G 紫微右栏空白(第二次,真根治)**：上次只改 `.horosa-ziwei-tabs`(2 类)被 redesign 皮肤 `.horosa-ziwei-redesign .horosa-ziwei-tabs`(3 类,`:7536`)按特异性压过 → 无效。真病灶=全局 `.horosa-content-tabs .ant-tabs-tabpane > *{height:100%!important}`(`:5285`)撑满 + meta-scroll `align-content:start` 留空网格轨道。**修**:ziwei 作用域(4 类)覆盖 `tabpane>*{height:auto!important;max-height:none!important;min-height:0!important}` + meta-scroll `min-height:0`。
- **H 紫微点宫位神煞变(仅三合盘)**：`ZWHouseSangHe.drawTitle` 在有 `flyHouse`(点过宫)时把本命将前/岁前十二神改写成以被点宫为流年支的流年神煞 → 删该改写块(本命神煞恒定;`flyHouse` 仍只驱动三方四正高亮);`getYearJiang/getTaisui` import 已转注释。
- **atlas 全量城市**：`scripts/build-cities.js`(构建脚本,不进 bundle)从 `vendor/kinastro/tools/cities/{cities.json(world pop≥15000)+china_cities.json(中国树)}` 生成 `src/data/citiesFull.json`(**34299 城,2.27MB,短键 {n,e,r,y,x}**);`GeoCoordSelector` `componentDidMount` **动态 `import()` 懒加载**(.catch 兜底仅小库)+ 防抖 180ms 搜 n/e/r。坐标头改度分秒(`AstroHelper.formatLonDms/formatLatDms`,`116°24′27″E`)。
- **atlas 时区手改+持久化**：`GeoCoordSelector` 加时区 Select(默认自动 `dstAwareZoneAt`,可覆盖)+「自动」按钮 → onChange 带 `zone` → `GeoCoordModal` 透传(+`openSeq` remount key 重置 override)→ **`ChartData`/`CaseData`/`ChartFormData` 三处 `changeGeo` 对称改**(`geo.zone` 存在则写 `flds.zone`+`zoneManual=true`,否则维持 `applyDstToFields`)。fields.zone→`localcharts:246` 存盘→AI 已读,自动贯通。
- **天文馆**：`PlanetariumBabylon` 加 `immersive` state,「全屏」改 `toggleImmersive`(纯 CSS grid `0/1fr/0` 隐两 aside+滑出动画,320ms 后 `engine.resize()`)+ stage 内悬浮「退出沉浸」按钮(`planetarium.less .planetarium-immersive-exit`);「收合」改 `.planetarium-collapse` 仅 `<XQIcon name="prev">` 箭头、定位左栏右上角、`.is-left-collapsed` 下 `rotate(180deg)`。保留 `fullscreenchange` 监听。

**本轮自检**:`npm test` 147 绿(新增 horary/election mock + preset⊆techniques 断言)+ `npm run build` 绿;preview 实测:起课时间改经纬度→7 式法(含卜卦/择日)全「已就绪」、命盘时间→星盘「已就绪」、紫微右栏无空块、atlas 搜 paris 出全球结果+度分秒+时区下拉、天文馆全屏沉浸+箭头收合。

### 7. 经纬度/时区 全半球根治 + 真太阳时·直接时间(用户验收追加;**改任何「选地点/经纬度/时区」前先读**)
**坐标串正反转换是全仓共性坑,西经/南纬/小负值都曾产畸形 → 后端 param error / 落宫差错。规范转换器 `AstroHelper.convertLatToStr/convertLonToStr`(正向)+ `convertLatStrToDegree/convertLonStrToDegree`(反向)是单一真源,已重写为完全正确,新增 `astro/__tests__/AstroHelperGeo.test.js`(18 例:四半球+赤道本初+(-1,0)+分=10+往返)做回归门禁。**
- **正向(gps→'NNeMM' 串)三坑**:① `splitDegree` 对负值**只把 res[0](度)取负、res[1]/res[2](分秒)是正绝对值**——手抄转换误把分也取负 → 「121w0-44」畸形(西经/南纬命中);② **|值|<1 的小负值(伦敦 -0.12)**:`parseInt(-0.5)=0`、`-0===0` → 度部分丢负号,用 `deg[0]<0` 判向会把西/南误判成东/北 → 须用 `splitDegree` 的 **`res[3]=['-']` 符号标记** 或原始值符号判向;③ `>10` 补零致分=10 产「010」三位串(应 `>=10`)。修法:规范转换器方向按**原始值符号**、度分**绝对值**、`>=10`;另 6 个手抄文件(命盘 ChartData / 事盘 CaseData / ChartFormData / dice / Azimuth / AstroDirectionForm)的 changeGeo 改 `Math.abs` + 条件补 `|| (deg[3] && deg[3].length)`;AI 分析 `gpsToLonLatStrings` 同款。
- **反向(串→十进制)**:原 `deg + 1.0/min`(应 `min/60`)+ else 分支 `*10` 均错 → 手输经纬度算出的 gpsLat 偏(116e24→116.04) → 地图点位/时区推断偏。已重写为 `deg + min/60`。
- **时区:选地点自动校正**(`dstAwareZoneAt(gpsLat,gpsLng,date)` + `DateTime.setZone`——**只改时区标签、保留出生钟面时刻、不移位**,见 `comp/DateTime.js:290`)。已覆盖:① AI 挂载抽屉命盘/起课时间(onOk 显式推断,未手改时区时);② 占星 `AstroChartMain.changeGeo`;③ 术数页 `ziwei/guolao/cntradition/calendar(NongLi)/jieqi` 的 changeGeo(setZone in `let dt=...` 后);④ 命盘/事盘录入 `ChartData/CaseData/ChartFormData`(`applyDstToFields`)。原子串 `GeoCoordSelector.withZone` 仅在**手改时区**时附 `zone`,选点走各 changeGeo 自动推断;手改优先(`rec.zone`)。六壬/dunjia/suzhan 的 changeGeo 不持时间对象、zone 由持久化 fields 重建,无需改。
- **🔒 真太阳时 / 直接时间(铁律)**:`timeAlg=0`=真太阳时(**按经度校正起盘时刻**)、`=1`=直接时间(**用钟表时,不做经度时间校正**)。`buildFieldObject` 原把 `timeAlg/after23NewDay/lateZiHourUseNextDay` **写死** → canping/heluo 等八字类快照对「直接时间」盘错用真太阳时校正/忽略晚子时。修法:`buildFieldObject` 读 `record.timeAlg/after23NewDay/lateZiHourUseNextDay`(默认 0/默认值)。**`setZone` 只改时区偏移≠真太阳时经度校正**;真太阳时校正在后端/`baziLunarLocal.applyApparentSolarTime`,按 timeAlg gate,**勿对直接时间盘施加经度时间校正**。
- **经纬度+时区 四同步**:`buildChartBaziParams` 透传 `zone/lon/lat/gps/timeAlg`;`localcharts.js:246` 存 zone;`astroAiSnapshot`/`aiAnalysisContext` 读 zone → 挂载/导出/储存一致。
- AI 挂载抽屉宽 460→**560**(经纬度/时区输入不被裁)。
- **自检**:`AstroHelperGeo.test`(18 例)+ `release_preflight.sh [25]`(坐标转换/timeAlg 哨兵)。改坐标/时区/timeAlg 后必跑 + preview 实测「选异地(美西/伦敦)→坐标干净、时区自动、无 param error」。
