# Horosa Web 项目结构（GitHub 上传版）

更新时间：2026-02-27

## 1) 根目录（入口）

- `Horosa_OneClick_Mac.command`：Mac 一键部署+启动主入口
- `Horosa_Local.command`：已安装依赖后的快速启动入口（含 `/static/umi.*` 白屏兼容补丁）
- `Horosa_Local_Windows.bat` / `Horosa_Local_Windows.ps1`：Windows 启动入口
- `Prepare_Runtime_Mac.command` / `Prepare_Runtime_Windows.*`：离线 runtime 打包脚本
- `README.md`：部署和上传说明
- `PROJECT_STRUCTURE.md`：目录结构说明（本文件）

## 2) 主业务代码

- `Horosa-Web/`

### 2.1 前端（Umi/React）

- `Horosa-Web/astrostudyui/src/`：前端业务源码
- `Horosa-Web/astrostudyui/public/`：静态资源
- `Horosa-Web/astrostudyui/dist-file/`：构建产物（GitHub 版默认不提交）
- `Horosa-Web/astrostudyui/node_modules/`：依赖目录（不提交）
- `Horosa-Web/astrostudyui/src/components/tongshefa/TongSheFaMain.js`：统摄法主模块（四卦选择、本卦/互潜/错亲盘式、三十二观/三界/爻位/纳甲筮法、事盘保存、AI快照）
- `Horosa-Web/astrostudyui/src/components/cnyibu/CnYiBuMain.js`：易与三式子菜单入口（已新增“统摄法”标签）
- `Horosa-Web/astrostudyui/src/utils/localcases.js`：本地事盘类型映射（已新增 `tongshefa`）
- `Horosa-Web/astrostudyui/src/utils/aiExport.js`：AI导出技术识别与分段导出（已新增统摄法导出链路）

### 2.2 Java 后端（Maven 多模块）

- `Horosa-Web/astrostudysrv/`
  - 关键模块：`boundless`、`basecomm`、`image`、`astrostudy`、`astrostudycn`、`astroreader`、`astrodeeplearn`、`astroesp`、`astrostudyboot`
  - 启动 Jar：`Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar`（构建产物，不提交）

### 2.3 Python 图表服务

- `Horosa-Web/astropy/astrostudy/`：算法实现
- `Horosa-Web/astropy/websrv/`：服务入口
- 主入口：`Horosa-Web/astropy/websrv/webchartsrv.py`

### 2.4 本地运行脚本（主工程内）

- `Horosa-Web/start_horosa_local.sh`
- `Horosa-Web/stop_horosa_local.sh`
- `Horosa-Web/verify_horosa_local.sh`

## 3) 自动化脚本（新增整理）

- `scripts/mac/bootstrap_and_run.sh`
  - Mac 首次自动安装依赖、构建、启动的核心脚本
- `scripts/requirements/mac-python.txt`
  - Mac Python 依赖清单
- `scripts/repo/clean_for_github.sh`
  - 清理 node_modules/target/runtime/logs，准备上传 GitHub

## 4) runtime 与缓存目录

- `runtime/README.md`：runtime 说明
- `runtime/*`：离线打包产物目录（默认不提交）
- `.runtime/`：一键脚本生成的本地 Python venv（默认不提交）
- `.runtime/mac/node/`：一键部署在 Homebrew 不可用时直连安装的 Node runtime（默认不提交）
- `.runtime/mac/python/`：一键部署在 Homebrew 不可用时直连安装的 Python runtime（Miniconda，默认不提交）

## 5) modules（扩展参考资料）

- `modules/fengshui/naqi/`
- `modules/reference/kintaiyi-master/`
- `modules/reference/xuan-utils-pro-master/`
- `modules/reference/zhong-zhou-zi-wei-dou-shu-2/`

## 6) 建议检索路径

- 改前端页面：`Horosa-Web/astrostudyui/src/components/`
- 改前端模型：`Horosa-Web/astrostudyui/src/models/`
- 改后端接口：`Horosa-Web/astrostudysrv/astrostudyboot/`
- 改 Python 服务：`Horosa-Web/astropy/websrv/`
- 排查启动日志：`Horosa-Web/.horosa-local-logs/`

## 7) 本次性能修复说明（结构层）

- 未新增第三方依赖包；一键部署脚本与依赖清单无需额外安装步骤。
- 节气计算性能关键路径位于：
  - `Horosa-Web/astropy/astrostudy/jieqi/YearJieQi.py`
  - `Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/controller/JieQiController.java`
- 节气页面展示链路（前端拆分“全24节气卡片”与“图盘子集异步加载”）位于：
  - `Horosa-Web/astrostudyui/src/components/jieqi/JieQiChartsMain.js`
- 统一参数哈希缓存层位于：
  - `Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/helper/ParamHashCacheHelper.java`

## 8) 本次统摄法新增结构（2026-02-23）

- 页面入口：
  - `Horosa-Web/astrostudyui/src/components/cnyibu/CnYiBuMain.js` -> `TabPane tab="统摄法" key="tongshefa"`
- 统摄法主实现：
  - `Horosa-Web/astrostudyui/src/components/tongshefa/TongSheFaMain.js`
  - 含：本卦/互潜/错亲矩阵、边框显示开关、四位卦象下拉、三十二观/三界/爻位/纳甲筮法、事盘保存与回填。
- 事盘类型与模块快照：
  - `Horosa-Web/astrostudyui/src/utils/localcases.js`（caseType + label 映射）
  - `Horosa-Web/astrostudyui/src/utils/moduleAiSnapshot.js`（复用模块快照存储，统摄法使用 `module=tongshefa`）
- AI 导出链路：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - 已支持：技术识别 `tongshefa`、导出分段 `本卦/六爻/潜藏/亲和`、旧分段名兼容映射（互潜->潜藏，错亲->亲和，统摄法起盘->本卦）。

## 9) 本次六壬格局参考新增结构（2026-02-25）

- 六壬页面主实现：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - 新增：右栏底部 `大格/小局` 双标签、六壬格局匹配引擎、匹配结果卡片展示、AI 快照同步分区。
  - 修复：`起课` 时可读取未确认时间草稿并同步排盘，不再依赖先点“确定”。
  - 二次加严：`三交/游子/解离/乱首/孤寡/龙战/赘婿` 等小局触发条件改为强约束组合匹配，降低宽松误命中。
  - 文案升级：改为文献原文块（诗诀 + 荀注 + 要点/依据），去除“主象/判词/风险/建议”模板文案。
  - 文案对齐（续）：`大格/小局` 其余条目荀注已按 `12. 大格.md` 与 `13. 小局.md` 逐字回填；`局式/局义/局注` 与荀注合并同块展示，保持右栏与 AI 导出一致。
  - 小局全收录：匹配条目由 15 条提升至 62 条（含 `旺孕/德孕/二烦/天祸/天寇/天狱/死奇/魄化/三阴/富贵/天合局/宫时局/北斗局` 全部缺口），并保持 `泆女+狡童` 双项可判。
  - 规则口径加严：新增日月支、节气、昨日干支、旬内天干映射、宫时孟仲季叠合、斗罡落位等上下文字段；小局匹配改为按 `13. 小局.md` 局式计算，不再停留在 41 条简化版。
  - 自检覆盖：`XIAO_JU_META`、`XIAO_JU_REFERENCE_TEXT`、`matchXiaoJuReferences` 三处键集合已对齐（62/62/62）。
- 六壬输入组件：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengInput.js`
  - 新增 `timeHook` 透传，供父组件在点击 `起课` 时读取当前时间编辑值。
- AI 导出链路：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - 六壬 AI 导出设置预设分区：`起盘信息`、`大格`、`小局`（已移除 `分类占`）。

## 10) 本次遁甲八宫新增结构（2026-02-25）

- 遁甲页面主实现：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - 右侧标签改为：`概览`、`神煞`、`八宫`（已移除原 `状态` 与 `历法` 标签，内容并入 `概览`）。
  - `八宫` 标签新增宫位按钮顺序：`乾/坎/艮/震/巽/离/坤/兑`，点击宫位后显示五段内容：
    - 奇门吉格（名称）
    - 奇门凶格（名称）
    - 十干克应（天盘干 + 地盘干）
    - 八门克应与奇仪主应（人盘门 + 地盘本位门；人盘门 + 天盘干）
    - 八神加八门（当前宫八神 + 当前宫八门）
- 遁甲八宫规则模块：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaBaGongRules.js`
  - 统一承载八宫规则映射与判定逻辑，供界面展示与 AI 快照导出复用。
- 遁甲 AI 快照导出：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaCalc.js`
  - 快照新增 `[八宫详解]` 分区，并按八宫输出对应计算结果。
- AI 导出设置：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - 遁甲预设分区新增 `八宫详解`，与新增快照分区保持同步。

## 11) 本次六壬宫时局算法修正（2026-02-25）

- 六壬页面主实现：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - 宫时局匹配口径从“孟仲季全盘轮转泛化”改为用户指定直判：
    - `绛宫时`：登明（亥）加四仲（子午卯酉）；
    - `明堂时`：神后（子）加四仲（子午卯酉）；
    - `玉堂时`：大吉（丑）加四仲（子午卯酉）。
  - 右栏命中证据文案改为“X加四仲”表达，减少误触发歧义。
  - `绛宫时/明堂时/玉堂时` 的 `局式/局义/局注` 已按用户给定原文更新，保持详情展示与 AI 快照一致。
- 一致性校验：
  - 小局三处键集合（`XIAO_JU_META`、`XIAO_JU_REFERENCE_TEXT`、`matchXiaoJuReferences`）仍保持 `62/62/62` 对齐，无新增缺口。

## 12) 本次遁甲八宫展示优化（2026-02-25）

- 遁甲页面主实现：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - 八宫右栏由连续文本改为板块卡片式布局（风格对齐六壬大格/小局）：
    - `奇门吉格`
    - `奇门凶格`
    - `十干克应`
    - `八门克应和奇仪主应`
    - `八神加八门`
  - 删除“第一部分/第二部分…”等编号文案。
  - 删除“当前宫位：X9宫”行，避免无依据宫位数字在右栏出现。
  - 删除八宫顶部冗余说明卡文案，仅保留核心结果板块。
- 八宫规则快照输出：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaBaGongRules.js`
  - 八宫快照标题从 `X9宫` 调整为 `X宫`，与页面展示口径统一。

## 13) 六壬宫时局命中修复（2026-02-25）

- 六壬小局匹配实现：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - 宫时局条件修正为“天盘加临地盘”直判（使用 `upDownMap` 逆查）：
    - `绛宫时`：天盘 `亥` 加临地盘四仲；
    - `明堂时`：天盘 `子` 加临地盘四仲；
    - `玉堂时`：天盘 `丑` 加临地盘四仲。
  - 移除此前“月将+时支”临时判定，恢复宫时局在小局栏的正常命中展示。

## 14) 六壬小局展示分栏优化（2026-02-25）

- 六壬页面主实现：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - 在“格局参考”Tabs 中新增 `参考` 标签页（位于 `小局` 右侧）。
  - 将 `始终/迍福/刑德`（键：`shizhong`/`tunfu`/`xingde`）从 `小局` 视图分流到 `参考` 视图。
  - 两个标签页沿用同一张卡片样式与命中依据展示，保证视觉一致。

## 15) 遁甲八宫吉凶格释义展示（2026-02-25）

- 八宫规则与展示实现：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaBaGongRules.js`
  - 新增吉凶格释义映射：
    - `QIMEN_JIGE_INTERPRETATION`
    - `QIMEN_XIONGGE_INTERPRETATION`
  - `buildQimenBaGongPanelData` 返回新增字段：
    - `jiPatternDetails`（`格名：释义`）
    - `xiongPatternDetails`（`格名：释义`）
  - 八宫快照 `[八宫详解]` 的吉凶格输出改为多行 `- 格名：释义`。
- 遁甲页面 UI：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - 八宫页 `奇门吉格/奇门凶格` 改为逐条展示“格名：释义”，不再仅显示格名。

## 16) 遁甲八宫释义显示开关（2026-02-25）

- 遁甲页面 UI：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - 新增 `showPatternInterpretation` 展示状态（默认开启）。
  - 在“换日/经纬度选择”区域中，新增按钮 `释义：是/否`，位于“经纬度选择”左侧。
  - 八宫 `奇门吉格/奇门凶格` 根据开关切换显示模式：
    - 开：`格名：释义`
    - 关：仅格名

## 17) 遁甲释义开关本地持久化（2026-02-25）

- 遁甲页面 UI：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - 新增本地持久化键：`qimenShowPatternInterpretation`。
  - 页面加载时读取本地值作为 `showPatternInterpretation` 初始状态；无值默认开启。
  - 点击“释义：是/否”时同步写入本地存储，刷新后保持上次选择。

## 18) 遁甲奇门演卦（2026-02-25）

- 八宫规则模块：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaBaGongRules.js`
  - 新增门卦映射与六十四卦名映射。
  - 新增 `buildQimenFuShiYiGua(pan)`：
    - 值符值使演卦：地盘值符宫为内卦、天盘值使宫为外卦。
  - `buildQimenBaGongPanelData` 新增：
    - `menFangYiGua`
    - `menFangYiGuaText`
    - 用于八宫“门方演卦例”展示。
- 遁甲页面展示：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - 概览新增：`奇门演卦`（符使演卦）。
  - 八宫每个宫位最下方新增板块：`奇门演卦`（门方演卦）。
- 快照导出：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaCalc.js`
  - `buildDunJiaSnapshotText` 增加概览演卦行；`[八宫详解]` 增加每宫“奇门演卦（门方）”。

## 19) AI导出分区同步补齐（2026-02-25）

- 六壬快照与导出：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - 快照分区改为：
    - `[大格]`
    - `[小局]`（主小局）
    - `[参考]`（始终/迍福/刑德分流）
- 遁甲快照与导出：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaCalc.js`
  - 新增独立分区 `[奇门演卦]`（值符值使演卦）；门方演卦继续在 `[八宫详解]` 分宫输出。
- AI 导出设置预设：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - `liureng` 预设分区新增 `参考`。
  - `qimen` 预设分区新增 `奇门演卦`。

## 20) 六壬参考常驻条目（2026-02-25）

- 六壬小局匹配与分栏：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `参考` 分流键新增：`wuqi`（物气）、`xingu`（新故）。
  - 常驻参考键集合为：`wuqi`、`xingu`、`tunfu`、`shizhong`、`xingde`。
  - 对上述五键启用“未命中也补入”机制，确保在“参考”标签始终可见；其余小局维持盘式条件命中。

## 21) 六壬“入课传”严判边界修正（2026-02-25）

- 六壬小局匹配实现：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `courseBranches` 边界收紧为“四课上下神 + 三传地支”，移除此前混入的扩展位（如行年/贵人）。
  - 所有依赖“入课传”语义的条目随之统一严判（含 `三奇/六仪/游子/孤寡/官爵` 等），避免出现“左盘无此局式仍命中”的误报。

## 22) 遁甲吉凶格算法二次严判（2026-02-25）

- 八宫规则实现：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaBaGongRules.js`
  - 按上传术文对吉格/凶格判定做二次收紧，重点包括：
    - `天遁/地遁/人遁/鬼遁/云遁/龙遁/虎遁` 的门、神、宫位与干组合条件；
    - `三奇得使` 收紧为“日干映射三奇 + 地盘值使门宫 + 对应地干组合”；
    - `玉女守门` 使用“值使门加丁奇 + 时干映射 + 指定时辰补例”联合判定；
    - `三奇入墓` 收紧为 `乙坤、丙乾、丁艮`。
- 格名补齐：
  - 吉格新增：`青龙回首`、`飞鸟跌穴`。
  - 凶格新增：`青龙逃走`、`白虎猖狂`、`螣蛇夭矫`、`朱雀投江`、`太白火荧`、`荧入太白`、`飞宫格`、`伏宫格`、`大格`、`小格`、`天网四张格`、`地罗遮格`。
  - `伏吟/返吟` 格名与文献口径统一（替代旧命名 `门伏吟/门反吟`）。
- 释义联动：
  - 新增与重命名格名均补齐 `QIMEN_JIGE_INTERPRETATION` / `QIMEN_XIONGGE_INTERPRETATION`，确保“格名：释义”与算法输出一致。

## 23) 六壬三光与天合局严判修正（2026-02-25）

- 小局匹配实现：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `三光` 从“偏宽松”改为“硬条件”：
    - 日干、日支、初传三者均需旺相；
    - 三传神将需全为吉神（贵人、六合、青龙、太常、太阴、天后）；
    - 保留日辰与发用无硬克约束。
  - `XIAO_JU_META.sanguang.condition` 同步更新为上述判定口径。
- 天合局判定扩展：
  - 新增天合规则集（甲己、乙庚、丙辛、丁壬、戊癸）统一驱动匹配。
  - 命中源由扩展到原文强调的三类显位：
    - 同课上下相合；
    - 三传有合；
    - 日干与日支上神有合，或日支与日干上神有合。
  - 新增上下课天干对、日支旬干、天合天干池等上下文字段用于证据回溯与界面展示。

## 24) 六壬十二盘式判定接入（2026-02-25）

- 新增盘式算法模块：
  - `Horosa-Web/astrostudyui/src/components/liureng/LRPanStyle.js`
  - 提供统一方法 `resolveLiuRengTwelvePanStyle(yueBranch, timeBranch)`。
  - 基于 `distance = (月将序 - 占时序 + 12) % 12` 映射十二式：
    - 伏吟、进连茹、进间传、生胎、顺三合、四墓覆生、反吟、四绝体、逆三合、病胎、退间传、退连茹。
- 六壬盘中心展示链路：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengChart.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/RengChart.js`
  - `Horosa-Web/astrostudyui/src/components/liureng/LRCommChart.js`
  - `Horosa-Web/astrostudyui/src/components/liureng/LRChart.js`
  - `Horosa-Web/astrostudyui/src/components/liureng/LRInnerChart.js`
  - `Horosa-Web/astrostudyui/src/components/liureng/LRCircleChart.js`
  - 在天地盘中心区 `XX课` 下新增第三行盘式文案（`XX式`），圆盘/方盘均一致。
- AI 导出与设置同步：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
    - 快照新增独立分区 `[十二盘式]`；
    - `[起盘信息]` 增加 `十二盘式` 摘要行。
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
    - `liureng` 预设分区新增 `十二盘式`，导出设置可单独勾选。

## 25) 六壬神将悬浮窗与“概览”条目（2026-02-25）

- 神将文档模块化：
  - `Horosa-Web/astrostudyui/src/components/liureng/LRShenJiangDoc.js`
  - 汇总《神》《将》两章核心数据：
    - 12神神义摘要；
    - 12将“临十二神”判词；
    - 将名归一（如 `贵人→天乙`、`玄武→元武`）。
  - 导出 `buildLiuRengHouseTipObj`，统一生成“天盘神 + 地盘神”双层悬浮窗内容。
- 六壬盘悬浮窗接入：
  - `Horosa-Web/astrostudyui/src/components/liureng/LRCommChart.js`
  - `Horosa-Web/astrostudyui/src/components/liureng/LRChart.js`
  - `Horosa-Web/astrostudyui/src/components/liureng/LRCircleChart.js`
  - `Horosa-Web/astrostudyui/src/components/graph/D3Circle.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/RengChart.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengChart.js`
  - 方盘/圆盘的神将区块均可 hover 出现文档浮窗，内容明确区分天盘神、地盘神。
- 六壬右栏“概览”：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - 在 `参考` 右侧新增 `概览` Tab，展示：
    - `天将发用来意诀`
    - `天将杂主吉凶`
  - 匹配基于当前盘的 `发用` 与 `日干上神`，并附命中依据。
- AI 导出同步：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
    - 快照新增 `[概览]` 分区。
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
    - `liureng` 预设分区新增 `概览`。

## 26) 六壬/遁甲格局算法严检收口（2026-02-25）

- 六壬小局收紧：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `三阳` 按局式收紧为：贵人顺治 + 日干/日支在贵人前 + 日干/日支/初传皆旺相。
  - `富贵` 收紧为：贵人所乘旺相 + 贵人临核心位 + 三传皆生旺。

- 遁甲八宫收紧：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaBaGongRules.js`
  - `三奇得使` 与 `玉女守门` 去除非原文扩展条件，按上传术文主条件判定。
  - `伏吟/返吟` 由“门单判”改为“门+星联合判定”。
  - `时干入墓` 改为固定五个时干支硬触发（戊戌、壬辰、丙戌、癸未、丁丑）。
  - `门迫/门受制` 使用五行克制硬判（门克宫 / 宫克门）。
  - `星门入墓` 改为“星+门+宫位”联合匹配；`三奇受制` 改为奇墓/击刑/迫制联合判定。

## 27) 六壬原文荀注回填与依据口径修正（2026-02-25）

- 六壬主实现：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `XIAO_JU_REFERENCE_TEXT` 大规模回填为长版原文（含 `增注`），不再使用摘要化短注。
  - 回填覆盖面：
    - 淫泆局、新孕局、隐匿局、乖别局、凶否局、吉泰局、五行局、天合局、宫时局、北斗局相关条目。

- 依据展示与命中逻辑：
  - **罗网**：
    - 命中口径由“同位”扩展为“同位 + 上神加临”双通道；
    - 依据拆分为“命中地位 / 命中上神”两行输出。
  - **概览**：
    - 按 `group + name` 合并同名条目，避免重复卡片；
    - 合并后依据并集去重，确保多条依据完整保留。
  - **乱首/赘婿依据文案**：
    - 修正法一/法二“临”方向描述，统一为与盘面上下神关系一致的表述。

- 变更登记：
  - `UPGRADE_LOG.md` 已同步新增对应记录，便于后续追溯“原文回填 + 判定修正 + 展示修正”。

## 28) 六壬神/将浮窗文案升级（2026-02-25）

- 资料与渲染：
  - `Horosa-Web/astrostudyui/src/components/liureng/LRShenJiangDoc.js`
  - 十二神条目升级为文档化结构字段：`title/month/verse1/verse2/desc/symbol`（对应《神》章）。
  - 标题改为优先文档标题（如 `登明亥神`、`河魁戌神`）。
- 十二将浮窗口径：
  - 保留：`天盘神`、`地盘神`、两盘对应判词。
  - 移除：`天盘神义/地盘神义` 展示行，避免与需求冲突。

## 29) 遁甲时间显示与快照导出同步（2026-02-25）

- 遁甲主界面：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - 左盘顶部与右侧概览统一显示：
    - `直接时间`
    - `真太阳时`
  - 增强 `parseDisplayDateHm` 兼容多种时间格式，减少空值显示。
- 快照导出：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaCalc.js`
  - `[起盘信息]` 新增：
    - `直接时间`
    - `真太阳时`
    - `计算基准`

## 30) AI 导出缺段补齐机制（遁甲/六壬）（2026-02-25）

- 导出实现：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
- 遁甲：
  - 旧缓存缺段时，自动从当前页面补齐：
    - `奇门演卦`
    - `八宫详解`
  - 过滤兜底新增保留项：`奇门演卦`、`八宫详解`。
- 六壬：
  - 旧缓存缺段时，自动从右侧四个标签补齐：
    - `大格`
    - `小局`
    - `参考`
    - `概览`
- 通用：
  - 新增分段存在性检测与内容合并函数，避免“缓存优先导致新分段导不出”。

## 31) timeAlg 与真太阳时显示解耦（2026-02-25）

- 遁甲与三式合一：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
- 修正内容：
  - 删除“选直接时间时改用时区中央经线”的地理参数替换逻辑。
  - `timeAlg` 仅用于计算基准切换；
  - 左侧显示用 `真太阳时` 始终基于真实经纬度计算，不随该选项被改写。

## 32) 三式合一参数区布局调整（2026-02-25）

- 右侧参数布局：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
- 调整：
  - 将原先分两行的参数合并到同一行四列：
    - `时计太乙`
    - `太乙统宗`
    - `回归黄道`
    - `整宫制`

## 33) 六壬/遁甲导出源切换为计算快照（2026-02-25）

- 导出实现：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
- 调整要点：
  - `extractLiuRengContent` 与 `extractQiMenContent` 不再从右侧DOM采集文本。
  - 导出仅使用“计算阶段快照”：
    - 本地模块快照：`loadModuleAISnapshot(module)`；
    - 当前案例快照兜底：`currentCase.payload.snapshot`。
  - 无快照时不再DOM拼装补齐，避免“右侧展示态”影响导出原文排版。

## 34) AI导出去“右侧栏目”与原始段落排版（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaCalc.js`
- 结构调整：
  - 新增 `AI_EXPORT_FORBIDDEN_SECTIONS`：
    - 当前对 `liureng/qimen/sanshiunited` 禁止导出 `[右侧栏目]`。
  - 新增导出净化函数：
    - `getForbiddenSectionSet(key)`
    - `stripForbiddenSections(content, key)`
  - 导出流水更新：
    - `buildPayload` 在分段过滤前先执行 `stripForbiddenSections`；
    - `applyUserSectionFilter` 在“无用户设置”及“有设置”两条路径都执行禁用分段剔除。
  - 导出设置选项源更新：
    - `getOptionsForTechniqueKey` 会过滤禁用分段，避免设置面板再次出现“右侧栏目”。
  - 奇门分段映射兼容：
    - 旧分段名 `概览/右侧栏目` 映射到 `盘面要素`；
    - 预设分段改为 `起盘信息/盘型/盘面要素/奇门演卦/八宫详解/九宫方盘`。
  - 文本整形策略：
    - `normalizeText` 对 `liureng/qimen/sanshiunited` 走“保留原始段落”分支，避免统一转`-`列表。
  - 快照分段命名：
    - `buildDunJiaSnapshotText` 将 `[右侧栏目]` 改为 `[盘面要素]`。

## 35) 真太阳时显示与时间算法彻底解耦（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaCalc.js`
- 结构调整：
  - 遁甲与三式合一新增显示用参数构造函数：
    - `buildDisplaySolarParams(params)`：固定 `timeAlg=0`。
  - 新增显示真太阳时解析链路：
    - `resolveDisplaySolarTime(params, primaryResult)`。
    - 当用户选择`直接时间`时，额外获取`timeAlg=0`对应的`birth`作为显示值。
  - 状态与缓存签名新增字段：
    - `displaySolarTime`进入组件状态；
    - 遁甲盘缓存键 / 重算签名纳入该字段，避免缓存命中导致旧显示残留。
  - 盘面写入口径变更：
    - `calcDunJia`的`realSunTime`优先取`context.displaySolarTime`，其次才回退`nongli.birth`。
- 行为结果：
  - `timeAlg`仍仅决定盘面计算基准；
  - 左盘与概览里的“真太阳时”不再被“直接时间”按钮覆盖。

## 36) 导出前模块快照强制刷新（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
- 结构调整：
  - AI导出新增导出前刷新函数：
    - `requestModuleSnapshotRefresh(moduleName)`；
    - 在`extractLiuRengContent`、`extractQiMenContent`中先触发刷新事件再读取模块快照。
  - 六壬组件新增事件监听：
    - 监听`horosa:refresh-module-snapshot`；
    - 当`detail.module==='liureng'`时调用`saveLiuRengAISnapshot`即时重写快照。
  - 遁甲组件新增事件监听：
    - 当`detail.module==='qimen'`时重写当前`pan`快照。
  - 分段兼容：
    - `aiExport.mapLegacySectionTitle`中补充六壬旧分段名`三传(初传/中传/末传) -> 三传`。
- 行为结果：
  - 六壬导出优先使用当前盘即时快照，降低读取旧案例快照导致“格局参考缺失”的概率。

## 37) 三式合一重算容错兜底（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
- 结构调整：
  - `recalcByNongli` 调度回调加入异常捕获：
    - 任一子步骤报错时，重算 Promise 仍可正常结束，不阻塞后续刷新。
  - `performRecalcByNongli` 中太乙计算改为可降级：
    - `calcTaiyiPanFromKintaiyi` 异常时返回 `taiyi=null`，其余盘继续渲染。
  - `refreshAll` 增加“空盘兜底二次重算”：
    - 当异步重算未产生变更且当前 `dunjia` 为空时，立即执行一次同步重算。
- 行为结果：
  - 三式合一不会因单一子模块异常直接落入“暂无三式合一数据”空态。

## 38) AI导出实时快照回传链路（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js`
- 结构调整：
  - `aiExport.requestModuleSnapshotRefresh(moduleName)` 从“仅派发通知”升级为“派发+回收实时文本”：
    - 事件 `detail` 新增 `snapshotText` 回传槽。
  - `extractQiMenContent`/`extractLiuRengContent` 数据源优先级更新：
    - 实时回传快照（刷新后） > 模块缓存快照 > `window.__horosa_*_snapshot_text` > 旧缓存兜底。
    - 核心分段缺失时不再直接信任旧缓存（遁甲看`[奇门演卦]/[八宫详解]`，六壬看`[大格]/[小局]/[参考]/[概览]`）。
  - 遁甲组件新增回传能力：
    - `saveQimenLiveSnapshot` 返回快照文本并记录 `window.__horosa_qimen_snapshot_at`；
    - 在 `horosa:refresh-module-snapshot` 中回填 `evt.detail.snapshotText` 并重写模块快照。
  - 六壬组件新增回传能力：
    - `saveLiuRengAISnapshot` 改为返回快照文本；
    - 在刷新事件中回填 `evt.detail.snapshotText`。
- 行为结果：
  - 导出触发时优先拿当前盘实时文本，降低“八宫详解/格局参考偶发缺失”风险。
- 本地运行包同步：
  - `runtime/mac/bundle/dist-file/` 已与 `Horosa-Web/astrostudyui/dist-file/` 同步；
  - 运行时入口脚本更新为 `umi.3fc83e7f.js`。

## 39) 真太阳时显示二次请求容错（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
- 结构调整：
  - 两处 `resolveDisplaySolarTime` 统一改为：
    - 先读 `getNongliLocalCache(timeAlg=0)`（缓存命中直接返回）；
    - 缓存未命中再请求 `fetchPreciseNongli(timeAlg=0)`；
    - 请求异常时回退主请求时间，不抛错。
- 行为结果：
  - “显示真太阳时”的辅助请求不再影响主盘计算成功与否；
  - 三式合一不会再因该辅助请求失败而出现“暂无三式合一数据”空白；
  - 在缓存命中场景减少一次额外接口调用，避免不必要时延。
- 本地运行包同步：
  - `runtime/mac/bundle/dist-file/` 已同步为最新构建，入口脚本更新为 `umi.c3707dd4.js`。

## 40) 修复后自检流程（2026-02-25）

- 自检入口与脚本：
  - `Horosa-Web/verify_horosa_local.sh`
  - `Horosa-Web/astrostudyui/.tmp_horosa_perf_check.js`
- 自检范围：
  - 本地服务端口（8899/9999）可用性；
  - 关键接口链路（`/nongli/time`、`/jieqi/year`、`/liureng/gods`）；
  - 前端单元测试（`umi-test`）；
  - 前端构建产物与运行目录一致性（`dist-file` -> `runtime/mac/bundle/dist-file`）。
- 当前基线结果：
  - 单测 `3/3` 套件通过，`16/16` 用例通过；
  - 接口 smoke/perf 检查通过；
  - 运行端页面脚本版本：`umi.c3707dd4.js`。

## 41) 三式合一时区标准化修复（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
- 结构调整（仅三式合一）：
  - 新增时区标准化链路：
    - `parseZoneOffsetHour`：兼容 `+08:00`、纯数字、`UTC/GMT`、`东/西X区`；
    - `normalizeZoneOffset`：统一输出 `±HH:mm`。
  - 请求参数入口改造：
    - `onTimeChanged`
    - `getTimeFieldsFromSelector`
    - `genParams`
    - `genJieqiParams`
  - 以上路径全部保证发送到精确历法服务的 `zone` 为合法格式。
- 行为结果：
  - 修复三式合一“精确历法服务不可用”假阳性；
  - 避免因 `zone=8/东8区` 导致 `/nongli/time` 失败；
  - 遁甲模块逻辑保持不变（按要求未改）。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.6bdb560e.js`。

## 42) 精确历法桥接层参数归一（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/preciseCalcBridge.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
- 结构调整：
  - 在桥接层新增统一归一化方法：
    - `normalizeZone`：兼容 `+08:00` / `8` / `UTC+8` / `东8区`，统一输出 `±HH:mm`；
    - `normalizeAd`：兼容 `AD/BC/1/-1`，并按日期符号兜底；
    - `normalizeBit`：统一布尔/数值开关到 `0/1`。
  - 请求参数入口统一：
    - `fetchPreciseNongli`、`fetchPreciseJieqiYear`、`fetchPreciseJieqiSeed`
      都在“缓存键构建、缓存读写、网络请求”前三步先做归一化。
  - 三式合一参数口径补齐：
    - `SanShiUnitedMain.genParams` 新增 `ad` 字段透传。
- 行为结果：
  - 彻底避免 `zone` 被透传为单字符导致 `/nongli/time` 抛出
    `StringIndexOutOfBounds(begin 1, end 3, length 1)`；
  - 即使上层模块传入历史格式时区，也能稳定拿到精确历法结果。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.88aa4eb2.js`。

## 43) 三式合一 displaySolarTime 与排盘解耦（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
- 结构调整：
  - `getCachedDunJia` 恢复旧稳定口径：
    - 移除 `displaySolarTime` 参数；
    - 缓存键不再包含显示时间；
    - 调用 `calcDunJia` 时不再把显示时间写入上下文。
  - `performRecalcByNongli` 改为“两段式”：
    - 先得到 `panRaw`（纯计算结果）；
    - 再覆盖 `realSunTime` 为 `displaySolarTime`（纯展示字段）。
  - 新增 `normalizeCalcFieldsForDunJia`：
    - 在三式合一调用遁甲计算前统一 `date/time/zone/ad` 输入格式；
    - 降低 `DateTime` 类型漂移导致的重算异常。
- 行为结果：
  - 修复“显示真太阳时”改动影响三式合一排盘的问题；
  - 三式合一继续支持“直接时间/真太阳时”双时间显示，同时计算路径保持稳定。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.9107fbb7.js`。

## 44) 三式合一失败提示可观测性增强（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
- 结构调整：
  - `refreshAll` catch 分支对非精确历法异常输出具体 `error.message`：
    - 从固定文案“请重试”改为带原因提示，便于定位真实失败点。
- 行为结果：
  - 用户端可直接看到导致三式合一失败的具体错误文本；
  - 减少“无法复现/无法定位”的来回排查成本。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.8191667a.js`。

## 45) 三式合一稳定回退：撤销 displaySolarTime 主链路（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
- 结构调整：
  - `refreshAll` 不再在主流程中额外请求/注入 `displaySolarTime`；
  - `recalcByNongli`、`performRecalcByNongli` 恢复为稳定签名（不携带显示时间参数）；
  - 三式合一内部对 `this.state.options` 统一增加空值兜底；
  - 修正 `overrideOptions` 为空时的读取路径，避免 `taiyiStyle` 空对象异常。
- 行为结果：
  - 修复三式合一报错：`null is not an object (evaluating 'n.taiyiStyle')`；
  - 三式合一起盘链路回到稳定计算路径，不再因显示时间分支中断。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.62edd81c.js`。

## 46) 遁甲左盘日期渲染兼容短年份（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
- 结构调整：
  - `parseDisplayDateHm` 的年份解析改为可变位数（非固定4位）；
  - `getBoardTimeInfo` 统一通过解析函数生成日期/时间，不再使用固定下标切片。
- 行为结果：
  - 输入 `100`、`999` 等短年份时，左侧盘头日期不再显示 `日期--`；
  - 保持 `直接时间/真太阳时` 展示逻辑不变。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.25ee3d4c.js`。

## 47) 三式合一顶部日期行统一与双时间显示解耦（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.less`
- 结构调整：
  - 顶部“日期”行改为同一文本节点输出，统一字号；
  - 直接时间显示改为 `HH:mm:ss`，真太阳时显示改为 `HH:mm:ss`；
  - 新增 `displaySolarTime` 显示状态与 `resolveDisplaySolarTime`（仅用于显示层）；
  - `displaySolarTime` 不参与三式合一主排盘重算签名与计算上下文。
- 行为结果：
  - 左盘日期行固定输出：`年-月-日 真太阳时：XX:XX:XX 直接时间：XX:XX:XX`；
  - 右侧时间算法选择仍决定实际排盘计算基准；
  - 页面稳定性保持，不回引此前 `n.taiyiStyle` 崩溃问题。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.34a10371.js`，样式为 `umi.b7659491.css`。

## 48) 遁甲/三式合一时间算法对齐八字紫微口径（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaCalc.js`
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`
- 结构调整：
  - `DunJiaCalc.buildGanzhiForQimen` 升级为 `buildGanzhiForQimen(nongli, dateParts, opts, context)`：
    - 引入 `parseDateTimeText / resolveCalcDateTime`；
    - 当 `timeAlg=0` 时按真太阳时文本解析小时用于时柱计算；
    - 当 `timeAlg=1` 时按直接时间口径（并保留精确历法时柱优先兜底）；
    - 年/月/日/时支持从 `nongli.bazi.fourColumns` 读取兜底。
  - `SanShiUnitedMain.getQimenOptions` 增加 `timeAlg` 透传：
    - 三式合一右侧“真太阳时/直接时间”选择可直接影响遁甲子模块计算。
  - `DunJiaMain` 的盘头时间解析增强：
    - `parseDisplayDateHm` 支持可变位数年份；
    - `getBoardTimeInfo` 使用解析兜底，避免短年份出现 `日期--`。
- 行为结果：
  - 遁甲与三式合一的时间算法行为与八字/紫微一致：右侧选项直接影响实际计算口径；
  - 真太阳时与直接时间可同时显示，且在小时跨界时可驱动时柱变化；
  - 短年份（<4位）盘头日期显示恢复稳定。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.01433c13.js`，样式为 `umi.b7659491.css`。

## 49) 三式合一顶部神煞列宽调整（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.less`
- 结构调整：
  - `.topBox` 两列布局由 `1fr 174px` 改为 `minmax(0, 1fr) 148px`；
  - 固定收窄右侧“神煞双列”区域，释放左侧“日期/真太阳时/直接时间”行的可用宽度。
- 行为结果：
  - 三式合一盘左上“日期行”更易完整显示；
  - 不影响排盘计算、数据结构与右侧参数面板逻辑。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.01433c13.js`，样式为 `umi.4fac2da6.css`。

## 50) 奇门遁甲取象悬浮窗（干/门/星/神）接入（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/dunjia/QimenXiangDoc.js`
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`
- 结构调整：
  - 新增 `QimenXiangDoc.js`：
    - 内置并解析 `4.取象 1.md` 全文（十天干/八门/九星/八神）；
    - 解析规则支持 `#` 标题、`####` 子标题、空行、分割线；
    - 子标题在渲染层按“标题 + 分割线”展示；
    - 提供 `buildQimenXiangTipObj` 与 `formatQimenDocLineToHtml`（保留 `<font>` 与 `**加粗**`）。
  - `DunJiaMain.js`：
    - 引入 `Popover`；
    - 新增 `renderQimenDocPopover` / `renderQimenHoverNode`；
    - 在宫格中将天盘干、地盘干、八神、九星、八门节点统一接入 hover 悬浮窗口。
- 行为结果：
  - 奇门遁甲盘实现与六壬/紫微一致的“鼠标悬停看释义”交互；
  - 支持干、门、星、神四类取象；原文条目不删减并可滚动查看。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.e9018768.js`，样式为 `umi.4fac2da6.css`。

## 51) 奇门悬浮窗繁体安全转简（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/dunjia/QimenXiangDoc.js`
- 结构调整：
  - 新增 `SAFE_TRAD_TO_SIMP_MAP` + `toSafeSimplified`，以白名单方式做繁体转简体；
  - `normalizeText`（索引匹配）与 `formatQimenDocLineToHtml`（悬浮窗正文渲染）统一复用该转换链路；
  - 规避语义误转：不引入 `乾 -> 干` 这类破坏术数语义的替换。
- 行为结果：
  - 奇门干/门/星/神悬浮窗显示为更一致的简体文本；
  - 术数关键字保持原义，避免误读。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.c042ba38.js`，样式为 `umi.4fac2da6.css`。

## 52) 占星“行星”白屏与希腊点标题排版修复（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/astro/AstroPlanet.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroLots.js`
- 结构调整：
  - `AstroPlanet` 修正实例方法绑定：`genPlanetsDom.bind(this)`，防止 Tab 懒加载时进入“行星”页触发 `this` 为空。
  - `AstroLots` 新增 `renderTitle`：
    - 符号（`AstroMsg`）用 `AstroFont`；
    - 名称（`AstroTxtMsg/AstroMsgCN`）用 `NormalFont`；
    - 占位符符号 `{` 不再显示。
  - 移除 `AstroLots` Card 根级 `AstroFont`，避免希腊点标题与正文挤压重叠。
- 行为结果：
  - 占星页点击“行星”不再白屏；
  - 希腊点列表标题恢复可读，不再全部挤成一团。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.21875f3f.js`，样式为 `umi.4fac2da6.css`。

## 53) 占星图释义悬浮开关（星/宫/座/相）接入（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/astro/ChartDisplaySelector.js`
  - `Horosa-Web/astrostudyui/src/models/app.js`
  - `Horosa-Web/astrostudyui/src/pages/index.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroChart.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroDoubleChart.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroChartCircle.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroMeaningData.js`
- 结构调整：
  - 新增 app 级别配置项 `showAstroMeaning`，并纳入 `GlobalSetup` 持久化。
  - 星盘组件抽屉新增勾选项：`是否显示星/宫/座/相释义`（最下方）。
  - `AstroChartCircle` 新增 `setShowAstroMeaning(flag)`：
    - 开启时为行星/宫位 tooltip 追加释义正文；
    - 开启时给星座环与相位线附加 tooltip；
    - tooltip 样式扩展为宽版可滚动容器，支持长文本。
  - `AstroDoubleChart` 由 `AstroHelper.drawDoubleChart` 迁移为 `AstroChartCircle.drawDoubleChart`，统一单盘/双盘的 tooltip 行为。
  - `AstroMeaningData.js` 更新为完整释义数据集：
    - 行星（太阳、月亮、水星、金星、火星、木星、土星、天王、海王、冥王、北交、南交）；
    - 星座（白羊至双鱼）；
    - 宫位（1th~12th）；
    - 相位（0/30/45/60/90/120/135/150/180）。
- 行为结果：
  - 关闭开关：保持当前基础显示（中文名 + 黄经信息）；
  - 开启开关：鼠标悬停星/宫位/星座/相位可见完整释义悬浮窗，覆盖占星单盘与双盘页面。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.cc6e307f.js`，样式为 `umi.4fac2da6.css`。

## 54) 占星释义原文直存解析（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/astro/AstroMeaningData.js`
- 结构调整：
  - 引入 `RAW_ASTRO_REFERENCE` 保存用户提供的星/星座/宫位释义原文；
  - 通过 `extractBetween + blockToMeaning` 按起止标记切块，构建行星/星座/宫位释义映射；
  - 不再对原文进行简写改写或内容压缩。
- 行为结果：
  - Tooltip 展示数据来源于原文文本本体；
  - 保留原文层级与措辞，减少“参考文本被改动”的风险。
- 运行包同步：
  - `runtime/mac/bundle/dist-file/index.html` 当前入口脚本为 `umi.caedc923.js`，样式为 `umi.4fac2da6.css`。

## 55) 占星释义开关全模块同步（含推运/量化表格，2026-02-25）

- 目标文件（核心）：
  - `Horosa-Web/astrostudyui/src/pages/index.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroMeaningPopover.js`（新增）
  - `Horosa-Web/astrostudyui/src/components/astro/AstroMeaningData.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroChartMain.js`
  - `Horosa-Web/astrostudyui/src/components/astro3d/AstroChartMain3D.js`
  - `Horosa-Web/astrostudyui/src/components/direction/AstroDirectMain.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroFirdaria.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroAspect.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroPlanet.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroLots.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroInfo.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroDoubleChartMain.js`
  - `Horosa-Web/astrostudyui/src/components/relative/AspectInfo.js`
  - `Horosa-Web/astrostudyui/src/components/relative/MidpointInfo.js`
  - `Horosa-Web/astrostudyui/src/components/relative/AntisciaInfo.js`
  - `Horosa-Web/astrostudyui/src/components/germany/Midpoint.js`
  - `Horosa-Web/astrostudyui/src/components/germany/AspectToMidpoint.js`
  - `Horosa-Web/astrostudyui/src/components/germany/MidpointMain.js`
  - `Horosa-Web/astrostudyui/src/components/germany/AstroMidpoint.js`
  - `Horosa-Web/astrostudyui/src/components/germany/AstroGermany.js`
  - `Horosa-Web/astrostudyui/src/components/dice/DiceMain.js`
  - `Horosa-Web/astrostudyui/src/components/otherbu/OtherBuMain.js`
  - 及相关包装组件：`IndiaChartMain/IndiaChart`、`HellenAstroMain/AstroChart13`、`JieQiChartsMain/JieQiChart`、`AstroSolarReturn/AstroLunarReturn/AstroGivenYear/AstroProfection/AstroSolarArc/AstroZR`、`AstroRelative` 与其子组件。

- 结构变化：
  - 新增占星释义渲染工具：
    - `AstroMeaningPopover.js`
      - `isMeaningEnabled(flag)`：统一判断开关；
      - `renderMeaningContent(tip)`：统一生成可滚动 tooltip 内容；
      - `wrapWithMeaning(node, enabled, tip)`：为任意节点挂载释义悬浮层。
  - `showAstroMeaning` 从 `pages/index.js` 透传至推运盘、量化盘、关系盘、节气盘、希腊星术、星盘、西洋游戏、印度律盘与相关内部组件。
  - 推运与量化相关表格组件统一接入悬浮释义：
    - 推运：`AstroPrimaryDirection`、`AstroFirdaria`
    - 关系盘：`AspectInfo`、`MidpointInfo`、`AntisciaInfo`
    - 量化盘：`Midpoint`、`AspectToMidpoint`
  - 星盘右侧页签统一接入悬浮释义：
    - `AstroAspect`（相位）
    - `AstroPlanet`（行星）
    - `AstroLots`（希腊点）
    - `AstroInfo`（行星标签）
  - 西洋游戏 `DiceMain` 的骰子结果（行星/星座/宫位）及两类图盘也同步接入。

- 行为结果：
  - 同一个开关可跨页面控制释义显示，避免“主盘有、子页无”的割裂。
  - 推运盘“表格也是”已生效：悬停行星/相位文本可显示释义。
  - 七政四余未改动，保持默认 RA 显示行为不变。

## 56) 三式合一外圈释义同步补齐（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`

- 结构变化：
  - 三式合一页面接入占星释义工具：
    - `buildMeaningTipByCategory`
    - `isMeaningEnabled`
    - `wrapWithMeaning`
  - `buildOuterData` 增加 `starsByBranchMeta`（包含 `shortTxt/fullTxt/objId`），用于在外圈星曜短标上挂载准确释义。
  - 外圈渲染 `renderOuterMarks` 新增三类悬浮释义：
    - 地支：显示对应星座释义（按 `BRANCH_SIGN_ID_MAP` 映射）；
    - 宫位：显示对应宫位释义（1~12宫）；
    - 星曜：显示完整星曜文本 + 行星释义。

- 计算与兼容性：
  - 仅改渲染层；不改起盘算法、时间算法、参数签名与缓存逻辑。
  - 七政四余（`guolao/*`）未触及，默认 `RA/赤经` 显示保持原行为。

## 57) 占星释义悬浮窗层级化排版（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/astro/AstroMeaningPopover.js`

- 结构变化：
  - 悬浮窗渲染器新增 Markdown 风格语义解析：
    - `#`/`##`/`####` 开头行识别为“标题行”；
    - 标题行以下自动绘制分隔线；
    - 行内 `**...**` 解析为加粗片段；
    - `==` 保持为分割线；空行渲染为间距行。
  - 视觉层级调整为接近遁甲浮窗：
    - 顶部标题更大更粗；
    - 小节标题加粗并与正文分离；
    - 正文行高、颜色、间距统一。

- 行为结果：
  - 占星相关释义浮窗（星/宫/座/相及其扩展表格）主次更清晰；
  - 用户提供文本中的 `#` 与 `**` 标记可以直接体现在悬浮窗中。

## 58) 希腊点释义专用数据源（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/astro/AstroMeaningData.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroLots.js`

- 结构变化：
  - `AstroMeaningData.js` 新增 `RAW_ASTRO_LOTS_REFERENCE`（希腊点原文全文）；
  - 新增 `LOT_BLOCK_MARKERS` 与 `LOT_MEANINGS`，支持 `buildMeaningTipByCategory('lot', key)`；
  - `resolveMeaning('planet', key)` 增加希腊点兜底（兼容旧调用路径）；
  - `AstroLots` 的标题释义入口从 `planet` 改为 `lot` 分类。

- 行为结果：
  - 希腊点悬浮释义优先显示用户提供的专用文本，不再混入行星释义；
  - 其他占星页面若以旧路径请求希腊点释义，仍能显示同一套文案，避免模块间不一致。

## 59) AI导出占星释义开关与注释注入（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - `Horosa-Web/astrostudyui/src/components/homepage/PageHeader.js`

- 结构变化：
  - `AI_EXPORT_SETTINGS_VERSION` 升级为 `5`；
  - 新增 `astroMeaning` 配置块（按技法独立）；
  - 在 `listAIExportTechniqueSettings()` 中新增：
    - `supportsAstroMeaning`
    - `astroMeaning`
  - `PageHeader` 的 “AI导出设置” 弹窗新增占星注释复选项：
    - `在对应分段输出星/宫/座/相/希腊点释义`
  - 导出流程新增 `applyAstroMeaningFilterByContext()`：
    - 仅在占星相关技法且开关开启时生效；
    - 按分段识别并在对应位置追加 `[...]释义` 分段；
    - 注释来源统一调用 `AstroMeaningData`（行星/星座/宫位/相位/希腊点）。

- 行为结果：
  - AI导出与前端释义能力同步；
  - 用户在 AI导出设置中勾选后，导出文本会在对应分段输出完整注释内容；
  - 不勾选时保持原有导出格式与体量。

## 60) AI导出占星注释全分段覆盖与对应位置输出（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`

- 结构变化：
  - 注释注入策略从“标题白名单触发”升级为“标题显式触发 + 内容识别触发”：
    - 显式标题（行星/希腊点/相位/宫位/信息/推运等）持续触发注释；
    - 其它占星分段只要检测到星/宫/座/相/希腊点关键词也触发注释。
  - `appendAstroMeaningSections` 去掉跨分段全局去重，改为每个分段独立注释块。

- 行为结果：
  - AI导出在所有占星相关页面更稳定地输出注释；
  - 注释会跟随原分段出现在“对应位置”，不会因前文重复而被省略；
  - 仍受 AI导出设置里的“占星注释”开关控制。

## 61) 左侧星盘 tooltip 富文本渲染与遁甲风格化（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/helper.js`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroChartCircle.js`

- 结构变化：
  - `helper.js`：
    - 新增 tooltip 富文本解析器：
      - `# / ## / ### / ####` 标题识别；
      - `**...**` 行内加粗渲染；
      - `==` 分割线保留；
      - 仅在检测到富文本标记时启用新渲染，否则走 `genHtmlLegacy`。
    - 新增 `escapeTooltipHtml`、`renderTooltipInlineBoldHtml` 等工具函数。
  - `AstroChartCircle.js`：
    - tooltip 容器样式改为白底卡片（560px + max-width），增加边框与阴影，提升层次可读性。

- 行为结果：
  - 左侧星盘（含推运等基于 `AstroChartCircle` 的图盘）悬浮释义不再显示原始 markdown；
  - 标题/分割线/加粗层级与遁甲风格趋同；
  - 非占星普通 tooltip 渲染保持兼容。

## 62) 遁甲顶部四柱配色对齐八字紫微（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js`

- 结构变化：
  - 引入八字配色数据源：
    - `BaZiColor`（天干五行色）
    - `ZhiColor`（地支色）
  - 新增映射函数：
    - `GAN_COLOR_MAP`
    - `getBaZiStemColor(stem)`
    - `getBaZiBranchColor(branch)`
  - `renderBoard` 顶部四柱 `pillars` 颜色来源改为按干支字符动态映射。

- 行为结果：
  - 遁甲左上角“年/月/日/时”显示配色与八字紫微方案一致；
  - 修改仅作用于顶部四柱文本，不影响下方九宫方盘与宫格内容显示。

## 63) 三式合一左盘同步六壬/遁甲/占星悬浮释义（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`

- 结构变化：
  - 引入六壬释义数据源：
    - `buildLiuRengShenTipObj`
    - `buildLiuRengHouseTipObj`
  - 引入遁甲释义数据源：
    - `buildQimenXiangTipObj`
  - 新增 `toQimenMeaningTip()`：
    - 将遁甲文档块（blank/divider/subTitle/text）转换为统一 tooltip 行结构（兼容 `wrapWithMeaning`）。
  - `renderLiuRengMarks()`：
    - 给“天盘支”挂载十二神悬浮释义；
    - 给“天将”挂载将神/天地盘对应悬浮释义。
  - `renderQimenBlock()`：
    - 给天盘干、八神、地盘干、九星、八门挂载遁甲悬浮释义。

- 行为结果：
  - 三式合一左盘悬浮能力与单盘保持一致：
    - 占星（星/宫/座）可悬浮；
    - 六壬（神/将）可悬浮；
    - 遁甲（干/门/星/神）可悬浮。
  - 全部受 `showAstroMeaning` 开关统一控制，关闭释义时不显示 tooltip。

## 64) 三式合一悬浮无响应修复（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.less`
  - `Horosa-Web/astrostudyui/src/components/astro/AstroMeaningPopover.js`

- 结构变化：
  - `SanShiUnitedMain.less`：
    - `.outerCell`、`.qmBlock`、`.lrMark` 改为 `pointer-events: auto`，允许悬浮命中。
  - `AstroMeaningPopover.js`：
    - `wrapWithMeaning` 从“外包 span 触发”改为“优先直接 clone 原节点触发”；
    - 解决绝对定位节点悬浮时触发区域丢失的问题。

- 行为结果：
  - 三式合一左盘鼠标悬停可稳定弹出释义；
  - 同时提升其他使用 `wrapWithMeaning` 的绝对定位节点兼容性。

## 65) AI导出同步三式悬浮注释（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - `Horosa-Web/astrostudyui/src/components/homepage/PageHeader.js`

- 结构变化：
  - `aiExport.js`：
    - 新增技法集合 `AI_EXPORT_HOVER_MEANING_TECHNIQUES`（`qimen/liureng/sanshiunited`）；
    - 扩展注释开关覆盖：`AI_EXPORT_ASTRO_MEANING_TECHNIQUES` 加入 `qimen/liureng`；
    - 新增技法文案元信息 `getMeaningSettingMetaByTechnique`；
    - 新增三类注释构建器：
      - `appendQimenMeaningSections`（干/门/星/神注释）
      - `appendLiurengMeaningSections`（十二神/天将注释）
      - `appendSanShiUnitedMeaningSections`（六壬/遁甲/占星合并注释）
    - `applyAstroMeaningFilterByContext` 改为按技法分流注释注入。
  - `PageHeader.js`：
    - AI导出设置弹窗中“注释开关”标题与描述改为按技法动态显示（占星类/三式类不同文案）。

- 行为结果：
  - 六壬、遁甲、三式合一在 AI 导出设置中可独立勾选“悬浮注释输出”；
  - 勾选后导出文本在对应分段追加与悬浮窗口一致的注释内容；
  - 不勾选保持原始导出正文不变。

## 66) AI导出统一改为计算快照通道（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`

- 结构变化：
  - 导出提取函数去 DOM 右栏化：
    - `extractAstroContent` 仅走 `astroAiSnapshot`（星盘/希腊）与 `indiachart` 快照；
    - `extractSixYaoContent` 仅走 `guazhan` 快照；
    - `extractSanShiUnitedContent` 仅走 `sanshiunited` 快照；
    - `extractTaiYiContent`、`extractGermanyContent`、`extractJieQiContent`、`extractRelativeContent`、`extractOtherBuContent` 统一仅走对应模块快照。
    - `extractTongSheFaContent` 与 `extractFengShuiContent` 移除 `extractGenericContent` 回退。
  - `extractGenericContent` 删除最终 DOM 文本兜底，避免误采右侧栏目文本。
  - 六爻分段设置与快照标题对齐：
    - 预设改为 `起盘信息/卦象/六爻与动爻/卦辞与断语`；
    - 兼容映射：`起卦方式 -> 卦象`，`卦辞 -> 卦辞与断语`。

- 行为结果：
  - AI导出默认不再从右侧栏目复制文本，改为计算阶段快照输出；
  - 占星盘导出恢复为稳定分段文本来源（避免Tab抓取导致的缺段/串段）；
  - 六爻旧配置用户无需重配，过滤项仍有效。

## 67) 三式合一占星悬浮兼容修复（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/astro/AstroMeaningPopover.js`

- 结构变化：
  - 新增 `normalizeTip()`：
    - 统一将 `string / array / object` 三种tip输入规范为 `{ title, tips }`；
    - 保留对象型tip的标题与细节结构。
  - `renderMeaningContent()`：
    - 改为基于 `normalizeTip` 后的数据渲染，避免字符串tip被判空。

- 行为结果：
  - 三式合一左盘占星元素（外圈星/宫/座）在开启释义时可正常弹出悬浮；
  - 六壬/遁甲悬浮逻辑与显示不受影响。

## 68) AI导出风水快照化与全模块快照链路收口（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - `Horosa-Web/astrostudyui/src/components/fengshui/FengShuiMain.js`
  - `Horosa-Web/astrostudyui/public/fengshui/app.js`

- 结构变化：
  - `aiExport.js`：
    - `extractTongSheFaContent` 改为仅使用模块快照（支持 `horosa:refresh-module-snapshot` 主动刷新）；
    - `extractFengShuiContent` 改为仅使用模块快照（先刷新，再读缓存）。
  - `FengShuiMain.js`：
    - 新增 iframe 引用与轮询快照同步；
    - 新增 `horosa:refresh-module-snapshot` 监听，支持导出时即时拉取风水快照；
    - 将快照保存到 `moduleAiSnapshot('fengshui')`。
  - `public/fengshui/app.js`：
    - 新增 AI 快照文本生成器（分段模板）：
      - `[起盘信息]`
      - `[标记判定]`
      - `[冲突清单]`
      - `[建议汇总]`
      - `[纳气建议]`
    - 在标记列表更新时实时同步 `window.__horosa_fengshui_snapshot_text`。

- 行为结果：
  - AI导出链路进一步统一到“计算/模块快照”来源；
  - 导出过程不再依赖页面右栏/DOM文本拼接；
  - 风水页面也具备与其它术法一致的快照导出能力与导出设置过滤能力。

## 69) AI导出分段过滤容错（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`

- 结构变化：
  - `applyUserSectionFilter(content, key)`：
    - 配置值非数组时：直接走正文（仅剔除禁用分段）；
    - 分段数组为空时：回退到 `AI_EXPORT_PRESET_SECTIONS[key]`；
    - 过滤后为空时：回退原始正文，避免导出空白。
  - `applyUserSectionFilterByContext(content, 'jieqi')`：
    - 若节气盘分段过滤结果为空，回退原始正文。

- 行为结果：
  - 星盘、推运盘、量化盘、关系盘、节气盘、希腊星术、统摄法等页面，不会再因设置分段为空/失配而出现“当前页面没有可导出文本”误报；
  - AI导出设置仍然有效，但加入了防误清空保护。

## 70) AI导出 payload 级回退与全技法自检（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`

- 结构变化：
  - `buildPayload()`：
    - 新增 `rawSnapshotContent` 保存计算快照原文；
    - 在“分段过滤 + 后天信息过滤 + 释义注入”之后，若内容为空则回退至 `rawSnapshotContent` 再生成导出文本。
  - 一致性校验：
    - 校验导出分发链路覆盖（`context.key -> extract*Content`）；
    - 校验禁导出分段（`右侧栏目`）剔除规则；
    - 校验分段过滤与 payload 兜底开关已启用。

- 行为结果：
  - 所有方法页面 AI 导出在设置误配时不会被清空；
  - 保持“计算快照优先”的导出来源，不回退右侧栏目复制；
  - AI导出设置仍按所选分段生效，且具备空白保护。

## 71) AI导出上下文 store 兜底识别（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`

- 结构变化：
  - 新增 `resolveContextByAstroState()`：
    - 读取 `store.astro.currentTab/currentSubTab`，映射当前技法导出 key；
    - 覆盖 `astrochart / direction / germanytech / relativechart / jieqichart / locastro / hellenastro / indiachart / cntradition / cnyibu / guolao / otherbu / fengshui / sanshiunited`。
  - 新增 `withStoreContextFallback(context)`：
    - 当 DOM 上下文识别为 `generic` 或处于 `direction/cntradition/cnyibu` 时，改用 store 结果兜底。
  - `buildPayload()` 与 `getCurrentAIExportContext()`：
    - 统一调用 `withStoreContextFallback(resolveActiveContext())`，确保 AI导出与 AI导出设置读取同一技法上下文。
  - `getAstroCachedContent()`：
    - 增加 `loadAstroAISnapshot()` 回退链，在签名不匹配或保存失败时仍可导出现存快照。

- 行为结果：
  - 修复“当前页面没有可导出文本”误报（由 DOM 技法识别失败触发）；
  - 星盘、推运盘、量化盘、关系盘、节气盘、希腊星术、统摄法等页面导出链路更稳；
  - 保持“计算快照优先”，不依赖右侧栏目复制。

## 72) 三式合一占星悬浮提示结构化对齐（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`

- 结构变化：
  - 新增释义对象处理函数：
    - `normalizeMeaningTip`
    - `mergeMeaningTips`
    - `buildOuterHouseMeaningTip`
    - `buildOuterBranchMeaningTip`
    - `buildOuterStarMeaningTip`
  - `renderOuterMarks`：
    - `宫位`、`地支-星座`、`星曜` 悬浮说明全部改为结构化 `title + tips`，不再拼接对象到字符串。

- 行为结果：
  - 修复三式合一占星悬浮出现 `[object Object]`；
  - 悬浮内容样式与星盘统一（标题、分段、加粗/分隔线风格一致）。

## 73) 星座释义补齐四尊贵状态（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/astro/AstroMeaningData.js`

- 结构变化：
  - 新增 `SIGN_DIGNITY_LINES` 常量：
    - 为 12 星座增加 `入庙 / 擢升 / 入落 / 入陷` 文案映射。
  - 新增 `enrichSignMeaningWithDignity(signKey, meaning)`：
    - 在星座释义 tips 中插入四尊贵状态；
    - 默认插入在“宫位属性”后；
    - 若已存在“入庙”行则跳过，避免重复。
  - 调整 `resolveMeaning('sign', key)`：
    - 返回补齐后的星座释义对象，而非原始 `SIGN_MEANINGS`。

- 行为结果：
  - 星盘相关页面与三式合一中，星座悬浮释义统一新增四尊贵状态；
  - AI导出“星座释义”分段自动携带四尊贵状态；
  - AI导出设置中的占星注释开关仍按原逻辑控制输出，仅内容被增强。

## 74) 量化盘 AI 导出快照刷新链路补齐（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/germany/AstroMidpoint.js`
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`

- 结构变化：
  - `AstroMidpoint.js`：
    - 新增 `saveGermanySnapshot(paramsOverride, resultOverride)`，统一生成并保存 `[起盘信息]/[中点]/[中点相位]` 快照；
    - 新增 `handleSnapshotRefreshRequest(evt)`，响应 `horosa:refresh-module-snapshot` 且 `module === 'germany'`；
    - `componentDidMount` 注册监听并主动尝试写入快照；
    - `componentDidUpdate` 在 `midpoints/chart/fields` 变化时自动刷新快照；
    - `componentWillUnmount` 注销监听；
    - `requestChart` 改为通过 `saveGermanySnapshot` 落库，确保导出与页面同源。
  - `aiExport.js`：
    - `extractGermanyContent` 改为“先刷新再读缓存”：
      - 先 `requestModuleSnapshotRefresh('germany')`；
      - 刷新失败再回退 `getModuleCachedContent('germany')`。

- 行为结果：
  - 量化盘页面点击 AI导出时，不再因本地快照未及时落库而提示“当前页面没有可导出文本”；
  - 保持“计算阶段快照导出”的实现方式，不依赖右侧栏复制。

## 75) AI导出稳态增强（2026-02-25）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - `Horosa-Web/astrostudyui/src/utils/moduleAiSnapshot.js`
  - `Horosa-Web/astrostudyui/src/utils/astroAiSnapshot.js`

- 结构变化：
  - `moduleAiSnapshot.js`：
    - 新增 `MODULE_SNAPSHOT_MEMORY` 内存快照池；
    - `saveModuleAISnapshot/loadModuleAISnapshot` 改为“localStorage + 内存双通道”。
  - `astroAiSnapshot.js`：
    - 新增 `ASTRO_AI_SNAPSHOT_MEMORY`；
    - `saveAstroAISnapshot/loadAstroAISnapshot` 支持 localStorage 失败时内存兜底。
  - `aiExport.js`：
    - `withStoreContextFallback` 增强：当 DOM 上下文与 store 上下文冲突或不完整时，优先采用 store 当前术法；
    - `getCurrentAIExportContext` 对 `direction` 返回 `primarydirect`；
    - 新增 `normalizeExportKey/getTechniqueLabelByKey/getCandidateExportKeys/extractContentByKey`；
    - `buildPayload` 改为候选键兜底提取，并按 `usedExportKey` 执行分段过滤/注释开关；
    - 推运子模块导出增加 refresh 优先（法达/太阳弧/返照/流年等）；
    - `requestModuleSnapshotRefresh` 等待窗口从 `80ms` 调整为 `220ms`；
    - `getModuleCachedContent` 增加跨模块别名识别，减少 case 快照读取误判。

- 行为结果：
  - 修复多个术法点击 AI导出“无反应/无可导出文本”；
  - 修复上下文误判导致的导出串台；
  - 在 localStorage 异常情况下，仍可通过内存快照稳定导出。

## 76) 星盘组件底部选项统一复选框（2026-02-27）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/astro/ChartDisplaySelector.js`
  - `Horosa-Web/astrostudyui/src/models/app.js`
  - `Horosa-Web/astrostudyui/src/pages/index.js`

- 结构变化：
  - `ChartDisplaySelector`：
    - 移除 `Checkbox.Group + Select` 混合结构，改为统一单项 `Checkbox` 渲染；
    - `主/界限法显示界限法` 改为纯复选框（布尔勾选映射 `showPdBounds: 1/0`）；
    - 新增底部开关：`仅按照本垣擢升计算互容接纳`。
  - `app` 模型新增 `showOnlyRulExaltReception` 状态并纳入 `GlobalSetup` 持久化。
  - `index` 页面补充 `showOnlyRulExaltReception` 下发，保证显示链路可读该配置。

- 行为结果：
  - 星盘组件底部选项风格统一，不再出现“下拉+复选框”混合断层；
  - “主/界限法显示界限法”交互与其它选项一致；
  - 新增“仅按照本垣擢升计算互容接纳”全局开关进入状态与持久化链路。

## 77) 接纳/互容本垣擢升过滤同步到信息面板与AI快照（2026-02-27）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/astro/AstroInfo.js`
  - `Horosa-Web/astrostudyui/src/utils/astroAiSnapshot.js`

- 结构变化：
  - `AstroInfo` 新增：
    - `getOnlyRulerExaltReceptionEnabled`
    - `hasRulerOrExalt`
    - `keepReceptionLine`
    - `keepMutualLine`
  - `receptions/mutuals` 渲染前先按本垣/擢升规则过滤：
    - 正接纳：`supplierRulerShip` 必含 `ruler/exalt`；
    - 邪接纳：`supplierRulerShip` 或 `beneficiaryDignity` 任一含 `ruler/exalt`；
    - 互容：双方 `rulerShip` 均含 `ruler/exalt`。
  - `astroAiSnapshot` 新增同名过滤辅助并应用到 `buildInfoSection`；
  - `createAstroSnapshotSignature` 纳入该开关位（`...|onlyRulerExaltReception`）；
  - `build/save/get` 快照函数签名新增 `options`，支持导出链路传入该开关并保持一致。

- 行为结果：
  - 页面右侧“接纳/互容”与 AI导出“信息”分段使用同一过滤规则；
  - 切换开关后不会误命中旧快照，导出内容与当前显示保持对齐；
  - 当过滤后为空时，不再输出空“接纳/互容”标题分节。

## 78) 本地启动脚本服务生命周期修复（2026-02-27）

- 目标文件：
  - `Horosa_Local.command`
  - `Horosa-Web/stop_horosa_local.sh`
  - `README.md`

- 结构变化：
  - `Horosa_Local.command`：
    - 新增 `WEB_PID_FILE`（`.horosa_web.pid`）管理前端静态服务进程；
    - `cleanup` 改为统一调用 `stop_horosa_local.sh` 做 py/java/web 全量回收；
    - 启动前 stale 检查从 `py/java` 扩展为 `py/java/web`；
    - `HOROSA_KEEP_SERVICES_RUNNING` 默认从 `1` 调整为 `0`（默认关窗停服）。
  - `stop_horosa_local.sh`：
    - 新增 web 进程 `stop_by_pid_file "web" "${WEB_PID_FILE}"`。
  - `README.md`：
    - 增补 `HOROSA_KEEP_SERVICES_RUNNING=1` 说明（默认 `0`）。

- 行为结果：
  - 默认关闭窗口后会自动停止本地服务，不再出现后台残留常驻；
  - 需要常驻时可显式设置环境变量开启；
  - pid 文件与 stop 脚本职责对齐，清理链路更稳定。

## 79) 本地启动浏览器优先级调整为 Safari（2026-02-27）

- 目标文件：
  - `Horosa_Local.command`

- 结构变化：
  - 新增 Safari 跟踪函数：
    - `launch_safari_window`
    - `safari_window_exists`
    - `wait_for_safari_window_close`
  - 自动停止模式的打开顺序改为：
    - Safari（可跟踪关闭） -> Chromium app window -> `open -a Safari` -> 系统默认浏览器。

- 行为结果：
  - 软件默认优先以 Safari 打开；
  - 在默认“自动停服”模式下，关闭 Safari 窗口即可触发停服，无需手动回车。

## 80) 三式合一外圈星曜简称去歧义（2026-02-27）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`

- 结构变化：
  - `shortMainStarLabel(name)` 新增天顶/中天特判：
    - `天顶` -> `顶`
    - `中天` -> `顶`

- 行为结果：
  - 外圈短标签不再出现“天顶=天”与“天王星=天”冲突；
  - 悬浮全称保持不变，短标签识别更清晰。

## 81) 六壬/三式合一天将悬浮正文按将拆分补全（2026-02-28）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/liureng/LRShenJiangDoc.js`

- 结构变化：
  - 新增 `JIANG_INFO`：
    - 收录十二天将的 `intros / verses / extra` 文案结构；
    - `天乙` 专门承载“主清御…天乙持魁钺…”加粗段落；
    - 其余十一将仅使用本将对应文案。
  - 新增 `buildJiangDocTips(jiang)`：
    - 按当前天将动态生成悬浮正文；
    - 统一插入将名标题（`### **将名**`）与该将诗诀（加粗）。
  - `buildLiuRengHouseTipObj`：
    - 在原“天盘神/地盘神命中信息”前追加当前天将正文；
    - 保留命中位说明用于格位定位。
  - 去重调整：
    - 移除正文内“XX临十二神”整段，避免与当前盘面命中位信息重复。

- 行为结果：
  - 六壬与三式合一中的天将悬浮，不再出现“把天乙内容灌到所有将”的错误；
  - 每个天将显示对应原文段落与诗诀；
  - 悬浮内容更完整，同时避免重复段落堆叠。

## 82) 六壬悬浮样式对齐三式合一富文本风格（2026-02-28）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/utils/helper.js`
  - `Horosa-Web/astrostudyui/src/components/liureng/LRCommChart.js`

- 结构变化：
  - `helper.js`：
    - `genHtml(tipobj, needpadding, forceRich)`：新增 `forceRich`，可强制富文本渲染路径；
    - `creatTooltip(..., needpadding, forceRich)`：新增参数透传。
  - `LRCommChart.js`：
    - 六壬宫位将神悬浮、神义悬浮统一传入 `forceRich=true`。

- 行为结果：
  - 六壬相关悬浮窗统一使用与三式合一相同的富文本视觉层级；
  - 不再因文本缺少 `#/**` 标记而回退到旧版列表风格。

## 83) 六壬盘悬浮容器样式卡片化（2026-02-28）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengChart.js`
  - `Horosa-Web/astrostudyui/src/utils/helper.js`

- 结构变化：
  - `LiuRengChart.setupToolTip` 从旧版蓝底定宽提示框升级为白底卡片样式：
    - `width:auto + max-width/min-width`
    - `max-height + overflow-y`
    - `background/border/shadow/z-index` 对齐统一悬浮风格。
  - `helper.creatTooltip` 增加 `forceRich=true` 时的不透明显示策略（`opacity=1`）。

- 行为结果：
  - 六壬盘悬浮不再出现“半透明蓝底整条覆盖”的旧观感；
  - 视觉层级、可读性、滚动行为与三式合一悬浮更一致。

## 84) 文档同步确认：六壬悬浮窗调整（2026-02-28）

- 同步范围：
  - 六壬天将文案补全与去重；
  - 六壬悬浮富文本强制渲染；
  - 六壬提示容器样式卡片化（白底、边框、阴影、自动宽高）。

- 已登记文件：
  - `Horosa-Web/astrostudyui/src/components/liureng/LRShenJiangDoc.js`
  - `Horosa-Web/astrostudyui/src/components/liureng/LRCommChart.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengChart.js`
  - `Horosa-Web/astrostudyui/src/utils/helper.js`

- 结果：
  - 变更已在 `UPGRADE_LOG.md` 与 `PROJECT_STRUCTURE.md` 双处落档，可追踪。

## 85) 六壬悬浮标题去重（2026-02-28）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/liureng/LRShenJiangDoc.js`

- 结构变化：
  - `buildJiangDocTips(jiang)`：移除正文开头的 `### **将名**` 注入。

- 行为结果：
  - 六壬与三式合一中的六壬悬浮，仅保留卡片最上方标题显示一次名称；
  - 正文不再重复同名标题。

## 86) 六壬悬浮加粗语义补齐（2026-02-28）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/liureng/LRShenJiangDoc.js`

- 结构变化：
  - 新增 `formatJiangIntroLine(line)`：
    - 识别 `其吉：/其吉:` 与 `其戾：/其戾:` 前缀并转成加粗输出。
  - `buildLiuRengHouseTipObj`：
    - `天盘神`、`地盘神` 标签改为 markdown 加粗。
  - `buildLiuRengShenTipObj`：
    - 两句诗 (`verse1`/`verse2`) 改为整句加粗；
    - `类象` 标签改为加粗前缀（`**类象：**`）。

- 行为结果：
  - 六壬与三式合一的六壬悬浮，重点语义标签层级更清晰；
  - 天将/地支两类悬浮在排版强调上保持一致。

## 87) 六壬悬浮追加四课/三传上下文（2026-02-28）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/liureng/LRShenJiangDoc.js`
  - `Horosa-Web/astrostudyui/src/components/liureng/LRCommChart.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/RengChart.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`

- 结构变化：
  - `LRShenJiangDoc.js`：
    - 新增 `appendKeAndChuanTips(tips, tipContext)`，输出四课/三传的“地支+天将”段落；
    - `buildLiuRengShenTipObj(branch, tipContext)` 与 `buildLiuRengHouseTipObj(..., tipContext)` 支持可选上下文参数。
  - `LRCommChart.js`：
    - 新增 `sanChuanData` 状态与 `setSanChuanData`；
    - 新增 `buildTooltipContext()`，聚合 `getKe()` 与 `sanChuanData` 供悬浮使用。
  - `RengChart.js`：
    - 三传图计算后将 `cuangs` 回写到主六壬盘实例，保证悬浮读取到最新三传。
  - `SanShiUnitedMain.js`：
    - 六壬环悬浮调用增加 `liurengTipContext`（`keData.raw + sanChuan`）。

- 行为结果：
  - 六壬与三式合一中的六壬悬浮，均可直接看到四课与三传的地支/天将上下文，判断链更完整。

## 88) 四课/三传元素级悬浮提示（2026-02-28）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/liureng/KeChart.js`
  - `Horosa-Web/astrostudyui/src/components/liureng/ChuangChart.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/RengChart.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`

- 结构变化：
  - `KeChart`：新增 `buildKeTipObj`，每课列绑定元素级 tooltip（地支/天将）。
  - `ChuangChart`：新增 `buildChuanTipObj` 与支提取逻辑，每传列绑定元素级 tooltip（地支/天将）。
  - `RengChart`：`drawGua2` 将 `divTooltip` 下发至 `KeChart/ChuangChart`。
  - `SanShiUnitedMain`：中宫四课列与三传行包裹 `wrapWithMeaning`，显示对应地支/天将信息。

- 行为结果：
  - 用户将鼠标放到四课/三传对应元素上时，弹出对应“地支+天将”提示；
  - 不再把该信息混入其他悬浮正文段落。

## 89) 四课/三传元素悬浮精细化映射（2026-02-28）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/liureng/KeChart.js`
  - `Horosa-Web/astrostudyui/src/components/liureng/ChuangChart.js`
  - `Horosa-Web/astrostudyui/src/components/lrzhan/RengChart.js`
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`

- 结构变化：
  - `KeChart`：
    - 新增按元素映射的 tooltip 逻辑：
      - 天将 -> `buildLiuRengHouseTipObj`
      - 地支 -> `buildLiuRengShenTipObj`
    - 去掉整列统一提示，避免一个悬浮覆盖多个语义。
  - `ChuangChart`：
    - 三传上半区仅“地支位”挂接十二神释义；
    - 天将行挂接天将释义；
    - 六亲行保持无悬浮。
  - `RengChart`：
    - `drawGua2` 下发 `liuRengChart` 到 `KeChart` 供天将释义定位使用。
  - `SanShiUnitedMain`：
    - 中宫四课/三传从整列包裹改为单字符包裹：
      - 地支与天将字符可悬浮；
      - 天干与六亲字符不悬浮。

- 行为结果：
  - 鼠标停在“哪个元素”就显示“哪个元素”对应释义；
  - 不再出现整列同一提示或非目标元素弹出提示。

## 90) 三式合一后天十二宫悬浮标题去重（2026-02-28）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`

- 结构变化：
  - `buildOuterHouseMeaningTip`：
    - 合并分段时不再注入正文内 `N宫` 子标题（`title: ''`）；
    - 保留 tooltip 顶部标题作为唯一宫名显示。

- 行为结果：
  - 后天十二宫悬浮不再出现“宫名重复两次”；
  - 视觉上与用户期望一致（仅顶部显示宫名）。

## 91) 三式合一上升点简称调整（2026-02-28）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js`

- 结构变化：
  - `shortMainStarLabel` 新增上升点简称映射：
    - `上升` -> `升`

- 行为结果：
  - 三式合一外圈星盘不再显示“上”，统一显示“升”。

## 92) 修复六壬四课/三传横线伪影（2026-02-28）

- 目标文件：
  - `Horosa-Web/astrostudyui/src/components/liureng/KeChart.js`
  - `Horosa-Web/astrostudyui/src/components/liureng/ChuangChart.js`

- 结构变化：
  - 元素级悬浮热区 `rect` 显式关闭描边：
    - `stroke: none`
    - `stroke-width: 0`

- 行为结果：
  - 去除四课地支区与三传干支区中部意外横线；
  - 保留元素级悬浮触发行为不变。

## 93) Horosa_Local 端口占用自动清理兜底（2026-02-28）

- 目标文件：
  - `Horosa_Local.command`

- 结构变化：
  - 新增函数：
    - `get_listener_pids(port)`：读取端口监听 PID 列表。
    - `is_horosa_web_listener(pid)`：识别是否为 Horosa 遗留 `http.server`（按命令行/工作目录判断）。
    - `cleanup_stale_horosa_web_listener(port)`：在启动前自动清理旧网页监听进程。
  - 启动 `[2/4]` 网页服务前流程调整：
    - 若端口已占用，先尝试清理可识别的 Horosa 残留进程；
    - 清理后仍占用则中止，并写入占用信息到诊断日志。

- 行为结果：
  - 关闭窗口后遗留的旧 `python -m http.server` 不再阻塞下次启动；
  - 对非 Horosa 进程保持保守，不误杀其他服务。
