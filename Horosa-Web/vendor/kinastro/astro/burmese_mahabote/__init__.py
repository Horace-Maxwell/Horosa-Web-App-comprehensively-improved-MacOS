"""
緬甸／撣族 Mahabote 深度占星子套件
Burmese / Shan Mahabote Deep Astrology sub-package

包含：
  - constants.py  : 完整 8 守護星座資料庫、宮位定義、相容性矩陣
  - calculator.py : 排盤計算、大運小運、流年盤、合婚
  - renderer.py   : Streamlit 多標籤 UI 渲染

古法依據：
  - Barbara Cameron, *The Little Key* (traditional Mahabote handbook)
  - Traditional Pali-Burmese manuscript astrology
  - Shan (Tai Yai) cultural calendar traditions
"""

from .calculator import compute_mahabote_chart, compute_compatibility, MahaboteChart
from .renderer import render_streamlit as render_mahabote_chart

__all__ = [
    "compute_mahabote_chart",
    "render_mahabote_chart",
    "compute_compatibility",
    "MahaboteChart",
]
