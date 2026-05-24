"""
astro/sassanian/sassanian_astronomy.py — 薩珊天文計算模組

Sassanian Astronomy and Astrological Calculations
基於薩珊王朝天文學傳統（3-7 世紀）

References
----------
- Al-Biruni, "The Chronology of Ancient Nations" (tr. Sachau, 1879)
- Pingree, D. (1963). "Classical and Byzantine Astrology in Sassanian Persia"
- Greater Bundahishn (Iranian Bundahishn, tr. Anklesaria, 1956)
- Dorotheus of Sidon, Pahlavi translation (Pingree, 1976)
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import swisseph as swe
from datetime import datetime
import json
import os

# 獲取當前檔案所在目錄
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass
class SassanianPlanetPosition:
    """薩珊行星位置資料結構"""
    name: str
    name_pahlavi: str
    longitude_tropical: float  # 回歸黃道經度
    longitude_sidereal: float  # 恆星黃道經度（薩珊 Ayanamsa）
    latitude: float
    house: int  # 整宮制宮位
    sign: str
    sign_pahlavi: str
    is_retrograde: bool
    speed: float


def calculate_sassanian_ayanamsa(julian_day: float) -> float:
    """
    計算薩珊 Ayanamsa（歲差修正值）

    薩珊 Ayanamsa 基於 Al-Biruni 記載和現代重建，約為 22° 左右
    不同於現代 Lahiri (23.85°) 或 Fagan-Bradley (24.04°)

    Parameters
    ----------
    julian_day : float
        儒略日

    Returns
    -------
    float
        薩珊 Ayanamsa 值（度數）

    References
    ----------
    - Al-Biruni, "The Chronology of Ancient Nations"
    - Pingree (1963) "Classical and Byzantine Astrology in Sassanian Persia"
    """
    # 薩珊 Ayanamsa 基於 J2000 起算點約 22°
    # 使用簡單的線性歲差模型
    # 參考：Al-Biruni 記載薩珊時期春分點在白羊座 0° 前約 22°

    # J2000 儒略日
    j2000 = 2451545.0

    # 從 J2000 起算的年數
    years_from_j2000 = (julian_day - j2000) / 365.25

    # 基礎 Ayanamsa (J2000 時約 22°)
    # 根據 Pingree 重建，薩珊 Ayanamsa 在 500 CE 約為 21.5°
    base_ayanamsa = 22.0

    # 歲差率：約 50.3 角秒/年 = 0.01397°/年
    precession_rate = 0.01397

    ayanamsa = base_ayanamsa + (years_from_j2000 * precession_rate)

    return ayanamsa % 360


def get_royal_stars_positions(julian_day: float) -> Dict[str, Dict]:
    """
    獲取四顆皇家恆星的位置

    四顆皇家恆星在薩珊占星中具有核心地位：
    - Tascheter (Aldebaran) - 春分點守護者
    - Vanand (Regulus) - 夏分點守護者
    - Satevis (Antares) - 秋分點守護者
    - Hastorang (Fomalhaut) - 冬至點守護者

    Parameters
    ----------
    julian_day : float
        儒略日

    Returns
    -------
    Dict[str, Dict]
        四顆皇家恆星的位置資訊

    References
    ----------
    - Greater Bundahishn, Chapter II
    - Al-Biruni, "The Chronology of Ancient Nations"
    """
    # 載入皇家恆星資料
    royal_stars_path = os.path.join(_CURRENT_DIR, "data", "royal_stars.json")
    with open(royal_stars_path, "r", encoding="utf-8") as f:
        royal_stars_data = json.load(f)

    result = {}

    for star_name, star_data in royal_stars_data["royal_stars"].items():
        # 計算薩珊 Ayanamsa
        ayanamsa = calculate_sassanian_ayanamsa(julian_day)

        # 薩珊恆星經度（固定位置，基於古代觀測）
        sassanian_longitude = star_data["sassanian_longitude"]

        # 現代恆星經度（考慮自行）
        # 使用 swisseph 計算恆星位置
        star_id = star_name.lower()
        try:
            # swisseph 恆星計算
            lon, lat, dist = swe.fixstar_ut(star_id, julian_day, flag=swe.FLG_SWIEPH)
            modern_longitude = lon % 360
        except:
            modern_longitude = star_data["modern_longitude"]

        result[star_name] = {
            "name_en": star_data["name_en"],
            "name_cn": star_data["name_cn"],
            "name_pahlavi": star_data["name_pahlavi"],
            "sassanian_longitude": sassanian_longitude,
            "modern_longitude": modern_longitude,
            "constellation": star_data["constellation"],
            "meaning_en": star_data["meaning_en"],
            "meaning_cn": star_data["meaning_cn"],
            "element": star_data["element"],
            "nature": star_data["nature"],
            "ruling_planet": star_data["ruling_planet"],
            "orb": 5.0  # 5° 容許度用於判斷合相
        }

    return result


def compute_sassanian_planet_positions(
    year: int,
    month: int,
    day: int,
    hour: float,
    minute: float,
    longitude: float,
    latitude: float,
    timezone: float,
    ayanamsa_mode: str = "sassanian"
) -> List[SassanianPlanetPosition]:
    """
    計算薩珊行星位置（使用整宮制和薩珊 Ayanamsa）

    Parameters
    ----------
    year : int
        出生年份
    month : int
        出生月份
    day : int
        出生日期
    hour : float
        出生小時
    minute : float
        出生分鐘
    longitude : float
        出生地經度
    latitude : float
        出生地緯度
    timezone : float
        時區
    ayanamsa_mode : str
        Ayanamsa 模式，預設 "sassanian"

    Returns
    -------
    List[SassanianPlanetPosition]
        薩珊行星位置列表

    References
    ----------
    - Dorotheus of Sidon, Pahlavi translation
    - Greater Bundahishn
    """
    # 載入 Pahlavi 名稱
    pahlavi_path = os.path.join(_CURRENT_DIR, "data", "pahlavi_names.json")
    with open(pahlavi_path, "r", encoding="utf-8") as f:
        pahlavi_data = json.load(f)

    # 計算儒略日
    julian_day = swe.julday(year, month, day, hour + minute / 60.0)

    # 計算薩珊 Ayanamsa
    ayanamsa = calculate_sassanian_ayanamsa(julian_day)

    # 設置薩珊 Ayanamsa
    swe.set_sid_mode(swe.SIDM_USER, ayanamsa, 0)

    # 行星列表
    planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    planet_ids = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
    }

    # 計算上升點（Ascendant）
    # 使用 swe.houses 獲取上升點
    cusps, ascmc = swe.houses(julian_day, latitude, longitude, b"P")
    asc_longitude = ascmc[0] % 360  # ascmc[0] = Ascendant
    asc_sidereal = (asc_longitude - ayanamsa) % 360

    # 整宮制：上升點所在星座為第 1 宮
    asc_sign_index = int(asc_sidereal // 30)

    planet_positions = []

    for planet_name in planets:
        planet_id = planet_ids[planet_name]

        # 計算行星位置（回歸黃道）
        # swe.calc_ut 回傳 (result_array, extra_info)，參數順序：(jd, planet_id, flag)
        calc_result, _ = swe.calc_ut(julian_day, planet_id, swe.FLG_SWIEPH)
        lon = calc_result[0]  # 經度
        lat = calc_result[1]  # 緯度
        dist = calc_result[2]  # 距離
        speed_lon = calc_result[3]  # 經度速度

        # 回歸黃道經度
        longitude_tropical = lon % 360

        # 薩珊恆星黃道經度
        longitude_sidereal = (longitude_tropical - ayanamsa) % 360

        # 判斷逆行
        is_retrograde = speed_lon < 0

        # 整宮制宮位計算
        # 行星所在星座相對於上升星座的位置
        planet_sign_index = int(longitude_sidereal // 30)
        house = ((planet_sign_index - asc_sign_index) % 12) + 1

        # 獲取星座名稱
        zodiac_signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        sign = zodiac_signs[planet_sign_index]

        # 獲取 Pahlavi 名稱
        pahlavi_name = pahlavi_data["planets"][planet_name]["pahlavi"]
        sign_pahlavi = pahlavi_data["zodiac_signs"][sign]["pahlavi"]

        planet_positions.append(SassanianPlanetPosition(
            name=planet_name,
            name_pahlavi=pahlavi_name,
            longitude_tropical=longitude_tropical,
            longitude_sidereal=longitude_sidereal,
            latitude=lat,
            house=house,
            sign=sign,
            sign_pahlavi=sign_pahlavi,
            is_retrograde=is_retrograde,
            speed=speed_lon
        ))

    return planet_positions


def get_sassanian_houses(
    year: int,
    month: int,
    day: int,
    hour: float,
    minute: float,
    longitude: float,
    latitude: float,
    timezone: float
) -> List[Dict]:
    """
    計算薩珊整宮制宮位

    薩珊占星使用整宮制（Whole Sign Houses）：
    - 上升點所在星座為第 1 宮
    - 每個星座完整佔據一個宮位
    - 不考慮宮位大小差異

    Parameters
    ----------
    year : int
        出生年份
    month : int
        出生月份
    day : int
        出生日期
    hour : float
        出生小時
    minute : float
        出生分鐘
    longitude : float
        出生地經度
    latitude : float
        出生地緯度
    timezone : float
        時區

    Returns
    -------
    List[Dict]
        12 個宮位的資訊

    References
    ----------
    - Dorotheus of Sidon, Pahlavi translation
    - Pingree (1976)
    """
    # 載入 Pahlavi 名稱
    pahlavi_path = os.path.join(_CURRENT_DIR, "data", "pahlavi_names.json")
    with open(pahlavi_path, "r", encoding="utf-8") as f:
        pahlavi_data = json.load(f)

    # 計算儒略日
    julian_day = swe.julday(year, month, day, hour + minute / 60.0)

    # 計算薩珊 Ayanamsa
    ayanamsa = calculate_sassanian_ayanamsa(julian_day)

    # 計算上升點
    # 使用 swe.houses 獲取上升點
    cusps, ascmc = swe.houses(julian_day, latitude, longitude, b"P")
    asc_longitude = ascmc[0] % 360  # ascmc[0] = Ascendant
    asc_sidereal = (asc_longitude - ayanamsa) % 360

    # 上升點所在星座索引
    asc_sign_index = int(asc_sidereal // 30)

    # 星座名稱
    zodiac_signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    # 宮位意義（Pahlavi）
    house_meanings = {
        1: {"pahlavi": "Jan", "meaning_en": "Life, Body", "meaning_cn": "生命、身體"},
        2: {"pahlavi": "Darah", "meaning_en": "Wealth", "meaning_cn": "財富"},
        3: {"pahlavi": "Bradar", "meaning_en": "Siblings", "meaning_cn": "兄弟姐妹"},
        4: {"pahlavi": "Pidar", "meaning_en": "Father, Home", "meaning_cn": "父親、家園"},
        5: {"pahlavi": "Farzand", "meaning_en": "Children", "meaning_cn": "子女"},
        6: {"pahlavi": "Bimar", "meaning_en": "Illness", "meaning_cn": "疾病"},
        7: {"pahlavi": "Zan", "meaning_en": "Spouse", "meaning_cn": "配偶"},
        8: {"pahlavi": "Marg", "meaning_en": "Death", "meaning_cn": "死亡"},
        9: {"pahlavi": "Keshvar", "meaning_en": "Travel", "meaning_cn": "旅行"},
        10: {"pahlavi": "Kar", "meaning_en": "Career", "meaning_cn": "事業"},
        11: {"pahlavi": "Dust", "meaning_en": "Friends", "meaning_cn": "朋友"},
        12: {"pahlavi": "Dushman", "meaning_en": "Enemies", "meaning_cn": "敵人"},
    }

    houses = []

    for i in range(12):
        # 整宮制：第 i+1 宮對應上升星座後的第 i 個星座
        sign_index = (asc_sign_index + i) % 12
        sign = zodiac_signs[sign_index]
        sign_start = sign_index * 30
        sign_end = (sign_index + 1) * 30

        houses.append({
            "house_number": i + 1,
            "sign": sign,
            "sign_pahlavi": pahlavi_data["zodiac_signs"][sign]["pahlavi"],
            "longitude_start": sign_start,
            "longitude_end": sign_end,
            "meaning_pahlavi": house_meanings[i + 1]["pahlavi"],
            "meaning_en": house_meanings[i + 1]["meaning_en"],
            "meaning_cn": house_meanings[i + 1]["meaning_cn"],
        })

    return houses


# 測試用歷史星盤資料（281 CE 和 381 CE）
HISTORICAL_HOROSCOPES = {
    "281_CE": {
        "date": datetime(281, 3, 15, 12, 0),
        "location": {"longitude": 44.5, "latitude": 33.3, "timezone": 3.0},  # 泰西封 Ctesiphon
        "description": "Sassanian example horoscope from 281 CE (Dorotheus Pahlavi)",
        "source": "Pingree (1976), Dorotheus of Sidon Pahlavi translation"
    },
    "381_CE": {
        "date": datetime(381, 7, 22, 6, 0),
        "location": {"longitude": 44.5, "latitude": 33.3, "timezone": 3.0},  # 泰西封 Ctesiphon
        "description": "Sassanian example horoscope from 381 CE",
        "source": "Pingree (1976), Dorotheus of Sidon Pahlavi translation"
    }
}


if __name__ == "__main__":
    # 測試薩珊天文計算
    print("=" * 60)
    print("薩珊天文計算測試 (Sassanian Astronomy Test)")
    print("=" * 60)

    # 測試現代日期
    test_date = datetime(1980, 1, 15, 10, 30)
    julian_day = swe.julday(
        test_date.year, test_date.month, test_date.day,
        test_date.hour + test_date.minute / 60.0
    )

    ayanamsa = calculate_sassanian_ayanamsa(julian_day)
    print(f"\n測試日期：{test_date}")
    print(f"薩珊 Ayanamsa: {ayanamsa:.4f}°")

    # 計算行星位置
    positions = compute_sassanian_planet_positions(
        year=1980, month=1, day=15, hour=10, minute=30,
        longitude=121.5, latitude=25.0, timezone=8.0
    )

    print("\n行星位置（薩珊系統）:")
    print("-" * 80)
    print(f"{'行星':<10} {'Pahlavi':<12} {'經度':<10} {'星座':<10} {'宮位':<6} {'逆行':<6}")
    print("-" * 80)

    for pos in positions:
        retro = "是" if pos.is_retrograde else "否"
        print(f"{pos.name:<10} {pos.name_pahlavi:<12} {pos.longitude_sidereal:>8.2f}° "
              f"{pos.sign:<10} {pos.house:<6} {retro:<6}")

    # 計算宮位
    houses = get_sassanian_houses(
        year=1980, month=1, day=15, hour=10, minute=30,
        longitude=121.5, latitude=25.0, timezone=8.0
    )

    print("\n整宮制宮位:")
    print("-" * 60)
    for h in houses:
        print(f"第{h['house_number']:2}宮 ({h['meaning_pahlavi']:>10}): {h['sign']:<12} "
              f"[{h['longitude_start']:>6.0f}° - {h['longitude_end']:>6.0f}°]")

    # 獲取皇家恆星位置
    royal_stars = get_royal_stars_positions(julian_day)
    print("\n四顆皇家恆星:")
    print("-" * 80)
    for star_name, star_data in royal_stars.items():
        print(f"{star_data['name_pahlavi']:>12} ({star_data['name_en']:>10}): "
              f"{star_data['sassanian_longitude']:>8.2f}° ({star_data['constellation']})")

    print("\n" + "=" * 60)
    print("測試完成")
