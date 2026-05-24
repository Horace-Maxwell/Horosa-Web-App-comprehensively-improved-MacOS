"""
紫微斗數排盤模組 (Zi Wei Dou Shu Chart Module)

紫微斗數是中國傳統命理學的重要命理排盤系統，以下是主要特點：
- 十二宮位（命宮、兄弟宮、夫妻宮、子女宮、財帛宮、疾厄宮、
           遷移宮、交友宮、官祿宮、田宅宮、福德宮、父母宮）
- 主星：紫微系（紫微、天機、太陽、武曲、天同、廉貞）+
         天府系（天府、太陰、貪狼、巨門、天相、天梁、七殺、破軍）
- 五行局決定排盤規則（水二局、木三局、金四局、土五局、火六局）

使用農曆新年查找表搭配 pyswisseph 朔望月計算確定農曆月份。
"""

import math

import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

from astro.ziwei_vietnamese import (
    get_zodiac_year_label,
    get_vietnamese_zodiac_name,
    get_star_vietnamese_info,
    get_palace_vietnamese_info,
    get_marriage_compatibility,
    build_vietnam_mode_header_html,
    VIETNAMESE_DA_XIAN_TIPS,
    VIETNAMESE_CULTURAL_NOTE,
    VIETNAMESE_MARRIAGE_COMPAT,
    VIETNAMESE_ZODIAC_NAMES,
    VI_FLAG,
    VI_ACCENT_COLOR,
    VI_STAR_COLOR,
)

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
# 命宮在某地支，兄弟宮在下一個地支，依此類推
PALACE_SEQUENCE = [
    "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
    "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮",
]

# 紫微系：相對於紫微星地支的偏移（逆佈 mod 12）
ZIWEI_GROUP = {
    "紫微": 0,
    "天機": 11,   # -1 mod 12
    "太陽": 9,    # -3 mod 12
    "武曲": 8,    # -4 mod 12
    "天同": 7,    # -5 mod 12
    "廉貞": 4,    # -8 mod 12
}

# 天府系：相對於天府星地支的偏移（順佈 mod 12）
TIANFU_GROUP = {
    "天府": 0,
    "太陰": 1,
    "貪狼": 2,
    "巨門": 3,
    "天相": 4,
    "天梁": 5,
    "七殺": 6,
    "破軍": 10,
}

# ============================================================
# 納音五行局 (Nayin Wu Xing Ju)
# ============================================================
# 60 甲子納音五行對應局數，每兩組干支共用一個納音
# 索引 = 六十甲子序號 // 2 (0-29)
# 值 = 五行局數: 金4, 火6, 木3, 土5, 水2
NAYIN_WUXING_JU = [
    4, 6, 3, 5, 4,  # 甲子乙丑海中金, 丙寅丁卯爐中火, 戊辰己巳大林木, 庚午辛未路旁土, 壬申癸酉劍鋒金
    6, 2, 5, 4, 3,  # 甲戌乙亥山頭火, 丙子丁丑澗下水, 戊寅己卯城頭土, 庚辰辛巳白蠟金, 壬午癸未楊柳木
    2, 5, 6, 3, 2,  # 甲申乙酉泉中水, 丙戌丁亥屋上土, 戊子己丑霹靂火, 庚寅辛卯松柏木, 壬辰癸巳長流水
    4, 6, 3, 5, 4,  # 甲午乙未沙中金, 丙申丁酉山下火, 戊戌己亥平地木, 庚子辛丑壁上土, 壬寅癸卯金箔金
    6, 2, 5, 4, 3,  # 甲辰乙巳覆燈火, 丙午丁未天河水, 戊申己酉大驛土, 庚戌辛亥釵環金, 壬子癸丑桑柘木
    2, 5, 6, 3, 2,  # 甲寅乙卯大溪水, 丙辰丁巳沙中土, 戊午己未天上火, 庚申辛酉石榴木, 壬戌癸亥大海水
]

# ============================================================
# 四化表 (Four Transformations by Year Stem)
# ============================================================
# 索引 = 年干 (0=甲 ~ 9=癸)
# 值 = (化祿, 化權, 化科, 化忌) 的星曜名
SIHUA_TABLE = [
    ("廉貞", "破軍", "武曲", "太陽"),  # 甲
    ("天機", "天梁", "紫微", "太陰"),  # 乙
    ("天同", "天機", "文昌", "廉貞"),  # 丙
    ("太陰", "天同", "天機", "巨門"),  # 丁
    ("貪狼", "太陰", "右弼", "天機"),  # 戊
    ("武曲", "貪狼", "天梁", "文曲"),  # 己
    ("太陽", "武曲", "天府", "天同"),  # 庚
    ("巨門", "太陽", "文曲", "文昌"),  # 辛
    ("天梁", "紫微", "左輔", "武曲"),  # 壬
    ("破軍", "巨門", "太陰", "貪狼"),  # 癸
]

# ============================================================
# 祿存表 (Lu Cun by Year Stem)
# ============================================================
# 甲寅 乙卯 丙巳 丁午 戊巳 己午 庚申 辛酉 壬亥 癸子
LUCUN_TABLE = [2, 3, 5, 6, 5, 6, 8, 9, 11, 0]

# ============================================================
# 天魁天鉞表 (Tian Kui / Tian Yue by Year Stem)
# ============================================================
# (天魁branch, 天鉞branch) by year stem
TIANKUI_TIANYUE_TABLE = [
    (1, 7),   # 甲: 丑, 未
    (0, 8),   # 乙: 子, 申
    (11, 9),  # 丙: 亥, 酉
    (11, 9),  # 丁: 亥, 酉
    (1, 7),   # 戊: 丑, 未
    (0, 8),   # 己: 子, 申
    (1, 7),   # 庚: 丑, 未
    (6, 2),   # 辛: 午, 寅
    (3, 5),   # 壬: 卯, 巳
    (3, 5),   # 癸: 卯, 巳
]

# ============================================================
# 火星鈴星起始宮 (Huo Xing / Ling Xing base by year branch group)
# ============================================================
# 年支分四組: 寅午戌(火), 申子辰(水), 巳酉丑(金), 亥卯未(木)
# (火星base, 鈴星base)
HUOXING_LINGXING_BASE = {
    (2, 6, 10): (1, 3),   # 寅午戌: 火星起丑, 鈴星起卯
    (8, 0, 4):  (2, 10),  # 申子辰: 火星起寅, 鈴星起戌
    (5, 9, 1):  (3, 10),  # 巳酉丑: 火星起卯, 鈴星起戌
    (11, 3, 7): (9, 10),  # 亥卯未: 火星起酉, 鈴星起戌
}

# ============================================================
# 天馬表 (Tian Ma by Year Branch)
# ============================================================
TIANMA_TABLE = {
    0: 2, 1: 11, 2: 8, 3: 5, 4: 2, 5: 11,   # 子寅 丑亥 寅申 卯巳 辰寅 巳亥
    6: 8, 7: 5, 8: 2, 9: 11, 10: 8, 11: 5,   # 午申 未巳 申寅 酉亥 戌申 亥巳
}

# ============================================================
# 命主 / 身主表
# ============================================================
MING_ZHU_TABLE = ["貪狼", "巨門", "祿存", "文曲", "廉貞", "武曲",
                  "破軍", "武曲", "廉貞", "文曲", "祿存", "巨門"]
SHEN_ZHU_TABLE = ["火星", "天相", "天梁", "天同", "文昌", "天機",
                  "火星", "天相", "天梁", "天同", "文昌", "天機"]

# ============================================================
# 星曜亮度表 (Star Brightness)
# ============================================================
# 亮度等級: 廟=6, 旺=5, 得=4, 利=3, 平=2, 不=1, 陷=0
# 索引 = 地支 (0=子 ~ 11=亥), 值 = 亮度等級
BRIGHTNESS_TABLE = {
    "紫微": [5, 6, 1, 4, 1, 6, 5, 5, 5, 2, 6, 4],
    "天機": [4, 6, 5, 6, 2, 1, 4, 6, 5, 6, 2, 1],
    "太陽": [5, 6, 6, 6, 5, 4, 2, 1, 0, 0, 1, 2],
    "武曲": [6, 5, 2, 4, 6, 5, 6, 4, 2, 6, 5, 2],
    "天同": [2, 1, 5, 4, 1, 6, 5, 0, 2, 6, 4, 6],
    "廉貞": [2, 0, 6, 5, 2, 2, 6, 2, 6, 0, 2, 5],
    "天府": [6, 5, 6, 4, 6, 5, 6, 4, 6, 5, 6, 4],
    "太陰": [6, 6, 0, 0, 1, 2, 4, 5, 6, 6, 5, 6],
    "貪狼": [5, 6, 2, 6, 2, 6, 5, 6, 2, 6, 2, 6],
    "巨門": [6, 5, 4, 6, 2, 1, 6, 5, 4, 6, 2, 1],
    "天相": [6, 4, 6, 2, 4, 5, 6, 4, 6, 2, 4, 5],
    "天梁": [6, 5, 6, 4, 2, 4, 6, 5, 6, 4, 2, 4],
    "七殺": [6, 5, 6, 2, 4, 4, 6, 5, 6, 2, 4, 4],
    "破軍": [5, 6, 2, 4, 0, 2, 5, 6, 2, 4, 0, 2],
    "文昌": [4, 6, 5, 2, 4, 6, 4, 0, 4, 6, 5, 4],
    "文曲": [4, 2, 4, 6, 5, 6, 4, 0, 4, 2, 5, 6],
    "左輔": [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
    "右弼": [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
    "祿存": [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
}
BRIGHTNESS_LABELS = {6: "廟", 5: "旺", 4: "得", 3: "利", 2: "平", 1: "不", 0: "陷"}

# 主星屬性（五行、別稱、顏色）
STAR_ATTRIBUTES = {
    "紫微": ("土", "帝王星", "#C62828"),
    "天機": ("木", "謀略星", "#2E7D32"),
    "太陽": ("火", "官祿星", "#E65100"),
    "武曲": ("金", "財星", "#F9A825"),
    "天同": ("水", "福星", "#1565C0"),
    "廉貞": ("火", "囚星", "#AD1457"),
    "天府": ("土", "財帛星", "#6A1B9A"),
    "太陰": ("水", "田宅星", "#37474F"),
    "貪狼": ("木/水", "桃花星", "#4A148C"),
    "巨門": ("水", "是非星", "#004D40"),
    "天相": ("水", "印星", "#0D47A1"),
    "天梁": ("土", "蔭星", "#33691E"),
    "七殺": ("金/火", "將星", "#B71C1C"),
    "破軍": ("水", "耗星", "#311B92"),
}

# 農曆新年公曆日期查找表 1900–2050（月, 日）
# 資料來源：天文計算（公開領域）
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

# 平均朔望月長度（天）。此常數用於逼近下次朔望的初始估算；
# 精確朔日時刻由 pyswisseph 的日月黃經迭代法確定。
_SYNODIC_MONTH = 29.5305891

# 北京時間（CST = UTC+8）偏移量（以 JD 天為單位）。
# 農曆以北京時間為準，日期邊界為午夜零時。
_CST_OFFSET = 8.0 / 24.0

# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class ZiweiPalace:
    """紫微斗數宮位資料"""
    index: int                      # 宮位序號 0-11（從命宮算起）
    name: str                       # 宮位名稱
    branch: int                     # 地支索引 0-11（子=0）
    branch_name: str                # 地支名稱
    stem: int                       # 天干索引 0-9
    stem_name: str                  # 天干名稱
    stars: list = field(default_factory=list)       # 主星名稱
    aux_stars: list = field(default_factory=list)   # 輔助星名稱
    brightness: dict = field(default_factory=dict)  # {星名: 亮度標籤}
    sihua: dict = field(default_factory=dict)       # {星名: 四化類型}
    da_xian: str = ""               # 大限年齡範圍 e.g. "3~12"
    da_xian_start: int = 0          # 大限起始年齡
    liu_nian_ages: list = field(default_factory=list)  # 流年年齡列表
    xiao_xian_ages: list = field(default_factory=list) # 小限年齡列表


@dataclass
class ZiweiChart:
    """紫微斗數命盤資料"""
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
    lunar_year_stem: int       # 天干索引
    lunar_year_branch: int     # 地支索引

    # 時辰
    hour_branch: int           # 0-11

    # 命盤關鍵資訊
    ming_gong_branch: int      # 命宮地支索引
    shen_gong_branch: int      # 身宮地支索引
    wu_xing_ju: int            # 五行局（2-6）
    ziwei_branch: int          # 紫微星地支索引
    yin_yang: str              # "陰" or "陽"
    ming_zhu: str              # 命主星名
    shen_zhu: str              # 身主星名

    # 四化
    sihua: dict = field(default_factory=dict)  # {星名: 四化類型}

    # 宮位資料
    palaces: list = field(default_factory=list)  # List[ZiweiPalace]

    # 三合組
    sanhe_groups: list = field(default_factory=list)  # List of (branch1, branch2, branch3)

    # 越南模式
    vietnam_mode: bool = False  # True = 越南 Tử Vi 模式（以貓代兔）


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
        return 0   # 子時 (23:00–01:00)
    return (total_minutes + 60) // 120  # 每 2 小時一個時辰


def _find_new_moon_near(jd_approx: float) -> float:
    """
    以迭代法（牛頓法）找出最接近 jd_approx 的朔（新月）Julian Day。
    收斂至誤差 < 0.0001° 的日食相角。
    """
    jd = jd_approx
    for _ in range(50):
        sun_lon = _normalize(swe.calc_ut(jd, swe.SUN)[0][0])
        moon_lon = _normalize(swe.calc_ut(jd, swe.MOON)[0][0])
        diff = moon_lon - sun_lon
        if diff > 180:
            diff -= 360.0
        elif diff < -180:
            diff += 360.0
        # 月球相對太陽速度約 12.19°/天
        correction = diff / (360.0 / _SYNODIC_MONTH)
        jd -= correction
        if abs(diff) < 0.0001:
            break
    return jd


def _get_cny_jd(year: int) -> float:
    """取得農曆新年的 Julian Day。僅支援 1900–2050；超出範圍時回傳近似值。"""
    if year in _CHINESE_NEW_YEAR:
        m, d = _CHINESE_NEW_YEAR[year]
        return swe.julday(year, m, d, 12.0)
    # 超出查找表範圍：以鄰近端點外推（精度不佳，僅作 fallback）
    if year < 1900:
        m, d = _CHINESE_NEW_YEAR[1900]
        base_jd = swe.julday(1900, m, d, 12.0)
        return base_jd - (1900 - year) * 365.2425
    m, d = _CHINESE_NEW_YEAR[2050]
    base_jd = swe.julday(2050, m, d, 12.0)
    return base_jd + (year - 2050) * 365.2425


def _solar_to_lunar(jd: float) -> tuple[int, int, int, bool]:
    """
    將 Julian Day 轉換為農曆日期。

    農曆以北京時間（UTC+8）為準，日期邊界為午夜零時。
    計算農曆日時，須將 JD（世界時）偏移至北京時間後再取整天數。

    Returns:
        (lunar_year, lunar_month, lunar_day, is_leap_month)
        lunar_month: 1-12（閏月與正常月同編號，is_leap_month=True 區分）
    """
    # 先由儒略日推算公曆年份
    gd = swe.revjul(jd)  # (year, month, day, hour)
    gy = int(gd[0])

    # 確定農曆年：若在當年農曆新年之前，則屬於前一農曆年
    cny_this = _get_cny_jd(gy)
    if jd < cny_this:
        lunar_year = gy - 1
        cny_jd = _get_cny_jd(gy - 1)
    else:
        lunar_year = gy
        cny_jd = cny_this

    # 找出農曆新年當天精確的朔日 JD
    nm_start = _find_new_moon_near(cny_jd)
    # 確保 nm_start <= cny_jd（處理精度邊界）
    while nm_start > cny_jd + 1.0:
        nm_start = _find_new_moon_near(nm_start - _SYNODIC_MONTH)

    # 從農曆新年（正月初一）的朔日開始，逐月計算
    month = 0
    prev_nm = nm_start
    next_nm = _find_new_moon_near(nm_start + _SYNODIC_MONTH)
    is_leap = False

    for m in range(14):  # 農曆年最多 13 個月
        if next_nm > jd:
            month = m + 1
            break
        prev_nm = next_nm
        next_nm = _find_new_moon_near(prev_nm + _SYNODIC_MONTH)
    else:
        month = 1  # fallback

    # 農曆日（1 起計）
    # JD 整數對應世界時正午；加 0.5 轉為以午夜為基準，再加 CST 偏移量
    # 即可取得北京時間的日曆日序號（floor 取整）。
    nm_cal_day = math.floor(prev_nm + _CST_OFFSET + 0.5)
    jd_cal_day = math.floor(jd + _CST_OFFSET + 0.5)
    lunar_day = jd_cal_day - nm_cal_day + 1
    lunar_day = max(1, min(lunar_day, 30))

    # 閏月判斷（簡化版）：農曆年有 13 個月時，第 13 個月視為閏月並折回 12。
    # 嚴格的中氣判斷需要太陽黃經計算，此處採取保守近似——若月份計數超過
    # 12 即標記為閏月，並以相同月份編號記錄。對紫微斗數安星而言，正確的
    # 農曆月份編號（1–12）是關鍵輸入，閏月旗標供顯示用途參考。
    if month > 12:
        is_leap = True
        month = month - 12

    return lunar_year, month, lunar_day, is_leap


def _get_year_stem(lunar_year: int) -> int:
    """
    取得農曆年的天干索引（甲=0, 乙=1, ..., 癸=9）。
    公式：(year - 4) % 10
    """
    return (lunar_year - 4) % 10


def _get_year_branch(lunar_year: int) -> int:
    """
    取得農曆年的地支索引（子=0, 丑=1, ..., 亥=11）。
    公式：(year - 4) % 12
    """
    return (lunar_year - 4) % 12


def _get_ming_gong_branch(lunar_month: int, hour_branch: int) -> int:
    """
    計算命宮地支索引。

    規則（虎月法）：
      以寅宮（地支索引2）為正月所在，逐月順數；
      再由出生時辰逆數。
    公式：(1 + lunar_month - hour_branch) % 12
    """
    return (1 + lunar_month - hour_branch) % 12


def _get_shen_gong_branch(lunar_month: int, hour_branch: int) -> int:
    """
    計算身宮地支索引。

    規則：以寅宮起，逐月順數，再順數時辰。
    公式：(1 + lunar_month + hour_branch) % 12
    """
    return (1 + lunar_month + hour_branch) % 12


def _get_ming_gong_stem(year_stem: int, ming_gong_branch: int) -> int:
    """
    取得命宮天干索引（用於判斷五行局）。

    步驟：
      1. 以年天干推算寅宮天干（虎年起法）：
         寅宮天干 = (2 * (year_stem % 5) + 2) % 10
      2. 命宮天干 = (寅宮天干 + (命宮地支 - 2 + 12) % 12) % 10
    """
    yin_stem = (2 * (year_stem % 5) + 2) % 10
    steps = (ming_gong_branch - 2 + 12) % 12
    return (yin_stem + steps) % 10


def _get_wu_xing_ju(ming_gong_stem: int, ming_gong_branch: int) -> int:
    """
    由命宮天干地支的納音五行判斷五行局號（2-6）。

    使用六十甲子納音五行查表法：
      1. 由天干地支計算六十甲子序號
      2. 每兩組共用一個納音五行
      3. 納音五行對應局數：金4 木3 水2 火6 土5
    """
    sexagenary = (6 * ming_gong_stem - 5 * ming_gong_branch) % 60
    pair_idx = sexagenary // 2
    return NAYIN_WUXING_JU[pair_idx]


def _get_ziwei_branch(lunar_day: int, wu_xing_ju: int) -> int:
    """
    由農曆生日與五行局計算紫微星所在地支索引。

    安紫微法：以局數 N 分組，每 N 天為一組。
    組內第一天（餘數=N-1）在最高位，之後逐日降低。
    整除時為組底。

    公式（使用整數除法）：
      q, r = divmod(lunar_day, wu_xing_ju)
      若 r == 0: branch = q % 12
      若 r > 0: branch = (q + 3 - r) % 12
    """
    n = wu_xing_ju
    q, r = divmod(lunar_day, n)
    if r == 0:
        return q % 12
    return (q + 3 - r) % 12


def _get_tianfu_branch(ziwei_branch: int) -> int:
    """
    由紫微星地支計算天府星地支索引。
    天府與紫微關於寅宮對稱。
    公式：(4 - ziwei_branch + 12) % 12
    """
    return (4 - ziwei_branch + 12) % 12


def _place_main_stars(ziwei_branch: int) -> dict[int, list[str]]:
    """
    計算所有 14 顆主星的地支索引，返回 {branch_index: [star_names]} 映射。
    """
    stars: dict[int, list[str]] = {i: [] for i in range(12)}
    tianfu_branch = _get_tianfu_branch(ziwei_branch)

    for name, offset in ZIWEI_GROUP.items():
        b = (ziwei_branch + offset) % 12
        stars[b].append(name)

    for name, offset in TIANFU_GROUP.items():
        b = (tianfu_branch + offset) % 12
        stars[b].append(name)

    return stars


def _place_auxiliary_stars(
    year_stem: int, year_branch: int,
    lunar_month: int, hour_branch: int,
    lunar_day: int,
) -> dict[int, list[str]]:
    """
    計算輔助星的地支索引，返回 {branch_index: [star_names]} 映射。
    """
    aux: dict[int, list[str]] = {i: [] for i in range(12)}

    # 文昌 (based on hour branch, reverse from 戌)
    wen_chang = (10 - hour_branch + 12) % 12
    aux[wen_chang].append("文昌")

    # 文曲 (based on hour branch, forward from 辰)
    wen_qu = (4 + hour_branch) % 12
    aux[wen_qu].append("文曲")

    # 左輔 (based on lunar month, forward from 辰)
    zuo_fu = (3 + lunar_month) % 12
    aux[zuo_fu].append("左輔")

    # 右弼 (based on lunar month, reverse from 戌)
    you_bi = (11 - lunar_month + 12) % 12
    aux[you_bi].append("右弼")

    # 祿存 (by year stem)
    lu_cun_branch = LUCUN_TABLE[year_stem]
    aux[lu_cun_branch].append("祿存")

    # 擎羊 = 祿存 + 1
    qing_yang = (lu_cun_branch + 1) % 12
    aux[qing_yang].append("擎羊")

    # 陀羅 = 祿存 - 1
    tuo_luo = (lu_cun_branch - 1 + 12) % 12
    aux[tuo_luo].append("陀羅")

    # 天魁 / 天鉞
    kui_branch, yue_branch = TIANKUI_TIANYUE_TABLE[year_stem]
    aux[kui_branch].append("天魁")
    aux[yue_branch].append("天鉞")

    # 火星 / 鈴星 (by year branch group + hour branch)
    huo_base, ling_base = 1, 3  # default
    for branches, bases in HUOXING_LINGXING_BASE.items():
        if year_branch in branches:
            huo_base, ling_base = bases
            break
    huo_xing = (huo_base + hour_branch) % 12
    ling_xing = (ling_base + hour_branch) % 12
    aux[huo_xing].append("火星")
    aux[ling_xing].append("鈴星")

    # 地劫 / 天空
    di_jie = (hour_branch + 11) % 12
    tian_kong = (11 - hour_branch + 12) % 12
    aux[di_jie].append("地劫")
    aux[tian_kong].append("天空")

    # 天馬
    tian_ma = TIANMA_TABLE.get(year_branch, 2)
    aux[tian_ma].append("天馬")

    # 天刑 (based on lunar month, forward from 酉)
    tian_xing = (8 + lunar_month) % 12
    aux[tian_xing].append("天刑")

    # 天姚 (based on lunar month, forward from 丑)
    tian_yao = (0 + lunar_month) % 12
    aux[tian_yao].append("天姚")

    # 天喜 (by year branch: 戌起子 reverse)
    tian_xi = (10 - year_branch + 12) % 12
    aux[tian_xi].append("天喜")

    # 紅鸞 (by year branch)
    hong_luan = (4 - year_branch + 12) % 12
    aux[hong_luan].append("紅鸞")

    # 天哭 / 天虛 (by year branch)
    tian_ku = (6 + year_branch) % 12
    tian_xu = (6 - year_branch + 12) % 12
    aux[tian_ku].append("天哭")
    aux[tian_xu].append("天虛")

    # 龍池 / 鳳閣 (by year branch)
    long_chi = (4 + year_branch) % 12
    feng_ge = (10 - year_branch + 12) % 12
    aux[long_chi].append("龍池")
    aux[feng_ge].append("鳳閣")

    # 恩光 / 天貴 (by day: from 文昌/文曲 forward by day)
    en_guang = (wen_chang + lunar_day - 1) % 12
    tian_gui = (wen_qu + lunar_day - 1) % 12
    aux[en_guang].append("恩光")
    aux[tian_gui].append("天貴")

    # 三台 / 八座 (by month + day, adjusted from 左輔/右弼)
    san_tai = (zuo_fu + lunar_day - 1) % 12
    ba_zuo = (you_bi - lunar_day + 1 + 12) % 12
    aux[san_tai].append("三台")
    aux[ba_zuo].append("八座")

    # 台輔 / 封誥 (by hour)
    tai_fu = (6 + hour_branch) % 12
    feng_gao = (2 + hour_branch) % 12
    aux[tai_fu].append("台輔")
    aux[feng_gao].append("封誥")

    # 天官 / 天福 (by year stem)
    _TIANGUAN = [7, 4, 5, 11, 3, 9, 11, 6, 3, 9]
    _TIANFU_AUX = [9, 8, 0, 11, 3, 6, 11, 2, 3, 6]
    aux[_TIANGUAN[year_stem]].append("天官")
    aux[_TIANFU_AUX[year_stem]].append("天福")

    return aux


def _compute_sihua(year_stem: int, stars_by_branch: dict[int, list[str]],
                   aux_by_branch: dict[int, list[str]]) -> dict[str, str]:
    """
    計算四化：化祿、化權、化科、化忌。
    Returns {star_name: transformation_type}
    """
    lu, quan, ke, ji = SIHUA_TABLE[year_stem]
    return {lu: "祿", quan: "權", ke: "科", ji: "忌"}


def _compute_sanhe_groups(ming_gong_branch: int) -> list[tuple[int, int, int]]:
    """
    計算三合組（每組三個宮位，間隔4個地支）。
    Returns list of (branch1, branch2, branch3) tuples.
    """
    groups = []
    for start in range(4):
        group = tuple((start + i * 4) % 12 for i in range(3))
        groups.append(group)
    return groups


def _compute_feixing(palace_stem: int) -> dict[str, str]:
    """
    計算飛星四化（由宮位天干決定）。
    Returns {star_name: transformation_type}
    """
    lu, quan, ke, ji = SIHUA_TABLE[palace_stem]
    return {lu: "祿", quan: "權", ke: "科", ji: "忌"}


def _build_palaces(
    ming_gong_branch: int,
    year_stem: int,
    stars_by_branch: dict[int, list[str]],
    aux_by_branch: dict[int, list[str]],
    sihua: dict[str, str],
    wu_xing_ju: int,
    is_yang_male_or_yin_female: bool,
) -> list[ZiweiPalace]:
    """
    建立十二宮位資料。
    命宮在 ming_gong_branch，依地支逆序（counter-clockwise）排列。
    宮位天干由虎年起法推算。
    大限方向：陽男陰女順行（地支增加），陰男陽女逆行（地支減少）。
    """
    # 寅宮天干
    yin_stem = (2 * (year_stem % 5) + 2) % 10

    palaces = []
    for idx in range(12):
        # 宮位按逆時針排列（地支遞減）
        branch = (ming_gong_branch - idx + 12) % 12
        palace_name = PALACE_SEQUENCE[idx]
        steps = (branch - 2 + 12) % 12
        stem = (yin_stem + steps) % 10

        # 星曜亮度
        brightness = {}
        all_stars = stars_by_branch.get(branch, []) + aux_by_branch.get(branch, [])
        for star in all_stars:
            if star in BRIGHTNESS_TABLE:
                level = BRIGHTNESS_TABLE[star][branch]
                brightness[star] = BRIGHTNESS_LABELS.get(level, "")

        # 宮位四化（本命四化）
        palace_sihua = {}
        for star in all_stars:
            if star in sihua:
                palace_sihua[star] = sihua[star]

        # 大限：陰男陽女逆行（palace idx直接對應），陽男陰女順行（反轉idx）
        if is_yang_male_or_yin_female:
            da_xian_num = (12 - idx) % 12 if idx > 0 else 0
        else:
            da_xian_num = idx
        da_xian_start = wu_xing_ju + da_xian_num * 10
        da_xian_end = da_xian_start + 9
        da_xian = f"{da_xian_start}~{da_xian_end}"

        palaces.append(ZiweiPalace(
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
        ))
    return palaces


# ============================================================
# 計算函數 (Computation)
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_ziwei_chart(
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
    vietnam_mode: bool = False,
) -> ZiweiChart:
    """
    計算紫微斗數命盤。

    Parameters:
        year, month, day: 公曆出生日期
        hour, minute:     出生時間（24 小時制）
        timezone:         時區偏移（UTC+N）
        latitude:         緯度（排盤資訊用途）
        longitude:        經度（排盤資訊用途）
        location_name:    地點名稱
        gender:           性別（"男" or "女"）
        vietnam_mode:     是否啟用越南 Tử Vi 模式（以貓代兔等越南特色）

    Returns:
        ZiweiChart: 命盤資料
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

    # 五行局（使用納音五行）
    mg_stem = _get_ming_gong_stem(year_stem, ming_gong_branch)
    wu_xing_ju = _get_wu_xing_ju(mg_stem, ming_gong_branch)

    # 紫微星位置
    ziwei_branch = _get_ziwei_branch(lunar_day, wu_xing_ju)

    # 安主星
    stars_by_branch = _place_main_stars(ziwei_branch)

    # 安輔助星
    aux_by_branch = _place_auxiliary_stars(
        year_stem, year_branch, lunar_month, hour_branch, lunar_day
    )

    # 陰陽判斷
    yin_yang = "陽" if year_stem % 2 == 0 else "陰"
    is_yang_male_or_yin_female = (
        (yin_yang == "陽" and gender == "男") or
        (yin_yang == "陰" and gender == "女")
    )

    # 四化
    sihua = _compute_sihua(year_stem, stars_by_branch, aux_by_branch)

    # 命主 / 身主
    ming_zhu = MING_ZHU_TABLE[ming_gong_branch]
    shen_zhu = SHEN_ZHU_TABLE[year_branch]

    # 三合組
    sanhe_groups = _compute_sanhe_groups(ming_gong_branch)

    # 建立宮位
    palaces = _build_palaces(
        ming_gong_branch, year_stem, stars_by_branch, aux_by_branch,
        sihua, wu_xing_ju, is_yang_male_or_yin_female,
    )

    return ZiweiChart(
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
        yin_yang=yin_yang, ming_zhu=ming_zhu, shen_zhu=shen_zhu,
        sihua=sihua, palaces=palaces, sanhe_groups=sanhe_groups,
        vietnam_mode=vietnam_mode,
    )


# ============================================================
# 渲染函數 (Rendering)
# ============================================================

def render_ziwei_chart(chart: ZiweiChart, after_chart_hook=None) -> None:
    """渲染完整的紫微斗數命盤。"""
    if chart.vietnam_mode:
        st.markdown(build_vietnam_mode_header_html(), unsafe_allow_html=True)
        st.subheader(f"{VI_FLAG} 越南 Tử Vi Đẩu Số 命盤")
    else:
        st.subheader("🌟 紫微斗數命盤")
    _render_sihua_legend()
    _render_palace_grid(chart)
    if after_chart_hook:
        after_chart_hook()
    st.divider()
    _render_info(chart)
    st.divider()
    _render_star_table(chart)
    st.divider()
    _render_feixing_table(chart)
    st.divider()
    _render_palace_details(chart)
    if chart.vietnam_mode:
        st.divider()
        _render_vietnam_cultural_section(chart)


def _render_info(chart: ZiweiChart) -> None:
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
        st.write(f"**命主:** {chart.ming_zhu}　**身主:** {chart.shen_zhu}")

    # 四化資訊
    sihua_str = "　".join(
        f"{star}化{hua}" for star, hua in chart.sihua.items()
    )
    st.info(f"**四化:** {sihua_str}")


def _day_to_chinese(day: int) -> str:
    """將農曆日數字轉為中文（如 1→一、11→十一）。"""
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
    palace: ZiweiPalace, is_ming: bool, is_shen: bool
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

    # 四化顏色
    SIHUA_COLORS = {"祿": "#00E676", "權": "#FF5252", "科": "#42A5F5", "忌": "#FF9800"}

    # 主星 HTML（含亮度和四化標記）
    stars_html = ""
    for star in palace.stars:
        attr = STAR_ATTRIBUTES.get(star, ("", "", "#aaa"))
        color = attr[2]
        bright = palace.brightness.get(star, "")
        bright_html = f'<span style="color:#aaa;font-size:9px">{bright}</span>' if bright else ""
        hua = palace.sihua.get(star, "")
        hua_html = ""
        if hua:
            hc = SIHUA_COLORS.get(hua, "#fff")
            hua_html = f'<span style="color:{hc};font-size:10px;font-weight:bold">化{hua}</span>'
        stars_html += (
            f'<div style="display:flex;align-items:center;gap:2px">'
            f'<span style="color:{color};font-size:13px;font-weight:bold">{star}</span>'
            f'{bright_html}{hua_html}</div>'
        )

    # 輔助星 HTML（含亮度和四化標記）
    aux_html = ""
    for star in palace.aux_stars:
        bright = palace.brightness.get(star, "")
        bright_str = f"({bright})" if bright else ""
        hua = palace.sihua.get(star, "")
        hua_str = ""
        if hua:
            hc = SIHUA_COLORS.get(hua, "#fff")
            hua_str = f'<span style="color:{hc};font-size:9px"> 化{hua}</span>'
        aux_html += (
            f'<span style="color:#888;font-size:10px">{star}{bright_str}</span>{hua_str} '
        )

    if not stars_html and not aux_html:
        stars_html = '<div style="color:#666;font-size:11px">─</div>'

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
        f'</div>'
    )


def _center_info_html(chart: ZiweiChart) -> str:
    """產生中宮資訊 HTML（顯示在命盤中央 2×2 格）。"""
    wu_ju = WU_XING_JU_NAMES[chart.wu_xing_ju]
    leap = "（閏）" if chart.is_leap_month else ""
    lm = LUNAR_MONTH_NAMES[chart.lunar_month - 1]
    ld = f"初{_day_to_chinese(chart.lunar_day)}"
    ys = HEAVENLY_STEMS[chart.lunar_year_stem]
    yb = EARTHLY_BRANCHES[chart.lunar_year_branch]

    # 越南模式：生肖名稱覆寫（卯→貓）
    zodiac_label = get_zodiac_year_label(chart.lunar_year_branch, chart.vietnam_mode)
    if chart.vietnam_mode:
        title_text = f"{VI_FLAG} 越南 Tử Vi 命盤"
        title_color = VI_STAR_COLOR
        _zh, yb_vi_full = VIETNAMESE_ZODIAC_NAMES[chart.lunar_year_branch]
        # yb_vi_full is like "Tý / Chuột"; take the first part
        yb_vi = yb_vi_full.split(" / ")[0]
        year_line = (
            f'{chart.lunar_year}年 {ys}{yb}年（{zodiac_label}年/{yb_vi}）'
        )
    else:
        title_text = "紫微斗數命盤"
        title_color = "#c8a96e"
        year_line = f'{chart.lunar_year}年 {ys}{yb}年'

    sihua_html = ""
    SIHUA_COLORS = {"祿": "#00E676", "權": "#FF5252", "科": "#42A5F5", "忌": "#FF9800"}
    for star, hua in chart.sihua.items():
        hc = SIHUA_COLORS.get(hua, "#fff")
        sihua_html += f'<span style="color:{hc};font-size:11px;margin:0 3px">{star}化{hua}</span>'

    return (
        f'<div style="background:#0d0d1a;border:2px solid {title_color};border-radius:10px;'
        f'padding:12px;text-align:center;height:100%;color:#e0d5b0;'
        f'display:flex;flex-direction:column;justify-content:center;">'
        f'<div style="font-size:20px;font-weight:bold;color:{title_color};margin-bottom:4px">'
        f'{title_text}</div>'
        f'<div style="font-size:12px;margin:2px 0">'
        f'{chart.gender}命 / {chart.yin_yang}{chart.gender} / {wu_ju}</div>'
        f'<div style="font-size:12px;margin:2px 0">'
        f'{year_line}</div>'
        f'<div style="font-size:12px;margin:2px 0">'
        f'{lm}{leap} {ld} {HOUR_BRANCH_NAMES[chart.hour_branch]}</div>'
        f'<div style="font-size:11px;margin:2px 0;color:#aaa">'
        f'命主: {chart.ming_zhu}  身主: {chart.shen_zhu}</div>'
        f'<div style="font-size:11px;margin:4px 0;color:#FF6B6B">'
        f'命宮: {EARTHLY_BRANCHES[chart.ming_gong_branch]}宮 '
        f'<span style="color:#4ECDC4">身宮: {EARTHLY_BRANCHES[chart.shen_gong_branch]}宮</span>'
        f'</div>'
        f'<div style="margin-top:4px">{sihua_html}</div>'
        f'<div style="font-size:10px;color:#888;margin-top:4px">'
        f'自化圖示: <span style="color:#00E676">→祿</span>'
        f'<span style="color:#FF5252">→權</span>'
        f'<span style="color:#42A5F5">→科</span>'
        f'<span style="color:#FF9800">→忌</span></div>'
        f'</div>'
    )


def _render_palace_grid(chart: ZiweiChart) -> None:
    """
    渲染南式紫微斗數命盤方格（使用 CSS Grid 單一 HTML 元素）。

    佈局（4×4 方格，中央 2×2 為命盤資訊）：
      巳(5)  午(6)  未(7)  申(8)
      辰(4)  [中宮 info]   酉(9)
      卯(3)  [中宮 info]   戌(10)
      寅(2)  丑(1)  子(0)  亥(11)
    """
    st.markdown("#### 🀄 十二宮命盤方格")

    branch_to_palace: dict[int, ZiweiPalace] = {p.branch: p for p in chart.palaces}

    def cell(branch: int) -> str:
        p = branch_to_palace[branch]
        return _palace_cell_html(
            p,
            is_ming=(p.branch == chart.ming_gong_branch),
            is_shen=(p.branch == chart.shen_gong_branch),
        )

    # 4×4 grid 佈局，中央 2×2 合併為命盤資訊
    # Grid positions (row, col): 1-indexed
    grid_layout = [
        # Row 1: 巳5, 午6, 未7, 申8
        (1, 1, 5), (1, 2, 6), (1, 3, 7), (1, 4, 8),
        # Row 2 left + right: 辰4, 酉9
        (2, 1, 4), (2, 4, 9),
        # Row 3 left + right: 卯3, 戌10
        (3, 1, 3), (3, 4, 10),
        # Row 4: 寅2, 丑1, 子0, 亥11
        (4, 1, 2), (4, 2, 1), (4, 3, 0), (4, 4, 11),
    ]

    cells_html = ""
    for row, col, branch in grid_layout:
        cells_html += (
            f'<div style="grid-row:{row};grid-column:{col}">'
            f'{cell(branch)}</div>'
        )

    # 中宮（rows 2-3, cols 2-3）
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


def _render_star_table(chart: ZiweiChart) -> None:
    """渲染主星位置匯總表格。"""
    if chart.vietnam_mode:
        st.markdown("#### ⭐ 主星分佈表（越南 Tử Vi）")
    else:
        st.markdown("#### ⭐ 主星分佈表")

    all_stars = list(ZIWEI_GROUP.keys()) + list(TIANFU_GROUP.keys())
    branch_to_palace: dict[int, ZiweiPalace] = {p.branch: p for p in chart.palaces}

    if chart.vietnam_mode:
        header = "| 星曜 | 越南名 (Tên Việt) | 五行 | 所在宮位 | 亮度 | 四化 |"
        sep = "|:---:|:---:|:---:|:---:|:---:|:---:|"
    else:
        header = "| 星曜 | 五行 | 別稱 | 所在宮位 | 地支 | 亮度 | 四化 |"
        sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]

    for star in all_stars:
        attr = STAR_ATTRIBUTES[star]
        wuxing, alias, color = attr
        palace = next(
            (p for p in chart.palaces if star in p.stars), None
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
        if chart.vietnam_mode:
            vi_info = get_star_vietnamese_info(star)
            vi_name = vi_info["vi_name"] if vi_info else star
            rows.append(
                f"| {name_html} | {vi_name} | {wuxing} "
                f"| {palace.name}{marker} "
                f"| {bright} "
                f"| {hua_str} |"
            )
        else:
            rows.append(
                f"| {name_html} | {wuxing} | {alias} "
                f"| {palace.name}{marker} "
                f"| {palace.branch_name} "
                f"| {bright} "
                f"| {hua_str} |"
            )

    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_sihua_legend() -> None:
    """渲染四化圖例說明。"""
    st.markdown(
        '<div style="text-align:center;padding:4px;font-size:12px">'
        '四化圖示: '
        '<span style="color:#00E676;font-weight:bold">●祿</span> '
        '<span style="color:#FF5252;font-weight:bold">●權</span> '
        '<span style="color:#42A5F5;font-weight:bold">●科</span> '
        '<span style="color:#FF9800;font-weight:bold">●忌</span>'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_feixing_table(chart: ZiweiChart) -> None:
    """渲染飛星四化表（各宮位天干的四化）。"""
    st.markdown("#### 🌠 飛星四化表")
    st.markdown("*各宮位天干所引發的四化（宮干飛星）*")

    header = "| 宮位 | 天干 | 化祿 | 化權 | 化科 | 化忌 |"
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]

    SIHUA_COLORS = {"祿": "#00E676", "權": "#FF5252", "科": "#42A5F5", "忌": "#FF9800"}

    for palace in chart.palaces:
        feixing = _compute_feixing(palace.stem)
        lu_star = SIHUA_TABLE[palace.stem][0]
        quan_star = SIHUA_TABLE[palace.stem][1]
        ke_star = SIHUA_TABLE[palace.stem][2]
        ji_star = SIHUA_TABLE[palace.stem][3]
        rows.append(
            f"| {palace.name}({palace.branch_name}) | {palace.stem_name} "
            f'| <span style="color:{SIHUA_COLORS["祿"]}">{lu_star}</span> '
            f'| <span style="color:{SIHUA_COLORS["權"]}">{quan_star}</span> '
            f'| <span style="color:{SIHUA_COLORS["科"]}">{ke_star}</span> '
            f'| <span style="color:{SIHUA_COLORS["忌"]}">{ji_star}</span> |'
        )

    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_palace_details(chart: ZiweiChart) -> None:
    """渲染十二宮位詳細說明。"""
    if chart.vietnam_mode:
        st.markdown("#### 📋 十二宮位詳情（越南 Tử Vi）")
    else:
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

    # 三合組顯示
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

            # 四化
            sihua_str = ""
            for star, hua in palace.sihua.items():
                sihua_str += f" {star}化{hua}"

            if chart.vietnam_mode:
                vi_info = get_palace_vietnamese_info(palace.name)
                vi_name = vi_info["vi_name"] if vi_info else ""
                desc = vi_info["zh_interp"] if vi_info else _PALACE_DESC.get(palace.name, "")
                vi_desc = vi_info["vi_interp"] if vi_info else ""
                st.markdown(
                    f"**{palace.stem_name}{palace.branch_name} {palace.name}**"
                    + (f" *{vi_name}*" if vi_name else "")
                    + f" {marker_str} 大限:{palace.da_xian}\n\n"
                    f"⭐ 主星: {stars_str}\n\n"
                    f"🔹 輔星: {aux_str}\n\n"
                    + (f"🔸 四化: {sihua_str}\n\n" if sihua_str else "")
                    + f"*{desc}*\n\n"
                    + (f'<span style="color:#aaa;font-size:11px">🇻🇳 {vi_desc}</span>' if vi_desc else ""),
                    unsafe_allow_html=True,
                )
            else:
                desc = _PALACE_DESC.get(palace.name, "")
                st.markdown(
                    f"**{palace.stem_name}{palace.branch_name} {palace.name}** "
                    f"{marker_str} 大限:{palace.da_xian}\n\n"
                    f"⭐ 主星: {stars_str}\n\n"
                    f"🔹 輔星: {aux_str}\n\n"
                    + (f"🔸 四化: {sihua_str}\n\n" if sihua_str else "")
                    + f"*{desc}*"
                )


def _render_vietnam_cultural_section(chart: ZiweiChart) -> None:
    """渲染越南 Tử Vi 文化特色說明區塊（僅在越南模式時顯示）。"""
    st.markdown(f"#### {VI_FLAG} 越南 Tử Vi 特色說明")

    # 文化說明
    st.info(VIETNAMESE_CULTURAL_NOTE)

    # 生肖資訊：特別標示「貓年」
    zodiac_zh, zodiac_vi = get_vietnamese_zodiac_name(chart.lunar_year_branch)
    st.markdown(
        f"**🐾 生肖年份（越南）**：{zodiac_zh}年（{zodiac_vi}）"
        + ("　← 越南曆法以**貓**代替中國的「兔」🐱" if chart.lunar_year_branch == 3 else "")
    )

    # 越南命宮大限詮釋
    ming_gong_palace = next(
        (p for p in chart.palaces if p.branch == chart.ming_gong_branch), None
    )
    if ming_gong_palace:
        da_xian_key = f"{ming_gong_palace.name}大限"
        da_xian_tip = VIETNAMESE_DA_XIAN_TIPS.get(da_xian_key)
        if da_xian_tip:
            st.markdown(f"**🔮 大限提示**：{da_xian_tip}")

    # 越南婚姻合婚提示（基於年支）
    st.markdown("---")
    st.markdown(f"##### 💕 越南傳統合婚參考（{zodiac_zh}年生人）")

    compat_rows = []
    branch1 = chart.lunar_year_branch
    for branch2 in range(12):
        if branch2 == branch1:
            continue
        key = (min(branch1, branch2), max(branch1, branch2))
        info = VIETNAMESE_MARRIAGE_COMPAT.get(key)
        if info:
            zh2, vi2 = VIETNAMESE_ZODIAC_NAMES[branch2]
            level_color = {
                "大吉": VI_ACCENT_COLOR,
                "吉": "#4CAF50",
                "不利": "#888",
            }.get(info["level"], "#aaa")
            compat_rows.append(
                f'<span style="color:{level_color};font-weight:bold">{info["level"]}</span> '
                f'{zh2}（{vi2}） — {info["note"]}'
            )

    if compat_rows:
        st.markdown(
            "<br>".join(f"• {r}" for r in compat_rows),
            unsafe_allow_html=True,
        )
    else:
        st.write("（無特殊合婚記錄，請查看夫妻宮星曜）")
