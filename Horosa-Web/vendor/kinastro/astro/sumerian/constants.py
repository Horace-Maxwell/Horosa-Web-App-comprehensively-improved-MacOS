"""
astro/sumerian/constants.py — Sumerian / Mesopotamian Astrology Constants

Sources:
- MUL.APIN tablets (~1000 BCE): star lists, heliacal risings, three paths
- Enūma Anu Enlil (~70 tablets, 2000–500 BCE): planetary omens
- K.8538 Nineveh Planisphere (~650 BCE): 8-sector circular star map
- Hunger & Pingree, "MUL.APIN: An Astronomical Compendium in Cuneiform" (1989)
- Koch-Westenholz, "Mesopotamian Astrology" (1995)
- Rochberg, "The Heavenly Writing" (2004)
"""

from __future__ import annotations
from typing import Dict, List, Tuple

# ============================================================
# Colour palette — deep gold, lapis blue, terracotta, sandstone
# ============================================================
SUMER_GOLD = "#C9A227"
SUMER_GOLD_LIGHT = "#E8C96A"
SUMER_LAPIS = "#1A3A6B"
SUMER_LAPIS_LIGHT = "#2A5298"
SUMER_TERRACOTTA = "#A0522D"
SUMER_TERRACOTTA_LIGHT = "#CD853F"
SUMER_SANDSTONE = "#D2B48C"
SUMER_SANDSTONE_DARK = "#8B7355"
SUMER_CLAY = "#8B6914"
SUMER_BG = "#0D0A02"
SUMER_BG2 = "#1A1200"
SUMER_BORDER = "rgba(201,162,39,0.35)"

# ============================================================
# 12 Zodiac signs — Akkadian names from MUL.APIN tradition
# Format: (index, akkadian_name, chinese_name, english_name, western_equivalent)
# ============================================================
SUMERIAN_ZODIAC_SIGNS: List[Tuple] = [
    (0,  "LU.HUN.GA",          "雇農/雇工",       "The Hired Man",          "Aries"),
    (1,  "GU₄.AN.NA",          "天牛",             "The Bull of Heaven",     "Taurus"),
    (2,  "MAŠ.TAB.BA",         "雙子",             "The Great Twins",        "Gemini"),
    (3,  "ALLUTTU",             "螃蟹",             "The Crab",               "Cancer"),
    (4,  "UR.GU.LA",            "獅子",             "The Lion",               "Leo"),
    (5,  "AB.SIN",              "穗/犁溝",          "The Furrow",             "Virgo"),
    (6,  "zibānītu",            "天秤",             "The Scales",             "Libra"),
    (7,  "GIR₂.TAB",           "蠍子",             "The Scorpion",           "Scorpio"),
    (8,  "PA.BIL.SAG",         "射手",             "The Archer / Pabilsag",  "Sagittarius"),
    (9,  "SUḪUR.MAŠ₂",        "山羊魚",           "The Goat-Fish",          "Capricorn"),
    (10, "GU.LA",               "大者/水瓶",        "The Great One",          "Aquarius"),
    (11, "KUN.MEŠ",             "魚尾/雙魚",        "The Tails",              "Pisces"),
]

# Quick lookup dictionaries
ZODIAC_SIGN_ORDER: List[str] = [s[4] for s in SUMERIAN_ZODIAC_SIGNS]
AKKADIAN_NAME: Dict[str, str] = {s[4]: s[1] for s in SUMERIAN_ZODIAC_SIGNS}
SIGN_CN: Dict[str, str] = {s[4]: s[2] for s in SUMERIAN_ZODIAC_SIGNS}
SIGN_EN: Dict[str, str] = {s[4]: s[3] for s in SUMERIAN_ZODIAC_SIGNS}

# ============================================================
# Planetary deity mapping — Enūma Anu Enlil standard
# ============================================================
MESOPOTAMIAN_DEITIES: Dict[str, Dict] = {
    "Sun": {
        "akkadian": "Šamaš",
        "sumerian": "dUTU",
        "role_cn": "太陽神 · 正義守護者",
        "role_en": "Sun god · guardian of justice",
        "color": "#DAA520",
        "glyph": "☉",
    },
    "Moon": {
        "akkadian": "Sîn",
        "sumerian": "dEN.ZU / dNANNA",
        "role_cn": "月神 · 智慧之主",
        "role_en": "Moon god · lord of wisdom",
        "color": "#A8C4D8",
        "glyph": "☽",
    },
    "Venus": {
        "akkadian": "Ištar",
        "sumerian": "dINANNA",
        "role_cn": "愛與戰爭女神",
        "role_en": "Goddess of love and war",
        "color": "#2E7D32",
        "glyph": "♀",
    },
    "Mercury": {
        "akkadian": "Nabû",
        "sumerian": "dNA.BI.UM",
        "role_cn": "書寫與智慧之神",
        "role_en": "God of writing and wisdom",
        "color": "#8B6914",
        "glyph": "☿",
    },
    "Mars": {
        "akkadian": "Nergal",
        "sumerian": "dU.GUR",
        "role_cn": "戰爭與瘟疫之神",
        "role_en": "God of war and pestilence",
        "color": "#B71C1C",
        "glyph": "♂",
    },
    "Jupiter": {
        "akkadian": "Marduk",
        "sumerian": "dAMAR.UTU",
        "role_cn": "眾神之王 · 巴比倫主神",
        "role_en": "King of gods · patron of Babylon",
        "color": "#1565C0",
        "glyph": "♃",
    },
    "Saturn": {
        "akkadian": "Ninurta",
        "sumerian": "dNIN.URTA",
        "role_cn": "農業與戰爭之神",
        "role_en": "God of agriculture and war",
        "color": "#4A4A4A",
        "glyph": "♄",
    },
}

# ============================================================
# Three Paths of MUL.APIN
# The sky was divided into three bands by declination:
#   Path of Enlil  — northern stars (dec > +17°)
#   Path of Anu    — equatorial belt (dec ±17°)
#   Path of Ea     — southern stars (dec < -17°)
# ============================================================
MULAPIN_PATHS: Dict[str, Dict] = {
    "Enlil": {
        "cn": "恩利爾之路",
        "en": "Path of Enlil",
        "desc_cn": "天球北帶（赤緯 > +17°），對應北方神域，共 33 顆星座",
        "desc_en": "Northern band of the sky (dec > +17°), domain of Enlil, 33 constellations",
        "color": SUMER_LAPIS_LIGHT,
        "dec_limit": 17.0,
        "direction": "north",
    },
    "Anu": {
        "cn": "安努之路",
        "en": "Path of Anu",
        "desc_cn": "天球赤道帶（赤緯 ±17°），對應天界神域，共 23 顆星座",
        "desc_en": "Equatorial band of the sky (dec ±17°), domain of Anu, 23 constellations",
        "color": SUMER_GOLD,
        "dec_limit": 0.0,
        "direction": "equator",
    },
    "Ea": {
        "cn": "埃阿之路",
        "en": "Path of Ea",
        "desc_cn": "天球南帶（赤緯 < -17°），對應深淵水域神域，共 15 顆星座",
        "desc_en": "Southern band of the sky (dec < -17°), domain of Ea, 15 constellations",
        "color": SUMER_TERRACOTTA_LIGHT,
        "dec_limit": -17.0,
        "direction": "south",
    },
}

# ============================================================
# MUL.APIN — 36 Heliacal Rising Stars (one per decan of the year)
# Each entry: (star_name, akkadian, month_index, path, meaning_cn, meaning_en)
# month_index: 0=Nisannu(I)…11=Addaru(XII)
# ============================================================
MULAPIN_36_STARS: List[Dict] = [
    # Month I — Nisannu (Mar/Apr)
    {"star": "Pleiades",         "akkadian": "MUL.MUL",       "month": 0, "path": "Enlil",
     "cn": "昴宿星團",           "en": "The Stars (Pleiades)"},
    {"star": "Taurus",           "akkadian": "GU₄.AN.NA",     "month": 0, "path": "Anu",
     "cn": "天牛",               "en": "Bull of Heaven"},
    {"star": "True Shepherd",    "akkadian": "SIPA.ZI.AN.NA", "month": 0, "path": "Anu",
     "cn": "真牧人 (獵戶α)",    "en": "True Shepherd of Anu (Orion)"},
    # Month II — Ayyaru (Apr/May)
    {"star": "Old Man",          "akkadian": "ŠIBZIANNA",     "month": 1, "path": "Enlil",
     "cn": "老人星 (英仙座)",    "en": "The Old Man (Perseus)"},
    {"star": "Crook",            "akkadian": "GAMLU",         "month": 1, "path": "Enlil",
     "cn": "鐮刀 (御夫)",        "en": "The Crook (Auriga)"},
    {"star": "Great Twins",      "akkadian": "MAŠ.TAB.BA.GAL.GAL", "month": 1, "path": "Anu",
     "cn": "大雙子 (雙子)",      "en": "The Great Twins (Gemini)"},
    # Month III — Simanu (May/Jun)
    {"star": "Crab",             "akkadian": "ALLUTTU",       "month": 2, "path": "Enlil",
     "cn": "螃蟹 (巨蟹)",        "en": "The Crab (Cancer)"},
    {"star": "Arrow",            "akkadian": "KAK.SI.SÁ",    "month": 2, "path": "Anu",
     "cn": "箭 (天狼星α)",       "en": "The Arrow (Sirius)"},
    {"star": "Bow",              "akkadian": "BAN",           "month": 2, "path": "Ea",
     "cn": "弓 (大犬座)",        "en": "The Bow (Canis Major)"},
    # Month IV — Du'uzu (Jun/Jul)
    {"star": "Serpent",          "akkadian": "MUŠ",           "month": 3, "path": "Anu",
     "cn": "蛇 (長蛇座)",        "en": "The Serpent (Hydra)"},
    {"star": "Lion",             "akkadian": "UR.GU.LA",      "month": 3, "path": "Anu",
     "cn": "獅子 (獅子座α)",     "en": "The Lion (Leo)"},
    {"star": "Raven",            "akkadian": "UGA",           "month": 3, "path": "Ea",
     "cn": "鴉 (烏鴉座)",        "en": "The Raven (Corvus)"},
    # Month V — Abu (Jul/Aug)
    {"star": "Furrow",           "akkadian": "AB.SIN",        "month": 4, "path": "Anu",
     "cn": "穗 (室女座α角宿一)", "en": "The Furrow (Virgo/Spica)"},
    {"star": "Scales",           "akkadian": "zibānītu",      "month": 4, "path": "Anu",
     "cn": "天秤 (天秤座)",      "en": "The Scales (Libra)"},
    {"star": "Frond of Erua",    "akkadian": "TIR.AN.NA",     "month": 4, "path": "Enlil",
     "cn": "虹 (天弓)",          "en": "The Rainbow (Boötes region)"},
    # Month VI — Ululu (Aug/Sep)
    {"star": "Scorpion",         "akkadian": "GIR₂.TAB",      "month": 5, "path": "Ea",
     "cn": "蠍子 (天蠍座)",      "en": "The Scorpion (Scorpio)"},
    {"star": "Anzu Bird",        "akkadian": "AN.ZU",         "month": 5, "path": "Enlil",
     "cn": "安祖鳥 (天鵰)",      "en": "The Anzu Bird (Aquila)"},
    {"star": "Dead Man",         "akkadian": "LU.LIM",        "month": 5, "path": "Enlil",
     "cn": "倒下之人 (牧夫座)",  "en": "The Standing Dead Man (Boötes)"},
    # Month VII — Tashritu (Sep/Oct)
    {"star": "Goat-Fish",        "akkadian": "SUḪUR.MAŠ₂",   "month": 6, "path": "Ea",
     "cn": "山羊魚 (摩羯座)",    "en": "The Goat-Fish (Capricorn)"},
    {"star": "Pabilsag",         "akkadian": "PA.BIL.SAG",   "month": 6, "path": "Enlil",
     "cn": "射手 (人馬座)",      "en": "Pabilsag (Sagittarius)"},
    {"star": "Horse",            "akkadian": "ANŠE.KUR.RA",  "month": 6, "path": "Enlil",
     "cn": "馬 (飛馬座)",        "en": "The Horse (Pegasus)"},
    # Month VIII — Arahsamnu (Oct/Nov)
    {"star": "Panther",          "akkadian": "UD.KA.DUḪ.A",  "month": 7, "path": "Enlil",
     "cn": "豹 (天龍座)",        "en": "The Panther (Draco region)"},
    {"star": "Swallow",          "akkadian": "SIM.MAḪ",      "month": 7, "path": "Anu",
     "cn": "燕子 (南魚座/寶瓶)", "en": "The Swallow (Pisces Australis)"},
    {"star": "Great One",        "akkadian": "GU.LA",         "month": 7, "path": "Anu",
     "cn": "大者 (寶瓶座)",      "en": "The Great One (Aquarius)"},
    # Month IX — Kislimu (Nov/Dec)
    {"star": "Tails",            "akkadian": "KUN.MEŠ",       "month": 8, "path": "Anu",
     "cn": "魚尾 (雙魚座)",      "en": "The Tails (Pisces)"},
    {"star": "Anunitu",          "akkadian": "d.A.NU.NI.TUM", "month": 8, "path": "Anu",
     "cn": "阿努尼圖 (北魚+仙女)", "en": "Anunitu (N. Fish / Andromeda)"},
    {"star": "Field",            "akkadian": "IKU",           "month": 8, "path": "Anu",
     "cn": "田野 (飛馬座大方塊)", "en": "The Field (Pegasus Square)"},
    # Month X — Tebetu (Dec/Jan)
    {"star": "Hired Man",        "akkadian": "LU.HUN.GA",     "month": 9, "path": "Anu",
     "cn": "雇農 (白羊座)",      "en": "The Hired Man (Aries)"},
    {"star": "Stars",            "akkadian": "MUL.MUL (II)",  "month": 9, "path": "Enlil",
     "cn": "星星 (昴宿再升)",    "en": "The Stars (Pleiades, 2nd)"},
    {"star": "Dumuzi's Sheep",   "akkadian": "UDU.IDIM.GU₄", "month": 9, "path": "Enlil",
     "cn": "牧羊 (金牛座β)",     "en": "Dumuzi's Sheep (Aldebaran)"},
    # Month XI — Shabatu (Jan/Feb)
    {"star": "Sitting Gods",     "akkadian": "DINGIR.MES",    "month": 10, "path": "Enlil",
     "cn": "坐神 (仙后座)",      "en": "Sitting Gods (Cassiopeia)"},
    {"star": "Bark of Heaven",   "akkadian": "MÁ.GUR₈",      "month": 10, "path": "Enlil",
     "cn": "天舟 (天船座)",      "en": "Bark of Heaven (Argo)"},
    {"star": "Fox",              "akkadian": "KA₅.A",         "month": 10, "path": "Enlil",
     "cn": "狐狸 (小狐狸座)",    "en": "The Fox (Vulpecula)"},
    # Month XII — Addaru (Feb/Mar)
    {"star": "Demon",            "akkadian": "UD.KA.DUḪ.A₂", "month": 11, "path": "Enlil",
     "cn": "惡魔 (天蠍β幻蠍)",   "en": "The Demon (Ophiuchus region)"},
    {"star": "Kidney",           "akkadian": "IR₃",           "month": 11, "path": "Ea",
     "cn": "腎臟 (天秤北側)",    "en": "The Kidney (N. Libra region)"},
    {"star": "Mad Dog",          "akkadian": "UR.KU",         "month": 11, "path": "Ea",
     "cn": "狂犬 (南天狼)",      "en": "The Mad Dog (southern sky)"},
]

# ============================================================
# K.8538 Planisphere — 8-sector definitions
# Each sector spans 45° of ecliptic longitude
# ============================================================
K8538_SECTORS: List[Dict] = [
    {
        "index": 0,
        "direction": "NE",
        "direction_cn": "東北",
        "lon_start": 0.0,
        "lon_end": 45.0,
        "season_cn": "春分初",
        "season_en": "Early Spring",
        "color": "#B8860B",
        "constellations": ["Hired Man (Aries)", "Bull of Heaven (Taurus)"],
        "akkadian_label": "𒀭𒌓",
    },
    {
        "index": 1,
        "direction": "E",
        "direction_cn": "東",
        "lon_start": 45.0,
        "lon_end": 90.0,
        "season_cn": "春末",
        "season_en": "Late Spring",
        "color": "#9B7D4D",
        "constellations": ["Great Twins (Gemini)", "Crab (Cancer)"],
        "akkadian_label": "𒀭𒂗",
    },
    {
        "index": 2,
        "direction": "SE",
        "direction_cn": "東南",
        "lon_start": 90.0,
        "lon_end": 135.0,
        "season_cn": "夏至初",
        "season_en": "Early Summer",
        "color": "#7A6232",
        "constellations": ["Lion (Leo)", "Furrow (Virgo)"],
        "akkadian_label": "𒀭𒈾",
    },
    {
        "index": 3,
        "direction": "S",
        "direction_cn": "南",
        "lon_start": 135.0,
        "lon_end": 180.0,
        "season_cn": "夏末",
        "season_en": "Late Summer",
        "color": "#5C4A2A",
        "constellations": ["Scales (Libra)", "Scorpion (Scorpio)"],
        "akkadian_label": "𒀭𒌍",
    },
    {
        "index": 4,
        "direction": "SW",
        "direction_cn": "西南",
        "lon_start": 180.0,
        "lon_end": 225.0,
        "season_cn": "秋分初",
        "season_en": "Early Autumn",
        "color": "#8B6914",
        "constellations": ["Pabilsag (Sagittarius)", "Goat-Fish (Capricorn)"],
        "akkadian_label": "𒀭𒊩𒌆",
    },
    {
        "index": 5,
        "direction": "W",
        "direction_cn": "西",
        "lon_start": 225.0,
        "lon_end": 270.0,
        "season_cn": "秋末",
        "season_en": "Late Autumn",
        "color": "#A0845C",
        "constellations": ["Great One (Aquarius)", "Swallow (Pisces Aus.)"],
        "akkadian_label": "𒀭𒃲",
    },
    {
        "index": 6,
        "direction": "NW",
        "direction_cn": "西北",
        "lon_start": 270.0,
        "lon_end": 315.0,
        "season_cn": "冬至初",
        "season_en": "Early Winter",
        "color": "#B89E6E",
        "constellations": ["Tails (Pisces)", "Anunitu"],
        "akkadian_label": "𒀭𒀀",
    },
    {
        "index": 7,
        "direction": "N",
        "direction_cn": "北",
        "lon_start": 315.0,
        "lon_end": 360.0,
        "season_cn": "冬末",
        "season_en": "Late Winter",
        "color": "#D4B87A",
        "constellations": ["Field (Pegasus)", "Stars (Pleiades)"],
        "akkadian_label": "𒀭𒀊",
    },
]

# ============================================================
# Dignity tables — domicile, exaltation, detriment, fall
# (classical 7-planet system)
# ============================================================
DOMICILE: Dict[str, List[int]] = {
    "Sun":     [4],
    "Moon":    [3],
    "Mars":    [0, 7],
    "Mercury": [2, 5],
    "Jupiter": [8, 11],
    "Venus":   [1, 6],
    "Saturn":  [9, 10],
}
EXALTATION: Dict[str, int] = {
    "Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5,
    "Jupiter": 3, "Venus": 11, "Saturn": 6,
}
DETRIMENT: Dict[str, List[int]] = {
    "Sun":     [10],
    "Moon":    [9],
    "Mars":    [1, 6],
    "Mercury": [8, 11],
    "Jupiter": [2, 5],
    "Venus":   [0, 7],
    "Saturn":  [3, 4],
}
FALL: Dict[str, int] = {
    "Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11,
    "Jupiter": 9, "Venus": 5, "Saturn": 0,
}

# ============================================================
# Enūma Anu Enlil — Omen database
# 30+ basic rules organized by planet × sign × phenomenon
# Format: (planet, sign_idx, condition, text_cn, text_en)
# ============================================================
EAE_OMENS: List[Dict] = [
    # ── Šamaš (Sun) omens ─────────────────────────────────────
    {"planet": "Sun",  "sign": "Aries",       "condition": "exalt",
     "cn": "Šamaš 居白羊之首，春分旭升，王權煥然，國家昌盛。",
     "en": "Šamaš rises at the Ram's head at spring equinox — the king's power renews; the land flourishes."},
    {"planet": "Sun",  "sign": "Leo",         "condition": "domicile",
     "cn": "Šamaš 入獅子宮，炎夏正午，君王征伐必勝，御駕親征吉。",
     "en": "Šamaš enters the Lion — midsummer noon; the king leads battle to victory."},
    {"planet": "Sun",  "sign": "Libra",       "condition": "fall",
     "cn": "Šamaš 在天秤受制，秋分日蝕之兆，君主宜防宮廷陰謀。",
     "en": "Šamaš afflicted in the Scales — eclipse at autumn equinox; the ruler must guard against court intrigue."},
    {"planet": "Sun",  "sign": "Aquarius",    "condition": "detriment",
     "cn": "Šamaš 在大者（寶瓶）削弱，嚴冬陽光微弱，農田荒蕪之兆。",
     "en": "Šamaš weakened in the Great One — winter sun fades; farmland risks lying barren."},
    # ── Sîn (Moon) omens ──────────────────────────────────────
    {"planet": "Moon", "sign": "Taurus",      "condition": "exalt",
     "cn": "Sîn 升於金牛，月光皎潔如鏡，豐年有望，婦人生貴子。",
     "en": "Sîn exalted in the Bull — moonlight pure as a mirror; a fruitful year; a noble child is born."},
    {"planet": "Moon", "sign": "Cancer",      "condition": "domicile",
     "cn": "Sîn 居螃蟹宮，月亮滿圓無虧，河水豐沛，婚嫁吉慶。",
     "en": "Sîn at home in the Crab — the moon is full and round; rivers run high; marriages rejoice."},
    {"planet": "Moon", "sign": "Scorpio",     "condition": "fall",
     "cn": "Sîn 落陷天蠍，月蝕之兆，王室婦人有憂，瘟疫將至。",
     "en": "Sîn fallen in the Scorpion — lunar eclipse omen; royal women face sorrow; pestilence approaches."},
    {"planet": "Moon", "sign": "Capricorn",   "condition": "detriment",
     "cn": "Sîn 在山羊魚受抑，月光昏暗，牧畜有損，寒潮來臨。",
     "en": "Sîn afflicted in the Goat-Fish — moon dims; livestock suffer; cold currents arrive."},
    # ── Nabû (Mercury) omens ──────────────────────────────────
    {"planet": "Mercury", "sign": "Gemini",   "condition": "domicile",
     "cn": "Nabû 居雙子宮，書吏與商旅皆順，合約大吉，信使捷報。",
     "en": "Nabû at home in the Twins — scribes and merchants prosper; contracts are auspicious; envoys bring good news."},
    {"planet": "Mercury", "sign": "Virgo",    "condition": "domicile",
     "cn": "Nabû 在穗宮運行，農業記錄精準，倉廩充實，帳目無誤。",
     "en": "Nabû in the Furrow — agricultural records are accurate; granaries fill; accounts are in order."},
    {"planet": "Mercury", "sign": "Pisces",   "condition": "fall",
     "cn": "Nabû 落陷雙魚，書吏有誤，使節受阻，文書遺失。",
     "en": "Nabû fallen in the Tails — scribes err; envoys are delayed; documents are lost."},
    {"planet": "Mercury", "sign": "Sagittarius", "condition": "detriment",
     "cn": "Nabû 逆行射手，消息混亂，謠言四起，商旅宜謹慎。",
     "en": "Nabû retrograde in the Archer — messages are confused; rumours spread; merchants should be cautious."},
    # ── Ištar (Venus) omens ───────────────────────────────────
    {"planet": "Venus",  "sign": "Taurus",    "condition": "domicile",
     "cn": "Ištar 居天牛宮，晨星明亮如火炬，婚姻大吉，牛羊豐盛。",
     "en": "Ištar at home in the Bull — morning star blazes like a torch; marriages are blessed; cattle thrive."},
    {"planet": "Venus",  "sign": "Libra",     "condition": "domicile",
     "cn": "Ištar 在天秤居正，外交協議達成，美人恩寵，和平繁榮。",
     "en": "Ištar in the Scales — diplomatic treaties are concluded; beauty is favoured; peace prevails."},
    {"planet": "Venus",  "sign": "Pisces",    "condition": "exalt",
     "cn": "Ištar 升揚雙魚，夕星柔美，愛情與豐收同至，神廟香火旺盛。",
     "en": "Ištar exalted in the Tails — evening star glows softly; love and harvest arrive together; temple offerings multiply."},
    {"planet": "Venus",  "sign": "Aries",     "condition": "detriment",
     "cn": "Ištar 在雇農宮受抑，女性地位受損，愛情波折，春種不豐。",
     "en": "Ištar afflicted in the Hired Man — women's status suffers; love encounters setbacks; spring sowing yields poorly."},
    {"planet": "Venus",  "sign": "Scorpio",   "condition": "detriment",
     "cn": "Ištar 在天蠍受制，戰爭帶來女性悲劇，美色招禍，宜防暗算。",
     "en": "Ištar afflicted in the Scorpion — war brings tragedy to women; beauty invites danger; beware hidden schemes."},
    # ── Nergal (Mars) omens ───────────────────────────────────
    {"planet": "Mars",  "sign": "Aries",      "condition": "domicile",
     "cn": "Nergal 居雇農宮，軍隊出征大吉，將士英勇，敵方潰敗。",
     "en": "Nergal at home in the Hired Man — military campaigns are greatly favoured; soldiers are valiant; the enemy is routed."},
    {"planet": "Mars",  "sign": "Scorpio",    "condition": "domicile",
     "cn": "Nergal 在天蠍宮強盛，瘟疫肆虐之兆，邊境紛爭，祭司薦祭。",
     "en": "Nergal strong in the Scorpion — pestilence looms; border conflicts flare; priests must make offerings."},
    {"planet": "Mars",  "sign": "Capricorn",  "condition": "exalt",
     "cn": "Nergal 升揚山羊魚，冬日戰事有利，山地征伐，築城護國。",
     "en": "Nergal exalted in the Goat-Fish — winter campaigns are favoured; mountain warfare succeeds; city walls are strengthened."},
    {"planet": "Mars",  "sign": "Cancer",     "condition": "fall",
     "cn": "Nergal 落陷螃蟹，軍隊受困，將領患疾，夏日戰爭不利。",
     "en": "Nergal fallen in the Crab — the army is trapped; the general falls ill; summer warfare is inauspicious."},
    # ── Marduk (Jupiter) omens ────────────────────────────────
    {"planet": "Jupiter", "sign": "Sagittarius", "condition": "domicile",
     "cn": "Marduk 居射手宮，眾神賜福，王令天下，正義大行其道。",
     "en": "Marduk at home in the Archer — the gods bestow blessings; the king rules all lands; justice prevails."},
    {"planet": "Jupiter", "sign": "Pisces",   "condition": "domicile",
     "cn": "Marduk 在雙魚宮，神廟修復，宗教典儀昌盛，河流豐沛。",
     "en": "Marduk in the Tails — temples are restored; religious ceremonies flourish; rivers flow abundantly."},
    {"planet": "Jupiter", "sign": "Cancer",   "condition": "exalt",
     "cn": "Marduk 升揚螃蟹，眾神歡聚，農業豐年，王室喜慶大典。",
     "en": "Marduk exalted in the Crab — the gods rejoice; agricultural year is bountiful; royal celebrations abound."},
    {"planet": "Jupiter", "sign": "Gemini",   "condition": "detriment",
     "cn": "Marduk 在雙子受抑，法令不彰，文書爭議，財庫虧損。",
     "en": "Marduk afflicted in the Twins — laws falter; document disputes arise; the treasury is depleted."},
    # ── Ninurta (Saturn) omens ────────────────────────────────
    {"planet": "Saturn", "sign": "Capricorn", "condition": "domicile",
     "cn": "Ninurta 居山羊魚宮，農作豐收，水利工程順利，城牆堅固。",
     "en": "Ninurta at home in the Goat-Fish — harvests are abundant; irrigation works succeed; city walls stand firm."},
    {"planet": "Saturn", "sign": "Aquarius",  "condition": "domicile",
     "cn": "Ninurta 在大者宮，老者受尊，傳統習俗維繫，礦山有收。",
     "en": "Ninurta in the Great One — elders are respected; traditions are maintained; mines yield ore."},
    {"planet": "Saturn", "sign": "Libra",     "condition": "exalt",
     "cn": "Ninurta 升揚天秤，土地丈量精準，法律公正，邊界明確。",
     "en": "Ninurta exalted in the Scales — land surveys are accurate; laws are just; borders are clearly defined."},
    {"planet": "Saturn", "sign": "Aries",     "condition": "fall",
     "cn": "Ninurta 落陷雇農，農地荒廢，水渠乾涸，饑荒將至。",
     "en": "Ninurta fallen in the Hired Man — farmland lies fallow; irrigation channels dry up; famine approaches."},
    {"planet": "Saturn", "sign": "Cancer",    "condition": "detriment",
     "cn": "Ninurta 在螃蟹受制，夏日旱澇不定，建築工程延誤，老人多病。",
     "en": "Ninurta afflicted in the Crab — summer alternates between drought and flood; construction is delayed; the elderly suffer illness."},
    # ── Special phenomena ─────────────────────────────────────
    {"planet": "Venus",  "sign": None,        "condition": "morning_star",
     "cn": "Ištar 晨星升起，新的戰爭季節開始，女王即將登基或被廢。",
     "en": "Ištar rises as morning star — a new season of war begins; a queen ascends or is deposed."},
    {"planet": "Venus",  "sign": None,        "condition": "evening_star",
     "cn": "Ištar 夕星落日後現，愛情與外交繁盛，和平談判有望。",
     "en": "Ištar appears as evening star after sunset — love and diplomacy flourish; peace negotiations are favoured."},
    {"planet": "Jupiter", "sign": None,       "condition": "heliacal_rising",
     "cn": "Marduk 偕日升起，新年大典吉兆，諸神與王合一，神聖婚禮典儀。",
     "en": "Marduk rises heliacally — auspicious omen for the New Year festival; king and god are united in sacred marriage."},
    {"planet": "Mars",   "sign": None,        "condition": "retrograde",
     "cn": "Nergal 逆行，軍隊應先撤而非進攻，醫療祭儀宜即行，防瘟疫傳播。",
     "en": "Nergal retrogrades — armies should retreat rather than advance; medical rites should be performed immediately; guard against epidemic spread."},
]

# ============================================================
# Planet sign-condition lookup (for omen engine)
# ============================================================

def _get_planet_condition(planet: str, sign_idx: int) -> str:
    """Return the dignitary condition of a planet in a given sign index."""
    if sign_idx == EXALTATION.get(planet):
        return "exalt"
    if sign_idx in DOMICILE.get(planet, []):
        return "domicile"
    if sign_idx in DETRIMENT.get(planet, []):
        return "detriment"
    if sign_idx == FALL.get(planet):
        return "fall"
    return "neutral"
