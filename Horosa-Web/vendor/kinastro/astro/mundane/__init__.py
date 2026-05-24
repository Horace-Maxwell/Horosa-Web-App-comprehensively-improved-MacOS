"""
astro/mundane — Mundane Astrology Module (世俗占星 / 國家占星 / 世界占星)

Mundane Astrology studies nations, historical eras, and collective destiny.
This module covers:
  - Ingress Charts (入宮圖): Sun's entry into cardinal signs
  - Eclipse Charts (日月食): Solar and lunar eclipse positions
  - Great Conjunctions (木土大合相): Jupiter-Saturn 20-year cycle
  - National Overview (國家運勢): Country-specific Mundane charts

Entry points (lazy-loaded to avoid importing Streamlit in non-UI contexts):
  - compute_ingress_chart(...)     → MundaneChart
  - compute_eclipse_chart(...)     → (EclipseInfo, MundaneChart)
  - get_great_conjunctions_timeline(...) → List[GreatConjunction]
  - render_streamlit(...)          → None (Streamlit UI)

Usage::

    from astro.mundane import compute_ingress_chart, render_streamlit

    chart = compute_ingress_chart(year=2025, ingress_type="aries")
    # or in Streamlit context:
    render_streamlit()
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .calculator import MundaneChart, EclipseInfo, GreatConjunction


def compute_ingress_chart(*args, **kwargs):  # type: ignore[override]
    """Lazy-load and call the ingress chart calculator."""
    from .calculator import compute_ingress_chart as _fn
    return _fn(*args, **kwargs)


def compute_eclipse_chart(*args, **kwargs):  # type: ignore[override]
    """Lazy-load and call the eclipse chart calculator."""
    from .calculator import compute_eclipse_chart as _fn
    return _fn(*args, **kwargs)


def get_great_conjunctions_timeline(*args, **kwargs):  # type: ignore[override]
    """Lazy-load and return the Great Conjunctions timeline."""
    from .calculator import get_great_conjunctions_timeline as _fn
    return _fn(*args, **kwargs)


def compute_current_outer_planets(*args, **kwargs):  # type: ignore[override]
    """Lazy-load and compute current outer planet positions."""
    from .calculator import compute_current_outer_planets as _fn
    return _fn(*args, **kwargs)


def render_streamlit(*args, **kwargs):  # type: ignore[override]
    """Lazy-load and call the Streamlit renderer."""
    from .renderer import render_streamlit as _fn
    return _fn(*args, **kwargs)


__all__ = [
    "compute_ingress_chart",
    "compute_eclipse_chart",
    "get_great_conjunctions_timeline",
    "compute_current_outer_planets",
    "render_streamlit",
]
