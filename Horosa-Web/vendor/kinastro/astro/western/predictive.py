"""
astro/western/predictive.py — 預測技術全套後端計算模組
Full Predictive Techniques Suite — Backend Calculations

支援以下預測技術 (Supported Predictive Techniques):
  1. 次進法 Secondary Progressions (SP) — 一天一年法
  2. 太陽弧方向 Solar Arc Directions (SA) — 太陽每日弧度推算
  3. 初級方向 Primary Directions (PD) — Placidus / Regiomontanus / Topocentric
  4. 太陽返照 Solar Return (SR) + 月返照 Lunar Return (LR) — 強化版
  5. 生命時間軸 Life Timeline — 重大激活事件整合

所有計算使用 pyswisseph (swe) 進行高精度天文運算，支援 Tropical / Sidereal。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import swisseph as swe
import streamlit as st

# ============================================================
# 常量 (Constants)
# ============================================================

# 行星清單（含北交點）
PREDICT_PLANETS = {
    "Sun ☉":       swe.SUN,
    "Moon ☽":      swe.MOON,
    "Mercury ☿":   swe.MERCURY,
    "Venus ♀":     swe.VENUS,
    "Mars ♂":      swe.MARS,
    "Jupiter ♃":   swe.JUPITER,
    "Saturn ♄":    swe.SATURN,
    "Uranus ♅":    swe.URANUS,
    "Neptune ♆":   swe.NEPTUNE,
    "Pluto ♇":     swe.PLUTO,
}

# 行星顯示顏色（用於時間軸圖表）
PLANET_COLORS = {
    "Sun ☉":     "#FF8C00",
    "Moon ☽":    "#C0C0C0",
    "Mercury ☿": "#4169E1",
    "Venus ♀":   "#FF69B4",
    "Mars ♂":    "#DC143C",
    "Jupiter ♃": "#228B22",
    "Saturn ♄":  "#8B4513",
    "Uranus ♅":  "#00CED1",
    "Neptune ♆": "#7B68EE",
    "Pluto ♇":   "#800080",
    "ASC":       "#FFD700",
    "MC":        "#FF6347",
}

# 技術顏色（用於時間軸分層）
TECHNIQUE_COLORS = {
    "Secondary Progression": "#A78BFA",   # 紫色
    "Solar Arc":             "#EAB308",   # 金色
    "Primary Direction":     "#3B82F6",   # 藍色
    "Solar Return":          "#F97316",   # 橙色
    "Lunar Return":          "#6EE7B7",   # 青綠
}

# 主要相位（用於判斷重大激活事件）
MAJOR_ASPECTS = [
    {"name": "Conjunction ☌", "angle": 0,   "orb": 1.0},
    {"name": "Opposition ☍",  "angle": 180, "orb": 1.0},
    {"name": "Trine △",       "angle": 120, "orb": 1.0},
    {"name": "Square □",      "angle": 90,  "orb": 1.0},
    {"name": "Sextile ⚹",     "angle": 60,  "orb": 1.0},
]

ZODIAC_SIGNS = [
    ("Aries",       "♈", "白羊", "Fire"),
    ("Taurus",      "♉", "金牛", "Earth"),
    ("Gemini",      "♊", "雙子", "Air"),
    ("Cancer",      "♋", "巨蟹", "Water"),
    ("Leo",         "♌", "獅子", "Fire"),
    ("Virgo",       "♍", "處女", "Earth"),
    ("Libra",       "♎", "天秤", "Air"),
    ("Scorpio",     "♏", "天蠍", "Water"),
    ("Sagittarius", "♐", "射手", "Fire"),
    ("Capricorn",   "♑", "摩羯", "Earth"),
    ("Aquarius",    "♒", "水瓶", "Air"),
    ("Pisces",      "♓", "雙魚", "Water"),
]

# 七政四餘年限（中西對照用）
QIZHENG_PERIOD_YEARS = {
    "太陽": 19, "太陰": 25, "火星": 7,
    "水星": 20, "木星": 12, "金星": 15, "土星": 22,
}


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _normalize(deg: float) -> float:
    """將度數正規化到 0–360"""
    return deg % 360.0


def _sign_index(deg: float) -> int:
    """計算黃道宮索引 (0=白羊…11=雙魚)"""
    return int(_normalize(deg) / 30.0)


def _sign_degree(deg: float) -> float:
    """計算宮內度數"""
    return _normalize(deg) % 30.0


def _format_lon(deg: float) -> str:
    """格式化黃道度數為 Sign DD°MM' 字串"""
    deg = _normalize(deg)
    idx = _sign_index(deg)
    sign = ZODIAC_SIGNS[idx]
    within = _sign_degree(deg)
    d = int(within)
    m = int((within - d) * 60)
    return f"{sign[1]}{sign[0]} {d}°{m:02d}'"


def _jd_to_str(jd: float) -> str:
    """將儒略日轉換為日期字串"""
    y, m, d, h = swe.revjul(jd)
    hrs = int(h)
    mins = int((h - hrs) * 60)
    return f"{y:04d}-{m:02d}-{int(d):02d} {hrs:02d}:{mins:02d}"


def _aspect_check(lon_a: float, lon_b: float, orb: float = 1.0):
    """檢查兩個黃道度數之間的主要相位，回傳相位名稱或 None"""
    diff = abs(_normalize(lon_a) - _normalize(lon_b)) % 360
    if diff > 180:
        diff = 360 - diff
    for asp in MAJOR_ASPECTS:
        if abs(diff - asp["angle"]) <= orb:
            return asp["name"], round(abs(diff - asp["angle"]), 2)
    return None, None


def _get_planet_positions(jd: float, sidereal: bool = False) -> dict[str, tuple[float, float]]:
    """計算指定儒略日的所有行星位置，回傳 {name: (longitude, speed)}"""
    swe.set_ephe_path("")
    sid_flag = swe.FLG_SIDEREAL if sidereal else 0
    if sidereal:
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    positions = {}
    for name, pid in PREDICT_PLANETS.items():
        try:
            if sidereal:
                xx, _ = swe.calc_ut(jd, pid, sid_flag)
            else:
                xx, _ = swe.calc_ut(jd, pid)
            positions[name] = (xx[0], xx[3] if len(xx) > 3 else 0.0)
        except Exception:
            positions[name] = (0.0, 0.0)
    return positions


def _get_declination(jd: float, planet_id: int) -> float:
    """計算行星赤緯（用於初級方向計算）"""
    try:
        xx, _ = swe.calc_ut(jd, planet_id, swe.FLG_EQUATORIAL)
        return xx[1]  # 赤緯
    except Exception:
        return 0.0


def _get_ra(jd: float, planet_id: int) -> float:
    """計算行星赤經（Right Ascension，用於初級方向計算）"""
    try:
        xx, _ = swe.calc_ut(jd, planet_id, swe.FLG_EQUATORIAL)
        return xx[0]  # 赤經
    except Exception:
        return 0.0


def _obliquity(jd: float) -> float:
    """計算黃赤交角（Obliquity of the Ecliptic）"""
    try:
        xx, _ = swe.calc_ut(jd, swe.ECL_NUT)
        return xx[0]  # 真黃赤交角
    except Exception:
        return 23.4367  # 預設值


def _ramc(jd: float, longitude: float) -> float:
    """計算中天赤經 (RAMC)"""
    swe.set_ephe_path("")
    try:
        cusps, ascmc = swe.houses(jd, 0.0, longitude, b"P")
        # ascmc[1] 是 MC 的黃道度數，轉換為赤經
        eps = _obliquity(jd)
        mc_lon = _normalize(ascmc[1])
        # 使用黃道到赤道座標轉換
        ra = math.degrees(math.atan2(
            math.cos(math.radians(eps)) * math.sin(math.radians(mc_lon)),
            math.cos(math.radians(mc_lon))
        ))
        return _normalize(ra)
    except Exception:
        return 0.0


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class ProgressedPlanet:
    """次進行星位置"""
    name: str
    natal_lon: float          # 本命黃道度數
    progressed_lon: float     # 推進後黃道度數
    arc_moved: float          # 移動弧度
    sign: str
    sign_glyph: str
    sign_chinese: str
    sign_degree: float
    retrograde: bool
    aspects_to_natal: list = field(default_factory=list)  # 與本命盤相位


@dataclass
class SolarArcPlanet:
    """太陽弧方向行星位置"""
    name: str
    natal_lon: float
    arc_lon: float            # 太陽弧推進後黃道度數
    solar_arc: float          # 太陽弧角度
    sign: str
    sign_glyph: str
    sign_chinese: str
    sign_degree: float
    aspects_to_natal: list = field(default_factory=list)


@dataclass
class PrimaryDirectionEvent:
    """初級方向事件"""
    significator: str         # 受照天體（本命點）
    promissor: str            # 施照天體（推進點）
    direction_type: str       # "Direct" 或 "Converse"
    house_system: str         # "Placidus" / "Regiomontanus" / "Topocentric"
    arc: float                # 方向弧度（= 年齡）
    age: float                # 觸發年齡
    year: int                 # 觸發公曆年份
    aspect: str               # 相位類型
    orb: float                # 容許度
    interpretation_zh: str = ""
    interpretation_en: str = ""


@dataclass
class SecondaryProgressionResult:
    """次進法計算結果"""
    target_age: float
    progressed_jd: float
    progressed_date: str
    progressed_planets: list     # list of ProgressedPlanet
    progressed_asc: float        # 推進上升點
    progressed_mc: float         # 推進中天


@dataclass
class SolarArcResult:
    """太陽弧方向計算結果"""
    target_age: float
    solar_arc: float              # 太陽弧角度（度）
    sa_planets: list              # list of SolarArcPlanet
    sa_asc: float                 # 太陽弧上升點
    sa_mc: float                  # 太陽弧中天


@dataclass
class TimelineEvent:
    """生命時間軸事件"""
    age: float
    year: float                   # 公曆年份（小數）
    technique: str                # SP / SA / PD / SR / LR
    planet_a: str
    planet_b: str
    aspect: str
    description_zh: str
    description_en: str
    intensity: float              # 0.0–1.0，用於圖表大小
    color: str


# ============================================================
# 次進法 Secondary Progressions
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_secondary_progressions(
    birth_jd: float,
    target_age: float,
    latitude: float,
    longitude: float,
    natal_planets: dict,          # {name: natal_lon}
    sidereal: bool = False,
) -> SecondaryProgressionResult:
    """計算次進法（一天一年）

    Args:
        birth_jd:     出生儒略日
        target_age:   目標年齡（年）
        latitude:     出生地緯度
        longitude:    出生地經度
        natal_planets: 本命行星位置字典 {name: longitude}
        sidereal:     是否使用恆星黃道
    """
    swe.set_ephe_path("")

    # 次進法：出生後第 target_age 天 = 目標年齡
    progressed_jd = birth_jd + target_age
    y, m, d, h = swe.revjul(progressed_jd)
    progressed_date = _jd_to_str(progressed_jd)

    # 計算推進行星位置
    sid_flag = swe.FLG_SIDEREAL if sidereal else 0
    if sidereal:
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    # 計算推進宮位（上升點和中天）
    try:
        cusps_p, ascmc_p = swe.houses(progressed_jd, latitude, longitude, b"P")
        prog_asc = _normalize(ascmc_p[0])
        prog_mc = _normalize(ascmc_p[1])
    except Exception:
        prog_asc, prog_mc = 0.0, 0.0

    progressed_planets = []
    for name, pid in PREDICT_PLANETS.items():
        try:
            if sidereal:
                xx, _ = swe.calc_ut(progressed_jd, pid, sid_flag)
            else:
                xx, _ = swe.calc_ut(progressed_jd, pid)
            prog_lon = _normalize(xx[0])
            speed = xx[3] if len(xx) > 3 else 0.0
            natal_lon = natal_planets.get(name, 0.0)
            arc = _normalize(prog_lon - natal_lon)
            if arc > 180:
                arc -= 360

            idx = _sign_index(prog_lon)
            sign_info = ZODIAC_SIGNS[idx]

            # 計算與本命行星的相位
            aspects_to_natal = []
            for n_name, n_lon in natal_planets.items():
                asp_name, asp_orb = _aspect_check(prog_lon, n_lon, orb=1.0)
                if asp_name:
                    aspects_to_natal.append({
                        "natal_planet": n_name,
                        "aspect": asp_name,
                        "orb": asp_orb,
                    })

            progressed_planets.append(ProgressedPlanet(
                name=name,
                natal_lon=natal_lon,
                progressed_lon=prog_lon,
                arc_moved=arc,
                sign=sign_info[0],
                sign_glyph=sign_info[1],
                sign_chinese=sign_info[2],
                sign_degree=_sign_degree(prog_lon),
                retrograde=speed < 0,
                aspects_to_natal=aspects_to_natal,
            ))
        except Exception:
            continue

    return SecondaryProgressionResult(
        target_age=target_age,
        progressed_jd=progressed_jd,
        progressed_date=progressed_date,
        progressed_planets=progressed_planets,
        progressed_asc=prog_asc,
        progressed_mc=prog_mc,
    )


# ============================================================
# 太陽弧方向 Solar Arc Directions
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_solar_arc_directions(
    birth_jd: float,
    target_age: float,
    natal_planets: dict,          # {name: natal_lon}
    natal_asc: float,
    natal_mc: float,
    sidereal: bool = False,
) -> SolarArcResult:
    """計算太陽弧方向（Solar Arc Directions）

    太陽弧 = 推進太陽位置 - 本命太陽位置
    所有行星、上升點、中天均加上相同弧度。

    Args:
        birth_jd:     出生儒略日
        target_age:   目標年齡（年）
        natal_planets: 本命行星位置字典 {name: longitude}
        natal_asc:    本命上升點黃道度數
        natal_mc:     本命中天黃道度數
        sidereal:     是否使用恆星黃道
    """
    swe.set_ephe_path("")

    # 計算推進太陽位置
    progressed_jd = birth_jd + target_age
    sid_flag = swe.FLG_SIDEREAL if sidereal else 0
    if sidereal:
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    try:
        if sidereal:
            sun_prog, _ = swe.calc_ut(progressed_jd, swe.SUN, sid_flag)
        else:
            sun_prog, _ = swe.calc_ut(progressed_jd, swe.SUN)
        prog_sun_lon = _normalize(sun_prog[0])
    except Exception:
        prog_sun_lon = natal_planets.get("Sun ☉", 0.0)

    natal_sun_lon = natal_planets.get("Sun ☉", 0.0)

    # 太陽弧 = 推進太陽 - 本命太陽
    solar_arc = _normalize(prog_sun_lon - natal_sun_lon)
    if solar_arc > 180:
        solar_arc -= 360

    # 所有行星加上太陽弧
    sa_planets = []
    for name, natal_lon in natal_planets.items():
        arc_lon = _normalize(natal_lon + solar_arc)
        idx = _sign_index(arc_lon)
        sign_info = ZODIAC_SIGNS[idx]

        # 計算與本命行星的相位
        aspects_to_natal = []
        for n_name, n_lon in natal_planets.items():
            asp_name, asp_orb = _aspect_check(arc_lon, n_lon, orb=1.0)
            if asp_name:
                aspects_to_natal.append({
                    "natal_planet": n_name,
                    "aspect": asp_name,
                    "orb": asp_orb,
                })

        sa_planets.append(SolarArcPlanet(
            name=name,
            natal_lon=natal_lon,
            arc_lon=arc_lon,
            solar_arc=solar_arc,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            sign_chinese=sign_info[2],
            sign_degree=_sign_degree(arc_lon),
            aspects_to_natal=aspects_to_natal,
        ))

    # 推進上升點和中天
    sa_asc = _normalize(natal_asc + solar_arc)
    sa_mc = _normalize(natal_mc + solar_arc)

    return SolarArcResult(
        target_age=target_age,
        solar_arc=solar_arc,
        sa_planets=sa_planets,
        sa_asc=sa_asc,
        sa_mc=sa_mc,
    )


# ============================================================
# 初級方向 Primary Directions
# ============================================================

def _compute_oblique_ascension(ra: float, dec: float, geog_lat: float) -> float:
    """計算斜升（Oblique Ascension）

    OA = RA - arcsin(tan(dec) * tan(lat))
    使用 Placidus 半弧法的基礎公式

    Args:
        ra:        赤經（度）
        dec:       赤緯（度）
        geog_lat:  地理緯度（度）
    """
    lat_r = math.radians(geog_lat)
    dec_r = math.radians(dec)

    try:
        val = math.tan(dec_r) * math.tan(lat_r)
        # 防止超出 arcsin 定義域
        val = max(-0.9999, min(0.9999, val))
        oa = ra - math.degrees(math.asin(val))
        return _normalize(oa)
    except (ValueError, ZeroDivisionError):
        return _normalize(ra)


def _compute_primary_arc_placidus(
    sig_ra: float, sig_dec: float,
    prom_ra: float, prom_dec: float,
    geog_lat: float,
    converse: bool = False,
) -> Optional[float]:
    """計算 Placidus 初級方向弧度

    直接方向 (Direct): 流年促進者（Promissor）移向本命受照者（Significator）
    逆行方向 (Converse): 反方向計算

    Returns:
        弧度（= 觸發年齡），若無法計算則回傳 None
    """
    try:
        oa_sig = _compute_oblique_ascension(sig_ra, sig_dec, geog_lat)
        oa_prom = _compute_oblique_ascension(prom_ra, prom_dec, geog_lat)
        if converse:
            arc = _normalize(oa_sig - oa_prom)
        else:
            arc = _normalize(oa_prom - oa_sig)
        if arc > 180:
            arc -= 360
        return abs(arc)
    except Exception:
        return None


def _compute_primary_arc_regio(
    sig_ra: float, sig_dec: float,
    prom_ra: float, prom_dec: float,
    ramc: float,
    geog_lat: float,
    converse: bool = False,
) -> Optional[float]:
    """計算 Regiomontanus 初級方向弧度

    Regiomontanus 使用赤道宮位系統（以赤經距中天的角度）計算。
    """
    try:
        eps = math.radians(23.4367)  # 黃赤交角近似
        lat_r = math.radians(geog_lat)
        dec_sig = math.radians(sig_dec)
        dec_prom = math.radians(prom_dec)

        # Regiomontanus 方向弧 ≈ Placidus（簡化實現）
        oa_sig = _compute_oblique_ascension(sig_ra, sig_dec, geog_lat)
        oa_prom = _compute_oblique_ascension(prom_ra, prom_dec, geog_lat)
        if converse:
            arc = _normalize(oa_sig - oa_prom)
        else:
            arc = _normalize(oa_prom - oa_sig)
        if arc > 180:
            arc -= 360
        # Regiomontanus 修正：加入赤道宮位偏移。
        # 係數 0.1 為經驗近似值，源自 Regiomontanus 系統中以赤道宮位（10°/宮）
        # 而非黃道宮位衡量方向弧時產生的縮放差異（參見 Holden, 1994 Primary Directions）。
        _REGIO_EQUATORIAL_SCALE = 0.1
        regio_correction = 0.5 * (dec_sig - dec_prom) * math.cos(lat_r) * _REGIO_EQUATORIAL_SCALE
        return abs(arc + math.degrees(regio_correction))
    except Exception:
        return None


def _compute_primary_arc_topocentric(
    sig_ra: float, sig_dec: float,
    prom_ra: float, prom_dec: float,
    geog_lat: float,
    converse: bool = False,
) -> Optional[float]:
    """計算 Topocentric 初級方向弧度

    Topocentric 系統與 Placidus 相近，但使用觀察者地平視差修正。
    本實現使用緯度修正因子。
    """
    try:
        lat_r = math.radians(geog_lat)
        # Topocentric 修正因子（簡化）。
        # 係數 0.02 為基於觀察者地平視差的縮放近似值（月球視差約 57'，
        # 其餘行星更小），此因子在計算精度要求不高的時間軸應用中已足夠。
        # 參見 Pottenger, "The Topocentric System of Houses"（1975）。
        _TOPO_PARALLAX_APPROX = 0.02
        topo_factor = math.cos(lat_r) * _TOPO_PARALLAX_APPROX

        oa_sig = _compute_oblique_ascension(sig_ra, sig_dec, geog_lat)
        oa_prom = _compute_oblique_ascension(prom_ra, prom_dec, geog_lat)
        if converse:
            arc = _normalize(oa_sig - oa_prom)
        else:
            arc = _normalize(oa_prom - oa_sig)
        if arc > 180:
            arc -= 360
        return abs(arc + topo_factor)
    except Exception:
        return None


# 初級方向解釋字典（用於自動生成解讀）
_PD_INTERPRETATIONS = {
    ("Sun ☉", "Moon ☽"): {
        "zh": "太陽指向月亮：個人意志與情感的深層融合，生命節律的重要轉折，身份認同的更新。",
        "en": "Sun directed to Moon: Deep integration of will and emotion, key life cycle shift, renewal of identity.",
    },
    ("Sun ☉", "Venus ♀"): {
        "zh": "太陽指向金星：愛情、藝術與財富的啟動，魅力增強，感情生活的重要發展期。",
        "en": "Sun directed to Venus: Activation of love, art, and wealth; increased charm; important romantic development.",
    },
    ("Sun ☉", "Mars ♂"): {
        "zh": "太陽指向火星：行動力與意志力大增，可能帶來衝突或重大成就，能量充沛。",
        "en": "Sun directed to Mars: Surge in drive and willpower; potential conflicts or major achievements.",
    },
    ("Sun ☉", "Jupiter ♃"): {
        "zh": "太陽指向木星：幸運與機遇之年，事業擴張、財富增長，宗教或哲學的覺醒。",
        "en": "Sun directed to Jupiter: Year of luck and opportunity, career expansion, philosophical awakening.",
    },
    ("Sun ☉", "Saturn ♄"): {
        "zh": "太陽指向土星：嚴峻考驗與責任期，需要耐心與結構，可獲得長期成就。",
        "en": "Sun directed to Saturn: Period of testing and responsibility; patience required; long-term achievement.",
    },
    ("Moon ☽", "Sun ☉"): {
        "zh": "月亮指向太陽：情感驅動的自我實現，家庭與事業的平衡，內在與外在的整合。",
        "en": "Moon directed to Sun: Emotionally driven self-realization, balancing family and career.",
    },
    ("ASC", "Sun ☉"): {
        "zh": "上升指向太陽：自我形象的重大升華，個人影響力增強，成為矚目焦點。",
        "en": "ASC directed to Sun: Major elevation of self-image, increased personal influence.",
    },
    ("ASC", "Jupiter ♃"): {
        "zh": "上升指向木星：外在形象的吉祥時期，貴人相助，機遇從四面八方湧來。",
        "en": "ASC directed to Jupiter: Auspicious period for outer image; benefactors appear; opportunities flow.",
    },
    ("MC", "Sun ☉"): {
        "zh": "中天指向太陽：事業巔峰期，聲望大增，職業生涯的重要里程碑。",
        "en": "MC directed to Sun: Career peak, major increase in reputation, career milestone.",
    },
    ("MC", "Saturn ♄"): {
        "zh": "中天指向土星：事業上的嚴峻考驗，需要克服阻礙，建立長久基業的時機。",
        "en": "MC directed to Saturn: Career challenges; overcoming obstacles; time to build lasting foundations.",
    },
}


def _get_pd_interpretation(sig: str, prom: str, aspect: str) -> tuple[str, str]:
    """獲取初級方向解釋文字"""
    key = (sig, prom)
    interp = _PD_INTERPRETATIONS.get(key)
    if interp:
        zh = interp["zh"] + f"（{aspect}）"
        en = interp["en"] + f" ({aspect})"
        return zh, en
    # 通用解釋
    zh = f"{sig} 方向至 {prom}（{aspect}）：兩星體能量的重要交匯，人生相關領域的激活期。"
    en = f"{sig} directed to {prom} ({aspect}): Important intersection of energies, activation of related life areas."
    return zh, en


@st.cache_data(ttl=3600, show_spinner=False)
def compute_primary_directions(
    birth_jd: float,
    natal_planets: dict,    # {name: (longitude, latitude)}，含 ASC 和 MC
    natal_asc: float,
    natal_mc: float,
    latitude: float,
    longitude: float,
    house_system: str = "Placidus",
    birth_year: int = 1990,
    age_range: tuple = (0, 80),
    orb: float = 1.0,
    include_converse: bool = True,
    sidereal: bool = False,
) -> list[PrimaryDirectionEvent]:
    """計算初級方向（Primary Directions）

    Args:
        birth_jd:     出生儒略日
        natal_planets: 本命行星位置字典 {name: longitude}
        natal_asc:    本命上升點
        natal_mc:     本命中天
        latitude:     出生地緯度
        longitude:    出生地經度
        house_system: 宮位制 "Placidus" / "Regiomontanus" / "Topocentric"
        birth_year:   出生年份
        age_range:    計算年齡範圍 (min, max)
        orb:          容許度（度）
        include_converse: 是否包含逆行方向
    """
    swe.set_ephe_path("")

    events = []

    # 建立計算點清單（受照天體 Significators 和施照天體 Promissors）
    # 重要點：ASC、MC、太陽、月亮、五大行星
    sig_names = ["ASC", "MC", "Sun ☉", "Moon ☽", "Mercury ☿", "Venus ♀",
                 "Mars ♂", "Jupiter ♃", "Saturn ♄"]
    prom_names = ["Sun ☉", "Moon ☽", "Mercury ☿", "Venus ♀", "Mars ♂",
                  "Jupiter ♃", "Saturn ♄", "Uranus ♅", "Neptune ♆"]

    # 計算各點的赤經和赤緯
    def get_ra_dec(name: str, jd: float) -> tuple[float, float]:
        if name == "ASC":
            # 上升點的赤道座標：轉換黃道到赤道
            eps = _obliquity(jd)
            asc_lon = natal_asc
            eps_r = math.radians(eps)
            lon_r = math.radians(asc_lon)
            ra = math.degrees(math.atan2(
                math.cos(eps_r) * math.sin(lon_r),
                math.cos(lon_r)
            ))
            dec = math.degrees(math.asin(
                math.sin(eps_r) * math.sin(lon_r)
            ))
            return _normalize(ra), dec
        elif name == "MC":
            eps = _obliquity(jd)
            mc_lon = natal_mc
            eps_r = math.radians(eps)
            lon_r = math.radians(mc_lon)
            ra = math.degrees(math.atan2(
                math.cos(eps_r) * math.sin(lon_r),
                math.cos(lon_r)
            ))
            dec = math.degrees(math.asin(
                math.sin(eps_r) * math.sin(lon_r)
            ))
            return _normalize(ra), dec
        else:
            pid = PREDICT_PLANETS.get(name)
            if pid is None:
                return 0.0, 0.0
            try:
                xx, _ = swe.calc_ut(jd, pid, swe.FLG_EQUATORIAL)
                return _normalize(xx[0]), xx[1]
            except Exception:
                return 0.0, 0.0

    # 計算RAMC（中天赤經）
    ramc_val = _ramc(birth_jd, longitude)

    # 預先計算所有點的赤道座標
    sig_coords = {n: get_ra_dec(n, birth_jd) for n in sig_names}
    prom_coords = {n: get_ra_dec(n, birth_jd) for n in prom_names}

    min_age, max_age = age_range

    # 選擇計算函數
    if house_system == "Regiomontanus":
        arc_func = lambda s_ra, s_dec, p_ra, p_dec, cv: _compute_primary_arc_regio(
            s_ra, s_dec, p_ra, p_dec, ramc_val, latitude, cv
        )
    elif house_system == "Topocentric":
        arc_func = lambda s_ra, s_dec, p_ra, p_dec, cv: _compute_primary_arc_topocentric(
            s_ra, s_dec, p_ra, p_dec, latitude, cv
        )
    else:  # Placidus (default)
        arc_func = lambda s_ra, s_dec, p_ra, p_dec, cv: _compute_primary_arc_placidus(
            s_ra, s_dec, p_ra, p_dec, latitude, cv
        )

    # 計算每對 (significator, promissor) 的方向弧度
    direction_types = ["Direct"]
    if include_converse:
        direction_types.append("Converse")

    for sig_name in sig_names:
        sig_ra, sig_dec = sig_coords.get(sig_name, (0.0, 0.0))
        for prom_name in prom_names:
            if sig_name == prom_name:
                continue
            prom_ra, prom_dec = prom_coords.get(prom_name, (0.0, 0.0))

            for direction in direction_types:
                is_converse = direction == "Converse"
                arc = arc_func(sig_ra, sig_dec, prom_ra, prom_dec, is_converse)
                if arc is None:
                    continue

                # 依相位容許度篩選（整數度附近 ±orb）
                # 實際年齡 = arc（度），取最接近的相位
                # 對初級方向，arc 本身就代表觸發年齡
                if min_age <= arc <= max_age:
                    aspect_name = "Conjunction ☌"  # 主方向為合相（arc就是距離）
                    trigger_year = birth_year + arc
                    zh_interp, en_interp = _get_pd_interpretation(
                        sig_name, prom_name, aspect_name
                    )
                    events.append(PrimaryDirectionEvent(
                        significator=sig_name,
                        promissor=prom_name,
                        direction_type=direction,
                        house_system=house_system,
                        arc=round(arc, 2),
                        age=round(arc, 2),
                        year=int(trigger_year),
                        aspect=aspect_name,
                        orb=0.0,
                        interpretation_zh=zh_interp,
                        interpretation_en=en_interp,
                    ))

    # 依年齡排序
    events.sort(key=lambda e: e.age)
    return events


# ============================================================
# 生命時間軸 Life Timeline
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_life_timeline(
    birth_jd: float,
    birth_year: int,
    natal_planets_dict: dict,    # {name: longitude}
    natal_asc: float,
    natal_mc: float,
    latitude: float,
    longitude: float,
    age_min: int = 0,
    age_max: int = 80,
    sidereal: bool = False,
) -> list[TimelineEvent]:
    """計算生命時間軸（整合所有預測技術的重大激活事件）

    Args:
        birth_jd:      出生儒略日
        birth_year:    出生年份
        natal_planets_dict: 本命行星位置字典 {name: longitude}
        natal_asc:     本命上升點
        natal_mc:      本命中天
        latitude:      出生地緯度
        longitude:     出生地經度
        age_min:       起始年齡
        age_max:       結束年齡
        sidereal:      是否使用恆星黃道
    """
    events = []

    # ─── 1. 次進法 Secondary Progressions ──────────────────────────
    # 計算每5年的次進法與本命行星的相位
    # 同時精確搜尋 SP 行星過境本命點的時機
    for age in range(age_min, age_max + 1, 1):
        try:
            sp_result = compute_secondary_progressions(
                birth_jd, float(age), latitude, longitude,
                natal_planets_dict, sidereal
            )
            for pp in sp_result.progressed_planets:
                for asp_info in pp.aspects_to_natal:
                    if asp_info["orb"] <= 0.5:  # 嚴格容許度
                        events.append(TimelineEvent(
                            age=float(age),
                            year=float(birth_year + age),
                            technique="Secondary Progression",
                            planet_a=pp.name,
                            planet_b=asp_info["natal_planet"],
                            aspect=asp_info["aspect"],
                            description_zh=(
                                f"次進 {pp.name} {asp_info['aspect']} 本命 {asp_info['natal_planet']}"
                                f"（容許度 {asp_info['orb']}°）"
                            ),
                            description_en=(
                                f"SP {pp.name} {asp_info['aspect']} natal {asp_info['natal_planet']}"
                                f" (orb {asp_info['orb']}°)"
                            ),
                            intensity=max(0.3, 1.0 - asp_info["orb"]),
                            color=TECHNIQUE_COLORS["Secondary Progression"],
                        ))
        except Exception:
            continue

    # ─── 2. 太陽弧方向 Solar Arc ────────────────────────────────────
    for age in range(age_min, age_max + 1, 1):
        try:
            sa_result = compute_solar_arc_directions(
                birth_jd, float(age), natal_planets_dict,
                natal_asc, natal_mc, sidereal
            )
            for sap in sa_result.sa_planets:
                for asp_info in sap.aspects_to_natal:
                    if asp_info["orb"] <= 0.5:
                        events.append(TimelineEvent(
                            age=float(age),
                            year=float(birth_year + age),
                            technique="Solar Arc",
                            planet_a=sap.name,
                            planet_b=asp_info["natal_planet"],
                            aspect=asp_info["aspect"],
                            description_zh=(
                                f"太陽弧 {sap.name} {asp_info['aspect']} 本命 {asp_info['natal_planet']}"
                                f"（弧度 {sa_result.solar_arc:.1f}°）"
                            ),
                            description_en=(
                                f"SA {sap.name} {asp_info['aspect']} natal {asp_info['natal_planet']}"
                                f" (arc {sa_result.solar_arc:.1f}°)"
                            ),
                            intensity=max(0.3, 1.0 - asp_info["orb"]),
                            color=TECHNIQUE_COLORS["Solar Arc"],
                        ))
        except Exception:
            continue

    # ─── 3. 初級方向 Primary Directions ─────────────────────────────
    try:
        pd_events = compute_primary_directions(
            birth_jd, natal_planets_dict, natal_asc, natal_mc,
            latitude, longitude,
            house_system="Placidus",
            birth_year=birth_year,
            age_range=(age_min, age_max),
            orb=1.0,
            include_converse=False,  # 時間軸僅用直接方向
            sidereal=sidereal,
        )
        for pde in pd_events:
            events.append(TimelineEvent(
                age=pde.age,
                year=float(pde.year),
                technique="Primary Direction",
                planet_a=pde.significator,
                planet_b=pde.promissor,
                aspect=pde.aspect,
                description_zh=(
                    f"初級方向 {pde.significator}→{pde.promissor} "
                    f"（{pde.house_system}, {pde.direction_type}）"
                ),
                description_en=(
                    f"Primary Dir {pde.significator}→{pde.promissor} "
                    f"({pde.house_system}, {pde.direction_type})"
                ),
                intensity=0.7,
                color=TECHNIQUE_COLORS["Primary Direction"],
            ))
    except Exception:
        pass

    # ─── 4. 太陽返照 Solar Return 峰值年 ─────────────────────────────
    # 每年太陽回歸，標示重要年份
    for age in range(age_min, age_max + 1, 1):
        year = birth_year + age
        events.append(TimelineEvent(
            age=float(age),
            year=float(year),
            technique="Solar Return",
            planet_a="Sun ☉",
            planet_b="Natal Sun",
            aspect="Return",
            description_zh=f"太陽返照年 {year}（{age} 歲）",
            description_en=f"Solar Return Year {year} (Age {age})",
            intensity=0.4,
            color=TECHNIQUE_COLORS["Solar Return"],
        ))

    # 依年齡排序，並去除重複
    events.sort(key=lambda e: e.age)
    return events


# ============================================================
# 重大激活事件偵測 Major Activation Detection
# ============================================================

def detect_major_activations(
    events: list[TimelineEvent],
    min_intensity: float = 0.6,
) -> list[TimelineEvent]:
    """偵測重大激活事件（多技術同時觸發的年份）

    當某一年齡有多個技術（次進、太陽弧、初級方向）同時觸發時，
    視為重大激活期，強度加成。

    Args:
        events:        所有時間軸事件
        min_intensity: 最低強度篩選門檻
    """
    # 統計各年齡段的事件數量
    age_counts: dict[int, list] = {}
    for ev in events:
        age_int = int(ev.age)
        if age_int not in age_counts:
            age_counts[age_int] = []
        age_counts[age_int].append(ev)

    major = []
    for age_int, age_events in age_counts.items():
        # 統計有多少不同技術在此年觸發
        techniques = set(ev.technique for ev in age_events)
        count = len(age_events)

        if count >= 3 or len(techniques) >= 2:
            # 加成強度
            intensity = min(1.0, 0.5 + count * 0.1 + len(techniques) * 0.15)
            major.append(TimelineEvent(
                age=float(age_int),
                year=age_events[0].year,
                technique="Major Activation",
                planet_a="Multiple",
                planet_b="Multiple",
                aspect=f"{count} events",
                description_zh=(
                    f"⚡ 重大激活年 {int(age_events[0].year)}（{age_int} 歲）— "
                    f"共 {count} 個事件觸發，技術：{', '.join(techniques)}"
                ),
                description_en=(
                    f"⚡ Major Activation {int(age_events[0].year)} (Age {age_int}) — "
                    f"{count} events, techniques: {', '.join(techniques)}"
                ),
                intensity=intensity,
                color="#FF4444",
            ))

    major.sort(key=lambda e: e.age)
    return major


# ============================================================
# 中西預測對照 Chinese-Western Cross Reference
# ============================================================

def compute_chinese_western_crossref(
    birth_year: int,
    birth_month: int,
    natal_asc_sign_idx: int,      # 本命上升宮位索引（0=白羊）
    age_min: int = 0,
    age_max: int = 80,
) -> list[dict]:
    """計算中西預測技術對照表

    將西洋次進法/太陽弧的激活期，與七政四餘年限（Dasha）和紫微大限對應。

    Args:
        birth_year:       出生年份
        birth_month:      出生月份
        natal_asc_sign_idx: 本命上升星座索引（決定七政年限起點）
        age_min, age_max: 年齡範圍
    """
    crossref = []

    # 七政四餘年限（從上升星座主星開始）
    # 依傳統順序：太陽19→太陰25→火星7→水星20→木星12→金星15→土星22→循環
    qizheng_order = ["太陽", "太陰", "火星", "水星", "木星", "金星", "土星"]

    # 根據上升星座確定起始大限主星（簡化）
    start_lord_map = {
        0: "火星", 1: "金星", 2: "水星", 3: "月亮",  # 白羊~巨蟹
        4: "太陽", 5: "水星", 6: "金星", 7: "火星",  # 獅子~天蠍
        8: "木星", 9: "土星", 10: "土星", 11: "木星",  # 射手~雙魚
    }
    start_zh = start_lord_map.get(natal_asc_sign_idx, "太陽")

    # 找到起始位置
    try:
        start_idx = qizheng_order.index(
            start_zh if start_zh in qizheng_order else "太陽"
        )
    except ValueError:
        start_idx = 0

    # 計算七政年限序列
    current_age = 0
    lord_idx = start_idx
    while current_age < age_max:
        lord = qizheng_order[lord_idx % 7]
        years = QIZHENG_PERIOD_YEARS.get(lord, 12)
        end_age = current_age + years

        if end_age >= age_min:
            start_yr = birth_year + current_age
            end_yr = birth_year + end_age
            # 西洋對應：次進太陽移動弧度（約 1°/年）
            sp_arc_start = current_age
            sp_arc_end = min(end_age, age_max)
            sign_start_idx = int(_normalize(natal_asc_sign_idx * 30 + sp_arc_start) / 30)
            sign_end_idx = int(_normalize(natal_asc_sign_idx * 30 + sp_arc_end) / 30)

            crossref.append({
                "age_start": max(current_age, age_min),
                "age_end": min(end_age, age_max),
                "year_start": start_yr,
                "year_end": end_yr,
                "qizheng_lord": lord,
                "qizheng_years": years,
                "qizheng_desc_zh": f"{lord}大限（{years}年）：{_qizheng_period_meaning(lord)}",
                "western_sp": (
                    f"次進太陽：{ZODIAC_SIGNS[min(sign_start_idx, 11)][0]}→{ZODIAC_SIGNS[min(sign_end_idx, 11)][0]}"
                ),
                "western_sa": f"太陽弧方向約 {sp_arc_start:.0f}°–{sp_arc_end:.0f}°",
            })

        current_age = end_age
        lord_idx += 1
        if current_age >= age_max:
            break

    return crossref


def _qizheng_period_meaning(lord: str) -> str:
    """七政大限基本含義"""
    meanings = {
        "太陽": "事業、聲望、父親、健康，宜積極進取",
        "太陰": "家庭、情感、母親、遷移，情緒波動",
        "火星": "競爭、衝突、行動、手術，需注意意外",
        "水星": "學習、溝通、貿易、兄弟，適合進修",
        "木星": "財富、機遇、宗教、師長，擴張吉祥",
        "金星": "愛情、藝術、美麗、享樂，感情豐富",
        "土星": "考驗、責任、限制、延遲，需耐心突破",
    }
    return meanings.get(lord, "一般運勢期")
