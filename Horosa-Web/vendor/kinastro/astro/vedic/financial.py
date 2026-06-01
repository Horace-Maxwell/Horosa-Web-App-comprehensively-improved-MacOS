"""
印度占星股票金融子模組 (Vedic Stock Financial Astrology)

功能：
- 搜尋股票代碼並讀取行情資料
- 以上市日期作為「出生盤」起印度占星盤
- 以查詢時刻起印度占星流時盤，評估吉凶
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

import streamlit as st

from astro.vedic.indian import compute_vedic_chart
from astro.qizheng.financial.stock_fetcher import (
    fetch_stock_info,
    get_display_name,
    get_strength_label,
)


_BENEFIC = frozenset({"Jupiter", "Venus", "Mercury", "Moon"})
_MALEFIC = frozenset({"Saturn", "Mars", "Rahu", "Ketu", "Sun"})

_PLANET_BASE_SCORE = {
    "Jupiter": 3,
    "Venus": 2,
    "Mercury": 1,
    "Moon": 1,
    "Sun": 0,
    "Mars": -1,
    "Saturn": -1,
    "Rahu": -1,
    "Ketu": -1,
}

_HOUSE_SCORE = {
    1: 2, 2: 1, 3: 0, 4: 1, 5: 2, 6: -1,
    7: 1, 8: -2, 9: 2, 10: 2, 11: 1, 12: -2,
}

_OWN_SIGNS = {
    "Sun": {"Simha"},
    "Moon": {"Karka"},
    "Mars": {"Mesha", "Vrischika"},
    "Mercury": {"Mithuna", "Kanya"},
    "Jupiter": {"Dhanu", "Meena"},
    "Venus": {"Vrishabha", "Tula"},
    "Saturn": {"Makara", "Kumbha"},
}

# Market tuple shape: (timezone, latitude, longitude)
_MARKET_HK = (8.0, 22.3193, 114.1694)
_MARKET_SH = (8.0, 31.2304, 121.4737)
_MARKET_SZ = (8.0, 22.5431, 114.0579)
_MARKET_DEFAULT = (-5.0, 40.7128, -74.0060)

_QUERY_MINUTE = 30  # Use half-hour snapshot for hourly transit scoring.


@dataclass
class VedicStockFortuneEntry:
    planet: str
    house: int
    rashi: str
    score: int
    judgment_zh: str
    judgment_en: str


@dataclass
class VedicStockFortuneData:
    query_date: date
    query_hour: int
    entries: list[VedicStockFortuneEntry] = field(default_factory=list)
    total_score: int = 0
    overall_zh: str = ""
    overall_en: str = ""


@dataclass
class VedicStockData:
    ipo_chart: object
    query_chart: object
    daily_fortune: VedicStockFortuneData
    price_ratio: Optional[float]
    strength_label_zh: str
    strength_label_en: str
    strength_color: str



def _planet_key(name: str) -> str:
    return name.split(" ")[0].strip()



def _score_planet(planet) -> tuple[int, str, str]:
    key = _planet_key(planet.name)
    score = _PLANET_BASE_SCORE.get(key, 0)

    house_mod = _HOUSE_SCORE.get(getattr(planet, "house", 0), 0)
    score += house_mod

    if key in _OWN_SIGNS and planet.rashi in _OWN_SIGNS[key]:
        score += 1

    if planet.retrograde:
        if key in _BENEFIC:
            score -= 1
        elif key in _MALEFIC:
            score += 1

    if score >= 3:
        zh = "吉星得勢，主多頭有利"
        en = "Strongly auspicious for bullish momentum"
    elif score >= 1:
        zh = "星力偏吉，可審慎布局"
        en = "Mildly auspicious; prudent entries favored"
    elif score == 0:
        zh = "星力中和，宜觀察"
        en = "Neutral energy; observe first"
    elif score >= -2:
        zh = "凶象漸顯，控制風險"
        en = "Rising downside risk; tighten risk control"
    else:
        zh = "煞象偏重，宜保守"
        en = "Strong malefic pressure; stay defensive"

    return score, zh, en


@st.cache_data(ttl=300, show_spinner=False)
def compute_vedic_stock_data(
    ipo_year: int,
    ipo_month: int,
    ipo_day: int,
    ipo_hour: int,
    ipo_minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    query_year: int,
    query_month: int,
    query_day: int,
    query_hour: int,
    current_price: Optional[float],
    week52_high: Optional[float],
    week52_low: Optional[float],
    query_minute: int = _QUERY_MINUTE,
) -> VedicStockData:
    ipo_chart = compute_vedic_chart(
        year=ipo_year,
        month=ipo_month,
        day=ipo_day,
        hour=ipo_hour,
        minute=ipo_minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name="Stock IPO",
    )

    query_chart = compute_vedic_chart(
        year=query_year,
        month=query_month,
        day=query_day,
        hour=query_hour,
        minute=query_minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name="Stock Transit",
    )

    entries: list[VedicStockFortuneEntry] = []
    total_score = 0
    for p in query_chart.planets:
        score, j_zh, j_en = _score_planet(p)
        total_score += score
        entries.append(
            VedicStockFortuneEntry(
                planet=p.name,
                house=getattr(p, "house", 0),
                rashi=p.rashi,
                score=score,
                judgment_zh=j_zh,
                judgment_en=j_en,
            )
        )

    if total_score >= 10:
        overall_zh = "整體星勢大吉，偏多格局明顯。"
        overall_en = "Overall strongly auspicious and bullish."
    elif total_score >= 4:
        overall_zh = "整體偏吉，可分批布局。"
        overall_en = "Overall mildly auspicious; scale in gradually."
    elif total_score >= -2:
        overall_zh = "星勢中性，宜等待確認。"
        overall_en = "Neutral conditions; wait for confirmation."
    elif total_score >= -8:
        overall_zh = "凶象偏多，宜守不宜攻。"
        overall_en = "More malefic signs; defend rather than attack."
    else:
        overall_zh = "煞象顯著，宜降低曝險。"
        overall_en = "Strongly adverse; reduce exposure."

    daily_fortune = VedicStockFortuneData(
        query_date=date(query_year, query_month, query_day),
        query_hour=query_hour,
        entries=entries,
        total_score=total_score,
        overall_zh=overall_zh,
        overall_en=overall_en,
    )

    if (
        current_price is not None
        and week52_high is not None
        and week52_low is not None
        and week52_high != week52_low
    ):
        raw_ratio = (current_price - week52_low) / (week52_high - week52_low)
        clamped_ratio = max(0.0, min(1.0, raw_ratio))
        ratio = clamped_ratio * 100.0
    else:
        ratio = None

    label_zh, label_en, color = get_strength_label(ratio)

    return VedicStockData(
        ipo_chart=ipo_chart,
        query_chart=query_chart,
        daily_fortune=daily_fortune,
        price_ratio=ratio,
        strength_label_zh=label_zh,
        strength_label_en=label_en,
        strength_color=color,
    )



def _infer_market_location(normalized_ticker: str) -> tuple[float, float, float]:
    t = (normalized_ticker or "").upper()
    if t.endswith(".HK"):
        return _MARKET_HK
    if t.endswith(".SS"):
        return _MARKET_SH
    if t.endswith(".SZ"):
        return _MARKET_SZ
    return _MARKET_DEFAULT


def _format_price(value: Optional[float]) -> str:
    if value is None:
        return "—"
    if value >= 1000:
        return f"{value:.1f}"
    if value >= 1:
        return f"{value:.2f}"
    return f"{value:.3f}"



def render_vedic_financial_tab(input_tz: float = 8.0):
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, rgba(70,30,140,0.2), rgba(15,10,45,0.45));
            border: 1px solid rgba(180,140,255,0.35);
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 18px;
        ">
        <span style="font-size:1.1em;font-weight:700;color:#d8b4fe;">💰 印度金融占星 / Vedic Financial Astrology</span><br/>
        <span style="color:#c4b5fd;font-size:0.9em;">
        可搜尋股票，以上市時間作為印度占星起盤，並以查詢時刻判斷吉凶。
        / Search stocks, cast IPO as Vedic birth chart, and judge auspiciousness by transit time.
        </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_input, col_info = st.columns([1, 2], gap="medium")

    with col_input:
        ticker_input = st.text_input(
            "股票代碼 / Ticker",
            value=st.session_state.get("_vedic_stock_ticker", ""),
            placeholder="700.HK / AAPL / 600519.SS",
            key="_vedic_stock_ticker_input",
        )
        fetch_btn = st.button("📡 搜尋股票 / Fetch Stock", key="_vedic_stock_fetch_btn", width="stretch")

        if fetch_btn and ticker_input.strip():
            st.session_state["_vedic_stock_ticker"] = ticker_input.strip()
            st.session_state.pop("_vedic_stock_info", None)

        active_ticker = st.session_state.get("_vedic_stock_ticker", "").strip()
        if active_ticker and "_vedic_stock_info" not in st.session_state:
            with st.spinner(f"擷取 {active_ticker} 中… / Fetching {active_ticker}…"):
                st.session_state["_vedic_stock_info"] = fetch_stock_info(active_ticker)

        stock = st.session_state.get("_vedic_stock_info")

    with col_info:
        if stock and not stock.error:
            name = get_display_name(stock)
            price_str = _format_price(stock.current_price)
            st.markdown(f"**{name}**  ")
            st.caption(f"{stock.normalized_ticker} | {stock.exchange or 'N/A'} | {stock.currency or 'N/A'}")
            st.write(f"現價 / Price: **{price_str}**")
            st.write(f"52W High/Low: **{stock.week52_high or '—'} / {stock.week52_low or '—'}**")

    if not stock or stock.error:
        if stock and stock.error:
            st.error(stock.error)
        else:
            st.info("請先輸入股票代碼並搜尋。 / Enter a ticker first.")
        return

    default_tz, default_lat, default_lon = _infer_market_location(stock.normalized_ticker)

    st.divider()
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        ipo_date = st.date_input(
            "上市日期 / IPO Date",
            value=stock.ipo_date or date(2000, 1, 1),
            key="_vedic_stock_ipo_date",
        )
    with c2:
        ipo_time = st.time_input(
            "上市時間 / IPO Time",
            value=datetime.strptime("09:30", "%H:%M").time(),
            key="_vedic_stock_ipo_time",
            step=60,
        )
    with c3:
        timezone = st.number_input(
            "時區 / Timezone",
            value=float(default_tz if default_tz is not None else input_tz),
            min_value=-12.0,
            max_value=14.0,
            step=0.5,
            key="_vedic_stock_tz",
        )
    with c4:
        latitude = st.number_input(
            "緯度 / Latitude",
            value=float(default_lat),
            min_value=-90.0,
            max_value=90.0,
            step=0.0001,
            format="%.4f",
            key="_vedic_stock_lat",
        )
    with c5:
        longitude = st.number_input(
            "經度 / Longitude",
            value=float(default_lon),
            min_value=-180.0,
            max_value=180.0,
            step=0.0001,
            format="%.4f",
            key="_vedic_stock_lon",
        )

    q1, q2 = st.columns(2)
    with q1:
        query_date = st.date_input("查詢日期 / Query Date", value=date.today(), key="_vedic_stock_query_date")
    with q2:
        query_hour = st.slider("查詢時辰 / Query Hour", 0, 23, datetime.now().hour, key="_vedic_stock_query_hour")

    with st.spinner("🔮 計算印度金融占星… / Computing Vedic financial astrology…"):
        data = compute_vedic_stock_data(
            ipo_year=ipo_date.year,
            ipo_month=ipo_date.month,
            ipo_day=ipo_date.day,
            ipo_hour=ipo_time.hour,
            ipo_minute=ipo_time.minute,
            timezone=float(timezone),
            latitude=float(latitude),
            longitude=float(longitude),
            query_year=query_date.year,
            query_month=query_date.month,
            query_day=query_date.day,
            query_hour=int(query_hour),
            query_minute=_QUERY_MINUTE,
            current_price=stock.current_price,
            week52_high=stock.week52_high,
            week52_low=stock.week52_low,
        )

    tab_ipo, tab_fortune, tab_strength = st.tabs([
        "🌠 IPO 印度盤 / IPO Vedic Chart",
        "📅 流時吉凶 / Transit Fortune",
        "💹 強弱度 / Price Strength",
    ])

    with tab_ipo:
        st.subheader("🌠 IPO 印度占星盤")
        st.caption(f"Lagna: {data.ipo_chart.asc_rashi} | Ayanamsa: {data.ipo_chart.ayanamsa:.2f}°")
        rows = []
        for p in data.ipo_chart.planets:
            rows.append({
                "Graha": p.name,
                "House": p.house,
                "Rashi": f"{p.rashi} ({p.rashi_chinese})",
                "Degree": f"{p.sign_degree:.2f}°",
                "Nakshatra": f"{p.nakshatra} ({p.nakshatra_chinese})",
                "R": "℞" if p.retrograde else "",
            })
        st.dataframe(rows, width="stretch")

    with tab_fortune:
        df = data.daily_fortune
        st.subheader(f"📅 {df.query_date} {df.query_hour:02d}:00 吉凶總評")
        st.info(f"{df.overall_zh} / {df.overall_en}（Score: {df.total_score:+d}）")
        rows = [
            {
                "Graha": e.planet,
                "House": e.house,
                "Rashi": e.rashi,
                "Score": e.score,
                "判語": e.judgment_zh,
                "Judgment": e.judgment_en,
            }
            for e in df.entries
        ]
        st.dataframe(rows, width="stretch")

    with tab_strength:
        ratio_str = f"{data.price_ratio:.1f}%" if data.price_ratio is not None else "N/A"
        st.subheader("💹 52 週強弱度")
        st.markdown(
            f"<span style='color:{data.strength_color};font-weight:700;font-size:1.1em;'>"
            f"{ratio_str} · {data.strength_label_zh} / {data.strength_label_en}</span>",
            unsafe_allow_html=True,
        )
