"""
astro/western/predictive_ui.py — 預測技術全套 Streamlit 前端模組
Full Predictive Techniques Suite — Streamlit UI

美學風格：深色高端占星質感、精緻漸層、微互動動畫、現代排版
整合 Plotly 互動式生命時間軸、PDF 匯出、中西預測對照表、AI 解讀
"""

from __future__ import annotations

import io
import math
from datetime import datetime
from typing import Optional

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from astro.western.predictive import (
    compute_secondary_progressions,
    compute_solar_arc_directions,
    compute_primary_directions,
    compute_life_timeline,
    detect_major_activations,
    compute_chinese_western_crossref,
    TECHNIQUE_COLORS,
    PLANET_COLORS,
    ZODIAC_SIGNS,
    _format_lon,
    _sign_index,
)

# ============================================================
# 通用 CSS（深色占星美學主題）
# ============================================================

PREDICTIVE_CSS = """
<style>
/* ── 預測技術全套專用樣式 ── */
.pred-hero {
    background: linear-gradient(135deg,
        rgba(15,10,40,0.97) 0%,
        rgba(30,15,60,0.95) 40%,
        rgba(10,25,50,0.97) 100%);
    border: 1px solid rgba(167,139,250,0.25);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05);
}
.pred-hero::before {
    content: "✦ ✧ ✦ ✧ ✦ ✧ ✦";
    position: absolute;
    top: 12px; right: 20px;
    color: rgba(234,179,8,0.2);
    font-size: 0.85rem;
    letter-spacing: 4px;
}
.pred-hero-title {
    font-family: 'Cinzel', 'Noto Serif TC', serif;
    font-size: clamp(1.4rem, 3vw, 2rem);
    font-weight: 700;
    background: linear-gradient(135deg, #EAB308 0%, #A78BFA 60%, #7DD3FC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.4rem 0;
    letter-spacing: 0.05em;
}
.pred-hero-sub {
    color: rgba(200,185,255,0.75);
    font-size: 0.9rem;
    letter-spacing: 0.08em;
    margin: 0;
}
.pred-technique-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    margin: 0.2rem 0.2rem;
    border: 1px solid;
}
.pred-badge-sp   { background: rgba(167,139,250,0.12); border-color: rgba(167,139,250,0.4); color: #A78BFA; }
.pred-badge-sa   { background: rgba(234,179,8,0.12);   border-color: rgba(234,179,8,0.4);   color: #EAB308; }
.pred-badge-pd   { background: rgba(59,130,246,0.12);  border-color: rgba(59,130,246,0.4);  color: #7DD3FC; }
.pred-badge-sr   { background: rgba(249,115,22,0.12);  border-color: rgba(249,115,22,0.4);  color: #F97316; }
.pred-badge-lr   { background: rgba(110,231,183,0.12); border-color: rgba(110,231,183,0.4); color: #6EE7B7; }

.pred-section-header {
    font-family: 'Cinzel', 'Noto Serif TC', serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #EAB308;
    letter-spacing: 0.08em;
    border-bottom: 1px solid rgba(234,179,8,0.25);
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem 0;
}
.pred-planet-card {
    background: linear-gradient(135deg, rgba(20,15,50,0.9), rgba(10,20,40,0.9));
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin: 0.4rem 0;
    transition: all 0.25s ease;
}
.pred-planet-card:hover {
    border-color: rgba(167,139,250,0.5);
    box-shadow: 0 4px 16px rgba(167,139,250,0.15);
}
.pred-crossref-row {
    background: linear-gradient(90deg, rgba(20,15,50,0.85), rgba(10,25,45,0.85));
    border: 1px solid rgba(100,80,180,0.2);
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin: 0.3rem 0;
    font-size: 0.88rem;
}
.pred-major-year {
    background: linear-gradient(135deg, rgba(255,68,68,0.1), rgba(234,179,8,0.1));
    border: 1px solid rgba(255,68,68,0.35);
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin: 0.4rem 0;
    color: #FFB3B3;
    font-size: 0.88rem;
}
.pred-export-btn {
    background: linear-gradient(135deg, rgba(167,139,250,0.2), rgba(59,130,246,0.2));
    border: 1px solid rgba(167,139,250,0.4);
    color: #A78BFA;
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s ease;
}
</style>
"""


# ============================================================
# 輔助渲染函數
# ============================================================

def _first_two_words(s: str) -> str:
    """Extract the first two whitespace-separated words from a string.

    Used to match aspect names like 'Conjunction ☌' or 'Trine △' from
    longer strings such as 'Conjunction ☌ (some details)'.
    """
    parts = s.split()
    return " ".join(parts[:2]) if len(parts) >= 2 else s


def _render_technique_badges():
    """渲染技術徽章列表"""
    badges = [
        ("pred-badge-sp", "🌙", "次進法 SP"),
        ("pred-badge-sa", "☀️", "太陽弧 SA"),
        ("pred-badge-pd", "🔭", "初級方向 PD"),
        ("pred-badge-sr", "🌟", "太陽返照 SR"),
        ("pred-badge-lr", "🌊", "月亮返照 LR"),
    ]
    html = '<div style="margin: 0.5rem 0;">'
    for cls, icon, label in badges:
        html += f'<span class="pred-technique-badge {cls}">{icon} {label}</span>'
    html += "</div>"
    return html


def _render_section_header(icon: str, title_zh: str, title_en: str):
    """渲染美觀的分節標題"""
    st.markdown(
        f'<div class="pred-section-header">{icon} {title_zh} <span style="color:rgba(167,139,250,0.6);font-size:0.85em">/ {title_en}</span></div>',
        unsafe_allow_html=True,
    )


def _planet_sign_str(lon: float) -> str:
    """格式化行星黃道位置"""
    idx = _sign_index(lon)
    sign = ZODIAC_SIGNS[idx]
    within = lon % 30
    d = int(within)
    m = int((within - d) * 60)
    return f"{sign[1]} {sign[0]} {d}°{m:02d}' ({sign[2]})"


def _get_natal_dict(w_chart) -> dict[str, float]:
    """從 WesternChart 物件提取本命行星位置字典"""
    return {p.name: p.longitude for p in w_chart.planets}


# ============================================================
# 次進法 UI
# ============================================================

def _render_secondary_progressions(
    w_chart,
    target_age: float,
    lang: str = "zh",
):
    """渲染次進法 (Secondary Progressions) 分頁"""
    _render_section_header("🌙", "次進法 Secondary Progressions", "Day-for-a-Year Method")

    natal_dict = _get_natal_dict(w_chart)
    birth_jd = w_chart.julian_day

    with st.spinner("計算次進行星位置… Computing SP positions…"):
        sp = compute_secondary_progressions(
            birth_jd, target_age,
            w_chart.latitude, w_chart.longitude,
            natal_dict,
            getattr(w_chart, "sidereal_mode", False),
        )

    # 顯示推進日期
    st.markdown(
        f'<div class="pred-planet-card" style="border-color:rgba(167,139,250,0.4)">'
        f'<span style="color:#A78BFA;font-weight:600">推進日期 Progressed Date</span>: '
        f'<span style="color:#EAB308">{sp.progressed_date}</span> '
        f'&nbsp;|&nbsp; 推進 ASC: <span style="color:#FFD700">{_planet_sign_str(sp.progressed_asc)}</span> '
        f'&nbsp;|&nbsp; 推進 MC: <span style="color:#FF6347">{_planet_sign_str(sp.progressed_mc)}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # 行星位置對照表
    import pandas as pd
    rows = []
    for pp in sp.progressed_planets:
        natal_lon = natal_dict.get(pp.name, 0.0)
        retro = "℞" if pp.retrograde else ""
        rows.append({
            "行星 Planet": pp.name,
            "本命位置 Natal": _planet_sign_str(natal_lon),
            "推進位置 Progressed": f"{_planet_sign_str(pp.progressed_lon)} {retro}",
            "移動弧度 Arc": f"{pp.arc_moved:+.2f}°",
            "相位 Aspects": ", ".join(
                f"{a['aspect']}→{a['natal_planet']}({a['orb']}°)"
                for a in pp.aspects_to_natal[:2]
            ) if pp.aspects_to_natal else "—",
        })

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch", hide_index=True)

    # 重要相位高亮
    active_aspects = [
        (pp, asp)
        for pp in sp.progressed_planets
        for asp in pp.aspects_to_natal
    ]
    if active_aspects:
        _render_section_header("⚡", "活躍相位", "Active Aspects")
        for pp, asp in active_aspects[:8]:
            asp_color = {
                "Conjunction ☌": "#FFD700",
                "Opposition ☍":  "#FF6B6B",
                "Trine △":       "#6EE7B7",
                "Square □":      "#F97316",
                "Sextile ⚹":     "#7DD3FC",
            }.get(_first_two_words(asp["aspect"]), "#A78BFA")
            st.markdown(
                f'<div class="pred-planet-card">'
                f'<span style="color:{PLANET_COLORS.get(pp.name, "#A78BFA")};font-weight:700">{pp.name}</span> '
                f'<span style="color:{asp_color};font-size:1.1em">{asp["aspect"]}</span> '
                f'<span style="color:#C0C0FF">{asp["natal_planet"]}</span> '
                f'<span style="color:rgba(200,200,200,0.6);font-size:0.85em">(orb {asp["orb"]}°)</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("此年齡段無顯著次進相位 / No significant SP aspects at this age.")


# ============================================================
# 太陽弧方向 UI
# ============================================================

def _render_solar_arc(
    w_chart,
    target_age: float,
    lang: str = "zh",
):
    """渲染太陽弧方向 (Solar Arc Directions) 分頁"""
    _render_section_header("☀️", "太陽弧方向 Solar Arc Directions", "SA = Progressed Sun − Natal Sun")

    natal_dict = _get_natal_dict(w_chart)
    birth_jd = w_chart.julian_day

    with st.spinner("計算太陽弧… Computing Solar Arc…"):
        sa = compute_solar_arc_directions(
            birth_jd, target_age, natal_dict,
            w_chart.ascendant, w_chart.midheaven,
            getattr(w_chart, "sidereal_mode", False),
        )

    # 太陽弧摘要卡
    st.markdown(
        f'<div class="pred-planet-card" style="border-color:rgba(234,179,8,0.4)">'
        f'<span style="color:#EAB308;font-weight:700">太陽弧 Solar Arc</span>: '
        f'<span style="color:#FFD700;font-size:1.2em">{sa.solar_arc:+.3f}°</span>'
        f'&nbsp;|&nbsp; SA ASC: <span style="color:#FFD700">{_planet_sign_str(sa.sa_asc)}</span>'
        f'&nbsp;|&nbsp; SA MC: <span style="color:#FF6347">{_planet_sign_str(sa.sa_mc)}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    import pandas as pd
    rows = []
    for sap in sa.sa_planets:
        rows.append({
            "行星 Planet": sap.name,
            "本命位置 Natal": _planet_sign_str(sap.natal_lon),
            "太陽弧位置 SA": _planet_sign_str(sap.arc_lon),
            "相位 Aspects": ", ".join(
                f"{a['aspect']}→{a['natal_planet']}({a['orb']}°)"
                for a in sap.aspects_to_natal[:2]
            ) if sap.aspects_to_natal else "—",
        })

    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    # 活躍相位
    active_sa = [
        (sap, asp)
        for sap in sa.sa_planets
        for asp in sap.aspects_to_natal
    ]
    if active_sa:
        _render_section_header("⚡", "太陽弧活躍相位", "Active SA Aspects")
        for sap, asp in active_sa[:8]:
            st.markdown(
                f'<div class="pred-planet-card">'
                f'<b style="color:{PLANET_COLORS.get(sap.name, "#EAB308")}">{sap.name}</b> '
                f'<b style="color:#EAB308">[SA]</b> '
                f'<span style="color:#FFD700">{asp["aspect"]}</span> '
                f'<span style="color:#C0C0FF">本命 {asp["natal_planet"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ============================================================
# 初級方向 UI
# ============================================================

def _render_primary_directions(
    w_chart,
    age_min: int,
    age_max: int,
    house_system: str,
    include_converse: bool,
    lang: str = "zh",
):
    """渲染初級方向 (Primary Directions) 分頁"""
    _render_section_header("🔭", "初級方向 Primary Directions", f"{house_system} System")

    natal_dict = _get_natal_dict(w_chart)
    birth_jd = w_chart.julian_day
    birth_year = w_chart.year

    with st.spinner(f"計算 {house_system} 初級方向… Computing Primary Directions…"):
        events = compute_primary_directions(
            birth_jd, natal_dict, w_chart.ascendant, w_chart.midheaven,
            w_chart.latitude, w_chart.longitude,
            house_system=house_system,
            birth_year=birth_year,
            age_range=(age_min, age_max),
            orb=1.0,
            include_converse=include_converse,
        )

    if not events:
        st.info("此範圍內無初級方向事件 / No Primary Direction events in this range.")
        return

    st.caption(f"共找到 {len(events)} 個事件 / Found {len(events)} events")

    import pandas as pd
    rows = []
    for ev in events:
        rows.append({
            "觸發年 Year": ev.year,
            "年齡 Age": f"{ev.age:.1f}",
            "受照者 Sig.": ev.significator,
            "方向 Dir.": ev.direction_type,
            "施照者 Prom.": ev.promissor,
            "相位 Asp.": ev.aspect,
            "宮位制 System": ev.house_system,
            "解釋 Interp.": ev.interpretation_zh if lang in ("zh", "zh_cn") else ev.interpretation_en,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True, height=400)

    # 詳細事件展示（前10個）
    _render_section_header("📅", "重要事件詳解", "Key Events Detail")
    for ev in events[:10]:
        with st.expander(
            f"🔭 {ev.year} 年（{ev.age:.1f} 歲）— {ev.significator} → {ev.promissor}"
        ):
            interp = ev.interpretation_zh if lang in ("zh", "zh_cn") else ev.interpretation_en
            st.markdown(f"**宮位制 System:** {ev.house_system} | **方向 Direction:** {ev.direction_type}")
            st.markdown(f"**方向弧 Arc:** {ev.arc:.2f}° = {ev.age:.1f} years")
            st.info(interp)


# ============================================================
# 生命時間軸 Plotly 圖表
# ============================================================

def _build_timeline_figure(
    events: list,
    major_events: list,
    birth_year: int,
    age_max: int,
    lang: str = "zh",
) -> go.Figure:
    """建立精美的生命時間軸 Plotly 圖表

    分層顯示各技術，hover 顯示詳細資訊，顏色區分不同技術。
    """
    fig = go.Figure()

    # ── 繪製背景：星空漸層效果 ────────────────────────────────────
    fig.add_shape(
        type="rect",
        x0=birth_year, x1=birth_year + age_max,
        y0=-0.5, y1=5.5,
        fillcolor="rgba(5,5,25,0.95)",
        line=dict(color="rgba(0,0,0,0)"),
        layer="below",
    )

    # ── 技術分層 y 軸位置 ────────────────────────────────────────
    technique_y = {
        "Secondary Progression": 4,
        "Solar Arc":             3,
        "Primary Direction":     2,
        "Solar Return":          1,
        "Lunar Return":          0,
    }

    technique_labels_zh = {
        "Secondary Progression": "🌙 次進法",
        "Solar Arc":             "☀️ 太陽弧",
        "Primary Direction":     "🔭 初級方向",
        "Solar Return":          "🌟 太陽返照",
        "Lunar Return":          "🌊 月返照",
    }

    # ── 分技術繪製散點 ────────────────────────────────────────────
    technique_groups: dict[str, list] = {}
    for ev in events:
        t = ev.technique
        if t not in technique_groups:
            technique_groups[t] = []
        technique_groups[t].append(ev)

    for technique, evs in technique_groups.items():
        y_pos = technique_y.get(technique, 0)
        color = TECHNIQUE_COLORS.get(technique, "#888")

        xs = [ev.year for ev in evs]
        ys = [y_pos + 0.0 for _ in evs]
        sizes = [max(6, min(24, ev.intensity * 20)) for ev in evs]
        opacities = [max(0.3, min(1.0, ev.intensity)) for ev in evs]

        hover_texts = []
        for ev in evs:
            desc = ev.description_zh if lang in ("zh", "zh_cn") else ev.description_en
            hover_texts.append(
                f"<b style='color:{color}'>{technique}</b><br>"
                f"年份 Year: <b>{int(ev.year)}</b> | 年齡 Age: <b>{ev.age:.1f}</b><br>"
                f"{ev.planet_a} {ev.aspect} {ev.planet_b}<br>"
                f"<i>{desc}</i>"
            )

        label = technique_labels_zh.get(technique, technique) if lang in ("zh", "zh_cn") else technique

        fig.add_trace(go.Scatter(
            x=xs,
            y=ys,
            mode="markers",
            name=label,
            marker=dict(
                size=sizes,
                color=color,
                opacity=opacities,
                symbol="circle",
                line=dict(color=color, width=1),
            ),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=hover_texts,
        ))

    # ── 繪製重大激活事件（特殊標記） ─────────────────────────────
    if major_events:
        mx = [ev.year for ev in major_events]
        my = [5.2 for _ in major_events]
        ms = [max(10, min(30, ev.intensity * 28)) for ev in major_events]
        m_hover = [
            f"<b style='color:#FF4444'>⚡ 重大激活年</b><br>"
            f"年份: <b>{int(ev.year)}</b> | 年齡: <b>{ev.age:.1f}</b><br>"
            f"{ev.description_zh if lang in ('zh', 'zh_cn') else ev.description_en}"
            for ev in major_events
        ]
        fig.add_trace(go.Scatter(
            x=mx, y=my,
            mode="markers+text",
            name="⚡ 重大激活 Major" if lang in ("zh", "zh_cn") else "⚡ Major Activation",
            marker=dict(
                size=ms, color="#FF4444",
                symbol="star", opacity=0.9,
                line=dict(color="#FFD700", width=1.5),
            ),
            text=[str(int(ev.year)) for ev in major_events],
            textposition="top center",
            textfont=dict(color="#FFD700", size=10, family="Cinzel"),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=m_hover,
        ))

    # ── 繪製年代背景帶（10年一格） ────────────────────────────────
    for decade_offset in range(0, age_max, 10):
        decade_year = birth_year + decade_offset
        fig.add_vline(
            x=decade_year,
            line=dict(color="rgba(167,139,250,0.12)", width=1, dash="dot"),
        )
        fig.add_annotation(
            x=decade_year, y=5.6,
            text=f"{decade_offset}歲" if lang in ("zh", "zh_cn") else f"Age {decade_offset}",
            showarrow=False,
            font=dict(size=9, color="rgba(200,180,255,0.5)", family="Noto Serif TC"),
        )

    # ── 圖表佈局 ─────────────────────────────────────────────────
    fig.update_layout(
        title=dict(
            text="✦ 生命時間軸 Life Timeline ✦" if lang in ("zh", "zh_cn") else "✦ Life Timeline ✦",
            font=dict(size=16, family="Cinzel, serif", color="#EAB308"),
            x=0.5, xanchor="center",
        ),
        paper_bgcolor="rgba(5,5,25,0.95)",
        plot_bgcolor="rgba(8,8,30,0.90)",
        font=dict(family="Noto Serif TC, Cinzel, sans-serif", color="#C0C0FF"),
        xaxis=dict(
            title=dict(text="公曆年份 Year" if lang in ("zh", "zh_cn") else "Year", font=dict(color="#A78BFA")),
            tickfont=dict(color="#8080CC"),
            gridcolor="rgba(100,80,200,0.08)",
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            tickvals=[0, 1, 2, 3, 4, 5.2],
            ticktext=[
                "🌊 月返照",
                "🌟 太陽返照",
                "🔭 初級方向",
                "☀️ 太陽弧",
                "🌙 次進法",
                "⚡ 重大激活",
            ] if lang in ("zh", "zh_cn") else [
                "🌊 Lunar Ret.",
                "🌟 Solar Ret.",
                "🔭 Primary Dir.",
                "☀️ Solar Arc",
                "🌙 Sec. Prog.",
                "⚡ Major",
            ],
            tickfont=dict(color="#A78BFA", size=11),
            gridcolor="rgba(100,80,200,0.06)",
            showgrid=True,
            zeroline=False,
        ),
        legend=dict(
            bgcolor="rgba(10,8,30,0.85)",
            bordercolor="rgba(167,139,250,0.3)",
            borderwidth=1,
            font=dict(color="#C0C0FF", size=11),
            orientation="h",
            y=-0.15,
            x=0.5,
            xanchor="center",
        ),
        margin=dict(l=20, r=20, t=60, b=80),
        height=500,
        hoverlabel=dict(
            bgcolor="rgba(10,5,30,0.97)",
            bordercolor="rgba(167,139,250,0.5)",
            font=dict(color="#E0E0FF", size=12, family="Noto Serif TC"),
        ),
    )

    return fig


def _render_life_timeline(
    w_chart,
    age_min: int,
    age_max: int,
    lang: str = "zh",
):
    """渲染生命時間軸主要介面"""
    _render_section_header("📊", "生命時間軸", "Life Timeline")

    natal_dict = _get_natal_dict(w_chart)
    birth_year = w_chart.year
    birth_jd = w_chart.julian_day
    sidereal = getattr(w_chart, "sidereal_mode", False)

    with st.spinner("計算生命時間軸（可能需要幾秒）… Computing Life Timeline…"):
        timeline_events = compute_life_timeline(
            birth_jd, birth_year, natal_dict,
            w_chart.ascendant, w_chart.midheaven,
            w_chart.latitude, w_chart.longitude,
            age_min=age_min, age_max=age_max,
            sidereal=sidereal,
        )

    # 偵測重大激活事件
    major_events = detect_major_activations(timeline_events, min_intensity=0.5)

    # 摘要統計
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        sp_count = sum(1 for e in timeline_events if e.technique == "Secondary Progression")
        st.metric("🌙 次進法 SP", sp_count)
    with col2:
        sa_count = sum(1 for e in timeline_events if e.technique == "Solar Arc")
        st.metric("☀️ 太陽弧 SA", sa_count)
    with col3:
        pd_count = sum(1 for e in timeline_events if e.technique == "Primary Direction")
        st.metric("🔭 初級方向 PD", pd_count)
    with col4:
        st.metric("⚡ 重大激活年", len(major_events))

    # 繪製 Plotly 時間軸
    fig = _build_timeline_figure(
        timeline_events, major_events, birth_year, age_max, lang
    )
    st.plotly_chart(fig, width="stretch", config={
        "displayModeBar": True,
        "modeBarButtonsToAdd": ["downloadSVG"],
        "scrollZoom": True,
    })

    # 重大激活年詳情
    if major_events:
        _render_section_header("⚡", "重大激活年份", "Major Activation Years")
        cols = st.columns(min(3, len(major_events)))
        for i, ev in enumerate(major_events[:9]):
            with cols[i % 3]:
                st.markdown(
                    f'<div class="pred-major-year">'
                    f'<b style="color:#FF8888">{int(ev.year)} 年</b> ({ev.age:.0f} 歲)<br>'
                    f'<span style="color:#FFD0D0;font-size:0.8em">{ev.description_zh if lang in ("zh","zh_cn") else ev.description_en}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    return timeline_events, major_events


# ============================================================
# 中西預測對照表 UI
# ============================================================

def _render_cross_reference(
    w_chart,
    age_min: int,
    age_max: int,
    lang: str = "zh",
):
    """渲染中西預測技術對照表"""
    _render_section_header("☯️", "中西預測對照表", "Chinese-Western Cross Reference")

    # 取得本命上升星座索引
    asc_idx = _sign_index(w_chart.ascendant)
    crossref = compute_chinese_western_crossref(
        w_chart.year, w_chart.month,
        asc_idx, age_min, age_max,
    )

    import pandas as pd
    rows = []
    for cr in crossref:
        rows.append({
            "年齡 Age": f"{cr['age_start']}–{cr['age_end']}",
            "公曆年 Year": f"{cr['year_start']}–{cr['year_end']}",
            "七政大限 QZ Period": cr["qizheng_desc_zh"],
            "次進太陽 SP Sun": cr["western_sp"],
            "太陽弧 SA": cr["western_sa"],
        })

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch", hide_index=True)

    st.caption(
        "💡 七政大限按上升星座主星起算。對照僅供參考，各體系算法有所不同。\n"
        "Chinese Dasha periods calculated from ASC sign lord. For reference only."
    )


# ============================================================
# AI 解讀資料準備
# ============================================================

def format_predictive_for_ai(
    w_chart,
    target_age: float,
    sp_result,
    sa_result,
    major_events: list,
    lang: str = "zh",
) -> str:
    """格式化預測技術資料為 AI 解讀用文字"""
    lines = []
    lines.append(f"=== 預測技術全套分析 — {w_chart.year}年出生 (目標年齡: {target_age:.1f}歲) ===\n")

    # 次進摘要
    if sp_result:
        lines.append("【次進法 Secondary Progressions】")
        active = [
            (pp, asp)
            for pp in sp_result.progressed_planets
            for asp in pp.aspects_to_natal
            if asp["orb"] <= 1.0
        ]
        for pp, asp in active[:5]:
            lines.append(
                f"  SP {pp.name} {asp['aspect']} 本命 {asp['natal_planet']} "
                f"(orb {asp['orb']}°) — {_planet_sign_str(pp.progressed_lon)}"
            )
        if not active:
            lines.append("  此年齡無顯著次進相位")

    # 太陽弧摘要
    if sa_result:
        lines.append(f"\n【太陽弧方向 Solar Arc = {sa_result.solar_arc:+.2f}°】")
        active_sa = [
            (sap, asp)
            for sap in sa_result.sa_planets
            for asp in sap.aspects_to_natal
            if asp["orb"] <= 1.0
        ]
        for sap, asp in active_sa[:5]:
            lines.append(
                f"  SA {sap.name} {asp['aspect']} 本命 {asp['natal_planet']} (orb {asp['orb']}°)"
            )
        if not active_sa:
            lines.append("  此年齡無顯著太陽弧相位")

    # 重大激活年
    if major_events:
        lines.append("\n【重大激活年 Major Activation Years】")
        for ev in major_events[:5]:
            lines.append(f"  {int(ev.year)}年（{ev.age:.0f}歲）: {ev.description_zh}")

    lines.append("\n請根據以上預測技術資料，提供：")
    lines.append("1. 該年齡段的整體運勢趨勢解讀")
    lines.append("2. 次進法與太陽弧的核心議題")
    lines.append("3. 七政四餘大限對應的中國命理解讀")
    lines.append("4. 人生建議與注意事項")
    lines.append("請同時提供中文與英文解讀。")

    return "\n".join(lines)


# ============================================================
# PDF 匯出
# ============================================================

def _generate_pdf_report(
    w_chart,
    target_age: float,
    sp_result,
    sa_result,
    major_events: list,
    timeline_fig: Optional[go.Figure] = None,
    lang: str = "zh",
) -> bytes:
    """生成 PDF 報告（使用純文字格式，不依賴重型 PDF 庫）

    Returns:
        PDF bytes（若 reportlab 未安裝則回傳 HTML bytes）
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer,
            Table, TableStyle, HRFlowable,
        )
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        )

        styles = getSampleStyleSheet()
        gold = HexColor("#D4AF37")
        purple = HexColor("#7B68EE")
        dark = HexColor("#1a1040")
        light = HexColor("#e0d8ff")

        title_style = ParagraphStyle(
            "AstroTitle",
            parent=styles["Title"],
            textColor=gold,
            fontSize=20,
            spaceAfter=8,
            alignment=TA_CENTER,
        )
        heading_style = ParagraphStyle(
            "AstroHeading",
            parent=styles["Heading2"],
            textColor=purple,
            fontSize=13,
            spaceBefore=12,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "AstroBody",
            parent=styles["Normal"],
            textColor=light,
            fontSize=10,
            leading=14,
            spaceAfter=4,
        )

        story = []

        # 標題
        story.append(Paragraph(
            "✦ 預測技術全套報告 Full Predictive Techniques Report ✦",
            title_style,
        ))
        story.append(Paragraph(
            f"出生年份 Birth Year: {w_chart.year}  |  目標年齡 Target Age: {target_age:.1f}",
            body_style,
        ))
        story.append(HRFlowable(color=gold, thickness=1, spaceAfter=12))

        # 次進法摘要
        story.append(Paragraph("🌙 次進法 Secondary Progressions", heading_style))
        if sp_result:
            story.append(Paragraph(
                f"推進日期: {sp_result.progressed_date}",
                body_style,
            ))
            active = [
                (pp, asp)
                for pp in sp_result.progressed_planets
                for asp in pp.aspects_to_natal
            ]
            for pp, asp in active[:5]:
                story.append(Paragraph(
                    f"  SP {pp.name} {asp['aspect']} 本命 {asp['natal_planet']} (orb {asp['orb']}°)",
                    body_style,
                ))

        # 太陽弧摘要
        story.append(Paragraph("☀️ 太陽弧方向 Solar Arc Directions", heading_style))
        if sa_result:
            story.append(Paragraph(
                f"太陽弧: {sa_result.solar_arc:+.3f}°",
                body_style,
            ))

        # 重大激活年
        story.append(Paragraph("⚡ 重大激活年 Major Activation Years", heading_style))
        for ev in major_events[:10]:
            story.append(Paragraph(
                f"  {int(ev.year)} 年 ({ev.age:.0f} 歲): {ev.description_zh}",
                body_style,
            ))

        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(color=gold, thickness=0.5))
        story.append(Paragraph(
            "Generated by KinAstro 堅占星 | kinastro.streamlit.app",
            ParagraphStyle("Footer", parent=styles["Normal"],
                           textColor=HexColor("#888888"), fontSize=8, alignment=TA_CENTER),
        ))

        doc.build(story)
        return buffer.getvalue()

    except ImportError:
        # reportlab 未安裝時，退回 HTML 格式
        html = _generate_html_report(w_chart, target_age, sp_result, sa_result, major_events, lang)
        return html.encode("utf-8")


def _generate_html_report(
    w_chart,
    target_age: float,
    sp_result,
    sa_result,
    major_events: list,
    lang: str = "zh",
) -> str:
    """生成 HTML 格式報告"""
    lines = [
        "<!DOCTYPE html><html><head>",
        "<meta charset='utf-8'>",
        "<title>KinAstro Predictive Report</title>",
        "<style>",
        "body{background:#0a0520;color:#c0c0ff;font-family:'Noto Serif TC',serif;padding:2rem;}",
        "h1{color:#EAB308;border-bottom:1px solid #EAB308;padding-bottom:0.5rem;}",
        "h2{color:#A78BFA;} .event{background:rgba(40,30,80,0.8);border:1px solid rgba(167,139,250,0.3);",
        "border-radius:8px;padding:0.5rem 1rem;margin:0.3rem 0;} .major{border-color:#FF4444;color:#FFB3B3;}",
        "</style></head><body>",
        f"<h1>✦ 預測技術全套報告 / Predictive Report ✦</h1>",
        f"<p>出生年份: <b>{w_chart.year}</b> | 目標年齡: <b>{target_age:.1f}</b></p>",
    ]

    if sp_result:
        lines.append("<h2>🌙 次進法 Secondary Progressions</h2>")
        lines.append(f"<p>推進日期: <b>{sp_result.progressed_date}</b></p>")
        for pp in sp_result.progressed_planets:
            for asp in pp.aspects_to_natal[:2]:
                lines.append(
                    f"<div class='event'>SP {pp.name} {asp['aspect']} 本命 {asp['natal_planet']}</div>"
                )

    if sa_result:
        lines.append("<h2>☀️ 太陽弧方向 Solar Arc Directions</h2>")
        lines.append(f"<p>太陽弧: <b>{sa_result.solar_arc:+.3f}°</b></p>")

    if major_events:
        lines.append("<h2>⚡ 重大激活年 Major Activation Years</h2>")
        for ev in major_events:
            lines.append(
                f"<div class='event major'><b>{int(ev.year)} 年</b> ({ev.age:.0f} 歲): {ev.description_zh}</div>"
            )

    lines.append("<hr style='border-color:#A78BFA;margin-top:2rem;'>")
    lines.append("<p style='color:#888;font-size:0.8rem;text-align:center'>Generated by KinAstro 堅占星</p>")
    lines.append("</body></html>")
    return "\n".join(lines)


# ============================================================
# 主要渲染函數（入口）
# ============================================================

def render_predictive_suite(
    w_chart,
    lang: str = "zh",
    ai_callback=None,       # AI 解讀回呼函數 (prompt) -> None
):
    """渲染「預測技術全套」完整頁面

    Args:
        w_chart:      WesternChart 物件（本命盤）
        lang:         語言代碼 "zh" / "zh_cn" / "en"
        ai_callback:  AI 解讀回呼，接受 (prompt_text) 並渲染 AI 結果
    """
    # ── CSS 注入 ───────────────────────────────────────────────
    st.markdown(PREDICTIVE_CSS, unsafe_allow_html=True)

    # ── Hero 標題區 ────────────────────────────────────────────
    st.markdown(
        '<div class="pred-hero">'
        '<h2 class="pred-hero-title">✦ 預測技術全套 Full Predictive Suite ✦</h2>'
        '<p class="pred-hero-sub">Secondary Progressions · Solar Arc · Primary Directions · Returns · Life Timeline</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(_render_technique_badges(), unsafe_allow_html=True)

    # ── 側邊控制面板 ───────────────────────────────────────────
    with st.sidebar.expander("🔭 預測技術設定 / Predictive Settings", expanded=False):
        target_age = st.slider(
            "目標年齡 Target Age",
            min_value=1, max_value=90,
            value=35, step=1,
            key="pred_target_age",
        )
        timeline_max = st.slider(
            "時間軸範圍 Timeline Max Age",
            min_value=20, max_value=90,
            value=70, step=5,
            key="pred_timeline_max",
        )
        pd_system = st.selectbox(
            "初級方向宮位制 PD System",
            options=["Placidus", "Regiomontanus", "Topocentric"],
            key="pred_pd_system",
        )
        include_converse = st.checkbox(
            "包含逆行方向 Include Converse",
            value=False,
            key="pred_converse",
        )

    target_age = st.session_state.get("pred_target_age", 35)
    timeline_max = st.session_state.get("pred_timeline_max", 70)
    pd_system = st.session_state.get("pred_pd_system", "Placidus")
    include_converse = st.session_state.get("pred_converse", False)

    # ── 子分頁 ─────────────────────────────────────────────────
    if lang in ("zh", "zh_cn"):
        tab_labels = [
            "🌙 次進法",
            "☀️ 太陽弧",
            "🔭 初級方向",
            "📊 生命時間軸",
            "☯️ 中西對照",
            "🤖 AI 深度解讀",
        ]
    else:
        tab_labels = [
            "🌙 Sec. Prog.",
            "☀️ Solar Arc",
            "🔭 Primary Dir.",
            "📊 Life Timeline",
            "☯️ Cross Ref.",
            "🤖 AI Reading",
        ]

    tabs = st.tabs(tab_labels)

    # ── 計算共用資料 ────────────────────────────────────────────
    natal_dict = _get_natal_dict(w_chart)
    birth_jd = w_chart.julian_day
    sidereal = getattr(w_chart, "sidereal_mode", False)

    sp_result = None
    sa_result = None
    timeline_events = []
    major_events = []

    # ── Tab 0: 次進法 ───────────────────────────────────────────
    with tabs[0]:
        sp_result = compute_secondary_progressions(
            birth_jd, float(target_age),
            w_chart.latitude, w_chart.longitude,
            natal_dict, sidereal,
        )
        _render_secondary_progressions(w_chart, float(target_age), lang)

    # ── Tab 1: 太陽弧方向 ───────────────────────────────────────
    with tabs[1]:
        sa_result = compute_solar_arc_directions(
            birth_jd, float(target_age), natal_dict,
            w_chart.ascendant, w_chart.midheaven, sidereal,
        )
        _render_solar_arc(w_chart, float(target_age), lang)

    # ── Tab 2: 初級方向 ─────────────────────────────────────────
    with tabs[2]:
        _render_primary_directions(
            w_chart,
            age_min=0,
            age_max=timeline_max,
            house_system=pd_system,
            include_converse=include_converse,
            lang=lang,
        )

    # ── Tab 3: 生命時間軸 ───────────────────────────────────────
    with tabs[3]:
        timeline_events, major_events = _render_life_timeline(
            w_chart, age_min=0, age_max=timeline_max, lang=lang,
        )

        # PDF / HTML 匯出按鈕
        st.divider()
        _render_section_header("📄", "匯出報告", "Export Report")
        col_pdf, col_html = st.columns(2)
        with col_pdf:
            if st.button("📄 匯出 PDF 報告", key="pred_export_pdf"):
                with st.spinner("生成報告中…"):
                    pdf_bytes = _generate_pdf_report(
                        w_chart, float(target_age),
                        sp_result, sa_result, major_events,
                        lang=lang,
                    )
                try:
                    # 嘗試確認是否為 PDF（先確認長度再比較 magic bytes）
                    is_pdf = len(pdf_bytes) >= 4 and pdf_bytes[:4] == b"%PDF"
                except Exception:
                    is_pdf = False

                if is_pdf:
                    st.download_button(
                        label="⬇️ 下載 PDF",
                        data=pdf_bytes,
                        file_name=f"kinastro_predictive_{w_chart.year}_{target_age}y.pdf",
                        mime="application/pdf",
                        key="pred_dl_pdf",
                    )
                else:
                    st.download_button(
                        label="⬇️ 下載 HTML 報告",
                        data=pdf_bytes,
                        file_name=f"kinastro_predictive_{w_chart.year}_{target_age}y.html",
                        mime="text/html",
                        key="pred_dl_html",
                    )
        with col_html:
            if st.button("🌐 匯出 HTML 報告", key="pred_export_html"):
                html_str = _generate_html_report(
                    w_chart, float(target_age),
                    sp_result, sa_result, major_events, lang,
                )
                st.download_button(
                    label="⬇️ 下載 HTML",
                    data=html_str.encode("utf-8"),
                    file_name=f"kinastro_predictive_{w_chart.year}_{target_age}y.html",
                    mime="text/html",
                    key="pred_dl_html2",
                )

    # ── Tab 4: 中西對照 ─────────────────────────────────────────
    with tabs[4]:
        _render_cross_reference(w_chart, age_min=0, age_max=timeline_max, lang=lang)

    # ── Tab 5: AI 深度解讀 ──────────────────────────────────────
    with tabs[5]:
        _render_section_header("🤖", "AI 深度解讀", "AI Deep Reading")

        st.markdown(
            '<div class="pred-planet-card" style="border-color:rgba(234,179,8,0.3)">'
            '結合次進法、太陽弧、初級方向及中國大限，生成雙語 AI 深度解讀報告。<br>'
            '<span style="color:rgba(200,180,255,0.6);font-size:0.85em">'
            'Combines SP, SA, Primary Directions & Chinese Dasha for bilingual AI deep reading.</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        if sp_result is None:
            sp_result = compute_secondary_progressions(
                birth_jd, float(target_age),
                w_chart.latitude, w_chart.longitude,
                natal_dict, sidereal,
            )
        if sa_result is None:
            sa_result = compute_solar_arc_directions(
                birth_jd, float(target_age), natal_dict,
                w_chart.ascendant, w_chart.midheaven, sidereal,
            )
        if not major_events:
            tl = compute_life_timeline(
                birth_jd, w_chart.year, natal_dict,
                w_chart.ascendant, w_chart.midheaven,
                w_chart.latitude, w_chart.longitude,
                age_min=max(0, target_age - 10),
                age_max=min(90, target_age + 10),
                sidereal=sidereal,
            )
            major_events = detect_major_activations(tl)

        ai_prompt = format_predictive_for_ai(
            w_chart, float(target_age),
            sp_result, sa_result, major_events, lang,
        )

        with st.expander(
            "📋 查看 AI 解讀提示詞 / View AI Prompt",
            expanded=False,
        ):
            st.code(ai_prompt, language="text")

        if ai_callback is not None:
            ai_callback(ai_prompt)
        else:
            st.info(
                "請在左側側邊欄設定 AI API Key 並點擊「AI 解讀」按鈕。\n"
                "Please configure AI API Key in the sidebar and click 'AI Analysis'."
            )
