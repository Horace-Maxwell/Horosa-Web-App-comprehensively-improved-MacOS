# 神易數兵占 | Shenyishu Military Divination System

**講武全書兵佔卷之十六 · 明州玄谷蔡時宜撰**

---

[中文](#中文說明) | [English](#english)

## 中文說明

### 簡介

**神易數**是一套基於《講武全書》卷十六的古代兵佔推演系統。本系統運用天干地支、八卦、五行、神煞等傳統易學理論，對指定時間進行軍事吉凶推演，為研究中國古代兵學與易學的交叉領域提供工具。

### 功能特色

- 🔮 **干支推演** — 自動計算年、月、日、時四柱干支
- ☯️ **八卦與五行** — 連山卦、歸藏卦、八卦及五行分析
- ⚔️ **行軍佔** — 總數分析（主將、我兵、賊寇三方對比）
- 🏯 **主客判斷** — 陰陽數理判定主客形勢
- 🌟 **神煞系統** — 貴人、驛馬、天財、魁元、羊刃、正祿、白虎、血光、破碎、劫殺等
- 📊 **吉凶評分** — 綜合評分與等級（大吉、吉、平、凶、大凶）
- 🖥️ **多種介面** — 命令列（CLI）、JSON 輸出、Web 伺服器

### 安裝

```bash
pip install -r requirements.txt
```

### 使用方式

#### 命令列模式

```bash
# 基本使用（預設時間）
python shenyishu.py

# 指定時間
python shenyishu.py --year 2024 --month 3 --day 15 --hour 10

# 簡寫參數
python shenyishu.py -y 2024 -m 3 -d 15 -t 10
```

#### JSON 輸出

```bash
python shenyishu.py --year 2024 --month 3 --day 15 --hour 10 --json
```

#### Web 伺服器模式

```bash
# 啟動伺服器（預設埠 8080）
python shenyishu.py --server

# 指定埠
python shenyishu.py --server --port 9090
```

啟動後可訪問：
- 網頁介面：`http://localhost:8080`
- API 端點：`http://localhost:8080/api/bingzhan?year=2024&month=3&day=15&hour=10`

### API 參數

| 參數   | 說明   | 類型  | 預設值 |
|--------|--------|-------|--------|
| `year` | 年份   | int   | 2023   |
| `month`| 月份   | int   | 7      |
| `day`  | 日期   | int   | 4      |
| `hour` | 時辰   | int   | 22     |

### 系統依賴

- Python 3.6+
- [sxtwl](https://pypi.org/project/sxtwl/) — 壽星天文曆（中國農曆計算庫）

---

## English

### Introduction

**Shenyishu** (神易數) is an ancient Chinese military divination system based on Volume 16 of *"The Complete Book of Military Arts"* (講武全書). The system uses traditional Chinese metaphysics — Heavenly Stems and Earthly Branches (天干地支), Eight Trigrams (八卦), Five Elements (五行), and Spirit Stars (神煞) — to perform auspiciousness analysis for military affairs based on a given date and time.

### Features

- 🔮 **Stem-Branch Calculation** — Automatic computation of the Four Pillars (year, month, day, hour)
- ☯️ **Trigrams & Five Elements** — Lianshan, Guicang, Bagua, and Wuxing analysis
- ⚔️ **Military Analysis** — Numerical analysis of commander, troops, and enemy forces
- 🏯 **Host-Guest Judgment** — Yin-Yang determination of strategic positions
- 🌟 **Spirit Stars System** — Noble Person, Post Horse, Heavenly Wealth, Star Chief, Blade, Official Salary, White Tiger, Blood Light, Broken, Robbery Star, and more
- 📊 **Auspiciousness Score** — Comprehensive scoring with five levels (Great Fortune, Fortune, Neutral, Misfortune, Great Misfortune)
- 🖥️ **Multiple Interfaces** — CLI, JSON output, and Web server with UI

### Installation

```bash
pip install -r requirements.txt
```

### Usage

#### Command Line

```bash
# Basic usage (default date/time)
python shenyishu.py

# Specify date and time
python shenyishu.py --year 2024 --month 3 --day 15 --hour 10

# Short flags
python shenyishu.py -y 2024 -m 3 -d 15 -t 10
```

#### JSON Output

```bash
python shenyishu.py --year 2024 --month 3 --day 15 --hour 10 --json
```

#### Web Server

```bash
# Start server (default port 8080)
python shenyishu.py --server

# Custom port
python shenyishu.py --server --port 9090
```

Once running, access:
- Web UI: `http://localhost:8080`
- API endpoint: `http://localhost:8080/api/bingzhan?year=2024&month=3&day=15&hour=10`

### API Parameters

| Parameter | Description | Type | Default |
|-----------|-------------|------|---------|
| `year`    | Year        | int  | 2023    |
| `month`   | Month       | int  | 7       |
| `day`     | Day         | int  | 4       |
| `hour`    | Hour        | int  | 22      |

### Requirements

- Python 3.6+
- [sxtwl](https://pypi.org/project/sxtwl/) — Chinese Astronomical Calendar library

---

## 授權 | License

此項目僅供學術研究與文化傳承之用。

This project is for academic research and cultural heritage purposes.
