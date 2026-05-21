# 04 印度与全球玄学系统

## 印度 Jyotish

### 基础概念

| 概念 | 说明 | APP 实现 |
| --- | --- | --- |
| Rashi | 十二星座/宫位，通常恒星黄道 | D1 主盘 |
| Bhava | 宫位，可用整宫或 bhava chalit | 宫位模式切换 |
| Graha | 九曜：日月五星、罗喉、计都 | 星体表与强弱 |
| Nakshatra | 27/28 月宿 | 宿、pada、主星、象义 |
| Ayanamsa | 恒星黄道岁差差值 | Lahiri 等可选 |
| Varga | 分盘 | D2-D60 |
| Dasha | 行运期 | 时间轴 |
| Yoga | 行星组合 | 规则命中 |
| Bala | 力量评分 | Shadbala、Vimshopaka 等 |
| Panchanga | 五历支 | 择日/日历 |

### 分盘路线

当前项目已有 D2、D3、D4、D5、D6、D7、D8、D9、D10、D11、D12、D16、D20、D24、D27、D30、D40、D45、D60 等代码资产。后续需要：

- 为每个分盘加入中文/英文名称、用途和规则说明。
- 明确分盘算法版本，尤其奇偶、正逆、起点差异。
- 分盘结果可叠加显示：D1 + D9 + D10 + D60。
- 分盘强度评分：同一行星在多分盘中的状态。

### Dasha 系统

优先级：

1. Vimshottari Dasha：最常用，必须 P0。
2. Yogini Dasha：P1。
3. Ashtottari、Shodashottari、Dwisaptati Sama、Shatabdika：P2。
4. Kalachakra Dasha：复杂但高价值，P1/P2。
5. Chara Dasha：Jaimini 必备，P1。
6. Narayana Dasha、Mandooka Dasha：P2。

功能形态：

- 大限/小限/子限时间轴。
- 当前 Dasha lord 的宫位、星座、Nakshatra、尊贵、相位、yoga。
- Dasha + transit + varga 共同触发。
- 事件回填，看哪些 Dasha 规则对用户命例最有解释力。

### Jaimini

需要实现：

- Chara Karaka：Atmakaraka、Amatyakaraka 等。
- Karakamsha：AK 在 D9 的位置。
- Rashi Drishti：星座相位，不同于 Parashara graha drishti。
- Argala：干预/阻隔。
- Chara Dasha。
- Jaimini yogas。

### Ashtakavarga

- Bhinna Ashtakavarga：每颗星对各宫 bindu。
- Sarvashtakavarga：总 bindu。
- Transit scoring：行运星经过高/低 bindu 区。
- Kakshya、Trikona Shodhana、Ekadhipatya Shodhana。

### Tajika 与年度盘

- Varshaphala 年度盘。
- Muntha。
- Sahams。
- Tajika yogas：Ithasala、Easarpha、Nakta、Yamaya 等。
- 年主、月主、日主。

### Prashna 与 Muhurta

- Prashna：问卜盘，需记录问题、问时、问地、问者状态。
- Muhurta：择时，结合 Panchanga、Tarabala、Chandrabala、Lagna、避凶时。
- Panchanga：Tithi、Vara、Nakshatra、Yoga、Karana 的日历视图。

### Nadi / KP

- Nadi：资料复杂，建议先知识库和案例库，再算法化。
- KP：Placidus-like cusp、stellar/sub-lord 体系，适合做专业插件。

## Vastu Shastra

印度空间玄学，应与风水并列：

- Vastu Purusha Mandala。
- 五元素与方向。
- 八方位神。
- 宅地形状、入口、房间分配。
- Ayadi 计算。
- 与 Jyotish 的命盘择向联动。

实现路径：

1. 简单户型方位分析。
2. Mandala 网格叠加。
3. 房间功能建议。
4. 与风水同屏对照。

## 玛雅历法与中美洲系统

### 核心

- Tzolkin：260 日，20 day signs x 13 numbers。
- Haab：365 日。
- Calendar Round：52 年循环。
- Long Count：长纪年。
- Lords of the Night 等扩展。

APP 功能：

- 日期换算。
- Day sign 解释。
- 生日图腾/能量解释。
- 重要事件日历。
- 与现代 Gregorian/Julian 对照。

注意：

- 需要避免 New Age 伪系统与传统资料混淆。
- 对活态文化保持来源说明。

## 阿拉伯、波斯与伊斯兰世界传统

### 阿拉伯/中世纪占星

- Lots/Parts：Fortune、Spirit、Marriage、Children 等。
- Annual Revolutions：太阳返照年度判断。
- Firdaria：当前 APP 已有相关。
- Dorothean triplicity rulers。
- Sahl、Masha'allah、Abu Ma'shar、Bonatti 传统。
- Lunar Mansions：28 月宿，和印度 Nakshatra、中国二十八宿可对照。

### Ilm al-raml / Geomancy

- 16 geomantic figures。
- 四母、四女、四侄、二证、一裁判。
- 十二宫或十六宫解释。
- 问题类型：求财、旅行、疾病、诉讼、婚姻。

实现：

- 随机点生成、手动输入、二进制输入。
- Shield chart、House chart。
- 图形含义、行星/元素/星座对应。
- 与西方 horary 的宫位对应。

### 字母数字

- Abjad：阿拉伯字母数值。
- Gematria：希伯来字母数值。
- Notarikon、Temurah。

适合作为“文字数理工具”，但要标注宗教/文化语境。

## 犹太卡巴拉与赫尔墨斯系统

- 生命树：十个 Sephiroth、二十二路径。
- 希伯来字母、塔罗大牌、行星、星座、元素对应。
- Gematria。
- Golden Dawn 对应体系。
- 行星日时、护符、仪式魔法。

产品形态：

- 对应表数据库。
- 生命树交互图。
- 塔罗/占星/字母三向联动。
- 仅作象征研究与教学，不鼓励危险仪式承诺。

## 非洲与非裔系统

### Ifa

- 256 Odu。
- Opele 或 Ikin 生成。
- 解释依赖训练有素祭司和口传语料。

产品策略：

- 先做资料索引与文化介绍。
- 若无可靠授权，不应伪装成“自动 Ifa 祭司”。
- 可做“结构学习工具”：Odu 编码、名称、公开资料引用。

### Diloggun / 贝壳占卜

- 贝壳开合数。
- Orisha 对应。
- 解释高度宗教化。

策略同 Ifa：尊重边界，先知识库。

### Sikidy

- 马达加斯加 geomancy。
- 与阿拉伯 raml/欧洲 geomancy 有结构亲缘。
- 可作为 geomancy 家族扩展。

## 欧洲民俗、北欧、凯尔特

### Runes

- Elder Futhark：24 字母。
- Younger Futhark、Anglo-Saxon Futhorc。
- 抽取、投掷、三符文、九符文、符文盘。
- 每个符文：音值、名称、诗篇、象征、正逆位争议。

实现：

- 符文卡库。
- 抽取随机性记录。
- 多套字母系统切换。
- 符文诗文本与翻译。

### Ogham

- 20 主字母 + forfeda。
- 树木/植物对应。
- 适合作为卡片/签条系统。

### 欧洲民俗择时

- 月相、星期行星、节气、圣徒日、农事历。
- 可接入“民俗日历”模块。

## 日本、韩国、越南、藏传

### 日本

- 九星气学：一白水星到九紫火星，本命星、月命星、方位。
- 六曜：先胜、友引、先负、仏灭、大安、赤口。
- 宿曜道：基于二十七宿，受印度/中国影响。
- 阴阳道：方忌、物忌等，资料需谨慎。

### 韩国/越南

- 四柱与风水本地化。
- 越南 Tử Vi 与紫微斗数同源但有本地术语。

### 藏传

- 藏历、五行、生肖、九宫、Parkha、Mewa。
- Mo 占：骰子/念珠等。
- Kalachakra astrology。

策略：先做历法与知识库，再做复杂预测。

## 纳入优先级

| 优先级 | 系统 | 原因 |
| --- | --- | --- |
| P0 | Jyotish 深化 | 当前分支重点，已有代码基础 |
| P0 | 中世纪/希腊化西占深化 | 与现有占星强相关 |
| P1 | Geomancy | 规则清晰，适合快速新增世界占卜 |
| P1 | Runes/Ogham | 卡牌化体验好，工程成本低 |
| P1 | Vastu | 可与风水/空间模块协同 |
| P2 | Mayan | 历法换算可做，解释需谨慎 |
| P2 | Kabbalah/Gematria | 知识图谱价值高 |
| P3 | Ifa/Diloggun | 文化与授权边界复杂，先资料化 |

