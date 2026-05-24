"""
七政四餘金融占星模組 (Financial Astrology Module for Seven Governors and Four Remainders)

整合七政四餘傳統財星理論與現代金融占星，提供：
- 財富行星總覽 (Wealth Planet Overview)
- 木星-土星週期分析 (Jupiter-Saturn Cycle Analysis)
- 關鍵財富過運 (Key Wealth Transits)
- 歷史金融事件相關性 (Historical Financial Correlations)
- 當前金融展望 (Current Financial Outlook)

Integrates classical Chinese Seven Governors theory with modern Financial Astrology,
covering Jupiter-Saturn Great Conjunctions, outer planet transits, and market timing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone as tz_cls
from typing import Optional

import pandas as pd
import streamlit as st
import swisseph as swe

from .calculator import (
    ChartData, PlanetPosition,
    _normalize_degree, _get_western_sign, _get_chinese_sign,
    _degree_to_sign_degree,
    get_stock_lingyun_chart,
)
from .constants import FIVE_ELEMENTS, TWELVE_SIGNS_WESTERN
from .financial.gann_macro_stock import (
    GANN_NATAL_DEFAULT,
    GANN_NATAL_PRESETS,
    GANN_NATAL_REFERENCE_PRICES,
    build_gann_macro_timing,
    compute_square_of_nine_levels,
)
from .financial.backtesting import run_backtest_mvp
from .financial.data_loader import load_great_conjunctions, load_historical_events
from .financial.financial_scoring import classify_wealth_score, compute_wealth_score_breakdown
from .financial.transit_search import angle_diff, find_all_aspect_hits, find_closest_event, signed_angle_to_target


# ============================================================
# 財富相關行星對照 (Wealth-Related Planet Mapping)
# 傳統七政四餘財星判斷：木星（擴張）、土星（收縮）、
# 紫氣（貴氣財源）、月孛（暗財）、羅睺（橫財）、計都（業力財）
# ============================================================

# 財星能量（正值=有利，負值=挑戰）
_WEALTH_PLANET_ENERGY = {
    "太陽": {"score": 1, "zh": "事業財源", "en": "Career & Status Wealth"},
    "太陰": {"score": 1, "zh": "月收入、流動資金", "en": "Monthly Income & Liquidity"},
    "木星": {"score": 3, "zh": "擴張財星（最吉）", "en": "Expansion Planet (Most Auspicious)"},
    "金星": {"score": 2, "zh": "享受財、投資財", "en": "Pleasure & Investment Wealth"},
    "水星": {"score": 1, "zh": "交易財、流通財", "en": "Trade & Circulation Wealth"},
    "火星": {"score": -1, "zh": "競爭風險", "en": "Competition & Risk"},
    "土星": {"score": -1, "zh": "收縮、延遲", "en": "Contraction & Delay"},
    "羅睺": {"score": 2, "zh": "橫財、外來財", "en": "Windfall & Foreign Wealth"},
    "計都": {"score": -1, "zh": "業力損失", "en": "Karmic Loss"},
    "月孛": {"score": 1, "zh": "隱藏財源", "en": "Hidden Wealth Source"},
    "紫氣": {"score": 3, "zh": "貴人財、紫氣財星", "en": "Noble Patron Wealth"},
}

# 財帛宮索引（七政四餘第二宮）
_CAIBO_HOUSE_INDEX = 1

@st.cache_data(ttl=3600, show_spinner=False)
def _get_historical_events() -> list[dict]:
    """快取歷史金融事件資料。"""
    return load_historical_events()


@st.cache_data(ttl=3600, show_spinner=False)
def _get_great_conjunctions() -> list[dict]:
    """快取木土大合相資料。"""
    return load_great_conjunctions()


# ============================================================
# 資料類別定義
# ============================================================

@dataclass
class FinancialData:
    """金融占星計算結果 / Financial Astrology Computed Result"""
    # 財星位置列表（含財富能量評分）
    wealth_planets: list = field(default_factory=list)
    # 財帛宮行星
    caibo_planets: list = field(default_factory=list)
    # 木星當前位置
    jupiter_pos: Optional[PlanetPosition] = None
    # 土星當前位置
    saturn_pos: Optional[PlanetPosition] = None
    # 下一次木土合相（近似）
    next_conjunction: Optional[dict] = None
    # 未來 12 個月重要過運列表
    upcoming_transits: list = field(default_factory=list)
    # 整體財富能量分數
    total_wealth_score: int = 0
    # 分層評分細節
    wealth_score_breakdown: dict = field(default_factory=dict)
    # 財富運勢摘要文字
    summary_zh: str = ""
    summary_en: str = ""


# ============================================================
# 計算函數
# ============================================================

@st.cache_data(ttl=1800, show_spinner=False)
def compute_financial_aspects(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float,
    latitude: float, longitude: float,
    gender: str = "male",
) -> FinancialData:
    """
    計算七政四餘金融占星關鍵指標。
    Compute key Financial Astrology indicators from the Seven Governors chart.

    Parameters:
        year, month, day, hour, minute: 出生時間 / birth datetime
        timezone: 時區 / timezone offset
        latitude, longitude: 出生地坐標 / birth coordinates
        gender: 性別

    Returns:
        FinancialData
    """
    swe.set_ephe_path("")
    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    # ── 取得出生盤行星位置 ──────────────────────────────────
    from .calculator import (
        _get_mansion_info, _degree_to_sign_degree, _check_qidu,
        _get_sign_element, _get_western_sign, _get_chinese_sign,
    )
    from .constants import SEVEN_GOVERNORS, FOUR_REMAINDERS

    planets = []
    # 七政
    for name, planet_id in SEVEN_GOVERNORS.items():
        result, _ = swe.calc_ut(jd, planet_id)
        lon = _normalize_degree(result[0])
        lat = result[1]
        speed = result[3]
        pos = PlanetPosition(
            name=name, longitude=lon, latitude=lat,
            sign_western=_get_western_sign(lon),
            sign_chinese=_get_chinese_sign(lon),
            sign_degree=_degree_to_sign_degree(lon),
            element=FIVE_ELEMENTS.get(name, ""),
            retrograde=(speed < 0),
        )
        planets.append(pos)

    # 四餘
    ketu_result, _ = swe.calc_ut(jd, FOUR_REMAINDERS["計都"])
    ketu_lon = _normalize_degree(ketu_result[0])
    rahu_lon = _normalize_degree(ketu_lon + 180.0)

    for name, lon, lat in [
        ("羅睺", rahu_lon, -ketu_result[1]),
        ("計都", ketu_lon,  ketu_result[1]),
    ]:
        planets.append(PlanetPosition(
            name=name, longitude=lon, latitude=lat,
            sign_western=_get_western_sign(lon),
            sign_chinese=_get_chinese_sign(lon),
            sign_degree=_degree_to_sign_degree(lon),
            element=FIVE_ELEMENTS.get(name, ""), retrograde=False,
        ))

    for name, planet_id in [("月孛", FOUR_REMAINDERS["月孛"]), ("紫氣", FOUR_REMAINDERS["紫氣"])]:
        result, _ = swe.calc_ut(jd, planet_id)
        lon = _normalize_degree(result[0])
        planets.append(PlanetPosition(
            name=name, longitude=lon, latitude=result[1],
            sign_western=_get_western_sign(lon),
            sign_chinese=_get_chinese_sign(lon),
            sign_degree=_degree_to_sign_degree(lon),
            element=FIVE_ELEMENTS.get(name, ""), retrograde=False,
        ))

    # ── 宮位計算（取得財帛宮行星）────────────────────────
    cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")
    caibo_cusp = cusps[_CAIBO_HOUSE_INDEX]    # 第二宮宮頭
    caibo_end  = cusps[(_CAIBO_HOUSE_INDEX + 1) % 12]

    def _in_house(lon: float, start: float, end: float) -> bool:
        if start < end:
            return start <= lon < end
        return lon >= start or lon < end  # 跨越0°

    caibo_planets = [p for p in planets if _in_house(p.longitude, caibo_cusp, caibo_end)]

    # ── 財富能量評分（分層模型）───────────────────────────
    wealth_planets = []
    for p in planets:
        info = _WEALTH_PLANET_ENERGY.get(p.name)
        if info:
            entry = dict(info)
            entry["planet"] = p
            wealth_planets.append(entry)
    score_breakdown = compute_wealth_score_breakdown(planets, tuple(cusps))
    total_score = int(round(score_breakdown.total_score))

    # ── 取得木星與土星的位置物件 ────────────────────────
    jupiter_pos = next((p for p in planets if p.name == "木星"), None)
    saturn_pos  = next((p for p in planets if p.name == "土星"), None)

    # ── 估算下一次木土合相（迭代法，步進30天）──────────
    next_conjunction = _estimate_next_conjunction(jd)

    # ── 未來 12 個月關鍵過運（木星、土星對出生盤關鍵點）──
    upcoming_transits = _compute_upcoming_wealth_transits(
        birth_jd=jd,
        birth_planets=planets,
        birth_caibo_cusp=caibo_cusp,
        tz=timezone,
    )

    # ── 財富摘要文字 ─────────────────────────────────
    summary_zh, summary_en = _generate_summary(total_score, jupiter_pos, saturn_pos, caibo_planets)

    return FinancialData(
        wealth_planets=wealth_planets,
        caibo_planets=caibo_planets,
        jupiter_pos=jupiter_pos,
        saturn_pos=saturn_pos,
        next_conjunction=next_conjunction,
        upcoming_transits=upcoming_transits,
        total_wealth_score=total_score,
        wealth_score_breakdown={
            "base_score": round(score_breakdown.base_score, 2),
            "dignity_score": round(score_breakdown.dignity_score, 2),
            "aspect_score": round(score_breakdown.aspect_score, 2),
            "house_lord_score": round(score_breakdown.house_lord_score, 2),
            "total_score": round(score_breakdown.total_score, 2),
        },
        summary_zh=summary_zh,
        summary_en=summary_en,
    )


def _estimate_next_conjunction(from_jd: float) -> dict:
    """
    從指定 Julian Day 往後搜尋下一次木土合相（黃經差 < 1°）。
    步進 30 天，精度約 ±15 天。
    Search for the next Jupiter-Saturn conjunction (longitude diff < 1°) after from_jd.
    """
    try:
        end_jd = from_jd + 365.2425 * 45.0

        def _func(jd: float) -> float:
            jup, _ = swe.calc_ut(jd, swe.JUPITER)
            sat, _ = swe.calc_ut(jd, swe.SATURN)
            return signed_angle_to_target(jup[0], sat[0])

        result = find_closest_event(
            _func,
            start_jd=from_jd,
            end_jd=end_jd,
            coarse_step=10.0,
            tolerance=1e-5,
        )
        jup, _ = swe.calc_ut(result.jd, swe.JUPITER)
        sat, _ = swe.calc_ut(result.jd, swe.SATURN)
        orb = angle_diff(jup[0], sat[0])
        if orb > 2.0:
            return {}
        yr, mo, dy, hr = swe.revjul(result.jd)
        lon = _normalize_degree(jup[0])
        return {
            "year": yr,
            "month": mo,
            "day": int(dy),
            "longitude": lon,
            "sign": TWELVE_SIGNS_WESTERN[int(lon / 30)],
            "sign_degree": lon % 30,
            "orb": round(orb, 4),
            "converged": result.converged,
            "solver": result.method,
        }
    except Exception:
        pass
    return {}


def _compute_upcoming_wealth_transits(
    birth_jd: float,
    birth_planets: list,
    birth_caibo_cusp: float,
    tz: float,
) -> list:
    """
    計算未來 12 個月內木星、土星、天王星對出生盤關鍵點的主要相位。
    Key aspects: conjunction (0°), sextile (60°), square (90°), trine (120°), opposition (180°)
    Returns a list of dicts sorted by date.
    """
    results = []

    # 關鍵出生盤感受點：木星、土星、紫氣、財帛宮宮頭
    natal_points = []
    for p in birth_planets:
        if p.name in ("木星", "土星", "紫氣", "羅睺", "太陽", "太陰"):
            natal_points.append((p.name, p.longitude))
    natal_points.append(("財帛宮", birth_caibo_cusp))

    transit_planets = {
        "木星": swe.JUPITER,
        "土星": swe.SATURN,
        "天王星": swe.URANUS,
    }

    aspect_angles = {
        "合相 0°": 0,
        "六合 60°": 60,
        "刑 90°": 90,
        "三合 120°": 120,
        "對沖 180°": 180,
    }

    orb = 3.0   # 容許度 / orb tolerance
    # 以「現在」為掃描起點 / start scan from current moment
    utc_now = datetime.now(tz=tz_cls.utc)
    local_now = utc_now + timedelta(hours=tz)
    now_jd = swe.julday(
        local_now.year, local_now.month, local_now.day,
        local_now.hour + local_now.minute / 60.0,
    )

    end_jd = now_jd + 365.0

    for t_name, t_id in transit_planets.items():
        def _transit_lon(jd: float, _pid=t_id) -> float:
            result, _ = swe.calc_ut(jd, _pid)
            return _normalize_degree(result[0])

        for n_name, n_lon in natal_points:
            for aspect_name, angle in aspect_angles.items():
                hits = find_all_aspect_hits(
                    lambda jd, _n=n_lon, _f=_transit_lon: _normalize_degree(_f(jd) - _n),
                    target_angle=float(angle),
                    start_jd=now_jd,
                    end_jd=end_jd,
                    orb=orb,
                    coarse_step=2.0,
                    precision=1e-4,
                    merge_gap_days=0.75,
                )
                for hit in hits:
                    t_lon = _transit_lon(hit.jd)
                    yr, mo, dy, hr = swe.revjul(hit.jd)
                    results.append({
                        "jd": hit.jd,
                        "date": f"{yr}/{mo:02d}/{int(dy):02d}",
                        "transit_planet": t_name,
                        "natal_point": n_name,
                        "aspect": aspect_name,
                        "favorable": angle in (0, 60, 120),
                        "t_lon": t_lon,
                        "n_lon": n_lon,
                        "orb": round(abs(hit.value), 4),
                        "converged": hit.converged,
                    })

    # 去重（保留同組合最早事件）
    seen = set()
    unique = []
    for r in results:
        key = (r["transit_planet"], r["natal_point"], r["aspect"])
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return sorted(unique, key=lambda x: x["jd"])[:20]  # 最多20筆


def _generate_summary(
    total_score: int,
    jupiter_pos: Optional[PlanetPosition],
    saturn_pos: Optional[PlanetPosition],
    caibo_planets: list,
) -> tuple[str, str]:
    """
    根據財富能量指標生成財運摘要文字。
    Generate summary text based on wealth energy indicators.
    """
    jup_sign_zh = jupiter_pos.sign_chinese if jupiter_pos else "未知"
    jup_sign_en = jupiter_pos.sign_western if jupiter_pos else "Unknown"
    sat_sign_zh = saturn_pos.sign_chinese if saturn_pos else "未知"
    sat_sign_en = saturn_pos.sign_western if saturn_pos else "Unknown"
    jup_retro_zh = "（逆行）" if jupiter_pos and jupiter_pos.retrograde else ""
    jup_retro_en = " (Rx)" if jupiter_pos and jupiter_pos.retrograde else ""

    caibo_names_zh = "、".join(p.name for p in caibo_planets) if caibo_planets else "無主星居財帛宮"
    caibo_names_en = ", ".join(p.name for p in caibo_planets) if caibo_planets else "No planet in 2nd house"

    level_zh, level_en = classify_wealth_score(float(total_score))

    zh = (
        f"木星位於{jup_sign_zh}{jup_retro_zh}，土星位於{sat_sign_zh}。"
        f"財帛宮主星：{caibo_names_zh}。"
        f"整體財富能量評分 {total_score}，{level_zh}。"
    )
    en = (
        f"Jupiter in {jup_sign_en}{jup_retro_en}, Saturn in {sat_sign_en}. "
        f"2nd House planets: {caibo_names_en}. "
        f"Overall wealth score: {total_score} — {level_en}."
    )
    return zh, en


# ============================================================
# 渲染函數（Streamlit UI）
# ============================================================

def render_financial_tab(
    chart: ChartData,
    params: dict,
    input_tz: float = 8.0,
):
    """
    渲染「金融占星 / Financial Astrology」子分頁。
    Render the Financial Astrology subtab within the Seven Governors chart view.

    Parameters:
        chart: 出生盤資料
        params: _calc_params dict（含 year/month/day/hour/minute/timezone/latitude/longitude）
        input_tz: 輸入時區（用於「當下時刻」模式）
    """
    # ── 延遲匯入 plotly（避免啟動時不必要載入）──────────
    import plotly.graph_objects as go

    # ── 頂部說明文字 ─────────────────────────────────────
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, rgba(88,28,220,0.18), rgba(20,10,60,0.35));
            border: 1px solid rgba(180,140,255,0.3);
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 18px;
        ">
        <span style="font-size:1.15em;font-weight:700;color:#c8aaff;">
        💰 金融占星 / Financial Astrology
        </span><br/>
        <span style="color:#b0b8d8;font-size:0.92em;">
        結合七政四餘傳統財星理論與現代金融占星，從木土週期到個人財運時機，洞察市場脈動。<br/>
        Combining classical Seven Governors wealth theory with modern Financial Astrology — 
        from Jupiter-Saturn cycles to personal wealth timing insights.
        </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # ── 模式切換：出生盤 / 當下時刻 ─────────────────────
    _use_now = st.toggle(
        "🕐 使用當下時刻 / Use Current Time",
        value=False,
        key="fin_use_now_toggle",
        help="切換後將以當前時刻重新計算金融占星指標 / Switch to recalculate using the current moment",
    )

    if _use_now:
        utc_now = datetime.now(tz=tz_cls.utc)
        local_now = utc_now + timedelta(hours=input_tz)
        fin_params = {
            "year": local_now.year, "month": local_now.month, "day": local_now.day,
            "hour": local_now.hour, "minute": local_now.minute,
            "timezone": input_tz,
            "latitude": params.get("latitude", 22.3),
            "longitude": params.get("longitude", 114.2),
            "gender": params.get("gender", "male"),
        }
        st.caption(
            f"📅 當前時刻：{local_now.strftime('%Y-%m-%d %H:%M')} (UTC+{input_tz:g}) / "
            f"Current time: {local_now.strftime('%Y-%m-%d %H:%M')}"
        )
    else:
        fin_params = {
            "year": params.get("year", chart.year),
            "month": params.get("month", chart.month),
            "day": params.get("day", chart.day),
            "hour": params.get("hour", chart.hour),
            "minute": params.get("minute", chart.minute),
            "timezone": params.get("timezone", chart.timezone),
            "latitude": params.get("latitude", chart.latitude),
            "longitude": params.get("longitude", chart.longitude),
            "gender": params.get("gender", "male"),
        }

    # ── 計算金融占星資料 ─────────────────────────────────
    with st.spinner("🔮 計算金融占星指標… / Computing financial astrology indicators…"):
        try:
            fin = compute_financial_aspects(**fin_params)
        except Exception as e:
            st.error(f"計算錯誤 / Computation error: {e}")
            st.exception(e)
            return

    if fin.wealth_score_breakdown:
        b = fin.wealth_score_breakdown
        st.caption(
            f"分層評分：本質 {b.get('base_score', 0):+.2f} / "
            f"廟旺 {b.get('dignity_score', 0):+.2f} / "
            f"相位 {b.get('aspect_score', 0):+.2f} / "
            f"宮主 {b.get('house_lord_score', 0):+.2f}"
        )

    # ── 六個子分頁 ────────────────────────────────────────
    (
        _tab_overview,
        _tab_jup_sat,
        _tab_transits,
        _tab_history,
        _tab_outlook,
        _tab_macro,
        _tab_stock,
    ) = st.tabs([
        "🌟 財星總覽 / Overview",
        "♃♄ 木土週期 / Jupiter-Saturn Cycles",
        "🔄 財富過運 / Wealth Transits",
        "📜 歷史對照 / Historical Correlations",
        "🔭 金融展望 / Current Outlook",
        "🌍 宏觀股市 / Macro Market",
        "📈 股票靈運 / Stock Fortune",
    ])

    # ════════════════════════════════════════════════════
    # 分頁 1：財星總覽 / Overview
    # ════════════════════════════════════════════════════
    with _tab_overview:
        _render_overview(fin, go)

    # ════════════════════════════════════════════════════
    # 分頁 2：木星-土星週期 / Jupiter-Saturn Cycles
    # ════════════════════════════════════════════════════
    with _tab_jup_sat:
        _render_jupiter_saturn(fin, go)

    # ════════════════════════════════════════════════════
    # 分頁 3：關鍵財富過運 / Wealth Transits
    # ════════════════════════════════════════════════════
    with _tab_transits:
        _render_wealth_transits(fin, go)

    # ════════════════════════════════════════════════════
    # 分頁 4：歷史相關性 / Historical Correlations
    # ════════════════════════════════════════════════════
    with _tab_history:
        _render_historical_correlations(go, fin_params, input_tz)

    # ════════════════════════════════════════════════════
    # 分頁 5：當前金融展望 / Current Outlook
    # ════════════════════════════════════════════════════
    with _tab_outlook:
        _render_current_outlook(fin, chart)

    # ════════════════════════════════════════════════════
    # 分頁 6：宏觀股市 / Macro Market
    # ════════════════════════════════════════════════════
    with _tab_macro:
        _render_macro_market(input_tz=input_tz)

    # ════════════════════════════════════════════════════
    # 分頁 7：股票靈運占星儀 / Stock Fortune Astrologer
    # ════════════════════════════════════════════════════
    with _tab_stock:
        try:
            from .financial import render_stock_fortune_tab
            render_stock_fortune_tab(input_tz=input_tz)
        except ImportError as _ie:
            st.error(f"股票靈運模組載入失敗 / Stock fortune module failed to load: {_ie}")
        except Exception as _se:
            st.error(f"股票靈運錯誤 / Stock fortune error: {_se}")
            st.exception(_se)


# ────────────────────────────────────────────────────────────
# 子渲染函數
# ────────────────────────────────────────────────────────────

def _render_overview(fin: FinancialData, go):
    """財星總覽分頁 / Wealth overview panel"""
    st.subheader("🌟 財星總覽 / Wealth Planet Overview")

    # 財運摘要卡片
    score = fin.total_wealth_score
    if score >= 6:
        bar_color, level_icon = "#22c55e", "🟢"
    elif score >= 3:
        bar_color, level_icon = "#a3e635", "🟡"
    elif score >= 0:
        bar_color, level_icon = "#facc15", "🟡"
    else:
        bar_color, level_icon = "#ef4444", "🔴"

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg,rgba(30,20,80,0.6),rgba(60,30,120,0.4));
            border:1px solid rgba(180,140,255,0.3); border-radius:14px;
            padding:18px 22px; margin-bottom:16px;
        ">
        <div style="font-size:1.05em;color:#b0b8d8;margin-bottom:8px;">
        {level_icon} <strong style="color:#e0d0ff;">財富能量 / Wealth Energy</strong>
        &nbsp;|&nbsp; 評分 {score:+d} / Score {score:+d}
        </div>
        <div style="color:#d4c8ff;font-size:0.93em;margin-bottom:6px;">{fin.summary_zh}</div>
        <div style="color:#9090b8;font-size:0.85em;">{fin.summary_en}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 財星能量表
    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown("**財星位置與能量評分 / Wealth Planet Positions & Scores**")
        rows = []
        for entry in fin.wealth_planets:
            p = entry["planet"]
            retro_sym = " ℞" if p.retrograde else ""
            rows.append({
                "星曜 Planet": f"{p.name}{retro_sym}",
                "星座 Sign": f"{p.sign_chinese}",
                "度數 Deg": f"{p.longitude:.1f}°",
                "財星意義 Meaning": entry["zh"],
                "Meaning (EN)": entry["en"],
                "能量 Score": f"{entry['score']:+d}",
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch", hide_index=True)

    with col_r:
        # Gauge chart for wealth score
        _max = 10
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "財富能量 / Wealth Score", "font": {"color": "#c8aaff", "size": 13}},
            number={"font": {"color": "#e0d0ff", "size": 28}},
            gauge={
                "axis": {"range": [-_max, _max], "tickfont": {"color": "#9090b8"}},
                "bar": {"color": bar_color},
                "bgcolor": "rgba(30,20,80,0.4)",
                "bordercolor": "rgba(180,140,255,0.3)",
                "steps": [
                    {"range": [-_max, -3], "color": "rgba(239,68,68,0.15)"},
                    {"range": [-3, 3],    "color": "rgba(250,204,21,0.10)"},
                    {"range": [3, _max],  "color": "rgba(34,197,94,0.15)"},
                ],
                "threshold": {
                    "line": {"color": "#c8aaff", "width": 2},
                    "thickness": 0.75, "value": score,
                },
            },
        ))
        fig.update_layout(
            height=200, margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "#c8aaff"},
        )
        st.plotly_chart(fig, width="stretch")

    # 財帛宮行星
    if fin.caibo_planets:
        st.markdown("**🏦 財帛宮 (2nd House) 行星**")
        for p in fin.caibo_planets:
            e = _WEALTH_PLANET_ENERGY.get(p.name, {})
            retro = " ℞" if p.retrograde else ""
            st.markdown(
                f"""<div style="
                    background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.25);
                    border-radius:8px;padding:8px 12px;margin:4px 0;display:inline-block;
                ">
                ⭐ <strong style="color:#86efac;">{p.name}{retro}</strong>
                &nbsp;{p.sign_chinese}&nbsp;{p.longitude:.1f}°
                &nbsp;—&nbsp;<span style="color:#d4c8ff;">{e.get('zh','')}</span>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.info("財帛宮目前無主星 / No planet currently in the 2nd house")


def _render_jupiter_saturn(fin: FinancialData, go):
    """木星-土星週期分頁 / Jupiter-Saturn cycle panel"""
    st.subheader("♃♄ 木星-土星大合相週期 / Jupiter-Saturn Great Conjunction Cycles")
    great_conjunctions = _get_great_conjunctions()

    col_l, col_r = st.columns([1, 1])
    with col_l:
        # 當前木土位置
        jup = fin.jupiter_pos
        sat = fin.saturn_pos
        if jup and sat:
            angle = abs(_normalize_degree(jup.longitude - sat.longitude))
            if angle > 180:
                angle = 360 - angle
            st.markdown(
                f"""
                <div style="
                    background:rgba(30,20,80,0.55);border:1px solid rgba(180,140,255,0.3);
                    border-radius:12px;padding:14px 18px;
                ">
                <div style="color:#c8aaff;font-weight:700;font-size:1.05em;margin-bottom:8px;">
                ♃ 木星 Jupiter</div>
                <div style="color:#d4c8ff;">位置：{jup.sign_chinese} {jup.longitude:.2f}°
                {"（逆行 Rx）" if jup.retrograde else ""}</div>
                <div style="color:#9090b8;font-size:0.85em;">{jup.sign_western} {jup.sign_degree:.1f}°</div>
                <br/>
                <div style="color:#c8aaff;font-weight:700;font-size:1.05em;margin-bottom:8px;">
                ♄ 土星 Saturn</div>
                <div style="color:#d4c8ff;">位置：{sat.sign_chinese} {sat.longitude:.2f}°
                {"（逆行 Rx）" if sat.retrograde else ""}</div>
                <div style="color:#9090b8;font-size:0.85em;">{sat.sign_western} {sat.sign_degree:.1f}°</div>
                <br/>
                <div style="color:#facc15;font-weight:600;">
                🔭 木土夾角：{angle:.1f}° / Jupiter-Saturn angle: {angle:.1f}°
                </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_r:
        # 下一次合相
        nc = fin.next_conjunction
        if nc:
            st.markdown(
                f"""
                <div style="
                    background:linear-gradient(135deg,rgba(34,197,94,0.12),rgba(30,80,30,0.2));
                    border:1px solid rgba(34,197,94,0.3);border-radius:12px;padding:14px 18px;
                ">
                <div style="color:#86efac;font-weight:700;font-size:1.05em;margin-bottom:8px;">
                🌟 下一次大合相 / Next Great Conjunction</div>
                <div style="color:#d4c8ff;">
                📅 預計：{nc['year']}/{nc['month']:02d}/{nc['day']:02d}</div>
                <div style="color:#d4c8ff;">
                📍 度數：{nc['sign']} {nc.get('sign_degree', 0):.1f}°
                ({nc.get('longitude', 0):.2f}° 黃經)</div>
                <div style="color:#9090b8;font-size:0.85em;margin-top:6px;">
                木土合相標誌新的 20 年財經週期開啟。<br/>
                Great Conjunctions mark new 20-year socio-economic cycles.
                </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown("**📊 重大木土合相歷史列表 / Historical Great Conjunctions**")

    # 時間軸圖
    labels, x_vals, colors, hover_texts = [], [], [], []
    for gc in great_conjunctions:
        dt_str = f"{gc['year']}-{gc['month']:02d}-{gc['day']:02d}"
        labels.append(f"{gc['year']} {gc['sign']}")
        x_vals.append(gc["year"] + gc["month"] / 12.0)
        colors.append("#86efac" if "牛市" in gc["note_zh"] or "擴張" in gc["note_zh"] or "新週期" in gc["note_zh"] else "#f87171")
        hover_texts.append(
            f"<b>{gc['year']}/{gc['month']:02d}/{gc['day']:02d}</b><br>"
            f"星座: {gc['sign']}<br>"
            f"黃經: {gc['lon']:.1f}°<br>"
            f"{gc['note_zh']}<br>{gc['note_en']}"
        )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals, y=[1] * len(x_vals),
        mode="markers+text",
        marker=dict(size=18, color=colors, symbol="star",
                    line=dict(width=1.5, color="#c8aaff")),
        text=labels, textposition="top center",
        hovertext=hover_texts, hoverinfo="text",
        textfont=dict(color="#e0d0ff", size=10),
    ))
    fig.update_layout(
        height=200, margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,10,60,0.4)",
        xaxis=dict(title="Year", color="#9090b8", gridcolor="rgba(180,140,255,0.1)"),
        yaxis=dict(showticklabels=False, range=[0.5, 1.8]),
        title=dict(text="木土大合相時間軸 / Great Conjunction Timeline", font=dict(color="#c8aaff", size=13)),
        font=dict(color="#c8aaff"),
    )
    st.plotly_chart(fig, width="stretch")

    # 擴張/收縮週期示意圖
    _render_expansion_contraction_chart(go, great_conjunctions)

    # 表格
    import pandas as pd
    gc_rows = []
    for gc in great_conjunctions:
        gc_rows.append({
            "年份 Year": gc["year"],
            "日期 Date": f"{gc['year']}/{gc['month']:02d}/{gc['day']:02d}",
            "星座 Sign": gc["sign"],
            "黃經 Lon": f"{gc['lon']:.1f}°",
            "歷史背景 (中)": gc["note_zh"],
            "Historical Note (EN)": gc["note_en"],
        })
    df_gc = pd.DataFrame(gc_rows)
    st.dataframe(df_gc, width="stretch", hide_index=True)


def _render_expansion_contraction_chart(go, great_conjunctions: list[dict]):
    """渲染市場擴張/收縮週期圖 / Market expansion/contraction cycle chart"""
    # 簡化版：以木土合相為分界，每合相後 ~10年擴張，~10年收縮
    periods = []
    conj_years = [gc["year"] for gc in great_conjunctions]
    for i, yr in enumerate(conj_years):
        end_yr = conj_years[i + 1] if i + 1 < len(conj_years) else yr + 20
        mid = (yr + end_yr) / 2
        periods.append({
            "start": yr, "end": mid,
            "phase_zh": "擴張 Expansion", "color": "rgba(34,197,94,0.25)",
        })
        periods.append({
            "start": mid, "end": end_yr,
            "phase_zh": "收縮 Contraction", "color": "rgba(239,68,68,0.20)",
        })

    fig = go.Figure()
    for p in periods:
        fig.add_vrect(
            x0=p["start"], x1=p["end"],
            fillcolor=p["color"],
            layer="below", line_width=0,
            annotation_text=p["phase_zh"],
            annotation_font_color="#a0a0c0",
            annotation_font_size=9,
        )
    # 合相垂直線
    for yr in conj_years:
        fig.add_vline(x=yr, line_dash="dot", line_color="rgba(200,170,255,0.5)", line_width=1.2)

    fig.add_trace(go.Scatter(
        x=conj_years, y=[0.5] * len(conj_years),
        mode="markers",
        marker=dict(size=12, color="#c8aaff", symbol="diamond"),
        name="合相 Conjunction",
        hovertext=[f"{gc['year']}: {gc['sign']}" for gc in great_conjunctions],
        hoverinfo="text",
    ))
    fig.update_layout(
        height=150, margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,10,60,0.4)",
        xaxis=dict(color="#9090b8", gridcolor="rgba(180,140,255,0.1)"),
        yaxis=dict(showticklabels=False, range=[0, 1]),
        title=dict(text="市場週期示意 / Market Cycle Illustration", font=dict(color="#c8aaff", size=12)),
        showlegend=False,
        font=dict(color="#c8aaff"),
    )
    st.plotly_chart(fig, width="stretch")


def _render_wealth_transits(fin: FinancialData, go):
    """財富過運分頁 / Wealth transit panel"""
    st.subheader("🔄 關鍵財富行星過運 / Key Wealth Planet Transits")
    st.caption(
        "顯示未來 12 個月木星、土星、天王星對本命盤關鍵點的主要相位。"
        " / Shows major aspects of Jupiter, Saturn, Uranus to natal chart key points in the next 12 months."
    )

    transits = fin.upcoming_transits
    if not transits:
        st.info("未來 12 個月內未偵測到顯著財富過運。/ No significant wealth transits found in the next 12 months.")
        return

    import pandas as pd
    rows = []
    for tr in transits:
        fav = tr["favorable"]
        tag_zh = "✅ 有利擴張" if fav else "⚠️ 謹慎重組"
        tag_en = "✅ Favorable" if fav else "⚠️ Caution"
        rows.append({
            "日期 Date": tr["date"],
            "過運星 Transit": tr["transit_planet"],
            "相位 Aspect": tr["aspect"],
            "本命點 Natal Point": tr["natal_point"],
            "趨勢 Trend": f"{tag_zh} / {tag_en}",
        })
    df_t = pd.DataFrame(rows)

    # 顏色標示：用 plotly 表格
    fill_colors = []
    for tr in transits:
        fill_colors.append("rgba(34,197,94,0.15)" if tr["favorable"] else "rgba(239,68,68,0.15)")

    # 第一欄用財星顏色標示，其餘欄用統一深色背景
    _neutral_col = ["rgba(20,10,60,0.3)"] * len(transits)
    cell_colors = [fill_colors] + [_neutral_col] * (len(df_t.columns) - 1)

    fig = go.Figure(go.Table(
        header=dict(
            values=list(df_t.columns),
            fill_color="rgba(88,28,220,0.4)",
            font=dict(color="#e0d0ff", size=12),
            align="left",
            line_color="rgba(180,140,255,0.3)",
        ),
        cells=dict(
            values=[df_t[c].tolist() for c in df_t.columns],
            fill_color=cell_colors,
            font=dict(color="#d4c8ff", size=11),
            align="left",
            line_color="rgba(180,140,255,0.15)",
        ),
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        height=min(60 + len(transits) * 28, 600),
    )
    st.plotly_chart(fig, width="stretch")

    # 時間軸圖：有利 vs 謹慎
    dates_fav = [tr["date"] for tr in transits if tr["favorable"]]
    dates_cau = [tr["date"] for tr in transits if not tr["favorable"]]
    labels_fav = [f"{tr['transit_planet']} {tr['aspect']} {tr['natal_point']}" for tr in transits if tr["favorable"]]
    labels_cau = [f"{tr['transit_planet']} {tr['aspect']} {tr['natal_point']}" for tr in transits if not tr["favorable"]]

    fig2 = go.Figure()
    if dates_fav:
        fig2.add_trace(go.Scatter(
            x=dates_fav, y=[1] * len(dates_fav),
            mode="markers+text", text=labels_fav,
            textposition="top center",
            marker=dict(size=14, color="#22c55e", symbol="circle"),
            name="有利 Favorable",
            textfont=dict(size=9, color="#86efac"),
        ))
    if dates_cau:
        fig2.add_trace(go.Scatter(
            x=dates_cau, y=[0.5] * len(dates_cau),
            mode="markers+text", text=labels_cau,
            textposition="top center",
            marker=dict(size=14, color="#ef4444", symbol="x"),
            name="謹慎 Caution",
            textfont=dict(size=9, color="#fca5a5"),
        ))
    fig2.update_layout(
        height=250, margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,10,60,0.4)",
        xaxis=dict(title="Date", color="#9090b8", gridcolor="rgba(180,140,255,0.1)"),
        yaxis=dict(showticklabels=False, range=[0, 1.8]),
        title=dict(text="財富過運時機 / Wealth Transit Timing", font=dict(color="#c8aaff", size=13)),
        legend=dict(font=dict(color="#c8aaff"), bgcolor="rgba(0,0,0,0)"),
        font=dict(color="#c8aaff"),
    )
    st.plotly_chart(fig2, width="stretch")


def _render_historical_correlations(go, fin_params: dict, input_tz: float):
    """歷史相關性分頁 / Historical correlations panel"""
    st.subheader("📜 歷史金融事件相關性 / Historical Financial Event Correlations")
    historical_events = _get_historical_events()

    # 歷史事件卡片
    col1, col2 = st.columns(2)
    for i, evt in enumerate(historical_events):
        target_col = col1 if i % 2 == 0 else col2
        border_color = "#f87171" if evt["market_impact"] == "crash" else "#86efac"
        bg_color = "rgba(239,68,68,0.1)" if evt["market_impact"] == "crash" else "rgba(34,197,94,0.1)"
        icon = "📉" if evt["market_impact"] == "crash" else "📈"
        with target_col:
            st.markdown(
                f"""<div style="
                    background:{bg_color};border:1px solid {border_color}40;
                    border-radius:10px;padding:12px 16px;margin-bottom:10px;
                ">
                <strong style="color:{border_color};">{icon} {evt['label_zh']}</strong><br/>
                <span style="color:#9090b8;font-size:0.82em;">{evt['label_en']}</span><br/>
                <span style="color:#b0b8d8;font-size:0.88em;">
                    木星 {evt['jup_lon_approx']}° / 土星 {evt['sat_lon_approx']}°
                </span><br/>
                <span style="color:#d4c8ff;font-size:0.88em;">{evt['note_zh']}</span><br/>
                <span style="color:#8090a8;font-size:0.80em;">{evt['note_en']}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    st.divider()

    # 自訂日期查詢
    st.markdown("**🔍 自訂日期金融解讀 / Custom Date Financial Reading**")
    col_d, col_t, col_tz = st.columns(3)
    with col_d:
        custom_date = st.date_input(
            "查詢日期 / Query date",
            value=datetime.now().date(),
            key="fin_custom_date",
        )
    with col_t:
        custom_time = st.time_input(
            "查詢時間 / Query time",
            value=datetime.now().time().replace(second=0, microsecond=0),
            key="fin_custom_time",
        )
    with col_tz:
        custom_tz = st.number_input(
            "時區 / Timezone",
            value=input_tz, format="%.1f",
            min_value=-12.0, max_value=14.0, step=0.5,
            key="fin_custom_tz",
        )

    if st.button("🔮 計算該日期金融指標 / Compute Financial Indicators", key="fin_compute_custom"):
        with st.spinner("計算中… / Computing…"):
            try:
                custom_fin = compute_financial_aspects(
                    year=custom_date.year, month=custom_date.month, day=custom_date.day,
                    hour=custom_time.hour, minute=custom_time.minute,
                    timezone=custom_tz,
                    latitude=fin_params.get("latitude", 22.3),
                    longitude=fin_params.get("longitude", 114.2),
                    gender=fin_params.get("gender", "male"),
                )
                st.success("計算完成 / Computation complete")
                st.markdown(f"**財富能量評分：{custom_fin.total_wealth_score:+d}**")
                st.info(custom_fin.summary_zh)
                st.caption(custom_fin.summary_en)

                # 行星位置快照
                import pandas as pd
                snap_rows = []
                for entry in custom_fin.wealth_planets:
                    p = entry["planet"]
                    snap_rows.append({
                        "星曜": f"{p.name}{' ℞' if p.retrograde else ''}",
                        "黃經": f"{p.longitude:.2f}°",
                        "星次": p.sign_chinese,
                        "財星意義": entry["zh"],
                    })
                st.dataframe(pd.DataFrame(snap_rows), width="stretch", hide_index=True)
            except Exception as e:
                st.error(f"錯誤 / Error: {e}")

    # 回測視覺化（簡易：顯示歷史事件的木土角度）
    st.divider()
    st.markdown("**📊 歷史事件木土夾角圖 / Jupiter-Saturn Angle at Historical Events**")

    evt_labels = [f"{e['year']}\n{e['label_zh'].split('（')[0]}" for e in historical_events]
    jup_sat_angles = []
    for e in historical_events:
        diff = abs(e["jup_lon_approx"] - e["sat_lon_approx"])
        if diff > 180:
            diff = 360 - diff
        jup_sat_angles.append(diff)
    bar_colors = [
        "#f87171" if e["market_impact"] == "crash" else "#86efac"
        for e in historical_events
    ]

    fig = go.Figure(go.Bar(
        x=evt_labels,
        y=jup_sat_angles,
        marker_color=bar_colors,
        marker_line_color="rgba(200,170,255,0.4)",
        marker_line_width=1,
        hovertemplate="%{x}<br>木土夾角: %{y:.1f}°<extra></extra>",
    ))
    fig.update_layout(
        height=260, margin=dict(l=20, r=20, t=40, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,10,60,0.4)",
        xaxis=dict(color="#9090b8", gridcolor="rgba(180,140,255,0.1)", tickfont=dict(size=9)),
        yaxis=dict(title="夾角 (°)", color="#9090b8", gridcolor="rgba(180,140,255,0.1)"),
        title=dict(text="歷史金融事件時的木土夾角 / Jupiter-Saturn Angle at Market Events",
                   font=dict(color="#c8aaff", size=12)),
        font=dict(color="#c8aaff"),
    )
    # 加入說明線
    for ref_angle, label in [(0, "合相 Conj"), (90, "刑 Square"), (120, "三合 Trine"), (180, "對沖 Opp")]:
        fig.add_hline(y=ref_angle, line_dash="dot",
                      line_color="rgba(200,170,255,0.3)",
                      annotation_text=label,
                      annotation_font_color="#8090b0",
                      annotation_font_size=9)
    st.plotly_chart(fig, width="stretch")


def _render_current_outlook(fin: FinancialData, chart: ChartData):
    """當前金融展望分頁 / Current financial outlook panel"""
    st.subheader("🔭 當前金融展望 / Current Financial Outlook")

    # 財富訊號清單
    st.markdown("**📡 財富訊號 / Wealth Signals**")
    signals = _build_wealth_signals(fin)
    for sig in signals:
        icon = "🟢" if sig["positive"] else "🔴"
        st.markdown(
            f"""<div style="
                background:{'rgba(34,197,94,0.10)' if sig['positive'] else 'rgba(239,68,68,0.10)'};
                border-left: 3px solid {'#22c55e' if sig['positive'] else '#ef4444'};
                border-radius:0 8px 8px 0;padding:8px 14px;margin:5px 0;
            ">
            {icon} <strong style="color:{'#86efac' if sig['positive'] else '#fca5a5'};">
            {sig['title_zh']}</strong> / <em style="color:#9090b8;">{sig['title_en']}</em><br/>
            <span style="color:#b0b8d8;font-size:0.88em;">{sig['desc_zh']}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()

    # 傳統文化解讀
    st.markdown("**📖 傳統財星解讀 / Classical Wealth Star Interpretation**")
    jup = fin.jupiter_pos
    sat = fin.saturn_pos
    ziqi = next((e["planet"] for e in fin.wealth_planets if e["planet"].name == "紫氣"), None)

    interp_lines = []
    if jup:
        if jup.retrograde:
            interp_lines.append(("⚠️", "木星逆行 Jupiter Rx",
                                  "擴張能量內斂，宜回顧投資組合而非新開發",
                                  "Expansion energy turns inward — review portfolios rather than new ventures"))
        else:
            interp_lines.append(("✅", "木星順行 Jupiter Direct",
                                  "傳統財星得力，擴張機遇活躍",
                                  "Classical wealth star empowered — expansion opportunities active"))
    if sat:
        if sat.retrograde:
            interp_lines.append(("⚠️", "土星逆行 Saturn Rx",
                                  "收縮壓力暫緩，可逐步布局",
                                  "Contraction pressure eases temporarily — gradual positioning possible"))
        else:
            interp_lines.append(("🔔", "土星順行 Saturn Direct",
                                  "市場紀律收緊，謹慎管理風險",
                                  "Market discipline tightens — manage risk carefully"))
    if ziqi:
        interp_lines.append(("🌟", "紫氣 Purple Star",
                              f"紫氣位於{ziqi.sign_chinese}，貴人扶助財源，{ziqi.sign_western}宮位帶來貴氣財運",
                              f"Purple Star in {ziqi.sign_western} — noble patron wealth and auspicious connections"))

    for icon_txt, title, zh, en in interp_lines:
        st.markdown(
            f"""<div style="
                background:rgba(88,28,220,0.12);border:1px solid rgba(180,140,255,0.25);
                border-radius:10px;padding:10px 16px;margin:6px 0;
            ">
            {icon_txt} <strong style="color:#c8aaff;">{title}</strong><br/>
            <span style="color:#d4c8ff;font-size:0.9em;">{zh}</span><br/>
            <span style="color:#8090a8;font-size:0.82em;">{en}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()

    # AI 一鍵解讀
    st.markdown("**🤖 AI 金融占星解讀 / AI Financial Astrology Reading**")
    _render_financial_ai_button(fin, chart)


def _render_macro_market(input_tz: float = 8.0):
    """宏觀股市分頁：地區板塊看多看空與股票靈運。"""
    from .stock_lingyun import REGION_PRESETS

    st.subheader("🌍 宏觀股市 / Macro Market")
    st.caption("依吳師青《天運占星學》：以太陽季節圖、關鍵宮位、天運統運與月相判斷板塊多空。")

    utc_now = datetime.now(tz=tz_cls.utc)
    local_now = utc_now + timedelta(hours=input_tz)

    region = st.selectbox(
        "分析地區 / Region",
        options=list(REGION_PRESETS.keys()),
        index=0,
        key="macro_market_region",
    )
    col_y, col_m = st.columns(2)
    with col_y:
        year = st.number_input(
            "年份 / Year",
            min_value=1900,
            max_value=2300,
            value=int(local_now.year),
            step=1,
            key="macro_market_year",
        )
    with col_m:
        month = st.number_input(
            "月份 / Month",
            min_value=1,
            max_value=12,
            value=int(local_now.month),
            step=1,
            key="macro_market_month",
        )

    lat = REGION_PRESETS[region]["lat"]
    lon = REGION_PRESETS[region]["lon"]
    with st.spinner("🔮 計算宏觀股市靈運… / Computing macro market spirit…"):
        data = get_stock_lingyun_chart(year=int(year), month=int(month), lat=float(lat), lon=float(lon))

    score = data.get("stock_score", {})
    st.markdown(
        f"""
        <div style="background:rgba(20,40,70,0.35);border:1px solid rgba(120,180,255,0.25);
        border-radius:12px;padding:14px 16px;margin:8px 0 14px 0;">
        <strong style="color:#93c5fd;">關鍵宮位總分 / Total Score：</strong>
        <span style="color:#e2e8f0;">{score.get('total_score', 0):+d}</span>
        &nbsp;|&nbsp;
        <strong style="color:#93c5fd;">宏觀判斷 / View：</strong>
        <span style="color:#fde68a;">{score.get('market_view', '中性')}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected = data.get("selected_chart", {})
    st.caption(
        f"當月主盤 / Active seasonal chart: {selected.get('ingress_name', '—')} "
        f"({selected.get('datetime_utc', '—')})"
    )

    import pandas as pd
    sectors_df = pd.DataFrame(score.get("sector_scores", []))
    if not sectors_df.empty:
        sectors_df["sectors"] = sectors_df["sectors"].apply(lambda x: "、".join(x))
        st.markdown("**📊 關鍵宮位板塊看多看空 / Key-House Sector Bull-Bear Map**")
        st.dataframe(sectors_df, width="stretch", hide_index=True)

    # 完整十二宮（吳師青天運占星學）
    twelve = score.get("twelve_houses", [])
    if twelve:
        st.markdown("**🏛️ 完整十二宮概覽（吳師青《天運占星學》）/ All Twelve Houses**")
        for row in twelve:
            h = row["house"]
            wu_name = row["wu_name"]
            summary = row["summary"]
            verb = row["verb"]
            keywords_str = "、".join(row["keywords"])
            planets_str = "、".join(row["planets"]) if row["planets"] else "（空宮）"
            is_key = row["is_key_house"]
            score_val = row["score"]
            view_val = row["view"]

            # 評分顏色
            if score_val is not None and score_val >= 1:
                score_color = "#4ade80"
            elif score_val is not None and score_val <= -1:
                score_color = "#f87171"
            else:
                score_color = "#94a3b8"

            key_badge = (
                '<span style="background:#1e3a5f;color:#93c5fd;font-size:0.7em;'
                'padding:1px 6px;border-radius:4px;margin-left:6px;">關鍵宮</span>'
                if is_key else ""
            )
            score_display = (
                f'&nbsp;|&nbsp;<span style="color:{score_color};">評分 {int(score_val):+d}／{view_val}</span>'
                if score_val is not None
                else ""
            )

            st.markdown(
                f"""<div style="background:rgba(20,35,60,0.30);border:1px solid rgba(100,150,220,0.20);
                border-radius:10px;padding:10px 14px;margin:5px 0;">
                <strong style="color:#c7d2fe;">第{h}宮（{wu_name}）{key_badge}</strong>
                {score_display}<br>
                <span style="color:#e2e8f0;">{summary}。</span>
                <span style="color:#94a3b8;font-size:0.9em;">關鍵詞：{keywords_str}等，{verb}。</span><br>
                <span style="color:#fde68a;font-size:0.9em;">⭐ 當前入宮星曜：{planets_str}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("**🪐 四大天運統運 / Four Great Transits**")
    st.code(data.get("four_great_transits", "—"), language="text")

    lunation = data.get("lunation", {})
    st.markdown("**🌑🌕 新月滿月月勢 / Lunation Trend**")
    st.write(
        f"本月趨勢評分：{lunation.get('monthly_trend_score', 0):+d}，"
        f"判斷：{lunation.get('monthly_trend_view', '中性')}"
    )
    nm = lunation.get("new_moon")
    if nm:
        st.write(f"新月：{nm.get('datetime_utc', '—')}（相位差 {nm.get('aspect_to_spring_sun', 0)}°）")
    fm = lunation.get("full_moon")
    if fm:
        st.write(f"滿月：{fm.get('datetime_utc', '—')}（相位差 {fm.get('aspect_to_spring_sun', 0)}°）")

    conjs = data.get("major_conjunctions", [])
    st.markdown("**☌ 主要會合 / Major Conjunctions**")
    if conjs:
        st.dataframe(pd.DataFrame(conjs), width="stretch", hide_index=True)
    else:
        st.info("本季節圖未偵測到主要會合。")

    st.divider()
    st.markdown("## 🌀 江恩占星（Gann Astrology）x 七政四餘")
    st.caption("時間優先 + 周期縮放 + 星曜守照共振，用於宏觀指數時窗判讀。")

    preset_names = list(GANN_NATAL_PRESETS.keys())
    default_idx = preset_names.index(GANN_NATAL_DEFAULT) if GANN_NATAL_DEFAULT in preset_names else 0
    selected_preset = st.selectbox(
        "指數出生圖建議 / Market Natal Preset",
        options=preset_names,
        index=default_idx,
        key="gann_macro_natal_preset",
    )
    natal_date = GANN_NATAL_PRESETS[selected_preset]

    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        gann_scale = st.slider(
            "周期縮放倍率 / Cycle Scale",
            min_value=0.01,
            max_value=1.0,
            value=0.1,
            step=0.01,
            key="gann_macro_scale",
        )
    with col_g2:
        cycle_orb_days = st.slider(
            "周期容差（日） / Cycle Orb",
            min_value=3,
            max_value=45,
            value=12,
            step=1,
            key="gann_macro_orb_days",
        )
    with col_g3:
        use_trading_days = st.checkbox(
            "以交易日縮放 / Trading-day scale",
            value=False,
            key="gann_macro_trading_days",
        )

    with st.spinner("🧭 計算江恩周期共振… / Computing Gann timing resonance…"):
        gann = build_gann_macro_timing(
            market_natal_date=natal_date,
            as_of_datetime=local_now,
            timezone=input_tz,
            cycle_scale=float(gann_scale),
            use_trading_days=bool(use_trading_days),
            cycle_orb_days=int(cycle_orb_days),
        )

    s = gann.get("scores", {})
    st.markdown(
        f"""
        <div style="background:rgba(51,65,85,0.35);border:1px solid rgba(148,163,184,0.35);
        border-radius:12px;padding:14px 16px;margin:8px 0 12px 0;">
        <strong style="color:#c4b5fd;">共振總分 / Resonance Score：</strong>
        <span style="color:#e2e8f0;">{s.get('total_score', 0):+d}</span>
        &nbsp;|&nbsp;
        <strong style="color:#c4b5fd;">分級 / Class：</strong>
        <span style="color:#fde68a;">{s.get('classification', '—')}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    near_hits = gann.get("near_cycle_hits", [])
    st.markdown("**⏳ 周期到期窗 / Active Biblical Timing Windows**")
    if near_hits:
        st.dataframe(pd.DataFrame(near_hits), width="stretch", hide_index=True)
    else:
        st.info("目前容差窗內無主要週期到期點。")

    near_ann = gann.get("near_anniversaries", [])
    st.markdown("**🗓️ Anniversary Dates 週年窗**")
    if near_ann:
        st.dataframe(pd.DataFrame(near_ann), width="stretch", hide_index=True)
    else:
        st.info("目前容差窗內無明顯週年日期共振。")

    hits = gann.get("qizheng_resonance_hits", [])
    st.markdown("**🪐 七政四餘守照共振 / Qizheng Resonance**")
    if hits:
        st.dataframe(pd.DataFrame(hits), width="stretch", hide_index=True)
    else:
        st.info("目前未偵測到明顯守照共振。")

    st.markdown("**✅ 建議進場條件 / Suggested Entry Conditions**")
    for cond in gann.get("entry_conditions", []):
        st.write(f"- {cond}")
    st.markdown("**🛑 建議出場條件 / Suggested Exit Conditions**")
    for cond in gann.get("exit_conditions", []):
        st.write(f"- {cond}")

    st.markdown("**🔢 Gann Square of 9（輪中輪）參考價位**")
    default_price = GANN_NATAL_REFERENCE_PRICES.get(selected_preset, 5000.0)
    sq_col1, sq_col2, sq_col3 = st.columns(3)
    with sq_col1:
        ref_price = st.number_input(
            "參考價格 / Reference Price",
            min_value=0.01,
            value=float(default_price),
            step=10.0,
            key="gann_square_reference_price",
        )
    with sq_col2:
        sq_ring = st.slider("Ring", min_value=1, max_value=4, value=2, step=1, key="gann_square_ring")
    with sq_col3:
        sq_desc = st.checkbox("含下行價位 / Include descending", value=False, key="gann_square_desc")
    sq9 = compute_square_of_nine_levels(
        float(ref_price),
        max_ring=int(sq_ring),
        angle_step=45,
        include_descending=bool(sq_desc),
    )
    st.dataframe(pd.DataFrame(sq9), width="stretch", hide_index=True)

    st.markdown("**🧪 Astro Backtesting（MVP）**")
    bt_col1, bt_col2 = st.columns(2)
    with bt_col1:
        bt_ticker = st.text_input("回測標的 / Ticker", value="^HSI", key="gann_bt_ticker")
    with bt_col2:
        bt_years = st.slider("回測年數 / Years", min_value=1, max_value=12, value=5, step=1, key="gann_bt_years")
    if st.button("執行回測 / Run Backtest", key="gann_run_backtest"):
        try:
            import yfinance as yf
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=365 * int(bt_years))
            px = yf.download(bt_ticker.strip(), start=start_dt.date(), end=end_dt.date(), progress=False, auto_adjust=False)
            if px is None or px.empty:
                st.warning("無法取得歷史價格資料。")
            else:
                if isinstance(px.columns, pd.MultiIndex):
                    px.columns = [c[0] for c in px.columns]
                px = px.rename(columns=str)

                def _feature_fn(ts: datetime) -> dict:
                    payload = build_gann_macro_timing(
                        market_natal_date=natal_date,
                        as_of_datetime=ts,
                        timezone=input_tz,
                        cycle_scale=float(gann_scale),
                        use_trading_days=bool(use_trading_days),
                        cycle_orb_days=int(cycle_orb_days),
                    )
                    s = payload.get("scores", {})
                    return {
                        "astro_score": float(s.get("total_score", 0)),
                        "cycle_score": float(s.get("cycle_score", 0)),
                        "astro_only_score": float(s.get("astro_score", 0)),
                    }

                bt = run_backtest_mvp(px, _feature_fn, horizons=(5, 10, 20), feature_col="astro_score")
                metrics = bt.get("metrics", [])
                if metrics:
                    st.dataframe(pd.DataFrame(metrics), width="stretch", hide_index=True)
                else:
                    st.info("樣本不足，未產生有效統計。")
        except Exception as e:
            st.error(f"Backtest error: {e}")


def _build_wealth_signals(fin: FinancialData) -> list:
    """
    建立財富訊號清單（根據行星位置）。
    Build wealth signal list from planetary positions.
    """
    signals = []
    jup = fin.jupiter_pos
    sat = fin.saturn_pos

    if jup:
        if not jup.retrograde:
            signals.append({
                "positive": True,
                "title_zh": "木星順行擴張",
                "title_en": "Jupiter Direct — Expansion",
                "desc_zh": f"木星於{jup.sign_chinese}順行，財富擴張訊號強。",
            })
        else:
            signals.append({
                "positive": False,
                "title_zh": "木星逆行收斂",
                "title_en": "Jupiter Retrograde — Introspection",
                "desc_zh": f"木星於{jup.sign_chinese}逆行，宜內省，避免過度擴張投資。",
            })

    if sat:
        if sat.retrograde:
            signals.append({
                "positive": True,
                "title_zh": "土星逆行緩壓",
                "title_en": "Saturn Rx — Pressure Eases",
                "desc_zh": f"土星於{sat.sign_chinese}逆行，市場收縮壓力暫時減緩。",
            })
        else:
            signals.append({
                "positive": False,
                "title_zh": "土星順行收緊",
                "title_en": "Saturn Direct — Tightening",
                "desc_zh": f"土星於{sat.sign_chinese}順行，市場趨向保守，宜控制槓桿。",
            })

    # 財帛宮訊號
    if fin.caibo_planets:
        for p in fin.caibo_planets:
            score = _WEALTH_PLANET_ENERGY.get(p.name, {}).get("score", 0)
            signals.append({
                "positive": score >= 1,
                "title_zh": f"財帛宮有{p.name}",
                "title_en": f"{p.name} in 2nd House",
                "desc_zh": f"{p.name}居財帛宮，{'直接強化財運' if score > 0 else '需注意財務風險'}。",
            })

    # 木土夾角訊號
    if jup and sat:
        angle = abs(_normalize_degree(jup.longitude - sat.longitude))
        if angle > 180:
            angle = 360 - angle
        if abs(angle - 120) < 10 or abs(angle - 60) < 8:
            signals.append({
                "positive": True,
                "title_zh": f"木土呈吉相位 {angle:.0f}°",
                "title_en": f"Jupiter-Saturn Harmonious Aspect {angle:.0f}°",
                "desc_zh": "木土三合/六合，市場擴張與穩健兼備，長線投資好時機。",
            })
        elif abs(angle - 90) < 8 or abs(angle - 180) < 8:
            signals.append({
                "positive": False,
                "title_zh": f"木土呈挑戰相位 {angle:.0f}°",
                "title_en": f"Jupiter-Saturn Challenging Aspect {angle:.0f}°",
                "desc_zh": "木土刑/對沖，市場波動加大，宜分散風險。",
            })

    return signals


def _render_financial_ai_button(fin: FinancialData, chart: ChartData):
    """
    渲染金融占星 AI 解讀按鈕。
    Registers financial astrology context for the global AI chat panel.
    """
    # 建立 AI prompt context
    ai_context = {
        "module": "financial_astrology",
        "wealth_score": fin.total_wealth_score,
        "summary_zh": fin.summary_zh,
        "summary_en": fin.summary_en,
        "jupiter": {
            "sign": fin.jupiter_pos.sign_chinese if fin.jupiter_pos else "",
            "lon": fin.jupiter_pos.longitude if fin.jupiter_pos else 0,
            "retrograde": fin.jupiter_pos.retrograde if fin.jupiter_pos else False,
        } if fin.jupiter_pos else {},
        "saturn": {
            "sign": fin.saturn_pos.sign_chinese if fin.saturn_pos else "",
            "lon": fin.saturn_pos.longitude if fin.saturn_pos else 0,
            "retrograde": fin.saturn_pos.retrograde if fin.saturn_pos else False,
        } if fin.saturn_pos else {},
        "caibo_planets": [p.name for p in fin.caibo_planets],
        "upcoming_transits": [
            {
                "date": t["date"],
                "transit": t["transit_planet"],
                "aspect": t["aspect"],
                "natal": t["natal_point"],
                "favorable": t["favorable"],
            }
            for t in fin.upcoming_transits[:10]
        ],
        "birth_chart": {
            "year": chart.year, "month": chart.month, "day": chart.day,
            "location": chart.location_name,
        },
        "ai_role_zh": "你是精通七政四餘與金融占星的明清財經國師，結合傳統財星與現代市場週期給出務實建議",
        "ai_role_en": "You are a master of Seven Governors and Financial Astrology — combining traditional wealth stars with modern market cycles to give practical financial insights",
    }

    st.info(
        "💡 點擊頁面底部 **AI 助理** 按鈕，取得金融占星個人化解讀。"
        " / Click the **AI Assistant** button at the bottom of the page for personalised financial astrology insights.",
        icon="🤖",
    )

    # 將 context 推送給全域 AI chat（複用現有機制）
    try:
        st.session_state["_global_chat_system"] = "tab_chinese_financial"
        st.session_state["_global_chat_chart"] = ai_context
        _transit_summary = ", ".join(
            f"{t['date']} {t['transit_planet']} {t['aspect']} {t['natal_point']}"
            for t in fin.upcoming_transits[:5]
        )
        st.session_state["_global_chat_page_content"] = (
            f"金融占星分析 / Financial Astrology Analysis:\n"
            f"財富評分: {fin.total_wealth_score}\n"
            f"{fin.summary_zh}\n{fin.summary_en}\n"
            f"未來過運: {_transit_summary}"
        )
    except Exception:
        pass
