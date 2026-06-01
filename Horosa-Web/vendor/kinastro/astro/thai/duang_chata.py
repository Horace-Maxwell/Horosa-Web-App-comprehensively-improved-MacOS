"""Thai Duang Chata (ดวงชะตา) core calculation.

This module is intentionally Streamlit-free and focuses on pure computation:
- 9 graha (Sun..Saturn + Rahu/Ketu) sidereal positions via pyswisseph
- 12 bhavas with selectable house systems
- Thai-style fortune number (เลขชะตา)
- Brahma Jati profile aggregation
- Thai Nine Palace divination grid derived from Lagna, graha, and fortune number
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import swisseph as swe

HouseSystem = Literal["whole_sign", "thai_traditional", "placidus"]
BrahmaJatiGender = Literal["male", "female"]


THAI_GRAHA_IDS: Dict[str, int] = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mars": swe.MARS,
    "mercury": swe.MERCURY,
    "jupiter": swe.JUPITER,
    "venus": swe.VENUS,
    "saturn": swe.SATURN,
}

PLANET_SYMBOLS: Dict[str, str] = {
    "sun": "☉",
    "moon": "☽",
    "mars": "♂",
    "mercury": "☿",
    "jupiter": "♃",
    "venus": "♀",
    "saturn": "♄",
    "rahu": "☊",
    "ketu": "☋",
}

PLANET_COLORS: Dict[str, str] = {
    "sun": "#ff9f1c",
    "moon": "#d8e2f2",
    "mars": "#ef476f",
    "mercury": "#5fa8d3",
    "jupiter": "#ffd166",
    "venus": "#ff7eb6",
    "saturn": "#8d6a9f",
    "rahu": "#9b5de5",
    "ketu": "#4361ee",
}

PLANET_NAMES: Dict[str, Dict[str, str]] = {
    "sun": {"th": "พระอาทิตย์", "zh": "太陽", "en": "Sun"},
    "moon": {"th": "พระจันทร์", "zh": "月亮", "en": "Moon"},
    "mars": {"th": "พระอังคาร", "zh": "火星", "en": "Mars"},
    "mercury": {"th": "พระพุธ", "zh": "水星", "en": "Mercury"},
    "jupiter": {"th": "พระพฤหัสบดี", "zh": "木星", "en": "Jupiter"},
    "venus": {"th": "พระศุกร์", "zh": "金星", "en": "Venus"},
    "saturn": {"th": "พระเสาร์", "zh": "土星", "en": "Saturn"},
    "rahu": {"th": "ราหู", "zh": "羅睺", "en": "Rahu"},
    "ketu": {"th": "เกตุ", "zh": "計都", "en": "Ketu"},
}

SIGNS = [
    {"en": "Aries", "zh": "白羊", "th": "เมษ", "glyph": "♈", "ruler": "mars"},
    {"en": "Taurus", "zh": "金牛", "th": "พฤษภ", "glyph": "♉", "ruler": "venus"},
    {"en": "Gemini", "zh": "雙子", "th": "เมถุน", "glyph": "♊", "ruler": "mercury"},
    {"en": "Cancer", "zh": "巨蟹", "th": "กรกฎ", "glyph": "♋", "ruler": "moon"},
    {"en": "Leo", "zh": "獅子", "th": "สิงห์", "glyph": "♌", "ruler": "sun"},
    {"en": "Virgo", "zh": "處女", "th": "กันย์", "glyph": "♍", "ruler": "mercury"},
    {"en": "Libra", "zh": "天秤", "th": "ตุลย์", "glyph": "♎", "ruler": "venus"},
    {"en": "Scorpio", "zh": "天蠍", "th": "พิจิก", "glyph": "♏", "ruler": "mars"},
    {"en": "Sagittarius", "zh": "射手", "th": "ธนู", "glyph": "♐", "ruler": "jupiter"},
    {"en": "Capricorn", "zh": "摩羯", "th": "มกร", "glyph": "♑", "ruler": "saturn"},
    {"en": "Aquarius", "zh": "水瓶", "th": "กุมภ์", "glyph": "♒", "ruler": "saturn"},
    {"en": "Pisces", "zh": "雙魚", "th": "มีน", "glyph": "♓", "ruler": "jupiter"},
]

THAI_ZODIAC_ANIMALS = [
    {"number": 1, "en": "Rat", "zh": "鼠", "th": "ชวด"},
    {"number": 2, "en": "Ox", "zh": "牛", "th": "ฉลู"},
    {"number": 3, "en": "Tiger", "zh": "虎", "th": "ขาล"},
    {"number": 4, "en": "Rabbit", "zh": "兔", "th": "เถาะ"},
    {"number": 5, "en": "Dragon", "zh": "龍", "th": "มะโรง"},
    {"number": 6, "en": "Snake", "zh": "蛇", "th": "มะเส็ง"},
    {"number": 7, "en": "Horse", "zh": "馬", "th": "มะเมีย"},
    {"number": 8, "en": "Goat", "zh": "羊", "th": "มะแม"},
    {"number": 9, "en": "Monkey", "zh": "猴", "th": "วอก"},
    {"number": 10, "en": "Rooster", "zh": "雞", "th": "ระกา"},
    {"number": 11, "en": "Dog", "zh": "狗", "th": "จอ"},
    {"number": 12, "en": "Pig", "zh": "豬", "th": "กุน"},
]

BHAVA_MEANINGS = {
    1: {"en": "Self & vitality", "zh": "自我與體能", "th": "ตัวตนและพลังชีวิต"},
    2: {"en": "Wealth & speech", "zh": "財富與口才", "th": "ทรัพย์สินและวาจา"},
    3: {"en": "Courage & skills", "zh": "勇氣與技能", "th": "ความกล้าและทักษะ"},
    4: {"en": "Home & roots", "zh": "家庭與根基", "th": "บ้านและรากฐาน"},
    5: {"en": "Creativity & children", "zh": "創造與子女", "th": "ความคิดสร้างสรรค์และบุตร"},
    6: {"en": "Service & obstacles", "zh": "服務與挑戰", "th": "งานรับใช้และอุปสรรค"},
    7: {"en": "Partnership", "zh": "伴侶與合作", "th": "คู่ครองและหุ้นส่วน"},
    8: {"en": "Transformation", "zh": "轉化與業力", "th": "การเปลี่ยนแปลงและกรรม"},
    9: {"en": "Dharma & learning", "zh": "信念與學問", "th": "ศรัทธาและการศึกษา"},
    10: {"en": "Career & status", "zh": "事業與名望", "th": "การงานและชื่อเสียง"},
    11: {"en": "Gains & network", "zh": "收穫與人脈", "th": "ผลประโยชน์และเครือข่าย"},
    12: {"en": "Retreat & liberation", "zh": "隱退與解脫", "th": "การปล่อยวางและหลุดพ้น"},
}

HOUSE_SYSTEM_NOTES: Dict[HouseSystem, Dict[str, str]] = {
    "whole_sign": {
        "en": "Whole-sign houses start House 1 at the beginning of the ascendant sign. Each sign becomes one full bhava.",
        "zh": "整宮制以命宮所在星座的 0° 作為第一宮起點，每個星座完整對應一宮。",
        "th": "ระบบโหราศาสตร์แบบทั้งราศีเริ่มภพที่ 1 จากต้นราศีลัคนา และให้หนึ่งราศีเท่ากับหนึ่งภพเต็ม",
    },
    "thai_traditional": {
        "en": "Thai traditional houses are implemented as a sidereal equal-house wheel. House 1 begins at the exact sidereal Lagna degree, then each bhava advances by 30°.",
        "zh": "泰式傳統宮制實作為恆星黃道等宮制：第一宮從實際恆星黃道上升點（Lagna）度數起算，其後每宮順推 30°。",
        "th": "ระบบภพแบบไทยดั้งเดิมในโมดูลนี้ใช้ภพเท่าจากลัคนานิรายนะจริง โดยภพที่ 1 เริ่มที่องศาลัคนาและเลื่อนภพละ 30°",
    },
    "placidus": {
        "en": "Placidus cusps are obtained directly from Swiss Ephemeris in sidereal mode.",
        "zh": "普拉西德宮位直接使用 Swiss Ephemeris 的恆星黃道宮頭計算。",
        "th": "ระบบพลาซิดัสใช้การคำนวณจุดต้นภพจาก Swiss Ephemeris ในโหมดนิรายนะโดยตรง",
    },
}

WEEKDAY_NAMES: Dict[int, Dict[str, str]] = {
    0: {"en": "Monday", "zh": "星期一", "th": "วันจันทร์"},
    1: {"en": "Tuesday", "zh": "星期二", "th": "วันอังคาร"},
    2: {"en": "Wednesday", "zh": "星期三", "th": "วันพุธ"},
    3: {"en": "Thursday", "zh": "星期四", "th": "วันพฤหัสบดี"},
    4: {"en": "Friday", "zh": "星期五", "th": "วันศุกร์"},
    5: {"en": "Saturday", "zh": "星期六", "th": "วันเสาร์"},
    6: {"en": "Sunday", "zh": "星期日", "th": "วันอาทิตย์"},
}

NINE_PALACE_LAYOUT = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6],
]

NINE_PALACE_DIRECTIONS: Dict[int, Dict[str, str]] = {
    1: {"en": "North (Kan)", "zh": "北方（坎）", "th": "ทิศเหนือ"},
    2: {"en": "Southwest (Kun)", "zh": "西南（坤）", "th": "ทิศตะวันตกเฉียงใต้"},
    3: {"en": "East (Zhen)", "zh": "東方（震）", "th": "ทิศตะวันออก"},
    4: {"en": "Southeast (Xun)", "zh": "東南（巽）", "th": "ทิศตะวันออกเฉียงใต้"},
    5: {"en": "Centre", "zh": "中宮", "th": "ศูนย์กลาง"},
    6: {"en": "Northwest (Qian)", "zh": "西北（乾）", "th": "ทิศตะวันตกเฉียงเหนือ"},
    7: {"en": "West (Dui)", "zh": "西方（兌）", "th": "ทิศตะวันตก"},
    8: {"en": "Northeast (Gen)", "zh": "東北（艮）", "th": "ทิศตะวันออกเฉียงเหนือ"},
    9: {"en": "South (Li)", "zh": "南方（離）", "th": "ทิศใต้"},
}

NINE_PALACE_ELEMENTS: Dict[int, Dict[str, str]] = {
    1: {"en": "Water", "zh": "水", "th": "ธาตุน้ำ"},
    2: {"en": "Earth", "zh": "土", "th": "ธาตุดิน"},
    3: {"en": "Wood", "zh": "木", "th": "ธาตุไม้"},
    4: {"en": "Wood", "zh": "木", "th": "ธาตุไม้"},
    5: {"en": "Earth", "zh": "土", "th": "ธาตุดิน"},
    6: {"en": "Metal", "zh": "金", "th": "ธาตุโลหะ"},
    7: {"en": "Metal", "zh": "金", "th": "ธาตุโลหะ"},
    8: {"en": "Earth", "zh": "土", "th": "ธาตุดิน"},
    9: {"en": "Fire", "zh": "火", "th": "ธาตุไฟ"},
}

NINE_PALACE_TEMPLATES: Dict[int, Dict[str, Any]] = {
    1: {
        "guardian": "sun",
        "title": {"th": "ภพอำนาจ", "zh": "權勢宮", "en": "Authority Palace"},
        "keywords": {
            "th": ["อำนาจ", "สุขภาพ", "ชื่อเสียง"],
            "zh": ["權威", "健康", "名望"],
            "en": ["authority", "vitality", "status"],
        },
        "summary": {
            "th": "ภพนี้สะท้อนบารมี การยืนหยัด และความสามารถในการนำชีวิตของตนเอง",
            "zh": "此宮主看權柄、健康與個人威望，是九宮格中的核心外顯力量。",
            "en": "This palace reflects authority, vitality, and the visible strength of personal leadership.",
        },
    },
    2: {
        "guardian": "moon",
        "title": {"th": "ภพจิตใจ", "zh": "情感宮", "en": "Emotional Palace"},
        "keywords": {
            "th": ["จิตใจ", "ครอบครัว", "ความอ่อนโยน"],
            "zh": ["情感", "家庭", "安寧"],
            "en": ["feelings", "family", "inner peace"],
        },
        "summary": {
            "th": "ภพนี้ดูอารมณ์ ความสัมพันธ์ในบ้าน และความมั่นคงทางใจ",
            "zh": "此宮主看情緒、家宅與內在安全感。",
            "en": "This palace measures emotional tides, domestic harmony, and inner steadiness.",
        },
    },
    3: {
        "guardian": "mars",
        "title": {"th": "ภพพลัง", "zh": "行動宮", "en": "Action Palace"},
        "keywords": {
            "th": ["กล้าหาญ", "การแข่งขัน", "แรงผลักดัน"],
            "zh": ["勇氣", "競爭", "執行力"],
            "en": ["courage", "competition", "drive"],
        },
        "summary": {
            "th": "ภพนี้ชี้แรงใจ ความเด็ดขาด และวิธีเผชิญอุปสรรค",
            "zh": "此宮主看行動力、膽識與對抗壓力的方式。",
            "en": "This palace shows initiative, bravery, and how one confronts resistance.",
        },
    },
    4: {
        "guardian": "mercury",
        "title": {"th": "ภพปัญญา", "zh": "智慧宮", "en": "Wisdom Palace"},
        "keywords": {
            "th": ["ปัญญา", "การสื่อสาร", "การเรียนรู้"],
            "zh": ["智慧", "溝通", "學習"],
            "en": ["intellect", "communication", "study"],
        },
        "summary": {
            "th": "ภพนี้ดูสติปัญญา การเจรจา และความสามารถในการปรับตัว",
            "zh": "此宮主看思辨、文書、交易與應變能力。",
            "en": "This palace speaks to intelligence, speech, trade, and adaptability.",
        },
    },
    5: {
        "guardian": "jupiter",
        "title": {"th": "ภพบุญวาสนา", "zh": "福德宮", "en": "Merit Palace"},
        "keywords": {
            "th": ["บุญ", "ครูบา", "โชคดี"],
            "zh": ["福德", "貴人", "幸運"],
            "en": ["merit", "blessings", "luck"],
        },
        "summary": {
            "th": "ภพนี้สะท้อนบุญเก่า ปัญญาครู และแรงคุ้มครองจากสิ่งดีงาม",
            "zh": "此宮主看福報、老師助力、善緣與長遠幸運。",
            "en": "This palace reflects merit, teachers, benefactors, and enduring blessings.",
        },
    },
    6: {
        "guardian": "venus",
        "title": {"th": "ภพทรัพย์เสน่ห์", "zh": "姻財宮", "en": "Love and Wealth Palace"},
        "keywords": {
            "th": ["ความรัก", "เสน่ห์", "ทรัพย์สิน"],
            "zh": ["感情", "魅力", "財富"],
            "en": ["love", "attraction", "resources"],
        },
        "summary": {
            "th": "ภพนี้ดูเสน่ห์ ความสัมพันธ์ และความสุขทางวัตถุ",
            "zh": "此宮主看姻緣、美感、財貨與生活享受。",
            "en": "This palace shows relationship magnetism, beauty, and material comfort.",
        },
    },
    7: {
        "guardian": "saturn",
        "title": {"th": "ภพงานวินัย", "zh": "事業宮", "en": "Discipline Palace"},
        "keywords": {
            "th": ["การงาน", "วินัย", "ความอดทน"],
            "zh": ["事業", "紀律", "耐力"],
            "en": ["career", "discipline", "endurance"],
        },
        "summary": {
            "th": "ภพนี้ดูความรับผิดชอบ เส้นทางอาชีพ และความยืนระยะในชีวิต",
            "zh": "此宮主看事業根基、責任感與長期承受力。",
            "en": "This palace covers duty, career foundations, and long-term stamina.",
        },
    },
    8: {
        "guardian": "rahu",
        "title": {"th": "ภพการเปลี่ยนแปลง", "zh": "變局宮", "en": "Change Palace"},
        "keywords": {
            "th": ["การเปลี่ยนแปลง", "ความทะเยอทะยาน", "เคราะห์"],
            "zh": ["變動", "野心", "試煉"],
            "en": ["change", "ambition", "tests"],
        },
        "summary": {
            "th": "ภพนี้ชี้บทเรียนใหญ่ การพลิกผัน และแรงผลักให้ก้าวออกนอกกรอบ",
            "zh": "此宮主看突變、執念、外緣與非常規機會。",
            "en": "This palace tracks upheaval, ambition, foreign influences, and unconventional openings.",
        },
    },
    9: {
        "guardian": "ketu",
        "title": {"th": "ภพจิตวิญญาณ", "zh": "靈性宮", "en": "Spiritual Palace"},
        "keywords": {
            "th": ["กรรมเก่า", "สมาธิ", "การปล่อยวาง"],
            "zh": ["前世", "靈修", "放下"],
            "en": ["karma", "contemplation", "release"],
        },
        "summary": {
            "th": "ภพนี้ดูสัญชาตญาณ ความลึกทางจิตใจ และบทเรียนจากกรรมเก่า",
            "zh": "此宮主看靈修、宿業、直覺與超越執著的能力。",
            "en": "This palace reveals karmic memory, intuition, and the path of release.",
        },
    },
}

PLANET_DIGNITIES: Dict[str, Dict[str, List[int]]] = {
    "sun": {"own": [4], "exalted": [0], "debilitated": [6]},
    "moon": {"own": [3], "exalted": [1], "debilitated": [7]},
    "mars": {"own": [0, 7], "exalted": [9], "debilitated": [3]},
    "mercury": {"own": [2, 5], "exalted": [5], "debilitated": [11]},
    "jupiter": {"own": [8, 11], "exalted": [3], "debilitated": [9]},
    "venus": {"own": [1, 6], "exalted": [11], "debilitated": [5]},
    "saturn": {"own": [9, 10], "exalted": [6], "debilitated": [0]},
    "rahu": {"own": [10], "exalted": [1, 2], "debilitated": [7, 8]},
    "ketu": {"own": [7], "exalted": [7, 8], "debilitated": [1, 2]},
}

DIGNITY_STRENGTH = {"exalted": 18, "own": 12, "neutral": 0, "debilitated": -12}
DIGNITY_INFLUENCE = {"exalted": 16, "own": 12, "neutral": 7, "debilitated": 3}
PLANET_NATURE_SCORE = {
    "sun": 2,
    "moon": 4,
    "mars": -2,
    "mercury": 3,
    "jupiter": 5,
    "venus": 4,
    "saturn": -1,
    "rahu": -3,
    "ketu": -2,
}

DIGNITY_LABELS: Dict[str, Dict[str, str]] = {
    "exalted": {"en": "Exalted", "zh": "入廟", "th": "เข้มแข็งมาก"},
    "own": {"en": "Own Sign", "zh": "居旺", "th": "เรือนตน"},
    "neutral": {"en": "Neutral", "zh": "平和", "th": "ปกติ"},
    "debilitated": {"en": "Debilitated", "zh": "落陷", "th": "อ่อนกำลัง"},
}

ROLE_LABELS: Dict[str, Dict[str, str]] = {
    "guardian": {"en": "Guardian graha", "zh": "主宮星", "th": "ดาวเจ้าภพ"},
    "bhava": {"en": "Bhava occupant", "zh": "本宮落星", "th": "ดาวสถิตภพ"},
    "lagna": {"en": "Lagna ruler", "zh": "命主星", "th": "ดาวเจ้าเรือนลัคนา"},
}

REGISTRY_UPDATE_EXAMPLE: Dict[str, Any] = {
    "id": "tab_thai_duang_chata",
    "name_zh": "泰國 Duang Chata",
    "name_en": "Thai Duang Chata",
    "category": "cat_asian",
    "icon": "🇹🇭",
    "tab_key": "tab_thai_duang_chata",
    "desc_key": "desc_thai_duang_chata",
    "spinner_key": "spinner_thai_duang_chata",
    "hint_key": "sys_hint_thai_duang_chata",
    "tags": ["thai", "duang_chata", "southeast_asia", "navagraha"],
    "maturity": "beta",
    "origin_culture": "Thai",
    "tradition_period": "Traditional Thai Horasastra",
    "ai_persona_key": "info_thai_duang_chata_prompt",
}


@dataclass
class DuangPlanet:
    key: str
    symbol: str
    longitude: float
    latitude: float
    speed: float
    sign_index: int
    sign_degree: float
    house: int
    retrograde: bool


@dataclass
class DuangBhava:
    number: int
    cusp: float
    sign_index: int
    ruler: str
    meaning: Dict[str, str]
    planets: List[str] = field(default_factory=list)


@dataclass
class DuangAnnualTrend:
    target_year: int
    age: int
    activated_house: int
    activated_sign_index: int
    activated_ruler: str
    fortune_cycle_number: int
    note: Dict[str, str]


@dataclass
class BrahmaJatiVariant:
    key: str
    title: Dict[str, str]
    meaning: Dict[str, str]


@dataclass
class BrahmaJatiAnnualPosition:
    position_number: int
    inclusive_age: int
    title: Dict[str, str]
    meaning: Dict[str, str]
    level: str
    activated_nine_palace: int


@dataclass
class BrahmaJatiProfile:
    zodiac_number: int
    zodiac_year_name: Dict[str, str]
    weekday_name: Dict[str, str]
    element: Dict[str, str]
    chanya: Dict[str, str]
    mingkwan: Dict[str, str]
    personality: Dict[str, str]
    note: str
    monthly_variant: Optional[BrahmaJatiVariant] = None
    weekday_variant: Optional[BrahmaJatiVariant] = None
    lucky_color: Optional[Dict[str, str]] = None
    lucky_color_meaning: Optional[str] = None
    zodiac_talisman: Optional[str] = None
    zodiac_ritual: Optional[str] = None
    general_remedies: List[str] = field(default_factory=list)
    annual_position: Optional[BrahmaJatiAnnualPosition] = None


@dataclass
class PalaceInfluence:
    key: str
    name: Dict[str, str]
    symbol: str
    role: Dict[str, str]
    dignity: str
    dignity_label: Dict[str, str]
    score: int
    house: int
    sign_index: int


@dataclass
class NinePalaceCell:
    palace_number: int
    row: int
    col: int
    title: Dict[str, str]
    direction: Dict[str, str]
    element: Dict[str, str]
    related_bhava: int
    related_sign_index: int
    guardian_planet: str
    keywords: Dict[str, List[str]]
    main_influences: List[PalaceInfluence]
    strength: int
    strength_label: Dict[str, str]
    interpretation: Dict[str, str]
    is_fortune_activated: bool = False
    is_brahma_jati_activated: bool = False
    activation_note: Optional[Dict[str, str]] = None


@dataclass
class NinePalaceGrid:
    layout: List[List[int]]
    palaces: List[NinePalaceCell]
    fortune_activation_palace: int
    brahma_jati_activation_palace: Optional[int]
    annual_trend_house: int


@dataclass
class DuangChataChart:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    weekday: int
    weekday_name: Dict[str, str]
    julian_day_ut: float
    ayanamsa: float
    house_system: HouseSystem
    house_system_note: Dict[str, str]
    ascendant: float
    planets: List[DuangPlanet]
    houses: List[DuangBhava]
    zodiac_year_number: int
    zodiac_year_animal: Dict[str, str]
    fortune_number: int
    annual_trend: DuangAnnualTrend
    brahma_jati_profile: Optional[BrahmaJatiProfile] = None
    nine_palace_grid: Optional[NinePalaceGrid] = None


_DATA_DIR = Path(__file__).resolve().parent / "data"


def _init_swe() -> None:
    try:
        from astro.swe_init import init_swe

        init_swe()
    except Exception:
        swe.set_ephe_path("")


@lru_cache(maxsize=16)
def _load_data_file(filename: str) -> Dict[str, Any]:
    path = _DATA_DIR / filename
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _norm(deg: float) -> float:
    return deg % 360.0


def _sign_index(lon: float) -> int:
    return int(_norm(lon) // 30)


def _sign_degree(lon: float) -> float:
    return _norm(lon) % 30.0


def _planet_dignity(planet_key: str, sign_index: int) -> str:
    dignities = PLANET_DIGNITIES.get(planet_key)
    if dignities is None:
        return "neutral"
    if sign_index in dignities["exalted"]:
        return "exalted"
    if sign_index in dignities["own"]:
        return "own"
    if sign_index in dignities["debilitated"]:
        return "debilitated"
    return "neutral"


def _strength_label(score: int) -> Dict[str, str]:
    if score >= 82:
        return {"en": "Very strong", "zh": "極旺", "th": "แข็งแรงมาก"}
    if score >= 68:
        return {"en": "Strong", "zh": "偏旺", "th": "แข็งแรง"}
    if score >= 50:
        return {"en": "Balanced", "zh": "中和", "th": "สมดุล"}
    if score >= 35:
        return {"en": "Sensitive", "zh": "偏弱", "th": "อ่อนไหว"}
    return {"en": "Challenged", "zh": "受壓", "th": "ถูกกดทับ"}


def _compute_fortune_number(year: int, month: int, day: int) -> tuple[int, Dict[str, str]]:
    animal = THAI_ZODIAC_ANIMALS[(year - 4) % 12]
    total = int(animal["number"]) + int(month) + int(day)
    total = ((total - 1) % 9) + 1
    return total, animal


def _whole_sign_cusps(ascendant: float) -> List[float]:
    asc_sign = _sign_index(ascendant)
    return [((asc_sign + i) % 12) * 30.0 for i in range(12)]


def _thai_equal_cusps(ascendant: float) -> List[float]:
    return [_norm(ascendant + i * 30.0) for i in range(12)]


def _resolve_house_cusps(
    *,
    jd_ut: float,
    latitude: float,
    longitude: float,
    ascendant: float,
    house_system: HouseSystem,
) -> List[float]:
    """Resolve house cusps for the requested system.

    The Thai traditional implementation deliberately uses equal 30° houses from
    the exact sidereal ascendant degree. This differs from whole-sign houses,
    where House 1 starts at the beginning of the ascendant sign.
    """
    if house_system == "whole_sign":
        return _whole_sign_cusps(ascendant)
    if house_system == "thai_traditional":
        return _thai_equal_cusps(ascendant)
    if house_system == "placidus":
        placidus_cusps, _ = swe.houses_ex(jd_ut, latitude, longitude, b"P", swe.FLG_SIDEREAL)
        return [_norm(placidus_cusps[i]) for i in range(12)]
    raise ValueError(f"Unsupported house_system: {house_system}")


def _planet_house_by_cusps(lon: float, cusps: List[float]) -> int:
    lon = _norm(lon)
    for i in range(12):
        start = _norm(cusps[i])
        end = _norm(cusps[(i + 1) % 12])
        if start < end:
            if start <= lon < end:
                return i + 1
        else:
            if lon >= start or lon < end:
                return i + 1
    return 1


def _planet_house_whole_sign(lon: float, ascendant: float) -> int:
    return ((_sign_index(lon) - _sign_index(ascendant)) % 12) + 1


def _build_annual_trend(
    *,
    birth_year: int,
    target_year: int,
    fortune_number: int,
    houses: List[DuangBhava],
) -> DuangAnnualTrend:
    age = max(0, target_year - birth_year)
    activated_house = (age % 12) + 1
    active = houses[activated_house - 1]
    cycle = ((fortune_number + target_year) % 9) or 9
    note = {
        "en": (
            f"Year focus on House {activated_house} ({BHAVA_MEANINGS[activated_house]['en']}). "
            f"Fortune cycle number {cycle} emphasizes practical pacing and consistency."
        ),
        "zh": (
            f"今年重點在第 {activated_house} 宮（{BHAVA_MEANINGS[activated_house]['zh']}），"
            f"命數循環 {cycle} 建議採取務實、穩定節奏。"
        ),
        "th": (
            f"ปีนี้เน้นภพที่ {activated_house} ({BHAVA_MEANINGS[activated_house]['th']}) "
            f"เลขวัฏจักร {cycle} เน้นความสม่ำเสมอและการวางแผนเชิงปฏิบัติ"
        ),
    }
    return DuangAnnualTrend(
        target_year=target_year,
        age=age,
        activated_house=activated_house,
        activated_sign_index=active.sign_index,
        activated_ruler=active.ruler,
        fortune_cycle_number=cycle,
        note=note,
    )


def _month_variant(month: int, thai_year_name: str) -> Optional[BrahmaJatiVariant]:
    monthly_data = _load_data_file("brahma_jati_monthly_variants.json")
    year_entry = monthly_data.get("years", {}).get(thai_year_name, {})
    for months_key, variant in year_entry.get("variants", {}).items():
        months = {int(part) for part in months_key.split("-")}
        if month in months:
            return BrahmaJatiVariant(
                key=months_key,
                title={
                    "th": variant.get("type_thai", ""),
                    "zh": variant.get("type_zh", ""),
                    "en": variant.get("type_en", ""),
                },
                meaning={
                    "th": variant.get("meaning_thai", variant.get("meaning_zh", "")),
                    "zh": variant.get("meaning_zh", ""),
                    "en": variant.get("meaning_en", ""),
                },
            )
    return None


def _weekday_variant(weekday_name_en: str, thai_year_name: str) -> Optional[BrahmaJatiVariant]:
    weekly_data = _load_data_file("brahma_jati_weekly_variants.json")
    year_entry = weekly_data.get("years", {}).get(thai_year_name, {})
    variant = year_entry.get("weekly", {}).get(weekday_name_en)
    if not variant:
        return None
    return BrahmaJatiVariant(
        key=weekday_name_en,
        title={
            "th": variant.get("type_thai", variant.get("type_en", "")),
            "zh": variant.get("type_zh", ""),
            "en": variant.get("type_en", ""),
        },
        meaning={
            "th": variant.get("meaning_thai", variant.get("meaning_en", "")),
            "zh": variant.get("meaning_zh", ""),
            "en": variant.get("meaning_en", ""),
        },
    )


def _annual_brahma_jati_position(
    *,
    birth_year: int,
    target_year: int,
    gender: BrahmaJatiGender,
) -> BrahmaJatiAnnualPosition:
    """Compute the annual Brahma Jati wheel position.

    The annual wheel counts inclusively from the birth year, so the birth year is
    treated as age 1 on the 12-position wheel. Male charts count forward from
    เจดีย์, while female charts count backward.
    """
    annual_data = _load_data_file("brahma_jati_12rasi.json")
    positions = annual_data.get("positions", {})
    inclusive_age = max(1, target_year - birth_year + 1)
    if gender == "male":
        position_number = ((inclusive_age - 1) % 12) + 1
    else:
        position_number = ((1 - inclusive_age) % 12) + 1
    position = positions[str(position_number)]
    activated_nine_palace = ((position_number - 1) % 9) + 1
    return BrahmaJatiAnnualPosition(
        position_number=position_number,
        inclusive_age=inclusive_age,
        title={
            "th": position.get("thai", ""),
            "zh": position.get("name_zh", ""),
            "en": position.get("name_en", ""),
        },
        meaning={
            "th": position.get("meaning_thai", position.get("meaning_en", "")),
            "zh": position.get("meaning_zh", ""),
            "en": position.get("meaning_en", ""),
        },
        level=position.get("level", ""),
        activated_nine_palace=activated_nine_palace,
    )


def compute_brahma_jati_profile(
    *,
    birth_year: int,
    month: int,
    weekday: int,
    target_year: Optional[int] = None,
    gender: BrahmaJatiGender = "male",
) -> BrahmaJatiProfile:
    """Combine Thai Brahma Jati birth-year, month, weekday, and annual wheel data."""
    animal = THAI_ZODIAC_ANIMALS[(birth_year - 4) % 12]
    thai_year_name = f"ปี{animal['th']}"
    weekday_name = WEEKDAY_NAMES.get(weekday, WEEKDAY_NAMES[0])

    birthyear_data = _load_data_file("brahma_jati_birthyear.json")
    birthyear_entry = birthyear_data.get("years", {}).get(str(animal["number"]), {})

    remedies_data = _load_data_file("brahma_jati_spells_remedies.json")
    color_entry = remedies_data.get("color_by_day", {}).get(weekday_name["en"])
    zodiac_remedy = remedies_data.get("per_zodiac", {}).get(thai_year_name, {})
    general_remedies = [
        text
        for _, text in sorted(remedies_data.get("general_remedies", {}).items(), key=lambda item: item[0])
    ]

    return BrahmaJatiProfile(
        zodiac_number=animal["number"],
        zodiac_year_name={"th": thai_year_name, "zh": birthyear_entry.get("name_zh", ""), "en": birthyear_entry.get("name_en", "")},
        weekday_name=weekday_name,
        element={
            "th": birthyear_entry.get("element_thai", ""),
            "zh": birthyear_entry.get("element_zh", ""),
            "en": birthyear_entry.get("element_en", ""),
        },
        chanya={
            "th": birthyear_entry.get("chanya_thai", ""),
            "zh": birthyear_entry.get("chanya_zh", ""),
            "en": birthyear_entry.get("chanya_en", ""),
        },
        mingkwan={
            "th": birthyear_entry.get("mingkwan_thai", ""),
            "zh": birthyear_entry.get("mingkwan_zh", ""),
            "en": birthyear_entry.get("mingkwan_en", ""),
        },
        personality={
            "th": birthyear_entry.get("personality_thai", birthyear_entry.get("personality_en", "")),
            "zh": birthyear_entry.get("personality_zh", ""),
            "en": birthyear_entry.get("personality_en", ""),
        },
        note=birthyear_entry.get("note", ""),
        monthly_variant=_month_variant(month, thai_year_name),
        weekday_variant=_weekday_variant(weekday_name["en"], thai_year_name),
        lucky_color={
            "th": color_entry.get("thai", ""),
            "zh": color_entry.get("zh", ""),
            "en": color_entry.get("en", ""),
        }
        if color_entry
        else None,
        lucky_color_meaning=color_entry.get("meaning") if color_entry else None,
        zodiac_talisman=zodiac_remedy.get("talisman"),
        zodiac_ritual=zodiac_remedy.get("ritual"),
        general_remedies=general_remedies,
        annual_position=_annual_brahma_jati_position(
            birth_year=birth_year,
            target_year=target_year or date.today().year,
            gender=gender,
        ),
    )


def _planet_influence(
    *,
    planet: DuangPlanet,
    role_key: str,
) -> PalaceInfluence:
    dignity = _planet_dignity(planet.key, planet.sign_index)
    return PalaceInfluence(
        key=planet.key,
        name=PLANET_NAMES[planet.key],
        symbol=planet.symbol,
        role=ROLE_LABELS[role_key],
        dignity=dignity,
        dignity_label=DIGNITY_LABELS[dignity],
        score=max(1, DIGNITY_INFLUENCE[dignity] + PLANET_NATURE_SCORE[planet.key]),
        house=planet.house,
        sign_index=planet.sign_index,
    )


def compute_nine_palace_grid(
    chart: DuangChataChart,
    *,
    brahma_jati_profile: Optional[BrahmaJatiProfile] = None,
) -> NinePalaceGrid:
    """Build a Thai Nine Palace (九宮格) grid from a full Duang Chata chart.

    Each palace is anchored to one graha in the traditional nine-graha sequence
    and then refined by:
    - the guardian graha's dignity and house placement
    - planets occupying the corresponding bhava (1..9)
    - resonance from Lagna lord, fortune number, and annual activation
    """
    profile = brahma_jati_profile or chart.brahma_jati_profile
    planet_map = {planet.key: planet for planet in chart.planets}
    lagna_ruler = SIGNS[_sign_index(chart.ascendant)]["ruler"]
    fortune_activation_palace = chart.fortune_number
    brahma_activation_palace = (
        profile.annual_position.activated_nine_palace if profile and profile.annual_position else None
    )

    palace_cells: List[NinePalaceCell] = []
    for row_index, row in enumerate(NINE_PALACE_LAYOUT):
        for col_index, palace_number in enumerate(row):
            template = NINE_PALACE_TEMPLATES[palace_number]
            guardian_key = template["guardian"]
            guardian = planet_map[guardian_key]
            bhava = chart.houses[palace_number - 1]
            guardian_dignity = _planet_dignity(guardian.key, guardian.sign_index)

            influence_keys: List[tuple[str, str]] = [(guardian.key, "guardian")]
            for planet_key in bhava.planets:
                if planet_key != guardian.key:
                    influence_keys.append((planet_key, "bhava"))
            if lagna_ruler not in {key for key, _ in influence_keys}:
                influence_keys.append((lagna_ruler, "lagna"))

            influences = [
                _planet_influence(planet=planet_map[key], role_key=role_key)
                for key, role_key in influence_keys
            ]
            influences.sort(key=lambda influence: influence.score, reverse=True)

            strength = 48
            strength += DIGNITY_STRENGTH[guardian_dignity]
            if guardian.house == palace_number:
                strength += 8
            if guardian.key == lagna_ruler:
                strength += 6
            if chart.annual_trend.activated_house == palace_number:
                strength += 7
            if palace_number == fortune_activation_palace:
                strength += 10
            if brahma_activation_palace == palace_number:
                strength += 12
            for influence in influences[1:]:
                strength += max(-3, influence.score - 8)
            strength = max(12, min(98, strength))
            strength_label = _strength_label(strength)

            top_names_en = ", ".join(PLANET_NAMES[item.key]["en"] for item in influences[:3])
            top_names_zh = "、".join(PLANET_NAMES[item.key]["zh"] for item in influences[:3])
            top_names_th = " · ".join(PLANET_NAMES[item.key]["th"] for item in influences[:3])

            activation_note: Optional[Dict[str, str]] = None
            if brahma_activation_palace == palace_number and profile and profile.annual_position:
                activation_note = {
                    "en": (
                        f"Brahma Jati annual wheel activates this palace via position "
                        f"{profile.annual_position.position_number} ({profile.annual_position.title['en']})."
                    ),
                    "zh": (
                        f"婆羅門命輪今年落在第 {profile.annual_position.position_number} 位"
                        f"（{profile.annual_position.title['zh']}），因此啟動此宮。"
                    ),
                    "th": (
                        f"ปีนี้พรหมชาติเดินถึงตำแหน่งที่ {profile.annual_position.position_number} "
                        f"({profile.annual_position.title['th']}) จึงกระตุ้นภพนี้เด่นเป็นพิเศษ"
                    ),
                }
            elif palace_number == fortune_activation_palace:
                activation_note = {
                    "en": f"Fortune number {chart.fortune_number} resonates directly with this palace.",
                    "zh": f"命數 {chart.fortune_number} 與此宮共振，因此此宮更容易顯化。",
                    "th": f"เลขชะตา {chart.fortune_number} สัมพันธ์กับภพนี้โดยตรง จึงเป็นภพที่ออกผลไว",
                }

            interpretation = {
                "en": (
                    f"{template['summary']['en']} {PLANET_NAMES[guardian.key]['en']} is {DIGNITY_LABELS[guardian_dignity]['en'].lower()} "
                    f"in {SIGNS[guardian.sign_index]['en']} and influences this palace through House {guardian.house}. "
                    f"Main influences: {top_names_en}."
                ),
                "zh": (
                    f"{template['summary']['zh']}{PLANET_NAMES[guardian.key]['zh']}在{SIGNS[guardian.sign_index]['zh']}，"
                    f"屬於{DIGNITY_LABELS[guardian_dignity]['zh']}狀態，並從第 {guardian.house} 宮引動此宮。"
                    f"主要作用星：{top_names_zh}。"
                ),
                "th": (
                    f"{template['summary']['th']} {PLANET_NAMES[guardian.key]['th']}อยู่ราศี{SIGNS[guardian.sign_index]['th']} "
                    f"ในสถานะ{DIGNITY_LABELS[guardian_dignity]['th']} และส่งผลจากภพที่ {guardian.house}. "
                    f"ดาวเด่นร่วม: {top_names_th}"
                ),
            }

            palace_cells.append(
                NinePalaceCell(
                    palace_number=palace_number,
                    row=row_index,
                    col=col_index,
                    title=template["title"],
                    direction=NINE_PALACE_DIRECTIONS[palace_number],
                    element=NINE_PALACE_ELEMENTS[palace_number],
                    related_bhava=bhava.number,
                    related_sign_index=bhava.sign_index,
                    guardian_planet=guardian.key,
                    keywords=template["keywords"],
                    main_influences=influences[:3],
                    strength=strength,
                    strength_label=strength_label,
                    interpretation=interpretation,
                    is_fortune_activated=palace_number == fortune_activation_palace,
                    is_brahma_jati_activated=palace_number == brahma_activation_palace,
                    activation_note=activation_note,
                )
            )

    palace_cells.sort(key=lambda item: item.palace_number)
    return NinePalaceGrid(
        layout=NINE_PALACE_LAYOUT,
        palaces=palace_cells,
        fortune_activation_palace=fortune_activation_palace,
        brahma_jati_activation_palace=brahma_activation_palace,
        annual_trend_house=chart.annual_trend.activated_house,
    )


def compute_duang_chata(
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    house_system: HouseSystem = "whole_sign",
    target_year: Optional[int] = None,
    brahma_jati_gender: BrahmaJatiGender = "male",
) -> DuangChataChart:
    """Compute a Thai Duang Chata chart with Brahma Jati and Nine Palace data."""
    _init_swe()
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    decimal_hour_ut = hour + minute / 60.0 - timezone
    jd_ut = swe.julday(year, month, day, decimal_hour_ut)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)

    _, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b"W", swe.FLG_SIDEREAL)
    ascendant = _norm(ascmc[0])
    cusps = _resolve_house_cusps(
        jd_ut=jd_ut,
        latitude=latitude,
        longitude=longitude,
        ascendant=ascendant,
        house_system=house_system,
    )

    planets: List[DuangPlanet] = []
    for key, pid in THAI_GRAHA_IDS.items():
        result, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        lon = _norm(result[0])
        lat = result[1]
        speed = result[3]
        house = (
            _planet_house_whole_sign(lon, ascendant)
            if house_system == "whole_sign"
            else _planet_house_by_cusps(lon, cusps)
        )
        planets.append(
            DuangPlanet(
                key=key,
                symbol=PLANET_SYMBOLS[key],
                longitude=lon,
                latitude=lat,
                speed=speed,
                sign_index=_sign_index(lon),
                sign_degree=_sign_degree(lon),
                house=house,
                retrograde=speed < 0,
            )
        )

    rahu_raw, _ = swe.calc_ut(jd_ut, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _norm(rahu_raw[0])
    ketu_lon = _norm(rahu_lon + 180.0)
    for key, lon, lat in (("rahu", rahu_lon, rahu_raw[1]), ("ketu", ketu_lon, -rahu_raw[1])):
        house = (
            _planet_house_whole_sign(lon, ascendant)
            if house_system == "whole_sign"
            else _planet_house_by_cusps(lon, cusps)
        )
        planets.append(
            DuangPlanet(
                key=key,
                symbol=PLANET_SYMBOLS[key],
                longitude=lon,
                latitude=lat,
                speed=rahu_raw[3],
                sign_index=_sign_index(lon),
                sign_degree=_sign_degree(lon),
                house=house,
                retrograde=True,
            )
        )

    houses: List[DuangBhava] = []
    for index in range(12):
        sign_idx = _sign_index(cusps[index])
        houses.append(
            DuangBhava(
                number=index + 1,
                cusp=_norm(cusps[index]),
                sign_index=sign_idx,
                ruler=SIGNS[sign_idx]["ruler"],
                meaning=BHAVA_MEANINGS[index + 1],
                planets=[],
            )
        )

    for planet in planets:
        houses[planet.house - 1].planets.append(planet.key)

    weekday = date(year, month, day).weekday()
    fortune_number, animal = _compute_fortune_number(year, month, day)
    target_year_value = target_year or date.today().year
    annual_trend = _build_annual_trend(
        birth_year=year,
        target_year=target_year_value,
        fortune_number=fortune_number,
        houses=houses,
    )
    brahma_jati_profile = compute_brahma_jati_profile(
        birth_year=year,
        month=month,
        weekday=weekday,
        target_year=target_year_value,
        gender=brahma_jati_gender,
    )

    chart = DuangChataChart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        weekday=weekday,
        weekday_name=WEEKDAY_NAMES[weekday],
        julian_day_ut=jd_ut,
        ayanamsa=ayanamsa,
        house_system=house_system,
        house_system_note=HOUSE_SYSTEM_NOTES[house_system],
        ascendant=ascendant,
        planets=planets,
        houses=houses,
        zodiac_year_number=animal["number"],
        zodiac_year_animal=animal,
        fortune_number=fortune_number,
        annual_trend=annual_trend,
        brahma_jati_profile=brahma_jati_profile,
    )
    chart.nine_palace_grid = compute_nine_palace_grid(chart, brahma_jati_profile=brahma_jati_profile)
    return chart


def chart_to_dict(chart: DuangChataChart) -> Dict[str, Any]:
    """Lightweight serializer for API, renderer, and AI prompt usage."""
    return {
        "birth": {
            "year": chart.year,
            "month": chart.month,
            "day": chart.day,
            "hour": chart.hour,
            "minute": chart.minute,
            "timezone": chart.timezone,
            "latitude": chart.latitude,
            "longitude": chart.longitude,
            "location_name": chart.location_name,
            "weekday": chart.weekday,
            "weekday_name": chart.weekday_name,
        },
        "meta": {
            "julian_day_ut": chart.julian_day_ut,
            "ayanamsa": chart.ayanamsa,
            "house_system": chart.house_system,
            "house_system_note": chart.house_system_note,
            "ascendant": chart.ascendant,
        },
        "zodiac_year_number": chart.zodiac_year_number,
        "zodiac_year_animal": chart.zodiac_year_animal,
        "fortune_number": chart.fortune_number,
        "planets": [
            {
                "key": planet.key,
                "symbol": planet.symbol,
                "longitude": planet.longitude,
                "latitude": planet.latitude,
                "sign_index": planet.sign_index,
                "sign_degree": planet.sign_degree,
                "house": planet.house,
                "retrograde": planet.retrograde,
            }
            for planet in chart.planets
        ],
        "houses": [
            {
                "number": house.number,
                "cusp": house.cusp,
                "sign_index": house.sign_index,
                "ruler": house.ruler,
                "meaning": house.meaning,
                "planets": house.planets,
            }
            for house in chart.houses
        ],
        "annual_trend": {
            "target_year": chart.annual_trend.target_year,
            "age": chart.annual_trend.age,
            "activated_house": chart.annual_trend.activated_house,
            "activated_sign_index": chart.annual_trend.activated_sign_index,
            "activated_ruler": chart.annual_trend.activated_ruler,
            "fortune_cycle_number": chart.annual_trend.fortune_cycle_number,
            "note": chart.annual_trend.note,
        },
        "brahma_jati_profile": asdict(chart.brahma_jati_profile) if chart.brahma_jati_profile else None,
        "nine_palace_grid": asdict(chart.nine_palace_grid) if chart.nine_palace_grid else None,
    }


if __name__ == "__main__":
    example_chart = compute_duang_chata(
        year=1992,
        month=7,
        day=14,
        hour=9,
        minute=30,
        timezone=7.0,
        latitude=13.7563,
        longitude=100.5018,
        location_name="Bangkok",
        house_system="thai_traditional",
        target_year=date.today().year,
    )
    payload = chart_to_dict(example_chart)
    print(
        json.dumps(
            {
                "fortune_number": payload["fortune_number"],
                "house_system": payload["meta"]["house_system"],
                "brahma_jati_activation_palace": payload["nine_palace_grid"]["brahma_jati_activation_palace"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
