"""
astro/astronomical_geomancy/chart_renderer_geomancy.py
══════════════════════════════════════════════════════════════════
Classical 4×4 Square Geomancy Chart SVG renderer.

Faithfully reproduces the antiquarian style of medieval European and
Arabic geomancy manuscripts:
  - 4×4 grid of 16 geomantic figures (dot patterns)
  - Zodiac glyphs (♈…♓) along the top border
  - Planet glyphs (☉☽☿♀♂♃♄☊☋) along the right border
  - Decorative outer border (double-rule with dash pattern)
  - SVG paper-grain filter + ink-bleed displacement filter
  - Parchment ("parchment") and dark ("dark") themes
  - Each figure cell is a deep-link to its wiki entry

Streamlit is imported only inside function bodies (per CONTRIBUTING.md).
"""

from __future__ import annotations

from typing import Dict, List

from .geomancy_figures import (
    CELL_H,
    CELL_W,
    get_figure_catalog,
    get_figure_svg_rows,
)

# ─────────────────────────────────────────────────────────────────────────────
# Themes
# ─────────────────────────────────────────────────────────────────────────────

_THEMES: Dict[str, Dict[str, str]] = {
    "parchment": {
        "paper": "#e8d5a8",
        "cell_odd": "#f0e0bc",
        "cell_even": "#e9d6ae",
        "ink": "#4a2f12",
        "grid": "#9a7040",
        "gold": "#a06820",
        "outer_border": "#7a4a18",
        "sign_color": "#800000",
        "planet_color": "#1a3a80",
        "label_color": "#6a4020",
        "slot_label": "#9a7040",
        "center_fill": "#ddc88a",
        "special_highlight": "#c8a020",
    },
    "dark": {
        "paper": "#0e0c09",
        "cell_odd": "#1a1710",
        "cell_even": "#181510",
        "ink": "#d4a85c",
        "grid": "#6a4a18",
        "gold": "#c8a030",
        "outer_border": "#c0900a",
        "sign_color": "#d06060",
        "planet_color": "#6090c0",
        "label_color": "#a08040",
        "slot_label": "#806030",
        "center_fill": "#1c1a12",
        "special_highlight": "#b88820",
    },
}


def get_theme(name: str) -> Dict[str, str]:
    """Return theme colour dict. Falls back to parchment for unknown names."""
    return _THEMES.get(name, _THEMES["parchment"])


# ─────────────────────────────────────────────────────────────────────────────
# Layout constants
# ─────────────────────────────────────────────────────────────────────────────

_CELL_PX = 175     # pixel size of each square cell in the SVG viewbox
_PAD = 72          # padding around the 4×4 grid (room for zodiac / planets)
_TITLE_H = 36      # extra height above grid for chart title
_FOOT_H = 28       # extra height below grid for attribution
_GRID_W = 4 * _CELL_PX
_GRID_H = 4 * _CELL_PX
_SVG_W = _GRID_W + 2 * _PAD
_SVG_H = _GRID_H + 2 * _PAD + _TITLE_H + _FOOT_H

# Slot labels (index 0-15, row-major)
_SLOT_ZH = [
    "母親一", "母親二", "母親三", "母親四",
    "女兒一", "女兒二", "女兒三", "女兒四",
    "姪輩一", "姪輩二", "姪輩三", "姪輩四",
    "左見證", "右見證", "判  官", "調解者",
]
_SLOT_EN = [
    "Mother I", "Mother II", "Mother III", "Mother IV",
    "Daughter I", "Daughter II", "Daughter III", "Daughter IV",
    "Niece I", "Niece II", "Niece III", "Niece IV",
    "Lt. Witness", "Rt. Witness", "Judge", "Reconciler",
]

# Zodiac glyphs (top border)
_ZODIAC = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

# Planet glyphs (right border)
_PLANETS_GLYPHS = ["☉", "☽", "☿", "♀", "♂", "♃", "♄", "☊", "☋"]


# ─────────────────────────────────────────────────────────────────────────────
# SVG filter definitions (paper grain, ink bleed, dot glow)
# ─────────────────────────────────────────────────────────────────────────────

_SVG_DEFS = """\
<defs>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&amp;family=Noto+Serif+TC:wght@300;400&amp;display=swap');
    .geo-lat { font-family: Cinzel, Georgia, 'Times New Roman', serif; }
    .geo-cjk { font-family: 'Noto Serif TC', 'Noto Sans CJK TC', 'SimSun', serif; }
    .geo-sym { font-family: 'Noto Sans Symbols2', 'Segoe UI Symbol', serif; }
  </style>
  <!-- Paper grain texture -->
  <filter id="paper" x="-5%" y="-5%" width="110%" height="110%">
    <feTurbulence type="fractalNoise" baseFrequency="0.022 0.018"
                  numOctaves="4" seed="17" result="noise"/>
    <feColorMatrix type="saturate" values="0.1" in="noise" result="desatNoise"/>
    <feBlend in="SourceGraphic" in2="desatNoise" mode="multiply" result="blended"/>
    <feComposite in="blended" in2="SourceGraphic" operator="in"/>
  </filter>
  <!-- Ink bleed (slight displacement) -->
  <filter id="inkBleed" x="-3%" y="-3%" width="106%" height="106%">
    <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2"
                  seed="3" result="noise"/>
    <feDisplacementMap in2="noise" in="SourceGraphic" scale="0.8"
                       xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <!-- Dot glow (subtle) -->
  <filter id="dotGlow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="0.7" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>"""


# ─────────────────────────────────────────────────────────────────────────────
# Dot-pattern renderer
# ─────────────────────────────────────────────────────────────────────────────

def _draw_figure_dots(
    name: str,
    ox: float,
    oy: float,
    t: Dict[str, str],
    dot_r: float = 4.2,
) -> str:
    """
    Render the dot pattern for a named geomantic figure at offset (ox, oy).
    ox/oy is the top-left corner of the CELL_W×CELL_H bounding box.
    Returns an SVG fragment string.
    """
    spec = get_figure_svg_rows().get(name)
    if spec is None:
        return ""
    parts: List[str] = []
    for yy, xs in zip(spec["rows_y"], spec["rows_x"]):
        for xx in xs:
            parts.append(
                f'<circle cx="{ox + xx:.1f}" cy="{oy + yy:.1f}" '
                f'r="{dot_r}" fill="{t["ink"]}" />'
            )
    return "".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Main SVG builder
# ─────────────────────────────────────────────────────────────────────────────

def build_square_chart_svg(
    figures_16: List[str],
    center_text: str = "",
    theme: str = "parchment",
    lang: str = "zh",
    chart_title: str = "",
) -> str:
    """
    Build a classical 4×4 Geomancy Square Chart as an SVG string.

    Args:
        figures_16:  16 figure name_en strings (row-major order).
                     Index 0-3 = Mothers 1-4, 4-7 = Daughters 1-4,
                     8-11 = Nieces 1-4, 12-15 = Witnesses/Judge/Reconciler.
        center_text: Short text shown in the centre decorative banner
                     (question summary or "Judgement").
        theme:       "parchment" | "dark"
        lang:        "zh" | "en" — controls slot label language.
        chart_title: Optional title rendered above the grid.

    Returns:
        SVG string (self-contained, no external dependencies at render time).
    """
    t = get_theme(theme)
    catalog = get_figure_catalog()
    slot_labels = _SLOT_ZH if lang == "zh" else _SLOT_EN

    # Grid origin (top-left corner of the 4×4 grid)
    gx = _PAD
    gy = _PAD + _TITLE_H

    parts: List[str] = [
        f'<svg viewBox="0 0 {_SVG_W} {_SVG_H}" xmlns="http://www.w3.org/2000/svg" '
        f'style="max-width:860px;width:100%;display:block;margin:auto;'
        f'background:{t["paper"]}">',
        _SVG_DEFS,
    ]

    # ── Background ────────────────────────────────────────────────────────────
    parts.append(
        f'<rect width="{_SVG_W}" height="{_SVG_H}" fill="{t["paper"]}" filter="url(#paper)"/>'
    )

    # ── Outer ornamental double-rule border ───────────────────────────────────
    parts += [
        f'<rect x="6" y="6" width="{_SVG_W-12}" height="{_SVG_H-12}" '
        f'fill="none" stroke="{t["outer_border"]}" stroke-width="3.5" '
        f'stroke-dasharray="10 4 2 4"/>',
        f'<rect x="12" y="12" width="{_SVG_W-24}" height="{_SVG_H-24}" '
        f'fill="none" stroke="{t["outer_border"]}" stroke-width="1" opacity="0.55"/>',
        # Corner ornaments
        *[
            f'<circle cx="{cx}" cy="{cy}" r="5" fill="{t["gold"]}" opacity="0.7"/>'
            for cx, cy in [
                (20, 20), (_SVG_W - 20, 20),
                (20, _SVG_H - 20), (_SVG_W - 20, _SVG_H - 20),
            ]
        ],
    ]

    # ── Chart title ───────────────────────────────────────────────────────────
    title_text = chart_title or (
        "地占神聖方形圖盤" if lang == "zh" else "The Sacred Square of Geomancy"
    )
    parts.append(
        f'<text x="{_SVG_W / 2:.1f}" y="{_TITLE_H:.1f}" text-anchor="middle" '
        f'class="geo-lat" font-size="16" fill="{t["gold"]}" '
        f'filter="url(#inkBleed)">{title_text}</text>'
    )

    # ── Main grid background ──────────────────────────────────────────────────
    parts.append(
        f'<rect x="{gx}" y="{gy}" width="{_GRID_W}" height="{_GRID_H}" '
        f'fill="{t["cell_odd"]}" stroke="{t["ink"]}" stroke-width="3"/>'
    )

    # Alternating cell background (checkerboard-lite)
    for idx in range(16):
        row, col = divmod(idx, 4)
        cx = gx + col * _CELL_PX
        cy = gy + row * _CELL_PX
        bg = t["cell_even"] if (row + col) % 2 == 0 else t["cell_odd"]
        parts.append(
            f'<rect x="{cx}" y="{cy}" width="{_CELL_PX}" height="{_CELL_PX}" '
            f'fill="{bg}" />'
        )

    # ── Grid lines ────────────────────────────────────────────────────────────
    for i in range(1, 4):
        lx = gx + i * _CELL_PX
        ly = gy + i * _CELL_PX
        parts += [
            f'<line x1="{lx}" y1="{gy}" x2="{lx}" y2="{gy + _GRID_H}" '
            f'stroke="{t["grid"]}" stroke-width="1.8"/>',
            f'<line x1="{gx}" y1="{ly}" x2="{gx + _GRID_W}" y2="{ly}" '
            f'stroke="{t["grid"]}" stroke-width="1.8"/>',
        ]

    # Heavier border around the final row (Witnesses/Judge/Reconciler)
    final_row_y = gy + 3 * _CELL_PX
    parts.append(
        f'<line x1="{gx}" y1="{final_row_y}" x2="{gx + _GRID_W}" y2="{final_row_y}" '
        f'stroke="{t["outer_border"]}" stroke-width="3"/>'
    )

    # ── Row group labels on left margin ───────────────────────────────────────
    _row_labels = (
        ["母親", "女兒", "姪輩", "見證·判官"] if lang == "zh"
        else ["Mothers", "Daughters", "Nieces", "Witnesses & Judge"]
    )
    for ri, rl in enumerate(_row_labels):
        mid_y = gy + ri * _CELL_PX + _CELL_PX // 2
        parts.append(
            f'<text x="{gx - 10:.1f}" y="{mid_y:.1f}" '
            f'text-anchor="middle" class="geo-cjk" '
            f'font-size="10" fill="{t["slot_label"]}" opacity="0.85" '
            f'transform="rotate(-90,{gx - 10:.1f},{mid_y:.1f})">{rl}</text>'
        )

    # ── Individual figure cells ───────────────────────────────────────────────
    for idx in range(min(16, len(figures_16))):
        row, col = divmod(idx, 4)
        cx = gx + col * _CELL_PX
        cy = gy + row * _CELL_PX
        fig_name = figures_16[idx]
        info = catalog.get(fig_name, {})
        slot_lbl = slot_labels[idx] if idx < len(slot_labels) else ""
        latin = info.get("latin", fig_name)
        zh_name = info.get("zh", "")
        wiki = info.get("wiki", "")
        omen = info.get("omen_zh" if lang == "zh" else "omen_en", "")

        # Special highlight for Judge (idx 14) and Reconciler (idx 15)
        if idx >= 14:
            parts.append(
                f'<rect x="{cx + 2}" y="{cy + 2}" '
                f'width="{_CELL_PX - 4}" height="{_CELL_PX - 4}" '
                f'fill="{t["special_highlight"]}" opacity="0.12" rx="3"/>'
            )

        # Slot position label (small, top-left of cell)
        parts.append(
            f'<text x="{cx + 7}" y="{cy + 15}" class="geo-cjk" '
            f'font-size="9" fill="{t["slot_label"]}" opacity="0.9">'
            f'{slot_lbl}</text>'
        )

        # Figure dot pattern (centred in cell)
        dot_ox = cx + (_CELL_PX - CELL_W) / 2
        dot_oy = cy + 20
        dot_svg = _draw_figure_dots(fig_name, dot_ox, dot_oy, t, dot_r=4.0)
        if dot_svg:
            parts.append(f'<g filter="url(#dotGlow)">{dot_svg}</g>')

        # Figure name — Latin (Cinzel, bottom of cell)
        lname_y = cy + _CELL_PX - 26
        parts.append(
            f'<text x="{cx + _CELL_PX / 2:.1f}" y="{lname_y:.1f}" '
            f'text-anchor="middle" class="geo-lat" '
            f'font-size="11.5" fill="{t["ink"]}" filter="url(#inkBleed)">'
            f'{latin}</text>'
        )

        # Figure name — Chinese (below Latin)
        if zh_name:
            cname_y = cy + _CELL_PX - 12
            parts.append(
                f'<text x="{cx + _CELL_PX / 2:.1f}" y="{cname_y:.1f}" '
                f'text-anchor="middle" class="geo-cjk" '
                f'font-size="9.5" fill="{t["label_color"]}">'
                f'{zh_name}</text>'
            )

        # Clickable transparent overlay → wiki link
        if wiki:
            omen_escaped = omen[:100].replace("&", "&amp;").replace("<", "&lt;")
            parts.append(
                f'<a href="{wiki}" target="_blank">'
                f'<rect x="{cx + 2}" y="{cy + 2}" '
                f'width="{_CELL_PX - 4}" height="{_CELL_PX - 4}" '
                f'fill="transparent" cursor="pointer">'
                f'<title>{latin} / {zh_name}&#10;{omen_escaped}</title>'
                f'</rect></a>'
            )

    # ── Centre decorative cross ───────────────────────────────────────────────
    # Thin gold lines crossing the middle of the grid
    cx_mid = gx + _GRID_W / 2
    cy_mid = gy + _GRID_H / 2
    cross_half = min(_GRID_W, _GRID_H) * 0.36
    # Horizontal line
    parts.append(
        f'<line x1="{cx_mid - cross_half:.1f}" y1="{cy_mid:.1f}" '
        f'x2="{cx_mid + cross_half:.1f}" y2="{cy_mid:.1f}" '
        f'stroke="{t["gold"]}" stroke-width="0.8" '
        f'stroke-dasharray="6 4" opacity="0.35"/>'
    )
    # Vertical line
    parts.append(
        f'<line x1="{cx_mid:.1f}" y1="{cy_mid - cross_half:.1f}" '
        f'x2="{cx_mid:.1f}" y2="{cy_mid + cross_half:.1f}" '
        f'stroke="{t["gold"]}" stroke-width="0.8" '
        f'stroke-dasharray="6 4" opacity="0.35"/>'
    )

    # ── Centre caption (over grid lines) ─────────────────────────────────────
    if center_text:
        ct = center_text[:70]
        parts += [
            f'<rect x="{cx_mid - 130:.1f}" y="{cy_mid - 18:.1f}" '
            f'width="260" height="36" rx="5" '
            f'fill="{t["center_fill"]}" stroke="{t["gold"]}" '
            f'stroke-width="1.2" opacity="0.88"/>',
            f'<text x="{cx_mid:.1f}" y="{cy_mid + 6:.1f}" '
            f'text-anchor="middle" class="geo-cjk" '
            f'font-size="12" fill="{t["ink"]}">{ct}</text>',
        ]

    # ── Zodiac glyphs along top border ────────────────────────────────────────
    z_step = _GRID_W / 12
    for i, gz in enumerate(_ZODIAC):
        zx = gx + (i + 0.5) * z_step
        parts.append(
            f'<text x="{zx:.1f}" y="{gy - 20:.1f}" text-anchor="middle" '
            f'class="geo-sym" font-size="20" fill="{t["sign_color"]}">{gz}</text>'
        )

    # ── Planet glyphs along right border ─────────────────────────────────────
    p_step = _GRID_H / len(_PLANETS_GLYPHS)
    for i, gp in enumerate(_PLANETS_GLYPHS):
        py = gy + (i + 0.5) * p_step
        parts.append(
            f'<text x="{gx + _GRID_W + 32:.1f}" y="{py + 7:.1f}" '
            f'text-anchor="middle" class="geo-sym" '
            f'font-size="18" fill="{t["planet_color"]}">{gp}</text>'
        )

    # ── Attribution footer ────────────────────────────────────────────────────
    parts.append(
        f'<text x="{_SVG_W / 2:.1f}" y="{gy + _GRID_H + _FOOT_H - 2:.1f}" '
        f'text-anchor="middle" class="geo-lat" '
        f'font-size="10" fill="{t["label_color"]}" opacity="0.75">'
        f'Geomantia Astronomica · Gerardus Cremonensis · XII c.</text>'
    )

    parts.append("</svg>")
    return "".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Streamlit render wrapper
# ─────────────────────────────────────────────────────────────────────────────

def render_geomancy_svg_chart(
    figures_16: List[str],
    center_text: str = "",
    theme: str = "parchment",
    lang: str = "zh",
    chart_title: str = "",
    height: int = 900,
) -> None:
    """
    Render the classical square geomancy chart in Streamlit.

    Args:
        figures_16:  16 figure name_en strings.
        center_text: Question / summary shown in the centre banner.
        theme:       "parchment" | "dark"
        lang:        "zh" | "en"
        chart_title: Optional title above the grid.
        height:      iframe height in pixels.
    """
    import streamlit.components.v1 as components  # lazy import per convention

    svg = build_square_chart_svg(
        figures_16=figures_16,
        center_text=center_text,
        theme=theme,
        lang=lang,
        chart_title=chart_title,
    )
    components.html(svg, height=height, scrolling=True)
