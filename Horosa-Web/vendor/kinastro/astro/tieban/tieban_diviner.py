#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
astro/tieban/tieban_diviner.py — 鐵板神數統一介面

TieBanDiviner: 支援「扣入法（kunji）」與「算盤打數（suanpan）」兩種模式
的統一計算器。

兩種版本對照：
- kunji   = 扣入法 + 坤集密碼表（江靜川版）
         使用 TieBanShenShu 引擎，查詢 tiaowen_full_12000.json
- suanpan = 算盤打數 + 金鎖銀匙歌（曹展碩實務版）
         使用 SuanpanTiaowenDatabase，查詢 suanpan_tiaowen_full.json

使用方式：
    from astro.tieban.tieban_diviner import TieBanDiviner, DivinerMethod
    from astro.tieban.tieban_calculator import TieBanBirthData, Ganzhi
    from datetime import datetime

    birth = TieBanBirthData(
        birth_dt=datetime(1990, 5, 15, 14, 30),
        year_gz=Ganzhi('庚', '午'),
        month_gz=Ganzhi('辛', '巳'),
        day_gz=Ganzhi('戊', '辰'),
        hour_gz=Ganzhi('己', '未'),
        gender="男",
    )

    # 扣入法模式
    kunji_diviner = TieBanDiviner(method="kunji")
    result = kunji_diviner.calculate(birth)

    # 算盤數模式
    suanpan_diviner = TieBanDiviner(method="suanpan")
    suanpan_result = suanpan_diviner.calculate(birth)

    # 統一查詢條文
    tiaowen = suanpan_diviner.get_tiaowen("水", gender_type="男命")
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from astro.tieban.tieban_calculator import (
    TieBanBirthData,
    TieBanResult,
    TieBanShenShu,
)
from astro.tieban.suanpan_full_structure import (
    BASE_NUMBER,
    NAYIN_TABLE,
    NAYIN_TO_ELEMENT,
    SuanpanGender,
    SuanpanResult,
    SuanpanTiaowenDatabase,
    get_dayun,
    get_nayin,
    get_nayin_element,
    suanpan_calculate,
)


# ============================================================================
# Enum
# ============================================================================

class DivinerMethod(str, Enum):
    """鐵板神數計算方式"""
    KUNJI   = "kunji"    # 扣入法（江靜川版）
    SUANPAN = "suanpan"  # 算盤打數（曹展碩實務版）


# ============================================================================
# TieBanDiviner
# ============================================================================

class TieBanDiviner:
    """
    鐵板神數統一計算器

    同時支援「扣入法（kunji）」與「算盤打數（suanpan）」兩種版本，
    提供一致的 API 介面，讓兩版本可以和平共存並隨時切換。

    Attributes
    ----------
    method : DivinerMethod
        當前使用的計算方式

    Parameters
    ----------
    method : str | DivinerMethod
        "kunji" 或 "suanpan"（預設 "kunji"）

    Examples
    --------
    >>> diviner = TieBanDiviner(method="suanpan")
    >>> result = diviner.calculate(birth_data)
    >>> tiaowen = diviner.get_tiaowen("水", gender_type="男命", number="2241")
    >>> dayun_list = diviner.get_dayun(birth_data, start_age=5)
    """

    def __init__(self, method: Union[str, DivinerMethod] = "kunji") -> None:
        if isinstance(method, str):
            try:
                method = DivinerMethod(method)
            except ValueError:
                raise ValueError(
                    f"未知計算方式 '{method}'，請使用 'kunji' 或 'suanpan'"
                )
        self.method = method

        # 延遲初始化各引擎（避免不必要的啟動開銷）
        self._kunji_engine: Optional[TieBanShenShu] = None
        self._suanpan_db: Optional[SuanpanTiaowenDatabase] = None

    # ── 引擎屬性（延遲載入） ────────────────────────────────────────────────

    @property
    def kunji_engine(self) -> TieBanShenShu:
        """扣入法引擎（延遲初始化）"""
        if self._kunji_engine is None:
            self._kunji_engine = TieBanShenShu()
        return self._kunji_engine

    @property
    def suanpan_db(self) -> SuanpanTiaowenDatabase:
        """算盤數條文資料庫（延遲初始化）"""
        if self._suanpan_db is None:
            self._suanpan_db = SuanpanTiaowenDatabase()
        return self._suanpan_db

    # ── 核心方法 ────────────────────────────────────────────────────────────

    def calculate(
        self,
        birth_data: TieBanBirthData,
    ) -> Union[TieBanResult, SuanpanResult]:
        """
        執行鐵板神數推算

        Parameters
        ----------
        birth_data : TieBanBirthData
            出生資料（年月日時干支 + 性別 + 父母六親）

        Returns
        -------
        TieBanResult
            method="kunji" 時的完整扣入法推算結果
        SuanpanResult
            method="suanpan" 時的算盤打數推算結果（已附帶條文）
        """
        if self.method == DivinerMethod.KUNJI:
            return self.kunji_engine.calculate(birth_data)

        # suanpan 模式
        year_gz  = str(birth_data.year_gz)
        month_gz = str(birth_data.month_gz)
        day_gz   = str(birth_data.day_gz)
        hour_gz  = str(birth_data.hour_gz)
        gender   = birth_data.gender

        calc = suanpan_calculate(
            year_gz=year_gz,
            month_gz=month_gz,
            day_gz=day_gz,
            hour_gz=hour_gz,
            gender=gender,
        )

        # 自動查詢條文並附帶到結果
        calc.tiaowen = self.suanpan_db.get_by_result(calc)
        return calc

    def get_tiaowen(
        self,
        department: Optional[str] = None,
        gender_type: str = "男命",
        number: Optional[str] = None,
        *,
        # kunji 模式參數
        tiaowen_number: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        查詢條文

        Parameters
        ----------
        department : str, optional
            【suanpan 模式】五部歸屬：水 / 火 / 木 / 金 / 土
        gender_type : str
            【suanpan 模式】男命 / 女命 / 歲運
        number : str, optional
            【suanpan 模式】條文編號（字串），如 "2241"
        tiaowen_number : int, optional
            【kunji 模式】條文編號（1001–13000）

        Returns
        -------
        Optional[Dict]
            條文資料；找不到時返回 None
        """
        if self.method == DivinerMethod.KUNJI:
            num = tiaowen_number
            if num is None:
                return None
            return self.kunji_engine.get_tiaowen(num)

        # suanpan 模式
        if department is None or number is None:
            return None
        return self.suanpan_db.get(department, gender_type, number)

    def get_dayun(
        self,
        birth_data: TieBanBirthData,
        start_age: int = 0,
        steps: int = 8,
    ) -> List[Union[Dict[str, Any], SuanpanResult]]:
        """
        大運推算

        Parameters
        ----------
        birth_data : TieBanBirthData
            出生資料
        start_age : int
            起運年齡
        steps : int
            推算大運步數（預設 8，每步 10 年）

        Returns
        -------
        List[SuanpanResult]
            method="suanpan"：各大運的算盤打數結果（含條文）
        List[Dict]
            method="kunji"：各大運條文查詢結果列表（格式同 get_tiaowen）
        """
        if self.method == DivinerMethod.SUANPAN:
            year_gz  = str(birth_data.year_gz)
            month_gz = str(birth_data.month_gz)
            day_gz   = str(birth_data.day_gz)
            hour_gz  = str(birth_data.hour_gz)
            gender   = birth_data.gender

            dayun_list = get_dayun(
                year_gz=year_gz,
                month_gz=month_gz,
                day_gz=day_gz,
                hour_gz=hour_gz,
                gender=gender,
                start_age=start_age,
                dayun_steps=steps,
            )
            # 附帶條文
            for item in dayun_list:
                item.tiaowen = self.suanpan_db.get_by_result(item)
            return dayun_list

        # kunji 模式：從推算結果的大運條文編號查詢
        result = self.kunji_engine.calculate(birth_data)
        tiaowen_base = result.tiaowen_number or 1001
        dayun_results = []
        for step in range(steps):
            age = start_age + step * 10
            num = tiaowen_base + step * 100
            num = ((num - 1001) % 12000) + 1001  # 保持在有效範圍
            entry = self.kunji_engine.get_tiaowen(num)
            dayun_results.append({
                "age": age,
                "step": step + 1,
                "tiaowen_number": num,
                "tiaowen": entry,
            })
        return dayun_results

    # ── 便捷屬性 / 資訊方法 ─────────────────────────────────────────────────

    def switch_method(self, method: Union[str, DivinerMethod]) -> "TieBanDiviner":
        """
        切換計算方式（回傳新實例，保留原有引擎快取）

        Parameters
        ----------
        method : str | DivinerMethod
            "kunji" 或 "suanpan"

        Returns
        -------
        TieBanDiviner
            切換方式後的新實例
        """
        new = TieBanDiviner(method=method)
        # 複用已初始化的引擎
        new._kunji_engine = self._kunji_engine
        new._suanpan_db   = self._suanpan_db
        return new

    def get_suanpan_stats(self) -> Dict[str, Any]:
        """取得算盤數資料庫統計資訊"""
        return {
            "total": self.suanpan_db.total,
            "by_department": self.suanpan_db.stats(),
            "departments": self.suanpan_db.list_departments(),
        }

    def get_kunji_db_info(self) -> Dict[str, Any]:
        """取得扣入法條文資料庫統計資訊"""
        return self.kunji_engine.get_tiaowen_database_info()

    def get_full_report(self, birth_data: TieBanBirthData) -> str:
        """
        生成完整文字報告

        Parameters
        ----------
        birth_data : TieBanBirthData
            出生資料

        Returns
        -------
        str
            完整報告（根據 method 選擇對應格式）
        """
        if self.method == DivinerMethod.KUNJI:
            return self.kunji_engine.get_full_report(birth_data)

        # suanpan 報告
        result = self.calculate(birth_data)
        assert isinstance(result, SuanpanResult)

        lines = [
            "═" * 50,
            "     鐵板算盤數推算報告（曹展碩實務版）",
            "═" * 50,
            "",
            "【基本資料】",
            f"年柱：{result.year_gz}　月柱：{result.month_gz}　"
            f"日柱：{result.day_gz}　時柱：{result.hour_gz}",
            f"性別：{result.gender}",
            "",
            "【定部】",
            f"納音：{result.nayin or '未知'}　→　五行部：{result.department or '未知'}",
            "",
            "【算盤打數過程】",
        ]
        for step in result.calculation_steps:
            lines.append(f"  {step}")

        lines += [
            "",
            "【條文】",
        ]
        if result.tiaowen:
            lines.append(f"  {result.tiaowen.get('text', '（條文待補充）')}")
            raw_key = result.tiaowen.get("raw_key", "")
            if raw_key:
                lines.append(f"  原始鍵：{raw_key}")
        else:
            lines.append(f"  （條文編號 {result.tiaowen_key} 暫無資料）")

        lines += [
            "",
            "═" * 50,
            "注意：算盤打數基於金鎖銀匙歌（曹展碩實務版）",
            "═" * 50,
        ]
        return "\n".join(lines)
