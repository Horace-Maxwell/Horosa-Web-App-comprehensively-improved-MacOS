# -*- coding: utf-8 -*-
"""
astro/shanghan_qianfa — 傷寒鈐法模組

Classical Chinese medical divination based on the Shang Han Lun (傷寒論),
using stem-branch (干支) Qianfa push-calculation to identify the Six Channels
(六經辨證) and recommend classical formulas (經方).
"""

from .calculator import compute_shanghan_qianfa, ShanghanResult
from .renderer import render_streamlit

__all__ = ["compute_shanghan_qianfa", "ShanghanResult", "render_streamlit"]
