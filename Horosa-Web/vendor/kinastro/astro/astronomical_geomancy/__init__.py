"""
astro/astronomical_geomancy/__init__.py
═══════════════════════════════════════
Public API for the Astronomical Geomancy (地占占星) module.
"""

from .calculator import compute_geomancy_chart, format_geomancy_for_prompt
from .renderer import render_streamlit, render_input_panel, build_geomancy_wheel_svg
from .models import (
    GeomancyChart,
    GeomancyFigure,
    HouseInfo,
    PlanetInHouse,
    GeomancyMode,
    GeomancyLayout,
    FigureMeaning,
)
from .chart_renderer_geomancy import render_geomancy_svg_chart, build_square_chart_svg
from .geomancy_figures import get_figure_catalog, get_figure_svg_rows

__all__ = [
    "compute_geomancy_chart",
    "format_geomancy_for_prompt",
    "render_streamlit",
    "render_input_panel",
    "build_geomancy_wheel_svg",
    "render_geomancy_svg_chart",
    "build_square_chart_svg",
    "get_figure_catalog",
    "get_figure_svg_rows",
    "GeomancyChart",
    "GeomancyFigure",
    "HouseInfo",
    "PlanetInHouse",
    "GeomancyMode",
    "GeomancyLayout",
    "FigureMeaning",
]
