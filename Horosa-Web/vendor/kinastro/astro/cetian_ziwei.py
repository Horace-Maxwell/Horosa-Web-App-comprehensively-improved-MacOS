"""
策天十八飛星紫微斗數排盤模組 (Ce Tian 18 Flying Stars Zi Wei Dou Shu Chart Module)

策天十八飛星紫微斗數，又稱十八飛星、策天派、北派紫微、道藏紫微，
是紫微斗數的古法前身與重要分支。源自明代《十八飛星策天紫微斗數全集》，
由陳希夷（希夷先生）傳承，後與標準紫微斗數合併。

與標準紫微斗數的區別：
- 使用十八飛星（而非標準十四主星），包含十一正曜及七副曜
- 每宮至少有正曜＋副曜，不存在空宮
- 重視「飛星」技術與四化飛化（星曜飛入他宮的影響）
- 以單宮獨斷為主，較少使用三方四會
- 需計算節氣（Solar Terms）影響星曜落度
- 強調古法格局，如刑刃哭姚等副曜的特殊解讀

飛星技術特點：
  十八飛星的核心在於「飛」——每顆星有其固定的飛化規則，
  星曜會由本宮飛入他宮，產生吉凶影響。此技術早於後世
  四化飛星系統（祿權科忌），是紫微斗數飛星派的古法根源。

使用農曆新年查找表搭配 pyswisseph 朔望月計算確定農曆月份。
"""

import math

import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

# ============================================================
# 常量 (Constants)
# ============================================================

EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

LUNAR_MONTH_NAMES = [
    "正月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "十一月", "十二月",
]

HOUR_BRANCH_NAMES = [
    "子時(23-01)", "丑時(01-03)", "寅時(03-05)", "卯時(05-07)",
    "辰時(07-09)", "巳時(09-11)", "午時(11-13)", "未時(13-15)",
    "申時(15-17)", "酉時(17-19)", "戌時(19-21)", "亥時(21-23)",
]

# 五行局
WU_XING_JU_NAMES = {2: "水二局", 3: "木三局", 4: "金四局", 5: "土五局", 6: "火六局"}

# 十二宮位名稱（從命宮起，逆時針地支方向排列）
PALACE_SEQUENCE = [
    "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
    "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮",
]

# ============================================================
# 策天十八飛星 (Ce Tian 18 Flying Stars)
# ============================================================
# 十二正曜 (indices 0-11) + 七副曜 (indices 12-18)
# (序號, 拼音, 中文, English)
CETIAN_18_FLYING_STARS = [
    ("0",  "ZiWei",     "紫微",   "Purple Micro"),
    ("1",  "TianXu",    "天虛",   "Heavenly Void"),
    ("2",  "TianGui",   "天貴",   "Heavenly Noble"),
    ("3",  "TianYin",   "天印",   "Heavenly Seal"),
    ("4",  "TianShou",  "天壽",   "Heavenly Longevity"),
    ("5",  "TianKong",  "天空",   "Heavenly Sky"),
    ("6",  "HongLuan",  "紅鸞",   "Red Phoenix"),
    ("7",  "TianKu2",   "天庫",   "Heavenly Storehouse"),  # 天庫（與天哭 TianKu 不同）
    ("8",  "TianGuan",  "天貫",   "Heavenly Official"),
    ("9",  "WenChang",  "文昌",   "Literary Prosperity"),
    ("10", "TianFu",    "天福",   "Heavenly Blessing"),
    ("11", "TianLu",    "天祿",   "Heavenly Prosperity"),
    # 七副曜
    ("12", "TianZhang", "天杖",   "Heavenly Staff"),
    ("13", "TianYi",    "天異",   "Heavenly Anomaly"),
    ("14", "MaoTou",    "旄頭",   "Mao Head / Banner"),
    ("15", "TianRen",   "天刃",   "Heavenly Blade"),
    ("16", "TianXing",  "天刑",   "Heavenly Punishment"),
    ("17", "TianYao",   "天姚",   "Heavenly Peach Blossom"),
    ("18", "TianKu",    "天哭",   "Heavenly Crying"),
]

# 正曜名稱列表
CETIAN_MAIN_STAR_NAMES = [s[2] for s in CETIAN_18_FLYING_STARS[:12]]
# 副曜名稱列表
CETIAN_AUX_STAR_NAMES = [s[2] for s in CETIAN_18_FLYING_STARS[12:]]

# ============================================================
# 納音五行局 (Nayin Wu Xing Ju)
# ============================================================
NAYIN_WUXING_JU = [
    4, 6, 3, 5, 4,
    6, 2, 5, 4, 3,
    2, 5, 6, 3, 2,
    4, 6, 3, 5, 4,
    6, 2, 5, 4, 3,
    2, 5, 6, 3, 2,
]

# ============================================================
# 策天飛星安星規則 (Ce Tian Star Placement Rules)
# ============================================================
# 紫微星安法與標準紫微相同（由五行局與農曆日決定）
# 其餘十七星由紫微星位置推算

# 正曜相對於紫微星的偏移（類似標準紫微系偏移）
CETIAN_MAIN_OFFSETS = {
    "紫微":  0,
    "天虛":  1,   # +1
    "天貴":  2,   # +2
    "天印":  3,   # +3
    "天壽":  4,   # +4
    "天空":  5,   # +5
    "紅鸞":  6,   # +6
    "天庫":  7,   # +7
    "天貫":  8,   # +8
    "文昌":  9,   # +9
    "天福": 10,   # +10
    "天祿": 11,   # +11
}

# 七副曜安星規則（由年支、月、時辰決定）
# 天杖: 以年支起子順行
# 天異: 以年支起丑逆行
# 旄頭: 以月數起寅順行
# 天刃: 以時辰起卯逆行
# 天刑: 以月數起酉順行
# 天姚: 以月數起丑順行
# 天哭: 以年支起午順行

# ============================================================
# 策天飛化規則 (Ce Tian Flying Transformation Rules)
# ============================================================
# 策天派四化表（年干決定，古法四化與標準紫微有所不同）
CETIAN_SIHUA_TABLE = [
    ("紫微", "天貴", "文昌", "天虛"),   # 甲
    ("天福", "天印", "紫微", "天壽"),   # 乙
    ("天祿", "天貫", "文昌", "天空"),   # 丙
    ("紅鸞", "天祿", "天貫", "天庫"),   # 丁
    ("天貴", "紅鸞", "天印", "天虛"),   # 戊
    ("文昌", "天貴", "天壽", "天刑"),   # 己
    ("天壽", "文昌", "天福", "天祿"),   # 庚
    ("天庫", "天壽", "天刑", "文昌"),   # 辛
    ("天印", "紫微", "天祿", "天貫"),   # 壬
    ("天空", "天庫", "紅鸞", "天貴"),   # 癸
]

# ============================================================
# 策天飛星飛化規則 (Flying Star Flight Rules)
# ============================================================
# 每顆星的飛化目標宮偏移（星飛入他宮的影響）
CETIAN_FLYING_RULES = {
    "紫微": {"fly_to_offset": 6,  "nature": "帝星飛化，主權貴變動"},
    "天虛": {"fly_to_offset": 4,  "nature": "虛星飛化，主虛驚空想"},
    "天貴": {"fly_to_offset": 8,  "nature": "貴星飛化，主貴人助力"},
    "天印": {"fly_to_offset": 3,  "nature": "印星飛化，主文書印信"},
    "天壽": {"fly_to_offset": 9,  "nature": "壽星飛化，主壽元福澤"},
    "天空": {"fly_to_offset": 7,  "nature": "空星飛化，主落空虛耗"},
    "紅鸞": {"fly_to_offset": 2,  "nature": "鸞星飛化，主婚姻喜慶"},
    "天庫": {"fly_to_offset": 10, "nature": "庫星飛化，主財庫聚散"},
    "天貫": {"fly_to_offset": 5,  "nature": "貫星飛化，主官運仕途"},
    "文昌": {"fly_to_offset": 1,  "nature": "昌星飛化，主文學才華"},
    "天福": {"fly_to_offset": 11, "nature": "福星飛化，主福德享受"},
    "天祿": {"fly_to_offset": 8,  "nature": "祿星飛化，主祿位進退"},
    "天杖": {"fly_to_offset": 3,  "nature": "杖星飛化，主權杖威嚴"},
    "天異": {"fly_to_offset": 6,  "nature": "異星飛化，主異變奇遇"},
    "旄頭": {"fly_to_offset": 9,  "nature": "旄星飛化，主旗鼓先鋒"},
    "天刃": {"fly_to_offset": 7,  "nature": "刃星飛化，主刀兵刑傷"},
    "天刑": {"fly_to_offset": 4,  "nature": "刑星飛化，主刑罰訴訟"},
    "天姚": {"fly_to_offset": 2,  "nature": "姚星飛化，主桃花風流"},
    "天哭": {"fly_to_offset": 10, "nature": "哭星飛化，主哭泣喪服"},
}

# ============================================================
# 節氣影響 (Solar Term Influence on Star Positions)
# ============================================================
# 24 節氣名稱與對應黃經度數
CETIAN_SOLAR_TERMS = {
    "立春": (315.0, "春始，紫微星得令"),
    "雨水": (330.0, "水潤，天壽星增輝"),
    "驚蟄": (345.0, "雷動，天刑星活躍"),
    "春分": (0.0,   "晝夜均，諸星平衡"),
    "清明": (15.0,  "天清，文昌星得力"),
    "穀雨": (30.0,  "雨生，天福星蔭庇"),
    "立夏": (45.0,  "夏始，紅鸞星當旺"),
    "小滿": (60.0,  "陽盛，天貫星通達"),
    "芒種": (75.0,  "種收，天祿星聚財"),
    "夏至": (90.0,  "陽極，天貴星顯達"),
    "小暑": (105.0, "暑起，天姚星躁動"),
    "大暑": (120.0, "暑盛，天空星虛耗"),
    "立秋": (135.0, "秋始，天庫星收藏"),
    "處暑": (150.0, "暑退，天印星安穩"),
    "白露": (165.0, "露凝，天虛星清冷"),
    "秋分": (180.0, "晝夜均，諸星平衡"),
    "寒露": (195.0, "寒起，天哭星感傷"),
    "霜降": (210.0, "霜至，天刃星肅殺"),
    "立冬": (225.0, "冬始，天異星潛藏"),
    "小雪": (240.0, "雪初，天杖星沉穩"),
    "大雪": (255.0, "雪盛，天壽星寧靜"),
    "冬至": (270.0, "陰極，紫微星轉運"),
    "小寒": (285.0, "寒甚，旄頭星堅守"),
    "大寒": (300.0, "極寒，天空星蟄伏"),
}

# ============================================================
# 古法格局 (Ce Tian Classical Patterns)
# ============================================================
CETIAN_PATTERNS = {
    "刑刃合會": {
        "stars": ["天刑", "天刃"],
        "condition": "同宮或對宮",
        "meaning": "主刑傷血光，宜慎防意外",
        "meaning_en": "Blade & Punishment together: risk of injury or legal trouble",
    },
    "哭姚交會": {
        "stars": ["天哭", "天姚"],
        "condition": "同宮或三合",
        "meaning": "主感情波折，喜中帶悲",
        "meaning_en": "Crying & Peach Blossom: emotional turbulence",
    },
    "紫貴同宮": {
        "stars": ["紫微", "天貴"],
        "condition": "同宮",
        "meaning": "帝座逢貴，大吉大利，權貴雙全",
        "meaning_en": "Emperor meets Noble: great fortune and authority",
    },
    "祿福相照": {
        "stars": ["天祿", "天福"],
        "condition": "對宮或三合",
        "meaning": "祿逢福德，衣食無憂，一生順遂",
        "meaning_en": "Prosperity meets Blessing: lifelong comfort",
    },
    "空虛對照": {
        "stars": ["天空", "天虛"],
        "condition": "同宮或對宮",
        "meaning": "虛空交會，多幻想而少實際",
        "meaning_en": "Void meets Empty: fantasy over reality",
    },
    "鸞印會合": {
        "stars": ["紅鸞", "天印"],
        "condition": "同宮或三合",
        "meaning": "婚姻有官印護持，佳偶天成",
        "meaning_en": "Phoenix & Seal: blessed marriage with authority backing",
    },
    "刑哭夾命": {
        "stars": ["天刑", "天哭"],
        "condition": "夾命宮",
        "meaning": "命宮受夾，幼年多災，宜行善積德",
        "meaning_en": "Punishment & Crying flanking Life: childhood hardship",
    },
    "昌貫文華": {
        "stars": ["文昌", "天貫"],
        "condition": "同宮",
        "meaning": "文昌逢官，科甲連登，文采斐然",
        "meaning_en": "Literary star meets Official: academic excellence",
    },
}

# ============================================================
# 星曜屬性 (Ce Tian Star Attributes)
# ============================================================
CETIAN_STAR_ATTRIBUTES = {
    "紫微": ("土", "帝星",   "#C62828"),
    "天虛": ("水", "虛星",   "#78909C"),
    "天貴": ("土", "貴星",   "#FFD700"),
    "天印": ("木", "印星",   "#2E7D32"),
    "天壽": ("土", "壽星",   "#8D6E63"),
    "天空": ("火", "空星",   "#90A4AE"),
    "紅鸞": ("水", "鸞星",   "#E91E63"),
    "天庫": ("金", "庫星",   "#F9A825"),
    "天貫": ("木", "官星",   "#1565C0"),
    "文昌": ("金", "文星",   "#7B1FA2"),
    "天福": ("水", "福星",   "#00897B"),
    "天祿": ("土", "祿星",   "#4CAF50"),
    "天杖": ("木", "杖星",   "#6D4C41"),
    "天異": ("火", "異星",   "#FF5722"),
    "旄頭": ("金", "旄星",   "#FF9800"),
    "天刃": ("金", "刃星",   "#D32F2F"),
    "天刑": ("火", "刑星",   "#B71C1C"),
    "天姚": ("水", "姚星",   "#E040FB"),
    "天哭": ("水", "哭星",   "#546E7A"),
}

# 星曜亮度表（策天十八飛星簡化版）
# 亮度等級: 廟=6, 旺=5, 得=4, 利=3, 平=2, 不=1, 陷=0
CETIAN_BRIGHTNESS_TABLE = {
    "紫微": [5, 6, 1, 4, 1, 6, 5, 5, 5, 2, 6, 4],
    "天虛": [2, 1, 4, 5, 3, 2, 4, 6, 5, 3, 1, 2],
    "天貴": [6, 5, 3, 2, 5, 6, 4, 3, 6, 5, 2, 4],
    "天印": [4, 6, 5, 6, 2, 1, 4, 6, 5, 6, 2, 1],
    "天壽": [5, 4, 6, 3, 5, 4, 6, 3, 5, 4, 6, 3],
    "天空": [1, 2, 3, 4, 2, 1, 3, 4, 2, 1, 3, 4],
    "紅鸞": [6, 5, 4, 6, 5, 4, 6, 5, 4, 6, 5, 4],
    "天庫": [5, 6, 4, 3, 6, 5, 4, 3, 6, 5, 4, 3],
    "天貫": [4, 5, 6, 2, 4, 5, 6, 2, 4, 5, 6, 2],
    "文昌": [4, 6, 5, 2, 4, 6, 4, 0, 4, 6, 5, 4],
    "天福": [6, 4, 5, 3, 6, 4, 5, 3, 6, 4, 5, 3],
    "天祿": [5, 3, 6, 4, 5, 3, 6, 4, 5, 3, 6, 4],
}
CETIAN_BRIGHTNESS_LABELS = {6: "廟", 5: "旺", 4: "得", 3: "利", 2: "平", 1: "不", 0: "陷"}

# 農曆新年公曆日期查找表 1900–2050（月, 日）
_CHINESE_NEW_YEAR: dict[int, tuple[int, int]] = {
    1900: (1, 31), 1901: (2, 19), 1902: (2,  8), 1903: (1, 29), 1904: (2, 16),
    1905: (2,  4), 1906: (1, 25), 1907: (2, 13), 1908: (2,  2), 1909: (1, 22),
    1910: (2, 10), 1911: (1, 30), 1912: (2, 18), 1913: (2,  6), 1914: (1, 26),
    1915: (2, 14), 1916: (2,  3), 1917: (1, 23), 1918: (2, 11), 1919: (2,  1),
    1920: (2, 20), 1921: (2,  8), 1922: (1, 28), 1923: (2, 16), 1924: (2,  5),
    1925: (1, 25), 1926: (2, 13), 1927: (2,  2), 1928: (1, 23), 1929: (2, 10),
    1930: (1, 30), 1931: (2, 17), 1932: (2,  6), 1933: (1, 26), 1934: (2, 14),
    1935: (2,  4), 1936: (1, 24), 1937: (2, 11), 1938: (1, 31), 1939: (2, 19),
    1940: (2,  8), 1941: (1, 27), 1942: (2, 15), 1943: (2,  5), 1944: (1, 25),
    1945: (2, 13), 1946: (2,  2), 1947: (1, 22), 1948: (2, 10), 1949: (1, 29),
    1950: (2, 17), 1951: (2,  6), 1952: (1, 27), 1953: (2, 14), 1954: (2,  3),
    1955: (1, 24), 1956: (2, 12), 1957: (1, 31), 1958: (2, 18), 1959: (2,  8),
    1960: (1, 28), 1961: (2, 15), 1962: (2,  5), 1963: (1, 25), 1964: (2, 13),
    1965: (2,  2), 1966: (1, 21), 1967: (2,  9), 1968: (1, 30), 1969: (2, 17),
    1970: (2,  6), 1971: (1, 27), 1972: (2, 15), 1973: (2,  3), 1974: (1, 23),
    1975: (2, 11), 1976: (1, 31), 1977: (2, 18), 1978: (2,  7), 1979: (1, 28),
    1980: (2, 16), 1981: (2,  5), 1982: (1, 25), 1983: (2, 13), 1984: (2,  2),
    1985: (2, 20), 1986: (2,  9), 1987: (1, 29), 1988: (2, 17), 1989: (2,  6),
    1990: (1, 27), 1991: (2, 15), 1992: (2,  4), 1993: (1, 23), 1994: (2, 10),
    1995: (1, 31), 1996: (2, 19), 1997: (2,  7), 1998: (1, 28), 1999: (2, 16),
    2000: (2,  5), 2001: (1, 24), 2002: (2, 12), 2003: (2,  1), 2004: (1, 22),
    2005: (2,  9), 2006: (1, 29), 2007: (2, 18), 2008: (2,  7), 2009: (1, 26),
    2010: (2, 14), 2011: (2,  3), 2012: (1, 23), 2013: (2, 10), 2014: (1, 31),
    2015: (2, 19), 2016: (2,  8), 2017: (1, 28), 2018: (2, 16), 2019: (2,  5),
    2020: (1, 25), 2021: (2, 12), 2022: (2,  1), 2023: (1, 22), 2024: (2, 10),
    2025: (1, 29), 2026: (2, 17), 2027: (2,  6), 2028: (1, 26), 2029: (2, 13),
    2030: (2,  3), 2031: (1, 23), 2032: (2, 11), 2033: (1, 31), 2034: (2, 19),
    2035: (2,  8), 2036: (1, 28), 2037: (2, 15), 2038: (2,  4), 2039: (1, 24),
    2040: (2, 12), 2041: (2,  1), 2042: (1, 22), 2043: (2, 10), 2044: (1, 30),
    2045: (2, 17), 2046: (2,  6), 2047: (1, 26), 2048: (2, 14), 2049: (2,  2),
    2050: (1, 23),
}

_SYNODIC_MONTH = 29.5305891
_CST_OFFSET = 8.0 / 24.0

# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class CetianPalace:
    """策天十八飛星宮位資料"""
    index: int                      # 宮位序號 0-11（從命宮算起）
    name: str                       # 宮位名稱
    branch: int                     # 地支索引 0-11（子=0）
    branch_name: str                # 地支名稱
    stem: int                       # 天干索引 0-9
    stem_name: str                  # 天干名稱
    stars: list = field(default_factory=list)       # 正曜名稱
    aux_stars: list = field(default_factory=list)   # 副曜名稱
    brightness: dict = field(default_factory=dict)  # {星名: 亮度標籤}
    sihua: dict = field(default_factory=dict)       # {星名: 四化類型}
    da_xian: str = ""               # 大限年齡範圍 e.g. "3~12"
    da_xian_start: int = 0          # 大限起始年齡
    flying_stars: dict = field(default_factory=dict)  # 飛星資訊 {星名: 飛入宮位}
    patterns: list = field(default_factory=list)      # 古法格局名稱


@dataclass
class CetianChart:
    """策天十八飛星命盤資料"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    julian_day: float
    gender: str                    # "男" or "女"

    # 農曆資訊
    lunar_year: int
    lunar_month: int
    lunar_day: int
    is_leap_month: bool
    lunar_year_stem: int           # 天干索引
    lunar_year_branch: int         # 地支索引

    # 時辰
    hour_branch: int               # 0-11

    # 命盤關鍵資訊
    ming_gong_branch: int          # 命宮地支索引
    shen_gong_branch: int          # 身宮地支索引
    wu_xing_ju: int                # 五行局（2-6）
    ziwei_branch: int              # 紫微星地支索引
    yin_yang: str                  # "陰" or "陽"

    # 四化
    sihua: dict = field(default_factory=dict)  # {星名: 四化類型}

    # 宮位資料
    palaces: list = field(default_factory=list)  # List[CetianPalace]

    # 飛星總表
    star_flight: dict = field(default_factory=dict)  # {星名: {from_branch, to_branch, nature}}

    # 節氣影響
    solar_term_influence: str = ""

    # 三合組
    sanhe_groups: list = field(default_factory=list)

    # 格局
    active_patterns: list = field(default_factory=list)


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _normalize(deg: float) -> float:
    return deg % 360.0


def _get_hour_branch(hour: int, minute: int) -> int:
    """
    根據出生時間取得時辰地支索引（子=0, 丑=1, ..., 亥=11）。
    子時跨越午夜：23:00-01:00 為子時。
    """
    total_minutes = hour * 60 + minute
    if total_minutes < 60 or total_minutes >= 23 * 60:
        return 0
    return (total_minutes + 60) // 120


def _find_new_moon_near(jd_approx: float) -> float:
    """以迭代法找出最接近 jd_approx 的朔（新月）Julian Day。"""
    jd = jd_approx
    for _ in range(50):
        sun_lon = _normalize(swe.calc_ut(jd, swe.SUN)[0][0])
        moon_lon = _normalize(swe.calc_ut(jd, swe.MOON)[0][0])
        diff = moon_lon - sun_lon
        if diff > 180:
            diff -= 360.0
        elif diff < -180:
            diff += 360.0
        correction = diff / (360.0 / _SYNODIC_MONTH)
        jd -= correction
        if abs(diff) < 0.0001:
            break
    return jd


def _get_cny_jd(year: int) -> float:
    """取得農曆新年的 Julian Day。"""
    if year in _CHINESE_NEW_YEAR:
        m, d = _CHINESE_NEW_YEAR[year]
        return swe.julday(year, m, d, 12.0)
    if year < 1900:
        m, d = _CHINESE_NEW_YEAR[1900]
        base_jd = swe.julday(1900, m, d, 12.0)
        return base_jd - (1900 - year) * 365.2425
    m, d = _CHINESE_NEW_YEAR[2050]
    base_jd = swe.julday(2050, m, d, 12.0)
    return base_jd + (year - 2050) * 365.2425


def _solar_to_lunar(jd: float) -> tuple[int, int, int, bool]:
    """將 Julian Day 轉換為農曆日期。"""
    gd = swe.revjul(jd)
    gy = int(gd[0])
    cny_this = _get_cny_jd(gy)
    if jd < cny_this:
        lunar_year = gy - 1
        cny_jd = _get_cny_jd(gy - 1)
    else:
        lunar_year = gy
        cny_jd = cny_this

    nm_start = _find_new_moon_near(cny_jd)
    while nm_start > cny_jd + 1.0:
        nm_start = _find_new_moon_near(nm_start - _SYNODIC_MONTH)

    month = 0
    prev_nm = nm_start
    next_nm = _find_new_moon_near(nm_start + _SYNODIC_MONTH)
    is_leap = False

    for m in range(14):
        if next_nm > jd:
            month = m + 1
            break
        prev_nm = next_nm
        next_nm = _find_new_moon_near(prev_nm + _SYNODIC_MONTH)
    else:
        month = 1

    nm_cal_day = math.floor(prev_nm + _CST_OFFSET + 0.5)
    jd_cal_day = math.floor(jd + _CST_OFFSET + 0.5)
    lunar_day = jd_cal_day - nm_cal_day + 1
    lunar_day = max(1, min(lunar_day, 30))

    if month > 12:
        is_leap = True
        month = month - 12

    return lunar_year, month, lunar_day, is_leap


def _get_year_stem(lunar_year: int) -> int:
    return (lunar_year - 4) % 10


def _get_year_branch(lunar_year: int) -> int:
    return (lunar_year - 4) % 12


def _get_ming_gong_branch(lunar_month: int, hour_branch: int) -> int:
    return (1 + lunar_month - hour_branch) % 12


def _get_shen_gong_branch(lunar_month: int, hour_branch: int) -> int:
    return (1 + lunar_month + hour_branch) % 12


def _get_ming_gong_stem(year_stem: int, ming_gong_branch: int) -> int:
    yin_stem = (2 * (year_stem % 5) + 2) % 10
    steps = (ming_gong_branch - 2 + 12) % 12
    return (yin_stem + steps) % 10


def _get_wu_xing_ju(ming_gong_stem: int, ming_gong_branch: int) -> int:
    sexagenary = (6 * ming_gong_stem - 5 * ming_gong_branch) % 60
    pair_idx = sexagenary // 2
    return NAYIN_WUXING_JU[pair_idx]


def _get_ziwei_branch(lunar_day: int, wu_xing_ju: int) -> int:
    """由農曆生日與五行局計算紫微星所在地支索引。"""
    n = wu_xing_ju
    q, r = divmod(lunar_day, n)
    if r == 0:
        return q % 12
    return (q + 3 - r) % 12


def _get_solar_term(jd: float) -> str:
    """計算出生時刻所處的節氣。"""
    sun_lon = _normalize(swe.calc_ut(jd, swe.SUN)[0][0])
    closest_term = ""
    min_diff = 999.0
    for term_name, (term_lon, _) in CETIAN_SOLAR_TERMS.items():
        diff = abs(sun_lon - term_lon)
        if diff > 180:
            diff = 360 - diff
        if diff < min_diff:
            min_diff = diff
            closest_term = term_name
    return closest_term


# ============================================================
# 安星函數 (Star Placement)
# ============================================================

def _place_cetian_main_stars(ziwei_branch: int) -> dict[int, list[str]]:
    """
    計算策天十二正曜的地支索引。
    所有正曜由紫微星位置順時針依次排列（每宮一顆）。
    """
    stars: dict[int, list[str]] = {i: [] for i in range(12)}
    for name, offset in CETIAN_MAIN_OFFSETS.items():
        b = (ziwei_branch + offset) % 12
        stars[b].append(name)
    return stars


def _place_cetian_aux_stars(
    year_branch: int, lunar_month: int, hour_branch: int,
) -> dict[int, list[str]]:
    """
    計算策天七副曜的地支索引。
    """
    aux: dict[int, list[str]] = {i: [] for i in range(12)}

    # 天杖: 以年支起子順行
    tian_zhang = (0 + year_branch) % 12
    aux[tian_zhang].append("天杖")

    # 天異: 以年支起丑逆行
    tian_yi = (1 - year_branch + 12) % 12
    aux[tian_yi].append("天異")

    # 旄頭: 以月數起寅順行
    mao_tou = (1 + lunar_month) % 12
    aux[mao_tou].append("旄頭")

    # 天刃: 以時辰起卯逆行
    tian_ren = (3 - hour_branch + 12) % 12
    aux[tian_ren].append("天刃")

    # 天刑: 以月數起酉順行
    tian_xing = (9 + lunar_month) % 12
    aux[tian_xing].append("天刑")

    # 天姚: 以月數起丑順行
    tian_yao = (1 + lunar_month) % 12
    aux[tian_yao].append("天姚")

    # 天哭: 以年支起午順行
    tian_ku = (6 + year_branch) % 12
    aux[tian_ku].append("天哭")

    return aux


def _compute_cetian_sihua(year_stem: int) -> dict[str, str]:
    """計算策天四化（年干決定）。"""
    lu, quan, ke, ji = CETIAN_SIHUA_TABLE[year_stem]
    return {lu: "祿", quan: "權", ke: "科", ji: "忌"}


def _compute_sanhe_groups(ming_gong_branch: int) -> list[tuple[int, int, int]]:
    """計算三合組。"""
    groups = []
    for start in range(4):
        group = tuple((start + i * 4) % 12 for i in range(3))
        groups.append(group)
    return groups


def _compute_star_flights(
    stars_by_branch: dict[int, list[str]],
    aux_by_branch: dict[int, list[str]],
) -> dict[str, dict]:
    """
    計算所有飛星的飛化路線。
    Returns {star_name: {from_branch, to_branch, nature}}
    """
    flights = {}
    for branch_idx in range(12):
        all_stars = stars_by_branch.get(branch_idx, []) + aux_by_branch.get(branch_idx, [])
        for star in all_stars:
            rule = CETIAN_FLYING_RULES.get(star)
            if rule:
                to_branch = (branch_idx + rule["fly_to_offset"]) % 12
                flights[star] = {
                    "from_branch": branch_idx,
                    "to_branch": to_branch,
                    "nature": rule["nature"],
                }
    return flights


def _detect_patterns(
    stars_by_branch: dict[int, list[str]],
    aux_by_branch: dict[int, list[str]],
    ming_gong_branch: int,
) -> list[dict]:
    """
    檢測古法格局。
    Returns list of {name, stars, meaning}
    """
    active = []
    # 合併所有星曜到宮位
    all_by_branch: dict[int, list[str]] = {i: [] for i in range(12)}
    for b in range(12):
        all_by_branch[b] = stars_by_branch.get(b, []) + aux_by_branch.get(b, [])

    for pattern_name, pattern_info in CETIAN_PATTERNS.items():
        required_stars = pattern_info["stars"]
        condition = pattern_info["condition"]

        if "同宮" in condition:
            for b in range(12):
                if all(s in all_by_branch[b] for s in required_stars):
                    active.append({
                        "name": pattern_name,
                        "stars": required_stars,
                        "meaning": pattern_info["meaning"],
                        "palace_branch": b,
                    })
                    break

        if "對宮" in condition and not any(p["name"] == pattern_name for p in active):
            for b in range(12):
                opp = (b + 6) % 12
                stars_here = all_by_branch[b]
                stars_opp = all_by_branch[opp]
                all_combined = stars_here + stars_opp
                if all(s in all_combined for s in required_stars):
                    if not all(s in stars_here for s in required_stars):
                        active.append({
                            "name": pattern_name,
                            "stars": required_stars,
                            "meaning": pattern_info["meaning"],
                            "palace_branch": b,
                        })
                        break

        if "夾命" in condition:
            left = (ming_gong_branch - 1 + 12) % 12
            right = (ming_gong_branch + 1) % 12
            flank_stars = all_by_branch[left] + all_by_branch[right]
            if all(s in flank_stars for s in required_stars):
                active.append({
                    "name": pattern_name,
                    "stars": required_stars,
                    "meaning": pattern_info["meaning"],
                    "palace_branch": ming_gong_branch,
                })

    return active


def _compute_cetian_feixing(palace_stem: int) -> dict[str, str]:
    """計算飛星四化（由宮位天干決定，使用策天四化表）。"""
    lu, quan, ke, ji = CETIAN_SIHUA_TABLE[palace_stem]
    return {lu: "祿", quan: "權", ke: "科", ji: "忌"}


def _build_cetian_palaces(
    ming_gong_branch: int,
    year_stem: int,
    stars_by_branch: dict[int, list[str]],
    aux_by_branch: dict[int, list[str]],
    sihua: dict[str, str],
    wu_xing_ju: int,
    is_yang_male_or_yin_female: bool,
    star_flights: dict[str, dict],
    active_patterns: list[dict],
) -> list[CetianPalace]:
    """建立十二宮位資料。"""
    yin_stem = (2 * (year_stem % 5) + 2) % 10

    palaces = []
    for idx in range(12):
        branch = (ming_gong_branch - idx + 12) % 12
        palace_name = PALACE_SEQUENCE[idx]
        steps = (branch - 2 + 12) % 12
        stem = (yin_stem + steps) % 10

        # 星曜亮度
        brightness = {}
        all_stars = stars_by_branch.get(branch, []) + aux_by_branch.get(branch, [])
        for star in all_stars:
            if star in CETIAN_BRIGHTNESS_TABLE:
                level = CETIAN_BRIGHTNESS_TABLE[star][branch]
                brightness[star] = CETIAN_BRIGHTNESS_LABELS.get(level, "")

        # 宮位四化
        palace_sihua = {}
        for star in all_stars:
            if star in sihua:
                palace_sihua[star] = sihua[star]

        # 大限
        if is_yang_male_or_yin_female:
            da_xian_num = (12 - idx) % 12 if idx > 0 else 0
        else:
            da_xian_num = idx
        da_xian_start = wu_xing_ju + da_xian_num * 10
        da_xian_end = da_xian_start + 9
        da_xian = f"{da_xian_start}~{da_xian_end}"

        # 飛星資訊
        palace_flights = {}
        for star in all_stars:
            if star in star_flights:
                flight = star_flights[star]
                palace_flights[star] = EARTHLY_BRANCHES[flight["to_branch"]]

        # 格局
        palace_patterns = [
            p["name"] for p in active_patterns
            if p.get("palace_branch") == branch
        ]

        palaces.append(CetianPalace(
            index=idx,
            name=palace_name,
            branch=branch,
            branch_name=EARTHLY_BRANCHES[branch],
            stem=stem,
            stem_name=HEAVENLY_STEMS[stem],
            stars=list(stars_by_branch.get(branch, [])),
            aux_stars=list(aux_by_branch.get(branch, [])),
            brightness=brightness,
            sihua=palace_sihua,
            da_xian=da_xian,
            da_xian_start=da_xian_start,
            flying_stars=palace_flights,
            patterns=palace_patterns,
        ))
    return palaces


# ============================================================
# 計算函數 (Computation)
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_cetian_ziwei_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    gender: str = "男",
) -> CetianChart:
    """
    計算策天十八飛星紫微斗數命盤。

    Parameters:
        year, month, day: 公曆出生日期
        hour, minute:     出生時間（24 小時制）
        timezone:         時區偏移（UTC+N）
        latitude:         緯度
        longitude:        經度
        location_name:    地點名稱
        gender:           性別（"男" or "女"）

    Returns:
        CetianChart: 策天飛星命盤資料
    """
    swe.set_ephe_path("")

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    # 農曆轉換
    lunar_year, lunar_month, lunar_day, is_leap = _solar_to_lunar(jd)

    # 時辰地支
    hour_branch = _get_hour_branch(hour, minute)

    # 農曆年天干地支
    year_stem = _get_year_stem(lunar_year)
    year_branch = _get_year_branch(lunar_year)

    # 命宮 / 身宮
    ming_gong_branch = _get_ming_gong_branch(lunar_month, hour_branch)
    shen_gong_branch = _get_shen_gong_branch(lunar_month, hour_branch)

    # 五行局
    mg_stem = _get_ming_gong_stem(year_stem, ming_gong_branch)
    wu_xing_ju = _get_wu_xing_ju(mg_stem, ming_gong_branch)

    # 紫微星位置
    ziwei_branch = _get_ziwei_branch(lunar_day, wu_xing_ju)

    # 安十二正曜
    stars_by_branch = _place_cetian_main_stars(ziwei_branch)

    # 安七副曜
    aux_by_branch = _place_cetian_aux_stars(year_branch, lunar_month, hour_branch)

    # 陰陽判斷
    yin_yang = "陽" if year_stem % 2 == 0 else "陰"
    is_yang_male_or_yin_female = (
        (yin_yang == "陽" and gender == "男") or
        (yin_yang == "陰" and gender == "女")
    )

    # 四化
    sihua = _compute_cetian_sihua(year_stem)

    # 飛星
    star_flights = _compute_star_flights(stars_by_branch, aux_by_branch)

    # 格局
    active_patterns = _detect_patterns(stars_by_branch, aux_by_branch, ming_gong_branch)

    # 節氣
    solar_term = _get_solar_term(jd)
    term_info = CETIAN_SOLAR_TERMS.get(solar_term, (0, ""))
    solar_term_influence = f"{solar_term}：{term_info[1]}"

    # 三合組
    sanhe_groups = _compute_sanhe_groups(ming_gong_branch)

    # 建立宮位
    palaces = _build_cetian_palaces(
        ming_gong_branch, year_stem, stars_by_branch, aux_by_branch,
        sihua, wu_xing_ju, is_yang_male_or_yin_female,
        star_flights, active_patterns,
    )

    return CetianChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd,
        gender=gender,
        lunar_year=lunar_year, lunar_month=lunar_month, lunar_day=lunar_day,
        is_leap_month=is_leap,
        lunar_year_stem=year_stem, lunar_year_branch=year_branch,
        hour_branch=hour_branch,
        ming_gong_branch=ming_gong_branch, shen_gong_branch=shen_gong_branch,
        wu_xing_ju=wu_xing_ju, ziwei_branch=ziwei_branch,
        yin_yang=yin_yang,
        sihua=sihua, palaces=palaces,
        star_flight=star_flights,
        solar_term_influence=solar_term_influence,
        sanhe_groups=sanhe_groups,
        active_patterns=active_patterns,
    )


# ============================================================
# 渲染函數 (Rendering)
# ============================================================

def render_cetian_ziwei_chart(chart: CetianChart, after_chart_hook=None) -> None:
    """渲染完整的策天十八飛星命盤。"""
    st.subheader("🌠 策天十八飛星紫微斗數命盤")
    _render_sihua_legend()
    _render_palace_grid(chart)
    if after_chart_hook:
        after_chart_hook()
    st.divider()
    _render_info(chart)
    st.divider()
    _render_star_table(chart)
    st.divider()
    _render_flying_star_table(chart)
    st.divider()
    _render_feixing_table(chart)
    st.divider()
    _render_patterns(chart)
    st.divider()
    _render_palace_details(chart)


def _render_info(chart: CetianChart) -> None:
    """渲染基本排盤資訊卡片。"""
    leap_str = "（閏月）" if chart.is_leap_month else ""
    lunar_date = (
        f"{chart.lunar_year}年"
        f"（{HEAVENLY_STEMS[chart.lunar_year_stem]}{EARTHLY_BRANCHES[chart.lunar_year_branch]}年）"
        f" {LUNAR_MONTH_NAMES[chart.lunar_month - 1]}{leap_str}"
        f" 初{_day_to_chinese(chart.lunar_day)}"
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**公曆:** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**時間:** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**時區:** UTC{chart.timezone:+.1f}")
        st.write(f"**性別:** {chart.gender}命 ({chart.yin_yang})")
    with col2:
        st.write(f"**農曆:** {lunar_date}")
        st.write(f"**時辰:** {HOUR_BRANCH_NAMES[chart.hour_branch]}")
        st.write(f"**地點:** {chart.location_name}")
    with col3:
        wu_ju_name = WU_XING_JU_NAMES[chart.wu_xing_ju]
        st.write(f"**命宮:** {EARTHLY_BRANCHES[chart.ming_gong_branch]}宮")
        st.write(f"**身宮:** {EARTHLY_BRANCHES[chart.shen_gong_branch]}宮")
        st.write(f"**五行局:** {wu_ju_name}")

    # 四化資訊
    sihua_str = "　".join(
        f"{star}化{hua}" for star, hua in chart.sihua.items()
    )
    st.info(f"**四化:** {sihua_str}")

    # 節氣影響
    if chart.solar_term_influence:
        st.success(f"**節氣:** {chart.solar_term_influence}")


def _day_to_chinese(day: int) -> str:
    """將農曆日數字轉為中文。"""
    units = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
    if day <= 10:
        return units[day]
    if day < 20:
        return f"十{units[day - 10]}"
    if day == 20:
        return "二十"
    if day < 30:
        return f"二十{units[day - 20]}"
    return "三十"


def _palace_cell_html(
    palace: CetianPalace, is_ming: bool, is_shen: bool
) -> str:
    """產生單一宮位的 HTML 卡片（用於 CSS Grid 命盤方格）。"""
    bg = "#1a1a2e"
    border_style = "border:1px solid #444;"
    if is_ming and is_shen:
        border_style = "border:3px solid #FFD700;"
        bg = "#2d1b00"
    elif is_ming:
        border_style = "border:3px solid #FF6B6B;"
        bg = "#2d0000"
    elif is_shen:
        border_style = "border:3px solid #4ECDC4;"
        bg = "#001a1a"

    label = ""
    if is_ming:
        label += '<span style="color:#FF6B6B;font-weight:bold;font-size:11px">【命】</span>'
    if is_shen:
        label += '<span style="color:#4ECDC4;font-weight:bold;font-size:11px">【身】</span>'

    SIHUA_COLORS = {"祿": "#00E676", "權": "#FF5252", "科": "#42A5F5", "忌": "#FF9800"}

    # 正曜 HTML
    stars_html = ""
    for star in palace.stars:
        attr = CETIAN_STAR_ATTRIBUTES.get(star, ("", "", "#aaa"))
        color = attr[2]
        bright = palace.brightness.get(star, "")
        bright_html = f'<span style="color:#aaa;font-size:9px">{bright}</span>' if bright else ""
        hua = palace.sihua.get(star, "")
        hua_html = ""
        if hua:
            hc = SIHUA_COLORS.get(hua, "#fff")
            hua_html = f'<span style="color:{hc};font-size:10px;font-weight:bold">化{hua}</span>'
        # 飛星箭頭
        fly_html = ""
        if star in palace.flying_stars:
            fly_html = f'<span style="color:#FFD700;font-size:9px">→{palace.flying_stars[star]}</span>'
        stars_html += (
            f'<div style="display:flex;align-items:center;gap:2px">'
            f'<span style="color:{color};font-size:13px;font-weight:bold">{star}</span>'
            f'{bright_html}{hua_html}{fly_html}</div>'
        )

    # 副曜 HTML
    aux_html = ""
    for star in palace.aux_stars:
        bright = palace.brightness.get(star, "")
        bright_str = f"({bright})" if bright else ""
        hua = palace.sihua.get(star, "")
        hua_str = ""
        if hua:
            hc = SIHUA_COLORS.get(hua, "#fff")
            hua_str = f'<span style="color:{hc};font-size:9px"> 化{hua}</span>'
        fly_html = ""
        if star in palace.flying_stars:
            fly_html = f'<span style="color:#FFD700;font-size:9px">→{palace.flying_stars[star]}</span>'
        aux_html += (
            f'<span style="color:#888;font-size:10px">{star}{bright_str}</span>{hua_str}{fly_html} '
        )

    if not stars_html and not aux_html:
        stars_html = '<div style="color:#666;font-size:11px">─</div>'

    # 格局標記
    pattern_html = ""
    if palace.patterns:
        for p in palace.patterns:
            pattern_html += f'<span style="color:#FFD700;font-size:8px;background:#333;padding:1px 3px;border-radius:3px;margin:1px">{p}</span>'

    return (
        f'<div style="background:{bg};padding:6px 5px;border-radius:6px;'
        f'min-height:130px;{border_style}">'
        f'<div style="display:flex;justify-content:space-between;align-items:center">'
        f'<span style="color:#c8a96e;font-size:10px">'
        f'{palace.stem_name}{palace.branch_name}</span>'
        f'{label}'
        f'<span style="color:#8B8000;font-size:9px">{palace.da_xian}</span>'
        f'</div>'
        f'<div style="color:#e0e0e0;font-size:11px;font-weight:bold;'
        f'border-bottom:1px solid #555;margin-bottom:3px;padding-bottom:1px">'
        f'{palace.name}</div>'
        f'{stars_html}'
        f'<div style="margin-top:3px;line-height:1.4">{aux_html}</div>'
        f'{pattern_html}'
        f'</div>'
    )


def _center_info_html(chart: CetianChart) -> str:
    """產生中宮資訊 HTML。"""
    wu_ju = WU_XING_JU_NAMES[chart.wu_xing_ju]
    leap = "（閏）" if chart.is_leap_month else ""
    lm = LUNAR_MONTH_NAMES[chart.lunar_month - 1]
    ld = f"初{_day_to_chinese(chart.lunar_day)}"
    ys = HEAVENLY_STEMS[chart.lunar_year_stem]
    yb = EARTHLY_BRANCHES[chart.lunar_year_branch]

    sihua_html = ""
    SIHUA_COLORS = {"祿": "#00E676", "權": "#FF5252", "科": "#42A5F5", "忌": "#FF9800"}
    for star, hua in chart.sihua.items():
        hc = SIHUA_COLORS.get(hua, "#fff")
        sihua_html += f'<span style="color:{hc};font-size:11px;margin:0 3px">{star}化{hua}</span>'

    solar_html = ""
    if chart.solar_term_influence:
        solar_html = (
            f'<div style="font-size:10px;color:#81C784;margin-top:3px">'
            f'🌿 {chart.solar_term_influence}</div>'
        )

    return (
        f'<div style="background:#0d0d1a;border:2px solid #c8a96e;border-radius:10px;'
        f'padding:12px;text-align:center;height:100%;color:#e0d5b0;'
        f'display:flex;flex-direction:column;justify-content:center;">'
        f'<div style="font-size:18px;font-weight:bold;color:#c8a96e;margin-bottom:4px">'
        f'策天十八飛星</div>'
        f'<div style="font-size:11px;color:#aaa;margin-bottom:4px">古法紫微斗數</div>'
        f'<div style="font-size:12px;margin:2px 0">'
        f'{chart.gender}命 / {chart.yin_yang}{chart.gender} / {wu_ju}</div>'
        f'<div style="font-size:12px;margin:2px 0">'
        f'{chart.lunar_year}年 {ys}{yb}年</div>'
        f'<div style="font-size:12px;margin:2px 0">'
        f'{lm}{leap} {ld} {HOUR_BRANCH_NAMES[chart.hour_branch]}</div>'
        f'<div style="font-size:11px;margin:4px 0;color:#FF6B6B">'
        f'命宮: {EARTHLY_BRANCHES[chart.ming_gong_branch]}宮 '
        f'<span style="color:#4ECDC4">身宮: {EARTHLY_BRANCHES[chart.shen_gong_branch]}宮</span>'
        f'</div>'
        f'<div style="margin-top:4px">{sihua_html}</div>'
        f'{solar_html}'
        f'<div style="font-size:10px;color:#888;margin-top:4px">'
        f'四化: <span style="color:#00E676">→祿</span>'
        f'<span style="color:#FF5252">→權</span>'
        f'<span style="color:#42A5F5">→科</span>'
        f'<span style="color:#FF9800">→忌</span></div>'
        f'</div>'
    )


def _render_palace_grid(chart: CetianChart) -> None:
    """渲染南式命盤方格（CSS Grid）。"""
    st.markdown("#### 🀄 策天十八飛星命盤方格")

    branch_to_palace: dict[int, CetianPalace] = {p.branch: p for p in chart.palaces}

    def cell(branch: int) -> str:
        p = branch_to_palace[branch]
        return _palace_cell_html(
            p,
            is_ming=(p.branch == chart.ming_gong_branch),
            is_shen=(p.branch == chart.shen_gong_branch),
        )

    grid_layout = [
        (1, 1, 5), (1, 2, 6), (1, 3, 7), (1, 4, 8),
        (2, 1, 4), (2, 4, 9),
        (3, 1, 3), (3, 4, 10),
        (4, 1, 2), (4, 2, 1), (4, 3, 0), (4, 4, 11),
    ]

    cells_html = ""
    for row, col, branch in grid_layout:
        cells_html += (
            f'<div style="grid-row:{row};grid-column:{col}">'
            f'{cell(branch)}</div>'
        )

    center_html = (
        f'<div style="grid-row:2/4;grid-column:2/4">'
        f'{_center_info_html(chart)}</div>'
    )

    full_html = (
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);'
        f'grid-template-rows:repeat(4,auto);gap:4px;'
        f'background:#111;padding:6px;border-radius:10px;'
        f'border:2px solid #c8a96e;">'
        f'{cells_html}'
        f'{center_html}'
        f'</div>'
    )

    st.markdown(full_html, unsafe_allow_html=True)


def _render_star_table(chart: CetianChart) -> None:
    """渲染十八飛星位置匯總表格。"""
    st.markdown("#### ⭐ 十八飛星分佈表")

    header = "| 星曜 | 五行 | 別稱 | 所在宮位 | 地支 | 亮度 | 四化 | 飛入 |"
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]

    all_star_names = CETIAN_MAIN_STAR_NAMES + CETIAN_AUX_STAR_NAMES
    for star in all_star_names:
        attr = CETIAN_STAR_ATTRIBUTES.get(star, ("", "", "#aaa"))
        wuxing, alias, color = attr
        palace = next(
            (p for p in chart.palaces if star in p.stars or star in p.aux_stars), None
        )
        if palace is None:
            continue
        is_ming = "【命】" if palace.branch == chart.ming_gong_branch else ""
        is_shen = "【身】" if palace.branch == chart.shen_gong_branch else ""
        marker = f"{is_ming}{is_shen}"
        name_html = f'<span style="color:{color};font-weight:bold">{star}</span>'
        bright = palace.brightness.get(star, "")
        hua = chart.sihua.get(star, "")
        hua_str = f"化{hua}" if hua else ""
        # 飛入宮位
        flight = chart.star_flight.get(star, {})
        fly_str = ""
        if flight:
            fly_str = f"→{EARTHLY_BRANCHES[flight['to_branch']]}"
        rows.append(
            f"| {name_html} | {wuxing} | {alias} "
            f"| {palace.name}{marker} "
            f"| {palace.branch_name} "
            f"| {bright} "
            f"| {hua_str} "
            f"| {fly_str} |"
        )

    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_sihua_legend() -> None:
    """渲染四化圖例說明。"""
    st.markdown(
        '<div style="text-align:center;padding:4px;font-size:12px">'
        '策天四化圖示: '
        '<span style="color:#00E676;font-weight:bold">●祿</span> '
        '<span style="color:#FF5252;font-weight:bold">●權</span> '
        '<span style="color:#42A5F5;font-weight:bold">●科</span> '
        '<span style="color:#FF9800;font-weight:bold">●忌</span>'
        '　<span style="color:#FFD700">→飛星箭頭</span>'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_flying_star_table(chart: CetianChart) -> None:
    """渲染飛星路線表。"""
    st.markdown("#### 🏹 飛星路線表")
    st.markdown("*各星曜由本宮飛入他宮的影響*")

    header = "| 星曜 | 本宮 | 飛入 | 飛化性質 |"
    sep = "|:---:|:---:|:---:|:---|"
    rows = [header, sep]

    for star_name, flight_info in chart.star_flight.items():
        from_b = EARTHLY_BRANCHES[flight_info["from_branch"]]
        to_b = EARTHLY_BRANCHES[flight_info["to_branch"]]
        nature = flight_info["nature"]
        attr = CETIAN_STAR_ATTRIBUTES.get(star_name, ("", "", "#aaa"))
        color = attr[2]
        name_html = f'<span style="color:{color};font-weight:bold">{star_name}</span>'
        rows.append(f"| {name_html} | {from_b}宮 | {to_b}宮 | {nature} |")

    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_feixing_table(chart: CetianChart) -> None:
    """渲染飛星四化表（各宮位天干的四化）。"""
    st.markdown("#### 🌠 宮干飛星四化表")
    st.markdown("*各宮位天干所引發的策天四化*")

    header = "| 宮位 | 天干 | 化祿 | 化權 | 化科 | 化忌 |"
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]

    SIHUA_COLORS = {"祿": "#00E676", "權": "#FF5252", "科": "#42A5F5", "忌": "#FF9800"}

    for palace in chart.palaces:
        lu_star = CETIAN_SIHUA_TABLE[palace.stem][0]
        quan_star = CETIAN_SIHUA_TABLE[palace.stem][1]
        ke_star = CETIAN_SIHUA_TABLE[palace.stem][2]
        ji_star = CETIAN_SIHUA_TABLE[palace.stem][3]
        rows.append(
            f"| {palace.name}({palace.branch_name}) | {palace.stem_name} "
            f'| <span style="color:{SIHUA_COLORS["祿"]}">{lu_star}</span> '
            f'| <span style="color:{SIHUA_COLORS["權"]}">{quan_star}</span> '
            f'| <span style="color:{SIHUA_COLORS["科"]}">{ke_star}</span> '
            f'| <span style="color:{SIHUA_COLORS["忌"]}">{ji_star}</span> |'
        )

    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_patterns(chart: CetianChart) -> None:
    """渲染古法格局檢測結果。"""
    st.markdown("#### 📜 古法格局")

    if not chart.active_patterns:
        st.info("此命盤未檢測到特殊古法格局。")
        return

    for pattern in chart.active_patterns:
        stars_str = "、".join(pattern["stars"])
        branch_name = EARTHLY_BRANCHES[pattern["palace_branch"]]
        st.markdown(
            f"**🔶 {pattern['name']}** — {stars_str} "
            f"（{branch_name}宮）\n\n"
            f"*{pattern['meaning']}*"
        )


def _render_palace_details(chart: CetianChart) -> None:
    """渲染十二宮位詳細說明。"""
    st.markdown("#### 📋 十二宮位詳情")

    _PALACE_DESC = {
        "命宮":  "代表人的個性、才能、命運走向",
        "兄弟宮": "兄弟姐妹、朋友關係",
        "夫妻宮": "婚姻、伴侶、感情",
        "子女宮": "子女、創造、學生",
        "財帛宮": "金錢、財富、財運",
        "疾厄宮": "健康、疾病、意外",
        "遷移宮": "旅行、遷徙、外出緣份",
        "交友宮": "朋友、同事、下屬",
        "官祿宮": "事業、工作、官運",
        "田宅宮": "房產、家庭、祖業",
        "福德宮": "福份、精神、享樂",
        "父母宮": "父母、長輩、文書",
    }

    # 三合組
    st.markdown("##### 🔺 三合")
    sanhe_names = {
        (0, 4, 8): "水局 (子辰申)",
        (1, 5, 9): "金局 (丑巳酉)",
        (2, 6, 10): "火局 (寅午戌)",
        (3, 7, 11): "木局 (卯未亥)",
    }
    branch_to_palace = {p.branch: p for p in chart.palaces}
    for group in chart.sanhe_groups:
        group_name = sanhe_names.get(group, "")
        palace_names = [
            branch_to_palace[b].name if b in branch_to_palace else EARTHLY_BRANCHES[b]
            for b in group
        ]
        st.write(f"**{group_name}:** {' ↔ '.join(palace_names)}")

    st.markdown("---")

    cols = st.columns(3)
    for i, palace in enumerate(chart.palaces):
        with cols[i % 3]:
            stars_str = "、".join(palace.stars) if palace.stars else "（空宮）"
            aux_str = "、".join(palace.aux_stars) if palace.aux_stars else ""
            markers = []
            if palace.branch == chart.ming_gong_branch:
                markers.append("🔴命")
            if palace.branch == chart.shen_gong_branch:
                markers.append("🔵身")
            marker_str = " ".join(markers)
            desc = _PALACE_DESC.get(palace.name, "")

            # 四化
            sihua_str = ""
            for star, hua in palace.sihua.items():
                sihua_str += f" {star}化{hua}"

            # 飛星
            fly_str = ""
            for star, target in palace.flying_stars.items():
                fly_str += f" {star}→{target}"

            # 格局
            pattern_str = ""
            if palace.patterns:
                pattern_str = "、".join(palace.patterns)

            st.markdown(
                f"**{palace.stem_name}{palace.branch_name} {palace.name}** "
                f"{marker_str} 大限:{palace.da_xian}\n\n"
                f"⭐ 正曜: {stars_str}\n\n"
                f"🔹 副曜: {aux_str}\n\n"
                + (f"🔸 四化: {sihua_str}\n\n" if sihua_str else "")
                + (f"🏹 飛星: {fly_str}\n\n" if fly_str else "")
                + (f"📜 格局: {pattern_str}\n\n" if pattern_str else "")
                + f"*{desc}*"
            )


# ============================================================
# SVG 飛星輪盤 (Flying Star Wheel SVG)
# ============================================================

def build_cetian_flyingstar_svg(chart: CetianChart, size: int = 700) -> str:
    """
    產生策天十八飛星輪盤 SVG（古籍手抄本風格 + 飛化箭頭）。

    Parameters:
        chart: 策天命盤資料
        size:  SVG 畫布大小（像素）

    Returns:
        完整 SVG 字串
    """
    cx, cy = size // 2, size // 2
    r_outer = size // 2 - 30
    r_inner = r_outer - 100
    r_text = r_inner + 50
    r_center = r_inner - 20

    # 基本 SVG 頭部
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'<rect width="{size}" height="{size}" fill="#0d0d1a"/>'
    )

    # 外圈
    svg += (
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" '
        f'fill="none" stroke="#c8a96e" stroke-width="2"/>'
    )
    svg += (
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" '
        f'fill="none" stroke="#c8a96e" stroke-width="1"/>'
    )

    # 十二宮分割線
    branch_to_palace = {p.branch: p for p in chart.palaces}
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        x1 = cx + r_inner * math.cos(angle)
        y1 = cy + r_inner * math.sin(angle)
        x2 = cx + r_outer * math.cos(angle)
        y2 = cy + r_outer * math.sin(angle)
        svg += (
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#c8a96e" stroke-width="1"/>'
        )

    # 宮位標籤與星曜
    SIHUA_COLORS = {"祿": "#00E676", "權": "#FF5252", "科": "#42A5F5", "忌": "#FF9800"}
    for i in range(12):
        mid_angle = math.radians(i * 30 + 15 - 90)
        tx = cx + r_text * math.cos(mid_angle)
        ty = cy + r_text * math.sin(mid_angle)

        palace = branch_to_palace.get(i)
        if palace:
            # 宮位名稱
            svg += (
                f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" '
                f'fill="#c8a96e" font-size="10" font-weight="bold">'
                f'{palace.name}</text>'
            )
            # 地支
            svg += (
                f'<text x="{tx:.1f}" y="{ty + 12:.1f}" text-anchor="middle" '
                f'fill="#888" font-size="9">{palace.branch_name}</text>'
            )
            # 星曜
            all_stars = palace.stars + palace.aux_stars
            for j, star in enumerate(all_stars[:3]):
                attr = CETIAN_STAR_ATTRIBUTES.get(star, ("", "", "#aaa"))
                color = attr[2]
                hua = palace.sihua.get(star, "")
                display_color = SIHUA_COLORS.get(hua, color) if hua else color
                sy = ty + 24 + j * 11
                svg += (
                    f'<text x="{tx:.1f}" y="{sy:.1f}" text-anchor="middle" '
                    f'fill="{display_color}" font-size="9">{star}</text>'
                )

    # 飛星箭頭
    for star_name, flight_info in chart.star_flight.items():
        from_b = flight_info["from_branch"]
        to_b = flight_info["to_branch"]
        if from_b == to_b:
            continue
        from_angle = math.radians(from_b * 30 + 15 - 90)
        to_angle = math.radians(to_b * 30 + 15 - 90)
        r_arrow = r_center
        fx = cx + r_arrow * math.cos(from_angle)
        fy = cy + r_arrow * math.sin(from_angle)
        tx_a = cx + r_arrow * math.cos(to_angle)
        ty_a = cy + r_arrow * math.sin(to_angle)

        attr = CETIAN_STAR_ATTRIBUTES.get(star_name, ("", "", "#aaa"))
        arrow_color = attr[2]

        svg += (
            f'<line x1="{fx:.1f}" y1="{fy:.1f}" '
            f'x2="{tx_a:.1f}" y2="{ty_a:.1f}" '
            f'stroke="{arrow_color}" stroke-width="0.8" '
            f'opacity="0.4" stroke-dasharray="3,2"/>'
        )

    # 中心標題
    svg += (
        f'<text x="{cx}" y="{cy - 10}" text-anchor="middle" '
        f'fill="#c8a96e" font-size="14" font-weight="bold">策天十八飛星</text>'
    )
    svg += (
        f'<text x="{cx}" y="{cy + 10}" text-anchor="middle" '
        f'fill="#aaa" font-size="11">古法紫微斗數</text>'
    )

    svg += '</svg>'
    return svg
