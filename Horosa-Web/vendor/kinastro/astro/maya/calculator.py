"""
astro/maya/calculator.py — 瑪雅占星排盤計算
(Maya Astrology Chart Calculator)

整合 Tzolk'in、Haab、Long Count 與西方行星位置的完整排盤計算。
Comprehensive chart calculation integrating Tzolk'in, Haab, Long Count, and Western planetary positions.
"""

from __future__ import annotations
from dataclasses import dataclass, field

import swisseph as swe

from .constants import (
    MAYAN_PLANETS,
    PLANET_COLORS,
    ZODIAC_SIGNS,
    TZOLKIN_DAY_DATA,
    VENUS_CYCLE_DAYS,
    MAYAN_EPOCH_JD,
    DEGREES_PER_TZOLKIN_SIGN,
)
from .tzolkin import compute_tzolkin, compute_haab, compute_calendar_round, TzolkinDay, HaabDay, CalendarRound
from .long_count import jd_to_long_count, LongCount


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class MayanPlanet:
    """行星位置資料（帶瑪雅對應）"""
    name: str
    longitude: float
    latitude: float
    sign: str
    sign_glyph: str
    sign_chinese: str
    sign_degree: float
    retrograde: bool
    tzolkin_sign_index: int    # Day sign this planet maps to (via position)
    tzolkin_sign_name: str
    tzolkin_sign_cn: str
    tzolkin_glyph: str


@dataclass
class VenusCycleInfo:
    """金星週期資料"""
    venus_longitude: float
    elongation: float          # Angular distance from Sun (degrees)
    phase_name_cn: str
    phase_name_en: str
    phase_meaning_cn: str
    phase_meaning_en: str
    venus_tzolkin_sign: str    # Tzolk'in day sign for Venus position
    venus_tzolkin_number: int


@dataclass
class MayanChart:
    """瑪雅占星完整排盤結果"""
    # Input parameters
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    julian_day: float

    # Calendar data
    tzolkin: TzolkinDay
    haab: HaabDay
    calendar_round: CalendarRound
    long_count: LongCount

    # Lord of the Night (9-day cycle)
    lord_of_night: int          # 1–9 (G1 through G9)
    lord_of_night_str: str

    # Planetary positions
    planets: list[MayanPlanet]

    # Venus cycle
    venus: VenusCycleInfo

    # Backward-compat properties
    @property
    def baktun(self) -> int:    return self.long_count.baktun
    @property
    def katun(self) -> int:     return self.long_count.katun
    @property
    def tun(self) -> int:       return self.long_count.tun
    @property
    def winal(self) -> int:     return self.long_count.winal
    @property
    def kin(self) -> int:       return self.long_count.kin
    @property
    def long_count_str(self) -> str: return self.long_count.date_str
    @property
    def tzolkin_number(self) -> int:    return self.tzolkin.number
    @property
    def tzolkin_day_name(self) -> str:  return self.tzolkin.sign_name
    @property
    def tzolkin_name_cn(self) -> str:   return self.tzolkin.sign_name_cn
    @property
    def tzolkin_glyph(self) -> str:     return self.tzolkin.glyph_emoji
    @property
    def tzolkin_energy(self) -> str:    return self.tzolkin.sign_name_cn
    @property
    def haab_day(self) -> int:          return self.haab.day_of_month
    @property
    def haab_month(self) -> str:        return self.haab.month_name
    @property
    def haab_month_cn(self) -> str:     return self.haab.month_name_cn
    @property
    def haab_month_glyph(self) -> str:  return self.haab.month_glyph
    @property
    def haab_date_str(self) -> str:     return self.haab.date_str
    @property
    def calendar_round_str(self) -> str: return self.calendar_round.round_str


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _normalize(deg: float) -> float:
    return deg % 360.0


def _sign_index(deg: float) -> int:
    return int(_normalize(deg) / 30.0)


def _sign_degree(deg: float) -> float:
    return _normalize(deg) % 30.0


def _get_lord_of_night(jd: float) -> tuple[int, str]:
    """
    計算夜之主宰（Lord of the Night，G1–G9）。
    The 9-day cycle resets at the Mayan epoch.
    """
    d = int(jd - MAYAN_EPOCH_JD)
    lord_num = (d % 9) + 1   # 1–9
    lord_str = f"G{lord_num} — 冥界第{lord_num}位守護者"
    return lord_num, lord_str


def _compute_venus_info(jd: float, venus_lon: float, sun_lon: float) -> VenusCycleInfo:
    """
    計算金星週期相位資訊。
    Compute Venus cycle phase information.
    """
    from .constants import VENUS_PHASES, DEGREES_PER_TZOLKIN_SIGN
    from .tzolkin import compute_tzolkin

    # Signed elongation (0–360°, east = 0–180, west = 180–360)
    diff = _normalize(venus_lon - sun_lon)

    # Unsign elongation for display (0–180°)
    elongation = diff if diff <= 180 else 360 - diff

    # Determine Venus synodic phase:
    #   diff < 10° or diff > 350° → inferior conjunction (Venus between Earth & Sun)
    #   10° ≤ diff ≤ 170°         → evening star (Venus east of Sun, sets after Sun)
    #   170° < diff < 190°        → superior conjunction (Venus behind Sun)
    #   190° ≤ diff ≤ 350°        → morning star (Venus west of Sun, rises before Sun)
    if diff < 10 or diff > 350:
        phase_idx = 3   # inferior conjunction
    elif diff > 190:
        phase_idx = 0   # morning star (Venus west of Sun)
    elif diff > 170:
        phase_idx = 1   # superior conjunction
    else:
        phase_idx = 2   # evening star (Venus east of Sun)

    phase = VENUS_PHASES[phase_idx]

    # Venus Tzolk'in sign: map Venus longitude to a day sign (18° per sign)
    v_tz = compute_tzolkin(jd)
    v_sign_idx = int(_normalize(venus_lon) / DEGREES_PER_TZOLKIN_SIGN) % 20
    v_sign = TZOLKIN_DAY_DATA[v_sign_idx]

    return VenusCycleInfo(
        venus_longitude=venus_lon,
        elongation=elongation,
        phase_name_cn=phase["name_cn"],
        phase_name_en=phase["name_en"],
        phase_meaning_cn=phase["meaning_cn"],
        phase_meaning_en=phase["meaning_en"],
        venus_tzolkin_sign=v_sign["name"],
        venus_tzolkin_number=v_tz.number,
    )


# ============================================================
# 主計算函數 (Main Calculation Function)
# ============================================================

def compute_maya_chart(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float,
    latitude: float, longitude: float,
    location_name: str = "",
) -> MayanChart:
    """
    計算完整瑪雅占星排盤。
    Compute the complete Maya astrology chart.

    Uses the corrected GMT correlation offsets for Tzolk'in and Haab.
    """
    swe.set_ephe_path("")

    # Julian Day (convert local time to UT)
    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    # Tzolk'in, Haab, Calendar Round
    tz = compute_tzolkin(jd)
    haab = compute_haab(jd)
    cr = compute_calendar_round(jd)
    lc = jd_to_long_count(jd)

    # Lord of the Night
    lord_num, lord_str = _get_lord_of_night(jd)

    # Planetary positions
    planets: list[MayanPlanet] = []
    sun_lon = 0.0
    venus_lon = 0.0
    for name, planet_id in MAYAN_PLANETS.items():
        result, _ = swe.calc_ut(jd, planet_id)
        plon = _normalize(result[0])
        plat = result[1]
        speed = result[3]
        idx = _sign_index(plon)
        sign_info = ZODIAC_SIGNS[idx]

        # Map planet longitude to a Tzolk'in sign (18° per sign)
        tz_sign_idx = int(plon / DEGREES_PER_TZOLKIN_SIGN) % 20
        tz_sign_data = TZOLKIN_DAY_DATA[tz_sign_idx]

        planets.append(MayanPlanet(
            name=name,
            longitude=plon,
            latitude=plat,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            sign_chinese=sign_info[2],
            sign_degree=_sign_degree(plon),
            retrograde=(speed < 0),
            tzolkin_sign_index=tz_sign_idx,
            tzolkin_sign_name=tz_sign_data["name"],
            tzolkin_sign_cn=tz_sign_data["name_cn"],
            tzolkin_glyph=tz_sign_data["glyph_emoji"],
        ))

        if planet_id == swe.SUN:
            sun_lon = plon
        if planet_id == swe.VENUS:
            venus_lon = plon

    venus_info = _compute_venus_info(jd, venus_lon, sun_lon)

    return MayanChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd,
        tzolkin=tz,
        haab=haab,
        calendar_round=cr,
        long_count=lc,
        lord_of_night=lord_num,
        lord_of_night_str=lord_str,
        planets=planets,
        venus=venus_info,
    )
