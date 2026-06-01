"""
astro/rectification/calculator.py — 出生時間校正多技術評分引擎

Birth Chart Rectification — Multi-Technique Scoring Engine

Classical references:
  - Vettius Valens, Anthology (2nd c. CE) — Profections, Zodiacal Releasing
  - William Lilly, Christian Astrology III (1647) — Primary Directions to Angles
  - Reinhold Ebertin, The Combination of Stellar Influences (1940) — Solar Arcs
  - Robert Hand, Planets in Transit (1976) — Transit timing
  - Bernadette Brady, Predictive Astrology (1992) — Multi-technique integration

Architecture:
  - ``score_candidate`` — scores a single candidate birth time against a list of events
  - ``run_rectification`` — generates candidates and returns ranked results
  - Each technique scoring function is isolated for testability
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from .constants import (
    TECHNIQUE_WEIGHTS,
    ANGLE_BONUS,
    LUMINARY_BONUS,
    EVENT_ORB_YEARS,
    CANDIDATE_STEP_MINUTES,
    DEFAULT_SEARCH_WINDOW_MINUTES,
    PLANET_NAMES_SHORT,
    PLANET_CHINESE,
    RECT_GOLD,
    RECT_PURPLE,
    RECT_BLUE,
    RECT_TEAL,
    RECT_ORANGE,
    _ASIN_CLAMP,
    SECONDARY_PROGRESSION_MAX_ORB,
    ZR_LOOSING_THRESHOLD_YEARS,
)

# ============================================================
# Constants
# ============================================================

_ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

_SIGN_CHINESE = {
    "Aries": "白羊", "Taurus": "金牛", "Gemini": "雙子", "Cancer": "巨蟹",
    "Leo": "獅子", "Virgo": "處女", "Libra": "天秤", "Scorpio": "天蠍",
    "Sagittarius": "射手", "Capricorn": "摩羯", "Aquarius": "水瓶", "Pisces": "雙魚",
}

_SIGN_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

_SIGN_YEARS = {
    "Aries": 15, "Taurus": 8, "Gemini": 20, "Cancer": 25,
    "Leo": 19, "Virgo": 20, "Libra": 8, "Scorpio": 15,
    "Sagittarius": 12, "Capricorn": 27, "Aquarius": 30, "Pisces": 12,
}

_PREDICT_PLANETS = {
    "Sun ☉": swe.SUN,
    "Moon ☽": swe.MOON,
    "Mercury ☿": swe.MERCURY,
    "Venus ♀": swe.VENUS,
    "Mars ♂": swe.MARS,
    "Jupiter ♃": swe.JUPITER,
    "Saturn ♄": swe.SATURN,
    "Uranus ♅": swe.URANUS,
    "Neptune ♆": swe.NEPTUNE,
    "Pluto ♇": swe.PLUTO,
}

_OUTER_PLANETS = {
    "Jupiter ♃": swe.JUPITER,
    "Saturn ♄": swe.SATURN,
    "Uranus ♅": swe.URANUS,
    "Neptune ♆": swe.NEPTUNE,
    "Pluto ♇": swe.PLUTO,
}

_ANGLES = {"ASC", "MC", "DSC", "IC"}
_LUMINARIES = {"Sun ☉", "Moon ☽", "Sun", "Moon"}

_MAJOR_ASPECTS = [
    ("Conjunction ☌", 0.0, 1.5),
    ("Opposition ☍", 180.0, 1.5),
    ("Trine △", 120.0, 1.5),
    ("Square □", 90.0, 1.5),
    ("Sextile ⚹", 60.0, 1.5),
]

# ============================================================
# Data Classes
# ============================================================

@dataclass
class LifeEvent:
    """A single life event used for rectification matching.

    Attributes:
        date_str:    ISO date string, e.g. ``"2015-03-12"``
        description: Short text description (bilingual OK)
        year:        Float year derived from date_str
        category:    Optional event category key from constants.EVENT_CATEGORIES
    """
    date_str: str
    description: str
    year: float = 0.0
    category: str = "other"

    def __post_init__(self) -> None:
        if not self.year and self.date_str:
            try:
                d = datetime.strptime(self.date_str[:10], "%Y-%m-%d")
                self.year = d.year + (d.month - 1) / 12.0 + (d.day - 1) / 365.0
            except ValueError:
                self.year = 0.0


@dataclass
class TechniqueHit:
    """A single technique match for a life event.

    Attributes:
        technique:      Technique identifier (e.g. ``"primary_direction"``)
        description_zh: Chinese description of the match
        description_en: English description of the match
        score:          Raw score contribution
        year_diff:      Distance in years between hit and event
        color:          Hex colour for display
    """
    technique: str
    description_zh: str
    description_en: str
    score: float
    year_diff: float
    color: str = RECT_GOLD


@dataclass
class EventMatch:
    """Matches found for a single life event.

    Attributes:
        event:     The source LifeEvent
        hits:      List of TechniqueHit objects
        total_score: Sum of hit scores
    """
    event: LifeEvent
    hits: List[TechniqueHit] = field(default_factory=list)
    total_score: float = 0.0

    def __post_init__(self) -> None:
        if not self.total_score and self.hits:
            self.total_score = sum(h.score for h in self.hits)


@dataclass
class CandidateResult:
    """Result for a single candidate birth time.

    Attributes:
        birth_jd:          Julian day of candidate birth time
        birth_datetime_str: Human-readable datetime string
        hour:              Integer birth hour
        minute:            Integer birth minute
        asc_lon:           Ascendant longitude
        mc_lon:            Midheaven longitude
        asc_sign:          Ascendant sign name
        mc_sign:           Midheaven sign name
        total_score:       Weighted technique score
        confidence:        Confidence percentage (0–100)
        event_matches:     Per-event match details
        technique_scores:  Score breakdown by technique
        planet_positions:  {name: longitude} natal chart
        house_cusps:       12-element list of house cusp longitudes
    """
    birth_jd: float
    birth_datetime_str: str
    hour: int
    minute: int
    asc_lon: float
    mc_lon: float
    asc_sign: str
    mc_sign: str
    total_score: float
    confidence: float
    event_matches: List[EventMatch] = field(default_factory=list)
    technique_scores: Dict[str, float] = field(default_factory=dict)
    planet_positions: Dict[str, float] = field(default_factory=dict)
    house_cusps: List[float] = field(default_factory=list)

# ============================================================
# Low-level helpers
# ============================================================

def _normalize(deg: float) -> float:
    """Normalise a longitude to [0, 360)."""
    return deg % 360.0


def _sign_idx(lon: float) -> int:
    """Return sign index 0–11 for a given longitude."""
    return int(_normalize(lon) / 30.0)


def _sign_deg(lon: float) -> float:
    """Return degrees within sign (0–30)."""
    return _normalize(lon) % 30.0


def _sign_name(lon: float) -> str:
    """Return sign name for longitude."""
    return _ZODIAC_SIGNS[_sign_idx(lon)]


def _aspect_check(lon_a: float, lon_b: float, orb: float = 1.5
                  ) -> Tuple[Optional[str], float]:
    """Check for major aspect between two longitudes.

    Returns:
        (aspect_name, orb_value) or (None, 999.0) if no aspect.
    """
    diff = abs(_normalize(lon_a) - _normalize(lon_b)) % 360
    if diff > 180:
        diff = 360 - diff
    for name, angle, max_orb in _MAJOR_ASPECTS:
        actual_orb = abs(diff - angle)
        if actual_orb <= min(orb, max_orb):
            return name, round(actual_orb, 2)
    return None, 999.0


def _obliquity(jd: float) -> float:
    """Return true obliquity of the ecliptic for Julian Day."""
    try:
        xx, _ = swe.calc_ut(jd, swe.ECL_NUT)
        return xx[0]
    except Exception:
        return 23.4367


def _compute_natal_chart(
    jd: float, lat: float, lon: float
) -> Tuple[Dict[str, float], float, float, List[float]]:
    """Compute natal chart for given JD and location.

    Returns:
        (planet_lons, asc, mc, house_cusps_12)

    All longitudes are tropical ecliptic degrees.
    """
    swe.set_ephe_path("")
    planet_lons: Dict[str, float] = {}

    for name, pid in _PREDICT_PLANETS.items():
        try:
            xx, _ = swe.calc_ut(jd, pid)
            planet_lons[name] = _normalize(xx[0])
        except Exception:
            planet_lons[name] = 0.0

    try:
        cusps, ascmc = swe.houses(jd, lat, lon, b"P")
        asc = _normalize(ascmc[0])
        mc = _normalize(ascmc[1])
        house_cusps = [_normalize(c) for c in cusps[:12]]
    except Exception:
        asc, mc = 0.0, 0.0
        house_cusps = [float(i * 30) for i in range(12)]

    return planet_lons, asc, mc, house_cusps


def _year_to_jd(year_float: float) -> float:
    """Convert a fractional year (e.g. 2015.5) to Julian Day."""
    year = int(year_float)
    frac = year_float - year
    # JD for Jan 1 of year + fraction of year in days
    jd_jan1 = swe.julday(year, 1, 1, 0.0)
    return jd_jan1 + frac * 365.25


def _event_age(event_year: float, birth_jd: float) -> float:
    """Return approximate age in years at event."""
    birth_year_float = _jd_to_year(birth_jd)
    return event_year - birth_year_float


def _jd_to_year(jd: float) -> float:
    """Convert Julian Day to fractional year."""
    try:
        y, m, d, h = swe.revjul(jd)
        jd_jan1 = swe.julday(y, 1, 1, 0.0)
        jd_dec31 = swe.julday(y + 1, 1, 1, 0.0)
        frac = (jd - jd_jan1) / (jd_dec31 - jd_jan1)
        return y + frac
    except Exception:
        return 0.0


def _is_angle_involved(name: str) -> bool:
    """Return True if name is an angle (ASC/MC/DSC/IC)."""
    return name in _ANGLES or name.upper() in {"ASC", "MC", "DSC", "IC"}


def _is_luminary(name: str) -> bool:
    """Return True if name is Sun or Moon."""
    n = name.split()[0] if " " in name else name
    return n in {"Sun", "Moon"}


def _score_bonus(name_a: str, name_b: str) -> float:
    """Compute multiplier bonus for angle/luminary involvement."""
    bonus = 1.0
    if _is_angle_involved(name_a) or _is_angle_involved(name_b):
        bonus *= ANGLE_BONUS
    if _is_luminary(name_a) or _is_luminary(name_b):
        bonus *= LUMINARY_BONUS
    return bonus


# ============================================================
# Technique Scoring Functions
# ============================================================

def _score_primary_directions(
    birth_jd: float,
    natal_planets: Dict[str, float],
    natal_asc: float,
    natal_mc: float,
    lat: float,
    lon: float,
    event_year: float,
    birth_year_float: float,
    event_age: float,
) -> List[TechniqueHit]:
    """Score Primary Directions for a single event.

    Uses Placidus oblique ascension formula.
    Arc in degrees ≈ age in years (Ptolemaic key).

    Ref: Lilly, Christian Astrology III; Placidus, Primum Mobile (1657).

    Args:
        birth_jd:          Julian Day of birth
        natal_planets:     {planet_name: longitude}
        natal_asc:         Natal Ascendant longitude
        natal_mc:          Natal Midheaven longitude
        lat:               Geographic latitude
        lon:               Geographic longitude
        event_year:        Fractional year of life event
        birth_year_float:  Fractional birth year
        event_age:         Age in years at event

    Returns:
        List of TechniqueHit objects with scored matches.
    """
    hits: List[TechniqueHit] = []
    weight = TECHNIQUE_WEIGHTS["primary_direction"]
    orb_years = EVENT_ORB_YEARS

    # We check if any directed arc lands near event_age
    # Significators: ASC, MC + major planets
    significators = {
        "ASC": natal_asc,
        "MC": natal_mc,
        **{k: v for k, v in natal_planets.items()
           if k in ("Sun ☉", "Moon ☽", "Venus ♀", "Mars ♂", "Jupiter ♃", "Saturn ♄")},
    }
    promissors = natal_planets

    # Pre-compute RA/Dec for all points at birth JD
    def _ra_dec(name: str) -> Tuple[float, float]:
        if name == "ASC":
            return _ecliptic_to_equatorial(natal_asc, birth_jd)
        elif name == "MC":
            return _ecliptic_to_equatorial(natal_mc, birth_jd)
        else:
            pid = _PREDICT_PLANETS.get(name)
            if pid is None:
                return 0.0, 0.0
            try:
                xx, _ = swe.calc_ut(birth_jd, pid, swe.FLG_EQUATORIAL)
                return _normalize(xx[0]), xx[1]
            except Exception:
                return 0.0, 0.0

    for sig_name, sig_lon in significators.items():
        sig_ra, sig_dec = _ra_dec(sig_name)
        for prom_name, prom_lon in promissors.items():
            if sig_name == prom_name:
                continue
            prom_ra, prom_dec = _ra_dec(prom_name)
            arc = _placidus_arc(sig_ra, sig_dec, prom_ra, prom_dec, lat)
            if arc is None:
                continue
            year_diff = abs(arc - event_age)
            if year_diff <= orb_years:
                bonus = _score_bonus(sig_name, prom_name)
                # Score peaks at 0 year_diff, drops linearly
                precision_factor = max(0.1, 1.0 - year_diff / orb_years)
                raw_score = weight * bonus * precision_factor
                sig_cn = PLANET_CHINESE.get(sig_name.split()[0], sig_name.split()[0])
                prom_cn = PLANET_CHINESE.get(prom_name.split()[0], prom_name.split()[0])
                hits.append(TechniqueHit(
                    technique="primary_direction",
                    description_zh=(
                        f"初級方向：{sig_cn} → {prom_cn}，"
                        f"弧度 {arc:.1f}° ≈ 年齡 {event_age:.1f}（誤差 {year_diff:.1f} 年）"
                    ),
                    description_en=(
                        f"Primary Direction: {sig_name} → {prom_name}, "
                        f"arc {arc:.1f}° ≈ age {event_age:.1f} (±{year_diff:.1f}y)"
                    ),
                    score=round(raw_score, 3),
                    year_diff=year_diff,
                    color=RECT_BLUE,
                ))

    return hits


def _ecliptic_to_equatorial(lon: float, jd: float) -> Tuple[float, float]:
    """Convert ecliptic longitude to RA/Dec at given JD."""
    eps = math.radians(_obliquity(jd))
    lon_r = math.radians(lon)
    ra = math.degrees(math.atan2(
        math.cos(eps) * math.sin(lon_r),
        math.cos(lon_r)
    ))
    dec = math.degrees(math.asin(math.sin(eps) * math.sin(lon_r)))
    return _normalize(ra), dec


def _placidus_arc(
    sig_ra: float, sig_dec: float,
    prom_ra: float, prom_dec: float,
    geog_lat: float,
) -> Optional[float]:
    """Compute Placidus primary direction arc (direct direction only).

    Returns:
        Arc in degrees (= approximate triggering age), or None if undefined.

    Ref: Placidus de Titi, Primum Mobile (1657); Holden, A History of
    Horoscopic Astrology (1996) ch. 13.
    """
    try:
        lat_r = math.radians(geog_lat)
        dec_sig_r = math.radians(sig_dec)
        dec_prom_r = math.radians(prom_dec)

        val_sig = _clamp_asin(math.tan(dec_sig_r) * math.tan(lat_r))
        val_prom = _clamp_asin(math.tan(dec_prom_r) * math.tan(lat_r))

        oa_sig = _normalize(sig_ra - math.degrees(math.asin(val_sig)))
        oa_prom = _normalize(prom_ra - math.degrees(math.asin(val_prom)))
        arc = _normalize(oa_prom - oa_sig)
        if arc > 180:
            arc -= 360
        return abs(arc)
    except (ValueError, ZeroDivisionError):
        return None


def _clamp_asin(value: float) -> float:
    """Clamp a value to the arcsine domain [-_ASIN_CLAMP, _ASIN_CLAMP].

    Prevents ValueError when floating-point errors push the argument
    just outside [-1, 1].
    """
    return max(-_ASIN_CLAMP, min(_ASIN_CLAMP, value))


def _score_solar_arc(
    birth_jd: float,
    natal_planets: Dict[str, float],
    natal_asc: float,
    natal_mc: float,
    event_age: float,
) -> List[TechniqueHit]:
    """Score Solar Arc Directions for a single event.

    Solar arc = progressed Sun longitude − natal Sun longitude.
    All natal points are shifted by this arc.

    Ref: Ebertin, The Combination of Stellar Influences (1940).

    Args:
        birth_jd:      Julian Day of birth
        natal_planets: {planet_name: longitude}
        natal_asc:     Natal ASC longitude
        natal_mc:      Natal MC longitude
        event_age:     Age in years at event

    Returns:
        List of TechniqueHit objects.
    """
    hits: List[TechniqueHit] = []
    weight = TECHNIQUE_WEIGHTS["solar_arc"]
    orb = EVENT_ORB_YEARS

    # Compute solar arc for event_age
    prog_jd = birth_jd + event_age
    try:
        sun_prog, _ = swe.calc_ut(prog_jd, swe.SUN)
        sun_natal = natal_planets.get("Sun ☉", 0.0)
        solar_arc = _normalize(sun_prog[0] - sun_natal)
        if solar_arc > 180:
            solar_arc -= 360
    except Exception:
        solar_arc = event_age  # approximate 1°/year

    # Check SA angles/planets against natal planets
    sa_points = {
        "SA ASC": _normalize(natal_asc + solar_arc),
        "SA MC": _normalize(natal_mc + solar_arc),
    }
    for pname, nlon in natal_planets.items():
        short = pname.split()[0]
        sa_points[f"SA {short}"] = _normalize(nlon + solar_arc)

    # Cross-check SA points against natal chart
    natal_check = {
        "ASC": natal_asc,
        "MC": natal_mc,
        **natal_planets,
    }

    for sa_name, sa_lon in sa_points.items():
        for nat_name, nat_lon in natal_check.items():
            if sa_name.replace("SA ", "") == nat_name.split()[0]:
                continue
            asp, asp_orb = _aspect_check(sa_lon, nat_lon, orb=1.0)
            if asp:
                bonus = _score_bonus(sa_name, nat_name)
                precision_factor = max(0.1, 1.0 - asp_orb)
                raw_score = weight * bonus * precision_factor
                sa_cn = PLANET_CHINESE.get(sa_name.replace("SA ", ""), sa_name)
                nat_cn = PLANET_CHINESE.get(nat_name.split()[0], nat_name.split()[0])
                hits.append(TechniqueHit(
                    technique="solar_arc",
                    description_zh=(
                        f"太陽弧：{sa_cn} {asp} 本命 {nat_cn}"
                        f"（容許 {asp_orb:.1f}°）"
                    ),
                    description_en=(
                        f"Solar Arc: {sa_name} {asp} natal {nat_name} (orb {asp_orb:.1f}°)"
                    ),
                    score=round(raw_score, 3),
                    year_diff=asp_orb,
                    color=RECT_GOLD,
                ))

    return hits


def _score_secondary_progressions(
    birth_jd: float,
    natal_planets: Dict[str, float],
    natal_asc: float,
    natal_mc: float,
    lat: float,
    lon: float,
    event_age: float,
) -> List[TechniqueHit]:
    """Score Secondary Progressions for a single event.

    Day-for-a-year: chart cast for (birth_jd + event_age days)
    is the progressed chart for that age.

    Progressed Moon is especially sensitive to exact birth time.

    Ref: Sepharial, Primary Directions Made Easy (1898).

    Args:
        birth_jd:      Julian Day of birth
        natal_planets: {planet_name: longitude}
        natal_asc:     Natal ASC longitude
        natal_mc:      Natal MC longitude
        lat:           Geographic latitude
        lon:           Geographic longitude
        event_age:     Age in years at event

    Returns:
        List of TechniqueHit objects.
    """
    hits: List[TechniqueHit] = []
    weight = TECHNIQUE_WEIGHTS["secondary_progression"]

    prog_jd = birth_jd + event_age  # 1 day = 1 year

    try:
        cusps_p, ascmc_p = swe.houses(prog_jd, lat, lon, b"P")
        prog_asc = _normalize(ascmc_p[0])
        prog_mc = _normalize(ascmc_p[1])
    except Exception:
        prog_asc, prog_mc = natal_asc, natal_mc

    prog_planets: Dict[str, float] = {}
    for name, pid in _PREDICT_PLANETS.items():
        try:
            xx, _ = swe.calc_ut(prog_jd, pid)
            prog_planets[name] = _normalize(xx[0])
        except Exception:
            prog_planets[name] = natal_planets.get(name, 0.0)

    check_targets = {
        "ASC": natal_asc,
        "MC": natal_mc,
        **natal_planets,
    }

    prog_points = {
        "Prog ASC": prog_asc,
        "Prog MC": prog_mc,
        **{f"Prog {n.split()[0]}": v for n, v in prog_planets.items()},
    }

    for pp_name, pp_lon in prog_points.items():
        for tgt_name, tgt_lon in check_targets.items():
            short_pp = pp_name.replace("Prog ", "")
            if short_pp == tgt_name.split()[0]:
                continue
            asp, asp_orb = _aspect_check(pp_lon, tgt_lon, orb=1.0)
            if asp and asp_orb <= SECONDARY_PROGRESSION_MAX_ORB:
                bonus = _score_bonus(pp_name, tgt_name)
                precision_factor = max(0.1, 1.0 - asp_orb / SECONDARY_PROGRESSION_MAX_ORB)
                raw_score = weight * bonus * precision_factor
                pp_cn = PLANET_CHINESE.get(short_pp, short_pp)
                tgt_cn = PLANET_CHINESE.get(tgt_name.split()[0], tgt_name.split()[0])
                hits.append(TechniqueHit(
                    technique="secondary_progression",
                    description_zh=(
                        f"次進：推進{pp_cn} {asp} 本命{tgt_cn}"
                        f"（容許 {asp_orb:.1f}°）"
                    ),
                    description_en=(
                        f"Sec.Prog: Prog.{pp_name} {asp} natal {tgt_name} (orb {asp_orb:.1f}°)"
                    ),
                    score=round(raw_score, 3),
                    year_diff=asp_orb,
                    color=RECT_PURPLE,
                ))

    return hits


def _score_profections(
    natal_asc: float,
    birth_year_float: float,
    event_year: float,
    natal_planets: Dict[str, float],
    house_cusps: List[float],
) -> List[TechniqueHit]:
    """Score Annual Profections for a single event.

    The ASC moves one sign per year. At event_year, the profected sign
    activates its ruler as Time Lord. If the Time Lord is activated by
    primary direction or transit at the same time, it confirms the time.

    Ref: Vettius Valens, Anthology IV.1–3 (2nd c. CE).

    Args:
        natal_asc:         Natal ASC longitude
        birth_year_float:  Fractional birth year
        event_year:        Fractional year of event
        natal_planets:     {planet_name: longitude}
        house_cusps:       12-element cusp list

    Returns:
        List of TechniqueHit objects.
    """
    hits: List[TechniqueHit] = []
    weight = TECHNIQUE_WEIGHTS["profection"]

    age = event_year - birth_year_float
    if age < 0:
        return hits

    asc_idx = _sign_idx(natal_asc)
    prof_idx = (asc_idx + int(age)) % 12
    prof_sign = _ZODIAC_SIGNS[prof_idx]
    time_lord = _SIGN_RULERS[prof_sign]

    # Check if time lord is in an angular house (enhances score)
    time_lord_key = next((k for k in natal_planets if k.split()[0] == time_lord), None)
    if time_lord_key is None:
        return hits

    tl_lon = natal_planets[time_lord_key]
    house_num = _find_house(tl_lon, house_cusps)
    angular = house_num in (1, 4, 7, 10)
    succedent = house_num in (2, 5, 8, 11)

    strength = 1.2 if angular else (1.0 if succedent else 0.7)

    tl_cn = PLANET_CHINESE.get(time_lord, time_lord)
    sign_cn = _SIGN_CHINESE.get(prof_sign, prof_sign)
    hits.append(TechniqueHit(
        technique="profection",
        description_zh=(
            f"流年小限：{int(age)}歲進入{sign_cn}宮，時間主星{tl_cn}"
            f"（{house_num}宮{'角宮' if angular else ''}）已激活"
        ),
        description_en=(
            f"Profection: Age {int(age)} → {prof_sign} (house {prof_idx+1}), "
            f"Time Lord {time_lord} in H{house_num}"
        ),
        score=round(weight * strength, 3),
        year_diff=age % 1,  # fractional year within profection year
        color=RECT_TEAL,
    ))
    return hits


def _score_zodiacal_releasing(
    fortune_lon: float,
    birth_jd: float,
    event_year: float,
    birth_year_float: float,
) -> List[TechniqueHit]:
    """Score Zodiacal Releasing (Lot of Fortune) for a single event.

    Checks whether the event falls near a period boundary or
    "Loosing of the Bond" transition.

    Ref: Vettius Valens, Anthology IV.1, VII.6 (2nd c. CE).

    Args:
        fortune_lon:       Lot of Fortune longitude
        birth_jd:          Julian Day of birth
        event_year:        Fractional year of event
        birth_year_float:  Fractional birth year

    Returns:
        List of TechniqueHit objects.
    """
    hits: List[TechniqueHit] = []
    weight = TECHNIQUE_WEIGHTS["zodiacal_releasing"]

    event_jd = _year_to_jd(event_year)
    start_idx = _sign_idx(fortune_lon)
    cur_jd = birth_jd

    for i in range(30):
        idx = (start_idx + i) % 12
        sign = _ZODIAC_SIGNS[idx]
        yrs = _SIGN_YEARS[sign]
        end_jd = cur_jd + yrs * 365.25

        # Check if event falls within this period
        if cur_jd <= event_jd <= end_jd:
            # Score based on how close event is to period boundary
            dist_to_start = abs(event_jd - cur_jd) / 365.25
            dist_to_end = abs(event_jd - end_jd) / 365.25
            min_dist = min(dist_to_start, dist_to_end)

            # "Loosing of the Bond" = within ZR_LOOSING_THRESHOLD_YEARS of boundary
            is_loosing = min_dist <= ZR_LOOSING_THRESHOLD_YEARS
            strength = (1.5 if is_loosing else 0.8)

            sign_cn = _SIGN_CHINESE.get(sign, sign)
            ruler = _SIGN_RULERS[sign]
            ruler_cn = PLANET_CHINESE.get(ruler, ruler)

            period_start_year = _jd_to_year(cur_jd)
            period_end_year = _jd_to_year(end_jd)

            hits.append(TechniqueHit(
                technique="zodiacal_releasing",
                description_zh=(
                    f"黃道釋放：L1 期間 {sign_cn}（{ruler_cn}）"
                    f" {period_start_year:.1f}–{period_end_year:.1f}"
                    + ("，鬆脫期！" if is_loosing else "")
                ),
                description_en=(
                    f"ZR: L1 {sign} ({ruler}) period "
                    f"{period_start_year:.1f}–{period_end_year:.1f}"
                    + (" [LOOSING OF BOND]" if is_loosing else "")
                ),
                score=round(weight * strength, 3),
                year_diff=min_dist,
                color=RECT_TEAL,
            ))
            break

        if end_jd > event_jd + 365 * 30:
            break
        cur_jd = end_jd

    return hits


def _score_transits(
    natal_planets: Dict[str, float],
    natal_asc: float,
    natal_mc: float,
    event_year: float,
) -> List[TechniqueHit]:
    """Score major transits (outer planets to natal points) for a single event.

    Uses outer planets only; inner planet transits too frequent to be
    reliable for rectification.

    Ref: Robert Hand, Planets in Transit (1976).

    Args:
        natal_planets: {planet_name: longitude}
        natal_asc:     Natal ASC longitude
        natal_mc:      Natal MC longitude
        event_year:    Fractional year of event

    Returns:
        List of TechniqueHit objects.
    """
    hits: List[TechniqueHit] = []
    weight_outer = TECHNIQUE_WEIGHTS["transit_outer"]

    event_jd = _year_to_jd(event_year)

    transit_positions: Dict[str, float] = {}
    for pname, pid in _OUTER_PLANETS.items():
        try:
            xx, _ = swe.calc_ut(event_jd, pid)
            transit_positions[pname] = _normalize(xx[0])
        except Exception:
            continue

    natal_check = {
        "ASC": natal_asc,
        "MC": natal_mc,
        **natal_planets,
    }

    for tr_name, tr_lon in transit_positions.items():
        for nat_name, nat_lon in natal_check.items():
            asp, asp_orb = _aspect_check(tr_lon, nat_lon, orb=1.0)
            if asp:
                bonus = _score_bonus(tr_name, nat_name)
                precision_factor = max(0.1, 1.0 - asp_orb)
                raw_score = weight_outer * bonus * precision_factor
                tr_cn = PLANET_CHINESE.get(tr_name.split()[0], tr_name.split()[0])
                nat_cn = PLANET_CHINESE.get(nat_name.split()[0], nat_name.split()[0])
                hits.append(TechniqueHit(
                    technique="transit_outer",
                    description_zh=(
                        f"過境：流年{tr_cn} {asp} 本命{nat_cn}"
                        f"（容許 {asp_orb:.1f}°）"
                    ),
                    description_en=(
                        f"Transit: {tr_name} {asp} natal {nat_name} (orb {asp_orb:.1f}°)"
                    ),
                    score=round(raw_score, 3),
                    year_diff=asp_orb,
                    color=RECT_ORANGE,
                ))

    return hits


def _find_house(lon: float, cusps: List[float]) -> int:
    """Return 1-based house number for a longitude given 12 house cusps."""
    for i in range(12):
        c1 = cusps[i]
        c2 = cusps[(i + 1) % 12]
        if c2 < c1:
            if lon >= c1 or lon < c2:
                return i + 1
        elif c1 <= lon < c2:
            return i + 1
    return 1


def _compute_lot_of_fortune(
    planet_lons: Dict[str, float],
    asc: float,
    is_day: bool,
) -> float:
    """Compute Lot of Fortune longitude.

    Day chart: ASC + Moon − Sun.
    Night chart: ASC + Sun − Moon.

    Ref: Valens, Anthology II.1.
    """
    sun = planet_lons.get("Sun ☉", 0.0)
    moon = planet_lons.get("Moon ☽", 0.0)
    if is_day:
        return _normalize(asc + moon - sun)
    else:
        return _normalize(asc + sun - moon)


# ============================================================
# Main Scoring Function
# ============================================================

def score_candidate(
    birth_jd: float,
    lat: float,
    lon: float,
    events: List[LifeEvent],
    techniques: Optional[List[str]] = None,
) -> CandidateResult:
    """Score a single candidate birth time against a list of life events.

    Computes natal chart, then applies each enabled technique across all
    events, accumulating weighted scores.

    Args:
        birth_jd:   Julian Day of candidate birth time
        lat:        Geographic latitude of birth
        lon:        Geographic longitude of birth
        events:     List of LifeEvent objects
        techniques: List of technique keys to use (default: all)

    Returns:
        CandidateResult with total_score and per-event matches.
    """
    if techniques is None:
        techniques = list(TECHNIQUE_WEIGHTS.keys())

    swe.set_ephe_path("")

    planet_lons, asc, mc, cusps = _compute_natal_chart(birth_jd, lat, lon)
    birth_year_float = _jd_to_year(birth_jd)

    is_day = True
    sun_lon = planet_lons.get("Sun ☉", 0.0)
    sun_above_horizon = _is_above_horizon(sun_lon, asc, cusps)
    is_day = sun_above_horizon

    fortune_lon = _compute_lot_of_fortune(planet_lons, asc, is_day)

    event_matches: List[EventMatch] = []
    technique_scores: Dict[str, float] = {t: 0.0 for t in TECHNIQUE_WEIGHTS}

    for event in events:
        if not event.year:
            continue
        event_age = _event_age(event.year, birth_jd)
        if event_age < 0 or event_age > 100:
            continue

        all_hits: List[TechniqueHit] = []

        # 1. Primary Directions
        if "primary_direction" in techniques:
            try:
                pd_hits = _score_primary_directions(
                    birth_jd, planet_lons, asc, mc, lat, lon,
                    event.year, birth_year_float, event_age,
                )
                all_hits.extend(pd_hits)
            except Exception:
                pass

        # 2. Solar Arc
        if "solar_arc" in techniques:
            try:
                sa_hits = _score_solar_arc(
                    birth_jd, planet_lons, asc, mc, event_age,
                )
                all_hits.extend(sa_hits)
            except Exception:
                pass

        # 3. Secondary Progressions
        if "secondary_progression" in techniques:
            try:
                sp_hits = _score_secondary_progressions(
                    birth_jd, planet_lons, asc, mc, lat, lon, event_age,
                )
                all_hits.extend(sp_hits)
            except Exception:
                pass

        # 4. Profections
        if "profection" in techniques:
            try:
                pf_hits = _score_profections(
                    asc, birth_year_float, event.year, planet_lons, cusps,
                )
                all_hits.extend(pf_hits)
            except Exception:
                pass

        # 5. Zodiacal Releasing
        if "zodiacal_releasing" in techniques:
            try:
                zr_hits = _score_zodiacal_releasing(
                    fortune_lon, birth_jd, event.year, birth_year_float,
                )
                all_hits.extend(zr_hits)
            except Exception:
                pass

        # 6. Transits
        if "transit_outer" in techniques:
            try:
                tr_hits = _score_transits(planet_lons, asc, mc, event.year)
                all_hits.extend(tr_hits)
            except Exception:
                pass

        match_score = sum(h.score for h in all_hits)
        for h in all_hits:
            technique_scores[h.technique] = (
                technique_scores.get(h.technique, 0.0) + h.score
            )

        event_matches.append(EventMatch(
            event=event,
            hits=all_hits,
            total_score=round(match_score, 3),
        ))

    total_score = sum(em.total_score for em in event_matches)

    # Build datetime string
    try:
        y, m, d, h = swe.revjul(birth_jd)
        hr = int(h)
        mn = int((h - hr) * 60)
        dt_str = f"{int(y):04d}-{int(m):02d}-{int(d):02d} {hr:02d}:{mn:02d}"
    except Exception:
        dt_str = "Unknown"
        hr, mn = 0, 0

    return CandidateResult(
        birth_jd=birth_jd,
        birth_datetime_str=dt_str,
        hour=hr,
        minute=mn,
        asc_lon=asc,
        mc_lon=mc,
        asc_sign=_sign_name(asc),
        mc_sign=_sign_name(mc),
        total_score=round(total_score, 3),
        confidence=0.0,  # set by caller after normalising
        event_matches=event_matches,
        technique_scores={k: round(v, 3) for k, v in technique_scores.items()},
        planet_positions=planet_lons,
        house_cusps=cusps,
    )


def _is_above_horizon(sun_lon: float, asc: float, cusps: List[float]) -> bool:
    """Return True if Sun is in houses 7–12 (above horizon = day chart)."""
    h = _find_house(sun_lon, cusps)
    return h in (7, 8, 9, 10, 11, 12)


# ============================================================
# Candidate Generation & Ranking
# ============================================================

def run_rectification(
    approx_birth_datetime: datetime,
    lat: float,
    lon: float,
    timezone_offset: float,
    events: List[LifeEvent],
    search_window_minutes: int = DEFAULT_SEARCH_WINDOW_MINUTES,
    step_minutes: int = CANDIDATE_STEP_MINUTES,
    techniques: Optional[List[str]] = None,
    top_n: int = 5,
) -> List[CandidateResult]:
    """Run full multi-technique birth chart rectification.

    Generates candidate birth times at ``step_minutes`` intervals within
    ``±search_window_minutes`` of ``approx_birth_datetime``, scores each
    candidate against ``events``, and returns the top ``top_n`` results
    ranked by total score.

    Args:
        approx_birth_datetime: Best-guess birth datetime (UTC-local, naive)
        lat:                   Geographic latitude
        lon:                   Geographic longitude
        timezone_offset:       Hours east of UTC (e.g. +8 for HKT)
        events:                List of LifeEvent objects
        search_window_minutes: Half-width of search window (minutes)
        step_minutes:          Time step between candidates (minutes)
        techniques:            Techniques to use; None = all
        top_n:                 Number of top results to return

    Returns:
        List of up to ``top_n`` CandidateResult objects, sorted by total_score
        descending, with confidence percentages set.
    """
    swe.set_ephe_path("")

    if techniques is None:
        techniques = list(TECHNIQUE_WEIGHTS.keys())

    # Convert approximate birth time to Julian Day (UTC)
    utc_dt = approx_birth_datetime - timedelta(hours=timezone_offset)
    base_jd = swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0,
    )

    # Generate candidate JDs
    n_steps = search_window_minutes // step_minutes
    candidate_jds: List[float] = []
    for i in range(-n_steps, n_steps + 1):
        candidate_jds.append(base_jd + i * step_minutes / (24 * 60))

    # Score each candidate
    results: List[CandidateResult] = []
    for cjd in candidate_jds:
        try:
            res = score_candidate(cjd, lat, lon, events, techniques)
            results.append(res)
        except Exception:
            continue

    if not results:
        return []

    # Sort by total score descending
    results.sort(key=lambda r: r.total_score, reverse=True)

    # Normalise confidence as percentage of highest score
    max_score = results[0].total_score if results[0].total_score > 0 else 1.0
    for r in results:
        r.confidence = round(min(100.0, (r.total_score / max_score) * 100), 1)

    return results[:top_n]
