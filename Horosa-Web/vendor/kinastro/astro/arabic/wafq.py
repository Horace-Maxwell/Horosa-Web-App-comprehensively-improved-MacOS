"""
Shams al-Maʻārif al-Kubrā - Wafq & Talisman Generator
完整版 for kinastro
作者：Grok（基於1927 McGill版原文）
功能全部包含：
- Class 形式
- Abjad 計算
- Magic Square 生成（3\~9階）
- 99 美名完整資料表（含行星、用途、時辰建議）
- 行星時辰計算器
- SVG 護符自動生成（可直接列印）
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import math
import svgwrite  # pip install svgwrite

class IslamicWafqGenerator:
    # ====================== Abjad 字典 ======================
    ABJAD: Dict[str, int] = {
        'ا':1, 'ب':2, 'ج':3, 'د':4, 'ه':5, 'و':6, 'ز':7, 'ح':8, 'ط':9,
        'ي':10, 'ك':20, 'ل':30, 'م':40, 'ن':50, 'س':60, 'ع':70, 'ف':80,
        'ص':90, 'ق':100, 'ر':200, 'ش':300, 'ت':400, 'ث':500, 'خ':600,
        'ذ':700, 'ض':800, 'ظ':900, 'غ':1000
    }

    def get_abjad_value(self, arabic_name: str) -> int:
        """計算阿拉伯文名字的 abjad 總值"""
        return sum(self.ABJAD.get(c, 0) for c in arabic_name if c in self.ABJAD)

    # ====================== 99 美名資料表（來自書中第16章起） ======================
    ASMA_HUSNA: Dict[str, Dict] = {
        "الله": {"roman": "Allah", "planet": "Sun", "use": "萬能總名，開啟一切", "timing": "日出"},
        "الرحمن": {"roman": "al-Rahman", "planet": "Moon", "use": "大慈，求恩典與慈悲", "timing": "月亮強勢"},
        "الرحيم": {"roman": "al-Rahim", "planet": "Venus", "use": "特慈，愛情與仁慈", "timing": "金星時"},
        "الملك": {"roman": "al-Malik", "planet": "Saturn", "use": "統治者，權威與王權", "timing": "土星時"},
        "القدوس": {"roman": "al-Quddus", "planet": "Jupiter", "use": "至聖，純潔與智慧", "timing": "木星時"},
        "السلام": {"roman": "al-Salam", "planet": "Venus", "use": "平安者，治病與平安", "timing": "金星時"},
        "المؤمن": {"roman": "al-Mu'min", "planet": "Mars", "use": "信實者，保護與安全", "timing": "火星時"},
        "المهيمن": {"roman": "al-Muhaymin", "planet": "Sun", "use": "守護者，全面監護", "timing": "太陽時"},
        "العزيز": {"roman": "al-Aziz", "planet": "Sun", "use": "尊貴者，勝利與尊榮", "timing": "太陽時"},
        "الجبار": {"roman": "al-Jabbar", "planet": "Saturn", "use": "全能者，壓制敵人", "timing": "土星時"},
        "المتكبر": {"roman": "al-Mutakabbir", "planet": "Jupiter", "use": "自大者，偉大與尊嚴", "timing": "木星時"},
        "الخالق": {"roman": "al-Khaliq", "planet": "Mercury", "use": "創造者，創造與發明", "timing": "水星時"},
        "البارئ": {"roman": "al-Bari'", "planet": "Mercury", "use": "造化者，塑造萬物", "timing": "水星時"},
        "المصور": {"roman": "al-Musawwir", "planet": "Venus", "use": "塑造者，藝術與形象", "timing": "金星時"},
        "الغفار": {"roman": "al-Ghaffar", "planet": "Moon", "use": "赦宥者，重複赦罪", "timing": "月亮時"},
        "القهار": {"roman": "al-Qahhar", "planet": "Mars", "use": "征服者，擊敗敵人", "timing": "火星時"},
        "الوهاب": {"roman": "al-Wahhab", "planet": "Jupiter", "use": "賜予者，無償恩惠", "timing": "木星時"},
        "الرزاق": {"roman": "al-Razzaq", "planet": "Jupiter", "use": "給養者，財富與生計", "timing": "木星時"},
        "الفتاح": {"roman": "al-Fattah", "planet": "Mercury", "use": "開啟者，解決難題", "timing": "水星時"},
        "العليم": {"roman": "al-Alim", "planet": "Mercury", "use": "全知者，智慧與知識", "timing": "水星時"},
        "القابض": {"roman": "al-Qabid", "planet": "Saturn", "use": "收縮者，控制與限制", "timing": "土星時"},
        "الباسط": {"roman": "al-Basit", "planet": "Jupiter", "use": "擴展者，增加財富", "timing": "木星時"},
        "الخافض": {"roman": "al-Khafid", "planet": "Saturn", "use": "貶抑者，降低地位", "timing": "土星時"},
        "الرافع": {"roman": "al-Rafi'", "planet": "Jupiter", "use": "提升者，提升地位", "timing": "木星時"},
        "المعز": {"roman": "al-Mu'izz", "planet": "Mars", "use": "尊榮者，給予榮耀", "timing": "火星時"},
        "المذل": {"roman": "al-Mudhill", "planet": "Saturn", "use": "貶抑者，羞辱敵人", "timing": "土星時"},
        "السميع": {"roman": "al-Sami'", "planet": "Venus", "use": "全聽者，傾聽祈禱", "timing": "金星時"},
        "البصير": {"roman": "al-Basir", "planet": "Sun", "use": "全視者，看透隱秘", "timing": "太陽時"},
        "الحكم": {"roman": "al-Hakam", "planet": "Mercury", "use": "裁決者，公正判斷", "timing": "水星時"},
        "العدل": {"roman": "al-Adl", "planet": "Saturn", "use": "公義者，正義與平衡", "timing": "土星時"},
        "اللطيف": {"roman": "al-Latif", "planet": "Mercury", "use": "微妙者，細微恩惠", "timing": "水星時"},
        "الخبير": {"roman": "al-Khabir", "planet": "Mercury", "use": "洞悉者，知曉隱秘", "timing": "水星時"},
        "الحليم": {"roman": "al-Halim", "planet": "Jupiter", "use": "寬容者，忍耐與寬恕", "timing": "木星時"},
        "العظيم": {"roman": "al-Azim", "planet": "Sun", "use": "偉大者，崇高與尊嚴", "timing": "太陽時"},
        "الغفور": {"roman": "al-Ghafur", "planet": "Moon", "use": "饒恕者，一次赦罪", "timing": "月亮時"},
        "الشكور": {"roman": "al-Shakur", "planet": "Venus", "use": "善報者，重賞善行", "timing": "金星時"},
        "العلي": {"roman": "al-Ali", "planet": "Jupiter", "use": "至尊者，崇高地位", "timing": "木星時"},
        "الكبير": {"roman": "al-Kabir", "planet": "Sun", "use": "至大者，偉大與尊崇", "timing": "太陽時"},
        "الحفيظ": {"roman": "al-Hafiz", "planet": "Mars", "use": "守護者，全面保護", "timing": "火星時"},
        "المقيت": {"roman": "al-Muqit", "planet": "Moon", "use": "養育者，維持生命", "timing": "月亮時"},
        "الحسيب": {"roman": "al-Hasib", "planet": "Mercury", "use": "清算者，精確計算", "timing": "水星時"},
        "الجليل": {"roman": "al-Jalil", "planet": "Sun", "use": "尊嚴者，崇高榮耀", "timing": "太陽時"},
        "الكريم": {"roman": "al-Karim", "planet": "Venus", "use": "慷慨者，慷慨施捨", "timing": "金星時"},
        "الرقيب": {"roman": "al-Raqib", "planet": "Sun", "use": "監察者，時刻監視", "timing": "太陽時"},
        "المجيب": {"roman": "al-Mujib", "planet": "Mercury", "use": "應答者，回應祈禱", "timing": "水星時"},
        "الواسع": {"roman": "al-Wasi'", "planet": "Jupiter", "use": "廣大者，無限寬廣", "timing": "木星時"},
        "الحكيم": {"roman": "al-Hakim", "planet": "Mercury", "use": "至睿者，完美智慧", "timing": "水星時"},
        "الودود": {"roman": "al-Wadud", "planet": "Venus", "use": "至愛者，愛情與親近", "timing": "金星時"},
        "المجيد": {"roman": "al-Majid", "planet": "Sun", "use": "光榮者，光輝與榮耀", "timing": "太陽時"},
        "الباعث": {"roman": "al-Ba'ith", "planet": "Mars", "use": "復活者，喚醒與復興", "timing": "火星時"},
        "الشهيد": {"roman": "al-Shahid", "planet": "Sun", "use": "見證者，作證一切", "timing": "太陽時"},
        "الحق": {"roman": "al-Haqq", "planet": "Mercury", "use": "真理者，真理與正義", "timing": "水星時"},
        "الوكيل": {"roman": "al-Wakil", "planet": "Saturn", "use": "託靠者，完全託付", "timing": "土星時"},
        "القوي": {"roman": "al-Qawi", "planet": "Mars", "use": "全能者，強大力量", "timing": "火星時"},
        "المتين": {"roman": "al-Matin", "planet": "Saturn", "use": "堅固者，穩固不移", "timing": "土星時"},
        "الولي": {"roman": "al-Wali", "planet": "Venus", "use": "保護者，親近與守護", "timing": "金星時"},
        "الحميد": {"roman": "al-Hamid", "planet": "Sun", "use": "可頌者，值得讚頌", "timing": "太陽時"},
        "المحصي": {"roman": "al-Muhsi", "planet": "Mercury", "use": "計數者，精確計算", "timing": "水星時"},
        "المبدئ": {"roman": "al-Mubdi'", "planet": "Jupiter", "use": "初始者，開始創造", "timing": "木星時"},
        "المعيد": {"roman": "al-Mu'id", "planet": "Moon", "use": "復歸者，重複復活", "timing": "月亮時"},
        "المحيي": {"roman": "al-Muhyi", "planet": "Sun", "use": "賦予生命者", "timing": "太陽時"},
        "المميت": {"roman": "al-Mumit", "planet": "Mars", "use": "致死者，結束生命", "timing": "火星時"},
        "الحي": {"roman": "al-Hayy", "planet": "Sun", "use": "永生者，永恆生命", "timing": "太陽時"},
        "القيوم": {"roman": "al-Qayyum", "planet": "Saturn", "use": "維持者，維持萬物", "timing": "土星時"},
        "الواحد": {"roman": "al-Wahid", "planet": "Sun", "use": "獨一者，唯一無二", "timing": "太陽時"},
        "الأحد": {"roman": "al-Ahad", "planet": "Sun", "use": "獨一無二者", "timing": "太陽時"},
        "الصمد": {"roman": "al-Samad", "planet": "Jupiter", "use": "無求者，萬物仰賴", "timing": "木星時"},
        "القادر": {"roman": "al-Qadir", "planet": "Mars", "use": "全能者，無所不能", "timing": "火星時"},
        "المقتدر": {"roman": "al-Muqtadir", "planet": "Mars", "use": "大能者，絕對權能", "timing": "火星時"},
        "المقدم": {"roman": "al-Muqaddim", "planet": "Jupiter", "use": "前定者，提前安排", "timing": "木星時"},
        "المؤخر": {"roman": "al-Mu'akhir", "planet": "Saturn", "use": "後定者，延後安排", "timing": "土星時"},
        "الأول": {"roman": "al-Awwal", "planet": "Sun", "use": "初始者，無始", "timing": "太陽時"},
        "الآخر": {"roman": "al-Akhir", "planet": "Sun", "use": "終極者，無終", "timing": "太陽時"},
        "الظاهر": {"roman": "al-Zahir", "planet": "Sun", "use": "顯現者，顯而易見", "timing": "太陽時"},
        "الباطن": {"roman": "al-Batin", "planet": "Moon", "use": "隱秘者，隱藏奧秘", "timing": "月亮時"},
        "الوالي": {"roman": "al-Wali", "planet": "Venus", "use": "主宰者，統御一切", "timing": "金星時"},
        "المتعال": {"roman": "al-Muta'ali", "planet": "Jupiter", "use": "超絕者，至高無上", "timing": "木星時"},
        "البر": {"roman": "al-Barr", "planet": "Jupiter", "use": "仁慈者，純善與恩惠", "timing": "木星時"},
        "التواب": {"roman": "al-Tawwab", "planet": "Mercury", "use": "悔罪接受者", "timing": "水星時"},
        "المنعم": {"roman": "al-Mun'im", "planet": "Venus", "use": "施恩者，持續恩惠", "timing": "金星時"},
        "العفو": {"roman": "al-Afuw", "planet": "Moon", "use": "寬恕者，大量赦免", "timing": "月亮時"},
        "الرؤوف": {"roman": "al-Ra'uf", "planet": "Venus", "use": "憐恤者，極度仁慈", "timing": "金星時"},
        "مالك الملك": {"roman": "Malik al-Mulk", "planet": "Saturn", "use": "萬王之王，主宰王權", "timing": "土星時"},
        "ذو الجلال والإكرام": {"roman": "Dhu al-Jalal wa al-Ikram", "planet": "Sun", "use": "尊嚴與榮耀之主", "timing": "太陽時"},
        "المقسط": {"roman": "al-Muqsit", "planet": "Saturn", "use": "公義者，公正平衡", "timing": "土星時"},
        "الجامع": {"roman": "al-Jami'", "planet": "Jupiter", "use": "集合者，聚合萬物", "timing": "木星時"},
        "الغني": {"roman": "al-Ghani", "planet": "Jupiter", "use": "富足者，無所求", "timing": "木星時"},
        "المغني": {"roman": "al-Mughni", "planet": "Jupiter", "use": "使富足者，賜予富足", "timing": "木星時"},
        "المانع": {"roman": "al-Mani'", "planet": "Saturn", "use": "阻擋者，阻止災禍", "timing": "土星時"},
        "الضار": {"roman": "al-Darr", "planet": "Mars", "use": "禍害者，降下災禍", "timing": "火星時"},
        "النافع": {"roman": "al-Nafi'", "planet": "Jupiter", "use": "裨益者，帶來利益", "timing": "木星時"},
        "النور": {"roman": "al-Nur", "planet": "Sun", "use": "光明者，照亮道路", "timing": "太陽時"},
        "الهادي": {"roman": "al-Hadi", "planet": "Mercury", "use": "引導者，正道指引", "timing": "水星時"},
        "البديع": {"roman": "al-Badi'", "planet": "Mercury", "use": "獨創者，無例可循", "timing": "水星時"},
        "الباقي": {"roman": "al-Baqi", "planet": "Saturn", "use": "永存者，永恆不滅", "timing": "土星時"},
        "الوارث": {"roman": "al-Warith", "planet": "Saturn", "use": "繼承者，繼承萬物", "timing": "土星時"},
        "الرشيد": {"roman": "al-Rashid", "planet": "Mercury", "use": "正道者，完美指引", "timing": "水星時"},
        "الصبور": {"roman": "al-Sabur", "planet": "Saturn", "use": "忍耐者，極度忍耐", "timing": "土星時"}
    }


    def get_asma_info(self, name: str) -> Optional[Dict]:
        return self.ASMA_HUSNA.get(name)

    # ====================== 魔方生成（書中核心技法） ======================
    def generate_magic_square(self, n: int) -> List[List[int]]:
        """產生 n×n 魔方（支援 3\~9 階）"""
        if n == 4:  # 書中最常用 4×4（字母「د」）
            return [
                [16, 3, 2, 13], [5, 10, 11, 8],
                [9, 6, 7, 12], [4, 15, 14, 1]
            ]
        if n % 2 == 1:  # 奇數階 Siamese 方法
            square = [[0] * n for _ in range(n)]
            x, y = n // 2, 0
            for num in range(1, n*n + 1):
                square[y][x] = num
                nx, ny = (x + 1) % n, (y - 1) % n
                if square[ny][nx] != 0:
                    y = (y + 1) % n
                else:
                    x, y = nx, ny
            return square
        raise ValueError("目前支援 3\~9 階，偶數階僅支援 4×4")

    # ====================== 行星時辰計算器 ======================
    def planetary_hours(self, date: datetime, latitude: float = 25.0) -> Dict:
        """簡單行星時辰（日出到日落12小時，夜間12小時）"""
        # 假設日出 06:00，日落 18:00（實際專案可接 sunrise-sunset API）
        sunrise = datetime.combine(date.date(), datetime.min.time()) + timedelta(hours=6)
        sunset = sunrise + timedelta(hours=12)
        
        day_length = 12
        night_length = 12
        planets = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
        
        hours = {}
        current = sunrise
        for i in range(24):
            if current < sunset:
                planet = planets[i % 7]
                period = "day"
            else:
                planet = planets[(i + 6) % 7]  # 夜間從木星開始
                period = "night"
            hours[f"Hour {i+1}"] = {"planet": planet, "time": current.strftime("%H:%M"), "period": period}
            current += timedelta(hours=1)
        return hours

    # ====================== SVG 護符生成（可直接列印） ======================
    def generate_talisman_svg(self, square: List[List[int]], title: str = "Wafq", 
                              asma: str = "", filename: str = "talisman.svg"):
        """生成可列印的 SVG 護符圖"""
        dwg = svgwrite.Drawing(filename, size=("400px", "450px"))
        
        # 邊框
        dwg.add(dwg.rect((10, 10), (380, 430), stroke="gold", stroke_width=8, fill="none"))
        
        # 方陣
        n = len(square)
        cell_size = 280 // n
        for y in range(n):
            for x in range(n):
                dwg.add(dwg.rect(
                    (40 + x*cell_size, 60 + y*cell_size),
                    (cell_size, cell_size),
                    stroke="black", stroke_width=2, fill="#f8f1d3"
                ))
                dwg.add(dwg.text(
                    str(square[y][x]), 
                    insert=(40 + x*cell_size + cell_size/2, 60 + y*cell_size + cell_size/2 + 8),
                    text_anchor="middle", font_size="18px", font_family="serif", fill="black"
                ))
        
        # 標題與神名
        dwg.add(dwg.text(title, insert=(200, 35), text_anchor="middle", font_size="22px", font_family="serif"))
        if asma:
            dwg.add(dwg.text(asma, insert=(200, 410), text_anchor="middle", font_size="18px", font_family="serif"))
        
        dwg.save()
        print(f"✅ SVG 護符已生成：{filename}（可直接列印或刻印）")

    # ====================== 完整製作流程 ======================
    def create_talisman(self, n: int, asma_name: str = "", output_svg: bool = True):
        """一鍵製作護符（書中完整流程）"""
        square = self.generate_magic_square(n)
        info = self.get_asma_info(asma_name) or {}
        
        title = f"{asma_name or 'Wafq'} {n}×{n}"
        print(f"\n=== 製作 {title} 護符 ===")
        print(f"神名：{asma_name} ({info.get('roman', '')})")
        print(f"用途：{info.get('use', '通用')}")
        print(f"建議時辰：{info.get('timing', '行星強勢時')}")
        
        # 顯示方陣
        for row in square:
            print(' '.join(f'{num:3}' for num in row))
        
        if output_svg:
            self.generate_talisman_svg(square, title=title, asma=asma_name)
        
        print("使用提醒：大淨、禮兩拜、誦寶座經100次、焚乳香、金星/木星時製作")


# ====================== 使用範例 ======================
if __name__ == "__main__":
    wafq = IslamicWafqGenerator()
    
    # 1. 書中最經典 4×4（字母「د」）
    wafq.create_talisman(4, asma_name="الودود")
    
    # 2. 3×3 通用護符
    wafq.create_talisman(3, asma_name="الله")
    
    # 3. 行星時辰查詢
    today = datetime.now()
    hours = wafq.planetary_hours(today)
    print("\n今日行星時辰範例（第1小時）：", hours["Hour 1"])
    
    # 4. Abjad 計算
    print("神名「ودود」abjad 值 =", wafq.get_abjad_value("ودود"))
