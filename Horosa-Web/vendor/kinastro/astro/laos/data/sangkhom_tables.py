"""
老撾占星術 (ໄທຣາສາດລາວ) ສັງຄົມ 吉凶擇日表格模組
Sangkhom Activity Auspiciousness Tables

包含結婚、建房、出行、開業、祭祀等常見活動的宜忌表
支援寮國文與中文雙語輸出
"""

from typing import Dict, Any, List, Optional
from datetime import date
from .constants import LAO_WEEKDAYS, get_weekday_name
from .calendar_rules import get_lao_date_info


# ============================================================
# 核心 ສັງຄົມ 宜忌大表（寮國文 + 中文雙語）
# ============================================================

SANGKHOM_TABLES: Dict[str, Dict[str, Dict[str, str]]] = {
    "ການແຕ່ງງານ": {  # 結婚
        "chinese_name": "結婚",
        "0": {"status": "✅ ດີ", "note": "ວັນອາທິດ - ເໝາະສົມທີ່ສຸດ", "note_zh": "星期日 - 最為適合"},
        "1": {"status": "✅ ດີ", "note": "ວັນຈັນ - ໄດ້ຮັບຄວາມສຸກ", "note_zh": "星期一 - 能獲得幸福"},
        "2": {"status": "⚠️ ປານກາງ", "note": "ວັນອັງຄານ - ຕ້ອງລະມັດລະວັງ", "note_zh": "星期二 - 需謹慎"},
        "3": {"status": "❌ ອາດເປັນອຸບັດເຫດ", "note": "ວັນພຸດ - ບໍ່ແນະນຳ", "note_zh": "星期三 - 不建議"},
        "4": {"status": "✅ ດີຫຼາຍ", "note": "ວັນພະຫັດ - ມີໂຊກລາບ", "note_zh": "星期四 - 有吉運"},
        "5": {"status": "✅ ດີ", "note": "ວັນສຸກ - ຄວາມຮັກອົບອຸ່ນ", "note_zh": "星期五 - 愛情溫暖"},
        "6": {"status": "⚠️ ປານກາງ", "note": "ວັນສົບ - ຕ້ອງເບິ່ງເວລາເພີ່ມ", "note_zh": "星期六 - 需額外看時辰"},
    },

    "ການສ້າງເຮືອນ": {  # 建房 / 動土
        "chinese_name": "建房 / 動土",
        "0": {"status": "❌ ອັນຕະລາຍ", "note": "ວັນອາທິດ - ບໍ່ເໝາະ", "note_zh": "星期日 - 不適合"},
        "1": {"status": "✅ ດີຫຼາຍ", "note": "ວັນຈັນ - ມີຄວາມສະຖິດສະຖຽນ", "note_zh": "星期一 - 穩定性佳"},
        "2": {"status": "⚠️ ປານກາງ", "note": "ວັນອັງຄານ - ຕ້ອງຫຼົດຮູບ", "note_zh": "星期二 - 需調整格局"},
        "3": {"status": "✅ ດີ", "note": "ວັນພຸດ - ເໝາະສົມ", "note_zh": "星期三 - 適合"},
        "4": {"status": "❌ ອັນຕະລາຍ", "note": "ວັນພະຫັດ - ບໍ່ແນະນຳ", "note_zh": "星期四 - 不建議"},
        "5": {"status": "✅ ດີ", "note": "ວັນສຸກ - ໄດ້ຮັບຄວາມອຸ່ນອົບ", "note_zh": "星期五 - 獲得溫暖能量"},
        "6": {"status": "✅ ດີຫຼາຍ", "note": "ວັນສົບ - ມີໂຊກລາບ", "note_zh": "星期六 - 有吉運"},
    },

    "ການເດີນທາງ": {  # 出行
        "chinese_name": "出行 / 旅行",
        "0": {"status": "✅ ດີ", "note": "ວັນອາທິດ - ປອດໄພ", "note_zh": "星期日 - 安全"},
        "1": {"status": "❌ ອັນຕະລາຍ", "note": "ວັນຈັນ - ງ່າຍຕິດຂັດ", "note_zh": "星期一 - 容易受阻"},
        "2": {"status": "✅ ດີ", "note": "ວັນອັງຄານ - ສຳເລັດຕາມຄວາມປາຖະໜາ", "note_zh": "星期二 - 容易達成心願"},
        "3": {"status": "⚠️ ປານກາງ", "note": "ວັນພຸດ - ຕ້ອງລະມັດລະວັງ", "note_zh": "星期三 - 需謹慎"},
        "4": {"status": "✅ ດີຫຼາຍ", "note": "ວັນພະຫັດ - ໄດ້ຮັບການຊ່ວຍເຫຼືອ", "note_zh": "星期四 - 獲得幫助"},
        "5": {"status": "✅ ດີ", "note": "ວັນສຸກ - ກັບມາໄດຢ່າງປອດໄພ", "note_zh": "星期五 - 平安歸來"},
        "6": {"status": "❌ ອັນຕະລາຍ", "note": "ວັນສົບ - ງ່າຍເກີດອຸບັດເຫດ", "note_zh": "星期六 - 容易發生意外"},
    },

    "ການເປີດກິຈະການ": {  # 開業
        "chinese_name": "開業 / 開店",
        "0": {"status": "✅ ດີ", "note": "ວັນອາທິດ - ມີກຳໄລ", "note_zh": "星期日 - 有利潤"},
        "1": {"status": "⚠️ ປານກາງ", "note": "ວັນຈັນ - ຕ້ອງເບິ່ງເວລາ", "note_zh": "星期一 - 需看時辰"},
        "2": {"status": "❌ ອັນຕະລາຍ", "note": "ວັນອັງຄານ - ງ່າຍຂາດທຶນ", "note_zh": "星期二 - 容易虧損"},
        "3": {"status": "✅ ດີຫຼາຍ", "note": "ວັນພຸດ - ບໍລິສັດເຕີບໂຕ", "note_zh": "星期三 - 公司成長"},
        "4": {"status": "✅ ດີ", "note": "ວັນພະຫັດ - ມີຄູ່ຮ່ວມງານ", "note_zh": "星期四 - 有合作夥伴"},
        "5": {"status": "✅ ດີ", "note": "ວັນສຸກ - ລູກຄ້າອົບອຸ່ນ", "note_zh": "星期五 - 客戶溫暖"},
        "6": {"status": "⚠️ ປານກາງ", "note": "ວັນສົບ - ຕ້ອງລະມັດລະວັງ", "note_zh": "星期六 - 需謹慎"},
    },

    "ການບູຊາບູຊາ": {  # 祭祀 / 做功德
        "chinese_name": "祭祀 / 做功德",
        "0": {"status": "✅ ດີຫຼາຍ", "note": "ວັນອາທິດ - ຜົນບຸນໃຫຍ່", "note_zh": "星期日 - 功德很大"},
        "1": {"status": "✅ ດີ", "note": "ວັນຈັນ - ເໝາະສົມ", "note_zh": "星期一 - 適合"},
        "2": {"status": "✅ ດີ", "note": "ວັນອັງຄານ - ໄດຮັບການປົກປ້ອງ", "note_zh": "星期二 - 獲得庇佑"},
        "3": {"status": "✅ ດີ", "note": "ວັນພຸດ - ຜົນບຸນເຕັມ", "note_zh": "星期三 - 功德圓滿"},
        "4": {"status": "✅ ດີ", "note": "ວັນພະຫັດ - ເປັນສິ່ງດີ", "note_zh": "星期四 - 是好事"},
        "5": {"status": "✅ ດີຫຼາຍ", "note": "ວັນສຸກ - ບຸນໃຫຍ່", "note_zh": "星期五 - 功德很大"},
        "6": {"status": "✅ ດີ", "note": "ວັນສົບ - ເໝາະສົມ", "note_zh": "星期六 - 適合"},
    },
}


# ==================== 月份補充規則 ====================
SANGKHOM_MONTH_RULES: Dict[int, Dict[str, str]] = {
    1: {"status": "✅ ດີ", "note": "ເດືອນມັງກອນ - ເໝາະກັບການເລີ່ມຕົ້ນ", "note_zh": "一月 - 適合開始新事物"},
    3: {"status": "⚠️ ປານກາງ", "note": "ເດືອນມີນາ - ຕ້ອງລະມັດລະວັງ", "note_zh": "三月 - 需謹慎"},
    5: {"status": "✅ ດີຫຼາຍ", "note": "ເດືອນພຶດສະພາ - ມີໂຊກລາບ", "note_zh": "五月 - 有吉運"},
    7: {"status": "❌ ອັນຕະລາຍ", "note": "ເດືອນກໍລະກົດ - ງ່າຍເກີດບັນຫາ", "note_zh": "七月 - 容易出問題"},
}


def get_sangkhom_for_date(
    activity: str,
    greg_date: date,
    sikarat_level: Optional[str] = None,
    is_special_year_bad: bool = False
) -> Dict[str, Any]:
    """
    根據活動與日期查詢 ສັງຄົມ 吉凶（支援 Sikarat 與特殊年）

    Returns:
        包含寮國文與中文的完整建議
    """
    info = get_lao_date_info(greg_date)
    weekday_num = str(info["weekday_num"])

    activity_data = SANGKHOM_TABLES.get(activity, {})
    if not activity_data:
        return {
            "activity": activity,
            "status": "❓ ບໍ່ມີຂໍ້ມູນ",
            "note": "ບໍ່ພົບກິດຈະກຳນີ້",
            "note_zh": "找不到此活動資料"
        }

    weekday_result = activity_data.get(weekday_num, {
        "status": "❓ ບໍ່ມີຂໍ້ມູນ",
        "note": "ບໍ່ພົບຂໍ້ມູນ ສັງຄົມ",
        "note_zh": "無此星期資料"
    })

    month_result = SANGKHOM_MONTH_RULES.get(info["lao_month"], {
        "status": "✅ ດີ", "note": "ເດືອນທົ່ວໄປ", "note_zh": "一般月份"
    })

    # 簡單調整（可後續擴充）
    final_status = weekday_result["status"]
    if is_special_year_bad and "✅" in final_status:
        final_status = "⚠️ ປານກາງ"

    return {
        "activity": activity,
        "chinese_name": activity_data.get("chinese_name", activity),
        "gregorian_date": greg_date.isoformat(),
        "lao_date": info.get("full_lao_date_with_weekday", ""),
        "weekday": info.get("weekday_lao", ""),
        "status": final_status,
        "note": weekday_result.get("note", ""),
        "note_zh": weekday_result.get("note_zh", ""),
        "month_note": month_result.get("note", ""),
        "month_note_zh": month_result.get("note_zh", ""),
        "recommendation": f"{final_status} - {weekday_result.get('note', '')}",
        "recommendation_zh": f"{final_status} - {weekday_result.get('note_zh', '')}",
        "overall": "✅ ແນະນຳ" if "✅" in final_status else "⚠️ ລະມັດລະວັງ",
        "sikarat_level": sikarat_level,
        "is_special_year_bad": is_special_year_bad
    }


def get_sangkhom_recommendation(activity: str, greg_date: date) -> str:
    """快速取得單一行文字建議（中寮雙語）"""
    result = get_sangkhom_for_date(activity, greg_date)
    return f"{result['chinese_name']}：{result['recommendation']} ({result['lao_date']})"


# ==================== 支援活動清單 ====================
SUPPORTED_SANGKHOM_ACTIVITIES: List[str] = list(SANGKHOM_TABLES.keys())


# ==================== 測試 ====================
if __name__ == "__main__":
    from datetime import date

    test_date = date(2026, 5, 20)
    result = get_sangkhom_for_date("ການແຕ່ງງານ", test_date)
    print(result)

    print("\n中文建議：", get_sangkhom_recommendation("ການແຕ່ງງານ", test_date))
    print("支援活動：", SUPPORTED_SANGKHOM_ACTIVITIES)
