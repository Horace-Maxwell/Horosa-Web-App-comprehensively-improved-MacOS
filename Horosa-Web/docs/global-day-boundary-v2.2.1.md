# 全局设置 · 日界点 + 晚子时·时柱起干 (v2.2.1)

发布版本 = **v2.2.1**。本文为最终版,涵盖两个独立全局开关 + 所有 bug 根因 + 验证步骤。

## 用户拍板·语义矩阵

两个独立的全局开关,组合下 **27日 23:30 直接时间** 的四柱矩阵：

| | 日柱开关=1（默认，"23点算第二天"）| 日柱开关=0（"24点算第二天"）|
|---|---|---|
| 时柱开关=1（默认，"晚子时按次日日柱计算"）| 丙午 癸巳 **壬寅 庚子** | 丙午 癸巳 **辛丑 庚子** |
| 时柱开关=0（"晚子时按当日柱计算"）| 丙午 癸巳 **壬寅 庚子**（日柱已次日、等价）| 丙午 癸巳 **辛丑 戊子** ← 核心新 case |

**关键不变量**：
- 两个开关在 `hour ∈ [23:00, 24:00)` 才生效；其他时辰一律没区别。
- 默认值不变（=1）= 保留 v2.2.0 已发布的行为。
- value 0/1 的含义全栈一致：前端 fields、Java boolean、Python int、AI snapshot。

## 后端字段名

| 全局偏好（localStorage `globalSetup`）| dva fields | Java/Python 传输 |
|---|---|---|
| `dayBoundary: 'after23' \| 'after24'` | `after23NewDay: 1 \| 0` | `after23NewDay` |
| `lateZiHourMode: 'nextDay' \| 'today'` | `lateZiHourUseNextDay: 1 \| 0` | `lateZiHourUseNextDay` |

## 涉及改动（按层）

### 前端
- `utils/dayBoundary.js`：新增 `LATE_ZI_HOUR_NEXT_DAY / LATE_ZI_HOUR_TODAY` 常量 + `normalizeLateZiHourMode / lateZiHourModeToBit / globalDefaultLateZiHourUseNextDay / readGlobalLateZiHourMode / defaultLateZiHourUseNextDay`。
- `models/app.js`：state + globalSetup 序列化 + `normalizeGlobalSetup` 加 `lateZiHourMode` 字段。
- `components/homepage/PageHeader.js`：Modal 加第二个 XQSegmented + `changeLateZiHourMode` 广播 `horosa:late-zi-hour-mode-changed` 事件。
- `layouts/app.js`：`mapStateToProps` 加 `lateZiHourMode` + 透传给 `<PageHeader>`。
- `models/astro.js`：fields schema 加 `lateZiHourUseNextDay`、`fieldsToParams` 透传、`syncLateZiHourMode` reducer、`syncFromGlobalLateZiHour` subscription、`fetchByChartData` 命盘恢复时回填。
- `utils/baziLunarLocal.js`：buildFourColumns 接受 `opts.lateZiHourUseNextDay`、新增 `computeOverrideTimeGan(eightChar, lateZiHourUseNextDay)` — 当 lateZi=0 且 hour==23 时用 `getDayGanIndexExact2()` 起子时，绕开 lunar.js 硬编码的 Exact day gan。
- `utils/preciseCalcBridge.js` + `utils/localCalcCache.js`：`NONG_LI_KEYS` + `JIE_QI_YEAR_KEYS` 加 `'lateZiHourUseNextDay'`。
- `utils/aiAnalysisContext.js`：DEFAULT_DUNJIA_OPTIONS、所有 field schema、buildCaseSnapshotFields、buildChartLiuRengParams、buildChartZiweiParams、各 nongliParams 加 `lateZiHourUseNextDay`；新增 `buildDayBoundaryMeta()` 给 AI 显式标注排盘规则。
- `utils/astroAiSnapshot.js`：`buildBaseInfoLines` 加一行 "排盘规则：日柱开关【...】+ 时柱开关【...】"。
- `utils/localcharts.js` + `utils/kentangCaseSave.js` + `models/user.js`：命盘 record / case record 加 `lateZiHourUseNextDay` 字段，持久化随存随取。

### Java
- `helper/BaZiHelper.java`：4 个 time-related method 加 `boolean lateZiHourUseNextDay` 重载（保留旧签名默认 `true`）。Shift 触发条件：`hour==23 && !after23NewDay && lateZiHourUseNextDay`。
- `model/BaZi.java`：state 加 `lateZiHourUseNextDay` 字段，构造函数加新重载（默认 `true`），`calculateFourColumn` 调用 `getTimeColumn` 时传该字段。
- `helper/NongliHelper.java`：`getNongLi` 加 9-arg public overload + 7-arg 跨包简便重载，`getTimeGanziStr` 调用同步加 `lateZiHourUseNextDay`。
- `model/OnlyFourColumns.java`：加 10-arg 构造重载。
- `controller/ChartController.java:265 getParams()`：白名单加 `lateZiHourUseNextDay`（**关键** — 这是上一轮同款 bug 的同方向修复）；`chart()` 方法读 `lateZiHourUseNextDay` 并传给 `OnlyFourColumns`。
- **重编 jar 三 module**（astrostudy → astrostudycn → astrostudyboot）+ 替换 `runtime/mac/bundle/astrostudyboot.jar` + 重启 Java 进程。

### Python（Phase 2，目前未改 — 七政 Moira 等主流走 Java，已 OK）
预留：`vendor/kinwuzhao/config.py`、`vendor/kinastro/astro/shaozi/calculator.py`、`vendor/kinastro/astro/fendjing/fendjing_calculator.py`、`vendor/kinastro/astro/nanji/calculator.py`、`vendor/shenyishu/shenyishu.py`、`vendor/kinwangji/kinwangji/wanji.py + jieqi.py` 添加 `hour_gan_use_next_day` 参数。当前 hour==23 总是按次日干起（= 默认 `true` 行为）。`服务层 webqizhengkinsrv` 已有 `jd_for_hour` 路径,但 chart 端点用的是 Java backend 结果而非 Python。

### jest 自检
`src/utils/__tests__/baziLunarLocal.dayBoundary.test.js`：保留原 4 个日柱开关 case + 新增 6 个时柱开关 case（含核心新 case `after23=0 + lateZi=0 → 辛丑 戊子`）。`umi-test`: **139/139 PASS**。

## 历史 bug 根因（本版本一并修复 / 文档化）

### Bug A · ChartController.getParams() 白名单丢字段
`ChartController:265 getParams()` 是白名单设计，未显式 `putAll("after23NewDay")` 时 Java backend 永远拿不到该字段（`ConvertUtility.getValueAsInt(..., 1)` 回退到默认 1）。**修法**：在 `getParams()` 显式 `params.put("after23NewDay", TransData.get("after23NewDay"))` + 同样为 `lateZiHourUseNextDay`。**审计**：所有 chart-flow controller (`ChartController` / `QueryChartController` / `IndiaChartController` / `JieQiController` 等) 的 `getParams()` 都要 grep。

### Bug B · Apr 20 旧 Java 进程未死
重编 `astrostudyboot.jar` 后，`runtime/mac/bundle/astrostudyboot.jar` 替换但 `:9999` 上跑的是 Apr 20 启动的 launcher 进程（loaded 旧 class 进 JVM 内存）。**症状**：bytecode 是新的，行为是旧的。**修法**：`lsof -ti :9999` 找 PID + `ps -p PID -o lstart=` 确认进程启动时间 > jar mtime；否则 kill + `start_horosa_local.sh` 重启。

### Bug C · lunar-javascript 时柱硬编码
`EightChar.getTimeGan()` 内部 `timeGanIndex = (dayGanIndexExact % 5 * 2 + timeZhiIndex) % 10` — 永远用 Exact（shifted）day gan。`setSect` 只影响 day pillar，不影响 time pillar。**修法**：前端 `baziLunarLocal.js` 自己用 `getDayGanIndexExact / Exact2 + getTimeZhiIndex` 算时干，绕开 lunar.js。

### Bug D · Java cache + Redis + 本地 file
`ParamHashCacheHelper` 三层缓存（内存 + Redis + `.horosa-cache/paramhash/`）。重编 jar 后内存自动清，但 Redis / 本地文件 cache 不会。新增 key 字段后 cache key 改变自然 miss；改字段类型可能命中错误条目。**调试**：`redis-cli KEYS "*chart*"` + 必要时清 `.horosa-cache`。

### Bug E · 客户端 fetchChart in-memory cache
`services/astro.js:5 chartMem` 用 `JSON.stringify(values)` 作 key。新字段进 values 后 key 改变自动 miss，无需手工清；要强制刷新可在 `requestOptions.cache = false`。

## 验证步骤

### jest 单测
```bash
cd Horosa-Web/astrostudyui
npx umi-test --testPathPattern=baziLunarLocal.dayBoundary
# 期望: 10 个 case 全绿（4 日柱 + 6 时柱）
```

### 后端端到端（dev server）
```bash
# 1. 启动本地栈
cd Horosa-Web && HOROSA_SKIP_UI_BUILD=1 ./start_horosa_local.sh

# 2. preview 自检 27日 23:30 直接时间 + 4 case 矩阵
# 全部命中上方矩阵后即通过

# 3. 切换两个全局开关、验证日柱/时柱跳变
# 4. 保存命盘 → 重新打开 → 验证 after23NewDay + lateZiHourUseNextDay 已持久化
```

### 是否重编 jar / 重打 runtime
- **必须重编 jar**（BaZiHelper + BaZi + NongliHelper + OnlyFourColumns + ChartController 都改了）：mvn 三 module 链 → 替换 `runtime/mac/bundle/astrostudyboot.jar` → kill 旧 :9999 进程重启。
- **不必重打 Python runtime**（Python vendor 暂未改）。如 Phase 2 改了 vendor 则要重打。

## 发布检查清单

- [ ] npm run build 通过
- [ ] npx umi-test 全绿（139+）
- [ ] Java mvn 三 module 链全过 + jar 替换 runtime/mac/bundle/
- [ ] preview 4 case 矩阵全过 + 8 大技法切换跳变 + 持久化
- [ ] release_preflight.sh 加 v2.2.1 版本门禁 + windows-sync-handoff 顶部加条目
- [ ] launcher version assertion 升 2.2.1
- [ ] skill repo AGENTS.md + horosa-agent/SKILL.md 同步章节
