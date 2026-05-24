"""
astro/astrocartography.py — Astrocartography (地點占星 / 搬遷線) 計算模組

純粹使用 pyswisseph 實現 Astrocartography 四條線（AC、MC、IC、DC）的計算。

數學原理：
───────────────────────────────────────────
Astrocartography 顯示在出生時刻，各行星在地球上何處具有角度力量
(angular power) ——即該行星恰好位在該地點的某一軸點上。

1. MC 線（中天線）：行星黃經 = 當地 Medium Coeli
   → 使用恆星時 + 行星黃經反推地理經度
   → MC 線是一條垂直的經度線（所有緯度共用同一經度）

2. IC 線（底天線）：MC + 180°，同樣是垂直經線

3. AC 線（上升線）：行星黃經 = 當地 Ascendant
   → 使用球面三角公式，遍歷緯度求解：
     tan(RAMC) = -sin(λ) / [cos(ε)·tan(φ) + sin(ε)·cos(λ)]
   其中 λ=行星黃經, ε=黃赤交角, φ=地理緯度, RAMC=當地恆星時
   → 反推地理經度 = RAMC - 格林威治恆星時(GAST)

4. DC 線（下降線）：行星黃經 + 180° 作為 AC 公式的輸入

Paran（緯度交叉點）：兩條線在同一緯度交叉的點，
代表兩顆行星能量在該緯度同時角化。

References:
- Jim Lewis & Ariel Guttman, *The Astro*Carto*Graphy Book of Maps*
- Swiss Ephemeris documentation on swe.houses / swe.calc_ut
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import streamlit as st
import swisseph as swe

# ============================================================
# 常量 Constants
# ============================================================

# 行星列表（Sun ~ Pluto + Chiron）
# Planet list: Sun through Pluto plus Chiron
ACG_PLANETS: dict[str, int] = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
    "Uranus":  swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto":   swe.PLUTO,
    "Chiron":  swe.CHIRON,
}

# 行星符號 / Planet glyphs
PLANET_GLYPHS: dict[str, str] = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
    "Neptune": "♆", "Pluto": "♇", "Chiron": "⚷",
}

# 線條顏色 / Line colours
LINE_COLORS: dict[str, str] = {
    "AC": "#e74c3c",  # 紅 Red
    "MC": "#3498db",  # 藍 Blue
    "IC": "#2ecc71",  # 綠 Green
    "DC": "#9b59b6",  # 紫 Purple
}

# 行星顏色 / Planet line base colours (for map rendering)
PLANET_COLORS: dict[str, str] = {
    "Sun": "#FF8C00", "Moon": "#C0C0C0", "Mercury": "#4169E1",
    "Venus": "#FF69B4", "Mars": "#DC143C", "Jupiter": "#228B22",
    "Saturn": "#8B4513", "Uranus": "#00CED1", "Neptune": "#7B68EE",
    "Pluto": "#800080", "Chiron": "#D2691E",
}

# 緯度取樣範圍和步長 / Latitude sampling range and step
LAT_MIN = -70.0   # 極地附近(±90°)球面三角公式中 tan(φ) 趨近無窮大，計算不穩定
LAT_MAX = 70.0    # 因此截止 ±70°；此範圍涵蓋絕大多數有人居住的地區
LAT_STEP = 1.0    # 1° step → 141 points per line
N_LAT_SAMPLES = int((LAT_MAX - LAT_MIN) / LAT_STEP) + 1

# 黃赤交角近似值（度）— 精確值由 swe.calc_ut 取得
# Obliquity of the ecliptic — approximate; precise value from swe
OBLIQUITY_DEFAULT = 23.4393

# ============================================================
# 行星能量解釋 Planet Energy Interpretations
# ============================================================

PLANET_LINE_MEANINGS: dict[str, dict[str, str]] = {
    "Sun": {
        "AC": "自我認同與活力充沛，適合展現個人魅力與領導力的地方。",
        "MC": "事業與聲譽的巔峰地帶，適合追求名聲、成就與公眾形象。",
        "IC": "內在根基與家庭感強烈的地方，適合安居與建立歸屬感。",
        "DC": "人際關係與合作夥伴能量強烈，適合尋找重要關係。",
    },
    "Moon": {
        "AC": "情感豐沛、直覺力強，適合滋養身心與建立安全感。",
        "MC": "公眾形象與情感連結強，適合照顧他人的事業（醫護、教育）。",
        "IC": "家庭溫暖與內心安定之地，適合置產、養育子女。",
        "DC": "情感連結深厚的關係之地，適合找到情感伴侶。",
    },
    "Mercury": {
        "AC": "思維敏捷、溝通能力強，適合學習、寫作與社交。",
        "MC": "知識與傳播事業的黃金地帶，適合媒體、教育、商業。",
        "IC": "思考與內在探索的安靜之地，適合閱讀與自我反思。",
        "DC": "交流與合作的活躍之地，適合建立商業夥伴關係。",
    },
    "Venus": {
        "AC": "魅力與美感突出，適合追求愛情、藝術與享受生活。",
        "MC": "藝術與美學事業的寶地，適合時尚、設計、娛樂產業。",
        "IC": "家庭和諧與美感生活之地，適合裝潢、園藝與安居。",
        "DC": "戀愛與婚姻運勢旺盛之地，適合尋找靈魂伴侶。",
    },
    "Mars": {
        "AC": "能量充沛、行動力強，適合運動、創業與挑戰自我。",
        "MC": "事業野心與競爭力旺盛之地，適合軍事、運動、領導。",
        "IC": "內在衝突或家庭壓力較大，需注意居家安全。",
        "DC": "關係中可能有衝突或激情，適合需要果斷行動的合作。",
    },
    "Jupiter": {
        "AC": "幸運與擴展的能量，適合冒險、旅行與自我成長。",
        "MC": "事業擴展與成功的黃金地帶，適合國際商業與高等教育。",
        "IC": "家庭富足與內心滿足之地，適合投資房產。",
        "DC": "貴人運旺盛，適合遇到慷慨的合作夥伴或伴侶。",
    },
    "Saturn": {
        "AC": "責任與紀律的考驗之地，適合磨練意志與建立結構。",
        "MC": "事業穩健但需長期耕耘，適合政府、法律、建築行業。",
        "IC": "家庭責任較重，可能感到孤獨但能建立堅固的根基。",
        "DC": "關係中需要耐心與承諾，適合長期穩定的夥伴關係。",
    },
    "Uranus": {
        "AC": "突變與創新能量強烈，適合追求自由與獨特生活方式。",
        "MC": "事業中的突破與變革，適合科技、創新與社會改革。",
        "IC": "居住環境可能不穩定，但適合追求非傳統的生活方式。",
        "DC": "關係中充滿驚喜與變化，適合開放式或非傳統關係。",
    },
    "Neptune": {
        "AC": "靈性與直覺力強，適合藝術、靈修與療癒工作。",
        "MC": "創意與靈感事業之地，適合音樂、電影、靈性產業。",
        "IC": "內心敏感與幻想之地，需注意邊界感與現實平衡。",
        "DC": "關係中充滿浪漫但需謹防迷惑，適合靈性伴侶。",
    },
    "Pluto": {
        "AC": "深層轉化與力量的地帶，適合心理治療與自我重生。",
        "MC": "權力與影響力強大之地，適合研究、金融與權力機構。",
        "IC": "家庭中可能有深層的心理課題，適合進行家族療癒。",
        "DC": "關係中可能有控制或深層糾纏，適合學習放手與轉化。",
    },
    "Chiron": {
        "AC": "療癒傷口與幫助他人的能量，適合成為療癒者。",
        "MC": "事業中以療癒為使命，適合醫療、諮商與教育。",
        "IC": "內在傷痛需要面對與療癒之地，適合靜修與自我成長。",
        "DC": "在關係中學習療癒與被療癒，適合互相扶持的夥伴。",
    },
}


# ============================================================
# 資料類 Data Classes
# ============================================================

@dataclass
class AcgLinePoint:
    """Astrocartography 線上的一個取樣點"""
    longitude: float   # 地理經度 -180 ~ +180
    latitude: float    # 地理緯度 -90 ~ +90


@dataclass
class AcgLine:
    """一條 Astrocartography 線"""
    planet: str        # 行星名稱
    line_type: str     # "AC", "MC", "IC", "DC"
    points: list[AcgLinePoint] = field(default_factory=list)


@dataclass
class ParanPoint:
    """Paran（緯度交叉點）— 兩條線在同一緯度交叉"""
    latitude: float
    longitude: float
    planet1: str
    line_type1: str
    planet2: str
    line_type2: str


@dataclass
class AcgResult:
    """Astrocartography 完整計算結果"""
    # 行星線：{ "Sun": {"AC": [(lon,lat),...], "MC": [...], ...}, ... }
    lines: dict[str, dict[str, list[tuple[float, float]]]]
    # 行星能量解釋
    meanings: dict[str, dict[str, str]]
    # Paran 交叉點
    parans: list[ParanPoint]
    # 出生 Julian Day
    julian_day: float
    # 行星黃經
    planet_longitudes: dict[str, float]
    # 黃赤交角
    obliquity: float
    # 格林威治恆星時 (度)
    gast_deg: float


# ============================================================
# 核心計算函數 Core Computation Functions
# ============================================================

def _normalize(deg: float) -> float:
    """將角度標準化到 0~360°"""
    return deg % 360.0


def _deg2rad(deg: float) -> float:
    return math.radians(deg)


def _rad2deg(rad: float) -> float:
    return math.degrees(rad)


def _normalize_lon(lon: float) -> float:
    """將地理經度標準化到 -180 ~ +180"""
    lon = lon % 360.0
    if lon > 180.0:
        lon -= 360.0
    return lon


def compute_obliquity(jd: float) -> float:
    """使用 pyswisseph 計算精確黃赤交角 (obliquity of the ecliptic)

    利用 swe.calc_ut 計算特殊天體 SE_ECL_NUT 取得 ε (epsilon)。
    swe.calc_ut(jd, SE_ECL_NUT) 回傳 [true_obliquity, mean_obliquity, nutation_lon, nutation_obl, ...]

    Args:
        jd: Julian Day (UT)

    Returns:
        True obliquity in degrees (真黃赤交角)
    """
    ecl_nut, _ = swe.calc_ut(jd, swe.ECL_NUT)
    return ecl_nut[0]  # true obliquity


def compute_gast(jd: float) -> float:
    """計算格林威治視恆星時 (GAST) in degrees

    格林威治恆星時 = swe.sidtime(jd) 回傳的是小時，需 × 15 轉為度數

    球面天文學基本公式：
    GAST (度) = sidtime * 15.0

    Args:
        jd: Julian Day (UT)

    Returns:
        GAST in degrees (0~360)
    """
    sidtime_hours = swe.sidtime(jd)
    return _normalize(sidtime_hours * 15.0)


def compute_planet_longitudes(jd: float) -> dict[str, float]:
    """計算所有 ACG 行星的熱帶黃道經度

    使用 swe.calc_ut(jd, planet_id) 取得行星的黃經 (tropical ecliptic longitude)。
    若某顆行星（如 Chiron）無法計算（缺少星曆表），則跳過。

    Args:
        jd: Julian Day (UT)

    Returns:
        dict: { "Sun": 123.45, "Moon": 67.89, ... }
    """
    longitudes: dict[str, float] = {}
    for name, planet_id in ACG_PLANETS.items():
        try:
            result, _ = swe.calc_ut(jd, planet_id)
            longitudes[name] = _normalize(result[0])
        except Exception:
            # Some bodies (e.g. Chiron) may require additional ephemeris files;
            # skip gracefully if unavailable.
            pass
    return longitudes


def compute_mc_longitude(planet_lon: float, gast_deg: float,
                         obliquity: float = OBLIQUITY_DEFAULT) -> float:
    """計算 MC 線的地理經度

    MC 線數學原理：
    ─────────────────
    當行星恰好在某地的中天 (MC) 時，表示行星的黃經等於該地的 MC 度數。
    對於 MC 線，行星的赤經 (RA) 等於當地恆星時 (RAMC)。

    簡化計算：MC 線是一條垂直的經線。
    行星黃經透過黃赤交角轉換為赤經 (RA)：
        tan(RA) = cos(ε) · tan(λ)
    其中 λ = 行星黃經, ε = 黃赤交角

    但更準確的做法是直接使用行星黃經作為 RAMC，
    因為 MC 的定義就是黃道與子午圈的交點。

    精確做法：
        RAMC = atan2( sin(λ)·cos(ε), cos(λ) )
        地理經度 = RAMC - GAST

    Args:
        planet_lon: 行星黃經 (degrees)
        gast_deg: 格林威治視恆星時 (degrees)
        obliquity: 黃赤交角 (degrees), 預設使用近似值

    Returns:
        地理經度 (-180 ~ +180)
    """
    lam = _deg2rad(planet_lon)
    eps = _deg2rad(obliquity)
    # 黃經轉赤經
    # RA = atan2(sin(λ)·cos(ε), cos(λ))
    ra = _rad2deg(math.atan2(math.sin(lam) * math.cos(eps), math.cos(lam)))
    ra = _normalize(ra)
    geo_lon = ra - gast_deg
    return _normalize_lon(geo_lon)


def compute_mc_line(planet_lon: float, gast_deg: float,
                    obliquity: float) -> list[tuple[float, float]]:
    """計算 MC 線（中天線）的地球座標

    MC 線是一條垂直的經線——所有緯度共用同一地理經度。
    因為行星在 MC 時，行星的赤經 = 當地恆星時 (Local Sidereal Time, LST)。

    精確黃經→赤經轉換：
        RA = atan2( sin(λ)·cos(ε), cos(λ) )
    其中 λ=行星黃經, ε=黃赤交角

    地理經度 = RA - GAST

    Args:
        planet_lon: 行星黃經 (degrees)
        gast_deg: GAST (degrees)
        obliquity: 黃赤交角 (degrees)

    Returns:
        list of (longitude, latitude) tuples
    """
    lam = _deg2rad(planet_lon)
    eps = _deg2rad(obliquity)

    # 黃經→赤經
    ra = _rad2deg(math.atan2(math.sin(lam) * math.cos(eps), math.cos(lam)))
    ra = _normalize(ra)

    # 地理經度 = RA - GAST
    geo_lon = _normalize_lon(ra - gast_deg)

    # MC 線是一條垂直線，遍歷所有緯度
    points = []
    lat = LAT_MIN
    while lat <= LAT_MAX:
        points.append((geo_lon, lat))
        lat += LAT_STEP
    return points


def compute_ic_line(planet_lon: float, gast_deg: float,
                    obliquity: float) -> list[tuple[float, float]]:
    """計算 IC 線（底天線）的地球座標

    IC = MC + 180°，因此 IC 線就是 MC 線偏移 180° 經度。

    Args:
        planet_lon: 行星黃經 (degrees)
        gast_deg: GAST (degrees)
        obliquity: 黃赤交角 (degrees)

    Returns:
        list of (longitude, latitude) tuples
    """
    return compute_mc_line(_normalize(planet_lon + 180.0), gast_deg, obliquity)


def compute_ac_line(planet_lon: float, gast_deg: float,
                    obliquity: float) -> list[tuple[float, float]]:
    """計算 AC 線（上升線）的地球座標

    AC 線數學原理（球面三角公式）：
    ──────────────────────────────────
    上升點 (Ascendant) 是黃道帶與地平線的東方交點。
    當行星恰好位在某地的上升點時：

    Ascendant 公式 (Placidus / classic formula):
        tan(ASC) = -cos(RAMC) / [sin(ε)·tan(φ) + cos(ε)·sin(RAMC)]

    我們要找：給定行星黃經 λ，在每個緯度 φ 上，
    什麼經度才會讓上升點 = λ？

    反解過程：
    1. 給定 λ 和 φ，解出使 ASC = λ 的 RAMC
    2. 地理經度 = RAMC - GAST

    對 ASC 公式做代數變換解 RAMC：
        令 ASC = λ (行星黃經)
        -cos(RAMC) / [sin(ε)·tan(φ) + cos(ε)·sin(RAMC)] = tan(λ)

        -cos(RAMC) = tan(λ)·[sin(ε)·tan(φ) + cos(ε)·sin(RAMC)]
        -cos(RAMC) = tan(λ)·sin(ε)·tan(φ) + tan(λ)·cos(ε)·sin(RAMC)
        -cos(RAMC) - tan(λ)·cos(ε)·sin(RAMC) = tan(λ)·sin(ε)·tan(φ)

    使用輔助角法 (auxiliary angle method)：
        A·cos(RAMC) + B·sin(RAMC) = C
        where A = -1, B = -tan(λ)·cos(ε), C = tan(λ)·sin(ε)·tan(φ)

        R = √(A² + B²)
        RAMC = atan2(C/R, ...) — 需要解三角方程

    實務上使用迭代法或直接遍歷經度更穩定。
    這裡我們遍歷緯度，對每個緯度用 swe.houses 取得精確 ASC。

    ─────── 高效做法 ───────
    遍歷緯度，對每個緯度用解析法求出 RAMC 使 ASC = λ：

    令 λ = 行星黃經, ε = 黃赤交角, φ = 地理緯度

    由 ASC 公式反解：
    RAMC = atan2(-cos(λ), sin(λ)·cos(ε) + tan(φ)·sin(ε))

    注意：atan2 的使用需要仔細處理象限。

    Args:
        planet_lon: 行星黃經 (degrees, tropical)
        gast_deg: GAST (degrees)
        obliquity: 黃赤交角 (degrees)

    Returns:
        list of (longitude, latitude) tuples
    """
    lam = _deg2rad(planet_lon)
    eps = _deg2rad(obliquity)

    sin_lam = math.sin(lam)
    cos_lam = math.cos(lam)
    sin_eps = math.sin(eps)
    cos_eps = math.cos(eps)

    points = []
    lat = LAT_MIN
    while lat <= LAT_MAX:
        phi = _deg2rad(lat)
        tan_phi = math.tan(phi)

        # 反解 RAMC from ASC 公式:
        # ASC = atan2(-cos(RAMC), sin(ε)·tan(φ) + cos(ε)·sin(RAMC))
        #
        # 我們要 ASC = λ，反推 RAMC。
        # 令 y = -cos(RAMC), x = sin(ε)·tan(φ) + cos(ε)·sin(RAMC)
        # 則 tan(λ) = y/x = -cos(RAMC) / [sin(ε)·tan(φ) + cos(ε)·sin(RAMC)]
        #
        # 直接解析解：
        # RAMC = atan2(-cos(λ), sin(λ)·cos(ε) + tan(φ)·sin(ε))
        #
        # 這是從 AC 公式反解得到的公式。
        # 推導：將 ASC 公式寫成 R·sin(RAMC+δ) 形式再反解。

        y = -cos_lam
        x = sin_lam * cos_eps + tan_phi * sin_eps

        if abs(x) < 1e-12 and abs(y) < 1e-12:
            lat += LAT_STEP
            continue

        ramc = _rad2deg(math.atan2(y, x))
        ramc = _normalize(ramc)

        geo_lon = _normalize_lon(ramc - gast_deg)
        points.append((geo_lon, lat))

        lat += LAT_STEP

    return points


def compute_dc_line(planet_lon: float, gast_deg: float,
                    obliquity: float) -> list[tuple[float, float]]:
    """計算 DC 線（下降線）的地球座標

    DC = ASC + 180°。
    等同於用 (planet_lon + 180°) 來計算 AC 線。

    Args:
        planet_lon: 行星黃經 (degrees)
        gast_deg: GAST (degrees)
        obliquity: 黃赤交角 (degrees)

    Returns:
        list of (longitude, latitude) tuples
    """
    return compute_ac_line(_normalize(planet_lon + 180.0), gast_deg, obliquity)


def find_parans(lines: dict[str, dict[str, list[tuple[float, float]]]],
                lat_tolerance: float = 2.0,
                lon_tolerance: float = 5.0) -> list[ParanPoint]:
    """找出 Paran（緯度交叉點）— 兩條不同行星的線在附近交叉

    Paran 定義：兩條線（不同行星）在相似緯度上的經度也足夠接近。
    代表兩顆行星能量在該地理位置同時角化。

    Args:
        lines: 計算結果
        lat_tolerance: 緯度容許誤差 (degrees)
        lon_tolerance: 經度容許誤差 (degrees)

    Returns:
        list of ParanPoint
    """
    parans: list[ParanPoint] = []

    # 展開所有線段
    all_lines: list[tuple[str, str, list[tuple[float, float]]]] = []
    for planet, line_dict in lines.items():
        for line_type, pts in line_dict.items():
            all_lines.append((planet, line_type, pts))

    # 兩兩比較
    seen: set[tuple] = set()
    for i in range(len(all_lines)):
        p1, lt1, pts1 = all_lines[i]
        for j in range(i + 1, len(all_lines)):
            p2, lt2, pts2 = all_lines[j]
            if p1 == p2:
                continue  # 同行星不算 paran

            # Build latitude index for pts2 for O(n) comparison
            lat_index: dict[float, tuple[float, float]] = {}
            for lon2, lat2 in pts2:
                lat_key = round(lat2, 1)
                lat_index[lat_key] = (lon2, lat2)

            for lon1, lat1 in pts1:
                lat_key = round(lat1, 1)
                pt2 = lat_index.get(lat_key)
                if pt2 is None:
                    continue
                lon2, lat2 = pt2
                if abs(lat1 - lat2) > lat_tolerance:
                    continue

                # Check longitude proximity (handle wraparound)
                d_lon = abs(lon1 - lon2)
                if d_lon > 180:
                    d_lon = 360 - d_lon
                if d_lon <= lon_tolerance:
                    key = tuple(sorted([(p1, lt1), (p2, lt2)])) + (lat_key,)
                    if key not in seen:
                        seen.add(key)
                        parans.append(ParanPoint(
                            latitude=lat1,
                            longitude=(lon1 + lon2) / 2,
                            planet1=p1, line_type1=lt1,
                            planet2=p2, line_type2=lt2,
                        ))

    return parans


# ============================================================
# 主計算函數 Main Computation Function
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_astrocartography(
    year: int, month: int, day: int,
    hour: int, minute: int, timezone: float,
    latitude: float = 0.0, longitude: float = 0.0,
    **kwargs: Any,
) -> AcgResult:
    """計算 Astrocartography 全部行星線

    完整流程：
    1. swe.julday 計算 Julian Day
    2. swe.calc_ut 取得所有行星黃經
    3. swe.sidtime 取得 GAST（格林威治視恆星時）
    4. compute_obliquity 取得精確黃赤交角
    5. 對每顆行星計算 MC/IC/AC/DC 四條線
    6. 找出 Paran 交叉點

    Args:
        year, month, day: 出生日期
        hour, minute: 出生時間
        timezone: 時區 (UTC offset, e.g. +8 for CST)
        latitude, longitude: 出生地經緯度（用於記錄，不影響 ACG 計算）

    Returns:
        AcgResult 包含所有行星線座標、解釋、Paran
    """
    swe.set_ephe_path("")

    # 1. 計算 Julian Day (UT)
    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    # 2. 計算所有行星黃經
    planet_lons = compute_planet_longitudes(jd)

    # 3. 計算 GAST（格林威治視恆星時, 度）
    gast_deg = compute_gast(jd)

    # 4. 計算精確黃赤交角
    obliquity = compute_obliquity(jd)

    # 5. 對每顆行星計算四條線
    lines: dict[str, dict[str, list[tuple[float, float]]]] = {}
    for planet_name, planet_lon in planet_lons.items():
        lines[planet_name] = {
            "MC": compute_mc_line(planet_lon, gast_deg, obliquity),
            "IC": compute_ic_line(planet_lon, gast_deg, obliquity),
            "AC": compute_ac_line(planet_lon, gast_deg, obliquity),
            "DC": compute_dc_line(planet_lon, gast_deg, obliquity),
        }

    # 6. 找出 Paran 交叉點
    parans = find_parans(lines)

    return AcgResult(
        lines=lines,
        meanings=PLANET_LINE_MEANINGS,
        parans=parans,
        julian_day=jd,
        planet_longitudes=planet_lons,
        obliquity=obliquity,
        gast_deg=gast_deg,
    )


@st.cache_data(ttl=3600, show_spinner=False)
def compute_astrocartography_transit(
    natal_year: int, natal_month: int, natal_day: int,
    natal_hour: int, natal_minute: int, natal_timezone: float,
    transit_year: int, transit_month: int, transit_day: int,
    transit_hour: int = 12, transit_minute: int = 0,
    transit_timezone: float = 0.0,
    **kwargs: Any,
) -> AcgResult:
    """計算流年搬遷線 (Transit Astrocartography)

    使用流年時刻的行星位置，計算當下行星的四條線。
    供日期滑桿動態更新使用。

    Args:
        natal_*: 出生資料（用於記錄）
        transit_*: 流年日期時間

    Returns:
        AcgResult
    """
    return compute_astrocartography(
        year=transit_year, month=transit_month, day=transit_day,
        hour=transit_hour, minute=transit_minute, timezone=transit_timezone,
    )


# ============================================================
# AI Prompt Template
# ============================================================

ACG_AI_PROMPT_TEMPLATE = """你是一位專業的地點占星 (Astrocartography) 分析師。
以下是用戶的 Astrocartography 搬遷線資料：

【出生資料】
Julian Day: {julian_day:.4f}
行星黃經: {planet_longitudes}
格林威治恆星時: {gast_deg:.2f}°
黃赤交角: {obliquity:.4f}°

【主要行星線摘要】
{line_summary}

【Paran 交叉點（多線交匯能量區）】
{paran_summary}

請根據以上資料，從地點占星的角度分析：
1. 🌟 最適合搬遷的城市/地區（結合行星能量）
2. 💼 事業發展最佳方位
3. ❤️ 感情與人際關係最佳方位
4. ⚠️ 需要注意或避免的地區
5. 🔄 流年搬遷建議（如有流年資料）
6. 🔮 與其他占星體系（紫微、八字）的交叉比較建議

請用繁體中文回答，語氣親切專業，適當加入占星術語解說。
"""


def format_acg_for_prompt(result: AcgResult) -> str:
    """Format ACG result into AI prompt text"""
    # Line summary
    line_parts = []
    for planet, line_dict in result.lines.items():
        glyph = PLANET_GLYPHS.get(planet, "")
        for lt in ("MC", "IC", "AC", "DC"):
            pts = line_dict.get(lt, [])
            if pts:
                # Sample a few representative points
                mid = len(pts) // 2
                sample_pt = pts[mid]
                meaning = result.meanings.get(planet, {}).get(lt, "")
                line_parts.append(
                    f"  {planet} {glyph} {lt}: 經度 ≈ {sample_pt[0]:.1f}°, "
                    f"緯度 ≈ {sample_pt[1]:.1f}° | {meaning}"
                )

    line_summary = "\n".join(line_parts)

    # Paran summary
    paran_parts = []
    for p in result.parans[:20]:  # Limit to top 20
        paran_parts.append(
            f"  {p.planet1} {p.line_type1} × {p.planet2} {p.line_type2}: "
            f"緯度 {p.latitude:.1f}°, 經度 {p.longitude:.1f}°"
        )
    paran_summary = "\n".join(paran_parts) if paran_parts else "  無顯著交叉點"

    # Planet longitudes as readable string
    lon_strs = [f"{k} {PLANET_GLYPHS.get(k, '')}: {v:.2f}°"
                for k, v in result.planet_longitudes.items()]

    return ACG_AI_PROMPT_TEMPLATE.format(
        julian_day=result.julian_day,
        planet_longitudes=", ".join(lon_strs),
        gast_deg=result.gast_deg,
        obliquity=result.obliquity,
        line_summary=line_summary,
        paran_summary=paran_summary,
    )
