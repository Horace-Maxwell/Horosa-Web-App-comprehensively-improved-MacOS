# task⑥ — 辅盘新增「卜卦盘 / 择日盘」（西洋断事规则库 + 事件盘存盘）技术文档

> **状态**：macOS 端已完成 + 验证，本地提交于分支 `feature/round-tasks-1-5`（commit `d2ef43b`，52 文件 +4191/−28），**尚未发布**。与本轮 **①–⑤ 修复（commit `ffd0312`）合并后一起发布**（目标版本约 **v2.2.2**，以合并发布的实际版本为准）。
>
> **性质：纯前端（`astrostudyui/src`）零后端。** ⚠️ **不动 Java、不动 Python、不重编 `astrostudyboot.jar`、不重打 runtime**——这是本批里 Windows 同步最简单的一项：只搬前端 `src/` + `npm run build && npm run build:file`。
>
> 本文逐条给：做了什么 / 文件落点 / 为什么零后端 / 验证 / **Windows 必做**。

---

## 0. 总览

在「辅盘」大 tab（`key=auxchart`）下、骰子之后，新增两个子盘：

- **卜卦盘（horary）**：西洋卜卦（Sibly 71 + Dorotheus 43 + Sahl 全部 + Hephaistion 补充 + 盗窃失物 11 步）。
- **择日盘（election）**：西洋择日（择日清单 §1–§10：月亮/命主/角宫/用事专属…）。

两盘**复用占星页的三栏 UI**（左设置+调时 / 中圆盘 `AstroChart` / 右判断 tab），各自**自包含、时间独立**于主占星盘（自己的 `fetchChart` + 本地 `fields`，默认「此刻起卦」）。

落地结构（全部新增在 `Horosa-Web/astrostudyui/src/`）：

| 目录 | 文件数 | 内容 |
|---|---|---|
| `divination/data/` | 17 | planets / signs / dignities（埃及界·多禄阿三分性·迦勒底十度）/ aspects / lots / houseMeanings（含转宫）/ bodyParts / shipParts / directions / fixedStars / midpoints / topicMaster（27 题目）/ castMoments / glossary / decanImages / planetaryHours / dorotheusDegrees |
| `divination/engine/` | 9 | utils / chartFacts（后端结果归一化）/ conditions / moon / aspectsEngine / reception / perfection / radicality / chartRequest |
| `divination/horary/` | 6 | significators / timing / describe / theftModule / horaryEngine / horarySnapshot |
| `divination/election/` | 8 | scoring / hardFlags / modules / rulePacks / workflow / natalIntegration / electionEngine / electionSnapshot |
| `components/divination/` | 1 | DivinationChartShell（两盘共用三栏壳） |
| `components/horary/` | 2 | HoraryMain（壳包装）/ HoraryJudgment（右栏 5 tab） |
| `components/election/` | 2 | ElectionMain（壳包装 + 扫描择优）/ ElectionJudgment（右栏 5 tab） |

改动的既有文件：`components/auxchart/AuxChartMain.js`、`pages/index.js`、`utils/aiExport.js`、`utils/localcases.js`、`layouts/app.less`、新增 `utils/divinationCaseSave.js`。

---

## 1. 为什么零后端（关键，决定 Windows 同步面）

引擎直接消费现成 `/chart` 端点（`astropy` 的 flatlib `perchart.py`）已经产出的字段：尊贵（庙旺陷弱/界/十度/三分性）、相位（含**入相/出相**）、接纳、互容、映点、被夹、月空亡、日主/时主、逆行。前端只在这些之上**纯 JS 计算**少量派生量：燃烧/日下/居日心、角宫归属、月相、托勒密五相位过滤。

⇒ **没有新后端路由、没有 Java/Python 改动**。Windows 同步只需前端源码 + 重建前端包。

---

## 2. 卜卦引擎（`divination/horary/horaryEngine.js` 编排）

`runHorary(chartResult, category)` 跑：根本性 → 征象星指派 → 完成法 → 月亮报告 → 单星状态 → Sibly 六问 → 应期方位 → 加权裁决 → 描述（+ 盗窃类专属）。右栏 `HoraryJudgment` 5 tab：**裁决 / 征象 / 完成 / 时空 / 描述**。

- **根因性 radicality**：是否适合判断（上升早晚度、月空、土星落一/七宫、上升主落 2/8 宫…）——只给警告不阻断。
- **完成法 perfection**：① 入相位（直接）② 光线传递（中间星先离 A 再入 B）③ 光线汇集（两星共入较重星）④ 落位；破坏：阻碍/挫败/折返/燃烧/出相/无接纳的刑冲。
- **本轮重点（用户「所有征象都要摆出来让用户判断」）**：
  - 完成法的**光线传递明确写出谁在谁之间传递**：`perfection.js` 输出 `光线传递：<T> 刚从 <A> 出相位、正入相位 <B> → 由 <T> 把 <A> 的光线带给 <B>`，并置 `translatorFrom/translatorTo`。
  - 完成 tab 新增 **「月亮的故事（过去→未来）」**（`buildMoonStory`：月的 separating 已过 + applying 将会，逐条命名 + 容许度）。
  - 完成 tab 新增 **「相位全览（七政之间）」**（`buildAllAspects`：七政两两去重，**仅托勒密五相位** 0/60/90/120/180，标入相/出相 + 容许度 + 吉凶色，先正相位后按容许度排序）。
  - 三分法则等术语在面板里加**白话解释**（如「把命主/月亮/事项星当三大征象，数几颗安全」）。
  - `ASPECT_CN = {0:合相,60:六合,90:四分(刑),120:三合,180:对分(冲)}` 统一中文相位名（引擎、snapshot、择日应期共用本地常量，零跨模块耦合）。
- **Sibly 六问**：能否成事 / 好坏 / 真假 / 何处…（`buildQueries`）。
- **描述 describe.js**：84 条 planet-in-sign 外貌性情逐字条文 + 行星性情；盗窃/疾病/死亡按类别叠加。
- **盗窃 theftModule.js**：失主=命主+月亮、盗贼=7宫主、赃物=2宫主、藏匿=4宫 的 11 步。

裁决 `buildVerdict`：完成法(权重3)/三分法则(2)/月亮 findings/关键征象星状态 加权 → leaning(yes/no/even)，**只呈现证据与倾向，从不下命定结论**。

---

## 3. 择日引擎（`divination/election/electionEngine.js` 编排）

`runElection(chartResult, topicId)` → 右栏 `ElectionJudgment` 5 tab：**总评 / 红线 / 分项 / 应期 / 建议**。

- **13 模块 modules.js**：月亮（空亡/燃烧之路/凶星相位/快慢/增减光）、命主星、上升度、用事征象星、角宫吉凶、凶星落角、第八宫、逆行、月相…
- **红线 hardFlags.js**：硬伤分级 critical→**严重·红线** / high→**较重** / medium→**中等** / low→**轻微**（中文分级 + 图例，替代原 high/medium/low 生硬英文）。
- **评分 scoring.js**：0–100 + 等级（极佳/不错/中等/欠佳/不宜含红线）。
- **27 用事专属 rulePacks.js**：`evaluateTopicPack(topicId, facts)` 按婚/市/迁/动土/手术…各自宜忌。
- **扫描择优 workflow.js**：`generateCandidates`（本日逐时 6–22 点 / 未来 14 日同时刻）+ `rankResults`（消去法排名，先严重后较重）；`ElectionMain` 左栏「本日逐时择优 / 未来14日」→ Modal 排名 →「用此刻」跳转。
- **应期 tab**：月亮入相位（**本轮改为中文相位名 + 仅托勒密五相位**）。
- 本命合参 `natalIntegration.js` **保留模块文件**，但右栏的「本命合参」渲染块已删（合参按用户要求改在**中间栏叠盘**做，属后续项）。

---

## 4. AI 四环节同步（`utils/aiExport.js`）

| 环节 | 接法 |
|---|---|
| 导出技法 | `AI_EXPORT_TECHNIQUES` 加 `{horary:'卜卦盘'}`、`{election:'择日盘'}` |
| 导出设置 | `AI_EXPORT_PRESET_SECTIONS.horary = [起卦信息,根本性,征象星指派,完成分析,**月亮的故事,相位全览**,裁决,应期方位,描述]`；`.election = [起盘信息,总评,红线,分项,用事专属,应期,建议]`。⚠️ `applyUserSectionFilter` 加 `horary` 分支 `picked.push('月亮的故事','相位全览')`——防旧设置数组过滤掉新增两段（与 jinkou/liureng/qimen 同款保留法） |
| 分析挂载 | `getExtractorKindByExportKey` → `module:horary`/`module:election`；`getStructuredSnapshotKeysByExportKey` → `['horary']`/`['election']` |
| 快照 | `horary/horarySnapshot.js` `buildHorarySnapshot`（含 [月亮的故事] [相位全览] 段）、`election/electionSnapshot.js` `buildElectionSnapshot` → 生命周期 `saveModuleAISnapshot('horary'/'election', text)` |

---

## 5. 事件盘存盘（双向：存 → 列表 → 重新打开还原）

复用占星盘**既有事件盘管道**（`astro/openDrawer` caseadd → `upsertLocalCase` → `user.currentCase`），与六壬 `kentangCaseSave` 同款，零后端。

- **新增 `utils/divinationCaseSave.js`**：
  - `openDivinationCaseDrawer({dispatch, fields, module, extra})`：组 record（caseType=module、divTime、zone/经纬/pos、payload={module,version,savedAt,settings(黄道/宫制/守护),questionCategory|topicId}、sourceModule）→ dispatch caseadd。
  - `getDivinationSavedCasePayload(module)`：从 `getStore().user.currentCase` 拉本技法案例（校验 sourceModule/caseType/payloadModule），返回 payload + `caseVersion` + 时间地点。
- **`utils/localcases.js`**：`CASE_TYPE_OPTIONS` 加 `{value:'horary',label:'卜卦',subTab:'horary',tab:'auxchart',module:'horary'}` 与 election 同款；`CASE_TYPE_ALIASES` 加 卜卦/卜卦盘/择日/择日盘 中文别名。**必须加**——否则 `getCaseTypeMeta` 对未知 caseType 默认落 `tab:'cnyibu'`，applyCase 会把卜卦案例错误路由到「华人易卜」大 tab。
- **`components/divination/DivinationChartShell.js`**：
  - 左栏「术语速查」旁加 **「存为事件盘」按钮**（仅当收到 `dispatch`+`saveModule` 时显示）→ `saveCase()` 调 `openDivinationCaseDrawer`。
  - **重开还原 `applyRestoreIfAny()`**（`componentDidMount`+`componentDidUpdate` 调）：拉 `getDivinationSavedCasePayload(saveModule)`，**caseVersion 变了才应用**（六壬式拉取，非 push 灌；防手动调时间后被反复覆盖）；解析 divTime 字符串→`DateTime`（同 `user/applyCase` 的 `tm.parse('YYYY-MM-DD HH:mm:ss')`）→ `patchFields` 时间/地点/设置 + `setExtra` 类别。
  - 加 **`_mounted` 守卫**（`componentWillUnmount` 置 false，`refetch` 异步 setState 前检查），消除切盘时的 React unmounted-setState 告警。
- **`components/{horary/HoraryMain,election/ElectionMain}.js`**：给 Shell 透传 `dispatch={this.props.dispatch}`（AuxChartMain 已下发）+ `saveModule="horary"|"election"`。
- **`components/auxchart/AuxChartMain.js`**：加 `componentDidUpdate` 响应外部 `props.currentSubTab` 变化切到 horary/election 子盘（照 `CnYiBuMain` 范式）。**坑**：原 `findTab()` 只读 `state.currentTab`、不读 `props.currentSubTab`——没有这个 didUpdate，从事件盘列表 `applyCase` 切不到对应子盘。
- **`pages/index.js`**：`auxChartTabs` 归一化列表由 `['germanytech','hellenastro','locastro','otherbu']` 补全为含 `harmonic/horary/election`（修一个**既有**漏项：调波盘也曾受影响）。

`user/applyCase`（`models/user.js`）**未改、现成可用**——它按 `getCaseTypeMeta` 查 tab/subTab、灌时间地点、切大 tab + fetchByFields；卜卦/择日靠 Shell 的拉取式还原接住。

---

## 6. UI / 布局

- 三栏 CSS Grid（左设置 / 中盘 ≥620 / 右判断），`horosa-astro-no-bottom-dock` 消底部空隙。
- 右栏全面卡片化（`layouts/app.less` 末尾 `:global{ .horosa-divi-* }`）：证词独立成行、`align-self:start` 不留空卡、红线中文分级图例。**不同 signification 各占一行**。
- 语义色（吉凶/五行/天将）不动（[[semantic-colors-intentional]]）。

---

## 7. 验证（macOS 已过）

- **单元测试**：`npx umi-test src/utils/__tests__/localStorageManagement.test.js` → **16/16**（含「每个新增 case 类型可寻址」「每族案例路由回正确工作区」两条遍历测试，覆盖新加的 horary/election）；`aiAnalysisSelection.test.js` → **3/3**。
- **存盘端到端**：卜卦盘「存为事件盘」→「添加起课」抽屉类型显示「卜卦」→ 提交 → `localStorage horosa.localCases.v1` 写入完整 record（caseType/divTime/payload）。
- **重开端到端**：`user/applyCase` 一条特征案例（2020-01-01 08:00 / 婚姻类 / 验证地点）→ 自动回卜卦盘且时间/地点/问题类别/黄道全部正确还原。
- **console**：无新增运行时错误（`_mounted` 守卫消除了 Shell 的 unmounted 告警）；余下 antd `TabPane deprecated`、dva `unmodel`、`CaseData` unmounted 均为全 App 既有良性告警。

---

## 8. Windows 必做（简单——纯前端）

1. **同步前端源码**到 Windows 仓库对应路径（纯 JS/LESS，无平台分支）：
   - 新增目录：`src/divination/`（data/engine/horary/election 全部）、`src/components/divination/`、`src/components/horary/`、`src/components/election/`。
   - 新增文件：`src/utils/divinationCaseSave.js`。
   - 改动文件：`src/components/auxchart/AuxChartMain.js`、`src/pages/index.js`、`src/utils/aiExport.js`、`src/utils/localcases.js`、`src/layouts/app.less`。
2. **重建前端**：`npm run build` 然后 `npm run build:file`（**顺序执行，勿并行**，两者都写 `src/.umi-production`）。
3. ⏸ **不需重编 `astrostudyboot.jar`**（没动 Java）。
4. ⏸ **不需重打 Python runtime**（没动 `astropy`/`vendor`）。
5. 自检：辅盘底部 dock 出现「卜卦盘 / 择日盘」；各自起盘出完整圆盘 + 右栏 5 tab；「存为事件盘」→ 事件盘列表能看到「卜卦 / 择日」类型 → 列表「应用」能切回对应子盘并还原时间/地点/类别；AI 导出选「卜卦盘 / 择日盘」分段齐全（含月亮的故事 / 相位全览）。

> 后续项（不在本批）：与主命盘合参的**中间栏叠盘（biwheel）**——属较大改动（动共享 `<AstroChart>`），先出方案再做。
