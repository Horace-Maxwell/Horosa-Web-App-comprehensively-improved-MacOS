"""
astro/mundane/renderer.py — Mundane Astrology Streamlit UI

Renders the full Mundane Astrology interface with:
  Tab 1: Ingress Chart (入宮圖) — Spring/Summer/Autumn/Winter equinox/solstice
  Tab 2: Eclipse Chart (日月食) — Next solar/lunar eclipses
  Tab 3: Great Conjunctions (木土大合相) — Jupiter-Saturn timeline
  Tab 4: National Overview (國家世俗運勢) — Country selector + outer planet transits

Visual theme: dark cosmic with imperial gold accents (深藍、靛紫、金色、星空).
Follows KinAstro conventions:
  - compute_* called before render_* (pure/cacheable)
  - render_streamlit() is the single entry point
  - i18n via astro.i18n.t() / auto_cn()
  - st.dataframe(..., width="stretch")
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

from .calculator import (
    MundaneChart,
    MundanePlanet,
    MundaneAspect,
    EclipseInfo,
    GreatConjunction,
    compute_ingress_chart,
    compute_eclipse_chart,
    get_great_conjunctions_timeline,
    compute_next_great_conjunction,
    compute_current_outer_planets,
    compute_national_mundane,
    format_mundane_chart_for_prompt,
    _sign_index_from_lon,
)
from .constants import (
    INGRESS_NAMES_EN,
    INGRESS_NAMES_ZH,
    INGRESS_ICONS,
    COUNTRY_CAPITALS,
    MUNDANE_HOUSES,
    OUTER_PLANET_THEMES,
    PLANET_GLYPHS,
    PLANET_NAMES_ZH,
    SIGN_NAMES_EN,
    SIGN_NAMES_ZH,
    SIGN_ELEMENTS,
    SIGN_GLYPHS,
    MUNDANE_COLORS,
    ELEMENT_CYCLE_DESCRIPTIONS,
    GREAT_CONJUNCTIONS,
)
from astro.i18n import auto_cn, t


# ─────────────────────────────────────────────────────────────────────────────
# CSS  世俗占星 UI 樣式
# ─────────────────────────────────────────────────────────────────────────────

_MUNDANE_CSS = """
<style>
/* ── Mundane Astrology — Cosmic Imperial Theme ───────────────────── */
.mundane-header {
    background: linear-gradient(135deg, #050a14 0%, #0d1a35 50%, #050a14 100%);
    border: 1px solid #C8A951;
    border-radius: 10px;
    padding: 20px 28px;
    margin-bottom: 20px;
    box-shadow: 0 0 30px rgba(200,169,81,0.18), inset 0 0 60px rgba(29,48,102,0.3);
    position: relative;
    overflow: hidden;
}
.mundane-header::before {
    content: '⭐';
    position: absolute;
    right: 22px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 3rem;
    opacity: 0.15;
}
.mundane-title {
    color: #C8A951;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin: 0 0 6px 0;
    text-shadow: 0 0 12px rgba(200,169,81,0.4);
}
.mundane-subtitle {
    color: #8899BB;
    font-size: 0.95rem;
    margin: 0;
}
/* ── Cards ───────────────────────────────────────────────────────── */
.mundane-card {
    background: #0d1428;
    border: 1px solid #2A3A5A;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.mundane-card:hover {
    border-color: #C8A951;
    box-shadow: 0 0 12px rgba(200,169,81,0.12);
}
.mundane-card-title {
    color: #C8A951;
    font-size: 1.05rem;
    font-weight: 600;
    margin: 0 0 8px 0;
}
/* ── Planet Table ────────────────────────────────────────────────── */
.planet-row {
    display: flex;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #1A2540;
    font-size: 0.9rem;
}
.planet-glyph {
    font-size: 1.2rem;
    width: 30px;
    text-align: center;
}
.planet-name { color: #E8D8A0; width: 100px; }
.planet-pos  { color: #C8A951; width: 140px; }
.planet-house{ color: #8899BB; width: 60px; }
.planet-retro{ color: #FF6347; font-size: 0.75rem; }
/* ── Aspect Grid ─────────────────────────────────────────────────── */
.aspect-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    margin: 2px;
}
/* ── Eclipse Badge ───────────────────────────────────────────────── */
.eclipse-card {
    background: linear-gradient(135deg, #0d1428 0%, #1a0e30 100%);
    border: 1px solid #6A3FA0;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 14px;
}
/* ── Conjunction Timeline ────────────────────────────────────────── */
.conj-item {
    border-left: 3px solid #C8A951;
    padding: 8px 14px;
    margin: 8px 0;
    background: #0d1428;
    border-radius: 0 6px 6px 0;
}
.conj-future {
    border-left-color: #4A9B8A;
    opacity: 0.9;
}
.conj-year { color: #C8A951; font-weight: 700; font-size: 1.1rem; }
.conj-sign { color: #8899BB; margin: 2px 0; }
.conj-note { color: #A8B8D0; font-size: 0.9rem; }
/* ── SVG Chart Container ─────────────────────────────────────────── */
.mundane-chart-container {
    background: radial-gradient(ellipse at center, #0d1428 0%, #050a14 100%);
    border: 1px solid #2A3A5A;
    border-radius: 10px;
    padding: 10px;
    display: flex;
    justify-content: center;
}
/* ── House Interpretation ────────────────────────────────────────── */
.house-card {
    background: #080f1e;
    border: 1px solid #1A2540;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 4px 0;
    font-size: 0.88rem;
}
.house-number { color: #C8A951; font-weight: 700; }
.house-planet { color: #E8D8A0; }
.house-meaning{ color: #7B8DB0; }
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
# SVG Chart Builder  SVG 輪盤繪製
# ─────────────────────────────────────────────────────────────────────────────

_SVG_W = 500
_SVG_H = 500
_CX    = 250
_CY    = 250
_R_OUTER = 220   # Outer ring (zodiac band)
_R_INNER = 175   # Inner ring (house boundary)
_R_PLANET= 145   # Planet placement radius
_R_ASPECT= 90    # Aspect lines radius


def _lon_to_angle_svg(lon: float, asc: float) -> float:
    """Convert ecliptic longitude to SVG angle (degrees, clockwise from top)."""
    # In astrology wheels, ASC is on the left (180° in SVG space)
    # and we go counter-clockwise for increasing ecliptic longitude.
    angle = (asc - lon) % 360
    # Convert to SVG: 0° at top, clockwise
    return angle


def _polar_to_xy(cx: float, cy: float, r: float, angle_deg: float) -> Tuple[float, float]:
    """Convert polar (radius, angle in degrees from top, clockwise) to Cartesian."""
    rad = math.radians(angle_deg - 90)  # -90 so 0° is at top
    x = cx + r * math.cos(rad)
    y = cy + r * math.sin(rad)
    return x, y


def _build_mundane_svg(chart: MundaneChart) -> str:
    """
    Build an SVG astrology wheel for a MundaneChart.

    Renders: zodiac ring, sign symbols, house cusps, planet positions,
    and aspect lines.
    """
    lines: List[str] = []

    # ── SVG header
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{_SVG_W}" height="{_SVG_H}" '
        f'viewBox="0 0 {_SVG_W} {_SVG_H}">'
    )

    # ── Defs: gradients + filters
    lines.append("""
<defs>
  <radialGradient id="bg-grad" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#0d1428" stop-opacity="1"/>
    <stop offset="100%" stop-color="#050a14" stop-opacity="1"/>
  </radialGradient>
  <filter id="glow">
    <feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="blur"/>
    <feComposite in="SourceGraphic" in2="blur" operator="over"/>
  </filter>
  <filter id="planet-glow">
    <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="blur"/>
    <feComposite in="SourceGraphic" in2="blur" operator="over"/>
  </filter>
</defs>""")

    # ── Background circle
    lines.append(
        f'<circle cx="{_CX}" cy="{_CY}" r="{_R_OUTER + 10}" '
        f'fill="url(#bg-grad)" stroke="#2A3A5A" stroke-width="1.5"/>'
    )

    # ── Zodiac band (outer ring segments, 12 × 30°)
    _element_colors = {
        "Fire":  "#C94B2A",
        "Earth": "#8B6333",
        "Air":   "#2A8B8B",
        "Water": "#2A4A8B",
    }

    asc = chart.asc
    for i in range(12):
        lon_start = i * 30.0
        lon_end   = lon_start + 30.0
        elem = SIGN_ELEMENTS[i]
        color = _element_colors.get(elem, "#2A3A5A")

        # Start and end angles in SVG space
        a_start = _lon_to_angle_svg(lon_start, asc)
        a_end   = _lon_to_angle_svg(lon_end,   asc)

        # Outer and inner arc points
        x1o, y1o = _polar_to_xy(_CX, _CY, _R_OUTER, a_start)
        x2o, y2o = _polar_to_xy(_CX, _CY, _R_OUTER, a_end)
        x1i, y1i = _polar_to_xy(_CX, _CY, _R_INNER, a_start)
        x2i, y2i = _polar_to_xy(_CX, _CY, _R_INNER, a_end)

        # Counter-clockwise sweep for astrology wheel (increasing longitude goes CCW)
        sweep = 0
        # Each sign spans exactly 30°, always less than 180°, so large-arc-flag = 0
        large_arc = 0
        # Inner arc must sweep the opposite direction to close the segment correctly
        sweep_inner = 1 - sweep  # = 1 (clockwise) to close the sector shape

        path = (
            f"M {x1o:.2f},{y1o:.2f} "
            f"A {_R_OUTER},{_R_OUTER} 0 {large_arc},{sweep} {x2o:.2f},{y2o:.2f} "
            f"L {x2i:.2f},{y2i:.2f} "
            f"A {_R_INNER},{_R_INNER} 0 {large_arc},{sweep_inner} {x1i:.2f},{y1i:.2f} Z"
        )
        lines.append(
            f'<path d="{path}" fill="{color}" fill-opacity="0.25" '
            f'stroke="#2A3A5A" stroke-width="0.8"/>'
        )

        # Sign glyph at mid-segment
        mid_angle = _lon_to_angle_svg(i * 30 + 15, asc)
        gx, gy = _polar_to_xy(_CX, _CY, (_R_OUTER + _R_INNER) / 2, mid_angle)
        glyph = SIGN_GLYPHS[i]
        lines.append(
            f'<text x="{gx:.2f}" y="{gy:.2f}" '
            f'text-anchor="middle" dominant-baseline="central" '
            f'font-size="13" fill="{color}" fill-opacity="0.9" '
            f'filter="url(#glow)">{glyph}</text>'
        )

    # ── House cusp lines (thin gold lines)
    cusps = chart.cusps  # 1-based, so cusps[1]..cusps[12]
    for h in range(1, 13):
        if h < len(cusps):
            cusp_lon = cusps[h]
        else:
            continue
        a = _lon_to_angle_svg(cusp_lon, asc)
        xi, yi = _polar_to_xy(_CX, _CY, _R_ASPECT - 10, a)
        xo, yo = _polar_to_xy(_CX, _CY, _R_INNER, a)
        is_angular = h in (1, 4, 7, 10)
        color = "#C8A951" if is_angular else "#2A3A5A"
        width = "1.5" if is_angular else "0.8"
        lines.append(
            f'<line x1="{xi:.2f}" y1="{yi:.2f}" x2="{xo:.2f}" y2="{yo:.2f}" '
            f'stroke="{color}" stroke-width="{width}" stroke-opacity="0.75"/>'
        )
        # House number
        num_angle = _lon_to_angle_svg(cusp_lon + 15, asc)
        nx, ny = _polar_to_xy(_CX, _CY, _R_ASPECT - 22, num_angle)
        lines.append(
            f'<text x="{nx:.2f}" y="{ny:.2f}" '
            f'text-anchor="middle" dominant-baseline="central" '
            f'font-size="9" fill="#7B8DB0" fill-opacity="0.8">{h}</text>'
        )

    # ── ASC / MC markers
    for lon_val, label, col in [
        (asc, "ASC", "#FFD700"),
        (chart.mc, "MC", "#C0C0C0"),
        ((asc + 180) % 360, "DSC", "#FFD700"),          # DSC is always exactly opposite ASC
        ((chart.mc + 180) % 360, "IC", "#C0C0C0"),      # IC is always exactly opposite MC
    ]:
        a = _lon_to_angle_svg(lon_val, asc)
        xi, yi = _polar_to_xy(_CX, _CY, _R_INNER - 2, a)
        xo, yo = _polar_to_xy(_CX, _CY, _R_INNER + 14, a)
        lines.append(
            f'<line x1="{xi:.2f}" y1="{yi:.2f}" x2="{xo:.2f}" y2="{yo:.2f}" '
            f'stroke="{col}" stroke-width="2" stroke-opacity="0.9"/>'
        )
        lx, ly = _polar_to_xy(_CX, _CY, _R_INNER + 24, a)
        lines.append(
            f'<text x="{lx:.2f}" y="{ly:.2f}" '
            f'text-anchor="middle" dominant-baseline="central" '
            f'font-size="9" font-weight="bold" fill="{col}">{label}</text>'
        )

    # ── Aspect lines (inner circle)
    _aspect_colors = {
        "Conjunction":  "#FFD700",
        "Opposition":   "#FF4444",
        "Trine":        "#00AA66",
        "Square":       "#FF5500",
        "Sextile":      "#4488FF",
        "Quincunx":     "#9370DB",
        "Semi-square":  "#FF8855",
        "Sesquiquadrate": "#FF9944",
    }
    for asp in chart.aspects:
        pl1 = chart.planets.get(asp.planet1)
        pl2 = chart.planets.get(asp.planet2)
        if not pl1 or not pl2:
            continue
        a1 = _lon_to_angle_svg(pl1.longitude, asc)
        a2 = _lon_to_angle_svg(pl2.longitude, asc)
        x1, y1 = _polar_to_xy(_CX, _CY, _R_ASPECT, a1)
        x2, y2 = _polar_to_xy(_CX, _CY, _R_ASPECT, a2)
        col = _aspect_colors.get(asp.aspect_name, "#AAAAAA")
        opacity = max(0.2, 0.7 - asp.orb / 8.0)
        lines.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{col}" stroke-width="1.2" stroke-opacity="{opacity:.2f}"/>'
        )

    # ── Planet symbols
    _planet_colors = {
        "Sun":     "#FFD700",
        "Moon":    "#C0C0C0",
        "Mercury": "#88AAFF",
        "Venus":   "#FF88AA",
        "Mars":    "#FF5533",
        "Jupiter": "#FFB533",
        "Saturn":  "#AAAAAA",
        "Uranus":  "#44DDCC",
        "Neptune": "#4466FF",
        "Pluto":   "#AA44AA",
    }
    for name, pl in chart.planets.items():
        a = _lon_to_angle_svg(pl.longitude, asc)
        px, py = _polar_to_xy(_CX, _CY, _R_PLANET, a)
        col = _planet_colors.get(name, "#E8D8A0")
        glyph = pl.glyph

        # Circle backing
        lines.append(
            f'<circle cx="{px:.2f}" cy="{py:.2f}" r="11" '
            f'fill="#0d1428" stroke="{col}" stroke-width="1.2" '
            f'stroke-opacity="0.8" filter="url(#planet-glow)"/>'
        )
        # Planet glyph
        lines.append(
            f'<text x="{px:.2f}" y="{py:.2f}" '
            f'text-anchor="middle" dominant-baseline="central" '
            f'font-size="12" fill="{col}" filter="url(#planet-glow)">'
            f'{glyph}</text>'
        )
        # Retrograde marker
        if pl.is_retrograde:
            rx, ry = _polar_to_xy(_CX, _CY, _R_PLANET - 18, a)
            lines.append(
                f'<text x="{rx:.2f}" y="{ry:.2f}" '
                f'text-anchor="middle" dominant-baseline="central" '
                f'font-size="8" fill="#FF6347">ℛ</text>'
            )

    # ── Centre: chart type + date
    dt_str = chart.utc_datetime.strftime("%Y-%m-%d %H:%M UTC")
    lines.append(
        f'<text x="{_CX}" y="{_CY - 10}" '
        f'text-anchor="middle" dominant-baseline="central" '
        f'font-size="11" fill="#C8A951" font-weight="bold">'
        f'{chart.chart_type_label_zh}</text>'
    )
    lines.append(
        f'<text x="{_CX}" y="{_CY + 8}" '
        f'text-anchor="middle" dominant-baseline="central" '
        f'font-size="9" fill="#7B8DB0">{dt_str}</text>'
    )

    lines.append("</svg>")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Sub-render: Ingress Chart tab  入宮圖分頁
# ─────────────────────────────────────────────────────────────────────────────

def _render_ingress_tab() -> None:
    """Render the Ingress Chart tab content."""
    st.markdown(
        auto_cn(
            "**入宮圖（Ingress Chart）**是世俗占星最核心的工具。"
            "太陽進入基本星座（春分牡羊、夏至巨蟹、秋分天秤、冬至摩羯）時的星盤，"
            "預示接下來一季乃至一年的國家與世界大勢。",
            "**Ingress Charts** are the cornerstone of Mundane Astrology. "
            "The chart cast for the moment the Sun enters a cardinal sign "
            "forecasts national and world trends for the following season or year."
        )
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        ingress_year = st.number_input(
            auto_cn("年份", "Year"),
            min_value=1800,
            max_value=2100,
            value=datetime.now().year,
            step=1,
            key="mundane_ingress_year",
        )

    with col2:
        ingress_options = {
            auto_cn("♈ 牡羊入宮（春分）", "♈ Aries Ingress (Vernal Equinox)"): "aries",
            auto_cn("♋ 巨蟹入宮（夏至）", "♋ Cancer Ingress (Summer Solstice)"): "cancer",
            auto_cn("♎ 天秤入宮（秋分）", "♎ Libra Ingress (Autumnal Equinox)"): "libra",
            auto_cn("♑ 摩羯入宮（冬至）", "♑ Capricorn Ingress (Winter Solstice)"): "capricorn",
        }
        ingress_label = st.selectbox(
            auto_cn("入宮類型", "Ingress Type"),
            options=list(ingress_options.keys()),
            key="mundane_ingress_type",
        )
        ingress_type = ingress_options[ingress_label]

    with col3:
        house_system_opts = {
            auto_cn("整宮制", "Whole Sign"): "W",
            "Placidus": "P",
        }
        hs_label = st.selectbox(
            auto_cn("宮位制", "House System"),
            options=list(house_system_opts.keys()),
            key="mundane_ingress_hs",
        )
        house_system = house_system_opts[hs_label]

    # Location selection
    st.divider()
    loc_col1, loc_col2 = st.columns([2, 1])

    with loc_col1:
        country_opts = [auto_cn("全球視角（赤道）", "Global View (Equatorial)")] + list(COUNTRY_CAPITALS.keys())
        selected_country = st.selectbox(
            auto_cn("地點 / 國家", "Location / Country"),
            options=country_opts,
            key="mundane_ingress_country",
            help=auto_cn(
                "選擇國家後，宮位制將以該國首都計算，影響星盤宮位分布。",
                "Select a country to calculate houses from its capital's coordinates."
            ),
        )

    with loc_col2:
        sidereal = st.checkbox(
            auto_cn("恆星黃道（Lahiri）", "Sidereal (Lahiri)"),
            key="mundane_ingress_sidereal",
            value=False,
        )

    if selected_country == auto_cn("全球視角（赤道）", "Global View (Equatorial)"):
        lat, lon, loc_name = 0.0, 0.0, auto_cn("全球視角", "Global View")
    else:
        country_data = COUNTRY_CAPITALS.get(selected_country)
        if country_data:
            name_zh, lat, lon, _tz = country_data
            loc_name = f"{name_zh} ({selected_country})"
        else:
            lat, lon, loc_name = 0.0, 0.0, selected_country

    # Compute chart with spinner
    with st.spinner(auto_cn("計算入宮圖中…", "Computing ingress chart…")):
        try:
            chart = compute_ingress_chart(
                year=ingress_year,
                ingress_type=ingress_type,
                latitude=lat,
                longitude=lon,
                location_name=loc_name,
                house_system=house_system,
                sidereal=sidereal,
            )
        except Exception as e:
            st.error(f"計算失敗 / Calculation failed: {e}")
            return

    # Display chart
    st.subheader(
        auto_cn(
            f"🌟 {chart.year} 年 {chart.chart_type_label_zh}",
            f"🌟 {chart.year} {chart.chart_type_label_en}"
        )
    )
    st.caption(
        auto_cn(
            f"📅 {chart.utc_datetime.strftime('%Y年%m月%d日 %H:%M')} UTC  "
            f"📍 {loc_name}  |  宮位：{hs_label}",
            f"📅 {chart.utc_datetime.strftime('%Y-%m-%d %H:%M')} UTC  "
            f"📍 {loc_name}  |  Houses: {hs_label}"
        )
    )

    chart_col, info_col = st.columns([1, 1])

    with chart_col:
        svg = _build_mundane_svg(chart)
        st.markdown(
            f'<div class="mundane-chart-container">{svg}</div>',
            unsafe_allow_html=True,
        )

    with info_col:
        _render_planet_table(chart)

    st.divider()
    _render_aspects(chart)
    st.divider()
    _render_house_interpretations(chart)
    st.divider()
    _render_ingress_ai_button(chart)


def _render_planet_table(chart: MundaneChart) -> None:
    """Render a styled planet position table."""
    st.markdown(auto_cn("#### 🪐 行星位置", "#### 🪐 Planet Positions"))

    import pandas as pd

    rows = []
    for name, pl in chart.planets.items():
        retro = "℞" if pl.is_retrograde else ""
        rows.append({
            auto_cn("符號", "Glyph"): pl.glyph,
            auto_cn("行星", "Planet"): f"{pl.name_zh} / {name}",
            auto_cn("位置", "Position"): f"{pl.degree_in_sign:.1f}° {pl.sign_en} {pl.sign_glyph}",
            auto_cn("宮位", "House"): pl.house if pl.house > 0 else "-",
            auto_cn("逆行", "Retro"): retro,
        })

    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def _render_aspects(chart: MundaneChart) -> None:
    """Render the aspects section."""
    st.markdown(auto_cn("#### 🔗 主要相位", "#### 🔗 Major Aspects"))

    if not chart.aspects:
        st.info(auto_cn("此星盤中無主要相位。", "No major aspects found in this chart."))
        return

    import pandas as pd

    rows = []
    for asp in sorted(chart.aspects, key=lambda a: a.orb):
        apply = auto_cn("趨近 ▲", "Applying ▲") if asp.applying else auto_cn("離散 ▼", "Separating ▼")
        p1 = chart.planets.get(asp.planet1)
        p2 = chart.planets.get(asp.planet2)
        g1 = p1.glyph if p1 else ""
        g2 = p2.glyph if p2 else ""
        rows.append({
            auto_cn("行星 1", "Planet 1"): f"{g1} {asp.planet1}",
            auto_cn("相位", "Aspect"): f"{asp.aspect_name} ({asp.aspect_zh})",
            auto_cn("行星 2", "Planet 2"): f"{g2} {asp.planet2}",
            auto_cn("容許度", "Orb"): f"{asp.orb:.2f}°",
            auto_cn("狀態", "Status"): apply,
        })

    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def _render_house_interpretations(chart: MundaneChart) -> None:
    """Render a simplified house interpretation guide."""
    st.markdown(auto_cn("#### 🏛️ 宮位世俗象徵", "#### 🏛️ House Mundane Significations"))

    occupied_houses: Dict[int, List[str]] = {}
    for name, pl in chart.planets.items():
        if pl.house > 0:
            occupied_houses.setdefault(pl.house, []).append(f"{pl.glyph} {name}")

    cols = st.columns(2)
    for h in range(1, 13):
        house_info = MUNDANE_HOUSES.get(h, {})
        planets_in_house = occupied_houses.get(h, [])
        meaning = auto_cn(house_info.get("zh", ""), house_info.get("en", ""))
        planet_str = "、".join(planets_in_house) if planets_in_house else auto_cn("（空宮）", "(empty)")

        with cols[(h - 1) % 2]:
            st.markdown(
                f'<div class="house-card">'
                f'<span class="house-number">第 {h} 宮</span>'
                f'<span class="house-planet"> · {planet_str}</span><br/>'
                f'<span class="house-meaning">{meaning}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


def _render_ingress_ai_button(chart: MundaneChart) -> None:
    """Render the AI analysis button for the Ingress chart."""
    try:
        from astro.ai_analysis import format_chart_for_prompt
    except ImportError:
        return

    st.markdown(auto_cn("#### 🤖 AI 欽天監解讀", "#### 🤖 AI Celestial Analysis"))

    from .constants import MUNDANE_AI_PERSONA_ZH, MUNDANE_AI_PERSONA_EN
    persona = auto_cn(MUNDANE_AI_PERSONA_ZH, MUNDANE_AI_PERSONA_EN)
    prompt_text = format_mundane_chart_for_prompt(chart)

    if st.button(
        auto_cn("✨ 請欽天監星官解讀此入宮圖", "✨ Request Imperial Astrologer Reading"),
        key="mundane_ingress_ai_btn",
    ):
        st.session_state["mundane_ai_prompt"] = prompt_text
        st.session_state["mundane_ai_persona"] = persona

    if "mundane_ai_prompt" in st.session_state:
        _run_mundane_ai_chat(
            st.session_state.get("mundane_ai_prompt", ""),
            st.session_state.get("mundane_ai_persona", persona),
        )


def _run_mundane_ai_chat(prompt: str, persona: str) -> None:
    """Run a single-turn AI analysis for Mundane chart data."""
    try:
        import os
        from astro.ai_analysis import CerebrasClient, OpenAIClient, DEFAULT_MODEL

        api_key = (
            os.environ.get("CEREBRAS_API_KEY", "")
            or st.session_state.get("cerebras_api_key", "")
        )
        openai_key = (
            os.environ.get("OPENAI_API_KEY", "")
            or st.session_state.get("openai_api_key", "")
        )

        if not api_key and not openai_key:
            st.info(auto_cn(
                "💡 請在 AI 設定中輸入 API Key 以啟用 AI 解讀。",
                "💡 Enter your AI API key in the AI settings to enable analysis."
            ))
            return

        with st.spinner(auto_cn("欽天監星官推算中…", "The Imperial Astrologer is consulting the stars…")):
            if api_key:
                client = CerebrasClient(api_key=api_key)
                messages = [
                    {"role": "system", "content": persona},
                    {"role": "user", "content": prompt},
                ]
                response = client.chat(messages=messages, model=DEFAULT_MODEL)
            else:
                client = OpenAIClient(api_key=openai_key)
                messages = [
                    {"role": "system", "content": persona},
                    {"role": "user", "content": prompt},
                ]
                response = client.chat(messages=messages, model="gpt-4o-mini")

        st.markdown(
            f'<div class="mundane-card">'
            f'<div class="mundane-card-title">🌟 欽天監星官解讀</div>'
            f'{response}</div>',
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.warning(auto_cn(f"AI 解讀暫時不可用：{e}", f"AI analysis temporarily unavailable: {e}"))


# ─────────────────────────────────────────────────────────────────────────────
# Sub-render: Eclipse Chart tab  日月食分頁
# ─────────────────────────────────────────────────────────────────────────────

def _render_eclipse_tab() -> None:
    """Render the Eclipse Chart tab."""
    st.markdown(
        auto_cn(
            "**日月食（Eclipse）**是世俗占星的重要天象。"
            "日食影響長達 6 個月至 1 年，月食影響約 1 個月。"
            "食發生的星座與宮位揭示國家、地區的重要事件。",
            "**Eclipses** are critical Mundane events. Solar eclipses effect change for "
            "6 months to a year; lunar eclipses for about a month. "
            "The sign and house of the eclipse reveals key national and regional themes."
        )
    )

    ecl_col1, ecl_col2, ecl_col3 = st.columns(3)
    with ecl_col1:
        ecl_year = st.number_input(
            auto_cn("搜尋年份", "Search Year"),
            min_value=1900, max_value=2100,
            value=datetime.now().year,
            key="mundane_ecl_year",
        )
    with ecl_col2:
        ecl_month = st.number_input(
            auto_cn("搜尋月份", "Search Month"),
            min_value=1, max_value=12,
            value=datetime.now().month,
            key="mundane_ecl_month",
        )
    with ecl_col3:
        ecl_kind = st.selectbox(
            auto_cn("日食 / 月食", "Solar / Lunar"),
            options=[auto_cn("日食 ☉", "Solar ☉"), auto_cn("月食 ☽", "Lunar ☽")],
            key="mundane_ecl_kind",
        )

    eclipse_kind = "solar" if auto_cn("日食", "Solar") in ecl_kind else "lunar"

    # Location
    ecl_loc = st.selectbox(
        auto_cn("地點 / 國家", "Location / Country"),
        options=[auto_cn("全球視角", "Global View")] + list(COUNTRY_CAPITALS.keys()),
        key="mundane_ecl_country",
    )

    if ecl_loc == auto_cn("全球視角", "Global View"):
        ecl_lat, ecl_lon, ecl_loc_name = 0.0, 0.0, "Global"
    else:
        cd = COUNTRY_CAPITALS.get(ecl_loc)
        if cd:
            name_zh, ecl_lat, ecl_lon, _tz = cd
            ecl_loc_name = f"{name_zh} ({ecl_loc})"
        else:
            ecl_lat, ecl_lon, ecl_loc_name = 0.0, 0.0, ecl_loc

    with st.spinner(auto_cn("搜尋日月食中…", "Searching for eclipse…")):
        try:
            eclipse_info, chart = compute_eclipse_chart(
                year=ecl_year, month=ecl_month,
                eclipse_kind=eclipse_kind,
                latitude=ecl_lat, longitude=ecl_lon,
                location_name=ecl_loc_name,
                house_system="W",
            )
        except Exception as e:
            st.error(f"計算失敗 / Calculation failed: {e}")
            return

    # Display eclipse info card
    kind_label = auto_cn("日食", "Solar Eclipse") if eclipse_kind == "solar" else auto_cn("月食", "Lunar Eclipse")
    type_label = auto_cn(eclipse_info.eclipse_type_zh, eclipse_info.eclipse_type_en)
    dt_str = eclipse_info.utc_datetime.strftime("%Y-%m-%d %H:%M UTC")

    sign_en = eclipse_info.sign_en
    sign_zh = eclipse_info.sign_zh
    deg_in_sign = eclipse_info.longitude % 30

    st.markdown(
        f'<div class="eclipse-card">'
        f'<div class="mundane-card-title">🌑 {type_label} {kind_label}</div>'
        f'<p style="color:#A8B8D0; margin:4px 0">📅 {dt_str}</p>'
        f'<p style="color:#C8A951; margin:4px 0">📍 {deg_in_sign:.1f}° {sign_en} ({sign_zh})</p>'
        f'<p style="color:#8899BB; margin:4px 0">🏙️ {ecl_loc_name}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # SVG wheel
    ecl_chart_col, ecl_info_col = st.columns([1, 1])
    with ecl_chart_col:
        if chart:
            svg = _build_mundane_svg(chart)
            st.markdown(
                f'<div class="mundane-chart-container">{svg}</div>',
                unsafe_allow_html=True,
            )
    with ecl_info_col:
        if chart:
            _render_planet_table(chart)

    if chart:
        st.divider()
        _render_aspects(chart)


# ─────────────────────────────────────────────────────────────────────────────
# Sub-render: Great Conjunctions tab  木土大合相分頁
# ─────────────────────────────────────────────────────────────────────────────

def _render_conjunctions_tab() -> None:
    """Render the Great Conjunctions timeline tab."""
    st.markdown(
        auto_cn(
            "**木土大合相（Great Conjunction）**每約 20 年發生一次，"
            "標誌時代的重大轉折。2020 年合相進入風象三角（寶瓶座），"
            "開啟資訊、民主、科技新紀元，終結 200 年土象（工業物質）時代。",
            "**The Great Conjunction** of Jupiter and Saturn occurs roughly every 20 years, "
            "marking major historical turning points. The 2020 conjunction entered Air signs "
            "(Aquarius), opening a new era of information, democracy, and technology, "
            "ending 200 years of the Earth (industrial) cycle."
        )
    )

    # Element cycle explanation
    with st.expander(auto_cn("📚 元素週期說明", "📚 Element Cycle Explanation"), expanded=False):
        for elem, desc in ELEMENT_CYCLE_DESCRIPTIONS.items():
            elem_icons = {"Fire": "🔥", "Earth": "🌍", "Air": "💨", "Water": "💧"}
            ico = elem_icons.get(elem, "✦")
            st.markdown(
                f"**{ico} {elem}**: {auto_cn(desc['zh'], desc['en'])}"
            )

    # Year range filter
    range_col1, range_col2 = st.columns(2)
    with range_col1:
        start_yr = st.number_input(
            auto_cn("起始年份", "Start Year"),
            min_value=1800, max_value=2060,
            value=1900, step=20,
            key="gc_start_year",
        )
    with range_col2:
        end_yr = st.number_input(
            auto_cn("結束年份", "End Year"),
            min_value=1820, max_value=2070,
            value=2065, step=20,
            key="gc_end_year",
        )

    conjunctions = get_great_conjunctions_timeline(start_year=start_yr, end_year=end_yr)

    if not conjunctions:
        st.info(auto_cn("此區間無記錄。", "No conjunctions in this range."))
        return

    # Plotly timeline chart
    try:
        import plotly.graph_objects as go

        _elem_plot_colors = {
            "Fire":  "#C94B2A",
            "Earth": "#8B6333",
            "Air":   "#2A8B8B",
            "Water": "#2A4A8B",
        }
        _elem_plot_names = {
            "Fire":  auto_cn("火象", "Fire"),
            "Earth": auto_cn("土象", "Earth"),
            "Air":   auto_cn("風象", "Air"),
            "Water": auto_cn("水象", "Water"),
        }

        fig = go.Figure()

        today_year = datetime.now().year

        # Group by element
        from collections import defaultdict
        by_element: Dict[str, List[GreatConjunction]] = defaultdict(list)
        for gc in conjunctions:
            by_element[gc.element].append(gc)

        for elem, gcs in by_element.items():
            color = _elem_plot_colors.get(elem, "#AAAAAA")
            years = [gc.year for gc in gcs]
            signs = [f"{SIGN_GLYPHS[gc.sign_index]} {gc.sign_zh}" for gc in gcs]
            notes = [auto_cn(gc.notes_zh, gc.notes_en) for gc in gcs]
            marker_symbols = ["circle" if not gc.is_future else "star" for gc in gcs]
            sizes = [18 if not gc.is_future else 22 for gc in gcs]

            fig.add_trace(go.Scatter(
                x=years,
                y=[gc.longitude for gc in gcs],
                mode="markers+text",
                name=_elem_plot_names.get(elem, elem),
                marker=dict(
                    symbol=marker_symbols,
                    size=sizes,
                    color=color,
                    opacity=0.85,
                    line=dict(width=1.5, color="#C8A951"),
                ),
                text=[str(yr) for yr in years],
                textposition="top center",
                textfont=dict(size=10, color=color),
                customdata=list(zip(signs, notes)),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "%{customdata[0]}<br>"
                    "%{customdata[1]}<extra></extra>"
                ),
            ))

        # Today line
        fig.add_vline(
            x=today_year,
            line_dash="dash",
            line_color="#C8A951",
            line_width=1.5,
            annotation_text=auto_cn("今日", "Today"),
            annotation_font_color="#C8A951",
        )

        fig.update_layout(
            title=dict(
                text=auto_cn("木土大合相時間軸 (Jupiter–Saturn Great Conjunctions)", "Jupiter–Saturn Great Conjunctions Timeline"),
                font=dict(color="#C8A951", size=14),
            ),
            paper_bgcolor="#050a14",
            plot_bgcolor="#0d1428",
            xaxis=dict(
                title=auto_cn("年份", "Year"),
                color="#7B8DB0",
                gridcolor="#1A2540",
                showgrid=True,
            ),
            yaxis=dict(
                title=auto_cn("合相黃經度數", "Conjunction Longitude (°)"),
                color="#7B8DB0",
                gridcolor="#1A2540",
                range=[0, 360],
                showgrid=True,
            ),
            legend=dict(
                font=dict(color="#E8D8A0"),
                bgcolor="#0d1428",
                bordercolor="#2A3A5A",
            ),
            height=400,
            margin=dict(l=40, r=40, t=50, b=40),
        )

        st.plotly_chart(fig, width="stretch")

    except ImportError:
        st.warning("Plotly not available for timeline chart.")

    # Conjunction cards
    st.divider()
    st.markdown(auto_cn("#### 📋 合相詳表", "#### 📋 Conjunction Detail List"))

    for gc in conjunctions:
        is_future = gc.is_future
        css_class = "conj-item conj-future" if is_future else "conj-item"
        future_tag = auto_cn("（預測）", "(Projected)") if is_future else ""
        elem_icon = {"Fire": "🔥", "Earth": "🌍", "Air": "💨", "Water": "💧"}.get(gc.element, "✦")
        note = auto_cn(gc.notes_zh, gc.notes_en)

        st.markdown(
            f'<div class="{css_class}">'
            f'<span class="conj-year">{gc.year} {future_tag}</span> '
            f'<span class="conj-sign">{elem_icon} {SIGN_GLYPHS[gc.sign_index]} {gc.sign_zh} ({gc.sign_en}), '
            f'{gc.longitude:.1f}°</span><br/>'
            f'<span class="conj-note">{note}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Sub-render: National Overview tab  國家運勢總覽分頁
# ─────────────────────────────────────────────────────────────────────────────

def _render_national_tab() -> None:
    """Render the National / World Overview tab."""
    st.markdown(
        auto_cn(
            "選擇國家，查看當前外行星在該國星盤中的位置與象徵，"
            "結合年度入宮圖分析國家的時代運勢。",
            "Select a country to view current outer planet positions in its "
            "national chart, combined with the annual ingress for a macro-level reading."
        )
    )

    nat_col1, nat_col2 = st.columns([2, 1])
    with nat_col1:
        nat_country = st.selectbox(
            auto_cn("選擇國家", "Select Country"),
            options=list(COUNTRY_CAPITALS.keys()),
            key="mundane_nat_country",
        )
    with nat_col2:
        nat_year = st.number_input(
            auto_cn("年份", "Year"),
            min_value=1800, max_value=2100,
            value=datetime.now().year,
            key="mundane_nat_year",
        )

    country_data = COUNTRY_CAPITALS.get(nat_country)
    if not country_data:
        st.error(auto_cn("找不到國家資料。", "Country data not found."))
        return

    name_zh, lat, lon, tz = country_data

    # Outer planet overview
    st.divider()
    st.markdown(auto_cn("#### 🌍 當前外行星概況", "#### 🌍 Current Outer Planet Overview"))

    try:
        today = datetime.now()
        outer = compute_current_outer_planets(today.year, today.month, today.day)

        import pandas as pd
        rows = []
        for pname, pl in outer.items():
            theme = OUTER_PLANET_THEMES.get(pname, {})
            theme_text = auto_cn(theme.get("zh", ""), theme.get("en", ""))
            retro = "℞" if pl.is_retrograde else ""
            rows.append({
                auto_cn("行星", "Planet"): f"{pl.glyph} {pl.name_zh} / {pname}",
                auto_cn("位置", "Position"): f"{pl.degree_in_sign:.1f}° {pl.sign_en} {pl.sign_glyph} {retro}",
                auto_cn("星座", "Sign"): pl.sign_zh,
                auto_cn("象徵主題", "Mundane Theme"): theme_text,
            })

        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    except Exception as e:
        st.warning(f"{e}")

    # National Aries Ingress
    st.divider()
    st.markdown(
        auto_cn(
            f"#### {SIGN_GLYPHS[0]} {name_zh} {nat_year} 年牡羊入宮圖",
            f"#### {SIGN_GLYPHS[0]} {nat_country} — {nat_year} Aries Ingress"
        )
    )

    with st.spinner(auto_cn("計算國家入宮圖中…", "Computing national ingress…")):
        try:
            nat_chart = compute_national_mundane(
                year=nat_year,
                country_key=nat_country,
                country_data=country_data,
                ingress_type="aries",
                house_system="W",
            )
        except Exception as e:
            st.error(f"計算失敗 / Calculation failed: {e}")
            return

    ncol1, ncol2 = st.columns([1, 1])
    with ncol1:
        svg = _build_mundane_svg(nat_chart)
        st.markdown(
            f'<div class="mundane-chart-container">{svg}</div>',
            unsafe_allow_html=True,
        )
    with ncol2:
        _render_planet_table(nat_chart)
        _render_ingress_ai_button(nat_chart)

    # World map: country highlight
    try:
        import plotly.graph_objects as go

        fig = go.Figure()

        # Mark all capitals as small dots
        all_lats = [v[1] for v in COUNTRY_CAPITALS.values()]
        all_lons = [v[2] for v in COUNTRY_CAPITALS.values()]
        all_names = [v[0] for v in COUNTRY_CAPITALS.values()]

        fig.add_trace(go.Scattergeo(
            lat=all_lats, lon=all_lons,
            text=all_names,
            mode="markers",
            marker=dict(size=5, color="#2A3A5A", opacity=0.5),
            hovertemplate="%{text}<extra></extra>",
        ))

        # Highlight selected country
        fig.add_trace(go.Scattergeo(
            lat=[lat], lon=[lon],
            text=[name_zh],
            mode="markers+text",
            marker=dict(size=14, color="#C8A951", opacity=0.9,
                        line=dict(width=2, color="#FFD700")),
            textposition="top right",
            textfont=dict(color="#C8A951", size=12),
            hovertemplate=f"{name_zh}<extra></extra>",
        ))

        fig.update_geos(
            projection_type="natural earth",
            showland=True, landcolor="#0d1428",
            showocean=True, oceancolor="#050a14",
            showcountries=True, countrycolor="#2A3A5A",
            showframe=False,
            bgcolor="#050a14",
        )
        fig.update_layout(
            paper_bgcolor="#050a14",
            margin=dict(l=0, r=0, t=30, b=0),
            height=320,
            title=dict(
                text=auto_cn(f"📍 {name_zh}", f"📍 {nat_country}"),
                font=dict(color="#C8A951"),
            ),
            showlegend=False,
        )

        st.plotly_chart(fig, width="stretch")

    except ImportError:
        st.caption(auto_cn("需要 Plotly 才能顯示世界地圖。", "Plotly required for world map."))


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point  主入口
# ─────────────────────────────────────────────────────────────────────────────

def render_streamlit(
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    hour: Optional[int] = None,
    minute: Optional[int] = None,
    timezone: Optional[float] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    location_name: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Main Streamlit renderer for the Mundane Astrology module.

    Called from app.py when tab_mundane is selected.
    Session state birth parameters are accepted as optional overrides
    but Mundane charts primarily use their own independent controls.
    """
    # Inject CSS
    st.markdown(_MUNDANE_CSS, unsafe_allow_html=True)

    # Header
    st.markdown(
        '<div class="mundane-header">'
        '<div class="mundane-title">🌍 Mundane Astrology · 世俗占星</div>'
        '<div class="mundane-subtitle">'
        'National & World Astrology · 國家占星 · 世界占星 · 時代脈動'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Main tabs
    tab_ingress, tab_eclipse, tab_conjunctions, tab_national = st.tabs([
        auto_cn("♈ 入宮圖", "♈ Ingress Chart"),
        auto_cn("🌑 日月食", "🌑 Eclipses"),
        auto_cn("♃♄ 木土大合相", "♃♄ Great Conjunctions"),
        auto_cn("🌍 國家運勢", "🌍 National Overview"),
    ])

    with tab_ingress:
        _render_ingress_tab()

    with tab_eclipse:
        _render_eclipse_tab()

    with tab_conjunctions:
        _render_conjunctions_tab()

    with tab_national:
        _render_national_tab()
