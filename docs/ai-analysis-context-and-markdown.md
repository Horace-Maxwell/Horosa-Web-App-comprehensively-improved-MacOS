# AI 分析：上下文挂载修复、全命盘技法接入、面板/布局重做与 Markdown 渲染

> 日期：2026-05-25 · 范围：`Horosa-Web/astrostudyui` 的「AI 分析」功能 + 新增前端依赖 + 本地一键启动器/kentang 引擎修复 + 仓库治理（harness/skill/docs）
> 目的：让其他 agent 能完整 catch up 本轮改动、按既定流程验收，并据此执行 GitHub 发布。

---

## 0. TL;DR

- **修复了「挂错盘」严重 bug**：选中某个命盘后勾选八字/紫微/印度占星等技法时，右侧「本轮挂载上下文」原本挂载的是「主程序里上次看过的那张盘」，而不是当前选中的盘。
- **命盘侧**：现在每个勾选的技法都按**该盘的出生数据**实时无头复算并挂载。已接入 9 个：星盘、印度占星、八字、紫微、法达、主限法、七政四余、宿占、量化盘。
- **事盘（占卜盘）侧**：只挂载它**起盘时保存的那个技法**的数据，**绝不按时间重算**；勾选其它技法显示「缺失」。
- **硬不变量**：出生/起盘签名不匹配的快照一律拒绝，任何情况下都不会挂错盘。
- **面板重做**：折叠面板 + 完整内容 + 状态标签 + 出生签名；新加技法面板自动展开。
- **布局**：系统提示移到右列上方；顶部按钮行移到底部发送键左侧。
- **历史页**：删除右上两个空白输入框。
- **Markdown 渲染**：AI 回复用 `marked + DOMPurify` 渲染（标题/加粗/列表/表格/代码/引用），不再是一团 `**` 乱码。
- **本地一键启动 + kentang 引擎修复**：修复 `start_horosa_local.sh` 选错 Python（缺 `cn2an`）、`vendor/` 不在 `PYTHONPATH`，以及前端 kentang 端口解析过时——使本地 奇门/太乙/三式合一/术数（`kinqimen` 等）正常起盘（详见 §7）。
- **治理**：新增 harness 配置（权限 + 嵌入式 Python env）、`horosa-dev` 技能、本文档。

全部经 `npm run build`（exit 0）+ 本地全栈 + 浏览器预览端到端验收通过。

---

## 1. 背景与问题

用户在「AI 分析」选中命盘「李」并勾选八字/紫微时，挂载的八字显示当天日期（2026-05-25）、紫微显示当前默认丙年——都不是李的出生数据。另外提出：面板信息看不全/滑不动、系统提示占位浪费、顶部按钮行占位、历史页两个空白框无用、AI 输出的 Markdown 无法正常渲染。

## 2. 根因（已确认）

文件：`Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js`

1. `buildTechniqueContext()` 中**只有西洋星盘**（`astrochart`/`astrochart_like`）走实时按盘重算；其余技法只查 `payload` 快照与**全局模块缓存** `loadModuleAISnapshot('bazi')`。原重算分支被 `if(source.sourceType === 'case')` 限定，**命盘不重算**。
2. 模块缓存 `horosa.ai.snapshot.module.v1.<module>`（`utils/moduleAiSnapshot.js`）是**全局单条**、每次主程序算盘即被覆盖、key 不含出生时间——本质是「上次算过的那张盘」。
3. 兜底应由 `isSnapshotMetaCompatible()` 把关，但 `pickSnapshotCandidate()` **只把 `compatible` 当排序权重、不做过滤**，不匹配的缓存照样被挂载。

UI 侧：聊天气泡用 `<div>{item.content}</div>` 直出纯文本，从不解析 Markdown。

---

## 3. 改动详解（按区块）

### A. 上下文挂载正确性（核心）

文件：`src/utils/aiAnalysisContext.js`

- **A1 硬性兼容过滤**：`pickSnapshotCandidate()` 改为先剔除 `compatible === false` 的候选：
  ```js
  const valid = (candidates || []).filter((item)=>item && item.content && item.compatible !== false);
  ```
  `getTechniqueSnapshotFromPayload` / `getTechniqueSnapshotFromCache` 已用 `isSnapshotMetaCompatible` 计算 `compatible`（源签名为空时为 true，不误伤）。仅此一处即根除「挂错盘」。**改候选选择逻辑时务必保留此过滤。**

- **命盘技法无头重算注册表**：
  - `fetchChartResultForRecord(record, {includePrimaryDirection})`：用 `buildFieldObject` + `fieldParams` 调 `fetchChart`（`/chart`，`predictive` 已开）取西洋盘原始结果（含 `predictives.firdaria`、可选 `predictives.primaryDirection`）。
  - `buildChartBaziParams(record)` / `buildChartZiweiParams(record)`：形状对齐各组件 `genParams`（date `YYYY-MM-DD` / time `HH:mm:ss`）。
  - `regenerateChartTechniqueSnapshot(record, key)`：按 key 分派（见技法表），`try/catch` 返回 `''`，失败安全降级为「缺失」。

- **`buildTechniqueContext()` 按 `sourceType` 分流**：
  - **chart**：`payload` 命中优先 → 兼容缓存（A1 已过滤）→ 仍无则 `regenerateChartTechniqueSnapshot`，生成后 `saveGeneratedTechniqueSnapshot`（带 `buildSnapshotMetaFromRecord` 出生签名）。
  - **case**：见 F 区。

### F. 事盘（占卜盘）：只用已存技法，绝不按时间重算

文件：`src/utils/aiAnalysisContext.js`

- `buildTechniqueContext()` 的 case 分支：只用本案例 `payload`（`getTechniqueSnapshotFromPayload` + 从 payload 重建文本的 `generateCaseTechniqueSnapshot`）；**不调用** `regenerateCaseTechniqueSnapshot`（按时间重新起盘），**也不读全局模块缓存**。勾选的技法不在 payload 中 → 返回空 → 显示「缺失」。
- `buildCaseContext()`：同样移除了 `regenerateCaseTechniqueSnapshot` 兜底，仅保留 `payload` + `generateCaseTechniqueSnapshot`。
- 设计理由：事盘绑定起盘那一刻的卦/课（掷币、骰子、手动起卦不可由时间重现）。命盘按时间重算（A）与事盘禁止重算（F）是**两条相反规则**，互不影响。
- 注：`regenerateCaseTechniqueSnapshot` 及其 6 个 helper（`requestLiurengGods`/`regenerate{Liureng,Jinkou,Qimen,Taiyi,SanshiUnified}Snapshot`）现已无人调用，属保留的死代码（无 ESLint 门禁、不影响构建），可后续清理。

### 已接入的命盘技法

| 技法 key | 标签 | 取数 | 复用 builder（已 export） | 设置 |
| --- | --- | --- | --- | --- |
| `astrochart` | 星盘 | `/chart` | `buildChartContext`（原有） | — |
| `indiachart` | 印度占星 | Python `/india/chart` | `buildIndiaSnapshotForFields`（`components/astro/IndiaChart.js`） | D1 命盘 |
| `bazi` | 八字 | 本地算 + `/bazi/direct` | `buildBaziSnapshotForParams`（`components/cntradition/BaZi.js`） | — |
| `ziwei` | 紫微斗数 | `/ziwei/birth` | `buildZiweiSnapshotForParams`（`components/ziwei/ZiWeiMain.js`） | — |
| `firdaria` | 星运-法达星限 | `/chart`（predictive） | `buildFirdariaSnapshotText`（`components/direction/AstroDirectMain.js`） | — |
| `primarydirect` | 星运-主/界限法 | `/chart`（`includePrimaryDirection`） | `buildPrimaryDirectSnapshotText`（同上） | 默认 Alchabitius 弧 / Ptolemy 时钥 / 含界限 |
| `guolao` | 七政四余 | `/chart`（七政参数） | `buildGuolaoSnapshotForFields`（`components/guolao/GuoLaoChartMain.js`） | **沿用 `getStoredGuolao*` 已保存设置** |
| `suzhan` | 宿占 | `/chart`（标准盘的二十八宿） | `buildSuzhanSnapshotText`（`components/suzhan/SuZhanMain.js`） | 常用默认 |
| `germany` | 量化盘 | `/chart` + `/germany/midpoint` | `buildGermanySnapshotForFields`（`components/germany/AstroMidpoint.js`） | — |

`planetDisplay = null` ⇒ 显示全部传统星曜（builder 内 `isTraditionPlanet` 兜底）。

**未接入（仅安全降级，永不挂错盘）**：profection / solararc / solarreturn / lunarreturn / givenyear（需目标时刻语义）、jieqi（节气盘，需 N 次取数 + 列表参数）、primarydirchart / zodialrelease / decennials / cntradition / fengshui（仅 DOM 抓取或 iframe，无可复用 builder）。
**本质不可复算**：`otherbu`（骰子随机）、`relative`（合盘需两张盘）。

### 各组件新增的导出（A3）

- `components/cntradition/BaZi.js` → `export async function buildBaziSnapshotForParams(params)`（内部走 `fetchBaziDirectCached` + `normalizeBaziResult` + `buildBaziSnapshotText`）。
- `components/ziwei/ZiWeiMain.js` → `export async function buildZiweiSnapshotForParams(params)`（`/ziwei/birth` + `buildZiWeiSnapshotText`）。
- `components/astro/IndiaChart.js` → `export async function buildIndiaSnapshotForFields(fields, chartnum)`（复用已导出的 `fieldsToParams`/`requestIndiaChartData`）。
- `components/direction/AstroDirectMain.js` → 导出新增 `buildFirdariaSnapshotText`（`buildPrimaryDirectSnapshotText` 原已导出）。
- `components/guolao/GuoLaoChartMain.js` → `export async function buildGuolaoSnapshotForFields(fields)`。
- `components/germany/AstroMidpoint.js` → `export async function buildGermanySnapshotForFields(fields)`。
- `components/suzhan/SuZhanMain.js` → 给 `buildSuzhanSnapshotText` 加 `export`。

> 这些组件**未**反向 import `aiAnalysisContext`，无循环依赖（已核查）。新增技法时务必维持这一点。

### B. 「本轮挂载上下文」面板重做

文件：`components/aianalysis/AIAnalysisMain.js`、`AIAnalysisMain.less`

- `lockedContextItems` 改为携带**完整 `content` + `meta` + `status`**（不再预截断 180/120 字）。
- 渲染改用 antd `Collapse`：每个挂载层一个 Panel；头部 = 标题 + 类型 Tag + **状态 Tag**（`已就绪`/`缺失`/`待生成`，见 `CONTEXT_STATUS_META`）+ **出生签名小字**（`buildContextSignatureText(meta)`，便于核对挂的是不是这张盘）；体内 `.contextBody` 完整文本、`white-space:pre-wrap`、`max-height` 内部滚动。
- **自动展开**：`Collapse` 改为受控 `activeKey={contextActiveKeys}`；`contextActiveKeys` 由 effect 维护——新出现的层 key 自动加入（默认展开），用户手动收起的保持收起，移除的剔除（`seenContextKeysRef` 记录已见过的 key）。否则「挂载后才加技法」时新面板默认收起、看起来像空的。

### C. 主页面布局

文件：`AIAnalysisMain.js`（`renderAnalysisPane`）、`.less`

- **系统提示**移出顶部工具栏 → 放进 `chatSplit` 右列、`本轮挂载上下文` 卡之上（`.sideColumn` 竖向 flex：`.systemPromptCard` 固定高 + `.contextCard` 撑满）。顶部网格由 5 列降为 4 列。
- **按钮行**（刷新案例/新对话/重新生成/编辑上一条并分支/停止生成）移入底部 `composerActions`，置于「发送分析」左侧（`.composerTools` 左 + `.composerSend` 右，`flex-wrap`）。

### D. 历史页

文件：`AIAnalysisMain.js`（`renderHistoryPane`）

- 删除右上两个无 label/placeholder 的 `<Input>`（startDate/endDate）、对应过滤调用、`historyFilter` 的 `startDate/endDate` 字段，以及不再被引用的 `filterByDateRange` 函数。其余筛选不变。

### Markdown 渲染

文件：`AIAnalysisMain.js`、`.less`；依赖 `marked@^4.3.0`、`dompurify@^2.5.9`

- 模块级 `marked.setOptions({gfm:true, breaks:true, headerIds:false, mangle:false})`。
- `renderMarkdownToHtml(text)`：`marked.parse` → `DOMPurify.sanitize`（`ADD_ATTR:['target','rel']`）→ 返回安全 HTML。**保留 DOMPurify 这一步**，防止模型输出恶意 HTML 造成 XSS。
- 气泡渲染：`item.role === 'user'` → `.messageText`（纯文本 pre-wrap）；否则 → `.markdownBody`（`dangerouslySetInnerHTML`）。
- `.less` 新增 `.markdownBody` 全套样式（标题/段落/有序无序列表/表格/行内与块级代码/引用/链接/hr/img），`white-space:normal`，明暗主题用现有 CSS 变量自适应。`.messageBubble` 不再统一 `pre-wrap`（移到 `.messageText`）。

### 依赖

`Horosa-Web/astrostudyui/package.json` 新增：`"marked": "^4.3.0"`、`"dompurify": "^2.5.9"`（均选 CommonJS 友好版本，兼容 umi3 / webpack4 / React 17 / Node 25）。`package-lock.json` 相应更新。

### 仓库治理（harness / skill / docs）

- `.claude/settings.json`（可提交）：`permissions.allow` 收录本项目 dev/verify 常用命令（build、start/stop backend、只读 verify 脚本、lsof、git 只读、Claude Preview MCP 工具）；`permissions.deny` 拦截 `git push` / `git reset --hard` / `rm -rf`。
- `.claude/settings.local.json`（已加入 `.gitignore`，机器相关）：`env.HOROSA_PYTHON` 指向嵌入式 Python；`HOROSA_DESKTOP_MONGO_OPTIONAL=1`。
- `.claude/launch.json`：Claude Preview 的 `horosa-ui` dev server（`:8000`）。
- `.claude/skills/horosa-dev/SKILL.md`：项目 dev/verify/release 操作技能（含上述注意点与验收流程）。

> 2026-05-25 release 后补充：harness 需同时放行 `verify_public_distribution_readiness.sh`、
> `verify_github_release_end_to_end.sh`、AI 分析浏览器验收脚本、kentang/icon 只读 verifier、`git ls-remote`
> 与 `gh release view`。发布脚本会创建/更新 app tag 与 runtime tag；不要在脚本成功后再手动 `git tag`。

---

## 4. 变更文件清单

```
Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js          # A1 过滤 + 命盘重算注册表 + 事盘 F + 导入 builder
Horosa-Web/astrostudyui/src/components/aianalysis/AIAnalysisMain.js   # 面板/布局/历史/Markdown/自动展开
Horosa-Web/astrostudyui/src/components/aianalysis/AIAnalysisMain.less # 面板/布局/markdownBody 样式
Horosa-Web/astrostudyui/src/components/cntradition/BaZi.js       # export buildBaziSnapshotForParams
Horosa-Web/astrostudyui/src/components/ziwei/ZiWeiMain.js        # export buildZiweiSnapshotForParams
Horosa-Web/astrostudyui/src/components/astro/IndiaChart.js       # export buildIndiaSnapshotForFields
Horosa-Web/astrostudyui/src/components/direction/AstroDirectMain.js   # export buildFirdariaSnapshotText
Horosa-Web/astrostudyui/src/components/guolao/GuoLaoChartMain.js # export buildGuolaoSnapshotForFields
Horosa-Web/astrostudyui/src/components/germany/AstroMidpoint.js  # export buildGermanySnapshotForFields
Horosa-Web/astrostudyui/src/components/suzhan/SuZhanMain.js      # export buildSuzhanSnapshotText
Horosa-Web/astrostudyui/src/integrations/kentang/serviceRoot.js  # 本地 kentang 端口解析 → 图表服务 8899（§7）
Horosa-Web/start_horosa_local.sh                                 # 一键启动器：Python 选择/就绪校验/vendor PYTHONPATH（§7）
Horosa-Web/astrostudyui/package.json (+ package-lock.json)       # marked + dompurify
.gitignore                                                       # ignore .claude/settings.local.json
.claude/settings.json · .claude/settings.local.json · .claude/launch.json · .claude/skills/horosa-dev/SKILL.md
docs/ai-analysis-context-and-markdown.md                         # 本文档
```

---

## 5. 验收（端到端，已执行）

环境：`npm run build` 通过；本地全栈 Java `:9999` + Python `:8899`（`HOROSA_PYTHON` 指向 `runtime/mac/python`）；浏览器预览 `:8000`，以 `?srv=127.0.0.1:9999` / `localStorage` 强制后端。

复现步骤（其他 agent 复跑见 `horosa-dev` 技能「Acceptance / verification procedure」）：
1. 向 `localStorage['horosa.localCharts.v1']` 注入一张已知出生时间的测试命盘（如 1990-06-15 14:30，北京）。
2. 选中该盘，勾选 印度/八字/紫微/七政四余/宿占/量化盘/主限法/法达。
3. 读取右侧每个折叠面板的 header（状态+签名）与 body。

实测结果：9 个技法面板全部「已就绪」，签名均为 **1990/06/15 · +08:00**（与测试盘一致，**无串盘**），内容非空：
- 印度占星 D1 命盘；七政四余「命度=占星上升·罗计=北计南罗」（确认沿用保存设置）；量化盘宫位+中点；主限法真太阳时 14:13:05 + 完整界限表；法达表；八字乾造+大运流年；紫微生年庚/命宫丁亥；宿占现实距星法。
- 新加技法面板**自动展开**（受控 activeKey 生效）。
- Markdown：历史会话的报告渲染出 `<strong>/<h*>/<ul>/<table>`，**零个残留 `**`**。
- 布局：系统提示在右列上方；按钮行在底部发送键左侧。

---

## 6. 已知限制 / 后续

- 未接入的推运/节气/合盘/骰子等仅安全降级（见技法表）。如需接入 profection 族，需先定「目标时刻」语义（AI 分析页无该选项）；guolao/suzhan/jieqi 的 `planetDisplay` 已用 `null→全部传统星曜` 兜底。
- `aiAnalysisContext.js` 中事盘的时间重算 helper 为保留死代码，可清理。
- 仅 macOS arm64 发布链路；Windows 见 `docs/windows-porting-and-release-checklist.md`（尚未实现发布流）。

---

## 7. 本地一键启动 + kentang 引擎修复（奇门/太乙/三式合一/术数）

排查「三式合一计算异常：`sanshi.qimen.kinqimen_unavailable`」时发现并修复了三处问题，使本地一键启动（`Horosa-Web/start_horosa_local.sh`，被 `tools/mac/Horosa_Local.command` 调用）能完整跑通 kentang/kin 系列技法。

**根因链**：
1. **Python 选错解释器**：`start_horosa_local.sh` 默认用 `.runtime/mac/venv/bin/python3`（指向 miniconda base 的残缺 venv，缺 `cn2an`）。而 `python_runtime_ready` 只校验 `cherrypy/jsonpickle/swisseph`，该 venv 三者都有却缺 `cn2an` → 通过校验却在启动时 `import cn2an` 崩溃。完整解释器是嵌入式 `runtime/mac/python/bin/python3`（与嵌入式 Java 同级）。
2. **vendor 不在 PYTHONPATH**：kentang 引擎（`kinqimen`/`kintaiyi`/`kinjinkou`/`kinwangji`/`kinwuzhao`/`taixuanshifa`/`jingjue`/`shenyishu`/`kinastro-*`）是 `Horosa-Web/vendor/` 下的命名空间包；`PYTHONPATH_ASTRO` 只含 `flatlib-ctrad2:astropy` → `import kinqimen` 失败。
3. **前端端口解析过时**：kentang 引擎实际全部挂载在**主图表服务 `CHART_PORT`（默认 8899）**（见 `astropy/websrv/webchartsrv.py:261` 的 `mount_kentang_services`，发布校验 `verify_kentang_runtime_endpoints.py --root http://127.0.0.1:${CHART_PORT}` 也在此端口）。但前端 `integrations/kentang/serviceRoot.js` 的 `KENTANG_SERVICE_CONFIG` 把本地 `:9999` 映射到**每引擎独立端口**（qimen→8898 等，遗留自引擎曾各自独立的时代），本地没有任何进程监听这些端口 → fetch 失败 → 回退到 Java `/qimen/pan`（Java 无此路由/非 kin 引擎）→ `pan.source !== 'kinqimen'` → 抛 `kinqimen_unavailable`。

**修复**：
- `start_horosa_local.sh`：
  - 默认解释器优先选 `runtime/mac/python`（缺失才回退 venv）；`resolve_python_bin` 候选顺序同步把嵌入式排在 venv 前。
  - `python_runtime_ready` 探针补齐启动期必需依赖：`("cherrypy","jsonpickle","swisseph","cn2an","sxtwl","cnlunar")` —— 缺任一即拒绝该 python（fail-fast，并提示安装/换嵌入式）。
  - `PYTHONPATH_ASTRO` 追加 `${ROOT}/vendor`（line 16，始终经 line 618 注入 python 服务；嵌入式 NOUSERSITE 下 `$PYTHONPATH` 追加会被跳过，故必须改基串）。
- `integrations/kentang/serviceRoot.js`：`resolveKentangServiceRoot` 对本地 `:9999` 后端统一解析到 `LOCAL_KENTANG_CHART_PORT = 8899`（图表服务），不再用每引擎遗留端口。仅影响本地分支；生产 `srv.horosa.com`（非 `:9999`）原样返回，按路径路由，不受影响。

**验证（已执行）**：clean env（`env -u HOROSA_PYTHON -u PYTHONPATH`）跑修复后的 `start_horosa_local.sh` → 日志显示 `python resolved: …/runtime/mac/python/…`，9999/8899 起；`curl -XPOST 127.0.0.1:8899/qimen/pan` 返回 `"source":"kinqimen"`；浏览器预览里 占星→卜三式→起盘：qimen/taiyi 请求命中 `127.0.0.1:8899/{qimen,taiyi}/pan`（HTTP 200），无 `计算异常`，三式合一盘正常渲染（阳遁二局中元/值符天芮/值使死门/完整奇门+六壬盘）。

> 关联文件：`Horosa-Web/start_horosa_local.sh`、`Horosa-Web/astrostudyui/src/integrations/kentang/serviceRoot.js`。
> 说明：#3 的前端修复同样改善桌面应用的本地模式（若其 kentang 也曾命中 8898 失败）；生产网关按路径路由不受影响。

---

## 8. GitHub 发布 Runbook（其他 agent 执行）

> 手动、macOS 签名链路；**无** CI 在 tag push 时自动发布（`.github/workflows/ci.yml` 只跑测试）。
> build/sign/publish/push 属高影响操作，`.claude/settings.json` **未**自动放行，执行前先与用户确认。

### 8.1 版本与文件（务必同步）

| 文件 | 字段 | 示例 |
| --- | --- | --- |
| `Horosa_Desktop_Installer/package.json` | `version` | `2.1.3` |
| `Horosa_Desktop_Installer/src-tauri/Cargo.toml` | `version` | `2.1.3` |
| `Horosa_Desktop_Installer/src-tauri/tauri.conf.json` | `version` | `2.1.3` |
| `CITATION.cff` | `version` | `"2.1.3"` |
| `Horosa_Desktop_Installer/config/release_config.json` | `runtimeVersion` | `2.1.3-runtime1`（app 升版时重置 `-runtime1`，仅 runtime 改动时递增 `-runtime<N>`） |

> 前三者必须**完全一致**。`Cargo.lock`/`package-lock.json` 自动再生。前端 `astrostudyui/package.json` 无 version 字段（版本随桌面壳）。

### 8.2 有序步骤

```bash
# 0) 前置：分支干净、版本已决定
git status

# 1) 改版本（上表）+ 追加 UPGRADE_LOG.md 条目（格式见文件顶部：日期/Scope/Files/Details/Verification，追加不改历史）
#    可选：README.md/README_EN.md/README_ZH.md 版本徽章

# 2) 发布前门禁
python3 -m json.tool .claude/settings.json >/dev/null
python3 -m json.tool .claude/settings.local.json >/dev/null
python3 -m json.tool .claude/launch.json >/dev/null
cd Horosa-Web/astrostudyui
npm test -- --runInBand src/utils/__tests__/aiAnalysisContext.test.js
npm test -- --runInBand src/integrations/kentang/__tests__/serviceRoot.test.js src/utils/__tests__/aiAnalysisSelection.test.js
npm run build
npm run build:file
cd ../..
python3 scripts/browser_horosa_aianalysis_check.py
cd Horosa-Web
env -u HOROSA_PYTHON -u PYTHONPATH HOROSA_SKIP_UI_BUILD=1 ./start_horosa_local.sh
./stop_horosa_local.sh
cd ..

# 注：若 Umi 生成缓存损坏，需要清理 `src/.umi-production` / `.umi-production` / dist 输出时，
#     先向用户确认；`.claude/settings.json` 默认 deny `rm -rf`。

# 3) 提交；通常验证后推 main（若用户明确要求可提前推 main）
git commit -m "release: prepare vX.Y.Z beta"
git push origin main

# 4) 签名前置（Developer ID Application/Installer + notarytool profile）
cd Horosa_Desktop_Installer && ./scripts/check_apple_signing_prereqs.sh

# 5) 构建 + 签名 + 公证 + staple
HOROSA_PUBLIC_DISTRIBUTION=1 ./scripts/build_desktop_release.sh
#    产物 dist/: Horosa-Desktop-macos-arm64.zip, Horosa-Installer-macos-arm64-offline.pkg,
#               horosa-runtime-macos-arm64.tar.gz, horosa-latest.json

# 6) 验收产物（不重建）
HOROSA_DESKTOP_SKIP_REBUILD=1 ./scripts/verify_desktop_packaging.sh
./scripts/verify_runtime_backend_boot.sh --timeout 300         # 隔离启动 runtime + 17+ kentang 端点冒烟
./scripts/verify_public_distribution_readiness.sh             # 签名/公证/staple 校验

# 7) 发布到 GitHub（需 GITHUB_TOKEN；按 release_config.json 决定 prerelease/make_latest）
#    publish 脚本负责创建/更新 vX.Y.Z 与 vX.Y.Z-runtime<N> 两个 tag/release；成功后不要再手动 git tag。
GITHUB_TOKEN=... ./scripts/publish_github_release.sh

# 8) 必做：远端发布确认 + 下载产物端到端校验
git ls-remote --heads --tags origin main refs/tags/vX.Y.Z refs/tags/vX.Y.Z-runtime<N>
gh release view vX.Y.Z --repo Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS
gh release view vX.Y.Z-runtime<N> --repo Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS
curl -fsSL https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/horosa-latest.json | python3 -m json.tool
./scripts/verify_github_release_end_to_end.sh
```

### 8.3 检查单

- 发布前：版本四文件同步 + runtime 版本 + UPGRADE_LOG 条目；harness JSON、AI 分析/kentang 测试、顺序 build/build:file、浏览器 AI 分析冒烟、clean-env 本地启动通过；`check_apple_signing_prereqs.sh` 通过。
- 构建：`build_desktop_release.sh` exit 0；`dist/` 四件产物齐全。
- 验收：`verify_desktop_packaging.sh` + `verify_runtime_backend_boot.sh`（+ readiness）通过。
- 发布：`publish_github_release.sh` exit 0；Release 页 tag/版本/资产正确；`horosa-latest.json` 可达。
- 发布后：app tag 与 runtime tag 均已推；`.pkg` 安装+启动正常、版本号正确、检查更新可拉取清单；`verify_github_release_end_to_end.sh` 通过。

### 8.4 模糊点（执行者注意）

- beta 通道：`release_config.json` 的 `releaseChannel:"beta"` 默认 `prerelease=false`、`make_latest=true`，正文含 "Beta"。可用 `HOROSA_RELEASE_PRERELEASE` / `HOROSA_RELEASE_MAKE_LATEST` 覆盖。
- 仅 runtime 改动：app 版本不动，递增 `runtimeVersion` 的 `-runtime<N>`；如 runtime 资产哈希变了需对应升版或 `HOROSA_FORCE_RUNTIME_UPLOAD=1`。
- 发布走脚本内 GitHub API（curl + `GITHUB_TOKEN`，回退 `git credential fill`），非 `gh` CLI。
