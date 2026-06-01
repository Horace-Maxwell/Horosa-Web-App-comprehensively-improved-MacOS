from typing import List, Dict, Optional


# ====================== 七大行星詳細特性 (Laṭāʼif al-Ishāra) ======================
class PlanetaryProperties:
    """《Shams al-Maʻārif al-Kubrā》附錄《لطائف الإشارة في خصائص الكواكب السيارة》完整七大行星特性表"""

    PLANETS: List[Dict] = [
        {
            "planet": "Zuhal", "arabic": "زحل", "english": "Saturn",
            "temp": "Cold-Dry", "element": "Earth", "color": "Black",
            "omens": "紀律、耐心、長期事業、農業、建築、老人、疾病、限制、遺產",
            "talisman_use": "求穩定、長期目標、權威、保護房屋、化解慢性病",
            "timing": "土星強勢時（週六、土星時辰）",
            "letter": "ح", "wafq_size": 3,
            "note": "書中稱為最沉重、最冷乾之星，適合壓制敵人或求耐力"
        },
        {
            "planet": "Mushteri", "arabic": "المشتري", "english": "Jupiter",
            "temp": "Hot-Wet", "element": "Air", "color": "White/Yellow",
            "omens": "智慧、宗教、富足、幸運、旅行、哲學、擴展、子女",
            "talisman_use": "求財富、知識、幸運、婚姻、子嗣、地位提升",
            "timing": "木星強勢時（週四、木星時辰）",
            "letter": "ج", "wafq_size": 4,
            "note": "書中視為最吉祥、最有益之星，常與 al-Wahhab、al-Razzaq 配合"
        },
        {
            "planet": "Mirrikh", "arabic": "المريخ", "english": "Mars",
            "temp": "Hot-Dry", "element": "Fire", "color": "Red",
            "omens": "勇氣、戰爭、勝利、力量、敵人、血液、火災",
            "talisman_use": "戰勝敵人、提升勇氣、保護、征服、運動",
            "timing": "火星強勢時（週二、火星時辰）",
            "letter": "د", "wafq_size": 5,
            "note": "書中用於征服、壓制與戰鬥相關護符"
        },
        {
            "planet": "Shams", "arabic": "الشمس", "english": "Sun",
            "temp": "Hot-Dry", "element": "Fire", "color": "Gold/Yellow",
            "omens": "權力、尊榮、領導、藝術、心靈、父親、健康",
            "talisman_use": "求尊榮、地位、領導力、健康、藝術成功",
            "timing": "太陽時（日出、正午）",
            "letter": "ا", "wafq_size": 6,
            "note": "書中最尊貴之星，常與 al-Aziz、al-Malik 配合"
        },
        {
            "planet": "Zuhra", "arabic": "الزهرة", "english": "Venus",
            "temp": "Cold-Wet", "element": "Water/Air", "color": "Green/White",
            "omens": "愛情、婚姻、美麗、藝術、和諧、快樂、女性",
            "talisman_use": "求愛情、婚姻、和睦、藝術創作、吸引力",
            "timing": "金星強勢時（週五、金星時辰）",
            "letter": "ب", "wafq_size": 7,
            "note": "書中最常用於愛情與美麗護符"
        },
        {
            "planet": "Utarid", "arabic": "عطارد", "english": "Mercury",
            "temp": "Cold-Dry / Hot-Wet", "element": "Air", "color": "Mixed",
            "omens": "智慧、商業、溝通、學習、旅行、醫藥、詭計",
            "talisman_use": "求智慧、記憶、商業成功、口才、學習",
            "timing": "水星強勢時（週三、水星時辰）",
            "letter": "ز", "wafq_size": 8,
            "note": "書中視為最靈活、最適合知識與商業之星"
        },
        {
            "planet": "Qamar", "arabic": "القمر", "english": "Moon",
            "temp": "Cold-Wet", "element": "Water", "color": "Silver/White",
            "omens": "情感、家庭、旅行、安全、夢境、母親、變化",
            "talisman_use": "求家庭和睦、旅行平安、夢境指引、情感平穩",
            "timing": "月亮強勢時（週一、月亮時辰）",
            "letter": "ط", "wafq_size": 9,
            "note": "書中最接近地球之星，變化快速，常與 al-Muhaymin 配合"
        }
    ]

    def get_planet(self, name: str) -> Optional[Dict]:
        """依英文或阿拉伯文名稱取得行星特性"""
        name = name.lower()
        return next((p for p in self.PLANETS 
                    if p["english"].lower() == name or p["arabic"] == name), None)

    def list_all(self) -> List[Dict]:
        return self.PLANETS

    def print_all(self):
        """美觀列印全部七大行星特性"""
        print("\n=== 《Shams al-Maʻārif》七大行星詳細特性 ===")
        for p in self.PLANETS:
            print(f"{p['arabic']:6} ({p['english']})")
            print(f"   體質：{p['temp']:12}  元素：{p['element']:6}  顏色：{p['color']}")
            print(f"   徵兆：{p['omens']}")
            print(f"   護符用途：{p['talisman_use']}")
            print(f"   建議時辰：{p['timing']}")
            print(f"   對應字母：{p['letter']}   推薦方陣：{p['wafq_size']}×{p['wafq_size']}\n")
