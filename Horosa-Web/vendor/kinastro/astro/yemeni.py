"""
astro/yemeni.py — 也門占星 (Yemeni / South Arabian / Rasulid Astrology)

也門占星是南阿拉伯半島最古老的占星傳統之一，源自公元前 8 世紀的示巴王國
（Kingdom of Saba'），在 13 世紀 Rasulid 王朝統治時期達到頂峰。

核心文獻：
  al-Malik al-Ashraf ʿUmar ibn Yūsuf 的
  《Kitāb al-Tabṣira fī ʿIlm al-Nujūm》（星學洞見之書）

本模組重點在「也門本土 Rasulid 月宿魔法傳統」，與 arabian.py 的廣義伊斯蘭-
波斯阿拉伯占星明確區隔。核心特色包括：

1. 28 個月宿（Manazil）的 Talismanic Magic（護符魔法）、醫療與農業擇時
2. Anwā' 天氣星宿預兆
3. 附庸星（Affiliated / Subsidiary Planets）傳統
4. 阿拉伯點與 Firdaria 週期

架構 100% 模仿 astro/western/hellenistic.py，使用 sidereal zodiac 計算。
"""
import math
import streamlit as st
import swisseph as swe
from dataclasses import dataclass, field

from astro.i18n import t

# ============================================================
# Sidereal Ayanamsa Mode
# ============================================================
YEMENI_AYANAMSA_MODE = swe.SIDM_LAHIRI

# ============================================================
# 12 宮黃道 — 阿拉伯標準名（也門傳統）
# ============================================================
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_CN = {
    "Aries": "白羊座", "Taurus": "金牛座", "Gemini": "雙子座", "Cancer": "巨蟹座",
    "Leo": "獅子座", "Virgo": "處女座", "Libra": "天秤座", "Scorpio": "天蠍座",
    "Sagittarius": "射手座", "Capricorn": "摩羯座", "Aquarius": "水瓶座", "Pisces": "雙魚座",
}
SIGN_AR = {
    "Aries": "الحمل", "Taurus": "الثور", "Gemini": "الجوزاء",
    "Cancer": "السرطان", "Leo": "الأسد", "Virgo": "السنبلة",
    "Libra": "الميزان", "Scorpio": "العقرب", "Sagittarius": "القوس",
    "Capricorn": "الجدي", "Aquarius": "الدلو", "Pisces": "الحوت",
}

# ============================================================
# 28 月宿（Manazil）— al-Malik al-Ashraf 傳統完整列表
# (index, transliteration, arabic, chinese, english, stars, fortune)
# ============================================================
YEMENI_MANAZIL = [
    ("0",  "Al-Sharatan",    "الشرطان",   "角宿 / 雙角",     "The Two Signs",         "β γ Ari",       "吉 - 開創、護符製作"),
    ("1",  "Al-Butain",      "البطين",    "胃宿",           "The Little Belly",      "ε δ ρ Ari",     "中性 - 穩定"),
    ("2",  "Al-Thurayya",    "الثريا",    "昴宿",           "The Pleiades",          "η Tau (Pleiades)", "吉 - 農業、財運"),
    ("3",  "Al-Dabaran",     "الدبران",   "畢宿",           "The Follower",          "α Tau (Aldebaran)", "凶 - 衝突、分離"),
    ("4",  "Al-Haqʿa",       "الهقعة",    "觜宿",           "The White Spot",        "λ φ Ori",       "凶 - 疾病"),
    ("5",  "Al-Hanʿa",       "الهنعة",    "參宿",           "The Mark",              "γ ξ Gem",       "吉 - 教育、學問"),
    ("6",  "Al-Dhiraʿ",      "الذراع",    "井宿",           "The Forearm",           "α β Gem (Castor & Pollux)", "吉 - 友誼、合作"),
    ("7",  "Al-Nathra",      "النثرة",    "鬼宿",           "The Gap / Nostrils",    "ε γ δ Cnc (Praesepe)", "中性 - 內省"),
    ("8",  "Al-Tarf",        "الطرف",     "柳宿",           "The Glance / Eye",      "κ Cnc, λ Leo",  "凶 - 爭訟"),
    ("9",  "Al-Jabha",       "الجبهة",    "星宿",           "The Forehead",          "ζ γ η α Leo",   "吉 - 領導、榮耀"),
    ("10", "Al-Zubra",       "الزبرة",    "張宿",           "The Mane",              "δ θ Leo",       "吉 - 婚姻、伴侶"),
    ("11", "Al-Sarfa",       "الصرفة",    "翼宿",           "The Changer",           "β Leo (Denebola)", "中性 - 變革、轉換"),
    ("12", "Al-ʿAwwa",       "العواء",    "軫宿",           "The Barker / Howler",   "β η γ δ ε Vir", "吉 - 收穫、療癒"),
    ("13", "Al-Simak",       "السماك",    "角宿 (西)",      "The Unarmed / Spike",   "α Vir (Spica)", "大吉 - 護符、豐收"),
    ("14", "Al-Ghafr",       "الغفر",     "亢宿",           "The Covering",          "ι κ λ Vir",     "中性 - 隱藏、休養"),
    ("15", "Al-Zubana",      "الزبانى",   "氐宿",           "The Claws",             "α β Lib",       "凶 - 訴訟"),
    ("16", "Al-Iklil",       "الإكليل",   "房宿",           "The Crown",             "β δ π Sco",     "吉 - 權力、尊貴"),
    ("17", "Al-Qalb",        "القلب",     "心宿",           "The Heart",             "α Sco (Antares)", "凶 - 危險、毀滅"),
    ("18", "Al-Shawla",      "الشولة",    "尾宿",           "The Sting",             "λ υ Sco",       "凶 - 報復"),
    ("19", "Al-Naʿaʾim",     "النعائم",   "箕宿",           "The Ostriches",         "γ δ ε η Sgr",   "吉 - 旅行、冒險"),
    ("20", "Al-Baldah",      "البلدة",    "斗宿",           "The City / Empty Place","(void in Sgr)", "中性 - 空虛、等待"),
    ("21", "Saʿd al-Dhabih", "سعد الذابح", "牛宿",           "Luck of the Slaughterer","α β Cap",      "中性 - 犧牲"),
    ("22", "Saʿd Bulaʿ",     "سعد بلع",   "女宿",           "Luck of the Swallower", "ν μ Cap",       "凶 - 吞噬"),
    ("23", "Saʿd al-Suʿud",  "سعد السعود", "虛宿",           "Luckiest of the Lucky", "β Aqr, ξ Aqr",  "大吉 - 最大吉祥"),
    ("24", "Saʿd al-Akhbiya","سعد الأخبية","危宿",           "Luck of the Tents",     "γ Aqr, ζ Aqr, η Aqr", "吉 - 庇護、安居"),
    ("25", "Al-Fargh al-Muqaddam", "الفرغ المقدم", "室宿",  "The Front Spout",       "α β Peg",       "吉 - 建設"),
    ("26", "Al-Fargh al-Muʾakhkhar","الفرغ المؤخر","壁宿",   "The Rear Spout",        "γ Peg, α And",  "吉 - 完工"),
    ("27", "Al-Risha",       "الرشاء",    "魚腹 / 繩宿",    "The Cord / Belly of the Fish", "β And",  "吉 - 完成、療癒"),
]

# ============================================================
# 附庸星（Affiliated Planets）— Rasulid 也門特有
# 每個月宿對應一個主要行星守護，依 al-Ashraf 文獻
# ============================================================
YEMENI_AFFILIATED_STARS = {
    "Al-Sharatan":    {"planet": "Mars",    "element": "Fire",  "cn": "火星主管"},
    "Al-Butain":      {"planet": "Venus",   "element": "Earth", "cn": "金星主管"},
    "Al-Thurayya":    {"planet": "Moon",    "element": "Water", "cn": "月亮主管"},
    "Al-Dabaran":     {"planet": "Mars",    "element": "Fire",  "cn": "火星主管"},
    "Al-Haqʿa":       {"planet": "Mercury", "element": "Air",   "cn": "水星主管"},
    "Al-Hanʿa":       {"planet": "Jupiter", "element": "Air",   "cn": "木星主管"},
    "Al-Dhiraʿ":      {"planet": "Venus",   "element": "Water", "cn": "金星主管"},
    "Al-Nathra":       {"planet": "Moon",    "element": "Water", "cn": "月亮主管"},
    "Al-Tarf":        {"planet": "Saturn",  "element": "Fire",  "cn": "土星主管"},
    "Al-Jabha":       {"planet": "Sun",     "element": "Fire",  "cn": "太陽主管"},
    "Al-Zubra":       {"planet": "Venus",   "element": "Fire",  "cn": "金星主管"},
    "Al-Sarfa":       {"planet": "Sun",     "element": "Fire",  "cn": "太陽主管"},
    "Al-ʿAwwa":       {"planet": "Mercury", "element": "Air",   "cn": "水星主管"},
    "Al-Simak":       {"planet": "Venus",   "element": "Earth", "cn": "金星主管"},
    "Al-Ghafr":       {"planet": "Mars",    "element": "Fire",  "cn": "火星主管"},
    "Al-Zubana":      {"planet": "Jupiter", "element": "Air",   "cn": "木星主管"},
    "Al-Iklil":       {"planet": "Mars",    "element": "Water", "cn": "火星主管"},
    "Al-Qalb":        {"planet": "Mars",    "element": "Fire",  "cn": "火星主管"},
    "Al-Shawla":      {"planet": "Saturn",  "element": "Water", "cn": "土星主管"},
    "Al-Naʿaʾim":     {"planet": "Jupiter", "element": "Fire",  "cn": "木星主管"},
    "Al-Baldah":      {"planet": "Saturn",  "element": "Earth", "cn": "土星主管"},
    "Saʿd al-Dhabih": {"planet": "Saturn",  "element": "Earth", "cn": "土星主管"},
    "Saʿd Bulaʿ":     {"planet": "Saturn",  "element": "Water", "cn": "土星主管"},
    "Saʿd al-Suʿud":  {"planet": "Jupiter", "element": "Air",   "cn": "木星主管"},
    "Saʿd al-Akhbiya":{"planet": "Moon",    "element": "Water", "cn": "月亮主管"},
    "Al-Fargh al-Muqaddam": {"planet": "Mars", "element": "Air", "cn": "火星主管"},
    "Al-Fargh al-Muʾakhkhar":{"planet":"Mercury","element":"Air","cn": "水星主管"},
    "Al-Risha":       {"planet": "Venus",   "element": "Water", "cn": "金星主管"},
}

# ============================================================
# 護符魔法屬性 — YEMENI_TALISMANIC_PROPERTIES
# 每個月宿的 Rasulid 護符用途（依 al-Ashraf 文獻）
# ============================================================
YEMENI_TALISMANIC_PROPERTIES = {
    "Al-Sharatan":    {"use": "開創新事業、製作旅行護符", "use_en": "Initiate ventures, travel talismans", "incense": "乳香", "metal": "鐵"},
    "Al-Butain":      {"use": "尋找失物、穩定情勢", "use_en": "Finding lost items, stabilization", "incense": "玫瑰", "metal": "銅"},
    "Al-Thurayya":    {"use": "農業豐收、招財護符", "use_en": "Agricultural prosperity, wealth charms", "incense": "沒藥", "metal": "銀"},
    "Al-Dabaran":     {"use": "護身符防小人、驅邪", "use_en": "Protection amulets, warding off evil", "incense": "檀香", "metal": "鐵"},
    "Al-Haqʿa":       {"use": "學習魔法、提升智慧", "use_en": "Study magic, enhance wisdom", "incense": "桂皮", "metal": "水銀"},
    "Al-Hanʿa":       {"use": "教育護符、考試成功", "use_en": "Education talismans, exam success", "incense": "乳香", "metal": "錫"},
    "Al-Dhiraʿ":      {"use": "友誼結盟護符", "use_en": "Friendship alliance charms", "incense": "玫瑰", "metal": "銅"},
    "Al-Nathra":       {"use": "療癒護符、治療疾病", "use_en": "Healing talismans, curing illness", "incense": "龍腦", "metal": "銀"},
    "Al-Tarf":        {"use": "法律訴訟護符", "use_en": "Legal matter talismans", "incense": "沉香", "metal": "鉛"},
    "Al-Jabha":       {"use": "領導權力護符", "use_en": "Leadership and authority charms", "incense": "乳香", "metal": "金"},
    "Al-Zubra":       {"use": "婚姻和合護符", "use_en": "Marriage harmony talismans", "incense": "玫瑰", "metal": "銅"},
    "Al-Sarfa":       {"use": "轉運護符、改變命運", "use_en": "Fortune-turning talismans", "incense": "白檀", "metal": "金"},
    "Al-ʿAwwa":       {"use": "收穫豐盛、療癒植物", "use_en": "Abundant harvest, herbal healing", "incense": "沒藥", "metal": "水銀"},
    "Al-Simak":       {"use": "最強護符日、一切順遂", "use_en": "Most powerful talisman day, all-purpose", "incense": "乳香", "metal": "銅"},
    "Al-Ghafr":       {"use": "隱身護符、避禍", "use_en": "Concealment charms, avoiding misfortune", "incense": "沉香", "metal": "鐵"},
    "Al-Zubana":      {"use": "法律勝訴護符", "use_en": "Legal victory talismans", "incense": "桂皮", "metal": "錫"},
    "Al-Iklil":       {"use": "王權護符、尊貴加冕", "use_en": "Royal power talismans, coronation", "incense": "乳香", "metal": "鐵"},
    "Al-Qalb":        {"use": "勇氣護符（需謹慎）", "use_en": "Courage talismans (use with caution)", "incense": "龍血", "metal": "鐵"},
    "Al-Shawla":      {"use": "復仇護符（不建議）", "use_en": "Revenge talismans (not recommended)", "incense": "硫磺", "metal": "鉛"},
    "Al-Naʿaʾim":     {"use": "旅行安全護符", "use_en": "Safe travel talismans", "incense": "乳香", "metal": "錫"},
    "Al-Baldah":      {"use": "等待時機、冥想護符", "use_en": "Patience and meditation charms", "incense": "沉香", "metal": "鉛"},
    "Saʿd al-Dhabih": {"use": "犧牲奉獻護符", "use_en": "Sacrifice and devotion charms", "incense": "沒藥", "metal": "鉛"},
    "Saʿd Bulaʿ":     {"use": "消災解厄（需護身符）", "use_en": "Disaster relief (needs protection)", "incense": "硫磺", "metal": "鉛"},
    "Saʿd al-Suʿud":  {"use": "最大吉祥護符、萬事如意", "use_en": "Greatest fortune talismans", "incense": "乳香", "metal": "錫"},
    "Saʿd al-Akhbiya":{"use": "房屋安宅護符、家庭和睦", "use_en": "Home protection, family harmony", "incense": "龍腦", "metal": "銀"},
    "Al-Fargh al-Muqaddam": {"use": "建築開工護符", "use_en": "Construction commencement charms", "incense": "檀香", "metal": "鐵"},
    "Al-Fargh al-Muʾakhkhar":{"use":"完工慶祝護符","use_en":"Completion celebration talismans","incense":"玫瑰","metal":"水銀"},
    "Al-Risha":       {"use": "療癒完成、新循環開始", "use_en": "Healing completion, new cycle", "incense": "沒藥", "metal": "銅"},
}

# ============================================================
# Anwā' 天氣星宿預兆 — YEMENI_ANWA
# ============================================================
YEMENI_ANWA = {
    "Al-Sharatan":    {"weather": "春風起始、宜播種", "weather_en": "Spring winds begin, good for sowing"},
    "Al-Butain":      {"weather": "溫暖穩定", "weather_en": "Warm and stable"},
    "Al-Thurayya":    {"weather": "降雨預兆、春雨豐沛", "weather_en": "Rain omen, abundant spring rain"},
    "Al-Dabaran":     {"weather": "大風或暴雨", "weather_en": "Strong winds or storms"},
    "Al-Haqʿa":       {"weather": "寒流可能", "weather_en": "Cold front possible"},
    "Al-Hanʿa":       {"weather": "晴朗溫暖", "weather_en": "Clear and warm"},
    "Al-Dhiraʿ":      {"weather": "適中天氣", "weather_en": "Moderate weather"},
    "Al-Nathra":       {"weather": "濕氣重、霧氣", "weather_en": "Humid, foggy"},
    "Al-Tarf":        {"weather": "炎熱開始", "weather_en": "Heat begins"},
    "Al-Jabha":       {"weather": "盛夏炎熱", "weather_en": "Midsummer heat"},
    "Al-Zubra":       {"weather": "持續炎熱", "weather_en": "Continued heat"},
    "Al-Sarfa":       {"weather": "季節轉換之風", "weather_en": "Seasonal change winds"},
    "Al-ʿAwwa":       {"weather": "秋風初起", "weather_en": "Autumn winds begin"},
    "Al-Simak":       {"weather": "氣候宜人、豐收季節", "weather_en": "Pleasant climate, harvest season"},
    "Al-Ghafr":       {"weather": "降溫轉涼", "weather_en": "Cooling down"},
    "Al-Zubana":      {"weather": "多風乾燥", "weather_en": "Windy and dry"},
    "Al-Iklil":       {"weather": "涼爽宜人", "weather_en": "Cool and pleasant"},
    "Al-Qalb":        {"weather": "天氣多變、不穩", "weather_en": "Changeable, unstable weather"},
    "Al-Shawla":      {"weather": "寒流降臨", "weather_en": "Cold front arrives"},
    "Al-Naʿaʾim":     {"weather": "冬季預備", "weather_en": "Winter preparation"},
    "Al-Baldah":      {"weather": "嚴寒、萬物收藏", "weather_en": "Severe cold, all things stored"},
    "Saʿd al-Dhabih": {"weather": "冬季最冷時段", "weather_en": "Coldest period of winter"},
    "Saʿd Bulaʿ":     {"weather": "持續寒冷", "weather_en": "Continued cold"},
    "Saʿd al-Suʿud":  {"weather": "寒退回暖跡象", "weather_en": "Cold retreating, warming signs"},
    "Saʿd al-Akhbiya":{"weather": "初春暖意", "weather_en": "Early spring warmth"},
    "Al-Fargh al-Muqaddam": {"weather": "春雨漸來", "weather_en": "Spring rain approaching"},
    "Al-Fargh al-Muʾakhkhar":{"weather":"萬物復甦","weather_en":"All things revive"},
    "Al-Risha":       {"weather": "春季正式開始", "weather_en": "Spring officially begins"},
}

# ============================================================
# 阿拉伯點 (Arabic Parts) — 也門傳統
# ============================================================
YEMENI_ARABIC_PARTS = {
    "Part of Fortune":  {"formula_day": "ASC + Moon - Sun", "formula_night": "ASC + Sun - Moon",
                         "cn": "幸運點", "ar": "سهم السعادة"},
    "Part of Spirit":   {"formula_day": "ASC + Sun - Moon", "formula_night": "ASC + Moon - Sun",
                         "cn": "精神點", "ar": "سهم الروح"},
    "Part of Commerce": {"formula_day": "ASC + Mercury - Sun", "formula_night": "ASC + Sun - Mercury",
                         "cn": "商業點", "ar": "سهم التجارة"},
    "Part of Marriage":  {"formula_day": "ASC + Venus - Saturn", "formula_night": "ASC + Saturn - Venus",
                          "cn": "婚姻點", "ar": "سهم الزواج"},
    "Part of Victory":  {"formula_day": "ASC + Jupiter - Sun", "formula_night": "ASC + Sun - Jupiter",
                         "cn": "勝利點", "ar": "سهم النصر"},
    "Part of Fate":     {"formula_day": "ASC + Saturn - Sun", "formula_night": "ASC + Sun - Saturn",
                         "cn": "宿命點", "ar": "سهم القهر"},
}

# ============================================================
# Firdaria 週期 — YEMENI_FIRDARIA
# 日生與夜生各異的行星統治週期年數
# ============================================================
YEMENI_FIRDARIA = {
    "day_order": [
        ("Sun", 10), ("Venus", 8), ("Mercury", 13),
        ("Moon", 9), ("Saturn", 11), ("Jupiter", 12), ("Mars", 7),
    ],
    "night_order": [
        ("Moon", 9), ("Saturn", 11), ("Jupiter", 12),
        ("Mars", 7), ("Sun", 10), ("Venus", 8), ("Mercury", 13),
    ],
}

# ============================================================
# 預兆 (Omens) — al-Ashraf 風格 YEMENI_OMENS
# ============================================================
YEMENI_OMENS = {
    "Sun":     {"strong": "君主得勢、萬事榮昌", "weak": "統治者失勢、旱災",
                "strong_en": "Ruler prospers, glory", "weak_en": "Ruler weakened, drought"},
    "Moon":    {"strong": "人民安樂、農作豐收", "weak": "水患、疫病",
                "strong_en": "People prosper, good harvest", "weak_en": "Floods, epidemics"},
    "Mercury": {"strong": "商貿繁榮、學問興盛", "weak": "詐騙盛行、通訊不暢",
                "strong_en": "Trade flourishes, learning thrives", "weak_en": "Fraud prevalent, communication issues"},
    "Venus":   {"strong": "愛情美滿、藝術繁榮", "weak": "道德敗壞、奢靡",
                "strong_en": "Love fulfilled, arts flourish", "weak_en": "Moral decay, excess"},
    "Mars":    {"strong": "軍事勝利、勇氣充沛", "weak": "戰爭、暴力、火災",
                "strong_en": "Military victory, courage", "weak_en": "War, violence, fire"},
    "Jupiter": {"strong": "公義興盛、宗教繁榮", "weak": "法律不彰、信仰動搖",
                "strong_en": "Justice prevails, religion thrives", "weak_en": "Lawlessness, faith shaken"},
    "Saturn":  {"strong": "建設穩固、農業長久", "weak": "飢荒、瘟疫、地震",
                "strong_en": "Solid construction, lasting agriculture", "weak_en": "Famine, plague, earthquake"},
}

GRAHA_CN = {
    "Sun": "太陽", "Moon": "月亮", "Mercury": "水星", "Venus": "金星",
    "Mars": "火星", "Jupiter": "木星", "Saturn": "土星",
}

PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿",
    "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
}

ZODIAC_GLYPHS = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓",
]


# ============================================================
# 工具函數 (Utility Functions)
# ============================================================
def _sign_idx(lon):
    return int(lon / 30) % 12


def _sign_deg(lon):
    return lon % 30


def _normalize(deg):
    return deg % 360


def _find_house(lon, cusps):
    for i in range(12):
        c1 = cusps[i]
        c2 = cusps[(i + 1) % 12]
        if c2 < c1:
            if lon >= c1 or lon < c2:
                return i + 1
        elif c1 <= lon < c2:
            return i + 1
    return 1


def _get_manzil_index(sidereal_moon_lon):
    """Return 0–27 index of the lunar mansion for sidereal Moon longitude."""
    return int(_normalize(sidereal_moon_lon) / (360.0 / 28)) % 28


def _jd_to_date(jd):
    y, m, d, h = swe.revjul(jd)
    return f"{y:04d}-{m:02d}-{int(d):02d}"


# ============================================================
# 資料類 (Data Classes)
# ============================================================
@dataclass
class YemeniPlanet:
    name: str
    longitude: float
    sign: str
    sign_cn: str
    sign_degree: float
    house: int
    retrograde: bool = False


@dataclass
class YemeniHouse:
    number: int
    cusp: float
    sign: str
    sign_cn: str


@dataclass
class YemeniManzil:
    index: int
    name: str
    arabic: str
    chinese: str
    english: str
    stars: str
    fortune: str
    planet: str
    element: str
    talisman_use: str
    talisman_use_en: str
    weather: str
    weather_en: str


@dataclass
class YemeniArabicPart:
    name: str
    name_cn: str
    name_ar: str
    longitude: float
    sign: str
    sign_cn: str
    sign_degree: float
    house: int
    formula: str


@dataclass
class YemeniOmen:
    planet: str
    planet_cn: str
    condition: str
    text: str
    text_en: str


@dataclass
class YemeniFirdariaPeriod:
    planet: str
    planet_cn: str
    years: int
    start_date: str
    end_date: str


@dataclass
class YemeniChart:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude_geo: float
    location_name: str
    julian_day: float
    is_day_chart: bool
    ascendant: float
    midheaven: float
    positions: dict = field(default_factory=dict)
    planets: list = field(default_factory=list)
    houses: list = field(default_factory=list)
    manazil: list = field(default_factory=list)
    affiliated_stars: dict = field(default_factory=dict)
    arabic_parts: list = field(default_factory=list)
    talismans: dict = field(default_factory=dict)
    omens: list = field(default_factory=list)
    firdaria: list = field(default_factory=list)


# ============================================================
# 核心計算函數 (Core Computation)
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def compute_yemeni_chart(year, month, day, hour, minute, timezone,
                         latitude, longitude, location_name=""):
    """
    計算也門占星排盤 (Sidereal Zodiac)

    Returns
    -------
    YemeniChart : 包含 positions, houses, planets, manazil,
                  affiliated_stars, arabic_parts, talismans, omens, firdaria
    """
    swe.set_ephe_path("")
    swe.set_sid_mode(YEMENI_AYANAMSA_MODE)

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    # Sidereal house cusps
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"P",
                                 swe.FLG_SIDEREAL)
    ascendant = ascmc[0]
    midheaven = ascmc[1]

    # ── Planet positions (sidereal) ────────────────────────────
    planet_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
        "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
    }
    planet_longs = {}
    planets = []
    for name, pid in planet_ids.items():
        result, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        lon = _normalize(result[0])
        speed = result[3]
        idx = _sign_idx(lon)
        planet_longs[name] = lon
        planets.append(YemeniPlanet(
            name=name, longitude=lon,
            sign=ZODIAC_SIGNS[idx], sign_cn=SIGN_CN[ZODIAC_SIGNS[idx]],
            sign_degree=round(_sign_deg(lon), 2),
            house=_find_house(lon, cusps),
            retrograde=speed < 0,
        ))

    # ── Day / Night determination ────────────────────────────
    sun_lon = planet_longs["Sun"]
    sun_house = _find_house(sun_lon, cusps)
    is_day = sun_house >= 7

    # ── Houses ───────────────────────────────────────────────
    houses = []
    for i in range(12):
        c = cusps[i]
        idx = _sign_idx(c)
        houses.append(YemeniHouse(
            number=i + 1, cusp=c,
            sign=ZODIAC_SIGNS[idx], sign_cn=SIGN_CN[ZODIAC_SIGNS[idx]],
        ))

    # ── 28 Manazil (based on sidereal Moon) ──────────────────
    moon_lon = planet_longs["Moon"]
    manzil_idx = _get_manzil_index(moon_lon)
    manazil_list = []
    m = YEMENI_MANAZIL[manzil_idx]
    name_key = m[1]
    aff = YEMENI_AFFILIATED_STARS.get(name_key, {})
    talis = YEMENI_TALISMANIC_PROPERTIES.get(name_key, {})
    anwa = YEMENI_ANWA.get(name_key, {})
    manazil_list.append(YemeniManzil(
        index=manzil_idx,
        name=name_key,
        arabic=m[2],
        chinese=m[3],
        english=m[4],
        stars=m[5],
        fortune=m[6],
        planet=aff.get("planet", ""),
        element=aff.get("element", ""),
        talisman_use=talis.get("use", ""),
        talisman_use_en=talis.get("use_en", ""),
        weather=anwa.get("weather", ""),
        weather_en=anwa.get("weather_en", ""),
    ))

    # ── Affiliated stars for the birth manzil ────────────────
    affiliated = YEMENI_AFFILIATED_STARS.get(name_key, {})

    # ── Arabic Parts ─────────────────────────────────────────
    arabic_parts = []
    sun = planet_longs.get("Sun", 0)
    moon = planet_longs.get("Moon", 0)
    mercury = planet_longs.get("Mercury", 0)
    venus = planet_longs.get("Venus", 0)
    jupiter = planet_longs.get("Jupiter", 0)
    saturn = planet_longs.get("Saturn", 0)
    asc = ascendant

    part_formulas = [
        ("Part of Fortune", "幸運點", "سهم السعادة",
         _normalize(asc + moon - sun) if is_day else _normalize(asc + sun - moon),
         "ASC+Moon-Sun" if is_day else "ASC+Sun-Moon"),
        ("Part of Spirit", "精神點", "سهم الروح",
         _normalize(asc + sun - moon) if is_day else _normalize(asc + moon - sun),
         "ASC+Sun-Moon" if is_day else "ASC+Moon-Sun"),
        ("Part of Commerce", "商業點", "سهم التجارة",
         _normalize(asc + mercury - sun) if is_day else _normalize(asc + sun - mercury),
         "ASC+Mercury-Sun" if is_day else "ASC+Sun-Mercury"),
        ("Part of Marriage", "婚姻點", "سهم الزواج",
         _normalize(asc + venus - saturn) if is_day else _normalize(asc + saturn - venus),
         "ASC+Venus-Saturn" if is_day else "ASC+Saturn-Venus"),
        ("Part of Victory", "勝利點", "سهم النصر",
         _normalize(asc + jupiter - sun) if is_day else _normalize(asc + sun - jupiter),
         "ASC+Jupiter-Sun" if is_day else "ASC+Sun-Jupiter"),
        ("Part of Fate", "宿命點", "سهم القهر",
         _normalize(asc + saturn - sun) if is_day else _normalize(asc + sun - saturn),
         "ASC+Saturn-Sun" if is_day else "ASC+Sun-Saturn"),
    ]
    for pname, pcn, par, plon, pformula in part_formulas:
        idx = _sign_idx(plon)
        arabic_parts.append(YemeniArabicPart(
            name=pname, name_cn=pcn, name_ar=par,
            longitude=plon, sign=ZODIAC_SIGNS[idx],
            sign_cn=SIGN_CN[ZODIAC_SIGNS[idx]],
            sign_degree=round(_sign_deg(plon), 2),
            house=_find_house(plon, cusps),
            formula=pformula,
        ))

    # ── Talismans for the birth manzil ───────────────────────
    talismans = YEMENI_TALISMANIC_PROPERTIES.get(name_key, {})

    # ── Omens (al-Ashraf style) ──────────────────────────────
    omens = []
    for pname, plon_val in planet_longs.items():
        p_idx = _sign_idx(plon_val)
        p_house = _find_house(plon_val, cusps)
        omen_data = YEMENI_OMENS.get(pname, {})
        # Angular houses (1,4,7,10) = strong; cadent (3,6,9,12) = weak
        if p_house in (1, 4, 7, 10):
            condition = "strong"
            text = omen_data.get("strong", "")
            text_en = omen_data.get("strong_en", "")
        else:
            condition = "weak"
            text = omen_data.get("weak", "")
            text_en = omen_data.get("weak_en", "")
        omens.append(YemeniOmen(
            planet=pname, planet_cn=GRAHA_CN.get(pname, pname),
            condition=condition, text=text, text_en=text_en,
        ))

    # ── Firdaria periods ─────────────────────────────────────
    firdaria = []
    fird_order = YEMENI_FIRDARIA["day_order"] if is_day else YEMENI_FIRDARIA["night_order"]
    cur_jd = jd
    for fp_name, fp_years in fird_order:
        end_jd = cur_jd + fp_years * 365.25
        firdaria.append(YemeniFirdariaPeriod(
            planet=fp_name, planet_cn=GRAHA_CN.get(fp_name, fp_name),
            years=fp_years,
            start_date=_jd_to_date(cur_jd), end_date=_jd_to_date(end_jd),
        ))
        cur_jd = end_jd

    return YemeniChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude_geo=longitude,
        location_name=location_name, julian_day=jd,
        is_day_chart=is_day,
        ascendant=ascendant, midheaven=midheaven,
        positions=planet_longs,
        planets=planets, houses=houses,
        manazil=manazil_list,
        affiliated_stars=affiliated,
        arabic_parts=arabic_parts,
        talismans=talismans,
        omens=omens,
        firdaria=firdaria,
    )


# ============================================================
# 28 月宿曼荼羅 SVG — 古也門石刻 / Rasulid 手稿風格
# ============================================================
def build_yemeni_manzil_mandala_svg(chart, year=None, month=None, day=None,
                                    hour=None, minute=None, tz=None,
                                    location=""):
    """Build an SVG string for a 28-mansion Yemeni-style mandala disc.

    Visual design references:
    - Ancient South Arabian stone inscriptions (Musnad script style)
    - Rasulid manuscript illustrations (al-Ashraf's Tabṣira)
    - Arabic geometric patterns (girih tiles)

    Returns
    -------
    str – complete ``<svg>`` markup.
    """
    SIZE = 640
    CX, CY = SIZE / 2, SIZE / 2
    R_OUTER = 280
    R_INNER = 200
    R_MANZIL_LABEL = 245
    R_PLANET = 160
    R_CENTRE = 70

    birth_manzil = chart.manazil[0].index if chart.manazil else 0

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SIZE} {SIZE}" '
        f'style="width:100%;max-width:640px;margin:auto;display:block;" '
        f'font-family="serif">'
    )

    # ── Background ────────────────────────────────────────────
    svg.append(
        f'<rect width="{SIZE}" height="{SIZE}" fill="#1a0f05" rx="8"/>'
    )

    # ── Outer decorative ring ─────────────────────────────────
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER + 20}" '
        f'fill="none" stroke="#c8a04a" stroke-width="2"/>'
    )
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER + 16}" '
        f'fill="none" stroke="#8b6914" stroke-width="0.5"/>'
    )

    # ── Geometric pattern ring (girih-inspired dots) ──────────
    for i in range(56):
        a = math.radians(i * 360 / 56)
        dx = CX + (R_OUTER + 18) * math.cos(a)
        dy = CY + (R_OUTER + 18) * math.sin(a)
        svg.append(
            f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="1.2" fill="#c8a04a" opacity="0.6"/>'
        )

    # ── Outer & inner mansion rings ───────────────────────────
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER}" '
        f'fill="none" stroke="#c8a04a" stroke-width="1.5"/>'
    )
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_INNER}" '
        f'fill="none" stroke="#c8a04a" stroke-width="1"/>'
    )

    # ── 28 mansion sectors ────────────────────────────────────
    sector_angle = 360 / 28
    for i in range(28):
        angle = math.radians(i * sector_angle - 90)
        x1 = CX + R_INNER * math.cos(angle)
        y1 = CY + R_INNER * math.sin(angle)
        x2 = CX + R_OUTER * math.cos(angle)
        y2 = CY + R_OUTER * math.sin(angle)
        svg.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#8b6914" stroke-width="0.5" opacity="0.6"/>'
        )

    # ── Mansion labels + highlight birth manzil ───────────────
    for i, m in enumerate(YEMENI_MANAZIL):
        mid_angle_deg = i * sector_angle + sector_angle / 2 - 90
        mid_angle = math.radians(mid_angle_deg)

        # Highlight birth manzil
        if i == birth_manzil:
            a_start = math.radians(i * sector_angle - 90)
            a_end = math.radians((i + 1) * sector_angle - 90)
            large_arc = 0
            x_o1 = CX + R_OUTER * math.cos(a_start)
            y_o1 = CY + R_OUTER * math.sin(a_start)
            x_o2 = CX + R_OUTER * math.cos(a_end)
            y_o2 = CY + R_OUTER * math.sin(a_end)
            x_i2 = CX + R_INNER * math.cos(a_end)
            y_i2 = CY + R_INNER * math.sin(a_end)
            x_i1 = CX + R_INNER * math.cos(a_start)
            y_i1 = CY + R_INNER * math.sin(a_start)
            svg.append(
                f'<path d="M{x_o1:.1f},{y_o1:.1f} '
                f'A{R_OUTER},{R_OUTER} 0 {large_arc},1 {x_o2:.1f},{y_o2:.1f} '
                f'L{x_i2:.1f},{y_i2:.1f} '
                f'A{R_INNER},{R_INNER} 0 {large_arc},0 {x_i1:.1f},{y_i1:.1f} Z" '
                f'fill="#c8a04a" fill-opacity="0.25" stroke="#c8a04a" stroke-width="1"/>'
            )

        # Arabic name label
        lx = CX + R_MANZIL_LABEL * math.cos(mid_angle)
        ly = CY + R_MANZIL_LABEL * math.sin(mid_angle)
        label_color = "#ffd700" if i == birth_manzil else "#c8a04a"
        font_weight = "bold" if i == birth_manzil else "normal"
        font_size = "8" if i == birth_manzil else "6.5"
        svg.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{label_color}" '
            f'font-size="{font_size}" font-weight="{font_weight}" '
            f'transform="rotate({mid_angle_deg + 90:.1f},{lx:.1f},{ly:.1f})">'
            f'{m[2]}</text>'
        )

        # Index number (near inner ring)
        r_idx = R_INNER + 12
        nx = CX + r_idx * math.cos(mid_angle)
        ny = CY + r_idx * math.sin(mid_angle)
        svg.append(
            f'<text x="{nx:.1f}" y="{ny:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#8b6914" '
            f'font-size="6" opacity="0.7">{i + 1}</text>'
        )

    # ── Planet positions on inner disc ────────────────────────
    for p in chart.planets:
        p_angle_deg = (p.longitude / 360 * 360) - 90  # scale to 360°
        p_angle = math.radians(p_angle_deg)
        px = CX + R_PLANET * math.cos(p_angle)
        py = CY + R_PLANET * math.sin(p_angle)
        glyph = PLANET_GLYPHS.get(p.name, p.name[0])
        color = {
            "Sun": "#ffd700", "Moon": "#c0c0c0", "Mercury": "#ffa500",
            "Venus": "#228b22", "Mars": "#dc143c", "Jupiter": "#4169e1",
            "Saturn": "#a0a0a0",
        }.get(p.name, "#c8a04a")
        svg.append(
            f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{color}" '
            f'font-size="16" font-weight="bold">{glyph}</text>'
        )
        # Degree label
        deg_r = R_PLANET - 18
        dx = CX + deg_r * math.cos(p_angle)
        dy = CY + deg_r * math.sin(p_angle)
        svg.append(
            f'<text x="{dx:.1f}" y="{dy:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#8b6914" '
            f'font-size="7">{p.sign_degree:.0f}°</text>'
        )

    # ── Centre circle ─────────────────────────────────────────
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_CENTRE}" '
        f'fill="#1a0f05" stroke="#c8a04a" stroke-width="1.5"/>'
    )

    # ── Centre text ───────────────────────────────────────────
    svg.append(
        f'<text x="{CX}" y="{CY - 40}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#ffd700" '
        f'font-size="11" font-weight="bold">☪ 也門占星</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY - 26}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#c8a04a" '
        f'font-size="8">Rasulid Astrology</text>'
    )

    sect_label = "☉ Day / 日生" if chart.is_day_chart else "☽ Night / 夜生"
    svg.append(
        f'<text x="{CX}" y="{CY - 10}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#c8a04a" '
        f'font-size="8">{sect_label}</text>'
    )

    if year is not None and month is not None and day is not None:
        date_str = f"{year}-{month:02d}-{day:02d}"
        svg.append(
            f'<text x="{CX}" y="{CY + 4}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#c8a04a" '
            f'font-size="8">{date_str}</text>'
        )

    if hour is not None and minute is not None:
        tz_str = f" UTC{tz:+.1f}" if tz is not None else ""
        time_str = f"{hour:02d}:{minute:02d}{tz_str}"
        svg.append(
            f'<text x="{CX}" y="{CY + 18}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#c8a04a" '
            f'font-size="8">{time_str}</text>'
        )

    # Birth manzil name in centre
    if chart.manazil:
        m = chart.manazil[0]
        svg.append(
            f'<text x="{CX}" y="{CY + 34}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#ffd700" '
            f'font-size="8" font-weight="bold">{m.arabic} {m.chinese}</text>'
        )

    if location:
        svg.append(
            f'<text x="{CX}" y="{CY + 48}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#8b6914" '
            f'font-size="6">{location[:25]}</text>'
        )

    svg.append("</svg>")
    return "\n".join(svg)


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================
def render_yemeni_chart(chart_obj, after_chart_hook=None):
    """Render Yemeni chart in Streamlit."""
    st.subheader("☪ " + t("yemeni_chart_title"))

    # ── Chart info ────────────────────────────────────────────
    sect = "☀️ 日盤 (Day Chart)" if chart_obj.is_day_chart else "🌙 夜盤 (Night Chart)"
    st.info(f"**{t('yemeni_sect')}**: {sect}")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**日期 (Date):** {chart_obj.year}/{chart_obj.month}/{chart_obj.day}")
        st.write(f"**時間 (Time):** {chart_obj.hour:02d}:{chart_obj.minute:02d}")
        st.write(f"**時區 (Timezone):** UTC{chart_obj.timezone:+.1f}")
    with col2:
        st.write(f"**地點 (Location):** {chart_obj.location_name}")
        asc_idx = _sign_idx(chart_obj.ascendant)
        mc_idx = _sign_idx(chart_obj.midheaven)
        st.write(
            f"**上升點 (ASC):** {ZODIAC_SIGNS[asc_idx]} "
            f"({SIGN_CN[ZODIAC_SIGNS[asc_idx]]}) "
            f"{_sign_deg(chart_obj.ascendant):.2f}°"
        )
        st.write(
            f"**天頂 (MC):** {ZODIAC_SIGNS[mc_idx]} "
            f"({SIGN_CN[ZODIAC_SIGNS[mc_idx]]}) "
            f"{_sign_deg(chart_obj.midheaven):.2f}°"
        )

    if after_chart_hook:
        after_chart_hook()

    st.divider()

    # ── Manazil (lunar mansions) ──────────────────────────────
    st.markdown(f"#### 🌙 {t('yemeni_manazil_title')}")
    if chart_obj.manazil:
        m = chart_obj.manazil[0]
        st.success(
            f"**{t('yemeni_birth_manzil')}**: "
            f"第 {m.index + 1} 宿 — **{m.name}** ({m.arabic}) — {m.chinese}\n\n"
            f"**{t('yemeni_stars')}**: {m.stars}　|　"
            f"**{t('yemeni_fortune')}**: {m.fortune}\n\n"
            f"**{t('yemeni_affiliated_planet')}**: {m.planet} ({m.element})"
        )

    st.divider()

    # ── Talismanic Magic ──────────────────────────────────────
    st.markdown(f"#### 🔮 {t('yemeni_talisman_title')}")
    if chart_obj.talismans:
        tdata = chart_obj.talismans
        st.markdown(
            f"- **護符用途 (Talisman Use):** {tdata.get('use', '—')}\n"
            f"- **{tdata.get('use_en', '')}**\n"
            f"- **薰香 (Incense):** {tdata.get('incense', '—')}\n"
            f"- **金屬 (Metal):** {tdata.get('metal', '—')}"
        )

    st.divider()

    # ── Anwā' weather omens ───────────────────────────────────
    st.markdown(f"#### 🌤️ {t('yemeni_anwa_title')}")
    if chart_obj.manazil:
        m = chart_obj.manazil[0]
        st.info(
            f"**{m.name}** — {m.weather} / {m.weather_en}"
        )

    st.divider()

    # ── Planet positions ──────────────────────────────────────
    st.markdown(f"#### 🪐 {t('yemeni_planet_positions')}")
    planet_data = []
    for p in chart_obj.planets:
        retro = "℞" if p.retrograde else ""
        planet_data.append({
            t("yemeni_col_planet"): f"{p.name} {PLANET_GLYPHS.get(p.name, '')} ({GRAHA_CN.get(p.name, p.name)})",
            t("yemeni_col_sign"): f"{ZODIAC_GLYPHS[ZODIAC_SIGNS.index(p.sign)]} {p.sign} ({p.sign_cn})",
            t("yemeni_col_degree"): f"{p.sign_degree}°",
            t("yemeni_col_house"): p.house,
            "℞": retro,
        })
    if planet_data:
        st.dataframe(planet_data, width="stretch", hide_index=True)

    st.divider()

    # ── Arabic Parts ──────────────────────────────────────────
    st.markdown(f"#### ☪ {t('yemeni_arabic_parts_title')}")
    parts_data = []
    for part in chart_obj.arabic_parts:
        parts_data.append({
            t("yemeni_col_part_name"): f"{part.name} ({part.name_cn})",
            t("yemeni_col_arabic"): part.name_ar,
            t("yemeni_col_sign"): f"{part.sign} ({part.sign_cn})",
            t("yemeni_col_degree"): f"{part.sign_degree}°",
            t("yemeni_col_house"): part.house,
            t("yemeni_col_formula"): part.formula,
        })
    if parts_data:
        st.dataframe(parts_data, width="stretch", hide_index=True)

    st.divider()

    # ── Omens ─────────────────────────────────────────────────
    st.markdown(f"#### 📜 {t('yemeni_omens_title')}")
    for o in chart_obj.omens:
        icon = "🌟" if o.condition == "strong" else "⚠️"
        st.markdown(
            f"{icon} **{o.planet}** ({o.planet_cn}) — "
            f"*{o.condition.upper()}*: {o.text} / {o.text_en}"
        )

    st.divider()

    # ── Firdaria ──────────────────────────────────────────────
    st.markdown(f"#### ⏳ {t('yemeni_firdaria_title')}")
    fird_data = []
    for fp in chart_obj.firdaria:
        fird_data.append({
            t("yemeni_col_planet"): f"{fp.planet} ({fp.planet_cn})",
            t("yemeni_col_years"): fp.years,
            t("yemeni_col_start"): fp.start_date,
            t("yemeni_col_end"): fp.end_date,
        })
    if fird_data:
        st.dataframe(fird_data, width="stretch", hide_index=True)

    st.divider()

    # ── Houses ────────────────────────────────────────────────
    st.markdown(f"#### 🏛️ {t('yemeni_houses_title')}")
    house_data = []
    for h in chart_obj.houses:
        house_data.append({
            t("yemeni_col_house"): h.number,
            t("yemeni_col_cusp"): f"{h.cusp:.2f}°",
            t("yemeni_col_sign"): f"{h.sign} ({h.sign_cn})",
            t("yemeni_col_arabic"): SIGN_AR.get(h.sign, ""),
        })
    if house_data:
        st.dataframe(house_data, width="stretch", hide_index=True)
