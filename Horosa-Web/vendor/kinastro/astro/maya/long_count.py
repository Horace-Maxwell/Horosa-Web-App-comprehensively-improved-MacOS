"""
astro/maya/long_count.py — Long Count 長紀年計算
(Long Count Calendar Calculations)

包含 Long Count 日期計算、週期詮釋與歷史事件對照。
Contains Long Count date calculations, period interpretations, and historical events.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .constants import (
    MAYAN_EPOCH_JD,
    KINS_PER_WINAL,
    KINS_PER_TUN,
    KINS_PER_KATUN,
    KINS_PER_BAKTUN,
    KINS_PER_PIKTUN,
    LONG_COUNT_PERIOD_MEANINGS,
    KATUN_THEMES,
    HISTORICAL_LONG_COUNT_EVENTS,
)


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class LongCount:
    """Long Count 完整日期資料"""
    baktun: int
    katun: int
    tun: int
    winal: int
    kin: int

    # Derived
    total_kins: int        # Total days since Mayan epoch
    date_str: str          # e.g., "13.0.7.15.3"

    # Period meanings
    baktun_meaning_cn: str
    baktun_meaning_en: str
    katun_meaning_cn: str
    katun_meaning_en: str

    # Fractional progress within current periods
    progress_in_katun: float    # 0.0–1.0 (progress through current Katun)
    progress_in_baktun: float   # 0.0–1.0 (progress through current Baktun)
    days_in_katun: int          # Days elapsed in the current Katun
    days_in_baktun: int         # Days elapsed in the current Baktun


# ============================================================
# 計算函數 (Calculation Functions) — pure, no Streamlit
# ============================================================

def jd_to_long_count(jd: float) -> LongCount:
    """
    將 Julian Day 轉換為 Long Count。
    Convert Julian Day to Long Count.
    """
    d = int(jd - MAYAN_EPOCH_JD)
    if d < 0:
        d = 0

    baktun = d // KINS_PER_BAKTUN
    rem = d % KINS_PER_BAKTUN
    katun = rem // KINS_PER_KATUN
    rem = rem % KINS_PER_KATUN
    tun = rem // KINS_PER_TUN
    rem = rem % KINS_PER_TUN
    winal = rem // KINS_PER_WINAL
    kin = rem % KINS_PER_WINAL

    date_str = f"{baktun}.{katun}.{tun}.{winal}.{kin}"

    # Period meanings
    baktun_m = LONG_COUNT_PERIOD_MEANINGS["baktun"]
    katun_theme = KATUN_THEMES.get(katun, KATUN_THEMES[0])

    # Progress within current periods
    days_in_baktun = d % KINS_PER_BAKTUN
    days_in_katun  = d % KINS_PER_KATUN
    progress_in_baktun = days_in_baktun / KINS_PER_BAKTUN
    progress_in_katun  = days_in_katun  / KINS_PER_KATUN

    return LongCount(
        baktun=baktun, katun=katun, tun=tun, winal=winal, kin=kin,
        total_kins=d,
        date_str=date_str,
        baktun_meaning_cn=baktun_m["meaning_cn"],
        baktun_meaning_en=baktun_m["meaning_en"],
        katun_meaning_cn=katun_theme["cn"],
        katun_meaning_en=katun_theme["en"],
        progress_in_katun=progress_in_katun,
        progress_in_baktun=progress_in_baktun,
        days_in_katun=days_in_katun,
        days_in_baktun=days_in_baktun,
    )


def long_count_to_jd(baktun: int, katun: int, tun: int, winal: int, kin: int) -> float:
    """
    將 Long Count 轉換為 Julian Day。
    Convert Long Count to Julian Day.
    """
    total = (
        baktun * KINS_PER_BAKTUN +
        katun  * KINS_PER_KATUN +
        tun    * KINS_PER_TUN +
        winal  * KINS_PER_WINAL +
        kin
    )
    return MAYAN_EPOCH_JD + total


def parse_long_count(lc_str: str) -> Optional[tuple[int, int, int, int, int]]:
    """
    解析 Long Count 字串（例如 "13.0.7.15.3"）。
    Parse a Long Count string (e.g., "13.0.7.15.3").

    Returns (baktun, katun, tun, winal, kin) or None on error.
    """
    try:
        parts = [int(p.strip()) for p in lc_str.split(".")]
        if len(parts) != 5:
            return None
        return (parts[0], parts[1], parts[2], parts[3], parts[4])
    except (ValueError, AttributeError):
        return None


def find_nearby_events(jd: float, window_kins: int = 720) -> list[dict]:
    """
    Find historical Long Count events within `window_kins` days of `jd`.
    返回在 window_kins 天範圍內的歷史事件清單。
    """
    results = []
    for event in HISTORICAL_LONG_COUNT_EVENTS:
        parts = parse_long_count(event["long_count"])
        if parts is None:
            continue
        event_jd = long_count_to_jd(*parts)
        diff = abs(event_jd - jd)
        if diff <= window_kins:
            results.append({**event, "delta_days": int(event_jd - jd), "event_jd": event_jd})
    return results


def get_all_events_as_timeline() -> list[dict]:
    """
    Return all historical events with their Julian Day values for timeline display.
    返回所有歷史事件（附 JD）供時間軸顯示。
    """
    timeline = []
    for event in HISTORICAL_LONG_COUNT_EVENTS:
        parts = parse_long_count(event["long_count"])
        if parts is None:
            continue
        event_jd = long_count_to_jd(*parts)
        timeline.append({**event, "event_jd": event_jd})
    return sorted(timeline, key=lambda x: x["event_jd"])


def get_period_summary(lc: LongCount, lang: str = "zh") -> str:
    """
    Return a one-paragraph summary of the current Long Count era.
    返回當前 Long Count 時代的摘要段落。
    """
    if lang == "en":
        return (
            f"You exist in B'ak'tun {lc.baktun}, K'atun {lc.katun}, "
            f"Tun {lc.tun} of the Long Count — {lc.date_str}. "
            f"You are {lc.progress_in_baktun * 100:.1f}% through the current "
            f"~394-year B'ak'tun cycle. {lc.katun_meaning_en}"
        )
    return (
        f"你生活在長紀年 {lc.date_str}，"
        f"第 {lc.baktun} 個 B'ak'tun（文明時代）的 K'atun {lc.katun}，"
        f"當前 B'ak'tun 已完成 {lc.progress_in_baktun * 100:.1f}%。"
        f"{lc.katun_meaning_cn}"
    )
