"""
astro/trutine_of_hermes/calculator.py — 赫密士出生前世盤計算引擎

Prenatal Epoch (Trutine of Hermes) Calculation Engine

Classical references:
  - Hermes Trismegistus (attributed) — original Trutine rule
  - Ptolemy, *Centiloquium* (Karpos), Aphorism 51 (2nd c. CE)
  - E.H. Bailey, *The Prenatal Epoch* (1916)
  - Sepharial (W.R. Old), *The Solar Epoch* (1913)

Architecture:
  - ``compute_epoch_chart`` — public API: returns both Natal + Epoch charts
  - ``_find_epoch_jd``       — iterative search for the Epoch Julian Day
  - ``_compute_full_chart``  — calculates all planet positions + houses
  - ``_moon_phase_info``     — determines Moon phase and elongation
  - ``_is_moon_above_horizon`` — determines Moon's horizon position
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from .constants import (
    GESTATION_DAYS_STANDARD,
    GESTATION_DAYS_SHORT,
    GESTATION_DAYS_LONG,
    GESTATION_SEARCH_RANGE_DAYS,
    EPOCH_SEARCH_STEP_MINUTES,
    MAX_EPOCH_ITERATIONS,
    TRUTINE_VARIANTS,
    EPOCH_NATAL_ASPECT_ORBS,
    ZODIAC_SIGNS,
    ZODIAC_SIGN_ZH,
    ZODIAC_GLYPHS,
    MOON_PHASE_ELONGATION,
    MOON_PHASE_NAMES,
    PLANET_DISPLAY,
    EPOCH_SOUL_THEMES,
)

# ============================================================
# Enums
# ============================================================


class TrutineVariant(str, Enum):
    """Supported Trutine of Hermes calculation variants.

    Ref: See constants.TRUTINE_VARIANTS for full descriptions.
    """
    HERMES_PTOLEMY = "hermes_ptolemy"
    """Classical Hermes/Ptolemy variant (Centiloquium Aphorism 51)."""

    BAILEY_STANDARD = "bailey_standard"
    """Bailey standard method (The Prenatal Epoch, 1916)."""

    SEPHARIAL = "sepharial"
    """Sepharial Solar Epoch method (The Solar Epoch, 1913)."""


# ============================================================
# Data Classes
# ============================================================


@dataclass
class EpochPlanetPosition:
    """A planet's position in either the Natal or Epoch chart.

    Attributes:
        name:          Planet name (e.g. ``"Moon"``)
        longitude:     Ecliptic longitude 0–360°
        sign:          Zodiac sign name (e.g. ``"Aries"``)
        sign_index:    Sign index 0–11
        degree_in_sign: Degrees within sign 0–30°
        retrograde:    True if planet is in retrograde motion
        display_zh:    Chinese display name
        display_en:    English display name
    """
    name: str
    longitude: float
    sign: str
    sign_index: int
    degree_in_sign: float
    retrograde: bool = False
    display_zh: str = ""
    display_en: str = ""

    def __post_init__(self) -> None:
        if not self.display_zh:
            self.display_zh = PLANET_DISPLAY.get(self.name, {}).get("zh", self.name)
        if not self.display_en:
            self.display_en = PLANET_DISPLAY.get(self.name, {}).get("en", self.name)

    @property
    def dms_str(self) -> str:
        """Return a degree-minute-second string like ``"15°32' Aries"``."""
        d = int(self.degree_in_sign)
        m = int((self.degree_in_sign - d) * 60)
        return f"{d}°{m:02d}′ {self.sign}"

    @property
    def dms_str_zh(self) -> str:
        """Return Chinese degree string like ``"白羊座 15°32'``."""
        d = int(self.degree_in_sign)
        m = int((self.degree_in_sign - d) * 60)
        sign_zh = ZODIAC_SIGN_ZH.get(self.sign, self.sign)
        return f"{sign_zh} {d}°{m:02d}′"


@dataclass
class CrossAspect:
    """An aspect between an Epoch planet and a Natal planet.

    Attributes:
        epoch_planet:   Name of the Epoch chart planet/angle
        natal_planet:   Name of the Natal chart planet/angle
        aspect_name:    Aspect name (e.g. ``"Conjunction ☌"``)
        aspect_angle:   Exact aspect angle (0, 60, 90, 120, 180…)
        orb:            Actual orb in degrees
        applying:       True if aspect is applying
    """
    epoch_planet: str
    natal_planet: str
    aspect_name: str
    aspect_angle: float
    orb: float
    applying: bool = False


@dataclass
class PrenatalEpochChart:
    """Complete result for a Prenatal Epoch (Trutine of Hermes) calculation.

    Contains both the Natal chart and the Epoch chart, the reciprocal
    Moon-Ascendant relationship, cross-aspects, and soul-level interpretations.

    Ref: Bailey, The Prenatal Epoch (1916); Ptolemy, Centiloquium Ap. 51.

    Attributes:
        variant:              Which Trutine variant was used
        birth_jd:             Julian Day of birth
        birth_datetime_str:   Human-readable birth datetime
        birth_lat:            Birth latitude
        birth_lon:            Birth longitude
        birth_tz:             Birth timezone offset (hours)

        epoch_jd:             Julian Day of the Prenatal Epoch
        epoch_datetime_str:   Human-readable Epoch datetime
        gestation_days:       Actual gestation period calculated

        natal_planets:        {name: EpochPlanetPosition} at birth
        natal_asc:            Natal Ascendant longitude
        natal_mc:             Natal MC longitude
        natal_dsc:            Natal Descendant longitude
        natal_ic:             Natal IC longitude
        natal_house_cusps:    12 Placidus house cusp longitudes

        epoch_planets:        {name: EpochPlanetPosition} at Epoch
        epoch_asc:            Epoch Ascendant longitude
        epoch_mc:             Epoch MC longitude
        epoch_dsc:            Epoch Descendant longitude
        epoch_ic:             Epoch IC longitude
        epoch_house_cusps:    12 Placidus house cusp longitudes

        natal_moon_lon:       Natal Moon longitude (the key input)
        moon_above_horizon:   True if natal Moon is above the horizon
        moon_phase_name:      Moon phase name at birth
        moon_elongation:      Sun-Moon elongation at birth (degrees)
        is_waxing:            True if Moon is waxing at birth
        epoch_angle:          Which angle at Epoch = Natal Moon ("ASC"/"DSC")
        trutine_match_orb:    Orb between Epoch angle and Natal Moon (degrees)
        trutine_verified:     True if match is within 1°

        cross_aspects:        List[CrossAspect] between the two charts
        soul_interpretations: {theme: text} soul-level insights
        rectification_note:   Text note for rectification use
    """
    variant: str
    birth_jd: float
    birth_datetime_str: str
    birth_lat: float
    birth_lon: float
    birth_tz: float

    epoch_jd: float
    epoch_datetime_str: str
    gestation_days: float

    natal_planets: Dict[str, EpochPlanetPosition] = field(default_factory=dict)
    natal_asc: float = 0.0
    natal_mc: float = 0.0
    natal_dsc: float = 0.0
    natal_ic: float = 0.0
    natal_house_cusps: List[float] = field(default_factory=list)

    epoch_planets: Dict[str, EpochPlanetPosition] = field(default_factory=dict)
    epoch_asc: float = 0.0
    epoch_mc: float = 0.0
    epoch_dsc: float = 0.0
    epoch_ic: float = 0.0
    epoch_house_cusps: List[float] = field(default_factory=list)

    natal_moon_lon: float = 0.0
    moon_above_horizon: bool = True
    moon_phase_name: str = ""
    moon_elongation: float = 0.0
    is_waxing: bool = True
    epoch_angle: str = "ASC"
    trutine_match_orb: float = 999.0
    trutine_verified: bool = False

    cross_aspects: List[CrossAspect] = field(default_factory=list)
    soul_interpretations: Dict[str, str] = field(default_factory=dict)
    rectification_note: str = ""

    error: Optional[str] = None


# ============================================================
# Internal Helpers
# ============================================================

# Swiss Ephemeris planet IDs
_PLANET_IDS: Dict[str, int] = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
    "Uranus":  swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto":   swe.PLUTO,
}

# Aspect definitions: (name, exact_angle, default_orb)
_ASPECTS: List[Tuple[str, float, float]] = [
    ("Conjunction ☌",   0.0,   5.0),
    ("Opposition ☍",  180.0,   5.0),
    ("Trine △",       120.0,   4.0),
    ("Square □",       90.0,   4.0),
    ("Sextile ⚹",      60.0,   3.0),
    ("Quincunx ⚻",    150.0,   2.0),
    ("Semi-Sextile ⚺", 30.0,   1.5),
]


def _normalize(deg: float) -> float:
    """Normalise a longitude to [0, 360)."""
    return deg % 360.0


def _sign_index(lon: float) -> int:
    """Return sign index 0–11 for a given longitude."""
    return int(_normalize(lon) / 30.0)


def _sign_name(lon: float) -> str:
    """Return the zodiac sign name for a given longitude."""
    return ZODIAC_SIGNS[_sign_index(lon)]


def _deg_in_sign(lon: float) -> float:
    """Return degrees within sign (0–30)."""
    return _normalize(lon) % 30.0


def _jd_from_datetime(year: int, month: int, day: int,
                      hour: float, tz: float = 0.0) -> float:
    """Convert local datetime to Julian Day (UT).

    Args:
        year, month, day: Gregorian calendar date
        hour:             Local hour as float (e.g. 14.5 = 14:30)
        tz:               Timezone offset in hours east of UTC

    Returns:
        Julian Day Number (UT)
    """
    swe.set_ephe_path("")
    ut_hour = hour - tz
    return swe.julday(year, month, day, ut_hour)


def _jd_to_datetime_str(jd: float, tz: float = 0.0) -> str:
    """Convert Julian Day to a human-readable local datetime string.

    Args:
        jd: Julian Day (UT)
        tz: Timezone offset in hours

    Returns:
        String like ``"2024-03-15 14:32 (UTC+8)"``
    """
    y, mo, d, h = swe.revjul(jd)
    local_h = h + tz
    # Handle day overflow
    overflow_days = int(local_h // 24)
    local_h = local_h % 24
    if overflow_days:
        jd_shifted = jd + overflow_days
        y, mo, d, _ = swe.revjul(jd_shifted)
    hour_i = int(local_h)
    minute_i = int((local_h - hour_i) * 60)
    tz_sign = "+" if tz >= 0 else ""
    return f"{int(y):04d}-{int(mo):02d}-{int(d):02d} {hour_i:02d}:{minute_i:02d} (UTC{tz_sign}{tz:.0f})"


def _compute_full_chart(
    jd: float, lat: float, lon: float
) -> Tuple[Dict[str, EpochPlanetPosition], float, float, float, float, List[float]]:
    """Compute a complete chart for a given Julian Day and location.

    Uses Placidus house system.

    Args:
        jd:  Julian Day (UT)
        lat: Geographic latitude (degrees, north positive)
        lon: Geographic longitude (degrees, east positive)

    Returns:
        Tuple of:
          - planet_positions: {name: EpochPlanetPosition}
          - asc_lon: Ascendant longitude
          - mc_lon:  MC longitude
          - dsc_lon: Descendant longitude (ASC + 180)
          - ic_lon:  IC longitude (MC + 180)
          - house_cusps: 12-element list of cusp longitudes
    """
    swe.set_ephe_path("")
    planet_positions: Dict[str, EpochPlanetPosition] = {}

    for name, pid in _PLANET_IDS.items():
        try:
            xx, _ = swe.calc_ut(jd, pid)
            lon_ = _normalize(xx[0])
            # Check retrograde: speed < 0
            speed = xx[3]
            retro = speed < 0.0
            si = _sign_index(lon_)
            pos = EpochPlanetPosition(
                name=name,
                longitude=lon_,
                sign=ZODIAC_SIGNS[si],
                sign_index=si,
                degree_in_sign=_deg_in_sign(lon_),
                retrograde=retro,
            )
            planet_positions[name] = pos
        except Exception:
            planet_positions[name] = EpochPlanetPosition(
                name=name, longitude=0.0,
                sign="Aries", sign_index=0, degree_in_sign=0.0,
            )

    # House cusps
    try:
        cusps, ascmc = swe.houses(jd, lat, lon, b"P")
        asc_lon = _normalize(ascmc[0])
        mc_lon = _normalize(ascmc[1])
        house_cusps = [_normalize(c) for c in cusps[:12]]
    except Exception:
        asc_lon = 0.0
        mc_lon = 0.0
        house_cusps = [float(i * 30) for i in range(12)]

    dsc_lon = _normalize(asc_lon + 180.0)
    ic_lon = _normalize(mc_lon + 180.0)

    return planet_positions, asc_lon, mc_lon, dsc_lon, ic_lon, house_cusps


def _moon_phase_info(
    sun_lon: float, moon_lon: float
) -> Tuple[str, float, bool]:
    """Determine Moon phase, elongation, and waxing/waning status.

    Args:
        sun_lon:  Sun longitude (0–360°)
        moon_lon: Moon longitude (0–360°)

    Returns:
        Tuple of:
          - phase_name: Key from MOON_PHASE_NAMES
          - elongation: Moon elongation from Sun (0–360°)
          - is_waxing:  True if Moon is waxing
    """
    elongation = _normalize(moon_lon - sun_lon)
    is_waxing = elongation < 180.0

    phase_name = "waxing_crescent"
    for pname, (lo, hi) in MOON_PHASE_ELONGATION.items():
        if lo <= elongation < hi:
            phase_name = pname
            break

    return phase_name, elongation, is_waxing


def _is_moon_above_horizon(moon_lon: float, asc_lon: float) -> bool:
    """Determine if the Moon is above the horizon at birth.

    A planet is above the horizon if it is in houses 7–12,
    i.e., within 180° ahead of the Ascendant in the zodiac.

    Ref: Bailey (1916), Chapter II; standard house position logic.

    Args:
        moon_lon: Moon longitude (0–360°)
        asc_lon:  Ascendant longitude (0–360°)

    Returns:
        True if Moon is above the horizon (houses 7–12)
    """
    # Angular distance from ASC going counter-clockwise (zodiacal order)
    # Houses 1–6 are below horizon (from ASC to DSC going counterclockwise)
    # Houses 7–12 are above horizon (from DSC to ASC going counterclockwise)
    # DSC = ASC + 180
    dsc_lon = _normalize(asc_lon + 180.0)
    # Arc from ASC to Moon (counterclockwise / forward in zodiac)
    arc = _normalize(moon_lon - asc_lon)
    # If arc >= 180, Moon is between DSC and ASC (houses 7–12 = above horizon)
    return arc >= 180.0


def _angular_diff(lon_a: float, lon_b: float) -> float:
    """Return the absolute shortest arc between two longitudes (0–180°)."""
    diff = abs(_normalize(lon_a) - _normalize(lon_b))
    if diff > 180.0:
        diff = 360.0 - diff
    return diff


def _check_aspect(
    lon_a: float, lon_b: float
) -> Tuple[Optional[str], float, float]:
    """Check for the closest aspect between two longitudes.

    Args:
        lon_a, lon_b: Ecliptic longitudes

    Returns:
        (aspect_name, exact_angle, orb) or (None, 0, 999) if no aspect
    """
    diff = abs(_normalize(lon_a) - _normalize(lon_b))
    if diff > 180.0:
        diff = 360.0 - diff

    best = (None, 0.0, 999.0)
    for asp_name, asp_angle, max_orb in _ASPECTS:
        orb = abs(diff - asp_angle)
        orb_limit = EPOCH_NATAL_ASPECT_ORBS.get(asp_name, max_orb)
        if orb <= orb_limit and orb < best[2]:
            best = (asp_name, asp_angle, round(orb, 2))

    return best


def _find_epoch_jd(
    birth_jd: float,
    natal_moon_lon: float,
    natal_asc_lon: float,
    lat: float,
    lon: float,
    target_angle: str,  # "ASC" or "DSC"
    gestation_days: float,
    search_range_days: float = GESTATION_SEARCH_RANGE_DAYS,
    step_minutes: float = EPOCH_SEARCH_STEP_MINUTES,
) -> Tuple[float, float]:
    """Search for the Epoch Julian Day using the Trutine rule.

    Iterates backward from (birth_jd - gestation_days + range)
    to (birth_jd - gestation_days - range), stepping by step_minutes,
    and finds the moment when the Epoch chart's ASC (or DSC) most closely
    matches the Natal Moon position.

    Ref: Bailey (1916), Chapter III; Ptolemy Centiloquium Ap. 51.

    Args:
        birth_jd:        Julian Day of birth
        natal_moon_lon:  Natal Moon longitude (the target)
        natal_asc_lon:   Natal Ascendant longitude (for horizon test)
        lat, lon:        Geographic coordinates (birth location used)
        target_angle:    "ASC" or "DSC" — which Epoch angle should match
        gestation_days:  Central gestation period to search around
        search_range_days: ± range around gestation_days
        step_minutes:    Search granularity in minutes

    Returns:
        (best_epoch_jd, best_orb) — Julian Day of best match and its orb
    """
    # Search window
    start_jd = birth_jd - gestation_days - search_range_days
    end_jd   = birth_jd - gestation_days + search_range_days
    step_jd  = step_minutes / (24.0 * 60.0)

    best_jd = birth_jd - gestation_days
    best_orb = 999.0
    n_iter = 0

    current_jd = start_jd
    while current_jd <= end_jd and n_iter < MAX_EPOCH_ITERATIONS:
        try:
            _, asc_, mc_, dsc_, ic_, _ = _compute_full_chart(current_jd, lat, lon)
            angle_lon = asc_ if target_angle == "ASC" else dsc_
            orb = _angular_diff(angle_lon, natal_moon_lon)
            if orb < best_orb:
                best_orb = orb
                best_jd = current_jd
        except Exception:
            pass
        current_jd += step_jd
        n_iter += 1

    # Refine: fine search ±4 minutes around best
    refine_step = 1.0 / (24.0 * 60.0)  # 1 minute
    for delta_min in range(-4, 5):
        candidate_jd = best_jd + delta_min * refine_step
        try:
            _, asc_, mc_, dsc_, ic_, _ = _compute_full_chart(candidate_jd, lat, lon)
            angle_lon = asc_ if target_angle == "ASC" else dsc_
            orb = _angular_diff(angle_lon, natal_moon_lon)
            if orb < best_orb:
                best_orb = orb
                best_jd = candidate_jd
        except Exception:
            pass

    return best_jd, best_orb


def _compute_cross_aspects(
    epoch_planets: Dict[str, EpochPlanetPosition],
    epoch_asc: float,
    epoch_mc: float,
    natal_planets: Dict[str, EpochPlanetPosition],
    natal_asc: float,
    natal_mc: float,
) -> List[CrossAspect]:
    """Compute cross-aspects between the Epoch and Natal charts.

    Checks all Epoch planet/angle positions against all Natal
    planet/angle positions for the major aspects.

    Ref: Bailey (1916), Chapter VIII.

    Args:
        epoch_planets, natal_planets: {name: EpochPlanetPosition}
        epoch_asc, epoch_mc:          Epoch angle longitudes
        natal_asc, natal_mc:          Natal angle longitudes

    Returns:
        List of CrossAspect objects (sorted by orb, tightest first)
    """
    # Epoch points to check
    epoch_points: Dict[str, float] = {
        name: pos.longitude for name, pos in epoch_planets.items()
    }
    epoch_points["ASC (Epoch)"] = epoch_asc
    epoch_points["MC (Epoch)"] = epoch_mc
    epoch_points["DSC (Epoch)"] = _normalize(epoch_asc + 180.0)

    # Natal points to check
    natal_points: Dict[str, float] = {
        name: pos.longitude for name, pos in natal_planets.items()
    }
    natal_points["ASC"] = natal_asc
    natal_points["MC"] = natal_mc
    natal_points["DSC"] = _normalize(natal_asc + 180.0)

    aspects: List[CrossAspect] = []

    for e_name, e_lon in epoch_points.items():
        for n_name, n_lon in natal_points.items():
            asp_name, asp_angle, orb = _check_aspect(e_lon, n_lon)
            if asp_name is not None and orb < 999.0:
                aspects.append(CrossAspect(
                    epoch_planet=e_name,
                    natal_planet=n_name,
                    aspect_name=asp_name,
                    aspect_angle=asp_angle,
                    orb=orb,
                ))

    # Sort tightest first
    aspects.sort(key=lambda a: a.orb)
    return aspects


def _build_soul_interpretations(
    epoch_planets: Dict[str, EpochPlanetPosition],
    epoch_asc: float,
    natal_moon_lon: float,
    epoch_angle: str,
    trutine_match_orb: float,
) -> Dict[str, str]:
    """Build soul-level interpretation text for the Epoch chart.

    Ref: Bailey, The Prenatal Epoch (1916), Chapter IX;
         Alice Bailey, Esoteric Astrology (1951).

    Args:
        epoch_planets:     Epoch chart planet positions
        epoch_asc:         Epoch Ascendant longitude
        natal_moon_lon:    Natal Moon longitude
        epoch_angle:       "ASC" or "DSC" — which angle = Natal Moon
        trutine_match_orb: Orb of the Trutine match

    Returns:
        {theme_key: interpretation_text}
    """
    from astro.i18n import get_lang
    lang = get_lang()
    interps: Dict[str, str] = {}

    # Core Trutine match
    match_quality = (
        "極佳（< 1°）" if lang == "zh" else "Excellent (< 1°)"
    ) if trutine_match_orb < 1.0 else (
        "良好（< 3°）" if lang == "zh" else "Good (< 3°)"
    ) if trutine_match_orb < 3.0 else (
        "尚可（< 5°）" if lang == "zh" else "Fair (< 5°)"
    )

    if lang == "zh":
        interps["trutine_core"] = (
            f"**赫密士法則核心連結** — "
            f"本命月亮（{_format_lon_zh(natal_moon_lon)}）"
            f"= 前世盤{epoch_angle}（{_format_lon_zh(epoch_asc if epoch_angle == 'ASC' else _normalize(epoch_asc + 180.0))}），"
            f"誤差 {trutine_match_orb:.2f}°，匹配質量：{match_quality}。\n\n"
            f"這個神聖的互換點是靈魂從前世盤（受孕）過渡到本命盤（出生）的橋梁。"
        )
    else:
        angle_lon = epoch_asc if epoch_angle == "ASC" else _normalize(epoch_asc + 180.0)
        interps["trutine_core"] = (
            f"**Trutine Core Link** — "
            f"Natal Moon ({_format_lon_en(natal_moon_lon)}) "
            f"= Epoch {epoch_angle} ({_format_lon_en(angle_lon)}), "
            f"orb {trutine_match_orb:.2f}°, quality: {match_quality}.\n\n"
            f"This sacred exchange point is the bridge through which the soul "
            f"transitions from Epoch (conception) to Natal chart (birth)."
        )

    # Planet-level soul themes
    key_planets = ["Sun", "Moon", "ASC", "Saturn", "Venus", "Mars", "Jupiter"]
    for planet_name in key_planets:
        theme = EPOCH_SOUL_THEMES.get(planet_name, {})
        if not theme:
            continue

        if planet_name == "ASC":
            pos_str = _format_lon_zh(epoch_asc) if lang == "zh" else _format_lon_en(epoch_asc)
            sign = _sign_name(epoch_asc)
            sign_str = ZODIAC_SIGN_ZH.get(sign, sign) if lang == "zh" else sign
        else:
            if planet_name not in epoch_planets:
                continue
            pos = epoch_planets[planet_name]
            pos_str = pos.dms_str_zh if lang == "zh" else pos.dms_str
            sign_str = ZODIAC_SIGN_ZH.get(pos.sign, pos.sign) if lang == "zh" else pos.sign

        theme_text = theme.get("zh" if lang == "zh" else "en", "")
        if lang == "zh":
            interps[f"epoch_{planet_name}"] = (
                f"**前世盤{PLANET_DISPLAY.get(planet_name, {}).get('zh', planet_name)}**"
                f"位於 {pos_str}\n\n{theme_text}"
            )
        else:
            interps[f"epoch_{planet_name}"] = (
                f"**Epoch {PLANET_DISPLAY.get(planet_name, {}).get('en', planet_name)}**"
                f" ({pos_str})\n\n{theme_text}"
            )

    return interps


def _format_lon_zh(lon: float) -> str:
    """Format longitude as Chinese display string."""
    sign = _sign_name(lon)
    deg = int(_deg_in_sign(lon))
    mi = int((_deg_in_sign(lon) - deg) * 60)
    sign_zh = ZODIAC_SIGN_ZH.get(sign, sign)
    return f"{sign_zh} {deg}°{mi:02d}′"


def _format_lon_en(lon: float) -> str:
    """Format longitude as English display string."""
    sign = _sign_name(lon)
    deg = int(_deg_in_sign(lon))
    mi = int((_deg_in_sign(lon) - deg) * 60)
    glyph = ZODIAC_GLYPHS.get(sign, "")
    return f"{deg}°{mi:02d}′ {sign} {glyph}"


# ============================================================
# Public API
# ============================================================


def compute_epoch_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    variant: str = TrutineVariant.BAILEY_STANDARD,
    gestation_override: Optional[float] = None,
) -> PrenatalEpochChart:
    """Compute the Prenatal Epoch (Trutine of Hermes) chart.

    Given birth data, this function:
    1. Computes the full natal chart (all planets + houses)
    2. Determines the natal Moon's horizon position (above/below)
    3. Determines whether the Epoch ASC or DSC should equal the natal Moon
    4. Searches backward ~273 days to find the Epoch moment
    5. Computes the full Epoch chart
    6. Calculates cross-aspects between the two charts
    7. Generates soul-level interpretations

    Ref: Bailey, The Prenatal Epoch (1916);
         Ptolemy, Centiloquium Aphorism 51.

    Args:
        year, month, day:   Birth date (Gregorian)
        hour, minute:       Local birth time
        timezone:           UTC offset in hours (e.g. 8 for UTC+8)
        latitude:           Geographic latitude (degrees, N positive)
        longitude:          Geographic longitude (degrees, E positive)
        location_name:      Optional location description
        variant:            TrutineVariant enum or string key
        gestation_override: Override gestation period in days (None = auto)

    Returns:
        PrenatalEpochChart dataclass with complete results.
    """
    swe.set_ephe_path("")

    try:
        # ── Step 1: Birth Julian Day ────────────────────────
        birth_hour_float = hour + minute / 60.0
        birth_jd = _jd_from_datetime(year, month, day, birth_hour_float, timezone)
        birth_datetime_str = _jd_to_datetime_str(birth_jd, timezone)

        # ── Step 2: Natal Chart ─────────────────────────────
        (
            natal_planets, natal_asc, natal_mc, natal_dsc, natal_ic,
            natal_house_cusps,
        ) = _compute_full_chart(birth_jd, latitude, longitude)

        natal_moon_lon = natal_planets["Moon"].longitude
        natal_sun_lon = natal_planets["Sun"].longitude

        # ── Step 3: Moon Phase & Horizon ───────────────────
        moon_phase_name, moon_elongation, is_waxing = _moon_phase_info(
            natal_sun_lon, natal_moon_lon
        )
        moon_above = _is_moon_above_horizon(natal_moon_lon, natal_asc)

        # ── Step 4: Trutine Rule → Target Angle ────────────
        # Ptolemy Centiloquium Ap. 51:
        #   above horizon → Epoch ASC = Natal Moon
        #   below horizon → Epoch DSC = Natal Moon
        epoch_angle = "ASC" if moon_above else "DSC"

        # ── Step 5: Gestation Period ────────────────────────
        if gestation_override is not None:
            gestation_days = gestation_override
        else:
            # Bailey refinement: adjust gestation based on Moon elongation
            # and waxing/waning status.
            # Standard: 273 days
            # If Moon elongation is very small (near new moon) → shorter gestation
            # If Moon elongation is large (near full moon) → standard
            # Ref: Bailey (1916), Chapter III.
            gestation_days = GESTATION_DAYS_STANDARD
            if moon_elongation < 45.0 or moon_elongation > 315.0:
                # Near new moon — slightly shorter
                gestation_days = GESTATION_DAYS_SHORT + (
                    (moon_elongation if moon_elongation < 45 else 360 - moon_elongation)
                    / 45.0
                ) * (GESTATION_DAYS_STANDARD - GESTATION_DAYS_SHORT)
            elif 135.0 < moon_elongation < 225.0:
                # Near full moon — can be slightly longer
                gestation_days = GESTATION_DAYS_STANDARD + (
                    1.0 - abs(moon_elongation - 180.0) / 45.0
                ) * (GESTATION_DAYS_LONG - GESTATION_DAYS_STANDARD) * 0.3

        # ── Step 6: Find Epoch Julian Day ──────────────────
        epoch_jd, trutine_orb = _find_epoch_jd(
            birth_jd=birth_jd,
            natal_moon_lon=natal_moon_lon,
            natal_asc_lon=natal_asc,
            lat=latitude,
            lon=longitude,
            target_angle=epoch_angle,
            gestation_days=gestation_days,
        )

        actual_gestation = birth_jd - epoch_jd
        epoch_datetime_str = _jd_to_datetime_str(epoch_jd, timezone)

        # ── Step 7: Epoch Chart ─────────────────────────────
        (
            epoch_planets, epoch_asc, epoch_mc, epoch_dsc, epoch_ic,
            epoch_house_cusps,
        ) = _compute_full_chart(epoch_jd, latitude, longitude)

        trutine_verified = trutine_orb <= 1.0

        # ── Step 8: Cross-Aspects ───────────────────────────
        cross_aspects = _compute_cross_aspects(
            epoch_planets, epoch_asc, epoch_mc,
            natal_planets, natal_asc, natal_mc,
        )

        # ── Step 9: Soul Interpretations ───────────────────
        soul_interps = _build_soul_interpretations(
            epoch_planets=epoch_planets,
            epoch_asc=epoch_asc,
            natal_moon_lon=natal_moon_lon,
            epoch_angle=epoch_angle,
            trutine_match_orb=trutine_orb,
        )

        # ── Step 10: Rectification Note ────────────────────
        from astro.i18n import get_lang
        lang = get_lang()
        if lang == "zh":
            if trutine_orb < 1.0:
                rect_note = (
                    f"✅ **校正驗證通過** — 赫密士法則誤差 {trutine_orb:.2f}°（< 1°），"
                    f"強力佐證出生時間準確。"
                )
            elif trutine_orb < 3.0:
                rect_note = (
                    f"⚠️ **校正可用** — 赫密士法則誤差 {trutine_orb:.2f}°（< 3°），"
                    f"出生時間可能需要微調。"
                )
            else:
                rect_note = (
                    f"❌ **誤差較大** — 赫密士法則誤差 {trutine_orb:.2f}°，"
                    f"建議重新確認出生時間，或嘗試其他校正技術。"
                )
        else:
            if trutine_orb < 1.0:
                rect_note = (
                    f"✅ **Rectification Verified** — Trutine orb {trutine_orb:.2f}° (< 1°), "
                    f"strongly confirms birth time accuracy."
                )
            elif trutine_orb < 3.0:
                rect_note = (
                    f"⚠️ **Rectification Possible** — Trutine orb {trutine_orb:.2f}° (< 3°), "
                    f"birth time may need minor adjustment."
                )
            else:
                rect_note = (
                    f"❌ **Large Orb** — Trutine orb {trutine_orb:.2f}°, "
                    f"suggest verifying birth time or trying other rectification techniques."
                )

        return PrenatalEpochChart(
            variant=str(variant),
            birth_jd=birth_jd,
            birth_datetime_str=birth_datetime_str,
            birth_lat=latitude,
            birth_lon=longitude,
            birth_tz=timezone,
            epoch_jd=epoch_jd,
            epoch_datetime_str=epoch_datetime_str,
            gestation_days=actual_gestation,
            natal_planets=natal_planets,
            natal_asc=natal_asc,
            natal_mc=natal_mc,
            natal_dsc=natal_dsc,
            natal_ic=natal_ic,
            natal_house_cusps=natal_house_cusps,
            epoch_planets=epoch_planets,
            epoch_asc=epoch_asc,
            epoch_mc=epoch_mc,
            epoch_dsc=epoch_dsc,
            epoch_ic=epoch_ic,
            epoch_house_cusps=epoch_house_cusps,
            natal_moon_lon=natal_moon_lon,
            moon_above_horizon=moon_above,
            moon_phase_name=moon_phase_name,
            moon_elongation=moon_elongation,
            is_waxing=is_waxing,
            epoch_angle=epoch_angle,
            trutine_match_orb=trutine_orb,
            trutine_verified=trutine_verified,
            cross_aspects=cross_aspects,
            soul_interpretations=soul_interps,
            rectification_note=rect_note,
        )

    except Exception as exc:
        # Return a minimal chart with error info
        return PrenatalEpochChart(
            variant=str(variant),
            birth_jd=0.0,
            birth_datetime_str="",
            birth_lat=latitude,
            birth_lon=longitude,
            birth_tz=timezone,
            epoch_jd=0.0,
            epoch_datetime_str="",
            gestation_days=0.0,
            error=str(exc),
        )
