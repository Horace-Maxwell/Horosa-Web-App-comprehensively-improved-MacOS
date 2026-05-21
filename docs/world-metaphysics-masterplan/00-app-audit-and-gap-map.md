# 00 当前 APP 巡检与差距地图

## 巡检方法

本轮巡检包括：

- 打开本地预览 URL，确认应用标题与首页可用。
- 读取首页 DOM，提取顶栏、模块切换器、可见按钮、模块入口。
- 对照 `Horosa-Web/astrostudyui/src/pages/index.js` 的主导航与 `TabPane`。
- 检索 `src/components`、`astropy`、`astrostudysrv` 中的术数模块、后端接口与辅助库。

未进行任何代码修改。本目录仅新增规划文档。

## 当前主导航结构

源码 `navigationPages` 明确了 20 个主模块：

| 分组 | 模块 | key | 当前组件 |
| --- | --- | --- | --- |
| 命 | 占星 | `astrochart` | `AstroChartMain` |
| 命 | 星运 | `direction` | `AstroDirectMain` |
| 命 | 八字 | `bazi` | `BaZi` |
| 命 | 紫微 | `ziwei` | `ZiWeiMain` |
| 命 | 七政 | `guolao` | `GuoLaoChartMain` |
| 命 | 印占 | `indiachart` | `IndiaChartMain` |
| 命 | 辅盘 | `auxchart` | `AuxChartMain` |
| 命 | 合盘 | `relativechart` | `AstroRelative` |
| 卜 | 三式 | `sanshiunited` | `SanShiUnitedMain` |
| 卜 | 六壬 | `liureng` | `LiuRengMain` |
| 卜 | 遁甲 | `dunjia` | `DunJiaMain` |
| 卜 | 六爻 | `guazhan` | `GuaZhanMain` |
| 卜 | 太乙 | `taiyi` | `TaiYiMain` |
| 卜 | 分至 | `jieqichart` | `JieQiChartsMain` |
| 卜 | 风水 | `fengshui` | `FengShuiMain` |
| 卜 | 其他 | `cnyibu` | `CnYiBuMain` |
| 工具 | AI分析 | `aianalysis` | `AIAnalysisMain` |
| 工具 | 3D | `astrochart3D` | `AstroChartMain3D` |
| 工具 | 黄历 | `calendar` | `CalendarMain` |
| 工具 | 辅助 | `cntradition` | `CnTraditionMain` |

登录后还可扩展内容/管理入口：书籍阅读、星阙直播、管理工具。

## 已有后端与算法资产

### Python 天文/占星资产

- `Horosa-Web/astropy/websrv/webchartsrv.py`：挂载印度占星等服务。
- `Horosa-Web/astropy/astrostudy/perchart.py`：核心星盘结构。
- `Horosa-Web/astropy/astrostudy/termdirection.py`、`firdaria.py`、`perpredict.py`、`solararc.py`：推运相关。
- `Horosa-Web/astropy/astrostudy/india/chart2.py` 到 `chart60.py`：印度分盘。
- `Horosa-Web/astropy/astrostudy/india/jyotish_engine.py`：Jyotish 规则底座。
- `Horosa-Web/astropy/astrostudy/guostarsect`：七政四余/果老相关。
- `Horosa-Web/flatlib-ctrad2`：传统占星 Python 库改造版，含尊贵、相位、主限、小限、返照等。

### Java 中式术数资产

- `/bazi/birth`、`/bazi/direct`：八字与大运。
- `/ziwei/birth`：紫微。
- `/liureng/gods`、`/liureng/runyear`：六壬/年命。
- `/calendar/month`：农历/黄历基础。
- `/chart`、`/chart13`、`/india/chart`：星盘和十三分/印度盘。
- `modules/reference/xuan-utils-pro-master`：八字、紫微、六爻、梅花、奇门、大六壬参考实现。
- `modules/reference/kintaiyi-master`：太乙、六壬、历史文本、古籍和盘面参考。

### AI 资产

- `AIAnalysisMain`：分析、历史、资料、模板、设置五个工作区。
- 后端 `/aianalysis`：模型供应商、材料抽取、embedding、chat、stream。
- 支持全文优先、检索优先、自动模式。

## 模块差距总表

| 模块 | 当前强项 | 主要短板 | 顶级化优先级 |
| --- | --- | --- | --- |
| 占星 | 有星盘、宫位、相位、古典、推运入口 | 流派配置不够系统；固定星、小行星、阿拉伯点、昼夜、教派、分界来源需结构化 | P0 |
| 星运 | 已有主限、法达、小限、返照等 | 缺“时间搜索器”和事件验证；次限、三限、月限、进展月相需补齐 | P0 |
| 八字 | 大运/流年/月日已可见，信息密度高 | 子平流派、格局判定、旺衰、调候、病药、盲派、神煞来源版本需并列 | P0 |
| 印占 | 分盘体系很强 | Dasha、Jaimini、Ashtakavarga、Tajika、Muhurta、Prashna 尚需产品化 | P0 |
| 三式 | 已有三式合一入口 | 三式需要独立规则解释器、局法切换、古籍规则引用 | P0 |
| AI分析 | 产品形态已成型 | 需要“术法专属提示词 + 引用 + 结构化断语 + 验证登记” | P0 |
| 风水 | 有独立工作台 | 需补完整罗盘层、空间建模、坐向与飞星历法、户型导入 | P1 |
| 塔罗/卡牌 | 目前未见独立主模块 | 需要牌库、牌阵、抽牌随机性、解释来源、图像版权 | P1 |
| 灵数/姓名/相术 | 分散在辅助或未实现 | 输入模型简单，适合作为快速增长模块 | P1 |
| 研究验证 | 有案例/AI/深度学习痕迹 | 需预测登记、盲测、统计、匿名化、事件本体 | P0 |

## UI/产品结构建议

### 现有导航应保留，但增加“世界术法图谱”

当前模块切换器按“命/卜/工具”分组，适合专家快速进入。但世界级 APP 还应有一个“术法图谱”视图：

- 天象类：西占、印占、七政四余、玛雅、阿拉伯月宿、恒星、择时。
- 历法类：农历、节气、Panchanga、希伯来历、伊斯兰历、玛雅历。
- 命理类：八字、紫微、九星、灵数、人类图、姓名、相术。
- 占卜类：易经、六爻、梅花、三式、塔罗、符文、Geomancy、Ifa。
- 空间类：风水、Vastu、占星地图、地理择址。
- 身心象征类：梦占、体相、手相、脉轮/能量系统。
- 研究类：命例库、预测登记、盲测、统计报告。

### 每个模块都需要“三层输出”

1. 盘面层：图、表、时间轴、星曜/卦象/宫位/牌面。
2. 规则层：为什么这么排、用的哪套规则、可替换口径是什么。
3. 解读层：结构化断语、置信度、引用、案例、反证条件。

### 每个模块都需要“流派配置”

示例：

- 八字：子平、盲派、调候、格局、旺衰、象法、纳音、神煞派。
- 印占：Parashara、Jaimini、Tajika、Nadi、KP、南印/北印盘式。
- 奇门：转盘、飞盘、置闰、拆补、茅山/鸣法/法术奇门。
- 紫微：三合、飞星、河洛、钦天四化、中州派。
- 西占：古典、传统、现代、心理、演化、汉堡、宇宙生物学、金融占星。

## P0 工作包

1. 统一术法元数据系统：每个模块注册输入、输出、规则版本、流派、参考来源。
2. 统一时间与地点内核：时区、真太阳时、历法、儒略日、Delta T、地理坐标。
3. 统一“计算链路”可视化：让用户看到从出生数据到结果的每一步。
4. 统一案例库：命盘、卦盘、牌阵、风水局、事件、验证结果。
5. 统一研究协议：预测登记、命中标准、盲测、统计分析。
6. AI 引用与结构化输出：AI 不只聊天，要能生成可追踪、可比较、可验证的判断。

