"""
astro/primary_directions/calculator.py — Classical Primary Directions Engine

Implements the complete Primary Directions system following:

  1. Ptolemy, "Tetrabiblos" (c. 150 CE) — foundational Zodiacal method
  2. Regiomontanus, "Tabulae Directionum" (1490) — tabulated direction arcs
  3. Placidus de Titis, "Primum Mobile" (1657) — semi-arc Mundo method
  4. Martin Gansten, "Primary Directions: Astrology's Old Master Technique"
     (2009, Wessex Astrologer) — modern scholarly reconstruction

Two canonical methods:

  A. **Zodiacal Primary Directions** (Ptolemy/Placidus Zodiacal):
     Uses Oblique Ascension in the birth-latitude horizon system.
     Direction arc = OA(promittor) − OA(significator)
     where OA = RA − AD  and  AD = arcsin(tan δ · tan φ)
     (for above-the-horizon / diurnal arc; sign changes for nocturnal)

  B. **Placidus Mundo Primary Directions** (Mundane / Placidus Semi-Arc):
     More precise; uses the proportional position within the Placidus
     semi-arc.  The "pole of the significator" is derived from its
     fractional meridian distance, and the promittor's OA is recomputed
     with that pole.

     Semi-Arc SA = arccos(−tan δ · tan φ)    [Placidus 1657, Prop. IX]
     Meridian Distance MD = |RAMC − RA|
     Proportional factor p = MD / SA
     Pole of significator Ψ = arctan(sin(p · 90°) · tan φ)
     Arc = [RA(P) − arcsin(tan δ_P · tan Ψ)] − [RA(S) − arcsin(tan δ_S · tan Ψ)]

  Both methods support:
  - Direct directions  (significator moves forward/clockwise)
  - Converse directions (significator moves backward / counter-clockwise)
  - Aspect directions  (promittor at aspect positions)
  - Parallel of declination and Contra-parallel

  Time conversion keys:
  - Naibod (classical default): 1 year = 0.98563° of arc
  - Ptolemy: 1 year = 1.00000°
  - Solar Arc: 1 year = Sun's actual mean daily motion at birth

Public API:
    compute_primary_directions(...)  → PrimaryDirectionsResult
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from .constants import (
    PLANET_SWE_IDS,
    PLANET_NAMES_EN,
    PLANET_NAMES_ZH,
    PLANET_SYMBOLS,
    PLANET_ORDER,
    CLASSIC_PLANETS,
    ANGLE_POINTS,
    ZODIAC_SIGNS,
    SIGN_ZH,
    SIGN_SYMBOLS,
    ASPECTS,
    NAIBOD_KEY,
    PTOLEMY_KEY,
    get_event_nature,
    SIGNIFICATOR_MEANINGS,
    ASPECT_DIRECTION_MEANINGS,
    EXAMPLE_CHARTS,
)


# ──────────────────────────────────────────────────────────────
# Geometry helpers
# ──────────────────────────────────────────────────────────────

def _normalize(deg: float) -> float:
    """Reduce to [0°, 360°)."""
    return deg % 360.0


def _normalize_signed(deg: float) -> float:
    """Reduce to (−180°, 180°]."""
    d = deg % 360.0
    return d - 360.0 if d > 180.0 else d


def _arc_diff(a: float, b: float) -> float:
    """Minimum arc between two longitudes."""
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def _sign_from_lon(lon: float) -> Tuple[str, str, str, float]:
    """Return (sign_en, sign_zh, sign_symbol, degree_in_sign)."""
    idx = int(lon / 30.0) % 12
    return ZODIAC_SIGNS[idx], SIGN_ZH[idx], SIGN_SYMBOLS[idx], lon % 30.0


# ──────────────────────────────────────────────────────────────
# Equatorial position helpers
# ──────────────────────────────────────────────────────────────

def _ecliptic_to_equatorial(lon: float, lat: float = 0.0,
                             eps: float = 23.4365) -> Tuple[float, float]:
    """
    Convert ecliptic longitude/latitude to RA/Dec.

    Uses the standard spherical conversion:
      sin(Dec) = sin(lat)·cos(ε) + cos(lat)·sin(ε)·sin(lon)
      tan(RA)  = [sin(lon)·cos(ε) − tan(lat)·sin(ε)] / cos(lon)

    Args:
        lon: Ecliptic longitude (degrees).
        lat: Ecliptic latitude (degrees); 0 for points on ecliptic.
        eps: Obliquity of ecliptic (degrees).

    Returns:
        (RA, Dec) in degrees.
    """
    lo = math.radians(lon)
    la = math.radians(lat)
    e = math.radians(eps)

    sin_dec = math.sin(la) * math.cos(e) + math.cos(la) * math.sin(e) * math.sin(lo)
    # clamp for numerical safety
    sin_dec = max(-1.0, min(1.0, sin_dec))
    dec = math.degrees(math.asin(sin_dec))

    ra_y = math.sin(lo) * math.cos(e) - math.tan(la) * math.sin(e)
    ra_x = math.cos(lo)
    ra = math.degrees(math.atan2(ra_y, ra_x)) % 360.0
    return ra, dec


def _ascensional_difference(dec: float, lat: float) -> float:
    """
    Compute the Ascensional Difference (AD).

    AD = arcsin(tan δ · tan φ)
    where δ = declination, φ = geographic latitude.

    Ref: Ptolemy, Tetrabiblos II.11; Placidus, Primum Mobile, Def. IV.
    Edge cases:
      - |tan δ · tan φ| > 1: circumpolar or never-rises; return ±90°.

    Returns:
        AD in degrees (positive for planets with same-sign dec & lat).
    """
    val = math.tan(math.radians(dec)) * math.tan(math.radians(lat))
    val = max(-1.0, min(1.0, val))  # clamp for polar regions
    return math.degrees(math.asin(val))


def _oblique_ascension(ra: float, dec: float, lat: float) -> float:
    """
    Compute Oblique Ascension (OA).

    OA = RA − AD    [Ptolemy tradition, upper hemisphere]

    Returns degrees in [0, 360).
    """
    ad = _ascensional_difference(dec, lat)
    return _normalize(ra - ad)


def _oblique_descension(ra: float, dec: float, lat: float) -> float:
    """
    Compute Oblique Descension (OD).

    OD = RA + AD

    Returns degrees in [0, 360).
    """
    ad = _ascensional_difference(dec, lat)
    return _normalize(ra + ad)


def _semi_arc(dec: float, lat: float, diurnal: bool = True) -> float:
    """
    Compute Placidus Semi-Arc.

    SA_diurnal   = arccos(−tan δ · tan φ)       [0°–180°]
    SA_nocturnal = 180° − SA_diurnal

    Ref: Placidus de Titis, Primum Mobile (1657), Proposition IX.
    For polar regions where |tan δ · tan φ| > 1:
      - Circumpolar objects: SA_diurnal = 180° (always above horizon)
      - Never-rises: SA_diurnal = 0°

    Returns:
        Semi-arc in degrees.
    """
    val = -math.tan(math.radians(dec)) * math.tan(math.radians(lat))
    if val >= 1.0:
        sa_d = 0.0       # never rises
    elif val <= -1.0:
        sa_d = 180.0     # circumpolar
    else:
        sa_d = math.degrees(math.acos(val))
    return sa_d if diurnal else (180.0 - sa_d)


def _is_above_horizon(ra: float, ramc: float, dec: float, lat: float) -> bool:
    """
    Determine whether a point is above the horizon (in the diurnal arc).

    A planet is above the horizon when its RA is within its diurnal semi-arc
    of the RAMC (Midheaven's RA).

    Returns:
        True if above horizon (diurnal arc), False if below (nocturnal arc).
    """
    md = abs(_normalize_signed(ra - ramc))   # meridian distance 0–180
    sa_d = _semi_arc(dec, lat, diurnal=True)
    return md <= sa_d


def _meridian_distance(ra: float, ramc: float) -> float:
    """
    Compute Meridian Distance (MD): arc from MC (RAMC) to planet's RA.

    Returns value in [0°, 180°].
    """
    return abs(_normalize_signed(ra - ramc))


def _pole_of_significator(dec: float, lat: float, ra: float,
                           ramc: float, above: bool) -> float:
    """
    Compute the Placidus pole of a significator.

    The pole Ψ is the artificial latitude at which the significator lies
    on the equator of its Placidus house cusp.

    Formula (Placidus 1657, Gansten 2009 p. 56):
        p  = MD / SA          (proportional meridian distance, 0–1)
        Ψ  = arctan(sin(p·90°) · tan(φ))

    For the angular points (MD = 0 or SA = 0), Ψ = 0 (equatorial pole).

    Returns:
        Pole in degrees.
    """
    sa = _semi_arc(dec, lat, diurnal=above)
    if sa < 0.01:
        return 0.0
    md = _meridian_distance(ra, ramc)
    prop = min(1.0, md / sa)
    pole = math.degrees(
        math.atan(math.sin(math.radians(prop * 90.0)) * math.tan(math.radians(lat)))
    )
    return pole


def _oblique_ascension_with_pole(ra: float, dec: float, pole: float) -> float:
    """
    Compute OA using an artificial pole (Placidus Mundo method).

    OA_pole = RA − arcsin(tan δ · tan Ψ)

    Returns degrees in [0, 360).
    """
    val = math.tan(math.radians(dec)) * math.tan(math.radians(pole))
    val = max(-1.0, min(1.0, val))
    ad = math.degrees(math.asin(val))
    return _normalize(ra - ad)


# ──────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────

@dataclass
class ChartPoint:
    """A natal point with full equatorial and ecliptic data."""

    key: str
    name_en: str
    name_zh: str
    symbol: str

    # Ecliptic
    longitude: float          # 0–360° ecliptic longitude
    latitude: float = 0.0    # ecliptic latitude
    sign: str = ""
    sign_zh: str = ""
    sign_symbol: str = ""
    sign_degree: float = 0.0

    # Equatorial
    ra: float = 0.0           # Right Ascension 0–360°
    dec: float = 0.0          # Declination −90°–+90°

    # Derived
    oa: float = 0.0           # Oblique Ascension
    od: float = 0.0           # Oblique Descension
    sa_diurnal: float = 0.0   # Diurnal Semi-Arc
    sa_nocturnal: float = 0.0 # Nocturnal Semi-Arc
    md: float = 0.0           # Meridian Distance from MC
    above_horizon: bool = True

    retrograde: bool = False


@dataclass
class Direction:
    """
    A single Primary Direction event.

    Represents the moment when a directed significator contacts a promittor
    (or one of its aspect positions).
    """

    significator_key: str     # The point being directed (e.g., "AS", "SU")
    promittor_key: str        # The natal point being aspected (e.g., "SA")
    aspect_key: str           # Aspect type ("CNJ", "SQR", etc.)
    converse: bool            # True = converse direction, False = direct

    method: str               # "zodiacal" or "mundo"
    arc: float                # Direction arc in degrees

    # Time data
    time_key: str             # "naibod", "ptolemy", or "solar_arc"
    years: float              # Age at which direction perfects
    birth_date: date          # Birth date (for computing event_date)
    event_date: date          # Computed calendar date

    # Interpretive
    nature_zh: str = ""       # Classical nature of event (Chinese)
    nature_en: str = ""       # Classical nature of event (English)
    aspect_nature_zh: str = ""
    aspect_nature_en: str = ""
    sig_meaning_zh: str = ""
    sig_meaning_en: str = ""

    @property
    def direction_label_en(self) -> str:
        sig = PLANET_NAMES_EN.get(self.significator_key, self.significator_key)
        prom = PLANET_NAMES_EN.get(self.promittor_key, self.promittor_key)
        asp = next((a["name"] for a in ASPECTS if a["key"] == self.aspect_key), self.aspect_key)
        cv = " (Converse)" if self.converse else ""
        return f"{sig} directed to {asp} of {prom}{cv}"

    @property
    def direction_label_zh(self) -> str:
        sig = PLANET_NAMES_ZH.get(self.significator_key, self.significator_key)
        prom = PLANET_NAMES_ZH.get(self.promittor_key, self.promittor_key)
        asp = next((a["name_zh"] for a in ASPECTS if a["key"] == self.aspect_key), self.aspect_key)
        cv = "（逆向）" if self.converse else ""
        return f"{sig}主限至{prom}{asp}{cv}"


@dataclass
class PrimaryDirectionsResult:
    """
    Full Primary Directions analysis result.

    Contains natal chart data, all computed directions within a given age range,
    and metadata about the birth and method used.
    """

    # Natal data
    natal_points: List[ChartPoint]
    ramc: float             # Right Ascension of MC
    obliquity: float        # Ecliptic obliquity at birth

    # All computed directions, sorted by arc (ascending)
    directions: List[Direction]

    # Parameters
    method: str             # "zodiacal" or "mundo"
    time_key: str           # "naibod", "ptolemy", or "solar_arc"
    max_age: float          # Maximum age computed (years)
    include_converse: bool
    significators: List[str]
    promittors: List[str]
    include_aspects: List[str]

    # Birth info
    year: int = 0
    month: int = 0
    day: int = 0
    hour: int = 0
    minute: int = 0
    timezone: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    location_name: str = ""

    def get_point(self, key: str) -> Optional[ChartPoint]:
        for p in self.natal_points:
            if p.key == key:
                return p
        return None

    def directions_near_age(self, target_age: float, orb: float = 1.5) -> List[Direction]:
        """Return directions within orb years of a target age."""
        return [d for d in self.directions if abs(d.years - target_age) <= orb]


# ──────────────────────────────────────────────────────────────
# Position computation
# ──────────────────────────────────────────────────────────────

def _get_obliquity(jd: float) -> float:
    """Compute mean obliquity of the ecliptic using Swiss Ephemeris."""
    # swe.calc_ut with SE_ECL_NUT gives nutation/obliquity data
    eps_data, _ = swe.calc_ut(jd, swe.ECL_NUT, 0)
    return eps_data[0]  # mean obliquity in degrees


def _compute_natal_points(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float,
    latitude: float, longitude: float,
) -> Tuple[List[ChartPoint], float, float]:
    """
    Compute all natal chart points with full equatorial data.

    Returns:
        (natal_points, ramc, obliquity)
    """
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)

    obliquity = _get_obliquity(jd)

    # Placidus houses for ASC and MC
    houses, ascmc = swe.houses(jd, latitude, longitude, b"P")
    asc_lon = _normalize(ascmc[0])
    mc_lon = _normalize(ascmc[1])
    ramc = _normalize(ascmc[2])   # RAMC directly from swe

    points: List[ChartPoint] = []

    def _add_point(key: str, ecl_lon: float, ecl_lat: float = 0.0,
                   retrograde: bool = False) -> None:
        ra, dec = _ecliptic_to_equatorial(ecl_lon, ecl_lat, obliquity)
        sign_en, sign_zh, sign_sym, sdeg = _sign_from_lon(ecl_lon)
        sa_d = _semi_arc(dec, latitude, diurnal=True)
        sa_n = _semi_arc(dec, latitude, diurnal=False)
        oa = _oblique_ascension(ra, dec, latitude)
        od = _oblique_descension(ra, dec, latitude)
        above = _is_above_horizon(ra, ramc, dec, latitude)
        md = _meridian_distance(ra, ramc)
        points.append(ChartPoint(
            key=key,
            name_en=PLANET_NAMES_EN.get(key, key),
            name_zh=PLANET_NAMES_ZH.get(key, key),
            symbol=PLANET_SYMBOLS.get(key, key),
            longitude=ecl_lon,
            latitude=ecl_lat,
            sign=sign_en,
            sign_zh=sign_zh,
            sign_symbol=sign_sym,
            sign_degree=sdeg,
            ra=ra,
            dec=dec,
            oa=oa,
            od=od,
            sa_diurnal=sa_d,
            sa_nocturnal=sa_n,
            md=md,
            above_horizon=above,
            retrograde=retrograde,
        ))

    # 10 standard planets
    for key, pid in PLANET_SWE_IDS.items():
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        result, _ = swe.calc_ut(jd, pid, flags)
        ecl_lon = _normalize(result[0])
        ecl_lat = result[1]
        retro = result[3] < 0
        _add_point(key, ecl_lon, ecl_lat, retro)

    # True North Node
    result_node, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH)
    _add_point("NN", _normalize(result_node[0]), 0.0, False)

    # Ascendant (ecl lat = 0 for angles)
    _add_point("AS", asc_lon, 0.0, False)

    # Midheaven
    _add_point("MC", mc_lon, 0.0, False)

    # Descendant (opposite ASC)
    _add_point("DS", _normalize(asc_lon + 180.0), 0.0, False)

    # IC (opposite MC)
    _add_point("IC", _normalize(mc_lon + 180.0), 0.0, False)

    # Sort by standard order
    order_map = {k: i for i, k in enumerate(PLANET_ORDER)}
    points.sort(key=lambda p: order_map.get(p.key, 99))

    return points, ramc, obliquity


# ──────────────────────────────────────────────────────────────
# Aspect position helpers
# ──────────────────────────────────────────────────────────────

def _aspect_longitudes(base_lon: float, aspect_keys: List[str]) -> Dict[str, float]:
    """
    Compute the ecliptic longitudes for aspect positions of a promittor.

    For each aspect angle, returns the longitude (base ± angle).
    Conjunction = base itself.  Opposition = base + 180°, etc.

    Returns:
        Dict mapping aspect_key → ecliptic longitude of that aspect position.
    """
    result: Dict[str, float] = {}
    aspect_angles = {"CNJ": 0.0, "SXT": 60.0, "SQR": 90.0, "TRI": 120.0, "OPP": 180.0}
    for key in aspect_keys:
        if key in aspect_angles:
            # Both dexter and sinister for square/sextile/trine
            ang = aspect_angles[key]
            if ang == 0.0 or ang == 180.0:
                result[key] = _normalize(base_lon + ang)
            else:
                # Classical: dexter (forward) and sinister (backward) aspects
                # We compute both; the direction engine will handle the sign
                result[key + "_d"] = _normalize(base_lon + ang)   # sinister
                result[key + "_s"] = _normalize(base_lon - ang)   # dexter
    return result


# ──────────────────────────────────────────────────────────────
# Direction arc computation
# ──────────────────────────────────────────────────────────────

def _zodiacal_arc(
    sig: ChartPoint,
    prom_ra: float,
    prom_dec: float,
    lat: float,
    ramc: float,
    converse: bool,
) -> Optional[float]:
    """
    Compute Zodiacal Primary Direction arc.

    Method (Ptolemy / Placidus Zodiacal):
        Direct:   arc = OA(prom) − OA(sig)
        Converse: arc = OA(sig) − OA(prom)

    The OA is computed with the birth-latitude horizon system.

    Ref: Ptolemy, Tetrabiblos III.10–11; Gansten 2009, ch. 3.

    Returns:
        Arc in degrees [0°, 360°), or None if geometrically impossible.
    """
    # For significator's OA
    sig_oa = sig.oa

    # For promittor's OA (may differ from natal if it's an aspect position)
    prom_oa = _oblique_ascension(prom_ra, prom_dec, lat)

    if not converse:
        arc = _normalize(prom_oa - sig_oa)
    else:
        arc = _normalize(sig_oa - prom_oa)

    return arc


def _mundo_arc(
    sig: ChartPoint,
    prom_ra: float,
    prom_dec: float,
    lat: float,
    ramc: float,
    obliquity: float,
    converse: bool,
) -> Optional[float]:
    """
    Compute Placidus Mundo Primary Direction arc.

    Method (Placidus 1657, Gansten 2009 ch. 4):

        1. Compute the pole Ψ of the significator from its proportional
           meridian distance within its semi-arc.
        2. Compute OA of both significator and promittor using pole Ψ.
        3. arc = OA_Ψ(prom) − OA_Ψ(sig)   (direct)
                 OA_Ψ(sig) − OA_Ψ(prom)   (converse)

    This is the most accurate traditional method for Mundo directions.

    Returns:
        Arc in degrees [0°, 360°), or None if not applicable.
    """
    # Pole of significator
    pole = _pole_of_significator(
        sig.dec, lat, sig.ra, ramc, sig.above_horizon
    )

    # OA of significator with its own pole
    sig_oa = _oblique_ascension_with_pole(sig.ra, sig.dec, pole)

    # OA of promittor with significator's pole
    prom_oa = _oblique_ascension_with_pole(prom_ra, prom_dec, pole)

    if not converse:
        arc = _normalize(prom_oa - sig_oa)
    else:
        arc = _normalize(sig_oa - prom_oa)

    return arc


def _arc_to_years(arc: float, time_key: str,
                  sun_daily_motion: float = NAIBOD_KEY) -> float:
    """
    Convert a direction arc (degrees) to years of life.

    Keys:
        "naibod":     1 year = 0.98563° (mean solar motion, Naibod 1560)
        "ptolemy":    1 year = 1.00000° (simplified Ptolemy key)
        "solar_arc":  1 year = actual Sun daily motion at birth

    Ref: Naibod, Enarratio Elementorum Astrologiae (1560);
         Placidus, Primum Mobile (1657), Table of Keys.
    """
    if time_key == "naibod":
        key = NAIBOD_KEY
    elif time_key == "ptolemy":
        key = PTOLEMY_KEY
    elif time_key == "solar_arc":
        key = sun_daily_motion
    else:
        key = NAIBOD_KEY
    return arc / key if key > 0 else arc


def _years_to_date(birth_year: int, birth_month: int, birth_day: int,
                   years: float) -> date:
    """
    Convert a fractional number of years from birth to a calendar date.

    Uses a simple but accurate approach:
      integer_years passed → advance year
      fractional remainder → days in remaining year (accounting for leap years)
    """
    birth = date(birth_year, birth_month, birth_day)
    int_years = int(years)
    frac = years - int_years

    # Add integer years (handle Feb 29 edge case)
    try:
        interim = date(birth_year + int_years, birth_month, birth_day)
    except ValueError:
        # Feb 29 in non-leap year → use Mar 1
        interim = date(birth_year + int_years, 3, 1)

    # Add fractional year as days
    days_in_year = 365.25  # mean year
    extra_days = int(round(frac * days_in_year))
    event_date = interim + timedelta(days=extra_days)
    return event_date


# ──────────────────────────────────────────────────────────────
# Main direction computation
# ──────────────────────────────────────────────────────────────

def _compute_directions(
    natal_points: List[ChartPoint],
    ramc: float,
    obliquity: float,
    latitude: float,
    birth_date: date,
    method: str,
    time_key: str,
    max_age: float,
    significators: List[str],
    promittors: List[str],
    include_aspects: List[str],
    include_converse: bool,
    sun_daily_motion: float,
) -> List[Direction]:
    """
    Core engine: compute all Primary Directions.

    For each (significator, promittor, aspect) combination, compute the
    direction arc using the specified method, convert to years, and build
    Direction objects.

    The arc is filtered to [0°, max_arc] where max_arc = max_age × key.

    Returns:
        List of Direction objects sorted by years (ascending).
    """
    max_arc = max_age * (NAIBOD_KEY if time_key == "naibod" else
                        (PTOLEMY_KEY if time_key == "ptolemy" else sun_daily_motion))

    point_map: Dict[str, ChartPoint] = {p.key: p for p in natal_points}

    directions: List[Direction] = []

    for sig_key in significators:
        sig = point_map.get(sig_key)
        if sig is None:
            continue

        for prom_key in promittors:
            if prom_key == sig_key:
                continue
            prom = point_map.get(prom_key)
            if prom is None:
                continue

            # Build list of (aspect_key, prom_ra, prom_dec) to try
            prom_positions: List[Tuple[str, float, float]] = []

            for asp_key in include_aspects:
                if asp_key in ("PAR", "CPAR"):
                    # Parallel / contra-parallel use declination, not longitude
                    # Handle separately below
                    prom_positions.append((asp_key, prom.ra, prom.dec))
                elif asp_key == "CNJ":
                    prom_positions.append(("CNJ", prom.ra, prom.dec))
                elif asp_key == "OPP":
                    # Opposite RA position
                    opp_ra = _normalize(prom.ra + 180.0)
                    prom_positions.append(("OPP", opp_ra, -prom.dec))
                else:
                    # For SQR, TRI, SXT: use zodiacal aspect positions
                    # Convert promittor longitude to aspect positions
                    ang = {"SXT": 60.0, "SQR": 90.0, "TRI": 120.0}.get(asp_key, 0.0)
                    if ang == 0.0:
                        continue
                    # Sinister (forward) aspect
                    asp_lon_s = _normalize(prom.longitude + ang)
                    ra_s, dec_s = _ecliptic_to_equatorial(asp_lon_s, 0.0, obliquity)
                    prom_positions.append((asp_key + "_s", ra_s, dec_s))
                    # Dexter (backward) aspect
                    asp_lon_d = _normalize(prom.longitude - ang)
                    ra_d, dec_d = _ecliptic_to_equatorial(asp_lon_d, 0.0, obliquity)
                    prom_positions.append((asp_key + "_d", ra_d, dec_d))

            for converse in ([False, True] if include_converse else [False]):
                for asp_tag, p_ra, p_dec in prom_positions:
                    # Resolve actual aspect key (strip _s/_d suffix)
                    asp_key_clean = asp_tag.rstrip("_sd").rstrip("_")
                    if asp_tag.endswith("_s") or asp_tag.endswith("_d"):
                        asp_key_clean = asp_tag[:-2]

                    # Special handling for parallels
                    if asp_tag in ("PAR", "CPAR"):
                        _handle_parallel(
                            sig, prom, asp_tag, converse,
                            latitude, method, time_key, sun_daily_motion,
                            max_arc, birth_date, directions, ramc, obliquity
                        )
                        continue

                    # Compute arc
                    if method == "zodiacal":
                        arc = _zodiacal_arc(
                            sig, p_ra, p_dec, latitude, ramc, converse
                        )
                    else:  # mundo
                        arc = _mundo_arc(
                            sig, p_ra, p_dec, latitude, ramc, obliquity, converse
                        )

                    if arc is None or arc > max_arc or arc < 0.01:
                        continue

                    years = _arc_to_years(arc, time_key, sun_daily_motion)
                    if years > max_age:
                        continue

                    event_date = _years_to_date(
                        birth_date.year, birth_date.month, birth_date.day, years
                    )

                    nature = get_event_nature(prom_key, sig_key)
                    asp_nature = {"CNJ": "CNJ", "OPP": "OPP", "SQR": "SQR",
                                  "TRI": "TRI", "SXT": "SXT"}.get(asp_key_clean, "CNJ")
                    asp_nat = {"zh": "", "en": ""}
                    from .constants import ASPECT_DIRECTION_MEANINGS
                    if asp_key_clean in ASPECT_DIRECTION_MEANINGS:
                        asp_nat = ASPECT_DIRECTION_MEANINGS[asp_key_clean]

                    sig_meaning = SIGNIFICATOR_MEANINGS.get(sig_key, {"zh": "", "en": ""})

                    directions.append(Direction(
                        significator_key=sig_key,
                        promittor_key=prom_key,
                        aspect_key=asp_key_clean,
                        converse=converse,
                        method=method,
                        arc=arc,
                        time_key=time_key,
                        years=years,
                        birth_date=birth_date,
                        event_date=event_date,
                        nature_zh=nature.get("zh", ""),
                        nature_en=nature.get("en", ""),
                        aspect_nature_zh=asp_nat.get("zh", ""),
                        aspect_nature_en=asp_nat.get("en", ""),
                        sig_meaning_zh=sig_meaning.get("zh", ""),
                        sig_meaning_en=sig_meaning.get("en", ""),
                    ))

    directions.sort(key=lambda d: d.years)
    return directions


def _handle_parallel(
    sig: ChartPoint,
    prom: ChartPoint,
    asp_key: str,  # "PAR" or "CPAR"
    converse: bool,
    lat: float,
    method: str,
    time_key: str,
    sun_daily_motion: float,
    max_arc: float,
    birth_date: date,
    directions: List[Direction],
    ramc: float,
    obliquity: float,
) -> None:
    """
    Handle Parallel and Contra-parallel of declination.

    Parallel: both planets have the same declination (same hemisphere)
    Contra-parallel: planets have equal but opposite declination

    For direction arc computation, we find the RA position where the
    significator's declination equals ±promittor's declination, then
    compute the RA difference as the arc.
    """
    target_dec = prom.dec if asp_key == "PAR" else -prom.dec

    # Find the longitude on the ecliptic with the target declination
    # sin(target_dec) = sin(eps) * sin(lon)  (for points on ecliptic, lat=0)
    eps = obliquity
    sin_val = math.sin(math.radians(target_dec)) / math.sin(math.radians(eps))
    if abs(sin_val) > 1.0:
        return  # Impossible declination for this obliquity

    lon1 = math.degrees(math.asin(sin_val))  # 0°–90°
    # Two solutions: lon1 and 180° - lon1 (and + 180° for other hemisphere)
    candidate_lons = [lon1, 180.0 - lon1, lon1 + 180.0, 360.0 - lon1]

    for cand_lon in candidate_lons:
        cand_lon = _normalize(cand_lon)
        cand_ra, cand_dec = _ecliptic_to_equatorial(cand_lon, 0.0, obliquity)

        if method == "zodiacal":
            arc = _zodiacal_arc(sig, cand_ra, cand_dec, lat, ramc, converse)
        else:
            arc = _mundo_arc(sig, cand_ra, cand_dec, lat, ramc, obliquity, converse)

        if arc is None or arc > max_arc or arc < 0.01:
            continue

        years = _arc_to_years(arc, time_key, sun_daily_motion)
        event_date = _years_to_date(
            birth_date.year, birth_date.month, birth_date.day, years
        )

        nature = get_event_nature(prom.key, sig.key)
        from .constants import ASPECT_DIRECTION_MEANINGS
        asp_nat = ASPECT_DIRECTION_MEANINGS.get(asp_key, {"zh": "", "en": ""})
        sig_meaning = SIGNIFICATOR_MEANINGS.get(sig.key, {"zh": "", "en": ""})

        directions.append(Direction(
            significator_key=sig.key,
            promittor_key=prom.key,
            aspect_key=asp_key,
            converse=converse,
            method=method,
            arc=arc,
            time_key=time_key,
            years=years,
            birth_date=birth_date,
            event_date=event_date,
            nature_zh=nature.get("zh", ""),
            nature_en=nature.get("en", ""),
            aspect_nature_zh=asp_nat.get("zh", ""),
            aspect_nature_en=asp_nat.get("en", ""),
            sig_meaning_zh=sig_meaning.get("zh", ""),
            sig_meaning_en=sig_meaning.get("en", ""),
        ))


# ──────────────────────────────────────────────────────────────
# Solar Arc daily motion
# ──────────────────────────────────────────────────────────────

def _sun_daily_motion(year: int, month: int, day: int,
                      hour: int, minute: int, timezone: float) -> float:
    """Compute the Sun's mean daily motion at birth (degrees/day)."""
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)
    result, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
    return abs(result[3])  # daily speed in deg/day ≈ 0.9856–1.0185


# ──────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────

_DEFAULT_SIGNIFICATORS = ["AS", "MC", "SU", "MO"]
_DEFAULT_PROMITTORS = ["SU", "MO", "ME", "VE", "MA", "JU", "SA", "AS", "MC"]
_DEFAULT_ASPECTS = ["CNJ", "OPP", "SQR", "TRI", "SXT"]


def compute_primary_directions(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    method: str = "mundo",
    time_key: str = "naibod",
    max_age: float = 90.0,
    significators: Optional[List[str]] = None,
    promittors: Optional[List[str]] = None,
    include_aspects: Optional[List[str]] = None,
    include_converse: bool = True,
    location_name: str = "",
    **_kwargs,
) -> PrimaryDirectionsResult:
    """
    Compute Classical Primary Directions for a natal chart.

    Implements two canonical methods:

    A. **Zodiacal** (method="zodiacal"):
       Uses Oblique Ascension in the horizon system.
       Arc = OA(promittor) − OA(significator)
       Ref: Ptolemy, Tetrabiblos III.10–11.

    B. **Mundo / Placidus** (method="mundo", default):
       Uses the Placidus semi-arc proportional pole method.
       More precise; accounts for actual diurnal arc of each planet.
       Ref: Placidus de Titis, Primum Mobile (1657);
            Gansten, Primary Directions (2009), ch. 4.

    Time keys:
        "naibod"    — 1° = 1.01461 years (most common traditional key)
        "ptolemy"   — 1° = 1 year (Ptolemy's simplified key)
        "solar_arc" — 1° = Sun's actual daily motion at birth

    Args:
        year, month, day: Birth date.
        hour, minute: Local birth time (24h).
        timezone: UTC offset in hours (e.g. +8 for CST).
        latitude, longitude: Geographic coordinates of birthplace.
        method: "mundo" (Placidus, default) or "zodiacal" (Ptolemy).
        time_key: "naibod" (default), "ptolemy", or "solar_arc".
        max_age: Compute directions up to this age in years (default: 90).
        significators: List of point keys to direct. Defaults to AS, MC, SU, MO.
        promittors: List of natal points to be aspected. Defaults to 7 classical
            planets + AS + MC.
        include_aspects: List of aspect keys. Defaults to CNJ OPP SQR TRI SXT.
        include_converse: If True, also compute converse (backward) directions.
        location_name: Optional place name for display.

    Returns:
        PrimaryDirectionsResult with full natal data and sorted direction list.

    Raises:
        ValueError: For invalid parameters.
        RuntimeError: If Swiss Ephemeris fails (usually missing ephemeris files).
    """
    if method not in ("zodiacal", "mundo"):
        raise ValueError(f"method must be 'zodiacal' or 'mundo', got {method!r}")
    if time_key not in ("naibod", "ptolemy", "solar_arc"):
        raise ValueError(f"time_key must be 'naibod', 'ptolemy', or 'solar_arc'")
    if max_age <= 0:
        raise ValueError("max_age must be positive")

    if significators is None:
        significators = _DEFAULT_SIGNIFICATORS
    if promittors is None:
        promittors = _DEFAULT_PROMITTORS
    if include_aspects is None:
        include_aspects = _DEFAULT_ASPECTS

    # Validate requested keys exist
    valid_keys = set(PLANET_ORDER)
    for k in significators:
        if k not in valid_keys:
            raise ValueError(f"Unknown significator key: {k!r}")
    for k in promittors:
        if k not in valid_keys:
            raise ValueError(f"Unknown promittor key: {k!r}")

    natal_points, ramc, obliquity = _compute_natal_points(
        year, month, day, hour, minute, timezone, latitude, longitude
    )

    sun_daily = _sun_daily_motion(year, month, day, hour, minute, timezone)

    birth = date(year, month, day)

    directions = _compute_directions(
        natal_points=natal_points,
        ramc=ramc,
        obliquity=obliquity,
        latitude=latitude,
        birth_date=birth,
        method=method,
        time_key=time_key,
        max_age=max_age,
        significators=significators,
        promittors=promittors,
        include_aspects=include_aspects,
        include_converse=include_converse,
        sun_daily_motion=sun_daily,
    )

    return PrimaryDirectionsResult(
        natal_points=natal_points,
        ramc=ramc,
        obliquity=obliquity,
        directions=directions,
        method=method,
        time_key=time_key,
        max_age=max_age,
        include_converse=include_converse,
        significators=significators,
        promittors=promittors,
        include_aspects=include_aspects,
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
    )
