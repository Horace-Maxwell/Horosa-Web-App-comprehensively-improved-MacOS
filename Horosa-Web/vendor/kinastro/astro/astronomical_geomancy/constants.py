"""
astro/astronomical_geomancy/constants.py
═══════════════════════════════════════════════════════════════
Constants for Gerardus Cremonensis' Astronomical Geomancy
(地占占星 / Geomantia Astronomica)

Reference: Gerardus Cremonensis, "Astronomical Geomancy" (12th c.),
as preserved in Burnett & Pingree, "The Liber Aristotilis of Hugo of
Santalla" and related manuscripts.

Figure → Sign mapping follows Gerard's authentic scheme where each
geomantic figure is assigned a zodiac sign via planetary rulership and
elemental affinity.
"""

from __future__ import annotations
from typing import Dict, List, Tuple

# System display names
SYSTEM_NAME_ZH = "地占占星"
SYSTEM_NAME_EN = "Astronomical Geomancy"

# ─────────────────────────────────────────────────────────────────────────────
# 16 Geomantic Figures / 十六地占圖形
# ─────────────────────────────────────────────────────────────────────────────

# Each figure: (name_en, name_zh, dots pattern [row1..row4], element, planet)
# dot pattern: each row has 1 or 2 dots  — True=single, False=double
FIGURES: Dict[str, Dict] = {
    "Acquisitio": {
        "name_en": "Acquisitio",
        "name_zh": "得益（聚財）",
        "dots": [False, False, True, False],   # ∷ ∷ · ∷
        "element": "Fire",
        "element_zh": "火",
        "planet": "Jupiter",
        "planet_zh": "木星",
        "sign": "Aries",
        "sign_zh": "白羊座",
        "sign_num": 0,
        "quality": "fortunate",
        "quality_zh": "吉",
        "keywords_zh": "獲得、收益、積累、吉祥",
        "keywords_en": "gain, acquisition, accumulation, fortunate",
    },
    "Laetitia": {
        "name_en": "Laetitia",
        "name_zh": "喜悅",
        "dots": [True, False, False, False],   # · ∷ ∷ ∷
        "element": "Fire",
        "element_zh": "火",
        "planet": "Jupiter",
        "planet_zh": "木星",
        "sign": "Taurus",
        "sign_zh": "金牛座",
        "sign_num": 1,
        "quality": "fortunate",
        "quality_zh": "吉",
        "keywords_zh": "喜悅、歡愉、成功、福祉",
        "keywords_en": "joy, delight, success, wellbeing",
    },
    "Puer": {
        "name_en": "Puer",
        "name_zh": "男孩（陽剛）",
        "dots": [False, True, True, True],     # ∷ · · ·
        "element": "Fire",
        "element_zh": "火",
        "planet": "Mars",
        "planet_zh": "火星",
        "sign": "Gemini",
        "sign_zh": "雙子座",
        "sign_num": 2,
        "quality": "neutral",
        "quality_zh": "中",
        "keywords_zh": "衝動、行動、戰鬥、男性",
        "keywords_en": "impulse, action, combat, masculine energy",
    },
    "Rubeus": {
        "name_en": "Rubeus",
        "name_zh": "赤紅",
        "dots": [False, True, False, True],    # ∷ · ∷ ·
        "element": "Fire",
        "element_zh": "火",
        "planet": "Mars",
        "planet_zh": "火星",
        "sign": "Gemini",
        "sign_zh": "雙子座",
        "sign_num": 2,
        "quality": "unfortunate",
        "quality_zh": "凶",
        "keywords_zh": "憤怒、危險、衝突、熱情過剩",
        "keywords_en": "anger, danger, conflict, excessive passion",
    },
    "Albus": {
        "name_en": "Albus",
        "name_zh": "白色（純淨）",
        "dots": [False, False, True, True],    # ∷ ∷ · ·
        "element": "Air",
        "element_zh": "風",
        "planet": "Mercury",
        "planet_zh": "水星",
        "sign": "Cancer",
        "sign_zh": "巨蟹座",
        "sign_num": 3,
        "quality": "fortunate",
        "quality_zh": "吉",
        "keywords_zh": "智慧、純淨、商業、思考",
        "keywords_en": "wisdom, purity, commerce, thought",
    },
    "Via": {
        "name_en": "Via",
        "name_zh": "道路",
        "dots": [True, True, True, True],      # · · · ·
        "element": "Water",
        "element_zh": "水",
        "planet": "Moon",
        "planet_zh": "月亮",
        "sign": "Leo",
        "sign_zh": "獅子座",
        "sign_num": 4,
        "quality": "neutral",
        "quality_zh": "中",
        "keywords_zh": "旅行、道路、流動、變化",
        "keywords_en": "travel, journey, flow, change",
    },
    "Conjunctio": {
        "name_en": "Conjunctio",
        "name_zh": "合相（連接）",
        "dots": [False, True, True, False],    # ∷ · · ∷
        "element": "Air",
        "element_zh": "風",
        "planet": "Mercury",
        "planet_zh": "水星",
        "sign": "Virgo",
        "sign_zh": "處女座",
        "sign_num": 5,
        "quality": "neutral",
        "quality_zh": "中",
        "keywords_zh": "聯合、合作、連結、相遇",
        "keywords_en": "union, cooperation, connection, meeting",
    },
    "Caput_Draconis": {
        "name_en": "Caput Draconis",
        "name_zh": "龍頭（北交點）",
        "dots": [True, False, False, True],    # · ∷ ∷ ·  (ascending node variant)
        "element": "Earth",
        "element_zh": "土",
        "planet": "Caput Draconis",
        "planet_zh": "龍頭",
        "sign": "Virgo",
        "sign_zh": "處女座",
        "sign_num": 5,
        "quality": "fortunate",
        "quality_zh": "吉",
        "keywords_zh": "上升、成長、入世、良好開端",
        "keywords_en": "ascending, growth, beginning, good fortune",
    },
    "Puella": {
        "name_en": "Puella",
        "name_zh": "女孩（陰柔）",
        "dots": [True, False, True, False],    # · ∷ · ∷
        "element": "Air",
        "element_zh": "風",
        "planet": "Venus",
        "planet_zh": "金星",
        "sign": "Libra",
        "sign_zh": "天秤座",
        "sign_num": 6,
        "quality": "fortunate",
        "quality_zh": "吉",
        "keywords_zh": "美麗、愛情、和諧、女性",
        "keywords_en": "beauty, love, harmony, feminine energy",
    },
    "Amissio": {
        "name_en": "Amissio",
        "name_zh": "失去",
        "dots": [True, False, False, True],    # · ∷ ∷ ·  (same pattern as Caput Draconis; distinguished by planet/sign)
        "element": "Fire",
        "element_zh": "火",
        "planet": "Venus",
        "planet_zh": "金星",
        "sign": "Scorpio",
        "sign_zh": "天蠍座",
        "sign_num": 7,
        "quality": "unfortunate",
        "quality_zh": "凶",
        "keywords_zh": "失去、缺乏、消耗、放棄",
        "keywords_en": "loss, lack, depletion, abandonment",
    },
    "Tristitia": {
        "name_en": "Tristitia",
        "name_zh": "悲傷",
        "dots": [False, False, False, True],   # ∷ ∷ ∷ ·
        "element": "Earth",
        "element_zh": "土",
        "planet": "Saturn",
        "planet_zh": "土星",
        "sign": "Scorpio",
        "sign_zh": "天蠍座",
        "sign_num": 7,
        "quality": "unfortunate",
        "quality_zh": "凶",
        "keywords_zh": "悲傷、困頓、延遲、孤獨",
        "keywords_en": "sorrow, difficulty, delay, isolation",
    },
    "Cauda_Draconis": {
        "name_en": "Cauda Draconis",
        "name_zh": "龍尾（南交點）",
        "dots": [False, True, True, False],    # ∷ · · ∷  (descending node variant)
        "element": "Fire",
        "element_zh": "火",
        "planet": "Cauda Draconis",
        "planet_zh": "龍尾",
        "sign": "Sagittarius",
        "sign_zh": "射手座",
        "sign_num": 8,
        "quality": "unfortunate",
        "quality_zh": "凶",
        "keywords_zh": "下降、結束、消散、業力",
        "keywords_en": "descending, ending, dissipation, karma",
    },
    "Populus": {
        "name_en": "Populus",
        "name_zh": "民眾（群體）",
        "dots": [False, False, False, False],  # ∷ ∷ ∷ ∷
        "element": "Water",
        "element_zh": "水",
        "planet": "Moon",
        "planet_zh": "月亮",
        "sign": "Capricorn",
        "sign_zh": "摩羯座",
        "sign_num": 9,
        "quality": "neutral",
        "quality_zh": "中",
        "keywords_zh": "群眾、集體、社會、多數",
        "keywords_en": "people, collective, society, majority",
    },
    "Fortuna_Major": {
        "name_en": "Fortuna Major",
        "name_zh": "大吉（大福運）",
        "dots": [False, True, False, False],   # ∷ · ∷ ∷
        "element": "Earth",
        "element_zh": "土",
        "planet": "Sun",
        "planet_zh": "太陽",
        "sign": "Aquarius",
        "sign_zh": "水瓶座",
        "sign_num": 10,
        "quality": "fortunate",
        "quality_zh": "吉",
        "keywords_zh": "大吉、強運、榮耀、內在力量",
        "keywords_en": "great fortune, strong luck, honour, inner strength",
    },
    "Fortuna_Minor": {
        "name_en": "Fortuna Minor",
        "name_zh": "小吉（小福運）",
        "dots": [True, False, True, True],     # · ∷ · ·
        "element": "Fire",
        "element_zh": "火",
        "planet": "Sun",
        "planet_zh": "太陽",
        "sign": "Leo",
        "sign_zh": "獅子座",
        "sign_num": 4,
        "quality": "fortunate",
        "quality_zh": "吉",
        "keywords_zh": "小吉、短暫好運、外在幫助",
        "keywords_en": "minor fortune, brief luck, external help",
    },
    "Carcer": {
        "name_en": "Carcer",
        "name_zh": "監獄（囚困）",
        "dots": [True, True, False, True],     # · · ∷ ·
        "element": "Earth",
        "element_zh": "土",
        "planet": "Saturn",
        "planet_zh": "土星",
        "sign": "Pisces",
        "sign_zh": "雙魚座",
        "sign_num": 11,
        "quality": "unfortunate",
        "quality_zh": "凶",
        "keywords_zh": "限制、囚困、阻礙、隔絕",
        "keywords_en": "restriction, imprisonment, obstacle, isolation",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Zodiac Signs / 十二星座
# ─────────────────────────────────────────────────────────────────────────────

ZODIAC_SIGNS: List[Dict] = [
    {"en": "Aries",       "zh": "白羊座", "glyph": "♈", "element": "Fire",  "quality": "Cardinal"},
    {"en": "Taurus",      "zh": "金牛座", "glyph": "♉", "element": "Earth", "quality": "Fixed"},
    {"en": "Gemini",      "zh": "雙子座", "glyph": "♊", "element": "Air",   "quality": "Mutable"},
    {"en": "Cancer",      "zh": "巨蟹座", "glyph": "♋", "element": "Water", "quality": "Cardinal"},
    {"en": "Leo",         "zh": "獅子座", "glyph": "♌", "element": "Fire",  "quality": "Fixed"},
    {"en": "Virgo",       "zh": "處女座", "glyph": "♍", "element": "Earth", "quality": "Mutable"},
    {"en": "Libra",       "zh": "天秤座", "glyph": "♎", "element": "Air",   "quality": "Cardinal"},
    {"en": "Scorpio",     "zh": "天蠍座", "glyph": "♏", "element": "Water", "quality": "Fixed"},
    {"en": "Sagittarius", "zh": "射手座", "glyph": "♐", "element": "Fire",  "quality": "Mutable"},
    {"en": "Capricorn",   "zh": "摩羯座", "glyph": "♑", "element": "Earth", "quality": "Cardinal"},
    {"en": "Aquarius",    "zh": "水瓶座", "glyph": "♒", "element": "Air",   "quality": "Fixed"},
    {"en": "Pisces",      "zh": "雙魚座", "glyph": "♓", "element": "Water", "quality": "Mutable"},
]

# ─────────────────────────────────────────────────────────────────────────────
# 7 Traditional Planets + Nodes / 七星 + 龍頭龍尾
# ─────────────────────────────────────────────────────────────────────────────

PLANETS: List[Dict] = [
    {"key": "Sun",             "en": "Sun",              "zh": "太陽", "glyph": "☉", "nature": "hot/dry",   "nature_zh": "熱燥", "domicile": [4]},
    {"key": "Moon",            "en": "Moon",             "zh": "月亮", "glyph": "☽", "nature": "cold/moist","nature_zh": "冷濕", "domicile": [3]},
    {"key": "Mercury",         "en": "Mercury",          "zh": "水星", "glyph": "☿", "nature": "variable",  "nature_zh": "多變", "domicile": [2, 5]},
    {"key": "Venus",           "en": "Venus",            "zh": "金星", "glyph": "♀", "nature": "cold/moist","nature_zh": "冷濕", "domicile": [1, 6]},
    {"key": "Mars",            "en": "Mars",             "zh": "火星", "glyph": "♂", "nature": "hot/dry",   "nature_zh": "熱燥", "domicile": [0, 7]},
    {"key": "Jupiter",         "en": "Jupiter",          "zh": "木星", "glyph": "♃", "nature": "hot/moist", "nature_zh": "熱濕", "domicile": [8, 11]},
    {"key": "Saturn",          "en": "Saturn",           "zh": "土星", "glyph": "♄", "nature": "cold/dry",  "nature_zh": "冷燥", "domicile": [9, 10]},
    {"key": "Caput_Draconis",  "en": "Caput Draconis",   "zh": "龍頭", "glyph": "☊", "nature": "north node","nature_zh": "北交", "domicile": [5]},
    {"key": "Cauda_Draconis",  "en": "Cauda Draconis",   "zh": "龍尾", "glyph": "☋", "nature": "south node","nature_zh": "南交", "domicile": [8]},
]

# ─────────────────────────────────────────────────────────────────────────────
# 12 House Meanings / 十二宮含義
# ─────────────────────────────────────────────────────────────────────────────

HOUSE_MEANINGS: List[Dict] = [
    {
        "house": 1, "name_en": "Life & Querent", "name_zh": "第一宮：生命宮",
        "topics_zh": "問卜者自身、生命力、外貌、個性、壽命",
        "topics_en": "querent, vitality, appearance, character, lifespan",
        "gerard_zh": "主問卜者之命，觀其壽命強弱、身形氣色",
    },
    {
        "house": 2, "name_en": "Wealth & Resources", "name_zh": "第二宮：財帛宮",
        "topics_zh": "財富、資源、動產、收入、財務狀況",
        "topics_en": "wealth, resources, moveable property, income, finances",
        "gerard_zh": "主財帛動產，觀錢財得失",
    },
    {
        "house": 3, "name_en": "Siblings & Short Journeys", "name_zh": "第三宮：兄弟宮",
        "topics_zh": "兄弟姐妹、短途旅行、通訊、鄰里",
        "topics_en": "siblings, short journeys, communication, neighbours",
        "gerard_zh": "主兄弟姐妹，短途出行，書信往來",
    },
    {
        "house": 4, "name_en": "Parents & Home", "name_zh": "第四宮：父母宮",
        "topics_zh": "父親、家庭、不動產、根基、晚年",
        "topics_en": "father, home, real estate, foundations, old age",
        "gerard_zh": "主父親、家宅、土地，亦主事業之終結",
    },
    {
        "house": 5, "name_en": "Children & Pleasure", "name_zh": "第五宮：子女宮",
        "topics_zh": "子女、歡愉、愛好、投機、信使",
        "topics_en": "children, pleasure, hobbies, speculation, messengers",
        "gerard_zh": "主子嗣、歡樂、信使，觀子女緣分",
    },
    {
        "house": 6, "name_en": "Sickness & Servants", "name_zh": "第六宮：疾厄宮",
        "topics_zh": "疾病、僕人、小動物、日常勞務",
        "topics_en": "illness, servants, small animals, daily labour",
        "gerard_zh": "主疾病、奴僕，觀健康與日常勞作",
    },
    {
        "house": 7, "name_en": "Marriage & Enemies", "name_zh": "第七宮：夫妻宮",
        "topics_zh": "婚姻、伴侶、公開敵人、合約、訴訟",
        "topics_en": "marriage, partner, open enemies, contracts, litigation",
        "gerard_zh": "主婚姻伴侶、明顯的敵人與對手",
    },
    {
        "house": 8, "name_en": "Death & Inheritance", "name_zh": "第八宮：死亡宮",
        "topics_zh": "死亡、遺產、他人資源、危險、恐懼",
        "topics_en": "death, inheritance, others' resources, danger, fear",
        "gerard_zh": "主死亡、遺產，觀死亡之期與方式",
    },
    {
        "house": 9, "name_en": "Religion & Long Journeys", "name_zh": "第九宮：遷移宮",
        "topics_zh": "宗教、哲學、長途旅行、夢境、高等學問",
        "topics_en": "religion, philosophy, long journeys, dreams, higher learning",
        "gerard_zh": "主宗教信仰、遠行、夢兆、高等學問",
    },
    {
        "house": 10, "name_en": "Career & Honour", "name_zh": "第十宮：官祿宮",
        "topics_zh": "事業、名譽、地位、君主、母親",
        "topics_en": "career, honour, status, rulers, mother",
        "gerard_zh": "主事業成就、名譽地位，觀王者之氣",
    },
    {
        "house": 11, "name_en": "Friends & Fortune", "name_zh": "第十一宮：福德宮",
        "topics_zh": "朋友、希望、援助者、社交圈",
        "topics_en": "friends, hopes, benefactors, social circle",
        "gerard_zh": "主朋友、希望、恩人，觀貴人扶助",
    },
    {
        "house": 12, "name_en": "Secrets & Misfortune", "name_zh": "第十二宮：玄密宮",
        "topics_zh": "隱藏的敵人、囚禁、自我毀滅、秘密",
        "topics_en": "hidden enemies, imprisonment, self-undoing, secrets",
        "gerard_zh": "主隱藏的敵人、囚禁與自我損耗",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Question Categories / 問題類型
# ─────────────────────────────────────────────────────────────────────────────

QUESTION_TYPES: List[Dict] = [
    {"key": "life",      "zh": "🌟 生命與命運", "en": "🌟 Life & Destiny",      "primary_house": 1},
    {"key": "health",    "zh": "⚕️ 健康與疾病", "en": "⚕️ Health & Illness",     "primary_house": 6},
    {"key": "wealth",    "zh": "💰 財富與資源", "en": "💰 Wealth & Resources",   "primary_house": 2},
    {"key": "marriage",  "zh": "💑 婚姻與感情", "en": "💑 Marriage & Love",      "primary_house": 7},
    {"key": "career",    "zh": "🏆 事業與名譽", "en": "🏆 Career & Honour",      "primary_house": 10},
    {"key": "children",  "zh": "👶 子女與生育", "en": "👶 Children & Fertility",  "primary_house": 5},
    {"key": "journey",   "zh": "✈️ 旅行與遷移", "en": "✈️ Travel & Relocation",  "primary_house": 9},
    {"key": "religion",  "zh": "🕌 宗教與靈性", "en": "🕌 Religion & Spirituality","primary_house": 9},
    {"key": "enemy",     "zh": "⚔️ 敵人與訴訟", "en": "⚔️ Enemies & Litigation",  "primary_house": 7},
    {"key": "death",     "zh": "⚰️ 死亡與遺產", "en": "⚰️ Death & Inheritance",   "primary_house": 8},
    {"key": "custom",    "zh": "💬 自訂問題",   "en": "💬 Custom Question",       "primary_house": 1},
]

# ─────────────────────────────────────────────────────────────────────────────
# Figure dot display / 圖形點陣顯示
# ─────────────────────────────────────────────────────────────────────────────

DOT_SINGLE = "•"   # single point row
DOT_DOUBLE = "∶"   # double point row

# ─────────────────────────────────────────────────────────────────────────────
# Planet friendship / 行星友好關係（Chaldean scheme）
# ─────────────────────────────────────────────────────────────────────────────

# Friendly (F), Enemy (E), Neutral (N) from each planet's perspective
PLANET_RELATIONS: Dict[str, Dict[str, str]] = {
    "Sun":     {"Moon": "F", "Mercury": "N", "Venus": "E", "Mars": "F", "Jupiter": "F", "Saturn": "E"},
    "Moon":    {"Sun": "F",  "Mercury": "N", "Venus": "F", "Mars": "E", "Jupiter": "F", "Saturn": "E"},
    "Mercury": {"Sun": "F",  "Moon": "N",    "Venus": "F", "Mars": "N", "Jupiter": "N", "Saturn": "N"},
    "Venus":   {"Sun": "N",  "Moon": "F",    "Mercury": "F","Mars": "E", "Jupiter": "F", "Saturn": "N"},
    "Mars":    {"Sun": "F",  "Moon": "E",    "Mercury": "N","Venus": "E", "Jupiter": "F", "Saturn": "F"},
    "Jupiter": {"Sun": "F",  "Moon": "F",    "Mercury": "E","Venus": "F", "Mars": "N",    "Saturn": "N"},
    "Saturn":  {"Sun": "E",  "Moon": "E",    "Mercury": "N","Venus": "N", "Mars": "F",    "Jupiter": "N"},
}

# ─────────────────────────────────────────────────────────────────────────────
# UI theme colours
# ─────────────────────────────────────────────────────────────────────────────

GEOMANCY_THEME = {
    "bg": "#0B0F1E",
    "card": "#111827",
    "gold": "#C8A24A",
    "silver": "#B0B8C8",
    "crimson": "#8B1A1A",
    "green": "#1A5C2A",
    "text": "#EDD88A",
    "dot_active": "#C8A24A",
    "dot_inactive": "#2A3040",
    "house_ring": "#1E2845",
}
