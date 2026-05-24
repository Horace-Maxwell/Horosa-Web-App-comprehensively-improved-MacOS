"""
緬甸／撣族 Mahabote 深度占星計算模組
Burmese / Shan Mahabote Astrology — Calculator

包含：
  1. 古典 Mahabote 排盤計算（8 宮盤）
  2. 行星大運（Atar）計算
  3. 年度小運（Annual Minor Period）計算
  4. 流年盤（Year Chart）計算
  5. 合婚相容性計算（Compatibility）
  6. 敵對宮位分析（Hostile Aspect Analysis）
  7. 撣族曆法換算

算法依據：
  - Barbara Cameron, *The Little Key* (traditional Mahabote handbook)
  - Traditional Burmese Sakka (Myanmar Era) calendar conversion
  - Classical 7-planet Atar cycle (total 96 years)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Tuple

import streamlit as st

from .constants import (
    PLANET_PERIOD_YEARS,
    PLANET_SEQUENCE,
    PLANET_COLORS,
    MAHABOTE_HOUSES,
    WEEKDAY_NAMES_EN,
    WEEKDAY_NAMES_CN,
    WEEKDAY_NAMES_MYANMAR,
    BIRTH_SIGN_DATA,
    WEEKDAY_TO_SIGN,
    PLANET_TO_SIGN,
    DIRECTIONS_8,
    PLANET_TO_DIR_IDX,
    COMPAT_PLANETS,
    COMPAT_MATRIX,
    COMPAT_LABELS,
    COMPAT_PERCENT,
    HOSTILE_PAIRS,
    SHAN_CALENDAR_INFO,
)


# ============================================================
# 資料類定義 (Data Classes)
# ============================================================

@dataclass
class MahaboteHouse:
    """Single house in the Mahabote chart."""
    index: int
    name_en: str
    name_myanmar: str
    name_cn: str
    meaning: str
    description: str
    planet: str
    planet_cn: str
    planet_symbol: str
    is_birth_house: bool
    weekday_en: str
    weekday_cn: str
    animal_en: str
    animal_myanmar: str
    animal_cn: str
    animal_emoji: str
    sign_key: str     # Key into BIRTH_SIGN_DATA


@dataclass
class MahabotePeriod:
    """A single planetary major period (Atar / Dasa)."""
    planet: str
    planet_cn: str
    planet_symbol: str
    sign_key: str
    years: int
    start_age: int
    end_age: int
    is_current: bool


@dataclass
class MinorPeriod:
    """Annual minor period (sub-period based on age mod 8)."""
    age: int
    house_index: int
    house_name_en: str
    house_name_cn: str
    planet: str
    planet_cn: str
    planet_symbol: str
    sign_key: str
    is_current: bool
    quality: str   # 吉 / 凶 / 中性


@dataclass
class YearChartEntry:
    """A single house entry in the Year Chart."""
    house_index: int
    house_name_cn: str
    base_planet: str       # 本命盤行星
    transit_planet: str    # 流年行星
    interaction: str       # 吉凶互動描述


@dataclass
class CompatibilityResult:
    """Two-person Mahabote compatibility result."""
    person1_sign_key: str
    person2_sign_key: str
    person1_planet: str
    person2_planet: str
    person1_animal_cn: str
    person2_animal_cn: str
    score: int             # 1–5
    label_cn: str          # 非常相配 / 相配 / 中性 / 需努力 / 困難
    label_en: str          # Pesthi / Maitri / Sama / Shatru-M / Shatru
    emoji: str
    percent: int           # 0–100
    description: str       # 詳細描述
    hostile_note: Optional[str] = None


@dataclass
class MahaboteChart:
    """Complete Myanmar / Shan Mahabote chart result."""
    # ── Input ──────────────────────────────────────────────────
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str

    # ── Myanmar / Shan calendar ─────────────────────────────────
    myanmar_year: int
    shan_year: int

    # ── Weekday info ────────────────────────────────────────────
    weekday: int               # 0=Sunday … 6=Saturday
    weekday_name_en: str
    weekday_name_cn: str
    weekday_name_myanmar: str

    # ── Birth sign & planet ─────────────────────────────────────
    sign_key: str              # Key into BIRTH_SIGN_DATA
    birth_planet: str          # English planet name
    birth_planet_cn: str
    birth_planet_symbol: str
    birth_planet_element: str
    birth_direction: str
    is_rahu: bool

    # ── Birth animal ─────────────────────────────────────────────
    birth_animal_en: str
    birth_animal_myanmar: str
    birth_animal_cn: str
    birth_animal_emoji: str

    # ── Mahabote calculation ─────────────────────────────────────
    mahabote_value: int        # (ME_year + weekday_num) mod 8

    # ── Birth house ──────────────────────────────────────────────
    birth_house_name_en: str
    birth_house_name_myanmar: str
    birth_house_name_cn: str
    birth_house_meaning: str
    birth_house_description: str

    # ── Full 8-house chart ───────────────────────────────────────
    houses: List[MahaboteHouse] = field(default_factory=list)

    # ── Major periods (Atar) ─────────────────────────────────────
    periods: List[MahabotePeriod] = field(default_factory=list)

    # ── Minor periods (annual) ───────────────────────────────────
    minor_periods: List[MinorPeriod] = field(default_factory=list)

    # ── Year chart entries ───────────────────────────────────────
    year_chart: List[YearChartEntry] = field(default_factory=list)

    # ── Direction / omen data ────────────────────────────────────
    directions: List[dict] = field(default_factory=list)

    # ── Sign profile from database ───────────────────────────────
    sign_profile: dict = field(default_factory=dict)

    # ── Hostile aspects ──────────────────────────────────────────
    hostile_aspects: List[Tuple[str, str, str]] = field(default_factory=list)


# ============================================================
# Module-level static lookup tables
# ============================================================

# House name → minor period quality (static, moved out of function)
_HOUSE_QUALITY_MAP: Dict[str, str] = {
    "Bhin":   "吉",
    "Ayu":    "吉",
    "Winya":  "中性",
    "Kiya":   "吉",
    "Hein":   "大吉",
    "Marana": "凶",
    "Thila":  "吉",
    "Kamma":  "中性",
}

# Named house-pair interactions for year chart (static data)
_YEAR_CHART_INTERACTIONS: Dict[Tuple[str, str], str] = {
    ("Hein",   "Hein"):   "雙重權勢宮激活，事業大進，宜積極開創",
    ("Bhin",   "Hein"):   "本命宮配合權勢，個人魅力強，貴人多助",
    ("Marana", "Marana"): "雙重死亡宮疊加，需謹慎防災，多積善德",
    ("Thila",  "Hein"):   "道德宮與權勢宮合，名聲大好，適合公益",
    ("Kamma",  "Marana"): "業力宮遇衰退，舊業浮現，宜還願化解",
}


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _get_myanmar_year(year: int, month: int, day: int) -> int:
    """Calculate Myanmar Era (ME / Sakka) year from Gregorian date.

    Burmese New Year (Thingyan) typically falls on or around April 16–17.
    The classical cutoff used here: on/after April 16 → ME = year − 638;
    before April 16 → ME = year − 639.

    Ref: Barbara Cameron, *The Little Key*; traditional Burmese calendar texts.
    """
    if month > 4 or (month == 4 and day >= 16):
        return year - 638
    return year - 639


def _get_shan_year(me_year: int) -> int:
    """Approximate Shan (Tai) year from Myanmar Era year.

    Shan year ≈ ME year − 450  (traditional approximation).
    """
    return me_year + SHAN_CALENDAR_INFO["year_offset"]


def _get_weekday(year: int, month: int, day: int) -> int:
    """Day of week: 0=Sunday, 1=Monday, … 6=Saturday."""
    d = date(year, month, day)
    # Python weekday(): Mon=0 … Sun=6  →  we want Sun=0 … Sat=6
    return (d.weekday() + 1) % 7


def _local_solar_hour(hour: int, minute: int, timezone: float, longitude: float) -> float:
    """Convert clock time to approximate local solar time hour.

    Each degree of longitude offset from the timezone meridian = 4 minutes.
    Myanmar timezone is UTC+6:30 (6.5), longitude ≈ 96°E.
    """
    tz_meridian = timezone * 15.0
    offset_minutes = (longitude - tz_meridian) * 4.0
    total_minutes = hour * 60 + minute + offset_minutes
    return (total_minutes / 60.0) % 24


def _is_wednesday_evening(weekday: int, solar_hour: float) -> bool:
    """Wednesday after 18:00 local solar time → Rahu, not Mercury.

    Ref: Traditional Burmese Mahabote — Rahu rules the second half of Wednesday.
    """
    return weekday == 3 and solar_hour >= 18.0


def _get_sign_key(weekday: int, is_rahu: bool) -> str:
    """Return the BIRTH_SIGN_DATA key for this birth."""
    if is_rahu:
        return "Rahu"
    return WEEKDAY_TO_SIGN.get(weekday, "Sunday")


def _get_planet_for_weekday(weekday: int, is_rahu: bool) -> Tuple[str, str, str, str, str]:
    """Return (planet_en, planet_cn, planet_symbol, element_cn, direction_cn)."""
    sign_key = _get_sign_key(weekday, is_rahu)
    sd = BIRTH_SIGN_DATA[sign_key]
    dir_info = DIRECTIONS_8[PLANET_TO_DIR_IDX[sd["planet_en"]]]
    return (
        sd["planet_en"],
        sd["planet_cn"],
        sd["planet_symbol"],
        sd["element_cn"],
        dir_info["dir_cn"],
    )


def _compute_major_periods(
    weekday: int,
    birth_year: int,
    current_year: int,
) -> List[MahabotePeriod]:
    """Compute Atar (7-planet major periods), starting from birth weekday.

    Rahu-born use Mercury's Atar sequence start position.
    Two full 96-year cycles are built so every lifespan is covered.
    """
    start_weekday = weekday  # Rahu-born start from Mercury (weekday=3)
    periods: List[MahabotePeriod] = []
    age = 0
    current_age = current_year - birth_year

    for _ in range(2):   # cover 192 years
        for offset in range(7):
            wd_idx = (start_weekday + offset) % 7
            sign_key = WEEKDAY_TO_SIGN[wd_idx]
            sd = BIRTH_SIGN_DATA[sign_key]
            planet_name = sd["planet_en"]
            duration = PLANET_PERIOD_YEARS.get(planet_name, 0)
            if duration == 0:
                duration = PLANET_PERIOD_YEARS["Mercury"]
            start_age = age
            end_age = age + duration
            is_current = start_age <= current_age < end_age
            periods.append(MahabotePeriod(
                planet=planet_name,
                planet_cn=sd["planet_cn"],
                planet_symbol=sd["planet_symbol"],
                sign_key=sign_key,
                years=duration,
                start_age=start_age,
                end_age=end_age,
                is_current=is_current,
            ))
            age += duration
            if age > 120:
                break
        if age > 120:
            break

    return periods


def _compute_minor_periods(
    houses: List[MahaboteHouse],
    birth_year: int,
    current_year: int,
) -> List[MinorPeriod]:
    """Compute annual minor periods (age mod 8 maps to houses 0–7).

    Each year the energy moves to the next house in sequence.
    Returns up to 80 years of minor periods.
    """
    minor: List[MinorPeriod] = []
    current_age = current_year - birth_year

    for age in range(0, 81):
        house_idx = age % 8
        h = houses[house_idx]
        quality = _HOUSE_QUALITY_MAP.get(h.name_en, "中性")
        minor.append(MinorPeriod(
            age=age,
            house_index=house_idx,
            house_name_en=h.name_en,
            house_name_cn=h.name_cn,
            planet=h.planet,
            planet_cn=h.planet_cn,
            planet_symbol=h.planet_symbol,
            sign_key=h.sign_key,
            is_current=(age == current_age),
            quality=quality,
        ))

    return minor


def _compute_year_chart(
    chart_year: int,
    birth_year: int,
    houses: List[MahaboteHouse],
) -> List[YearChartEntry]:
    """Compute Year Chart (transit/annual overlay).

    The transit house is determined by the age in the given year mod 8,
    then shifted around the natal chart to show house-level annual energy.
    """
    age = chart_year - birth_year
    transit_house_idx = age % 8

    entries: List[YearChartEntry] = []
    for i in range(8):
        h = houses[i]
        transit_h = houses[(i + transit_house_idx) % 8]
        key = (h.name_en, transit_h.name_en)
        interaction = _YEAR_CHART_INTERACTIONS.get(
            key,
            f"本命{h.name_cn}遇流年{transit_h.name_cn}，宜觀察此宮主題的發展",
        )
        entries.append(YearChartEntry(
            house_index=i,
            house_name_cn=h.name_cn,
            base_planet=h.planet,
            transit_planet=transit_h.planet,
            interaction=interaction,
        ))
    return entries


def _find_hostile_aspects(birth_planet: str) -> List[Tuple[str, str, str]]:
    """Return hostile pairs relevant to the birth planet."""
    result = []
    for p1, p2, note in HOSTILE_PAIRS:
        if birth_planet in (p1, p2):
            other = p2 if birth_planet == p1 else p1
            result.append((birth_planet, other, note))
    return result


def _build_houses(
    mahabote_value: int,
    weekday: int,
    is_rahu: bool,
) -> List[MahaboteHouse]:
    """Build all 8 Mahabote houses with planet assignments.

    Birth planet sits at house index == mahabote_value.
    Subsequent houses fill clockwise using the PLANET_SEQUENCE order.
    """
    birth_sign_key = _get_sign_key(weekday, is_rahu)
    # Find starting planet index in PLANET_SEQUENCE
    birth_planet = BIRTH_SIGN_DATA[birth_sign_key]["planet_en"]
    # Rahu maps to Mercury in sequence
    effective_planet = "Mercury" if birth_planet == "Rahu" else birth_planet
    seq_start = PLANET_SEQUENCE.index(effective_planet)

    houses: List[MahaboteHouse] = []
    for i in range(8):
        h_info = MAHABOTE_HOUSES[i]
        planet_offset = (i - mahabote_value) % 8
        # With 7 planets and 8 houses, planet_offset 7 wraps back to offset 0
        planet_seq_idx = (seq_start + planet_offset) % 7
        planet_name = PLANET_SEQUENCE[planet_seq_idx]
        sign_key = PLANET_TO_SIGN[planet_name]
        sd = BIRTH_SIGN_DATA[sign_key]

        houses.append(MahaboteHouse(
            index=i,
            name_en=h_info[0],
            name_myanmar=h_info[1],
            name_cn=h_info[2],
            meaning=h_info[3],
            description=h_info[4],
            planet=planet_name,
            planet_cn=sd["planet_cn"],
            planet_symbol=sd["planet_symbol"],
            is_birth_house=(i == mahabote_value),
            weekday_en=sd["weekday_en"],
            weekday_cn=sd["weekday_cn"],
            animal_en=sd["animal_en"],
            animal_myanmar=sd["animal_myanmar"],
            animal_cn=sd["animal_cn"],
            animal_emoji=sd["animal_emoji"],
            sign_key=sign_key,
        ))
    return houses


# ============================================================
# 主計算函數 (Main Calculation)
# ============================================================

@st.cache_data(ttl=86400, show_spinner=False)
def compute_mahabote_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
) -> MahaboteChart:
    """Compute a complete Myanmar / Shan Mahabote astrology chart.

    Parameters follow the KinAstro standard _calc_params interface.

    Algorithm:
      1. Convert to Myanmar Era (Sakka year); April 16 cutoff.
      2. Determine birth weekday.
      3. Determine if Wednesday evening → Rahu.
      4. Compute Mahabote value = (ME_year + weekday_num) mod 8.
      5. Build 8-house chart with planetary assignments.
      6. Compute Atar major periods, annual minor periods, year chart.

    Ref: Barbara Cameron, *The Little Key*; traditional Burmese Mahabote texts.
    """
    me_year = _get_myanmar_year(year, month, day)
    shan_year = _get_shan_year(me_year)
    weekday = _get_weekday(year, month, day)

    solar_hour = _local_solar_hour(hour, minute, timezone, longitude)
    is_rahu = _is_wednesday_evening(weekday, solar_hour)

    sign_key = _get_sign_key(weekday, is_rahu)
    sd = BIRTH_SIGN_DATA[sign_key]
    dir_info = DIRECTIONS_8[PLANET_TO_DIR_IDX[sd["planet_en"]]]

    birth_planet = sd["planet_en"]
    birth_planet_cn = sd["planet_cn"]
    birth_planet_symbol = sd["planet_symbol"]
    birth_planet_element = sd["element_cn"]
    birth_direction = dir_info["dir_cn"]

    # Mahabote value: 1-based weekday (Sunday=1 … Saturday=7)
    weekday_num = weekday + 1
    mahabote_value = (me_year + weekday_num) % 8

    birth_house = MAHABOTE_HOUSES[mahabote_value]

    # Build 8-house chart
    houses = _build_houses(mahabote_value, weekday, is_rahu)

    # Periods
    current_year = date.today().year
    periods = _compute_major_periods(weekday, year, current_year)
    minor_periods = _compute_minor_periods(houses, year, current_year)

    # Year chart (for current year)
    year_chart = _compute_year_chart(current_year, year, houses)

    # Hostile aspects
    hostile_aspects = _find_hostile_aspects(birth_planet)

    return MahaboteChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
        myanmar_year=me_year,
        shan_year=shan_year,
        weekday=weekday,
        weekday_name_en=WEEKDAY_NAMES_EN[weekday],
        weekday_name_cn=WEEKDAY_NAMES_CN[weekday],
        weekday_name_myanmar=WEEKDAY_NAMES_MYANMAR[weekday],
        sign_key=sign_key,
        birth_planet=birth_planet,
        birth_planet_cn=birth_planet_cn,
        birth_planet_symbol=birth_planet_symbol,
        birth_planet_element=birth_planet_element,
        birth_direction=birth_direction,
        is_rahu=is_rahu,
        birth_animal_en=sd["animal_en"],
        birth_animal_myanmar=sd["animal_myanmar"],
        birth_animal_cn=sd["animal_cn"],
        birth_animal_emoji=sd["animal_emoji"],
        mahabote_value=mahabote_value,
        birth_house_name_en=birth_house[0],
        birth_house_name_myanmar=birth_house[1],
        birth_house_name_cn=birth_house[2],
        birth_house_meaning=birth_house[3],
        birth_house_description=birth_house[4],
        houses=houses,
        periods=periods,
        minor_periods=minor_periods,
        year_chart=year_chart,
        directions=list(DIRECTIONS_8),
        sign_profile=sd,
        hostile_aspects=hostile_aspects,
    )


# ============================================================
# 合婚計算 (Compatibility Calculation)
# ============================================================

def compute_compatibility(
    sign_key_1: str,
    sign_key_2: str,
) -> CompatibilityResult:
    """Compute Mahabote compatibility between two birth signs.

    Parameters
    ----------
    sign_key_1 : str
        First person's sign key (e.g. "Sunday", "Rahu")
    sign_key_2 : str
        Second person's sign key

    Returns
    -------
    CompatibilityResult
        Full compatibility analysis.
    """
    sd1 = BIRTH_SIGN_DATA[sign_key_1]
    sd2 = BIRTH_SIGN_DATA[sign_key_2]

    planet1 = sd1["planet_en"]
    planet2 = sd2["planet_en"]

    # Map Rahu to Mercury for matrix lookup
    p1_idx = COMPAT_PLANETS.index("Mercury" if planet1 == "Rahu" else planet1)
    p2_idx = COMPAT_PLANETS.index("Mercury" if planet2 == "Rahu" else planet2)

    score = COMPAT_MATRIX[p1_idx][p2_idx]
    label_cn, label_en, emoji = COMPAT_LABELS[score]
    percent = COMPAT_PERCENT[score]

    # Build description
    _descriptions = {
        5: (
            f"{sd1['animal_cn']}（{sd1['planet_cn']}）與"
            f"{sd2['animal_cn']}（{sd2['planet_cn']}）形成「Pesthi 婚配」關係，"
            "是古典緬甸占星中最理想的組合之一。"
            "雙方在目標、價值觀與人生節奏上高度契合，"
            "能夠相互扶持、共同成長。"
        ),
        4: (
            f"{sd1['animal_cn']}與{sd2['animal_cn']}形成「Maitri 友誼」關係，"
            "雙方相互欣賞、溝通順暢，是良好的伴侶或夥伴。"
            "在生活小事上偶有摩擦，但整體關係和諧。"
        ),
        3: (
            f"{sd1['animal_cn']}與{sd2['animal_cn']}形成「Sama 中性」關係，"
            "需要雙方主動培養理解與包容。"
            "並非天生的完美組合，但透過努力可建立穩固的關係。"
        ),
        2: (
            f"{sd1['animal_cn']}與{sd2['animal_cn']}形成「壓力」關係，"
            "雙方個性或目標方向存在明顯差異。"
            "需要高度的耐心、包容與溝通技巧來維持和諧。"
        ),
        1: (
            f"{sd1['animal_cn']}與{sd2['animal_cn']}形成「Shatru 對立」關係，"
            "是古典緬甸占星中挑戰最大的組合。"
            "兩人容易產生根本性的衝突，需要大量的相互理解與靈性修持。"
        ),
    }
    description = _descriptions.get(score, "")

    # Check hostile pairs
    hostile_note: Optional[str] = None
    for p1, p2, note in HOSTILE_PAIRS:
        if (planet1 == p1 and planet2 == p2) or (planet1 == p2 and planet2 == p1):
            hostile_note = note
            break

    return CompatibilityResult(
        person1_sign_key=sign_key_1,
        person2_sign_key=sign_key_2,
        person1_planet=planet1,
        person2_planet=planet2,
        person1_animal_cn=sd1["animal_cn"],
        person2_animal_cn=sd2["animal_cn"],
        score=score,
        label_cn=label_cn,
        label_en=label_en,
        emoji=emoji,
        percent=percent,
        description=description,
        hostile_note=hostile_note,
    )


# ============================================================
# 流年盤計算（Year Chart for any year）
# ============================================================

def compute_year_chart_for_year(
    chart: MahaboteChart,
    target_year: int,
) -> List[YearChartEntry]:
    """Compute the Year Chart (transit overlay) for a specific year.

    Parameters
    ----------
    chart : MahaboteChart
        The natal Mahabote chart.
    target_year : int
        The year to compute the transit chart for.
    """
    return _compute_year_chart(target_year, chart.year, chart.houses)
