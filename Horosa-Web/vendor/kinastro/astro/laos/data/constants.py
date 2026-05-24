# astro/lao/data/constants.py
"""
老撾占星術 (ໄທຣາສາດລາວ) 基礎常數表
嚴格對應書中 ວັນ・ເດືອນ・ປີ・ສີກາດ 章節

雙語設計：所有公開常數同時提供寮國文（Lao script）與中文對照。
- LAO_WEEKDAYS / LAO_WEEKDAYS_ZH
- LAO_MONTHS   / LAO_MONTHS_ZH
- LAO_SEASONS  / LAO_SEASONS_ZH
"""

from typing import Dict

# ==================== 1. 星期 (ວັນ) ====================
# 書中第1章 ວັນ，0=週日（依 Python weekday() 約定，週日為 0）
LAO_WEEKDAYS: Dict[int, str] = {
    0: "ວັນອາທິດ",      # Sunday
    1: "ວັນຈັນ",        # Monday
    2: "ວັນອັງຄານ",     # Tuesday
    3: "ວັນພຸດ",        # Wednesday
    4: "ວັນພະຫັດ",      # Thursday
    5: "ວັນສຸກ",        # Friday
    6: "ວັນສົບ",        # Saturday
}

# 中文星期對照（與 LAO_WEEKDAYS 索引相同）
LAO_WEEKDAYS_ZH: Dict[int, str] = {
    0: "星期日",
    1: "星期一",
    2: "星期二",
    3: "星期三",
    4: "星期四",
    5: "星期五",
    6: "星期六",
}

LAO_WEEKDAYS_SHORT: Dict[int, str] = {
    0: "ອາ.", 1: "ຈ.", 2: "ອ.", 3: "ພ.", 4: "ພຫ.", 5: "ສຸ.", 6: "ສົບ."
}

# ==================== 2. 月份 (ເດືອນ) ====================
LAO_MONTHS: Dict[int, str] = {
    1:  "ເດືອນມັງກອນ",    # January
    2:  "ເດືອນກຸມພາ",     # February
    3:  "ເດືອນມີນາ",      # March
    4:  "ເດືອນເມສາ",      # April
    5:  "ເດືອນພຶດສະພາ",   # May
    6:  "ເດືອນມິຖຸນາ",    # June
    7:  "ເດືອນກໍລະກົດ",   # July
    8:  "ເດືອນສິງຫາ",     # August
    9:  "ເດືອນກັນຍາ",     # September
    10: "ເດືອນຕຸລາ",      # October
    11: "ເດືອນພະຈິກ",     # November
    12: "ເດືອນທັນວາ",     # December
}

# 中文月份對照
LAO_MONTHS_ZH: Dict[int, str] = {
    1: "一月", 2: "二月", 3: "三月", 4: "四月",
    5: "五月", 6: "六月", 7: "七月", 8: "八月",
    9: "九月", 10: "十月", 11: "十一月", 12: "十二月",
}

# ==================== 3. 季節 (ລະດູ) ====================
# 書中三季：冷季（ລະດູໜາວ）、雨季（ລະດູຝົນ）、旱季（ລະດູແຫ້ງ）
LAO_SEASONS: Dict[int, str] = {
    1: "ລະດູໜາວ",    # 冷季 (11–2月)
    2: "ລະດູຝົນ",    # 雨季 (5–10月)
    3: "ລະດູແຫ້ງ",   # 旱季 (3–4月)
}

# 中文季節對照（key 與 LAO_SEASONS 相同）
LAO_SEASONS_ZH: Dict[int, str] = {
    1: "冷季（11–2月）",
    2: "雨季（5–10月）",
    3: "旱季（3–4月）",
}

# Lao 文字 → 中文反查（供 renderer 快速翻譯）
LAO_SEASON_NAME_ZH: Dict[str, str] = {
    v: LAO_SEASONS_ZH[k] for k, v in LAO_SEASONS.items()
}

# ==================== 4. 特殊年份規則 (ປີອະທິກະ...) ====================
SPECIAL_YEAR_CYCLES = {
    "ອະທິກະສຸຣະທິບ": {          # Adhikasurathib
        "cycle": 11,
        "offset": 0,
        "description": "ປີເພີ່ມສຸຣະທິບ (11 ປີມີ 1 ປີ)"
    },
    "ອະທິກະມາດ": {              # Adhikamat
        "cycle": 7,
        "offset": 2,
        "description": "ປີເພີ່ມມາດ (7 ປີມີ 1 ປີ)"
    },
    "ອະທິກະອານ": {               # Adhikawan
        "cycle": 19,
        "offset": 5,
        "description": "ປີເພີ່ມອານ (19 ປີມີ 1 ປີ)"
    },
}

BUDDHIST_ERA_OFFSET = 543   # ພ.ສ. = ค.ศ. + 543 (老撾/泰國佛曆)

# ==================== 5. 色嘎週期 (ສີກາດ) ====================
SIKARAT_CYCLE = [
    # 書中第36頁完整色嘎表（簡化為常用值，可後續擴充）
    "ສີກາດລາວ", "ສີກາດຝຣັ່ງ", "ສີກາດຈູລະ", "ສີກາດມະຫາ"
]

SIKARAT_NAMES = {
    0: "ສີກາດລາວ",
    1: "ສີກາດຝຣັ່ງ",
    2: "ສີກາດຈູລະ",
    3: "ສີກາດມະຫາ",
}

# ==================== 6. 其他核心常數 ====================
LAO_CALENDAR_RULES = {
    "default_era": "ພ.ສ.",           # 佛曆
    "gregorian_offset": -543,
    "days_in_month": [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
    "leap_month_rule": "ອະທິກະມາດ",   # 閏月規則
}

# ==================== 7. 符號與顯示 ====================
LAO_ASTRO_EMOJIS = {
    "sun": "☀️",
    "moon": "🌕",
    "planet": "🪐",
    "wheel": "🌀",
    "good": "✅",
    "bad": "❌",
}

# ==================== 工具函數 ====================
def get_weekday_name(day: int, short: bool = False, lang: str = "lao") -> str:
    """取得星期名稱。

    Args:
        day:   Python weekday() 值（0=週日 … 6=週六）。
        short: 是否使用縮寫（僅 Lao 文）。
        lang:  ``"lao"``（預設）或 ``"zh"``。
    """
    idx = day % 7
    if lang == "zh":
        return LAO_WEEKDAYS_ZH.get(idx, "未知")
    if short:
        return LAO_WEEKDAYS_SHORT.get(idx, "未知")
    return LAO_WEEKDAYS.get(idx, "未知")


def get_month_name(month: int, lang: str = "lao") -> str:
    """取得月份名稱。

    Args:
        month: 1–12。
        lang:  ``"lao"``（預設）或 ``"zh"``。
    """
    if lang == "zh":
        return LAO_MONTHS_ZH.get(month, f"{month}月")
    return LAO_MONTHS.get(month, f"ເດືອນ{month}")


def get_season(month: int, lang: str = "lao") -> str:
    """依格里曆月份回傳季節名稱。"""
    if month in (11, 12, 1, 2):
        key = 1
    elif month in (5, 6, 7, 8, 9, 10):
        key = 2
    else:
        key = 3
    if lang == "zh":
        return LAO_SEASONS_ZH.get(key, "未知季節")
    return LAO_SEASONS.get(key, "未知")


def is_special_year(year: int) -> dict:
    """判斷是否為特殊年份（傳入老撾佛曆年）。"""
    results = {}
    for name, rule in SPECIAL_YEAR_CYCLES.items():
        if (year - rule["offset"]) % rule["cycle"] == 0:
            results[name] = rule
    return results


# ==================== 公開介面 ====================
__all__ = [
    "LAO_WEEKDAYS", "LAO_WEEKDAYS_ZH", "LAO_WEEKDAYS_SHORT",
    "LAO_MONTHS",   "LAO_MONTHS_ZH",
    "LAO_SEASONS",  "LAO_SEASONS_ZH",  "LAO_SEASON_NAME_ZH",
    "SPECIAL_YEAR_CYCLES", "BUDDHIST_ERA_OFFSET",
    "SIKARAT_CYCLE", "SIKARAT_NAMES",
    "LAO_CALENDAR_RULES", "LAO_ASTRO_EMOJIS",
    "get_weekday_name", "get_month_name", "get_season", "is_special_year",
]
