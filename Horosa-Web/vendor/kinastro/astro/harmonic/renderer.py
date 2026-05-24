"""
astro/harmonic/renderer.py — Streamlit UI + SVG Mandala for Harmonic Astrology

Renders a professional Harmonic Astrology interface with:
  - Sacred Geometry / Mandala SVG charts per harmonic
  - Multi-harmonic comparative analysis view
  - John Addey tradition bilingual interpretations
  - AI analysis integration
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import streamlit as st

from .calculator import (
    HarmonicChart,
    HarmonicConjunction,
    HarmonicPlanet,
    MultiHarmonicResult,
    NatalPlanet,
    compute_harmonic_chart,
    compute_multi_harmonic,
)
from .constants import (
    HARMONIC_DEFS,
    PLANET_NAMES_EN,
    PLANET_NAMES_ZH,
    PLANET_SYMBOLS,
    PLANET_ORDER,
    SUPPORTED_HARMONICS,
)
from astro.i18n import auto_cn, get_ui_lang, t


# ──────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────

_CSS = """
<style>
.harmonic-header {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    border-left: 4px solid #a78bfa;
    padding: 14px 20px;
    border-radius: 8px;
    margin-bottom: 14px;
}
.harmonic-card {
    background: rgba(167, 139, 250, 0.08);
    border: 1px solid rgba(167, 139, 250, 0.25);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
}
.harmonic-conj-tight {
    background: rgba(16, 185, 129, 0.12);
    border-left: 3px solid #10b981;
    border-radius: 5px;
    padding: 8px 14px;
    margin-bottom: 6px;
}
.harmonic-conj-normal {
    background: rgba(99, 102, 241, 0.10);
    border-left: 3px solid #6366f1;
    border-radius: 5px;
    padding: 8px 14px;
    margin-bottom: 6px;
}
.harmonic-note {
    background: rgba(245, 158, 11, 0.08);
    border: 1px dashed rgba(245, 158, 11, 0.35);
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 0.90em;
    color: #fcd34d;
    margin: 10px 0;
}
.harmonic-theme {
    font-size: 1.05em;
    color: #c4b5fd;
    font-weight: 600;
    margin-bottom: 6px;
}
.harmonic-orb-tight { color: #34d399; font-weight: bold; }
.harmonic-orb-normal { color: #93c5fd; }
.harmonic-emphasis-row {
    display: inline-block;
    background: rgba(139, 92, 246, 0.15);
    border-radius: 12px;
    padding: 3px 10px;
    margin: 2px 3px;
    font-size: 0.88em;
}
</style>
"""


# ──────────────────────────────────────────────────────────────
# SVG Mandala rendering
# ──────────────────────────────────────────────────────────────

def _polar_to_xy(cx: float, cy: float, r: float, angle_deg: float) -> Tuple[float, float]:
    """Convert polar coordinates to SVG x,y.  0° = top (12 o'clock), clockwise."""
    rad = math.radians(angle_deg - 90.0)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def _svg_planet_marker(
    cx: float, cy: float, r: float,
    lon: float, symbol: str, color: str, r_text: float,
    size: float = 9.0,
    glow_color: str = "",
) -> str:
    """Render a planet marker (circle + symbol) on a given ring at longitude."""
    x, y = _polar_to_xy(cx, cy, r, lon)
    xt, yt = _polar_to_xy(cx, cy, r_text, lon)
    glow = f'filter="url(#glow)"' if glow_color else ""
    dot = (
        f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{size:.1f}" '
        f'fill="{color}" opacity="0.92" {glow}/>'
    )
    label = (
        f'<text x="{xt:.2f}" y="{yt:.2f}" text-anchor="middle" '
        f'dominant-baseline="middle" font-size="11" fill="{color}" '
        f'font-family="serif" font-weight="bold">{symbol}</text>'
    )
    return dot + label


def _svg_conjunction_arc(
    cx: float, cy: float, r: float,
    lon_a: float, lon_b: float, color: str, width: float = 1.5,
    opacity: float = 0.55,
) -> str:
    """Draw a line between two conjunction planets on the mandala."""
    x1, y1 = _polar_to_xy(cx, cy, r, lon_a)
    x2, y2 = _polar_to_xy(cx, cy, r, lon_b)
    return (
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke="{color}" stroke-width="{width:.1f}" opacity="{opacity:.2f}" '
        f'stroke-dasharray="4,3"/>'
    )


def _svg_sacred_petals(
    cx: float, cy: float, r: float,
    n: int, color: str, opacity: float = 0.12,
) -> str:
    """
    Draw N-fold sacred geometry petals as background decoration.
    Each petal is an arc from the center to the ring.
    """
    if n <= 1:
        return ""
    parts = []
    for i in range(n):
        angle = (360.0 / n) * i
        x1, y1 = _polar_to_xy(cx, cy, r * 0.5, angle)
        x2, y2 = _polar_to_xy(cx, cy, r, angle)
        parts.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" stroke-width="1" opacity="{opacity:.2f}"/>'
        )
    return "".join(parts)


def _svg_polygon(
    cx: float, cy: float, r: float, n: int,
    color: str, fill_opacity: float = 0.04,
    stroke_opacity: float = 0.20,
) -> str:
    """Draw a regular N-gon for sacred geometry background."""
    if n < 3:
        return ""
    pts = []
    for i in range(n):
        angle = (360.0 / n) * i
        x, y = _polar_to_xy(cx, cy, r, angle)
        pts.append(f"{x:.2f},{y:.2f}")
    pts_str = " ".join(pts)
    return (
        f'<polygon points="{pts_str}" fill="{color}" fill-opacity="{fill_opacity:.2f}" '
        f'stroke="{color}" stroke-width="1" stroke-opacity="{stroke_opacity:.2f}"/>'
    )


def _svg_degree_ticks(cx: float, cy: float, r_outer: float, color: str) -> str:
    """Draw fine degree tick marks around the outer ring."""
    parts = []
    for deg in range(0, 360, 10):
        r_inner = r_outer - (4 if deg % 30 == 0 else 2)
        x1, y1 = _polar_to_xy(cx, cy, r_inner, deg)
        x2, y2 = _polar_to_xy(cx, cy, r_outer, deg)
        parts.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" stroke-width="0.8" opacity="0.35"/>'
        )
    return "".join(parts)


def render_harmonic_chart_svg(
    chart: HarmonicChart,
    width: int = 440,
    show_natal_ring: bool = True,
) -> str:
    """
    Render a beautiful Sacred Geometry Mandala SVG for a Harmonic Chart.

    Design language:
      - Deep space background with harmonic-specific color theme
      - N-fold sacred geometry polygon and petal pattern
      - Outer ring: harmonic chart positions
      - Inner ring (optional): natal positions for comparison
      - Conjunction lines connecting close planets
      - Degree tick marks and sign boundary markers
      - Glow filter for planet markers

    Args:
        chart: The HarmonicChart to visualize.
        width: SVG width in pixels (height = width).
        show_natal_ring: Whether to draw the inner natal comparison ring.

    Returns:
        SVG string suitable for direct use with st.html() or st.markdown().
    """
    n = chart.harmonic_number
    hdef = HARMONIC_DEFS.get(n, {})
    color_primary = hdef.get("color_primary", "#a78bfa")
    color_secondary = hdef.get("color_secondary", "#c4b5fd")
    color_bg = hdef.get("color_bg", "#0f0c29")
    petals = hdef.get("petals", n)

    cx = cy = width / 2.0
    r_outer = width * 0.42
    r_tick = r_outer + 6
    r_planet = r_outer - 14
    r_planet_label = r_outer - 32
    r_natal = r_outer * 0.62 if show_natal_ring else 0.0
    r_natal_label = r_natal - 16
    r_polygon = r_outer * 0.75

    # ── Glow filter
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{width}" '
        f'viewBox="0 0 {width} {width}">',
        '<defs>',
        f'<filter id="glow" x="-40%" y="-40%" width="180%" height="180%">',
        f'<feGaussianBlur stdDeviation="3" result="blur"/>',
        f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
        '</filter>',
        f'<radialGradient id="bgGrad" cx="50%" cy="50%" r="50%">',
        f'<stop offset="0%" stop-color="{color_bg}" stop-opacity="1"/>',
        f'<stop offset="100%" stop-color="#000005" stop-opacity="1"/>',
        '</radialGradient>',
        '</defs>',
        # Background
        f'<rect width="{width}" height="{width}" fill="url(#bgGrad)"/>',
    ]

    # ── Outer glow ring
    svg_parts.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_outer:.1f}" '
        f'fill="none" stroke="{color_primary}" stroke-width="1.5" opacity="0.5"/>'
    )
    # ── Inner decorative rings
    for frac, op in [(0.85, 0.20), (0.70, 0.15), (0.55, 0.10)]:
        svg_parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_outer*frac:.1f}" '
            f'fill="none" stroke="{color_secondary}" stroke-width="0.8" opacity="{op}"/>'
        )

    # ── Sacred geometry: N-gon + petals
    if petals >= 3:
        svg_parts.append(_svg_polygon(cx, cy, r_polygon, petals, color_primary, 0.04, 0.18))
    svg_parts.append(_svg_sacred_petals(cx, cy, r_outer * 0.90, petals, color_secondary, 0.10))

    # ── Degree ticks
    svg_parts.append(_svg_degree_ticks(cx, cy, r_tick, color_secondary))

    # ── Sign boundary lines (12 divisions)
    for sign_i in range(12):
        angle = sign_i * 30.0
        x1, y1 = _polar_to_xy(cx, cy, r_outer * 0.50, angle)
        x2, y2 = _polar_to_xy(cx, cy, r_outer, angle)
        svg_parts.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color_primary}" stroke-width="0.6" opacity="0.22"/>'
        )

    # ── Natal comparison ring (inner)
    if show_natal_ring and r_natal > 0:
        svg_parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_natal:.1f}" '
            f'fill="none" stroke="#ffffff" stroke-width="0.8" opacity="0.15" stroke-dasharray="3,4"/>'
        )
        for np_ in chart.natal_planets:
            if np_.key in ("AS", "MC", "NN"):
                continue
            x, y = _polar_to_xy(cx, cy, r_natal, np_.natal_longitude)
            svg_parts.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" '
                f'fill="#888" opacity="0.45"/>'
            )

    # ── Conjunction lines (draw before planets so they go behind)
    conj_color_tight = "#34d399"
    conj_color_normal = color_secondary
    h_planets_map = {hp.key: hp for hp in chart.harmonic_planets}
    for conj in chart.conjunctions:
        pa = h_planets_map.get(conj.planet_a)
        pb = h_planets_map.get(conj.planet_b)
        if pa and pb:
            is_tight = conj.harmonic_orb < chart.conjunction_orb * 0.4
            c = conj_color_tight if is_tight else conj_color_normal
            svg_parts.append(_svg_conjunction_arc(
                cx, cy, r_planet, pa.harmonic_longitude, pb.harmonic_longitude,
                c, width=1.8 if is_tight else 1.2, opacity=0.65 if is_tight else 0.45,
            ))

    # ── Planet markers on outer ring
    # Planets involved in conjunctions get a glow
    conj_keys: set[str] = set()
    for conj in chart.conjunctions:
        conj_keys.add(conj.planet_a)
        conj_keys.add(conj.planet_b)

    for hp in chart.harmonic_planets:
        in_conj = hp.key in conj_keys
        color = color_primary if in_conj else "#666688"
        glow = color_primary if in_conj else ""
        svg_parts.append(_svg_planet_marker(
            cx, cy, r_planet, hp.harmonic_longitude,
            hp.symbol, color, r_planet_label,
            size=9.0 if in_conj else 6.0,
            glow_color=glow,
        ))

    # ── Center label
    svg_parts.append(
        f'<text x="{cx:.1f}" y="{cy - 10:.1f}" text-anchor="middle" '
        f'font-size="22" fill="{color_primary}" font-family="serif" '
        f'font-weight="bold" opacity="0.90">H{n}</text>'
    )
    svg_parts.append(
        f'<text x="{cx:.1f}" y="{cy + 12:.1f}" text-anchor="middle" '
        f'font-size="10" fill="{color_secondary}" font-family="sans-serif" '
        f'opacity="0.75">{len(chart.conjunctions)} conjunctions</text>'
    )

    svg_parts.append('</svg>')
    return "".join(svg_parts)


def render_multi_harmonic_summary_svg(
    result: MultiHarmonicResult,
    harmonics: Optional[List[int]] = None,
    width: int = 600,
) -> str:
    """
    Render a summary mandala showing multiple harmonics in a grid layout.

    Each mini-mandala represents one harmonic, showing the conjunction
    activity as a visual intensity indicator.
    """
    if harmonics is None:
        harmonics = [h for h in SUPPORTED_HARMONICS if h in result.harmonic_charts]

    cols = min(4, len(harmonics))
    rows = math.ceil(len(harmonics) / cols)
    cell_size = width // cols
    height = cell_size * rows + 40

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#050510"/>',
    ]

    for idx, n in enumerate(harmonics):
        row = idx // cols
        col = idx % cols
        x_off = col * cell_size
        y_off = row * cell_size

        chart = result.harmonic_charts.get(n)
        hdef = HARMONIC_DEFS.get(n, {})
        color_p = hdef.get("color_primary", "#a78bfa")
        color_s = hdef.get("color_secondary", "#c4b5fd")

        cx = x_off + cell_size / 2
        cy = y_off + cell_size / 2
        r = cell_size * 0.36
        n_conj = len(chart.conjunctions) if chart else 0

        # Mini ring
        svg_parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="none" stroke="{color_p}" stroke-width="1.2" opacity="0.5"/>'
        )

        # Sacred geometry mini polygon
        if n >= 3 and chart:
            pts = []
            for i in range(n):
                angle = (360.0 / n) * i
                x, y = _polar_to_xy(cx, cy, r * 0.7, angle)
                pts.append(f"{x:.1f},{y:.1f}")
            svg_parts.append(
                f'<polygon points="{" ".join(pts)}" fill="{color_p}" '
                f'fill-opacity="0.05" stroke="{color_p}" stroke-width="0.8" stroke-opacity="0.20"/>'
            )

        # Planet dots
        if chart:
            conj_keys: set[str] = set()
            for conj in chart.conjunctions:
                conj_keys.add(conj.planet_a)
                conj_keys.add(conj.planet_b)

            for hp in chart.harmonic_planets:
                in_conj = hp.key in conj_keys
                dot_r = 4.0 if in_conj else 2.5
                clr = color_p if in_conj else "#444466"
                x, y = _polar_to_xy(cx, cy, r - 8, hp.harmonic_longitude)
                svg_parts.append(
                    f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{dot_r:.1f}" fill="{clr}" opacity="0.85"/>'
                )

            # Conjunction lines
            h_map = {hp.key: hp for hp in chart.harmonic_planets}
            for conj in chart.conjunctions:
                pa = h_map.get(conj.planet_a)
                pb = h_map.get(conj.planet_b)
                if pa and pb:
                    x1, y1 = _polar_to_xy(cx, cy, r - 8, pa.harmonic_longitude)
                    x2, y2 = _polar_to_xy(cx, cy, r - 8, pb.harmonic_longitude)
                    svg_parts.append(
                        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                        f'stroke="{color_s}" stroke-width="1" opacity="0.45" stroke-dasharray="2,2"/>'
                    )

        # H-number label
        svg_parts.append(
            f'<text x="{cx:.1f}" y="{cy - 5:.1f}" text-anchor="middle" '
            f'font-size="18" fill="{color_p}" font-family="serif" font-weight="bold">H{n}</text>'
        )
        svg_parts.append(
            f'<text x="{cx:.1f}" y="{cy + 10:.1f}" text-anchor="middle" '
            f'font-size="9" fill="{color_s}" font-family="sans-serif">{n_conj} conj</text>'
        )

    svg_parts.append('</svg>')
    return "".join(svg_parts)


# ──────────────────────────────────────────────────────────────
# Streamlit renderer
# ──────────────────────────────────────────────────────────────

def _fmt_lon(lon: float) -> str:
    """Format a longitude as deg°min'."""
    d = int(lon)
    m = int((lon - d) * 60)
    return f"{d:03d}°{m:02d}′"


def _lang() -> str:
    return "zh" if get_ui_lang() in ("zh", "zh_cn") else "en"


def _render_single_harmonic(chart: HarmonicChart) -> None:
    """Render a single harmonic chart UI."""
    lang = _lang()
    n = chart.harmonic_number
    hdef = HARMONIC_DEFS.get(n, {})
    color_primary = hdef.get("color_primary", "#a78bfa")

    # Header
    name = chart.name_zh if lang == "zh" else chart.name_en
    theme = chart.theme_zh if lang == "zh" else chart.theme_en
    st.markdown(
        f'<div class="harmonic-header">'
        f'<div style="font-size:1.3em;font-weight:700;color:{color_primary}">✦ {name}</div>'
        f'<div class="harmonic-theme">{theme}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Addey note
    note = chart.addey_note_zh if lang == "zh" else chart.addey_note_en
    st.markdown(
        f'<div class="harmonic-note">📖 <b>John Addey</b>：{note}</div>',
        unsafe_allow_html=True,
    )

    col_svg, col_info = st.columns([1, 1])

    with col_svg:
        svg = render_harmonic_chart_svg(chart, width=380)
        st.html(svg)

    with col_info:
        # Planet positions table
        data = []
        for hp in chart.harmonic_planets:
            n_name = hp.name_zh if lang == "zh" else hp.name_en
            retro = " ℞" if hp.retrograde else ""
            natal_fmt = _fmt_lon(hp.natal_longitude)
            harm_fmt = _fmt_lon(hp.harmonic_longitude)
            sign_disp = f"{hp.sign_symbol} {hp.sign_zh if lang == 'zh' else hp.sign}"
            data.append({
                auto_cn("行星", "Planet"): f"{hp.symbol} {n_name}{retro}",
                auto_cn("本命", "Natal"): natal_fmt,
                auto_cn(f"H{n}位置", f"H{n} Pos"): harm_fmt,
                auto_cn("星座", "Sign"): sign_disp,
            })

        import pandas as pd
        df = pd.DataFrame(data)
        st.dataframe(df, width="stretch")

    # Conjunctions
    st.markdown(
        f'<div style="font-size:1.05em;font-weight:600;color:{color_primary};margin:14px 0 8px">',
        unsafe_allow_html=True,
    )
    conj_title = auto_cn(f"H{n} 合相（{len(chart.conjunctions)}）", f"H{n} Conjunctions ({len(chart.conjunctions)})")
    st.markdown(f"#### {conj_title}")

    if not chart.conjunctions:
        st.info(auto_cn("此諧波盤中無合相（在容許度內）。", "No conjunctions found within orb."))
    else:
        for conj in chart.conjunctions:
            pa_name = PLANET_NAMES_ZH.get(conj.planet_a, conj.planet_a) if lang == "zh" else PLANET_NAMES_EN.get(conj.planet_a, conj.planet_a)
            pb_name = PLANET_NAMES_ZH.get(conj.planet_b, conj.planet_b) if lang == "zh" else PLANET_NAMES_EN.get(conj.planet_b, conj.planet_b)
            pa_sym = PLANET_SYMBOLS.get(conj.planet_a, conj.planet_a)
            pb_sym = PLANET_SYMBOLS.get(conj.planet_b, conj.planet_b)
            orb_deg = int(conj.harmonic_orb)
            orb_min = int((conj.harmonic_orb - orb_deg) * 60)

            is_tight = conj.harmonic_orb < chart.conjunction_orb * 0.4
            css_class = "harmonic-conj-tight" if is_tight else "harmonic-conj-normal"
            orb_class = "harmonic-orb-tight" if is_tight else "harmonic-orb-normal"
            tight_label = auto_cn("【緊密】", "【Tight】") if is_tight else ""

            meaning = conj.meaning_zh if lang == "zh" else conj.meaning_en

            orb_label = auto_cn(f"容許度 {orb_deg}°{orb_min}′", f"orb {orb_deg}°{orb_min}′")
            if tight_label:
                orb_display = f"{tight_label} {orb_label}"
            else:
                orb_display = orb_label

            st.markdown(
                f'<div class="{css_class}">'
                f'<b>{pa_sym} {pa_name} ☌ {pb_sym} {pb_name}</b> '
                f'<span class="{orb_class}">{orb_display}</span>'
                f'<br/><small>{meaning}</small>'
                f'</div>',
                unsafe_allow_html=True,
            )


def _render_multi_harmonic(result: MultiHarmonicResult, harmonics: List[int]) -> None:
    """Render multi-harmonic comparative analysis."""
    lang = _lang()

    st.markdown(
        f'<div class="harmonic-header">'
        f'<div style="font-size:1.2em;font-weight:700;color:#a78bfa">✦ '
        f'{auto_cn("多諧波綜合分析", "Multi-Harmonic Comparative Analysis")}</div>'
        f'<div style="font-size:0.9em;color:#c4b5fd;margin-top:4px">'
        f'{auto_cn("Hamblin 方法：識別跨諧波行星重點", "Hamblin method: identifying multi-harmonic planetary emphasis")}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # Summary mandala grid
    available = [h for h in harmonics if h in result.harmonic_charts]
    if available:
        svg = render_multi_harmonic_summary_svg(result, available, width=580)
        st.html(svg)

    # Planet emphasis
    st.markdown(
        f"#### {auto_cn('多諧波行星重點（Hamblin）', 'Multi-Harmonic Planetary Emphasis (Hamblin)')}"
    )
    st.markdown(
        f'<div class="harmonic-note">'
        f'{auto_cn("出現在更多諧波合相中的行星，具有更強的主題性才能或靈性品質（David Hamblin，1983）。", "Planets appearing in conjunctions across more harmonics carry stronger thematic gifts or spiritual qualities (David Hamblin, 1983).")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    for emp in result.multi_emphasis:
        key = emp["key"]
        harmonics_list = emp["harmonics_active"]
        count = emp["count"]
        p_name = PLANET_NAMES_ZH.get(key, key) if lang == "zh" else PLANET_NAMES_EN.get(key, key)
        p_sym = PLANET_SYMBOLS.get(key, key)
        h_tags = " ".join(
            f'<span class="harmonic-emphasis-row" style="color:{HARMONIC_DEFS.get(h, {}).get("color_primary", "#a78bfa")}">H{h}</span>'
            for h in harmonics_list
        )
        bar_width = min(100, count * 12)
        st.markdown(
            f'<div class="harmonic-card">'
            f'<b>{p_sym} {p_name}</b> — '
            f'{auto_cn(f"活躍於 {count} 個諧波", f"Active in {count} harmonics")} '
            f'{h_tags}'
            f'<div style="margin-top:4px;height:4px;background:rgba(167,139,250,0.15);border-radius:2px;">'
            f'<div style="width:{bar_width}%;height:100%;background:#a78bfa;border-radius:2px;opacity:0.7"></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    # Per-harmonic summary
    st.markdown(f"#### {auto_cn('各諧波合相摘要', 'Per-Harmonic Conjunction Summary')}")
    cols = st.columns(min(4, len(available)))
    for i, n in enumerate(available):
        chart = result.harmonic_charts[n]
        hdef = HARMONIC_DEFS.get(n, {})
        color = hdef.get("color_primary", "#a78bfa")
        name = chart.name_zh if lang == "zh" else chart.name_en
        with cols[i % len(cols)]:
            st.markdown(
                f'<div class="harmonic-card" style="text-align:center;">'
                f'<div style="font-size:1.5em;font-weight:700;color:{color}">H{n}</div>'
                f'<div style="font-size:0.8em;color:#888">{name}</div>'
                f'<div style="font-size:1.3em;color:{color};margin-top:4px">{len(chart.conjunctions)}</div>'
                f'<div style="font-size:0.78em;color:#999">{auto_cn("合相", "conjunctions")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_harmonic(
    result,
    harmonic_selection: Optional[List[int]] = None,
) -> None:
    """
    Main Streamlit renderer for the Harmonic Astrology module.

    Args:
        result: Either HarmonicChart (single) or MultiHarmonicResult (multi).
        harmonic_selection: For MultiHarmonicResult, which harmonics to display.
    """
    st.html(_CSS)

    if isinstance(result, HarmonicChart):
        _render_single_harmonic(result)
    elif isinstance(result, MultiHarmonicResult):
        harmonics = harmonic_selection or [h for h in SUPPORTED_HARMONICS if h in result.harmonic_charts]

        # Top-level tabs: Multi-view + individual harmonics
        tab_labels = [auto_cn("📊 綜合分析", "📊 Multi-Analysis")]
        for n in harmonics:
            hdef = HARMONIC_DEFS.get(n, {})
            label = f"H{n}"
            tab_labels.append(label)

        tabs = st.tabs(tab_labels)

        with tabs[0]:
            _render_multi_harmonic(result, harmonics)

        for i, n in enumerate(harmonics):
            with tabs[i + 1]:
                chart = result.harmonic_charts.get(n)
                if chart:
                    _render_single_harmonic(chart)
