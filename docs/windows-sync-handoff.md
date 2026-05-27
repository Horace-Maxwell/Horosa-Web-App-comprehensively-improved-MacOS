# Windows 同步交接（给 Windows 端 Claude Code）

> 读者：在 **Windows 仓库**里干活的 Claude Code / 开发者。
> 作用：这是一份**逐版本的同步台账**——每次 macOS 端发布后，这里记录「改了什么、为什么、Windows 必须做什么才能跟上」。
> 与其它文档分工：本文是「改了啥 + 怎么跟」；通用移植/发布规范看
> [`windows-porting-and-release-checklist.md`](windows-porting-and-release-checklist.md)；每个修复的机制细节看对应的 fix 文档（下面每条都给了链接）。
> **倒序排列，最新版本在最上面。**

---

## 总则（每次同步都先看）

1. **两个仓库是平台分叉，不是同一份代码。** macOS 端在
   `Horosa-Web-App-comprehensively-improved-MacOS`；Windows 端是独立仓库。**共享的是
   `Horosa-Web/`（前端 `astrostudyui` + 后端 Java `astrostudysrv` + Python `astropy`/`vendor`）**；不共享的是
   `Horosa_Desktop_Installer/`（Tauri 外壳 + 打包链路）与 `runtime/`（平台运行时）。同步时**只搬 `Horosa-Web/` 的业务改动**，外壳/运行时各自维护。
2. **判断一次改动要不要重编后端**：看改动是否落在 `Horosa-Web/astrostudysrv/**`（Java）。是 → **必须在 Windows 重编 `astrostudyboot.jar`**（见下，这是最容易漏的）。只动前端 `astrostudyui/**` → 只需重建前端包。
3. **判断要不要重建前端**：动了 `astrostudyui/**` → `npm run build` 然后 `npm run build:file`（**顺序执行，勿并行**，两者都写 `src/.umi-production`）。
4. 同步后按每条下面的「验证」自检，再走 Windows 自己的发布链路。

---

## v2.1.8 — UI 几何/明暗 + 太乙四柱时间 + 主限推运年数 + Ollama 流式

**性质：前端为主,但 ⚠️ 改了 Java(`astrostudysrv/boundless` + `astrostudy`)→ Windows 必须重编 `astrostudyboot.jar`;另有 Python(`astropy`)改动随源码 rsync,无需重编 jar。** 机制细节见 [`ui-and-time-fixes-v2.1.8.md`](ui-and-time-fixes-v2.1.8.md)。

### 改了什么
- 前端(`astrostudyui` → `npm run build` 然后 `npm run build:file`):
  - 各西洋盘符号几何居中(`components/astro/{AstroChartCircle,AstroHelper}.js`:`dominant-baseline` middle→central)。
  - 太乙四柱随时间基准重算 + 同显直接/真太阳两时间(`components/taiyi/{TaiYiCalc,TaiYiMain}.js`,复用 `utils/baziLunarLocal`)。
  - 主限法:推运年数控件 + 表头/页码/去 core(`components/direction/AstroDirectMain.js`、`components/astro/AstroPrimaryDirection(Chart).js`、`layouts/app.less`)。
  - 紫微右栏空白/三合神煞字重/合盘选择条明亮/配置面板溢出/菜单精简(`layouts/app.less` + 相应组件、`components/homepage/PageHeader.js`)。
- 后端 Java(**重编 jar**):
  - `boundless/.../interceptor/SseHelper.java`:`new SseEmitter(120000L)` → `new SseEmitter(0L)`(去 AI 流式 120s 硬上限,修 Windows #6 Ollama「停止生成」)。
  - `astrostudy/.../service/AIAnalysisProxyService.java`:`buildJsonRequest` 流式仅在用户显式 requestTimeoutMs 时才加超时。
  - `astrostudy/.../controller/PredictiveController.java`:`getParams` 白名单透传 `pdYears`(主限法推运年数)。
- 后端 Python(rsync,**无需重编 jar**):`astropy/astrostudy/perchart.py`(`pdYears` 读取+clamp 1-180)、`perpredict.py`(主限 `max_arc=self.perchart.pdYears`)。

### Windows 要做
同步上述 `Horosa-Web/` 改动 → 因含 Java 改动,**重编 `astrostudyboot.jar`**(boundless install → astrostudy install → astrostudyboot clean package,见通用清单)→ 重建前端(`build` 然后 `build:file`)。

### 验证
占星清简盘星座质心居中;太乙切基准时日/时柱变、两时间稳定;主限法推运年数改值表格行数随之变(≤180);Ollama 慢模型不再 120s 中断(需真 Ollama)。

---

## v2.1.7 — 奇门/三式 真太阳时定盘修复

**性质：纯前端（`astrostudyui`）。⚠️ 不动 Java/Python → 不需重编 `astrostudyboot.jar`。**
机制细节全文：[`qimen-truesolar-time-fix-v2.1.7.md`](qimen-truesolar-time-fix-v2.1.7.md)。

### 改了什么
- `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaCalc.js`：`fetchQimenPan` 改用既有 `resolveCalcDateTime`，选「真太阳时」(timeAlg=0) 时按 `nongli.birth` 的真太阳时刻发后端排盘（此前漏用，奇门被当直接时间排）。三式六壬级联修复；太乙/紫微本就正确。

### Windows 要做的
1. 同步该前端文件到 Windows 仓库对应路径（纯 JS，无平台分支）。
2. **不需重编 `astrostudyboot.jar`**（没动 Java/Python）。
3. **重建前端**：`npm run build && npm run build:file`（顺序）。

### 验证
应用内：三式/遁甲选「真太阳时」→ 奇门时柱按真太阳时刻（例 1993-02-01 11:24 / 真太阳时 10:46 → 丁巳，原误作 戊午）；切「直接时间」→ 戊午。

---

## v2.1.6 — 奇门历法修复（月柱交节边界 + 置闰超神接气定局）+ 印度盘地图选点修复

**性质：纯 Python（`vendor/kinqimen`）+ 纯前端（`astrostudyui`）。⚠️ 不碰 Java → 不需重编 `astrostudyboot.jar`；奇门改的是随 runtime 包 rsync 的 vendored Python。**
机制细节全文：[`qimen-calendar-fix-v2.1.6.md`](qimen-calendar-fix-v2.1.6.md)。

### 改了什么
- **奇门(#4，上游 kinqimen #53/#9/#62/#43)**——`Horosa-Web/vendor/kinqimen/`：
  - `jieqi.py`：`gangzhi` 月柱按 sxtwl 精确交节时刻校正（交节当日、交节前沿用前一日月柱；立春兼校年柱）；新增 `zhirun_jieqi`（超神接气置闰后的定局节气）。
  - `config.py`：重写 `qimen_ju_name_zhirun`（改用 `zhirun_jieqi` + `findyuen` + 既有局数表，弃用旧农历启发式）；新增 `dingju_jieqi`。
  - `kinqimen.py`：`pan()` 的「節氣」标签改用 `config.dingju_jieqi(...,option)`（拆补=历法节气，置闰=超神节气）。
  - `test_qimen_calendar.py`：新增 11 项回归测试。
- **印度盘(#3)**——`Horosa-Web/astrostudyui/src/components/astro/IndiaChartMain.js`：`changeGeo` 改传扁平 `lon/lat/gpsLon/gpsLat`(+`tm`)，对齐 `AstroChartMain.changeGeo`（原把经纬度包成 `{value:...}` 与父级 `changeCond` 不符而报错）。

### Windows 要做的
1. 同步上述 vendored Python 4 个文件 + 前端 `IndiaChartMain.js` 到 Windows 仓库对应路径（纯 Python/JS，无平台分支）。
2. **不需重编 `astrostudyboot.jar`**（没动 Java）。vendored Python 随 runtime 包发布——确认 Windows 运行时打包把 `vendor/kinqimen/` 一并带上（与 macOS 的 rsync 等价）。
3. **重建前端**（动了 `astrostudyui/**`）：`npm run build && npm run build:file`（顺序执行）。

### 验证
- Python：`cd Horosa-Web/vendor/kinqimen && python3 test_qimen_calendar.py`（11/11）。
- 关键回归：2005-05-05 16:30→月柱庚辰；2027-10-31 20:49 置闰→立冬上元六局（节气标签立冬）；2004-09-01 拆补=处暑上元一局 / 置闰=白露上元九局。
- 前端：应用内印度盘地图选点→确认→正常排盘不报错。

---

## v2.1.5 — AI 分析页全面修复（供应商切换/鉴权 + 发送安全 + 静默失败透出）

**性质：前端为主 + 后端少量（`AIAnalysisProxyService.java` 改了）。⚠️ 后端改了 → 必须重编 `astrostudyboot.jar`（同 v2.1.4 流程）。**

### 改了什么
- 后端 `AIAnalysisProxyService.java`：`buildAuthHeaders` 对 gemini 不再加 `Authorization: Bearer`（否则原生接口 `ACCESS_TOKEN_TYPE_UNSUPPORTED`）；custom 支持 `providerOptions.authHeaderName`/`authPrefix` 覆盖（两个 key 已入 body 保留键）；reasoning 前缀加 `o5`。
- 前端 `components/aianalysis/AIAnalysisMain.js`（多处）：供应商卡片可点击 + 「设为当前」按钮；切 provider 类型清空旧 apiKey；删当前供应商自动补选；切换/删除会话先 abort 流；并发发送守卫；消息自动滚到底；embedding/分块失败提示；Markdown 解析失败退回纯文本。
- 前端 `services/aianalysis.js`：请求/流式尊重 `providerOptions.requestTimeoutMs`；流式 catch flush。
- 前端 `utils/aiAnalysisStore.js`：`saveUiPrefs` 配额超限记录而非静默。

### Windows 要做的
1. 同步上述 4 个文件到 Windows 仓库对应路径（纯 Java/JS，无平台分支）。
2. **重编 `astrostudyboot.jar`**（后端改了），命令见下方 v2.1.4 第 2 条；放到 Windows 运行时打包位置。
3. **重建前端**：`npm run build && npm run build:file`。

### 验证
多供应商切换（卡片/按钮）生效、切类型不串 key、Gemini 直连不再 401、流式中回车不并发、停止/切换会话中止流、嵌入缺失有提示。

---

## v2.1.4 — AI 分析：供应商兼容 + 错误透传 + 凭据脱敏

**性质：后端 Java 为主 + 前端少量。⚠️ 必须在 Windows 重编 `astrostudyboot.jar`。**
机制细节全文：[`ai-provider-compat-and-error-surfacing.md`](ai-provider-compat-and-error-surfacing.md)。

### 改了什么（三个家族）
- **A 参数兼容**：`AIAnalysisProxyService.java` 新增 `isOpenAIReasoningModel`；`buildOpenAIChatBody` 对 `gpt-5.x`/`o1`/`o3`/`o4` 省略 `temperature`、用 `max_completion_tokens`；其它模型（如 `gpt-4.1`）行为不变。
- **B 错误透传**：后端 `ensureSuccess` 读取并并入上游错误体；前端 `AIAnalysisMain.js` 流式 `onEvent` 处理 `error` 事件，替代「模型未返回可用内容」兜底。
- **C 凭据脱敏**：`HttpUriRequestHystrixCommand.java`（**共享库 boundless**）对错误信息里的 `Authorization`/`x-api-key`/`LocalIp` 等头脱敏，日志 URL 去 `?key=`。

### Windows 要做的（按顺序）
1. 把这三处源码改动同步到 Windows 仓库对应路径（路径与 macOS 一致，纯 Java/JS，无平台分支）：
   - `Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java`
   - `Horosa-Web/astrostudysrv/boundless/src/main/java/boundless/net/http/HttpUriRequestHystrixCommand.java`
   - `Horosa-Web/astrostudyui/src/components/aianalysis/AIAnalysisMain.js`
   - 测试（可选但建议）：`AIAnalysisProxyServiceTest.java`、`boundless/.../HttpUriRequestHystrixCommandTest.java`
2. **重编后端 `astrostudyboot.jar`（关键，发布链路不会替你编）**。仓库**没有 root reactor pom**，模块各自独立、版本固定（boundless `1.2.1.2`、astrostudy/astrostudyboot `1.0.0`）。用 **JDK 17**：
   ```bat
   cd Horosa-Web\astrostudysrv
   mvn -f boundless\pom.xml  install -DskipTests
   mvn -f astrostudy\pom.xml install -DskipTests
   mvn -f astrostudyboot\pom.xml clean package -DskipTests
   ```
   - **`clean` 必须有**：不 clean 时 astrostudyboot 自身源码未变，maven 会增量复用旧 fat jar、不重新打包依赖 → 改动进不去 jar。
   - 产物 `astrostudyboot\target\astrostudyboot.jar`。把它放到 Windows 运行时打包链路对应位置（macOS 是 `runtime/mac/bundle/astrostudyboot.jar`；Windows 对应 `runtime/win/.../astrostudyboot.jar`，以 Windows 仓库的运行时目录模型为准）。
   - 自检 jar 内含改动：解包 `BOOT-INF/lib/astrostudy-1.0.0.jar` 看 `AIAnalysisProxyService.class` 含 `max_completion_tokens`；`boundless-1.2.1.2.jar` 的 `HttpUriRequestHystrixCommand.class` 含 `redacted`。
3. **重建前端**：`cd Horosa-Web/astrostudyui && npm run build && npm run build:file`（顺序）。
4. JDK17 编译 + JUnit（boundless 2、astrostudy +2 新例）应通过。

### 验证
- 用一个推理模型名（如 `gpt-5.5` / `openai/gpt-5.5`）跑通对话（需真实 key）。已在 macOS 用真 key 验证：推理体（无 temperature + max_completion_tokens）能正常返回，流式答案在 `delta.content` 到达（reasoning 字段被正确忽略）。
- 故意触发上游错误（错 key / 错 model）→ 应显示**真实原因**而非「模型未返回可用内容」。
- 错误信息里 key 应显示为 `***redacted***`。

---

## v2.1.3 — 八字「直接时间 / 真太阳时」显示修复

**性质：前端为主（八字盘走前端本地计算），后端仅回退路径。无需重编后端即可让显示生效，但建议后端也同步。**
机制细节全文：[`bazi-time-display-fix.md`](bazi-time-display-fix.md)。

### 改了什么
- 主修复在前端 `astrostudyui/src/utils/baziLunarLocal.js`（本地计算在 `nongli` 加入与 `timeAlg` 无关的 `clockTime`/`solarTime`）+ 四处显示组件（`cntradition/{PaiBaZi,BaZiAppInfoPanel,BaZiLegacyView,BaZi}.js`）。
- 后端回退路径同款字段：`astrostudycn/.../model/BaZi.java`。

### Windows 要做的
1. 同步上述前端文件 → **重建前端包**（`npm run build` + `build:file`）。这是关键，单改后端在 Windows 同样不生效。
2. 后端 `BaZi.java` 同步后随下次 Java 重编带上（与 v2.1.4 的 jar 重编同一套流程）。

### 验证
- 八字盘切换「时间算法」，确认「直接时间」「真太阳时」两值都不跳，仅「计算基准」随之变；经度偏离 120°E 子午线时两值不同。

---

## 同步后通用自检（两版都适用）
- 后端启动：Java + Python 服务起得来，健康检查过（参照 porting checklist 的「Windows 发布前自检顺序」）。
- kentang/kin 路由 smoke（奇门/太乙/三式合一等打到图表服务端口）。
- 前端能加载、AI 分析能发消息。
- 发布前/后自检：见 [`windows-porting-and-release-checklist.md`](windows-porting-and-release-checklist.md) 的「Windows 发布前自检顺序」「Windows 发布后回下载自检」。
