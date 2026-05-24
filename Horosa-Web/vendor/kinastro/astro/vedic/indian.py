"""
印度占星排盤模組 (Indian/Vedic Astrology — Jyotish Chart Module)

使用 pyswisseph 以恆星黃道 (sidereal zodiac) 搭配 Lahiri 歲差
計算行星位置，包含 Nakshatra（二十七宿）與 Rashi（星座）資訊。
"""

import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

from astro import sukkayodo

# ============================================================
# 常量 (Constants)
# ============================================================

VEDIC_PLANETS = {
    "Surya (太陽)": swe.SUN,
    "Chandra (月亮)": swe.MOON,
    "Mangal (火星)": swe.MARS,
    "Budha (水星)": swe.MERCURY,
    "Guru (木星)": swe.JUPITER,
    "Shukra (金星)": swe.VENUS,
    "Shani (土星)": swe.SATURN,
}

# 七曜名稱索引對照 (lord index → name string)
# 0=Ketu, 1=Venus, 2=Sun, 3=Moon, 4=Mars, 5=Rahu, 6=Jupiter, 7=Saturn, 8=Mercury
GRAHA_NAMES_BY_INDEX = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury",
]

RASHIS = [
    ("Mesha", "♈", "白羊", "Mars", "火"),
    ("Vrishabha", "♉", "金牛", "Venus", "地"),
    ("Mithuna", "♊", "雙子", "Mercury", "風"),
    ("Karka", "♋", "巨蟹", "Moon", "水"),
    ("Simha", "♌", "獅子", "Sun", "火"),
    ("Kanya", "♍", "處女", "Mercury", "地"),
    ("Tula", "♎", "天秤", "Venus", "風"),
    ("Vrischika", "♏", "天蠍", "Mars", "水"),
    ("Dhanu", "♐", "射手", "Jupiter", "火"),
    ("Makara", "♑", "摩羯", "Saturn", "地"),
    ("Kumbha", "♒", "水瓶", "Saturn", "風"),
    ("Meena", "♓", "雙魚", "Jupiter", "水"),
]

# 二十七宿 (27 Nakshatras) — each spans 13°20'
# 每宿之主曜、符號、象徵、特性 (Lord, Symbol, Symbolism, Quality)
NAKSHATRA_PROPERTIES = [
    # (nak_name, lord, symbol, deity, quality, caste, nature)
    # lord: 0=Ketu, 1=Venus, 2=Sun, 3=Moon, 4=Mars, 5=Rahu, 6=Jupiter, 7=Saturn, 8=Mercury
    ("Ashwini",        0, "馬頭",   "Aswini Twins",  "Cheerful",    "Deva",  "Uttama"),
    ("Bharani",        1, "大陵",   "Yami (Death)",   "Passionate",  "Manushya","Kahara"),
    ("Krittika",       2, "昴宿",   "Agni",           "Fierce",      "Deva",  "Uttama"),
    ("Rohini",         3, "畢宿",   "Brahma/Prajna",  "Stable",      "Lunar", "Uttama"),
    ("Mrigashira",     4, "觜宿",   "Soma/Growth",    "Curious",     "Lunar", "Madhyama"),
    ("Ardra",          5, "參宿",   "Rudra (Storm)",  "Restless",    "Lunar", "Kahara"),
    ("Punarvasu",      6, "井宿",   "Aditi (Abode)",  "Renewing",    "Deva",  "Uttama"),
    ("Pushya",         7, "鬼宿",   "Brihaspati",     "Nurturing",   "Deva",  "Uttama"),
    ("Ashlesha",       8, "柳宿",   "Naga (Serpent)", "Seductive",   "Naga",  "Kahara"),
    ("Magha",          0, "星宿",   "Pitris (Ancestors)","Regal",   "Lunar", "Madhyama"),
    ("Purva Phalguni", 1, "張宿",   "Bhaga (Prosperity)","Loving",  "Lunar", "Madhyama"),
    ("Uttara Phalguni",2, "翼宿",   "Aryaman (Guardian)","Dutiful",  "Deva",  "Uttama"),
    ("Hasta",          3, "軫宿",   "Savitri (Creator)","Skillful",  "Lunar", "Madhyama"),
    ("Chitra",         4, "角宿",   "Tvashtar (Architect)","Radiant","Naga", "Uttama"),
    ("Swati",          5, "亢宿",   "Vayu (Wind)",    "Independent", "Naga",  "Madhyama"),
    ("Vishakha",       6, "氐宿",   "Indra/Agni",     "Multi-faceted","Lunar","Kahara"),
    ("Anuradha",       7, "房宿",   "Mitra (Friendship)","Balanced","Deva", "Uttama"),
    ("Jyeshtha",       8, "心宿",   "Indra (Chief)",  "Protective",  "Naga",  "Kahara"),
    ("Mula",           0, "尾宿",   "Nirriti (Destruction)","Deep","Naga",  "Kahara"),
    ("Purva Ashadha",  1, "箕宿",   "Apah (Water)",   "Victorious",  "Deva",  "Madhyama"),
    ("Uttara Ashadha", 2, "斗宿",   "Vishwa Devas",   "Truthful",    "Deva",  "Uttama"),
    ("Shravana",       3, "牛宿",   "Vishnu (Preserver)","Devoted",  "Lunar", "Uttama"),
    ("Dhanishta",      4, "女宿",   "Vasudev (Abundance)","Wealthy",  "Naga", "Madhyama"),
    ("Shatabhisha",    5, "虛宿",   "Varuna (Cosmic Waters)","Mysterious","Naga","Kahara"),
    ("Purva Bhadrapada",6,"危宿",  "Aja Ekapada",     "Heroic",      "Naga",  "Madhyama"),
    ("Uttara Bhadrapada",7,"室宿", "Ahir Budhya",    "Serene",      "Naga",  "Uttama"),
    ("Revati",         8, "壁宿",   "Pushan (Guardian)","Nurturing", "Lunar", "Uttama"),
]

NAKSHATRAS = [
    (prop[0], prop[2], prop[1])  # (name, chinese, lord_index)
    for prop in NAKSHATRA_PROPERTIES
]

# 七曜主宿對應表 (Graha → Nakshatras they rule)
GRAHA_NAKSHATRA_MAP = {
    "Ketu":     ["Ashwini", "Magha", "Mula"],
    "Venus":    ["Bharani", "Purva Phalguni", "Purva Ashadha"],
    "Sun":      ["Krittika", "Uttara Phalguni", "Uttara Ashadha"],
    "Moon":     ["Rohini", "Hasta", "Shravana"],
    "Mars":     ["Mrigashira", "Chitra", "Dhanishta"],
    "Rahu":     ["Ardra", "Swati", "Shatabhisha"],
    "Jupiter":  ["Punarvasu", "Vishakha", "Purva Bhadrapada"],
    "Saturn":   ["Pushya", "Anuradha", "Uttara Bhadrapada"],
    "Mercury":  ["Ashlesha", "Jyeshtha", "Revati"],
}

# 七曜與宿的吉凶屬性 (Graha's natural relationship with nakshatras)
GRAHA_NAKSHATRA_NATURE = {
    # 曜名: (吉宿數, 中宿數, 凶宿數)
    "Ketu":     (3, 0, 0),   # 3 個主宿皆為中凶
    "Venus":    (2, 1, 0),   # Venus 主 3 吉/中
    "Sun":      (1, 2, 0),   # Sun 主 1 吉 2 中
    "Moon":     (2, 1, 0),   # Moon 主 3 吉/中
    "Mars":     (1, 2, 0),   # Mars 主 1 吉 2 中
    "Rahu":     (0, 1, 2),   # Rahu 主 1 中 2 凶
    "Jupiter":  (3, 0, 0),   # Jupiter 3 個主宿皆吉
    "Saturn":   (1, 2, 0),   # Saturn 主 1 吉 2 中
    "Mercury":  (1, 2, 0),   # Mercury 主 1 吉 2 中
}

# 曜主與宿的守護關係說明 (Graha lord ↔ Nakshatra lord)
GRAHA_DESCRIPTION = {
    "Ketu":     "印度占星中的南交點，象徵解脫、業力。主管 Ashwini、Magha、Mula 三宿，帶有神秘與再生之力。",
    "Venus":    "愛與美之星，主管 Bharani、Purva Phalguni、Purva Ashadha。代表感情、藝術、繁榮，與親密關係密切。",
    "Sun":      "生命力與自我之星，主管 Krittika、Uttara Phalguni、Uttara Ashadha。象徵權威、領導力與靈魂之光。",
    "Moon":     "心意與情感之星，主管 Rohini、Hasta、Shravana。代表情緒、直覺、想象力，與内心世界最强聯結。",
    "Mars":     "能量與行動之星，主管 Mrigashira、Chitra、Dhanishta。象徵勇氣、戰鬥力與决断力。",
    "Rahu":     "印度占星中的北交點，主管 Ardra、Swati、Shatabhisha。代表野心、幻象與世俗成就。",
    "Jupiter":  "智慧與幸運之星，主管 Punarvasu、Vishakha、Purva Bhadrapada。象徵知識、豐盛與靈性成長。",
    "Saturn":   "業力與考驗之星，主管 Pushya、Anuradha、Uttara Bhadrapada。代表紀律、責任與生命的深度考驗。",
    "Mercury":  "溝通與智力之星，主管 Ashlesha、Jyeshtha、Revati。象徵心智、學習、商業技能與邏輯思維。",
}

PLANET_COLORS = {
    "Surya (太陽)": "#FF8C00",
    "Chandra (月亮)": "#C0C0C0",
    "Mangal (火星)": "#DC143C",
    "Budha (水星)": "#4169E1",
    "Guru (木星)": "#FFD700",
    "Shukra (金星)": "#FF69B4",
    "Shani (土星)": "#8B4513",
    "Rahu (羅睺)": "#800080",
    "Ketu (計都)": "#4B0082",
}


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class VedicPlanet:
    """Vedic planet position"""
    name: str
    longitude: float
    latitude: float
    rashi: str
    rashi_glyph: str
    rashi_chinese: str
    rashi_lord: str
    sign_degree: float
    nakshatra: str
    nakshatra_chinese: str
    nakshatra_lord: str
    nakshatra_pada: int
    retrograde: bool
    house: int = 0
    # 宿曜道 (Japanese 28 Mansions)
    sukkayodo_mansion: str = ""            # 宿曜道宿名
    sukkayodo_mansion_chinese: str = ""    # 中國星名
    sukkayodo_mansion_index: int = -1      # 宿曜道 28 宿索引 (0-27)
    sukkayodo_pada: int = 0                # 宿曜道四足


@dataclass
class VedicHouse:
    """Vedic bhava (house)"""
    number: int
    cusp: float
    rashi: str
    rashi_glyph: str
    planets: list = field(default_factory=list)


@dataclass
class VedicChart:
    """Indian / Vedic astrology chart"""
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
    houses: list
    ascendant: float
    asc_rashi: str


# ============================================================
# 計算函數 (Calculation Functions)
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


def _find_house(lon, cusps):
    lon = _normalize(lon)
    for i in range(12):
        start = _normalize(cusps[i])
        end = _normalize(cusps[(i + 1) % 12])
        if start < end:
            if start <= lon < end:
                return i + 1
        else:
            if lon >= start or lon < end:
                return i + 1
    return 1


@st.cache_data(ttl=3600, show_spinner=False)
def compute_vedic_chart(year, month, day, hour, minute, timezone,
                        latitude, longitude, location_name=""):
    """計算印度占星排盤 (Sidereal / Lahiri Ayanamsa)"""
    swe.set_ephe_path("")
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Compute sidereal house cusps
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"P",
                                 swe.FLG_SIDEREAL)
    ascendant = _normalize(ascmc[0])

    planets = []
    for name, pid in VEDIC_PLANETS.items():
        result, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        rashi = RASHIS[idx]
        nak_idx, pada = _nakshatra_info(lon)
        nak = NAKSHATRAS[nak_idx]
        sukk_idx, sukk_pada = sukkayodo.sukkayodo_info(lon)
        sukk = sukkayodo.SUKKAYODO_MANSION[sukk_idx]

        planets.append(VedicPlanet(
            name=name, longitude=lon, latitude=lat,
            rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
            rashi_lord=rashi[3], sign_degree=_sign_degree(lon),
            nakshatra=nak[0], nakshatra_chinese=nak[1],
            nakshatra_lord=nak[2], nakshatra_pada=pada,
            retrograde=speed < 0,
            sukkayodo_mansion=sukk[0], sukkayodo_mansion_chinese=sukk[2],
            sukkayodo_mansion_index=sukk_idx, sukkayodo_pada=sukk_pada,
        ))

    # Rahu (Mean North Node)
    rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _normalize(rahu_res[0])
    idx = _sign_index(rahu_lon)
    rashi = RASHIS[idx]
    nak_idx, pada = _nakshatra_info(rahu_lon)
    nak = NAKSHATRAS[nak_idx]
    sukk_idx, sukk_pada = sukkayodo.sukkayodo_info(rahu_lon)
    sukk = sukkayodo.SUKKAYODO_MANSION[sukk_idx]
    planets.append(VedicPlanet(
        name="Rahu (羅睺)", longitude=rahu_lon, latitude=rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], sign_degree=_sign_degree(rahu_lon),
        nakshatra=nak[0], nakshatra_chinese=nak[1],
        nakshatra_lord=nak[2], nakshatra_pada=pada,
        retrograde=False,
        sukkayodo_mansion=sukk[0], sukkayodo_mansion_chinese=sukk[2],
        sukkayodo_mansion_index=sukk_idx, sukkayodo_pada=sukk_pada,
    ))

    # Ketu (South Node = Rahu + 180°)
    ketu_lon = _normalize(rahu_lon + 180.0)
    idx = _sign_index(ketu_lon)
    rashi = RASHIS[idx]
    nak_idx, pada = _nakshatra_info(ketu_lon)
    nak = NAKSHATRAS[nak_idx]
    sukk_idx, sukk_pada = sukkayodo.sukkayodo_info(ketu_lon)
    sukk = sukkayodo.SUKKAYODO_MANSION[sukk_idx]
    planets.append(VedicPlanet(
        name="Ketu (計都)", longitude=ketu_lon, latitude=-rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], sign_degree=_sign_degree(ketu_lon),
        nakshatra=nak[0], nakshatra_chinese=nak[1],
        nakshatra_lord=nak[2], nakshatra_pada=pada,
        retrograde=False,
        sukkayodo_mansion=sukk[0], sukkayodo_mansion_chinese=sukk[2],
        sukkayodo_mansion_index=sukk_idx, sukkayodo_pada=sukk_pada,
    ))

    # Build houses
    houses = []
    for i in range(12):
        cusp = cusps[i]
        idx = _sign_index(cusp)
        rashi = RASHIS[idx]
        houses.append(VedicHouse(
            number=i + 1, cusp=cusp,
            rashi=rashi[0], rashi_glyph=rashi[1],
            planets=[],
        ))

    for p in planets:
        h = _find_house(p.longitude, cusps)
        p.house = h
        houses[h - 1].planets.append(p.name)

    asc_rashi = RASHIS[_sign_index(ascendant)][0]

    return VedicChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd, ayanamsa=ayanamsa,
        planets=planets, houses=houses,
        ascendant=ascendant, asc_rashi=asc_rashi,
    )


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_vedic_chart(chart, after_chart_hook=None):
    """渲染完整的印度占星排盤"""
    col1, col2 = st.columns(2)
    with col1:
        _render_south_indian_grid(chart)
    with col2:
        _render_north_indian_grid(chart)
    if after_chart_hook:
        after_chart_hook()
    st.divider()
    _render_info(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_house_table(chart)
    st.divider()
    _render_nakshatra_graha_relation(chart)


def _render_info(chart):
    st.subheader("📋 排盤資訊 (Chart Information)")
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


def _render_south_indian_grid(chart):
    """渲染南印度式方盤 (South Indian Chart) — SVG 等分格"""
    st.subheader("📊 南印度排盤 (South Indian Chart)")

    from html import escape as _esc

    # Fixed rashi positions in 4×4 grid: (col, row, rashi_index)
    si_cells = [
        (0, 0, 3), (1, 0, 2), (2, 0, 1), (3, 0, 0),
        (0, 1, 4),                         (3, 1, 11),
        (0, 2, 5),                         (3, 2, 10),
        (0, 3, 6), (1, 3, 7), (2, 3, 8), (3, 3, 9),
    ]

    rashi_planets = {i: [] for i in range(12)}
    for p in chart.planets:
        idx = _sign_index(p.longitude)
        short = p.name.split(" ")[0]
        rashi_planets[idx].append((short, p.name))

    asc_idx = _sign_index(chart.ascendant)
    S = 400
    cell = S // 4  # 100 — each cell is exactly the same size

    svg = [
        f'<svg viewBox="0 0 {S} {S}" xmlns="http://www.w3.org/2000/svg"'
        f' style="width:100%;max-width:{S}px;height:auto;'
        f'font-family:sans-serif;">'
    ]

    # Background
    svg.append(
        f'<rect width="{S}" height="{S}" fill="#1a1a2e" rx="4"/>'
    )

    # Grid lines (equal spacing)
    for i in range(5):
        svg.append(
            f'<line x1="{i * cell}" y1="0" x2="{i * cell}" y2="{S}"'
            f' stroke="#555" stroke-width="1"/>'
        )
        svg.append(
            f'<line x1="0" y1="{i * cell}" x2="{S}" y2="{i * cell}"'
            f' stroke="#555" stroke-width="1"/>'
        )

    # Center 2×2 info area
    svg.append(
        f'<rect x="{cell}" y="{cell}" width="{cell * 2}"'
        f' height="{cell * 2}" fill="#2a2a4a" stroke="#555"'
        f' stroke-width="1"/>'
    )

    # Rashi cells
    for col, row, ri in si_cells:
        x, y = col * cell, row * cell
        is_asc = (ri == asc_idx)
        if is_asc:
            svg.append(
                f'<rect x="{x + 1}" y="{y + 1}" width="{cell - 2}"'
                f' height="{cell - 2}" fill="#3d3010"/>'
            )
        rashi = RASHIS[ri]
        cx = x + cell // 2
        marker = " ▲" if is_asc else ""
        svg.append(
            f'<text x="{cx}" y="{y + 20}" text-anchor="middle"'
            f' font-size="11" font-weight="bold"'
            f' fill="#e0e0e0">{_esc(rashi[0])}{marker}</text>'
        )
        svg.append(
            f'<text x="{cx}" y="{y + 35}" text-anchor="middle"'
            f' font-size="10" fill="#888">{rashi[1]} {rashi[2]}</text>'
        )
        p_list = rashi_planets[ri]
        if p_list:
            for pi, (short, full) in enumerate(p_list):
                color = PLANET_COLORS.get(full, "#c8c8c8")
                py = y + 52 + pi * 14
                if py < y + cell - 5:
                    svg.append(
                        f'<text x="{cx}" y="{py}" text-anchor="middle"'
                        f' font-size="11" font-weight="bold"'
                        f' fill="{color}">{_esc(short)}</text>'
                    )
        else:
            svg.append(
                f'<text x="{cx}" y="{y + 55}" text-anchor="middle"'
                f' font-size="11" fill="#666">—</text>'
            )

    # Center info text
    info_cx = S // 2
    info_lines = [
        ("Jyotish 印度占星", 13, "bold", "#e0e0e0"),
        (f"{chart.year}/{chart.month}/{chart.day}", 11, "normal", "#bbb"),
        (f"{chart.hour:02d}:{chart.minute:02d} UTC{chart.timezone:+.1f}",
         11, "normal", "#bbb"),
        (chart.location_name, 10, "normal", "#999"),
        (f"Ayanamsa: {chart.ayanamsa:.2f}°", 10, "normal", "#999"),
    ]
    for i, (text, size, weight, color) in enumerate(info_lines):
        svg.append(
            f'<text x="{info_cx}" y="{cell + 35 + i * 25}"'
            f' text-anchor="middle" font-size="{size}"'
            f' font-weight="{weight}" fill="{color}">'
            f'{_esc(text)}</text>'
        )

    svg.append('</svg>')

    st.markdown(
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;'
        'max-width:100%;">' + '\n'.join(svg) + '</div>',
        unsafe_allow_html=True,
    )


def _render_north_indian_grid(chart):
    """渲染北印度式菱形盤 (North Indian Diamond Chart) — SVG

    Uses the traditional Kundli diamond layout: a square with two
    corner-to-corner diagonals and a diamond (midpoint connections),
    producing 12 regions (4 kite-shaped + 8 triangular).
    House 1 (Lagna) is always at the top; houses run counter-clockwise.
    """
    st.subheader("📊 北印度排盤 (North Indian Chart)")

    from html import escape as _esc

    rashi_planets = {i: [] for i in range(12)}
    for p in chart.planets:
        idx = _sign_index(p.longitude)
        short = p.name.split(" ")[0]
        rashi_planets[idx].append((short, p.name))

    asc_idx = _sign_index(chart.ascendant)

    S = 400
    M = S // 2   # 200 — midpoint
    Q = S // 4   # 100 — quarter

    # Key geometry --------------------------------------------------
    # Square corners
    TL, TR, BR, BL = (0, 0), (S, 0), (S, S), (0, S)
    # Midpoints of sides (diamond vertices)
    T, R, B, L = (M, 0), (S, M), (M, S), (0, M)
    # Diagonal–diamond intersection points
    P1, P2 = (Q, Q), (S - Q, Q)
    P3, P4 = (S - Q, S - Q), (Q, S - Q)

    # 12 house definitions -----------------------------------------
    # (house_offset, polygon_vertices, (text_cx, text_cy), is_kite)
    # Houses run counter-clockwise from top (H1 = Lagna).
    _houses = [
        (0,  [T, P2, (M, M), P1],  (M, M // 2),              True),
        (1,  [TL, T, P1],          (Q - 5, Q // 3 + 4),      False),
        (2,  [TL, P1, L],          (Q // 3 + 4, Q - 5),      False),
        (3,  [P1, (M, M), P4, L],  (M // 2, M),              True),
        (4,  [L, BL, P4],          (Q // 3 + 4, S - Q + 5),  False),
        (5,  [BL, B, P4],          (Q - 5, S - Q // 3 - 4),  False),
        (6,  [(M, M), P4, B, P3],  (M, S - M // 2),          True),
        (7,  [B, BR, P3],          (S - Q + 5, S - Q // 3 - 4), False),
        (8,  [BR, R, P3],          (S - Q // 3 - 4, S - Q + 5), False),
        (9,  [(M, M), P3, R, P2],  (S - M // 2, M),          True),
        (10, [R, TR, P2],          (S - Q // 3 - 4, Q - 5),  False),
        (11, [TR, T, P2],          (S - Q + 5, Q // 3 + 4),  False),
    ]

    svg = [
        f'<svg viewBox="0 0 {S} {S}" xmlns="http://www.w3.org/2000/svg"'
        f' style="width:100%;max-width:{S}px;height:auto;'
        f'font-family:sans-serif;">'
    ]
    svg.append(
        f'<rect width="{S}" height="{S}" fill="#1a1a2e" rx="4"/>'
    )

    # Draw each house region
    for house_num, poly, (cx, cy), is_large in _houses:
        ri = (asc_idx + house_num) % 12
        rashi = RASHIS[ri]
        is_lagna = (house_num == 0)
        fill = "#3d3010" if is_lagna else "#1e1e3a"

        pts = " ".join(f"{px},{py}" for px, py in poly)
        svg.append(
            f'<polygon points="{pts}" fill="{fill}"'
            f' stroke="#555" stroke-width="1.5"/>'
        )

        # Font sizes adapt to region size (kite vs triangle)
        fs = 11 if is_large else 9
        fs2 = 10 if is_large else 8
        lh = 14 if is_large else 12

        marker = " ▲" if is_lagna else ""
        svg.append(
            f'<text x="{cx}" y="{cy - 4}" text-anchor="middle"'
            f' font-size="{fs}" font-weight="bold"'
            f' fill="#e0e0e0">{_esc(rashi[0])}{marker}</text>'
        )
        svg.append(
            f'<text x="{cx}" y="{cy + 9}" text-anchor="middle"'
            f' font-size="{fs2}" fill="#888">'
            f'{rashi[1]} {rashi[2]}</text>'
        )

        # Planets
        p_list = rashi_planets[ri]
        if p_list:
            tspans = " ".join(
                f'<tspan fill="{PLANET_COLORS.get(full, "#c8c8c8")}">'
                f'{_esc(short)}</tspan>'
                for short, full in p_list
            )
            svg.append(
                f'<text x="{cx}" y="{cy + 9 + lh}"'
                f' text-anchor="middle" font-size="{fs}"'
                f' font-weight="bold">{tspans}</text>'
            )
        else:
            svg.append(
                f'<text x="{cx}" y="{cy + 9 + lh}"'
                f' text-anchor="middle" font-size="{fs}"'
                f' fill="#666">—</text>'
            )

    svg.append('</svg>')

    st.markdown(
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;'
        'max-width:100%;">' + '\n'.join(svg) + '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "▲ = Lagna (命宮/Ascendant)　　"
        "南印度：宮位固定・行星流動；"
        "北印度：宮位以 Lagna 為起點逆時針排列"
    )


def _render_planet_table(chart):
    st.subheader("🪐 行星位置 (Graha Positions)")
    header = ("| Graha | Rashi | Degree | Lord | "
              "Nakshatra | Pada | Nak Lord | R |")
    sep = ("|:-----:|:-----:|:------:|:----:|"
           ":--------:|:----:|:--------:|:-:|")
    rows = [header, sep]
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = (
            f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        )
        rows.append(
            f"| {name_html} | {p.rashi_glyph} {p.rashi} ({p.rashi_chinese}) "
            f"| {p.sign_degree:.2f}° | {p.rashi_lord} "
            f"| {p.nakshatra} ({p.nakshatra_chinese}) "
            f"| {p.nakshatra_pada} | {p.nakshatra_lord} | {retro} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_house_table(chart):
    st.subheader("🏛️ 宮位 (Bhava)")
    header = "| Bhava | Cusp | Rashi | Planets |"
    sep = "|:-----:|:----:|:-----:|:-------:|"
    rows = [header, sep]
    for h in chart.houses:
        planets_str = ", ".join(h.planets) if h.planets else "—"
        rows.append(
            f"| {h.number} | {_format_deg(h.cusp)} "
            f"| {h.rashi_glyph} {h.rashi} | {planets_str} |"
        )
    st.markdown("\n".join(rows))


def _render_nakshatra_graha_relation(chart):
    """渲染 27 宿與七曜關係表 (Nakshatra-Graha Relationship)"""
    st.subheader("🌟 二十七宿與七曜 (27 Nakshatras & 7 Grahas)")

    # 說明
    st.markdown(
        "**二十七宿 (Nakshatra)** 每宿由一顆**曜 (Graha)** 主管，"
        "稱為 **Nakshatra Lord**，共 9 曜（太陽至計都）管 27 宿。\n"
        "每宿分 **四足 (Pada/Quarter)**，各宿之首為該曜所主。"
    )

    # ---- 七曜概述 ----
    st.markdown("### 七曜概述 (Navagraha Overview)")
    overview_rows = [
        "| 曜 (Graha) | 主宿數 | 吉 | 中 | 凶 | 描述 Description |",
        "|:-----------|:------:|:--:|:--:|:--:|:-----------------|",
    ]
    for graha in GRAHA_DESCRIPTION:
        nature = GRAHA_NAKSHATRA_NATURE.get(graha, (0, 0, 0))
        overview_rows.append(
            f"| **{graha}** | 3 | {nature[0]} | {nature[1]} | {nature[2]} "
            f"| {GRAHA_DESCRIPTION[graha]} |"
        )
    st.markdown("\n".join(overview_rows))

    # ---- 七曜主管宿列表 ----
    st.markdown("### 七曜主宿對照 (Graha → Nakshatra)")
    rows = [
        "| 曜 (Graha) | 主宿 Nakshatras | 中文 |",
        "|:-----------|:---------------|:-----|",
    ]
    for graha, naks in GRAHA_NAKSHATRA_MAP.items():
        color = PLANET_COLORS.get(graha + " (" + graha + ")",
                                  PLANET_COLORS.get(f"{graha}", "#c8c8c8"))
        nak_texts = []
        for n in naks:
            # 找中文名
            for prop in NAKSHATRA_PROPERTIES:
                if prop[0] == n:
                    nak_texts.append(f"{n} ({prop[2]})")
                    break
        rows.append(
            f"| **{graha}** | {'、'.join(nak_texts)} | "
            f"{'、'.join([n for n in GRAHA_NAKSHATRA_MAP[graha]])} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)

    # ---- 完整 27 宿列表 ----
    st.markdown("### 二十七宿完整列表 (27 Nakshatras)")
    rows2 = [
        "| # | Nakshatra | 中國星名 | 主曜 Lord | 象徵 Symbol | 神祇 Deity | 特質 Quality |",
        "|:--:|:----------|:---------|:---------|:-----------|:-----------|:------------|",
    ]
    for i, prop in enumerate(NAKSHATRA_PROPERTIES):
        nak_name, chinese, lord_idx = prop[0], prop[2], prop[1]
        symbol, deity, quality = prop[3], prop[4], prop[5]
        lord_name = GRAHA_NAMES_BY_INDEX[lord_idx]
        color = PLANET_COLORS.get(lord_name, "#c8c8c8")
        rows2.append(
            f"| {i+1} | "
            f'<span style="color:{color};font-weight:bold">{nak_name}</span> | '
            f"{chinese} | {lord_name} | {symbol} | {deity} | {quality} |"
        )
    st.markdown("\n".join(rows2), unsafe_allow_html=True)

