"""
已完全展開所有 12 星座資料
支援：廟、旺、三方主、界、面、陷、落、游蕩
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum

class Planet(str, Enum):
    SUN = "太陽"
    MOON = "月亮"
    MERCURY = "水星"
    VENUS = "金星"
    MARS = "火星"
    JUPITER = "木星"
    SATURN = "土星"

class DignityType(str, Enum):
    DOMICILE = "廟"           # +5
    EXALTATION = "旺"         # +4
    TRIPLICITY = "三方主"     # +3 (日圖) / +2 (夜圖)
    TERM = "界"               # +2
    FACE = "面"               # +1
    DETRIMENT = "陷"          # -5
    FALL = "落"               # -4
    PEREGRINE = "游蕩"        # 0

# 星座中英對照（方便 kinastro 現有系統轉換）
SIGN_NAMES = {
    "Aries": "白羊座", "Taurus": "金牛座", "Gemini": "雙子座",
    "Cancer": "巨蟹座", "Leo": "獅子座", "Virgo": "處女座",
    "Libra": "天秤座", "Scorpio": "天蠍座", "Sagittarius": "射手座",
    "Capricorn": "摩羯座", "Aquarius": "水瓶座", "Pisces": "雙魚座"
}

# ==================== 完整 PTOLEMY_DIGNITIES 字典 ====================
PTOLEMY_DIGNITIES: Dict[str, Dict] = {
    "Aries": {
        "ruler": Planet.MARS,
        "exaltation": (Planet.SUN, 19),
        "triplicity_day": Planet.SUN,
        "triplicity_night": Planet.JUPITER,
        "detriment": Planet.VENUS,
        "fall": Planet.SATURN,
    },
    "Taurus": {
        "ruler": Planet.VENUS,
        "exaltation": (Planet.MOON, 3),
        "triplicity_day": Planet.VENUS,
        "triplicity_night": Planet.MOON,
        "detriment": Planet.MARS,
        "fall": None,
    },
    "Gemini": {
        "ruler": Planet.MERCURY,
        "exaltation": None,
        "triplicity_day": Planet.SATURN,
        "triplicity_night": Planet.MERCURY,
        "detriment": Planet.JUPITER,
        "fall": None,
    },
    "Cancer": {
        "ruler": Planet.MOON,
        "exaltation": (Planet.JUPITER, 15),
        "triplicity_day": Planet.VENUS,
        "triplicity_night": Planet.MARS,
        "detriment": Planet.SATURN,
        "fall": Planet.MARS,
    },
    "Leo": {
        "ruler": Planet.SUN,
        "exaltation": None,
        "triplicity_day": Planet.SUN,
        "triplicity_night": Planet.JUPITER,
        "detriment": Planet.SATURN,
        "fall": None,
    },
    "Virgo": {
        "ruler": Planet.MERCURY,
        "exaltation": (Planet.MERCURY, 15),
        "triplicity_day": Planet.VENUS,
        "triplicity_night": Planet.MOON,
        "detriment": Planet.JUPITER,
        "fall": Planet.VENUS,
    },
    "Libra": {
        "ruler": Planet.VENUS,
        "exaltation": (Planet.SATURN, 21),
        "triplicity_day": Planet.SATURN,
        "triplicity_night": Planet.MERCURY,
        "detriment": Planet.MARS,
        "fall": Planet.SUN,
    },
    "Scorpio": {
        "ruler": Planet.MARS,
        "exaltation": None,
        "triplicity_day": Planet.VENUS,
        "triplicity_night": Planet.MARS,
        "detriment": Planet.VENUS,
        "fall": Planet.MOON,
    },
    "Sagittarius": {
        "ruler": Planet.JUPITER,
        "exaltation": None,
        "triplicity_day": Planet.SUN,
        "triplicity_night": Planet.JUPITER,
        "detriment": Planet.MERCURY,
        "fall": None,
    },
    "Capricorn": {
        "ruler": Planet.SATURN,
        "exaltation": (Planet.MARS, 28),
        "triplicity_day": Planet.VENUS,
        "triplicity_night": Planet.MOON,
        "detriment": Planet.MOON,
        "fall": Planet.JUPITER,
    },
    "Aquarius": {
        "ruler": Planet.SATURN,
        "exaltation": None,
        "triplicity_day": Planet.SATURN,
        "triplicity_night": Planet.MERCURY,
        "detriment": Planet.SUN,
        "fall": None,
    },
    "Pisces": {
        "ruler": Planet.JUPITER,
        "exaltation": (Planet.VENUS, 27),
        "triplicity_day": Planet.VENUS,
        "triplicity_night": Planet.MARS,
        "detriment": Planet.MERCURY,
        "fall": Planet.MERCURY,
    },
}

# ==================== Ptolemaic Terms (托勒密界) ====================
PTOLEMAIC_TERMS: Dict[str, List[Tuple[int, int, Planet]]] = {
    "Aries": [(0, 6, Planet.JUPITER), (6, 14, Planet.VENUS), (14, 21, Planet.MERCURY),
              (21, 26, Planet.MARS), (26, 30, Planet.SATURN)],
    "Taurus": [(0, 8, Planet.VENUS), (8, 15, Planet.MERCURY), (15, 22, Planet.JUPITER),
               (22, 26, Planet.SATURN), (26, 30, Planet.MARS)],
    "Gemini": [(0, 7, Planet.MERCURY), (7, 14, Planet.JUPITER), (14, 21, Planet.VENUS),
               (21, 25, Planet.SATURN), (25, 30, Planet.MARS)],
    "Cancer": [(0, 6, Planet.MARS), (6, 13, Planet.JUPITER), (13, 20, Planet.MERCURY),
               (20, 27, Planet.VENUS), (27, 30, Planet.SATURN)],
    "Leo": [(0, 6, Planet.SATURN), (6, 13, Planet.MERCURY), (13, 19, Planet.VENUS),
            (19, 25, Planet.JUPITER), (25, 30, Planet.MARS)],
    "Virgo": [(0, 7, Planet.MERCURY), (7, 13, Planet.VENUS), (13, 18, Planet.JUPITER),
              (18, 24, Planet.SATURN), (24, 30, Planet.MARS)],
    "Libra": [(0, 6, Planet.SATURN), (6, 11, Planet.VENUS), (11, 19, Planet.JUPITER),
              (19, 24, Planet.MERCURY), (24, 30, Planet.MARS)],
    "Scorpio": [(0, 6, Planet.MARS), (6, 14, Planet.JUPITER), (14, 21, Planet.VENUS),
                (21, 27, Planet.MERCURY), (27, 30, Planet.SATURN)],
    "Sagittarius": [(0, 8, Planet.JUPITER), (8, 14, Planet.VENUS), (14, 19, Planet.MERCURY),
                    (19, 25, Planet.SATURN), (25, 30, Planet.MARS)],
    "Capricorn": [(0, 6, Planet.VENUS), (6, 12, Planet.MERCURY), (12, 19, Planet.JUPITER),
                  (19, 25, Planet.MARS), (25, 30, Planet.SATURN)],
    "Aquarius": [(0, 6, Planet.SATURN), (6, 12, Planet.MERCURY), (12, 20, Planet.VENUS),
                 (20, 25, Planet.JUPITER), (25, 30, Planet.MARS)],
    "Pisces": [(0, 8, Planet.VENUS), (8, 14, Planet.JUPITER), (14, 20, Planet.MERCURY),
               (20, 26, Planet.MARS), (26, 30, Planet.SATURN)],
}

# Face (每 10° 一面)
FACES: Dict[str, List[Tuple[int, int, Planet]]] = {
    sign: [(0, 10, Planet.MARS), (10, 20, Planet.SUN), (20, 30, Planet.VENUS)] if i % 3 == 0 else
          [(0, 10, Planet.MERCURY), (10, 20, Planet.MOON), (20, 30, Planet.SATURN)] if i % 3 == 1 else
          [(0, 10, Planet.JUPITER), (10, 20, Planet.MARS), (20, 30, Planet.SUN)]
    for i, sign in enumerate(PTOLEMY_DIGNITIES.keys())
}

class PtolemyDignityCalculator:
    def __init__(self, use_ptolemaic_terms: bool = True):
        self.use_ptolemaic_terms = use_ptolemaic_terms

    def get_dignities(self, planet: Planet, sign: str, degree: float, is_day_chart: bool = True) -> List[Tuple[DignityType, int]]:
        dignities: List[Tuple[DignityType, int]] = []
        data = PTOLEMY_DIGNITIES.get(sign, {})

        if data.get("ruler") == planet:
            dignities.append((DignityType.DOMICILE, 5))
        if data.get("exaltation") and data["exaltation"][0] == planet:
            dignities.append((DignityType.EXALTATION, 4))

        tri_key = "triplicity_day" if is_day_chart else "triplicity_night"
        if data.get(tri_key) == planet:
            score = 3 if is_day_chart else 2
            dignities.append((DignityType.TRIPLICITY, score))

        term_ruler = self._get_term_ruler(sign, degree)
        if term_ruler == planet:
            dignities.append((DignityType.TERM, 2))

        face_ruler = self._get_face_ruler(sign, degree)
        if face_ruler == planet:
            dignities.append((DignityType.FACE, 1))

        if data.get("detriment") == planet:
            dignities.append((DignityType.DETRIMENT, -5))
        if data.get("fall") == planet:
            dignities.append((DignityType.FALL, -4))

        if not dignities:
            dignities.append((DignityType.PEREGRINE, 0))

        return dignities

    def calculate_total_score(self, dignities_list: List[Tuple[DignityType, int]]) -> int:
        return sum(score for _, score in dignities_list)

    def _get_term_ruler(self, sign: str, degree: float) -> Optional[Planet]:
        for start, end, ruler in PTOLEMAIC_TERMS.get(sign, []):
            if start <= degree < end:
                return ruler
        return None

    def _get_face_ruler(self, sign: str, degree: float) -> Optional[Planet]:
        faces = FACES.get(sign, [])
        face_index = int(degree // 10)
        if face_index < len(faces):
            return faces[face_index][2]
        return None


# ==================== 中文顯示輔助 ====================
def dignity_to_chinese(dignities_list: List[Tuple[DignityType, int]]) -> str:
    return "、".join(f"{typ.value}({score})" for typ, score in dignities_list)


# ==================== 測試 ====================
if __name__ == "__main__":
    calc = PtolemyDignityCalculator()
    dignities = calc.get_dignities(Planet.SUN, "Aries", 19.0, is_day_chart=True)
    score = calc.calculate_total_score(dignities)
    print(f"太陽在白羊座19°（日圖）：{dignity_to_chinese(dignities)} → 總分 {score}")
