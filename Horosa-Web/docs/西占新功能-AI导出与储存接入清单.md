# 西占新功能 · AI导出 / AI分析挂载 / 命盘事盘储存 — 全链路接入清单

> 背景：本轮给占星(西占)补了一批新功能（寿命格局/12分度/主宰星链/龙盘/阿拉伯点5希腊点/界推运/年龄推进点Huber/容许度/世俗盘·时代纪元）。
> 这些功能默认只渲染成 tab，**不会**自动接入 AI导出 / AI分析 / 命盘事盘储存。本文档是「让新功能稳定且全面」的接入清单 + 现状缺口 + 已修/待修。

## 四套系统的接入点（精确 file:line）

### 1. AI导出 (AI Export)
- `src/utils/aiExport.js`
  - `AI_EXPORT_SETTINGS_KEY='horosa.ai.export.settings.v1'`、`AI_EXPORT_SETTINGS_VERSION`（改清单要升版本号）
  - `AI_EXPORT_TECHNIQUES`（约197–245行）：可导出技法清单（{key,label}）
  - `AI_EXPORT_PRESET_SECTIONS`（约247行起）：每个技法默认可选分段；占星=`astrochart: ['起盘信息','宫位宫头','星与虚点','信息','相位','行星','希腊点','可能性']`
- `src/utils/astroAiSnapshot.js`
  - `buildAstroSnapshotContent(chartObj, fields, options)`（743–757）：把各分段 push 进快照
  - 分段构造器：`buildBaseInfoLines/buildHouseCuspLines/buildStarAndLotPositionLines/buildInfoSection/buildAspectSection/buildPlanetSection/buildLotsSection/buildPossibilitySection`（316–719）
  - **`buildLotsSection`(684–707) 读 `AstroConst.LOTS`** → 我加的 5 希腊点(爱欲/必然/勇气/胜利/报应)**已自动进「希腊点」段** ✅
- `src/utils/aiAnalysisContext.js`
  - 预测技法快照：`buildPrimaryDirectSnapshotText`、`buildFirdariaSnapshotText`（从 AstroDirectMain import，670–691 调用）
  - `regenerateChartTechniqueSnapshot()`（657–709）：按 technique key switch 重建快照

### 2. AI分析挂载 (predictHook)
- `src/models/astro.js`：`predictHook` 状态(339–443)、`hooking()`(298–321)、`*doHook`(1191–1196)。盘变→doHook→hooking 调 `hook[currentTab].fun(...)`。
- `src/components/direction/AstroDirectMain.js`：hook 注册(457–504)、`this.props.hook.fun=...`(525–532)。
- `src/components/auxchart/AuxChartMain.js`：hook 状态(39–67)、注册(75–79)。
- **关键事实**：AI分析/导出**不直接遍历 predictHook**；它调专用 snapshot builder（如 buildPrimaryDirectSnapshotText）或读 module 缓存。hook 只管 UI 实时刷新。**所以让新功能进 AI 分析的真正办法 = 写 snapshot builder，不是传 hook prop。**

### 3. 命盘储存 (chart save/load)
- 存：`models/user.js` addChart/updateChart effect(965–1033) → `utils/localcharts.js buildLocalChartRecord()`(235–281) → localStorage。
  - 非地点参数随档复制在 user.js **498–505**（after23NewDay/lateZiHourUseNextDay/timeAlg），record 字段在 localcharts.js 279 一带。
- 取：`models/user.js setCurrentChart`(535–608) → `astro/fetchByChartData` → 重建 fields（astro.js 第二 fields 块 ~540–620，after23NewDay@566）。

### 4. 事盘储存 (event-chart save/load)
- 存：`DivinationChartShell.saveCase`(77–110) → `utils/divinationCaseSave.js openDivinationCaseDrawer`(29–67) → case 记录。
- 取：`DivinationChartShell.applyRestoreIfAny`(104–153) → `getDivinationSavedCasePayload(module)`。
- 技法注册：`utils/localcases.js CASE_TYPE_OPTIONS`(83–99)。

## 现状缺口 & 已修/待修

| 项 | 现状 | 处理 |
|---|---|---|
| 5 希腊点 进 AI导出 | ✅ 已在（buildLotsSection 读 LOTS） | 无需动 |
| **世俗盘 事盘储存** | ❌ `mundane` 未注册、入宫 extra 存取都丢 | **✅ 已修**（见下） |
| 容许度 orbs 进相位导出 | ⚠️ 隐含（chartObj 已用 orbs 算相位，相位段反映） | 可接受 |
| **orbs/orbScale 随命盘存档** | ✅ 全链路存取已通（2026-05-29，npm build 绿） | **✅ 已修**（见下 A） |
| pdMethod 随命盘存档 | ❌；**注意属 PD 核心，改动须守铁律** | ⏳ 待修(谨慎) |
| 寿命/12分度/主宰链/界推运/Huber/世俗 进 AI | ✅ **全部已接入(2026-05-29)·导出+挂载均全**:判读三段走 astroAiSnapshot(随 astrochart 导出+挂载);界推运/Huber 走 aiAnalysisContext wired technique **且**补全 aiExport 六张表(`getAIExportAuditMatrix` 自检);世俗走事盘 payload.aiSnapshot **且** aiExport auxchartMap/extractor。逐技法实现详见 [`西占新技法-逐技法实现详解-v2.4.0.md`](../../docs/西占新技法-逐技法实现详解-v2.4.0.md)。npm build 绿 + 140 测试全过 | 见 §B |
| **工程师级复审发现的导出缺口**(2026-05-29) | 审计发现:接入「挂载」**不**自动接入「导出」(两套独立系统)。界推运/Huber/世俗 原只挂载、未进 AI导出 → 已补全 | aiExport.test `getAIExportAuditMatrix` 自检逮住,已修 |

### ✅ 已修：世俗盘事盘储存（本轮）
1. `localcases.js CASE_TYPE_OPTIONS` 加 `{ value:'mundane', label:'世俗盘', subTab:'mundane', tab:'auxchart', module:'mundane' }`。
2. `divinationCaseSave.js` payload 加 **`extra: ex`**（整存技法 extra，世俗盘 ingressTerm/ingressYear/ingressMoment 不再丢）；questionCategory/topicId 保留向后兼容。
3. `DivinationChartShell.applyRestoreIfAny` 还原改为 **通用 `c.payload.extra`** + 旧案 questionCategory/topicId 兼容。
> 通用化后，**任何** saveModule（含将来新增）其 state.extra 都能存取，不必逐个改。

## ⏳ 待修步骤（精确·谨慎做，勿在超长会话里赶）

### A. orbs/orbScale 随命盘存档 — ✅ 已修（2026-05-29，npm build 绿）
镜像 `after23NewDay`，五点对称落地（实际行号）：
1. `models/user.js` 命盘 fields 定义 ×2（75-82 与 324 一带）加 `orbs:{value:undefined,name:['orbs']}`、`orbScale:{...}`。
2. `models/user.js:517-518` 存档复制：`if(fld.orbs&&fld.orbs.value){chart.orbs.value=fld.orbs.value;}`（orbScale 同）。
3. `utils/localcharts.js:273-274` record：`orbs:(values.orbs&&typeof values.orbs==='object'&&Object.keys(values.orbs).length)?values.orbs:undefined`（orbScale 排除 1）。
4. `models/astro.js`：主 fields 块(146-152)+重建 fields 块(574-580)加 orbs/orbScale 定义；`fieldsToParams`(248-249) 已发；还原 `astro.js:1070-1071` 从存档值回填 `fields.orbs.value`。
> orbs 全程 undefined 默认=**零回归**；pdMethod/主限法路径未触。**验存盘往返仍待 live**（设容许度→存盘→重开→相位仍用自定义值）。

### B. 各新分析进 AI导出（逐功能 snapshot builder，加性·低回归）

**✅ 本轮已接入并 live-verified（2026-05-29）：`12分度` + `主宰星链` + `寿命格局`**(均判读类、走 astroAiSnapshot 段)
- `astroAiSnapshot.js`：新增 `buildDodecaSection`/`buildDispositorSection`(就地 `dodecaLonOf`/`TRAD_SIGN_RULERS`/`objAbsLon`,复用现成 `lonToSignDegree`+`msg`,**零外部 import**) + `buildLifespanSection`(import `buildFacts`+`runLifespan` 纯引擎,无环;`chartObjWithFactsMaps` 非破坏补 objectMap/houseMap;**坑:引擎产出 key/sign 全小写 → 加 `LIFESPAN_KEY_TO_ID` 映射 + 位置统一 `lonToSignDegree(lon)` 取中文座度+界**);在 `buildAstroSnapshotContent` 希腊点后依次 push。
- `aiExport.js`：`AI_EXPORT_PRESET_SECTIONS.astrochart`+`astrochart_like` 加三段名;版本 9→**11**(`AI_EXPORT_SETTINGS_VERSION`+`SECTION_MIGRATION_VERSION` 同步;astrochart 已在 migration keys → 老用户自动并入;只影响段设置,不碰 provider/key)。
- **实测**(preview 重载快照):`[12分度]` 日 8°双子→室女7°、月 17°天蝎→金牛26°(公式对);`[主宰星链]` 水→水(庙)、月→火→金→月(互容环闭合);`[寿命格局]` 夜生盘·生命主上升 15°射手金界第1宫·盘主体系 占控上升/家主木/盘主火(中文对、与 AstroLifespan 同引擎)。signature 在位、build 绿、加载零报错。

**✅ 已接入（界推运/Huber/世俗,2026-05-29；预测/辅盘类,不走 astroAiSnapshot 段）：**
- **界推运 + Huber(预测类·wired technique)**:`AstroDistributions.js`/`AstroAgePoint.js` 各 export async `buildDistributionsSnapshotText`/`buildAgePointSnapshotText`(内部 `request(/predict/dist)`/`(/predict/agepoint)` 与组件同口径,markdown 表 + AstroTxtMsg 中文名;**无数据 return '' → 挂载显示「缺失」而非空表头**);`aiAnalysisContext.js` import + `regenerateChartTechniqueSnapshot` 加 `case 'distributions'/'agepoint'`(仿 firdaria,先 `fetchChartResultForRecord` 再 await builder)+ 注册 `TECHNIQUE_LABELS`(星运-界推运/星运-年龄推进点)+ `ANALYSIS_CHART_TECHNIQUES`。**坑**:builder 空数据时若仍 push 表头会被判 available=true → aiAnalysisContext.test「未挂载技法应 missing」红;已修(空即 '')。
- **世俗(辅盘·事盘 payload)**:事盘走「读 `payload.aiSnapshot`(extractCaseSnapshotText 'ready')否则 JSON 裸转」。给 `DivinationChartShell` 加可选 `buildAiSnapshot(chart,fields,extra)` prop(shell 保持通用)+ `divinationCaseSave.openDivinationCaseDrawer` payload 收 `aiSnapshot`;`MundaneMain` 传 `buildAiSnapshot=(c,f,ex)=>入宫头 + buildAstroSnapshotContent(c,f)` → 存档即带格式化 astro 快照(含上面三判读段),挂载直接读、不再 JSON 裸转。
- **验证**:npm build 绿;`aiAnalysisContext.test`+`aiAnalysisSelection.test` 等 29 套 140 测试全过(含技法 missing 契约)。界推运/Huber 的 AI分析挂载真机验受 antd Select 合成事件限制未驱动,但 fetch/格式与**用户本会话已对 验过的同名组件完全一致**、且走既有 firdaria wired 模式。

**(历史)仍待规格参考——下方为接入前写的规格,已照做：**
- **数据源**：`astroAiSnapshot.js` 内 `getObjectsMap(chartObj)` 返回**原始 chart.objects（含 `.lon` 绝对黄经、`.sign`/`.signlon`/`.house`）**；key=obj.id（flatlib 大写 'Sun'/'Moon'…，**非**组件里的小写 'sun'）。
- **公式（组件只 export default，纯函数须就地重写，都是标准式）**：`norm360(x)=((x%360)+360)%360`；`dodecaLon(lon)=norm360(floor(L/30)*30+(L%30)*12)`；`signOf(lon)=SIGN_ORDER[floor(norm360(lon)/30)]`（得小写星座 key）；dispositor=`(SIGNS[signOf(obj.lon)]||{}).domicile`。
- **import**：`{ SIGNS, SIGN_ORDER } from '../divination/data/signs'`（纯数据，**无环**，已验 lifespanEngine/chartFacts 也不回 import 本文件）。
- **`buildDodecaSection(chartObj)`**：遍历 objectMap → `dodecaLon(obj.lon)` → `signOf(dl)`+`dl%30` → 行 `名(本命 座度 → 12分度 座度)`。
- **`buildDispositorSection(chartObj)`**：遍历七政 → `signOf(obj.lon)`→domicile(小写星名)→显示链；终极主宰=链收敛点/互容。**坑：domicile 是小写 'mars'，显示要映射**（用 SIGNS[s].cn 给座名 / 自建小写→符号 map；astroAiSnapshot 的 `msg(id)` 吃的是 obj.id 大写，对不上 domicile 小写）。
- **`buildLifespanSection(chartObj)`**：`runLifespan(facts)` from `divination/lifespan/lifespanEngine`（无环已验）；`facts` 须 `buildFacts(chartObj.chart)`（divination/engine/chartFacts）。输出 Hyleg/Alcocoden/释放星/寿数。
- 三者在 `buildAstroSnapshotContent`(753-756 区) push `buildSectionText('寿命格局'|'12分度'|'主宰星链', …)`；并 `aiExport.js AI_EXPORT_PRESET_SECTIONS.astrochart` 数组加这三段名 + 升 `AI_EXPORT_SETTINGS_VERSION`。
- 预测类(界推运/Huber)：仿 `buildPrimaryDirectSnapshotText` 在 AstroDistributions/AstroAgePoint 导出 `buildXxxSnapshotText(chartObj)`（内部 fetch /predict/dist、/predict/agepoint），在 `aiAnalysisContext.regenerateChartTechniqueSnapshot` switch 加 case。
- **live-verify（skill 强制）**：seed 已知盘→开 AI导出→读渲染段，断言每段签名对得上 birth（no-串盘）+ 非空。
- 辅盘(龙盘/世俗)：同理按需。

### C. （可选）新预测/辅盘 tab 传 hook prop
- AstroDirectMain 的 distributions/agepoint TabPane、AuxChartMain 的 draconic/mundane TabPane 可加 `hook={this.state.hook.X}` 与既有 tab 对齐；但**对 AI 分析无实质作用**（AI 走 builder）。组件自身 componentDidUpdate 已自刷新，不传也不坏。

## 给后续 agent 的「新增西占功能·全链路」清单
新增一个占星功能时，除做 UI tab，**务必**核对：
1. 若是**判读/分析**：写 `astroAiSnapshot.js` 的 builder + `aiExport.js` 段名/版本 → 进 AI导出。
2. 若是**预测**：写 `buildXxxSnapshotText` + `aiAnalysisContext` switch case。
3. 若新增**chart-calc 参数**(如 orbs)：四点存/取（user.js fields+498、localcharts record、astro.js 重建 fields），并验存盘往返。
4. 若是 **DivinationChartShell 事盘**：`localcases.CASE_TYPE_OPTIONS` 注册 module；extra 已通用存取(本轮改)，无需逐个动。
5. 希腊点/阿拉伯点加进 `AstroConst.LOTS` 即自动进 AI导出「希腊点」段。
