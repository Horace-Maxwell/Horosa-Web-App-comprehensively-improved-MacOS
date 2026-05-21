# 02 天文历算与占星引擎路线

## 总原则

占星类模块的顶级能力取决于两层：

1. 天文层：时间、坐标、历表、黄赤转换、恒星、月相、日月食、地理位置、时区、Delta T。
2. 术法层：黄道、宫位、相位、尊贵、昼夜、主限、分盘、Dasha、神煞、断语规则。

这两层必须分离。天文层追求物理精度与可复现；术法层允许流派并存。不要把“某一流派的解释”硬编码进天文计算。

## 时间与坐标基础设施

### 必备输入字段

- 本地日期与时间。
- 时区名：IANA timezone，如 `Asia/Shanghai`，不能只存 UTC offset。
- 地点：经纬度、海拔、地名、国家/地区。
- 历法：Gregorian、Julian、proleptic Gregorian、农历/印度历等。
- 时间置信度：精确、约略、未知、校正后。
- 太阳时策略：标准时、真太阳时、平太阳时、地方时。
- Delta T 模型版本。
- 黄道策略：热带、恒星、各 ayanamsa、自定义。

### 输出元数据

每次排盘都应附带：

```json
{
  "time": {
    "local": "2026-05-21T00:48:51",
    "timezone": "Asia/Shanghai",
    "utc": "2026-05-20T16:48:51Z",
    "calendar": "gregorian",
    "julian_day": 2461181.2006,
    "delta_t_model": "engine-default"
  },
  "location": {
    "lon": 119.3167,
    "lat": 26.0667,
    "elevation_m": null,
    "source": "user"
  },
  "astronomy": {
    "ephemeris": "Swiss Ephemeris or JPL",
    "zodiac": "tropical",
    "sidereal_mode": null,
    "house_system": "Placidus"
  },
  "tradition": {
    "module": "western_astrology",
    "school": "traditional",
    "rule_version": "xq-astrology-rules-v1"
  }
}
```

## 推荐天文/历算引擎

| 引擎/库 | 类型 | 优点 | 风险/注意 | 适用 |
| --- | --- | --- | --- | --- |
| Swiss Ephemeris / `pyswisseph` | 高精度占星历表 | 占星软件事实标准，行星、宫位、恒星、sidereal 模式支持强 | AGPL/商业许可需严肃处理；要固定 ephemeris 文件版本 | 生产级占星与 Jyotish |
| NASA/JPL SPICE | 科学级历表/几何 | NASA 官方生态，SPK/PCK 格式，可做高精度天体位置 | 学习曲线高，占星宫位/黄道需自己封装 | 研究级验证、3D、天体可视化 |
| Astropy | Python 天文基础 | 坐标、时间、单位、框架转换强 | 不是占星库，宫位/术法需自建 | 坐标、恒星、教学、验证 |
| Skyfield | Python 天体位置 | JPL ephemeris 使用友好，适合日月行星、卫星、月相 | 占星术法层需自建 | 天文教学、月相、交食、可视化 |
| IAU SOFA/ERFA | 标准天文学算法 | 基础天文标准权威 | 底层，产品封装成本高 | 时间尺度、岁差章动、严肃校验 |
| Flatlib | 传统占星库 | 传统占星对象、尊贵、相位、宫位较贴近术法 | 维护状态与精度需验证；当前项目已有改造版 | 古典占星快速迭代 |
| Kerykeion | Python 占星库/API | 现代 Python 封装、SVG 图表、Swiss Ephemeris | 产品耦合度与许可策略需评估 | 快速对照、图表参考 |
| PyMeeus | Meeus 算法 | 可读性强、依赖少，适合教学 | 精度与长期范围不如专业历表 | 历法/节气算法教学、轻量工具 |
| astronomia / VSOP87 JS | JS 天文算法 | 前端可跑，适合离线和可视化 | 要处理精度、章动、视位置等细节 | 前端教学、轻量日月行星 |

## 西方占星体系

### 基础模块

- 星体：日月、水金火木土、天海冥、交点、凯龙、谷神等小行星。
- 点：ASC、MC、Vertex、East Point、Part of Fortune、Spirit、Eros 等 Lots。
- 黄道：热带、恒星；岁差和 ayanamsa 可配置。
- 宫位：Whole Sign、Equal、Porphyry、Alcabitius、Regiomontanus、Placidus、Koch、Campanus、Topocentric、Morinus。
- 相位：托勒密相位、次要相位、反平行、同纬、antiscia/contra-antiscia。
- 尊贵：守护、擢升、三分、界、面；埃及界/托勒密界；现代守护可选。
- 状态：昼夜、sect、combust、under beams、cazimi、retrograde、speed、latitude、orientality。
- 恒星：投影到黄经、赤经合、纬度容许；固定星版本和岁差处理。

### 流派

| 流派 | 特点 | 需要功能 |
| --- | --- | --- |
| 希腊化占星 | Whole Sign、Lots、sect、三分主、zodiacal releasing、annual profection | Lot 计算器、释放时间轴、主星规则 |
| 中世纪阿拉伯/拉丁 | Lots、receptions、almutem、firdaria、revolutions、horary | 接纳矩阵、主星评分、问卜盘 |
| 文艺复兴传统 | William Lilly 系、卜卦/择时、医学占星 | 卜卦规则、月亮状态、问事模板 |
| 现代心理占星 | 行星原型、心理动力、成长叙事 | 解释文本、主题聚类、咨询记录 |
| 演化占星 | 月交点、冥王星、灵魂议题 | 轴线叙事、阶段性问题模板 |
| 汉堡学派/宇宙生物学 | 中点、90 度盘、假想星、轴点 | 中点网格、harmonic dial、搜索器 |
| 金融/世运占星 | ingress、lunation、eclipse、mundane charts | 国家/市场事件库、统计对照 |
| 医学占星 | 身体部位、体液、行星状态 | 健康免责声明、历史资料库 |

## 推运与时序

### 已有能力

当前星运模块可见：主/界限法、主限法盘、黄道星释、法达星限、小限法、太阳弧、太阳返照、月亮返照、流年法、十年大运。

### 应补齐

- Secondary progressions：日一年法、月亮相位、月亮宫位。
- Tertiary progressions：月日映射。
- Solar arc：所有点太阳弧推进，相位搜索。
- Directions：primary directions 不同 arc、promissor/significator、mundane/zodiacal。
- Profections：年/月/日小限，lord of year。
- Returns：太阳、月亮、金星、火星、木星、土星返照。
- Transits：多条件搜索，如“土星合本命月亮且火星触发”。
- Eclipses：日月食到本命点，食季影响范围。
- Zodiacal releasing：Spirit/Fortune/Eros/Basis。
- Firdaria：昼夜盘、节点纳入、子限。
- Decennials/Monomoiria/Bounds releasing 等传统时主体系。

### 产品形态

- 时间轴：将所有推运事件汇总到一条可过滤时间线。
- 事件搜索器：用户输入星体/相位/容许度/时间范围，返回命中窗口。
- 事件回填：用户记录真实事件，系统反推哪些技法命中。
- 技法对照：同一事件显示“主限、流年、返照、法达、小限”的共同点。

## 印度 Jyotish

详见 `04-indian-and-global-systems.md`。这里强调工程要点：

- Rashi D1 必须支持北印、南印、东印样式。
- 分盘必须记录分割规则、边界、反转规则、奇偶规则。
- Ayanamsa 必须可选：Lahiri、Raman、Krishnamurti、Fagan/Bradley、Yukteswar、自定义。
- Nakshatra：27/28 宿、pada、lord、deity、symbol、guna、yoni、varna、nadi。
- Dasha：必须独立成可扩展引擎，而非 UI 内硬写。
- Yoga：规则库化，支持命中证据与强度评分。
- Ashtakavarga：BAV/SAV、bindu、transit scoring。
- Jaimini：Chara karaka、rashi drishti、argala、chara dasha。
- Tajika：年度盘、Muntha、Sahams、Yogas。

## 七政四余与中国星命

当前七政模块已有 Moira 风格工作。后续应形成：

- 七政：日月五星。
- 四余：紫气、月孛、罗喉、计都。
- 十二宫、二十八宿、命度、身度、主星、身宫。
- 果老星宗：格局、神煞、禄马贵人、化曜、虚实。
- 演禽：二十八宿与禽星。
- 中西天文参数对照：同一时间点的热带黄道、恒星黄道、中国星宿度数。

## 计算质量要求

### 回归测试

每个引擎至少准备三类测试：

- 金标准测试：对照 Astro.com、Swiss Ephemeris、Jagannatha Hora、Maitreya、Morinus、Solar Fire 等。
- 典籍案例测试：古籍命例或教材样例。
- 极端输入测试：高纬度、古代日期、闰秒附近、时区历史变更、无出生时。

### 精度显示

用户界面应显示“适用精度”：

- 星体黄经：秒/分级。
- 宫位：高纬度可能不可用或多解。
- 古代日期：Delta T 不确定性。
- 出生时间不准：宫位、月亮、上升、主限结果风险。

### 许可策略

Swiss Ephemeris 是强大但许可敏感。商业产品需确认商业授权或服务端隔离策略。若开源发布，AGPL 影响需要法务判断。JPL/SPICE、Astropy、Skyfield、PyMeeus 等也应逐项建立许可证表。

