"""
astro/rectification/constants.py — 出生時間校正常量與評分權重

Birth Chart Rectification Constants & Scoring Weights

Classical references:
  - Vettius Valens, Anthology (2nd century CE) — Lots, Zodiacal Releasing
  - William Lilly, Christian Astrology (1647) — Primary Directions to Angles
  - Jean-Baptiste Morin (Morinus), Astrologia Gallica (1661) — Direction theory
  - Robert Hand, Planets in Transit — Modern transits
  - Bernadette Brady, Predictive Astrology — Multiple technique integration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

# ============================================================
# 評分權重 (Scoring Weights)
# ============================================================
# Primary Directions to angles carry the highest classical authority.
# Ref: Lilly, Christian Astrology III; Morinus, Astrologia Gallica XVIII.

TECHNIQUE_WEIGHTS: Dict[str, float] = {
    "primary_direction": 5.0,    # 初級方向：最高權重（Lilly, Valens）
    "solar_arc": 3.5,            # 太陽弧：強度次之（Witte, Ebertin）
    "secondary_progression": 3.0, # 次進法：一天一年（古典傳承）
    "profection": 2.5,           # 流年小限：Valens 推薦
    "zodiacal_releasing": 2.0,   # 黃道釋放：Valens Anthology VII
    "transit_outer": 2.0,        # 外行星過境：木土天海冥
    "transit_inner": 1.0,        # 內行星過境：日月水金火
}

# Bonus multipliers for angle/luminary involvement
# Ref: Lilly, CA I.7 — "Angles are seats of power"
ANGLE_BONUS: float = 2.0        # 涉及 ASC/MC/DSC/IC 的方向加倍
LUMINARY_BONUS: float = 1.5     # 涉及日/月的方向加成 1.5x
ANGULAR_HOUSE_BONUS: float = 1.3  # 行星在角宮（1/4/7/10）加成

# Orb used when matching directed planets to event dates (in years)
EVENT_ORB_YEARS: float = 1.5    # 事件與方向弧觸發年份允許誤差（年）

# Candidate time step (minutes) for brute-force search
CANDIDATE_STEP_MINUTES: int = 4   # 每 4 分鐘一個候選時間

# Default search window (minutes either side of given birth time)
DEFAULT_SEARCH_WINDOW_MINUTES: int = 120   # ±2 小時

# ============================================================
# 技術說明字典 (Technique Descriptions)
# ============================================================

TECHNIQUE_INFO: Dict[str, Dict[str, str]] = {
    "primary_direction": {
        "zh_name": "初級方向 Primary Directions",
        "zh_desc": (
            "初級方向是古典占星校正最重要的技術。天球每日自轉 1° 對應人生 1 年，"
            "上升點（ASC）和中天（MC）對本命行星的方向弧直接對應重大生命事件。"
            "源自 Ptolemy《Tetrabiblos》，William Lilly《Christian Astrology》完整記錄，"
            "Placidus、Regiomontanus 發展宮位制算法。"
        ),
        "en_desc": (
            "Primary Directions are the most authoritative classical rectification technique. "
            "The celestial sphere rotates ~1°/day = 1 year of life. Directions of ASC/MC "
            "to natal planets time major life events with high precision. "
            "Ref: Ptolemy Tetrabiblos III.10; Lilly Christian Astrology III."
        ),
        "weight_label": "5.0×",
    },
    "solar_arc": {
        "zh_name": "太陽弧方向 Solar Arc Directions",
        "zh_desc": (
            "太陽弧以太陽每年推進的弧度（≈1°）統一移動所有行星和宮位軸，"
            "是現代占星最廣泛使用的推進技術。"
            "Reinhold Ebertin 的相位組合（Cosmobiology）大量應用此技術，"
            "弧到角宮是強力的時間指標。"
        ),
        "en_desc": (
            "Solar Arc moves all planets and angles by the Sun's yearly arc (~1°). "
            "When directed planets or angles hit natal significators, they time events. "
            "Ref: Reinhold Ebertin, The Combination of Stellar Influences (1940)."
        ),
        "weight_label": "3.5×",
    },
    "secondary_progression": {
        "zh_name": "次進法 Secondary Progressions",
        "zh_desc": (
            "一天一年法：出生後第 N 天的星象對應人生第 N 年的趨勢。"
            "次進月亮（SP Moon）每月移動約 1° 是最精確的校正工具，"
            "能精確到出生時間的分鐘級別。"
            "Placidus《Primum Mobile》、Sepharial 詳細闡述此法。"
        ),
        "en_desc": (
            "Day-for-a-year progressions: the chart cast for N days after birth "
            "describes themes for life year N. Progressed Moon timing is particularly "
            "sensitive to exact birth time — ideal for fine-tuning to the minute. "
            "Ref: Sepharial, Primary Directions Made Easy (1898)."
        ),
        "weight_label": "3.0×",
    },
    "profection": {
        "zh_name": "流年小限 Annual Profections",
        "zh_desc": (
            "Vettius Valens《Anthology》核心技術：上升點每年順行一宮，"
            "每12年循環一次，激活該宮主星為「流年時間主星」。"
            "時間主星所在宮位及其相位揭示該年的核心主題，"
            "是古典希臘校正最簡便有效的工具。"
        ),
        "en_desc": (
            "Vettius Valens' core timing technique from the Anthology: the Ascendant "
            "moves one sign per year, activating that sign's ruler as Time Lord. "
            "The Time Lord's natal placement reveals yearly themes. "
            "Ref: Valens, Anthology IV.1–3 (2nd century CE)."
        ),
        "weight_label": "2.5×",
    },
    "zodiacal_releasing": {
        "zh_name": "黃道釋放 Zodiacal Releasing",
        "zh_desc": (
            "源自 Valens《Anthology》的多層期間系統，從福點（Lot of Fortune）"
            "或靈點（Lot of Spirit）起始，按星座小限年計算 L1/L2/L3 週期。"
            "「鬆脫期」（Loosing of the Bond）是生命最重要的轉折點。"
            "校正時可比對重大事件是否落在鬆脫期附近。"
        ),
        "en_desc": (
            "Valens' multi-level period system from the Lot of Fortune or Spirit. "
            "L1/L2/L3 periods calculated from sign minor years. The 'Loosing of the Bond' "
            "marks life's most pivotal transitions — ideal rectification markers. "
            "Ref: Valens, Anthology IV.1, VII.6."
        ),
        "weight_label": "2.0×",
    },
    "transit": {
        "zh_name": "行星過境 Transits",
        "zh_desc": (
            "外行星（木星、土星、天王星、海王星、冥王星）與本命行星及角宮的合衝刑三，"
            "提供粗略的時間確認（年度級別）。"
            "土星過境角宮對應重大人生階段；木星合本命 ASC 對應起始與發展。"
            "Robert Hand《Planets in Transit》是現代標準參考。"
        ),
        "en_desc": (
            "Outer planet transits (Jupiter, Saturn, Uranus, Neptune, Pluto) "
            "to natal planets and angles provide broad year-level timing confirmation. "
            "Saturn transits to angles mark life phases; Jupiter-ASC marks new beginnings. "
            "Ref: Robert Hand, Planets in Transit (1976)."
        ),
        "weight_label": "1–2×",
    },
}

# ============================================================
# 生命事件類別 (Life Event Categories)
# ============================================================
# Used for AI-assisted event suggestion and weighted matching

EVENT_CATEGORIES: Dict[str, Dict[str, str]] = {
    "marriage": {
        "zh": "婚姻/伴侶關係",
        "en": "Marriage / Partnership",
        "emoji": "💍",
        "key_planets": ["Venus", "Moon", "Jupiter", "ASC", "DSC"],
        "key_houses": [7, 1, 5, 11],
    },
    "career_peak": {
        "zh": "事業高峰 / 升職",
        "en": "Career Peak / Promotion",
        "emoji": "📈",
        "key_planets": ["Sun", "Saturn", "Jupiter", "MC"],
        "key_houses": [10, 1, 6],
    },
    "birth_child": {
        "zh": "子女出生",
        "en": "Birth of Child",
        "emoji": "👶",
        "key_planets": ["Moon", "Jupiter", "Venus"],
        "key_houses": [5, 1, 4],
    },
    "death_parent": {
        "zh": "父母離世",
        "en": "Death of Parent",
        "emoji": "🕯️",
        "key_planets": ["Saturn", "Moon", "Sun"],
        "key_houses": [4, 8, 12],
    },
    "relocation": {
        "zh": "移居 / 重大搬遷",
        "en": "Relocation / Major Move",
        "emoji": "✈️",
        "key_planets": ["Jupiter", "Uranus", "Moon", "Mercury"],
        "key_houses": [9, 4, 3],
    },
    "health_crisis": {
        "zh": "重大健康危機",
        "en": "Major Health Crisis",
        "emoji": "🏥",
        "key_planets": ["Saturn", "Mars", "Sun", "Moon"],
        "key_houses": [6, 8, 12],
    },
    "business_start": {
        "zh": "創業 / 重大事業開始",
        "en": "Business Start / Major Venture",
        "emoji": "🚀",
        "key_planets": ["Sun", "Mars", "Jupiter", "Uranus"],
        "key_houses": [1, 10, 2],
    },
    "divorce": {
        "zh": "離婚 / 重大感情結束",
        "en": "Divorce / Major Breakup",
        "emoji": "💔",
        "key_planets": ["Saturn", "Mars", "Uranus", "Venus"],
        "key_houses": [7, 8, 12],
    },
    "financial_gain": {
        "zh": "重大財富增長",
        "en": "Major Financial Gain",
        "emoji": "💰",
        "key_planets": ["Jupiter", "Venus", "Sun"],
        "key_houses": [2, 8, 11],
    },
    "financial_loss": {
        "zh": "重大財務損失",
        "en": "Major Financial Loss",
        "emoji": "📉",
        "key_planets": ["Saturn", "Neptune", "Pluto"],
        "key_houses": [2, 8, 12],
    },
    "education": {
        "zh": "教育 / 考試 / 入學",
        "en": "Education / Exam / Enrollment",
        "emoji": "🎓",
        "key_planets": ["Jupiter", "Mercury", "Saturn"],
        "key_houses": [9, 3, 1],
    },
    "accident": {
        "zh": "意外事故",
        "en": "Accident / Sudden Event",
        "emoji": "⚡",
        "key_planets": ["Mars", "Uranus", "Saturn"],
        "key_houses": [1, 8, 12],
    },
    "other": {
        "zh": "其他重大事件",
        "en": "Other Major Event",
        "emoji": "⭐",
        "key_planets": ["Sun", "Moon", "Saturn", "Jupiter"],
        "key_houses": [1, 4, 7, 10],
    },
}

# ============================================================
# AI 提示建議 (AI-Assisted Event Suggestions)
# ============================================================

AI_EVENT_SUGGESTIONS: List[Dict[str, str]] = [
    {"zh": "💍 建議補充：有無結婚或長期同居關係？", "en": "💍 Suggested: Any marriage or long-term partnership?"},
    {"zh": "👶 建議補充：有無子女出生事件？", "en": "👶 Suggested: Any birth of children?"},
    {"zh": "📈 建議補充：有無升職、創業或重大事業轉折？", "en": "📈 Suggested: Any major career milestone?"},
    {"zh": "🏥 建議補充：有無重大健康危機或手術？", "en": "🏥 Suggested: Any major health crisis or surgery?"},
    {"zh": "✈️ 建議補充：有無重大移居或出國定居？", "en": "✈️ Suggested: Any major relocation abroad?"},
    {"zh": "🕯️ 建議補充：有無父母或至親的離世？", "en": "🕯️ Suggested: Any death of a parent or close relative?"},
    {"zh": "💔 建議補充：有無離婚或重大感情破裂？", "en": "💔 Suggested: Any divorce or major breakup?"},
    {"zh": "📉 建議補充：有無重大財務損失或破產？", "en": "📉 Suggested: Any major financial loss or bankruptcy?"},
]

# ============================================================
# 歷史校正介紹 (Historical Rectification Introduction)
# ============================================================

RECTIFICATION_HISTORY: Dict[str, str] = {
    "zh": """
**出生時間校正（Rectification）** 是占星術中技術要求最高的工作之一——通過分析一個人的重大生命事件，
反推最精確的出生時間。

### 古典時期（Hellenistic）
Vettius Valens（公元 2 世紀）在《Anthology》中記載了使用**流年小限（Profections）**
和**黃道釋放（Zodiacal Releasing）**作為時間確認工具的方法。
Ptolemy 在《Tetrabiblos》III.3 描述了以**太陽弧**和**角宮方向**進行校正的基本原理。

### 中世紀與文藝復興
William Lilly（1647）在《Christian Astrology》第三冊詳細記錄了**初級方向到角宮**的校正技術，
主張 ASC 和 MC 對本命行星的方向精確對應人生事件。
Guido Bonatus（13 世紀）和 Jean-Baptiste Morin（Morinus，1661）進一步完善了計算體系。

### 現代演化
Alan Leo、Sepharial 推廣了**次進法（Secondary Progressions）**；
Reinhold Ebertin 發展了**太陽弧（Solar Arcs）**在校正中的應用；
Noel Tyl、Bernadette Brady 則整合多種技術形成系統性校正框架。

### 本工具的方法
本校正引擎結合六種預測技術，以加權評分對候選出生時間進行排名，
初級方向到角宮賦予最高權重，輔以太陽弧、次進法、流年小限及過境進行交叉驗證。
""",
    "en": """
**Birth Chart Rectification** is among the most technically demanding tasks in astrology —
inferring the precise birth time by matching a person's major life events
against astrological timing techniques.

### Hellenistic Period
Vettius Valens (2nd century CE) in the *Anthology* used **Annual Profections**
and **Zodiacal Releasing** as timing confirmation tools.
Ptolemy's *Tetrabiblos* III.3 describes rectification using solar arcs and angular directions.

### Medieval & Renaissance
William Lilly (1647) in *Christian Astrology* Book III detailed **Primary Directions to Angles**,
asserting that directions of ASC/MC to natal planets precisely time life events.
Guido Bonatus (13th c.) and Jean-Baptiste Morin (Morinus, 1661) refined the calculation systems.

### Modern Evolution
Alan Leo and Sepharial popularized **Secondary Progressions**;
Reinhold Ebertin developed **Solar Arcs** for rectification;
Noel Tyl and Bernadette Brady integrated multiple techniques into systematic frameworks.

### This Tool's Approach
The engine combines six predictive techniques with weighted scoring to rank candidate birth times.
Primary Directions to angles carry the highest weight, cross-validated with Solar Arcs,
Secondary Progressions, Profections, Zodiacal Releasing, and major Transits.
""",
}

# ============================================================
# 行星名稱映射 (Planet Name Mappings)
# ============================================================
# Map between different naming conventions used across modules

PLANET_NAMES_SHORT: Dict[str, str] = {
    "Sun ☉": "Sun",
    "Moon ☽": "Moon",
    "Mercury ☿": "Mercury",
    "Venus ♀": "Venus",
    "Mars ♂": "Mars",
    "Jupiter ♃": "Jupiter",
    "Saturn ♄": "Saturn",
    "Uranus ♅": "Uranus",
    "Neptune ♆": "Neptune",
    "Pluto ♇": "Pluto",
}

PLANET_NAMES_DISPLAY: Dict[str, str] = {v: k for k, v in PLANET_NAMES_SHORT.items()}

PLANET_CHINESE: Dict[str, str] = {
    "Sun": "太陽", "Moon": "月亮", "Mercury": "水星", "Venus": "金星",
    "Mars": "火星", "Jupiter": "木星", "Saturn": "土星",
    "Uranus": "天王星", "Neptune": "海王星", "Pluto": "冥王星",
    "ASC": "上升點", "MC": "中天", "DSC": "下降點", "IC": "天底",
}

# Outer planets for transit matching (high impact)
# Note: populated in calculator.py using swisseph IDs to avoid import at module load

# Precision threshold for arcsine clamp (avoids domain errors near ±1).
# Exported for use in calculator.py; the underscore prefix is a package-internal
# convention (not strict private) since it has no useful meaning to end users.
_ASIN_CLAMP: float = 0.9999

# Max orb (in degrees) for Secondary Progression hits
SECONDARY_PROGRESSION_MAX_ORB: float = 0.8

# "Loosing of the Bond" window: event within this many years of a ZR boundary
ZR_LOOSING_THRESHOLD_YEARS: float = 1.0

# Score threshold for "confident" candidate (percentage)
CONFIDENCE_HIGH: float = 70.0
CONFIDENCE_MEDIUM: float = 45.0
CONFIDENCE_LOW: float = 25.0

# Visual theme colours matching the app dark theme
RECT_GOLD: str = "#EAB308"
RECT_PURPLE: str = "#A78BFA"
RECT_BLUE: str = "#3B82F6"
RECT_TEAL: str = "#6EE7B7"
RECT_ORANGE: str = "#F97316"
RECT_CRIMSON: str = "#EF4444"
RECT_BG_DARK: str = "rgba(10,8,30,0.97)"
RECT_BORDER: str = "rgba(167,139,250,0.25)"
