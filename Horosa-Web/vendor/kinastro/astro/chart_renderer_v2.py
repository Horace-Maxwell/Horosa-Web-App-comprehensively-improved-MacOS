"""
astro/chart_renderer_v2.py — Cultural SVG Chart Wrapper (v2)

Provides ``build_cultural_svg()`` which wraps any raw SVG string in a
culturally-themed container with CSS class, hover glow, and optional
slow-spin animation.  All culture-specific visual effects are driven by
the CSS classes defined in ``styles/custom.css`` and
``astro/chart_theme.py`` — this module only generates the HTML wrapper.

Enhanced in v2.1 with:
- SVG filter defs (glow, drop-shadow, radial gradients)
- ``inject_svg_enhancements()`` to upgrade existing SVG strings
- ``build_legend_html()`` for chart legend blocks
- Theme-aware colour helpers using ``astro.chart_theme``
"""

from __future__ import annotations
import re

from astro.icons import SYSTEM_CSS_CLASS
from astro.chart_theme import (
    ASPECT_COLORS,
    PLANET_COLORS,
    CHART_BG,
    CHART_RING_STROKE,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    FONT_FAMILY,
)

# ═══════════════════════════════════════════════════════════════
# SVG quality helpers
# ═══════════════════════════════════════════════════════════════

_SVG_DEFS_ID = "kinastro-v2-defs"

_SVG_DEFS_TEMPLATE = """\
<defs id="{defs_id}">
  <!-- Soft outer glow for planet symbols -->
  <filter id="ka-glow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="blur"/>
    <feComposite in="SourceGraphic" in2="blur" operator="over"/>
  </filter>
  <!-- Subtle drop-shadow for house cusps and rings -->
  <filter id="ka-shadow" x="-10%" y="-10%" width="120%" height="120%">
    <feDropShadow dx="0" dy="1" stdDeviation="2"
                  flood-color="rgba(0,0,0,0.55)" flood-opacity="1"/>
  </filter>
  <!-- Deep-space radial background gradient -->
  <radialGradient id="ka-bg-grad" cx="50%" cy="50%" r="50%">
    <stop offset="0%"   stop-color="{inner_color}" stop-opacity="1"/>
    <stop offset="100%" stop-color="{outer_color}" stop-opacity="1"/>
  </radialGradient>
  <!-- Aspect line gradients per major aspect -->
  <linearGradient id="ka-aspect-trine" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%"   stop-color="#00AA00" stop-opacity="0.85"/>
    <stop offset="100%" stop-color="#00CC55" stop-opacity="0.85"/>
  </linearGradient>
  <linearGradient id="ka-aspect-square" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%"   stop-color="#FF4500" stop-opacity="0.85"/>
    <stop offset="100%" stop-color="#FF6030" stop-opacity="0.85"/>
  </linearGradient>
  <linearGradient id="ka-aspect-opposition" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%"   stop-color="#FF0000" stop-opacity="0.80"/>
    <stop offset="100%" stop-color="#CC0033" stop-opacity="0.80"/>
  </linearGradient>
  <linearGradient id="ka-aspect-sextile" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%"   stop-color="#4169E1" stop-opacity="0.80"/>
    <stop offset="100%" stop-color="#6688FF" stop-opacity="0.80"/>
  </linearGradient>
  <linearGradient id="ka-aspect-conjunction" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%"   stop-color="#FFD700" stop-opacity="0.90"/>
    <stop offset="100%" stop-color="#FFA500" stop-opacity="0.90"/>
  </linearGradient>
  <!-- Ring stroke gradient -->
  <linearGradient id="ka-ring-grad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%"   stop-color="{ring_color}" stop-opacity="0.9"/>
    <stop offset="50%"  stop-color="{accent_color}" stop-opacity="0.6"/>
    <stop offset="100%" stop-color="{ring_color}" stop-opacity="0.9"/>
  </linearGradient>
</defs>"""


def build_svg_defs(
    inner_color: str = "#1a1740",
    outer_color: str = "#0a0920",
) -> str:
    """Return an SVG ``<defs>`` block with KinAstro filter and gradient defs.

    Insert this string immediately after the opening ``<svg …>`` tag of any
    chart SVG to enable the glow/shadow filters and gradients defined here.

    Parameters
    ----------
    inner_color : str
        Centre colour of the radial background gradient.
    outer_color : str
        Edge colour of the radial background gradient.
    """
    return _SVG_DEFS_TEMPLATE.format(
        defs_id=_SVG_DEFS_ID,
        inner_color=inner_color,
        outer_color=outer_color,
        ring_color=CHART_RING_STROKE,
        accent_color=PRIMARY_COLOR,
    )


def inject_svg_enhancements(
    svg_content: str,
    *,
    inner_color: str = "#1a1740",
    outer_color: str = "#0a0920",
) -> str:
    """Inject KinAstro SVG defs into an existing SVG string.

    If the SVG already contains the defs block (identified by
    ``id="kinastro-v2-defs"``), the function returns *svg_content* unchanged.

    Parameters
    ----------
    svg_content : str
        A complete ``<svg …>…</svg>`` string.
    inner_color, outer_color : str
        Colours for the radial background gradient defs.

    Returns
    -------
    str
        The enhanced SVG string with defs injected.
    """
    if _SVG_DEFS_ID in svg_content:
        return svg_content  # already enhanced

    # Find the first closing '>' of the opening <svg> tag and insert after it.
    match = re.search(r"<svg[^>]*>", svg_content, re.IGNORECASE)
    if not match:
        return svg_content  # not a valid SVG, return as-is

    insert_pos = match.end()
    defs = build_svg_defs(inner_color=inner_color, outer_color=outer_color)
    return svg_content[:insert_pos] + "\n" + defs + svg_content[insert_pos:]


def build_legend_html(
    items: list[tuple[str, str]],
    *,
    title: str = "",
    columns: int = 3,
) -> str:
    """Build an HTML legend block for a chart.

    Parameters
    ----------
    items : list of (label, colour) tuples
        Each entry is a (display label, hex colour) pair shown as a
        coloured dot + label.
    title : str, optional
        Optional heading rendered above the legend grid.
    columns : int
        Number of CSS grid columns (default 3).

    Returns
    -------
    str
        HTML string safe for ``st.markdown(..., unsafe_allow_html=True)``.
    """
    rows_html = ""
    for label, color in items:
        rows_html += (
            f'<div class="ka-legend-item">'
            f'<span class="ka-legend-dot" style="background:{color};'
            f'box-shadow:0 0 6px {color}80;"></span>'
            f'<span class="ka-legend-label">{label}</span>'
            f"</div>"
        )

    title_html = (
        f'<div class="ka-legend-title">{title}</div>' if title else ""
    )

    return (
        f'<div class="ka-legend-block">'
        f"{title_html}"
        f'<div class="ka-legend-grid" style="grid-template-columns:repeat({columns},1fr);">'
        f"{rows_html}"
        f"</div>"
        f"</div>"
        f"<style>"
        f".ka-legend-block{{margin:8px 0 16px;padding:10px 14px;"
        f"background:rgba(255,255,255,0.04);border:1px solid rgba(167,139,250,0.18);"
        f"border-radius:10px;}}"
        f".ka-legend-title{{font-size:0.78rem;color:#b0b0d0;"
        f"letter-spacing:.06em;text-transform:uppercase;margin-bottom:8px;}}"
        f".ka-legend-grid{{display:grid;gap:6px 12px;}}"
        f".ka-legend-item{{display:flex;align-items:center;gap:6px;"
        f"font-size:0.82rem;color:#e0e0ff;}}"
        f".ka-legend-dot{{display:inline-block;width:10px;height:10px;"
        f"border-radius:50%;flex-shrink:0;}}"
        f".ka-legend-label{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}"
        f"</style>"
    )


def build_planet_legend(planet_keys: list[str] | None = None) -> str:
    """Return a legend block for the standard planet colour palette.

    Parameters
    ----------
    planet_keys : list of str, optional
        Planet names to include (e.g. ``["Sun", "Moon", "Mercury"]``).
        Defaults to all planets in :data:`astro.chart_theme.PLANET_COLORS`.
    """
    keys = planet_keys or list(PLANET_COLORS.keys())
    items = [(k, PLANET_COLORS[k]) for k in keys if k in PLANET_COLORS]
    return build_legend_html(items, title="Planets", columns=4)


def build_aspect_legend() -> str:
    """Return a legend block for the standard aspect colour palette."""
    items = list(ASPECT_COLORS.items())
    return build_legend_html(items, title="Aspects", columns=3)


# ═══════════════════════════════════════════════════════════════
# Cultural SVG wrapper
# ═══════════════════════════════════════════════════════════════

def build_cultural_svg(
    svg_content: str,
    system_key: str,
    *,
    title: str = "",
    animate_spin: bool = False,
    extra_class: str = "",
    enhance_svg: bool = True,
    show_legend: bool = False,
    legend_type: str = "planet",
) -> str:
    """Wrap *svg_content* in a themed ``<div>`` with culture CSS class.

    Parameters
    ----------
    svg_content : str
        Raw SVG markup (``<svg …>…</svg>``).
    system_key : str
        The system tab key, e.g. ``"tab_aztec"``.  Used to look up the
        CSS class from :data:`astro.icons.SYSTEM_CSS_CLASS`.
    title : str, optional
        Optional heading rendered above the chart.
    animate_spin : bool, optional
        If *True*, add the ``chart-slow-spin`` class for a gentle
        continuous rotation animation.
    extra_class : str, optional
        Additional CSS classes to append to the container.

    Returns
    -------
    str
        An HTML string safe for ``st.markdown(..., unsafe_allow_html=True)``.
    enhance_svg : bool, optional
        If *True* (default), call :func:`inject_svg_enhancements` to add
        glow/shadow filter defs to the raw SVG markup.
    show_legend : bool, optional
        If *True*, append a colour legend below the chart.
    legend_type : str, optional
        ``"planet"`` (default) or ``"aspect"`` — which legend to render.
    """
    culture_cls = SYSTEM_CSS_CLASS.get(system_key, "")
    spin_cls = " chart-slow-spin" if animate_spin else ""
    extra = f" {extra_class}" if extra_class else ""

    classes = f"chart-v2-container chart-glow-wrap{spin_cls} {culture_cls}{extra}".strip()

    # Optionally inject SVG quality enhancements (filters/gradients)
    if enhance_svg and svg_content.strip().startswith("<svg"):
        svg_content = inject_svg_enhancements(svg_content)

    parts: list[str] = []
    parts.append(f'<div class="{classes}">')
    if title:
        parts.append(f'<div class="chart-v2-title">{title}</div>')
    parts.append(svg_content)
    parts.append("</div>")

    if show_legend:
        if legend_type == "aspect":
            parts.append(build_aspect_legend())
        else:
            parts.append(build_planet_legend())

    return "\n".join(parts)


def build_culture_info_card(
    system_key: str,
    heading: str,
    body: str,
) -> str:
    """Return a small glassmorphism popup card with cultural styling.

    This is the 'click-to-reveal detail card' described in the UI spec.
    """
    culture_cls = SYSTEM_CSS_CLASS.get(system_key, "")
    return (
        f'<div class="culture-info-card {culture_cls}">'
        f'<h4>{heading}</h4>'
        f'<p>{body}</p>'
        f'</div>'
    )
