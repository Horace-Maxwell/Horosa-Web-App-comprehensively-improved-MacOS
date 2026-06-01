"""
老撾占星術 (ໄທຣາສາດລາວ) 曆法轉換規則模組
Lao Calendar Rules Module

負責西曆 ↔ 老撾佛曆的轉換、星期、月份、季節、特殊年份等完整資訊提取。
所有回傳 dict 均包含 ``_zh`` 欄位供中文前端直接使用。
"""

from datetime import date
from typing import Any, Dict, Optional

from .constants import (
    BUDDHIST_ERA_OFFSET,
    LAO_CALENDAR_RULES,
    LAO_MONTHS,
    LAO_MONTHS_ZH,
    LAO_SEASONS,
    LAO_SEASONS_ZH,
    LAO_WEEKDAYS,
    LAO_WEEKDAYS_ZH,
    get_month_name,
    get_season,
    get_weekday_name,
)
from .special_years import analyze_special_year, get_lao_year_from_gregorian


def gregorian_to_lao(greg_date: date) -> Dict[str, Any]:
    """將西曆日期轉換為老撾傳統日期資訊（核心函數）。

    回傳 dict 包含 Lao 文字欄位與對應 ``_zh`` 中文欄位。
    """
    lao_year = get_lao_year_from_gregorian(greg_date.year)
    month = greg_date.month
    day = greg_date.day
    weekday_num = greg_date.weekday()

    # 季節判斷（依傳統老撾占星三季）
    if month in (11, 12, 1, 2):
        season_key = 1
    elif month in (5, 6, 7, 8, 9, 10):
        season_key = 2
    else:
        season_key = 3

    season_lao = LAO_SEASONS[season_key]
    season_zh = LAO_SEASONS_ZH[season_key]

    weekday_lao = LAO_WEEKDAYS.get(weekday_num, "ວັນອາທິດ")
    weekday_zh = LAO_WEEKDAYS_ZH.get(weekday_num, "星期日")
    month_lao = LAO_MONTHS.get(month, f"ເດືອນ{month}")
    month_zh = LAO_MONTHS_ZH.get(month, f"{month}月")

    special_info = analyze_special_year(lao_year, era="lao")

    return {
        "gregorian_date": greg_date.isoformat(),
        "lao_year": lao_year,
        "lao_year_display": f"ພ.ສ. {lao_year}",
        "lao_year_display_zh": f"佛曆 {lao_year} 年",
        "lao_month": month,
        "lao_month_name": month_lao,
        "lao_month_name_zh": month_zh,
        "lao_day": day,
        "weekday_num": weekday_num,
        "weekday_lao": weekday_lao,
        "weekday_lao_short": get_weekday_name(weekday_num, short=True),
        "weekday_zh": weekday_zh,
        "season": season_lao,
        "season_zh": season_zh,
        "is_special_year": special_info.get("is_special", False),
        "special_types": special_info.get("special_types", {}),
        "full_lao_date": f"{day} {month_lao} ພ.ສ. {lao_year}",
        "full_lao_date_zh": f"佛曆 {lao_year} 年 {month_zh} {day} 日",
        "full_lao_date_with_weekday": (
            f"{weekday_lao} {day} {month_lao} ພ.ສ. {lao_year}"
        ),
        "full_lao_date_with_weekday_zh": (
            f"{weekday_zh} {month_zh} {day} 日 佛曆 {lao_year} 年"
        ),
    }


def lao_to_gregorian(lao_year: int, lao_month: int, lao_day: int) -> Optional[date]:
    """老撾佛曆日期轉西曆日期（簡化版）。"""
    try:
        greg_year = lao_year - BUDDHIST_ERA_OFFSET
        return date(greg_year, lao_month, lao_day)
    except ValueError:
        return None


def get_lao_date_info(greg_date: date) -> Dict[str, Any]:
    """取得老撾日期的完整占星資訊（推薦在 calculator.py 中呼叫）。

    包含日期、星期、月份、季節、特殊年份等，以及對應中文欄位。
    """
    base_info = gregorian_to_lao(greg_date)

    return {
        **base_info,
        "calendar_type": "ໄທຣາສາດລາວ",
        "calendar_type_zh": "老撾占星曆",
        "era": LAO_CALENDAR_RULES.get("default_era", "ພ.ສ."),
        "era_zh": "佛曆",
    }


def is_valid_lao_date(lao_year: int, lao_month: int, lao_day: int) -> bool:
    """驗證老撾日期是否合法。"""
    if not (1 <= lao_month <= 12):
        return False
    if not (1 <= lao_day <= 31):
        return False
    try:
        return lao_to_gregorian(lao_year, lao_month, lao_day) is not None
    except Exception:
        return False


def get_current_season(greg_date: date) -> Dict[str, str]:
    """單獨取得季節資訊（含中文）。"""
    month = greg_date.month
    if month in (11, 12, 1, 2):
        key = 1
    elif month in (5, 6, 7, 8, 9, 10):
        key = 2
    else:
        key = 3
    return {"lao": LAO_SEASONS[key], "zh": LAO_SEASONS_ZH[key]}


# ==================== 測試與開發用 ====================
if __name__ == "__main__":
    today = date.today()
    info = get_lao_date_info(today)

    print("=== 今日老撾占星日期資訊 ===")
    print(f"西曆日期     : {info['gregorian_date']}")
    print(f"老撾佛曆     : {info['full_lao_date_with_weekday']}")
    print(f"中文顯示     : {info['full_lao_date_with_weekday_zh']}")
    print(f"季節         : {info['season']} ({info['season_zh']})")
    print(f"是否特殊年份 : {'是' if info['is_special_year'] else '否'}")
    if info["special_types"]:
        print(f"特殊類型     : {info['special_types']}")

    print("\n=== 其他日期測試 ===")
    test_date = date(2026, 5, 20)
    print(get_lao_date_info(test_date)["full_lao_date_with_weekday_zh"])
