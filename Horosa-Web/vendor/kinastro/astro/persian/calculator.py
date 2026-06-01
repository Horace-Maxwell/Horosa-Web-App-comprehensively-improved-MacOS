"""
astro/persian/calculator.py — 薩珊波斯高階占星計算引擎

Advanced Sassanian / Persian Astrology Calculator
深度實現波斯薩珊占星傳統的核心技術：

1. Firdaria 生命週期 (正確的日夜序列與年數)
2. Hyleg & Alcocoden (生命給予者與壽命給予者)
3. Almuten Figuris (全盤最強行星)
4. 年度 + 月度主限 (Annual + Monthly Profections)
5. 埃及界 (Egyptian Bounds)
6. 多德卡特摩里亞 (Dodecatemoria / 12th Parts)
7. 反射點 (Antiscia & Contra-antiscia)
8. 擴展阿拉伯點 (Extended Arabic Parts)
9. Dorotheus 風格解讀
10. 三分守護星 (Triplicity Lords)
11. 整宮制 (Whole Sign Houses)

Primary Sources:
- Dorotheus of Sidon, "Carmen Astrologicum" (1st century CE)
- Ptolemy, "Tetrabiblos" (2nd century CE)
- Abu Ma'shar, "Introductorium in Astronomiam" (9th century CE)
- Masha'allah ibn Athari, "On Nativities" (8th century CE)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import swisseph as swe

from .constants import (
    PLANET_NAMES_CN,
    PLANET_GLYPHS,
    ZODIAC_SIGNS,
    FIRDARIA_YEARS,
    FIRDARIA_DAY_ORDER,
    FIRDARIA_NIGHT_ORDER,
    FIRDARIA_SUBPERIOD_PLANETS,
    DOMICILE,
    EXALTATION,
    DETRIMENT,
    FALL,
    TRIPLICITY_LORDS,
    ELEMENT_OF_SIGN,
    EGYPTIAN_BOUNDS,
    DECAN_RULERS,
    ARABIC_PARTS,
    ROYAL_STARS,
    PLANETARY_MAJOR_YEARS,
    PLANETARY_MINOR_YEARS,
    PLANETARY_MIDDLE_YEARS,
    HOUSE_SIGNIFICATIONS,
    DOROTHEUS_INTERPRETATIONS,
    PLANET_NATURE,
    DIURNAL_PLANETS,
    NOCTURNAL_PLANETS,
    BENEFIC_PLANETS,
    MALEFIC_PLANETS,
    PLANET_SECT_JOY,
)

# ─────────────────────────────────────────────────────────────
# Swiss Ephemeris planet IDs
# ─────────────────────────────────────────────────────────────

_PLANET_IDS: Dict[str, int] = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
}

# Direct sign-name to index lookup (faster than ZODIAC_SIGNS.index + generator)
_SIGN_INDEX: Dict[str, int] = {z[0]: i for i, z in enumerate(ZODIAC_SIGNS)}

# ─────────────────────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────────────────────

@dataclass
class DeepPlanetPos:
    """Planet position with full dignity analysis."""
    name:          str
    name_cn:       str
    glyph:         str
    longitude:     float       # tropical, 0-360°
    latitude:      float
    speed:         float       # deg/day  (negative = retrograde)
    sign:          str
    sign_cn:       str
    sign_index:    int         # 0-11
    sign_glyph:    str
    degree_in_sign: float      # 0-30°
    house:         int         # 1-12 (whole-sign)
    is_retrograde: bool

    # Essential dignities
    dignity:       str         # "Domicile" | "Exaltation" | "Triplicity" | "Bound" | "Face" | "Peregrine" | "Detriment" | "Fall"
    dignity_cn:    str
    dignity_score: float       # numeric score for Almuten
    domicile_lord: str         # lord of the sign
    exalt_lord:    str         # exaltation lord (may be "")
    triplicity_day_lord:   str
    triplicity_night_lord: str
    triplicity_part_lord:  str
    egyptian_bound_lord:   str
    decan_lord:    str

    # Sect
    is_in_sect: bool           # planet matches the sect of the chart

    # Antiscia
    antiscion_longitude:       float
    contra_antiscion_longitude: float
    antiscion_sign:            str
    contra_antiscion_sign:     str

    # Dodecatemoria
    dodecatemoria_longitude:   float
    dodecatemoria_sign:        str
    dodecatemoria_sign_cn:     str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "name_cn": self.name_cn,
            "glyph": self.glyph,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "speed": self.speed,
            "sign": self.sign,
            "sign_cn": self.sign_cn,
            "sign_index": self.sign_index,
            "sign_glyph": self.sign_glyph,
            "degree_in_sign": self.degree_in_sign,
            "house": self.house,
            "is_retrograde": self.is_retrograde,
            "dignity": self.dignity,
            "dignity_cn": self.dignity_cn,
            "dignity_score": self.dignity_score,
            "domicile_lord": self.domicile_lord,
            "exalt_lord": self.exalt_lord,
            "triplicity_day_lord": self.triplicity_day_lord,
            "triplicity_night_lord": self.triplicity_night_lord,
            "triplicity_part_lord": self.triplicity_part_lord,
            "egyptian_bound_lord": self.egyptian_bound_lord,
            "decan_lord": self.decan_lord,
            "is_in_sect": self.is_in_sect,
            "antiscion_longitude": self.antiscion_longitude,
            "contra_antiscion_longitude": self.contra_antiscion_longitude,
            "antiscion_sign": self.antiscion_sign,
            "contra_antiscion_sign": self.contra_antiscion_sign,
            "dodecatemoria_longitude": self.dodecatemoria_longitude,
            "dodecatemoria_sign": self.dodecatemoria_sign,
            "dodecatemoria_sign_cn": self.dodecatemoria_sign_cn,
        }


@dataclass
class DeepFirdarPeriod:
    """A major Firdaria period with sub-periods."""
    major_lord:    str
    major_lord_cn: str
    major_glyph:   str
    start_jd:      float
    end_jd:        float
    start_date:    str
    end_date:      str
    duration_years: float
    is_current:    bool
    sub_periods:   List["DeepFirdarSubPeriod"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "major_lord": self.major_lord,
            "major_lord_cn": self.major_lord_cn,
            "major_glyph": self.major_glyph,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "duration_years": self.duration_years,
            "is_current": self.is_current,
            "sub_periods": [sp.to_dict() for sp in self.sub_periods],
        }


@dataclass
class DeepFirdarSubPeriod:
    """A Firdaria sub-period (minor period)."""
    major_lord:  str
    sub_lord:    str
    sub_lord_cn: str
    sub_glyph:   str
    start_date:  str
    end_date:    str
    duration_years: float
    is_current:  bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "major_lord": self.major_lord,
            "sub_lord": self.sub_lord,
            "sub_lord_cn": self.sub_lord_cn,
            "sub_glyph": self.sub_glyph,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "duration_years": self.duration_years,
            "is_current": self.is_current,
        }


@dataclass
class DeepHylegResult:
    """Hyleg (Giver of Life) result."""
    hyleg_planet:  str
    hyleg_cn:      str
    hyleg_glyph:   str
    longitude:     float
    sign:          str
    sign_cn:       str
    degree:        float
    house:         int
    is_valid:      bool
    method:        str   # "sun_day" | "moon_night" | "lot_fortune" | "ascendant"
    reason_en:     str
    reason_cn:     str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hyleg_planet": self.hyleg_planet,
            "hyleg_cn": self.hyleg_cn,
            "hyleg_glyph": self.hyleg_glyph,
            "longitude": self.longitude,
            "sign": self.sign,
            "sign_cn": self.sign_cn,
            "degree": self.degree,
            "house": self.house,
            "is_valid": self.is_valid,
            "method": self.method,
            "reason_en": self.reason_en,
            "reason_cn": self.reason_cn,
        }


@dataclass
class DeepAlcocodenResult:
    """Alcocoden (Giver of Years) result."""
    lord:             str
    lord_cn:          str
    lord_glyph:       str
    base_years_major: int
    base_years_minor: int
    base_years_middle: int
    modified_years:   float
    aspect_modifiers: List[str]
    final_range_min:  float
    final_range_max:  float
    reason_en:        str
    reason_cn:        str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lord": self.lord,
            "lord_cn": self.lord_cn,
            "lord_glyph": self.lord_glyph,
            "base_years_major": self.base_years_major,
            "base_years_minor": self.base_years_minor,
            "base_years_middle": self.base_years_middle,
            "modified_years": self.modified_years,
            "aspect_modifiers": self.aspect_modifiers,
            "final_range_min": self.final_range_min,
            "final_range_max": self.final_range_max,
            "reason_en": self.reason_en,
            "reason_cn": self.reason_cn,
        }


@dataclass
class DeepAlmutenResult:
    """Almuten Figuris — chart ruler by dignity points."""
    planet:        str
    planet_cn:     str
    planet_glyph:  str
    total_score:   float
    all_scores:    Dict[str, float]   # planet -> score
    breakdown:     Dict[str, Dict[str, float]]  # planet -> {point -> score}
    reason_en:     str
    reason_cn:     str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "planet": self.planet,
            "planet_cn": self.planet_cn,
            "planet_glyph": self.planet_glyph,
            "total_score": self.total_score,
            "all_scores": self.all_scores,
            "breakdown": self.breakdown,
            "reason_en": self.reason_en,
            "reason_cn": self.reason_cn,
        }


@dataclass
class DeepProfectionYear:
    """Annual or monthly profection result."""
    period_type:   str    # "annual" | "monthly"
    age:           int    # for annual; month index for monthly
    month:         Optional[int]   # 1-12 for monthly
    sign:          str
    sign_cn:       str
    sign_index:    int
    sign_glyph:    str
    lord:          str
    lord_cn:       str
    lord_glyph:    str
    start_date:    str
    end_date:      str
    house_activated: int
    signification_en: str
    signification_cn: str
    is_current:    bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "period_type": self.period_type,
            "age": self.age,
            "month": self.month,
            "sign": self.sign,
            "sign_cn": self.sign_cn,
            "sign_index": self.sign_index,
            "sign_glyph": self.sign_glyph,
            "lord": self.lord,
            "lord_cn": self.lord_cn,
            "lord_glyph": self.lord_glyph,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "house_activated": self.house_activated,
            "signification_en": self.signification_en,
            "signification_cn": self.signification_cn,
            "is_current": self.is_current,
        }


@dataclass
class DeepArabicPart:
    """An Arabic Part / Persian Lot."""
    name_en:       str
    name_cn:       str
    name_arabic:   str
    longitude:     float
    sign:          str
    sign_cn:       str
    sign_glyph:    str
    degree:        float
    house:         int
    lord:          str
    lord_cn:       str
    lord_glyph:    str
    formula_used:  str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name_en": self.name_en,
            "name_cn": self.name_cn,
            "name_arabic": self.name_arabic,
            "longitude": self.longitude,
            "sign": self.sign,
            "sign_cn": self.sign_cn,
            "sign_glyph": self.sign_glyph,
            "degree": self.degree,
            "house": self.house,
            "lord": self.lord,
            "lord_cn": self.lord_cn,
            "lord_glyph": self.lord_glyph,
            "formula_used": self.formula_used,
        }


@dataclass
class DeepRoyalStar:
    """Royal star conjunction prominence."""
    star_name:      str
    star_name_cn:   str
    star_pahlavi:   str
    star_longitude: float
    guardian:       str
    conjunction_planet: Optional[str]
    conjunction_planet_cn: Optional[str]
    conjunction_glyph: Optional[str]
    orb:            float
    is_prominent:   bool
    meaning_en:     str
    meaning_cn:     str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "star_name": self.star_name,
            "star_name_cn": self.star_name_cn,
            "star_pahlavi": self.star_pahlavi,
            "star_longitude": self.star_longitude,
            "guardian": self.guardian,
            "conjunction_planet": self.conjunction_planet,
            "conjunction_planet_cn": self.conjunction_planet_cn,
            "conjunction_glyph": self.conjunction_glyph,
            "orb": self.orb,
            "is_prominent": self.is_prominent,
            "meaning_en": self.meaning_en,
            "meaning_cn": self.meaning_cn,
        }


@dataclass
class TriplicityInfo:
    """Triplicity lord info for a chart."""
    element:        str
    element_cn:     str
    signs:          List[str]
    day_lord:       str
    day_lord_cn:    str
    night_lord:     str
    night_lord_cn:  str
    part_lord:      str
    part_lord_cn:   str
    active_lord:    str      # which lord is active based on day/night

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element": self.element,
            "element_cn": self.element_cn,
            "signs": self.signs,
            "day_lord": self.day_lord,
            "day_lord_cn": self.day_lord_cn,
            "night_lord": self.night_lord,
            "night_lord_cn": self.night_lord_cn,
            "part_lord": self.part_lord,
            "part_lord_cn": self.part_lord_cn,
            "active_lord": self.active_lord,
        }


@dataclass
class DorotheusSummary:
    """Dorotheus-style life topic interpretation."""
    longevity_en:   str
    longevity_cn:   str
    marriage_en:    str
    marriage_cn:    str
    children_en:    str
    children_cn:    str
    career_en:      str
    career_cn:      str
    general_en:     str
    general_cn:     str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "longevity_en": self.longevity_en,
            "longevity_cn": self.longevity_cn,
            "marriage_en": self.marriage_en,
            "marriage_cn": self.marriage_cn,
            "children_en": self.children_en,
            "children_cn": self.children_cn,
            "career_en": self.career_en,
            "career_cn": self.career_cn,
            "general_en": self.general_en,
            "general_cn": self.general_cn,
        }


@dataclass
class DeepSassanianChart:
    """Complete advanced Sassanian chart result."""
    # Birth data
    year:       int
    month:      int
    day:        int
    hour:       int
    minute:     int
    latitude:   float
    longitude:  float
    timezone:   float

    # Chart fundamentals
    julian_day: float
    ascendant:  float
    midheaven:  float
    asc_sign:   str
    asc_sign_cn: str
    is_day_chart: bool

    # Planet positions
    planets:    List[DeepPlanetPos]

    # Houses (whole sign — cusps are just sign starts)
    houses:     List[float]   # 12 whole-sign cusps

    # Techniques
    firdaria:          List[DeepFirdarPeriod]
    current_firdaria:  Optional[DeepFirdarPeriod]
    current_sub:       Optional[DeepFirdarSubPeriod]

    hyleg:     Optional[DeepHylegResult]
    alcocoden: Optional[DeepAlcocodenResult]
    almuten:   Optional[DeepAlmutenResult]

    annual_profections:  List[DeepProfectionYear]
    monthly_profections: List[DeepProfectionYear]
    current_annual_prof: Optional[DeepProfectionYear]
    current_monthly_prof: Optional[DeepProfectionYear]

    arabic_parts: List[DeepArabicPart]
    royal_stars:  List[DeepRoyalStar]
    triplicity_lords: List[TriplicityInfo]
    dorotheus:    Optional[DorotheusSummary]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year": self.year, "month": self.month, "day": self.day,
            "hour": self.hour, "minute": self.minute,
            "latitude": self.latitude, "longitude": self.longitude,
            "timezone": self.timezone,
            "julian_day": self.julian_day,
            "ascendant": self.ascendant, "midheaven": self.midheaven,
            "asc_sign": self.asc_sign, "asc_sign_cn": self.asc_sign_cn,
            "is_day_chart": self.is_day_chart,
            "planets": [p.to_dict() for p in self.planets],
            "houses": self.houses,
            "firdaria": [f.to_dict() for f in self.firdaria],
            "current_firdaria": self.current_firdaria.to_dict() if self.current_firdaria else None,
            "current_sub": self.current_sub.to_dict() if self.current_sub else None,
            "hyleg": self.hyleg.to_dict() if self.hyleg else None,
            "alcocoden": self.alcocoden.to_dict() if self.alcocoden else None,
            "almuten": self.almuten.to_dict() if self.almuten else None,
            "annual_profections": [p.to_dict() for p in self.annual_profections],
            "monthly_profections": [p.to_dict() for p in self.monthly_profections],
            "current_annual_prof": self.current_annual_prof.to_dict() if self.current_annual_prof else None,
            "current_monthly_prof": self.current_monthly_prof.to_dict() if self.current_monthly_prof else None,
            "arabic_parts": [a.to_dict() for a in self.arabic_parts],
            "royal_stars": [r.to_dict() for r in self.royal_stars],
            "triplicity_lords": [tl.to_dict() for tl in self.triplicity_lords],
            "dorotheus": self.dorotheus.to_dict() if self.dorotheus else None,
        }


# ─────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────

def _norm(lon: float) -> float:
    """Normalize longitude to [0, 360)."""
    return lon % 360.0


def _sign_from_lon(lon: float) -> Tuple[str, str, str, int, float]:
    """Return (sign_name, sign_cn, sign_glyph, sign_index 0-11, degree_in_sign)."""
    idx = int(lon // 30) % 12
    deg = lon % 30
    s = ZODIAC_SIGNS[idx]
    return s[0], s[2], s[1], idx, deg


def _jd_to_date_str(jd: float) -> str:
    """Convert Julian Day to YYYY-MM-DD string."""
    year, month, day, _ = swe.revjul(jd, swe.GREG_CAL)
    return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"


def _jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Day to Python datetime."""
    year, month, day, hour_frac = swe.revjul(jd, swe.GREG_CAL)
    h = int(hour_frac)
    m = int((hour_frac - h) * 60)
    return datetime(int(year), int(month), int(day), h, m)


def _now_jd() -> float:
    """Current Julian Day."""
    n = datetime.utcnow()
    return swe.julday(n.year, n.month, n.day, n.hour + n.minute / 60.0)


def _get_dignity(
    planet_name: str,
    sign: str,
    degree: float,
    is_day: bool,
) -> Tuple[str, str, float]:
    """
    Calculate planet dignity and score.
    Returns (dignity_en, dignity_cn, score).
    Score mapping: Domicile=5, Exaltation=4, Triplicity=3, Bound=2, Face=1,
                   Detriment=-5, Fall=-4, Peregrine=0
    """
    dom = DOMICILE.get(sign, "")
    exalt = EXALTATION.get(sign, "")
    det = DETRIMENT.get(sign, "")
    fall_planet = FALL.get(sign, "")
    element = ELEMENT_OF_SIGN.get(sign, "Fire")
    trip = TRIPLICITY_LORDS.get(element, ("", "", ""))
    trip_lord = trip[0] if is_day else trip[1]

    # Egyptian bound
    bounds = EGYPTIAN_BOUNDS.get(sign, [])
    bound_lord = ""
    for planet, start, end in bounds:
        if start <= degree < end:
            bound_lord = planet
            break

    # Decan ruler — clamp to [0, 2] to guard against floating-point edge at 30°
    decan_idx = _SIGN_INDEX.get(sign, 0) * 3 + min(int(degree // 10), 2)
    decan_lord = DECAN_RULERS[decan_idx % 36]

    if planet_name == dom:
        return "Domicile", "廟", 5.0
    if planet_name == det:
        return "Detriment", "陷", -5.0
    if planet_name == fall_planet:
        return "Fall", "弱", -4.0
    if planet_name == exalt:
        return "Exaltation", "旺", 4.0
    if planet_name == trip_lord:
        return "Triplicity", "三分", 3.0
    if planet_name == bound_lord:
        return "Bound (Egyptian)", "界", 2.0
    if planet_name == decan_lord:
        return "Face (Decan)", "面", 1.0
    return "Peregrine", "無尊嚴", 0.0


def _get_dignity_score_full(
    planet_name: str,
    sign: str,
    degree: float,
    is_day: bool,
) -> float:
    """Calculate cumulative dignity score for Almuten calculation."""
    dom = DOMICILE.get(sign, "")
    exalt = EXALTATION.get(sign, "")
    element = ELEMENT_OF_SIGN.get(sign, "Fire")
    trip = TRIPLICITY_LORDS.get(element, ("", "", ""))
    trip_day, trip_night, trip_part = trip
    active_trip = trip_day if is_day else trip_night

    bounds = EGYPTIAN_BOUNDS.get(sign, [])
    bound_lord = ""
    for planet, start, end in bounds:
        if start <= degree < end:
            bound_lord = planet
            break

    decan_idx = _SIGN_INDEX.get(sign, 0) * 3 + min(int(degree // 10), 2)
    decan_lord = DECAN_RULERS[decan_idx % 36]

    score = 0.0
    if planet_name == dom:         score += 5.0
    if planet_name == exalt:       score += 4.0
    if planet_name == active_trip: score += 3.0
    if planet_name == trip_part:   score += 1.5   # participating lord partial
    if planet_name == bound_lord:  score += 2.0
    if planet_name == decan_lord:  score += 1.0
    return score


def _antiscion(lon: float) -> float:
    """
    Antiscion: reflection over the Cancer/Capricorn solstice axis.
    The solstice axis runs through 0° Cancer (90°) and 0° Capricorn (270°).
    Formula: antiscion = (180° - lon) mod 360°
    """
    return _norm(180.0 - lon)


def _contra_antiscion(lon: float) -> float:
    """
    Contra-antiscion: reflection over the Aries/Libra equinox axis.
    Formula: contra-antiscion = (360° - lon) mod 360°  = -lon mod 360°
    """
    return _norm(360.0 - lon)


def _dodecatemoria(lon: float) -> float:
    """
    Dodecatemoria (12th part): each degree in a sign expanded × 12.
    Formula: (sign_index × 30 + degree_in_sign × 12) mod 360°
    """
    degree_in_sign = lon % 30
    sign_index = int(lon // 30) % 12
    return _norm(sign_index * 30 + degree_in_sign * 12)


def _get_sign_lord(sign: str) -> str:
    """Return the domicile lord of a sign."""
    return DOMICILE.get(sign, "Sun")


def _whole_sign_house(planet_lon: float, asc_lon: float) -> int:
    """
    Whole Sign house number (1-12).
    In Whole Sign, the house is determined by how many signs the planet is
    from the sign containing the Ascendant.
    """
    asc_sign_idx = int(asc_lon // 30) % 12
    planet_sign_idx = int(planet_lon // 30) % 12
    house = (planet_sign_idx - asc_sign_idx) % 12 + 1
    return house


# ─────────────────────────────────────────────────────────────
# Core Calculation Functions
# ─────────────────────────────────────────────────────────────

def _compute_planets(jd: float, asc: float, is_day: bool) -> List[DeepPlanetPos]:
    """Compute all planet positions with full dignity analysis."""
    positions = []
    sign_names = [z[0] for z in ZODIAC_SIGNS]

    for pname, pid in _PLANET_IDS.items():
        calc_result = swe.calc(jd, pid, swe.FLG_SPEED)
        lon = _norm(calc_result[0][0])
        lat = calc_result[0][1]
        speed = calc_result[0][3]
        is_retro = speed < 0.0

        sign, sign_cn, sign_glyph, sign_idx, deg_in_sign = _sign_from_lon(lon)
        house = _whole_sign_house(lon, asc)

        dignity_en, dignity_cn, d_score = _get_dignity(pname, sign, deg_in_sign, is_day)

        # Triplicity lords for this planet's sign
        element = ELEMENT_OF_SIGN.get(sign, "Fire")
        trip = TRIPLICITY_LORDS.get(element, ("", "", ""))

        # Egyptian bound lord
        bounds = EGYPTIAN_BOUNDS.get(sign, [])
        bound_lord = ""
        for planet, start, end in bounds:
            if start <= deg_in_sign < end:
                bound_lord = planet
                break

        # Decan lord — clamp to [0, 2] to guard against floating-point edge at 30°
        decan_idx = sign_idx * 3 + min(int(deg_in_sign // 10), 2)
        decan_lord = DECAN_RULERS[decan_idx % 36]

        # Sect
        in_sect = False
        if is_day and pname in DIURNAL_PLANETS:
            in_sect = True
        elif not is_day and pname in NOCTURNAL_PLANETS:
            in_sect = True
        elif pname == "Mercury":
            # Mercury joins the sect of the chart
            in_sect = True

        # Antiscia and Contra-antiscia
        ant_lon = _antiscion(lon)
        cant_lon = _contra_antiscion(lon)
        ant_sign, _, _, _, _ = _sign_from_lon(ant_lon)
        cant_sign, _, _, _, _ = _sign_from_lon(cant_lon)

        # Dodecatemoria
        dodec_lon = _dodecatemoria(lon)
        dodec_sign, dodec_sign_cn, _, _, _ = _sign_from_lon(dodec_lon)

        positions.append(DeepPlanetPos(
            name=pname,
            name_cn=PLANET_NAMES_CN.get(pname, pname),
            glyph=PLANET_GLYPHS.get(pname, "?"),
            longitude=lon,
            latitude=lat,
            speed=speed,
            sign=sign,
            sign_cn=sign_cn,
            sign_index=sign_idx,
            sign_glyph=sign_glyph,
            degree_in_sign=deg_in_sign,
            house=house,
            is_retrograde=is_retro,
            dignity=dignity_en,
            dignity_cn=dignity_cn,
            dignity_score=d_score,
            domicile_lord=DOMICILE.get(sign, ""),
            exalt_lord=EXALTATION.get(sign, ""),
            triplicity_day_lord=trip[0],
            triplicity_night_lord=trip[1],
            triplicity_part_lord=trip[2],
            egyptian_bound_lord=bound_lord,
            decan_lord=decan_lord,
            is_in_sect=in_sect,
            antiscion_longitude=ant_lon,
            contra_antiscion_longitude=cant_lon,
            antiscion_sign=ant_sign,
            contra_antiscion_sign=cant_sign,
            dodecatemoria_longitude=dodec_lon,
            dodecatemoria_sign=dodec_sign,
            dodecatemoria_sign_cn=dodec_sign_cn,
        ))

    return positions


def _compute_firdaria(
    birth_jd: float,
    is_day: bool,
    now_jd: float,
    num_cycles: int = 2,
) -> Tuple[List[DeepFirdarPeriod], Optional[DeepFirdarPeriod], Optional[DeepFirdarSubPeriod]]:
    """
    Compute Firdaria periods with correct traditional years and sequences.

    Day chart:   Sun(10)→Venus(8)→Mercury(13)→Moon(9)→Saturn(11)→Jupiter(12)→Mars(7)→Node(5)
    Night chart: Moon(9)→Saturn(11)→Jupiter(12)→Mars(7)→Sun(10)→Venus(8)→Mercury(13)→Node(5)

    Sub-periods divide each major period among the same 7 planets proportionally.
    """
    order = FIRDARIA_DAY_ORDER if is_day else FIRDARIA_NIGHT_ORDER

    current_firdaria = None
    current_sub = None
    all_periods: List[DeepFirdarPeriod] = []
    cur_jd = birth_jd

    for cycle in range(num_cycles):
        for major_lord in order:
            major_years = FIRDARIA_YEARS.get(major_lord, 0)
            if major_years == 0:
                continue
            end_jd = cur_jd + major_years * 365.25
            is_current_major = cur_jd <= now_jd < end_jd

            # Sub-periods: rotate 7 classical planets starting at major lord
            # Nodes don't have sub-periods in the same way
            if major_lord in ("North Node", "South Node"):
                sub_periods: List[DeepFirdarSubPeriod] = []
            else:
                sub_seven = FIRDARIA_SUBPERIOD_PLANETS
                start_idx = sub_seven.index(major_lord) if major_lord in sub_seven else 0
                rotated = sub_seven[start_idx:] + sub_seven[:start_idx]
                total_major_days = major_years * 365.25
                sub_cur_jd = cur_jd
                sub_periods = []
                for sub_lord in rotated:
                    sub_years = FIRDARIA_YEARS.get(sub_lord, 10) / 75.0 * major_years
                    sub_end_jd = sub_cur_jd + sub_years * 365.25
                    is_current_sub = is_current_major and sub_cur_jd <= now_jd < sub_end_jd

                    sp = DeepFirdarSubPeriod(
                        major_lord=major_lord,
                        sub_lord=sub_lord,
                        sub_lord_cn=PLANET_NAMES_CN.get(sub_lord, sub_lord),
                        sub_glyph=PLANET_GLYPHS.get(sub_lord, "?"),
                        start_date=_jd_to_date_str(sub_cur_jd),
                        end_date=_jd_to_date_str(sub_end_jd),
                        duration_years=sub_years,
                        is_current=is_current_sub,
                    )
                    sub_periods.append(sp)
                    if is_current_sub and current_sub is None:
                        current_sub = sp
                    sub_cur_jd = sub_end_jd

            major_period = DeepFirdarPeriod(
                major_lord=major_lord,
                major_lord_cn=PLANET_NAMES_CN.get(major_lord, major_lord),
                major_glyph=PLANET_GLYPHS.get(major_lord, "?"),
                start_jd=cur_jd,
                end_jd=end_jd,
                start_date=_jd_to_date_str(cur_jd),
                end_date=_jd_to_date_str(end_jd),
                duration_years=float(major_years),
                is_current=is_current_major,
                sub_periods=sub_periods,
            )
            all_periods.append(major_period)
            if is_current_major and current_firdaria is None:
                current_firdaria = major_period

            cur_jd = end_jd

    return all_periods, current_firdaria, current_sub


def _compute_hyleg_alcocoden(
    planets: List[DeepPlanetPos],
    asc: float,
    mc: float,
    is_day: bool,
) -> Tuple[Optional[DeepHylegResult], Optional[DeepAlcocodenResult]]:
    """
    Compute Hyleg (Giver of Life) and Alcocoden (Giver of Years).

    Hyleg determination (following Ptolemy / Dorotheus):
    - Day chart: prefer Sun if in houses 1,7,9,10,11
    - Night chart: prefer Moon if in houses 1,7,9,10,11
    - Otherwise try Part of Fortune, then Ascendant

    Alcocoden: planet with most dignities at Hyleg's position.
    """
    sun = next((p for p in planets if p.name == "Sun"), None)
    moon = next((p for p in planets if p.name == "Moon"), None)

    # Part of Fortune
    if sun and moon:
        pof_lon = _norm(asc + moon.longitude - sun.longitude) if is_day \
                  else _norm(asc + sun.longitude - moon.longitude)
    else:
        pof_lon = asc

    pof_sign, pof_sign_cn, pof_glyph, pof_idx, pof_deg = _sign_from_lon(pof_lon)
    pof_house = _whole_sign_house(pof_lon, asc)

    # Hylegical houses (places of life)
    HYLEG_HOUSES = {1, 7, 9, 10, 11}

    hyleg: Optional[DeepHylegResult] = None

    if is_day and sun and sun.house in HYLEG_HOUSES:
        hyleg = DeepHylegResult(
            hyleg_planet="Sun",
            hyleg_cn="太陽",
            hyleg_glyph="☉",
            longitude=sun.longitude,
            sign=sun.sign,
            sign_cn=sun.sign_cn,
            degree=sun.degree_in_sign,
            house=sun.house,
            is_valid=True,
            method="sun_day",
            reason_en=f"Day chart; Sun in house {sun.house} (hylegical place)",
            reason_cn=f"日間盤；太陽在第{sun.house}宮（生命宮位）",
        )

    if hyleg is None and not is_day and moon and moon.house in HYLEG_HOUSES:
        hyleg = DeepHylegResult(
            hyleg_planet="Moon",
            hyleg_cn="月亮",
            hyleg_glyph="☽",
            longitude=moon.longitude,
            sign=moon.sign,
            sign_cn=moon.sign_cn,
            degree=moon.degree_in_sign,
            house=moon.house,
            is_valid=True,
            method="moon_night",
            reason_en=f"Night chart; Moon in house {moon.house} (hylegical place)",
            reason_cn=f"夜間盤；月亮在第{moon.house}宮（生命宮位）",
        )

    # Try Part of Fortune
    if hyleg is None and pof_house in HYLEG_HOUSES:
        hyleg = DeepHylegResult(
            hyleg_planet="Part of Fortune",
            hyleg_cn="幸運點",
            hyleg_glyph="⊕",
            longitude=pof_lon,
            sign=pof_sign,
            sign_cn=pof_sign_cn,
            degree=pof_deg,
            house=pof_house,
            is_valid=True,
            method="lot_fortune",
            reason_en=f"Part of Fortune in house {pof_house} (hylegical place)",
            reason_cn=f"幸運點在第{pof_house}宮（生命宮位）",
        )

    # Fallback: Ascendant
    if hyleg is None:
        asc_sign, asc_sign_cn, asc_glyph, asc_idx, asc_deg = _sign_from_lon(asc)
        hyleg = DeepHylegResult(
            hyleg_planet="Ascendant",
            hyleg_cn="上升點",
            hyleg_glyph="AC",
            longitude=asc,
            sign=asc_sign,
            sign_cn=asc_sign_cn,
            degree=asc_deg,
            house=1,
            is_valid=True,
            method="ascendant",
            reason_en="Default Hyleg: Ascendant (no primary Hyleg found in hylegical places)",
            reason_cn="預設生命點：上升點（在生命宮位中未找到主要生命給予者）",
        )

    # Alcocoden: find planet with highest dignity score at Hyleg position
    hyleg_sign, _, _, _, hyleg_deg = _sign_from_lon(hyleg.longitude)
    scores: Dict[str, float] = {}
    for pname in _PLANET_IDS:
        scores[pname] = _get_dignity_score_full(pname, hyleg_sign, hyleg_deg, is_day)

    alco_lord = max(scores, key=scores.get)
    alco_score = scores[alco_lord]

    # Aspect modifiers to Alcocoden
    alco_planet = next((p for p in planets if p.name == alco_lord), None)
    modifiers = []
    mod_base = float(PLANETARY_MIDDLE_YEARS.get(alco_lord, 45))

    if alco_planet:
        for p in planets:
            if p.name == alco_lord:
                continue
            orb = abs(p.longitude - alco_planet.longitude)
            if orb > 180:
                orb = 360 - orb
            aspect = None
            if orb <= 2.0:
                aspect = "conjunction"
            elif abs(orb - 60) <= 4:
                aspect = "sextile"
            elif abs(orb - 90) <= 4:
                aspect = "square"
            elif abs(orb - 120) <= 4:
                aspect = "trine"
            elif abs(orb - 180) <= 4:
                aspect = "opposition"

            if aspect:
                cn_asp = {"conjunction":"合相","sextile":"六分相","square":"四分相","trine":"三分相","opposition":"對分相"}.get(aspect,"")
                if p.name in BENEFIC_PLANETS:
                    if aspect in ("trine", "sextile", "conjunction"):
                        mod_base *= 1.15
                        modifiers.append(f"{p.glyph} {p.name} {cn_asp} +15%")
                elif p.name in MALEFIC_PLANETS:
                    if aspect in ("square", "opposition"):
                        mod_base *= 0.85
                        modifiers.append(f"{p.glyph} {p.name} {cn_asp} -15%")
                    elif aspect == "conjunction":
                        mod_base *= 0.90
                        modifiers.append(f"{p.glyph} {p.name} {cn_asp} -10%")

    alcocoden = DeepAlcocodenResult(
        lord=alco_lord,
        lord_cn=PLANET_NAMES_CN.get(alco_lord, alco_lord),
        lord_glyph=PLANET_GLYPHS.get(alco_lord, "?"),
        base_years_major=PLANETARY_MAJOR_YEARS.get(alco_lord, 57),
        base_years_minor=PLANETARY_MINOR_YEARS.get(alco_lord, 30),
        base_years_middle=PLANETARY_MIDDLE_YEARS.get(alco_lord, 43),
        modified_years=round(mod_base, 1),
        aspect_modifiers=modifiers,
        final_range_min=float(PLANETARY_MINOR_YEARS.get(alco_lord, 20)),
        final_range_max=float(PLANETARY_MAJOR_YEARS.get(alco_lord, 80)),
        reason_en=f"{alco_lord} has the highest dignity score ({alco_score:.1f}) at Hyleg position {hyleg_sign} {hyleg_deg:.1f}°",
        reason_cn=f"{PLANET_NAMES_CN.get(alco_lord,alco_lord)}在生命點（{hyleg_sign} {hyleg_deg:.1f}°）的尊嚴分數最高（{alco_score:.1f}分）",
    )

    return hyleg, alcocoden


def _compute_almuten(
    planets: List[DeepPlanetPos],
    asc: float,
    mc: float,
    is_day: bool,
) -> DeepAlmutenResult:
    """
    Almuten Figuris: planet with highest cumulative dignity score
    across key chart points (Ascendant, MC, Sun, Moon, Part of Fortune).
    """
    sun = next((p for p in planets if p.name == "Sun"), None)
    moon = next((p for p in planets if p.name == "Moon"), None)

    pof_lon = asc  # default
    if sun and moon:
        pof_lon = _norm(asc + moon.longitude - sun.longitude) if is_day \
                  else _norm(asc + sun.longitude - moon.longitude)

    key_points = {
        "Ascendant (上升)":       asc,
        "Midheaven (天頂)":       mc,
        "Sun (太陽)":             sun.longitude if sun else asc,
        "Moon (月亮)":            moon.longitude if moon else asc,
        "Part of Fortune (幸運點)": pof_lon,
    }

    all_scores: Dict[str, float] = {p.name: 0.0 for p in planets}
    breakdown:  Dict[str, Dict[str, float]] = {p.name: {} for p in planets}

    for point_name, point_lon in key_points.items():
        p_sign, _, _, _, p_deg = _sign_from_lon(point_lon)
        for pname in _PLANET_IDS:
            sc = _get_dignity_score_full(pname, p_sign, p_deg, is_day)
            if sc != 0:
                all_scores[pname] += sc
                breakdown[pname][point_name] = sc

    best = max(all_scores, key=all_scores.get)
    best_score = all_scores[best]

    return DeepAlmutenResult(
        planet=best,
        planet_cn=PLANET_NAMES_CN.get(best, best),
        planet_glyph=PLANET_GLYPHS.get(best, "?"),
        total_score=best_score,
        all_scores=all_scores,
        breakdown=breakdown.get(best, {}),
        reason_en=(
            f"{best} accumulates the highest total dignity score ({best_score:.1f}) "
            "across the five key chart points (Ascendant, MC, Sun, Moon, Part of Fortune)."
        ),
        reason_cn=(
            f"{PLANET_NAMES_CN.get(best,best)}在五個關鍵點（上升、天頂、太陽、月亮、幸運點）"
            f"中積累了最高的尊嚴總分（{best_score:.1f}分）。"
        ),
    )


def _compute_profections(
    birth_jd: float,
    asc: float,
    now_jd: float,
    num_years: int = 80,
) -> Tuple[List[DeepProfectionYear], List[DeepProfectionYear],
           Optional[DeepProfectionYear], Optional[DeepProfectionYear]]:
    """
    Compute annual and monthly profections.

    Annual: each year the Ascendant moves forward one whole sign (30°/year).
    Monthly: each month the Ascendant moves forward 2.5° (30°/12 months).

    Returns (annual_list, monthly_list, current_annual, current_monthly).
    """
    sign_list = [z[0] for z in ZODIAC_SIGNS]
    asc_sign_idx = int(asc // 30) % 12

    annual: List[DeepProfectionYear] = []
    monthly: List[DeepProfectionYear] = []
    current_annual: Optional[DeepProfectionYear] = None
    current_monthly: Optional[DeepProfectionYear] = None

    now_dt = _jd_to_datetime(now_jd)

    for age in range(num_years):
        # Annual: one sign per year
        annual_sign_idx = (asc_sign_idx + age) % 12
        sign_data = ZODIAC_SIGNS[annual_sign_idx]
        sign_name = sign_data[0]
        sign_cn = sign_data[2]
        sign_glyph = sign_data[1]
        lord = DOMICILE.get(sign_name, "Sun")

        year_start_jd = birth_jd + age * 365.25
        year_end_jd   = birth_jd + (age + 1) * 365.25
        house_activated = age % 12 + 1
        sig = HOUSE_SIGNIFICATIONS.get(house_activated, {"en": "", "cn": ""})
        is_cur = year_start_jd <= now_jd < year_end_jd

        prof = DeepProfectionYear(
            period_type="annual",
            age=age,
            month=None,
            sign=sign_name,
            sign_cn=sign_cn,
            sign_index=annual_sign_idx,
            sign_glyph=sign_glyph,
            lord=lord,
            lord_cn=PLANET_NAMES_CN.get(lord, lord),
            lord_glyph=PLANET_GLYPHS.get(lord, "?"),
            start_date=_jd_to_date_str(year_start_jd),
            end_date=_jd_to_date_str(year_end_jd),
            house_activated=house_activated,
            signification_en=sig["en"],
            signification_cn=sig["cn"],
            is_current=is_cur,
        )
        annual.append(prof)
        if is_cur:
            current_annual = prof

            # Monthly profections within this year
            for m in range(12):
                monthly_sign_idx = (annual_sign_idx + m) % 12
                m_data = ZODIAC_SIGNS[monthly_sign_idx]
                m_sign = m_data[0]
                m_sign_cn = m_data[2]
                m_glyph = m_data[1]
                m_lord = DOMICILE.get(m_sign, "Sun")
                m_house = (m % 12) + 1
                m_start_jd = year_start_jd + m * (365.25 / 12)
                m_end_jd   = year_start_jd + (m + 1) * (365.25 / 12)
                m_sig = HOUSE_SIGNIFICATIONS.get((annual_sign_idx + m) % 12 + 1, {"en": "", "cn": ""})
                m_is_cur = m_start_jd <= now_jd < m_end_jd

                mp = DeepProfectionYear(
                    period_type="monthly",
                    age=age,
                    month=m + 1,
                    sign=m_sign,
                    sign_cn=m_sign_cn,
                    sign_index=monthly_sign_idx,
                    sign_glyph=m_glyph,
                    lord=m_lord,
                    lord_cn=PLANET_NAMES_CN.get(m_lord, m_lord),
                    lord_glyph=PLANET_GLYPHS.get(m_lord, "?"),
                    start_date=_jd_to_date_str(m_start_jd),
                    end_date=_jd_to_date_str(m_end_jd),
                    house_activated=(annual_sign_idx + m) % 12 + 1,
                    signification_en=m_sig["en"],
                    signification_cn=m_sig["cn"],
                    is_current=m_is_cur,
                )
                monthly.append(mp)
                if m_is_cur:
                    current_monthly = mp

    return annual, monthly, current_annual, current_monthly


def _compute_arabic_parts(
    planets: List[DeepPlanetPos],
    asc: float,
    houses: List[float],
    is_day: bool,
) -> List[DeepArabicPart]:
    """Compute extended Arabic Parts / Persian Lots."""
    pmap = {p.name: p.longitude for p in planets}
    sun_lon = pmap.get("Sun", 0.0)
    moon_lon = pmap.get("Moon", 0.0)
    mer_lon  = pmap.get("Mercury", 0.0)
    ven_lon  = pmap.get("Venus", 0.0)
    mar_lon  = pmap.get("Mars", 0.0)
    jup_lon  = pmap.get("Jupiter", 0.0)
    sat_lon  = pmap.get("Saturn", 0.0)

    cusp8 = houses[7] if len(houses) > 7 else asc

    # Part of Fortune longitude
    pof = _norm(asc + moon_lon - sun_lon) if is_day else _norm(asc + sun_lon - moon_lon)
    pos = _norm(asc + sun_lon - moon_lon) if is_day else _norm(asc + moon_lon - sun_lon)

    def _lot(a: float, b: float, reverse: bool = False) -> float:
        if reverse:
            return _norm(asc + b - a)
        return _norm(asc + a - b)

    exalt_19aries = 19.0  # 19° Aries

    formulas = [
        # (name_en, name_cn, name_arabic, day_lon, night_lon)
        ("Part of Fortune",      "幸運點",          "سهم السعادة",
         _norm(asc + moon_lon - sun_lon), _norm(asc + sun_lon - moon_lon)),
        ("Part of Spirit",       "精神點",          "سهم الروح",
         _norm(asc + sun_lon - moon_lon), _norm(asc + moon_lon - sun_lon)),
        ("Part of Marriage (Venus)", "婚姻點（金星）", "سهم الزواج",
         _lot(ven_lon, sun_lon), _lot(sun_lon, ven_lon)),
        ("Part of Marriage (Saturn)", "婚姻點（土星）","سهم الزواج (زحل)",
         _lot(sat_lon, ven_lon), _lot(ven_lon, sat_lon)),
        ("Part of Children",     "子女點",          "سهم الأولاد",
         _lot(jup_lon, sat_lon), _lot(sat_lon, jup_lon)),
        ("Part of Father",       "父親點",          "سهم الأب",
         _lot(sun_lon, sat_lon), _lot(sat_lon, sun_lon)),
        ("Part of Mother",       "母親點",          "سهم الأم",
         _lot(moon_lon, ven_lon), _lot(ven_lon, moon_lon)),
        ("Part of Siblings",     "兄弟點",          "سهم الإخوة",
         _lot(jup_lon, sat_lon), _lot(sat_lon, jup_lon)),
        ("Part of Illness",      "疾病點",          "سهم المرض",
         _lot(mar_lon, sat_lon), _lot(sat_lon, mar_lon)),
        ("Part of Career",       "職業點",          "سهم العمل",
         _lot(mer_lon, sun_lon), _lot(sun_lon, mer_lon)),
        ("Part of Travel",       "旅行點",          "سهم السفر",
         _lot(jup_lon, moon_lon), _lot(moon_lon, jup_lon)),
        ("Part of Death",        "死亡點",          "سهم الموت",
         _lot(cusp8, moon_lon), _lot(moon_lon, cusp8)),
        ("Part of Exaltation",   "尊貴點",          "سهم الشرف",
         _lot(exalt_19aries, sun_lon), _lot(sun_lon, exalt_19aries)),
        ("Part of Basis",        "基礎點",          "سهم الأساس",
         _lot(pof, pos), _lot(pos, pof)),
    ]

    results: List[DeepArabicPart] = []
    for name_en, name_cn, name_ar, day_lon, night_lon in formulas:
        lot_lon = day_lon if is_day else night_lon
        lot_lon = _norm(lot_lon)
        lot_sign, lot_sign_cn, lot_glyph, _, lot_deg = _sign_from_lon(lot_lon)
        lot_house = _whole_sign_house(lot_lon, asc)
        lot_lord = DOMICILE.get(lot_sign, "Sun")

        results.append(DeepArabicPart(
            name_en=name_en,
            name_cn=name_cn,
            name_arabic=name_ar,
            longitude=lot_lon,
            sign=lot_sign,
            sign_cn=lot_sign_cn,
            sign_glyph=lot_glyph,
            degree=lot_deg,
            house=lot_house,
            lord=lot_lord,
            lord_cn=PLANET_NAMES_CN.get(lot_lord, lot_lord),
            lord_glyph=PLANET_GLYPHS.get(lot_lord, "?"),
            formula_used=f"{'Day' if is_day else 'Night'}: ASC + A − B",
        ))

    return results


def _compute_royal_stars(
    planets: List[DeepPlanetPos],
    asc: float,
) -> List[DeepRoyalStar]:
    """Check which royal stars are conjunct planets or angles."""
    results: List[DeepRoyalStar] = []

    # Include Ascendant as a point to check
    points = {p.name: p.longitude for p in planets}
    points["Ascendant"] = asc

    for star_name, star_data in ROYAL_STARS.items():
        star_lon = star_data["longitude"]
        orb_limit = star_data["orb"]
        best_orb = orb_limit + 1
        best_planet = None

        for pname, plon in points.items():
            orb = abs(plon - star_lon)
            if orb > 180:
                orb = 360 - orb
            if orb <= orb_limit and orb < best_orb:
                best_orb = orb
                best_planet = pname

        is_prominent = best_planet is not None

        results.append(DeepRoyalStar(
            star_name=star_name,
            star_name_cn=star_data["name_cn"],
            star_pahlavi=star_data["name_pahlavi"],
            star_longitude=star_lon,
            guardian=star_data["guardian"],
            conjunction_planet=best_planet if is_prominent else None,
            conjunction_planet_cn=PLANET_NAMES_CN.get(best_planet, best_planet) if is_prominent and best_planet != "Ascendant" else ("上升點" if best_planet == "Ascendant" else None),
            conjunction_glyph=PLANET_GLYPHS.get(best_planet, "AC") if is_prominent and best_planet else None,
            orb=round(best_orb, 2) if is_prominent else 0.0,
            is_prominent=is_prominent,
            meaning_en=star_data["meaning_en"],
            meaning_cn=star_data["meaning_cn"],
        ))

    return results


def _compute_triplicity_lords(is_day: bool) -> List[TriplicityInfo]:
    """Compute triplicity lords for each element."""
    element_signs = {
        "Fire":  (["Aries", "Leo", "Sagittarius"],  "火象"),
        "Earth": (["Taurus", "Virgo", "Capricorn"],  "土象"),
        "Air":   (["Gemini", "Libra", "Aquarius"],   "風象"),
        "Water": (["Cancer", "Scorpio", "Pisces"],   "水象"),
    }

    results: List[TriplicityInfo] = []
    for element, (signs, element_cn) in element_signs.items():
        trip = TRIPLICITY_LORDS.get(element, ("Sun", "Moon", "Saturn"))
        day_lord, night_lord, part_lord = trip
        active = day_lord if is_day else night_lord

        results.append(TriplicityInfo(
            element=element,
            element_cn=element_cn,
            signs=signs,
            day_lord=day_lord,
            day_lord_cn=PLANET_NAMES_CN.get(day_lord, day_lord),
            night_lord=night_lord,
            night_lord_cn=PLANET_NAMES_CN.get(night_lord, night_lord),
            part_lord=part_lord,
            part_lord_cn=PLANET_NAMES_CN.get(part_lord, part_lord),
            active_lord=active,
        ))

    return results


def _compute_dorotheus(
    planets: List[DeepPlanetPos],
    asc: float,
    is_day: bool,
    hyleg: Optional[DeepHylegResult],
    alcocoden: Optional[DeepAlcocodenResult],
) -> DorotheusSummary:
    """
    Generate Dorotheus-style life topic interpretations.
    Based on Carmen Astrologicum (Dorotheus of Sidon) and Pahlavi tradition.
    """
    interp = DOROTHEUS_INTERPRETATIONS

    # Longevity: based on Hyleg/Alcocoden and their condition
    hyleg_name = hyleg.hyleg_planet if hyleg else "Sun"
    alco_name  = alcocoden.lord if alcocoden else "Sun"
    alco_planet = next((p for p in planets if p.name == alco_name), None)

    lon_key_en = lon_key_cn = ""
    if alco_planet:
        if alco_planet.dignity in ("Domicile", "Exaltation"):
            lon_key_en = interp["longevity"].get(f"{alco_name}_dignified_en", interp["longevity"].get("Jupiter_dignified_en", ""))
            lon_key_cn = interp["longevity"].get(f"{alco_name}_dignified_cn", interp["longevity"].get("Jupiter_dignified_cn", ""))
        else:
            lon_key_en = interp["longevity"].get(f"{alco_name}_afflicted_en", interp["longevity"].get("Saturn_afflicted_en", ""))
            lon_key_cn = interp["longevity"].get(f"{alco_name}_afflicted_cn", interp["longevity"].get("Saturn_afflicted_cn", ""))
    if not lon_key_en:
        lon_key_en = interp["longevity"].get("Jupiter_dignified_en", "")
        lon_key_cn = interp["longevity"].get("Jupiter_dignified_cn", "")

    # Marriage: Venus and 7th house
    venus = next((p for p in planets if p.name == "Venus"), None)
    h7_planets = [p for p in planets if p.house == 7]
    mar_en = mar_cn = ""
    if venus:
        if venus.dignity in ("Domicile", "Exaltation"):
            mar_en = interp["marriage"].get("Venus_dignified_en", "")
            mar_cn = interp["marriage"].get("Venus_dignified_cn", "")
        else:
            mar_en = interp["marriage"].get("Venus_afflicted_en", "")
            mar_cn = interp["marriage"].get("Venus_afflicted_cn", "")
    for p7 in h7_planets:
        if p7.name in ("Saturn", "Mars", "Jupiter", "Moon"):
            key_e = f"{p7.name}_in_7th_en"
            key_c = f"{p7.name}_in_7th_cn"
            add_e = interp["marriage"].get(key_e, "")
            add_c = interp["marriage"].get(key_c, "")
            if add_e:
                mar_en = (mar_en + " " + add_e).strip()
                mar_cn = (mar_cn + " " + add_c).strip()

    # Children: Jupiter and 5th house
    jupiter = next((p for p in planets if p.name == "Jupiter"), None)
    h5_planets = [p for p in planets if p.house == 5]
    chi_en = chi_cn = ""
    if jupiter and jupiter.dignity in ("Domicile", "Exaltation"):
        chi_en = interp["children"].get("Jupiter_dignified_en", "")
        chi_cn = interp["children"].get("Jupiter_dignified_cn", "")
    for p5 in h5_planets:
        if p5.name in ("Saturn", "Mars", "Venus", "Moon"):
            key_e = f"{p5.name}_in_5th_en"
            key_c = f"{p5.name}_in_5th_cn"
            add_e = interp["children"].get(key_e, "")
            add_c = interp["children"].get(key_c, "")
            if add_e:
                chi_en = (chi_en + " " + add_e).strip()
                chi_cn = (chi_cn + " " + add_c).strip()
    if not chi_en:
        chi_en = interp["children"].get("Jupiter_dignified_en", "")
        chi_cn = interp["children"].get("Jupiter_dignified_cn", "")

    # Career: 10th house planets
    h10_planets = [p for p in planets if p.house == 10]
    car_en = car_cn = ""
    for p10 in h10_planets:
        key_e = f"{p10.name}_in_10th_en"
        key_c = f"{p10.name}_in_10th_cn"
        add_e = interp["career"].get(key_e, "")
        add_c = interp["career"].get(key_c, "")
        if add_e:
            car_en = (car_en + " " + add_e).strip()
            car_cn = (car_cn + " " + add_c).strip()
    if not car_en:
        # Use domicile lord of MC
        mc_planet = next((p for p in planets if p.house == 10), None)
        car_en = interp["career"].get("Sun_in_10th_en", "")
        car_cn = interp["career"].get("Sun_in_10th_cn", "")

    # General
    gen_key = "day_chart" if is_day else "night_chart"
    gen_en = interp["general"].get(f"{gen_key}_en", "")
    gen_cn = interp["general"].get(f"{gen_key}_cn", "")

    dignified_count = sum(1 for p in planets if p.dignity in ("Domicile", "Exaltation"))
    if dignified_count >= 3:
        gen_en += " " + interp["general"].get("many_dignified_en", "")
        gen_cn += " " + interp["general"].get("many_dignified_cn", "")
    elif dignified_count == 0:
        afflicted = sum(1 for p in planets if p.dignity in ("Detriment", "Fall"))
        if afflicted >= 3:
            gen_en += " " + interp["general"].get("many_afflicted_en", "")
            gen_cn += " " + interp["general"].get("many_afflicted_cn", "")

    return DorotheusSummary(
        longevity_en=lon_key_en.strip() or "Analysis requires chart assessment.",
        longevity_cn=lon_key_cn.strip() or "需要星盤評估。",
        marriage_en=mar_en.strip() or "Venus placement guides marriage prospects.",
        marriage_cn=mar_cn.strip() or "金星位置指引婚姻前景。",
        children_en=chi_en.strip() or "Jupiter placement guides children prospects.",
        children_cn=chi_cn.strip() or "木星位置指引子女前景。",
        career_en=car_en.strip() or "10th house planets describe career themes.",
        career_cn=car_cn.strip() or "第十宮行星描述事業主題。",
        general_en=gen_en.strip(),
        general_cn=gen_cn.strip(),
    )


# ─────────────────────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────────────────────

def compute_deep_sassanian_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    latitude: float,
    longitude: float,
    timezone: float,
) -> DeepSassanianChart:
    """
    Compute a complete advanced Sassanian Persian astrological chart.

    Uses Whole Sign Houses throughout, corrected Firdaria sequences,
    full Egyptian bounds, Dodecatemoria, Antiscia, extended Arabic parts,
    and Dorotheus-style interpretations.

    Parameters
    ----------
    year, month, day, hour, minute : int
        Birth date and time (local).
    latitude, longitude : float
        Geographic coordinates.
    timezone : float
        UTC offset in hours (e.g., +8 for Asia/Taipei).

    Returns
    -------
    DeepSassanianChart
        Complete advanced chart result.
    """
    # Convert to UTC Julian Day
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)

    # Use tropical zodiac: do NOT pass swe.FLG_SIDEREAL in calc() calls

    # Compute Ascendant and MC via Placidus (for angles only)
    houses_data = swe.houses(jd, latitude, longitude, b'P')
    asc = houses_data[1][0]
    mc  = houses_data[1][2]

    # Whole Sign cusps: the ASC sign starts at 0° of its sign
    asc_sign_idx = int(asc // 30) % 12
    ws_houses = [float(s * 30) for s in range(asc_sign_idx, asc_sign_idx + 12)]
    ws_houses = [_norm(h) for h in ws_houses]

    asc_sign, asc_sign_cn, _, _, _ = _sign_from_lon(asc)

    # Determine day/night chart: Sun above horizon = day
    # In Whole Sign, houses 7-12 are above horizon (opposite sign from ASC side)
    sun_raw = swe.calc(jd, swe.SUN, swe.FLG_SPEED)
    sun_lon = _norm(sun_raw[0][0])
    sun_house = _whole_sign_house(sun_lon, asc)
    is_day = sun_house in {7, 8, 9, 10, 11, 12}

    # Compute planet positions
    planets = _compute_planets(jd, asc, is_day)

    now_jd = _now_jd()

    # Firdaria
    firdaria, current_firdaria, current_sub = _compute_firdaria(jd, is_day, now_jd)

    # Hyleg & Alcocoden
    hyleg, alcocoden = _compute_hyleg_alcocoden(planets, asc, mc, is_day)

    # Almuten
    almuten = _compute_almuten(planets, asc, mc, is_day)

    # Profections
    annual_profs, monthly_profs, cur_annual, cur_monthly = _compute_profections(
        jd, asc, now_jd
    )

    # Arabic Parts
    arabic_parts = _compute_arabic_parts(planets, asc, ws_houses, is_day)

    # Royal Stars
    royal_stars = _compute_royal_stars(planets, asc)

    # Triplicity Lords
    triplicity_lords = _compute_triplicity_lords(is_day)

    # Dorotheus interpretations
    dorotheus = _compute_dorotheus(planets, asc, is_day, hyleg, alcocoden)

    return DeepSassanianChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        latitude=latitude, longitude=longitude,
        timezone=timezone,
        julian_day=jd,
        ascendant=asc,
        midheaven=mc,
        asc_sign=asc_sign,
        asc_sign_cn=asc_sign_cn,
        is_day_chart=is_day,
        planets=planets,
        houses=ws_houses,
        firdaria=firdaria,
        current_firdaria=current_firdaria,
        current_sub=current_sub,
        hyleg=hyleg,
        alcocoden=alcocoden,
        almuten=almuten,
        annual_profections=annual_profs,
        monthly_profections=monthly_profs,
        current_annual_prof=cur_annual,
        current_monthly_prof=cur_monthly,
        arabic_parts=arabic_parts,
        royal_stars=royal_stars,
        triplicity_lords=triplicity_lords,
        dorotheus=dorotheus,
    )
