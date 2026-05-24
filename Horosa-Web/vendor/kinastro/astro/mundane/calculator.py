"""
astro/mundane/calculator.py — Mundane Astrology Computation Engine

Implements core Mundane Astrology calculations:
1. Ingress Chart — Sun entry into cardinal signs (Aries/Cancer/Libra/Capricorn)
2. Eclipse Chart — Solar and Lunar eclipse positions and types
3. Great Conjunction — Jupiter-Saturn conjunctions (historical + upcoming)
4. Mundane Planet Positions — positions for any moment with house system
5. Outer Planet Transits — major outer planet sign ingresses

All compute_* functions are pure (no Streamlit dependency), supporting
@st.cache_data caching in the renderer layer.

世俗占星計算引擎（純函式，無 Streamlit 依賴）：
1. 入宮圖（太陽進入基本星座）
2. 日月食圖（日食 / 月食位置與類型）
3. 木土大合相（歷史與預測）
4. 世俗行星位置（任意時刻 + 宮位制）
5. 外行星換座過運

Sources:
- Campion, "The Book of World Horoscopes" (1988, 1996)
- Baigent et al., "Mundane Astrology" (1984)
- Lilly, "Christian Astrology" Book III (1647)
- Ptolemy, "Tetrabiblos" Book II
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, date, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

import swisseph as swe

from .constants import (
    PLANET_IDS,
    MUNDANE_PLANETS,
    PLANET_GLYPHS,
    PLANET_NAMES_ZH,
    SIGN_NAMES_EN,
    SIGN_NAMES_ZH,
    SIGN_GLYPHS,
    SIGN_ELEMENTS,
    SIGN_MODALITIES,
    INGRESS_LONGITUDES,
    INGRESS_NAMES_EN,
    INGRESS_NAMES_ZH,
    MUNDANE_ASPECTS,
    MUNDANE_HOUSES,
    OUTER_PLANET_THEMES,
    GREAT_CONJUNCTIONS,
    ECLIPSE_TYPES,
    ECLIPSE_TYPES_ZH,
)


# ─────────────────────────────────────────────────────────────────────────────
# Ephemeris path initialisation  ephemeris 路徑初始化
# ─────────────────────────────────────────────────────────────────────────────

def _init_swe() -> None:
    """Initialise Swiss Ephemeris path if available."""
    try:
        from astro.swe_init import init_swe
        init_swe()
    except Exception:
        pass  # Use built-in ephemeris if custom path not available


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Julian Day conversion  儒略日轉換
# ─────────────────────────────────────────────────────────────────────────────

def _datetime_to_jd(dt: datetime) -> float:
    """Convert a UTC datetime to Julian Day number."""
    return swe.julday(
        dt.year, dt.month, dt.day,
        dt.hour + dt.minute / 60.0 + dt.second / 3600.0,
    )


def _jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Day to UTC datetime."""
    y, mo, d, h = swe.revjul(jd)
    hour = int(h)
    minute = int((h - hour) * 60)
    second = int(((h - hour) * 60 - minute) * 60)
    return datetime(y, mo, d, hour, minute, second, tzinfo=timezone.utc)


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Sign from longitude  由黃經取星座
# ─────────────────────────────────────────────────────────────────────────────

def _sign_index_from_lon(lon: float) -> int:
    """Return 0-based zodiac sign index (0=Aries … 11=Pisces)."""
    return int(lon % 360 / 30)


def _degree_in_sign(lon: float) -> float:
    """Return degrees within the current sign (0–30)."""
    return lon % 30


# ─────────────────────────────────────────────────────────────────────────────
# Helper: House computation  宮位計算
# ─────────────────────────────────────────────────────────────────────────────

def _compute_houses(jd: float, lat: float, lon: float, hsys: str = "W") -> Tuple[List[float], float, float]:
    """
    Compute house cusps, ASC, and MC for a given Julian Day and location.

    Args:
        jd:   Julian Day (UT)
        lat:  Geographic latitude
        lon:  Geographic longitude
        hsys: House system code. 'W'=Whole Sign, 'P'=Placidus (default 'W')

    Returns:
        (cusps[1..12], asc, mc) where cusps[0] is unused.
    """
    cusps, angles = swe.houses(jd, lat, lon, hsys.encode())
    asc = angles[0]
    mc  = angles[1]
    return list(cusps), asc, mc


def _planet_house_whole_sign(planet_lon: float, asc_lon: float) -> int:
    """Return 1-based Whole Sign house number for a planet."""
    asc_sign = _sign_index_from_lon(asc_lon)
    planet_sign = _sign_index_from_lon(planet_lon)
    return ((planet_sign - asc_sign) % 12) + 1


def _planet_house_placidus(planet_lon: float, cusps: List[float]) -> int:
    """Return 1-based Placidus house number for a planet.

    House i spans from cusps[i] to cusps[i+1], where cusps[13] wraps
    back to cusps[1] (house 12 spans cusps[12] → cusps[1]).
    """
    pl = planet_lon % 360
    for i in range(12, 0, -1):
        cusp_start = cusps[i] % 360
        # cusp_end: house 12 wraps to cusp[1]; all others go to cusp[i+1]
        next_idx = (i % 12) + 1
        cusp_end = cusps[next_idx] % 360
        if cusp_end > cusp_start:
            if cusp_start <= pl < cusp_end:
                return i
        else:
            # Wraps around 0°/360° boundary
            if pl >= cusp_start or pl < cusp_end:
                return i
    return 1


# ─────────────────────────────────────────────────────────────────────────────
# Data Classes  資料類別
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class MundanePlanet:
    """Position data for one planet in a Mundane chart."""
    name: str             # e.g. "Jupiter"
    longitude: float      # Ecliptic longitude 0–360°
    latitude: float       # Ecliptic latitude
    sign_index: int       # 0–11
    sign_en: str          # "Aries" etc.
    sign_zh: str          # "牡羊" etc.
    sign_glyph: str       # "♈" etc.
    degree_in_sign: float # 0–30°
    house: int            # 1–12
    is_retrograde: bool
    glyph: str            # Planet glyph "♃" etc.
    name_zh: str          # Chinese planet name


@dataclass
class MundaneAspect:
    """An aspect between two planets in a Mundane chart."""
    planet1: str
    planet2: str
    angle: float          # Actual angular separation
    aspect_name: str      # "Conjunction" etc.
    aspect_zh: str        # "合相" etc.
    orb: float            # Deviation from exact
    applying: bool        # True = applying, False = separating
    color: str            # Hex colour


@dataclass
class MundaneChart:
    """Complete Mundane chart (Ingress or Moment chart)."""
    chart_type: str             # "ingress_aries" / "eclipse_solar" / "moment"
    chart_type_label_en: str
    chart_type_label_zh: str
    jd: float                   # Julian Day (UT)
    utc_datetime: datetime
    latitude: float
    longitude: float
    location_name: str
    house_system: str           # "W" or "P"
    asc: float                  # Ascendant longitude
    mc: float                   # Midheaven longitude
    cusps: List[float]          # 12 house cusps (1-based index)
    planets: Dict[str, MundanePlanet]
    aspects: List[MundaneAspect]
    # Ingress-specific
    ingress_type: Optional[str] = None   # "aries"/"cancer"/"libra"/"capricorn"
    year: Optional[int] = None


@dataclass
class EclipseInfo:
    """Information about a solar or lunar eclipse."""
    eclipse_kind: str        # "solar" or "lunar"
    eclipse_type_code: int   # swe ECL_* constant
    eclipse_type_en: str     # "Total" / "Annular" / "Partial" etc.
    eclipse_type_zh: str
    jd_maximum: float        # JD of maximum eclipse
    utc_datetime: datetime
    saros_number: Optional[int]
    sign_index: int          # Sign of the eclipse body (Sun/Moon)
    sign_en: str
    sign_zh: str
    longitude: float         # Ecliptic longitude at maximum
    chart: Optional[MundaneChart] = None


@dataclass
class GreatConjunction:
    """A Jupiter-Saturn conjunction event."""
    year: int
    month: int
    day: int
    longitude: float
    sign_index: int
    sign_en: str
    sign_zh: str
    element: str
    notes_zh: str
    notes_en: str
    is_future: bool


# ─────────────────────────────────────────────────────────────────────────────
# Core: Compute planet positions for a JD  計算行星位置
# ─────────────────────────────────────────────────────────────────────────────

def _compute_planet_positions(
    jd: float,
    lat: float,
    lon: float,
    house_system: str = "W",
    sidereal: bool = False,
) -> Tuple[Dict[str, MundanePlanet], List[MundaneAspect], float, float, List[float]]:
    """
    Calculate all Mundane planet positions, aspects, ASC, MC, and house cusps.

    Returns (planets_dict, aspects_list, asc, mc, cusps).
    """
    _init_swe()

    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    if sidereal:
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        flags |= swe.FLG_SIDEREAL

    # Compute house cusps
    cusps, asc, mc = _compute_houses(jd, lat, lon, house_system)

    # Compute planet positions
    planets: Dict[str, MundanePlanet] = {}
    for name, pid in PLANET_IDS.items():
        try:
            result, _ = swe.calc_ut(jd, pid, flags)
            pl_lon = result[0]
            pl_lat = result[1]
            speed  = result[3]

            sign_idx = _sign_index_from_lon(pl_lon)
            if house_system == "W":
                house = _planet_house_whole_sign(pl_lon, asc)
            else:
                house = _planet_house_placidus(pl_lon, cusps)

            planets[name] = MundanePlanet(
                name=name,
                longitude=pl_lon,
                latitude=pl_lat,
                sign_index=sign_idx,
                sign_en=SIGN_NAMES_EN[sign_idx],
                sign_zh=SIGN_NAMES_ZH[sign_idx],
                sign_glyph=SIGN_GLYPHS[sign_idx],
                degree_in_sign=_degree_in_sign(pl_lon),
                house=house,
                is_retrograde=(speed < 0),
                glyph=PLANET_GLYPHS.get(name, ""),
                name_zh=PLANET_NAMES_ZH.get(name, name),
            )
        except Exception:
            pass

    # Compute aspects
    aspects: List[MundaneAspect] = []
    planet_names = list(planets.keys())
    for i, p1 in enumerate(planet_names):
        for p2 in planet_names[i + 1:]:
            lon1 = planets[p1].longitude
            lon2 = planets[p2].longitude
            diff = abs(lon1 - lon2) % 360
            if diff > 180:
                diff = 360 - diff

            for asp in MUNDANE_ASPECTS:
                orb = abs(diff - asp["angle"])
                if orb <= asp["orb"]:
                    # Determine applying/separating
                    speed1 = 0.0
                    speed2 = 0.0
                    try:
                        r1, _ = swe.calc_ut(jd, PLANET_IDS[p1], flags)
                        r2, _ = swe.calc_ut(jd, PLANET_IDS[p2], flags)
                        speed1 = r1[3]
                        speed2 = r2[3]
                    except Exception:
                        pass
                    applying = (speed1 - speed2) * (lon1 - lon2) < 0

                    aspects.append(MundaneAspect(
                        planet1=p1,
                        planet2=p2,
                        angle=diff,
                        aspect_name=asp["name"],
                        aspect_zh=asp["name_zh"],
                        orb=orb,
                        applying=applying,
                        color=asp["color"],
                    ))
                    break  # Only record closest matching aspect

    return planets, aspects, asc, mc, cusps


# ─────────────────────────────────────────────────────────────────────────────
# Ingress Chart  入宮圖計算
# ─────────────────────────────────────────────────────────────────────────────

def _find_ingress_jd(year: int, ingress_type: str) -> float:
    """
    Find the Julian Day of the Sun's entry into the given cardinal sign for *year*.

    Uses swe.solcross_ut for precision.

    Args:
        year:         Gregorian year
        ingress_type: "aries" | "cancer" | "libra" | "capricorn"

    Returns:
        Julian Day (UT) of the ingress moment.
    """
    _init_swe()
    target_lon = INGRESS_LONGITUDES[ingress_type]

    # Approximate starting JD (slightly before expected ingress)
    approx_months = {"aries": 3, "cancer": 6, "libra": 9, "capricorn": 12}
    month = approx_months[ingress_type]
    jd_start = swe.julday(year, month, 1, 0.0)

    # Search forward up to 40 days for Sun crossing target longitude
    jd_crossing = swe.solcross_ut(target_lon, jd_start, swe.FLG_SWIEPH)
    return jd_crossing


def compute_ingress_chart(
    year: int,
    ingress_type: str = "aries",
    latitude: float = 0.0,
    longitude: float = 0.0,
    location_name: str = "Global",
    house_system: str = "W",
    sidereal: bool = False,
) -> MundaneChart:
    """
    Compute an Ingress Chart for the Sun's entry into a cardinal sign.

    Args:
        year:          The year for the ingress.
        ingress_type:  "aries" | "cancer" | "libra" | "capricorn".
        latitude:      Location latitude (0 = equatorial / global view).
        longitude:     Location longitude.
        location_name: Display name for the location.
        house_system:  "W" (Whole Sign) or "P" (Placidus).
        sidereal:      Use sidereal zodiac (Lahiri ayanamsa) if True.

    Returns:
        MundaneChart with full planet positions and aspects.
    """
    jd = _find_ingress_jd(year, ingress_type)
    utc_dt = _jd_to_datetime(jd)

    planets, aspects, asc, mc, cusps = _compute_planet_positions(
        jd, latitude, longitude, house_system, sidereal
    )

    return MundaneChart(
        chart_type=f"ingress_{ingress_type}",
        chart_type_label_en=INGRESS_NAMES_EN[ingress_type],
        chart_type_label_zh=INGRESS_NAMES_ZH[ingress_type],
        jd=jd,
        utc_datetime=utc_dt,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        house_system=house_system,
        asc=asc,
        mc=mc,
        cusps=cusps,
        planets=planets,
        aspects=aspects,
        ingress_type=ingress_type,
        year=year,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Eclipse Chart  日月食計算
# ─────────────────────────────────────────────────────────────────────────────

def _find_next_eclipse(jd_start: float, eclipse_kind: str, backward: bool = False) -> EclipseInfo:
    """
    Find the next (or previous) solar or lunar eclipse from jd_start.

    Args:
        jd_start:     Search start Julian Day.
        eclipse_kind: "solar" or "lunar".
        backward:     If True, search backward in time.

    Returns:
        EclipseInfo with basic eclipse details (no chart attached).
    """
    _init_swe()
    flag = swe.ECL_ALLTYPES_SOLAR if eclipse_kind == "solar" else swe.ECL_ALLTYPES_LUNAR

    if eclipse_kind == "solar":
        if backward:
            result = swe.sol_eclipse_when_glob(jd_start, flag | swe.ECL_BACKWARDS, False)
        else:
            result = swe.sol_eclipse_when_glob(jd_start, flag, False)
        # result: (retval, tret) where tret[0] = JD of maximum
        ec_type_code = result[0]
        jd_max = result[1][0]
    else:
        if backward:
            result = swe.lun_eclipse_when(jd_start, flag | swe.ECL_BACKWARDS, False)
        else:
            result = swe.lun_eclipse_when(jd_start, flag, False)
        ec_type_code = result[0]
        jd_max = result[1][0]

    utc_dt = _jd_to_datetime(jd_max)

    # Get the body's position at maximum
    body_id = swe.SUN if eclipse_kind == "solar" else swe.MOON
    try:
        pos, _ = swe.calc_ut(jd_max, body_id, swe.FLG_SWIEPH)
        ecl_lon = pos[0]
    except Exception:
        ecl_lon = 0.0

    sign_idx = _sign_index_from_lon(ecl_lon)

    ec_type_en = ECLIPSE_TYPES.get(ec_type_code, "Unknown")
    ec_type_zh = ECLIPSE_TYPES_ZH.get(ec_type_code, "未知")

    return EclipseInfo(
        eclipse_kind=eclipse_kind,
        eclipse_type_code=ec_type_code,
        eclipse_type_en=ec_type_en,
        eclipse_type_zh=ec_type_zh,
        jd_maximum=jd_max,
        utc_datetime=utc_dt,
        saros_number=None,
        sign_index=sign_idx,
        sign_en=SIGN_NAMES_EN[sign_idx],
        sign_zh=SIGN_NAMES_ZH[sign_idx],
        longitude=ecl_lon,
        chart=None,
    )


def compute_eclipse_chart(
    year: int,
    month: int,
    eclipse_kind: str = "solar",
    latitude: float = 0.0,
    longitude: float = 0.0,
    location_name: str = "Global",
    house_system: str = "W",
    search_forward: bool = True,
) -> Tuple[EclipseInfo, MundaneChart]:
    """
    Compute the next (or nearest) solar/lunar eclipse from a given year/month,
    and build the full Mundane chart at that moment.

    Args:
        year, month:   Start of search window.
        eclipse_kind:  "solar" or "lunar".
        latitude/longitude: Location for house calculation.
        location_name: Display name.
        house_system:  "W" or "P".
        search_forward: True = search forward in time.

    Returns:
        (EclipseInfo, MundaneChart) tuple.
    """
    _init_swe()
    jd_start = swe.julday(year, month, 1, 12.0)

    eclipse_info = _find_next_eclipse(jd_start, eclipse_kind, backward=not search_forward)

    planets, aspects, asc, mc, cusps = _compute_planet_positions(
        eclipse_info.jd_maximum, latitude, longitude, house_system
    )

    dt = eclipse_info.utc_datetime
    label_en = f"{eclipse_info.eclipse_type_en} {eclipse_kind.capitalize()} Eclipse"
    label_zh = f"{eclipse_info.eclipse_type_zh}{'日食' if eclipse_kind == 'solar' else '月食'}"

    chart = MundaneChart(
        chart_type=f"eclipse_{eclipse_kind}",
        chart_type_label_en=label_en,
        chart_type_label_zh=label_zh,
        jd=eclipse_info.jd_maximum,
        utc_datetime=dt,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        house_system=house_system,
        asc=asc,
        mc=mc,
        cusps=cusps,
        planets=planets,
        aspects=aspects,
    )

    eclipse_info.chart = chart
    return eclipse_info, chart


# ─────────────────────────────────────────────────────────────────────────────
# Great Conjunctions  木土大合相
# ─────────────────────────────────────────────────────────────────────────────

def _get_element_for_sign(sign_index: int) -> str:
    """Return the element string for a sign index."""
    return SIGN_ELEMENTS[sign_index]


def get_great_conjunctions_timeline(
    start_year: int = 1800,
    end_year: int = 2070,
) -> List[GreatConjunction]:
    """
    Return the list of Jupiter-Saturn Great Conjunctions between start_year and end_year.

    Combines hard-coded historical data from GREAT_CONJUNCTIONS with any
    approximate future events. For years up to 2060, data is pre-computed.

    Args:
        start_year: Minimum year (inclusive).
        end_year:   Maximum year (inclusive).

    Returns:
        List of GreatConjunction sorted by year.
    """
    today_year = datetime.now().year
    result: List[GreatConjunction] = []

    for gc in GREAT_CONJUNCTIONS:
        yr = gc["year"]
        if not (start_year <= yr <= end_year):
            continue
        sign_idx = gc["sign_index"]
        elem = _get_element_for_sign(sign_idx)
        result.append(GreatConjunction(
            year=yr,
            month=gc["month"],
            day=gc["day"],
            longitude=gc["longitude"],
            sign_index=sign_idx,
            sign_en=SIGN_NAMES_EN[sign_idx],
            sign_zh=SIGN_NAMES_ZH[sign_idx],
            element=elem,
            notes_zh=gc["notes_zh"],
            notes_en=gc["notes_en"],
            is_future=(yr > today_year),
        ))

    result.sort(key=lambda x: x.year)
    return result


def compute_next_great_conjunction(from_year: Optional[int] = None) -> Optional[GreatConjunction]:
    """
    Return the next (future) Great Conjunction from from_year.

    Args:
        from_year: Start year to search from (defaults to current year).

    Returns:
        GreatConjunction or None if no future conjunction is in the dataset.
    """
    if from_year is None:
        from_year = datetime.now().year

    for gc in sorted(GREAT_CONJUNCTIONS, key=lambda x: x["year"]):
        if gc["year"] >= from_year:
            sign_idx = gc["sign_index"]
            return GreatConjunction(
                year=gc["year"],
                month=gc["month"],
                day=gc["day"],
                longitude=gc["longitude"],
                sign_index=sign_idx,
                sign_en=SIGN_NAMES_EN[sign_idx],
                sign_zh=SIGN_NAMES_ZH[sign_idx],
                element=_get_element_for_sign(sign_idx),
                notes_zh=gc["notes_zh"],
                notes_en=gc["notes_en"],
                is_future=(gc["year"] > datetime.now().year),
            )
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Current Outer Planet Positions  當前外行星位置
# ─────────────────────────────────────────────────────────────────────────────

def compute_current_outer_planets(
    year: int,
    month: int,
    day: int,
    hour: float = 12.0,
) -> Dict[str, MundanePlanet]:
    """
    Compute current positions of outer planets (Jupiter, Saturn, Uranus, Neptune, Pluto).

    Used for the 'World Trends Overview' tab.

    Args:
        year, month, day: Date.
        hour:             UT hour (default noon).

    Returns:
        Dict of planet_name → MundanePlanet (house=0, global chart).
    """
    _init_swe()
    jd = swe.julday(year, month, day, hour)

    outer_planets = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    result: Dict[str, MundanePlanet] = {}

    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    for name in outer_planets:
        pid = PLANET_IDS[name]
        try:
            pos, _ = swe.calc_ut(jd, pid, flags)
            lon = pos[0]
            lat = pos[1]
            speed = pos[3]
            sign_idx = _sign_index_from_lon(lon)

            result[name] = MundanePlanet(
                name=name,
                longitude=lon,
                latitude=lat,
                sign_index=sign_idx,
                sign_en=SIGN_NAMES_EN[sign_idx],
                sign_zh=SIGN_NAMES_ZH[sign_idx],
                sign_glyph=SIGN_GLYPHS[sign_idx],
                degree_in_sign=_degree_in_sign(lon),
                house=0,  # Global view — no specific location
                is_retrograde=(speed < 0),
                glyph=PLANET_GLYPHS.get(name, ""),
                name_zh=PLANET_NAMES_ZH.get(name, name),
            )
        except Exception:
            pass

    return result


# ─────────────────────────────────────────────────────────────────────────────
# National Chart: Ingress + Outer Planet transits for a specific country
# ─────────────────────────────────────────────────────────────────────────────

def compute_national_mundane(
    year: int,
    country_key: str,
    country_data: Tuple[str, float, float, float],
    ingress_type: str = "aries",
    house_system: str = "W",
) -> MundaneChart:
    """
    Compute the Mundane Ingress chart for a specific country/capital location.

    Args:
        year:           Year for the ingress.
        country_key:    Country key from COUNTRY_CAPITALS.
        country_data:   (name_zh, lat, lon, tz) tuple.
        ingress_type:   "aries" | "cancer" | "libra" | "capricorn".
        house_system:   "W" or "P".

    Returns:
        MundaneChart computed for the country's capital coordinates.
    """
    name_zh, lat, lon, tz = country_data
    return compute_ingress_chart(
        year=year,
        ingress_type=ingress_type,
        latitude=lat,
        longitude=lon,
        location_name=f"{name_zh} ({country_key})",
        house_system=house_system,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Moment Chart  任意時刻世俗圖
# ─────────────────────────────────────────────────────────────────────────────

def compute_moment_chart(
    year: int,
    month: int,
    day: int,
    hour: float,
    minute: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    house_system: str = "W",
    sidereal: bool = False,
) -> MundaneChart:
    """
    Compute a Mundane chart for any arbitrary moment (e.g. event time).

    Args:
        year, month, day: Date.
        hour, minute:     Time (UT).
        latitude/longitude: Location.
        location_name:    Display name.
        house_system:     "W" or "P".
        sidereal:         Use sidereal zodiac if True.

    Returns:
        MundaneChart.
    """
    _init_swe()
    jd = swe.julday(year, month, day, hour + minute / 60.0)
    utc_dt = _jd_to_datetime(jd)

    planets, aspects, asc, mc, cusps = _compute_planet_positions(
        jd, latitude, longitude, house_system, sidereal
    )

    return MundaneChart(
        chart_type="moment",
        chart_type_label_en="Event/Moment Chart",
        chart_type_label_zh="事件星盤",
        jd=jd,
        utc_datetime=utc_dt,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        house_system=house_system,
        asc=asc,
        mc=mc,
        cusps=cusps,
        planets=planets,
        aspects=aspects,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Format helpers for AI prompt generation
# ─────────────────────────────────────────────────────────────────────────────

def format_mundane_chart_for_prompt(chart: MundaneChart) -> str:
    """
    Format a MundaneChart into a plain-text string suitable for AI analysis.

    Returns a structured text summary of the chart.
    """
    lines = [
        f"=== {chart.chart_type_label_zh} / {chart.chart_type_label_en} ===",
        f"Date/Time (UTC): {chart.utc_datetime.strftime('%Y-%m-%d %H:%M')}",
        f"Location: {chart.location_name} ({chart.latitude:.2f}°N, {chart.longitude:.2f}°E)",
        f"House System: {'Whole Sign 整宮' if chart.house_system == 'W' else 'Placidus'}",
        f"ASC: {chart.asc:.2f}° {SIGN_NAMES_EN[_sign_index_from_lon(chart.asc)]}",
        f"MC:  {chart.mc:.2f}° {SIGN_NAMES_EN[_sign_index_from_lon(chart.mc)]}",
        "",
        "--- Planet Positions 行星位置 ---",
    ]

    for name, pl in chart.planets.items():
        retro = " (R)" if pl.is_retrograde else ""
        lines.append(
            f"  {pl.glyph} {name} ({pl.name_zh}): "
            f"{pl.degree_in_sign:.1f}° {pl.sign_en} ({pl.sign_zh}){retro}, "
            f"House {pl.house}"
        )

    lines.extend(["", "--- Major Aspects 主要相位 ---"])
    for asp in sorted(chart.aspects, key=lambda a: a.orb)[:15]:
        applying = "applying 趨近" if asp.applying else "separating 離散"
        lines.append(
            f"  {asp.planet1} {asp.aspect_name} ({asp.aspect_zh}) {asp.planet2} "
            f"[orb {asp.orb:.2f}°, {applying}]"
        )

    if chart.ingress_type:
        lines.append(f"\nIngress Type: {INGRESS_NAMES_EN.get(chart.ingress_type, '')}")
        lines.append(f"入宮類型: {INGRESS_NAMES_ZH.get(chart.ingress_type, '')}")

    return "\n".join(lines)
