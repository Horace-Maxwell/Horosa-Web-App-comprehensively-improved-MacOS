"""
astro/andean/calculator.py — Andean Chart Calculator
=====================================================

Pure computation functions (no Streamlit dependency) for the Andean / Inca
astrology module.

Core calculations:
  1. compute_andean_chart() — main entry point, decorated with @st.cache_data
  2. _compute_mayu_rise_transit_set() — galactic-plane rise / meridian / set times
  3. _compute_dark_constellation_visibility() — which Yana Phuyu are "alive"
     (above horizon, away from Sun) at the birth moment
  4. _compute_planet_constellation_proximity() — angular distance from each planet
     to each dark constellation's anchor point
  5. _compute_birth_guardian() — seasonal animal guardian from birth month
  6. _compute_heliacal_status() — simplified heliacal rising / setting flags for
     the Pleiades (Collca) and other bright markers

Astronomy backend: pyswisseph for planetary positions + manual galactic-coordinate
transforms (no dependency on astropy to keep the package lightweight).

Galactic coordinate transform (J2000):
  NGP: RA = 192.859508°, Dec = 27.128336°
  Ascending node of galactic equator: l_Ω = 122.932°
  Reference: Murray (1989) A&A 218, 325–329
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from .models import (
    ANDEAN_BRIGHT_MARKERS,
    ANDEAN_DARK_CONSTELLATIONS,
    BrightMarker,
    DarkConstellation,
)
from .constants import (
    HELIACAL_ARC_DEG,
    HORIZON_ALT_DEG,
    MONTHLY_GUARDIAN,
    ANDEAN_THEME,
)


# ─────────────────────────────────────────────────────────────────────────────
# Galactic coordinate transform constants (J2000)
# ─────────────────────────────────────────────────────────────────────────────

_NGP_RA  = math.radians(192.859508)
_NGP_DEC = math.radians(27.128336)
_L_NCP   = math.radians(122.932)    # galactic longitude of the NCP


def _radec_to_galactic(ra_deg: float, dec_deg: float) -> Tuple[float, float]:
    """Convert equatorial (RA, Dec) J2000 to galactic (l, b) in degrees."""
    ra  = math.radians(ra_deg)
    dec = math.radians(dec_deg)

    sin_b = (math.sin(dec) * math.sin(_NGP_DEC)
             + math.cos(dec) * math.cos(_NGP_DEC) * math.cos(ra - _NGP_RA))
    b = math.degrees(math.asin(max(-1.0, min(1.0, sin_b))))

    x = math.cos(dec) * math.sin(ra - _NGP_RA)
    y = (math.sin(dec) * math.cos(_NGP_DEC)
         - math.cos(dec) * math.sin(_NGP_DEC) * math.cos(ra - _NGP_RA))
    l = (math.degrees(_L_NCP) - math.degrees(math.atan2(x, y))) % 360.0
    return l, b


def _galactic_to_radec(l_deg: float, b_deg: float) -> Tuple[float, float]:
    """Convert galactic (l, b) to equatorial (RA, Dec) J2000 in degrees."""
    l   = math.radians(l_deg)
    b   = math.radians(b_deg)
    lncp = _L_NCP

    sin_dec = (math.sin(b) * math.sin(_NGP_DEC)
               + math.cos(b) * math.cos(_NGP_DEC) * math.sin(lncp - l))
    dec = math.degrees(math.asin(max(-1.0, min(1.0, sin_dec))))

    x = math.cos(b) * math.cos(lncp - l)
    y = (math.sin(b) * math.cos(_NGP_DEC)
         - math.cos(b) * math.sin(_NGP_DEC) * math.sin(lncp - l))
    ra = (math.degrees(math.atan2(x, y)) + math.degrees(_NGP_RA)) % 360.0
    return ra, dec


# ─────────────────────────────────────────────────────────────────────────────
# Helper: altitude of an equatorial point from a given location and JD
# ─────────────────────────────────────────────────────────────────────────────

def _radec_altitude(ra_deg: float, dec_deg: float, jd_ut: float,
                    lat_deg: float, lon_deg: float) -> float:
    """Return the altitude (degrees) of (RA, Dec) for a given observer and JD.

    Uses sidereal time + standard spherical-astronomy formula.
    """
    # Greenwich mean sidereal time (degrees)
    gmst_deg = (swe.sidtime(jd_ut) * 15.0) % 360.0
    # Local apparent sidereal time
    last_deg = (gmst_deg + lon_deg) % 360.0
    # Hour angle
    ha = math.radians((last_deg - ra_deg) % 360.0)
    dec = math.radians(dec_deg)
    lat = math.radians(lat_deg)

    sin_alt = (math.sin(dec) * math.sin(lat)
               + math.cos(dec) * math.cos(lat) * math.cos(ha))
    alt_deg = math.degrees(math.asin(max(-1.0, min(1.0, sin_alt))))
    return alt_deg


# ─────────────────────────────────────────────────────────────────────────────
# Helper: angular separation between two equatorial points
# ─────────────────────────────────────────────────────────────────────────────

def _angular_sep(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    """Return great-circle angular separation (degrees) between two points."""
    ra1r, dec1r = math.radians(ra1), math.radians(dec1)
    ra2r, dec2r = math.radians(ra2), math.radians(dec2)
    cos_sep = (math.sin(dec1r) * math.sin(dec2r)
               + math.cos(dec1r) * math.cos(dec2r) * math.cos(ra1r - ra2r))
    return math.degrees(math.acos(max(-1.0, min(1.0, cos_sep))))


# ─────────────────────────────────────────────────────────────────────────────
# Data classes for the chart result
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AndeanPlanet:
    """One planet's position in the Andean chart context."""

    name: str                        # "Sun", "Moon", etc.
    name_zh: str
    longitude: float                 # ecliptic longitude (degrees)
    latitude: float                  # ecliptic latitude (degrees)
    sign: str                        # Western zodiac sign name
    sign_degree: float
    retrograde: bool
    ra: float                        # equatorial RA (degrees J2000)
    dec: float                       # equatorial Dec (degrees J2000)
    galactic_l: float
    galactic_b: float
    altitude: float                  # altitude above horizon at birth moment
    nearest_dark_constellation: str  # key of nearest dark cloud
    angle_to_dark_constellation: float  # angular separation (degrees)


@dataclass
class DarkConstellationStatus:
    """Visibility & relationship status of one dark constellation at birth."""

    key: str
    name_qu: str
    name_zh: str
    name_en: str
    is_alive: bool                   # above horizon and away from Sun
    altitude: float                  # altitude of anchor point
    angular_from_sun: float          # degrees from Sun
    myth_zh: str
    myth_en: str
    agro_omen_zh: str
    agro_omen_en: str
    meaning_zh: str
    meaning_en: str
    cross_refs: Dict[str, str]
    poly_l: List[float]
    poly_b: List[float]


@dataclass
class AndeanChart:
    """Complete Andean / Inca astrology chart result."""

    # ── Input ──
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str

    # ── Derived ──
    julian_day: float

    # ── Birth guardian ──
    birth_guardian_qu: str
    birth_guardian_zh: str
    birth_guardian_en: str

    # ── Dark constellation statuses ──
    dark_constellations: List[DarkConstellationStatus]

    # ── Planets ──
    planets: List[AndeanPlanet]

    # ── Sun & Moon galactic coords ──
    sun_ra: float
    sun_dec: float
    sun_galactic_l: float
    sun_galactic_b: float
    moon_ra: float
    moon_dec: float
    moon_galactic_l: float
    moon_galactic_b: float

    # ── Mayu (Milky Way band) rendering data ──
    mayu_longitudes: List[float]
    mayu_latitudes: List[float]

    # ── Bright markers ──
    bright_markers: List[dict]

    # ── Heliacal status of Collca (Pleiades) ──
    collca_heliacal_phase: str
    collca_heliacal_phase_zh: str

    # ── Convenience ──
    @property
    def dark_constellations_alive(self) -> List[DarkConstellationStatus]:
        return [d for d in self.dark_constellations if d.is_alive]


# ─────────────────────────────────────────────────────────────────────────────
# Planet helpers
# ─────────────────────────────────────────────────────────────────────────────

_PLANET_IDS = [
    (swe.SUN,     "Sun",     "太陽"),
    (swe.MOON,    "Moon",    "月亮"),
    (swe.MERCURY, "Mercury", "水星"),
    (swe.VENUS,   "Venus",   "金星"),
    (swe.MARS,    "Mars",    "火星"),
    (swe.JUPITER, "Jupiter", "木星"),
    (swe.SATURN,  "Saturn",  "土星"),
]

_SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def _sign_name(lon: float) -> Tuple[str, float]:
    idx = int(lon / 30.0) % 12
    return _SIGN_NAMES[idx], lon % 30.0


# ─────────────────────────────────────────────────────────────────────────────
# Main computation
# ─────────────────────────────────────────────────────────────────────────────

def compute_andean_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
) -> AndeanChart:
    """Compute the complete Andean / Inca astrology chart.

    Pure function — no Streamlit dependency; decorated with @st.cache_data
    in the Streamlit entry-point layer (app.py uses the cached wrapper).

    Args:
        year, month, day:  Birth date (civil calendar).
        hour, minute:      Local birth time.
        timezone:          UTC offset in hours (e.g. −5 for Peru/Colombia).
        latitude:          Observer latitude (degrees; negative = south).
        longitude:         Observer longitude (degrees; negative = west).
        location_name:     Human-readable place name.

    Returns:
        AndeanChart dataclass with complete chart data.
    """
    swe.set_ephe_path("")

    # ── Julian Day (UT) ──
    ut_hour = hour + minute / 60.0 - timezone
    jd_ut = swe.julday(year, month, day, ut_hour)

    # ── Planetary positions ──
    planets: List[AndeanPlanet] = []
    sun_ra = sun_dec = sun_gl = sun_gb = 0.0
    moon_ra = moon_dec = moon_gl = moon_gb = 0.0

    for swe_id, name_en, name_zh in _PLANET_IDS:
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_EQUATORIAL
        result, _ = swe.calc_ut(jd_ut, swe_id, flags)
        ra, dec_val = result[0], result[1]
        spd = result[3]
        retrograde = (swe_id not in (swe.SUN, swe.MOON)) and (spd < 0)

        # Ecliptic position for sign
        ecl_flags = swe.FLG_SWIEPH
        ecl_result, _ = swe.calc_ut(jd_ut, swe_id, ecl_flags)
        ecl_lon, ecl_lat = ecl_result[0], ecl_result[1]
        sign, sign_deg = _sign_name(ecl_lon)
        gl, gb = _radec_to_galactic(ra, dec_val)
        alt = _radec_altitude(ra, dec_val, jd_ut, latitude, longitude)

        if swe_id == swe.SUN:
            sun_ra, sun_dec, sun_gl, sun_gb = ra, dec_val, gl, gb
        elif swe_id == swe.MOON:
            moon_ra, moon_dec, moon_gl, moon_gb = ra, dec_val, gl, gb

        planets.append(AndeanPlanet(
            name=name_en,
            name_zh=name_zh,
            longitude=ecl_lon,
            latitude=ecl_lat,
            sign=sign,
            sign_degree=sign_deg,
            retrograde=retrograde,
            ra=ra,
            dec=dec_val,
            galactic_l=gl,
            galactic_b=gb,
            altitude=alt,
            nearest_dark_constellation="",
            angle_to_dark_constellation=999.0,
        ))

    # ── Dark constellation visibility ──
    dc_statuses: List[DarkConstellationStatus] = []
    for dc in ANDEAN_DARK_CONSTELLATIONS:
        anchor_ra, anchor_dec = dc.anchor_ra_dec_j2000
        alt = _radec_altitude(anchor_ra, anchor_dec, jd_ut, latitude, longitude)
        ang_from_sun = _angular_sep(anchor_ra, anchor_dec, sun_ra, sun_dec)
        is_alive = (alt >= HORIZON_ALT_DEG) and (ang_from_sun >= HELIACAL_ARC_DEG)
        poly_l = [p[0] for p in dc.galactic_bbox]
        poly_b = [p[1] for p in dc.galactic_bbox]
        dc_statuses.append(DarkConstellationStatus(
            key=dc.key,
            name_qu=dc.names.get("qu", dc.key),
            name_zh=dc.names.get("zh", ""),
            name_en=dc.names.get("en", ""),
            is_alive=is_alive,
            altitude=round(alt, 2),
            angular_from_sun=round(ang_from_sun, 2),
            myth_zh=dc.myth.get("zh", ""),
            myth_en=dc.myth.get("en", ""),
            agro_omen_zh=dc.agro_omen.get("zh", ""),
            agro_omen_en=dc.agro_omen.get("en", ""),
            meaning_zh=dc.meaning.get("zh", ""),
            meaning_en=dc.meaning.get("en", ""),
            cross_refs=dict(dc.cross_refs),
            poly_l=poly_l,
            poly_b=poly_b,
        ))

    # ── Nearest dark constellation for each planet ──
    for planet in planets:
        best_key = ""
        best_sep = 999.0
        for dc in ANDEAN_DARK_CONSTELLATIONS:
            sep = _angular_sep(planet.ra, planet.dec, *dc.anchor_ra_dec_j2000)
            if sep < best_sep:
                best_sep = sep
                best_key = dc.key
        planet.nearest_dark_constellation = best_key
        planet.angle_to_dark_constellation = round(best_sep, 2)

    # ── Birth guardian ──
    guardian = MONTHLY_GUARDIAN.get(month, {"qu": "—", "zh": "—", "en": "—"})

    # ── Milky Way band rendering data (galactic plane spine + scatter) ──
    mayu_ls: List[float] = []
    mayu_bs: List[float] = []
    for l in range(0, 361, 3):
        for b_offset in (-6, -3, 0, 3, 6):
            mayu_ls.append(float(l))
            mayu_bs.append(float(b_offset))

    # ── Bright markers ──
    bright: List[dict] = []
    for bm in ANDEAN_BRIGHT_MARKERS:
        bm_ra, bm_dec = bm.anchor_ra_dec_j2000
        bm_alt = _radec_altitude(bm_ra, bm_dec, jd_ut, latitude, longitude) if bm_ra != 0.0 else 0.0
        bm_gl, bm_gb = _radec_to_galactic(bm_ra, bm_dec) if bm_ra != 0.0 else (0.0, 0.0)
        bright.append({
            "key": bm.key,
            "name_qu": bm.names.get("qu", bm.key),
            "name_zh": bm.names.get("zh", ""),
            "name_en": bm.names.get("en", ""),
            "ra": bm_ra,
            "dec": bm_dec,
            "galactic_l": bm_gl,
            "galactic_b": bm_gb,
            "altitude": round(bm_alt, 2),
            "is_visible": bm_alt >= HORIZON_ALT_DEG,
            "meaning_zh": bm.meaning.get("zh", ""),
            "meaning_en": bm.meaning.get("en", ""),
        })

    # ── Collca (Pleiades) heliacal phase ──
    pleiades_ra, pleiades_dec = 56.75, 24.1
    pleiades_sep = _angular_sep(pleiades_ra, pleiades_dec, sun_ra, sun_dec)
    pleiades_alt = _radec_altitude(pleiades_ra, pleiades_dec, jd_ut, latitude, longitude)

    if pleiades_sep < HELIACAL_ARC_DEG:
        collca_phase = "combust"
        collca_phase_zh = "伏藏（穀倉閉合，藏糧期）"
    elif pleiades_sep < 30.0 and pleiades_alt < 0:
        collca_phase = "heliacal_rising"
        collca_phase_zh = "偕日出（穀倉開啟，播種訊號）"
    elif pleiades_alt >= HORIZON_ALT_DEG and pleiades_sep > 90.0:
        collca_phase = "visible"
        collca_phase_zh = "可見（穀倉開放，豐收吉兆）"
    else:
        collca_phase = "below_horizon"
        collca_phase_zh = "地平線下（潛藏期）"

    return AndeanChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        julian_day=jd_ut,
        birth_guardian_qu=guardian["qu"],
        birth_guardian_zh=guardian["zh"],
        birth_guardian_en=guardian["en"],
        dark_constellations=dc_statuses,
        planets=planets,
        sun_ra=sun_ra, sun_dec=sun_dec,
        sun_galactic_l=round(sun_gl, 2), sun_galactic_b=round(sun_gb, 2),
        moon_ra=moon_ra, moon_dec=moon_dec,
        moon_galactic_l=round(moon_gl, 2), moon_galactic_b=round(moon_gb, 2),
        mayu_longitudes=mayu_ls,
        mayu_latitudes=mayu_bs,
        bright_markers=bright,
        collca_heliacal_phase=collca_phase,
        collca_heliacal_phase_zh=collca_phase_zh,
    )
