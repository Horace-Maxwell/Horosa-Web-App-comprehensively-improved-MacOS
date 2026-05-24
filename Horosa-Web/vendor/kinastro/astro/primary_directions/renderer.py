"""
astro/primary_directions/renderer.py — Streamlit UI + SVG Timeline

Renders a professional Primary Directions interface with:
  - Classical manuscript-style SVG timeline chart
  - Bilingual direction list (Chinese / English)
  - Significator filter controls
  - AI analysis integration
  - PDF export support

Visual style: Renaissance astronomical manuscript aesthetic —
  aged parchment texture, serif typography, elegant ink line-work,
  vermillion accent marks for key events.
"""

from __future__ import annotations

import math
from datetime import date
from typing import Dict, List, Optional, Tuple

import streamlit as st

from .calculator import (
    ChartPoint,
    Direction,
    PrimaryDirectionsResult,
    compute_primary_directions,
    _DEFAULT_SIGNIFICATORS,
    _DEFAULT_PROMITTORS,
    _DEFAULT_ASPECTS,
)
from .constants import (
    PLANET_NAMES_EN,
    PLANET_NAMES_ZH,
    PLANET_SYMBOLS,
    PLANET_COLORS,
    PLANET_ORDER,
    CLASSIC_PLANETS,
    ANGLE_POINTS,
    ASPECTS,
    ASPECT_DIRECTION_MEANINGS,
    EXAMPLE_CHARTS,
)
from astro.i18n import auto_cn, get_ui_lang, t


# ──────────────────────────────────────────────────────────────
# CSS — Classical manuscript style
# ──────────────────────────────────────────────────────────────

_CSS = """
<style>
.pd-header {
    background: linear-gradient(135deg, #1a1208 0%, #2d1f0a 50%, #1a1208 100%);
    border-left: 4px solid #c8a84b;
    padding: 16px 22px;
    border-radius: 6px;
    margin-bottom: 16px;
    font-family: Georgia, serif;
}
.pd-header h3 {
    color: #e8d08a;
    margin: 0 0 4px 0;
    font-size: 1.18em;
    letter-spacing: 0.08em;
}
.pd-header p {
    color: #c8b878;
    margin: 0;
    font-size: 0.88em;
    opacity: 0.85;
}
.pd-section-title {
    color: #c8a84b;
    font-family: Georgia, serif;
    font-size: 1.05em;
    font-weight: bold;
    letter-spacing: 0.06em;
    border-bottom: 1px solid rgba(200, 168, 75, 0.3);
    padding-bottom: 5px;
    margin: 18px 0 10px 0;
}
.pd-direction-row {
    background: rgba(200, 168, 75, 0.06);
    border: 1px solid rgba(200, 168, 75, 0.18);
    border-left: 3px solid;
    border-radius: 4px;
    padding: 10px 14px;
    margin-bottom: 7px;
    font-family: Georgia, serif;
}
.pd-direction-key {
    font-size: 1.02em;
    font-weight: bold;
    color: #e8d08a;
    margin-bottom: 3px;
}
.pd-direction-date {
    font-size: 0.88em;
    color: #a89858;
}
.pd-direction-nature {
    font-size: 0.85em;
    color: #c8b878;
    margin-top: 4px;
    font-style: italic;
}
.pd-natal-table {
    font-family: 'Courier New', monospace;
    font-size: 0.83em;
    background: rgba(20, 14, 6, 0.6);
    border: 1px solid rgba(200, 168, 75, 0.2);
    border-radius: 4px;
    padding: 10px;
}
.pd-note {
    background: rgba(200, 168, 75, 0.07);
    border: 1px dashed rgba(200, 168, 75, 0.30);
    border-radius: 5px;
    padding: 10px 14px;
    font-size: 0.87em;
    color: #c8b878;
    font-style: italic;
    margin: 10px 0;
    font-family: Georgia, serif;
}
.pd-angle-badge {
    display: inline-block;
    background: rgba(200, 168, 75, 0.18);
    border: 1px solid rgba(200, 168, 75, 0.4);
    border-radius: 10px;
    padding: 2px 9px;
    font-size: 0.82em;
    color: #e8d08a;
    margin: 1px 3px;
}
</style>
"""

# Aspect colors (classical: benefic vs malefic)
_ASPECT_COLORS = {
    "CNJ": "#e8d08a",   # gold — conjunction: most powerful
    "TRI": "#78c878",   # green — trine: benefic
    "SXT": "#78b8e8",   # blue — sextile: benefic
    "SQR": "#e87848",   # orange-red — square: challenging
    "OPP": "#d84848",   # red — opposition: most challenging
    "PAR": "#d8b8e8",   # lavender — parallel
    "CPAR": "#a8a8d8",  # periwinkle — contra-parallel
}

_DEFAULT_COLOR = "#c8b878"


# ──────────────────────────────────────────────────────────────
# Shared helpers
# ──────────────────────────────────────────────────────────────

def _format_birth_str(year: int, month: int, day: int) -> str:
    """Format a birth date string in the current UI language."""
    if get_ui_lang() != "en":
        return f"{year}年{month}月{day}日"
    return f"{month}/{day}/{year}"


# ──────────────────────────────────────────────────────────────
# SVG Timeline (classical manuscript style)
# ──────────────────────────────────────────────────────────────

def render_primary_directions_svg(
    result: PrimaryDirectionsResult,
    max_display_age: float = 80.0,
    highlight_ages: Optional[List[float]] = None,
    width: int = 820,
    height: int = 600,
) -> str:
    """
    Render a classical-style Primary Directions timeline as SVG.

    Style: Renaissance astronomical manuscript — aged parchment texture,
    fine ink line-work, vermillion highlights for major events, serif type.

    The timeline runs horizontally from birth (age 0) to max_display_age.
    Each direction is plotted as a vertical tick mark with the planet glyph.
    Significator rows are separated by horizontal bands.

    Args:
        result: The computed PrimaryDirectionsResult.
        max_display_age: Right edge of the timeline in years.
        highlight_ages: List of ages to mark with special vermillion indicators.
        width: SVG canvas width in pixels.
        height: SVG canvas height in pixels.

    Returns:
        SVG string (complete, self-contained).
    """
    if highlight_ages is None:
        highlight_ages = []

    # Filter to direct directions only for clarity
    dirs = [d for d in result.directions
            if not d.converse and d.years <= max_display_age]

    # Group by significator
    sig_keys = list(dict.fromkeys(d.significator_key for d in dirs))
    sig_keys = sig_keys[:6]  # max 6 rows

    margin_left = 80
    margin_right = 30
    margin_top = 70
    margin_bottom = 50
    row_height = (height - margin_top - margin_bottom) // max(len(sig_keys), 1)

    timeline_w = width - margin_left - margin_right

    def age_to_x(age: float) -> float:
        return margin_left + (age / max_display_age) * timeline_w

    # ── SVG start ──────────────────────────────────────────────
    parts: List[str] = []

    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )

    # ── Definitions: filters, gradients, patterns ──────────────
    parts.append("""
<defs>
  <!-- Aged parchment grain texture -->
  <filter id="parchment-texture" x="0%" y="0%" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.65 0.62" numOctaves="4"
                  seed="8" result="noise"/>
    <feColorMatrix in="noise" type="saturate" values="0" result="grayNoise"/>
    <feBlend in="SourceGraphic" in2="grayNoise" mode="multiply" result="blend"/>
    <feComposite in="blend" in2="SourceGraphic" operator="in"/>
  </filter>
  <!-- Glow for major events -->
  <filter id="event-glow" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="2.5" result="blur"/>
    <feComposite in="SourceGraphic" in2="blur" operator="over"/>
  </filter>
  <!-- Drop shadow for header text -->
  <filter id="text-shadow">
    <feDropShadow dx="1" dy="1" stdDeviation="1.5" flood-color="#3a2a08" flood-opacity="0.7"/>
  </filter>
  <!-- Parchment background gradient -->
  <linearGradient id="parchment-bg" x1="0" y1="0" x2="1" y2="1"
                  gradientUnits="objectBoundingBox">
    <stop offset="0%" stop-color="#f4e8c8"/>
    <stop offset="35%" stop-color="#ecdcb0"/>
    <stop offset="70%" stop-color="#e8d4a0"/>
    <stop offset="100%" stop-color="#e0c888"/>
  </linearGradient>
  <!-- Row band gradient -->
  <linearGradient id="row-band" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#c89840" stop-opacity="0.12"/>
    <stop offset="100%" stop-color="#c89840" stop-opacity="0.04"/>
  </linearGradient>
  <!-- Vignette -->
  <radialGradient id="vignette" cx="50%" cy="50%" r="70%">
    <stop offset="60%" stop-color="#8b6914" stop-opacity="0"/>
    <stop offset="100%" stop-color="#2a1a04" stop-opacity="0.35"/>
  </radialGradient>
</defs>
""")

    # ── Background ─────────────────────────────────────────────
    parts.append(
        f'<rect width="{width}" height="{height}" fill="url(#parchment-bg)"/>'
    )
    # Fine noise grain overlay
    parts.append(
        f'<rect width="{width}" height="{height}" '
        f'fill="#8b6914" opacity="0.07" filter="url(#parchment-texture)"/>'
    )
    # Vignette
    parts.append(
        f'<rect width="{width}" height="{height}" fill="url(#vignette)"/>'
    )

    # ── Decorative border ──────────────────────────────────────
    _draw_manuscript_border(parts, width, height)

    # ── Title ─────────────────────────────────────────────────
    birth_str = _format_birth_str(result.year, result.month, result.day)
    loc = result.location_name or ""
    method_label = "Mundo (Placidus)" if result.method == "mundo" else "Zodiacal (Ptolemy)"
    key_label = {"naibod": "Naibod Key", "ptolemy": "Ptolemy Key",
                 "solar_arc": "Solar Arc Key"}.get(result.time_key, result.time_key)

    parts.append(
        f'<text x="{width//2}" y="24" text-anchor="middle" '
        f'font-family="Georgia,\'Times New Roman\',serif" font-size="14" '
        f'font-weight="bold" fill="#4a2a08" letter-spacing="1.5" '
        f'filter="url(#text-shadow)">'
        f'PRIMARY DIRECTIONS — TABULAE DIRECTIONUM</text>'
    )
    parts.append(
        f'<text x="{width//2}" y="42" text-anchor="middle" '
        f'font-family="Georgia,serif" font-size="10.5" fill="#6a4a18" '
        f'font-style="italic">'
        f'{birth_str}  {loc}  ·  {method_label}  ·  {key_label}</text>'
    )
    parts.append(
        f'<text x="{width//2}" y="57" text-anchor="middle" '
        f'font-family="Georgia,serif" font-size="9.5" fill="#8a6428" '
        f'font-style="italic" letter-spacing="0.8">'
        f'古典主限推運 ·  Age 0 – {int(max_display_age)}</text>'
    )

    # ── Age axis ───────────────────────────────────────────────
    axis_y = height - margin_bottom + 5
    parts.append(
        f'<line x1="{margin_left}" y1="{axis_y}" '
        f'x2="{margin_left + timeline_w}" y2="{axis_y}" '
        f'stroke="#6a4a18" stroke-width="1.5"/>'
    )

    # Decade ticks and labels
    for age in range(0, int(max_display_age) + 1, 10):
        x = age_to_x(age)
        parts.append(
            f'<line x1="{x:.1f}" y1="{axis_y}" '
            f'x2="{x:.1f}" y2="{axis_y + 7}" '
            f'stroke="#6a4a18" stroke-width="1.2"/>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{axis_y + 17}" text-anchor="middle" '
            f'font-family="Georgia,serif" font-size="9" fill="#5a3a12">{age}</text>'
        )
        # Light vertical guide line
        parts.append(
            f'<line x1="{x:.1f}" y1="{margin_top}" '
            f'x2="{x:.1f}" y2="{axis_y}" '
            f'stroke="#8a6428" stroke-width="0.4" stroke-dasharray="3,5" opacity="0.35"/>'
        )

    # 5-year minor ticks
    for age in range(0, int(max_display_age) + 1, 5):
        if age % 10 != 0:
            x = age_to_x(age)
            parts.append(
                f'<line x1="{x:.1f}" y1="{axis_y}" '
                f'x2="{x:.1f}" y2="{axis_y + 4}" '
                f'stroke="#6a4a18" stroke-width="0.8"/>'
            )

    # "Age" axis label
    parts.append(
        f'<text x="{margin_left + timeline_w // 2}" y="{axis_y + 30}" '
        f'text-anchor="middle" font-family="Georgia,serif" font-size="9" '
        f'fill="#5a3a12" font-style="italic">Anno Vitæ (Age)</text>'
    )

    # ── Significator rows ──────────────────────────────────────
    row_dirs: Dict[str, List[Direction]] = {k: [] for k in sig_keys}
    for d in dirs:
        if d.significator_key in row_dirs:
            row_dirs[d.significator_key].append(d)

    for row_idx, sig_key in enumerate(sig_keys):
        row_y_center = margin_top + row_idx * row_height + row_height // 2
        row_y_top = margin_top + row_idx * row_height
        row_y_bot = row_y_top + row_height

        # Row band (alternating shade)
        if row_idx % 2 == 0:
            parts.append(
                f'<rect x="{margin_left}" y="{row_y_top}" '
                f'width="{timeline_w}" height="{row_height}" '
                f'fill="url(#row-band)" opacity="0.7"/>'
            )

        # Significator label (left margin)
        sym = PLANET_SYMBOLS.get(sig_key, sig_key)
        name_zh = PLANET_NAMES_ZH.get(sig_key, sig_key)
        parts.append(
            f'<text x="{margin_left - 8}" y="{row_y_center + 4}" '
            f'text-anchor="end" font-family="Georgia,serif" font-size="11" '
            f'font-weight="bold" fill="#4a2a08">{sym}</text>'
        )
        parts.append(
            f'<text x="{margin_left - 8}" y="{row_y_center + 15}" '
            f'text-anchor="end" font-family="\'Noto Sans CJK TC\',serif" '
            f'font-size="8.5" fill="#6a4228">{name_zh}</text>'
        )

        # Horizontal row guide line
        parts.append(
            f'<line x1="{margin_left}" y1="{row_y_center}" '
            f'x2="{margin_left + timeline_w}" y2="{row_y_center}" '
            f'stroke="#8a6428" stroke-width="0.5" stroke-dasharray="1,6" opacity="0.5"/>'
        )

        # Direction markers for this row
        for d in row_dirs[sig_key]:
            x = age_to_x(d.years)
            asp_color = _ASPECT_COLORS.get(d.aspect_key, _DEFAULT_COLOR)
            prom_sym = PLANET_SYMBOLS.get(d.promittor_key, d.promittor_key)
            asp_sym = next((a["symbol"] for a in ASPECTS if a["key"] == d.aspect_key), "")

            # Check if this is a highlight age
            is_highlight = any(abs(d.years - ha) < 1.5 for ha in highlight_ages)

            if is_highlight:
                # Vermillion highlight ring
                parts.append(
                    f'<circle cx="{x:.1f}" cy="{row_y_center:.1f}" r="7" '
                    f'fill="none" stroke="#c83020" stroke-width="1.5" '
                    f'opacity="0.8" filter="url(#event-glow)"/>'
                )

            # Vertical tick line
            tick_h = row_height * 0.35
            parts.append(
                f'<line x1="{x:.1f}" y1="{row_y_center - tick_h:.1f}" '
                f'x2="{x:.1f}" y2="{row_y_center + tick_h:.1f}" '
                f'stroke="{asp_color}" stroke-width="1.2" opacity="0.85"/>'
            )

            # Planet glyph above the tick
            parts.append(
                f'<text x="{x:.1f}" y="{row_y_center - tick_h - 2:.1f}" '
                f'text-anchor="middle" dominant-baseline="bottom" '
                f'font-family="Georgia,serif" font-size="9" '
                f'fill="{asp_color}" opacity="0.9">{prom_sym}{asp_sym}</text>'
            )

            # Age label below (only for major events — CNJ/OPP)
            if d.aspect_key in ("CNJ", "OPP") or is_highlight:
                age_label = f"{d.years:.1f}"
                parts.append(
                    f'<text x="{x:.1f}" y="{row_y_center + tick_h + 9:.1f}" '
                    f'text-anchor="middle" '
                    f'font-family="Georgia,serif" font-size="7.5" '
                    f'fill="{asp_color}" opacity="0.8">{age_label}</text>'
                )

    # ── Legend ─────────────────────────────────────────────────
    legend_items = [
        ("CNJ", "合相/Conjunction"),
        ("OPP", "對分/Opposition"),
        ("SQR", "四分/Square"),
        ("TRI", "三分/Trine"),
        ("SXT", "六分/Sextile"),
    ]
    legend_y = height - 15
    lx = margin_left
    for asp_key, asp_label in legend_items:
        c = _ASPECT_COLORS.get(asp_key, _DEFAULT_COLOR)
        parts.append(
            f'<rect x="{lx}" y="{legend_y - 8}" width="12" height="6" '
            f'fill="{c}" opacity="0.8"/>'
        )
        parts.append(
            f'<text x="{lx + 14}" y="{legend_y - 2}" '
            f'font-family="Georgia,serif" font-size="8" fill="#4a2a08">{asp_label}</text>'
        )
        lx += 110

    parts.append("</svg>")
    return "".join(parts)


def _draw_manuscript_border(parts: List[str], width: int, height: int) -> None:
    """Draw an elegant double-line border with corner ornaments."""
    pad = 5
    pad2 = 9
    w, h = width, height

    # Outer border
    parts.append(
        f'<rect x="{pad}" y="{pad}" width="{w-2*pad}" height="{h-2*pad}" '
        f'fill="none" stroke="#8b6914" stroke-width="1.5" opacity="0.7"/>'
    )
    # Inner border
    parts.append(
        f'<rect x="{pad2}" y="{pad2}" width="{w-2*pad2}" height="{h-2*pad2}" '
        f'fill="none" stroke="#8b6914" stroke-width="0.8" opacity="0.45"/>'
    )

    # Corner ornaments (simple cross pattern)
    corners = [(pad, pad), (w - pad, pad), (pad, h - pad), (w - pad, h - pad)]
    for cx, cy in corners:
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="3" '
            f'fill="#8b6914" opacity="0.55"/>'
        )
        parts.append(
            f'<line x1="{cx-7}" y1="{cy}" x2="{cx+7}" y2="{cy}" '
            f'stroke="#8b6914" stroke-width="0.8" opacity="0.4"/>'
        )
        parts.append(
            f'<line x1="{cx}" y1="{cy-7}" x2="{cx}" y2="{cy+7}" '
            f'stroke="#8b6914" stroke-width="0.8" opacity="0.4"/>'
        )


# ──────────────────────────────────────────────────────────────
# Streamlit renderer
# ──────────────────────────────────────────────────────────────

def render_primary_directions(result: PrimaryDirectionsResult) -> None:
    """
    Render the full Primary Directions UI in Streamlit.

    Shows:
      1. SVG classical timeline
      2. Natal positions table
      3. Direction list (filterable by significator / age range)
      4. Individual direction interpretation cards
    """
    st.markdown(_CSS, unsafe_allow_html=True)
    lang = get_ui_lang()
    is_zh = lang != "en"

    # ── Header ────────────────────────────────────────────────
    method_label = (
        auto_cn("Mundo（Placidus 半弧體系）", "Mundo (Placidus Semi-Arc)")
        if result.method == "mundo" else
        auto_cn("黃道法（Ptolemy 斜升法）", "Zodiacal (Ptolemy Oblique Ascension)")
    )
    key_label = {
        "naibod":    auto_cn("奈包德時間鍵（0.9856°/年）", "Naibod Key (0.9856°/yr)"),
        "ptolemy":   auto_cn("托勒密時間鍵（1°/年）", "Ptolemy Key (1°/yr)"),
        "solar_arc": auto_cn("太陽弧時間鍵", "Solar Arc Key"),
    }.get(result.time_key, result.time_key)

    birth_str = _format_birth_str(result.year, result.month, result.day)
    loc = result.location_name or ""

    st.markdown(
        f'<div class="pd-header">'
        f'<h3>⚷ {auto_cn("古典主限推運", "Classical Primary Directions")}'
        f' — Tabulæ Directionum</h3>'
        f'<p>{birth_str}  {loc}<br/>'
        f'{auto_cn("方法", "Method")}: {method_label} &nbsp;·&nbsp; '
        f'{auto_cn("時間鍵", "Time Key")}: {key_label} &nbsp;·&nbsp; '
        f'{auto_cn("最大年齡", "Max Age")}: {int(result.max_age)} {auto_cn("歲", "yrs")}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Classical note ─────────────────────────────────────────
    st.markdown(
        f'<div class="pd-note">'
        + auto_cn(
            '✦ 主限推運（Primary Directions）乃西方古典占星最核心的時機推算體系，'
            '起源於 Claudius Ptolemy《占星四書》（約 150 CE），'
            '後由 Regiomontanus（1490年）與 Placidus de Titis（1657年）加以精算。'
            '其核心原理：地球自轉帶動天球旋轉，每 1° 的轉動弧對應約 1 年的生命歷程。'
            '合相、對分、四分、三分、六分代表不同質性的重要事件。',
            'Primary Directions are the most fundamental timing technique of classical Western astrology, '
            'originating with Claudius Ptolemy\'s *Tetrabiblos* (c. 150 CE) and refined by '
            'Regiomontanus (1490) and Placidus de Titis (1657). '
            'The core principle: each 1° of Earth\'s diurnal rotation corresponds to ~1 year of life. '
            'Conjunction, opposition, square, trine and sextile mark events of different qualities.',
        )
        + '</div>',
        unsafe_allow_html=True,
    )

    # ── Controls ───────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        show_converse = st.checkbox(
            auto_cn("顯示逆向主限", "Show Converse Directions"),
            value=False,
            key="pd_show_converse",
        )
    with col2:
        age_range = st.slider(
            auto_cn("年齡範圍", "Age Range"),
            min_value=0,
            max_value=int(result.max_age),
            value=(0, min(80, int(result.max_age))),
            key="pd_age_range",
        )
    with col3:
        filter_sigs = st.multiselect(
            auto_cn("過濾主星", "Filter Significators"),
            options=[f"{PLANET_SYMBOLS.get(k,'')}{PLANET_NAMES_ZH.get(k,k)}" for k in result.significators],
            default=[],
            key="pd_sig_filter",
        )

    age_min, age_max = age_range

    # ── SVG Timeline ───────────────────────────────────────────
    st.markdown(
        f'<p class="pd-section-title">'
        + auto_cn("◈ 主限推運時間軸（Tabulæ Directionum）", "◈ Primary Directions Timeline (Tabulæ Directionum)")
        + "</p>",
        unsafe_allow_html=True,
    )
    svg = render_primary_directions_svg(
        result,
        max_display_age=float(age_max),
    )
    st.markdown(svg, unsafe_allow_html=True)

    # ── Natal Positions ────────────────────────────────────────
    with st.expander(auto_cn("⊕ 出生盤位置（赤道坐標）", "⊕ Natal Positions (Equatorial Data)")):
        _render_natal_table(result, lang)

    # ── Direction list ─────────────────────────────────────────
    st.markdown(
        f'<p class="pd-section-title">'
        + auto_cn("◈ 主限推運清單", "◈ Primary Directions List")
        + "</p>",
        unsafe_allow_html=True,
    )

    # Filter directions
    selected_sigs: set[str] = set()
    if filter_sigs:
        for label in filter_sigs:
            for k in result.significators:
                sym = PLANET_SYMBOLS.get(k, "")
                zh = PLANET_NAMES_ZH.get(k, k)
                if f"{sym}{zh}" == label:
                    selected_sigs.add(k)

    filtered = [
        d for d in result.directions
        if age_min <= d.years <= age_max
        and (show_converse or not d.converse)
        and (not selected_sigs or d.significator_key in selected_sigs)
    ]

    if not filtered:
        st.info(auto_cn("此範圍內無主限推運。", "No directions in this range."))
    else:
        for d in filtered[:60]:  # cap at 60 for performance
            _render_direction_card(d, lang)

    if len(filtered) > 60:
        st.caption(
            auto_cn(f"⋯ 共 {len(filtered)} 個推運，僅顯示前 60 個。",
                    f"⋯ {len(filtered)} directions total; showing first 60.")
        )


def _render_natal_table(result: PrimaryDirectionsResult, lang: str) -> None:
    """Render a compact table of natal positions with equatorial data."""
    is_zh = lang != "en"
    rows = []
    for p in result.natal_points:
        if p.key not in (CLASSIC_PLANETS + ANGLE_POINTS + ["NN"]):
            continue
        rows.append({
            auto_cn("行星", "Planet"): f"{p.symbol} {p.name_zh if is_zh else p.name_en}",
            auto_cn("黃道經度", "Ecliptic Lon"): f"{p.sign_symbol}{p.sign_degree:.2f}° ({p.longitude:.3f}°)",
            auto_cn("赤經(RA)", "RA"): f"{p.ra:.3f}°",
            auto_cn("赤緯(Dec)", "Dec"): f"{p.dec:+.3f}°",
            auto_cn("斜升(OA)", "OA"): f"{p.oa:.3f}°",
            auto_cn("晝弧(SA)", "Diurnal SA"): f"{p.sa_diurnal:.2f}°",
        })
    if rows:
        import pandas as pd
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch")


def _render_direction_card(d: Direction, lang: str) -> None:
    """Render a single direction as a styled card."""
    is_zh = lang != "en"
    asp_color = _ASPECT_COLORS.get(d.aspect_key, _DEFAULT_COLOR)

    label = d.direction_label_zh if is_zh else d.direction_label_en
    ev_date = d.event_date.strftime("%Y年%m月" if is_zh else "%b %Y")

    sig_sym = PLANET_SYMBOLS.get(d.significator_key, d.significator_key)
    prom_sym = PLANET_SYMBOLS.get(d.promittor_key, d.promittor_key)
    asp_sym = next((a["symbol"] for a in ASPECTS if a["key"] == d.aspect_key), "")

    conv_badge = f'<span class="pd-angle-badge">{"逆向" if is_zh else "Converse"}</span>' \
        if d.converse else ""
    method_badge = f'<span class="pd-angle-badge">{"Mundo" if d.method=="mundo" else "黃道"}</span>'

    nature = d.nature_zh if is_zh else d.nature_en
    asp_nat = d.aspect_nature_zh if is_zh else d.aspect_nature_en

    st.markdown(
        f'<div class="pd-direction-row" style="border-left-color: {asp_color};">'
        f'<div class="pd-direction-key">'
        f'{sig_sym} → {prom_sym} {asp_sym} &nbsp;{conv_badge}{method_badge}</div>'
        f'<div style="color:{asp_color}; font-size:0.93em; font-family:Georgia,serif;">'
        f'{label}</div>'
        f'<div class="pd-direction-date">'
        f'{auto_cn("弧度","Arc")}: {d.arc:.3f}° &nbsp;·&nbsp; '
        f'{auto_cn("年齡","Age")}: {d.years:.2f}{auto_cn("歲","yrs")} &nbsp;·&nbsp; '
        f'{auto_cn("時間","Date")}: {ev_date}</div>'
        f'<div class="pd-direction-nature">{nature}</div>'
        f'<div class="pd-direction-nature" style="color:#a08848;">{asp_nat}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
