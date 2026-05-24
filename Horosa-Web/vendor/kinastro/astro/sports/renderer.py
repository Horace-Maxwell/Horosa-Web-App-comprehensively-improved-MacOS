from __future__ import annotations

from datetime import datetime
from typing import Optional

import plotly.graph_objects as go
import streamlit as st

from astro.chart_renderer_v2 import build_cultural_svg
from astro.horary.renderer import render_western_horary_svg
from astro.i18n import auto_cn, get_lang
from .sports_horary import (
    SportsHoraryResult,
    TeamNatalInput,
    analyze_event_chart_with_team_natal,
    analyze_sports_horary,
    build_ai_interpretation_prompt,
)


_SPORTS_CSS = """
<style>
.sports-shell { background: linear-gradient(160deg, #070b11 0%, #0e1722 65%, #0c2130 100%); border: 1px solid rgba(53, 137, 189, .22); border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.sports-header { background: linear-gradient(145deg, #0d141d 0%, #172430 60%, #173247 100%); border: 1px solid rgba(71, 201, 128, .35); border-left: 6px solid #2ecc71; border-radius: 12px; padding: 16px 20px; margin-bottom: 12px; }
.sports-header h2 { margin: 0; color: #e7fff1; }
.sports-header p { margin: 6px 0 0; color: #a8d9c0; font-size: .92rem; }
.sports-card { background: rgba(9, 13, 19, .78); border: 1px solid rgba(95, 133, 168, .28); border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; }
.sports-muted { color: #95a5b3; font-size: .88rem; }
.sports-disclaimer { background: rgba(192, 57, 43, .10); border-left: 4px solid #e74c3c; border-radius: 8px; color: #ffd4ce; padding: 10px 12px; font-size: .88rem; }
</style>
"""

_POPULAR_MATCHES = [
    {"label": "EPL: Arsenal vs Liverpool", "match": "EPL Round", "team1": "Arsenal", "team2": "Liverpool"},
    {"label": "NBA: Lakers vs Celtics", "match": "NBA Playoffs", "team1": "Lakers", "team2": "Celtics"},
    {"label": "UCL: Real Madrid vs Bayern", "match": "UCL Knockout", "team1": "Real Madrid", "team2": "Bayern"},
]

_HISTORICAL_CASES = [
    {"sport": "Football", "match": "2022 FIFA WC Final: Argentina vs France", "note": "Moon momentum and late reversal signatures."},
    {"sport": "Basketball", "match": "2023 NBA Finals G5: Nuggets vs Heat", "note": "Angular lord strength aligned with home execution."},
]


def _plot_win_probability(result: SportsHoraryResult) -> go.Figure:
    p1 = result.match_analysis.winner_probability[result.team1] * 100
    p2 = result.match_analysis.winner_probability[result.team2] * 100
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[result.team1, result.team2],
        y=[p1, p2],
        marker_color=["#2ecc71", "#e74c3c"],
        text=[f"{p1:.1f}%", f"{p2:.1f}%"],
        textposition="auto",
    ))
    fig.update_layout(
        height=320,
        template="plotly_dark",
        title=auto_cn("勝率對比", "Win Probability"),
        yaxis_title="%",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


def _plot_confidence_gauge(result: SportsHoraryResult) -> go.Figure:
    p = max(result.match_analysis.winner_probability.values()) * 100
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=p,
        number={"suffix": "%"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#1abc9c"},
            "steps": [
                {"range": [0, 45], "color": "#7f8c8d"},
                {"range": [45, 65], "color": "#2980b9"},
                {"range": [65, 100], "color": "#27ae60"},
            ],
        },
        title={"text": auto_cn("主導勝率儀表", "Edge Gauge")},
    ))
    fig.update_layout(height=280, template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
    return fig


def _plot_radar(result: SportsHoraryResult) -> go.Figure:
    labels = ["Strength", "InjurySafety", "UpsetControl", "Flow", "Trend"]
    p1 = result.match_analysis.winner_probability[result.team1]
    p2 = result.match_analysis.winner_probability[result.team2]
    upset = result.advanced.upset_indicator
    t1 = [
        min(1.0, result.match_analysis.team1_strength / 8.0),
        1.0 - result.advanced.injury_risk_team1,
        1.0 - upset * 0.6,
        p1,
        0.55,
    ]
    t2 = [
        min(1.0, result.match_analysis.team2_strength / 8.0),
        1.0 - result.advanced.injury_risk_team2,
        1.0 - upset * 0.4,
        p2,
        0.52,
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=t1, theta=labels, fill="toself", name=result.team1, line=dict(color="#2ecc71")))
    fig.add_trace(go.Scatterpolar(r=t2, theta=labels, fill="toself", name=result.team2, line=dict(color="#3498db")))
    fig.update_layout(
        template="plotly_dark",
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        height=360,
        margin=dict(l=20, r=20, t=40, b=20),
        title=auto_cn("主客隊雷達對照", "Team Radar Comparison"),
    )
    return fig


def _render_dashboard(result: SportsHoraryResult, lang: str) -> None:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(result.team1, f"{result.match_analysis.winner_probability[result.team1]:.1%}")
    with c2:
        st.metric(result.team2, f"{result.match_analysis.winner_probability[result.team2]:.1%}")
    with c3:
        st.metric(auto_cn("逆轉指標", "Upset"), f"{result.advanced.upset_indicator:.1%}")

    st.plotly_chart(_plot_win_probability(result), use_container_width=True)
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(_plot_confidence_gauge(result), use_container_width=True)
    with g2:
        st.plotly_chart(_plot_radar(result), use_container_width=True)

    with st.expander(auto_cn("核心證據（Top Testimonies）", "Top Testimonies"), expanded=True):
        for t in result.match_analysis.key_testimonies[:10]:
            st.write(f"- {(t.description_zh if lang == 'zh' else t.description_en)}")


def _render_historical_cases() -> None:
    st.markdown('<div class="sports-card">', unsafe_allow_html=True)
    st.subheader(auto_cn("歷史賽例展示", "Historical Cases"))
    for row in _HISTORICAL_CASES:
        st.write(f"- **{row['sport']}** · {row['match']} — {row['note']}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_streamlit(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    **kwargs,
) -> None:
    st.markdown(_SPORTS_CSS, unsafe_allow_html=True)
    lang = get_lang()

    st.markdown(
        '<div class="sports-header">'
        f'<h2>{auto_cn("🏟️ Sports Astrology 運動占星", "🏟️ Sports Astrology")}</h2>'
        f'<p>{auto_cn("Frawley 為主、Vedic 輔助，輸出概率式結論與風險提示。", "Frawley-led with Vedic support, producing probabilistic output and risk cues.")}</p>'
        "</div>",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(auto_cn("### 運動占星 / Sports Astrology", "### Sports Astrology"))
        pick = st.selectbox(
            auto_cn("熱門賽事快速查詢", "Popular Match Lookup"),
            options=[""] + [x["label"] for x in _POPULAR_MATCHES],
        )
        if pick:
            selected = next((x for x in _POPULAR_MATCHES if x["label"] == pick), None)
            if selected:
                st.session_state["sports_match_name"] = selected["match"]
                st.session_state["sports_team1"] = selected["team1"]
                st.session_state["sports_team2"] = selected["team2"]
        analysis_mode = st.radio(
            auto_cn("分析模式", "Mode"),
            options=["horary", "event"],
            format_func=lambda x: auto_cn("Horary 問卜", "Horary") if x == "horary" else auto_cn("Event Chart", "Event Chart"),
            key="sports_analysis_mode",
        )

    c1, c2, c3 = st.columns(3)
    with c1:
        match_name = st.text_input(auto_cn("比賽名稱", "Match Name"), key="sports_match_name", value=st.session_state.get("sports_match_name", "EPL Match"))
        team1 = st.text_input(auto_cn("主隊 / Team 1", "Home / Team 1"), key="sports_team1", value=st.session_state.get("sports_team1", "Team A"))
    with c2:
        team2 = st.text_input(auto_cn("客隊 / Team 2", "Away / Team 2"), key="sports_team2", value=st.session_state.get("sports_team2", "Team B"))
        preferred = st.selectbox(
            auto_cn("喜好方（可選）", "Preferred Side"),
            options=["", team1, team2],
            format_func=lambda x: auto_cn("無", "None") if x == "" else x,
        )
    with c3:
        question = st.text_input(
            auto_cn("提問內容（可選）", "Question (Optional)"),
            value="Who is more likely to win this match?",
        )
        st.caption(auto_cn("主判準：1宮 vs 7宮；輸出為概率而非保證。", "Core rule: 1st vs 7th; probabilistic, not deterministic."))

    if st.button(auto_cn("開始分析", "Run Analysis"), type="primary"):
        result = analyze_sports_horary(
            match_name=match_name,
            team1=team1,
            team2=team2,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            preferred_team=preferred or None,
            question_text=question if analysis_mode == "horary" else f"Event chart mode: {question}",
        )
        st.session_state["sports_last_result"] = result

    result: Optional[SportsHoraryResult] = st.session_state.get("sports_last_result")
    if not result:
        _render_historical_cases()
        st.info(auto_cn("請先輸入比賽資訊並執行分析。", "Please input match data and run analysis first."))
        return

    tabs = st.tabs([
        auto_cn("Horary 判斷", "Horary"),
        auto_cn("Event Chart", "Event Chart"),
        auto_cn("視覺化", "Visuals"),
        auto_cn("跨體系對照", "Cross-system"),
        auto_cn("PDF 報告", "PDF Report"),
    ])

    with tabs[0]:
        col_chart, col_text = st.columns([3, 2])
        with col_chart:
            svg = render_western_horary_svg(result.chart)
            wrapped = build_cultural_svg(svg, "tab_sports_astrology", title=auto_cn("雙方對照 Horary 星盤", "Dual Horary Chart"))
            st.markdown(wrapped, unsafe_allow_html=True)
        with col_text:
            st.markdown('<div class="sports-card">', unsafe_allow_html=True)
            st.subheader(auto_cn("文字結論", "Conclusion"))
            st.write(result.match_analysis.explanation)
            st.caption(auto_cn("此區為 Frawley 傳統主判斷。", "This panel is Frawley-primary judgment."))
            st.markdown("</div>", unsafe_allow_html=True)

    with tabs[1]:
        st.markdown('<div class="sports-card">', unsafe_allow_html=True)
        st.subheader(auto_cn("事件時間軸（前後關鍵 transit）", "Event Timeline (key transits)"))
        for item in result.timeline_transits:
            st.write(f"- **{item['label']}**: {item['time']}")
        st.markdown("</div>", unsafe_allow_html=True)
        with st.expander(auto_cn("Event + Team Natal 對照", "Event + Team Natal Comparison"), expanded=True):
            dt = datetime(year, month, day, hour, minute)
            rows = analyze_event_chart_with_team_natal(
                event_year=dt.year,
                event_month=dt.month,
                event_day=dt.day,
                event_hour=dt.hour,
                event_minute=dt.minute,
                timezone=timezone,
                latitude=latitude,
                longitude=longitude,
                location_name=location_name,
                teams=[
                    TeamNatalInput(team_name=result.team1, year=2000, month=1, day=1),
                    TeamNatalInput(team_name=result.team2, year=2001, month=1, day=1),
                ],
            )
            for row in rows:
                st.write(f"- {row.team}: **{row.synastry_score:+.2f}** · {', '.join(row.key_aspects[:3]) or '—'}")

    with tabs[2]:
        _render_dashboard(result, lang)

    with tabs[3]:
        st.markdown('<div class="sports-card">', unsafe_allow_html=True)
        st.subheader(auto_cn("跨體系對照：Frawley × Vedic × Hellenistic/ZR", "Cross-system Lens"))
        st.write(auto_cn("Frawley 為主判斷，Vedic 作為輔助校驗；可進一步串接紫微大限與 Zodiacal Releasing 進行時序對照。", "Frawley remains primary; Vedic is secondary confirmation. You can extend with Ziwei major periods and Zodiacal Releasing timing overlays."))
        st.code(build_ai_interpretation_prompt(result, lang=lang), language="text")
        st.markdown("</div>", unsafe_allow_html=True)
        _render_historical_cases()

    with tabs[4]:
        st.markdown('<div class="sports-card">', unsafe_allow_html=True)
        st.subheader(auto_cn("PDF 收藏版內容預覽", "Collector PDF Preview"))
        st.write(auto_cn("建議 PDF 章節：雙星盤、核心證據、概率儀表、關鍵時間點、結論與免責。", "Suggested PDF sections: dual charts, key testimonies, probability gauges, timing checkpoints, conclusion, disclaimer."))
        st.text_area(
            auto_cn("可匯出文字摘要", "Exportable Summary"),
            value=(
                f"{result.match_name}\n"
                f"{result.team1} vs {result.team2}\n"
                f"{result.match_analysis.explanation}\n"
                f"Upset: {result.advanced.upset_indicator:.1%}\n"
            ),
            height=180,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="sports-disclaimer">'
        + auto_cn(
            "⚠️ 本功能僅提供概率式占星判斷，不構成保證、投資或投注建議。請務必結合傷病資訊、戰術分析與資金管理。",
            "⚠️ This feature provides probabilistic astrology only and is not guaranteed betting or investment advice. Always combine with injury news, tactics, and bankroll management.",
        )
        + "</div>",
        unsafe_allow_html=True,
    )
