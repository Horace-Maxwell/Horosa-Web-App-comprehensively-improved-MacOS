#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算盤打數完整結構模組 (suanpan_full_structure.py)
================================================
曹展碩實務版「鐵板算盤數」— 金鎖銀匙歌 + 算盤打數 + 五部條文

主要功能：
1. 金鎖銀匙歌 + 算盤打數（千百十零）
2. 五部（水火木金土）條文資料庫（延遲載入）
3. 大運、流年計算框架
4. 與 kunji_full_structure.py 共用工具函式，設計模式一致

本檔案與 kunji_full_structure.py 互補：
- kunji  = 扣入法 + 坤集密碼表（江靜川版）
- suanpan = 算盤打數 + 金鎖銀匙歌（曹展碩實務版）
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


# ====================== 1. 常數定義 ======================

class SuanpanDepartment(str, Enum):
    """五部歸屬（由納音決定）"""
    WATER = "水"
    FIRE  = "火"
    WOOD  = "木"
    GOLD  = "金"
    EARTH = "土"


class SuanpanGender(str, Enum):
    """命宮性別類型"""
    MALE   = "男命"
    FEMALE = "女命"
    SUIYUN = "歲運"   # 流年 / 大運查詢

    @classmethod
    def from_str(cls, s: str) -> "SuanpanGender":
        if s in ("男", "男命"):
            return cls.MALE
        if s in ("女", "女命"):
            return cls.FEMALE
        if s in ("歲運", "大運", "流年"):
            return cls.SUIYUN
        return cls.MALE


# ====================== 2. 金鎖銀匙歌核心數表 ======================

# 算盤打數基底（千位起始）
BASE_NUMBER: int = 2000

# 歲君加數（根據納音五行，各部加數不同）
SUIJUN_ADD: Dict[str, int] = {
    "水": 27,
    "火": 27,
    "木": 0,
    "金": 0,
    "土": 50,
}

# 納音配數（1水 2火 3木 4金 5土，供算盤打數定部用）
NAYIN_ADD: Dict[str, int] = {
    "水": 1,
    "火": 2,
    "木": 3,
    "金": 4,
    "土": 5,
}
# 向後相容別名
NAYIN_ELEMENT_ADD = NAYIN_ADD

# 天干數值（用於算盤打數）
STEM_VALUES: Dict[str, int] = {
    "甲": 1, "乙": 2, "丙": 3, "丁": 4, "戊": 5,
    "己": 6, "庚": 7, "辛": 8, "壬": 9, "癸": 0,
}

# 地支數值（用於算盤打數）
BRANCH_VALUES: Dict[str, int] = {
    "子": 1,  "丑": 2,  "寅": 3,  "卯": 4,
    "辰": 5,  "巳": 6,  "午": 7,  "未": 8,
    "申": 9,  "酉": 10, "戌": 11, "亥": 12,
}

# 六十納音對應五行（用於定部）
NAYIN_TO_ELEMENT: Dict[str, str] = {
    # 金
    "海中金": "金", "劍鋒金": "金", "白蠟金": "金",
    "砂中金": "金", "金箔金": "金", "釵釧金": "金",
    # 木
    "大林木": "木", "楊柳木": "木", "松柏木": "木",
    "平地木": "木", "桑柘木": "木", "石榴木": "木",
    # 水
    "澗下水": "水", "泉中水": "水", "長流水": "水",
    "天河水": "水", "大溪水": "水", "大海水": "水",
    # 火
    "爐中火": "火", "山頭火": "火", "霹靂火": "火",
    "山下火": "火", "覆燈火": "火", "天上火": "火",
    # 土
    "路旁土": "土", "城頭土": "土", "屋上土": "土",
    "壁上土": "土", "大驛土": "土", "砂中土": "土",
}

# 六十納音完整表（干支 → 納音）
NAYIN_TABLE: Dict[str, str] = {
    "甲子": "海中金", "乙丑": "海中金",
    "丙寅": "爐中火", "丁卯": "爐中火",
    "戊辰": "大林木", "己巳": "大林木",
    "庚午": "路旁土", "辛未": "路旁土",
    "壬申": "劍鋒金", "癸酉": "劍鋒金",
    "甲戌": "山頭火", "乙亥": "山頭火",
    "丙子": "澗下水", "丁丑": "澗下水",
    "戊寅": "城頭土", "己卯": "城頭土",
    "庚辰": "白蠟金", "辛巳": "白蠟金",
    "壬午": "楊柳木", "癸未": "楊柳木",
    "甲申": "泉中水", "乙酉": "泉中水",
    "丙戌": "屋上土", "丁亥": "屋上土",
    "戊子": "霹靂火", "己丑": "霹靂火",
    "庚寅": "松柏木", "辛卯": "松柏木",
    "壬辰": "長流水", "癸巳": "長流水",
    "甲午": "砂中金", "乙未": "砂中金",
    "丙申": "山下火", "丁酉": "山下火",
    "戊戌": "平地木", "己亥": "平地木",
    "庚子": "壁上土", "辛丑": "壁上土",
    "壬寅": "金箔金", "癸卯": "金箔金",
    "甲辰": "覆燈火", "乙巳": "覆燈火",
    "丙午": "天河水", "丁未": "天河水",
    "戊申": "大驛土", "己酉": "大驛土",
    "庚戌": "釵釧金", "辛亥": "釵釧金",
    "壬子": "桑柘木", "癸丑": "桑柘木",
    "甲寅": "大溪水", "乙卯": "大溪水",
    "丙辰": "砂中土", "丁巳": "砂中土",
    "戊午": "天上火", "己未": "天上火",
    "庚申": "石榴木", "辛酉": "石榴木",
    "壬戌": "大海水", "癸亥": "大海水",
}


# ====================== 3. 資料類別 ======================

@dataclass
class SuanpanResult:
    """算盤打數推算結果"""
    # 輸入資料
    year_gz: str
    month_gz: str
    day_gz: str
    hour_gz: str
    gender: str

    # 納音與五行
    nayin: str = ""
    department: str = ""          # 水 / 火 / 木 / 金 / 土

    # 算盤打數過程
    stem_sum: int = 0             # 天干數合計
    branch_sum: int = 0           # 地支數合計
    suijun_add: int = 0           # 歲君加數
    total_number: int = 0         # 算盤總數

    # 定位條文
    tiaowen_key: str = ""         # 條文編號（字串鍵）
    tiaowen: Optional[Dict[str, Any]] = None   # 完整條文資料

    # 大運相關
    dayun_number: Optional[int] = None
    dayun_tiaowen: Optional[Dict[str, Any]] = None

    # 備注
    note: str = ""
    calculation_steps: List[str] = field(default_factory=list)


# ====================== 4. 核心計算函式 ======================

def get_nayin(year_gz: str) -> str:
    """
    查詢年柱納音（用於定部）

    Parameters
    ----------
    year_gz : str
        年柱干支，如「壬辰」

    Returns
    -------
    str
        納音名稱，如「長流水」；找不到時返回空字串
    """
    return NAYIN_TABLE.get(year_gz, "")


def get_nayin_element(nayin: str) -> str:
    """
    從納音名稱取得五行屬性（用於定部）

    Parameters
    ----------
    nayin : str
        納音名稱，如「長流水」

    Returns
    -------
    str
        五行屬性：水 / 火 / 木 / 金 / 土；找不到時返回空字串
    """
    return NAYIN_TO_ELEMENT.get(nayin, "")


def suanpan_calculate(
    year_gz: str,
    month_gz: str,
    day_gz: str,
    hour_gz: str,
    gender: str = "男",
    is_dayun: bool = False,
    dayun_offset: int = 0,
) -> SuanpanResult:
    """
    鐵板算盤數核心計算函式（金鎖銀匙歌）

    計算流程（曹展碩實務版）：
    1. 年柱納音定部（水/火/木/金/土）
    2. 天干數相加（年+月+日+時）
    3. 地支數相加（年+月+日+時）
    4. 加歲君加數
    5. 總數定刻 → 對應條文編號

    Parameters
    ----------
    year_gz : str
        年柱干支，如「壬辰」
    month_gz : str
        月柱干支，如「丙午」
    day_gz : str
        日柱干支，如「甲戌」
    hour_gz : str
        時柱干支，如「甲午」
    gender : str
        性別，「男」或「女」
    is_dayun : bool
        是否為大運查詢
    dayun_offset : int
        大運偏移量（每 10 年一步，供流年推算用）

    Returns
    -------
    SuanpanResult
        算盤打數結果
    """
    steps: List[str] = []

    # Step 1: 定部（年柱納音五行）
    nayin = get_nayin(year_gz)
    department = get_nayin_element(nayin) if nayin else ""
    steps.append(f"年柱 {year_gz} → 納音：{nayin or '未知'} → 部：{department or '未知'}")

    # Step 2: 天干數合計
    stem_sum = 0
    for gz in (year_gz, month_gz, day_gz, hour_gz):
        if gz:
            stem_char = gz[0] if gz else ""
            v = STEM_VALUES.get(stem_char, 0)
            stem_sum += v
    steps.append(f"天干數合計：{stem_sum}")

    # Step 3: 地支數合計
    branch_sum = 0
    for gz in (year_gz, month_gz, day_gz, hour_gz):
        if gz and len(gz) >= 2:
            branch_char = gz[1]
            v = BRANCH_VALUES.get(branch_char, 0)
            branch_sum += v
    steps.append(f"地支數合計：{branch_sum}")

    # Step 4: 歲君加數（按部別）
    suijun = SUIJUN_ADD.get(department, 0) if department else 0
    if is_dayun:
        suijun += dayun_offset
    steps.append(f"歲君加數：{suijun}（部：{department}，大運偏移：{dayun_offset}）")

    # Step 5: 算盤總數
    total = BASE_NUMBER + stem_sum + branch_sum + suijun
    steps.append(f"算盤總數：{BASE_NUMBER} + {stem_sum} + {branch_sum} + {suijun} = {total}")

    # Step 6: 定位條文（條文鍵為字串）
    tiaowen_key = str(total)
    steps.append(f"定條文鍵：{tiaowen_key}")

    result = SuanpanResult(
        year_gz=year_gz,
        month_gz=month_gz,
        day_gz=day_gz,
        hour_gz=hour_gz,
        gender=gender,
        nayin=nayin,
        department=department,
        stem_sum=stem_sum,
        branch_sum=branch_sum,
        suijun_add=suijun,
        total_number=total,
        tiaowen_key=tiaowen_key,
        note="算盤打數計算完成（金鎖銀匙歌，曹展碩實務版）",
        calculation_steps=steps,
    )
    return result


# ====================== 5. 五部條文資料庫（延遲載入） ======================

class SuanpanTiaowenDatabase:
    """
    算盤打數五部條文資料庫（延遲載入）

    資料來源：astro/tieban/data/suanpan_tiaowen_full.json
    結構：{ "水": { "男命": { "2241": {...}, ... }, "女命": {...}, "歲運": {...} }, ... }

    特點：
    - 延遲載入（Lazy Loading）：首次查詢時才載入 JSON
    - 支援五部 × 三性別（男命/女命/歲運）分類查詢
    - 支援條文號碼模糊匹配

    使用範例：
        db = SuanpanTiaowenDatabase()
        tiaowen = db.get("水", "男命", "2241")
        # -> {'text': '舟放浪波翻…', 'raw_key': '二二四一'}
    """

    _DATA_FILENAME = "suanpan_tiaowen_full.json"

    def __init__(self) -> None:
        self._data: Optional[Dict[str, Dict[str, Dict[str, Dict]]]] = None

    def _ensure_loaded(self) -> None:
        """延遲載入：首次查詢時才從 JSON 讀取資料"""
        if self._data is not None:
            return
        self._data = {dept: {"男命": {}, "女命": {}, "歲運": {}} for dept in ("水", "火", "木", "金", "土")}
        data_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data", self._DATA_FILENAME,
        )
        if not os.path.exists(data_path):
            import warnings
            warnings.warn(
                f"SuanpanTiaowenDatabase: 找不到資料檔案 {data_path}，"
                "將使用空資料庫。請確認 suanpan_tiaowen_full.json 已放置於 data/ 目錄。",
                UserWarning,
                stacklevel=3,
            )
            return
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self._data = raw
        except Exception as exc:
            import warnings
            warnings.warn(
                f"SuanpanTiaowenDatabase: 載入 {data_path} 失敗（{exc}），使用空資料庫。",
                UserWarning,
                stacklevel=3,
            )

    @property
    def total(self) -> int:
        """資料庫條文總數"""
        self._ensure_loaded()
        count = 0
        for dept_data in self._data.values():
            for gender_data in dept_data.values():
                count += len(gender_data)
        return count

    def get(
        self,
        department: str,
        gender_type: str,
        number: str,
    ) -> Optional[Dict[str, Any]]:
        """
        查詢單一條文

        Parameters
        ----------
        department : str
            五部歸屬：水 / 火 / 木 / 金 / 土
        gender_type : str
            性別類型：男命 / 女命 / 歲運
        number : str
            條文號碼（字串），如 "2241"

        Returns
        -------
        Optional[Dict]
            條文資料（text, raw_key）；找不到時返回 None
        """
        self._ensure_loaded()
        dept_data = self._data.get(department, {})
        gender_data = dept_data.get(gender_type, {})
        entry = gender_data.get(number)
        if entry is not None:
            return dict(entry)
        # 模糊匹配：去掉前導零對比
        number_stripped = number.lstrip("0") or "0"
        for k, v in gender_data.items():
            if k.lstrip("0") == number_stripped:
                return dict(v)
        return None

    def get_by_result(self, calc: SuanpanResult) -> Optional[Dict[str, Any]]:
        """
        根據 SuanpanResult 自動查詢條文

        Parameters
        ----------
        calc : SuanpanResult
            算盤打數計算結果

        Returns
        -------
        Optional[Dict]
            找到的條文；找不到時嘗試模組化後再查，仍無結果則返回 None
        """
        self._ensure_loaded()
        gender_type = SuanpanGender.from_str(calc.gender).value
        dept = calc.department
        if not dept:
            return None

        # 優先精確查詢
        entry = self.get(dept, gender_type, calc.tiaowen_key)
        if entry:
            return entry

        # 找不到時：在本部本性別中按序號取模，確保能拿到一條條文
        gender_data = self._data.get(dept, {}).get(gender_type, {})
        if not gender_data:
            return None
        keys = sorted(gender_data.keys())
        idx = calc.total_number % len(keys)
        return dict(gender_data[keys[idx]])

    def get_suiyun_by_result(self, calc: SuanpanResult) -> Optional[Dict[str, Any]]:
        """
        根據 SuanpanResult 查詢歲運條文（含模數回退）

        優先以 tiaowen_key 精確查詢歲運條文；若找不到，則以
        total_number 取模確保一定能返回一條歲運條文。

        Parameters
        ----------
        calc : SuanpanResult
            算盤打數計算結果

        Returns
        -------
        Optional[Dict]
            歲運條文；本部無歲運資料時返回 None
        """
        self._ensure_loaded()
        dept = calc.department
        if not dept:
            return None

        # 優先精確查詢
        entry = self.get(dept, "歲運", calc.tiaowen_key)
        if entry:
            return entry

        # 找不到時：在本部歲運中按序號取模，確保能拿到一條條文
        suiyun_data = self._data.get(dept, {}).get("歲運", {})
        if not suiyun_data:
            return None
        keys = sorted(suiyun_data.keys())
        idx = calc.total_number % len(keys)
        return dict(suiyun_data[keys[idx]])

    def get_all(
        self,
        department: str,
        gender_type: str,
    ) -> Dict[str, Dict[str, Any]]:
        """取得某部某性別的全部條文"""
        self._ensure_loaded()
        return dict(self._data.get(department, {}).get(gender_type, {}))

    def list_departments(self) -> List[str]:
        """列出所有部別"""
        self._ensure_loaded()
        return list(self._data.keys())

    def stats(self) -> Dict[str, Dict[str, int]]:
        """統計各部各性別條文數量"""
        self._ensure_loaded()
        result: Dict[str, Dict[str, int]] = {}
        for dept, dept_data in self._data.items():
            result[dept] = {g: len(v) for g, v in dept_data.items()}
        return result


# ====================== 6. 大運計算 ======================

def get_dayun(
    year_gz: str,
    month_gz: str,
    day_gz: str,
    hour_gz: str,
    gender: str = "男",
    start_age: int = 0,
    dayun_steps: int = 8,
) -> List[SuanpanResult]:
    """
    大運推算框架（每大運 10 年）

    Parameters
    ----------
    year_gz, month_gz, day_gz, hour_gz : str
        四柱干支
    gender : str
        性別
    start_age : int
        起運年齡
    dayun_steps : int
        推算大運步數（預設 8 步 = 80 年）

    Returns
    -------
    List[SuanpanResult]
        各大運的算盤打數結果列表
    """
    results = []
    for step in range(dayun_steps):
        age = start_age + step * 10
        offset = step * 10  # 大運偏移量
        calc = suanpan_calculate(
            year_gz=year_gz,
            month_gz=month_gz,
            day_gz=day_gz,
            hour_gz=hour_gz,
            gender=gender,
            is_dayun=True,
            dayun_offset=offset,
        )
        calc.dayun_number = age
        calc.note = f"大運第 {step + 1} 步，起運年齡：{age} 歲"
        results.append(calc)
    return results


# ====================== 7. 資料匯出工具 ======================

def export_suanpan_data() -> Dict[str, Any]:
    """匯出算盤打數核心參數（供 JSON 儲存或 Streamlit 顯示）"""
    return {
        "base_number": BASE_NUMBER,
        "suijun_add": SUIJUN_ADD,
        "nayin_add": NAYIN_ADD,
        "stem_values": STEM_VALUES,
        "branch_values": BRANCH_VALUES,
        "version": "2.0",
        "source": "曹展碩實務版鐵板算盤數",
        "note": "算盤打數版，與 kunji_full_structure.py 互補使用",
    }


def save_to_json(filepath: str = "suanpan_full_structure.json") -> None:
    """將核心參數存成 JSON，方便 kinastro 其他模組載入"""
    data = export_suanpan_data()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 算盤數完整資料已儲存至 {filepath}")


# ====================== 測試 ======================
if __name__ == "__main__":
    print("=== 鐵板算盤數 模組測試 ===")

    # 測試計算
    test = suanpan_calculate("壬辰", "丙午", "甲戌", "甲午", gender="男")
    print("測試計算結果：")
    print(f"  納音：{test.nayin}，部：{test.department}")
    print(f"  天干數合計：{test.stem_sum}，地支數合計：{test.branch_sum}")
    print(f"  算盤總數：{test.total_number}，條文鍵：{test.tiaowen_key}")
    print(f"  計算步驟：")
    for step in test.calculation_steps:
        print(f"    - {step}")

    # 載入條文資料庫並查詢
    db = SuanpanTiaowenDatabase()
    tiaowen = db.get_by_result(test)
    print(f"\n  查詢條文：{tiaowen}")
    print(f"\n  資料庫統計：{db.stats()}")

    # 大運測試
    dayun_list = get_dayun("壬辰", "丙午", "甲戌", "甲午", gender="男", start_age=5)
    print(f"\n  大運（前 3 步）：")
    for d in dayun_list[:3]:
        print(f"    - 年齡 {d.dayun_number}：總數={d.total_number}，條文鍵={d.tiaowen_key}")

    print("\n✅ suanpan_full_structure.py 已完整生成並載入完成！")
    print("可與 kunji_full_structure.py 同時使用於 kinastro 專案")
