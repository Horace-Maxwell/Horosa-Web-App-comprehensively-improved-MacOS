"""
astro/electional/calculator.py — Electional Astrology & Vedic Muhurta Computation Engine

Implements both Western Electional (Lilly / Bonatti / Al-Biruni) and Vedic Muhurta
(Muhurta Chintamani / Kalaprakashika / BPHS) election systems.

Western Electional sources:
  - William Lilly, "Christian Astrology" (1647) [CA]
  - Guido Bonatti, "Liber Astronomiae" (~1277) [LA]
  - Al-Biruni, "Book of Instruction in the Elements of the Art of Astrology" [BI]

Vedic Muhurta sources:
  - Muhurta Chintamani [MC]
  - Kalaprakashika [KP]
  - Brihat Parashara Hora Shastra [BPHS]
  - Muhurta Martanda [MM]
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import swisseph as swe

from .constants import (
    TRADITIONAL_PLANETS, PLANET_IDS, PLANET_GLYPHS, PLANET_CN, PLANET_NATURE,
    ZODIAC_SIGNS, SIGN_NAMES, DOMICILE_RULERS, DETRIMENT_RULERS,
    EXALTATION, FALL_SIGN, DIGNITY_SCORES, MEAN_MOTION,
    CHALDEAN_ORDER, WEEKDAY_RULERS,
    CAZIMI_ORB, COMBUSTION_ORB, VIA_COMBUSTA_START, VIA_COMBUSTA_END,
    ASPECT_DEFINITIONS,
    WESTERN_ACTIVITY_TYPES, HOUSE_SIGNIFICATIONS, SCORE_WEIGHTS,
    SCORE_EXCELLENT, SCORE_GOOD, SCORE_NEUTRAL, SCORE_POOR,
    NAKSHATRAS, TITHIS, VARA_NAMES, YOGAS, KARANAS,
    NAKSHATRA_GOOD_FOR, NAKSHATRA_AVOID_FOR,
    TITHI_GOOD_FOR, TITHI_AVOID_FOR,
    VARA_GOOD_FOR, VARA_AVOID_FOR,
    INAUSPICIOUS_YOGAS, VISHTI_KARANA_NAME,
    VEDIC_RASHIS, VEDIC_EXALTATION, VEDIC_DEBILITATION,
    VEDIC_PLANETS, VEDIC_PLANET_IDS, VEDIC_PLANET_CN,
    LAGNA_GOOD_FOR, LAGNA_AVOID_FOR,
    GANDANTA_RANGES, LAHIRI_AYANAMSA,
    VEDIC_ACTIVITY_TYPES,
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


def _jd_to_local_datetime(jd: float, timezone: float) -> datetime:
    """Convert Julian Day Number (UT) back to local datetime."""
    # swe.revjul returns (year, month, day, hour_decimal)
    y, m, d, h = swe.revjul(jd)
    h_local = h + timezone
    # Handle day overflow
    extra_days = int(h_local // 24)
    h_local = h_local % 24
    hour = int(h_local)
    minute = int((h_local - hour) * 60)
    from datetime import date
    base = date(int(y), int(m), int(d)) + timedelta(days=extra_days)
    return datetime(base.year, base.month, base.day, hour, minute)


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


def _format_sign_pos(lon: float) -> str:
    """Format ecliptic longitude as 'DD°MM' SignName'."""
    idx = _sign_index(lon)
    sign = ZODIAC_SIGNS[idx][0]
    d = _sign_degree(lon)
    return f"{int(d)}°{int((d % 1)*60):02d}' {sign}"


def _get_essential_dignity(planet: str, lon: float) -> Tuple[str, int]:
    """
    Return (dignity_name, score) for a planet at a given longitude.
    Source: Lilly CA pp. 101-116.
    """
    sign_idx = _sign_index(lon)
    deg_in_sign = _sign_degree(lon)
    element = ZODIAC_SIGNS[sign_idx][3]

    if DOMICILE_RULERS.get(sign_idx) == planet:
        return ("domicile", DIGNITY_SCORES["domicile"])
    if DETRIMENT_RULERS.get(sign_idx) == planet:
        return ("detriment", DIGNITY_SCORES["detriment"])
    if planet in EXALTATION:
        ex_sign, _ = EXALTATION[planet]
        if sign_idx == ex_sign:
            return ("exaltation", DIGNITY_SCORES["exaltation"])
    if planet in FALL_SIGN and FALL_SIGN[planet] == sign_idx:
        return ("fall", DIGNITY_SCORES["fall"])
    return ("peregrine", DIGNITY_SCORES["peregrine"])


def _is_retrograde(speed: float) -> bool:
    return speed < 0.0


def _is_combusted(planet: str, planet_lon: float, sun_lon: float) -> bool:
    if planet == "Sun":
        return False
    return _angular_distance(planet_lon, sun_lon) <= COMBUSTION_ORB


def _is_in_via_combusta(lon: float) -> bool:
    lon = _normalize(lon)
    return VIA_COMBUSTA_START <= lon <= VIA_COMBUSTA_END


def _compute_sunrise_sunset(jd: float, lat: float, lon: float) -> Tuple[float, float]:
    """
    Compute sunrise and sunset Julian Days for a given JD and location.
    Returns (sunrise_jd, sunset_jd).
    """
    swe.set_ephe_path("")
    # swe.rise_trans returns (retflag, tret) where tret is a tuple of event times
    try:
        retval, tret = swe.rise_trans(jd - 0.5, swe.SUN, "", swe.CALC_RISE | swe.BIT_DISC_CENTER,
                                      [lon, lat, 0.0], 1013.25, 10.0)
        sunrise = tret[0]
        retval2, tret2 = swe.rise_trans(jd - 0.5, swe.SUN, "", swe.CALC_SET | swe.BIT_DISC_CENTER,
                                        [lon, lat, 0.0], 1013.25, 10.0)
        sunset = tret2[0]
    except Exception:
        # Fallback: approximate sunrise as 6:00 local, sunset as 18:00 local
        sunrise = jd - (jd % 1) + 0.0   # rough approximate
        sunset = sunrise + 0.5
    return sunrise, sunset


def _get_planetary_hour(jd: float, lat: float, lon: float, timezone: float) -> Tuple[str, int]:
    """
    Compute the planetary hour lord for a given Julian Day.

    The day is divided into 12 day-hours (sunrise to sunset) and 12 night-hours
    (sunset to next sunrise). The first hour of the day belongs to the day ruler.
    Subsequent hours follow the Chaldean order.

    Source: Lilly CA p. 483; Al-Biruni BI §330.

    Returns: (planet_name, hour_number_1_to_24)
    """
    swe.set_ephe_path("")
    sunrise, sunset = _compute_sunrise_sunset(jd, lat, lon)

    # Get next sunrise
    try:
        _, tret3 = swe.rise_trans(jd + 0.3, swe.SUN, "", swe.CALC_RISE | swe.BIT_DISC_CENTER,
                                   [lon, lat, 0.0], 1013.25, 10.0)
        next_sunrise = tret3[0]
    except Exception:
        next_sunrise = sunrise + 1.0

    # Day ruler: weekday of sunrise
    # JD 0 = Monday (Jan 1, 4713 BC)
    # Use the local date to determine weekday
    local_dt = _jd_to_local_datetime(sunrise, timezone)
    weekday = local_dt.weekday()  # 0=Mon, 6=Sun
    # Convert to Python weekday to our convention (0=Sun … 6=Sat)
    # Python: 0=Mon … 6=Sun → our: 0=Sun … 6=Sat
    day_ruler_idx = (weekday + 1) % 7  # 0=Sun in our convention
    day_ruler = WEEKDAY_RULERS[day_ruler_idx]

    # Chaldean position of day ruler
    chaldean_pos = CHALDEAN_ORDER.index(day_ruler)

    # Day hours: sunrise to sunset
    day_duration = sunset - sunrise
    night_duration = next_sunrise - sunset
    day_hour_len = day_duration / 12.0
    night_hour_len = night_duration / 12.0

    if sunrise <= jd < sunset:
        hour_num_0 = int((jd - sunrise) / day_hour_len)
        hour_num_0 = min(hour_num_0, 11)
        hour_number = hour_num_0 + 1
        planet_idx = (chaldean_pos + hour_num_0) % 7
    else:
        # Night hour
        if jd >= sunset:
            hour_num_0 = int((jd - sunset) / night_hour_len)
        else:
            hour_num_0 = int((jd - (next_sunrise - night_duration)) / night_hour_len)
        hour_num_0 = min(hour_num_0, 11)
        hour_number = hour_num_0 + 13
        planet_idx = (chaldean_pos + 12 + hour_num_0) % 7

    planet_lord = CHALDEAN_ORDER[planet_idx]
    return planet_lord, hour_number


def _is_voc_moon(moon_lon: float, moon_speed: float,
                  planets: List["ElectionalPlanet"]) -> Tuple[bool, str]:
    """
    Check if the Moon is Void of Course.

    The Moon is VOC when it makes no more applying aspects to any traditional
    planet before it leaves its current sign.
    Source: Lilly CA p. 122.

    Returns: (is_voc: bool, description: str)
    """
    sign_idx = _sign_index(moon_lon)
    deg_in_sign = _sign_degree(moon_lon)
    degrees_to_end = 30.0 - deg_in_sign
    # Estimate time to leave sign (days)
    time_to_end = degrees_to_end / abs(moon_speed) if moon_speed != 0 else 9999.0

    for planet in planets:
        if planet.name == "Moon":
            continue
        for asp_def in ASPECT_DEFINITIONS:
            target_angle = asp_def["angle"]
            orb = asp_def["orb"]
            diff = abs(_normalize(moon_lon - planet.longitude))
            if diff > 180.0:
                diff = 360.0 - diff
            actual_orb = abs(diff - target_angle)
            if actual_orb > orb:
                continue
            # Check if applying
            dt = 0.01
            moon_fut = moon_lon + moon_speed * dt
            planet_fut = planet.longitude + planet.speed * dt
            diff_now = abs(_normalize(moon_lon - planet.longitude))
            if diff_now > 180.0:
                diff_now = 360.0 - diff_now
            diff_fut = abs(_normalize(moon_fut - planet_fut))
            if diff_fut > 180.0:
                diff_fut = 360.0 - diff_fut
            orb_now = abs(diff_now - target_angle)
            orb_fut = abs(diff_fut - target_angle)
            if orb_fut < orb_now:
                # Applying aspect found — not VOC
                return (False, f"Moon applying {asp_def['en']} to {planet.name}")

    return (True, f"Moon Void of Course in {ZODIAC_SIGNS[sign_idx][0]} — no more aspects before sign change")


# ============================================================
# Data Classes
# ============================================================

@dataclass
class ElectionalPlanet:
    """Planet position and state for an electional chart."""
    name: str
    glyph: str
    name_cn: str
    longitude: float
    sign: str
    sign_cn: str
    sign_index: int
    degree_in_sign: float
    house: int
    retrograde: bool
    speed: float
    essential_dignity: str    # domicile/exaltation/peregrine/detriment/fall
    essential_score: int
    combust: bool
    formatted_pos: str
    nature: str               # benefic/malefic/neutral


@dataclass
class WesternElectionalFactor:
    """A single Western electional factor (good or bad)."""
    factor_key: str
    description_en: str
    description_cn: str
    score: float
    is_positive: bool
    source_ref: str = ""     # e.g. "Lilly CA p. 122"


@dataclass
class WesternElectionalResult:
    """Result of Western Electional analysis for a single datetime."""
    # Time
    datetime_local: datetime
    julian_day: float
    latitude: float
    longitude: float
    location_name: str
    activity_type: str
    timezone: float

    # Chart basics
    ascendant: float
    asc_sign: str
    asc_sign_cn: str
    asc_lord: str
    house_cusps: List[float]
    planets: List[ElectionalPlanet]

    # Moon state
    moon_is_voc: bool
    moon_voc_desc: str
    moon_in_via_combusta: bool
    moon_phase: str          # "waxing" / "waning"
    moon_phase_cn: str
    moon_applies_to: str     # planet Moon applies to (if any)

    # Planetary hour
    planetary_hour_lord: str
    planetary_hour_number: int
    planetary_hour_suitable: bool

    # Key factors
    factors: List[WesternElectionalFactor]
    total_score: float
    quality: str             # "Excellent" / "Good" / "Neutral" / "Poor" / "Avoid"
    quality_cn: str
    quality_stars: str       # "★★★★★" etc.

    # Recommendations
    summary_en: str
    summary_cn: str


@dataclass
class PanchangaElement:
    """A single element of the Vedic Panchanga."""
    name: str
    value: str
    value_cn: str
    nature: str              # benefic/malefic/mixed
    score: float
    notes_en: str
    notes_cn: str


@dataclass
class VedicMuhurtaFactor:
    """A single Vedic Muhurta factor."""
    factor_key: str
    description_en: str
    description_cn: str
    score: float
    is_positive: bool
    source_ref: str = ""


@dataclass
class VedicMuhurtaResult:
    """Result of Vedic Muhurta analysis for a single datetime."""
    # Time
    datetime_local: datetime
    julian_day: float
    latitude: float
    longitude: float
    location_name: str
    activity_type: str
    timezone: float

    # Sidereal chart
    ayanamsa: float
    lagna_sidereal: float
    lagna_rashi: str
    lagna_rashi_cn: str
    lagna_rashi_index: int

    # Moon sidereal
    moon_sidereal: float
    moon_rashi: str
    moon_rashi_cn: str

    # Panchanga
    panchanga: Dict[str, PanchangaElement]

    # Gandanta
    is_gandanta: bool
    gandanta_note: str

    # Jupiter/Venus combustion
    jupiter_combust: bool
    venus_combust: bool

    # Factors
    factors: List[VedicMuhurtaFactor]
    total_score: float
    quality: str
    quality_cn: str
    quality_stars: str

    # Summary
    summary_en: str
    summary_cn: str


# ============================================================
# Western Electional Computation
# ============================================================

def _compute_chart_basics(jd: float, lat: float, lon: float
                           ) -> Tuple[List[ElectionalPlanet], float, List[float]]:
    """
    Compute planets and house cusps (Placidus) for a given JD and location.
    Returns (planets, ascendant, house_cusps).
    """
    swe.set_ephe_path("")

    # House cusps
    cusps, ascmc = swe.houses(jd, lat, lon, b"P")
    asc = ascmc[0]
    house_cusps = list(cusps)

    # Planets
    planet_list: List[ElectionalPlanet] = []
    sun_lon = 0.0
    for pname in TRADITIONAL_PLANETS:
        pid = PLANET_IDS[pname]
        res, _ = swe.calc_ut(jd, pid)
        plon = _normalize(res[0])
        speed = res[3]
        if pname == "Sun":
            sun_lon = plon
        sign_idx = _sign_index(plon)
        sign_info = ZODIAC_SIGNS[sign_idx]
        retro = _is_retrograde(speed)
        dignity, dscore = _get_essential_dignity(pname, plon)
        combust = _is_combusted(pname, plon, sun_lon)
        house = _find_house(plon, tuple(house_cusps))
        planet_list.append(ElectionalPlanet(
            name=pname,
            glyph=PLANET_GLYPHS[pname],
            name_cn=PLANET_CN[pname],
            longitude=plon,
            sign=sign_info[0],
            sign_cn=sign_info[2],
            sign_index=sign_idx,
            degree_in_sign=_sign_degree(plon),
            house=house,
            retrograde=retro,
            speed=speed,
            essential_dignity=dignity,
            essential_score=dscore,
            combust=combust,
            formatted_pos=_format_sign_pos(plon),
            nature=PLANET_NATURE.get(pname, "neutral"),
        ))

    return planet_list, asc, house_cusps


def _score_western_election(
    jd: float,
    planets: List[ElectionalPlanet],
    asc: float,
    house_cusps: List[float],
    activity_type: str,
    timezone: float,
    lat: float,
    lon: float,
) -> Tuple[List[WesternElectionalFactor], float]:
    """
    Score a Western electional chart against rules for the given activity.
    Returns (factors, total_score).

    Sources: Lilly CA pp. 383-536; Bonatti LA Tractatus VI.
    """
    factors: List[WesternElectionalFactor] = []
    score: float = 0.0

    activity = WESTERN_ACTIVITY_TYPES.get(activity_type, WESTERN_ACTIVITY_TYPES["important_meeting"])
    planet_dict = {p.name: p for p in planets}
    moon = planet_dict.get("Moon")
    mercury = planet_dict.get("Mercury")

    # ── 1. Moon Void of Course ───────────────────────────────────
    if moon:
        is_voc, voc_desc = _is_voc_moon(moon.longitude, moon.speed, planets)
        if is_voc:
            s = SCORE_WEIGHTS["moon_voc"]
            factors.append(WesternElectionalFactor(
                factor_key="moon_voc",
                description_en=f"Moon is Void of Course — {voc_desc}",
                description_cn=f"月亮虛空（Void of Course）— {voc_desc}",
                score=s,
                is_positive=False,
                source_ref="Lilly CA p. 122",
            ))
            score += s

    # ── 2. Moon in Via Combusta ──────────────────────────────────
    if moon and _is_in_via_combusta(moon.longitude):
        s = SCORE_WEIGHTS["moon_via_combusta"]
        factors.append(WesternElectionalFactor(
            factor_key="moon_via_combusta",
            description_en="Moon in Via Combusta (15° Libra – 15° Scorpio) — weakened",
            description_cn="月亮在焦途（Via Combusta，天秤15°至天蠍15°）— 力量削弱",
            score=s,
            is_positive=False,
            source_ref="Lilly CA p. 123",
        ))
        score += s

    # ── 3. Moon Phase ────────────────────────────────────────────
    if moon:
        sun = planet_dict.get("Sun")
        if sun:
            diff = _arc_diff(moon.longitude, sun.longitude)
            if diff > 0:
                s = SCORE_WEIGHTS["moon_waxing"]
                factors.append(WesternElectionalFactor(
                    factor_key="moon_waxing",
                    description_en="Moon waxing (increasing in light) — favourable",
                    description_cn="月亮漸盈（增光）— 有利",
                    score=s,
                    is_positive=True,
                    source_ref="Lilly CA p. 113",
                ))
                score += s
            else:
                s = SCORE_WEIGHTS["moon_waning"]
                factors.append(WesternElectionalFactor(
                    factor_key="moon_waning",
                    description_en="Moon waning (decreasing in light) — slightly unfavourable",
                    description_cn="月亮漸虧（減光）— 略為不利",
                    score=s,
                    is_positive=False,
                    source_ref="Lilly CA p. 113",
                ))
                score += s

    # ── 4. Moon applies to benefic/malefic ──────────────────────
    if moon:
        for asp_def in ASPECT_DEFINITIONS:
            for planet in planets:
                if planet.name == "Moon":
                    continue
                diff = abs(_normalize(moon.longitude - planet.longitude))
                if diff > 180.0:
                    diff = 360.0 - diff
                actual_orb = abs(diff - asp_def["angle"])
                if actual_orb > asp_def["orb"]:
                    continue
                dt = 0.01
                moon_fut = moon.longitude + moon.speed * dt
                planet_fut = planet.longitude + planet.speed * dt
                diff_fut = abs(_normalize(moon_fut - planet_fut))
                if diff_fut > 180.0:
                    diff_fut = 360.0 - diff_fut
                orb_fut = abs(diff_fut - asp_def["angle"])
                if orb_fut >= actual_orb:
                    continue  # separating
                if planet.nature == "benefic" and asp_def["nature"] in ("benefic", "neutral"):
                    s = SCORE_WEIGHTS["moon_applies_benefic"]
                    factors.append(WesternElectionalFactor(
                        factor_key="moon_applies_benefic",
                        description_en=f"Moon applying {asp_def['en']} to {planet.name} (benefic) — auspicious",
                        description_cn=f"月亮入相{asp_def['cn']}{PLANET_CN[planet.name]}（吉星）— 吉利",
                        score=s,
                        is_positive=True,
                        source_ref="Lilly CA p. 109",
                    ))
                    score += s
                elif planet.nature == "malefic":
                    s = SCORE_WEIGHTS["moon_applies_malefic"]
                    factors.append(WesternElectionalFactor(
                        factor_key="moon_applies_malefic",
                        description_en=f"Moon applying {asp_def['en']} to {planet.name} (malefic) — inauspicious",
                        description_cn=f"月亮入相{asp_def['cn']}{PLANET_CN[planet.name]}（凶星）— 不吉",
                        score=s,
                        is_positive=False,
                        source_ref="Lilly CA p. 109",
                    ))
                    score += s

    # ── 5. Key house placement ───────────────────────────────────
    key_houses = activity.get("key_houses", [1, 7])
    key_planets = activity.get("key_planets", [])
    avoid_planets = activity.get("avoid_planets", [])

    for planet in planets:
        if planet.house in key_houses:
            if planet.name in avoid_planets:
                s = SCORE_WEIGHTS["malefic_in_key_house"]
                factors.append(WesternElectionalFactor(
                    factor_key="malefic_in_key_house",
                    description_en=f"{planet.name} in House {planet.house} (key house) — afflicts this area",
                    description_cn=f"{PLANET_CN[planet.name]}在第{planet.house}宮（關鍵宮位）— 帶來不利影響",
                    score=s,
                    is_positive=False,
                    source_ref=activity.get("lilly_ref", "Lilly CA"),
                ))
                score += s
            elif planet.name in key_planets:
                s = SCORE_WEIGHTS["benefic_in_key_house"]
                factors.append(WesternElectionalFactor(
                    factor_key="benefic_in_key_house",
                    description_en=f"{planet.name} in House {planet.house} (key house) — strengthens this area",
                    description_cn=f"{PLANET_CN[planet.name]}在第{planet.house}宮（關鍵宮位）— 強化此領域",
                    score=s,
                    is_positive=True,
                    source_ref=activity.get("lilly_ref", "Lilly CA"),
                ))
                score += s

    # ── 6. Planet Dignity ────────────────────────────────────────
    for planet in planets:
        if planet.name in key_planets:
            if planet.essential_dignity in ("domicile", "exaltation"):
                s = SCORE_WEIGHTS["planet_dignified"]
                factors.append(WesternElectionalFactor(
                    factor_key="planet_dignified",
                    description_en=f"{planet.name} in {planet.essential_dignity} — essential strength",
                    description_cn=f"{PLANET_CN[planet.name]}在{planet.essential_dignity}（本質尊貴）— 強健",
                    score=s,
                    is_positive=True,
                    source_ref="Lilly CA p. 101",
                ))
                score += s
            elif planet.essential_dignity in ("detriment", "fall"):
                s = SCORE_WEIGHTS["planet_debilitated"]
                factors.append(WesternElectionalFactor(
                    factor_key="planet_debilitated",
                    description_en=f"{planet.name} in {planet.essential_dignity} — essential weakness",
                    description_cn=f"{PLANET_CN[planet.name]}在{planet.essential_dignity}（本質受損）— 羸弱",
                    score=s,
                    is_positive=False,
                    source_ref="Lilly CA p. 101",
                ))
                score += s

    # ── 7. Retrograde Mercury for signing / communication ────────
    if activity_type in ("contract_signing", "important_meeting", "business_opening"):
        if mercury and mercury.retrograde:
            s = SCORE_WEIGHTS["retrograde_mercury"]
            factors.append(WesternElectionalFactor(
                factor_key="retrograde_mercury",
                description_en="Mercury retrograde — avoid signing contracts or starting negotiations",
                description_cn="水星逆行 — 避免簽約或開始談判",
                score=s,
                is_positive=False,
                source_ref="Lilly CA p. 114; Al-Biruni BI §455",
            ))
            score += s

    # ── 8. Planetary Hour ────────────────────────────────────────
    hour_lord, hour_num = _get_planetary_hour(jd, lat, lon, timezone)
    if hour_lord in key_planets:
        s = SCORE_WEIGHTS["good_planetary_hour"]
        factors.append(WesternElectionalFactor(
            factor_key="good_planetary_hour",
            description_en=f"Planetary Hour of {hour_lord} (Hour {hour_num}) — supportive for this activity",
            description_cn=f"行星時：{PLANET_CN.get(hour_lord, hour_lord)}（第{hour_num}時）— 有利此活動",
            score=s,
            is_positive=True,
            source_ref="Lilly CA p. 483; Al-Biruni BI §330",
        ))
        score += s
    elif hour_lord in avoid_planets:
        s = SCORE_WEIGHTS["bad_planetary_hour"]
        factors.append(WesternElectionalFactor(
            factor_key="bad_planetary_hour",
            description_en=f"Planetary Hour of {hour_lord} (Hour {hour_num}) — unfavourable for this activity",
            description_cn=f"行星時：{PLANET_CN.get(hour_lord, hour_lord)}（第{hour_num}時）— 不利此活動",
            score=s,
            is_positive=False,
            source_ref="Lilly CA p. 483; Al-Biruni BI §330",
        ))
        score += s

    return factors, score


def compute_western_electional(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    activity_type: str = "important_meeting",
    location_name: str = "",
) -> WesternElectionalResult:
    """
    Compute a Western Traditional Electional chart for a specific date/time.

    Source: Lilly CA pp. 383-536; Bonatti LA Tractatus VI.

    Args:
        year, month, day, hour, minute: Local date and time.
        timezone: UTC offset in hours (e.g. 8.0 for UTC+8).
        latitude, longitude: Location in decimal degrees.
        activity_type: One of the keys in WESTERN_ACTIVITY_TYPES.
        location_name: Optional display name for the location.

    Returns:
        WesternElectionalResult with full analysis.
    """
    swe.set_ephe_path("")
    jd = _julian_day(year, month, day, hour, minute, timezone)
    planets, asc, house_cusps = _compute_chart_basics(jd, latitude, longitude)

    planet_dict = {p.name: p for p in planets}
    moon = planet_dict.get("Moon")
    sun = planet_dict.get("Sun")

    asc_sign_idx = _sign_index(asc)
    asc_sign = ZODIAC_SIGNS[asc_sign_idx][0]
    asc_sign_cn = ZODIAC_SIGNS[asc_sign_idx][2]
    asc_lord = DOMICILE_RULERS.get(asc_sign_idx, "Saturn")

    # Moon VOC
    moon_is_voc = False
    moon_voc_desc = ""
    if moon:
        moon_is_voc, moon_voc_desc = _is_voc_moon(moon.longitude, moon.speed, planets)

    # Moon Via Combusta
    moon_via_combusta = moon is not None and _is_in_via_combusta(moon.longitude)

    # Moon phase
    moon_phase = "waxing"
    moon_phase_cn = "漸盈"
    if moon and sun:
        diff = _arc_diff(moon.longitude, sun.longitude)
        if diff < 0:
            moon_phase = "waning"
            moon_phase_cn = "漸虧"

    # Moon applies to
    moon_applies_to = ""
    if moon:
        for asp_def in ASPECT_DEFINITIONS:
            for planet in planets:
                if planet.name == "Moon":
                    continue
                diff = abs(_normalize(moon.longitude - planet.longitude))
                if diff > 180.0:
                    diff = 360.0 - diff
                actual_orb = abs(diff - asp_def["angle"])
                if actual_orb > asp_def["orb"]:
                    continue
                dt = 0.01
                moon_fut = moon.longitude + moon.speed * dt
                planet_fut = planet.longitude + planet.speed * dt
                diff_fut = abs(_normalize(moon_fut - planet_fut))
                if diff_fut > 180.0:
                    diff_fut = 360.0 - diff_fut
                orb_fut = abs(diff_fut - asp_def["angle"])
                if orb_fut < actual_orb:
                    moon_applies_to = f"{asp_def['en']} {planet.name}"
                    break
            if moon_applies_to:
                break

    # Planetary hour
    hour_lord, hour_num = _get_planetary_hour(jd, latitude, longitude, timezone)
    activity = WESTERN_ACTIVITY_TYPES.get(activity_type, WESTERN_ACTIVITY_TYPES["important_meeting"])
    key_planets = activity.get("key_planets", [])
    avoid_planets = activity.get("avoid_planets", [])
    suitable_hour = hour_lord in key_planets

    # Score
    factors, total_score = _score_western_election(
        jd, planets, asc, house_cusps, activity_type, timezone, latitude, longitude
    )

    # Quality
    if total_score >= SCORE_EXCELLENT:
        quality, quality_cn, stars = "Excellent", "極佳", "★★★★★"
    elif total_score >= SCORE_GOOD:
        quality, quality_cn, stars = "Good", "良好", "★★★★☆"
    elif total_score >= SCORE_NEUTRAL:
        quality, quality_cn, stars = "Neutral", "中性", "★★★☆☆"
    elif total_score >= SCORE_POOR:
        quality, quality_cn, stars = "Poor", "不佳", "★★☆☆☆"
    else:
        quality, quality_cn, stars = "Avoid", "應迴避", "★☆☆☆☆"

    # Summary
    positives = [f.description_en for f in factors if f.is_positive]
    negatives = [f.description_en for f in factors if not f.is_positive]
    positives_cn = [f.description_cn for f in factors if f.is_positive]
    negatives_cn = [f.description_cn for f in factors if not f.is_positive]

    summary_en = (
        f"Western Electional Analysis for {activity.get('en', activity_type)} — "
        f"Score: {total_score:+.0f} ({quality})\n"
    )
    if positives:
        summary_en += "Favourable factors: " + "; ".join(positives[:3]) + "\n"
    if negatives:
        summary_en += "Adverse factors: " + "; ".join(negatives[:3])

    summary_cn = (
        f"西方傳統擇日分析：{activity.get('cn', activity_type)} — "
        f"評分：{total_score:+.0f}（{quality_cn}）\n"
    )
    if positives_cn:
        summary_cn += "有利因素：" + "；".join(positives_cn[:3]) + "\n"
    if negatives_cn:
        summary_cn += "不利因素：" + "；".join(negatives_cn[:3])

    local_dt = datetime(year, month, day, hour, minute)

    return WesternElectionalResult(
        datetime_local=local_dt,
        julian_day=jd,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        activity_type=activity_type,
        timezone=timezone,
        ascendant=asc,
        asc_sign=asc_sign,
        asc_sign_cn=asc_sign_cn,
        asc_lord=asc_lord,
        house_cusps=house_cusps,
        planets=planets,
        moon_is_voc=moon_is_voc,
        moon_voc_desc=moon_voc_desc,
        moon_in_via_combusta=moon_via_combusta,
        moon_phase=moon_phase,
        moon_phase_cn=moon_phase_cn,
        moon_applies_to=moon_applies_to,
        planetary_hour_lord=hour_lord,
        planetary_hour_number=hour_num,
        planetary_hour_suitable=suitable_hour,
        factors=factors,
        total_score=total_score,
        quality=quality,
        quality_cn=quality_cn,
        quality_stars=stars,
        summary_en=summary_en,
        summary_cn=summary_cn,
    )


# ============================================================
# Western Electional: Find Best Windows
# ============================================================

def find_western_elections(
    start_year: int, start_month: int, start_day: int,
    end_year: int, end_month: int, end_day: int,
    timezone: float,
    latitude: float,
    longitude: float,
    activity_type: str = "important_meeting",
    location_name: str = "",
    step_hours: float = 1.0,
    min_score: float = 15.0,
    max_results: int = 10,
) -> List[WesternElectionalResult]:
    """
    Search for auspicious time windows in a date range for Western Electional.

    Scans every ``step_hours`` hours and returns results above ``min_score``,
    sorted by score descending, up to ``max_results``.

    Source: Lilly CA pp. 383-536.
    """
    swe.set_ephe_path("")
    results: List[WesternElectionalResult] = []

    start_jd = _julian_day(start_year, start_month, start_day, 6, 0, timezone)
    end_jd = _julian_day(end_year, end_month, end_day, 22, 0, timezone)

    jd = start_jd
    while jd <= end_jd:
        local_dt = _jd_to_local_datetime(jd, timezone)
        try:
            result = compute_western_electional(
                year=local_dt.year, month=local_dt.month, day=local_dt.day,
                hour=local_dt.hour, minute=local_dt.minute,
                timezone=timezone, latitude=latitude, longitude=longitude,
                activity_type=activity_type, location_name=location_name,
            )
            if result.total_score >= min_score:
                results.append(result)
        except Exception:
            pass
        jd += step_hours / 24.0

    # Sort by score descending
    results.sort(key=lambda r: r.total_score, reverse=True)
    return results[:max_results]


# ============================================================
# Vedic Muhurta Computation
# ============================================================

def _compute_sidereal_lagna(jd: float, lat: float, lon: float) -> Tuple[float, float]:
    """
    Compute sidereal Lagna (Ascendant) and ayanamsa using Lahiri ayanamsa.
    Returns (sidereal_asc, ayanamsa).
    """
    swe.set_ephe_path("")
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    cusps, ascmc = swe.houses(jd, lat, lon, b"P")
    tropical_asc = ascmc[0]
    sidereal_asc = _normalize(tropical_asc - ayanamsa)
    return sidereal_asc, ayanamsa


def _compute_sidereal_moon(jd: float) -> Tuple[float, float]:
    """
    Compute sidereal Moon position and speed.
    Returns (sidereal_lon, speed).
    """
    swe.set_ephe_path("")
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    res, _ = swe.calc_ut(jd, swe.MOON)
    tropical_moon = _normalize(res[0])
    sidereal_moon = _normalize(tropical_moon - ayanamsa)
    speed = res[3]
    return sidereal_moon, speed


def _compute_panchanga(jd: float) -> Dict[str, Any]:
    """
    Compute all five Panchanga elements for a given Julian Day.

    The Panchanga consists of:
      1. Tithi   — Lunar day (Moon - Sun elongation / 12°)
      2. Vara    — Weekday (day of week, with its planetary ruler)
      3. Nakshatra — Lunar mansion (Moon's sidereal position / 13°20')
      4. Yoga    — Sum of Sun + Moon sidereal positions / 13°20'
      5. Karana  — Half Tithi

    Source: Muhurta Chintamani Ch. 1-5; Kalaprakashika.

    Returns a dict with keys: tithi, vara, nakshatra, yoga, karana.
    """
    swe.set_ephe_path("")
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Sun sidereal
    sun_res, _ = swe.calc_ut(jd, swe.SUN)
    sun_sid = _normalize(sun_res[0] - ayanamsa)

    # Moon sidereal
    moon_res, _ = swe.calc_ut(jd, swe.MOON)
    moon_sid = _normalize(moon_res[0] - ayanamsa)
    moon_speed = moon_res[3]

    # ── Tithi ────────────────────────────────────────────────────
    # Each Tithi spans 12° of Moon-Sun elongation
    elongation = _normalize(moon_sid - sun_sid)
    tithi_num = int(elongation / 12.0) + 1  # 1-30
    tithi_num = min(tithi_num, 30)
    tithi_data = TITHIS[tithi_num - 1]
    tithi_deg_rem = elongation % 12.0  # degrees remaining in current Tithi

    # ── Vara ─────────────────────────────────────────────────────
    # Use Julian Day to get weekday (JD 0.5 = Mon, so JD % 7 gives weekday)
    weekday = int((jd + 1.5)) % 7  # 0=Sun, 1=Mon, ... 6=Sat
    vara_data = VARA_NAMES[weekday]

    # ── Nakshatra ────────────────────────────────────────────────
    # Each Nakshatra spans 360/27 = 13.333...°
    nakshatra_span = 360.0 / 27.0
    nakshatra_idx = int(moon_sid / nakshatra_span)  # 0-26
    nakshatra_idx = min(nakshatra_idx, 26)
    nakshatra_data = NAKSHATRAS[nakshatra_idx]
    nakshatra_deg_rem = moon_sid % nakshatra_span

    # ── Yoga ─────────────────────────────────────────────────────
    # Yoga = (Sun + Moon sidereal) / 13.333...°
    yoga_sum = _normalize(sun_sid + moon_sid)
    yoga_idx = int(yoga_sum / nakshatra_span)  # 0-26
    yoga_idx = min(yoga_idx, 26)
    yoga_data = YOGAS[yoga_idx]

    # ── Karana ───────────────────────────────────────────────────
    # Karana = half Tithi. First Tithi has Kimstughna (fixed) in first half,
    # Bava in second half. Then the 7 movable Karanas repeat.
    # Each Tithi has 2 Karanas.
    # For simplicity: karana_num within month (1-60)
    karana_in_month = int(elongation / 6.0) + 1  # 1-60
    # Fixed karanas occupy specific positions:
    # Karana 1 (first half of Tithi 1): Kimstughna
    # Karanas 2-57: cycle of 7 movable
    # Karana 58: Shakuni, 59: Chatushpada, 60: Naga
    FIXED_KARANA_MAP = {1: 11, 58: 8, 59: 9, 60: 10}  # maps position to KARANAS num (1-based)
    if karana_in_month in FIXED_KARANA_MAP:
        karana_data = KARANAS[FIXED_KARANA_MAP[karana_in_month] - 1]
    else:
        movable_idx = ((karana_in_month - 2) % 7)  # 0-6
        karana_data = KARANAS[movable_idx]

    return {
        "tithi": {"data": tithi_data, "num": tithi_num, "deg_rem": tithi_deg_rem},
        "vara": {"data": vara_data, "weekday": weekday},
        "nakshatra": {"data": nakshatra_data, "idx": nakshatra_idx, "deg_rem": nakshatra_deg_rem},
        "yoga": {"data": yoga_data, "idx": yoga_idx},
        "karana": {"data": karana_data},
        "sun_sid": sun_sid,
        "moon_sid": moon_sid,
        "moon_speed": moon_speed,
    }


def _score_vedic_muhurta(
    panchanga: Dict[str, Any],
    lagna_idx: int,
    activity_type: str,
    jd: float,
) -> Tuple[List[VedicMuhurtaFactor], float]:
    """
    Score a Vedic Muhurta chart based on Panchanga and Lagna.
    Returns (factors, total_score).

    Sources: Muhurta Chintamani; Kalaprakashika; BPHS Ch. 95-97.
    """
    factors: List[VedicMuhurtaFactor] = []
    score: float = 0.0

    tithi_num = panchanga["tithi"]["num"]
    vara_weekday = panchanga["vara"]["weekday"]
    nakshatra_idx = panchanga["nakshatra"]["idx"]
    nakshatra_num = nakshatra_idx + 1  # 1-27
    yoga_idx = panchanga["yoga"]["idx"]
    yoga_num = yoga_idx + 1  # 1-27
    karana_data = panchanga["karana"]["data"]

    good_tithis = TITHI_GOOD_FOR.get(activity_type, [])
    bad_tithis = TITHI_AVOID_FOR.get(activity_type, [])
    good_varas = VARA_GOOD_FOR.get(activity_type, [])
    bad_varas = VARA_AVOID_FOR.get(activity_type, [])
    good_nakshatras = NAKSHATRA_GOOD_FOR.get(activity_type, [])
    bad_nakshatras = NAKSHATRA_AVOID_FOR.get(activity_type, [])

    # ── Tithi ────────────────────────────────────────────────────
    tithi_data = panchanga["tithi"]["data"]
    if tithi_num in good_tithis:
        s = SCORE_WEIGHTS["good_tithi"]
        factors.append(VedicMuhurtaFactor(
            factor_key="good_tithi",
            description_en=f"Tithi {tithi_data['name']} (#{tithi_num}) is auspicious for {activity_type}",
            description_cn=f"第{tithi_num}日（{tithi_data['name']}）對此活動吉祥",
            score=s, is_positive=True,
            source_ref="Muhurta Chintamani Ch. 3",
        ))
        score += s
    elif tithi_num in bad_tithis:
        s = SCORE_WEIGHTS["bad_tithi"]
        factors.append(VedicMuhurtaFactor(
            factor_key="bad_tithi",
            description_en=f"Tithi {tithi_data['name']} (#{tithi_num}) is inauspicious for {activity_type}",
            description_cn=f"第{tithi_num}日（{tithi_data['name']}）對此活動不吉",
            score=s, is_positive=False,
            source_ref="Muhurta Chintamani Ch. 3",
        ))
        score += s

    # ── Vara ─────────────────────────────────────────────────────
    vara_data = panchanga["vara"]["data"]
    if vara_weekday in good_varas:
        s = SCORE_WEIGHTS["good_vara"]
        factors.append(VedicMuhurtaFactor(
            factor_key="good_vara",
            description_en=f"Vara: {vara_data['name']} (ruled by {vara_data['planet']}) — auspicious",
            description_cn=f"日曜：{vara_data['cn']}（{VEDIC_PLANET_CN.get(vara_data['planet'], vara_data['planet'])}主宰）— 吉祥",
            score=s, is_positive=True,
            source_ref="Muhurta Chintamani Ch. 1",
        ))
        score += s
    elif vara_weekday in bad_varas:
        s = SCORE_WEIGHTS["bad_vara"]
        factors.append(VedicMuhurtaFactor(
            factor_key="bad_vara",
            description_en=f"Vara: {vara_data['name']} (ruled by {vara_data['planet']}) — inauspicious",
            description_cn=f"日曜：{vara_data['cn']}（{VEDIC_PLANET_CN.get(vara_data['planet'], vara_data['planet'])}主宰）— 不吉",
            score=s, is_positive=False,
            source_ref="Muhurta Chintamani Ch. 1",
        ))
        score += s

    # ── Nakshatra ────────────────────────────────────────────────
    nak_data = panchanga["nakshatra"]["data"]
    if nakshatra_num in good_nakshatras:
        s = SCORE_WEIGHTS["good_nakshatra"]
        factors.append(VedicMuhurtaFactor(
            factor_key="good_nakshatra",
            description_en=f"Nakshatra: {nak_data['name']} (#{nakshatra_num}) — auspicious for {activity_type}",
            description_cn=f"那舍特拉：{nak_data['name']}（第{nakshatra_num}宿）— 對此活動吉祥",
            score=s, is_positive=True,
            source_ref="Muhurta Chintamani Ch. 2",
        ))
        score += s
    elif nakshatra_num in bad_nakshatras:
        s = SCORE_WEIGHTS["bad_nakshatra"]
        factors.append(VedicMuhurtaFactor(
            factor_key="bad_nakshatra",
            description_en=f"Nakshatra: {nak_data['name']} (#{nakshatra_num}) — inauspicious for {activity_type}",
            description_cn=f"那舍特拉：{nak_data['name']}（第{nakshatra_num}宿）— 對此活動不吉",
            score=s, is_positive=False,
            source_ref="Muhurta Chintamani Ch. 2",
        ))
        score += s

    # ── Yoga ─────────────────────────────────────────────────────
    yoga_data = panchanga["yoga"]["data"]
    if yoga_num in INAUSPICIOUS_YOGAS:
        s = SCORE_WEIGHTS["bad_yoga"]
        factors.append(VedicMuhurtaFactor(
            factor_key="bad_yoga",
            description_en=f"Yoga: {yoga_data['name']} (#{yoga_num}) — inauspicious yoga, avoid for important activities",
            description_cn=f"瑜伽：{yoga_data['cn']}（第{yoga_num}瑜伽）— 不吉瑜伽，重要活動應避免",
            score=s, is_positive=False,
            source_ref="Muhurta Chintamani Ch. 4",
        ))
        score += s

    # ── Karana ───────────────────────────────────────────────────
    if karana_data["name"] == VISHTI_KARANA_NAME:
        s = SCORE_WEIGHTS["vishti_karana"]
        factors.append(VedicMuhurtaFactor(
            factor_key="vishti_karana",
            description_en="Karana: Vishti (Bhadra) — the most malefic Karana, avoid ALL auspicious activities",
            description_cn="卡拉那：毘濕提（Vishti/Bhadra）— 最凶惡的半日，應避免所有吉祥活動",
            score=s, is_positive=False,
            source_ref="Muhurta Chintamani Ch. 5; Kalaprakashika",
        ))
        score += s

    # ── Lagna ────────────────────────────────────────────────────
    good_lagnas = LAGNA_GOOD_FOR.get(activity_type, [])
    bad_lagnas = LAGNA_AVOID_FOR.get(activity_type, [])
    if lagna_idx in good_lagnas:
        s = SCORE_WEIGHTS["good_lagna"]
        rashi = VEDIC_RASHIS[lagna_idx]
        factors.append(VedicMuhurtaFactor(
            factor_key="good_lagna",
            description_en=f"Lagna in {rashi['name']} — auspicious rising sign for {activity_type}",
            description_cn=f"命宮在{rashi['cn']} — 對此活動的吉祥上升星座",
            score=s, is_positive=True,
            source_ref="Muhurta Chintamani; Kalaprakashika",
        ))
        score += s
    elif lagna_idx in bad_lagnas:
        s = SCORE_WEIGHTS["bad_lagna"]
        rashi = VEDIC_RASHIS[lagna_idx]
        factors.append(VedicMuhurtaFactor(
            factor_key="bad_lagna",
            description_en=f"Lagna in {rashi['name']} — inauspicious rising sign for {activity_type}",
            description_cn=f"命宮在{rashi['cn']} — 對此活動不吉的上升星座",
            score=s, is_positive=False,
            source_ref="Muhurta Chintamani; Kalaprakashika",
        ))
        score += s

    return factors, score


def compute_vedic_muhurta(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    activity_type: str = "important_meeting",
    location_name: str = "",
) -> VedicMuhurtaResult:
    """
    Compute a Vedic Muhurta analysis for a specific date/time.

    Calculates the Panchanga (5 limbs), Lagna (sidereal ascendant),
    and scores the time based on traditional Muhurta rules.

    Source: Muhurta Chintamani; Kalaprakashika; BPHS Ch. 95-97.

    Args:
        year, month, day, hour, minute: Local date and time.
        timezone: UTC offset in hours.
        latitude, longitude: Location in decimal degrees.
        activity_type: One of the keys in VEDIC_ACTIVITY_TYPES.
        location_name: Optional display name for the location.

    Returns:
        VedicMuhurtaResult with Panchanga and full analysis.
    """
    swe.set_ephe_path("")
    jd = _julian_day(year, month, day, hour, minute, timezone)

    # Sidereal Lagna
    lagna_sid, ayanamsa = _compute_sidereal_lagna(jd, latitude, longitude)
    lagna_idx = _sign_index(lagna_sid)
    lagna_rashi = VEDIC_RASHIS[lagna_idx]

    # Sidereal Moon
    moon_sid, moon_speed = _compute_sidereal_moon(jd)
    moon_rashi_idx = _sign_index(moon_sid)
    moon_rashi = VEDIC_RASHIS[moon_rashi_idx]

    # Panchanga
    panch_raw = _compute_panchanga(jd)

    # Gandanta check (Moon in Gandanta)
    is_gandanta = any(
        lo <= moon_sid < hi
        for lo, hi in GANDANTA_RANGES
    )
    gandanta_note = ""
    if is_gandanta:
        gandanta_note = (
            "Moon is in Gandanta (junction of water and fire signs) — "
            "inauspicious for new beginnings. Source: BPHS Ch. 95."
        )

    # Jupiter and Venus combustion
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    sun_res, _ = swe.calc_ut(jd, swe.SUN)
    jup_res, _ = swe.calc_ut(jd, swe.JUPITER)
    ven_res, _ = swe.calc_ut(jd, swe.VENUS)
    sun_lon = _normalize(sun_res[0])
    jup_combust = _angular_distance(_normalize(jup_res[0]), sun_lon) < 11.0
    ven_combust = _angular_distance(_normalize(ven_res[0]), sun_lon) < 10.0

    if activity_type == "marriage":
        if jup_combust:
            gandanta_note += (
                "\nJupiter is combust — not ideal for Vivaha Muhurta; "
                "guru (Jupiter) should be visible. Source: Muhurta Chintamani Ch. 7."
            )
        if ven_combust:
            gandanta_note += (
                "\nVenus is combust — not ideal for marriage; "
                "Shukra should be visible. Source: Muhurta Chintamani Ch. 7."
            )

    # Build Panchanga elements
    tithi_data = panch_raw["tithi"]["data"]
    vara_data = panch_raw["vara"]["data"]
    nak_data = panch_raw["nakshatra"]["data"]
    yoga_data = panch_raw["yoga"]["data"]
    karana_data = panch_raw["karana"]["data"]

    panchanga: Dict[str, PanchangaElement] = {
        "tithi": PanchangaElement(
            name="Tithi",
            value=f"{tithi_data['name']} (#{panch_raw['tithi']['num']})",
            value_cn=f"{tithi_data['cn']}（第{panch_raw['tithi']['num']}日）",
            nature=tithi_data["nature"],
            score=SCORE_WEIGHTS["good_tithi"] if panch_raw["tithi"]["num"] in TITHI_GOOD_FOR.get(activity_type, []) else
                  SCORE_WEIGHTS["bad_tithi"] if panch_raw["tithi"]["num"] in TITHI_AVOID_FOR.get(activity_type, []) else 0.0,
            notes_en=f"Paksha: {'Shukla (waxing)' if tithi_data['paksha'] == 'shukla' else 'Krishna (waning)'}",
            notes_cn=f"月相：{'白分（漸盈）' if tithi_data['paksha'] == 'shukla' else '黑分（漸虧）'}",
        ),
        "vara": PanchangaElement(
            name="Vara",
            value=f"{vara_data['name']} ({vara_data['planet']})",
            value_cn=vara_data["cn"],
            nature=vara_data["nature"],
            score=0.0,
            notes_en=f"Weekday ruled by {vara_data['planet']}",
            notes_cn=f"由{VEDIC_PLANET_CN.get(vara_data['planet'], vara_data['planet'])}主宰的星期",
        ),
        "nakshatra": PanchangaElement(
            name="Nakshatra",
            value=f"{nak_data['name']} (#{panch_raw['nakshatra']['idx']+1})",
            value_cn=f"{nak_data['cn']}（第{panch_raw['nakshatra']['idx']+1}宿）",
            nature=nak_data["nature"],
            score=0.0,
            notes_en=f"Ruler: {nak_data['ruler']}; Nature: {nak_data['nature']}",
            notes_cn=f"主宰星：{VEDIC_PLANET_CN.get(nak_data['ruler'], nak_data['ruler'])}；性質：{nak_data['nature']}",
        ),
        "yoga": PanchangaElement(
            name="Yoga",
            value=f"{yoga_data['name']} (#{panch_raw['yoga']['idx']+1})",
            value_cn=f"{yoga_data['cn']}（第{panch_raw['yoga']['idx']+1}瑜伽）",
            nature=yoga_data["nature"],
            score=SCORE_WEIGHTS["bad_yoga"] if panch_raw["yoga"]["idx"]+1 in INAUSPICIOUS_YOGAS else 0.0,
            notes_en=f"Sun+Moon combination; nature: {yoga_data['nature']}",
            notes_cn=f"太陽+月亮組合；性質：{yoga_data['nature']}",
        ),
        "karana": PanchangaElement(
            name="Karana",
            value=karana_data["name"],
            value_cn=karana_data["cn"],
            nature=karana_data["nature"],
            score=SCORE_WEIGHTS["vishti_karana"] if karana_data["name"] == VISHTI_KARANA_NAME else 0.0,
            notes_en=f"Half-Tithi; nature: {karana_data['nature']}; movable: {karana_data['movable']}",
            notes_cn=f"半日；性質：{karana_data['nature']}；可動：{karana_data['movable']}",
        ),
    }

    # Score
    factors, total_score = _score_vedic_muhurta(panch_raw, lagna_idx, activity_type, jd)

    if is_gandanta:
        total_score += SCORE_WEIGHTS["gandanta"]
        factors.append(VedicMuhurtaFactor(
            factor_key="gandanta",
            description_en="Moon in Gandanta — inauspicious junction point",
            description_cn="月亮在甘達塔（水象與火象星座交界）— 不吉的交界點",
            score=SCORE_WEIGHTS["gandanta"],
            is_positive=False,
            source_ref="BPHS Ch. 95",
        ))

    if activity_type == "marriage":
        if not jup_combust:
            total_score += SCORE_WEIGHTS["jupiter_visible"]
            factors.append(VedicMuhurtaFactor(
                factor_key="jupiter_visible",
                description_en="Jupiter is visible (not combust) — favourable for Vivaha",
                description_cn="木星可見（未被燃燒）— 對婚姻有利",
                score=SCORE_WEIGHTS["jupiter_visible"],
                is_positive=True,
                source_ref="Muhurta Chintamani Ch. 7",
            ))
        if not ven_combust:
            total_score += SCORE_WEIGHTS["venus_visible"]
            factors.append(VedicMuhurtaFactor(
                factor_key="venus_visible",
                description_en="Venus is visible (not combust) — favourable for Vivaha",
                description_cn="金星可見（未被燃燒）— 對婚姻有利",
                score=SCORE_WEIGHTS["venus_visible"],
                is_positive=True,
                source_ref="Muhurta Chintamani Ch. 7",
            ))

    # Quality
    if total_score >= SCORE_EXCELLENT:
        quality, quality_cn, stars = "Excellent", "極佳", "★★★★★"
    elif total_score >= SCORE_GOOD:
        quality, quality_cn, stars = "Good", "良好", "★★★★☆"
    elif total_score >= SCORE_NEUTRAL:
        quality, quality_cn, stars = "Neutral", "中性", "★★★☆☆"
    elif total_score >= SCORE_POOR:
        quality, quality_cn, stars = "Poor", "不佳", "★★☆☆☆"
    else:
        quality, quality_cn, stars = "Avoid", "應迴避", "★☆☆☆☆"

    # Summary
    positives = [f.description_en for f in factors if f.is_positive]
    negatives = [f.description_en for f in factors if not f.is_positive]
    positives_cn = [f.description_cn for f in factors if f.is_positive]
    negatives_cn = [f.description_cn for f in factors if not f.is_positive]

    act_info = VEDIC_ACTIVITY_TYPES.get(activity_type, {})
    summary_en = (
        f"Vedic Muhurta for {act_info.get('en', activity_type)} — "
        f"Score: {total_score:+.0f} ({quality})\n"
        f"Panchanga: Tithi {tithi_data['name']}, Vara {vara_data['name']}, "
        f"Nakshatra {nak_data['name']}, Yoga {yoga_data['name']}, Karana {karana_data['name']}\n"
    )
    if positives:
        summary_en += "Auspicious: " + "; ".join(positives[:3]) + "\n"
    if negatives:
        summary_en += "Inauspicious: " + "; ".join(negatives[:3])

    summary_cn = (
        f"吠陀擇日（{act_info.get('cn', activity_type)}）— "
        f"評分：{total_score:+.0f}（{quality_cn}）\n"
        f"五曆：第{panch_raw['tithi']['num']}日 {tithi_data['name']}，"
        f"{vara_data['cn']}，{nak_data['name']}宿，"
        f"{yoga_data['cn']}瑜伽，{karana_data['name']}卡拉那\n"
    )
    if positives_cn:
        summary_cn += "吉利：" + "；".join(positives_cn[:3]) + "\n"
    if negatives_cn:
        summary_cn += "不利：" + "；".join(negatives_cn[:3])

    local_dt = datetime(year, month, day, hour, minute)

    return VedicMuhurtaResult(
        datetime_local=local_dt,
        julian_day=jd,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        activity_type=activity_type,
        timezone=timezone,
        ayanamsa=ayanamsa,
        lagna_sidereal=lagna_sid,
        lagna_rashi=lagna_rashi["name"],
        lagna_rashi_cn=lagna_rashi["cn"],
        lagna_rashi_index=lagna_idx,
        moon_sidereal=moon_sid,
        moon_rashi=moon_rashi["name"],
        moon_rashi_cn=moon_rashi["cn"],
        panchanga=panchanga,
        is_gandanta=is_gandanta,
        gandanta_note=gandanta_note,
        jupiter_combust=jup_combust,
        venus_combust=ven_combust,
        factors=factors,
        total_score=total_score,
        quality=quality,
        quality_cn=quality_cn,
        quality_stars=stars,
        summary_en=summary_en,
        summary_cn=summary_cn,
    )


# ============================================================
# Vedic Muhurta: Find Best Windows
# ============================================================

def find_vedic_muhurtas(
    start_year: int, start_month: int, start_day: int,
    end_year: int, end_month: int, end_day: int,
    timezone: float,
    latitude: float,
    longitude: float,
    activity_type: str = "important_meeting",
    location_name: str = "",
    step_hours: float = 1.0,
    min_score: float = 15.0,
    max_results: int = 10,
) -> List[VedicMuhurtaResult]:
    """
    Search for auspicious Muhurta windows in a date range.

    Scans every ``step_hours`` hours and returns results above ``min_score``,
    sorted by score descending, up to ``max_results``.

    Source: Muhurta Chintamani; Kalaprakashika.
    """
    swe.set_ephe_path("")
    results: List[VedicMuhurtaResult] = []

    start_jd = _julian_day(start_year, start_month, start_day, 6, 0, timezone)
    end_jd = _julian_day(end_year, end_month, end_day, 22, 0, timezone)

    jd = start_jd
    while jd <= end_jd:
        local_dt = _jd_to_local_datetime(jd, timezone)
        try:
            result = compute_vedic_muhurta(
                year=local_dt.year, month=local_dt.month, day=local_dt.day,
                hour=local_dt.hour, minute=local_dt.minute,
                timezone=timezone, latitude=latitude, longitude=longitude,
                activity_type=activity_type, location_name=location_name,
            )
            if result.total_score >= min_score:
                results.append(result)
        except Exception:
            pass
        jd += step_hours / 24.0

    results.sort(key=lambda r: r.total_score, reverse=True)
    return results[:max_results]


# ============================================================
# Unified Dispatch
# ============================================================

def compute_electional_chart(
    tradition: str,
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    activity_type: str = "important_meeting",
    location_name: str = "",
) -> Any:
    """
    Unified dispatcher: compute either Western electional or Vedic Muhurta.

    Args:
        tradition: 'western' or 'vedic'
        (other args same as compute_western_electional / compute_vedic_muhurta)
    """
    if tradition == "vedic":
        return compute_vedic_muhurta(
            year, month, day, hour, minute,
            timezone, latitude, longitude,
            activity_type, location_name,
        )
    return compute_western_electional(
        year, month, day, hour, minute,
        timezone, latitude, longitude,
        activity_type, location_name,
    )
