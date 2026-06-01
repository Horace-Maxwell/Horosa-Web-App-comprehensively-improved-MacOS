"""
猶太 Mazzalot 占星模組 (Jewish Mazzalot Astrology Module)

猶太 Mazzalot（מַזָּלוֹת）占星是猶太傳統中的黃道體系，源自 Talmud（塔木德）、
Sefer Yetzirah（創造之書）與聖經星象解讀。

核心概念與歷史背景：

1. Mazzalot 一詞出自聖經（列王紀下 23:5；約伯記 38:32），意為「星宿 / 星座」。
   Talmud（Shabbat 156a）記載了十二 Mazzalot 與人格特質的對應關係。

2. Sefer Yetzirah（約公元 2–6 世紀）將 22 個希伯來字母分為三類：
   - 3 個母字母（Aleph, Mem, Shin）→ 元素
   - 7 個雙字母（Bet, Gimel, Dalet, Kaph, Pe, Resh, Tav）→ 七大行星
   - 12 個簡單字母 → 12 個 Mazzalot（黃道星座）

3. 十二支派（Twelve Tribes of Israel）與十二 Mazzalot 的對應源自
   Midrash（如 Bamidbar Rabbah 2:7），以雅各祝福（創世記 49 章）
   與摩西祝福（申命記 33 章）為基礎。

4. 猶太傳統強調「Ein Mazal l'Yisrael」（אין מזל לישראל）——
   以色列人可以透過 Torah 學習與善行超越星宿影響，
   因此本模組的靈性解讀側重救贖與教導，而非宿命預測。

本模組 100% 參考 kabbalistic.py 的架構、類別設計、函數命名、常量定義方式、
註解風格、i18n 呼叫方式與 chart dict 格式來實現。
使用 sidereal zodiac（Fagan-Bradley ayanamsa）計算行星位置，
與巴比倫體系保持天文計算的一致性。
"""

import math
import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

from astro.i18n import t

# ============================================================
# Ayanamsa 設定 (Sidereal Mode)
# ============================================================
MAZZALOT_AYANAMSA_MODE = swe.SIDM_FAGAN_BRADLEY

# ============================================================
# 12 Mazzalot 黃道星座 — Talmud 標準希伯來名稱
# (索引, 拉丁轉寫, 希伯來文, 中文名, 英文名, 西洋對應, 支派對應)
# ============================================================
MAZZALOT_SIGNS = [
    ("0",  "Ṭaleh",    "טָלֶה",      "公羊 / 羔羊",    "The Ram",      "Aries",       "Reuben / Judah"),
    ("1",  "Shor",      "שׁוֹר",      "公牛",           "The Bull",     "Taurus",      "Joseph / Ephraim"),
    ("2",  "Teomim",    "תְּאוֹמִים",  "雙子",           "The Twins",    "Gemini",      "Simeon / Levi"),
    ("3",  "Sartan",    "סַרְטָן",    "螃蟹",           "The Crab",     "Cancer",      "Issachar"),
    ("4",  "Aryeh",     "אַרְיֵה",    "獅子",           "The Lion",     "Leo",         "Judah / Dan"),
    ("5",  "Betulah",   "בְּתוּלָה",  "處女",           "The Virgin",   "Virgo",       "Naphtali"),
    ("6",  "Moznayim",  "מֹאזְנַיִם",  "天秤",           "The Scales",   "Libra",       "Asher"),
    ("7",  "Akrav",     "עַקְרָב",    "蠍子",           "The Scorpion", "Scorpio",     "Dan / Manasseh"),
    ("8",  "Keshet",    "קֶשֶׁת",     "弓 / 射手",      "The Bow",      "Sagittarius", "Gad"),
    ("9",  "Gedi",      "גְּדִי",     "山羊 / 羔羊",    "The Kid",      "Capricorn",   "Zebulun"),
    ("10", "Dli",       "דְּלִי",     "水瓶 / 水桶",    "The Bucket",   "Aquarius",    "Benjamin"),
    ("11", "Dagim",     "דָּגִים",    "雙魚",           "The Fish",     "Pisces",      "Joseph / Benjamin"),
]

# 西洋星座名稱列表（用於交叉參照）
ZODIAC_SIGNS = [s[5] for s in MAZZALOT_SIGNS]
SIGN_CN = {s[5]: s[3] for s in MAZZALOT_SIGNS}
SIGN_HEBREW = {s[5]: s[2] for s in MAZZALOT_SIGNS}
SIGN_TRANSLITERATION = {s[5]: s[1] for s in MAZZALOT_SIGNS}

# ============================================================
# 希伯來簡單字母對應 — Sefer Yetzirah 傳統
# 12 個簡單字母分別對應 12 個 Mazzalot
# ============================================================
MAZZALOT_HEBREW_LETTERS = {
    "Aries":       "ה (Heh)",
    "Taurus":      "ו (Vav)",
    "Gemini":      "ז (Zayin)",
    "Cancer":      "ח (Chet)",
    "Leo":         "ט (Tet)",
    "Virgo":       "י (Yod)",
    "Libra":       "ל (Lamed)",
    "Scorpio":     "נ (Nun)",
    "Sagittarius": "ס (Samekh)",
    "Capricorn":   "ע (Ayin)",
    "Aquarius":    "צ (Tsade)",
    "Pisces":      "ק (Qoph)",
}

# ============================================================
# 十二支派對應 — Midrash / Bamidbar Rabbah 傳統
# 包含支派名稱、希伯來文、聖經祝福摘要
# ============================================================
MAZZALOT_TRIBES = {
    "Aries":       {"tribe": "Reuben / Judah",      "hebrew": "רְאוּבֵן / יְהוּדָה",   "blessing": "長子之力，獅子之勇 (創49:3,9)"},
    "Taurus":      {"tribe": "Joseph / Ephraim",     "hebrew": "יוֹסֵף / אֶפְרַיִם",   "blessing": "豐盛的枝子，如牛之首生 (申33:17)"},
    "Gemini":      {"tribe": "Simeon / Levi",        "hebrew": "שִׁמְעוֹן / לֵוִי",     "blessing": "雙子兄弟，利器為兵械 (創49:5)"},
    "Cancer":      {"tribe": "Issachar",             "hebrew": "יִשָּׂשכָר",            "blessing": "強壯之驢，伏於二負之間 (創49:14)"},
    "Leo":         {"tribe": "Judah / Dan",          "hebrew": "יְהוּדָה / דָּן",       "blessing": "猶大是獅子，但是法官 (創49:9,16)"},
    "Virgo":       {"tribe": "Naphtali",             "hebrew": "נַפְתָּלִי",            "blessing": "被釋放的母鹿，出嘉美的言語 (創49:21)"},
    "Libra":       {"tribe": "Asher",                "hebrew": "אָשֵׁר",               "blessing": "糧食豐富，供應君王美味 (創49:20)"},
    "Scorpio":     {"tribe": "Dan / Manasseh",       "hebrew": "דָּן / מְנַשֶּׁה",      "blessing": "但必作道上的蛇 (創49:17)"},
    "Sagittarius": {"tribe": "Gad",                  "hebrew": "גָּד",                 "blessing": "追兵追他，他卻追趕他們 (創49:19)"},
    "Capricorn":   {"tribe": "Zebulun",              "hebrew": "זְבוּלֻן",             "blessing": "住在海口，為船隻的港口 (創49:13)"},
    "Aquarius":    {"tribe": "Benjamin",             "hebrew": "בִּנְיָמִין",           "blessing": "如狼，早晨吃食物 (創49:27)"},
    "Pisces":      {"tribe": "Joseph / Benjamin",    "hebrew": "יוֹסֵף / בִּנְיָמִין",  "blessing": "多結果子的枝子 (創49:22)"},
}

# ============================================================
# Talmud 風格靈性解讀 (Spiritual Omens)
# 基於 Shabbat 156a 的行星性格描述
# ============================================================
MAZZALOT_OMENS = {
    "Aries": {
        "strong": "Ṭaleh 之子，性情勇猛果決，如亞伯拉罕獻羔羊之信心。主行動力與開創。",
        "strong_en": "Born under Ṭaleh — bold and decisive, like Abraham's faith in offering the ram. Governs initiative and pioneering spirit.",
        "weak": "Ṭaleh 之勢弱，須防衝動行事，當以 Torah 智慧約束烈火性情。",
        "weak_en": "Ṭaleh is weakened — guard against impulsiveness; temper fiery nature with Torah wisdom.",
    },
    "Taurus": {
        "strong": "Shor 之子，穩重堅毅，如約瑟在埃及的忍耐。主物質豐盛與勤勉。",
        "strong_en": "Born under Shor — steadfast and resilient, like Joseph's patience in Egypt. Governs material abundance and diligence.",
        "weak": "Shor 之勢弱，固執可能成為絆腳石，當學習靈活變通。",
        "weak_en": "Shor is weakened — stubbornness may become a stumbling block; learn flexibility.",
    },
    "Gemini": {
        "strong": "Teomim 之子，聰慧善辯，如以利沙之雙倍靈恩。主溝通與學識。",
        "strong_en": "Born under Teomim — witty and articulate, like Elisha's double portion. Governs communication and knowledge.",
        "weak": "Teomim 之勢弱，易心志不定，當以信仰錨定心靈。",
        "weak_en": "Teomim is weakened — prone to indecision; anchor the spirit with faith.",
    },
    "Cancer": {
        "strong": "Sartan 之子，感情豐富，重視家庭，如以撒迦安居帳幕。主家庭與照護。",
        "strong_en": "Born under Sartan — emotionally rich, family-oriented, like Issachar dwelling in tents. Governs home and nurturing.",
        "weak": "Sartan 之勢弱，情緒易波動，當以禱告穩定內心。",
        "weak_en": "Sartan is weakened — emotions fluctuate; stabilize the heart through prayer.",
    },
    "Leo": {
        "strong": "Aryeh 之子，領導力強，如猶大之獅。主權威與慷慨。",
        "strong_en": "Born under Aryeh — strong leadership, like the Lion of Judah. Governs authority and generosity.",
        "weak": "Aryeh 之勢弱，驕傲可能遮蔽智慧，當以謙卑事奉。",
        "weak_en": "Aryeh is weakened — pride may cloud wisdom; serve with humility.",
    },
    "Virgo": {
        "strong": "Betulah 之子，心思縝密，如以斯帖之細心。主分析與純潔。",
        "strong_en": "Born under Betulah — meticulous and careful, like Esther's discernment. Governs analysis and purity.",
        "weak": "Betulah 之勢弱，過度挑剔可能傷人，當以慈悲平衡完美主義。",
        "weak_en": "Betulah is weakened — excessive criticism may hurt others; balance perfectionism with compassion.",
    },
    "Libra": {
        "strong": "Moznayim 之子，追求公義，如所羅門王的智慧審判。主平衡與和諧。",
        "strong_en": "Born under Moznayim — pursues justice, like King Solomon's wise judgment. Governs balance and harmony.",
        "weak": "Moznayim 之勢弱，猶豫不決，當以 Torah 律法為判斷基準。",
        "weak_en": "Moznayim is weakened — indecisive; let Torah law guide your judgments.",
    },
    "Scorpio": {
        "strong": "Akrav 之子，意志堅定，洞察力深，如以利亞的烈火精神。主轉化與重生。",
        "strong_en": "Born under Akrav — strong-willed with deep insight, like Elijah's fiery spirit. Governs transformation and rebirth.",
        "weak": "Akrav 之勢弱，報復心重，當以寬恕代替怨恨。",
        "weak_en": "Akrav is weakened — vengeful tendencies; replace resentment with forgiveness.",
    },
    "Sagittarius": {
        "strong": "Keshet 之子，追求真理，如亞伯拉罕的尋神之旅。主智慧與探索。",
        "strong_en": "Born under Keshet — truth-seeker, like Abraham's journey to find God. Governs wisdom and exploration.",
        "weak": "Keshet 之勢弱，過度樂觀可能輕忽風險，當以審慎行事。",
        "weak_en": "Keshet is weakened — over-optimism may overlook risks; act with prudence.",
    },
    "Capricorn": {
        "strong": "Gedi 之子，勤勉自律，如尼希米重建城牆之堅持。主責任與成就。",
        "strong_en": "Born under Gedi — diligent and disciplined, like Nehemiah's perseverance in rebuilding. Governs responsibility and achievement.",
        "weak": "Gedi 之勢弱，過度嚴苛，當以恩慈待人。",
        "weak_en": "Gedi is weakened — overly harsh; treat others with grace.",
    },
    "Aquarius": {
        "strong": "Dli 之子，富有遠見，如摩西帶領眾人走向自由。主革新與人道。",
        "strong_en": "Born under Dli — visionary, like Moses leading the people to freedom. Governs innovation and humanitarianism.",
        "weak": "Dli 之勢弱，過於疏離，當以社群連結溫暖人心。",
        "weak_en": "Dli is weakened — too detached; warm hearts through community bonds.",
    },
    "Pisces": {
        "strong": "Dagim 之子，直覺強烈，如約拿在大魚腹中的靈性覺醒。主靈感與慈悲。",
        "strong_en": "Born under Dagim — strong intuition, like Jonah's spiritual awakening in the great fish. Governs inspiration and compassion.",
        "weak": "Dagim 之勢弱，容易逃避現實，當以信仰面對困難。",
        "weak_en": "Dagim is weakened — prone to escapism; face difficulties with faith.",
    },
}

# ============================================================
# 希伯來月份對應
# ============================================================
MAZZALOT_MONTHS = {
    "Aries":       "Nisan (尼散月)",
    "Taurus":      "Iyyar (以珥月)",
    "Gemini":      "Sivan (西彎月)",
    "Cancer":      "Tammuz (搭模斯月)",
    "Leo":         "Av (埃波月)",
    "Virgo":       "Elul (以祿月)",
    "Libra":       "Tishrei (提斯利月)",
    "Scorpio":     "Cheshvan (乞斯流月)",
    "Sagittarius": "Kislev (基斯流月)",
    "Capricorn":   "Tevet (提別月)",
    "Aquarius":    "Shevat (細罷特月)",
    "Pisces":      "Adar (亞達月)",
}

# ============================================================
# 行星對應 — 七大古典行星（與 Babylonian 一致）
# ============================================================
MAZZALOT_PLANETS = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
}

GRAHA_CN = {
    "Sun": "太陽 ☉", "Moon": "月亮 ☽", "Mercury": "水星 ☿",
    "Venus": "金星 ♀", "Mars": "火星 ♂", "Jupiter": "木星 ♃",
    "Saturn": "土星 ♄",
}

PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿",
    "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
}

PLANET_COLORS = {
    "Sun": "#b8860b", "Moon": "#556b7f", "Mercury": "#8b6914",
    "Venus": "#2e7d32", "Mars": "#b71c1c", "Jupiter": "#1565c0",
    "Saturn": "#4a4a4a",
}

# 黃道符號
ZODIAC_GLYPHS = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓",
]

# ============================================================
# 品位表 — 廟旺落陷（用於 omen 判斷）
# ============================================================
DOMICILE = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
            "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10]}
EXALTATION = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5,
              "Jupiter": 3, "Venus": 11, "Saturn": 6}
DETRIMENT = {"Sun": [10], "Moon": [9], "Mars": [1, 6], "Mercury": [8, 11],
             "Jupiter": [2, 5], "Venus": [0, 7], "Saturn": [3, 4]}
FALL = {"Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11,
        "Jupiter": 9, "Venus": 5, "Saturn": 0}


# ============================================================
# 內部工具函數 (Internal Helpers)
# ============================================================
def _sign_idx(lon):
    """根據黃經返回星座索引 (0–11)"""
    return int(lon / 30) % 12


def _sign_deg(lon):
    """返回在星座內的度數"""
    return lon % 30


def _normalize(deg):
    """將角度正規化至 0–360°"""
    return deg % 360


def _find_house(lon, cusps):
    """根據黃經與宮頭列表找到所在宮位 (1–12)"""
    for i in range(12):
        c1 = cusps[i]
        c2 = cusps[(i + 1) % 12]
        if c2 < c1:
            if lon >= c1 or lon < c2:
                return i + 1
        elif c1 <= lon < c2:
            return i + 1
    return 1


def _format_deg(deg):
    """格式化度數為 d°mm'ss" 格式"""
    deg = _normalize(deg)
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""


# ============================================================
# 資料類 (Data Classes)
# ============================================================
@dataclass
class MazzalotPlanetPosition:
    """單一行星在 sidereal 黃道中的位置及 Mazzalot 對應"""
    name: str
    longitude: float
    sign_idx: int
    sign_hebrew: str         # 希伯來星座名
    sign_transliteration: str  # 拉丁轉寫
    sign_cn: str             # 中文名
    sign_en: str             # 英文名
    sign_western: str        # 西洋對應
    sign_degree: float
    house: int
    hebrew_letter: str       # Sefer Yetzirah 對應字母
    tribe: str               # 支派對應
    tribe_hebrew: str        # 支派希伯來文
    hebrew_month: str        # 希伯來月份


@dataclass
class MazzalotOmen:
    """Talmud 風格靈性解讀"""
    planet: str
    condition: str           # "strong" or "weak"
    text: str                # 中文解讀
    text_en: str = ""        # 英文解讀


@dataclass
class MazzalotChart:
    """完整的猶太 Mazzalot 占星排盤"""
    ascendant: float
    midheaven: float
    is_day_chart: bool
    planet_longitudes: dict       # {name: sidereal_longitude}
    planet_houses: dict           # {name: house_number}
    house_cusps: list             # 12 sidereal cusps
    positions: list               # list[MazzalotPlanetPosition]
    omens: list                   # list[MazzalotOmen]
    aspects: list = field(default_factory=list)
    ayanamsa: float = 0.0
    julian_day: float = 0.0
    # 上升點對應資訊
    asc_mazzalot: str = ""        # 上升 Mazzalot 名稱
    asc_tribe: str = ""           # 上升支派
    asc_letter: str = ""          # 上升希伯來字母
    asc_month: str = ""           # 上升希伯來月份


# ============================================================
# 相位計算 (Aspect Calculation)
# ============================================================
_MAJOR_ASPECTS = [
    ("conjunction", 0, 8),
    ("opposition", 180, 8),
    ("trine", 120, 8),
    ("square", 90, 7),
    ("sextile", 60, 6),
]


def _compute_aspects(planet_longs):
    """計算行星之間的主要相位"""
    aspects = []
    names = list(planet_longs.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]
            diff = abs(planet_longs[p1] - planet_longs[p2])
            if diff > 180:
                diff = 360 - diff
            for asp_name, asp_angle, orb in _MAJOR_ASPECTS:
                if abs(diff - asp_angle) <= orb:
                    aspects.append({
                        "planet1": p1,
                        "planet2": p2,
                        "aspect": asp_name,
                        "angle": round(diff, 2),
                        "orb": round(abs(diff - asp_angle), 2),
                    })
                    break
    return aspects


# ============================================================
# Omen 判斷 (Spiritual Omen Determination)
# ============================================================
def _determine_omen(planet, sign_idx):
    """根據品位判斷靈性 omen（基於 Talmud Shabbat 156a 傳統）

    Returns
    -------
    tuple of (condition, text, text_en)
    """
    western_sign = ZODIAC_SIGNS[sign_idx]
    is_strong = (
        sign_idx in DOMICILE.get(planet, [])
        or EXALTATION.get(planet) == sign_idx
    )
    condition = "strong" if is_strong else "weak"
    omen_dict = MAZZALOT_OMENS.get(western_sign, {})
    text = omen_dict.get(condition, "")
    text_en = omen_dict.get(f"{condition}_en", "")
    return condition, text, text_en


# ============================================================
# 主計算函數 (Main Compute Function)
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def compute_mazzalot_chart(year, month, day, hour, minute, timezone,
                           lat, lon):
    """計算猶太 Mazzalot 占星排盤（Sidereal Zodiac, Placidus Houses）

    Parameters
    ----------
    year, month, day : int
        公曆出生日期
    hour, minute : int
        出生時間（當地時間）
    timezone : float
        UTC 偏移量（小時）
    lat, lon : float
        地理緯度 / 經度

    Returns
    -------
    MazzalotChart
    """
    # Julian Day (UT)
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)

    # 設定 sidereal 模式
    swe.set_sid_mode(MAZZALOT_AYANAMSA_MODE)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # 宮位計算（sidereal）
    cusps_tuple, ascmc = swe.houses_ex(jd, lat, lon,
                                       b'P',  # Placidus
                                       swe.FLG_SIDEREAL)
    cusps = list(cusps_tuple)
    asc = ascmc[0]
    mc = ascmc[1]

    # 日夜盤判斷
    sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    sun_house = _find_house(sun_pos, cusps)
    is_day = sun_house in (7, 8, 9, 10, 11, 12)

    # 計算行星位置
    planet_longs = {}
    planet_houses = {}
    positions = []
    omens = []

    for name, pid in MAZZALOT_PLANETS.items():
        result = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        sid_lon = result[0][0]
        idx = _sign_idx(sid_lon)
        house = _find_house(sid_lon, cusps)
        planet_longs[name] = sid_lon
        planet_houses[name] = house

        mz = MAZZALOT_SIGNS[idx]
        western_sign = mz[5]
        tribe_info = MAZZALOT_TRIBES.get(western_sign, {})

        positions.append(MazzalotPlanetPosition(
            name=name,
            longitude=round(sid_lon, 4),
            sign_idx=idx,
            sign_hebrew=mz[2],
            sign_transliteration=mz[1],
            sign_cn=mz[3],
            sign_en=mz[4],
            sign_western=western_sign,
            sign_degree=round(_sign_deg(sid_lon), 2),
            house=house,
            hebrew_letter=MAZZALOT_HEBREW_LETTERS.get(western_sign, "—"),
            tribe=tribe_info.get("tribe", "—"),
            tribe_hebrew=tribe_info.get("hebrew", "—"),
            hebrew_month=MAZZALOT_MONTHS.get(western_sign, "—"),
        ))

        condition, text, text_en = _determine_omen(name, idx)
        omens.append(MazzalotOmen(
            planet=name,
            condition=condition,
            text=text,
            text_en=text_en,
        ))

    # 相位計算
    aspects = _compute_aspects(planet_longs)

    # 上升點對應
    asc_idx = _sign_idx(asc)
    asc_sign = ZODIAC_SIGNS[asc_idx]
    asc_tribe_info = MAZZALOT_TRIBES.get(asc_sign, {})

    return MazzalotChart(
        ascendant=asc,
        midheaven=mc,
        is_day_chart=is_day,
        planet_longitudes=planet_longs,
        planet_houses=planet_houses,
        house_cusps=cusps,
        positions=positions,
        omens=omens,
        aspects=aspects,
        ayanamsa=round(ayanamsa, 4),
        julian_day=jd,
        asc_mazzalot=MAZZALOT_SIGNS[asc_idx][1],
        asc_tribe=asc_tribe_info.get("tribe", "—"),
        asc_letter=MAZZALOT_HEBREW_LETTERS.get(asc_sign, "—"),
        asc_month=MAZZALOT_MONTHS.get(asc_sign, "—"),
    )


# ============================================================
# 大衛之星輪盤 SVG (Star of David Wheel SVG)
# ============================================================
def build_mazzalot_star_of_david_svg(chart, year=None, month=None, day=None,
                                     hour=None, minute=None, tz=None,
                                     location=""):
    """產生大衛之星輪盤 SVG — 復古希伯來文字風格

    以六芒星（Star of David / Magen David）為核心結構，
    將 12 個 Mazzalot 分佈於外環 12 區間，
    六芒星的 6 個頂點標示六個方向 / 支派，
    中央顯示 Torah 卷軸與排盤資訊。

    Parameters
    ----------
    chart : MazzalotChart
    year, month, day, hour, minute, tz : 出生資料（用於中央顯示）
    location : str

    Returns
    -------
    str — 完整的 <svg> 標記
    """
    SIZE = 620
    CX, CY = SIZE / 2, SIZE / 2
    R_OUTER = 270
    R_INNER = 200
    R_STAR = 155
    R_CENTER = 60

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SIZE} {SIZE}" '
        f'style="width:100%;max-width:620px;margin:auto;display:block;" '
        f'font-family="serif">'
    )

    # ── Defs: 羊皮紙背景漸層 + 濾鏡 ──────────────────────────
    svg.append('<defs>')
    svg.append(
        '<radialGradient id="parchment_bg" cx="50%" cy="50%" r="55%">'
        '<stop offset="0%" stop-color="#f5e6c8"/>'
        '<stop offset="60%" stop-color="#e8d5a8"/>'
        '<stop offset="100%" stop-color="#c9b48c"/>'
        '</radialGradient>'
    )
    # 紙紋濾鏡
    svg.append(
        '<filter id="parchment_noise" x="0%" y="0%" width="100%" height="100%">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.5" '
        'numOctaves="3" stitchTiles="stitch" result="noise"/>'
        '<feColorMatrix type="saturate" values="0" in="noise" result="grey"/>'
        '<feBlend in="SourceGraphic" in2="grey" mode="multiply"/>'
        '</filter>'
    )
    # 行星光暈
    svg.append(
        '<filter id="mz_planet_glow">'
        '<feGaussianBlur stdDeviation="2" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/>'
        '<feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    )
    svg.append('</defs>')

    # ── 背景圓（羊皮紙風格）──────────────────────────────────
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER + 20}" '
        f'fill="url(#parchment_bg)" filter="url(#parchment_noise)" '
        f'stroke="#8b7355" stroke-width="3"/>'
    )

    # ── Torah 卷軸邊框裝飾 ────────────────────────────────────
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER + 15}" '
        f'fill="none" stroke="#6b4c2a" stroke-width="1" '
        f'stroke-dasharray="8,4"/>'
    )
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER + 8}" '
        f'fill="none" stroke="#8b6914" stroke-width="0.5"/>'
    )

    # ── 外環（12 區間分割）───────────────────────────────────
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER}" '
        f'fill="none" stroke="#5c3a1e" stroke-width="2"/>'
    )
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_INNER}" '
        f'fill="none" stroke="#5c3a1e" stroke-width="1.5"/>'
    )

    # 12 Mazzalot 區間分割線與標籤
    for i in range(12):
        angle = i * 30
        rad = math.radians(angle)
        # 分割線
        x1 = CX + R_INNER * math.cos(rad)
        y1 = CY - R_INNER * math.sin(rad)
        x2 = CX + R_OUTER * math.cos(rad)
        y2 = CY - R_OUTER * math.sin(rad)
        svg.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#5c3a1e" stroke-width="1"/>'
        )

        # Mazzalot 標籤（區間中央）
        mid_angle = angle + 15
        mid_rad = math.radians(mid_angle)

        # 希伯來文名稱（外圈）
        r_hebrew = (R_OUTER + R_INNER) / 2 + 15
        hx = CX + r_hebrew * math.cos(mid_rad)
        hy = CY - r_hebrew * math.sin(mid_rad)
        mz = MAZZALOT_SIGNS[i]
        svg.append(
            f'<text x="{hx:.1f}" y="{hy:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#3a2510" '
            f'font-size="12" font-weight="bold">{mz[2]}</text>'
        )

        # 拉丁轉寫（中圈）
        r_latin = (R_OUTER + R_INNER) / 2 - 5
        lx = CX + r_latin * math.cos(mid_rad)
        ly = CY - r_latin * math.sin(mid_rad)
        svg.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#6b4c2a" '
            f'font-size="7" font-style="italic">{mz[1]}</text>'
        )

        # 黃道符號（內側）
        r_glyph = (R_OUTER + R_INNER) / 2 - 20
        gx = CX + r_glyph * math.cos(mid_rad)
        gy = CY - r_glyph * math.sin(mid_rad)
        svg.append(
            f'<text x="{gx:.1f}" y="{gy:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="14">{ZODIAC_GLYPHS[i]}</text>'
        )

        # 希伯來字母（最外側小字）
        r_letter = R_OUTER + 5
        letter_x = CX + r_letter * math.cos(mid_rad)
        letter_y = CY - r_letter * math.sin(mid_rad)
        letter_char = MAZZALOT_HEBREW_LETTERS.get(ZODIAC_SIGNS[i], "")
        if letter_char:
            # 只取第一個字元（字母本身）
            letter_display = letter_char.split(" ")[0]
            svg.append(
                f'<text x="{letter_x:.1f}" y="{letter_y:.1f}" text-anchor="middle" '
                f'dominant-baseline="central" fill="#8b6914" '
                f'font-size="9">{letter_display}</text>'
            )

    # ── 大衛之星（六芒星）────────────────────────────────────
    # 正三角形 + 倒三角形
    star_points_up = []
    star_points_down = []
    for i in range(3):
        # 正三角形：頂點在上（90°, 210°, 330°）
        angle_up = 90 + i * 120
        rad_up = math.radians(angle_up)
        star_points_up.append(
            (CX + R_STAR * math.cos(rad_up),
             CY - R_STAR * math.sin(rad_up))
        )
        # 倒三角形：頂點在下（270°, 30°, 150°）
        angle_down = 270 + i * 120
        rad_down = math.radians(angle_down)
        star_points_down.append(
            (CX + R_STAR * math.cos(rad_down),
             CY - R_STAR * math.sin(rad_down))
        )

    # 繪製正三角形
    pts_up = " ".join(f"{x:.1f},{y:.1f}" for x, y in star_points_up)
    svg.append(
        f'<polygon points="{pts_up}" '
        f'fill="none" stroke="#1a237e" stroke-width="2" '
        f'opacity="0.7"/>'
    )
    # 繪製倒三角形
    pts_down = " ".join(f"{x:.1f},{y:.1f}" for x, y in star_points_down)
    svg.append(
        f'<polygon points="{pts_down}" '
        f'fill="none" stroke="#1a237e" stroke-width="2" '
        f'opacity="0.7"/>'
    )

    # ── 行星標記 ──────────────────────────────────────────────
    for pos in chart.positions:
        # 計算行星在輪盤中的角度位置
        sector = pos.sign_idx
        sector_centre_angle = sector * 30 + 15

        # 計算同區間行星數量以避免重疊
        planets_in_sector = [p for p in chart.positions
                             if p.sign_idx == sector]
        idx_in_sector = planets_in_sector.index(pos)
        n_in_sector = len(planets_in_sector)

        # 在內環與六芒星之間放置行星
        r_base = R_CENTER + 25
        r_step = (R_INNER - R_CENTER - 50) / max(n_in_sector, 1)
        r_planet = r_base + idx_in_sector * r_step

        # 角度微調
        angle_spread = 15
        angle_offset = (idx_in_sector - (n_in_sector - 1) / 2) * (
            angle_spread / max(n_in_sector, 1))
        pa = sector_centre_angle + angle_offset
        rad = math.radians(pa)

        px = CX + r_planet * math.cos(rad)
        py = CY - r_planet * math.sin(rad)

        pglyph = PLANET_GLYPHS.get(pos.name, pos.name[0])
        pcolor = PLANET_COLORS.get(pos.name, "#5c3a1e")

        # 行星光暈
        svg.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="10" '
            f'fill="{pcolor}" fill-opacity="0.12" stroke="none" '
            f'filter="url(#mz_planet_glow)"/>'
        )
        # 行星符號
        svg.append(
            f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{pcolor}" '
            f'font-size="16" font-weight="bold">{pglyph}</text>'
        )
        # 度數標籤
        r_label = r_planet + 16
        lx = CX + r_label * math.cos(rad)
        ly = CY - r_label * math.sin(rad)
        svg.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="6">{pos.sign_degree:.0f}° {pos.sign_transliteration}</text>'
        )

    # ── 中央圓（Torah 卷軸風格）──────────────────────────────
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_CENTER}" '
        f'fill="#f5e6c8" stroke="#6b4c2a" stroke-width="2"/>'
    )

    # 中央文字
    svg.append(
        f'<text x="{CX}" y="{CY - 40}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#1a237e" '
        f'font-size="12" font-weight="bold">✡ מַזָּלוֹת</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY - 26}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#3a2510" '
        f'font-size="8">Mazzalot</text>'
    )

    sect_label = "☉ Day / 日生" if chart.is_day_chart else "☽ Night / 夜生"
    svg.append(
        f'<text x="{CX}" y="{CY - 10}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#5c3a1e" '
        f'font-size="7">{sect_label}</text>'
    )

    if year is not None and month is not None and day is not None:
        date_str = f"{year}-{month:02d}-{day:02d}"
        svg.append(
            f'<text x="{CX}" y="{CY + 4}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="7">{date_str}</text>'
        )

    if hour is not None and minute is not None:
        tz_str = f" UTC{tz:+.1f}" if tz is not None else ""
        time_str = f"{hour:02d}:{minute:02d}{tz_str}"
        svg.append(
            f'<text x="{CX}" y="{CY + 16}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#5c3a1e" '
            f'font-size="7">{time_str}</text>'
        )

    # 上升點資訊
    asc_idx = _sign_idx(chart.ascendant)
    asc_deg = round(_sign_deg(chart.ascendant), 1)
    asc_mz = MAZZALOT_SIGNS[asc_idx]
    svg.append(
        f'<text x="{CX}" y="{CY + 30}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#8b4513" '
        f'font-size="7">ASC {ZODIAC_GLYPHS[asc_idx]} '
        f'{asc_mz[2]} {asc_deg}°</text>'
    )

    if location:
        svg.append(
            f'<text x="{CX}" y="{CY + 42}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#7a5c30" '
            f'font-size="6">{location[:25]}</text>'
        )

    # ── Ein Mazal 銘文（底部）────────────────────────────────
    svg.append(
        f'<text x="{CX}" y="{SIZE - 10}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#6b4c2a" '
        f'font-size="8" font-style="italic">'
        f'אין מזל לישראל — Ein Mazal l\'Yisrael</text>'
    )

    svg.append("</svg>")
    return "\n".join(svg)


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================
def render_mazzalot_chart(chart, after_chart_hook=None):
    """渲染完整的猶太 Mazzalot 占星排盤

    Parameters
    ----------
    chart : MazzalotChart
    after_chart_hook : callable, optional
        渲染主要排盤後呼叫的鉤子函數
    """
    st.subheader(t("mazzalot_chart_title"))
    st.info(
        f"**Ayanamsa**: {chart.ayanamsa}° (Fagan-Bradley) | "
        f"**Sect**: {'Day ☉ 日生' if chart.is_day_chart else 'Night ☽ 夜生'} | "
        f"**JD**: {chart.julian_day:.4f}"
    )

    # ── 上升點（Ascendant）資訊 ───────────────────────────────
    st.markdown(
        f"**✡ {t('mazzalot_ascendant')}**: {chart.asc_mazzalot} "
        f"({_format_deg(chart.ascendant)}) — "
        f"{t('mazzalot_col_tribe')}: {chart.asc_tribe} | "
        f"{t('mazzalot_col_letter')}: {chart.asc_letter} | "
        f"{t('mazzalot_col_month')}: {chart.asc_month}"
    )

    # ── 靈性提醒 ─────────────────────────────────────────────
    st.caption(
        "💡 *אין מזל לישראל — Ein Mazal l'Yisrael* — "
        "猶太傳統認為以色列人可以透過 Torah 學習與善行超越星宿影響。"
    )

    if after_chart_hook:
        after_chart_hook()

    # ── 行星位置表 ────────────────────────────────────────────
    st.markdown("#### ✡ " + t("mazzalot_planet_positions"))
    pos_data = []
    for pos in chart.positions:
        pos_data.append({
            t("mazzalot_col_planet"): f"{pos.name} ({GRAHA_CN.get(pos.name, pos.name)})",
            t("mazzalot_col_mazzalot"): f"{pos.sign_hebrew} {pos.sign_transliteration}",
            t("mazzalot_col_degree"): f"{pos.sign_degree:.2f}°",
            t("mazzalot_col_house"): pos.house,
            t("mazzalot_col_letter"): pos.hebrew_letter,
            t("mazzalot_col_tribe"): f"{pos.tribe} ({pos.tribe_hebrew})",
            t("mazzalot_col_month"): pos.hebrew_month,
        })
    if pos_data:
        st.dataframe(pos_data, width="stretch")

    # ── 靈性解讀 (Omens) ─────────────────────────────────────
    st.markdown("#### 📜 " + t("mazzalot_omens_title"))
    for omen in chart.omens:
        icon = "🌟" if omen.condition == "strong" else "⚠️"
        en_part = f"  \n_{omen.text_en}_" if omen.text_en else ""
        st.markdown(
            f"{icon} **{omen.planet}** ({GRAHA_CN.get(omen.planet, omen.planet)}) — "
            f"*{omen.condition.upper()}*: {omen.text}{en_part}"
        )

    # ── 相位 (Aspects) ───────────────────────────────────────
    if chart.aspects:
        st.markdown("#### ⚡ " + t("mazzalot_aspects_title"))
        asp_data = []
        for asp in chart.aspects:
            asp_data.append({
                t("mazzalot_col_planet") + " 1": asp["planet1"],
                t("mazzalot_col_planet") + " 2": asp["planet2"],
                t("mazzalot_col_aspect"): asp["aspect"].capitalize(),
                t("mazzalot_col_angle"): f"{asp['angle']:.2f}°",
                t("mazzalot_col_orb"): f"{asp['orb']:.2f}°",
            })
        st.dataframe(asp_data, width="stretch")

    # ── 宮位 (Houses) ────────────────────────────────────────
    st.markdown("#### 🏛️ " + t("mazzalot_houses_title"))
    house_data = []
    for i, cusp in enumerate(chart.house_cusps):
        idx = _sign_idx(cusp)
        mz = MAZZALOT_SIGNS[idx]
        house_data.append({
            t("mazzalot_col_house"): i + 1,
            t("mazzalot_col_cusp"): f"{cusp:.2f}°",
            t("mazzalot_col_mazzalot"): f"{mz[2]} {mz[1]}",
            t("mazzalot_col_letter"): MAZZALOT_HEBREW_LETTERS.get(mz[5], "—"),
        })
    st.dataframe(house_data, width="stretch")
