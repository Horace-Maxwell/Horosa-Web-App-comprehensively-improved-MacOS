"""
蒙古祖爾海占星排盤模組 (Mongolian Zurkhai Astrology Chart Module)

蒙古祖爾海 (Зурхай / Zurkhai / Shar Zurkhai) 是蒙古傳統占星術，
源自藏傳佛教曆算體系，以松巴堪布 (Sumpa Khenpo Yeshe Peljor) 的
德古斯布揚圖祖爾海 (Tegus Buyantu Zurkhai) 為核心文獻。

核心特點：
- **12 生肖 (動物)**：鼠、牛、虎、兔、龍、蛇、馬、羊、猴、雞、狗、豬
- **五行 (元素)**：木、火、土、金、水，各分陰陽
- **60 年循環**：12 生肖 × 5 元素
- **擇吉 (Auspicious Timing)**：結婚、出行、建屋、醫療等吉凶計算
- **障礙年 (Obstacle Years)**：特定年齡對應的災厄年份
- **元素相生相剋**：木→火→土→金→水→木 (相生)；
  木→土→水→火→金→木 (相剋)

文化聲明：
此計算依循蒙古傳統祖爾海古法，僅供文化學習與參考，
重要決定請諮詢合格的蒙古占星師 (Zurkhaič) 或喇嘛。
"""

import math
import streamlit as st
from dataclasses import dataclass, field
from datetime import date, timedelta

# ============================================================
# 常量 (Constants) — 十二生肖
# ============================================================

# 12 Animal Signs (zodiac): (index, Mongolian, English, Chinese, emoji)
ANIMALS = [
    (0,  "Hulgana",  "Rat",     "鼠", "🐀"),
    (1,  "Ükher",    "Ox",      "牛", "🐂"),
    (2,  "Bar",      "Tiger",   "虎", "🐅"),
    (3,  "Tuulai",   "Rabbit",  "兔", "🐇"),
    (4,  "Luu",      "Dragon",  "龍", "🐉"),
    (5,  "Mogoi",    "Snake",   "蛇", "🐍"),
    (6,  "Mori",     "Horse",   "馬", "🐴"),
    (7,  "Honi",     "Sheep",   "羊", "🐑"),
    (8,  "Bich",     "Monkey",  "猴", "🐒"),
    (9,  "Tahia",    "Rooster", "雞", "🐓"),
    (10, "Nokhoi",   "Dog",     "狗", "🐕"),
    (11, "Gakhai",   "Pig",     "豬", "🐖"),
]

# ============================================================
# 常量 (Constants) — 五行 (Elements)
# ============================================================

# Five Elements: (index, Mongolian, English, Chinese, color, emoji)
ELEMENTS = [
    (0, "Mod",    "Wood",  "木", "#228B22", "🌳"),
    (1, "Gal",    "Fire",  "火", "#DC143C", "🔥"),
    (2, "Shoroo", "Earth", "土", "#DAA520", "🌍"),
    (3, "Temür",  "Metal", "金", "#C0C0C0", "⚙️"),
    (4, "Us",     "Water", "水", "#1E90FF", "💧"),
]

# ============================================================
# 陰陽 (Yin-Yang / Erh-Eme)
# ============================================================

# (index, Mongolian, English, Chinese, symbol)
POLARITIES = [
    (0, "Er",  "Yang", "陽", "☀️"),
    (1, "Eme", "Yin",  "陰", "🌙"),
]

# ============================================================
# 五行相生相剋 (Element Interactions)
# ============================================================

# 相生 (Generating / Productive Cycle): 木→火→土→金→水→木
GENERATING_CYCLE = {0: 1, 1: 2, 2: 3, 3: 4, 4: 0}

# 相剋 (Overcoming / Destructive Cycle): 木→土→水→火→金→木
OVERCOMING_CYCLE = {0: 2, 2: 4, 4: 1, 1: 3, 3: 0}

# Element relationship descriptions (Chinese + English)
ELEMENT_RELATIONS = {
    "generating": "相生 (Generating / Züin Tüshee)",
    "overcoming": "相剋 (Overcoming / Darakh Tüshee)",
    "same":       "同行 (Same Element)",
    "weakening":  "洩氣 (Weakening / Sulrakh)",
    "resisting":  "耗氣 (Resisting / Tsereg)",
}

# ============================================================
# 60 年循環 (Sexagenary Cycle / Jaran Jiliin Ergiilt)
# 從 1924 年 (木鼠陽年) 開始的循環
# ============================================================

# Reference: 1924 = Wood Rat Yang (cycle year 0)
CYCLE_BASE_YEAR = 1924

# 12 months Mongolian names
MONTH_ANIMALS = [
    "虎月 (Bar Sar / Tiger Month)",    # Month 1
    "兔月 (Tuulai Sar / Rabbit Month)",  # Month 2
    "龍月 (Luu Sar / Dragon Month)",    # Month 3
    "蛇月 (Mogoi Sar / Snake Month)",   # Month 4
    "馬月 (Mori Sar / Horse Month)",    # Month 5
    "羊月 (Honi Sar / Sheep Month)",    # Month 6
    "猴月 (Bich Sar / Monkey Month)",   # Month 7
    "雞月 (Tahia Sar / Rooster Month)", # Month 8
    "狗月 (Nokhoi Sar / Dog Month)",    # Month 9
    "豬月 (Gakhai Sar / Pig Month)",    # Month 10
    "鼠月 (Hulgana Sar / Rat Month)",   # Month 11
    "牛月 (Ükher Sar / Ox Month)",      # Month 12
]

# Day animal cycle (repeats every 12 days from a reference)
# Reference: Jan 1, 1924 = Rat day (index 0) — simplified approximation

# ============================================================
# 障礙年 (Obstacle Years / Jiltei Jil)
# 每 12 年一輪的障礙年：9歲、21歲、33歲、45歲、57歲、69歲、81歲、93歲
# 另有特殊障礙年取決於生肖
# ============================================================

# General obstacle ages (every 12 years starting from 9)
GENERAL_OBSTACLE_AGES = [9, 21, 33, 45, 57, 69, 81, 93]

# Special obstacle relationships: animal -> list of challenging animal years
# When your birth animal meets these animals in the current year
ANIMAL_CONFLICTS = {
    0:  [6],   # Rat ↔ Horse
    1:  [7],   # Ox ↔ Sheep
    2:  [8],   # Tiger ↔ Monkey
    3:  [9],   # Rabbit ↔ Rooster
    4:  [10],  # Dragon ↔ Dog
    5:  [11],  # Snake ↔ Pig
    6:  [0],   # Horse ↔ Rat
    7:  [1],   # Sheep ↔ Ox
    8:  [2],   # Monkey ↔ Tiger
    9:  [3],   # Rooster ↔ Rabbit
    10: [4],   # Dog ↔ Dragon
    11: [5],   # Pig ↔ Snake
}

# Harmonious animal pairs (Three Harmonies / Gurvan Naiz)
ANIMAL_HARMONIES = {
    0:  [4, 8],   # Rat + Dragon + Monkey (Water trine)
    1:  [5, 9],   # Ox + Snake + Rooster (Metal trine)
    2:  [6, 10],  # Tiger + Horse + Dog (Fire trine)
    3:  [7, 11],  # Rabbit + Sheep + Pig (Wood trine)
    4:  [0, 8],   # Dragon + Rat + Monkey
    5:  [1, 9],   # Snake + Ox + Rooster
    6:  [2, 10],  # Horse + Tiger + Dog
    7:  [3, 11],  # Sheep + Rabbit + Pig
    8:  [0, 4],   # Monkey + Rat + Dragon
    9:  [1, 5],   # Rooster + Ox + Snake
    10: [2, 6],   # Dog + Tiger + Horse
    11: [3, 7],   # Pig + Rabbit + Sheep
}

# ============================================================
# 擇吉 (Auspicious Timing) — 活動類型與適宜/忌避規則
# ============================================================

# Activity types: (key, Chinese, English, Mongolian)
ACTIVITY_TYPES = [
    ("marriage",    "結婚",   "Marriage",      "Gerlekh"),
    ("travel",      "出行",   "Travel",        "Ayalal"),
    ("building",    "建屋/動土", "Building",    "Barilag"),
    ("medical",     "醫療",   "Medical",       "Emchilgee"),
    ("ceremony",    "祭祀/儀式", "Ceremony",    "Zan Üil"),
    ("funeral",     "葬禮",   "Funeral",       "Oršuulga"),
    ("business",    "商業/交易", "Business",    "Naimaany"),
    ("study",       "學習/開學", "Study",       "Surguuli"),
]

# Auspicious animal-day combinations for each activity
# key -> set of favorable day-animal indices
ACTIVITY_FAVORABLE_DAYS = {
    "marriage":  {0, 3, 4, 7, 8, 11},   # Rat, Rabbit, Dragon, Sheep, Monkey, Pig
    "travel":    {2, 6, 10},              # Tiger, Horse, Dog
    "building":  {1, 4, 5, 9},            # Ox, Dragon, Snake, Rooster
    "medical":   {3, 7, 11},              # Rabbit, Sheep, Pig
    "ceremony":  {0, 4, 8},               # Rat, Dragon, Monkey
    "funeral":   {1, 5, 9},               # Ox, Snake, Rooster
    "business":  {0, 2, 4, 6, 8, 10},     # Yang animals
    "study":     {3, 7, 8, 11},            # Rabbit, Sheep, Monkey, Pig
}

# Inauspicious animal-day combinations for each activity
ACTIVITY_UNFAVORABLE_DAYS = {
    "marriage":  {2, 5, 6, 9},    # Tiger, Snake, Horse, Rooster
    "travel":    {1, 5, 7, 11},   # Ox, Snake, Sheep, Pig
    "building":  {0, 6, 10},      # Rat, Horse, Dog
    "medical":   {2, 5, 8},       # Tiger, Snake, Monkey
    "ceremony":  {5, 9, 11},      # Snake, Rooster, Pig
    "funeral":   {0, 3, 6},       # Rat, Rabbit, Horse
    "business":  {5, 9, 11},      # Snake, Rooster, Pig
    "study":     {2, 5, 6, 9},    # Tiger, Snake, Horse, Rooster
}

# Nahas (障礙日 / inauspicious days) — days to avoid major activities
# Based on the weekday (0=Mon .. 6=Sun)
NAHAS_WEEKDAYS = {
    1: "火曜日 (Tuesday) — 忌婚嫁、出行 / Avoid marriage & travel",
    5: "土曜日 (Saturday) — 忌動土、建屋 / Avoid building & construction",
}

# ============================================================
# 生肖性格描述
# ============================================================

ANIMAL_PERSONALITIES = {
    0:  ("聰明機智，善於理財，適應力強。",
         "Intelligent, resourceful, adaptable."),
    1:  ("勤勉踏實，忠誠可靠，意志堅定。",
         "Diligent, reliable, determined."),
    2:  ("勇敢自信，領導力強，熱情活力。",
         "Brave, confident, passionate leader."),
    3:  ("溫和善良，心思細膩，藝術天賦。",
         "Gentle, kind, artistic."),
    4:  ("氣宇非凡，有魄力，充滿活力。",
         "Majestic, powerful, energetic."),
    5:  ("深沉智慧，直覺敏銳，善於思考。",
         "Wise, intuitive, thoughtful."),
    6:  ("自由奔放，熱情開朗，行動力強。",
         "Free-spirited, enthusiastic, active."),
    7:  ("溫順和平，富同情心，有藝術感。",
         "Peaceful, compassionate, artistic."),
    8:  ("聰慧機靈，多才多藝，好奇心強。",
         "Clever, versatile, curious."),
    9:  ("勤奮踏實，觀察敏銳，守時守信。",
         "Hardworking, observant, punctual."),
    10: ("忠誠正直，勇敢無畏，重情重義。",
         "Loyal, honest, brave."),
    11: ("寬厚仁慈，樂觀豁達，享受生活。",
         "Generous, optimistic, enjoys life."),
}

# Element personality modifiers
ELEMENT_PERSONALITIES = {
    0: ("木：仁慈、成長、創意。",
        "Wood: Benevolent, growth-oriented, creative."),
    1: ("火：熱情、果斷、領導。",
        "Fire: Passionate, decisive, leadership."),
    2: ("土：穩重、務實、守信。",
        "Earth: Stable, practical, trustworthy."),
    3: ("金：堅毅、正義、精確。",
        "Metal: Resolute, just, precise."),
    4: ("水：智慧、靈活、深沉。",
        "Water: Wise, flexible, profound."),
}


# ============================================================
# 資料類別 (Dataclasses)
# ============================================================

@dataclass
class ZurkhaiAnimal:
    """生肖資料"""
    index: int
    name_mn: str       # Mongolian name
    name_en: str       # English name
    name_cn: str       # Chinese name
    emoji: str
    personality_cn: str
    personality_en: str


@dataclass
class ZurkhaiElement:
    """五行資料"""
    index: int
    name_mn: str
    name_en: str
    name_cn: str
    color: str
    emoji: str
    personality_cn: str
    personality_en: str


@dataclass
class ZurkhaiPolarity:
    """陰陽"""
    index: int
    name_mn: str
    name_en: str
    name_cn: str
    symbol: str


@dataclass
class ZurkhaiDayInfo:
    """日期的祖爾海資訊"""
    date: date
    animal: ZurkhaiAnimal
    element: ZurkhaiElement
    polarity: ZurkhaiPolarity
    month_name: str
    is_nahas: bool
    nahas_note: str


@dataclass
class ZurkhaiAuspicious:
    """擇吉結果"""
    activity_key: str
    activity_cn: str
    activity_en: str
    activity_mn: str
    is_favorable: bool
    is_unfavorable: bool
    note_cn: str
    note_en: str


@dataclass
class ZurkhaiChart:
    """祖爾海排盤結果"""
    # Input parameters
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str

    # Birth year attributes
    birth_animal: ZurkhaiAnimal
    birth_element: ZurkhaiElement
    birth_polarity: ZurkhaiPolarity
    cycle_year: int           # Position in 60-year cycle (0-59)

    # Current year attributes
    current_animal: ZurkhaiAnimal
    current_element: ZurkhaiElement
    current_polarity: ZurkhaiPolarity
    current_cycle_year: int

    # Day info
    day_info: ZurkhaiDayInfo

    # Element interactions
    year_element_relation: str     # Relation key (generating, overcoming, etc.)
    year_element_relation_cn: str  # Chinese description
    year_element_relation_en: str  # English description

    # Animal relationships
    is_conflict_year: bool
    is_harmony_year: bool
    conflict_note_cn: str
    conflict_note_en: str

    # Obstacle year check
    age: int
    is_obstacle_age: bool
    obstacle_note_cn: str
    obstacle_note_en: str

    # Auspicious timing for the day
    auspicious_results: list  # list[ZurkhaiAuspicious]

    # Overall day assessment
    day_rating: str           # "吉" / "凶" / "平"
    day_rating_en: str        # "Auspicious" / "Inauspicious" / "Neutral"


# ============================================================
# 計算輔助函數 (Calculation Helpers)
# ============================================================

def _get_animal(year: int) -> ZurkhaiAnimal:
    """根據年份計算生肖。"""
    idx = (year - CYCLE_BASE_YEAR) % 12
    a = ANIMALS[idx]
    p_cn, p_en = ANIMAL_PERSONALITIES[idx]
    return ZurkhaiAnimal(
        index=a[0], name_mn=a[1], name_en=a[2],
        name_cn=a[3], emoji=a[4],
        personality_cn=p_cn, personality_en=p_en,
    )


def _get_element(year: int) -> ZurkhaiElement:
    """根據年份計算五行元素。每個元素管兩年（陽年+陰年）。"""
    idx = ((year - CYCLE_BASE_YEAR) // 2) % 5
    e = ELEMENTS[idx]
    p_cn, p_en = ELEMENT_PERSONALITIES[idx]
    return ZurkhaiElement(
        index=e[0], name_mn=e[1], name_en=e[2],
        name_cn=e[3], color=e[4], emoji=e[5],
        personality_cn=p_cn, personality_en=p_en,
    )


def _get_polarity(year: int) -> ZurkhaiPolarity:
    """根據年份計算陰陽。偶數年=陽，奇數年=陰。"""
    idx = (year - CYCLE_BASE_YEAR) % 2
    p = POLARITIES[idx]
    return ZurkhaiPolarity(
        index=p[0], name_mn=p[1], name_en=p[2],
        name_cn=p[3], symbol=p[4],
    )


def _get_cycle_year(year: int) -> int:
    """計算 60 年循環中的位置 (0-59)。"""
    return (year - CYCLE_BASE_YEAR) % 60


def _get_day_animal(d: date) -> ZurkhaiAnimal:
    """計算某日的日生肖。"""
    # Convert to a simple day count from reference
    ref = date(1924, 1, 1)
    delta = (d - ref).days
    idx = delta % 12
    a = ANIMALS[idx]
    p_cn, p_en = ANIMAL_PERSONALITIES[idx]
    return ZurkhaiAnimal(
        index=a[0], name_mn=a[1], name_en=a[2],
        name_cn=a[3], emoji=a[4],
        personality_cn=p_cn, personality_en=p_en,
    )


def _get_day_element(d: date) -> ZurkhaiElement:
    """計算某日的日元素。每 2 天換一個元素。"""
    ref = date(1924, 1, 1)
    delta = (d - ref).days
    idx = (delta // 2) % 5
    e = ELEMENTS[idx]
    p_cn, p_en = ELEMENT_PERSONALITIES[idx]
    return ZurkhaiElement(
        index=e[0], name_mn=e[1], name_en=e[2],
        name_cn=e[3], color=e[4], emoji=e[5],
        personality_cn=p_cn, personality_en=p_en,
    )


def _get_day_polarity(d: date) -> ZurkhaiPolarity:
    """計算某日的陰陽。"""
    ref = date(1924, 1, 1)
    delta = (d - ref).days
    idx = delta % 2
    p = POLARITIES[idx]
    return ZurkhaiPolarity(
        index=p[0], name_mn=p[1], name_en=p[2],
        name_cn=p[3], symbol=p[4],
    )


def _get_month_name(month: int) -> str:
    """獲取蒙古月份名稱（月份 1-12）。"""
    return MONTH_ANIMALS[(month - 1) % 12]


def _check_nahas(d: date) -> tuple[bool, str]:
    """檢查是否為障礙日 (Nahas)。"""
    weekday = d.weekday()  # 0=Monday
    if weekday in NAHAS_WEEKDAYS:
        return True, NAHAS_WEEKDAYS[weekday]
    return False, ""


def _get_element_relation(birth_elem_idx: int, current_elem_idx: int) -> tuple[str, str, str]:
    """計算兩個元素之間的關係。

    Returns:
        (relation_key, Chinese description, English description)
    """
    if birth_elem_idx == current_elem_idx:
        return "same", "同行 — 元素相同，力量穩固", "Same element — stable energy"

    if GENERATING_CYCLE.get(birth_elem_idx) == current_elem_idx:
        b_cn = ELEMENTS[birth_elem_idx][3]
        c_cn = ELEMENTS[current_elem_idx][3]
        return ("generating",
                f"相生 — {b_cn}生{c_cn}，有利發展",
                f"Generating — {ELEMENTS[birth_elem_idx][2]} produces "
                f"{ELEMENTS[current_elem_idx][2]}, favorable")

    if GENERATING_CYCLE.get(current_elem_idx) == birth_elem_idx:
        c_cn = ELEMENTS[current_elem_idx][3]
        b_cn = ELEMENTS[birth_elem_idx][3]
        return ("weakening",
                f"洩氣 — {c_cn}生{b_cn}，能量洩漏需留意",
                f"Weakening — energy draining, be cautious")

    if OVERCOMING_CYCLE.get(birth_elem_idx) == current_elem_idx:
        b_cn = ELEMENTS[birth_elem_idx][3]
        c_cn = ELEMENTS[current_elem_idx][3]
        return ("overcoming",
                f"相剋 — {b_cn}剋{c_cn}，主動有力但須謹慎",
                f"Overcoming — active but use caution")

    # current overcomes birth
    c_cn = ELEMENTS[current_elem_idx][3]
    b_cn = ELEMENTS[birth_elem_idx][3]
    return ("resisting",
            f"耗氣 — {c_cn}剋{b_cn}，受外力壓制，宜守不宜攻",
            f"Resisting — suppressed by external force, be defensive")


def _check_conflict(birth_animal_idx: int, current_animal_idx: int) -> tuple[bool, str, str]:
    """檢查生肖衝突 (Six Clashes / Zurgaan Setgel)。"""
    if current_animal_idx in ANIMAL_CONFLICTS.get(birth_animal_idx, []):
        b = ANIMALS[birth_animal_idx]
        c = ANIMALS[current_animal_idx]
        return (True,
                f"沖犯 — {b[3]}({b[2]})沖{c[3]}({c[2]})，"
                "此年宜謹慎，避免重大變動。",
                f"Conflict — {b[2]} clashes with {c[2]}. "
                "Exercise caution this year.")
    return False, "", ""


def _check_harmony(birth_animal_idx: int, current_animal_idx: int) -> tuple[bool, str, str]:
    """檢查生肖三合 (Three Harmonies / Gurvan Naiz)。"""
    if current_animal_idx in ANIMAL_HARMONIES.get(birth_animal_idx, []):
        b = ANIMALS[birth_animal_idx]
        c = ANIMALS[current_animal_idx]
        return (True,
                f"三合 — {b[3]}({b[2]})與{c[3]}({c[2]})三合，"
                "此年運勢順遂，適合發展。",
                f"Harmony — {b[2]} and {c[2]} form a trine. "
                "A favorable year for progress.")
    return False, "", ""


def _check_obstacle_age(birth_year: int, current_year: int) -> tuple[int, bool, str, str]:
    """檢查是否為障礙年齡。蒙古傳統以虛歲計算。"""
    age = current_year - birth_year + 1  # 虛歲
    is_obstacle = age in GENERAL_OBSTACLE_AGES
    if is_obstacle:
        return (age, True,
                f"障礙年 — 今年虛歲 {age} 為障礙年 (Jiltei Jil)，"
                "宜多行善事、誦經祈福，避免冒險。",
                f"Obstacle Year — Age {age} (Mongolian reckoning) is an "
                "obstacle year. Perform meritorious deeds and avoid risks.")
    return age, False, "", ""


def _compute_auspicious(day_animal_idx: int) -> list[ZurkhaiAuspicious]:
    """計算當日各項活動的吉凶。"""
    results = []
    for act_key, act_cn, act_en, act_mn in ACTIVITY_TYPES:
        fav = day_animal_idx in ACTIVITY_FAVORABLE_DAYS.get(act_key, set())
        unfav = day_animal_idx in ACTIVITY_UNFAVORABLE_DAYS.get(act_key, set())

        if fav:
            note_cn = f"✅ 今日{ANIMALS[day_animal_idx][3]}日適合{act_cn}"
            note_en = (f"✅ {ANIMALS[day_animal_idx][2]} day is favorable "
                       f"for {act_en.lower()}")
        elif unfav:
            note_cn = f"❌ 今日{ANIMALS[day_animal_idx][3]}日不宜{act_cn}"
            note_en = (f"❌ {ANIMALS[day_animal_idx][2]} day is unfavorable "
                       f"for {act_en.lower()}")
        else:
            note_cn = f"⚖️ 今日{ANIMALS[day_animal_idx][3]}日對{act_cn}無特殊影響"
            note_en = (f"⚖️ {ANIMALS[day_animal_idx][2]} day is neutral "
                       f"for {act_en.lower()}")

        results.append(ZurkhaiAuspicious(
            activity_key=act_key,
            activity_cn=act_cn,
            activity_en=act_en,
            activity_mn=act_mn,
            is_favorable=fav,
            is_unfavorable=unfav,
            note_cn=note_cn,
            note_en=note_en,
        ))
    return results


def _compute_day_rating(day_animal_idx: int, is_nahas: bool,
                        auspicious_results: list) -> tuple[str, str]:
    """綜合評估當日吉凶。"""
    if is_nahas:
        return "凶", "Inauspicious"

    fav_count = sum(1 for r in auspicious_results if r.is_favorable)
    unfav_count = sum(1 for r in auspicious_results if r.is_unfavorable)

    if fav_count > unfav_count + 2:
        return "吉", "Auspicious"
    elif unfav_count > fav_count + 2:
        return "凶", "Inauspicious"
    else:
        return "平", "Neutral"


# ============================================================
# 主要計算函數 (Main Computation)
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_zurkhai_chart(year, month, day, hour, minute,
                          timezone, latitude, longitude,
                          location_name="") -> ZurkhaiChart:
    """計算蒙古祖爾海排盤。

    Args:
        year, month, day: 出生日期（公曆）
        hour, minute: 出生時間
        timezone: 時區 (UTC offset)
        latitude, longitude: 出生地經緯度
        location_name: 地點名稱

    Returns:
        ZurkhaiChart 排盤結果
    """
    # Current date for comparison
    today = date.today()
    current_year = today.year

    # Birth year attributes
    birth_animal = _get_animal(year)
    birth_element = _get_element(year)
    birth_polarity = _get_polarity(year)
    cycle_year = _get_cycle_year(year)

    # Current year attributes
    current_animal = _get_animal(current_year)
    current_element = _get_element(current_year)
    current_polarity = _get_polarity(current_year)
    current_cycle_year = _get_cycle_year(current_year)

    # Day info
    birth_date = date(year, month, day)
    day_animal = _get_day_animal(birth_date)
    day_element = _get_day_element(birth_date)
    day_polarity = _get_day_polarity(birth_date)
    month_name = _get_month_name(month)
    is_nahas, nahas_note = _check_nahas(birth_date)

    day_info = ZurkhaiDayInfo(
        date=birth_date,
        animal=day_animal,
        element=day_element,
        polarity=day_polarity,
        month_name=month_name,
        is_nahas=is_nahas,
        nahas_note=nahas_note,
    )

    # Element interaction between birth & current year
    rel_key, rel_cn, rel_en = _get_element_relation(
        birth_element.index, current_element.index)

    # Animal conflict/harmony
    is_conflict, conflict_cn, conflict_en = _check_conflict(
        birth_animal.index, current_animal.index)
    is_harmony = False
    harmony_cn, harmony_en = "", ""
    if not is_conflict:
        is_harmony, harmony_cn, harmony_en = _check_harmony(
            birth_animal.index, current_animal.index)
    conflict_note_cn = conflict_cn or harmony_cn
    conflict_note_en = conflict_en or harmony_en

    # Obstacle age
    age, is_obstacle, obstacle_cn, obstacle_en = _check_obstacle_age(
        year, current_year)

    # Auspicious timing for today
    today_animal = _get_day_animal(today)
    auspicious_results = _compute_auspicious(today_animal.index)

    # Overall day rating
    today_nahas, _ = _check_nahas(today)
    day_rating, day_rating_en = _compute_day_rating(
        today_animal.index, today_nahas, auspicious_results)

    return ZurkhaiChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
        birth_animal=birth_animal,
        birth_element=birth_element,
        birth_polarity=birth_polarity,
        cycle_year=cycle_year,
        current_animal=current_animal,
        current_element=current_element,
        current_polarity=current_polarity,
        current_cycle_year=current_cycle_year,
        day_info=day_info,
        year_element_relation=rel_key,
        year_element_relation_cn=rel_cn,
        year_element_relation_en=rel_en,
        is_conflict_year=is_conflict,
        is_harmony_year=is_harmony,
        conflict_note_cn=conflict_note_cn,
        conflict_note_en=conflict_note_en,
        age=age,
        is_obstacle_age=is_obstacle,
        obstacle_note_cn=obstacle_cn,
        obstacle_note_en=obstacle_en,
        auspicious_results=auspicious_results,
        day_rating=day_rating,
        day_rating_en=day_rating_en,
    )


# ============================================================
# Streamlit 渲染函數 (Rendering Functions)
# ============================================================

def render_zurkhai_chart(chart: ZurkhaiChart, after_chart_hook=None) -> None:
    """渲染蒙古祖爾海排盤 Streamlit 介面。"""
    _render_zurkhai_wheel(chart)
    st.divider()
    _render_element_balance(chart)
    if after_chart_hook:
        after_chart_hook()
    st.divider()
    _render_info(chart)
    st.divider()
    _render_year_forecast(chart)
    st.divider()
    _render_auspicious_table(chart)
    st.divider()
    _render_sixty_year_table(chart)
    st.divider()
    _render_element_cycle_diagram()
    st.divider()
    _render_history()
    st.divider()
    _render_cultural_note()


# --- 星盤圖 (Star Chart / Wheel) ---

# Element color map for the 12 animals in the 60-year cycle.
# Each animal position (0-11) in the cycle has an associated element color
# determined by the cycle year element.
_WHEEL_ELEMENT_COLORS = [e[4] for e in ELEMENTS]  # Wood, Fire, Earth, Metal, Water


def _build_zurkhai_wheel_svg(chart: ZurkhaiChart) -> str:
    """Build an SVG circular star chart for the Zurkhai system.

    The wheel displays:
    - Outer ring: 12 animal signs arranged clockwise, starting from Rat at top
    - Middle ring: element color + polarity for each animal position
    - Birth year animal highlighted with a gold border
    - Current year animal highlighted with a cyan marker
    - Conflict (沖) / Harmony (合) relationship lines
    - Center: birth year element and animal summary

    Returns:
        SVG markup string.
    """
    cx, cy = 250, 250       # center
    r_outer = 230            # outer ring radius
    r_mid = 180              # middle ring (element band)
    r_inner = 130            # inner boundary
    r_text = 205             # animal text radius
    r_elem = 155             # element text radius
    n = 12                   # 12 animals
    slice_angle = 360 / n    # 30° per slice

    birth_idx = chart.birth_animal.index
    current_idx = chart.current_animal.index

    # Start SVG
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 500 500" '
        'style="width:100%;max-width:500px;margin:auto;display:block;" '
        'font-family="sans-serif">',
        # Background
        '<rect width="500" height="500" rx="16" '
        'fill="#1a1a2e" stroke="#333" stroke-width="1"/>',
    ]

    # --- Draw 12 segments ---
    for i in range(n):
        # Angles: 0° = top (12 o'clock), clockwise
        # SVG angles are measured from 3 o'clock, so offset by -90°
        start_deg = i * slice_angle - 90 - slice_angle / 2
        end_deg = start_deg + slice_angle
        start_rad = math.radians(start_deg)
        end_rad = math.radians(end_deg)

        # Arc endpoints for outer ring
        ox1 = cx + r_outer * math.cos(start_rad)
        oy1 = cy + r_outer * math.sin(start_rad)
        ox2 = cx + r_outer * math.cos(end_rad)
        oy2 = cy + r_outer * math.sin(end_rad)
        # Arc endpoints for middle ring
        mx1 = cx + r_mid * math.cos(start_rad)
        my1 = cy + r_mid * math.sin(start_rad)
        mx2 = cx + r_mid * math.cos(end_rad)
        my2 = cy + r_mid * math.sin(end_rad)
        # Arc endpoints for inner ring
        ix1 = cx + r_inner * math.cos(start_rad)
        iy1 = cy + r_inner * math.sin(start_rad)
        ix2 = cx + r_inner * math.cos(end_rad)
        iy2 = cy + r_inner * math.sin(end_rad)

        large_arc = 0  # Each slice is 30° < 180°

        # Compute element for a year that has animal index i
        # nearest to the birth year
        year_for_animal = chart.year + (i - birth_idx) % 12
        anim_elem_idx = ((year_for_animal - CYCLE_BASE_YEAR) // 2) % 5
        elem_color = _WHEEL_ELEMENT_COLORS[anim_elem_idx]

        # Outer ring segment (animal names)
        is_birth = (i == birth_idx)
        is_current = (i == current_idx)
        fill_outer = f"{elem_color}33"
        if is_birth:
            fill_outer = f"{elem_color}66"
        stroke_outer = "gold" if is_birth else (
            "#00e5ff" if is_current else "#444")
        sw_outer = "3" if is_birth or is_current else "1"

        # Outer ring path: arc from ox1,oy1 to ox2,oy2, lines to mx2,my2
        # and arc back to mx1,my1
        parts.append(
            f'<path d="M{ox1:.1f},{oy1:.1f} '
            f'A{r_outer},{r_outer} 0 {large_arc} 1 {ox2:.1f},{oy2:.1f} '
            f'L{mx2:.1f},{my2:.1f} '
            f'A{r_mid},{r_mid} 0 {large_arc} 0 {mx1:.1f},{my1:.1f} Z" '
            f'fill="{fill_outer}" stroke="{stroke_outer}" '
            f'stroke-width="{sw_outer}"/>'
        )

        # Middle ring path (element band): arc from mx1 to mx2, line to ix2,
        # arc back to ix1
        fill_mid = f"{elem_color}44"
        parts.append(
            f'<path d="M{mx1:.1f},{my1:.1f} '
            f'A{r_mid},{r_mid} 0 {large_arc} 1 {mx2:.1f},{my2:.1f} '
            f'L{ix2:.1f},{iy2:.1f} '
            f'A{r_inner},{r_inner} 0 {large_arc} 0 {ix1:.1f},{iy1:.1f} Z" '
            f'fill="{fill_mid}" stroke="#555" stroke-width="0.5"/>'
        )

        # Animal emoji + name text
        mid_deg = i * slice_angle - 90
        mid_rad = math.radians(mid_deg)
        tx = cx + r_text * math.cos(mid_rad)
        ty = cy + r_text * math.sin(mid_rad)
        a_info = ANIMALS[i]
        emoji = a_info[4]
        cn_name = a_info[3]

        # Birth / current markers
        marker = ""
        if is_birth:
            marker = "🎂"
        elif is_current:
            marker = "📅"

        parts.append(
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" font-size="16" fill="white">'
            f'{emoji}</text>'
        )
        # Chinese name below emoji
        ty2 = ty + 16
        parts.append(
            f'<text x="{tx:.1f}" y="{ty2:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" font-size="9" fill="#ddd">'
            f'{cn_name}{marker}</text>'
        )

        # Element text in middle ring
        ex = cx + r_elem * math.cos(mid_rad)
        ey = cy + r_elem * math.sin(mid_rad)
        elem_info = ELEMENTS[anim_elem_idx]
        elem_emoji = elem_info[5]
        elem_cn = elem_info[3]
        parts.append(
            f'<text x="{ex:.1f}" y="{ey:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" font-size="10" '
            f'fill="{elem_color}">'
            f'{elem_emoji}{elem_cn}</text>'
        )

    # --- Conflict / Harmony lines ---
    # Draw conflict line (red dashed) if exists
    if chart.is_conflict_year:
        _add_relation_line(parts, cx, cy, r_inner - 10,
                           birth_idx, current_idx, n, "#ff4444", "4,3")
    # Draw harmony line (green) if exists
    if chart.is_harmony_year:
        _add_relation_line(parts, cx, cy, r_inner - 10,
                           birth_idx, current_idx, n, "#44ff88", "")

    # --- Center circle ---
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="75" '
        f'fill="#1a1a2e" stroke="#666" stroke-width="1.5"/>'
    )

    # Center content: birth year info
    a = chart.birth_animal
    e = chart.birth_element
    p = chart.birth_polarity

    parts.append(
        f'<text x="{cx}" y="{cy - 35}" text-anchor="middle" '
        f'font-size="28" fill="white">{a.emoji}</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy - 10}" text-anchor="middle" '
        f'font-size="14" fill="white" font-weight="bold">'
        f'{p.name_cn}{e.name_cn}{a.name_cn}</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" '
        f'font-size="10" fill="#aaa">'
        f'{p.name_en} {e.name_en} {a.name_en}</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy + 24}" text-anchor="middle" '
        f'font-size="10" fill="#888">'
        f'{p.name_mn} {e.name_mn} {a.name_mn}</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy + 42}" text-anchor="middle" '
        f'font-size="10" fill="{e.color}">'
        f'{e.emoji} {chart.year} · {p.symbol}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


def _add_relation_line(parts: list, cx: float, cy: float, r: float,
                       idx1: int, idx2: int, n: int,
                       color: str, dash: str) -> None:
    """Add a line between two animal positions on the wheel."""
    slice_angle = 360 / n
    rad1 = math.radians(idx1 * slice_angle - 90)
    rad2 = math.radians(idx2 * slice_angle - 90)
    x1 = cx + r * math.cos(rad1)
    y1 = cy + r * math.sin(rad1)
    x2 = cx + r * math.cos(rad2)
    y2 = cy + r * math.sin(rad2)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    parts.append(
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
        f'x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="2" opacity="0.7"{dash_attr}/>'
    )


def _render_zurkhai_wheel(chart: ZurkhaiChart) -> None:
    """渲染祖爾海星盤圖 (Zurkhai Star Chart Wheel)。"""
    st.subheader("🔮 祖爾海星盤 / Zurkhai Star Chart")

    svg = _build_zurkhai_wheel_svg(chart)
    st.markdown(svg, unsafe_allow_html=True)

    # Legend below the chart
    legend_parts = ["🎂 = 出生年 (Birth Year)", "📅 = 今年 (Current Year)"]
    if chart.is_conflict_year:
        legend_parts.append(
            '<span style="color:#ff4444;">⚡ 紅色虛線 = 沖 (Conflict)</span>')
    if chart.is_harmony_year:
        legend_parts.append(
            '<span style="color:#44ff88;">✨ 綠色線 = 三合 (Harmony)</span>')
    st.markdown(
        '<div style="text-align:center;font-size:12px;color:#aaa;">'
        + " &nbsp;|&nbsp; ".join(legend_parts)
        + "</div>",
        unsafe_allow_html=True,
    )


# --- 基本資料 ---
def _render_info(chart: ZurkhaiChart) -> None:
    """渲染基本排盤資訊。"""
    st.subheader("📋 祖爾海排盤基本資料 / Zurkhai Chart Info")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎂 出生資料 / Birth Data")
        a = chart.birth_animal
        e = chart.birth_element
        p = chart.birth_polarity
        st.write(f"**出生日期：** {chart.year}/{chart.month}/{chart.day} "
                 f"{chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**出生地點：** {chart.location_name} "
                 f"({chart.latitude:.2f}°, {chart.longitude:.2f}°)")
        st.write(f"**時區：** UTC{chart.timezone:+.1f}")

        st.markdown("---")
        st.markdown("#### 🐾 出生年生肖 / Birth Year Animal")
        st.markdown(
            f'<div style="background:{e.color}22;padding:12px;'
            f'border-radius:8px;border:2px solid {e.color};">'
            f'<span style="font-size:2em;">{a.emoji}</span> '
            f'<b>{p.name_cn}{e.name_cn}{a.name_cn}</b><br>'
            f'{p.symbol} {p.name_en} {e.emoji} {e.name_en} '
            f'{a.name_en}<br>'
            f'<small>🇲🇳 {p.name_mn} {e.name_mn} {a.name_mn}</small>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.write(f"**60年循環位置：** 第 {chart.cycle_year + 1} 年 / "
                 f"Year {chart.cycle_year + 1} of 60")

    with col2:
        st.markdown("#### 🌟 性格特質 / Personality")
        st.markdown(
            f"**{a.emoji} {a.name_cn}（{a.name_mn}）性格：**\n\n"
            f"- {a.personality_cn}\n"
            f"- {a.personality_en}"
        )
        st.markdown(
            f"**{e.emoji} {e.name_cn}行（{e.name_mn}）特質：**\n\n"
            f"- {e.personality_cn}\n"
            f"- {e.personality_en}"
        )
        st.markdown(
            f"**{p.symbol} {p.name_cn}（{p.name_mn}）屬性：**\n\n"
            f"- {'外向、主動、積極 / Outward, active, assertive' if p.index == 0 else '內斂、被動、包容 / Inward, receptive, nurturing'}"
        )

        st.markdown("---")
        st.markdown("#### 📅 出生日資訊 / Birth Day Info")
        d = chart.day_info
        st.write(f"**日生肖：** {d.animal.emoji} {d.animal.name_cn} "
                 f"({d.animal.name_mn})")
        st.write(f"**日五行：** {d.element.emoji} {d.element.name_cn} "
                 f"({d.element.name_mn})")
        st.write(f"**日陰陽：** {d.polarity.symbol} {d.polarity.name_cn}")
        st.write(f"**月份：** {d.month_name}")
        if d.is_nahas:
            st.warning(f"⚠️ 障礙日 (Nahas): {d.nahas_note}")


# --- 五行平衡 ---
def _render_element_balance(chart: ZurkhaiChart) -> None:
    """渲染五行元素平衡與相生相剋圖。"""
    st.subheader("⚖️ 五行元素平衡 / Five Element Balance")

    be = chart.birth_element
    ce = chart.current_element

    # Element relation display
    st.markdown(
        f"**出生年元素：** {be.emoji} {be.name_cn} ({be.name_mn} / "
        f"{be.name_en})")
    st.markdown(
        f"**今年元素：** {ce.emoji} {ce.name_cn} ({ce.name_mn} / "
        f"{ce.name_en})")
    st.markdown(
        f"**元素關係：** {chart.year_element_relation_cn}")
    st.markdown(
        f"*{chart.year_element_relation_en}*")

    # Visual element bar
    cols = st.columns(5)
    for i, (idx, mn, en, cn, color, emoji) in enumerate(ELEMENTS):
        with cols[i]:
            is_birth = (idx == be.index)
            is_current = (idx == ce.index)
            label_parts = []
            if is_birth:
                label_parts.append("🎂出生")
            if is_current:
                label_parts.append("📅今年")
            label = " / ".join(label_parts) if label_parts else "—"
            border = f"border:3px solid gold;" if is_birth or is_current else ""
            st.markdown(
                f'<div style="background:{color}22;padding:10px;'
                f'border-radius:8px;text-align:center;{border}">'
                f'<span style="font-size:1.5em;">{emoji}</span><br>'
                f'<b>{cn}</b><br>{en}<br>'
                f'<small>{mn}</small><br>'
                f'<small>{label}</small>'
                f'</div>',
                unsafe_allow_html=True,
            )


# --- 年運預測 ---
def _render_year_forecast(chart: ZurkhaiChart) -> None:
    """渲染年運預測。"""
    st.subheader("🔮 年運預測 / Year Forecast")

    ca = chart.current_animal
    ce = chart.current_element
    cp = chart.current_polarity
    today = date.today()

    st.markdown(
        f"**今年 ({today.year})：** {ca.emoji} "
        f"{cp.name_cn}{ce.name_cn}{ca.name_cn}年 "
        f"({cp.name_mn} {ce.name_mn} {ca.name_mn} Jil)")
    st.write(f"**虛歲：** {chart.age}")

    # Conflict / Harmony
    if chart.is_conflict_year:
        st.error(f"⚠️ {chart.conflict_note_cn}")
        st.caption(chart.conflict_note_en)
    elif chart.is_harmony_year:
        st.success(f"✨ {chart.conflict_note_cn}")
        st.caption(chart.conflict_note_en)
    else:
        st.info("今年生肖無特殊沖合關係。/ No special animal conflict or "
                "harmony this year.")

    # Obstacle age
    if chart.is_obstacle_age:
        st.warning(f"🚧 {chart.obstacle_note_cn}")
        st.caption(chart.obstacle_note_en)


# --- 擇吉 ---
def _render_auspicious_table(chart: ZurkhaiChart) -> None:
    """渲染今日擇吉表。"""
    today = date.today()
    today_animal = _get_day_animal(today)
    today_element = _get_day_element(today)

    st.subheader(f"📅 今日擇吉 / Today's Auspicious Timing ({today})")
    st.markdown(
        f"**今日：** {today_animal.emoji} {today_animal.name_cn}日 "
        f"({today_animal.name_mn}) | "
        f"{today_element.emoji} {today_element.name_cn} "
        f"({today_element.name_mn})")

    # Day rating badge
    rating_color = {"吉": "#228B22", "凶": "#DC143C", "平": "#DAA520"}
    rc = rating_color.get(chart.day_rating, "#888")
    st.markdown(
        f'<div style="display:inline-block;background:{rc};color:white;'
        f'padding:6px 16px;border-radius:20px;font-size:1.2em;">'
        f'今日總評：{chart.day_rating} / {chart.day_rating_en}</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    # Activity table
    header = "| 活動 Activity | 蒙古名 | 吉凶 | 說明 |"
    sep = "|:---|:---|:---:|:---|"
    rows = [header, sep]
    for r in chart.auspicious_results:
        if r.is_favorable:
            icon = "✅ 吉"
        elif r.is_unfavorable:
            icon = "❌ 凶"
        else:
            icon = "⚖️ 平"
        rows.append(
            f"| {r.activity_cn} {r.activity_en} | {r.activity_mn} "
            f"| {icon} | {r.note_cn} |")
    st.markdown("\n".join(rows))


# --- 60 年循環表 ---
def _render_sixty_year_table(chart: ZurkhaiChart) -> None:
    """渲染 60 年循環簡表。"""
    st.subheader("🔄 六十年循環 / 60-Year Cycle (Jaran Jiliin Ergiilt)")

    header = "| # | 年份 | 元素 | 生肖 | 陰陽 | 蒙古名 |"
    sep = "|:---:|:---:|:---:|:---:|:---:|:---|"
    rows = [header, sep]

    # Show current 60-year cycle starting from the nearest start
    cycle_start = CYCLE_BASE_YEAR + (_get_cycle_year(chart.year) // 60) * 60
    # Align to the cycle containing birth year
    while cycle_start + 60 <= chart.year:
        cycle_start += 60
    while cycle_start > chart.year:
        cycle_start -= 60

    for i in range(60):
        y = cycle_start + i
        a = ANIMALS[(y - CYCLE_BASE_YEAR) % 12]
        e = ELEMENTS[((y - CYCLE_BASE_YEAR) // 2) % 5]
        p = POLARITIES[(y - CYCLE_BASE_YEAR) % 2]
        mark = " **👈**" if y == chart.year else ""
        rows.append(
            f"| {i+1} | {y}{mark} | {e[5]} {e[3]} | "
            f"{a[4]} {a[3]} | {p[4]} {p[3]} | "
            f"{p[1]} {e[1]} {a[1]} |")

    st.markdown("\n".join(rows))
    st.caption("👈 = 出生年 / Birth year")


# --- 五行相生相剋圖 ---
def _render_element_cycle_diagram() -> None:
    """渲染五行相生相剋示意。"""
    st.subheader("♻️ 五行相生相剋 / Five Element Cycles")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 相生 (Generating Cycle / Züin Tüshee)")
        st.markdown(
            '<div style="text-align:center;font-size:1.3em;'
            'line-height:2em;">'
            '🌳 木 → 🔥 火 → 🌍 土 → ⚙️ 金 → 💧 水 → 🌳 木'
            '</div>'
            '<div style="text-align:center;color:#666;">'
            'Mod → Gal → Shoroo → Temür → Us → Mod'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            | 生 | 說明 |
            |:---:|:---|
            | 木→火 | 木燃燒生火 / Wood feeds Fire |
            | 火→土 | 火化灰成土 / Fire creates Earth (ash) |
            | 土→金 | 土中蘊金 / Earth bears Metal |
            | 金→水 | 金化為水 / Metal collects Water |
            | 水→木 | 水滋養木 / Water nourishes Wood |
            """
        )

    with col2:
        st.markdown("#### 相剋 (Overcoming Cycle / Darakh Tüshee)")
        st.markdown(
            '<div style="text-align:center;font-size:1.3em;'
            'line-height:2em;">'
            '🌳 木 → 🌍 土 → 💧 水 → 🔥 火 → ⚙️ 金 → 🌳 木'
            '</div>'
            '<div style="text-align:center;color:#666;">'
            'Mod → Shoroo → Us → Gal → Temür → Mod'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            | 剋 | 說明 |
            |:---:|:---|
            | 木→土 | 木紮根破土 / Wood parts Earth |
            | 土→水 | 土阻擋水 / Earth absorbs Water |
            | 水→火 | 水滅火 / Water quenches Fire |
            | 火→金 | 火鎔金 / Fire melts Metal |
            | 金→木 | 金伐木 / Metal chops Wood |
            """
        )


# --- 歷史簡介 ---
def _render_history() -> None:
    """渲染祖爾海歷史簡介。"""
    st.subheader("📖 歷史簡介 / Historical Background")
    st.markdown(
        """
        #### 松巴堪布與德古斯布揚圖祖爾海
        #### Sumpa Khenpo Yeshe Peljor & Tegus Buyantu Zurkhai

        **祖爾海 (Зурхай / Zurkhai)** 是蒙古傳統占星術的總稱，其蒙古語名稱
        來自藏語「rtsis」（曆算），意為「天文曆算占星」。

        蒙古祖爾海體系的核心文獻為 **《德古斯布揚圖祖爾海》
        (Tegus Buyantu Zurkhai / Тэгүс Буянт Зурхай)**，由 18 世紀
        著名的蒙古族藏傳佛教學者 **松巴堪布·益西班覺
        (Sumpa Khenpo Yeshe Peljor / Сүмбэ Хамбо Ишбалжир，1704-1788)**
        在西藏曆算基礎上編纂而成。

        松巴堪布是安多地區（今青海）的傑出學者，精通天文、曆算、醫學、
        歷史等多個領域。他在藏傳佛教時輪金剛 (Kalachakra) 曆法的基礎上，
        融合蒙古遊牧民族的實際需求，創立了適合蒙古人使用的占星系統。

        ##### 核心原理

        - **十二生肖循環**：源自中亞遊牧文化與中國干支體系
        - **五行平衡**：木、火、土、金、水的相生相剋
        - **陰陽調和**：天地萬物的二元平衡
        - **藏傳佛教曆算**：結合時輪金剛 (Kalachakra) 的天文計算
        - **擇吉避凶**：為遊牧生活中的重要決定提供天時指引

        ##### 文化意義

        祖爾海在蒙古遊牧社會中扮演重要角色：
        - 🐎 **遷徙擇日**：選擇遷移牧場的吉日
        - 💒 **婚嫁擇吉**：確定結婚的良辰吉日
        - 🏥 **醫療時機**：配合藏蒙醫學的治療時間
        - 🙏 **宗教儀式**：佛教法會、灌頂的吉時選擇
        - ⚰️ **喪葬禮儀**：確定安葬的適當時間

        蒙古祖爾海體現了「天人合一」的東方哲學思想，融合了薩滿信仰、
        藏傳佛教與遊牧民族的生活智慧。
        """
    )


# --- 文化尊重提示 ---
def _render_cultural_note() -> None:
    """渲染文化尊重提示。"""
    st.info(
        "🙏 **文化尊重提示 / Cultural Respect Note**\n\n"
        "此計算依循蒙古傳統祖爾海 (Zurkhai) 古法，"
        "基於松巴堪布 (Sumpa Khenpo) 的德古斯布揚圖祖爾海 "
        "(Tegus Buyantu Zurkhai) 體系，"
        "僅供文化學習與參考。\n\n"
        "重要決定請諮詢合格的蒙古占星師 (Zurkhaič / Зурхайч) "
        "或喇嘛。\n\n"
        "This calculation follows traditional Mongolian Zurkhai methods "
        "based on the Tegus Buyantu Zurkhai system by Sumpa Khenpo "
        "Yeshe Peljor. It is provided for cultural learning and reference "
        "only. For important decisions, please consult a qualified "
        "Mongolian astrologer (Zurkhaič) or lama."
    )
