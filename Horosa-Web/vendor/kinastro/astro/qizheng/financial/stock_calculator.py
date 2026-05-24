"""
股票七政四餘排盤計算模組 (Stock Astrology Calculator)

以股票上市日期+時間作為「出生盤」進行七政四餘排盤，
並計算流日流時吉凶（當日/當時星曜落宮及四餘飛星化曜）。
"""

from __future__ import annotations

import streamlit as st
import swisseph as swe
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone as tz_cls
from typing import Optional

from ..calculator import (
    ChartData, PlanetPosition,
    _normalize_degree, _get_western_sign, _get_chinese_sign,
    _degree_to_sign_degree,
)
from ..constants import SEVEN_GOVERNORS, FOUR_REMAINDERS, FIVE_ELEMENTS, TWELVE_PALACES


# ============================================================
# 流日流時吉凶規則（傳統七政四餘飛星）
# ============================================================

# 每顆行星對流日流時的基本吉凶傾向
_DAILY_PLANET_FORTUNE = {
    "太陽": {"score": 2,  "zh": "日曜主旺，事業光明",         "en": "Sun empowers career & status"},
    "太陰": {"score": 1,  "zh": "月曜主流動，財資周轉順",      "en": "Moon favors liquidity & cash flow"},
    "木星": {"score": 3,  "zh": "木星入廟，利多頭擴張",        "en": "Jupiter in glory — bullish expansion"},
    "金星": {"score": 2,  "zh": "金曜主享受，利短線操作",      "en": "Venus favors short-term gains"},
    "水星": {"score": 1,  "zh": "水曜主交易，資訊流通利市",    "en": "Mercury boosts trading & information"},
    "火星": {"score": -2, "zh": "火曜主衝突，防市場震盪",      "en": "Mars warns of conflict & volatility"},
    "土星": {"score": -2, "zh": "土星主收縮，謹慎保守布局",    "en": "Saturn cautions conservative positioning"},
    "羅睺": {"score": 1,  "zh": "羅睺守財帛，橫財機遇現",     "en": "Rahu in wealth house — windfall opportunity"},
    "計都": {"score": -1, "zh": "計都業力，防舊帳重現",        "en": "Ketu brings karmic debt to light"},
    "月孛": {"score": -1, "zh": "月孛暗耗，防隱性財損",        "en": "Moon's Apogee — hidden financial drain"},
    "紫氣": {"score": 2,  "zh": "紫氣貴人，適合尋求合作",      "en": "Purple Star attracts noble patrons"},
}

# 逆行懲罰（四捨五入至整數）
_RETROGRADE_PENALTY = {
    "木星": -1,
    "金星": -1,
    "水星": -2,
    "土星":  1,   # 土星逆行反而減壓
    "火星": -1,
}

# 七政四餘吉凶星次對照
# 入廟得力 (+2)、旺相得力 (+1)、失落 (-1)、陷落 (-2)
_SIGN_DIGNITY = {
    "木星": {"射手": 2, "雙魚": 2, "巨蟹": 1, "牡羊": 1, "雙子": -1, "處女": -2},
    "土星": {"摩羯": 2, "水瓶": 2, "天秤": 1, "牡羊": -2, "巨蟹": -1, "獅子": -1},
    "金星": {"金牛": 2, "天秤": 2, "雙魚": 1, "牡羊": -2, "天蠍": -2, "處女": -1},
    "火星": {"牡羊": 2, "天蠍": 2, "摩羯": 1, "天秤": -1, "金牛": -2, "巨蟹": -2},
    "水星": {"處女": 2, "雙子": 2, "水瓶": 1, "射手": -1, "雙魚": -2, "獅子": -1},
    "太陽": {"獅子": 2, "牡羊": 1, "水瓶": -1, "天秤": -2},
    "太陰": {"巨蟹": 2, "金牛": 1, "摩羯": -2, "天蠍": -1},
}

# ============================================================
# 時辰吉凶：傳統七政行星時（Chaldean Planetary Hours）
# ============================================================

# 迦勒底順序（由慢至快）：土星 木星 火星 太陽 金星 水星 太陰
_CHALDEAN_ORDER = ["土星", "木星", "火星", "太陽", "金星", "水星", "太陰"]
# 各星曜迦勒底索引（由 weekday 推日主）
# weekday: 0=Mon(太陰=6), 1=Tue(火星=2), 2=Wed(水星=5), 3=Thu(木星=1),
#          4=Fri(金星=4), 5=Sat(土星=0), 6=Sun(太陽=3)
_WEEKDAY_DAY_RULER_IDX = {0: 6, 1: 2, 2: 5, 3: 1, 4: 4, 5: 0, 6: 3}
# 日出大約 06:00，故午夜00:00對應 offset = 0 - 6 = -6 ≡ +1 (mod 7)
_MIDNIGHT_OFFSET = -6

# 月亮守照相位分數（positive = benefic side, negative = malefic）
_MOON_ASPECT_ORBS: dict[int, float] = {0: 8.0, 60: 6.0, 90: 8.0, 120: 8.0, 180: 9.0}
_MOON_ASPECT_WEIGHTS: dict[int, float] = {0: 2.0, 60: 1.0, 90: -1.5, 120: 1.5, 180: -2.0}
_MOON_PLANET_MODIFIER: dict[str, float] = {
    "太陽": 1.0, "木星": 1.0, "金星": 1.0, "紫氣": 0.8, "水星": 0.4,
    "火星": -1.0, "土星": -1.0, "計都": -0.8, "月孛": -0.7, "羅睺": -0.3,
}


def _get_planetary_hour_score(query_date: date, query_hour: int) -> int:
    """計算當前時辰的行星時星曜吉凶分數（傳統迦勒底行星時）。"""
    weekday = query_date.weekday()
    day_ruler_idx = _WEEKDAY_DAY_RULER_IDX[weekday]
    # 午夜00:00 = 日出(06:00)前 6 小時，序列向前移 6 位
    hour_idx = (day_ruler_idx + _MIDNIGHT_OFFSET + query_hour) % 7
    hour_ruler = _CHALDEAN_ORDER[hour_idx]
    return _DAILY_PLANET_FORTUNE.get(hour_ruler, {}).get("score", 0)


def _moon_aspect_score(moon_lon: float, planets: list[PlanetPosition]) -> int:
    """依月亮與各行星的精確守照角度，計算時辰吉凶附加分。"""
    score = 0.0
    for p in planets:
        if p.name in ("太陰",):
            continue
        diff = abs(moon_lon - p.longitude) % 360
        if diff > 180:
            diff = 360 - diff
        modifier = _MOON_PLANET_MODIFIER.get(p.name, 0.0)
        if modifier == 0.0:
            continue
        for aspect_deg, orb in _MOON_ASPECT_ORBS.items():
            angle_diff = abs(diff - aspect_deg)
            if angle_diff <= orb:
                proximity = 1.0 - angle_diff / orb
                score += _MOON_ASPECT_WEIGHTS[aspect_deg] * modifier * proximity
    return round(score)


@dataclass
class DailyFortuneEntry:
    """流日流時單一星曜吉凶條目"""
    planet: str
    sign_zh: str
    sign_en: str
    longitude: float
    retrograde: bool
    score: int
    judgment_zh: str   # 斷語（中文）
    judgment_en: str   # 斷語（英文）
    color: str         # 吉凶顏色（hex）


@dataclass
class DailyFortuneData:
    """流日流時吉凶計算結果"""
    query_date: date
    query_hour: int
    timezone: float
    julian_day: float
    entries: list = field(default_factory=list)   # List[DailyFortuneEntry]
    total_score: int = 0
    overall_zh: str = ""
    overall_en: str = ""


@dataclass
class StockChartData:
    """股票七政四餘完整分析結果"""
    # 上市出生盤
    ipo_chart: Optional[ChartData] = None
    ipo_planets: list = field(default_factory=list)   # 上市盤行星 List[PlanetPosition]
    ipo_jd: float = 0.0
    # 流日流時
    daily_fortune: Optional[DailyFortuneData] = None
    # 股價比例強弱
    price_ratio: Optional[float] = None              # 0~100%
    strength_label_zh: str = ""
    strength_label_en: str = ""
    strength_color: str = "#9090b8"
    # 流時飛星文字
    transit_summary_zh: str = ""
    transit_summary_en: str = ""


# ============================================================
# 計算函數
# ============================================================

def _calc_planets_at_jd(jd: float) -> list:
    """計算指定 Julian Day 的七政四餘行星位置列表。"""
    swe.set_ephe_path("")
    planets = []

    for name, planet_id in SEVEN_GOVERNORS.items():
        try:
            result, _ = swe.calc_ut(jd, planet_id)
        except Exception:
            continue
        lon = _normalize_degree(result[0])
        planets.append(PlanetPosition(
            name=name,
            longitude=lon,
            latitude=result[1],
            sign_western=_get_western_sign(lon),
            sign_chinese=_get_chinese_sign(lon),
            sign_degree=_degree_to_sign_degree(lon),
            element=FIVE_ELEMENTS.get(name, ""),
            retrograde=(result[3] < 0),
        ))

    # 四餘：羅睺、計都
    try:
        ketu_r, _ = swe.calc_ut(jd, FOUR_REMAINDERS["計都"])
        ketu_lon = _normalize_degree(ketu_r[0])
        rahu_lon = _normalize_degree(ketu_lon + 180.0)
        for name, lon, lat in [
            ("羅睺", rahu_lon, -ketu_r[1]),
            ("計都", ketu_lon,  ketu_r[1]),
        ]:
            planets.append(PlanetPosition(
                name=name, longitude=lon, latitude=lat,
                sign_western=_get_western_sign(lon),
                sign_chinese=_get_chinese_sign(lon),
                sign_degree=_degree_to_sign_degree(lon),
                element=FIVE_ELEMENTS.get(name, ""), retrograde=False,
            ))
    except Exception:
        pass

    for fname in ("月孛", "紫氣"):
        try:
            r, _ = swe.calc_ut(jd, FOUR_REMAINDERS[fname])
            lon = _normalize_degree(r[0])
            planets.append(PlanetPosition(
                name=fname, longitude=lon, latitude=r[1],
                sign_western=_get_western_sign(lon),
                sign_chinese=_get_chinese_sign(lon),
                sign_degree=_degree_to_sign_degree(lon),
                element=FIVE_ELEMENTS.get(fname, ""), retrograde=False,
            ))
        except Exception:
            pass

    return planets


def _planet_score(p: PlanetPosition) -> tuple[int, str, str]:
    """
    計算單一行星的流日流時吉凶分數及斷語。
    Returns (score, judgment_zh, judgment_en)
    """
    base = _DAILY_PLANET_FORTUNE.get(p.name, {})
    score = base.get("score", 0)
    desc_zh = base.get("zh", "")
    desc_en = base.get("en", "")

    # 逆行修正
    if p.retrograde:
        penalty = _RETROGRADE_PENALTY.get(p.name, -1)
        score += penalty
        retro_zh = f"（逆行{'減能' if penalty < 0 else '緩壓'}）"
        retro_en = f" (Retrograde {'weakens' if penalty < 0 else 'softens'})"
        desc_zh += retro_zh
        desc_en += retro_en

    # 星座尊貴/失落修正（只做七政）
    dignity_map = _SIGN_DIGNITY.get(p.name, {})
    # 用中文星座名（去掉西方長名前三字）
    sign_key = p.sign_western[:3] if p.sign_western else ""
    # 改用中文星次判斷
    for sign_zh, mod in dignity_map.items():
        if sign_zh in p.sign_chinese:
            score += mod
            if mod >= 2:
                desc_zh += f"，入廟得力+{mod}"
                desc_en += f", in domicile +{mod}"
            elif mod == 1:
                desc_zh += "，旺相得力+1"
                desc_en += ", exaltation +1"
            elif mod == -1:
                desc_zh += "，失令-1"
                desc_en += ", in detriment -1"
            elif mod <= -2:
                desc_zh += f"，陷落{mod}"
                desc_en += f", in fall {mod}"
            break

    return score, desc_zh, desc_en


@st.cache_data(ttl=300, show_spinner=False)
def compute_daily_fortune(
    query_year: int, query_month: int, query_day: int,
    query_hour: int,
    timezone: float,
) -> DailyFortuneData:
    """
    計算指定流日流時的七政四餘吉凶。

    Parameters:
        query_year/month/day: 查詢日期
        query_hour: 查詢時辰（0-23）
        timezone: 時區偏移

    Returns:
        DailyFortuneData
    """
    decimal_hour = query_hour + 0.5 - timezone   # 取時辰中點
    jd = swe.julday(query_year, query_month, query_day, decimal_hour)
    planets = _calc_planets_at_jd(jd)

    entries = []
    total = 0
    moon_lon: float = 0.0
    for p in planets:
        score, j_zh, j_en = _planet_score(p)
        total += score
        if p.name == "太陰":
            moon_lon = p.longitude
        if score >= 2:
            color = "#FFD700"
        elif score == 1:
            color = "#86efac"
        elif score == 0:
            color = "#60a5fa"
        elif score == -1:
            color = "#fb923c"
        else:
            color = "#f87171"
        entries.append(DailyFortuneEntry(
            planet=p.name,
            sign_zh=p.sign_chinese,
            sign_en=p.sign_western,
            longitude=p.longitude,
            retrograde=p.retrograde,
            score=score,
            judgment_zh=j_zh,
            judgment_en=j_en,
            color=color,
        ))

    # 行星時吉凶（傳統迦勒底行星時，逐時輪替）
    total += _get_planetary_hour_score(date(query_year, query_month, query_day), query_hour)

    # 月亮守照附加分（依月亮精確度數計算對各星的相位）
    total += _moon_aspect_score(moon_lon, planets)

    # 整體斷語
    if total >= 8:
        overall_zh = "今時諸星皆吉，大利多頭，宜積極操作。"
        overall_en = "All stars auspicious — bullish energy, active trading favored."
    elif total >= 4:
        overall_zh = "今時財星得力，偏向多頭，謹慎擇機入場。"
        overall_en = "Wealth stars empowered — moderate bullish, select entry carefully."
    elif total >= 0:
        overall_zh = "今時星力平和，宜觀望，靜待明確信號。"
        overall_en = "Stars in balance — wait and observe for clear signals."
    elif total >= -4:
        overall_zh = "今時凶星偏多，市場震盪，宜守不宜進。"
        overall_en = "Challenging stars dominate — volatility expected, avoid new positions."
    else:
        overall_zh = "今時凶星煞氣重，防大幅波動，宜出清保守。"
        overall_en = "Strong malefic energy — significant risk, consider exiting positions."

    return DailyFortuneData(
        query_date=date(query_year, query_month, query_day),
        query_hour=query_hour,
        timezone=timezone,
        julian_day=jd,
        entries=entries,
        total_score=total,
        overall_zh=overall_zh,
        overall_en=overall_en,
    )


@st.cache_data(ttl=600, show_spinner=False)
def compute_stock_chart(
    ipo_year: int, ipo_month: int, ipo_day: int,
    ipo_hour: int, ipo_minute: int,
    timezone: float,
    # 股價比例參數
    current_price: Optional[float],
    week52_high: Optional[float],
    week52_low: Optional[float],
    # 流日流時查詢
    query_year: int, query_month: int, query_day: int,
    query_hour: int,
) -> StockChartData:
    """
    以上市日期時間作為「出生盤」，計算股票七政四餘完整分析。

    Parameters:
        ipo_*: 上市日期與時間（出生盤用）
        timezone: 時區
        current_price/week52_high/week52_low: 股價資料（用於計算強弱度）
        query_*: 流日流時查詢時間

    Returns:
        StockChartData
    """
    from .stock_fetcher import get_strength_label

    # ── IPO 出生盤行星 ────────────────────────────────────
    decimal_hour = ipo_hour + ipo_minute / 60.0 - timezone
    ipo_jd = swe.julday(ipo_year, ipo_month, ipo_day, decimal_hour)
    ipo_planets = _calc_planets_at_jd(ipo_jd)

    # ── 流日流時吉凶 ──────────────────────────────────────
    daily_fortune = compute_daily_fortune(
        query_year=query_year, query_month=query_month,
        query_day=query_day, query_hour=query_hour,
        timezone=timezone,
    )

    # ── 股價比例強弱度 ────────────────────────────────────
    if (
        current_price is not None
        and week52_high is not None
        and week52_low is not None
        and week52_high != week52_low
    ):
        price_ratio: Optional[float] = max(0.0, min(1.0,
            (current_price - week52_low) / (week52_high - week52_low)
        )) * 100.0
    else:
        price_ratio = None
    sl_zh, sl_en, sl_color = get_strength_label(price_ratio)

    # ── 流時飛星摘要文字 ──────────────────────────────────
    top_good = [e for e in daily_fortune.entries if e.score >= 2]
    top_bad  = [e for e in daily_fortune.entries if e.score <= -2]
    good_str = "、".join(e.planet for e in top_good[:3])
    bad_str  = "、".join(e.planet for e in top_bad[:3])
    ratio_str = f"{price_ratio:.0f}%" if price_ratio is not None else "N/A"

    transit_zh = (
        f"流時吉星：{good_str or '無'} | 凶星：{bad_str or '無'} | "
        f"股價強弱度：{ratio_str}（{sl_zh}）"
    )
    transit_en = (
        f"Auspicious: {', '.join(e.planet for e in top_good[:3]) or 'None'} | "
        f"Malefic: {', '.join(e.planet for e in top_bad[:3]) or 'None'} | "
        f"Price Strength: {ratio_str} ({sl_en})"
    )

    return StockChartData(
        ipo_planets=ipo_planets,
        ipo_jd=ipo_jd,
        daily_fortune=daily_fortune,
        price_ratio=price_ratio,
        strength_label_zh=sl_zh,
        strength_label_en=sl_en,
        strength_color=sl_color,
        transit_summary_zh=transit_zh,
        transit_summary_en=transit_en,
    )
