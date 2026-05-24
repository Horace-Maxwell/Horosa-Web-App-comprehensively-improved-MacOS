"""
astro/babylonian.py — 古巴比倫占星 (Babylonian / Chaldean Astrology)

古巴比倫占星是所有西洋占星體系的直接源頭，起源於美索不達米亞文明。
核心文獻與天文記錄：

1. MUL.APIN 星表（約公元前 1000 年）
   美索不達米亞最重要的天文目錄泥板，記錄了 66 顆恆星/星座的升沒時間，
   以及 12 宮黃道的劃分方式。所有宮位名稱均使用 Akkadian（阿卡德語）古名。

2. Enūma Anu Enlil 預兆集（約 70 片泥板，公元前 2000–500 年）
   美索不達米亞最龐大的天文預兆集，將天體現象（日月食、行星運行、氣象）
   與國家命運、農業豐歉、戰爭勝敗等人間吉凶對應。
   七大行星神：Shamash（太陽）、Sin（月）、Nabu（水星）、
   Ishtar（金星）、Nergal（火星）、Marduk（木星）、Ninurta（土星）。

3. K.8538 尼尼微星盤（公元前 650 年左右）
   出土於亞述帝國尼尼微圖書館的圓形泥板星圖，將天球平面投影為 8 個
   楔形區間（sector），是已知最早的平面星圖之一。本模組的 SVG 視覺化
   即以此泥板為原型，採用復古陶土紋理與楔形文字風格。

本模組 100% 模仿 astro/western/hellenistic.py 的架構、類別設計、函數命名、
常量定義方式、註解風格、i18n 呼叫方式與 chart dict 格式來實現。
"""
import math
import streamlit as st
import swisseph as swe
from dataclasses import dataclass, field

from astro.i18n import t

# ============================================================
# 12 宮黃道 — MUL.APIN 標準 Akkadian 古名
# ============================================================
BABYLONIAN_ZODIAC_SIGNS = [
    ("0", "LU.HUN.GA", "雇農 / 雇工", "The Hired Man", "Aries"),
    ("1", "GU4.AN.NA", "天牛", "The Bull of Heaven", "Taurus"),
    ("2", "MAŠ.TAB.BA.GAL.GAL", "大雙子", "The Great Twins", "Gemini"),
    ("3", "ALLA", "螃蟹", "The Crab", "Cancer"),
    ("4", "UR.GU.LA", "獅子", "The Lion", "Leo"),
    ("5", "AB.SIN", "穗 / 犁溝", "The Furrow", "Virgo"),
    ("6", "ZI.BA.AN.NA", "天秤", "The Scales", "Libra"),
    ("7", "GIR.TAB", "蠍子", "The Scorpion", "Scorpio"),
    ("8", "PA.BIL.SAG", "射手 / 巴比倫射手", "The Archer / Pabilsag", "Sagittarius"),
    ("9", "SUḪUR.MAŠ", "山羊魚", "The Goat-Fish", "Capricorn"),
    ("10", "GU", "大者 / 水瓶", "The Great One", "Aquarius"),
    ("11", "ZIB.ME", "魚尾 / 雙魚", "The Tails / Two Fish", "Pisces"),
]

# Western-equivalent sign names (for cross-referencing)
ZODIAC_SIGNS = [s[4] for s in BABYLONIAN_ZODIAC_SIGNS]
SIGN_CN = {s[4]: s[2] for s in BABYLONIAN_ZODIAC_SIGNS}
AKKADIAN_NAME = {s[4]: s[1] for s in BABYLONIAN_ZODIAC_SIGNS}
SIGN_EN = {s[4]: s[3] for s in BABYLONIAN_ZODIAC_SIGNS}

# ============================================================
# 行星神對應 — Enūma Anu Enlil 標準
# ============================================================
BABYLONIAN_PLANET_GODS = {
    "Sun": "Shamash (太陽神)",
    "Moon": "Sin (月神)",
    "Mercury": "Nabu (智慧神)",
    "Venus": "Ishtar (愛與戰爭女神)",
    "Mars": "Nergal (戰爭與瘟疫神)",
    "Jupiter": "Marduk (主神)",
    "Saturn": "Ninurta (農業與戰爭神)",
}

GRAHA_CN = {
    "Sun": "太陽", "Moon": "月亮", "Mercury": "水星", "Venus": "金星",
    "Mars": "火星", "Jupiter": "木星", "Saturn": "土星",
}

# ============================================================
# Ayanamsa & Epoch
# ============================================================
BABYLONIAN_AYANAMSA_MODE = swe.SIDM_FAGAN_BRADLEY
# MUL.APIN observation era baseline (~746 BCE Feb 26, Nabonassar epoch).
# Retained for cross-referencing and future historical chart calculations.
BABYLONIAN_EPOCH_JD = 1721139.5

# ============================================================
# K.8538 Planisphere — 8 區間方位 / 顏色
# ============================================================
BABYLONIAN_DIRECTIONS = [
    "NE", "E", "SE", "S", "SW", "W", "NW", "N",
]

BABYLONIAN_COLORS = [
    "#c4a35a",  # NE — gold-ochre
    "#9b7d4d",  # E  — dark ochre
    "#7a6232",  # SE — clay brown
    "#5c4a2a",  # S  — deep earth
    "#8b6914",  # SW — amber
    "#a0845c",  # W  — sandstone
    "#b89e6e",  # NW — light clay
    "#d4b87a",  # N  — pale gold
]

BABYLONIAN_DIRECTION_CN = {
    "NE": "東北", "E": "東", "SE": "東南", "S": "南",
    "SW": "西南", "W": "西", "NW": "西北", "N": "北",
}

# ============================================================
# K.8538 Sector constellation data — connect-the-dots patterns
# Each entry: sector index → list of (name, Akkadian label,
#   list of (r_frac, angle_offset) points for dot-line pattern)
# Coordinates are relative: r_frac ∈ [0,1] within sector radial
# range, angle_offset in degrees from sector centre.
# ============================================================
BABYLONIAN_K8538_CONSTELLATIONS = {
    0: [("Pleiades", "MUL.MUL",
         [(0.35, -8), (0.38, -4), (0.40, 0), (0.37, 4), (0.42, 7)])],
    1: [("Bull of Heaven", "GU4.AN.NA",
         [(0.30, -10), (0.50, -6), (0.65, 0), (0.55, 8), (0.35, 12)])],
    2: [("True Shepherd", "SIPA.ZI.AN.NA",
         [(0.25, -5), (0.45, -2), (0.60, 3), (0.70, 8)])],
    3: [("Arrow", "KAK.SI.SÁ",
         [(0.30, 0), (0.45, 0), (0.60, 0), (0.75, 0)])],
    4: [("Great Twins", "MAŠ.TAB.BA",
         [(0.30, -8), (0.50, -6), (0.50, 6), (0.30, 8)])],
    5: [("Scorpion", "GIR.TAB",
         [(0.25, -5), (0.40, -3), (0.55, 0), (0.65, 5), (0.60, 10),
          (0.50, 12)])],
    6: [("Eagle", "TI8",
         [(0.35, -6), (0.50, 0), (0.35, 6), (0.55, -3), (0.55, 3)])],
    7: [("Field", "IKU",
         [(0.30, -8), (0.30, 8), (0.55, 8), (0.55, -8), (0.30, -8)])],
}

# ============================================================
# K.8538 sector Akkadian cuneiform-style labels
# ============================================================
BABYLONIAN_K8538_SECTOR_LABELS = [
    "𒀭𒌓",   # Sector 0 — Shamash / Sun glyph
    "𒀭𒂗",   # Sector 1 — Enlil reference
    "𒀭𒈾",   # Sector 2 — Nabu reference
    "𒀭𒌍",   # Sector 3 — generic star
    "𒀭𒊩𒌆", # Sector 4 — Ishtar reference
    "𒀭𒃲",   # Sector 5 — great/gal
    "𒀭𒀀",   # Sector 6 — Anu reference
    "𒀭𒀊",   # Sector 7 — field reference
]

# ============================================================
# Enūma Anu Enlil 預兆 (placeholder omens)
# ============================================================
BABYLONIAN_OMENS = {
    "Sun": {
        "strong": "Shamash 光明照耀，王權穩固，國泰民安。",
        "strong_en": "Shamash shines bright — the king's throne is firm, the land prospers.",
        "weak": "Shamash 黯淡，君主須防叛亂，穀物歉收。",
        "weak_en": "Shamash is dim — the ruler must beware rebellion; grain harvest fails.",
    },
    "Moon": {
        "strong": "Sin 月光皎潔，豐年有望，婦人生貴子。",
        "strong_en": "Sin's light is pure — a prosperous year; a noble child is born.",
        "weak": "Sin 見虧，河水泛濫之兆，牧畜有災。",
        "weak_en": "Sin wanes — floods threaten; livestock face calamity.",
    },
    "Mercury": {
        "strong": "Nabu 運行順暢，書吏與商旅有利。",
        "strong_en": "Nabu moves smoothly — scribes and merchants thrive.",
        "weak": "Nabu 逆行，文書有誤，使節延遲。",
        "weak_en": "Nabu retrogrades — documents err; envoys are delayed.",
    },
    "Venus": {
        "strong": "Ishtar 晨星明亮，戰爭得勝，婚姻吉慶。",
        "strong_en": "Ishtar as morning star shines — victory in war; marriages rejoice.",
        "weak": "Ishtar 隱沒，和平受阻，農事不利。",
        "weak_en": "Ishtar is hidden — peace is obstructed; agriculture suffers.",
    },
    "Mars": {
        "strong": "Nergal 高懸，軍隊出征有利。",
        "strong_en": "Nergal rides high — military expeditions are favoured.",
        "weak": "Nergal 低沉，瘟疫之兆，邊境不安。",
        "weak_en": "Nergal sinks low — pestilence looms; borders are restless.",
    },
    "Jupiter": {
        "strong": "Marduk 居廟，國王受神眷，正義伸張。",
        "strong_en": "Marduk dwells in his temple — the king is divinely favoured; justice prevails.",
        "weak": "Marduk 落陷，法令不彰，財庫虧損。",
        "weak_en": "Marduk is fallen — laws falter; the treasury is depleted.",
    },
    "Saturn": {
        "strong": "Ninurta 穩行，農作豐收，水利順暢。",
        "strong_en": "Ninurta moves steadily — abundant harvest; irrigation flows well.",
        "weak": "Ninurta 遲滯，築城失敗，饑荒之兆。",
        "weak_en": "Ninurta stalls — fortification fails; famine looms.",
    },
}

# ============================================================
# Dignity tables (same as Hellenistic, used for condition scoring)
# ============================================================
SIGN_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

DOMICILE = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
            "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10]}
EXALTATION = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5,
              "Jupiter": 3, "Venus": 11, "Saturn": 6}
DETRIMENT = {"Sun": [10], "Moon": [9], "Mars": [1, 6], "Mercury": [8, 11],
             "Jupiter": [2, 5], "Venus": [0, 7], "Saturn": [3, 4]}
FALL = {"Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11,
        "Jupiter": 9, "Venus": 5, "Saturn": 0}


# ============================================================
# Planet / zodiac glyph constants
# ============================================================
ZODIAC_GLYPHS = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓",
]

PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿",
    "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
}

PLANET_COLORS = {
    "Sun": "#b8860b", "Moon": "#556b7f", "Mercury": "#8b6914",
    "Venus": "#2e7d32", "Mars": "#b71c1c", "Jupiter": "#1565c0",
    "Saturn": "#4a4a4a",
}


# ============================================================
# Internal helpers
# ============================================================
def _sign_idx(lon):
    return int(lon / 30) % 12


def _sign_deg(lon):
    return lon % 30


def _normalize(deg):
    return deg % 360


def _find_house(lon, cusps):
    for i in range(12):
        c1 = cusps[i]
        c2 = cusps[(i + 1) % 12]
        if c2 < c1:
            if lon >= c1 or lon < c2:
                return i + 1
        elif c1 <= lon < c2:
            return i + 1
    return 1


def _jd_to_date(jd):
    y, m, d, h = swe.revjul(jd)
    return f"{y:04d}-{m:02d}-{int(d):02d}"


# ============================================================
# Dataclasses
# ============================================================
@dataclass
class BabylonianPlanetPosition:
    """Position of a single planet in sidereal longitude."""
    name: str
    god_name: str
    longitude: float
    sign_idx: int
    sign_akkadian: str
    sign_cn: str
    sign_en: str
    sign_western: str
    sign_degree: float
    house: int


@dataclass
class BabylonianOmen:
    """Enūma Anu Enlil style omen for a planet."""
    planet: str
    god_name: str
    condition: str   # "strong" or "weak"
    text: str
    text_en: str = ""


@dataclass
class BabylonianChart:
    """Complete Babylonian natal chart — matches hellenistic chart key structure."""
    ascendant: float
    midheaven: float
    is_day_chart: bool
    planet_longitudes: dict       # {name: sidereal_longitude}
    planet_houses: dict           # {name: house_number}
    house_cusps: list             # 12 sidereal cusps
    positions: list               # list[BabylonianPlanetPosition]
    planets: dict                 # {name: god_name}  (BABYLONIAN_PLANET_GODS)
    omens: list                   # list[BabylonianOmen]
    aspects: list = field(default_factory=list)
    ayanamsa: float = 0.0
    julian_day: float = 0.0
    planisphere_data: dict = field(default_factory=dict)   # K.8538 8-sector data


# ============================================================
# SWE planet ID mapping
# ============================================================
_PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
}


# ============================================================
# Aspect calculation
# ============================================================
_MAJOR_ASPECTS = [
    ("conjunction", 0, 8),
    ("opposition", 180, 8),
    ("trine", 120, 8),
    ("square", 90, 7),
    ("sextile", 60, 6),
]


def _compute_aspects(planet_longs):
    """Compute major aspects between planets."""
    aspects = []
    names = list(planet_longs.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]
            diff = abs(planet_longs[p1] - planet_longs[p2])
            if diff > 180:
                diff = 360 - diff
            for asp_name, asp_angle, orb in _MAJOR_ASPECTS:
                if abs(diff - asp_angle) <= orb:
                    aspects.append({
                        "planet1": p1,
                        "planet2": p2,
                        "aspect": asp_name,
                        "angle": round(diff, 2),
                        "orb": round(abs(diff - asp_angle), 2),
                    })
                    break
    return aspects


# ============================================================
# Omen determination
# ============================================================
def _determine_omen(planet, sign_idx):
    """Simple omen logic based on domicile/exaltation vs. detriment/fall.

    Returns
    -------
    tuple of (condition, text, text_en)
        condition : str — ``"strong"`` or ``"weak"``
        text : str — Chinese omen text
        text_en : str — English omen text
    """
    is_strong = (
        sign_idx in DOMICILE.get(planet, [])
        or EXALTATION.get(planet) == sign_idx
    )
    condition = "strong" if is_strong else "weak"
    omen_dict = BABYLONIAN_OMENS.get(planet, {})
    text = omen_dict.get(condition, "")
    text_en = omen_dict.get(f"{condition}_en", "")
    return condition, text, text_en


# ============================================================
# K.8538 planisphere sector data builder
# ============================================================
def _build_planisphere_data(planet_longs, positions):
    """Build 8-sector planisphere data mapping each planet to its 45° sector.

    Returns
    -------
    dict with keys:
        'sectors': list of 8 dicts, each containing direction, colour,
                   constellation info, and list of planets in that sector.
    """
    sectors = []
    for i in range(8):
        direction = BABYLONIAN_DIRECTIONS[i]
        constellation_data = BABYLONIAN_K8538_CONSTELLATIONS.get(i, [])
        planets_in_sector = [
            {
                "name": p.name,
                "god": p.god_name,
                "longitude": p.longitude,
                "degree": p.sign_degree,
                "akkadian": p.sign_akkadian,
            }
            for p in positions
            if int(p.longitude / 45) % 8 == i
        ]
        sectors.append({
            "index": i,
            "direction": direction,
            "direction_cn": BABYLONIAN_DIRECTION_CN[direction],
            "colour": BABYLONIAN_COLORS[i],
            "label": BABYLONIAN_K8538_SECTOR_LABELS[i],
            "constellations": [
                {"name": c[0], "akkadian": c[1], "dots": c[2]}
                for c in constellation_data
            ],
            "planets": planets_in_sector,
        })
    return {"sectors": sectors}


# ============================================================
# Main compute function
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def compute_babylonian_chart(year, month, day, hour, minute, timezone,
                             lat, lon):
    """Compute a Babylonian sidereal natal chart.

    Parameters
    ----------
    year, month, day : int
        Birth date (Gregorian).
    hour, minute : int
        Birth time (local).
    timezone : float
        UTC offset in hours.
    lat, lon : float
        Geographic latitude / longitude.

    Returns
    -------
    BabylonianChart
    """
    # Julian Day (UT)
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)

    # Set sidereal mode
    swe.set_sid_mode(BABYLONIAN_AYANAMSA_MODE)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # House cusps (sidereal)
    cusps_tuple, ascmc = swe.houses_ex(jd, lat, lon,
                                       b'P',  # Placidus
                                       swe.FLG_SIDEREAL)
    cusps = list(cusps_tuple)
    asc = ascmc[0]
    mc = ascmc[1]

    # Determine day/night chart (Sun above horizon = houses 7–12)
    sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    sun_house = _find_house(sun_pos, cusps)
    is_day = sun_house in (7, 8, 9, 10, 11, 12)

    # Compute planet positions
    planet_longs = {}
    planet_houses = {}
    positions = []
    omens = []

    for name, pid in _PLANET_IDS.items():
        result = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        sid_lon = result[0][0]
        idx = _sign_idx(sid_lon)
        house = _find_house(sid_lon, cusps)
        planet_longs[name] = sid_lon
        planet_houses[name] = house

        bz = BABYLONIAN_ZODIAC_SIGNS[idx]
        positions.append(BabylonianPlanetPosition(
            name=name,
            god_name=BABYLONIAN_PLANET_GODS.get(name, name),
            longitude=round(sid_lon, 4),
            sign_idx=idx,
            sign_akkadian=bz[1],
            sign_cn=bz[2],
            sign_en=bz[3],
            sign_western=bz[4],
            sign_degree=round(_sign_deg(sid_lon), 2),
            house=house,
        ))

        condition, text, text_en = _determine_omen(name, idx)
        omens.append(BabylonianOmen(
            planet=name,
            god_name=BABYLONIAN_PLANET_GODS.get(name, name),
            condition=condition,
            text=text,
            text_en=text_en,
        ))

    # Aspects
    aspects = _compute_aspects(planet_longs)

    # ── K.8538 planisphere data (8 sectors) ───────────────────
    planisphere_data = _build_planisphere_data(planet_longs, positions)

    return BabylonianChart(
        ascendant=asc,
        midheaven=mc,
        is_day_chart=is_day,
        planet_longitudes=planet_longs,
        planet_houses=planet_houses,
        house_cusps=cusps,
        positions=positions,
        planets=dict(BABYLONIAN_PLANET_GODS),
        omens=omens,
        aspects=aspects,
        ayanamsa=round(ayanamsa, 4),
        julian_day=jd,
        planisphere_data=planisphere_data,
    )


# ============================================================
# K.8538 Planisphere SVG — 8 區間泥板風格
# ============================================================
def build_k8538_planisphere_svg(chart, year=None, month=None, day=None,
                                hour=None, minute=None, tz=None,
                                location=""):
    """Build a K.8538-style planisphere SVG with 8 sectors.

    High-fidelity reproduction of the Nineveh planisphere disc (K.8538,
    British Museum): vitrified clay texture, 8 radial wedge sectors,
    connect-the-dots constellation patterns, cuneiform-style labels,
    concentric rings, and an irregular damaged-edge silhouette.

    Parameters
    ----------
    chart : BabylonianChart
    year, month, day, hour, minute, tz : birth-data for centre display
    location : str

    Returns
    -------
    str – complete ``<svg>`` markup.
    """
    SIZE = 620
    CX, CY = SIZE / 2, SIZE / 2
    R_OUTER = 260
    R_INNER = 65
    R_MID = 170

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SIZE} {SIZE}" '
        f'style="width:100%;max-width:620px;margin:auto;display:block;" '
        f'font-family="serif">'
    )

    # ── Defs: clay texture gradient + filters ──────────────────
    svg.append('<defs>')
    svg.append(
        '<radialGradient id="clay_bg" cx="50%" cy="50%" r="55%">'
        '<stop offset="0%" stop-color="#d4b07a"/>'
        '<stop offset="60%" stop-color="#c49a5c"/>'
        '<stop offset="100%" stop-color="#a07842"/>'
        '</radialGradient>'
    )
    # Noise-like filter for clay texture
    svg.append(
        '<filter id="clay_noise" x="0%" y="0%" width="100%" height="100%">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.65" '
        'numOctaves="3" stitchTiles="stitch" result="noise"/>'
        '<feColorMatrix type="saturate" values="0" in="noise" result="grey"/>'
        '<feBlend in="SourceGraphic" in2="grey" mode="multiply"/>'
        '</filter>'
    )
    # Glow filter for planet markers
    svg.append(
        '<filter id="planet_glow">'
        '<feGaussianBlur stdDeviation="2" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/>'
        '<feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    )
    svg.append('</defs>')

    # ── Background circle (clay disc) ─────────────────────────
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER + 20}" '
        f'fill="url(#clay_bg)" filter="url(#clay_noise)" '
        f'stroke="#7a5c30" stroke-width="3"/>'
    )

    # ── Damaged-edge cracks (irregular incisions on rim) ───────
    _crack_angles = [15, 58, 112, 175, 223, 287, 330]
    for ca in _crack_angles:
        rad_c = math.radians(ca)
        r_start = R_OUTER + 10
        r_end = R_OUTER - 8
        cx1 = CX + r_start * math.cos(rad_c)
        cy1 = CY - r_start * math.sin(rad_c)
        cx2 = CX + r_end * math.cos(rad_c + 0.04)
        cy2 = CY - r_end * math.sin(rad_c + 0.04)
        svg.append(
            f'<line x1="{cx1:.1f}" y1="{cy1:.1f}" '
            f'x2="{cx2:.1f}" y2="{cy2:.1f}" '
            f'stroke="#8b7355" stroke-width="0.6" opacity="0.5"/>'
        )

    # Outer rim
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER}" '
        f'fill="none" stroke="#5c3a1e" stroke-width="2.5"/>'
    )

    # Middle ring
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_MID}" '
        f'fill="none" stroke="#7a5c30" stroke-width="1" '
        f'stroke-dasharray="4,3"/>'
    )

    # Inner circle (centre area)
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_INNER}" '
        f'fill="#d4b87a" stroke="#5c3a1e" stroke-width="1.5"/>'
    )

    # ── 8 radial sector lines ─────────────────────────────────
    for i in range(8):
        angle = i * 45
        rad = math.radians(angle)
        x2 = CX + R_OUTER * math.cos(rad)
        y2 = CY - R_OUTER * math.sin(rad)
        svg.append(
            f'<line x1="{CX}" y1="{CY}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#5c3a1e" stroke-width="1.5"/>'
        )

    # ── Sector labels (direction + cuneiform + colour band) ───
    for i in range(8):
        angle = (i * 45 + 22.5)   # Centre of sector
        rad = math.radians(angle)

        # Direction label (outer)
        r_dir = R_OUTER + 12
        dx = CX + r_dir * math.cos(rad)
        dy = CY - r_dir * math.sin(rad)
        direction = BABYLONIAN_DIRECTIONS[i]
        svg.append(
            f'<text x="{dx:.1f}" y="{dy:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="10" font-weight="bold">{direction}</text>'
        )

        # Cuneiform sector label (inside outer rim)
        r_cunei = R_OUTER - 15
        clx = CX + r_cunei * math.cos(rad)
        cly = CY - r_cunei * math.sin(rad)
        sector_label = BABYLONIAN_K8538_SECTOR_LABELS[i]
        svg.append(
            f'<text x="{clx:.1f}" y="{cly:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="9" opacity="0.7">{sector_label}</text>'
        )

        # Coloured wedge fill (subtle)
        a1 = i * 45
        a2 = (i + 1) * 45
        r1 = math.radians(a1)
        r2 = math.radians(a2)
        ax1 = CX + R_OUTER * math.cos(r1)
        ay1 = CY - R_OUTER * math.sin(r1)
        ax2 = CX + R_OUTER * math.cos(r2)
        ay2 = CY - R_OUTER * math.sin(r2)
        ix1 = CX + R_INNER * math.cos(r1)
        iy1 = CY - R_INNER * math.sin(r1)
        ix2 = CX + R_INNER * math.cos(r2)
        iy2 = CY - R_INNER * math.sin(r2)
        path = (
            f'M{ix1:.1f},{iy1:.1f} '
            f'L{ax1:.1f},{ay1:.1f} '
            f'A{R_OUTER},{R_OUTER} 0 0,0 {ax2:.1f},{ay2:.1f} '
            f'L{ix2:.1f},{iy2:.1f} '
            f'A{R_INNER},{R_INNER} 0 0,1 {ix1:.1f},{iy1:.1f} Z'
        )
        svg.append(
            f'<path d="{path}" fill="{BABYLONIAN_COLORS[i]}" '
            f'fill-opacity="0.15" stroke="none"/>'
        )

    # ── Connect-the-dots constellation patterns ───────────────
    for sector_idx, constellations in BABYLONIAN_K8538_CONSTELLATIONS.items():
        sector_base_angle = sector_idx * 45 + 22.5
        for name, akk_label, dots in constellations:
            # Convert relative (r_frac, angle_offset) → absolute SVG coords
            points = []
            for r_frac, a_off in dots:
                r = R_INNER + r_frac * (R_MID - R_INNER)
                a = math.radians(sector_base_angle + a_off)
                px = CX + r * math.cos(a)
                py = CY - r * math.sin(a)
                points.append((px, py))
            # Draw connecting lines
            if len(points) >= 2:
                line_pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
                svg.append(
                    f'<polyline points="{line_pts}" fill="none" '
                    f'stroke="#8b7355" stroke-width="0.8" '
                    f'stroke-dasharray="3,2" opacity="0.6"/>'
                )
            # Draw dots (star points)
            for px, py in points:
                svg.append(
                    f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2" '
                    f'fill="#5c3a1e" opacity="0.7"/>'
                )
            # Constellation Akkadian label
            if points:
                mid = points[len(points) // 2]
                svg.append(
                    f'<text x="{mid[0]:.1f}" y="{mid[1] - 6:.1f}" '
                    f'text-anchor="middle" dominant-baseline="central" '
                    f'fill="#7a5c30" font-size="5" '
                    f'font-style="italic" opacity="0.8">{akk_label}</text>'
                )

    # ── Place planets in sectors ──────────────────────────────
    for pos in chart.positions:
        sector = int(pos.longitude / 45) % 8
        sector_centre_angle = sector * 45 + 22.5
        planet_list_in_sector = [p for p in chart.positions
                                 if int(p.longitude / 45) % 8 == sector]
        idx_in_sector = planet_list_in_sector.index(pos)
        n_in_sector = len(planet_list_in_sector)

        # Spread planets radially within the sector
        r_base = R_MID + 5
        r_step = (R_OUTER - R_MID - 45) / max(n_in_sector, 1)
        r_planet = r_base + idx_in_sector * r_step

        # Slight angular offset
        angle_spread = 20
        angle_offset = (idx_in_sector - (n_in_sector - 1) / 2) * (
            angle_spread / max(n_in_sector, 1))
        pa = sector_centre_angle + angle_offset
        rad = math.radians(pa)

        px = CX + r_planet * math.cos(rad)
        py = CY - r_planet * math.sin(rad)

        pglyph = PLANET_GLYPHS.get(pos.name, pos.name[0])
        pcolor = PLANET_COLORS.get(pos.name, "#5c3a1e")

        # Glowing planet marker
        svg.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="10" '
            f'fill="{pcolor}" fill-opacity="0.12" stroke="none" '
            f'filter="url(#planet_glow)"/>'
        )
        svg.append(
            f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{pcolor}" '
            f'font-size="18" font-weight="bold">{pglyph}</text>'
        )

        # Degree + Akkadian sign (small label)
        r_label = r_planet + 18
        lx = CX + r_label * math.cos(rad)
        ly = CY - r_label * math.sin(rad)
        svg.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="7">{pos.sign_degree:.0f}° {pos.sign_akkadian}</text>'
        )

    # ── Zodiac ring (outer band, 12 divisions) ────────────────
    R_ZODIAC_OUTER = R_OUTER - 5
    R_ZODIAC_INNER = R_OUTER - 35
    for i in range(12):
        a1 = i * 30
        a2 = (i + 1) * 30
        mid_a = a1 + 15
        rad_mid = math.radians(mid_a)

        r_glyph = (R_ZODIAC_OUTER + R_ZODIAC_INNER) / 2
        gx = CX + r_glyph * math.cos(rad_mid)
        gy = CY - r_glyph * math.sin(rad_mid)
        svg.append(
            f'<text x="{gx:.1f}" y="{gy:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="14">{ZODIAC_GLYPHS[i]}</text>'
        )

        # Akkadian name (tiny, further out)
        r_akk = R_ZODIAC_OUTER + 3
        akx = CX + r_akk * math.cos(rad_mid)
        aky = CY - r_akk * math.sin(rad_mid)
        akk = BABYLONIAN_ZODIAC_SIGNS[i][1]
        # Truncate long names
        if len(akk) > 8:
            akk = akk[:8] + "…"
        svg.append(
            f'<text x="{akx:.1f}" y="{aky:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#7a5c30" '
            f'font-size="5" font-style="italic">{akk}</text>'
        )

        # Tick marks for zodiac divisions
        r1 = math.radians(a1)
        tx1 = CX + R_ZODIAC_INNER * math.cos(r1)
        ty1 = CY - R_ZODIAC_INNER * math.sin(r1)
        tx2 = CX + R_ZODIAC_OUTER * math.cos(r1)
        ty2 = CY - R_ZODIAC_OUTER * math.sin(r1)
        svg.append(
            f'<line x1="{tx1:.1f}" y1="{ty1:.1f}" '
            f'x2="{tx2:.1f}" y2="{ty2:.1f}" '
            f'stroke="#7a5c30" stroke-width="0.7"/>'
        )

    # ── Centre text ───────────────────────────────────────────
    svg.append(
        f'<text x="{CX}" y="{CY - 38}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#5c3a1e" '
        f'font-size="11" font-weight="bold">K.8538</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY - 24}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#5c3a1e" '
        f'font-size="9">𒀭 MUL.APIN</text>'
    )

    sect_label = "☉ Day / 日生" if chart.is_day_chart else "☽ Night / 夜生"
    svg.append(
        f'<text x="{CX}" y="{CY - 8}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#5c3a1e" '
        f'font-size="8">{sect_label}</text>'
    )

    if year is not None and month is not None and day is not None:
        date_str = f"{year}-{month:02d}-{day:02d}"
        svg.append(
            f'<text x="{CX}" y="{CY + 6}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="8">{date_str}</text>'
        )

    if hour is not None and minute is not None:
        tz_str = f" UTC{tz:+.1f}" if tz is not None else ""
        time_str = f"{hour:02d}:{minute:02d}{tz_str}"
        svg.append(
            f'<text x="{CX}" y="{CY + 18}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="8">{time_str}</text>'
        )

    # ASC sign info
    asc_idx = _sign_idx(chart.ascendant)
    asc_deg = round(_sign_deg(chart.ascendant), 1)
    asc_akk = BABYLONIAN_ZODIAC_SIGNS[asc_idx][1]
    svg.append(
        f'<text x="{CX}" y="{CY + 32}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#8b4513" '
        f'font-size="8">ASC {ZODIAC_GLYPHS[asc_idx]} '
        f'{asc_akk} {asc_deg}°</text>'
    )

    if location:
        svg.append(
            f'<text x="{CX}" y="{CY + 44}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#7a5c30" '
            f'font-size="6">{location[:25]}</text>'
        )

    svg.append("</svg>")
    return "\n".join(svg)


# Backward-compatible alias — app.py and other modules import this name.
# build_k8538_planisphere_svg is the canonical function; this alias
# ensures existing ``from astro.babylonian import build_babylonian_planisphere_svg``
# statements continue to work without modification.
build_babylonian_planisphere_svg = build_k8538_planisphere_svg


# ============================================================
# Render Babylonian chart in Streamlit
# ============================================================
def render_babylonian_chart(chart, after_chart_hook=None):
    """Render the Babylonian natal chart details in Streamlit.

    Parameters
    ----------
    chart : BabylonianChart
    after_chart_hook : callable, optional
        If provided, called after rendering the main chart section.
    """
    st.subheader(t("babylonian_chart_title"))
    st.info(
        f"**Ayanamsa**: {chart.ayanamsa}° (Fagan-Bradley) | "
        f"**Sect**: {'Day ☉ 日生' if chart.is_day_chart else 'Night ☽ 夜生'} | "
        f"**JD**: {chart.julian_day:.4f}"
    )

    # ── Planet positions ──────────────────────────────────────
    st.markdown("#### 𒀭 " + t("babylonian_planet_positions"))
    pos_data = []
    for pos in chart.positions:
        pos_data.append({
            t("babylonian_col_planet"): f"{pos.name} ({GRAHA_CN.get(pos.name, pos.name)})",
            t("babylonian_col_god"): pos.god_name,
            t("babylonian_col_akkadian"): pos.sign_akkadian,
            t("babylonian_col_sign_cn"): pos.sign_cn,
            t("babylonian_col_degree"): f"{pos.sign_degree:.2f}°",
            t("babylonian_col_house"): pos.house,
        })
    if pos_data:
        st.dataframe(pos_data, width="stretch")

    # ── Omens ─────────────────────────────────────────────────
    st.markdown("#### 📜 " + t("babylonian_omens_title"))
    for omen in chart.omens:
        icon = "🌟" if omen.condition == "strong" else "⚠️"
        en_part = f"  \n_{omen.text_en}_" if omen.text_en else ""
        st.markdown(
            f"{icon} **{omen.planet}** ({omen.god_name}) — "
            f"*{omen.condition.upper()}*: {omen.text}{en_part}"
        )

    # ── Aspects ───────────────────────────────────────────────
    if chart.aspects:
        st.markdown("#### ⚡ " + t("babylonian_aspects_title"))
        asp_data = []
        for asp in chart.aspects:
            asp_data.append({
                t("babylonian_col_planet") + " 1": asp["planet1"],
                t("babylonian_col_planet") + " 2": asp["planet2"],
                t("babylonian_col_aspect"): asp["aspect"].capitalize(),
                t("babylonian_col_angle"): f"{asp['angle']:.2f}°",
                t("babylonian_col_orb"): f"{asp['orb']:.2f}°",
            })
        st.dataframe(asp_data, width="stretch")

    # ── House cusps ───────────────────────────────────────────
    st.markdown("#### 🏛️ " + t("babylonian_houses_title"))
    house_data = []
    for i, cusp in enumerate(chart.house_cusps):
        idx = _sign_idx(cusp)
        bz = BABYLONIAN_ZODIAC_SIGNS[idx]
        house_data.append({
            t("babylonian_col_house"): i + 1,
            t("babylonian_col_cusp"): f"{cusp:.2f}°",
            t("babylonian_col_akkadian"): bz[1],
            t("babylonian_col_sign_cn"): bz[2],
        })
    st.dataframe(house_data, width="stretch")

    if after_chart_hook:
        after_chart_hook()
