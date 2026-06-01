"""
astro/harmonic/constants.py — Constants for Harmonic Astrology (John Addey)

Based on:
  - John Addey, "Harmonics in Astrology" (1976, L.N. Fowler & Co.)
  - David Hamblin, "Harmonic Charts" (1983, Aquarian Press)

The core principle: multiply every planet's longitude by harmonic number N
(mod 360°) and examine conjunctions in the resulting chart.
"""

from __future__ import annotations

from typing import Dict, Tuple

# ── Swiss Ephemeris planet IDs (keyed by standard abbreviation)
PLANET_SWE_IDS: Dict[str, int] = {
    "SU": 0,   # Sun
    "MO": 1,   # Moon
    "ME": 2,   # Mercury
    "VE": 3,   # Venus
    "MA": 4,   # Mars
    "JU": 5,   # Jupiter
    "SA": 6,   # Saturn
    "UR": 7,   # Uranus
    "NE": 8,   # Neptune
    "PL": 9,   # Pluto
    # 10 = TRUE_NODE handled separately
}

PLANET_NAMES_EN: Dict[str, str] = {
    "SU": "Sun",
    "MO": "Moon",
    "ME": "Mercury",
    "VE": "Venus",
    "MA": "Mars",
    "JU": "Jupiter",
    "SA": "Saturn",
    "UR": "Uranus",
    "NE": "Neptune",
    "PL": "Pluto",
    "AS": "Ascendant",
    "MC": "Midheaven",
    "NN": "North Node",
}

PLANET_NAMES_ZH: Dict[str, str] = {
    "SU": "太陽",
    "MO": "月亮",
    "ME": "水星",
    "VE": "金星",
    "MA": "火星",
    "JU": "木星",
    "SA": "土星",
    "UR": "天王星",
    "NE": "海王星",
    "PL": "冥王星",
    "AS": "上升點",
    "MC": "中天",
    "NN": "北交點",
}

PLANET_SYMBOLS: Dict[str, str] = {
    "SU": "☉",
    "MO": "☽",
    "ME": "☿",
    "VE": "♀",
    "MA": "♂",
    "JU": "♃",
    "SA": "♄",
    "UR": "♅",
    "NE": "♆",
    "PL": "♇",
    "AS": "AC",
    "MC": "MC",
    "NN": "☊",
}

# Standard order for output
PLANET_ORDER: list[str] = [
    "SU", "MO", "ME", "VE", "MA", "JU", "SA", "UR", "NE", "PL", "AS", "MC", "NN"
]

ZODIAC_SIGNS: list[str] = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_ZH: list[str] = [
    "白羊", "金牛", "雙子", "巨蟹",
    "獅子", "處女", "天秤", "天蠍",
    "射手", "摩羯", "水瓶", "雙魚",
]

SIGN_SYMBOLS: list[str] = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

# ──────────────────────────────────────────────────────────────
# Harmonic definitions (Addey tradition)
# Each entry: (number, name_zh, name_en, theme_zh, theme_en, conjunction_orb_deg)
# ──────────────────────────────────────────────────────────────

HARMONIC_DEFS: Dict[int, Dict] = {
    1: {
        "name_zh": "一諧波 (基礎盤)",
        "name_en": "1st Harmonic (Natal)",
        "theme_zh": "原始自我、本命基礎",
        "theme_en": "Primary self, natal foundation",
        "addey_note_zh": "1H 即本命盤本身，代表自我的基礎面向。",
        "addey_note_en": "H1 is the natal chart itself, representing the fundamental self.",
        "orb": 8.0,
        "color_primary": "#4a90d9",
        "color_secondary": "#a8c8f0",
        "color_bg": "#0d1b2a",
        "petals": 1,
        "svg_theme": "solar",
    },
    2: {
        "name_zh": "二諧波",
        "name_en": "2nd Harmonic",
        "theme_zh": "對立、張力與整合",
        "theme_en": "Opposition, polarity, and integration",
        "addey_note_zh": (
            "Addey：2H 與對分相（180°）相關，揭示生命中的衝突與互補極性。"
            "在2H 盤中的合相，對應本命盤的對分相。代表兩極整合的人生課題。"
        ),
        "addey_note_en": (
            "Addey: H2 is related to the opposition aspect (180°). "
            "Conjunctions in H2 correspond to natal oppositions. "
            "It reveals polarities and the challenge of integration."
        ),
        "orb": 6.0,
        "color_primary": "#e8475f",
        "color_secondary": "#f4a0b0",
        "color_bg": "#1a0d0f",
        "petals": 2,
        "svg_theme": "opposition",
    },
    3: {
        "name_zh": "三諧波",
        "name_en": "3rd Harmonic",
        "theme_zh": "才能、和諧與喜悅創造",
        "theme_en": "Talent, harmony, and joyful creativity",
        "addey_note_zh": (
            "Addey：3H 是最重要的才能諧波之一，與三分相（120°）相關。"
            "在3H 盤中的合相揭示天賦才能、藝術能力和創造力。"
            "Jupiter 特別重要：3H 中 Jupiter 合相個人行星顯示幸運與才能。"
        ),
        "addey_note_en": (
            "Addey: H3 is one of the most important talent harmonics, "
            "related to the trine (120°). Conjunctions in H3 reveal innate "
            "gifts, artistic ability, and creative flow. Jupiter is especially "
            "significant: Jupiter conjunct personal planets in H3 indicates luck and talent."
        ),
        "orb": 5.0,
        "color_primary": "#f5a623",
        "color_secondary": "#fad180",
        "color_bg": "#1a1200",
        "petals": 3,
        "svg_theme": "trine",
    },
    4: {
        "name_zh": "四諧波",
        "name_en": "4th Harmonic",
        "theme_zh": "基礎、結構與穩定",
        "theme_en": "Foundation, structure, and stability",
        "addey_note_zh": (
            "Addey：4H 與四分相（90°）及對分相相關，揭示生命中的結構與挑戰。"
            "在4H 盤中的合相代表透過努力和磨練建立的穩固基礎。"
            "Saturn 在4H 具有特殊重要性。"
        ),
        "addey_note_en": (
            "Addey: H4 relates to the square (90°) and opposition. "
            "Conjunctions in H4 indicate challenges that build foundations. "
            "Saturn carries particular significance in H4."
        ),
        "orb": 5.0,
        "color_primary": "#7b68ee",
        "color_secondary": "#b8adff",
        "color_bg": "#0d0d1a",
        "petals": 4,
        "svg_theme": "square",
    },
    5: {
        "name_zh": "五諧波",
        "name_en": "5th Harmonic",
        "theme_zh": "天賦、創意表現與靈魂使命",
        "theme_en": "Talent, creative expression, and soul purpose",
        "addey_note_zh": (
            "Addey：5H 是最著名的「才能諧波」，與五分相（72°）相關。"
            "Addey 在研究傑出人物（音樂家、藝術家、運動員）時發現，"
            "5H 盤中的合相密度遠超隨機分佈，強力指向特定領域的天賦。"
            "Venus 和 Mercury 在5H 的合相與藝術才華高度相關。"
            "Sun 在5H 合相外行星顯示強烈的創意衝動與表達慾望。"
        ),
        "addey_note_en": (
            "Addey: H5 is the celebrated 'talent harmonic', related to the "
            "quintile (72°). In his research on outstanding individuals — musicians, "
            "artists, athletes — Addey found that H5 conjunctions cluster far beyond "
            "random distribution, strongly indicating specific domains of gift. "
            "Venus and Mercury conjunctions in H5 correlate with artistic genius. "
            "Sun conjunct outer planets in H5 indicates powerful creative drive."
        ),
        "orb": 4.0,
        "color_primary": "#00c9a7",
        "color_secondary": "#80e8d4",
        "color_bg": "#001a15",
        "petals": 5,
        "svg_theme": "quintile",
    },
    7: {
        "name_zh": "七諧波",
        "name_en": "7th Harmonic",
        "theme_zh": "靈性、神秘直覺與業力關係",
        "theme_en": "Spirituality, mystical intuition, and karmic bonds",
        "addey_note_zh": (
            "Addey：7H 與七分相（51.43°）相關，是最具靈性與神秘色彩的諧波。"
            "在靈性導師、神祕主義者、詩人和具有深刻直覺的人的命盤中常見強烈的7H 模式。"
            "Neptune 和 Pluto 在7H 的合相與深層靈性體驗相關。"
            "7H 也揭示業力關係和靈魂層次的連結。"
        ),
        "addey_note_en": (
            "Addey: H7 relates to the septile (51.43°) and carries the most "
            "spiritual and mysterious quality of harmonics. Strong H7 patterns "
            "appear in the charts of spiritual teachers, mystics, poets, and those "
            "with profound intuitive gifts. Neptune and Pluto conjunctions in H7 "
            "relate to deep spiritual experiences. H7 also reveals karmic bonds "
            "and soul-level connections."
        ),
        "orb": 4.0,
        "color_primary": "#9b59b6",
        "color_secondary": "#d2a8e8",
        "color_bg": "#0f0a14",
        "petals": 7,
        "svg_theme": "septile",
    },
    9: {
        "name_zh": "九諧波",
        "name_en": "9th Harmonic",
        "theme_zh": "靈性進化、高頻意識與整合智慧",
        "theme_en": "Spiritual evolution, elevated consciousness, and integrated wisdom",
        "addey_note_zh": (
            "Addey：9H 與九分相（40°）相關，代表靈性發展的最高層次。"
            "在哲學家、宗教領袖和高度覺醒個體的命盤中，9H 模式尤為突出。"
            "9H 盤中 Jupiter 的合相指向宗教智慧；Sun-Moon 合相指向整合的靈性自我。"
            "也與過去世業力整合、今生靈性使命緊密相連。"
        ),
        "addey_note_en": (
            "Addey: H9 relates to the novile (40°) and represents the highest "
            "level of spiritual development. H9 patterns are particularly prominent "
            "in the charts of philosophers, religious leaders, and highly awakened "
            "individuals. Jupiter conjunctions in H9 point to religious wisdom; "
            "Sun-Moon conjunctions indicate an integrated spiritual self. "
            "H9 also connects deeply to past-life karmic integration and present soul mission."
        ),
        "orb": 3.5,
        "color_primary": "#f0c040",
        "color_secondary": "#fae090",
        "color_bg": "#1a1500",
        "petals": 9,
        "svg_theme": "novile",
    },
    12: {
        "name_zh": "十二諧波",
        "name_en": "12th Harmonic",
        "theme_zh": "業力整合、奉獻與潛意識模式",
        "theme_en": "Karmic synthesis, service, and unconscious patterns",
        "addey_note_zh": (
            "Addey：12H 是4H 和3H 的複合（4×3），整合結構與才能兩種能量。"
            "與十二分相（30°）相關。12H 揭示深層業力模式、潛意識動力和服務他人的使命。"
            "Neptune 在12H 的強勢位置常見於靈媒、療癒師和宗教服務者的命盤中。"
        ),
        "addey_note_en": (
            "Addey: H12 is the compound of H4 and H3 (4×3), integrating "
            "structural and creative energies. Related to the semi-sextile (30°). "
            "H12 reveals deep karmic patterns, unconscious motivations, and the "
            "mission of service to others. Neptune prominent in H12 frequently "
            "appears in charts of mediums, healers, and those in religious service."
        ),
        "orb": 3.0,
        "color_primary": "#17a2b8",
        "color_secondary": "#80d8e4",
        "color_bg": "#001215",
        "petals": 12,
        "svg_theme": "duodecile",
    },
}

# All supported harmonic numbers (in display order)
SUPPORTED_HARMONICS: list[int] = [1, 2, 3, 4, 5, 7, 9, 12]

# Conjunction orb for each harmonic (degrees) — tighter for higher harmonics
DEFAULT_CONJUNCTION_ORB: Dict[int, float] = {
    h: HARMONIC_DEFS[h]["orb"] for h in SUPPORTED_HARMONICS
}

# ──────────────────────────────────────────────────────────────
# Planet combination interpretations in harmonic charts
# (John Addey tradition, expanded by Hamblin)
# ──────────────────────────────────────────────────────────────

HARMONIC_CONJUNCTION_MEANINGS: Dict[frozenset, Dict[str, str]] = {
    frozenset({"SU", "MO"}): {
        "zh": "太陽與月亮：意志與情感的深度整合，身心合一，強烈的個人完整感。",
        "en": "Sun–Moon: Deep integration of will and emotion, psychosomatic unity, strong sense of personal wholeness.",
    },
    frozenset({"SU", "ME"}): {
        "zh": "太陽與水星：思維與自我高度一致，溝通能力突出，智識才能。",
        "en": "Sun–Mercury: Mind and self in high alignment, outstanding communication, intellectual gifts.",
    },
    frozenset({"SU", "VE"}): {
        "zh": "太陽與金星：美感天賦、藝術創造力、愛與美的表達能力。",
        "en": "Sun–Venus: Aesthetic gifts, artistic creativity, capacity for expressing love and beauty.",
    },
    frozenset({"SU", "MA"}): {
        "zh": "太陽與火星：強烈的行動衝動、意志力、開創性能量與競爭才能。",
        "en": "Sun–Mars: Powerful drive to act, willpower, pioneering energy, competitive talent.",
    },
    frozenset({"SU", "JU"}): {
        "zh": "太陽與木星：幸運擴展、慷慨大方、哲學智慧、領導才能。",
        "en": "Sun–Jupiter: Lucky expansion, generosity, philosophical wisdom, leadership talent.",
    },
    frozenset({"SU", "SA"}): {
        "zh": "太陽與土星：嚴謹的紀律、責任感、深度耐心與建構能力。",
        "en": "Sun–Saturn: Rigorous discipline, sense of responsibility, profound patience and the capacity to build.",
    },
    frozenset({"SU", "UR"}): {
        "zh": "太陽與天王星：革命性創新、獨特個性、突破傳統的才能。",
        "en": "Sun–Uranus: Revolutionary innovation, unique individuality, talent for breaking conventions.",
    },
    frozenset({"SU", "NE"}): {
        "zh": "太陽與海王星：靈性感知、藝術靈感、夢境智慧、神秘洞察力。",
        "en": "Sun–Neptune: Spiritual sensitivity, artistic inspiration, dream wisdom, mystical insight.",
    },
    frozenset({"SU", "PL"}): {
        "zh": "太陽與冥王星：深層轉化力量、強烈的重生衝動、隱藏的權力才能。",
        "en": "Sun–Pluto: Deep transformative power, intense drive toward rebirth, hidden power talent.",
    },
    frozenset({"MO", "VE"}): {
        "zh": "月亮與金星：情感美感、滋養藝術、溫柔的創造力與人際和諧才能。",
        "en": "Moon–Venus: Emotional aesthetics, nurturing artistry, gentle creativity, talent for harmony.",
    },
    frozenset({"MO", "JU"}): {
        "zh": "月亮與木星：情感豐盛、慷慨滋養他人、樂觀的情感基調，幸運感受。",
        "en": "Moon–Jupiter: Emotional abundance, generous nurturing, optimistic feeling tone, emotional luck.",
    },
    frozenset({"MO", "SA"}): {
        "zh": "月亮與土星：深厚的情感耐力、穩定的情感結構、通過感情考驗的能力。",
        "en": "Moon–Saturn: Deep emotional endurance, stable emotional structure, capacity to withstand emotional trials.",
    },
    frozenset({"MO", "NE"}): {
        "zh": "月亮與海王星：靈性直覺、超感知覺、夢境才能、深邃同理心。",
        "en": "Moon–Neptune: Spiritual intuition, extrasensory perception, dream talent, deep empathy.",
    },
    frozenset({"MO", "PL"}): {
        "zh": "月亮與冥王星：深層情感轉化、強烈的心理洞察力、情感再生能力。",
        "en": "Moon–Pluto: Deep emotional transformation, intense psychological insight, capacity for emotional rebirth.",
    },
    frozenset({"ME", "VE"}): {
        "zh": "水星與金星：語言美感、詩意溝通、優雅表達的藝術才能。",
        "en": "Mercury–Venus: Linguistic aesthetics, poetic communication, talent for elegant expression.",
    },
    frozenset({"ME", "MA"}): {
        "zh": "水星與火星：敏銳辯論、快速思維、智識競爭力與說服才能。",
        "en": "Mercury–Mars: Sharp debate, quick thinking, intellectual competitiveness and persuasion talent.",
    },
    frozenset({"ME", "JU"}): {
        "zh": "水星與木星：寬廣哲學視野、教學才能、語言擴展力與智慧表達。",
        "en": "Mercury–Jupiter: Broad philosophical vision, teaching talent, linguistic expansion, wise expression.",
    },
    frozenset({"ME", "UR"}): {
        "zh": "水星與天王星：天才直覺、革命性思想、科技創新才能、閃電悟性。",
        "en": "Mercury–Uranus: Genius intuition, revolutionary thought, technological innovation, lightning insight.",
    },
    frozenset({"ME", "NE"}): {
        "zh": "水星與海王星：詩意幻想、靈媒溝通才能、神秘語言感知。",
        "en": "Mercury–Neptune: Poetic fantasy, mediumistic communication talent, mystical linguistic perception.",
    },
    frozenset({"VE", "MA"}): {
        "zh": "金星與火星：激情創造力、藝術衝動、愛情才能、美麗的戰鬥精神。",
        "en": "Venus–Mars: Passionate creativity, artistic impulse, love talent, beautiful fighting spirit.",
    },
    frozenset({"VE", "JU"}): {
        "zh": "金星與木星：豐盛之美、幸運的藝術才能、慷慨的愛，美好生活。",
        "en": "Venus–Jupiter: Abundant beauty, lucky artistic talent, generous love, the good life.",
    },
    frozenset({"VE", "NE"}): {
        "zh": "金星與海王星：超凡美感、神聖之愛、靈性藝術才能、理想化創造力。",
        "en": "Venus–Neptune: Transcendent beauty, divine love, spiritual artistic talent, idealized creativity.",
    },
    frozenset({"JU", "NN"}): {
        "zh": "木星與北交點：業力幸運、集體成長方向、擴展性的靈魂使命。",
        "en": "Jupiter–North Node: Karmic luck, collective growth direction, expansive soul mission.",
    },
    frozenset({"SA", "NN"}): {
        "zh": "土星與北交點：業力責任、結構性的靈魂課題、通過紀律實現使命。",
        "en": "Saturn–North Node: Karmic responsibility, structural soul lesson, fulfilling mission through discipline.",
    },
    frozenset({"NE", "PL"}): {
        "zh": "海王星與冥王星：世代性的靈性轉化力量，深層集體意識的重塑。",
        "en": "Neptune–Pluto: Generational spiritual transformation, deep reshaping of collective consciousness.",
    },
}


def get_conjunction_meaning(key_a: str, key_b: str) -> Dict[str, str]:
    """Return the bilingual interpretation for a planet pair conjunction."""
    pair = frozenset({key_a, key_b})
    return HARMONIC_CONJUNCTION_MEANINGS.get(pair, {
        "zh": f"{PLANET_NAMES_ZH.get(key_a, key_a)}與{PLANET_NAMES_ZH.get(key_b, key_b)}：特殊的諧波共鳴，揭示獨特的才能模式。",
        "en": f"{PLANET_NAMES_EN.get(key_a, key_a)}–{PLANET_NAMES_EN.get(key_b, key_b)}: A unique harmonic resonance revealing a distinctive talent pattern.",
    })


# ──────────────────────────────────────────────────────────────
# Harmonic-specific conjunction meanings override
# (e.g. same pair means different things in H5 vs H7)
# ──────────────────────────────────────────────────────────────

HARMONIC_SPECIFIC_MEANINGS: Dict[Tuple[int, frozenset], Dict[str, str]] = {
    (5, frozenset({"SU", "VE"})): {
        "zh": "【5H】太陽-金星合相：極強的藝術天賦，美學創造力，音樂或視覺藝術的卓越才能。Addey 特別強調此組合在知名藝術家命盤中的高頻出現。",
        "en": "【H5】Sun–Venus conjunction: Exceptional artistic talent, aesthetic creativity, outstanding gifts in music or visual arts. Addey particularly noted this combination's high frequency in charts of renowned artists.",
    },
    (5, frozenset({"SU", "ME"})): {
        "zh": "【5H】太陽-水星合相：語言創造天才，卓越的寫作或演說才能，思維與表達高度融合。",
        "en": "【H5】Sun–Mercury conjunction: Linguistic creative genius, outstanding writing or oratory talent, mind and expression deeply fused.",
    },
    (5, frozenset({"MO", "VE"})): {
        "zh": "【5H】月亮-金星合相：深層情感美感，直覺性藝術才能，音樂感知天賦。",
        "en": "【H5】Moon–Venus conjunction: Deep emotional aesthetics, intuitive artistic talent, musical sensitivity as a gift.",
    },
    (7, frozenset({"SU", "NE"})): {
        "zh": "【7H】太陽-海王星合相：深刻的靈性本質，神秘直覺，靈媒或通靈才能的高度指標。",
        "en": "【H7】Sun–Neptune conjunction: Profound spiritual essence, mystical intuition, a strong indicator of mediumistic or psychic gifts.",
    },
    (7, frozenset({"MO", "NE"})): {
        "zh": "【7H】月亮-海王星合相：超感知覺，靈性夢境，情感直覺高達神秘層次。",
        "en": "【H7】Moon–Neptune conjunction: Extrasensory perception, spiritual dreaming, emotional intuition elevated to mystical levels.",
    },
    (9, frozenset({"SU", "JU"})): {
        "zh": "【9H】太陽-木星合相：靈性智慧的頂點，哲學與宗教領悟力，高度的精神進化標誌。",
        "en": "【H9】Sun–Jupiter conjunction: The apex of spiritual wisdom, philosophical and religious insight, a strong marker of advanced spiritual evolution.",
    },
    (9, frozenset({"SU", "MO"})): {
        "zh": "【9H】太陽-月亮合相：整合的靈性自我，身心靈完整合一，高度的靈性覺醒潛能。",
        "en": "【H9】Sun–Moon conjunction: Integrated spiritual self, complete unity of body, mind and spirit, high potential for spiritual awakening.",
    },
}


def get_harmonic_specific_meaning(
    harmonic: int, key_a: str, key_b: str
) -> Dict[str, str]:
    """Return harmonic-specific conjunction meaning if available, else general."""
    pair = frozenset({key_a, key_b})
    specific = HARMONIC_SPECIFIC_MEANINGS.get((harmonic, pair))
    if specific:
        return specific
    return get_conjunction_meaning(key_a, key_b)
