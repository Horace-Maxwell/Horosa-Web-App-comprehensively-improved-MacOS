"""
astro/hellenistic.py — 希臘占星 (Hellenistic Astrology)

Lots, Egyptian Bounds, Annual Profections, Zodiacal Releasing,
Planetary Condition scoring, Sect analysis, Greek horoscope SVG chart.
"""
import math
import streamlit as st
import swisseph as swe
from dataclasses import dataclass, field

ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_CN = {
    "Aries": "白羊座", "Taurus": "金牛座", "Gemini": "雙子座", "Cancer": "巨蟹座",
    "Leo": "獅子座", "Virgo": "處女座", "Libra": "天秤座", "Scorpio": "天蠍座",
    "Sagittarius": "射手座", "Capricorn": "摩羯座", "Aquarius": "水瓶座", "Pisces": "雙魚座",
}

SIGN_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# Minor years for Zodiacal Releasing
SIGN_YEARS = {
    "Aries": 15, "Taurus": 8, "Gemini": 20, "Cancer": 25,
    "Leo": 19, "Virgo": 20, "Libra": 8, "Scorpio": 15,
    "Sagittarius": 12, "Capricorn": 27, "Aquarius": 30, "Pisces": 12,
}

# Egyptian Bounds (Ptolemaic)
EGYPTIAN_BOUNDS = {
    0: [("Jupiter",0,6),("Venus",6,12),("Mercury",12,20),("Mars",20,25),("Saturn",25,30)],
    1: [("Venus",0,8),("Mercury",8,14),("Jupiter",14,22),("Saturn",22,27),("Mars",27,30)],
    2: [("Mercury",0,6),("Jupiter",6,12),("Venus",12,17),("Mars",17,24),("Saturn",24,30)],
    3: [("Mars",0,7),("Venus",7,13),("Mercury",13,19),("Jupiter",19,26),("Saturn",26,30)],
    4: [("Jupiter",0,6),("Venus",6,11),("Saturn",11,18),("Mercury",18,24),("Mars",24,30)],
    5: [("Mercury",0,7),("Venus",7,17),("Jupiter",17,21),("Mars",21,28),("Saturn",28,30)],
    6: [("Saturn",0,6),("Mercury",6,14),("Jupiter",14,21),("Venus",21,28),("Mars",28,30)],
    7: [("Mars",0,7),("Venus",7,11),("Mercury",11,19),("Jupiter",19,24),("Saturn",24,30)],
    8: [("Jupiter",0,12),("Venus",12,17),("Mercury",17,21),("Mars",21,26),("Saturn",26,30)],
    9: [("Mercury",0,7),("Jupiter",7,14),("Venus",14,22),("Saturn",22,26),("Mars",26,30)],
    10:[("Mercury",0,7),("Venus",7,13),("Jupiter",13,20),("Mars",20,25),("Saturn",25,30)],
    11:[("Venus",0,12),("Jupiter",12,16),("Mercury",16,19),("Mars",19,28),("Saturn",28,30)],
}

# Dignity tables
DOMICILE = {"Sun": [4], "Moon": [3], "Mars": [0,7], "Mercury": [2,5],
            "Jupiter": [8,11], "Venus": [1,6], "Saturn": [9,10]}
EXALTATION = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5,
              "Jupiter": 3, "Venus": 11, "Saturn": 6}
DETRIMENT = {"Sun": [10], "Moon": [9], "Mars": [1,6], "Mercury": [8,11],
             "Jupiter": [2,5], "Venus": [0,7], "Saturn": [3,4]}
FALL = {"Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11,
        "Jupiter": 9, "Venus": 5, "Saturn": 0}


def _sign_idx(lon): return int(lon / 30) % 12
def _sign_deg(lon): return lon % 30
def _normalize(deg): return deg % 360


@dataclass
class Lot:
    name: str
    name_cn: str
    longitude: float
    sign: str
    sign_degree: float
    house: int
    formula_en: str
    meaning_en: str
    meaning_cn: str


@dataclass
class BoundsEntry:
    sign: str
    planet: str
    start_degree: float
    end_degree: float


@dataclass
class ProfectionResult:
    current_age: int
    profected_sign: str
    profected_sign_cn: str
    time_lord: str
    time_lord_cn: str
    house_from_asc: int


@dataclass
class ZodiacalReleasingPeriod:
    level: str
    sign: str
    sign_cn: str
    ruler: str
    start_jd: float
    end_jd: float
    start_date: str
    end_date: str
    years: float


@dataclass
class PlanetCondition:
    planet: str
    score: int
    details: list  # list of (factor, points, description)


@dataclass
class HellenisticChart:
    ascendant: float
    midheaven: float
    is_day_chart: bool
    planet_longitudes: dict
    planet_houses: dict
    house_cusps: list
    lots: list = field(default_factory=list)
    bounds: list = field(default_factory=list)
    profection: object = None
    zodiacal_releasing: list = field(default_factory=list)
    planet_conditions: list = field(default_factory=list)
    sect_analysis: dict = field(default_factory=dict)


GRAHA_CN = {"Sun": "太陽", "Moon": "月亮", "Mercury": "水星", "Venus": "金星",
            "Mars": "火星", "Jupiter": "木星", "Saturn": "土星"}


def _jd_to_date(jd):
    y, m, d, h = swe.revjul(jd)
    return f"{y:04d}-{m:02d}-{int(d):02d}"


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


def compute_lots(planet_longs, ascendant, is_day, cusps):
    """Compute 7 Greek Lots."""
    sun = planet_longs.get("Sun", 0)
    moon = planet_longs.get("Moon", 0)
    venus = planet_longs.get("Venus", 0)
    mars = planet_longs.get("Mars", 0)
    mercury = planet_longs.get("Mercury", 0)
    jupiter = planet_longs.get("Jupiter", 0)
    saturn = planet_longs.get("Saturn", 0)

    if is_day:
        fortune = _normalize(ascendant + moon - sun)
        spirit = _normalize(ascendant + sun - moon)
    else:
        fortune = _normalize(ascendant + sun - moon)
        spirit = _normalize(ascendant + moon - sun)

    defs = [
        ("Lot of Fortune", "福點", fortune, "Asc+Moon-Sun (day)", "Body, health, fortune", "身體、健康、財運"),
        ("Lot of Spirit", "靈點", spirit, "Asc+Sun-Moon (day)", "Mind, career, purpose", "心靈、事業、目的"),
        ("Lot of Eros", "愛神點", _normalize(ascendant + venus - spirit), "Asc+Venus-Spirit", "Love, desire", "愛情、慾望"),
        ("Lot of Necessity", "命運點", _normalize(ascendant + fortune - mercury), "Asc+Fortune-Mercury", "Fate, obligations", "命運、義務"),
        ("Lot of Courage", "勇氣點", _normalize(ascendant + fortune - mars), "Asc+Fortune-Mars", "Boldness, conflict", "勇敢、衝突"),
        ("Lot of Victory", "勝利點", _normalize(ascendant + jupiter - spirit), "Asc+Jupiter-Spirit", "Success, abundance", "成功、豐盛"),
        ("Lot of Nemesis", "報應點", _normalize(ascendant + fortune - saturn), "Asc+Fortune-Saturn", "Hidden enemies, karma", "隱敵、業力"),
    ]
    lots = []
    for name, cn, lon, formula, m_en, m_cn in defs:
        idx = _sign_idx(lon)
        lots.append(Lot(
            name=name, name_cn=cn, longitude=lon,
            sign=ZODIAC_SIGNS[idx], sign_degree=round(_sign_deg(lon), 2),
            house=_find_house(lon, cusps),
            formula_en=formula, meaning_en=m_en, meaning_cn=m_cn,
        ))
    return lots


def get_bound_lord(sign_idx, degree):
    for planet, start, end in EGYPTIAN_BOUNDS.get(sign_idx, []):
        if start <= degree < end:
            return BoundsEntry(
                sign=ZODIAC_SIGNS[sign_idx], planet=planet,
                start_degree=start, end_degree=end,
            )
    return None


def compute_profections(ascendant_lon, birth_year, current_year):
    if current_year is None:
        return None
    age = current_year - birth_year
    asc_idx = _sign_idx(ascendant_lon)
    prof_idx = (asc_idx + age) % 12
    sign = ZODIAC_SIGNS[prof_idx]
    ruler = SIGN_RULERS[sign]
    return ProfectionResult(
        current_age=age, profected_sign=sign,
        profected_sign_cn=SIGN_CN[sign], time_lord=ruler,
        time_lord_cn=GRAHA_CN.get(ruler, ruler),
        house_from_asc=(prof_idx - asc_idx) % 12 + 1,
    )


def compute_zodiacal_releasing(fortune_lon, birth_jd, target_jd):
    """L1 periods from Lot of Fortune."""
    start_idx = _sign_idx(fortune_lon)
    periods = []
    cur_jd = birth_jd
    for i in range(20):  # ~20 L1 periods to cover most lifetimes
        idx = (start_idx + i) % 12
        sign = ZODIAC_SIGNS[idx]
        yrs = SIGN_YEARS[sign]
        end_jd = cur_jd + yrs * 365.25
        periods.append(ZodiacalReleasingPeriod(
            level="L1", sign=sign, sign_cn=SIGN_CN[sign],
            ruler=SIGN_RULERS[sign],
            start_jd=cur_jd, end_jd=end_jd,
            start_date=_jd_to_date(cur_jd), end_date=_jd_to_date(end_jd),
            years=yrs,
        ))
        if end_jd > target_jd and i > 2:
            break
        cur_jd = end_jd
    return periods


def compute_planet_conditions(planet_longs, planet_houses, is_day, asc_lon):
    results = []
    for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        if planet not in planet_longs:
            continue
        lon = planet_longs[planet]
        idx = _sign_idx(lon)
        house = planet_houses.get(planet, 0)
        score = 0
        details = []

        # Sect
        day_planets = {"Sun", "Jupiter", "Saturn"}
        night_planets = {"Moon", "Venus", "Mars"}
        if is_day and planet in day_planets:
            score += 3; details.append(("Sect", 3, "In preferred sect"))
        elif not is_day and planet in night_planets:
            score += 3; details.append(("Sect", 3, "In preferred sect"))
        elif planet in day_planets or planet in night_planets:
            score -= 3; details.append(("Sect", -3, "Against sect"))

        # Domicile
        if idx in DOMICILE.get(planet, []):
            score += 5; details.append(("Domicile", 5, f"In own sign {ZODIAC_SIGNS[idx]}"))
        # Exaltation
        if EXALTATION.get(planet) == idx:
            score += 4; details.append(("Exaltation", 4, f"Exalted in {ZODIAC_SIGNS[idx]}"))
        # Detriment
        if idx in DETRIMENT.get(planet, []):
            score -= 5; details.append(("Detriment", -5, f"In detriment"))
        # Fall
        if FALL.get(planet) == idx:
            score -= 4; details.append(("Fall", -4, f"In fall"))

        # House (angular/succedent/cadent)
        if house in (1, 4, 7, 10):
            score += 3; details.append(("Angular", 3, f"House {house}"))
        elif house in (2, 5, 8, 11):
            score += 1; details.append(("Succedent", 1, f"House {house}"))
        elif house in (3, 6, 9, 12):
            score -= 1; details.append(("Cadent", -1, f"House {house}"))

        results.append(PlanetCondition(planet=planet, score=score, details=details))
    return results


def _compute_sect(planet_longs, planet_houses, is_day):
    sect = "Day" if is_day else "Night"
    day_benefic = "Jupiter"
    night_benefic = "Venus"
    return {
        "sect": sect,
        "sect_light": "Sun" if is_day else "Moon",
        "benefic_of_sect": day_benefic if is_day else night_benefic,
        "malefic_of_sect": "Saturn" if is_day else "Mars",
    }


@st.cache_data(ttl=3600, show_spinner=False)
def compute_hellenistic_chart(western_chart, birth_year=None,
                              current_year=None, current_jd=None):
    """Derive Hellenistic techniques from a WesternChart."""
    p_longs = {p.name.split()[0]: p.longitude for p in western_chart.planets}
    p_houses = {p.name.split()[0]: p.house for p in western_chart.planets}
    cusps = [h.cusp for h in western_chart.houses]
    asc = western_chart.ascendant
    is_day = western_chart.is_day_chart

    lots = compute_lots(p_longs, asc, is_day, cusps)
    asc_idx = _sign_idx(asc)
    bound = get_bound_lord(asc_idx, _sign_deg(asc))
    profection = compute_profections(asc, birth_year or western_chart.year,
                                     current_year)

    fortune_lon = lots[0].longitude if lots else 0.0
    birth_jd = western_chart.julian_day
    zr = compute_zodiacal_releasing(fortune_lon, birth_jd,
                                     current_jd or birth_jd + 36525)
    conditions = compute_planet_conditions(p_longs, p_houses, is_day, asc)
    sect = _compute_sect(p_longs, p_houses, is_day)

    return HellenisticChart(
        ascendant=asc, midheaven=western_chart.midheaven,
        is_day_chart=is_day, planet_longitudes=p_longs,
        planet_houses=p_houses, house_cusps=cusps,
        lots=lots, bounds=[bound] if bound else [],
        profection=profection, zodiacal_releasing=zr,
        planet_conditions=conditions, sect_analysis=sect,
    )


# ============================================================
# Greek Horoscope SVG — θέμα (Thema) Chart
# ============================================================
# Based on ancient Greek papyrus horoscope format (cf. L 497).
# Square frame with 12 triangular house sections radiating from centre.
# Whole-sign houses; ASC at left, MC at top.

ZODIAC_GLYPHS = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓",
]

ZODIAC_GREEK = [
    "Κριός", "Ταῦρος", "Δίδυμοι", "Καρκίνος",
    "Λέων", "Παρθένος", "Ζυγός", "Σκορπίος",
    "Τοξότης", "Αἰγόκερως", "Ὑδροχόος", "Ἰχθύες",
]

PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿",
    "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
}

PLANET_COLORS_GREEK = {
    "Sun": "#b8860b", "Moon": "#556b7f", "Mercury": "#8b6914",
    "Venus": "#2e7d32", "Mars": "#b71c1c", "Jupiter": "#1565c0",
    "Saturn": "#4a4a4a",
}

ELEMENT_OF_SIGN = [
    "fire", "earth", "air", "water",
    "fire", "earth", "air", "water",
    "fire", "earth", "air", "water",
]

ELEMENT_COLORS = {
    "fire": "#b71c1c", "earth": "#2e7d32",
    "air": "#1565c0", "water": "#00838f",
}

HOUSE_ROMAN = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ",
               "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ", "Ⅺ", "Ⅻ"]

# Greek names for the 12 topoi (places)
TOPOS_GREEK = [
    "Ὡροσκόπος",       # I   – Horoskopos (Ascendant)
    "Πύλη Ἅιδου",      # II  – Gate of Hades
    "Θεά",              # III – Goddess
    "Ὑπόγειον",         # IV  – Subterranean (IC)
    "Ἀγαθὴ Τύχη",      # V   – Good Fortune
    "Κακὴ Τύχη",        # VI  – Bad Fortune
    "Δύσις",            # VII – Setting (Descendant)
    "Ἐπικαταφορά",      # VIII – Epicataphora
    "Θεός",             # IX  – God
    "Μεσουράνημα",      # X   – Midheaven (MC)
    "Ἀγαθὸς Δαίμων",   # XI  – Good Daimon
    "Κακὸς Δαίμων",     # XII – Bad Daimon
]

TOPOS_CN = [
    "命宮", "財帛宮", "兄弟宮", "田宅宮",
    "子女宮", "奴僕宮", "夫妻宮", "疾厄宮",
    "遷移宮", "官祿宮", "福德宮", "玄秘宮",
]


def _ray_to_square(cx, cy, half, angle_deg):
    """Where a ray from (cx, cy) at *angle_deg* meets a square boundary.

    Angle convention: 0° = right, clockwise positive (SVG natural).
    The square spans [cx-half, cx+half] × [cy-half, cy+half].
    """
    rad = math.radians(angle_deg % 360)
    ca, sa = math.cos(rad), math.sin(rad)
    candidates = []
    if abs(ca) > 1e-9:
        t = half / abs(ca)
        if abs(sa * t) <= half + 0.5:
            candidates.append(t)
    if abs(sa) > 1e-9:
        t = half / abs(sa)
        if abs(ca * t) <= half + 0.5:
            candidates.append(t)
    t = min(candidates) if candidates else half
    return cx + t * ca, cy + t * sa


def build_greek_horoscope_svg(chart, year=None, month=None, day=None,
                              hour=None, minute=None, tz=None,
                              location=""):
    """Build an SVG string for a Greek-style square horoscope chart (θέμα).

    Layout based on the ancient Greek papyrus horoscope form (cf. L 497):
    - Square outer frame with parchment colouring.
    - 12 triangular whole-sign house sections radiating from centre.
    - Ascendant (House I) at the left, MC (House X) at the top.
    - Zodiac sign glyphs, Greek sign names, planet symbols, lots.
    - Centre circle with birth data, sect, and ASC info.

    Parameters
    ----------
    chart : HellenisticChart
    year, month, day, hour, minute, tz : birth-data for centre display
    location : location string for centre display

    Returns
    -------
    str – complete ``<svg>`` markup.
    """
    SIZE = 620
    CX, CY = SIZE / 2, SIZE / 2
    HALF = 250                          # half-side of chart square

    # ── angle helpers ──────────────────────────────────────────────
    def _boundary(h):
        """Angle of boundary line between house h-1 and house h (1-indexed).

        Houses go counterclockwise (decreasing SVG angle) from ASC at 180°.
        Offset by +15° so that square corners fall exactly on boundaries.
        """
        return (195 - (h - 1) * 30) % 360

    def _centre_angle(h):
        """Centre angle of house h."""
        return (180 - (h - 1) * 30) % 360

    def _polar(r, a):
        """Polar → SVG coordinates."""
        rad = math.radians(a)
        return CX + r * math.cos(rad), CY + r * math.sin(rad)

    def _edge(a):
        return _ray_to_square(CX, CY, HALF, a)

    # ── house data ─────────────────────────────────────────────────
    asc_idx = _sign_idx(chart.ascendant)

    houses = []
    for h in range(1, 13):
        sign_idx = (asc_idx + h - 1) % 12
        planets = [(p, round(_sign_deg(lon), 1))
                   for p, lon in chart.planet_longitudes.items()
                   if _sign_idx(lon) == sign_idx]
        lots = [l for l in chart.lots
                if l.sign == ZODIAC_SIGNS[sign_idx]]
        houses.append({
            "h": h, "sign_idx": sign_idx,
            "planets": planets, "lots": lots,
            "angular": h in (1, 4, 7, 10),
            "succedent": h in (2, 5, 8, 11),
        })

    # ── SVG construction ──────────────────────────────────────────
    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SIZE} {SIZE}" '
        f'style="width:100%;max-width:620px;margin:auto;display:block;" '
        f'font-family="serif">'
    )

    # Background (warm parchment)
    svg.append(f'<rect width="{SIZE}" height="{SIZE}" fill="#f5e6c8" rx="6"/>')

    # Double decorative border
    svg.append(
        f'<rect x="8" y="8" width="{SIZE-16}" height="{SIZE-16}" '
        f'fill="none" stroke="#5c3a1e" stroke-width="2.5" rx="3"/>'
    )
    svg.append(
        f'<rect x="14" y="14" width="{SIZE-28}" height="{SIZE-28}" '
        f'fill="none" stroke="#8b7355" stroke-width="1" rx="2"/>'
    )

    # Greek-key meander top/bottom decorative strip
    for row_y in (22, SIZE - 30):
        for xi in range(10):
            mx = 30 + xi * 56
            if mx > SIZE - 50:
                break
            svg.append(
                f'<path d="M{mx},{row_y} h12 v6 h-6 v-3 h-6 z" '
                f'fill="none" stroke="#8b7355" stroke-width="0.8" opacity="0.5"/>'
            )

    # Chart square area
    sq_x, sq_y = CX - HALF, CY - HALF
    svg.append(
        f'<rect x="{sq_x}" y="{sq_y}" width="{HALF*2}" height="{HALF*2}" '
        f'fill="#efe0c0" stroke="#5c3a1e" stroke-width="2"/>'
    )

    # ── filled house-section triangles ──────────────────────────
    for hd in houses:
        h = hd["h"]
        ba1 = _boundary(h)
        ba2 = _boundary(h % 12 + 1)
        p1 = _edge(ba1)
        p2 = _edge(ba2)

        if hd["angular"]:
            fill = "#e0cfa0"
        elif hd["succedent"]:
            fill = "#ebe0c0"
        else:
            fill = "#f2e8d0"

        pts = f"{CX},{CY} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
        svg.append(
            f'<polygon points="{pts}" fill="{fill}" '
            f'stroke="#8b6914" stroke-width="0.5"/>'
        )

    # ── boundary lines ─────────────────────────────────────────
    for h in range(1, 13):
        p = _edge(_boundary(h))
        svg.append(
            f'<line x1="{CX}" y1="{CY}" x2="{p[0]:.1f}" y2="{p[1]:.1f}" '
            f'stroke="#5c3a1e" stroke-width="1.2"/>'
        )

    # ── centre circle ──────────────────────────────────────────
    CR = 68
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{CR}" '
        f'fill="#f5e6c8" stroke="#5c3a1e" stroke-width="1.5"/>'
    )

    # ── house content ──────────────────────────────────────────
    for hd in houses:
        h = hd["h"]
        si = hd["sign_idx"]
        ca = _centre_angle(h)

        # Distance from centre to the square edge along centre angle
        ex, ey = _edge(ca)
        d_edge = math.hypot(ex - CX, ey - CY)

        # Zodiac glyph (outer area)
        r_glyph = d_edge * 0.73
        gx, gy = _polar(r_glyph, ca)
        elem = ELEMENT_OF_SIGN[si]
        svg.append(
            f'<text x="{gx:.1f}" y="{gy:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{ELEMENT_COLORS[elem]}" '
            f'font-size="22" font-weight="bold">'
            f'{ZODIAC_GLYPHS[si]}</text>'
        )

        # Greek sign name (smaller, further in)
        r_greek = d_edge * 0.60
        gnx, gny = _polar(r_greek, ca)
        svg.append(
            f'<text x="{gnx:.1f}" y="{gny:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="8" font-style="italic">'
            f'{ZODIAC_GREEK[si]}</text>'
        )

        # House Roman numeral (near centre)
        r_house = d_edge * 0.33
        hx, hy = _polar(r_house, ca)
        h_color = "#8b4513" if hd["angular"] else "#8b7355"
        h_weight = "bold" if hd["angular"] else "normal"
        h_fsize = "14" if hd["angular"] else "12"
        svg.append(
            f'<text x="{hx:.1f}" y="{hy:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{h_color}" '
            f'font-size="{h_fsize}" font-weight="{h_weight}">'
            f'{HOUSE_ROMAN[h - 1]}</text>'
        )

        # Topos Chinese name (宮位名, small label in outer area)
        r_topos = d_edge * 0.86
        tx, ty = _polar(r_topos, ca)
        topos_cn_label = TOPOS_CN[h - 1]
        svg.append(
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#7a6a50" '
            f'font-size="8">'
            f'{topos_cn_label}</text>'
        )

        # Planets in this sign
        if hd["planets"]:
            n = len(hd["planets"])
            r_planet = d_edge * 0.49
            for pi, (pname, pdeg) in enumerate(hd["planets"]):
                offset = (pi - (n - 1) / 2) * 7
                pa = ca + offset
                px, py = _polar(r_planet, pa)
                pglyph = PLANET_GLYPHS.get(pname, pname[0])
                pcolor = PLANET_COLORS_GREEK.get(pname, "#5c3a1e")
                svg.append(
                    f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" '
                    f'dominant-baseline="central" fill="{pcolor}" '
                    f'font-size="16" font-weight="bold">'
                    f'{pglyph}</text>'
                )
                # Degree label
                r_deg = d_edge * 0.41
                dx, dy = _polar(r_deg, pa)
                svg.append(
                    f'<text x="{dx:.1f}" y="{dy:.1f}" text-anchor="middle" '
                    f'dominant-baseline="central" fill="#5c3a1e" '
                    f'font-size="7">{pdeg:.0f}°</text>'
                )

        # Lots (small markers)
        if hd["lots"]:
            n_lots = len(hd["lots"])
            r_lot = d_edge * 0.82
            for li, lot in enumerate(hd["lots"]):
                la = ca + (li - (n_lots - 1) / 2) * 6
                lx, ly = _polar(r_lot, la)
                lot_color = "#8b0000" if "Fortune" in lot.name else "#1a5276"
                abbr = lot.name_cn[0] if lot.name_cn else "L"
                svg.append(
                    f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="8" '
                    f'fill="{lot_color}" fill-opacity="0.2" '
                    f'stroke="{lot_color}" stroke-width="0.8"/>'
                )
                svg.append(
                    f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
                    f'dominant-baseline="central" fill="{lot_color}" '
                    f'font-size="9" font-weight="bold">{abbr}</text>'
                )

    # ── cardinal point labels (outside the square) ─────────────
    cardinal = [
        (180, "ASC", "Ὡροσκόπος"),
        (90, "IC", "Ὑπόγειον"),
        (0, "DESC", "Δύσις"),
        (270, "MC", "Μεσουράνημα"),
    ]
    for angle, eng, greek in cardinal:
        lx, ly = _polar(HALF + 20, angle)
        svg.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="11" font-weight="bold">{eng}</text>'
        )
        lx2, ly2 = _polar(HALF + 33, angle)
        svg.append(
            f'<text x="{lx2:.1f}" y="{ly2:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#8b7355" '
            f'font-size="7" font-style="italic">{greek}</text>'
        )

    # ── centre text ───────────────────────────────────────────
    svg.append(
        f'<text x="{CX}" y="{CY - 42}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#5c3a1e" '
        f'font-size="16" font-weight="bold">ΘΕΜΑ</text>'
    )

    sect_label = "☉ Day / 日生" if chart.is_day_chart else "☽ Night / 夜生"
    svg.append(
        f'<text x="{CX}" y="{CY - 24}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#5c3a1e" '
        f'font-size="9">{sect_label}</text>'
    )

    if year is not None and month is not None and day is not None:
        date_str = f"{year}-{month:02d}-{day:02d}"
        svg.append(
            f'<text x="{CX}" y="{CY - 8}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="9">{date_str}</text>'
        )

    if hour is not None and minute is not None:
        tz_str = f" UTC{tz:+.1f}" if tz is not None else ""
        time_str = f"{hour:02d}:{minute:02d}{tz_str}"
        svg.append(
            f'<text x="{CX}" y="{CY + 6}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="9">{time_str}</text>'
        )

    # ASC sign + degree
    asc_sign = ZODIAC_SIGNS[asc_idx]
    asc_deg = round(_sign_deg(chart.ascendant), 1)
    svg.append(
        f'<text x="{CX}" y="{CY + 22}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#8b4513" '
        f'font-size="9">ASC {ZODIAC_GLYPHS[asc_idx]} '
        f'{asc_sign} {asc_deg}°</text>'
    )

    # Bound lord
    if chart.bounds:
        b = chart.bounds[0]
        svg.append(
            f'<text x="{CX}" y="{CY + 36}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#8b7355" '
            f'font-size="8">Bound: {b.planet} '
            f'({b.start_degree}°–{b.end_degree}°)</text>'
        )

    if location:
        svg.append(
            f'<text x="{CX}" y="{CY + 50}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#8b7355" '
            f'font-size="7">{location[:25]}</text>'
        )

    svg.append("</svg>")
    return "\n".join(svg)


def render_hellenistic_chart(chart):
    """Render Hellenistic chart in Streamlit."""
    import streamlit as st

    st.subheader("☿ Hellenistic Astrology / 希臘占星")
    sect = chart.sect_analysis
    st.info(f"**Sect**: {sect.get('sect', '—')} chart | "
            f"Benefic of sect: {sect.get('benefic_of_sect', '—')} | "
            f"Malefic of sect: {sect.get('malefic_of_sect', '—')}")

    # Lots
    st.markdown("#### Lots / 希臘點")
    lot_data = []
    for lot in chart.lots:
        lot_data.append({
            "Name": f"{lot.name} ({lot.name_cn})",
            "Sign": lot.sign,
            "Degree": f"{lot.sign_degree:.2f}°",
            "House": lot.house,
            "Meaning": lot.meaning_cn,
        })
    if lot_data:
        st.dataframe(lot_data, width="stretch")

    # Bounds
    if chart.bounds:
        b = chart.bounds[0]
        st.markdown(f"#### Ascendant Bound Lord / 上升界主: **{b.planet}** "
                    f"({b.sign} {b.start_degree}°–{b.end_degree}°)")

    # Profection
    if chart.profection:
        pf = chart.profection
        st.markdown(f"#### Annual Profection / 年限推進")
        st.write(f"Age {pf.current_age} → **{pf.profected_sign}** ({pf.profected_sign_cn}) | "
                 f"Time Lord: **{pf.time_lord}** ({pf.time_lord_cn}) | "
                 f"House {pf.house_from_asc}")

    # Zodiacal Releasing
    if chart.zodiacal_releasing:
        st.markdown("#### Zodiacal Releasing / 黃道釋放 (L1)")
        zr_data = [{"Sign": p.sign, "Sign (CN)": p.sign_cn,
                     "Ruler": p.ruler, "Years": p.years,
                     "Start": p.start_date, "End": p.end_date}
                    for p in chart.zodiacal_releasing]
        st.dataframe(zr_data, width="stretch")

    # Planet Conditions
    if chart.planet_conditions:
        st.markdown("#### Planetary Condition / 行星狀態評分")
        cond_data = []
        for pc in chart.planet_conditions:
            detail_str = "; ".join(f"{f}: {p:+d}" for f, p, _ in pc.details)
            cond_data.append({"Planet": pc.planet, "Score": pc.score,
                              "Details": detail_str})
        st.dataframe(cond_data, width="stretch")


# ============================================================
# Extended Hellenistic Lots  (Valens / Hellenistic tradition)
# ============================================================
# 12 additional Lots following Vettius Valens' *Anthologies* and
# standard Hellenistic formulae.  Each Lot uses a day / night
# formula variant (the night formula reverses the subtraction
# of the two significator planets).

# Exaltation degree lookup — the exact degree of exaltation used
# in the Lot of Exaltation formula.
_EXALTATION_DEG = {
    "Sun": 19.0,    # Aries 19°
    "Moon": 33.0,   # Taurus 3°  → 30 + 3 = 33
}


def compute_extended_lots(planet_longs, ascendant, is_day, cusps):
    """Compute 12 extended Hellenistic / Valens Lots.

    計算 12 個擴充希臘 Lots（瓦倫斯 / 希臘傳統）

    Parameters
    ----------
    planet_longs : dict
        Planet name → ecliptic longitude (0-360).
    ascendant : float
        Ascendant longitude.
    is_day : bool
        True for day chart, False for night chart.
    cusps : list[float]
        12 whole-sign house cusps.

    Returns
    -------
    list[Lot]
        12 Lot dataclass instances with the same schema as
        ``compute_lots()`` output.
    """
    sun = planet_longs.get("Sun", 0.0)
    moon = planet_longs.get("Moon", 0.0)
    venus = planet_longs.get("Venus", 0.0)
    mars = planet_longs.get("Mars", 0.0)
    mercury = planet_longs.get("Mercury", 0.0)
    jupiter = planet_longs.get("Jupiter", 0.0)
    saturn = planet_longs.get("Saturn", 0.0)

    # Pre-compute Fortune & Spirit (needed for some Lots)
    if is_day:
        fortune = _normalize(ascendant + moon - sun)
        spirit = _normalize(ascendant + sun - moon)
    else:
        fortune = _normalize(ascendant + sun - moon)
        spirit = _normalize(ascendant + moon - sun)

    # ── Lot definitions ────────────────────────────────────────
    # Each tuple: (english_name, chinese_name, selected_longitude,
    #              formula_en, meaning_en, meaning_cn)
    # Day/night selection is applied via conditional expressions.

    # 1. Lot of Basis  基礎點
    #    Day: Asc + Fortune - Spirit | Night: Asc + Spirit - Fortune
    basis_day = _normalize(ascendant + fortune - spirit)
    basis_night = _normalize(ascendant + spirit - fortune)

    # 2. Lot of Exaltation  尊貴點
    #    Day: Asc + 19°Aries - Sun | Night: Asc + 3°Taurus - Moon
    exalt_day = _normalize(ascendant + _EXALTATION_DEG["Sun"] - sun)
    exalt_night = _normalize(ascendant + _EXALTATION_DEG["Moon"] - moon)

    # 3. Lot of Marriage  婚姻點
    #    Day: Asc + Venus - Saturn | Night: Asc + Saturn - Venus
    marriage_day = _normalize(ascendant + venus - saturn)
    marriage_night = _normalize(ascendant + saturn - venus)

    # 4. Lot of Children  子女點
    #    Day: Asc + Jupiter - Saturn | Night: Asc + Saturn - Jupiter
    children_day = _normalize(ascendant + jupiter - saturn)
    children_night = _normalize(ascendant + saturn - jupiter)

    # 5. Lot of Parents (Father)  父母點
    #    Day: Asc + Saturn - Sun | Night: Asc + Sun - Saturn
    parents_day = _normalize(ascendant + saturn - sun)
    parents_night = _normalize(ascendant + sun - saturn)

    # 6. Lot of Siblings  兄弟姐妹點
    #    Day: Asc + Saturn - Jupiter | Night: Asc + Jupiter - Saturn
    siblings_day = _normalize(ascendant + saturn - jupiter)
    siblings_night = _normalize(ascendant + jupiter - saturn)

    # 7. Lot of Friends  朋友點
    #    Day: Asc + Moon - Mercury | Night: Asc + Mercury - Moon
    friends_day = _normalize(ascendant + moon - mercury)
    friends_night = _normalize(ascendant + mercury - moon)

    # 8. Lot of Enemies  敵人點
    #    Day: Asc + Mars - Saturn | Night: Asc + Saturn - Mars
    enemies_day = _normalize(ascendant + mars - saturn)
    enemies_night = _normalize(ascendant + saturn - mars)

    # 9. Lot of Health  健康點
    #    Day: Asc + Mars - Saturn | Night: Asc + Saturn - Mars
    #    (Valens variant using Fortune)
    #    Day: Asc + Fortune - Mars | Night: Asc + Mars - Fortune
    health_day = _normalize(ascendant + fortune - mars)
    health_night = _normalize(ascendant + mars - fortune)

    # 10. Lot of Career / Achievement  事業點
    #    Day: Asc + Saturn - Sun  (same base as Valens' "Lot of Accomplishment")
    #    Variant: Asc + Mars - Mercury (Dorotheus)
    #    We use: Day: Asc + Mars - Moon | Night: Asc + Moon - Mars
    career_day = _normalize(ascendant + mars - moon)
    career_night = _normalize(ascendant + moon - mars)

    # 11. Lot of Travel  旅行點
    #    Day: Asc + Mercury - Mars | Night: Asc + Mars - Mercury
    travel_day = _normalize(ascendant + mercury - mars)
    travel_night = _normalize(ascendant + mars - mercury)

    # 12. Lot of Death  死亡點
    #    Day: Asc + Moon - 8th cusp | Night: Asc + 8th cusp - Moon
    #    Valens: Day: Asc + Saturn - Moon | Night: Asc + Moon - Saturn
    death_day = _normalize(ascendant + saturn - moon)
    death_night = _normalize(ascendant + moon - saturn)

    defs = [
        ("Lot of Basis", "基礎點",
         basis_day if is_day else basis_night,
         "Day: Asc+Fortune-Spirit / Night: Asc+Spirit-Fortune",
         "Foundation, life direction", "生命基礎、方向"),
        ("Lot of Exaltation", "尊貴點",
         exalt_day if is_day else exalt_night,
         "Day: Asc+19°Ari-Sun / Night: Asc+3°Tau-Moon",
         "Honour, eminence", "榮譽、顯赫"),
        ("Lot of Marriage", "婚姻點",
         marriage_day if is_day else marriage_night,
         "Day: Asc+Venus-Saturn / Night: Asc+Saturn-Venus",
         "Partnership, marriage", "伴侶、婚姻"),
        ("Lot of Children", "子女點",
         children_day if is_day else children_night,
         "Day: Asc+Jupiter-Saturn / Night: Asc+Saturn-Jupiter",
         "Offspring, fertility", "子嗣、生育"),
        ("Lot of Parents", "父母點",
         parents_day if is_day else parents_night,
         "Day: Asc+Saturn-Sun / Night: Asc+Sun-Saturn",
         "Father, authority figures", "父親、權威人物"),
        ("Lot of Siblings", "兄弟姐妹點",
         siblings_day if is_day else siblings_night,
         "Day: Asc+Saturn-Jupiter / Night: Asc+Jupiter-Saturn",
         "Brothers, sisters, peers", "兄弟姐妹、同輩"),
        ("Lot of Friends", "朋友點",
         friends_day if is_day else friends_night,
         "Day: Asc+Moon-Mercury / Night: Asc+Mercury-Moon",
         "Friendship, alliances", "友誼、同盟"),
        ("Lot of Enemies", "敵人點",
         enemies_day if is_day else enemies_night,
         "Day: Asc+Mars-Saturn / Night: Asc+Saturn-Mars",
         "Open enemies, adversaries", "公開敵人、對手"),
        ("Lot of Health", "健康點",
         health_day if is_day else health_night,
         "Day: Asc+Fortune-Mars / Night: Asc+Mars-Fortune",
         "Vitality, physical health", "活力、身體健康"),
        ("Lot of Career", "事業點",
         career_day if is_day else career_night,
         "Day: Asc+Mars-Moon / Night: Asc+Moon-Mars",
         "Career, achievement, praxis", "事業、成就"),
        ("Lot of Travel", "旅行點",
         travel_day if is_day else travel_night,
         "Day: Asc+Mercury-Mars / Night: Asc+Mars-Mercury",
         "Foreign travel, journeys", "遠行、旅途"),
        ("Lot of Death", "死亡點",
         death_day if is_day else death_night,
         "Day: Asc+Saturn-Moon / Night: Asc+Moon-Saturn",
         "Mortality, endings", "死亡、終結"),
    ]

    lots = []
    for name, cn, lon, formula, m_en, m_cn in defs:
        idx = _sign_idx(lon)
        lots.append(Lot(
            name=name, name_cn=cn, longitude=lon,
            sign=ZODIAC_SIGNS[idx], sign_degree=round(_sign_deg(lon), 2),
            house=_find_house(lon, cusps),
            formula_en=formula, meaning_en=m_en, meaning_cn=m_cn,
        ))
    return lots


# ============================================================
# Valens Synkrasis — Planetary Combinations (σύγκρασις)
# ============================================================
# Implements Vettius Valens' classical *planetary mixture* logic.
# Two or three planets are evaluated together considering sect,
# essential dignity, aspect type, bound ruler, and phase.

# Aspect type score modifiers
_ASPECT_SCORE = {
    "conjunction": 12,
    "trine": 10,
    "sextile": 6,
    "square": -4,
    "opposition": -8,
}

# Orb thresholds for aspect detection (degrees)
_ASPECT_ORBS = {
    0: ("conjunction", 8),
    60: ("sextile", 6),
    90: ("square", 7),
    120: ("trine", 8),
    180: ("opposition", 8),
}

# Valens-style keywords per planet pair family
_PAIR_KEYWORDS = {
    ("Sun", "Moon"): {
        "positive": ["帝王相位 / Royal Union", "光明調和 / Luminaries Harmony"],
        "negative": ["內在衝突 / Inner Conflict", "光暗拉扯 / Light-Dark Tension"],
    },
    ("Sun", "Jupiter"): {
        "positive": ["榮耀與幸運 / Glory & Fortune", "領袖光環 / Kingly Aura"],
        "negative": ["過度自信 / Overconfidence", "權勢膨脹 / Power Inflation"],
    },
    ("Sun", "Saturn"): {
        "positive": ["隱藏的統治者 / Hidden Ruler", "堅韌領導 / Steadfast Authority"],
        "negative": ["壓抑自我 / Suppressed Self", "權威受挫 / Authority Undermined"],
    },
    ("Sun", "Mars"): {
        "positive": ["戰將之光 / Warrior's Light", "果斷行動 / Decisive Action"],
        "negative": ["激烈衝突 / Fierce Conflict", "暴力傾向 / Violent Tendency"],
    },
    ("Sun", "Venus"): {
        "positive": ["優雅權威 / Graceful Authority", "藝術才華 / Artistic Brilliance"],
        "negative": ["虛榮矛盾 / Vanity Conflict", "愛與權衝突 / Love-Power Clash"],
    },
    ("Sun", "Mercury"): {
        "positive": ["聰慧領袖 / Wise Leader", "口才卓越 / Eloquent Authority"],
        "negative": ["心智緊張 / Mental Strain", "意見分歧 / Opinion Clash"],
    },
    ("Moon", "Venus"): {
        "positive": ["柔美共鳴 / Gentle Resonance", "情感豐沛 / Emotional Richness"],
        "negative": ["情緒依賴 / Emotional Dependence", "過度感性 / Over-Sensitivity"],
    },
    ("Moon", "Mars"): {
        "positive": ["情感勇氣 / Emotional Courage", "直覺行動 / Instinctive Action"],
        "negative": ["情緒暴躁 / Emotional Volatility", "衝動反應 / Impulsive Reaction"],
    },
    ("Moon", "Jupiter"): {
        "positive": ["慈悲智慧 / Compassionate Wisdom", "靈性成長 / Spiritual Growth"],
        "negative": ["情感膨脹 / Emotional Inflation", "過度樂觀 / Over-Optimism"],
    },
    ("Moon", "Saturn"): {
        "positive": ["情感堅韌 / Emotional Resilience", "自律深沉 / Disciplined Depth"],
        "negative": ["情感壓抑 / Emotional Suppression", "憂鬱傾向 / Melancholic Tendency"],
    },
    ("Moon", "Mercury"): {
        "positive": ["心智靈敏 / Mental Agility", "溝通情感 / Communicating Feelings"],
        "negative": ["思緒紛亂 / Scattered Thoughts", "焦慮多變 / Anxious Fluctuation"],
    },
    ("Mercury", "Venus"): {
        "positive": ["藝文才華 / Literary Grace", "社交魅力 / Social Charm"],
        "negative": ["膚淺表達 / Shallow Expression", "輕浮言辭 / Frivolous Words"],
    },
    ("Mercury", "Mars"): {
        "positive": ["辯論高手 / Master Debater", "策略思維 / Strategic Mind"],
        "negative": ["言語攻擊 / Verbal Aggression", "爭論不休 / Endless Argument"],
    },
    ("Mercury", "Jupiter"): {
        "positive": ["博學多聞 / Erudite Wisdom", "哲學深度 / Philosophical Depth"],
        "negative": ["誇大言辭 / Exaggerated Speech", "理論脫節 / Theory Disconnect"],
    },
    ("Mercury", "Saturn"): {
        "positive": ["精密思維 / Precise Thinking", "學術嚴謹 / Scholarly Rigor"],
        "negative": ["悲觀思維 / Pessimistic Thinking", "溝通障礙 / Communication Block"],
    },
    ("Venus", "Mars"): {
        "positive": ["熱情之愛 / Passionate Love", "創造力爆發 / Creative Burst"],
        "negative": ["愛恨交織 / Love-Hate Entangle", "慾望失控 / Desire Out of Control"],
    },
    ("Venus", "Jupiter"): {
        "positive": ["大福大愛 / Great Fortune & Love", "豐盛之美 / Abundant Beauty"],
        "negative": ["奢侈浪費 / Extravagance", "過度放縱 / Over-Indulgence"],
    },
    ("Venus", "Saturn"): {
        "positive": ["忠誠之愛 / Loyal Love", "持久之美 / Enduring Beauty"],
        "negative": ["愛情阻礙 / Love Obstacles", "情感冷漠 / Emotional Coldness"],
    },
    ("Mars", "Jupiter"): {
        "positive": ["正義之戰 / Righteous Battle", "積極擴展 / Active Expansion"],
        "negative": ["魯莽冒進 / Reckless Advance", "過度征服 / Over-Conquest"],
    },
    ("Mars", "Saturn"): {
        "positive": ["紀律戰士 / Disciplined Warrior", "堅忍不拔 / Tenacious Endurance"],
        "negative": ["破壞之力 / Destructive Force", "殘酷壓迫 / Cruel Oppression"],
    },
    ("Jupiter", "Saturn"): {
        "positive": ["智慧之柱 / Pillar of Wisdom", "社會建設 / Social Building"],
        "negative": ["擴張與限制 / Expansion vs Restriction", "信念動搖 / Faith Shaken"],
    },
}


def _get_aspect(lon_a, lon_b):
    """Detect the Ptolemaic aspect between two longitudes.

    偵測兩個黃經之間的托勒密相位

    Returns
    -------
    tuple[str, float] | None
        (aspect_name, exact_angular_distance) or None if no aspect.
    """
    diff = abs(lon_a - lon_b) % 360
    if diff > 180:
        diff = 360 - diff
    for target, (name, orb) in _ASPECT_ORBS.items():
        if abs(diff - target) <= orb:
            return name, diff
    return None


def _planet_dignity_score(planet, lon):
    """Essential dignity score for a single planet.

    行星的本質尊貴評分

    Returns
    -------
    int
        Positive for dignities, negative for debilities.
    """
    idx = _sign_idx(lon)
    score = 0
    if idx in DOMICILE.get(planet, []):
        score += 5
    if EXALTATION.get(planet) == idx:
        score += 4
    if idx in DETRIMENT.get(planet, []):
        score -= 5
    if FALL.get(planet) == idx:
        score -= 4
    return score


def _is_morning_star(planet, sun_lon, planet_lon):
    """Check if a planet rises before the Sun (morning star / φαίνων).

    判斷行星是否為晨星

    Mercury and Venus are relevant; outer planets always have
    a phase but the distinction is less meaningful.
    """
    diff = (planet_lon - sun_lon) % 360
    return diff > 180  # planet behind the Sun → rises before it


def _mutual_reception(planet_a, lon_a, planet_b, lon_b):
    """Check if two planets are in mutual reception (each in the other's domicile).

    判斷兩顆行星是否互容
    """
    idx_a = _sign_idx(lon_a)
    idx_b = _sign_idx(lon_b)
    a_in_b_dom = idx_a in DOMICILE.get(planet_b, [])
    b_in_a_dom = idx_b in DOMICILE.get(planet_a, [])
    return a_in_b_dom and b_in_a_dom


def calculate_valens_synkrasis(planet_longs, sect, bound_rulers=None):
    """Compute Valens-style planetary combinations (σύγκρασις).

    計算瓦倫斯行星組合（Synkrasis）

    Evaluates every pair of the 7 traditional planets, scoring them
    on sect, essential dignity, aspect, reception, bound ruler, and
    phase (morning / evening star).

    Parameters
    ----------
    planet_longs : dict
        Planet name → ecliptic longitude (0-360).
    sect : str
        ``"Day"`` or ``"Night"``.
    bound_rulers : dict | None
        Optional mapping of planet → bound ruler for bonus scoring.

    Returns
    -------
    list[dict]
        Each dict contains:
        - ``combination_name`` (str)
        - ``planet_a`` / ``planet_b`` (str)
        - ``aspect`` (str | None)
        - ``strength_score`` (int, 0-100)
        - ``valens_keywords`` (list[str])
        - ``interpretation_template`` (str, prompt for AI)
    """
    is_day = sect == "Day"
    sun_lon = planet_longs.get("Sun", 0.0)

    day_sect = {"Sun", "Jupiter", "Saturn"}
    night_sect = {"Moon", "Venus", "Mars"}

    planets_list = [p for p in
                    ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
                    if p in planet_longs]

    results = []
    for i, pa in enumerate(planets_list):
        for pb in planets_list[i + 1:]:
            lon_a = planet_longs[pa]
            lon_b = planet_longs[pb]

            # ── Base score (start at 50) ─────────────────────────
            score = 50

            # 1. Aspect bonus/penalty
            aspect_info = _get_aspect(lon_a, lon_b)
            aspect_name = aspect_info[0] if aspect_info else None
            if aspect_info:
                score += _ASPECT_SCORE.get(aspect_info[0], 0)

            # 2. Sect agreement
            for p in (pa, pb):
                if is_day and p in day_sect:
                    score += 3
                elif not is_day and p in night_sect:
                    score += 3
                elif p in day_sect or p in night_sect:
                    score -= 2

            # 3. Essential dignity
            score += _planet_dignity_score(pa, lon_a)
            score += _planet_dignity_score(pb, lon_b)

            # 4. Mutual reception
            if _mutual_reception(pa, lon_a, pb, lon_b):
                score += 8

            # 5. Phase bonus (morning star = stronger in Valens)
            for p, lon in ((pa, lon_a), (pb, lon_b)):
                if p in ("Mercury", "Venus"):
                    if _is_morning_star(p, sun_lon, lon):
                        score += 2

            # 6. Bound ruler bonus
            if bound_rulers:
                for p in (pa, pb):
                    if bound_rulers.get(p) == pa or bound_rulers.get(p) == pb:
                        score += 3

            # Clamp to 0-100
            score = max(0, min(100, score))

            # ── Keywords ─────────────────────────────────────────
            key = (pa, pb) if (pa, pb) in _PAIR_KEYWORDS else (pb, pa)
            pair_kw = _PAIR_KEYWORDS.get(key, {
                "positive": ["和諧共振 / Harmonious Resonance"],
                "negative": ["張力衝突 / Tension & Conflict"],
            })
            if score >= 50:
                keywords = pair_kw["positive"]
            else:
                keywords = pair_kw["negative"]

            # ── Combination name ─────────────────────────────────
            combo_name = f"{pa}–{pb}"

            # ── Interpretation template ──────────────────────────
            aspect_str = aspect_name or "no major aspect"
            template = (
                f"Interpret the Valens Synkrasis of {pa} and {pb} "
                f"({aspect_str}, strength {score}/100, "
                f"{'day' if is_day else 'night'} chart). "
                f"Keywords: {', '.join(keywords)}. "
                f"Consider sect, dignity, and phase in the analysis."
            )

            results.append({
                "combination_name": combo_name,
                "planet_a": pa,
                "planet_b": pb,
                "aspect": aspect_name,
                "strength_score": score,
                "valens_keywords": keywords,
                "interpretation_template": template,
            })

    # Sort by strength descending
    results.sort(key=lambda r: r["strength_score"], reverse=True)
    return results


# ============================================================
# Extended Hellenistic dataclass
# ============================================================

@dataclass
class HellenisticExtended:
    """Extended Hellenistic data (Lots + Synkrasis).

    擴充的希臘占星資料（Lots + 行星組合）
    """
    extended_lots: list = field(default_factory=list)
    synkrasis: list = field(default_factory=list)


def compute_hellenistic_extended(western_chart, hellenistic_chart):
    """Compute extended Hellenistic techniques from existing charts.

    從現有星盤資料計算擴充希臘占星技法

    Parameters
    ----------
    western_chart : WesternChart
        The base western chart.
    hellenistic_chart : HellenisticChart
        The standard Hellenistic chart (from ``compute_hellenistic_chart``).

    Returns
    -------
    HellenisticExtended
    """
    p_longs = hellenistic_chart.planet_longitudes
    cusps = hellenistic_chart.house_cusps
    asc = hellenistic_chart.ascendant
    is_day = hellenistic_chart.is_day_chart

    ext_lots = compute_extended_lots(p_longs, asc, is_day, cusps)

    sect_str = "Day" if is_day else "Night"
    synkrasis = calculate_valens_synkrasis(p_longs, sect_str)

    return HellenisticExtended(
        extended_lots=ext_lots,
        synkrasis=synkrasis,
    )


# ============================================================
# Streamlit rendering for extended features
# ============================================================

def render_extended_lots(lots):
    """Render the 12 extended Lots in Streamlit.

    在 Streamlit 中渲染 12 個擴充 Lots
    """
    import streamlit as st

    st.subheader("📜 Extended Hellenistic Lots / 擴充古代 Lots")
    st.caption("Based on Vettius Valens' *Anthologies* and Hellenistic tradition")

    lot_data = []
    for lot in lots:
        lot_data.append({
            "Name": f"{lot.name} ({lot.name_cn})",
            "Sign": lot.sign,
            "Degree": f"{lot.sign_degree:.2f}°",
            "House": lot.house,
            "Formula": lot.formula_en,
            "Meaning": lot.meaning_cn,
        })
    if lot_data:
        st.dataframe(lot_data, width="stretch")


def render_valens_combinations(synkrasis):
    """Render Valens Synkrasis table in Streamlit.

    在 Streamlit 中渲染瓦倫斯行星組合表
    """
    import streamlit as st

    st.subheader("⚗️ Valens Synkrasis / 瓦倫斯行星組合")
    st.caption("Planetary combination analysis following Vettius Valens' method")

    combo_data = []
    for c in synkrasis:
        combo_data.append({
            "Combination": c["combination_name"],
            "Aspect": c["aspect"] or "—",
            "Strength": f"{c['strength_score']}/100",
            "Keywords": " · ".join(c["valens_keywords"]),
        })
    if combo_data:
        st.dataframe(combo_data, width="stretch")

    # Show top 3 strongest combinations as highlights
    top3 = synkrasis[:3]
    if top3:
        st.markdown("#### 🏆 Top Combinations / 最強組合")
        for c in top3:
            emoji = "🔥" if c["strength_score"] >= 70 else "⭐"
            st.info(
                f"{emoji} **{c['combination_name']}** — "
                f"Strength: {c['strength_score']}/100 | "
                f"Aspect: {c['aspect'] or 'none'}\n\n"
                f"Keywords: {' · '.join(c['valens_keywords'])}"
            )
