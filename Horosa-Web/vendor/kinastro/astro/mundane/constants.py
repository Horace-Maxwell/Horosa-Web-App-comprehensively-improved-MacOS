"""
astro/mundane/constants.py — Mundane Astrology Constants

Constants for Mundane (World / National) Astrology calculations:
- Planet IDs, symbols, and glyphs
- Ingress seasonal points (Aries / Cancer / Libra / Capricorn)
- Country capitals with coordinates (lat, lon, tz_offset)
- Great Conjunction history and planet pairs
- Eclipse types
- Aspect definitions for Mundane interpretation
- Traditional Mundane house significations
- AI persona for Mundane readings

世俗占星（國家占星 / 世界占星）常數：
- 行星 ID、符號、象形符
- 四大入宮點（牡羊 / 巨蟹 / 天秤 / 摩羯）
- 主要國家首都經緯度
- 木土大合相歷史
- 日月食類型
- 相位定義
- 傳統世俗占星宮位象徵
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Any

import swisseph as swe

# ─────────────────────────────────────────────────────────────────────────────
# Planet IDs (Swiss Ephemeris)  行星 swe ID 對照
# ─────────────────────────────────────────────────────────────────────────────

PLANET_IDS: Dict[str, int] = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
    "Uranus":  swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto":   swe.PLUTO,
}

# Planets included in Mundane charts  世俗占星使用行星
MUNDANE_PLANETS: List[str] = [
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
]

# Western glyph symbols  西方行星符號
PLANET_GLYPHS: Dict[str, str] = {
    "Sun":     "☉",
    "Moon":    "☽",
    "Mercury": "☿",
    "Venus":   "♀",
    "Mars":    "♂",
    "Jupiter": "♃",
    "Saturn":  "♄",
    "Uranus":  "♅",
    "Neptune": "♆",
    "Pluto":   "♇",
}

# Chinese planet names  中文行星名稱
PLANET_NAMES_ZH: Dict[str, str] = {
    "Sun":     "太陽",
    "Moon":    "月亮",
    "Mercury": "水星",
    "Venus":   "金星",
    "Mars":    "火星",
    "Jupiter": "木星",
    "Saturn":  "土星",
    "Uranus":  "天王星",
    "Neptune": "海王星",
    "Pluto":   "冥王星",
}

# ─────────────────────────────────────────────────────────────────────────────
# Zodiac Signs  黃道星座
# ─────────────────────────────────────────────────────────────────────────────

SIGN_NAMES_EN: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_NAMES_ZH: List[str] = [
    "牡羊", "金牛", "雙子", "巨蟹",
    "獅子", "處女", "天秤", "天蠍",
    "射手", "摩羯", "寶瓶", "雙魚",
]

SIGN_GLYPHS: List[str] = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓",
]

SIGN_ELEMENTS: List[str] = [
    "Fire", "Earth", "Air", "Water",
    "Fire", "Earth", "Air", "Water",
    "Fire", "Earth", "Air", "Water",
]

SIGN_MODALITIES: List[str] = [
    "Cardinal", "Fixed", "Mutable",
    "Cardinal", "Fixed", "Mutable",
    "Cardinal", "Fixed", "Mutable",
    "Cardinal", "Fixed", "Mutable",
]

# ─────────────────────────────────────────────────────────────────────────────
# Ingress Types  入宮類型
# ─────────────────────────────────────────────────────────────────────────────

# Tropical longitude of Sun at each ingress  各入宮時太陽黃經
INGRESS_LONGITUDES: Dict[str, float] = {
    "aries":      0.0,    # Spring Equinox 春分（最重要）
    "cancer":    90.0,    # Summer Solstice 夏至
    "libra":    180.0,    # Autumn Equinox 秋分
    "capricorn": 270.0,   # Winter Solstice 冬至
}

INGRESS_NAMES_EN: Dict[str, str] = {
    "aries":      "Aries Ingress (Spring Equinox)",
    "cancer":     "Cancer Ingress (Summer Solstice)",
    "libra":      "Libra Ingress (Autumnal Equinox)",
    "capricorn":  "Capricorn Ingress (Winter Solstice)",
}

INGRESS_NAMES_ZH: Dict[str, str] = {
    "aries":      "牡羊入宮（春分）",
    "cancer":     "巨蟹入宮（夏至）",
    "libra":      "天秤入宮（秋分）",
    "capricorn":  "摩羯入宮（冬至）",
}

INGRESS_ICONS: Dict[str, str] = {
    "aries":     "♈",
    "cancer":    "♋",
    "libra":     "♎",
    "capricorn": "♑",
}

# ─────────────────────────────────────────────────────────────────────────────
# Country/Capital Data  國家首都資料 {country_en: (name_zh, lat, lon, tz)}
# Format: (name_zh, lat, lon, utc_offset)
# ─────────────────────────────────────────────────────────────────────────────

COUNTRY_CAPITALS: Dict[str, Tuple[str, float, float, float]] = {
    # East Asia 東亞
    "China (Beijing)":       ("中國 北京",   39.9042,  116.4074,  8.0),
    "Taiwan (Taipei)":       ("台灣 台北",   25.0330,  121.5654,  8.0),
    "Hong Kong":             ("香港",        22.3193,  114.1694,  8.0),
    "Japan (Tokyo)":         ("日本 東京",   35.6762,  139.6503,  9.0),
    "South Korea (Seoul)":   ("南韓 首爾",   37.5665,  126.9780,  9.0),
    "North Korea (Pyongyang)":("北韓 平壤",  39.0392,  125.7625,  9.0),
    "Mongolia (Ulaanbaatar)":("蒙古 烏蘭巴托",47.8864,  106.9057,  8.0),
    # Southeast Asia 東南亞
    "Vietnam (Hanoi)":       ("越南 河內",   21.0285,  105.8542,  7.0),
    "Thailand (Bangkok)":    ("泰國 曼谷",   13.7563,  100.5018,  7.0),
    "Singapore":             ("新加坡",       1.3521,  103.8198,  8.0),
    "Malaysia (Kuala Lumpur)":("馬來西亞 吉隆坡",3.1390, 101.6869, 8.0),
    "Indonesia (Jakarta)":   ("印尼 雅加達", -6.2088,  106.8456,  7.0),
    "Philippines (Manila)":  ("菲律賓 馬尼拉",14.5995, 120.9842,  8.0),
    "Myanmar (Naypyidaw)":   ("緬甸 奈比多",  19.7633,  96.0785,  6.5),
    "Cambodia (Phnom Penh)": ("柬埔寨 金邊",  11.5564,  104.9282,  7.0),
    # South Asia 南亞
    "India (New Delhi)":     ("印度 新德里",  28.6139,   77.2090,  5.5),
    "Pakistan (Islamabad)":  ("巴基斯坦 伊斯蘭馬巴德",33.6844, 73.0479, 5.0),
    "Bangladesh (Dhaka)":    ("孟加拉 達卡",  23.8103,   90.4125,  6.0),
    "Sri Lanka (Colombo)":   ("斯里蘭卡 可倫坡",6.9271, 79.8612,  5.5),
    "Nepal (Kathmandu)":     ("尼泊爾 加德滿都",27.7172, 85.3240,  5.75),
    # Central/West Asia 中西亞
    "Iran (Tehran)":         ("伊朗 德黑蘭",  35.6892,   51.3890,  3.5),
    "Turkey (Ankara)":       ("土耳其 安卡拉",39.9334,   32.8597,  3.0),
    "Saudi Arabia (Riyadh)": ("沙烏地阿拉伯 利雅德",24.6877, 46.7219, 3.0),
    "Israel (Jerusalem)":    ("以色列 耶路撒冷",31.7683, 35.2137, 2.0),
    "UAE (Abu Dhabi)":       ("阿聯酋 阿布扎比",24.4539, 54.3773, 4.0),
    "Iraq (Baghdad)":        ("伊拉克 巴格達", 33.3128,  44.3615,  3.0),
    "Afghanistan (Kabul)":   ("阿富汗 喀布爾", 34.5553,  69.2075,  4.5),
    # Europe 歐洲
    "United Kingdom (London)": ("英國 倫敦",  51.5074,  -0.1278,  0.0),
    "France (Paris)":          ("法國 巴黎",  48.8566,   2.3522,  1.0),
    "Germany (Berlin)":        ("德國 柏林",  52.5200,  13.4050,  1.0),
    "Russia (Moscow)":         ("俄羅斯 莫斯科",55.7558, 37.6173, 3.0),
    "Italy (Rome)":            ("義大利 羅馬", 41.9028,  12.4964,  1.0),
    "Spain (Madrid)":          ("西班牙 馬德里",40.4168, -3.7038,  1.0),
    "Ukraine (Kyiv)":          ("烏克蘭 基輔", 50.4501,  30.5234,  2.0),
    "Poland (Warsaw)":         ("波蘭 華沙",  52.2297,  21.0122,  1.0),
    "Netherlands (Amsterdam)": ("荷蘭 阿姆斯特丹",52.3676, 4.9041, 1.0),
    "Switzerland (Bern)":      ("瑞士 伯恩",  46.9480,   7.4474,  1.0),
    "Sweden (Stockholm)":      ("瑞典 斯德哥爾摩",59.3293, 18.0686, 1.0),
    "Greece (Athens)":         ("希臘 雅典",  37.9838,  23.7275,  2.0),
    # Americas 美洲
    "USA (Washington DC)":   ("美國 華盛頓特區",38.9072, -77.0369, -5.0),
    "Canada (Ottawa)":       ("加拿大 渥太華",45.4215, -75.6972, -5.0),
    "Mexico (Mexico City)":  ("墨西哥 墨西哥城",19.4326,-99.1332, -6.0),
    "Brazil (Brasilia)":     ("巴西 巴西利亞",-15.7942,-47.8822, -3.0),
    "Argentina (Buenos Aires)":("阿根廷 布宜諾斯艾利斯",-34.6037,-58.3816,-3.0),
    "Colombia (Bogota)":     ("哥倫比亞 波哥大", 4.7110,-74.0721, -5.0),
    # Africa 非洲
    "South Africa (Pretoria)":("南非 比勒陀利亞",-25.7479, 28.2293, 2.0),
    "Nigeria (Abuja)":       ("奈及利亞 阿布加", 9.0579,   7.4951,  1.0),
    "Egypt (Cairo)":         ("埃及 開羅",   30.0444,  31.2357,  2.0),
    "Ethiopia (Addis Ababa)":("衣索比亞 阿迪斯阿貝巴", 9.0300, 38.7400, 3.0),
    # Oceania 大洋洲
    "Australia (Canberra)":  ("澳洲 坎培拉", -35.2809,  149.1300, 10.0),
    "New Zealand (Wellington)":("紐西蘭 惠靈頓",-41.2865, 174.7762, 12.0),
}

# ─────────────────────────────────────────────────────────────────────────────
# Great Conjunction History  木土大合相歷史
# Approximate dates; used for timeline visualisation
# (year, month, day, zodiac_lon, sign_index, notes_zh, notes_en)
# ─────────────────────────────────────────────────────────────────────────────

GREAT_CONJUNCTIONS: List[Dict[str, Any]] = [
    {
        "year": 1802, "month": 7,  "day": 17,
        "longitude": 90.0, "sign_index": 2,  # Gemini
        "notes_zh": "雙子座合相，拿破崙戰爭高峰",
        "notes_en": "Gemini conjunction, peak of Napoleonic Wars",
    },
    {
        "year": 1821, "month": 6,  "day": 19,
        "longitude": 30.0, "sign_index": 1,  # Taurus
        "notes_zh": "金牛座合相，拿破崙去世，民族主義興起",
        "notes_en": "Taurus conjunction, death of Napoleon, rising nationalism",
    },
    {
        "year": 1842, "month": 1,  "day": 26,
        "longitude": 350.0, "sign_index": 11,  # Pisces
        "notes_zh": "雙魚座合相，工業革命與社會改革",
        "notes_en": "Pisces conjunction, Industrial Revolution and social reform",
    },
    {
        "year": 1861, "month": 10, "day": 21,
        "longitude": 180.0, "sign_index": 5,  # Virgo
        "notes_zh": "處女座合相，美國南北戰爭，義大利統一",
        "notes_en": "Virgo conjunction, US Civil War, Italian unification",
    },
    {
        "year": 1881, "month": 4,  "day": 18,
        "longitude": 1.0,   "sign_index": 0,  # Aries
        "notes_zh": "牡羊座合相，帝國主義擴張高峰",
        "notes_en": "Aries conjunction, peak of imperial expansion",
    },
    {
        "year": 1901, "month": 11, "day": 28,
        "longitude": 241.0, "sign_index": 8,  # Sagittarius
        "notes_zh": "射手座合相，維多利亞時代結束，新世紀開端",
        "notes_en": "Sagittarius conjunction, end of Victorian era, new century",
    },
    {
        "year": 1921, "month": 9,  "day": 10,
        "longitude": 157.0, "sign_index": 4,  # Virgo
        "notes_zh": "處女座合相，一戰後秩序重建，共產主義興起",
        "notes_en": "Virgo conjunction, post-WWI order, rise of communism",
    },
    {
        "year": 1940, "month": 8,  "day": 8,
        "longitude": 134.0, "sign_index": 4,  # Leo
        "notes_zh": "獅子座合相（土相元素週期末），二次世界大戰",
        "notes_en": "Leo conjunction (end of Earth triplicity), WWII",
    },
    {
        "year": 1961, "month": 2,  "day": 19,
        "longitude": 300.0, "sign_index": 9,  # Capricorn
        "notes_zh": "摩羯座合相，冷戰高峰，太空競賽",
        "notes_en": "Capricorn conjunction, Cold War peak, Space Race",
    },
    {
        "year": 1981, "month": 1,  "day": 1,
        "longitude": 185.0, "sign_index": 6,  # Libra
        "notes_zh": "天秤座合相，里根時代，蘇聯解體前夕",
        "notes_en": "Libra conjunction, Reagan era, eve of Soviet collapse",
    },
    {
        "year": 2000, "month": 5,  "day": 28,
        "longitude": 63.0,  "sign_index": 1,  # Taurus
        "notes_zh": "金牛座合相（千禧年），網路泡沫，全球化高峰",
        "notes_en": "Taurus conjunction (millennium), dot-com bubble, peak globalisation",
    },
    {
        "year": 2020, "month": 12, "day": 21,
        "longitude": 300.7, "sign_index": 10,  # Aquarius (0.7° into Aquarius)
        "notes_zh": "寶瓶座合相（風象元素新紀元），COVID-19 大流行，數位革命",
        "notes_en": "Aquarius conjunction (new Air triplicity era), COVID-19 pandemic, digital revolution",
    },
    {
        "year": 2040, "month": 11, "day": 2,
        "longitude": 233.0, "sign_index": 7,  # Libra (projected)
        "notes_zh": "天秤座合相（預測），風象時代深化",
        "notes_en": "Libra conjunction (projected), deepening Air era",
    },
    {
        "year": 2060, "month": 4,  "day": 7,
        "longitude": 60.0,  "sign_index": 2,  # Gemini (60–90°)
        "notes_zh": "雙子座合相（預測），風象三合完成",
        "notes_en": "Gemini conjunction (projected), Air triplicity complete",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Eclipse Types  日月食類型
# ─────────────────────────────────────────────────────────────────────────────

ECLIPSE_TYPES: Dict[int, str] = {
    swe.ECL_TOTAL:    "Total",
    swe.ECL_ANNULAR:  "Annular",
    swe.ECL_PARTIAL:  "Partial",
    swe.ECL_ANNULAR_TOTAL: "Hybrid (Annular-Total)",
}

ECLIPSE_TYPES_ZH: Dict[int, str] = {
    swe.ECL_TOTAL:    "全食",
    swe.ECL_ANNULAR:  "環食",
    swe.ECL_PARTIAL:  "偏食",
    swe.ECL_ANNULAR_TOTAL: "全環食（混合食）",
}

# ─────────────────────────────────────────────────────────────────────────────
# Aspects  相位定義
# ─────────────────────────────────────────────────────────────────────────────

MUNDANE_ASPECTS: List[Dict[str, Any]] = [
    {"name": "Conjunction",  "name_zh": "合相",  "angle": 0.0,   "orb": 8.0,  "color": "#FFD700", "nature": "neutral"},
    {"name": "Sextile",      "name_zh": "六合",  "angle": 60.0,  "orb": 6.0,  "color": "#4169E1", "nature": "harmonious"},
    {"name": "Square",       "name_zh": "刑相",  "angle": 90.0,  "orb": 8.0,  "color": "#FF4500", "nature": "tense"},
    {"name": "Trine",        "name_zh": "三合",  "angle": 120.0, "orb": 8.0,  "color": "#00AA00", "nature": "harmonious"},
    {"name": "Opposition",   "name_zh": "對相",  "angle": 180.0, "orb": 8.0,  "color": "#FF0000", "nature": "tense"},
    {"name": "Quincunx",     "name_zh": "補相",  "angle": 150.0, "orb": 3.0,  "color": "#9370DB", "nature": "adjusting"},
    {"name": "Semi-square",  "name_zh": "半刑",  "angle": 45.0,  "orb": 2.0,  "color": "#FF6347", "nature": "tense"},
    {"name": "Sesquiquadrate","name_zh": "倍半刑","angle": 135.0, "orb": 2.0,  "color": "#FF8C00", "nature": "tense"},
]

# ─────────────────────────────────────────────────────────────────────────────
# Traditional Mundane House Significations  傳統世俗占星宮位象徵
# Sources: Lilly "Christian Astrology", Campion "Book of World Horoscopes"
# ─────────────────────────────────────────────────────────────────────────────

MUNDANE_HOUSES: Dict[int, Dict[str, str]] = {
    1:  {"en": "The people, general conditions of the country, physical health of nation",
         "zh": "人民、國家整體狀況、民族健康"},
    2:  {"en": "National wealth, treasury, trade, financial resources, banks",
         "zh": "國家財富、國庫、貿易、金融資源、銀行"},
    3:  {"en": "Communication, transport, neighboring countries, media, education",
         "zh": "通訊、交通、鄰國、媒體、教育"},
    4:  {"en": "Land, agriculture, opposition party, housing, natural resources",
         "zh": "土地、農業、在野黨、房地產、自然資源"},
    5:  {"en": "Speculation, entertainment, children, birthrate, ambassadors",
         "zh": "投機、娛樂、兒童、出生率、大使"},
    6:  {"en": "Public health, labour, army rank and file, civil service, food supply",
         "zh": "公共衛生、勞工、軍隊士兵、公務員、糧食供應"},
    7:  {"en": "Foreign relations, open enemies, war, treaties, allies",
         "zh": "外交關係、公開敵人、戰爭、條約、盟友"},
    8:  {"en": "Death rate, taxation, national debt, losses from war, legacies",
         "zh": "死亡率、稅收、國家債務、戰爭損失、遺產"},
    9:  {"en": "Religion, law, philosophy, long-distance travel, higher education, foreign trade",
         "zh": "宗教、法律、哲學、遠途旅行、高等教育、對外貿易"},
    10: {"en": "Government, ruler, prime minister, national reputation, administration",
         "zh": "政府、統治者、首相、國家聲譽、行政機構"},
    11: {"en": "Parliament, allies of government, national hopes, local government",
         "zh": "議會、政府盟友、國家希望、地方政府"},
    12: {"en": "Prisons, hospitals, hidden enemies, espionage, secret societies",
         "zh": "監獄、醫院、隱藏敵人、間諜活動、秘密組織"},
}

# ─────────────────────────────────────────────────────────────────────────────
# Outer Planet Mundane Themes  外行星世俗象徵
# ─────────────────────────────────────────────────────────────────────────────

OUTER_PLANET_THEMES: Dict[str, Dict[str, str]] = {
    "Jupiter": {
        "en": "Expansion, prosperity, religion, law, international trade, abundance",
        "zh": "擴張、繁榮、宗教、法律、國際貿易、豐裕",
    },
    "Saturn": {
        "en": "Restriction, government authority, old institutions, debt, famine, death",
        "zh": "限制、政府權威、舊制度、債務、饑荒、死亡",
    },
    "Uranus": {
        "en": "Revolution, technology, sudden upheaval, democracy, electricity",
        "zh": "革命、科技、突然動盪、民主、電力",
    },
    "Neptune": {
        "en": "Dissolution, spirituality, mass delusion, oil, epidemics, socialism",
        "zh": "消解、靈性、集體幻象、石油、瘟疫、社會主義",
    },
    "Pluto": {
        "en": "Transformation, mass power, plutocracy, nuclear power, organised crime",
        "zh": "轉化、群眾力量、財閥政治、核能、有組織犯罪",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# AI Mundane Persona (欽天監星官)
# Used to populate the AI system prompt for Mundane readings
# ─────────────────────────────────────────────────────────────────────────────

MUNDANE_AI_PERSONA_ZH = (
    "你是古代欽天監星官，精通中西 Mundane 占星傳統。"
    "以宏觀、歷史視野給出國家與時代運勢解讀。"
    "融合西方入宮圖、大合相傳統與中國天象紀事，語言莊重而富有詩意，"
    "引用古籍（如《史記·天官書》、《乙巳占》、《開元占經》），"
    "並結合現代地緣政治視角分析當前星象對世界的影響。"
)

MUNDANE_AI_PERSONA_EN = (
    "You are an ancient celestial official of the Imperial Astronomical Bureau (欽天監), "
    "versed in both Western Mundane and Classical Chinese sky-omen traditions. "
    "Offer national and epochal destiny readings with a grand historical perspective. "
    "Blend Western ingress chart analysis, great conjunction cycles, and Chinese astronomical records. "
    "Your language is solemn and poetic, citing classical sources (Shiji Tianguanshu, Yisi Zhan, "
    "Kaiyuan Zhanjing) while incorporating modern geopolitical insight."
)

# ─────────────────────────────────────────────────────────────────────────────
# Element / Triplicity Cycle for Great Conjunctions
# Each element cycle lasts ~200 years (10 conjunctions × ~20 years)
# ─────────────────────────────────────────────────────────────────────────────

ELEMENT_CYCLE_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    "Fire": {
        "en": "Fire Triplicity (Aries/Leo/Sagittarius): Age of ideology, religion, exploration",
        "zh": "火象三角（牡羊/獅子/射手）：意識形態、宗教、探索的時代",
    },
    "Earth": {
        "en": "Earth Triplicity (Taurus/Virgo/Capricorn): Age of materialism, industry, empire",
        "zh": "土象三角（金牛/處女/摩羯）：物質主義、工業、帝國的時代",
    },
    "Air": {
        "en": "Air Triplicity (Gemini/Libra/Aquarius): Age of information, democracy, technology",
        "zh": "風象三角（雙子/天秤/寶瓶）：資訊、民主、科技的時代（2020年起）",
    },
    "Water": {
        "en": "Water Triplicity (Cancer/Scorpio/Pisces): Age of emotion, spirituality, dissolution",
        "zh": "水象三角（巨蟹/天蠍/雙魚）：情感、靈性、消解的時代",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Colour Palette for Mundane UI  世俗占星 UI 色彩
# ─────────────────────────────────────────────────────────────────────────────

MUNDANE_COLORS = {
    "bg_dark":      "#0a0e1a",     # Deep space dark background
    "bg_card":      "#0d1428",     # Card background
    "accent_gold":  "#C8A951",     # Imperial gold
    "accent_blue":  "#1B4F8A",     # Deep navy
    "accent_indigo":"#3D2B8A",     # Cosmic indigo
    "text_primary": "#E8D8A0",     # Warm parchment text
    "text_muted":   "#7B8DB0",     # Muted bluish grey
    "border":       "#2A3A5A",     # Subtle border
    "fire_red":     "#C94B2A",     # Fire signs
    "earth_brown":  "#8B6333",     # Earth signs
    "air_cyan":     "#2A8B8B",     # Air signs
    "water_blue":   "#2A4A8B",     # Water signs
}
