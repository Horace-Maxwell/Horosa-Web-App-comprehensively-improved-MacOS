"""
老撾占星術 (ໄທຣາສາດລາວ) ສີກາດ 時辰／吉凶時段計算模組
Sikarat (ສີກາດ) Time Division Module

ສີກາດ คือ 老撾傳統婆羅門式「色嘎」時段系統，用來判斷一天中各時段的吉凶
支援四種體系：
- ສີກາດລາວ（老撾傳統）
- ສີກາດຝຣັ່ງ（法式）
- ສີກາດຈູລະ（小色嘎）
- ສີກາດມະຫາ（大色嘎）
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from .constants import get_weekday_name


# ============================================================
# ສີກາດ 基礎表格（寮國文 + 中文雙語）
# ============================================================

SIKARAT_PERIODS: Dict[int, Dict[str, Dict[str, str]]] = {
    0: {  # 凌晨～清晨 (00:00-05:59)
        "name_zh": "凌晨時段",
        "ສີກາດລາວ": {"status": "✅ ດີຫຼາຍ", "note": "ເວລາບູຊາ ເໝາະສົມ", "note_zh": "適合供佛、祈福"},
        "ສີກາດຝຣັ່ງ": {"status": "⚠️ ປານກາງ", "note": "ປານກາງ", "note_zh": "普通"},
        "ສີກາດຈູລະ": {"status": "✅ ດີ", "note": "ດີ", "note_zh": "良好"},
        "ສີກາດມະຫາ": {"status": "❌ ອັນຕະລາຍ", "note": "ອັນຕະລາຍ", "note_zh": "危險"},
    },
    1: {  # 上午 (06:00-11:59)
        "name_zh": "上午時段",
        "ສີກາດລາວ": {"status": "✅ ດີ", "note": "ດີ", "note_zh": "良好"},
        "ສີກາດຝຣັ່ງ": {"status": "✅ ດີຫຼາຍ", "note": "ດີຫຼາຍ", "note_zh": "非常良好"},
        "ສີກາດຈູລະ": {"status": "⚠️ ປານກາງ", "note": "ປານກາງ", "note_zh": "普通"},
        "ສີກາດມະຫາ": {"status": "✅ ດີ", "note": "ດີ", "note_zh": "良好"},
    },
    2: {  # 中午 (12:00-17:59)
        "name_zh": "中午至下午時段",
        "ສີກາດລາວ": {"status": "⚠️ ປານກາງ", "note": "ປານກາງ", "note_zh": "普通"},
        "ສີກາດຝຣັ່ງ": {"status": "❌ ອັນຕະລາຍ", "note": "ອັນຕະລາຍ", "note_zh": "危險"},
        "ສີກາດຈູລະ": {"status": "✅ ດີຫຼາຍ", "note": "ດີຫຼາຍ", "note_zh": "非常良好"},
        "ສີກາດມະຫາ": {"status": "✅ ດີ", "note": "ດີ", "note_zh": "良好"},
    },
    3: {  # 晚上 (18:00-23:59)
        "name_zh": "傍晚至夜晚時段",
        "ສີກາດລາວ": {"status": "✅ ດີ", "note": "ດີ", "note_zh": "良好"},
        "ສີກາດຝຣັ່ງ": {"status": "✅ ດີ", "note": "ດີ", "note_zh": "良好"},
        "ສີກາດຈູລະ": {"status": "❌ ອັນຕະລາຍ", "note": "ອັນຕະລາຍ", "note_zh": "危險"},
        "ສີກາດມະຫາ": {"status": "⚠️ ປານກາງ", "note": "ປານກາງ", "note_zh": "普通"},
    },
}


# 每小時對應的 ສີກາດ 類型
SIKARAT_HOUR_TABLE: Dict[int, str] = {
    0: "ສີກາດລາວ", 1: "ສີກາດລາວ", 2: "ສີກາດຝຣັ່ງ",
    3: "ສີກາດຝຣັ່ງ", 4: "ສີກາດຝຣັ່ງ", 5: "ສີກາດຈູລະ",
    6: "ສີກາດຈູລະ", 7: "ສີກາດມະຫາ", 8: "ສີກາດມະຫາ",
    9: "ສີກາດລາວ", 10: "ສີກາດລາວ", 11: "ສີກາດຝຣັ່ງ",
    12: "ສີກາດຝຣັ່ງ", 13: "ສີກາດຈູລະ", 14: "ສີກາດຈູລະ",
    15: "ສີກາດມະຫາ", 16: "ສີກາດມະຫາ", 17: "ສີກາດລາວ",
    18: "ສີກາດລາວ", 19: "ສີກາດຝຣັ່ງ", 20: "ສີກາດຝຣັ່ງ",
    21: "ສີກາດຈູລະ", 22: "ສີກາດຈູລະ", 23: "ສີກາດມະຫາ",
}


def get_sikarat_by_hour(
    hour: int, 
    sikarat_type: str = "ສີກາດລາວ"
) -> Dict[str, Any]:
    """
    根據小時取得該時段的 ສີກາດ 吉凶資訊（雙語）

    Args:
        hour: 0-23
        sikarat_type: ສີກາດລາວ / ສີກາດຝຣັ່ງ / ສີກາດຈູລະ / ສີກາດມະຫາ
    """
    if not 0 <= hour <= 23:
        raise ValueError("小時必須在 0-23 之間")

    period_index = (hour // 6) % 4
    period_data = SIKARAT_PERIODS.get(period_index, {})
    type_data = period_data.get(sikarat_type, {})

    return {
        "hour": hour,
        "period_name": period_data.get("name_zh", "未知時段"),
        "sikarat_type": sikarat_type,
        "status": type_data.get("status", "❓ ບໍ່ມີຂໍ້ມູນ"),
        "note": type_data.get("note", ""),
        "note_zh": type_data.get("note_zh", ""),
        "recommendation": f"{type_data.get('status', '')} - {type_data.get('note', '')}",
        "recommendation_zh": f"{type_data.get('status', '')} - {type_data.get('note_zh', '')}"
    }


def get_sikarat_for_datetime(
    dt: datetime, 
    sikarat_type: str = "ສີກາດລາວ"
) -> Dict[str, Any]:
    """
    根據完整 datetime 取得 ສີກາດ 資訊（推薦在 calculator.py 使用）
    """
    sikarat_info = get_sikarat_by_hour(dt.hour, sikarat_type)

    return {
        "gregorian_time": dt.isoformat(),
        "hour": dt.hour,
        "minute": dt.minute,
        "weekday": get_weekday_name(dt.weekday()),
        "period_name": sikarat_info["period_name"],
        "sikarat_type": sikarat_type,
        "status": sikarat_info["status"],
        "note": sikarat_info["note"],
        "note_zh": sikarat_info["note_zh"],
        "recommendation": sikarat_info["recommendation"],
        "recommendation_zh": sikarat_info["recommendation_zh"]
    }


def get_best_sikarat_hours(
    sikarat_type: str = "ສີກາດລາວ",
    limit: int = 6
) -> List[Dict[str, Any]]:
    """
    取得當日較佳的 ສີກາດ 時段（雙語）
    """
    good_hours = []
    for h in range(24):
        result = get_sikarat_by_hour(h, sikarat_type)
        if "✅" in result["status"]:
            good_hours.append({
                "hour": f"{h:02d}:00",
                "status": result["status"],
                "note": result["note"],
                "note_zh": result["note_zh"]
            })
    return good_hours[:limit]


def get_sikarat_summary(dt: datetime) -> Dict[str, Any]:
    """快速取得四種 ສີກາດ 體系的比較摘要"""
    summary = {}
    for stype in ["ສີກາດລາວ", "ສີກາດຝຣັ່ງ", "ສີກາດຈູລະ", "ສີກາດມະຫາ"]:
        info = get_sikarat_by_hour(dt.hour, stype)
        summary[stype] = {
            "status": info["status"],
            "note_zh": info["note_zh"]
        }
    return summary


# ==================== 公開介面 ====================
__all__ = [
    "SIKARAT_PERIODS",
    "SIKARAT_HOUR_TABLE",
    "get_sikarat_by_hour",
    "get_sikarat_for_datetime",
    "get_best_sikarat_hours",
    "get_sikarat_summary",
]


# ==================== 測試 ====================
if __name__ == "__main__":
    from datetime import datetime

    now = datetime.now()
    print("=== 當前 ສີກາດ 時段 ===")
    print(get_sikarat_for_datetime(now))

    print("\n=== 四種體系比較 ===")
    print(get_sikarat_summary(now))

    print("\n今日較佳時段：")
    for item in get_best_sikarat_hours(limit=5):
        print(item)
