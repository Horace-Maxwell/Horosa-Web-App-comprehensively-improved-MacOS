"""
astro/esoteric — Alice Bailey 七道光線靈性占星體系

Implements Alice A. Bailey's Esoteric Astrology system as described in:
  - *Esoteric Astrology* (A Treatise on the Seven Rays, Vol. III, Lucis Publishing 1951)
  - *Esoteric Psychology* Vol. I–II
  - *A Treatise on the Seven Rays* Vol. I–V

Public API:
    compute_esoteric_chart   — compute a complete Esoteric Astrology chart
    render_streamlit         — Streamlit UI renderer
    render_esoteric_chart_svg — generate a Seven Rays Mandala SVG
    EsotericChart            — chart result dataclass
    SEVEN_RAYS               — Seven Rays data dictionary
    SIGN_RULERS              — Esoteric rulers for all 12 signs
    EXAMPLE_CHARTS           — Example birth data for testing
"""

from .calculator import (
    compute_esoteric_chart,
    get_ray_interaction_analysis,
    EsotericChart,
    EsotericPoint,
    RayIndicator,
    RayTally,
)
from .renderer import render_streamlit, render_esoteric_chart_svg
from .constants import (
    SEVEN_RAYS,
    SIGN_RULERS,
    PLANET_RAY_MAP,
    ZODIAC_SIGNS,
    SIGN_ZH,
    EXAMPLE_CHARTS,
    RayData,
    SignRulers,
)

__all__ = [
    "compute_esoteric_chart",
    "get_ray_interaction_analysis",
    "EsotericChart",
    "EsotericPoint",
    "RayIndicator",
    "RayTally",
    "render_streamlit",
    "render_esoteric_chart_svg",
    "SEVEN_RAYS",
    "SIGN_RULERS",
    "PLANET_RAY_MAP",
    "ZODIAC_SIGNS",
    "SIGN_ZH",
    "EXAMPLE_CHARTS",
    "RayData",
    "SignRulers",
]
