"""
astro/trutine_of_hermes/constants.py — 赫密士出生前世盤常量

Classical Trutine of Hermes / Prenatal Epoch Constants

Historical references:
  - Hermes Trismegistus (attributed) — original Trutine rule
  - Ptolemy, *Centiloquium* (Karpos), Aphorism 51 (2nd c. CE)
  - Ptolemy, *Tetrabiblos* IV.9 — gestation and birth
  - E.H. Bailey, *The Prenatal Epoch* (1916) — most complete modern treatment
  - Sepharial (W.R. Old), *The Solar Epoch* (1913)
  - E. Selin, *The Prenatal Epoch* in Encyclopaedia of the History of Science
  - Nicholas deVore, *Encyclopedia of Astrology* (1947) — summary of rules
  - David Cochrane, modern computational verification
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# ============================================================
# Gestation Period Constants
# ============================================================
# The classical gestation is 273 days (approximately 9 lunar months).
# Bailey distinguishes between two gestation lengths based on
# Moon phase at birth:
#
# Ref: Bailey, The Prenatal Epoch (1916), Chapter III.

GESTATION_DAYS_STANDARD: float = 273.0
"""Standard gestation period in days (approximately 9 lunar months).
Ref: Bailey (1916), Ptolemy Tetrabiblos IV.9."""

GESTATION_DAYS_SHORT: float = 257.0
"""Shorter gestation variant (~8.5 lunar months) for certain cases.
Ref: Bailey (1916), Chapter III; some texts cite 258 days."""

GESTATION_DAYS_LONG: float = 289.0
"""Longer gestation variant (~9.5 lunar months).
Ref: Bailey (1916), Chapter III; some texts cite 288 days."""

# Approximate gestation range to search around (±days from standard)
GESTATION_SEARCH_RANGE_DAYS: float = 20.0

# Fine-search step in minutes for finding the exact Epoch moment
EPOCH_SEARCH_STEP_MINUTES: float = 4.0

# Maximum iteration count to avoid infinite loops
MAX_EPOCH_ITERATIONS: int = 5000

# ============================================================
# Trutine Core Rule
# ============================================================
# The Trutine of Hermes states a reciprocal relationship between
# the Natal and Epoch charts:
#
#   If Moon is ABOVE the horizon at birth (i.e., in houses 7–12):
#       Moon at Birth  →  Ascendant at Epoch
#       Ascendant at Birth  →  Moon at Epoch
#
#   If Moon is BELOW the horizon at birth (i.e., in houses 1–6):
#       Moon at Birth  →  Descendant at Epoch
#       Descendant at Birth  →  Moon at Epoch  (some variants)
#
# Waxing Moon refinement (Bailey):
#   - Waxing + above horizon: Moon at birth = ASC at Epoch
#   - Waxing + below horizon: Moon at birth = DSC at Epoch
#   - Waning + above horizon: Moon at birth = ASC at Epoch  (same)
#   - Waning + below horizon: Moon at birth = DSC at Epoch  (same)
#
# The primary rule is purely based on horizon position.
# Ref: Bailey (1916), Chapter II; Ptolemy Centiloquium Aphorism 51.

TRUTINE_RULE: Dict[str, Dict[str, str]] = {
    "above_horizon": {
        "epoch_angle": "ASC",
        "zh": "月亮在出生時位於地平線上方（第7–12宮），"
              "故前世盤的上升點（ASC）等於本命盤的月亮位置",
        "en": "Moon above horizon at birth (houses 7–12): "
              "Moon at Birth = Ascendant at Epoch",
    },
    "below_horizon": {
        "epoch_angle": "DSC",
        "zh": "月亮在出生時位於地平線下方（第1–6宮），"
              "故前世盤的下降點（DSC）等於本命盤的月亮位置",
        "en": "Moon below horizon at birth (houses 1–6): "
              "Moon at Birth = Descendant at Epoch",
    },
}

# ============================================================
# Moon Phase Adjustment (Bailey's refinement)
# ============================================================
# Bailey adds a further distinction based on whether the Moon is
# waxing or waning at birth:
#
#   WAXING Moon (Moon further from Sun in direct motion, elongation 0–180°):
#     - If above horizon: ASC at Epoch = Moon at Birth
#     - If below horizon: DSC at Epoch = Moon at Birth
#
#   WANING Moon (elongation 180–360°):
#     - Same rule as waxing in most interpretations
#     - Bailey notes minor adjustments based on exact elongation
#
# The key insight: gestation period adjustment uses the Moon's
# elongation from the Sun at birth.
#
# Ref: Bailey, Chapter IV–V.

MOON_PHASE_NAMES: Dict[str, str] = {
    "new_moon":        "新月 New Moon",
    "waxing_crescent": "眉月 Waxing Crescent",
    "first_quarter":   "上弦月 First Quarter",
    "waxing_gibbous":  "盈凸月 Waxing Gibbous",
    "full_moon":       "滿月 Full Moon",
    "waning_gibbous":  "虧凸月 Waning Gibbous",
    "last_quarter":    "下弦月 Last Quarter",
    "waning_crescent": "殘月 Waning Crescent",
}

# Elongation ranges (degrees) for each Moon phase
# elongation = Moon longitude - Sun longitude (mod 360)
MOON_PHASE_ELONGATION: Dict[str, Tuple[float, float]] = {
    "new_moon":        (0.0,   22.5),
    "waxing_crescent": (22.5,  67.5),
    "first_quarter":   (67.5, 112.5),
    "waxing_gibbous":  (112.5, 157.5),
    "full_moon":       (157.5, 202.5),
    "waning_gibbous":  (202.5, 247.5),
    "last_quarter":    (247.5, 292.5),
    "waning_crescent": (292.5, 360.0),
}

# ============================================================
# Sex Degrees (Optional Gender Confirmation)
# ============================================================
# Some classical texts note that the Epoch Moon or ASC falling
# in certain degree ranges confirms the gender of the native.
# These are the "masculine" and "feminine" degrees.
#
# Ref: Bailey (1916), Appendix; Sepharial, Solar Epoch (1913).
#
# Note: These are of historical interest only. Modern usage
# focuses on the astronomical/astrological calculation, not
# gender determination.

SEX_DEGREES_MASCULINE: List[Tuple[str, float, float]] = [
    ("Aries",       0.0,  30.0),
    ("Gemini",      0.0,  30.0),
    ("Leo",         0.0,  30.0),
    ("Libra",       0.0,  30.0),
    ("Sagittarius", 0.0,  30.0),
    ("Aquarius",    0.0,  30.0),
]
"""Masculine signs (fire + air) for sex degree confirmation.
Ref: Bailey (1916), Appendix B."""

SEX_DEGREES_FEMININE: List[Tuple[str, float, float]] = [
    ("Taurus",      0.0,  30.0),
    ("Cancer",      0.0,  30.0),
    ("Virgo",       0.0,  30.0),
    ("Scorpio",     0.0,  30.0),
    ("Capricorn",   0.0,  30.0),
    ("Pisces",      0.0,  30.0),
]
"""Feminine signs (earth + water) for sex degree confirmation.
Ref: Bailey (1916), Appendix B."""

# ============================================================
# Trutine Variants
# ============================================================
# Different historical authorities propose slight variations:

TRUTINE_VARIANTS: Dict[str, Dict[str, str]] = {
    "hermes_ptolemy": {
        "zh_name": "赫密士/托勒密 經典法",
        "en_name": "Classical Hermes/Ptolemy",
        "zh_desc": (
            "最古老的版本，源自赫密士·特里斯墨吉斯忒斯，托勒密《百句箴言》第51條。"
            "規則：月亮在地平線上方→前世盤上升 = 本命月亮；"
            "月亮在地平線下方→前世盤下降 = 本命月亮。"
            "妊娠期：約273天（9個太陰月）。"
        ),
        "en_desc": (
            "The oldest version, attributed to Hermes Trismegistus and "
            "codified in Ptolemy's Centiloquium Aphorism 51. "
            "Rule: Moon above horizon → Epoch ASC = Natal Moon; "
            "Moon below horizon → Epoch DSC = Natal Moon. "
            "Gestation: ~273 days (9 lunar months)."
        ),
        "gestation_days": GESTATION_DAYS_STANDARD,
        "source": "Ptolemy, Centiloquium Aphorism 51 (2nd c. CE)",
    },
    "bailey_standard": {
        "zh_name": "貝利標準法",
        "en_name": "Bailey Standard",
        "zh_desc": (
            "E.H. Bailey 在《出生前世盤》（1916）中詳細闡述的完整方法。"
            "加入月相（上弦/下弦）細分，並根據日月角距精確調整妊娠期。"
            "被認為是現代最系統、最完整的前世盤計算體系。"
        ),
        "en_desc": (
            "E.H. Bailey's complete method from *The Prenatal Epoch* (1916). "
            "Adds Moon phase (waxing/waning) subdivision and precise gestation "
            "adjustment based on Sun-Moon elongation. "
            "Considered the most systematic modern treatment."
        ),
        "gestation_days": GESTATION_DAYS_STANDARD,
        "source": "E.H. Bailey, The Prenatal Epoch (1916)",
    },
    "sepharial": {
        "zh_name": "賽法利亞爾 太陽紀元法",
        "en_name": "Sepharial Solar Epoch",
        "zh_desc": (
            "賽法利亞爾（W.R. Old）在《太陽紀元》（1913）中的方法。"
            "以太陽（而非月亮）作為主要紀元標誌，"
            "強調妊娠期的太陽-月亮角距變化。"
        ),
        "en_desc": (
            "Sepharial's method from *The Solar Epoch* (1913). "
            "Uses the Sun (rather than Moon) as primary epoch marker, "
            "emphasising the solar-lunar elongation shift over gestation."
        ),
        "gestation_days": GESTATION_DAYS_STANDARD,
        "source": "Sepharial (W.R. Old), The Solar Epoch (1913)",
    },
}

# ============================================================
# Aspect Orbs for Epoch-Natal Cross-Aspects
# ============================================================
# Orbs for comparison aspects between Epoch and Natal charts.
# Tighter than standard natal orbs because we're comparing two charts.
# Ref: Bailey (1916), Chapter VIII.

EPOCH_NATAL_ASPECT_ORBS: Dict[str, float] = {
    "Conjunction ☌":  5.0,
    "Opposition ☍":   5.0,
    "Trine △":        4.0,
    "Square □":       4.0,
    "Sextile ⚹":      3.0,
    "Quincunx ⚻":     2.0,
    "Semi-Sextile ⚺": 1.5,
}

# ============================================================
# Planet IDs and Display Data
# ============================================================

PLANET_DISPLAY: Dict[str, Dict[str, str]] = {
    "Sun":     {"zh": "太陽 ☉", "en": "Sun ☉",     "glyph": "☉", "color": "#FFD700"},
    "Moon":    {"zh": "月亮 ☽", "en": "Moon ☽",    "glyph": "☽", "color": "#C0C0C0"},
    "Mercury": {"zh": "水星 ☿", "en": "Mercury ☿", "glyph": "☿", "color": "#A0A0FF"},
    "Venus":   {"zh": "金星 ♀", "en": "Venus ♀",   "glyph": "♀", "color": "#FF69B4"},
    "Mars":    {"zh": "火星 ♂", "en": "Mars ♂",    "glyph": "♂", "color": "#FF4444"},
    "Jupiter": {"zh": "木星 ♃", "en": "Jupiter ♃", "glyph": "♃", "color": "#FF8C00"},
    "Saturn":  {"zh": "土星 ♄", "en": "Saturn ♄",  "glyph": "♄", "color": "#8B8B8B"},
    "Uranus":  {"zh": "天王星 ♅", "en": "Uranus ♅","glyph": "♅", "color": "#40E0D0"},
    "Neptune": {"zh": "海王星 ♆", "en": "Neptune ♆","glyph": "♆", "color": "#4169E1"},
    "Pluto":   {"zh": "冥王星 ♇", "en": "Pluto ♇", "glyph": "♇", "color": "#8B0000"},
    "ASC":     {"zh": "上升點",   "en": "ASC",      "glyph": "⬆", "color": "#00FF7F"},
    "MC":      {"zh": "中天",     "en": "MC",       "glyph": "⬆", "color": "#00BFFF"},
    "DSC":     {"zh": "下降點",   "en": "DSC",      "glyph": "⬇", "color": "#90EE90"},
    "IC":      {"zh": "天底",     "en": "IC",       "glyph": "⬇", "color": "#87CEEB"},
}

ZODIAC_SIGNS: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

ZODIAC_SIGN_ZH: Dict[str, str] = {
    "Aries": "白羊座 ♈", "Taurus": "金牛座 ♉", "Gemini": "雙子座 ♊",
    "Cancer": "巨蟹座 ♋", "Leo": "獅子座 ♌", "Virgo": "處女座 ♍",
    "Libra": "天秤座 ♎", "Scorpio": "天蠍座 ♏", "Sagittarius": "射手座 ♐",
    "Capricorn": "摩羯座 ♑", "Aquarius": "水瓶座 ♒", "Pisces": "雙魚座 ♓",
}

ZODIAC_GLYPHS: Dict[str, str] = {
    "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
    "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
    "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓",
}

# ============================================================
# Soul-Level Interpretation Themes
# ============================================================
# These interpretive keywords are drawn from the tradition that
# the Prenatal Epoch represents the "soul's entry" — the moment
# of spiritual incarnation, before physical birth.
#
# Ref: Alice Bailey, *Esoteric Astrology* (1951);
#      Bailey, *The Prenatal Epoch* (1916), Introduction.

EPOCH_SOUL_THEMES: Dict[str, Dict[str, str]] = {
    "Sun": {
        "zh": "靈魂目標與本質力量 — 前世盤太陽揭示此次轉世的核心靈魂任務與意志表達",
        "en": "Soul Purpose & Core Power — Epoch Sun reveals the core soul task and will-expression for this incarnation",
    },
    "Moon": {
        "zh": "情緒記憶與靈魂習性 — 前世盤月亮反映攜入此世的情緒模式、靈魂習慣與舊有制約",
        "en": "Emotional Memory & Soul Habits — Epoch Moon reflects emotional patterns, soul habits, and conditioning carried into this life",
    },
    "Mercury": {
        "zh": "思維工具與溝通使命 — 前世盤水星顯示靈魂在此世學習和表達的心智模式",
        "en": "Mind Tool & Communication Mission — Epoch Mercury shows the mental patterns the soul chose for learning in this life",
    },
    "Venus": {
        "zh": "愛的課題與靈魂價值觀 — 前世盤金星揭示此生在關係與美的追求中的靈魂主題",
        "en": "Love Lessons & Soul Values — Epoch Venus reveals soul themes in relationships and the pursuit of beauty in this life",
    },
    "Mars": {
        "zh": "行動原動力與業力驅動 — 前世盤火星顯示靈魂帶入此世的衝動、勇氣與業力挑戰",
        "en": "Action Drive & Karmic Impulse — Epoch Mars shows the drive, courage, and karmic challenges the soul brought into this life",
    },
    "Jupiter": {
        "zh": "擴展路徑與靈魂祝福 — 前世盤木星指示此生靈魂成長的方向與來自高靈的祝福",
        "en": "Expansion Path & Soul Blessings — Epoch Jupiter indicates the direction of soul growth and blessings from higher realms",
    },
    "Saturn": {
        "zh": "業力課題與靈魂限制 — 前世盤土星揭示靈魂在此世需要克服的業力障礙與結構性課題",
        "en": "Karmic Lessons & Soul Restrictions — Epoch Saturn reveals the karmic obstacles and structural lessons the soul must overcome in this life",
    },
    "ASC": {
        "zh": "靈魂化身的門戶 — 前世盤上升點是靈魂進入肉身的方式，代表靈魂選擇的外在呈現",
        "en": "Gateway of Incarnation — Epoch ASC is how the soul chose to enter the body, representing the outer presentation chosen by the soul",
    },
    "Moon_natal": {
        "zh": "靈魂交換點（本命月亮 = 前世盤上升/下降）— 這是赫密士法則的核心靈魂連結點",
        "en": "Soul Exchange Point (Natal Moon = Epoch ASC/DSC) — This is the core soul-link point of the Trutine of Hermes",
    },
}

# ============================================================
# Historical Introduction Text
# ============================================================

TRUTINE_HISTORY: Dict[str, str] = {
    "zh": """
**赫密士出生前世盤（Trutine of Hermes / Prenatal Epoch）** 是古典希臘化占星術中
最神秘也最深刻的技術之一，被認為是赫密士·特里斯墨吉斯忒斯（Hermes Trismegistus）
——傳說中「三重偉大的赫密士」——所傳下的靈魂層級工具。

### 古典淵源

托勒密在《百句箴言》（Centiloquium / Karpos）第51條記載了這條法則：

> *"月亮在地平線上方時，前世盤的上升點等於本命盤的月亮；*
> *月亮在地平線下方時，前世盤的下降點等於本命盤的月亮。"*

這意味著受孕時刻（前世盤，即 Prenatal Epoch）與出生時刻（本命盤）之間，
存在一種神聖的互換關係：**月亮↔上升/下降點**。

### 靈魂層級意義

前世盤代表「靈魂入身之時」——靈魂在受孕時選擇進入人世的天象印記。
相比本命盤（出生時刻），前世盤更接近靈魂本質：

- **前世盤太陽**：靈魂此世的核心任務
- **前世盤月亮**：攜入此世的情緒記憶與靈魂習性
- **前世盤上升**：靈魂化身的方式與外在呈現
- **前世盤與本命盤的相位**：揭示靈魂計劃與現實生命的對話

### 現代復興

E.H. Bailey 在 1916 年的《出生前世盤》（*The Prenatal Epoch*）
中對這一技術進行了最系統的現代整理，
賦予了精確的計算方法和大量案例驗證。
本工具以 Bailey 的方法為核心，結合托勒密的原始規則。

### 校正驗證用途

前世盤也是出生時間校正的重要工具——
如果計算出的前世盤上升點（或下降點）
確實等於本命盤月亮（誤差在 1°以內），
則可以作為出生時間正確性的強力佐證。
""",
    "en": """
**The Trutine of Hermes** (also known as the **Prenatal Epoch** or
**Conception Chart**) is one of the most profound and mysterious techniques
in classical Hellenistic astrology, attributed to Hermes Trismegistus —
the legendary "Thrice-Great Hermes."

### Classical Origins

Ptolemy recorded the core rule in the *Centiloquium* (Karpos), Aphorism 51:

> *"When the Moon is above the horizon, the Ascendant of the Epoch*
> *equals the Moon's position at birth; when below, the Descendant."*

This reveals a sacred reciprocal relationship between the moment of conception
(the Epoch chart) and the moment of birth (the Natal chart):
**Moon ↔ Ascendant/Descendant**.

### Soul-Level Meaning

The Prenatal Epoch represents the "moment of soul entry" — the celestial
imprint at the moment the soul chose to enter the world through conception.
Compared to the Natal chart (birth), the Epoch chart is closer to the soul's
essence:

- **Epoch Sun**: Core soul task for this incarnation
- **Epoch Moon**: Emotional memory and soul habits carried in
- **Epoch ASC**: How the soul chose to incarnate and present itself
- **Epoch-Natal aspects**: The dialogue between soul plan and lived life

### Modern Revival

E.H. Bailey's *The Prenatal Epoch* (1916) provides the most systematic
modern treatment, with precise calculation methods and extensive case studies.
This module uses Bailey's method as its foundation, combined with Ptolemy's
original rule.

### Rectification Verification

The Epoch is also a powerful birth-time rectification tool —
if the calculated Epoch ASC (or DSC) matches the Natal Moon position
within 1°, this strongly confirms the birth time is accurate.
""",
}

# ============================================================
# Colour Theme
# ============================================================

TRUTINE_GOLD: str = "#C9A227"      # Hermetic gold
TRUTINE_SILVER: str = "#A8B8C8"    # Lunar silver
TRUTINE_PURPLE: str = "#7B5EA7"    # Mystical purple
TRUTINE_TEAL: str = "#2D9B8A"      # Alchemical teal
TRUTINE_CRIMSON: str = "#8B2020"   # Mars red
TRUTINE_BG: str = "rgba(8,6,24,0.97)"
TRUTINE_BORDER: str = "rgba(201,162,39,0.30)"
TRUTINE_BORDER_SILVER: str = "rgba(168,184,200,0.25)"
