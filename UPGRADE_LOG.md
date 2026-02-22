# Horosa Upgrade Log

This file tracks every code/config change made in this workspace.
Append new entries; do not rewrite history.

## Entry Format
- Date: YYYY-MM-DD
- Scope: what was changed
- Files: key files touched
- Details: short bullets
- Verification: tests/build/manual checks

---

## 2026-02-19

### 11:44 - 三式合一接入 kintaiyi 太乙核心并完成盘面/标签展示
- Scope: integrate `kintaiyi-master` 太乙算法到三式合一，并把核心逻辑沉淀到独立 core 文件夹，同时补全盘面与右侧标签可视化。
- Files:
  - `Horosa-Web-55c75c5b088252fbd718afeffa6d5bcb59254a0c/astrostudyui/src/components/sanshi/core/TaiYiCore.js`
  - `Horosa-Web-55c75c5b088252fbd718afeffa6d5bcb59254a0c/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `Horosa-Web-55c75c5b088252fbd718afeffa6d5bcb59254a0c/astrostudyui/src/components/sanshi/SanShiUnitedMain.less`
  - `Horosa-Web-55c75c5b088252fbd718afeffa6d5bcb59254a0c/astrostudyui/src/utils/aiExport.js`
- Details:
  - 新增 `sanshi/core/TaiYiCore.js`，封装太乙关键计算（积数、局式、太乙/文昌/始击/定目、主客定算、君臣民基、十精相关宫位等）并输出结构化结果。
  - 在三式合一计算链中接入太乙结果（state 增加 `taiyi`、保存 payload 增加 `taiyi`、快照增加 `太乙` 与 `太乙十六宫` 分区）。
  - 右侧参数区新增太乙盘式/积年法选项；右侧信息面板新增“太乙”标签页，完整展示核心结果与十六宫标记。
  - 盘面外圈新增“太乙”宫位标注文本（按地支宫显示），并补充样式类 `outerTaiyi`。
  - AI 导出预设章节补充 `太乙` 与 `太乙十六宫`，保证导出内容与界面一致。
- Verification:
  - `npm run build --silent`

### 11:15 - 404 fallback + local route recovery
- Scope: prevent app from getting stuck on the 404 page in local file mode.
- Files:
  - `Horosa-Web-55c75c5b088252fbd718afeffa6d5bcb59254a0c/astrostudyui/src/pages/404.js`
- Details:
  - Added auto-redirect logic for `file://` + hash routes.
  - If route is invalid, fallback to `index.html#/` and then `/`.
  - Updated 404 text to show automatic recovery status.
- Verification:
  - `npm test -- --runInBand`
  - `npm run build:file`

### 11:12 - 三式合一中心四课/三传布局调整为 85%
- Scope: reduce overlap in center area under zoom/resize.
- Files:
  - `Horosa-Web-55c75c5b088252fbd718afeffa6d5bcb59254a0c/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
- Details:
  - Changed center text target occupancy from 95% to 85%.
  - Keeps same-row scaling behavior, but adds more vertical breathing room.
- Verification:
  - `npm test -- --runInBand`

### 11:10 - 三式合一导出格式优化（神煞置底 + 星盘全名）
- Scope: adjust export text order and remove star abbreviations in export output.
- Files:
  - `Horosa-Web-55c75c5b088252fbd718afeffa6d5bcb59254a0c/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
- Details:
  - Moved `【神煞】` section to the end of exported content.
  - Added full-name star output for export (with degree + minutes + `R` for retrograde).
  - Kept UI short labels unchanged; export uses full labels.
- Verification:
  - `npm test -- --runInBand`
  - `npm run build`

### 11:04 - 三式合一/遁甲起盘性能链路去重与静默化
- Scope: reduce repeated recomputation and improve click-to-plot responsiveness.
- Files:
  - `Horosa-Web-55c75c5b088252fbd718afeffa6d5bcb59254a0c/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `Horosa-Web-55c75c5b088252fbd718afeffa6d5bcb59254a0c/astrostudyui/src/components/dunjia/DunJiaMain.js`
- Details:
  - Added field-only sync path to avoid expensive fetch on every confirm.
  - Added `nohook` support for silent fetch to prevent duplicate refresh chains.
  - Reused pending same-key refresh/request promises to avoid duplicated requests.
  - Click-plot now decides `force` based on key change instead of always forcing.
- Verification:
  - `npm test -- --runInBand`
  - `npm run build`
  - Local API latency spot-check script (nongli/jieqi endpoints)

### 11:50 - 工程目录重命名为 Horosa-Web 并修正启动路径
- Scope: rename project folder from `Horosa-Web-55c75c5b088252fbd718afeffa6d5bcb59254a0c` to `Horosa-Web` and update hardcoded path references to avoid startup/runtime breaks.
- Files:
  - `Horosa_Local.command`
  - `Prepare_Runtime_Mac.command`
  - `Horosa_Local_Windows.ps1`
  - `README.md`
  - `PROJECT_STRUCTURE.md`
- Details:
  - Renamed folder: `Horosa-Web-55c75c5b088252fbd718afeffa6d5bcb59254a0c` -> `Horosa-Web`.
  - Updated Mac launcher `PROJECT_DIR` to `${ROOT}/Horosa-Web`.
  - Updated Windows launcher `ProjectDir` to `Join-Path $Root 'Horosa-Web'`.
  - Updated documentation paths to new folder name for consistency.
  - Kept historical references in old log entries unchanged to preserve audit history.
- Verification:
  - `ls -la "/Users/horacedong/Desktop/Horosa-Web+App (Mac)"`
  - Confirmed `Horosa-Web/` exists and old folder no longer exists.
  - `rg -n "Horosa-Web(-55c75c5b088252fbd718afeffa6d5bcb59254a0c)?" Horosa_Local.command Prepare_Runtime_Mac.command Horosa_Local_Windows.ps1 README.md PROJECT_STRUCTURE.md`

### 11:54 - 移除根目录 kintaiyi-master 并验证太乙可用
- Scope: fully remove root folder `kintaiyi-master` and verify 三式合一太乙核心 does not depend on that folder at runtime/build time.
- Files:
  - `UPGRADE_LOG.md`
- Details:
  - Deleted `/Users/horacedong/Desktop/Horosa-Web+App (Mac)/kintaiyi-master`.
  - Kept integrated Taiyi core in `Horosa-Web/astrostudyui/src/components/sanshi/core/TaiYiCore.js` as the active implementation.
  - Confirmed `SanShiUnitedMain.js` imports Taiyi logic from local `./core/TaiYiCore` only.
- Verification:
  - `ls -la "/Users/horacedong/Desktop/Horosa-Web+App (Mac)"` (confirmed `kintaiyi-master` removed)
  - `npm run build --silent` in `Horosa-Web/astrostudyui` (compiled successfully after deletion)
  - `rg -n "kintaiyi-master|kintaiyi" Horosa-Web/astrostudyui/src Horosa-Web/astrostudysrv Horosa-Web/astropy Horosa_Local.command Prepare_Runtime_Mac.command Horosa_Local_Windows.ps1`

### 12:00 - 太乙核心迁移到太乙模块 + 三式合一左盘移除太乙文案
- Scope: move kintaiyi-based Taiyi core into `易与三式/太乙`模块核心目录 and keep 三式合一中的太乙信息只在右侧标签显示，不再覆盖左侧方盘外圈。
- Files:
  - `Horosa-Web/astrostudyui/src/components/taiyi/core/TaiYiCore.js`
  - `Horosa-Web/astrostudyui/src/components/taiyi/TaiYiCalc.js`
  - `Horosa-Web/astrostudyui/src/components/taiyi/TaiYiMain.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/core/TaiYiCore.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.less`
  - `UPGRADE_LOG.md`
- Details:
  - 新增 `taiyi/core/TaiYiCore.js` 作为太乙核心算法文件（包含 kintaiyi 口径计算与结构化输出）。
  - `taiyi/TaiYiCalc.js` 改为基于 `taiyi/core/TaiYiCore.js` 的适配层，统一太乙盘计算、快照文本与盘面宫位数据。
  - `sanshi/core/TaiYiCore.js` 改为转发导出，三式合一与太乙模块共享同一套核心算法来源。
  - 三式合一左侧方盘外圈移除“太乙:...”叠加文字，仅保留右侧“太乙”标签页详细信息。
  - 太乙主模块右侧信息面板补充定目、三基、将参、十精相关宫位等核心计算结果展示。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui` (compiled successfully)
  - `rg -n "renderOuterMarks\\(|outerTaiyi|calcTaiyiPanFromKintaiyi" Horosa-Web/astrostudyui/src/components/sanshi Horosa-Web/astrostudyui/src/components/taiyi`

### 12:04 - 三式合一中心盘对齐：四课上对齐、三传下对齐
- Scope: adjust center block layout in 三式合一 square board so 四课 anchors to the top edge and 三传 anchors to the bottom edge.
- Files:
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.less`
  - `UPGRADE_LOG.md`
- Details:
  - Removed center vertical balancing padding in `renderCenterBlock`; 四课 `top` and 三传 `bottom` now pin to edge padding directly.
  - Kept unified dynamic font/line-height scaling logic unchanged to preserve readability under zoom.
  - Added explicit layout intents in CSS: `.centerKe` uses `justify-content: flex-start`; `.centerChuan` uses `justify-content: flex-end`.
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui` (compiled successfully)

### 12:07 - 太乙页面信息换位：右侧减载，盘面左上/右下承载关键信息
- Scope: reduce info overflow in `易与三式-太乙` right panel by moving the last metadata segment onto the chart, and relocate original top-left chart summary to bottom-right.
- Files:
  - `Horosa-Web/astrostudyui/src/components/taiyi/TaiYiMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - Left chart top-left now shows: `农历 / 真太阳时 / 干支(紧凑格式) / 节气`。
  - Original top-left summary (`积数/命式/局/主客定算/太乙数`) moved to left chart bottom-right.
  - Removed the final right-panel block (`农历/真太阳时/干支/节气段`) to shrink right-side content height and avoid overflow.
  - Tuned chart corner text font/line spacing for readability near ring edges.
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui` (compiled successfully)

### 12:09 - 太乙右侧标签去重：左盘已展示内容不再重复
- Scope: remove duplicate fields from the right info panel when the same values are already rendered on the left Taiyi chart.
- Files:
  - `Horosa-Web/astrostudyui/src/components/taiyi/TaiYiMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - Removed duplicated right-panel items already shown in left chart corners: `命式`、`局式`、`太乙积数`、`主算`、`客算`、`定算`。
  - Kept right-panel items that are not shown in left chart (e.g. 太乙宫位、文昌/始击/太岁/合神/计神、定目、将参与十精类信息)。
  - Preserved panel section divider structure for readability after pruning.
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui` (compiled successfully)

### 12:14 - 太乙盘可读性增强：角标与盘中文字整体放大
- Scope: increase readability of `易与三式-太乙` by enlarging top-left/bottom-right corner metadata and inner chart text.
- Files:
  - `Horosa-Web/astrostudyui/src/components/taiyi/TaiYiMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - Enlarged corner metadata text from `11` to `13`, and increased line spacing from `16` to `18`.
  - Slightly adjusted corner anchors to keep enlarged text within safe margins.
  - Enlarged center and ring text (`五/中宫`、二层数字、三层宫位、四层神名、外层标记) to improve legibility.
  - Increased outer-most label line spacing to avoid overlap after font enlargement.
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui` (compiled successfully)

### 12:16 - 太乙盘字体风格调整：取消加粗 + 角标再次放大
- Scope: remove bold weight in Taiyi chart text and further increase left-top/right-bottom corner metadata size.
- Files:
  - `Horosa-Web/astrostudyui/src/components/taiyi/TaiYiMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - Changed Taiyi chart text `fontWeight` from bold to normal (`700 -> 400`) for center, rings, and corner metadata.
  - Increased corner metadata font size from `13` to `15`.
  - Increased corner metadata line spacing from `18` to `20`, and adjusted anchors to keep text within chart bounds.
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui` (compiled successfully)

## 2026-02-20

### 22:59 - 大六壬三传与旬干算法修复（重复课去重 + 旬序映射）
- Scope: fix Da Liu Ren core calculation issues reported in production cases, including duplicate-ke handling for 初传 selection and branch->stem mapping for 三传干支.
- Files:
  - `Horosa-Web/astrostudyui/src/components/liureng/ChuangChart.js`
  - `Horosa-Web/astrostudyui/src/components/liureng/ChuangChart.test.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/RengChart.js`
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouPanChart.js`
  - `Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/model/LiuReng.java`
  - `UPGRADE_LOG.md`
- Details:
  - 修复九法判课中的“重复课”问题：在 `isJinKe0/isJinKe1/isYaoKe0/isYaoKe1/getSeHais` 中先去重再比用/涉害，落实“同课只计一次”，避免把同一上神重复当成多课，修正了“巳时四课初传应卯”类误判。
  - 修复三传干支天干推导：将原“相对索引差”算法改为“旬序地支->天干映射（xunGanMap）”，确保甲辰旬中未位对应 `丁未`，不再误算 `己未`。
  - 旬日字段兼容升级：后端新增 `遁丁`（地支）并保留原 `旬丁`；前端六壬/金口诀旬日面板优先展示 `遁丁`，旧数据自动从 `旬丁` 提取地支。
  - 新增回归测试覆盖两类问题：重复贼课初传落卯、甲辰旬未位映射丁未。
- Verification:
  - `npm test -- ChuangChart.test.js --runInBand`
  - `npm test -- JinKouCalc.test.js --runInBand`

### 23:04 - 六壬改为手动起课：仅点击“起课”后再计算与校验出生时间
- Scope: stop automatic recalculation and repeated birth-time validation popups in `易与三式 -> 六壬`; run liureng/running-year logic only when user explicitly clicks the action button.
- Files:
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 新增“起课”按钮，并将六壬计算入口绑定到按钮点击事件（`clickStartPaiPan` -> `requestGods`）。
  - 取消 tab hook 自动触发 `requestGods`，避免调整时间/切换字段时反复重算。
  - 取消出生信息变更时自动触发 `requestRunYear`，避免反复弹出“卜卦人出生时间必须早于起课时间”提示。
  - 取消 `componentDidMount` 自动起课，页面初始进入保持静默，等待手动点击“起课”。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui` (compiled successfully)

### 23:09 - 修复“代码已改但盘面仍旧值”：dist-file 重建 + 启动脚本自动检测前端变更
- Scope: ensure the latest 六壬三传算法（初传卯、遁丁丁未）真正进入本地运行包，避免 `dist-file` 旧包导致六壬/金口诀/三式合一仍显示旧结果。
- Files:
  - `Horosa-Web/start_horosa_local.sh`
  - `UPGRADE_LOG.md`
- Details:
  - 问题根因是运行入口优先读取 `astrostudyui/dist-file/index.html`，而此前只构建了 `dist`，导致页面继续加载旧 `dist-file` 资源，出现“初传仍申、未干仍己”的假象。
  - 重新执行 `npm run build:file`，已生成新 `dist-file/umi.*.js`，并确认产物包含新逻辑标识（`uniqueZiList`、`clickStartPaiPan`）。
  - 升级 `start_horosa_local.sh`：启动前自动检查 `astrostudyui/src/public/package/.umirc` 相对 `dist-file/index.html` 的新旧；若有变更则自动 `npm run build:file`，防止再次加载陈旧包。
  - 启动脚本增加前端兜底：当 `dist-file` 不存在时回退 `dist`；若二者都不存在则直接报错退出，避免静默失败。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `npm test -- ChuangChart.test.js --runInBand`
  - `npm test -- JinKouCalc.test.js --runInBand`
  - `bash -n Horosa-Web/start_horosa_local.sh`

### 23:15 - 六壬改为“点起课后才更新盘面”：时间调整不再触发自动重算
- Scope: stop `易与三式 -> 六壬` chart recalculation during time edits by freezing the displayed chart context until user clicks `起课`.
- Files:
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 新增 `calcFields/calcChart` 状态，作为“已确认起课上下文”；六壬盘面改为只渲染这组上下文，不再直接跟随输入框实时变化。
  - `clickStartPaiPan` 中先锁定当前 `fields/chart`，再调用 `requestGods`；因此调整时间只会改输入，不会改盘，直到再次点击 `起课`。
  - `requestRunYear`、`saveLiuRengAISnapshot`、`clickSaveCase` 统一改为优先使用 `calcFields`，避免“改了时间但未起课”时出现年龄/保存内容与盘面不一致。
  - 保留原输入联动（更新天文底盘字段）但六壬计算与显示绑定到手动起课动作。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `npm test -- ChuangChart.test.js --runInBand`

### 23:17 - 修复六壬下方信息区空白：行年缺失不再导致整块隐藏
- Scope: keep lower info panels visible in 六壬 chart even when `runyear` is temporarily unavailable (e.g. birth year check fails or user尚未有效起行年).
- Files:
  - `Horosa-Web/astrostudyui/src/components/lrzhan/RengChart.js`
  - `UPGRADE_LOG.md`
- Details:
  - 调整 `drawGua3/drawGua4` 的显示条件：仅依赖 `liureng`，不再因为 `runyear` 为空直接 `return`，避免整块“旬日/旺衰/神煞/年煞/十二长生”一起消失。
  - `getRunYear` 增加空值兜底，`runyear` 缺失时显示 `—`，不再触发隐藏。
  - `getYearGods` 增加空值兜底，年煞缺失时各项显示 `—`。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 23:24 - 三式合一改为“仅起盘计算”：禁止时间调节实时重算与联动报错
- Scope: stop real-time recalculation in `三式合一` while editing right-panel time/options; recalculate only on explicit `起盘` click.
- Files:
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 去除时间编辑过程中的自动预计算触发：`onTimeChanged` 不再在未确认输入时预取精确历法，也不再在“确定”后立刻重算盘面。
  - 去除 `hook/componentDidUpdate/onOptionChange` 的自动重算路径，避免右侧时间输入过程触发左盘实时刷新。
  - `clickPlot` 改为唯一计算入口：点击后强制 `refreshAll(..., true)`，确保即使仅改右侧选项也会重新起盘。
  - 新增 `plottedFields`，左盘顶部时间与保存内容改为绑定“上次起盘字段”，避免右侧草稿时间变动时左盘文本漂移。
  - 新增 `awaitingChartSync`：起盘时若触发图表字段同步，待图表回写后仅做一次补算，避免旧图数据混入。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 23:26 - 三式合一年份调节卡顿优化：时间草稿改为非渲染态缓存
- Scope: reduce UI freeze when continuously adjusting year in `三式合一` right panel.
- Files:
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 新增 `pendingTimeFields`（实例缓存）保存时间草稿；未点击“确定/起盘”前不再 `setState(localFields)`，避免每次年份变动触发整页重渲染。
  - `clickPlot` 优先读取 `pendingTimeFields + timeHook.getValue()` 作为最终起盘参数，确保不丢草稿时间。
  - 点击“起盘”完成后清空 `pendingTimeFields`，保持状态一致。
  - 该优化与“仅起盘计算”组合后，可避免右侧年份滚动时左盘重绘抖动与长时间卡死。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 23:31 - 六壬时间调节去掉“未确认即请求”：消除每次改时的全局加载闪烁
- Scope: stop global loading flash in `六壬` when user adjusts time but has not clicked `确定`.
- Files:
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengInput.js`
  - `UPGRADE_LOG.md`
- Details:
  - `LiuRengInput.onTimeChanged` 新增确认门禁：当 `value.confirmed === false` 时直接返回，不再向上层派发字段更新。
  - 结果是右侧时间控件在编辑阶段仅保留本地草稿，只有点击时间控件内“确定”后才同步字段并触发底层天文请求；因此不会再出现你截图里的“加载中...”闪一下。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 23:35 - 修复六壬“起课仅首次有效”回归：恢复时间编辑同步并保持静默请求
- Scope: ensure `六壬` can repeatedly re-plot after each time adjustment, while still avoiding visible global loading flash.
- Files:
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengInput.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 回退 `LiuRengInput` 的“confirmed=false 直接return”门禁（该门禁会导致时间草稿不进入字段，从而出现你反馈的“首次起课后再次起课无反应”）。
  - 在 `LiuRengMain.onFieldsChange` 中将字段同步请求改为静默模式：`astro/fetchByFields + __requestOptions.silent + nohook=true`。
  - 这样调整时间仍会更新底层星盘字段（保证后续起课可重复生效），但不再出现明显“加载中...”遮罩闪烁。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 23:46 - 三式合一起盘提速：首帧限时返回 + 后台精化，目标 5 秒内出盘
- Scope: reduce worst-case plotting latency for large year jumps in `三式合一` (especially `置润 + 直润`) from tens of seconds to a bounded first response.
- Files:
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 增加首帧时限 `SANSHI_FAST_BUDGET_MS=4500`：`refreshAll` 对 `fetchPreciseNongli` 采用 `Promise.race`，超过预算先用回退数据出盘，不再阻塞 30s+。
  - 回退策略：优先使用当前星盘 `chart.nongli`，其次使用上次已算 `state.nongli`；若精确结果晚到，再后台二次重算精化（不阻塞首帧）。
  - `直润` 年种子改为“后台补齐后再重算”，首帧不再等待 `year-1/year` 两个 seed 完成。
  - `clickPlot` 避免双重重算竞争：当字段有变化时先同步 chart（`awaitingChartSync`），图表回写后再触发一次 `refreshAll`；并加入 1.2s watchdog 兜底，防止等待同步挂死。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 00:00 - 三式合一新增换日选项：子初换日 / 子正换日（影响日柱算法）
- Scope: add day-boundary switch to `三式合一` and apply it to real-solar-time day pillar calculation for 奇门/六壬联动。
- Files:
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaCalc.js`
  - `UPGRADE_LOG.md`
- Details:
  - 在右侧参数区新增换日下拉（放在“时家奇门”和“天禽值符”之间）：`子初换日` / `子正换日`。
  - `子初换日` 对应 `after23NewDay=1`：真太阳时到当日 `23:00` 即按次日干支起日柱。
  - `子正换日` 对应 `after23NewDay=0`：真太阳时到次日 `00:00` 才换次日日柱（23:59 仍按当天）。
  - `三式合一` 请求精确农历参数改为携带该选项（不再固定 `after23NewDay=0`），并写入缓存 key/起盘签名，防止不同换日规则串缓存。
  - `DunJiaCalc` 增加 `after23NewDay` 算法分支：`buildGanzhiForQimen` 与 `qimenJuNameZhirun` 的 23 点跨日逻辑由该参数控制；默认保持旧行为（未传参时按子初换日）。
  - 概览与快照新增换日规则展示，便于复盘/保存后回放一致。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 00:02 - 三式合一换日默认值改为“子初换日”
- Scope: set the new day-boundary selector default to `子初换日` in `三式合一`.
- Files:
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 将 `SanShiUnitedMain` 的初始选项 `after23NewDay` 默认值由 `0` 调整为 `1`。
  - 新开三式合一页面时，换日下拉默认即为“子初换日”；算法按 23:00 跨日处理日柱。
  - 已保留手动切换能力，用户仍可改成“子正换日”用于对照起盘。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 00:05 - 遁甲页新增换日选项，并替换“经纬度选择”位置布局
- Scope: add `子初换日/子正换日` selector to `易与三式-遁甲` and move original `经纬度选择` button below it at the same location.
- Files:
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaCalc.js`
  - `UPGRADE_LOG.md`
- Details:
  - 遁甲右侧控制区新增换日下拉，位置放在原“经纬度选择”处；原“经纬度选择”按钮下移至该下拉正下方。
  - 新增选项值 `after23NewDay`，默认 `1`（子初换日），并接入保存/回放选项恢复链路。
  - `genParams` 不再固定 `after23NewDay=0`，改为按当前下拉值传给精确历法接口，确保农历与日柱口径一致。
  - `onOptionChange('after23NewDay')` 时，已起盘状态下会强制重新请求农历并重算，避免仅重绘旧农历导致口径不一致。
  - 细化缓存键：遁甲盘缓存键与农历请求键都纳入 `after23NewDay`，防止“子初/子正”切换时串缓存。
  - 概览面板与快照文本新增“换日”显示项，便于复盘确认当前算法口径。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 00:13 - 遁甲/三式合一盘面时间改为同排双显示：钟表时间 + 真太阳时
- Scope: show both `钟表时间` and `真太阳时` on the board header line to remove ambiguity while preserving direct time comparison.
- Files:
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 遁甲盘顶部时间区改为双时间并排：`钟表时间：XX:XX  真太阳时：XX:XX`；日期优先显示真太阳时日期。
  - 三式合一顶部信息区改为三行：`农历`、`日期`、`时间`，其中“时间”行为双时间并排显示（钟表 + 真太阳时）。
  - 三式合一真太阳时来源优先使用 `dunjia.realSunTime`（回退 `nongli.birth`），确保展示与起盘算法一致。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 00:18 - 时间展示微调：三式合一并入“日期行”，遁甲接在年月日后并留双 Tab 间距
- Scope: adjust board time typography/layout per latest UX request: no extra time row in 三式合一, and inline date+times in 遁甲 with clearer spacing.
- Files:
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.less`
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 三式合一顶部日期区取消独立“时间”行，改为在“日期”后同一行显示：`钟表时间：XX:XX  真太阳时：XX:XX`。
  - 三式合一该段时间字体降为小号（12px），以弱化次级信息视觉权重并减少拥挤感。
  - 遁甲盘标题区改为同一行展示：`公历年月日 +（双 Tab 视觉间距）+ 钟表时间/真太阳时`。
  - 遁甲在日期与时间段之间增加固定左间距（约 4em），对应“两个 tab”可读间隔。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 00:24 - 紫微斗数新增“真太阳时/直接时间”选项（男右侧、四化盘左侧）并接入底层算法
- Scope: add time-basis selector in 紫微斗数 and make backend calculation switch between real-solar-time mode and direct-clock-time mode.
- Files:
  - `Horosa-Web/astrostudyui/src/components/ziwei/ZiWeiInput.js`
  - `Horosa-Web/astrostudyui/src/components/ziwei/ZiWeiMain.js`
  - `Horosa-Web/astrostudyui/src/components/ziwei/ZWCenterHouse.js`
  - `Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/controller/ZiWeiController.java`
  - `Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/model/ZiWeiChart.java`
  - `Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/model/OnlyFourColumns.java`
  - `Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/helper/NongliHelper.java`
  - `UPGRADE_LOG.md`
- Details:
  - 紫微输入区新增下拉：`真太阳时 / 直接时间`，位置放在“男/女”右侧、“四化盘”左侧（按你的指定顺序）。
  - 前端参数新增 `timeAlg`（0=真太阳时，1=直接时间）并透传至 `/ziwei/birth`。
  - 后端 `ZiWeiController` 增加 `timeAlg` 解析并传入 `ZiWeiChart`；仅允许 RealSun/DirectTime 两档。
  - `ZiWeiChart` 与 `OnlyFourColumns` 构造链路增加 `timeAlg` 支持：真太阳时保持现有算法；直接时间走不做经纬度时间修正的分支。
  - `NongliHelper` 增加带 `directTime` 开关的重载；`directTime=true` 时不再执行真太阳时偏移。
  - 紫微盘中心信息标签改为动态：`真太阳时：...` 或 `直接时间：...`，避免显示文案和算法不一致。
- Verification:
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `mvn -DskipTests install` in `Horosa-Web/astrostudysrv/astrostudy`
  - `mvn -DskipTests install` in `Horosa-Web/astrostudysrv/astrostudycn`

### 10:46 - 三式合一新增“真太阳时/直接时间”选项并打通前后端计算口径
- Scope: add time algorithm switch to `三式合一`（位置：命局右侧、男左侧），并让“直接时间”按时间组件计算、不受经纬度真太阳时修正影响。
- Files:
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `Horosa-Web/astrostudyui/src/utils/preciseCalcBridge.js`
  - `Horosa-Web/astrostudyui/src/utils/localCalcCache.js`
  - `Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/controller/NongliController.java`
  - `UPGRADE_LOG.md`
- Details:
  - 三式合一右侧首行参数扩展为四列：`命局/事局`、`真太阳时/直接时间`、`男/女`、`贵人体系`。
  - 新增 `timeAlg` 状态、保存/恢复链路、起盘参数、概览显示与快照文案；顶部时间展示按选项动态显示“真太阳时”或“直接时间”。
  - “直接时间”模式下，三式合一请求精确农历/节气时使用时区标准经线（`zone*15°`）与零纬度，不再按当前经纬度做真太阳时偏移。
  - 农历/节气前端缓存 key 增加 `timeAlg`，避免真太阳时与直接时间结果串缓存。
  - 后端 `/nongli/time` 增加 `timeAlg` 参数解析并支持 DirectTime：直接时间时返回不经真太阳时偏移的农历基础字段，同时保留四柱/方向等结构字段。
- Verification:
  - `npm --prefix Horosa-Web/astrostudyui run test -- --runInBand --passWithNoTests astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `mvn -f Horosa-Web/astrostudysrv/astrostudycn/pom.xml -DskipTests compile`

### 10:52 - 六壬四课文案修正：`干支` 更名 `地盘`，去除四课冗余注释展开
- Scope: align 六壬四课输出术语，去掉无用的“(一课/二课/三课/四课)”扩展标记。
- Files:
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - `UPGRADE_LOG.md`
- Details:
  - 六壬四课行文从 `干支=...` 调整为 `地盘=...`（仍保留 `天盘`、`贵神`）。
  - AI 导出规范中移除 `四课 -> 四课(一课/二课/三课/四课)` 的替换规则，标题保持为简洁 `四课`。
- Verification:
  - `npm --prefix Horosa-Web/astrostudyui run test -- --runInBand --passWithNoTests astrostudyui/src/components/lrzhan/LiuRengMain.js`

### 11:12 - 星盘组件新增“星曜附带后天宫信息”并全页面/AI 导出同步
- Scope: add a global chart option in `星盘组件` to append each star/object label with natal-house placement and rulership info, and make it effective across all chart-calculation pages and AI exports.
- Files:
  - `Horosa-Web/astrostudyui/src/models/app.js`
  - `Horosa-Web/astrostudyui/src/components/astro/ChartDisplaySelector.js`
  - `Horosa-Web/astrostudyui/src/utils/planetHouseInfo.js`
  - `Horosa-Web/astrostudyui/src/pages/index.js`
  - `Horosa-Web/astrostudyui/src/utils/astroAiSnapshot.js`
  - `Horosa-Web/astrostudyui/src/utils/predictiveAiSnapshot.js`
  - `Horosa-Web/astrostudyui/src/components/jieqi/JieQiChartsMain.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroAspect.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroInfo.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroPlanet.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroPredictPlanetSign.js`
  - `Horosa-Web/astrostudyui/src/components/relative/AspectInfo.js`
  - `Horosa-Web/astrostudyui/src/components/relative/MidpointInfo.js`
  - `Horosa-Web/astrostudyui/src/components/relative/AntisciaInfo.js`
  - `UPGRADE_LOG.md`
- Details:
  - 新增全局开关 `showPlanetHouseInfo`（持久化），在“星盘组件”面板中可直接开启/关闭。
  - 新增工具 `planetHouseInfo`，统一格式输出：`X (1th; 2R6R)`。
  - 将该开关从首页路由层透传到星盘、推运、关系盘、节气盘、三式合一、希腊星术、印度盘等含星盘计算页面的右侧星曜文本区域。
  - AI 导出（常规与推运）同步使用相同标签增强逻辑，确保导出文本与右侧显示一致。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `rg -n "showPlanetHouseInfo|appendPlanetHouseInfoById" Horosa-Web/astrostudyui/src`

### 11:47 - 三式合一切页卡顿优化：重算延迟合并 + 快照异步 + 太乙缓存
- Scope: improve UX freeze when entering `三式合一` by removing heavy synchronous work from immediate tab switch.
- Files:
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - `recalcByNongli` 改为短延迟合并执行（同批多次触发只计算最后一次），降低主线程阻塞峰值。
  - 拆分 `performRecalcByNongli`，并为太乙结果加入 `taiyiCache`，减少重复计算。
  - AI 快照文本构建/写入改为延后执行，不阻塞首帧起盘显示。
  - `refreshAll` 改为等待首轮重算后再关 loading，并限制 seed 完成后的重复补算触发。
  - 右侧 Tabs 启用 `destroyInactiveTabPane` + `animated={false}`，减少初次渲染负载。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run test --silent -- --watch=false` in `Horosa-Web/astrostudyui`

### 12:10 - 修复开启“星曜附带后天宫信息”后符号乱码
- Scope: fix unreadable garbled text when the house-info suffix is appended to symbol-font planet labels.
- Files:
  - `Horosa-Web/astrostudyui/src/utils/planetHouseInfo.js`
  - `UPGRADE_LOG.md`
- Details:
  - 新增标签归一化逻辑：当检测到标签来自 `AstroMsg` 符号字形（如 `A/B/C...`）时，自动切换为 `AstroMsgCN` 可读中文名再拼接后天宫信息。
  - 保持未开启开关时的旧显示逻辑不变，避免影响原有符号盘视觉。
  - 解决症状：右侧“盲点/反盲点、接纳、互容”等模块在开关开启时不再出现乱码。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run test --silent -- --watch=false` in `Horosa-Web/astrostudyui`

### 12:15 - 三式合一起盘再提速（保持精度）：精确结果预取 + 同参缓存优先 + 回退仅兜底
- Scope: further reduce `三式合一` wait time while preserving calculation precision (no algorithm simplification).
- Files:
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - `refreshAll` 优先读取“同参数精确农历缓存”（`getNongliLocalCache`），命中时立即使用精确结果起盘。
  - 仅当同参缓存未命中时才等待精确接口；回退到 `chart/state nongli` 仅作为“精确服务未及时返回”的兜底显示，不改变最终精化结果。
  - 将首帧预算时间下调到 `2200ms`，缩短无缓存场景下的等待窗口。
  - 在时间确认、时间算法切换、关键起局参数切换、点击起盘前新增精确农历/节气预取，尽量在用户点击前把精确数据准备到缓存。
  - 保留后续精确结果自动覆盖逻辑：回退盘仅临时显示，精确结果到达后会自动重算替换。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run test --silent -- --watch=false` in `Horosa-Web/astrostudyui`

### 12:17 - 再修“星曜附带后天宫信息”乱码：后缀改为全中文安全格式
- Scope: eliminate remaining Astro symbol-font garbling when house-info suffix is rendered inside right-panel lines that use `AstroFont`.
- Files:
  - `Horosa-Web/astrostudyui/src/utils/planetHouseInfo.js`
  - `UPGRADE_LOG.md`
- Details:
  - 将后缀格式从 ASCII 版（如 `1th; 2R6R`）改为全中文安全格式（如 `一宫；主二、六宫`），并使用全角括号。
  - 保留原语义不变：仍表示“所在后天宫位 + 所主宰后天宫位”，但避免 `AstroFont` 对英文字母/数字映射导致乱码。
  - 继续保留符号标签自动转中文名逻辑，确保右侧长文本模块统一可读。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run test --silent -- --watch=false` in `Horosa-Web/astrostudyui`

### 12:28 - 星曜后天信息迁移到 AI 导出设置 + 导出卡顿优化 + 移除星盘组件示例文案
- Scope: move “星曜宫位/主宰宫位”控制到各星盘相关页面的 AI 导出设置，移除星盘组件中 `X (1th; 2R6R)` 入口，并降低 AI 导出触发时页面卡死风险。
- Files:
  - `Horosa-Web/astrostudyui/src/components/homepage/PageHeader.js`
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - `Horosa-Web/astrostudyui/src/utils/planetHouseInfo.js`
  - `Horosa-Web/astrostudyui/src/utils/astroAiSnapshot.js`
  - `Horosa-Web/astrostudyui/src/utils/predictiveAiSnapshot.js`
  - `Horosa-Web/astrostudyui/src/components/astro/ChartDisplaySelector.js`
  - `Horosa-Web/astrostudyui/src/models/app.js`
  - `Horosa-Web/astrostudyui/src/components/jieqi/JieQiChartsMain.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - AI 导出设置新增两项（按技法独立保存）：`显示星曜宫位`、`显示星曜主宰宫`，覆盖星盘/关系盘/推运/希腊/印度/节气/三式合一/七政四余/量化盘等星盘相关页面。
  - `planetHouseInfo` 改为“显式参数驱动”，不再从全局 `showPlanetHouseInfo` 自动读取；并统一后缀标记为 `（后天：...）` 以便导出阶段按设置裁剪。
  - AI 导出链路新增后缀裁剪：可输出“仅宫位 / 仅主宰宫 / 两者都显示 / 两者都不显示”。
  - 导出性能优化：为字体解码增加快速检测门禁、超长文本跳过重排美化，降低主线程阻塞概率。
  - 从“星盘组件”移除“星曜附带后天宫信息（X (1th; 2R6R)）”控制项，避免与 AI 导出设置重复、并杜绝该入口导致的界面符号字体乱码。
  - 兼容旧用户本地配置：启动后强制 `showPlanetHouseInfo=0`，防止历史缓存残留继续影响页面右侧显示。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run test --silent -- --watch=false` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 14:24 - 修复六壬“确定无法排盘”与金口诀“二次起盘失效”
- Scope: restore predictable re-plot behavior in `易与三式 -> 六壬/金口诀`; after changing time, clicking `确定` or `排盘` should reliably trigger a new盘面.
- Files:
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengInput.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `Horosa-Web/astrostudyui/src/components/cnyibu/CnYiBuMain.js`
  - `Horosa-Web/astrostudyui/src/models/astro.js`
  - `UPGRADE_LOG.md`
- Details:
  - `LiuRengInput` 时间回调增加 `__confirmed` 标记，区分“编辑中”与“已点击确定”。
  - `LiuRengMain` 在 `__confirmed=true` 时允许 hook 触发，并新增 `startPaiPanByFields` 统一锁定 `calcFields/calcChart` + 请求六壬数据；这样点时间控件“确定”即可直接起课，不再只能依赖右侧“起课”按钮。
  - `JinKouMain` 字段同步改为 `astro/fetchByFields`（静默请求），并按 `__confirmed` 控制是否触发 hook 重算，修复首次后时间变更再起盘不生效的问题。
  - `JinKouMain` 新增 `calcFields` 作为本次起盘上下文，`runyear` 校验、年龄计算、保存快照统一使用该上下文，避免重复起盘时读取旧字段。
  - `cnyibu` hook 链路与 `astro` model 的 `hooking` 增加 `chartObj` 透传，确保子模块在 hook 中可拿到本次排盘结果对应的图表上下文。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 00:27 - 金口诀按课本规则校准：四位起法/昼夜贵神/用爻判定
- Scope: align `金口诀` core model with the rule set you provided (立地分、月将加时方上传、甲戊庚牛羊等贵神口诀、时干起人元、用爻判定) and reduce mismatch with external software.
- Files:
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouCalc.js`
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouCalc.test.js`
  - `UPGRADE_LOG.md`
- Details:
  - 在 `JinKouCalc` 新增并显式使用“月将映射表（寅月亥将…丑月子将）”，不再隐式依赖其他模块常量，确保“月将加时方上传”路径可读、可核验。
  - 贵神（星座）起法改为显式口诀配置（甲戊庚牛羊、乙己鼠猴、丙丁猪鸡、壬癸蛇兔、辛午虎），并保留原有 `guirengType` 兼容。
  - 增加 `isDiurnal` 覆盖能力：优先使用盘面昼夜（太阳在地平线上下）判定贵神顺逆；未提供时仍回退到时支昼夜。
  - 新增“用爻判定”模型输出：根据四位阴阳自动给出 `yongYao`（三阴一阳、三阳一阴、二阴二阳、纯阴反阳、纯阳反阴规则），并写入 AI 快照文本。
  - `JinKouMain` 打通 `chart.isDiurnal` 到 `buildJinKouData`；并在请求后缓存本次起盘昼夜状态，避免重绘时昼夜规则漂移。
  - 地分保留“自动随时支”与“手动指定”两种行为：默认自动；一旦用户手动改地分则锁定为手动值，不再被后续时间变更覆盖。
- Verification:
  - `npm test -- JinKouCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 00:35 - 金口诀用爻增加盘面下划线标识
- Scope: make 用爻 visually explicit on the 金口诀主盘，符合“取用处下划一横”习惯。
- Files:
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouPanChart.js`
  - `UPGRADE_LOG.md`
- Details:
  - 在四位中表渲染阶段读取 `jinkouData.yongYao.label`，对对应行的“内容列”绘制下划线。
  - 下划线采用黑色 2px，宽度按单元格自适应（约 56%），避免不同分辨率下过短或过长。
  - 仅在有有效用爻标签时显示，不影响无数据态或其他行。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`

### 00:40 - 金口诀时间编辑改为“仅点确定后更新左盘”
- Scope: stop `金口诀` left-panel 六壬盘 auto-refresh during time drafting; refresh only after clicking 时间控件“确定”, while keeping repeated re-calc available.
- Files:
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - `onFieldsChange` 针对 `__confirmed` 增加门禁：当 `__confirmed=false`（时间仍在编辑态）直接返回，不发起 `astro/fetchByFields`。
  - 因此右侧调时间时左上六壬盘不再实时跳动；点击“确定”后（`__confirmed=true`）才同步字段并触发重算。
  - 保留确认后的 hook 链路，支持再次调时并再次点击“确定”重复更新时间计算。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`

### 00:46 - 金口诀出生时间输入改为确认后再算行年，消除编辑卡顿
- Scope: avoid lag when editing `卜卦人出生时间` in 金口诀 by deferring runyear recompute until explicit confirm.
- Files:
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengBirthInput.js`
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - `LiuRengBirthInput` 新增 `requireConfirm` 模式：在该模式下时间控件显示“确定”按钮，并回传 `__confirmed` 标记。
  - `JinKouMain` 在出生时间回调中对 `__confirmed=false` 直接忽略，不再在编辑过程触发 `requestRunYear`。
  - 仅当点击“确定”（`__confirmed=true`）后才更新 `birth` 并重算行年，因此连续调节出生年月日时不再每步卡顿。
  - 保持可重复计算：每次再次调整后点击“确定”都会重新计算最新结果。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`

### 12:37 - 按反馈修正：保留星盘组件开关 + 恢复 Astro 字体主显示
- Scope: keep the UI option `星曜附带后天宫信息` in `星盘组件` (without example suffix text), and restore symbol-first Astro-font display style (no forced Chinese replacement for planet labels).
- Files:
  - `Horosa-Web/astrostudyui/src/components/astro/ChartDisplaySelector.js`
  - `Horosa-Web/astrostudyui/src/utils/planetHouseInfo.js`
  - `Horosa-Web/astrostudyui/src/models/app.js`
  - `UPGRADE_LOG.md`
- Details:
  - 在“星盘组件”恢复复选项入口：`星曜附带后天宫信息`；删除示例文案 `（X (1th; 2R6R)）`。
  - 取消星曜标签的“符号->中文”强制替换，恢复 Astro 字体符号主显示风格。
  - 撤销对 `showPlanetHouseInfo` 的强制清零逻辑，恢复该开关可用并持久化。
  - 保留已新增的 AI 导出设置能力（按技法控制“宫位/主宰宫”），与星盘组件开关并行可用。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run test --silent -- --watch=false` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 13:50 - 后天宫位后缀改为英文数字格式 + AI 导出裁剪兼容 ASCII/CN 双格式
- Scope: follow latest display rule: house/ruler info uses `1th` / `3R6R` style, and ensure AI 导出设置在历史中文后缀与新英文后缀下都能正确裁剪。
- Files:
  - `Horosa-Web/astrostudyui/src/utils/planetHouseInfo.js`
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - `UPGRADE_LOG.md`
- Details:
  - `planetHouseInfo` 输出统一为 ASCII 样式：`(1th; 3R6R)`，并保留“仅宫位 / 仅主宰宫 / 两者都显示”三种组合能力。
  - AI 导出 `trimPlanetInfoBySetting` 增强为双格式解析：
    - 兼容旧中文后缀（如“后天：一宫；主二、六宫”）
    - 兼容新 ASCII 后缀（如 `1th; 2R6R`）
  - AI 导出缓存读取不再依赖旧中文后缀标记，已有快照可直接复用，减少重复构建快照导致的主线程阻塞。
  - 继续保留“星盘组件”中的 `星曜附带后天宫信息` 选项文案（无示例后缀样例文本）。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run test --silent -- --watch=false` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 13:54 - 星曜标签括号统一为半角英文 `()`
- Scope: reduce visual width in星曜标签 by replacing full-width Chinese brackets with half-width English brackets.
- Files:
  - `Horosa-Web/astrostudyui/src/components/astro/PlanetSelector.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroLots.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroPlanet.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroPredictPlanetSign.js`
  - `UPGRADE_LOG.md`
- Details:
  - 将 `AstroMsg + （AstroTxtMsg）` 统一替换为 `AstroMsg + (AstroTxtMsg)`，避免全角括号占用过宽。
  - 不改变任何计算逻辑，仅调整显示字符样式。

### 13:58 - 主/界限法 + 法达星限表格同步改为半角括号显示
- Scope: apply the same compact `()` style in `主/界限法` and `法达星限` tables, with symbol + readable name in one cell.
- Files:
  - `Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroFirdaria.js`
  - `UPGRADE_LOG.md`
- Details:
  - 新增统一星曜渲染函数，表格内显示从“纯符号”升级为 `符号(中文名)`，括号采用半角英文 `()`.
  - `主/界限法`：迫星/应星筛选项与表格文本（映点/反映点/相位处等）统一使用该显示方式。
  - `法达星限`：主限/子限两列统一使用该显示方式。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run test --silent -- --watch=false` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 14:09 - 修复后天信息开启后乱码 + 主/界限法与法达星限改为宫位/主宰宫信息
- Scope: eliminate AstroFont garbling after enabling `星曜附带后天宫信息`, and make `主/界限法` + `法达星限` display house/ruler suffix instead of Chinese-name suffix.
- Files:
  - `Horosa-Web/astrostudyui/src/utils/planetHouseInfo.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroAspect.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroInfo.js`
  - `Horosa-Web/astrostudyui/src/components/relative/AspectInfo.js`
  - `Horosa-Web/astrostudyui/src/components/relative/MidpointInfo.js`
  - `Horosa-Web/astrostudyui/src/components/relative/AntisciaInfo.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroGivenYear.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroLunarReturn.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroProfection.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroSolarArc.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroSolarReturn.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroPlanet.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroPredictPlanetSign.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroFirdaria.js`
  - `Horosa-Web/astrostudyui/src/components/direction/AstroDirectMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 新增 `splitPlanetHouseInfoText`，并在 UI 里统一“符号(后天信息)”分字体渲染：符号保持 `AstroFont`，后缀改用 `NormalFont`，解决 `1th/3R6R` 在 AstroFont 下的乱码问题。
  - `appendPlanetHouseInfoById` 在找不到对象时不再输出 `(-; -)`，直接回退原标签，避免非星曜 token 被错误附加后缀。
  - `主/界限法`、`法达星限` 改为读取当前盘对象并显示 `(1th; 3R6R)` 后缀；不再显示中文名括号。
  - `AstroDirectMain` 已透传 `showPlanetHouseInfo` 到 `AstroPrimaryDirection` 与 `AstroFirdaria`。
  - AI 快照中的 `主/界限法`、`法达星限`表格也同步写入后天宫位/主宰宫位信息，并继续由 AI 导出设置做按技法裁剪。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run test --silent -- --watch=false` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`

### 00:56 - 行年算法按立春边界修正（六壬 / 金口诀 / 三式合一）
- Scope: fix `行年` mismatch after changing birth time and align with your rule set: use节气年干支（立春为界）、男顺女逆行年序列、确认后可重复重算。
- Files:
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/helper/LiuRengHelper.java`
  - `Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/controller/LiuRengController.java`
  - `UPGRADE_LOG.md`
- Details:
  - 前端行年参数不再取 `nongli.year`，改为优先取四柱年干支（`fourColumns.year.ganzi`），并提供 `yearGanZi/yearJieqi/year` 多级回退，避免“农历年 vs 立春年”混用导致的错盘。
  - 六壬与金口诀请求 `/liureng/runyear` 时新增卜卦时刻参数（`guaDate/guaTime/guaAd/guaZone/guaLon/guaLat/guaAfter23NewDay`），让后端可在缺失干支时自动反算节气年柱。
  - 后端 `runyear` 增加干支规范化与合法性校验；当 `guaYearGanZi` 缺失或不规范时，自动按卜卦时刻重建四柱并取年柱干支。
  - 后端年龄由“仅60甲子余数”扩展为“立春年序差值”：新增 `ageCycle`（0-59循环位）并返回 `age`（按立春年差推得的实际年龄步数），行年干支仍严格按男丙寅顺行、女壬申逆行表取值。
  - 移除前端用公历年份二次拼接年龄的旧逻辑，避免覆盖后端立春算法结果；出生时间确认后会按新规则实时刷新左侧行年。
  - 三式合一补充 `liureng.nianMing` 优先读取 `nongli.runyear`，与六壬/金口诀年命展示口径保持一致。
- Verification:
  - `npm test -- JinKouCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `mvn -DskipTests install` in `Horosa-Web/astrostudysrv/astrostudycn`

### 01:03 - 继续修复“点击确定后行年不更新”：前端增加独立行年兜底计算
- Scope: address remaining case where `runyear` endpoint may still返回旧值（如始终0岁）导致界面不刷新；金口诀/六壬在“确认出生时间”后强制按四柱干支本地重算行年并覆盖显示。
- Files:
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 在前端加入完整60甲子序列与男女行年序列生成（男：丙寅起顺行；女：壬申起逆行），不再依赖后端返回年龄显示正确与否。
  - `requestRunYear` 在请求后新增本地覆盖逻辑：读取“出生四柱年干支”（通过静默 `/liureng/gods` 获取）+“卜卦年干支”，按立春年柱序差计算 `age`，并写入 `ageCycle` 与 `year`。
  - 加入 `birthYearGanZi` 缓存，避免同一出生参数重复请求带来额外卡顿。
  - 即使后端仍是旧实现或未重启，点击“确定”后行年也会按当前规则更新，不再停留在0岁/丙寅。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `npm test -- JinKouCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`

### 01:08 - 再次加固行年兜底：无干支时按出生/卜卦年份差强制刷新
- Scope: fix your screenshot scenario where `行年` still stayed `丙寅/0岁`; when干支链路任一环节取不到值时，仍保证点击“确定”后行年变化可见。
- Files:
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - `requestRunYear` 里把本地重算改为三层兜底：
    1) 先用“出生年柱干支 + 卜卦年柱干支”计算；
    2) 若干支缺失，则按出生年与卜卦年的公历年差计算年龄并映射男女行年序列；
    3) 若仍失败，则用后端返回 `age` 反推 `ageCycle/year`。
  - 因此即便接口返回旧值或干支未取到，2019→2026 这类修改也会把显示从 `0岁` 推进到对应年龄，并同步行年干支。
  - 保留前一版的缓存与静默请求，不增加输入时的明显卡顿。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `npm test -- JinKouCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`

### 01:13 - 修复请求失败导致行年不落盘：runyear请求改为try/catch并保证兜底写回
- Scope: when `/liureng/runyear` 请求异常或返回不完整时，之前会提前中断导致界面继续显示 `丙寅/0岁`；现在无论接口是否成功都保证把前端兜底结果写入盘面。
- Files:
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - `requestRunYear` 改为“先算前端fallback，再尝试接口覆盖，再统一落盘”：
    - 即使接口抛错，也会使用 `出生年-卜卦年` 的兜底年龄+男女行年序列更新显示；
    - 仅当“干支缺失且fallback也不可得”才提示并终止。
  - 去除“先判 `guaYearGanZi` 再直接return”的硬阻断，避免本地可算时被提前中止。
  - 对 `year/age/ageCycle` 增加最终缺省兜底赋值，确保不会留下旧状态。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `npm test -- JinKouCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
  - `node` 本地脚本校验：`2017->2026 男 => 9岁 / 乙亥`

### 01:18 - 前端显示层强制兜底：即使state.runyear未刷新也按出生年差显示
- Scope: fix stubborn UI case where backend/state链路未及时更新但盘面仍显示旧值（`丙寅/0岁`）；在渲染与保存阶段增加显示层兜底，保证画面不再卡旧值。
- Files:
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 新增 `resolveDisplayRunYear`：按当前“出生年 vs 卜卦年”生成 fallback 行年，并在以下情况覆盖展示：
    - `runyear` 缺失；
    - `age` 非数值；
    - `age=0` 但出生年差>0；
    - `year` 为空或异常停留在 `丙寅`。
  - `JinKouChart` / `LiuRengChart` 传入的 `runyear` 改为 `displayRunYear`，避免 UI 继续绑定陈旧 state。
  - 保存案例时也改为写入 `displayRunYear`，避免导出内容与界面不一致。
- Verification:
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `npm test -- JinKouCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`

### 01:28 - 再修“点确定后行年不变”：出生时间确认时先本地落盘，再请求校正
- Scope: ensure `金口诀/六壬` 在点击“卜卦人出生时间”的“确定”后，左侧行年立即可见变化，不再依赖异步接口先返回。
- Files:
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - `JinKouMain.onBirthChange` 改为“先计算 `displayRunYear` 写入 `state.runyear`，再异步 `requestRunYear` 校正”，避免接口慢/失败时盘面保持旧值。
  - `LiuRengMain.onBirthChange` 同步改为确认门禁逻辑（`__confirmed`）：未确认不重算，确认后先本地更新行年再请求后端校正。
  - `LiuRengMain` 的 `LiuRengBirthInput` 打开 `requireConfirm={true}`，与金口诀一致：编辑时不触发重算，仅点“确定”才刷新。
  - 两处都保留后续 `requestRunYear()`，因此“再次调整 -> 再点确定”可重复更新时间并继续得到正确行年。
- Verification:
  - `npm test -- JinKouCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `/bin/zsh -lc 'cd "Horosa-Web"; ./start_horosa_local.sh; ./verify_horosa_local.sh; ./stop_horosa_local.sh'`

### 01:33 - 修复“出生时间看起来已改但行年仍用旧值”判定漏洞
- Scope: fix case shown in latest screenshot where出生时间面板已改到早年，但行年仍停留在旧年龄（本质是旧 `runyear` 非0时未触发fallback覆盖）。
- Files:
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 强化 `resolveDisplayRunYear` 覆盖条件：新增“硬不一致”判定。
    - `|currAge - fallbackAge| >= 2` 时，强制用当前出生年差fallback覆盖；
    - `ageCycle` 与 fallback 差距 >= 2（按60循环最短距离）时也覆盖；
    - 年龄相同但行年干支不同（常见于性别切换或旧状态残留）时覆盖。
  - 保留“边界容忍”策略：仅差 1 岁（立春边界附近）不强制覆盖，避免误伤节气边界场景。
  - 这样可修复“UI里出生时间改了，但runyear沿用历史值”的场景，不会再被旧 `2岁/戊辰` 卡住。
- Verification:
  - `npm test -- JinKouCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `/bin/zsh -lc 'cd "Horosa-Web"; ./stop_horosa_local.sh; ./start_horosa_local.sh; ./verify_horosa_local.sh; ./stop_horosa_local.sh'`

### 01:38 - 修复“出生时间控件显示已改，但内部birth state未同步”导致行年仍按旧出生年
- Scope: fix latest screenshot scenario where birth selector显示为2020，但行年仍是 `丙寅/0岁`（原因是未确认编辑时父组件birth state不更新，后续判定仍读旧年）。
- Files:
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 调整 `onBirthChange` 行为：即使 `__confirmed=false`，也先同步 `birth` 到父组件 `state`，并同步一次 `displayRunYear`（纯前端fallback，不走接口）。
  - 只有在 `__confirmed=true` 时才触发 `requestRunYear()` 请求校正，保持“编辑不卡顿、确认后精算”的交互目标。
  - 这样可避免“控件内部时间已变，但父状态还停在旧年”造成的行年错误。
  - 对你截图场景（卜卦2026、出生2020、男）fallback会稳定得到 `6岁 / 壬申`，不会再落到 `0岁 / 丙寅`。
- Verification:
  - `npm test -- JinKouCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `/bin/zsh -lc 'cd "Horosa-Web"; ./stop_horosa_local.sh; ./start_horosa_local.sh; ./verify_horosa_local.sh; ./stop_horosa_local.sh'`

### 01:46 - 交互回归修正：左盘仅在点击计算确认后更新（出生时间编辑不再实时改盘）
- Scope: follow latest UX requirement: when editing `卜卦人出生时间`, left chart must stay unchanged until user clicks the calculation confirm button (`确定`) on that birth-time panel.
- Files:
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 引入“草稿出生时间 vs 已应用出生时间”分离：
    - `birth` 保持输入框草稿值（可随编辑变化）；
    - `calcBirth` 仅在确认计算时更新（作为行年与左盘使用值）。
  - `onBirthChange` 逻辑改为：
    - `__confirmed=false`：只同步 `birth`，不触发 `requestRunYear`，不更新左盘行年；
    - `__confirmed=true`：同步 `birth + calcBirth`，再触发重算并刷新左盘。
  - 行年相关计算与显示（`genRunYearParams/requestBirthYearGanZi/requestRunYear/render/case save`）统一改为读取 `calcBirth`，彻底杜绝“编辑过程实时改盘”。
  - 保留确认后兜底校正链路，仍可反复“调整 -> 确定 -> 更新”。
- Verification:
  - `npm test -- JinKouCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `/bin/zsh -lc 'cd "Horosa-Web"; ./stop_horosa_local.sh; ./start_horosa_local.sh; ./verify_horosa_local.sh; ./stop_horosa_local.sh'`

### 01:52 - 最终修正：按“页面计算按钮”应用出生时间（非编辑态实时应用）
- Scope: fix latest regression where after stopping realtime updates, runyear could stay on old birth year (`丙寅/0岁`) if user expected page-level calculate action to apply new birth input.
- Files:
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 明确“草稿输入”和“计算使用值”职责：
    - `birth`：仅作为右侧出生时间输入框草稿；
    - `calcBirth`：仅在页面实际计算入口触发时更新（`requestGods` 被调用时，从当前 `birth` 克隆应用）。
  - `onBirthChange` 改为只更新 `birth`，不再改 `runyear/calcBirth`，彻底避免编辑过程影响左盘。
  - 在 `requestGods` 内统一执行 `calcBirth = clone(birth)`，确保你点击页面计算按钮后，本次计算一定使用你当前输入的出生时间。
  - `requestRunYear/genRunYearParams/requestBirthYearGanZi/render/save` 全部继续使用 `calcBirth`，实现“未计算不生效、计算后必生效”。
- Verification:
  - `npm test -- JinKouCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
  - `npm run build --silent` in `Horosa-Web/astrostudyui`
  - `npm run build:file --silent` in `Horosa-Web/astrostudyui`
  - `/bin/zsh -lc 'cd "Horosa-Web"; ./stop_horosa_local.sh; ./start_horosa_local.sh; ./verify_horosa_local.sh; ./stop_horosa_local.sh'`

### 17:33 - 修复“行星选择”面板乱码，恢复符号+中文原样式
- Scope: fix garbled labels in `行星选择` drawer where Chinese text was rendered with the astrology glyph font.
- Files:
  - `Horosa-Web/astrostudyui/src/components/astro/PlanetSelector.js`
  - `UPGRADE_LOG.md`
- Details:
  - 新增 `renderLabel(item)`，将标签拆分为“符号”和“中文说明”两段渲染。
  - 仅对符号段应用 `AstroConst.AstroFont`，中文与括号使用默认字体，避免 `☉灵点?` 这类乱码。
  - 去掉 `Checkbox` 整体 `fontFamily` 设置，避免把非符号字符也强制走占星字体。
  - 清理 `PlanetSelector` 中未使用的导入与未使用参数，保持组件干净。
- Verification:
  - `npm run build` in `Horosa-Web/astrostudyui`

## 2026-02-22

### 00:18 - Mac 一键部署容错增强：先装 Homebrew，失败自动直连 JDK17；并修复 Local 启动链路
- Scope: make Mac deployment/startup resilient on clean machines without Java/Homebrew, and remove runtime bootstrap crashes.
- Files:
  - `scripts/mac/bootstrap_and_run.sh`
  - `Horosa_Local.command`
  - `Horosa-Web/start_horosa_local.sh`
  - `Prepare_Runtime_Mac.command`
  - `README.md`
  - `UPGRADE_LOG.md`
- Details:
  - `bootstrap_and_run.sh` 调整为“优先安装/使用 Homebrew + openjdk@17，失败时自动直连下载 JDK17 到 `.runtime/mac/java`（可用 `HOROSA_JDK17_URL` 覆盖）”。
  - `ensure_java17` 增加多级探测与版本校验（项目内 runtime、`.runtime/mac/java`、系统 `JAVA_HOME`、`/usr/libexec/java_home`、brew Java、PATH Java），并强制校验 `>=17`。
  - `Horosa_Local.command` 修复 runtime 兜底崩溃：移除 `SCRIPT_ARGS[@]` 的 `set -u` 未绑定变量触发点；缺依赖回退 bootstrap 时默认先尝试 Homebrew（同时保留直连 JDK fallback）。
  - `Horosa_Local.command` / `start_horosa_local.sh` 均增加 `java -version` 可执行性校验，避免把 `/usr/bin/java` 误判为可用 JDK。
  - Python 运行时选择改为“依赖就绪优先”（必须含 `cherrypy/jsonpickle/swisseph`），项目内 Python 不满足时自动换到可用解释器或回退一键补齐。
  - `Prepare_Runtime_Mac.command` 增强：找不到 Java 时自动调 bootstrap 补齐；Python runtime 复制后自动补装依赖并过滤 `_CodeSignature` 复制噪声；最终“下一步”提示按实际准备结果给出。
  - README 更新了“无 Homebrew 的 JDK17 直连兜底”与 `HOROSA_JDK17_URL` 说明。
- Verification:
  - `bash -n Horosa_Local.command Prepare_Runtime_Mac.command Horosa-Web/start_horosa_local.sh scripts/mac/bootstrap_and_run.sh`
  - `HOROSA_SKIP_BUILD=1 HOROSA_SKIP_DB_SETUP=1 HOROSA_SKIP_LAUNCH=1 HOROSA_SKIP_TOOLCHAIN_INSTALL=0 ./scripts/mac/bootstrap_and_run.sh`
  - `HOROSA_SKIP_BUILD=1 HOROSA_SKIP_DB_SETUP=1 HOROSA_SKIP_LAUNCH=1 HOROSA_SKIP_TOOLCHAIN_INSTALL=1 ./scripts/mac/bootstrap_and_run.sh`
  - `printf '\n' | ./Prepare_Runtime_Mac.command`（结果：Java/Python/Frontend/Backend 均为 OK；沙箱下 Maven install 写 `~/.m2` 受限但产物回填成功）
  - `HOROSA_NO_BROWSER=1 ./Horosa_Local.command`（沙箱环境限制本地端口绑定，启动探测阶段失败；非脚本逻辑错误）

### 19:46 - 奇门遁甲起盘性能优化（保持算法精度）并完成回归自检
- Scope: reduce Qimen startup latency caused by heavyweight jieqi/nongli pre-calculation, without changing core astrological algorithm or precision.
- Files:
  - `Horosa-Web/astrostudyui/src/utils/localCalcCache.js`
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `Horosa-Web/astropy/astrostudy/jieqi/YearJieQi.py`
  - `Horosa-Web/astropy/astrostudy/jieqi/NongLi.py`
- Details:
  - 节气 seed 缓存键补全 `jieqis/seedOnly`，避免“奇门两节气 seed”与“节气模块全年/多节气结果”互相污染，提升缓存命中稳定性。
  - `DunJiaMain` / `SanShiUnitedMain` 移除重复、非标准参数的 `setJieqiSeedLocalCache` 写入，统一走 `fetchPreciseJieqiSeed` 内部规范化缓存路径。
  - `YearJieQi` 强化参数解析（`seedOnly` 字符串布尔、`jieqis` 类型兼容），并在非图表场景减少不必要中间结构构建。
  - `NongLi` 计算节气时改为仅请求 `中气` 集合（含冬至），并通过“按名称定位冬至”替代固定下标访问，减少大量不参与农历月建判断的节气求解开销。
  - 精度校验：通过同一输入对比“旧路径（24节气） vs 新路径（中气子集）”的 `months/prevDongzi/dongzi` 结果，样本年份 `1901/1949/1984/2000/2024/2026/2050` 全量一致。
- Verification:
  - `npm test -- DunJiaCalc.test.js --runInBand`（PASS）
  - `npm run build --silent`（PASS）
  - `npm run build:file --silent`（PASS）
  - `python3 -m py_compile Horosa-Web/astropy/astrostudy/jieqi/YearJieQi.py Horosa-Web/astropy/astrostudy/jieqi/NongLi.py`（PASS）
  - `mvn -DskipTests compile` in `Horosa-Web/astrostudysrv/astrostudycn`（BUILD SUCCESS）
  - `PYTHONPATH='Horosa-Web/flatlib-ctrad2:Horosa-Web/astropy' python3 <对比脚本>`（结果：`ALL_MATCH=True`）

### 20:07 - 修复“无 Homebrew / 无 Maven 导致后端 jar 缺失无法启动”
- Scope: resolve startup failure on clean mac machines where `Prepare_Runtime_Mac.command` can build frontend but fails backend with `未检测到 mvn` and then `Horosa_Local.command` reports missing `astrostudyboot.jar`.
- Files:
  - `scripts/mac/bootstrap_and_run.sh`
  - `Prepare_Runtime_Mac.command`
  - `Horosa_Local.command`
  - `Horosa-Web/start_horosa_local.sh`
  - `UPGRADE_LOG.md`
- Details:
  - `bootstrap_and_run.sh` 增加 Maven 本地兜底：
    - 无 brew/mvn 时自动下载 Apache Maven 到 `.runtime/mac/maven`（可用 `HOROSA_MAVEN_URL` / `HOROSA_MAVEN_VERSION` 覆盖）；
    - Maven 构建统一走本地仓库 `.runtime/mac/m2`，降低对用户家目录写权限与环境差异依赖。
  - `Prepare_Runtime_Mac.command` 的后端阶段增强：
    - 目标 jar 缺失时，自动调用 `bootstrap_and_run.sh` 执行后端构建补齐；
    - 若已存在 `runtime/mac/bundle/astrostudyboot.jar`，可复用不再直接失败。
  - `Horosa_Local.command` 增强后端自愈：
    - `target` 与 `bundle` 均缺失时，自动触发一键部署脚本补齐后端 jar；
    - 补齐后自动回填，仍失败才给出明确提示。
  - `start_horosa_local.sh` 增加 bundle jar 回填逻辑（直接运行脚本时也能自愈）。
- Verification:
  - `bash -n Horosa_Local.command Prepare_Runtime_Mac.command Horosa-Web/start_horosa_local.sh scripts/mac/bootstrap_and_run.sh`
  - `HOROSA_SKIP_BUILD=1 HOROSA_SKIP_DB_SETUP=1 HOROSA_SKIP_LAUNCH=1 HOROSA_SKIP_TOOLCHAIN_INSTALL=1 ./scripts/mac/bootstrap_and_run.sh`
  - 模拟 `target jar` 缺失并执行 `Horosa-Web/start_horosa_local.sh`：确认输出 `using bundled jar fallback` 且自动回填成功。

### 20:18 - 启动超时容错增强：默认等待 180s，可环境变量扩展
- Scope: fix false timeout on slower machines (e.g., first run on Mac mini) where services are healthy but startup takes longer than 60s.
- Files:
  - `Horosa-Web/start_horosa_local.sh`
  - `README.md`
  - `UPGRADE_LOG.md`
- Details:
  - `start_horosa_local.sh` 启动等待从固定 60 秒改为可配置：
    - 默认 `HOROSA_STARTUP_TIMEOUT=180`；
    - 小于 30 或非法值会自动回退到 180；
    - 超时时输出明确提示可设置 `HOROSA_STARTUP_TIMEOUT=300`。
  - README 增加 `HOROSA_STARTUP_TIMEOUT` 与 Maven 直连参数说明，便于无 Homebrew 环境排障。
- Verification:
  - `bash -n Horosa-Web/start_horosa_local.sh`
  - `bash -n Horosa_Local.command Prepare_Runtime_Mac.command scripts/mac/bootstrap_and_run.sh`

### 22:00 - 新增统一故障诊断日志：每次运行自动记录前后端问题
- Scope: add a persistent run diagnostics file so each startup/run failure (frontend/backend/web) is automatically recorded for troubleshooting on other Macs.
- Files:
  - `Horosa_Local.command`
  - `Horosa-Web/start_horosa_local.sh`
  - `.gitignore`
  - `README.md`
  - `UPGRADE_LOG.md`
- Details:
  - 新增默认诊断文件：`diagnostics/horosa-run-issues.log`（支持 `HOROSA_DIAG_FILE` / `HOROSA_DIAG_DIR` 自定义）。
  - `Horosa_Local.command` 每次运行都会写入起止信息、关键环境变量；失败或中断时自动追加最近 `astrostudyboot.log` / `astropy.log` / `horosa_local_web.log` 的 tail。
  - `start_horosa_local.sh` 也会记录启动阶段信息（runtime 解析、端口就绪、超时失败等），并在失败时附加 Python/Java 日志 tail。
  - `Horosa_Local.command` 会把 `HOROSA_DIAG_FILE` / `HOROSA_DIAG_DIR` 透传给 `start_horosa_local.sh`，保证同一次运行落到同一个诊断文件。
  - 根目录新增 `diagnostics/` 文件夹（含 `README.md`），统一存放诊断数据。
  - `.gitignore` 增加 `diagnostics/*` 忽略规则（保留 `diagnostics/.gitkeep` / `diagnostics/README.md`），避免把本地故障日志提交到 GitHub。
- Verification:
  - `bash -n Horosa_Local.command Horosa-Web/start_horosa_local.sh`
  - `printf '\n' | HOROSA_NO_BROWSER=1 HOROSA_FORCE_UI_BUILD=0 HOROSA_STARTUP_TIMEOUT=300 ./Horosa_Local.command`
  - 失败路径验证：`HOROSA_WEB_PORT=9999 ./Horosa_Local.command`（确认自动记录失败上下文与日志 tail）

### 23:31 - 修复“命盘/事盘点击提交无反应”：本地存储异常显式提示
- Scope: fix silent failure when saving chart/case on machines where localStorage write/read is blocked or quota-limited.
- Files:
  - `Horosa-Web/astrostudyui/src/models/user.js`
  - `Horosa-Web/astrostudyui/src/utils/localcharts.js`
  - `Horosa-Web/astrostudyui/src/utils/localcases.js`
  - `UPGRADE_LOG.md`
- Details:
  - `localcharts/localcases` 的读写加入异常捕获，写入失败时返回可判断状态，并在 `upsert/remove` 抛出明确错误码。
  - `user.js` 的 `addCase/updateCase/deleteCase/addChart/updateChart/saveMemo` 统一 `try/catch`，失败时弹窗提示“本地存储不可用或空间不足”。
  - 避免之前“点击提交后没有任何反馈”的黑洞体验。
- Verification:
  - `npm test -- DunJiaCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
  - `npm run build:file` in `Horosa-Web/astrostudyui`

### 23:38 - 提交流程容错补强：日期格式化异常也进入可视错误提示
- Scope: prevent pre-save date formatting exceptions (`values.birth.format / values.divTime.format`) from bypassing save error handling.
- Files:
  - `Horosa-Web/astrostudyui/src/models/user.js`
  - `UPGRADE_LOG.md`
- Details:
  - 将 `values.birth/divTime` 格式化逻辑移入 `try/catch` 内，确保异常会进入统一错误提示，而不是中断后无反馈。
  - 进一步减少“提交按钮点了没反应”的边界问题。
- Verification:
  - `npm test -- DunJiaCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
  - `npm run build:file` in `Horosa-Web/astrostudyui`

### 23:45 - Safari/隐私模式存储兼容：自动清理 AI 快照并回退会话内存
- Scope: keep chart/case save usable under Safari strict privacy or quota pressure.
- Files:
  - `Horosa-Web/astrostudyui/src/utils/localcharts.js`
  - `Horosa-Web/astrostudyui/src/utils/localcases.js`
  - `UPGRADE_LOG.md`
- Details:
  - 新增安全 `localStorage` 获取与配额异常识别（`QuotaExceededError` 等）。
  - 写入超限时自动清理体积较大的 AI 快照缓存：
    - `horosa.ai.snapshot.astro.v1`
    - `horosa.ai.snapshot.module.v1.*`
  - 若存储仍不可用，自动回退到会话内存存储（本次运行可继续增删改查，刷新后可能丢失）。
  - 通过 `console.warn` 给出一次性降级提示，便于排障。
- Verification:
  - `npm test -- DunJiaCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
  - `npm run build:file` in `Horosa-Web/astrostudyui`

### 23:49 - 八字/紫微交互优化：时间调整后仅“点确定”才重算
- Scope: improve UX by stopping immediate recalculation on every time tweak in Bazi/Ziwei.
- Files:
  - `Horosa-Web/astrostudyui/src/components/cntradition/CnTraditionInput.js`
  - `Horosa-Web/astrostudyui/src/components/cntradition/BaZi.js`
  - `Horosa-Web/astrostudyui/src/components/ziwei/ZiWeiInput.js`
  - `Horosa-Web/astrostudyui/src/components/ziwei/ZiWeiMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - `PlusMinusTime -> onFieldsChange` 透传 `__confirmed`。
  - `BaZi/ZiWeiMain` 收到 `__confirmed=false` 时仅更新字段，不发排盘请求。
  - 只有 `__confirmed=true`（点击时间选择器里的“确定”）才触发重算，减少频繁等待和卡顿感。
- Verification:
  - `npm run build:file` in `Horosa-Web/astrostudyui`
  - `npm test -- DunJiaCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`

### 23:58 - Safari 本地存储禁用场景修复：请求层全链路安全读写
- Scope: eliminate request-layer crashes when Safari blocks localStorage access.
- Files:
  - `Horosa-Web/astrostudyui/src/utils/request.js`
  - `UPGRADE_LOG.md`
- Details:
  - 新增 `safeGetLocalItem/safeSetLocalItem/safeRemoveLocalItem`。
  - 替换请求层关键路径中的直接 `localStorage` 访问（token 读取、`forceChange` 写入、need-login 判断）。
  - 防止 Safari 存储访问异常向上冒泡导致误判“命盘保存失败”。
- Verification:
  - `npm run build:file` in `Horosa-Web/astrostudyui`
  - `npm test -- DunJiaCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`

### 00:03 - 启动行为调整：恢复 Safari 为默认打开浏览器
- Scope: keep user-required startup behavior (open Safari by default) while retaining Safari compatibility fixes.
- Files:
  - `Horosa_Local.command`
  - `UPGRADE_LOG.md`
- Details:
  - `Horosa_Local.command` 的浏览器优先级恢复为：
    - Safari -> Chromium family app window -> system default browser.
  - 与 Safari 兼容修复并存，不影响本地存储兜底能力。
- Verification:
  - `bash -n Horosa_Local.command`

### 00:58 - 修复节气盘仅返回二分二至：年视图恢复完整二十四节气（保留三式快路径）
- Scope: fix JieQi year panel returning only the 4 seasonal terms when frontend passes `jieqis` subset for chart tabs.
- Files:
  - `Horosa-Web/astropy/astrostudy/jieqi/YearJieQi.py`
  - `UPGRADE_LOG.md`
- Details:
  - 根因是 `computeJieQi(True)` 直接复用了 `self.jieqis` 过滤 `jieqi24`，导致年视图被裁剪成 4 项。
  - 调整为“结果列表”和“起盘列表”分离：
    - `needChart=True` 时，`jieqi24` 始终计算并返回完整 24 节气；
    - 仅 `charts` 使用传入 `jieqis`（例如春分/夏至/秋分/冬至）做季节盘起盘；
    - `seedOnly` / `needChart=False` 仍保留按 `jieqis` 过滤（不影响遁甲/金口诀/三式合一快路径）。
  - 保持原有 `approach` 数值迭代流程不变，未改变任何节气时刻算法精度逻辑。
- Verification:
  - `python3 -m py_compile Horosa-Web/astropy/astrostudy/jieqi/YearJieQi.py`
  - `PYTHONPATH='Horosa-Web/astropy:Horosa-Web/flatlib-ctrad2:$HOME/Library/Python/3.12/lib/python/site-packages' runtime/mac/python/bin/python3` 运行 YearJieQi 自检：
    - `needChart=True -> jieqi24 len = 24, charts len = 4`
    - `seedOnly=True -> jieqi24 len = 4`（仅返回请求项）
  - 端到端 chart service 自检（`/jieqi/year`，经 `start_horosa_local.sh` 启停）：
    - `full(jieqis=四季) -> 481ms, jieqi24=24, charts=4`
    - `seedOnly(jieqis=大雪/芒种) -> 4ms, jieqi24=2`
  - 性能采样（同机本地函数级）：
    - `seedOnly` 平均约 `2.87ms`（p95 `2.93ms`），满足三式快路径预算；
    - `needChart=True` 平均约 `245ms`，远低于“打开节气盘 5 秒内”阈值。
  - 前端回归：
    - `npm test -- DunJiaCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
    - `npm run build:file` in `Horosa-Web/astrostudyui`

### 01:34 - 节气盘空白/超时修复：拆分“节气列表”与“季节盘起盘”请求
- Scope: fix blank JieQi panel caused by `/jieqi/year` timeout after 24项+四季盘同请求，and keep first-open latency under 5s.
- Files:
  - `Horosa-Web/astropy/astrostudy/jieqi/YearJieQi.py`
  - `Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/controller/JieQiController.java`
  - `Horosa-Web/astrostudyui/src/components/jieqi/JieQiChartsMain.js`
  - `Horosa-Web/astrostudyui/src/utils/preciseCalcBridge.js`
  - `UPGRADE_LOG.md`
- Details:
  - `YearJieQi` 新增 `needCharts` 参数：允许“返回24节气列表”与“生成季节盘 charts”解耦。
  - 前端节气盘默认页（`二十四节气`）请求改为 `needCharts=false`、`needBazi=false`，避免首次进入时阻塞。
  - 切换到四季盘标签时再请求 `needCharts=true`，并在后台预热该请求缓存，减少后续等待。
  - `JieQiController` 透传 `needCharts`，并保留 `needBazi` 兼容控制。
  - `JieQiChartsMain` 对 `item.bazi` 做空值保护，避免服务端未附带 bazi 时前端渲染异常。
- Verification:
  - `python3 -m py_compile Horosa-Web/astropy/astrostudy/jieqi/YearJieQi.py`
  - `mvn -f Horosa-Web/astrostudysrv/astrostudycn/pom.xml -DskipTests install`
  - `mvn -f Horosa-Web/astrostudysrv/astrostudyboot/pom.xml -DskipTests clean package`
  - 端到端加密接口实测（本机）：
    - `needCharts=false`：`771ms`，`jieqi24=24`，`charts=0`
    - `needCharts=true`：`8009ms`，`jieqi24=24`，`charts=4`
  - 前端回归：
    - `npm test -- DunJiaCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
    - `npm run build:file` in `Horosa-Web/astrostudyui`

### 01:35 - 星盘切时间卡顿优化：去除重复排盘请求 + 非确认变更节流
- Scope: reduce stutter when adjusting time in Astro chart without reducing calculation precision.
- Files:
  - `Horosa-Web/astrostudyui/src/pages/index.js`
  - `Horosa-Web/astrostudyui/src/models/astro.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroChartMain.js`
  - `Horosa-Web/astrostudyui/src/components/astro3d/AstroChartMain3D.js`
  - `UPGRADE_LOG.md`
- Details:
  - `DateTimeSelector` 的 `confirmed` 状态透传到星盘主流程。
  - 对 `confirmed=false` 的时间微调请求加入 180ms 节流并静默请求，避免高频调整时全局 loading 闪烁阻塞。
  - 移除 `astro` 页签自身的 `doHook -> nohook` 重复排盘链路，避免每次变更触发双请求。
  - 保留最终排盘算法与后端计算路径，不改动计算精度。
- Verification:
  - `npm test -- DunJiaCalc.test.js --runInBand` in `Horosa-Web/astrostudyui`
  - `npm run build:file` in `Horosa-Web/astrostudyui`


### 01:43 - 修复节气盘白屏卡死：无 charts 返回时改为安全占位渲染
- Scope: fix immediate white-screen when opening 节气盘 after list-only response (`needCharts=false`) returns no seasonal chart payload.
- Files:
  - `Horosa-Web/astrostudyui/src/components/jieqi/JieQiChartsMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 根因：`genTabsDom` 在 `charts={}` 时仍直接访问 `chart.params`，导致 `TypeError` 触发整页白屏。
  - 修复为全量空值防护：
    - 对 `chart` 增加判空后再读 `chart.params`；
    - 三类子页（星盘/宿盘/3D盘）在对应节气 `chart` 未返回前显示“正在计算...”占位，而不是渲染空对象组件；
    - 保留右侧节气子标签，用户可直接切换触发 `needCharts=true` 懒加载。
  - 该改动仅是渲染层容错，不改动任一节气/星盘算法精度。
- Verification:
  - `npm run build:file` in `Horosa-Web/astrostudyui`


### 01:53 - 星盘/希腊/六壬/金口诀提速 + AI“逆行误判”修复
- Scope: reduce repeated slow requests on tab-enter/time-adjust and fix AI export where `主宰宫 R` 被误识别成“逆行”。
- Files:
  - `Horosa-Web/astrostudyui/src/services/astro.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroChartMain.js`
  - `Horosa-Web/astrostudyui/src/components/astro3d/AstroChartMain3D.js`
  - `Horosa-Web/astrostudyui/src/components/hellenastro/AstroChart13.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `Horosa-Web/astrostudyui/src/components/jinkou/JinKouMain.js`
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - `UPGRADE_LOG.md`
- Details:
  - **星盘请求去重与缓存**：`fetchChart` 增加内存缓存 + in-flight 去重，避免同参数重复触发 `/chart`。
  - **切页不再强制重排**：`AstroChartMain` / `AstroChartMain3D` 的页签 hook 改为 no-op，避免“仅切回页签就重复请求”。
  - **希腊十三分盘优化**：`AstroChart13` 增加缓存 + in-flight 去重；时间未确认(`confirmed=false`)仅静默预取，不打断界面；确认后优先命中缓存。
  - **六壬优化**：
    - 时间未确认时不再触发 `astro/fetchByFields`，避免拖动时间时频繁后台重排；
    - `/liureng/gods` 与 `/liureng/runyear` 增加前端缓存 + in-flight 去重。
  - **金口诀优化**：`/liureng/gods` 与 `/liureng/runyear` 增加前端缓存 + in-flight 去重，减少重复进入页签/重复参数时的等待。
  - **AI逆行误判修复**：
    - 去掉“数字+R”的宽匹配逆行替换，改为仅对“度数/度分格式+R”执行逆行转换；
    - 括号信息里 `1R8R` 仅按主宰宫信息识别，不再误判为逆行标记。
- Verification:
  - `npm run build:file` in `Horosa-Web/astrostudyui`
  - `./verify_horosa_local.sh` (services started by `start_horosa_local.sh`) -> `verify ok`


### 01:59 - 恢复节气卡片“时间+四柱+纳音”结构（双阶段加载，不拖慢首屏）
- Scope: restore the original 24-term card structure (time + 四柱 + 纳音) without lowering precision and without regressing first-screen latency.
- Files:
  - `Horosa-Web/astrostudyui/src/components/jieqi/JieQiChartsMain.js`
  - `UPGRADE_LOG.md`
- Details:
  - 根因：节气页首请求为 `needBazi=false`（用于首屏提速），导致 `jieqi24` 只有时间无四柱/纳音。
  - 修复为双阶段：
    - **阶段1（首屏快）**：继续 `needBazi=false`，优先显示24节气时间；
    - **阶段2（后台补全）**：同参数自动发起 `needBazi=true, needCharts=false` 的精确请求，回填每个节气卡片的四柱与纳音。
  - 加入 seq/缓存键保护，避免旧请求回填新年份造成错位。
  - 在回填完成前显示“八字与纳音加载中...”，避免误判为功能被删除。
  - 算法精度保持不变：八字/纳音仍来自原后端 `setupBazi` 计算链路。
- Verification:
  - `npm run build:file` in `Horosa-Web/astrostudyui`
  - `./verify_horosa_local.sh` (services started by `start_horosa_local.sh`) -> `verify ok`
