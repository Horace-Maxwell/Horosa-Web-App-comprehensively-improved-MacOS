"""
astro/damo — 達摩一掌經排盤模組 (Damo One Palm Scripture Module)

達摩一掌經（又名一掌金）是中國傳統命理術數，相傳由達摩祖師所創。
以左手掌十二地支宮位為基礎，透過年、月、日、時四柱推算出對應的
十二星與六道輪迴，藉此論斷前世今生與性格命運。

Public API:
    compute_damo_chart()  — 純計算函式（可快取）
    render_damo_chart()   — Streamlit 渲染函式
    DamoChart             — 排盤結果資料類
"""

from astro.damo.calculator import compute_damo_chart, DamoChart  # noqa: F401
from astro.damo.renderer import render_damo_chart  # noqa: F401
