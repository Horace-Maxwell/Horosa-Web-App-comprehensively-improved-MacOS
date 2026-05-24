"""
納迪占星排盤模組 (Nadi Astrology Chart Module)

納迪占星 (Nadi Jyotish) 源自南印度泰米爾那德邦的古代棕櫚葉手稿傳統，
以三種「納迪脈輪」為核心，透過行星所在星宿判斷體質、性格與命運走向：

- **三大納迪脈輪**：
  - Aadi Nadi（初脈 / 風型 Vata）：神經系統、思維活動、風元素
  - Madhya Nadi（中脈 / 火型 Pitta）：消化代謝、熱情意志、火元素
  - Antya Nadi（末脈 / 水型 Kapha）：體液免疫、穩定耐力、水土元素

- **27 星宿 Nakshatra** 依次歸屬三大脈輪，每 9 宿為一輪
- **納迪宮分 (Nadi Amsha)**：每宮 30° 分成 150 個小分，每小分 12'
- **命主納迪 (Janma Nadi)**：以出生月亮所在星宿決定
- **上升納迪 (Lagna Nadi)**：以上升點所在星宿決定

使用 pyswisseph 以恆星黃道 (sidereal zodiac / Lahiri ayanamsa) 計算。
"""

import json
import os
import re

import pandas as pd
import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

# ── Nadi JSON Data ────────────────────────────────────────────────────────────
_NADI_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "nadi", "data")


@st.cache_data(show_spinner=False)
def _load_nadi_json(filename: str) -> dict:
    path = os.path.join(_NADI_DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_nakshatra_guna_data() -> dict:
    return _load_nadi_json("nadi_nakshatra_guna.json")


def _get_planet_nakshatra_data() -> dict:
    return _load_nadi_json("nadi_planet_nakshatra.json")


def _get_nadi_yogas_data() -> dict:
    return _load_nadi_json("nadi_yogas.json")


def _get_nadi_bhavas_data() -> dict:
    return _load_nadi_json("nadi_bhavas.json")


# Mapping from nadi.py planet names to JSON planet keys
_PLANET_NAME_TO_JSON_KEY = {
    "Surya": "sun",
    "Chandra": "moon",
    "Mangal": "mars",
    "Budha": "mercury",
    "Guru": "jupiter",
    "Shukra": "venus",
    "Shani": "saturn",
    "Rahu": "rahu",
    "Ketu": "ketu",
}

# Alternate nakshatra spellings → nakshatra index (0-based)
_NAKSHATRA_ALT_NAMES: dict[str, int] = {
    "aswini": 0, "ashwini": 0,
    "bharani": 1,
    "krithika": 2, "krittika": 2,
    "rohini": 3,
    "mrigasira": 4, "mrigashira": 4,
    "arudra": 5, "ardra": 5,
    "punarvasu": 6,
    "pushyami": 7, "pushya": 7,
    "aslesha": 8, "ashlesha": 8,
    "makha": 9, "magha": 9,
    "pubba": 10, "purva phalguni": 10,
    "uttara": 11, "uttara phalguni": 11,
    "hasta": 12,
    "chitha": 13, "chitra": 13,
    "swati": 14,
    "visaka": 15, "vishakha": 15,
    "anuradha": 16,
    "jyeshta": 17, "jyeshtha": 17,
    "mula": 18,
    "purvashada": 19, "purva ashadha": 19,
    "uttarashada": 20, "uttara ashadha": 20,
    "sravana": 21, "shravana": 21,
    "dhanishta": 22,
    "satabisha": 23, "shatabhisha": 23,
    "purvabhadrapada": 24, "purva bhadrapada": 24,
    "uttarabhadrapada": 25, "uttara bhadrapada": 25,
    "revati": 26,
}


def _extract_nakshatra_indices_from_group(group_str: str) -> set[int]:
    """Extract nakshatra indices mentioned in a nakshatra_group string.

    The group strings use full-width Chinese parentheses （…） to enclose a
    comma- or 、-separated list of nakshatra names, e.g.
    ``'月亮星宿（Rohini、Hasta、Sravana）'``.
    """
    # Extract text inside full-width parentheses （…）
    m = re.search(r"（(.+?)）", group_str)
    if not m:
        return set()
    inner = m.group(1)
    # Split by "、" or ","
    names = [n.strip().lower() for n in re.split(r"[、,]", inner)]
    indices = set()
    for name in names:
        idx = _NAKSHATRA_ALT_NAMES.get(name)
        if idx is not None:
            indices.add(idx)
    return indices


def _match_planet_nakshatra_effect(planet_name: str, nakshatra_index: int) -> str | None:
    """
    Given a planet name (e.g. 'Surya (太陽)') and its nakshatra index,
    return the matching effect description from nadi_planet_nakshatra.json,
    or None if no match found.
    """
    parts = planet_name.split("(", 1)
    key_part = parts[0].strip()
    tokens = key_part.split()
    if not tokens:
        return None
    json_key = _PLANET_NAME_TO_JSON_KEY.get(tokens[0])
    if not json_key:
        return None
    effects_data = _get_planet_nakshatra_data().get("planet_nakshatra_effects", {})
    planet_effects = effects_data.get(json_key, {}).get("effects", [])
    for eff in planet_effects:
        indices = _extract_nakshatra_indices_from_group(eff.get("nakshatra_group", ""))
        if nakshatra_index in indices:
            return eff.get("description", "")
    return None


def _nakshatra_guna_entry(nakshatra_index: int, nak_keys: list, guna_data: dict) -> dict | None:
    """Return the guna data entry for a 0-based nakshatra index, or None if out of range."""
    if nakshatra_index < 0 or nakshatra_index >= len(nak_keys):
        return None
    return guna_data.get(nak_keys[nakshatra_index])


# ============================================================
# 常量 (Constants)
# ============================================================

# 三大納迪脈輪 (Nadi types)
# 0 = Aadi (初脈/風型 Vata)
# 1 = Madhya (中脈/火型 Pitta)
# 2 = Antya (末脈/水型 Kapha)
NADI_NAMES = [
    {
        "english":   "Aadi Nadi",
        "chinese":   "初脈",
        "element":   "風型 (Vata)",
        "element_cn":"風 / 神經",
        "color":     "#4A90D9",
        "symbol":    "🌬️",
        "body":      "神經系統、呼吸系統",
        "traits":    "靈活善變、思維活躍、創意豐富；但易過度焦慮、注意力分散",
        "health":    "易患神經系統疾病、皮膚乾燥、關節問題",
        "career":    "適合思想型工作：教育、研究、媒體、藝術",
        "marriage":  "兩人皆屬 Aadi Nadi 時婚配不宜（Nadi Dosha），建議避免",
    },
    {
        "english":   "Madhya Nadi",
        "chinese":   "中脈",
        "element":   "火型 (Pitta)",
        "element_cn":"火 / 代謝",
        "color":     "#E8542A",
        "symbol":    "🔥",
        "body":      "消化系統、肝膽、血液循環",
        "traits":    "意志堅定、有領導力、熱情積極；但易急躁、固執、好勝",
        "health":    "易患消化問題、發炎、血壓偏高",
        "career":    "適合行動型工作：管理、法律、醫學、軍政",
        "marriage":  "兩人皆屬 Madhya Nadi 時婚配不宜（Nadi Dosha），建議避免",
    },
    {
        "english":   "Antya Nadi",
        "chinese":   "末脈",
        "element":   "水型 (Kapha)",
        "element_cn":"水土 / 免疫",
        "color":     "#2ECC71",
        "symbol":    "💧",
        "body":      "免疫系統、淋巴系統、骨骼肌肉",
        "traits":    "沉穩踏實、耐心持久、感情豐富；但易遲緩、依賴、抗拒改變",
        "health":    "易患痰濕積聚、肥胖、水腫",
        "career":    "適合支援型工作：財務、行政、護理、農業",
        "marriage":  "兩人皆屬 Antya Nadi 時婚配不宜（Nadi Dosha），建議避免",
    },
]

# 27 星宿對納迪脈輪的歸屬
# 順序：Aadi(0), Madhya(1), Antya(2), Antya(2), Madhya(1), Aadi(0) 每 6 宿一循環
# 索引 0-26 對應 Ashwini 至 Revati
NAKSHATRA_NADI = [
    0,  # 0  Ashwini        — Aadi  (初脈)
    1,  # 1  Bharani        — Madhya (中脈)
    2,  # 2  Krittika       — Antya (末脈)
    2,  # 3  Rohini         — Antya (末脈)
    1,  # 4  Mrigashira     — Madhya (中脈)
    0,  # 5  Ardra          — Aadi  (初脈)
    0,  # 6  Punarvasu      — Aadi  (初脈)
    1,  # 7  Pushya         — Madhya (中脈)
    2,  # 8  Ashlesha       — Antya (末脈)
    2,  # 9  Magha          — Antya (末脈)
    1,  # 10 Purva Phalguni — Madhya (中脈)
    0,  # 11 Uttara Phalguni— Aadi  (初脈)
    0,  # 12 Hasta          — Aadi  (初脈)
    1,  # 13 Chitra         — Madhya (中脈)
    2,  # 14 Swati          — Antya (末脈)
    2,  # 15 Vishakha       — Antya (末脈)
    1,  # 16 Anuradha       — Madhya (中脈)
    0,  # 17 Jyeshtha       — Aadi  (初脈)
    0,  # 18 Mula           — Aadi  (初脈)
    1,  # 19 Purva Ashadha  — Madhya (中脈)
    2,  # 20 Uttara Ashadha — Antya (末脈)
    2,  # 21 Shravana       — Antya (末脈)
    1,  # 22 Dhanishta      — Madhya (中脈)
    0,  # 23 Shatabhisha    — Aadi  (初脈)
    0,  # 24 Purva Bhadrapada— Aadi (初脈)
    1,  # 25 Uttara Bhadrapada— Madhya(中脈)
    2,  # 26 Revati         — Antya (末脈)
]

# 27 星宿名稱（與 indian.py 一致）
NAKSHATRA_NAMES = [
    ("Ashwini",           "阿什維尼"),
    ("Bharani",           "巴拉尼"),
    ("Krittika",          "昴宿"),
    ("Rohini",            "畢宿"),
    ("Mrigashira",        "觜宿"),
    ("Ardra",             "參宿"),
    ("Punarvasu",         "井宿"),
    ("Pushya",            "鬼宿"),
    ("Ashlesha",          "柳宿"),
    ("Magha",             "星宿"),
    ("Purva Phalguni",    "張宿"),
    ("Uttara Phalguni",   "翼宿"),
    ("Hasta",             "軫宿"),
    ("Chitra",            "角宿"),
    ("Swati",             "亢宿"),
    ("Vishakha",          "氐宿"),
    ("Anuradha",          "房宿"),
    ("Jyeshtha",          "心宿"),
    ("Mula",              "尾宿"),
    ("Purva Ashadha",     "箕宿"),
    ("Uttara Ashadha",    "斗宿"),
    ("Shravana",          "牛宿"),
    ("Dhanishta",         "女宿"),
    ("Shatabhisha",       "虛宿"),
    ("Purva Bhadrapada",  "危宿"),
    ("Uttara Bhadrapada", "室宿"),
    ("Revati",            "壁宿"),
]

# 行星名稱（納迪排盤用）
NADI_PLANETS = {
    "Surya (太陽)":    swe.SUN,
    "Chandra (月亮)":  swe.MOON,
    "Mangal (火星)":   swe.MARS,
    "Budha (水星)":    swe.MERCURY,
    "Guru (木星)":     swe.JUPITER,
    "Shukra (金星)":   swe.VENUS,
    "Shani (土星)":    swe.SATURN,
}

# 十二宮星座
RASHIS = [
    ("Mesha",      "♈", "白羊"),
    ("Vrishabha",  "♉", "金牛"),
    ("Mithuna",    "♊", "雙子"),
    ("Karka",      "♋", "巨蟹"),
    ("Simha",      "♌", "獅子"),
    ("Kanya",      "♍", "處女"),
    ("Tula",       "♎", "天秤"),
    ("Vrischika",  "♏", "天蠍"),
    ("Dhanu",      "♐", "射手"),
    ("Makara",     "♑", "摩羯"),
    ("Kumbha",     "♒", "水瓶"),
    ("Meena",      "♓", "雙魚"),
]

# 行星顯示顏色
PLANET_COLORS = {
    "Surya (太陽)":    "#FF8C00",
    "Chandra (月亮)":  "#8888CC",
    "Mangal (火星)":   "#DC143C",
    "Budha (水星)":    "#228B22",
    "Guru (木星)":     "#DAA520",
    "Shukra (金星)":   "#FF69B4",
    "Shani (土星)":    "#8B4513",
    "Rahu (羅睺)":     "#800080",
    "Ketu (計都)":     "#4B0082",
}

# 納迪宮分描述（每宮 150 宮分，每個 12'）
NADI_AMSHA_PER_SIGN = 150

# 納迪宮分吉凶分類（1-50 = 初段, 51-100 = 中段, 101-150 = 末段）
NADI_AMSHA_SECTION = [
    (1,   50,  "初段 (Aadi Section)",  "初生、成長、自我發展", "#4A90D9"),
    (51,  100, "中段 (Madhya Section)", "成熟、事業、家庭關係", "#E8542A"),
    (101, 150, "末段 (Antya Section)",  "蛻變、靈性、人生收穫", "#2ECC71"),
]


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class NadiPlanet:
    """納迪行星資料"""
    name: str
    longitude: float
    rashi: str
    rashi_glyph: str
    rashi_chinese: str
    sign_degree: float
    nakshatra: str
    nakshatra_chinese: str
    nakshatra_index: int
    nakshatra_pada: int
    nadi_type: int          # 0=Aadi, 1=Madhya, 2=Antya
    nadi_name_cn: str
    nadi_amsha: int         # 1–150
    retrograde: bool


@dataclass
class NadiChart:
    """納迪占星命盤"""
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
    planets: list
    ascendant_lon: float
    asc_nakshatra: str
    asc_nakshatra_chinese: str
    asc_nakshatra_index: int
    asc_nadi_type: int
    asc_nadi_name_cn: str
    asc_rashi: str
    asc_rashi_cn: str
    janma_nadi_type: int        # Moon's nadi
    janma_nadi_name_cn: str
    janma_nakshatra: str
    janma_nakshatra_cn: str


# ============================================================
# 計算函數 (Calculation Functions)
# ============================================================

def _normalize(deg: float) -> float:
    return deg % 360.0


def _sign_index(deg: float) -> int:
    return int(_normalize(deg) / 30.0)


def _sign_degree(deg: float) -> float:
    return _normalize(deg) % 30.0


def _nakshatra_info(deg: float):
    """返回 (nakshatra_index, pada) — 以恆星黃道度數計算。"""
    deg = _normalize(deg)
    span = 360.0 / 27.0          # 13°20'
    idx = int(deg / span) % 27
    pada = int((deg % span) / (span / 4.0)) + 1
    return idx, min(pada, 4)


def _nadi_amsha(sign_deg: float) -> int:
    """計算納迪宮分 (1–150)。每宮 30°，分 150 份，每份 0.2°。"""
    return min(int(sign_deg / 0.2) + 1, NADI_AMSHA_PER_SIGN)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_nadi_chart(year, month, day, hour, minute, timezone,
                       latitude, longitude, location_name="") -> NadiChart:
    """計算納迪占星命盤（使用恆星黃道 Lahiri 歲差）。"""
    swe.set_ephe_path("")
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # 計算上升點
    _, ascmc = swe.houses_ex(jd, latitude, longitude, b"P", swe.FLG_SIDEREAL)
    asc_lon = _normalize(ascmc[0])
    asc_nak_idx, _ = _nakshatra_info(asc_lon)
    asc_nak = NAKSHATRA_NAMES[asc_nak_idx]
    asc_nadi = NAKSHATRA_NADI[asc_nak_idx]
    asc_sign_idx = _sign_index(asc_lon)

    planets = []
    moon_planet = None

    for name, pid in NADI_PLANETS.items():
        result, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        lon = _normalize(result[0])
        speed = result[3]
        nak_idx, pada = _nakshatra_info(lon)
        nadi_type = NAKSHATRA_NADI[nak_idx]
        sign_deg = _sign_degree(lon)
        amsha = _nadi_amsha(sign_deg)
        sign_idx = _sign_index(lon)
        rashi = RASHIS[sign_idx]
        nak = NAKSHATRA_NAMES[nak_idx]

        p = NadiPlanet(
            name=name, longitude=lon,
            rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
            sign_degree=sign_deg,
            nakshatra=nak[0], nakshatra_chinese=nak[1],
            nakshatra_index=nak_idx, nakshatra_pada=pada,
            nadi_type=nadi_type,
            nadi_name_cn=NADI_NAMES[nadi_type]["chinese"],
            nadi_amsha=amsha,
            retrograde=(speed < 0),
        )
        planets.append(p)
        if name == "Chandra (月亮)":
            moon_planet = p

    # Rahu（平均北交點）
    rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _normalize(rahu_res[0])
    nak_idx, pada = _nakshatra_info(rahu_lon)
    sign_deg = _sign_degree(rahu_lon)
    sign_idx = _sign_index(rahu_lon)
    rashi = RASHIS[sign_idx]
    nak = NAKSHATRA_NAMES[nak_idx]
    planets.append(NadiPlanet(
        name="Rahu (羅睺)", longitude=rahu_lon,
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        sign_degree=sign_deg,
        nakshatra=nak[0], nakshatra_chinese=nak[1],
        nakshatra_index=nak_idx, nakshatra_pada=pada,
        nadi_type=NAKSHATRA_NADI[nak_idx],
        nadi_name_cn=NADI_NAMES[NAKSHATRA_NADI[nak_idx]]["chinese"],
        nadi_amsha=_nadi_amsha(sign_deg),
        retrograde=False,
    ))

    # Ketu（南交點 = Rahu + 180°）
    ketu_lon = _normalize(rahu_lon + 180.0)
    nak_idx, pada = _nakshatra_info(ketu_lon)
    sign_deg = _sign_degree(ketu_lon)
    sign_idx = _sign_index(ketu_lon)
    rashi = RASHIS[sign_idx]
    nak = NAKSHATRA_NAMES[nak_idx]
    planets.append(NadiPlanet(
        name="Ketu (計都)", longitude=ketu_lon,
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        sign_degree=sign_deg,
        nakshatra=nak[0], nakshatra_chinese=nak[1],
        nakshatra_index=nak_idx, nakshatra_pada=pada,
        nadi_type=NAKSHATRA_NADI[nak_idx],
        nadi_name_cn=NADI_NAMES[NAKSHATRA_NADI[nak_idx]]["chinese"],
        nadi_amsha=_nadi_amsha(sign_deg),
        retrograde=False,
    ))

    # 命主納迪 = 月亮星宿的納迪
    if moon_planet:
        janma_nadi_type = moon_planet.nadi_type
        janma_nak = moon_planet.nakshatra
        janma_nak_cn = moon_planet.nakshatra_chinese
    else:
        janma_nadi_type = 0
        janma_nak = ""
        janma_nak_cn = ""

    return NadiChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd, ayanamsa=ayanamsa,
        planets=planets,
        ascendant_lon=asc_lon,
        asc_nakshatra=asc_nak[0], asc_nakshatra_chinese=asc_nak[1],
        asc_nakshatra_index=asc_nak_idx,
        asc_nadi_type=asc_nadi,
        asc_nadi_name_cn=NADI_NAMES[asc_nadi]["chinese"],
        asc_rashi=RASHIS[asc_sign_idx][0],
        asc_rashi_cn=RASHIS[asc_sign_idx][2],
        janma_nadi_type=janma_nadi_type,
        janma_nadi_name_cn=NADI_NAMES[janma_nadi_type]["chinese"],
        janma_nakshatra=janma_nak,
        janma_nakshatra_cn=janma_nak_cn,
    )


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def _nadi_badge(nadi_type: int) -> str:
    """返回 Markdown 格式的納迪徽章。"""
    info = NADI_NAMES[nadi_type]
    return f"**{info['symbol']} {info['chinese']} ({info['element']})**"


def _render_nadi_south_indian_grid(chart: NadiChart) -> None:
    """渲染納迪占星南印度式方盤，行星以納迪脈輪色標示。"""
    st.subheader("📊 納迪星盤 (Nadi Chart — South Indian Style)")

    # South Indian chart: fixed rashi positions in 4×4 grid
    si_grid = [
        [3, 2, 1, 0],       # Cancer  Gemini  Taurus  Aries
        [4, -1, -1, 11],    # Leo     [center]        Pisces
        [5, -1, -1, 10],    # Virgo   [center]        Aquarius
        [6, 7, 8, 9],       # Libra   Scorpio Sagitt  Capricorn
    ]

    # Group planets by rashi index
    rashi_planets: dict[int, list] = {i: [] for i in range(12)}
    for p in chart.planets:
        idx = _sign_index(p.longitude)
        short = p.name.split(" ")[0]
        rashi_planets[idx].append((short, p.name, p.nadi_type, p.retrograde))

    asc_idx = _sign_index(chart.ascendant_lon)

    cell_style = (
        "border:1px solid #444; padding:6px; text-align:center; "
        "vertical-align:top; font-size:13px; word-break:break-word;"
    )
    asc_cell_style = cell_style + " background:#3d3010;"
    center_style = (
        "border:1px solid #444; padding:10px; text-align:center; "
        "vertical-align:middle; font-size:14px; background:#2a2a2a; "
        "color:#e0e0e0;"
    )

    html = (
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        '<table style="border-collapse:collapse; margin:auto; width:100%; min-width:280px; table-layout:fixed;">'
    )
    for row_idx, row in enumerate(si_grid):
        html += "<tr>"
        col_idx = 0
        while col_idx < len(row):
            idx = row[col_idx]
            if idx == -1:
                if row_idx == 1 and col_idx == 1:
                    # Center cell: chart info
                    asc_nadi = NADI_NAMES[chart.asc_nadi_type]
                    j_nadi = NADI_NAMES[chart.janma_nadi_type]
                    center_content = (
                        f"<b>🔱 Nadi Jyotish</b><br/>"
                        f"{chart.year}/{chart.month}/{chart.day} "
                        f"{chart.hour:02d}:{chart.minute:02d}<br/>"
                        f"UTC{chart.timezone:+.1f} {chart.location_name}<br/>"
                        f"<small>Ayanamsa: {chart.ayanamsa:.2f}°</small><br/>"
                        f"<small>命主: {j_nadi['symbol']}{j_nadi['chinese']} "
                        f"上升: {asc_nadi['symbol']}{asc_nadi['chinese']}</small>"
                    )
                    html += (
                        f'<td colspan="2" rowspan="2" '
                        f'style="{center_style}">{center_content}</td>'
                    )
                    col_idx += 2
                    continue
                else:
                    col_idx += 1
                    continue
            else:
                rashi = RASHIS[idx]
                style = asc_cell_style if idx == asc_idx else cell_style
                p_list = rashi_planets[idx]
                if p_list:
                    p_parts = []
                    for short, full, nadi_type, retro in p_list:
                        nadi_color = NADI_NAMES[nadi_type]["color"]
                        retro_mark = "℞" if retro else ""
                        p_parts.append(
                            f'<span style="color:{nadi_color};font-weight:bold">'
                            f'{short}{retro_mark}</span>'
                        )
                    p_html = " ".join(p_parts)
                else:
                    p_html = '<span style="color:#999">—</span>'
                marker = " 🔺" if idx == asc_idx else ""
                cell_content = (
                    f"<b>{rashi[0]}{marker}</b><br/>"
                    f'<small style="color:#888">{rashi[1]} {rashi[2]}</small>'
                    f"<br/>{p_html}"
                )
                html += f'<td style="{style}">{cell_content}</td>'
            col_idx += 1
        html += "</tr>"
    html += "</table></div>"

    # Nadi color legend
    legend_parts = []
    for nadi in NADI_NAMES:
        legend_parts.append(
            f'<span style="color:{nadi["color"]};font-weight:bold">'
            f'{nadi["symbol"]} {nadi["chinese"]} ({nadi["english"]})</span>'
        )
    html += (
        '<p style="text-align:center;margin-top:6px;font-size:13px">'
        f'行星色彩：{" &nbsp;|&nbsp; ".join(legend_parts)}</p>'
    )

    st.markdown(html, unsafe_allow_html=True)


def render_nadi_chart(chart: NadiChart, after_chart_hook=None) -> None:
    """在 Streamlit 中渲染納迪占星命盤。"""

    st.subheader("🔱 納迪占星 (Nadi Jyotish) 命盤")

    # ---- 納迪星盤（南印度式） ----
    _render_nadi_south_indian_grid(chart)

    if after_chart_hook:
        after_chart_hook()

    st.divider()

    # ---- 基本資訊 ----
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("出生日期", f"{chart.year}-{chart.month:02d}-{chart.day:02d}")
        st.metric("出生時間", f"{chart.hour:02d}:{chart.minute:02d}")
    with col2:
        st.metric("出生地點", chart.location_name or "自訂地點")
        st.metric("歲差修正 (Ayanamsa)", f"{chart.ayanamsa:.4f}°")
    with col3:
        jnadi = NADI_NAMES[chart.janma_nadi_type]
        st.metric(
            "命主納迪 (Janma Nadi)",
            f"{jnadi['symbol']} {jnadi['chinese']}",
            help="由出生月亮星宿決定"
        )
        lnadi = NADI_NAMES[chart.asc_nadi_type]
        st.metric(
            "上升納迪 (Lagna Nadi)",
            f"{lnadi['symbol']} {lnadi['chinese']}",
            help="由上升點星宿決定"
        )

    st.divider()

    # ---- 三大脈輪說明卡 ----
    st.subheader("三大納迪脈輪 (Three Nadi Channels)")
    cols = st.columns(3)
    for i, (col, nadi) in enumerate(zip(cols, NADI_NAMES)):
        with col:
            is_janma = (i == chart.janma_nadi_type)
            is_lagna = (i == chart.asc_nadi_type)
            border = "3px solid gold" if is_janma else "1px solid #444"
            tag = ""
            if is_janma:
                tag += " 🌙命主"
            if is_lagna:
                tag += " ⬆️上升"
            st.markdown(
                f"""<div style="border:{border};border-radius:8px;padding:12px;
                    background:linear-gradient(135deg,{nadi['color']}22,#111);
                    margin-bottom:4px">
                <h4 style="margin:0;color:{nadi['color']}">{nadi['symbol']} {nadi['english']}
                  {nadi['chinese']}{tag}</h4>
                <p style="margin:4px 0 2px;font-size:0.85em">
                  <b>元素</b>：{nadi['element_cn']}<br>
                  <b>身體</b>：{nadi['body']}<br>
                  <b>特質</b>：{nadi['traits']}<br>
                  <b>健康</b>：{nadi['health']}<br>
                  <b>事業</b>：{nadi['career']}
                </p></div>""",
                unsafe_allow_html=True,
            )

    st.divider()

    # ---- 上升點資訊 ----
    st.subheader("上升點 (Lagna / Ascendant)")
    asc_nadi = NADI_NAMES[chart.asc_nadi_type]
    st.markdown(
        f"**上升星座**：{chart.asc_rashi} {chart.asc_rashi_cn} "
        f"&nbsp;|&nbsp; **上升度數**：{chart.ascendant_lon:.2f}° "
        f"&nbsp;|&nbsp; **上升星宿**：{chart.asc_nakshatra} ({chart.asc_nakshatra_chinese}) "
        f"&nbsp;|&nbsp; **上升納迪**：{asc_nadi['symbol']} {asc_nadi['chinese']} ({asc_nadi['element']})"
    )

    st.divider()

    # ---- 行星納迪表 ----
    st.subheader("行星納迪分布 (Planetary Nadi Positions)")

    # 按納迪類型分組顯示
    nadi_groups: dict[int, list] = {0: [], 1: [], 2: []}
    for p in chart.planets:
        nadi_groups[p.nadi_type].append(p)

    group_cols = st.columns(3)
    for nadi_idx, col in enumerate(group_cols):
        nadi_info = NADI_NAMES[nadi_idx]
        planet_list = nadi_groups[nadi_idx]
        with col:
            st.markdown(
                f"<h4 style='color:{nadi_info['color']}'>"
                f"{nadi_info['symbol']} {nadi_info['chinese']} ({nadi_info['english']})</h4>",
                unsafe_allow_html=True,
            )
            if not planet_list:
                st.caption("（無行星）")
            for p in planet_list:
                retro = " ℞" if p.retrograde else ""
                color = PLANET_COLORS.get(p.name, "#aaa")
                st.markdown(
                    f"<span style='color:{color}'>●</span> **{p.name}**{retro}  \n"
                    f"<small>{p.rashi_glyph} {p.rashi} ({p.rashi_chinese}) "
                    f"{p.sign_degree:.1f}°&nbsp; "
                    f"| {p.nakshatra} ({p.nakshatra_chinese}) 第{p.nakshatra_pada}足 "
                    f"| 宮分 #{p.nadi_amsha}</small>",
                    unsafe_allow_html=True,
                )
            st.markdown("")

    st.divider()

    # ---- 詳細行星表 ----
    st.subheader("行星詳細資料")

    table_rows = []
    for p in chart.planets:
        nadi_info = NADI_NAMES[p.nadi_type]
        retro = "℞" if p.retrograde else "—"
        amsha_section = "初段" if p.nadi_amsha <= 50 else ("中段" if p.nadi_amsha <= 100 else "末段")
        table_rows.append({
            "行星": p.name,
            "黃道度數": f"{p.longitude:.2f}°",
            "星座 (Rashi)": f"{p.rashi_glyph} {p.rashi} {p.rashi_chinese}",
            "宮內度": f"{p.sign_degree:.2f}°",
            "星宿 (Nakshatra)": f"{p.nakshatra} ({p.nakshatra_chinese})",
            "足 (Pada)": p.nakshatra_pada,
            "納迪": f"{nadi_info['symbol']} {nadi_info['chinese']}",
            "宮分 (Amsha)": f"#{p.nadi_amsha} {amsha_section}",
            "逆行": retro,
        })

    import pandas as pd
    df = pd.DataFrame(table_rows)
    st.dataframe(df, width='stretch', hide_index=True)

    st.divider()

    # ---- 命主納迪解讀 ----
    st.subheader("命主納迪解讀 (Janma Nadi Reading)")
    jnadi_info = NADI_NAMES[chart.janma_nadi_type]
    lnadi_info = NADI_NAMES[chart.asc_nadi_type]

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            f"### {jnadi_info['symbol']} 命主納迪：{jnadi_info['chinese']} ({jnadi_info['english']})\n\n"
            f"**命主星宿**：{chart.janma_nakshatra} ({chart.janma_nakshatra_cn})\n\n"
            f"**元素屬性**：{jnadi_info['element']}\n\n"
            f"**身體關聯**：{jnadi_info['body']}\n\n"
            f"**性格特質**：{jnadi_info['traits']}\n\n"
            f"**健康提示**：{jnadi_info['health']}\n\n"
            f"**適合方向**：{jnadi_info['career']}"
        )
    with col_b:
        st.markdown(
            f"### {lnadi_info['symbol']} 上升納迪：{lnadi_info['chinese']} ({lnadi_info['english']})\n\n"
            f"**上升星宿**：{chart.asc_nakshatra} ({chart.asc_nakshatra_chinese})\n\n"
            f"**元素屬性**：{lnadi_info['element']}\n\n"
            f"**身體關聯**：{lnadi_info['body']}\n\n"
            f"**性格特質**：{lnadi_info['traits']}\n\n"
            f"**健康提示**：{lnadi_info['health']}\n\n"
            f"**適合方向**：{lnadi_info['career']}"
        )

    # 同一納迪警示
    if chart.janma_nadi_type == chart.asc_nadi_type:
        same_nadi = NADI_NAMES[chart.janma_nadi_type]
        st.warning(
            f"⚠️ **命主納迪與上升納迪相同**（均為 {same_nadi['chinese']}）\n\n"
            "在納迪匹配中，相同納迪的伴侶可能面臨 **Nadi Dosha（脈衝衝突）**，"
            "婚姻匹配時需謹慎考慮。建議諮詢傳統納迪占星師以確認完整影響。"
        )

    st.divider()

    # ---- 納迪宮分說明 ----
    st.subheader("納迪宮分 (Nadi Amsha) 說明")
    st.markdown(
        """
        **納迪宮分**是納迪占星中最精細的分區系統：

        | 宮分段落 | 範圍 | 含義 |
        |:---:|:---:|:---|
        | 初段 (Aadi Section) | 宮分 #1–50 | 初生、成長、自我發展階段 |
        | 中段 (Madhya Section) | 宮分 #51–100 | 成熟、事業、家庭關係階段 |
        | 末段 (Antya Section) | 宮分 #101–150 | 蛻變、靈性、人生收穫階段 |

        - 每個黃道宮（30°）分成 **150 個宮分**，每分跨度 **12 弧分（0.2°）**
        - 行星所在宮分可進一步細化 Nakshatra 的能量表現
        - 傳統棕櫚葉手稿根據宮分號碼對應特定的人生事件預言
        """
    )

    st.divider()
    _render_nakshatra_guna_section(chart)

    st.divider()
    _render_planet_nakshatra_effects_section(chart)

    st.divider()
    _render_yoga_section(chart)

    st.divider()
    _render_bhava_section()


# ── New render sections backed by JSON data ───────────────────────────────────

def _render_nakshatra_guna_section(chart: "NadiChart") -> None:
    """顯示每顆行星所在星宿的品質（Guna）解析。"""
    st.subheader("🌟 星宿品質解析 (Nakshatra Guna)")
    st.caption("根據《納迪棕櫚葉》傳統，每個星宿具有 Satwika（善性）、Rajasa（動性）或 Thamasic（惰性）品質，影響行星的表現方式。")

    guna_data = _get_nakshatra_guna_data().get("nakshatras", {})
    nak_keys = list(guna_data.keys())  # ordered list: '1_Aswini' … '27_Revati'

    rows = []
    # Include ascendant
    asc_entry = _nakshatra_guna_entry(chart.asc_nakshatra_index, nak_keys, guna_data)
    if asc_entry:
        rows.append({
            "行星 / 點": "⬆️ 上升 (Lagna)",
            "星宿": f"{chart.asc_nakshatra} ({chart.asc_nakshatra_chinese})",
            "品質 (Guna)": asc_entry.get("guna", "—"),
            "主星": asc_entry.get("ruler", "—"),
            "說明": asc_entry.get("description", ""),
        })

    for p in chart.planets:
        entry = _nakshatra_guna_entry(p.nakshatra_index, nak_keys, guna_data)
        if entry:
            rows.append({
                "行星 / 點": p.name,
                "星宿": f"{p.nakshatra} ({p.nakshatra_chinese})",
                "品質 (Guna)": entry.get("guna", "—"),
                "主星": entry.get("ruler", "—"),
                "說明": entry.get("description", ""),
            })

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch", hide_index=True)

    # Show planet_guna_change in expanders for planets with an interesting note
    with st.expander("▶ 行星品質轉化說明（點擊展開）"):
        for p in chart.planets:
            entry = _nakshatra_guna_entry(p.nakshatra_index, nak_keys, guna_data)
            if entry and entry.get("planet_guna_change"):
                st.markdown(f"**{p.name}** 在 {p.nakshatra}：{entry['planet_guna_change']}")


def _render_planet_nakshatra_effects_section(chart: "NadiChart") -> None:
    """依命盤行星所在星宿，顯示對應的納迪影響描述。"""
    st.subheader("🪐 行星星宿影響 (Planet-Nakshatra Effects)")
    st.caption("根據每顆行星落在特定星宿群的傳統解讀，以下為命盤中有對應記載的影響。")

    found_any = False
    for p in chart.planets:
        desc = _match_planet_nakshatra_effect(p.name, p.nakshatra_index)
        if desc:
            found_any = True
            color = PLANET_COLORS.get(p.name, "#888")
            nadi_info = NADI_NAMES[p.nadi_type]
            st.markdown(
                f"<div style='border-left:4px solid {color};padding:8px 12px;"
                f"margin:6px 0;background:linear-gradient(90deg,{color}11,transparent)'>"
                f"<b style='color:{color}'>{p.name}</b> "
                f"<span style='color:#aaa;font-size:0.85em'>"
                f"{p.nakshatra} ({p.nakshatra_chinese}) — {nadi_info['symbol']} {nadi_info['chinese']}"
                f"</span><br/>{desc}</div>",
                unsafe_allow_html=True,
            )

    if not found_any:
        st.info("命盤中的行星星宿位置未能在現有記錄中找到對應的特定描述，請參考星宿品質解析。")


def _render_yoga_section(chart: "NadiChart") -> None:
    """展示納迪瑜伽格局說明，並標示命主上升點的年命主星 (Yoga Karaka)。"""
    st.subheader("🔯 瑜伽格局 (Yoga Patterns)")

    yogas_data = _get_nadi_yogas_data()
    yogas = yogas_data.get("yogas", {})
    lagna_karakas = yogas_data.get("lagna_specific_yoga_karakas", {})

    # Lagna yoga karaka
    asc_rashi_key = chart.asc_rashi.lower() if chart.asc_rashi else ""
    karaka = lagna_karakas.get(asc_rashi_key)
    if karaka:
        st.info(
            f"⭐ **命主上升為 {chart.asc_rashi} ({chart.asc_rashi_cn})**，"
            f"年命主星（Yoga Karaka）為：**{karaka}**"
        )

    st.caption("以下為納迪占星主要瑜伽格局說明，供命盤解讀參考：")
    for yoga_key, yoga in yogas.items():
        with st.expander(f"🔸 {yoga.get('name', yoga_key)}"):
            st.markdown(f"**條件**：{yoga.get('conditions', '—')}")
            st.markdown(f"**效果**：{yoga.get('effect', '—')}")
            if yoga.get("notes"):
                st.markdown(f"**備注**：{yoga['notes']}")
            if yoga.get("guna_influence"):
                st.markdown(f"**品質影響**：{yoga['guna_influence']}")
            if yoga.get("related_bhavas"):
                st.markdown("**相關宮位**：" + "、".join(yoga["related_bhavas"]))


def _render_bhava_section() -> None:
    """展示十二宮 (Bhava) 的納迪解讀說明。"""
    st.subheader("🏠 十二宮納迪解讀 (Bhava Overview)")
    st.caption("納迪占星以 Jeeva（靈魂）與 Sarira（身體）概念解讀各宮主星與落入行星的互動。")

    bhavas_data = _get_nadi_bhavas_data().get("bhavas", {})
    for bhava_key, bhava in bhavas_data.items():
        with st.expander(f"🏛️ {bhava.get('title', bhava_key)}"):
            st.markdown(bhava.get("description", ""))
            if bhava.get("jeeva_sarira"):
                st.markdown(f"**Jeeva / Sarira**：{bhava['jeeva_sarira']}")
            rules = bhava.get("key_rules", [])
            if rules:
                st.markdown("**主要規則**：")
                for rule in rules:
                    st.markdown(f"- {rule}")
