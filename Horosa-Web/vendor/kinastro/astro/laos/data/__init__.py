# astro/lao/data/__init__.py
"""
老撾占星術 (ໄທຣາສາດລາວ) 數據模組
使用方式：
    from astro.lao.data import (
        LAO_WEEKDAYS,
        SPECIAL_YEAR_CYCLES,
        SANGKHOM_TABLES,
        SIKARAT_CYCLE,
        # ... 其他常數
    )
"""

from .constants import *
from .special_years import *
from .calendar_rules import *
from .sangkhom_tables import *
from .sikarat import *
from .symbols import *

# 公開所有重要名稱，方便 from astro.lao.data import * 使用
__all__ = [
    # constants.py
    "LAO_WEEKDAYS",
    "LAO_MONTHS",
    "LAO_SEASONS",
    "SIKARAT_CYCLE",
    "SPECIAL_YEAR_CYCLES",
    "BUDDHIST_ERA_OFFSET",
    "LAO_CALENDAR_RULES",

    # special_years.py
    "is_adhikamas_year",
    "is_adhikawan_year",
    "is_adhikara_year",
    "get_special_year_type",

    # calendar_rules.py
    "lao_to_gregorian",
    "gregorian_to_lao",
    "get_lao_date_info",

    # sangkhom_tables.py
    "SANGKHOM_TABLES",
    "get_sangkhom_for_date",
    "get_sangkhom_recommendation",

    # sikarat.py
    "get_sikarat_period",
    "SIKARAT_NAMES",

    # symbols.py
    "LAO_ZODIAC_SYMBOLS",
    "BRAHMAN_WHEEL_SYMBOLS",
    "LAO_ASTRO_EMOJIS",
]

__version__ = "1.0.0"
__description__ = "老撾傳統婆羅門占星完整數據表與規則"

# 方便一次性載入所有資料
def load_all_data():
    """一次性載入所有老撾占星數據（供測試與初始化使用）"""
    return {
        "weekdays": LAO_WEEKDAYS,
        "months": LAO_MONTHS,
        "special_years": SPECIAL_YEAR_CYCLES,
        "sangkhom": SANGKHOM_TABLES,
        "sikarat": SIKARAT_CYCLE,
        "symbols": BRAHMAN_WHEEL_SYMBOLS,
    }
