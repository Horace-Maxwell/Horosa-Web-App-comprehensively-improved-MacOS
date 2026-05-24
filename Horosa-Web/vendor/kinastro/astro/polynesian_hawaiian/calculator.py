"""
Polynesian / Hawaiian Star Lore Calculator

Detects rising, setting, and culminating stars; identifies 32-house compass
positions; computes the guardian house (where Hōkūleʻa stood at birth).
"""

import math
from dataclasses import dataclass, field
from typing import Optional

import swisseph as swe

from .constants import HAWAIIAN_STARS, COMPASS_HOUSES, STAR_LINES, SEASONS

# ============================================================
# Star-status classification thresholds
# ============================================================
# Altitude range (degrees) around the horizon used to classify a star as rising/setting.
HORIZON_THRESHOLD_DEG: float = 2.0
# Minimum altitude (degrees) for a star to be considered culminating (near meridian).
CULMINATION_ALT_THRESHOLD: float = 60.0
# Maximum absolute hour angle (degrees) for a star to be considered at culmination.
CULMINATION_HA_THRESHOLD: float = 15.0

# ============================================================
# Swiss Ephemeris initialisation
# ============================================================

def _init_swe() -> None:
    """Set ephemeris path if local data exists, else fall back to built-in."""
    import os
    ephe_path = os.path.join(os.path.dirname(__file__), "..", "data", "ephe")
    if os.path.isdir(ephe_path):
        swe.set_ephe_path(ephe_path)
    else:
        swe.set_ephe_path("")


# ============================================================
# Result dataclass
# ============================================================

@dataclass
class PolynesianResult:
    """Full result of a Polynesian / Hawaiian star lore calculation."""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    lat: float
    lon: float
    timezone_offset: float
    location_name: str

    star_positions: list = field(default_factory=list)
    """Per-star dicts with name, hawaiian_name, altitude, azimuth, status."""

    rising_stars: list = field(default_factory=list)
    """Stars currently near the eastern horizon (rising)."""

    setting_stars: list = field(default_factory=list)
    """Stars currently near the western horizon (setting)."""

    culminating_stars: list = field(default_factory=list)
    """Stars near upper culmination (high altitude, hour angle ≈ 0)."""

    guardian_house: dict = field(default_factory=dict)
    """The 32-house compass house where Hōkūleʻa stood at the birth moment."""

    guardian_star: dict = field(default_factory=dict)
    """Full HAWAIIAN_STARS entry for Hōkūleʻa (Arcturus)."""

    season: str = ""
    """Current Hawaiian season name ('Makahiki', 'Hoʻoilo', or 'Kau')."""

    season_info: dict = field(default_factory=dict)
    """Full SEASONS entry for the detected season."""

    compass_house_highlight: int = 0
    """Index (0-31) of the highlighted compass house."""


# ============================================================
# Helper: Julian Day
# ============================================================

def _julian_day(year: int, month: int, day: int,
                hour: float, tz_offset: float) -> float:
    """Convert local time to Julian Day (UT)."""
    ut_hour = hour - tz_offset
    return swe.julday(year, month, day, ut_hour)


# ============================================================
# Helper: Local Sidereal Time
# ============================================================

def _local_sidereal_time(jd_ut: float, lon_deg: float) -> float:
    """Return Local Sidereal Time in degrees [0, 360)."""
    # Greenwich Mean Sidereal Time via swe.sidtime returns decimal hours
    gmst_hours = swe.sidtime(jd_ut)
    lst_hours = gmst_hours + lon_deg / 15.0
    lst_deg = (lst_hours * 15.0) % 360.0
    return lst_deg


# ============================================================
# Helper: Altitude & Azimuth
# ============================================================

def _alt_az(ra_deg: float, dec_deg: float,
             lst_deg: float, lat_deg: float) -> tuple[float, float]:
    """
    Compute altitude and azimuth (from North, clockwise) for a star.

    Parameters
    ----------
    ra_deg  : Right Ascension in degrees
    dec_deg : Declination in degrees
    lst_deg : Local Sidereal Time in degrees
    lat_deg : Observer latitude in degrees

    Returns
    -------
    (altitude_deg, azimuth_deg)  both in degrees
    """
    ha_deg = (lst_deg - ra_deg) % 360.0  # hour angle
    ha = math.radians(ha_deg)
    dec = math.radians(dec_deg)
    lat = math.radians(lat_deg)

    sin_alt = (math.sin(dec) * math.sin(lat)
               + math.cos(dec) * math.cos(lat) * math.cos(ha))
    sin_alt = max(-1.0, min(1.0, sin_alt))
    alt = math.degrees(math.asin(sin_alt))

    cos_az_num = math.sin(dec) - math.sin(alt) * math.sin(lat)
    cos_az_den = math.cos(math.radians(alt)) * math.cos(lat)
    if abs(cos_az_den) < 1e-9:
        az = 0.0
    else:
        cos_az = cos_az_num / cos_az_den
        cos_az = max(-1.0, min(1.0, cos_az))
        az = math.degrees(math.acos(cos_az))
        if math.sin(ha) > 0:
            # HA > 0 means the star is west of the meridian (setting side);
            # the standard formula gives az measured from N, so we mirror it.
            az = 360.0 - az

    return alt, az


# ============================================================
# Helper: Get star RA/Dec via Swiss Ephemeris
# ============================================================

def _star_ra_dec(swe_name: str, jd_ut: float,
                 fallback_ra: float, fallback_dec: float) -> tuple[float, float]:
    """
    Retrieve equatorial coordinates (RA, Dec) for a fixed star.

    Falls back to approximate hard-coded values if the ephemeris file is missing.
    Returns (ra_degrees, dec_degrees).
    """
    try:
        _name_out, xx = swe.fixstar_ut(swe_name, jd_ut, swe.FLG_EQUATORIAL)
        return float(xx[0]), float(xx[1])
    except Exception:
        pass

    # Second attempt: ecliptic → equatorial via swe.cotrans
    try:
        _name_out, xx = swe.fixstar_ut(swe_name, jd_ut)
        ecl_lon, ecl_lat = float(xx[0]), float(xx[1])
        eps = swe.calc_ut(jd_ut, swe.ECL_NUT)[0][0]  # obliquity
        eq = swe.cotrans([ecl_lon, ecl_lat, 1.0], -eps)
        return float(eq[0]), float(eq[1])
    except Exception:
        return fallback_ra, fallback_dec


# ============================================================
# Helper: Compass house lookup
# ============================================================

def compass_house_for_azimuth(azimuth_deg: float) -> dict:
    """
    Return the COMPASS_HOUSES entry whose midpoint is closest to *azimuth_deg*.
    """
    az = azimuth_deg % 360.0
    best = COMPASS_HOUSES[0]
    best_dist = 180.0
    for house in COMPASS_HOUSES:
        d = abs((house["direction_deg"] - az + 180.0) % 360.0 - 180.0)
        if d < best_dist:
            best_dist = d
            best = house
    return best


# ============================================================
# Helper: Season detection
# ============================================================

def _detect_season(month: int) -> tuple[str, dict]:
    """Return (season_name, season_dict) for the given calendar month."""
    if month in (11, 12, 1, 2):
        name = "Makahiki"
    elif month in (5, 6, 7, 8, 9, 10):
        name = "Kau"
    else:
        name = "Hoʻoilo"
    return name, SEASONS[name]


# ============================================================
# Main computation
# ============================================================

def compute_polynesian_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    lat: float,
    lon: float,
    timezone_offset: float,
    location_name: str = "",
) -> PolynesianResult:
    """
    Compute a Polynesian / Hawaiian star lore chart.

    Parameters
    ----------
    year, month, day : birth date
    hour, minute     : birth local time (24-hour)
    lat, lon         : observer latitude / longitude (degrees)
    timezone_offset  : hours east of UTC (negative for west)
    location_name    : optional place name string

    Returns
    -------
    PolynesianResult  populated with star positions, guardian house, season.
    """
    _init_swe()

    decimal_hour = hour + minute / 60.0
    jd_ut = _julian_day(year, month, day, decimal_hour, timezone_offset)
    lst_deg = _local_sidereal_time(jd_ut, lon)

    star_positions: list[dict] = []
    rising_stars: list[dict] = []
    setting_stars: list[dict] = []
    culminating_stars: list[dict] = []

    guardian_house: dict = {}
    guardian_star: dict = {}

    for western_name, info in HAWAIIAN_STARS.items():
        swe_name = info.get("swe_name", western_name)
        fallback_ra = info.get("ra_approx", 0.0)
        fallback_dec = info.get("dec_approx", 0.0)

        ra, dec = _star_ra_dec(swe_name, jd_ut, fallback_ra, fallback_dec)
        alt, az = _alt_az(ra, dec, lst_deg, lat)

        ha_deg = (lst_deg - ra) % 360.0
        # Normalise to [-180, 180]
        if ha_deg > 180.0:
            ha_deg -= 360.0

        # Determine status
        if -HORIZON_THRESHOLD_DEG <= alt <= HORIZON_THRESHOLD_DEG:
            status = "rising" if ha_deg < 0 else "setting"
        elif alt > CULMINATION_ALT_THRESHOLD and abs(ha_deg) < CULMINATION_HA_THRESHOLD:
            status = "culminating"
        elif alt > 0.0:
            status = "above"
        else:
            status = "below"

        house = compass_house_for_azimuth(az)

        entry = {
            "western_name": western_name,
            "hawaiian_name": info["hawaiian_name"],
            "ra": ra,
            "dec": dec,
            "altitude": alt,
            "azimuth": az,
            "hour_angle": ha_deg,
            "status": status,
            "compass_house": house,
            "magnitude": info.get("magnitude", 99.0),
            "meaning": info["meaning"],
            "meaning_cn": info["meaning_cn"],
            "star_line": info.get("star_line", ""),
            "star_line_cn": info.get("star_line_cn", ""),
            "mythology": info.get("mythology", ""),
            "mythology_cn": info.get("mythology_cn", ""),
        }
        star_positions.append(entry)

        if status == "rising":
            rising_stars.append(entry)
        elif status == "setting":
            setting_stars.append(entry)
        elif status == "culminating":
            culminating_stars.append(entry)

        if western_name == "Arcturus":
            guardian_house = house
            guardian_star = {**info, "ra": ra, "dec": dec,
                             "altitude": alt, "azimuth": az}

    # Sort by magnitude (brightest first)
    star_positions.sort(key=lambda x: x["magnitude"])

    season_name, season_info = _detect_season(month)

    return PolynesianResult(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        lat=lat, lon=lon,
        timezone_offset=timezone_offset,
        location_name=location_name,
        star_positions=star_positions,
        rising_stars=rising_stars,
        setting_stars=setting_stars,
        culminating_stars=culminating_stars,
        guardian_house=guardian_house,
        guardian_star=guardian_star,
        season=season_name,
        season_info=season_info,
        compass_house_highlight=guardian_house.get("index", 0),
    )
