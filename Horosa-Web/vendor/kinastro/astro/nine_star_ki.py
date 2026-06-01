"""
astro/nine_star_ki.py — 日本九星氣學排盤模組
Japanese Nine Star Ki (九星氣學 / Kyūsei Kigaku) Astrology Module

九星氣學是一種源自中國、在日本廣泛發展的傳統命理體系，
以洛書九宮（Lo Shu Square）為基礎，結合九顆飛星與五行理論。

Core Calculation Rules:
- 本命星 (Year Star / Principal Star): Based on solar year starting at Li Chun (立春, ~Feb 4).
  If birth date is before Li Chun, use previous year.
  Formula: sum all digits of adjusted year until single/double digit ≤ 10, then 11 - result (mod 9, 0→9)
- 月命星 (Month Star): Flying Star method — starts from year-group reference star,
  moves counterclockwise (陰遁) through Lo Shu palaces by solar month.
- 日命星 (Day Star): Daily cycle based on a 9-day repeating pattern anchored to a
  known epoch, adjusted to the solar month start (節).

Cultural Notice:
This module provides calculations for cultural learning and reference only.
For important life decisions please consult a qualified Nine Star Ki practitioner.
"""

from __future__ import annotations

import streamlit as st
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

# ============================================================
# 九星定義 (Nine Star Definitions)
# ============================================================

# Each entry: (number, zh_name, jp_name, en_name, element_zh, element_en,
#              direction_zh, direction_en, color_zh, color_en, hex_color,
#              personality_zh, personality_en, lucky_numbers)
NINE_STARS = [
    (
        1, "一白水星", "一白水星 (Ichihaku Suisei)", "One White Water Star",
        "水", "Water", "北", "North", "白", "White", "#E8F4FD",
        "聰明機靈、善於溝通、適應力強、直覺敏銳、情感豐富",
        "Intelligent, communicative, adaptable, intuitive, emotionally rich",
        [1, 6],
    ),
    (
        2, "二黑土星", "二黒土星 (Jikoку Dosei)", "Two Black Earth Star",
        "土", "Earth", "西南", "Southwest", "黑", "Black", "#2C3E50",
        "勤勞踏實、服務精神、耐心細心、重視家庭、穩重可靠",
        "Diligent, service-oriented, patient, family-focused, reliable",
        [2, 5, 8],
    ),
    (
        3, "三碧木星", "三碧木星 (Sanpeki Mokusei)", "Three Jade Wood Star",
        "木", "Wood", "東", "East", "碧", "Jade Green", "#27AE60",
        "積極進取、直率坦誠、精力充沛、創新開拓、好勝心強",
        "Ambitious, frank, energetic, innovative, competitive",
        [3, 4],
    ),
    (
        4, "四綠木星", "四緑木星 (Shiryoku Mokusei)", "Four Green Wood Star",
        "木", "Wood", "東南", "Southeast", "綠", "Green", "#1E8449",
        "溫和有禮、善於溝通、有藝術才華、重視人際關係、信義為先",
        "Gentle, diplomatic, artistic, relationship-oriented, trustworthy",
        [3, 4],
    ),
    (
        5, "五黃土星", "五黄土星 (Goou Dosei)", "Five Yellow Earth Star",
        "土", "Earth", "中宮", "Center", "黃", "Yellow", "#F1C40F",
        "領導才能強、意志堅定、霸氣十足、變化多端、影響力大",
        "Strong leadership, determined, authoritative, versatile, influential",
        [2, 5, 8],
    ),
    (
        6, "六白金星", "六白金星 (Roppaku Kinsei)", "Six White Metal Star",
        "金", "Metal", "西北", "Northwest", "白", "White", "#ECF0F1",
        "正直高尚、責任心強、追求完美、有領袖風範、重視榮譽",
        "Righteous, responsible, perfectionist, leadership qualities, honor-driven",
        [6, 7],
    ),
    (
        7, "七赤金星", "七赤金星 (Shichiseki Kinsei)", "Seven Red Metal Star",
        "金", "Metal", "西", "West", "赤", "Red", "#E74C3C",
        "口才出眾、魅力十足、享受生活、善於社交、靈活變通",
        "Eloquent, charismatic, pleasure-seeking, sociable, flexible",
        [6, 7],
    ),
    (
        8, "八白土星", "八白土星 (Hachihaku Dosei)", "Eight White Earth Star",
        "土", "Earth", "東北", "Northeast", "白", "White", "#F8F9FA",
        "踏實穩健、意志力強、重視家族、善於積累、轉變中成長",
        "Steady, strong-willed, family-focused, accumulative, grows through change",
        [2, 5, 8],
    ),
    (
        9, "九紫火星", "九紫火星 (Kyushi Kasei)", "Nine Purple Fire Star",
        "火", "Fire", "南", "South", "紫", "Purple", "#8E44AD",
        "熱情洋溢、直覺出色、重視禮儀、有藝術鑑賞力、追求完美",
        "Passionate, intuitive, etiquette-conscious, aesthetic, perfectionist",
        [9],
    ),
]

# Star lookup by number (1-9)
STAR_BY_NUM: dict[int, dict] = {}
for _s in NINE_STARS:
    STAR_BY_NUM[_s[0]] = {
        "number": _s[0],
        "zh_name": _s[1],
        "jp_name": _s[2],
        "en_name": _s[3],
        "element_zh": _s[4],
        "element_en": _s[5],
        "direction_zh": _s[6],
        "direction_en": _s[7],
        "color_zh": _s[8],
        "color_en": _s[9],
        "hex_color": _s[10],
        "personality_zh": _s[11],
        "personality_en": _s[12],
        "lucky_numbers": _s[13],
    }

# ============================================================
# 相性表 (Compatibility Matrix)
# ============================================================
# Compatibility score: 3=最佳, 2=良好, 1=普通, 0=需注意
# Based on Five-Element generating/overcoming cycles and traditional tables

_COMPAT_TABLE: dict[tuple[int, int], int] = {
    # 1白水星
    (1, 1): 2, (1, 2): 0, (1, 3): 1, (1, 4): 1,
    (1, 5): 0, (1, 6): 3, (1, 7): 3, (1, 8): 0, (1, 9): 1,
    # 2黑土星
    (2, 1): 0, (2, 2): 2, (2, 3): 0, (2, 4): 0,
    (2, 5): 2, (2, 6): 1, (2, 7): 1, (2, 8): 3, (2, 9): 3,
    # 3碧木星
    (3, 1): 1, (3, 2): 0, (3, 3): 2, (3, 4): 3,
    (3, 5): 0, (3, 6): 0, (3, 7): 0, (3, 8): 0, (3, 9): 3,
    # 4綠木星
    (4, 1): 1, (4, 2): 0, (4, 3): 3, (4, 4): 2,
    (4, 5): 0, (4, 6): 0, (4, 7): 0, (4, 8): 0, (4, 9): 3,
    # 5黃土星
    (5, 1): 0, (5, 2): 2, (5, 3): 0, (5, 4): 0,
    (5, 5): 2, (5, 6): 1, (5, 7): 1, (5, 8): 3, (5, 9): 3,
    # 6白金星
    (6, 1): 3, (6, 2): 1, (6, 3): 0, (6, 4): 0,
    (6, 5): 1, (6, 6): 2, (6, 7): 3, (6, 8): 1, (6, 9): 0,
    # 7赤金星
    (7, 1): 3, (7, 2): 1, (7, 3): 0, (7, 4): 0,
    (7, 5): 1, (7, 6): 3, (7, 7): 2, (7, 8): 1, (7, 9): 0,
    # 8白土星
    (8, 1): 0, (8, 2): 3, (8, 3): 0, (8, 4): 0,
    (8, 5): 3, (8, 6): 1, (8, 7): 1, (8, 8): 2, (8, 9): 3,
    # 9紫火星
    (9, 1): 1, (9, 2): 3, (9, 3): 3, (9, 4): 3,
    (9, 5): 3, (9, 6): 0, (9, 7): 0, (9, 8): 3, (9, 9): 2,
}

COMPAT_LABELS = {
    3: ("最佳 ★★★", "Best ★★★", "#27AE60"),
    2: ("良好 ★★", "Good ★★", "#3498DB"),
    1: ("普通 ★", "Average ★", "#F39C12"),
    0: ("需注意 ☆", "Caution ☆", "#E74C3C"),
}

# ============================================================
# 洛書九宮飛星順序 (Lo Shu Flying Star Order)
# ============================================================
# 逆時針 (陰遁) 飛星宮位順序：5→4→3→2→1→9→8→7→6→5...
# 起始於每月中宮星，按陰遁逆飛

# 月命星起始值 (年命星 → 對應正月（寅月）中宮星)
# 依年命星分三組：
#   組1 (1, 4, 7): 正月中宮 = 8白
#   組2 (2, 5, 8): 正月中宮 = 2黑
#   組3 (3, 6, 9): 正月中宮 = 5黃
_YEAR_STAR_TO_MONTH_BASE: dict[int, int] = {
    1: 8, 4: 8, 7: 8,
    2: 2, 5: 2, 8: 2,
    3: 5, 6: 5, 9: 5,
}

# 陰遁飛星逆飛序列 (counterclockwise)
# Star sequence when flying counterclockwise starting from n: n, n-1, n-2 ... (mod 9, 0→9)
def _fly_star_ccw(start: int, steps: int) -> int:
    """Return the star number after flying *steps* positions counterclockwise from *start*."""
    return ((start - 1 - steps) % 9) + 1


# ============================================================
# 立春日期估算 (Li Chun Date Estimation)
# ============================================================

def _li_chun_date(year: int) -> date:
    """Approximate Li Chun (立春) date for *year*.

    Li Chun falls on Feb 3, 4, or 5 each year. The exact date shifts
    slightly due to the tropical year. This approximation uses a simple
    formula that is accurate within ±1 day for 1901–2100.
    """
    # Standard approximation: Feb 4 or 5 depending on the year's position
    # in the 4-year cycle (leap year offsets)
    # More precise: JDE ≈ 2451623.80984 + 365.242189623 * (Y - 2000 + 0/12)
    # For Li Chun (315° ecliptic lon), offset from Spring equinox ~ -44.7 days
    # Simple empirical formula (accurate to ±1 day 1901-2100):
    #   day = int(4.6295 + 0.2422 * (year - 1900) - int((year - 1900) / 4))
    # But we clamp to [3, 5] and use Feb 4 as default fallback.
    offset = 4.6295 + 0.2422 * (year - 1900) - (year - 1900) // 4
    day = int(offset)
    day = max(3, min(5, day))
    return date(year, 2, day)


# ============================================================
# 年命星計算 (Year Star / Principal Star Calculation)
# ============================================================

def compute_year_star(birth_date: date) -> int:
    """Compute the Year Star (本命星 / Principal Star) number (1–9).

    Uses the solar year starting at Li Chun (立春, ≈Feb 4).
    If birth_date is before Li Chun, the previous year is used.

    Formula:
    1. Sum all digits of the adjusted year, reduce to ≤ 10.
    2. Year Star = 11 − reduced_sum   (result ∈ 1–9; if result = 0 → 9)
    """
    year = birth_date.year
    li_chun = _li_chun_date(year)
    if birth_date < li_chun:
        year -= 1

    # Digit reduction: sum digits until single digit or ≤ 10
    n = sum(int(d) for d in str(year))
    while n > 10:
        n = sum(int(d) for d in str(n))

    star = 11 - n
    if star <= 0:
        star += 9
    return star


# ============================================================
# 月命星計算 (Month Star Calculation)
# ============================================================

# 24節氣月序 (Solar month index, 0=寅月/February)
# Node dates (approximate day-of-month for each 節)
# 寅月=Feb4, 卯月=Mar6, 辰月=Apr5, 巳月=May6, 午月=Jun6, 未月=Jul7,
# 申月=Aug7, 酉月=Sep8, 戌月=Oct8, 亥月=Nov7, 子月=Dec7, 丑月=Jan6(next yr)
_SOLAR_TERM_STARTS: list[tuple[int, int]] = [
    # (month, approx_day) — start of each 節 (Jié)
    (2, 4),   # 寅月 — 立春
    (3, 6),   # 卯月 — 驚蟄
    (4, 5),   # 辰月 — 清明
    (5, 6),   # 巳月 — 立夏
    (6, 6),   # 午月 — 芒種
    (7, 7),   # 未月 — 小暑
    (8, 7),   # 申月 — 立秋
    (9, 8),   # 酉月 — 白露
    (10, 8),  # 戌月 — 寒露
    (11, 7),  # 亥月 — 立冬
    (12, 7),  # 子月 — 大雪
    (1, 6),   # 丑月 — 小寒 (of next year; but belongs to previous solar year)
]


def _solar_month_index(d: date) -> int:
    """Return the solar month index (0–11) for date *d*.

    Index 0 = 寅月 (starts ~Feb 4, Li Chun).
    Index 11 = 丑月 (starts ~Jan 6).
    """
    # Try matching from month 11 (January) down to find the current 節
    # We need to find which solar month the date falls in.
    # Build a list of (date, index) for the current and surrounding years
    year = d.year
    boundaries = []
    for idx, (m, day) in enumerate(_SOLAR_TERM_STARTS):
        if m == 1:
            # 丑月 starts in January — belongs to the current year's cycle
            boundaries.append((date(year, 1, day), idx))
        else:
            boundaries.append((date(year, m, day), idx))
        # Also add previous year's December (子月) boundary
    # Add next year January too
    boundaries.append((date(year + 1, 1, _SOLAR_TERM_STARTS[11][1]), 11))
    # Sort and find the latest boundary ≤ d
    boundaries.sort()
    result = 11  # default 丑月
    for bd, idx in boundaries:
        if d >= bd:
            result = idx
    return result


def compute_month_star(birth_date: date, year_star: int) -> int:
    """Compute the Month Star (月命星) number (1–9).

    Starting from the year-group base star for 寅月 (1st solar month),
    the star flies counterclockwise (陰遁) by one position per solar month.
    """
    base = _YEAR_STAR_TO_MONTH_BASE[year_star]
    solar_month_idx = _solar_month_index(birth_date)
    return _fly_star_ccw(base, solar_month_idx)


# ============================================================
# 日命星計算 (Day Star Calculation)
# ============================================================

# Epoch: 2000-01-06 is known to be Day Star 1 (一白)
# (This is a commonly used reference epoch in Nine Star Ki day calculations.)
_DAY_STAR_EPOCH = date(2000, 1, 6)
_DAY_STAR_EPOCH_STAR = 1


def compute_day_star(birth_date: date) -> int:
    """Compute the Day Star (日命星) number (1–9).

    Uses a 9-day repeating cycle anchored to a known epoch.
    The cycle flies forward (陽遁 for day) — each day the star increases by 1.
    """
    delta = (birth_date - _DAY_STAR_EPOCH).days
    star = ((_DAY_STAR_EPOCH_STAR - 1 + delta) % 9) + 1
    return star


# ============================================================
# 流年星計算 (Annual Star / Current Year Star)
# ============================================================

def compute_annual_star(target_year: int) -> int:
    """Compute the Annual Flying Star (流年星) for *target_year*.

    The annual star is the star occupying the center palace (中宮) in the
    given solar year. It follows the same formula as the year star but
    applied to the target year directly.
    """
    n = sum(int(d) for d in str(target_year))
    while n > 10:
        n = sum(int(d) for d in str(n))
    star = 11 - n
    if star <= 0:
        star += 9
    return star


def compute_annual_month_star(annual_star: int, solar_month_idx: int) -> int:
    """Compute the Monthly Flying Star for the given annual star and solar month."""
    base = _YEAR_STAR_TO_MONTH_BASE[annual_star]
    return _fly_star_ccw(base, solar_month_idx)


# ============================================================
# 相性計算 (Compatibility Calculation)
# ============================================================

def compute_compatibility(star_a: int, star_b: int) -> dict:
    """Return compatibility data between two Year Stars."""
    score = _COMPAT_TABLE.get((star_a, star_b), 1)
    label_zh, label_en, color = COMPAT_LABELS[score]
    return {
        "score": score,
        "label_zh": label_zh,
        "label_en": label_en,
        "color": color,
    }


# ============================================================
# 完整排盤結果 (Full Chart Result)
# ============================================================

@dataclass
class NineStarKiChart:
    """Complete Nine Star Ki chart result."""
    # Birth info
    birth_date: date = field(default_factory=date.today)
    li_chun_date: date = field(default_factory=date.today)
    adjusted_year: int = 0
    is_before_li_chun: bool = False

    # Three stars
    year_star: int = 1
    month_star: int = 1
    day_star: int = 1

    # Star details (from STAR_BY_NUM)
    year_star_info: dict = field(default_factory=dict)
    month_star_info: dict = field(default_factory=dict)
    day_star_info: dict = field(default_factory=dict)

    # Solar month index (0-11)
    solar_month_idx: int = 0

    # Annual star for current year
    current_year_star: int = 1
    current_year_month_star: int = 1

    # Compatibility list for year star vs all others
    compatibility: list = field(default_factory=list)


@st.cache_data(show_spinner=False)
def compute_nine_star_ki_chart(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0,
    timezone: float = 8.0,
    latitude: float = 22.32,
    longitude: float = 114.17,
    location_name: str = "",
) -> NineStarKiChart:
    """Compute a full Nine Star Ki chart.

    Parameters
    ----------
    year, month, day : int
        Birth date.
    hour, minute : int
        Birth time (used for context; day star uses the calendar date only).
    timezone : float
        UTC offset (not used in calculation but kept for API consistency).
    latitude, longitude : float
        Birth location (not used in Nine Star Ki calculation but kept for consistency).
    location_name : str
        Display name of the birth location.

    Returns
    -------
    NineStarKiChart
        Complete chart with year, month, and day stars.
    """
    bd = date(year, month, day)
    lc = _li_chun_date(year)
    adj_year = year if bd >= lc else year - 1
    is_before = bd < lc

    ys = compute_year_star(bd)
    sm_idx = _solar_month_index(bd)
    ms = compute_month_star(bd, ys)
    ds = compute_day_star(bd)

    # Current year stats
    today = date.today()
    cur_year = today.year
    cur_lc = _li_chun_date(cur_year)
    effective_cur_year = cur_year if today >= cur_lc else cur_year - 1
    cas = compute_annual_star(effective_cur_year)
    cur_sm_idx = _solar_month_index(today)
    cams = compute_annual_month_star(cas, cur_sm_idx)

    # Compatibility
    compat = []
    for other in range(1, 10):
        c = compute_compatibility(ys, other)
        c["other_star"] = other
        c["other_star_info"] = STAR_BY_NUM[other]
        compat.append(c)

    return NineStarKiChart(
        birth_date=bd,
        li_chun_date=lc,
        adjusted_year=adj_year,
        is_before_li_chun=is_before,
        year_star=ys,
        month_star=ms,
        day_star=ds,
        year_star_info=STAR_BY_NUM[ys],
        month_star_info=STAR_BY_NUM[ms],
        day_star_info=STAR_BY_NUM[ds],
        solar_month_idx=sm_idx,
        current_year_star=cas,
        current_year_month_star=cams,
        compatibility=compat,
    )


# ============================================================
# 洛書九宮圖 SVG (Lo Shu Square SVG)
# ============================================================

# Lo Shu standard direction mapping: star number → grid position (row, col)
# Standard Lo Shu: 4=SE, 9=S, 2=SW, 3=E, 5=C, 7=W, 8=NE, 1=N, 6=NW
_LO_SHU_POSITIONS: dict[int, tuple[int, int]] = {
    4: (0, 2), 9: (0, 1), 2: (0, 0),
    3: (1, 2), 5: (1, 1), 7: (1, 0),
    8: (2, 2), 1: (2, 1), 6: (2, 0),
}

_LO_SHU_LABELS = {
    (0, 0): "西南 SW", (0, 1): "南 S",  (0, 2): "東南 SE",
    (1, 0): "西 W",   (1, 1): "中 C",  (1, 2): "東 E",
    (2, 0): "西北 NW", (2, 1): "北 N",  (2, 2): "東北 NE",
}


def build_lo_shu_svg(
    highlighted_star: Optional[int] = None,
    year_star: Optional[int] = None,
    month_star: Optional[int] = None,
    day_star: Optional[int] = None,
    width: int = 300,
) -> str:
    """Build an SVG Lo Shu 9-palace diagram.

    Highlights the given star(s) with colored backgrounds.
    """
    cell = width // 3
    h = cell * 3
    pad = 4

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" '
        f'style="font-family:Arial,sans-serif;background:#1a1a2e;border-radius:8px;">'
    ]

    for star_num, (row, col) in _LO_SHU_POSITIONS.items():
        x = col * cell
        y = row * cell
        info = STAR_BY_NUM[star_num]

        # Determine background color
        bg = info["hex_color"]
        # Darken non-highlighted cells
        is_ys = star_num == year_star
        is_ms = star_num == month_star
        is_ds = star_num == day_star
        is_hl = star_num == highlighted_star

        opacity = "ff" if (is_ys or is_ms or is_ds or is_hl) else "44"

        # Stroke
        stroke_color = "#FFD700" if is_ys else ("#87CEEB" if is_ms else ("#90EE90" if is_ds else "#333"))
        stroke_w = 3 if (is_ys or is_ms or is_ds) else 1

        lines.append(
            f'<rect x="{x+1}" y="{y+1}" width="{cell-2}" height="{cell-2}" '
            f'fill="{bg}{opacity}" stroke="{stroke_color}" stroke-width="{stroke_w}" rx="4"/>'
        )

        # Direction label
        dir_label = _LO_SHU_LABELS.get((row, col), "")
        lines.append(
            f'<text x="{x + cell//2}" y="{y + 14}" '
            f'text-anchor="middle" font-size="8" fill="#aaa">{dir_label}</text>'
        )

        # Star number
        lines.append(
            f'<text x="{x + cell//2}" y="{y + cell//2 - 4}" '
            f'text-anchor="middle" font-size="18" font-weight="bold" fill="#fff">{star_num}</text>'
        )

        # Star name
        name_short = info["zh_name"][:3]
        lines.append(
            f'<text x="{x + cell//2}" y="{y + cell//2 + 14}" '
            f'text-anchor="middle" font-size="9" fill="#ddd">{name_short}</text>'
        )

        # Element + color
        elem_label = f"{info['element_zh']}·{info['color_zh']}"
        lines.append(
            f'<text x="{x + cell//2}" y="{y + cell - pad*2}" '
            f'text-anchor="middle" font-size="8" fill="#bbb">{elem_label}</text>'
        )

    # Legend
    legend_items = []
    if year_star:
        legend_items.append(("金框=本命星", "#FFD700"))
    if month_star:
        legend_items.append(("藍框=月命星", "#87CEEB"))
    if day_star:
        legend_items.append(("綠框=日命星", "#90EE90"))

    for li, (ltext, lcolor) in enumerate(legend_items):
        lines.append(
            f'<text x="{width - 4}" y="{h - 8 - li * 12}" '
            f'text-anchor="end" font-size="8" fill="{lcolor}">{ltext}</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


# ============================================================
# Streamlit 渲染函數 (Streamlit Rendering Functions)
# ============================================================

def render_nine_star_ki_chart(
    chart: NineStarKiChart,
    after_chart_hook=None,
    lang: str = "zh",
) -> None:
    """Render the Nine Star Ki chart in Streamlit.

    Parameters
    ----------
    chart : NineStarKiChart
        The computed chart.
    after_chart_hook : callable, optional
        A callable injected after the main chart (e.g. AI button).
    lang : str
        Display language: 'zh' or 'en'.
    """
    import pandas as pd

    is_zh = lang in ("zh", "zh_cn")

    # ── Header ──────────────────────────────────────────────
    st.subheader("🌟 九星氣學 / Japanese Nine Star Ki (Kyūsei Kigaku)")
    if chart.is_before_li_chun:
        lc_str = chart.li_chun_date.strftime("%Y-%m-%d")
        msg = (
            f"⚠️ 出生日期（{chart.birth_date}）在立春（{lc_str}）之前，"
            f"故採用前一年（{chart.adjusted_year}年）計算本命星。"
            if is_zh else
            f"⚠️ Birth date ({chart.birth_date}) is before Li Chun ({lc_str}); "
            f"using previous year ({chart.adjusted_year}) for Year Star."
        )
        st.info(msg)

    # ── Three Stars Overview ─────────────────────────────────
    col_ys, col_ms, col_ds = st.columns(3)

    def _star_card(col, star_info: dict, label_zh: str, label_en: str, border_color: str):
        with col:
            label = label_zh if is_zh else label_en
            bg = star_info["hex_color"]
            st.markdown(
                f'<div style="background:{bg}33;border:2px solid {border_color};'
                f'border-radius:10px;padding:12px;text-align:center;">'
                f'<div style="font-size:28px;font-weight:bold;color:{border_color};">'
                f'{star_info["number"]}</div>'
                f'<div style="font-size:14px;font-weight:bold;">{label}</div>'
                f'<div style="font-size:16px;">{star_info["zh_name"]}</div>'
                f'<div style="font-size:11px;color:#aaa;">{star_info["en_name"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    _star_card(col_ys, chart.year_star_info, "本命星 (年)", "Year Star", "#FFD700")
    _star_card(col_ms, chart.month_star_info, "月命星", "Month Star", "#87CEEB")
    _star_card(col_ds, chart.day_star_info, "日命星", "Day Star", "#90EE90")

    st.markdown("---")

    # ── Lo Shu Square ────────────────────────────────────────
    col_svg, col_detail = st.columns([1, 2])
    with col_svg:
        title = "洛書九宮圖 / Lo Shu Square" if is_zh else "Lo Shu Square"
        st.markdown(f"**{title}**")
        svg = build_lo_shu_svg(
            year_star=chart.year_star,
            month_star=chart.month_star,
            day_star=chart.day_star,
            width=300,
        )
        st.markdown(svg, unsafe_allow_html=True)
        st.caption(
            "金框=本命星 · 藍框=月命星 · 綠框=日命星"
            if is_zh else
            "Gold=Year · Blue=Month · Green=Day"
        )

    with col_detail:
        # Three Stars Detail Table
        detail_title = "三星詳情 / Three Stars Detail" if is_zh else "Three Stars Detail"
        st.markdown(f"**{detail_title}**")
        rows = []
        for star_info, role_zh, role_en in [
            (chart.year_star_info, "本命星", "Year Star"),
            (chart.month_star_info, "月命星", "Month Star"),
            (chart.day_star_info, "日命星", "Day Star"),
        ]:
            rows.append({
                ("角色" if is_zh else "Role"): role_zh if is_zh else role_en,
                ("星數" if is_zh else "Star #"): star_info["number"],
                ("名稱" if is_zh else "Name"): star_info["zh_name"] if is_zh else star_info["en_name"],
                ("五行" if is_zh else "Element"): (
                    star_info["element_zh"] if is_zh else star_info["element_en"]
                ),
                ("方位" if is_zh else "Direction"): (
                    star_info["direction_zh"] if is_zh else star_info["direction_en"]
                ),
                ("顏色" if is_zh else "Color"): (
                    star_info["color_zh"] if is_zh else star_info["color_en"]
                ),
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    st.markdown("---")

    # ── Year Star Detailed Reading ────────────────────────────
    with st.expander(
        f"{'📖 本命星性格解析' if is_zh else '📖 Year Star Personality'} — {chart.year_star_info['zh_name']}",
        expanded=True,
    ):
        ys_info = chart.year_star_info
        cols_info = st.columns(3)
        with cols_info[0]:
            st.metric("五行 Element", ys_info["element_zh"] if is_zh else ys_info["element_en"])
            st.metric("方位 Direction", ys_info["direction_zh"] if is_zh else ys_info["direction_en"])
        with cols_info[1]:
            st.metric("顏色 Color", ys_info["color_zh"] if is_zh else ys_info["color_en"])
            st.metric("吉數 Lucky #", str(ys_info["lucky_numbers"]))
        with cols_info[2]:
            st.metric("日文名 Japanese", ys_info["jp_name"].split("(")[0].strip())

        st.markdown(f"**{'性格特質' if is_zh else 'Personality'}:**")
        st.write(ys_info["personality_zh"] if is_zh else ys_info["personality_en"])

    # ── Month Star Brief ─────────────────────────────────────
    with st.expander(
        f"{'🌙 月命星解析' if is_zh else '🌙 Month Star'} — {chart.month_star_info['zh_name']}",
        expanded=False,
    ):
        ms_info = chart.month_star_info
        sm_names_zh = ["寅月", "卯月", "辰月", "巳月", "午月", "未月",
                        "申月", "酉月", "戌月", "亥月", "子月", "丑月"]
        sm_names_en = ["Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Sheep",
                       "Monkey", "Rooster", "Dog", "Pig", "Rat", "Ox"]
        sm_label = sm_names_zh[chart.solar_month_idx] if is_zh else sm_names_en[chart.solar_month_idx]
        st.caption(
            f"出生太陽月：{sm_label} (第 {chart.solar_month_idx + 1} 節)"
            if is_zh else
            f"Solar Birth Month: {sm_label} (Section {chart.solar_month_idx + 1})"
        )
        c1, c2 = st.columns(2)
        c1.metric("五行", ms_info["element_zh"] if is_zh else ms_info["element_en"])
        c2.metric("方位", ms_info["direction_zh"] if is_zh else ms_info["direction_en"])
        st.write(ms_info["personality_zh"] if is_zh else ms_info["personality_en"])

    # ── Day Star Brief ───────────────────────────────────────
    with st.expander(
        f"{'☀️ 日命星解析' if is_zh else '☀️ Day Star'} — {chart.day_star_info['zh_name']}",
        expanded=False,
    ):
        ds_info = chart.day_star_info
        c1, c2 = st.columns(2)
        c1.metric("五行", ds_info["element_zh"] if is_zh else ds_info["element_en"])
        c2.metric("方位", ds_info["direction_zh"] if is_zh else ds_info["direction_en"])
        st.write(ds_info["personality_zh"] if is_zh else ds_info["personality_en"])

    st.markdown("---")

    # ── Annual / Monthly Stars (流年/流月) ───────────────────
    with st.expander(
        f"{'📅 流年流月九星 / Annual & Monthly Flying Stars' if is_zh else '📅 Annual & Monthly Flying Stars'}",
        expanded=False,
    ):
        today_year = date.today().year
        lc_today = _li_chun_date(today_year)
        effective_year = today_year if date.today() >= lc_today else today_year - 1

        st.markdown(
            f"**{'當前流年星 Current Annual Star'}：{chart.current_year_star} — "
            f"{STAR_BY_NUM[chart.current_year_star]['zh_name']}**"
        )
        st.markdown(
            f"**{'當前流月星 Current Monthly Star'}：{chart.current_year_month_star} — "
            f"{STAR_BY_NUM[chart.current_year_month_star]['zh_name']}**"
        )

        st.caption(
            "流年星居中宮，其他八星依陰遁順序飛入各宮。"
            if is_zh else
            "The annual star occupies the center palace; others fly in counterclockwise order."
        )

        # Show 12-month table for current effective year
        annual_star = chart.current_year_star
        base_star = _YEAR_STAR_TO_MONTH_BASE[annual_star]
        sm_zh = ["寅月(2月)", "卯月(3月)", "辰月(4月)", "巳月(5月)", "午月(6月)", "未月(7月)",
                 "申月(8月)", "酉月(9月)", "戌月(10月)", "亥月(11月)", "子月(12月)", "丑月(1月)"]
        sm_en = ["Tiger(Feb)", "Rabbit(Mar)", "Dragon(Apr)", "Snake(May)", "Horse(Jun)", "Sheep(Jul)",
                 "Monkey(Aug)", "Rooster(Sep)", "Dog(Oct)", "Pig(Nov)", "Rat(Dec)", "Ox(Jan)"]
        monthly_rows = []
        for idx in range(12):
            mstar = _fly_star_ccw(base_star, idx)
            minfo = STAR_BY_NUM[mstar]
            monthly_rows.append({
                ("月份" if is_zh else "Month"): sm_zh[idx] if is_zh else sm_en[idx],
                ("月命星" if is_zh else "Monthly Star"): f"{mstar} {minfo['zh_name'] if is_zh else minfo['en_name']}",
                ("五行" if is_zh else "Element"): minfo["element_zh"] if is_zh else minfo["element_en"],
                ("方位" if is_zh else "Direction"): minfo["direction_zh"] if is_zh else minfo["direction_en"],
            })
        st.dataframe(pd.DataFrame(monthly_rows), hide_index=True, width="stretch")

    # ── Compatibility Table ──────────────────────────────────
    with st.expander(
        f"{'💞 相性分析 / Compatibility Analysis' if is_zh else '💞 Compatibility Analysis'}",
        expanded=False,
    ):
        compat_rows = []
        for c in chart.compatibility:
            other_info = c["other_star_info"]
            compat_rows.append({
                ("對象星" if is_zh else "Other Star"): (
                    f"{c['other_star']} {other_info['zh_name']}"
                    if is_zh else
                    f"{c['other_star']} {other_info['en_name']}"
                ),
                ("五行" if is_zh else "Element"): (
                    other_info["element_zh"] if is_zh else other_info["element_en"]
                ),
                ("相性" if is_zh else "Compatibility"): c["label_zh"] if is_zh else c["label_en"],
            })
        df_compat = pd.DataFrame(compat_rows)
        st.dataframe(df_compat, hide_index=True, width="stretch")
        st.caption(
            "相性以五行生剋關係與傳統九星相性表為準。"
            if is_zh else
            "Compatibility based on Five-Element cycles and traditional Nine Star Ki tables."
        )

    # ── Tooltips / Explanation ───────────────────────────────
    with st.expander(
        f"{'ℹ️ 什麼是九星氣學？' if is_zh else 'ℹ️ What is Nine Star Ki?'}",
        expanded=False,
    ):
        if is_zh:
            st.markdown("""
**九星氣學 (Kyūsei Kigaku)** 是源於中國洛書，在日本廣泛發展的傳統命理體系。

- **立春 (Li Chun / Risshun)**: 每年約2月4日，太陽進入黃道315°，為九星氣學新年的開始。
  若出生於立春前，使用前一年計算本命星。

- **本命星 (Honmeisei / Year Star)**: 以出生年份（立春起算）計算，代表基本性格與人生課題。
  計算公式：將年份各位數相加，縮減至10以下，再用 11 減去該數。

- **月命星 (Tsukimeisei / Month Star)**: 以洛書九宮陰遁飛星方法，
  依本命星所屬組別的寅月起始星，逆飛至出生太陽月，代表感情與直覺面。

- **日命星 (Himeisei / Day Star)**: 以每9天為一循環計算，代表當日性格細節。

- **洛書九宮 (Lo Shu Square)**: 九星各有其方位、五行、顏色，
  在九宮中依陰遁/陽遁飛移，影響風水方位與流年吉凶。

- **流年星 (Nenkan Star)**: 每年中宮星，影響該年整體能量與方位吉凶。
""")
        else:
            st.markdown("""
**Nine Star Ki (Kyūsei Kigaku)** is a traditional divination system originating from the
Chinese Lo Shu square, widely developed in Japan.

- **Li Chun (立春 / Risshun)**: Around Feb 4 each year, when the Sun enters 315° ecliptic.
  This marks the Nine Star Ki New Year. If born before Li Chun, the previous year is used.

- **Year Star (本命星 / Honmeisei)**: Calculated from birth year (Li Chun calendar),
  representing core personality and life themes.
  Formula: sum year digits, reduce to ≤10, then 11 minus that sum.

- **Month Star (月命星 / Tsukimeisei)**: Flying Star method using the counterclockwise
  (陰遁) Lo Shu movement, represents emotional and intuitive aspects.

- **Day Star (日命星 / Himeisei)**: 9-day cycle representing daily character nuances.

- **Lo Shu Square (洛書 / Rakusho)**: Each of the 9 stars occupies a direction, element,
  and color, flying through the 9 palaces annually and monthly.

- **Annual Star (流年星)**: The star in the center palace each year, indicating
  the year's overall energy and auspicious directions.
""")

    # ── After-chart hook (e.g., AI button) ──────────────────
    if after_chart_hook is not None:
        after_chart_hook()
