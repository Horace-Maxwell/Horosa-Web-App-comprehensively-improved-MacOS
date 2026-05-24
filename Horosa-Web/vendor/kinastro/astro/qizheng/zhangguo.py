"""
張果星宗斷語模組 (Zhang Guo Xing Zong — Star Readings Module)

載入 zhangguo_star_in_branch.json 與 zhangguo_patterns.json，
提供星曜落宮斷語查詢與格局匹配功能，供七政四餘排盤使用。
"""

import json
import os
import streamlit as st
from dataclasses import dataclass, field
from typing import Optional

_DATA_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "data")

# ============================================================
# 星曜名稱映射: 排盤計算名 → 張果星宗 JSON 名
# ============================================================
PLANET_TO_ZHANGGUO = {
    "太陽": "日",
    "太陰": "月",
    "水星": "水星",
    "金星": "金星",
    "火星": "火星",
    "木星": "木星",
    "土星": "土星",
    "羅睺": "羅",
    "計都": "計",
    "月孛": "孛",
    "紫氣": "氣",
}

# 標準十二地支
EARTHLY_BRANCHES = [
    "子", "丑", "寅", "卯", "辰", "巳",
    "午", "未", "申", "酉", "戌", "亥",
]

BRANCH_SET = set(EARTHLY_BRANCHES)


# ============================================================
# 資料結構
# ============================================================
@dataclass
class ZhangguoReading:
    """單條張果星宗斷語"""
    entry_id: int
    star: str           # 星曜 (JSON 名)
    branch: str         # 地支 (or abstract position)
    gender: str         # "both" / "male" / "female"
    reading_type: str   # "合格" / "忌格"
    description: str    # 完整斷語
    note: str           # 出處 / 格名


@dataclass
class ZhangguoPattern:
    """張果星宗格局"""
    pattern_id: int
    name: str
    pattern_type: str   # "合格" / "忌格" / "次格" / "總論"
    category: str       # "日月" / "五星" / "四餘" / ...
    condition: str      # 成格條件
    note: str           # 說明


@dataclass
class ZhangguoResult:
    """張果星宗匹配結果"""
    matched_readings: list = field(default_factory=list)   # List[ZhangguoReading]
    all_patterns: list = field(default_factory=list)        # List[ZhangguoPattern]


# ============================================================
# 資料載入 (cached via @st.cache_data)
# ============================================================


@st.cache_data(show_spinner=False)
def _load_star_data() -> list:
    fpath = os.path.join(_DATA_DIR, "zhangguo_star_in_branch.json")
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("entries", [])


@st.cache_data(show_spinner=False)
def _load_pattern_data() -> list:
    fpath = os.path.join(_DATA_DIR, "zhangguo_patterns.json")
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("patterns", [])


# ============================================================
# 查詢函式
# ============================================================
def lookup_star_in_branch(
    star_name: str,
    branch_name: str,
    gender: str = "both",
) -> list[ZhangguoReading]:
    """
    查詢某星曜在某地支的所有斷語。

    Args:
        star_name: 張果星宗中的星名 (日/月/金星/木星/…/羅/計/氣/孛)
        branch_name: 地支名 (子/丑/…/亥)
        gender: "male" / "female" / "both"

    Returns:
        匹配的 ZhangguoReading 列表
    """
    entries = _load_star_data()
    results = []
    for e in entries:
        if e["star"] != star_name:
            continue
        if e["branch"] != branch_name:
            continue
        # gender: "both" matches everything; otherwise must match exactly or be "both"
        e_gender = e.get("gender", "both")
        if e_gender != "both" and e_gender != gender and gender != "both":
            continue
        results.append(ZhangguoReading(
            entry_id=e.get("id", 0),
            star=e["star"],
            branch=e["branch"],
            gender=e_gender,
            reading_type=e.get("type", ""),
            description=e.get("description", ""),
            note=e.get("note", ""),
        ))
    return results


def match_chart_readings(planets, houses, gender="both"):
    """
    根據排盤結果，匹配所有適用的張果星宗斷語。

    Args:
        planets: List[PlanetPosition] — 排盤的星曜列表
        houses:  List[HouseData] — 排盤的宮位列表
        gender:  "male" / "female"

    Returns:
        List[ZhangguoReading]
    """
    # Build branch lookup from houses
    palace_to_branch = {}
    for h in houses:
        palace_to_branch[h.index] = h.branch

    all_readings = []
    for planet in planets:
        zg_name = PLANET_TO_ZHANGGUO.get(planet.name)
        if zg_name is None:
            continue
        branch_idx = palace_to_branch.get(planet.palace_index)
        if branch_idx is None or not (0 <= branch_idx < 12):
            continue
        branch_name = EARTHLY_BRANCHES[branch_idx]
        readings = lookup_star_in_branch(zg_name, branch_name, gender)
        all_readings.extend(readings)

    return all_readings


def get_all_patterns() -> list[ZhangguoPattern]:
    """取得所有張果星宗格局（供參考顯示）"""
    entries = _load_pattern_data()
    return [
        ZhangguoPattern(
            pattern_id=e.get("id", 0),
            name=e.get("name", ""),
            pattern_type=e.get("type", ""),
            category=e.get("category", ""),
            condition=e.get("condition", ""),
            note=e.get("note", ""),
        )
        for e in entries
    ]


def compute_zhangguo(planets, houses, gender="both") -> ZhangguoResult:
    """
    計算張果星宗完整結果。

    Args:
        planets: List[PlanetPosition]
        houses:  List[HouseData]
        gender:  "male" / "female"

    Returns:
        ZhangguoResult
    """
    readings = match_chart_readings(planets, houses, gender)
    patterns = get_all_patterns()
    return ZhangguoResult(
        matched_readings=readings,
        all_patterns=patterns,
    )
