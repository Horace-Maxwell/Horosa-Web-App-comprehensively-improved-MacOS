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

## 启动机制稳健化（端口 / 就绪根治 · 分支 `feature/startup-port-readiness-hardening` · 版本待定）

> 机制详解:[`启动机制稳健化-端口与就绪.md`](启动机制稳健化-端口与就绪.md)。根治两个反复症状:①端口被占用→用不了;②打开后「后端未启动 / 本地排盘服务未就绪」。**设计铁律:全部增量式,只在「今天本来就会坏」的失败路径触发,启动/排盘成功路径与今天逐字节一致。** **无 Java 改动 → 不需重编 jar。**

### A. 共享前端(Windows **必须**同步 + 重建前端包:`npm run build` 然后 `npm run build:file`)
- **新增** `astrostudyui/src/utils/serviceStatus.js`(全局在线/离线态 + 严格离线判定)、`astrostudyui/src/utils/chartFetch.js`(排盘裸 fetch 透明重试薄包装)、`astrostudyui/src/components/common/ServiceStatusBanner.js`(非阻塞重连横幅)。
- **改** `astrostudyui/src/utils/request.js`:加 `fetchWithRetryConnRefused`(`request()`/`requestRaw()` 的 fetch 经它——拿到响应即置在线;仅当传 `opts.retry` 且「后端不可达」(`TypeError`)时退避重试;最终不可达置离线)。**SSE `requestStream` 绝不接入重试**(防双发 / 重复计费)。
- **改** 四引擎排盘主路径:`components/dunjia/DunJiaCalc.js`、`components/taiyi/TaiYiCalc.js`、`components/jinkou/JinKouCalc.js`、`services/qizheng.js` 的裸 `fetch(buildKentangEndpoint…)` → `fetchChartWithRetry(…)`;其 `request()` 兜底加 `retry: { retries: 2 }`。
- **改** `layouts/app.js`:挂载 `<ServiceStatusBanner />`(与现有 `<UpdateNotifier />` 并列)。
- **改** `astrostudyui/scripts/warmHorosaRuntime.js`:加 `HOROSA_WARM_MINIMAL=1` 最小热身模式(仅 `/chart`,供启动期有界同步热身)。
- **验证**:`npm run test`(或 `umi-test`)全绿(mac 端本轮 140/140);构建后随便排个盘正常;杀掉本地后端→顶部出现「服务连接中断…」横幅、恢复请求后自动消失;save / AI / SSE 故意失败时**不**重试(无双提交/双计费)。

### B. 启动器 / 脚本逻辑(Windows 在自己的启动器里**镜像同等语义**,代码不共享)
> macOS 端落在 `Horosa-Web/start_horosa_local.sh` + Tauri `main.rs`;Windows 启动器是独立实现,需把下列语义搬过去。
- **端口冲突可重试**:端口被占 / 子进程 bind 失败 → 启动器以**可区分的失败信号**(mac 用 `exit 3`)上报;外层(mac 在 `main.rs`)**换一对全新空闲端口重试,最多 5 次**;**web / 静态服务器端口绝不参与重试环**(铁律:否则会关掉刚起的静态服务器→导航连不上,即 v2.4.0 `[9]E` 同类回归)。
- **卡死自家后端精准回收**:启动前若自家 PID 文件指向的进程仍存活,**经命令行签名核实是自家后端**(含 `astrostudyboot.jar` / `webchartsrv.py` + `-Dhorosa.runtime.owner` 标记)才 `kill -9` 续启,否则维持失败、**绝不误杀**。Windows 用 `tasklist`/`wmic` 查命令行。
- **就绪前最小同步热身**:就绪后、导航前同步跑一次最小 `/chart` 预热(`HOROSA_WARM_MINIMAL=1`),**严格非致命 + 有界**(超时即照常导航)。防 Spring 懒加载下首次排盘打冷 bean 弹「未就绪」。
- **Java 启动加** `-Dhorosa.runtime.owner=horosa-desktop`(供回收识别)。
- **curl 缺失兜底**:就绪 HTTP 探测在无 curl 时改用内置 python urllib,**绝不静默放行**(否则就绪坍缩成「仅端口监听」)。
- **铁律**:bind 错匹配只用精确 token(`Address already in use` / `Errno 48` / `BindException` / `Port N was already in use`),**绝不用裸 `port`**(否则 Spring banner / `--server.port=` 等正常输出会被误判为端口冲突)。

### C. macOS 专属(Windows 不照搬代码,只镜像语义)
- `Horosa_Desktop_Installer/src-tauri/src/main.rs`:`start_runtime_with_port_retry` / `error_is_port_conflict` / `PORT_RETRY_MAX` + 调用处。Windows 在其等价启动器里实现「失败→换口重试、web 不入环」。
- 单实例:**Mac 不加插件 / 不设 `LSMultipleInstancesProhibited`**(会破坏更新换版);若 Windows 双开是真问题,用 handoff-aware 的 `requestSingleInstanceLock`(更新换版时放行)。

---

## v2.4.0（重发补丁,版本号不变）— 热修「更新后卡启动页 / 不进主界面」(真因 cleanup_state 误杀静态服务器)

> 发布后真机发现此 bug,**版本号保持 2.4.0、覆盖重发原 GitHub release**(非 2.4.1)。**前两次误诊(快路径、模态弹框)没修好,靠真机实测定位。** 机制:[`更新后卡启动页-真因cleanup_state误杀静态服务器-v2.4.0.md`](更新后卡启动页-真因cleanup_state误杀静态服务器-v2.4.0.md)。

**性质:macOS 专属(Tauri 外壳 `main.rs` + `web_shutdown`/静态服务器实现)。共享 `Horosa-Web/` 零改动 → Windows 不必同步代码、不必重编 jar。**
- **真因**:`runtime_bootstrap` 的 `first_launch_after_update` 分支里调 `cleanup_state(&app)`,它把本次刚 `start_static_server` 起的静态服务器(web_port)`web_shutdown.store(true)` 关掉 → `emit_ready` 导航的 `frontend_url` 连不上 → 停启动页 + 按钮死(实测 curl web_port=000、进程零监听)。普通启动不走此分支故正常。
- **修法**:删掉首启分支里的 `cleanup_state` 调用(顺手去掉同路径阻塞式 MessageDialog,防御性)。
- **Windows 怎么办**:**只要 Windows 没有「更新后卡启动页/不进主界面」症状,无需动作**;若有,排查其首启路径是否在起好本地 web/静态服务后又把它关掉。

---

## v2.4.0（已发 2026-05-30）— 西占技法批量补全(6 技法全链路 AI) + 更新后自启修复 + orbs 存档

> 逐技法实现详解(校对用):[`西占新技法-逐技法实现详解-v2.4.0.md`](西占新技法-逐技法实现详解-v2.4.0.md);更新自启:[`更新后自启修复-v2.3.2.md`](更新后自启修复-v2.3.2.md)(文件名沿用旧标签,实际随 2.4.0 发)。

### A. 共享后端/前端(Windows **必须**同步,含**重编 `astrostudyboot.jar`**)

- **Java `astrostudysrv`(改了 → Windows 必须重编 jar)**:
  - `astrostudy/.../controller/PredictiveController.java`:新增 `/predict/dist`(界推运)、`/predict/agepoint`(年龄推进点)路由。
  - `astrostudy/.../controller/AstroExtraController.java`:新增 `/astroextra/greatconj`(木土大合相,仅 startYear/endYear 参数,不走 getBaseParams)。
  - `astrostudy/.../helper/AstroHelper.java`:加 AgePoint/Distribution/GreatConj 常量 + getter。
  - `astrostudycn/.../controller/ChartController.java`:`getParams()` 白名单加 `orbs`/`orbScale`(容许度透传)。
  - 重编(JDK17):`mvn -f astrostudy/pom.xml install -DskipTests && mvn -f astrostudycn/pom.xml install -DskipTests && mvn -f astrostudyboot/pom.xml clean package -DskipTests`。**`clean` 必须**(否则复用 5/28 旧 astrostudy/astrostudycn 依赖 jar——本轮真踩:fat jar 20:08 重打但内嵌 astrostudy-1.0.0.jar 还是 5/28,缺路由)。**验证用 `javap`(看 dist/agepoint/greatconj 方法在)而非内嵌 jar 的 mtime——内嵌 mtime 是 Maven reproducible-build 固定戳(5/28),不反映内容新旧。**
- **Python `astropy`(共享,同步)**:`astrostudy/perpredict.py`(`getDistributions`/`getAgePoint`,模块级 `from astrostudy.termdirection import TermDirection`)、`astrostudy/agepoint.py`(**新建**,Koch 宫 `swisseph.houses_ex2(...,b'K')`)、`astrostudy/astroextra.py`(`compute_great_conjunctions`,cap≈3400年)、`websrv/webpredictsrv.py`(`dist`/`agepoint` 端点)、`websrv/webastroextrasrv.py`(`greatconj`)。`flatlib-ctrad2` 的 object.py/arabicparts.py 亦有改。
- **前端 `astrostudyui`(共享,重建前端 `npm run build` + `build:file`)**:6 技法全链路 AI——`utils/astroAiSnapshot.js`(buildDodeca/Dispositor/LifespanSection)、`utils/aiAnalysisContext.js`(distributions/agepoint wired technique)、`utils/aiExport.js`(**六张登记表** + auxchartMap/extractor，见逐技法详解 §4-6)、`components/astro/{AstroDodeca,AstroDispositor,AstroLifespan,AstroDistributions,AstroAgePoint}.js`、`components/mundane/MundaneMain.js`、`components/divination/DivinationChartShell.js`(buildAiSnapshot prop + 刷新事件)、`utils/divinationCaseSave.js`(payload.aiSnapshot)、orbs 存档(`models/user.js`/`utils/localcharts.js`/`models/astro.js` 镜像 after23NewDay)。**勿改坏 pdMethod/主限法**。
- **验证**:`npm run build` + `build:file` 绿;`npm test` 29 套 140 全过(关键自检 `aiAnalysisContext.test` 技法 missing 契约 + `aiExport.test getAIExportAuditMatrix` 每技法六表齐)。

### B. Mac 专属(Windows N/A)— 更新后无法自动打开修复

**性质:macOS 专属(Tauri 外壳 `src-tauri/src/main.rs`),Windows 更新流不同。**
- **真因**:更新后首启被强制全量慢校验(`fast_path_enabled = !first_launch_after_update && …`),fast-path 标记只在整轮成功后才写;冷首启像卡死被强退→标记没写→下次又全量→反复(实测三启 trusted=0/0/1)。该全量冗余(`apply_update` 已 `verify_sha256`)。
- **修法**:对已验签 runtime 在 `start_runtime` 前预写标记 + 取消首启强制全量。
- **Windows 怎么办**:**只要无「更新后首启反复卡」症状,无需动作**;若有,按同思路改 Windows 自己 updater,**代码另写勿照搬 mac main.rs**。

---

## v2.3.1（发布中）— 更新后启动卡顿修复 + #10「服务不稳定」(SSE 并发竞态 + SSE 标志跨请求污染)

> 机制细节:[`服务不稳定-SSE并发与签名污染修复-v2.3.1.md`](服务不稳定-SSE并发与签名污染修复-v2.3.1.md)(#10)、[`更新后启动卡顿修复-v2.3.1.md`](更新后启动卡顿修复-v2.3.1.md)(更新卡顿)。

**性质:#10 全在共享后端 `astrostudysrv`(Java)→ Windows 必须重编 `astrostudyboot.jar`。更新卡顿部分是 Mac 外壳/启动脚本,Windows 各自维护对应实现。**

- **改了什么(#10 · 共享 · 必须同步)**:
  - `astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java`:新增线程安全内部类 `SseChannel`,收口**所有** SSE emitter 写(`send`/`complete`/`completeWithError` 单锁串行化 + `closed` 幂等);心跳与读流不再 race、**心跳不再自行 complete**(收尾统一在 `chatStream`)。修 AI「几句话后停止」。**保留** #8 的 `QueueLog.error` 一级异常日志 + `keep-alive` 心跳帧。
  - `boundless/src/main/java/boundless/spring/help/interceptor/RequestHeaderInterceptor.java`:`preHandle` ① 非 `REQUEST` dispatcher type **早返回**(免 async re-dispatch 用空 body 重复验签 → 消除 `signature.error`);② `REQUEST` 进来先 `TransData.setSSE(false)` **归零**(`__sse__` 存在 request 对象 attribute、Tomcat 复用 request 对象会残留 → 污染后续排盘/predict 的 `complete()`/`afterCompletion` 走 event-stream 分支)。需 `import javax.servlet.DispatcherType;`。
- **Windows 必须做什么**:同步上面两个 `.java`(共享路径完全一致)→ **JDK17 重编 `astrostudyboot.jar`**(`mvn -f boundless install → astrostudy install → astrostudyboot clean package`;gotcha #10,`clean` 必须)→ 替换 Windows 运行时 bundle 的 jar。**前端无改动、不重建前端包。**
- **更新卡顿部分(Mac 外壳/脚本 · Windows 自行对应)**:`Horosa_Desktop_Installer/src-tauri/src/main.rs`(更新标记「读取即消费」+ 首启 `emit_indeterminate_progress` 提示 + mongo 一律 skip ping)、`Horosa-Web/start_horosa_local.sh`(pid 判存活 `prune_stale_pid_file` + warmup 后台非阻塞 + 轮询 0.2s 与 trusted 解耦)。Windows 端若有相同的「更新后首启慢路径 / 残留 pid 误拦 / 更新标记残留」机制,在 Windows 对应启动器/脚本做同样修复;无对应实现则跳过。
- **验证**:重编后起服务,三套全过 = 功能零降级且验签未破坏 —— `verify_kentang_runtime_endpoints.py --root http://127.0.0.1:8899`(17 引擎 200)、`HOROSA_SERVER_ROOT=http://127.0.0.1:9999 node astrostudyui/scripts/verifyHorosaRuntimeFull.js`(exit 0)、`… verifyPrimaryDirectionRuntime.js`(exit 0,即 `/predict/pd`)。有真实 provider key 时:AI 长流完整不截断、排盘与 AI 交错不再 `signature.error`。
- **版本**:`2.3.1 / 2.3.1-runtime1`。

---

## （待发布·v2.3.0 同批·分支 `feature/heluo-school-interp`）河洛理数：取化工法（左栏选项）+ 运盘节气 label + 命运篇判断补全

> ⚠️ macOS 端**已实现、尚未发布**（分支 `feature/heluo-school-interp`）。纯前端，机制细节见
> [`河洛理数-流派与命运篇补全-v2.3.0.md`](河洛理数-流派与命运篇补全-v2.3.0.md)。先登记方便 Windows 同步。

- **改了什么**：① 取化工法做成河洛**左栏 per-技法选项**（土王寄坤艮/直取四方伯，镜像参评数古法/明法；**不入全局设置**）；② 运盘流年/流月行加**精确节气交时 label**（纯展示·不改卦序）；③ 命运篇补 5 项「可算却未显示」判断——阴阳二数命名（二十四数名）、众宗/众疾、顺/反数+季节宜、正/反对体凶、看命大法命格综合。均依《河洛理数》原文逐条审计，**主链算法零改**。
- **Windows 必须做什么**：重新同步前端 3 文件 `astrostudyui/src/utils/heluoLocal.js`、`src/components/shusuan/HeLuoMain.js`、`src/components/kinastro/KinAstroMain.js`（+ `scripts/_heluoTest.mjs`）；`npm run build` 然后 `npm run build:file`（顺序，勿并行）。**无 Java、不重编 `astrostudyboot.jar`、不重打 runtime。**
- **验证**：本机 `scripts/_heluoTest.mjs`（esbuild bundle → node）**96 断言全过**；`npm run build` 绿；preview 左栏「取化工法」可切、流年立春/流月节气 label、数名/命格/命局对体/顺逆/众宗 各行渲染（均已实测）。
- **典籍口径（已定稿）**：土用＝四立前 18 日（标准土王用事，采用·不改）；天数 39→4（「遇十用零数」规则正确）；A1 寄爻顺起**不做·已撤**（`yuanTang` 维持原始单一实现）。

---

## （待发布·分支 `feature/acg-map-upgrade`）占星地图（ACG / 地理占星）全面升级

> ⚠️ macOS 端**已本地提交、尚未发布**（分支 `feature/acg-map-upgrade`）。机制细节见
> [`acg-map-地理占星.md`](acg-map-地理占星.md)。先登记方便 Windows 同步。

**性质：前端 + Python + Java 都动了 → Windows 必须重编 `astrostudyboot.jar`。**
辅盘「占星地图」(`locastro`) 从旧的高德地图 + 迭代搜经度，整体换成 **D3-geo + 内置 GeoJSON + 赤经/赤纬解析法**。

**改动文件（都在 `Horosa-Web/`）**：
- Python：`astropy/astrostudy/acg/ACGraph.py`（重写为解析法：GMST=`sidtime`、RA/Dec=`cotrans` 真交角、四轴线全球连续+极区闭合到 MC/IC、地理参考线、Parans、Local Space、落点 `pointReport`；横线多点采样）；`astropy/websrv/webacgsrv.py`（新增 `acgpoint`）。
- Java：`controller/AcgController.java`（新增 `/location/acgpoint`）、`helper/AstroHelper.java`（`getAcg` 改 `requestNoCache` + 新增 `getAcgPoint`）。
- 前端：`astrostudyui/src/components/acg/` 改 `AstroAcg.js`，新增 `AcgD3Map.js`、`AcgPointPanel.js`、`interpretations.zh.js`、`world.geo.json`（Natural Earth 110m 开源国界，约 168KB，随源码走）。

**Windows 必做**：
1. **重编 `astrostudyboot.jar`**（动了 Java；JDK17：`mvn -f astrostudy/pom.xml install -DskipTests` → `mvn -f astrostudyboot/pom.xml clean package -DskipTests`，`clean` 必须）。
2. **重建前端**：`npm run build` 然后 `npm run build:file`（顺序，勿并行）。`world.geo.json` 会被打进包。
3. 无新增 npm/Python 依赖，无新端口（`acgpoint` 复用 `/location` 挂载）。

**验证**：辅盘→占星地图：四轴线平滑连贯（极区钩子闭合、跨180°不留缝）、白底/深底胶囊标注随明暗主题反色且**字形无描边**、参考线（赤道/黄道/回归线）可见、Parans 三态（关/日月/全部）、点击地图出落点分析；明暗主题切换地图跟随。

**关键坑（同步时照搬，勿"优化"掉）**：① 整宽横线必须多点采样（两点 `[-180..180]` 会被 d3 裁成点）；② 标注字形必须 inline `style('stroke','none')` 覆盖全局 `text{stroke}`（presentation 属性无效）；③ `getAcg` 必须 `requestNoCache`（否则改后端后同盘命中旧缓存）。详见技术文档。

---

## （待发布·v2.3.0 同批，与 ①–⑤ 合并）task⑥：辅盘新增「卜卦盘 + 择日盘」（西洋断事 + 事件盘存盘）

> ⚠️ macOS 端**已完成、已本地提交、尚未发布**（commit `d2ef43b` @ 分支 `feature/round-tasks-1-5`，52 文件 +4191/−28）。与下面 ①–⑤（`ffd0312`）**合并为同一版本发布（v2.3.0）**。先登记方便 Windows 同步，不必等发布。

**性质：纯前端（`astrostudyui/src`）零后端。** 本批里同步最简单的一项——**不动 Java/Python、不重编 `astrostudyboot.jar`、不重打 runtime**，只搬前端源码 + 重建前端包。引擎全部消费现成 `/chart` 端点字段（尊贵 / 相位含入出相 / 接纳 / 互容 / 映点 / 月空 / 日时主 / 逆行），前端只补算燃烧·角宫·月相·托勒密过滤 → 零新路由。

**新增 / 改动文件**：
- 新增目录：`src/divination/{data(17)/engine(9)/horary(6)/election(8)}`、`src/components/{divination/DivinationChartShell, horary/{HoraryMain,HoraryJudgment}, election/{ElectionMain,ElectionJudgment}}`；新增 `src/utils/divinationCaseSave.js`。
- 改动文件：`src/components/auxchart/AuxChartMain.js`（注册两子盘 TabPane+dock + `componentDidUpdate` 响应 `currentSubTab`）、`src/pages/index.js`（`auxChartTabs` 补全 `harmonic/horary/election`）、`src/utils/aiExport.js`（导出技法+设置+挂载+快照）、`src/utils/localcases.js`（`CASE_TYPE_OPTIONS`+别名加 horary/election）、`src/layouts/app.less`（`:global` 判断卡片 CSS）。

**关键变化（逐条）**：
1. **卜卦** 右栏 5 tab（裁决/征象/完成/时空/描述）：Sibly71+Dorotheus43+Sahl+Hephaistion+盗窃11步。完成 tab 把所有可能用到的征象摆出供用户自判：**光线传递明确写出「由谁在哪两星间传递」**、月亮的故事（刚离→将会）、相位全览（仅托勒密五相位）、三分法则白话解释。
2. **择日** 右栏 5 tab（总评/红线/分项/应期/建议）：13 模块 + 红线**中文分级**（严重/较重/中等/轻微）+ 0–100 评分 + 27 用事专属 + 本日逐时/未来14日扫描择优；应期相位名中文化。
3. **AI 四环节同步**：导出技法 / 导出设置（preset 含「月亮的故事」「相位全览」+ `applyUserSectionFilter` 防旧设置过滤）/ 分析挂载（`module:horary|election`）/ 快照。
4. **事件盘双向存盘**：Shell「存为事件盘」→ 事件盘库（复用 `astro/openDrawer` caseadd 管道，同六壬）；`CASE_TYPE_OPTIONS`+别名加 horary/election（`tab=auxchart`，否则 `getCaseTypeMeta` 默认落 cnyibu 路由错）；列表 `user/applyCase`（**未改、现成**）→ Shell `applyRestoreIfAny` 拉 `currentCase` 还原时间/地点/类别/设置（caseVersion 防重，六壬式拉取）；**坑**：AuxChartMain 原 `findTab()` 只读 state→加 `componentDidUpdate`(照 CnYiBuMain) 才能被 applyCase 切子盘；`index.js auxChartTabs` 原漏 harmonic/horary/election 已补。Shell 加 `_mounted` 守卫消除异步 setState 告警。
5. 删除择日右栏本命合参死代码（合参按需求归**中间栏叠盘**，属后续项）。

**Windows 端必做**：
- ✅ **同步前端源码**（上列新增目录 + 5 个改动文件 + `divinationCaseSave.js`）。纯 JS/LESS，无平台分支。
- ✅ **重建前端**：`npm run build` 然后 `npm run build:file`（顺序勿并行）。
- ⏸ **不需重编 `astrostudyboot.jar`**（没动 Java）。
- ⏸ **不需重打 Python runtime**（没动 `astropy`/`vendor`）。

**验证**：`npx umi-test src/utils/__tests__/localStorageManagement.test.js`（16/16，含覆盖新 case 类型的遍历测试）+ `aiAnalysisSelection.test.js`（3/3）；preview 辅盘 dock 出「卜卦盘/择日盘」→ 起盘出完整圆盘 + 右栏 5 tab；「存为事件盘」→ 事件盘列表见「卜卦/择日」类型 →「应用」切回对应子盘并还原时间/地点/类别；AI 导出选两盘时分段齐全（含月亮的故事/相位全览）。

**机制详见**：[`docs/horary-election-charts.md`](horary-election-charts.md)

---

## （待发布·随 task⑥ 合并）①–⑤ 修复：AI代理 Issue #9 + 六壬发三传 + 占星右栏空白块 + 风水UI + 快捷dock

> ⚠️ 本节是 macOS 端**已完成、已本地提交但尚未发布**的一轮修复（commit `ffd0312` @ 分支 `feature/round-tasks-1-5`），将与 **task⑥（辅盘加「卜卦盘」「择日盘」，另一 session 做）合并后一起发布**；**随 v2.3.0 合并发布**。先在此登记，方便 Windows 同步，不必等发布。

**改动范围**：前端（`astrostudyui`）+ Java 后端（`astrostudysrv`，**因 ① 需重编 `astrostudyboot.jar`**）+ 启动器 JVM 参数。

**关键变化（逐条）**：
1. **#9 内置 Java 走系统代理（治本）**：`boundless` `HttpClientUtility.getHttpHost()` 加 `ProxySelector.getDefault()` 回退；`astrostudy` `AIAnalysisProxyService.streamHttpClient` 加 `.proxy(ProxySelector.getDefault())`；启动器加 `-Djava.net.useSystemProxies=true`。**只加 flag 无效**（流式 JDK HttpClient 默认不走代理、`getHttpHost` 只读 `http.proxyHost` 系统属性而 flag 不填它）——三处缺一不可。
2. **六壬 / 三式合一 发三传顺序**：`components/liureng/ChuangChart.js` `getSangCuang` 把八专(isBaZhuang)移到遥克(isYaoKe)之后（按典籍 `0.基石/2.九法`：遥克第4法→八专第9法）。**六壬引擎是我们自有前端 JS，非 ken**；标准六壬与三式合一共用 `ChuangChart`，一改两修。纯前端。
3. **占星右栏 tab 下空白块**：`app.less` `.horosa-content-tabs .ant-tabs-tabpane > *{height:100%}`，内容容器填满 pane（覆盖占星/紫微/印度/果老 + 复用 AstroChartMain 的十三分盘/合盘/节气）。纯前端 CSS。
4. **风水页 UI**：选择栏对齐 + 文字间距 + 安全距离精修（语义色不动）。纯前端 CSS。
5. **快捷功能 dock**：基础 `.horosa-bottom-quick-actions` 列网格 `repeat(8)`→自适应 `grid-auto-flow:column`（兼容太乙等动态动作数）。纯前端 CSS。

**Windows 端必做**：
- ✅ **重编 `astrostudyboot.jar`**（仅 ①：`HttpClientUtility.java` + `AIAnalysisProxyService.java`），重编后**重启 Java 进程**。
- ✅ **Windows 启动器加 `-Djava.net.useSystemProxies=true`**：macOS 在 `start_horosa_local.sh` 已加；Windows 外壳不共享，需在 Electron `service-manager.js` spawn Java 处各自加（① 才算完整修复）。
- ✅ **重建前端**（`npm run build` → `npm run build:file`，顺序勿并行）：②③④⑤ 都是前端，一次重建即可。
- ⏸ Python runtime 不需重打（vendor 未动）。

**验证**：`npx umi-test src/components/liureng/ChuangChart.test.js` 期望 3/3；preview 检查 占星右栏内容填满（无 tab 下空白）/ 风水选择栏间距 / 太乙底部 dock 填满；① 真·代理需 Windows 开系统代理后在「测试连接」实测（无代理时回归不变）。

**机制详见**：[`docs/round-tasks-1-5-fixes.md`](round-tasks-1-5-fixes.md)

---

## v2.2.1 — 日界点完成版（含晚子时·时柱起干第二开关）+ ChartController 白名单 bug + AI 分析 SSE 双修复 Issue #8

**改动范围**：前端 + Java 后端（需重编 `astrostudyboot.jar`）；Python vendor 暂未动（Phase 2）。

**关键变化**：
1. **新增第二个独立全局开关「晚子时·时柱起干」**：
   - `lateZiHourMode = 'nextDay' (默认) | 'today'` （后端字段 `lateZiHourUseNextDay = 1|0`）
   - 只在 `hour ∈ [23:00, 24:00)` 影响时干；与日柱开关 `after23NewDay` 完全独立。
   - 27日 23:30 矩阵详见 `Horosa-Web/docs/global-day-boundary-v2.2.1.md`。
2. **修复 ChartController.getParams() 白名单丢字段 bug**：旧版 `getParams()` 不显式 `putAll("after23NewDay")` 导致 Java backend 永远拿默认值，本版本一并修复 + 加 `lateZiHourUseNextDay`。**Mac 端在审计中又发现 7 个同型 controller**（BaZiBirth/PaiBaZi/LiuReng/ZiWei/Nongli/JieQi/QueryChart）+ 3 个 Model（BaZiDirect/LiuReng/ZiWeiChart）也缺 `lateZiHourUseNextDay` 透传 → 全部修。Windows 同步 jar 时这一批控制器变更要一并带过去。
3. **AI 挂载**：`buildAstroSnapshotContent` 加 "排盘规则" 行，AI snapshot/导出 markdown 显式标注两个开关状态。
4. **持久化**：命盘 / 案例 schema 都加 `lateZiHourUseNextDay` 字段；保存/恢复时按用户实际选择走。
5. **jest 自检**：新增 6 个时柱开关 case，含核心新 case `after23=0 + lateZi=0 → 辛丑 戊子`。
6. **Windows Issue #8 / AI 分析"GPU 加载完后划水然后停止"修复**（`AIAnalysisProxyService.java`）：
   - **Fix 1（必须）** — catch 块第一步必须 `QueueLog.error(AppLoggers.ErrorLogger, e)` 记录一级异常，`sendEvent` / `completeWithError` 各自嵌套 `try`。修了之前"上游 Ollama 抛错 → catch 内 sendEvent 撞 `ClientAbortException` 抛 `RuntimeException` 把 `ai-analysis-chat-stream` 线程炸了 → 原始一级异常被 `safeErrorMessage` 吞掉根因黑盒"的可观测性 bug。
   - **Fix 2（治本）** — `streamOpenAICompatible` / `streamAnthropic` / `streamGemini` 三处全部包一层 `withHeartbeat`，每 15s 给 emitter 写 `: keep-alive` 注释帧，防止 Ollama 慢首 token（本地 10–60s）期间客户端/Chromium/中间件按空闲超时切断 SSE socket。心跳本身 try-catch；发现客户端断了主动 `emitter.complete()` 并停 schedule。
   - **防回归** — `release_preflight.sh` 加 [7] 哨兵：grep `QueueLog.error(AppLoggers.ErrorLogger` 与 `keep-alive` 必须命中 `AIAnalysisProxyService.java`，任一丢失阻断发布。Windows 端 `release_selfcheck.py` 建议同步同款 grep 哨兵。

**Windows 端必做**：
- ✅ **重编 `astrostudyboot.jar`**（`BaZiHelper.java`、`BaZi.java`、`NongliHelper.java`、`OnlyFourColumns.java`、`ChartController.java` 都改了）。重编后**必须重启 Java 进程**（吸取 Mac v2.2.1 教训：旧 launcher 进程残留会让新 class 形同未上线 — 用 `lsof -ti :9999` + `ps -p PID -o lstart=` 确认）。
- ✅ **重新 `npm run build`**（前端 baziLunarLocal / aiAnalysisContext / models 都改了）。
- ⏸ Python runtime 包**不需要重打**（vendor 暂未动）。
- 🔒 `release_preflight.sh` 版本门禁应升级到 2.2.1。
- 🔒 launcher version assertion 升 2.2.1。

**验证**：跑 `npx umi-test`（期望 139+ all green），preview 检查 27日 23:30 四 case 矩阵，重点验证 `after23=0 + lateZi=0 → 辛丑 戊子`（新行为）。

**机制详见**：[`Horosa-Web/docs/global-day-boundary-v2.2.1.md`](../Horosa-Web/docs/global-day-boundary-v2.2.1.md)

### v2.2.1 补充（发版前收尾这一轮——以下都要同步到 Windows）

> 机制详见 [`docs/v2.2.1-session-addendum.md`](v2.2.1-session-addendum.md)。

1. **`(1,0)` 边界四柱一致性（Java，必同步 + 重编 jar）**：`BaZiHelper.getTimeColumn`（两个重载）+ `getTimeGanziStr` + `getTimeStartGan` 共 **4 条**晚子时时柱分支,原来只写了 `after23=0 && lateZi=1` 一侧,**漏了对称的 `after23=1 && lateZi=0`**(日柱进位次日但时柱按今日干起 → 应退一位 `+9`)。补全后 `(1,0)=戊子`,与 baziLunarLocal/奇门/太乙一致(此前 Java 系技法返 庚子)。**钉定矩阵更新为 `(1,0)=壬寅 戊子`**(release notes 已改)。
2. **Moira / 金口诀 / 太乙 切换后需刷新才生效（前端，必同步）**：根因是各自 fetch 把两开关漏在 payload / client cache key 外。`guolao/GuoLaoChartMain.js normalizeChartParams`(cache key 补两开关)、`jinkou/JinKouCalc.js fetchJinKouPan`(payload 补两开关 + genGodsParams)、`taiyi/TaiYiCalc.js fetchTaiyiPan`(payload 补 lateZi)、`dunjia/DunJiaCalc.js fetchQimenPan`+`DunJiaMain getQimenOptionsKey`(已含)。后端 webqimensrv/webtaiyisrv/webjinkousrv + Java `/liureng/gods` 都已读两开关。
3. **AI 挂载之前是死代码（前端，必同步）**：`utils/aiAnalysisContext.js buildDayBoundaryMeta` 之前**定义了但从未被调用** → AI 实际看不到排盘规则。本轮在 `buildContextLayers` 加「排盘规则（日界点·晚子时）」上下文层 + `utils/aiExport.js` 导出头加同款行。之前 release notes 宣称的「AI 挂载排盘规则」现在才真正生效。
4. **AI 供应商连通性（Java + 前端，必同步）**：① `AIAnalysisProxyService.buildAnthropicBody` 的 content 块过去复用 Gemini 的 `buildTextPart`(只有 `text`)→ Anthropic 报 `messages.content: missing field type`(503),对话+测试连接全挂;新增 `buildAnthropicTextPart` 补 `type:"text"`(Mac #9)。② 前端 `AIAnalysisMain.testProfileChat` catch 把 URL 编码的裸 401 解码 + 对未登录/未配置给可操作中文提示(Mac #8)。③ `boundless/HttpClientUtility.getHttpHost` 无代理环境变量时回退读 `http(s).proxyHost` 系统属性(Win #9,**需 Windows 实测**;纯增量无属性时行为不变)。④ **Win #8 Ollama「加载后不出字」已排查 = Ollama/Windows 环境问题**(端点 `/v1` 正确、心跳+无超时已在),非应用 bug,Windows 端核查环境/GPU。
5. **软件内升级非阻塞 UX（macOS launcher 自研,Windows 壳自理；但前端 UpdateNotifier 共享）**：`main.rs` 新增 `update_check_silent`/`update_start_background`/`update_install_and_restart` + `horosa://update-*` 事件(不接管 launcher 界面);启动自动检测改 emit `update-available` 非阻塞。**前端共享件**:`components/update/UpdateNotifier.js`+`.less`(挂 `layouts/app.js`)、`utils/aiAnalysisDesktop.js` 三个 update 桥函数、`PageHeader` 设置菜单加「检查更新/关于星阙」。Windows Electron 壳的更新命令需 Win 端按同样事件/命令名自行接线。
6. **偏好设置精修（前端,纯样式/文案,必同步）**：`xq-ui` 令牌下统一 `PageHeader.less` 的 `aiSetting*` 说明卡 + 新 `about*` 样式 + 关于弹窗;不动任何数据绑定/语义色。

**本轮额外重编 jar**:Java 改了 `BaZiHelper`(getTimeColumn/getTimeGanziStr/getTimeStartGan)+ `AIAnalysisProxyService`(Anthropic type)+ `boundless/HttpClientUtility`(proxy)→ Windows 必须重编 `astrostudyboot.jar`。

**验证**:`npx umi-test` 139 green;preview 27日23:30 跑 `(1,0)=戊子` 跨技法一致;桌面壳模拟 `horosa-latest.json` 更高版本验证非阻塞卡片→后台下载可最小化→重启更新;偏好弹窗亮/暗;AI 配 Anthropic key 测试连接应成功。

---

## v2.3.0 — 全局日界点（早/晚子时换日）+ 自动更新稳定化

> 性质：**前端（`astrostudyui`）+ Java（`astrostudysrv`，4 个 Controller）+ Python（`astropy/websrv` + `vendor`，7 个引擎+service）+ macOS launcher（Tauri `main.rs`）**。
> ⚠️ **本版含 Java 改动 → Windows 必须重编 `astrostudyboot.jar`**；含 Python vendor 改动 → 重新 rsync `Horosa-Web/vendor/` 到 runtime；自动更新 P0 修复在 macOS launcher（main.rs）—— Windows Electron 壳的自动检查更新接线**属 Win 端自理**（不同 OS、不同壳）。

机制细节见 [`global-day-boundary-v2.3.0.md`](global-day-boundary-v2.3.0.md)。

### 前端 + Java（共享 `Horosa-Web/`）
- 新「设置 → 全局设置」Modal（`XQSegmented` 二选一：23点后次日 / 24点后次日），存 `app.dayBoundary`，复用 `globalSetup` localStorage。
- 新建 `utils/dayBoundary.js`：`defaultAfter23NewDay()` 实时读全局，各技法回退使用（不依赖 React/dva，纯函数）。
- **修核心 bug** `utils/baziLunarLocal.js:637` `setSect` 按 `after23NewDay` 决定（八字/河洛/参评/preciseCalcBridge 本地 nongli 受益，单测 + lunar setSect(1)/(2) 方向验证：23:30 → 己卯 / 戊寅）。
- **修核心 bug** `components/dunjia/DunJiaCalc.js` 移除 `buildGanzhiForQimen` 二次进位（避免与后端 nongli 已换日叠加成双重换日，附注释防回退）。三式合一复用 `DunJiaCalc`，自动受益。
- 各技法 `after23NewDay` 默认值统一接 `defaultAfter23NewDay()`：奇门/太乙/金口/六壬/六爻/紫微/三式/八字/河洛/参评 + `aiAnalysisContext`（3 处）。
- `fieldsToParams` 补传 `after23NewDay`：主盘 `models/astro.js`、`hellenastro/AstroChart13`、`astro/IndiaChart`、`guolao/GuoLaoChartMain`、`jieqi/JieQiChartsMain` `genParams`、`utils/preciseCalcBridge.js` `JIE_QI_YEAR_KEYS`、`utils/aiAnalysisContext.js` `buildCaseSnapshotParams`。
- `KinAstroMain.js buildPayload`（一处覆盖 shaozi/tieban/chunzi/fendjing/nanji/beiji/xianqin/cetian 等 kinastro 系）+ `WuZhaoMain` / `HuangJiMain` / `ShenYiShuMain` 各自 payload 补传。
- **Java 4 处硬编码 `false` 改读参数 → 重编 jar**：`astrostudycn/.../ChartController.java:75`、`JieQiController.java:64`、`QueryChartController.java:40`，以及 `astrostudy/.../NongliHelper.java:680`（被 `chart13`/印度盘调用）。覆盖主盘/七政底盘/紫微底盘/28宿/印度/分至/历史/中点/推运。重编链：boundless（不变可跳）→ astrostudy install → **astrostudycn install** → astrostudyboot clean package（JDK17）。

### 后端 Python vendor + websrv（rsync 同步，**无需重编 jar**，但需重打 runtime 包）

7 个技法组（详细模式见 fix 文档）：

| 技法 | 改造文件 |
|---|---|
| wuzhao（五兆） | `vendor/kinwuzhao/config.py`（gangzhi1/gangzhi 加 `after23_new_day=1` 参数 + `and` 条件）+ `astropy/websrv/webwuzhaosrv.py` 取参传引擎 |
| nanji（南极神數） | `vendor/kinastro/astro/nanji/calculator.py:465 from_solar_datetime` 加参 + `webnanjisrv.py` 传 |
| shaozi/tieban/chunzi | `vendor/kinastro/astro/shaozi/calculator.py:221 calculate_ganzhi_from_datetime` 加 `after23_new_day=1` 参数，模式 B：`if after23 and hour==23: 日期+1 算日柱`（时支保留原 hour）。一处引擎覆盖三个 service（webshaozisrv/webtiebansrv/webchunzisrv） |
| fendjing（鬼谷分定经） | `vendor/kinastro/astro/fendjing/fendjing_calculator.py:114 compute_fendjing_chart` 加参 + `webfendjingsrv.py` 传 |
| shenyishu（神易数，日柱进卦） | `vendor/shenyishu/shenyishu.py:300 Shenyishu.__init__` 加参 + `webshenyishusrv.py` 传 |
| qizheng（七政四余 kin 版） | **service 层 jd 调整**（引擎不动）：`astropy/websrv/webqizhengkinsrv.py` 算日柱前 `jd_for_day = chart.julian_day + (1.0 if dt.hour==23 and after23 else 0.0)`，shensha/get_bazi_stems_branches 用 `jd_for_day`；compute_chart 的星历 jd 不动 |
| wangji（皇极经世） | **thread-local 方案**避免深透传：`vendor/kinwangji/kinwangji/wanji.py` + `jieqi.py` 各加 `_AFTER23_LOCAL = threading.local()` + `set_after23_new_day`/`_is_after23_active`，3 处 `if hour==23 and _is_after23_active()`；`astropy/websrv/webwangjisrv.py` 在 `wanji_four_gua` 调用前 import 两个 set 函数并 set |

**豁免**（不改，避免破坏已工作的主流）：
- 奇门 kinqimen / 太乙 kintaiyi / 金口 kinjinkou 引擎内部的 `if hour==23` —— 前端 nongli/overlay 已决定日柱，引擎内部那处不影响展示。
- 京房/荆诀 jingjue（纯 seed 起卦）、太玄 taixuan（cnlunar 第三方固定 23 点换日、不可参数化）、北极 beiji（不显示日柱）、演禽 xianqin（农历定宫）：不涉及/不可控。
- 死代码/死副本：`kinastro/astro/bazi/calculator.py`、`damo`、`diqiyijue`、`liuyao_lifetime`、`kinwangji` 顶层副本、`kinastro/astro/wangji/*`（审计确认无 service import）。
- `vendor/kinastro/astro/bazi/constants.py:571` 是**时支索引**（子时 23-01 点→0），不是日柱换日，**不要动**。

### macOS launcher（`Horosa_Desktop_Installer/src-tauri/src/main.rs`）—— Windows 端不适用
自动更新 P0：接线「自动检查更新」死开关——`auto_check_updates: bool` 在 `main.rs:257/286` 定义且默认 `true`，但 setup 闭包**从不消费它**（这就是体感「自动更新不工作/不稳定」的核心）。在 setup 闭包末尾、`Ok(())` 前加 `thread::spawn`：启动延迟 10 秒，若偏好启用则静默 `resolve_update_plan`，**仅当发现新版才调 `check_for_updates`** 弹更新框，无更新/网络失败静默 `eprintln!` 写日志（避免每次启动打扰）。**需重编 launcher**（`cargo build --release`，或走完整 `npm run tauri build`）。

注：本仓自研 OTA（`reqwest` + GitHub Release + SHA256 + bash helper + `ditto` 替换 + Apple 公证装订）已确认**不迁** Tauri 官方 `tauri-plugin-updater`——自研方案承担 app + 独立 runtime.tar.gz 双更新 + 双向回滚 + 离线 pkg 兜底，官方做不到。

Windows Electron 外壳的自动更新另算（不在本仓代码内）。

### Windows 自检
1. 同步 `Horosa-Web/` 全部改动（前端 + Python vendor + Python websrv + Java 源）。
2. 重编 jar（JDK17，4 模块链：astrostudy → astrostudycn → astrostudyboot clean package）。
3. 前端：`npm run build && npm run build:file`（顺序，不并行）。
4. 启动栈，浏览器进「设置 → 全局设置」看 Modal（两个单选+当前态）；进八字页设 23:30 切换「23点算第二天/当天」下拉，日柱在 **己卯 / 戊寅**（次日 / 当天）跳变；任意命盘技法移动时间到 22:59→23:01，日柱按全局设置在 23 点边界跳变。
5. 抽查 wangji/wuzhao/shaozi 的 23:30 日柱在两个设置下不同（embedded python 直调引擎可独立验证）。

---

## v2.2.0 — 数算两新技法（邵子参评数 / 河洛理数）+ 调波盘绘制 + 风水 React 化

> 发布版本号 **2.2.0**（开发期内部标记曾用 v2.1.9；下列技术文档文件名仍带 `-v2.1.9` 但即本版内容）。

> 本版含：v2.1.8 专轮延后的两项 UI（#9 调波盘、#11 风水），以及「数算」模块两个新技法（邵子参评数 canping、河洛理数 heluo，全前端本地计算）。

**性质：前端（`astrostudyui`）+ Python（`astropy`，rsync）+ Java（`astrostudysrv`，仅 #6 AI 修复）。⚠️ 因含 Java 改动，本版**必须重编 `astrostudyboot.jar`**（#9 调波盘是 Python、#11 风水与数算两技法是纯前端；唯独 #6 的后端加固动了 Java）。数算两技法连 Python 都不涉及。**

### #9 调波盘：绘制调波盘本体（复用量化盘星盘 UI）
机制细节见 [`harmonic-chart-v2.1.9.md`](harmonic-chart-v2.1.9.md)。
- **后端 Python（rsync，无需重编 jar）**：
  - `astropy/astrostudy/thirteenthchart.py` 新增 `HarmonicChart`（与 `ThirteenthChart` 同构：逐点 `relocate(lon*harmonic%360)` + ASC/MC 变换、DESC/IC=+180、房宫 equal-30、`reinit`）。
  - `astropy/astrostudy/astroextra.py` `build_harmonic`：套用 `HarmonicChart` 后，在原有 `positions/conjunctions` 基础上**增量返回**完整盘对象 `chart`（与 `/chart` 同形）。复用现成 `/astroextra/harmonic` 端点，不新增路由。
- **前端（`build` 然后 `build:file`）**：
  - `components/auxchart/AstroHarmonicLab.js` 重写为量化盘布局（复用 `horosa-aux-module-page xq-chart-renderer-germany` + `horosa-midpoint-*` 既有 CSS）：左大盘 `astro/AstroChart value={result.chart}`，右栏调波数控件 + 两表。**最外层勿包 `Spin`**（会断开 `app.less` 填充选择器的直接子链）。
  - `components/auxchart/AuxChartMain.js`：给 `AstroHarmonicLab` 透传 `planetDisplay/chartDisplay/lotsDisplay/showAstroMeaning`。

### #11 风水：iframe → React 全重写 + 明暗 + 占屏
机制细节见 [`fengshui-react-rewrite-v2.1.9.md`](fengshui-react-rewrite-v2.1.9.md)。**纯前端，不重编 jar。**
- 新增 `components/fengshui/fengshuiEngine.js`（从 `public/fengshui/app.js` 移植的框架无关 canvas 引擎：常量/绘制/几何/判定/撤销重做/导出/快照；画布铺满工作区、图居中、纳气盘延伸出图不被裁）。
- 重写 `components/fengshui/FengShuiMain.js`（Antd 重构 + `<canvas ref>` + `ResizeObserver`→`resize` + `keydown` + AI 快照 `saveModuleAISnapshot('fengshui')`/`horosa:refresh-module-snapshot`）；**删除 iframe**。
- `layouts/app.less` 末尾 `:global { .horosa-fengshui-* }` 布局+明暗。
- **两坑**：`app.less` 是 CSS Module，全局类必须包 `:global{}`（否则被哈希）；canvas 必须 `position:absolute`（否则 in-flow + ResizeObserver 高度失控）。
- 嵌入模式本就隐藏的「项目管理/项目文件/最近/自动保存」按原样略去。`public/fengshui/` 旧独立站点无引用，可后续清理。

### 数算新技法：邵子参评数（canping）+ 河洛理数（heluo）
机制细节见 [`shusuan-canping-heluo-v2.1.9.md`](shusuan-canping-heluo-v2.1.9.md)。**纯前端本地计算，四柱来自 `utils/baziLunarLocal.js`（星阙自己的八字），不碰任何 kentang/Python 后端，不重编 jar。**
- 在「数算」既有金色技法 rail（`components/kinastro/KinAstroMain.js` `renderTechniqueRail` 内 `moduleKey==='shusuan'` 的硬编码列表）**新增两个入口**，不是另起一条 rail。
- `TECHNIQUE_CONFIG` 加 `canping`/`heluo`（`native:true`）；`fetchPan` 对 `native` 直接跳过 `postKinAstro`；`renderCenter`/`renderRightPanel` 顶部加 native 分支渲染原生组件；`constructor` state 加 `canpingMethod/canpingLiunian`。
- **邵子参评数**（金锁银匙）：`utils/canpingLocal.js` + `utils/data/canpingTiaowen.json`（五部×78）；组件 `components/shusuan/CanPingMain.js`（古法/明法开关、本命/大运/流年）。
- **河洛理数**：`utils/heluoLocal.js`（起命 天地数→卦→元堂→后天、起运 大限/流年、命运篇 元气/化工/得体等判断、爻辞查找）+ `utils/data/heluoTiaowen.json`（64卦×6爻，由 `scripts/buildHeluoData.js` 从 5 个条文 md 解析；脚本读 Obsidian 源 `~/Documents/Obsidianl Vault ABCDE/玄哲/4.条文/河洛理数/`，**仅生成的 JSON 入库**）；组件 `components/shusuan/HeLuoMain.js`（先天/后天卦象+元堂+爻辞、大限表点选联动流年、右栏命运篇判断）。
- `layouts/app.less` 末尾 `:global { .horosa-canping-* }` 与 `:global { .horosa-heluo-* }` 布局+明暗。
- 算法验证：`scripts/_heluoTest.mjs`（esbuild bundle 后 node 跑）共 72 断言全过——含算例 甲子丁卯庚申庚辰→天风姤·上九、董盘 丙戌丁酉丙寅癸巳→先天否上九/后天临六三、大限 1–45/46起、**先天/后天 5 个大限的流年逐卦逐动爻、含 临初九后天阳爻大限(起阴年)**、多年流月(2021/2052/2057/2075/2076)、流日 30 日动爻初→上、理数含/藏/覆。
- **⚠️ v2.2.0 流年算法修订（覆盖发布）**：初版 `liuNian` 的动爻位写死从初爻数（阳爻 1..6、阴爻 1..5），**只在元堂=上九时偶合**，其余大限流年全错。已按典籍重写为**从上一年動爻往上一爻链式累变**（阳爻另加首年阳年不变/阴年变元堂 + 第2、3年连变应爻）。Windows 端**重新同步 `utils/heluoLocal.js`** 即可（纯前端，无 Java，不重编 jar）；对照本机 `_heluoTest.mjs` 72 断言。

### #6 AI 分析：模型选项不能覆盖（前端 + Java）⚠️ 本版唯一 Java 改动
机制细节见 [`ai-model-selection-fix.md`](ai-model-selection-fix.md)。根因纯前端：测试连接/下拉用全量模型（含 embedding）首个、无视选中聊天模型 + Gemini 预设 `defaultChatModels: []` 导致唯一模型是 `text-embedding-004`，被当聊天模型送进 `:generateContent` → 404。后端无此 bug，加固为防御性。
- **前端（`build` 然后 `build:file`）**：
  - `utils/aiAnalysisProviders.js`：Gemini `defaultChatModels` 补 `['gemini-2.5-flash','gemini-2.5-pro']`。
  - `components/aianalysis/AIAnalysisMain.js`：新增 `normalizeProfileChatModels`（全量上剔除 embedding）；模型下拉 `modelOptions`、profile 列表「聊天模型」展示、`testProfileChat`（加 `preferredModel`，无模型时清晰提示而非静默 404）改用之；工具栏「测试连接」传选中模型；`ensureChunkEmbeddings` 的 `requestEmbeddingVectors` 补 `providerOptions`。
  - `utils/__tests__/aiAnalysisProviders.test.js`：+Gemini 默认聊天模型断言。
- **后端 Java（`astrostudysrv` → 必须重编 `astrostudyboot.jar`）**：`astrostudy/.../service/AIAnalysisProxyService.java`：`embeddings()` 两处 `buildAuthHeaders` 2 参→3 参带 `params`（修自定义鉴权头在 embeddings 失效）；`chat()`/`chatStream()` 解析 model 后加 `isEmbeddingModel` 守卫，抛 580014 可读错误。

### #7 拉取模型失败 — 本版不改码
OpenAI/OpenRouter 同时「拉取模型失败」。后端 `listModels` 链路（URL 拼接 / `Authorization: Bearer` / OpenRouter `HTTP-Referer`+`X-Title` / `extractModelIds` 解析 `data[]`）经核对无误，且 OpenRouter `/models` 为公开端点（无 key 也返回）；同时失败最可能是**上报者机器连不上外网（网络/代理）**。本版不改码，仅在 GitHub issue 给排查指引（引导用「连接诊断」DNS/TCP/HTTP）。Windows 无需同步。

### Windows 要做
同步上述 `Horosa-Web/` 改动 → **本版含 Java 改动（#6 `AIAnalysisProxyService.java`），必须重编 `astrostudyboot.jar`** → 同时重建前端（`npm run build` 然后 `npm run build:file`）；Python（`astropy`）随源码同步。数算两技法连 Python 都无关，只随前端 `src/` 同步即可（`utils/data/*.json` 务必带上）。#7 不涉及代码同步。

### 验证
- #9：辅盘→调波盘出现完整大盘（ASC/星/宫/相位按调波数变换）；改调波数盘与表即时重绘；明暗均正常。
- #11：风水→上传户型图→框选房屋→纳气盘八方(气红水蓝)外接房屋框且延伸出图不被裁→放置标记→判定列表/汇总→AI 快照写入；明暗、占满屏（无底部空隙）均正常。
- 数算：右侧金色 rail 出现「邵子参评数」「河洛理数」（不是新蓝条）；中右栏皆用 app 卡片样式。
  - 河洛理数→左输时间→中栏先后天卦象+元堂+爻辞、大限/流年表每行带「卦气」标签且点击就地展开爻辞、右栏命运篇 4 卡；化工按真实节气**准确**算（用项目既有 `lunar-javascript`，无新依赖、无后端）；顶部可正常上滑（`align-self:flex-start` 修复）。
  - 邵子参评数→「取法」古法/明法下拉在**左栏**、切换重算；中栏列 1–120 岁全表流年。
  - 二者明暗均正常。
- #6：新建 Gemini 配置预填 `gemini-2.5-flash/2.5-pro`；模型下拉不再出现 `text-embedding-004`；选中聊天模型「测试连接」走选中模型、无模型时给清晰提示；把 embedding 模型送 chat 被后端拦下报可读错误（需重编 jar 生效）。`aiAnalysisProviders.test.js` 4 断言全过。

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

> 打包链路提示(`Horosa_Desktop_Installer/` 不共享,仅供参考):本版 macOS 端发现 `scripts/verify_launcher_console_states.py` 硬编码了 launcher 的 `来源 pkg <版本>` 断言(launcher 用 `APP_VERSION` 渲染该行),漏改会在「编译+签名+公证」之后才报 ready-state 失败。macOS 已把它纳入 `release_preflight.sh` 的版本 lockstep 门禁。Windows 打包链路如有同类「launcher 版本断言」,请同样每版同步、并在 preflight 里加门禁。

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
