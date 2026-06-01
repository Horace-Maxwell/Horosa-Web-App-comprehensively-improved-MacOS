"""
astro/andean/renderer.py — Streamlit renderer for Andean / Inca Astrology
=========================================================================

Renders the complete Andean chart UI including:
  • Mayu (Milky Way) dark-sky interactive Plotly chart
  • Yana Phuyu (Dark Constellation) panel with myth & omen text
  • Planets table with galactic coordinates
  • Bright markers panel (Pleiades/Collca, Chakana/Southern Cross, etc.)
  • Birth guardian summary
  • Sub-tabs: Sky Chart | Planets | Constellations | Markers

IMPORTANT: Streamlit is imported only inside the function bodies, per
CONTRIBUTING.md convention, so this module can be imported in unit-test
contexts without Streamlit being present.
"""

from __future__ import annotations

from typing import Any, Callable, Optional


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _t(key: str, lang: str = "zh") -> str:
    """Simple translation helper — returns Quechua label where applicable."""
    return key


def _chakana_svg_watermark(gold: str = "#C8A24A", opacity: float = 0.10) -> str:
    """Return a Chakana (Andean cross) SVG string for use as a watermark."""
    # Chakana proportions: outer 12-step cross with central hole
    return f"""<svg viewBox="0 0 120 120" width="120" height="120"
         xmlns="http://www.w3.org/2000/svg" style="display:inline-block">
  <g fill="{gold}" opacity="{opacity}">
    <!-- Chakana cross — simplified 12-pointed stepped form -->
    <path d="
      M46,0 h28 v20 h20 v28 h20 v28 h-20 v28 h-28 v-20 h-28 v-28 h-20 v-28 h20 z
    " transform="translate(3,3) scale(0.95)"/>
    <!-- Central diamond -->
    <rect x="48" y="48" width="24" height="24" rx="12" fill="#0B0F1E" opacity="1"/>
  </g>
</svg>"""


def _collca_badge_html(phase: str, phase_zh: str, gold: str = "#C8A24A") -> str:
    icon = {"combust": "🌑", "heliacal_rising": "🌅", "visible": "✨",
            "below_horizon": "🌙"}.get(phase, "⭐")
    bg = "#1A2A1A" if phase == "visible" else "#2A1A0A"
    return (
        f'<div style="background:{bg};border:1px solid {gold};'
        f'border-radius:8px;padding:8px 14px;display:inline-block;'
        f'font-size:13px;color:#EDD88A">'
        f'{icon} <b>Collca (昴宿)</b>: {phase_zh}</div>'
    )


def _build_mayu_figure(chart: Any) -> Any:
    """Build the Plotly dark-sky figure showing Mayu and dark constellations."""
    import plotly.graph_objects as go
    from .constants import ANDEAN_THEME

    fig = go.Figure()

    # ── Milky Way band ──
    fig.add_trace(go.Scattergl(
        x=chart.mayu_longitudes,
        y=chart.mayu_latitudes,
        mode="markers",
        marker=dict(size=1.5, color=ANDEAN_THEME["milky"], opacity=0.22),
        name="Mayu (天河)",
        hoverinfo="skip",
    ))

    # ── Dark constellations (dormant) ──
    for dc in chart.dark_constellations:
        if dc.is_alive:
            continue
        color = ANDEAN_THEME["dormant"]
        poly_l = dc.poly_l + [dc.poly_l[0]]
        poly_b = dc.poly_b + [dc.poly_b[0]]
        fig.add_trace(go.Scatter(
            x=poly_l, y=poly_b,
            fill="toself",
            fillcolor="rgba(90,90,122,0.15)",
            line=dict(color=color, width=1, dash="dot"),
            name=f"{dc.name_qu} (伏藏)",
            hovertemplate=(
                f"<b>{dc.name_qu}</b> ({dc.name_zh})<br>"
                f"高度: {dc.altitude:.1f}°<br>"
                f"狀態: 地平線下或被太陽遮蔽<extra></extra>"
            ),
        ))

    # ── Dark constellations (alive) ──
    for dc in chart.dark_constellations:
        if not dc.is_alive:
            continue
        poly_l = dc.poly_l + [dc.poly_l[0]]
        poly_b = dc.poly_b + [dc.poly_b[0]]
        fig.add_trace(go.Scatter(
            x=poly_l, y=poly_b,
            fill="toself",
            fillcolor="rgba(200,162,74,0.18)",
            line=dict(color=ANDEAN_THEME["gold"], width=2),
            name=f"⚡ {dc.name_qu}",
            hovertemplate=(
                f"<b>{dc.name_qu}</b> — {dc.name_zh}<br>"
                f"高度: {dc.altitude:.1f}° | 離日角: {dc.angular_from_sun:.1f}°<br>"
                f"{dc.agro_omen_zh}<extra></extra>"
            ),
        ))

    # ── Bright markers ──
    for bm in chart.bright_markers:
        if bm["galactic_l"] == 0.0 and bm["galactic_b"] == 0.0:
            continue
        marker_color = ANDEAN_THEME["gold"] if bm["is_visible"] else ANDEAN_THEME["dormant"]
        fig.add_trace(go.Scatter(
            x=[bm["galactic_l"]], y=[bm["galactic_b"]],
            mode="markers+text",
            marker=dict(size=10, color=marker_color, symbol="star"),
            text=[bm["name_qu"]],
            textposition="top right",
            textfont=dict(size=9, color=marker_color),
            name=bm["name_qu"],
            hovertemplate=(
                f"<b>{bm['name_qu']}</b> ({bm['name_zh']})<br>"
                f"l={bm['galactic_l']:.1f}° b={bm['galactic_b']:.1f}°<br>"
                f"高度: {bm['altitude']:.1f}°<extra></extra>"
            ),
        ))

    # ── Sun marker ──
    fig.add_trace(go.Scatter(
        x=[chart.sun_galactic_l], y=[chart.sun_galactic_b],
        mode="markers+text",
        marker=dict(size=14, color=ANDEAN_THEME["sun"], symbol="circle"),
        text=["☀ 太陽"],
        textposition="top right",
        textfont=dict(size=9, color=ANDEAN_THEME["sun"]),
        name="太陽 Sun",
        hovertemplate=(
            f"<b>Sun</b><br>l={chart.sun_galactic_l:.1f}°, b={chart.sun_galactic_b:.1f}°"
            "<extra></extra>"
        ),
    ))

    # ── Moon marker ──
    fig.add_trace(go.Scatter(
        x=[chart.moon_galactic_l], y=[chart.moon_galactic_b],
        mode="markers+text",
        marker=dict(size=10, color=ANDEAN_THEME["moon"], symbol="circle"),
        text=["☽ 月亮"],
        textposition="bottom right",
        textfont=dict(size=9, color=ANDEAN_THEME["moon"]),
        name="月亮 Moon",
        hovertemplate=(
            f"<b>Moon</b><br>l={chart.moon_galactic_l:.1f}°, b={chart.moon_galactic_b:.1f}°"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        paper_bgcolor=ANDEAN_THEME["bg"],
        plot_bgcolor=ANDEAN_THEME["bg"],
        font=dict(color=ANDEAN_THEME["text"], family="serif"),
        title=dict(
            text="🌌 Mayu — 天河暗星宿天空圖",
            font=dict(color=ANDEAN_THEME["header"], size=16),
            x=0.5,
        ),
        xaxis=dict(
            title="銀河經度 Galactic Longitude l°",
            range=[0, 360],
            gridcolor="#1F2940",
            tickcolor=ANDEAN_THEME["gold"],
            color=ANDEAN_THEME["text"],
        ),
        yaxis=dict(
            title="銀河緯度 Galactic Latitude b°",
            range=[-30, 30],
            gridcolor="#1F2940",
            tickcolor=ANDEAN_THEME["gold"],
            color=ANDEAN_THEME["text"],
        ),
        legend=dict(
            orientation="h",
            bgcolor="rgba(11,15,30,0.7)",
            bordercolor=ANDEAN_THEME["gold"],
            borderwidth=1,
            font=dict(size=10),
        ),
        margin=dict(l=50, r=20, t=50, b=50),
        height=480,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Sub-tab renderers
# ─────────────────────────────────────────────────────────────────────────────

def _render_sky_tab(st: Any, chart: Any) -> None:
    """Render the Mayu sky chart and dark constellation overview."""
    from .constants import ANDEAN_THEME

    # Chakana watermark strip
    st.markdown(
        '<div style="text-align:center;opacity:0.15">'
        + _chakana_svg_watermark(ANDEAN_THEME["gold"], 1.0)
        + '</div>',
        unsafe_allow_html=True,
    )

    # Collca (Pleiades) phase badge
    st.markdown(
        _collca_badge_html(chart.collca_heliacal_phase, chart.collca_heliacal_phase_zh),
        unsafe_allow_html=True,
    )
    st.markdown("")

    # Main sky figure
    st.plotly_chart(_build_mayu_figure(chart), width="stretch")

    # Stats row
    alive_count = len(chart.dark_constellations_alive)
    total_count = len(chart.dark_constellations)
    col1, col2, col3 = st.columns(3)
    col1.metric("⚡ 活躍暗星宿 Active", f"{alive_count} / {total_count}")
    col2.metric("☀ 太陽銀河經度", f"l = {chart.sun_galactic_l:.1f}°")
    col3.metric("☽ 月亮銀河緯度", f"b = {chart.moon_galactic_b:.1f}°")


def _render_constellations_tab(st: Any, chart: Any, lang: str = "zh") -> None:
    """Render dark constellation myth & omen panel."""
    from .constants import ANDEAN_THEME

    alive = chart.dark_constellations_alive
    dormant = [d for d in chart.dark_constellations if not d.is_alive]

    if alive:
        st.markdown(
            f'<h4 style="color:{ANDEAN_THEME["gold"]}">⚡ 活躍暗星宿（出生時可見）</h4>',
            unsafe_allow_html=True,
        )
        for dc in alive:
            with st.expander(f"⚡ {dc.name_qu} — {dc.name_zh}", expanded=True):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Quechua**: {dc.name_qu}")
                    st.markdown(f"**高度**: {dc.altitude:.1f}°")
                    st.markdown(f"**離日角**: {dc.angular_from_sun:.1f}°")
                    st.markdown("---")
                    st.markdown(f"**神話**\n\n{dc.myth_zh}")
                with c2:
                    st.markdown(f"**農業預兆**\n\n{dc.agro_omen_zh}")
                    if dc.cross_refs:
                        st.markdown("**跨文化對應**")
                        for k, v in dc.cross_refs.items():
                            st.caption(f"• {k}: {v}")

    if dormant:
        st.markdown("---")
        st.markdown(
            f'<h5 style="color:{ANDEAN_THEME["dormant"]}">🌙 伏藏暗星宿（地平線下或被太陽遮蔽）</h5>',
            unsafe_allow_html=True,
        )
        for dc in dormant:
            with st.expander(f"🌙 {dc.name_qu} — {dc.name_zh}", expanded=False):
                st.caption(f"高度 {dc.altitude:.1f}° | 離日角 {dc.angular_from_sun:.1f}°")
                st.markdown(f"**意義**: {dc.meaning_zh}")
                st.caption(dc.agro_omen_zh)


def _render_planets_tab(st: Any, chart: Any) -> None:
    """Render planetary positions with galactic coordinates."""
    import pandas as pd

    rows = []
    for p in chart.planets:
        rows.append({
            "行星": f"{p.name_zh} ({p.name})",
            "黃道度數": f"{p.sign} {p.sign_degree:.1f}°",
            "逆行": "♺" if p.retrograde else "",
            "RA": f"{p.ra:.1f}°",
            "Dec": f"{p.dec:.1f}°",
            "銀經 l": f"{p.galactic_l:.1f}°",
            "銀緯 b": f"{p.galactic_b:.1f}°",
            "地平高度": f"{p.altitude:.1f}°",
            "最近暗星宿": p.nearest_dark_constellation,
            "角距": f"{p.angle_to_dark_constellation:.1f}°",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)

    st.caption(
        "銀經 l = 銀河經度（Galactic Longitude）；"
        "銀緯 b = 銀河緯度（Galactic Latitude）；"
        "地平高度 > 5° 且離太陽 > 12° 者為可見。"
    )


def _render_markers_tab(st: Any, chart: Any) -> None:
    """Render bright Andean stellar markers (Pleiades, Chakana, etc.)."""
    from .constants import ANDEAN_THEME

    for bm in chart.bright_markers:
        vis = "✨ 可見" if bm["is_visible"] else "🌙 不可見"
        color = ANDEAN_THEME["gold"] if bm["is_visible"] else ANDEAN_THEME["dormant"]
        with st.expander(f'{vis} {bm["name_qu"]} — {bm["name_zh"]}', expanded=bm["is_visible"]):
            st.markdown(f'<span style="color:{color}"><b>{bm["name_en"]}</b></span>',
                        unsafe_allow_html=True)
            if bm["galactic_l"] != 0.0:
                st.markdown(
                    f"**銀河座標**: l = {bm['galactic_l']:.1f}°, b = {bm['galactic_b']:.1f}°"
                )
                st.markdown(f"**地平高度**: {bm['altitude']:.1f}°")
            st.markdown(f"**文化意義**: {bm['meaning_zh']}")

    # Collca special phase box
    st.info(
        f"**Collca（昴宿星團 / Pleiades）相位**: {chart.collca_heliacal_phase_zh}\n\n"
        "昴宿的偕日出是印加曆法最重要的天文事件，標誌農業年的開始與豐收預測。"
    )


def _render_guardian_box(st: Any, chart: Any) -> None:
    """Render the birth animal guardian box at the top."""
    from .constants import ANDEAN_THEME

    st.markdown(
        f"""<div style="background:{ANDEAN_THEME['bg_card']};
            border:2px solid {ANDEAN_THEME['gold']};
            border-radius:12px;padding:14px 20px;margin-bottom:14px">
        <span style="font-size:18px;color:{ANDEAN_THEME['header']}">
        ⛰️ 出生守護靈（Andean Birth Guardian）
        </span><br>
        <span style="font-size:22px;color:{ANDEAN_THEME['gold']};font-weight:bold">
        {chart.birth_guardian_qu}
        </span>
        <span style="color:{ANDEAN_THEME['text']};font-size:15px">
        &nbsp;—&nbsp;{chart.birth_guardian_zh} / {chart.birth_guardian_en}
        </span><br>
        <span style="font-size:11px;color:#888">
        {chart.year}-{chart.month:02d}-{chart.day:02d}
        &nbsp;|&nbsp;{chart.location_name}
        &nbsp;|&nbsp;lat {chart.latitude:.2f}°, lon {chart.longitude:.2f}°
        </span>
        </div>""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main render entry point
# ─────────────────────────────────────────────────────────────────────────────

def render_streamlit(
    chart: Any,
    after_chart_hook: Optional[Callable[[], None]] = None,
    lang: str = "zh",
) -> None:
    """Render the complete Andean astrology chart in Streamlit.

    Args:
        chart:             AndeanChart dataclass from compute_andean_chart().
        after_chart_hook:  Optional callback rendered after the chart header
                           (used to inject the AI analysis button from app.py).
        lang:              Display language key ("zh" or "en").
    """
    import streamlit as st

    # Birth guardian header
    _render_guardian_box(st, chart)

    # AI button hook
    if after_chart_hook is not None:
        after_chart_hook()

    # Sub-tabs
    tab_sky, tab_constellations, tab_planets, tab_markers = st.tabs([
        "🌌 天河星圖",
        "🦙 暗星宿",
        "🪐 行星",
        "⭐ 明星標記",
    ])

    with tab_sky:
        _render_sky_tab(st, chart)

    with tab_constellations:
        _render_constellations_tab(st, chart, lang)

    with tab_planets:
        _render_planets_tab(st, chart)

    with tab_markers:
        _render_markers_tab(st, chart)
