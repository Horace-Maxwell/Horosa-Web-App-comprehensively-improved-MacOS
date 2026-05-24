from __future__ import annotations

from pathlib import Path
from typing import Any

import plotly.graph_objects as go
import streamlit as st


@st.cache_data(show_spinner=False)
def _load_armenian_css() -> str:
    css_path = Path(__file__).resolve().parents[1] / "styles" / "armenian_theme.css"
    if css_path.exists():
        return css_path.read_text(encoding="utf-8")
    return ""


def build_armenian_wheel(chart: Any, mode: str = "Ancient Map (Sevsar)") -> go.Figure:
    signs = chart.metadata.get("signs") or []
    if not signs:
        signs = [
            {"hy": "Խոյ"}, {"hy": "Ցուլ"}, {"hy": "Երկվորյակ"}, {"hy": "Խեցգետին"},
            {"hy": "Առյուծ"}, {"hy": "Կույս"}, {"hy": "Կշեռք"}, {"hy": "Կարիճ"},
            {"hy": "Աղեղնավոր"}, {"hy": "Այծեղջյուր"}, {"hy": "Ջրհոս"}, {"hy": "Ձկներ"},
        ]

    bg = "#1d130f" if "Ancient" in mode else "#2a1a14"
    fig = go.Figure()

    for i, s in enumerate(signs):
        center = i * 30 + 15
        fig.add_trace(
            go.Scatterpolar(
                r=[1.02],
                theta=[center],
                mode="text",
                text=[s.get("hy", "")],
                textfont=dict(color="#d4af6a", size=13),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    for p in getattr(chart, "planets", []):
        fig.add_trace(
            go.Scatterpolar(
                r=[0.72],
                theta=[float(p.longitude)],
                mode="markers+text",
                marker=dict(size=8, color="#f3e6c8", line=dict(color="#8a5a2a", width=1)),
                text=[p.name.split(" ")[0]],
                textposition="top center",
                textfont=dict(color="#f3e6c8", size=10),
                name=p.name,
                hovertemplate=(
                    f"<b>{p.name}</b><br>{p.sign_hy} {p.sign_degree:.2f}°"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1.15]),
            angularaxis=dict(direction="clockwise", rotation=90, showticklabels=False, ticks=""),
            bgcolor=bg,
        ),
        paper_bgcolor=bg,
        plot_bgcolor=bg,
        margin=dict(l=10, r=10, t=10, b=10),
        height=560,
        showlegend=False,
    )
    return fig


def render_armenian_page(chart: Any, after_chart_hook=None):
    css = _load_armenian_css()
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    st.markdown('<div class="arm-wrap">', unsafe_allow_html=True)
    st.subheader("✶ Armenian Astrology — Հայկական Աստղագուշակություն")

    mode = st.segmented_control(
        "Visual Mode",
        options=["Ancient Map (Sevsar)", "Modern Manuscript"],
        default="Ancient Map (Sevsar)",
    )

    c1, c2, c3 = st.columns([1, 1, 1])
    c1.metric("Haykian Year", chart.haykian_date.get("hayk_year", "-"))
    c2.metric("Orion/Hayk Visible", "Yes" if chart.haykian_date.get("orion_hayk_visible") else "No")
    c3.metric("Zodiac Basis", chart.zodiac_mode)

    tabs = st.tabs([
        "🜂 Wheel",
        "🪐 Planets",
        "📜 Ancestral Reading",
        "🔭 Transit/Progression/Return",
        "🧭 Cultural Notes",
    ])

    with tabs[0]:
        klass = "arm-map-mode" if "Ancient" in mode else "arm-modern-mode"
        st.markdown(f'<div class="{klass}">', unsafe_allow_html=True)
        st.plotly_chart(build_armenian_wheel(chart, mode=mode), width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    with tabs[1]:
        st.dataframe([
            {
                "Planet": p.name,
                "Longitude": round(float(p.longitude), 4),
                "Armenian Sign": p.sign_hy,
                "Translit": p.sign_translit,
                "Degree": round(float(p.sign_degree), 2),
                "House": p.house,
                "R": "R" if p.retrograde else "",
            }
            for p in chart.planets
        ], width="stretch")

    with tabs[2]:
        chips = " ".join([f'<span class="arm-chip">{k}</span>' for k in chart.ancestral_keywords])
        st.markdown(chips or "—", unsafe_allow_html=True)
        st.caption(
            "These keys are the recommended structured fields to pass into Cerebras/Ollama "
            "for Armenian-style readings and cross-system comparison."
        )
        st.caption("Prompt payload keys: natal_summary, transit_hits, progression_hits, solar_return, haykian_date, ancestral_keywords, comparison_targets")

    with tabs[3]:
        st.info("Transit / Progression / Solar Return engines are available through ArmenianChart API.")

    with tabs[4]:
        with st.expander("📚 Historical Sources", expanded=False):
            for src in chart.metadata.get("cultural_sources", []):
                st.markdown(f"- [{src.get('title', '')}]({src.get('url', '')}) · `{src.get('grade', 'reference')}`")

    st.markdown("</div>", unsafe_allow_html=True)
    if after_chart_hook:
        after_chart_hook()
