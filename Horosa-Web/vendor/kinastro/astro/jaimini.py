"""
Jaimini 占星排盤模組 (Jaimini Astrology — Jaimini Sutras Chart Module)

Jaimini 占星源自古印度聖人 Jaimini 所著之《Jaimini Sutras》（約公元前 2 世紀），
與 Parashara 體系（BPHS）並列為印度 Jyotish 兩大核心流派。

Jaimini 體系的核心特色（與 Parashara Jyotish 的明確區別）：
1. **Chara Karaka（可變徵象星）**：以行星在星座內的實際度數高低，動態分配 7 種角色
   （Atmakaraka、Amatyakaraka 等），而非 Parashara 的固定 Karaka。
2. **Rashi Drishti（星座視線）**：以整個星座之間的相互視線取代 Parashara 的
   Graha Drishti（行星視線），活動座 ↔ 固定座互視，雙體座之間互視。
3. **Argala（介入）與 Virodhargala（阻擋）**：分析某宮位對另一宮位的干預效果。
4. **Arudha Pada（虛象宮）**：反映外在世界對命主的感知，計算方式獨特。
5. **Chara Dasha（可變大運）**：以星座為單位的大運系統，與 Vimshottari Dasha 截然不同。
6. **Sthira Karaka（固定徵象星）**：每顆行星永遠代表固定的主題。
7. 強調整個 **Rashi（星座）的整體解讀**，而非個別行星的度數精確度。

本模組使用 pyswisseph 以恆星黃道 (Sidereal Zodiac) 搭配 Lahiri 歲差 +
Whole Sign Houses 計算行星位置，並實作上述 Jaimini 古法計算。
"""

import math
import json
import os
from html import escape as _esc
import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

from astro.i18n import t, get_lang

# ============================================================
# 常量 (Constants)
# ============================================================

# 七顆用於 Chara Karaka 計算的行星（不含 Rahu/Ketu）
JAIMINI_KARAKA_PLANETS = {
    "Sun (太陽)": swe.SUN,
    "Moon (月亮)": swe.MOON,
    "Mars (火星)": swe.MARS,
    "Mercury (水星)": swe.MERCURY,
    "Jupiter (木星)": swe.JUPITER,
    "Venus (金星)": swe.VENUS,
    "Saturn (土星)": swe.SATURN,
}

# Chara Karaka 名稱（依度數高→低排序對應）
JAIMINI_CHARA_KARAKA_NAMES = [
    ("Atmakaraka",    "AK",  "靈魂徵象星"),
    ("Amatyakaraka",  "AmK", "大臣徵象星"),
    ("Bhratrukaraka", "BK",  "兄弟徵象星"),
    ("Matrukaraka",   "MK",  "母親徵象星"),
    ("Putrakaraka",   "PK",  "子女徵象星"),
    ("Gnatikaraka",   "GK",  "敵人徵象星"),
    ("Darakaraka",    "DK",  "配偶徵象星"),
]

# 十二星座 Rashis（與 vedic/indian.py 相同格式）
JAIMINI_RASHIS = [
    ("Mesha",      "♈", "白羊", "Mars",    "Chara"),
    ("Vrishabha",  "♉", "金牛", "Venus",   "Sthira"),
    ("Mithuna",    "♊", "雙子", "Mercury", "Dwiswabhava"),
    ("Karka",      "♋", "巨蟹", "Moon",    "Chara"),
    ("Simha",      "♌", "獅子", "Sun",     "Sthira"),
    ("Kanya",      "♍", "處女", "Mercury", "Dwiswabhava"),
    ("Tula",       "♎", "天秤", "Venus",   "Chara"),
    ("Vrischika",  "♏", "天蠍", "Mars",    "Sthira"),
    ("Dhanu",      "♐", "射手", "Jupiter", "Dwiswabhava"),
    ("Makara",     "♑", "摩羯", "Saturn",  "Chara"),
    ("Kumbha",     "♒", "水瓶", "Saturn",  "Sthira"),
    ("Meena",      "♓", "雙魚", "Jupiter", "Dwiswabhava"),
]

# 星座性質 → 索引對照
JAIMINI_SIGN_QUALITY = {i: JAIMINI_RASHIS[i][4] for i in range(12)}

# ============================================================
# Rashi Drishti（星座視線）規則表
# ============================================================
# Chara ↔ Sthira 互視（排除自身對面的座）
# Dwiswabhava ↔ Dwiswabhava 互視
# 格式：JAIMINI_RASHI_DRISHTI[sign_index] → list of aspected sign indices

def _build_rashi_drishti_table():
    """建立 Rashi Drishti 規則表（古法規則）。

    Rules per Jaimini Sutras:
    - Movable (Chara) signs aspect all Fixed (Sthira) signs except
      the one adjacent (next sign).
    - Fixed (Sthira) signs aspect all Movable (Chara) signs except
      the one adjacent (previous sign).
    - Dual (Dwiswabhava) signs aspect the other three Dual signs.
    """
    table = {}
    chara_idx   = [i for i in range(12) if JAIMINI_SIGN_QUALITY[i] == "Chara"]
    sthira_idx  = [i for i in range(12) if JAIMINI_SIGN_QUALITY[i] == "Sthira"]
    dwi_idx     = [i for i in range(12) if JAIMINI_SIGN_QUALITY[i] == "Dwiswabhava"]

    for i in range(12):
        q = JAIMINI_SIGN_QUALITY[i]
        if q == "Chara":
            # Aspect all Sthira except the next sign
            table[i] = [s for s in sthira_idx if s != (i + 1) % 12]
        elif q == "Sthira":
            # Aspect all Chara except the previous sign
            table[i] = [c for c in chara_idx if c != (i - 1) % 12]
        else:  # Dwiswabhava
            table[i] = [d for d in dwi_idx if d != i]
    return table


JAIMINI_RASHI_DRISHTI = _build_rashi_drishti_table()

# ============================================================
# Argala（介入）與 Virodhargala（阻擋）規則
# ============================================================
# (argala_offset, virodhargala_offset, name_zh, name_en)
JAIMINI_ARGALA_RULES = [
    (2,  12, "第二宮 Argala（財富介入）",      "2nd House Argala (Wealth)"),
    (4,  10, "第四宮 Argala（幸福介入）",      "4th House Argala (Happiness)"),
    (11,  3, "第十一宮 Argala（收益介入）",    "11th House Argala (Gains)"),
    (5,   9, "第五宮 Argala（子女/功德介入）", "5th House Argala (Children/Merit)"),
]

# ============================================================
# Sthira Karaka（固定徵象星）
# ============================================================
JAIMINI_STHIRA_KARAKA = [
    ("Sun",     "太陽", "父親",       "Father"),
    ("Moon",    "月亮", "母親",       "Mother"),
    ("Mars",    "火星", "兄弟姐妹",   "Siblings"),
    ("Mercury", "水星", "親戚",       "Relatives"),
    ("Jupiter", "木星", "子女",       "Children"),
    ("Venus",   "金星", "配偶",       "Spouse"),
    ("Saturn",  "土星", "壽命、痛苦", "Longevity, suffering"),
]

# 行星顏色（SVG 視覺化用）
JAIMINI_PLANET_COLORS = {
    "Sun (太陽)":     "#FF8C00",
    "Moon (月亮)":    "#C0C0C0",
    "Mars (火星)":    "#DC143C",
    "Mercury (水星)": "#4169E1",
    "Jupiter (木星)": "#FFD700",
    "Venus (金星)":   "#FF69B4",
    "Saturn (土星)":  "#8B4513",
    "Rahu (羅睺)":    "#800080",
    "Ketu (計都)":    "#4B0082",
}

# 行星符號
JAIMINI_PLANET_GLYPHS = {
    "Sun (太陽)":     "☉",
    "Moon (月亮)":    "☽",
    "Mars (火星)":    "♂",
    "Mercury (水星)": "☿",
    "Jupiter (木星)": "♃",
    "Venus (金星)":   "♀",
    "Saturn (土星)":  "♄",
    "Rahu (羅睺)":    "☊",
    "Ketu (計都)":    "☋",
}

# 二十七宿 (27 Nakshatras) — 簡表
JAIMINI_NAKSHATRAS = [
    ("Ashwini",           "馬頭宿",  "Ketu"),
    ("Bharani",           "大陵宿",  "Venus"),
    ("Krittika",          "昴宿",    "Sun"),
    ("Rohini",            "畢宿",    "Moon"),
    ("Mrigashira",        "觜宿",    "Mars"),
    ("Ardra",             "參宿",    "Rahu"),
    ("Punarvasu",         "井宿",    "Jupiter"),
    ("Pushya",            "鬼宿",    "Saturn"),
    ("Ashlesha",          "柳宿",    "Mercury"),
    ("Magha",             "星宿",    "Ketu"),
    ("Purva Phalguni",    "張宿",    "Venus"),
    ("Uttara Phalguni",   "翼宿",    "Sun"),
    ("Hasta",             "軫宿",    "Moon"),
    ("Chitra",            "角宿",    "Mars"),
    ("Swati",             "亢宿",    "Rahu"),
    ("Vishakha",          "氐宿",    "Jupiter"),
    ("Anuradha",          "房宿",    "Saturn"),
    ("Jyeshtha",          "心宿",    "Mercury"),
    ("Mula",              "尾宿",    "Ketu"),
    ("Purva Ashadha",     "箕宿",    "Venus"),
    ("Uttara Ashadha",    "斗宿",    "Sun"),
    ("Shravana",          "牛宿",    "Moon"),
    ("Dhanishta",         "女宿",    "Mars"),
    ("Shatabhisha",       "虛宿",    "Rahu"),
    ("Purva Bhadrapada",  "危宿",    "Jupiter"),
    ("Uttara Bhadrapada", "室宿",    "Saturn"),
    ("Revati",            "壁宿",    "Mercury"),
]


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class JaiminiPlanet:
    """Jaimini planet position"""
    name: str
    longitude: float
    latitude: float
    rashi: str
    rashi_glyph: str
    rashi_chinese: str
    rashi_lord: str
    rashi_quality: str
    sign_degree: float
    nakshatra: str
    nakshatra_chinese: str
    nakshatra_lord: str
    nakshatra_pada: int
    retrograde: bool
    house: int = 0
    chara_karaka: str = ""
    chara_karaka_abbr: str = ""


@dataclass
class JaiminiHouse:
    """Jaimini bhava (house) — Whole Sign"""
    number: int
    cusp: float
    rashi: str
    rashi_glyph: str
    rashi_quality: str
    planets: list = field(default_factory=list)


@dataclass
class JaiminiArgala:
    """Argala / Virodhargala analysis for a house"""
    target_house: int
    argala_house: int
    argala_type_zh: str
    argala_type_en: str
    argala_planets: list
    virodhargala_house: int
    virodhargala_planets: list
    is_obstructed: bool


@dataclass
class JaiminiPada:
    """Arudha Pada for a house"""
    house: int
    pada_sign_index: int
    pada_sign: str
    pada_sign_glyph: str
    label: str


@dataclass
class JaiminiCharaDasha:
    """A single Chara Dasha period"""
    sign: str
    sign_glyph: str
    sign_chinese: str
    years: int
    start_year: float
    end_year: float


@dataclass
class JaiminiChart:
    """Jaimini astrology chart (main return type)"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    julian_day: float
    ayanamsa: float
    planets: list           # List[JaiminiPlanet]
    houses: list            # List[JaiminiHouse]
    ascendant: float
    asc_rashi: str
    chara_karakas: list     # List[tuple(planet_name, karaka_name, abbr, degree)]
    rashi_drishti: dict     # {sign_index: [aspected_indices]}
    argala: list            # List[JaiminiArgala]
    padas: list             # List[JaiminiPada]
    chara_dasha: list       # List[JaiminiCharaDasha]
    sthira_karakas: list    # Fixed Sthira Karaka assignments


# ============================================================
# 計算輔助函數 (Calculation Helpers)
# ============================================================

def _normalize(deg):
    return deg % 360.0


def _sign_index(deg):
    return int(_normalize(deg) / 30.0)


def _sign_degree(deg):
    return _normalize(deg) % 30.0


def _nakshatra_info(deg):
    """Return (nakshatra_index, pada) for a given sidereal longitude."""
    deg = _normalize(deg)
    nak_span = 360.0 / 27.0  # 13°20'
    idx = int(deg / nak_span) % 27
    pada = int((deg % nak_span) / (nak_span / 4.0)) + 1
    return idx, min(pada, 4)


def _format_deg(deg):
    deg = _normalize(deg)
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""


def _whole_sign_cusps(asc_lon):
    """Compute Whole Sign house cusps from Ascendant longitude."""
    asc_sign = _sign_index(asc_lon)
    return [((asc_sign + i) % 12) * 30.0 for i in range(12)]


def _find_house_ws(lon, asc_lon):
    """Find house number (1-12) for a longitude using Whole Sign Houses."""
    asc_sign = _sign_index(asc_lon)
    planet_sign = _sign_index(lon)
    return ((planet_sign - asc_sign) % 12) + 1


def _rashi_lord_map():
    """Return dict: sign_index → lord planet english name."""
    return {i: JAIMINI_RASHIS[i][3] for i in range(12)}


def _lord_to_swe_id(lord_name):
    """Map a lord name (e.g., 'Mars') to its swe constant."""
    _map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
    }
    return _map.get(lord_name)


# ============================================================
# Chara Karaka 計算
# ============================================================

def _compute_chara_karakas(planets):
    """計算 7 顆 Chara Karaka（可變徵象星）。

    規則：取 7 顆行星（Sun–Saturn），按各自在星座內的度數
    （sign_degree）從高到低排序，依序分配 AK、AmK、BK、MK、PK、GK、DK。

    Parameters
    ----------
    planets : list[JaiminiPlanet]
        Must contain exactly the 7 classical planets (Sun–Saturn).

    Returns
    -------
    list[tuple[str, str, str, float]]
        [(planet_name, karaka_name, karaka_abbr, sign_degree), ...]
    """
    # Filter to the 7 karaka planets (exclude Rahu/Ketu)
    karaka_candidates = [
        p for p in planets
        if p.name in JAIMINI_KARAKA_PLANETS
    ]
    # Sort by sign_degree descending
    karaka_candidates.sort(key=lambda p: p.sign_degree, reverse=True)

    result = []
    for i, p in enumerate(karaka_candidates[:7]):
        karaka = JAIMINI_CHARA_KARAKA_NAMES[i]
        p.chara_karaka = karaka[0]
        p.chara_karaka_abbr = karaka[1]
        result.append((p.name, karaka[0], karaka[1], p.sign_degree))
    return result


# ============================================================
# Argala 計算
# ============================================================

def _compute_argala(houses):
    """計算所有宮位的 Argala 與 Virodhargala。

    Returns
    -------
    list[JaiminiArgala]
    """
    results = []
    for h in houses:
        target = h.number  # 1-12
        for offset, obstruct_offset, name_zh, name_en in JAIMINI_ARGALA_RULES:
            argala_idx = ((target - 1 + offset) % 12)
            virodh_idx = ((target - 1 + obstruct_offset) % 12)
            argala_h = houses[argala_idx]
            virodh_h = houses[virodh_idx]
            a_planets = argala_h.planets[:]
            v_planets = virodh_h.planets[:]
            # Argala is obstructed if virodhargala house has >= planets
            is_obstructed = len(v_planets) >= len(a_planets)
            if a_planets:  # Only record if there are planets causing argala
                results.append(JaiminiArgala(
                    target_house=target,
                    argala_house=argala_h.number,
                    argala_type_zh=name_zh,
                    argala_type_en=name_en,
                    argala_planets=a_planets,
                    virodhargala_house=virodh_h.number,
                    virodhargala_planets=v_planets,
                    is_obstructed=is_obstructed,
                ))
    return results


# ============================================================
# Arudha Pada 計算
# ============================================================

def _compute_padas(houses, planets, asc_lon):
    """計算 12 宮位的 Arudha Pada。

    規則：
    1. 找到該宮位的主星（lord）
    2. 找到主星所在的星座
    3. 從該宮位到主星所在星座數 N 個星座
    4. 再從主星所在星座數 N 個星座 → 得到 Pada 所在星座
    5. 特例：如果 Pada 落在同一宮位或其第七宮，則取第十宮。
    """
    lord_map = _rashi_lord_map()
    asc_sign = _sign_index(asc_lon)
    padas = []

    # Planet name → sign index mapping
    planet_sign_map = {}
    for p in planets:
        # Map lord name to the planet's sign
        short = p.name.split(" ")[0]
        planet_sign_map[short] = _sign_index(p.longitude)

    for h in houses:
        house_num = h.number
        house_sign_idx = (asc_sign + house_num - 1) % 12
        lord = lord_map[house_sign_idx]
        lord_sign = planet_sign_map.get(lord)
        if lord_sign is None:
            # Fallback: lord_sign = house_sign_idx
            lord_sign = house_sign_idx

        # Count from house_sign_idx to lord_sign
        count = (lord_sign - house_sign_idx) % 12 + 1
        # Pada sign = lord_sign + (count - 1) steps further
        pada_sign_idx = (lord_sign + count - 1) % 12

        # Special rule: if pada falls in same house or 7th from it
        if pada_sign_idx == house_sign_idx or pada_sign_idx == (house_sign_idx + 6) % 12:
            pada_sign_idx = (house_sign_idx + 9) % 12  # 10th from house

        rashi = JAIMINI_RASHIS[pada_sign_idx]
        label = f"A{house_num}"
        if house_num == 1:
            label = "AL"
        elif house_num == 12:
            label = "UL"
        elif house_num == 7:
            label = "A7"

        padas.append(JaiminiPada(
            house=house_num,
            pada_sign_index=pada_sign_idx,
            pada_sign=rashi[0],
            pada_sign_glyph=rashi[1],
            label=label,
        ))

    return padas


# ============================================================
# Chara Dasha 計算
# ============================================================

def _compute_chara_dasha(asc_lon, planets, birth_jd):
    """計算 Jaimini Chara Dasha 大運。

    規則（K.N. Rao 方法）：
    - 奇數星座（Aries=1, Gemini=3 等）的 Lagna → 從 Lagna 正序開始
    - 偶數星座（Taurus=2, Cancer=4 等）的 Lagna → 從第 7 宮逆序開始
    - 每個星座的大運年數 = 該星座主星到該星座的距離（含首尾計算）
    """
    asc_sign = _sign_index(asc_lon)
    lord_map = _rashi_lord_map()

    # Planet positions map: lord_name → sign_index
    planet_sign_map = {}
    for p in planets:
        short = p.name.split(" ")[0]
        planet_sign_map[short] = _sign_index(p.longitude)

    # Determine order: traditional odd signs (Aries idx=0, Gemini idx=2, etc.) go forward
    starts_forward = (asc_sign % 2 == 0)  # Aries=0 is index 0 = odd sign in tradition

    dasha_periods = []
    if starts_forward:
        start_sign = asc_sign
        direction = 1  # Forward
    else:
        start_sign = (asc_sign + 6) % 12  # 7th house
        direction = -1  # Backward

    # Convert JD to approximate year
    birth_year_approx = 2000.0 + (birth_jd - 2451545.0) / 365.25

    current_year = birth_year_approx
    for i in range(12):
        sign_idx = (start_sign + direction * i) % 12
        rashi = JAIMINI_RASHIS[sign_idx]
        lord = lord_map[sign_idx]
        lord_sign = planet_sign_map.get(lord, sign_idx)

        # Duration = distance from sign to lord's sign
        if starts_forward:
            duration = (lord_sign - sign_idx) % 12
        else:
            duration = (sign_idx - lord_sign) % 12

        # If lord is in own sign, duration = 12
        if duration == 0:
            duration = 12

        dasha_periods.append(JaiminiCharaDasha(
            sign=rashi[0],
            sign_glyph=rashi[1],
            sign_chinese=rashi[2],
            years=duration,
            start_year=round(current_year, 2),
            end_year=round(current_year + duration, 2),
        ))
        current_year += duration

    return dasha_periods


# ============================================================
# 主計算函數 (Main Compute Function)
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_jaimini_chart(year, month, day, hour, minute, timezone,
                          latitude, longitude, location_name=""):
    """計算 Jaimini 占星排盤 (Sidereal / Lahiri Ayanamsa / Whole Sign Houses)

    計算內容包含：
    - 9 顆行星位置（7 + Rahu + Ketu）
    - 7 顆 Chara Karaka（可變徵象星）
    - Rashi Drishti（星座視線）
    - Argala 與 Virodhargala
    - Arudha Pada（12 宮虛象宮）
    - Chara Dasha（可變大運）
    - Sthira Karaka（固定徵象星）

    Returns
    -------
    JaiminiChart
        Complete Jaimini chart object compatible with vedic chart dict format.
    """
    swe.set_ephe_path("")
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Compute ascendant using Whole Sign houses
    _, ascmc = swe.houses_ex(jd, latitude, longitude, b"W",
                             swe.FLG_SIDEREAL)
    ascendant = _normalize(ascmc[0])
    cusps = _whole_sign_cusps(ascendant)

    # Compute planet positions
    planets = []
    for name, pid in JAIMINI_KARAKA_PLANETS.items():
        result, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        rashi = JAIMINI_RASHIS[idx]
        nak_idx, pada = _nakshatra_info(lon)
        nak = JAIMINI_NAKSHATRAS[nak_idx]

        planets.append(JaiminiPlanet(
            name=name, longitude=lon, latitude=lat,
            rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
            rashi_lord=rashi[3], rashi_quality=rashi[4],
            sign_degree=_sign_degree(lon),
            nakshatra=nak[0], nakshatra_chinese=nak[1],
            nakshatra_lord=nak[2], nakshatra_pada=pada,
            retrograde=speed < 0,
        ))

    # Rahu (Mean North Node)
    rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _normalize(rahu_res[0])
    idx = _sign_index(rahu_lon)
    rashi = JAIMINI_RASHIS[idx]
    nak_idx, pada = _nakshatra_info(rahu_lon)
    nak = JAIMINI_NAKSHATRAS[nak_idx]
    planets.append(JaiminiPlanet(
        name="Rahu (羅睺)", longitude=rahu_lon, latitude=rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], rashi_quality=rashi[4],
        sign_degree=_sign_degree(rahu_lon),
        nakshatra=nak[0], nakshatra_chinese=nak[1],
        nakshatra_lord=nak[2], nakshatra_pada=pada,
        retrograde=False,
    ))

    # Ketu (South Node = Rahu + 180°)
    ketu_lon = _normalize(rahu_lon + 180.0)
    idx = _sign_index(ketu_lon)
    rashi = JAIMINI_RASHIS[idx]
    nak_idx, pada = _nakshatra_info(ketu_lon)
    nak = JAIMINI_NAKSHATRAS[nak_idx]
    planets.append(JaiminiPlanet(
        name="Ketu (計都)", longitude=ketu_lon, latitude=-rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], rashi_quality=rashi[4],
        sign_degree=_sign_degree(ketu_lon),
        nakshatra=nak[0], nakshatra_chinese=nak[1],
        nakshatra_lord=nak[2], nakshatra_pada=pada,
        retrograde=False,
    ))

    # Build Whole Sign houses
    asc_sign = _sign_index(ascendant)
    houses = []
    for i in range(12):
        sign_idx = (asc_sign + i) % 12
        cusp = sign_idx * 30.0
        rashi = JAIMINI_RASHIS[sign_idx]
        houses.append(JaiminiHouse(
            number=i + 1, cusp=cusp,
            rashi=rashi[0], rashi_glyph=rashi[1],
            rashi_quality=rashi[4],
            planets=[],
        ))

    # Assign planets to houses
    for p in planets:
        h = _find_house_ws(p.longitude, ascendant)
        p.house = h
        houses[h - 1].planets.append(p.name)

    # Chara Karaka
    chara_karakas = _compute_chara_karakas(planets)

    # Rashi Drishti (use pre-built table)
    rashi_drishti = dict(JAIMINI_RASHI_DRISHTI)

    # Argala
    argala = _compute_argala(houses)

    # Arudha Pada
    padas = _compute_padas(houses, planets, ascendant)

    # Chara Dasha
    chara_dasha = _compute_chara_dasha(ascendant, planets, jd)

    # Sthira Karaka
    sthira_karakas = list(JAIMINI_STHIRA_KARAKA)

    asc_rashi = JAIMINI_RASHIS[asc_sign][0]

    return JaiminiChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd, ayanamsa=ayanamsa,
        planets=planets, houses=houses,
        ascendant=ascendant, asc_rashi=asc_rashi,
        chara_karakas=chara_karakas,
        rashi_drishti=rashi_drishti,
        argala=argala,
        padas=padas,
        chara_dasha=chara_dasha,
        sthira_karakas=sthira_karakas,
    )


# ============================================================
# SVG 視覺化 — Rashi Drishti 箭頭圖 (Rashi Drishti Arrow Chart)
# ============================================================

def build_jaimini_rashi_chart_svg(chart):
    """產生 Jaimini Rashi Drishti 視覺化 SVG。

    以圓形排列 12 個星座，箭頭表示 Rashi Drishti（星座視線），
    行星位置以符號標註。

    Returns
    -------
    str
        Complete ``<svg>`` markup wrapped in a centering ``<div>``.
    """
    SIZE = 640
    CX, CY = SIZE / 2, SIZE / 2
    R_OUTER = 270
    R_INNER = 200
    R_LABEL = 240
    R_CENTRE = 70

    # Planets grouped by sign
    rashi_planets = {i: [] for i in range(12)}
    for p in chart.planets:
        idx = _sign_index(p.longitude)
        short = p.name.split(" ")[0]
        glyph = JAIMINI_PLANET_GLYPHS.get(p.name, short[:2])
        karaka = p.chara_karaka_abbr
        rashi_planets[idx].append((short, glyph, p.name, karaka))

    asc_sign = _sign_index(chart.ascendant)

    svg = []
    svg.append(
        f'<div style="text-align:center;overflow-x:auto;'
        f'-webkit-overflow-scrolling:touch;max-width:100%;">'
    )
    svg.append(
        f'<svg viewBox="0 0 {SIZE} {SIZE}" xmlns="http://www.w3.org/2000/svg"'
        f' style="width:100%;max-width:{SIZE}px;height:auto;'
        f'font-family:sans-serif;">'
    )

    # Defs for arrowheads
    svg.append('<defs>')
    svg.append(
        '<marker id="jm-arrow" viewBox="0 0 10 10" refX="8" refY="5"'
        ' markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#ff9900"/>'
        '</marker>'
    )
    svg.append('</defs>')

    # Background
    svg.append(
        f'<rect width="{SIZE}" height="{SIZE}" fill="#1a1520" rx="12"/>'
    )

    # Outer decorative ring
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER + 15}"'
        f' fill="none" stroke="#d4af37" stroke-width="2" opacity="0.4"/>'
    )
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER}"'
        f' fill="none" stroke="#d4af37" stroke-width="1.5"/>'
    )
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_INNER}"'
        f' fill="none" stroke="#555" stroke-width="1"/>'
    )

    # Draw 12 sign sectors and radial lines
    for i in range(12):
        angle_start = math.radians(-90 + i * 30)
        angle_end = math.radians(-90 + (i + 1) * 30)
        angle_mid = math.radians(-90 + i * 30 + 15)

        # Radial line
        x1 = CX + R_INNER * math.cos(angle_start)
        y1 = CY + R_INNER * math.sin(angle_start)
        x2 = CX + R_OUTER * math.cos(angle_start)
        y2 = CY + R_OUTER * math.sin(angle_start)
        svg.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"'
            f' stroke="#555" stroke-width="1"/>'
        )

        # Sign index (starting from Aries at top)
        sign_idx = (asc_sign + i) % 12
        rashi = JAIMINI_RASHIS[sign_idx]
        is_asc = (i == 0)

        # Label position
        lx = CX + R_LABEL * math.cos(angle_mid)
        ly = CY + R_LABEL * math.sin(angle_mid)

        # Highlight ASC sector
        if is_asc:
            a1 = math.radians(-90 + i * 30)
            a2 = math.radians(-90 + (i + 1) * 30)
            x_a1 = CX + R_INNER * math.cos(a1)
            y_a1 = CY + R_INNER * math.sin(a1)
            x_a2 = CX + R_OUTER * math.cos(a1)
            y_a2 = CY + R_OUTER * math.sin(a1)
            x_a3 = CX + R_OUTER * math.cos(a2)
            y_a3 = CY + R_OUTER * math.sin(a2)
            x_a4 = CX + R_INNER * math.cos(a2)
            y_a4 = CY + R_INNER * math.sin(a2)
            svg.append(
                f'<path d="M {x_a1:.1f} {y_a1:.1f} L {x_a2:.1f} {y_a2:.1f}'
                f' A {R_OUTER} {R_OUTER} 0 0 1 {x_a3:.1f} {y_a3:.1f}'
                f' L {x_a4:.1f} {y_a4:.1f}'
                f' A {R_INNER} {R_INNER} 0 0 0 {x_a1:.1f} {y_a1:.1f} Z"'
                f' fill="#3d3010" opacity="0.6"/>'
            )

        # Sign label
        marker = " ▲" if is_asc else ""
        svg.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle"'
            f' dominant-baseline="central" font-size="10" font-weight="bold"'
            f' fill="#e0e0e0">{_esc(rashi[1])} {_esc(rashi[2])}{marker}</text>'
        )

        # Planet glyphs in sector
        p_list = rashi_planets[sign_idx]
        if p_list:
            r_planet = (R_INNER + R_OUTER) / 2
            for pi, (short, glyph, full, karaka) in enumerate(p_list):
                offset_angle = angle_mid + (pi - len(p_list) / 2) * 0.12
                px = CX + r_planet * math.cos(offset_angle)
                py = CY + r_planet * math.sin(offset_angle)
                color = JAIMINI_PLANET_COLORS.get(full, "#c8c8c8")
                label = glyph
                if karaka:
                    label = f"{glyph}({karaka})"
                svg.append(
                    f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle"'
                    f' dominant-baseline="central" font-size="11"'
                    f' font-weight="bold" fill="{color}">'
                    f'{_esc(label)}</text>'
                )

    # Draw Rashi Drishti arrows (only for occupied signs)
    occupied_signs = set()
    for p in chart.planets:
        occupied_signs.add(_sign_index(p.longitude))

    drawn_pairs = set()
    for src_sign in occupied_signs:
        for tgt_sign in JAIMINI_RASHI_DRISHTI.get(src_sign, []):
            pair = tuple(sorted([src_sign, tgt_sign]))
            if pair in drawn_pairs:
                continue
            drawn_pairs.add(pair)

            # Arrow from src to tgt through the inner circle
            src_sector = (src_sign - asc_sign) % 12
            tgt_sector = (tgt_sign - asc_sign) % 12
            a_src = math.radians(-90 + src_sector * 30 + 15)
            a_tgt = math.radians(-90 + tgt_sector * 30 + 15)
            r_arr = R_INNER - 15
            sx = CX + r_arr * math.cos(a_src)
            sy = CY + r_arr * math.sin(a_src)
            tx = CX + r_arr * math.cos(a_tgt)
            ty = CY + r_arr * math.sin(a_tgt)
            svg.append(
                f'<line x1="{sx:.1f}" y1="{sy:.1f}"'
                f' x2="{tx:.1f}" y2="{ty:.1f}"'
                f' stroke="#ff9900" stroke-width="1" opacity="0.5"'
                f' marker-end="url(#jm-arrow)"/>'
            )

    # Centre circle with chart info
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_CENTRE}"'
        f' fill="#2a2a4a" stroke="#d4af37" stroke-width="1.5"/>'
    )
    info_lines = [
        ("Jaimini", 13, "bold", "#d4af37"),
        (f"{chart.year}/{chart.month}/{chart.day}", 10, "normal", "#bbb"),
        (f"{chart.hour:02d}:{chart.minute:02d} UTC{chart.timezone:+.1f}", 9, "normal", "#999"),
        (f"Ay: {chart.ayanamsa:.2f}°", 9, "normal", "#888"),
    ]
    for li, (text, size, weight, color) in enumerate(info_lines):
        svg.append(
            f'<text x="{CX}" y="{CY - 25 + li * 18}" text-anchor="middle"'
            f' font-size="{size}" font-weight="{weight}" fill="{color}">'
            f'{_esc(text)}</text>'
        )

    svg.append('</svg>')
    svg.append('</div>')
    return "\n".join(svg)


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_jaimini_chart(chart, after_chart_hook=None):
    """渲染完整的 Jaimini 占星排盤"""
    # SVG — Rashi Drishti chart
    svg = build_jaimini_rashi_chart_svg(chart)
    st.markdown(svg, unsafe_allow_html=True)

    if after_chart_hook:
        after_chart_hook()

    st.divider()
    _render_info(chart)
    st.divider()
    _render_chara_karaka_table(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_house_table(chart)
    st.divider()
    _render_rashi_drishti_section(chart)
    st.divider()
    _render_argala_section(chart)
    st.divider()
    _render_pada_section(chart)
    st.divider()
    _render_sthira_karaka_section(chart)


def _render_info(chart):
    """渲染基本排盤資訊"""
    lang = get_lang()
    title = "📋 排盤資訊 (Chart Information)" if lang == "zh" else "📋 Chart Information"
    st.subheader(title)
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**日期 (Date):** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**時間 (Time):** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**時區 (TZ):** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**地點 (Location):** {chart.location_name}")
        st.write(f"**Ayanamsa (歲差):** {chart.ayanamsa:.4f}°")
        st.write(f"**Lagna (命宮):** {chart.asc_rashi} "
                 f"{_format_deg(chart.ascendant)}")
        st.write(f"**House System:** Whole Sign")


def _render_chara_karaka_table(chart):
    """渲染 Chara Karaka（可變徵象星）表"""
    lang = get_lang()
    title = "🔮 Chara Karaka 可變徵象星" if lang == "zh" else "🔮 Chara Karaka (Variable Significators)"
    st.subheader(title)
    if lang == "zh":
        st.markdown(
            "**Chara Karaka** 依行星在星座內的度數高→低排列，"
            "決定每顆行星在 Jaimini 體系中扮演的角色。"
        )
    else:
        st.markdown(
            "**Chara Karaka** are assigned by ranking each planet's degree "
            "within its sign from highest to lowest."
        )

    header = "| Karaka | Planet | Abbr | Degree |"
    sep = "|:------|:------|:----:|:------:|"
    rows = [header, sep]
    for planet_name, karaka_name, abbr, degree in chart.chara_karakas:
        color = JAIMINI_PLANET_COLORS.get(planet_name, "#c8c8c8")
        planet_html = f'<span style="color:{color};font-weight:bold">{planet_name}</span>'
        # Find Chinese name for karaka
        karaka_cn = ""
        for kn, ka, kcn in JAIMINI_CHARA_KARAKA_NAMES:
            if kn == karaka_name:
                karaka_cn = kcn
                break
        rows.append(
            f"| **{karaka_name}** ({karaka_cn}) | {planet_html} "
            f"| {abbr} | {degree:.2f}° |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_planet_table(chart):
    """渲染行星位置表"""
    lang = get_lang()
    title = "🪐 行星位置 (Graha Positions)" if lang == "zh" else "🪐 Graha Positions"
    st.subheader(title)
    header = ("| Graha | Rashi | Degree | Quality | "
              "Nakshatra | Pada | House | CK | R |")
    sep = ("|:-----:|:-----:|:------:|:-------:|"
           ":--------:|:----:|:-----:|:--:|:-:|")
    rows = [header, sep]
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = JAIMINI_PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = (
            f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        )
        ck = p.chara_karaka_abbr if p.chara_karaka_abbr else "—"
        rows.append(
            f"| {name_html} | {p.rashi_glyph} {p.rashi} ({p.rashi_chinese}) "
            f"| {p.sign_degree:.2f}° | {p.rashi_quality} "
            f"| {p.nakshatra} ({p.nakshatra_chinese}) "
            f"| {p.nakshatra_pada} | {p.house} | {ck} | {retro} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_house_table(chart):
    """渲染宮位表"""
    lang = get_lang()
    title = "🏛️ 宮位 Whole Sign (Bhava)" if lang == "zh" else "🏛️ Bhava (Whole Sign Houses)"
    st.subheader(title)
    header = "| Bhava | Rashi | Quality | Planets |"
    sep = "|:-----:|:-----:|:-------:|:-------:|"
    rows = [header, sep]
    for h in chart.houses:
        planets_str = ", ".join(h.planets) if h.planets else "—"
        rows.append(
            f"| {h.number} | {h.rashi_glyph} {h.rashi} "
            f"| {h.rashi_quality} | {planets_str} |"
        )
    st.markdown("\n".join(rows))


def _render_rashi_drishti_section(chart):
    """渲染 Rashi Drishti 星座視線"""
    lang = get_lang()
    title = "👁️ Rashi Drishti 星座視線" if lang == "zh" else "👁️ Rashi Drishti (Sign Aspects)"
    st.subheader(title)
    if lang == "zh":
        st.markdown(
            "**Rashi Drishti** 是 Jaimini 體系獨有的視線系統：\n"
            "- 活動星座 (Chara) ↔ 固定星座 (Sthira) 互視\n"
            "- 雙體星座 (Dwiswabhava) 之間互視\n"
            "- 圖中橙色箭頭顯示有行星之星座的視線關係"
        )
    else:
        st.markdown(
            "**Rashi Drishti** is unique to Jaimini:\n"
            "- Cardinal (Chara) ↔ Fixed (Sthira) signs aspect each other\n"
            "- Dual (Dwiswabhava) signs aspect each other\n"
            "- Orange arrows in the chart show aspect relationships for occupied signs"
        )

    # Table of aspects for occupied houses
    occupied = set()
    for p in chart.planets:
        occupied.add(_sign_index(p.longitude))

    header = "| Sign | Quality | Aspects |"
    sep = "|:-----|:-------:|:--------|"
    rows = [header, sep]
    for si in sorted(occupied):
        rashi = JAIMINI_RASHIS[si]
        aspects = chart.rashi_drishti.get(si, [])
        aspect_names = [f"{JAIMINI_RASHIS[a][1]} {JAIMINI_RASHIS[a][0]}" for a in aspects]
        rows.append(
            f"| {rashi[1]} {rashi[0]} ({rashi[2]}) | {rashi[4]} "
            f"| {', '.join(aspect_names)} |"
        )
    st.markdown("\n".join(rows))


def _render_argala_section(chart):
    """渲染 Argala 與 Virodhargala 分析"""
    lang = get_lang()
    title = "🔗 Argala 介入分析" if lang == "zh" else "🔗 Argala (Intervention Analysis)"
    st.subheader(title)
    if lang == "zh":
        st.markdown(
            "**Argala**（介入）是 Jaimini 體系中的特殊影響力分析。\n"
            "**Virodhargala**（阻擋）可抵消 Argala 的效果。"
        )
    else:
        st.markdown(
            "**Argala** (intervention) shows special influence analysis.\n"
            "**Virodhargala** (obstruction) can nullify Argala effects."
        )

    if not chart.argala:
        st.info("No active Argala found." if lang == "en" else "未發現有效的 Argala。")
        return

    header = ("| Target | Type | Argala House | Planets | "
              "Obstruct House | Obstruct Planets | Status |")
    sep = ("|:------:|:-----|:------------:|:--------|"
           ":-------------:|:----------------|:------:|")
    rows = [header, sep]
    for a in chart.argala:
        a_type = a.argala_type_en if lang == "en" else a.argala_type_zh
        a_planets = ", ".join(a.argala_planets) if a.argala_planets else "—"
        v_planets = ", ".join(a.virodhargala_planets) if a.virodhargala_planets else "—"
        status = "❌ Obstructed" if a.is_obstructed else "✅ Active"
        rows.append(
            f"| H{a.target_house} | {a_type} | H{a.argala_house} "
            f"| {a_planets} | H{a.virodhargala_house} "
            f"| {v_planets} | {status} |"
        )
    st.markdown("\n".join(rows))


def _render_pada_section(chart):
    """渲染 Arudha Pada（虛象宮）"""
    lang = get_lang()
    title = "🎯 Arudha Pada 虛象宮" if lang == "zh" else "🎯 Arudha Pada"
    st.subheader(title)
    if lang == "zh":
        st.markdown(
            "**Arudha Pada**（虛象宮）反映外在世界對命主的感知。"
            "AL = 命宮虛象，UL = 婚姻虛象，A7 = 伴侶虛象。"
        )
    else:
        st.markdown(
            "**Arudha Pada** reflects how the world perceives the native. "
            "AL = Arudha Lagna, UL = Upapada, A7 = Darapada."
        )

    header = "| House | Label | Pada Sign |"
    sep = "|:-----:|:-----:|:----------|"
    rows = [header, sep]
    for pd in chart.padas:
        rows.append(
            f"| H{pd.house} | **{pd.label}** "
            f"| {pd.pada_sign_glyph} {pd.pada_sign} |"
        )
    st.markdown("\n".join(rows))


def _render_sthira_karaka_section(chart):
    """渲染 Sthira Karaka（固定徵象星）"""
    lang = get_lang()
    title = "⚓ Sthira Karaka 固定徵象星" if lang == "zh" else "⚓ Sthira Karaka (Fixed Significators)"
    st.subheader(title)
    if lang == "zh":
        st.markdown(
            "**Sthira Karaka** 與 Chara Karaka 不同，"
            "每顆行星永遠代表固定的主題，不因度數而改變。"
        )
    else:
        st.markdown(
            "**Sthira Karaka** differ from Chara Karaka — "
            "each planet permanently represents fixed themes."
        )

    header = "| Planet | Signification |"
    sep = "|:------|:-------------|"
    rows = [header, sep]
    for planet_en, planet_zh, sig_zh, sig_en in chart.sthira_karakas:
        if lang == "zh":
            rows.append(f"| **{planet_en}** ({planet_zh}) | {sig_zh} |")
        else:
            rows.append(f"| **{planet_en}** | {sig_en} |")
    st.markdown("\n".join(rows))


def render_jaimini_dasha(chart):
    """渲染 Chara Dasha 大運"""
    lang = get_lang()
    title = "📅 Chara Dasha 可變大運" if lang == "zh" else "📅 Chara Dasha"
    st.subheader(title)
    if lang == "zh":
        st.markdown(
            "**Chara Dasha** 以星座為單位的大運系統，"
            "是 Jaimini 體系最重要的預測工具。"
        )
    else:
        st.markdown(
            "**Chara Dasha** is a sign-based dasha system, "
            "the most important predictive tool in the Jaimini system."
        )

    header = "| Sign | Years | Start | End |"
    sep = "|:-----|:-----:|:-----:|:---:|"
    rows = [header, sep]
    for d in chart.chara_dasha:
        rows.append(
            f"| {d.sign_glyph} {d.sign} ({d.sign_chinese}) "
            f"| {d.years} | {d.start_year:.1f} | {d.end_year:.1f} |"
        )
    st.markdown("\n".join(rows))
