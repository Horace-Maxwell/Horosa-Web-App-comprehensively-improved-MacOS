"""
緬甸 Mahabote 排盤模組 (Myanmar Mahabote Astrology Chart Module)

Mahabote (မဟာဘုတ်) 是緬甸傳統占星術核心體系，意為「大創造」或「大決定」，
源自古緬甸與印度-苯教融合，以 **8 方位輪盤** 為基礎：

- **七曜行星** + **羅睺 (Rahu)**：日、月、火、水、木、金、土 + 羅睺
- **羅睺 (Rahu)**：星期三傍晚（當地太陽時 18:00 後）出生者歸羅睺管轄
- **八方位**：NE（東北）開始順時針 → NE、E、SE、S、SW、W、NW、N
- **八宮位**：Bhin、Ayu、Winya、Kiya、Hein、Marana、Thila + Kamma（業力/未知宮）
- **行星大運 (Atar)**：七星循環共 96 年
- **Sakka 曆計算**：Sakka 年 = Gregorian 年 − 638
- **計算公式**：Mahabote 值 = (Sakka 年 + 星期數) mod 8

文化聲明：
此計算依循緬甸傳統 Mahabote 古法，僅供文化學習與參考，
重要決定請諮詢合格的緬甸占星師。
"""

import math
import streamlit as st
from dataclasses import dataclass, field
from datetime import date


# ============================================================
# 常量 (Constants)
# ============================================================

# Weekday planets: (English, Myanmar, Chinese, symbol, element, direction)
WEEKDAY_PLANETS = [
    ("Sun",     "တနင်္ဂနွေ", "太陽", "☉", "火 Fire",  "NE 東北"),   # Sunday=0
    ("Moon",    "တနင်္လာ",   "月亮", "☽", "水 Water", "E 東"),      # Monday=1
    ("Mars",    "အင်္ဂါ",    "火星", "♂", "火 Fire",  "SE 東南"),   # Tuesday=2
    ("Mercury", "ဗုဒ္ဓဟူး",  "水星", "☿", "土 Earth", "S 南"),      # Wednesday=3
    ("Jupiter", "ကြာသပတေး",  "木星", "♃", "風 Air",   "W 西"),      # Thursday=4
    ("Venus",   "သောကြာ",    "金星", "♀", "水 Water", "NW 西北"),   # Friday=5
    ("Saturn",  "စနေ",       "土星", "♄", "火 Fire",  "N 北"),      # Saturday=6
]

# Rahu (pseudo-planet for Wednesday evening, after 18:00 local solar time)
RAHU_INFO = ("Rahu", "ရာဟု", "羅睺", "☊", "—", "SW 西南")

# Weekday animal signs: (English, Myanmar, Chinese, emoji)
WEEKDAY_ANIMALS = [
    ("Garuda",          "ဂဠုန်",    "迦樓羅",   "🦅"),  # Sunday=0
    ("Tiger",           "ကျား",     "虎",       "🐅"),  # Monday=1
    ("Lion",            "ခြင်္သေ့",  "獅",       "🦁"),  # Tuesday=2
    ("Tusked Elephant", "ဆင်စွယ်",  "象(有牙)",  "🐘"),  # Wednesday=3
    ("Rat",             "ကြွက်",    "鼠",       "🐀"),  # Thursday=4
    ("Guinea Pig",      "ပူးရွှေ",   "天竺鼠",   "🐹"),  # Friday=5
    ("Naga",            "နဂါး",     "龍/那伽",   "🐉"),  # Saturday=6
]

# Rahu animal sign (Wednesday evening)
RAHU_ANIMAL = ("Tuskless Elephant", "ဆင်", "象(無牙)", "🐘")

# Mahabote 8 Houses (expanded with 8th Kamma / Void house)
# (English, Myanmar, Chinese, meaning, description)
MAHABOTE_HOUSES = [
    ("Bhin",   "ဘင်",     "本命宮", "State of Being",
     "出生狀態，代表此生的起點與本質。此宮主性格基調、天賦潛力。"),
    ("Ayu",    "အာယု",    "壽命宮", "Longevity",
     "壽命與健康。此宮主體能、壽限、生命活力。"),
    ("Winya",  "ဝိညာဉ်",  "意識宮", "Consciousness",
     "精神與意識。此宮主智力、學習能力、精神狀態。"),
    ("Kiya",   "ကိယာ",    "身體宮", "Physical Body",
     "肉體與物質。此宮主身體健康、外貌特徵、物質享受。"),
    ("Hein",   "ဟိန်း",    "權勢宮", "Power / Prosperity",
     "力量與繁榮。此宮主事業成就、社會地位、財富。"),
    ("Marana", "မရဏ",     "死亡宮", "Death / Decline",
     "衰退與終結。此宮主危機、挑戰、人生低谷。"),
    ("Thila",  "သီလ",     "道德宮", "Virtue / Morality",
     "品德與修為。此宮主道德標準、宗教修行、行善積德。"),
    ("Kamma",  "ကမ္မ",     "業力宮", "Karma / Void",
     "業力與未知。此宮為第八隱藏宮，主前世業報、未解之緣、神秘力量。"),
]

# 8 Directions data: (direction_en, direction_cn, direction_myanmar,
#   planet_en, planet_symbol, planet_cn, weekday_idx, animal_en, animal_emoji, animal_cn,
#   omen_career, omen_marriage, omen_health, fortune)
# Ordered: NE → E → SE → S → SW → W → NW → N (clockwise from NE)
DIRECTIONS_8 = [
    {
        "dir_en": "NE", "dir_cn": "東北", "dir_myanmar": "အရှေ့မြောက်",
        "planet": "Sun", "symbol": "☉", "planet_cn": "太陽",
        "weekday_idx": 0, "animal": "Garuda", "animal_emoji": "🦅", "animal_cn": "迦樓羅",
        "fortune": "吉",
        "omen_career": "領導力強，適合開創事業，有貴人扶持。",
        "omen_marriage": "婚姻光明，伴侶忠誠，但需避免過於強勢。",
        "omen_health": "精力充沛，心臟與視力需注意保養。",
    },
    {
        "dir_en": "E", "dir_cn": "東", "dir_myanmar": "အရှေ့",
        "planet": "Moon", "symbol": "☽", "planet_cn": "月亮",
        "weekday_idx": 1, "animal": "Tiger", "animal_emoji": "🐅", "animal_cn": "虎",
        "fortune": "吉",
        "omen_career": "才華橫溢，適合文學、藝術、教育領域。",
        "omen_marriage": "感情豐富，婚姻和諧，但情緒波動需控制。",
        "omen_health": "消化系統與水分代謝需留意，情緒影響健康。",
    },
    {
        "dir_en": "SE", "dir_cn": "東南", "dir_myanmar": "အရှေ့တောင်",
        "planet": "Mars", "symbol": "♂", "planet_cn": "火星",
        "weekday_idx": 2, "animal": "Lion", "animal_emoji": "🦁", "animal_cn": "獅",
        "fortune": "凶中帶吉",
        "omen_career": "勇猛果敢，軍警、運動、競爭型事業有利。",
        "omen_marriage": "性格剛烈，婚姻需忍讓，易有口角衝突。",
        "omen_health": "血液循環與外傷需防範，火氣旺盛。",
    },
    {
        "dir_en": "S", "dir_cn": "南", "dir_myanmar": "တောင်",
        "planet": "Mercury", "symbol": "☿", "planet_cn": "水星",
        "weekday_idx": 3, "animal": "Tusked Elephant", "animal_emoji": "🐘",
        "animal_cn": "象(有牙)",
        "fortune": "中性",
        "omen_career": "智商高，適合商業、通訊、寫作、學術。",
        "omen_marriage": "善於溝通，但需避免口舌是非影響感情。",
        "omen_health": "神經系統與呼吸道較弱，需防過勞。",
    },
    {
        "dir_en": "SW", "dir_cn": "西南", "dir_myanmar": "အနောက်တောင်",
        "planet": "Rahu", "symbol": "☊", "planet_cn": "羅睺",
        "weekday_idx": -1, "animal": "Tuskless Elephant", "animal_emoji": "🐘",
        "animal_cn": "象(無牙)",
        "fortune": "凶",
        "omen_career": "命運多舛但深具靈性，適合宗教、玄學、醫療。",
        "omen_marriage": "婚姻考驗多，需培養信任與耐心。",
        "omen_health": "體質較弱，需防不明疾病與精神壓力。",
    },
    {
        "dir_en": "W", "dir_cn": "西", "dir_myanmar": "အနောက်",
        "planet": "Jupiter", "symbol": "♃", "planet_cn": "木星",
        "weekday_idx": 4, "animal": "Rat", "animal_emoji": "🐀", "animal_cn": "鼠",
        "fortune": "大吉",
        "omen_career": "智慧與福報兼具，適合教育、法律、宗教。",
        "omen_marriage": "婚姻美滿，伴侶賢德，子女孝順。",
        "omen_health": "肝膽系統需注意，整體福壽綿長。",
    },
    {
        "dir_en": "NW", "dir_cn": "西北", "dir_myanmar": "အနောက်မြောက်",
        "planet": "Venus", "symbol": "♀", "planet_cn": "金星",
        "weekday_idx": 5, "animal": "Guinea Pig", "animal_emoji": "🐹",
        "animal_cn": "天竺鼠",
        "fortune": "吉",
        "omen_career": "藝術才華出眾，適合設計、音樂、時尚、外交。",
        "omen_marriage": "桃花旺盛，婚姻甜蜜，但需防爛桃花。",
        "omen_health": "腎臟與泌尿系統需注意，享樂過度損健康。",
    },
    {
        "dir_en": "N", "dir_cn": "北", "dir_myanmar": "မြောက်",
        "planet": "Saturn", "symbol": "♄", "planet_cn": "土星",
        "weekday_idx": 6, "animal": "Naga", "animal_emoji": "🐉", "animal_cn": "龍/那伽",
        "fortune": "凶中帶吉",
        "omen_career": "刻苦耐勞，大器晚成，適合建築、農業、礦業。",
        "omen_marriage": "婚姻來遲但穩固，需耐心等待良緣。",
        "omen_health": "骨骼與關節需注意，晚年養生重要。",
    },
]

# Weekday names
WEEKDAY_NAMES_EN = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday",
]
WEEKDAY_NAMES_CN = [
    "星期日", "星期一", "星期二", "星期三",
    "星期四", "星期五", "星期六",
]

# Planet period durations (Atar / Dasa) — total 96 years
PLANET_PERIOD_YEARS = {
    "Sun": 6,
    "Moon": 15,
    "Mars": 8,
    "Mercury": 17,
    "Jupiter": 19,
    "Venus": 21,
    "Saturn": 10,
}

# Colours for rendering
PLANET_COLORS = {
    "Sun":     "#FFD700",
    "Moon":    "#C0C0C0",
    "Mars":    "#DC143C",
    "Mercury": "#228B22",
    "Jupiter": "#4169E1",
    "Venus":   "#FF69B4",
    "Saturn":  "#000080",
    "Rahu":    "#556B2F",
}


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class MahaboteHouse:
    """Single house in the Mahabote chart."""
    index: int
    name_en: str
    name_myanmar: str
    name_cn: str
    meaning: str
    description: str
    planet: str            # Planet English name
    planet_cn: str         # Planet Chinese name
    planet_symbol: str
    is_birth_house: bool   # Whether this is the birth planet's house
    weekday_en: str        # Weekday English name (e.g. "Sunday")
    weekday_cn: str        # Weekday Chinese name (e.g. "星期日")
    animal_en: str         # Animal sign English name
    animal_myanmar: str    # Animal sign Myanmar name
    animal_cn: str         # Animal sign Chinese name
    animal_emoji: str      # Animal sign emoji


@dataclass
class MahabotePeriod:
    """A single planetary period (Atar)."""
    planet: str
    planet_cn: str
    planet_symbol: str
    years: int
    start_age: int
    end_age: int
    is_current: bool


@dataclass
class MahaboteOmen:
    """Traditional omen reading for a direction-planet placement."""
    direction_en: str
    direction_cn: str
    planet: str
    planet_cn: str
    fortune: str
    omen_career: str
    omen_marriage: str
    omen_health: str


@dataclass
class MahaboteChart:
    """Complete Myanmar Mahabote chart result."""
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

    # Myanmar calendar
    myanmar_year: int

    # Weekday info
    weekday: int               # 0=Sunday … 6=Saturday
    weekday_name_en: str
    weekday_name_cn: str
    weekday_name_myanmar: str

    # Birth planet info
    birth_planet: str
    birth_planet_cn: str
    birth_planet_symbol: str
    birth_planet_element: str
    birth_direction: str

    # Wednesday evening → Rahu?
    is_rahu: bool

    # Birth animal sign
    birth_animal_en: str
    birth_animal_myanmar: str
    birth_animal_cn: str
    birth_animal_emoji: str

    # Mahabote calculation
    mahabote_value: int        # (Sakka_year + weekday_num) mod 8

    # Birth house
    birth_house_name_en: str
    birth_house_name_myanmar: str
    birth_house_name_cn: str
    birth_house_meaning: str
    birth_house_description: str

    # All 8 houses
    houses: list               # list[MahaboteHouse]

    # Planetary periods (Atar)
    periods: list              # list[MahabotePeriod]

    # Direction placements
    directions: list = field(default_factory=list)

    # Traditional omens
    omens: list = field(default_factory=list)    # list[MahaboteOmen]


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _get_myanmar_year(year, month, day):
    """Calculate Myanmar Era (ME / Sakka) year from Gregorian date.

    Myanmar New Year (Thingyan) typically falls around April 17.
    Sakka year = Gregorian year - 638 (on/after Apr 17) or - 639 (before Apr 17).
    """
    if month > 4 or (month == 4 and day >= 17):
        return year - 638
    return year - 639


def _get_weekday(year, month, day):
    """Day of week: 0=Sunday, 1=Monday, … 6=Saturday."""
    d = date(year, month, day)
    # Python weekday(): Mon=0 … Sun=6  →  we want Sun=0 … Sat=6
    return (d.weekday() + 1) % 7


def _local_solar_hour(hour, minute, timezone, longitude):
    """Convert clock time to approximate local solar time hour.

    Local solar time accounts for the difference between the timezone
    meridian and the actual longitude of the birth place.
    Each degree of longitude = 4 minutes of time.
    """
    tz_meridian = timezone * 15.0  # standard meridian for the timezone
    offset_minutes = (longitude - tz_meridian) * 4.0
    total_minutes = hour * 60 + minute + offset_minutes
    solar_hour = total_minutes / 60.0
    # Normalize to 0-24 range
    solar_hour = solar_hour % 24
    return solar_hour


def _is_wednesday_evening(weekday, hour):
    """Wednesday after 18:00 is ruled by Rahu instead of Mercury.

    When called from compute_mahabote_chart, ``hour`` should be the
    local-solar-time hour so the 18:00 threshold reflects the birth
    location's actual solar noon.  Helper tests may still pass the
    raw clock hour directly.
    """
    return weekday == 3 and hour >= 18


def _compute_periods(weekday, birth_year, current_year):
    """Compute Atar (planetary periods), starting from the birth weekday."""
    periods = []
    age = 0
    current_age = current_year - birth_year

    # Build 2 full cycles (192 years) to cover any lifespan
    for _ in range(2):
        for offset in range(7):
            day_idx = (weekday + offset) % 7
            planet_info = WEEKDAY_PLANETS[day_idx]
            planet_name = planet_info[0]
            duration = PLANET_PERIOD_YEARS[planet_name]
            start_age = age
            end_age = age + duration
            is_current = start_age <= current_age < end_age
            periods.append(MahabotePeriod(
                planet=planet_name,
                planet_cn=planet_info[2],
                planet_symbol=planet_info[3],
                years=duration,
                start_age=start_age,
                end_age=end_age,
                is_current=is_current,
            ))
            age += duration
            if age > 120:
                break
        if age > 120:
            break

    return periods


def _build_omens(birth_planet):
    """Build omen readings based on the birth planet's direction placement."""
    omens = []
    for d in DIRECTIONS_8:
        omens.append(MahaboteOmen(
            direction_en=d["dir_en"],
            direction_cn=d["dir_cn"],
            planet=d["planet"],
            planet_cn=d["planet_cn"],
            fortune=d["fortune"],
            omen_career=d["omen_career"],
            omen_marriage=d["omen_marriage"],
            omen_health=d["omen_health"],
        ))
    return omens


# ============================================================
# 計算函數 (Calculation)
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_mahabote_chart(year, month, day, hour, minute,
                           timezone, latitude, longitude,
                           location_name=""):
    """Compute a Myanmar Mahabote astrology chart.

    Uses the Sakka calendar and mod-8 formula for the authentic
    8-direction / 8-house Mahabote system.
    """

    me_year = _get_myanmar_year(year, month, day)
    weekday = _get_weekday(year, month, day)

    # Use local solar time for Rahu determination
    solar_hour = _local_solar_hour(hour, minute, timezone, longitude)
    is_rahu = _is_wednesday_evening(weekday, int(solar_hour))

    # Birth planet
    planet_info = WEEKDAY_PLANETS[weekday]
    animal_info = WEEKDAY_ANIMALS[weekday]
    if is_rahu:
        birth_planet = RAHU_INFO[0]
        birth_planet_cn = RAHU_INFO[2]
        birth_planet_symbol = RAHU_INFO[3]
        birth_planet_element = RAHU_INFO[4]
        birth_direction = RAHU_INFO[5]
        birth_animal = RAHU_ANIMAL
    else:
        birth_planet = planet_info[0]
        birth_planet_cn = planet_info[2]
        birth_planet_symbol = planet_info[3]
        birth_planet_element = planet_info[4]
        birth_direction = planet_info[5]
        birth_animal = animal_info

    # Mahabote value: use 1-based weekday (Sunday=1 … Saturday=7)
    # Authentic formula: (Sakka_year + weekday_num) mod 8
    weekday_num = weekday + 1
    mahabote_value = (me_year + weekday_num) % 8

    birth_house = MAHABOTE_HOUSES[mahabote_value]

    # Place planets in the 8 houses.
    # Birth planet sits at *mahabote_value*; subsequent weekdays
    # fill the next houses cyclically. With 8 houses and 7 weekday
    # planets, the 8th (Kamma) house wraps back and repeats the
    # birth planet (planet_offset=7 → (weekday+7)%7 == weekday).
    houses = []
    for i in range(8):
        h_info = MAHABOTE_HOUSES[i]
        planet_offset = (i - mahabote_value) % 8
        # Map into the 7 weekday planets cyclically
        planet_weekday = (weekday + planet_offset) % 7
        p_info = WEEKDAY_PLANETS[planet_weekday]
        a_info = WEEKDAY_ANIMALS[planet_weekday]

        houses.append(MahaboteHouse(
            index=i,
            name_en=h_info[0],
            name_myanmar=h_info[1],
            name_cn=h_info[2],
            meaning=h_info[3],
            description=h_info[4],
            planet=p_info[0],
            planet_cn=p_info[2],
            planet_symbol=p_info[3],
            is_birth_house=(i == mahabote_value),
            weekday_en=WEEKDAY_NAMES_EN[planet_weekday],
            weekday_cn=WEEKDAY_NAMES_CN[planet_weekday],
            animal_en=a_info[0],
            animal_myanmar=a_info[1],
            animal_cn=a_info[2],
            animal_emoji=a_info[3],
        ))

    # Direction placements (copy of DIRECTIONS_8 for inclusion in chart)
    directions = list(DIRECTIONS_8)

    # Build omens
    omens = _build_omens(birth_planet)

    # Atar periods
    from datetime import date as _date
    current_year = _date.today().year
    periods = _compute_periods(weekday, year, current_year)

    return MahaboteChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
        myanmar_year=me_year,
        weekday=weekday,
        weekday_name_en=WEEKDAY_NAMES_EN[weekday],
        weekday_name_cn=WEEKDAY_NAMES_CN[weekday],
        weekday_name_myanmar=planet_info[1],
        birth_planet=birth_planet,
        birth_planet_cn=birth_planet_cn,
        birth_planet_symbol=birth_planet_symbol,
        birth_planet_element=birth_planet_element,
        birth_direction=birth_direction,
        is_rahu=is_rahu,
        birth_animal_en=birth_animal[0],
        birth_animal_myanmar=birth_animal[1],
        birth_animal_cn=birth_animal[2],
        birth_animal_emoji=birth_animal[3],
        mahabote_value=mahabote_value,
        birth_house_name_en=birth_house[0],
        birth_house_name_myanmar=birth_house[1],
        birth_house_name_cn=birth_house[2],
        birth_house_meaning=birth_house[3],
        birth_house_description=birth_house[4],
        houses=houses,
        periods=periods,
        directions=directions,
        omens=omens,
    )


# ============================================================
# SVG 輪盤 (8-Sector Wheel Visualization)
# ============================================================

def build_mahabote_wheel_svg(chart, size=480):
    """Build an 8-sector retro-style Mahabote wheel as inline SVG.

    Generates a traditional Burmese compass-style wheel with 8 sectors
    (NE→E→SE→S→SW→W→NW→N), each showing the planet symbol, animal
    totem and Myanmar script.
    """
    cx, cy = size / 2, size / 2
    r_outer = size / 2 - 10
    r_inner = r_outer * 0.38
    r_mid = (r_outer + r_inner) / 2
    r_label = r_outer * 0.78
    r_animal = r_outer * 0.58

    # Direction order: NE, E, SE, S, SW, W, NW, N
    # Angles: NE starts at -67.5° (top-right), each sector is 45°
    sectors = DIRECTIONS_8
    sector_angle = 45
    start_offset = -67.5 - 90  # Rotate so NE is top-right

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {size} {size}" '
        f'style="max-width:100%;height:auto;font-family:serif;">'
    ]

    # Background circle
    svg_parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" '
        f'fill="#1a1a2e" stroke="#c9a96e" stroke-width="3"/>'
    )

    # Draw sectors
    for idx, sec in enumerate(sectors):
        angle_start = start_offset + idx * sector_angle
        angle_end = angle_start + sector_angle
        a1 = math.radians(angle_start)
        a2 = math.radians(angle_end)
        a_mid = math.radians((angle_start + angle_end) / 2)

        # Sector path (pie slice)
        x1_o = cx + r_outer * math.cos(a1)
        y1_o = cy + r_outer * math.sin(a1)
        x2_o = cx + r_outer * math.cos(a2)
        y2_o = cy + r_outer * math.sin(a2)
        x1_i = cx + r_inner * math.cos(a1)
        y1_i = cy + r_inner * math.sin(a1)
        x2_i = cx + r_inner * math.cos(a2)
        y2_i = cy + r_inner * math.sin(a2)

        color = PLANET_COLORS.get(sec["planet"], "#888")
        is_birth = (sec["planet"] == chart.birth_planet)
        fill_opacity = "0.35" if is_birth else "0.15"
        stroke_w = "3" if is_birth else "1"
        stroke_c = "#FFD700" if is_birth else "#c9a96e"

        path = (
            f'M {x1_i:.1f} {y1_i:.1f} '
            f'L {x1_o:.1f} {y1_o:.1f} '
            f'A {r_outer:.1f} {r_outer:.1f} 0 0 1 {x2_o:.1f} {y2_o:.1f} '
            f'L {x2_i:.1f} {y2_i:.1f} '
            f'A {r_inner:.1f} {r_inner:.1f} 0 0 0 {x1_i:.1f} {y1_i:.1f} Z'
        )
        svg_parts.append(
            f'<path d="{path}" fill="{color}" fill-opacity="{fill_opacity}" '
            f'stroke="{stroke_c}" stroke-width="{stroke_w}"/>'
        )

        # Direction label
        lx = cx + r_label * math.cos(a_mid)
        ly = cy + r_label * math.sin(a_mid)
        svg_parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="#c9a96e" '
            f'font-size="11" font-weight="bold">'
            f'{sec["dir_cn"]}</text>'
        )

        # Planet symbol
        sx = cx + r_mid * math.cos(a_mid)
        sy = cy + r_mid * math.sin(a_mid)
        svg_parts.append(
            f'<text x="{sx:.1f}" y="{sy:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="{color}" '
            f'font-size="22">{sec["symbol"]}</text>'
        )

        # Animal + planet name
        ax = cx + r_animal * math.cos(a_mid)
        ay = cy + r_animal * math.sin(a_mid)
        svg_parts.append(
            f'<text x="{ax:.1f}" y="{ay:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="white" '
            f'font-size="10">{sec["animal_emoji"]} {sec["animal_cn"]}</text>'
        )

    # Center circle
    svg_parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" '
        f'fill="#0d0d1a" stroke="#c9a96e" stroke-width="2"/>'
    )

    # Center content
    birth_color = PLANET_COLORS.get(chart.birth_planet, "#c9a96e")
    svg_parts.append(
        f'<text x="{cx}" y="{cy - 22}" text-anchor="middle" '
        f'fill="#c9a96e" font-size="10">မဟာဘုတ်</text>'
    )
    svg_parts.append(
        f'<text x="{cx}" y="{cy + 2}" text-anchor="middle" '
        f'fill="{birth_color}" font-size="28">'
        f'{chart.birth_planet_symbol}</text>'
    )
    svg_parts.append(
        f'<text x="{cx}" y="{cy + 22}" text-anchor="middle" '
        f'fill="{birth_color}" font-size="12" font-weight="bold">'
        f'{chart.birth_planet_cn}</text>'
    )
    svg_parts.append(
        f'<text x="{cx}" y="{cy + 38}" text-anchor="middle" '
        f'fill="#aaa" font-size="9">ME {chart.myanmar_year} · '
        f'{chart.weekday_name_cn}</text>'
    )

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


# ============================================================
# 渲染函數 (Rendering)
# ============================================================

def render_mahabote_chart(chart, after_chart_hook=None):
    """Render the complete Myanmar Mahabote chart."""
    # SVG Wheel
    svg = build_mahabote_wheel_svg(chart)
    st.markdown(
        f'<div style="text-align:center;margin:0 auto;max-width:500px;">{svg}</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    _render_compass(chart)
    st.divider()
    _render_mahabote_grid(chart)
    if after_chart_hook:
        after_chart_hook()
    st.divider()
    _render_info(chart)
    st.divider()
    _render_house_table(chart)
    st.divider()
    _render_omens(chart)
    st.divider()
    _render_periods(chart)


# -- Info section ----------------------------------------------------------

def _render_info(chart):
    st.subheader("📋 排盤資訊 (Chart Information)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**日期:** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**時間:** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**時區:** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**地點:** {chart.location_name}")
        st.write(f"**緯度:** {chart.latitude:.4f}°")
        st.write(f"**經度:** {chart.longitude:.4f}°")
    with col3:
        st.write(f"**緬甸年 (Sakka / ME):** {chart.myanmar_year}")
        st.write(
            f"**出生星期:** {chart.weekday_name_cn} "
            f"({chart.weekday_name_en} / {chart.weekday_name_myanmar})"
        )
        rahu_note = " ⚠️ 星期三傍晚 → 羅睺 (Rahu)" if chart.is_rahu else ""
        st.write(
            f"**出生行星:** {chart.birth_planet_symbol} "
            f"{chart.birth_planet} ({chart.birth_planet_cn}){rahu_note}"
        )
        st.write(
            f"**生肖動物:** {chart.birth_animal_emoji} "
            f"{chart.birth_animal_en} ({chart.birth_animal_cn} / "
            f"{chart.birth_animal_myanmar})"
        )

    # Highlight box
    color = PLANET_COLORS.get(chart.birth_planet, "#888")
    st.markdown(
        f'<div style="background:{color}22;border:2px solid {color};'
        f'padding:12px;border-radius:8px;margin-top:8px;">'
        f'<b style="font-size:18px;">'
        f'{chart.birth_planet_symbol} {chart.birth_planet_cn} '
        f'({chart.birth_planet})</b> — '
        f'方位 {chart.birth_direction} · 元素 {chart.birth_planet_element} · '
        f'動物 {chart.birth_animal_emoji} {chart.birth_animal_cn}<br/>'
        f'<b>Mahabote 宮位:</b> '
        f'{chart.birth_house_name_cn} {chart.birth_house_name_myanmar} '
        f'({chart.birth_house_name_en}) — {chart.birth_house_meaning}<br/>'
        f'<span style="font-size:13px;color:#888;">'
        f'{chart.birth_house_description}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


# -- Compass ---------------------------------------------------------------

def _render_compass(chart):
    """Render an 8-direction compass showing weekday-planet associations."""
    st.subheader("🧭 八方位行星羅盤 (Planetary Compass)")

    # Directions in display order:
    # (direction, weekday_idx, planet_en, symbol, planet_cn, weekday_cn, animal_emoji, animal_cn)
    # weekday_idx=-1 for Rahu (Wednesday evening)
    directions = [
        ("N 北",    6, "Saturn",  "♄", "土星", "星期六", "🐉", "龍/那伽"),
        ("NE 東北", 0, "Sun",     "☉", "太陽", "星期日", "🦅", "迦樓羅"),
        ("E 東",    1, "Moon",    "☽", "月亮", "星期一", "🐅", "虎"),
        ("SE 東南", 2, "Mars",    "♂", "火星", "星期二", "🦁", "獅"),
        ("S 南",    3, "Mercury", "☿", "水星", "星期三", "🐘", "象(有牙)"),
        ("SW 西南", -1, "Rahu",   "☊", "羅睺", "星期三夜", "🐘", "象(無牙)"),
        ("W 西",    4, "Jupiter", "♃", "木星", "星期四", "🐀", "鼠"),
        ("NW 西北", 5, "Venus",   "♀", "金星", "星期五", "🐹", "天竺鼠"),
    ]

    # Build a 3×5 compass layout:
    # Row 0:       NW    N    NE
    # Row 1:  W              E
    # Row 2:       SW    S    SE
    _cell = _compass_cell
    birth = chart.birth_planet

    row0 = [_cell(directions[7], birth), _cell(directions[0], birth),
            _cell(directions[1], birth)]
    row1_l = _cell(directions[6], birth)
    row1_r = _cell(directions[2], birth)
    row2 = [_cell(directions[5], birth), _cell(directions[4], birth),
            _cell(directions[3], birth)]

    center_html = (
        '<td style="text-align:center;font-size:28px;'
        'vertical-align:middle;">🧭</td>'
    )

    html = (
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        '<table style="border-collapse:separate;border-spacing:4px;'
        'margin:auto;width:80%;max-width:500px;table-layout:fixed;">'
        f'<tr>{"".join(row0)}</tr>'
        f'<tr>{row1_l}{center_html}{row1_r}</tr>'
        f'<tr>{"".join(row2)}</tr>'
        '</table></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def _compass_cell(direction_info, birth_planet):
    """Build one compass cell."""
    (dir_label, _, planet_en, symbol,
     planet_cn, weekday_cn, animal_emoji, animal_cn) = direction_info
    is_birth = (planet_en == birth_planet)
    color = PLANET_COLORS.get(planet_en, "#888")
    border = f"3px solid {color}" if is_birth else "1px solid #555"
    bg = f"{color}22" if is_birth else "#1a1a2e"
    return (
        f'<td style="background:{bg};border:{border};padding:10px;'
        f'border-radius:8px;text-align:center;color:white;width:33%;">'
        f'<div style="font-size:10px;color:#aaa;">{dir_label}</div>'
        f'<div style="font-size:10px;color:#ccc;">{weekday_cn}</div>'
        f'<div style="font-size:24px;">{symbol}</div>'
        f'<div style="font-size:13px;font-weight:bold;color:{color};">'
        f'{planet_en}</div>'
        f'<div style="font-size:12px;">{planet_cn}</div>'
        f'<div style="font-size:11px;">{animal_emoji} {animal_cn}</div>'
        f'</td>'
    )


# -- Mahabote 3×3 grid (8 houses) ------------------------------------------

def _render_mahabote_grid(chart):
    """Render a 3×3 grid representing the 8 Mahabote houses."""
    st.subheader("🏛️ Mahabote 八宮盤 (Mahabote House Grid)")

    # Layout mapping (8 houses + centre):
    #   Row 0: Kamma(7)  Thila(6)  Marana(5)
    #   Row 1: Hein(4)   Centre    Bhin(0)
    #   Row 2: Kiya(3)   Winya(2)  Ayu(1)
    grid_map = [
        [7, 6, 5],
        [4, "center", 0],
        [3, 2, 1],
    ]

    html = (
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        '<table style="border-collapse:separate;border-spacing:4px;'
        'margin:auto;width:100%;min-width:280px;table-layout:fixed;">'
    )

    for row in grid_map:
        html += '<tr>'
        for cell in row:
            if cell == "center":
                html += _center_cell(chart)
            else:
                html += _house_cell(chart.houses[cell])
        html += '</tr>'

    html += '</table></div>'
    st.markdown(html, unsafe_allow_html=True)


def _house_cell(house):
    """Render a single house cell."""
    color = PLANET_COLORS.get(house.planet, "#888")
    border = "3px solid gold" if house.is_birth_house else "1px solid #555"
    bg = f"{color}15"
    star = "⭐ " if house.is_birth_house else ""
    return (
        f'<td style="background:{bg};border:{border};padding:12px;'
        f'border-radius:8px;text-align:center;vertical-align:top;'
        f'color:white;width:33%;">'
        f'<div style="font-size:11px;color:#aaa;">'
        f'{house.name_en} ({house.meaning})</div>'
        f'<div style="font-size:16px;font-weight:bold;">'
        f'{star}{house.name_cn} {house.name_myanmar}</div>'
        f'<div style="font-size:10px;color:#ccc;">{house.weekday_cn}</div>'
        f'<div style="font-size:26px;margin:4px 0;">{house.planet_symbol}</div>'
        f'<div style="font-size:13px;color:{color};font-weight:bold;">'
        f'{house.planet} ({house.planet_cn})</div>'
        f'<div style="font-size:12px;">'
        f'{house.animal_emoji} {house.animal_cn}</div>'
        f'</td>'
    )


def _center_cell(chart):
    """Center cell with summary info."""
    color = PLANET_COLORS.get(chart.birth_planet, "#888")
    return (
        f'<td style="background:#0d0d1a;border:2px solid {color};'
        f'padding:12px;border-radius:8px;text-align:center;'
        f'vertical-align:middle;color:white;width:33%;">'
        f'<div style="font-size:11px;color:#aaa;">Mahabote</div>'
        f'<div style="font-size:32px;">{chart.birth_planet_symbol}</div>'
        f'<div style="font-size:14px;font-weight:bold;color:{color};">'
        f'{chart.birth_planet_cn}</div>'
        f'<div style="font-size:11px;color:#bbb;">'
        f'ME {chart.myanmar_year}<br/>'
        f'{chart.weekday_name_cn}</div>'
        f'</td>'
    )


# -- House table ------------------------------------------------------------

def _render_house_table(chart):
    st.subheader("📊 八宮詳表 (House Details)")
    header = (
        "| # | 宮位 (House) | 緬甸文 | 含義 (Meaning) "
        "| 星期 | 行星 | 動物 | 說明 |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|"
    rows = [header, sep]
    for h in chart.houses:
        star = "⭐" if h.is_birth_house else ""
        color = PLANET_COLORS.get(h.planet, "#888")
        planet_html = (
            f'<span style="color:{color};font-weight:bold;">'
            f'{h.planet_symbol} {h.planet} ({h.planet_cn})</span>'
        )
        animal_html = f'{h.animal_emoji} {h.animal_cn}'
        rows.append(
            f"| {h.index} "
            f"| {star} {h.name_cn} ({h.name_en}) "
            f"| {h.name_myanmar} "
            f"| {h.meaning} "
            f"| {h.weekday_cn} "
            f"| {planet_html} "
            f"| {animal_html} "
            f"| {h.description} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


# -- Omen readings ---------------------------------------------------------

def _render_omens(chart):
    """Render traditional omen interpretations for the birth planet."""
    st.subheader("🔮 傳統預兆解讀 (Traditional Omens)")
    st.markdown(
        "依據緬甸 Mahabote 古籍，每個方位行星落宮對應不同吉凶預兆："
    )

    # Find the birth planet's omen
    birth_omen = None
    for o in chart.omens:
        if o.planet == chart.birth_planet:
            birth_omen = o
            break

    if birth_omen:
        color = PLANET_COLORS.get(birth_omen.planet, "#888")
        fortune_color = {
            "大吉": "#FFD700", "吉": "#32CD32",
            "中性": "#87CEEB", "凶": "#DC143C", "凶中帶吉": "#FF8C00",
        }.get(birth_omen.fortune, "#888")
        st.markdown(
            f'<div style="background:{color}15;border:2px solid {color};'
            f'padding:16px;border-radius:10px;color:white;margin-bottom:12px;">'
            f'<h4 style="margin:0 0 8px 0;">'
            f'⭐ 本命方位：{birth_omen.direction_cn} — '
            f'{birth_omen.planet_cn} ({birth_omen.planet})</h4>'
            f'<div style="margin-bottom:8px;">'
            f'<span style="background:{fortune_color};color:white;'
            f'padding:2px 10px;border-radius:4px;font-weight:bold;">'
            f'{birth_omen.fortune}</span></div>'
            f'<div style="margin:4px 0;">💼 <b>事業：</b>{birth_omen.omen_career}</div>'
            f'<div style="margin:4px 0;">💕 <b>婚姻：</b>{birth_omen.omen_marriage}</div>'
            f'<div style="margin:4px 0;">🏥 <b>健康：</b>{birth_omen.omen_health}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # All omens summary
    with st.expander("📖 八方位完整預兆一覽"):
        for o in chart.omens:
            is_birth = (o.planet == chart.birth_planet)
            marker = "⭐ " if is_birth else ""
            color = PLANET_COLORS.get(o.planet, "#888")
            st.markdown(
                f"**{marker}{o.direction_cn} ({o.direction_en})** — "
                f"<span style='color:{color};font-weight:bold;'>"
                f"{o.planet_cn} ({o.planet})</span> · {o.fortune}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"  - 💼 事業：{o.omen_career}\n"
                f"  - 💕 婚姻：{o.omen_marriage}\n"
                f"  - 🏥 健康：{o.omen_health}"
            )


# -- Atar periods -----------------------------------------------------------

def _render_periods(chart):
    st.subheader("📅 行星大運 (Atar / Planetary Periods)")
    st.markdown(
        "緬甸占星將人生分為七星循環大運，每顆行星主宰一段年歲"
        "（共 96 年一輪），由出生星期的行星開始："
    )

    header = "| 行星 | 起始年齡 | 結束年齡 | 年數 | 當前 |"
    sep = "|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    for p in chart.periods:
        if p.start_age > 110:
            break
        color = PLANET_COLORS.get(p.planet, "#888")
        current = "👈 **現行**" if p.is_current else ""
        planet_html = (
            f'<span style="color:{color};font-weight:bold;">'
            f'{p.planet_symbol} {p.planet} ({p.planet_cn})</span>'
        )
        rows.append(
            f"| {planet_html} "
            f"| {p.start_age} "
            f"| {p.end_age} "
            f"| {p.years} "
            f"| {current} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)

    # Visual timeline
    _render_period_timeline(chart)


def _render_period_timeline(chart):
    """Render a visual horizontal bar timeline of Atar periods."""
    max_age = 96
    html = (
        '<div style="display:flex;width:100%;height:36px;'
        'border-radius:6px;overflow:hidden;margin-top:8px;">'
    )
    for p in chart.periods:
        if p.start_age >= max_age:
            break
        end = min(p.end_age, max_age)
        width_pct = (end - p.start_age) / max_age * 100
        color = PLANET_COLORS.get(p.planet, "#888")
        border = "3px solid gold" if p.is_current else "none"
        html += (
            f'<div style="width:{width_pct:.1f}%;background:{color};'
            f'border:{border};display:flex;align-items:center;'
            f'justify-content:center;font-size:11px;color:white;'
            f'font-weight:bold;min-width:20px;" '
            f'title="{p.planet} ({p.planet_cn}): '
            f'{p.start_age}–{end} 歲">'
            f'{p.planet_symbol}'
            f'</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    st.caption("行星大運時間軸（0–96 歲），金框為現行大運")
