"""KinAstro Kinketika 公開 API。"""

from __future__ import annotations

from .engine import KinketikaEngine, SystemKey
from .ketika_data import ACTIVITY_CATALOGUE, BINTANG_TUJUH, FORTUNE_LABELS, KETIKA_LIMA, KetikaPeriod


def render_streamlit(*args, **kwargs):
    """延遲載入 Streamlit renderer。"""
    from .renderer import render_streamlit as _fn

    return _fn(*args, **kwargs)


__all__ = [
    "ACTIVITY_CATALOGUE",
    "BINTANG_TUJUH",
    "FORTUNE_LABELS",
    "KETIKA_LIMA",
    "KetikaPeriod",
    "KinketikaEngine",
    "SystemKey",
    "render_streamlit",
]
