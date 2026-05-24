"""
astro/damo/calculator.py — 達摩一掌經排盤核心計算模組
(Damo One Palm Scripture — Core Computation Module)

達摩一掌經（一掌金）以左手掌十二地支為宮位，配合十二星與六道，
透過年月日時四柱推算前世今生的因果業力。

排盤規則：
1. 年宮 = 出生年地支對應宮位（父母宮，前四世）
2. 年上起月：男命順行、女命逆行數至出生月
3. 月上起日：同方向數至出生日
4. 日上起時：同方向數至出生時辰（子=1, 丑=2 ... 亥=12）
5. 四宮各得一星一道，由此推斷命運

此模組為純計算函式，不含 UI 邏輯，支援 @st.cache_data 快取。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional

import streamlit as st

# ============================================================
# 常量 (Constants)
# ============================================================

EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳",
                     "午", "未", "申", "酉", "戌", "亥"]

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊",
                   "己", "庚", "辛", "壬", "癸"]

# 十二宮固定對應：地支 → (星名, 六道)
PALACE_MAP = {
    "子": ("天貴星", "佛道"),
    "丑": ("天厄星", "鬼道"),
    "寅": ("天權星", "人道"),
    "卯": ("天破星", "畜道"),
    "辰": ("天奸星", "修羅道"),
    "巳": ("天文星", "仙道"),
    "午": ("天福星", "佛道"),
    "未": ("天驛星", "鬼道"),
    "申": ("天孤星", "人道"),
    "酉": ("天刃星", "畜道"),
    "戌": ("天藝星", "修羅道"),
    "亥": ("天壽星", "仙道"),
}

# 時辰名稱
SHICHEN_NAMES = [
    "子時", "丑時", "寅時", "卯時", "辰時", "巳時",
    "午時", "未時", "申時", "酉時", "戌時", "亥時",
]

# 農曆月份名稱
LUNAR_MONTH_NAMES = [
    "正月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "十一月", "十二月",
]


# ============================================================
# 資料模型 (Data Models)
# ============================================================

@dataclass
class DamoPalace:
    """單一宮位結果。"""
    palace_name: str = ""        # 年宮/月宮/日宮/時宮
    palace_alias: str = ""       # 父母宮/事業交友宮/夫妻宮/命宮
    past_life_era: str = ""      # 前四世/前三世/前二世/前一世
    branch: str = ""             # 落在的地支
    star: str = ""               # 所得星名
    realm: str = ""              # 所得六道
    branch_index: int = 0        # 地支索引 (0-11)


@dataclass
class DamoChart:
    """達摩一掌經排盤結果資料類。"""
    # ── 共用欄位 (Common fields) ──
    year: int = 0
    month: int = 0
    day: int = 0
    hour: int = 0
    minute: int = 0
    timezone: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    location_name: str = ""
    julian_day: float = 0.0
    planets: list = field(default_factory=list)

    # ── 體系特有欄位 (Damo-specific fields) ──
    name: str = ""
    gender: str = ""                 # "male" / "female"
    lunar_year: int = 0
    lunar_month: int = 0
    lunar_day: int = 0
    lunar_leap: bool = False
    birth_branch: str = ""           # 出生年地支
    birth_shichen: str = ""          # 出生時辰名
    shichen_index: int = 0           # 時辰索引 (0-11)

    # 四宮結果
    year_palace: Optional[DamoPalace] = None
    month_palace: Optional[DamoPalace] = None
    day_palace: Optional[DamoPalace] = None
    hour_palace: Optional[DamoPalace] = None

    # 總論
    realm_summary: str = ""          # 六道綜合分析
    overall_summary: str = ""        # 總性格總論


# ============================================================
# 輔助函式 (Helper Functions)
# ============================================================

def _hour_to_shichen(hour: int) -> int:
    """將 24 小時制轉換為時辰索引 (0=子, 1=丑 ... 11=亥)。

    子時: 23:00-00:59 → 0
    丑時: 01:00-02:59 → 1
    寅時: 03:00-04:59 → 2
    ...
    亥時: 21:00-22:59 → 11
    """
    if hour == 23:
        return 0  # 晚子時歸子時
    return (hour + 1) // 2 % 12


def _year_to_branch_index(lunar_year: int) -> int:
    """農曆年份轉地支索引 (0=子, 1=丑 ... 11=亥)。

    天干地支以甲子(1)起算，地支 = (年 - 4) % 12
    例如: 1984 甲子年 → (1984-4)%12 = 0 → 子
    """
    return (lunar_year - 4) % 12


def _count_forward(start_index: int, steps: int) -> int:
    """順時針（正向）數 steps 步。"""
    return (start_index + steps - 1) % 12


def _count_backward(start_index: int, steps: int) -> int:
    """逆時針（反向）數 steps 步。"""
    return (start_index - steps + 1) % 12


def _get_palace_info(branch_index: int) -> tuple:
    """取得指定地支索引的宮位資訊 (星名, 六道)。"""
    branch = EARTHLY_BRANCHES[branch_index]
    return PALACE_MAP[branch]


def _solar_to_lunar_fallback(year: int, month: int, day: int,
                              hour: int, minute: int,
                              timezone: float) -> tuple:
    """嘗試使用 pyswisseph 進行陽曆轉農曆。

    Returns: (lunar_year, lunar_month, lunar_day, is_leap)
    若轉換失敗則回傳近似值。
    """
    try:
        import swisseph as swe
        decimal_hour = hour + minute / 60.0 - timezone
        jd = swe.julday(year, month, day, decimal_hour)

        # 使用 ziwei 模組的農曆轉換
        from astro.ziwei import _solar_to_lunar
        ly, lm, ld, leap = _solar_to_lunar(jd)
        return (ly, lm, ld, leap)
    except Exception:
        # 簡易回退：直接使用陽曆作為近似農曆
        return (year, month, day, False)


def _compute_realm_summary(palaces: list) -> str:
    """計算六道綜合分析。"""
    realm_count = {}
    for p in palaces:
        realm_count[p.realm] = realm_count.get(p.realm, 0) + 1

    parts = []
    # 檢查四宮六道分佈
    dominant = max(realm_count, key=realm_count.get)
    dominant_count = realm_count[dominant]

    if dominant_count >= 3:
        parts.append(f"四宮中有三宮以上落入{dominant}，{dominant}的特質在此命格中極為顯著。")
    elif dominant_count == 2:
        parts.append(f"四宮中有兩宮落入{dominant}，此道特質為命格主調。")

    # 吉凶道分析
    good_realms = {"佛道", "仙道"}
    good_count = sum(1 for p in palaces if p.realm in good_realms)
    if good_count >= 3:
        parts.append("此命格佛仙道氣重，前世修行功深，今生福慧兼具。宜繼續精進修持。")
    elif good_count == 0:
        parts.append("此命格前世業力較重，今生雖有磨練，但正是消業積福的大好機會。相由心生，命由己造，積極行善定能改運。")
    else:
        parts.append("此命格善惡兼具，人生有順有逆，正是修行歷練的好命格。把握今生，廣種善因。")

    return "".join(parts)


def _compute_overall_summary(palaces: list) -> str:
    """計算總性格總論。"""
    hour_p = palaces[3]  # 時宮 = 命宮
    parts = [f"命宮（時宮）落入{hour_p.branch}宮，得{hour_p.star}，屬{hour_p.realm}。"]

    # 檢查年月日時四宮的吉凶搭配
    year_p, month_p, day_p = palaces[0], palaces[1], palaces[2]

    parts.append(f"\n年宮（父母宮）得{year_p.star}，顯示前四世因果與家庭背景。")
    parts.append(f"月宮（事業交友宮）得{month_p.star}，揭示事業方向與人際關係。")
    parts.append(f"日宮（夫妻宮）得{day_p.star}，反映婚姻感情與家庭狀況。")
    parts.append(f"時宮（命宮）得{hour_p.star}，決定此生總體命運格調。")

    return "".join(parts)


# ============================================================
# 核心計算 (Core Computation)
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_damo_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    gender: str = "male",
) -> DamoChart:
    """達摩一掌經核心排盤計算。

    Parameters
    ----------
    year, month, day : int
        陽曆出生年月日
    hour, minute : int
        出生時分 (24h)
    timezone : float
        UTC 時區偏移
    latitude, longitude : float
        出生地經緯度
    location_name : str
        出生地名稱
    gender : str
        性別 "male" 或 "female"

    Returns
    -------
    DamoChart
        排盤結果
    """
    # ── 陽曆轉農曆 ──
    lunar_year, lunar_month, lunar_day, lunar_leap = _solar_to_lunar_fallback(
        year, month, day, hour, minute, timezone
    )

    # ── 基本參數 ──
    is_male = (gender == "male")
    shichen_idx = _hour_to_shichen(hour)
    year_branch_idx = _year_to_branch_index(lunar_year)

    chart = DamoChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
        lunar_year=lunar_year,
        lunar_month=lunar_month,
        lunar_day=lunar_day,
        lunar_leap=lunar_leap,
        gender=gender,
        birth_branch=EARTHLY_BRANCHES[year_branch_idx],
        birth_shichen=SHICHEN_NAMES[shichen_idx],
        shichen_index=shichen_idx,
    )

    # ── 1. 年宮（父母宮）= 出生年地支 ──
    year_star, year_realm = _get_palace_info(year_branch_idx)
    chart.year_palace = DamoPalace(
        palace_name="年宮",
        palace_alias="父母宮",
        past_life_era="前四世",
        branch=EARTHLY_BRANCHES[year_branch_idx],
        star=year_star,
        realm=year_realm,
        branch_index=year_branch_idx,
    )

    # ── 2. 月宮（事業交友宮）= 年上起月 ──
    # 從年宮開始，男命順數、女命逆數至月份
    if is_male:
        month_branch_idx = _count_forward(year_branch_idx, lunar_month)
    else:
        month_branch_idx = _count_backward(year_branch_idx, lunar_month)

    month_star, month_realm = _get_palace_info(month_branch_idx)
    chart.month_palace = DamoPalace(
        palace_name="月宮",
        palace_alias="事業交友宮",
        past_life_era="前三世",
        branch=EARTHLY_BRANCHES[month_branch_idx],
        star=month_star,
        realm=month_realm,
        branch_index=month_branch_idx,
    )

    # ── 3. 日宮（夫妻宮）= 月上起日 ──
    if is_male:
        day_branch_idx = _count_forward(month_branch_idx, lunar_day)
    else:
        day_branch_idx = _count_backward(month_branch_idx, lunar_day)

    day_star, day_realm = _get_palace_info(day_branch_idx)
    chart.day_palace = DamoPalace(
        palace_name="日宮",
        palace_alias="夫妻宮",
        past_life_era="前二世",
        branch=EARTHLY_BRANCHES[day_branch_idx],
        star=day_star,
        realm=day_realm,
        branch_index=day_branch_idx,
    )

    # ── 4. 時宮（命宮）= 日上起時 ──
    # 時辰步數：子=1, 丑=2 ... 亥=12
    hour_steps = shichen_idx + 1
    if is_male:
        hour_branch_idx = _count_forward(day_branch_idx, hour_steps)
    else:
        hour_branch_idx = _count_backward(day_branch_idx, hour_steps)

    hour_star, hour_realm = _get_palace_info(hour_branch_idx)
    chart.hour_palace = DamoPalace(
        palace_name="時宮",
        palace_alias="命宮",
        past_life_era="前一世",
        branch=EARTHLY_BRANCHES[hour_branch_idx],
        star=hour_star,
        realm=hour_realm,
        branch_index=hour_branch_idx,
    )

    # ── 綜合分析 ──
    all_palaces = [chart.year_palace, chart.month_palace,
                   chart.day_palace, chart.hour_palace]
    chart.realm_summary = _compute_realm_summary(all_palaces)
    chart.overall_summary = _compute_overall_summary(all_palaces)

    return chart


# ============================================================
# 資料載入 (Data Loading)
# ============================================================

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_DAMO_DATA_FILE = os.path.join(_DATA_DIR, "damo_data.json")


def load_damo_data() -> dict:
    """載入 damo_data.json 解讀資料。"""
    with open(_DAMO_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
