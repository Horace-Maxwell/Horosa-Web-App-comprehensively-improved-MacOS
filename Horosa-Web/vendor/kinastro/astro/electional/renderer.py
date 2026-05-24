"""
astro/electional/renderer.py — Electional Astrology & Vedic Muhurta Renderer

SVG Visuals:
  - render_western_electional_svg(): 17th-century astrological manuscript aesthetic,
    Lilly-era woodcut style, antique parchment, classical ink calligraphy.
  - render_vedic_muhurta_svg(): Traditional Indian Panchanga / Muhurta table style,
    Sanskrit-inspired decorative borders, lotus motifs, temple-inscription aesthetic.

Streamlit UI:
  - render_streamlit(): Main entry point; tabs for Western and Vedic traditions.
"""

from __future__ import annotations

import html
import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import streamlit as st

from astro.i18n import auto_cn, get_lang, t
from .calculator import (
    WesternElectionalResult,
    VedicMuhurtaResult,
    ElectionalPlanet,
    WesternElectionalFactor,
    VedicMuhurtaFactor,
    PanchangaElement,
    compute_western_electional,
    compute_vedic_muhurta,
    find_western_elections,
    find_vedic_muhurtas,
)
from .constants import (
    PLANET_GLYPHS, PLANET_CN,
    ZODIAC_SIGNS,
    WESTERN_ACTIVITY_TYPES, VEDIC_ACTIVITY_TYPES,
    VEDIC_RASHIS,
)


# ============================================================
# Utility
# ============================================================

def _xml_escape(text: str) -> str:
    return html.escape(str(text), quote=True)


# ============================================================
# CSS — Antique Manuscript Aesthetic
# ============================================================

_ELECTIONAL_CSS = """
<style>
/* ── Electional Module Global Styles ────────────────────────────── */
.elect-header {
    background: linear-gradient(135deg, #1A0E00 0%, #3A2000 50%, #5C3000 100%);
    border: 1px solid #8B5E00;
    border-left: 6px solid #D4AF37;
    padding: 18px 24px;
    border-radius: 8px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.elect-header::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='8' height='8'%3E%3Crect width='8' height='8' fill='%231A0E00'/%3E%3Ccircle cx='1' cy='1' r='0.8' fill='%23D4AF37' opacity='0.05'/%3E%3C/svg%3E");
    pointer-events: none;
}
.elect-header h2 { color: #F5DEB3; margin: 0 0 4px 0; font-size: 1.5em; font-family: 'Georgia', serif; }
.elect-header p  { color: #C8A86A; margin: 0; font-size: 0.88em; font-style: italic; }

.elect-section {
    background: rgba(139,94,0,0.08);
    border: 1px solid rgba(139,94,0,0.25);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 14px;
}
.elect-section h4 {
    color: #D4AF37;
    margin: 0 0 10px 0;
    font-family: 'Georgia', serif;
    letter-spacing: 0.05em;
    border-bottom: 1px solid rgba(212,175,55,0.25);
    padding-bottom: 6px;
}

.factor-good {
    background: rgba(42,100,60,0.15);
    border-left: 4px solid #2E7D52;
    border-radius: 4px;
    padding: 7px 12px;
    margin-bottom: 6px;
    color: #7EC8A0;
    font-family: 'Georgia', serif;
    font-size: 0.88em;
}
.factor-bad {
    background: rgba(130,40,30,0.15);
    border-left: 4px solid #9B2226;
    border-radius: 4px;
    padding: 7px 12px;
    margin-bottom: 6px;
    color: #F0A080;
    font-family: 'Georgia', serif;
    font-size: 0.88em;
}
.factor-neutral {
    background: rgba(100,90,60,0.12);
    border-left: 4px solid #8B7A50;
    border-radius: 4px;
    padding: 7px 12px;
    margin-bottom: 6px;
    color: #D0C080;
    font-family: 'Georgia', serif;
    font-size: 0.88em;
}

.quality-excellent {
    background: linear-gradient(135deg, rgba(212,175,55,0.25), rgba(180,140,40,0.15));
    border: 2px solid #D4AF37;
    border-radius: 8px; padding: 12px 20px;
    color: #F5DEB3; font-size: 1.15em; font-family: 'Georgia', serif;
    font-weight: bold; text-align: center; letter-spacing: 0.08em;
}
.quality-good {
    background: rgba(42,100,60,0.18);
    border: 2px solid #2E7D52;
    border-radius: 8px; padding: 12px 20px;
    color: #7EC8A0; font-size: 1.1em; font-family: 'Georgia', serif;
    font-weight: bold; text-align: center;
}
.quality-neutral {
    background: rgba(100,90,60,0.15);
    border: 2px solid #8B7A50;
    border-radius: 8px; padding: 12px 20px;
    color: #D0C080; font-size: 1.1em; font-family: 'Georgia', serif;
    font-weight: bold; text-align: center;
}
.quality-poor {
    background: rgba(130,80,20,0.15);
    border: 2px solid #9B6A26;
    border-radius: 8px; padding: 12px 20px;
    color: #E0A060; font-size: 1.1em; font-family: 'Georgia', serif;
    font-weight: bold; text-align: center;
}
.quality-avoid {
    background: rgba(130,30,30,0.18);
    border: 2px solid #9B2226;
    border-radius: 8px; padding: 12px 20px;
    color: #F07070; font-size: 1.1em; font-family: 'Georgia', serif;
    font-weight: bold; text-align: center;
}

.panchanga-row {
    display: flex; align-items: center;
    padding: 5px 10px; margin-bottom: 4px;
    background: rgba(20,10,0,0.5);
    border: 1px solid rgba(139,94,0,0.3);
    border-radius: 4px;
    font-family: 'Georgia', serif; font-size: 0.88em;
}
.panchanga-label { color: #D4AF37; width: 110px; font-weight: bold; }
.panchanga-value { color: #F5DEB3; flex: 1; }
.panchanga-good  { border-left: 3px solid #2E7D52 !important; }
.panchanga-bad   { border-left: 3px solid #9B2226 !important; }

.classical-quote {
    border-left: 3px solid #D4AF37;
    padding: 6px 14px;
    margin: 10px 0;
    font-style: italic;
    color: #C8A86A;
    font-size: 0.88em;
    font-family: 'Georgia', serif;
    background: rgba(139,94,0,0.08);
    border-radius: 0 4px 4px 0;
}

.elect-moon-good {
    background: rgba(42,100,60,0.15);
    border: 1px solid rgba(46,125,82,0.5);
    border-radius: 6px; padding: 8px 14px;
    color: #7EC8A0; font-family: 'Georgia', serif; font-size: 0.9em;
}
.elect-moon-bad {
    background: rgba(130,40,30,0.15);
    border: 1px solid rgba(155,34,38,0.5);
    border-radius: 6px; padding: 8px 14px;
    color: #F0A080; font-family: 'Georgia', serif; font-size: 0.9em;
}

.elect-result-card {
    background: rgba(30,18,0,0.7);
    border: 1px solid rgba(212,175,55,0.35);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-family: 'Georgia', serif;
}
.elect-result-time { color: #D4AF37; font-weight: bold; font-size: 1.05em; }
.elect-result-score { color: #F5DEB3; font-size: 0.9em; }
</style>
"""


# ============================================================
# SVG: Western Electional Chart
# ============================================================

def render_western_electional_svg(result: WesternElectionalResult) -> str:
    """
    Render a Western Electional chart as SVG.

    Style: 17th-century astrological manuscript / Lilly-era book aesthetic.
    Features:
      - Antique parchment background with subtle texture
      - Circular wheel with 12 houses and zodiac band
      - Planet glyphs placed at their houses
      - Central summary panel with score and quality
      - Auspicious/inauspicious factors listed in classical style
      - Gold and ink colour palette throughout

    Returns an SVG string.
    """
    W, H = 600, 620
    cx, cy = W // 2, 300
    R_outer = 240
    R_zodiac_inner = 215
    R_house = 170
    R_planet = 193
    R_inner = 100

    # ── Colour palette (parchment & ink) ───────────────────────
    bg_parchment = "#F5EDCC"
    paper_mid = "#EAD898"
    ink_dark = "#2C1A00"
    ink_gold = "#8B5E00"
    ink_green = "#1A5C2A"
    ink_red = "#7A1818"
    circle_dark = "#4A2E00"
    gold_accent = "#C8960A"

    parts: List[str] = []

    # ── SVG header ──────────────────────────────────────────────
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" font-family="Georgia,\'Times New Roman\',serif">'
    )

    # ── Defs ────────────────────────────────────────────────────
    parts.extend([
        '<defs>',
        '  <radialGradient id="parch" cx="50%" cy="42%" r="62%">',
        f'    <stop offset="0%" stop-color="#FAF3DA"/>',
        f'    <stop offset="65%" stop-color="{bg_parchment}"/>',
        f'    <stop offset="100%" stop-color="#D8C070"/>',
        '  </radialGradient>',
        '  <filter id="ptex" x="-3%" y="-3%" width="106%" height="106%">',
        '    <feTurbulence type="fractalNoise" baseFrequency="0.68" numOctaves="3" '
        '      stitchTiles="stitch" result="noise"/>',
        '    <feColorMatrix type="saturate" values="0" in="noise" result="grey"/>',
        '    <feBlend in="SourceGraphic" in2="grey" mode="multiply" result="blend"/>',
        '    <feComposite in="blend" in2="SourceGraphic" operator="in"/>',
        '  </filter>',
        '</defs>',
    ])

    # ── Background parchment ────────────────────────────────────
    parts.append(
        f'<rect width="{W}" height="{H}" rx="12" ry="12" '
        f'fill="url(#parch)" stroke="{circle_dark}" stroke-width="3" filter="url(#ptex)"/>'
    )
    # Double border frame
    parts.append(
        f'<rect x="8" y="8" width="{W-16}" height="{H-16}" rx="9" ry="9" '
        f'fill="none" stroke="{ink_gold}" stroke-width="1.2" opacity="0.7"/>'
    )
    parts.append(
        f'<rect x="13" y="13" width="{W-26}" height="{H-26}" rx="7" ry="7" '
        f'fill="none" stroke="{ink_dark}" stroke-width="0.4" opacity="0.4"/>'
    )

    # ── Title ───────────────────────────────────────────────────
    activity = WESTERN_ACTIVITY_TYPES.get(result.activity_type, {})
    act_en = activity.get("en", result.activity_type)
    act_cn = activity.get("cn", result.activity_type)
    dt_str = result.datetime_local.strftime("%Y-%m-%d %H:%M")
    parts.extend([
        f'<text x="{cx}" y="36" text-anchor="middle" font-size="15" '
        f'fill="{circle_dark}" font-weight="bold" font-style="italic" letter-spacing="1">'
        f'Western Electional Astrology ✦ {_xml_escape(act_en)}</text>',
        f'<text x="{cx}" y="52" text-anchor="middle" font-size="9" '
        f'fill="{ink_gold}" letter-spacing="0.5">'
        f'{_xml_escape(act_cn)} ✦ {_xml_escape(dt_str)}</text>',
    ])

    # ── Outer circle (zodiac band) ───────────────────────────────
    parts.extend([
        f'<circle cx="{cx}" cy="{cy}" r="{R_outer}" fill="none" '
        f'stroke="{circle_dark}" stroke-width="2"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{R_zodiac_inner}" fill="none" '
        f'stroke="{circle_dark}" stroke-width="1"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{R_house}" fill="rgba(244,237,200,0.5)" '
        f'stroke="{circle_dark}" stroke-width="1.5"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{R_inner}" fill="rgba(244,237,200,0.85)" '
        f'stroke="{circle_dark}" stroke-width="1.5"/>',
    ])

    # ── Zodiac Signs (outer band) ───────────────────────────────
    SIGN_ELEMENTS = {
        "fire": ink_red, "earth": ink_gold,
        "air": "#1A3A6A", "water": "#1A5C5C",
    }
    for i, (sname, sglyph, scn, element) in enumerate(ZODIAC_SIGNS):
        # Starting angle: Aries = 0° from Ascendant (East = left for traditional chart)
        # Standard astrological convention: ASC = 0°, counter-clockwise
        angle_start = (i * 30) - 90  # degrees from top, zodiac goes CCW
        angle_mid = angle_start + 15
        rad_mid = math.radians(angle_mid)
        # Position in zodiac band
        r_glyph = (R_outer + R_zodiac_inner) / 2
        gx = cx + r_glyph * math.cos(rad_mid)
        gy = cy + r_glyph * math.sin(rad_mid)
        colour = SIGN_ELEMENTS.get(element, ink_dark)

        # Dividing line
        rad_start = math.radians(angle_start)
        lx1 = cx + R_zodiac_inner * math.cos(rad_start)
        ly1 = cy + R_zodiac_inner * math.sin(rad_start)
        lx2 = cx + R_outer * math.cos(rad_start)
        ly2 = cy + R_outer * math.sin(rad_start)
        parts.append(
            f'<line x1="{lx1:.1f}" y1="{ly1:.1f}" x2="{lx2:.1f}" y2="{ly2:.1f}" '
            f'stroke="{circle_dark}" stroke-width="0.7" opacity="0.6"/>'
        )
        # Glyph
        parts.append(
            f'<text x="{gx:.1f}" y="{gy+4:.1f}" text-anchor="middle" font-size="13" '
            f'fill="{colour}">{_xml_escape(sglyph)}</text>'
        )

    # ── House Cusps ─────────────────────────────────────────────
    asc = result.ascendant
    for i in range(12):
        cusp = result.house_cusps[i]
        # Convert to angle: ASC is at the left (180°), standard wheel
        cusp_offset = (cusp - asc) % 360.0
        angle_deg = 180.0 - cusp_offset  # standard horoscope wheel orientation
        rad = math.radians(angle_deg)
        lx1 = cx + R_inner * math.cos(rad)
        ly1 = cy + R_inner * math.sin(rad)
        lx2 = cx + R_house * math.cos(rad)
        ly2 = cy + R_house * math.sin(rad)
        parts.append(
            f'<line x1="{lx1:.1f}" y1="{ly1:.1f}" x2="{lx2:.1f}" y2="{ly2:.1f}" '
            f'stroke="{circle_dark}" stroke-width="{"2.0" if i in (0, 3, 6, 9) else "0.8"}"/>'
        )
        # House number at midpoint
        next_cusp = result.house_cusps[(i + 1) % 12]
        next_offset = (next_cusp - asc) % 360.0
        mid_offset = (cusp_offset + next_offset) / 2.0
        if abs(next_offset - cusp_offset) > 180:
            mid_offset = (cusp_offset + next_offset + 360) / 2.0
        mid_angle = 180.0 - mid_offset
        mid_rad = math.radians(mid_angle)
        r_num = (R_inner + R_house) / 2
        nx = cx + r_num * math.cos(mid_rad)
        ny = cy + r_num * math.sin(mid_rad)
        parts.append(
            f'<text x="{nx:.1f}" y="{ny+3:.1f}" text-anchor="middle" font-size="9" '
            f'fill="{ink_gold}" opacity="0.8">{i+1}</text>'
        )

    # ── Planets ─────────────────────────────────────────────────
    planet_house_count: Dict[int, int] = {}
    for planet in result.planets:
        lon = planet.longitude
        offset = (lon - asc) % 360.0
        angle_deg = 180.0 - offset
        rad = math.radians(angle_deg)

        # Stagger planets in same house
        house = planet.house
        planet_house_count[house] = planet_house_count.get(house, 0) + 1
        stagger = (planet_house_count[house] - 1) * 5

        r_p = R_planet - stagger
        px = cx + r_p * math.cos(rad)
        py = cy + r_p * math.sin(rad)

        # Colour by nature
        if planet.nature == "benefic":
            pcolor = ink_green
        elif planet.nature == "malefic":
            pcolor = ink_red
        else:
            pcolor = ink_gold

        # Highlight if retrograde
        rx_marker = ""
        if planet.retrograde:
            rx_marker = (
                f'<text x="{px+7:.1f}" y="{py-4:.1f}" text-anchor="middle" '
                f'font-size="7" fill="{ink_red}" font-style="italic">℞</text>'
            )

        parts.append(
            f'<text x="{px:.1f}" y="{py+4:.1f}" text-anchor="middle" '
            f'font-size="14" fill="{pcolor}" font-weight="bold">'
            f'{_xml_escape(planet.glyph)}</text>'
        )
        if rx_marker:
            parts.append(rx_marker)

    # ── ASC marker ──────────────────────────────────────────────
    asc_rad = math.radians(180.0)
    ax1 = cx + R_house * math.cos(asc_rad)
    ay1 = cy + R_house * math.sin(asc_rad)
    ax2 = cx + R_zodiac_inner * math.cos(asc_rad)
    ay2 = cy + R_zodiac_inner * math.sin(asc_rad)
    parts.append(
        f'<line x1="{ax1:.1f}" y1="{ay1:.1f}" x2="{ax2:.1f}" y2="{ay2:.1f}" '
        f'stroke="{gold_accent}" stroke-width="2.5"/>'
    )
    parts.append(
        f'<text x="{cx - R_house - 14:.1f}" y="{cy+5:.1f}" text-anchor="middle" '
        f'font-size="9" fill="{gold_accent}" font-weight="bold">ASC</text>'
    )

    # ── Central Score Panel ──────────────────────────────────────
    score_text = f"{result.total_score:+.0f}"
    quality_colour = (
        gold_accent if result.quality == "Excellent" else
        ink_green if result.quality == "Good" else
        ink_gold if result.quality == "Neutral" else
        "#8B4513" if result.quality == "Poor" else ink_red
    )
    parts.extend([
        f'<text x="{cx}" y="{cy-20}" text-anchor="middle" font-size="9" '
        f'fill="{ink_dark}" font-style="italic" opacity="0.7">Score</text>',
        f'<text x="{cx}" y="{cy+8}" text-anchor="middle" font-size="26" '
        f'fill="{quality_colour}" font-weight="bold">{_xml_escape(score_text)}</text>',
        f'<text x="{cx}" y="{cy+24}" text-anchor="middle" font-size="10" '
        f'fill="{quality_colour}">{_xml_escape(result.quality_stars)}</text>',
        f'<text x="{cx}" y="{cy+40}" text-anchor="middle" font-size="9" '
        f'fill="{ink_dark}" font-style="italic">{_xml_escape(result.quality)}</text>',
    ])

    # Moon state indicator
    moon_colour = ink_red if result.moon_is_voc else ink_green
    moon_status = "☽ VOC" if result.moon_is_voc else f"☽ {result.moon_phase}"
    parts.append(
        f'<text x="{cx}" y="{cy+56}" text-anchor="middle" font-size="8.5" '
        f'fill="{moon_colour}" font-style="italic">{_xml_escape(moon_status)}</text>'
    )

    # Planetary hour
    parts.append(
        f'<text x="{cx}" y="{cy+70}" text-anchor="middle" font-size="8" '
        f'fill="{ink_gold}" opacity="0.8">'
        f'Hour: {_xml_escape(PLANET_GLYPHS.get(result.planetary_hour_lord, result.planetary_hour_lord))}'
        f'</text>'
    )

    # ── ASC Sign and Lord ────────────────────────────────────────
    parts.extend([
        f'<text x="{cx}" y="{cy - 52}" text-anchor="middle" font-size="8.5" '
        f'fill="{ink_dark}" font-style="italic">ASC: {_xml_escape(result.asc_sign)} · '
        f'Lord: {_xml_escape(result.asc_lord)}</text>',
    ])

    # ── Bottom caption ───────────────────────────────────────────
    hour_lord_glyph = PLANET_GLYPHS.get(result.planetary_hour_lord, result.planetary_hour_lord)
    parts.extend([
        f'<text x="{cx}" y="{H - 44}" text-anchor="middle" font-size="9" '
        f'fill="{circle_dark}" font-style="italic">'
        f'William Lilly · Christian Astrology (1647) · Electional Rules</text>',
        f'<text x="{cx}" y="{H - 28}" text-anchor="middle" font-size="8" '
        f'fill="{ink_gold}">'
        f'{_xml_escape(result.location_name or "")}'
        f' ✦ Lat {result.latitude:.2f}° Lon {result.longitude:.2f}°</text>',
        f'<text x="{cx}" y="{H - 14}" text-anchor="middle" font-size="7.5" '
        f'fill="{ink_dark}" opacity="0.6">'
        f'Planetary Hour {hour_lord_glyph} (Hr {result.planetary_hour_number}) ✦ '
        f'{"Suitable" if result.planetary_hour_suitable else "Not ideal"} for {_xml_escape(act_en)}</text>',
    ])

    parts.append('</svg>')
    return "\n".join(parts)


# ============================================================
# SVG: Vedic Muhurta / Panchanga Chart
# ============================================================

def render_vedic_muhurta_svg(result: VedicMuhurtaResult) -> str:
    """
    Render a Vedic Muhurta / Panchanga chart as SVG.

    Style: Traditional Indian Panchanga almanac aesthetic.
    Features:
      - Rich saffron/crimson/cream palette (temple manuscript feel)
      - Five-element Panchanga table with Sanskrit/devanagari-inspired decorations
      - South Indian chart grid for Lagna
      - Lotus and yantra border motifs
      - Auspicious/inauspicious indicators in classical style

    Returns an SVG string.
    """
    W, H = 620, 680
    cx = W // 2

    # ── Colour palette (Indian manuscript) ──────────────────────
    saffron = "#E8830A"
    deep_saffron = "#C05A00"
    crimson = "#8B1A1A"
    cream = "#FAF0DC"
    gold = "#C8960A"
    dark_ink = "#2A1000"
    light_cream = "#FFF8EC"
    lotus_pink = "#C04060"
    green_ok = "#1A6030"
    red_bad = "#8B1A1A"
    border_dark = "#4A2000"

    parts: List[str] = []

    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" font-family="Georgia,\'Times New Roman\',serif">'
    )

    # ── Defs ────────────────────────────────────────────────────
    parts.extend([
        '<defs>',
        '  <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">',
        f'    <stop offset="0%" stop-color="#FDF6E4"/>',
        f'    <stop offset="100%" stop-color="#F0DDB0"/>',
        '  </linearGradient>',
        '  <filter id="ptex2">',
        '    <feTurbulence type="fractalNoise" baseFrequency="0.70" numOctaves="3" '
        '      stitchTiles="stitch" result="noise"/>',
        '    <feColorMatrix type="saturate" values="0" in="noise" result="grey"/>',
        '    <feBlend in="SourceGraphic" in2="grey" mode="multiply"/>',
        '  </filter>',
        '</defs>',
    ])

    # ── Background ───────────────────────────────────────────────
    parts.append(
        f'<rect width="{W}" height="{H}" rx="14" ry="14" '
        f'fill="url(#bg-grad)" stroke="{border_dark}" stroke-width="3" filter="url(#ptex2)"/>'
    )
    # Outer decorative border
    parts.append(
        f'<rect x="6" y="6" width="{W-12}" height="{H-12}" rx="10" '
        f'fill="none" stroke="{saffron}" stroke-width="2.5" opacity="0.8"/>'
    )
    parts.append(
        f'<rect x="11" y="11" width="{W-22}" height="{H-22}" rx="8" '
        f'fill="none" stroke="{gold}" stroke-width="1" opacity="0.6"/>'
    )

    # Decorative corner lotus motifs
    for (lx, ly, rot) in [(28, 28, 0), (W-28, 28, 90), (28, H-28, 270), (W-28, H-28, 180)]:
        parts.append(
            f'<g transform="translate({lx},{ly}) rotate({rot})">'
            f'<text x="0" y="5" text-anchor="middle" font-size="18" '
            f'fill="{saffron}" opacity="0.7">✿</text></g>'
        )

    # ── Title ───────────────────────────────────────────────────
    activity = VEDIC_ACTIVITY_TYPES.get(result.activity_type, {})
    act_en = activity.get("en", result.activity_type)
    act_cn = activity.get("cn", result.activity_type)
    dt_str = result.datetime_local.strftime("%Y-%m-%d %H:%M")

    parts.extend([
        f'<text x="{cx}" y="40" text-anchor="middle" font-size="16" '
        f'fill="{crimson}" font-weight="bold" letter-spacing="1.5" font-style="italic">'
        f'॥ Vedic Muhurta Panchanga ॥</text>',
        f'<text x="{cx}" y="56" text-anchor="middle" font-size="10" '
        f'fill="{deep_saffron}">{_xml_escape(act_en)} ✦ {_xml_escape(act_cn)}</text>',
        f'<text x="{cx}" y="70" text-anchor="middle" font-size="9" '
        f'fill="{dark_ink}" opacity="0.7">{_xml_escape(dt_str)} ✦ '
        f'{_xml_escape(result.location_name or "")} '
        f'({result.latitude:.2f}°N {result.longitude:.2f}°E)</text>',
    ])

    # Decorative divider
    parts.append(
        f'<line x1="40" y1="78" x2="{W-40}" y2="78" '
        f'stroke="{saffron}" stroke-width="1.5" opacity="0.7"/>'
    )
    parts.append(
        f'<text x="{cx}" y="74" text-anchor="middle" font-size="14" '
        f'fill="{gold}" opacity="0.5">✦ ✦ ✦</text>'
    )

    # ── Score Box ───────────────────────────────────────────────
    score_colour = (
        green_ok if result.quality in ("Excellent", "Good") else
        gold if result.quality == "Neutral" else red_bad
    )
    parts.extend([
        f'<rect x="{cx-80}" y="84" width="160" height="52" rx="8" '
        f'fill="rgba(200,150,10,0.12)" stroke="{gold}" stroke-width="1.5"/>',
        f'<text x="{cx}" y="108" text-anchor="middle" font-size="22" '
        f'fill="{score_colour}" font-weight="bold">'
        f'{result.quality_stars} {result.total_score:+.0f}</text>',
        f'<text x="{cx}" y="127" text-anchor="middle" font-size="10" '
        f'fill="{score_colour}">{_xml_escape(result.quality)} / {_xml_escape(result.quality_cn)}</text>',
    ])

    # ── Panchanga Table ──────────────────────────────────────────
    tbl_x, tbl_y = 40, 148
    tbl_w, tbl_h = W - 80, 200
    row_h = 36

    # Table background
    parts.append(
        f'<rect x="{tbl_x}" y="{tbl_y}" width="{tbl_w}" height="{tbl_h}" '
        f'rx="6" fill="rgba(255,248,236,0.8)" stroke="{saffron}" stroke-width="1.5"/>'
    )

    # Header
    parts.append(
        f'<rect x="{tbl_x}" y="{tbl_y}" width="{tbl_w}" height="28" '
        f'rx="6" fill="rgba(232,131,10,0.2)" stroke="{saffron}" stroke-width="1"/>'
    )
    parts.extend([
        f'<text x="{tbl_x + tbl_w//2}" y="{tbl_y + 19}" text-anchor="middle" '
        f'font-size="11" fill="{crimson}" font-weight="bold" letter-spacing="2">'
        f'✦ PANCHANGA — THE FIVE LIMBS ✦</text>',
    ])

    panchanga_keys = ["tithi", "vara", "nakshatra", "yoga", "karana"]
    panchanga_labels = ["Tithi (日)", "Vara (曜)", "Nakshatra (宿)", "Yoga (瑜伽)", "Karana (卡拉那)"]

    for i, (key, label) in enumerate(zip(panchanga_keys, panchanga_labels)):
        elem = result.panchanga.get(key)
        if not elem:
            continue
        row_y = tbl_y + 28 + i * row_h

        # Row background
        row_fill = "rgba(232,131,10,0.06)" if i % 2 == 0 else "rgba(255,248,236,0.4)"
        parts.append(
            f'<rect x="{tbl_x}" y="{row_y}" width="{tbl_w}" height="{row_h}" '
            f'fill="{row_fill}" stroke="{saffron}" stroke-width="0.5" opacity="0.6"/>'
        )

        # Nature indicator
        nat_colour = green_ok if elem.nature == "benefic" else (red_bad if elem.nature == "malefic" else gold)
        nat_sym = "✦" if elem.nature == "benefic" else ("✘" if elem.nature == "malefic" else "○")
        parts.extend([
            f'<text x="{tbl_x + 14}" y="{row_y + row_h//2 + 4}" text-anchor="middle" '
            f'font-size="12" fill="{nat_colour}">{nat_sym}</text>',
            f'<text x="{tbl_x + 32}" y="{row_y + row_h//2 + 1}" '
            f'font-size="9.5" fill="{dark_ink}" font-weight="bold">{_xml_escape(label)}</text>',
            f'<text x="{tbl_x + 32}" y="{row_y + row_h//2 + 13}" '
            f'font-size="8.5" fill="{deep_saffron}" font-style="italic">'
            f'{_xml_escape(elem.notes_en[:50])}</text>',
            # Value
            f'<text x="{tbl_x + tbl_w - 16}" y="{row_y + row_h//2 + 1}" '
            f'text-anchor="end" font-size="10" fill="{nat_colour}" font-weight="bold">'
            f'{_xml_escape(elem.value)}</text>',
            f'<text x="{tbl_x + tbl_w - 16}" y="{row_y + row_h//2 + 13}" '
            f'text-anchor="end" font-size="8.5" fill="{dark_ink}">'
            f'{_xml_escape(elem.value_cn)}</text>',
        ])

    # ── Lagna / Moon Indicator ───────────────────────────────────
    info_y = tbl_y + tbl_h + 12

    parts.extend([
        f'<rect x="{tbl_x}" y="{info_y}" width="{(tbl_w - 10)//2}" height="48" '
        f'rx="6" fill="rgba(200,150,10,0.10)" stroke="{gold}" stroke-width="1.2"/>',
        f'<text x="{tbl_x + (tbl_w-10)//4}" y="{info_y+16}" text-anchor="middle" '
        f'font-size="9" fill="{crimson}" font-weight="bold">LAGNA (上升)</text>',
        f'<text x="{tbl_x + (tbl_w-10)//4}" y="{info_y+32}" text-anchor="middle" '
        f'font-size="12" fill="{deep_saffron}" font-weight="bold">'
        f'{_xml_escape(result.lagna_rashi)}</text>',
        f'<text x="{tbl_x + (tbl_w-10)//4}" y="{info_y+44}" text-anchor="middle" '
        f'font-size="8.5" fill="{dark_ink}">{_xml_escape(result.lagna_rashi_cn)}</text>',
    ])

    moon_x = tbl_x + (tbl_w - 10)//2 + 10
    parts.extend([
        f'<rect x="{moon_x}" y="{info_y}" width="{(tbl_w-10)//2}" height="48" '
        f'rx="6" fill="rgba(200,150,10,0.10)" stroke="{gold}" stroke-width="1.2"/>',
        f'<text x="{moon_x + (tbl_w-10)//4}" y="{info_y+16}" text-anchor="middle" '
        f'font-size="9" fill="{crimson}" font-weight="bold">MOON RASHI (月亮星座)</text>',
        f'<text x="{moon_x + (tbl_w-10)//4}" y="{info_y+32}" text-anchor="middle" '
        f'font-size="12" fill="{deep_saffron}" font-weight="bold">'
        f'{_xml_escape(result.moon_rashi)}</text>',
        f'<text x="{moon_x + (tbl_w-10)//4}" y="{info_y+44}" text-anchor="middle" '
        f'font-size="8.5" fill="{dark_ink}">{_xml_escape(result.moon_rashi_cn)}</text>',
    ])

    # ── Factors List ─────────────────────────────────────────────
    fac_y = info_y + 62
    parts.append(
        f'<text x="{cx}" y="{fac_y}" text-anchor="middle" font-size="10" '
        f'fill="{crimson}" font-weight="bold" letter-spacing="1">✦ KEY MUHURTA FACTORS ✦</text>'
    )
    fac_y += 10
    max_factors = min(len(result.factors), 6)
    for i, fac in enumerate(result.factors[:max_factors]):
        fy = fac_y + i * 22
        fac_colour = green_ok if fac.is_positive else red_bad
        fac_sym = "✦" if fac.is_positive else "✘"
        # Truncate description
        desc = fac.description_en[:72] + "…" if len(fac.description_en) > 72 else fac.description_en
        parts.extend([
            f'<rect x="{tbl_x}" y="{fy+2}" width="{tbl_w}" height="18" '
            f'rx="3" fill="{("rgba(26,96,48,0.12)" if fac.is_positive else "rgba(139,26,26,0.12)")}"/>',
            f'<text x="{tbl_x+12}" y="{fy+14}" font-size="10" fill="{fac_colour}">{fac_sym}</text>',
            f'<text x="{tbl_x+28}" y="{fy+14}" font-size="8.5" fill="{dark_ink}">'
            f'{_xml_escape(desc)}</text>',
            f'<text x="{tbl_x+tbl_w-8}" y="{fy+14}" text-anchor="end" font-size="8.5" '
            f'fill="{fac_colour}" font-weight="bold">{fac.score:+.0f}</text>',
        ])

    # ── Gandanta / Special Warning ───────────────────────────────
    if result.is_gandanta or result.gandanta_note:
        warn_y = fac_y + max_factors * 22 + 8
        parts.extend([
            f'<rect x="{tbl_x}" y="{warn_y}" width="{tbl_w}" height="26" '
            f'rx="4" fill="rgba(139,26,26,0.15)" stroke="{red_bad}" stroke-width="1"/>',
            f'<text x="{tbl_x+12}" y="{warn_y+17}" font-size="8.5" fill="{red_bad}">'
            f'⚠ Gandanta: {_xml_escape(result.gandanta_note[:80] if result.gandanta_note else "Moon in Gandanta")}</text>',
        ])

    # ── Bottom footer ─────────────────────────────────────────────
    parts.extend([
        f'<line x1="40" y1="{H-40}" x2="{W-40}" y2="{H-40}" '
        f'stroke="{saffron}" stroke-width="1" opacity="0.6"/>',
        f'<text x="{cx}" y="{H-24}" text-anchor="middle" font-size="8.5" '
        f'fill="{dark_ink}" font-style="italic" opacity="0.7">'
        f'Muhurta Chintamani · Kalaprakashika · BPHS</text>',
        f'<text x="{cx}" y="{H-12}" text-anchor="middle" font-size="7.5" '
        f'fill="{saffron}" opacity="0.7">'
        f'Ayanamsa (Lahiri): {result.ayanamsa:.4f}°</text>',
    ])

    parts.append('</svg>')
    return "\n".join(parts)


# ============================================================
# Streamlit UI Helpers
# ============================================================

def _quality_box(quality: str, quality_cn: str, stars: str, score: float) -> str:
    cls_map = {
        "Excellent": "quality-excellent",
        "Good": "quality-good",
        "Neutral": "quality-neutral",
        "Poor": "quality-poor",
        "Avoid": "quality-avoid",
    }
    cls = cls_map.get(quality, "quality-neutral")
    return (
        f'<div class="{cls}">'
        f'{stars} &nbsp; {html.escape(quality)} / {html.escape(quality_cn)} &nbsp; '
        f'({score:+.0f} pts)'
        f'</div>'
    )


def _render_western_result(result: WesternElectionalResult) -> None:
    """Render a WesternElectionalResult in Streamlit."""
    lang = get_lang()

    # Quality box
    st.markdown(_quality_box(result.quality, result.quality_cn, result.quality_stars, result.total_score),
                unsafe_allow_html=True)

    # SVG chart
    svg = render_western_electional_svg(result)
    st.components.v1.html(f"<div style='text-align:center'>{svg}</div>", height=640, scrolling=False)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="elect-section"><h4>🌙 Moon State / 月亮狀態</h4>', unsafe_allow_html=True)
        moon_class = "elect-moon-bad" if result.moon_is_voc or result.moon_in_via_combusta else "elect-moon-good"
        moon_text = f"{'⚠️ Void of Course' if result.moon_is_voc else '✓ Not Void'} | "
        moon_text += f"{'⚠️ Via Combusta' if result.moon_in_via_combusta else '✓ Not Via Combusta'} | "
        moon_text += f"{result.moon_phase_cn} ({result.moon_phase})"
        if result.moon_applies_to:
            moon_text += f" | Applies to: {result.moon_applies_to}"
        st.markdown(f'<div class="{moon_class}">{html.escape(moon_text)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="elect-section"><h4>⏰ Planetary Hour / 行星時</h4>', unsafe_allow_html=True)
        hour_glyph = PLANET_GLYPHS.get(result.planetary_hour_lord, "")
        hr_cn = PLANET_CN.get(result.planetary_hour_lord, result.planetary_hour_lord)
        suitable = "✓ Suitable" if result.planetary_hour_suitable else "○ Neutral"
        hour_class = "elect-moon-good" if result.planetary_hour_suitable else "factor-neutral"
        st.markdown(
            f'<div class="{hour_class}">'
            f'{hour_glyph} Hour of {html.escape(result.planetary_hour_lord)} '
            f'({html.escape(hr_cn)}) — Hour #{result.planetary_hour_number} — {suitable}'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Factors
    st.markdown('<div class="elect-section"><h4>📋 Electional Factors / 擇日因素</h4>', unsafe_allow_html=True)
    for fac in result.factors:
        cls = "factor-good" if fac.is_positive else "factor-bad"
        sym = "✦" if fac.is_positive else "✘"
        desc = fac.description_cn if lang == "zh" else fac.description_en
        ref = f" <em style='font-size:0.8em;opacity:0.7'>({html.escape(fac.source_ref)})</em>" if fac.source_ref else ""
        st.markdown(
            f'<div class="{cls}">{sym} {html.escape(desc)}'
            f'<span style="float:right;font-weight:bold">{fac.score:+.0f}</span>{ref}</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Traditional rules note
    activity = WESTERN_ACTIVITY_TYPES.get(result.activity_type, {})
    note = activity.get("notes_cn" if lang == "zh" else "notes_en", "")
    if note:
        st.markdown(
            f'<div class="classical-quote">'
            f'📖 {html.escape(note)}'
            f'</div>',
            unsafe_allow_html=True,
        )


def _render_vedic_result(result: VedicMuhurtaResult) -> None:
    """Render a VedicMuhurtaResult in Streamlit."""
    lang = get_lang()

    st.markdown(_quality_box(result.quality, result.quality_cn, result.quality_stars, result.total_score),
                unsafe_allow_html=True)

    svg = render_vedic_muhurta_svg(result)
    st.components.v1.html(f"<div style='text-align:center'>{svg}</div>", height=700, scrolling=False)

    # Panchanga
    st.markdown('<div class="elect-section"><h4>🌿 Panchanga — 五曆要素</h4>', unsafe_allow_html=True)
    for key, elem in result.panchanga.items():
        nat_sym = "✦" if elem.nature == "benefic" else ("✘" if elem.nature == "malefic" else "○")
        row_class = "panchanga-row panchanga-good" if elem.nature == "benefic" else (
            "panchanga-row panchanga-bad" if elem.nature == "malefic" else "panchanga-row")
        val = elem.value_cn if lang == "zh" else elem.value
        note = elem.notes_cn if lang == "zh" else elem.notes_en
        st.markdown(
            f'<div class="{row_class}">'
            f'<span class="panchanga-label">{nat_sym} {html.escape(elem.name)}</span>'
            f'<span class="panchanga-value">{html.escape(val)} — {html.escape(note[:60])}</span>'
            f'<span style="color:#D4AF37;font-weight:bold;margin-left:8px">{elem.score:+.0f}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Warnings
    if result.is_gandanta or result.gandanta_note:
        st.warning(f"⚠️ {result.gandanta_note or 'Moon in Gandanta — inauspicious junction.'}")

    # Factors
    st.markdown('<div class="elect-section"><h4>📋 Muhurta Factors / 擇時因素</h4>', unsafe_allow_html=True)
    for fac in result.factors:
        cls = "factor-good" if fac.is_positive else "factor-bad"
        sym = "✦" if fac.is_positive else "✘"
        desc = fac.description_cn if lang == "zh" else fac.description_en
        ref = f" <em style='font-size:0.8em;opacity:0.7'>({html.escape(fac.source_ref)})</em>" if fac.source_ref else ""
        st.markdown(
            f'<div class="{cls}">{sym} {html.escape(desc)}'
            f'<span style="float:right;font-weight:bold">{fac.score:+.0f}</span>{ref}</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Special notes
    act_info = VEDIC_ACTIVITY_TYPES.get(result.activity_type, {})
    note = act_info.get("special_notes_cn" if lang == "zh" else "special_notes_en", "")
    if note:
        st.markdown(
            f'<div class="classical-quote">📖 {html.escape(note)}</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# Main Streamlit Renderer
# ============================================================

def render_streamlit(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    **kwargs,
) -> None:
    """
    Main Streamlit renderer for the Electional / Muhurta module.

    Presents tabs for Western Traditional Electional and Vedic Muhurta,
    each with two sub-modes: validate a specific time, or search for best windows.
    """
    import streamlit.components.v1 as components
    st.markdown(_ELECTIONAL_CSS, unsafe_allow_html=True)
    lang = get_lang()

    st.markdown(
        '<div class="elect-header">'
        '<h2>⏳ 擇日占星 · Electional Astrology & Vedic Muhurta</h2>'
        '<p>Western Traditional Electional (Lilly/Bonatti) · Vedic Muhurta Panchanga '
        '(Muhurta Chintamani / Kalaprakashika / BPHS)</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    west_tab, vedic_tab = st.tabs([
        auto_cn("⚜️ 西方傳統擇日（Lilly/Bonatti）", "⚜️ Western Electional (Lilly/Bonatti)"),
        auto_cn("🪷 吠陀擇時（Vedic Muhurta）", "🪷 Vedic Muhurta"),
    ])

    with west_tab:
        _render_western_tab(year, month, day, hour, minute, timezone, latitude, longitude, location_name)

    with vedic_tab:
        _render_vedic_tab(year, month, day, hour, minute, timezone, latitude, longitude, location_name)


def _render_western_tab(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float, latitude: float, longitude: float,
    location_name: str,
) -> None:
    """Render Western Electional tab."""
    lang = get_lang()

    st.markdown(
        '<div class="classical-quote">'
        '"In elections, the Moon is the principal significator; '
        'see that she be free from impediments, and applying to some good planet." '
        '— William Lilly, <em>Christian Astrology</em> p. 383'
        '</div>',
        unsafe_allow_html=True,
    )

    # Activity type
    activity_options = list(WESTERN_ACTIVITY_TYPES.keys())
    activity_labels = {
        k: f"{WESTERN_ACTIVITY_TYPES[k]['cn']} / {WESTERN_ACTIVITY_TYPES[k]['en']}"
        for k in activity_options
    }
    act_type = st.selectbox(
        auto_cn("🏷️ 活動類型", "🏷️ Activity Type"),
        options=activity_options,
        format_func=lambda k: activity_labels[k],
        key="elect_west_activity",
    )

    mode = st.radio(
        auto_cn("🔍 模式", "🔍 Mode"),
        options=["validate", "search"],
        format_func=lambda x: auto_cn("✅ 驗證特定時間", "✅ Validate Specific Time") if x == "validate"
        else auto_cn("🔎 搜尋最佳時段", "🔎 Search Best Windows"),
        key="elect_west_mode",
        horizontal=True,
    )

    if mode == "validate":
        if st.button(auto_cn("🔮 分析此時間", "🔮 Analyse This Time"),
                     key="elect_west_validate", type="primary"):
            try:
                with st.spinner(auto_cn("計算西方傳統擇日…", "Computing Western Electional chart…")):
                    result = compute_western_electional(
                        year=year, month=month, day=day,
                        hour=hour, minute=minute,
                        timezone=timezone, latitude=latitude, longitude=longitude,
                        activity_type=act_type, location_name=location_name,
                    )
                _render_western_result(result)
            except Exception as e:
                st.error(f"Error: {e}")
                st.exception(e)

    else:  # search
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                auto_cn("🗓️ 搜尋起始日期", "🗓️ Search Start Date"),
                value=datetime(year, month, day).date(),
                key="elect_west_start",
            )
        with col2:
            end_date = st.date_input(
                auto_cn("🗓️ 搜尋結束日期", "🗓️ Search End Date"),
                value=(datetime(year, month, day) + timedelta(days=7)).date(),
                key="elect_west_end",
            )

        min_score = st.slider(
            auto_cn("⭐ 最低評分篩選", "⭐ Minimum Score Filter"),
            min_value=-30, max_value=60, value=15,
            key="elect_west_minscore",
        )
        max_results = st.slider(
            auto_cn("📋 最多結果數", "📋 Max Results"),
            min_value=3, max_value=20, value=8,
            key="elect_west_maxres",
        )

        if st.button(auto_cn("🔮 搜尋最佳吉時", "🔮 Search Auspicious Windows"),
                     key="elect_west_search", type="primary"):
            if start_date >= end_date:
                st.warning(auto_cn("結束日期必須晚於起始日期", "End date must be after start date"))
                return
            with st.spinner(auto_cn("搜尋中…可能需要數秒", "Searching… this may take a few seconds")):
                results = find_western_elections(
                    start_year=start_date.year, start_month=start_date.month, start_day=start_date.day,
                    end_year=end_date.year, end_month=end_date.month, end_day=end_date.day,
                    timezone=timezone, latitude=latitude, longitude=longitude,
                    activity_type=act_type, location_name=location_name,
                    min_score=float(min_score), max_results=max_results,
                    step_hours=1.0,
                )
            if not results:
                st.warning(auto_cn(
                    f"在所選日期範圍內未找到評分 ≥ {min_score} 的吉時。請放寬篩選條件或延長日期範圍。",
                    f"No windows with score ≥ {min_score} found in the selected range. "
                    f"Try lowering the minimum score or extending the date range."
                ))
            else:
                st.success(auto_cn(
                    f"找到 {len(results)} 個推薦時段，按評分由高至低排列：",
                    f"Found {len(results)} recommended windows, sorted by score:"
                ))
                for i, r in enumerate(results):
                    with st.expander(
                        f"#{i+1} {r.datetime_local.strftime('%Y-%m-%d %H:%M')} — "
                        f"{r.quality_stars} {r.total_score:+.0f} pts ({r.quality})",
                        expanded=(i == 0),
                    ):
                        _render_western_result(r)


def _render_vedic_tab(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float, latitude: float, longitude: float,
    location_name: str,
) -> None:
    """Render Vedic Muhurta tab."""
    lang = get_lang()

    st.markdown(
        '<div class="classical-quote">'
        '"चन्द्रबलं तिथिश्च नक्षत्रं वारयोगकरणं च। '
        'पञ्चाङ्गशुद्धौ सर्वं शुभं भवति।" '
        '— Moon-strength, Tithi, Nakshatra, Vara, Yoga, Karana — when the Panchanga is pure, '
        'all is auspicious. · <em>Muhurta Chintamani</em>'
        '</div>',
        unsafe_allow_html=True,
    )

    activity_options = list(VEDIC_ACTIVITY_TYPES.keys())
    activity_labels = {
        k: f"{VEDIC_ACTIVITY_TYPES[k]['cn']} / {VEDIC_ACTIVITY_TYPES[k]['en']}"
        for k in activity_options
    }
    act_type = st.selectbox(
        auto_cn("🏷️ 活動類型", "🏷️ Activity Type"),
        options=activity_options,
        format_func=lambda k: activity_labels[k],
        key="elect_vedic_activity",
    )

    mode = st.radio(
        auto_cn("🔍 模式", "🔍 Mode"),
        options=["validate", "search"],
        format_func=lambda x: auto_cn("✅ 驗證特定時間", "✅ Validate Specific Time") if x == "validate"
        else auto_cn("🔎 搜尋最佳 Muhurta", "🔎 Search Best Muhurta"),
        key="elect_vedic_mode",
        horizontal=True,
    )

    if mode == "validate":
        if st.button(auto_cn("🪷 分析此 Muhurta", "🪷 Analyse This Muhurta"),
                     key="elect_vedic_validate", type="primary"):
            try:
                with st.spinner(auto_cn("計算吠陀擇時…", "Computing Vedic Muhurta…")):
                    result = compute_vedic_muhurta(
                        year=year, month=month, day=day,
                        hour=hour, minute=minute,
                        timezone=timezone, latitude=latitude, longitude=longitude,
                        activity_type=act_type, location_name=location_name,
                    )
                _render_vedic_result(result)
            except Exception as e:
                st.error(f"Error: {e}")
                st.exception(e)

    else:  # search
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                auto_cn("🗓️ 搜尋起始日期", "🗓️ Search Start Date"),
                value=datetime(year, month, day).date(),
                key="elect_vedic_start",
            )
        with col2:
            end_date = st.date_input(
                auto_cn("🗓️ 搜尋結束日期", "🗓️ Search End Date"),
                value=(datetime(year, month, day) + timedelta(days=7)).date(),
                key="elect_vedic_end",
            )

        min_score = st.slider(
            auto_cn("⭐ 最低評分篩選", "⭐ Minimum Score Filter"),
            min_value=-30, max_value=60, value=15,
            key="elect_vedic_minscore",
        )
        max_results = st.slider(
            auto_cn("📋 最多結果數", "📋 Max Results"),
            min_value=3, max_value=20, value=8,
            key="elect_vedic_maxres",
        )

        if st.button(auto_cn("🪷 搜尋最佳吉時", "🪷 Search Auspicious Muhurtas"),
                     key="elect_vedic_search", type="primary"):
            if start_date >= end_date:
                st.warning(auto_cn("結束日期必須晚於起始日期", "End date must be after start date"))
                return
            with st.spinner(auto_cn("搜尋吠陀吉時中…", "Searching Vedic Muhurtas…")):
                results = find_vedic_muhurtas(
                    start_year=start_date.year, start_month=start_date.month, start_day=start_date.day,
                    end_year=end_date.year, end_month=end_date.month, end_day=end_date.day,
                    timezone=timezone, latitude=latitude, longitude=longitude,
                    activity_type=act_type, location_name=location_name,
                    min_score=float(min_score), max_results=max_results,
                    step_hours=1.0,
                )
            if not results:
                st.warning(auto_cn(
                    f"在所選日期範圍內未找到評分 ≥ {min_score} 的吉時。請放寬篩選條件或延長日期範圍。",
                    f"No Muhurtas with score ≥ {min_score} found in the selected range."
                ))
            else:
                st.success(auto_cn(
                    f"找到 {len(results)} 個推薦 Muhurta，按評分由高至低排列：",
                    f"Found {len(results)} recommended Muhurtas, sorted by score:"
                ))
                for i, r in enumerate(results):
                    with st.expander(
                        f"#{i+1} {r.datetime_local.strftime('%Y-%m-%d %H:%M')} — "
                        f"{r.quality_stars} {r.total_score:+.0f} pts ({r.quality})",
                        expanded=(i == 0),
                    ):
                        _render_vedic_result(r)
