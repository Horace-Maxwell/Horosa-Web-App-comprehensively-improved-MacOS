"""
七政四餘金融股票占星子模組 (Stock Astrology Sub-module for Seven Governors)

提供股票靈運占星儀功能：
- 以上市日期/時間作為「出生盤」排盤
- yfinance 股票資料擷取（名稱、股價、52週高低）
- 流日流時吉凶分析
- 股價比例強弱度
- AI 七政四餘語調解讀
"""

from .stock_fetcher import fetch_stock_info, StockInfo
from .stock_calculator import compute_stock_chart, StockChartData
from .stock_renderer import render_stock_fortune_tab
from .gann_macro_stock import (
    GANN_NATAL_DEFAULT,
    GANN_NATAL_PRESETS,
    GANN_NATAL_REFERENCE_PRICES,
    build_gann_macro_timing,
    build_gann_macro_with_dasha_context,
    build_gann_full_confluence,
    compute_biblical_cycle_dates,
    find_nearest_square_of_nine_levels,
    compute_square_of_nine_levels,
    compute_time_price_squaring,
    compute_gann_angles,
    get_gann_angle_at_date,
    compute_natural_squares_vibration,
    compute_solar_ingress_gann_confluence,
)

__all__ = [
    "fetch_stock_info",
    "StockInfo",
    "compute_stock_chart",
    "StockChartData",
    "render_stock_fortune_tab",
    "GANN_NATAL_DEFAULT",
    "GANN_NATAL_PRESETS",
    "GANN_NATAL_REFERENCE_PRICES",
    "build_gann_macro_timing",
    "build_gann_macro_with_dasha_context",
    "build_gann_full_confluence",
    "compute_biblical_cycle_dates",
    "find_nearest_square_of_nine_levels",
    "compute_square_of_nine_levels",
    "compute_time_price_squaring",
    "compute_gann_angles",
    "get_gann_angle_at_date",
    "compute_natural_squares_vibration",
    "compute_solar_ingress_gann_confluence",
]
