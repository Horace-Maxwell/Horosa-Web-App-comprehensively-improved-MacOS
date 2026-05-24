"""
泰國占星排盤模組 (Thai Horasastra Astrology Module)

โหราศาสตร์ไทย — Thai Horasastra based on Jyotish, with 9 Navagraha
(including ราหู Rahu & เกตุ Ketu), 12 Rashi, 27 Nakshatra,
Whole Sign Houses, Brahma Jati (พรหมชาติ) remedies, and
traditional day-planet (Phra) correspondences.
"""

import json
import math
import os
import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

# ============================================================
# 常量 (Constants)
# ============================================================

# Buddhist Era offset: BE year = CE year + 543
_BE_OFFSET = 543


def _to_be_year(ce_year):
    """Convert CE year to Buddhist Era (พุทธศักราช / พ.ศ.) year."""
    return ce_year + _BE_OFFSET


THAI_PLANETS = {
    "พระอาทิตย์ (太陽)": swe.SUN,
    "พระจันทร์ (月亮)": swe.MOON,
    "พระอังคาร (火星)": swe.MARS,
    "พระพุธ (水星)": swe.MERCURY,
    "พระพฤหัสบดี (木星)": swe.JUPITER,
    "พระศุกร์ (金星)": swe.VENUS,
    "พระเสาร์ (土星)": swe.SATURN,
}

# Thai names for the 12 Rashis
# Tuple: (full_name, glyph, chinese, lord, short_abbr)
# short_abbr: 2-char Thai abbreviation used in traditional Thai astrology charts
THAI_RASHIS = [
    ("เมษ (Mesha)", "♈", "白羊", "พระอังคาร", "มษ"),
    ("พฤษภ (Vrishabha)", "♉", "金牛", "พระศุกร์", "พษ"),
    ("เมถุน (Mithuna)", "♊", "雙子", "พระพุธ", "มถ"),
    ("กรกฎ (Karka)", "♋", "巨蟹", "พระจันทร์", "กร"),
    ("สิงห์ (Simha)", "♌", "獅子", "พระอาทิตย์", "สห"),
    ("กันย์ (Kanya)", "♍", "處女", "พระพุธ", "กย"),
    ("ตุลย์ (Tula)", "♎", "天秤", "พระศุกร์", "ตล"),
    ("พิจิก (Vrischika)", "♏", "天蠍", "พระอังคาร", "พก"),
    ("ธนู (Dhanu)", "♐", "射手", "พระพฤหัสบดี", "ธน"),
    ("มกร (Makara)", "♑", "摩羯", "พระเสาร์", "มก"),
    ("กุมภ์ (Kumbha)", "♒", "水瓶", "พระเสาร์", "กภ"),
    ("มีน (Meena)", "♓", "雙魚", "พระพฤหัสบดี", "มน"),
]

# Thai day-planet correspondences for interpretive context
THAI_DAY_PLANETS = {
    0: ("วันอาทิตย์ (Sunday)", "พระอาทิตย์"),
    1: ("วันจันทร์ (Monday)", "พระจันทร์"),
    2: ("วันอังคาร (Tuesday)", "พระอังคาร"),
    3: ("วันพุธ (Wednesday)", "พระพุธ"),
    4: ("วันพฤหัสบดี (Thursday)", "พระพฤหัสบดี"),
    5: ("วันศุกร์ (Friday)", "พระศุกร์"),
    6: ("วันเสาร์ (Saturday)", "พระเสาร์"),
}

PLANET_COLORS = {
    "พระอาทิตย์ (太陽)": "#FF8C00",
    "พระจันทร์ (月亮)": "#C0C0C0",
    "พระอังคาร (火星)": "#DC143C",
    "พระพุธ (水星)": "#4169E1",
    "พระพฤหัสบดี (木星)": "#FFD700",
    "พระศุกร์ (金星)": "#FF69B4",
    "พระเสาร์ (土星)": "#8B4513",
    "ราหู (羅睺)": "#800080",
    "เกตุ (計都)": "#4B0082",
}

# ============================================================
# 27 Nakshatras (二十七宿 / นักษัตร)
# Each spans 13°20' (800').  Index = int(moon_sidereal_lon / (360/27))
# Tuple: (thai_name, english_name, chinese_name, lord_planet, brief_reading)
# lord_planet key: Su=Sun, Mo=Moon, Ma=Mars, Me=Mercury, Ju=Jupiter,
#                  Ve=Venus, Sa=Saturn, Ra=Rahu, Ke=Ketu
# ============================================================

THAI_NAKSHATRAS = [
    ("อัศวินี", "Ashwini", "馬頭宿", "Ke", "敏捷、療癒、先驅精神，宜開創新事業。"),
    ("ภรณี", "Bharani", "大陵宿", "Ve", "熱情、強烈、承載生死，宜藝術與感情。"),
    ("กฤตติกา", "Krittika", "昴宿", "Su", "鋒利、淨化、領導力，宜決斷與權威。"),
    ("โรหิณี", "Rohini", "畢宿", "Mo", "美麗、穩定、豐饒，宜財富與享樂。"),
    ("มฤคศิรา", "Mrigashira", "觜宿", "Ma", "好奇、探索、溫和，宜旅行與研究。"),
    ("อารทรา", "Ardra", "參宿", "Ra", "風暴、變革、深刻，宜突破與轉型。"),
    ("ปุนรวสุ", "Punarvasu", "井宿", "Ju", "回歸、重生、智慧，宜學習與修行。"),
    ("ปุษยะ", "Pushya", "鬼宿", "Sa", "滋養、吉祥、穩重，最吉之宿，萬事可行。"),
    ("อาศเลษา", "Ashlesha", "柳宿", "Me", "蛇性、神秘、深邃，宜研究與靈性修行。"),
    ("มฆา", "Magha", "星宿", "Ke", "皇族、祖先、權勢，宜祭祀與傳承。"),
    ("ปุรวผลคุณี", "Purva Phalguni", "張宿", "Ve", "享樂、愛情、創意，宜婚姻與藝術。"),
    ("อุตตรผลคุณี", "Uttara Phalguni", "翼宿", "Su", "友善、守護、責任，宜合作與契約。"),
    ("หัสตะ", "Hasta", "軫宿", "Mo", "巧手、技藝、聰慧，宜手工與治療。"),
    ("จิตรา", "Chitra", "角宿", "Ma", "輝煌、建築、美學，宜設計與創造。"),
    ("สวาตี", "Swati", "亢宿", "Ra", "獨立、自由、柔韌，宜貿易與外交。"),
    ("วิศาขา", "Vishakha", "氐宿", "Ju", "雙重、決心、目標，宜競爭與成就。"),
    ("อนุราธา", "Anuradha", "房宿", "Sa", "友誼、忠誠、組織，宜合作與團隊。"),
    ("เชษฐา", "Jyeshtha", "心宿", "Me", "首領、保護、勇敢，宜領導與防衛。"),
    ("มูละ", "Mula", "尾宿", "Ke", "根源、破壞重建、深層，宜研究與靈修。"),
    ("ปุรวาษาฒ", "Purva Ashadha", "箕宿", "Ve", "勝利、淨化、激勵，宜宣傳與說服。"),
    ("อุตตราษาฒ", "Uttara Ashadha", "斗宿", "Su", "不可戰勝、正義、真理，宜從政與公義。"),
    ("ศรวณะ", "Shravana", "牛宿", "Mo", "聆聽、學習、傳播，宜教育與傳媒。"),
    ("ธนิษฐา", "Dhanishta", "女宿", "Ma", "富裕、韻律、名望，宜音樂與表演。"),
    ("ศตภิษัช", "Shatabhisha", "虛宿", "Ra", "百藥、治療、神秘，宜醫療與靈性。"),
    ("ปุรวภัทรปท", "Purva Bhadrapada", "危宿", "Ju", "燃燒、苦行、英雄，宜靈修與轉化。"),
    ("อุตตรภัทรปท", "Uttara Bhadrapada", "室宿", "Sa", "深沉、安穩、智慧，宜冥想與穩定。"),
    ("เรวตี", "Revati", "壁宿", "Me", "養育、旅途、圓滿，宜遠行與收成。"),
]

# Lord abbreviation → full Thai planet name
_NAK_LORD_MAP = {
    "Su": "พระอาทิตย์ (太陽)", "Mo": "พระจันทร์ (月亮)",
    "Ma": "พระอังคาร (火星)", "Me": "พระพุธ (水星)",
    "Ju": "พระพฤหัสบดี (木星)", "Ve": "พระศุกร์ (金星)",
    "Sa": "พระเสาร์ (土星)", "Ra": "ราหู (羅睺)",
    "Ke": "เกตุ (計都)",
}

# Day-planet traditional omens (吉凶預兆)
THAI_DAY_OMENS = {
    0: "วันอาทิตย์出生者具備領導魅力與權威，宜從事公職或領導職務。太陽守護帶來光明正大之性格。",
    1: "วันจันทร์出生者情感細膩、直覺敏銳，宜從事藝術、照護或教育。月亮守護帶來柔和與智慧。",
    2: "วันอังคาร出生者勇敢果斷、精力充沛，宜從事軍警、運動或競爭性行業。火星守護帶來行動力。",
    3: "วันพุธ出生者聰慧靈活、善於溝通，宜從事商業、文學或學術。水星守護帶來機智與人緣。",
    4: "วันพฤหัสบดี出生者福德深厚、受人尊敬，宜從事宗教、教育或顧問。木星守護帶來幸運與擴展。",
    5: "วันศุกร์出生者風雅迷人、愛好美感，宜從事藝術、時尚或娛樂。金星守護帶來魅力與財運。",
    6: "วันเสาร์出生者堅毅沉穩、紀律嚴明，宜從事工程、法律或管理。土星守護帶來持久力與智慧。",
}

# Brahma Jati JSON loader (cached)
_DATA_DIR = os.path.join(os.path.dirname(__file__), "thai", "data")


@st.cache_data(ttl=86400, show_spinner=False)
def _load_brahma_jati_remedies():
    """Load Brahma Jati spells & remedies JSON."""
    path = os.path.join(_DATA_DIR, "brahma_jati_spells_remedies.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# Planet glyphs for SVG rendering
PLANET_GLYPHS_THAI = {
    "พระอาทิตย์ (太陽)": "☉", "พระจันทร์ (月亮)": "☽",
    "พระอังคาร (火星)": "♂", "พระพุธ (水星)": "☿",
    "พระพฤหัสบดี (木星)": "♃", "พระศุกร์ (金星)": "♀",
    "พระเสาร์ (土星)": "♄", "ราหู (羅睺)": "☊",
    "เกตุ (計都)": "☋",
}


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class ThaiPlanet:
    """Thai planet position"""
    name: str
    longitude: float
    latitude: float
    rashi: str
    rashi_glyph: str
    rashi_chinese: str
    rashi_lord: str
    sign_degree: float
    retrograde: bool
    house: int = 0
    rashi_abbr: str = ""


@dataclass
class ThaiHouse:
    """Thai bhava (house)"""
    number: int
    cusp: float
    rashi: str
    rashi_glyph: str
    planets: list = field(default_factory=list)


@dataclass
class ThaiChart:
    """Thai astrology chart"""
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
    day_of_week: int
    day_planet: str
    planets: list
    houses: list
    ascendant: float
    asc_rashi: str
    nakshatra: dict = field(default_factory=dict)
    brahma_jati: dict = field(default_factory=dict)
    omens: str = ""
    remedies: dict = field(default_factory=dict)


# ============================================================
# 計算函數 (Calculation Functions)
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


def _format_deg_thai(sign_degree):
    """Format degree within sign as DD:MM style (Thai app convention).

    Args:
        sign_degree (float): degree within sign (0–30).

    Returns:
        str: e.g. "04:12" for 4°12'.
    """
    d = int(sign_degree)
    m = int((sign_degree - d) * 60)
    return f"{d:02d}:{m:02d}"


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


def _nakshatra_index(lon):
    """Return 0-based Nakshatra index for a sidereal longitude."""
    return int(_normalize(lon) / (360.0 / 27.0)) % 27


def _get_nakshatra_info(lon):
    """Return Nakshatra dict for a given sidereal longitude."""
    idx = _nakshatra_index(lon)
    nak = THAI_NAKSHATRAS[idx]
    pada = int((_normalize(lon) % (360.0 / 27.0)) / (360.0 / 108.0)) + 1
    return {
        "index": idx,
        "thai": nak[0],
        "english": nak[1],
        "chinese": nak[2],
        "lord": nak[3],
        "lord_name": _NAK_LORD_MAP.get(nak[3], nak[3]),
        "reading": nak[4],
        "pada": pada,
    }


def _whole_sign_cusps(asc_lon):
    """Compute Whole Sign house cusps from Ascendant longitude.

    In Whole Sign Houses the cusp of House 1 starts at the beginning
    of the Ascendant's sign (i.e. sign_index * 30).
    """
    asc_sign = _sign_index(asc_lon)
    return [((asc_sign + i) % 12) * 30.0 for i in range(12)]


@st.cache_data(ttl=3600, show_spinner=False)
def compute_thai_chart(year, month, day, hour, minute, timezone,
                       latitude, longitude, location_name=""):
    """計算泰國占星排盤 (Sidereal / Lahiri Ayanamsa / Whole Sign Houses)

    Returns a ThaiChart with 9 Navagraha positions, 27-Nakshatra data
    for Moon, Brahma Jati colour/remedy, and day-planet omen reading.
    """
    swe.set_ephe_path("")
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Day of week: 0=Mon … 6=Sun in Python, but we need 0=Sun … 6=Sat
    import datetime as _dt
    dt = _dt.date(year, month, day)
    # isoweekday: 1=Mon … 7=Sun → convert to 0=Sun,1=Mon,...,6=Sat
    dow = dt.isoweekday() % 7
    day_name, day_planet = THAI_DAY_PLANETS[dow]

    # Compute sidereal Ascendant (use Whole Sign to get ascmc; raw cusps
    # are discarded in favour of our own _whole_sign_cusps calculation)
    _, ascmc = swe.houses_ex(jd, latitude, longitude, b"W",
                             swe.FLG_SIDEREAL)
    ascendant = _normalize(ascmc[0])

    # Whole Sign cusps
    cusps = _whole_sign_cusps(ascendant)

    planets = []
    moon_lon = None
    for name, pid in THAI_PLANETS.items():
        result, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        rashi = THAI_RASHIS[idx]

        planets.append(ThaiPlanet(
            name=name, longitude=lon, latitude=lat,
            rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
            rashi_lord=rashi[3], sign_degree=_sign_degree(lon),
            retrograde=speed < 0, rashi_abbr=rashi[4],
        ))
        if pid == swe.MOON:
            moon_lon = lon

    # Rahu (ราหู) — Mean Node; always retrograde in Thai tradition
    rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _normalize(rahu_res[0])
    idx = _sign_index(rahu_lon)
    rashi = THAI_RASHIS[idx]
    planets.append(ThaiPlanet(
        name="ราหู (羅睺)", longitude=rahu_lon, latitude=rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], sign_degree=_sign_degree(rahu_lon),
        retrograde=True, rashi_abbr=rashi[4],
    ))

    # Ketu (เกตุ) — always opposite Rahu; also always retrograde
    ketu_lon = _normalize(rahu_lon + 180.0)
    idx = _sign_index(ketu_lon)
    rashi = THAI_RASHIS[idx]
    planets.append(ThaiPlanet(
        name="เกตุ (計都)", longitude=ketu_lon, latitude=-rahu_res[1],
        rashi=rashi[0], rashi_glyph=rashi[1], rashi_chinese=rashi[2],
        rashi_lord=rashi[3], sign_degree=_sign_degree(ketu_lon),
        retrograde=True, rashi_abbr=rashi[4],
    ))

    # Build Whole Sign houses
    houses = []
    for i in range(12):
        cusp = cusps[i]
        idx = _sign_index(cusp)
        rashi = THAI_RASHIS[idx]
        houses.append(ThaiHouse(
            number=i + 1, cusp=cusp,
            rashi=rashi[0], rashi_glyph=rashi[1],
            planets=[],
        ))

    for p in planets:
        h = _find_house(p.longitude, cusps)
        p.house = h
        houses[h - 1].planets.append(p.name)

    asc_rashi = THAI_RASHIS[_sign_index(ascendant)][0]

    # Moon Nakshatra
    nakshatra = _get_nakshatra_info(moon_lon) if moon_lon is not None else {}

    # Day-planet omens
    omens = THAI_DAY_OMENS.get(dow, "")

    # Brahma Jati colour/remedy from JSON
    bj_data = _load_brahma_jati_remedies()
    _day_names_en = ["Sunday", "Monday", "Tuesday", "Wednesday",
                     "Thursday", "Friday", "Saturday"]
    day_en = _day_names_en[dow]
    bj_color = {}
    if bj_data:
        color_by_day = bj_data.get("color_by_day", {})
        bj_color = color_by_day.get(day_en, {})
    brahma_jati = {
        "day_color": bj_color,
        "general_remedies": bj_data.get("general_remedies", {}),
    }
    remedies = bj_color

    return ThaiChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd, ayanamsa=ayanamsa,
        day_of_week=dow, day_planet=day_planet,
        planets=planets, houses=houses,
        ascendant=ascendant, asc_rashi=asc_rashi,
        nakshatra=nakshatra, brahma_jati=brahma_jati,
        omens=omens, remedies=remedies,
    )


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_thai_chart(chart, after_chart_hook=None):
    """渲染完整的泰國占星排盤"""
    # SVG mandala chart
    svg = build_thai_mandala_svg(chart)
    st.markdown(svg, unsafe_allow_html=True)

    if after_chart_hook:
        after_chart_hook()
    st.divider()
    _render_info(chart)
    st.divider()
    _render_nakshatra_section(chart)
    st.divider()
    _render_omens_section(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_house_table(chart)
    st.divider()
    _render_brahma_jati_section(chart)


def _render_info(chart):
    st.subheader("📋 ข้อมูลดวง (排盤資訊)")
    be_year = _to_be_year(chart.year)
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**วันที่ (日期):** {chart.day:02d}/{chart.month:02d}/{be_year} "
                 f"<small style='color:#888'>(พ.ศ. / ค.ศ. {chart.year})</small>",
                 unsafe_allow_html=True)
        st.write(f"**เวลา (時間):** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**เขตเวลา (時區):** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**สถานที่ (地點):** {chart.location_name}")
        day_name = THAI_DAY_PLANETS[chart.day_of_week][0]
        st.write(f"**{day_name}**")
        st.write(f"**ดาวประจำวัน (日主星):** {chart.day_planet}")
        st.write(f"**ลัคนา (命宮):** {chart.asc_rashi} "
                 f"{_format_deg(chart.ascendant)}")
        st.write(f"**Ayanamsa (歲差):** {chart.ayanamsa:.4f}°")


def _render_thai_grid(chart):
    """渲染泰國式方盤"""
    st.subheader("📊 ผังดวงชาตา (泰國排盤)")

    # Thai chart uses similar layout to South Indian
    grid = [
        [3, 2, 1, 0],
        [4, -1, -1, 11],
        [5, -1, -1, 10],
        [6, 7, 8, 9],
    ]

    rashi_planets = {i: [] for i in range(12)}
    for p in chart.planets:
        idx = _sign_index(p.longitude)
        # Use short Thai name (first word)
        short = p.name.split(" ")[0]
        rashi_planets[idx].append((short, p.name))

    asc_idx = _sign_index(chart.ascendant)

    cell_style = (
        "border:1px solid #444; padding:6px; text-align:center; "
        "vertical-align:top; font-size:13px;"
    )
    asc_cell_style = cell_style + " background:#3d3010;"
    center_style = (
        "border:1px solid #444; padding:10px; text-align:center; "
        "vertical-align:middle; font-size:14px; background:#2a2a2a; "
        "color:#e0e0e0;"
    )

    html = '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;"><table style="border-collapse:collapse; margin:auto; width:100%; table-layout:fixed;">'
    for row_idx, row in enumerate(grid):
        html += "<tr>"
        col_idx = 0
        while col_idx < len(row):
            idx = row[col_idx]
            if idx == -1:
                if row_idx == 1 and col_idx == 1:
                    be_year = _to_be_year(chart.year)
                    center_content = (
                        f"<b>ดวงชาตา 泰國占星</b><br/>"
                        f"{chart.day:02d}/{chart.month:02d}/{be_year}"
                        f"<small style='color:#aaa'> (พ.ศ. / ค.ศ. {chart.year})</small><br/>"
                        f"{chart.hour:02d}:{chart.minute:02d} "
                        f"UTC{chart.timezone:+.1f}<br/>"
                        f"{chart.location_name}<br/>"
                        f"Ayanamsa: {chart.ayanamsa:.2f}°"
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
                rashi = THAI_RASHIS[idx]
                style = asc_cell_style if idx == asc_idx else cell_style
                p_list = rashi_planets[idx]
                p_html = " ".join(
                    f'<span style="color:{PLANET_COLORS.get(full, "#e0e0e0")};'
                    f'font-weight:bold">{short}</span>'
                    for short, full in p_list
                ) if p_list else '<span style="color:#666">—</span>'
                marker = " 🔺" if idx == asc_idx else ""
                cell_content = (
                    f"<b>{rashi[4]}{marker}</b>"
                    f'<small style="color:#888"> {rashi[1]}</small><br/>'
                    f'<small style="color:#666">{rashi[2]}</small>'
                    f"<br/>{p_html}"
                )
                html += f'<td style="{style}">{cell_content}</td>'
            col_idx += 1
        html += "</tr>"
    html += "</table></div>"
    st.markdown(html, unsafe_allow_html=True)


def _render_planet_table(chart):
    st.subheader("🪐 ตำแหน่งดาว (行星位置)")
    # Thai-style table: planet | sign abbr | DD:MM | retrograde marker
    header = "| ดาว (Planet) | ราศี (Rashi) | ตำแหน่ง (DD:MM) | เจ้าเรือน (Lord) | ภพ (House) | สถานะ |"
    sep = "|:------------:|:------------:|:---------------:|:----------------:|:----------:|:------:|"
    rows = [header, sep]
    for p in chart.planets:
        # "พ" = พักร (retrograde), "" = direct
        retro_marker = "พ" if p.retrograde else ""
        deg_thai = _format_deg_thai(p.sign_degree)
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = (
            f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        )
        sign_display = (
            f'{p.rashi_glyph} <b>{p.rashi_abbr}</b> '
            f'<small style="color:#888">({p.rashi_chinese})</small>'
        )
        rows.append(
            f"| {name_html} | {sign_display} "
            f"| {deg_thai} | {p.rashi_lord} "
            f"| {p.house} | {retro_marker} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_house_table(chart):
    st.subheader("🏛️ ภพ (宮位)")
    header = "| ภพ (Bhava) | จุดเริ่ม (Cusp) | ราศี (Rashi) | ดาวในภพ (Planets) |"
    sep = "|:----------:|:--------------:|:------------:|:-----------------:|"
    rows = [header, sep]
    for h in chart.houses:
        planets_str = ", ".join(h.planets) if h.planets else "—"
        rows.append(
            f"| {h.number} | {_format_deg(h.cusp)} "
            f"| {h.rashi_glyph} {h.rashi} | {planets_str} |"
        )
    st.markdown("\n".join(rows))


def _render_nakshatra_section(chart):
    """Render Moon Nakshatra information."""
    nak = chart.nakshatra
    if not nak:
        return
    st.subheader("🌙 นักษัตร — Moon Nakshatra (月亮宿)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"**นักษัตร (Nakshatra):** {nak.get('thai', '')} / "
            f"{nak.get('english', '')} / {nak.get('chinese', '')}"
        )
        st.markdown(f"**บาท (Pada):** {nak.get('pada', '')}")
    with col2:
        lord_name = nak.get('lord_name', '')
        lord_color = PLANET_COLORS.get(lord_name, '#e0e0e0')
        st.markdown(
            f"**เจ้าเรือน (Lord):** "
            f"<span style='color:{lord_color};font-weight:bold'>"
            f"{lord_name}</span>",
            unsafe_allow_html=True,
        )
    reading = nak.get('reading', '')
    if reading:
        st.info(f"📖 {reading}")


def _render_omens_section(chart):
    """Render day-planet omen reading."""
    if not chart.omens:
        return
    st.subheader("🔮 คำทำนายตามวันเกิด (日主星預兆)")
    day_name = THAI_DAY_PLANETS[chart.day_of_week][0]
    st.markdown(f"**{day_name}** — ดาวประจำวัน: **{chart.day_planet}**")
    st.markdown(chart.omens)


def _render_brahma_jati_section(chart):
    """Render Brahma Jati colour/remedy section from computed chart data."""
    bj = chart.brahma_jati
    if not bj:
        return
    st.subheader("📿 พรหมชาติ — Brahma Jati (吉色與補救)")
    day_color = bj.get("day_color", {})
    if day_color:
        st.markdown(
            f"**สีมงคล (Lucky Colour):** "
            f"{day_color.get('thai', '')} / {day_color.get('zh', '')} / "
            f"{day_color.get('en', '')}"
        )
        meaning = day_color.get('meaning', '')
        if meaning:
            st.markdown(f"**ผลลัพธ์ (Effect):** {meaning}")
    general = bj.get("general_remedies", {})
    if general:
        with st.expander("📋 คำแนะนำการแก้ไข (General Remedies / 通用補救法)", expanded=False):
            for k, v in general.items():
                st.markdown(f"**{k}.** {v}")


# ============================================================
# Thai Gold Mandala SVG Chart (ผังดวงแบบมณฑลทอง)
# ============================================================


def build_thai_mandala_svg(chart):
    """Build a Thai gold mandala-style SVG chart.

    Features:
    - 12 Whole-Sign house sectors arranged in a circle
    - Gold border with lotus petal decorations
    - Thai temple (Phra) styling with warm gold palette
    - Planet glyphs with Thai text labels
    - Nakshatra callout for Moon
    - Centre circle with birth data and BE year

    Returns
    -------
    str – complete ``<svg>`` markup wrapped in a centring ``<div>``.
    """
    SIZE = 640
    CX, CY = SIZE / 2, SIZE / 2
    R_OUTER = 270       # outer circle radius
    R_INNER = 200       # inner circle (house content area)
    R_CENTRE = 72       # centre info circle

    asc_idx = _sign_index(chart.ascendant)

    # ── house data ─────────────────────────────────────────────
    house_data = []
    for h in range(1, 13):
        sign_idx = (asc_idx + h - 1) % 12
        plist = [(p.name, round(_sign_degree(p.longitude), 1), p.retrograde)
                 for p in chart.planets if _sign_index(p.longitude) == sign_idx]
        house_data.append({"h": h, "sign_idx": sign_idx, "planets": plist})

    def _polar(r, a):
        rad = math.radians(a)
        return CX + r * math.cos(rad), CY - r * math.sin(rad)

    def _house_angle(h):
        """Centre angle of house h (1-indexed). House 1 at left (180°)."""
        return (180 - (h - 1) * 30) % 360

    def _boundary_angle(h):
        return (195 - (h - 1) * 30) % 360

    svg = []
    svg.append(
        f'<div style="text-align:center;overflow-x:auto;max-width:100%;">'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SIZE} {SIZE}" '
        f'style="width:100%;max-width:640px;display:inline-block;" '
        f'font-family="serif">'
    )

    # Background — deep Thai temple blue-black
    svg.append(f'<rect width="{SIZE}" height="{SIZE}" fill="#1a1520" rx="10"/>')

    # Outer gold decorative ring
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER + 18}" '
        f'fill="none" stroke="#c9a84c" stroke-width="3" opacity="0.6"/>'
    )
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER + 12}" '
        f'fill="none" stroke="#d4af37" stroke-width="1.5"/>'
    )

    # Lotus petal decorations around the outer ring
    for i in range(24):
        a = i * 15
        px, py = _polar(R_OUTER + 15, a)
        petal_r = 6
        svg.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{petal_r}" '
            f'fill="#d4af37" fill-opacity="0.15" '
            f'stroke="#d4af37" stroke-width="0.5"/>'
        )

    # Outer ring background
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER}" '
        f'fill="#2a2030" stroke="#d4af37" stroke-width="2"/>'
    )
    # Inner ring
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_INNER}" '
        f'fill="#1e1828" stroke="#b8962e" stroke-width="1.5"/>'
    )

    # ── house sector lines ─────────────────────────────────────
    for h in range(1, 13):
        ba = _boundary_angle(h)
        p1 = _polar(R_OUTER, ba)
        p2 = _polar(R_CENTRE + 4, ba)
        svg.append(
            f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" '
            f'x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" '
            f'stroke="#b8962e" stroke-width="0.8" opacity="0.7"/>'
        )

    # ── house content ──────────────────────────────────────────
    for hd in house_data:
        h = hd["h"]
        si = hd["sign_idx"]
        ca = _house_angle(h)
        rashi = THAI_RASHIS[si]

        # Sign glyph (outer area)
        gx, gy = _polar(R_OUTER * 0.88, ca)
        svg.append(
            f'<text x="{gx:.1f}" y="{gy:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#d4af37" '
            f'font-size="18" font-weight="bold">{rashi[1]}</text>'
        )

        # Thai abbreviation (inner area)
        ax, ay = _polar(R_OUTER * 0.77, ca)
        svg.append(
            f'<text x="{ax:.1f}" y="{ay:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#c9a84c" '
            f'font-size="10">{rashi[4]}</text>'
        )

        # House number
        hx, hy = _polar(R_INNER * 0.55, ca)
        h_fill = "#d4af37" if h in (1, 4, 7, 10) else "#9a8a5a"
        svg.append(
            f'<text x="{hx:.1f}" y="{hy:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{h_fill}" '
            f'font-size="11">{h}</text>'
        )

        # Planets
        if hd["planets"]:
            n = len(hd["planets"])
            for pi, (pname, pdeg, retro) in enumerate(hd["planets"]):
                offset = (pi - (n - 1) / 2) * 8
                pa = ca + offset
                px, py = _polar(R_INNER * 0.75, pa)
                pglyph = PLANET_GLYPHS_THAI.get(pname, "?")
                pcolor = PLANET_COLORS.get(pname, "#e0e0e0")
                retro_mark = " ℞" if retro else ""
                svg.append(
                    f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" '
                    f'dominant-baseline="central" fill="{pcolor}" '
                    f'font-size="14" font-weight="bold">'
                    f'{pglyph}{retro_mark}</text>'
                )

    # ── ASC marker ─────────────────────────────────────────────
    asc_angle = _house_angle(1)
    asc_x, asc_y = _polar(R_OUTER + 8, asc_angle)
    svg.append(
        f'<text x="{asc_x:.1f}" y="{asc_y:.1f}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#d4af37" '
        f'font-size="13" font-weight="bold">ASC</text>'
    )

    # ── centre circle (temple motif) ───────────────────────────
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_CENTRE}" '
        f'fill="#241e30" stroke="#d4af37" stroke-width="2"/>'
    )
    # Inner decorative circle
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_CENTRE - 6}" '
        f'fill="none" stroke="#b8962e" stroke-width="0.8"/>'
    )

    # Centre text
    svg.append(
        f'<text x="{CX}" y="{CY - 40}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#d4af37" '
        f'font-size="14" font-weight="bold">ดวงชาตา</text>'
    )
    be_year = _to_be_year(chart.year)
    svg.append(
        f'<text x="{CX}" y="{CY - 22}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#c9a84c" '
        f'font-size="9">{chart.day:02d}/{chart.month:02d}/{be_year} '
        f'(พ.ศ.)</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY - 8}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#9a8a5a" '
        f'font-size="9">{chart.hour:02d}:{chart.minute:02d} '
        f'UTC{chart.timezone:+.1f}</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY + 8}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#9a8a5a" '
        f'font-size="8">{chart.location_name}</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY + 22}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#7a6a50" '
        f'font-size="8">Ayanamsa: {chart.ayanamsa:.2f}°</text>'
    )
    # Nakshatra callout in centre
    nak = chart.nakshatra
    if nak:
        svg.append(
            f'<text x="{CX}" y="{CY + 36}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#c9a84c" '
            f'font-size="8">☽ {nak.get("thai", "")} '
            f'{nak.get("chinese", "")}</text>'
        )
    # Lagna label
    svg.append(
        f'<text x="{CX}" y="{CY + 50}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#b8962e" '
        f'font-size="8">ลัคนา: {chart.asc_rashi}</text>'
    )

    svg.append("</svg></div>")
    return "\n".join(svg)


# ============================================================
# Thai Numerology 9-Box Grid (ตาราง 9 ช่อง)
# ============================================================

# Navagraha number → planet correspondence (Thai Numerology)
THAI_NUMEROLOGY_PLANETS = {
    1: ("พระอาทิตย์ (太陽)", "☀️", "#FF8C00"),
    2: ("พระจันทร์ (月亮)", "🌙", "#C0C0C0"),
    3: ("พระอังคาร (火星)", "🔴", "#DC143C"),
    4: ("พระพุธ (水星)", "💚", "#4169E1"),
    5: ("พระพฤหัสบดี (木星)", "💛", "#FFD700"),
    6: ("พระศุกร์ (金星)", "💗", "#FF69B4"),
    7: ("พระเสาร์ (土星)", "🟤", "#8B4513"),
    8: ("ราหู (羅睺)", "🟣", "#800080"),
    9: ("เกตุ (計都)", "🔵", "#4B0082"),
}

# Grid layout: 3 rows × 3 cols, each cell holds the number shown
# [1, 4, 7]
# [2, 5, 8]
# [3, 6, 9]
_NINE_GRID_LAYOUT = [
    [1, 4, 7],
    [2, 5, 8],
    [3, 6, 9],
]

# Line definitions: name → list of numbers in that line
_NINE_GRID_LINES = {
    "147": [1, 4, 7],
    "258": [2, 5, 8],
    "369": [3, 6, 9],
    "123": [1, 2, 3],
    "456": [4, 5, 6],
    "789": [7, 8, 9],
    "159": [1, 5, 9],
    "357": [3, 5, 7],
}

# Line meaning descriptions (Thai + Chinese)
_LINE_MEANINGS = {
    "147": {
        "name_th": "เส้นพลังงาน (行動力線)",
        "name_zh": "行動力線",
        "desc": "意志力強、物質成就、行動果斷。此線完整代表您具備堅定的意志和實現目標的能力。",
        "desc_th": "ความแข็งแกร่งของความตั้งใจ ความสำเร็จทางวัตถุ ความเด็ดขาด",
        "remedy": "配戴橙色或棕色寶石，增強太陽與土星的力量。",
    },
    "258": {
        "name_th": "เส้นความสมดุลทางอารมณ์ (情感平衡線)",
        "name_zh": "情感平衡線",
        "desc": "情感豐富、同理心強、人際關係和諧。此線完整代表您在情感上非常均衡。",
        "desc_th": "อารมณ์อ่อนไหว ความเห็นอกเห็นใจ ความสัมพันธ์ที่ดี",
        "remedy": "配戴白色或銀色寶石，加強月亮能量；以薰衣草精油平衡情緒。",
    },
    "369": {
        "name_th": "เส้นสติปัญญา (思維線)",
        "name_zh": "思維線",
        "desc": "思維敏捷、創意十足、學習能力強。此線完整代表您擁有卓越的智力與創造力。",
        "desc_th": "ความฉลาด ความคิดสร้างสรรค์ ทักษะการเรียนรู้",
        "remedy": "配戴紅色或珊瑚色寶石，增強火星與計都的創意能量。",
    },
    "123": {
        "name_th": "เส้นเป้าหมาย (目標線)",
        "name_zh": "目標線",
        "desc": "目標明確、行動力強、勇於突破。此線完整代表您具備強烈的成就動機。",
        "desc_th": "เป้าหมายชัดเจน พลังงานสูง กล้าที่จะก้าวข้ามขีดจำกัด",
        "remedy": "選擇以1、2、3結尾的車牌，或在名字中加入對應數字的筆畫。",
    },
    "456": {
        "name_th": "เส้นการทำงานและความสามัคคี (工作和諧線)",
        "name_zh": "工作和諧線",
        "desc": "勤奮努力、工作穩定、人際和諧。此線完整代表您在職場中表現出色。",
        "desc_th": "ความขยันหมั่นเพียร ความมั่นคง ความสามัคคี",
        "remedy": "配戴藍色或深藍色寶石，增強水星與金星的職場能量。",
    },
    "789": {
        "name_th": "เส้นวิญญาณ (靈性線)",
        "name_zh": "靈性線",
        "desc": "靈性覺知高、智慧深厚、直覺敏銳。此線完整代表您具備深刻的靈性洞察力。",
        "desc_th": "จิตวิญญาณที่สูง ปัญญา สัญชาตญาณที่เฉียบแหลม",
        "remedy": "冥想與靜心修行，配戴紫色或靛藍色水晶，強化土星、羅睺、計都能量。",
    },
    "159": {
        "name_th": "เส้นผู้นำ (領導力線)",
        "name_zh": "領導力線",
        "desc": "天生領袖氣質、決策能力強、有遠見。此線完整代表您具備天賦的領導才能。",
        "desc_th": "ความเป็นผู้นำโดยธรรมชาติ ความสามารถในการตัดสินใจ วิสัยทัศน์",
        "remedy": "選擇以5結尾的手機號碼，配戴黃色寶石（黃玉或黃水晶）。",
    },
    "357": {
        "name_th": "เส้นสมาธิ (專注力線)",
        "name_zh": "專注力線",
        "desc": "專注力強、毅力持久、不輕易放棄。此線完整代表您具備超強的耐力與執行力。",
        "desc_th": "สมาธิสูง ความอดทน ไม่ยอมแพ้ง่าย",
        "remedy": "冥想訓練，配戴紅色或橙色寶石，增強火星與土星的持久力。",
    },
}

# Missing number remedies
_MISSING_NUMBER_REMEDIES = {
    1: "缺少太陽能量：可選擇以1結尾的車牌或電話號碼，多穿橙色衣物，配戴紅寶石或石榴石。",
    2: "缺少月亮能量：多親近水域，配戴珍珠或月光石，以白色或銀色為幸運色。",
    3: "缺少火星能量：多運動，配戴珊瑚或紅色寶石，增強行動力與決斷力。",
    4: "缺少水星能量：多閱讀與溝通，配戴祖母綠或綠色寶石，增強學習與表達能力。",
    5: "缺少木星能量：多行善積德，配戴黃色蛋白石或黃玉，增強幸運與擴展能量。",
    6: "缺少金星能量：注重美感與人際關係，配戴鑽石或白水晶，增強魅力與財運。",
    7: "缺少土星能量：培養耐心與紀律，配戴藍寶石或紫水晶，增強持久力與責任感。",
    8: "缺少羅睺能量：注意業力課題，配戴赫松石或灰色寶石，轉化羅睺帶來的考驗。",
    9: "缺少計都能量：深化靈性修行，配戴貓眼石或深色寶石，融化過去世業障。",
}


def _digit_reduce(n):
    """Reduce integer to single digit 1–9 (no master numbers in Thai system).

    Args:
        n (int): non-negative integer to reduce.

    Returns:
        int: value in range 1–9.  Returns 9 for multiples of 9, and 1 for 0.
    """
    if n <= 0:
        return 1
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def calculate_thai_nine_grid(day, month, year):
    """計算泰國 Numerology 9宮格數據 (Thai Numerology 9-Box Grid)

    Args:
        day (int): 出生日 (1–31)
        month (int): 出生月 (1–12)
        year (int): 出生年 (e.g. 1990)

    Returns:
        dict with keys:
            - counts (dict[int, int]): digit 1–9 occurrence counts
            - birth_number (int): 出生日數字（Birth Number, 1–9）
            - life_path (int): 生命靈數（Life Path Number, 1–9）
            - complete_lines (list[str]): list of complete line keys, e.g. ["147", "159"]
            - strongest (list[int]): digit(s) with highest count (>0)
            - missing (list[int]): digits with count 0
            - day, month, year (int): original inputs
    """
    # Collect all digits from DD/MM/YYYY, ignoring zeros
    date_str = f"{day:02d}{month:02d}{year:04d}"
    raw_digits = [int(c) for c in date_str if c != "0"]

    # Count raw occurrences of digits 1–9
    counts = {i: 0 for i in range(1, 10)}
    for d in raw_digits:
        if 1 <= d <= 9:
            counts[d] += 1

    # Birth Number: reduce birth day to single digit 1–9
    birth_number = _digit_reduce(day if day > 0 else 1)

    # Life Path Number: sum all non-zero digits then reduce
    total = sum(raw_digits)
    life_path = _digit_reduce(total) if total > 0 else 1

    # Add derived numbers to the grid counts
    counts[birth_number] += 1
    counts[life_path] += 1

    # If birth_number == life_path, it was counted twice — that is intentional
    # (both are independent derived numbers)

    # Detect complete lines (all 3 numbers in the line have count > 0)
    complete_lines = [
        line_name
        for line_name, nums in _NINE_GRID_LINES.items()
        if all(counts[n] > 0 for n in nums)
    ]

    # Strongest number(s)
    max_count = max(counts.values())
    strongest = [n for n, c in counts.items() if c == max_count and c > 0]

    # Missing numbers
    missing = [n for n, c in counts.items() if c == 0]

    return {
        "counts": counts,
        "birth_number": birth_number,
        "life_path": life_path,
        "complete_lines": complete_lines,
        "strongest": strongest,
        "missing": missing,
        "day": day,
        "month": month,
        "year": year,
    }


def render_nine_grid(result):
    """渲染泰國 Numerology 9宮格圖譜 (Thai Numerology 9-Box Grid UI)

    Args:
        result (dict): output from calculate_thai_nine_grid()
    """
    counts = result["counts"]
    complete_lines = result["complete_lines"]
    strongest = result["strongest"]
    missing = result["missing"]
    birth_number = result["birth_number"]
    life_path = result["life_path"]

    st.subheader("🔢 ตาราง 9 ช่อง — Thai Numerology 9宮格圖譜")

    # ── Summary row ──────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            f"**เลขวันเกิด (Birth Number / 出生日數):** "
            f"**{birth_number}** &nbsp; "
            f"{THAI_NUMEROLOGY_PLANETS[birth_number][1]} "
            f"{THAI_NUMEROLOGY_PLANETS[birth_number][0]}"
        )
    with col_b:
        st.markdown(
            f"**เลขชีวิต (Life Path / 生命靈數):** "
            f"**{life_path}** &nbsp; "
            f"{THAI_NUMEROLOGY_PLANETS[life_path][1]} "
            f"{THAI_NUMEROLOGY_PLANETS[life_path][0]}"
        )

    st.markdown("")

    # ── 3×3 grid ─────────────────────────────────────────────
    # Determine which cells are part of a complete line for highlighting
    highlighted = set()
    for line_name in complete_lines:
        for n in _NINE_GRID_LINES[line_name]:
            highlighted.add(n)

    cell_base = (
        "display:flex; flex-direction:column; align-items:center; "
        "justify-content:center; border:2px solid #555; border-radius:8px; "
        "padding:10px 6px; min-width:90px; min-height:90px; "
        "font-size:15px; text-align:center;"
    )

    grid_html = (
        '<div style="display:grid; grid-template-columns:repeat(3,1fr); '
        'gap:8px; max-width:360px; margin:0 auto 16px auto;">'
    )

    for row in _NINE_GRID_LAYOUT:
        for num in row:
            cnt = counts[num]
            planet_name, planet_emoji, planet_color = THAI_NUMEROLOGY_PLANETS[num]
            is_highlighted = num in highlighted
            is_missing = cnt == 0

            if is_missing:
                bg = "#1a1a2e"
                text_color = "#555"
                border_color = "#333"
                count_str = "—"
            elif is_highlighted:
                bg = "#1e3a1e"
                text_color = planet_color
                border_color = planet_color
                count_str = f"×{cnt}"
            else:
                bg = "#1a1a1a"
                text_color = planet_color
                border_color = "#555"
                count_str = f"×{cnt}"

            cell_style = (
                f"{cell_base} background:{bg}; "
                f"border-color:{border_color}; color:{text_color};"
            )

            num_display = (
                f'<span style="font-size:22px; font-weight:bold;">{num}</span>'
            )
            count_display = (
                f'<span style="font-size:13px; color:{text_color};">'
                f"{count_str}</span>"
            )
            emoji_display = (
                f'<span style="font-size:16px;">{planet_emoji}</span>'
            )

            grid_html += (
                f'<div style="{cell_style}">'
                f"{num_display}{count_display}{emoji_display}"
                f"</div>"
            )

    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

    # ── Planet legend ─────────────────────────────────────────
    with st.expander("🪐 行星數字對應 (Navagraha Correspondence)", expanded=False):
        legend_cols = st.columns(3)
        for i, (num, (pname, pemoji, pcolor)) in enumerate(
            THAI_NUMEROLOGY_PLANETS.items()
        ):
            with legend_cols[i % 3]:
                st.markdown(
                    f'<span style="color:{pcolor}; font-weight:bold;">'
                    f"{pemoji} {num} = {pname}</span>",
                    unsafe_allow_html=True,
                )

    # ── Complete lines ────────────────────────────────────────
    st.markdown("### 🌟 完整線條 (เส้นที่สมบูรณ์ — Complete Lines)")
    if complete_lines:
        for line_name in complete_lines:
            meaning = _LINE_MEANINGS[line_name]
            nums = _NINE_GRID_LINES[line_name]
            emojis = "→".join(
                f"{THAI_NUMEROLOGY_PLANETS[n][1]}{n}" for n in nums
            )
            st.markdown(
                f"**{emojis} &nbsp; {line_name} {meaning['name_th']}**  \n"
                f"{meaning['desc']}  \n"
                f"*{meaning['desc_th']}*  \n"
                f"💊 後天化解：{meaning['remedy']}"
            )
            st.markdown("---")
    else:
        st.info("目前沒有完整的長線。透過補數字（改名、選車牌號碼、佩戴對應護符）可逐步形成能量線條。")

    # ── Strongest numbers ─────────────────────────────────────
    st.markdown("### 💪 最強數字 (ตัวเลขที่แข็งแกร่งที่สุด — Strongest Numbers)")
    if strongest:
        max_cnt = counts[strongest[0]]
        for n in strongest:
            pname, pemoji, pcolor = THAI_NUMEROLOGY_PLANETS[n]
            st.markdown(
                f'<span style="color:{pcolor}; font-size:16px; font-weight:bold;">'
                f"{pemoji} {n} — {pname}</span>  \n"
                f"出現 **{max_cnt}** 次。您的主要能量中心。",
                unsafe_allow_html=True,
            )
    else:
        st.info("數字分布均勻，無特別突出的主導數字。")

    # ── Missing numbers ───────────────────────────────────────
    st.markdown("### 🎯 缺失數字 (ตัวเลขที่ขาดหาย — Missing Numbers / 人生課題)")
    if missing:
        for n in missing:
            pname, pemoji, pcolor = THAI_NUMEROLOGY_PLANETS[n]
            remedy = _MISSING_NUMBER_REMEDIES[n]
            st.markdown(
                f'<span style="color:{pcolor}; font-size:16px; font-weight:bold;">'
                f"{pemoji} {n} — {pname}</span>  \n"
                f"此生課題：{remedy}",
                unsafe_allow_html=True,
            )
    else:
        st.success("🎉 您的生日包含所有數字 1–9，能量非常完整！")

    # ── Personality summary ───────────────────────────────────
    _render_numerology_summary(result)

    # ── Future expansion placeholder ──────────────────────────
    # TODO: 姓名 Numerology (Name Numerology)
    # 未來可加入以泰文/中文姓名字母對應數字的計算，
    # 進一步補強缺失數字，或強化現有優勢數字。


def _render_numerology_summary(result):
    """渲染數字學性格總結 (Personality summary based on Life Path and Birth Number)"""
    birth_number = result["birth_number"]
    life_path = result["life_path"]

    # Template personality summaries (to be refined in future)
    _personality = {
        1: "您是天生的先驅者與領導者，獨立自主、意志堅定。您喜歡開創新局，不畏挑戰。",
        2: "您具備敏感細膩的情感與強大的同理心，擅長協調與合作，是優秀的和平使者。",
        3: "您充滿創意與活力，表達能力強，天生樂觀，能為周圍帶來歡樂與靈感。",
        4: "您腳踏實地、勤奮努力，注重細節與秩序，是建設與穩定的力量。",
        5: "您愛好自由、適應力強，充滿好奇心，擅長交際，渴望多樣化的生命體驗。",
        6: "您富有責任感與愛心，重視家庭與和諧，是照顧者與守護者的典型。",
        7: "您深思熟慮、富有哲思，喜歡獨處與研究，具有深刻的靈性與分析能力。",
        8: "您具備強大的執行力與野心，擅長掌控資源，追求物質與精神的雙重成就。",
        9: "您慈悲博愛、視野寬廣，有強烈的使命感，渴望為世界帶來正面改變。",
    }

    st.markdown("### 🌸 性格總結 (สรุปบุคลิกภาพ — Personality Summary)")
    pname_bn, pemoji_bn, pcolor_bn = THAI_NUMEROLOGY_PLANETS[birth_number]
    pname_lp, pemoji_lp, pcolor_lp = THAI_NUMEROLOGY_PLANETS[life_path]

    st.markdown(
        f"**{pemoji_bn} 出生日數 {birth_number} — {pname_bn}**  \n"
        f"{_personality[birth_number]}"
    )
    if life_path != birth_number:
        st.markdown(
            f"**{pemoji_lp} 生命靈數 {life_path} — {pname_lp}**  \n"
            f"{_personality[life_path]}"
        )


# ============================================================
# 九宮占 — Nine Palace Divination (ดวง 9 ทิศ)
# ============================================================

# Planet name → (palace number, life domain zh, life domain th, emoji)
_PALACE_PLANETS = {
    "พระอาทิตย์ (太陽)": (1, "權勢 — 地位與健康", "สถานะและสุขภาพ", "☀️"),
    "พระจันทร์ (月亮)": (2, "情感 — 心靈與家庭", "อารมณ์และครอบครัว", "🌙"),
    "พระอังคาร (火星)": (3, "行動 — 勇氣與競爭", "พลังงานและการแข่งขัน", "🔴"),
    "พระพุธ (水星)": (4, "智慧 — 溝通與學習", "สติปัญญาและการสื่อสาร", "💚"),
    "พระพฤหัสบดี (木星)": (5, "福德 — 智慧與幸運", "โชคลาภและปัญญา", "💛"),
    "พระศุกร์ (金星)": (6, "愛情 — 姻緣與財富", "ความรักและทรัพย์สิน", "💗"),
    "พระเสาร์ (土星)": (7, "事業 — 紀律與長壽", "การงานและอายุยืน", "🟤"),
    "ราหู (羅睺)": (8, "變化 — 野心與挑戰", "การเปลี่ยนแปลงและความทะเยอทะยาน", "🟣"),
    "เกตุ (計都)": (9, "靈性 — 解脫與前世", "จิตวิญญาณและกรรมเก่า", "🔵"),
}

# 3×3 palace grid layout (row × col), each cell is a palace number
_PALACE_GRID = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6],
]

# Palace number → (direction zh, direction th, element)
# Keys 1–9 correspond to the Lo Shu magic-square numbers.
# Values: (Chinese direction with trigram, Thai direction, Five-Element)
_PALACE_DIRECTIONS = {
    1: ("北 (坎)", "ทิศเหนือ", "水"),
    2: ("西南 (坤)", "ทิศตะวันตกเฉียงใต้", "土"),
    3: ("東 (震)", "ทิศตะวันออก", "木"),
    4: ("東南 (巽)", "ทิศตะวันออกเฉียงใต้", "木"),
    5: ("中宮", "ศูนย์กลาง", "土"),
    6: ("西北 (乾)", "ทิศตะวันตกเฉียงเหนือ", "金"),
    7: ("西 (兌)", "ทิศตะวันตก", "金"),
    8: ("東北 (艮)", "ทิศตะวันออกเฉียงเหนือ", "土"),
    9: ("南 (離)", "ทิศใต้", "火"),
}

# Planetary dignities: planet name → {"own": [sign_indices], "exalted": [sign_indices],
#                                      "debilitated": [sign_indices]}
# Sign indices: 0=Aries,1=Taurus,...,11=Pisces
_DIGNITIES = {
    "พระอาทิตย์ (太陽)": {"own": [4], "exalted": [0], "debilitated": [6]},
    "พระจันทร์ (月亮)": {"own": [3], "exalted": [1], "debilitated": [7]},
    "พระอังคาร (火星)": {"own": [0, 7], "exalted": [9], "debilitated": [3]},
    "พระพุธ (水星)": {"own": [2, 5], "exalted": [5], "debilitated": [11]},
    "พระพฤหัสบดี (木星)": {"own": [8, 11], "exalted": [3], "debilitated": [9]},
    "พระศุกร์ (金星)": {"own": [1, 6], "exalted": [11], "debilitated": [5]},
    "พระเสาร์ (土星)": {"own": [9, 10], "exalted": [6], "debilitated": [0]},
    "ราหู (羅睺)": {"own": [10], "exalted": [1, 2], "debilitated": [7, 8]},
    "เกตุ (計都)": {"own": [7], "exalted": [7, 8], "debilitated": [1, 2]},
}

# Detailed palace readings keyed by (palace_number, status)
# status: "exalted", "own", "neutral", "debilitated"
_PALACE_READINGS = {
    (1, "exalted"): "權勢極旺，領導力超群，事業順遂，貴人提攜，社會地位崇高。",
    (1, "own"): "權勢穩固，自信充足，健康良好，受人尊重。",
    (1, "neutral"): "地位平穩，需更努力以提升影響力，健康尚可。",
    (1, "debilitated"): "權勢受損，自信不足，注意健康問題，宜低調行事。",
    (2, "exalted"): "情感豐盈，內心安寧，家庭幸福和睦，母親福澤深厚。",
    (2, "own"): "心靈穩定，感受力強，家庭關係和諧。",
    (2, "neutral"): "情感起伏不定，需注意調適心緒，家庭關係尚可。",
    (2, "debilitated"): "情緒波動大，易焦慮不安，家庭或感情恐有波折。",
    (3, "exalted"): "行動力極強，勇敢果斷，競爭中必勝，事業突飛猛進。",
    (3, "own"): "精力充沛，果斷有力，面對挑戰不畏縮。",
    (3, "neutral"): "行動力一般，需加強決斷力與執行力。",
    (3, "debilitated"): "行動受阻，容易猶豫，注意與人衝突，慎防意外。",
    (4, "exalted"): "智慧超群，口才出眾，學業與考試大吉，貿易獲利。",
    (4, "own"): "思維敏捷，溝通順暢，學習能力強。",
    (4, "neutral"): "智慧平平，溝通時需多加留意，學業需勤奮。",
    (4, "debilitated"): "思維混亂，溝通不暢，注意合約文書問題。",
    (5, "exalted"): "福德最旺，智慧與幸運兼備，子女賢孝，師長庇護。",
    (5, "own"): "福德深厚，心懷善念，好運連連。",
    (5, "neutral"): "福德尚可，宜多行善積德以增福報。",
    (5, "debilitated"): "福德不足，諸事不順，宜修心養性，廣結善緣。",
    (6, "exalted"): "姻緣極佳，感情甜蜜，財運亨通，生活舒適奢華。",
    (6, "own"): "感情穩定，審美出眾，財運不錯。",
    (6, "neutral"): "感情平淡，財運一般，需多經營人際關係。",
    (6, "debilitated"): "感情波折，破財之虞，注意奢侈浪費。",
    (7, "exalted"): "事業大成，紀律嚴明，持久耐勞，長壽安康。",
    (7, "own"): "事業穩健，責任心強，有恆心毅力。",
    (7, "neutral"): "事業平穩，需更多耐心與紀律。",
    (7, "debilitated"): "事業受阻，壓力沉重，注意健康與過勞問題。",
    (8, "exalted"): "變化中逢吉，野心得以實現，海外發展大利。",
    (8, "own"): "善於應變，抓住機遇，適合跨領域發展。",
    (8, "neutral"): "變化不定，需謹慎應對新局面。",
    (8, "debilitated"): "變動頻繁，幻想多於實際，慎防欺詐與迷惑。",
    (9, "exalted"): "靈性覺悟高，直覺敏銳，修行有成，前世善緣深。",
    (9, "own"): "靈性穩定，善於內觀，適合靈修與研究。",
    (9, "neutral"): "靈性尚淺，宜多靜心冥想以提升覺知。",
    (9, "debilitated"): "靈性迷茫，執念較重，需放下過去，向前邁進。",
}


def _get_planet_dignity(planet_name, sign_index):
    """Determine a planet's dignity status from its zodiac sign index.

    Returns one of: "exalted", "own", "debilitated", "neutral".
    """
    d = _DIGNITIES.get(planet_name)
    if d is None:
        return "neutral"
    if sign_index in d["exalted"]:
        return "exalted"
    if sign_index in d["own"]:
        return "own"
    if sign_index in d["debilitated"]:
        return "debilitated"
    return "neutral"


_DIGNITY_LABELS = {
    "exalted": ("入廟 (สูง)", "🔥", "大吉"),
    "own": ("居旺 (เรือน)", "✨", "吉"),
    "neutral": ("平和 (ปกติ)", "☁️", "平"),
    "debilitated": ("落陷 (ต่ำ)", "💧", "凶"),
}


def calculate_nine_palace_divination(chart):
    """Calculate Nine Palace Divination (九宮占) from a ThaiChart.

    Maps each of the nine Navagraha planets to its corresponding palace,
    evaluates dignity based on zodiac sign, and returns palace data with
    divination readings.

    Args:
        chart (ThaiChart): computed Thai astrology chart.

    Returns:
        dict: keys include "palaces" (list of 9 palace dicts) and
              "ascendant_rashi" (str).
    """
    # Build planet lookup: name → ThaiPlanet
    planet_map = {p.name: p for p in chart.planets}

    palaces = []
    for palace_num in range(1, 10):
        # Find the planet assigned to this palace
        planet_name = None
        palace_meta = None
        for pname, meta in _PALACE_PLANETS.items():
            if meta[0] == palace_num:
                planet_name = pname
                palace_meta = meta
                break

        planet = planet_map.get(planet_name)
        # _sign_index is defined earlier in this module (line ~125).
        # Fallback sign_idx=0 is only reached if planet_map lookup fails,
        # which should not happen since compute_thai_chart always produces
        # all nine Navagraha planets.
        sign_idx = _sign_index(planet.longitude) if planet else 0
        dignity = _get_planet_dignity(planet_name, sign_idx) if planet else "neutral"
        label, icon, fortune = _DIGNITY_LABELS[dignity]
        direction_zh, direction_th, element = _PALACE_DIRECTIONS[palace_num]
        reading = _PALACE_READINGS.get((palace_num, dignity), "")

        palaces.append({
            "number": palace_num,
            "planet_name": planet_name,
            "emoji": palace_meta[3] if palace_meta else "",
            "domain_zh": palace_meta[1] if palace_meta else "",
            "domain_th": palace_meta[2] if palace_meta else "",
            "rashi": planet.rashi if planet else "",
            "rashi_chinese": planet.rashi_chinese if planet else "",
            "rashi_glyph": planet.rashi_glyph if planet else "",
            "sign_degree": planet.sign_degree if planet else 0.0,
            "retrograde": planet.retrograde if planet else False,
            "dignity": dignity,
            "dignity_label": label,
            "dignity_icon": icon,
            "fortune": fortune,
            "direction_zh": direction_zh,
            "direction_th": direction_th,
            "element": element,
            "reading": reading,
        })

    return {
        "palaces": palaces,
        "ascendant_rashi": chart.asc_rashi,
    }


def render_nine_palace_divination(result):
    """Render Nine Palace Divination (九宮占) using Streamlit.

    Displays a 3×3 grid of palaces with planet positions, dignity,
    fortune indicators, and divination readings.

    Args:
        result (dict): output of :func:`calculate_nine_palace_divination`.
    """
    st.markdown("### 🏯 九宮占 (ดวง 9 ทิศ — Nine Palace Divination)")
    st.markdown(
        "九宮占以洛書九宮為基礎，將九曜分佈於九方位宮位，"
        "依行星廟旺落陷判斷各宮位的吉凶。"
    )

    palace_map = {p["number"]: p for p in result["palaces"]}

    # Render 3×3 grid
    for row in _PALACE_GRID:
        cols = st.columns(3)
        for ci, palace_num in enumerate(row):
            p = palace_map[palace_num]
            fortune_color = {
                "大吉": "#D4AF37", "吉": "#4CAF50",
                "平": "#888888", "凶": "#E53935",
            }.get(p["fortune"], "#888888")
            retro = " (逆行 ℞)" if p["retrograde"] else ""
            with cols[ci]:
                st.markdown(
                    f"<div style='border:2px solid {fortune_color}; "
                    f"border-radius:10px; padding:10px; text-align:center; "
                    f"min-height:180px; background:rgba(0,0,0,0.02);'>"
                    f"<div style='font-size:0.8em; color:#666;'>"
                    f"{p['direction_zh']} · {p['element']}</div>"
                    f"<div style='font-size:1.3em;'>{p['emoji']} "
                    f"<b>第{p['number']}宮</b></div>"
                    f"<div style='font-size:0.9em;'>{p['domain_zh']}</div>"
                    f"<div style='margin:4px 0; font-size:0.85em;'>"
                    f"{p['rashi_glyph']} {p['rashi_chinese']} "
                    f"{p['sign_degree']:.1f}°{retro}</div>"
                    f"<div style='font-size:1.1em; color:{fortune_color}; "
                    f"font-weight:bold;'>"
                    f"{p['dignity_icon']} {p['fortune']} · {p['dignity_label']}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # Detailed readings
    st.markdown("---")
    st.markdown("### 📖 九宮詳解 (คำอธิบาย 9 ทิศ)")
    for palace_num in range(1, 10):
        p = palace_map[palace_num]
        fortune_color = {
            "大吉": "#D4AF37", "吉": "#4CAF50",
            "平": "#888888", "凶": "#E53935",
        }.get(p["fortune"], "#888888")
        retro = " ℞" if p["retrograde"] else ""
        st.markdown(
            f"**{p['emoji']} 第{p['number']}宮 — "
            f"{p['domain_zh']}** ({p['direction_zh']})  \n"
            f"行星：{p['planet_name']}　"
            f"星座：{p['rashi_glyph']} {p['rashi_chinese']} "
            f"{p['sign_degree']:.1f}°{retro}　"
            f"<span style='color:{fortune_color}; font-weight:bold;'>"
            f"{p['dignity_icon']} {p['fortune']} · {p['dignity_label']}</span>  \n"
            f"{p['reading']}",
            unsafe_allow_html=True,
        )
