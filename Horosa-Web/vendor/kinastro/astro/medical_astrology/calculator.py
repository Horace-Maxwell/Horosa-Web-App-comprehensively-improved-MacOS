"""
astro/medical_astrology/calculator.py — Medical Astrology Computation Engine

Implements classical Iatromathematics calculations:
1. Temperament (體質) analysis from birth chart
2. Health tendency report — vulnerable body parts
3. Critical day computation for acute illness
4. Electional timing engine for medical procedures
5. Egyptian Decan body-zone integration

Sources:
- Ptolemy "Tetrabiblos" Book I ch. 10–24
- Galen "On the Temperaments" (De Temperamentis)
- Avicenna "Canon of Medicine" Book I, Fen 3
- Culpeper "Astrological Judgement of Diseases" (1655)
- Lilly "Christian Astrology" (1647) pp. 252–260
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Tuple

import swisseph as swe
import streamlit as st

from .constants import (
    ZODIAC_BODY_PARTS,
    ZODIAC_SIGN_ORDER,
    FOUR_HUMORS,
    PLANET_MEDICAL,
    DECAN_BODY_PARTS,
    CRITICAL_DAYS,
    ELECTIONAL_RULES,
    PLANETARY_HOUR_ORDER,
    DAY_RULERS,
    ELEMENT_HUMOR_MAP,
    PLANET_TEMPERAMENT_CONTRIBUTION,
    TEMPERAMENT_DESCRIPTIONS,
    MOON_PHASE_MEDICAL,
)


# ============================================================
# Swiss Ephemeris planet IDs
# ============================================================

_PLANET_IDS: Dict[str, int] = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}

_CLASSICAL_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

# ============================================================
# Data Classes
# ============================================================


@dataclass
class PlanetPosition:
    """A planet's position in the birth chart."""

    name: str
    longitude: float        # ecliptic 0–360°
    sign: str               # e.g. "Aries"
    sign_index: int         # 0–11
    degree_in_sign: float   # 0–30°
    decan_index: int        # 0–35 (which of the 36 decans)
    decan_number: int       # 1, 2, or 3 within the sign
    house: int              # 1–12
    is_retrograde: bool
    element: str
    quality: str


@dataclass
class TemperamentScore:
    """Humoral balance derived from birth chart."""

    choleric: float = 0.0
    melancholic: float = 0.0
    sanguine: float = 0.0
    phlegmatic: float = 0.0

    @property
    def dominant(self) -> str:
        scores = {
            "Choleric": self.choleric,
            "Melancholic": self.melancholic,
            "Sanguine": self.sanguine,
            "Phlegmatic": self.phlegmatic,
        }
        return max(scores, key=scores.get)

    @property
    def secondary(self) -> str:
        scores = {
            "Choleric": self.choleric,
            "Melancholic": self.melancholic,
            "Sanguine": self.sanguine,
            "Phlegmatic": self.phlegmatic,
        }
        sorted_humors = sorted(scores, key=scores.get, reverse=True)
        return sorted_humors[1]

    def as_dict(self) -> Dict[str, float]:
        return {
            "Choleric": self.choleric,
            "Melancholic": self.melancholic,
            "Sanguine": self.sanguine,
            "Phlegmatic": self.phlegmatic,
        }

    def normalized(self) -> Dict[str, float]:
        total = self.choleric + self.melancholic + self.sanguine + self.phlegmatic
        if total == 0:
            return {"Choleric": 0.25, "Melancholic": 0.25, "Sanguine": 0.25, "Phlegmatic": 0.25}
        return {
            "Choleric": self.choleric / total,
            "Melancholic": self.melancholic / total,
            "Sanguine": self.sanguine / total,
            "Phlegmatic": self.phlegmatic / total,
        }


@dataclass
class BodyZoneHealth:
    """Health assessment for a body zone / sign area."""

    sign: str
    body_parts_en: List[str]
    body_parts_cn: List[str]
    affliction_score: float    # higher = more vulnerable
    strength_score: float      # higher = more protected
    net_score: float           # strength - affliction
    afflicting_planets: List[str]
    supporting_planets: List[str]
    diseases_en: List[str]
    diseases_cn: List[str]
    risk_level: str            # "high", "moderate", "low"


@dataclass
class CriticalDayInfo:
    """A computed critical day for acute illness onset."""

    onset_date: date
    crisis_date: date
    crisis_day_number: int
    crisis_type: str           # "critical" or "indicator"
    moon_longitude_at_onset: float
    moon_longitude_at_crisis: float
    significance_en: str
    significance_cn: str
    classical_ref: str


@dataclass
class ElectionalWindow:
    """A favorable window for a medical procedure."""

    procedure: str
    procedure_name_en: str
    procedure_name_cn: str
    start_dt: datetime
    end_dt: datetime
    moon_sign: str
    moon_phase: str
    planetary_hour: str
    score: float               # 0.0–10.0 quality score
    favorable_factors: List[str]
    warning_factors: List[str]


@dataclass
class MedicalChart:
    """Complete medical astrology analysis."""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str

    # Core chart data
    planets: List[PlanetPosition] = field(default_factory=list)
    ascendant_longitude: float = 0.0
    asc_sign: str = "Aries"
    mc_longitude: float = 0.0
    house_cusps: List[float] = field(default_factory=list)

    # Medical analysis
    temperament: TemperamentScore = field(default_factory=TemperamentScore)
    body_zones: List[BodyZoneHealth] = field(default_factory=list)
    critical_days: List[CriticalDayInfo] = field(default_factory=list)
    electional_windows: List[ElectionalWindow] = field(default_factory=list)

    # Decan analysis
    asc_decan_index: int = 0
    sun_decan_index: int = 0
    moon_decan_index: int = 0


# ============================================================
# Utility helpers
# ============================================================

def _normalize(deg: float) -> float:
    return deg % 360.0


def _sign_index(deg: float) -> int:
    return int(_normalize(deg) / 30.0)


def _sign_from_lon(deg: float) -> str:
    return ZODIAC_SIGN_ORDER[_sign_index(deg)]


def _degree_in_sign(deg: float) -> float:
    return _normalize(deg) % 30.0


def _decan_index(deg: float) -> int:
    """Return the decan index 0–35 for an ecliptic longitude."""
    lon = _normalize(deg)
    sign_idx = int(lon / 30.0)
    deg_in_sign = lon % 30.0
    decan_num = int(deg_in_sign / 10.0)  # 0, 1, or 2
    return sign_idx * 3 + decan_num


def _aspect_angle(lon_a: float, lon_b: float) -> float:
    """Shortest arc between two longitudes."""
    diff = abs(_normalize(lon_a) - _normalize(lon_b))
    if diff > 180:
        diff = 360 - diff
    return diff


def _is_aspect(lon_a: float, lon_b: float, aspect: float, orb: float = 8.0) -> bool:
    return abs(_aspect_angle(lon_a, lon_b) - aspect) <= orb


def _julian_day(year: int, month: int, day: int,
                hour: int, minute: int, timezone: float) -> float:
    """Convert local time to Julian Day (UT)."""
    ut_hour = hour + minute / 60.0 - timezone
    return swe.julday(year, month, day, ut_hour)


def _moon_phase_angle(jd: float) -> float:
    """Moon elongation from Sun (0°=new, 180°=full)."""
    sun_lon = swe.calc_ut(jd, swe.SUN)[0][0]
    moon_lon = swe.calc_ut(jd, swe.MOON)[0][0]
    return _normalize(moon_lon - sun_lon)


def _moon_phase_name(phase_angle: float) -> str:
    for key, info in MOON_PHASE_MEDICAL.items():
        lo, hi = info["range_deg"]
        if lo <= phase_angle < hi:
            return key
    return "waning_crescent"


# ============================================================
# Temperament Calculation
# Source: Ptolemy Tetrabiblos I.8–9; Galen "On the Temperaments"
# ============================================================

def _compute_temperament(planets: List[PlanetPosition],
                         asc_sign: str) -> TemperamentScore:
    """Calculate the four-humor temperament balance.

    Weighting (classical priority order, Ptolemy Tetrabiblos I.8):
    1. Ascendant sign: weight 3
    2. Sun sign: weight 2 (vital force)
    3. Moon sign: weight 2 (bodily moisture)
    4. Other classical planets in their sign: weight 1

    Also adds planetary nature contribution for classical 7 planets.
    """
    scores = TemperamentScore()

    def _add(humor: str, weight: float) -> None:
        if humor == "Choleric":
            scores.choleric += weight
        elif humor == "Melancholic":
            scores.melancholic += weight
        elif humor == "Sanguine":
            scores.sanguine += weight
        elif humor == "Phlegmatic":
            scores.phlegmatic += weight

    # Ascendant sign element
    asc_data = ZODIAC_BODY_PARTS.get(asc_sign, {})
    asc_element = asc_data.get("element", "Fire")
    _add(ELEMENT_HUMOR_MAP[asc_element], 3.0)

    for planet in planets:
        if planet.name not in _CLASSICAL_PLANETS:
            continue
        element = planet.element
        humor = ELEMENT_HUMOR_MAP.get(element, "Choleric")

        # Higher weight for luminaries
        if planet.name == "Sun":
            _add(humor, 2.0)
            # Also add Sun's inherent planetary temperament
            sun_humor = PLANET_TEMPERAMENT_CONTRIBUTION.get("Sun", "Choleric")
            _add(sun_humor, 1.0)
        elif planet.name == "Moon":
            _add(humor, 2.0)
            moon_humor = PLANET_TEMPERAMENT_CONTRIBUTION.get("Moon", "Phlegmatic")
            _add(moon_humor, 1.0)
        else:
            # Other classical planets
            _add(humor, 1.0)
            planet_humor = PLANET_TEMPERAMENT_CONTRIBUTION.get(planet.name, "")
            if planet_humor:
                _add(planet_humor, 0.5)

    return scores


# ============================================================
# Body Zone Health Analysis
# ============================================================

_BENEFICS = {"Venus", "Jupiter"}
_MALEFICS = {"Mars", "Saturn"}
_NEUTRAL = {"Sun", "Moon", "Mercury"}

# Aspect weights for medical analysis
_ASPECT_WEIGHTS = {
    0: 2.0,   # conjunction — intensifies (can be good or bad)
    60: 1.0,  # sextile — mild benefit/harm
    90: -2.0, # square — strong affliction
    120: 1.5, # trine — strong benefit
    180: -2.0, # opposition — strong affliction
    150: -0.5, # quincunx — mild adjustment needed
}


def _compute_body_zones(planets: List[PlanetPosition],
                        asc_sign: str) -> List[BodyZoneHealth]:
    """Analyse each zodiac sign's body zone for health vulnerabilities.

    Rules (Culpeper, Lilly):
    - Planets in a sign affect its body zone
    - Malefics (Mars, Saturn) in a sign = affliction
    - Benefics (Venus, Jupiter) in a sign = protection
    - Aspects from malefics to the sign's ruler = weakens
    - Planets ruling the 6th, 8th, or 12th house (traditional disease houses)
      add vulnerability
    """
    # Build planet longitude map for aspect calculation
    planet_lons: Dict[str, float] = {p.name: p.longitude for p in planets}
    planet_signs: Dict[str, str] = {p.name: p.sign for p in planets}

    zones: List[BodyZoneHealth] = []

    for sign in ZODIAC_SIGN_ORDER:
        sign_data = ZODIAC_BODY_PARTS[sign]
        sign_idx = ZODIAC_SIGN_ORDER.index(sign)
        sign_lon_start = sign_idx * 30.0

        affliction = 0.0
        strength = 0.0
        afflicting: List[str] = []
        supporting: List[str] = []

        for planet in planets:
            if planet.name not in _CLASSICAL_PLANETS:
                continue
            lon = planet.longitude

            # Planet IN the sign
            if planet.sign == sign:
                if planet.name in _MALEFICS:
                    affliction += 2.0
                    afflicting.append(planet.name)
                elif planet.name in _BENEFICS:
                    strength += 2.0
                    supporting.append(planet.name)
                else:
                    # Neutral — depends on context
                    pass

            # Aspects to the sign's midpoint
            sign_mid = sign_lon_start + 15.0
            angle = _aspect_angle(lon, sign_mid)

            for asp_deg, weight in _ASPECT_WEIGHTS.items():
                if abs(angle - asp_deg) <= 8.0:
                    if planet.name in _MALEFICS:
                        if weight < 0:
                            affliction += abs(weight)
                            if planet.name not in afflicting:
                                afflicting.append(planet.name)
                    elif planet.name in _BENEFICS:
                        if weight > 0:
                            strength += weight
                            if planet.name not in supporting:
                                supporting.append(planet.name)
                    break  # Only count strongest aspect

        net = strength - affliction
        if net < -2:
            risk = "high"
        elif net < 0:
            risk = "moderate"
        else:
            risk = "low"

        zones.append(BodyZoneHealth(
            sign=sign,
            body_parts_en=sign_data["body_parts_en"],
            body_parts_cn=sign_data["body_parts_cn"],
            affliction_score=round(affliction, 2),
            strength_score=round(strength, 2),
            net_score=round(net, 2),
            afflicting_planets=afflicting,
            supporting_planets=supporting,
            diseases_en=sign_data["diseases_en"],
            diseases_cn=sign_data["diseases_cn"],
            risk_level=risk,
        ))

    return zones


# ============================================================
# Critical Days Calculation
# ============================================================

def _compute_critical_days(onset: date,
                           jd_onset: float) -> List[CriticalDayInfo]:
    """Compute the classical critical days starting from illness onset.

    Uses the Moon's natal longitude at onset, then tracks Moon's progress
    through the 28-day lunation to find crisis/indicator days.
    """
    moon_at_onset = swe.calc_ut(jd_onset, swe.MOON)[0][0]
    result: List[CriticalDayInfo] = []

    for key, info in CRITICAL_DAYS.items():
        day_n = info["day"]
        crisis_date = onset + timedelta(days=day_n - 1)
        # Compute Julian day at crisis date noon
        jd_crisis = swe.julday(crisis_date.year, crisis_date.month, crisis_date.day, 12.0)
        moon_at_crisis = swe.calc_ut(jd_crisis, swe.MOON)[0][0]

        result.append(CriticalDayInfo(
            onset_date=onset,
            crisis_date=crisis_date,
            crisis_day_number=day_n,
            crisis_type=info["type"],
            moon_longitude_at_onset=round(moon_at_onset, 4),
            moon_longitude_at_crisis=round(moon_at_crisis, 4),
            significance_en=info["significance_en"],
            significance_cn=info["significance_cn"],
            classical_ref=info["classical_ref"],
        ))

    return result


# ============================================================
# Electional Timing Engine
# ============================================================

def _get_planetary_hour(dt: datetime, timezone: float) -> Tuple[str, int]:
    """Return (planet_name, hour_number) for the given datetime.

    Classical planetary hours:
    1. Find the day ruler from the weekday.
    2. Divide the day into 12 diurnal and 12 nocturnal hours.
    3. Count hours from sunrise using the Chaldean order.

    Simplified implementation: uses fixed 1-hour planetary hour blocks
    starting from sunrise (6:00 local time approximation).
    """
    weekday_name = dt.strftime("%A")
    day_ruler = DAY_RULERS.get(weekday_name, "Sun")

    # Index of day ruler in Chaldean order
    try:
        ruler_idx = PLANETARY_HOUR_ORDER.index(day_ruler)
    except ValueError:
        ruler_idx = 3  # Sun

    # Hours since midnight (approximate — assumes solar noon at 12:00)
    hour_of_day = dt.hour
    # Each planet rules approx 1 hour; 24 hours / 7 = cycle
    # Hour 1 (6am) starts with day ruler
    hours_since_6am = (hour_of_day - 6) % 24
    planet_hour_idx = (ruler_idx + hours_since_6am) % 7
    planet = PLANETARY_HOUR_ORDER[planet_hour_idx]
    return planet, (hours_since_6am % 7) + 1


def _score_electional_window(
    procedure: str,
    phase_angle: float,
    moon_phase: str,
    planetary_hour: str,
    moon_sign: str,
) -> Tuple[float, List[str], List[str]]:
    """Score a potential electional window for a medical procedure.

    Args:
        procedure: key from ELECTIONAL_RULES
        phase_angle: Moon-Sun elongation in degrees (0=new, 180=full)
        moon_phase: moon phase key string
        planetary_hour: name of the ruling planet for this hour
        moon_sign: zodiac sign the Moon is in

    Returns (score 0–10, favorable_factors, warning_factors).
    """
    rules = ELECTIONAL_RULES.get(procedure, {})
    if not rules:
        return 5.0, [], []

    score = 5.0
    favorable: List[str] = []
    warnings: List[str] = []

    # phase_angle is already the Moon-Sun elongation (0–360°)

    # Bloodletting: favored during waxing (Moon building up blood)
    if procedure == "bloodletting":
        if 45 <= phase_angle < 180:
            score += 2.0
            favorable.append("Moon waxing — blood rises")
        elif phase_angle >= 315 or phase_angle < 45:
            score -= 2.0
            warnings.append("New Moon — diminished vitality for bloodletting")
        if planetary_hour in ("Moon", "Mars"):
            score += 1.0
            favorable.append(f"Favorable planetary hour: {planetary_hour}")

    elif procedure == "surgery":
        # Waning Moon preferred
        if 180 <= phase_angle < 315:
            score += 2.5
            favorable.append("Moon waning — reduced bleeding risk")
        elif 135 <= phase_angle < 180:
            score -= 1.5
            warnings.append("Near Full Moon — high bleeding risk")
        elif phase_angle >= 315:
            score -= 1.0
            warnings.append("Near New Moon — diminished vitality")
        if moon_sign in ("Cancer", "Scorpio", "Pisces", "Aries", "Leo"):
            warnings.append(f"Caution: Moon in {moon_sign} — avoid surgery on ruled body parts")
            score -= 1.0
        if planetary_hour in ("Mars", "Sun"):
            score += 1.0
            favorable.append(f"Favorable planetary hour: {planetary_hour} (surgical vigor)")

    elif procedure == "medicine_taking":
        # Mutable signs favour movement
        if moon_sign in ("Gemini", "Virgo", "Sagittarius", "Pisces"):
            score += 1.5
            favorable.append(f"Moon in mutable sign {moon_sign} — promotes movement of medicine")
        if planetary_hour in ("Jupiter", "Moon"):
            score += 1.0
            favorable.append(f"Favorable planetary hour: {planetary_hour}")
        # Waning for purging, waxing for tonics
        if 180 <= phase_angle < 360:
            favorable.append("Moon waning — good for purging/eliminating medicines")
        else:
            favorable.append("Moon waxing — good for tonic/building medicines")

    elif procedure == "cauterization":
        if moon_sign in ("Aries", "Leo", "Sagittarius", "Taurus", "Virgo", "Capricorn"):
            score += 1.5
            favorable.append(f"Moon in dry sign {moon_sign} — favorable for cautery")
        if moon_sign in ("Cancer", "Scorpio", "Pisces"):
            score -= 2.0
            warnings.append(f"Moon in water sign {moon_sign} — resists cauterization")
        if planetary_hour == "Mars":
            score += 1.5
            favorable.append("Mars hour — cauterizing fire principle active")

    elif procedure == "bathing":
        if moon_sign in ("Cancer", "Scorpio", "Pisces"):
            score += 2.0
            favorable.append(f"Moon in water sign {moon_sign} — excellent for bathing")
        if planetary_hour == "Venus":
            score += 1.0
            favorable.append("Venus hour — relaxation and skin benefit")

    elif procedure == "fasting":
        if 180 <= phase_angle < 360:
            score += 2.0
            favorable.append("Moon waning — diminishing principle supports fasting")
        if moon_sign in ("Virgo", "Capricorn"):
            score += 1.5
            favorable.append(f"Moon in {moon_sign} — digestive control and discipline")
        if planetary_hour in ("Moon", "Saturn"):
            score += 0.5
            favorable.append(f"{planetary_hour} hour — supports fasting intention")

    elif procedure == "herbal_remedy":
        if moon_sign in ("Virgo", "Taurus"):
            score += 1.5
            favorable.append(f"Moon in {moon_sign} — stable medicinal virtue")
        if 45 <= phase_angle < 180:
            score += 1.0
            favorable.append("Moon waxing — herb potency at maximum")

    # Full Moon warning for surgery/bloodletting — covers full_moon phase range 170–225°
    if moon_phase == "full_moon" and procedure in ("surgery", "bloodletting"):
        score -= 3.0
        warnings.append("⚠️ Near Full Moon — high risk of excess bleeding")

    # New Moon general caution
    if phase_angle < 15 or phase_angle > 345:
        score -= 1.0
        warnings.append("Near New Moon — diminished vital force")

    return round(max(0.0, min(10.0, score)), 1), favorable, warnings


def compute_electional_windows(
    procedure: str,
    search_from: datetime,
    search_days: int = 14,
    timezone: float = 8.0,
) -> List[ElectionalWindow]:
    """Search for favorable electional windows for a medical procedure.

    Scans each 2-hour block over search_days to find windows scoring ≥ 6.0.
    Returns up to 8 best windows sorted by score.

    Args:
        procedure: key from ELECTIONAL_RULES
        search_from: start of search window
        search_days: how many days to scan (max 30 for performance)
        timezone: UTC offset for planetary hour computation

    Returns:
        List of ElectionalWindow sorted by score descending.
    """
    search_days = min(search_days, 30)
    windows: List[ElectionalWindow] = []

    current = search_from.replace(minute=0, second=0, microsecond=0)
    end_search = search_from + timedelta(days=search_days)

    while current < end_search:
        jd = _julian_day(current.year, current.month, current.day,
                         current.hour, current.minute, timezone)
        moon_calc = swe.calc_ut(jd, swe.MOON)
        moon_lon = moon_calc[0][0]
        moon_sign = _sign_from_lon(moon_lon)
        phase_angle = _moon_phase_angle(jd)
        moon_phase = _moon_phase_name(phase_angle)
        planet_hour, _ = _get_planetary_hour(current, timezone)

        score, favorable, warnings = _score_electional_window(
            procedure, phase_angle, moon_phase, planet_hour, moon_sign
        )

        if score >= 6.0:
            proc_data = ELECTIONAL_RULES.get(procedure, {})
            windows.append(ElectionalWindow(
                procedure=procedure,
                procedure_name_en=proc_data.get("name_en", procedure),
                procedure_name_cn=proc_data.get("name_cn", procedure),
                start_dt=current,
                end_dt=current + timedelta(hours=2),
                moon_sign=moon_sign,
                moon_phase=moon_phase,
                planetary_hour=planet_hour,
                score=score,
                favorable_factors=favorable,
                warning_factors=warnings,
            ))

        current += timedelta(hours=2)  # scan in 2-hour blocks

    # Sort by score descending, return top 8
    windows.sort(key=lambda w: w.score, reverse=True)
    return windows[:8]


# ============================================================
# Main Computation Entry Point
# ============================================================


@st.cache_data(ttl=3600, show_spinner=False)
def compute_medical_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    onset_date_str: Optional[str] = None,
    **kwargs: Any,
) -> MedicalChart:
    """Compute the full medical astrology chart.

    Args:
        year, month, day, hour, minute: birth date/time (local)
        timezone: UTC offset (e.g. +8 for CST)
        latitude, longitude: birth location
        location_name: display name for location
        onset_date_str: ISO date string for acute illness onset (optional)
        **kwargs: ignored extra params (for compatibility with _calc_params)

    Returns:
        MedicalChart with temperament, body zones, and optional critical days.
    """
    jd = _julian_day(year, month, day, hour, minute, timezone)

    # ── House calculation ──
    cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')  # Placidus
    asc_lon = ascmc[0]
    mc_lon = ascmc[1]
    asc_sign = _sign_from_lon(asc_lon)

    # ── Planet positions ──
    planets: List[PlanetPosition] = []
    for pname, pid in _PLANET_IDS.items():
        calc_result = swe.calc_ut(jd, pid)
        lon = calc_result[0][0]
        speed = calc_result[0][3]
        is_retro = speed < 0 and pname not in ("Sun", "Moon")

        sign_idx = _sign_index(lon)
        sign = ZODIAC_SIGN_ORDER[sign_idx]
        deg_in_sign = _degree_in_sign(lon)
        sign_data = ZODIAC_BODY_PARTS[sign]
        element = sign_data["element"]
        quality = sign_data["quality"]

        dec_idx = _decan_index(lon)
        dec_num = int(deg_in_sign / 10.0) + 1  # 1, 2, 3

        # House placement
        p_house = 1
        for h in range(12):
            cusp_start = cusps[h]
            cusp_end = cusps[(h + 1) % 12]
            # Wrap-around check
            if cusp_start <= cusp_end:
                if cusp_start <= lon < cusp_end:
                    p_house = h + 1
                    break
            else:
                if lon >= cusp_start or lon < cusp_end:
                    p_house = h + 1
                    break

        planets.append(PlanetPosition(
            name=pname,
            longitude=round(lon, 4),
            sign=sign,
            sign_index=sign_idx,
            degree_in_sign=round(deg_in_sign, 4),
            decan_index=dec_idx,
            decan_number=dec_num,
            house=p_house,
            is_retrograde=is_retro,
            element=element,
            quality=quality,
        ))

    # ── Temperament ──
    temperament = _compute_temperament(planets, asc_sign)

    # ── Body zone health ──
    body_zones = _compute_body_zones(planets, asc_sign)

    # ── Critical days (if onset provided) ──
    critical_days: List[CriticalDayInfo] = []
    if onset_date_str:
        try:
            onset = date.fromisoformat(onset_date_str)
            jd_onset = swe.julday(onset.year, onset.month, onset.day, 12.0)
            critical_days = _compute_critical_days(onset, jd_onset)
        except (ValueError, Exception):
            pass

    # ── Find decan indices for ASC, Sun, Moon ──
    asc_decan = _decan_index(asc_lon)
    sun_planet = next((p for p in planets if p.name == "Sun"), None)
    moon_planet = next((p for p in planets if p.name == "Moon"), None)
    sun_decan = sun_planet.decan_index if sun_planet else 0
    moon_decan = moon_planet.decan_index if moon_planet else 0

    return MedicalChart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        planets=planets,
        ascendant_longitude=round(asc_lon, 4),
        asc_sign=asc_sign,
        mc_longitude=round(mc_lon, 4),
        house_cusps=list(cusps),
        temperament=temperament,
        body_zones=body_zones,
        critical_days=critical_days,
        asc_decan_index=asc_decan,
        sun_decan_index=sun_decan,
        moon_decan_index=moon_decan,
    )
