"""
astro/esoteric/renderer.py — Streamlit UI + SVG Mandala for Esoteric Astrology

Includes:
  - render_streamlit(): Full Streamlit UI for Esoteric Astrology analysis
  - render_esoteric_chart_svg(): High-quality SVG Seven Rays Mandala with
    Sacred Geometry, ray beam effects, and dual Soul/Personality Ray display.

Visual Design Philosophy:
  The SVG mandala draws on Theosophical sacred art tradition —
  a seven-pointed star (heptagram) with ray-coloured beams,
  soft radiance/glow effects, and the dignified aesthetic of
  Alice Bailey's era. The central wheel represents the soul's
  journey through the Seven Rays.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import streamlit as st

from .calculator import (
    EsotericChart,
    RayIndicator,
    RayTally,
    compute_esoteric_chart,
    get_ray_interaction_analysis,
)
from .constants import (
    SEVEN_RAYS,
    SIGN_RULERS,
    SIGN_ZH,
    ZODIAC_SIGNS,
    RayData,
    get_ray_interaction,
    EXAMPLE_CHARTS,
)
from astro.i18n import auto_cn, get_ui_lang, t


# ============================================================
#  CSS
# ============================================================

_ESOTERIC_CSS = """
<style>
.eso-header {
    background: linear-gradient(135deg, #0d0d2b 0%, #1a0a3d 40%, #2d0a4e 100%);
    border-left: 4px solid #9b59b6;
    padding: 14px 20px;
    border-radius: 8px;
    margin-bottom: 14px;
}
.eso-ray-card {
    background: rgba(30, 10, 60, 0.85);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
    border: 1px solid rgba(150, 80, 220, 0.3);
}
.eso-soul-ray {
    background: linear-gradient(135deg, rgba(30, 58, 138, 0.4) 0%, rgba(88, 28, 135, 0.4) 100%);
    border: 1.5px solid #3b82f6;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.eso-personality-ray {
    background: linear-gradient(135deg, rgba(20, 83, 45, 0.4) 0%, rgba(146, 64, 14, 0.3) 100%);
    border: 1.5px solid #4ade80;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.eso-confidence-strong { color: #4ade80; font-weight: bold; }
.eso-confidence-moderate { color: #fbbf24; font-weight: bold; }
.eso-confidence-weak { color: #f87171; font-weight: bold; }
.eso-ruler-table td { padding: 4px 10px; vertical-align: top; }
.eso-disclaimer {
    background: rgba(40, 10, 80, 0.5);
    border: 1px solid #7c3aed;
    border-radius: 6px;
    padding: 10px 16px;
    font-size: 0.85em;
    color: #c4b5fd;
    margin: 14px 0;
}
.eso-glamour {
    background: rgba(60, 10, 10, 0.4);
    border-left: 3px solid #dc2626;
    border-radius: 4px;
    padding: 8px 12px;
    margin-bottom: 6px;
}
.eso-service {
    background: rgba(10, 60, 30, 0.4);
    border-left: 3px solid #16a34a;
    border-radius: 4px;
    padding: 8px 12px;
    margin-bottom: 6px;
}
</style>
"""


# ============================================================
#  SVG Mandala — render_esoteric_chart_svg()
# ============================================================

def render_esoteric_chart_svg(
    chart: EsotericChart,
    width: int = 700,
    height: int = 700,
) -> str:
    """
    Generate a high-quality SVG Seven Rays Mandala.

    Design elements:
      - Deep violet/indigo background (Theosophical colour of space)
      - Seven radial ray beams with their traditional colours,
        soft glow (SVG feGaussianBlur filter), and gradient fills
      - Heptagram (7-pointed star) as sacred geometry frame
      - Inner circle with Soul Ray and Personality Ray highlights
      - Outer ring with all 12 zodiac signs
      - Ray colour wheel with labels
      - Decorative lotus petals at beam terminals
      - Central esoteric eye / lotus symbol
      - Elegant bilingual annotations

    Args:
        chart: Computed EsotericChart.
        width, height: SVG dimensions in pixels.

    Returns:
        SVG string suitable for st.components.v1.html() or PDF embedding.
    """
    cx, cy = width / 2, height / 2
    outer_r = min(cx, cy) * 0.90
    inner_r = outer_r * 0.38
    star_r = outer_r * 0.72
    mid_r = outer_r * 0.55
    zodiac_r = outer_r * 0.82

    soul_ray = chart.soul_ray_indicator.ray if chart.soul_ray_indicator else 2
    pers_ray = chart.personality_ray_indicator.ray if chart.personality_ray_indicator else 4

    soul_rd = SEVEN_RAYS[soul_ray]
    pers_rd = SEVEN_RAYS[pers_ray]

    # Ray angle offsets — Ray 1 at top (270° = 12 o'clock), clockwise
    def ray_angle(ray_num: int) -> float:
        """Return angle in radians for a ray (Ray 1 at top, clockwise)."""
        base_deg = -90.0 + (ray_num - 1) * (360.0 / 7)
        return math.radians(base_deg)

    def polar(r: float, angle_rad: float) -> Tuple[float, float]:
        return cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad)

    lines: List[str] = []

    # ── Background
    lines.append(
        f'<rect width="{width}" height="{height}" '
        f'fill="url(#bgGradient)" rx="18"/>'
    )

    # ── SVG defs (gradients, filters, patterns)
    defs = _build_defs(soul_rd, pers_rd, cx, cy, outer_r)
    lines.insert(0, defs)

    # ── Outer decorative rings
    lines.append(_outer_rings(cx, cy, outer_r, zodiac_r))

    # ── Seven Ray beams (from centre outward)
    for ray_num in range(1, 8):
        rd = SEVEN_RAYS[ray_num]
        ang = ray_angle(ray_num)
        tip_x, tip_y = polar(star_r, ang)
        is_soul = (ray_num == soul_ray)
        is_pers = (ray_num == pers_ray)
        beam_w = 28 if is_soul else (22 if is_pers else 16)
        opacity = 0.85 if is_soul else (0.75 if is_pers else 0.55)
        lines.append(_draw_ray_beam(cx, cy, tip_x, tip_y, rd, beam_w, opacity, ray_num))

    # ── Heptagram (7-pointed star)
    lines.append(_draw_heptagram(cx, cy, star_r * 0.95))

    # ── Zodiac ring labels (12 signs)
    lines.append(_zodiac_ring(cx, cy, zodiac_r, outer_r))

    # ── Ray petal terminals at star tips
    for ray_num in range(1, 8):
        rd = SEVEN_RAYS[ray_num]
        ang = ray_angle(ray_num)
        tip_x, tip_y = polar(star_r * 0.97, ang)
        is_soul = (ray_num == soul_ray)
        is_pers = (ray_num == pers_ray)
        lines.append(_draw_ray_petal(tip_x, tip_y, rd, is_soul, is_pers))

    # ── Ray number labels (along beams)
    for ray_num in range(1, 8):
        rd = SEVEN_RAYS[ray_num]
        ang = ray_angle(ray_num)
        lx, ly = polar(mid_r * 1.02, ang)
        is_soul = (ray_num == soul_ray)
        is_pers = (ray_num == pers_ray)
        lines.append(_draw_ray_label(lx, ly, ang, rd, ray_num, is_soul, is_pers))

    # ── Inner sacred circle
    lines.append(_inner_sacred_circle(cx, cy, inner_r))

    # ── Central soul/personality display
    lines.append(_central_display(cx, cy, inner_r, soul_rd, pers_rd, soul_ray, pers_ray))

    # ── Outer legend panel (bottom)
    lines.append(_legend_panel(width, height, soul_rd, pers_rd, soul_ray, pers_ray, chart))

    svg_content = "\n".join(lines)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" '
        f'style="font-family: Georgia, serif; background: #0a0520;">'
        f'{svg_content}'
        f'</svg>'
    )


def _build_defs(
    soul_rd: RayData, pers_rd: RayData,
    cx: float, cy: float, outer_r: float,
) -> str:
    """Build SVG <defs> with gradients and filters."""
    soul_color = soul_rd.svg_color
    soul_glow = soul_rd.svg_glow
    pers_color = pers_rd.svg_color
    pers_glow = pers_rd.svg_glow

    ray_grads = ""
    for i, (rn, rd) in enumerate(SEVEN_RAYS.items()):
        ray_grads += (
            f'<radialGradient id="rayGrad{rn}" cx="50%" cy="50%" r="50%">'
            f'<stop offset="0%" stop-color="{rd.svg_glow}" stop-opacity="0.9"/>'
            f'<stop offset="100%" stop-color="{rd.svg_color}" stop-opacity="0.3"/>'
            f'</radialGradient>'
        )
        ray_grads += (
            f'<linearGradient id="beamGrad{rn}" x1="0.5" y1="0" x2="0.5" y2="1">'
            f'<stop offset="0%" stop-color="{rd.svg_glow}" stop-opacity="0.95"/>'
            f'<stop offset="60%" stop-color="{rd.svg_color}" stop-opacity="0.7"/>'
            f'<stop offset="100%" stop-color="{rd.svg_color}" stop-opacity="0.1"/>'
            f'</linearGradient>'
        )

    return f"""<defs>
  <!-- Background gradient -->
  <radialGradient id="bgGradient" cx="50%" cy="50%" r="65%">
    <stop offset="0%" stop-color="#1a0a3d"/>
    <stop offset="55%" stop-color="#0d0520"/>
    <stop offset="100%" stop-color="#060212"/>
  </radialGradient>

  <!-- Glow filter for Soul Ray -->
  <filter id="soulGlow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="6" result="blur"/>
    <feComposite in="SourceGraphic" in2="blur" operator="over"/>
  </filter>

  <!-- Glow filter for Personality Ray -->
  <filter id="persGlow" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="4" result="blur"/>
    <feComposite in="SourceGraphic" in2="blur" operator="over"/>
  </filter>

  <!-- Soft glow filter for general beams -->
  <filter id="beamGlow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>

  <!-- Star glow -->
  <filter id="starGlow">
    <feGaussianBlur stdDeviation="2.5" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>

  <!-- Soul highlight ring gradient -->
  <radialGradient id="soulRingGrad" cx="50%" cy="50%" r="50%">
    <stop offset="70%" stop-color="{soul_color}" stop-opacity="0.0"/>
    <stop offset="90%" stop-color="{soul_glow}" stop-opacity="0.6"/>
    <stop offset="100%" stop-color="{soul_color}" stop-opacity="0.2"/>
  </radialGradient>

  <!-- Personality highlight ring gradient -->
  <radialGradient id="persRingGrad" cx="50%" cy="50%" r="50%">
    <stop offset="70%" stop-color="{pers_color}" stop-opacity="0.0"/>
    <stop offset="90%" stop-color="{pers_glow}" stop-opacity="0.4"/>
    <stop offset="100%" stop-color="{pers_color}" stop-opacity="0.15"/>
  </radialGradient>

  <!-- Inner circle gradient -->
  <radialGradient id="innerGrad" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#2d1060" stop-opacity="0.95"/>
    <stop offset="70%" stop-color="#1a0a3d" stop-opacity="0.9"/>
    <stop offset="100%" stop-color="#0d0520" stop-opacity="0.8"/>
  </radialGradient>

  {ray_grads}
</defs>"""


def _outer_rings(cx: float, cy: float, outer_r: float, zodiac_r: float) -> str:
    """Draw decorative outer rings."""
    r1 = outer_r * 0.98
    r2 = outer_r * 0.87
    r3 = zodiac_r * 0.90
    lines = []
    # Outer decorative ring
    lines.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r1:.1f}" '
                 f'fill="none" stroke="#6b21a8" stroke-width="1.5" stroke-opacity="0.5"/>')
    lines.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r1 - 4:.1f}" '
                 f'fill="none" stroke="#9333ea" stroke-width="0.5" stroke-opacity="0.3"/>')
    # Zodiac ring band
    lines.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{zodiac_r:.1f}" '
                 f'fill="none" stroke="#7c3aed" stroke-width="14" stroke-opacity="0.12"/>')
    lines.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{zodiac_r:.1f}" '
                 f'fill="none" stroke="#a855f7" stroke-width="0.8" stroke-opacity="0.5"/>')
    lines.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r2:.1f}" '
                 f'fill="none" stroke="#7c3aed" stroke-width="0.5" stroke-opacity="0.4"/>')
    # Tick marks at 30° intervals (12 signs)
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        x1 = cx + zodiac_r * 0.92 * math.cos(ang)
        y1 = cy + zodiac_r * 0.92 * math.sin(ang)
        x2 = cx + zodiac_r * 1.02 * math.cos(ang)
        y2 = cy + zodiac_r * 1.02 * math.sin(ang)
        lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                     f'stroke="#9333ea" stroke-width="1" stroke-opacity="0.6"/>')
    return "\n".join(lines)


def _draw_ray_beam(
    cx: float, cy: float,
    tip_x: float, tip_y: float,
    rd: RayData,
    beam_w: float, opacity: float,
    ray_num: int,
) -> str:
    """Draw a single ray beam from centre to tip."""
    dx = tip_x - cx
    dy = tip_y - cy
    length = math.sqrt(dx * dx + dy * dy)
    # Perpendicular unit vector
    px = -dy / length * beam_w / 2
    py = dx / length * beam_w / 2

    # Beam polygon (tapered from centre, wide at middle, narrow at tip)
    mid_x = cx + dx * 0.45
    mid_y = cy + dy * 0.45

    points_str = (
        f"{cx:.1f},{cy:.1f} "
        f"{mid_x + px:.1f},{mid_y + py:.1f} "
        f"{tip_x + px * 0.3:.1f},{tip_y + py * 0.3:.1f} "
        f"{tip_x:.1f},{tip_y:.1f} "
        f"{tip_x - px * 0.3:.1f},{tip_y - py * 0.3:.1f} "
        f"{mid_x - px:.1f},{mid_y - py:.1f}"
    )

    return (
        f'<polygon points="{points_str}" '
        f'fill="{rd.svg_color}" opacity="{opacity:.2f}" '
        f'filter="url(#beamGlow)"/>'
        # Bright core line
        f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{tip_x:.1f}" y2="{tip_y:.1f}" '
        f'stroke="{rd.svg_glow}" stroke-width="1.5" opacity="{min(opacity + 0.1, 1.0):.2f}"/>'
    )


def _draw_heptagram(cx: float, cy: float, r: float) -> str:
    """Draw a 7-pointed star (heptagram) as sacred geometry frame."""
    # {7/2} star polygon — connect every 2nd vertex
    n = 7
    step = 2
    pts = []
    for i in range(n):
        ang = math.radians(-90 + i * 360 / n)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))

    # Reorder by step
    ordered = []
    idx = 0
    for _ in range(n):
        ordered.append(pts[idx % n])
        idx += step

    pt_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in ordered)
    return (
        f'<polygon points="{pt_str}" '
        f'fill="none" stroke="#c084fc" stroke-width="1.2" '
        f'stroke-opacity="0.45" filter="url(#starGlow)"/>'
    )


def _zodiac_ring(cx: float, cy: float, ring_r: float, outer_r: float) -> str:
    """Draw zodiac sign symbols on the outer ring."""
    symbols = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
    abbr = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
            "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
    lines = []
    for i, (sym, ab) in enumerate(zip(symbols, abbr)):
        ang = math.radians(i * 30 - 75)  # offset by 15° to centre in sign
        x = cx + ring_r * math.cos(ang)
        y = cy + ring_r * math.sin(ang)
        lines.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-size="12" fill="#c084fc" '
            f'opacity="0.7">{sym}</text>'
        )
    return "\n".join(lines)


def _draw_ray_petal(
    tip_x: float, tip_y: float,
    rd: RayData,
    is_soul: bool,
    is_pers: bool,
) -> str:
    """Draw a lotus petal / diamond at each ray tip."""
    size = 10 if is_soul else (8 if is_pers else 6)
    glow_filter = 'filter="url(#soulGlow)"' if is_soul else (
        'filter="url(#persGlow)"' if is_pers else ""
    )
    ring_stroke = rd.svg_glow if (is_soul or is_pers) else rd.svg_color
    ring_w = 2.5 if is_soul else (1.8 if is_pers else 1.0)
    return (
        f'<circle cx="{tip_x:.1f}" cy="{tip_y:.1f}" r="{size}" '
        f'fill="{rd.svg_color}" fill-opacity="0.7" '
        f'stroke="{ring_stroke}" stroke-width="{ring_w}" {glow_filter}/>'
    )


def _draw_ray_label(
    lx: float, ly: float, ang: float,
    rd: RayData, ray_num: int,
    is_soul: bool, is_pers: bool,
) -> str:
    """Draw ray label text near the mid-point of the beam."""
    fill = rd.svg_glow if (is_soul or is_pers) else "#d8b4fe"
    font_size = 12 if (is_soul or is_pers) else 10
    opacity = 1.0 if (is_soul or is_pers) else 0.75
    badge = " ✦" if is_soul else (" ◈" if is_pers else "")
    label = f"R{ray_num}{badge}"
    return (
        f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
        f'dominant-baseline="middle" font-size="{font_size}" '
        f'fill="{fill}" opacity="{opacity:.2f}" '
        f'font-weight="{"bold" if (is_soul or is_pers) else "normal"}">'
        f'{label}</text>'
    )


def _inner_sacred_circle(cx: float, cy: float, r: float) -> str:
    """Draw the inner sacred circle with decorative rings."""
    lines = []
    # Main inner circle
    lines.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
        f'fill="url(#innerGrad)" stroke="#9333ea" stroke-width="1.5" stroke-opacity="0.7"/>'
    )
    # Inner decorative rings
    lines.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.85:.1f}" '
        f'fill="none" stroke="#7c3aed" stroke-width="0.8" stroke-opacity="0.5"/>'
    )
    lines.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.65:.1f}" '
        f'fill="none" stroke="#6d28d9" stroke-width="0.6" stroke-opacity="0.4"/>'
    )
    # Lotus petals (8 petals)
    petal_r = r * 0.30
    for i in range(8):
        ang = math.radians(i * 45)
        px = cx + r * 0.72 * math.cos(ang)
        py = cy + r * 0.72 * math.sin(ang)
        lines.append(
            f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{petal_r * 0.5:.1f}" ry="{petal_r:.1f}" '
            f'transform="rotate({i * 45:.0f} {px:.1f} {py:.1f})" '
            f'fill="#4c1d95" fill-opacity="0.5" stroke="#9333ea" stroke-width="0.5" stroke-opacity="0.6"/>'
        )
    # Central eye / lotus symbol
    lines.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.22:.1f}" '
        f'fill="#2d1060" stroke="#a855f7" stroke-width="1.2" stroke-opacity="0.8"/>'
    )
    lines.append(
        f'<text x="{cx:.1f}" y="{cy - r * 0.05:.1f}" text-anchor="middle" '
        f'dominant-baseline="middle" font-size="{r * 0.28:.0f}" fill="#c084fc" opacity="0.85">'
        f'☽⊙☉</text>'
    )
    return "\n".join(lines)


def _central_display(
    cx: float, cy: float, inner_r: float,
    soul_rd: RayData, pers_rd: RayData,
    soul_ray: int, pers_ray: int,
) -> str:
    """Display Soul Ray and Personality Ray at centre."""
    lines = []
    offset_y = inner_r * 0.45

    # Soul Ray label (top half of inner circle)
    lines.append(
        f'<text x="{cx:.1f}" y="{cy - offset_y:.1f}" text-anchor="middle" '
        f'dominant-baseline="middle" font-size="11" fill="{soul_rd.svg_glow}" '
        f'font-weight="bold" filter="url(#soulGlow)">✦ Soul R{soul_ray}</text>'
    )
    lines.append(
        f'<text x="{cx:.1f}" y="{cy - offset_y + 14:.1f}" text-anchor="middle" '
        f'dominant-baseline="middle" font-size="8.5" fill="{soul_rd.svg_glow}" opacity="0.85">'
        f'{soul_rd.name_en.split("/")[0].strip()}</text>'
    )

    # Personality Ray label (bottom half)
    lines.append(
        f'<text x="{cx:.1f}" y="{cy + offset_y - 14:.1f}" text-anchor="middle" '
        f'dominant-baseline="middle" font-size="8.5" fill="{pers_rd.svg_glow}" opacity="0.85">'
        f'{pers_rd.name_en.split("/")[0].strip()}</text>'
    )
    lines.append(
        f'<text x="{cx:.1f}" y="{cy + offset_y:.1f}" text-anchor="middle" '
        f'dominant-baseline="middle" font-size="11" fill="{pers_rd.svg_glow}" '
        f'font-weight="bold" filter="url(#persGlow)">◈ Pers R{pers_ray}</text>'
    )
    return "\n".join(lines)


def _legend_panel(
    width: float, height: float,
    soul_rd: RayData, pers_rd: RayData,
    soul_ray: int, pers_ray: int,
    chart: EsotericChart,
) -> str:
    """Draw a compact legend strip at the bottom of the SVG."""
    panel_h = 52
    py = height - panel_h - 2
    lines = []

    # Panel background
    lines.append(
        f'<rect x="10" y="{py}" width="{width - 20}" height="{panel_h}" '
        f'rx="6" fill="#0d0520" fill-opacity="0.85" stroke="#6b21a8" stroke-width="0.8"/>'
    )

    # Soul Ray block
    lines.append(
        f'<rect x="20" y="{py + 6}" width="14" height="14" rx="3" '
        f'fill="{soul_rd.svg_color}" fill-opacity="0.85"/>'
    )
    soul_label = f"Soul Ray {soul_ray}: {soul_rd.name_zh} / {soul_rd.name_en.split('/')[0].strip()}"
    lines.append(
        f'<text x="40" y="{py + 16}" font-size="10.5" fill="{soul_rd.svg_glow}" font-weight="bold">'
        f'{soul_label}</text>'
    )

    # Personality Ray block
    lines.append(
        f'<rect x="20" y="{py + 28}" width="14" height="14" rx="3" '
        f'fill="{pers_rd.svg_color}" fill-opacity="0.85"/>'
    )
    pers_label = f"Pers Ray {pers_ray}: {pers_rd.name_zh} / {pers_rd.name_en.split('/')[0].strip()}"
    lines.append(
        f'<text x="40" y="{py + 40}" font-size="10.5" fill="{pers_rd.svg_glow}">'
        f'{pers_label}</text>'
    )

    # ASC/Sun/Moon info
    asc_zh = SIGN_ZH.get(chart.asc_sign, chart.asc_sign)
    sun_zh = SIGN_ZH.get(chart.sun_sign, chart.sun_sign)
    moon_zh = SIGN_ZH.get(chart.moon_sign, chart.moon_sign)
    info_str = f"上升 {asc_zh} · 太陽 {sun_zh} · 月亮 {moon_zh}"
    lines.append(
        f'<text x="{width - 20}" y="{py + 16}" text-anchor="end" '
        f'font-size="10" fill="#c084fc" opacity="0.75">{info_str}</text>'
    )

    # Name
    name_str = chart.location_name or ""
    lines.append(
        f'<text x="{width - 20}" y="{py + 34}" text-anchor="end" '
        f'font-size="9.5" fill="#9333ea" opacity="0.7">'
        f'{chart.year}-{chart.month:02d}-{chart.day:02d}  {name_str}</text>'
    )

    return "\n".join(lines)


# ============================================================
#  Streamlit renderer
# ============================================================

def render_streamlit(chart: EsotericChart) -> None:
    """
    Render a complete Esoteric Astrology analysis in Streamlit.

    Tabs:
      1. 七道光線 Mandala — SVG mandala visualisation
      2. 靈魂光線 Soul Ray — Soul Ray indicator + interpretation
      3. 人格光線 Personality Ray — Personality Ray indicator
      4. 光線分佈 Ray Distribution — Full tally + esoteric rulers table
      5. 靈性課題 Spiritual Path — Glamours, service direction, interaction
    """
    st.markdown(_ESOTERIC_CSS, unsafe_allow_html=True)

    lang = get_ui_lang()
    is_zh = lang in ("zh", "zh_cn")

    # Header
    title_zh = "✨ 靈性占星 · 七道光線分析（Alice Bailey 體系）"
    title_en = "✨ Esoteric Astrology · Seven Rays Analysis (Alice Bailey System)"
    subtitle_zh = (
        f"上升 {SIGN_ZH.get(chart.asc_sign, chart.asc_sign)} · "
        f"太陽 {SIGN_ZH.get(chart.sun_sign, chart.sun_sign)} · "
        f"月亮 {SIGN_ZH.get(chart.moon_sign, chart.moon_sign)}"
    )
    subtitle_en = (
        f"ASC {chart.asc_sign} · Sun {chart.sun_sign} · Moon {chart.moon_sign}"
    )

    st.markdown(
        f'<div class="eso-header">'
        f'<h3 style="color:#c084fc;margin:0">{title_zh if is_zh else title_en}</h3>'
        f'<p style="color:#9333ea;margin:4px 0 0">{subtitle_zh if is_zh else subtitle_en}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Disclaimer
    disc_zh = (
        "⚠️ **靈性免責聲明**：靈魂光線的判斷本質上是靈性辨識的過程，"
        "而非機械計算公式。本分析提供的是「傾向性指標」，"
        "最終確認需要冥想、靈性導師指引及個人洞察。"
        "——愛麗絲·貝利《秘傳占星》第3頁"
    )
    disc_en = (
        "⚠️ **Spiritual Disclaimer**: Soul Ray determination is inherently a process of "
        "spiritual discernment, not mechanical calculation. This analysis provides "
        "'tendency indicators'. Final confirmation requires meditation, spiritual guidance "
        "and personal insight. — Alice Bailey, *Esoteric Astrology*, p. 3"
    )
    st.markdown(
        f'<div class="eso-disclaimer">{disc_zh if is_zh else disc_en}</div>',
        unsafe_allow_html=True,
    )

    # Tabs
    tab_labels = (
        ["🌈 七道光線圖", "☉ 靈魂光線", "🌙 人格光線", "📊 光線分佈", "🌿 靈性路徑"]
        if is_zh else
        ["🌈 Mandala", "☉ Soul Ray", "🌙 Personality Ray", "📊 Ray Distribution", "🌿 Spiritual Path"]
    )
    tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_labels)

    with tab1:
        _render_mandala_tab(chart, is_zh)

    with tab2:
        _render_soul_ray_tab(chart, is_zh)

    with tab3:
        _render_personality_ray_tab(chart, is_zh)

    with tab4:
        _render_ray_distribution_tab(chart, is_zh)

    with tab5:
        _render_spiritual_path_tab(chart, is_zh)


# ── Tab renderers ──────────────────────────────────────────

def _render_mandala_tab(chart: EsotericChart, is_zh: bool) -> None:
    """Tab 1: SVG Mandala."""
    svg = render_esoteric_chart_svg(chart, width=640, height=640)
    import streamlit.components.v1 as components
    components.html(
        f'<div style="display:flex;justify-content:center;background:#060212;padding:16px;border-radius:12px">'
        f'{svg}</div>',
        height=680,
        scrolling=False,
    )
    if is_zh:
        st.caption(
            "七道光線曼陀羅：✦ 標記靈魂光線，◈ 標記人格光線。"
            "七芒星（Heptagram）代表七道光線體系的神聖幾何基礎。"
            "外環為黃道十二宮，中央蓮花象徵靈魂的顯化。"
        )
    else:
        st.caption(
            "Seven Rays Mandala: ✦ marks the Soul Ray, ◈ marks the Personality Ray. "
            "The heptagram represents the sacred geometric foundation of the Seven Ray system. "
            "The outer ring shows the zodiac; the central lotus symbolizes soul manifestation."
        )


def _render_soul_ray_tab(chart: EsotericChart, is_zh: bool) -> None:
    """Tab 2: Soul Ray analysis."""
    if not chart.soul_ray_indicator:
        st.warning("Soul Ray indicator not computed.")
        return

    ind = chart.soul_ray_indicator
    rd = ind.ray_data
    conf_map = {"strong": ("高 Strong", "eso-confidence-strong"),
                "moderate": ("中 Moderate", "eso-confidence-moderate"),
                "weak": ("低 Weak", "eso-confidence-weak")}
    conf_label, conf_cls = conf_map.get(ind.confidence, ("—", ""))

    st.markdown(
        f'<div class="eso-soul-ray">'
        f'<h4 style="color:{rd.svg_glow};margin:0 0 6px">✦ '
        f'{"靈魂光線" if is_zh else "Soul Ray"} {ind.ray} — '
        f'{"" if not is_zh else rd.name_zh + " / "}{rd.name_en}</h4>'
        f'<p style="margin:0 0 4px">{"信心度" if is_zh else "Confidence"}: '
        f'<span class="{conf_cls}">{conf_label}</span></p>'
        f'<p style="color:#a78bfa;margin:0;font-size:0.9em">{rd.color}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{'靈魂目的' if is_zh else 'Soul Purpose'}**")
        st.markdown(rd.soul_purpose_zh if is_zh else rd.soul_purpose_en)
        st.markdown(f"**{'主要品質' if is_zh else 'Core Qualities'}**")
        quals = rd.qualities_zh if is_zh else rd.qualities_en
        for q in quals:
            st.markdown(f"• {q}")

    with col2:
        st.markdown(f"**{'靈性統治星' if is_zh else 'Esoteric Rulers'}**")
        _render_ruler_table(chart.asc_sign, is_zh)
        st.markdown(f"**{'服務方向' if is_zh else 'Service Direction'}**")
        st.markdown(rd.service_zh if is_zh else rd.service_en)

    # Supporting factors
    with st.expander("📋 " + ("支持因素" if is_zh else "Supporting Factors")):
        factors = ind.supporting_factors_zh if is_zh else ind.supporting_factors
        for f_str in factors:
            st.markdown(f"• {f_str}")

    # Bailey reference
    st.markdown(
        f'<div class="eso-disclaimer" style="font-size:0.8em">'
        f'{"光線品質參考：" if is_zh else "Ray quality reference: "}'
        f'Alice Bailey, <i>Esoteric Psychology</i> Vol. I, pp. 49–200; '
        f'<i>Esoteric Astrology</i>, pp. 44–65.'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_personality_ray_tab(chart: EsotericChart, is_zh: bool) -> None:
    """Tab 3: Personality Ray analysis."""
    if not chart.personality_ray_indicator:
        st.warning("Personality Ray indicator not computed.")
        return

    ind = chart.personality_ray_indicator
    rd = ind.ray_data
    conf_map = {"strong": ("高 Strong", "eso-confidence-strong"),
                "moderate": ("中 Moderate", "eso-confidence-moderate"),
                "weak": ("低 Weak", "eso-confidence-weak")}
    conf_label, conf_cls = conf_map.get(ind.confidence, ("—", ""))

    st.markdown(
        f'<div class="eso-personality-ray">'
        f'<h4 style="color:{rd.svg_glow};margin:0 0 6px">◈ '
        f'{"人格光線" if is_zh else "Personality Ray"} {ind.ray} — '
        f'{"" if not is_zh else rd.name_zh + " / "}{rd.name_en}</h4>'
        f'<p style="margin:0 0 4px">{"信心度" if is_zh else "Confidence"}: '
        f'<span class="{conf_cls}">{conf_label}</span></p>'
        f'<p style="color:#86efac;margin:0;font-size:0.9em">{rd.color}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{'此生人格特質' if is_zh else 'Personality Qualities'}**")
        quals = rd.qualities_zh if is_zh else rd.qualities_en
        for q in quals:
            st.markdown(f"• {q}")
        st.markdown(f"**{'主要幻相（Glamour）' if is_zh else 'Chief Glamour'}**")
        st.markdown(
            f'<div class="eso-glamour">{rd.glamour_zh if is_zh else rd.glamour_en}</div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(f"**{'傳統統治星' if is_zh else 'Exoteric Rulers'}**")
        _render_ruler_table(chart.asc_sign, is_zh)
        st.markdown(f"**{'服務方向' if is_zh else 'Service Direction'}**")
        st.markdown(rd.service_zh if is_zh else rd.service_en)

    # Supporting factors
    with st.expander("📋 " + ("支持因素" if is_zh else "Supporting Factors")):
        factors = ind.supporting_factors_zh if is_zh else ind.supporting_factors
        for f_str in factors:
            st.markdown(f"• {f_str}")


def _render_ray_distribution_tab(chart: EsotericChart, is_zh: bool) -> None:
    """Tab 4: Full Ray distribution and esoteric rulers."""
    if not chart.ray_tally:
        return

    tally = chart.ray_tally
    top_rays = tally.top_rays(7)

    st.markdown(f"#### {'七道光線分佈' if is_zh else 'Seven Rays Distribution'}")

    # Bar chart using st.progress
    max_score = max(s for _, s in top_rays) if top_rays else 1.0
    soul_ray = chart.soul_ray_indicator.ray if chart.soul_ray_indicator else 0
    pers_ray = chart.personality_ray_indicator.ray if chart.personality_ray_indicator else 0

    for ray_num, score in sorted(top_rays, key=lambda x: x[0]):
        rd = SEVEN_RAYS[ray_num]
        pct = int(score / max_score * 100) if max_score > 0 else 0
        badge = " ✦ 靈魂" if (ray_num == soul_ray and is_zh) else (
                " ✦ Soul" if ray_num == soul_ray else (
                " ◈ 人格" if (ray_num == pers_ray and is_zh) else (
                " ◈ Pers" if ray_num == pers_ray else "")))
        label = (f"R{ray_num} {rd.name_zh}/{rd.name_en.split('/')[0].strip()}{badge}"
                 if is_zh else
                 f"R{ray_num} {rd.name_en}{badge}")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(pct / 100, text=label)
        with col2:
            st.markdown(f'<span style="color:{rd.svg_glow}">{score:.1f}</span>',
                        unsafe_allow_html=True)

    # Esoteric Rulers Table
    st.markdown("---")
    st.markdown(f"#### {'星座靈性統治星表' if is_zh else 'Sign Esoteric Rulers Table'}")
    _render_full_rulers_table(is_zh)

    # Planets with their Rays
    st.markdown("---")
    st.markdown(f"#### {'行星光線對照' if is_zh else 'Planet → Ray Assignments'}")
    _render_planet_rays_table(chart, is_zh)


def _render_spiritual_path_tab(chart: EsotericChart, is_zh: bool) -> None:
    """Tab 5: Spiritual path — glamours, service, interaction."""
    # Soul-Personality interaction
    interaction = get_ray_interaction_analysis(chart)
    if interaction:
        s_ray = chart.soul_ray_indicator.ray if chart.soul_ray_indicator else 0
        p_ray = chart.personality_ray_indicator.ray if chart.personality_ray_indicator else 0
        itype = interaction.get("type", "")
        badge = {"complementary": "🌿 和諧 / Harmonious",
                 "tension": "⚡ 張力 / Tension",
                 "same": "⊙ 同光線 / Same Ray"}.get(itype, "")
        st.markdown(
            f"#### {'靈魂與人格光線互動' if is_zh else 'Soul–Personality Ray Interaction'} {badge}"
        )
        st.markdown(interaction.get("zh" if is_zh else "en", ""))

    st.markdown("---")

    # Glamours to overcome
    if chart.personality_ray_indicator:
        rd = chart.personality_ray_indicator.ray_data
        st.markdown(f"#### {'需克服的幻相（Glamours）' if is_zh else 'Glamours to Overcome'}")
        st.markdown(
            f'<div class="eso-glamour">'
            f'{"人格光線" if is_zh else "Personality Ray"} {rd.number} — '
            f'{rd.glamour_zh if is_zh else rd.glamour_en}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Service direction
    if chart.soul_ray_indicator:
        soul_rd = chart.soul_ray_indicator.ray_data
        st.markdown(
            f"#### {'靈性服務方向' if is_zh else 'Spiritual Service Direction'}"
        )
        st.markdown(
            f'<div class="eso-service">'
            f'{"靈魂光線" if is_zh else "Soul Ray"} {soul_rd.number} — '
            f'{soul_rd.service_zh if is_zh else soul_rd.service_en}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # All Seven Rays overview
    st.markdown("---")
    st.markdown(f"#### {'七道光線概覽' if is_zh else 'Seven Rays Overview'}")
    for rn, rd in SEVEN_RAYS.items():
        with st.expander(
            f"Ray {rn}: {rd.name_zh} / {rd.name_en}"
            if is_zh else f"Ray {rn}: {rd.name_en}"
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**{'顏色' if is_zh else 'Color'}:** {rd.color}")
                st.markdown(f"**{'主要品質' if is_zh else 'Core Quality'}:** "
                            f"{rd.quality_zh if is_zh else rd.quality_en}")
                st.markdown(f"**{'靈性統治星' if is_zh else 'Esoteric Planets'}:** "
                            f"{', '.join(rd.esoteric_planets)}")
                st.markdown(f"**{'傳統統治星' if is_zh else 'Exoteric Planets'}:** "
                            f"{', '.join(rd.exoteric_planets)}")
            with col2:
                st.markdown(f"**{'相關星座' if is_zh else 'Signs'}:** "
                            f"{', '.join(rd.signs)}")
                st.markdown(f"**{'幻相' if is_zh else 'Glamour'}:** "
                            f"{rd.glamour_zh if is_zh else rd.glamour_en}")
                st.markdown(f"**{'服務方向' if is_zh else 'Service'}:** "
                            f"{rd.service_zh if is_zh else rd.service_en}")


# ── Helper renderers ───────────────────────────────────────

def _render_ruler_table(sign: str, is_zh: bool) -> None:
    """Render a compact rulers table for a sign."""
    rulers = SIGN_RULERS.get(sign)
    if not rulers:
        return
    sign_zh = SIGN_ZH.get(sign, sign)
    rows = [
        ("傳統統治星 Exoteric" if is_zh else "Exoteric Ruler", rulers.exoteric),
        ("靈性統治星 Esoteric" if is_zh else "Esoteric Ruler", rulers.esoteric),
        ("階層統治星 Hierarchical" if is_zh else "Hierarchical Ruler", rulers.hierarchical),
        ("傳遞光線 Rays" if is_zh else "Rays Transmitted",
         ", ".join(f"R{r}" for r in rulers.rays_transmitted)),
    ]
    html_rows = "".join(
        f'<tr><td style="color:#9333ea;padding:3px 8px">{k}</td>'
        f'<td style="color:#e2e8f0;padding:3px 8px">{v}</td></tr>'
        for k, v in rows
    )
    st.markdown(
        f'<table style="font-size:0.9em;border-collapse:collapse">'
        f'<tr><td colspan="2" style="color:#a855f7;font-weight:bold;padding:2px 8px">'
        f'{sign_zh if is_zh else sign}</td></tr>'
        f'{html_rows}</table>',
        unsafe_allow_html=True,
    )


def _render_full_rulers_table(is_zh: bool) -> None:
    """Render the complete esoteric rulers table for all 12 signs."""
    headers = (
        ["星座", "傳統統治星", "靈性統治星", "階層統治星", "傳遞光線"]
        if is_zh else
        ["Sign", "Exoteric", "Esoteric", "Hierarchical", "Rays"]
    )
    rows = []
    for sign in ZODIAC_SIGNS:
        rulers = SIGN_RULERS.get(sign)
        if rulers:
            rows.append({
                headers[0]: SIGN_ZH[sign] if is_zh else sign,
                headers[1]: rulers.exoteric,
                headers[2]: rulers.esoteric,
                headers[3]: rulers.hierarchical,
                headers[4]: " ".join(f"R{r}" for r in rulers.rays_transmitted),
            })
    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)


def _render_planet_rays_table(chart: EsotericChart, is_zh: bool) -> None:
    """Render planet Ray assignments from the chart."""
    from .constants import PLANET_RAY_MAP
    rows = []
    for p in chart.points:
        planet_rays = PLANET_RAY_MAP.get(p.name, [])
        sign_rays = p.sign_rays
        rows.append({
            ("行星" if is_zh else "Planet"): p.name,
            ("星座" if is_zh else "Sign"): SIGN_ZH.get(p.sign, p.sign) if is_zh else p.sign,
            ("度數" if is_zh else "Degree"): f"{p.sign_degree:.1f}°",
            ("行星光線" if is_zh else "Planet Rays"): " ".join(f"R{r}" for r in planet_rays) or "—",
            ("星座光線" if is_zh else "Sign Rays"): " ".join(f"R{r}" for r in sign_rays) or "—",
        })
    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)
