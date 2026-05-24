"""Public API for the European Geomancy module."""

from .figures import FIGURES, GeomanticFigure, all_figures, figure_from_pattern, render_figure_svg
from .chart import ShieldChart, build_house_chart, build_shield_chart, render_house_chart_svg, render_shield_chart_svg
from .engine import GeomancyReading, generate_reading, list_figure_names
from .interpretations import astrology_bridge_interpretation, build_ai_prompt, structured_interpretation

__all__ = [
    "FIGURES",
    "GeomanticFigure",
    "ShieldChart",
    "GeomancyReading",
    "all_figures",
    "figure_from_pattern",
    "render_figure_svg",
    "build_shield_chart",
    "build_house_chart",
    "render_shield_chart_svg",
    "render_house_chart_svg",
    "generate_reading",
    "list_figure_names",
    "structured_interpretation",
    "astrology_bridge_interpretation",
    "build_ai_prompt",
]
