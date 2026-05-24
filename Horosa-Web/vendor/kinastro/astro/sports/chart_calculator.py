"""
起盤模組 (Chart Calculator)

同時生成：
1. Western Tropical 圖 (Regiomontanus 宮位制) — 依 Frawley 偏好
2. Vedic Sidereal 圖 (Lahiri Ayanamsa) + Navamsa (D9) — 依 Gambler's Dharma

基於 pyswisseph 計算行星位置、宮位、Ascendant 等。
"""

import swisseph as swe
from .models import (
    MatchInput, PlanetInfo, HouseInfo,
    WesternChartData, VedicPlanetInfo, VedicChartData,
)

# ============================================================
# 常量
# ============================================================

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

ZODIAC_GLYPHS = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓",
]

RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka",
    "Simha", "Kanya", "Tula", "Vrischika",
    "Dhanu", "Makara", "Kumbha", "Meena",
]

# Traditional rulers only (Frawley ignores outer planets)
TRADITIONAL_RULERS = {
    0: "Mars",      # Aries
    1: "Venus",     # Taurus
    2: "Mercury",   # Gemini
    3: "Moon",      # Cancer
    4: "Sun",       # Leo
    5: "Mercury",   # Virgo
    6: "Venus",     # Libra
    7: "Mars",      # Scorpio
    8: "Jupiter",   # Sagittarius
    9: "Saturn",    # Capricorn
    10: "Saturn",   # Aquarius
    11: "Jupiter",  # Pisces
}

# Vedic rulers (same as traditional)
VEDIC_RULERS = TRADITIONAL_RULERS.copy()

# Essential dignities (traditional)
DOMICILE = {
    "Sun": [4], "Moon": [3], "Mercury": [2, 5], "Venus": [1, 6],
    "Mars": [0, 7], "Jupiter": [8, 11], "Saturn": [9, 10],
}
EXALTATION = {
    "Sun": 0, "Moon": 1, "Mercury": 5, "Venus": 11,
    "Mars": 9, "Jupiter": 3, "Saturn": 6,
}
DETRIMENT = {
    "Sun": [10], "Moon": [9], "Mercury": [8, 11], "Venus": [0, 7],
    "Mars": [1, 6], "Jupiter": [2, 5], "Saturn": [3, 4],
}
FALL = {
    "Sun": 6, "Moon": 7, "Mercury": 11, "Venus": 5,
    "Mars": 3, "Jupiter": 9, "Saturn": 0,
}

# Planets we calculate (traditional 7 only for Frawley)
TRADITIONAL_PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
}

# Speed thresholds (Frawley's table)
SPEED_FAST = {
    "Moon": 14.167, "Mercury": 1.667, "Venus": 1.167,
    "Mars": 0.717, "Jupiter": 0.200, "Saturn": 0.100,
}
SPEED_SLOW = {
    "Moon": 12.250, "Mercury": 0.333, "Venus": 0.250,
    "Mars": 0.167, "Jupiter": 0.050, "Saturn": 0.033,
}

# Navamsa constants
PADA_SIZE_DEGREES = 10.0 / 3.0  # 3°20' per pada

# Nakshatras (27)
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]


# ============================================================
# 輔助函數
# ============================================================

def _normalize(deg: float) -> float:
    """標準化角度至 0-360"""
    return deg % 360.0


def _sign_index(deg: float) -> int:
    """黃經度數 → 星座索引 (0-11)"""
    return int(_normalize(deg) / 30.0)


def _sign_degree(deg: float) -> float:
    """黃經度數 → 星座內度數"""
    return _normalize(deg) % 30.0


def _get_essential_dignity(planet_name: str, sign_idx: int) -> str:
    """取得行星本質尊貴狀態"""
    if sign_idx in DOMICILE.get(planet_name, []):
        return "domicile"
    if EXALTATION.get(planet_name) == sign_idx:
        return "exaltation"
    if sign_idx in DETRIMENT.get(planet_name, []):
        return "detriment"
    if FALL.get(planet_name) == sign_idx:
        return "fall"
    return "peregrine"


def _find_house(lon: float, cusps: tuple) -> int:
    """判斷行星落入哪個宮位 (1-12)"""
    lon = _normalize(lon)
    for i in range(12):
        cusp_start = _normalize(cusps[i])
        cusp_end = _normalize(cusps[(i + 1) % 12])
        if cusp_start < cusp_end:
            if cusp_start <= lon < cusp_end:
                return i + 1
        else:  # crosses 0°
            if lon >= cusp_start or lon < cusp_end:
                return i + 1
    return 1


def _angle_diff(a: float, b: float) -> float:
    """計算兩角度最小差值 (0-180)"""
    d = abs(_normalize(a) - _normalize(b))
    return min(d, 360.0 - d)


def _navamsa_longitude(sidereal_lon: float) -> float:
    """計算 Navamsa (D9) 位置

    Each sign has 4 Navamsa padas of 3°20' each.
    Navamsa sign = (sign_index * 9 + pada_index) % 12
    """
    total_padas = int(sidereal_lon / PADA_SIZE_DEGREES)
    navamsa_sign = total_padas % 12
    remainder_in_pada = sidereal_lon - total_padas * PADA_SIZE_DEGREES
    # Map remainder proportionally into 30° of the navamsa sign
    navamsa_degree = (remainder_in_pada / PADA_SIZE_DEGREES) * 30.0
    return _normalize(navamsa_sign * 30.0 + navamsa_degree)


def _nakshatra_info(deg: float):
    """計算 Nakshatra 和 Pada"""
    deg = _normalize(deg)
    nak_span = 360.0 / 27.0  # 13°20'
    nak_idx = int(deg / nak_span)
    if nak_idx >= 27:
        nak_idx = 26
    pada_span = nak_span / 4.0  # 3°20'
    pada = int((deg - nak_idx * nak_span) / pada_span) + 1
    if pada > 4:
        pada = 4
    return nak_idx, pada


# ============================================================
# 西洋占星盤計算 (Regiomontanus)
# ============================================================

def compute_western_chart(match: MatchInput) -> WesternChartData:
    """計算西洋 Tropical 占星盤 (Regiomontanus 宮位制)

    依照 Frawley 的要求：
    - 使用 Regiomontanus 宮位制 (b'R')
    - 只計算傳統七星 (Sun-Saturn)
    - 計算 North/South Node
    """
    swe.set_ephe_path("")

    decimal_hour = match.hour + match.minute / 60.0 - match.timezone
    jd = swe.julday(match.year, match.month, match.day, decimal_hour)

    # Regiomontanus house system
    cusps, ascmc = swe.houses(jd, match.latitude, match.longitude, b'R')
    ascendant = _normalize(ascmc[0])
    midheaven = _normalize(ascmc[1])

    planets = []
    sun_lon = 0.0
    moon_lon = 0.0
    for name, pid in TRADITIONAL_PLANETS.items():
        result, _ = swe.calc_ut(jd, pid)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)

        if name == "Sun":
            sun_lon = lon
        if name == "Moon":
            moon_lon = lon

        planets.append(PlanetInfo(
            name=name,
            longitude=lon,
            latitude=lat,
            sign_index=idx,
            sign_name=ZODIAC_SIGNS[idx],
            sign_degree=_sign_degree(lon),
            house=_find_house(lon, cusps),
            retrograde=speed < 0,
            speed=speed,
            essential_dignity=_get_essential_dignity(name, idx),
        ))

    # North Node
    rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE)
    north_node_lon = _normalize(rahu_res[0])
    south_node_lon = _normalize(north_node_lon + 180.0)

    # Build houses
    houses = []
    for i in range(12):
        cusp = cusps[i]
        idx = _sign_index(cusp)
        lord = TRADITIONAL_RULERS[idx]
        h = HouseInfo(
            number=i + 1,
            cusp=cusp,
            sign_index=idx,
            sign_name=ZODIAC_SIGNS[idx],
            lord=lord,
            planets_in_house=[],
        )
        houses.append(h)

    for p in planets:
        houses[p.house - 1].planets_in_house.append(p.name)

    # Lot of Fortune (Frawley considers it unreliable, but compute for reference)
    is_day = sun_lon > cusps[0] if cusps[0] < cusps[6] else \
        (sun_lon > cusps[0] or sun_lon < cusps[6])
    lot_of_fortune = _normalize(ascendant + moon_lon - sun_lon) if is_day \
        else _normalize(ascendant + sun_lon - moon_lon)

    return WesternChartData(
        ascendant=ascendant,
        midheaven=midheaven,
        planets=planets,
        houses=houses,
        julian_day=jd,
        lot_of_fortune=lot_of_fortune,
        north_node_lon=north_node_lon,
        south_node_lon=south_node_lon,
    )


# ============================================================
# Vedic 占星盤計算 (Sidereal + Navamsa)
# ============================================================

def compute_vedic_chart(match: MatchInput) -> VedicChartData:
    """計算 Vedic Sidereal 占星盤 (Lahiri Ayanamsa) + Navamsa D9

    依照 Gambler's Dharma 的需求：
    - Rasi 圖 (D1)
    - Navamsa 圖 (D9)
    - 行星位置含 Rahu/Ketu
    """
    swe.set_ephe_path("")
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    decimal_hour = match.hour + match.minute / 60.0 - match.timezone
    jd = swe.julday(match.year, match.month, match.day, decimal_hour)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Sidereal house cusps (Placidus for Vedic, whole-sign is common but we
    # need cusps for cuspal-strength technique)
    cusps, ascmc = swe.houses_ex(jd, match.latitude, match.longitude,
                                 b"P", swe.FLG_SIDEREAL)
    ascendant = _normalize(ascmc[0])

    planets = []
    for name, pid in TRADITIONAL_PLANETS.items():
        result, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        nak_idx, pada = _nakshatra_info(lon)

        planets.append(VedicPlanetInfo(
            name=name,
            longitude=lon,
            rashi_index=idx,
            rashi_name=RASHI_NAMES[idx],
            rashi_lord=VEDIC_RULERS[idx],
            sign_degree=_sign_degree(lon),
            nakshatra=NAKSHATRAS[nak_idx],
            nakshatra_pada=pada,
            house=_find_house(lon, cusps),
            retrograde=speed < 0,
        ))

    # Rahu
    rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _normalize(rahu_res[0])
    idx = _sign_index(rahu_lon)
    nak_idx, pada = _nakshatra_info(rahu_lon)
    planets.append(VedicPlanetInfo(
        name="Rahu", longitude=rahu_lon,
        rashi_index=idx, rashi_name=RASHI_NAMES[idx],
        rashi_lord=VEDIC_RULERS[idx], sign_degree=_sign_degree(rahu_lon),
        nakshatra=NAKSHATRAS[nak_idx], nakshatra_pada=pada,
        house=_find_house(rahu_lon, cusps), retrograde=False,
    ))

    # Ketu
    ketu_lon = _normalize(rahu_lon + 180.0)
    idx = _sign_index(ketu_lon)
    nak_idx, pada = _nakshatra_info(ketu_lon)
    planets.append(VedicPlanetInfo(
        name="Ketu", longitude=ketu_lon,
        rashi_index=idx, rashi_name=RASHI_NAMES[idx],
        rashi_lord=VEDIC_RULERS[idx], sign_degree=_sign_degree(ketu_lon),
        nakshatra=NAKSHATRAS[nak_idx], nakshatra_pada=pada,
        house=_find_house(ketu_lon, cusps), retrograde=False,
    ))

    # Build Rasi houses
    houses = []
    for i in range(12):
        cusp = cusps[i]
        idx = _sign_index(cusp)
        houses.append(HouseInfo(
            number=i + 1, cusp=cusp,
            sign_index=idx, sign_name=RASHI_NAMES[idx],
            lord=VEDIC_RULERS[idx], planets_in_house=[],
        ))
    for p in planets:
        houses[p.house - 1].planets_in_house.append(p.name)

    # === Navamsa (D9) ===
    nav_asc = _navamsa_longitude(ascendant)
    nav_asc_idx = _sign_index(nav_asc)

    navamsa_planets = []
    for p in planets:
        nav_lon = _navamsa_longitude(p.longitude)
        idx = _sign_index(nav_lon)
        nak_idx, pada = _nakshatra_info(nav_lon)
        navamsa_planets.append(VedicPlanetInfo(
            name=p.name, longitude=nav_lon,
            rashi_index=idx, rashi_name=RASHI_NAMES[idx],
            rashi_lord=VEDIC_RULERS[idx], sign_degree=_sign_degree(nav_lon),
            nakshatra=NAKSHATRAS[nak_idx], nakshatra_pada=pada,
            house=0,  # Navamsa houses computed from nav ASC
            retrograde=p.retrograde,
        ))

    # Assign navamsa houses based on whole-sign from nav ASC
    for np in navamsa_planets:
        offset = (np.rashi_index - nav_asc_idx) % 12
        np.house = offset + 1

    return VedicChartData(
        ascendant=ascendant,
        asc_rashi_index=_sign_index(ascendant),
        planets=planets,
        houses=houses,
        navamsa_ascendant=nav_asc,
        navamsa_asc_rashi_index=nav_asc_idx,
        navamsa_planets=navamsa_planets,
        julian_day=jd,
        ayanamsa=ayanamsa,
    )


# ============================================================
# 工具函數
# ============================================================

def get_planet_by_name(planets: list, name: str):
    """根據名稱在行星列表中尋找行星"""
    for p in planets:
        if p.name == name:
            return p
    return None


def format_longitude(lon: float) -> str:
    """格式化黃經為 '度°分′ 星座' 格式"""
    idx = _sign_index(lon)
    deg = _sign_degree(lon)
    d = int(deg)
    m = int((deg - d) * 60)
    return f"{d}°{m:02d}′ {ZODIAC_SIGNS[idx]} {ZODIAC_GLYPHS[idx]}"


def format_vedic_longitude(lon: float) -> str:
    """格式化 Vedic 黃經"""
    idx = _sign_index(lon)
    deg = _sign_degree(lon)
    d = int(deg)
    m = int((deg - d) * 60)
    return f"{d}°{m:02d}′ {RASHI_NAMES[idx]}"
