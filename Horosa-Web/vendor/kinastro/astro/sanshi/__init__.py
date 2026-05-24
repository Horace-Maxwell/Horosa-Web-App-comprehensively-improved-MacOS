"""
astro/sanshi — 三式（大六壬、奇門遁甲、太乙神數）整合模組
Sanshi (Three Styles) — Da Liu Ren, Qi Men Dun Jia, Taiyi Shen Shu

Public API:
    compute_liuren_chart()  — 大六壬排盤計算
    render_liuren_chart()   — 大六壬 Streamlit 渲染
    compute_qimen_chart()   — 奇門遁甲排盤計算
    render_qimen_chart()    — 奇門遁甲 Streamlit 渲染
    compute_taiyi_chart()   — 太乙神數（命法）計算
    render_taiyi_chart()    — 太乙神數 Streamlit 渲染
    LunMingAnalyzer         — 大六壬論命分析
    compute_qimen_luming()  — 奇門祿命計算
    render_qimen_luming()   — 奇門祿命 Streamlit 渲染
"""

from astro.sanshi.liuren import compute_liuren_chart, render_liuren_chart  # noqa: F401
from astro.sanshi.liuren import compute_lunming, render_lunming_report  # noqa: F401
from astro.sanshi.qimen import compute_qimen_chart, render_qimen_chart  # noqa: F401
from astro.sanshi.taiyi import compute_taiyi_chart, render_taiyi_chart  # noqa: F401
from astro.sanshi.lunming import LunMingAnalyzer  # noqa: F401
from astro.sanshi.qimen_luming import compute_qimen_luming, render_qimen_luming  # noqa: F401
