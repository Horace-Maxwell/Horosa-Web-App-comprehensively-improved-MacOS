"""
astro/horary/calculator.py — Traditional Horary Astrology Computation Engine

Implements both Western (Lilly/Bonatti) and Vedic (Prashna Marga) horary systems.

Sources:
- William Lilly, "Christian Astrology" (1647) [CA]
- Guido Bonatti, "Liber Astronomiae" (~1277) [LA]
-《Prasna Marga》— Traditional Kerala Prashna text [PM]
- Vettius Valens, "Anthology" [VV] (for ancient context)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import swisseph as swe

from .constants import (
    TRADITIONAL_PLANETS, PLANET_IDS, PLANET_GLYPHS, PLANET_CN,
    ZODIAC_SIGNS, SIGN_NAMES, SIGN_MODALITY,
    DOMICILE_RULERS, EXALTATION, FALL_SIGN, TRIPLICITY_RULERS,
    TERMS_PTOLEMY, FACES,
    DIGNITY_SCORES, ACCIDENTAL_DIGNITY_SCORES, MEAN_MOTION,
    PLANETARY_JOYS,
    ASPECT_DEFINITIONS,
    HOUSE_SIGNIFICATIONS, QUESTION_TYPES,
    STRICTURE_DESCRIPTIONS, VOC_EXCEPTIONS,
    COMBUSTION_ORB, CAZIMI_ORB, UNDER_SUNBEAMS_ORB,
    VIA_COMBUSTA_START, VIA_COMBUSTA_END,
    VEDIC_RASHIS, VEDIC_EXALTATION, VEDIC_DEBILITATION,
    VEDIC_OWN_SIGNS, PRASHNA_QUESTION_TYPES,
    TIMING_UNIT, HOUSE_TIMING,
    DETRIMENT_RULERS,
)


# ============================================================
# Helper Functions
# ============================================================

def _normalize(deg: float) -> float:
    """Normalise angle to 0–360°."""
    return deg % 360.0


def _sign_index(deg: float) -> int:
    """Return zodiac sign index (0=Aries … 11=Pisces) from ecliptic longitude."""
    return int(_normalize(deg) / 30.0)


def _sign_degree(deg: float) -> float:
    """Return degree within sign (0–30)."""
    return _normalize(deg) % 30.0


def _angular_distance(a: float, b: float) -> float:
    """Shortest angular distance between two ecliptic longitudes."""
    diff = abs(_normalize(a) - _normalize(b))
    if diff > 180.0:
        diff = 360.0 - diff
    return diff


def _arc_diff(a: float, b: float) -> float:
    """Signed difference a - b in range -180..180 (positive = a ahead of b)."""
    diff = (_normalize(a) - _normalize(b)) % 360.0
    if diff > 180.0:
        diff -= 360.0
    return diff


def _julian_day(year: int, month: int, day: int,
                hour: int, minute: int, timezone: float) -> float:
    """Convert local datetime to Julian Day Number (UT)."""
    decimal_hour = hour + minute / 60.0 - timezone
    return swe.julday(year, month, day, decimal_hour)


def _find_house(lon: float, cusps: Tuple[float, ...]) -> int:
    """Return house number (1-12) for given ecliptic longitude."""
    lon = _normalize(lon)
    for i in range(12):
        start = _normalize(cusps[i])
        end = _normalize(cusps[(i + 1) % 12])
        if start < end:
            if start <= lon < end:
                return i + 1
        else:
            if lon >= start or lon < end:
                return i + 1
    return 1


def _format_dms(deg: float) -> str:
    """Format decimal degrees as D°M'S\"."""
    deg = _normalize(deg)
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""


def _sign_pos_str(deg: float) -> str:
    """Format ecliptic longitude as 'DD° SignName' (e.g. '15° Aries')."""
    idx = _sign_index(deg)
    sign = ZODIAC_SIGNS[idx][0]
    d = _sign_degree(deg)
    return f"{int(d)}°{int((d % 1) * 60):02d}' {sign}"


# ============================================================
# Essential Dignity Calculation
# ============================================================

def _get_essential_dignity(planet: str, lon: float) -> Tuple[str, int]:
    """
    Return (dignity_name, score) for a planet at a given longitude.

    Order of precedence: domicile > exaltation > triplicity > term > face > detriment > fall.
    Source: Lilly CA pp. 101-116; Bonatti LA Tract. I
    """
    sign_idx = _sign_index(lon)
    deg_in_sign = _sign_degree(lon)
    sign_name = ZODIAC_SIGNS[sign_idx][0]
    element = ZODIAC_SIGNS[sign_idx][3]

    # Domicile
    if DOMICILE_RULERS.get(sign_idx) == planet:
        return ("domicile", DIGNITY_SCORES["domicile"])

    # Exaltation
    if planet in EXALTATION:
        ex_sign, ex_deg = EXALTATION[planet]
        if sign_idx == ex_sign:
            return ("exaltation", DIGNITY_SCORES["exaltation"])

    # Detriment (opposite sign of domicile)
    if DETRIMENT_RULERS.get(sign_idx) == planet:
        return ("detriment", DIGNITY_SCORES["detriment"])

    # Fall (opposite sign of exaltation)
    if planet in FALL_SIGN and FALL_SIGN[planet] == sign_idx:
        return ("fall", DIGNITY_SCORES["fall"])

    # Triplicity
    trip = TRIPLICITY_RULERS.get(element)
    if trip:
        if planet in trip[:2]:  # day or night ruler
            return ("triplicity", DIGNITY_SCORES["triplicity"])

    # Term (Ptolemaic bounds)
    terms = TERMS_PTOLEMY.get(sign_idx, [])
    for (term_planet, start, end) in terms:
        if term_planet == planet and start <= deg_in_sign < end:
            return ("term", DIGNITY_SCORES["term"])

    # Face / Decanate
    face_idx = int(deg_in_sign / 10)
    face_rulers = FACES.get(sign_idx, [])
    if face_idx < len(face_rulers) and face_rulers[face_idx] == planet:
        return ("face", DIGNITY_SCORES["face"])

    return ("peregrine", DIGNITY_SCORES["peregrine"])


def _get_combust_status(planet: str, planet_lon: float, sun_lon: float) -> str:
    """
    Return combustion status relative to the Sun.
    Source: Lilly CA p. 113; Bonatti LA Tract. I
    """
    if planet == "Sun":
        return "none"
    dist = _angular_distance(planet_lon, sun_lon)
    if dist <= CAZIMI_ORB:
        return "cazimi"  # In the heart of the Sun — special dignity
    if dist <= COMBUSTION_ORB:
        return "combust"
    if dist <= UNDER_SUNBEAMS_ORB:
        return "under_sunbeams"
    return "free"


def _is_oriental(planet: str, planet_lon: float, sun_lon: float) -> bool:
    """
    A planet is Oriental of the Sun if it rises before the Sun (ahead in zodiac).
    Superior planets (Mars, Jupiter, Saturn) are stronger when Oriental.
    Inferior planets (Mercury, Venus, Moon) are stronger when Occidental.
    Source: Lilly CA p. 113
    """
    # Oriental = planet's longitude is ahead of the Sun (modulo 360)
    diff = _arc_diff(planet_lon, sun_lon)
    return diff > 0.0


def _is_in_via_combusta(lon: float) -> bool:
    """Check if longitude is in Via Combusta (15° Libra – 15° Scorpio)."""
    lon = _normalize(lon)
    return VIA_COMBUSTA_START <= lon <= VIA_COMBUSTA_END


# ============================================================
# Data Classes
# ============================================================

@dataclass
class HoraryPlanet:
    """Planet position and dignities for a horary chart."""
    name: str
    glyph: str
    name_cn: str
    longitude: float
    sign: str
    sign_cn: str
    sign_glyph: str
    sign_index: int
    degree_in_sign: float
    house: int
    retrograde: bool
    speed: float
    essential_dignity: str   # domicile / exaltation / triplicity / term / face / peregrine / detriment / fall
    essential_score: int
    combust_status: str      # cazimi / combust / under_sunbeams / free
    accidental_score: int
    total_strength: int
    is_fast: bool            # faster than mean motion
    is_oriental: bool        # oriental of the Sun
    in_joy: bool             # in its joy house
    in_via_combusta: bool    # for Moon only
    formatted_pos: str       # "15°23' Aries"

    def strength_label(self) -> str:
        """Return a human-readable strength assessment."""
        if self.essential_dignity == "domicile":
            return "Essential Strength: In Domicile (入廟) ★★★★★"
        if self.essential_dignity == "exaltation":
            return "Essential Strength: In Exaltation (入旺) ★★★★☆"
        if self.essential_dignity == "triplicity":
            return "Essential Strength: In Triplicity (三合尊貴) ★★★☆☆"
        if self.essential_dignity == "term":
            return "Essential Strength: In Term (界) ★★☆☆☆"
        if self.essential_dignity == "face":
            return "Essential Strength: In Face/Decanate (旬) ★☆☆☆☆"
        if self.essential_dignity == "detriment":
            return "Essential Weakness: In Detriment (落陷) ✗✗✗✗✗"
        if self.essential_dignity == "fall":
            return "Essential Weakness: In Fall (失旺) ✗✗✗✗☆"
        return "Essential Strength: Peregrine (漂泊) ○"


@dataclass
class HoraryAspect:
    """An aspect between two planets in a horary chart."""
    planet1: str
    planet2: str
    aspect_name: str
    aspect_cn: str
    angle: float
    orb: float
    exact_angle: float
    is_applying: bool        # True = applying, False = separating
    is_partile: bool         # within 1° orb
    nature: str              # benefic / malefic / neutral
    has_reception: bool      # mutual or one-way reception
    reception_type: str      # "mutual_domicile", "mutual_exaltation", "one_way", "none"

    def description(self) -> str:
        """Return formatted aspect description."""
        status = "Applying (入相)" if self.is_applying else "Separating (離相)"
        partile = " [Partile]" if self.is_partile else ""
        reception = f" [Reception: {self.reception_type}]" if self.has_reception else ""
        return f"{self.planet1} {self.aspect_name} {self.planet2} ({self.orb:.2f}° orb, {status}){partile}{reception}"


@dataclass
class VoidOfCourseMoon:
    """Void of Course Moon analysis."""
    is_voc: bool
    last_aspect: Optional[str]      # description of last aspect made
    next_sign: str                   # sign Moon will enter next
    sign_index: int                  # current sign
    has_exception: bool              # True if in one of Lilly's exception signs
    exception_note: str              # Lilly's exception description


@dataclass
class Stricture:
    """A stricture against judgment."""
    key: str
    severity: str                    # warning / caution / info
    en: str
    cn: str
    lilly_ref: str


@dataclass
class TranslationOfLight:
    """Translation of Light between two significators."""
    carrier_planet: str              # planet translating the light
    from_planet: str                 # planet that separated
    to_planet: str                   # planet that will conjoin
    description_en: str
    description_cn: str


@dataclass
class CollectionOfLight:
    """Collection of Light."""
    collector_planet: str            # planet collecting both lights
    significator1: str
    significator2: str
    description_en: str
    description_cn: str


@dataclass
class WesternHoraryJudgment:
    """The horary judgment for a Western (Lilly/Bonatti) horary question."""
    question: str
    question_type: str
    querent_significator: str        # Lord of ASC
    quesited_significator: str       # Lord of relevant house
    perfection_method: str           # how/if the matter perfects
    verdict: str                     # "yes" / "no" / "unclear" / "depends"
    verdict_cn: str
    timing_hint: str
    timing_hint_cn: str
    key_factors: List[str]
    warnings: List[str]
    aphorisms_applied: List[str]     # Lilly aphorisms that apply
    full_judgment_en: str
    full_judgment_cn: str


@dataclass
class WesternHoraryChart:
    """Complete Western Horary Chart (Lilly/Bonatti tradition)."""
    # Time and place
    question_datetime: str
    latitude: float
    longitude: float
    location_name: str
    question_text: str
    question_type: str

    # Computed values
    julian_day: float
    ascendant: float
    midheaven: float
    asc_sign: str
    asc_sign_cn: str
    asc_degree: float
    asc_lord: str                    # Lord of ASC = Querent's significator

    # Planets
    planets: List[HoraryPlanet]

    # House cusps
    house_cusps: List[float]         # 12 cusps (0-indexed)
    house_signs: List[str]           # sign on each cusp

    # Aspects
    aspects: List[HoraryAspect]

    # Moon
    moon_voc: VoidOfCourseMoon
    moon_in_via_combusta: bool

    # Strictures
    strictures: List[Stricture]

    # Special techniques
    translations_of_light: List[TranslationOfLight]
    collections_of_light: List[CollectionOfLight]

    # Planetary hour lord (radicality check)
    planetary_hour_lord: str
    is_radical: bool                 # ASC lord == planetary hour lord

    # Judgment
    judgment: WesternHoraryJudgment


@dataclass
class VedicPlanetPos:
    """Vedic planet position for Prashna."""
    name: str
    name_vedic: str
    longitude: float
    sign: str                        # Rashi name (Vedic)
    sign_cn: str
    sign_lord: str
    sign_index: int
    degree_in_sign: float
    house: int
    retrograde: bool
    speed: float
    dignity: str                     # exalted / own / debilitated / neutral
    formatted_pos: str


@dataclass
class ArudhaLagna:
    """Arudha Lagna computation result."""
    sign_index: int
    sign: str
    sign_cn: str
    longitude: float
    description_en: str
    description_cn: str


@dataclass
class VedicPrashnaNumerology:
    """Optional number-based Lagna determination (1-108)."""
    number: int
    rashi_index: int                 # derived sign index
    rashi: str
    navamsa_pada: int                # 1-9 cycle
    description_en: str
    description_cn: str


@dataclass
class VedicPrashnaJudgment:
    """The Vedic Prashna judgment."""
    question: str
    question_type: str
    lagna_lord: str
    lagna_lord_status: str
    moon_status: str
    verdict: str
    verdict_cn: str
    key_yogas: List[str]
    key_factors_en: List[str]
    key_factors_cn: List[str]
    timing_hint: str
    timing_hint_cn: str
    full_judgment_en: str
    full_judgment_cn: str


@dataclass
class VedicPrashnaChart:
    """Complete Vedic Prashna Chart (Prasna Marga tradition)."""
    # Time and place
    question_datetime: str
    latitude: float
    longitude: float
    location_name: str
    question_text: str
    question_type: str

    # Computed values
    julian_day: float
    ayanamsa: float
    ascendant: float                 # sidereal
    asc_sign: str
    asc_sign_cn: str
    asc_degree: float
    asc_lord: str

    # Planets
    planets: List[VedicPlanetPos]

    # House cusps (sidereal)
    house_cusps: List[float]
    house_signs: List[str]

    # Arudha Lagna
    arudha_lagna: ArudhaLagna

    # Optional: number-based Lagna
    numerology: Optional[VedicPrashnaNumerology]

    # Judgment
    judgment: VedicPrashnaJudgment


# ============================================================
# Core Western Horary Computation
# ============================================================

def _compute_planets_horary(jd: float) -> Tuple[List[HoraryPlanet], float]:
    """
    Compute positions of the seven traditional planets for a horary chart.

    Returns: (list of HoraryPlanet, sun_longitude)
    """
    swe.set_ephe_path("")

    planet_data: Dict[str, Dict] = {}
    for pname in TRADITIONAL_PLANETS:
        pid = PLANET_IDS[pname]
        res, _ = swe.calc_ut(jd, pid)
        planet_data[pname] = {
            "lon": _normalize(res[0]),
            "speed": res[3],
        }

    sun_lon = planet_data["Sun"]["lon"]

    # We need house data to assign houses; but houses are computed in the main function.
    # Return raw data; houses assigned later.
    return planet_data, sun_lon


def _compute_aspects(planets: List[HoraryPlanet]) -> List[HoraryAspect]:
    """
    Compute all aspects between the seven traditional planets.

    Applies/separates logic: if planet A is faster and moving towards the
    exact aspect, it is applying. Source: Lilly CA pp. 108-110.
    """
    aspects: List[HoraryAspect] = []
    planet_dict = {p.name: p for p in planets}

    for i, p1 in enumerate(planets):
        for j, p2 in enumerate(planets):
            if j <= i:
                continue
            lon1, lon2 = p1.longitude, p2.longitude
            for asp_def in ASPECT_DEFINITIONS:
                target_angle = asp_def["angle"]
                orb = asp_def["orb"]
                # Compute actual angular separation
                diff = abs(_normalize(lon1 - lon2))
                if diff > 180.0:
                    diff = 360.0 - diff

                actual_orb = abs(diff - target_angle)
                if actual_orb > orb:
                    continue

                # Determine applying / separating
                # Faster planet is the one applying
                # Applying: the angular separation is decreasing (planets moving towards exact aspect)
                spd1, spd2 = p1.speed, p2.speed
                # Net approach rate: positive = approaching
                # For most aspects: applying if faster planet is moving towards the aspect angle
                is_applying = _is_applying_aspect(lon1, lon2, spd1, spd2, target_angle)

                # Reception check
                has_reception, reception_type = _check_reception(p1, p2)

                # Partile: orb within 1°
                is_partile = actual_orb <= 1.0

                aspects.append(HoraryAspect(
                    planet1=p1.name,
                    planet2=p2.name,
                    aspect_name=asp_def["en"],
                    aspect_cn=asp_def["cn"],
                    angle=target_angle,
                    orb=actual_orb,
                    exact_angle=target_angle,
                    is_applying=is_applying,
                    is_partile=is_partile,
                    nature=asp_def["nature"],
                    has_reception=has_reception,
                    reception_type=reception_type,
                ))

    # Sort by orb (tightest first)
    aspects.sort(key=lambda a: a.orb)
    return aspects


def _is_applying_aspect(lon1: float, lon2: float, spd1: float, spd2: float,
                         target_angle: float) -> bool:
    """
    Determine if the aspect is applying or separating.

    For an applying aspect, the orb must be decreasing (planets moving toward exact).
    The faster planet is the one 'applying' to the slower.
    Source: Lilly CA p. 109: "Applying is when the lesser planet is moving toward
    the greater, or when both move toward each other."
    """
    # Current signed difference
    diff_now = _arc_diff(lon1, lon2)

    # Small time step to check direction
    dt = 0.01  # 0.01 days ~ 14 minutes
    lon1_fut = lon1 + spd1 * dt
    lon2_fut = lon2 + spd2 * dt
    diff_fut = _arc_diff(lon1_fut, lon2_fut)

    # Orb of aspect currently vs future
    def _orb(d: float) -> float:
        return abs(abs(d) - target_angle)

    orb_now = _orb(diff_now)
    orb_fut = _orb(diff_fut)
    return orb_fut < orb_now  # applying if getting tighter


def _check_reception(p1: HoraryPlanet, p2: HoraryPlanet) -> Tuple[bool, str]:
    """
    Check for mutual or one-way reception between two planets.

    Reception: planet A is in the sign (or exaltation) of planet B and vice versa.
    Source: Lilly CA pp. 126-128; Bonatti LA Tract. I
    """
    p1_sign_lord = DOMICILE_RULERS.get(p1.sign_index)
    p2_sign_lord = DOMICILE_RULERS.get(p2.sign_index)

    p1_ex_sign = EXALTATION.get(p1.name, (None, None))[0]
    p2_ex_sign = EXALTATION.get(p2.name, (None, None))[0]

    # p1 receives p2 (p2 is in p1's sign)
    p1_receives_p2 = (DOMICILE_RULERS.get(p2.sign_index) == p1.name)
    # p2 receives p1 (p1 is in p2's sign)
    p2_receives_p1 = (DOMICILE_RULERS.get(p1.sign_index) == p2.name)

    # Exaltation reception
    p1_ex_receives_p2 = (p1_ex_sign is not None and p2.sign_index == p1_ex_sign)
    p2_ex_receives_p1 = (p2_ex_sign is not None and p1.sign_index == p2_ex_sign)

    if (p1_receives_p2 or p1_ex_receives_p2) and (p2_receives_p1 or p2_ex_receives_p1):
        return (True, "mutual_domicile" if (p1_receives_p2 and p2_receives_p1) else "mutual_exaltation")
    if p1_receives_p2 or p1_ex_receives_p2 or p2_receives_p1 or p2_ex_receives_p1:
        return (True, "one_way")

    return (False, "none")


def _compute_voc_moon(moon_lon: float, moon_speed: float,
                      planets: List[HoraryPlanet]) -> VoidOfCourseMoon:
    """
    Compute Void of Course Moon status.

    Lilly's definition: Moon is VOC when it makes no more applying aspects to
    any of the seven traditional planets before leaving its current sign.
    Exception: in Taurus, Cancer, Sagittarius, Pisces — VOC may still yield results.
    Source: Lilly CA p. 122
    """
    sign_idx = _sign_index(moon_lon)
    deg_in_sign = _sign_degree(moon_lon)
    degrees_to_end = 30.0 - deg_in_sign  # degrees remaining in sign

    # Next sign
    next_sign_idx = (sign_idx + 1) % 12
    next_sign = ZODIAC_SIGNS[next_sign_idx][0]

    # Check applying aspects to all planets within remaining degrees
    last_aspect_desc = None
    will_aspect = False

    for planet in planets:
        if planet.name == "Moon":
            continue
        # For each major aspect, will Moon reach it before leaving sign?
        for asp_def in ASPECT_DEFINITIONS[:5]:  # Major aspects only
            target = asp_def["angle"]
            # Current difference
            diff = _arc_diff(moon_lon, planet.longitude)
            raw_diff = abs(diff)
            if raw_diff > 180:
                raw_diff = 360 - raw_diff
            current_orb = abs(raw_diff - target)

            if current_orb <= asp_def["orb"] and _is_applying_aspect(
                moon_lon, planet.longitude, moon_speed, planet.speed, target
            ):
                # Applying aspect found — not VOC
                will_aspect = True
                last_aspect_desc = f"Moon {asp_def['en']} {planet.name} (orb {current_orb:.1f}°)"
                break
            elif not _is_applying_aspect(
                moon_lon, planet.longitude, moon_speed, planet.speed, target
            ):
                # Separating — track as last aspect
                if current_orb <= asp_def["orb"]:
                    last_aspect_desc = f"Moon separating from {asp_def['en']} {planet.name}"
        if will_aspect:
            break

    is_voc = not will_aspect
    has_exception = sign_idx in VOC_EXCEPTIONS
    exception_note = ""
    if has_exception:
        sign_name = ZODIAC_SIGNS[sign_idx][0]
        exception_note = (
            f"Lilly's exception: Moon VOC in {sign_name} may still yield results, "
            f"though slowly. (CA p. 122)"
        )

    return VoidOfCourseMoon(
        is_voc=is_voc,
        last_aspect=last_aspect_desc,
        next_sign=next_sign,
        sign_index=sign_idx,
        has_exception=has_exception,
        exception_note=exception_note,
    )


def _check_strictures(asc_degree: float, planets: List[HoraryPlanet],
                      moon_voc: VoidOfCourseMoon) -> List[Stricture]:
    """
    Check for Strictures Against Judgment.
    Source: Lilly CA pp. 121-123; Bonatti LA 4th Consideration
    """
    strictures: List[Stricture] = []
    asc_deg_in_sign = _sign_degree(asc_degree)

    # Early Ascendant (< 3°)
    if asc_deg_in_sign < 3.0:
        s = STRICTURE_DESCRIPTIONS["early_ascendant"]
        strictures.append(Stricture(
            key="early_ascendant",
            severity=s["severity"],
            en=s["en"],
            cn=s["cn"],
            lilly_ref=s["lilly_ref"],
        ))

    # Late Ascendant (> 27°)
    if asc_deg_in_sign > 27.0:
        s = STRICTURE_DESCRIPTIONS["late_ascendant"]
        strictures.append(Stricture(
            key="late_ascendant",
            severity=s["severity"],
            en=s["en"],
            cn=s["cn"],
            lilly_ref=s["lilly_ref"],
        ))

    # VOC Moon
    if moon_voc.is_voc and not moon_voc.has_exception:
        s = STRICTURE_DESCRIPTIONS["voc_moon"]
        strictures.append(Stricture(
            key="voc_moon",
            severity=s["severity"],
            en=s["en"],
            cn=s["cn"],
            lilly_ref=s["lilly_ref"],
        ))

    # Saturn in 1st
    for p in planets:
        if p.name == "Saturn" and p.house == 1:
            s = STRICTURE_DESCRIPTIONS["saturn_in_1st"]
            strictures.append(Stricture(
                key="saturn_in_1st",
                severity=s["severity"],
                en=s["en"],
                cn=s["cn"],
                lilly_ref=s["lilly_ref"],
            ))
        if p.name == "Saturn" and p.house == 7:
            s = STRICTURE_DESCRIPTIONS["saturn_in_7th"]
            strictures.append(Stricture(
                key="saturn_in_7th",
                severity=s["severity"],
                en=s["en"],
                cn=s["cn"],
                lilly_ref=s["lilly_ref"],
            ))

    # Moon in Via Combusta
    moon = next((p for p in planets if p.name == "Moon"), None)
    if moon and moon.in_via_combusta:
        s = STRICTURE_DESCRIPTIONS["moon_in_via_combusta"]
        strictures.append(Stricture(
            key="moon_in_via_combusta",
            severity=s["severity"],
            en=s["en"],
            cn=s["cn"],
            lilly_ref=s["lilly_ref"],
        ))

    return strictures


def _compute_planetary_hour_lord(jd: float, latitude: float, longitude: float) -> str:
    """
    Compute the Planetary Hour Lord at the time of the question.

    Used for radicality check (Bonatti's 1st Consideration).
    The 7 planets cycle in Chaldean order from Saturn down to Moon.
    Source: Bonatti LA 1st Consideration; Lilly CA p. 481
    """
    # Compute sunrise and sunset for the day
    # Julian day at local midnight
    gmt_day = jd  # already in UT

    # Compute sunrise
    try:
        rise_res = swe.rise_trans(gmt_day - 0.5, swe.SUN, b"", swe.FLG_SWIEPH,
                                   swe.CALC_RISE, [latitude, longitude, 0])
        sunrise_jd = rise_res[1][0]
        set_res = swe.rise_trans(gmt_day - 0.5, swe.SUN, b"", swe.FLG_SWIEPH,
                                  swe.CALC_SET, [latitude, longitude, 0])
        sunset_jd = set_res[1][0]
    except Exception:
        # Fallback: approximate
        sunrise_jd = gmt_day - 0.25  # 6am UTC
        sunset_jd = gmt_day + 0.25   # 6pm UTC

    # Day of week (0=Monday in Python, but we need Sunday=0 for Chaldean)
    # Use Julian Day: JD 0.0 = Monday, January 1, 4713 BC (Julian)
    # Day rulers: Sunday=Sun, Monday=Moon, Tuesday=Mars, Wednesday=Mercury,
    # Thursday=Jupiter, Friday=Venus, Saturday=Saturn
    day_of_week = int(jd + 1.5) % 7  # 0=Sun, 1=Mon, 2=Tue, ...
    _CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
    _DAY_RULERS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    day_ruler = _DAY_RULERS[day_of_week]
    # First hour of the day is ruled by the day ruler
    day_ruler_idx = _CHALDEAN_ORDER.index(day_ruler)

    # Determine if daytime or nighttime
    is_day = sunrise_jd <= gmt_day <= sunset_jd

    if is_day:
        day_len = sunset_jd - sunrise_jd
        hours_since_sunrise = (gmt_day - sunrise_jd) / day_len * 12.0
    else:
        night_start = sunset_jd
        next_sunrise = sunrise_jd + 1.0  # approximate
        night_len = next_sunrise - night_start
        if gmt_day >= sunset_jd:
            hours_since_sunset = (gmt_day - night_start) / night_len * 12.0
        else:
            hours_since_sunset = (gmt_day - (night_start - 1.0)) / night_len * 12.0
        hours_since_sunrise = 12.0 + hours_since_sunset

    hour_number = int(hours_since_sunrise)
    planet_idx = (day_ruler_idx + hour_number) % 7
    return _CHALDEAN_ORDER[planet_idx]


def _compute_translation_of_light(significator1: str, significator2: str,
                                    planets: List[HoraryPlanet],
                                    aspects: List[HoraryAspect]) -> List[TranslationOfLight]:
    """
    Check for Translation of Light between significators.

    Translation of Light: A swifter planet separates from one significator and
    applies to another, carrying ('translating') the light from one to the other.
    Source: Lilly CA pp. 128-129; Bonatti LA Tract. I
    """
    translations: List[TranslationOfLight] = []
    planet_dict = {p.name: p for p in planets}

    sig1 = planet_dict.get(significator1)
    sig2 = planet_dict.get(significator2)
    if not sig1 or not sig2:
        return translations

    # Look for a planet that:
    # 1. Has separated from sig1 (within a wide orb, separating)
    # 2. Is now applying to sig2
    for carrier in planets:
        if carrier.name in (significator1, significator2):
            continue
        # Check separation from sig1
        sep_from_sig1 = False
        app_to_sig2 = False
        for asp in aspects:
            if (asp.planet1 == carrier.name and asp.planet2 == significator1) or \
               (asp.planet2 == carrier.name and asp.planet1 == significator1):
                if not asp.is_applying:
                    sep_from_sig1 = True
            if (asp.planet1 == carrier.name and asp.planet2 == significator2) or \
               (asp.planet2 == carrier.name and asp.planet1 == significator2):
                if asp.is_applying:
                    app_to_sig2 = True

        if sep_from_sig1 and app_to_sig2:
            translations.append(TranslationOfLight(
                carrier_planet=carrier.name,
                from_planet=significator1,
                to_planet=significator2,
                description_en=(
                    f"{carrier.name} separates from {significator1} and applies to {significator2}, "
                    f"translating the light between the significators. "
                    f"This may bring the matter to perfection. (Lilly CA p. 129)"
                ),
                description_cn=(
                    f"{PLANET_CN.get(carrier.name, carrier.name)}離相於{PLANET_CN.get(significator1, significator1)}"
                    f"，並入相於{PLANET_CN.get(significator2, significator2)}，"
                    f"在主星之間傳遞光芒。此可使事情得以完成。（Lilly CA p. 129）"
                ),
            ))

    return translations


def _compute_collection_of_light(significator1: str, significator2: str,
                                   planets: List[HoraryPlanet],
                                   aspects: List[HoraryAspect]) -> List[CollectionOfLight]:
    """
    Check for Collection of Light.

    Collection of Light: Both significators apply to a third, heavier planet,
    which collects their light and perfects the matter.
    Source: Lilly CA p. 129; Bonatti LA Tract. I
    """
    collections: List[CollectionOfLight] = []
    planet_dict = {p.name: p for p in planets}

    sig1 = planet_dict.get(significator1)
    sig2 = planet_dict.get(significator2)
    if not sig1 or not sig2:
        return collections

    # The collector must be heavier (slower) than both significators
    collector_candidates = [
        p for p in planets
        if p.name not in (significator1, significator2) and
           abs(p.speed) < min(abs(sig1.speed), abs(sig2.speed))
    ]

    for collector in collector_candidates:
        sig1_applies = False
        sig2_applies = False
        for asp in aspects:
            names = {asp.planet1, asp.planet2}
            if collector.name in names:
                other = asp.planet2 if asp.planet1 == collector.name else asp.planet1
                if other == significator1 and asp.is_applying:
                    sig1_applies = True
                if other == significator2 and asp.is_applying:
                    sig2_applies = True

        if sig1_applies and sig2_applies:
            collections.append(CollectionOfLight(
                collector_planet=collector.name,
                significator1=significator1,
                significator2=significator2,
                description_en=(
                    f"Both {significator1} and {significator2} apply to {collector.name}, "
                    f"which collects their light and may bring the matter to perfection. "
                    f"(Lilly CA p. 129)"
                ),
                description_cn=(
                    f"{PLANET_CN.get(significator1, significator1)}與"
                    f"{PLANET_CN.get(significator2, significator2)}"
                    f"均入相於{PLANET_CN.get(collector.name, collector.name)}，"
                    f"後者聚其光芒，或可使事情圓滿。（Lilly CA p. 129）"
                ),
            ))

    return collections


def _judge_western_horary(
    question_type: str,
    question_text: str,
    asc_lord: str,
    planets: List[HoraryPlanet],
    aspects: List[HoraryAspect],
    moon_voc: VoidOfCourseMoon,
    strictures: List[Stricture],
    translations: List[TranslationOfLight],
    collections: List[CollectionOfLight],
) -> WesternHoraryJudgment:
    """
    Produce a traditional Horary judgment.

    Combines Lilly's perfection techniques with Bonatti's consideration framework.
    Source: Lilly CA Part I & II; Bonatti LA 146 Considerations
    """
    qt = QUESTION_TYPES.get(question_type, QUESTION_TYPES["general"])
    q_house = qt["primary_house"]

    # Find quesited significator = Lord of the question house
    from .constants import DOMICILE_RULERS, ZODIAC_SIGNS
    house_cusp_sign_idx = None
    planet_dict = {p.name: p for p in planets}

    # The quesited is the lord of the relevant house
    # We need the house sign — use the house's cusp sign for lord determination
    # As a fallback, use position of relevant planets
    quesited = None
    for p in planets:
        if p.house == q_house:
            quesited = DOMICILE_RULERS.get(p.sign_index, asc_lord)
            break

    # Primary method: find the lord of the house cusp sign (set in WesternHoraryChart)
    # We determine it from the house signs list — but that's in the chart, not here.
    # For judgment, look for applying/separating aspects between querent and quesited.
    if quesited is None:
        quesited = "Moon"  # Moon as general significatrix

    # Determine perfection method
    perfection_method = "none"
    verdict = "unclear"
    verdict_cn = "不明"
    key_factors: List[str] = []
    warnings: List[str] = []
    aphorisms: List[str] = []

    # Check for direct aspect between querent and quesited
    for asp in aspects:
        if {asp.planet1, asp.planet2} == {asc_lord, quesited}:
            if asp.is_applying:
                if asp.nature in ("benefic", "neutral"):
                    perfection_method = f"Direct applying {asp.aspect_name}"
                    verdict = "yes" if asp.nature == "benefic" else "unclear"
                    verdict_cn = "是" if asp.nature == "benefic" else "不明"
                    key_factors.append(
                        f"✅ {asc_lord} applies to {quesited} by {asp.aspect_name} "
                        f"(orb {asp.orb:.1f}°, {'partile' if asp.is_partile else 'platic'})"
                    )
                    if asp.has_reception:
                        key_factors.append(
                            f"✅ Reception: {asp.reception_type} — greatly assists perfection. "
                            f"(Lilly CA p. 126)"
                        )
                        aphorisms.append("Aphorism 5: Mutual reception assists perfection.")
                else:
                    perfection_method = f"Afflicted aspect ({asp.aspect_name})"
                    verdict = "no"
                    verdict_cn = "否"
                    key_factors.append(
                        f"⚠️ {asc_lord} applies to {quesited} by {asp.aspect_name} "
                        f"(malefic aspect, orb {asp.orb:.1f}°)"
                    )
            else:
                key_factors.append(
                    f"↩️ {asc_lord} separating from {quesited} by {asp.aspect_name} — "
                    f"matter has already passed or moving away."
                )
            break

    # Translation of Light
    if translations:
        t = translations[0]
        if verdict == "unclear":
            verdict = "yes_via_translation"
            verdict_cn = "可成（光之傳遞）"
        key_factors.append(
            f"🔄 Translation of Light: {t.carrier_planet} carries light from "
            f"{t.from_planet} to {t.to_planet}. (CA p. 129)"
        )
        aphorisms.append("Aphorism 6: Translation of Light may perfect the matter.")
        perfection_method = "Translation of Light"

    # Collection of Light
    if collections:
        c = collections[0]
        if verdict in ("unclear", "none"):
            verdict = "yes_via_collection"
            verdict_cn = "可成（光之聚合）"
        key_factors.append(
            f"⭕ Collection of Light: {c.collector_planet} collects light from "
            f"{c.significator1} and {c.significator2}. (CA p. 129)"
        )
        aphorisms.append("Aphorism 7: Collection of Light may perfect the matter.")
        perfection_method = "Collection of Light"

    # VOC Moon warnings
    if moon_voc.is_voc:
        if moon_voc.has_exception:
            warnings.append(
                f"⚠️ Moon is Void of Course in {ZODIAC_SIGNS[moon_voc.sign_index][0]}, "
                f"but Lilly's exception applies (may still yield results, slowly)."
            )
            aphorisms.append("Aphorism 2: VOC Moon in exception sign may yet yield results.")
        else:
            warnings.append(
                "⛔ Moon is Void of Course — matter will likely come to nothing. "
                "(Lilly CA p. 122)"
            )
            if verdict in ("unclear", "none"):
                verdict = "no"
                verdict_cn = "否"

    # Stricture warnings
    for s in strictures:
        if s.severity == "warning":
            warnings.append(f"⛔ Stricture: {s.en} ({s.lilly_ref})")
        elif s.severity == "caution":
            warnings.append(f"⚠️ Caution: {s.en} ({s.lilly_ref})")

    # Planet strength assessment
    for p in planets:
        if p.name in (asc_lord, quesited):
            if p.combust_status == "combust":
                warnings.append(
                    f"⛔ {p.name} is COMBUST — severely weakened, cannot perform. "
                    f"(Lilly CA p. 113)"
                )
                aphorisms.append("Aphorism 4: A combust planet cannot help the querent.")
            elif p.combust_status == "cazimi":
                key_factors.append(
                    f"✨ {p.name} is CAZIMI (in the heart of the Sun) — "
                    f"exceptionally strong despite proximity. (CA p. 113)"
                )

    # Timing hint
    moon = next((p for p in planets if p.name == "Moon"), None)
    timing_en = timing_cn = "Timing unclear"
    if moon:
        modality = SIGN_MODALITY.get(moon.sign, "Mutable")
        t_info = TIMING_UNIT.get(modality, {})
        timing_en = t_info.get("en", "Timing unclear")
        timing_cn = t_info.get("cn", "時機不明")

    # Compose full judgment text
    full_en = _compose_western_judgment_en(
        question_text, question_type, asc_lord, quesited, verdict,
        key_factors, warnings, aphorisms, perfection_method, timing_en
    )
    full_cn = _compose_western_judgment_cn(
        question_text, question_type, asc_lord, quesited, verdict_cn,
        key_factors, warnings, aphorisms, perfection_method, timing_cn
    )

    return WesternHoraryJudgment(
        question=question_text,
        question_type=question_type,
        querent_significator=asc_lord,
        quesited_significator=quesited,
        perfection_method=perfection_method,
        verdict=verdict,
        verdict_cn=verdict_cn,
        timing_hint=timing_en,
        timing_hint_cn=timing_cn,
        key_factors=key_factors,
        warnings=warnings,
        aphorisms_applied=aphorisms,
        full_judgment_en=full_en,
        full_judgment_cn=full_cn,
    )


def _compose_western_judgment_en(question, q_type, querent, quesited, verdict,
                                   factors, warnings, aphorisms, method, timing) -> str:
    lines = [
        f"═══ HORARY JUDGMENT (Lilly/Bonatti Tradition) ═══",
        f"Question: {question}",
        f"Type: {QUESTION_TYPES.get(q_type, {}).get('en', q_type)}",
        f"",
        f"Querent's Significator: {querent} {PLANET_GLYPHS.get(querent, '')}",
        f"Quesited's Significator: {quesited} {PLANET_GLYPHS.get(quesited, '')}",
        f"",
        f"VERDICT: {verdict.upper().replace('_', ' ')}",
        f"Perfection Method: {method}",
        f"",
    ]
    if factors:
        lines.append("Key Factors:")
        lines.extend(f"  {f}" for f in factors)
        lines.append("")
    if warnings:
        lines.append("Cautions & Strictures:")
        lines.extend(f"  {w}" for w in warnings)
        lines.append("")
    if aphorisms:
        lines.append("Applied Aphorisms (Lilly):")
        lines.extend(f"  {a}" for a in aphorisms)
        lines.append("")
    lines.append(f"Timing: {timing}")
    return "\n".join(lines)


def _compose_western_judgment_cn(question, q_type, querent, quesited, verdict_cn,
                                   factors, warnings, aphorisms, method, timing_cn) -> str:
    q_cn = PLANET_CN.get(querent, querent)
    qs_cn = PLANET_CN.get(quesited, quesited)
    lines = [
        f"═══ 卜卦占星判斷（Lilly / Bonatti 傳統）═══",
        f"問題：{question}",
        f"問題類型：{QUESTION_TYPES.get(q_type, {}).get('cn', q_type)}",
        f"",
        f"問卜者主星：{q_cn} {PLANET_GLYPHS.get(querent, '')}",
        f"所問之事主星：{qs_cn} {PLANET_GLYPHS.get(quesited, '')}",
        f"",
        f"判斷結果：{verdict_cn}",
        f"完成方式：{method}",
        f"",
    ]
    if factors:
        lines.append("關鍵因素：")
        lines.extend(f"  {f}" for f in factors)
        lines.append("")
    if warnings:
        lines.append("注意事項與障礙：")
        lines.extend(f"  {w}" for w in warnings)
        lines.append("")
    lines.append(f"時機：{timing_cn}")
    return "\n".join(lines)


# ============================================================
# Main Western Horary Computation Entry Point
# ============================================================

def compute_western_horary(
    year: int, month: int, day: int,
    hour: int, minute: int, timezone: float,
    latitude: float, longitude: float,
    location_name: str = "",
    question_text: str = "",
    question_type: str = "general",
) -> WesternHoraryChart:
    """
    Compute a complete Western Horary chart in the Lilly/Bonatti tradition.

    Args:
        year, month, day, hour, minute: Local time of question
        timezone: UTC offset
        latitude, longitude: Geographic coordinates of question
        location_name: Human-readable place name
        question_text: The question being asked
        question_type: One of the QUESTION_TYPES keys

    Returns:
        WesternHoraryChart with all computed data and judgment

    Source: Lilly "Christian Astrology" Part I & II; Bonatti "Liber Astronomiae"
    """
    swe.set_ephe_path("")

    jd = _julian_day(year, month, day, hour, minute, timezone)

    # Compute house cusps (Regiomontanus — Lilly's preferred system)
    # Source: Lilly CA p. 29
    cusps, ascmc = swe.houses(jd, latitude, longitude, b"R")
    ascendant = _normalize(ascmc[0])
    midheaven = _normalize(ascmc[1])

    asc_sign_idx = _sign_index(ascendant)
    asc_sign = ZODIAC_SIGNS[asc_sign_idx][0]
    asc_sign_cn = ZODIAC_SIGNS[asc_sign_idx][2]
    asc_degree = _sign_degree(ascendant)
    asc_lord = DOMICILE_RULERS[asc_sign_idx]

    # Compute planet positions
    sun_lon = 0.0
    raw_planets: Dict[str, Dict] = {}
    for pname in TRADITIONAL_PLANETS:
        pid = PLANET_IDS[pname]
        res, _ = swe.calc_ut(jd, pid)
        raw_planets[pname] = {
            "lon": _normalize(res[0]),
            "lat": res[1],
            "speed": res[3],
        }
    sun_lon = raw_planets["Sun"]["lon"]

    # Build HoraryPlanet objects
    planets: List[HoraryPlanet] = []
    for pname in TRADITIONAL_PLANETS:
        d = raw_planets[pname]
        lon = d["lon"]
        speed = d["speed"]
        sign_idx = _sign_index(lon)
        sign_info = ZODIAC_SIGNS[sign_idx]
        house = _find_house(lon, cusps)

        dignity, ess_score = _get_essential_dignity(pname, lon)
        combust = _get_combust_status(pname, lon, sun_lon)

        # Accidental score
        acc_score = 0
        h_type = HOUSE_TIMING.get(house, "Cadent")
        if h_type == "Angular":
            acc_score += ACCIDENTAL_DIGNITY_SCORES["angular"]
        elif h_type == "Succedent":
            acc_score += ACCIDENTAL_DIGNITY_SCORES["succedent"]
        else:
            acc_score += ACCIDENTAL_DIGNITY_SCORES["cadent"]

        if speed < 0:
            acc_score += ACCIDENTAL_DIGNITY_SCORES["retrograde"]
        else:
            acc_score += ACCIDENTAL_DIGNITY_SCORES["direct"]

        mean_spd = MEAN_MOTION.get(pname, 1.0)
        is_fast = abs(speed) > mean_spd
        if is_fast:
            acc_score += ACCIDENTAL_DIGNITY_SCORES["fast"]
        else:
            acc_score += ACCIDENTAL_DIGNITY_SCORES["slow"]

        if combust == "cazimi":
            acc_score += ACCIDENTAL_DIGNITY_SCORES["cazimi"]
        elif combust == "combust":
            acc_score += ACCIDENTAL_DIGNITY_SCORES["combust"]
        elif combust == "under_sunbeams":
            acc_score += ACCIDENTAL_DIGNITY_SCORES["under_sunbeams"]
        else:
            acc_score += ACCIDENTAL_DIGNITY_SCORES["free_from_combustion"]

        joy_house = PLANETARY_JOYS.get(pname, 0)
        in_joy = (house == joy_house)
        if in_joy:
            acc_score += ACCIDENTAL_DIGNITY_SCORES["joy_house"]

        is_oriental_val = _is_oriental(pname, lon, sun_lon)
        in_via = _is_in_via_combusta(lon) and pname == "Moon"

        planets.append(HoraryPlanet(
            name=pname,
            glyph=PLANET_GLYPHS[pname],
            name_cn=PLANET_CN[pname],
            longitude=lon,
            sign=sign_info[0],
            sign_cn=sign_info[2],
            sign_glyph=sign_info[1],
            sign_index=sign_idx,
            degree_in_sign=_sign_degree(lon),
            house=house,
            retrograde=speed < 0,
            speed=speed,
            essential_dignity=dignity,
            essential_score=ess_score,
            combust_status=combust,
            accidental_score=acc_score,
            total_strength=ess_score + acc_score,
            is_fast=is_fast,
            is_oriental=is_oriental_val,
            in_joy=in_joy,
            in_via_combusta=in_via,
            formatted_pos=f"{int(_sign_degree(lon))}°{int((_sign_degree(lon) % 1)*60):02d}' {sign_info[0]}",
        ))

    # Aspects
    aspects = _compute_aspects(planets)

    # VOC Moon
    moon_planet = next(p for p in planets if p.name == "Moon")
    moon_voc = _compute_voc_moon(moon_planet.longitude, moon_planet.speed, planets)

    # Strictures
    strictures = _check_strictures(ascendant, planets, moon_voc)

    # Planetary hour lord (radicality)
    # Strict Lilly definition: radical when hour lord == ASC lord (Lilly CA p.121).
    # Extended check: Bonatti (Consideration 1) also allows Moon's sign lord as
    # a secondary indicator of the querent's sincerity.
    try:
        ph_lord = _compute_planetary_hour_lord(jd, latitude, longitude)
    except Exception:
        ph_lord = asc_lord
    is_radical = (ph_lord == asc_lord) or (ph_lord == DOMICILE_RULERS.get(_sign_index(moon_planet.longitude)))

    # Quesited significator
    qt = QUESTION_TYPES.get(question_type, QUESTION_TYPES["general"])
    q_house_idx = qt["primary_house"] - 1
    house_cusp_sign_idx = _sign_index(cusps[q_house_idx])
    quesited = DOMICILE_RULERS.get(house_cusp_sign_idx, "Moon")

    # Translation and Collection of Light
    translations = _compute_translation_of_light(asc_lord, quesited, planets, aspects)
    collections = _compute_collection_of_light(asc_lord, quesited, planets, aspects)

    # Judgment
    judgment = _judge_western_horary(
        question_type, question_text, asc_lord, planets, aspects,
        moon_voc, strictures, translations, collections
    )

    # House signs list
    house_cusps_list = list(cusps[:12])
    house_signs = [ZODIAC_SIGNS[_sign_index(c)][0] for c in house_cusps_list]

    dt_str = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} (UTC{timezone:+.1f})"

    return WesternHoraryChart(
        question_datetime=dt_str,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        question_text=question_text,
        question_type=question_type,
        julian_day=jd,
        ascendant=ascendant,
        midheaven=midheaven,
        asc_sign=asc_sign,
        asc_sign_cn=asc_sign_cn,
        asc_degree=asc_degree,
        asc_lord=asc_lord,
        planets=planets,
        house_cusps=house_cusps_list,
        house_signs=house_signs,
        aspects=aspects,
        moon_voc=moon_voc,
        moon_in_via_combusta=moon_planet.in_via_combusta,
        strictures=strictures,
        translations_of_light=translations,
        collections_of_light=collections,
        planetary_hour_lord=ph_lord,
        is_radical=is_radical,
        judgment=judgment,
    )


# ============================================================
# Vedic Prashna Computation
# ============================================================

def _vedic_dignity(planet: str, sign_idx: int) -> str:
    """Return Vedic dignity status."""
    if sign_idx in VEDIC_OWN_SIGNS.get(planet, []):
        return "own_sign"
    if VEDIC_EXALTATION.get(planet) == sign_idx:
        return "exalted"
    if VEDIC_DEBILITATION.get(planet) == sign_idx:
        return "debilitated"
    return "neutral"


def _compute_arudha_lagna(asc_lon: float, cusps: Tuple[float, ...],
                           lagna_lord: str, planet_data: Dict[str, float]) -> ArudhaLagna:
    """
    Compute Arudha Lagna (external image / manifestation).

    Method: Count from Lagna to the Lagna Lord's rashi.
    Then count the same number of signs from the Lagna Lord's rashi.
    If result = Lagna or 7th from Lagna, move to 10th from that position.
    Source: Prasna Marga Chapter 4, v. 15-16; Jaimini Sutras 1.3
    """
    asc_sign_idx = _sign_index(asc_lon)
    lord_lon = planet_data.get(lagna_lord, asc_lon)
    lord_sign_idx = _sign_index(lord_lon)

    # Count from Lagna to Lord's sign (1-based)
    count = (lord_sign_idx - asc_sign_idx) % 12 + 1

    # Count same from Lord's sign
    arudha_idx = (lord_sign_idx + count - 1) % 12

    # Special rule: if Arudha = Lagna or 7th from Lagna
    seventh_from_lagna = (asc_sign_idx + 6) % 12
    if arudha_idx == asc_sign_idx or arudha_idx == seventh_from_lagna:
        # Move to 10th from the computed position
        arudha_idx = (arudha_idx + 9) % 12

    arudha_lon = arudha_idx * 30.0 + 15.0  # midpoint of sign
    sign_info = VEDIC_RASHIS[arudha_idx]

    return ArudhaLagna(
        sign_index=arudha_idx,
        sign=sign_info[0],
        sign_cn=sign_info[2],
        longitude=arudha_lon,
        description_en=(
            f"Arudha Lagna falls in {sign_info[0]} (sign {arudha_idx + 1}). "
            f"This is the 'external image' of the querent's situation — "
            f"how the matter appears to the outside world. "
            f"(Prasna Marga Ch. 4, v. 15-16)"
        ),
        description_cn=(
            f"阿魯達命宮（Arudha Lagna）落於{sign_info[2]}（第{arudha_idx + 1}宮）。"
            f"此為問卜者處境的「外在形象」，代表事情在外界的顯現方式。"
            f"（《Prasna Marga》第四章第15-16節）"
        ),
    )


def _compute_prashna_numerology(number: int) -> Optional[VedicPrashnaNumerology]:
    """
    Compute number-based Prashna Lagna from a querent-given number (1-108).

    Method: Divide number by 12; remainder gives the rashi.
    Number 1-12 → Mesha-Meena; then cycles repeat 9 times (108 total).
    Source: Prasna Marga Ch. 2, v. 1-5
    """
    if not (1 <= number <= 108):
        return None

    rashi_idx = (number - 1) % 12
    navamsa_cycle = (number - 1) // 12 + 1  # 1-9
    sign_info = VEDIC_RASHIS[rashi_idx]

    return VedicPrashnaNumerology(
        number=number,
        rashi_index=rashi_idx,
        rashi=sign_info[0],
        navamsa_pada=navamsa_cycle,
        description_en=(
            f"Number {number} → {sign_info[0]} (Navamsa cycle {navamsa_cycle}). "
            f"This determines the Prashna Lagna when no birth data is available. "
            f"(Prasna Marga Ch. 2, v. 1-5)"
        ),
        description_cn=(
            f"數字{number} → {sign_info[2]}（那瓦曼薩周期{navamsa_cycle}）。"
            f"此法在無出生資料時確定問卜命宮。"
            f"（《Prasna Marga》第二章第1-5節）"
        ),
    )


def _judge_vedic_prashna(
    question_type: str,
    question_text: str,
    asc_lord: str,
    planets: List[VedicPlanetPos],
    arudha: ArudhaLagna,
) -> VedicPrashnaJudgment:
    """
    Generate a traditional Vedic Prashna judgment.
    Source: Prasna Marga various chapters
    """
    planet_dict = {p.name: p for p in planets}
    moon = planet_dict.get("Moon")
    lagna_lord_planet = planet_dict.get(asc_lord)

    # Assess Lagna Lord
    lagna_lord_status = "unknown"
    if lagna_lord_planet:
        if lagna_lord_planet.dignity in ("exalted", "own_sign"):
            lagna_lord_status = "strong"
        elif lagna_lord_planet.dignity == "debilitated":
            lagna_lord_status = "weak"
        else:
            lagna_lord_status = "moderate"

    # Assess Moon
    moon_status = "unknown"
    if moon:
        if moon.dignity in ("exalted", "own_sign"):
            moon_status = "strong"
        elif moon.dignity == "debilitated":
            moon_status = "weak"
        else:
            moon_status = "moderate"

    # Question-specific logic
    qt = PRASHNA_QUESTION_TYPES.get(question_type, PRASHNA_QUESTION_TYPES["general"])
    primary_house = qt["primary_house"]
    karaka = qt.get("karaka", "Moon")
    pm_ref = qt["pm_ref"]

    key_yogas: List[str] = []
    key_factors_en: List[str] = []
    key_factors_cn: List[str] = []
    verdict = "unclear"
    verdict_cn = "不明"

    # Basic positive/negative indicators
    positive = 0
    negative = 0

    if lagna_lord_status == "strong":
        positive += 2
        key_factors_en.append(f"✅ Lagna Lord ({asc_lord}) is strong ({lagna_lord_planet.dignity if lagna_lord_planet else ''})")
        key_factors_cn.append(f"✅ 命宮主星（{asc_lord}）強旺（{lagna_lord_planet.dignity if lagna_lord_planet else ''}）")
    elif lagna_lord_status == "weak":
        negative += 2
        key_factors_en.append(f"⚠️ Lagna Lord ({asc_lord}) is weak ({lagna_lord_planet.dignity if lagna_lord_planet else ''})")
        key_factors_cn.append(f"⚠️ 命宮主星（{asc_lord}）虛弱（{lagna_lord_planet.dignity if lagna_lord_planet else ''}）")

    if moon_status == "strong":
        positive += 1
        key_factors_en.append(f"✅ Moon (Chandra) is strong ({moon.dignity if moon else ''})")
        key_factors_cn.append(f"✅ 月亮（Chandra）強旺（{moon.dignity if moon else ''}）")
    elif moon_status == "weak":
        negative += 1
        key_factors_en.append(f"⚠️ Moon (Chandra) is weak ({moon.dignity if moon else ''})")
        key_factors_cn.append(f"⚠️ 月亮（Chandra）虛弱（{moon.dignity if moon else ''}）")

    # Karaka for question type
    karaka_planet = planet_dict.get(karaka)
    if karaka_planet:
        if karaka_planet.dignity in ("exalted", "own_sign"):
            positive += 1
            key_factors_en.append(f"✅ Question Karaka ({karaka}) is strong")
            key_factors_cn.append(f"✅ 問題業力星（{karaka}）強旺")
        elif karaka_planet.dignity == "debilitated":
            negative += 1
            key_factors_en.append(f"⚠️ Question Karaka ({karaka}) is debilitated")
            key_factors_cn.append(f"⚠️ 問題業力星（{karaka}）衰弱入落")

    # Arudha Lagna assessment
    key_factors_en.append(
        f"🔮 Arudha Lagna: {arudha.sign} — {arudha.description_en[:80]}..."
    )
    key_factors_cn.append(
        f"🔮 阿魯達命宮：{arudha.sign_cn} — {arudha.description_cn[:50]}…"
    )

    # Determine verdict
    if positive > negative + 1:
        verdict = "yes"
        verdict_cn = "是（吉）"
    elif negative > positive + 1:
        verdict = "no"
        verdict_cn = "否（凶）"
    else:
        verdict = "mixed"
        verdict_cn = "吉凶參半"

    # Timing
    if moon:
        modality = SIGN_MODALITY.get(moon.sign, "Mutable")
        t_info = TIMING_UNIT.get(modality, {})
        timing_en = t_info.get("en", "Timing unclear")
        timing_cn = t_info.get("cn", "時機不明")
    else:
        timing_en = "Timing unclear"
        timing_cn = "時機不明"

    # Full judgment
    full_en = _compose_vedic_judgment_en(
        question_text, question_type, asc_lord, arudha,
        verdict, key_factors_en, key_yogas, timing_en, pm_ref
    )
    full_cn = _compose_vedic_judgment_cn(
        question_text, question_type, asc_lord, arudha,
        verdict_cn, key_factors_cn, key_yogas, timing_cn, pm_ref
    )

    return VedicPrashnaJudgment(
        question=question_text,
        question_type=question_type,
        lagna_lord=asc_lord,
        lagna_lord_status=lagna_lord_status,
        moon_status=moon_status,
        verdict=verdict,
        verdict_cn=verdict_cn,
        key_yogas=key_yogas,
        key_factors_en=key_factors_en,
        key_factors_cn=key_factors_cn,
        timing_hint=timing_en,
        timing_hint_cn=timing_cn,
        full_judgment_en=full_en,
        full_judgment_cn=full_cn,
    )


def _compose_vedic_judgment_en(question, q_type, lagna_lord, arudha,
                                verdict, factors, yogas, timing, pm_ref) -> str:
    qt = PRASHNA_QUESTION_TYPES.get(q_type, {})
    lines = [
        f"═══ VEDIC PRASHNA JUDGMENT (Prasna Marga Tradition) ═══",
        f"Question: {question}",
        f"Type: {qt.get('en', q_type)} — {pm_ref}",
        f"",
        f"Prasna Lagna Lord: {lagna_lord}",
        f"Arudha Lagna: {arudha.sign}",
        f"",
        f"VERDICT: {verdict.upper().replace('_', ' ')}",
        f"",
    ]
    if factors:
        lines.append("Key Indicators:")
        lines.extend(f"  {f}" for f in factors)
        lines.append("")
    if yogas:
        lines.append("Special Yogas:")
        lines.extend(f"  {y}" for y in yogas)
        lines.append("")
    lines.append(f"Timing: {timing}")
    return "\n".join(lines)


def _compose_vedic_judgment_cn(question, q_type, lagna_lord, arudha,
                                verdict_cn, factors_cn, yogas, timing_cn, pm_ref) -> str:
    qt = PRASHNA_QUESTION_TYPES.get(q_type, {})
    lines = [
        f"═══ 吠陀問卦判斷（Prasna Marga 傳統）═══",
        f"問題：{question}",
        f"類型：{qt.get('cn', q_type)} — {pm_ref}",
        f"",
        f"問卦命宮主星：{lagna_lord}",
        f"阿魯達命宮：{arudha.sign_cn}",
        f"",
        f"判斷結果：{verdict_cn}",
        f"",
    ]
    if factors_cn:
        lines.append("關鍵指標：")
        lines.extend(f"  {f}" for f in factors_cn)
        lines.append("")
    if yogas:
        lines.append("特殊組合（Yoga）：")
        lines.extend(f"  {y}" for y in yogas)
        lines.append("")
    lines.append(f"時機：{timing_cn}")
    return "\n".join(lines)


def compute_vedic_prashna(
    year: int, month: int, day: int,
    hour: int, minute: int, timezone: float,
    latitude: float, longitude: float,
    location_name: str = "",
    question_text: str = "",
    question_type: str = "general",
    prashna_number: Optional[int] = None,
) -> VedicPrashnaChart:
    """
    Compute a complete Vedic Prashna chart (Prasna Marga tradition).

    Args:
        year/month/day/hour/minute: Local time of question
        timezone: UTC offset
        latitude, longitude: Geographic coordinates
        question_text: The question
        question_type: One of PRASHNA_QUESTION_TYPES keys
        prashna_number: Optional 1-108 number given by querent (traditional method)

    Returns:
        VedicPrashnaChart with full computation and judgment

    Source: Prasna Marga (Kerala Jyotish Prashna text);
            Arudha Lagna also described in Jaimini Sutras 1.3
    """
    swe.set_ephe_path("")
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    jd = _julian_day(year, month, day, hour, minute, timezone)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Sidereal houses (Placidus)
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"P", swe.FLG_SIDEREAL)
    ascendant = _normalize(ascmc[0])

    asc_sign_idx = _sign_index(ascendant)
    asc_sign_info = VEDIC_RASHIS[asc_sign_idx]
    asc_lord = asc_sign_info[3]

    # If prashna_number is given, override Lagna
    numerology = None
    if prashna_number and 1 <= prashna_number <= 108:
        numerology = _compute_prashna_numerology(prashna_number)
        # Override Lagna with number-based calculation
        asc_sign_idx = numerology.rashi_index
        asc_sign_info = VEDIC_RASHIS[asc_sign_idx]
        asc_lord = asc_sign_info[3]

    # Traditional planets + Rahu/Ketu
    planet_lons: Dict[str, float] = {}
    planets_list: List[VedicPlanetPos] = []

    vedic_planet_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
    }

    for pname, pid in vedic_planet_map.items():
        res, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        lon = _normalize(res[0])
        speed = res[3]
        sign_idx = _sign_index(lon)
        sign_info = VEDIC_RASHIS[sign_idx]
        house = _find_house(lon, cusps)
        dignity = _vedic_dignity(pname, sign_idx)
        planet_lons[pname] = lon

        from .constants import VEDIC_PLANET_NAMES
        planets_list.append(VedicPlanetPos(
            name=pname,
            name_vedic=VEDIC_PLANET_NAMES.get(pname, pname),
            longitude=lon,
            sign=sign_info[0],
            sign_cn=sign_info[2],
            sign_lord=sign_info[3],
            sign_index=sign_idx,
            degree_in_sign=_sign_degree(lon),
            house=house,
            retrograde=speed < 0,
            speed=speed,
            dignity=dignity,
            formatted_pos=f"{int(_sign_degree(lon))}°{int((_sign_degree(lon) % 1)*60):02d}' {sign_info[0]}",
        ))

    # Rahu (Mean Node)
    rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _normalize(rahu_res[0])
    planet_lons["Rahu"] = rahu_lon
    rahu_sign_idx = _sign_index(rahu_lon)
    rahu_sign = VEDIC_RASHIS[rahu_sign_idx]
    planets_list.append(VedicPlanetPos(
        name="Rahu", name_vedic="Rahu (羅睺)",
        longitude=rahu_lon, sign=rahu_sign[0], sign_cn=rahu_sign[2],
        sign_lord=rahu_sign[3], sign_index=rahu_sign_idx,
        degree_in_sign=_sign_degree(rahu_lon),
        house=_find_house(rahu_lon, cusps),
        retrograde=True, speed=rahu_res[3],
        dignity="neutral",
        formatted_pos=f"{int(_sign_degree(rahu_lon))}°{int((_sign_degree(rahu_lon) % 1)*60):02d}' {rahu_sign[0]}",
    ))

    # Ketu (South Node)
    ketu_lon = _normalize(rahu_lon + 180.0)
    planet_lons["Ketu"] = ketu_lon
    ketu_sign_idx = _sign_index(ketu_lon)
    ketu_sign = VEDIC_RASHIS[ketu_sign_idx]
    planets_list.append(VedicPlanetPos(
        name="Ketu", name_vedic="Ketu (計都)",
        longitude=ketu_lon, sign=ketu_sign[0], sign_cn=ketu_sign[2],
        sign_lord=ketu_sign[3], sign_index=ketu_sign_idx,
        degree_in_sign=_sign_degree(ketu_lon),
        house=_find_house(ketu_lon, cusps),
        retrograde=True, speed=-rahu_res[3],
        dignity="neutral",
        formatted_pos=f"{int(_sign_degree(ketu_lon))}°{int((_sign_degree(ketu_lon) % 1)*60):02d}' {ketu_sign[0]}",
    ))

    # Arudha Lagna
    arudha = _compute_arudha_lagna(ascendant, cusps, asc_lord, planet_lons)

    # Judgment
    judgment = _judge_vedic_prashna(
        question_type, question_text, asc_lord, planets_list, arudha
    )

    house_cusps_list = list(cusps[:12])
    house_signs = [VEDIC_RASHIS[_sign_index(c)][0] for c in house_cusps_list]
    dt_str = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} (UTC{timezone:+.1f})"

    asc_lon_final = ascendant if not numerology else (asc_sign_idx * 30.0 + 15.0)

    return VedicPrashnaChart(
        question_datetime=dt_str,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        question_text=question_text,
        question_type=question_type,
        julian_day=jd,
        ayanamsa=ayanamsa,
        ascendant=ascendant,
        asc_sign=asc_sign_info[0],
        asc_sign_cn=asc_sign_info[2],
        asc_degree=_sign_degree(ascendant),
        asc_lord=asc_lord,
        planets=planets_list,
        house_cusps=house_cusps_list,
        house_signs=house_signs,
        arudha_lagna=arudha,
        numerology=numerology,
        judgment=judgment,
    )


# ============================================================
# Unified Entry Point
# ============================================================

def compute_horary_chart(
    year: int, month: int, day: int,
    hour: int, minute: int, timezone: float,
    latitude: float, longitude: float,
    location_name: str = "",
    question_text: str = "",
    question_type: str = "general",
    tradition: str = "western",
    prashna_number: Optional[int] = None,
) -> Any:
    """
    Unified entry point for horary computation.

    Args:
        tradition: "western" (Lilly/Bonatti) or "vedic" (Prashna Marga)
        prashna_number: Optional 1-108 number for Vedic tradition

    Returns:
        WesternHoraryChart or VedicPrashnaChart depending on tradition
    """
    if tradition == "vedic":
        return compute_vedic_prashna(
            year, month, day, hour, minute, timezone,
            latitude, longitude, location_name,
            question_text, question_type, prashna_number
        )
    else:
        return compute_western_horary(
            year, month, day, hour, minute, timezone,
            latitude, longitude, location_name,
            question_text, question_type
        )


# ============================================================
# Test Cases
# ============================================================

def _test_case_1_western():
    """
    Classic Lilly horary: 'Will I sell my house?' (fictional example).
    Location: London (~51.5°N, 0.1°W), 2024-03-21 14:30 UTC+0.
    """
    return compute_western_horary(
        year=2024, month=3, day=21, hour=14, minute=30, timezone=0.0,
        latitude=51.509, longitude=-0.118,
        location_name="London, UK",
        question_text="Will I sell my house?",
        question_type="property",
    )


def _test_case_2_western():
    """
    Marriage query: 'Will I marry this person?' (fictional example).
    Location: New York (~40.7°N, 74.0°W), 2024-06-15 10:00 UTC-5.
    """
    return compute_western_horary(
        year=2024, month=6, day=15, hour=10, minute=0, timezone=-5.0,
        latitude=40.714, longitude=-74.006,
        location_name="New York, USA",
        question_text="Will I marry this person?",
        question_type="marriage",
    )


def _test_case_3_vedic():
    """
    Vedic Prashna: 'Will my business succeed?' (fictional example).
    Location: Mumbai (~18.9°N, 72.8°E), 2024-01-10 09:15 UTC+5.5.
    """
    return compute_vedic_prashna(
        year=2024, month=1, day=10, hour=9, minute=15, timezone=5.5,
        latitude=18.975, longitude=72.826,
        location_name="Mumbai, India",
        question_text="Will my business succeed?",
        question_type="career",
        prashna_number=42,
    )
