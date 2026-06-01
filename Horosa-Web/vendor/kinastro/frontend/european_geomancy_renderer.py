"""Streamlit renderer for European Geomancy."""

from __future__ import annotations

from typing import Callable, Optional

import streamlit as st
import streamlit.components.v1 as components

from astro.european_geomancy import (
    all_figures,
    astrology_bridge_interpretation,
    build_ai_prompt,
    generate_reading,
    render_figure_svg,
    render_house_chart_svg,
    render_shield_chart_svg,
    structured_interpretation,
)


def _theme_css() -> str:
    return """
<style>
.eg-header {background:linear-gradient(135deg,#0B0F18 0%,#1A1025 55%,#0B0F18 100%);border:1px solid #886838;border-radius:10px;padding:16px 18px;margin-bottom:14px;}
.eg-title {color:#E3C787;font-size:1.45rem;font-family:serif;font-weight:700;margin:0;}
.eg-sub {color:#AAB6CC;font-size:0.9rem;margin:4px 0 0 0;}
.eg-card {background:#101722;border:1px solid #32445e;border-radius:8px;padding:10px;min-height:108px;}
.eg-k {color:#E3C787;font-weight:600;font-size:0.95rem;}
.eg-v {color:#B8C6DD;font-size:0.9rem;}
</style>
"""


def _render_figure_catalog() -> None:
    figures = list(all_figures())
    st.markdown("### 16 Geomantic Figures")

    for i in range(0, 16, 4):
        cols = st.columns(4)
        for j, fig in enumerate(figures[i:i + 4]):
            with cols[j]:
                components.html(render_figure_svg(fig, width=100, with_title=True), height=132, scrolling=False)
                with st.expander(f"{fig.latin} · {fig.zh}"):
                    st.write(f"**Element**: {fig.element}")
                    st.write(f"**Planet**: {fig.planet}")
                    st.write(f"**Zodiac**: {fig.zodiac}")
                    st.write(f"**Positive**: {', '.join(fig.positive_keywords)}")
                    st.write(f"**Negative**: {', '.join(fig.negative_keywords)}")
                    st.write(f"**Historical**: {fig.historical_meaning}")


def render_european_geomancy(after_chart_hook: Optional[Callable[[], None]] = None) -> None:
    """Render the full European Geomancy page."""
    st.markdown(_theme_css(), unsafe_allow_html=True)
    st.markdown(
        '<div class="eg-header"><p class="eg-title">🜃 European Geomancy</p>'
        '<p class="eg-sub">Renaissance geomancy with Shield Chart, House Chart, and astrological synthesis.</p></div>',
        unsafe_allow_html=True,
    )

    with st.form("eg_form"):
        question = st.text_area(
            "問題 / Question",
            placeholder="例如：我今年事業能否突破？ / e.g. How will my career develop this year?",
            height=90,
        )
        c1, c2 = st.columns(2)
        with c1:
            question_type = st.selectbox(
                "問題類型 / Question Type",
                options=["general", "wealth", "relationship", "career", "travel", "health"],
                format_func=lambda x: {
                    "general": "General",
                    "wealth": "Wealth",
                    "relationship": "Relationship",
                    "career": "Career",
                    "travel": "Travel",
                    "health": "Health",
                }[x],
            )
        with c2:
            cast_method = st.selectbox(
                "起卦方式 / Casting Method",
                options=["traditional", "coin", "number", "manual"],
                format_func=lambda x: {
                    "traditional": "Traditional dots",
                    "coin": "Coin toss",
                    "number": "Random numbers",
                    "manual": "Manual input",
                }[x],
            )

        manual_input = None
        if cast_method == "manual":
            manual_input = st.text_area(
                "手動輸入（4 行，每行 4 個整數）",
                value="1 3 5 7\n2 4 6 8\n1 2 3 4\n9 9 9 9",
                height=120,
            )

        submitted = st.form_submit_button("🔮 Cast European Geomancy")

    if submitted:
        try:
            reading = generate_reading(
                question=question,
                question_type=question_type,
                cast_method=cast_method,
                manual_input=manual_input,
            )
            st.session_state["_eg_reading"] = reading
            history = st.session_state.get("_eg_history", [])
            history.insert(0, reading.to_json())
            st.session_state["_eg_history"] = history[:30]
        except Exception as exc:
            st.error(f"Casting failed: {exc}")

    reading = st.session_state.get("_eg_reading")
    if not reading:
        st.info("請輸入問題並起卦。 / Enter a question and cast a chart.")
        return

    tabs = st.tabs(["🔹 Figures", "🛡 Shield Chart", "🏛 House Chart", "📜 Interpretation", "🕘 History"])

    with tabs[0]:
        _render_figure_catalog()

    with tabs[1]:
        st.markdown("### Shield Chart")
        components.html(render_shield_chart_svg(reading.shield), height=760, scrolling=True)

    with tabs[2]:
        st.markdown("### House Chart (12 Houses)")
        components.html(render_house_chart_svg(reading.houses), height=900, scrolling=True)

    with tabs[3]:
        st.markdown("### Structured Interpretation")
        interp = structured_interpretation(reading, lang="zh")
        for key, title in [
            ("current_state", "問卜者現況"),
            ("development", "事情發展"),
            ("aids_obstacles", "助力與阻力"),
            ("outcome", "最終結果"),
        ]:
            st.markdown(f'<div class="eg-card"><div class="eg-k">{title}</div><div class="eg-v">{interp[key]}</div></div>', unsafe_allow_html=True)
            st.write("")
        st.markdown("### Astrology Bridge")
        st.info(astrology_bridge_interpretation(reading, lang="zh"))
        with st.expander("AI 深度報告上下文 / AI Prompt Context"):
            st.code(build_ai_prompt(reading, lang="zh"), language="markdown")

    with tabs[4]:
        st.markdown("### Reading History")
        history = st.session_state.get("_eg_history", [])
        if not history:
            st.info("目前尚無歷史記錄。")
        for idx, item in enumerate(history, 1):
            st.markdown(
                f"**#{idx}** {item['created_at_utc']} · {item['question']}  \n"
                f"Method: `{item['cast_method']}` · Judge: `{item['judge']}` · Reconciler: `{item['reconciler']}`"
            )

    if after_chart_hook:
        after_chart_hook()
