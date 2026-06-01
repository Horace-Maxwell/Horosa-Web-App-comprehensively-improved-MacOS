"""Public API for Huangji Jingshi module."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .huangji import HuangjiPanResult


def compute_huangji_pan(*args, **kwargs) -> "HuangjiPanResult":
    from .huangji import compute_huangji_pan as _fn

    return _fn(*args, **kwargs)


def render_streamlit(*args, **kwargs) -> None:
    from .renderer import render_streamlit as _fn

    return _fn(*args, **kwargs)


def get_classics_data(key: str = "xinyi_fawei") -> dict:
    """Return loaded classics JSON data.

    Args:
        key: One of 'xinyi_fawei', 'huangji_jingshi_shu', 'guanwu_yanyi'.
    """
    from .huangji import _GUANWU_YANYI, _HUANGJI_JINGSHI_SHU, _XINYI_FAWEI

    mapping = {
        "xinyi_fawei": _XINYI_FAWEI,
        "huangji_jingshi_shu": _HUANGJI_JINGSHI_SHU,
        "guanwu_yanyi": _GUANWU_YANYI,
    }
    return mapping.get(key, {})


__all__ = ["compute_huangji_pan", "render_streamlit", "get_classics_data"]
