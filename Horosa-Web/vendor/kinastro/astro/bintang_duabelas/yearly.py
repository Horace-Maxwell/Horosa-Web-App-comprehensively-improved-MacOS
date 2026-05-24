"""
astro/bintang_duabelas/yearly.py
================================

Bintang Duabelas 年運模組。
"""

from __future__ import annotations


class YearlyFortune:
    """年運資料查詢。"""

    DAY_PLANET_INFO: dict[str, dict[str, str]] = {
        "ahad": {"planet_ar": "الشمس", "planet_en": "Sun", "planet_zh": "太陽", "nature": "Hot and Dry (熱燥)", "metal": "Gold (金)", "angel_above": "Ruqa'il (روقائيل)", "angel_below": "Maimun (ميمون)"},
        "isnin": {"planet_ar": "القمر", "planet_en": "Moon", "planet_zh": "月亮", "nature": "Cold and Moist (冷濕)", "metal": "Silver (銀)", "angel_above": "Jibra'il (جبرائيل)", "angel_below": "Murrah (مرة)"},
        "selasa": {"planet_ar": "المريخ", "planet_en": "Mars", "planet_zh": "火星", "nature": "Hot and Dry (熱燥)", "metal": "Copper (銅)", "angel_above": "Sama'il (سمائيل)", "angel_below": "Al-Ahmar (الأحمر)"},
        "rabu": {"planet_ar": "عطارد", "planet_en": "Mercury", "planet_zh": "水星", "nature": "Cold and Moist, mixed with Hot (冷濕兼熱)", "metal": "Mercury/Quicksilver (水銀)", "angel_above": "Mika'il (ميكائيل)", "angel_below": "Barqan (برقان)"},
        "khamis": {"planet_ar": "المشتري", "planet_en": "Jupiter", "planet_zh": "木星", "nature": "Hot and Moist (熱濕)", "metal": "Tin (錫)", "angel_above": "Sarfya'il (صرفيائيل)", "angel_below": "Shamhurash (شمهورش)"},
        "jumaat": {"planet_ar": "الزهرة", "planet_en": "Venus", "planet_zh": "金星", "nature": "Cold and Dry (冷燥)", "metal": "Iron (鐵)", "angel_above": "Anya'il (عنيائيل)", "angel_below": "Rub'ah (ربعة)"},
        "sabtu": {"planet_ar": "زحل", "planet_en": "Saturn", "planet_zh": "土星", "nature": "Cold and Moist (冷濕)", "metal": "Lead (鉛)", "angel_above": "Kasfya'il (كسفيائيل)", "angel_below": "Al-Mudhahab (المذهب)"},
    }

    YEARLY_FORTUNES: dict[str, dict[str, str | list[str]]] = {
        "ahad": {"ruler": "Sun (太陽 / الشمس)", "summary_en": "A year of hardship for rulers. Earthquakes and floods occur. Spring brings good harvests, but summer drought follows. Autumn has good rainfall, but winter frost damages crops. Plague and war may affect the people.", "summary_zh": "此年國王（君主）將經歷艱難。有地震與洪水。春季穀物生長繁茂，但夏季遭遇乾旱。秋季雨量豐沛，冬季嚴重霜凍導致農作物受損。亦將爆發瘟疫與戰爭。", "agriculture": "Spring good, summer drought, autumn rain, winter frost", "calamities": ["Earthquake", "Flood", "Plague", "War"]},
        "isnin": {"ruler": "Moon (月亮 / القمر)", "summary_en": "A year of grace and peace. Abundant rainfall brings good harvests. The climate is mild in spring, with brief summer drought. Autumn is favorable with good grain. Minor illness at year end.", "summary_zh": "此年將獲得恩典與和平。雨水充沛，農作物豐收。春季氣候溫和，夏季短暫乾旱。秋季風調雨順，五穀豐登。冬季有小規模疾病。", "agriculture": "Good rainfall, good harvests throughout", "calamities": ["Minor illness at year end"]},
        "selasa": {"ruler": "Mars (火星 / المريخ)", "summary_en": "A year of war and conflict. Internal strife and rebellion. Earthquakes and volcanic eruptions with storms. Spring is unusually hot, summer brings severe drought and famine. Autumn cold, poor harvest. Winter plague causes many deaths.", "summary_zh": "此年面臨戰爭與衝突，可能引發內亂與叛變。有地震與火山爆發，伴隨暴風雨。春季異常炎熱，夏季嚴重乾旱與飢荒。秋季寒冷，收成不佳。冬季瘟疫造成大量死亡。", "agriculture": "Hot spring, drought, cold autumn, poor harvest", "calamities": ["War", "Earthquake", "Volcanic eruption", "Famine", "Plague"]},
        "rabu": {"ruler": "Mercury (水星 / عطارد)", "summary_en": "A year of legal disputes and political struggles. Corruption among officials. Earthquakes and floods occur. Spring is too hot, summer drought and famine. Autumn cold, poor harvest. Winter brings disease and death.", "summary_zh": "此年面臨法律糾紛與政治鬥爭，官員貪腐。有地震與洪水。春季異常炎熱，夏季乾旱飢荒。秋季寒冷收成不佳，冬季疾病死亡。", "agriculture": "Moderate Nile, unusual crops, mixed fortune", "calamities": ["Legal disputes", "Corruption", "Earthquake", "Flood"]},
        "khamis": {"ruler": "Jupiter (木星 / المشتري)", "summary_en": "A year of justice and prosperity. Kings rule fairly. Abundant harvest and moderate grain prices. Some storms but justice prevails. Plants are fertile, grains plentiful. Minor cold at year end, strong westerly winds.", "summary_zh": "此年公正繁榮。國王公正治國。豐收且糧價適中。有風暴但正義獲勝。植物繁茂，糧食充足。年末略有寒冷，西風強勁。", "agriculture": "Fertile plants, plentiful grain, moderate prices", "calamities": ["Storms", "Minor cold"]},
        "jumaat": {"ruler": "Venus (金星 / الزهرة)", "summary_en": "A year of contentment and joy. People are happy and prosperous. Kings are strong, the Nile is moderate. Entertainment and merrymaking abound. Food is cheap. Late year may see some conflict due to Venus-Saturn opposition.", "summary_zh": "此年滿足喜悅。人民幸福繁榮。國王強大，河水適中。娛樂豐富。食物便宜。年末因金星土星對沖可能有衝突。", "agriculture": "Good food production, cheap prices", "calamities": ["Late-year conflict from Venus-Saturn opposition"]},
        "sabtu": {"ruler": "Saturn (土星 / زحل)", "summary_en": "A year of hardship for the Roman lands. Plague and misfortune abound. The righteous and the young suffer. Kings of Persia die. Pregnant women face danger. Beginning is difficult, end improves. Westerly winds blow.", "summary_zh": "此年羅馬之地艱難。瘟疫與不幸頻發。義人與年輕人受苦。波斯國王去世。孕婦面臨危險。開始困難，結尾好轉。西風吹拂。", "agriculture": "Difficult growing conditions", "calamities": ["Plague", "Misfortune", "Danger for pregnant women"]},
    }

    def get_yearly_fortune(self, day_name: str) -> dict[str, str | list[str]]:
        """依歲首星期取得年運資料。"""
        day_key = day_name.lower()
        return {
            "day": day_name,
            **self.DAY_PLANET_INFO.get(day_key, self.DAY_PLANET_INFO["ahad"]),
            **self.YEARLY_FORTUNES.get(day_key, self.YEARLY_FORTUNES["ahad"]),
        }

    def get_day_info(self, day_name: str) -> dict[str, str]:
        """回傳某天對應的主宰行星資訊。"""
        return self.DAY_PLANET_INFO.get(day_name.lower(), self.DAY_PLANET_INFO["ahad"])

    def list_all_days(self) -> list[dict[str, str]]:
        """列出七日主宰資訊。"""
        return [{"day": day, **info} for day, info in self.DAY_PLANET_INFO.items()]


__all__ = ["YearlyFortune"]
