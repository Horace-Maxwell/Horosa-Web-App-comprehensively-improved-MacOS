from typing import List, Dict, Optional


# ====================== 十二星座徵兆 (Zahr al-Murūj fī Dalā'il al-Burūj) ======================
class ZodiacSigns:
    """《Shams al-Maʻārif al-Kubrā》附錄《زهر المروج في دلائل البروج》完整十二星座徵兆表
    包含阿拉伯名、元素、統治行星、主要徵兆與護符用途（直接來自書中描述）"""

    SIGNS: List[Dict] = [
        {
            "no": 1, "arabic": "الحمل", "english": "Aries", "element": "Fire", "ruler": "Mars",
            "omens": "勇敢、開創、領導、戰勝敵人、適合開始新事業、旅行、求勝利",
            "talisman_use": "戰勝敵人、提升勇氣、開創新局",
            "timing": "火星強勢或白羊座上升時"
        },
        {
            "no": 2, "arabic": "الثور", "english": "Taurus", "element": "Earth", "ruler": "Venus",
            "omens": "穩定、財富、耐心、愛情、農業與物質享受",
            "talisman_use": "求財富、穩定關係、治病與長壽",
            "timing": "金星時或金牛座"
        },
        {
            "no": 3, "arabic": "الجوزاء", "english": "Gemini", "element": "Air", "ruler": "Mercury",
            "omens": "智慧、溝通、學習、商業、旅行、多變",
            "talisman_use": "增強記憶、學習、商業成功、口才",
            "timing": "水星時或雙子座"
        },
        {
            "no": 4, "arabic": "السرطان", "english": "Cancer", "element": "Water", "ruler": "Moon",
            "omens": "家庭、情感、保護、安全、繁殖與滋養",
            "talisman_use": "家庭和睦、保護房屋、求子嗣",
            "timing": "月亮強勢或巨蟹座"
        },
        {
            "no": 5, "arabic": "الأسد", "english": "Leo", "element": "Fire", "ruler": "Sun",
            "omens": "尊榮、領導、權力、藝術、慷慨",
            "talisman_use": "提升地位、求尊榮、藝術成功",
            "timing": "太陽時或獅子座"
        },
        {
            "no": 6, "arabic": "السنبلة", "english": "Virgo", "element": "Earth", "ruler": "Mercury",
            "omens": "精細、分析、醫療、純潔、工作",
            "talisman_use": "醫療、學習、精確工作、淨化",
            "timing": "水星時或處女座"
        },
        {
            "no": 7, "arabic": "الميزان", "english": "Libra", "element": "Air", "ruler": "Venus",
            "omens": "平衡、正義、愛情、婚姻、藝術",
            "talisman_use": "婚姻和諧、求公正、藝術創作",
            "timing": "金星時或天秤座"
        },
        {
            "no": 8, "arabic": "العقرب", "english": "Scorpio", "element": "Water", "ruler": "Mars",
            "omens": "神秘、轉化、權力、性、死亡與重生",
            "talisman_use": "擊敗敵人、轉化危機、保護",
            "timing": "火星時或天蠍座"
        },
        {
            "no": 9, "arabic": "القوس", "english": "Sagittarius", "element": "Fire", "ruler": "Jupiter",
            "omens": "哲學、旅行、宗教、幸運、擴展",
            "talisman_use": "遠行安全、求知識、幸運",
            "timing": "木星時或射手座"
        },
        {
            "no": 10, "arabic": "الجدي", "english": "Capricorn", "element": "Earth", "ruler": "Saturn",
            "omens": "紀律、野心、權力、耐心、事業",
            "talisman_use": "事業成功、長期目標、權威",
            "timing": "土星時或摩羯座"
        },
        {
            "no": 11, "arabic": "الدلو", "english": "Aquarius", "element": "Air", "ruler": "Saturn",
            "omens": "創新、自由、人道、知識、未來",
            "talisman_use": "創新發明、自由、社群",
            "timing": "土星時或水瓶座"
        },
        {
            "no": 12, "arabic": "الحوت", "english": "Pisces", "element": "Water", "ruler": "Jupiter",
            "omens": "靈性、直覺、慈悲、藝術、隱秘",
            "talisman_use": "靈性提升、慈悲、治癒、隱藏保護",
            "timing": "木星時或雙魚座"
        }
    ]

    def get_sign(self, number: int) -> Optional[Dict]:
        """依序號取得星座徵兆"""
        return next((s for s in self.SIGNS if s["no"] == number), None)

    def get_by_arabic(self, arabic: str) -> Optional[Dict]:
        """依阿拉伯文名稱取得"""
        return next((s for s in self.SIGNS if s["arabic"] == arabic), None)

    def get_by_english(self, english: str) -> Optional[Dict]:
        """依英文名稱取得"""
        return next((s for s in self.SIGNS if s["english"].lower() == english.lower()), None)

    def list_all(self) -> List[Dict]:
        return self.SIGNS

    def print_all(self):
        """美觀列印全部十二星座徵兆"""
        print("\n=== 《Shams al-Maʻārif》十二星座徵兆 ===")
        for s in self.SIGNS:
            print(f"{s['no']:2d}. {s['arabic']:8} ({s['english']})")
            print(f"   元素：{s['element']:6}  主宰：{s['ruler']:8}")
            print(f"   徵兆：{s['omens']}")
            print(f"   護符用途：{s['talisman_use']}")
            print(f"   建議時辰：{s['timing']}\n")
