"""
astro/tibetan.py — 西藏占星 / 時輪金剛占星 (Tibetan Kalachakra Astrology)

時輪金剛續 (Kalachakra Tantra) 為藏傳占星的根本古法，
融合印度天文學 (Jyotish)、中國干支體系與苯教本土元素，
形成獨特的藏傳曆算體系 (rTsis / Tsi)。

核心體系包含：
- 藏曆 (Lunisolar Calendar / lo-tho)：陰陽合曆，以六十年循環 (rab-byung) 為週期
- 五行 (ḥByung-ba / Junwa)：木 (Shing)、火 (Me)、土 (Sa)、金 (Lcags)、水 (Chu)
- 十二生肖 (lo-rtags)：鼠 (Byi-ba)、牛 (Glang) 等十二獸
- 九宮 Mewa (sMe-ba dgu)：1-9 九個數字，對應顏色、方位、吉凶
- 八卦 Parkha (sPar-kha brgyad)：八方位，類似易經八卦
- 五力 (Five Forces)：La (魂)、Sok (命)、Lu (身體)、Wangthang (權勢)、Lungta (風馬)
- 九曜 (Graha)：七星 + Rahu (Ra-hu) + Ketu (Khe-ta)
- 二十七宿 (rGyu-skar / Nakshatra)：月亮星宿系統

與蒙古祖爾海 (Zurkhai) 的區別：
- 祖爾海偏重日常擇吉與世俗活動指引，以松巴堪布《德古斯布揚圖》為典
- 藏傳占星以《時輪金剛續》為根本，著重宇宙論、曼荼羅觀想與密續修行指導
- 藏傳占星融入 Mewa 九宮與 Parkha 八卦，並強調五力 (Five Forces) 系統
- 視覺表現以時輪金剛曼荼羅 (Kalachakra Mandala) 為核心圖像

文化聲明：
此計算依循藏傳占星古法，僅供文化學習與參考。
重要決定請諮詢合格的藏傳占星師 (rTsis-pa) 或上師。
"""

import math
import streamlit as st
import swisseph as swe
from dataclasses import dataclass, field
from datetime import date

# ============================================================
# 常量 (Constants) — 十二生肖 (Tibetan Twelve Animals)
# ============================================================

# (index, Tibetan, Chinese, English, element)
TIBETAN_ANIMALS = [
    (0,  "Byi-ba",    "鼠", "Rat",     "Wood"),
    (1,  "Glang",     "牛", "Ox",      "Wood"),
    (2,  "sTag",      "虎", "Tiger",   "Fire"),
    (3,  "Yos",       "兔", "Rabbit",  "Fire"),
    (4,  "ḥBrug",     "龍", "Dragon",  "Earth"),
    (5,  "sBrul",     "蛇", "Snake",   "Earth"),
    (6,  "rTa",       "馬", "Horse",   "Metal"),
    (7,  "Lug",       "羊", "Sheep",   "Metal"),
    (8,  "sPre-hu",   "猴", "Monkey",  "Water"),
    (9,  "Bya",       "鳥", "Bird",    "Water"),
    (10, "Khyi",      "狗", "Dog",     "Earth"),
    (11, "Phag",      "豬", "Pig",     "Water"),
]

# ============================================================
# 常量 (Constants) — 五行 (Five Elements / ḥByung-ba)
# ============================================================

# (index, Tibetan, English, Chinese, color, emoji)
TIBETAN_ELEMENTS = [
    (0, "Shing",  "Wood",  "木", "#228B22", "🌳"),
    (1, "Me",     "Fire",  "火", "#DC143C", "🔥"),
    (2, "Sa",     "Earth", "土", "#DAA520", "🌍"),
    (3, "Lcags",  "Metal", "金", "#C0C0C0", "⚙️"),
    (4, "Chu",    "Water", "水", "#1E90FF", "💧"),
]

# ============================================================
# 陰陽 (Pho-Mo / Male-Female)
# ============================================================

TIBETAN_POLARITIES = [
    (0, "Pho",  "Yang", "陽", "☀️"),
    (1, "Mo",   "Yin",  "陰", "🌙"),
]

# ============================================================
# 九宮 Mewa (sMe-ba dgu / Nine Mewa)
# ============================================================

# Each Mewa: (number, Tibetan_name, color_cn, color_en, direction, auspicious)
KALACHAKRA_MEWA = [
    (1, "sMe-ba dkar-po",     "白", "White",          "北 North",    True),
    (2, "sMe-ba nag-po",      "黑", "Black",          "西南 SW",     False),
    (3, "sMe-ba sngon-po",    "藍", "Blue",           "東 East",     True),
    (4, "sMe-ba ljang-khu",   "綠", "Green",          "東南 SE",     True),
    (5, "sMe-ba ser-po",      "黃", "Yellow",         "中央 Center", False),
    (6, "sMe-ba dkar-po",     "白", "White",          "西北 NW",     True),
    (7, "sMe-ba dmar-po",     "紅", "Red",            "西 West",     False),
    (8, "sMe-ba dkar-po",     "白", "White",          "東北 NE",     True),
    (9, "sMe-ba dmar-po",     "紅", "Maroon/Red",     "南 South",    False),
]

# ============================================================
# 八卦 Parkha (sPar-kha brgyad / Eight Parkha)
# ============================================================

# (index, Tibetan, Chinese_trigram, English, direction, element)
KALACHAKRA_PARKHA = [
    (0, "Kham",  "坎", "Kan (Water)",    "北 North",     "Water"),
    (1, "Li",    "離", "Li (Fire)",      "南 South",     "Fire"),
    (2, "Dui",   "兌", "Dui (Lake)",     "西 West",      "Metal"),
    (3, "Gen",   "艮", "Gen (Mountain)", "東北 NE",      "Earth"),
    (4, "Qian",  "乾", "Qian (Heaven)",  "西北 NW",      "Metal"),
    (5, "Kun",   "坤", "Kun (Earth)",    "西南 SW",      "Earth"),
    (6, "Zhen",  "震", "Zhen (Thunder)", "東 East",      "Wood"),
    (7, "Xun",   "巽", "Xun (Wind)",     "東南 SE",      "Wood"),
]

# ============================================================
# 五力 (Five Forces / dBang-thang lnga)
# ============================================================

KALACHAKRA_FIVE_FORCES = [
    ("La",        "魂",   "Soul",      "生命的精神核心 / Spiritual core of life"),
    ("Sok",       "命",   "Life",      "生命活力 / Life vitality"),
    ("Lu",        "身",   "Body",      "身體健康 / Physical health"),
    ("Wangthang", "權勢", "Power",     "個人權威與影響力 / Authority and influence"),
    ("Lungta",    "風馬", "Wind Horse", "運勢與好運 / Fortune and luck"),
]

# ============================================================
# 九曜 (Nine Planets / Graha) — Kalachakra 古法
# ============================================================

TIBETAN_PLANET_GODS = {
    "Sun":     "Nyima (ཉི་མ) / 太陽神",
    "Moon":    "Dawa (ཟླ་བ) / 月神",
    "Mercury": "Lhakpa (ལྷག་པ) / 水星",
    "Venus":   "Pasang (པ་སངས) / 金星",
    "Mars":    "Mig-dmar (མིག་དམར) / 火星",
    "Jupiter": "Phur-bu (ཕུར་བུ) / 木星",
    "Saturn":  "Spen-pa (སྤེན་པ) / 土星",
    "Rahu":    "Ra-hu (ར་ཧུ) / 羅睺",
    "Ketu":    "Khe-ta (ཁེ་ཏ) / 計都",
}

TIBETAN_GRAHA_CN = {
    "Sun": "太陽", "Moon": "月亮", "Mercury": "水星", "Venus": "金星",
    "Mars": "火星", "Jupiter": "木星", "Saturn": "土星",
    "Rahu": "羅睺", "Ketu": "計都",
}

TIBETAN_PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
    "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE,
}

TIBETAN_PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
    "Rahu": "☊", "Ketu": "☋",
}

TIBETAN_PLANET_COLORS = {
    "Sun": "#b8860b", "Moon": "#556b7f", "Mercury": "#8b6914",
    "Venus": "#2e7d32", "Mars": "#b71c1c", "Jupiter": "#1565c0",
    "Saturn": "#4a4a4a", "Rahu": "#555555", "Ketu": "#777777",
}

# ============================================================
# 二十七宿 (rGyu-skar / Nakshatra)
# ============================================================

KALACHAKRA_NAKSHATRAS = [
    ("Ashvini",       "馬頭", 0.0),
    ("Bharani",       "三足", 13.333),
    ("Krittika",      "昴宿", 26.667),
    ("Rohini",        "畢宿", 40.0),
    ("Mrigashira",    "觜宿", 53.333),
    ("Ardra",         "參宿", 66.667),
    ("Punarvasu",     "井宿", 80.0),
    ("Pushya",        "鬼宿", 93.333),
    ("Ashlesha",      "柳宿", 106.667),
    ("Magha",         "星宿", 120.0),
    ("Purva Phalguni","張宿", 133.333),
    ("Uttara Phalguni","翼宿", 146.667),
    ("Hasta",         "角宿", 160.0),
    ("Chitra",        "亢宿", 173.333),
    ("Svati",         "氐宿", 186.667),
    ("Vishakha",      "房宿", 200.0),
    ("Anuradha",      "心宿", 213.333),
    ("Jyeshtha",      "尾宿", 226.667),
    ("Mula",          "箕宿", 240.0),
    ("Purva Ashadha", "斗宿", 253.333),
    ("Uttara Ashadha","牛宿", 266.667),
    ("Shravana",      "女宿", 280.0),
    ("Dhanishta",     "虛宿", 293.333),
    ("Shatabhisha",   "危宿", 306.667),
    ("Purva Bhadrapada","室宿", 320.0),
    ("Uttara Bhadrapada","壁宿", 333.333),
    ("Revati",        "奎宿", 346.667),
]

# ============================================================
# 十二宮 (Sidereal Signs)
# ============================================================

KALACHAKRA_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

KALACHAKRA_SIGN_CN = {
    "Aries": "白羊", "Taurus": "金牛", "Gemini": "雙子", "Cancer": "巨蟹",
    "Leo": "獅子", "Virgo": "處女", "Libra": "天秤", "Scorpio": "天蠍",
    "Sagittarius": "射手", "Capricorn": "摩羯", "Aquarius": "水瓶", "Pisces": "雙魚",
}

KALACHAKRA_SIGN_GLYPHS = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓",
]

# ============================================================
# 生肖性格描述
# ============================================================

TIBETAN_ANIMAL_PERSONALITIES = {
    0:  ("聰明機智，適應力強，善察人心。",
         "Clever, adaptable, perceptive of human nature."),
    1:  ("勤勉踏實，耐力持久，可靠穩重。",
         "Diligent, enduring, reliable and stable."),
    2:  ("勇猛威嚴，充滿魄力，天生領袖。",
         "Courageous, powerful, a natural leader."),
    3:  ("溫和善良，藝術天賦，心思細膩。",
         "Gentle, artistic, sensitive and refined."),
    4:  ("威嚴高貴，精力充沛，魅力非凡。",
         "Majestic, energetic, charismatic."),
    5:  ("深沉智慧，直覺敏銳，善於思辨。",
         "Wise, intuitive, analytical."),
    6:  ("自由奔放，熱情開朗，勇往直前。",
         "Free-spirited, enthusiastic, forward-moving."),
    7:  ("溫順和善，富同情心，具藝術感。",
         "Gentle, compassionate, artistic."),
    8:  ("聰慧靈巧，多才多藝，善於變通。",
         "Clever, versatile, adaptable."),
    9:  ("勤勞精確，觀察敏銳，注重細節。",
         "Industrious, observant, detail-oriented."),
    10: ("忠誠正直，勇敢無畏，守護本能。",
         "Loyal, righteous, brave, protective."),
    11: ("寬厚仁慈，樂觀豁達，享受當下。",
         "Generous, optimistic, enjoys the present."),
}

TIBETAN_ELEMENT_PERSONALITIES = {
    0: ("木 (Shing)：仁慈、創意、成長力。",
        "Wood (Shing): Benevolent, creative, growth-oriented."),
    1: ("火 (Me)：熱情、果斷、啟發力。",
        "Fire (Me): Passionate, decisive, inspiring."),
    2: ("土 (Sa)：穩重、務實、包容力。",
        "Earth (Sa): Stable, practical, nurturing."),
    3: ("金 (Lcags)：堅毅、正義、精確。",
        "Metal (Lcags): Resolute, just, precise."),
    4: ("水 (Chu)：智慧、靈活、深沉。",
        "Water (Chu): Wise, flexible, profound."),
}

# ============================================================
# 60 年循環基準年 (rab-byung cycle)
# 第 16 個勝生週期 (rab-byung) 始於 1927 年（火兔陰年）
# 為簡化對照，使用 1924 年（木鼠陽年）作為基準
# ============================================================

KALACHAKRA_CYCLE_BASE_YEAR = 1924

# 五行相生相剋
KALACHAKRA_GENERATING = {0: 1, 1: 2, 2: 3, 3: 4, 4: 0}
KALACHAKRA_OVERCOMING = {0: 2, 2: 4, 4: 1, 1: 3, 3: 0}


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _sign_idx(lon):
    return int(lon / 30) % 12


def _sign_deg(lon):
    return lon % 30


def _normalize(deg):
    return deg % 360


def _get_nakshatra(sid_lon):
    """Return nakshatra index (0-26) from sidereal longitude."""
    return int(sid_lon / (360.0 / 27)) % 27


def _get_tibetan_animal(year):
    idx = (year - KALACHAKRA_CYCLE_BASE_YEAR) % 12
    a = TIBETAN_ANIMALS[idx]
    p_cn, p_en = TIBETAN_ANIMAL_PERSONALITIES[idx]
    return idx, a, p_cn, p_en


def _get_tibetan_element(year):
    idx = ((year - KALACHAKRA_CYCLE_BASE_YEAR) // 2) % 5
    return idx, TIBETAN_ELEMENTS[idx]


def _get_tibetan_polarity(year):
    idx = (year - KALACHAKRA_CYCLE_BASE_YEAR) % 2
    return idx, TIBETAN_POLARITIES[idx]


def _get_mewa_for_year(year):
    """Calculate birth Mewa number (1-9) from year.

    Traditional formula: Mewa cycles in a descending sequence from a reference.
    Reference: 1927 (start of 16th rab-byung) = Mewa 1.
    Male descends, Female ascends; simplified here with a universal formula.
    """
    mewa = (10 - ((year - 1927) % 9)) % 9
    if mewa == 0:
        mewa = 9
    return mewa


def _get_parkha_for_year(year, is_male=True):
    """Calculate birth Parkha (0-7) from year and gender.

    Traditional formula uses different sequences for male and female.
    Male: Li → Kham → Dui → Qian → Kun → Xun → Zhen → Gen (descending)
    Female: Kham → Li → Gen → Zhen → Xun → Kun → Qian → Dui (ascending)
    """
    if is_male:
        seq = [1, 0, 2, 4, 5, 7, 6, 3]  # Li, Kham, Dui, Qian, Kun, Xun, Zhen, Gen
    else:
        seq = [0, 1, 3, 6, 7, 5, 4, 2]  # Kham, Li, Gen, Zhen, Xun, Kun, Qian, Dui
    idx = (year - 1927) % 8
    return seq[idx]


def _compute_five_forces(animal_idx, element_idx, mewa_num):
    """Compute Five Forces based on animal, element, and Mewa.

    Each force is rated: "strong" (強), "medium" (中), "weak" (弱).
    Simplified traditional algorithm.
    """
    forces = []
    # La (Soul) — related to Mewa
    la_strength = "strong" if mewa_num in (1, 3, 6, 8) else (
        "medium" if mewa_num in (4, 9) else "weak")
    forces.append(("La", "魂", "Soul", la_strength))

    # Sok (Life) — related to element
    sok_strength = "strong" if element_idx in (0, 1) else (
        "medium" if element_idx == 2 else "weak")
    forces.append(("Sok", "命", "Life", sok_strength))

    # Lu (Body) — related to animal
    lu_strength = "strong" if animal_idx in (2, 4, 6) else (
        "medium" if animal_idx in (0, 1, 8, 9) else "weak")
    forces.append(("Lu", "身", "Body", lu_strength))

    # Wangthang (Power) — combined animal + element
    wangthang_score = (animal_idx + element_idx) % 3
    wangthang_strength = ["strong", "medium", "weak"][wangthang_score]
    forces.append(("Wangthang", "權勢", "Power", wangthang_strength))

    # Lungta (Wind Horse) — combined Mewa + animal
    lungta_score = (mewa_num + animal_idx) % 3
    lungta_strength = ["strong", "medium", "weak"][lungta_score]
    forces.append(("Lungta", "風馬", "Wind Horse", lungta_strength))

    return forces


def _element_relation(birth_idx, current_idx):
    """Get element relationship."""
    if birth_idx == current_idx:
        return "same", "同行 — 元素相同", "Same element — stable"
    if KALACHAKRA_GENERATING.get(birth_idx) == current_idx:
        b_cn = TIBETAN_ELEMENTS[birth_idx][3]
        c_cn = TIBETAN_ELEMENTS[current_idx][3]
        return ("generating",
                f"相生 — {b_cn}生{c_cn}，有利發展",
                f"Generating — favorable")
    if KALACHAKRA_GENERATING.get(current_idx) == birth_idx:
        return ("weakening",
                "洩氣 — 能量外洩，宜守",
                "Weakening — conserve energy")
    if KALACHAKRA_OVERCOMING.get(birth_idx) == current_idx:
        return ("overcoming",
                "相剋 — 主動有力但須謹慎",
                "Overcoming — active, use caution")
    return ("resisting",
            "耗氣 — 受壓制，宜守不宜攻",
            "Resisting — defensive stance advised")


# ============================================================
# 資料類別 (Dataclasses)
# ============================================================

@dataclass
class TibetanAnimalInfo:
    """藏傳生肖資料"""
    index: int
    name_tibetan: str
    name_cn: str
    name_en: str
    fixed_element: str
    emoji: str
    personality_cn: str
    personality_en: str


@dataclass
class TibetanElementInfo:
    """藏傳五行資料"""
    index: int
    name_tibetan: str
    name_en: str
    name_cn: str
    color: str
    emoji: str
    personality_cn: str
    personality_en: str


@dataclass
class TibetanMewa:
    """九宮 Mewa"""
    number: int
    name_tibetan: str
    color_cn: str
    color_en: str
    direction: str
    is_auspicious: bool


@dataclass
class TibetanParkha:
    """八卦 Parkha"""
    index: int
    name_tibetan: str
    name_cn: str
    name_en: str
    direction: str
    element: str


@dataclass
class TibetanForce:
    """五力"""
    name_tibetan: str
    name_cn: str
    name_en: str
    strength: str  # "strong", "medium", "weak"


@dataclass
class TibetanPlanetPosition:
    """九曜位置"""
    name: str
    name_cn: str
    god_name: str
    glyph: str
    sidereal_lon: float
    sign: str
    sign_cn: str
    sign_degree: float
    nakshatra: str
    nakshatra_cn: str


@dataclass
class TibetanChart:
    """藏傳時輪金剛占星排盤結果"""
    # Input
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str

    # Animal / Element / Polarity
    birth_animal: TibetanAnimalInfo
    birth_element: TibetanElementInfo
    birth_polarity_cn: str
    birth_polarity_en: str
    birth_polarity_symbol: str
    cycle_year: int

    # Mewa / Parkha / Five Forces
    mewa: TibetanMewa
    parkha: TibetanParkha
    five_forces: list  # list[TibetanForce]

    # Planets (nine graha)
    planets: list  # list[TibetanPlanetPosition]
    ayanamsa: float

    # Current year
    current_animal_cn: str
    current_animal_en: str
    current_element_cn: str
    current_element_en: str
    element_relation_cn: str
    element_relation_en: str

    # Omens / summary
    omens: list = field(default_factory=list)  # list of str


# ============================================================
# 主計算函數 (Main Computation)
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_tibetan_chart(year, month, day, hour, minute,
                          timezone, latitude, longitude,
                          location_name="", gender="male") -> TibetanChart:
    """計算藏傳時輪金剛占星排盤。

    Args:
        year, month, day: 出生日期（公曆）
        hour, minute: 出生時間
        timezone: 時區 (UTC offset)
        latitude, longitude: 出生地經緯度
        location_name: 地點名稱
        gender: "male" or "female"

    Returns:
        TibetanChart 排盤結果
    """
    # --- Animal / Element / Polarity ---
    animal_idx, animal_tuple, anim_p_cn, anim_p_en = _get_tibetan_animal(year)
    elem_idx, elem_tuple = _get_tibetan_element(year)
    pol_idx, pol_tuple = _get_tibetan_polarity(year)
    cycle_year = (year - KALACHAKRA_CYCLE_BASE_YEAR) % 60

    animal_emojis = ["🐀", "🐂", "🐅", "🐇", "🐉", "🐍",
                     "🐴", "🐑", "🐒", "🐦", "🐕", "🐖"]

    birth_animal = TibetanAnimalInfo(
        index=animal_idx,
        name_tibetan=animal_tuple[1],
        name_cn=animal_tuple[2],
        name_en=animal_tuple[3],
        fixed_element=animal_tuple[4],
        emoji=animal_emojis[animal_idx],
        personality_cn=anim_p_cn,
        personality_en=anim_p_en,
    )

    ep_cn, ep_en = TIBETAN_ELEMENT_PERSONALITIES[elem_idx]
    birth_element = TibetanElementInfo(
        index=elem_idx,
        name_tibetan=elem_tuple[1],
        name_en=elem_tuple[2],
        name_cn=elem_tuple[3],
        color=elem_tuple[4],
        emoji=elem_tuple[5],
        personality_cn=ep_cn,
        personality_en=ep_en,
    )

    # --- Mewa ---
    mewa_num = _get_mewa_for_year(year)
    mewa_data = KALACHAKRA_MEWA[mewa_num - 1]
    mewa = TibetanMewa(
        number=mewa_data[0],
        name_tibetan=mewa_data[1],
        color_cn=mewa_data[2],
        color_en=mewa_data[3],
        direction=mewa_data[4],
        is_auspicious=mewa_data[5],
    )

    # --- Parkha ---
    is_male = (gender == "male")
    parkha_idx = _get_parkha_for_year(year, is_male=is_male)
    parkha_data = KALACHAKRA_PARKHA[parkha_idx]
    parkha = TibetanParkha(
        index=parkha_data[0],
        name_tibetan=parkha_data[1],
        name_cn=parkha_data[2],
        name_en=parkha_data[3],
        direction=parkha_data[4],
        element=parkha_data[5],
    )

    # --- Five Forces ---
    raw_forces = _compute_five_forces(animal_idx, elem_idx, mewa_num)
    five_forces = [
        TibetanForce(name_tibetan=f[0], name_cn=f[1], name_en=f[2], strength=f[3])
        for f in raw_forces
    ]

    # --- Planet positions (Sidereal / Lahiri ayanamsa) ---
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    planets = []
    for name, pid in TIBETAN_PLANET_IDS.items():
        pos, _ = swe.calc_ut(jd, pid)
        trop_lon = pos[0]
        ayanamsa_val = swe.get_ayanamsa_ut(jd)
        sid_lon = _normalize(trop_lon - ayanamsa_val)
        s_idx = _sign_idx(sid_lon)
        nak_idx = _get_nakshatra(sid_lon)

        planets.append(TibetanPlanetPosition(
            name=name,
            name_cn=TIBETAN_GRAHA_CN[name],
            god_name=TIBETAN_PLANET_GODS[name],
            glyph=TIBETAN_PLANET_GLYPHS[name],
            sidereal_lon=round(sid_lon, 4),
            sign=KALACHAKRA_SIGNS[s_idx],
            sign_cn=KALACHAKRA_SIGN_CN[KALACHAKRA_SIGNS[s_idx]],
            sign_degree=round(_sign_deg(sid_lon), 2),
            nakshatra=KALACHAKRA_NAKSHATRAS[nak_idx][0],
            nakshatra_cn=KALACHAKRA_NAKSHATRAS[nak_idx][1],
        ))

    # Ketu = opposite of Rahu
    rahu_planet = next((p for p in planets if p.name == "Rahu"), None)
    if rahu_planet:
        ketu_lon = _normalize(rahu_planet.sidereal_lon + 180)
        k_idx = _sign_idx(ketu_lon)
        k_nak = _get_nakshatra(ketu_lon)
        planets.append(TibetanPlanetPosition(
            name="Ketu",
            name_cn=TIBETAN_GRAHA_CN["Ketu"],
            god_name=TIBETAN_PLANET_GODS["Ketu"],
            glyph=TIBETAN_PLANET_GLYPHS["Ketu"],
            sidereal_lon=round(ketu_lon, 4),
            sign=KALACHAKRA_SIGNS[k_idx],
            sign_cn=KALACHAKRA_SIGN_CN[KALACHAKRA_SIGNS[k_idx]],
            sign_degree=round(_sign_deg(ketu_lon), 2),
            nakshatra=KALACHAKRA_NAKSHATRAS[k_nak][0],
            nakshatra_cn=KALACHAKRA_NAKSHATRAS[k_nak][1],
        ))

    ayanamsa_val = swe.get_ayanamsa_ut(jd)

    # --- Current year info ---
    current_year = date.today().year
    c_anim_idx, c_anim, _, _ = _get_tibetan_animal(current_year)
    c_elem_idx, c_elem = _get_tibetan_element(current_year)
    rel_key, rel_cn, rel_en = _element_relation(elem_idx, c_elem_idx)

    # --- Omens (簡易吉凶提示) ---
    omens = []
    strength_cn = {"strong": "強", "medium": "中", "weak": "弱"}
    for f in five_forces:
        if f.strength == "strong":
            omens.append(f"✅ {f.name_cn}({f.name_tibetan})力量充沛")
        elif f.strength == "weak":
            omens.append(f"⚠️ {f.name_cn}({f.name_tibetan})力量不足，宜注意")

    if not mewa.is_auspicious:
        omens.append(f"⚠️ Mewa {mewa.number}（{mewa.color_cn}）屬不吉之數，宜多行善")
    else:
        omens.append(f"✅ Mewa {mewa.number}（{mewa.color_cn}）屬吉祥之數")

    return TibetanChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
        birth_animal=birth_animal,
        birth_element=birth_element,
        birth_polarity_cn=pol_tuple[3],
        birth_polarity_en=pol_tuple[2],
        birth_polarity_symbol=pol_tuple[4],
        cycle_year=cycle_year,
        mewa=mewa,
        parkha=parkha,
        five_forces=five_forces,
        planets=planets,
        ayanamsa=round(ayanamsa_val, 4),
        current_animal_cn=c_anim[2],
        current_animal_en=c_anim[3],
        current_element_cn=c_elem[3],
        current_element_en=c_elem[2],
        element_relation_cn=rel_cn,
        element_relation_en=rel_en,
        omens=omens,
    )


# ============================================================
# Kalachakra 曼荼羅 SVG (Mandala-style Chart)
# ============================================================

def build_kalachakra_mandala_svg(chart, year=None, month=None, day=None,
                                 hour=None, minute=None, tz=None,
                                 location=""):
    """Build Kalachakra Mandala-style SVG chart.

    Concentric rings:
    - Outer ring: 12 Animal signs
    - Middle ring: 8 Parkha (trigrams)
    - Inner ring: 9 Mewa (magic square)
    - Center: Birth info summary
    - Planet markers on outer ring

    Returns:
        str — complete ``<svg>`` markup.
    """
    SIZE = 620
    CX, CY = SIZE / 2, SIZE / 2

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SIZE} {SIZE}" '
        f'style="width:100%;max-width:620px;margin:auto;display:block;" '
        f'font-family="serif">'
    )

    # Background — thangka-style warm gold
    svg.append(f'<rect width="{SIZE}" height="{SIZE}" fill="#2c1810" rx="8"/>')

    # Decorative border (double frame)
    svg.append(
        f'<rect x="6" y="6" width="{SIZE-12}" height="{SIZE-12}" '
        f'fill="none" stroke="#c49a3c" stroke-width="3" rx="6"/>'
    )
    svg.append(
        f'<rect x="12" y="12" width="{SIZE-24}" height="{SIZE-24}" '
        f'fill="none" stroke="#8b6914" stroke-width="1.5" rx="4"/>'
    )

    # --- Outer ring: 12 Animals ---
    R_OUTER = 270
    R_MID = 210
    R_PARKHA = 160
    R_MEWA = 100
    R_CENTER = 60

    # Background circles
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER}" '
        f'fill="none" stroke="#c49a3c" stroke-width="2"/>'
    )
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_MID}" '
        f'fill="none" stroke="#8b6914" stroke-width="1.5"/>'
    )
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_PARKHA}" '
        f'fill="none" stroke="#8b6914" stroke-width="1"/>'
    )
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_MEWA}" '
        f'fill="none" stroke="#8b6914" stroke-width="1"/>'
    )

    animal_emojis = ["🐀", "🐂", "🐅", "🐇", "🐉", "🐍",
                     "🐴", "🐑", "🐒", "🐦", "🐕", "🐖"]

    # Draw 12 animal segments
    slice_angle = 30.0
    birth_animal_idx = chart.birth_animal.index

    for i in range(12):
        start_deg = i * slice_angle - 90 - slice_angle / 2
        end_deg = start_deg + slice_angle
        mid_deg = i * slice_angle - 90
        mid_rad = math.radians(mid_deg)

        # Segment fill
        is_birth = (i == birth_animal_idx)
        elem_name = TIBETAN_ANIMALS[i][4]
        elem_colors = {"Wood": "#228B22", "Fire": "#DC143C", "Earth": "#DAA520",
                       "Metal": "#C0C0C0", "Water": "#1E90FF"}
        e_color = elem_colors.get(elem_name, "#888")
        fill = f"{e_color}44" if not is_birth else f"{e_color}88"

        # Draw arc segment
        s_rad = math.radians(start_deg)
        e_rad = math.radians(end_deg)
        ox1 = CX + R_OUTER * math.cos(s_rad)
        oy1 = CY + R_OUTER * math.sin(s_rad)
        ox2 = CX + R_OUTER * math.cos(e_rad)
        oy2 = CY + R_OUTER * math.sin(e_rad)
        mx1 = CX + R_MID * math.cos(s_rad)
        my1 = CY + R_MID * math.sin(s_rad)
        mx2 = CX + R_MID * math.cos(e_rad)
        my2 = CY + R_MID * math.sin(e_rad)

        stroke = "#c49a3c" if is_birth else "#5c3a1e"
        sw = "2.5" if is_birth else "0.8"

        svg.append(
            f'<path d="M{ox1:.1f},{oy1:.1f} '
            f'A{R_OUTER},{R_OUTER} 0 0 1 {ox2:.1f},{oy2:.1f} '
            f'L{mx2:.1f},{my2:.1f} '
            f'A{R_MID},{R_MID} 0 0 0 {mx1:.1f},{my1:.1f} Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )

        # Animal emoji + text
        r_text = (R_OUTER + R_MID) / 2
        tx = CX + r_text * math.cos(mid_rad)
        ty = CY + r_text * math.sin(mid_rad)
        a_info = TIBETAN_ANIMALS[i]

        svg.append(
            f'<text x="{tx:.1f}" y="{ty - 5:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" font-size="18" fill="white">'
            f'{animal_emojis[i]}</text>'
        )
        svg.append(
            f'<text x="{tx:.1f}" y="{ty + 12:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" font-size="8" fill="#ddd">'
            f'{a_info[2]}</text>'
        )

        # Radial divider
        svg.append(
            f'<line x1="{mx1:.1f}" y1="{my1:.1f}" '
            f'x2="{ox1:.1f}" y2="{oy1:.1f}" '
            f'stroke="#5c3a1e" stroke-width="0.5"/>'
        )

    # --- Planet markers on outer ring ---
    for p in chart.planets:
        # Place planet glyph at its sidereal position
        p_angle = p.sidereal_lon - 90  # offset so 0° is at top
        p_rad = math.radians(p_angle)
        r_planet = R_OUTER + 16
        px = CX + r_planet * math.cos(p_rad)
        py = CY + r_planet * math.sin(p_rad)
        p_color = TIBETAN_PLANET_COLORS.get(p.name, "#ddd")
        svg.append(
            f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{p_color}" '
            f'font-size="14" font-weight="bold">{p.glyph}</text>'
        )

    # --- Middle ring: 8 Parkha ---
    parkha_slice = 45.0
    parkha_symbols = ["☵", "☲", "☱", "☶", "☰", "☷", "☳", "☴"]  # trigram symbols
    birth_parkha_idx = chart.parkha.index

    for i in range(8):
        mid_deg = i * parkha_slice - 90
        mid_rad = math.radians(mid_deg)
        r_pk = (R_MID + R_PARKHA) / 2
        pkx = CX + r_pk * math.cos(mid_rad)
        pky = CY + r_pk * math.sin(mid_rad)

        pk_data = KALACHAKRA_PARKHA[i]
        is_birth_pk = (i == birth_parkha_idx)
        pk_color = "#c49a3c" if is_birth_pk else "#a89060"
        pk_size = "18" if is_birth_pk else "14"

        svg.append(
            f'<text x="{pkx:.1f}" y="{pky - 4:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{pk_color}" '
            f'font-size="{pk_size}" font-weight="bold">{parkha_symbols[i]}</text>'
        )
        svg.append(
            f'<text x="{pkx:.1f}" y="{pky + 10:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#8b7355" '
            f'font-size="7">{pk_data[2]}</text>'
        )

    # --- Inner ring: 9 Mewa (magic square arrangement approximated on circle) ---
    mewa_positions = [
        (270, "S"),   # 1 — South/bottom (water)
        (225, "SW"),  # 2 — SW
        (0, "E"),     # 3 — East
        (315, "SE"),  # 4 — SE (adjusted)
        (None, "C"),  # 5 — Center
        (135, "NW"),  # 6 — NW
        (180, "W"),   # 7 — West
        (45, "NE"),   # 8 — NE
        (90, "N"),    # 9 — North/top
    ]

    mewa_colors = {
        1: "#ffffff", 2: "#333333", 3: "#4169E1", 4: "#228B22",
        5: "#DAA520", 6: "#ffffff", 7: "#DC143C", 8: "#ffffff", 9: "#8B0000",
    }

    birth_mewa = chart.mewa.number

    for m_num in range(1, 10):
        angle, _ = mewa_positions[m_num - 1]
        color = mewa_colors[m_num]
        is_birth_mewa = (m_num == birth_mewa)

        if angle is None:
            # Center Mewa
            mx, my = CX, CY - R_MEWA + 20
        else:
            r_mewa_pos = (R_PARKHA + R_MEWA) / 2
            m_rad = math.radians(angle - 90)
            mx = CX + r_mewa_pos * math.cos(m_rad)
            my = CY + r_mewa_pos * math.sin(m_rad)

        bg_r = 12 if is_birth_mewa else 9
        if is_birth_mewa:
            svg.append(
                f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{bg_r}" '
                f'fill="#c49a3c" fill-opacity="0.5" '
                f'stroke="#c49a3c" stroke-width="1.5"/>'
            )

        text_color = color if color != "#333333" else "#aaa"
        f_size = "14" if is_birth_mewa else "11"
        svg.append(
            f'<text x="{mx:.1f}" y="{my:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{text_color}" '
            f'font-size="{f_size}" font-weight="bold">{m_num}</text>'
        )

    # --- Center circle ---
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_CENTER}" '
        f'fill="#2c1810" stroke="#c49a3c" stroke-width="2"/>'
    )

    # Center text
    svg.append(
        f'<text x="{CX}" y="{CY - 38}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#c49a3c" '
        f'font-size="12" font-weight="bold">ཀཱ་ལ་ཙཀྲ</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY - 22}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#c49a3c" '
        f'font-size="10">時輪金剛</text>'
    )

    a = chart.birth_animal
    e = chart.birth_element
    svg.append(
        f'<text x="{CX}" y="{CY - 6}" text-anchor="middle" '
        f'dominant-baseline="central" fill="white" '
        f'font-size="16">{a.emoji}</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY + 10}" text-anchor="middle" '
        f'dominant-baseline="central" fill="white" '
        f'font-size="10" font-weight="bold">'
        f'{chart.birth_polarity_cn}{e.name_cn}{a.name_cn}</text>'
    )

    if year is not None and month is not None and day is not None:
        date_str = f"{year}-{month:02d}-{day:02d}"
        svg.append(
            f'<text x="{CX}" y="{CY + 24}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#8b7355" '
            f'font-size="8">{date_str}</text>'
        )

    if hour is not None and minute is not None:
        tz_str = f" UTC{tz:+.1f}" if tz is not None else ""
        time_str = f"{hour:02d}:{minute:02d}{tz_str}"
        svg.append(
            f'<text x="{CX}" y="{CY + 36}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#8b7355" '
            f'font-size="8">{time_str}</text>'
        )

    if location:
        svg.append(
            f'<text x="{CX}" y="{CY + 48}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#8b7355" '
            f'font-size="7">{location[:25]}</text>'
        )

    svg.append("</svg>")
    return "\n".join(svg)


# ============================================================
# Streamlit 渲染函數 (Rendering Functions)
# ============================================================

def render_tibetan_chart(chart, after_chart_hook=None):
    """Render Tibetan Kalachakra chart in Streamlit."""
    _render_mandala(chart)
    st.divider()
    _render_basic_info(chart)
    st.divider()
    _render_mewa_parkha(chart)
    st.divider()
    _render_five_forces(chart)
    st.divider()
    _render_planets(chart)
    st.divider()
    _render_omens(chart)
    if after_chart_hook:
        after_chart_hook()
    st.divider()
    _render_history()
    st.divider()
    _render_cultural_note()


def _render_mandala(chart):
    """渲染時輪金剛曼荼羅圖。"""
    st.subheader("☸️ 時輪金剛曼荼羅 / Kalachakra Mandala")
    svg = build_kalachakra_mandala_svg(
        chart,
        year=chart.year, month=chart.month, day=chart.day,
        hour=chart.hour, minute=chart.minute, tz=chart.timezone,
        location=chart.location_name,
    )
    st.markdown(svg, unsafe_allow_html=True)
    st.caption(
        '<p style="text-align:center;color:#888;font-size:11px;">'
        'Kalachakra Mandala · 時輪金剛曼荼羅 · '
        'Outer: 12 Animals · Middle: 8 Parkha · Inner: 9 Mewa'
        '</p>',
        unsafe_allow_html=True,
    )


def _render_basic_info(chart):
    """渲染基本排盤資訊。"""
    st.subheader("📋 藏傳占星基本資料 / Tibetan Chart Info")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎂 出生資料 / Birth Data")
        st.write(f"**出生日期：** {chart.year}/{chart.month}/{chart.day} "
                 f"{chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**出生地點：** {chart.location_name} "
                 f"({chart.latitude:.2f}°, {chart.longitude:.2f}°)")
        st.write(f"**時區：** UTC{chart.timezone:+.1f}")

        st.markdown("---")
        a = chart.birth_animal
        e = chart.birth_element
        st.markdown("#### 🐾 出生年生肖與五行 / Birth Year Animal & Element")
        st.markdown(
            f'<div style="background:{e.color}22;padding:12px;'
            f'border-radius:8px;border:2px solid {e.color};">'
            f'<span style="font-size:2em;">{a.emoji}</span> '
            f'<b>{chart.birth_polarity_cn}{e.name_cn}{a.name_cn}</b><br>'
            f'{chart.birth_polarity_symbol} {chart.birth_polarity_en} '
            f'{e.emoji} {e.name_en} {a.name_en}<br>'
            f'<small>🏔️ {a.name_tibetan} · {e.name_tibetan}</small>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.write(f"**60年循環位置：** 第 {chart.cycle_year + 1} 年 / "
                 f"Year {chart.cycle_year + 1} of 60")
        st.write(f"**固有五行：** {a.fixed_element}")

    with col2:
        st.markdown("#### 🌟 性格特質 / Personality")
        st.markdown(
            f"**{a.emoji} {a.name_cn}（{a.name_tibetan}）性格：**\n\n"
            f"- {a.personality_cn}\n"
            f"- {a.personality_en}"
        )
        st.markdown(
            f"**{e.emoji} {e.name_cn}行（{e.name_tibetan}）特質：**\n\n"
            f"- {e.personality_cn}\n"
            f"- {e.personality_en}"
        )

        st.markdown("---")
        st.markdown("#### 📅 今年運勢 / Current Year")
        st.write(f"**今年生肖：** {chart.current_animal_cn} ({chart.current_animal_en})")
        st.write(f"**今年五行：** {chart.current_element_cn} ({chart.current_element_en})")
        st.write(f"**元素關係：** {chart.element_relation_cn}")
        st.write(f"*{chart.element_relation_en}*")


def _render_mewa_parkha(chart):
    """渲染 Mewa 九宮與 Parkha 八卦。"""
    st.subheader("🔮 Mewa 九宮 與 Parkha 八卦")

    col1, col2 = st.columns(2)

    mewa_colors_map = {
        "白": "#f0f0f0", "黑": "#333", "藍": "#4169E1",
        "綠": "#228B22", "黃": "#DAA520", "紅": "#DC143C",
    }

    with col1:
        m = chart.mewa
        bg = mewa_colors_map.get(m.color_cn, "#888")
        text_c = "#000" if m.color_cn in ("白", "黃") else "#fff"
        auspicious_label = "✅ 吉 Auspicious" if m.is_auspicious else "⚠️ 不吉 Inauspicious"

        st.markdown(
            f'<div style="background:{bg};color:{text_c};padding:16px;'
            f'border-radius:10px;text-align:center;">'
            f'<span style="font-size:2.5em;font-weight:bold;">{m.number}</span><br>'
            f'<b>Mewa {m.number} — {m.color_cn} ({m.color_en})</b><br>'
            f'{m.name_tibetan}<br>'
            f'<small>方位 Direction: {m.direction}</small><br>'
            f'<small>{auspicious_label}</small>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Mewa reference table
        st.markdown("##### 九宮對照 / Mewa Reference")
        mewa_data = []
        for md in KALACHAKRA_MEWA:
            mewa_data.append({
                "Mewa": md[0],
                "顏色 Color": f"{md[2]} ({md[3]})",
                "方位 Direction": md[4],
                "吉凶": "吉 ✅" if md[5] else "不吉 ⚠️",
            })
        st.dataframe(mewa_data, width="stretch")

    with col2:
        pk = chart.parkha
        trigram_symbols = {"坎": "☵", "離": "☲", "兌": "☱", "艮": "☶",
                           "乾": "☰", "坤": "☷", "震": "☳", "巽": "☴"}
        tri_sym = trigram_symbols.get(pk.name_cn, "☰")

        st.markdown(
            f'<div style="background:#1a1a2e;color:#ddd;padding:16px;'
            f'border-radius:10px;text-align:center;border:2px solid #c49a3c;">'
            f'<span style="font-size:2.5em;">{tri_sym}</span><br>'
            f'<b>{pk.name_cn} ({pk.name_tibetan})</b><br>'
            f'{pk.name_en}<br>'
            f'<small>方位 Direction: {pk.direction}</small><br>'
            f'<small>元素 Element: {pk.element}</small>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Parkha reference table
        st.markdown("##### 八卦對照 / Parkha Reference")
        parkha_data = []
        for pd_item in KALACHAKRA_PARKHA:
            parkha_data.append({
                "卦 Trigram": pd_item[2],
                "Tibetan": pd_item[1],
                "English": pd_item[3],
                "方位": pd_item[4],
                "元素": pd_item[5],
            })
        st.dataframe(parkha_data, width="stretch")


def _render_five_forces(chart):
    """渲染五力 (Five Forces)。"""
    st.subheader("💪 五力 / Five Forces (dBang-thang lnga)")

    strength_emoji = {"strong": "🟢 強", "medium": "🟡 中", "weak": "🔴 弱"}
    strength_en = {"strong": "Strong", "medium": "Medium", "weak": "Weak"}

    cols = st.columns(5)
    for i, f in enumerate(chart.five_forces):
        with cols[i]:
            s_label = strength_emoji.get(f.strength, "—")
            bg_color = {"strong": "#1b5e20", "medium": "#f57f17",
                        "weak": "#b71c1c"}.get(f.strength, "#333")
            st.markdown(
                f'<div style="background:{bg_color}22;padding:10px;'
                f'border-radius:8px;text-align:center;'
                f'border:2px solid {bg_color};">'
                f'<b>{f.name_cn}</b><br>'
                f'<small>{f.name_tibetan}</small><br>'
                f'<small>{f.name_en}</small><br>'
                f'{s_label}<br>'
                f'<small>{strength_en[f.strength]}</small>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Force reference
    with st.expander("五力說明 / Five Forces Explanation"):
        for name_t, name_cn, name_en, desc in KALACHAKRA_FIVE_FORCES:
            st.markdown(f"- **{name_cn} ({name_t} / {name_en})**: {desc}")


def _render_planets(chart):
    """渲染九曜位置。"""
    st.subheader("🪐 九曜位置 / Nine Graha Positions")
    st.caption(f"Ayanamsa (Lahiri): {chart.ayanamsa}°")

    planet_data = []
    for p in chart.planets:
        planet_data.append({
            "曜 Planet": f"{p.glyph} {p.name_cn} ({p.name})",
            "藏傳神祇": p.god_name,
            "恆星經度": f"{p.sidereal_lon:.2f}°",
            "星座 Sign": f"{p.sign_cn} ({p.sign})",
            "度數 Degree": f"{p.sign_degree:.2f}°",
            "宿 Nakshatra": f"{p.nakshatra} ({p.nakshatra_cn})",
        })
    st.dataframe(planet_data, width="stretch")


def _render_omens(chart):
    """渲染吉凶提示。"""
    st.subheader("📜 吉凶提示 / Omens & Guidance")
    for omen in chart.omens:
        st.markdown(f"- {omen}")


def _render_history():
    """渲染歷史背景。"""
    with st.expander("📖 時輪金剛占星歷史 / History of Kalachakra Astrology"):
        st.markdown("""
**時輪金剛續 (Kalachakra Tantra)**

時輪金剛法是藏傳佛教最深奧的密續體系之一，相傳由釋迦牟尼佛於
印度南部的 Dhanyakataka 傳授予香巴拉國王 Suchandra。

時輪 (Kalachakra) 意為「時間之輪」，分為三個層次：
- **外時輪 (Outer Kalachakra)**：宇宙天文曆法、星象運行
- **內時輪 (Inner Kalachakra)**：人體脈輪、氣脈明點
- **別時輪 (Alternative Kalachakra)**：修行道次第、灌頂觀想

藏傳占星（rTsis）以外時輪為基礎，融合：
- 印度天文學 (Jyotish Shastra)：九曜、二十七宿、十二宮
- 中國曆算：干支、五行、八卦
- 苯教本土元素：Mewa 九宮、Parkha 八卦、五力系統

11 世紀由阿底峽尊者與其弟子將時輪法傳入西藏，
此後成為藏傳佛教四大教派共同尊奉的曆算與占星體系。
""")


def _render_cultural_note():
    """渲染文化聲明。"""
    st.info(
        "🏔️ **文化聲明 / Cultural Note**\n\n"
        "此藏傳時輪金剛占星排盤依循傳統古法計算，僅供文化學習與參考。\n"
        "重要人生決定請諮詢合格的藏傳占星師 (rTsis-pa) 或上師。\n\n"
        "*This Tibetan Kalachakra astrology chart follows traditional methods "
        "and is for cultural reference only. For important life decisions, "
        "please consult a qualified Tibetan astrologer (rTsis-pa) or lama.*"
    )
