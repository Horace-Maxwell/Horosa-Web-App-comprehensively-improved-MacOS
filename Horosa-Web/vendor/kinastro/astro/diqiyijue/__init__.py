"""Public API for the Di Qi Yi Jue module."""

from __future__ import annotations
from typing import TYPE_CHECKING

from .calculator import DiQiYiJue, DiqiyijueChart, DiqiyijueEngine, compute_diqiyijue_chart

if TYPE_CHECKING:
    from typing import Any


def render_diqiyijue_chart(*args, **kwargs) -> None:
    """Lazy-load and call the Streamlit renderer."""
    from .renderer import render_diqiyijue_chart as _fn
    return _fn(*args, **kwargs)


__all__ = [
    'DiQiYiJue',
    'DiqiyijueChart',
    'DiqiyijueEngine',
    'compute_diqiyijue_chart',
    'render_diqiyijue_chart',
]
