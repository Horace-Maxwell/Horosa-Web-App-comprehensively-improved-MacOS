"""
astro/western_transit.py — 西洋占星流年過運 (Western Transits)

Computes transit planet positions and aspects to natal chart.
"""
import streamlit as st
import swisseph as swe
from dataclasses import dataclass, field

from astro.interpretations import get_transit_reading

WESTERN_PLANETS = {
    "Sun ☉": swe.SUN, "Moon ☽": swe.MOON, "Mercury ☿": swe.MERCURY,
    "Venus ♀": swe.VENUS, "Mars ♂": swe.MARS, "Jupiter ♃": swe.JUPITER,
    "Saturn ♄": swe.SATURN, "Uranus ♅": swe.URANUS,
    "Neptune ♆": swe.NEPTUNE, "Pluto ♇": swe.PLUTO,
}

ASPECT_TYPES = [
    {"name": "Conjunction (合)", "symbol": "☌", "angle": 0, "orb": 8},
    {"name": "Opposition (沖)", "symbol": "☍", "angle": 180, "orb": 8},
    {"name": "Trine (三合)", "symbol": "△", "angle": 120, "orb": 6},
    {"name": "Square (刑)", "symbol": "□", "angle": 90, "orb": 6},
    {"name": "Sextile (六合)", "symbol": "⚹", "angle": 60, "orb": 4},
]

ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def _normalize(deg):
    return deg % 360.0


def _angle_diff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


@dataclass
class TransitAspect:
    transit_planet: str
    natal_planet: str
    aspect_name: str
    aspect_symbol: str
    aspect_angle: float
    orb: float
    is_applying: bool
    interpretation_en: str
    interpretation_cn: str


@dataclass
class TransitResult:
    transit_date: str
    transit_jd: float
    transit_planets: list   # list of (name, lon, sign, degree, retrograde)
    aspects_to_natal: list  # list of TransitAspect


@st.cache_data(ttl=3600, show_spinner=False)
def compute_western_transits(natal_chart, year, month, day,
                             hour=12, minute=0, timezone=0.0):
    """Compute transit aspects to natal chart for a given date."""
    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    # Transit positions
    transit_planets = []
    transit_lons = {}
    for name, pid in WESTERN_PLANETS.items():
        xx, _ = swe.calc_ut(jd, pid)
        lon = xx[0]
        speed = xx[3] if len(xx) > 3 else 0
        idx = int(lon / 30) % 12
        transit_planets.append((name, lon, ZODIAC_SIGNS[idx],
                                round(lon % 30, 2), speed < 0))
        transit_lons[name] = (lon, speed)

    # Natal positions
    natal_lons = {}
    for p in natal_chart.planets:
        natal_lons[p.name] = p.longitude

    # Find aspects
    aspects = []
    for t_name, (t_lon, t_speed) in transit_lons.items():
        for n_name, n_lon in natal_lons.items():
            diff = _angle_diff(t_lon, n_lon)
            for asp in ASPECT_TYPES:
                orb = abs(diff - asp["angle"])
                if orb <= asp["orb"]:
                    is_applying = t_speed > 0  # simplified
                    aspects.append(TransitAspect(
                        transit_planet=t_name, natal_planet=n_name,
                        aspect_name=asp["name"], aspect_symbol=asp["symbol"],
                        aspect_angle=asp["angle"], orb=round(orb, 2),
                        is_applying=is_applying,
                        interpretation_en=get_transit_reading(t_name, n_name, asp["name"], "en"),
                        interpretation_cn=get_transit_reading(t_name, n_name, asp["name"], "zh"),
                    ))

    aspects.sort(key=lambda a: a.orb)

    return TransitResult(
        transit_date=f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}",
        transit_jd=jd, transit_planets=transit_planets,
        aspects_to_natal=aspects,
    )
