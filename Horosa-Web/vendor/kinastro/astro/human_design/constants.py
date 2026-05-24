# -*- coding: utf-8 -*-
"""
astro/human_design/constants.py — Human Design 人間圖常數定義

Core Human Design (Ra Uru Hu) constants:
  - 64 Gates → Rave Mandala zodiac position mapping
  - 36 Channels → gate-pair to center connection mapping
  - 9 Centers and their gate memberships
  - Types, Strategies, Authorities, Profiles
  - Incarnation Cross data

計算規則 / Calculation rules:
  - Gate mapping: 64 gates × 5.625° (360° / 64), starting with Gate 25 at 0° Aries
  - Line: floor(offset_within_gate / 0.9375°) + 1  (6 lines per gate)
  - Design chart offset: ~88 Solar Arc degrees ≈ 88 days before birth (pyswisseph bisection)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ============================================================
#  Rave Mandala gate sequence (from 0° Aries, clockwise)
# ============================================================
# The 64 gates are evenly distributed: each covers 5.625° (= 360/64).
# This is the sequence of gate numbers starting from 0° Aries (longitude 0°).
# gate = GATE_SEQUENCE[floor(longitude / 5.625)]
GATE_SEQUENCE: List[int] = [
    25, 17, 21, 51, 42,  3, 27, 24,  2, 23,  # 0°–56.25°
     8, 20, 16, 35, 45, 12, 15, 52, 39, 53,  # 56.25°–112.5°
    62, 56, 31, 33,  7,  4, 29, 59, 40, 64,  # 112.5°–168.75°
    47,  6, 46, 18, 48, 57, 32, 50, 28, 44,  # 168.75°–225°
     1, 43, 14, 34,  9,  5, 26, 11, 10, 58,  # 225°–281.25°
    38, 54, 61, 60, 41, 19, 13, 49, 30, 55,  # 281.25°–337.5°
    37, 63, 22, 36,                           # 337.5°–360°
]

# Degrees per gate and per line
DEGREES_PER_GATE: float = 360.0 / 64       # 5.625°
DEGREES_PER_LINE: float = DEGREES_PER_GATE / 6  # 0.9375°


def longitude_to_gate_line(longitude: float) -> Tuple[int, int]:
    """Convert ecliptic longitude (0–360°) to (gate_number, line_number 1–6).

    Args:
        longitude: Tropical ecliptic longitude in degrees [0, 360)

    Returns:
        (gate, line) where gate ∈ 1..64 and line ∈ 1..6
    """
    lon = longitude % 360.0
    slot = int(lon / DEGREES_PER_GATE)         # 0..63
    slot = min(slot, 63)                        # guard against float rounding at 360°
    gate = GATE_SEQUENCE[slot]
    offset_in_gate = lon - slot * DEGREES_PER_GATE
    line = int(offset_in_gate / DEGREES_PER_LINE) + 1
    line = min(max(line, 1), 6)
    return gate, line


# ============================================================
#  Centers — 9 Human Design centers and their gates
# ============================================================
CENTER_GATES: Dict[str, List[int]] = {
    "Head":         [64, 61, 63],
    "Ajna":         [47, 24,  4, 17, 43, 11],
    "Throat":       [62, 23, 56, 35, 12, 45, 33,  8, 31, 20, 16],
    "G":            [ 7,  1, 13, 10, 25, 15, 46,  2],
    "Ego":          [26, 40, 51, 21],
    "SolarPlexus":  [36, 22, 37,  6, 49, 55, 30],
    "Sacral":       [ 5, 14, 29, 59,  9,  3, 42, 27, 34],
    "Spleen":       [48, 57, 44, 50, 32, 28, 18],
    "Root":         [53, 60, 52, 19, 39, 41, 38, 54, 58],
}

# Reverse map: gate → center
GATE_TO_CENTER: Dict[int, str] = {
    g: center
    for center, gates in CENTER_GATES.items()
    for g in gates
}

# Chinese names for centers
CENTER_ZH: Dict[str, str] = {
    "Head":         "頭腦中心",
    "Ajna":         "Ajna 中心",
    "Throat":       "喉嚨中心",
    "G":            "G 中心（自我）",
    "Ego":          "自我/心臟中心",
    "SolarPlexus":  "太陽神經叢中心",
    "Sacral":       "薦骨中心",
    "Spleen":       "脾臟中心",
    "Root":         "根中心",
}

CENTER_EN: Dict[str, str] = {
    "Head":         "Head Center",
    "Ajna":         "Ajna Center",
    "Throat":       "Throat Center",
    "G":            "G Center (Self/Identity)",
    "Ego":          "Ego/Heart Center",
    "SolarPlexus":  "Solar Plexus Center",
    "Sacral":       "Sacral Center",
    "Spleen":       "Spleen/Splenic Center",
    "Root":         "Root Center",
}

# Motor centers (have energy to initiate action)
MOTOR_CENTERS = {"Ego", "SolarPlexus", "Sacral", "Root"}


# ============================================================
#  36 Channels — (gate_a, gate_b, center_a, center_b, name_en, name_zh)
# ============================================================
@dataclass(frozen=True)
class ChannelDef:
    gate_a: int
    gate_b: int
    name_en: str
    name_zh: str

    @property
    def gates(self) -> Tuple[int, int]:
        return (self.gate_a, self.gate_b)

    def __contains__(self, gate: int) -> bool:
        return gate == self.gate_a or gate == self.gate_b

    def partner(self, gate: int) -> int:
        """Return the partner gate of a given gate in this channel."""
        if gate == self.gate_a:
            return self.gate_b
        if gate == self.gate_b:
            return self.gate_a
        raise ValueError(f"Gate {gate} not in channel {self.gate_a}-{self.gate_b}")


CHANNELS: List[ChannelDef] = [
    # Head ↔ Ajna (3)
    ChannelDef( 4, 63, "Logic",          "邏輯通道"),
    ChannelDef(24, 61, "Awareness",       "意識通道"),
    ChannelDef(47, 64, "Abstraction",     "抽象通道"),
    # Ajna ↔ Throat (3)
    ChannelDef(11, 56, "Curiosity",       "好奇通道"),
    ChannelDef(17, 62, "Acceptance",      "接納通道"),
    ChannelDef(23, 43, "Structuring",     "結構通道"),
    # Throat ↔ G (4)
    ChannelDef( 1,  8, "Inspiration",     "靈感通道"),
    ChannelDef( 7, 31, "The Alpha",       "領導通道"),
    ChannelDef(13, 33, "The Prodigal",    "浪子通道"),
    ChannelDef(10, 20, "Awakening",       "覺醒通道"),      # Integration
    # Throat ↔ Solar Plexus (2)
    ChannelDef(12, 22, "Openness",        "開放通道"),
    ChannelDef(35, 36, "Transitoriness",  "短暫通道"),
    # Throat ↔ Ego (1)
    ChannelDef(21, 45, "The Money Line",  "財富通道"),
    # Throat ↔ Spleen (2)
    ChannelDef(16, 48, "The Wavelength",  "波長通道"),
    ChannelDef(20, 57, "Transmission",    "傳遞通道"),      # Integration
    # Throat ↔ Sacral (1)
    ChannelDef(20, 34, "Busy-ness",       "忙碌通道"),      # Integration
    # G ↔ Sacral (4)
    ChannelDef( 2, 14, "The Beat",        "節拍通道"),
    ChannelDef( 5, 15, "Rhythm",          "韻律通道"),
    ChannelDef(10, 34, "Exploration",     "探索通道"),      # Integration
    ChannelDef(29, 46, "Discovery",       "發現通道"),
    # G ↔ Spleen (1)
    ChannelDef(10, 57, "Perfected Form",  "完美形式通道"),  # Integration
    # G ↔ Ego (1)
    ChannelDef(25, 51, "Initiation",      "啟動通道"),
    # Ego ↔ Solar Plexus (1)
    ChannelDef(37, 40, "Community",       "社群通道"),
    # Ego ↔ Spleen (1)
    ChannelDef(26, 44, "Surrender",       "臣服通道"),
    # Solar Plexus ↔ Sacral (1)
    ChannelDef( 6, 59, "Mating",          "交配通道"),
    # Solar Plexus ↔ Root (3)
    ChannelDef(19, 49, "Synthesis",       "整合通道"),
    ChannelDef(30, 41, "Recognition",     "認可通道"),
    ChannelDef(39, 55, "Emoting",         "情緒通道"),
    # Sacral ↔ Spleen (2)
    ChannelDef(27, 50, "Preservation",    "保存通道"),
    ChannelDef(34, 57, "Power",           "力量通道"),      # Integration
    # Sacral ↔ Root (3)
    ChannelDef( 3, 60, "Mutation",        "突變通道"),
    ChannelDef( 9, 52, "Concentration",   "專注通道"),
    ChannelDef(42, 53, "Maturation",      "成熟通道"),
    # Spleen ↔ Root (3)
    ChannelDef(18, 58, "Judgment",        "判斷通道"),
    ChannelDef(28, 38, "Struggle",        "奮鬥通道"),
    ChannelDef(32, 54, "Transformation",  "轉化通道"),
]

# Fast lookup: gate → list of channels containing that gate
GATE_CHANNELS: Dict[int, List[ChannelDef]] = {}
for _ch in CHANNELS:
    for _g in (_ch.gate_a, _ch.gate_b):
        GATE_CHANNELS.setdefault(_g, []).append(_ch)


# ============================================================
#  Types, Strategies, Authorities
# ============================================================
TYPE_ZH = {
    "Manifestor":            "顯示者",
    "Generator":             "生產者",
    "Manifesting Generator": "顯示生產者",
    "Projector":             "投射者",
    "Reflector":             "反映者",
}

STRATEGY_ZH = {
    "To Inform":              "告知",
    "To Respond":             "回應",
    "To Respond + Inform":    "回應後告知",
    "To Wait for Invitation": "等待邀請",
    "To Wait & Reflect":      "等待與反映",
}

AUTHORITY_ZH = {
    "Emotional":       "情緒權威",
    "Sacral":          "薦骨權威",
    "Splenic":         "脾臟權威",
    "Ego Manifested":  "自我顯化權威",
    "Ego Projected":   "自我投射權威",
    "Self-Projected":  "自我投射權威（G中心）",
    "Environmental":   "環境權威",
    "Lunar":           "月亮權威",
    "None":            "無",
}

# Type → (Strategy, Not-Self Theme, Signature)
TYPE_INFO: Dict[str, Dict[str, str]] = {
    "Manifestor": {
        "strategy":     "To Inform",
        "not_self_zh":  "憤怒",
        "not_self_en":  "Anger",
        "signature_zh": "平靜",
        "signature_en": "Peace",
        "desc_zh": (
            "顯示者是人間圖五大類型中唯一有能力直接啟動和開始行動的人。"
            "他們不需要等待回應或邀請，但需要在行動前告知相關人員，以減少阻力。"
            "當顯示者跟隨「告知」策略時，會體驗到平靜（Signature）；"
            "當忽略策略時，會遭遇憤怒（Not-Self）。"
        ),
        "desc_en": (
            "Manifestors are the only type with the energy to initiate and start things. "
            "They don't need to wait for response or invitation, but need to inform "
            "others before acting to minimize resistance. "
            "When following the 'To Inform' strategy, they experience Peace (Signature); "
            "when ignoring it, they encounter Anger (Not-Self)."
        ),
    },
    "Generator": {
        "strategy":     "To Respond",
        "not_self_zh":  "挫折",
        "not_self_en":  "Frustration",
        "signature_zh": "滿足",
        "signature_en": "Satisfaction",
        "desc_zh": (
            "生產者是人口中最多的類型（約37%），擁有可持續的薦骨能量。"
            "他們最重要的能力是「回應」——等待生命中有什麼觸動他們的薦骨，"
            "而不是主動啟動。當生產者真正回應所熱愛的事，會感到深刻的滿足感。"
        ),
        "desc_en": (
            "Generators are the most common type (~37%), with sustainable Sacral energy. "
            "Their key ability is 'To Respond' — waiting for something in life to "
            "trigger their Sacral response, rather than initiating. "
            "When Generators respond to what they love, they feel deep Satisfaction."
        ),
    },
    "Manifesting Generator": {
        "strategy":     "To Respond + Inform",
        "not_self_zh":  "挫折與憤怒",
        "not_self_en":  "Frustration & Anger",
        "signature_zh": "滿足與平靜",
        "signature_en": "Satisfaction & Peace",
        "desc_zh": (
            "顯示生產者兼具生產者的薦骨回應能量與顯示者的喉嚨通道連接。"
            "他們行動迅速、可跳步、同時進行多任務。"
            "策略是先等待薦骨回應，回應後再告知相關人員，然後快速行動。"
        ),
        "desc_en": (
            "Manifesting Generators combine Generator's Sacral response energy with "
            "Manifestor's Throat-Motor connection. They move fast, skip steps, "
            "and multi-task naturally. "
            "Strategy: wait for Sacral response first, then inform others, then act."
        ),
    },
    "Projector": {
        "strategy":     "To Wait for Invitation",
        "not_self_zh":  "苦澀",
        "not_self_en":  "Bitterness",
        "signature_zh": "成功",
        "signature_en": "Success",
        "desc_zh": (
            "投射者約佔人口21%，沒有定義的薦骨中心，天生擅長引導和管理他人的能量。"
            "他們最重要的策略是「等待邀請」——特別是在重大人生決策（工作、關係、住所）上。"
            "當被真正邀請後發揮才能，投射者會體驗到成功的喜悅。"
        ),
        "desc_en": (
            "Projectors (~21% of population) have no defined Sacral, and are naturally "
            "gifted at guiding and managing others' energy. "
            "Their key strategy is 'Wait for Invitation', especially for major life decisions "
            "(work, relationships, home). When recognized and invited, Projectors experience Success."
        ),
    },
    "Reflector": {
        "strategy":     "To Wait & Reflect",
        "not_self_zh":  "失望",
        "not_self_en":  "Disappointment",
        "signature_zh": "驚喜",
        "signature_en": "Surprise",
        "desc_zh": (
            "反映者約佔人口1%，所有9個中心均未定義，是月亮週期（約29.5天）的反映者。"
            "他們如同社群的鏡子，能感知和反映周圍環境的健康狀況。"
            "重大決策需要等待完整的月亮週期，讓不同的月亮通道帶來不同視角後再做決定。"
        ),
        "desc_en": (
            "Reflectors (~1% of population) have all 9 centers undefined, "
            "reflecting the lunar cycle (~29.5 days). "
            "They are mirrors for their community, sensing and reflecting "
            "the health of their environment. "
            "Major decisions require waiting a full lunar cycle for diverse perspectives."
        ),
    },
}

# Authority descriptions
AUTHORITY_INFO: Dict[str, Dict[str, str]] = {
    "Emotional": {
        "desc_zh": "需要等待情緒波浪平穩後再做決定，不在情緒高峰或低谷時決策。「不確定時，就等一等。」",
        "desc_en": "Wait for emotional clarity — not during highs or lows. 'When in doubt, wait it out.'",
    },
    "Sacral": {
        "desc_zh": "聆聽薦骨的即時「嗯哼/嗯嗯」回應。只在直接問是/否問題時才有效。",
        "desc_en": "Listen to the immediate Sacral gut-response ('uh-huh / un-un'). Works only with direct yes/no questions.",
    },
    "Splenic": {
        "desc_zh": "信任脾臟的第一直覺。脾臟只說一次，需要活在當下才能聽到。",
        "desc_en": "Trust the first spontaneous intuitive hit. The Spleen speaks only once — stay present to hear it.",
    },
    "Ego Manifested": {
        "desc_zh": "從內心真實的欲望和意志力做決定。問自己：「我真正想要什麼？」",
        "desc_en": "Decide from genuine heart desire and willpower. Ask: 'What do I really want?'",
    },
    "Ego Projected": {
        "desc_zh": "等待被邀請後，用心裡真正想說的話來回應。需要他人的認可和邀請。",
        "desc_en": "Wait for invitation, then respond from the heart. Needs recognition and invitation from others.",
    },
    "Self-Projected": {
        "desc_zh": "透過大聲說話來找到真相。需要可信任的傾聽者來幫助釐清方向。",
        "desc_en": "Find truth by talking it out. Needs trusted listeners to help clarify direction.",
    },
    "Environmental": {
        "desc_zh": "需要在正確的環境和與對的人交流後才能做決定，是外在的過程而非內在的。",
        "desc_en": "Decisions emerge through the right environment and conversations — an outer process, not inner.",
    },
    "Lunar": {
        "desc_zh": "等待完整的月亮週期（約29.5天），在不同時機與不同的人討論後做決定。",
        "desc_en": "Wait a full lunar cycle (~29.5 days), discussing with different people at different times.",
    },
}


# ============================================================
#  Profiles (12 Profiles = combination of 6 lines)
# ============================================================
PROFILE_INFO: Dict[str, Dict[str, str]] = {
    "1/3": {"name_zh": "研究者/殉道者",    "name_en": "Investigator/Martyr",        "theme_zh": "安全感基礎 + 透過試誤學習"},
    "1/4": {"name_zh": "研究者/機會主義者", "name_en": "Investigator/Opportunist",   "theme_zh": "安全感基礎 + 透過人際網絡"},
    "2/4": {"name_zh": "隱士/機會主義者",   "name_en": "Hermit/Opportunist",         "theme_zh": "天賦自然流露 + 人際關係網絡"},
    "2/5": {"name_zh": "隱士/異端",        "name_en": "Hermit/Heretic",             "theme_zh": "天賦自然流露 + 實際解決方案"},
    "3/5": {"name_zh": "殉道者/異端",      "name_en": "Martyr/Heretic",             "theme_zh": "透過試誤 + 實際解決方案"},
    "3/6": {"name_zh": "殉道者/榜樣",      "name_en": "Martyr/Role Model",          "theme_zh": "透過試誤 + 三階段人生旅程"},
    "4/6": {"name_zh": "機會主義者/榜樣",  "name_en": "Opportunist/Role Model",     "theme_zh": "人際網絡基礎 + 三階段人生旅程"},
    "4/1": {"name_zh": "機會主義者/研究者", "name_en": "Opportunist/Investigator",   "theme_zh": "人際網絡 + 安全感基礎"},
    "5/1": {"name_zh": "異端/研究者",      "name_en": "Heretic/Investigator",       "theme_zh": "實際解決方案 + 安全感基礎"},
    "5/2": {"name_zh": "異端/隱士",        "name_en": "Heretic/Hermit",             "theme_zh": "實際解決方案 + 天賦自然流露"},
    "6/2": {"name_zh": "榜樣/隱士",        "name_en": "Role Model/Hermit",          "theme_zh": "三階段人生旅程 + 天賦自然流露"},
    "6/3": {"name_zh": "榜樣/殉道者",      "name_en": "Role Model/Martyr",          "theme_zh": "三階段人生旅程 + 透過試誤"},
}

# 12 valid profile combinations (Personality Sun line / Design Sun line)
# Opposite lines: 1↔4, 2↔5, 3↔6, 4↔1, 5↔2, 6↔3
OPPOSITE_LINE = {1: 4, 2: 5, 3: 6, 4: 1, 5: 2, 6: 3}

VALID_PROFILES = set(PROFILE_INFO.keys())


# ============================================================
#  Definition types
# ============================================================
DEFINITION_ZH = {
    "Single":       "單一定義",
    "Split":        "分割定義",
    "Triple Split":  "三重分割",
    "Quad Split":   "四重分割",
    "No Definition": "無定義",
}

DEFINITION_EN = {
    "Single":       "Single Definition",
    "Split":        "Split Definition",
    "Triple Split":  "Triple Split Definition",
    "Quad Split":   "Quad Split Definition",
    "No Definition": "No Definition (Reflector)",
}


# ============================================================
#  Planets used for HD chart (Personality + Design)
# ============================================================
HD_PLANET_NAMES = [
    "Sun", "Earth", "North Node", "South Node",
    "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
]

# pyswisseph planet IDs (Earth = calculated as Sun + 180°)
import swisseph as swe  # noqa: E402
SWE_PLANET_IDS: Dict[str, int] = {
    "Sun":        swe.SUN,
    "Moon":       swe.MOON,
    "Mercury":    swe.MERCURY,
    "Venus":      swe.VENUS,
    "Mars":       swe.MARS,
    "Jupiter":    swe.JUPITER,
    "Saturn":     swe.SATURN,
    "Uranus":     swe.URANUS,
    "Neptune":    swe.NEPTUNE,
    "Pluto":      swe.PLUTO,
    "North Node": swe.TRUE_NODE,
}

PLANET_ZH: Dict[str, str] = {
    "Sun":        "太陽",
    "Earth":      "地球",
    "North Node": "北交點",
    "South Node": "南交點",
    "Moon":       "月亮",
    "Mercury":    "水星",
    "Venus":      "金星",
    "Mars":       "火星",
    "Jupiter":    "木星",
    "Saturn":     "土星",
    "Uranus":     "天王星",
    "Neptune":    "海王星",
    "Pluto":      "冥王星",
}


# ============================================================
#  Incarnation Cross base data (simplified — Sun/Earth gates at 0°/180°)
# ============================================================
# A full cross has 4 gates: Personality Sun, Personality Earth,
# Design Sun, Design Earth.
# The "Right/Left/Juxtaposition" angle is determined by the Sun gate line.
# Lines 1-3 → Right Angle Cross; Line 4 → Juxtaposition; Lines 5-6 → Left Angle Cross
CROSS_ANGLE_BY_LINE: Dict[int, str] = {
    1: "Right Angle",
    2: "Right Angle",
    3: "Right Angle",
    4: "Juxtaposition",
    5: "Left Angle",
    6: "Left Angle",
}

CROSS_ANGLE_ZH = {
    "Right Angle":   "右角度",
    "Juxtaposition": "並列",
    "Left Angle":    "左角度",
}


# ============================================================
#  Example birth data for testing
# ============================================================
EXAMPLE_CHARTS = [
    {
        "name": "Ra Uru Hu (Alan Robert Krakower)",
        "year": 1948, "month": 4, "day": 9,
        "hour": 8, "minute": 0,
        "timezone": -5.0,
        "latitude": 45.5017, "longitude": -73.5673,
        "location_name": "Montreal, Canada",
    },
    {
        "name": "Example — Generator",
        "year": 1985, "month": 3, "day": 15,
        "hour": 14, "minute": 30,
        "timezone": 8.0,
        "latitude": 25.033, "longitude": 121.565,
        "location_name": "Taipei, Taiwan",
    },
    {
        "name": "Example — Projector",
        "year": 1990, "month": 7, "day": 22,
        "hour": 6, "minute": 45,
        "timezone": 8.0,
        "latitude": 22.3193, "longitude": 114.1694,
        "location_name": "Hong Kong",
    },
]
