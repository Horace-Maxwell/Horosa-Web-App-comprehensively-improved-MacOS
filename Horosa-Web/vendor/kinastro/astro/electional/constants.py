"""
astro/electional/constants.py — Constants for Electional Astrology & Vedic Muhurta

Western Electional sources:
  - William Lilly, "Christian Astrology" (1647) [CA]
  - Al-Biruni, "Book of Instruction in the Elements of the Art of Astrology" (~1029) [BI]
  - Guido Bonatti, "Liber Astronomiae" (~1277) [LA]
  - Abu Ma'shar, "Kitab al-Mudkhal al-Kabir" [KM]

Vedic Muhurta sources:
  - Muhurta Chintamani [MC]
  - Kalaprakashika [KP]
  - Brihat Parashara Hora Shastra [BPHS]
  - Muhurta Martanda [MM]
  - Electional Astrology by B. V. Raman [BVR]
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional

# ============================================================
# Western — Traditional Planet Data
# ============================================================

TRADITIONAL_PLANETS: List[str] = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
]

PLANET_IDS: Dict[str, int] = {
    "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3,
    "Mars": 4, "Jupiter": 5, "Saturn": 6,
}

PLANET_GLYPHS: Dict[str, str] = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
}

PLANET_CN: Dict[str, str] = {
    "Sun": "太陽", "Moon": "月亮", "Mercury": "水星", "Venus": "金星",
    "Mars": "火星", "Jupiter": "木星", "Saturn": "土星",
}

PLANET_NATURE: Dict[str, str] = {
    "Sun": "benefic",   # moderate benefic in electional
    "Moon": "benefic",
    "Mercury": "neutral",
    "Venus": "benefic",
    "Mars": "malefic",
    "Jupiter": "benefic",
    "Saturn": "malefic",
}

# ============================================================
# Zodiac Signs (Western Tropical)
# ============================================================

ZODIAC_SIGNS: List[Tuple[str, str, str, str]] = [
    # (name, glyph, cn_name, element)
    ("Aries", "♈", "牡羊座", "fire"),
    ("Taurus", "♉", "金牛座", "earth"),
    ("Gemini", "♊", "雙子座", "air"),
    ("Cancer", "♋", "巨蟹座", "water"),
    ("Leo", "♌", "獅子座", "fire"),
    ("Virgo", "♍", "處女座", "earth"),
    ("Libra", "♎", "天秤座", "air"),
    ("Scorpio", "♏", "天蠍座", "water"),
    ("Sagittarius", "♐", "射手座", "fire"),
    ("Capricorn", "♑", "摩羯座", "earth"),
    ("Aquarius", "♒", "水瓶座", "air"),
    ("Pisces", "♓", "雙魚座", "water"),
]

SIGN_NAMES: List[str] = [s[0] for s in ZODIAC_SIGNS]

# Domicile Rulers (traditional seven)
DOMICILE_RULERS: Dict[int, str] = {
    0: "Mars",      # Aries
    1: "Venus",     # Taurus
    2: "Mercury",   # Gemini
    3: "Moon",      # Cancer
    4: "Sun",       # Leo
    5: "Mercury",   # Virgo
    6: "Venus",     # Libra
    7: "Mars",      # Scorpio
    8: "Jupiter",   # Sagittarius
    9: "Saturn",    # Capricorn
    10: "Saturn",   # Aquarius
    11: "Jupiter",  # Pisces
}

DETRIMENT_RULERS: Dict[int, str] = {
    (k + 6) % 12: v for k, v in DOMICILE_RULERS.items()
}

# Exaltation: planet → (sign_index, exact_degree)
EXALTATION: Dict[str, Tuple[int, float]] = {
    "Sun": (0, 19.0),        # Aries 19°
    "Moon": (1, 3.0),        # Taurus 3°
    "Mercury": (5, 15.0),    # Virgo 15°
    "Venus": (11, 27.0),     # Pisces 27°
    "Mars": (9, 28.0),       # Capricorn 28°
    "Jupiter": (3, 15.0),    # Cancer 15°
    "Saturn": (6, 21.0),     # Libra 21°
}

FALL_SIGN: Dict[str, int] = {
    planet: (sign + 6) % 12
    for planet, (sign, _) in EXALTATION.items()
}

# Essential Dignity Scores (Lilly, CA pp. 101-116)
DIGNITY_SCORES: Dict[str, int] = {
    "domicile": 5,
    "exaltation": 4,
    "triplicity": 3,
    "term": 2,
    "face": 1,
    "peregrine": 0,
    "detriment": -5,
    "fall": -4,
}

# Mean daily motion for traditional planets (degrees/day)
MEAN_MOTION: Dict[str, float] = {
    "Sun": 0.9856,
    "Moon": 13.1764,
    "Mercury": 1.3833,
    "Venus": 1.2000,
    "Mars": 0.5240,
    "Jupiter": 0.0831,
    "Saturn": 0.0334,
}

# ============================================================
# Planetary Hours (Chaldean Order)
# Source: Lilly CA p. 483; Al-Biruni BI §330
# ============================================================

# Chaldean order: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon
CHALDEAN_ORDER: List[str] = [
    "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon",
]

# Day names (0=Sunday … 6=Saturday)
WEEKDAY_NAMES: List[str] = [
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
]

WEEKDAY_NAMES_CN: List[str] = [
    "星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六",
]

# Day ruler for each weekday (0=Sun, 1=Mon, … 6=Sat)
WEEKDAY_RULERS: List[str] = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
]

# ============================================================
# Combustion Orbs (Western)
# Source: Lilly CA pp. 113-114
# ============================================================

CAZIMI_ORB: float = 0.2917    # 17' — in the heart of the Sun
COMBUSTION_ORB: float = 8.5   # 8°30' combustion
UNDER_SUNBEAMS_ORB: float = 17.0

VIA_COMBUSTA_START: float = 195.0   # 15° Libra
VIA_COMBUSTA_END: float = 225.0     # 15° Scorpio

# ============================================================
# Aspect Definitions (Western)
# ============================================================

ASPECT_DEFINITIONS: List[Dict] = [
    {"angle": 0,   "en": "Conjunction", "cn": "合相",    "nature": "neutral", "orb": 8.0},
    {"angle": 60,  "en": "Sextile",     "cn": "六合相",  "nature": "benefic", "orb": 6.0},
    {"angle": 90,  "en": "Square",      "cn": "四分相",  "nature": "malefic", "orb": 8.0},
    {"angle": 120, "en": "Trine",       "cn": "三合相",  "nature": "benefic", "orb": 8.0},
    {"angle": 180, "en": "Opposition",  "cn": "對分相",  "nature": "malefic", "orb": 8.0},
]

# ============================================================
# Western Electional Activity Types
# Source: Lilly CA pp. 383-536; Bonatti LA Tractatus VI
# ============================================================

WESTERN_ACTIVITY_TYPES: Dict[str, Dict] = {
    "marriage": {
        "en": "Marriage / Wedding",
        "cn": "婚姻／婚禮",
        "key_houses": [1, 7],
        "key_planets": ["Venus", "Moon", "Jupiter"],
        "avoid_planets": ["Mars", "Saturn"],
        "house_lords": [1, 7],
        "moon_rules": [
            "Moon applying to Venus or Jupiter is excellent",
            "Moon in Taurus, Cancer, Libra, or Pisces preferred",
            "Avoid Moon VOC, in Via Combusta, or applying to Mars/Saturn",
        ],
        "moon_rules_cn": [
            "月亮入相金星或木星為最佳",
            "月亮在金牛、巨蟹、天秤或雙魚座為佳",
            "避免虛空月、焦途月，避免月亮入相火星或土星",
        ],
        "benefic_positions": ["Venus in 1st or 7th", "Jupiter in 1st or 7th"],
        "notes_en": (
            "For marriage: strengthen the 1st and 7th house cusps and their lords. "
            "Place Venus in the 1st or 7th if possible. Avoid Mars and Saturn in 1st, 7th, or 8th. "
            "Moon should be applying to a benefic and free from combustion. "
            "Lilly CA pp. 383-388."
        ),
        "notes_cn": (
            "婚姻擇日：強化第一宮與第七宮及其宮主星。如可能，將金星置於第一或第七宮。"
            "避免火星和土星在第一、七、八宮。月亮應入相吉星且不受燃燒。"
            "（Lilly CA pp. 383-388）"
        ),
        "lilly_ref": "CA pp. 383-388",
    },
    "business_opening": {
        "en": "Business Opening / Commerce",
        "cn": "開業／商業",
        "key_houses": [1, 2, 10],
        "key_planets": ["Mercury", "Jupiter", "Venus", "Moon"],
        "avoid_planets": ["Mars", "Saturn"],
        "house_lords": [1, 2, 10],
        "moon_rules": [
            "Moon applying to Jupiter, Venus, or Sun favours prosperity",
            "Moon in Taurus, Cancer, Virgo, or Sagittarius is good for commerce",
            "Moon increasing in light (waxing) is preferred",
        ],
        "moon_rules_cn": [
            "月亮入相木星、金星或太陽有利繁榮",
            "月亮在金牛、巨蟹、處女或射手座利於商業",
            "月亮漸盈（增光）為佳",
        ],
        "notes_en": (
            "For opening a business: favour Mercury (contracts/commerce) and Jupiter (prosperity). "
            "ASC lord and 10th house lord should be strong and free from affliction. "
            "2nd house lord (wealth) should be well-placed. "
            "Lilly CA pp. 391-393; Bonatti LA Tract. VI."
        ),
        "notes_cn": (
            "開業擇日：強化水星（合約/商業）和木星（繁榮）。"
            "命宮主星和第十宮主星應強健且不受惡化。"
            "第二宮主星（財富）應位置良好。"
            "（Lilly CA pp. 391-393；Bonatti LA Tract. VI）"
        ),
        "lilly_ref": "CA pp. 391-393",
    },
    "contract_signing": {
        "en": "Contract Signing / Legal Agreement",
        "cn": "簽約／法律協議",
        "key_houses": [1, 3, 7],
        "key_planets": ["Mercury", "Jupiter"],
        "avoid_planets": ["Mars", "Saturn"],
        "house_lords": [1, 3, 7],
        "moon_rules": [
            "Moon applying to Mercury favours communication and agreement",
            "Moon in Gemini, Virgo, or Libra supports contracts",
            "Avoid retrograde Mercury when signing contracts",
        ],
        "moon_rules_cn": [
            "月亮入相水星有利溝通與協議",
            "月亮在雙子、處女或天秤座有利合約",
            "簽約時避免水星逆行",
        ],
        "notes_en": (
            "For contracts: Mercury must be direct, well-dignified, and free from combustion. "
            "7th house (the other party) should not be afflicted. "
            "Avoid Saturn in 7th (obstructive counterparty). "
            "Al-Biruni BI §455; Lilly CA pp. 391-393."
        ),
        "notes_cn": (
            "簽約擇日：水星必須順行、尊貴且不受燃燒。"
            "第七宮（對方）不應受惡化。"
            "避免土星在第七宮（阻礙的對方）。"
            "（Al-Biruni BI §455；Lilly CA pp. 391-393）"
        ),
        "lilly_ref": "CA pp. 391-393; Al-Biruni BI §455",
    },
    "relocation": {
        "en": "Relocation / Moving House",
        "cn": "搬家／遷居",
        "key_houses": [1, 4, 7],
        "key_planets": ["Moon", "Jupiter", "Venus"],
        "avoid_planets": ["Mars", "Saturn"],
        "house_lords": [1, 4],
        "moon_rules": [
            "Moon waxing and applying to benefics favours the move",
            "Moon in Cancer, Taurus, or Pisces for harmonious new home",
            "Avoid Moon in Scorpio or applying to Saturn",
        ],
        "moon_rules_cn": [
            "月亮漸盈且入相吉星有利搬遷",
            "月亮在巨蟹、金牛或雙魚座有利和諧新家",
            "避免月亮在天蠍或入相土星",
        ],
        "notes_en": (
            "For relocation: 4th house (home, roots) and its lord are key. "
            "Strengthen the 1st house for the person, and 4th for the new home. "
            "Moon in Cancer or Taurus in the 4th is excellent. "
            "Lilly CA pp. 394-396."
        ),
        "notes_cn": (
            "搬家擇日：第四宮（家園、根基）及其宮主星是關鍵。"
            "強化第一宮（個人）和第四宮（新家）。"
            "月亮在第四宮的巨蟹或金牛座為最佳。"
            "（Lilly CA pp. 394-396）"
        ),
        "lilly_ref": "CA pp. 394-396",
    },
    "travel": {
        "en": "Travel / Journey",
        "cn": "旅行／出行",
        "key_houses": [1, 3, 9],
        "key_planets": ["Moon", "Mercury", "Jupiter"],
        "avoid_planets": ["Mars", "Saturn"],
        "house_lords": [1, 3, 9],
        "moon_rules": [
            "Moon in Gemini, Sagittarius, or Aquarius favours travel",
            "Moon applying to a benefic and increasing in light",
            "Avoid Moon in 8th or 12th house",
        ],
        "moon_rules_cn": [
            "月亮在雙子、射手或水瓶座有利旅行",
            "月亮入相吉星且增光",
            "避免月亮在第八或第十二宮",
        ],
        "notes_en": (
            "For travel: 3rd house (short journeys) or 9th house (long journeys). "
            "The Moon (the wanderer) should be free and applying to benefics. "
            "Avoid Saturn in 3rd or 9th (delays and obstructions). "
            "Lilly CA pp. 397-400."
        ),
        "notes_cn": (
            "旅行擇日：第三宮（短途）或第九宮（長途）。"
            "月亮（旅行者）應自由且入相吉星。"
            "避免土星在第三或第九宮（延誤與阻礙）。"
            "（Lilly CA pp. 397-400）"
        ),
        "lilly_ref": "CA pp. 397-400",
    },
    "surgery": {
        "en": "Surgery / Medical Procedure",
        "cn": "手術／醫療程序",
        "key_houses": [1, 6],
        "key_planets": ["Moon", "Mars"],
        "avoid_planets": ["Saturn"],
        "house_lords": [1, 6],
        "moon_rules": [
            "Avoid Moon in the sign ruling the body part being operated on",
            "Avoid Moon in the 1st, 8th, or the sign the patient's ASC is in",
            "Moon should not be in square or opposition to Mars or Saturn",
            "Do not operate on the full Moon or new Moon",
        ],
        "moon_rules_cn": [
            "避免月亮在手術部位所對應的星座",
            "避免月亮在第一、八宮或病人上升星座",
            "月亮不應與火星或土星四分或對分",
            "不在滿月或新月時手術",
        ],
        "notes_en": (
            "For surgery: the Moon must NOT be in the sign ruling the body part being treated. "
            "Avoid full Moon (excess bleeding) and new Moon (weakness). "
            "Mars in the 6th may cause complications. "
            "A waning Moon in a fixed sign with Jupiter present is most stable. "
            "Lilly CA pp. 404-408; Culpeper's Herbal tradition."
        ),
        "notes_cn": (
            "手術擇日：月亮絕對不能在手術部位對應的星座中。"
            "避免滿月（失血過多）和新月（體弱）。"
            "火星在第六宮可能引起併發症。"
            "月虧且在固定星座、木星在場是最穩定的配置。"
            "（Lilly CA pp. 404-408；Culpeper 草藥傳統）"
        ),
        "lilly_ref": "CA pp. 404-408",
    },
    "property_purchase": {
        "en": "Property Purchase / Real Estate",
        "cn": "買房／房地產",
        "key_houses": [1, 2, 4],
        "key_planets": ["Moon", "Jupiter", "Venus"],
        "avoid_planets": ["Mars", "Saturn"],
        "house_lords": [1, 2, 4],
        "moon_rules": [
            "Moon in Cancer (own sign) in the 4th is ideal",
            "Moon waxing and applying to Jupiter or Venus",
            "4th house and its lord should be strong",
        ],
        "moon_rules_cn": [
            "月亮在第四宮的巨蟹座（本宮）為最佳",
            "月亮漸盈且入相木星或金星",
            "第四宮及其宮主星應強健",
        ],
        "notes_en": (
            "For property purchase: 4th house (land, property) is paramount. "
            "Moon in Cancer in the 4th, or Jupiter in the 4th are excellent. "
            "Avoid Saturn in the 4th (encumbrances, old buildings with issues). "
            "2nd house (finances) should be well-placed. "
            "Lilly CA pp. 394-396."
        ),
        "notes_cn": (
            "買房擇日：第四宮（土地、房產）至關重要。"
            "月亮在第四宮的巨蟹座，或木星在第四宮為最佳。"
            "避免土星在第四宮（有擔保物、問題房屋）。"
            "第二宮（財務）應位置良好。"
            "（Lilly CA pp. 394-396）"
        ),
        "lilly_ref": "CA pp. 394-396",
    },
    "litigation": {
        "en": "Litigation / Legal Action",
        "cn": "訴訟／法律行動",
        "key_houses": [1, 7],
        "key_planets": ["Mars", "Sun", "Jupiter"],
        "avoid_planets": ["Saturn"],
        "house_lords": [1, 7],
        "moon_rules": [
            "Moon applying to the Sun or Mars can indicate active pursuit",
            "Moon stronger than 7th house lord favours the querent",
            "Avoid Saturn in the 1st (restricts your action)",
        ],
        "moon_rules_cn": [
            "月亮入相太陽或火星可指示積極追求",
            "月亮強於第七宮主星有利問卜者",
            "避免土星在第一宮（限制行動）",
        ],
        "notes_en": (
            "For litigation: make the 1st house lord stronger than the 7th (opponent). "
            "Place Mars well (as it governs conflict). "
            "Jupiter in the 1st or applying to the ASC lord gives legal advantage. "
            "Avoid Saturn in the 1st or 7th. "
            "Lilly CA pp. 415-420."
        ),
        "notes_cn": (
            "訴訟擇日：使第一宮主星強於第七宮主星（對手）。"
            "火星配置良好（因其主宰衝突）。"
            "木星在第一宮或入相命宮主星提供法律優勢。"
            "避免土星在第一或第七宮。"
            "（Lilly CA pp. 415-420）"
        ),
        "lilly_ref": "CA pp. 415-420",
    },
    "important_meeting": {
        "en": "Important Meeting / Conference",
        "cn": "重要會議／洽談",
        "key_houses": [1, 3, 7],
        "key_planets": ["Mercury", "Jupiter", "Moon"],
        "avoid_planets": ["Mars", "Saturn"],
        "house_lords": [1, 3, 7],
        "moon_rules": [
            "Moon applying to Mercury or Jupiter favours productive discourse",
            "Moon in Gemini, Libra, or Aquarius for communication and balance",
            "Avoid Moon VOC (nothing comes of it)",
        ],
        "moon_rules_cn": [
            "月亮入相水星或木星有利富有成效的對話",
            "月亮在雙子、天秤或水瓶座有利溝通與平衡",
            "避免虛空月（一事無成）",
        ],
        "notes_en": (
            "For important meetings: Mercury (communication) should be direct and dignified. "
            "Jupiter in the 1st or 7th brings goodwill. "
            "Moon not VOC is essential — a VOC Moon means nothing comes of the meeting. "
            "Lilly CA pp. 391-393."
        ),
        "notes_cn": (
            "重要會議擇日：水星（溝通）應順行且尊貴。"
            "木星在第一或第七宮帶來善意。"
            "月亮不能虛空 — 虛空月意味著會議無結果。"
            "（Lilly CA pp. 391-393）"
        ),
        "lilly_ref": "CA pp. 391-393",
    },
}

# ============================================================
# House Significations (Western)
# ============================================================

HOUSE_SIGNIFICATIONS: Dict[int, Dict] = {
    1: {"en": "Self, body, beginning", "cn": "自我、身體、開始"},
    2: {"en": "Wealth, possessions", "cn": "財富、財產"},
    3: {"en": "Short travel, siblings, communication", "cn": "短途旅行、兄弟姐妹、溝通"},
    4: {"en": "Home, property, roots, father", "cn": "家園、房產、根基、父親"},
    5: {"en": "Children, pleasure, creativity", "cn": "子女、娛樂、創意"},
    6: {"en": "Health, illness, servants", "cn": "健康、疾病、僕人"},
    7: {"en": "Partners, marriage, open enemies", "cn": "伴侶、婚姻、公開敵人"},
    8: {"en": "Death, transformation, others' money", "cn": "死亡、蛻變、他人財物"},
    9: {"en": "Long travel, religion, philosophy", "cn": "長途旅行、宗教、哲學"},
    10: {"en": "Career, status, reputation, mother", "cn": "事業、地位、名聲、母親"},
    11: {"en": "Friends, hopes, groups", "cn": "朋友、希望、群體"},
    12: {"en": "Hidden enemies, confinement, karma", "cn": "隱藏敵人、監禁、業力"},
}

# ============================================================
# Vedic — Panchanga Constants
# Source: Muhurta Chintamani; Brihat Parashara Hora Shastra
# ============================================================

# Nakshatras (27 lunar mansions) + Abhijit (28th)
NAKSHATRAS: List[Dict] = [
    {"num": 1,  "name": "Ashwini",     "cn": "馬蹄宿",   "ruler": "Ketu",    "nature": "light",   "span": (0.0, 13.333)},
    {"num": 2,  "name": "Bharani",     "cn": "胃宿",      "ruler": "Venus",   "nature": "fierce",  "span": (13.333, 26.667)},
    {"num": 3,  "name": "Krittika",    "cn": "昴宿",      "ruler": "Sun",     "nature": "mixed",   "span": (26.667, 40.0)},
    {"num": 4,  "name": "Rohini",      "cn": "畢宿",      "ruler": "Moon",    "nature": "fixed",   "span": (40.0, 53.333)},
    {"num": 5,  "name": "Mrigashira",  "cn": "觜宿",      "ruler": "Mars",    "nature": "soft",    "span": (53.333, 66.667)},
    {"num": 6,  "name": "Ardra",       "cn": "參宿",      "ruler": "Rahu",    "nature": "fierce",  "span": (66.667, 80.0)},
    {"num": 7,  "name": "Punarvasu",   "cn": "井宿",      "ruler": "Jupiter", "nature": "movable", "span": (80.0, 93.333)},
    {"num": 8,  "name": "Pushya",      "cn": "鬼宿",      "ruler": "Saturn",  "nature": "light",   "span": (93.333, 106.667)},
    {"num": 9,  "name": "Ashlesha",    "cn": "柳宿",      "ruler": "Mercury", "nature": "fierce",  "span": (106.667, 120.0)},
    {"num": 10, "name": "Magha",       "cn": "星宿",      "ruler": "Ketu",    "nature": "fierce",  "span": (120.0, 133.333)},
    {"num": 11, "name": "Purva Phalguni","cn": "張宿",    "ruler": "Venus",   "nature": "fierce",  "span": (133.333, 146.667)},
    {"num": 12, "name": "Uttara Phalguni","cn": "翼宿",   "ruler": "Sun",     "nature": "fixed",   "span": (146.667, 160.0)},
    {"num": 13, "name": "Hasta",       "cn": "軫宿",      "ruler": "Moon",    "nature": "light",   "span": (160.0, 173.333)},
    {"num": 14, "name": "Chitra",      "cn": "角宿",      "ruler": "Mars",    "nature": "soft",    "span": (173.333, 186.667)},
    {"num": 15, "name": "Swati",       "cn": "亢宿",      "ruler": "Rahu",    "nature": "movable", "span": (186.667, 200.0)},
    {"num": 16, "name": "Vishakha",    "cn": "氐宿",      "ruler": "Jupiter", "nature": "mixed",   "span": (200.0, 213.333)},
    {"num": 17, "name": "Anuradha",    "cn": "房宿",      "ruler": "Saturn",  "nature": "soft",    "span": (213.333, 226.667)},
    {"num": 18, "name": "Jyeshtha",    "cn": "心宿",      "ruler": "Mercury", "nature": "fierce",  "span": (226.667, 240.0)},
    {"num": 19, "name": "Mula",        "cn": "尾宿",      "ruler": "Ketu",    "nature": "fierce",  "span": (240.0, 253.333)},
    {"num": 20, "name": "Purva Ashadha","cn": "箕宿",     "ruler": "Venus",   "nature": "fierce",  "span": (253.333, 266.667)},
    {"num": 21, "name": "Uttara Ashadha","cn": "斗宿",    "ruler": "Sun",     "nature": "fixed",   "span": (266.667, 280.0)},
    {"num": 22, "name": "Shravana",    "cn": "牛宿",      "ruler": "Moon",    "nature": "movable", "span": (280.0, 293.333)},
    {"num": 23, "name": "Dhanishtha",  "cn": "女宿",      "ruler": "Mars",    "nature": "movable", "span": (293.333, 306.667)},
    {"num": 24, "name": "Shatabhisha", "cn": "虛宿",      "ruler": "Rahu",    "nature": "movable", "span": (306.667, 320.0)},
    {"num": 25, "name": "Purva Bhadrapada","cn": "危宿",  "ruler": "Jupiter", "nature": "fierce",  "span": (320.0, 333.333)},
    {"num": 26, "name": "Uttara Bhadrapada","cn": "室宿", "ruler": "Saturn",  "nature": "fixed",   "span": (333.333, 346.667)},
    {"num": 27, "name": "Revati",      "cn": "壁宿",      "ruler": "Mercury", "nature": "soft",    "span": (346.667, 360.0)},
]

# Nakshatras good for each activity
# Source: Muhurta Chintamani Ch. 2; Kalaprakashika
NAKSHATRA_GOOD_FOR: Dict[str, List[int]] = {
    # Nakshatra number (1-27) that is good for the activity
    "marriage":          [4, 7, 10, 12, 13, 15, 17, 21, 22, 26, 27],  # Rohini, Punarvasu, etc.
    "business_opening":  [1, 4, 7, 8, 12, 13, 15, 17, 21, 22, 27],
    "contract_signing":  [1, 7, 13, 15, 17, 22, 27],
    "relocation":        [4, 7, 12, 13, 17, 21, 22, 27],
    "travel":            [1, 5, 7, 13, 22, 27],
    "surgery":           [1, 3, 10, 14],  # Mars-ruled or fierce Nakshatras
    "property_purchase": [4, 8, 12, 21, 26],
    "litigation":        [3, 10, 14, 19],
    "important_meeting": [4, 7, 13, 15, 17, 22, 27],
}

# Nakshatras to avoid for each activity
NAKSHATRA_AVOID_FOR: Dict[str, List[int]] = {
    "marriage":          [2, 6, 9, 10, 11, 13, 14, 18, 19, 20, 25],
    "business_opening":  [2, 6, 9, 10, 11, 18, 19, 23, 25],
    "contract_signing":  [2, 6, 9, 10, 18, 19, 25],
    "relocation":        [2, 6, 9, 10, 18, 19, 25],
    "travel":            [2, 6, 9, 18, 19, 25],
    "surgery":           [18, 19, 23, 24, 25],
    "property_purchase": [2, 6, 9, 18, 19, 25],
    "litigation":        [],
    "important_meeting": [2, 6, 9, 10, 18, 19, 25],
}

# ============================================================
# Vedic — Tithi (Lunar Day) Constants
# Source: Muhurta Chintamani Ch. 3; BPHS Ch. 95
# ============================================================

TITHIS: List[Dict] = [
    {"num": 1,  "name": "Pratipada",   "cn": "第一日",  "paksha": "shukla", "nature": "mixed"},
    {"num": 2,  "name": "Dwitiya",     "cn": "第二日",  "paksha": "shukla", "nature": "benefic"},
    {"num": 3,  "name": "Tritiya",     "cn": "第三日",  "paksha": "shukla", "nature": "benefic"},
    {"num": 4,  "name": "Chaturthi",   "cn": "第四日",  "paksha": "shukla", "nature": "malefic"},
    {"num": 5,  "name": "Panchami",    "cn": "第五日",  "paksha": "shukla", "nature": "benefic"},
    {"num": 6,  "name": "Shashthi",    "cn": "第六日",  "paksha": "shukla", "nature": "mixed"},
    {"num": 7,  "name": "Saptami",     "cn": "第七日",  "paksha": "shukla", "nature": "benefic"},
    {"num": 8,  "name": "Ashtami",     "cn": "第八日",  "paksha": "shukla", "nature": "mixed"},
    {"num": 9,  "name": "Navami",      "cn": "第九日",  "paksha": "shukla", "nature": "malefic"},
    {"num": 10, "name": "Dashami",     "cn": "第十日",  "paksha": "shukla", "nature": "benefic"},
    {"num": 11, "name": "Ekadashi",    "cn": "第十一日","paksha": "shukla", "nature": "benefic"},
    {"num": 12, "name": "Dwadashi",    "cn": "第十二日","paksha": "shukla", "nature": "benefic"},
    {"num": 13, "name": "Trayodashi",  "cn": "第十三日","paksha": "shukla", "nature": "benefic"},
    {"num": 14, "name": "Chaturdashi", "cn": "第十四日","paksha": "shukla", "nature": "malefic"},
    {"num": 15, "name": "Purnima",     "cn": "滿月",    "paksha": "shukla", "nature": "benefic"},
    {"num": 16, "name": "Pratipada",   "cn": "第一日",  "paksha": "krishna","nature": "mixed"},
    {"num": 17, "name": "Dwitiya",     "cn": "第二日",  "paksha": "krishna","nature": "benefic"},
    {"num": 18, "name": "Tritiya",     "cn": "第三日",  "paksha": "krishna","nature": "benefic"},
    {"num": 19, "name": "Chaturthi",   "cn": "第四日",  "paksha": "krishna","nature": "malefic"},
    {"num": 20, "name": "Panchami",    "cn": "第五日",  "paksha": "krishna","nature": "benefic"},
    {"num": 21, "name": "Shashthi",    "cn": "第六日",  "paksha": "krishna","nature": "mixed"},
    {"num": 22, "name": "Saptami",     "cn": "第七日",  "paksha": "krishna","nature": "benefic"},
    {"num": 23, "name": "Ashtami",     "cn": "第八日",  "paksha": "krishna","nature": "mixed"},
    {"num": 24, "name": "Navami",      "cn": "第九日",  "paksha": "krishna","nature": "malefic"},
    {"num": 25, "name": "Dashami",     "cn": "第十日",  "paksha": "krishna","nature": "benefic"},
    {"num": 26, "name": "Ekadashi",    "cn": "第十一日","paksha": "krishna","nature": "benefic"},
    {"num": 27, "name": "Dwadashi",    "cn": "第十二日","paksha": "krishna","nature": "benefic"},
    {"num": 28, "name": "Trayodashi",  "cn": "第十三日","paksha": "krishna","nature": "benefic"},
    {"num": 29, "name": "Chaturdashi", "cn": "第十四日","paksha": "krishna","nature": "malefic"},
    {"num": 30, "name": "Amavasya",    "cn": "新月",    "paksha": "krishna","nature": "malefic"},
]

# Tithis good for activities (tithi number 1-30)
TITHI_GOOD_FOR: Dict[str, List[int]] = {
    "marriage":          [2, 3, 5, 7, 10, 11, 12, 13, 15],
    "business_opening":  [2, 3, 5, 7, 10, 11, 12, 13],
    "contract_signing":  [2, 3, 7, 10, 11, 12, 13],
    "relocation":        [2, 3, 5, 7, 10, 11, 12, 13],
    "travel":            [2, 3, 5, 7, 10, 11, 12, 13],
    "surgery":           [5, 7, 10, 11, 12, 13],
    "property_purchase": [2, 3, 5, 7, 10, 11, 12, 13],
    "litigation":        [4, 9, 14, 24, 29],
    "important_meeting": [2, 3, 5, 7, 10, 11, 12, 13],
}

TITHI_AVOID_FOR: Dict[str, List[int]] = {
    "marriage":          [4, 9, 14, 15, 19, 24, 29, 30],
    "business_opening":  [4, 9, 14, 19, 24, 29, 30],
    "contract_signing":  [4, 9, 14, 19, 24, 29, 30],
    "relocation":        [4, 9, 14, 19, 24, 29, 30],
    "travel":            [4, 9, 14, 19, 24, 29, 30],
    "surgery":           [4, 9, 14, 15, 19, 24, 29, 30],
    "property_purchase": [4, 9, 14, 19, 24, 29, 30],
    "litigation":        [1, 2, 3, 15, 30],
    "important_meeting": [4, 9, 14, 19, 24, 29, 30],
}

# ============================================================
# Vedic — Vara (Weekday) Constants
# Source: Muhurta Chintamani Ch. 1
# ============================================================

VARA_NAMES: List[Dict] = [
    {"num": 0, "name": "Ravivara",   "planet": "Sun",     "cn": "日曜日（週日）", "nature": "mixed"},
    {"num": 1, "name": "Somavara",   "planet": "Moon",    "cn": "月曜日（週一）", "nature": "benefic"},
    {"num": 2, "name": "Mangalavara","planet": "Mars",    "cn": "火曜日（週二）", "nature": "malefic"},
    {"num": 3, "name": "Budhavara",  "planet": "Mercury", "cn": "水曜日（週三）", "nature": "benefic"},
    {"num": 4, "name": "Guruvara",   "planet": "Jupiter", "cn": "木曜日（週四）", "nature": "benefic"},
    {"num": 5, "name": "Shukravara", "planet": "Venus",   "cn": "金曜日（週五）", "nature": "benefic"},
    {"num": 6, "name": "Shanivara",  "planet": "Saturn",  "cn": "土曜日（週六）", "nature": "malefic"},
]

VARA_GOOD_FOR: Dict[str, List[int]] = {
    "marriage":          [0, 1, 3, 4, 5],
    "business_opening":  [1, 3, 4, 5],
    "contract_signing":  [3, 4, 5],
    "relocation":        [1, 3, 4, 5],
    "travel":            [0, 1, 3, 4, 5],
    "surgery":           [0, 2, 6],   # Sun, Mars, Saturn for surgery
    "property_purchase": [1, 3, 4, 5],
    "litigation":        [0, 2, 6],
    "important_meeting": [1, 3, 4, 5],
}

VARA_AVOID_FOR: Dict[str, List[int]] = {
    "marriage":          [2, 6],
    "business_opening":  [2, 6],
    "contract_signing":  [2, 6],
    "relocation":        [2, 6],
    "travel":            [2, 6],
    "surgery":           [1, 4, 5],
    "property_purchase": [2, 6],
    "litigation":        [1, 4, 5],
    "important_meeting": [2, 6],
}

# ============================================================
# Vedic — Yoga (Sun+Moon combinations, 27 yogas)
# Source: Muhurta Chintamani Ch. 4; Kalaprakashika
# ============================================================

YOGAS: List[Dict] = [
    {"num": 1,  "name": "Vishkambha",  "cn": "毘首羯磨", "nature": "malefic"},
    {"num": 2,  "name": "Priti",       "cn": "愛",        "nature": "benefic"},
    {"num": 3,  "name": "Ayushman",    "cn": "壽",        "nature": "benefic"},
    {"num": 4,  "name": "Saubhagya",   "cn": "幸運",      "nature": "benefic"},
    {"num": 5,  "name": "Shobhana",    "cn": "莊嚴",      "nature": "benefic"},
    {"num": 6,  "name": "Atiganda",    "cn": "大障",      "nature": "malefic"},
    {"num": 7,  "name": "Sukarman",    "cn": "善業",      "nature": "benefic"},
    {"num": 8,  "name": "Dhriti",      "cn": "持",        "nature": "benefic"},
    {"num": 9,  "name": "Shula",       "cn": "戈",        "nature": "malefic"},
    {"num": 10, "name": "Ganda",       "cn": "障",        "nature": "malefic"},
    {"num": 11, "name": "Vriddhi",     "cn": "增益",      "nature": "benefic"},
    {"num": 12, "name": "Dhruva",      "cn": "固定",      "nature": "benefic"},
    {"num": 13, "name": "Vyaghata",    "cn": "虎",        "nature": "malefic"},
    {"num": 14, "name": "Harshana",    "cn": "喜悅",      "nature": "benefic"},
    {"num": 15, "name": "Vajra",       "cn": "金剛",      "nature": "mixed"},
    {"num": 16, "name": "Siddhi",      "cn": "成就",      "nature": "benefic"},
    {"num": 17, "name": "Vyatipata",   "cn": "災厄",      "nature": "malefic"},
    {"num": 18, "name": "Variyan",     "cn": "優越",      "nature": "benefic"},
    {"num": 19, "name": "Parigha",     "cn": "障礙",      "nature": "malefic"},
    {"num": 20, "name": "Shiva",       "cn": "吉祥",      "nature": "benefic"},
    {"num": 21, "name": "Siddha",      "cn": "成就",      "nature": "benefic"},
    {"num": 22, "name": "Sadhya",      "cn": "成就",      "nature": "benefic"},
    {"num": 23, "name": "Shubha",      "cn": "吉",        "nature": "benefic"},
    {"num": 24, "name": "Shukla",      "cn": "白",        "nature": "benefic"},
    {"num": 25, "name": "Brahma",      "cn": "梵天",      "nature": "benefic"},
    {"num": 26, "name": "Indra",       "cn": "因陀羅",    "nature": "benefic"},
    {"num": 27, "name": "Vaidhriti",   "cn": "無力",      "nature": "malefic"},
]

INAUSPICIOUS_YOGAS: List[int] = [1, 6, 9, 10, 13, 17, 19, 27]

# ============================================================
# Vedic — Karana (Half Tithi, 11 types)
# Source: Muhurta Chintamani Ch. 5
# ============================================================

KARANAS: List[Dict] = [
    # Movable Karanas (repeat 8 times through the month)
    {"num": 1, "name": "Bava",      "cn": "寶",   "nature": "benefic",  "movable": True},
    {"num": 2, "name": "Balava",    "cn": "吉",   "nature": "benefic",  "movable": True},
    {"num": 3, "name": "Kaulava",   "cn": "和",   "nature": "benefic",  "movable": True},
    {"num": 4, "name": "Taitila",   "cn": "穩",   "nature": "benefic",  "movable": True},
    {"num": 5, "name": "Garaja",    "cn": "象",   "nature": "benefic",  "movable": True},
    {"num": 6, "name": "Vanija",    "cn": "商",   "nature": "benefic",  "movable": True},
    {"num": 7, "name": "Vishti",    "cn": "毒刃", "nature": "malefic",  "movable": True},
    # Fixed Karanas (appear once each)
    {"num": 8, "name": "Shakuni",   "cn": "骰",   "nature": "malefic",  "movable": False},
    {"num": 9, "name": "Chatushpada","cn": "四足", "nature": "mixed",    "movable": False},
    {"num": 10,"name": "Naga",      "cn": "蛇",   "nature": "malefic",  "movable": False},
    {"num": 11,"name": "Kimstughna","cn": "虎",   "nature": "benefic",  "movable": False},
]

# Vishti Karana (Bhadra) is the most malefic — avoid for ALL activities
VISHTI_KARANA_NAME: str = "Vishti"

# ============================================================
# Vedic — Rashis (Sidereal Zodiac)
# ============================================================

VEDIC_RASHIS: List[Dict] = [
    {"num": 1,  "name": "Mesha",      "cn": "牡羊（白羊）", "ruler": "Mars",    "nature": "movable",  "element": "fire"},
    {"num": 2,  "name": "Vrishabha",  "cn": "金牛",         "ruler": "Venus",   "nature": "fixed",    "element": "earth"},
    {"num": 3,  "name": "Mithuna",    "cn": "雙子",         "ruler": "Mercury", "nature": "dual",     "element": "air"},
    {"num": 4,  "name": "Karka",      "cn": "巨蟹",         "ruler": "Moon",    "nature": "movable",  "element": "water"},
    {"num": 5,  "name": "Simha",      "cn": "獅子",         "ruler": "Sun",     "nature": "fixed",    "element": "fire"},
    {"num": 6,  "name": "Kanya",      "cn": "處女",         "ruler": "Mercury", "nature": "dual",     "element": "earth"},
    {"num": 7,  "name": "Tula",       "cn": "天秤",         "ruler": "Venus",   "nature": "movable",  "element": "air"},
    {"num": 8,  "name": "Vrishchika", "cn": "天蠍",         "ruler": "Mars",    "nature": "fixed",    "element": "water"},
    {"num": 9,  "name": "Dhanu",      "cn": "射手",         "ruler": "Jupiter", "nature": "dual",     "element": "fire"},
    {"num": 10, "name": "Makara",     "cn": "摩羯",         "ruler": "Saturn",  "nature": "movable",  "element": "earth"},
    {"num": 11, "name": "Kumbha",     "cn": "水瓶",         "ruler": "Saturn",  "nature": "fixed",    "element": "air"},
    {"num": 12, "name": "Meena",      "cn": "雙魚",         "ruler": "Jupiter", "nature": "dual",     "element": "water"},
]

# Vedic Lagna quality for activities
# Lagna signs that are auspicious/inauspicious for each activity
LAGNA_GOOD_FOR: Dict[str, List[int]] = {
    # sign index 0-11
    "marriage":          [1, 3, 4, 6, 7, 11],   # Taurus, Cancer, Leo, Libra, Scorpio, Pisces
    "business_opening":  [0, 2, 4, 5, 8, 10],
    "contract_signing":  [2, 3, 5, 6, 8, 10, 11],
    "relocation":        [0, 1, 3, 6, 9, 11],
    "travel":            [0, 2, 3, 5, 8, 9],
    "surgery":           [0, 2, 4, 5, 7, 9],
    "property_purchase": [1, 3, 4, 6, 9, 11],
    "litigation":        [0, 4, 7, 10],
    "important_meeting": [2, 3, 5, 6, 9, 11],
}

LAGNA_AVOID_FOR: Dict[str, List[int]] = {
    "marriage":          [0, 2, 5, 8, 9, 10],  # Aries, Gemini, Virgo, Sagittarius, Capricorn, Aquarius
    "business_opening":  [3, 6, 7, 11],
    "contract_signing":  [0, 4, 7],
    "relocation":        [2, 4, 5, 7, 10],
    "travel":            [1, 6, 7, 10, 11],
    "surgery":           [1, 3, 6, 8, 10, 11],
    "property_purchase": [2, 5, 7, 10],
    "litigation":        [1, 3, 6, 9, 11],
    "important_meeting": [0, 4, 7, 10],
    "general":           [],
}

# ============================================================
# Vedic — Muhurta Activity Types
# Source: Muhurta Chintamani; Kalaprakashika
# ============================================================

VEDIC_ACTIVITY_TYPES: Dict[str, Dict] = {
    "marriage": {
        "en": "Vivaha (Marriage)",
        "cn": "婚姻（Vivaha）",
        "special_notes_en": (
            "Vivaha Muhurta is the most elaborate and sacred in Vedic tradition. "
            "Requirements: Moon should be in a benefic Nakshatra (Rohini, Mrigashira, Magha, Uttara Phalguni, "
            "Hasta, Swati, Anuradha, Mula, Uttara Ashadha, Uttara Bhadrapada, Revati). "
            "Lagna must not be 8th from natal Moon (Janma Rashi). "
            "Avoid Gandanta points (junction of water and fire signs). "
            "Jupiter or Venus must be visible (not combust). "
            "Source: Muhurta Chintamani Ch. 7; BPHS Ch. 97."
        ),
        "special_notes_cn": (
            "婚姻擇日是吠陀傳統中最精細、最神聖的儀式。"
            "要求：月亮應在吉祥的那舍特拉（Rohini、Mrigashira、Magha、Uttara Phalguni、"
            "Hasta、Swati、Anuradha、Mula、Uttara Ashadha、Uttara Bhadrapada、Revati）。"
            "命宮不得是本命月星座的第八宮。"
            "避免甘達塔點（水象與火象星座交界）。"
            "木星或金星必須可見（不受燃燒）。"
            "（《Muhurta Chintamani》第七章；《BPHS》第九十七章）"
        ),
        "lilly_ref": "Muhurta Chintamani Ch. 7; BPHS Ch. 97",
    },
    "business_opening": {
        "en": "Vanijya (Commerce / Opening)",
        "cn": "商業開業（Vanijya）",
        "special_notes_en": "Mercury (Budha) should be strong. Moon waxing. Source: Muhurta Chintamani Ch. 9.",
        "special_notes_cn": "水星（布達）應強健。月亮漸盈。（《Muhurta Chintamani》第九章）",
        "lilly_ref": "Muhurta Chintamani Ch. 9",
    },
    "contract_signing": {
        "en": "Lekha (Writing / Agreement)",
        "cn": "書寫協議（Lekha）",
        "special_notes_en": "Mercury strong and in a benefic house. Source: Muhurta Chintamani Ch. 9.",
        "special_notes_cn": "水星強健且在吉宮。（《Muhurta Chintamani》第九章）",
        "lilly_ref": "Muhurta Chintamani Ch. 9",
    },
    "relocation": {
        "en": "Griha Pravesha (House Entering)",
        "cn": "入宅（Griha Pravesha）",
        "special_notes_en": (
            "Griha Pravesha: Moon should be in Rohini, Mrigashira, Pushya, Uttara Phalguni, Hasta, "
            "Chitra, Swati, Shravana, or Uttara Ashadha. Lagna in a fixed sign is preferred. "
            "Source: Muhurta Chintamani Ch. 8."
        ),
        "special_notes_cn": (
            "入宅：月亮應在 Rohini、Mrigashira、Pushya、Uttara Phalguni、Hasta、"
            "Chitra、Swati、Shravana 或 Uttara Ashadha。命宮最好在固定星座中。"
            "（《Muhurta Chintamani》第八章）"
        ),
        "lilly_ref": "Muhurta Chintamani Ch. 8",
    },
    "travel": {
        "en": "Yatra (Journey / Travel)",
        "cn": "出行（Yatra）",
        "special_notes_en": "Moon should be in Ashwini, Mrigashira, Punarvasu, Pushya, Hasta, Swati, Shravana, or Revati for travel. Source: Muhurta Chintamani Ch. 11.",
        "special_notes_cn": "月亮應在 Ashwini、Mrigashira、Punarvasu、Pushya、Hasta、Swati、Shravana 或 Revati 出行。（《Muhurta Chintamani》第十一章）",
        "lilly_ref": "Muhurta Chintamani Ch. 11",
    },
    "surgery": {
        "en": "Shastra Karma (Medical Surgery)",
        "cn": "手術（Shastra Karma）",
        "special_notes_en": "Moon in Aries, Gemini, Leo, or Sagittarius. Avoid the Nakshatra of the body part. Source: Muhurta Chintamani Ch. 13.",
        "special_notes_cn": "月亮在牡羊、雙子、獅子或射手座。避免手術部位所在的那舍特拉。（《Muhurta Chintamani》第十三章）",
        "lilly_ref": "Muhurta Chintamani Ch. 13",
    },
    "property_purchase": {
        "en": "Griha Kray (Property Purchase)",
        "cn": "購置房產（Griha Kray）",
        "special_notes_en": "4th house strong. Moon in fixed signs. Source: Muhurta Chintamani Ch. 8.",
        "special_notes_cn": "第四宮強健。月亮在固定星座。（《Muhurta Chintamani》第八章）",
        "lilly_ref": "Muhurta Chintamani Ch. 8",
    },
    "litigation": {
        "en": "Vivada (Dispute / Litigation)",
        "cn": "訴訟（Vivada）",
        "special_notes_en": "Choose Mars or Sun hora. Avoid benefic days for conflict. Source: Muhurta Martanda.",
        "special_notes_cn": "選擇火星或太陽時辰。衝突中避免吉星之日。（《Muhurta Martanda》）",
        "lilly_ref": "Muhurta Martanda",
    },
    "important_meeting": {
        "en": "Mitra Milana (Important Meeting)",
        "cn": "重要會見（Mitra Milana）",
        "special_notes_en": "Mercury strong. Moon in benefic Nakshatra. Source: Muhurta Chintamani Ch. 9.",
        "special_notes_cn": "水星強健。月亮在吉祥那舍特拉。（《Muhurta Chintamani》第九章）",
        "lilly_ref": "Muhurta Chintamani Ch. 9",
    },
}

# ============================================================
# Gandanta Points (junction of water/fire signs)
# Source: BPHS Ch. 95; Muhurta Chintamani
# ============================================================

# The last/first degree of water-fire pairs (Pisces-Aries, Cancer-Leo, Scorpio-Sagittarius)
GANDANTA_RANGES: List[Tuple[float, float]] = [
    (356.0, 360.0),  # Last 4° of Pisces (sidereal)
    (0.0, 4.0),      # First 4° of Aries
    (116.0, 120.0),  # Last 4° of Cancer
    (120.0, 124.0),  # First 4° of Leo
    (236.0, 240.0),  # Last 4° of Scorpio
    (240.0, 244.0),  # First 4° of Sagittarius
]

# ============================================================
# Vedic Planet Constants (Sidereal)
# ============================================================

VEDIC_PLANET_IDS: Dict[str, int] = {
    "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3,
    "Mars": 4, "Jupiter": 5, "Saturn": 6, "Rahu": 10, "Ketu": 10,
}

VEDIC_PLANETS: List[str] = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu",
]

VEDIC_PLANET_CN: Dict[str, str] = {
    "Sun": "太陽（蘇利耶）", "Moon": "月亮（錢德拉）",
    "Mercury": "水星（布達）", "Venus": "金星（舒克拉）",
    "Mars": "火星（曼加拉）", "Jupiter": "木星（古魯）",
    "Saturn": "土星（沙尼）", "Rahu": "羅睺", "Ketu": "計都",
}

VEDIC_EXALTATION: Dict[str, int] = {
    "Sun": 0,       # Aries (sidereal)
    "Moon": 1,      # Taurus
    "Mercury": 5,   # Virgo
    "Venus": 11,    # Pisces
    "Mars": 9,      # Capricorn
    "Jupiter": 3,   # Cancer
    "Saturn": 6,    # Libra
    "Rahu": 2,      # Gemini (by tradition)
    "Ketu": 8,      # Sagittarius
}

VEDIC_DEBILITATION: Dict[str, int] = {
    planet: (sign + 6) % 12
    for planet, sign in VEDIC_EXALTATION.items()
}

# Default Ayanamsa (Lahiri)
LAHIRI_AYANAMSA: int = 1   # swe.SIDM_LAHIRI

# ============================================================
# Scoring Constants
# ============================================================

SCORE_WEIGHTS: Dict[str, float] = {
    # Western
    "moon_voc":          -30.0,   # Moon VOC is a strong negative
    "moon_via_combusta": -15.0,   # Moon in Via Combusta
    "malefic_in_key_house": -12.0,
    "benefic_in_key_house": +12.0,
    "moon_applies_benefic": +15.0,
    "moon_applies_malefic": -15.0,
    "planet_dignified":   +8.0,
    "planet_debilitated": -8.0,
    "retrograde_mercury": -10.0,
    "good_planetary_hour": +8.0,
    "bad_planetary_hour":  -8.0,
    "moon_waxing":         +5.0,
    "moon_waning":         -3.0,
    # Vedic
    "good_tithi":          +10.0,
    "bad_tithi":           -10.0,
    "good_vara":           +8.0,
    "bad_vara":            -8.0,
    "good_nakshatra":      +12.0,
    "bad_nakshatra":       -12.0,
    "bad_yoga":            -12.0,
    "vishti_karana":       -20.0,  # Bhadra / Vishti is very malefic
    "good_lagna":          +10.0,
    "bad_lagna":           -10.0,
    "gandanta":            -15.0,
    "jupiter_visible":     +10.0,
    "venus_visible":       +10.0,
}

# Score thresholds
SCORE_EXCELLENT:  float = 40.0
SCORE_GOOD:       float = 20.0
SCORE_NEUTRAL:    float = 0.0
SCORE_POOR:       float = -15.0
