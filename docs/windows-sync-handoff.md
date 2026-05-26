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
