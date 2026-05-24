"""Streamlit renderer for Bahre Hasab (traditional Ethiopian liturgical calendar)."""

from __future__ import annotations

from datetime import date
from typing import Callable, Optional

import plotly.graph_objects as go
import streamlit as st

from astro.bahre_hasab.engine import analyze_bahre_hasab_date, annual_bahre_hasab_overview
from astro.bahre_hasab.interpretations import TRADITION_NOTE_EN, TRADITION_NOTE_ZH
from astro.i18n import auto_cn, get_lang


def _traditional_table_style() -> str:
    return """
    <style>
      .bh-panel {background: linear-gradient(145deg,#111827,#1f2937); border:1px solid #b08d57; border-radius:12px; padding:14px; color:#f3e8c8; margin-bottom:12px;}
      .bh-title {font-size:1.05rem; font-weight:700; color:#eab308; margin-bottom:8px;}
      .bh-sub {opacity:0.9; font-size:0.92rem;}
    </style>
    """


def render_bahre_hasab_tab(*, calc_params: dict, after_chart_hook: Optional[Callable[[], None]] = None) -> None:
    st.markdown(_traditional_table_style(), unsafe_allow_html=True)

    default_date = date(
        int(calc_params.get("year", date.today().year)),
        int(calc_params.get("month", date.today().month)),
        int(calc_params.get("day", date.today().day)),
    )

    c1, c2 = st.columns([2, 1])
    with c1:
        selected = st.date_input("Gregorian Date", value=default_date, key="bahre_hasab_date_input")
    with c2:
        overview_year = st.number_input("Ethiopian Year", min_value=1, max_value=9999, value=2017, step=1)

    analysis = analyze_bahre_hasab_date(selected)
    overview = annual_bahre_hasab_overview(int(overview_year))

    st.markdown(
        f"<div class='bh-panel'><div class='bh-title'>ባሕረ ሐሳብ · Bahre Hasab</div>"
        f"<div class='bh-sub'>{auto_cn(TRADITION_NOTE_ZH, TRADITION_NOTE_EN)}</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"- **Gregorian**: {analysis.input_gregorian.isoformat()}\n"
        f"- **Ethiopian**: {analysis.ethiopian_date.iso()}\n"
        f"- **ዓመተ ዓለም / Amete Alem**: {analysis.bahre_year.amete_alem}\n"
        f"- **ወንበር / Wenber**: {analysis.bahre_year.wenber}\n"
        f"- **አበቅቴ / Abekte**: {analysis.bahre_year.abekte}\n"
        f"- **መጥቅዕ / Metqi**: {analysis.bahre_year.metqi}\n"
        f"- **Evangelist Cycle**: {analysis.bahre_year.evangelist}\n"
        f"- **Hasabe Kewakibit Weekday**: {analysis.kewakibit.weekday_name_geez} ({analysis.kewakibit.weekday_name_en}) {analysis.kewakibit.weekday_planet_lord}"
    )

    rows = []
    for feast in analysis.bahre_year.movable_feasts:
        rows.append(
            {
                "Feast (Ge'ez)": feast.name_geez,
                "Feast (EN)": feast.name_en,
                "Gregorian": feast.gregorian.isoformat(),
                "Ethiopian": feast.ethiopian.iso(),
                "Type": "Fast" if feast.is_fast else "Feast",
            }
        )

    st.subheader(auto_cn("年度可移動節日（依 Bahre Hasab）", "Movable Feasts (Bahre Hasab)"))
    st.dataframe(rows, width="stretch")

    x = [r["Feast (EN)"] for r in rows]
    y = [date.fromisoformat(r["Gregorian"]).timetuple().tm_yday for r in rows]
    fig = go.Figure(
        data=[
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers+text",
                text=[r["Feast (Ge'ez)"] for r in rows],
                textposition="top center",
                line=dict(color="#eab308", width=2),
                marker=dict(size=8, color="#f59e0b"),
            )
        ]
    )
    fig.update_layout(
        title=auto_cn("傳統節日年內位置圖", "Annual Position of Movable Feasts"),
        xaxis_title="Feasts",
        yaxis_title="Day of Year",
        template="plotly_dark",
        height=420,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig, width="stretch")

    st.subheader(auto_cn("Bahre Hasab 年度總覽", "Bahre Hasab Yearly Overview"))
    st.write(
        {
            "ethiopian_year": overview["ethiopian_year"],
            "amete_alem": overview["amete_alem"],
            "wenber": overview["wenber"],
            "abekte": overview["abekte"],
            "metqi": overview["metqi"],
            "evangelist": overview["evangelist"],
        }
    )

    if after_chart_hook is not None:
        after_chart_hook()

    if get_lang() in ("zh", "zh_cn"):
        st.caption("所有結果標註：依據傳統 Bahre Hasab 方法。")
    else:
        st.caption("All outputs are marked as: based on traditional Bahre Hasab method.")
