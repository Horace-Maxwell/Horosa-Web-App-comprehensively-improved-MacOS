# **Python 太乙神數 Kintaiyi 堅太乙 年計 月計 日計 時計 分計 命法**
[![Python](https://img.shields.io/pypi/pyversions/kintaiyi)](https://pypi.org/project/kintaiyi/)
[![PIP](https://img.shields.io/pypi/v/kintaiyi)](https://pypi.org/project/kintaiyi/)
[![Downloads](https://img.shields.io/pypi/dm/kintaiyi)](https://pypi.org/project/kintaiyi/)
[![TG Me](https://img.shields.io/badge/chat-on%20telegram-blue)](https://t.me/haizhonggum)
[![TG Channel](https://img.shields.io/badge/chat-on%20telegram-red)](https://t.me/numerology_coding)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?logo=paypal&style=flat-square)](https://www.paypal.me/kinyeah)&nbsp;

![alt text](https://github.com/kentang2017/kintaiyi/blob/master/pic/Untitled-1.png)
[![taiyishenshu](https://github.com/user-attachments/assets/84e345b2-29c9-407d-a2de-808ed407d5b5)](https://www.youtube.com/watch?v=FKnPu8FOIlc)

 ## 1. 導讀 Introduction
太乙神數是古代漢族占卜術的一種，與遁甲，六壬合稱三式，是推算天時以及歷史變化規律的術數學。周武王時以術數"卜世三十，卜年八百"推之，至邵雍形成歷史哲學而大備。據太乙神數推算，上古時有一年冬至日半夜，恰好日月合璧、五星連珠，定為甲子年、甲子月、甲子日、甲子時，稱作太極上元，上元甲子以來的年數，叫太乙積年。由太乙積年再求出太乙流年和太歲值卦，以斷本年各月的氣運凶吉，預測一些重大政治事件和天災人禍。採用五元六紀，三百六十年為一大周期，七十二年為一小周期，太乙每宮居三年，不入中宮，二十四年轉一周，七十二年遊三期。

太乙以一為太極生二目(主、客目)，二目生主客大小客與計神共八將。太乙乃天地之神，其星在太乙之前，統十六神而知風雨、水旱、兵革之事。昔黃帝與蚩尤大戰，適逢大霧，以霧書昏風後相，造指南車克之，是以取太乙之法，傳至今三千餘年，例目以為術數。外閱龍圖，內演龜文，凡天地之所以設君臣父子，之所以立陰陽，太乙了然演數則理昭著，太乙周行流運六十四卦，貴神入門十精之星，使經緯錯縮表理，集為一書。延續至今三千餘年不衰，為當今社會預測、決斷，提供了寶貴依據。

相傳太乙式產生于黃帝戰蚩尤時。其法大扺本于《易緯.乾鑿度》太乙行九宮法。採用五元六紀，三百六十年為一大周期，七十二年為一小周期，太乙每宮居三年，不入中宮，二十四年轉一周，七十二年遊三期。太乙以一為太極生二目(主、客目)，二目生主客大小客與計神共八將。(與易經太極分二儀，二儀生四象，四象生八卦相仿)。以太乙八將所乘十六神之方位關系定出格局。可佔內外祝福。又臨四時之分野，可佔水旱疾疫。再推三基五福大小遊二限，可預測古今治亂。又可推出年卦、月卦等。

因應現代都市人的需求，與時並進，就時計太乙的基礎上，下開分計太乙，至於果效，留待閣下驗證。

Tai Yi Shen Shu is a form of divination from China. It is also one of the Three Styles (三式; sānshì; 'three styles') of divination, the others being Da Liu Ren and Qi Men Dun Jia. Tai Yi Shen Shu is used to predict macroscopic events like wars or the meaning of supernovae. One form of Tai Yi Shen Shu has been popularized over the centuries to predict personal fortunes. Genghis Khan, emperor of China, referred to Tai Yi at one point to decide whether or not his planned invasion of Japan would succeed. When the Tai Yi count indicated that invasion would prove unsuccessful, Khan decided not to invade Japan that year. Numerous similar examples abound in classical Chinese literature, especially among the dynastic histories.

The methodology is quite similar to the other arts with a rotating heavenly plate and fixed earthly plate. While the art makes use of the 8 trigrams as well as the 64 hexagrams as a foundation, analysis is conducted from the Tai Yi Cosmic Board and the array of symbols found thereon, with special reference to the position of symbols in specific palaces. Important symbols include the Calculator, the Scholar, Tai Yi and Tai Yi, for example.

A number of spirits rotate around the sixteen palaces of the Tai Yi cosmic board, of which there are 72 cosmic boards for the Yin Dun period of each year, and 72 cosmic boards for the Yang Dun period of the year. The spirits land in different palaces with each configuration of the cosmic board. Each cosmic board contains a number of "counts" or numbers – the Host Count and the Guest Count taking primary importance over the Fixed Count.

含史事對照的多功能太鳦排盤 https://kintaiyi.streamlitapp.com (欲窮千里目，麻煩國內朋友擔條梯子看。)

Taiyishenshu, one of the Ancient Chinese Divinations, along with Qimendunjia and Dailiuren known as "three styles".


## 2. 安裝套件 Installation
```python
	pip install kintaiyi
	pip install --upgrade sxtwl, numpy, ephem, cn2an 
```
## 3. 起課方式 Quickstart
```python
	from kintaiyi import kintaiyi
    	year = 1552
    	month = 9
    	day = 24
    	hour = 0
    	minute = 0
	ji = 0 # 0 為年計；1 為月計；2 為日計：3 為時計；4 為分計
	method = 1 # 0 太乙統宗; 1: 太乙金鏡; 2: 太乙淘金歌; 3: 太乙局
    	print(Taiyi(year, month, day, hour, minute).kook(ji, method))
    
	{'太乙計': '年計', '太乙公式類別': '太乙金鏡', '公元日期': '1552年9月24日0時', '干支': ['壬子', '庚戌', '丙戌', '戊子', '甲子'], '農曆': {'年': 1552, '月': 9, '日': 7}, '年號': '明世宗朱厚熜 嘉靖三十一年', '紀元': '第四紀第四戊子元', '太歲': '子', '局式': {'文': '陽遁十三局', '數': 13, '年': '理天', '積年數': 1938109}, '五子元局': '陽遁二百二十九局', '陽九': '子', '百六': '丑', '太乙落宮': 6, '太乙': '兌', '天乙': '巳', '地乙': '乾', '四神': '中', '直符': '巽', '文昌': ['巽', ''], '始擊': '辰', '主算': [18, ['三才足數', '上和']], '主將': 8, '主參': 4, '客算': [19, ['三才足數', '雜重陽']], '客將': 9, '客參': 7, '定算': [19, ['三才足數', '雜重陽']], '合神': '丑', '計神': '寅', '定目': '辰', '君基': '酉', '臣基': '酉', '民基': '申', '五福': '坤', '帝符': '辰', '太尊': '子', '飛鳥': 4, '三風': 1, '五風': 5, '八風': 6, '大游': 5, '小游': 1, '二十八宿值日': '翼', '太歲二十八宿': '翼', '太歲值宿斷事': '陰陽失序，多雨水。', '始擊二十八宿': '心', '始擊值宿斷事': '太子、諸王有憂。', '十天干歲始擊落宮預測': '中國有兵。', '八門值事': '傷', '八門分佈': {6: '傷', 1: '杜', 8: '景', 3: '死', 4: '驚', 9: '開', 2: '休', 7: '生'}, '八宮旺衰': {7: '旺', 6: '相', 1: '胎', 8: '沒', 3: '死', 4: '囚', 9: '休', 2: '廢'}, '推太乙當時法': '太乙時計才顯示', '推三門具不具': '三門具。', '推五將發不發': '五將發。', '推主客相闗法': '主尅客，主勝', '推多少以占勝負': '客以多筭臨少，主人敗也。', '推太乙風雲飛鳥助戰法': '飛鳥扶主人陣者，主人勝', '推雷公入水': '子', '推臨津問道': '卯', '推獅子反擲': '卯', '推白雲捲空': '申', '推猛虎相拒': '未', '推白龍得雲': '戌', '推回軍無言': '酉'}


