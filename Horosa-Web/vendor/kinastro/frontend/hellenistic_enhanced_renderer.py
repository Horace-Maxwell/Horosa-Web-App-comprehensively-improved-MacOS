"""frontend/hellenistic_enhanced_renderer.py
Enhanced Streamlit UI for Hellenistic Prediction Techniques:
  • Annual Profections  (年度守護星 / Lord of the Year)
  • Zodiacal Releasing  (黃道釋放, L1 / L2 / L3, Fortune & Spirit)

美學風格：深色占星質感，Plotly 互動時間軸，精緻層次呈現
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import streamlit as st
import plotly.graph_objects as go

from astro.hellenistic.profections import (
    ProfectionYear,
    compute_profections_table,
    SIGN_GLYPHS,
    PLANET_GLYPHS,
    ZODIAC_SIGNS,
)
from astro.hellenistic.zodiacal_releasing import (
    ZRPeriod,
    compute_zodiacal_releasing_full,
    flatten_periods,
    get_current_periods,
)

if TYPE_CHECKING:
    pass

# How many extra years to show ahead of the current age (one full 12-year cycle)
_PROFECTION_CYCLE_BUFFER = 13

# ─────────────────────────────────────────────────────────────
# Colour palette
# ─────────────────────────────────────────────────────────────

_PLANET_COLORS = {
    "Sun": "#EAB308",
    "Moon": "#94A3B8",
    "Mercury": "#A78BFA",
    "Venus": "#34D399",
    "Mars": "#F87171",
    "Jupiter": "#60A5FA",
    "Saturn": "#9CA3AF",
}

_ELEMENT_COLORS = {
    "fire": "#EF4444",
    "earth": "#84CC16",
    "air": "#38BDF8",
    "water": "#818CF8",
}

_ELEMENT_OF_SIGN = {
    "Aries": "fire", "Leo": "fire", "Sagittarius": "fire",
    "Taurus": "earth", "Virgo": "earth", "Capricorn": "earth",
    "Gemini": "air", "Libra": "air", "Aquarius": "air",
    "Cancer": "water", "Scorpio": "water", "Pisces": "water",
}

_CURRENT_HIGHLIGHT = "rgba(234,179,8,0.18)"
_PEAK_HIGHLIGHT = "rgba(96,165,250,0.12)"
_LOOSENING_HIGHLIGHT = "rgba(167,139,250,0.12)"


# ─────────────────────────────────────────────────────────────
# Annual Profections
# ─────────────────────────────────────────────────────────────

def render_annual_profections(
    asc_lon: float,
    birth_year: int,
    num_years: int = 24,
    lang: str = "zh",
) -> None:
    """Render the Annual Profections panel.

    渲染年度守護星面板

    Parameters
    ----------
    asc_lon:
        Natal Ascendant longitude.
    birth_year:
        Birth year (e.g. 1990).
    num_years:
        How many years to display (default 24).
    lang:
        ``"zh"`` or ``"en"``.
    """
    today = date.today()
    current_age = today.year - birth_year

    # Ensure num_years covers current age plus at least one 12-year cycle ahead
    num_years = max(num_years, current_age + _PROFECTION_CYCLE_BUFFER)
    # Round up to next multiple of 12 for clean display
    num_years = ((num_years + 11) // 12) * 12

    rows = compute_profections_table(
        asc_lon=asc_lon,
        birth_year=birth_year,
        num_years=num_years,
        current_age=current_age,
    )

    # ── Header ──────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg,
                rgba(15,10,40,0.97) 0%,
                rgba(30,15,60,0.95) 40%,
                rgba(10,25,50,0.97) 100%);
            border: 1px solid rgba(167,139,250,0.25);
            border-radius: 12px;
            padding: 1.2rem 1.6rem 1rem;
            margin-bottom: 1rem;
        ">
            <div style="
                font-family: 'Cinzel', serif;
                font-size: 1.3rem;
                font-weight: 700;
                background: linear-gradient(135deg, #EAB308 0%, #A78BFA 60%, #7DD3FC 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 0.3rem;
            ">
                🗓 Annual Profections / 年度守護星
            </div>
            <div style="color: rgba(200,185,255,0.7); font-size: 0.85rem;">
                The Ascendant advances one Whole-Sign house per year.
                每年上升點沿整個星座前進一宮，該宮主星成為本年守護星。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Current year hero card ───────────────────────────────
    current = next((r for r in rows if r.is_current), None)
    if current:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="⏳ 當前年齡 / Current Age",
                value=str(current.age),
            )
        with col2:
            st.metric(
                label="♈ 年限星座 / Profected Sign",
                value=f"{current.sign_glyph} {current.sign}",
                help=f"Chinese: {current.sign_cn} | House {current.house}",
            )
        with col3:
            planet_color = _PLANET_COLORS.get(current.lord, "#ccc")
            st.metric(
                label="⚡ 年度守護星 / Lord of the Year",
                value=f"{current.lord_glyph} {current.lord}",
                help=f"{current.lord_cn} | {current.lord_glyph}",
            )

        themes_label = "、".join(current.house_themes_zh[:4]) if lang == "zh" else ", ".join(current.house_themes_en[:4])
        st.info(
            f"🏠 第 **{current.house}** 宮主題 / House {current.house} Themes: "
            f"**{themes_label}**"
        )

    st.divider()

    # ── Plotly timeline ──────────────────────────────────────
    fig = _build_profections_chart(rows, lang)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Table ────────────────────────────────────────────────
    _render_profections_table(rows, lang)


def _build_profections_chart(rows: list[ProfectionYear], lang: str) -> go.Figure:
    """Build an interactive Plotly Gantt-style profections timeline."""
    fig = go.Figure()

    y_labels = []
    for row in rows:
        sign_color = _ELEMENT_COLORS.get(_ELEMENT_OF_SIGN.get(row.sign, "fire"), "#aaa")
        planet_color = _PLANET_COLORS.get(row.lord, "#888")
        label = f"Age {row.age} | {row.sign_glyph} {row.sign} | {row.lord_glyph} {row.lord}"
        y_labels.append(label)

        bar_color = sign_color if not row.is_current else "#EAB308"
        opacity = 0.9 if row.is_current else 0.55

        # Each profection year spans one calendar year
        x_start = row.calendar_year
        x_end = row.calendar_year + 1

        fig.add_trace(go.Bar(
            x=[x_end - x_start],
            y=[label],
            base=[x_start],
            orientation="h",
            marker=dict(
                color=bar_color,
                opacity=opacity,
                line=dict(
                    color="rgba(255,255,255,0.15)" if not row.is_current else "#EAB308",
                    width=1.5 if row.is_current else 0.5,
                ),
            ),
            showlegend=False,
            hovertemplate=(
                f"<b>Age {row.age}</b><br>"
                f"Year: {row.calendar_year}<br>"
                f"Sign: {row.sign_glyph} {row.sign} ({row.sign_cn})<br>"
                f"House: {row.house}<br>"
                f"Lord: {row.lord_glyph} {row.lord} ({row.lord_cn})<br>"
                f"Themes: {', '.join(row.house_themes_en[:3])}<br>"
                "<extra></extra>"
            ),
            name=label,
        ))

    # Current year marker
    current = next((r for r in rows if r.is_current), None)
    if current:
        fig.add_vline(
            x=current.calendar_year + (date.today().month - 1) / 12,
            line=dict(color="#EAB308", width=2, dash="dot"),
            annotation_text="Today",
            annotation_font_color="#EAB308",
        )

    fig.update_layout(
        title=dict(
            text="Annual Profections Timeline / 年度守護星時間軸",
            font=dict(color="#E2E8F0", size=14),
        ),
        barmode="overlay",
        height=max(400, len(rows) * 22 + 80),
        margin=dict(l=20, r=20, t=40, b=30),
        paper_bgcolor="rgba(15,10,40,0.97)",
        plot_bgcolor="rgba(25,15,50,0.9)",
        xaxis=dict(
            title="Year",
            color="#94A3B8",
            gridcolor="rgba(255,255,255,0.07)",
        ),
        yaxis=dict(
            color="#94A3B8",
            gridcolor="rgba(255,255,255,0.05)",
            autorange="reversed",
        ),
        font=dict(color="#CBD5E1", size=11),
    )
    return fig


def _render_profections_table(rows: list[ProfectionYear], lang: str) -> None:
    """Render the profections as a styled Streamlit table."""
    st.markdown("#### 📋 年度守護星完整列表 / Full Profections List")

    table_rows = []
    for row in rows:
        themes = "、".join(row.house_themes_zh[:3]) if lang == "zh" else ", ".join(row.house_themes_en[:3])
        marker = "⭐ 當前" if row.is_current else ""
        table_rows.append({
            "": marker,
            "歲/Age": row.age,
            "年份/Year": row.calendar_year,
            "星座/Sign": f"{row.sign_glyph} {row.sign} ({row.sign_cn})",
            "宮位/House": row.house,
            "守護星/Lord": f"{row.lord_glyph} {row.lord} ({row.lord_cn})",
            "宮位主題/Themes": themes,
        })

    st.dataframe(
        table_rows,
        use_container_width=True,
        height=min(600, len(table_rows) * 35 + 60),
    )


# ─────────────────────────────────────────────────────────────
# Zodiacal Releasing
# ─────────────────────────────────────────────────────────────

def render_zodiacal_releasing(
    fortune_lon: float,
    spirit_lon: float,
    birth_jd: float,
    target_jd: float,
    lang: str = "zh",
) -> None:
    """Render the Zodiacal Releasing panel with Fortune / Spirit selector.

    渲染黃道釋放面板，含 Fortune / Spirit 切換

    Parameters
    ----------
    fortune_lon:
        Longitude of the Lot of Fortune.
    spirit_lon:
        Longitude of the Lot of Spirit.
    birth_jd:
        Julian Day of birth.
    target_jd:
        Current/target Julian Day.
    lang:
        ``"zh"`` or ``"en"``.
    """
    # ── Header ──────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg,
                rgba(15,10,40,0.97) 0%,
                rgba(20,35,60,0.95) 40%,
                rgba(10,20,50,0.97) 100%);
            border: 1px solid rgba(96,165,250,0.25);
            border-radius: 12px;
            padding: 1.2rem 1.6rem 1rem;
            margin-bottom: 1rem;
        ">
            <div style="
                font-family: 'Cinzel', serif;
                font-size: 1.3rem;
                font-weight: 700;
                background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 60%, #34D399 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 0.3rem;
            ">
                ⚙ Zodiacal Releasing / 黃道釋放
            </div>
            <div style="color: rgba(200,185,255,0.7); font-size: 0.85rem;">
                Multi-level time-lord technique from Vettius Valens' <em>Anthologies</em>.
                Layer 1 in years · Layer 2 in months · Layer 3 in days.
                多層級時主：L1（年）→ L2（月）→ L3（日）
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Fortune / Spirit selector ────────────────────────────
    source = st.radio(
        "釋放起點 / Releasing from:",
        options=["🌙 Lot of Fortune（幸運點 — 身體/生活）",
                 "☀ Lot of Spirit（精神點 — 事業/心智）"],
        horizontal=True,
        key="zr_source_select",
    )
    use_fortune = "Fortune" in source
    lot_lon = fortune_lon if use_fortune else spirit_lon
    lot_label = "Lot of Fortune (幸運點)" if use_fortune else "Lot of Spirit (精神點)"
    lot_sign = ZODIAC_SIGNS[int(lot_lon / 30) % 12]

    st.caption(f"📍 {lot_label}: **{SIGN_GLYPHS.get(lot_sign, '')} {lot_sign}** {lot_lon % 30:.1f}°")

    # ── Compute ──────────────────────────────────────────────
    with st.spinner("計算黃道釋放時主…"):
        l1_periods = compute_zodiacal_releasing_full(
            lot_lon=lot_lon,
            birth_jd=birth_jd,
            target_jd=target_jd,
            source="fortune" if use_fortune else "spirit",
        )

    if not l1_periods:
        st.warning("No periods computed.")
        return

    # ── Current periods hero card ────────────────────────────
    current = get_current_periods(l1_periods)
    _render_zr_current_card(current, lang)

    st.divider()

    # ── Level selector ───────────────────────────────────────
    level_tab_labels = ["L1 大週期 / Major Periods", "L2 小週期 / Sub-Periods", "⏱ 時間軸 / Timeline"]
    _l1_tab, _l2_tab, _timeline_tab = st.tabs(level_tab_labels)

    with _l1_tab:
        _render_zr_level_table(l1_periods, level=1, lang=lang)

    with _l2_tab:
        _render_zr_l2_section(l1_periods, target_jd, lang=lang)

    with _timeline_tab:
        fig = _build_zr_timeline(l1_periods, target_jd, lot_label)
        st.plotly_chart(fig, use_container_width=True)


def _render_zr_current_card(
    current: dict[str, ZRPeriod | None],
    lang: str,
) -> None:
    """Show the current L1/L2/L3 periods as metric cards."""
    st.markdown("#### 🎯 當前時主 / Current Periods")
    cols = st.columns(3)
    levels = ["L1", "L2", "L3"]
    level_labels = ["L1 大週期", "L2 小週期", "L3 細週期"]

    for col, lvl, label in zip(cols, levels, level_labels):
        p: ZRPeriod | None = current.get(lvl)
        with col:
            if p:
                badges = []
                if p.is_peak:
                    badges.append("⚡ Peak")
                if p.is_loosening:
                    badges.append("🔓 Loosening")
                badge_str = " ".join(badges)
                st.markdown(
                    f"""
                    <div style="
                        background: rgba(255,255,255,0.05);
                        border: 1px solid rgba(255,255,255,0.12);
                        border-radius: 10px;
                        padding: 0.8rem 1rem;
                        text-align: center;
                    ">
                        <div style="color: #94A3B8; font-size: 0.75rem; margin-bottom: 4px;">{label}</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: #EAB308;">
                            {p.sign_glyph} {p.sign}
                        </div>
                        <div style="color: #CBD5E1; font-size: 0.9rem;">{p.sign_cn}</div>
                        <div style="color: {_PLANET_COLORS.get(p.ruler, '#ccc')}; font-size: 0.85rem; margin-top: 4px;">
                            {p.ruler_glyph} {p.ruler} ({p.ruler_cn})
                        </div>
                        <div style="color: #64748B; font-size: 0.75rem; margin-top: 4px;">
                            {p.start_date} → {p.end_date}
                        </div>
                        <div style="margin-top: 6px; font-size: 0.75rem; color: #A78BFA;">{badge_str}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="
                        background: rgba(255,255,255,0.02);
                        border: 1px solid rgba(255,255,255,0.06);
                        border-radius: 10px;
                        padding: 0.8rem 1rem;
                        text-align: center;
                        color: #64748B;
                    ">
                        <div style="font-size: 0.75rem;">{label}</div>
                        <div style="margin-top: 8px;">—</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def _render_zr_level_table(
    periods: list[ZRPeriod],
    level: int,
    lang: str,
) -> None:
    """Render a table of ZRPeriod rows for a given level."""
    rows = []
    for p in periods:
        if p.level != level:
            continue
        badges = []
        if p.is_current:
            badges.append("⭐ 當前")
        if p.is_peak:
            badges.append("⚡ Peak")
        if p.is_loosening:
            badges.append("🔓 Loosening")

        rows.append({
            "狀態": " ".join(badges),
            "L": f"L{p.level}",
            "星座/Sign": f"{p.sign_glyph} {p.sign} ({p.sign_cn})",
            "守護/Ruler": f"{p.ruler_glyph} {p.ruler} ({p.ruler_cn})",
            "起始/Start": p.start_date,
            "結束/End": p.end_date,
            "時長/Duration": f"{p.duration_years:.2f}y",
            "宮/H": p.house_from_lot,
        })

    if rows:
        st.dataframe(rows, use_container_width=True, height=min(500, len(rows) * 35 + 60))
    else:
        st.info("No periods at this level.")


def _render_zr_l2_section(
    l1_periods: list[ZRPeriod],
    target_jd: float,
    lang: str,
) -> None:
    """Render L2 sub-periods for all L1 periods with an expander per L1."""
    current_l1 = next((p for p in l1_periods if p.is_current), None)

    for l1 in l1_periods:
        is_open = l1.is_current
        header = (
            f"{'⭐ ' if l1.is_current else ''}"
            f"{l1.sign_glyph} **{l1.sign}** ({l1.sign_cn}) "
            f"| {l1.ruler_glyph} {l1.ruler} "
            f"| {l1.start_date} → {l1.end_date} "
            f"| {l1.duration_years:.1f}y"
        )
        with st.expander(header, expanded=is_open):
            if l1.sub_periods:
                _render_zr_level_table(l1.sub_periods, level=2, lang=lang)
            else:
                st.caption("Sub-periods not computed for this L1 (too far from target date).")


def _build_zr_timeline(
    l1_periods: list[ZRPeriod],
    target_jd: float,
    lot_label: str,
) -> go.Figure:
    """Build a Plotly Gantt chart for L1 and L2 periods."""
    import swisseph as swe

    def jd_to_year_frac(jd: float) -> float:
        y, m, d, _ = swe.revjul(jd)
        return y + (m - 1) / 12.0 + (d - 1) / 365.25

    fig = go.Figure()

    # ── L1 bars ─────────────────────────────────────────────
    for p in l1_periods:
        color = _ELEMENT_COLORS.get(_ELEMENT_OF_SIGN.get(p.sign, "fire"), "#888")
        opacity = 0.85 if p.is_current else 0.5
        x_start = jd_to_year_frac(p.start_jd)
        x_end = jd_to_year_frac(p.end_jd)

        badges = []
        if p.is_peak:
            badges.append("⚡")
        if p.is_loosening:
            badges.append("🔓")

        label = f"L1 {p.sign_glyph} {p.sign}"

        fig.add_trace(go.Bar(
            x=[x_end - x_start],
            y=[label],
            base=[x_start],
            orientation="h",
            marker=dict(
                color=color,
                opacity=opacity,
                line=dict(
                    color="#EAB308" if p.is_current else "rgba(255,255,255,0.1)",
                    width=2 if p.is_current else 0.5,
                ),
            ),
            showlegend=False,
            hovertemplate=(
                f"<b>L1: {p.sign} ({p.sign_cn})</b><br>"
                f"Ruler: {p.ruler} ({p.ruler_cn})<br>"
                f"{p.start_date} → {p.end_date}<br>"
                f"Duration: {p.duration_years:.2f} years<br>"
                f"House from Lot: {p.house_from_lot}<br>"
                + ("⚡ Peak Period<br>" if p.is_peak else "")
                + ("<extra></extra>")
            ),
            name=label,
        ))

        # ── L2 bars inside each L1 ───────────────────────────
        for sub in p.sub_periods:
            sub_color = _PLANET_COLORS.get(sub.ruler, "#888")
            sub_x_start = jd_to_year_frac(sub.start_jd)
            sub_x_end = jd_to_year_frac(sub.end_jd)
            sub_label = f"  L2 {sub.sign_glyph} {sub.sign}"

            fig.add_trace(go.Bar(
                x=[sub_x_end - sub_x_start],
                y=[sub_label],
                base=[sub_x_start],
                orientation="h",
                marker=dict(
                    color=sub_color,
                    opacity=0.8 if sub.is_current else 0.35,
                    line=dict(
                        color="#EAB308" if sub.is_current else "rgba(255,255,255,0.05)",
                        width=1.5 if sub.is_current else 0.3,
                    ),
                ),
                showlegend=False,
                hovertemplate=(
                    f"<b>L2: {sub.sign} ({sub.sign_cn})</b><br>"
                    f"Ruler: {sub.ruler}<br>"
                    f"{sub.start_date} → {sub.end_date}<br>"
                    f"Duration: {sub.duration_years:.3f} years<br>"
                    + ("🔓 Loosening of Bonds<br>" if sub.is_loosening else "")
                    + ("⚡ Peak<br>" if sub.is_peak else "")
                    + "<extra></extra>"
                ),
                name=sub_label,
            ))

    # Today marker
    today_yr = jd_to_year_frac(target_jd)
    fig.add_vline(
        x=today_yr,
        line=dict(color="#EAB308", width=2, dash="dot"),
        annotation_text="Now",
        annotation_font_color="#EAB308",
    )

    fig.update_layout(
        title=dict(
            text=f"Zodiacal Releasing Timeline — {lot_label}",
            font=dict(color="#E2E8F0", size=13),
        ),
        barmode="overlay",
        height=max(500, (len(l1_periods) + sum(len(p.sub_periods) for p in l1_periods)) * 18 + 80),
        margin=dict(l=20, r=20, t=40, b=30),
        paper_bgcolor="rgba(15,10,40,0.97)",
        plot_bgcolor="rgba(25,15,50,0.9)",
        xaxis=dict(
            title="Year",
            color="#94A3B8",
            gridcolor="rgba(255,255,255,0.07)",
        ),
        yaxis=dict(
            color="#94A3B8",
            gridcolor="rgba(255,255,255,0.05)",
            autorange="reversed",
        ),
        font=dict(color="#CBD5E1", size=10),
    )
    return fig
