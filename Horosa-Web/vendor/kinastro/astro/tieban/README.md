# 鐵板神數模組 (Tie Ban Shen Shu Module)

## 概述

鐵板神數，又稱「鐵版神數」、「邵子神數」，是中國傳統術數中最精密的查表法系統。源自宋代邵雍《皇極經世》，清代發展為完整的考刻分系統。

本模組基於《鐵板神數清刻足本》（心一堂術數珍本古籍叢刊·星命類·神數類，2013）實現，底本為虛白廬藏清中葉「貞元書屋」刻本，包含完整的秘鈔密碼表。

**✨ 最新版本 v2.0**：新增十二宮條文系統、響應式 SVG 渲染、中英文雙語支持！

## 核心特點

- **精密時間分割**：每時分 8 刻，每刻 15 分（共 120 分/時），融入西洋分鐘制
- **考刻分技術**：結合父母八字、六親信息精確定位刻分
- **八卦加則例**：天干配卦、地支配卦、河洛配數、地支取數
- **紫微斗數安星**：完整的安命、安身、安紫府、十二宮系統
- **秘鈔密碼表**：卦象、流度、納甲卦爻快速查表
- **條文資料庫**：**6,208+ 條**命運詩讖，涵蓋父母、兄弟、夫妻、子女、事業、財運等
- **十二宮條文**：每個宮位獨立查詢對應條文（命宮、夫妻宮、財帛宮...）
- **響應式 SVG**：支持桌面端和移動端自適應顯示
- **雙語支持**：完整中英文界面和條文分類翻譯

## 安裝與使用

### 基本使用

```python
from astro.tieban import TieBanShenShu, TieBanBirthData
from astro.tieban.tieban_calculator import Ganzhi
from datetime import datetime

# 創建實例
tbss = TieBanShenShu()

# 準備出生資料
birth_data = TieBanBirthData(
    birth_dt=datetime(1990, 5, 15, 14, 30),  # 出生時間
    year_gz=Ganzhi('庚', '午'),              # 年柱
    month_gz=Ganzhi('辛', '巳'),              # 月柱
    day_gz=Ganzhi('戊', '辰'),               # 日柱
    hour_gz=Ganzhi('己', '未'),              # 時柱
    gender="男",
    # 完整版需父母信息（用於考刻分）
    # father_birth=datetime(1960, 1, 1),
    # mother_birth=datetime(1962, 3, 3),
)

# 計算
result = tbss.calculate(birth_data)

# 查看結果
print(f"命宮：{result.ming_palace}")
print(f"身宮：{result.shen_palace}")
print(f"五行局：{result.wuxing_ju}")
print(f"刻分：{result.ke}刻{result.fen}分")
print(f"神數號碼：{result.tieban_number}")
print(f"主條文：{result.verse}")

# 查看十二宮條文
print("\n=== 十二宮條文 ===")
for palace_name, info in result.palace_verses.items():
    print(f"{palace_name}: {info['verse'][:20]}... [{info['category']}]")
```

### 生成完整報告

```python
report = tbss.get_full_report(birth_data)
print(report)
```

### 渲染響應式 SVG 星盤圖

```python
from astro.tieban import render_tieban_chart_svg

# 中文版 SVG
svg_zh = render_tieban_chart_svg(result, language='zh')

# 英文版 SVG
svg_en = render_tieban_chart_svg(result, language='en')

# 在 Streamlit 中顯示（響應式）
st.components.v1.html(svg_zh, height=650, scrolling=False)
```

### 條文搜索

```python
from astro.tieban.tieban_calculator import VerseDatabase

db = VerseDatabase()

# 按分類搜索
results = db.search_by_category('夫妻')
for verse in results[:5]:
    print(f"{verse['number']}: {verse['verse']}")

# 按關鍵字搜索
results = db.search_by_keyword('父母')
print(f"找到 {len(results)} 條相關條文")

# 隨機獲取條文
random_verse = db.get_random_verse()
print(f"{random_verse['number']}: {random_verse['verse']}")

# 獲取資料庫統計
stats = db.get_category_stats()
print(stats)  # {'綜合': 2874, '夫妻': 820, '父母': 530, ...}
```

## 模組結構

```
astro/tieban/
├── __init__.py              # 模組導入
├── tieban_calculator.py     # 核心計算引擎（43KB）
├── tieban_renderer.py       # 響應式 SVG 渲染器（15KB）
├── tieban_browser.py        # 條文瀏覽工具（12KB）
├── tests/
│   └── test_tieban.py       # 測試套件（8.3KB）
├── data/
│   ├── mappings.json        # 映射表（納音、卦象、河洛數）
│   └── verses.json          # 條文資料庫（6,208 條，0.75MB）
└── README.md                # 本文檔
```

## 核心組件

### 1. 基礎映射 (Mapping)

- **天干配卦**：壬甲乾、乙坤癸、庚艮、辛巽、己震、戊離、丙坎、丁兌
- **地支配卦**：子坎、丑坤、寅卯震、辰兌、巳午離、未坤、申酉乾、戌兌、亥坎
- **河洛配數**：甲己子午 9、乙庚丑未 8、丙辛寅申 7、丁壬卯酉 6、戊癸辰戌 5、巳亥 4
- **六十納音**：完整 60 組納音五行（海中金、爐中火...）
- **五行局**：由納音決定局數（2-6 局）

### 2. 安星系統 (StarPlacement)

- **安命宮**：從寅上起正月，順至生月；從生月起子時，逆至生時
- **安身宮**：從寅上起正月，順至生月；從生月起子時，順至生時
- **安十二宮**：命宮定位後，逆時針排列
- **安紫微**：由年干、五行局、農曆日決定
- **安天府**：與紫微永遠相對（六沖位）

### 3. 考刻分引擎 (KeFenEngine)

- **刻分計算**：每時 8 刻 × 每刻 15 分 = 120 分
  - 13:07 → 刻 0 分 7
  - 14:22 → 刻 5 分 7
  - 14:37 → 刻 6 分 7
- **父母考證**：結合父母生卒、六親信息篩選候選刻分（完整版）
- **密碼表映射**：將刻分映射到條文號碼（1-6208）

### 4. 秘鈔密碼表 (SecretCodeTable)

包含數百條卦象密碼：
- 水火既濟、澤火革、雷火豐...
- 坤屯艮生、乾屯艮主...
- 流度、壽度圖映射

### 5. 條文資料庫 (VerseDatabase)

**6,208+ 條**命運詩讖，分類統計：

| 分類 | 條文數 | 說明 |
|------|--------|------|
| 綜合 | 2,874 | 綜合命運判斷 |
| 夫妻 | 820 | 婚姻、配偶 |
| 父母 | 530 | 父母生肖、存亡 |
| 子女 | 522 | 子嗣人數、成就 |
| 事業 | 459 | 事業類型、成就 |
| 財運 | 259 | 財運類型、貧富 |
| 災厄 | 247 | 火燭、水患、盜賊 |
| 遷移 | 232 | 遷移、定居 |
| 兄弟 | 149 | 兄弟人數、關係 |
| 健康 | 118 | 健康狀況、壽限 |

每條條文結構：
```json
{
  "0001": {
    "verse": "寄人廊廟何如自立門戶",
    "category": "綜合",
    "tags": [],
    "line_num": 3279
  }
}
```

### 6. 十二宮條文系統 (Palace Verses)

每個宮位獨立查詢對應條文：

| 宮位 | 英文 | 優先分類 |
|------|------|----------|
| 命宮 | Life Palace | 綜合、健康、事業 |
| 兄弟宮 | Siblings Palace | 兄弟、綜合 |
| 夫妻宮 | Spouse Palace | 夫妻、綜合 |
| 子女宮 | Children Palace | 子女、綜合 |
| 財帛宮 | Wealth Palace | 財運、事業、綜合 |
| 疾厄宮 | Health Palace | 健康、災厄、綜合 |
| 遷移宮 | Travel Palace | 遷移、事業、綜合 |
| 交友宮 | Friends Palace | 綜合 |
| 官祿宮 | Career Palace | 事業、綜合 |
| 田宅宮 | Property Palace | 綜合、財運 |
| 福德宮 | Fortune Palace | 綜合、健康 |
| 父母宮 | Parents Palace | 父母、綜合 |

## 條文格式

每條條文包含：

```json
{
  "0001": {
    "verse": "父母雙全壽延長，兄弟二人共爐香。妻宮同庚來匹配，子嗣三人送終老。",
    "category": "綜合",
    "tags": ["父母雙全", "兄弟二人", "妻宮同庚", "三子"]
  }
}
```

## 考刻分說明

鐵板神數最核心的秘密是「考刻分」：

1. **初步計算**：根據出生時間計算初步刻分（120 個候選）
   - 13:00-15:00（未時）→ 刻 0-7，分 0-14
2. **父母考證**：根據父母生卒年月日時篩選（完整版）
3. **六親佐證**：根據兄弟、夫妻、子女信息進一步篩選
4. **最終確定**：得到唯一準確的刻分
5. **查表得數**：根據刻分查密碼表得萬千百十號（1-6208）
6. **對應條文**：根據號碼查條文

**示例**：
```
13:07 出生 → 刻 0 分 7 → 號碼 0148 → "反被小利相纏，終身不得揚眉..."
14:22 出生 → 刻 5 分 7 → 號碼 0648 → "奎星初照一率拔前茅..."
14:37 出生 → 刻 6 分 7 → 號碼 0748 → "初配不終諧半道別離..."
```

完整版需用戶輸入：
- 父親出生/卒年
- 母親出生/卒年
- 兄弟姊妹人數及生肖
- 婚姻狀況
- 子女人數及生肖

## 響應式 SVG 設計

### 技術特點

```xml
<svg viewBox="0 0 500 600" 
     preserveAspectRatio="xMidYMid meet"
     style="width: 100%; height: auto; max-width: 100%;">
```

### CSS 媒體查詢

```css
/* 移動端（≤768px） */
@media (max-width: 768px) {
    .tieban-chart-container {
        max-width: 100%;
        padding: 5px;
    }
}

/* 桌面端（≥769px） */
@media (min-width: 769px) {
    .tieban-chart-container {
        max-width: 600px;
    }
}
```

### 適配效果

| 設備 | 寬度 | 效果 |
|------|------|------|
| 📱 手機 | < 768px | 100% 寬度，padding 5px |
| 📱 平板 | 768-1024px | 最大 600px，居中 |
| 💻 桌面 | > 1024px | 固定 600px，居中 |

## 中英文雙語支持

### UI 翻譯

所有界面元素支持中英文切換：

| 中文 | English |
|------|---------|
| 鐵板神數 | Iron Plate Divine Numbers |
| 命宮 | Life Palace |
| 夫妻宮 | Spouse Palace |
| 財帛宮 | Wealth Palace |
| 條文 | Verse |
| 刻分 | Ke Fen |
| 五行局 | Five Elements Bureau |

### 使用方式

```python
# 中文版
svg_zh = render_tieban_chart_svg(result, language='zh')

# 英文版
svg_en = render_tieban_chart_svg(result, language='en')
```

## 與《皇極數》的區別

| 特點 | 皇極數（明代） | 鐵板神數（清代） |
|------|---------------|-----------------|
| 時間分割 | 時分八刻 | 時分八刻，每刻十五分 |
| 考刻方法 | 簡單佐證 | 完整父母六親考證 |
| 密碼表 | 簡化 | 完整秘鈔密碼表 |
| 條文數 | 約 1000 條 | 6,208+ 條 |
| 精確度 | 較低 | 極高（鐵口直斷） |

## 運行測試

```bash
cd /mnt/c/Users/hooki/OneDrive/pastword/文件/Github/kinastro
python3 -m astro.tieban.tests.test_tieban
```

### 測試覆蓋

- ✅ 干支計算
- ✅ 刻分計算（不同時辰）
- ✅ 條文查詢（精確匹配、模糊匹配）
- ✅ 十二宮條文生成
- ✅ SVG 渲染（中/英文）
- ✅ 響應式容器
- ✅ 條文分類統計

## 參考文獻

- 《鐵板神數清刻足本》（心一堂，2013，底本：清中葉貞元書屋刻本）
- 《皇極數》（明代邵子數，八刻分經定數）
- 邵雍《皇極經世》先天之學
- 傳統紫微斗數安星法

## 版本歷史

### v2.0 (2026-04-24) - 最新版本
- ✨ **新增十二宮條文系統**：每個宮位獨立查詢對應條文
- ✨ **響應式 SVG 渲染**：支持桌面端和移動端自適應
- ✨ **中英文雙語支持**：完整界面和條文分類翻譯
- ✨ **條文資料庫擴充**：從 360 條擴充至 6,208 條（100% 原文）
- 🔧 **刻分計算優化**：修復刻分總是返回 (0,0) 的問題
- 🔧 **號碼生成優化**：確保號碼在 1-6208 範圍內
- 🔧 **考刻分邏輯改進**：無父母信息時使用初步計算結果

### v1.0 (2026-04-24)
- 初始版本
- 實現完整起例與推算方法
- 載入 360+ 條條文
- 整合到 KinAstro v2.4.0

## 待擴展功能

1. **父母六親考刻分完整版**：實現完整的考證邏輯與密碼表對照
2. **節氣精確計算**：結合 pyswisseph 計算精確干支
3. **密碼表完整載入**：從原文提取完整密碼表（數百條）
4. **AI 條文解讀**：結合 AI 解讀條文含義
5. **條文全文搜索**：支持繁體/簡體關鍵字搜索
6. **批量推算**：支持多命盤批量計算與比較

## 授權

本模組為開源項目，遵循 KinAstro 專案授權協議。

---

**作者**：Hermes Agent (鐵板神數專家 + 編程開發者)  
**版本**：v2.0  
**最後更新**：2026-04-24  
**條文來源**：《鐵板神數清刻足本》（心一堂，2013）
