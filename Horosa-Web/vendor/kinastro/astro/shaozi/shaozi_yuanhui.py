#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邵子神數 元會運世模組 (shaozi_yuanhui.py)
==========================================

專為 https://github.com/kentang2017/kinastro 專案設計

此模組實作邵雍《皇極經世》中的「元會運世」時間哲學系統，
用於分析個人出生年所處的大時代背景與人生階段。

核心概念：
- 1 元 = 12 會 = 129,600 年
- 1 會 = 30 運 = 10,800 年
- 1 運 = 12 世 = 360 年
- 1 世 = 30 年

使用方式：
    from shaozi_yuanhui import YuanHuiYunShi

    yhy = YuanHuiYunShi(birth_year=1990)
    print(yhy.get_cycle_info())
    print(yhy.get_life_stage())
"""

from typing import Dict, Any


class YuanHuiYunShi:
    """
    邵子神數 元會運世系統

    計算出生年對應的「元、會、運、世」位置，
    並提供人生階段判斷與大時代背景解讀。
    """

    # ==================== 常數定義 ====================
    YUAN_YEARS = 129600      # 1 元 = 129,600 年
    HUI_YEARS = 10800        # 1 會 = 10,800 年
    YUN_YEARS = 360          # 1 運 = 360 年
    SHI_YEARS = 30           # 1 世 = 30 年

    # 基準年（邵雍常用宋真宗大中祥符元年為起算點）
    BASE_YEAR = 1008

    def __init__(self, birth_year: int):
        """
        初始化元會運世計算

        Args:
            birth_year: 出生年份（西元年）
        """
        self.birth_year = birth_year
        self.yuan, self.hui, self.yun, self.shi = self._calculate_cycles()

    def _calculate_cycles(self) -> tuple:
        """
        計算出生年對應的元會運世

        Returns:
            (yuan, hui, yun, shi)
        """
        years_since_base = self.birth_year - self.BASE_YEAR

        # 元
        yuan = (years_since_base // self.YUAN_YEARS) + 1
        remaining = years_since_base % self.YUAN_YEARS

        # 會
        hui = (remaining // self.HUI_YEARS) + 1
        remaining %= self.HUI_YEARS

        # 運
        yun = (remaining // self.YUN_YEARS) + 1
        remaining %= self.YUN_YEARS

        # 世
        shi = (remaining // self.SHI_YEARS) + 1

        return yuan, hui, yun, shi

    def get_cycle_info(self) -> Dict[str, Any]:
        """
        取得完整的元會運世資訊

        Returns:
            包含元、會、運、世及對應年數的字典
        """
        return {
            "birth_year": self.birth_year,
            "元": self.yuan,
            "會": self.hui,
            "運": self.yun,
            "世": self.shi,
            "對應年數": {
                "元": self.YUAN_YEARS,
                "會": self.HUI_YEARS,
                "運": self.YUN_YEARS,
                "世": self.SHI_YEARS
            },
            "累計年數": {
                "元": (self.yuan - 1) * self.YUAN_YEARS,
                "會": (self.hui - 1) * self.HUI_YEARS,
                "運": (self.yun - 1) * self.YUN_YEARS,
                "世": (self.shi - 1) * self.SHI_YEARS
            }
        }

    def get_life_stage(self) -> str:
        """
        根據「世」的位置判斷人生階段

        Returns:
            人生階段文字描述
        """
        if self.shi <= 3:
            return "早年（奠基期） - 學習、成長、建立基礎"
        elif self.shi <= 6:
            return "中年前期（發展期） - 事業、家庭、社會角色建立"
        elif self.shi <= 9:
            return "中晚年（收穫期） - 成果展現、社會地位穩固"
        else:
            return "晚年（傳承期） - 智慧傳承、回顧總結、留名後世"

    def get_era_description(self) -> str:
        """
        簡單描述當前所處的時代階段（可後續擴充更詳細解讀）

        Returns:
            時代階段文字描述
        """
        if self.yun <= 4:
            return "上升發展期"
        elif self.yun <= 8:
            return "穩定成熟期"
        else:
            return "轉型調整期"

    def get_summary(self) -> str:
        """
        回傳簡潔的文字摘要（適合顯示用）

        Returns:
            格式化的元會運世摘要文字
        """
        info = self.get_cycle_info()
        return (
            f"出生年：{self.birth_year} 年\n"
            f"元會運世：第{info['元']}元 第{info['會']}會 第{info['運']}運 第{info['世']}世\n"
            f"人生階段：{self.get_life_stage()}\n"
            f"時代階段：{self.get_era_description()}"
        )


# ====================== 獨立測試 ======================

if __name__ == "__main__":
    print("=" * 60)
    print("邵子神數 元會運世系統測試")
    print("=" * 60)

    # 測試幾個不同年份
    test_years = [1960, 1985, 1995, 2010, 2025]

    for year in test_years:
        yhy = YuanHuiYunShi(year)
        print(f"\n【{year}年出生】")
        print(yhy.get_summary())
        print("-" * 40)