"""
astro/maya/mayan_glyphs.py — 瑪雅日符號 SVG 渲染
(Maya Day Sign SVG Rendering)

生成 Tzolk'in 日符號卡片與輪盤 SVG。
Generates Tzolk'in day sign cards and the Tzolk'in wheel SVG.

純 Python + SVG 字串生成，無外部資源依賴。
Pure Python + SVG string generation, no external resource dependencies.
"""

from __future__ import annotations
import math
import random
from .constants import TZOLKIN_DAY_DATA


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _polar(cx: float, cy: float, r: float, angle_deg: float) -> tuple[float, float]:
    """Convert polar coordinates to SVG x,y (y-axis points down)."""
    angle_rad = math.radians(angle_deg)
    return cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad)


def _arc_path(cx: float, cy: float, r: float,
               start_deg: float, end_deg: float,
               large_arc: int = 0) -> str:
    """Return an SVG arc path segment (arc only, no M/Z)."""
    x1, y1 = _polar(cx, cy, r, start_deg)
    x2, y2 = _polar(cx, cy, r, end_deg)
    return f"A {r:.2f},{r:.2f} 0 {large_arc},1 {x2:.2f},{y2:.2f}"


def _slice_path(cx: float, cy: float, r_out: float, r_in: float,
                start_deg: float, end_deg: float) -> str:
    """Return a full SVG path for an annular (ring) slice / sector."""
    # Outer arc corners
    ox1, oy1 = _polar(cx, cy, r_out, start_deg)
    ox2, oy2 = _polar(cx, cy, r_out, end_deg)
    # Inner arc corners
    ix1, iy1 = _polar(cx, cy, r_in, start_deg)
    ix2, iy2 = _polar(cx, cy, r_in, end_deg)
    # For our 18-degree slices large_arc_flag = 0
    return (
        f"M {ox1:.2f},{oy1:.2f} "
        f"A {r_out:.2f},{r_out:.2f} 0 0,1 {ox2:.2f},{oy2:.2f} "
        f"L {ix2:.2f},{iy2:.2f} "
        f"A {r_in:.2f},{r_in:.2f} 0 0,0 {ix1:.2f},{iy1:.2f} Z"
    )


# ============================================================
# Tzolk'in 輪盤 SVG (Tzolk'in Wheel SVG)
# ============================================================

def generate_tzolkin_wheel_svg(
    current_sign_index: int,
    current_number: int,
    size: int = 560,
) -> str:
    """
    生成 Tzolk'in 輪盤 SVG（20 個日符號環 + 中央數字顯示）。
    Generate the Tzolk'in wheel SVG (20 day sign ring + central number display).

    Parameters
    ----------
    current_sign_index : int (0–19)  — currently active day sign
    current_number     : int (1–13)  — currently active sacred tone
    size               : int         — SVG canvas size in pixels
    """
    cx = cy = size / 2
    r_out = size * 0.47     # Outer ring edge
    r_in  = size * 0.315    # Inner ring edge
    r_mid = (r_out + r_in) / 2   # Middle of the ring (for labels)
    r_emoji = r_mid * 1.0        # Emoji placement radius
    r_text  = r_mid * 0.87       # Name text placement radius

    # Each slice is 18° wide (360 / 20).  We start at the top (-90°) and go clockwise.
    # Sign 0 (Imix) is at the top.
    slice_deg = 18.0

    # Colour palette for the 4 Mayan elements (repeated 5×)
    ELEMENT_COLORS = {
        "water": "#1a5276",
        "air":   "#2e4057",
        "earth": "#4a3728",
        "fire":  "#7d2b00",
    }
    HIGHLIGHT_RING_COLOR = "#FFD700"

    lines: list[str] = []

    # ── Background ────────────────────────────────────────────
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">'
    )
    # Dark cosmic background
    lines.append(
        f'<defs>'
        f'<radialGradient id="bgGrad" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="#1a0a2e"/>'
        f'<stop offset="100%" stop-color="#0a0415"/>'
        f'</radialGradient>'
        f'<filter id="glow"><feGaussianBlur stdDeviation="3" result="coloredBlur"/>'
        f'<feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        f'</defs>'
    )
    lines.append(f'<rect width="{size}" height="{size}" fill="url(#bgGrad)"/>')

    # Subtle starfield (fixed seed for reproducibility)
    rng = random.Random(42)
    for _ in range(60):
        sx = rng.uniform(0, size)
        sy = rng.uniform(0, size)
        sr = rng.uniform(0.5, 1.5)
        so = rng.uniform(0.3, 0.9)
        lines.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{sr:.1f}" fill="white" opacity="{so:.2f}"/>')

    # ── Outer decorative ring ─────────────────────────────────
    lines.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_out:.1f}" '
        f'fill="none" stroke="#4a3000" stroke-width="3"/>'
    )

    # ── 20 Slices ─────────────────────────────────────────────
    for i, day in enumerate(TZOLKIN_DAY_DATA):
        angle_center = -90 + i * slice_deg
        angle_start  = angle_center - slice_deg / 2
        angle_end    = angle_center + slice_deg / 2

        is_active = (i == current_sign_index)
        base_color = ELEMENT_COLORS.get(day["element"], "#2e2e2e")
        fill_color = day["color"] if is_active else base_color
        stroke_color = HIGHLIGHT_RING_COLOR if is_active else "#3a2a0a"
        stroke_w = 3 if is_active else 1

        # Slice path
        path_d = _slice_path(cx, cy, r_out, r_in, angle_start, angle_end)
        opacity = "1" if is_active else "0.82"
        lines.append(
            f'<path d="{path_d}" fill="{fill_color}" stroke="{stroke_color}" '
            f'stroke-width="{stroke_w}" opacity="{opacity}"/>'
        )

        # Emoji
        ex, ey = _polar(cx, cy, r_emoji * 0.72 + r_in * 0.28, angle_center)
        emoji_size = 18 if is_active else 14
        lines.append(
            f'<text x="{ex:.1f}" y="{ey:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-size="{emoji_size}">'
            f'{day["glyph_emoji"]}</text>'
        )

        # Day sign name (rotated to follow the ring)
        nx, ny = _polar(cx, cy, r_text * 0.55 + r_in * 0.45, angle_center)
        name_color = HIGHLIGHT_RING_COLOR if is_active else "#d4b896"
        name_size = 9 if is_active else 7
        lines.append(
            f'<text x="{nx:.1f}" y="{ny + emoji_size/2 + 4:.1f}" text-anchor="middle" '
            f'font-size="{name_size}" fill="{name_color}" font-family="serif">'
            f'{day["name"]}</text>'
        )

    # ── Inner ring: 13 Sacred Numbers ─────────────────────────
    r_num_out = r_in - size * 0.01
    r_num_in  = r_in - size * 0.09
    num_slice = 360.0 / 13
    for n in range(1, 14):
        angle_center = -90 + (n - 1) * num_slice
        angle_start  = angle_center - num_slice / 2
        angle_end    = angle_center + num_slice / 2

        is_active_n = (n == current_number)
        fill_c = "#4a1a00" if is_active_n else "#1e0e00"
        stroke_c = HIGHLIGHT_RING_COLOR if is_active_n else "#6b3a00"

        path_d = _slice_path(cx, cy, r_num_out, r_num_in, angle_start, angle_end)
        lines.append(
            f'<path d="{path_d}" fill="{fill_c}" stroke="{stroke_c}" stroke-width="1"/>'
        )
        nx, ny = _polar(cx, cy, (r_num_out + r_num_in) / 2, angle_center)
        num_col = HIGHLIGHT_RING_COLOR if is_active_n else "#c8a060"
        lines.append(
            f'<text x="{nx:.1f}" y="{ny:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-size="10" fill="{num_col}" font-weight="bold">'
            f'{n}</text>'
        )

    # ── Inner decorative circle ───────────────────────────────
    r_core = r_num_in - size * 0.01
    lines.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_core:.1f}" '
        f'fill="#0a0415" stroke="#6b3a00" stroke-width="2"/>'
    )

    # Active day sign in centre
    active = TZOLKIN_DAY_DATA[current_sign_index]
    lines.append(
        f'<text x="{cx:.1f}" y="{cy - 28:.1f}" text-anchor="middle" '
        f'font-size="32" dominant-baseline="middle">{active["glyph_emoji"]}</text>'
    )
    lines.append(
        f'<text x="{cx:.1f}" y="{cy + 4:.1f}" text-anchor="middle" '
        f'font-size="16" fill="{HIGHLIGHT_RING_COLOR}" font-weight="bold" font-family="serif">'
        f'{current_number} {active["name"]}</text>'
    )
    lines.append(
        f'<text x="{cx:.1f}" y="{cy + 24:.1f}" text-anchor="middle" '
        f'font-size="11" fill="#d4b896" font-family="serif">'
        f'{active["name_cn"]}</text>'
    )
    # Subtle element label
    element_col = "#aaa"
    lines.append(
        f'<text x="{cx:.1f}" y="{cy + 44:.1f}" text-anchor="middle" '
        f'font-size="9" fill="{element_col}">'
        f'{active["direction_cn"]} · {active["element_cn"]} · {active["deity_cn"][:6]}</text>'
    )

    lines.append("</svg>")
    return "\n".join(lines)


# ============================================================
# 日符號卡片 HTML (Day Sign Card HTML)
# ============================================================

def generate_day_sign_card_html(
    sign_index: int,
    number: int,
    highlighted: bool = False,
    compact: bool = False,
) -> str:
    """
    生成單個日符號的 HTML 卡片。
    Generate an HTML card for a single day sign.

    Parameters
    ----------
    sign_index  : int (0–19)
    number      : int (1–13)
    highlighted : bool — whether to show gold border/glow
    compact     : bool — compact version (smaller text, for grid display)
    """
    day = TZOLKIN_DAY_DATA[sign_index]
    border = "3px solid #FFD700" if highlighted else f"1px solid {day['color']}44"
    glow   = f"box-shadow: 0 0 20px {day['color']}88;" if highlighted else ""
    bg     = f"linear-gradient(135deg, {day['color']}33, #0a0415)"
    padding = "12px" if compact else "18px"
    emoji_size = "36px" if compact else "52px"
    heading_size = "15px" if compact else "20px"

    card = f"""<div style="
        background: {bg};
        border: {border};
        border-radius: 12px;
        padding: {padding};
        text-align: center;
        color: white;
        font-family: 'Georgia', serif;
        {glow}
    ">
        <div style="font-size:{emoji_size}; margin-bottom:6px;">{day['glyph_emoji']}</div>
        <div style="font-size:{heading_size}; font-weight:bold; color:#FFD700;">
            {number} {day['name']}
        </div>
        <div style="font-size:13px; color:#d4b896; margin:4px 0;">
            {day['name_cn']} · {day['name_en']}
        </div>"""

    if not compact:
        card += f"""
        <div style="font-size:11px; color:#aaa; margin:6px 0;">
            {day['direction_cn']} · {day['element_cn']} · {day['deity_cn']}
        </div>
        <hr style="border-color:{day['color']}55; margin:8px 0;">
        <div style="font-size:12px; color:#c8b060; text-align:left; line-height:1.6;">
            {day['personality_cn']}
        </div>"""

    card += "\n    </div>"
    return card


def generate_haab_grid_html(current_haab_month_index: int) -> str:
    """
    生成 Haab 十九個月份的網格 HTML。
    Generate the Haab 19-month grid HTML.
    """
    from .constants import HAAB_MONTHS
    html = '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px;">'
    for i, m in enumerate(HAAB_MONTHS):
        is_active = (i == current_haab_month_index)
        border = "2px solid #FFD700" if is_active else "1px solid #3a2a0a"
        bg = "#3a1000" if i == 18 else ("#2a5a2a" if is_active else "#1a1a2e")
        html += (
            f'<div style="background:{bg};padding:6px;border-radius:6px;'
            f'text-align:center;color:white;{border}">'
            f'<div style="font-size:16px">{m[3]}</div>'
            f'<div style="font-size:10px;font-weight:bold">{m[1]}</div>'
            f'<div style="font-size:9px;color:#aaa">{m[2]}</div>'
            f'</div>'
        )
    html += '</div>'
    return html


def generate_tzolkin_mini_grid_html(current_sign_index: int) -> str:
    """
    生成 Tzolk'in 20 個日符號的小型網格 HTML（用於縮略顯示）。
    Generate a mini grid of all 20 Tzolk'in day signs for thumbnail display.
    """
    from .constants import TZOLKIN_DAY_DATA
    html = '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:4px;">'
    for day in TZOLKIN_DAY_DATA:
        is_active = (day["index"] == current_sign_index)
        border = "2px solid #FFD700" if is_active else f"1px solid {day['color']}44"
        bg = day["color"] if is_active else f"{day['color']}22"
        html += (
            f'<div style="background:{bg};padding:6px;border-radius:6px;'
            f'text-align:center;color:white;border:{border};">'
            f'<div style="font-size:14px">{day["glyph_emoji"]}</div>'
            f'<div style="font-size:9px;font-weight:bold">{day["name"]}</div>'
            f'<div style="font-size:8px;color:#bbb">{day["name_cn"]}</div>'
            f'</div>'
        )
    html += '</div>'
    return html
