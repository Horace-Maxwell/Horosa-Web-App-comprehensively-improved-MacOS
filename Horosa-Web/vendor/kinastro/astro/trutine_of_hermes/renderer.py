"""
astro/trutine_of_hermes/renderer.py — 赫密士出生前世盤 Streamlit 介面

Prenatal Epoch (Trutine of Hermes) — Streamlit UI

美學風格：古典希臘化 × 煉金術 × 月光銀金主題

Provides a 5-tab interface:
  Tab 1 — 前世盤排盤     (Epoch Chart Calculation)
  Tab 2 — 與本命盤對照   (Natal vs Epoch Comparison)
  Tab 3 — 校正驗證       (Rectification Validation)
  Tab 4 — 靈魂層級解讀   (Soul-Level Interpretations)
  Tab 5 — 歷史與理論     (Historical Context & Theory)
"""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Dict, List, Optional

import streamlit as st

from .calculator import (
    PrenatalEpochChart,
    TrutineVariant,
    compute_epoch_chart,
    _normalize,
    _sign_name,
    _deg_in_sign,
    _format_lon_zh,
    _format_lon_en,
)
from .constants import (
    ZODIAC_SIGNS,
    ZODIAC_SIGN_ZH,
    ZODIAC_GLYPHS,
    PLANET_DISPLAY,
    TRUTINE_VARIANTS,
    TRUTINE_HISTORY,
    MOON_PHASE_NAMES,
    EPOCH_SOUL_THEMES,
    TRUTINE_GOLD,
    TRUTINE_SILVER,
    TRUTINE_PURPLE,
    TRUTINE_TEAL,
    TRUTINE_BG,
    TRUTINE_BORDER,
    TRUTINE_BORDER_SILVER,
)
from astro.i18n import auto_cn, get_lang, t

# ============================================================
# CSS
# ============================================================

_TRUTINE_CSS = """
<style>
/* ── Trutine of Hermes Module Styles ── */
.trutine-hero {
    background: linear-gradient(135deg,
        rgba(8,6,24,0.98) 0%,
        rgba(20,12,45,0.97) 40%,
        rgba(12,8,30,0.98) 100%);
    border: 1px solid rgba(201,162,39,0.32);
    border-radius: 18px;
    padding: 2rem 2.5rem 1.6rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 48px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.04);
}
.trutine-hero::before {
    content: "☿ ☽ ♄ ☿ ☽";
    position: absolute; top: 12px; right: 20px;
    color: rgba(201,162,39,0.20); font-size: 0.9rem; letter-spacing: 5px;
}
.trutine-hero-title {
    font-size: 1.75rem; font-weight: 700; color: #C9A227;
    font-family: 'Georgia', serif; margin: 0 0 0.3rem 0;
    text-shadow: 0 0 20px rgba(201,162,39,0.35);
    letter-spacing: 0.04em;
}
.trutine-hero-sub {
    font-size: 0.9rem; color: rgba(168,184,200,0.85);
    margin: 0 0 0.6rem 0; font-style: italic;
}
.trutine-badge {
    display: inline-block;
    background: rgba(201,162,39,0.12);
    border: 1px solid rgba(201,162,39,0.35);
    color: #C9A227; border-radius: 20px;
    padding: 2px 12px; font-size: 0.78rem;
    letter-spacing: 0.05em; margin-right: 6px;
}
.trutine-card {
    background: rgba(20,14,42,0.85);
    border: 1px solid rgba(201,162,39,0.22);
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 2px 16px rgba(0,0,0,0.35);
}
.trutine-card-silver {
    background: rgba(16,20,35,0.85);
    border: 1px solid rgba(168,184,200,0.22);
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.9rem;
}
.trutine-section-title {
    color: #C9A227; font-size: 1.05rem; font-weight: 600;
    font-family: 'Georgia', serif;
    border-bottom: 1px solid rgba(201,162,39,0.25);
    padding-bottom: 0.4rem; margin-bottom: 0.8rem;
}
.trutine-moon-indicator {
    display: flex; align-items: center; gap: 10px;
    background: rgba(168,184,200,0.08);
    border: 1px solid rgba(168,184,200,0.25);
    border-radius: 10px; padding: 10px 16px;
    margin: 8px 0;
}
.trutine-moon-glyph {
    font-size: 1.8rem; color: #A8B8C8;
    text-shadow: 0 0 12px rgba(168,184,200,0.5);
}
.trutine-rule-box {
    background: linear-gradient(135deg,
        rgba(201,162,39,0.08) 0%,
        rgba(45,155,138,0.06) 100%);
    border: 1px solid rgba(201,162,39,0.30);
    border-left: 4px solid #C9A227;
    border-radius: 8px; padding: 12px 16px; margin: 10px 0;
}
.trutine-verified {
    background: rgba(45,155,138,0.12);
    border: 1px solid rgba(45,155,138,0.40);
    border-radius: 8px; padding: 10px 14px; margin: 8px 0;
    color: #2D9B8A;
}
.trutine-unverified {
    background: rgba(139,32,32,0.12);
    border: 1px solid rgba(139,32,32,0.40);
    border-radius: 8px; padding: 10px 14px; margin: 8px 0;
    color: #EF4444;
}
.planet-row-natal {
    background: rgba(201,162,39,0.06);
    border-left: 3px solid #C9A227;
    border-radius: 4px; padding: 5px 10px; margin-bottom: 4px;
    font-size: 0.87rem;
}
.planet-row-epoch {
    background: rgba(168,184,200,0.06);
    border-left: 3px solid #A8B8C8;
    border-radius: 4px; padding: 5px 10px; margin-bottom: 4px;
    font-size: 0.87rem;
}
.aspect-conjunction { color: #FFD700; font-weight: 600; }
.aspect-opposition  { color: #FF4444; font-weight: 600; }
.aspect-trine       { color: #4CAF50; font-weight: 600; }
.aspect-square      { color: #FF8C00; font-weight: 600; }
.aspect-sextile     { color: #40E0D0; }
.aspect-other       { color: #A8B8C8; }
.gestation-timeline {
    background: rgba(16,12,36,0.9);
    border: 1px solid rgba(201,162,39,0.20);
    border-radius: 10px; padding: 14px 18px;
    margin: 10px 0;
    font-family: 'Courier New', monospace;
    font-size: 0.82rem; color: #A8B8C8;
}
.soul-insight-card {
    background: linear-gradient(135deg,
        rgba(123,94,167,0.10) 0%,
        rgba(8,6,24,0.95) 100%);
    border: 1px solid rgba(123,94,167,0.28);
    border-radius: 10px; padding: 12px 16px;
    margin-bottom: 10px;
}
.soul-insight-title { color: #C9A227; font-weight: 600; font-size: 0.95rem; }
.soul-insight-text  { color: #C8C8E0; font-size: 0.87rem; line-height: 1.55; margin-top: 5px; }
.hermetic-quote {
    border-left: 3px solid #C9A227;
    padding: 8px 16px;
    background: rgba(201,162,39,0.05);
    border-radius: 0 8px 8px 0;
    font-style: italic; color: #C0B090;
    margin: 12px 0;
}
</style>
"""

# ============================================================
# Helpers
# ============================================================

def _zh(zh_text: str, en_text: str = "") -> str:
    """Return bilingual text based on current language."""
    return auto_cn(zh_text, en_text)


def _planet_row_html(name: str, lon: float, retro: bool, chart_type: str) -> str:
    """Build an HTML row for a planet position."""
    lang = get_lang()
    pdata = PLANET_DISPLAY.get(name, {})
    glyph = pdata.get("glyph", "")
    color = pdata.get("color", "#888")
    display = pdata.get("zh" if lang == "zh" else "en", name)
    retro_mark = " ℞" if retro else ""
    pos_str = _format_lon_zh(lon) if lang == "zh" else _format_lon_en(lon)
    css_class = "planet-row-natal" if chart_type == "natal" else "planet-row-epoch"
    return (
        f'<div class="{css_class}">'
        f'<span style="color:{color};font-size:1.1em;">{glyph}</span> '
        f'<span style="color:#E0E0F0;">{display}{retro_mark}</span> '
        f'<span style="color:#A0A0C0;float:right;">{pos_str}</span>'
        f'</div>'
    )


def _aspect_color_class(asp_name: str) -> str:
    """Return CSS class for aspect colouring."""
    asp = asp_name.lower()
    if "conjunction" in asp:
        return "aspect-conjunction"
    if "opposition" in asp:
        return "aspect-opposition"
    if "trine" in asp:
        return "aspect-trine"
    if "square" in asp:
        return "aspect-square"
    if "sextile" in asp:
        return "aspect-sextile"
    return "aspect-other"


def _render_planet_table(
    planets: dict,
    asc: float,
    mc: float,
    house_cusps: List[float],
    chart_type: str = "natal",
) -> None:
    """Render planet positions in a compact HTML table."""
    lang = get_lang()

    # Build rows
    rows_html = ""
    order = ["Sun", "Moon", "Mercury", "Venus", "Mars",
             "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    for name in order:
        pos = planets.get(name)
        if pos is None:
            continue
        rows_html += _planet_row_html(name, pos.longitude, pos.retrograde, chart_type)

    # Add angles
    angles = [("ASC", asc), ("MC", mc), ("DSC", _normalize(asc + 180)), ("IC", _normalize(mc + 180))]
    for ang_name, ang_lon in angles:
        pdata = PLANET_DISPLAY.get(ang_name, {})
        display = pdata.get("zh" if lang == "zh" else "en", ang_name)
        color = pdata.get("color", "#888")
        pos_str = _format_lon_zh(ang_lon) if lang == "zh" else _format_lon_en(ang_lon)
        css_class = "planet-row-natal" if chart_type == "natal" else "planet-row-epoch"
        rows_html += (
            f'<div class="{css_class}" style="border-left-style:dashed;">'
            f'<span style="color:{color};">◈</span> '
            f'<span style="color:#D0D0F0;font-style:italic;">{display}</span> '
            f'<span style="color:#909090;float:right;">{pos_str}</span>'
            f'</div>'
        )

    st.markdown(rows_html, unsafe_allow_html=True)


def _render_zodiac_wheel_svg(
    natal_planets: dict,
    natal_asc: float,
    epoch_planets: Optional[dict] = None,
    epoch_asc: Optional[float] = None,
    natal_moon_lon: float = 0.0,
    epoch_angle: str = "ASC",
    label_natal: str = "本命",
    label_epoch: str = "前世盤",
) -> None:
    """Render a dual-ring zodiac wheel SVG showing Natal (inner) and Epoch (outer) charts."""
    cx, cy = 300, 300
    r_outer = 240   # outer boundary
    r_signs = 220   # sign band outer
    r_sign_inner = 195
    r_epoch_outer = 185  # Epoch planet ring outer
    r_epoch_inner = 155
    r_natal_outer = 145  # Natal planet ring outer
    r_natal_inner = 115
    r_inner = 100   # inner circle

    def lon_to_xy(lon: float, r: float) -> tuple:
        """Convert longitude to SVG x,y (0° Aries at 9 o'clock, clockwise)."""
        angle_deg = (lon - natal_asc) % 360
        rad = math.radians(90 - angle_deg)
        x = cx + r * math.cos(rad)
        y = cy - r * math.sin(rad)
        return x, y

    svg_parts = [
        f'<svg width="600" height="600" viewBox="0 0 600 600" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'style="background:radial-gradient(ellipse at center,#0d0820 0%,#060412 100%);">',
        # Outer circle
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" '
        f'stroke="rgba(201,162,39,0.40)" stroke-width="1.5"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_sign_inner}" fill="none" '
        f'stroke="rgba(201,162,39,0.25)" stroke-width="0.8"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_epoch_inner}" fill="none" '
        f'stroke="rgba(168,184,200,0.20)" stroke-width="0.8"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_natal_inner}" fill="none" '
        f'stroke="rgba(201,162,39,0.18)" stroke-width="0.8"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="rgba(8,6,24,0.6)" '
        f'stroke="rgba(201,162,39,0.15)" stroke-width="1"/>',
    ]

    # Sign dividers and glyphs
    sign_colors = {
        "fire": "#FF8C00", "earth": "#8B7355",
        "air": "#87CEEB",  "water": "#4169E1",
    }
    sign_elements = [
        "fire","earth","air","water","fire","earth",
        "air","water","fire","earth","air","water",
    ]
    sign_glyphs_list = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]

    for i in range(12):
        sign_lon = i * 30.0
        # Divider line at sign boundary
        x1, y1 = lon_to_xy(sign_lon, r_sign_inner)
        x2, y2 = lon_to_xy(sign_lon, r_outer)
        svg_parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="rgba(201,162,39,0.30)" stroke-width="0.8"/>'
        )
        # Sign glyph at midpoint
        mid_lon = sign_lon + 15.0
        gx, gy = lon_to_xy(mid_lon, (r_signs + r_sign_inner) / 2)
        elem = sign_elements[i]
        color = sign_colors[elem]
        svg_parts.append(
            f'<text x="{gx:.1f}" y="{gy:.1f}" '
            f'text-anchor="middle" dominant-baseline="central" '
            f'font-size="14" fill="{color}" opacity="0.85">'
            f'{sign_glyphs_list[i]}</text>'
        )

    # ASC line (dashed)
    ax, ay = lon_to_xy(natal_asc, r_outer)
    svg_parts.append(
        f'<line x1="{cx}" y1="{cy}" x2="{ax:.1f}" y2="{ay:.1f}" '
        f'stroke="rgba(0,255,127,0.55)" stroke-width="1.2" stroke-dasharray="4,3"/>'
    )
    svg_parts.append(
        f'<text x="{ax:.1f}" y="{ay:.1f}" '
        f'text-anchor="middle" dominant-baseline="central" '
        f'font-size="11" fill="rgba(0,255,127,0.9)" font-weight="bold">ASC</text>'
    )

    # Epoch planets (outer ring, silver)
    if epoch_planets and epoch_asc is not None:
        for name, pos in epoch_planets.items():
            if name not in ["Sun", "Moon", "Mercury", "Venus", "Mars",
                            "Jupiter", "Saturn"]:
                continue
            pdata = PLANET_DISPLAY.get(name, {})
            color = pdata.get("color", "#888")
            glyph = pdata.get("glyph", "?")
            px, py = lon_to_xy(pos.longitude, (r_epoch_outer + r_epoch_inner) / 2)
            svg_parts.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="9" '
                f'fill="rgba(16,12,36,0.85)" stroke="{color}" stroke-width="1.2"/>'
            )
            svg_parts.append(
                f'<text x="{px:.1f}" y="{py:.1f}" '
                f'text-anchor="middle" dominant-baseline="central" '
                f'font-size="10" fill="{color}">{glyph}</text>'
            )

        # Epoch ASC marker
        eax, eay = lon_to_xy(epoch_asc, r_epoch_outer)
        svg_parts.append(
            f'<text x="{eax:.1f}" y="{eay:.1f}" '
            f'text-anchor="middle" dominant-baseline="central" '
            f'font-size="9" fill="#A8B8C8" font-style="italic">Ep.ASC</text>'
        )

    # Natal planets (inner ring, gold)
    planet_order = ["Sun", "Moon", "Mercury", "Venus", "Mars",
                    "Jupiter", "Saturn"]
    for name in planet_order:
        pos = natal_planets.get(name)
        if pos is None:
            continue
        pdata = PLANET_DISPLAY.get(name, {})
        color = pdata.get("color", "#888")
        glyph = pdata.get("glyph", "?")
        px, py = lon_to_xy(pos.longitude, (r_natal_outer + r_natal_inner) / 2)
        svg_parts.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="10" '
            f'fill="rgba(8,6,24,0.9)" stroke="{color}" stroke-width="1.5"/>'
        )
        svg_parts.append(
            f'<text x="{px:.1f}" y="{py:.1f}" '
            f'text-anchor="middle" dominant-baseline="central" '
            f'font-size="11" fill="{color}" font-weight="500">{glyph}</text>'
        )

    # Highlight Natal Moon (special golden ring)
    moon_pos = natal_planets.get("Moon")
    if moon_pos:
        mx, my = lon_to_xy(moon_pos.longitude, (r_natal_outer + r_natal_inner) / 2)
        svg_parts.append(
            f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="13" '
            f'fill="none" stroke="#C9A227" stroke-width="2" stroke-dasharray="3,2"/>'
        )

    # Epoch Asc highlight (if matches natal moon)
    if epoch_asc is not None:
        epoch_angle_lon = epoch_asc if epoch_angle == "ASC" else _normalize(epoch_asc + 180.0)
        ex, ey = lon_to_xy(epoch_angle_lon, r_epoch_inner - 8)
        svg_parts.append(
            f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="12" '
            f'fill="none" stroke="#A8B8C8" stroke-width="2.5" stroke-dasharray="4,2"/>'
        )

    # Center label
    svg_parts.append(
        f'<text x="{cx}" y="{cy-12}" '
        f'text-anchor="middle" font-size="12" fill="rgba(201,162,39,0.7)" font-family="Georgia,serif">'
        f'☽↔{epoch_angle}</text>'
    )
    svg_parts.append(
        f'<text x="{cx}" y="{cy+10}" '
        f'text-anchor="middle" font-size="9" fill="rgba(168,184,200,0.5)">'
        f'Trutine of Hermes</text>'
    )

    svg_parts.append("</svg>")
    st.markdown("".join(svg_parts), unsafe_allow_html=True)


def _render_gestation_timeline(chart: PrenatalEpochChart) -> None:
    """Render a simple text timeline of the gestation period."""
    lang = get_lang()
    days = chart.gestation_days
    weeks = days / 7.0

    # Moon phase emoji
    phase_emojis = {
        "new_moon": "🌑", "waxing_crescent": "🌒", "first_quarter": "🌓",
        "waxing_gibbous": "🌔", "full_moon": "🌕", "waning_gibbous": "🌖",
        "last_quarter": "🌗", "waning_crescent": "🌘",
    }
    phase_emoji = phase_emojis.get(chart.moon_phase_name, "🌙")
    phase_zh = MOON_PHASE_NAMES.get(chart.moon_phase_name, chart.moon_phase_name)

    timeline_html = f"""
<div class="gestation-timeline">
  <div style="color:#C9A227;font-weight:600;margin-bottom:8px;font-family:Georgia,serif;">
    {'妊娠期時間軸' if lang == 'zh' else 'Gestation Timeline'}
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
    <span style="color:#A8B8C8;">🌱 {'前世盤（受孕）：' if lang == 'zh' else 'Prenatal Epoch (Conception):'}</span>
    <span style="color:#C9A227;font-weight:500;">{chart.epoch_datetime_str}</span>
  </div>
  <div style="margin:8px 0;padding:4px 0;border-top:1px solid rgba(201,162,39,0.15);
              border-bottom:1px solid rgba(201,162,39,0.15);">
    <span style="color:#7B5EA7;">{'⟶  妊娠期：' if lang == 'zh' else '⟶  Gestation:'}</span>
    <span style="color:#C9A227;font-weight:600;"> {days:.1f} {'天' if lang == 'zh' else 'days'}
    ({weeks:.1f} {'週' if lang == 'zh' else 'weeks'})</span>
    <span style="color:#888;font-size:0.85em;">
      {'（標準：273天）' if lang == 'zh' else ' (standard: 273 days)'}
    </span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
    <span style="color:#A8B8C8;">👶 {'本命出生：' if lang == 'zh' else 'Birth:'}</span>
    <span style="color:#C9A227;font-weight:500;">{chart.birth_datetime_str}</span>
  </div>
  <div style="margin-top:10px;padding-top:8px;border-top:1px dashed rgba(168,184,200,0.15);">
    <span style="color:#888;">{'出生時月相：' if lang == 'zh' else 'Moon phase at birth:'}</span>
    <span style="color:#A8B8C8;">{phase_emoji} {phase_zh}</span>
    <span style="color:#666;">（{'上弦（漸盈）' if chart.is_waxing else '下弦（漸虧）'}，
    {'伸長' if lang == 'zh' else 'elongation'} {chart.moon_elongation:.1f}°）</span>
  </div>
  <div style="margin-top:6px;">
    <span style="color:#888;">{'月亮位置：' if lang == 'zh' else 'Moon position:'}</span>
    <span style="color:#A8B8C8;">{'地平線' + ('上方' if chart.moon_above_horizon else '下方')
      if lang == 'zh' else 'Above horizon' if chart.moon_above_horizon else 'Below horizon'}</span>
    <span style="color:#C9A227;margin-left:8px;">→ {'前世盤' if lang == 'zh' else 'Epoch'} {chart.epoch_angle}
    = {'本命月亮' if lang == 'zh' else 'Natal Moon'}</span>
  </div>
</div>
"""
    st.markdown(timeline_html, unsafe_allow_html=True)


# ============================================================
# Tab Renderers
# ============================================================

def _render_tab_epoch_chart(chart: PrenatalEpochChart) -> None:
    """Tab 1: Epoch Chart calculation results and dual-chart display."""
    lang = get_lang()

    # Trutine Rule Box
    rule_text = (
        f"{'月亮在地平線' + ('上方' if chart.moon_above_horizon else '下方') + '，'}"
        f"{'前世盤上升點（ASC）= 本命月亮' if chart.epoch_angle == 'ASC' else '前世盤下降點（DSC）= 本命月亮'}"
        if lang == "zh"
        else (
            f"Moon {'above' if chart.moon_above_horizon else 'below'} horizon → "
            f"Epoch {'ASC' if chart.epoch_angle == 'ASC' else 'DSC'} = Natal Moon"
        )
    )
    moon_lon_str = (_format_lon_zh(chart.natal_moon_lon) if lang == "zh"
                    else _format_lon_en(chart.natal_moon_lon))

    epoch_angle_lon = (chart.epoch_asc if chart.epoch_angle == "ASC"
                       else chart.epoch_dsc)
    epoch_lon_str = (_format_lon_zh(epoch_angle_lon) if lang == "zh"
                     else _format_lon_en(epoch_angle_lon))

    verified_class = "trutine-verified" if chart.trutine_verified else "trutine-unverified"
    match_icon = "✅" if chart.trutine_verified else ("⚠️" if chart.trutine_match_orb < 3 else "❌")

    st.markdown(f"""
<div class="trutine-rule-box">
<div style="color:#C9A227;font-weight:600;margin-bottom:6px;">
  ☿ {'赫密士法則' if lang == 'zh' else 'Trutine of Hermes Rule'}
</div>
<div style="color:#D0C890;">{rule_text}</div>
<div style="margin-top:6px;font-size:0.87rem;">
  <span style="color:#A8B8C8;">{'本命月亮：' if lang == 'zh' else 'Natal Moon: '}</span>
  <span style="color:#C9A227;font-weight:600;">{moon_lon_str}</span>
  <span style="color:#888;margin:0 8px;">→</span>
  <span style="color:#A8B8C8;">{'前世盤' if lang == 'zh' else 'Epoch'} {chart.epoch_angle}：</span>
  <span style="color:#C9A227;font-weight:600;">{epoch_lon_str}</span>
</div>
</div>
<div class="{verified_class}" style="margin-top:6px;">
  {match_icon} {'誤差 ' if lang == 'zh' else 'Orb: '}<strong>{chart.trutine_match_orb:.2f}°</strong>
  {' — 赫密士法則驗證' + ('通過' if chart.trutine_verified else '未通過') if lang == 'zh'
   else ' — Trutine ' + ('verified' if chart.trutine_verified else 'not verified')}
</div>
""", unsafe_allow_html=True)

    # Gestation Timeline
    _render_gestation_timeline(chart)

    # Dual chart columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f'<div class="trutine-section-title">{"🌙 本命盤" if lang == "zh" else "🌙 Natal Chart"}</div>',
            unsafe_allow_html=True,
        )
        st.caption(chart.birth_datetime_str)
        _render_planet_table(
            chart.natal_planets, chart.natal_asc, chart.natal_mc,
            chart.natal_house_cusps, chart_type="natal",
        )

    with col2:
        st.markdown(
            f'<div class="trutine-section-title">{"✨ 前世盤（Prenatal Epoch）" if lang == "zh" else "✨ Prenatal Epoch Chart"}</div>',
            unsafe_allow_html=True,
        )
        st.caption(chart.epoch_datetime_str)
        _render_planet_table(
            chart.epoch_planets, chart.epoch_asc, chart.epoch_mc,
            chart.epoch_house_cusps, chart_type="epoch",
        )

    # Zodiac wheel visualization
    st.markdown("---")
    st.markdown(
        f'<div class="trutine-section-title">{"☿ 雙圈天球圖（前世盤外環・本命盤內環）" if lang == "zh" else "☿ Dual Zodiac Wheel (Epoch outer · Natal inner)"}</div>',
        unsafe_allow_html=True,
    )
    _render_zodiac_wheel_svg(
        natal_planets=chart.natal_planets,
        natal_asc=chart.natal_asc,
        epoch_planets=chart.epoch_planets,
        epoch_asc=chart.epoch_asc,
        natal_moon_lon=chart.natal_moon_lon,
        epoch_angle=chart.epoch_angle,
        label_natal=_zh("本命", "Natal"),
        label_epoch=_zh("前世盤", "Epoch"),
    )


def _render_tab_comparison(chart: PrenatalEpochChart) -> None:
    """Tab 2: Natal vs Epoch comparison with cross-aspects."""
    lang = get_lang()

    st.markdown(
        f'<div class="trutine-section-title">{"⚡ 前世盤與本命盤的相互相位" if lang == "zh" else "⚡ Cross-Aspects Between Epoch and Natal Charts"}</div>',
        unsafe_allow_html=True,
    )

    if not chart.cross_aspects:
        st.info(_zh("未找到顯著相位", "No significant aspects found"))
        return

    # Display top cross-aspects
    asp_data = []
    for asp in chart.cross_aspects[:30]:
        asp_data.append({
            _zh("前世盤行星", "Epoch Planet"): asp.epoch_planet,
            _zh("相位", "Aspect"): asp.aspect_name,
            _zh("本命行星", "Natal Planet"): asp.natal_planet,
            _zh("誤差", "Orb"): f"{asp.orb:.2f}°",
        })

    if asp_data:
        import pandas as pd
        df = pd.DataFrame(asp_data)
        st.dataframe(df, width="stretch")

    # Notable aspects (orb < 1°)
    tight_aspects = [a for a in chart.cross_aspects if a.orb < 1.0]
    if tight_aspects:
        st.markdown("---")
        st.markdown(
            f'<div class="trutine-section-title">{"🔑 緊密相位（< 1°）" if lang == "zh" else "🔑 Tight Aspects (< 1°)"}</div>',
            unsafe_allow_html=True,
        )
        for asp in tight_aspects:
            css = _aspect_color_class(asp.aspect_name)
            st.markdown(
                f'<div style="padding:6px 12px;margin:4px 0;background:rgba(20,14,42,0.7);">'
                f'<span style="color:#A8B8C8;">{asp.epoch_planet}</span> '
                f'<span class="{css}">{asp.aspect_name}</span> '
                f'<span style="color:#A8B8C8;">{asp.natal_planet}</span> '
                f'<span style="color:#666;font-size:0.85em;"> ({asp.orb:.2f}°)</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Planet-by-planet position comparison table
    st.markdown("---")
    st.markdown(
        f'<div class="trutine-section-title">{"📊 行星位置對照表" if lang == "zh" else "📊 Planet Position Comparison"}</div>',
        unsafe_allow_html=True,
    )

    comparison_data = []
    planets_to_compare = ["Sun", "Moon", "Mercury", "Venus", "Mars",
                          "Jupiter", "Saturn"]
    for pname in planets_to_compare:
        natal_pos = chart.natal_planets.get(pname)
        epoch_pos = chart.epoch_planets.get(pname)
        if not natal_pos or not epoch_pos:
            continue

        pdata = PLANET_DISPLAY.get(pname, {})
        display = pdata.get("zh" if lang == "zh" else "en", pname)

        natal_str = (_format_lon_zh(natal_pos.longitude) if lang == "zh"
                     else _format_lon_en(natal_pos.longitude))
        epoch_str = (_format_lon_zh(epoch_pos.longitude) if lang == "zh"
                     else _format_lon_en(epoch_pos.longitude))

        # Shortest arc between natal and epoch positions
        diff = abs(natal_pos.longitude - epoch_pos.longitude) % 360
        if diff > 180:
            diff = 360 - diff

        comparison_data.append({
            _zh("行星", "Planet"): display,
            _zh("本命盤", "Natal"): natal_str,
            _zh("前世盤", "Epoch"): epoch_str,
            _zh("差距", "Difference"): f"{diff:.1f}°",
        })

    if comparison_data:
        import pandas as pd
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, width="stretch")


def _render_tab_rectification(chart: PrenatalEpochChart) -> None:
    """Tab 3: Rectification validation using the Trutine of Hermes."""
    lang = get_lang()

    # Rectification note (from calculator)
    st.markdown(
        f'<div class="trutine-card">{chart.rectification_note}</div>',
        unsafe_allow_html=True,
    )

    # Detailed match info
    moon_lon_str = (_format_lon_zh(chart.natal_moon_lon) if lang == "zh"
                    else _format_lon_en(chart.natal_moon_lon))
    epoch_angle_lon = chart.epoch_asc if chart.epoch_angle == "ASC" else chart.epoch_dsc
    epoch_lon_str = (_format_lon_zh(epoch_angle_lon) if lang == "zh"
                     else _format_lon_en(epoch_angle_lon))

    st.markdown(
        f'<div class="trutine-card">'
        f'<div class="trutine-section-title">{"📐 赫密士法則匹配詳情" if lang == "zh" else "📐 Trutine Match Details"}</div>'
        f'<table style="width:100%;font-size:0.9rem;">'
        f'<tr><td style="color:#888;padding:4px 8px;">{"本命月亮" if lang == "zh" else "Natal Moon"}</td>'
        f'    <td style="color:#C9A227;font-weight:600;">{moon_lon_str}</td></tr>'
        f'<tr><td style="color:#888;padding:4px 8px;">{"目標角度" if lang == "zh" else "Target Angle"}</td>'
        f'    <td style="color:#C9A227;">{"前世盤 " if lang == "zh" else "Epoch "}{chart.epoch_angle}</td></tr>'
        f'<tr><td style="color:#888;padding:4px 8px;">{"實際角度位置" if lang == "zh" else "Actual Angle Position"}</td>'
        f'    <td style="color:#A8B8C8;">{epoch_lon_str}</td></tr>'
        f'<tr><td style="color:#888;padding:4px 8px;">{"誤差（Orb）" if lang == "zh" else "Orb"}</td>'
        f'    <td style="color:{"#2D9B8A" if chart.trutine_match_orb < 1 else "#EF4444"};font-weight:600;">'
        f'{chart.trutine_match_orb:.3f}°</td></tr>'
        f'<tr><td style="color:#888;padding:4px 8px;">{"妊娠期" if lang == "zh" else "Gestation"}</td>'
        f'    <td style="color:#A8B8C8;">{chart.gestation_days:.1f} {"天" if lang == "zh" else "days"}</td></tr>'
        f'<tr><td style="color:#888;padding:4px 8px;">{"月亮相位" if lang == "zh" else "Moon Phase"}</td>'
        f'    <td style="color:#A8B8C8;">{MOON_PHASE_NAMES.get(chart.moon_phase_name, chart.moon_phase_name)}</td></tr>'
        f'</table>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Guidance text
    st.markdown("---")
    if lang == "zh":
        st.markdown("""
**如何利用前世盤進行出生時間校正？**

1. **誤差 < 1°** — 出生時間可靠，前世盤可直接用於靈魂分析
2. **誤差 1–3°** — 出生時間可能稍有誤差；可嘗試調整 ±15 分鐘
3. **誤差 3–5°** — 出生時間需要驗證；建議結合初級方向或次進法進一步校正
4. **誤差 > 5°** — 出生時間很可能不準確；建議使用本系統的「出生時間校正」模組

前世盤校正與其他技術相比的獨特優勢：
- 月亮↔ASC/DSC 的互換不依賴生命事件，是純天文計算
- 可作為其他校正技術的獨立交叉驗證
- 誤差容限嚴格（通常要求 ≤ 1°），校正精度高
""")
    else:
        st.markdown("""
**How to Use the Epoch for Birth Time Rectification?**

1. **Orb < 1°** — Birth time is reliable; Epoch can be used directly for soul analysis
2. **Orb 1–3°** — Birth time may have slight error; try adjusting ±15 minutes
3. **Orb 3–5°** — Birth time needs verification; combine with Primary Directions or Progressions
4. **Orb > 5°** — Birth time is likely inaccurate; use the Rectification module

Unique advantages of Epoch rectification vs other techniques:
- The Moon↔ASC/DSC reciprocity is a pure astronomical calculation, independent of life events
- Can serve as an independent cross-verification for other rectification techniques
- Tight tolerance (typically ≤ 1°) provides high rectification precision
""")

    # Link to Rectification module
    st.info(_zh(
        "💡 提示：將此前世盤數據結合「出生時間校正」模組中的初級方向和次進法，可獲得最高精度的校正結果。",
        "💡 Tip: Combine this Epoch data with Primary Directions and Secondary Progressions "
        "in the Rectification module for the highest accuracy.",
    ))


def _render_tab_soul_interpretations(chart: PrenatalEpochChart) -> None:
    """Tab 4: Soul-level interpretations of the Epoch chart."""
    lang = get_lang()

    st.markdown(
        f'<div class="trutine-section-title">'
        f'{"✨ 靈魂層級解讀 — 前世盤的深層意義" if lang == "zh" else "✨ Soul-Level Interpretations — Deep Meaning of the Epoch Chart"}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Hermetic quote
    if lang == "zh":
        quote = (
            "「月亮在地平線上方時，前世盤的上升點等於本命盤的月亮；"
            "月亮在地平線下方時，前世盤的下降點等於本命盤的月亮。」"
            " — 托勒密《百句箴言》第51條"
        )
    else:
        quote = (
            '"When the Moon is above the horizon, the Ascendant of the Epoch '
            'equals the Moon\'s position at birth; when below, the Descendant." '
            "— Ptolemy, Centiloquium Aphorism 51"
        )
    st.markdown(
        f'<div class="hermetic-quote">{quote}</div>',
        unsafe_allow_html=True,
    )

    # Soul interpretations
    if chart.soul_interpretations:
        for key, text in chart.soul_interpretations.items():
            # Parse title and body
            if "\n\n" in text:
                title_part, body_part = text.split("\n\n", 1)
            else:
                title_part = text
                body_part = ""

            st.markdown(
                f'<div class="soul-insight-card">'
                f'<div class="soul-insight-title">{title_part}</div>'
                f'<div class="soul-insight-text">{body_part}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info(_zh("正在生成靈魂層級解讀…", "Generating soul-level interpretations…"))

    # Epoch-Natal soul connection
    st.markdown("---")
    st.markdown(
        f'<div class="trutine-section-title">'
        f'{"🌀 靈魂計劃 vs 現實生命" if lang == "zh" else "🌀 Soul Plan vs Lived Life"}'
        f'</div>',
        unsafe_allow_html=True,
    )
    if lang == "zh":
        st.markdown("""
前世盤（受孕時刻）代表**靈魂的計劃** — 靈魂進入人世時選擇的天象印記。
本命盤（出生時刻）代表**現實生命** — 靈魂穿越出生的閾限，具現化到人間的起點。

兩者之間的相位與互換，揭示了：
- 靈魂計劃與現實命運的對話
- 此世需要整合的業力主題
- 靈魂本質（前世盤）與外在呈現（本命盤）的關係

**月亮↔上升點的互換** 是最核心的靈魂連結：
月亮代表靈魂記憶、情緒習性，上升點代表化身的方式與外在呈現。
這個互換說明，靈魂攜帶的記憶正是此世選擇的化身方式的根源。
""")
    else:
        st.markdown("""
The **Prenatal Epoch** (conception moment) represents the **Soul's Plan** —
the celestial imprint chosen by the soul as it entered the world.
The **Natal Chart** (birth moment) represents **Lived Life** —
the starting point where the soul crossed the threshold of birth into manifestation.

The aspects and reciprocities between them reveal:
- The dialogue between soul plan and earthly destiny
- Karmic themes to be integrated in this life
- The relationship between soul essence (Epoch) and outer expression (Natal)

**The Moon ↔ Ascendant/Descendant exchange** is the core soul link:
The Moon represents soul memory and emotional habits; the Ascendant represents
the mode of incarnation. This exchange shows that the soul's memories are the
very source of the incarnation style chosen for this life.
""")


def _render_tab_history(chart: PrenatalEpochChart) -> None:
    """Tab 5: Historical context and theoretical background."""
    lang = get_lang()

    history_text = TRUTINE_HISTORY.get(lang if lang in ("zh", "en") else "en", "")
    st.markdown(history_text)

    # Variant info
    st.markdown("---")
    st.markdown(
        f'<div class="trutine-section-title">{"📚 計算方法" if lang == "zh" else "📚 Calculation Method"}</div>',
        unsafe_allow_html=True,
    )
    variant_key = chart.variant.split(".")[-1] if "." in chart.variant else chart.variant
    variant_info = TRUTINE_VARIANTS.get(variant_key, TRUTINE_VARIANTS["bailey_standard"])
    name_key = "zh_name" if lang == "zh" else "en_name"
    desc_key = "zh_desc" if lang == "zh" else "en_desc"

    st.markdown(
        f'<div class="trutine-card">'
        f'<div style="color:#C9A227;font-weight:600;">{variant_info.get(name_key, "")}</div>'
        f'<div style="color:#A8B8C8;margin-top:6px;font-size:0.9rem;">{variant_info.get(desc_key, "")}</div>'
        f'<div style="color:#666;margin-top:6px;font-size:0.8rem;font-style:italic;">'
        f'{"來源：" if lang == "zh" else "Source: "}{variant_info.get("source", "")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # All variants overview
    st.markdown(
        f'<div class="trutine-section-title">{"🔬 其他計算方法" if lang == "zh" else "🔬 Other Calculation Variants"}</div>',
        unsafe_allow_html=True,
    )
    for vk, vdata in TRUTINE_VARIANTS.items():
        active = (vk == variant_key)
        border_color = "#C9A227" if active else "rgba(168,184,200,0.20)"
        st.markdown(
            f'<div class="trutine-card" style="border-color:{border_color};">'
            f'<div style="color:{"#C9A227" if active else "#A8B8C8"};font-weight:600;">'
            f'{"● " if active else "○ "}{vdata.get(name_key, vk)}</div>'
            f'<div style="color:#888;font-size:0.85rem;margin-top:4px;">'
            f'{vdata.get(desc_key, "")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# Main Renderer
# ============================================================

def render_streamlit(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
) -> None:
    """Main Streamlit renderer for the Trutine of Hermes / Prenatal Epoch module.

    Provides a 5-tab interface with dual-chart visualization,
    soul-level interpretations, and rectification validation.

    Args:
        year, month, day:   Birth date
        hour, minute:       Local birth time
        timezone:           UTC offset in hours
        latitude:           Geographic latitude
        longitude:          Geographic longitude
        location_name:      Optional location string
    """
    # Inject CSS
    st.markdown(_TRUTINE_CSS, unsafe_allow_html=True)

    lang = get_lang()

    # ── Hero Header ──────────────────────────────────────────
    st.markdown(f"""
<div class="trutine-hero">
  <div class="trutine-hero-title">
    {'赫密士出生前世盤' if lang == 'zh' else 'Trutine of Hermes'}
  </div>
  <div class="trutine-hero-sub">
    {'Trutine of Hermes · Prenatal Epoch · 受孕星盤 · 靈魂入身之印記' if lang == 'zh'
     else 'Prenatal Epoch · Conception Chart · Soul Incarnation Imprint'}
  </div>
  <div>
    <span class="trutine-badge">{'古典希臘化' if lang == 'zh' else 'Hellenistic'}</span>
    <span class="trutine-badge">{'赫密士傳承' if lang == 'zh' else 'Hermetic'}</span>
    <span class="trutine-badge">{'托勒密《百句箴言》' if lang == 'zh' else 'Ptolemy Centiloquium'}</span>
    <span class="trutine-badge">{'E.H. Bailey 1916' if lang == 'zh' else 'E.H. Bailey 1916'}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Options sidebar ──────────────────────────────────────
    with st.expander(
        _zh("⚙️ 計算選項", "⚙️ Calculation Options"),
        expanded=False,
    ):
        variant_options = {
            "bailey_standard": _zh("貝利標準法 (推薦)", "Bailey Standard (Recommended)"),
            "hermes_ptolemy":  _zh("赫密士/托勒密 經典法", "Classical Hermes/Ptolemy"),
            "sepharial":       _zh("賽法利亞爾 太陽紀元法", "Sepharial Solar Epoch"),
        }
        selected_variant = st.selectbox(
            _zh("計算方法", "Calculation Method"),
            options=list(variant_options.keys()),
            format_func=lambda k: variant_options[k],
            key="trutine_variant",
        )
        use_gestation_override = st.checkbox(
            _zh("自訂妊娠期天數", "Custom Gestation Period"),
            value=False,
            key="trutine_gestation_override_enabled",
        )
        gestation_override = None
        if use_gestation_override:
            gestation_override = st.slider(
                _zh("妊娠期（天）", "Gestation Period (days)"),
                min_value=250, max_value=300,
                value=273, step=1,
                key="trutine_gestation_days",
            )

    # ── Compute ──────────────────────────────────────────────
    with st.spinner(t("spinner_trutine_of_hermes")):
        chart = compute_epoch_chart(
            year=year, month=month, day=day,
            hour=hour, minute=minute,
            timezone=timezone,
            latitude=latitude, longitude=longitude,
            location_name=location_name,
            variant=selected_variant,
            gestation_override=float(gestation_override) if gestation_override else None,
        )

    if chart.error:
        st.error(f"{'計算錯誤：' if lang == 'zh' else 'Calculation error: '}{chart.error}")
        return

    # ── Tabs ─────────────────────────────────────────────────
    tab_labels = [
        _zh("前世盤排盤", "Epoch Chart"),
        _zh("與本命盤對照", "Natal Comparison"),
        _zh("校正驗證", "Rectification"),
        _zh("靈魂層級解讀", "Soul Insights"),
        _zh("歷史與理論", "History & Theory"),
    ]
    tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_labels)

    with tab1:
        _render_tab_epoch_chart(chart)

    with tab2:
        _render_tab_comparison(chart)

    with tab3:
        _render_tab_rectification(chart)

    with tab4:
        _render_tab_soul_interpretations(chart)

    with tab5:
        _render_tab_history(chart)
