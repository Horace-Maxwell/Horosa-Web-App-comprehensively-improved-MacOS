# 08 可嵌入库、数据源与选型索引

## 选型原则

1. 先看许可证，再看功能。玄学 APP 很容易用到 AGPL、非商用、版权不明资料。
2. 天文/历法核心要可复现。固定版本、固定数据文件、记录配置。
3. 术法规则要可替换。不要把某个库的流派判断当成唯一真理。
4. 资料库要可引用。AI 输出必须知道来源。
5. 图像素材要清楚版权。塔罗、符文、星图、古籍扫描都要记录来源。

## 天文与占星

| 名称 | 语言 | 用途 | 推荐程度 | 注意 |
| --- | --- | --- | --- | --- |
| Swiss Ephemeris / `pyswisseph` | C/Python | 行星、月亮、恒星、宫位、sidereal | 极高 | AGPL/商业授权重点审查 |
| JPL SPICE / SpiceyPy | C/Python | 科学级历表、3D 几何 | 高 | 术法层需自建 |
| Astropy | Python | 时间、坐标、单位、天文转换 | 高 | 科学天文，不含占星术法 |
| Skyfield | Python | JPL ephemeris 易用封装 | 高 | 宫位/尊贵需自建 |
| ERFA/SOFA | C/Python | IAU 标准天文算法 | 高 | 底层工具 |
| Flatlib | Python | 传统占星对象与规则 | 中高 | 可作为对照；当前项目已有改造版 |
| Kerykeion | Python/API | 占星封装与 SVG 图表 | 中 | 适合参考/对照 |
| PyMeeus | Python | Meeus 算法、历法教学 | 中 | 轻量，非最高精度 |
| astronomia | JS | Meeus/VSOP87 前端计算 | 中 | 适合前端教学和离线演示 |
| VSOP87 JS 实现 | JS | 行星位置 | 中 | 需补视位置、岁差章动 |

## 中国历法与术数

| 名称 | 语言 | 用途 | 推荐程度 | 注意 |
| --- | --- | --- | --- | --- |
| 6tail `lunar-javascript` | JS | 公历、农历、黄历、干支、节气、宜忌等 | 高 | MIT；适合前端/Node |
| 6tail `lunar-java` | Java | 同上 Java 版 | 高 | 可接后端 |
| 6tail `tyme` 系列 | 多语言 | 更现代的历法库 | 中高 | 需评估成熟度 |
| `sxtwl_cpp` | C++/Python 等 | 寿星天文历，农历节气 | 高 | 多语言绑定，需版本固定 |
| `cnlunar` | Python | 中国农历/节气/神煞 | 中 | 适合对照 |
| 项目内 `xuan-utils-pro-master` | Java | 八字、紫微、奇门、六爻、梅花、大六壬参考 | 高 | 作为规则参考，不直接照搬需审查许可 |
| 项目内 `kintaiyi-master` | Python | 太乙/六壬/历史文本 | 高 | 非常适合太乙深化 |

## 印度 Jyotish

| 名称 | 类型 | 用途 | 注意 |
| --- | --- | --- | --- |
| Swiss Ephemeris sidereal modes | 底层历表 | Lahiri、Raman、Krishnamurti 等 | 许可审查 |
| 项目内 `jyotish_engine.py` | 内部代码 | Jyotish 规则底座 | 应扩展成独立规则引擎 |
| Maitreya / Jagannatha Hora | 外部软件 | 金标准对照 | 不一定可嵌入，但可用于测试 |
| drik-panchanga 类开源项目 | 参考 | Panchanga、Muhurta | 逐项审查许可 |

## 地理与时区

| 名称 | 用途 | 注意 |
| --- | --- | --- |
| IANA Time Zone Database | 时区历史 | 必备 |
| GeoNames | 地名、经纬度、时区 API/离线数据 | 免费额度和署名要求 |
| OpenStreetMap / Nominatim | 地理编码 | 使用政策限制，建议自建或商业服务 |
| Natural Earth | 国家/地图底图 | 适合可视化 |
| NASA SRTM / Mapbox terrain | 高程/地形 | 风水/占星地图可用 |

## 卡牌与图像

| 名称 | 用途 | 注意 |
| --- | --- | --- |
| Wikimedia Commons Rider-Waite-Smith | RWS 牌图 | 原版多地区公有领域，但具体扫描/上色版本需核查 |
| 自制牌面 | 商业产品最稳 | 可统一星阙视觉 |
| OpenMoji | 图标/符号辅助 | 开源图标，不是塔罗牌库 |
| 自定义 Oracle deck schema | 用户/授权牌库 | 需要版权字段 |

## AI 与检索

| 组件 | 用途 |
| --- | --- |
| 向量数据库：pgvector、Qdrant、Weaviate、Milvus | 资料检索 |
| 全文检索：PostgreSQL FTS、Meilisearch、OpenSearch | 术语/古籍检索 |
| 文档解析：unstructured、Apache Tika、marker、docling | PDF/Word/网页导入 |
| 图数据库：Neo4j、Kuzu、PostgreSQL edges | 术法知识图谱 |
| 统计：SciPy、statsmodels、scikit-learn、R | 验证研究 |
| 数据仓库：DuckDB、Parquet | 本地研究数据 |

## 前端可视化

| 名称 | 用途 |
| --- | --- |
| D3 | 星盘、关系图、统计图 |
| Three.js | 3D 天球、轨道、空间风水 |
| deck.gl / MapLibre | 占星地图、风水地理 |
| Cytoscape.js / React Flow | 规则链、四化链、知识图谱 |
| Monaco Editor | AI 模板、规则编辑器，当前 AI 模块已用 |

## 许可风险分级

| 等级 | 说明 | 策略 |
| --- | --- | --- |
| L0 | MIT/Apache/BSD/公有领域 | 可优先集成 |
| L1 | LGPL/MPL | 可用但需隔离修改 |
| L2 | GPL/AGPL | 商业闭源风险高，需法务 |
| L3 | 非商用/不明 | 不进入核心产品 |
| L4 | 活态宗教/文化授权不明 | 只做资料索引或取得授权 |

## 推荐技术路线

### 近期

- 继续保留现有 Python + Java 后端。
- 抽出 `metaphysics-core`：时间地点、干支、历法、天文配置、规则元数据。
- 将 Jyotish、八字、三式作为第一批“规则化模块”。
- 以 PostgreSQL + JSONB + pgvector 支撑案例、盘、知识库。

### 中期

- 插件化每个术法模块。
- 引入图数据库或边表建知识图谱。
- 建立 `golden_cases/` 回归样例。
- 研究数据转 DuckDB/Parquet。

### 长期

- 高精度天文服务可独立成服务。
- 规则引擎支持 DSL。
- 专家可在 UI 中编辑规则、测试规则、发布规则包。
- 建立多语言世界玄学资料库。

