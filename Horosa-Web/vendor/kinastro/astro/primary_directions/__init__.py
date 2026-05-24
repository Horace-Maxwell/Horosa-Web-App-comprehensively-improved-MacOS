"""
astro/primary_directions — Classical Primary Directions (古典主限推運)

Implements the Hellenistic / Traditional Western Primary Directions system:

  - Zodiacal Primary Directions (黃道主限): Oblique Ascension method
    [Ptolemy, Tetrabiblos c. 150 CE]

  - Mundo Primary Directions (世間主限): Placidus Semi-Arc method
    [Placidus de Titis, Primum Mobile 1657; Gansten 2009]

  - Direct and Converse directions
  - Five major aspects: conjunction, sextile, square, trine, opposition
  - Parallel and contra-parallel of declination
  - Time keys: Naibod (default), Ptolemy (1°/yr), Solar Arc

  - Classical manuscript-style SVG timeline visualization
  - Bilingual (Chinese / English) delineations

Public API:
    compute_primary_directions    — full computation
    render_primary_directions     — Streamlit UI
    render_primary_directions_svg — standalone SVG timeline
"""

from .calculator import (
    compute_primary_directions,
    ChartPoint,
    Direction,
    PrimaryDirectionsResult,
)
from .renderer import (
    render_primary_directions,
    render_primary_directions_svg,
)
from .constants import EXAMPLE_CHARTS

__all__ = [
    "compute_primary_directions",
    "ChartPoint",
    "Direction",
    "PrimaryDirectionsResult",
    "render_primary_directions",
    "render_primary_directions_svg",
    "EXAMPLE_CHARTS",
]
