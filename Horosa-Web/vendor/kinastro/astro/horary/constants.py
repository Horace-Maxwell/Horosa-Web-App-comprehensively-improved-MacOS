"""
astro/horary/constants.py — Traditional Horary Astrology Constants

Complete reference tables for both Western (Lilly/Bonatti) and Vedic (Prashna) horary.

Sources:
- William Lilly, "Christian Astrology" (1647) [CA]
- Guido Bonatti, "Liber Astronomiae" (~1277) [LA]
- Vettius Valens, "Anthology" [VV]
- Firmicus Maternus, "Mathesis" [FM]
-《Prasna Marga》 (Traditional Kerala Jyotish text on Horary) [PM]
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Optional

# ============================================================
# Seven Traditional Planets (Horary uses only these)
# 七傳統行星（卜卦占星只使用這七顆）
# ============================================================

TRADITIONAL_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

PLANET_GLYPHS: Dict[str, str] = {
    "Sun":     "☉",
    "Moon":    "☽",
    "Mercury": "☿",
    "Venus":   "♀",
    "Mars":    "♂",
    "Jupiter": "♃",
    "Saturn":  "♄",
}

PLANET_CN: Dict[str, str] = {
    "Sun":     "太陽",
    "Moon":    "月亮",
    "Mercury": "水星",
    "Venus":   "金星",
    "Mars":    "火星",
    "Jupiter": "木星",
    "Saturn":  "土星",
}

# Swiss Ephemeris planet IDs
import swisseph as swe
PLANET_IDS: Dict[str, int] = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
}

# ============================================================
# Zodiac Signs
# ============================================================

ZODIAC_SIGNS: List[Tuple[str, str, str, str]] = [
    # (english, glyph, chinese, element)
    ("Aries",       "♈", "白羊", "Fire"),
    ("Taurus",      "♉", "金牛", "Earth"),
    ("Gemini",      "♊", "雙子", "Air"),
    ("Cancer",      "♋", "巨蟹", "Water"),
    ("Leo",         "♌", "獅子", "Fire"),
    ("Virgo",       "♍", "處女", "Earth"),
    ("Libra",       "♎", "天秤", "Air"),
    ("Scorpio",     "♏", "天蠍", "Water"),
    ("Sagittarius", "♐", "射手", "Fire"),
    ("Capricorn",   "♑", "摩羯", "Earth"),
    ("Aquarius",    "♒", "水瓶", "Air"),
    ("Pisces",      "♓", "雙魚", "Water"),
]

SIGN_NAMES = [s[0] for s in ZODIAC_SIGNS]

# Sign modalities
SIGN_MODALITY: Dict[str, str] = {
    "Aries": "Cardinal",    "Taurus": "Fixed",     "Gemini": "Mutable",
    "Cancer": "Cardinal",   "Leo": "Fixed",         "Virgo": "Mutable",
    "Libra": "Cardinal",    "Scorpio": "Fixed",     "Sagittarius": "Mutable",
    "Capricorn": "Cardinal","Aquarius": "Fixed",    "Pisces": "Mutable",
}

# ============================================================
# Essential Dignities — Traditional Seven Planets
# 本質尊貴 — 傳統七星（Lilly CA pp. 101-115）
# ============================================================

# Domicile rulers (sign 0-11)
# Source: Lilly CA p. 104; Bonatti LA Tract. I
DOMICILE_RULERS: Dict[int, str] = {
    0:  "Mars",    # Aries
    1:  "Venus",   # Taurus
    2:  "Mercury", # Gemini
    3:  "Moon",    # Cancer
    4:  "Sun",     # Leo
    5:  "Mercury", # Virgo
    6:  "Venus",   # Libra
    7:  "Mars",    # Scorpio
    8:  "Jupiter", # Sagittarius
    9:  "Saturn",  # Capricorn
    10: "Saturn",  # Aquarius
    11: "Jupiter", # Pisces
}

# Exaltation rulers and exact degree (seven traditional planets only)
# Source: Lilly CA pp. 106-107
EXALTATION_RULERS: Dict[int, Tuple[str, int]] = {
    0:  ("Sun",     19),  # Sun exalted 19° Aries
    1:  ("Moon",    3),   # Moon exalted 3° Taurus
    3:  ("Jupiter", 15),  # Jupiter exalted 15° Cancer
    5:  ("Mercury", 15),  # Mercury exalted 15° Virgo
    6:  ("Saturn",  21),  # Saturn exalted 21° Libra
    9:  ("Mars",    28),  # Mars exalted 28° Capricorn
    11: ("Venus",   27),  # Venus exalted 27° Pisces
}

# Correct exaltation mapping
EXALTATION: Dict[str, Tuple[int, int]] = {
    # planet: (sign_index, degree)
    "Sun":     (0, 19),   # 19° Aries — Lilly CA p.106
    "Moon":    (1, 3),    # 3° Taurus
    "Mercury": (5, 15),   # 15° Virgo
    "Venus":   (11, 27),  # 27° Pisces
    "Mars":    (9, 28),   # 28° Capricorn
    "Jupiter": (3, 15),   # 15° Cancer
    "Saturn":  (6, 21),   # 21° Libra
}

# Detriment = opposite sign of domicile
def _detriment_sign(domicile_idx: int) -> int:
    return (domicile_idx + 6) % 12

DETRIMENT_RULERS: Dict[int, str] = {
    (_detriment_sign(idx)): planet
    for idx, planet in DOMICILE_RULERS.items()
}

# Fall = opposite sign of exaltation
FALL_SIGN: Dict[str, int] = {
    planet: (sign + 6) % 12
    for planet, (sign, _) in EXALTATION.items()
}

# Triplicity rulers (Lilly uses Day/Night/Participating)
# Source: Lilly CA pp. 109-110; Dorothean triplicity
TRIPLICITY_RULERS: Dict[str, Tuple[str, str, str]] = {
    # element: (day_ruler, night_ruler, participating)
    "Fire":  ("Sun",     "Jupiter", "Saturn"),
    "Earth": ("Venus",   "Moon",    "Mars"),
    "Air":   ("Saturn",  "Mercury", "Jupiter"),
    "Water": ("Venus",   "Mars",    "Moon"),
}

# Terms (Ptolemaic boundaries) — 5 planets divide each sign
# Each tuple: (planet, degree_start, degree_end)
# Source: Lilly CA pp. 113-114 (Ptolemy's terms)
TERMS_PTOLEMY: Dict[int, List[Tuple[str, int, int]]] = {
    0:  [("Jupiter",0,6),  ("Venus",6,12),   ("Mercury",12,20), ("Mars",20,25),   ("Saturn",25,30)],
    1:  [("Venus",0,8),    ("Mercury",8,14),  ("Jupiter",14,22), ("Saturn",22,27), ("Mars",27,30)],
    2:  [("Mercury",0,6),  ("Jupiter",6,12),  ("Venus",12,17),   ("Mars",17,24),   ("Saturn",24,30)],
    3:  [("Mars",0,7),     ("Venus",7,13),    ("Mercury",13,19), ("Jupiter",19,26),("Saturn",26,30)],
    4:  [("Jupiter",0,6),  ("Venus",6,11),    ("Saturn",11,18),  ("Mercury",18,24),("Mars",24,30)],
    5:  [("Mercury",0,7),  ("Venus",7,13),    ("Jupiter",13,18), ("Saturn",18,24), ("Mars",24,30)],
    6:  [("Saturn",0,6),   ("Mercury",6,14),  ("Jupiter",14,21), ("Venus",21,28),  ("Mars",28,30)],
    7:  [("Mars",0,7),     ("Venus",7,11),    ("Mercury",11,19), ("Jupiter",19,24),("Saturn",24,30)],
    8:  [("Jupiter",0,12), ("Venus",12,17),   ("Mercury",17,21), ("Saturn",21,26), ("Mars",26,30)],
    9:  [("Mercury",0,7),  ("Jupiter",7,14),  ("Venus",14,22),   ("Saturn",22,26), ("Mars",26,30)],
    10: [("Mercury",0,7),  ("Venus",7,13),    ("Jupiter",13,20), ("Mars",20,25),   ("Saturn",25,30)],
    11: [("Venus",0,12),   ("Jupiter",12,16), ("Mercury",16,19), ("Mars",19,28),   ("Saturn",28,30)],
}

# Faces / Decanates (Chaldean order)
# Source: Lilly CA p.116; Bonatti LA Tract. V c. 3
# Each sign has 3 faces, each ruled by a planet (Chaldean order: Saturn→Jupiter→Mars→Sun→Venus→Mercury→Moon, repeat)
_CHALDEAN = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
# Face at degree 0-9 = face 1, 10-19 = face 2, 20-29 = face 3
# Starting sequence: Aries f1 = Mars, f2 = Sun, f3 = Venus
# (full Chaldean faces table)
FACES: Dict[int, List[str]] = {
    0:  ["Mars",    "Sun",     "Venus"],
    1:  ["Mercury", "Moon",    "Saturn"],
    2:  ["Jupiter", "Mars",    "Sun"],
    3:  ["Venus",   "Mercury", "Moon"],
    4:  ["Saturn",  "Jupiter", "Mars"],
    5:  ["Sun",     "Venus",   "Mercury"],
    6:  ["Moon",    "Saturn",  "Jupiter"],
    7:  ["Mars",    "Sun",     "Venus"],
    8:  ["Mercury", "Moon",    "Saturn"],
    9:  ["Jupiter", "Mars",    "Sun"],
    10: ["Venus",   "Mercury", "Moon"],
    11: ["Saturn",  "Jupiter", "Mars"],
}

# ============================================================
# Dignity Scores (for strength calculation)
# Source: Lilly CA p. 115; used in judgment
# ============================================================

DIGNITY_SCORES: Dict[str, int] = {
    "domicile":   5,
    "exaltation": 4,
    "triplicity": 3,
    "term":       2,
    "face":       1,
    "peregrine":  0,
    "detriment": -5,
    "fall":       -4,
}

# Accidental Dignity scores
# Source: Lilly CA pp. 115-116
ACCIDENTAL_DIGNITY_SCORES: Dict[str, int] = {
    "angular":           5,   # 1st, 4th, 7th, 10th house
    "succedent":         3,   # 2nd, 5th, 8th, 11th house
    "cadent":           -3,   # 3rd, 6th, 9th, 12th house
    "direct":            4,   # not retrograde
    "retrograde":       -5,
    "fast":              2,   # faster than mean motion
    "slow":             -2,
    "oriental":          2,   # oriental of the Sun (for Mars, Jupiter, Saturn)
    "occidental":        2,   # occidental of the Sun (for Moon, Venus, Mercury)
    "cazimi":            5,   # within 17' of Sun center (partile conjunction)
    "combust":          -5,   # within 8° 30' of Sun
    "under_sunbeams":   -4,   # within 17° of Sun but outside combustion
    "joy_house":         2,   # planet in its joy house
    "free_from_combustion": 2, # more than 17° from Sun
}

# Planetary mean daily motions (approximate, for fast/slow detection)
MEAN_MOTION: Dict[str, float] = {
    "Sun":     0.9833,
    "Moon":   13.1764,
    "Mercury": 1.3833,
    "Venus":   1.2000,
    "Mars":    0.5240,
    "Jupiter": 0.0831,
    "Saturn":  0.0334,
}

# Planetary Joys (house they rejoice in)
# Source: Lilly CA p. 92; Bonatti LA
PLANETARY_JOYS: Dict[str, int] = {
    "Mercury": 1,
    "Moon":    3,
    "Venus":   5,
    "Mars":    6,
    "Sun":     9,
    "Jupiter": 11,
    "Saturn":  12,
}

# ============================================================
# Aspects (Horary — strict traditional orbs)
# Source: Lilly CA pp. 106-108
# ============================================================

ASPECT_DEFINITIONS: List[Dict] = [
    # name, angle, english_name, chinese_name, orb, nature
    {"name": "conjunction",  "angle": 0,   "en": "Conjunction ☌",   "cn": "合相",   "orb": 8.0,  "nature": "neutral"},
    {"name": "sextile",      "angle": 60,  "en": "Sextile ⚹",       "cn": "六合",   "orb": 6.0,  "nature": "benefic"},
    {"name": "square",       "angle": 90,  "en": "Square □",        "cn": "刑相",   "orb": 6.0,  "nature": "malefic"},
    {"name": "trine",        "angle": 120, "en": "Trine △",         "cn": "三合",   "orb": 8.0,  "nature": "benefic"},
    {"name": "opposition",   "angle": 180, "en": "Opposition ☍",    "cn": "沖相",   "orb": 8.0,  "nature": "malefic"},
    # Minor aspects used in Horary
    {"name": "quincunx",     "angle": 150, "en": "Quincunx ⚻",      "cn": "梅花相", "orb": 3.0,  "nature": "neutral"},  # Bonatti
    {"name": "semi-sextile", "angle": 30,  "en": "Semi-sextile ⌖",  "cn": "半六合", "orb": 2.0,  "nature": "neutral"},
]

# Note: In strict Lilly tradition, only 5 major aspects are used for judgment.
# Quincunx is mentioned by Bonatti as a "refranation" aspect.

# ============================================================
# House Significations (Horary)
# Source: Lilly CA pp. 50-64; Bonatti LA Tract. II
# ============================================================

HOUSE_SIGNIFICATIONS: Dict[int, Dict] = {
    1:  {
        "en": "The querent, body, vitality, the question itself, life",
        "cn": "問卜者本身、身體、生命力、問題本質",
        "topics": ["life", "health", "appearance", "self", "vitality"],
    },
    2:  {
        "en": "Wealth, movable goods, financial resources, possessions, helpers",
        "cn": "財富、動產、財務資源、助手",
        "topics": ["money", "wealth", "possessions", "income"],
    },
    3:  {
        "en": "Siblings, short journeys, communications, neighbours, letters, rumours",
        "cn": "兄弟姊妹、短途旅行、通訊、鄰居",
        "topics": ["siblings", "travel_short", "communication", "letters"],
    },
    4:  {
        "en": "Father, land, property, home, end of matter, hidden treasure, grave",
        "cn": "父親、土地、房產、家宅、事情結果、寶藏、墓地",
        "topics": ["father", "property", "home", "end_of_matter", "real_estate"],
    },
    5:  {
        "en": "Children, pleasure, love affairs, gambling, entertainment, ambassadors",
        "cn": "子女、享樂、戀愛、賭博、娛樂、大使",
        "topics": ["children", "romance", "pleasure", "gambling"],
    },
    6:  {
        "en": "Illness, servants, small animals, work, employees, clothing",
        "cn": "疾病、僕人、小動物、工作、員工、衣物",
        "topics": ["illness", "servants", "small_animals", "work"],
    },
    7:  {
        "en": "Marriage, partnerships, open enemies, the astrologer, contracts",
        "cn": "婚姻、合夥、公開敵人、占星師、合同",
        "topics": ["marriage", "partnership", "enemies", "contracts", "others"],
    },
    8:  {
        "en": "Death, legacies, partner's wealth, surgeries, fears, transformation",
        "cn": "死亡、遺產、伴侶財富、手術、恐懼、轉化",
        "topics": ["death", "legacies", "surgery", "transformation"],
    },
    9:  {
        "en": "Long journeys, religion, philosophy, higher education, foreign lands, dreams",
        "cn": "長途旅行、宗教、哲學、高等教育、異鄉、夢境",
        "topics": ["travel_long", "religion", "education", "foreign"],
    },
    10: {
        "en": "Career, honour, reputation, authority, the king/queen, mother",
        "cn": "事業、名譽、聲望、權威、君主、母親",
        "topics": ["career", "honor", "authority", "status"],
    },
    11: {
        "en": "Friends, hopes, wishes, allies, the king's advisors",
        "cn": "友人、希望、願望、同盟、君主謀臣",
        "topics": ["friends", "hopes", "wishes", "allies"],
    },
    12: {
        "en": "Hidden enemies, exile, imprisonment, sorrow, large animals, self-undoing",
        "cn": "隱藏敵人、流亡、監禁、悲傷、大型動物、自我破壞",
        "topics": ["hidden_enemies", "imprisonment", "sorrow", "large_animals"],
    },
}

# ============================================================
# Question Types and Signification Mapping
# Source: Lilly CA various chapters; Bonatti LA Tract. V-VIII
# ============================================================

QUESTION_TYPES: Dict[str, Dict] = {
    "marriage": {
        "en": "Marriage / Partnership",
        "cn": "婚姻／合夥",
        "primary_house": 7,
        "secondary_houses": [1, 5],
        "primary_significator_house": 7,
        "secondary_significator_house": 5,
        "arabic_part": "Lot of Marriage",
        "lilly_ref": "CA Part II, Chapter 37",
        "bonatti_ref": "Liber Astronomiae Tract. V, c. 15",
    },
    "career": {
        "en": "Career / Profession",
        "cn": "事業／職業",
        "primary_house": 10,
        "secondary_houses": [1, 2, 6],
        "primary_significator_house": 10,
        "arabic_part": None,
        "lilly_ref": "CA Part II, Chapter 43",
        "bonatti_ref": "Liber Astronomiae Tract. VI, c. 8",
    },
    "wealth": {
        "en": "Wealth / Financial",
        "cn": "財富／財務",
        "primary_house": 2,
        "secondary_houses": [8, 10, 11],
        "primary_significator_house": 2,
        "arabic_part": "Lot of Fortune",
        "lilly_ref": "CA Part II, Chapter 41",
        "bonatti_ref": "Liber Astronomiae Tract. V, c. 11",
    },
    "lost_item": {
        "en": "Lost / Stolen Item",
        "cn": "失物／被盜物品",
        "primary_house": 2,
        "secondary_houses": [4, 7, 8],
        "primary_significator_house": 2,
        "arabic_part": None,
        "lilly_ref": "CA Part II, Chapter 49",
        "bonatti_ref": "Liber Astronomiae Tract. VI, c. 5",
    },
    "illness": {
        "en": "Health / Illness",
        "cn": "健康／疾病",
        "primary_house": 6,
        "secondary_houses": [1, 8, 12],
        "primary_significator_house": 6,
        "arabic_part": None,
        "lilly_ref": "CA Part III",
        "bonatti_ref": "Liber Astronomiae Tract. V, c. 4",
    },
    "travel": {
        "en": "Travel / Journey",
        "cn": "旅行／旅程",
        "primary_house": 9,
        "secondary_houses": [3, 12],
        "primary_significator_house": 9,
        "arabic_part": None,
        "lilly_ref": "CA Part II, Chapter 34",
        "bonatti_ref": "Liber Astronomiae Tract. V, c. 14",
    },
    "missing_person": {
        "en": "Missing Person / Fugitive",
        "cn": "失蹤人員／逃亡者",
        "primary_house": 7,
        "secondary_houses": [1, 4],
        "primary_significator_house": 7,
        "arabic_part": None,
        "lilly_ref": "CA Part II, Chapter 48",
        "bonatti_ref": "Liber Astronomiae Tract. VI, c. 4",
    },
    "property": {
        "en": "Property / Real Estate",
        "cn": "房產／不動產",
        "primary_house": 4,
        "secondary_houses": [1, 2],
        "primary_significator_house": 4,
        "arabic_part": None,
        "lilly_ref": "CA Part II, Chapter 40",
        "bonatti_ref": "Liber Astronomiae Tract. V, c. 9",
    },
    "general": {
        "en": "General Question (Yes/No)",
        "cn": "一般問題（是非題）",
        "primary_house": 1,
        "secondary_houses": [7],
        "primary_significator_house": 1,
        "arabic_part": "Lot of Fortune",
        "lilly_ref": "CA Part I, Chapter 7",
        "bonatti_ref": "Liber Astronomiae 146 Considerations",
    },
}

# ============================================================
# Strictures Against Judgment
# Source: Lilly CA pp. 121-123
# ============================================================

STRICTURE_DESCRIPTIONS: Dict[str, Dict] = {
    "early_ascendant": {
        "en": "Early Ascendant (< 3°): The matter is not yet ripe; events have not fully developed.",
        "cn": "上升點過早（< 3°）：事情尚未成熟，一切尚在發展之中。",
        "severity": "warning",
        "lilly_ref": "CA p. 122",
    },
    "late_ascendant": {
        "en": "Late Ascendant (> 27°): The matter is near its end or is too late to act upon.",
        "cn": "上升點過晚（> 27°）：事情接近終結，或已過採取行動的時機。",
        "severity": "warning",
        "lilly_ref": "CA p. 122",
    },
    "voc_moon": {
        "en": "Void of Course Moon: The Moon makes no more aspects before leaving its sign. The matter will come to nothing or yield little result.",
        "cn": "月亮無入相位（虛空月）：月亮在離開星座前不再形成任何相位。事情將無結果或徒勞無功。",
        "severity": "warning",
        "lilly_ref": "CA p. 122",
    },
    "saturn_in_1st": {
        "en": "Saturn in 1st House: The querent's affairs are obstructed; delays and obstacles prevail.",
        "cn": "土星在第一宮：問卜者之事受阻，延誤與障礙盛行。",
        "severity": "caution",
        "lilly_ref": "CA p. 123",
    },
    "saturn_in_7th": {
        "en": "Saturn in 7th House: The astrologer may misjudge; obstruction in the matter signified by the 7th house.",
        "cn": "土星在第七宮：占星師可能判斷有誤；第七宮所代表之事受阻。",
        "severity": "caution",
        "lilly_ref": "CA p. 123",
    },
    "moon_in_via_combusta": {
        "en": "Moon in Via Combusta (15° Libra – 15° Scorpio): Weakens the judgment; difficult and unfortunate matters.",
        "cn": "月亮在燃燒之路（天秤15°至天蠍15°）：削弱判斷；事情困難不順。",
        "severity": "caution",
        "lilly_ref": "CA p. 123",
    },
    "asc_lord_combust": {
        "en": "Lord of the Ascendant combust: The querent is in a weakened state and may not see clearly.",
        "cn": "上升主星焦傷：問卜者狀態衰弱，可能視野不清。",
        "severity": "caution",
        "lilly_ref": "CA p. 123",
    },
    "early_degree_ascending": {
        "en": "Early degrees of 1st house (0°-3°): Too early to judge clearly.",
        "cn": "第一宮宮頭度數過小（0°-3°）：時機過早，難以明確判斷。",
        "severity": "info",
        "lilly_ref": "CA p. 122",
    },
}

# ============================================================
# Void of Course Moon — Lilly's Exceptions
# Source: Lilly CA p. 122
# Signs where VOC Moon may still show results (Lilly exceptions)
# ============================================================

VOC_EXCEPTIONS: List[int] = [
    1,   # Taurus — Moon in own exaltation sign
    3,   # Cancer — Moon in own domicile sign
    8,   # Sagittarius — Jupiter's domicile, expansive fortune
    11,  # Pisces — Jupiter's domicile, spiritual support
]

# ============================================================
# Combustion distances
# Source: Lilly CA p. 113
# ============================================================

COMBUSTION_ORB: float = 8.5      # degrees — combustion zone
CAZIMI_ORB: float = 0.2833       # 17 arcminutes — cazimi (heart of Sun)
UNDER_SUNBEAMS_ORB: float = 17.0 # degrees — under sunbeams

# ============================================================
# Via Combusta (Combust Way)
# Source: Lilly CA p. 123; Bonatti LA
# ============================================================

VIA_COMBUSTA_START: float = 195.0  # 15° Libra (Libra=180°, +15=195°)
VIA_COMBUSTA_END: float = 225.0    # 15° Scorpio (Scorpio=210°, +15=225°)

# ============================================================
# Lilly's Aphorisms (selected for judgment)
# Source: Lilly CA Part I, Chapter 16
# ============================================================

LILLY_APHORISMS: List[Dict] = [
    {
        "number": 1,
        "en": "The Moon making good aspect to the Lord of the Ascendant, or the Lord of the question, brings the matter to perfection.",
        "cn": "月亮與上升主星或問題主星形成吉相，事情可得圓滿。",
        "lilly_ref": "CA Part I, Aph. 1",
    },
    {
        "number": 2,
        "en": "If the Moon be void of course and in Taurus, Cancer, Sagittarius or Pisces, the matter may yet proceed, but slowly.",
        "cn": "若月亮虛空且位於金牛、巨蟹、射手或雙魚，事情或仍可進行，但緩慢。",
        "lilly_ref": "CA Part I, Aph. 2 / p. 122",
    },
    {
        "number": 3,
        "en": "A planet in its own dignities is strong and able to perform what is required of it.",
        "cn": "行星在本尊貴位時，力量強健，足以完成所求之事。",
        "lilly_ref": "CA Part I, Aph. 3",
    },
    {
        "number": 4,
        "en": "A combust planet has no strength and cannot help the querent; it is in a state of affliction.",
        "cn": "焦傷行星毫無力量，無法助問卜者；此行星處於受困狀態。",
        "lilly_ref": "CA Part I, Aph. 4",
    },
    {
        "number": 5,
        "en": "Mutual reception by domicile or exaltation greatly assists perfection of a matter.",
        "cn": "行星互換廟旺（相互接納）大助事情圓滿。",
        "lilly_ref": "CA Part I, Aph. 5",
    },
    {
        "number": 6,
        "en": "Translation of Light brings matters to perfection that seem otherwise impossible.",
        "cn": "光之傳遞可使看似不可能之事得以完成。",
        "lilly_ref": "CA Part I, Aph. 6",
    },
    {
        "number": 7,
        "en": "Collection of Light: when two planets both apply to a third, the third collects their light and brings the matter to perfection.",
        "cn": "光之聚合：兩顆行星同時向第三顆入相，第三顆聚其光，事情得圓滿。",
        "lilly_ref": "CA Part I, Aph. 7",
    },
    {
        "number": 8,
        "en": "Prohibition occurs when a faster planet intercepts between two significators before their aspect is complete.",
        "cn": "禁阻：快速行星插入兩主星之間，阻止其相位完成。",
        "lilly_ref": "CA Part I, Aph. 8",
    },
]

# ============================================================
# Bonatti's Key Considerations (selected)
# Source: Bonatti "Liber Astronomiae" 146 Considerations
# ============================================================

BONATTI_CONSIDERATIONS: List[Dict] = [
    {
        "number": 1,
        "en": "See whether the querent has come to you freely, and whether the hour is radical (the ASC lord rules the hour).",
        "cn": "查看問卜者是否主動前來，以及問時是否正時（上升主星統治問時）。",
        "ref": "Bonatti, 1st Consideration",
    },
    {
        "number": 2,
        "en": "The Moon is the general significatrix of all questions; consider her carefully.",
        "cn": "月亮是所有問題的共同主星；須謹慎考量。",
        "ref": "Bonatti, 2nd Consideration",
    },
    {
        "number": 3,
        "en": "If the Lord of the 7th house is weak or afflicted, the judgment of the astrologer will be imperfect.",
        "cn": "若第七宮主星虛弱或受困，占星師的判斷將不完整。",
        "ref": "Bonatti, 3rd Consideration",
    },
    {
        "number": 4,
        "en": "Consider whether the ASC is early or late, and whether Saturn is in the 1st or 7th.",
        "cn": "考量上升點是否過早或過晚，以及土星是否在第一或第七宮。",
        "ref": "Bonatti, 4th Consideration",
    },
    {
        "number": 5,
        "en": "If the significators are applying by good aspect with reception, the matter will perfect perfectly.",
        "cn": "若主星通過吉相入相並有互容，事情將得圓滿完成。",
        "ref": "Bonatti, 7th Consideration",
    },
]

# ============================================================
# Vedic Prashna — Rashis and Lords
# Source: Prasna Marga (Kerala Jyotish, traditional text)
# ============================================================

VEDIC_RASHIS: List[Tuple[str, str, str, str]] = [
    # (english, glyph, chinese, lord)
    ("Mesha",     "♈", "牧羊", "Mars"),
    ("Vrishabha", "♉", "金牛", "Venus"),
    ("Mithuna",   "♊", "雙子", "Mercury"),
    ("Karka",     "♋", "巨蟹", "Moon"),
    ("Simha",     "♌", "獅子", "Sun"),
    ("Kanya",     "♍", "處女", "Mercury"),
    ("Tula",      "♎", "天秤", "Venus"),
    ("Vrischika", "♏", "天蠍", "Mars"),
    ("Dhanu",     "♐", "射手", "Jupiter"),
    ("Makara",    "♑", "摩羯", "Saturn"),
    ("Kumbha",    "♒", "水瓶", "Saturn"),
    ("Meena",     "♓", "雙魚", "Jupiter"),
]

# Vedic planet names
VEDIC_PLANET_NAMES: Dict[str, str] = {
    "Sun":     "Surya (太陽)",
    "Moon":    "Chandra (月亮)",
    "Mars":    "Mangal (火星)",
    "Mercury": "Budha (水星)",
    "Jupiter": "Guru (木星)",
    "Venus":   "Shukra (金星)",
    "Saturn":  "Shani (土星)",
    "Rahu":    "Rahu (羅睺)",
    "Ketu":    "Ketu (計都)",
}

# Vedic exaltation signs
VEDIC_EXALTATION: Dict[str, int] = {
    "Sun":     0,   # Mesha (Aries)
    "Moon":    1,   # Vrishabha (Taurus)
    "Mars":    9,   # Makara (Capricorn)
    "Mercury": 5,   # Kanya (Virgo)
    "Jupiter": 3,   # Karka (Cancer)
    "Venus":   11,  # Meena (Pisces)
    "Saturn":  6,   # Tula (Libra)
}

# Vedic debilitation (fall) — opposite of exaltation
VEDIC_DEBILITATION: Dict[str, int] = {
    planet: (sign + 6) % 12
    for planet, sign in VEDIC_EXALTATION.items()
}

# Vedic domicile (own sign)
VEDIC_OWN_SIGNS: Dict[str, List[int]] = {
    "Sun":     [4],           # Simha (Leo)
    "Moon":    [3],           # Karka (Cancer)
    "Mars":    [0, 7],        # Mesha, Vrischika
    "Mercury": [2, 5],        # Mithuna, Kanya
    "Jupiter": [8, 11],       # Dhanu, Meena
    "Venus":   [1, 6],        # Vrishabha, Tula
    "Saturn":  [9, 10],       # Makara, Kumbha
}

# ============================================================
# Arudha Lagna computation
# Source: Prasna Marga Chapter 4; also Jaimini Sutras
# ============================================================

# The Arudha Lagna (external image / manifestation indicator) is computed as:
# Count the Lagna lord's sign from Lagna; then count the same distance again.
# Special rule: if result falls in Lagna itself or 7th from Lagna,
# move 10th from that position.
# Source: Prasna Marga Ch. 4, v. 15-16

# ============================================================
# Prashna Question Types (Vedic)
# Source: Prasna Marga various chapters
# ============================================================

PRASHNA_QUESTION_TYPES: Dict[str, Dict] = {
    "marriage": {
        "en": "Marriage / Relationships",
        "cn": "婚姻／感情",
        "primary_house": 7,
        "karaka": "Venus",
        "pm_ref": "Prasna Marga Ch. 15",
    },
    "career": {
        "en": "Career / Profession",
        "cn": "事業／職業",
        "primary_house": 10,
        "karaka": "Sun",
        "pm_ref": "Prasna Marga Ch. 16",
    },
    "wealth": {
        "en": "Wealth / Finance",
        "cn": "財富／財務",
        "primary_house": 2,
        "karaka": "Jupiter",
        "pm_ref": "Prasna Marga Ch. 14",
    },
    "health": {
        "en": "Health / Disease",
        "cn": "健康／疾病",
        "primary_house": 6,
        "karaka": "Mars",
        "pm_ref": "Prasna Marga Ch. 12",
    },
    "general": {
        "en": "General Question",
        "cn": "一般問題",
        "primary_house": 1,
        "karaka": "Moon",
        "pm_ref": "Prasna Marga Ch. 1",
    },
}

# ============================================================
# Timing indicators in Horary
# Source: Lilly CA pp. 143-148
# ============================================================

TIMING_UNIT: Dict[str, Dict] = {
    "Cardinal": {
        "en": "Cardinal sign — Days or weeks",
        "cn": "開創星座 — 日或週",
        "unit": "days",
    },
    "Fixed": {
        "en": "Fixed sign — Months or years",
        "cn": "固定星座 — 月或年",
        "unit": "months",
    },
    "Mutable": {
        "en": "Mutable sign — Weeks or months",
        "cn": "變動星座 — 週或月",
        "unit": "weeks",
    },
}

HOUSE_TIMING: Dict[int, str] = {
    1:  "Angular",   4: "Angular",   7:  "Angular",   10: "Angular",
    2:  "Succedent", 5: "Succedent", 8:  "Succedent",  11: "Succedent",
    3:  "Cadent",    6: "Cadent",    9:  "Cadent",     12: "Cadent",
}
