"""
astro/horary/renderer.py — Horary Astrology Streamlit Renderer & SVG Chart Generator

Renders both Western (Lilly/Bonatti) and Vedic (Prashna Marga) horary charts.
Visual style: 17th-century astrological manuscript aesthetic with antique parchment quality.

Sources:
- William Lilly, "Christian Astrology" (1647) frontispiece and woodcut illustrations
- Traditional Indian Jyotish chart formats (North Indian / South Indian)
- Medieval European astrological manuscript art
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import streamlit as st

from astro.i18n import auto_cn, get_lang, t
from .calculator import (
    WesternHoraryChart,
    VedicPrashnaChart,
    HoraryPlanet,
    HoraryAspect,
    compute_western_horary,
    compute_vedic_prashna,
)
from .constants import (
    PLANET_GLYPHS, PLANET_CN,
    ZODIAC_SIGNS, SIGN_NAMES,
    QUESTION_TYPES, PRASHNA_QUESTION_TYPES,
    ASPECT_DEFINITIONS,
)

# ============================================================
# CSS — Antique Manuscript Aesthetic
# ============================================================

_HORARY_CSS = """
<style>
/* ── Horary Module Global Styles ────────────────────────────── */
.horary-header {
    background: linear-gradient(135deg, #0D1B2A 0%, #1B2D4A 50%, #2A3F62 100%);
    border: 1px solid #3D5A80;
    border-left: 6px solid #A78BFA;
    padding: 18px 24px;
    border-radius: 8px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.horary-header::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='6' height='6'%3E%3Crect width='6' height='6' fill='%230D1B2A'/%3E%3Ccircle cx='1' cy='1' r='0.6' fill='%23A78BFA' opacity='0.06'/%3E%3C/svg%3E");
    pointer-events: none;
}
.horary-header h2 { color: #C4B5FD; margin: 0 0 4px 0; font-size: 1.5em; font-family: serif; }
.horary-header p  { color: #93A8C4; margin: 0; font-size: 0.88em; font-style: italic; }

.horary-section {
    background: rgba(123,78,190,0.06);
    border: 1px solid rgba(123,78,190,0.20);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 14px;
}
.horary-section h4 { color: #A78BFA; margin: 0 0 10px 0; font-family: serif; letter-spacing: 0.04em; }

.stricture-warning {
    background: rgba(220,80,40,0.12);
    border-left: 4px solid #E05A3A;
    border-radius: 4px;
    padding: 8px 14px;
    margin-bottom: 8px;
    color: #F4A07C;
}
.stricture-caution {
    background: rgba(234,179,8,0.10);
    border-left: 4px solid #EAB308;
    border-radius: 4px;
    padding: 8px 14px;
    margin-bottom: 8px;
    color: #F0D080;
}
.stricture-info {
    background: rgba(42,157,143,0.10);
    border-left: 4px solid #2A9D8F;
    border-radius: 4px;
    padding: 8px 14px;
    margin-bottom: 8px;
    color: #7ECFC8;
}

.verdict-yes {
    background: rgba(42,157,143,0.15);
    border: 2px solid #2A9D8F;
    border-radius: 8px;
    padding: 12px 20px;
    color: #7ECFC8;
    font-size: 1.1em;
    font-family: serif;
    font-weight: bold;
    text-align: center;
}
.verdict-no {
    background: rgba(155,34,38,0.15);
    border: 2px solid #9B2226;
    border-radius: 8px;
    padding: 12px 20px;
    color: #F08898;
    font-size: 1.1em;
    font-family: serif;
    font-weight: bold;
    text-align: center;
}
.verdict-unclear {
    background: rgba(167,139,250,0.12);
    border: 2px solid #7B4EBE;
    border-radius: 8px;
    padding: 12px 20px;
    color: #C4B5FD;
    font-size: 1.1em;
    font-family: serif;
    font-weight: bold;
    text-align: center;
}

.planet-row {
    display: flex;
    align-items: center;
    padding: 4px 8px;
    border-radius: 4px;
    margin-bottom: 4px;
    background: rgba(13,27,42,0.6);
    border: 1px solid rgba(61,90,128,0.35);
    font-family: monospace;
    font-size: 0.88em;
}
.planet-strong { border-left: 3px solid #2A9D8F; }
.planet-weak   { border-left: 3px solid #9B2226; }
.planet-neutral{ border-left: 3px solid #7B4EBE; }

.judgment-text {
    background: rgba(13,27,42,0.80);
    border: 1px solid rgba(61,90,128,0.50);
    border-radius: 8px;
    padding: 16px 20px;
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 0.9em;
    line-height: 1.7;
    color: #C8D8EA;
    white-space: pre-wrap;
}

.arudha-box {
    background: linear-gradient(135deg, rgba(123,78,190,0.20), rgba(42,63,98,0.30));
    border: 1px solid rgba(167,139,250,0.35);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    font-style: italic;
    color: #C4B5FD;
}

.classical-quote {
    border-left: 3px solid #A78BFA;
    padding: 6px 12px;
    margin: 8px 0;
    font-style: italic;
    color: #93A8C4;
    font-size: 0.88em;
    font-family: Georgia, serif;
}
</style>
"""


# ============================================================
# SVG: Western Horary Chart
# ============================================================

def render_western_horary_svg(chart: WesternHoraryChart) -> str:
    """
    Render a traditional Western Horary chart as SVG.

    Style: 17th-century astrological manuscript / Lilly-era woodcut aesthetic.
    Circular chart with 12 houses, planets placed at proper positions,
    aspects drawn as coloured lines, antique parchment background.

    Returns an SVG string suitable for st.markdown() / components.html().
    """
    W, H = 560, 560
    cx, cy = W // 2, H // 2
    R_outer = 240
    R_inner = 165
    R_planet = 200

    # Parchment colours
    bg_colour = "#F4E9C8"
    paper_mid = "#E8D5A0"
    ink_dark = "#2C1A00"
    ink_gold = "#8B5E00"
    ink_red = "#8B1A00"
    circle_colour = "#5C3A00"
    text_colour = "#1E0C00"

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" font-family="Georgia,serif">',

        # ── Background parchment ────────────────────────────────────
        f'<defs>',
        f'  <radialGradient id="parchment" cx="50%" cy="45%" r="60%">',
        f'    <stop offset="0%" stop-color="#F8F0D4"/>',
        f'    <stop offset="70%" stop-color="#EDE0B0"/>',
        f'    <stop offset="100%" stop-color="#D4C080"/>',
        f'  </radialGradient>',
        f'  <filter id="paper-texture" x="-5%" y="-5%" width="110%" height="110%">',
        f'    <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" '
        f'      stitchTiles="stitch" result="noise"/>',
        f'    <feColorMatrix type="saturate" values="0" in="noise" result="grey"/>',
        f'    <feBlend in="SourceGraphic" in2="grey" mode="multiply" result="blend"/>',
        f'    <feComposite in="blend" in2="SourceGraphic" operator="in"/>',
        f'  </filter>',
        f'  <filter id="ink-blur">',
        f'    <feGaussianBlur stdDeviation="0.3"/>',
        f'  </filter>',
        f'</defs>',

        # Outer border
        f'<rect width="{W}" height="{H}" rx="12" ry="12" fill="url(#parchment)" '
        f'stroke="{circle_colour}" stroke-width="3" filter="url(#paper-texture)"/>',

        # Decorative outer frame (double border)
        f'<rect x="8" y="8" width="{W-16}" height="{H-16}" rx="8" ry="8" '
        f'fill="none" stroke="{ink_gold}" stroke-width="1.2" opacity="0.6"/>',
        f'<rect x="12" y="12" width="{W-24}" height="{H-24}" rx="6" ry="6" '
        f'fill="none" stroke="{ink_dark}" stroke-width="0.5" opacity="0.3"/>',

        # ── Outer circle (zodiac band) ──────────────────────────────
        f'<circle cx="{cx}" cy="{cy}" r="{R_outer}" fill="none" '
        f'stroke="{circle_colour}" stroke-width="1.8"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{R_outer - 20}" fill="none" '
        f'stroke="{circle_colour}" stroke-width="0.8"/>',

        # ── Inner house circle ──────────────────────────────────────
        f'<circle cx="{cx}" cy="{cy}" r="{R_inner}" fill="rgba(244,233,200,0.7)" '
        f'stroke="{circle_colour}" stroke-width="1.5"/>',

        # ── Center circle (horizon / cross) ────────────────────────
        f'<circle cx="{cx}" cy="{cy}" r="24" fill="rgba(244,233,200,0.9)" '
        f'stroke="{ink_gold}" stroke-width="1"/>',
    ]

    # ── Draw zodiac signs band ──────────────────────────────────────
    SIGN_GLYPHS = [s[1] for s in ZODIAC_SIGNS]
    SIGN_COLOURS = {
        "Fire":  "#8B1A00",
        "Earth": "#5C3A00",
        "Air":   "#1A3A5C",
        "Water": "#0A3B5C",
    }

    for i in range(12):
        # Place sign i at its ecliptic position.
        # In standard Western chart: ASC = 9 o'clock (left / 180° in SVG coords),
        # so sign_angle = 180 - (ecl - asc) when measured from the SVG origin.
        asc_angle_deg = chart.ascendant
        sign_ecl = i * 30.0 + 15.0  # midpoint of sign i on ecliptic
        svg_angle_rad = math.radians(180.0 - (sign_ecl - asc_angle_deg))
        mid_r = (R_outer + R_outer - 20) / 2
        gx = cx + mid_r * math.cos(svg_angle_rad)
        gy = cy - mid_r * math.sin(svg_angle_rad)
        elem = ZODIAC_SIGNS[i][3]
        c = SIGN_COLOURS.get(elem, ink_dark)
        svg_parts.append(
            f'<text x="{gx:.1f}" y="{gy:.1f}" text-anchor="middle" dominant-baseline="central" '
            f'font-size="15" fill="{c}" font-weight="bold" opacity="0.85">'
            f'{SIGN_GLYPHS[i]}</text>'
        )

    # ── Draw house dividers ─────────────────────────────────────────
    for i, cusp in enumerate(chart.house_cusps):
        ecl = cusp
        svg_angle_rad = math.radians(180.0 - (ecl - chart.ascendant))
        x1 = cx + R_inner * math.cos(svg_angle_rad)
        y1 = cy - R_inner * math.sin(svg_angle_rad)
        x2 = cx + (R_outer - 20) * math.cos(svg_angle_rad)
        y2 = cy - (R_outer - 20) * math.sin(svg_angle_rad)

        is_angle_house = (i in (0, 3, 6, 9))
        lw = "1.8" if is_angle_house else "0.9"
        lc = ink_dark if is_angle_house else circle_colour
        svg_parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{lc}" stroke-width="{lw}" opacity="0.8"/>'
        )

        # House number label
        next_cusp = chart.house_cusps[(i + 1) % 12]
        mid_ecl = ecl + _angular_diff_mid(ecl, next_cusp)
        mid_rad = math.radians(180.0 - (mid_ecl - chart.ascendant))
        hx = cx + (R_inner + 18) * math.cos(mid_rad)
        hy = cy - (R_inner + 18) * math.sin(mid_rad)
        svg_parts.append(
            f'<text x="{hx:.1f}" y="{hy:.1f}" text-anchor="middle" dominant-baseline="central" '
            f'font-size="9" fill="{ink_gold}" font-style="italic" opacity="0.7">{i+1}</text>'
        )

    # ── ASC / MC / DSC / IC markers ─────────────────────────────────
    for label, ecl in [("ASC", chart.ascendant),
                        ("MC",  chart.midheaven),
                        ("DSC", (chart.ascendant + 180) % 360),
                        ("IC",  (chart.midheaven + 180) % 360)]:
        svg_angle_rad = math.radians(180.0 - (ecl - chart.ascendant))
        x1 = cx + R_inner * math.cos(svg_angle_rad)
        y1 = cy - R_inner * math.sin(svg_angle_rad)
        x2 = cx + R_outer * math.cos(svg_angle_rad)
        y2 = cy - R_outer * math.sin(svg_angle_rad)
        tx = cx + (R_outer + 16) * math.cos(svg_angle_rad)
        ty = cy - (R_outer + 16) * math.sin(svg_angle_rad)
        svg_parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{ink_red}" stroke-width="2" opacity="0.9"/>'
        )
        svg_parts.append(
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" dominant-baseline="central" '
            f'font-size="9" fill="{ink_red}" font-weight="bold" font-family="serif">{label}</text>'
        )

    # ── Aspects ──────────────────────────────────────────────────────
    planet_xy: Dict[str, tuple] = {}
    for p in chart.planets:
        ecl = p.longitude
        svg_angle_rad = math.radians(180.0 - (ecl - chart.ascendant))
        px = cx + R_planet * math.cos(svg_angle_rad)
        py = cy - R_planet * math.sin(svg_angle_rad)
        planet_xy[p.name] = (px, py)

    ASPECT_COLOURS = {
        "trine":       "#1A6E28",  # green — benefic
        "sextile":     "#1A4E8E",  # blue — benefic
        "conjunction": "#5C3A00",  # dark gold — neutral
        "square":      "#8B1A00",  # dark red — malefic
        "opposition":  "#6B0000",  # deep red — malefic
        "quincunx":    "#5C5C00",  # olive — neutral
    }

    for asp in chart.aspects[:12]:  # limit to top 12 aspects for clarity
        if asp.planet1 in planet_xy and asp.planet2 in planet_xy:
            x1, y1 = planet_xy[asp.planet1]
            x2, y2 = planet_xy[asp.planet2]
            colour = ASPECT_COLOURS.get(asp.aspect_name.split(" ")[0].lower(),
                                         "#8B691466")
            dash = "4,3" if not asp.is_applying else "none"
            opacity = "0.7" if asp.is_applying else "0.35"
            svg_parts.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{colour}" stroke-width="1" stroke-dasharray="{dash}" '
                f'opacity="{opacity}"/>'
            )

    # ── Planets ──────────────────────────────────────────────────────
    PLANET_ELEM_COLOURS = {
        "Sun":     "#B8860B",
        "Moon":    "#708090",
        "Mercury": "#2E4A8E",
        "Venus":   "#8B2252",
        "Mars":    "#8B1A00",
        "Jupiter": "#1A5C1A",
        "Saturn":  "#3A2800",
    }

    for p in chart.planets:
        ecl = p.longitude
        svg_angle_rad = math.radians(180.0 - (ecl - chart.ascendant))
        px = cx + R_planet * math.cos(svg_angle_rad)
        py = cy - R_planet * math.sin(svg_angle_rad)
        glyph = PLANET_GLYPHS.get(p.name, p.name[0])
        pc = PLANET_ELEM_COLOURS.get(p.name, ink_dark)

        # Highlight significators
        is_querent = (p.name == chart.asc_lord)
        is_quesited = (p.name == chart.judgment.quesited_significator)

        # Background circle for the planet
        if is_querent or is_quesited:
            ring_c = "#C5A03F" if is_querent else "#8B1A00"
            svg_parts.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="13" '
                f'fill="rgba(244,233,200,0.9)" stroke="{ring_c}" stroke-width="2"/>'
            )
        else:
            svg_parts.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="11" '
                f'fill="rgba(244,233,200,0.85)" stroke="{circle_colour}" stroke-width="1"/>'
            )

        # Planet glyph
        fs = "14" if is_querent or is_quesited else "12"
        svg_parts.append(
            f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" font-size="{fs}" fill="{pc}" '
            f'font-weight="bold">{glyph}</text>'
        )

        # Retrograde marker
        if p.retrograde:
            svg_parts.append(
                f'<text x="{px + 9:.1f}" y="{py - 8:.1f}" font-size="7" '
                f'fill="{ink_red}" font-style="italic">℞</text>'
            )

        # Degree label
        deg_str = f"{int(p.degree_in_sign)}°"
        label_r = R_planet + 22
        lx = cx + label_r * math.cos(svg_angle_rad)
        ly = cy - label_r * math.sin(svg_angle_rad)
        svg_parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" font-size="8" fill="{ink_gold}" '
            f'opacity="0.8">{deg_str}</text>'
        )

    # ── Void of Course Moon indicator ────────────────────────────────
    if chart.moon_voc.is_voc:
        voc_text = "VOC" if not chart.moon_voc.has_exception else "VOC*"
        voc_colour = ink_red if not chart.moon_voc.has_exception else ink_gold
        svg_parts.append(
            f'<text x="{cx}" y="{cy + 36}" text-anchor="middle" '
            f'font-size="11" fill="{voc_colour}" font-style="italic" '
            f'font-family="serif">{voc_text}</text>'
        )

    # ── Title and question ───────────────────────────────────────────
    q_preview = chart.question_text[:45] + "…" if len(chart.question_text) > 45 else chart.question_text
    svg_parts.extend([
        f'<text x="{cx}" y="22" text-anchor="middle" font-size="12" '
        f'fill="{ink_dark}" font-family="serif" font-weight="bold" font-style="italic" opacity="0.9">'
        f'Horary Astrology</text>',
        f'<text x="{cx}" y="37" text-anchor="middle" font-size="8.5" '
        f'fill="{ink_gold}" font-family="serif" opacity="0.8">'
        f'{_xml_escape(q_preview)}</text>',
        f'<text x="{cx}" y="{H-14}" text-anchor="middle" font-size="8" '
        f'fill="{ink_gold}" opacity="0.6" font-family="serif" font-style="italic">'
        f'{_xml_escape(chart.question_datetime)} · {_xml_escape(chart.location_name)}</text>',
    ])

    # ── Chart center decoration ──────────────────────────────────────
    svg_parts.append(
        f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
        f'font-size="20" fill="{ink_gold}" opacity="0.25" font-family="serif">✦</text>'
    )

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def _angular_diff_mid(start: float, end: float) -> float:
    """Return half the angular distance from start to end (going forward)."""
    diff = (end - start) % 360.0
    return diff / 2.0


def _xml_escape(s: str) -> str:
    """Escape XML/SVG special characters."""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;"))


# ============================================================
# SVG: Vedic Prashna Chart (North Indian style)
# ============================================================

def render_vedic_prashna_svg(
    chart: VedicPrashnaChart,
    style: str = "north_indian",
) -> str:
    """
    Render a Vedic Prashna chart as SVG.

    style: "north_indian" (diamond grid) or "south_indian" (square grid)

    North Indian style: traditional diamond grid with Lagna at top-centre.
    Features antique Indian manuscript aesthetic — warm ochre tones, Sanskrit-style glyphs.

    Returns SVG string.
    """
    if style == "south_indian":
        return _render_south_indian_prashna_svg(chart)
    return _render_north_indian_prashna_svg(chart)


def _render_north_indian_prashna_svg(chart: VedicPrashnaChart) -> str:
    """North Indian style Prashna SVG — traditional diamond grid."""
    W, H = 520, 540
    cx, cy = W // 2, H // 2 - 10

    # Antique Indian manuscript palette
    bg_colour = "#FAF0DC"
    border_colour = "#8B4A00"
    ink_colour = "#2C0D00"
    gold_colour = "#A0680A"
    red_colour = "#8B1A00"
    blue_colour = "#1A3060"

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" font-family="serif">',

        # Parchment background
        f'<defs>',
        f'  <linearGradient id="vp-bg" x1="0%" y1="0%" x2="100%" y2="100%">',
        f'    <stop offset="0%" stop-color="#FDF5E4"/>',
        f'    <stop offset="50%" stop-color="#F5E8C4"/>',
        f'    <stop offset="100%" stop-color="#E8D4A0"/>',
        f'  </linearGradient>',
        f'  <filter id="vp-texture">',
        f'    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" '
        f'      stitchTiles="stitch" result="noise"/>',
        f'    <feColorMatrix in="noise" type="saturate" values="0.2" result="colorNoise"/>',
        f'    <feBlend in="SourceGraphic" in2="colorNoise" mode="multiply"/>',
        f'  </filter>',
        f'</defs>',

        f'<rect width="{W}" height="{H}" rx="8" ry="8" fill="url(#vp-bg)" '
        f'stroke="{border_colour}" stroke-width="3"/>',
        f'<rect x="6" y="6" width="{W-12}" height="{H-12}" rx="5" ry="5" '
        f'fill="none" stroke="{gold_colour}" stroke-width="1" opacity="0.5"/>',
    ]

    # ── North Indian diamond grid ─────────────────────────────────
    # Grid: 4x4 squares, centre 2x2 is empty (contains the "lagna cross")
    # Houses: Top=1, TopRight=2, Right=3, BotRight=4, Bot=5, BotLeft=6,
    #         Left=7, TopLeft=8 (outer); inner corners: TopRight=9...

    sq = 110  # grid unit size
    grid_x0 = cx - sq * 2  # left start
    grid_y0 = cy - sq * 2  # top start

    # Draw the 4x4 grid lines
    for row in range(5):
        y = grid_y0 + row * sq
        svg_parts.append(
            f'<line x1="{grid_x0}" y1="{y}" x2="{grid_x0 + 4*sq}" y2="{y}" '
            f'stroke="{border_colour}" stroke-width="1.2" opacity="0.7"/>'
        )
    for col in range(5):
        x = grid_x0 + col * sq
        svg_parts.append(
            f'<line x1="{x}" y1="{grid_y0}" x2="{x}" y2="{grid_y0 + 4*sq}" '
            f'stroke="{border_colour}" stroke-width="1.2" opacity="0.7"/>'
        )

    # Diagonal lines in four corner cells
    # Top-left triangle
    for (r, c) in [(0,0),(0,3),(3,0),(3,3)]:
        x0 = grid_x0 + c * sq
        y0 = grid_y0 + r * sq
        # diagonal across 2x2
        if r == 0 and c == 0:
            svg_parts.append(
                f'<line x1="{x0}" y1="{y0}" x2="{x0+2*sq}" y2="{y0+2*sq}" '
                f'stroke="{border_colour}" stroke-width="0.9" opacity="0.5"/>'
            )
        elif r == 0 and c == 3:
            svg_parts.append(
                f'<line x1="{x0+sq}" y1="{y0}" x2="{x0-sq}" y2="{y0+2*sq}" '
                f'stroke="{border_colour}" stroke-width="0.9" opacity="0.5"/>'
            )
        elif r == 3 and c == 0:
            svg_parts.append(
                f'<line x1="{x0}" y1="{y0+sq}" x2="{x0+2*sq}" y2="{y0-sq}" '
                f'stroke="{border_colour}" stroke-width="0.9" opacity="0.5"/>'
            )
        elif r == 3 and c == 3:
            svg_parts.append(
                f'<line x1="{x0+sq}" y1="{y0+sq}" x2="{x0-sq}" y2="{y0-sq}" '
                f'stroke="{border_colour}" stroke-width="0.9" opacity="0.5"/>'
            )

    # ── House positions in North Indian grid ──────────────────────
    # Lagna = top-centre cell (col 1-2, row 0)
    # Houses go clockwise from top-centre
    # Cell centres for each house (1-12):
    asc_sign_idx = chart.house_signs[0].lower() if chart.house_signs else "mesha"
    # House 1 = Lagna sign; houses fixed, signs rotate
    lagna_idx = [s[0].lower() for s in _VEDIC_RASHIS_LIST()].index(
        chart.asc_sign.lower()
    ) if chart.asc_sign.lower() in [s[0].lower() for s in _VEDIC_RASHIS_LIST()] else 0

    # Cell coordinates (col, row) for houses 1-12 (0-indexed)
    HOUSE_CELLS = [
        (1, 0),  # House 1 — top centre
        (2, 0),  # House 2 — top right
        (3, 0),  # House 3 — right top
        (3, 1),  # House 4 — right mid-top
        (3, 2),  # House 5 — right mid-bot
        (3, 3),  # House 6 — right bot
        (2, 3),  # House 7 — bot right
        (1, 3),  # House 8 — bot left
        (0, 3),  # House 9 — left bot
        (0, 2),  # House 10 — left mid-bot
        (0, 1),  # House 11 — left mid-top
        (0, 0),  # House 12 — left top
    ]

    # Build planet house occupancy
    planet_in_house: Dict[int, List[str]] = {i: [] for i in range(1, 13)}
    for p in chart.planets:
        if 1 <= p.house <= 12:
            planet_in_house[p.house].append(
                f"{_vedic_glyph(p.name)}"
            )

    arudha_house = chart.arudha_lagna.sign_index
    # Compute which house Arudha falls in
    arudha_house_num = ((arudha_house - lagna_idx) % 12) + 1

    for h_idx, (col, row) in enumerate(HOUSE_CELLS):
        house_num = h_idx + 1
        x = grid_x0 + col * sq
        y = grid_y0 + row * sq
        cx_cell = x + sq // 2
        cy_cell = y + sq // 2

        # Sign name for this house
        sign_num = (lagna_idx + h_idx) % 12
        from .constants import VEDIC_RASHIS
        sign_info = VEDIC_RASHIS[sign_num]

        # Highlight Lagna cell
        if house_num == 1:
            svg_parts.append(
                f'<rect x="{x+2}" y="{y+2}" width="{sq-4}" height="{sq-4}" '
                f'fill="rgba(160,104,10,0.12)" stroke="{gold_colour}" stroke-width="1.5" '
                f'stroke-dasharray="4,2" rx="2"/>'
            )

        # Arudha Lagna highlight
        if house_num == arudha_house_num:
            svg_parts.append(
                f'<rect x="{x+4}" y="{y+4}" width="{sq-8}" height="{sq-8}" '
                f'fill="rgba(139,26,0,0.07)" stroke="{red_colour}" stroke-width="1" '
                f'stroke-dasharray="3,3" rx="2" opacity="0.7"/>'
            )
            svg_parts.append(
                f'<text x="{cx_cell}" y="{y+16}" text-anchor="middle" '
                f'font-size="7.5" fill="{red_colour}" font-style="italic">AL</text>'
            )

        # House number (small, corner)
        svg_parts.append(
            f'<text x="{x+8}" y="{y+14}" text-anchor="start" '
            f'font-size="9" fill="{gold_colour}" opacity="0.6">{house_num}</text>'
        )

        # Sign glyph and name
        svg_parts.append(
            f'<text x="{cx_cell}" y="{cy_cell - 14}" text-anchor="middle" '
            f'font-size="16" fill="{ink_colour}" opacity="0.7">{sign_info[1]}</text>'
        )
        svg_parts.append(
            f'<text x="{cx_cell}" y="{cy_cell + 3}" text-anchor="middle" '
            f'font-size="8" fill="{ink_colour}" opacity="0.55">{sign_info[0][:4]}</text>'
        )

        # Planets in this house
        planets_here = planet_in_house.get(house_num, [])
        if planets_here:
            ptext = " ".join(planets_here[:4])
            svg_parts.append(
                f'<text x="{cx_cell}" y="{cy_cell + 22}" text-anchor="middle" '
                f'font-size="11" fill="{blue_colour}" font-weight="bold">{ptext}</text>'
            )

    # Centre cross (Lagna marker)
    cross_x, cross_y = grid_x0 + 2 * sq, grid_y0 + 2 * sq
    svg_parts.append(
        f'<circle cx="{cross_x}" cy="{cross_y}" r="32" '
        f'fill="rgba(250,240,220,0.9)" stroke="{gold_colour}" stroke-width="1.5"/>'
    )
    svg_parts.append(
        f'<text x="{cross_x}" y="{cross_y - 6}" text-anchor="middle" '
        f'font-size="11" fill="{ink_colour}" font-family="serif" font-weight="bold">'
        f'प्रश्न</text>'
    )
    svg_parts.append(
        f'<text x="{cross_x}" y="{cross_y + 10}" text-anchor="middle" '
        f'font-size="9" fill="{gold_colour}" font-family="serif">Prashna</text>'
    )

    # ── Title ────────────────────────────────────────────────────────
    q_preview = chart.question_text[:50] + "…" if len(chart.question_text) > 50 else chart.question_text
    svg_parts.extend([
        f'<text x="{W//2}" y="20" text-anchor="middle" font-size="13" '
        f'fill="{ink_colour}" font-family="serif" font-weight="bold" font-style="italic">'
        f'Vedic Prashna</text>',
        f'<text x="{W//2}" y="34" text-anchor="middle" font-size="8.5" '
        f'fill="{gold_colour}" font-family="serif">'
        f'{_xml_escape(q_preview)}</text>',
        f'<text x="{W//2}" y="{H-14}" text-anchor="middle" font-size="8" '
        f'fill="{gold_colour}" opacity="0.65" font-family="serif" font-style="italic">'
        f'{_xml_escape(chart.question_datetime)} · Ayanamsa: {chart.ayanamsa:.2f}°</text>',
    ])

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def _render_south_indian_prashna_svg(chart: VedicPrashnaChart) -> str:
    """South Indian style Prashna SVG — fixed signs, planets and houses move."""
    W, H = 500, 520
    sq = 100  # cell size
    ox = (W - 4 * sq) // 2
    oy = 50

    bg_colour = "#FAF0DC"
    border_colour = "#8B4A00"
    ink_colour = "#2C0D00"
    gold_colour = "#A0680A"
    red_colour = "#8B1A00"

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" font-family="serif">',
        f'<rect width="{W}" height="{H}" rx="8" fill="{bg_colour}" '
        f'stroke="{border_colour}" stroke-width="2.5"/>',
        f'<rect x="5" y="5" width="{W-10}" height="{H-10}" rx="5" '
        f'fill="none" stroke="{gold_colour}" stroke-width="0.8" opacity="0.4"/>',
    ]

    # South Indian layout: signs are fixed in positions
    # Row 0: signs 11(Pisces), 0(Aries), 1(Taurus), 2(Gemini)
    # Row 1: signs 10(Aquarius), [empty], [empty], 3(Cancer)
    # Row 2: signs 9(Capricorn), [empty], [empty], 4(Leo)
    # Row 3: signs 8(Sagittarius), 7(Scorpio), 6(Libra), 5(Virgo)
    SOUTH_LAYOUT = [
        [11,  0,  1,  2],
        [10, -1, -1,  3],
        [ 9, -1, -1,  4],
        [ 8,  7,  6,  5],
    ]

    from .constants import VEDIC_RASHIS
    lagna_idx = 0
    for i, s in enumerate(VEDIC_RASHIS):
        if s[0].lower() == chart.asc_sign.lower():
            lagna_idx = i
            break

    # Which house number is each sign?
    sign_to_house = {(lagna_idx + h) % 12: h + 1 for h in range(12)}

    # Planet occupancy by sign
    planet_in_sign: Dict[int, List[str]] = {i: [] for i in range(12)}
    for p in chart.planets:
        sign_idx = p.sign_index
        if 0 <= sign_idx <= 11:
            planet_in_sign[sign_idx].append(_vedic_glyph(p.name))

    arudha_sign = chart.arudha_lagna.sign_index

    for row in range(4):
        for col in range(4):
            sign_idx = SOUTH_LAYOUT[row][col]
            x = ox + col * sq
            y = oy + row * sq
            cx_cell = x + sq // 2
            cy_cell = y + sq // 2

            if sign_idx < 0:
                # Center cells — empty, draw a light square
                svg_parts.append(
                    f'<rect x="{x}" y="{y}" width="{sq}" height="{sq}" '
                    f'fill="rgba(250,240,220,0.3)" stroke="{border_colour}" '
                    f'stroke-width="0.5" opacity="0.4"/>'
                )
                continue

            sign_info = VEDIC_RASHIS[sign_idx]
            house_num = sign_to_house.get(sign_idx, 0)
            is_lagna = (sign_idx == lagna_idx)
            is_arudha = (sign_idx == arudha_sign)

            fill = "rgba(160,104,10,0.12)" if is_lagna else "rgba(250,240,220,0.6)"
            border_w = "1.8" if is_lagna else "1.0"
            border_c = gold_colour if is_lagna else border_colour

            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{sq}" height="{sq}" '
                f'fill="{fill}" stroke="{border_c}" stroke-width="{border_w}"/>'
            )

            # Lagna marker
            if is_lagna:
                svg_parts.append(
                    f'<line x1="{x}" y1="{y}" x2="{x+18}" y2="{y}" '
                    f'stroke="{gold_colour}" stroke-width="2.5"/>'
                )
                svg_parts.append(
                    f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+18}" '
                    f'stroke="{gold_colour}" stroke-width="2.5"/>'
                )

            # Arudha marker
            if is_arudha:
                svg_parts.append(
                    f'<text x="{x+sq-8}" y="{y+14}" text-anchor="end" '
                    f'font-size="8" fill="{red_colour}" font-style="italic">AL</text>'
                )

            # Sign glyph + name
            svg_parts.append(
                f'<text x="{cx_cell}" y="{cy_cell - 22}" text-anchor="middle" '
                f'font-size="17" fill="{ink_colour}" opacity="0.7">{sign_info[1]}</text>'
            )
            svg_parts.append(
                f'<text x="{cx_cell}" y="{cy_cell - 6}" text-anchor="middle" '
                f'font-size="8.5" fill="{ink_colour}" opacity="0.5">{sign_info[0][:5]}</text>'
            )

            # House number
            svg_parts.append(
                f'<text x="{x+6}" y="{y+14}" font-size="9" '
                f'fill="{gold_colour}" opacity="0.7">{house_num}</text>'
            )

            # Planets
            planets_here = planet_in_sign.get(sign_idx, [])
            if planets_here:
                ptext = "".join(planets_here[:4])
                svg_parts.append(
                    f'<text x="{cx_cell}" y="{cy_cell + 20}" text-anchor="middle" '
                    f'font-size="12" fill="{border_colour}" font-weight="bold">{ptext}</text>'
                )

    # Title
    q_preview = chart.question_text[:50] + "…" if len(chart.question_text) > 50 else chart.question_text
    svg_parts.extend([
        f'<text x="{W//2}" y="22" text-anchor="middle" font-size="13" '
        f'fill="{ink_colour}" font-family="serif" font-weight="bold" font-style="italic">'
        f'Vedic Prashna (South Indian)</text>',
        f'<text x="{W//2}" y="36" text-anchor="middle" font-size="8.5" '
        f'fill="{gold_colour}">{_xml_escape(q_preview)}</text>',
        f'<text x="{W//2}" y="{H-12}" text-anchor="middle" font-size="8" '
        f'fill="{gold_colour}" opacity="0.6" font-style="italic">'
        f'Lagna: {_xml_escape(chart.asc_sign)} · AL: {_xml_escape(chart.arudha_lagna.sign)}</text>',
    ])

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def _vedic_glyph(planet_name: str) -> str:
    """Return a short Vedic abbreviation for the planet."""
    VEDIC_ABBR = {
        "Sun": "Su", "Moon": "Mo", "Mars": "Ma",
        "Mercury": "Me", "Jupiter": "Ju", "Venus": "Ve",
        "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke",
    }
    return VEDIC_ABBR.get(planet_name, planet_name[:2])


def _VEDIC_RASHIS_LIST():
    from .constants import VEDIC_RASHIS
    return VEDIC_RASHIS


# ============================================================
# Streamlit Renderer
# ============================================================

def render_streamlit(
    year: int, month: int, day: int,
    hour: int, minute: int, timezone: float,
    latitude: float, longitude: float,
    location_name: str = "",
    **kwargs
) -> None:
    """
    Main Streamlit renderer for the Horary module.

    Presents tabs for Western Horary and Vedic Prashna.
    """
    st.markdown(_HORARY_CSS, unsafe_allow_html=True)

    lang = get_lang()

    # ── Tradition selector ──────────────────────────────────────────
    west_tab, vedic_tab = st.tabs([
        auto_cn("⚜️ 西方傳統卜卦（Lilly/Bonatti）", "⚜️ Western Horary (Lilly/Bonatti)"),
        auto_cn("🪷 吠陀問卦（Prashna Marga）", "🪷 Vedic Prashna"),
    ])

    with west_tab:
        _render_western_tab(
            year, month, day, hour, minute, timezone,
            latitude, longitude, location_name
        )

    with vedic_tab:
        _render_vedic_tab(
            year, month, day, hour, minute, timezone,
            latitude, longitude, location_name
        )


def _render_western_tab(
    year, month, day, hour, minute, timezone,
    latitude, longitude, location_name
) -> None:
    """Render Western Horary (Lilly/Bonatti) section."""
    lang = get_lang()

    st.markdown(
        '<div class="classical-quote">'
        '"A question is radical, or fit to be judged, when the Lord of the hour at time of the question '
        'is the same as the Lord of the Ascendant." — William Lilly, <em>Christian Astrology</em> p. 121'
        '</div>',
        unsafe_allow_html=True,
    )

    # Question input
    q_text = st.text_area(
        auto_cn("📝 問題（Question）", "📝 Question"),
        placeholder=auto_cn(
            "請輸入您的問題，例如：「我會得到這份工作嗎？」",
            "Enter your horary question, e.g. 'Will I get this job?'"
        ),
        height=80,
        key="horary_west_question",
    )

    q_type = st.selectbox(
        auto_cn("🏷️ 問題類型", "🏷️ Question Type"),
        options=list(QUESTION_TYPES.keys()),
        format_func=lambda k: f"{QUESTION_TYPES[k]['cn']} / {QUESTION_TYPES[k]['en']}",
        key="horary_west_qtype",
    )

    if st.button(
        auto_cn("🔮 卜卦判斷", "🔮 Cast Horary Chart"),
        key="horary_west_cast",
        type="primary",
    ):
        with st.spinner(auto_cn("計算卜卦星盤…", "Computing horary chart…")):
            try:
                chart = compute_western_horary(
                    year=year, month=month, day=day,
                    hour=hour, minute=minute, timezone=timezone,
                    latitude=latitude, longitude=longitude,
                    location_name=location_name,
                    question_text=q_text or auto_cn("未指定問題", "Question not specified"),
                    question_type=q_type,
                )
                _render_western_chart(chart, lang)
            except Exception as e:
                st.error(f"Error computing horary chart: {e}")
                st.exception(e)


def _render_western_chart(chart: WesternHoraryChart, lang: str) -> None:
    """Render a computed Western Horary chart in Streamlit."""

    # SVG Chart
    col1, col2 = st.columns([3, 2])
    with col1:
        svg = render_western_horary_svg(chart)
        st.markdown(f'<div style="overflow:hidden;border-radius:8px">{svg}</div>',
                    unsafe_allow_html=True)

    with col2:
        # Radicality
        st.markdown(
            f'<div class="horary-section">'
            f'<h4>{"問卜記錄" if lang=="zh" else "Chart Details"}</h4>'
            f'<p style="color:#c4a876;font-size:0.85em;font-family:serif">'
            f'{"問題時間" if lang=="zh" else "Question Time"}: {chart.question_datetime}<br/>'
            f'{"問題地點" if lang=="zh" else "Location"}: {chart.location_name or "—"}<br/>'
            f'{"上升星座" if lang=="zh" else "Ascendant"}: '
            f'{int(chart.asc_degree)}° {chart.asc_sign_cn if lang=="zh" else chart.asc_sign}<br/>'
            f'{"問卜者主星" if lang=="zh" else "Querent Sig."}: '
            f'{PLANET_GLYPHS.get(chart.asc_lord, "")} {PLANET_CN.get(chart.asc_lord, chart.asc_lord) if lang=="zh" else chart.asc_lord}<br/>'
            f'{"問時主星" if lang=="zh" else "Hour Lord"}: '
            f'{PLANET_GLYPHS.get(chart.planetary_hour_lord, "")} {chart.planetary_hour_lord}<br/>'
            f'{"正時" if lang=="zh" else "Radical"}: '
            f'{"✅ 是" if chart.is_radical else "⚠️ 否"}'
            f'</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Verdict
        v = chart.judgment.verdict
        v_cn = chart.judgment.verdict_cn
        verdict_display = v_cn if lang == "zh" else v.replace("_", " ").title()
        verdict_class = "verdict-yes" if "yes" in v else ("verdict-no" if v == "no" else "verdict-unclear")
        st.markdown(
            f'<div class="{verdict_class}">'
            f'{"判斷" if lang=="zh" else "VERDICT"}: {verdict_display}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Strictures
    if chart.strictures:
        st.markdown(
            f'<div class="horary-section"><h4>'
            f'{"⚠️ 判斷障礙（Strictures Against Judgment）" if lang=="zh" else "⚠️ Strictures Against Judgment"}'
            f'</h4>',
            unsafe_allow_html=True,
        )
        for s in chart.strictures:
            text = s.cn if lang == "zh" else s.en
            css_class = f"stricture-{s.severity}"
            st.markdown(
                f'<div class="{css_class}">{text} <em style="font-size:0.8em">({s.lilly_ref})</em></div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Moon status
    moon = next((p for p in chart.planets if p.name == "Moon"), None)
    if moon:
        voc = chart.moon_voc
        moon_status_parts = []
        if voc.is_voc:
            if voc.has_exception:
                moon_status_parts.append(
                    auto_cn(f"月亮虛空（例外星座—仍可有結果，但緩慢）", "VOC Moon (exception sign — may still yield results)")
                )
            else:
                moon_status_parts.append(auto_cn("月亮虛空 ⛔", "Void of Course Moon ⛔"))
        if moon.in_via_combusta:
            moon_status_parts.append(auto_cn("月亮在燃燒之路 ⚠️", "Moon in Via Combusta ⚠️"))

    # Planets table
    st.markdown(
        f'<div class="horary-section"><h4>'
        f'{"🪐 行星位置與力量" if lang=="zh" else "🪐 Planetary Positions & Strength"}'
        f'</h4>',
        unsafe_allow_html=True,
    )

    planet_rows = []
    for p in chart.planets:
        sig_marker = ""
        if p.name == chart.asc_lord:
            sig_marker = " ◀ Q" if lang != "zh" else " ◀ 問"
        elif p.name == chart.judgment.quesited_significator:
            sig_marker = " ◀ A" if lang != "zh" else " ◀ 所問"
        retro = " ℞" if p.retrograde else ""
        combust = ""
        if p.combust_status == "cazimi":
            combust = " ✦Cazimi"
        elif p.combust_status == "combust":
            combust = " 🔥焦傷" if lang == "zh" else " 🔥Combust"
        elif p.combust_status == "under_sunbeams":
            combust = " ☀️光下" if lang == "zh" else " ☀️Sunbeams"

        dignity = p.essential_dignity
        dignity_display = {
            "domicile": "入廟" if lang == "zh" else "Domicile",
            "exaltation": "入旺" if lang == "zh" else "Exaltation",
            "triplicity": "三合" if lang == "zh" else "Triplicity",
            "term": "界" if lang == "zh" else "Term",
            "face": "旬" if lang == "zh" else "Face",
            "detriment": "落陷" if lang == "zh" else "Detriment",
            "fall": "失旺" if lang == "zh" else "Fall",
            "peregrine": "漂泊" if lang == "zh" else "Peregrine",
        }.get(dignity, dignity)

        name_display = f"{PLANET_GLYPHS.get(p.name, '')} {PLANET_CN.get(p.name, p.name) if lang=='zh' else p.name}"
        planet_rows.append({
            auto_cn("行星", "Planet"): name_display + sig_marker,
            auto_cn("位置", "Position"): p.formatted_pos,
            auto_cn("宮位", "House"): f"H{p.house}",
            auto_cn("本質尊貴", "Dignity"): dignity_display,
            auto_cn("力量", "Strength"): p.total_strength,
            auto_cn("狀態", "Status"): retro + combust,
        })

    if planet_rows:
        import pandas as pd
        df = pd.DataFrame(planet_rows)
        st.dataframe(df, width="stretch")

    st.markdown('</div>', unsafe_allow_html=True)

    # Aspects
    applying_aspects = [a for a in chart.aspects if a.is_applying]
    if applying_aspects:
        st.markdown(
            f'<div class="horary-section"><h4>'
            f'{"⚡ 入相相位（Applying Aspects）" if lang=="zh" else "⚡ Applying Aspects"}'
            f'</h4>',
            unsafe_allow_html=True,
        )
        for asp in applying_aspects[:8]:
            glyph1 = PLANET_GLYPHS.get(asp.planet1, "")
            glyph2 = PLANET_GLYPHS.get(asp.planet2, "")
            p1_cn = PLANET_CN.get(asp.planet1, asp.planet1)
            p2_cn = PLANET_CN.get(asp.planet2, asp.planet2)
            name_display = (
                f"{glyph1} {p1_cn} {asp.aspect_cn} {p2_cn} {glyph2}"
                if lang == "zh"
                else f"{glyph1} {asp.planet1} {asp.aspect_name} {asp.planet2} {glyph2}"
            )
            reception = f" [{auto_cn('互容', 'Reception')}]" if asp.has_reception else ""
            partile = f" [{auto_cn('合度', 'Partile')}]" if asp.is_partile else ""
            st.markdown(
                f'<div class="planet-row planet-{"strong" if asp.nature == "benefic" else "weak" if asp.nature == "malefic" else "neutral"}">'
                f'{name_display} — {asp.orb:.1f}° orb{reception}{partile}'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Translations / Collections
    if chart.translations_of_light:
        st.markdown(
            f'<div class="horary-section"><h4>'
            f'{"🔄 光之傳遞" if lang=="zh" else "🔄 Translation of Light"}'
            f'</h4>',
            unsafe_allow_html=True,
        )
        for tr in chart.translations_of_light:
            text = tr.description_cn if lang == "zh" else tr.description_en
            st.markdown(f'<p style="color:#d4c09c;font-style:italic;font-size:0.9em">{text}</p>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if chart.collections_of_light:
        st.markdown(
            f'<div class="horary-section"><h4>'
            f'{"⭕ 光之聚合" if lang=="zh" else "⭕ Collection of Light"}'
            f'</h4>',
            unsafe_allow_html=True,
        )
        for cl in chart.collections_of_light:
            text = cl.description_cn if lang == "zh" else cl.description_en
            st.markdown(f'<p style="color:#d4c09c;font-style:italic;font-size:0.9em">{text}</p>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Full judgment text
    with st.expander(
        auto_cn("📖 完整卜卦判斷文本", "📖 Full Horary Judgment"),
        expanded=True
    ):
        full_text = chart.judgment.full_judgment_cn if lang == "zh" else chart.judgment.full_judgment_en
        st.markdown(
            f'<div class="judgment-text">{_xml_escape(full_text)}</div>',
            unsafe_allow_html=True,
        )


def _render_vedic_tab(
    year, month, day, hour, minute, timezone,
    latitude, longitude, location_name
) -> None:
    """Render Vedic Prashna section."""
    lang = get_lang()

    st.markdown(
        '<div class="classical-quote">'
        '"When a person asks a question with an anxious mind, the Lagna at that moment '
        'is to be treated as the Janma Lagna for purposes of judgment." '
        '— <em>Prasna Marga</em>, Chapter 1, v. 4'
        '</div>',
        unsafe_allow_html=True,
    )

    q_text = st.text_area(
        auto_cn("📝 問題（Prashna）", "📝 Question (Prashna)"),
        placeholder=auto_cn(
            "請輸入您的問題，例如：「我的婚姻何時成就？」",
            "Enter your question, e.g. 'When will I marry?'"
        ),
        height=80,
        key="horary_vedic_question",
    )

    q_type = st.selectbox(
        auto_cn("🏷️ 問題類型", "🏷️ Question Type"),
        options=list(PRASHNA_QUESTION_TYPES.keys()),
        format_func=lambda k: f"{PRASHNA_QUESTION_TYPES[k]['cn']} / {PRASHNA_QUESTION_TYPES[k]['en']}",
        key="horary_vedic_qtype",
    )

    col_a, col_b = st.columns([2, 1])
    with col_a:
        chart_style = st.radio(
            auto_cn("圖表格式", "Chart Style"),
            options=["north_indian", "south_indian"],
            format_func=lambda s: auto_cn(
                "北印度格式" if s == "north_indian" else "南印度格式",
                "North Indian" if s == "north_indian" else "South Indian"
            ),
            horizontal=True,
            key="horary_vedic_style",
        )
    with col_b:
        prashna_num = st.number_input(
            auto_cn("問卜數字 (1-108, 可選)", "Prashna Number (1-108, optional)"),
            min_value=0, max_value=108, value=0, step=1,
            help=auto_cn(
                "傳統方法：問卜者提供1-108之間的數字以確定命宮。留0則使用實際時刻命宮。",
                "Traditional method: querent provides a number 1-108 to determine Lagna. Leave 0 to use actual moment."
            ),
            key="horary_vedic_num",
        )

    if st.button(
        auto_cn("🔮 問卦判斷", "🔮 Cast Prashna"),
        key="horary_vedic_cast",
        type="primary",
    ):
        with st.spinner(auto_cn("計算問卦星盤…", "Computing Prashna chart…")):
            try:
                chart = compute_vedic_prashna(
                    year=year, month=month, day=day,
                    hour=hour, minute=minute, timezone=timezone,
                    latitude=latitude, longitude=longitude,
                    location_name=location_name,
                    question_text=q_text or auto_cn("未指定問題", "Question not specified"),
                    question_type=q_type,
                    prashna_number=int(prashna_num) if prashna_num > 0 else None,
                )
                _render_vedic_chart(chart, lang, chart_style)
            except Exception as e:
                st.error(f"Error computing Prashna chart: {e}")
                st.exception(e)


def _render_vedic_chart(chart: VedicPrashnaChart, lang: str, style: str) -> None:
    """Render a computed Vedic Prashna chart in Streamlit."""
    from .constants import VEDIC_RASHIS

    col1, col2 = st.columns([3, 2])
    with col1:
        svg = render_vedic_prashna_svg(chart, style=style)
        st.markdown(f'<div style="overflow:hidden;border-radius:8px">{svg}</div>',
                    unsafe_allow_html=True)

    with col2:
        asc_sign_cn = chart.asc_sign_cn
        asc_sign_en = chart.asc_sign
        st.markdown(
            f'<div class="horary-section">'
            f'<h4>{"問卦記錄" if lang=="zh" else "Prashna Details"}</h4>'
            f'<p style="color:#c4a876;font-size:0.85em;font-family:serif">'
            f'{"問時" if lang=="zh" else "Time"}: {chart.question_datetime}<br/>'
            f'{"命宮" if lang=="zh" else "Lagna"}: '
            f'{int(chart.asc_degree)}° {asc_sign_cn if lang=="zh" else asc_sign_en}<br/>'
            f'{"命宮主星" if lang=="zh" else "Lagna Lord"}: {chart.asc_lord}<br/>'
            f'{"歲差" if lang=="zh" else "Ayanamsa"}: {chart.ayanamsa:.2f}°'
            f'</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Verdict
        v = chart.judgment.verdict
        v_cn = chart.judgment.verdict_cn
        verdict_display = v_cn if lang == "zh" else v.replace("_", " ").title()
        verdict_class = "verdict-yes" if "yes" in v else ("verdict-no" if v == "no" else "verdict-unclear")
        st.markdown(
            f'<div class="{verdict_class}">'
            f'{"判斷" if lang=="zh" else "VERDICT"}: {verdict_display}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Arudha Lagna
    al = chart.arudha_lagna
    al_text = al.description_cn if lang == "zh" else al.description_en
    st.markdown(
        f'<div class="arudha-box">'
        f'<strong>{"🔮 阿魯達命宮（Arudha Lagna）" if lang=="zh" else "🔮 Arudha Lagna"}</strong><br/>'
        f'{al_text}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Numerology if used
    if chart.numerology:
        n = chart.numerology
        n_text = n.description_cn if lang == "zh" else n.description_en
        st.info(f"{'🔢 問卜數字法：' if lang=='zh' else '🔢 Prashna Number Method: '}{n_text}")

    # Planets table
    st.markdown(
        f'<div class="horary-section"><h4>'
        f'{"🪐 行星位置（吠陀）" if lang=="zh" else "🪐 Planet Positions (Vedic)"}'
        f'</h4>',
        unsafe_allow_html=True,
    )
    planet_rows = []
    for p in chart.planets:
        retro = " ℞" if p.retrograde else ""
        dignity = {
            "exalted": "入旺" if lang == "zh" else "Exalted",
            "own_sign": "本宮" if lang == "zh" else "Own Sign",
            "debilitated": "落陷" if lang == "zh" else "Debilitated",
            "neutral": "中性" if lang == "zh" else "Neutral",
        }.get(p.dignity, p.dignity)
        planet_rows.append({
            auto_cn("行星", "Planet"): p.name_vedic,
            auto_cn("星座", "Sign"): f"{p.sign_cn if lang=='zh' else p.sign}",
            auto_cn("宮位", "House"): f"H{p.house}",
            auto_cn("尊貴", "Dignity"): dignity + retro,
            auto_cn("度數", "Degree"): p.formatted_pos,
        })

    if planet_rows:
        import pandas as pd
        df = pd.DataFrame(planet_rows)
        st.dataframe(df, width="stretch")

    st.markdown('</div>', unsafe_allow_html=True)

    # Key factors
    factors = chart.judgment.key_factors_cn if lang == "zh" else chart.judgment.key_factors_en
    if factors:
        st.markdown(
            f'<div class="horary-section"><h4>'
            f'{"🔑 關鍵指標" if lang=="zh" else "🔑 Key Indicators"}'
            f'</h4>',
            unsafe_allow_html=True,
        )
        for factor in factors:
            st.markdown(
                f'<div class="planet-row">{factor}</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Full judgment
    with st.expander(
        auto_cn("📖 完整問卦判斷文本", "📖 Full Prashna Judgment"),
        expanded=True
    ):
        full_text = chart.judgment.full_judgment_cn if lang == "zh" else chart.judgment.full_judgment_en
        st.markdown(
            f'<div class="judgment-text">{_xml_escape(full_text)}</div>',
            unsafe_allow_html=True,
        )
