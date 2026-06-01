"""
astro/sumerian/calculator.py — Sumerian / Mesopotamian Astrology Computation Engine

Implements:
1. Sidereal planetary positions via pyswisseph (Fagan-Bradley ayanamsa)
2. Mapping to Mesopotamian deities (Enūma Anu Enlil standard)
3. 12 Akkadian zodiac sign placement (MUL.APIN tradition)
4. Three sky paths: Path of Enlil / Anu / Ea (MUL.APIN declination bands)
5. K.8538 planisphere 8-sector placement
6. Omen interpretation engine (30+ Enūma Anu Enlil style rules)
7. Venus morning/evening star classification
8. MUL.APIN heliacal rising stars for the current month

Sources:
- Hunger & Pingree, "MUL.APIN: An Astronomical Compendium in Cuneiform" (1989)
- Koch-Westenholz, "Mesopotamian Astrology" (1995)
- Rochberg, "The Heavenly Writing" (2004)
- van der Waerden, "Science Awakening II" (1974)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import swisseph as swe
import streamlit as st

from .constants import (
    SUMERIAN_ZODIAC_SIGNS,
    ZODIAC_SIGN_ORDER,
    AKKADIAN_NAME,
    SIGN_CN,
    SIGN_EN,
    MESOPOTAMIAN_DEITIES,
    MULAPIN_PATHS,
    MULAPIN_36_STARS,
    K8538_SECTORS,
    DOMICILE,
    EXALTATION,
    DETRIMENT,
    FALL,
    EAE_OMENS,
    _get_planet_condition,
)

# ============================================================
# Swiss Ephemeris configuration
# ============================================================
_SIDEREAL_MODE = swe.SIDM_FAGAN_BRADLEY   # same as babylonian.py

_PLANET_IDS: Dict[str, int] = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
}

# ============================================================
# Data Classes
# ============================================================

@dataclass
class MesopotamianPlanet:
    """Position and attributes of a single planet in the Mesopotamian system."""
    name: str                  # Modern name (Sun, Moon, …)
    akkadian: str              # Deity Akkadian name (Šamaš, Sîn, …)
    sumerian: str              # Deity Sumerian name (dUTU, dEN.ZU, …)
    role_cn: str               # Deity role (Chinese)
    role_en: str               # Deity role (English)
    longitude: float           # Sidereal ecliptic longitude 0–360°
    sign_idx: int              # 0–11 in sidereal zodiac
    sign_western: str          # e.g. "Aries"
    sign_akkadian: str         # e.g. "LU.HUN.GA"
    sign_cn: str               # e.g. "雇農/雇工"
    sign_en: str               # e.g. "The Hired Man"
    degree_in_sign: float      # 0–30°
    house: int                 # 1–12
    is_retrograde: bool
    condition: str             # domicile / exalt / detriment / fall / neutral
    declination: float         # celestial declination
    path: str                  # Enlil / Anu / Ea
    sector: int                # K.8538 sector index 0–7
    color: str                 # display colour
    glyph: str                 # Unicode planet glyph


@dataclass
class MesopotamianOmen:
    """Single Enūma Anu Enlil style omen."""
    planet: str
    deity_name: str
    sign: Optional[str]        # None for non-sign phenomena
    condition: str
    text_cn: str
    text_en: str
    severity: str              # "auspicious" / "inauspicious" / "neutral"


@dataclass
class MesopotamianChart:
    """Complete Sumerian / Mesopotamian natal chart."""
    # Birth data
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude_birth: float
    location_name: str = ""

    # Computed values
    julian_day: float = 0.0
    ayanamsa: float = 0.0
    ascendant: float = 0.0
    midheaven: float = 0.0
    is_day_chart: bool = True
    house_cusps: List[float] = field(default_factory=list)

    # Planets
    planets: List[MesopotamianPlanet] = field(default_factory=list)

    # Omens
    omens: List[MesopotamianOmen] = field(default_factory=list)

    # Venus phase
    venus_phase: str = "unknown"   # morning_star / evening_star / unknown

    # K.8538 sector data (8 entries)
    sectors: List[Dict] = field(default_factory=list)

    # MUL.APIN stars visible this birth month
    heliacal_stars: List[Dict] = field(default_factory=list)

    # Planetary aspects
    aspects: List[Dict] = field(default_factory=list)


# ============================================================
# Internal helpers
# ============================================================

def _sign_idx(lon: float) -> int:
    """Return sidereal sign index (0–11) for ecliptic longitude."""
    return int(lon / 30.0) % 12


def _deg_in_sign(lon: float) -> float:
    """Return degree within sign (0–30)."""
    return lon % 30.0


def _find_house(lon: float, cusps: List[float]) -> int:
    """Return house number (1–12) for an ecliptic longitude."""
    for i in range(12):
        c1 = cusps[i]
        c2 = cusps[(i + 1) % 12]
        if c2 < c1:
            if lon >= c1 or lon < c2:
                return i + 1
        elif c1 <= lon < c2:
            return i + 1
    return 1


def _classify_path(declination: float) -> str:
    """Classify a celestial object into one of the three MUL.APIN paths."""
    if declination > 17.0:
        return "Enlil"
    if declination < -17.0:
        return "Ea"
    return "Anu"


def _k8538_sector(lon: float) -> int:
    """Return K.8538 planisphere sector index (0–7) for sidereal longitude."""
    return int(lon / 45.0) % 8


_MAJOR_ASPECTS: List[Tuple] = [
    ("conjunction", 0, 8),
    ("opposition", 180, 8),
    ("trine", 120, 7),
    ("square", 90, 7),
    ("sextile", 60, 6),
]


def _compute_aspects(planet_lons: Dict[str, float]) -> List[Dict]:
    """Compute major aspects between classical planets."""
    aspects: List[Dict] = []
    names = list(planet_lons.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]
            diff = abs(planet_lons[p1] - planet_lons[p2])
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


def _classify_venus_phase(venus_lon: float, sun_lon: float) -> str:
    """Classify Venus as morning star (Ištar ascending) or evening star."""
    diff = (venus_lon - sun_lon) % 360
    # Morning star: Venus rises before Sun (elongation 0–180 behind)
    if 0 < diff < 180:
        return "morning_star"
    return "evening_star"


def _find_omens(
    planet_name: str,
    sign_idx: int,
    condition: str,
    venus_phase: str = "",
    is_retrograde: bool = False,
) -> List[MesopotamianOmen]:
    """Match Enūma Anu Enlil omen rules for a planet."""
    matched: List[MesopotamianOmen] = []
    sign_western = ZODIAC_SIGN_ORDER[sign_idx] if 0 <= sign_idx < 12 else None
    deity = MESOPOTAMIAN_DEITIES.get(planet_name, {})
    deity_name = deity.get("akkadian", planet_name)

    for rule in EAE_OMENS:
        if rule["planet"] != planet_name:
            continue
        rule_cond = rule["condition"]
        rule_sign = rule.get("sign")

        # Non-sign phenomenon checks
        if rule_cond == "morning_star" and planet_name == "Venus":
            if venus_phase == "morning_star":
                matched.append(MesopotamianOmen(
                    planet=planet_name, deity_name=deity_name,
                    sign=None, condition=rule_cond,
                    text_cn=rule["cn"], text_en=rule["en"],
                    severity="neutral",
                ))
            continue
        if rule_cond == "evening_star" and planet_name == "Venus":
            if venus_phase == "evening_star":
                matched.append(MesopotamianOmen(
                    planet=planet_name, deity_name=deity_name,
                    sign=None, condition=rule_cond,
                    text_cn=rule["cn"], text_en=rule["en"],
                    severity="auspicious",
                ))
            continue
        if rule_cond == "retrograde":
            if is_retrograde:
                matched.append(MesopotamianOmen(
                    planet=planet_name, deity_name=deity_name,
                    sign=None, condition=rule_cond,
                    text_cn=rule["cn"], text_en=rule["en"],
                    severity="inauspicious",
                ))
            continue
        if rule_cond == "heliacal_rising":
            # Always show for Jupiter as a generic auspicious note
            matched.append(MesopotamianOmen(
                planet=planet_name, deity_name=deity_name,
                sign=None, condition=rule_cond,
                text_cn=rule["cn"], text_en=rule["en"],
                severity="auspicious",
            ))
            continue

        # Sign-specific omen: match sign AND condition
        if rule_sign and rule_sign == sign_western and rule_cond == condition:
            severity = "auspicious" if condition in ("domicile", "exalt") else "inauspicious"
            matched.append(MesopotamianOmen(
                planet=planet_name, deity_name=deity_name,
                sign=sign_western, condition=condition,
                text_cn=rule["cn"], text_en=rule["en"],
                severity=severity,
            ))

    return matched


def _build_sectors(planets: List[MesopotamianPlanet]) -> List[Dict]:
    """Build K.8538 8-sector summary mapping planets to their sectors."""
    sector_map: Dict[int, List[str]] = {i: [] for i in range(8)}
    for p in planets:
        sector_map[p.sector].append(f"{p.glyph} {p.akkadian}")

    result: List[Dict] = []
    for sec in K8538_SECTORS:
        idx = sec["index"]
        result.append({
            **sec,
            "planets_present": sector_map[idx],
        })
    return result


def _heliacal_stars_for_month(month: int) -> List[Dict]:
    """Return MUL.APIN 36-star entries visible in the given calendar month."""
    # Map Gregorian month (1–12) to Babylonian month index (0–11)
    # Approximate: Babylonian Nisannu I ~ Gregorian April
    bab_month = (month - 4) % 12
    return [s for s in MULAPIN_36_STARS if s["month"] == bab_month]


# ============================================================
# Main compute function
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_sumerian_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    lat: float,
    lon: float,
    location_name: str = "",
) -> MesopotamianChart:
    """Compute a Sumerian / Mesopotamian natal chart.

    Parameters
    ----------
    year, month, day : int  — Gregorian birth date.
    hour, minute : int      — Local birth time.
    timezone : float        — UTC offset in hours.
    lat, lon : float        — Geographic coordinates.
    location_name : str     — Optional display name.

    Returns
    -------
    MesopotamianChart
    """
    # Julian Day (Universal Time)
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)

    # Set sidereal mode (Fagan-Bradley)
    swe.set_sid_mode(_SIDEREAL_MODE)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Whole-sign house cusps — observational Mesopotamian approach
    # We compute ascendant via Placidus then snap to whole signs
    cusps_raw, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    asc_lon = ascmc[0]
    mc_lon = ascmc[1]

    # Whole-sign cusps: Asc sign starts at 0° of its sign
    asc_sign_idx = _sign_idx(asc_lon)
    cusps_ws: List[float] = [(asc_sign_idx + i) * 30.0 % 360 for i in range(12)]

    # Determine day/night (Sun above horizon = houses 7–12 in whole-sign)
    sun_sid = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    sun_house_ws = _find_house(sun_sid, cusps_ws)
    is_day = sun_house_ws in (7, 8, 9, 10, 11, 12)

    # Venus longitude for phase classification
    venus_sid = swe.calc_ut(jd, swe.VENUS, swe.FLG_SIDEREAL)[0][0]
    venus_phase = _classify_venus_phase(venus_sid, sun_sid)

    # Compute planetary positions
    planet_lons: Dict[str, float] = {}
    planets: List[MesopotamianPlanet] = []

    for planet_name, pid in _PLANET_IDS.items():
        res_ecl = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        res_equ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_EQUATORIAL)

        sid_lon = res_ecl[0][0]
        speed_lon = res_ecl[0][3]
        declination = res_equ[0][1]
        is_retro = speed_lon < 0

        idx = _sign_idx(sid_lon)
        sign_western = ZODIAC_SIGN_ORDER[idx]
        house = _find_house(sid_lon, cusps_ws)
        condition = _get_planet_condition(planet_name, idx)
        path = _classify_path(declination)
        sector = _k8538_sector(sid_lon)

        deity = MESOPOTAMIAN_DEITIES.get(planet_name, {})

        planets.append(MesopotamianPlanet(
            name=planet_name,
            akkadian=deity.get("akkadian", planet_name),
            sumerian=deity.get("sumerian", ""),
            role_cn=deity.get("role_cn", ""),
            role_en=deity.get("role_en", ""),
            longitude=round(sid_lon, 4),
            sign_idx=idx,
            sign_western=sign_western,
            sign_akkadian=AKKADIAN_NAME[sign_western],
            sign_cn=SIGN_CN[sign_western],
            sign_en=SIGN_EN[sign_western],
            degree_in_sign=round(_deg_in_sign(sid_lon), 2),
            house=house,
            is_retrograde=is_retro,
            condition=condition,
            declination=round(declination, 3),
            path=path,
            sector=sector,
            color=deity.get("color", "#C9A227"),
            glyph=deity.get("glyph", "★"),
        ))
        planet_lons[planet_name] = sid_lon

    # Gather omens
    omens: List[MesopotamianOmen] = []
    venus_p = next((p for p in planets if p.name == "Venus"), None)
    for p in planets:
        vphase = venus_phase if p.name == "Venus" else ""
        omens.extend(_find_omens(p.name, p.sign_idx, p.condition, vphase, p.is_retrograde))

    # Aspects
    aspects = _compute_aspects(planet_lons)

    # K.8538 sectors
    sectors = _build_sectors(planets)

    # MUL.APIN heliacal stars for this month
    heliacal_stars = _heliacal_stars_for_month(month)

    return MesopotamianChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone,
        latitude=lat,
        longitude_birth=lon,
        location_name=location_name,
        julian_day=round(jd, 5),
        ayanamsa=round(ayanamsa, 4),
        ascendant=round(asc_lon, 4),
        midheaven=round(mc_lon, 4),
        is_day_chart=is_day,
        house_cusps=cusps_ws,
        planets=planets,
        omens=omens,
        venus_phase=venus_phase,
        sectors=sectors,
        heliacal_stars=heliacal_stars,
        aspects=aspects,
    )
