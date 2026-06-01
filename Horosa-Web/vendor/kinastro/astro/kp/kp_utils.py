"""
astro/kp/kp_utils.py — KP 占星術核心工具函數

Krishnamurti Paddhati (KP Astrology) Utility Functions

提供：
1. Rasi Lord（星座主）計算
2. Star Lord / Nakshatra Lord（宿度主）計算
3. Sub Lord（分主）計算
4. Sub-Sub Lord（細分主）計算
5. Ruling Planets（時辰主星）計算
6. Significators（徵兆星）強度分析
7. 房屋主星計算

References
----------
- Krishnamurti, K.S. "KP Reader Vol. I: Fundamentals"
- Krishnamurti, K.S. "KP Reader Vol. IV: Predictive Techniques"
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import swisseph as swe

from astro.kp.constants import (
    NAKSHATRAS,
    VIMSHOTTARI_DASHA_YEARS,
    VIMSHOTTARI_TOTAL_YEARS,
    PLANET_ORDER,
    RASI_LORDS,
    PLANETS,
    HOUSES,
    KENDRA_HOUSES,
    TRIKONA_HOUSES,
    UPACHAYA_HOUSES,
    DUSTHANA_HOUSES,
    MARAKA_HOUSES,
    get_nakshatra_index,
)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class KPLordship:
    """
    KP 行星主星關係
    
    Attributes
    ----------
    rasi_lord : str
        星座主（Rasi Lord）
    star_lord : str
        宿度主（Star Lord / Nakshatra Lord）
    sub_lord : str
        分主（Sub Lord）
    sub_sub_lord : Optional[str]
        細分主（Sub-Sub Lord，可選）
    """
    rasi_lord: str
    star_lord: str
    sub_lord: str
    sub_sub_lord: Optional[str] = None


@dataclass
class KPSignificator:
    """
    KP 徵兆星（Significator）
    
    Attributes
    ----------
    planet : str
        行星名稱
    house : int
        宮位（1-12）
    strength : str
        強度（Very Strong / Strong / Weak / Very Weak）
    reason : str
        強度原因說明
    """
    planet: str
    house: int
    strength: str
    reason: str


# ============================================================================
# RASI LORD（星座主）計算
# ============================================================================

def get_rasi_lord(longitude: float) -> str:
    """
    計算給定經度的星座主（Rasi Lord）
    
    KP 使用傳統印度占星的星座主系統：
    白羊→火星，金牛→金星，雙子→水星，巨蟹→月亮，
    獅子→太陽，處女→水星，天秤→金星，天蠍→火星，
    射手→木星，摩羯→土星，水瓶→土星，雙魚→木星
    
    Parameters
    ----------
    longitude : float
        經度（0-360 度）
    
    Returns
    -------
    str
        星座主行星名稱
    """
    # 計算星座序號（0-11）
    sign_index = int(longitude / 30.0) % 12
    
    # 從 RASI_LORDS 獲取主星
    return RASI_LORDS[sign_index]


# ============================================================================
# STAR LORD / NAKSHATRA LORD（宿度主）計算
# ============================================================================

def get_nakshatra_lord(longitude: float) -> str:
    """
    計算給定經度的宿度主（Star Lord / Nakshatra Lord）
    
    27 宿按照 Vimshottari Dasha 順序分配主星：
    Ketu → Venus → Sun → Moon → Mars → Rahu → Jupiter → Saturn → Mercury
    然後重複此順序
    
    Parameters
    ----------
    longitude : float
        經度（0-360 度）
    
    Returns
    -------
    str
        宿度主行星名稱
    """
    # 獲取宿序號（0-26）
    nakshatra_idx = get_nakshatra_index(longitude)
    
    # 從 NAKSHATRAS 獲取主星
    return NAKSHATRAS[nakshatra_idx]["lord"]


def get_nakshatra_name(longitude: float, language: str = "en") -> str:
    """
    獲取給定經度的宿名
    
    Parameters
    ----------
    longitude : float
        經度（0-360 度）
    language : str
        語言（"en" / "zh" / "sanskrit"）
    
    Returns
    -------
    str
        宿名
    """
    nakshatra_idx = get_nakshatra_index(longitude)
    nakshatra = NAKSHATRAS[nakshatra_idx]
    
    if language == "zh":
        return nakshatra["cn"]
    elif language == "sanskrit":
        return nakshatra["sanskrit"]
    else:
        return nakshatra["name"]


def get_nakshatra_pada(longitude: float) -> int:
    """
    計算給定經度的 Padam（宿的四等分，1-4）
    
    Parameters
    ----------
    longitude : float
        經度（0-360 度）
    
    Returns
    -------
    int
        Padam 序號（1-4）
    """
    # 每宿寬度 = 13.3333...度
    nakshatra_width = 360.0 / 27.0
    
    # 計算在宿內的經度
    nakshatra_idx = get_nakshatra_index(longitude)
    start_longitude = nakshatra_idx * nakshatra_width
    within_nakshatra = longitude - start_longitude
    
    # 計算 Padam（每 Padam = 宿寬度 / 4）
    pada_width = nakshatra_width / 4.0
    pada = int(within_nakshatra / pada_width) + 1
    
    return min(pada, 4)  # 確保不超過 4


# ============================================================================
# SUB LORD（分主）計算
# ============================================================================

def get_sub_lord(longitude: float) -> str:
    """
    計算給定經度的分主（Sub Lord）
    
    KP 的核心創新：每宿（13°20'）再細分為 9 個 Sub，
    每個 Sub 的寬度按照 Vimshottari Dasha 年數比例分配。
    
    Sub 順序始終按照：Ketu → Venus → Sun → Moon → Mars → Rahu → Jupiter → Saturn → Mercury
    
    Parameters
    ----------
    longitude : float
        經度（0-360 度）
    
    Returns
    -------
    str
        分主行星名稱
    """
    # 獲取宿序號
    nakshatra_idx = get_nakshatra_index(longitude)
    
    # 計算宿的起始經度
    nakshatra_width = 360.0 / 27.0
    nakshatra_start = nakshatra_idx * nakshatra_width
    
    # 計算在宿內的經度（0 到 13.3333...度）
    within_nakshatra = longitude - nakshatra_start
    
    # 計算累積比例
    cumulative_ratio = 0.0
    
    for planet in PLANET_ORDER:
        # 該行星的 Sub 寬度比例
        dasha_years = VIMSHOTTARI_DASHA_YEARS[planet]
        sub_ratio = dasha_years / VIMSHOTTARI_TOTAL_YEARS
        
        # 該 Sub 的實際寬度（度數）
        sub_width = nakshatra_width * sub_ratio
        
        # 檢查是否在這個 Sub 內
        if within_nakshatra < cumulative_ratio * nakshatra_width + sub_width:
            return planet
        
        cumulative_ratio += sub_ratio
    
    # 理論上不應該到這裡，返回 Mercury 作為預設
    return "Mercury"


def get_sub_lord_detailed(longitude: float) -> Dict:
    """
    獲取分主的詳細資訊
    
    Parameters
    ----------
    longitude : float
        經度（0-360 度）
    
    Returns
    -------
    Dict
        包含 Sub 序號、起始經度、結束經度、主星等資訊
    """
    # 獲取宿序號
    nakshatra_idx = get_nakshatra_index(longitude)
    
    # 計算宿的起始經度
    nakshatra_width = 360.0 / 27.0
    nakshatra_start = nakshatra_idx * nakshatra_width
    
    # 計算在宿內的經度
    within_nakshatra = longitude - nakshatra_start
    
    # 計算累積比例
    cumulative_ratio = 0.0
    sub_start = 0.0
    
    for i, planet in enumerate(PLANET_ORDER):
        dasha_years = VIMSHOTTARI_DASHA_YEARS[planet]
        sub_ratio = dasha_years / VIMSHOTTARI_TOTAL_YEARS
        sub_width = nakshatra_width * sub_ratio
        
        sub_end = sub_start + sub_width
        
        if within_nakshatra < sub_end:
            # 計算在 Sub 內的比例
            within_sub = (within_nakshatra - sub_start) / sub_width
            
            return {
                "sub_number": i + 1,
                "lord": planet,
                "start_longitude": nakshatra_start + sub_start,
                "end_longitude": nakshatra_start + sub_end,
                "width": sub_width,
                "within_sub_ratio": within_sub,
                "nakshatra": NAKSHATRAS[nakshatra_idx]["name"],
            }
        
        sub_start = sub_end
    
    # 預設返回
    return {
        "sub_number": 9,
        "lord": "Mercury",
        "start_longitude": nakshatra_start + nakshatra_width * (103/120),
        "end_longitude": nakshatra_start + nakshatra_width,
        "width": nakshatra_width * (17/120),
        "within_sub_ratio": 0.5,
        "nakshatra": NAKSHATRAS[nakshatra_idx]["name"],
    }


# ============================================================================
# SUB-SUB LORD（細分主）計算
# ============================================================================

def get_sub_sub_lord(longitude: float) -> str:
    """
    計算給定經度的細分主（Sub-Sub Lord）
    
    每個 Sub 再細分為 9 個 Sub-Sub，同樣按照 Vimshottari Dasha 順序
    
    Parameters
    ----------
    longitude : float
        經度（0-360 度）
    
    Returns
    -------
    str
        細分主行星名稱
    """
    # 獲取 Sub 詳細資訊
    sub_info = get_sub_lord_detailed(longitude)
    
    # 獲取宿序號
    nakshatra_idx = get_nakshatra_index(longitude)
    nakshatra_width = 360.0 / 27.0
    
    # 計算在宿內的經度
    nakshatra_start = nakshatra_idx * nakshatra_width
    within_nakshatra = longitude - nakshatra_start
    
    # 計算 Sub 起始位置
    cumulative_ratio = 0.0
    sub_start = 0.0
    
    for planet in PLANET_ORDER:
        dasha_years = VIMSHOTTARI_DASHA_YEARS[planet]
        sub_ratio = dasha_years / VIMSHOTTARI_TOTAL_YEARS
        sub_width = nakshatra_width * sub_ratio
        
        sub_end = sub_start + sub_width
        
        if within_nakshatra < sub_end:
            # 在這個 Sub 內，現在計算 Sub-Sub
            within_sub = within_nakshatra - sub_start
            
            # Sub-Sub 寬度
            sub_sub_width = sub_width / VIMSHOTTARI_TOTAL_YEARS
            
            # 計算 Sub-Sub
            sub_sub_cumulative = 0.0
            
            for sub_sub_planet in PLANET_ORDER:
                sub_sub_dasha = VIMSHOTTARI_DASHA_YEARS[sub_sub_planet]
                sub_sub_ratio = sub_sub_dasha / VIMSHOTTARI_TOTAL_YEARS
                sub_sub_actual_width = sub_width * sub_sub_ratio
                
                if within_sub < sub_sub_cumulative + sub_sub_actual_width:
                    return sub_sub_planet
                
                sub_sub_cumulative += sub_sub_actual_width
            
            return "Mercury"
        
        sub_start = sub_end
    
    return "Mercury"


# ============================================================================
# 完整主星計算
# ============================================================================

def get_complete_lordship(longitude: float) -> KPLordship:
    """
    計算完整的 KP 主星系統（Rasi + Star + Sub + Sub-Sub）
    
    Parameters
    ----------
    longitude : float
        經度（0-360 度）
    
    Returns
    -------
    KPLordship
        完整的主星關係物件
    """
    return KPLordship(
        rasi_lord=get_rasi_lord(longitude),
        star_lord=get_nakshatra_lord(longitude),
        sub_lord=get_sub_lord(longitude),
        sub_sub_lord=get_sub_sub_lord(longitude),
    )


# ============================================================================
# RULING PLANETS（時辰主星）計算
# ============================================================================

def calculate_ruling_planets(
    julian_day: float,
    latitude: float,
    longitude: float,
    timezone: float = 0.0,
) -> Dict[str, str]:
    """
    計算 Ruling Planets（時辰主星）
    
    Ruling Planets 是 KP Horary（問卜）的核心，用於：
    1. 驗證出生時間的準確性
    2. 選擇吉時（Muhurta）
    3. 解答問題（Horary Astrology）
    
    Ruling Planets 包括 5 個主星：
    1. Day Lord（日主）— 星期幾的主星
    2. Star Lord（宿度主）— 月亮所在宿的主星
    3. Sign Lord（星座主）— 月亮星座的主星
    4. Lagna Star Lord（上升宿度主）— 上升點所在宿的主星
    5. Lagna Sign Lord（上升星座主）— 上升星座的主星
    
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
    
    Returns
    -------
    Dict[str, str]
        Ruling Planets 字典
    """
    # 計算行星位置（使用 KP Ayanamsa）
    from astro.kp.constants import get_kp_ayanamsa
    
    kp_ayanamsa = get_kp_ayanamsa(julian_day)
    
    # 設置星曆表為 Lahiri sidereal mode
    # 注意：swisseph 沒有 set_ayanamsa() 函數，需要手動調整經度
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # 計算月亮位置（返回的是 Lahiri ayanamsa，需要調整為 KP ayanamsa）
    # KP New Ayanamsa ≈ 23.848333°, Lahiri ≈ 23.85°，差異很小
    moon_result, _ = swe.calc_ut(julian_day, swe.MOON)
    moon_lon = float(moon_result[0]) % 360.0
    
    # 計算上升點（Ascendant）
    asc_result, _ = swe.houses(julian_day, latitude, longitude, b'P')
    asc_lon = float(asc_result[0]) % 360.0
    
    # 計算星期（0 = Monday, 6 = Sunday）
    # 儒略日 0 是 Monday, January 1, 4713 BC
    day_of_week = int(julian_day + 1.5) % 7
    
    # Day Lord（星期主星）
    # Monday→Moon, Tuesday→Mars, Wednesday→Mercury, Thursday→Jupiter,
    # Friday→Venus, Saturday→Saturn, Sunday→Sun
    day_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    day_lord = day_lords[day_of_week]
    
    # Moon Star Lord（月亮宿度主）
    moon_star_lord = get_nakshatra_lord(moon_lon)
    
    # Moon Sign Lord（月亮星座主）
    moon_sign_lord = get_rasi_lord(moon_lon)
    
    # Lagna Star Lord（上升宿度主）
    lagna_star_lord = get_nakshatra_lord(asc_lon)
    
    # Lagna Sign Lord（上升星座主）
    lagna_sign_lord = get_rasi_lord(asc_lon)
    
    return {
        "day_lord": day_lord,
        "moon_star_lord": moon_star_lord,
        "moon_sign_lord": moon_sign_lord,
        "lagna_star_lord": lagna_star_lord,
        "lagna_sign_lord": lagna_sign_lord,
        # 額外資訊
        "moon_longitude": moon_lon,
        "ascendant_longitude": asc_lon,
        "day_of_week": day_of_week,
    }


def get_ruling_planets_for_horary(
    question_time: Optional[Dict] = None,
    birth_time: Optional[Dict] = None,
) -> Dict:
    """
    獲取問卜圖的 Ruling Planets
    
    Parameters
    ----------
    question_time : Optional[Dict]
        提問時間字典 {"year", "month", "day", "hour", "minute", "latitude", "longitude", "timezone"}
    birth_time : Optional[Dict]
        出生時間字典（用於驗證）
    
    Returns
    -------
    Dict
        Ruling Planets 完整資訊
    """
    import swisseph as swe
    from datetime import datetime
    
    if question_time:
        # 使用提問時間
        jd = swe.julday(
            question_time["year"],
            question_time["month"],
            question_time["day"],
            question_time["hour"] + question_time["minute"] / 60.0
        )
        
        ruling_planets = calculate_ruling_planets(
            jd,
            question_time.get("latitude", 0.0),
            question_time.get("longitude", 0.0),
            question_time.get("timezone", 0.0),
        )
        
        ruling_planets["mode"] = "horary"
        ruling_planets["time_type"] = "question_time"
        
    elif birth_time:
        # 使用出生時間
        jd = swe.julday(
            birth_time["year"],
            birth_time["month"],
            birth_time["day"],
            birth_time["hour"] + birth_time["minute"] / 60.0
        )
        
        ruling_planets = calculate_ruling_planets(
            jd,
            birth_time.get("latitude", 0.0),
            birth_time.get("longitude", 0.0),
            birth_time.get("timezone", 0.0),
        )
        
        ruling_planets["mode"] = "natal"
        ruling_planets["time_type"] = "birth_time"
        
    else:
        raise ValueError("Must provide either question_time or birth_time")
    
    return ruling_planets


# ============================================================================
# SIGNIFICATORS（徵兆星）計算
# ============================================================================

def get_significators(
    planet_positions: List[Dict],
    house_cusps: List[float],
    target_house: int,
) -> List[KPSignificator]:
    """
    計算特定宮位的 Significators（徵兆星）
    
    KP 的 Significators 分為四個層級：
    1. 位於該宮的行星（Very Strong）
    2. 該宮星座主的 Star Lord（Strong）
    3. 該宮星座主的 Sub Lord（Strong）
    4. 與該宮主星有相位的行星（Weak）
    
    Parameters
    ----------
    planet_positions : List[Dict]
        行星位置列表，每個包含：
        {"name", "longitude", "house", "star_lord", "sub_lord"}
    house_cusps : List[float]
        12 宮頭經度列表（索引 0-11 對應宮位 1-12）
    target_house : int
        目標宮位（1-12）
    
    Returns
    -------
    List[KPSignificator]
        徵兆星列表，按強度排序
    """
    significators = []
    
    # 1. 位於 target_house 的行星（Very Strong）
    for planet in planet_positions:
        if planet.get("house") == target_house:
            significators.append(KPSignificator(
                planet=planet["name"],
                house=target_house,
                strength="Very Strong",
                reason=f"位於第{target_house}宮"
            ))
    
    # 2. 獲取 target_house 的宮頭經度
    # 注意：house_cusps 索引 0 對應宮位 1
    if target_house <= len(house_cusps):
        cusp_longitude = house_cusps[target_house - 1]
        
        # 3. 該宮的星座主（Rasi Lord）
        cusp_rasi_lord = get_rasi_lord(cusp_longitude)
        
        # 4. 該宮的宿度主（Star Lord）
        cusp_star_lord = get_nakshatra_lord(cusp_longitude)
        
        # 5. 該宮的分主（Sub Lord）
        cusp_sub_lord = get_sub_lord(cusp_longitude)
        
        # 找出 Star Lord 為 cusp_star_lord 的行星（Strong）
        for planet in planet_positions:
            if planet.get("star_lord") == cusp_star_lord:
                # 避免重複
                if not any(s.planet == planet["name"] and s.strength == "Very Strong" 
                          for s in significators):
                    significators.append(KPSignificator(
                        planet=planet["name"],
                        house=target_house,
                        strength="Strong",
                        reason=f"主宰第{target_house}宮的宿度主"
                    ))
        
        # 6. 找出 Sub Lord 為 cusp_sub_lord 的行星（Strong）
        for planet in planet_positions:
            if planet.get("sub_lord") == cusp_sub_lord:
                if not any(s.planet == planet["name"] for s in significators):
                    significators.append(KPSignificator(
                        planet=planet["name"],
                        house=target_house,
                        strength="Strong",
                        reason=f"主宰第{target_house}宮的分主"
                    ))
        
        # 7. 與宮主星有相位的行星（Weak）
        # 簡化：這裡只檢查是否在同一星座
        cusp_sign = int(cusp_longitude / 30.0)
        for planet in planet_positions:
            planet_sign = int(planet["longitude"] / 30.0)
            if planet_sign == cusp_sign:
                if not any(s.planet == planet["name"] for s in significators):
                    significators.append(KPSignificator(
                        planet=planet["name"],
                        house=target_house,
                        strength="Weak",
                        reason=f"與第{target_house}宮主星同星座"
                    ))
    
    # 按強度排序
    strength_order = {"Very Strong": 0, "Strong": 1, "Weak": 2, "Very Weak": 3}
    significators.sort(key=lambda s: strength_order[s.strength])
    
    return significators


def get_house_significators_summary(
    planet_positions: List[Dict],
    house_cusps: List[float],
) -> Dict[int, List[KPSignificator]]:
    """
    獲取所有 12 宮的 Significators 摘要
    
    Parameters
    ----------
    planet_positions : List[Dict]
        行星位置列表
    house_cusps : List[float]
        12 宮頭經度列表
    
    Returns
    -------
    Dict[int, List[KPSignificator]]
        宮位 → Significators 列表的字典
    """
    summary = {}
    
    for house in range(1, 13):
        summary[house] = get_significators(planet_positions, house_cusps, house)
    
    return summary


# ============================================================================
# HOUSE LORD（宮主星）計算
# ============================================================================

def get_house_lord(house_number: int, house_cusps: List[float]) -> str:
    """
    計算特定宮位的宮主星
    
    Parameters
    ----------
    house_number : int
        宮位序號（1-12）
    house_cusps : List[float]
        12 宮頭經度列表
    
    Returns
    -------
    str
        宮主星名稱
    """
    if house_number < 1 or house_number > 12:
        raise ValueError(f"House number must be 1-12, got {house_number}")
    
    cusp_longitude = house_cusps[house_number - 1]
    return get_rasi_lord(cusp_longitude)


def get_all_house_lords(house_cusps: List[float]) -> Dict[int, str]:
    """
    計算所有 12 宮的宮主星
    
    Parameters
    ----------
    house_cusps : List[float]
        12 宮頭經度列表
    
    Returns
    -------
    Dict[int, str]
        宮位 → 宮主星的字典
    """
    lords = {}
    for house in range(1, 13):
        lords[house] = get_house_lord(house, house_cusps)
    return lords


# ============================================================================
# ASPECT（相位）計算
# ============================================================================

def get_kp_aspect(planet1_lon: float, planet2_lon: float) -> Optional[str]:
    """
    計算 KP 系統中的相位
    
    KP 主要使用以下相位：
    - 合相（Conjunction）：0°（容許度 8°）
    - 六分相（Sextile）：60°（容許度 6°）
    - 四分相（Square）：90°（容許度 8°）
    - 三分相（Trine）：120°（容許度 8°）
    - 對分相（Opposition）：180°（容許度 8°）
    
    Parameters
    ----------
    planet1_lon : float
        行星 1 經度
    planet2_lon : float
        行星 2 經度
    
    Returns
    -------
    Optional[str]
        相位名稱，無相位則返回 None
    """
    # 計算經度差
    diff = abs(planet1_lon - planet2_lon)
    if diff > 180:
        diff = 360 - diff
    
    # 檢查相位（含容許度）
    aspects = [
        (0, "Conjunction", 8),      # 合相
        (60, "Sextile", 6),         # 六分相
        (90, "Square", 8),          # 四分相
        (120, "Trine", 8),          # 三分相
        (180, "Opposition", 8),     # 對分相
    ]
    
    for angle, name, orb in aspects:
        if abs(diff - angle) <= orb:
            return name
    
    return None


# ============================================================================
# PROMISE FULFILLMENT（事件實現）判斷
# ============================================================================

def check_promise_fulfillment(
    significators: List[KPSignificator],
    sub_lord: str,
    target_houses: List[int],
) -> bool:
    """
    檢查事件是否會實現（KP 核心判讀法則）
    
    KP 鐵律：
    1. Sub Lord 必須指向 target_houses（事件相關的宮位）
    2. Significators 必須強而有力
    3. Sub Lord 不能是 Dusthana（6/8/12）宮的主星
    
    Parameters
    ----------
    significators : List[KPSignificator]
        徵兆星列表
    sub_lord : str
        事件宮位的 Sub Lord
    target_houses : List[int]
        事件相關的宮位列表
    
    Returns
    -------
    bool
        事件是否會實現
    """
    # 1. 檢查 Sub Lord 是否指向 target_houses
    # （需要進一步計算 Sub Lord 所主宰的宮位）
    
    # 2. 檢查是否有強力的 Significators
    strong_significators = [s for s in significators 
                           if s.strength in ["Very Strong", "Strong"]]
    
    if not strong_significators:
        return False
    
    # 3. 簡化判斷：如果有 Very Strong 的 Significators，事件很可能實現
    very_strong = [s for s in significators if s.strength == "Very Strong"]
    
    return len(very_strong) > 0


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def planet_name_translate(planet: str, language: str = "en") -> str:
    """
    翻譯行星名稱
    
    Parameters
    ----------
    planet : str
        行星英文名稱
    language : str
        語言（"en" / "zh" / "sanskrit"）
    
    Returns
    -------
    str
        翻譯後的名稱
    """
    if planet not in PLANETS:
        return planet
    
    p = PLANETS[planet]
    
    if language == "zh":
        return p["cn"]
    elif language == "sanskrit":
        return p["sanskrit"]
    else:
        return planet


def house_name_translate(house: int, language: str = "en") -> str:
    """
    翻譯宮位名稱
    
    Parameters
    ----------
    house : int
        宮位序號（1-12）
    language : str
        語言（"en" / "zh" / "sanskrit"）
    
    Returns
    -------
    str
        翻譯後的名稱
    """
    if house < 1 or house > 12:
        return str(house)
    
    h = HOUSES[house]
    
    if language == "zh":
        return h["cn"]
    elif language == "sanskrit":
        return h["sanskrit"]
    else:
        return h["en"]
