# **Python Jingjue 荊訣**

[![Python](https://img.shields.io/pypi/pyversions/jingjue)](https://pypi.org/project/jingjue/)
[![PIP](https://img.shields.io/pypi/v/jingjue)](https://pypi.org/project/jingjue/)
[![Downloads](https://img.shields.io/pypi/dm/jingjue)](https://pypi.org/project/jingjue/)
[![TG](https://img.shields.io/badge/chat-on%20telegram-blue)](https://t.me/gnatnek)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?logo=paypal&style=flat-square)](https://www.paypal.me/kinyeah)&nbsp;

<img src="https://github.com/kentang2017/jingjue/blob/master/pic/jingjue.png" alt="jingjue" style="max-width: 100%; height: auto;">

---

## **1. 導讀 · Introduction**

### 中文簡介

《荊訣》是出土於北京大學所藏西漢竹書中的一篇占筮文獻，是迄今所見最完整的漢代算籌占卜法之一。全篇共記十六卦，卦名以天干地支命名，分別為：**甲、乙、丙、丁、戊、己、壬、癸**（天干）及**子、丑、寅、卯、辰、巳、午、未**（地支）。

《荊訣》原文記載占法如下：

> 「鑽龜告筮，不如荊訣。若陰若陽，若短若長。所蔔毋方，所占毋良，必察以明。卅筭以蔔其事，若吉若凶，唯筭所從。左手持書，右手操筭，必東面。用卅筭分，以為三分，其上分橫，中分從縱，下分橫。四四而除之，不盈者勿除。」

**起卦方法**：取三十根算籌，隨機分為上、中、下三份，各份以四除取餘數（餘數為零則視為四），三組餘數合為卦名，查表得卦辭，以判斷吉凶。《荊訣》與《易》之筮法相近，但自成一體，卦辭多具詩意，富含象徵意涵，描繪飛鳥、龍鳳、雲雨等自然意象，以此回應問卜者的疑問。

本系統卦辭文字內容參考自子居著[〈北大簡《荊訣》解析〉](http://xianqin.byethost10.com/2015/12/28/309)。

---

### English Introduction

**Jingjue (荊訣)** is an ancient Chinese divination text recovered from Western Han dynasty bamboo slips housed in the Peking University collection. It is one of the most complete surviving examples of Han-era stalk divination (算籌占), predating or contemporaneous with many received divinatory traditions.

The text records **sixteen hexagram-like figures (卦, Gua)**, each named after a Heavenly Stem (天干, Tiangan) or Earthly Branch (地支, Dizhi):

| Stems 天干 | Branches 地支 |
|-----------|--------------|
| 甲 乙 丙 丁 戊 己 壬 癸 | 子 丑 寅 卯 辰 巳 午 未 |

**How it works**:
Using **30 stalks (算籌)**, the diviner:
1. Divides the stalks into **three groups** (top, middle, bottom).
2. Calculates the **remainder of each group divided by 4** (a remainder of 0 counts as 4, giving values of 1–4).
3. The three remainders form a three-digit key that maps to one of the sixteen Gua.
4. The associated verse (卦辭) — often lyrical and imagery-rich, featuring birds, dragons, clouds, and travelling figures — is then interpreted to answer the diviner's question.

Jingjue shares structural similarities with the *Yi Jing* (易經) milfoil divination but stands as an independent system with its own poetic voice and symbolic vocabulary, offering a rare window into popular divination practice in early imperial China.

![cover](https://github.com/kentang2017/jingjue/blob/master/cover.jpg)

---

## **2. 十六卦一覽 · The Sixteen Gua**

| 卦名 | 關鍵詞 | Keyword |
|------|--------|---------|
| 甲 | 窮奇升天，中道而驚 | Danger mid-journey; beware of powerful spirits |
| 乙 | 龍處於澤，欲登於天 | Dragon ascending from the marsh; joyful occasion |
| 丙 | 有鳥將來，文身翠翼 | Colorful bird arriving; happiness without limit |
| 丁 | 百事順成，美人相知 | All affairs succeed; a beautiful meeting of minds |
| 戊 | 冥冥之海，獨得其光 | Light amid darkness; noble arrival foretold |
| 己 | 泰官甚敬，身獨遇惡 | Honours without, hardship within; inauspicious |
| 壬 | 鳳鳥不處，洋洋四國 | The Phoenix alights nowhere; efforts go unrewarded |
| 癸 | 玄鳥朝飛，洋洋翠羽 | The dark swallow soars; a person of promise draws near |
| 子 | 善哉首，如登高台 | A fine beginning; a distant traveller returns |
| 丑 | 道路矚望，美人不來 | Watching the road in vain; obstacles block the way |
| 寅 | 山有玄木，勞心將死 | Dark wood on the mountain; toil without recognition |
| 卯 | 藹藹者雲，蔽天白日 | Clouds veil the sun; desired meeting fails |
| 辰 | 玄龍在淵，嘉賓將來 | Black dragon in the deep; honoured guest arrives |
| 巳 | 時命將合，百事皆成 | Destined union; all endeavours meet with success |
| 午 | 前如凶，後乃吉光 | Hardship before, brightness after; a turning point |
| 未 | 釋哉心乎，翩翩飛鵠 | The heart unsettled; prayers go unanswered |

---

## **3. 安裝套件 · Installation**

```bash
pip install jingjue
```

---

## **4. 起課方式 · Usage**

```python
from jingjue import jingjue

# Cast a divination and retrieve the result
result = jingjue.qigua()

# result[0] — Gua name (卦名), e.g. "辰"
# result[1] — Gua verse (卦辭), e.g. "玄龍在淵，雲待在天..."
print("干卦：", result[0])
print("卦義：", result[1])
```

**Sample output:**

```
干卦： 辰
卦義： 玄龍在淵，雲待在天。嘉賓將來，以我為親。往來如矢，人莫之止。今日何如，如得父母。盈意中欲，其後不悔。吉，祟社。
```

---

## **5. 網頁版 · Web App**

An interactive web application built with **Streamlit** is included (`app.py`).
It allows you to cast a divination and view the Gua name and verse directly in your browser.

```bash
streamlit run app.py
```

---

## **6. 參考資料 · References**

- 子居，[〈北大簡《荊訣》解析〉](http://xianqin.byethost10.com/2015/12/28/309)，先秦史研究室網站，2015年12月28日。
- 北京大學藏西漢竹書整理小組，《北京大學藏西漢竹書》，上海古籍出版社。
