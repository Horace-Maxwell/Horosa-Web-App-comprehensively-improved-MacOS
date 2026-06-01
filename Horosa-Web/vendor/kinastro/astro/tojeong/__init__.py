"""
astro/tojeong — 土亭數排盤模組 (Tojeong Shu / 土亭數)

土亭數是朝鮮時代土亭李先生所創的占數系統。
以出生年月日時干支，配合先天數、後天數計算，得格局代碼，
查 129 格局斷語推斷吉凶。

核心算法：
1. 先天數：干順支逆，除十取零 → 置上為實
2. 後天數：順計干支，除百十取零 → 置下為法
3. 位位相乘，去首尾兩位 → 格局代碼
4. 查 129 格局斷語
"""

from .tojeong_calculator import compute_tojeong_chart, get_tojeong_pattern
from .tojeong_renderer import render_tojeong_chart

__all__ = [
    "compute_tojeong_chart",
    "get_tojeong_pattern",
    "render_tojeong_chart"
]
