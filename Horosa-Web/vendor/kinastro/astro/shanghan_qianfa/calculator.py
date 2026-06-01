# -*- coding: utf-8 -*-
"""
astro/shanghan_qianfa/calculator.py — 傷寒鈐法核心計算模組

Algorithm:
  - 普濟方（v1）：以出生年支＋發病日支雙支合算六經
  - 薛氏醫案（v2）：以發病日支直接定六經

Sources:
  - 曹樂齋《普濟方·傷寒鈐法》（明）
  - 薛己《薛氏醫案》（明）
  - 張仲景《傷寒論》（漢）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

import sxtwl

from .constants import (
    TIANGAN,
    DIZHI,
    SIX_CHANNELS,
    DIZHI_CHANNEL_MAP_V1,
    DIZHI_CHANNEL_MAP_V2,
    QIANFA_DOUBLE_MAP_V1,
    SHANGHAN_FORMULAS,
    SHANGHAN_ARTICLES,
    PROGNOSIS_DAYS,
    WUYUN_CHANNEL_MAP,
    LIUQI_YEAR_MAP,
)


# ────────────────────────────────────────────────
# Result dataclass
# ────────────────────────────────────────────────

@dataclass
class ShanghanResult:
    # Birth ganzhi
    birth_year_gz: str = ""
    birth_month_gz: str = ""
    birth_day_gz: str = ""

    # Onset ganzhi
    onset_year_gz: str = ""
    onset_month_gz: str = ""
    onset_day_gz: str = ""

    # Channel determination
    channel: str = ""
    channel_info: dict = field(default_factory=dict)

    # Formulas
    primary_formula: str = ""
    secondary_formulas: list = field(default_factory=list)
    formula_descriptions: dict = field(default_factory=dict)

    # Shanghan Lun articles
    articles: list = field(default_factory=list)

    # Prognosis
    prognosis: str = ""
    transmission_days: list = field(default_factory=list)

    # Meta
    method_version: str = "v1"
    calc_steps: list = field(default_factory=list)

    # Wu Yun context
    wuyun_context: dict = field(default_factory=dict)

    # Dates
    birth_date: Optional[date] = None
    onset_date: Optional[date] = None

    # Raw branch indices (for cross-reference)
    birth_year_dz: str = ""
    onset_day_dz: str = ""


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────

def _get_ganzhi(year: int, month: int, day: int) -> tuple[str, str, str, str, str]:
    """
    Return (year_gz, month_gz, day_gz, year_tg, year_dz) for a solar date.
    Uses sxtwl for accurate Chinese calendar computation.
    """
    lday = sxtwl.fromSolar(year, month, day)
    year_gz_obj = lday.getYearGZ()
    month_gz_obj = lday.getMonthGZ()
    day_gz_obj = lday.getDayGZ()

    y_tg = TIANGAN[year_gz_obj.tg]
    y_dz = DIZHI[year_gz_obj.dz]
    m_tg = TIANGAN[month_gz_obj.tg]
    m_dz = DIZHI[month_gz_obj.dz]
    d_tg = TIANGAN[day_gz_obj.tg]
    d_dz = DIZHI[day_gz_obj.dz]

    return (
        y_tg + y_dz,
        m_tg + m_dz,
        d_tg + d_dz,
        y_tg,
        y_dz,
    )


def _build_transmission_days(channel: str, onset: date) -> list[dict]:
    """Build the 12-day transmission schedule starting from onset date."""
    from datetime import timedelta
    result = []
    channel_order = ["太陽", "陽明", "少陽", "太陰", "少陰", "厥陰"]
    start_idx = channel_order.index(channel) if channel in channel_order else 0

    for prog in PROGNOSIS_DAYS:
        day_num = prog["day"]
        cycled_idx = (start_idx + day_num - 1) % 6
        effective_channel = channel_order[cycled_idx]
        actual_date = onset + timedelta(days=day_num - 1)
        result.append({
            "day": day_num,
            "date": actual_date.strftime("%Y-%m-%d"),
            "channel": effective_channel,
            "channel_en": SIX_CHANNELS.get(effective_channel, {}).get("en", effective_channel),
            "note": prog["note"],
            "icon": SIX_CHANNELS.get(effective_channel, {}).get("icon", ""),
        })
    return result


def _build_wuyun_context(birth_tg: str, birth_dz: str,
                          onset_tg: str, onset_dz: str) -> dict:
    """Build Wu Yun Liu Qi context for birth and onset years."""
    birth_wuyun = WUYUN_CHANNEL_MAP.get(birth_tg, {})
    birth_liuqi = LIUQI_YEAR_MAP.get(birth_dz, {})
    onset_wuyun = WUYUN_CHANNEL_MAP.get(onset_tg, {})
    onset_liuqi = LIUQI_YEAR_MAP.get(onset_dz, {})

    return {
        "birth_yun": birth_wuyun.get("yun", ""),
        "birth_qi": birth_liuqi.get("qi", ""),
        "birth_channel": birth_wuyun.get("channel", ""),
        "onset_yun": onset_wuyun.get("yun", ""),
        "onset_qi": onset_liuqi.get("qi", ""),
        "onset_channel": onset_wuyun.get("channel", ""),
    }


# ────────────────────────────────────────────────
# Main entry point
# ────────────────────────────────────────────────

def compute_shanghan_qianfa(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    onset_year: Optional[int] = None,
    onset_month: Optional[int] = None,
    onset_day: Optional[int] = None,
    method_version: str = "v1",
    location_name: str = "",
    **kwargs,
) -> ShanghanResult:
    """
    Compute 傷寒鈐法 (Shanghan Qianfa) Six-Channel diagnosis.

    Parameters
    ----------
    year, month, day : int
        Birth date (solar calendar).
    onset_year, onset_month, onset_day : int, optional
        Date of illness onset; defaults to today if not provided.
    method_version : str
        "v1" = 普濟方（雙支合算）; "v2" = 薛氏醫案（日支直接法）.
    """
    result = ShanghanResult(method_version=method_version)
    steps: list[str] = []

    # ── Birth ganzhi ──────────────────────────────
    b_year_gz, b_month_gz, b_day_gz, b_tg, b_dz = _get_ganzhi(year, month, day)
    result.birth_year_gz = b_year_gz
    result.birth_month_gz = b_month_gz
    result.birth_day_gz = b_day_gz
    result.birth_date = date(year, month, day)
    result.birth_year_dz = b_dz

    steps.append(f"出生日期：{year}-{month:02d}-{day:02d} → 農曆年干支：{b_year_gz}，月柱：{b_month_gz}，日柱：{b_day_gz}")

    # ── Onset ganzhi ─────────────────────────────
    today = datetime.now().date()
    oy = onset_year  if onset_year  is not None else today.year
    om = onset_month if onset_month is not None else today.month
    od = onset_day   if onset_day   is not None else today.day

    o_year_gz, o_month_gz, o_day_gz, o_tg, o_dz = _get_ganzhi(oy, om, od)
    result.onset_year_gz = o_year_gz
    result.onset_month_gz = o_month_gz
    result.onset_day_gz = o_day_gz
    result.onset_date = date(oy, om, od)

    # Extract the dizhi character from the day gz string (second character)
    o_day_dz = o_day_gz[-1]
    result.onset_day_dz = o_day_dz

    steps.append(f"發病日期：{oy}-{om:02d}-{od:02d} → 日干支：{o_day_gz}，日支：{o_day_dz}")

    # ── Channel determination ──────────────────────
    if method_version == "v2":
        channel = DIZHI_CHANNEL_MAP_V2.get(o_day_dz, "太陽")
        steps.append(f"薛氏醫案法（v2）：直接以發病日支「{o_day_dz}」定六經 → {channel}")
    else:
        # v1: double-branch method
        year_dz_char = b_year_gz[-1]
        channel = QIANFA_DOUBLE_MAP_V1.get((year_dz_char, o_day_dz))
        if channel is None:
            # Fallback to simple map
            channel = DIZHI_CHANNEL_MAP_V1.get(o_day_dz, "太陽")
        steps.append(
            f"普濟方法（v1）：出生年支「{year_dz_char}」＋發病日支「{o_day_dz}」"
            f" → 鈐法合算 → {channel}"
        )

    steps.append(f"六經歸類：{channel}（{SIX_CHANNELS.get(channel, {}).get('en', '')}）")

    result.channel = channel
    result.channel_info = SIX_CHANNELS.get(channel, {})
    result.calc_steps = steps

    # ── Formulas ──────────────────────────────────
    formula_data = SHANGHAN_FORMULAS.get(channel, {})
    result.primary_formula = formula_data.get("primary", "")
    result.secondary_formulas = formula_data.get("secondary", [])
    result.formula_descriptions = formula_data.get("descriptions", {})

    # ── Shanghan Lun articles ─────────────────────
    result.articles = SHANGHAN_ARTICLES.get(channel, [])

    # ── Prognosis ─────────────────────────────────
    channel_info = SIX_CHANNELS.get(channel, {})
    result.prognosis = channel_info.get("prognosis", "")
    result.transmission_days = _build_transmission_days(channel, result.onset_date)

    # ── Wu Yun context ────────────────────────────
    result.wuyun_context = _build_wuyun_context(b_tg, b_dz, o_tg, o_dz)

    return result
