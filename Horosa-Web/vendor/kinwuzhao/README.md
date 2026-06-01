<div align="center">

# 🌟 Python 五兆占卜 | Kinwuzhao 堅五兆

### 唐宋官方法定的折竹彈占術 • 復原敦煌遺書與正史記載

*The Official Divination Method of Tang & Song Dynasties — Restored from Dunhuang Manuscripts & Historical Records*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://kinwuzhao.streamlit.app/)
[![GitHub](https://img.shields.io/github/stars/kentang2017/kinwuzhao?style=social)](https://github.com/kentang2017/kinwuzhao)

[![image](https://github.com/kentang2017/kinwuzhao/blob/main/pic/wuzhao.png)](https://kinwuzhao.streamlit.app/)

<a href="https://kinwuzhao.streamlit.app/">
  <img src="https://img.shields.io/badge/%E2%9C%A8%20%E7%AB%8B%E5%8D%B3%E7%B7%9A%E4%B8%8A%E9%AB%94%E9%A9%97%20Try%20Live%20Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo" />
</a>

</div>

---

## ✨ Highlights 亮點

- 🏛️ **堅守古法，正宗唐宋官占** — 嚴格依據敦煌寫本 P.2859《五兆要訣略》及正史記載復原
- 🎋 **折竹彈占，千年再現** — 以 Python 完整實現「折竹彈占謂之五兆」的占卜儀軌
- 🔮 **五行 × 六獸 × 孤虛** — 內建水火木金土五兆體系，搭配青龍、朱雀、螣蛇等六獸斷事
- 🌐 **Streamlit 一鍵體驗** — 無需安裝，瀏覽器即可占卜，暗色主題介面精美
- 📚 **學術級文獻支撐** — 附古籍書目索引，涵蓋隋唐宋三朝五兆典籍

---

## 📖 簡介 Introduction

**五兆**是中國古代重要的占卜方法之一，與龜卜、易占並列為唐代官方法定占卜術。

> 「折竹彈占謂之五兆」 — 宋·趙彥衛《雲麓漫鈔》

其核心定義源自《舊唐書·太宗紀上》，宋代梅堯臣詩作「五兆中開卦」更印證了此術在士大夫階層的廣泛應用。20 世紀初敦煌藏經洞出土的文獻 **P.2859《五兆要訣略》** 等寫本，系統保存了五兆占卜的完整儀軌與卦辭體系，為今日復原提供了珍貴的第一手資料。

**Kinwuzhao** 堅五兆正是基於這些敦煌遺書與正史文獻，以 Python 精確復原的五兆占卜工具。

> *Wuzhao (Five Prognostications) was one of the officially sanctioned divination methods during the Tang and Song dynasties in China. This project faithfully restores the ancient practice based on Dunhuang manuscript P.2859 and historical records such as the Old Book of Tang.*

---

## 🚀 快速開始 Quick Start

### 方式一：線上體驗（推薦）

直接訪問 Streamlit 應用，無需安裝任何依賴：

👉 **<https://kinwuzhao.streamlit.app/>**

### 方式二：本地運行

```bash
# 1. 克隆倉庫
git clone https://github.com/kentang2017/kinwuzhao.git
cd kinwuzhao

# 2. 建立並啟用虛擬環境（建議）
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 啟動應用
streamlit run app.py
```

啟動後瀏覽器將自動開啟 `http://localhost:8501`，即可開始占卜。

### 方式三：Python 模組引入

```python
import config
import jieqi
import kinwuzhao

# 計算干支（年、月、日、時、分）
gz = config.gangzhi(2025, 6, 27, 11, 24)
# gz = ['乙巳', '壬午', '丁卯', '丙午', '壬辰']

# 取得當前節氣
jq = jieqi.jq(2025, 6, 27, 11, 24)
# jq = '夏至'

# 干支起盤（完整五兆排盤）
result = kinwuzhao.gangzhi_paipan(gz, 0, jq, "六")
# result 包含：兆、木鄉、火鄉、土鄉、金鄉、水鄉 各宮位資訊

# 日干起盤
result = kinwuzhao.five_zhao_paipan(0, jq, "六", gz[1], gz[2])
```

---

## 🧩 支援功能 Features

| 功能 Feature | 說明 Description |
|:---|:---|
| 🎋 五兆占卜 | 完整復原折竹彈占流程 |
| 🐉 六獸配置 | 青龍、朱雀、螣蛇、勾陳、白虎、玄武自動排列 |
| ☯️ 孤虛判斷 | 陰孤虛、陽孤虛雙系統分析 |
| 🔄 四種起盤模式 | 日干起盤、時干起盤、分干起盤、干支起盤 |
| 📅 天干排盤 | 精確到分鐘的干支計算（五虎遁月、五鼠遁時、五狗遁分） |
| 🔄 王相胎沒死囚廢休 | 依節氣判斷八宮五行旺衰全週期 |
| 🔒 關鎖煞 | 依季節四關四籥，結合六壬天地盤轉換標注 |
| 🐲 六獸死害 | 六獸落宮死害自動判斷與提示 |
| ⚔️ 將軍 | 六壬將軍方位標注 |
| 🌙 暗色主題 | 精美 Streamlit 暗色介面，SVG 九宮格排盤 |

---

## 🔮 四種起盤模式 Divination Modes

| 模式 | 說明 | 適用場景 |
|:---|:---|:---|
| **日干起盤** | 以月干支、日干支為基準起盤 | 日常占事 |
| **時干起盤** | 以日干支、時干支為基準起盤 | 精確到時辰 |
| **分干起盤** | 以時干支、分干支為基準起盤 | 精確到分鐘 |
| **干支起盤** | 綜合年月日時分干支數值總和起盤 | 完整排盤 |

---


## 📁 專案結構 Project Structure

```
kinwuzhao/
├── app.py              # Streamlit 應用主程式（介面與互動邏輯）
├── kinwuzhao.py        # 五兆核心排盤算法（five_zhao_paipan、gangzhi_paipan）
├── config.py           # 基礎配置（干支計算、五行關係、納音、孤虛等）
├── jieqi.py            # 節氣計算模組（基於天文曆法精確推算）
├── requirements.txt    # Python 依賴清單
├── example.md          # 占卜案例
├── guji.md             # 五兆古籍書目索引（隋唐宋三朝）
├── log.md              # 更新日誌
├── icon.png            # 應用圖標
└── .streamlit/
    └── config.toml     # Streamlit 暗色主題配置
```

---

## 📦 依賴套件 Dependencies

| 套件 | 用途 |
|:---|:---|
| [streamlit](https://streamlit.io/) | Web 應用框架 |
| [pendulum](https://pendulum.eustace.io/) | 時區與日期時間處理 |
| [sxtwl](https://pypi.org/project/sxtwl/) | 農曆與干支計算 |
| [ephem](https://rhodesmill.org/pyephem/) | 天文曆法計算（節氣推算） |
| [kinliuren](https://github.com/kentang2017/kinliuren) | 大六壬天地盤（關鎖·將軍計算） |
| [bidict](https://bidict.readthedocs.io/) | 雙向字典（天地盤轉換） |
| [altair](https://altair-viz.github.io/) | 圖表視覺化 |
| [streamlit-aggrid](https://github.com/PablocFonseca/streamlit-aggrid) | 表格元件 |

> 所有依賴可透過 `pip install -r requirements.txt` 一鍵安裝。

---

## 📚 古籍文獻 Historical Sources

本專案參考之古籍書目涵蓋隋唐宋三朝，包括：

| 朝代 | 書名 |
|:---|:---|
| 隋 | 《龜卜五兆動搖訣》、《五兆算經》 |
| 唐 | 孫思邈《五兆算經》 |
| 宋 | 《五兆龜經》、《五兆金車口訣》、《五兆秘訣》、《五行見五兆法》等 |
| 敦煌寫本 | P.2859《五兆要訣略》、《五兆卜法殘卷》、《五兆經法要決》 |

完整書目請參閱 [`guji.md`](guji.md)。

---

## 🤝 貢獻指南 Contributing

歡迎對五兆占卜有興趣的朋友參與貢獻！

1. **Fork** 本倉庫
2. 創建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m "Add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 **Pull Request**

無論是文獻校勘、程式優化、介面改進或文檔翻譯，我們都非常歡迎。

> *Contributions are welcome! Whether it's textual collation of historical sources, code optimization, UI improvements, or translations — feel free to open a PR.*

---

## 📬 聯絡方式 Contact

如有任何問題或建議，歡迎透過以下方式聯繫：

- **GitHub Issues**：[提交 Issue](https://github.com/kentang2017/kinwuzhao/issues)
- **微信公眾號**：搜索關注作者公眾號，獲取更多術數研究內容

---

## 📄 License

本專案目前尚未指定開源授權協議。如需使用或二次開發，請先聯繫作者。

> *This project has not yet specified an open-source license. Please contact the author before use or redistribution.*

---

## 🔗 相關專案 Related Projects

| 專案 Project | 說明 Description | 連結 Link |
|:---|:---|:---|
| **堅奇門 Kinqimen** | Python 奇門遁甲 | [GitHub](https://github.com/kentang2017/kinqimen) |
| **堅太乙 Kintaiyi** | Python 太乙神數 | [GitHub](https://github.com/kentang2017/kintaiyi) |
| **堅六壬 Kinliuren** | Python 大六壬 | [GitHub](https://github.com/kentang2017/kinliuren) |

---

<div align="center">

**堅守古法 · 正宗唐宋官占 · 以 Python 復原千年智慧**

*Preserving ancient methods — Authentic Tang & Song dynasty divination — Restored with Python*

⭐ 如果這個專案對你有幫助，請給一顆 Star！

</div>
