# -*- coding: utf-8 -*-
"""
astro/bazi/calculator.py — 子平八字核心計算模組
Traditional Ziping Bazi Astrology — Core Calculator

實現「子平正宗」古法推命，嚴格遵循：
  《子平真詮》（沈孝瞻）格局取用神法
  《三命通會》（萬民英）神煞、沖合刑害
  《淵海子平》（徐大升）原始子平法
  《滴天髓》（京圖）日主強弱辨析

主要函式：
    compute_bazi(year, month, day, hour, minute, gender,
                 timezone, latitude, longitude, location_name)
      → BaziChart（完整命盤資料類別）

測試命例：
    1. 毛澤東（Mao Zedong）：1893-12-26 07:30 湖南韶山
       八字：癸巳 甲子 丁酉 甲辰
    2. 蔣中正（Chiang Kai-shek）：1887-10-31 00:00 浙江寧波
       八字：丁亥 甲戌 丙戌 甲子
    3. 示例現代命盤：1985-02-04 10:00 北京
       八字：乙丑 戊寅 甲戌 丁巳
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Set, Tuple

from sxtwl import fromSolar

from .constants import (
    CANGGAN,
    CHANGSHENG_SEQUENCE,
    CHANGSHENG_START_YANG,
    CHANGSHENG_START_YIN,
    DIZHI,
    DZ_IDX,
    GUASU,
    GUCHEN,
    HONGLUAN,
    JIAZI,
    JIE_TO_MONTH_BRANCH,
    JIESHA,
    JIANGXING,
    LIUCHONG,
    LIUHAI,
    LIUHE,
    LUSHEN,
    MONTH_JIE_INDICES,
    MONTH_VITALITY,
    SANHUI,
    SANHE,
    SANXING_GROUPS,
    SHISHEN,
    SHISHEN_SHORT,
    SXTWL_JIEQI,
    TAOHUA,
    TG_IDX,
    TIANGAN,
    TIANGAN_HE,
    TIANXI,
    TIANYI_GUIREN,
    VITALITY_SCORES,
    WENCHANG,
    WUHU_DUN,
    WUSHU_DUN,
    WUXING_DZ,
    WUXING_KEME,
    WUXING_KE,
    WUXING_SHENG,
    WUXING_SHENGME,
    WUXING_TG,
    YANGREN,
    YINYANG_DZ,
    YINYANG_TG,
    YIMA,
    ZAISHA,
    ZHIBEN,
    hour_to_branch_idx,
)


# ──────────────────────────────────────────────────────────────────────────────
# 資料類別（Data Classes）
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Pillar:
    """一柱干支（Single Pillar — Stem + Branch）."""

    stem: str        # 天干 e.g. 甲
    branch: str      # 地支 e.g. 子
    wuxing_stem: str = field(default="")    # 天干五行
    wuxing_branch: str = field(default="") # 地支五行
    yinyang_stem: bool = field(default=True)   # 天干陰陽（True=陽）
    yinyang_branch: bool = field(default=True) # 地支陰陽（True=陽）
    shishen: str = field(default="")           # 十神（相對日主）
    canggan: List[str] = field(default_factory=list)    # 地支藏干
    canggan_shishen: List[str] = field(default_factory=list) # 藏干十神
    changsheng: str = field(default="")        # 十二長生

    @property
    def ganzhi(self) -> str:
        return self.stem + self.branch


@dataclass
class DayunStep:
    """一步大運（One Great Fortune Cycle）."""

    ganzhi: str          # 干支
    stem: str
    branch: str
    age_start: float     # 起運歲數
    age_end: float       # 終運歲數
    year_start: int      # 起運公曆年
    month_start: int     # 起運月份
    day_start: int       # 起運日
    shishen_stem: str = field(default="")
    shishen_branch: str = field(default="")


@dataclass
class ShenSha:
    """神煞條目（Shen Sha Entry）."""

    name: str        # 神煞名
    name_en: str     # 英文名
    pillar: str      # 所在柱（年/月/日/時）
    branch: str      # 所在地支
    is_auspicious: bool = True  # 吉/凶
    description_zh: str = field(default="")
    description_en: str = field(default="")


@dataclass
class BaziInteractions:
    """沖合刑害（Branch Interactions）."""

    liuhe: List[Tuple[str, str, str]] = field(default_factory=list)   # 六合：(支1, 支2, 化五行)
    sanhe: List[Tuple[List[str], str]] = field(default_factory=list)  # 三合：([支...], 五行)
    sanhui: List[Tuple[List[str], str]] = field(default_factory=list) # 三會
    liuchong: List[Tuple[str, str]] = field(default_factory=list)     # 六冲
    liuhai: List[Tuple[str, str]] = field(default_factory=list)       # 六害
    sanxing: List[Tuple[List[str], str]] = field(default_factory=list) # 三刑
    tiangan_he: List[Tuple[str, str, str]] = field(default_factory=list) # 天干相合


@dataclass
class BaziChart:
    """完整子平八字命盤（Complete Bazi Chart）.

    包含四柱、十神、格局、用神、大運、流年、神煞、沖合刑害及文字解讀。
    """

    # 輸入資訊
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    birth_minute: int
    gender: str           # 男 / 女
    timezone: float
    latitude: float
    longitude: float
    location_name: str

    # 四柱
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar

    # 日主資訊
    day_master: str       # 日主天干
    day_master_wuxing: str  # 日主五行
    day_master_strength: str      # 強弱：「身強」「身弱」「中和」
    day_master_strength_score: float  # 數值分數
    day_master_vitality: str      # 旺相休囚死

    # 格局
    pattern: str          # 格局名稱
    pattern_type: str     # 正格 / 從格 / 專旺格
    pattern_description_zh: str
    pattern_description_en: str

    # 用神忌神
    yongshen: str         # 用神（五行）
    xishen: str           # 喜神（五行）
    jishen: str           # 忌神（五行）
    jiaoshen: str         # 仇神（五行）
    tiaohoushen: str      # 調候用神
    yongshen_description_zh: str
    yongshen_description_en: str

    # 大運
    dayun_direction: str  # 順行 / 逆行
    dayun_start_age: float     # 起運歲數
    dayun_start_date: date     # 起運日期
    dayun_steps: List[DayunStep]

    # 當前大運及流年
    current_dayun: Optional[DayunStep]
    current_liunian: str      # 當前流年干支
    current_liunian_year: int

    # 神煞
    shensha_list: List[ShenSha]

    # 沖合刑害
    interactions: BaziInteractions

    # 文字解讀
    reading_zh: str       # 古典風格中文解讀
    reading_en: str       # 英文解讀

    # 輔助
    birth_datetime_str: str
    blind_school_report: Dict[str, object] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────────
# 輔助函式
# ──────────────────────────────────────────────────────────────────────────────

def _build_jiazi_seq() -> List[str]:
    """生成六十甲子序列。"""
    return [TIANGAN[i % 10] + DIZHI[i % 12] for i in range(60)]


_JIAZI_SEQ = _build_jiazi_seq()
_JIAZI_IDX: Dict[str, int] = {gz: i for i, gz in enumerate(_JIAZI_SEQ)}


def _jiazi_next(gz: str, steps: int = 1) -> str:
    """在六十甲子中往後推 steps 步。"""
    idx = _JIAZI_IDX.get(gz, 0)
    return _JIAZI_SEQ[(idx + steps) % 60]


def _jiazi_prev(gz: str, steps: int = 1) -> str:
    """在六十甲子中往前退 steps 步。"""
    idx = _JIAZI_IDX.get(gz, 0)
    return _JIAZI_SEQ[(idx - steps) % 60]


@lru_cache(maxsize=128)
def _get_shishen(day_stem: str, target_stem: str) -> str:
    """計算天干間的十神關係（以日主為基準）。

    典籍：《子平真詮》第一章
    """
    if day_stem == target_stem:
        return "日主"
    day_wx = WUXING_TG[day_stem]
    tgt_wx = WUXING_TG[target_stem]
    day_yang = YINYANG_TG[day_stem]
    tgt_yang = YINYANG_TG[target_stem]
    same_polarity = (day_yang == tgt_yang)

    if day_wx == tgt_wx:
        return "比肩" if same_polarity else "劫財"
    if WUXING_SHENG[day_wx] == tgt_wx:
        return "食神" if same_polarity else "傷官"
    if WUXING_KE[day_wx] == tgt_wx:
        return "偏財" if same_polarity else "正財"
    if WUXING_KE[tgt_wx] == day_wx:
        return "七殺" if same_polarity else "正官"
    if WUXING_SHENG[tgt_wx] == day_wx:
        return "偏印" if same_polarity else "正印"
    return ""


@lru_cache(maxsize=128)
def _get_changsheng(stem: str, branch: str) -> str:
    """計算天干在某地支的十二長生狀態。

    典籍：《三命通會》卷二「論十二運」
    """
    yang = YINYANG_TG[stem]
    start_map = CHANGSHENG_START_YANG if yang else CHANGSHENG_START_YIN
    start_branch = start_map.get(stem)
    if start_branch is None:
        return ""
    start_idx = DZ_IDX[start_branch]
    branch_idx = DZ_IDX[branch]
    if yang:
        offset = (branch_idx - start_idx) % 12
    else:
        offset = (start_idx - branch_idx) % 12
    return CHANGSHENG_SEQUENCE[offset]


def _get_kongwang(day_gz: str) -> Tuple[str, str]:
    """計算日柱的空亡地支。

    依六十甲子週期分組，每組10個，最後2個地支空亡。
    典籍：《三命通會》卷一「論空亡」
    """
    idx = _JIAZI_IDX.get(day_gz, 0)
    group = idx // 10  # 0–5
    # 每組甲子以亥為終，對應空亡地支
    # 甲子旬（0-9）: 戌亥空; 甲戌旬（10-19）: 申酉空; etc.
    kongwang_map = [
        ("戌", "亥"),  # 甲子旬
        ("申", "酉"),  # 甲戌旬
        ("午", "未"),  # 甲申旬
        ("辰", "巳"),  # 甲午旬
        ("寅", "卯"),  # 甲辰旬
        ("子", "丑"),  # 甲寅旬
    ]
    return kongwang_map[group % 6]


def _make_pillar(stem: str, branch: str, day_stem: str, label: str = "") -> Pillar:
    """建立一個 Pillar 物件。"""
    cg = CANGGAN.get(branch, [])
    cg_shishen = [_get_shishen(day_stem, s) for s in cg]
    ss = _get_shishen(day_stem, stem) if label != "日主" else "日主"
    cs = _get_changsheng(day_stem, branch)
    return Pillar(
        stem=stem,
        branch=branch,
        wuxing_stem=WUXING_TG[stem],
        wuxing_branch=WUXING_DZ[branch],
        yinyang_stem=YINYANG_TG[stem],
        yinyang_branch=YINYANG_DZ[branch],
        shishen=ss,
        canggan=cg,
        canggan_shishen=cg_shishen,
        changsheng=cs,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 四柱計算（Four Pillars Calculation）
# ──────────────────────────────────────────────────────────────────────────────

def _compute_four_pillars(
    year: int, month: int, day: int, hour: int, minute: int
) -> Tuple[Tuple[str, str], Tuple[str, str], Tuple[str, str], Tuple[str, str]]:
    """計算年月日時四柱干支。

    使用 sxtwl 計算，月柱以「節」為界（非農曆月份），
    時柱依五鼠遁日起時法精確計算。

    注意：23:00 以後視為翌日子時（傳統子時跨日規則）。

    典籍：《淵海子平》「起四柱法」

    Returns:
        ((年干, 年支), (月干, 月支), (日干, 日支), (時干, 時支))
    """
    # 23點後進入翌日子時
    calc_year, calc_month, calc_day, calc_hour = year, month, day, hour
    if hour == 23:
        dt = date(year, month, day) + timedelta(days=1)
        calc_year, calc_month, calc_day = dt.year, dt.month, dt.day
        calc_hour = 0

    cdate = fromSolar(calc_year, calc_month, calc_day)

    # 年柱（以立春為歲首）
    ygz_raw = cdate.getYearGZ(False)
    y_stem = TIANGAN[ygz_raw.tg]
    y_branch = DIZHI[ygz_raw.dz]

    # 月柱（sxtwl 直接使用節為界）
    mgz_raw = cdate.getMonthGZ()
    m_stem = TIANGAN[mgz_raw.tg]
    m_branch = DIZHI[mgz_raw.dz]

    # 日柱
    dgz_raw = cdate.getDayGZ()
    d_stem = TIANGAN[dgz_raw.tg]
    d_branch = DIZHI[dgz_raw.dz]

    # 時柱（五鼠遁日起時）
    h_branch = DIZHI[hour_to_branch_idx(calc_hour)]
    h_stem_base = WUSHU_DUN[d_stem]
    h_stem_idx = (TG_IDX[h_stem_base] + DZ_IDX[h_branch]) % 10
    h_stem = TIANGAN[h_stem_idx]

    return (y_stem, y_branch), (m_stem, m_branch), (d_stem, d_branch), (h_stem, h_branch)


# ──────────────────────────────────────────────────────────────────────────────
# 日主強弱分析（Day Master Strength Analysis）
# 典籍：《子平真詮》「論用神」，《滴天髓》「論身強身弱」
# ──────────────────────────────────────────────────────────────────────────────

def _analyze_day_master_strength(
    day_stem: str,
    year_stem: str, year_branch: str,
    month_stem: str, month_branch: str,
    hour_stem: str, hour_branch: str,
) -> Tuple[str, float, str]:
    """分析日主強弱。

    評分方式（古典旺相休囚死計分）：
    - 月令（月支）: 核心判斷基準，佔最大權重
    - 各柱天干：同五行（比劫）、生我（印）增力；
                克我（官殺）、我克（財）、我生（食傷）洩力
    - 各柱地支藏干：同上，權重略輕

    Returns:
        (強弱描述, 數值分數, 月令旺相休囚死)
    """
    dm_wx = WUXING_TG[day_stem]

    # 月令基礎分
    m_vitality = "死"
    for state, branches in MONTH_VITALITY[dm_wx].items():
        if month_branch in branches:
            m_vitality = state
            break
    score = float(VITALITY_SCORES[m_vitality]) * 3.0  # 月令三倍重

    # 各柱天干貢獻（不含日主自身）
    stems = [year_stem, month_stem, hour_stem]
    branches = [year_branch, month_branch, hour_branch]

    for s in stems:
        s_wx = WUXING_TG[s]
        if s_wx == dm_wx:
            score += 1.5  # 比劫幫身
        elif WUXING_SHENG.get(s_wx) == dm_wx:
            score += 1.5  # 印綬生身
        elif WUXING_KE.get(s_wx) == dm_wx:
            score -= 1.0  # 官殺克身
        elif WUXING_KE.get(dm_wx) == s_wx:
            score -= 0.5  # 財星洩身（耗身）
        elif WUXING_SHENG.get(dm_wx) == s_wx:
            score -= 0.5  # 食傷洩身

    for b in branches:
        b_cg = CANGGAN.get(b, [])
        for cg in b_cg:
            cg_wx = WUXING_TG[cg]
            if cg_wx == dm_wx:
                score += 0.8
            elif WUXING_SHENG.get(cg_wx) == dm_wx:
                score += 0.8
            elif WUXING_KE.get(cg_wx) == dm_wx:
                score -= 0.5
            elif WUXING_KE.get(dm_wx) == cg_wx:
                score -= 0.25
            elif WUXING_SHENG.get(dm_wx) == cg_wx:
                score -= 0.25

    # 強弱判斷
    if score >= 12:
        strength = "身強（過旺）"
    elif score >= 8:
        strength = "身強"
    elif score >= 5:
        strength = "中和"
    elif score >= 3:
        strength = "身弱"
    else:
        strength = "身弱（極弱）"

    return strength, round(score, 2), m_vitality


# ──────────────────────────────────────────────────────────────────────────────
# 格局判斷（Pattern Determination）
# 典籍：《子平真詮》卷一「論格局」
# ──────────────────────────────────────────────────────────────────────────────

# 月令本氣十神 → 正格名稱及說明（模組常數，避免每次調用重建字典）
_SHISHEN_TO_PATTERN: Dict[str, Tuple[str, str, str]] = {
    "食神": ("食神格",
             "食神生財，格局清純，主聰明、有才華、食祿豐厚。",
             "Output (Shishen) pattern: Creative intelligence, talent, abundant food and salary."),
    "傷官": ("傷官格",
             "傷官格局，才藝超群，聰明絕頂，然性情激烈，宜見印制傷。",
             "Hurting Official pattern: Brilliant talent but impulsive nature; beneficial to see Seal to control."),
    "偏財": ("偏財格",
             "偏財格，主廣結善緣、善於經營、財運寬厚，然財易散。",
             "Indirect Wealth pattern: Broad connections, business acumen, generous nature."),
    "正財": ("正財格",
             "正財格，主勤勞踏實，財運平穩，持家有方，婚姻美滿。",
             "Direct Wealth pattern: Diligent and steady, stable finances, harmonious family."),
    "七殺": ("七殺格",
             "七殺格（偏官格），權威刑戮之氣，宜食神制殺，或印化殺為貴。",
             "Seven Killings pattern: Authority and power; Shishen or Seal needed to control or transform."),
    "正官": ("正官格",
             "正官格，主貴氣正直，官祿亨通，名望顯赫，宜財印輔助。",
             "Direct Official pattern: Upright nobility, prosperous official career, fine reputation."),
    "偏印": ("偏印格",
             "偏印格（梟神奪食），多才多藝，然性孤僻，食神受制則困厄。",
             "Indirect Seal (Owl) pattern: Versatile talents but lonely disposition; watch for Output suppression."),
    "正印": ("正印格",
             "正印格，品德高尚，學識淵博，多得長輩庇蔭，官印相輝。",
             "Direct Seal pattern: Virtuous character, broad learning, protected by elders."),
}

# 從格（Following Patterns）干支 → 從格名
_CONG_PATTERNS: Dict[str, str] = {
    "正財": "從財格", "偏財": "從財格",
    "七殺": "從殺格", "正官": "從官格",
    "食神": "從食格", "傷官": "從食格",
}

# 五行一氣（專旺格）名稱及說明
_ZHUAN_WANG_PATTERN: Dict[str, Tuple[str, str, str]] = {
    "木": ("曲直格", "曲直仁壽格，全局木氣旺盛，宜水木流行。", "Qüzhi (Wood) pattern: Prosperous Wood throughout, favorable Water and Wood flow."),
    "火": ("炎上格", "炎上格，全局火氣旺盛，威顯名揚，宜木火流行。", "Yanshang (Fire) pattern: Blazing Fire throughout, prestige and fame."),
    "土": ("稼穡格", "稼穡格，全局土氣旺盛，富厚實在，宜火土流行。", "Jiase (Earth) pattern: Rich Earth throughout, stable wealth."),
    "金": ("從革格", "從革格，全局金氣旺盛，剛烈堅毅，宜土金流行。", "Conge (Metal) pattern: Powerful Metal throughout, resolute character."),
    "水": ("潤下格", "潤下格，全局水氣旺盛，聰明機智，宜金水流行。", "Runxia (Water) pattern: Flowing Water throughout, clever and resourceful."),
}


def _determine_pattern(
    day_stem: str,
    month_branch: str,
    all_stems: List[str],
    all_branches: List[str],
    strength_score: float,
) -> Tuple[str, str, str, str]:
    """判斷格局。

    取格原則（子平真詮）：
    1. 看月令地支藏干（以本氣為主）
    2. 本氣所代表的十神即為格局
    3. 例外：月令本氣為日主同五行 → 建祿格（臨官）/ 月刃格（帝旺）

    Returns:
        (格局名稱, 格局類型, 中文說明, 英文說明)
    """
    dm_wx = WUXING_TG[day_stem]

    # 取月令本氣
    main_cg = ZHIBEN.get(month_branch, "")
    if not main_cg:
        return "雜格", "特殊格", "月令藏干不明", "Unclear month branch stem"

    shishen = _get_shishen(day_stem, main_cg)

    # 建祿 / 月刃（月令本氣與日主同五行）
    if WUXING_TG[main_cg] == dm_wx:
        cs = _get_changsheng(day_stem, month_branch)
        if cs == "臨官":
            pattern = "建祿格"
            desc_zh = "月令建祿，日主得月令之氣，身強格貴，宜取財官食傷為用。"
            desc_en = "Jianlü pattern: Day master receives month's vital force at Lingguan stage. Strong constitution, best use Official, Wealth, or Output gods."
        elif cs == "帝旺":
            pattern = "月刃格"
            desc_zh = "月令羊刃，陽刃格也，剛烈之命，宜官煞制刃為貴。"
            desc_en = "Yueren (Sheep Blade) pattern: Month branch is Day master's Diwang stage. Fierce constitution requiring Official or Seven Killings to control."
        else:
            pattern = "建祿格"
            desc_zh = "月令同五行，日主得助，身強之命。"
            desc_en = "Month branch shares Day master element — strong constitution."
        return pattern, "正格", desc_zh, desc_en

    # 十神格局（使用模組級常數字典）
    if shishen in _SHISHEN_TO_PATTERN:
        name, zh, en = _SHISHEN_TO_PATTERN[shishen]
        return name, "正格", zh, en

    # 從格判斷（日主極弱，全局幾無比劫印）
    if strength_score <= 2.5:
        # 統計各五行勢力
        wx_counts: Dict[str, float] = {wx: 0.0 for wx in ["木", "火", "土", "金", "水"]}
        for s in all_stems:
            wx_counts[WUXING_TG[s]] += 1.0
        for b in all_branches:
            for cg in CANGGAN.get(b, []):
                wx_counts[WUXING_TG[cg]] += 0.5
        # 找最強五行（非日主）
        dominant_wx = max(
            {k: v for k, v in wx_counts.items() if k != dm_wx},
            key=lambda x: wx_counts[x]
        )
        dominant_ss_stems = [t for t in TIANGAN if WUXING_TG[t] == dominant_wx]
        if not dominant_ss_stems:
            return "普通格", "正格", "格局普通，依身強身弱取用。", "Ordinary pattern; use god based on strength."
        dominant_ss = _get_shishen(day_stem, dominant_ss_stems[0])
        if dominant_ss in _CONG_PATTERNS:
            name = _CONG_PATTERNS[dominant_ss]
            desc_zh = f"從格：日主極弱，從{dominant_ss}之勢，以{dominant_wx}為用，忌比劫印綬。"
            desc_en = f"Following pattern: Day master is extremely weak, following {dominant_ss}({dominant_wx}) force."
            return name, "從格", desc_zh, desc_en

    # 五行一氣格（專旺格）
    if strength_score >= 14 and dm_wx in _ZHUAN_WANG_PATTERN:
        name, zh, en = _ZHUAN_WANG_PATTERN[dm_wx]
        return name, "專旺格", zh, en

    return "普通格", "正格", "格局普通，依身強身弱取用。", "Ordinary pattern; use god based on strength."


# ──────────────────────────────────────────────────────────────────────────────
# 用神判斷（Use God Determination）
# 典籍：《子平真詮》「論用神」，《窮通寶鑑》（調候）
# ──────────────────────────────────────────────────────────────────────────────

def _determine_yongshen(
    day_stem: str,
    month_branch: str,
    strength: str,
    pattern: str,
    pattern_type: str,
    all_stems: List[str],
    all_branches: List[str],
) -> Tuple[str, str, str, str, str, str, str]:
    """判斷用神、喜神、忌神、調候用神。

    古典取用神三大原則（子平真詮）：
    1. 扶抑用神：身強抑之（取官殺財食傷），身弱扶之（取比劫印）
    2. 通關用神：兩組五行對峙，以通關之神化解
    3. 調候用神：依月令寒暖燥濕調節

    Returns:
        (用神五行, 喜神五行, 忌神五行, 仇神五行, 調候用神, 中文說明, 英文說明)
    """
    dm_wx = WUXING_TG[day_stem]

    # 從格：用神為所從之神
    if pattern_type == "從格":
        cong_wx_map = {
            "從財格": WUXING_KE[dm_wx],  # 財
            "從殺格": WUXING_KEME[dm_wx],  # 殺
            "從官格": WUXING_KEME[dm_wx],
            "從食格": WUXING_SHENG[dm_wx],  # 食傷
        }
        yong_wx = cong_wx_map.get(pattern, WUXING_SHENG[dm_wx])
        xi_wx = WUXING_SHENG[yong_wx] if WUXING_SHENG[yong_wx] != dm_wx else yong_wx
        ji_wx = dm_wx  # 日主本五行為忌
        jiao_wx = WUXING_SHENGME[dm_wx]  # 印也為忌
        tiao_wx = yong_wx
        zh = f"從格用神為{yong_wx}，忌日主{dm_wx}及印{jiao_wx}之氣。"
        en = f"Following pattern: Use god is {yong_wx}; avoid Day master element {dm_wx} and Seal {jiao_wx}."
        return yong_wx, xi_wx, ji_wx, jiao_wx, tiao_wx, zh, en

    # 專旺格
    if pattern_type == "專旺格":
        yong_wx = dm_wx
        xi_wx = WUXING_SHENGME[dm_wx]  # 生我之五行（印）
        ji_wx = WUXING_KEME[dm_wx]    # 克我之五行（官殺）
        jiao_wx = WUXING_KE[dm_wx]    # 我克之五行（財）
        tiao_wx = yong_wx
        zh = f"專旺格用神為{yong_wx}（比劫），忌{ji_wx}官殺及{jiao_wx}財星洩氣。"
        en = f"Specialized Vigor: Use god is {yong_wx} (Companions); avoid {ji_wx} Officials and {jiao_wx} Wealth."
        return yong_wx, xi_wx, ji_wx, jiao_wx, tiao_wx, zh, en

    # 扶抑用神（正格）
    is_strong = "強" in strength or strength == "中和"

    if is_strong:
        # 身強：以官殺（克身）、財星（耗身）、食傷（洩身）為用
        yong_wx = WUXING_KEME[dm_wx]   # 官殺（克我者）
        xi_wx = WUXING_KE[dm_wx]       # 財星（我克者，耗日主）
        ji_wx = dm_wx                   # 比劫（助身為忌）
        jiao_wx = WUXING_SHENGME[dm_wx]  # 印（生身為仇）
        tiao_wx = _tiaohoushen(day_stem, month_branch)
        zh = f"身強，宜以{yong_wx}官殺制身，或{xi_wx}財星耗洩，忌{ji_wx}比劫助旺。"
        en = f"Strong Day master: Use {yong_wx} (Officials) to restrain; {xi_wx} (Wealth) to drain. Avoid {ji_wx} (Companions) strengthening."
    else:
        # 身弱：以印（生身）、比劫（幫身）為用
        yong_wx = WUXING_SHENGME[dm_wx]  # 印（生我者）
        xi_wx = dm_wx                     # 比劫（同我者）
        ji_wx = WUXING_KEME[dm_wx]       # 官殺（克我為忌）
        jiao_wx = WUXING_KE[dm_wx]       # 財（洩印為仇）
        tiao_wx = _tiaohoushen(day_stem, month_branch)
        zh = f"身弱，宜以{yong_wx}印綬滋身，{xi_wx}比劫幫扶，忌{ji_wx}官殺克洩。"
        en = f"Weak Day master: Use {yong_wx} (Seal) to nourish; {xi_wx} (Companions) to support. Avoid {ji_wx} (Officials) weakening."

    return yong_wx, xi_wx, ji_wx, jiao_wx, tiao_wx, zh, en


def _tiaohoushen(day_stem: str, month_branch: str) -> str:
    """取調候用神（Climatic Adjustment God）。

    依月令寒暖燥濕，調節命局平衡。
    典籍：《窮通寶鑑》（余春台輯）

    Returns:
        調候用神五行
    """
    dm_wx = WUXING_TG[day_stem]
    # 寒冷月份（亥子丑）需火暖
    cold_branches = ["亥", "子", "丑"]
    # 炎熱月份（巳午未）需水潤
    hot_branches = ["巳", "午", "未"]
    # 燥月（辰戌）需水潤
    dry_branches = ["辰", "戌"]
    # 濕月（丑未）需火燥

    if month_branch in cold_branches:
        return "火"
    if month_branch in hot_branches:
        if dm_wx in ["金", "水"]:
            return "水"
        return "水"
    if month_branch in dry_branches:
        return "水"
    # 春月（寅卯辰）木旺，金水調候
    if month_branch in ["寅", "卯"]:
        return "金"
    # 秋月（申酉戌）金旺，火水調候
    if month_branch in ["申", "酉"]:
        return "火"
    return dm_wx  # 預設返回日主五行


# ──────────────────────────────────────────────────────────────────────────────
# 大運計算（Great Fortune Cycles）
# 典籍：《三命通會》卷三「論大運」
# ──────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=256)
def _find_nearest_jie(
    birth_year: int, birth_month: int, birth_day: int,
    forward: bool,
) -> Tuple[int, int, int, str]:
    """找到出生日期前後最近的「節」（月令節）。

    forward=True: 找下一個節（陽男陰女順行）
    forward=False: 找上一個節（陰男陽女逆行）

    Returns:
        (year, month, day, jieqi_name)
    """
    check_date = date(birth_year, birth_month, birth_day)
    step = timedelta(days=1) if forward else timedelta(days=-1)
    # 最多搜尋 90 天
    for _ in range(90):
        check_date += step
        try:
            cdate = fromSolar(check_date.year, check_date.month, check_date.day)
            if cdate.hasJieQi():
                jq_idx = cdate.getJieQi()
                jq_name = SXTWL_JIEQI[jq_idx]
                # 只取月令節（奇數索引）
                if jq_idx in MONTH_JIE_INDICES:
                    return check_date.year, check_date.month, check_date.day, jq_name
        except Exception:
            continue
    # 找不到時返回30天後/前
    fallback = date(birth_year, birth_month, birth_day) + (timedelta(days=30) if forward else timedelta(days=-30))
    return fallback.year, fallback.month, fallback.day, ""


def _compute_dayun(
    birth_year: int, birth_month: int, birth_day: int,
    year_stem: str, month_stem: str, month_branch: str,
    gender: str,
    reference_date: date,
) -> Tuple[str, float, date, List[DayunStep]]:
    """計算大運排盤。

    大運排法（子平正宗）：
    - 陽男陰女順行：以出生至下一個節的天數除以3得起運歲數
    - 陰男陽女逆行：以出生至上一個節的天數除以3得起運歲數
    - 從月柱順/逆推大運

    典籍：《三命通會》卷三「論起大運法」

    Returns:
        (方向描述, 起運歲數, 起運日期, 大運列表)
    """
    year_yang = YINYANG_TG[year_stem]
    is_male = (gender in ("男", "male", "m", "M"))

    # 陽男陰女順行；陰男陽女逆行
    forward = (year_yang and is_male) or (not year_yang and not is_male)
    direction = "順行" if forward else "逆行"

    # 找最近的節
    jie_y, jie_m, jie_d, jie_name = _find_nearest_jie(
        birth_year, birth_month, birth_day, forward=forward
    )
    jie_date = date(jie_y, jie_m, jie_d)
    birth_date_only = date(birth_year, birth_month, birth_day)
    days_diff = abs((jie_date - birth_date_only).days)
    start_age = days_diff / 3.0  # 傳統：3天≈1年

    # 起運日期（出生日 + days_diff 天，或 - days_diff 天）
    if forward:
        start_date = birth_date_only + timedelta(days=days_diff)
    else:
        start_date = birth_date_only + timedelta(days=days_diff)

    # 大運干支序列（從月柱順/逆推，每步一個月柱）
    month_gz = month_stem + month_branch
    steps: List[DayunStep] = []
    for i in range(10):
        if forward:
            gz = _jiazi_next(month_gz, i + 1)
        else:
            gz = _jiazi_prev(month_gz, i + 1)
        s = gz[0]
        b = gz[1]
        age_s = start_age + i * 10
        age_e = start_age + (i + 1) * 10

        # 起運年份
        dy_year = birth_year + int(age_s)
        dy_month = birth_month
        dy_day = birth_day
        try:
            dy_start_date = date(dy_year, dy_month, dy_day)
        except ValueError:
            dy_start_date = date(dy_year, dy_month, 28)

        steps.append(DayunStep(
            ganzhi=gz,
            stem=s,
            branch=b,
            age_start=round(age_s, 1),
            age_end=round(age_e, 1),
            year_start=dy_start_date.year,
            month_start=dy_start_date.month,
            day_start=dy_start_date.day,
        ))

    return direction, round(start_age, 1), start_date, steps


# ──────────────────────────────────────────────────────────────────────────────
# 神煞計算（Shen Sha Calculation）
# ──────────────────────────────────────────────────────────────────────────────

def _compute_shensha(
    day_stem: str,
    year_branch: str,
    month_branch: str,
    day_branch: str,
    hour_branch: str,
    day_gz: str,
) -> List[ShenSha]:
    """計算主要神煞。

    典籍：《三命通會》「論神煞」
    """
    shensha: List[ShenSha] = []
    all_branches = {
        "年": year_branch, "月": month_branch,
        "日": day_branch, "時": hour_branch,
    }
    all_pillars = list(all_branches.items())

    # 空亡
    kong1, kong2 = _get_kongwang(day_gz)
    for pname, b in all_pillars:
        if b in (kong1, kong2):
            shensha.append(ShenSha(
                name="空亡", name_en="Void (Kongwang)",
                pillar=pname, branch=b,
                is_auspicious=False,
                description_zh=f"{pname}柱{b}空亡，此宮所示事物虛而不實，有始無終。",
                description_en=f"{pname} pillar branch {b} is Void — affairs of this palace are insubstantial.",
            ))

    # 天乙貴人（以日干查）
    guiren_branches = TIANYI_GUIREN.get(day_stem, [])
    for pname, b in all_pillars:
        if b in guiren_branches:
            shensha.append(ShenSha(
                name="天乙貴人", name_en="Tianyi Noble Star",
                pillar=pname, branch=b,
                is_auspicious=True,
                description_zh=f"{pname}柱{b}坐天乙貴人，逢凶化吉，貴人扶持，官場得力。",
                description_en=f"{pname} pillar has Tianyi Noble — auspicious patron support and official favor.",
            ))

    # 文昌貴人
    wc = WENCHANG.get(day_stem, "")
    for pname, b in all_pillars:
        if b == wc:
            shensha.append(ShenSha(
                name="文昌貴人", name_en="Wenchang Literary Star",
                pillar=pname, branch=b,
                is_auspicious=True,
                description_zh=f"{pname}柱{b}逢文昌，聰明好學，文采出眾。",
                description_en=f"{pname} pillar has Wenchang — literary brilliance and academic talent.",
            ))

    # 驛馬（以年支或日支查，取四柱地支）
    for ref_name, ref_b in [("年", year_branch), ("日", day_branch)]:
        yima_b = YIMA.get(ref_b, "")
        for pname, b in all_pillars:
            if b == yima_b and pname != ref_name:
                shensha.append(ShenSha(
                    name="驛馬", name_en="Traveling Star (Yima)",
                    pillar=pname, branch=b,
                    is_auspicious=True,
                    description_zh=f"{pname}柱{b}逢驛馬，主奔波流動，遠行遷移，機變靈活。",
                    description_en=f"{pname} pillar has Yima — mobility, travel, and restless movement.",
                ))
                break

    # 桃花（以年支或日支查）
    for ref_b in [year_branch, day_branch]:
        th_b = TAOHUA.get(ref_b, "")
        for pname, b in all_pillars:
            if b == th_b:
                shensha.append(ShenSha(
                    name="桃花", name_en="Peach Blossom",
                    pillar=pname, branch=b,
                    is_auspicious=True,
                    description_zh=f"{pname}柱{b}逢桃花，面貌俊美，異性緣佳，情感豐富。",
                    description_en=f"{pname} pillar has Peach Blossom — attractive appearance and rich romantic life.",
                ))
                break

    # 將星（以年支查）
    js_b = JIANGXING.get(year_branch, "")
    for pname, b in all_pillars:
        if b == js_b:
            shensha.append(ShenSha(
                name="將星", name_en="General Star",
                pillar=pname, branch=b,
                is_auspicious=True,
                description_zh=f"{pname}柱{b}坐將星，具領袖氣質，掌管統御，逢之主貴。",
                description_en=f"{pname} pillar has General Star — leadership ability and commanding presence.",
            ))

    # 羊刃（陽干才論，以日干查月支）
    yr_b = YANGREN.get(day_stem, "")
    if month_branch == yr_b:
        shensha.append(ShenSha(
            name="月刃（羊刃）", name_en="Sheep Blade (Yangren)",
            pillar="月", branch=month_branch,
            is_auspicious=False,
            description_zh="月令逢羊刃，剛強有餘，性情激烈，宜以官殺制刃，化凶為吉。",
            description_en="Month branch is Sheep Blade — fierce and overbearing; Officials needed to control.",
        ))

    # 祿神
    lu_b = LUSHEN.get(day_stem, "")
    for pname, b in all_pillars:
        if b == lu_b:
            shensha.append(ShenSha(
                name="祿神", name_en="Official Salary Star",
                pillar=pname, branch=b,
                is_auspicious=True,
                description_zh=f"{pname}柱{b}坐祿神，衣食豐足，官祿亨通。",
                description_en=f"{pname} pillar has Lushen — abundance of food and official salary.",
            ))

    # 劫煞（以年支查）
    jiesha_b = JIESHA.get(year_branch, "")
    for pname, b in all_pillars:
        if b == jiesha_b:
            shensha.append(ShenSha(
                name="劫煞", name_en="Robbery Star",
                pillar=pname, branch=b,
                is_auspicious=False,
                description_zh=f"{pname}柱{b}逢劫煞，主破財、官非、意外，宜謹慎防範。",
                description_en=f"{pname} pillar has Robbery Star — risk of financial loss, legal trouble, accidents.",
            ))

    # 災煞（以年支查）
    zaisha_b = ZAISHA.get(year_branch, "")
    for pname, b in all_pillars:
        if b == zaisha_b:
            shensha.append(ShenSha(
                name="災煞", name_en="Calamity Star",
                pillar=pname, branch=b,
                is_auspicious=False,
                description_zh=f"{pname}柱{b}逢災煞，主疾病、災難，宜保重身體。",
                description_en=f"{pname} pillar has Calamity Star — illness and disasters; guard your health.",
            ))

    # 紅鸞天喜（以年支查）
    hl_b = HONGLUAN.get(year_branch, "")
    tx_b = TIANXI.get(year_branch, "")
    for pname, b in all_pillars:
        if b == hl_b:
            shensha.append(ShenSha(
                name="紅鸞", name_en="Red Phoenix",
                pillar=pname, branch=b,
                is_auspicious=True,
                description_zh=f"{pname}柱{b}逢紅鸞，婚緣喜慶，感情美滿。",
                description_en=f"{pname} pillar has Red Phoenix — marriage and romantic joy.",
            ))
        if b == tx_b:
            shensha.append(ShenSha(
                name="天喜", name_en="Heavenly Joy",
                pillar=pname, branch=b,
                is_auspicious=True,
                description_zh=f"{pname}柱{b}逢天喜，喜慶吉祥，逢凶化吉。",
                description_en=f"{pname} pillar has Heavenly Joy — celebrations and auspicious events.",
            ))

    return shensha


# ──────────────────────────────────────────────────────────────────────────────
# 沖合刑害計算（Interactions）
# ──────────────────────────────────────────────────────────────────────────────

def _compute_interactions(
    year_stem: str, year_branch: str,
    month_stem: str, month_branch: str,
    day_stem: str, day_branch: str,
    hour_stem: str, hour_branch: str,
) -> BaziInteractions:
    """計算四柱間的沖合刑害關係。"""
    branches = [
        ("年", year_branch), ("月", month_branch),
        ("日", day_branch), ("時", hour_branch),
    ]
    stems = [
        ("年", year_stem), ("月", month_stem),
        ("日", day_stem), ("時", hour_stem),
    ]
    all_b = [b for _, b in branches]

    liuhe_list = []
    for i in range(len(branches)):
        for j in range(i + 1, len(branches)):
            b1, b2 = branches[i][1], branches[j][1]
            key = (b1, b2)
            if key in LIUHE:
                liuhe_list.append((
                    f"{branches[i][0]}柱{b1}",
                    f"{branches[j][0]}柱{b2}",
                    LIUHE[key],
                ))

    # 三合
    sanhe_list = []
    for combo, wx in SANHE.items():
        present = [b for b in combo if b in all_b]
        if len(present) >= 2:
            pos = [f"{p}柱{b}" for p, b in branches if b in combo]
            sanhe_list.append((pos, wx))

    # 三會
    sanhui_list = []
    for combo, wx in SANHUI.items():
        present = [b for b in combo if b in all_b]
        if len(present) == 3:
            pos = [f"{p}柱{b}" for p, b in branches if b in combo]
            sanhui_list.append((pos, wx))

    # 六冲
    chong_list = []
    for i in range(len(branches)):
        for j in range(i + 1, len(branches)):
            b1, b2 = branches[i][1], branches[j][1]
            if LIUCHONG.get(b1) == b2:
                chong_list.append((
                    f"{branches[i][0]}柱{b1}",
                    f"{branches[j][0]}柱{b2}",
                ))

    # 六害
    hai_list = []
    for i in range(len(branches)):
        for j in range(i + 1, len(branches)):
            b1, b2 = branches[i][1], branches[j][1]
            if LIUHAI.get(b1) == b2:
                hai_list.append((
                    f"{branches[i][0]}柱{b1}",
                    f"{branches[j][0]}柱{b2}",
                ))

    # 三刑
    xing_list = []
    for group, xing_type in SANXING_GROUPS:
        if len(group) > 1:
            present = [b for b in group if b in all_b]
            if len(present) >= 2:
                pos = [f"{p}柱{b}" for p, b in branches if b in group]
                xing_list.append((pos, xing_type))
        else:  # 自刑
            cnt = all_b.count(group[0])
            if cnt >= 2:
                pos = [f"{p}柱{b}" for p, b in branches if b == group[0]]
                xing_list.append((pos, xing_type))

    # 天干相合
    tg_he_list = []
    for i in range(len(stems)):
        for j in range(i + 1, len(stems)):
            s1, s2 = stems[i][1], stems[j][1]
            key = (s1, s2)
            if key in TIANGAN_HE:
                tg_he_list.append((
                    f"{stems[i][0]}干{s1}",
                    f"{stems[j][0]}干{s2}",
                    TIANGAN_HE[key],
                ))

    return BaziInteractions(
        liuhe=liuhe_list,
        sanhe=sanhe_list,
        sanhui=sanhui_list,
        liuchong=chong_list,
        liuhai=hai_list,
        sanxing=xing_list,
        tiangan_he=tg_he_list,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 文字解讀（Textual Interpretation）
# ──────────────────────────────────────────────────────────────────────────────

def _generate_reading(
    chart: BaziChart,
) -> Tuple[str, str]:
    """生成古典風格文字解讀（中英雙語）。

    語言要求：典雅古風，引用典籍辭章。

    Returns:
        (中文解讀, 英文解讀)
    """
    yp = chart.year_pillar
    mp = chart.month_pillar
    dp = chart.day_pillar
    hp = chart.hour_pillar

    zh = f"""【子平八字命盤解讀】
【四柱命格】
　命主生於{chart.birth_year}年{chart.birth_month}月{chart.birth_day}日{chart.birth_hour}時，
　四柱干支：年柱{yp.ganzhi}、月柱{mp.ganzhi}、日柱{dp.ganzhi}、時柱{hp.ganzhi}。

【日主辨析】
　日主{chart.day_master}，五行屬{chart.day_master_wuxing}，月令{chart.month_pillar.branch}為{chart.day_master_vitality}，
　綜合評分{chart.day_master_strength_score}分，{chart.day_master_strength}。
　《滴天髓》云：「先觀月令，再察四柱，以定日主強弱。」

【格局論斷】
　命主格局為【{chart.pattern}】（{chart.pattern_type}），
　{chart.pattern_description_zh}

【用神取法】
　《子平真詮》取用神法：{chart.yongshen_description_zh}
　用神：{chart.yongshen}　喜神：{chart.xishen}　忌神：{chart.jishen}
　調候用神：{chart.tiaohoushen}

【大運排例】
　大運{chart.dayun_direction}，起運歲數約{chart.dayun_start_age}歲。
　首步大運：{chart.dayun_steps[0].ganzhi if chart.dayun_steps else '—'}，
　{chart.dayun_steps[0].age_start if chart.dayun_steps else '—'}歲至{chart.dayun_steps[0].age_end if chart.dayun_steps else '—'}歲。

【流年當運】
　當前流年：{chart.current_liunian}（{chart.current_liunian_year}年）。
　當前大運：{chart.current_dayun.ganzhi if chart.current_dayun else '—'}。

【神煞列舉】
"""
    for ss in chart.shensha_list[:6]:
        zh += f"　{ss.pillar}柱逢{ss.name}：{ss.description_zh}\n"

    zh += """
《淵海子平》有云：「八字者，命之根本，天地造化之所賦也。
五行生剋制化，皆在其中。知其旺衰，辨其格局，取其用神，
則命運之吉凶禍福，可以推算無遺矣。」"""

    en = f"""【Ziping Bazi Chart Reading】

【Four Pillars】
Born {chart.birth_year}/{chart.birth_month:02d}/{chart.birth_day:02d} at {chart.birth_hour:02d}:{chart.birth_minute:02d}
Year: {yp.ganzhi} | Month: {mp.ganzhi} | Day: {dp.ganzhi} | Hour: {hp.ganzhi}

【Day Master Analysis】
Day Master: {chart.day_master} ({chart.day_master_wuxing})
Month Branch: {chart.month_pillar.branch} — {chart.day_master_vitality} state
Strength Score: {chart.day_master_strength_score} → {chart.day_master_strength}

【Pattern (Gé Jú)】
{chart.pattern} ({chart.pattern_type})
{chart.pattern_description_en}

【Use God (Yòng Shén)】
{chart.yongshen_description_en}
Use God: {chart.yongshen} | Favorable: {chart.xishen} | Unfavorable: {chart.jishen}
Climatic Adjustment: {chart.tiaohoushen}

【Great Fortune Cycles】
Direction: {chart.dayun_direction} | Starts at age: {chart.dayun_start_age}
First cycle: {chart.dayun_steps[0].ganzhi if chart.dayun_steps else '—'} (age {chart.dayun_steps[0].age_start if chart.dayun_steps else '—'}–{chart.dayun_steps[0].age_end if chart.dayun_steps else '—'})

【Current Fortune】
Current Year: {chart.current_liunian} ({chart.current_liunian_year})
Current Great Fortune Cycle: {chart.current_dayun.ganzhi if chart.current_dayun else '—'}

"The Eight Characters are the root of destiny — Heaven and Earth's bestowment at birth.
Within the five elements' generation and restraint, all of fate is contained."
— Yuanhai Ziping (源海子平)"""

    return zh, en


# ──────────────────────────────────────────────────────────────────────────────
# 流年干支
# ──────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=256)
def _get_liunian_gz(year: int) -> str:
    """取某公曆年的流年干支（以立春為界）。

    使用 sxtwl 找到實際立春日期（通常為2月3–5日），
    以立春為歲首取年干支。若在預期範圍內未找到立春，
    退而搜尋整個2月，最終以2月4日作為保底。
    """
    # 立春通常落在 2月3–5日，擴大搜尋至 2月1–8日保險
    # _DEFAULT_LICHUN_DAY=4: 立春最常見於2月4日，用作搜尋失敗時的保底值
    _DEFAULT_LICHUN_DAY = 4
    found_day = _DEFAULT_LICHUN_DAY
    for d in range(1, 9):
        try:
            cdate = fromSolar(year, 2, d)
            if cdate.hasJieQi() and cdate.getJieQi() == 3:  # 3 = 立春
                found_day = d
                break
        except Exception:
            continue
    ref_date = fromSolar(year, 2, found_day)
    tg_raw = ref_date.getYearGZ(False)
    return TIANGAN[tg_raw.tg] + DIZHI[tg_raw.dz]


def _get_current_dayun(
    dayun_steps: List[DayunStep],
    birth_year: int,
    reference_year: int,
) -> Optional[DayunStep]:
    """取得當前所在的大運步。"""
    age = reference_year - birth_year
    for step in dayun_steps:
        if step.age_start <= age < step.age_end:
            return step
    return None


# ──────────────────────────────────────────────────────────────────────────────
# 主計算函式（Main Computation Function）
# ──────────────────────────────────────────────────────────────────────────────

def compute_bazi(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    gender: str = "男",
    timezone: float = 8.0,
    latitude: float = 25.033,
    longitude: float = 121.565,
    location_name: str = "",
    reference_date: Optional[date] = None,
) -> BaziChart:
    """計算完整子平八字命盤。

    嚴格依古法子平正宗推算，包含：
    - 四柱干支（以節氣為月令界）
    - 十神、長生、藏干
    - 日主強弱分析（古典旺相休囚死）
    - 格局（依月令取格，《子平真詮》法）
    - 用神喜忌神（扶抑、調候）
    - 大運（起運歲數精確計算，陽男陰女順行）
    - 流年
    - 神煞（天乙貴人、驛馬、桃花、空亡等）
    - 沖合刑害

    Args:
        year: 出生年（公曆）
        month: 出生月（公曆）
        day: 出生日（公曆）
        hour: 出生時（24小時制，0–23）
        minute: 出生分
        gender: 性別（「男」「女」）
        timezone: UTC 時差（如 8.0 = UTC+8）
        latitude: 出生地緯度
        longitude: 出生地經度
        location_name: 出生地名
        reference_date: 計算當前大運/流年的參考日期（預設今日）

    Returns:
        BaziChart 完整命盤資料

    Raises:
        ValueError: 出生日期超出 sxtwl 支援範圍
    """
    if reference_date is None:
        reference_date = date.today()

    # 計算四柱
    (y_stem, y_branch), (m_stem, m_branch), (d_stem, d_branch), (h_stem, h_branch) = \
        _compute_four_pillars(year, month, day, hour, minute)

    # 建立四柱物件
    year_pillar = _make_pillar(y_stem, y_branch, d_stem)
    month_pillar = _make_pillar(m_stem, m_branch, d_stem)
    day_pillar = _make_pillar(d_stem, d_branch, d_stem, label="日主")
    hour_pillar = _make_pillar(h_stem, h_branch, d_stem)
    day_pillar.shishen = "日主"

    # 日主分析
    dm = d_stem
    dm_wx = WUXING_TG[dm]
    dm_strength, dm_score, dm_vitality = _analyze_day_master_strength(
        dm, y_stem, y_branch, m_stem, m_branch, h_stem, h_branch
    )

    # 格局
    all_stems = [y_stem, m_stem, d_stem, h_stem]
    all_branches = [y_branch, m_branch, d_branch, h_branch]
    pattern, pattern_type, pattern_desc_zh, pattern_desc_en = _determine_pattern(
        dm, m_branch, all_stems, all_branches, dm_score
    )

    # 用神
    yong, xi, ji, jiao, tiao, yong_zh, yong_en = _determine_yongshen(
        dm, m_branch, dm_strength, pattern, pattern_type, all_stems, all_branches
    )

    # 大運
    direction, start_age, start_date, dayun_steps = _compute_dayun(
        year, month, day, y_stem, m_stem, m_branch, gender, reference_date
    )

    # 填入大運十神
    for step in dayun_steps:
        step.shishen_stem = _get_shishen(dm, step.stem)
        step.shishen_branch = "/".join([_get_shishen(dm, cg) for cg in CANGGAN.get(step.branch, [])])

    # 當前大運流年
    current_dayun = _get_current_dayun(dayun_steps, year, reference_date.year)
    current_liunian = _get_liunian_gz(reference_date.year)

    # 神煞
    day_gz = d_stem + d_branch
    shensha_list = _compute_shensha(
        dm, y_branch, m_branch, d_branch, h_branch, day_gz
    )

    # 沖合刑害
    interactions = _compute_interactions(
        y_stem, y_branch, m_stem, m_branch,
        d_stem, d_branch, h_stem, h_branch
    )

    # 建立命盤（暫時填入空解讀）
    chart = BaziChart(
        birth_year=year,
        birth_month=month,
        birth_day=day,
        birth_hour=hour,
        birth_minute=minute,
        gender=gender,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        year_pillar=year_pillar,
        month_pillar=month_pillar,
        day_pillar=day_pillar,
        hour_pillar=hour_pillar,
        day_master=dm,
        day_master_wuxing=dm_wx,
        day_master_strength=dm_strength,
        day_master_strength_score=dm_score,
        day_master_vitality=dm_vitality,
        pattern=pattern,
        pattern_type=pattern_type,
        pattern_description_zh=pattern_desc_zh,
        pattern_description_en=pattern_desc_en,
        yongshen=yong,
        xishen=xi,
        jishen=ji,
        jiaoshen=jiao,
        tiaohoushen=tiao,
        yongshen_description_zh=yong_zh,
        yongshen_description_en=yong_en,
        dayun_direction=direction,
        dayun_start_age=start_age,
        dayun_start_date=start_date,
        dayun_steps=dayun_steps,
        current_dayun=current_dayun,
        current_liunian=current_liunian,
        current_liunian_year=reference_date.year,
        shensha_list=shensha_list,
        interactions=interactions,
        reading_zh="",
        reading_en="",
        birth_datetime_str=f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}",
    )

    # 生成解讀
    reading_zh, reading_en = _generate_reading(chart)
    chart.reading_zh = reading_zh
    chart.reading_en = reading_en

    # 盲派分析整合（不阻斷主流程）
    try:
        from .bazi_blind_school_logic import BlindSchoolBazi
        chart.blind_school_report = BlindSchoolBazi.from_bazi_chart(chart).full_report()
    except (ImportError, ValueError, AttributeError, TypeError, KeyError) as e:
        chart.blind_school_report = {
            "error": f"blind_school_analysis_failed: {e}",
        }

    return chart


# ──────────────────────────────────────────────────────────────────────────────
# 測試命例（Classic Test Cases）
# ──────────────────────────────────────────────────────────────────────────────

TEST_CASES = [
    {
        "name": "毛澤東 (Mao Zedong)",
        "year": 1893, "month": 12, "day": 26,
        "hour": 7, "minute": 30,
        "gender": "男",
        "timezone": 8.0,
        "latitude": 27.9,
        "longitude": 112.55,
        "location_name": "湖南韶山",
        "expected_pillars": "癸巳 甲子 丁酉 甲辰",
        "note": "歷史名人典型命例，癸巳年甲子月丁酉日甲辰時",
    },
    {
        "name": "蔣中正 (Chiang Kai-shek)",
        "year": 1887, "month": 10, "day": 31,
        "hour": 0, "minute": 0,
        "gender": "男",
        "timezone": 8.0,
        "latitude": 29.87,
        "longitude": 121.55,
        "location_name": "浙江寧波",
        "expected_pillars": "丁亥 庚戌 己巳 甲子",
        "note": "歷史名人命例（sxtwl 計算）",
    },
    {
        "name": "示例現代命盤",
        "year": 1985, "month": 2, "day": 4,
        "hour": 10, "minute": 0,
        "gender": "男",
        "timezone": 8.0,
        "latitude": 39.9,
        "longitude": 116.4,
        "location_name": "北京",
        "expected_pillars": "乙丑 戊寅 甲戌 己巳",
        "note": "現代示例，立春日甲日主",
    },
]
