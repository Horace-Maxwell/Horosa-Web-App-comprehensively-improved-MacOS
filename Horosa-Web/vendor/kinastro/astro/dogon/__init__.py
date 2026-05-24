"""
astro/dogon — Dogon Sirius Cosmology module.

Lazy exports to avoid Streamlit dependency during non-UI imports.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .calculator import DogonSiriusChart


def compute_dogon_sirius_chart(*args, **kwargs):
    from .calculator import compute_dogon_sirius_chart as _fn
    return _fn(*args, **kwargs)


def format_dogon_sirius_for_prompt(*args, **kwargs) -> str:
    from .calculator import format_dogon_sirius_for_prompt as _fn
    return _fn(*args, **kwargs)


def render_dogon_sirius_chart(*args, **kwargs) -> None:
    from .renderer import render_dogon_sirius_chart as _fn
    return _fn(*args, **kwargs)


def build_cross_system_comparison(*args, **kwargs) -> str:
    from .interpretations import build_cross_system_comparison as _fn
    return _fn(*args, **kwargs)


__all__ = [
    "compute_dogon_sirius_chart",
    "format_dogon_sirius_for_prompt",
    "render_dogon_sirius_chart",
    "build_cross_system_comparison",
]
