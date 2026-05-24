"""
老撾占星術 (ໄທຣາສາດລາວ) 統一資料載入器
Lao Astrology Data Loader

負責集中載入所有傳統資料表（Sangkhom、Sikarat、特殊年份、常數等）
支援 JSON 與 Python dict 兩種來源，方便後續維護與擴充
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache

# 專案根目錄下的 data 資料夾
DATA_DIR = Path(__file__).parent


@lru_cache(maxsize=32)
def load_json(filename: str) -> Dict[str, Any]:
    """從 JSON 檔案載入資料"""
    file_path = DATA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"資料檔案不存在: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_sangkhom_data() -> Dict[str, Any]:
    """取得 Sangkhom 活動吉凶表"""
    try:
        return load_json("sangkhom_tables.json")
    except FileNotFoundError:
        # 如果沒有 JSON，則從 sangkhom_tables.py 匯入
        from .sangkhom_tables import SANGKHOM_DATA
        return SANGKHOM_DATA


def get_sikarat_data() -> Dict[str, Any]:
    """取得 Sikarat 時段資料"""
    try:
        return load_json("sikarat.json")
    except FileNotFoundError:
        from .sikarat import SIKARAT_PERIODS, SIKARAT_HOUR_TABLE
        return {
            "periods": SIKARAT_PERIODS,
            "hour_table": SIKARAT_HOUR_TABLE,
            "metadata": {
                "version": "1.0",
                "description": "老撾傳統 ສີກາດ 時段系統"
            }
        }


def get_special_years_data() -> Dict[str, Any]:
    """取得特殊年份規則"""
    try:
        return load_json("special_years.json")
    except FileNotFoundError:
        from .special_years import SPECIAL_YEAR_CYCLES
        return {
            "cycles": SPECIAL_YEAR_CYCLES,
            "metadata": {
                "version": "1.0",
                "description": "老撾占星特殊年份週期"
            }
        }


def get_calendar_constants() -> Dict[str, Any]:
    """取得曆法相關常數"""
    try:
        return load_json("calendar_constants.json")
    except FileNotFoundError:
        from .constants import (
            LAO_WEEKDAYS, LAO_MONTHS, LAO_SEASONS,
            BUDDHIST_ERA_OFFSET, LAO_CALENDAR_RULES
        )
        return {
            "weekdays": LAO_WEEKDAYS,
            "months": LAO_MONTHS,
            "seasons": LAO_SEASONS,
            "buddhist_era_offset": BUDDHIST_ERA_OFFSET,
            "calendar_rules": LAO_CALENDAR_RULES,
        }


@lru_cache(maxsize=16)
def get_all_data() -> Dict[str, Any]:
    """
    一次性取得所有資料（推薦在應用程式啟動時呼叫）
    """
    return {
        "sangkhom": get_sangkhom_data(),
        "sikarat": get_sikarat_data(),
        "special_years": get_special_years_data(),
        "calendar": get_calendar_constants(),
        "metadata": {
            "version": "1.0",
            "source": "ໂຫຣາສາດລາວ",
            "last_updated": "2026-05-20",
            "description": "老撾占星統一資料集"
        }
    }


def reload_all_data() -> None:
    """清除快取並重新載入所有資料（開發或更新資料時使用）。"""
    get_all_data.cache_clear()
    load_json.cache_clear()
    print("✅ 所有老撾占星資料已重新載入")


# ==================== 便捷函數 ====================

def get_supported_activities() -> list:
    """取得所有支援的 Sangkhom 活動"""
    data = get_sangkhom_data()
    return list(data.get("activities", {}).keys())


def get_sikarat_types() -> list:
    """取得支援的 Sikarat 體系"""
    return ["ສີກາດລາວ", "ສີກາດຝຣັ່ງ", "ສີກາດຈູລະ", "ສີກາດມະຫາ"]


# ==================== 測試與開發用 ====================
if __name__ == "__main__":
    print("=== 老撾占星資料載入測試 ===")
    all_data = get_all_data()
    
    print(f"✅ Sangkhom 活動數量: {len(all_data['sangkhom'].get('activities', {}))}")
    print(f"✅ Sikarat 時段數量: {len(all_data['sikarat'].get('hour_table', {}))}")
    print(f"✅ 特殊年份週期數量: {len(all_data['special_years'].get('cycles', {}))}")
    
    print("\n=== 範例輸出 ===")
    from datetime import date
    from .calendar_rules import get_lao_date_info
    
    today_info = get_lao_date_info(date.today())
    print(f"今日: {today_info.get('full_lao_date_with_weekday_zh', '')}")
    
    print("\n支援活動預覽:", get_supported_activities()[:5])
