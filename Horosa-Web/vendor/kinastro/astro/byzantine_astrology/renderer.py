"""
astro/byzantine_astrology/renderer.py — Streamlit UI for Byzantine Astrology

Renders a multi-tab Byzantine-aesthetic interface:
  Tab 1: 本命拜占庭排盤  — Byzantine Natal Chart
  Tab 2: 政治占星        — Political Astrology
  Tab 3: 徵兆解讀        — Omen Interpretation (Seismologia/Selenodromia/Vrontologia)
  Tab 4: 歷史案例        — Historical Charts
  Tab 5: 占星師與技法    — Astrologers & Techniques

Byzantine aesthetic: gold on dark background, mosaic-style, Greek manuscript-inspired.

Sources:
- Rhetorius of Egypt, "Compendium" (ca. 6th c.)
- Hephaestion of Thebes, "Apotelesmatika" (ca. 415 CE)
- Paulus Alexandrinus, "Eisagogika" (378 CE)
- Catalogus Codicum Astrologorum Graecorum (CCAG)
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Dict, List, Optional, Any

import streamlit as st

from .calculator import (
    ByzantineChart,
    ByzantinePlanetPos,
    ByzantineLot,
    ByzantineAspect,
    FirdarPeriod,
    OmenAnalysis,
    compute_byzantine_chart,
    load_historical_chart,
    _sign_from_lon,
)
from .constants import (
    BYZANTINE_ASTROLOGERS,
    BYZANTINE_SIGN_NAMES,
    BYZANTINE_PLANET_NAMES,
    CLASSICAL_PLANET_ORDER,
    BYZANTINE_HOUSES,
    BYZANTINE_LOTS,
    BYZANTINE_ASPECTS,
    BYZANTINE_TRIPLICITY_LORDS,
    CHRISTIAN_SYNCRETISM,
    SEISMOLOGIA,
    SELENODROMIA,
    VRONTOLOGIA,
    THEOPHILUS_MILITARY_RULES,
    ARABO_BYZANTINE_TECHNIQUES,
    POLITICAL_HOROSCOPES,
    ZODIAC_SIGN_ORDER,
)
from astro.i18n import auto_cn, get_lang, t

# ============================================================
# CSS — Byzantine Gold & Mosaic Aesthetic
# ============================================================

_CSS = """
<style>
/* ── Byzantine Header ──────────────────────────────── */
.byz-header {
    background: linear-gradient(135deg, #1a0e00 0%, #3d2400 40%, #1a0e00 100%);
    border: 2px solid #C9A84C;
    border-radius: 8px;
    padding: 18px 24px;
    margin-bottom: 18px;
    box-shadow: 0 0 24px rgba(201,168,76,0.25);
    position: relative;
    overflow: hidden;
}
.byz-header::before {
    content: '✚';
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 3em;
    color: rgba(201,168,76,0.15);
    pointer-events: none;
}
.byz-header h2 { color: #C9A84C; margin: 0 0 4px 0; font-size: 1.45em; letter-spacing: 0.04em; }
.byz-header p  { color: #d4b896; margin: 0; font-size: 0.88em; }

/* ── Gold Divider ───────────────────────────────────── */
.byz-divider {
    border: none;
    border-top: 1px solid #C9A84C44;
    margin: 16px 0;
}

/* ── Planet Cards ───────────────────────────────────── */
.byz-planet-card {
    background: rgba(30, 18, 4, 0.9);
    border: 1px solid #C9A84C55;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    transition: border-color 0.2s;
}
.byz-planet-card:hover { border-color: #C9A84C; }
.byz-planet-card h4 { color: #C9A84C; margin: 0 0 4px 0; font-size: 1em; }
.byz-planet-card .greek { color: #a08050; font-style: italic; font-size: 0.85em; }
.byz-planet-card .position { color: #e8d4a8; font-size: 0.9em; }
.byz-planet-card .dignity { font-size: 0.8em; padding: 1px 6px; border-radius: 3px; }
.dignity-domicile   { background: rgba(40,200,100,0.18); color: #40c870; }
.dignity-exaltation { background: rgba(200,160,40,0.18); color: #C9A84C; }
.dignity-detriment  { background: rgba(220,60,60,0.18);  color: #dc6060; }
.dignity-fall       { background: rgba(180,60,180,0.18); color: #c060c0; }
.dignity-peregrine  { background: rgba(100,100,100,0.18); color: #999; }

/* ── Aspect Table ───────────────────────────────────── */
.byz-aspect-row {
    border-left: 3px solid;
    border-radius: 4px;
    padding: 6px 10px;
    margin-bottom: 5px;
    font-size: 0.88em;
    background: rgba(30,18,4,0.6);
}

/* ── Lot Cards ──────────────────────────────────────── */
.byz-lot-card {
    background: rgba(20, 12, 3, 0.85);
    border: 1px solid #9B6E2055;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 6px;
}
.byz-lot-card h5 { color: #9B6E20; margin: 0 0 3px 0; font-size: 0.92em; }
.byz-lot-card .gr { color: #7a5018; font-style: italic; font-size: 0.82em; }

/* ── Omen Cards ─────────────────────────────────────── */
.byz-omen-severe   { border-left: 4px solid #dc3545; background: rgba(220,53,69,0.1);  border-radius:5px; padding: 10px 14px; margin-bottom: 8px; }
.byz-omen-moderate { border-left: 4px solid #fd7e14; background: rgba(253,126,20,0.1); border-radius:5px; padding: 10px 14px; margin-bottom: 8px; }
.byz-omen-mild     { border-left: 4px solid #28a745; background: rgba(40,167,69,0.1);  border-radius:5px; padding: 10px 14px; margin-bottom: 8px; }
.byz-omen-severe h5   { color: #dc3545; margin: 0 0 4px 0; }
.byz-omen-moderate h5 { color: #fd7e14; margin: 0 0 4px 0; }
.byz-omen-mild h5     { color: #28a745; margin: 0 0 4px 0; }

/* ── Astrologer Card ────────────────────────────────── */
.byz-astrologer {
    background: linear-gradient(135deg, rgba(30,18,4,0.95), rgba(50,30,8,0.95));
    border: 1px solid #C9A84C77;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 14px;
}
.byz-astrologer h3 { color: #C9A84C; margin: 0 0 2px 0; }
.byz-astrologer .gr-name { color: #a08050; font-style: italic; font-size: 0.9em; }
.byz-astrologer .period  { color: #888; font-size: 0.82em; }

/* ── Historical Chart Card ──────────────────────────── */
.byz-hist-card {
    background: rgba(25, 14, 4, 0.92);
    border: 1px solid #8B6914;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.byz-hist-card h4 { color: #D4AF37; margin: 0 0 4px 0; }
.byz-hist-card .gr { color: #8B6914; font-style: italic; font-size: 0.85em; }

/* ── Profection Banner ──────────────────────────────── */
.byz-profection {
    background: linear-gradient(90deg, rgba(201,168,76,0.12), rgba(201,168,76,0.04));
    border: 1px solid #C9A84C55;
    border-radius: 8px;
    padding: 14px 20px;
    margin-bottom: 14px;
}

/* ── Syncretism Card ────────────────────────────────── */
.byz-sync {
    background: rgba(15, 25, 50, 0.8);
    border: 1px solid #2E5AA855;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.byz-sync h5 { color: #5B8DD9; margin: 0 0 4px 0; }

/* ── Source Reference ───────────────────────────────── */
.byz-source { color: #666; font-size: 0.75em; font-style: italic; margin-top: 4px; }

/* ── Byzantine Cross SVG accent ────────────────────── */
.byz-cross { color: #C9A84C; opacity: 0.6; }
</style>
"""

# ============================================================
# SVG Helpers
# ============================================================

def _build_byzantine_chart_svg(chart: ByzantineChart) -> str:
    """
    Build a Byzantine-style horoscope wheel SVG.

    Inspired by medieval Greek papyrus horoscope format and
    Byzantine manuscript chart diagrams (square chart with
    12 houses radiating from center, gold on dark background).

    Args:
        chart: computed ByzantineChart

    Returns:
        HTML div containing inline SVG
    """
    W, H = 480, 480
    cx, cy = 240, 240
    outer_r = 210
    inner_r = 130
    label_r = 170

    gold = "#C9A84C"
    dark = "#1a0e00"
    gold_pale = "#8B6914"
    text_col = "#e8d4a8"

    svg_parts: List[str] = []

    # Background
    svg_parts.append(f'<rect width="{W}" height="{H}" fill="{dark}" rx="12"/>')

    # Outer decorative border (mosaic-style)
    svg_parts.append(
        f'<rect x="4" y="4" width="{W-8}" height="{H-8}" '
        f'fill="none" stroke="{gold}" stroke-width="2" rx="10" '
        f'stroke-dasharray="8,4"/>'
    )

    # ── Draw 12 house sectors ─────────────────────────
    asc_lon = chart.ascendant
    asc_sign_idx = ZODIAC_SIGN_ORDER.index(chart.ascendant_sign)

    planet_by_house: Dict[int, List[ByzantinePlanetPos]] = {}
    for p in chart.planets:
        planet_by_house.setdefault(p.house, []).append(p)

    for house_num in range(1, 13):
        # Angle for house cusp: house 1 = ASC
        # In whole-sign houses, each house is exactly 30°
        # ASC is at left (180° in screen coords)
        sign_idx = (asc_sign_idx + house_num - 1) % 12

        # Convert to screen angle (0° = right, CCW)
        # ASC sign starts at 180° screen angle (left)
        start_angle_ecl = (asc_sign_idx + house_num - 1) * 30
        end_angle_ecl = start_angle_ecl + 30

        # Convert ecliptic (0=Aries, CCW) to screen (0=right, CW)
        def ecl_to_screen(ecl: float) -> float:
            return (180 - ecl) % 360

        start_scr = math.radians(ecl_to_screen(start_angle_ecl))
        end_scr = math.radians(ecl_to_screen(end_angle_ecl))

        # Sector path: arc from start to end
        def polar(r: float, angle: float) -> tuple:
            return (cx + r * math.cos(angle), cy - r * math.sin(angle))

        x1o, y1o = polar(outer_r, start_scr)
        x2o, y2o = polar(outer_r, end_scr)
        x1i, y1i = polar(inner_r, start_scr)
        x2i, y2i = polar(inner_r, end_scr)

        # Fill color — angular houses are brighter
        if house_num in (1, 4, 7, 10):
            fill = "rgba(201,168,76,0.08)"
            stroke_col = gold
        else:
            fill = "rgba(201,168,76,0.03)"
            stroke_col = gold_pale

        large_arc = 0  # 30° < 180°

        path = (
            f'M {x1i:.1f},{y1i:.1f} '
            f'L {x1o:.1f},{y1o:.1f} '
            f'A {outer_r},{outer_r} 0 {large_arc},0 {x2o:.1f},{y2o:.1f} '
            f'L {x2i:.1f},{y2i:.1f} '
            f'A {inner_r},{inner_r} 0 {large_arc},1 {x1i:.1f},{y1i:.1f} Z'
        )
        svg_parts.append(
            f'<path d="{path}" fill="{fill}" stroke="{stroke_col}" stroke-width="0.8"/>'
        )

        # House number
        mid_angle_scr = math.radians(ecl_to_screen(start_angle_ecl + 15))
        hx, hy = polar(label_r, mid_angle_scr)
        svg_parts.append(
            f'<text x="{hx:.1f}" y="{hy:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-size="10" fill="{gold_pale}">{house_num}</text>'
        )

        # Sign glyph
        sign_name = ZODIAC_SIGN_ORDER[sign_idx]
        sign_glyph = BYZANTINE_SIGN_NAMES[sign_name]["glyph"]
        gx, gy = polar(outer_r - 12, mid_angle_scr)
        svg_parts.append(
            f'<text x="{gx:.1f}" y="{gy:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-size="11" fill="{gold}">{sign_glyph}</text>'
        )

        # Planets in this house
        planets_in = planet_by_house.get(house_num, [])
        for pi, planet in enumerate(planets_in):
            px_base, py_base = polar(inner_r - 22 - pi * 14, mid_angle_scr)
            retro = "℞" if planet.is_retrograde else ""
            svg_parts.append(
                f'<text x="{px_base:.1f}" y="{py_base:.1f}" text-anchor="middle" '
                f'dominant-baseline="middle" font-size="13" fill="{text_col}">'
                f'{planet.glyph}{retro}</text>'
            )

    # ── Center emblem — Byzantine cross ───────────────
    cross_size = 18
    svg_parts.append(
        f'<text x="{cx}" y="{cy}" text-anchor="middle" '
        f'dominant-baseline="middle" font-size="{cross_size}" fill="{gold}" '
        f'opacity="0.7">✚</text>'
    )

    # ── ASC / MC labels ────────────────────────────────
    asc_scr = math.radians(ecl_to_screen(asc_lon))
    asc_px, asc_py = polar(outer_r + 16, asc_scr)
    svg_parts.append(
        f'<text x="{asc_px:.1f}" y="{asc_py:.1f}" text-anchor="middle" '
        f'font-size="9" fill="{gold}" font-weight="bold">ASC</text>'
    )

    mc_lon = chart.midheaven
    mc_scr = math.radians(ecl_to_screen(mc_lon))
    mc_px, mc_py = polar(outer_r + 16, mc_scr)
    svg_parts.append(
        f'<text x="{mc_px:.1f}" y="{mc_py:.1f}" text-anchor="middle" '
        f'font-size="9" fill="{gold_pale}" font-weight="bold">MC</text>'
    )

    svg_inner = "\n".join(svg_parts)
    return (
        f'<div style="display:flex;justify-content:center;margin:10px 0;">'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
        f'{svg_inner}'
        f'</svg></div>'
    )


def _build_omen_wheel_svg(omens: List[OmenAnalysis]) -> str:
    """
    Build a visual omen wheel SVG showing omen severity by compass direction.

    Args:
        omens: list of OmenAnalysis objects

    Returns:
        HTML string with SVG
    """
    W, H = 300, 300
    cx, cy = 150, 150
    R = 110

    gold = "#C9A84C"
    dark = "#0d0800"

    severity_colors = {"severe": "#dc3545", "moderate": "#fd7e14", "mild": "#28a745"}
    omen_types = {"seismologia": "🌍", "selenodromia": "🌙", "vrontologia": "⚡"}

    svg_parts = [
        f'<rect width="{W}" height="{H}" fill="{dark}" rx="10"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{gold}" stroke-width="1" opacity="0.3"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{R//2}" fill="none" stroke="{gold}" stroke-width="0.5" opacity="0.2"/>',
        # Cardinal direction lines
        f'<line x1="{cx}" y1="{cy-R}" x2="{cx}" y2="{cy+R}" stroke="{gold}" stroke-width="0.5" opacity="0.3"/>',
        f'<line x1="{cx-R}" y1="{cy}" x2="{cx+R}" y2="{cy}" stroke="{gold}" stroke-width="0.5" opacity="0.3"/>',
        # N/S/E/W labels
        f'<text x="{cx}" y="{cy-R-8}" text-anchor="middle" font-size="11" fill="{gold}">N</text>',
        f'<text x="{cx}" y="{cy+R+16}" text-anchor="middle" font-size="11" fill="{gold}">S</text>',
        f'<text x="{cx+R+8}" y="{cy+4}" text-anchor="middle" font-size="11" fill="{gold}">E</text>',
        f'<text x="{cx-R-8}" y="{cy+4}" text-anchor="middle" font-size="11" fill="{gold}">W</text>',
        # Center cross
        f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="16" fill="{gold}" opacity="0.5">✚</text>',
    ]

    # Plot omens as dots
    type_angle_map = {
        "seismologia": [0, 90, 180, 270],
        "selenodromia": [45, 135, 225, 315],
        "vrontologia": [22, 112, 202, 292],
    }
    plotted: List[tuple] = []

    for i, omen in enumerate(omens[:12]):  # max 12 shown
        angle = (i * 30 + 10) % 360
        r = R * 0.6 + (i % 3) * 15
        rad = math.radians(angle - 90)  # 0 = north
        x = cx + r * math.cos(rad)
        y = cy + r * math.sin(rad)
        color = severity_colors.get(omen.severity, "#888")
        svg_parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{color}" opacity="0.7"/>'
        )
        icon = omen_types.get(omen.omen_type, "•")
        svg_parts.append(
            f'<text x="{x:.1f}" y="{y+4:.1f}" text-anchor="middle" font-size="8" fill="white">{icon}</text>'
        )

    # Legend
    legend_y = H - 30
    for idx, (sev, col) in enumerate(severity_colors.items()):
        lx = 20 + idx * 90
        svg_parts.append(f'<circle cx="{lx+6}" cy="{legend_y}" r="5" fill="{col}" opacity="0.8"/>')
        svg_parts.append(
            f'<text x="{lx+14}" y="{legend_y+4}" font-size="9" fill="{gold}">{sev.capitalize()}</text>'
        )

    svg_inner = "\n".join(svg_parts)
    return (
        f'<div style="display:flex;justify-content:center;margin:10px 0;">'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
        f'{svg_inner}'
        f'</svg></div>'
    )


# ============================================================
# UI Rendering Functions
# ============================================================

def _render_planet_table(planets: List[ByzantinePlanetPos]) -> None:
    """Render a Byzantine-styled planet position table."""
    lang = get_lang()

    st.markdown(
        auto_cn(
            "**行星位置表 (Πλανήτες / Planets)**",
            en_text="**Planetary Positions (Πλανήτες)**",
        )
    )

    for p in planets:
        dignity_class = f"dignity-{p.dignity.lower()}"
        dignity_label = {
            "Domicile": auto_cn("廟", en_text="Domicile"),
            "Exaltation": auto_cn("旺", en_text="Exaltation"),
            "Detriment": auto_cn("陷", en_text="Detriment"),
            "Fall": auto_cn("落", en_text="Fall"),
            "Peregrine": auto_cn("游離", en_text="Peregrine"),
        }.get(p.dignity, p.dignity)

        planet_cn_name = BYZANTINE_PLANET_NAMES.get(p.name, {}).get("cn", p.name)
        sign_cn = p.sign_cn
        retro_badge = (
            ' <span style="color:#ff8888;font-size:0.8em">(℞)</span>'
            if p.is_retrograde else ""
        )

        st.markdown(
            f'<div class="byz-planet-card">'
            f'<h4>{p.glyph} {auto_cn(planet_cn_name, en_text=p.name)}'
            f' <span class="{dignity_class} dignity">{dignity_label}</span>{retro_badge}</h4>'
            f'<div class="greek">{BYZANTINE_PLANET_NAMES.get(p.name,{}).get("greek","")}</div>'
            f'<div class="position">'
            f'{auto_cn(sign_cn, en_text=p.sign)} {BYZANTINE_SIGN_NAMES[p.sign]["greek"]} '
            f'{p.degree_in_sign:.1f}° — '
            f'{auto_cn("第", en_text="House ")}{p.house}{auto_cn("宮", en_text="")}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _render_aspect_table(aspects: List[ByzantineAspect]) -> None:
    """Render Byzantine aspect table."""
    if not aspects:
        st.info(auto_cn("無顯著相位", en_text="No significant aspects found"))
        return

    st.markdown(
        auto_cn(
            "**相位表 (Σχηματισμοί / Aspects)**",
            en_text="**Aspect Table (Σχηματισμοί)**",
        )
    )

    for asp in sorted(aspects, key=lambda a: a.orb):
        p1_glyph = BYZANTINE_PLANET_NAMES.get(asp.planet1, {}).get("glyph", asp.planet1)
        p2_glyph = BYZANTINE_PLANET_NAMES.get(asp.planet2, {}).get("glyph", asp.planet2)
        p1_cn = BYZANTINE_PLANET_NAMES.get(asp.planet1, {}).get("cn", asp.planet1)
        p2_cn = BYZANTINE_PLANET_NAMES.get(asp.planet2, {}).get("cn", asp.planet2)
        applying = auto_cn("趨近", en_text="Applying") if asp.is_applying else auto_cn("分離", en_text="Separating")

        st.markdown(
            f'<div class="byz-aspect-row" style="border-color:{asp.color}">'
            f'{p1_glyph} {auto_cn(p1_cn, en_text=asp.planet1)} '
            f'<span style="color:{asp.color};font-size:1.2em">{asp.glyph}</span> '
            f'{p2_glyph} {auto_cn(p2_cn, en_text=asp.planet2)} — '
            f'<span style="color:{asp.color}">'
            f'{auto_cn(asp.aspect_name_cn, en_text=asp.aspect_name)}'
            f'</span> ({asp.orb:.1f}° orb, {applying})'
            f'<br/><span style="color:#888;font-size:0.82em">'
            f'{auto_cn(asp.quality_cn, en_text=asp.quality_en)}'
            f'</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _render_lots(lots: List[ByzantineLot]) -> None:
    """Render Byzantine lots (Κλῆροι)."""
    st.markdown(
        auto_cn(
            "**命份份額 (Κλῆροι / Lots)**",
            en_text="**Byzantine Lots (Κλῆροι)**",
        )
    )
    st.caption(
        auto_cn(
            "來源：保羅·亞歷山大里亞《占星入門》第14–24章",
            en_text="Source: Paulus Alexandrinus, Eisagogika ch. 14–24",
        )
    )

    for lot in lots:
        sign_cn = BYZANTINE_SIGN_NAMES[lot.sign]["cn"]
        sign_gr = lot.sign_gr
        st.markdown(
            f'<div class="byz-lot-card">'
            f'<h5>{auto_cn(lot.name_cn, en_text=lot.name_en)}</h5>'
            f'<div class="gr">{lot.name_gr} — {lot.formula_used}</div>'
            f'<div style="color:#e8d4a8;font-size:0.88em">'
            f'{auto_cn(sign_cn, en_text=lot.sign)} {sign_gr} '
            f'{lot.degree_in_sign:.1f}° — '
            f'{auto_cn("第", en_text="House ")}{lot.house}{auto_cn("宮", en_text="")}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _render_profection(chart: ByzantineChart) -> None:
    """Render annual profection analysis."""
    prf = chart.profection
    if not prf:
        st.info(auto_cn("無行運資料", en_text="No profection data available"))
        return

    lord_glyph = BYZANTINE_PLANET_NAMES.get(prf.lord_of_year, {}).get("glyph", "")
    lord_cn = BYZANTINE_PLANET_NAMES.get(prf.lord_of_year, {}).get("cn", prf.lord_of_year)
    sign_cn = BYZANTINE_SIGN_NAMES[prf.sign_activated]["cn"]

    st.markdown(
        f'<div class="byz-profection">'
        f'<h4 style="color:#C9A84C;margin:0 0 8px 0">'
        f'{auto_cn("年度行運（向運）Ἐπαφέσεις", en_text="Annual Profection (Ἐπαφέσεις)")}'
        f'</h4>'
        f'<div style="color:#e8d4a8">'
        f'{auto_cn("年齡", en_text="Age")}: <b>{prf.age}</b> — '
        f'{auto_cn("激活宮位", en_text="Activated House")}: '
        f'<b style="color:#C9A84C">{auto_cn("第", en_text="H")}{prf.house_activated}{auto_cn("宮", en_text="")}</b><br/>'
        f'{auto_cn("激活星座", en_text="Activated Sign")}: '
        f'<b>{auto_cn(sign_cn, en_text=prf.sign_activated)}</b> ({prf.sign_gr})<br/>'
        f'{auto_cn("年主", en_text="Lord of the Year")}: '
        f'<b style="color:#C9A84C">{lord_glyph} {auto_cn(lord_cn, en_text=prf.lord_of_year)}</b>'
        f'</div>'
        f'<hr style="border-color:#C9A84C33;margin:8px 0"/>'
        f'<div style="color:#d4b896;font-size:0.88em">'
        f'<b>{auto_cn("宮位象義", en_text="House Themes")}:</b> '
        f'{auto_cn("、".join(prf.house_significations_cn), en_text=", ".join(prf.house_significations_en))}'
        f'</div>'
        f'<div style="color:#888;font-size:0.8em;margin-top:4px">'
        f'{prf.house_name_en}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        auto_cn(
            "來源：保羅·亞歷山大里亞《占星入門》第31章；雷托里烏斯《綱要》",
            en_text="Source: Paulus Alexandrinus, Eisag. ch. 31; Rhetorius, Compend.",
        )
    )


def _render_firdaria(firdaria: List[FirdarPeriod], current_age: int = 30) -> None:
    """Render Firdaria (planetary period) table."""
    st.markdown(
        auto_cn(
            "**菲爾達里亞 (Firdaria) — 阿拉伯-拜占庭行星時期**",
            en_text="**Firdaria — Arabo-Byzantine Planetary Periods**",
        )
    )
    st.caption(
        auto_cn(
            "來源：埃德薩的塞奧菲盧斯；阿布·馬夏爾；拜占庭傳統",
            en_text="Source: Theophilus of Edessa; Abu Ma'shar; Byzantine tradition",
        )
    )

    # Show periods around current age
    relevant = [p for p in firdaria if p.end_year_age >= max(0, current_age - 5)][:12]

    for period in relevant:
        is_current = period.start_year_age <= current_age < period.end_year_age
        bg = "rgba(201,168,76,0.12)" if is_current else "rgba(30,18,4,0.6)"
        border = "#C9A84C" if is_current else "#4a3010"
        current_badge = (
            f' <span style="background:#C9A84C;color:#000;padding:1px 6px;'
            f'border-radius:3px;font-size:0.75em">'
            f'{auto_cn("當前", en_text="ACTIVE")}</span>'
            if is_current else ""
        )
        m_glyph = period.main_planet_glyph
        s_glyph = period.sub_planet_glyph
        m_cn = BYZANTINE_PLANET_NAMES.get(period.main_planet, {}).get("cn", period.main_planet)
        s_cn = BYZANTINE_PLANET_NAMES.get(period.sub_planet, {}).get("cn", period.sub_planet)

        st.markdown(
            f'<div style="background:{bg};border:1px solid {border};border-radius:6px;'
            f'padding:8px 12px;margin-bottom:5px;font-size:0.88em">'
            f'{m_glyph} <b>{auto_cn(m_cn, en_text=period.main_planet)}</b> / '
            f'{s_glyph} {auto_cn(s_cn, en_text=period.sub_planet)}{current_badge}<br/>'
            f'<span style="color:#888">'
            f'{auto_cn("年齡", en_text="Age")} {period.start_year_age:.1f}–{period.end_year_age:.1f}'
            f'</span><br/>'
            f'<span style="color:#b0946a;font-size:0.82em">'
            f'{auto_cn(period.quality_cn, en_text=period.quality_en)}'
            f'</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _render_omens(omens: List[OmenAnalysis]) -> None:
    """Render omen analysis (Seismologia, Selenodromia, Vrontologia)."""
    if not omens:
        st.info(auto_cn("無徵兆記錄", en_text="No omens found for this chart"))
        return

    # Group by type
    seismo = [o for o in omens if o.omen_type == "seismologia"]
    seleno = [o for o in omens if o.omen_type == "selenodromia"]
    vronto = [o for o in omens if o.omen_type == "vrontologia"]

    for group, title_zh, title_en, icon in [
        (seismo, "地震預兆（地震占）", "Seismologia — Earthquake Omens", "🌍"),
        (seleno, "月相預兆（月行占）", "Selenodromia — Moon Phase Omens", "🌙"),
        (vronto, "雷鳴預兆（雷鳴占）", "Vrontologia — Thunder Omens", "⚡"),
    ]:
        if not group:
            continue

        st.markdown(
            f'**{icon} {auto_cn(title_zh, en_text=title_en)}**'
        )

        for omen in group:
            css_class = f"byz-omen-{omen.severity}"
            sev_label = {
                "severe": auto_cn("嚴重", en_text="Severe"),
                "moderate": auto_cn("中等", en_text="Moderate"),
                "mild": auto_cn("輕微", en_text="Mild"),
            }.get(omen.severity, omen.severity)

            planet_cn = BYZANTINE_PLANET_NAMES.get(omen.trigger_planet, {}).get("cn", omen.trigger_planet)
            sign_cn = BYZANTINE_SIGN_NAMES.get(omen.trigger_sign, {}).get("cn", omen.trigger_sign) if omen.trigger_sign in BYZANTINE_SIGN_NAMES else omen.trigger_sign

            st.markdown(
                f'<div class="{css_class}">'
                f'<h5>{icon} {sev_label} — '
                f'{auto_cn(planet_cn, en_text=omen.trigger_planet)} '
                f'{auto_cn("於", en_text="in ")} '
                f'{auto_cn(sign_cn, en_text=omen.trigger_sign)}</h5>'
                f'<div style="color:#e8d4a8">{auto_cn(omen.omen_cn, en_text=omen.omen_en)}</div>'
                f'<div style="color:#999;font-size:0.82em">'
                f'{auto_cn("地區", en_text="Region")}: '
                f'{auto_cn(omen.region_cn, en_text=omen.region_en)}'
                f'</div>'
                f'<div class="byz-source">{omen.source_ref}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr class="byz-divider"/>', unsafe_allow_html=True)


# ============================================================
# Main Tab Renderers
# ============================================================

def _render_tab_natal(chart: ByzantineChart) -> None:
    """Tab 1: Byzantine Natal Chart."""
    col1, col2 = st.columns([1, 1])

    with col1:
        # Ascendant info
        asc_cn = BYZANTINE_SIGN_NAMES[chart.ascendant_sign]["cn"]
        asc_glyph = BYZANTINE_SIGN_NAMES[chart.ascendant_sign]["glyph"]
        sect = auto_cn("晝盤", en_text="Day Chart") if chart.is_day_chart else auto_cn("夜盤", en_text="Night Chart")

        st.markdown(
            f'<div class="byz-hist-card">'
            f'<h4>{asc_glyph} {auto_cn("上升星座", en_text="Ascendant Sign")}: '
            f'{auto_cn(asc_cn, en_text=chart.ascendant_sign)} '
            f'({chart.ascendant_sign_gr}) {chart.ascendant:.1f}°</h4>'
            f'<div style="color:#999;font-size:0.85em">'
            f'{sect} | '
            f'{auto_cn("中天", en_text="MC")}: '
            f'{BYZANTINE_SIGN_NAMES[ZODIAC_SIGN_ORDER[int(chart.midheaven // 30) % 12]]["glyph"]} '
            f'{chart.midheaven:.1f}°'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        _render_planet_table(chart.planets)

    with col2:
        # Byzantine chart wheel
        chart_svg = _build_byzantine_chart_svg(chart)
        st.markdown(chart_svg, unsafe_allow_html=True)

        st.markdown('<hr class="byz-divider"/>', unsafe_allow_html=True)
        _render_lots(chart.lots)

    st.markdown('<hr class="byz-divider"/>', unsafe_allow_html=True)

    col3, col4 = st.columns([1, 1])
    with col3:
        _render_aspect_table(chart.aspects)
    with col4:
        _render_profection(chart)

    st.markdown('<hr class="byz-divider"/>', unsafe_allow_html=True)

    # House significations
    with st.expander(auto_cn("🏛️ 十二宮象義（Τόποι / Places）", en_text="🏛️ Twelve House Significations (Τόποι)")):
        for house_num, house_data in BYZANTINE_HOUSES.items():
            has_planets = any(p.house == house_num for p in chart.planets)
            bg = "rgba(201,168,76,0.08)" if has_planets else "transparent"
            st.markdown(
                f'<div style="background:{bg};border-radius:4px;padding:6px 10px;margin-bottom:4px">'
                f'<b style="color:#C9A84C">{house_num}. '
                f'{auto_cn(house_data["name_cn"], en_text=house_data["name_en"])}</b><br/>'
                f'<span style="color:#b0946a;font-size:0.85em">'
                f'{auto_cn("、".join(house_data["signifies_cn"]), en_text=", ".join(house_data["signifies_en"]))}'
                f'</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.caption(
            auto_cn(
                "來源：雷托里烏斯《綱要》第57–112章；保羅·亞歷山大里亞第24章",
                en_text="Source: Rhetorius, Compend. chs. 57–112; Paulus Alex. ch. 24",
            )
        )


def _render_tab_political(chart: ByzantineChart) -> None:
    """Tab 2: Political Astrology — Byzantine mundane chart analysis."""
    st.markdown(
        auto_cn(
            "### 🏛️ 拜占庭政治占星（Mundane Astrology）",
            en_text="### 🏛️ Byzantine Political Astrology (Mundane)",
        )
    )
    st.markdown(
        auto_cn(
            (
                "拜占庭占星師為皇帝、城市和宗教建立「政治星盤」，"
                "以預測帝國的命運。以下分析適用於世俗（政治）解讀。"
            ),
            en_text=(
                "Byzantine astrologers cast 'political horoscopes' for emperors, cities, "
                "and religions to predict the fate of the Empire. "
                "The following analysis applies a mundane interpretation to the current chart."
            ),
        )
    )

    # Key house analysis for political charts
    st.markdown(
        auto_cn("**政治宮位解讀**", en_text="**Political House Analysis**")
    )

    political_houses = {
        1: auto_cn("人民與國家", en_text="The People & Nation"),
        4: auto_cn("土地、農業、反對黨", en_text="Land, Agriculture, Opposition"),
        7: auto_cn("外國關係、敵人、戰爭", en_text="Foreign Relations, Enemies, War"),
        10: auto_cn("皇帝、政府、最高權威", en_text="Emperor, Government, Supreme Authority"),
        9: auto_cn("教會、宗教、占星師", en_text="Church, Religion, Astrologers"),
        11: auto_cn("議會、皇帝的盟友", en_text="Senate, Emperor's Allies"),
    }

    for house_num, theme in political_houses.items():
        planets_here = [p for p in chart.planets if p.house == house_num]
        house_data = BYZANTINE_HOUSES.get(house_num, {})
        has_planets_str = ""
        if planets_here:
            planet_strs = [
                f"{p.glyph} {auto_cn(BYZANTINE_PLANET_NAMES.get(p.name,{}).get('cn',p.name), en_text=p.name)}"
                for p in planets_here
            ]
            has_planets_str = " | " + ", ".join(planet_strs)

        bg = "rgba(201,168,76,0.08)" if planets_here else "rgba(30,18,4,0.5)"
        st.markdown(
            f'<div style="background:{bg};border:1px solid #4a3010;border-radius:6px;'
            f'padding:10px 14px;margin-bottom:7px">'
            f'<b style="color:#C9A84C">H{house_num} — {theme}</b>{has_planets_str}<br/>'
            f'<span style="color:#888;font-size:0.82em">'
            f'{auto_cn("、".join(house_data.get("signifies_cn",[])), en_text=", ".join(house_data.get("signifies_en",[])))}'
            f'</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="byz-divider"/>', unsafe_allow_html=True)

    # Theophilus Military Rules
    with st.expander(
        auto_cn(
            "⚔️ 塞奧菲盧斯軍事占星規則",
            en_text="⚔️ Theophilus of Edessa's Military Rules",
        )
    ):
        for i, rule in enumerate(THEOPHILUS_MILITARY_RULES, 1):
            st.markdown(
                f'<div style="border-left:3px solid #B22222;padding:8px 12px;'
                f'margin-bottom:8px;background:rgba(178,34,34,0.06);border-radius:4px">'
                f'<b style="color:#B22222">{i}.</b> '
                f'{auto_cn(rule["rule_cn"], en_text=rule["rule_en"])}<br/>'
                f'<span class="byz-source">{rule["source"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Triplicity analysis
    with st.expander(
        auto_cn("🔥 三分性主宰分析", en_text="🔥 Triplicity Lord Analysis")
    ):
        for element, trip_data in BYZANTINE_TRIPLICITY_LORDS.items():
            element_icons = {"Fire": "🔥", "Earth": "🌍", "Air": "💨", "Water": "🌊"}
            icon = element_icons.get(element, "")
            day_lord_cn = BYZANTINE_PLANET_NAMES.get(trip_data["day_lord"], {}).get("cn", trip_data["day_lord"])
            night_lord_cn = BYZANTINE_PLANET_NAMES.get(trip_data["night_lord"], {}).get("cn", trip_data["night_lord"])
            co_lord_cn = BYZANTINE_PLANET_NAMES.get(trip_data.get("co_lord",""), {}).get("cn", trip_data.get("co_lord",""))

            st.markdown(
                f'<div style="border:1px solid #4a3010;border-radius:6px;'
                f'padding:10px 14px;margin-bottom:8px;background:rgba(30,18,4,0.7)">'
                f'<b style="color:#C9A84C">{icon} {element} '
                f'({", ".join(trip_data["signs"])})</b><br/>'
                f'{auto_cn("晝", en_text="Day Lord")}: '
                f'{BYZANTINE_PLANET_NAMES.get(trip_data["day_lord"],{}).get("glyph","")}'
                f' {auto_cn(day_lord_cn, en_text=trip_data["day_lord"])} | '
                f'{auto_cn("夜", en_text="Night Lord")}: '
                f'{BYZANTINE_PLANET_NAMES.get(trip_data["night_lord"],{}).get("glyph","")}'
                f' {auto_cn(night_lord_cn, en_text=trip_data["night_lord"])} | '
                f'{auto_cn("共主", en_text="Co-Lord")}: '
                f'{BYZANTINE_PLANET_NAMES.get(trip_data.get("co_lord",""),{}).get("glyph","")}'
                f' {auto_cn(co_lord_cn, en_text=trip_data.get("co_lord",""))}'
                f'<br/><span style="color:#888;font-size:0.82em">'
                f'{auto_cn(trip_data["byzantine_note_cn"], en_text=trip_data["byzantine_note_en"])}'
                f'</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


def _render_tab_omens(chart: ByzantineChart) -> None:
    """Tab 3: Omen Interpretation."""
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(
            auto_cn("### 🌍⚡🌙 天象徵兆解讀", en_text="### 🌍⚡🌙 Celestial Omen Interpretation")
        )
        st.markdown(
            auto_cn(
                (
                    "拜占庭占星師依據行星位置和月相解讀天象徵兆，"
                    "預測地震（地震占）、月相影響（月行占）和雷鳴（雷鳴占）。"
                    "以下基於當前星盤位置。"
                ),
                en_text=(
                    "Byzantine astrologers interpreted celestial omens from planetary positions "
                    "and Moon phases, predicting earthquakes (Seismologia), lunar influences "
                    "(Selenodromia), and thunder (Vrontologia). The following is based on "
                    "the current chart positions."
                ),
            )
        )
        _render_omens(chart.omens)

    with col2:
        # Omen wheel visualization
        st.markdown(
            auto_cn("**徵兆輪（視覺化）**", en_text="**Omen Wheel (Visualization)**")
        )
        wheel_svg = _build_omen_wheel_svg(chart.omens)
        st.markdown(wheel_svg, unsafe_allow_html=True)

        # Severity legend
        severity_legend = {
            "severe": (auto_cn("嚴重", en_text="Severe"), "#dc3545"),
            "moderate": (auto_cn("中等", en_text="Moderate"), "#fd7e14"),
            "mild": (auto_cn("輕微", en_text="Mild"), "#28a745"),
        }
        for sev, (label, color) in severity_legend.items():
            count = sum(1 for o in chart.omens if o.severity == sev)
            if count:
                st.markdown(
                    f'<span style="background:{color};color:white;padding:2px 8px;'
                    f'border-radius:3px;margin-right:6px;font-size:0.85em">'
                    f'{label}: {count}</span>',
                    unsafe_allow_html=True,
                )

        st.markdown("")

        # Monthly vrontologia reference
        with st.expander(
            auto_cn("📅 月度雷鳴占（完整表）", en_text="📅 Monthly Vrontologia Reference")
        ):
            month_names = list(VRONTOLOGIA.keys())
            for month_name in month_names:
                mdata = VRONTOLOGIA[month_name]
                st.markdown(
                    f'<div style="border-left:2px solid #C9A84C44;padding:6px 10px;margin-bottom:6px">'
                    f'<b style="color:#C9A84C">{mdata.get("month_cn",month_name)} '
                    f'({month_name}) {mdata.get("month_gr","")}</b><br/>'
                    f'<span style="font-size:0.82em;color:#d4b896">'
                    f'⬆️ {mdata.get("thunder_from_east",{}).get("omen_en","")} | '
                    f'⬇️ {mdata.get("thunder_from_south",{}).get("omen_en","")}'
                    f'</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


def _render_tab_historical(chart: ByzantineChart) -> None:
    """Tab 4: Historical Charts — Load and display preset Byzantine horoscopes."""
    st.markdown(
        auto_cn("### 👑 歷史政治星盤", en_text="### 👑 Historical Political Horoscopes")
    )
    st.markdown(
        auto_cn(
            "以下是拜占庭占星傳統中著名的政治星盤。點擊加載任何一個以查看其星盤分析。",
            en_text=(
                "The following are famous political horoscopes from the Byzantine astrological tradition. "
                "Click to load any one for chart analysis."
            ),
        )
    )

    for chart_key, chart_data in POLITICAL_HOROSCOPES.items():
        with st.expander(
            f'{chart_data["icon"]} {auto_cn(chart_data["name_cn"], en_text=chart_data["name_en"])}'
        ):
            # Display description
            st.markdown(
                f'<div class="byz-hist-card">'
                f'<h4>{auto_cn(chart_data["name_cn"], en_text=chart_data["name_en"])}</h4>'
                f'<div class="gr">{chart_data.get("name_gr","")}</div>'
                f'<div style="color:#888;font-size:0.82em">{chart_data.get("date_str","")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                auto_cn(chart_data["description_cn"], en_text=chart_data["description_en"])
            )

            # Key planets
            if "key_planets_en" in chart_data:
                st.markdown(
                    auto_cn("**主要行星詮釋**", en_text="**Key Planetary Interpretations**")
                )
                for planet, meaning in chart_data["key_planets_en"].items():
                    glyph = BYZANTINE_PLANET_NAMES.get(planet, {}).get("glyph", "")
                    st.markdown(f"- {glyph} **{planet}**: {meaning}")

            # Historical use
            if "historical_use_en" in chart_data:
                st.markdown(auto_cn("**歷史使用**", en_text="**Historical Use**"))
                for use in chart_data["historical_use_en"]:
                    st.markdown(f"- {use}")

            st.caption(f"📚 {chart_data.get('source_ref','')}")

            # Load button (only for charts with valid JD)
            if chart_data.get("julian_day_approx") is not None:
                if st.button(
                    auto_cn(f"🔭 加載此星盤", en_text=f"🔭 Load This Chart"),
                    key=f"load_hist_{chart_key}",
                ):
                    with st.spinner(auto_cn("計算歷史星盤…", en_text="Computing historical chart…")):
                        hist_chart = load_historical_chart(chart_key)
                    if hist_chart:
                        st.session_state[f"_byz_hist_{chart_key}"] = hist_chart
                        st.success(auto_cn("歷史星盤已加載", en_text="Historical chart loaded"))

                # Display if loaded
                if f"_byz_hist_{chart_key}" in st.session_state:
                    hist = st.session_state[f"_byz_hist_{chart_key}"]
                    st.markdown('<hr class="byz-divider"/>', unsafe_allow_html=True)
                    _render_planet_table(hist.planets)
            else:
                st.info(
                    auto_cn(
                        "此為神話性星盤，無法計算實際行星位置。",
                        en_text="This is a mythological chart; actual planetary positions cannot be computed.",
                    )
                )


def _render_tab_astrologers(chart: ByzantineChart) -> None:
    """Tab 5: Byzantine Astrologers & Techniques."""
    st.markdown(
        auto_cn(
            "### 🏛️ 拜占庭占星師與技法",
            en_text="### 🏛️ Byzantine Astrologers & Techniques",
        )
    )

    # Astrologer cards
    for key, astro in BYZANTINE_ASTROLOGERS.items():
        with st.expander(
            f'{astro["icon"]} {auto_cn(astro["name_cn"], en_text=astro["name_en"])} '
            f'({astro["floruit"]})'
        ):
            st.markdown(
                f'<div class="byz-astrologer">'
                f'<h3>{astro["icon"]} {auto_cn(astro["name_cn"], en_text=astro["name_en"])}</h3>'
                f'<div class="gr-name">{astro["name_gr"]}</div>'
                f'<div class="period">📅 {astro["floruit"]} | 📍 {astro["location"]} | ⏳ {astro["period"]}</div>'
                f'<hr style="border-color:#C9A84C22;margin:8px 0"/>'
                f'<div style="color:#C9A84C;font-size:0.88em">'
                f'📖 <i>{auto_cn(astro["work_cn"], en_text=astro["work_en"])}</i> '
                f'— {astro["work_gr"]}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                auto_cn("**主要貢獻**", en_text="**Key Contributions**")
            )
            contribs = auto_cn(
                astro["key_contributions_cn"],
                en_text=astro["key_contributions_en"],
            )
            if isinstance(contribs, list):
                for item in contribs:
                    st.markdown(f"- {item}")
            else:
                st.markdown(contribs)

            st.markdown(
                f'<div style="color:#C9A84C;font-size:0.88em">'
                f'🔑 {auto_cn("標誌性技法", en_text="Signature Technique")}: '
                f'<b>{astro["signature_technique"]}</b>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"📚 {astro['source_ref']}")

    st.markdown('<hr class="byz-divider"/>', unsafe_allow_html=True)

    # Christian-Astrological Syncretism
    st.markdown(
        auto_cn(
            "### ✝️ 基督教-占星融合",
            en_text="### ✝️ Christian-Astrological Syncretism",
        )
    )
    st.markdown(
        auto_cn(
            "拜占庭占星師將古典行星與基督教聖人和神學概念融合，創造了獨特的融合傳統。",
            en_text=(
                "Byzantine astrologers fused classical planetary symbolism with Christian "
                "saints and theological concepts, creating a unique syncretic tradition."
            ),
        )
    )

    for planet_key, sync_data in CHRISTIAN_SYNCRETISM.items():
        glyph = sync_data["glyph"]
        planet_cn = sync_data["planet_cn"]
        st.markdown(
            f'<div class="byz-sync">'
            f'<h5>{glyph} {auto_cn(planet_cn, en_text=planet_key)}</h5>'
            f'<div style="color:#e8d4a8;font-size:0.88em">'
            f'✝️ {auto_cn(sync_data["biblical_figure_cn"], en_text=sync_data["biblical_figure_en"])}<br/>'
            f'🕊️ {auto_cn(sync_data["saint_cn"], en_text=sync_data["saint_en"])}<br/>'
            f'📅 {auto_cn(sync_data["liturgical_day_cn"], en_text=sync_data["liturgical_day_en"])}'
            f'</div>'
            f'<div style="color:#aaa;font-size:0.82em;margin-top:6px">'
            f'{auto_cn(sync_data["theological_note_cn"], en_text=sync_data["theological_note_en"])}'
            f'</div>'
            f'<div class="byz-source">{sync_data["source_ref"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="byz-divider"/>', unsafe_allow_html=True)

    # Arabo-Byzantine Techniques
    st.markdown(
        auto_cn(
            "### 🌙 阿拉伯-拜占庭過渡技法",
            en_text="### 🌙 Arabo-Byzantine Transitional Techniques",
        )
    )

    for tech_key, tech_data in ARABO_BYZANTINE_TECHNIQUES.items():
        with st.expander(
            auto_cn(tech_data["name_cn"], en_text=tech_data["name_en"])
        ):
            st.markdown(
                f'<div class="byz-hist-card">'
                f'<div style="color:#888;font-size:0.82em">'
                f'{auto_cn(tech_data["origin_cn"], en_text=tech_data["origin_en"])}'
                f'</div>'
                f'<div style="color:#e8d4a8;margin-top:6px">'
                f'{auto_cn(tech_data["description_cn"], en_text=tech_data["description_en"])}'
                f'</div>'
                f'<div class="byz-source">{tech_data["source_ref"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ============================================================
# Main Entry Point
# ============================================================

def render_streamlit(
    year: int,
    month: int,
    day: int,
    hour: float,
    minute: float = 0.0,
    timezone: float = 0.0,
    latitude: float = 41.016,
    longitude: float = 28.977,
    location_name: str = "",
    **kwargs: Any,
) -> None:
    """
    Render the Byzantine Astrology Streamlit interface.

    Args:
        year: birth/event year
        month: birth/event month (1–12)
        day: birth/event day
        hour: hour (0–23)
        minute: minute (0–59)
        timezone: UTC offset in hours
        latitude: geographic latitude
        longitude: geographic longitude
        location_name: display name for location
        **kwargs: additional params (ignored)
    """
    # Inject CSS
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Header ──────────────────────────────────────
    st.markdown(
        f'<div class="byz-header">'
        f'<h2>✚ {auto_cn("拜占庭占星", en_text="Byzantine Astrology")} '
        f'— Βυζαντινὴ Ἀστρολογία</h2>'
        f'<p>'
        f'{auto_cn("東羅馬帝國占星傳統（公元4–15世紀）", en_text="Eastern Roman Empire Astrological Tradition (4th–15th Century CE)")} · '
        f'{auto_cn("希臘化 → 阿拉伯 → 拜占庭傳承", en_text="Hellenistic → Arabic → Byzantine Transmission")}'
        f'</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Compute chart ────────────────────────────────
    with st.spinner(t("spinner_byzantine_astrology")):
        chart = compute_byzantine_chart(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name or "Constantinople",
            # Show profection for age 30 by default (a common classical reference age)
            current_year=year + 30,
        )

    # ── Tabs ─────────────────────────────────────────
    tab_labels = [
        auto_cn("📜 本命拜占庭排盤", en_text="📜 Byzantine Natal Chart"),
        auto_cn("🏛️ 政治占星", en_text="🏛️ Political Astrology"),
        auto_cn("⚡ 徵兆解讀", en_text="⚡ Omen Interpretation"),
        auto_cn("👑 歷史案例", en_text="👑 Historical Charts"),
        auto_cn("🔬 占星師與技法", en_text="🔬 Astrologers & Techniques"),
    ]

    tabs = st.tabs(tab_labels)

    with tabs[0]:
        _render_tab_natal(chart)

    with tabs[1]:
        _render_tab_political(chart)

    with tabs[2]:
        _render_tab_omens(chart)

    with tabs[3]:
        _render_tab_historical(chart)

    with tabs[4]:
        _render_tab_astrologers(chart)

    # ── Firdaria at bottom ────────────────────────────
    with st.expander(
        auto_cn(
            "⏳ 菲爾達里亞行星時期 (Firdaria)",
            en_text="⏳ Firdaria Planetary Periods",
        )
    ):
        _render_firdaria(chart.firdaria, current_age=30)

    # ── Sources footer ────────────────────────────────
    st.markdown('<hr class="byz-divider"/>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="color:#555;font-size:0.75em">'
        f'📚 {auto_cn("主要來源", en_text="Primary Sources")}: '
        f'Paulus Alexandrinus, <i>Eisagogika</i> (378 CE) · '
        f'Rhetorius of Egypt, <i>Compendium</i> (ca. 515 CE) · '
        f'Hephaestion of Thebes, <i>Apotelesmatika</i> (ca. 415 CE) · '
        f'Theophilus of Edessa, <i>Apotelesmatics</i> (ca. 785 CE) · '
        f'<i>Catalogus Codicum Astrologorum Graecorum</i> (CCAG) · '
        f'Lydus, <i>De Ostentis</i>'
        f'</div>',
        unsafe_allow_html=True,
    )
