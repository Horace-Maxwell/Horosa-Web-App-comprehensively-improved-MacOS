# 本轮修复 ①–⑤ — 技术文档（给 Windows 同步）

> **状态**：这 5 项已在 macOS 端完成 + 验证，本地提交于分支 `feature/round-tasks-1-5`（commit `ffd0312`，6 文件 +115/−16），**尚未发布**。将与 **task⑥（辅盘加「卜卦盘」「择日盘」，由另一 session 做）合并后一起发布**（目标版本约 **v2.2.2**，以合并发布的实际版本为准）。
> 本文逐条给：根因 / 改动 / 是否需重编 `astrostudyboot.jar` / 验证 / **Windows 必做**。

---

## ① Windows issue #9「配置 OpenAI key 提示连接超时」— 内置 Java 走系统代理（治本）

**根因**：GUI 启动的桌面应用通常拿不到 `http_proxy` 环境变量；用户「本地代理正常」但内置 Java 仍直连 `api.openai.com:443` 超时。上一版 v2.2.1 只给 `HttpClientUtility.getHttpHost()` 加了读 `http(s).proxyHost` **系统属性**的回退——**但只加启动器 flag 仍无效**，深查发现两条出站链路都没真正用上代理：
- **流式 AI** 用 JDK `java.net.http.HttpClient`（`AIAnalysisProxyService.streamHttpClient`）。`HttpClient.newBuilder()…build()` **不调 `.proxy()` 时默认完全不走代理**，无视所有系统属性/flag。
- **非流式**（测试连接 / 拉模型）走 Apache 经 `getHttpHost()`，只读 `http(s).proxyHost` **系统属性**；而 `-Djava.net.useSystemProxies=true` **不会**写这俩属性，它只让 `ProxySelector.getDefault()` 去查 OS 代理。
- 全仓原本无任何 `ProxySelector` 使用。

**改动（3 处，缺一不可）**：
1. `Horosa-Web/astrostudysrv/boundless/src/main/java/boundless/net/http/HttpClientUtility.java` `getHttpHost()`：env / 系统属性都没给代理时，**回退 `ProxySelector.getDefault().select(new URI("https://api.openai.com"))`**，取首个 `Proxy.Type.HTTP` 的 host:port。无系统代理 → 返回 null、行为不变。（新增 import `java.net.ProxySelector` / `java.net.URI`）
2. `Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java` `streamHttpClient`：builder 加 `.proxy(ProxySelector.getDefault())`（新增 import `java.net.ProxySelector`）。无代理 → ProxySelector 返回 DIRECT、localhost 自动 bypass，行为不变。
3. 启动器 `Horosa-Web/start_horosa_local.sh`（`"${JAVA_BIN}" -jar "${JAR}"` 那行）加 JVM 参数 **`-Djava.net.useSystemProxies=true`**——让 `ProxySelector.getDefault()` 真正读 macOS/Windows 系统代理。localhost/127.0.0.1 默认 bypass，本地 :9999/:8899 不受影响。

**需重编 `astrostudyboot.jar`**（动了 boundless + astrostudy 两个模块）。

**验证（Mac）**：JDK17 `mvn` 重编 boundless→astrostudy→astrostudyboot 成功；`javap -c` 确认两 class 常量池含 `java/net/ProxySelector.getDefault`；`bash -n start_horosa_local.sh` 通过、本地栈带该 flag 正常起 :9999。真·代理 e2e 需真实系统代理（按惯例发版后实测）。

**Windows 必做**：
- **重编 `astrostudyboot.jar`**（同步 `HttpClientUtility.java` + `AIAnalysisProxyService.java`），重编后**重启 Java 进程**。
- **Windows 启动器加同一 JVM 参数 `-Djava.net.useSystemProxies=true`**：macOS 在 `start_horosa_local.sh` 加了；Windows 外壳不共享，需在 Electron `service-manager.js` spawn Java 处各自加。
- 验证：Windows 系统代理指向可达端口 → AI 配置「测试连接」OpenAI / 流式分析应通（原超时）；无代理时不变（回归）。

---

## ② 六壬 / 三式合一 发三传顺序修复（纯前端 JS，**无需重编 jar**）

**根因**：六壬引擎是**我们自己的前端 JS（不是 ken）**——`Horosa-Web/astrostudyui/src/components/liureng/ChuangChart.js` `getSangCuang()` 把 `isBaZhuang`(八专) 调度排在 `isYaoKe`(遥克) **之前**。按典籍 `0.基石/2.九法`：遥克是第 4 法、八专是第 9 法。导致「八专结构(干支同位) + 四课无近克但日干与他课上神有遥克」被误判为八专课（正确应为遥克的蒿矢/弹射课）。

**改动**：`getSangCuang` 顺序改为 伏吟/返吟 → 贼克(JinKe0/1) → **遥克(YaoKe0/1) → 八专(BaZhuang) → 别责(BieZe) → 昴星(MaoXing，兜底最后)**。加回归单测 `ChuangChart.test.js`（甲寅日八专结构 + 天盘=地盘+4 → 日干甲遥克戌土 → 期望「弹射课」）。**标准六壬（`lrzhan`）与三式合一（`sanshi/SanShiUnitedMain` 复用 `ChuangChart`）共用此引擎，改一处两边同修**。其余 9 法边规、课体→格局映射(19/19)、`LRConst` 常量、小局检测(62 局) 均核对正确，未改（避免回归）。

**验证**：`npx umi-test src/components/liureng/ChuangChart.test.js` → 3/3 绿。
**Windows 必做**：重建前端（`npm run build` → `build:file`）。无需重编 jar。

---

## ③ 占星右栏 tab 下「空白块」（纯前端 CSS，**无需重编 jar**）

**根因**：`AstroChartMain` 右栏内容容器按固定 px 定高（`tabHeight = height − 100`，组件内部再减 ~78px），比实际 pane 矮约 **111px** → tab 下方留死白块；且内容多的 tab（相位等）被压在更小区域内滚动，后续内容被「挡住」。

**改动**：`Horosa-Web/astrostudyui/src/layouts/app.less` 加
`.horosa-content-tabs .ant-tabs-tabpane > * { height:100% !important; max-height:100% !important; }`——内容容器填满 pane。随视口高度自适应。**覆盖所有走 `.horosa-content-tabs` 的页面**：占星 / 紫微 / 印度盘 / 果老，以及复用 `AstroChartMain` 的 十三分盘 / 合盘 / 节气 / astro3d。其他技法（太乙/金口/苏占/占卦/三式/六壬/八字…）用 `content-holder { flex:1; overflow:auto }`，本就正确，未动。

**验证**：preview 占星 信息/相位/行星 tab 内容填满（scroll 685 / pane 693，死白块消失，相位 1237 内容用满高度滚动）；明暗双色。
**Windows 必做**：重建前端。无需重编 jar。

---

## ④ 风水页 UI 精修（纯前端 CSS，**无需重编 jar**）

**根因（用户反馈：选择栏/文字间隔/安全距离）**：左控制栏 tab（基础/纳气盘/标注/导出）贴左边框（距边 4px，与卡片 16px 错位）；canvas 工具栏水平 padding 仅 2px；字段/标签/卡片标题间距偏挤；quickbar gap 偏小。

**改动**：`app.less`（`:global` 风水块）——选择栏 tab 头加左右内边距(对齐卡片，4px→18px)、工作区 tab 内边距、`canvas-toolbar` padding `4 2 6`→`6 10 10`、`quickbar` gap 6→8 / padding 加大、`field`/`label`/`card-title` 间距 + `line-height`、卡片 padding 12→14。**只动结构/中性间距与排版，语义色（气位红/水位蓝）不动**（[[semantic-colors-intentional]]）。

**验证**：preview 风水页明暗双色，选择栏与卡片对齐、间距/安全距离改善、无破版。
**Windows 必做**：重建前端。无需重编 jar。

---

## ⑤ 全页「快捷功能」dock 列网格自适应（纯前端 CSS，**无需重编 jar**）

**根因**：基础规则 `.horosa-bottom-quick-actions` 写死 `grid-template-columns: repeat(8, minmax(78px,1fr))`；但多数技法（太乙 6~9 动态 / 六壬 / 镜诀 / 金口 / 占卦…）都用这条基础规则，动作数 ≠8 时右侧留空列、>8 时第 9 个被裁。

**改动**：`app.less` 基础规则改 `grid-auto-flow: column; grid-auto-columns: minmax(78px,1fr)`——按实际动作数填满整行；8 个时与原 `repeat(8)` 等价（占星/占卦不变），少于 8 个填满无空列，兼容太乙条件式动态动作数。`aux`(repeat 5) / `guolao`(repeat 7) 各自有固定列覆盖且与其数匹配，未动。

**验证**：preview 太乙底部 dock 填满（rightGap=0）；占星 8 项布局不变。
**Windows 必做**：重建前端。无需重编 jar。

---

## 汇总 · Windows 端同步动作

| 动作 | 因为 |
| :-- | :-- |
| **重编 `astrostudyboot.jar`** + 重启 Java | 仅 ①（boundless `HttpClientUtility` + astrostudy `AIAnalysisProxyService`）|
| **Windows 启动器加 `-Djava.net.useSystemProxies=true`** | ① 启动器侧（Windows 外壳 `service-manager.js`，不与 macOS `start_horosa_local.sh` 共享）|
| **重建前端**（`npm run build` → `build:file`，顺序勿并行）| ②（`ChuangChart.js`）③④⑤（`app.less`）合并到一次重建即可 |

文件清单见上；macOS 仓 commit `ffd0312` @ 分支 `feature/round-tasks-1-5`。本轮纯前端的 ②③④⑤ + 后端的 ① 都在此一并交接。
