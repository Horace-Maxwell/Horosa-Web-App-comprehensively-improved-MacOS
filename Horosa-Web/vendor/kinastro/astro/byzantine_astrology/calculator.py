"""
astro/byzantine_astrology/calculator.py — Byzantine Astrology Computation Engine

Implements Byzantine astrological calculations:
1. Byzantine natal chart with classical Hellenistic techniques
2. Political / mundane chart analysis (city founding, imperial horoscopes)
3. Omen-based predictions (Seismologia, Selenodromia, Vrontologia)
4. Byzantine lots (Κλῆροι) computation
5. Firdaria (planetary time periods) — Arabo-Byzantine technique
6. Annual profections with Byzantine house significations

Primary Sources:
- Paulus Alexandrinus, "Eisagogika" (378 CE)
- Rhetorius of Egypt, "Compendium" (ca. 6th c.)
- Hephaestion of Thebes, "Apotelesmatika" (ca. 415 CE)
- Theophilus of Edessa, "Apotelesmatics" (ca. 785 CE)
- Catalogus Codicum Astrologorum Graecorum (CCAG)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple

import swisseph as swe

from .constants import (
    BYZANTINE_SIGN_NAMES,
    ZODIAC_SIGN_ORDER,
    BYZANTINE_PLANET_NAMES,
    CLASSICAL_PLANET_ORDER,
    BYZANTINE_LOTS,
    BYZANTINE_ASPECTS,
    BYZANTINE_HOUSES,
    BYZANTINE_TRIPLICITY_LORDS,
    SEISMOLOGIA,
    SELENODROMIA,
    VRONTOLOGIA,
    CHRISTIAN_SYNCRETISM,
    THEOPHILUS_MILITARY_RULES,
    ARABO_BYZANTINE_TECHNIQUES,
    POLITICAL_HOROSCOPES,
    BYZANTINE_ASTROLOGERS,
)


# ============================================================
# Swiss Ephemeris Planet IDs
# ============================================================

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
class ByzantinePlanetPos:
    """A planet's position in Byzantine astrological terms."""
    name: str
    longitude: float        # ecliptic 0–360°
    sign: str               # e.g. "Aries"
    sign_gr: str            # Greek name e.g. "Κριός"
    sign_cn: str            # Chinese name
    sign_index: int         # 0–11
    degree_in_sign: float   # 0–30°
    house: int              # 1–12 (whole-sign)
    is_retrograde: bool
    element: str            # Fire/Earth/Air/Water
    quality: str            # Cardinal/Fixed/Mutable
    dignity: str            # Domicile/Exaltation/Detriment/Fall/Peregrine
    glyph: str              # ☉ ☽ ☿ etc.


@dataclass
class ByzantineLot:
    """A Byzantine Lot (Κλῆρος) position."""
    name_en: str
    name_cn: str
    name_gr: str
    longitude: float
    sign: str
    sign_gr: str
    sign_cn: str
    house: int
    degree_in_sign: float
    formula_used: str


@dataclass
class ByzantineAspect:
    """An aspect between two planets in Byzantine tradition."""
    planet1: str
    planet2: str
    aspect_name: str
    aspect_name_cn: str
    orb: float
    exact_degrees: int
    is_applying: bool
    quality_en: str
    quality_cn: str
    glyph: str
    color: str


@dataclass
class Profection:
    """Annual profection result for Byzantine predictive astrology."""
    age: int
    year_number: int        # year of life (age + 1)
    house_activated: int    # 1–12
    sign_activated: str
    sign_gr: str
    lord_of_year: str       # planet ruling activated sign
    house_significations_en: List[str]
    house_significations_cn: List[str]
    house_name_en: str
    house_name_cn: str


@dataclass
class FirdarPeriod:
    """A single Firdar (planetary period) in Byzantine-Arabic tradition."""
    main_planet: str
    main_planet_glyph: str
    sub_planet: str
    sub_planet_glyph: str
    start_year_age: float
    end_year_age: float
    duration_years: float
    quality_en: str
    quality_cn: str


@dataclass
class OmenAnalysis:
    """Result of an omen interpretation (Seismologia/Selenodromia/Vrontologia)."""
    omen_type: str          # "seismologia" | "selenodromia" | "vrontologia"
    trigger_planet: str     # planet causing the omen
    trigger_sign: str       # sign the trigger is in
    severity: str           # "severe" | "moderate" | "mild"
    omen_en: str
    omen_cn: str
    region_en: str
    region_cn: str
    source_ref: str


@dataclass
class ByzantineChart:
    """Complete Byzantine astrological chart result."""
    # Birth data
    year: int
    month: int
    day: int
    hour: float
    latitude: float
    longitude: float
    location_name: str

    # Chart data
    julian_day: float
    ascendant: float
    midheaven: float
    ascendant_sign: str
    ascendant_sign_gr: str
    is_day_chart: bool

    # Planets
    planets: List[ByzantinePlanetPos]

    # Lots
    lots: List[ByzantineLot]

    # Aspects
    aspects: List[ByzantineAspect]

    # Profection
    profection: Optional[Profection]

    # Firdaria
    firdaria: List[FirdarPeriod]

    # Omens
    omens: List[OmenAnalysis]

    # Mode
    chart_mode: str         # "natal" | "political" | "mundane" | "omen"

    # Historical example data (if loading a preset chart)
    historical_name: Optional[str] = None
    historical_desc_en: Optional[str] = None
    historical_desc_cn: Optional[str] = None


# ============================================================
# Helper Functions
# ============================================================

def _julian_day(year: int, month: int, day: int, hour: float) -> float:
    """Convert date/time to Julian Day number."""
    return swe.julday(year, month, day, hour)


def _sign_from_lon(lon: float) -> Tuple[str, int, float]:
    """Return (sign_name, sign_index 0-11, degree_in_sign) for ecliptic longitude."""
    sign_index = int(lon // 30) % 12
    degree_in_sign = lon % 30
    sign_name = ZODIAC_SIGN_ORDER[sign_index]
    return sign_name, sign_index, degree_in_sign


def _element_of_sign(sign: str) -> str:
    """Return the element of a zodiac sign."""
    fire = {"Aries", "Leo", "Sagittarius"}
    earth = {"Taurus", "Virgo", "Capricorn"}
    air = {"Gemini", "Libra", "Aquarius"}
    water = {"Cancer", "Scorpio", "Pisces"}
    if sign in fire:
        return "Fire"
    if sign in earth:
        return "Earth"
    if sign in air:
        return "Air"
    return "Water"


def _quality_of_sign(sign: str) -> str:
    """Return the quality (modality) of a zodiac sign."""
    cardinal = {"Aries", "Cancer", "Libra", "Capricorn"}
    fixed = {"Taurus", "Leo", "Scorpio", "Aquarius"}
    if sign in cardinal:
        return "Cardinal"
    if sign in fixed:
        return "Fixed"
    return "Mutable"


# Classical planetary domiciles
_DOMICILES: Dict[str, List[str]] = {
    "Sun":     ["Leo"],
    "Moon":    ["Cancer"],
    "Mercury": ["Gemini", "Virgo"],
    "Venus":   ["Taurus", "Libra"],
    "Mars":    ["Aries", "Scorpio"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Saturn":  ["Capricorn", "Aquarius"],
}

# Classical planetary exaltations
_EXALTATIONS: Dict[str, str] = {
    "Sun":     "Aries",
    "Moon":    "Taurus",
    "Mercury": "Virgo",
    "Venus":   "Pisces",
    "Mars":    "Capricorn",
    "Jupiter": "Cancer",
    "Saturn":  "Libra",
}

# Classical planetary detriments (opposite of domicile)
_DETRIMENTS: Dict[str, List[str]] = {
    "Sun":     ["Aquarius"],
    "Moon":    ["Capricorn"],
    "Mercury": ["Sagittarius", "Pisces"],
    "Venus":   ["Aries", "Scorpio"],
    "Mars":    ["Libra", "Taurus"],
    "Jupiter": ["Gemini", "Virgo"],
    "Saturn":  ["Cancer", "Leo"],
}

# Classical planetary falls (opposite of exaltation)
_FALLS: Dict[str, str] = {
    "Sun":     "Libra",
    "Moon":    "Scorpio",
    "Mercury": "Pisces",
    "Venus":   "Virgo",
    "Mars":    "Cancer",
    "Jupiter": "Capricorn",
    "Saturn":  "Aries",
}


def _dignity_of_planet(planet: str, sign: str) -> str:
    """Determine the essential dignity of a planet in a sign."""
    if sign in _DOMICILES.get(planet, []):
        return "Domicile"
    if _EXALTATIONS.get(planet) == sign:
        return "Exaltation"
    if sign in _DETRIMENTS.get(planet, []):
        return "Detriment"
    if _FALLS.get(planet) == sign:
        return "Fall"
    return "Peregrine"


def _whole_sign_house(planet_sign_index: int, asc_sign_index: int) -> int:
    """Compute whole-sign house number (1–12) used in Byzantine tradition."""
    return ((planet_sign_index - asc_sign_index) % 12) + 1


def _angle_diff(lon1: float, lon2: float) -> float:
    """Shortest angular difference between two ecliptic longitudes, 0–180."""
    diff = abs(lon1 - lon2) % 360
    if diff > 180:
        diff = 360 - diff
    return diff


# ============================================================
# Lot Calculation
# ============================================================

def _compute_lot(formula: str, asc: float, sun_lon: float, moon_lon: float,
                 venus_lon: float, mercury_lon: float, mars_lon: float,
                 jupiter_lon: float, saturn_lon: float, is_day: bool,
                 fortune_lon: Optional[float] = None,
                 spirit_lon: Optional[float] = None) -> float:
    """
    Compute a Byzantine lot longitude from its formula string.

    Args:
        formula: e.g. "ASC + Moon − Sun" (day formula)
        asc: ascendant longitude
        sun_lon: Sun longitude
        moon_lon: Moon longitude
        ... other planet longitudes
        is_day: True if day chart
        fortune_lon: precomputed Fortune longitude (for dependent lots)
        spirit_lon: precomputed Spirit longitude

    Returns:
        Lot longitude 0–360
    """
    # Parse simple formulas of the form "ASC + X − Y"
    var_map = {
        "ASC": asc,
        "Moon": moon_lon,
        "Sun": sun_lon,
        "Venus": venus_lon,
        "Mercury": mercury_lon,
        "Mars": mars_lon,
        "Jupiter": jupiter_lon,
        "Saturn": saturn_lon,
        "Fortune": fortune_lon or 0.0,
        "Spirit": spirit_lon or 0.0,
    }

    # Remove the day/night prefix if present
    f = formula.replace("ASC + ", "").strip()

    # Simple: "ASC + Moon − Sun" → parse tokens
    tokens = formula.replace("−", "-").replace("–", "-").split()
    # tokens like: ["ASC", "+", "Moon", "−", "Sun"]
    result = 0.0
    sign = 1
    for tok in tokens:
        if tok in ("+",):
            sign = 1
        elif tok in ("-", "−", "–"):
            sign = -1
        elif tok in var_map:
            result += sign * var_map[tok]
        # else: ignore unknown tokens

    return result % 360


def _compute_all_lots(asc: float, planet_lons: Dict[str, float],
                      is_day: bool) -> List[ByzantineLot]:
    """
    Compute all Byzantine lots.

    Args:
        asc: ascendant longitude
        planet_lons: dict of planet name -> longitude
        is_day: True if day chart

    Returns:
        List of ByzantineLot objects
    """
    sun = planet_lons.get("Sun", 0.0)
    moon = planet_lons.get("Moon", 0.0)
    venus = planet_lons.get("Venus", 0.0)
    mercury = planet_lons.get("Mercury", 0.0)
    mars = planet_lons.get("Mars", 0.0)
    jupiter = planet_lons.get("Jupiter", 0.0)
    saturn = planet_lons.get("Saturn", 0.0)

    results: List[ByzantineLot] = []

    fortune_lon: Optional[float] = None
    spirit_lon: Optional[float] = None

    for lot_key, lot_data in BYZANTINE_LOTS.items():
        formula = lot_data["day_formula"] if is_day else lot_data["night_formula"]

        lon = _compute_lot(
            formula, asc, sun, moon, venus, mercury, mars, jupiter, saturn,
            is_day, fortune_lon, spirit_lon
        )

        sign, sign_idx, deg_in_sign = _sign_from_lon(lon)
        sign_info = BYZANTINE_SIGN_NAMES[sign]
        asc_sign, asc_idx, _ = _sign_from_lon(asc)
        house = _whole_sign_house(sign_idx, asc_idx)

        lot = ByzantineLot(
            name_en=lot_data["name_en"],
            name_cn=lot_data["name_cn"],
            name_gr=lot_data["name_gr"],
            longitude=lon,
            sign=sign,
            sign_gr=sign_info["greek"],
            sign_cn=sign_info["cn"],
            house=house,
            degree_in_sign=deg_in_sign,
            formula_used=formula,
        )
        results.append(lot)

        if lot_key == "fortune":
            fortune_lon = lon
        elif lot_key == "spirit":
            spirit_lon = lon

    return results


# ============================================================
# Aspect Calculation
# ============================================================

def _compute_aspects(planet_lons: Dict[str, float]) -> List[ByzantineAspect]:
    """
    Compute Byzantine aspects between all classical planets.

    Args:
        planet_lons: dict of planet name -> longitude

    Returns:
        List of ByzantineAspect objects
    """
    planets = [p for p in CLASSICAL_PLANET_ORDER if p in planet_lons]
    aspects: List[ByzantineAspect] = []

    for i, p1 in enumerate(planets):
        for j, p2 in enumerate(planets):
            if j <= i:
                continue
            lon1 = planet_lons[p1]
            lon2 = planet_lons[p2]
            diff = _angle_diff(lon1, lon2)

            for asp_key, asp_data in BYZANTINE_ASPECTS.items():
                target = asp_data["degrees"]
                orb = asp_data["orb"]
                actual_orb = abs(diff - target)
                if actual_orb <= orb:
                    # Determine if applying
                    # A planet is applying if it's moving toward the aspect
                    # Simplified: use longitudinal order
                    is_applying = (lon2 - lon1) % 360 < 180

                    aspects.append(ByzantineAspect(
                        planet1=p1,
                        planet2=p2,
                        aspect_name=asp_data["name_en"],
                        aspect_name_cn=asp_data["name_cn"],
                        orb=round(actual_orb, 2),
                        exact_degrees=target,
                        is_applying=is_applying,
                        quality_en=asp_data["quality_en"],
                        quality_cn=asp_data["quality_cn"],
                        glyph=asp_data["glyph"],
                        color=asp_data["color"],
                    ))

    return aspects


# ============================================================
# Profection Calculation
# ============================================================

def _compute_profection(asc_lon: float, birth_year: int,
                        current_year: int) -> Optional[Profection]:
    """
    Compute annual profection for Byzantine predictive astrology.

    Each year, the profected ASC moves one sign forward (30°) from the natal ASC.
    The house activated is determined by how many years have passed.

    Args:
        asc_lon: natal ascendant longitude
        birth_year: year of birth
        current_year: year for which to compute profection

    Returns:
        Profection object or None if years invalid
    """
    if current_year < birth_year:
        return None

    age = current_year - birth_year
    asc_sign, asc_idx, _ = _sign_from_lon(asc_lon)

    # House activated: cycles through 1–12 each year
    house_activated = (age % 12) + 1
    activated_sign_idx = (asc_idx + age) % 12
    activated_sign = ZODIAC_SIGN_ORDER[activated_sign_idx]
    activated_sign_gr = BYZANTINE_SIGN_NAMES[activated_sign]["greek"]

    # Lord of year = ruler of activated sign
    lord_of_year = "Sun"  # default
    for planet, domiciles in _DOMICILES.items():
        if activated_sign in domiciles:
            lord_of_year = planet
            break

    house_data = BYZANTINE_HOUSES.get(house_activated, {})

    return Profection(
        age=age,
        year_number=age + 1,
        house_activated=house_activated,
        sign_activated=activated_sign,
        sign_gr=activated_sign_gr,
        lord_of_year=lord_of_year,
        house_significations_en=house_data.get("signifies_en", []),
        house_significations_cn=house_data.get("signifies_cn", []),
        house_name_en=house_data.get("name_en", ""),
        house_name_cn=house_data.get("name_cn", ""),
    )


# ============================================================
# Firdaria Calculation
# ============================================================

# Day chart firdaria order (years each planet rules)
_FIRDARIA_DAY: List[Tuple[str, float]] = [
    ("Sun", 10.0),
    ("Venus", 8.0),
    ("Mercury", 13.0),
    ("Moon", 9.0),
    ("Saturn", 11.0),
    ("Jupiter", 12.0),
    ("Mars", 7.0),
    ("North Node", 3.0),
    ("South Node", 2.0),
]

# Night chart firdaria order
_FIRDARIA_NIGHT: List[Tuple[str, float]] = [
    ("Moon", 9.0),
    ("Saturn", 11.0),
    ("Jupiter", 12.0),
    ("Mars", 7.0),
    ("Sun", 10.0),
    ("Venus", 8.0),
    ("Mercury", 13.0),
    ("North Node", 3.0),
    ("South Node", 2.0),
]

_FIRDARIA_SUB_ORDER: List[str] = [
    "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"
]

_PLANET_QUALITY: Dict[str, Tuple[str, str]] = {
    "Sun":     ("Royal authority, vitality, father", "王權、生命力、父親"),
    "Moon":    ("Emotions, public life, mother", "情感、公眾生活、母親"),
    "Mercury": ("Intellect, commerce, writing", "智識、商業、書寫"),
    "Venus":   ("Love, arts, pleasure, women", "愛情、藝術、快樂、女性"),
    "Mars":    ("War, conflict, courage, surgery", "戰爭、衝突、勇氣、外科"),
    "Jupiter": ("Prosperity, religion, justice, honor", "繁榮、宗教、正義、榮譽"),
    "Saturn":  ("Delay, restriction, discipline, old age", "延遲、限制、紀律、老年"),
    "North Node": ("Increase, fortune, expansion", "增長、財富、擴展"),
    "South Node": ("Release, karma, decrease", "釋放、業力、減少"),
}


def _compute_firdaria(is_day: bool, age: int = 30) -> List[FirdarPeriod]:
    """
    Compute Firdaria periods up to given age.

    Args:
        is_day: True for day chart
        age: compute periods up to this age

    Returns:
        List of FirdarPeriod objects
    """
    order = _FIRDARIA_DAY if is_day else _FIRDARIA_NIGHT
    periods: List[FirdarPeriod] = []
    current_age = 0.0

    while current_age < age:
        for main_planet, main_years in order:
            if current_age >= age:
                break
            sub_duration = main_years / 7.0
            # Sub-periods: cycle through 7 classical planets starting from main
            main_idx = _FIRDARIA_SUB_ORDER.index(main_planet) if main_planet in _FIRDARIA_SUB_ORDER else 0
            for i in range(7):
                if current_age >= age:
                    break
                sub_planet = _FIRDARIA_SUB_ORDER[(main_idx + i) % 7]
                end_age = current_age + sub_duration

                main_q = _PLANET_QUALITY.get(main_planet, ("", ""))
                sub_q = _PLANET_QUALITY.get(sub_planet, ("", ""))

                periods.append(FirdarPeriod(
                    main_planet=main_planet,
                    main_planet_glyph=BYZANTINE_PLANET_NAMES.get(main_planet, {}).get("glyph", ""),
                    sub_planet=sub_planet,
                    sub_planet_glyph=BYZANTINE_PLANET_NAMES.get(sub_planet, {}).get("glyph", ""),
                    start_year_age=round(current_age, 2),
                    end_year_age=round(end_age, 2),
                    duration_years=round(sub_duration, 2),
                    quality_en=f"{main_q[0]} / {sub_q[0]}",
                    quality_cn=f"{main_q[1]} / {sub_q[1]}",
                ))
                current_age = end_age

    return [p for p in periods if p.start_year_age < age]


# ============================================================
# Omen Analysis
# ============================================================

def _analyze_seismologia(planet_lons: Dict[str, float]) -> List[OmenAnalysis]:
    """
    Analyze earthquake omens from planetary positions.

    Checks Sun, Saturn, Mars in various signs per Seismologia doctrine.

    Args:
        planet_lons: dict of planet name -> longitude

    Returns:
        List of OmenAnalysis objects
    """
    omens: List[OmenAnalysis] = []
    for planet_key, seismo_data in SEISMOLOGIA.items():
        if planet_key not in planet_lons:
            continue
        lon = planet_lons[planet_key]
        sign, _, _ = _sign_from_lon(lon)

        sign_effects = seismo_data.get("sign_effects", {})
        if sign in sign_effects:
            effect = sign_effects[sign]
            omens.append(OmenAnalysis(
                omen_type="seismologia",
                trigger_planet=planet_key,
                trigger_sign=sign,
                severity=effect["severity"],
                omen_en=effect["omen_en"],
                omen_cn=effect["omen_cn"],
                region_en=effect.get("region_en", ""),
                region_cn=effect.get("region_cn", ""),
                source_ref=seismo_data.get("source_ref", ""),
            ))
    return omens


def _analyze_selenodromia(moon_lon: float, sun_lon: float) -> List[OmenAnalysis]:
    """
    Analyze moon phase omens (Selenodromia).

    Args:
        moon_lon: Moon longitude
        sun_lon: Sun longitude

    Returns:
        List of OmenAnalysis objects
    """
    omens: List[OmenAnalysis] = []

    # Compute moon phase angle
    phase_angle = (moon_lon - sun_lon) % 360
    moon_sign, _, _ = _sign_from_lon(moon_lon)

    # Determine phase
    if phase_angle < 45 or phase_angle >= 315:
        phase_key = "new_moon"
        phase_data = SELENODROMIA["new_moon"]
    elif 45 <= phase_angle < 135:
        phase_key = "first_quarter"
        phase_data = SELENODROMIA["first_quarter"]
    elif 135 <= phase_angle < 225:
        phase_key = "full_moon"
        phase_data = SELENODROMIA["full_moon"]
    else:
        phase_key = "last_quarter"
        phase_data = SELENODROMIA["last_quarter"]

    sign_omens = phase_data.get("sign_omens", {})
    if moon_sign in sign_omens:
        effect = sign_omens[moon_sign]
        # Combine weather + political + other omens
        omen_parts_en = []
        omen_parts_cn = []
        for field_key in ("weather_en", "political_en", "medical_en", "agriculture_en"):
            if field_key in effect:
                omen_parts_en.append(effect[field_key])
        for field_key in ("weather_cn", "political_cn", "medical_cn", "agriculture_cn"):
            if field_key in effect:
                omen_parts_cn.append(effect[field_key])

        omens.append(OmenAnalysis(
            omen_type="selenodromia",
            trigger_planet="Moon",
            trigger_sign=moon_sign,
            severity="moderate",
            omen_en=f"[{phase_data['phase_en']} in {moon_sign}] " + " | ".join(omen_parts_en),
            omen_cn=f"[{phase_data['phase_cn']}於{BYZANTINE_SIGN_NAMES[moon_sign]['cn']}] " + " | ".join(omen_parts_cn),
            region_en="General (Empire-wide)",
            region_cn="全境（整個帝國）",
            source_ref=phase_data.get("source_ref", ""),
        ))
    else:
        # General phase omen
        general_en = phase_data.get("general_omen_en", "")
        general_cn = phase_data.get("general_omen_cn", "")
        if general_en:
            omens.append(OmenAnalysis(
                omen_type="selenodromia",
                trigger_planet="Moon",
                trigger_sign=moon_sign,
                severity="mild",
                omen_en=f"[{phase_data['phase_en']} in {moon_sign}] {general_en}",
                omen_cn=f"[{phase_data['phase_cn']}於{BYZANTINE_SIGN_NAMES[moon_sign]['cn']}] {general_cn}",
                region_en="General",
                region_cn="全境",
                source_ref=phase_data.get("source_ref", ""),
            ))

    return omens


def _analyze_vrontologia(month: int) -> List[OmenAnalysis]:
    """
    Generate Vrontologia (thunder omen) interpretations for the current month.

    Args:
        month: calendar month (1–12)

    Returns:
        List of OmenAnalysis objects for all four compass directions
    """
    month_names = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    if month < 1 or month > 12:
        return []

    month_name = month_names[month]
    month_data = VRONTOLOGIA.get(month_name, {})
    if not month_data:
        return []

    omens: List[OmenAnalysis] = []
    directions = ["east", "west", "north", "south"]

    for direction in directions:
        key = f"thunder_from_{direction}"
        if key not in month_data:
            continue
        effect = month_data[key]
        direction_cn = {"east": "東方", "west": "西方", "north": "北方", "south": "南方"}[direction]
        omens.append(OmenAnalysis(
            omen_type="vrontologia",
            trigger_planet="Thunder",
            trigger_sign=month_name,
            severity=effect["severity"],
            omen_en=f"[{month_name} — Thunder from the {direction.capitalize()}] {effect['omen_en']}",
            omen_cn=f"[{month_data.get('month_cn', month_name)}—{direction_cn}雷鳴] {effect['omen_cn']}",
            region_en="Empire",
            region_cn="帝國全境",
            source_ref=month_data.get("source_ref", ""),
        ))

    return omens


# ============================================================
# Main Chart Computation
# ============================================================

def compute_byzantine_chart(
    year: int,
    month: int,
    day: int,
    hour: float,
    minute: float = 0.0,
    timezone: float = 0.0,
    latitude: float = 41.016,
    longitude: float = 28.977,
    location_name: str = "Constantinople",
    current_year: Optional[int] = None,
    chart_mode: str = "natal",
) -> ByzantineChart:
    """
    Compute a full Byzantine astrological chart.

    Args:
        year: birth/event year
        month: birth/event month (1–12)
        day: birth/event day
        hour: birth/event hour (24h)
        minute: birth/event minute
        timezone: UTC offset in hours
        latitude: geographic latitude
        longitude: geographic longitude
        location_name: place name for display
        current_year: year for profection computation (defaults to year+30)
        chart_mode: "natal" | "political" | "mundane" | "omen"

    Returns:
        ByzantineChart with all computed data

    Sources:
        Paul. Alex., Eisag.; Rhet. Aeg., Compend.; Heph. Theb., Apotel.
    """
    # Convert local time to UT
    hour_ut = hour + minute / 60.0 - timezone

    # Julian day
    jd = _julian_day(year, month, day, hour_ut)

    # House cusps and ascendant (Whole-sign houses as per Byzantine tradition)
    cusps, ascmc = swe.houses(jd, latitude, longitude, b"W")
    asc_lon = ascmc[0]
    mc_lon = ascmc[1]

    asc_sign, asc_idx, _ = _sign_from_lon(asc_lon)

    # Compute planet positions
    planets: List[ByzantinePlanetPos] = []
    planet_lons: Dict[str, float] = {}

    for planet_name, planet_id in _PLANET_IDS.items():
        try:
            pos, _ = swe.calc_ut(jd, planet_id)
            lon = pos[0]
            speed = pos[3]
            is_retro = speed < 0.0

            sign, sign_idx, deg_in_sign = _sign_from_lon(lon)
            sign_info = BYZANTINE_SIGN_NAMES[sign]
            house = _whole_sign_house(sign_idx, asc_idx)
            element = _element_of_sign(sign)
            quality = _quality_of_sign(sign)
            dignity = _dignity_of_planet(planet_name, sign)

            p_info = BYZANTINE_PLANET_NAMES.get(planet_name, {})

            planets.append(ByzantinePlanetPos(
                name=planet_name,
                longitude=round(lon, 4),
                sign=sign,
                sign_gr=sign_info["greek"],
                sign_cn=sign_info["cn"],
                sign_index=sign_idx,
                degree_in_sign=round(deg_in_sign, 4),
                house=house,
                is_retrograde=is_retro,
                element=element,
                quality=quality,
                dignity=dignity,
                glyph=p_info.get("glyph", ""),
            ))
            planet_lons[planet_name] = lon
        except Exception:
            pass

    # Determine day/night chart
    sun_lon = planet_lons.get("Sun", 0.0)
    moon_lon = planet_lons.get("Moon", 0.0)
    # Day chart if Sun is above horizon (houses 7–12)
    sun_sign, sun_idx, _ = _sign_from_lon(sun_lon)
    sun_house = _whole_sign_house(sun_idx, asc_idx)
    is_day = sun_house in (7, 8, 9, 10, 11, 12)

    # Lots
    lots = _compute_all_lots(asc_lon, planet_lons, is_day)

    # Aspects
    aspects = _compute_aspects(planet_lons)

    # Profection
    _current_year = current_year or (year + 30)
    profection = _compute_profection(asc_lon, year, _current_year)

    # Firdaria (compute to age 80)
    firdaria = _compute_firdaria(is_day, age=80)

    # Omen analysis
    omens: List[OmenAnalysis] = []
    omens.extend(_analyze_seismologia(planet_lons))
    omens.extend(_analyze_selenodromia(moon_lon, sun_lon))
    omens.extend(_analyze_vrontologia(month))

    asc_sign_info = BYZANTINE_SIGN_NAMES[asc_sign]

    return ByzantineChart(
        year=year,
        month=month,
        day=day,
        hour=hour + minute / 60.0,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        julian_day=jd,
        ascendant=asc_lon,
        midheaven=mc_lon,
        ascendant_sign=asc_sign,
        ascendant_sign_gr=asc_sign_info["greek"],
        is_day_chart=is_day,
        planets=planets,
        lots=lots,
        aspects=aspects,
        profection=profection,
        firdaria=firdaria,
        omens=omens,
        chart_mode=chart_mode,
    )


def load_historical_chart(chart_key: str) -> Optional[ByzantineChart]:
    """
    Load a preset historical Byzantine chart.

    Args:
        chart_key: key from POLITICAL_HOROSCOPES dict

    Returns:
        ByzantineChart or None if key not found or chart data incomplete
    """
    if chart_key not in POLITICAL_HOROSCOPES:
        return None

    data = POLITICAL_HOROSCOPES[chart_key]
    if data.get("julian_day_approx") is None:
        # Mythological chart — return None with note
        return None

    try:
        chart = compute_byzantine_chart(
            year=data["year"],
            month=data["month"],
            day=data["day"],
            hour=data["hour"],
            minute=data.get("minute", 0),
            timezone=2.0,  # approximate for Eastern Mediterranean
            latitude=data["latitude"],
            longitude=data["longitude"],
            location_name=data["location_name_en"],
            chart_mode="political",
        )
        chart.historical_name = data["name_en"]
        chart.historical_desc_en = data["description_en"]
        chart.historical_desc_cn = data["description_cn"]
        return chart
    except Exception:
        return None
