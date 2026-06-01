"""
astro/maya/tzolkin.py — Tzolk'in 與 Haab 曆法計算
(Tzolk'in and Haab Calendar Calculations)

使用 GMT correlation (JD 584283 = 0.0.0.0.0 = 4 Ajaw 8 Kumku) 進行正確計算。
Uses GMT correlation for accurate calculations.
"""

from __future__ import annotations
from dataclasses import dataclass
from .constants import (
    MAYAN_EPOCH_JD,
    TZOLKIN_NUMBER_OFFSET,
    TZOLKIN_SIGN_OFFSET,
    HAAB_EPOCH_OFFSET,
    TZOLKIN_DAY_DATA,
    TZOLKIN_NUMBERS,
    HAAB_MONTHS,
)


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class TzolkinDay:
    """Tzolk'in 單日資料"""
    number: int          # 1–13 (神聖數字 / Sacred Tone)
    sign_index: int      # 0–19 (日符號索引 / Day Sign index)
    sign_name: str       # e.g., "Ajaw"
    sign_name_cn: str    # e.g., "阿哈瓦"
    sign_name_en: str    # e.g., "Sun Lord / Flower"
    glyph_emoji: str     # e.g., "☀️"
    day_position: int    # Position in 260-day cycle (0–259)

    # Rich interpretation data
    element: str
    element_cn: str
    direction: str
    direction_cn: str
    color: str           # Hex colour for visual display
    deity: str
    deity_cn: str
    personality_cn: str
    personality_en: str
    destiny_cn: str
    destiny_en: str
    mythology_cn: str
    mythology_en: str

    # Number interpretation
    number_name_cn: str
    number_tone_cn: str
    number_meaning_cn: str
    number_name_en: str
    number_tone_en: str
    number_meaning_en: str


@dataclass
class HaabDay:
    """Haab 民用曆單日資料"""
    day_of_month: int     # 0–19 (within the month)
    month_index: int      # 0–18 (18 named months + Wayeb)
    month_name: str       # e.g., "Kumku"
    month_name_cn: str    # e.g., "庫姆庫 (玉米)"
    month_glyph: str      # e.g., "🌽"
    day_of_year: int      # 0–364 (position in 365-day year)
    date_str: str         # e.g., "8 Kumku"


@dataclass
class CalendarRound:
    """Calendar Round (260 + 365 日曆合一)"""
    tzolkin: TzolkinDay
    haab: HaabDay
    round_str: str        # e.g., "4 Ajaw 8 Kumku"
    # How many days until this Calendar Round repeats (always 18,980 days = ~52 years)
    days_until_repeat: int
    next_repeat_jd: float


# ============================================================
# 計算函數 (Calculation Functions) — pure, no Streamlit
# ============================================================

def days_since_epoch(jd: float) -> int:
    """計算自瑪雅紀元起的天數 (Days since Mayan epoch, using floor)"""
    return int(jd - MAYAN_EPOCH_JD)


def compute_tzolkin(jd: float) -> TzolkinDay:
    """
    計算給定 Julian Day 的 Tzolk'in 日期。
    Compute the Tzolk'in date for a given Julian Day.

    Uses the corrected GMT correlation offsets:
      number = ((days + 3) % 13) + 1    → correct for epoch = 4 Ajaw
      sign   = (days + 19) % 20         → correct for epoch sign = Ajaw (index 19)
    """
    d = days_since_epoch(jd)

    number = ((d + TZOLKIN_NUMBER_OFFSET) % 13) + 1   # 1–13
    sign_index = (d + TZOLKIN_SIGN_OFFSET) % 20        # 0–19
    day_position = (d % 260)                            # 0–259 in the 260-day cycle

    sign_data = TZOLKIN_DAY_DATA[sign_index]
    num_data = TZOLKIN_NUMBERS[number - 1]              # list is 0-indexed, number is 1-based

    return TzolkinDay(
        number=number,
        sign_index=sign_index,
        sign_name=sign_data["name"],
        sign_name_cn=sign_data["name_cn"],
        sign_name_en=sign_data["name_en"],
        glyph_emoji=sign_data["glyph_emoji"],
        day_position=day_position,
        element=sign_data["element"],
        element_cn=sign_data["element_cn"],
        direction=sign_data["direction"],
        direction_cn=sign_data["direction_cn"],
        color=sign_data["color"],
        deity=sign_data["deity"],
        deity_cn=sign_data["deity_cn"],
        personality_cn=sign_data["personality_cn"],
        personality_en=sign_data["personality_en"],
        destiny_cn=sign_data["destiny_cn"],
        destiny_en=sign_data["destiny_en"],
        mythology_cn=sign_data["mythology_cn"],
        mythology_en=sign_data["mythology_en"],
        number_name_cn=num_data["name_cn"],
        number_tone_cn=num_data["tone_cn"],
        number_meaning_cn=num_data["meaning_cn"],
        number_name_en=num_data["name_en"],
        number_tone_en=num_data["tone_en"],
        number_meaning_en=num_data["meaning_en"],
    )


def compute_haab(jd: float) -> HaabDay:
    """
    計算給定 Julian Day 的 Haab 日期。
    Compute the Haab date for a given Julian Day.

    Uses the corrected GMT correlation offset:
      haab_position = (days + 348) % 365
      → At epoch: (0 + 348) % 365 = 348 = month 17 (Kumku), day 8  ✓
    """
    d = days_since_epoch(jd)
    haab_pos = (d + HAAB_EPOCH_OFFSET) % 365   # 0–364

    if haab_pos < 360:
        month_index = haab_pos // 20             # 0–17 (Pop through Kumku)
        day_of_month = haab_pos % 20             # 0–19
    else:
        month_index = 18                         # Wayeb (5 unlucky days)
        day_of_month = haab_pos - 360            # 0–4

    month_info = HAAB_MONTHS[month_index]
    return HaabDay(
        day_of_month=day_of_month,
        month_index=month_index,
        month_name=month_info[1],
        month_name_cn=month_info[2],
        month_glyph=month_info[3],
        day_of_year=haab_pos,
        date_str=f"{day_of_month} {month_info[1]}",
    )


def compute_calendar_round(jd: float) -> CalendarRound:
    """
    計算 Calendar Round（Tzolk'in + Haab 合一）。
    Compute the Calendar Round (Tzolk'in + Haab combined).

    The Calendar Round repeats every LCM(260, 365) = 18,980 days ≈ 52 years.
    """
    tzolkin = compute_tzolkin(jd)
    haab = compute_haab(jd)
    round_str = f"{tzolkin.number} {tzolkin.sign_name} / {haab.date_str}"

    # How many days until this exact combination recurs
    # The Calendar Round period is 18,980 days
    days_until_repeat = 18_980
    next_repeat_jd = jd + days_until_repeat

    return CalendarRound(
        tzolkin=tzolkin,
        haab=haab,
        round_str=round_str,
        days_until_repeat=days_until_repeat,
        next_repeat_jd=next_repeat_jd,
    )


def get_tzolkin_birthday_next(birth_jd: float, from_jd: float) -> float:
    """
    Find the next JD after `from_jd` on which the same Tzolk'in sign+number recurs.
    The Tzolk'in repeats every 260 days, so the answer is from_jd + offset where
    offset = (birth_pos - from_pos) % 260.
    """
    birth_pos = days_since_epoch(birth_jd) % 260
    from_pos  = days_since_epoch(from_jd) % 260
    diff = (birth_pos - from_pos) % 260
    if diff == 0:
        diff = 260  # advance to next occurrence
    return from_jd + diff


def tzolkin_day_label(tz: TzolkinDay, lang: str = "zh") -> str:
    """Return a short human-readable label, e.g., '4 阿哈瓦' or '4 Ajaw'."""
    if lang == "en":
        return f"{tz.number} {tz.sign_name}"
    return f"{tz.number} {tz.sign_name_cn}"
