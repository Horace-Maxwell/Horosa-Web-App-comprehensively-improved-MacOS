"""
astro/maya — 瑪雅占星模組 (Maya Astrology Module)

包含 Tzolk'in（神聖曆）、Long Count（長紀年）、Haab（民用曆）及 Calendar Round 的
完整計算與渲染功能，使用 GMT 關聯公式（JD 584283 = 0.0.0.0.0 = 4 Ajaw 8 Kumku）。

Contains full calculation and rendering for Tzolk'in, Long Count, Haab, and Calendar Round
using the GMT correlation (JD 584283 = 0.0.0.0.0 = 4 Ajaw 8 Kumku).

Backward-compatible: exposes compute_maya_chart() and render_maya_chart() at
the same module path as the original astro/maya.py.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .calculator import MayanChart


def compute_maya_chart(*args, **kwargs) -> "MayanChart":
    """Lazy-load and call the Maya chart calculator."""
    from .calculator import compute_maya_chart as _fn
    return _fn(*args, **kwargs)


def render_maya_chart(*args, **kwargs) -> None:
    """Lazy-load and call the Streamlit renderer."""
    from .renderer import render_maya_chart as _fn
    return _fn(*args, **kwargs)


__all__ = ["compute_maya_chart", "render_maya_chart"]
