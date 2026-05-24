# -*- coding: utf-8 -*-
"""
astro/nanji/__init__.py — 南極神數模組公開介面

南極神數（中國五大神數之一）完整 Python 實現。
結合子平八字、五星、二十八宿、建除十二辰與十八星圖，
以 246 條高質量手稿條文為輔助輸出。
"""

from .calculator import (
    NanJiShenShu,
    NanJiResult,
    TiaowenDatabase,
    TiaowenEntry,
    FourPillars,
    DaYunStep,
    calculate_year_pillar,
    calculate_month_pillar,
    calculate_hour_pillar,
    calculate_da_yun,
    get_jianchu_huainan,
    get_xiu_group,
    five_star_appear,
    get_wuxing_relation,
    interpret_chart_1,
    interpret_chart_6,
    interpret_general,
)

# renderer imports streamlit — defer to avoid breaking non-UI imports
def _get_render_streamlit():  # noqa: ANN201
    from .renderer import render_streamlit as _r
    return _r


def render_streamlit(*args, **kwargs):
    """南極神數 Streamlit 渲染入口（延遲載入 streamlit）"""
    return _get_render_streamlit()(*args, **kwargs)


__all__ = [
    "NanJiShenShu",
    "NanJiResult",
    "TiaowenDatabase",
    "TiaowenEntry",
    "FourPillars",
    "DaYunStep",
    "calculate_year_pillar",
    "calculate_month_pillar",
    "calculate_hour_pillar",
    "calculate_da_yun",
    "get_jianchu_huainan",
    "get_xiu_group",
    "five_star_appear",
    "get_wuxing_relation",
    "interpret_chart_1",
    "interpret_chart_6",
    "interpret_general",
    "render_streamlit",
]
