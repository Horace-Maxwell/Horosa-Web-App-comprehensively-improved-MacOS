<div align="center">

# 🌟 Python 太乙神數 | Kintaiyi 堅太乙

### 自古君王官臣珍重、上測天文下測國運必用之法 — 最豐富的開源太乙神數排盤工具

*The most authentic open-source Taiyi Shenshu (太乙神數) divination engine in Python*

[![PyPI version](https://img.shields.io/pypi/v/kintaiyi?color=blue&label=PyPI)](https://pypi.org/project/kintaiyi/)
[![Python](https://img.shields.io/pypi/pyversions/kintaiyi?label=Python)](https://pypi.org/project/kintaiyi/)
[![Downloads](https://img.shields.io/pypi/dm/kintaiyi?color=green&label=Downloads)](https://pypi.org/project/kintaiyi/)
[![CI](https://github.com/kentang2017/kintaiyi/actions/workflows/ci.yml/badge.svg)](https://github.com/kentang2017/kintaiyi/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/kentang2017/kintaiyi?style=social)](https://github.com/kentang2017/kintaiyi)
[![Telegram](https://img.shields.io/badge/Telegram-Channel-blue?logo=telegram)](https://t.me/numerology_coding)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?logo=paypal&style=flat-square)](https://www.paypal.me/kinyeah)

<br/>

[🚀 **立即在線體驗 Live Demo**](https://kintaiyi.streamlitapp.com) &nbsp;|&nbsp; [🎬 **YouTube 介紹**](https://www.youtube.com/watch?v=FKnPu8FOIlc) &nbsp;|&nbsp; [📦 **PyPI**](https://pypi.org/project/kintaiyi/) &nbsp;|&nbsp; [📖 **Wiki**](https://github.com/kentang2017/kintaiyi/wiki)

<br/>

![太乙神數盤圖](https://github.com/kentang2017/kintaiyi/blob/master/pic/Untitled-1.png?raw=true)


</div>

---

## 📑 目錄 Table of Contents

- [✨ 亮點 Highlights](#-亮點-highlights)
- [📖 簡介 Introduction](#-簡介-introduction)
- [🚀 快速開始 Quick Start](#-快速開始-quick-start)
- [📋 支援功能 Features](#-支援功能-features)
- [🖼️ 截圖與演示 Screenshots & Demo](#️-截圖與演示-screenshots--demo)
- [📦 安裝 Installation](#-安裝-installation)
- [🔧 進階使用 Advanced Usage](#-進階使用-advanced-usage)
- [🤝 貢獻指南 Contributing](#-貢獻指南-contributing)
- [💬 聯絡與社群 Contact & Community](#-聯絡與社群-contact--community)
- [📄 License](#-license)
- [🔗 相關專案 Related Projects](#-相關專案-related-projects)

---

- 🔮 **六種計法齊備** — 年計、月計、日計、時計、分計、命法，覆蓋所有太乙推算場景
  **Six Calculation Modes** — Year, Month, Day, Hour, Minute, and Life Destiny, covering all Taiyi divination scenarios
- 📜 **四大古法並存** — 太乙統宗、太乙金鏡、太乙淘金歌、太乙局，正宗古法不簡化
  **Four Classical Methods** — Taiyi Tongzong, Taiyi Jinjing, Taiyi Taojin Ge, and Taiyi Ju — authentic ancient formulas without simplification
- 📊 **輸出內容豐富** — 干支、局式、神煞、二十八宿、八門、八宮旺衰、兵陣預測、歷史年號對應
  **Rich Output** — Stems & Branches, board configuration, spirit indicators, 28 Lunar Mansions, Eight Gates, palace prosperity, battle predictions, and historical reign-year mapping
- 🏯 **歷史年號對照** — 內建完整中國歷代紀年與農曆換算
  **Historical Reign-Year Mapping** — Built-in complete Chinese dynastic chronology and lunar calendar conversion
- 🖥️ **多種使用方式** — Python API + Typer CLI + Streamlit 圖形介面，各取所需
  **Multiple Interfaces** — Python API + Typer CLI + Streamlit web GUI — use whichever suits your needs
- 🤖 **AI 智能分析** — 整合 Cerebras AI，可自動解讀盤面
  **AI-Powered Analysis** — Integrated with Cerebras AI for automatic board interpretation

---

## 📖 簡介 Introduction

**太乙神數**，與奇門遁甲、大六壬合稱「三式」，是中國古代最高層次的術數體系之一，專門用於推算天時國運與歷史變化規律。其法源於《易緯·乾鑿度》太乙行九宮法，相傳始於黃帝戰蚩尤之時，延續至今三千餘年。

**Tai Yi Shen Shu (太乙神數)**, together with Qi Men Dun Jia (奇門遁甲) and Da Liu Ren (大六壬), is known as the "Three Styles" (三式) — one of the highest-level divination systems in ancient China, specifically used for predicting celestial timing, national fortune, and historical patterns. The method originates from the *Yi Wei · Qian Zao Du* (易緯·乾鑿度) and the Taiyi Nine Palace traversal, said to date back to the era of the Yellow Emperor's battle against Chi You — over three thousand years ago.

**Kintaiyi 堅太乙**，取「堅守古法」之意。本套件嚴格依照古籍記載實現演算法，不做簡化、不作省略，旨在為太乙神數的研究者與愛好者提供一套**可驗證、可復現**的開源工具。無論是年運推算、國事預測，還是個人命理，皆可一鍵排盤。

**Kintaiyi (堅太乙)** means "steadfastly upholding ancient methods." This library strictly follows classical texts to implement its algorithms — no simplification, no omission — aiming to provide researchers and enthusiasts with a **verifiable and reproducible** open-source tool. Whether for yearly fortune prediction, national affairs forecasting, or personal destiny analysis, a complete divination board can be generated with a single command.

---

## 🚀 快速開始 Quick Start

### 安裝 Installation

```bash
pip install kintaiyi
```

選裝 CLI 或 Web 界面 / Optional extras for CLI or Web interface：

```bash
pip install kintaiyi[cli]       # 命令列工具 / Command-line tool (Typer CLI)
pip install kintaiyi[app]       # Streamlit 圖形介面 / Streamlit GUI
pip install kintaiyi[cli,app]   # 全部安裝 / Install all
```

### Python 程式碼範例 Python Code Example

```python
from kintaiyi.kintaiyi import Taiyi

# 排一個年計太乙盤 (Calculate a yearly Taiyi board)
result = Taiyi(2026, 3, 24, 12, 30).pan(ji_style=0, method=1)
print(result["太乙計"])       # → 年計
print(result["局式"])         # → {'文': '陽遁...', '數': ..., ...}
print(result["二十八宿值日"])  # → 二十八宿值日星
print(result["推主客相闗法"])  # → 主客勝負判斷
```

### CLI 命令列範例 CLI Examples

```bash
# 年計排盤 / Year calculation board
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode year --method 1

# 日計排盤，輸出 JSON / Day calculation board, output as JSON
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode day --output json

# 命法推算 / Life destiny calculation
kintaiyi calculate --date 1990-05-15 --time 08:00 --mode life --sex male
```

### Streamlit 一鍵啟動 Streamlit Quick Launch

```bash
pip install kintaiyi[app]
streamlit run apps/streamlit_app.py
```

---

## 📋 支援功能 Features

### 計法模式 Calculation Modes

| 模式 Mode | ji_style | 說明 Description |
|-----------|----------|-----------------|
| 年計 Year | `0` | 推算年運、國運大勢 / Predict yearly and national fortune trends |
| 月計 Month | `1` | 推算月份氣運吉凶 / Predict monthly auspiciousness and energy flow |
| 日計 Day | `2` | 推算日課吉凶 / Predict daily auspiciousness |
| 時計 Hour | `3` | 推算時辰吉凶 / Predict hourly auspiciousness |
| 分計 Minute | `4` | 現代延伸，精確至分鐘 / Modern extension, precise to the minute |
| 命法 Life | `5` | 個人命理推算 / Personal destiny calculation |

### 古法公式 Taiyi Methods

| 方法 Method | method | 來源 Source |
|------------|--------|------------|
| 太乙統宗 Taiyi Tongzong | `0` | 《太乙統宗寶鑑》*Taiyi Tongzong Baojian* |
| 太乙金鏡 Taiyi Jinjing | `1` | 《太乙金鏡式經》*Taiyi Jinjing Shi Jing* |
| 太乙淘金歌 Taiyi Taojin Ge | `2` | 《太乙淘金歌》*Taiyi Taojin Ge* |
| 太乙局 Taiyi Ju | `3` | 《太乙局》*Taiyi Ju* |

### 輸出內容 Output Fields

盤面輸出涵蓋以下資訊（Output includes but is not limited to）：

- **基本資訊** — 公元日期、農曆、干支五柱、歷史年號 / Basic Info — Gregorian date, lunar date, Five Pillars (stems & branches), historical reign year
- **局式** — 陰陽遁、局數、積年數、紀元 / Board Configuration — Yin/Yang escape, board number, accumulated years, epoch
- **太乙諸神** — 太乙、天乙、地乙、四神、直符、文昌、計神、合神 / Taiyi Spirits — Taiyi, Tianyi, Diyi, Four Spirits, Zhifu, Wenchang, Jishen, Heshen
- **主客算** — 主算、客算、定算，含三才數與格局判斷 / Host & Guest Calculations — host count, guest count, fixed count, including Three Powers (San Cai) numbers and pattern analysis
- **八門八宮** — 八門值事與分佈、八宮旺衰 / Eight Gates & Eight Palaces — gate assignments, distribution, and palace prosperity
- **二十八宿** — 值日宿、太歲宿、始擊宿及斷事 / 28 Lunar Mansions — duty mansion, Tai Sui mansion, initial-strike mansion, and interpretations
- **兵陣預測** — 推主客相關法、飛鳥助戰法、風雲諸法 / Battle Predictions — host-guest analysis, flying-bird battle assistance, wind-cloud techniques
- **七大兵法** — 雷公入水、臨津問道、獅子反擲、白雲捲空、猛虎相拒、白龍得雲、回軍無言 / Seven Military Strategies — Thunder Lord Enters Water, Asking the Way at the Ford, Lion's Reverse Throw, White Cloud Rolls the Sky, Fierce Tiger Standoff, White Dragon Seizes Cloud, Silent Army Retreat

---

## 🖼️ 截圖與演示 Screenshots & Demo

### 線上演示 Live Demo

👉 [**https://kintaiyi.streamlitapp.com**](https://kintaiyi.streamlitapp.com)

> 📌 大陸用戶可能需要使用 VPN 訪問 *(Mainland China users may need a VPN)*

### 盤圖預覽 Board Preview

<div align="center">

![太乙九宮分野圖](https://github.com/kentang2017/kintaiyi/blob/master/pic/%E5%A4%AA%E4%B9%99%E4%B9%9D%E5%AE%AE%E5%88%86%E9%87%8E%E5%9C%96.jpg?raw=true)

*太乙九宮分野圖 — Taiyi Nine Palace Sector Diagram*

</div>

---

## 📦 安裝 Installation

### 環境要求 Requirements

- Python ≥ 3.10

### 基本安裝 Basic Installation

```bash
pip install kintaiyi
```

### 可選依賴 Optional Extras

```bash
# CLI 命令列工具（基於 Typer）/ CLI command-line tool (based on Typer)
pip install kintaiyi[cli]

# Streamlit 圖形介面（完整 Web 應用）/ Streamlit GUI (full web application)
pip install kintaiyi[app]

# Flask Web 後端 / Flask web backend
pip install kintaiyi[web]

# 開發環境（pytest + ruff）/ Development environment (pytest + ruff)
pip install kintaiyi[dev]
```

### 從源碼安裝 Install from Source

```bash
git clone https://github.com/kentang2017/kintaiyi.git
cd kintaiyi
pip install -e ".[cli,app,dev]"
```

---

## 🔧 進階使用 Advanced Usage

### CLI 完整參數 CLI Options

```
kintaiyi calculate [OPTIONS]
```

| 參數 Option | 縮寫 | 說明 Description | 預設值 Default |
|-------------|------|-----------------|---------------|
| `--year` | `-y` | 公元年 Year | 當前年份 Current |
| `--month` | `-m` | 月 Month | 當前月份 Current |
| `--day` | `-d` | 日 Day | 當前日期 Current |
| `--hour` | `-H` | 時 Hour (0-23) | 當前小時 Current |
| `--minute` | `-M` | 分 Minute (0-59) | 當前分鐘 Current |
| `--date` | | 日期 Date (YYYY-MM-DD) | — |
| `--time` | | 時間 Time (HH:MM) | — |
| `--mode` | | 計法模式 Calculation mode | `year` |
| `--method` | | 古法公式 Classical method (0-3) | `0` |
| `--output` | `-o` | 輸出格式 Output format (text/json/markdown) | `text` |
| `--sex` | `-s` | 性別（命法時必填：male/female）Sex (required for life mode) | — |

```bash
# 查看版本 / Check version
kintaiyi version

# 使用個別參數 / Using individual parameters
kintaiyi calculate --year 1552 --month 9 --day 24 --hour 0 --minute 0 --mode year --method 1

# 使用日期字串 + JSON 輸出 / Using date string + JSON output
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode day --output json

# Markdown 表格輸出 / Markdown table output
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode hour --output markdown
```

### Python API

```python
from kintaiyi.kintaiyi import Taiyi

# 建立太乙物件 / Create a Taiyi object
taiyi = Taiyi(year=2026, month=3, day=24, hour=12, minute=30)

# 排盤 / Generate board
# ji_style: 0=年計 Year, 1=月計 Month, 2=日計 Day, 3=時計 Hour, 4=分計 Minute
# method:   0=統宗 Tongzong, 1=金鏡 Jinjing, 2=淘金歌 Taojin Ge, 3=太乙局 Taiyi Ju
result = taiyi.pan(ji_style=0, method=1)

# 命法推算 / Life destiny calculation
# Python API 使用中文 "男"/"女"；CLI 使用 male/female (Python API uses Chinese "男"/"女"; CLI uses male/female)
life_result = taiyi.taiyi_life(sex="男")  # "男" or "女"

# 結果為 dict，可直接轉 JSON / Result is a dict, can be directly converted to JSON
import json
print(json.dumps(result, ensure_ascii=False, indent=2))
```

### 輸出範例 Sample Output

```python
from kintaiyi.kintaiyi import Taiyi

result = Taiyi(1552, 9, 24, 0, 0).pan(ji_style=0, method=1)

# result 為 dict，包含 / result is a dict containing:
# {
#   "太乙計": "年計",                    # Calculation mode: Year
#   "太乙公式類別": "太乙金鏡",            # Method: Taiyi Jinjing
#   "公元日期": "1552年9月24日0時",        # Gregorian date
#   "干支": ["壬子", "庚戌", "丙戌", "戊子", "甲子"],  # Stems & Branches
#   "農曆": {"年": 1552, "月": 9, "日": 7},            # Lunar calendar
#   "年號": "明世宗朱厚熜 嘉靖三十一年",    # Historical reign year
#   "局式": {"文": "陽遁十三局", "數": 13, ...},  # Board config
#   "太乙落宮": 6,                        # Taiyi palace position
#   "太乙": "兌",                          # Taiyi trigram
#   "二十八宿值日": "翼",                  # 28 Mansions duty star
#   "推主客相闗法": "主尅客，主勝",         # Host-guest analysis
#   ...
# }
```

---

## 🤝 貢獻指南 Contributing

我們歡迎所有形式的貢獻！*All contributions are welcome!*

詳見 [CONTRIBUTING.md](CONTRIBUTING.md) / See [CONTRIBUTING.md](CONTRIBUTING.md) for full details.

- 🐛 **Bug 回報** — 提交 [Issue](https://github.com/kentang2017/kintaiyi/issues) / Report bugs via Issues
- ✨ **新功能** — 歡迎 PR 添加新古法、新計法 / PRs welcome for new methods and features
- 📚 **課例驗證** — 提供歷史課例以驗證演算法準確性 / Provide historical examples to verify algorithm accuracy
- 🌐 **翻譯** — 協助翻譯文檔或術語 / Help translate documentation or terminology
- ⭐ **Star** — 最簡單的支持方式！/ The easiest way to show your support!

### 開發環境設置 Development Setup

```bash
git clone https://github.com/kentang2017/kintaiyi.git
cd kintaiyi
pip install -e ".[dev]"

# 運行測試 / Run tests
pytest

# 代碼格式化 / Code formatting
ruff check src/ --fix
ruff format src/
```

---

## 💬 聯絡與社群 Contact & Community

| 渠道 Channel | 連結 Link |
|-------------|----------|
| 📢 Telegram 頻道 Channel | [numerology_coding](https://t.me/numerology_coding) |
| 💬 Telegram 私訊 DM | [haizhonggum](https://t.me/haizhonggum) |
| 🐛 GitHub Issues | [提交問題 Submit an Issue](https://github.com/kentang2017/kintaiyi/issues) |
| 💰 PayPal 捐助 Donate | [paypal.me/kinyeah](https://www.paypal.me/kinyeah) |

### 微信公眾號 WeChat Official Account

<div align="center">

![微信公眾號](https://raw.githubusercontent.com/kentang2017/kinliuren/refs/heads/master/pic/%E5%9C%96%E7%89%87_20260316084147.jpg)

</div>

---

<div align="center">

### ⭐ 喜歡這個專案？請給個 Star 支持！

### *Enjoying Kintaiyi? Give us a ⭐ on GitHub!*

[![Star this repo](https://img.shields.io/github/stars/kentang2017/kintaiyi?style=social)](https://github.com/kentang2017/kintaiyi)

</div>

---

## 📄 License

本專案採用 [MIT License](LICENSE) 開源協議。

This project is licensed under the [MIT License](LICENSE).

---

## 🔗 相關專案 Related Projects

| 專案 Project | 說明 Description | 連結 Link |
|-------------|-----------------|----------|
| 🔮 **堅奇門 kinqimen** | Python 奇門遁甲排盤 — Qi Men Dun Jia | [GitHub](https://github.com/kentang2017/kinqimen) |
| 🎴 **堅六壬 kinliuren** | Python 大六壬排盤 — Da Liu Ren | [GitHub](https://github.com/kentang2017/kinliuren) |

> 三式齊備，古法傳承 — *The Three Styles of Chinese divination, all open-sourced.*
