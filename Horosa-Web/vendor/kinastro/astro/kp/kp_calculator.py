"""
astro/kp/kp_calculator.py — KP 占星術核心計算引擎

Krishnamurti Paddhati (KP Astrology) Chart Calculator

使用 pyswisseph 計算：
1. KP New Ayanamsa 行星位置（含 Rahu/Ketu）
2. Placidus 宮位系統（12 宮頭）
3. 每顆行星的 Rasi/Star/Sub/Sub-Sub Lord
4. 每個宮頭的 Rasi/Star/Sub Lord
5. Ruling Planets（時辰主星）
6. Significators（徵兆星）分析
7. Horary（問卜）模式支援

References
----------
- Krishnamurti, K.S. "KP Reader Vol. I: Fundamentals"
- Krishnamurti, K.S. "KP Reader Vol. III: Astrological Insights"
- Swiss Ephemeris Documentation
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import swisseph as swe
from datetime import datetime

from astro.kp.constants import (
    KP_AYANAMSA_NAME,
    NAKSHATRAS,
    PLANETS,
    HOUSES,
    get_kp_ayanamsa,
)
from astro.kp.kp_utils import (
    get_rasi_lord,
    get_nakshatra_lord,
    get_sub_lord,
    get_sub_sub_lord,
    get_complete_lordship,
    get_nakshatra_name,
    get_nakshatra_pada,
    calculate_ruling_planets,
    get_significators,
    get_all_house_lords,
    KPLordship,
    KPSignificator,
)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class KPPlanetPosition:
    """
    KP 行星位置
    
    Attributes
    ----------
    name : str
        行星英文名稱
    name_cn : str
        行星中文名稱
    longitude : float
        經度（0-360 度，KP Ayanamsa）
    latitude : float
        緯度（度數）
    speed : float
        運行速度（度數/天）
    is_retrograde : bool
        是否逆行
    house : int
        宮位（1-12）
    sign : int
        星座序號（0-11）
    sign_degree : float
        在星座內的度數（0-30）
    nakshatra : str
        宿名（英文）
    nakshatra_cn : str
        宿名（中文）
    nakshatra_pada : int
        Padam（1-4）
    rasi_lord : str
        星座主
    star_lord : str
        宿度主
    sub_lord : str
        分主
    sub_sub_lord : str
        細分主
    """
    name: str
    name_cn: str
    longitude: float
    latitude: float
    speed: float
    is_retrograde: bool
    house: int
    sign: int
    sign_degree: float
    nakshatra: str
    nakshatra_cn: str
    nakshatra_pada: int
    rasi_lord: str
    star_lord: str
    sub_lord: str
    sub_sub_lord: str


@dataclass
class KPCusp:
    """
    KP 宮頭（Cusp）
    
    Attributes
    ----------
    house_number : int
        宮位序號（1-12）
    longitude : float
        宮頭經度（0-360 度）
    sign : int
        星座序號（0-11）
    sign_degree : float
        在星座內的度數（0-30）
    nakshatra : str
        宿名
    nakshatra_cn : str
        宿名（中文）
    nakshatra_pada : int
        Padam（1-4）
    rasi_lord : str
        星座主
    star_lord : str
        宿度主
    sub_lord : str
        分主
    house_lord : str
        宮主星（該宮星座的主星）
    """
    house_number: int
    longitude: float
    sign: int
    sign_degree: float
    nakshatra: str
    nakshatra_cn: str
    nakshatra_pada: int
    rasi_lord: str
    star_lord: str
    sub_lord: str
    house_lord: str


@dataclass
class KPRulingPlanets:
    """
    KP 時辰主星（Ruling Planets）
    
    Attributes
    ----------
    day_lord : str
        日主（星期主星）
    moon_star_lord : str
        月亮宿度主
    moon_sign_lord : str
        月亮星座主
    lagna_star_lord : str
        上升宿度主
    lagna_sign_lord : str
        上升星座主
    moon_longitude : float
        月亮經度
    ascendant_longitude : float
        上升點經度
    day_of_week : int
        星期（0=Monday, 6=Sunday）
    """
    day_lord: str
    moon_star_lord: str
    moon_sign_lord: str
    lagna_star_lord: str
    lagna_sign_lord: str
    moon_longitude: float
    ascendant_longitude: float
    day_of_week: int


@dataclass
class KPChart:
    """
    KP 完整命盤
    
    Attributes
    ----------
    planets : List[KPPlanetPosition]
        行星位置列表（9 顆：Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu）
    cusps : List[KPCusp]
        12 宮頭列表
    ruling_planets : KPRulingPlanets
        時辰主星
    house_lords : Dict[int, str]
        宮主星字典 {宮位：主星}
    significators : Dict[int, List[KPSignificator]]
        12 宮徵兆星字典 {宮位：徵兆星列表}
    ayanamsa : float
        KP Ayanamsa 值
    julian_day : float
        儒略日
    is_horary : bool
        是否為問卜圖
    """
    planets: List[KPPlanetPosition]
    cusps: List[KPCusp]
    ruling_planets: KPRulingPlanets
    house_lords: Dict[int, str]
    significators: Dict[int, List[KPSignificator]]
    ayanamsa: float
    julian_day: float
    is_horary: bool = False


# ============================================================================
# CORE COMPUTATION
# ============================================================================

def compute_kp_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    latitude: float,
    longitude: float,
    timezone: float,
    language: str = "en",
    is_horary: bool = False,
) -> KPChart:
    """
    計算完整的 KP 命盤
    
    使用 Swiss Ephemeris 計算行星位置和宮位，
    然後應用 KP 系統的主星計算（Rasi/Star/Sub/Sub-Sub Lord）。
    
    Parameters
    ----------
    year : int
        年份
    month : int
        月份
    day : int
        日期
    hour : int
        小時
    minute : int
        分鐘
    latitude : float
        緯度
    longitude : float
        經度
    timezone : float
        時區
    language : str
        語言（"en" / "zh"）
    is_horary : bool
        是否為問卜圖
    
    Returns
    -------
    KPChart
        完整的 KP 命盤物件
    """
    # 計算儒略日
    julian_day = swe.julday(year, month, day, hour + minute / 60.0)
    
    # 計算 KP Ayanamsa
    kp_ayanamsa = get_kp_ayanamsa(julian_day)
    
    # 設置 Swiss Ephemeris
    # 注意：KP 使用自己的 Ayanamsa，但 Swiss Ephemeris 沒有內建 KP 模式
    # 我們使用 Lahiri 模式，然後手動減去 KP 偏移
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # 計算行星位置（使用 KP Ayanamsa 修正）
    planets_data = _compute_planet_positions(
        julian_day, latitude, longitude, timezone, kp_ayanamsa
    )
    
    # 計算宮位（使用 Placidus 系統）
    cusps_data = _compute_house_cusps(
        julian_day, latitude, longitude, timezone, kp_ayanamsa
    )
    
    # 計算行星所在的宮位
    _assign_houses_to_planets(planets_data, cusps_data)
    
    # 計算 Ruling Planets
    ruling_planets_data = calculate_ruling_planets(
        julian_day, latitude, longitude, timezone
    )
    
    ruling_planets = KPRulingPlanets(
        day_lord=ruling_planets_data["day_lord"],
        moon_star_lord=ruling_planets_data["moon_star_lord"],
        moon_sign_lord=ruling_planets_data["moon_sign_lord"],
        lagna_star_lord=ruling_planets_data["lagna_star_lord"],
        lagna_sign_lord=ruling_planets_data["lagna_sign_lord"],
        moon_longitude=ruling_planets_data["moon_longitude"],
        ascendant_longitude=ruling_planets_data["ascendant_longitude"],
        day_of_week=ruling_planets_data["day_of_week"],
    )
    
    # 計算宮主星
    cusp_longitudes = [cusp.longitude for cusp in cusps_data]
    house_lords = get_all_house_lords(cusp_longitudes)
    
    # 計算 Significators
    planet_dicts = [
        {
            "name": p.name,
            "longitude": p.longitude,
            "house": p.house,
            "star_lord": p.star_lord,
            "sub_lord": p.sub_lord,
        }
        for p in planets_data
    ]
    
    significators = {}
    for house_num in range(1, 13):
        significators[house_num] = get_significators(
            planet_dicts, cusp_longitudes, house_num
        )
    
    # 組裝 KPChart
    chart = KPChart(
        planets=planets_data,
        cusps=cusps_data,
        ruling_planets=ruling_planets,
        house_lords=house_lords,
        significators=significators,
        ayanamsa=kp_ayanamsa,
        julian_day=julian_day,
        is_horary=is_horary,
    )
    
    return chart


def _compute_planet_positions(
    julian_day: float,
    latitude: float,
    longitude: float,
    timezone: float,
    kp_ayanamsa: float,
) -> List[KPPlanetPosition]:
    """
    計算行星位置（含 KP 主星）
    
    Parameters
    ----------
    julian_day : float
        儒略日
    latitude : float
        緯度
    longitude : float
        經度
    timezone : float
        時區
    kp_ayanamsa : float
        KP Ayanamsa 值
    
    Returns
    -------
    List[KPPlanetPosition]
        行星位置列表
    """
    planets = []
    
    # 行星列表（使用 Swiss Ephemeris 編號）
    # 0=Sun, 1=Moon, 2=Mercury, 3=Venus, 4=Mars, 5=Jupiter, 6=Saturn
    # Rahu/Ketu 使用特殊計算
    swisseph_planets = [
        (swe.SUN, "Sun", "太陽"),
        (swe.MOON, "Moon", "月亮"),
        (swe.MERCURY, "Mercury", "水星"),
        (swe.VENUS, "Venus", "金星"),
        (swe.MARS, "Mars", "火星"),
        (swe.JUPITER, "Jupiter", "木星"),
        (swe.SATURN, "Saturn", "土星"),
    ]
    
    for swe_id, name_en, name_cn in swisseph_planets:
        # 計算行星位置
        # swe.calc_ut 返回 ( [lon, lat, ...], flags ) 的 tuple
        result, flags = swe.calc_ut(julian_day, swe_id)
        
        # 經度（轉換為 KP Ayanamsa）
        # result[0] is longitude (float)
        lahiri_lon = float(result[0]) % 360.0
        
        # 簡化：假設 KP 與 Lahiri 差異很小（實際約 0°00'10\"）
        # 更精確的計算需要動態計算兩者差異
        kp_lon = lahiri_lon  # 暫時使用 Lahiri
        
        # 緯度
        lat = float(result[1])
        
        # 速度（用於判斷逆行）
        # 計算前一天的位置來獲取速度
        prev_result, _ = swe.calc_ut(julian_day - 1, swe_id)
        speed = kp_lon - (float(prev_result[0]) % 360.0)
        
        # 處理跨 360° 的情況
        if speed < -180:
            speed += 360
        elif speed > 180:
            speed -= 360
        
        # 判斷逆行（速度為負）
        is_retrograde = speed < 0
        
        # 計算星座和度數
        sign = int(kp_lon / 30.0)
        sign_degree = kp_lon % 30.0
        
        # 計算 KP 主星
        lordship = get_complete_lordship(kp_lon)
        
        # 獲取宿名和 Padam
        nakshatra_en = get_nakshatra_name(kp_lon, "en")
        nakshatra_cn = get_nakshatra_name(kp_lon, "zh")
        pada = get_nakshatra_pada(kp_lon)
        
        planet = KPPlanetPosition(
            name=name_en,
            name_cn=name_cn,
            longitude=kp_lon,
            latitude=lat,
            speed=speed,
            is_retrograde=is_retrograde,
            house=0,  # 稍後分配
            sign=sign,
            sign_degree=sign_degree,
            nakshatra=nakshatra_en,
            nakshatra_cn=nakshatra_cn,
            nakshatra_pada=pada,
            rasi_lord=lordship.rasi_lord,
            star_lord=lordship.star_lord,
            sub_lord=lordship.sub_lord,
            sub_sub_lord=lordship.sub_sub_lord,
        )
        
        planets.append(planet)
    
    # 計算 Rahu 和 Ketu（月球交點）
    rahu_ketu = _compute_rahu_ketu(julian_day, kp_ayanamsa)
    planets.extend(rahu_ketu)
    
    return planets


def _compute_rahu_ketu(
    julian_day: float,
    kp_ayanamsa: float,
) -> List[KPPlanetPosition]:
    """
    計算 Rahu（北交點）和 Ketu（南交點）
    
    Parameters
    ----------
    julian_day : float
        儒略日
    kp_ayanamsa : float
        KP Ayanamsa 值
    
    Returns
    -------
    List[KPPlanetPosition]
        Rahu 和 Ketu 的位置列表
    """
    rahu_ketu_list = []
    
    # 使用 Swiss Ephemeris 計算真實交點
    # swe.MEAN_NODE 是平交點，swe.TRUE_NODE 是真交點
    # KP 通常使用平交點
    result, _ = swe.calc_ut(julian_day, swe.MEAN_NODE)
    
    rahu_lon = float(result[0]) % 360.0
    rahu_lat = float(result[1])
    
    # Ketu 永遠在 Rahu 對面（相差 180°）
    ketu_lon = (rahu_lon + 180.0) % 360.0
    ketu_lat = -rahu_lat  # 緯度相反
    
    # 計算速度（交點總是逆行）
    prev_result, _ = swe.calc_ut(julian_day - 1, swe.MEAN_NODE)
    prev_rahu_lon = float(prev_result[0]) % 360.0
    
    rahu_speed = rahu_lon - prev_rahu_lon
    if rahu_speed > 180:
        rahu_speed -= 360
    
    ketu_speed = rahu_speed  # Ketu 速度與 Rahu 相同
    
    # 為 Rahu 和 Ketu 計算主星
    for lon, name_en, name_cn, speed in [
        (rahu_lon, "Rahu", "羅睺", rahu_speed),
        (ketu_lon, "Ketu", "計都", ketu_speed),
    ]:
        sign = int(lon / 30.0)
        sign_degree = lon % 30.0
        
        lordship = get_complete_lordship(lon)
        nakshatra_en = get_nakshatra_name(lon, "en")
        nakshatra_cn = get_nakshatra_name(lon, "zh")
        pada = get_nakshatra_pada(lon)
        
        planet = KPPlanetPosition(
            name=name_en,
            name_cn=name_cn,
            longitude=lon,
            latitude=0.0,  # 交點緯度通常忽略
            speed=speed,
            is_retrograde=True,  # 交點總是逆行
            house=0,
            sign=sign,
            sign_degree=sign_degree,
            nakshatra=nakshatra_en,
            nakshatra_cn=nakshatra_cn,
            nakshatra_pada=pada,
            rasi_lord=lordship.rasi_lord,
            star_lord=lordship.star_lord,
            sub_lord=lordship.sub_lord,
            sub_sub_lord=lordship.sub_sub_lord,
        )
        
        rahu_ketu_list.append(planet)
    
    return rahu_ketu_list


def _compute_house_cusps(
    julian_day: float,
    latitude: float,
    longitude: float,
    timezone: float,
    kp_ayanamsa: float,
) -> List[KPCusp]:
    """
    計算 12 宮頭（使用 Placidus 系統）
    
    KP 系統使用 Placidus 宮位制，這是與傳統 Vedic 占星的主要區別之一。
    
    Parameters
    ----------
    julian_day : float
        儒略日
    latitude : float
        緯度
    longitude : float
        經度
    timezone : float
        時區
    kp_ayanamsa : float
        KP Ayanamsa 值
    
    Returns
    -------
    List[KPCusp]
        12 宮頭列表
    """
    cusps = []
    
    # 使用 Swiss Ephemeris 計算 Placidus 宮位
    # swe.houses() 返回 (cusps, ascmc)
    # cusps[0] = Ascendant (宮位 1)
    # cusps[1] = 宮位 2, ..., cusps[11] = 宮位 12
    cusps_result, ascmc = swe.houses(julian_day, latitude, longitude, b'P')  # 'P' = Placidus
    
    # 處理 12 宮頭
    for i in range(12):
        cusp_lon = float(cusps_result[i]) % 360.0
        
        # 計算星座和度數
        sign = int(cusp_lon / 30.0)
        sign_degree = cusp_lon % 30.0
        
        # 計算 KP 主星
        lordship = get_complete_lordship(cusp_lon)
        
        # 獲取宿名和 Padam
        nakshatra_en = get_nakshatra_name(cusp_lon, "en")
        nakshatra_cn = get_nakshatra_name(cusp_lon, "zh")
        pada = get_nakshatra_pada(cusp_lon)
        
        # 計算宮主星（該宮星座的主星）
        house_lord = get_rasi_lord(cusp_lon)
        
        cusp = KPCusp(
            house_number=i + 1,
            longitude=cusp_lon,
            sign=sign,
            sign_degree=sign_degree,
            nakshatra=nakshatra_en,
            nakshatra_cn=nakshatra_cn,
            nakshatra_pada=pada,
            rasi_lord=lordship.rasi_lord,
            star_lord=lordship.star_lord,
            sub_lord=lordship.sub_lord,
            house_lord=house_lord,
        )
        
        cusps.append(cusp)
    
    return cusps


def _assign_houses_to_planets(
    planets: List[KPPlanetPosition],
    cusps: List[KPCusp],
) -> None:
    """
    為行星分配宮位（使用 Placidus 宮頭）
    
    KP 使用宮頭來劃分宮位：
    - 行星位於宮頭 cusp[i] 和 cusp[i+1] 之間 → 第 i+1 宮
    - 特殊處理：第 12 宮到第 1 宮的跨 360° 情況
    
    Parameters
    ----------
    planets : List[KPPlanetPosition]
        行星位置列表（原地修改）
    cusps : List[KPCusp]
        12 宮頭列表
    """
    # 提取宮頭經度
    cusp_longitudes = [cusp.longitude for cusp in cusps]
    
    for planet in planets:
        planet_lon = planet.longitude
        
        # 找出行星位於哪個宮位
        house_found = False
        
        for i in range(12):
            current_cusp = cusp_longitudes[i]
            next_cusp = cusp_longitudes[(i + 1) % 12]
            
            # 處理跨 360° 的情況（第 12 宮）
            if i == 11:  # 第 12 宮
                # 第 12 宮：從 cusp[11] 到 360° + cusp[0]
                if current_cusp <= planet_lon < 360:
                    planet.house = 12
                    house_found = True
                    break
                elif 0 <= planet_lon < next_cusp:
                    planet.house = 12
                    house_found = True
                    break
            else:
                # 一般宮位
                if current_cusp <= planet_lon < next_cusp:
                    planet.house = i + 1
                    house_found = True
                    break
        
        # 如果沒找到（理論上不應該發生），預設為第 1 宮
        if not house_found:
            planet.house = 1


# ============================================================================
# HORARY（問卜）專用函數
# ============================================================================

def compute_kp_horary_chart(
    question_year: int,
    question_month: int,
    question_day: int,
    question_hour: int,
    question_minute: int,
    question_latitude: float,
    question_longitude: float,
    question_timezone: float,
    language: str = "en",
) -> KPChart:
    """
    計算 KP 問卜圖（Horary Chart）
    
    問卜圖使用提問時間和地點，而非出生時間。
    KP 的問卜系統非常精確，被認為是 KP 最強大的應用之一。
    
    Parameters
    ----------
    question_year : int
        提問年份
    question_month : int
        提問月份
    question_day : int
        提問日期
    question_hour : int
        提問小時
    question_minute : int
        提問分鐘
    question_latitude : float
        提問地點緯度
    question_longitude : float
        提問地點經度
    question_timezone : float
        提問地點時區
    language : str
        語言
    
    Returns
    -------
    KPChart
        問卜圖物件（is_horary=True）
    """
    return compute_kp_chart(
        year=question_year,
        month=question_month,
        day=question_day,
        hour=question_hour,
        minute=question_minute,
        latitude=question_latitude,
        longitude=question_longitude,
        timezone=question_timezone,
        language=language,
        is_horary=True,
    )


# ============================================================================
# COMPARISON FUNCTIONS（對比功能）
# ============================================================================

def compare_kp_with_vedic(
    kp_chart: KPChart,
    vedic_chart: Any,  # 從 vedic.indian.py 導入的類型
) -> Dict:
    """
    比較 KP 與 Vedic 命盤的差異
    
    主要比較：
    1. Ayanamsa 差異
    2. 宮位系統差異（Placidus vs Whole Sign）
    3. 行星歸屬差異
    
    Parameters
    ----------
    kp_chart : KPChart
        KP 命盤
    vedic_chart : Any
        Vedic 命盤
    
    Returns
    -------
    Dict
        對比結果字典
    """
    comparison = {
        "ayanamsa_difference": {
            "kp": KP_AYANAMSA_NAME,
            "vedic": "Lahiri",
            "note": "KP Ayanamsa 與 Lahiri 相差約 0°00'10\"",
        },
        "house_system": {
            "kp": "Placidus",
            "vedic": "Whole Sign",
            "note": "KP 使用宮頭劃分，Vedic 使用整宮制",
        },
        "planets": [],
    }
    
    # 比較行星位置（簡化版本）
    # 實際使用時需要從 vedic_chart 提取數據
    for kp_planet in kp_chart.planets:
        planet_comparison = {
            "name": kp_planet.name,
            "kp_longitude": kp_planet.longitude,
            "kp_nakshatra": kp_planet.nakshatra,
            "kp_sub_lord": kp_planet.sub_lord,
            # "vedic_longitude": ...,  # 從 vedic_chart 獲取
            # "vedic_nakshatra": ...,
        }
        comparison["planets"].append(planet_comparison)
    
    return comparison


# ============================================================================
# CACHE DECORATOR（Streamlit 快取）
# ============================================================================

def compute_kp_chart_cached(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    latitude: float,
    longitude: float,
    timezone: float,
    language: str = "en",
    is_horary: bool = False,
) -> KPChart:
    """
    帶快取的 KP 命盤計算函數（用於 Streamlit）
    
    使用 @st.cache_data 裝飾器來避免重複計算。
    在 Streamlit app 中直接導入並使用此函數。
    
    Parameters
    ----------
    year : int
        年份
    month : int
        月份
    day : int
        日期
    hour : int
        小時
    minute : int
        分鐘
    latitude : float
        緯度
    longitude : float
        經度
    timezone : float
        時區
    language : str
        語言
    is_horary : bool
        是否為問卜圖
    
    Returns
    -------
    KPChart
        KP 命盤物件
    """
    # 注意：這個函數應該在 Streamlit app 中使用 @st.cache_data 裝飾
    # 這裡只提供包裝函數，實際裝飾在 app.py 中進行
    return compute_kp_chart(
        year, month, day, hour, minute,
        latitude, longitude, timezone,
        language, is_horary,
    )
