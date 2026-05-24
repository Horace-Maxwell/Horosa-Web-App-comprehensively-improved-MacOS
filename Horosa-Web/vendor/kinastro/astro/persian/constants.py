"""
astro/persian/constants.py — 波斯薩珊高階占星常量庫

Advanced Sassanian / Persian Astrology Constants
涵蓋 Firdaria、埃及界、三分法、多德卡特摩里亞、Dorotheus 解讀等

Primary Sources:
- Dorotheus of Sidon, "Carmen Astrologicum" (1st century CE, Pahlavi tr.)
- Ptolemy, "Tetrabiblos" (2nd century CE)
- Vettius Valens, "Anthology" (2nd century CE)
- Abu Ma'shar, "Introductorium in Astronomiam" (9th century CE)
- Masha'allah ibn Athari, "On Nativities" (8th century CE)
"""

from typing import Dict, List, Tuple

# ═══════════════════════════════════════════════════════════════
# 基本命名表 (Basic Naming Tables)
# ═══════════════════════════════════════════════════════════════

PLANET_NAMES_CN: Dict[str, str] = {
    "Sun":     "太陽",
    "Moon":    "月亮",
    "Mercury": "水星",
    "Venus":   "金星",
    "Mars":    "火星",
    "Jupiter": "木星",
    "Saturn":  "土星",
}

PLANET_GLYPHS: Dict[str, str] = {
    "Sun":     "☉",
    "Moon":    "☽",
    "Mercury": "☿",
    "Venus":   "♀",
    "Mars":    "♂",
    "Jupiter": "♃",
    "Saturn":  "♄",
}

ZODIAC_SIGNS: List[Tuple[str, str, str, str, str]] = [
    # (English, Glyph, Chinese, Element, Quality)
    ("Aries",        "♈", "白羊座", "Fire",  "Cardinal"),
    ("Taurus",       "♉", "金牛座", "Earth", "Fixed"),
    ("Gemini",       "♊", "雙子座", "Air",   "Mutable"),
    ("Cancer",       "♋", "巨蟹座", "Water", "Cardinal"),
    ("Leo",          "♌", "獅子座", "Fire",  "Fixed"),
    ("Virgo",        "♍", "處女座", "Earth", "Mutable"),
    ("Libra",        "♎", "天秤座", "Air",   "Cardinal"),
    ("Scorpio",      "♏", "天蠍座", "Water", "Fixed"),
    ("Sagittarius",  "♐", "射手座", "Fire",  "Mutable"),
    ("Capricorn",    "♑", "摩羯座", "Earth", "Cardinal"),
    ("Aquarius",     "♒", "水瓶座", "Air",   "Fixed"),
    ("Pisces",       "♓", "雙魚座", "Water", "Mutable"),
]

# ═══════════════════════════════════════════════════════════════
# Firdaria 生命週期 (Correct Traditional Values)
# ═══════════════════════════════════════════════════════════════
# Source: Abu Ma'shar "Introductorium" IV, Masha'allah "On Nativities"
# Total cycle = 75 years

FIRDARIA_YEARS: Dict[str, int] = {
    "Sun":     10,
    "Venus":    8,
    "Mercury": 13,
    "Moon":     9,
    "Saturn":  11,
    "Jupiter": 12,
    "Mars":     7,
    # Node periods (optional, traditional includes)
    "North Node": 3,
    "South Node": 2,
}

# Day chart order (Sect of the Day / 日間盤順序)
# Sun leads, followed by Venus, Mercury, Moon, Saturn, Jupiter, Mars
FIRDARIA_DAY_ORDER: List[str] = [
    "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars",
    "North Node", "South Node",
]

# Night chart order (Sect of the Night / 夜間盤順序)
# Moon leads, followed by Saturn, Jupiter, Mars, Sun, Venus, Mercury
FIRDARIA_NIGHT_ORDER: List[str] = [
    "Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury",
    "South Node", "North Node",
]

# Sub-period planets (same 7 planets rotate from major lord)
FIRDARIA_SUBPERIOD_PLANETS: List[str] = [
    "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars",
]

# ═══════════════════════════════════════════════════════════════
# 行星尊嚴規則 (Essential Dignities)
# ═══════════════════════════════════════════════════════════════

# Domicile (廟) — Traditional 7-planet rulers
DOMICILE: Dict[str, str] = {
    "Aries": "Mars",        "Taurus": "Venus",   "Gemini": "Mercury",
    "Cancer": "Moon",       "Leo": "Sun",         "Virgo": "Mercury",
    "Libra": "Venus",       "Scorpio": "Mars",    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",  "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# Exaltation (旺)
EXALTATION: Dict[str, str] = {
    "Aries": "Sun",       "Taurus": "Moon",    "Cancer": "Jupiter",
    "Virgo": "Mercury",   "Libra": "Saturn",   "Capricorn": "Mars",
    "Pisces": "Venus",
}

# Detriment (陷) — opposite of domicile
DETRIMENT: Dict[str, str] = {
    "Aries": "Venus",       "Taurus": "Mars",    "Gemini": "Jupiter",
    "Cancer": "Saturn",     "Leo": "Saturn",      "Virgo": "Jupiter",
    "Libra": "Mars",        "Scorpio": "Venus",   "Sagittarius": "Mercury",
    "Capricorn": "Moon",    "Aquarius": "Sun",    "Pisces": "Mercury",
}

# Fall (弱) — opposite of exaltation
FALL: Dict[str, str] = {
    "Libra": "Sun",       "Scorpio": "Moon",   "Capricorn": "Jupiter",
    "Pisces": "Mercury",  "Aries": "Saturn",   "Cancer": "Mars",
    "Virgo": "Venus",
}

# ═══════════════════════════════════════════════════════════════
# 三分守護星 (Triplicity Lords)
# ═══════════════════════════════════════════════════════════════
# Source: Dorotheus, "Carmen Astrologicum" Book I
# Each triplicity has three lords: Day, Night, Participating

TRIPLICITY_LORDS: Dict[str, Tuple[str, str, str]] = {
    # (Day Lord, Night Lord, Participating Lord)
    "Fire":  ("Sun",    "Jupiter", "Saturn"),   # Aries, Leo, Sagittarius
    "Earth": ("Venus",  "Moon",    "Mars"),     # Taurus, Virgo, Capricorn
    "Air":   ("Saturn", "Mercury", "Jupiter"),  # Gemini, Libra, Aquarius
    "Water": ("Venus",  "Mars",    "Moon"),     # Cancer, Scorpio, Pisces
}

ELEMENT_OF_SIGN: Dict[str, str] = {
    "Aries": "Fire",  "Leo": "Fire",  "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air",   "Libra": "Air",   "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}

# ═══════════════════════════════════════════════════════════════
# 埃及界 (Egyptian Bounds / Terms)
# ═══════════════════════════════════════════════════════════════
# Source: Ptolemy "Tetrabiblos" I.20, matching Dorotheus tradition
# Format: (planet, start_degree, end_degree)  — half-open [start, end)

EGYPTIAN_BOUNDS: Dict[str, List[Tuple[str, int, int]]] = {
    "Aries":       [("Jupiter", 0, 6),  ("Venus", 6, 14),   ("Mercury", 14, 21),
                    ("Mars", 21, 26),   ("Saturn", 26, 30)],
    "Taurus":      [("Venus", 0, 8),    ("Mercury", 8, 15),  ("Jupiter", 15, 22),
                    ("Saturn", 22, 26), ("Mars", 26, 30)],
    "Gemini":      [("Mercury", 0, 7),  ("Jupiter", 7, 14),  ("Venus", 14, 21),
                    ("Mars", 21, 25),   ("Saturn", 25, 30)],
    "Cancer":      [("Mars", 0, 7),     ("Venus", 7, 13),    ("Mercury", 13, 20),
                    ("Jupiter", 20, 27), ("Saturn", 27, 30)],
    "Leo":         [("Jupiter", 0, 6),  ("Venus", 6, 11),    ("Saturn", 11, 18),
                    ("Mercury", 18, 24), ("Mars", 24, 30)],
    "Virgo":       [("Mercury", 0, 7),  ("Venus", 7, 17),    ("Jupiter", 17, 21),
                    ("Mars", 21, 28),   ("Saturn", 28, 30)],
    "Libra":       [("Saturn", 0, 6),   ("Mercury", 6, 14),  ("Jupiter", 14, 21),
                    ("Venus", 21, 28),  ("Mars", 28, 30)],
    "Scorpio":     [("Mars", 0, 7),     ("Venus", 7, 11),    ("Mercury", 11, 19),
                    ("Jupiter", 19, 24), ("Saturn", 24, 30)],
    "Sagittarius": [("Jupiter", 0, 12), ("Venus", 12, 17),   ("Mercury", 17, 21),
                    ("Saturn", 21, 26), ("Mars", 26, 30)],
    "Capricorn":   [("Mercury", 0, 7),  ("Jupiter", 7, 14),  ("Venus", 14, 22),
                    ("Saturn", 22, 26), ("Mars", 26, 30)],
    "Aquarius":    [("Mercury", 0, 7),  ("Venus", 7, 13),    ("Jupiter", 13, 20),
                    ("Mars", 20, 25),   ("Saturn", 25, 30)],
    "Pisces":      [("Venus", 0, 12),   ("Jupiter", 12, 16), ("Mercury", 16, 19),
                    ("Mars", 19, 28),   ("Saturn", 28, 30)],
}

# ═══════════════════════════════════════════════════════════════
# 面 (Decans / Faces) — Chaldean Order
# ═══════════════════════════════════════════════════════════════
# Each sign has 3 decans of 10° each, ruled by planets in Chaldean order
# Chaldean order starts from Mars for Aries 0°

DECAN_RULERS: List[str] = [
    # Starting from Aries 0°, cycling through Chaldean order
    # Mars, Sun, Venus, Mercury, Moon, Saturn, Jupiter — repeating
    "Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter",
    "Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter",
    "Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter",
    "Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter",
    "Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter",
    "Mars", "Sun",
]  # 36 decans total (12 signs × 3)

# ═══════════════════════════════════════════════════════════════
# 波斯敏感點 / 阿拉伯點 (Arabic Parts / Persian Lots)
# ═══════════════════════════════════════════════════════════════
# Format: (name_en, name_cn, name_arabic, day_formula, night_formula)
# Formula: (A, B) means ASC + A - B; reversed for night
# "F" = Fortune (PoF), "S" = Spirit (PoS)

ARABIC_PARTS: List[Tuple[str, str, str, str, str]] = [
    # (name_en, name_cn, name_arabic,
    #  day_formula_desc, night_formula_desc)
    ("Part of Fortune",
     "幸運點 (命運之點)",
     "سهم السعادة",
     "ASC + Moon − Sun",
     "ASC + Sun − Moon"),
    ("Part of Spirit",
     "精神點 (靈魂之點)",
     "سهم الروح",
     "ASC + Sun − Moon",
     "ASC + Moon − Sun"),
    ("Part of Marriage (Venus)",
     "婚姻點 (金星)",
     "سهم الزواج",
     "ASC + Venus − Sun",
     "ASC + Sun − Venus"),
    ("Part of Marriage (Saturn)",
     "婚姻點 (土星)",
     "سهم الزواج (زحل)",
     "ASC + Saturn − Venus",
     "ASC + Venus − Saturn"),
    ("Part of Children",
     "子女點",
     "سهم الأولاد",
     "ASC + Jupiter − Saturn",
     "ASC + Saturn − Jupiter"),
    ("Part of Father",
     "父親點",
     "سهم الأب",
     "ASC + Sun − Saturn",
     "ASC + Saturn − Sun"),
    ("Part of Mother",
     "母親點",
     "سهم الأم",
     "ASC + Moon − Venus",
     "ASC + Venus − Moon"),
    ("Part of Siblings",
     "兄弟點",
     "سهم الإخوة",
     "ASC + Jupiter − Saturn",
     "ASC + Saturn − Jupiter"),
    ("Part of Illness",
     "疾病點",
     "سهم المرض",
     "ASC + Mars − Saturn",
     "ASC + Saturn − Mars"),
    ("Part of Career / Vocation",
     "職業點",
     "سهم العمل",
     "ASC + Mercury − Sun",
     "ASC + Sun − Mercury"),
    ("Part of Travel",
     "旅行點",
     "سهم السفر",
     "ASC + Jupiter − Moon",
     "ASC + Moon − Jupiter"),
    ("Part of Death",
     "死亡點",
     "سهم الموت",
     "ASC + Cusp8 − Moon",
     "ASC + Moon − Cusp8"),
    ("Part of Exaltation",
     "尊貴點",
     "سهم الشرف",
     "ASC + 19Aries − Sun",
     "ASC + Sun − 19Aries"),
    ("Part of Basis",
     "基礎點 (Fortune + Spirit)",
     "سهم الأساس",
     "ASC + PoF − PoS",
     "ASC + PoS − PoF"),
]

# ═══════════════════════════════════════════════════════════════
# 四顆波斯皇家恆星 (Four Persian Royal Stars)
# ═══════════════════════════════════════════════════════════════
# Tropical longitudes for J2000 epoch (approximate)

ROYAL_STARS: Dict[str, Dict] = {
    "Aldebaran": {
        "name_en":     "Aldebaran",
        "name_cn":     "畢宿五",
        "name_pahlavi": "Tascheter",
        "longitude":   69.9,   # ~9°54' Gemini
        "orb":         2.5,
        "guardian":    "Spring Equinox",
        "meaning_en":  "Honor, military success, eloquence; danger of violence if afflicted",
        "meaning_cn":  "榮耀、軍事成就、雄辯；若受克制則有暴力之危",
        "element":     "Fire",
        "planet_nature": "Mars/Mercury",
    },
    "Regulus": {
        "name_en":     "Regulus",
        "name_cn":     "軒轅十四",
        "name_pahlavi": "Vanant",
        "longitude":   149.8,  # ~29°48' Leo (tropical; traditional position ~29°50' Leo)
        "orb":         2.5,
        "guardian":    "Summer Solstice",
        "meaning_en":  "Kingship, honor, fame; swift rise and fall if afflicted",
        "meaning_cn":  "王權、榮耀、聲望；若受克制則大起大落",
        "element":     "Fire",
        "planet_nature": "Mars/Jupiter",
    },
    "Antares": {
        "name_en":     "Antares",
        "name_cn":     "心宿二",
        "name_pahlavi": "Satevis",
        "longitude":   249.7,  # ~9°43' Sagittarius
        "orb":         2.5,
        "guardian":    "Autumn Equinox",
        "meaning_en":  "Courage, tenacity; stubbornness, recklessness if afflicted",
        "meaning_cn":  "勇氣、堅韌；若受克制則頑固魯莽",
        "element":     "Fire",
        "planet_nature": "Mars/Jupiter",
    },
    "Fomalhaut": {
        "name_en":     "Fomalhaut",
        "name_cn":     "北落師門",
        "name_pahlavi": "Hastorang",
        "longitude":   333.9,  # ~3°52' Pisces
        "orb":         2.5,
        "guardian":    "Winter Solstice",
        "meaning_en":  "Idealism, spirituality, poetic gifts; delusion if afflicted",
        "meaning_cn":  "理想主義、靈性、詩才；若受克制則易有幻覺",
        "element":     "Water",
        "planet_nature": "Venus/Mercury",
    },
}

# ═══════════════════════════════════════════════════════════════
# 行星年數 (Planetary Years for Alcocoden)
# ═══════════════════════════════════════════════════════════════
# Source: Ptolemy "Tetrabiblos" IV.10, used for Alcocoden longevity

PLANETARY_MAJOR_YEARS: Dict[str, int] = {
    "Sun":     120,
    "Moon":    108,
    "Mercury": 76,
    "Venus":   82,
    "Mars":    66,
    "Jupiter": 79,
    "Saturn":  57,
}

PLANETARY_MINOR_YEARS: Dict[str, int] = {
    "Sun":     19,
    "Moon":    25,
    "Mercury": 20,
    "Venus":   8,
    "Mars":    15,
    "Jupiter": 12,
    "Saturn":  30,
}

PLANETARY_MIDDLE_YEARS: Dict[str, int] = {
    "Sun":     69,
    "Moon":    66,
    "Mercury": 48,
    "Venus":   45,
    "Mars":    40,
    "Jupiter": 45,
    "Saturn":  43,
}

# ═══════════════════════════════════════════════════════════════
# 整宮制宮位含義 (Whole Sign House Significations)
# ═══════════════════════════════════════════════════════════════

HOUSE_SIGNIFICATIONS: Dict[int, Dict[str, str]] = {
    1:  {"en": "Life, body, character, beginnings",       "cn": "生命、身體、性格、開端"},
    2:  {"en": "Resources, wealth, possessions",          "cn": "資源、財富、財物"},
    3:  {"en": "Siblings, short travel, communication",   "cn": "兄弟、短途旅行、溝通"},
    4:  {"en": "Parents, home, origins, endings",         "cn": "父母、家宅、根源、結局"},
    5:  {"en": "Children, pleasure, creativity, luck",    "cn": "子女、歡愉、創造力、好運"},
    6:  {"en": "Illness, servants, work, animals",        "cn": "疾病、僕人、工作、動物"},
    7:  {"en": "Marriage, partnerships, open enemies",    "cn": "婚姻、合夥、公開之敵"},
    8:  {"en": "Death, inheritance, others' resources",   "cn": "死亡、遺產、他人資源"},
    9:  {"en": "Religion, long travel, philosophy",       "cn": "宗教、長途旅行、哲學"},
    10: {"en": "Career, reputation, authority, honors",   "cn": "事業、聲譽、權威、榮譽"},
    11: {"en": "Friends, benefactors, hopes, groups",     "cn": "友誼、贊助人、希望、群體"},
    12: {"en": "Hidden enemies, imprisonment, isolation", "cn": "隱秘之敵、監禁、孤立"},
}

# ═══════════════════════════════════════════════════════════════
# Dorotheus-style 解讀引擎 (Dorotheus Interpretation Engine)
# ═══════════════════════════════════════════════════════════════
# Inspired by Dorotheus of Sidon, "Carmen Astrologicum" (1st century CE)
# and its Pahlavi translation used in Sassanian Persia.

# General planet nature interpretations
PLANET_NATURE: Dict[str, Dict[str, str]] = {
    "Sun": {
        "quality_en":  "Masculine, diurnal, hot & dry",
        "quality_cn":  "陽性、日間、熱而乾燥",
        "rules_en":    "Vitality, authority, father, kings, gold",
        "rules_cn":    "生命力、權威、父親、國王、黃金",
    },
    "Moon": {
        "quality_en":  "Feminine, nocturnal, cold & moist",
        "quality_cn":  "陰性、夜間、冷而潮濕",
        "rules_en":    "Body, emotions, mother, public, silver",
        "rules_cn":    "身體、情緒、母親、大眾、銀",
    },
    "Mercury": {
        "quality_en":  "Neutral, changeable, cold & dry",
        "quality_cn":  "中性、多變、冷而乾燥",
        "rules_en":    "Intellect, trade, writing, youth, messengers",
        "rules_cn":    "智識、貿易、書寫、青年、信使",
    },
    "Venus": {
        "quality_en":  "Feminine, nocturnal, cold & moist",
        "quality_cn":  "陰性、夜間、冷而潮濕",
        "rules_en":    "Beauty, love, arts, marriage, women",
        "rules_cn":    "美貌、愛情、藝術、婚姻、女性",
    },
    "Mars": {
        "quality_en":  "Masculine, nocturnal, hot & dry",
        "quality_cn":  "陽性、夜間、熱而乾燥",
        "rules_en":    "War, strife, fire, surgery, iron, courage",
        "rules_cn":    "戰爭、紛爭、火、外科、鐵、勇氣",
    },
    "Jupiter": {
        "quality_en":  "Masculine, diurnal, warm & moist",
        "quality_cn":  "陽性、日間、溫而潮濕",
        "rules_en":    "Wisdom, law, religion, wealth, expansion",
        "rules_cn":    "智慧、法律、宗教、財富、擴展",
    },
    "Saturn": {
        "quality_en":  "Masculine, diurnal, cold & dry",
        "quality_cn":  "陽性、日間、冷而乾燥",
        "rules_en":    "Longevity, land, death, restriction, cold",
        "rules_cn":    "長壽、土地、死亡、限制、寒冷",
    },
}

# Dorotheus-style life topic interpretations by house lord
# (lord_of_house, dignity) → interpretation
DOROTHEUS_INTERPRETATIONS: Dict[str, Dict[str, str]] = {
    "longevity": {
        "Sun_dignified_en":    "Strong vitality and long life when the Sun is well-placed. The native is robust and endures hardship with resilience.",
        "Sun_dignified_cn":    "太陽位置良好時，生命力旺盛，壽命較長。命主體格健壯，能忍受艱辛。",
        "Sun_afflicted_en":    "Danger to vitality, fever-related illness; lifespan may be curtailed by the malefics.",
        "Sun_afflicted_cn":    "生命力受威脅，易患發熱類疾病；凶星可能縮短壽命。",
        "Moon_dignified_en":   "Good constitution and reasonable longevity. Immunity is strong especially during youth.",
        "Moon_dignified_cn":   "體質良好，壽命合理。尤其在年輕時期免疫力強健。",
        "Moon_afflicted_en":   "Vulnerability to cold, damp illnesses; chronic weakness if Moon is debilitated.",
        "Moon_afflicted_cn":   "容易患寒濕類疾病；若月亮受損則慢性體弱。",
        "Saturn_dignified_en": "A long but austere life; the native perseveres through difficulties to old age.",
        "Saturn_dignified_cn": "生命悠長但艱苦；命主能克服困難活至老年。",
        "Saturn_afflicted_en": "Possible early hardship; illness of a cold or chronic nature; beware of falls and breaks.",
        "Saturn_afflicted_cn": "可能早期艱辛；寒性或慢性疾病；需防跌落骨折。",
        "Jupiter_dignified_en":"Excellent vitality and natural immunity; Jupiter protects against disease and grants long life.",
        "Jupiter_dignified_cn":"生命力優秀，天然免疫力佳；木星保護免遭疾病，賜予長壽。",
        "Mars_afflicted_en":   "Risk of accident, fever, and violence; lifespan may be shortened by impulsive acts.",
        "Mars_afflicted_cn":   "有事故、發熱、暴力的風險；衝動行事可能縮短壽命。",
        "Venus_dignified_en":  "Pleasant constitution; moderate longevity through careful living.",
        "Venus_dignified_cn":  "體質愉悅；通過謹慎生活可獲中等壽命。",
        "Mercury_dignified_en":"Mental agility contributes to health awareness; good longevity through adaptation.",
        "Mercury_dignified_cn":"心智靈活有助於健康意識；通過適應性獲得良好壽命。",
    },
    "marriage": {
        "Venus_dignified_en":  "Marriage is blessed and harmonious. The partner is beautiful, devoted, and prosperous.",
        "Venus_dignified_cn":  "婚姻幸福美滿。伴侶美麗、忠誠、繁榮。",
        "Venus_afflicted_en":  "Difficulty in marriage; discord, separations, or multiple unions are indicated.",
        "Venus_afflicted_cn":  "婚姻困難；紛爭、分離或多段婚姻有所顯示。",
        "Saturn_in_7th_en":    "Marriage comes late or is burdened by duty and restriction. The partner may be older or austere.",
        "Saturn_in_7th_cn":    "婚姻來遲或被義務和限制所困。伴侶可能年長或嚴肅。",
        "Mars_in_7th_en":      "Passionate but quarrelsome unions; risk of violence or abrupt endings in partnerships.",
        "Mars_in_7th_cn":      "充滿激情但愛爭吵的結合；夥伴關係中有暴力或突然結束的風險。",
        "Jupiter_in_7th_en":   "Marriage to a noble, generous, or learned person. The union brings growth and prosperity.",
        "Jupiter_in_7th_cn":   "與高貴、慷慨或博學之人結婚。此結合帶來成長和繁榮。",
        "Moon_in_7th_en":      "Marriage is influenced by the mother or family. Emotional connections are strong.",
        "Moon_in_7th_cn":      "婚姻受母親或家庭影響。情感連結深厚。",
    },
    "children": {
        "Jupiter_dignified_en": "Blessed with children; offspring are fortunate, noble, and bring honor to the family.",
        "Jupiter_dignified_cn": "有子女之福；後代幸運、高貴，為家庭帶來榮耀。",
        "Saturn_in_5th_en":    "Few children or late parenthood; existing children may face hardship.",
        "Saturn_in_5th_cn":    "子女稀少或晚育；現有子女可能面臨艱辛。",
        "Mars_in_5th_en":      "Children are bold and active but accident-prone; miscarriages possible.",
        "Mars_in_5th_cn":      "子女大膽活躍但易發生事故；可能有流產。",
        "Venus_in_5th_en":     "Loving relationship with children; offspring are artistic and charming.",
        "Venus_in_5th_cn":     "與子女關係親密；後代有藝術氣質且迷人。",
        "Moon_in_5th_en":      "Many children, especially daughters; strong maternal bond.",
        "Moon_in_5th_cn":      "子女眾多，尤其是女兒；母子情深。",
    },
    "career": {
        "Sun_in_10th_en":      "Destined for high position, public recognition, and leadership. The native shines in authority.",
        "Sun_in_10th_cn":      "命中注定高位、公眾認可和領導力。命主在權位上大放光彩。",
        "Saturn_in_10th_en":   "Career in traditional fields: law, government, agriculture, or building. Success comes through perseverance.",
        "Saturn_in_10th_cn":   "職業在傳統領域：法律、政府、農業或建築。通過堅持獲得成功。",
        "Jupiter_in_10th_en":  "Success in religious, philosophical, or judicial fields. The native earns honor and respect.",
        "Jupiter_in_10th_cn":  "在宗教、哲學或司法領域成功。命主贏得榮譽和尊重。",
        "Mars_in_10th_en":     "Military, surgical, or competitive career. Ambition drives swift advancement.",
        "Mars_in_10th_cn":     "軍事、外科或競爭性職業。野心驅動快速晉升。",
        "Venus_in_10th_en":    "Career in arts, beauty, or diplomacy. Charm and grace bring professional success.",
        "Venus_in_10th_cn":    "在藝術、美容或外交領域的職業。魅力和優雅帶來職業成功。",
        "Mercury_in_10th_en":  "Career in communication, commerce, or learning. Versatility and intellect are key assets.",
        "Mercury_in_10th_cn":  "在通訊、商業或學習領域的職業。多才多藝和智識是主要資產。",
        "Moon_in_10th_en":     "Career linked to public, food, or caregiving. Reputation fluctuates with popular opinion.",
        "Moon_in_10th_cn":     "職業與公眾、食物或護理相關。聲譽隨民意起伏。",
    },
    "general": {
        "day_chart_en":        "A diurnal chart strengthens the solar, Saturnine and Jovian planets. The native's public life is more pronounced.",
        "day_chart_cn":        "日間盤加強太陽、土星和木星的行星。命主的公共生活更為突出。",
        "night_chart_en":      "A nocturnal chart strengthens the lunar, Martian and Venereal planets. The native's inner life and intuition are strong.",
        "night_chart_cn":      "夜間盤加強月亮、火星和金星的行星。命主的內心生活和直覺強盛。",
        "many_dignified_en":   "Many planets in dignity indicate a fortunate life, talents easily expressed, and natural alignment with destiny.",
        "many_dignified_cn":   "多顆行星處於尊嚴位置，表示幸運的生命、才能易於表達以及與命運的自然協調。",
        "many_afflicted_en":   "Many planets in detriment or fall indicate obstacles, misdirected energy, and the need for conscious effort to overcome challenges.",
        "many_afflicted_cn":   "多顆行星處於陷或弱位置，表示障礙、能量錯誤導向，需要有意識的努力克服挑戰。",
    },
}

# ═══════════════════════════════════════════════════════════════
# 反射點 / 對射點 (Antiscia & Contra-antiscia)
# ═══════════════════════════════════════════════════════════════
# Antiscia: reflection over the Cancer/Capricorn axis (0° Cancer = 0° Capricorn)
# The antiscion of longitude L = (180° - L) if L < 180°, else (540° - L)
# More precisely: antiscion of L = (180 - L) mod 360  [mirrored over 0° Cancer axis]

# Contra-antiscia: reflection over the Aries/Libra axis
# Contra-antiscion of longitude L = (360 - L) mod 360  [mirrored over 0° Aries axis]

# Pairs of antiscia signs (mirrored over Cancer-Capricorn axis):
ANTISCIA_PAIRS: List[Tuple[str, str]] = [
    ("Aries",       "Virgo"),    # ♈ ↔ ♍  (both are 90° from solstice axis)
    ("Taurus",      "Leo"),      # ♉ ↔ ♌
    ("Gemini",      "Cancer"),   # ♊ ↔ ♋
    ("Libra",       "Pisces"),   # ♎ ↔ ♓
    ("Scorpio",     "Aquarius"), # ♏ ↔ ♒
    ("Sagittarius", "Capricorn"),# ♐ ↔ ♑
]

# ═══════════════════════════════════════════════════════════════
# 波斯占星色彩主題 (Persian Color Palette)
# ═══════════════════════════════════════════════════════════════

PERSIAN_COLORS = {
    "background":      "#0d0d1a",  # Deep night indigo
    "card_bg":         "#1a1a2e",  # Dark navy
    "card_border":     "#8B6914",  # Antique gold
    "accent_gold":     "#D4AF37",  # Royal gold
    "accent_saffron":  "#E67E22",  # Saffron orange
    "accent_turquoise":"#1ABC9C",  # Persian turquoise
    "accent_crimson":  "#C0392B",  # Deep crimson
    "text_primary":    "#F0E6D3",  # Warm parchment
    "text_secondary":  "#B8A88A",  # Faded parchment
    "text_muted":      "#6B5B45",  # Aged text
    "sun_color":       "#F39C12",  # Gold
    "moon_color":      "#BDC3C7",  # Silver
    "mercury_color":   "#27AE60",  # Green
    "venus_color":     "#E91E63",  # Pink/rose
    "mars_color":      "#E74C3C",  # Red
    "jupiter_color":   "#9B59B6",  # Purple
    "saturn_color":    "#607D8B",  # Blue-grey
    "benefic_color":   "#2ECC71",  # Green (benefic)
    "malefic_color":   "#E74C3C",  # Red (malefic)
    "neutral_color":   "#95A5A6",  # Grey (neutral)
    "current_period":  "#F39C12",  # Highlighted period
}

PLANET_COLORS: Dict[str, str] = {
    "Sun":     PERSIAN_COLORS["sun_color"],
    "Moon":    PERSIAN_COLORS["moon_color"],
    "Mercury": PERSIAN_COLORS["mercury_color"],
    "Venus":   PERSIAN_COLORS["venus_color"],
    "Mars":    PERSIAN_COLORS["mars_color"],
    "Jupiter": PERSIAN_COLORS["jupiter_color"],
    "Saturn":  PERSIAN_COLORS["saturn_color"],
}

# ═══════════════════════════════════════════════════════════════
# 行星屬性 (Planet Sect)
# ═══════════════════════════════════════════════════════════════
# Diurnal (日間) planets: Sun, Jupiter, Saturn (when above horizon)
# Nocturnal (夜間) planets: Moon, Venus, Mars (when above horizon)
# Mercury: sect varies by position

DIURNAL_PLANETS = {"Sun", "Jupiter", "Saturn"}
NOCTURNAL_PLANETS = {"Moon", "Venus", "Mars"}
BENEFIC_PLANETS = {"Jupiter", "Venus"}
MALEFIC_PLANETS = {"Saturn", "Mars"}

# Sect joy positions (行星喜悅宮位)
PLANET_SECT_JOY: Dict[str, int] = {
    "Sun":     9,   # 9th house
    "Moon":    3,   # 3rd house
    "Mercury": 1,   # 1st house
    "Venus":   5,   # 5th house
    "Mars":    6,   # 6th house
    "Jupiter": 11,  # 11th house
    "Saturn":  12,  # 12th house
}
