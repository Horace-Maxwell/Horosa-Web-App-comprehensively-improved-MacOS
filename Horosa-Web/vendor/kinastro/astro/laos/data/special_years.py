"""
老撾占星術 (ໄທຣາສາດລາວ) 特殊年份計算模組
Special Years (ອະທິກະ) Analysis Module

包含三種核心特殊年份：
1. ປີອະທິກະສຸຣະທິບ (Adhikasurathib) - 11年週期
2. ປີອະທິກະມາດ (Adhikamat) - 7年週期  
3. ປີອະທິກະອານ (Adhikawan) - 19年週期
"""

from typing import Dict, Any, List
from .constants import SPECIAL_YEAR_CYCLES, BUDDHIST_ERA_OFFSET


def is_adhikasurathib_year(year: int) -> bool:
    """判斷是否為 ປີອະທິກະສຸຣະທິບ (11年週期)"""
    rule = SPECIAL_YEAR_CYCLES["ອະທິກະສຸຣະທິບ"]
    return (year - rule["offset"]) % rule["cycle"] == 0


def is_adhikamat_year(year: int) -> bool:
    """判斷是否為 ປີອະທິກະມາດ (7年週期)"""
    rule = SPECIAL_YEAR_CYCLES["ອະທິກະມາດ"]
    return (year - rule["offset"]) % rule["cycle"] == 0


def is_adhikawan_year(year: int) -> bool:
    """判斷是否為 ປີອະທິກະອານ (19年週期)"""
    rule = SPECIAL_YEAR_CYCLES["ອະທິກະອານ"]
    return (year - rule["offset"]) % rule["cycle"] == 0


def get_special_year_type(lao_year: int) -> Dict[str, Dict[str, Any]]:
    """
    回傳該年的所有特殊年份類型（可同時多種）
    
    Returns:
        {
            "ອະທິກະສຸຣະທິບ": { ... },
            "ອະທິກະມາດ": { ... }
        }
    """
    results: Dict[str, Dict[str, Any]] = {}
    
    for name, rule in SPECIAL_YEAR_CYCLES.items():
        if (lao_year - rule["offset"]) % rule["cycle"] == 0:
            results[name] = {
                **rule,
                "is_special": True,
                "name_zh": {
                    "ອະທິກະສຸຣະທິບ": "阿提卡蘇拉提卜年",
                    "ອະທິກະມາດ": "阿提卡瑪德年",
                    "ອະທິກະອານ": "阿提卡安年"
                }.get(name, name),
                "description_zh": rule.get("description_zh", "")
            }
    
    return results


def is_special_year(lao_year: int) -> bool:
    """快速判斷該年是否為任一特殊年份"""
    return bool(get_special_year_type(lao_year))


def get_lao_year_from_gregorian(gregorian_year: int) -> int:
    """西元年轉老撾佛曆年"""
    return gregorian_year + BUDDHIST_ERA_OFFSET


def get_gregorian_year_from_lao(lao_year: int) -> int:
    """老撾佛曆年轉西元年"""
    return lao_year - BUDDHIST_ERA_OFFSET


def analyze_special_year(year: int, era: str = "lao") -> Dict[str, Any]:
    """
    完整分析特殊年份（推薦在 calculator.py 使用）
    
    Args:
        year: 年份
        era: "lao" (佛曆) 或 "gregorian" (西元年)
    """
    if era == "gregorian":
        lao_year = get_lao_year_from_gregorian(year)
    else:
        lao_year = year

    special = get_special_year_type(lao_year)
    
    special_list_zh: List[str] = [v["name_zh"] for v in special.values()]
    
    return {
        "lao_year": lao_year,
        "gregorian_year": get_gregorian_year_from_lao(lao_year),
        "is_special": bool(special),
        "special_types": special,
        "special_count": len(special),
        "description": "、".join(special.keys()) if special else "普通年份",
        "description_zh": "、".join(special_list_zh) if special_list_zh else "普通年份",
        "influence_note": "特殊年份需特別注意吉凶選擇，建議搭配 ສີກາດ 與 ສັງຄົມ 綜合判斷",
        "influence_note_zh": "特殊年份吉凶影響較大，建議參考 Sikarat 與 Sangkhom 綜合擇日"
    }


# ==================== 公開介面 ====================
__all__ = [
    "is_adhikasurathib_year",
    "is_adhikamat_year",
    "is_adhikawan_year",
    "get_special_year_type",
    "is_special_year",
    "get_lao_year_from_gregorian",
    "get_gregorian_year_from_lao",
    "analyze_special_year",
]


# ==================== 測試 ====================
if __name__ == "__main__":
    test_year = 2026
    lao_year = get_lao_year_from_gregorian(test_year)
    
    print("=== 特殊年份分析測試 ===")
    print(f"西元 {test_year} 年 → 老撾佛曆 {lao_year} 年")
    print(analyze_special_year(test_year, era="gregorian"))
    
    print("\n=== 單項判斷 ===")
    print(f"是否為 ປີອະທິກະສຸຣະທິບ: {is_adhikasurathib_year(lao_year)}")
    print(f"是否為 ປີອະທິກະມາດ: {is_adhikamat_year(lao_year)}")
    
    # 測試多個年份
    for y in range(2024, 2031):
        info = analyze_special_year(y, era="gregorian")
        if info["is_special"]:
            print(f"★ {y} 年 是特殊年份：{info['description_zh']}")
