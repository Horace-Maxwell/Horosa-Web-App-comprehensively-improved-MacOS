"""
西洋占星排盤模組 (Western Astrology Chart Module)

使用 pyswisseph 以回歸黃道 (tropical zodiac) 或恆星黃道 (sidereal zodiac) 計算行星位置，
包含天王星、海王星、冥王星等現代行星，並渲染西洋占星排盤。

本模組整合占星四書（Ptolemy Tetrabiblos、Firmicus Mathesis、
Lilly Christian Astrology）所包含的古典占星技法：
- 本質廟旺落陷（Essential Dignities & Debilities）
- 行星喜樂宮（Planetary Joy）
- 阿拉伯點（Arabic Parts / Lots）
- 恆星相位（Fixed Star Conjunctions）
- 命度主星（Chart Ruler）
- 日夜盤判定（Day/Night Sect）
- 恆星黃道選項（Sidereal Zodiac with Lahiri Ayanamsa）
"""

import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

# ============================================================
# 常量 (Constants)
# ============================================================

WESTERN_PLANETS = {
    "Sun ☉": swe.SUN,
    "Moon ☽": swe.MOON,
    "Mercury ☿": swe.MERCURY,
    "Venus ♀": swe.VENUS,
    "Mars ♂": swe.MARS,
    "Jupiter ♃": swe.JUPITER,
    "Saturn ♄": swe.SATURN,
    "Uranus ♅": swe.URANUS,
    "Neptune ♆": swe.NEPTUNE,
    "Pluto ♇": swe.PLUTO,
}

ZODIAC_SIGNS = [
    ("Aries", "♈", "白羊座", "Fire"),
    ("Taurus", "♉", "金牛座", "Earth"),
    ("Gemini", "♊", "雙子座", "Air"),
    ("Cancer", "♋", "巨蟹座", "Water"),
    ("Leo", "♌", "獅子座", "Fire"),
    ("Virgo", "♍", "處女座", "Earth"),
    ("Libra", "♎", "天秤座", "Air"),
    ("Scorpio", "♏", "天蠍座", "Water"),
    ("Sagittarius", "♐", "射手座", "Fire"),
    ("Capricorn", "♑", "摩羯座", "Earth"),
    ("Aquarius", "♒", "水瓶座", "Air"),
    ("Pisces", "♓", "雙魚座", "Water"),
]

ASPECT_TYPES = [
    {"name": "Conjunction (合)", "symbol": "☌", "angle": 0, "orb": 8},
    {"name": "Opposition (沖)", "symbol": "☍", "angle": 180, "orb": 8},
    {"name": "Trine (三合)", "symbol": "△", "angle": 120, "orb": 6},
    {"name": "Square (刑)", "symbol": "□", "angle": 90, "orb": 6},
    {"name": "Sextile (六合)", "symbol": "⚹", "angle": 60, "orb": 4},
]

PLANET_COLORS = {
    "Sun ☉": "#FF8C00",
    "Moon ☽": "#C0C0C0",
    "Mercury ☿": "#4169E1",
    "Venus ♀": "#FF69B4",
    "Mars ♂": "#DC143C",
    "Jupiter ♃": "#228B22",
    "Saturn ♄": "#8B4513",
    "Uranus ♅": "#00CED1",
    "Neptune ♆": "#7B68EE",
    "Pluto ♇": "#800080",
}

# ============================================================
# 古典占星常數（占星四書技法）
# ============================================================

# Essential Dignities — sign_index (0=Aries..11=Pisces)
# Each sign has domicile ruler, exaltation, fall, and detriment
# Detriment = opposite sign of domicile ((idx + 6) % 12)
# Fall = opposite sign of exaltation ((idx + 6) % 12)
CLASSICAL_DIGNITIES = {
    0:  {"domicile": "Mars ♂",    "exaltation": "Sun ☉"},
    1:  {"domicile": "Venus ♀",   "exaltation": "Moon ☽"},
    2:  {"domicile": "Mercury ☿", "exaltation": None},
    3:  {"domicile": "Moon ☽",    "exaltation": "Jupiter ♃"},
    4:  {"domicile": "Sun ☉",     "exaltation": "Pluto ♇"},
    5:  {"domicile": "Mercury ☿", "exaltation": "Mercury ☿"},
    6:  {"domicile": "Venus ♀",   "exaltation": "Saturn ♄"},
    7:  {"domicile": "Mars ♂",    "exaltation": "Uranus ♅"},
    8:  {"domicile": "Jupiter ♃", "exaltation": "Neptune ♆"},
    9:  {"domicile": "Saturn ♄",  "exaltation": "Mars ♂"},
    10: {"domicile": "Saturn ♄",  "exaltation": None},
    11: {"domicile": "Jupiter ♃", "exaltation": "Venus ♀"},
}

# Planetary Joy — each planet rejoices in a particular house (Lilly tradition)
# Sun joy 9th, Moon joy 4th, Mercury joy 1st, Venus joy 5th,
# Mars joy 6th, Jupiter joy 11th, Saturn joy 12th
PLANETAL_JOY = {
    "Sun ☉": 9,
    "Moon ☽": 4,
    "Mercury ☿": 1,
    "Venus ♀": 5,
    "Mars ♂": 6,
    "Jupiter ♃": 11,
    "Saturn ♄": 12,
}

# Dignity scores for weighting (Lilly/Ptolemy system)
DIGNITY_SCORES = {
    "domicile": 5,
    "exaltation": 4,
    "triplicity_day": 3,
    "triplicity_night": 3,
    "term": 2,
    "face": 1,
    "detriment": -5,
    "fall": -4,
}

# Fixed Stars — name, SwissEph star key, Chinese name, magnitude, classical meaning
# Orb is the conjunction orb in degrees; swe.fixstar2() used for positions
FIXED_STARS = [
    ("Aldebaran",   "Aldebaran",    "畢宿五",   0.85, "勇氣、好戰、軍事事務"),
    ("Regulus",     "Regulus",      "軒轅十四", 1.35, "王權、領袖、吉祥"),
    ("Antares",     "Antares",      "心宿二",   0.96, "膽識、軍事榮譽、火災危險"),
    ("Spica",       "Spica",        "角宿一",   0.97, "財富、創造天賦、學術之愛"),
    ("Pollux",      "Pollux",       "北河三",   1.14, "勇氣、保護、旅行者"),
    ("Procyon",     "Procyon",      "南河三",   0.34, "名聲、活力、變革"),
    ("Sirius",      "Sirius",       "天狼星",   -1.46, "榮耀、財富、高貴"),
    ("Castor",      "Castor",       "北河二",   1.93, "才智、技藝、旅行"),
    ("Vega",        "Vega",         "織女星",   0.03, "藝術、純潔、幸運"),
    ("Fomalhaut",   "Fomalhaut",    "北落師門", 1.16, "獨立、理想、變革"),
    ("Deneb",       "Deneb",        "天津四",   1.25, "飛行、創造力、皇室"),
    ("Altair",      "Altair",       "牛郎星",   0.76, "行動力、勇氣、軍事"),
    ("Betelgeuse",  "Betelgeuse",   "參宿四",   0.50, "野心、創造力、巨變"),
    ("Rigel",       "Rigel",        "參宿七",   0.13, "名聲、財富、技藝"),
    ("Capella",     "Capella",      "五車五",   0.08, "成功、財富、道德"),
    ("Proxima",     "Proxima Cen",  "比鄰星",   11.05, "親密關係、隱藏力量"),
    ("Alcyone",     "Alcyone",      "昴宿六",   2.87, "豐盛、領導力、神秘"),
    ("Algol",       "Algol",        "大陵五",   2.12, "危險、暴力、死亡"),
    ("Alphard",     "Alphard",      "星宿一",   2.00, "孤獨、秘密、旅行"),
    ("Bellatrix",   "Bellatrix",    "參宿三",   1.64, "勇敢、戰士、演說家"),
]

# Fixed star orbs (degrees) — custom per star brightness
FIXED_STAR_ORBS = {
    "Aldebaran": 1.0, "Regulus": 1.0, "Antares": 1.0, "Spica": 1.0,
    "Pollux": 1.0, "Procyon": 1.0, "Sirius": 1.0, "Castor": 1.0,
    "Vega": 1.0, "Fomalhaut": 1.0, "Deneb": 1.0, "Altair": 1.0,
    "Betelgeuse": 1.0, "Rigel": 1.0, "Capella": 1.0, "Alcyone": 1.0,
    "Algol": 0.5, "Alphard": 1.0, "Bellatrix": 1.0,
}

# Arabic Parts for Western module — (english, chinese, day_formula, night_formula)
# Formula: Part = ASC + A - B (normalize 0-360)
WESTERN_ARABIC_PARTS = [
    ("Lot of Fortune",  "幸運點",  ("Moon ☽", "Sun ☉"), ("Sun ☉", "Moon ☽")),
    ("Lot of Spirit",   "精神點",  ("Sun ☉",  "Moon ☽"), ("Moon ☽", "Sun ☉")),
    ("Lot of Marriage", "婚姻點",  ("Venus ♀", "Saturn ♄"), ("Saturn ♄", "Venus ♀")),
    ("Lot of Children", "子女點",  ("Jupiter ♃", "Moon ☽"), ("Moon ☽", "Jupiter ♃")),
    ("Lot of Mother",   "母親點",  ("Moon ☽", "Saturn ♄"), ("Saturn ♄", "Moon ☽")),
    ("Lot of Father",   "父親點",  ("Sun ☉",  "Saturn ♄"), ("Saturn ♄", "Sun ☉")),
]

# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class WesternPlanet:
    """西洋占星行星位置"""
    name: str
    longitude: float
    latitude: float
    sign: str
    sign_glyph: str
    sign_chinese: str
    sign_degree: float
    element: str
    retrograde: bool
    house: int = 0
    essential_dignity: str = "—"
    joy_status: str = "—"
    fixed_star_conjunctions: list = field(default_factory=list)


@dataclass
class WesternHouse:
    """西洋占星宮位"""
    number: int
    cusp: float
    sign: str
    sign_glyph: str
    planets: list = field(default_factory=list)


@dataclass
class ArabicPart:
    """阿拉伯點"""
    english_name: str
    chinese_name: str
    longitude: float
    sign: str
    sign_glyph: str
    sign_chinese: str
    sign_degree: float
    house: int = 0


@dataclass
class FixedStarConjunction:
    """恆星相位"""
    star_name: str
    star_name_cn: str
    star_longitude: float
    planet_name: str
    orb: float
    meaning: str


@dataclass
class WesternChart:
    """西洋占星排盤"""
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
    planets: list
    houses: list
    ascendant: float
    midheaven: float
    asc_sign: str
    mc_sign: str
    is_day_chart: bool = False
    chart_ruler: str = "—"
    chart_ruler_dignity: str = "—"
    lot_of_fortune: float = 0.0
    arabic_parts: list = field(default_factory=list)
    fixed_star_conjunctions: list = field(default_factory=list)
    sidereal_mode: bool = False
    ayanamsa: float = 0.0


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _normalize(deg):
    return deg % 360.0


def _sign_index(deg):
    return int(_normalize(deg) / 30.0)


def _sign_degree(deg):
    return _normalize(deg) % 30.0


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


def _get_essential_dignity(planet_name, sign_idx):
    """計算本質廟旺落陷"""
    short = planet_name.split(" ")[0]
    dig = CLASSICAL_DIGNITIES[sign_idx]
    # Domicile
    if dig["domicile"] and short == dig["domicile"].split(" ")[0]:
        return "入廟 (Domicile)"
    # Exaltation
    if dig["exaltation"] and short == dig["exaltation"].split(" ")[0]:
        return "入旺 (Exaltation)"
    # Detriment: opposite of domicile
    opp = (sign_idx + 6) % 12
    if CLASSICAL_DIGNITIES[opp]["domicile"] and short == CLASSICAL_DIGNITIES[opp]["domicile"].split(" ")[0]:
        return "落陷 (Detriment)"
    # Fall: opposite of exaltation
    if dig["exaltation"]:
        opp_ex = (sign_idx + 6) % 12
        if CLASSICAL_DIGNITIES[opp_ex]["exaltation"] and short == CLASSICAL_DIGNITIES[opp_ex]["exaltation"].split(" ")[0]:
            return "入弱 (Fall)"
    return "—"


def _get_joy_status(planet_name, house):
    """計算行星喜樂宮狀態"""
    short = planet_name.split(" ")[0]
    for pname, joy_house in PLANETAL_JOY.items():
        if pname.split(" ")[0] == short and joy_house == house:
            return "喜樂 (Joy)"
    return "—"


def _is_day_chart(sun_lon, cusps):
    """判斷日夜盤：Sun 在 7-12 宮 = 日盤"""
    sun_house = _find_house(sun_lon, cusps)
    return sun_house >= 7


def _get_chart_ruler(asc_idx, planets):
    """找命度主星及其 dignity"""
    ruler_name = CLASSICAL_DIGNITIES[asc_idx]["domicile"]
    if ruler_name:
        short = ruler_name.split(" ")[0]
        for p in planets:
            if p.name.split(" ")[0] == short:
                dignity = _get_essential_dignity(p.name, _sign_index(p.longitude))
                return p.name, dignity
    return "—", "—"


def _compute_arabic_part(ascendant, planet_lons, key_a, key_b, is_day):
    """計算單個阿拉伯點"""
    lon_a = planet_lons.get(key_a, 0.0)
    lon_b = planet_lons.get(key_b, 0.0)
    if is_day:
        lon = _normalize(ascendant + lon_a - lon_b)
    else:
        lon = _normalize(ascendant + lon_b - lon_a)
    return lon


def _compute_arabic_parts(ascendant, sun_lon, moon_lon, saturn_lon, jupiter_lon,
                          venus_lon, mercury_lon, is_day, cusps):
    """計算所有阿拉伯點"""
    planet_lons = {
        "Sun ☉": sun_lon,
        "Moon ☽": moon_lon,
        "Saturn ♄": saturn_lon,
        "Jupiter ♃": jupiter_lon,
        "Venus ♀": venus_lon,
        "Mercury ☿": mercury_lon,
    }
    parts = []
    for english, chinese, day_f, night_f in WESTERN_ARABIC_PARTS:
        key_a, key_b = day_f if is_day else night_f
        lon = _compute_arabic_part(ascendant, planet_lons, key_a, key_b, is_day)
        idx = _sign_index(lon)
        sign_info = ZODIAC_SIGNS[idx]
        house = _find_house(lon, cusps)
        parts.append(ArabicPart(
            english_name=english,
            chinese_name=chinese,
            longitude=lon,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            sign_chinese=sign_info[2],
            sign_degree=_sign_degree(lon),
            house=house,
        ))
    return parts


def _compute_fixed_star_conjunctions(planets, jd):
    """計算恆星相位（合相）

    優化：先一次性計算所有恆星位置，再與行星比對，
    避免對每顆行星重複呼叫 swe.fixstar2（從 O(planets×stars) 降為 O(stars) 次 swe 呼叫）。
    """
    results = []
    swe.set_ephe_path("")

    # Pre-compute all fixed star positions once
    star_positions = []
    for star_key, star_name, star_cn, _, meaning in FIXED_STARS:
        try:
            star_res, _ = swe.fixstar2(star_name, jd, swe.FLG_SWIEPH)
            star_lon = _normalize(star_res[0])
            orb = FIXED_STAR_ORBS.get(star_key, 1.0)
            star_positions.append((star_name, star_cn, star_lon, orb, meaning))
        except Exception:
            continue

    # Compare each planet against pre-computed star positions
    for p in planets:
        p_lon = _normalize(p.longitude)
        for star_name, star_cn, star_lon, orb, meaning in star_positions:
            diff = abs(p_lon - star_lon)
            if diff > 180:
                diff = 360 - diff
            if diff <= orb:
                results.append(FixedStarConjunction(
                    star_name=star_name,
                    star_name_cn=star_cn,
                    star_longitude=star_lon,
                    planet_name=p.name,
                    orb=round(diff, 2),
                    meaning=meaning,
                ))
    return results


# ============================================================
# 計算函數 (Calculation Functions)
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_western_chart(year, month, day, hour, minute, timezone,
                          latitude, longitude, location_name="",
                          sidereal=False):
    """計算西洋占星排盤

    Args:
        sidereal: 若為 True，使用恆星黃道（Lahiri Ayanamsa）
    """
    swe.set_ephe_path("")

    # Sidereal mode
    sidereal_flag = 0
    if sidereal:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        sidereal_flag = swe.FLG_SIDEREAL

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    if sidereal:
        cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"P", sidereal_flag)
        ayanamsa = swe.get_ayanamsa_ut(jd)
    else:
        cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")
        ayanamsa = 0.0
    ascendant = _normalize(ascmc[0])
    midheaven = _normalize(ascmc[1])

    planet_lons = {}
    planets = []
    for name, planet_id in WESTERN_PLANETS.items():
        if sidereal:
            result, _ = swe.calc_ut(jd, planet_id, sidereal_flag)
        else:
            result, _ = swe.calc_ut(jd, planet_id)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        sign_info = ZODIAC_SIGNS[idx]

        planet_lons[name] = lon
        pos = WesternPlanet(
            name=name,
            longitude=lon,
            latitude=lat,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            sign_chinese=sign_info[2],
            sign_degree=_sign_degree(lon),
            element=sign_info[3],
            retrograde=speed < 0,
            essential_dignity=_get_essential_dignity(name, idx),
        )
        planets.append(pos)

    # North Node (Rahu)
    if sidereal:
        rahu, _ = swe.calc_ut(jd, swe.MEAN_NODE, sidereal_flag)
    else:
        rahu, _ = swe.calc_ut(jd, swe.MEAN_NODE)
    rahu_lon = _normalize(rahu[0])
    idx = _sign_index(rahu_lon)
    sign_info = ZODIAC_SIGNS[idx]
    planet_lons["North Node ☊"] = rahu_lon
    planets.append(WesternPlanet(
        name="North Node ☊",
        longitude=rahu_lon,
        latitude=rahu[1],
        sign=sign_info[0],
        sign_glyph=sign_info[1],
        sign_chinese=sign_info[2],
        sign_degree=_sign_degree(rahu_lon),
        element=sign_info[3],
        retrograde=False,
    ))

    houses = []
    for i in range(12):
        cusp = cusps[i]
        idx = _sign_index(cusp)
        sign_info = ZODIAC_SIGNS[idx]
        houses.append(WesternHouse(
            number=i + 1,
            cusp=cusp,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            planets=[],
        ))

    for p in planets:
        h = _find_house(p.longitude, cusps)
        p.house = h
        p.joy_status = _get_joy_status(p.name, h)
        houses[h - 1].planets.append(p.name)

    asc_idx = _sign_index(ascendant)
    mc_idx = _sign_index(midheaven)

    sun_lon = planet_lons.get("Sun ☉", 0.0)
    moon_lon = planet_lons.get("Moon ☽", 0.0)
    is_day = _is_day_chart(sun_lon, cusps)
    chart_ruler, chart_ruler_dignity = _get_chart_ruler(asc_idx, planets)
    lot_of_fortune = _normalize(ascendant + moon_lon - sun_lon) if is_day \
        else _normalize(ascendant + sun_lon - moon_lon)

    # Arabic Parts
    arabic_parts = _compute_arabic_parts(
        ascendant, sun_lon, moon_lon,
        planet_lons.get("Saturn ♄", 0.0),
        planet_lons.get("Jupiter ♃", 0.0),
        planet_lons.get("Venus ♀", 0.0),
        planet_lons.get("Mercury ☿", 0.0),
        is_day, cusps,
    )

    # Fixed Star Conjunctions
    fixed_star_conjunctions = _compute_fixed_star_conjunctions(planets, jd)

    return WesternChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd,
        planets=planets, houses=houses,
        ascendant=ascendant, midheaven=midheaven,
        asc_sign=ZODIAC_SIGNS[asc_idx][0],
        mc_sign=ZODIAC_SIGNS[mc_idx][0],
        is_day_chart=is_day,
        chart_ruler=chart_ruler,
        chart_ruler_dignity=chart_ruler_dignity,
        lot_of_fortune=lot_of_fortune,
        arabic_parts=arabic_parts,
        fixed_star_conjunctions=fixed_star_conjunctions,
        sidereal_mode=sidereal,
        ayanamsa=ayanamsa,
    )


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_western_chart(chart, after_chart_hook=None, gender=None):
    """渲染完整的西洋占星排盤"""
    _render_wheel_chart(chart, gender=gender)
    if after_chart_hook:
        after_chart_hook()
    st.divider()
    _render_info(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_house_table(chart)
    st.divider()
    _render_aspects(chart)
    st.divider()
    _render_classical_dignities(chart)
    st.divider()
    _render_day_night_sect(chart)
    st.divider()
    _render_chart_ruler(chart)
    st.divider()
    _render_arabic_parts(chart)
    st.divider()
    _render_fixed_stars(chart)


def _render_info(chart):
    st.subheader("📋 Chart Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Date:** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**Time:** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**Timezone:** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**Location:** {chart.location_name}")
        asc_info = ZODIAC_SIGNS[_sign_index(chart.ascendant)]
        mc_info = ZODIAC_SIGNS[_sign_index(chart.midheaven)]
        st.write(
            f"**Ascendant:** {asc_info[1]} {chart.asc_sign} "
            f"({asc_info[2]}) "
            f"{_format_deg(chart.ascendant)}"
        )
        st.write(
            f"**Midheaven:** {mc_info[1]} {chart.mc_sign} {_format_deg(chart.midheaven)}"
        )
    if chart.sidereal_mode:
        st.info(f"⚙️ **Sidereal Mode (Lahiri Ayanamsa):** {chart.ayanamsa:.2f}°")


def _render_wheel_chart(chart, gender=None):
    """渲染西洋占星輪圖 (Western Wheel Chart) — SVG 版"""
    st.subheader("🔮 西洋占星輪盤 (Western Wheel)")

    asc_idx = _sign_index(chart.ascendant)
    mc_idx = _sign_index(chart.midheaven)

    house_signs = {}
    for h in chart.houses:
        house_signs[h.number] = _sign_index(h.cusp)

    asc_info = ZODIAC_SIGNS[asc_idx]
    mc_info = ZODIAC_SIGNS[mc_idx]

    wheel_grid = [
        [10, 11, 12, 1],
        [9, -1, -1, 2],
        [8, -1, -1, 3],
        [7, 6, 5, 4],
    ]

    # SVG layout constants
    W = 560
    CAP_H = 44
    CW = W / 4          # cell width  = 140
    CH = 110             # cell height = 110
    H = CAP_H + CH * 4  # total height

    def _esc(text):
        """Escape special XML characters for safe SVG text content."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    parts: list[str] = []
    parts.append(
        f'<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {W} {H}" '
        f'style="width:100%;max-width:{W}px;display:block;margin:auto;'
        f'font-family:sans-serif;">'
    )

    # Caption
    asc_deg = f"{_sign_degree(chart.ascendant):.1f}"
    mc_deg = f"{_sign_degree(chart.midheaven):.1f}"
    parts.append(
        f'<text x="{W / 2}" y="17" text-anchor="middle" '
        f'fill="#e0e0e0" font-size="14" font-weight="bold">'
        f'Western Wheel Chart</text>'
    )
    parts.append(
        f'<text x="{W / 2}" y="36" text-anchor="middle" '
        f'fill="#c8c8c8" font-size="11">'
        f'\u0020\u25B2 ASC {_esc(asc_info[1])}{_esc(asc_info[0])} {asc_deg}\u00B0'
        f'\u2003\u2B21 MC {_esc(mc_info[1])}{_esc(mc_info[0])} {mc_deg}\u00B0'
        f'</text>'
    )

    center_rendered = False
    for r, row_data in enumerate(wheel_grid):
        for c, idx in enumerate(row_data):
            x = c * CW
            y = CAP_H + r * CH
            cx = x + CW / 2

            if idx == -1:
                if center_rendered:
                    continue
                # Merge four centre cells into one — show birth info
                center_rendered = True
                mx = 1 * CW       # col 1
                my = CAP_H + 1 * CH  # row 1
                mw = CW * 2       # span 2 cols
                mh = CH * 2       # span 2 rows
                mcx = mx + mw / 2
                mcy = my + mh / 2

                parts.append(
                    f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" '
                    f'fill="#1a1a2e" stroke="#444" stroke-width="1" rx="2"/>'
                )

                # Birth date line
                date_str = f'{chart.year}/{chart.month:02d}/{chart.day:02d}'
                time_str = f'{chart.hour:02d}:{chart.minute:02d}'
                tz_str = f'UTC{chart.timezone:+.1f}'
                parts.append(
                    f'<text x="{mcx}" y="{mcy - 28}" text-anchor="middle" '
                    f'fill="#e0e0e0" font-size="12">'
                    f'{_esc(date_str)}  {_esc(time_str)}</text>'
                )
                parts.append(
                    f'<text x="{mcx}" y="{mcy - 10}" text-anchor="middle" '
                    f'fill="#aaa" font-size="11">{_esc(tz_str)}</text>'
                )

                # Gender line
                if gender:
                    gender_label = "男命" if gender == "male" else "女命"
                    parts.append(
                        f'<text x="{mcx}" y="{mcy + 10}" text-anchor="middle" '
                        f'fill="#e0e0e0" font-size="12">{_esc(gender_label)}</text>'
                    )

                # Location line
                if chart.location_name:
                    parts.append(
                        f'<text x="{mcx}" y="{mcy + 30}" text-anchor="middle" '
                        f'fill="#aaa" font-size="11">{_esc(chart.location_name)}</text>'
                    )
                continue

            h = next((hh for hh in chart.houses if hh.number == idx), None)
            if h is None:
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" '
                    f'fill="#1e1e2e" stroke="#444" stroke-width="1"/>'
                )
                continue

            sign_idx = house_signs.get(idx, _sign_index(h.cusp))
            sign_info = ZODIAC_SIGNS[sign_idx]
            planets_in_house = h.planets

            is_asc = idx == 1
            is_mc = idx == 10
            fill = (
                "#3d3010" if is_asc else ("#1a2a3d" if is_mc else "#1e1e2e")
            )

            parts.append(
                f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" '
                f'fill="{fill}" stroke="#444" stroke-width="1" rx="2"/>'
            )

            # House number + marker
            marker = " \u25B2" if is_asc else (" \u2B21" if is_mc else "")
            parts.append(
                f'<text x="{cx}" y="{y + 18}" text-anchor="middle" '
                f'fill="#e0e0e0" font-size="13" font-weight="bold">'
                f'{idx}{marker}</text>'
            )

            # Sign glyph + name
            parts.append(
                f'<text x="{cx}" y="{y + 34}" text-anchor="middle" '
                f'fill="#e0e0e0" font-size="11">'
                f'{_esc(sign_info[1])} {_esc(sign_info[0])}</text>'
            )

            # Degree
            parts.append(
                f'<text x="{cx}" y="{y + 48}" text-anchor="middle" '
                f'fill="#aaa" font-size="10">{_esc(_format_deg(h.cusp))}</text>'
            )

            # Planets – laid out in rows of up to 3
            if planets_in_house:
                n = len(planets_in_house)
                font_size = 11 if n <= 2 else (10 if n <= 3 else 9)
                names = [p.split(" ")[0] for p in planets_in_house]
                per_row = min(n, 3)
                p_spacing = 44   # horizontal gap between planet labels
                p_base_y = 66    # vertical offset for first planet row
                p_row_h = 16     # vertical gap between planet rows
                for i, (short, full) in enumerate(
                    zip(names, planets_in_house)
                ):
                    row_i = i // per_row
                    col_i = i % per_row
                    row_count = min(per_row, n - row_i * per_row)
                    px = cx + (col_i - (row_count - 1) / 2) * p_spacing
                    py = y + p_base_y + row_i * p_row_h
                    color = PLANET_COLORS.get(full, "#c8c8c8")
                    parts.append(
                        f'<text x="{px}" y="{py}" text-anchor="middle" '
                        f'fill="{color}" font-size="{font_size}" '
                        f'font-weight="bold">{_esc(short)}</text>'
                    )
            else:
                parts.append(
                    f'<text x="{cx}" y="{y + 68}" text-anchor="middle" '
                    f'fill="#555" font-size="11">\u2014</text>'
                )

    parts.append("</svg></div>")
    st.markdown("".join(parts), unsafe_allow_html=True)
    st.caption("▲ = House 1 (Ascendant)   ⬡ = House 10 (Midheaven)")


def _render_planet_table(chart):
    st.subheader("🪐 Planet Positions")
    header = (
        "| Planet | Sign | Degree | Element | House | Retrograde "
        "| Essential Dignity | Joy Status |"
    )
    sep = (
        "|:------:|:----:|:------:|:-------:|:-----:|:----------:"
        "|:---------------:|:---------:|"
    )
    rows = [header, sep]
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        rows.append(
            f"| {name_html} "
            f"| {p.sign_glyph} {p.sign} ({p.sign_chinese}) "
            f"| {p.sign_degree:.2f}° "
            f"| {p.element} "
            f"| {p.house} "
            f"| {retro} "
            f"| {p.essential_dignity} "
            f"| {p.joy_status} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_house_table(chart):
    st.subheader("🏛️ House Cusps")
    header = "| House | Cusp | Sign | Planets |"
    sep = "|:-----:|:----:|:----:|:-------:|"
    rows = [header, sep]
    for h in chart.houses:
        planets_str = ", ".join(h.planets) if h.planets else "—"
        rows.append(
            f"| {h.number} | {_format_deg(h.cusp)} "
            f"| {h.sign_glyph} {h.sign} | {planets_str} |"
        )
    st.markdown("\n".join(rows))


def _render_aspects(chart):
    st.subheader("🔗 Aspects")
    aspects = []
    for i in range(len(chart.planets)):
        for j in range(i + 1, len(chart.planets)):
            p1 = chart.planets[i]
            p2 = chart.planets[j]
            diff = abs(p1.longitude - p2.longitude)
            if diff > 180:
                diff = 360 - diff
            for asp in ASPECT_TYPES:
                orb = abs(diff - asp["angle"])
                if orb <= asp["orb"]:
                    aspects.append({
                        "p1": p1.name, "p2": p2.name,
                        "aspect": asp["name"], "symbol": asp["symbol"],
                        "orb": orb,
                    })
                    break
    if not aspects:
        st.info("No significant aspects found.")
        return
    header = "| Planet 1 | Aspect | Planet 2 | Orb |"
    sep = "|:--------:|:------:|:--------:|:---:|"
    rows = [header, sep]
    for a in aspects:
        rows.append(
            f"| {a['p1']} | {a['symbol']} {a['aspect']} "
            f"| {a['p2']} | {a['orb']:.1f}° |"
        )
    st.markdown("\n".join(rows))


def _render_classical_dignities(chart):
    st.subheader("🏛️ 本質廟旺落陷 (Essential Dignities & Debilities)")
    rows = [
        "| Planet | Sign | House | Dignity | Joy |",
        "|:------:|:----:|:-----:|:-------:|:---:|",
    ]
    for p in chart.planets:
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        dignity_icon = ""
        if "入廟" in p.essential_dignity:
            dignity_icon = "♔"
        elif "入旺" in p.essential_dignity:
            dignity_icon = "↑"
        elif "落陷" in p.essential_dignity:
            dignity_icon = "♕"
        elif "入弱" in p.essential_dignity:
            dignity_icon = "↓"
        rows.append(
            f"| {name_html} "
            f"| {p.sign_glyph} {p.sign} ({p.sign_chinese}) "
            f"| {p.house} "
            f"| {dignity_icon} {p.essential_dignity} "
            f"| {'⭐' if '喜樂' in p.joy_status else '—'} {p.joy_status} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)

    st.markdown("**符號說明:** ♔ 入廟 | ↑ 入旺 | ♕ 落陷 | ↓ 入弱 | ⭐ 喜樂")


def _render_day_night_sect(chart):
    st.subheader("☀️ 🌙 日夜盤判定 (Day & Night Sect)")
    if chart.is_day_chart:
        st.success(
            "**日盤 (Day Chart)** — 太陽位於地平線以上（House 7–12）\n\n"
            "日盤中，太陽作為主要主宰，行星若在日間位置（晝行星，如 Sun、Jupiter、Saturn）效力更強。\n\n"
            "⚠️ 本盤 Venus、Moon 等夜行星在此盤中效力減弱。"
        )
    else:
        st.info(
            "**夜盤 (Night Chart)** — 太陽位於地平線以下（House 1–6）\n\n"
            "夜盤中，月亮作為主要主宰，夜行星（如 Moon、Venus）效力更強。\n\n"
            "⚠️ 本盤 Sun、Jupiter 等日行星在此盤中效力減弱。"
        )


def _render_chart_ruler(chart):
    st.subheader("👑 命度主星 (Chart Ruler)")
    asc_idx = _sign_index(chart.ascendant)
    asc_sign_info = ZODIAC_SIGNS[asc_idx]
    ruler_info = CLASSICAL_DIGNITIES[asc_idx]
    ruler_name = ruler_info.get("domicile", "—")

    dignity_icon = ""
    dignity_text = chart.chart_ruler_dignity
    if "入廟" in dignity_text:
        dignity_icon = "♔"
    elif "入旺" in dignity_text:
        dignity_icon = "↑"
    elif "落陷" in dignity_text:
        dignity_icon = "♕"
    elif "入弱" in dignity_text:
        dignity_icon = "↓"

    st.markdown(
        f"**上升星座:** {asc_sign_info[1]} {asc_sign_info[0]}（{asc_sign_info[2]}）\n\n"
        f"**命度主星:** {chart.chart_ruler} — {dignity_icon} {dignity_text}\n\n"
        f"**主星守護:** {ruler_name or '—'} 守護 {asc_sign_info[0]}\n\n"
        f"命度主星是全盤最重要的行星，它的吉凶、廟旺落陷、飛遊狀態\n"
        f"決定了命主一生的主要命運走向。"
    )

    # Also show the main significators
    st.markdown("**主要象徵星:**")
    sig_cols = st.columns(3)
    with sig_cols[0]:
        st.markdown(f"**命度主星:** {chart.chart_ruler}")
    with sig_cols[1]:
        st.markdown(f"**助產星 (Exaltation):** "
                    f"{ruler_info.get('exaltation', '—') or '—'}")
    with sig_cols[2]:
        first_house_planets = next(
            (", ".join(h.planets) for h in chart.houses if h.number == 1), "空"
        )
        moon_name = next((p.name for p in chart.planets if "Moon" in p.name), "—")
        st.markdown(
            f"**命宮行星:** {first_house_planets}\n\n"
            f"**身宮 (Moon):** {moon_name}"
        )


def _render_arabic_parts(chart):
    st.subheader("🔮 阿拉伯點 / 幸運點 (Arabic Parts / Lots)")

    # Day/Night indicator
    sect = "日盤公式" if chart.is_day_chart else "夜盤公式"
    st.caption(f"計算方式: {sect} — Lot of Fortune = ASC + {'Moon - Sun' if chart.is_day_chart else 'Sun - Moon'}")

    header = "| Lot | Sign | Degree | House |"
    sep = "|:---|:----:|:------:|:-----:|"
    rows = [header, sep]
    for part in chart.arabic_parts:
        rows.append(
            f"| **{part.chinese_name}** ({part.english_name}) "
            f"| {part.sign_glyph} {part.sign} "
            f"| {part.sign_degree:.2f}° "
            f"| {part.house} |"
        )
    st.markdown("\n".join(rows))

    st.markdown(
        "**說明:** 阿拉伯點是古典占星的重要技法，"
        "透過上升點與行星經度的加減運算推導各生活領域的敏感度數。"
    )


def _render_fixed_stars(chart):
    st.subheader("⭐ 恆星相位 (Fixed Star Conjunctions)")

    if not chart.fixed_star_conjunctions:
        st.info("本盤無恆星與行星形成緊密合相（orb ≤ 1°）。")
        return

    header = "| Planet | Fixed Star | Chinese | Orb | 恆星意義 |"
    sep = "|:------:|:----------:|:-------:|:---:|:------:|"
    rows = [header, sep]
    for fc in chart.fixed_star_conjunctions:
        p_color = PLANET_COLORS.get(fc.planet_name, "#c8c8c8")
        planet_html = f'<span style="color:{p_color};font-weight:bold">{fc.planet_name}</span>'
        rows.append(
            f"| {planet_html} "
            f"| {fc.star_name} "
            f"| {fc.star_name_cn} "
            f"| {fc.orb:.2f}° "
            f"| {fc.meaning} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)

    st.markdown(
        "**恆星說明:** 恆星（Fixed Stars）與行星合相時，"
        "會赋予行星特殊的影響力，其效力較一般行星相位更為強烈且恆定。\n\n"
        "主要恆星：\n"
        "- **Aldebaran (畢宿五)** — 勇氣、好戰\n"
        "- **Regulus (軒轅十四)** — 王權、吉祥\n"
        "- **Antares (心宿二)** — 膽識、軍事\n"
        "- **Spica (角宿一)** — 財富、創造\n"
        "- **Sirius (天狼星)** — 榮耀、財富\n"
    )
