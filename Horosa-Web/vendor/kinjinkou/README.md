# 堅金口 · kinjinkou

> 金口訣排盤 · Jin Kou Jue Divination Chart · 大六壬金口訣起課系統

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 目錄 · Table of Contents

- [中文說明](#中文說明)
- [English Description](#english-description)
- [Installation · 安裝](#installation--安裝)
- [Usage · 使用方法](#usage--使用方法)
- [Features · 功能特點](#features--功能特點)
- [Project Structure · 項目結構](#project-structure--項目結構)

---

## 中文說明

### 什麼是金口訣？

**金口訣**（又稱**大六壬金口訣**或**孫臏預測學**）是中國古代四大術數之一「六壬術」的簡化分支，相傳為戰國時期兵法大師**孫臏**所創。金口訣以天干地支為核心，結合月將、地分、神將等要素，通過嚴謹的推演體系，達到預測吉凶、分析事件的目的。

金口訣是中國傳統命理「三式」（太乙、奇門遁甲、大六壬）中大六壬的簡化版本，操作更為簡便，應用廣泛，是民間術數中極具實用性的預測工具。

### 核心要素

| 要素 | 說明 |
|------|------|
| **天干地支** | 年柱、月柱、日柱、時柱、分柱，五柱干支為起課基礎 |
| **地分** | 十二地支之一，代表所問事項的方位或主體 |
| **月將** | 太陽所在宮位，決定天盤佈局 |
| **地盤、天盤、神盤** | 三盤疊加，呈現完整的時空格局 |
| **四課** | 人元、貴神、將神、地分，四課是金口訣分析的骨架 |
| **納音五行** | 根據干支推算五行屬性，補充分析資訊 |
| **四大空亡** | 分析時空中的虛位，預示事件的缺失或障礙 |

### 排盤步驟

1. 輸入占問時的**公曆日期與時間**
2. 選擇**地分**（十二地支之一，代表所問方位或事項）
3. 系統自動計算干支、節氣、農曆
4. 自動佈置天地神三盤，列出四課、五行、旺衰分析

---

## English Description

### What is Jin Kou Jue (金口訣)?

**Jin Kou Jue** (literally *"Golden Mouth Formula"*), also known as **Sun Bin Predictive Studies (孫臏預測學)**, is a simplified branch of **Da Liu Ren (大六壬)** — one of the Three Arts (*San Shi* 三式) of classical Chinese divination alongside *Tai Yi* and *Qi Men Dun Jia*. It is traditionally attributed to **Sun Bin**, the legendary strategist of the Warring States period.

Unlike the more complex Da Liu Ren system, Jin Kou Jue distils the core mechanics into a more accessible framework while retaining deep analytical power. It uses the **Heavenly Stems and Earthly Branches (干支)** system along with **Spirit Generals (神將)**, **Monthly Commander (月將)**, and **Earth Segment (地分)** to construct a divination chart (*pan* 盤) that reveals the nature, timing, and outcome of inquired events.

### Niche & Context

Jin Kou Jue occupies a **unique niche** in the landscape of Chinese metaphysics:

- It is **faster to cast** than full Da Liu Ren, making it ideal for on-the-spot divination.
- It retains the **rich symbolism** of the Six Ren Generals (六壬神將) — 12 divine figures including Gui Ren (貴人), Teng She (螣蛇), Zhu Que (朱雀), Liu He (六合), Gou Chen (勾陳), Qing Long (青龍), Tian Kong (天空), Bai Hu (白虎), Tai Chang (太常), Xuan Wu (玄武), Tai Yin (太陰), and Tian Hou (天后).
- It is widely practised in **Hong Kong, Taiwan, and mainland China**, often used for decision-making in business, travel, relationships, and health.
- Its simplicity makes it **teachable and learnable** without years of formal study, unlike Qi Men Dun Jia or Zi Wei Dou Shu.

### How the Chart Works

A Jin Kou Jue divination chart (*paipan* 排盤) consists of:

| Component | Description |
|-----------|-------------|
| **Di Pan** (地盤) | The Earth Plate — fixed arrangement of the 12 Earthly Branches |
| **Tian Pan** (天盤) | The Heaven Plate — rotated according to the Monthly Commander |
| **Shen Pan** (神盤) | The Spirit Plate — placement of the 12 Generals |
| **Si Ke** (四課) | The Four Lessons — Human, Noble Spirit, General Spirit, Earth Segment |
| **Wu Xing** (五行) | Five Elements analysis — Metal, Wood, Water, Fire, Earth |
| **Yin Yang & Wang Shuai** | Polarity and vitality assessment of each element |
| **Na Yin** (納音) | Musical resonance five-element attributes of each pillar |
| **Kong Wang** (空亡) | Void/Emptiness — the four missing branches indicating obstacles |

---

## Installation · 安裝

### Requirements · 環境需求

- Python 3.8+
- [pendulum](https://pendulum.eustace.io/) `>=3.0.0`
- [streamlit](https://streamlit.io/) `>=1.24.0`
- [sxtwl](https://github.com/yuahr/sxtwl_cpp) `>=2.0.6`
- [ephem](https://rhodesmill.org/pyephem/) `>=4.1.6`

### Install · 安裝步驟

```bash
git clone https://github.com/kentang2017/kinjinkou.git
cd kinjinkou
pip install -r requirements.txt
```

---

## Usage · 使用方法

### Streamlit Web App · 網頁應用

```bash
streamlit run app.py
```

Open your browser and navigate to `http://localhost:8501`.

1. Select the **date and time** of inquiry in the sidebar.
2. Choose the **Earth Segment (地分)** from the 12 Earthly Branches.
3. The chart is computed and displayed automatically.

在左側邊欄選擇占問日期和時間，選擇地分，系統自動起課排盤。

### Python API

```python
import pendulum
from kinjinkou import JinkoujueApi

# Create an API instance
api = JinkoujueApi()

# Set inquiry datetime (Hong Kong timezone)
dt = pendulum.datetime(2024, 6, 15, 10, 30, tz='Asia/Hong_Kong')

# Cast the chart with Earth Segment (地分)
api.paipan(dt, difen='子')

# Print the result
print(api.print_pan())
```

### Direct Paipan (干支 Input)

```python
from kinjinkou import Paipan

pp = Paipan()
ganzhi = {
    '年柱': '甲子',
    '月柱': '丙寅',
    '日柱': '丙午',
    '时柱': '甲午',
    '文本': '甲子年 丙寅月 丙午日 甲午時'
}
pp.paipan(ganzhi, difen='子')
print(pp.output())
```

---

## Features · 功能特點

- ✅ **五柱干支計算** — Automatic calculation of Year, Month, Day, Hour, and Minute pillars from Gregorian date
- ✅ **節氣判斷** — Automatic solar term (*jieqi*) identification using precise astronomical calculation
- ✅ **農曆轉換** — Gregorian-to-Lunar date conversion
- ✅ **三盤佈局** — Full Earth, Heaven, and Spirit plate construction
- ✅ **四課分析** — Four Lesson derivation (人元、貴神、將神、地分)
- ✅ **五行旺衰** — Five Elements vitality analysis
- ✅ **納音五行** — Na Yin (Musical Element) attributes for each pillar
- ✅ **四大空亡** — Void branches analysis
- ✅ **Streamlit UI** — Interactive web interface with real-time chart generation
- ✅ **Python API** — Programmatic access for integration and automation

---

## Project Structure · 項目結構

```
kinjinkou/
├── app.py                  # Streamlit web application
├── jieqi.py                # Solar term & Ganzhi calculation
├── run_paipan.py           # CLI runner example
├── requirements.txt        # Python dependencies
└── kinjinkou/              # Core library
    ├── __init__.py
    ├── jinkoujue/
    │   ├── jinkoujue_api.py    # High-level JinkoujueApi class
    │   ├── _paipan.py          # Core Paipan (chart casting) logic
    │   └── _fenxi.py           # Analysis modules (traditional & quantitative)
    ├── utils/                  # Database & utility helpers
    └── wannianli/              # Perpetual calendar (萬年曆) module
```

---

## Related Projects · 相關項目

- [kinliuren](https://github.com/kentang2017/kinliuren) — Python 大六壬排盤 (Full Da Liu Ren divination system)

---

## License

MIT © [kentang2017](https://github.com/kentang2017)
