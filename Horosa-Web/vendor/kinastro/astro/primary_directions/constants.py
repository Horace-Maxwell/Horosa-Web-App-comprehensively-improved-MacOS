"""
astro/primary_directions/constants.py — Constants for Classical Primary Directions

Based on:
  - Claudius Ptolemy, "Tetrabiblos" (c. 150 CE), Book III
  - Johannes Müller (Regiomontanus), "Tabulae Directionum" (1490)
  - Simon Placidus, "Primum Mobile" (1657)
  - Martin Gansten, "Primary Directions: Astrology's Old Master Technique" (2009)
  - Robert Hand, "Whole Sign Houses: The Oldest House System" and numerous technique papers
"""

from __future__ import annotations

from typing import Dict, List, Tuple

# ── Swiss Ephemeris planet IDs ─────────────────────────────────────────────
PLANET_SWE_IDS: Dict[str, int] = {
    "SU": 0,   # Sun
    "MO": 1,   # Moon
    "ME": 2,   # Mercury
    "VE": 3,   # Venus
    "MA": 4,   # Mars
    "JU": 5,   # Jupiter
    "SA": 6,   # Saturn
    "UR": 7,   # Uranus
    "NE": 8,   # Neptune
    "PL": 9,   # Pluto
    # AS and MC handled via swe.houses()
}

PLANET_NAMES_EN: Dict[str, str] = {
    "SU": "Sun",
    "MO": "Moon",
    "ME": "Mercury",
    "VE": "Venus",
    "MA": "Mars",
    "JU": "Jupiter",
    "SA": "Saturn",
    "UR": "Uranus",
    "NE": "Neptune",
    "PL": "Pluto",
    "AS": "Ascendant",
    "MC": "Midheaven",
    "NN": "North Node",
    "DS": "Descendant",
    "IC": "IC (Nadir)",
}

PLANET_NAMES_ZH: Dict[str, str] = {
    "SU": "太陽",
    "MO": "月亮",
    "ME": "水星",
    "VE": "金星",
    "MA": "火星",
    "JU": "木星",
    "SA": "土星",
    "UR": "天王星",
    "NE": "海王星",
    "PL": "冥王星",
    "AS": "上升點",
    "MC": "中天",
    "NN": "北交點",
    "DS": "下降點",
    "IC": "天底",
}

PLANET_SYMBOLS: Dict[str, str] = {
    "SU": "☉",
    "MO": "☽",
    "ME": "☿",
    "VE": "♀",
    "MA": "♂",
    "JU": "♃",
    "SA": "♄",
    "UR": "♅",
    "NE": "♆",
    "PL": "♇",
    "AS": "ASC",
    "MC": "MC",
    "NN": "☊",
    "DS": "DSC",
    "IC": "IC",
}

PLANET_COLORS: Dict[str, str] = {
    "SU": "#e8b84b",
    "MO": "#c8d8e8",
    "ME": "#88c8a8",
    "VE": "#e898b8",
    "MA": "#d85840",
    "JU": "#8890d8",
    "SA": "#908870",
    "UR": "#58b8c8",
    "NE": "#6878d8",
    "PL": "#885880",
    "AS": "#e8d8b0",
    "MC": "#d8c890",
    "NN": "#98d8a8",
    "DS": "#c8c8c8",
    "IC": "#a8a8a8",
}

PLANET_ORDER: List[str] = [
    "SU", "MO", "ME", "VE", "MA", "JU", "SA", "UR", "NE", "PL",
    "AS", "MC", "NN", "DS", "IC",
]

# Standard planet set for directing (classical 7 + angles + outer)
CLASSIC_PLANETS: List[str] = ["SU", "MO", "ME", "VE", "MA", "JU", "SA"]
ANGLE_POINTS: List[str] = ["AS", "MC", "DS", "IC"]
MODERN_PLANETS: List[str] = ["UR", "NE", "PL"]

# ── Zodiac ─────────────────────────────────────────────────────────────────
ZODIAC_SIGNS: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_ZH: List[str] = [
    "白羊", "金牛", "雙子", "巨蟹",
    "獅子", "處女", "天秤", "天蠍",
    "射手", "摩羯", "水瓶", "雙魚",
]

SIGN_SYMBOLS: List[str] = [
    "♈", "♉", "♊", "♋",
    "♌", "♍", "♎", "♏",
    "♐", "♑", "♒", "♓",
]

# ── Aspects ────────────────────────────────────────────────────────────────
# Classical major aspects (Ptolemy: Tetrabiblos I.13)
ASPECTS: List[Dict] = [
    {"name": "Conjunction",  "name_zh": "合相",   "angle": 0.0,   "symbol": "☌",  "orb": 1.5, "key": "CNJ"},
    {"name": "Sextile",      "name_zh": "六分相",  "angle": 60.0,  "symbol": "⚹",  "orb": 1.5, "key": "SXT"},
    {"name": "Square",       "name_zh": "四分相",  "angle": 90.0,  "symbol": "□",  "orb": 1.5, "key": "SQR"},
    {"name": "Trine",        "name_zh": "三分相",  "angle": 120.0, "symbol": "△",  "orb": 1.5, "key": "TRI"},
    {"name": "Opposition",   "name_zh": "對分相",  "angle": 180.0, "symbol": "☍",  "orb": 1.5, "key": "OPP"},
    # Ptolemy also acknowledges parallel of declination
    {"name": "Parallel",     "name_zh": "平行",   "angle": 0.0,   "symbol": "//", "orb": 1.0, "key": "PAR"},
    {"name": "Contraparallel","name_zh": "反平行", "angle": 180.0, "symbol": ")(", "orb": 1.0, "key": "CPAR"},
]

ASPECT_BY_KEY: Dict[str, Dict] = {a["key"]: a for a in ASPECTS}
ASPECT_KEYS: List[str] = [a["key"] for a in ASPECTS[:5]]  # main 5

# ── Time Conversion Keys ────────────────────────────────────────────────────
# Naibod Key (classical): mean daily motion of Sun = 59'8" = 0.98563° per year
# [Placidus, Primum Mobile, 1657; later confirmed by Naibod in "Enarratio Elementorum Astrologiae", 1560]
NAIBOD_KEY: float = 0.98563  # degrees per year

# Ptolemy Key: 1° of direction arc = 1 year (simplified)
PTOLEMY_KEY: float = 1.0  # degrees per year

# Solar Arc Key: use actual Sun's daily motion for the birth year
# Computed dynamically; nominal value:
SOLAR_ARC_NOMINAL: float = 0.9856  # degrees/year (approximately same as Naibod)

# ── Interpretation Data ────────────────────────────────────────────────────
# Significator meanings (classical, Ptolemy-based)
SIGNIFICATOR_MEANINGS: Dict[str, Dict] = {
    "AS": {
        "zh": "上升點（命宮主）：代表生命力、健康、個人形象、起點與新開始。",
        "en": "Ascendant (Lord of the 1st): Represents vitality, health, personal identity, beginnings.",
    },
    "MC": {
        "zh": "中天（事業天頂）：代表名聲、事業成就、社會地位、人生高峰。",
        "en": "Midheaven (MC): Represents career, reputation, social status, public achievement.",
    },
    "SU": {
        "zh": "太陽：代表生命力、父親、權威、榮耀、身份認同與創造力。",
        "en": "Sun: Represents life force, father, authority, honor, identity and creative power.",
    },
    "MO": {
        "zh": "月亮：代表情緒、母親、家庭、民眾、日常生活的節奏與變化。",
        "en": "Moon: Represents emotions, mother, family, the public, daily rhythms and changes.",
    },
    "ME": {
        "zh": "水星：代表思維、溝通、旅行、貿易、書寫與學習能力。",
        "en": "Mercury: Represents mind, communication, travel, trade, writing and learning.",
    },
    "VE": {
        "zh": "金星：代表愛情、美麗、藝術、財富、關係的和諧與享樂。",
        "en": "Venus: Represents love, beauty, art, wealth, harmonious relationships and pleasure.",
    },
    "MA": {
        "zh": "火星：代表行動力、競爭、衝突、勇氣、慾望與外科手術。",
        "en": "Mars: Represents action, competition, conflict, courage, desire and surgery.",
    },
    "JU": {
        "zh": "木星：代表擴張、智慧、宗教信仰、法律、社會地位提升與幸運。",
        "en": "Jupiter: Represents expansion, wisdom, religion, law, elevation and fortune.",
    },
    "SA": {
        "zh": "土星：代表限制、責任、老年、考驗、慢性疾病與時間的鐵律。",
        "en": "Saturn: Represents limitation, duty, old age, trials, chronic illness and time's law.",
    },
    "UR": {
        "zh": "天王星：代表突變、革命、科技、解放、意外與天才。",
        "en": "Uranus: Represents sudden change, revolution, technology, liberation and genius.",
    },
    "NE": {
        "zh": "海王星：代表夢幻、靈性、幻覺、犧牲、藝術創作與模糊邊界。",
        "en": "Neptune: Represents dreams, spirituality, illusion, sacrifice, artistic creation.",
    },
    "PL": {
        "zh": "冥王星：代表蛻變、毀滅與重生、深層心理、龐大力量與業力清算。",
        "en": "Pluto: Represents transformation, destruction/rebirth, depth psychology and karmic reckoning.",
    },
    "NN": {
        "zh": "北交點：代表業力方向、命運課題、靈魂進化的前進方向。",
        "en": "North Node: Represents karmic direction, soul's evolutionary path and destined lessons.",
    },
    "DS": {
        "zh": "下降點：代表伴侶、婚姻、公開的敵對關係與重要他人。",
        "en": "Descendant: Represents partnerships, marriage, open enemies and significant others.",
    },
    "IC": {
        "zh": "天底：代表家庭、根源、晚年、隱藏的基礎與祖先業力。",
        "en": "IC (Nadir): Represents home, roots, old age, hidden foundations and ancestral karma.",
    },
}

# Aspect nature in directions (classical delineation style)
ASPECT_DIRECTION_MEANINGS: Dict[str, Dict] = {
    "CNJ": {
        "zh": "合相：兩點能量的完全融合，效果最強烈，具體事件最易顯化。",
        "en": "Conjunction: Complete fusion of energies, strongest effect, most likely to manifest concretely.",
    },
    "OPP": {
        "zh": "對分相：對立張力，呈現公開衝突、重要對決或人際關係的危機轉捩點。",
        "en": "Opposition: Polarizing tension, public conflict, major confrontations or relationship turning points.",
    },
    "SQR": {
        "zh": "四分相：壓力挑戰，需要採取行動，是迫使人改變的摩擦力量。",
        "en": "Square: Pressure and challenge, demanding action, friction that forces change.",
    },
    "TRI": {
        "zh": "三分相：和諧流暢，才能與機緣自然湧現，屬於吉利與順遂的時期。",
        "en": "Trine: Harmonious flow, natural emergence of talents and opportunities, fortunate period.",
    },
    "SXT": {
        "zh": "六分相：機會之相，提供有利的可能性，需主動把握方能顯化。",
        "en": "Sextile: Aspect of opportunity, offering favorable possibilities requiring active engagement.",
    },
    "PAR": {
        "zh": "平行：類似合相的加強效應，行星赤緯相同，增強兩行星的相互影響。",
        "en": "Parallel: Strengthening effect similar to conjunction, same declination, enhances interaction.",
    },
    "CPAR": {
        "zh": "反平行：類似對分相的效應，行星赤緯相反，製造緊張的對立能量。",
        "en": "Contraparallel: Effect similar to opposition, opposite declinations, creating tense polarity.",
    },
}

# Nature of event based on promittor-significator combination (classical tradition)
EVENT_NATURE: Dict[Tuple[str, str], Dict] = {
    # Sun as promittor
    ("SU", "AS"): {"zh": "生命力轉變、健康關鍵時刻、自我形象的重塑", "en": "Vital turning point, health crisis or renewal, identity transformation"},
    ("SU", "MC"): {"zh": "事業高峰與榮耀時刻、獲得公眾認可與名聲", "en": "Career pinnacle, public recognition, honor and fame"},
    ("SU", "MO"): {"zh": "情緒健康與身體平衡的關鍵時刻、公私生活的協調", "en": "Emotional-physical balance, integration of public and private life"},
    # Moon as promittor
    ("MO", "AS"): {"zh": "情緒波動、民眾相關事務、女性關係的重要轉變", "en": "Emotional upheaval, public affairs, significant feminine relationships"},
    ("MO", "MC"): {"zh": "公眾形象轉變、女性貴人相助或女性相關事業", "en": "Public image shift, feminine benefactors, career related to public/women"},
    # Venus as promittor
    ("VE", "AS"): {"zh": "愛情機緣、美麗轉變、藝術才華的展現與財富增進", "en": "Love opportunity, aesthetic transformation, artistic talent manifests, financial gain"},
    ("VE", "MC"): {"zh": "事業上的藝術成就、因美麗才華獲得聲望、愛情影響事業", "en": "Artistic career achievement, fame through beauty/talent, love affecting career"},
    # Mars as promittor
    ("MA", "AS"): {"zh": "衝突或手術、意外傷害、勇氣激發的行動與競爭", "en": "Conflict or surgery, accidents, courageous action, competition"},
    ("MA", "MC"): {"zh": "事業上的鬥爭與競爭、軍事或運動方面的成就或危機", "en": "Career struggle and competition, military/athletic achievement or crisis"},
    # Jupiter as promittor
    ("JU", "AS"): {"zh": "幸運轉機、健康改善、社會地位提升與精神擴展", "en": "Fortunate turning point, health improvement, social elevation, spiritual expansion"},
    ("JU", "MC"): {"zh": "事業高峰、法律或宗教上的成就、社會地位的顯著提升", "en": "Career peak, legal/religious achievement, significant social advancement"},
    # Saturn as promittor
    ("SA", "AS"): {"zh": "健康挑戰、孤獨考驗、責任加重、慢性問題浮現", "en": "Health challenge, isolation, increased responsibilities, chronic issues emerge"},
    ("SA", "MC"): {"zh": "事業困境、社會地位受損、挫折後的重建與成熟", "en": "Career setbacks, social status damage, rebuilding after failure, maturation"},
    # Angles as promittors
    ("AS", "SU"): {"zh": "生命方向的重新定位、個人身份的顯著轉變", "en": "Reorientation of life direction, significant personal identity shift"},
    ("MC", "SU"): {"zh": "事業目標的重新定義、公眾身份的轉型", "en": "Career goal redefinition, public identity transformation"},
}


def get_event_nature(promittor: str, significator: str) -> Dict:
    """Return event nature for a significator-promittor combination."""
    key = (promittor, significator)
    if key in EVENT_NATURE:
        return EVENT_NATURE[key]
    # Generic based on promittor's nature
    return SIGNIFICATOR_MEANINGS.get(promittor, {
        "zh": f"{PLANET_NAMES_ZH.get(promittor, promittor)}主限推運：重要人生轉折",
        "en": f"{PLANET_NAMES_EN.get(promittor, promittor)} Primary Direction: significant life turning point",
    })


# ── Example Charts (for testing and demonstration) ────────────────────────
# Famous charts with well-documented life events for validation
EXAMPLE_CHARTS = [
    {
        "name": "Adolf Hitler",
        "name_zh": "阿道夫·希特勒（驗證用）",
        "year": 1889, "month": 4, "day": 20,
        "hour": 18, "minute": 30,
        "timezone": 1.0,
        "latitude": 48.2567, "longitude": 13.0333,
        "location_name": "Braunau am Inn, Austria",
        "note_zh": "主要用於方法論驗證，不代表任何價值立場",
        "note_en": "Used for methodological validation only",
    },
    {
        "name": "Princess Diana",
        "name_zh": "黛安娜王妃",
        "year": 1961, "month": 7, "day": 1,
        "hour": 19, "minute": 45,
        "timezone": 1.0,
        "latitude": 52.6333, "longitude": 0.5167,
        "location_name": "Sandringham, England",
        "note_zh": "有詳細生平記錄，1981年婚姻與1997年車禍",
        "note_en": "Well-documented life: 1981 marriage, 1997 accident",
    },
    {
        "name": "Carl Gustav Jung",
        "name_zh": "卡爾·榮格",
        "year": 1875, "month": 7, "day": 26,
        "hour": 19, "minute": 29,
        "timezone": 0.5,
        "latitude": 47.6167, "longitude": 8.5167,
        "location_name": "Kesswil, Switzerland",
        "note_zh": "心理學家，深度心理學創始人，有豐富傳記記錄",
        "note_en": "Psychologist, founder of analytical psychology, richly documented life",
    },
]
