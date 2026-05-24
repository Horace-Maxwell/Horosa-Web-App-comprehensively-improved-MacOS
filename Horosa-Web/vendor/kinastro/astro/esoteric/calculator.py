"""
astro/esoteric/calculator.py — Alice Bailey 七道光線分析引擎

核心演算依據：
  - Alice A. Bailey, *Esoteric Astrology* (A Treatise on the Seven Rays, Vol. III)
    (Lucis Publishing, 1951)
  - Alice A. Bailey, *Esoteric Psychology* Vol. I–II

**重要說明 / IMPORTANT NOTE:**
靈魂光線（Soul Ray）的判斷本質上是靈性辨識的過程，而非機械計算。
本模組提供的是「傾向性指標」——根據上升點、太陽、月亮及 esoteric rulers
的組合給出最可能的光線傾向，並附上信心度評估。
最終判斷需要靈性洞察與冥想確認。

Soul Ray determination is inherently a process of spiritual discernment,
not mechanical calculation. This module provides 'tendency indicators'
based on the combination of Ascendant, Sun, Moon and esoteric rulers,
with confidence assessment. Final determination requires spiritual insight.

Ref: *Esoteric Astrology*, pp. 3–15 (Introduction to the Science of the Stars);
     *Esoteric Psychology* Vol. I, pp. 9–33 (The Seven Rays and Our Solar System).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from .constants import (
    SEVEN_RAYS,
    SIGN_RULERS,
    PLANET_RAY_MAP,
    ZODIAC_SIGNS,
    SIGN_ZH,
    RayData,
    SignRulers,
    get_sign_rays,
    get_sign_from_longitude,
    get_degree_in_sign,
    get_ray_interaction,
    RAY_INTERACTION,
)


# ============================================================
#  SWE planet IDs
# ============================================================

_SWE_IDS: Dict[str, int] = {
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
#  Data classes
# ============================================================

@dataclass
class EsotericPoint:
    """A single planet/point in an Esoteric chart."""
    name: str                  # Planet name
    longitude: float           # Absolute ecliptic longitude 0–360°
    sign: str                  # Zodiac sign
    sign_degree: float         # Degree within sign (0–30)
    rays: List[int]            # Ray numbers transmitted by this planet
    sign_rays: List[int]       # Ray numbers transmitted by the sign
    esoteric_ruler_of: Optional[str] = None  # Sign for which this is the esoteric ruler
    is_esoteric_ruler: bool = False
    is_exoteric_ruler: bool = False
    retrograde: bool = False


@dataclass
class RayContribution:
    """A single Ray contribution with its source factor."""
    ray: int
    weight: float              # 0.0–1.0 weight
    source: str                # Description of source (EN)
    source_zh: str             # Description of source (ZH)
    factor: str                # 'asc', 'sun', 'moon', 'esoteric_ruler', 'planet_sign', etc.


@dataclass
class RayTally:
    """Aggregated Ray tally across all chart factors."""
    ray_scores: Dict[int, float] = field(default_factory=lambda: {i: 0.0 for i in range(1, 8)})
    contributions: List[RayContribution] = field(default_factory=list)

    def add(self, ray: int, weight: float, source: str, source_zh: str, factor: str) -> None:
        self.ray_scores[ray] = self.ray_scores.get(ray, 0.0) + weight
        self.contributions.append(RayContribution(ray, weight, source, source_zh, factor))

    def top_rays(self, n: int = 3) -> List[Tuple[int, float]]:
        """Return top N (ray, score) pairs sorted descending."""
        return sorted(self.ray_scores.items(), key=lambda kv: kv[1], reverse=True)[:n]


@dataclass
class RayIndicator:
    """
    Ray indicator with confidence assessment.

    Confidence levels:
      'strong' — multiple convergent factors (≥3 independent indicators)
      'moderate' — 2 convergent factors
      'weak' — single indicator or contradictory signals

    Ref: *Esoteric Astrology*, p. 3 (the difficulty of determining Soul Ray).
    """
    ray: int
    ray_data: RayData
    confidence: str            # 'strong' | 'moderate' | 'weak'
    score: float               # Relative score
    supporting_factors: List[str]           # EN descriptions
    supporting_factors_zh: List[str]        # ZH descriptions
    interpretation_en: str
    interpretation_zh: str


@dataclass
class EsotericChart:
    """
    Complete Esoteric Astrology chart result.

    Contains:
      - All planet positions with Ray assignments
      - Ascendant & MC with esoteric ruler info
      - Soul Ray indicator (primary spiritual Ray)
      - Personality Ray indicator (incarnational Ray)
      - Full Ray tally with all contributions
      - Glamours and challenges
      - Service direction analysis
    """
    # Birth data
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude_geo: float
    location_name: str

    # Chart positions
    points: List[EsotericPoint] = field(default_factory=list)
    asc_longitude: float = 0.0
    asc_sign: str = ""
    mc_longitude: float = 0.0
    mc_sign: str = ""

    # Esoteric rulers
    asc_exoteric_ruler: str = ""
    asc_esoteric_ruler: str = ""
    asc_hierarchical_ruler: str = ""

    # Ray analysis
    soul_ray_indicator: Optional[RayIndicator] = None
    personality_ray_indicator: Optional[RayIndicator] = None
    ray_tally: Optional[RayTally] = None

    # Sign rulers info
    asc_sign_rulers: Optional[SignRulers] = None
    sun_sign_rulers: Optional[SignRulers] = None

    # Helpers
    def get_planet(self, name: str) -> Optional[EsotericPoint]:
        for p in self.points:
            if p.name == name:
                return p
        return None

    @property
    def sun_sign(self) -> str:
        sun = self.get_planet("Sun")
        return sun.sign if sun else ""

    @property
    def moon_sign(self) -> str:
        moon = self.get_planet("Moon")
        return moon.sign if moon else ""


# ============================================================
#  Position computation
# ============================================================

def _compute_positions(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float,
    lat: float, lon: float,
) -> Tuple[List[EsotericPoint], float, float, float, float]:
    """
    Compute planetary positions + ASC/MC using Swiss Ephemeris.

    Returns (points, asc_lon, mc_lon, asc_sign, mc_sign).
    Uses Placidus houses (consistent with Western module).
    """
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)

    # Houses
    houses, ascmc = swe.houses(jd, lat, lon, b"P")
    asc_lon = ascmc[0] % 360.0
    mc_lon = ascmc[1] % 360.0

    points: List[EsotericPoint] = []

    for name, pid in _SWE_IDS.items():
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        result, _ = swe.calc_ut(jd, pid, flags)
        planet_lon = result[0] % 360.0
        retrograde = result[3] < 0  # speed < 0 → retrograde
        sign = get_sign_from_longitude(planet_lon)
        sdeg = get_degree_in_sign(planet_lon)
        planet_rays = PLANET_RAY_MAP.get(name, [])
        sign_r = get_sign_rays(sign)

        points.append(EsotericPoint(
            name=name,
            longitude=planet_lon,
            sign=sign,
            sign_degree=sdeg,
            rays=list(planet_rays),
            sign_rays=sign_r,
            retrograde=retrograde,
        ))

    asc_sign = get_sign_from_longitude(asc_lon)
    mc_sign = get_sign_from_longitude(mc_lon)
    return points, asc_lon, mc_lon, asc_sign, mc_sign


# ============================================================
#  Ray tally engine
# ============================================================

def _build_ray_tally(
    points: List[EsotericPoint],
    asc_lon: float,
    asc_sign: str,
    mc_lon: float,
    mc_sign: str,
) -> RayTally:
    """
    Build a weighted Ray tally from all chart factors.

    Weighting scheme (Bailey-consistent):
      ASC sign               — weight 3.0  (strongest personality indicator)
      ASC esoteric ruler     — weight 2.5  (soul expression through form)
      Sun sign               — weight 2.5  (life purpose / soul expression)
      Sun esoteric ruler     — weight 2.0
      Moon sign              — weight 1.5  (past karma / habit form)
      Moon planet            — weight 1.0
      Mercury, Venus, Mars   — weight 1.0  (personal planets)
      Jupiter, Saturn        — weight 0.8  (social/structural planets)
      Uranus, Neptune, Pluto — weight 1.2  (transpersonal / esoteric)
      MC sign                — weight 1.0  (public purpose)

    Ref: *Esoteric Astrology*, pp. 44–65 (relationship of Rays to planets and signs).
    """
    tally = RayTally()

    sign_rulers_cache: Dict[str, SignRulers] = {}
    for p in points:
        if p.sign in SIGN_RULERS:
            sign_rulers_cache[p.sign] = SIGN_RULERS[p.sign]

    # ── Ascendant sign rays
    asc_rays = get_sign_rays(asc_sign)
    asc_sign_zh = SIGN_ZH.get(asc_sign, asc_sign)
    for r in asc_rays:
        tally.add(r, 3.0,
                  f"Ascendant in {asc_sign} (sign transmits Ray {r})",
                  f"上升點在{asc_sign_zh}（星座傳遞第{r}光線）",
                  "asc_sign")

    # ── ASC esoteric ruler
    asc_rulers = SIGN_RULERS.get(asc_sign)
    if asc_rulers:
        esoteric_r = asc_rulers.esoteric.split()[0]  # strip "(veiling ...)"
        planet_rays = PLANET_RAY_MAP.get(esoteric_r, [])
        for r in planet_rays:
            tally.add(r, 2.5,
                      f"ASC Esoteric Ruler {asc_rulers.esoteric} transmits Ray {r}",
                      f"上升點靈性統治星 {asc_rulers.esoteric} 傳遞第{r}光線",
                      "asc_esoteric_ruler")

    # ── Sun
    sun = next((p for p in points if p.name == "Sun"), None)
    if sun:
        for r in get_sign_rays(sun.sign):
            sun_sign_zh = SIGN_ZH.get(sun.sign, sun.sign)
            tally.add(r, 2.5,
                      f"Sun in {sun.sign} (sign transmits Ray {r})",
                      f"太陽在{sun_sign_zh}（星座傳遞第{r}光線）",
                      "sun_sign")
        # Sun planet ray (veils deeper planets)
        for r in PLANET_RAY_MAP.get("Sun", []):
            tally.add(r, 1.5,
                      f"Sun planet (Ray {r}: Love-Wisdom)",
                      f"太陽行星（第{r}光線：愛-智慧）",
                      "sun_planet")
        # Sun sign esoteric ruler
        sun_rulers = SIGN_RULERS.get(sun.sign)
        if sun_rulers:
            er = sun_rulers.esoteric.split()[0]
            for r in PLANET_RAY_MAP.get(er, []):
                tally.add(r, 2.0,
                          f"Sun sign esoteric ruler {sun_rulers.esoteric} transmits Ray {r}",
                          f"太陽星座靈性統治星 {sun_rulers.esoteric} 傳遞第{r}光線",
                          "sun_esoteric_ruler")

    # ── Moon
    moon = next((p for p in points if p.name == "Moon"), None)
    if moon:
        moon_sign_zh = SIGN_ZH.get(moon.sign, moon.sign)
        for r in get_sign_rays(moon.sign):
            tally.add(r, 1.5,
                      f"Moon in {moon.sign} (sign transmits Ray {r})",
                      f"月亮在{moon_sign_zh}（星座傳遞第{r}光線）",
                      "moon_sign")
        for r in PLANET_RAY_MAP.get("Moon", []):
            tally.add(r, 1.0,
                      f"Moon planet (Ray {r}: Harmony through Conflict)",
                      f"月亮行星（第{r}光線：透過衝突的和諧）",
                      "moon_planet")

    # ── Personal planets
    personal_weights = {"Mercury": 1.0, "Venus": 1.0, "Mars": 1.0}
    for pname, pw in personal_weights.items():
        p = next((pt for pt in points if pt.name == pname), None)
        if p:
            for r in PLANET_RAY_MAP.get(pname, []):
                tally.add(r, pw,
                          f"{pname} transmits Ray {r}",
                          f"{pname} 傳遞第{r}光線",
                          "personal_planet")
            for r in get_sign_rays(p.sign):
                tally.add(r, pw * 0.5,
                          f"{pname} in {p.sign} (sign Ray {r})",
                          f"{pname} 在 {SIGN_ZH.get(p.sign, p.sign)}（星座第{r}光線）",
                          "personal_planet_sign")

    # ── Social planets
    social_weights = {"Jupiter": 0.8, "Saturn": 0.8}
    for pname, pw in social_weights.items():
        p = next((pt for pt in points if pt.name == pname), None)
        if p:
            for r in PLANET_RAY_MAP.get(pname, []):
                tally.add(r, pw,
                          f"{pname} transmits Ray {r}",
                          f"{pname} 傳遞第{r}光線",
                          "social_planet")
            for r in get_sign_rays(p.sign):
                tally.add(r, pw * 0.4,
                          f"{pname} in {p.sign} (sign Ray {r})",
                          f"{pname} 在 {SIGN_ZH.get(p.sign, p.sign)}（星座第{r}光線）",
                          "social_planet_sign")

    # ── Transpersonal planets (higher octave, esoteric significance)
    trans_weights = {"Uranus": 1.2, "Neptune": 1.2, "Pluto": 1.2}
    for pname, pw in trans_weights.items():
        p = next((pt for pt in points if pt.name == pname), None)
        if p:
            for r in PLANET_RAY_MAP.get(pname, []):
                tally.add(r, pw,
                          f"{pname} transmits Ray {r}",
                          f"{pname} 傳遞第{r}光線",
                          "transpersonal_planet")
            for r in get_sign_rays(p.sign):
                tally.add(r, pw * 0.4,
                          f"{pname} in {p.sign} (sign Ray {r})",
                          f"{pname} 在 {SIGN_ZH.get(p.sign, p.sign)}（星座第{r}光線）",
                          "transpersonal_sign")

    # ── MC sign
    mc_rays = get_sign_rays(mc_sign)
    mc_sign_zh = SIGN_ZH.get(mc_sign, mc_sign)
    for r in mc_rays:
        tally.add(r, 1.0,
                  f"Midheaven in {mc_sign} (sign transmits Ray {r})",
                  f"天頂在{mc_sign_zh}（星座傳遞第{r}光線）",
                  "mc_sign")

    return tally


# ============================================================
#  Ray indicator derivation
#  Bailey, *Esoteric Astrology*, pp. 3–15, 44–65
# ============================================================

_CONFIDENCE_THRESHOLDS = (6.0, 3.5)  # strong ≥ 6.0; moderate ≥ 3.5; weak < 3.5


def _derive_soul_ray_indicator(tally: RayTally, asc_sign: str) -> RayIndicator:
    """
    Derive the Soul Ray indicator.

    The soul ray is most strongly indicated by:
      1. The esoteric ruler of the Ascendant and its sign placement
      2. The Sun's sign esoteric ruler
      3. Any transpersonal planet emphasis
      4. Overall convergence of Ray energies

    Ref: *Esoteric Astrology*, pp. 44–52 (the Esoteric Ruler and Soul Purpose).

    NOTE: This gives a 'most likely' indicator. True soul ray requires
    direct spiritual confirmation.
    """
    # Weight soul-relevant factors more heavily
    soul_scores: Dict[int, float] = {i: 0.0 for i in range(1, 8)}
    soul_factors: Dict[int, List[str]] = {i: [] for i in range(1, 8)}
    soul_factors_zh: Dict[int, List[str]] = {i: [] for i in range(1, 8)}

    for c in tally.contributions:
        # Soul-level factors: esoteric rulers, transpersonal planets, ASC sign, Sun sign esoteric ruler
        if c.factor in ("asc_esoteric_ruler", "sun_esoteric_ruler", "transpersonal_planet",
                        "asc_sign", "sun_sign"):
            soul_scores[c.ray] += c.weight
            soul_factors[c.ray].append(c.source)
            soul_factors_zh[c.ray].append(c.source_zh)

    top = sorted(soul_scores.items(), key=lambda kv: kv[1], reverse=True)
    best_ray, best_score = top[0]
    second_score = top[1][1] if len(top) > 1 else 0.0

    # Confidence: strong if clear dominance; moderate if close
    gap = best_score - second_score
    if best_score >= _CONFIDENCE_THRESHOLDS[0] and gap >= 2.0:
        confidence = "strong"
    elif best_score >= _CONFIDENCE_THRESHOLDS[1] or gap >= 1.0:
        confidence = "moderate"
    else:
        confidence = "weak"

    ray_data = SEVEN_RAYS[best_ray]
    asc_rulers = SIGN_RULERS.get(asc_sign)
    asc_eso = asc_rulers.esoteric if asc_rulers else "—"

    _conf_zh = {"strong": "高", "moderate": "中", "weak": "低"}.get(confidence, confidence)
    interp_en = (
        f"Soul Ray indicator: Ray {best_ray} — {ray_data.name_en} "
        f"(confidence: {confidence}). "
        f"Primary indicators: ASC {asc_sign}, esoteric ruler {asc_eso}. "
        f"Soul purpose: {ray_data.soul_purpose_en}"
    )
    interp_zh = (
        f"靈魂光線指標：第{best_ray}光線 — {ray_data.name_zh} "
        f"（信心度：{_conf_zh}）。"
        f"主要指標：上升點{SIGN_ZH.get(asc_sign, asc_sign)}，靈性統治星 {asc_eso}。"
        f"靈魂目的：{ray_data.soul_purpose_zh}"
    )

    return RayIndicator(
        ray=best_ray,
        ray_data=ray_data,
        confidence=confidence,
        score=best_score,
        supporting_factors=soul_factors[best_ray],
        supporting_factors_zh=soul_factors_zh[best_ray],
        interpretation_en=interp_en,
        interpretation_zh=interp_zh,
    )


def _derive_personality_ray_indicator(tally: RayTally, asc_sign: str) -> RayIndicator:
    """
    Derive the Personality Ray indicator.

    The personality ray is most strongly indicated by:
      1. The Ascendant sign and its exoteric ruler
      2. The Moon sign (habitual patterns, past karma)
      3. Overall chart emphasis via personal planets

    Ref: *Esoteric Astrology*, pp. 52–65 (the Exoteric Ruler and Personality).
    """
    pers_scores: Dict[int, float] = {i: 0.0 for i in range(1, 8)}
    pers_factors: Dict[int, List[str]] = {i: [] for i in range(1, 8)}
    pers_factors_zh: Dict[int, List[str]] = {i: [] for i in range(1, 8)}

    for c in tally.contributions:
        if c.factor in ("asc_sign", "moon_sign", "moon_planet",
                        "personal_planet", "personal_planet_sign", "sun_planet"):
            pers_scores[c.ray] += c.weight
            pers_factors[c.ray].append(c.source)
            pers_factors_zh[c.ray].append(c.source_zh)

    top = sorted(pers_scores.items(), key=lambda kv: kv[1], reverse=True)
    best_ray, best_score = top[0]
    second_score = top[1][1] if len(top) > 1 else 0.0

    gap = best_score - second_score
    if best_score >= _CONFIDENCE_THRESHOLDS[0] and gap >= 2.0:
        confidence = "strong"
    elif best_score >= _CONFIDENCE_THRESHOLDS[1] or gap >= 1.0:
        confidence = "moderate"
    else:
        confidence = "weak"

    ray_data = SEVEN_RAYS[best_ray]
    asc_rulers = SIGN_RULERS.get(asc_sign)
    asc_exo = asc_rulers.exoteric if asc_rulers else "—"

    _conf_zh = {"strong": "高", "moderate": "中", "weak": "低"}.get(confidence, confidence)
    interp_en = (
        f"Personality Ray indicator: Ray {best_ray} — {ray_data.name_en} "
        f"(confidence: {confidence}). "
        f"Primary indicators: ASC {asc_sign}, exoteric ruler {asc_exo}. "
        f"Service direction: {ray_data.service_en}"
    )
    interp_zh = (
        f"人格光線指標：第{best_ray}光線 — {ray_data.name_zh} "
        f"（信心度：{_conf_zh}）。"
        f"主要指標：上升點{SIGN_ZH.get(asc_sign, asc_sign)}，傳統統治星 {asc_exo}。"
        f"服務方向：{ray_data.service_zh}"
    )

    return RayIndicator(
        ray=best_ray,
        ray_data=ray_data,
        confidence=confidence,
        score=best_score,
        supporting_factors=pers_factors[best_ray],
        supporting_factors_zh=pers_factors_zh[best_ray],
        interpretation_en=interp_en,
        interpretation_zh=interp_zh,
    )


# ============================================================
#  Public API
# ============================================================

def compute_esoteric_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    **_kwargs,
) -> EsotericChart:
    """
    Compute a complete Esoteric Astrology chart following Alice Bailey's system.

    Performs:
      1. Astronomical positions (Swiss Ephemeris, Placidus houses)
      2. Ray assignment to each planet and sign
      3. Full Ray tally with weighted contributions
      4. Soul Ray indicator (via esoteric rulers + soul-level factors)
      5. Personality Ray indicator (via exoteric rulers + form-level factors)
      6. Ray interaction analysis
      7. Glamour identification and service direction

    Args:
        year, month, day: Birth date (Gregorian).
        hour, minute: Local birth time.
        timezone: UTC offset in hours (e.g. 8.0 for UTC+8).
        latitude: Geographic latitude in decimal degrees (°N positive).
        longitude: Geographic longitude in decimal degrees (°E positive).
        location_name: Optional location name for display.

    Returns:
        EsotericChart dataclass with complete analysis.

    Note:
        Soul Ray and Personality Ray indicators are *tendencies*, not certainties.
        See *Esoteric Astrology* p. 3 for Bailey's own caution on this topic.
    """
    points, asc_lon, mc_lon, asc_sign, mc_sign = _compute_positions(
        year, month, day, hour, minute, timezone, latitude, longitude
    )

    chart = EsotericChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude_geo=longitude,
        location_name=location_name,
        points=points,
        asc_longitude=asc_lon,
        asc_sign=asc_sign,
        mc_longitude=mc_lon,
        mc_sign=mc_sign,
    )

    # Populate esoteric ruler info
    asc_rulers = SIGN_RULERS.get(asc_sign)
    if asc_rulers:
        chart.asc_exoteric_ruler = asc_rulers.exoteric
        chart.asc_esoteric_ruler = asc_rulers.esoteric
        chart.asc_hierarchical_ruler = asc_rulers.hierarchical
        chart.asc_sign_rulers = asc_rulers

    sun = chart.get_planet("Sun")
    if sun:
        chart.sun_sign_rulers = SIGN_RULERS.get(sun.sign)

    # Mark each point's esoteric ruler status
    for p in points:
        rulers = SIGN_RULERS.get(p.sign)
        if rulers:
            p.is_esoteric_ruler = p.name in rulers.esoteric
            p.is_exoteric_ruler = p.name in rulers.exoteric

    # Build Ray tally
    tally = _build_ray_tally(points, asc_lon, asc_sign, mc_lon, mc_sign)
    chart.ray_tally = tally

    # Derive indicators
    chart.soul_ray_indicator = _derive_soul_ray_indicator(tally, asc_sign)
    chart.personality_ray_indicator = _derive_personality_ray_indicator(tally, asc_sign)

    return chart


def get_ray_interaction_analysis(chart: EsotericChart) -> Optional[Dict]:
    """
    Return the interaction analysis between Soul Ray and Personality Ray.

    Ref: *Esoteric Psychology* Vol. I, pp. 201–230 (Ray interactions).
    """
    if not chart.soul_ray_indicator or not chart.personality_ray_indicator:
        return None
    s_ray = chart.soul_ray_indicator.ray
    p_ray = chart.personality_ray_indicator.ray
    if s_ray == p_ray:
        return {
            "zh": f"靈魂光線與人格光線同為第{s_ray}光線，此生課題在於整合靈魂目的與人格表達，避免單一光線的極端表現。",
            "en": f"Soul Ray and Personality Ray are both Ray {s_ray}. This life's challenge is integrating soul purpose with personality expression, avoiding the extremes of this single Ray.",
            "type": "same",
        }
    return get_ray_interaction(s_ray, p_ray)
