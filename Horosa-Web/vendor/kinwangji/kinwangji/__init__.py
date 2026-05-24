# -*- coding: utf-8 -*-
"""
kinwangji — 皇極經世 (Huangji Jingshi) Python implementation.

Implements Shao Yong's yuan-hui-yun-shi cycles and 24 solar terms calculation.
"""

from .wanji import (
    wanji_four_gua,
    display_pan,
    gangzhi,
    lunar_date_d,
    jiazi,
)

from .jieqi import (
    jq,
    gong_wangzhuai,
    get_jieqi_start_date,
    get_next_jieqi_start_date,
)

from .history import load_history, history_for_year

from .classics import list_classics, load_classic, get_sections

from .xinyi import (
    number_qigua,
    datetime_qigua,
    direction_qigua,
    character_qigua,
)

__all__ = [
    "wanji_four_gua",
    "display_pan",
    "gangzhi",
    "lunar_date_d",
    "jiazi",
    "jq",
    "gong_wangzhuai",
    "get_jieqi_start_date",
    "get_next_jieqi_start_date",
    "load_history",
    "history_for_year",
    "list_classics",
    "load_classic",
    "get_sections",
    "number_qigua",
    "datetime_qigua",
    "direction_qigua",
    "character_qigua",
]
