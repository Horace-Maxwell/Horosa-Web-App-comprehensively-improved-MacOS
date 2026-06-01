"""
astro/fendjing — 鬼谷分定經排盤模組 (Ghost Valley Fen Ding Jing / Two-End Pincers)

鬼谷分定經，又名兩頭鉗，相傳為戰國時期鬼谷子所創。
以出生年時天干排盤，配合十二宮與星曜，推斷一生命運。
"""

from .fendjing_calculator import compute_fendjing_chart, render_fendjing_chart

__all__ = ["compute_fendjing_chart", "render_fendjing_chart"]
