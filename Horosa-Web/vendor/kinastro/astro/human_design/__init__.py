# -*- coding: utf-8 -*-
"""
astro/human_design/__init__.py — Human Design 人間圖模組公開介面

Human Design system (Ra Uru Hu / Jovian Archive) — complete chart calculation
using pyswisseph for high-accuracy planetary positions.

Public API:
    compute_human_design_chart — compute a complete Human Design chart
    HumanDesignChart           — chart result dataclass
    GateActivation             — single planet gate/line activation
    ChannelActivation          — active channel with source info
    render_bodygraph_svg       — generate BodyGraph SVG string
    EXAMPLE_CHARTS             — example birth data for testing
"""

from .calculator import (
    compute_human_design_chart,
    HumanDesignChart,
    GateActivation,
    ChannelActivation,
)
from .constants import (
    EXAMPLE_CHARTS,
    CHANNELS,
    CENTER_GATES,
    GATE_SEQUENCE,
    longitude_to_gate_line,
)


# renderer imports streamlit — defer to avoid breaking non-UI imports
def _get_render_streamlit():  # noqa: ANN201
    from .renderer import render_streamlit as _r
    return _r


def render_streamlit(*args, **kwargs):
    """Human Design Streamlit 渲染入口（延遲載入 streamlit）"""
    return _get_render_streamlit()(*args, **kwargs)


def render_bodygraph_svg(*args, **kwargs):
    """Generate BodyGraph SVG (deferred import)."""
    from .renderer import render_bodygraph_svg as _r
    return _r(*args, **kwargs)


__all__ = [
    "compute_human_design_chart",
    "HumanDesignChart",
    "GateActivation",
    "ChannelActivation",
    "render_streamlit",
    "render_bodygraph_svg",
    "EXAMPLE_CHARTS",
    "CHANNELS",
    "CENTER_GATES",
    "GATE_SEQUENCE",
    "longitude_to_gate_line",
]
