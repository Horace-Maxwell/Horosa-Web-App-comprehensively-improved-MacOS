# **Python Taixuanshifa 太玄筮法**

[![Python](https://img.shields.io/pypi/pyversions/taixuanshifa)](https://pypi.org/project/taixuanshifa/)
[![PIP](https://img.shields.io/pypi/v/taixuanshifa)](https://pypi.org/project/taixuanshifa/)
[![Downloads](https://img.shields.io/pypi/dm/taixuanshifa)](https://pypi.org/project/taixuanshifa/)
[![TG](https://img.shields.io/badge/chat-on%20telegram-blue)](https://t.me/gnatnek)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?logo=paypal&style=flat-square)](https://www.paypal.me/kinyeah)&nbsp;

> A Python package for performing divinations using the ancient Chinese TaiXuan (太玄) system — an alternative to the I Ching created by the Confucian scholar Yang Xiong (BC 53 – 18 CE) of the Western Han Dynasty.

---

## Table of Contents

- [Features](#features-特色)
- [Introduction](#1-introduction-導讀)
- [Installation](#2-installation-安裝套件)
- [Quick Start](#3-quick-start-起卦)
- [Web Interface](#4-web-interface-網頁介面)
- [Contributing](#5-contributing-貢獻)
- [Donate](#6-donate-捐款)

---

## **Features 特色**

- 🔮 **81 Hexagrams** — Complete set of TaiXuan divination hexagrams with line-by-line interpretations
- 📅 **Date & Time Aware** — Divination incorporates Chinese lunar calendar and solar terms (節氣)
- 🌗 **Four Daily Periods** — Supports dawn (旦), midday (日中), evening (夕), and night (夜中) readings
- ⭐ **28 Star Lodges** — Integrates the traditional Chinese constellation system (二十八宿)
- 🌐 **Streamlit Web App** — Interactive web interface for easy divination
- 📦 **PyPI Package** — Installable via `pip` for use in your own Python projects

---

## **1. Introduction 導讀**

An alternative I Ching divination tool named TaiXuan created by a Chinese Confucian Yang Xiong (BC 53 – 18 CE) from the Western Han Dynasty.

《太玄》，又稱《太玄經》、《揚子太玄經》或《玄經》，是西漢學者揚雄的一部著作，用來闡述他的哲學體系和宇宙論。《四庫全書》中為避康熙皇帝的名諱，改稱其為《太元經》。《新唐書·藝文志》作十二卷，《文獻通考》作十卷。

《太玄》糅合了儒家、道家和陰陽家的學說。其首先從《老子》「玄之又玄」中概括出「玄」（玄奧）的概念，以玄為中心，按天地人三道的分類建立了一個形上學體系。《太玄》認為一切事物從發展到旺盛到消亡都可分成九個階段。

唐朝詩人李白的《俠客行》最後一句「白首太玄經」，即指此書。

<p align="center">
  <img src="https://github.com/kentang2017/taixuanshifa/blob/master/data/pic.png?raw=true" alt="太元方州部家八十一首圖" width="500">
  <br>
  <em>太元方州部家八十一首圖</em>
</p>

<p align="center">
  <img src="https://github.com/kentang2017/taixuanshifa/blob/master/pic/taixuan.png?raw=true" alt="太玄筮法" width="500">
  <br>
  <em>太玄筮法</em>
</p>

---

## **2. Installation 安裝套件**

```bash
pip install taixuanshifa
```

---

## **3. Quick Start 起卦**

### Perform a Divination 起卦

```python
from taixuanshifa import taixuanshifa

result = taixuanshifa.qigua()
print(result)
```

<details>
<summary>Example Output 輸出範例</summary>

```python
{
  '卦': {'眾': '陽氣信高懷齊，萬物宣明嫭大眾多。'},
  '初一': '冥兵始，火入耳，農輟馬穀，尸將班于田。測曰，「冥兵」之「始」、始則不臧也。',
  '次二': '兵無刃，師無陳，麟或賓之，溫。測曰，「兵無刃」、德服無方也。',
  '次三': '軍或纍車，丈人摧孥，內蹈之瑕。測曰，「軍或纍車」、廟戰內傷也。',
  '次四': '虎虓振廞，豹勝其祕否。測曰，「虎虓振廞」、如鷹之揚也。',
  '次五': '躆戰喈喈，若熊若螭。測曰，「躆戰喈喈」、恃力作王也。',
  '次六': '大兵雷霆，震其耳，維用詘腹。測曰，「大兵雷霆」、威震無疆也。',
  '次七': '旌旗絓羅，干戈蛾蛾，師孕言之，哭且䁲。測曰，「旌旗絓羅」、大恨民也。',
  '次八': '兵衰衰，見其病，不見輿尸。測曰，「兵衰衰」、不血刃也。',
  '上九': '斧刃缺，其柯折，可以止，不可以伐，往血。測曰，「刃缺」「柯折」、將不足往也。'
}
```

</details>

### Generate a Full Divination Chart 排盤

```python
from taixuanshifa import taixuanshifa

chart = taixuanshifa.Taixuan(2026, 3, 25, 10).pan()
print(chart)
```

---

## **4. Web Interface 網頁介面**

This project includes a **Streamlit web application** for interactive divination.

### Run Locally 本地運行

```bash
pip install -r requirements.txt
streamlit run app.py
```

The web interface lets you:
- 📅 Select a custom date and time
- 🔮 Generate a divination chart instantly
- 📖 Browse ancient texts (古籍)

---

## **5. Contributing 貢獻**

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## **6. Donate 捐款**

If you find this project helpful, please consider supporting its development:

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?logo=paypal&style=flat-square)](https://www.paypal.me/kinyeah)
