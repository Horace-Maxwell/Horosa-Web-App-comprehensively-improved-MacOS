<p align="center">
  <img src="pic/kwj.png" alt="Kinwangji Logo" width="160" />
</p>

<h1 align="center">堅皇極經世 Kinwangji</h1>

<p align="center">
  <em>Python 實現邵雍《皇極經世》數術系統</em><br/>
  <em>Python implementation of Shao Yong's Huangji Jingshi cosmological system</em>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python 3.8+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://github.com/kentang2017/kinwangji/stargazers"><img src="https://img.shields.io/github/stars/kentang2017/kinwangji?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/kentang2017/kinwangji/network/members"><img src="https://img.shields.io/github/forks/kentang2017/kinwangji?style=social" alt="GitHub Forks"></a>
  <a href="https://github.com/kentang2017/kinwangji/issues"><img src="https://img.shields.io/github/issues/kentang2017/kinwangji" alt="GitHub Issues"></a>
</p>

<p align="center">
  <a href="#簡介">中文</a> •
  <a href="#introduction">English</a> •
  <a href="#安裝-installation">Install</a> •
  <a href="#使用方式-usage">Usage</a> •
  <a href="#贊助-donate--sponsor">Donate</a>
</p>

---

## 簡介 Introduction

邵雍（1011–1077），字堯夫，號康節，北宋五子之一，以先天易學與象數哲學聞名。
《皇極經世》窮三十年觀天地之消長，建構宇宙大數：
一元 = **129,600 年**（12會 × 30運 × 12世 × 30年）
一元十二會、一會三十運、一運十二世、一世三十年，週而復始，推演古今治亂興亡。

本專案以現代 Python 重現部分核心算法，並提供互動介面，讓使用者輸入日期即可觀察「皇極」視角下的時空定位。

**Huangji Jingshi** (皇極經世, *Book of Supreme World Ordering Principles*) was authored by Shao Yong (邵雍, 1011–1077), one of the Five Masters of Northern Song and a pioneer of *Xiantian* (先天) Yi-learning and image-number philosophy.

The work models cosmic time as a single **Yuan (元)** of **129,600 years**, subdivided into Hui (會), Yun (運), and Shi (世) cycles. This package provides core algorithms for those cycles, precise 24 solar-term calculations, and an interactive Streamlit app.

---

## 主要功能 Features

| Emoji | 功能 (中文) | Feature (English) |
|:-----:|-------------|-------------------|
| 🌿 | 二十四節氣精確計算（天文曆法） | Precise 24 solar-term calculation (astronomical) |
| 🔄 | 元會運世時間框架換算 | Yuan-Hui-Yun-Shi cycle conversion |
| 📍 | 皇極經世大數週期定位 | Cosmic cycle positioning (year → Shi → Yun → Hui → Yuan) |
| 🎵 | 聲音律呂基礎對應 | Sound & pitch-pipe mapping (basic) |
| 📜 | 歷史年表對照 | Historical chronology lookup |
| 🖥️ | Streamlit 互動網頁應用 | Streamlit interactive web app |

---

## 安裝 Installation

需要 Python 3.8+，建議使用虛擬環境。
Requires Python 3.8+. A virtual environment is recommended.

```bash
# PyPI（如已發佈 / if published）
pip install kinwangji

# 從 GitHub 安裝 / Install from GitHub
pip install git+https://github.com/kentang2017/kinwangji.git

# 本地開發安裝（可編輯模式）/ Local editable install
git clone https://github.com/kentang2017/kinwangji.git
cd kinwangji
pip install -e .

# 包含 Streamlit 應用依賴 / With Streamlit app dependencies
pip install -e ".[app]"
```

---

## 使用方式 Usage

```python
from kinwangji import wanji_four_gua, display_pan, jq

# 取得某日的皇極經世卦象 / Get Huangji gua for a date
result = wanji_four_gua(2025, 6, 15, 10, 30)
print(result)

# 取得節氣 / Get solar term
solar_term = jq(2025, 6, 15, 10, 30)
print(solar_term)

# 顯示完整排盤 / Display full pan layout
print(display_pan(2025, 6, 15, 10, 30))
```

```python
from kinwangji import load_history, history_for_year

# 載入歷史年表 / Load historical chronology
history = load_history()

# 查詢特定年份 / Query a specific year
info = history_for_year(2025)
print(info)
```

---

## Streamlit 網頁應用 Web App

互動式網頁介面，選擇日期即可查看皇極經世時空坐標。支援中英雙語切換。

An interactive web interface to explore Huangji Jingshi coordinates for any date. Supports Chinese/English toggle.

```bash
pip install -e ".[app]"
streamlit run app.py
```

---

## 專案結構 Project Structure

```
kinwangji/
├── kinwangji/          # 主要套件 / Main package
│   ├── __init__.py
│   ├── jieqi.py        # 節氣計算 / Solar-term calculation
│   ├── wanji.py        # 皇極經世核心算法 / Core algorithms
│   ├── history.py      # 歷史年表 / Historical chronology
│   └── data/
│       └── data.pkl    # 卦象資料 / Gua data
├── examples/           # 使用範例 / Examples
├── tests/              # 測試 / Tests
├── app.py              # Streamlit 應用 / Streamlit app
├── pyproject.toml      # 專案配置 / Project config
└── README.md
```

---

## 貢獻 Contributing

歡迎提交 Issue 或 Pull Request！請確保新增程式碼附帶測試。

Contributions are welcome! Please open an issue or pull request. Make sure new code includes tests.

---

## 贊助 Donate / Sponsor

如果這個專案對您有幫助，歡迎透過以下方式支持：

If this project is helpful, consider supporting it:

<p align="center">
  <a href="https://www.paypal.com/paypalme/kentang2017">
    <img src="https://img.shields.io/badge/PayPal-Donate-blue?logo=paypal" alt="Donate via PayPal" />
  </a>
</p>

⭐ 也歡迎給本專案一顆星，讓更多人看到！
⭐ A GitHub star also helps — thank you!

---

## 授權 License

本專案採用 [MIT License](https://opensource.org/licenses/MIT) 授權。

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
