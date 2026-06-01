"""
astro/picatrix_behenian/calculator.py — Behenian Star Orb Detection & Magic Logic

Implements:
  1. ``detect_activations`` — find which Behenian stars are activated for a
     given set of planet/point longitudes (default orb 6°).
  2. ``compute_today_magic``  — wrapper that computes current sky positions
     and returns active stars.
  3. ``find_electional_windows`` — scan forward in time to find when the Moon
     applies to each Behenian star while the correct planetary ruler is
     dignified or strongly placed.

Sources
-------
  • Agrippa, *De Occulta Philosophia* Bk I ch. 32 (1531) — orb and procedure
  • *Ghayat al-Hakim* (Picatrix) Bk II ch. 12 — moon timing rules
  • Hermes Trismegistus, *Liber Hermetis de XV Stellis*
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import swisseph as swe

from .constants import (
    BEHENIAN_STARS,
    BehenianStar,
    BEHENIAN_ORB,
    BEHENIAN_STRONG_ORB,
    RULER_CN,
)


# ============================================================
# Swiss Ephemeris planet ID map
# ============================================================

_PLANET_IDS: dict[str, int] = {
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


# ============================================================
# Data Classes
# ============================================================

@dataclass
class BehenianActivation:
    """
    A single activation: one celestial body within orb of a Behenian star.

    Attributes
    ----------
    star : BehenianStar
        The activated Behenian fixed star.
    point_name : str
        Name of the natal / transiting point (e.g. "Moon", "Ascendant").
    point_longitude : float
        Ecliptic longitude of the point (degrees).
    star_longitude : float
        Computed ecliptic longitude of the star for the given JD.
    orb : float
        Angular separation between point and star (degrees, 0–180).
    is_strong : bool
        True if orb ≤ BEHENIAN_STRONG_ORB (1°).
    applying : Optional[bool]
        True  → point is approaching the star (applying conjunction)
        False → point has passed the star (separating)
        None  → not applicable (no speed info)
    ruler_active : bool
        True if the primary planetary ruler is also prominent in the chart
        (for talisman-making eligibility).
    """

    star: BehenianStar
    point_name: str
    point_longitude: float
    star_longitude: float
    orb: float
    is_strong: bool = False
    applying: Optional[bool] = None
    ruler_active: bool = False

    @property
    def star_name(self) -> str:
        return self.star.name

    @property
    def activation_level(self) -> str:
        """Return a human-readable activation level."""
        if self.orb <= BEHENIAN_STRONG_ORB:
            return "強烈激活 (Strong)"
        if self.orb <= 3.0:
            return "中等激活 (Moderate)"
        return "輕微激活 (Weak)"


@dataclass
class TodayMagicResult:
    """
    Aggregated result for the "今日魔法 Today's Magic" feature.

    Attributes
    ----------
    jd : float
        Julian Day for the query time.
    activations : list[BehenianActivation]
        All active Behenian stars at the query time.
    moon_longitude : float
        Current Moon ecliptic longitude.
    moon_sign : str
        Zodiac sign name of the Moon.
    moon_sign_degree : float
        Degree within the sign.
    """

    jd: float
    activations: List[BehenianActivation] = field(default_factory=list)
    moon_longitude: float = 0.0
    moon_sign: str = ""
    moon_sign_degree: float = 0.0


@dataclass
class ElectionalWindow:
    """
    A future time window suitable for making a specific Behenian talisman.

    Attributes
    ----------
    star : BehenianStar
        The target Behenian star.
    dt_utc : datetime
        UTC datetime of the window midpoint.
    jd : float
        Julian Day (UT) of the window midpoint.
    moon_longitude : float
        Moon longitude at that moment.
    orb : float
        Moon–star angular separation.
    ruler_longitude : float
        Longitude of the primary planetary ruler at that time.
    ruler_sign : str
        Zodiac sign of the ruler.
    applying : bool
        True if Moon is applying to the star.
    """

    star: BehenianStar
    dt_utc: datetime
    jd: float
    moon_longitude: float
    orb: float
    ruler_longitude: float
    ruler_sign: str
    applying: bool = True


# ============================================================
# Utility helpers
# ============================================================

_ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def _arc_sep(lon_a: float, lon_b: float) -> float:
    """Return the shortest arc between two ecliptic longitudes (0–180°)."""
    diff = abs(lon_a - lon_b) % 360.0
    return min(diff, 360.0 - diff)


def _sign_of(lon: float) -> str:
    return _ZODIAC_SIGNS[int(lon / 30) % 12]


def _jd_utc(year: int, month: int, day: int,
            hour: int = 12, minute: int = 0,
            timezone_offset: float = 0.0) -> float:
    """Convert calendar date/time to Julian Day (UT)."""
    ut_hour = hour + minute / 60.0 - timezone_offset
    jd, _ = swe.utc_to_jd(year, month, day,
                            int(ut_hour),
                            int((ut_hour % 1) * 60),
                            0.0,
                            swe.GREG_CAL)
    return jd


def _compute_star_longitude(star: BehenianStar, jd: float) -> float:
    """
    Compute the ecliptic longitude of a Behenian star for Julian Day *jd*.

    Falls back to the hardcoded approximate longitude if the Swiss Ephemeris
    lookup fails (e.g. star not in the ephemeris files).
    """
    try:
        swe_name = star.swe_name if star.swe_name else star.name
        _name_out, xx = swe.fixstar_ut(swe_name, jd)
        return float(xx[0])
    except Exception:
        return star.longitude  # use hardcoded fallback


def _compute_planet_lon(planet_id: int, jd: float) -> tuple[float, float]:
    """Return (longitude, speed_deg_per_day) for the given planet."""
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    xx, _ = swe.calc_ut(jd, planet_id, flags)
    return float(xx[0]), float(xx[3])


# ============================================================
# Core Detection
# ============================================================

def detect_activations(
    point_positions: dict[str, float],
    jd: float,
    orb: float = BEHENIAN_ORB,
    point_speeds: Optional[dict[str, float]] = None,
    ruler_positions: Optional[dict[str, float]] = None,
) -> List[BehenianActivation]:
    """
    Find Behenian star activations for a given set of point positions.

    Parameters
    ----------
    point_positions : dict[str, float]
        Mapping of {point_name: ecliptic_longitude}.  Keys can be planet
        names, "Ascendant", "MC", "Part of Fortune", etc.
    jd : float
        Julian Day for star position computation.
    orb : float
        Maximum orb in degrees (default: BEHENIAN_ORB = 6°).
    point_speeds : dict[str, float], optional
        Mapping of {point_name: speed_deg_per_day}.  If provided, used to
        determine applying vs separating.
    ruler_positions : dict[str, float], optional
        Mapping of {planet_name: longitude}.  Used to flag ``ruler_active``.

    Returns
    -------
    list[BehenianActivation]
        Sorted by orb (tightest first).
    """
    activations: List[BehenianActivation] = []

    for star in BEHENIAN_STARS:
        star_lon = _compute_star_longitude(star, jd)

        for point_name, point_lon in point_positions.items():
            sep = _arc_sep(point_lon, star_lon)
            if sep > orb:
                continue

            # Determine applying vs separating
            applying: Optional[bool] = None
            if point_speeds and point_name in point_speeds:
                speed = point_speeds[point_name]
                diff = (star_lon - point_lon) % 360.0
                if diff > 180.0:
                    diff -= 360.0
                # Positive speed: planet moving forward (direct)
                # Applying: diff > 0 and speed > 0, or diff < 0 and speed < 0
                applying = (diff * speed) > 0

            # Flag if primary ruler is strongly placed (within 10° of an angle
            # or in the same sign)
            ruler_active = False
            if ruler_positions:
                ruler_name = star.primary_ruler
                if ruler_name in ruler_positions:
                    r_lon = ruler_positions[ruler_name]
                    # Ruler is "active" if in the same sign as the activated point
                    point_sign_idx = int(point_lon / 30) % 12
                    ruler_sign_idx = int(r_lon / 30) % 12
                    ruler_active = (point_sign_idx == ruler_sign_idx) or (
                        _arc_sep(r_lon, point_lon) <= 10.0
                    )

            activations.append(BehenianActivation(
                star=star,
                point_name=point_name,
                point_longitude=point_lon,
                star_longitude=star_lon,
                orb=round(sep, 4),
                is_strong=sep <= BEHENIAN_STRONG_ORB,
                applying=applying,
                ruler_active=ruler_active,
            ))

    activations.sort(key=lambda a: a.orb)
    return activations


# ============================================================
# Today's Magic
# ============================================================

def compute_today_magic(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0,
    timezone_offset: float = 0.0,
    orb: float = BEHENIAN_ORB,
) -> TodayMagicResult:
    """
    Compute which Behenian stars are magically active at a given date/time.

    Positions for Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn are
    calculated via pyswisseph and checked against all 15 Behenian stars.

    Parameters
    ----------
    year, month, day : int
        Calendar date (proleptic Gregorian).
    hour, minute : int
        Local time.
    timezone_offset : float
        Hours east of UTC (e.g. +8 for HKT).
    orb : float
        Activation orb in degrees (default 6°).

    Returns
    -------
    TodayMagicResult
    """
    jd = _jd_utc(year, month, day, hour, minute, timezone_offset)

    point_positions: dict[str, float] = {}
    point_speeds: dict[str, float] = {}

    for pname, pid in _PLANET_IDS.items():
        try:
            lon, speed = _compute_planet_lon(pid, jd)
            point_positions[pname] = lon
            point_speeds[pname] = speed
        except Exception:
            pass

    activations = detect_activations(
        point_positions, jd, orb=orb,
        point_speeds=point_speeds,
        ruler_positions=point_positions,
    )

    moon_lon = point_positions.get("Moon", 0.0)
    moon_sign = _sign_of(moon_lon)
    moon_sign_degree = round(moon_lon % 30, 2)

    return TodayMagicResult(
        jd=jd,
        activations=activations,
        moon_longitude=moon_lon,
        moon_sign=moon_sign,
        moon_sign_degree=moon_sign_degree,
    )


# ============================================================
# Electional Windows
# ============================================================

def find_electional_windows(
    star_names: Optional[List[str]] = None,
    start_dt: Optional[datetime] = None,
    days_ahead: int = 30,
    step_hours: int = 4,
    orb: float = 4.0,
) -> List[ElectionalWindow]:
    """
    Scan forward in time to find windows for Behenian talisman making.

    A window is valid when:
      1. Moon is within *orb* degrees of the target star.
      2. Moon is **applying** (approaching) the star.

    Picatrix (Bk II ch. 12) requires that the talisman be made while the
    Moon is moving toward the star, not separating from it.

    Parameters
    ----------
    star_names : list[str], optional
        Names of Behenian stars to search for.  None → all 15.
    start_dt : datetime, optional
        Start of search window (UTC).  Defaults to now.
    days_ahead : int
        Number of days to scan ahead (default: 30).
    step_hours : int
        Time resolution in hours (default: 4 h).
    orb : float
        Moon–star orb for electional purposes (default: 4°, tighter than the
        6° natal detection orb).

    Returns
    -------
    list[ElectionalWindow]
        Sorted by datetime.
    """
    if start_dt is None:
        start_dt = datetime.now(tz=timezone.utc)
    else:
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)

    target_stars = [s for s in BEHENIAN_STARS
                    if star_names is None or s.name in star_names]

    windows: List[ElectionalWindow] = []
    step = timedelta(hours=step_hours)
    total_steps = int(days_ahead * 24 / step_hours)

    for i in range(total_steps):
        dt = start_dt + i * step
        jd = swe.julday(dt.year, dt.month, dt.day,
                        dt.hour + dt.minute / 60.0 + dt.second / 3600.0)

        try:
            moon_lon, moon_speed = _compute_planet_lon(swe.MOON, jd)
        except Exception:
            continue

        for star in target_stars:
            star_lon = _compute_star_longitude(star, jd)
            sep = _arc_sep(moon_lon, star_lon)
            if sep > orb:
                continue

            # Check applying
            diff = (star_lon - moon_lon) % 360.0
            if diff > 180.0:
                diff -= 360.0
            applying = (diff * moon_speed) > 0
            if not applying:
                continue

            # Ruler longitude
            ruler_id = _PLANET_IDS.get(star.primary_ruler, swe.SUN)
            try:
                ruler_lon, _ = _compute_planet_lon(ruler_id, jd)
            except Exception:
                ruler_lon = 0.0

            windows.append(ElectionalWindow(
                star=star,
                dt_utc=dt,
                jd=jd,
                moon_longitude=moon_lon,
                orb=round(sep, 3),
                ruler_longitude=ruler_lon,
                ruler_sign=_sign_of(ruler_lon),
                applying=True,
            ))

    windows.sort(key=lambda w: w.jd)
    return windows


# ============================================================
# Convenience: compute natal activations from a western chart
# ============================================================

def activations_from_chart(
    chart,
    orb: float = BEHENIAN_ORB,
) -> List[BehenianActivation]:
    """
    Derive Behenian activations from a pre-computed western chart object.

    Accepts the ``WesternChart`` objects returned by
    ``astro.western.western.compute_western_chart``.

    Parameters
    ----------
    chart : WesternChart
        The natal (or event) chart.
    orb : float
        Orb in degrees.

    Returns
    -------
    list[BehenianActivation]
    """
    point_positions: dict[str, float] = {}
    point_speeds: dict[str, float] = {}

    # Planets
    for p in chart.planets:
        pname = p.name.split("(")[0].strip().split()[0]
        point_positions[pname] = p.longitude
        if hasattr(p, "speed"):
            point_speeds[pname] = p.speed

    # Angles
    if hasattr(chart, "asc") and chart.asc is not None:
        point_positions["Ascendant"] = chart.asc
    if hasattr(chart, "mc") and chart.mc is not None:
        point_positions["MC"] = chart.mc

    # Part of Fortune
    if hasattr(chart, "part_of_fortune") and chart.part_of_fortune is not None:
        point_positions["Part of Fortune"] = chart.part_of_fortune

    return detect_activations(
        point_positions,
        chart.julian_day,
        orb=orb,
        point_speeds=point_speeds if point_speeds else None,
        ruler_positions=point_positions,
    )
