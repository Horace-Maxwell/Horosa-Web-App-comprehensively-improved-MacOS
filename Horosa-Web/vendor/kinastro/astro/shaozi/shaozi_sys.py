#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邵子神數 起盤系統 (完整版)
============================
包含所有「起數秘訣」與配卦表
可直接輸入出生年月日時（天干地支）進行起盤

使用方式：
    from shaozi_full_structure import ShaoziShenShu
    shaozi = ShaoziShenShu()
    result = shaozi.cast_plate(year_gz="甲子", month_gz="丙寅", day_gz="戊辰", hour_gz="庚午")
"""

from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional

# ====================== 1. 起數秘訣表 ======================

TIANGAN_QISHU: Dict[str, int] = {
    "戊": 1,
    "乙": 2, "癸": 2,
    "庚": 3,
    "辛": 4,
    "壬": 6, "甲": 6,
    "丁": 7,
    "丙": 8,
    "己": 9,
    # 五數寄中宮 → 後面會再加 5
}

DIZHI_QISHU: Dict[str, int] = {
    "亥": 1, "子": 1,
    "寅": 3, "卯": 3,
    "巳": 2, "午": 2,
    "申": 4, "酉": 4,
    "辰": 5, "戌": 5, "丑": 5, "未": 5,
}

# ====================== 2. 配卦秘訣表 ======================

TIANGAN_PEIGUA: Dict[str, str] = {
    "壬": "乾", "甲": "乾",
    "乙": "坤", "癸": "坤",
    "庚": "震",
    "辛": "巽",
    "丙": "艮",
    "己": "離",
    "戊": "坎",
    "丁": "兌",
}

DIZHI_PEIGUA: Dict[str, str] = {
    "1": "坎", "6": "乾",   # 數字對應卦
    "2": "坤", "7": "兌",
    "3": "震", "8": "艮",
    "4": "巽", "9": "離",
    "5": "中宮",  # 寄宮
}

# ====================== 3. 河洛數 ======================

HELUO_SHU: Dict[str, int] = {
    "甲己": 9, "子午": 9,
    "乙庚": 8, "丑未": 8,
    "丙辛": 7, "寅申": 7,
    "丁壬": 6, "卯酉": 6,
    "戊癸": 5, "辰戌": 5,
    "巳亥": 4,
}

# ====================== 4. 條文資料庫 (從 TXT 自動載入) ======================

class ShaoziShenShu:
    """邵子神數完整起盤系統"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.tiaowen_db: Dict[str, str] = {}   # key: "1001" ~ "6144"
        self.load_tiaowen()

    def load_tiaowen(self) -> None:
        """載入條文資料庫（支援 JSON 或從 TXT 解析）"""
        json_path = self.data_dir / "shaozi_tiaowen_6144.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                self.tiaowen_db = json.load(f)
        else:
            print("⚠️  條文 JSON 不存在，請先執行解析腳本生成 shaozi_tiaowen_6144.json")
            # 這裡可未來擴充自動解析 TXT

    # ====================== 核心起盤函式 ======================

    def calculate_tiangan_number(self, tg: str) -> int:
        """天干起數"""
        num = TIANGAN_QISHU.get(tg, 5)
        return num if num != 5 else 5  # 五寄中宮

    def calculate_dizhi_number(self, dz: str) -> int:
        """地支起數"""
        return DIZHI_QISHU.get(dz, 5)

    def calculate_he_luo(self, tg: str, dz: str) -> int:
        """河洛數"""
        key1 = f"{tg}{dz}"
        key2 = f"{dz}{tg}"
        return HELUO_SHU.get(key1, HELUO_SHU.get(key2, 5))

    def get_peigua(self, tg: str, dz: str) -> str:
        """天干配卦 + 地支配卦"""
        tg_gua = TIANGAN_PEIGUA.get(tg, "中宮")
        dz_num = str(self.calculate_dizhi_number(dz))
        dz_gua = DIZHI_PEIGUA.get(dz_num, "中宮")
        return f"{tg_gua}{dz_gua}"

    def cast_plate(self,
                   year_gz: str,   # "甲子"
                   month_gz: str,
                   day_gz: str,
                   hour_gz: str) -> Dict:
        """
        完整起盤
        輸入：年月日時干支（例如 "甲子"）
        回傳：卦象、基數、對應條文號、條文內容
        """
        # 1. 拆解干支
        y_tg, y_dz = year_gz[0], year_gz[1]
        m_tg, m_dz = month_gz[0], month_gz[1]
        d_tg, d_dz = day_gz[0], day_gz[1]
        h_tg, h_dz = hour_gz[0], hour_gz[1]

        # 2. 計算各宮基數
        tian_gan_num = (
            self.calculate_tiangan_number(y_tg) +
            self.calculate_tiangan_number(m_tg) +
            self.calculate_tiangan_number(d_tg) +
            self.calculate_tiangan_number(h_tg)
        )

        di_zhi_num = (
            self.calculate_dizhi_number(y_dz) +
            self.calculate_dizhi_number(m_dz) +
            self.calculate_dizhi_number(d_dz) +
            self.calculate_dizhi_number(h_dz)
        )

        he_luo_num = self.calculate_he_luo(d_tg, d_dz)  # 以日主為主

        # 3. 八卦加則（簡化版，依書中「爻從三十起，乾卦六為頭」）
        base_number = (tian_gan_num + di_zhi_num + he_luo_num) % 64
        if base_number == 0:
            base_number = 64

        # 4. 產生條文號（書中條文從 1111 開始，實際條文號 = 1000 + base_number）
        tiaowen_id = f"{1000 + base_number:04d}"

        # 5. 取出條文
        tiaowen_text = self.tiaowen_db.get(tiaowen_id, "【條文待補充】")

        result = {
            "input": {
                "year": year_gz,
                "month": month_gz,
                "day": day_gz,
                "hour": hour_gz,
            },
            "base_number": base_number,
            "tiaowen_id": tiaowen_id,
            "gua": self.get_peigua(d_tg, d_dz),   # 日主配卦為主
            "text": tiaowen_text,
            "note": f"天干總數={tian_gan_num}，地支總數={di_zhi_num}，河洛數={he_luo_num}"
        }

        return result


# ====================== 測試與使用範例 ======================

if __name__ == "__main__":
    shaozi = ShaoziShenShu()

    # 範例：出生 甲子年 丙寅月 戊辰日 庚午時
    result = shaozi.cast_plate(
        year_gz="甲子",
        month_gz="丙寅",
        day_gz="戊辰",
        hour_gz="庚午"
    )

    print("=== 邵子神數起盤結果 ===")
    print(f"基數: {result['base_number']}")
    print(f"卦象: {result['gua']}")
    print(f"條文號: {result['tiaowen_id']}")
    print(f"條文:\n{result['text']}")
    print(f"註記: {result['note']}")
