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
- **改任何 runtime 端点的响应结构 → 必须同步更新 `astrostudyui/scripts/verifyHorosaRuntimeFull.js` 的对应检查**（v2.3.0 踩过：acg 把 `/location/acg` 重写成 `{meta, planets:{<id>:{lines:{asc:[],mc:{lon}}}}, geo, parans}`，但旧 verify 仍按旧 flat 结构取 `objectKeys(acg)[0].asc`→发布验证 `verify_desktop_packaging` 误报「asc 非数组」。端点本身没坏[已过 `validate_acg.py` ]，是验证脚本陈旧。改端点契约的 PR 务必连带更新此验证）。

---

## 西占推运 + 宫制（v2.5.0 起）

- **双圈盘/推运组件「内圈本命冻结」坑（实测对不上选的盘）。** `AstroPersianDirected`/太阳弧族这类组件**构造时**用 `natalParams(props.value)` 把本命字段(date/time/lat/lon/zone)一次性写进 `state.params`，而 `componentDidUpdate` 换盘只重新**请求**、**不重算 natalParams** → app 初始默认盘是「now 盘」(birth=今天)，切到真盘后 `state.params.date` 冻结成今天 → 后端 `PerChart` 按 `data['date']` 把**内圈本命**按今天起盘。**修法=`requestData` 每次从当前 `props.value` 重算 `natalParams` 并 `{...state.params,...np}` 覆盖**(`AstroSolarArc` 靠 `props.hook.fun`/`genNatalParams` 避开)。**凡「构造时一次性 derive 本命 + update 不重 derive」的盘都会犯**，新增此类组件务必在 request 路径重算。React dev 会 shallow-freeze props，fiber 调试只能改 `props.value.params.xxx` 嵌套字段、不能整体替换 `props.value`。
- **自定义「整宫家族」宫制的 `inHouse` -5° 偏移坑（落宫 off-by-one）。** flatlib `House.inHouse` 只在 `self.hsys == const.HOUSES_WHOLE_SIGN` 时用 `distance(self.lon, lon)`；**否则**用 `distance(self.lon + House._OFFSET, lon)`(`_OFFSET=-5.0`)。所以「福点整宫制」这类自定义整宫制，重定位宫头后**每个 `house.hsys` 必须设成 `const.HOUSES_WHOLE_SIGN`**（不是自定义标记 `'Fortuna_Whole'`），否则福点/行星落宫整体差一宫。**盘级宫制中文名靠盘的 `hsys` 参数(24→福点整宫制)驱动，不靠逐宫 `house.hsys`**，所以这样设不影响显示。
- **新增 house system 三处同步（缺一即错位）。** ①后端 `astropy/astrostudy/perchart.py` 的 `hsys[]` 列表——**只能追加到末尾**(新 index)，**勿插中间**否则所有后续宫制 index 全错位、老盘读错宫制；自定义算法的再加 `custHouse_*` 常量 + `__init__` 里 `houseCust` 检测(底盘退化成某标准制) + `custHouse()` 分支重算 12 宫头。②前端 `constants/AstroConst.js` `HOUSE_SYSTEM_OPTIONS` 追加 `{value:<同后端index>, label}` + `HSYS_* ` 常量。③`constants/AstroText.js` 加 `AstroMsg[HSYS_*]` 标签。
- **改 `astropy/**/*.py` 后必须重启 Python chart 服务**(CherryPy 不热重载)：`./stop_horosa_local.sh && HOROSA_SKIP_UI_BUILD=1 ./start_horosa_local.sh`，否则 preview 仍跑旧码(直接 `python -c 'from astrostudy.perchart import PerChart'` 跑临时脚本验证逻辑则用的是新码——别被「脚本对、preview 错」误导)。注：curl 直打 `/predict/*` 会得 `no.register.app.in.sys.forapp:`(缺前端注册头)，**不代表后端坏**，要从前端 UI 验证。
- **Balbillus 算法口径**(还原自 129-year Balbillus 变体，独立 `utils/balbillus.js`，**不碰** decennials.js)：七星 Balbillus 小年(日19/月25/土30/木12/火15/金8/水20=129) → 主限长度 `= N×(1 − d/360)`，d=本命星黄经离其**擢升度**的角距(`nearest` 最近角距 / `forward` 顺黄道距，做成参数) → 主限序=七星按本命黄经升序、从**起始星**旋转 → 每主限再以该期主星为起点按 **129 权重**递归切子限(可 5 层) → 日期用 Hellenistic **360 日年**(可切 solar)。UI=antd `Tree` 懒加载(`loadData`)。起始星/年制/距离口径做成左栏选项；mode 默认 nearest，精校需对 core 同**本命**盘(其面板经度是 transit 盘、勿误用)。
- **行星 tab 底部空白 + 七政卡片矮**根因：`AstroPlanet`/`AstroLots` render 内部 `height-130` 过减 → `0.68t+0.32t` 只渲染 `t−202px` 内容、容器满高 `t` → 底部空白。**修法=`.horosa-planet-with-lots` 改 `display:flex;flex-direction:column`，`AstroPlanet` 加 `fill` 模式(`flex:1;height:100%`)撑满、`AstroLots` 加 `natural` 模式(内容高)**。别再用「固定百分比 height」拼两块。

---

## 本地服务端口健壮性（v2.5.0 起）

- **「排盘失败：本地排盘服务未就绪」/ Windows `portend.Timeout: Port 8899 not free`（code 70）反复起不来** → 根因 = 上次实例崩溃/强退后**僵尸 python 仍 LISTEN chart 端口**，新实例 CherryPy `portend` 直接「Port not free」退出。成熟修法在**共享** `astropy/websrv/webchartsrv.py`（Mac+Windows 同一份，桌面壳都 bundle 它）：`__main__` 里 `cherrypy.engine.start()` 前调 `ensure_chart_port_free('127.0.0.1', chart_port)` —— 探测端口 → 定位 LISTEN 该端口的 PID → **仅当命令行含 `python`+`webchartsrv`/`astropy`/`horosa`（即我们自己的僵尸）才 kill** → 轮询等 OS 释放后重试。跨平台（win=netstat/taskkill、posix=lsof/SIGKILL）。
- **dev 启动器 `start_horosa_local.sh` 同理**：旧逻辑端口被占就 `exit 1` 阻死；现 `reclaim_stale_port <port> <tag>`（tag=`webchartsrv`/`astrostudyboot`）只回收**自己的**僵尸再继续，非 Horosa 占用才报错退出。
- **铁律：回收必须靠命令行 tag 精确匹配「我们自己的进程」，绝不无差别 kill 端口占用者**（会误杀用户其他程序）。`release_preflight.sh [12]` 哨兵守 `ensure_chart_port_free` + `reclaim_stale_port` 在位。
- Windows 桌面壳是独立 repo，但 bundle 的就是这份共享 `webchartsrv.py` → 同步后端即获修复；桌面壳自身若再在 spawn python 前先清僵尸更稳（已记 handoff）。

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
