"""
七政四餘神煞計算模組 (Shen Sha / Divine Stars Module)

根據 MOIRA_chinese_astrology 對齊版。
以年柱（干支）、月支、時支為基準推算各種神煞，
將其分配到十二宮（地支）以便在排盤圖中顯示。

神煞分類：
  - 地支系（以年支為基準推算, 38 星 + 子星群）
  - 天干系（以年干為基準推算, 13 星）
  - 月支系（以月支為基準推算, 6 星）
  - 干支系（以年柱六十甲子為基準推算, 5 星）
  - 月時系（以月支＋時支為基準推算, 1 星）
  - 十二長生（以年柱納音五行為基準佈局）
"""

import streamlit as st
from dataclasses import dataclass, field

# ============================================================
# 天干地支
# ============================================================
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳",
                    "午", "未", "申", "酉", "戌", "亥"]

# 六十甲子索引：甲子=0, 乙丑=1, ..., 癸亥=59
SIXTY_JIAZI = [
    HEAVENLY_STEMS[i % 10] + EARTHLY_BRANCHES[i % 12] for i in range(60)
]


def gz_index(stem: int, branch: int) -> int:
    """由天干索引和地支索引計算六十甲子索引。

    六十甲子中, 索引 i 滿足 i % 10 = stem, i % 12 = branch。
    利用中國剩餘定理: i ≡ 6·stem − 5·branch (mod 60)
    因為 6·10 − 5·12 = 0 (mod 60), 且 6·stem ≡ stem (mod 10),
    −5·branch ≡ branch (mod 12)。
    """
    return (6 * stem - 5 * branch) % 60


@dataclass
class ShenShaItem:
    """單個神煞"""
    name: str              # 神煞名稱
    branch: int            # 所在地支索引 (0-11)
    category: str          # 類別：吉 / 凶 / 中
    source: str            # 來源：地支 / 天干 / 月支 / 干支 / 月時


@dataclass
class ShenShaResult:
    """神煞計算結果"""
    items: list = field(default_factory=list)         # List[ShenShaItem]
    branch_map: dict = field(default_factory=dict)    # branch_idx -> list of names


# ============================================================
# 地支系神煞查表 (以年支查, 共38星)
# 數據對齊 MOIRA_chinese_astrology moira_t.prop 地支{X}= 表
# 年支索引: 子=0, 丑=1, 寅=2, ..., 亥=11
# 值: 神煞所落入的地支索引
# ============================================================

# 歲駕: 子→子, 丑→丑, ... (即年支本身)
SUIJIA = {i: i for i in range(12)}
# 紅鸞
HONGLUAN = {0: 3, 1: 2, 2: 1, 3: 0, 4: 11, 5: 10, 6: 9, 7: 8, 8: 7, 9: 6, 10: 5, 11: 4}
# 天喜
TIANXI = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0, 10: 11, 11: 10}
# 卷舌
JUANSHE = {0: 9, 1: 10, 2: 11, 3: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8}
# 死符
SIFU = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 10, 6: 11, 7: 0, 8: 1, 9: 2, 10: 3, 11: 4}
# 大耗
DAHAO = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 0, 7: 1, 8: 2, 9: 3, 10: 4, 11: 5}
# 三刑 (MOIRA 特定映射, 非簡化對沖)
SANXING = {0: 3, 1: 10, 2: 5, 3: 6, 4: 4, 5: 8, 6: 6, 7: 1, 8: 2, 9: 9, 10: 7, 11: 11}
# 六害 (傳統六害映射)
LIUHAI = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1, 7: 0, 8: 11, 9: 10, 10: 9, 11: 8}
# 孤辰
GUCHEN = {0: 2, 1: 2, 2: 5, 3: 5, 4: 5, 5: 8, 6: 8, 7: 8, 8: 11, 9: 11, 10: 11, 11: 2}
# 寡宿
GUASU = {0: 10, 1: 10, 2: 1, 3: 1, 4: 1, 5: 4, 6: 4, 7: 4, 8: 7, 9: 7, 10: 7, 11: 10}
# 劫殺
JIESHA = {0: 5, 1: 2, 2: 11, 3: 8, 4: 5, 5: 2, 6: 11, 7: 8, 8: 5, 9: 2, 10: 11, 11: 8}
# 亡神
WANGSHEN = {0: 11, 1: 8, 2: 5, 3: 2, 4: 11, 5: 8, 6: 5, 7: 2, 8: 11, 9: 8, 10: 5, 11: 2}
# 的殺
DESHA = {0: 5, 1: 1, 2: 9, 3: 5, 4: 1, 5: 9, 6: 5, 7: 1, 8: 9, 9: 5, 10: 1, 11: 9}
# 大殺
DASHA = {0: 8, 1: 9, 2: 10, 3: 5, 4: 6, 5: 7, 6: 2, 7: 3, 8: 4, 9: 11, 10: 0, 11: 1}
# 咸池 (桃花)
XIANCHI = {0: 9, 1: 6, 2: 3, 3: 0, 4: 9, 5: 6, 6: 3, 7: 0, 8: 9, 9: 6, 10: 3, 11: 0}
# 天雄
TIANXIONG = {0: 8, 1: 9, 2: 10, 3: 11, 4: 0, 5: 1, 6: 2, 7: 3, 8: 4, 9: 5, 10: 6, 11: 7}
# 地雌
DICI = {0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 8, 7: 9, 8: 10, 9: 11, 10: 0, 11: 1}
# 五鬼
WUGUI = {0: 4, 1: 5, 2: 6, 3: 7, 4: 8, 5: 9, 6: 10, 7: 11, 8: 0, 9: 1, 10: 2, 11: 3}
# 貫索
GUANSUO = {0: 3, 1: 4, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11, 9: 0, 10: 1, 11: 2}
# 天空
TIANKONG = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11, 11: 0}
# 天狗
TIANGOU = {0: 10, 1: 11, 2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8, 11: 9}
# 驀越
MOYUE = {0: 11, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 11: 10}
# 天厄
TIANE = {0: 7, 1: 8, 2: 9, 3: 10, 4: 11, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4, 10: 5, 11: 6}
# 天哭
TIANKU = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 0, 7: 11, 8: 10, 9: 9, 10: 8, 11: 7}
# 披頭
PITOU = {0: 4, 1: 3, 2: 2, 3: 1, 4: 0, 5: 11, 6: 10, 7: 9, 8: 8, 9: 7, 10: 6, 11: 5}
# 血刃
XUEREN = {0: 10, 1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 3, 8: 2, 9: 1, 10: 0, 11: 11}
# 黃幡
HUANGFAN = {0: 4, 1: 1, 2: 7, 3: 10, 4: 4, 5: 1, 6: 7, 7: 10, 8: 4, 9: 1, 10: 7, 11: 10}
# 豹尾
BAOWEI = {0: 10, 1: 7, 2: 4, 3: 1, 4: 10, 5: 7, 6: 4, 7: 1, 8: 10, 9: 7, 10: 4, 11: 1}
# 驛馬
YIMA = {0: 2, 1: 11, 2: 8, 3: 5, 4: 2, 5: 11, 6: 8, 7: 5, 8: 2, 9: 11, 10: 8, 11: 5}
# 華蓋
HUAGAI = {0: 4, 1: 1, 2: 10, 3: 7, 4: 4, 5: 1, 6: 10, 7: 7, 8: 4, 9: 1, 10: 10, 11: 7}
# 地解
DIJIE = {0: 7, 1: 7, 2: 8, 3: 8, 4: 9, 5: 9, 6: 10, 7: 10, 8: 11, 9: 11, 10: 6, 11: 6}
# 將星
JIANGXING = {0: 0, 1: 9, 2: 6, 3: 3, 4: 0, 5: 9, 6: 6, 7: 3, 8: 0, 9: 9, 10: 6, 11: 3}
# 歲合
SUIHE = {0: 1, 1: 0, 2: 11, 3: 10, 4: 9, 5: 8, 6: 7, 7: 6, 8: 5, 9: 4, 10: 3, 11: 2}
# 災殺
ZAISHA = {0: 6, 1: 3, 2: 0, 3: 9, 4: 6, 5: 3, 6: 0, 7: 9, 8: 6, 9: 3, 10: 0, 11: 9}
# 天殺
TIANSHA = {0: 7, 1: 4, 2: 1, 3: 10, 4: 7, 5: 4, 6: 1, 7: 10, 8: 7, 9: 4, 10: 1, 11: 10}
# 地殺
DISHA = {0: 8, 1: 5, 2: 2, 3: 11, 4: 8, 5: 5, 6: 2, 7: 11, 8: 8, 9: 5, 10: 2, 11: 11}
# 板鞍
BANAN = {0: 1, 1: 10, 2: 7, 3: 4, 4: 1, 5: 10, 6: 7, 7: 4, 8: 1, 9: 10, 10: 7, 11: 4}
# 吞陷
TUNXIAN = {0: 10, 1: 2, 2: 1, 3: 10, 4: 4, 5: 3, 6: 2, 7: 2, 8: 10, 9: 10, 10: 2, 11: 2}

# ============================================================
# 子星群 (Sub-star groups)
# 與父星共享同一地支位置
# 數據對齊 MOIRA moira_t.prop
# ============================================================
STAR_GROUPS: dict[str, list[str]] = {
    "歲駕": ["劍鋒", "伏屍", "太歲"],
    "死符": ["小耗", "月德"],
    "大耗": ["闌干", "歲破", "月空"],
    "卷舌": ["絞殺", "天德", "福星", "福德", "披麻"],
    "天厄": ["暴敗", "紫微", "龍德"],
    "天雄": ["白虎"],
    "天狗": ["吊客"],
    "驀越": ["病符"],
    "的殺": ["破碎"],
    "咸池": ["桃花", "年殺"],
    "大殺": ["飛廉"],
    "天空": ["太陽", "晦氣"],
    "血刃": ["浮沉", "天解", "解神", "八座"],
    "災殺": ["囚獄"],
    "地殺": ["指背"],
    "板鞍": ["陰殺"],
    "歲合": ["玉堂"],
    "地雌": ["喪門", "地喪"],
    "貫索": ["勾神", "太陰", "卒暴"],
    "五鬼": ["官符", "年符", "飛符", "三台"],
}

# 子星的吉凶分類
_JI_SUBSTARS = frozenset(["月德", "天德", "福星", "福德", "紫微", "龍德",
                           "解神", "天解", "八座", "三台", "太陽", "玉堂"])

# ============================================================
# 天干系神煞查表 (以年干查, 共13星)
# 數據對齊 MOIRA moira_t.prop 天干{X}= 表
# 年干索引: 甲=0, 乙=1, ..., 癸=9
# ============================================================

# 祿勳
LUXUN = {0: 2, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 0}
# 天貴
TIANGUI = {0: 7, 1: 8, 2: 9, 3: 11, 4: 1, 5: 0, 6: 1, 7: 2, 8: 3, 9: 5}
# 玉貴
YUGUI = {0: 1, 1: 0, 2: 11, 3: 9, 4: 7, 5: 8, 6: 7, 7: 6, 8: 5, 9: 3}
# 天廚
TIANCHU = {0: 5, 1: 6, 2: 0, 3: 5, 4: 6, 5: 8, 6: 2, 7: 6, 8: 9, 9: 11}
# 文昌
WENCHANG = {0: 5, 1: 6, 2: 8, 3: 9, 4: 8, 5: 9, 6: 11, 7: 10, 8: 2, 9: 3}
# 陽刃 (僅陽干: 甲丙戊庚壬)
YANGREN = {0: 3, 2: 6, 4: 6, 6: 9, 8: 0}
# 陰刃 (僅陰干: 乙丁己辛癸)
YINREN = {1: 4, 3: 7, 5: 7, 7: 10, 9: 1}
# 飛刃
FEIREN = {0: 9, 1: 10, 2: 0, 3: 1, 4: 0, 5: 1, 6: 3, 7: 4, 8: 6, 9: 7}
# 國印
GUOYIN = {0: 10, 1: 11, 2: 1, 3: 2, 4: 1, 5: 2, 6: 4, 7: 5, 8: 7, 9: 8}
# 紅豔
HONGYAN = {0: 6, 1: 8, 2: 2, 3: 7, 4: 4, 5: 4, 6: 10, 7: 9, 8: 0, 9: 8}
# 流霞
LIUXIA = {0: 9, 1: 10, 2: 7, 3: 8, 4: 5, 5: 6, 6: 4, 7: 3, 8: 11, 9: 2}
# 學堂
XUETANG = {0: 11, 1: 6, 2: 2, 3: 9, 4: 2, 5: 9, 6: 5, 7: 0, 8: 8, 9: 3}
# 福貴
FUGUI = {0: 2, 1: 1, 2: 0, 3: 9, 4: 8, 5: 7, 6: 6, 7: 5, 8: 4, 9: 3}
# 官貴
GUANGUI = {0: 9, 1: 8, 2: 0, 3: 11, 4: 3, 5: 2, 6: 6, 7: 5, 8: 6, 9: 5}

# 飛刃子星群
FEIREN_SUBSTARS: dict[str, list[str]] = {
    "飛刃": ["唐符"],
}

# ============================================================
# 月支系神煞查表 (以月支查, 共6星)
# 數據對齊 MOIRA moira_t.prop 月支{X}= 表
# 月支索引: 子=0, 丑=1, ..., 亥=11
# ============================================================

# 月廉
YUELIAN_M = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 0, 7: 1, 8: 2, 9: 3, 10: 4, 11: 5}
# 月殺
YUESHA_M = {0: 8, 1: 9, 2: 10, 3: 5, 4: 6, 5: 7, 6: 2, 7: 3, 8: 4, 9: 11, 10: 0, 11: 1}
# 月符
YUEFU_M = {0: 4, 1: 5, 2: 6, 3: 7, 4: 8, 5: 9, 6: 10, 7: 11, 8: 0, 9: 1, 10: 2, 11: 3}
# 天耗 (月支版)
TIANHAO_M = {0: 8, 1: 10, 2: 0, 3: 2, 4: 4, 5: 6, 6: 8, 7: 10, 8: 0, 9: 2, 10: 4, 11: 6}
# 地耗 (月支版)
DIHAO_M = {0: 5, 1: 7, 2: 9, 3: 11, 4: 1, 5: 3, 6: 5, 7: 7, 8: 9, 9: 11, 10: 1, 11: 3}
# 注受
ZHUSHOU = {0: 2, 1: 1, 2: 0, 3: 11, 4: 10, 5: 9, 6: 10, 7: 11, 8: 0, 9: 1, 10: 2, 11: 3}

# ============================================================
# 干支系神煞 (以六十甲子索引查)
# 歲殿: (year_branch + year_stem) % 12
# 空亡, 孤虛: 基於旬 (decade) 計算
# 遊奕, 擎天: 60-entry 查表
# ============================================================

# 遊奕 (60甲子 lookup)
YOUYI_60 = {
    0: 6, 1: 4, 2: 2, 3: 1, 4: 11, 5: 9, 6: 6, 7: 4, 8: 2, 9: 11,
    10: 9, 11: 6, 12: 4, 13: 2, 14: 0, 15: 11, 16: 9, 17: 6, 18: 4, 19: 1,
    20: 11, 21: 9, 22: 6, 23: 4, 24: 2, 25: 0, 26: 10, 27: 9, 28: 6, 29: 3,
    30: 1, 31: 11, 32: 9, 33: 6, 34: 4, 35: 9, 36: 0, 37: 10, 38: 9, 39: 5,
    40: 3, 41: 1, 42: 11, 43: 9, 44: 6, 45: 4, 46: 2, 47: 0, 48: 10, 49: 6,
    50: 4, 51: 3, 52: 1, 53: 11, 54: 9, 55: 6, 56: 4, 57: 2, 58: 0, 59: 9,
}

# 擎天 (60甲子 lookup)
QINGTIAN_60 = {
    0: 0, 1: 10, 2: 8, 3: 7, 4: 5, 5: 3, 6: 0, 7: 10, 8: 8, 9: 5,
    10: 3, 11: 0, 12: 10, 13: 8, 14: 6, 15: 5, 16: 3, 17: 0, 18: 10, 19: 7,
    20: 5, 21: 3, 22: 0, 23: 10, 24: 8, 25: 6, 26: 4, 27: 3, 28: 0, 29: 9,
    30: 7, 31: 5, 32: 3, 33: 0, 34: 10, 35: 8, 36: 6, 37: 4, 38: 3, 39: 11,
    40: 9, 41: 7, 42: 5, 43: 3, 44: 0, 45: 10, 46: 8, 47: 6, 48: 4, 49: 0,
    50: 10, 51: 9, 52: 7, 53: 5, 54: 3, 55: 0, 56: 10, 57: 8, 58: 6, 59: 3,
}


def compute_suidian(year_branch: int, year_stem: int) -> int:
    """歲殿 = (year_branch + year_stem) % 12"""
    return (year_branch + year_stem) % 12


def compute_kongwang(gzi: int) -> tuple[int, int]:
    """空亡: 基於旬 (每十個甲子為一旬), 返回兩個空亡地支。

    六十甲子每十個為一旬, 十天干配十地支後剩餘兩地支即空亡:
    甲子旬(0-9)→戌亥(10,11), 甲戌旬(10-19)→申酉(8,9),
    甲申旬(20-29)→午未(6,7), 甲午旬(30-39)→辰巳(4,5),
    甲辰旬(40-49)→寅卯(2,3), 甲寅旬(50-59)→子丑(0,1)。
    通式: 第一空亡 = (5 − decade) × 2, 第二空亡 = 第一 + 1。
    """
    decade = gzi // 10
    first = (5 - decade) * 2
    return first % 12, (first + 1) % 12


def compute_guxu(gzi: int) -> tuple[int, int]:
    """孤虛: 基於旬, 返回兩個孤虛地支。

    孤虛與空亡類似但錯開, 規律為:
    甲子旬→辰巳(4,5), 甲戌旬→寅卯(2,3), 甲申旬→子丑(0,1),
    甲午旬→戌亥(10,11), 甲辰旬→申酉(8,9), 甲寅旬→午未(6,7)。
    通式: 第一孤虛 = (4 − 2·decade + 12) mod 12, 第二 = 第一 + 1。
    """
    decade = gzi // 10
    first = (4 - 2 * decade + 12) % 12
    return first, (first + 1) % 12


# ============================================================
# 十二長生 (Twelve Stages of Life Cycle)
# MOIRA 排列順序 (與年柱納音五行對應)
# ============================================================
TWELVE_LIFE_STAGES = [
    "長生", "養", "胎", "絕", "墓", "死",
    "病", "衰", "帝旺", "臨官", "冠帶", "沐浴",
]

# 納音五行 → 長生起始地支索引
# 金→辰(4), 木→戌(10), 水→丑(1), 土→丑(1), 火→未(7)
NAYIN_LIFE_START = {"金": 4, "木": 10, "水": 1, "土": 1, "火": 7}

# 六十甲子納音五行 (每對: 30 pairs for 60 pillars)
_NAYIN_SEQ = [
    "金", "火", "木", "土", "金",   # 甲子~壬申 (pairs 0-4)
    "火", "水", "土", "金", "木",   # 甲戌~壬午 (pairs 5-9)
    "水", "土", "火", "木", "水",   # 甲申~壬辰 (pairs 10-14)
    "金", "火", "木", "土", "金",   # 甲午~壬寅 (pairs 15-19)
    "火", "水", "土", "金", "木",   # 甲辰~壬子 (pairs 20-24)
    "水", "土", "火", "木", "水",   # 甲寅~壬戌 (pairs 25-29)
]


def get_nayin_element(gzi: int) -> str:
    """取得六十甲子索引對應的納音五行"""
    return _NAYIN_SEQ[gzi // 2]


def compute_twelve_life_stages(year_stem: int, year_branch: int = 0):
    """
    計算十二長生在十二地支的分佈 (MOIRA 納音法)。

    Parameters:
        year_stem: 年干索引 (0-9)
        year_branch: 年支索引 (0-11), 默認0以保持向後兼容

    Returns:
        dict: branch_idx -> stage_name
    """
    gzi = gz_index(year_stem, year_branch)
    nayin = get_nayin_element(gzi)
    start = NAYIN_LIFE_START[nayin]
    result = {}
    for i in range(12):
        branch = (start + i) % 12
        result[branch] = TWELVE_LIFE_STAGES[i]
    return result


# ============================================================
# 主要計算函數
# ============================================================

def get_year_stem(year: int) -> int:
    """取得年干索引 (甲=0 ... 癸=9)"""
    return (year - 4) % 10


def get_year_branch(year: int) -> int:
    """取得年支索引 (子=0 ... 亥=11)"""
    return (year - 4) % 12


def get_month_branch(solar_month: int) -> int:
    """
    取得月支索引。節氣月1=寅(2), 2=卯(3), ..., 12=丑(1)
    """
    return (solar_month + 1) % 12


def get_day_stem_branch(jd: float, timezone: float = 0.0):
    """
    由儒略日計算日干支。

    以 2001-01-01 (JDN 2451911) = 甲子日 為基準。

    Parameters:
        jd: 儒略日 (UT)
        timezone: 時區偏移 (小時), 用於將 UT 轉換為當地時間以確定日期
    """
    local_jd = jd + timezone / 24.0
    day_num = int(local_jd + 0.5)
    base_jd = 2451911  # 2001-01-01
    diff = day_num - base_jd
    day_stem = (0 + diff) % 10
    day_branch = (0 + diff) % 12
    return day_stem, day_branch


def get_hour_stem(day_stem: int, hour_branch: int) -> int:
    """
    由日干和時支推算時干。
    甲己日子時起甲子, 乙庚日子時起丙子, 丙辛日子時起戊子,
    丁壬日子時起庚子, 戊癸日子時起壬子
    """
    base = (day_stem % 5) * 2
    return (base + hour_branch) % 10


@st.cache_data(ttl=3600, show_spinner=False)
def compute_shensha(
    year: int,
    solar_month: int,
    julian_day: float,
    hour_branch: int,
    timezone: float = 0.0,
    ming_gong_branch: int | None = None,
) -> ShenShaResult:
    """
    計算神煞 (對齊 MOIRA_chinese_astrology)。

    Parameters:
        year: 西曆年份
        solar_month: 節氣月 (1-12)
        julian_day: 儒略日
        hour_branch: 時辰地支索引 (0-11)
        timezone: 時區偏移 (小時)
        ming_gong_branch: 命宮地支索引 (0-11)。保留向後兼容, 目前未使用。

    Returns:
        ShenShaResult: 包含所有神煞及其宮位分配
    """
    year_stem = get_year_stem(year)
    year_branch = get_year_branch(year)
    month_branch = get_month_branch(solar_month)
    day_stem, day_branch = get_day_stem_branch(julian_day, timezone)
    gzi = gz_index(year_stem, year_branch)

    items: list[ShenShaItem] = []
    seen: set[tuple[str, int]] = set()  # (name, branch) de-dup

    def _add(name: str, branch: int, category: str, source: str):
        key = (name, branch)
        if key not in seen:
            seen.add(key)
            items.append(ShenShaItem(
                name=name, branch=branch, category=category, source=source,
            ))

    def _add_with_subs(name: str, branch: int, cat: str, src: str):
        """添加父星及其子星群"""
        _add(name, branch, cat, src)
        subs = STAR_GROUPS.get(name)
        if subs:
            for s in subs:
                sub_cat = "吉" if s in _JI_SUBSTARS else cat
                _add(s, branch, sub_cat, src)

    # ==== 地支系 (年支查, 38 父星 + 子星) ====
    _add_with_subs("歲駕", SUIJIA[year_branch], "中", "地支")
    _add("紅鸞", HONGLUAN[year_branch], "吉", "地支")
    _add("天喜", TIANXI[year_branch], "吉", "地支")
    _add_with_subs("卷舌", JUANSHE[year_branch], "凶", "地支")
    _add_with_subs("死符", SIFU[year_branch], "凶", "地支")
    _add_with_subs("大耗", DAHAO[year_branch], "凶", "地支")
    _add("三刑", SANXING[year_branch], "凶", "地支")
    _add("六害", LIUHAI[year_branch], "凶", "地支")
    _add("孤辰", GUCHEN[year_branch], "凶", "地支")
    _add("寡宿", GUASU[year_branch], "凶", "地支")
    _add("劫殺", JIESHA[year_branch], "凶", "地支")
    _add("亡神", WANGSHEN[year_branch], "凶", "地支")
    _add_with_subs("的殺", DESHA[year_branch], "凶", "地支")
    _add_with_subs("大殺", DASHA[year_branch], "凶", "地支")
    _add_with_subs("咸池", XIANCHI[year_branch], "中", "地支")
    _add_with_subs("天雄", TIANXIONG[year_branch], "凶", "地支")
    _add_with_subs("地雌", DICI[year_branch], "凶", "地支")
    _add_with_subs("五鬼", WUGUI[year_branch], "凶", "地支")
    _add_with_subs("貫索", GUANSUO[year_branch], "凶", "地支")
    _add_with_subs("天空", TIANKONG[year_branch], "凶", "地支")
    _add_with_subs("天狗", TIANGOU[year_branch], "凶", "地支")
    _add_with_subs("驀越", MOYUE[year_branch], "凶", "地支")
    _add_with_subs("天厄", TIANE[year_branch], "凶", "地支")
    _add("天哭", TIANKU[year_branch], "凶", "地支")
    _add("披頭", PITOU[year_branch], "凶", "地支")
    _add_with_subs("血刃", XUEREN[year_branch], "凶", "地支")
    _add("黃幡", HUANGFAN[year_branch], "凶", "地支")
    _add("豹尾", BAOWEI[year_branch], "凶", "地支")
    _add("驛馬", YIMA[year_branch], "中", "地支")
    _add("華蓋", HUAGAI[year_branch], "吉", "地支")
    _add("地解", DIJIE[year_branch], "吉", "地支")
    _add("將星", JIANGXING[year_branch], "吉", "地支")
    _add_with_subs("歲合", SUIHE[year_branch], "吉", "地支")
    _add_with_subs("災殺", ZAISHA[year_branch], "凶", "地支")
    _add("天殺", TIANSHA[year_branch], "凶", "地支")
    _add_with_subs("地殺", DISHA[year_branch], "凶", "地支")
    _add_with_subs("板鞍", BANAN[year_branch], "凶", "地支")
    _add("吞陷", TUNXIAN[year_branch], "凶", "地支")

    # ==== 天干系 (年干查, 13 星) ====
    _add("祿勳", LUXUN[year_stem], "吉", "天干")
    _add("天貴", TIANGUI[year_stem], "吉", "天干")
    _add("玉貴", YUGUI[year_stem], "吉", "天干")
    _add("天廚", TIANCHU[year_stem], "吉", "天干")
    _add("文昌", WENCHANG[year_stem], "吉", "天干")
    # 陽刃 / 陰刃
    if year_stem in YANGREN:
        _add("陽刃", YANGREN[year_stem], "凶", "天干")
    if year_stem in YINREN:
        _add("陰刃", YINREN[year_stem], "凶", "天干")
    fr_branch = FEIREN[year_stem]
    _add("飛刃", fr_branch, "凶", "天干")
    # 飛刃子星
    for sub in FEIREN_SUBSTARS.get("飛刃", []):
        _add(sub, fr_branch, "凶", "天干")
    _add("國印", GUOYIN[year_stem], "吉", "天干")
    _add("紅豔", HONGYAN[year_stem], "中", "天干")
    _add("流霞", LIUXIA[year_stem], "凶", "天干")
    _add("學堂", XUETANG[year_stem], "吉", "天干")
    _add("福貴", FUGUI[year_stem], "吉", "天干")
    _add("官貴", GUANGUI[year_stem], "吉", "天干")

    # ==== 月支系 (月支查, 6 星) ====
    _add("月廉", YUELIAN_M[month_branch], "凶", "月支")
    _add("月殺", YUESHA_M[month_branch], "凶", "月支")
    _add("月符", YUEFU_M[month_branch], "凶", "月支")
    _add("天耗", TIANHAO_M[month_branch], "凶", "月支")
    _add("地耗", DIHAO_M[month_branch], "凶", "月支")
    _add("注受", ZHUSHOU[month_branch], "中", "月支")

    # ==== 干支系 (六十甲子查) ====
    _add("歲殿", compute_suidian(year_branch, year_stem), "吉", "干支")
    _add("遊奕", YOUYI_60[gzi], "凶", "干支")
    _add("擎天", QINGTIAN_60[gzi], "中", "干支")
    kw1, kw2 = compute_kongwang(gzi)
    _add("空亡", kw1, "凶", "干支")
    _add("空亡", kw2, "凶", "干支")
    gx1, gx2 = compute_guxu(gzi)
    _add("孤虛", gx1, "凶", "干支")
    _add("孤虛", gx2, "凶", "干支")

    # ==== 月時系 (斗杓) ====
    douzhuo = (month_branch + hour_branch + 2) % 12
    _add("斗杓", douzhuo, "中", "月時")

    # ==== 十二長生 (納音法) ====
    life_stages = compute_twelve_life_stages(year_stem, year_branch)
    for branch_idx, stage_name in life_stages.items():
        _add(stage_name, branch_idx, "中", "納音")

    # Build branch_map
    branch_map: dict[int, list[str]] = {}
    for item in items:
        if item.branch not in branch_map:
            branch_map[item.branch] = []
        branch_map[item.branch].append(item.name)

    return ShenShaResult(items=items, branch_map=branch_map)


def get_bazi_stems_branches(
    year: int,
    solar_month: int,
    julian_day: float,
    hour_branch: int,
    timezone: float = 0.0,
):
    """
    計算八字四柱天干地支。

    Returns:
        dict with keys: year_stem, year_branch, month_stem, month_branch,
                        day_stem, day_branch, hour_stem, hour_branch
              and their corresponding name strings.
    """
    ys = get_year_stem(year)
    yb = get_year_branch(year)
    mb = get_month_branch(solar_month)
    # 月干 = 年干 * 2 + 月支偏移 (虎月起法)
    yin_stem = (2 * (ys % 5) + 2) % 10
    ms = (yin_stem + (mb - 2 + 12) % 12) % 10
    ds, db = get_day_stem_branch(julian_day, timezone)
    hs = get_hour_stem(ds, hour_branch)

    return {
        "year_stem": ys, "year_branch": yb,
        "month_stem": ms, "month_branch": mb,
        "day_stem": ds, "day_branch": db,
        "hour_stem": hs, "hour_branch": hour_branch,
        "year_pillar": HEAVENLY_STEMS[ys] + EARTHLY_BRANCHES[yb],
        "month_pillar": HEAVENLY_STEMS[ms] + EARTHLY_BRANCHES[mb],
        "day_pillar": HEAVENLY_STEMS[ds] + EARTHLY_BRANCHES[db],
        "hour_pillar": HEAVENLY_STEMS[hs] + EARTHLY_BRANCHES[hour_branch],
    }
