"""
astro/persian/sassanian_astrology.py — 波斯薩珊王朝占星系統

Sassanian Astrology (224–651 CE) — 古代波斯薩珊王朝的占星傳統

本模組實現波斯薩珊王朝占星的核心技術：
1. Firdar / Firdaria (行星生命週期) — 薩珊占星最具特色的預測技法
2. Hyleg & Alcocoden (生命給予者與壽命給予者) — 古典壽命推算技術
3. Persian-style Profections (波斯式年度主限) — 基於度數的連續移動
4. Almuten Figuris (最強行星/命主星) — 根據薩珊尊嚴規則計算
5. Royal Stars (四顆皇家恆星) — 波斯傳統的重要恆星
6. Persian Lots (波斯阿拉伯點) — 特殊的敏感點計算

歷史參考：
- Umar al-Tabari (8 世紀) — 《Kitab al-Qirat fi Ilm al-Nujum》
- Masha'allah ibn Athari (8-9 世紀) — 《On Reception》
- Abu Ma'shar al-Balkhi (9 世紀) — 《Introductorium in Astronomiam》
- 薩珊王朝占星文献 (5-7 世紀)

注意：本模組使用熱帶黃道 (Tropical Zodiac)，與現代西洋占星相同，
但使用薩珊王朝的尊嚴規則和預測技法。
"""

from __future__ import annotations

import swisseph as swe
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
import math


# ═══════════════════════════════════════════════════════════════
# 常量定義 (Constants)
# ═══════════════════════════════════════════════════════════════

# 行星定義 (使用 Swiss Ephemeris IDs)
SASSANIAN_PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
}

# 12 星座 (熱帶黃道)
ZODIAC_SIGNS = [
    ("Aries", "♈", "白羊座", "Fire", "熱"),
    ("Taurus", "♉", "金牛座", "Earth", "冷"),
    ("Gemini", "♊", "雙子座", "Air", "濕"),
    ("Cancer", "♋", "巨蟹座", "Water", "乾"),
    ("Leo", "♌", "獅子座", "Fire", "熱"),
    ("Virgo", "♍", "處女座", "Earth", "冷"),
    ("Libra", "♎", "天秤座", "Air", "濕"),
    ("Scorpio", "♏", "天蠍座", "Water", "乾"),
    ("Sagittarius", "♐", "射手座", "Fire", "熱"),
    ("Capricorn", "♑", "摩羯座", "Earth", "冷"),
    ("Aquarius", "♒", "水瓶座", "Air", "濕"),
    ("Pisces", "♓", "雙魚座", "Water", "乾"),
]

# 薩珊尊嚴規則 (Essential Dignities per Sassanian tradition)
# 包含：Domicile (廟), Exaltation (旺), Triplicity (三分), Term (界), Decan (面)
SASSANIAN_DIGNITIES = {
    0: {"domicile": "Mars", "exaltation": "Sun", "triplicity_day": "Sun", "triplicity_night": "Jupiter", "term": {"0-6": "Venus", "6-12": "Mercury", "12-20": "Jupiter", "20-25": "Mars", "25-30": "Saturn"}},
    1: {"domicile": "Venus", "exaltation": "Moon", "triplicity_day": "Venus", "triplicity_night": "Moon", "term": {"0-8": "Mercury", "8-14": "Venus", "14-22": "Jupiter", "22-26": "Mars", "26-30": "Saturn"}},
    2: {"domicile": "Mercury", "exaltation": None, "triplicity_day": "Saturn", "triplicity_night": "Mercury", "term": {"0-7": "Jupiter", "7-13": "Venus", "13-19": "Mercury", "19-24": "Mars", "24-30": "Saturn"}},
    3: {"domicile": "Moon", "exaltation": "Jupiter", "triplicity_day": "Venus", "triplicity_night": "Moon", "term": {"0-6": "Mars", "6-12": "Venus", "12-18": "Mercury", "18-24": "Jupiter", "24-30": "Saturn"}},
    4: {"domicile": "Sun", "exaltation": None, "triplicity_day": "Sun", "triplicity_night": "Jupiter", "term": {"0-5": "Jupiter", "5-11": "Venus", "11-18": "Mercury", "18-24": "Mars", "24-30": "Saturn"}},
    5: {"domicile": "Mercury", "exaltation": "Mercury", "triplicity_day": "Venus", "triplicity_night": "Moon", "term": {"0-7": "Jupiter", "7-13": "Venus", "13-21": "Mercury", "21-26": "Mars", "26-30": "Saturn"}},
    6: {"domicile": "Venus", "exaltation": "Saturn", "triplicity_day": "Saturn", "triplicity_night": "Venus", "term": {"0-6": "Venus", "6-12": "Mercury", "12-18": "Jupiter", "18-24": "Mars", "24-30": "Saturn"}},
    7: {"domicile": "Mars", "exaltation": None, "triplicity_day": "Mars", "triplicity_night": "Moon", "term": {"0-6": "Venus", "6-12": "Mercury", "12-19": "Jupiter", "19-25": "Mars", "25-30": "Saturn"}},
    8: {"domicile": "Jupiter", "exaltation": None, "triplicity_day": "Sun", "triplicity_night": "Jupiter", "term": {"0-6": "Venus", "6-12": "Mercury", "12-19": "Jupiter", "19-25": "Mars", "25-30": "Saturn"}},
    9: {"domicile": "Saturn", "exaltation": "Mars", "triplicity_day": "Venus", "triplicity_night": "Moon", "term": {"0-6": "Venus", "6-12": "Mercury", "12-18": "Jupiter", "18-24": "Mars", "24-30": "Saturn"}},
    10: {"domicile": "Saturn", "exaltation": None, "triplicity_day": "Saturn", "triplicity_night": "Venus", "term": {"0-6": "Venus", "6-12": "Mercury", "12-20": "Jupiter", "20-25": "Mars", "25-30": "Saturn"}},
    11: {"domicile": "Jupiter", "exaltation": "Venus", "triplicity_day": "Venus", "triplicity_night": "Moon", "term": {"0-6": "Venus", "6-12": "Mercury", "12-21": "Jupiter", "21-26": "Mars", "26-30": "Saturn"}},
}

# Firdar 順序 (Sassanian Planetary Time Lords)
# 白天出生：Sun → Moon → Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon
# 夜晚出生：Moon → Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon → Saturn
# 每個主要週期的年數 (根據傳統分配)
FIRDAR_MAJOR_YEARS = {
    "Sun": 19,
    "Moon": 25,
    "Saturn": 15,
    "Jupiter": 16,
    "Mars": 10,
    "Venus": 20,
    "Mercury": 13,
}

# Firdar 子週期順序和比例
FIRDAR_SUB_ORDER = ["Sun", "Moon", "Saturn", "Jupiter", "Mars", "Venus", "Mercury"]

# 四顆皇家恆星 (Royal Stars of Persia)
# 使用現代經度位置 (熱帶黃道)
ROYAL_STARS = {
    "Aldebaran": {"longitude": 69.0, "name_en": "Aldebaran", "name_cn": "畢宿五"},  # ~9° Gemini
    "Regulus": {"longitude": 149.0, "name_en": "Regulus", "name_cn": "軒轅十四"},   # ~29° Leo
    "Antares": {"longitude": 249.0, "name_en": "Antares", "name_cn": "心宿二"},     # ~9° Sagittarius
    "Fomalhaut": {"longitude": 339.0, "name_en": "Fomalhaut", "name_cn": "北落師門"}, # ~19° Pisces
}

# 行星年數 (Planetary Years for Alcocoden)
PLANETARY_YEARS = {
    "Sun": 19,
    "Moon": 25,
    "Saturn": 43,
    "Jupiter": 79,
    "Mars": 66,
    "Venus": 82,
    "Mercury": 76,
}


# ═══════════════════════════════════════════════════════════════
# 資料類別 (Data Classes)
# ═══════════════════════════════════════════════════════════════

@dataclass
class SassanianPlanet:
    """波斯薩珊占星行星位置"""
    name: str
    name_cn: str
    longitude: float  # 經度 (0-360)
    latitude: float   # 緯度
    sign: str         # 星座英文名
    sign_glyph: str   # 星座符號
    sign_cn: str      # 星座中文名
    sign_degree: float  # 在星座內的度數 (0-30)
    house: int        # 宮位 (1-12)
    retrograde: bool  # 逆行狀態
    essential_dignity: str = ""  # 本質尊嚴
    accidental_dignity: str = ""  # 偶然尊嚴
    
    def to_dict(self) -> dict:
        """轉換為字典格式"""
        return {
            "name": self.name,
            "name_cn": self.name_cn,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "sign": self.sign,
            "sign_glyph": self.sign_glyph,
            "sign_cn": self.sign_cn,
            "sign_degree": self.sign_degree,
            "house": self.house,
            "retrograde": self.retrograde,
            "essential_dignity": self.essential_dignity,
            "accidental_dignity": self.accidental_dignity,
        }


@dataclass
class FirdarPeriod:
    """Firdar 生命週期"""
    lord: str
    lord_cn: str
    start_date: str
    end_date: str
    duration_years: float
    sub_periods: List["FirdarSubPeriod"] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "lord": self.lord,
            "lord_cn": self.lord_cn,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "duration_years": self.duration_years,
            "sub_periods": [sp.to_dict() for sp in self.sub_periods],
        }


@dataclass
class FirdarSubPeriod:
    """Firdar 子週期"""
    lord: str
    lord_cn: str
    start_date: str
    end_date: str
    duration_years: float
    
    def to_dict(self) -> dict:
        return {
            "lord": self.lord,
            "lord_cn": self.lord_cn,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "duration_years": self.duration_years,
        }


@dataclass
class HylegResult:
    """Hyleg (生命給予者) 結果"""
    hyleg_type: str  # "Sun", "Moon", "Ascendant", "Lot of Fortune"
    hyleg_name_cn: str
    longitude: float
    sign: str
    degree: float
    house: int
    is_valid: bool
    reason: str = ""
    
    def to_dict(self) -> dict:
        return {
            "hyleg_type": self.hyleg_type,
            "hyleg_name_cn": self.hyleg_name_cn,
            "longitude": self.longitude,
            "sign": self.sign,
            "degree": self.degree,
            "house": self.house,
            "is_valid": self.is_valid,
            "reason": self.reason,
        }


@dataclass
class AlcocodenResult:
    """Alcocoden (壽命給予者) 結果"""
    alcocoden_lord: str
    alcocoden_lord_cn: str
    planetary_years: int
    modified_years: float  # 經過相位修正後的年數
    aspects: List[str] = field(default_factory=list)
    reason: str = ""
    
    def to_dict(self) -> dict:
        return {
            "alcocoden_lord": self.alcocoden_lord,
            "alcocoden_lord_cn": self.alcocoden_lord_cn,
            "planetary_years": self.planetary_years,
            "modified_years": self.modified_years,
            "aspects": self.aspects,
            "reason": self.reason,
        }


@dataclass
class ProfectionYear:
    """年度主限年份"""
    age: int
    profection_sign: str
    profection_sign_cn: str
    profection_degree: float
    lord_of_year: str
    lord_of_year_cn: str
    start_date: str
    end_date: str
    
    def to_dict(self) -> dict:
        return {
            "age": self.age,
            "profection_sign": self.profection_sign,
            "profection_sign_cn": self.profection_sign_cn,
            "profection_degree": self.profection_degree,
            "lord_of_year": self.lord_of_year,
            "lord_of_year_cn": self.lord_of_year_cn,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }


@dataclass
class AlmutenFiguris:
    """Almuten Figuris (最強行星)"""
    planet: str
    planet_cn: str
    total_score: float
    dignity_scores: Dict[str, float] = field(default_factory=dict)
    reason: str = ""
    
    def to_dict(self) -> dict:
        return {
            "planet": self.planet,
            "planet_cn": self.planet_cn,
            "total_score": self.total_score,
            "dignity_scores": self.dignity_scores,
            "reason": self.reason,
        }


@dataclass
class PersianLot:
    """波斯敏感點 (Lots)"""
    name_en: str
    name_cn: str
    name_arabic: str
    longitude: float
    sign: str
    sign_cn: str
    degree: float
    house: int
    
    def to_dict(self) -> dict:
        return {
            "name_en": self.name_en,
            "name_cn": self.name_cn,
            "name_arabic": self.name_arabic,
            "longitude": self.longitude,
            "sign": self.sign,
            "sign_cn": self.sign_cn,
            "degree": self.degree,
            "house": self.house,
        }


@dataclass
class RoyalStarProminence:
    """皇家恆星顯著度"""
    star_name: str
    star_name_cn: str
    star_longitude: float
    conjunction_planet: str
    conjunction_planet_cn: str
    orb: float
    is_prominent: bool
    meaning_en: str
    meaning_cn: str
    
    def to_dict(self) -> dict:
        return {
            "star_name": self.star_name,
            "star_name_cn": self.star_name_cn,
            "star_longitude": self.star_longitude,
            "conjunction_planet": self.conjunction_planet,
            "conjunction_planet_cn": self.conjunction_planet_cn,
            "orb": self.orb,
            "is_prominent": self.is_prominent,
            "meaning_en": self.meaning_en,
            "meaning_cn": self.meaning_cn,
        }


@dataclass
class SassanianChart:
    """波斯薩珊占星星盤"""
    julian_day: float
    latitude: float
    longitude: float
    timezone: float
    is_day_birth: bool
    planets: List[SassanianPlanet]
    houses: List[float]  # 12 宮宮頭經度
    ascendant: float
    midheaven: float
    firdar: List[FirdarPeriod] = field(default_factory=list)
    current_firdar: Optional[FirdarPeriod] = None
    current_sub_period: Optional[FirdarSubPeriod] = None
    hyleg: Optional[HylegResult] = None
    alcocoden: Optional[AlcocodenResult] = None
    profections: List[ProfectionYear] = field(default_factory=list)
    almuten_figuris: Optional[AlmutenFiguris] = None
    royal_stars: List[RoyalStarProminence] = field(default_factory=list)
    persian_lots: List[PersianLot] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """轉換為字典格式"""
        return {
            "julian_day": self.julian_day,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "is_day_birth": self.is_day_birth,
            "planets": [p.to_dict() for p in self.planets],
            "houses": self.houses,
            "ascendant": self.ascendant,
            "midheaven": self.midheaven,
            "firdar": [f.to_dict() for f in self.firdar],
            "current_firdar": self.current_firdar.to_dict() if self.current_firdar else None,
            "current_sub_period": self.current_sub_period.to_dict() if self.current_sub_period else None,
            "hyleg": self.hyleg.to_dict() if self.hyleg else None,
            "alcocoden": self.alcocoden.to_dict() if self.alcocoden else None,
            "profections": [p.to_dict() for p in self.profections],
            "almuten_figuris": self.almuten_figuris.to_dict() if self.almuten_figuris else None,
            "royal_stars": [r.to_dict() for r in self.royal_stars],
            "persian_lots": [l.to_dict() for l in self.persian_lots],
        }


# ═══════════════════════════════════════════════════════════════
# 輔助函數 (Helper Functions)
# ═══════════════════════════════════════════════════════════════

def _get_sign_from_longitude(longitude: float) -> Tuple[str, str, str, float]:
    """從經度取得星座資訊"""
    sign_index = int(longitude // 30) % 12
    sign_info = ZODIAC_SIGNS[sign_index]
    degree_in_sign = longitude % 30
    return sign_info[0], sign_info[1], sign_info[2], degree_in_sign


def _normalize_longitude(lon: float) -> float:
    """標準化經度到 0-360 範圍"""
    while lon < 0:
        lon += 360
    while lon >= 360:
        lon -= 360
    return lon


def _julian_day_to_date(jd: float) -> str:
    """將儒略日轉換為日期字串"""
    # 使用 swe.revjul 來轉換
    year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)
    return f"{int(year):04d}-{month:02d}-{day:02d}"


def _calculate_dignity(planet_lon: float, planet_name: str, is_day: bool) -> str:
    """計算行星的本質尊嚴"""
    sign_index = int(planet_lon // 30) % 12
    degree_in_sign = planet_lon % 30
    dignity_info = SASSANIAN_DIGNITIES.get(sign_index, {})
    
    dignities = []
    
    # Domicile (廟)
    if dignity_info.get("domicile") == planet_name:
        dignities.append("Domicile (廟)")
    
    # Exaltation (旺)
    if dignity_info.get("exaltation") == planet_name:
        dignities.append("Exaltation (旺)")
    
    # Triplicity (三分)
    trip_key = "triplicity_day" if is_day else "triplicity_night"
    if dignity_info.get(trip_key) == planet_name:
        dignities.append("Triplicity (三分)")
    
    # Term (界)
    terms = dignity_info.get("term", {})
    for range_str, ruler in terms.items():
        if ruler == planet_name:
            start, end = map(int, range_str.split("-"))
            if start <= degree_in_sign < end:
                dignities.append("Term (界)")
                break
    
    return ", ".join(dignities) if dignities else "Peregrine (無尊嚴)"


# ═══════════════════════════════════════════════════════════════
# 核心計算函數 (Core Calculation Functions)
# ═══════════════════════════════════════════════════════════════

def calculate_firdar(birth_jd: float, is_day_birth: bool, num_years: int = 80) -> List[FirdarPeriod]:
    """
    計算 Firdar 生命週期 (Planetary Time Lords)
    
    Parameters
    ----------
    birth_jd : float
        出生儒略日
    is_day_birth : bool
        是否為白天出生
    num_years : int
        計算多少年的週期 (預設 80 年)
    
    Returns
    -------
    List[FirdarPeriod]
        Firdar 主要週期和子週期列表
    
    References
    ----------
    - Abu Ma'shar, "Introductorium in Astronomiam", Book IV
    - Masha'allah, "On Nativities"
    """
    # 決定 Firdar 順序
    if is_day_birth:
        # 白天：Sun → Moon → Saturn → Jupiter → Mars → Venus → Mercury
        major_order = ["Sun", "Moon", "Saturn", "Jupiter", "Mars", "Venus", "Mercury"]
    else:
        # 夜晚：Moon → Saturn → Jupiter → Mars → Sun → Venus → Mercury
        major_order = ["Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury"]
    
    # 行星名稱映射
    PLANET_CN = {
        "Sun": "太陽", "Moon": "月亮", "Saturn": "土星",
        "Jupiter": "木星", "Mars": "火星", "Venus": "金星", "Mercury": "水星"
    }
    
    firdar_periods = []
    current_jd = birth_jd
    
    # 計算主要週期
    for lord in major_order:
        major_years = FIRDAR_MAJOR_YEARS.get(lord, 10)
        end_jd = current_jd + (major_years * 365.25)
        
        # 計算子週期 (按比例分配)
        sub_periods = []
        sub_order_idx = FIRDAR_SUB_ORDER.index(lord) if lord in FIRDAR_SUB_ORDER else 0
        
        # 子週期順序從該行星開始
        rotated_sub_order = FIRDAR_SUB_ORDER[sub_order_idx:] + FIRDAR_SUB_ORDER[:sub_order_idx]
        
        sub_current_jd = current_jd
        for sub_lord in rotated_sub_order:
            # 子週期年數按比例計算
            sub_years = (FIRDAR_MAJOR_YEARS.get(sub_lord, 10) / sum(FIRDAR_MAJOR_YEARS.values())) * major_years
            sub_end_jd = sub_current_jd + (sub_years * 365.25)
            
            sub_periods.append(FirdarSubPeriod(
                lord=sub_lord,
                lord_cn=PLANET_CN.get(sub_lord, sub_lord),
                start_date=_julian_day_to_date(sub_current_jd),
                end_date=_julian_day_to_date(sub_end_jd),
                duration_years=sub_years,
            ))
            sub_current_jd = sub_end_jd
        
        firdar_periods.append(FirdarPeriod(
            lord=lord,
            lord_cn=PLANET_CN.get(lord, lord),
            start_date=_julian_day_to_date(current_jd),
            end_date=_julian_day_to_date(end_jd),
            duration_years=major_years,
            sub_periods=sub_periods,
        ))
        
        current_jd = end_jd
    
    return firdar_periods


def calculate_hyleg_alcocoden(planets: List[SassanianPlanet], houses: List[float], 
                               ascendant: float, is_day_birth: bool) -> Tuple[HylegResult, AlcocodenResult]:
    """
    計算 Hyleg (生命給予者) 和 Alcocoden (壽命給予者)
    
    Parameters
    ----------
    planets : List[SassanianPlanet]
        行星列表
    houses : List[float]
        12 宮宮頭經度
    ascendant : float
        上升點經度
    is_day_birth : bool
        是否為白天出生
    
    Returns
    -------
    Tuple[HylegResult, AlcocodenResult]
        Hyleg 和 Alcocoden 結果
    
    References
    ----------
    - Ptolemy, "Tetrabiblos", Book III
    - Umar al-Tabari, "On the Judgment of Stars"
    """
    PLANET_CN = {
        "Sun": "太陽", "Moon": "月亮", "Saturn": "土星",
        "Jupiter": "木星", "Mars": "火星", "Venus": "金星", "Mercury": "水星"
    }
    
    # 尋找太陽和月亮
    sun = next((p for p in planets if p.name == "Sun"), None)
    moon = next((p for p in planets if p.name == "Moon"), None)
    
    # 計算幸運點 (Lot of Fortune)
    if sun and moon:
        if is_day_birth:
            lot_fortune = _normalize_longitude(ascendant + moon.longitude - sun.longitude)
        else:
            lot_fortune = _normalize_longitude(ascendant + sun.longitude - moon.longitude)
    else:
        lot_fortune = ascendant
    
    lot_sign = int(lot_fortune // 30) % 12
    lot_degree = lot_fortune % 30
    
    # Hyleg 判斷規則 (優先順序)
    # 1. 太陽 (白天) / 月亮 (夜晚) - 如果在 1, 5, 7, 9, 10, 11 宮
    # 2. 幸運點 - 如果在上述宮位
    # 3. 上升點
    
    def get_house(longitude: float) -> int:
        """判斷經度所在的宮位"""
        for i, house_cusp in enumerate(houses):
            next_house = houses[(i + 1) % 12] if i < 11 else houses[0] + 360
            if house_cusp <= longitude < next_house:
                return i + 1
        return 1
    
    # 有利的宮位 (Hylegical places)
    favorable_houses = {1, 5, 7, 9, 10, 11}
    
    hyleg = None
    hyleg_reason = ""
    
    # 檢查太陽 (白天)
    if is_day_birth and sun:
        sun_house = get_house(sun.longitude)
        if sun_house in favorable_houses:
            hyleg = HylegResult(
                hyleg_type="Sun",
                hyleg_name_cn="太陽",
                longitude=sun.longitude,
                sign=sun.sign,
                degree=sun.sign_degree,
                house=sun_house,
                is_valid=True,
                reason=f"白天出生，太陽在第{sun_house}宮 (有利宮位)"
            )
            hyleg_reason = "Sun"
    
    # 檢查月亮 (夜晚)
    if not hyleg and moon:
        moon_house = get_house(moon.longitude)
        if (not is_day_birth and moon_house in favorable_houses) or is_day_birth:
            hyleg = HylegResult(
                hyleg_type="Moon",
                hyleg_name_cn="月亮",
                longitude=moon.longitude,
                sign=moon.sign,
                degree=moon.sign_degree,
                house=moon_house,
                is_valid=True,
                reason=f"{'夜晚出生，' if not is_day_birth else ''}月亮在第{moon_house}宮"
            )
            hyleg_reason = "Moon"
    
    # 檢查幸運點
    if not hyleg:
        lot_house = get_house(lot_fortune)
        if lot_house in favorable_houses:
            lot_sign_name, lot_glyph, lot_sign_cn, _ = _get_sign_from_longitude(lot_fortune)
            hyleg = HylegResult(
                hyleg_type="Lot of Fortune",
                hyleg_name_cn="幸運點",
                longitude=lot_fortune,
                sign=lot_sign_name,
                degree=lot_degree,
                house=lot_house,
                is_valid=True,
                reason=f"幸運點在第{lot_house}宮 (有利宮位)"
            )
            hyleg_reason = "Lot"
    
    # 預設為上升點
    if not hyleg:
        asc_sign, asc_glyph, asc_cn, asc_deg = _get_sign_from_longitude(ascendant)
        hyleg = HylegResult(
            hyleg_type="Ascendant",
            hyleg_name_cn="上升點",
            longitude=ascendant,
            sign=asc_sign,
            degree=asc_deg,
            house=1,
            is_valid=True,
            reason="預設為上升點"
        )
        hyleg_reason = "Asc"
    
    # 計算 Alcocoden (壽命給予者)
    # 規則：尋找 Hyleg 位置的最強守護星
    alcocoden_lord = None
    alcocoden_score = 0
    
    hyleg_lon = hyleg.longitude
    hyleg_sign_idx = int(hyleg_lon // 30) % 12
    hyleg_degree = hyleg_lon % 30
    
    # 檢查各種尊嚴
    dignity_info = SASSANIAN_DIGNITIES.get(hyleg_sign_idx, {})
    
    # 計算每個行星的尊嚴分數
    planet_scores = {"Sun": 0, "Moon": 0, "Saturn": 0, "Jupiter": 0, "Mars": 0, "Venus": 0, "Mercury": 0}
    
    # Domicile (廟) - 5 分
    domicile_lord = dignity_info.get("domicile")
    if domicile_lord:
        planet_scores[domicile_lord] += 5
    
    # Exaltation (旺) - 4 分
    exalt_lord = dignity_info.get("exaltation")
    if exalt_lord:
        planet_scores[exalt_lord] += 4
    
    # Triplicity (三分) - 3 分
    trip_key = "triplicity_day" if is_day_birth else "triplicity_night"
    trip_lord = dignity_info.get(trip_key)
    if trip_lord:
        planet_scores[trip_lord] += 3
    
    # Term (界) - 2 分
    terms = dignity_info.get("term", {})
    for range_str, ruler in terms.items():
        start, end = map(int, range_str.split("-"))
        if start <= hyleg_degree < end:
            planet_scores[ruler] += 2
            break
    
    # 尋找最高分的行星
    alcocoden_lord = max(planet_scores, key=planet_scores.get)
    alcocoden_score = planet_scores[alcocoden_lord]
    
    # 檢查相位修正
    aspects = []
    modified_years = PLANETARY_YEARS.get(alcocoden_lord, 50)
    
    # 尋找與 Hyleg 有相位的行星
    for p in planets:
        if p.name == alcocoden_lord:
            continue
        orb = abs(p.longitude - hyleg_lon)
        if orb > 180:
            orb = 360 - orb
        
        # 主要相位
        if orb <= 1:  # 合相
            aspects.append(f"{p.name} 合相 (0°)")
            if p.name in ["Jupiter", "Venus"]:
                modified_years *= 1.2  # 吉星增加 20%
            elif p.name in ["Saturn", "Mars"]:
                modified_years *= 0.8  # 凶星減少 20%
        elif 59 <= orb <= 61:  # 六分相
            aspects.append(f"{p.name} 六分相 (60°)")
            if p.name in ["Jupiter", "Venus"]:
                modified_years *= 1.1
        elif 89 <= orb <= 91:  # 四分相
            aspects.append(f"{p.name} 四分相 (90°)")
            if p.name in ["Saturn", "Mars"]:
                modified_years *= 0.9
        elif 119 <= orb <= 121:  # 三分相
            aspects.append(f"{p.name} 三分相 (120°)")
            if p.name in ["Jupiter", "Venus"]:
                modified_years *= 1.15
        elif 179 <= orb <= 181:  # 對分相
            aspects.append(f"{p.name} 對分相 (180°)")
            if p.name in ["Saturn", "Mars"]:
                modified_years *= 0.85
    
    alcocoden = AlcocodenResult(
        alcocoden_lord=alcocoden_lord,
        alcocoden_lord_cn=PLANET_CN.get(alcocoden_lord, alcocoden_lord),
        planetary_years=PLANETARY_YEARS.get(alcocoden_lord, 50),
        modified_years=round(modified_years, 1),
        aspects=aspects,
        reason=f"基於 Hyleg ({hyleg.hyleg_name_cn}) 位置的尊嚴計算，總分：{alcocoden_score}"
    )
    
    return hyleg, alcocoden


def calculate_profections(ascendant: float, birth_jd: float, num_years: int = 80) -> List[ProfectionYear]:
    """
    計算波斯式年度主限 (Degree-based Profections)
    
    與希臘占星的星座主限不同，波斯傳統使用連續度數移動：
    每年移動 30°，從上升點開始
    
    Parameters
    ----------
    ascendant : float
        上升點經度
    birth_jd : float
        出生儒略日
    num_years : int
        計算多少年 (預設 80)
    
    Returns
    -------
    List[ProfectionYear]
        年度主限列表
    """
    PLANET_CN = {
        "Sun": "太陽", "Moon": "月亮", "Saturn": "土星",
        "Jupiter": "木星", "Mars": "火星", "Venus": "金星", "Mercury": "水星"
    }
    
    # 行星守護關係
    SIGN_LORDS = {
        0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
        6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter"
    }
    
    profections = []
    current_jd = birth_jd
    
    for age in range(num_years):
        # 波斯式：每年移動 30°
        profection_lon = _normalize_longitude(ascendant + (age * 30))
        profection_sign_idx = int(profection_lon // 30) % 12
        profection_degree = profection_lon % 30
        
        sign_info = ZODIAC_SIGNS[profection_sign_idx]
        lord = SIGN_LORDS.get(profection_sign_idx, "Sun")
        
        end_jd = current_jd + 365.25
        
        profections.append(ProfectionYear(
            age=age,
            profection_sign=sign_info[0],
            profection_sign_cn=sign_info[2],
            profection_degree=profection_degree,
            lord_of_year=lord,
            lord_of_year_cn=PLANET_CN.get(lord, lord),
            start_date=_julian_day_to_date(current_jd),
            end_date=_julian_day_to_date(end_jd),
        ))
        
        current_jd = end_jd
    
    return profections


def calculate_almuten_figuris(planets: List[SassanianPlanet], ascendant: float, 
                               midheaven: float, is_day_birth: bool) -> AlmutenFiguris:
    """
    計算 Almuten Figuris (最強行星/命主星)
    
    根據薩珊尊嚴規則，計算每個行星在多個關鍵點的總分
    
    Parameters
    ----------
    planets : List[SassanianPlanet]
        行星列表
    ascendant : float
        上升點經度
    midheaven : float
        天頂經度
    is_day_birth : bool
        是否為白天出生
    
    Returns
    -------
    AlmutenFiguris
        最強行星結果
    
    References
    ----------
    - Masha'allah, "On Reception"
    - Abu Ma'shar, "The Great Introduction"
    """
    PLANET_CN = {
        "Sun": "太陽", "Moon": "月亮", "Saturn": "土星",
        "Jupiter": "木星", "Mars": "火星", "Venus": "金星", "Mercury": "水星"
    }
    
    # 關鍵點
    key_points = {
        "Ascendant": ascendant,
        "Midheaven": midheaven,
        "Sun": next((p.longitude for p in planets if p.name == "Sun"), 0),
        "Moon": next((p.longitude for p in planets if p.name == "Moon"), 0),
        "Lot of Fortune": 0,  # 會在下面計算
    }
    
    # 計算幸運點
    sun = next((p for p in planets if p.name == "Sun"), None)
    moon = next((p for p in planets if p.name == "Moon"), None)
    if sun and moon:
        if is_day_birth:
            key_points["Lot of Fortune"] = _normalize_longitude(ascendant + moon.longitude - sun.longitude)
        else:
            key_points["Lot of Fortune"] = _normalize_longitude(ascendant + sun.longitude - moon.longitude)
    
    # 計算每個行星的分數
    planet_scores = {p.name: {"total": 0.0, "breakdown": {}} for p in planets}
    
    for point_name, point_lon in key_points.items():
        sign_idx = int(point_lon // 30) % 12
        degree_in_sign = point_lon % 30
        dignity_info = SASSANIAN_DIGNITIES.get(sign_idx, {})
        
        # Domicile (廟) - 5 分
        domicile_lord = dignity_info.get("domicile")
        if domicile_lord and domicile_lord in planet_scores:
            planet_scores[domicile_lord]["total"] += 5
            planet_scores[domicile_lord]["breakdown"][f"{point_name}_domicile"] = 5
        
        # Exaltation (旺) - 4 分
        exalt_lord = dignity_info.get("exaltation")
        if exalt_lord and exalt_lord in planet_scores:
            planet_scores[exalt_lord]["total"] += 4
            planet_scores[exalt_lord]["breakdown"][f"{point_name}_exaltation"] = 4
        
        # Triplicity (三分) - 3 分
        trip_key = "triplicity_day" if is_day_birth else "triplicity_night"
        trip_lord = dignity_info.get(trip_key)
        if trip_lord and trip_lord in planet_scores:
            planet_scores[trip_lord]["total"] += 3
            planet_scores[trip_lord]["breakdown"][f"{point_name}_triplicity"] = 3
        
        # Term (界) - 2 分
        terms = dignity_info.get("term", {})
        for range_str, ruler in terms.items():
            start, end = map(int, range_str.split("-"))
            if start <= degree_in_sign < end:
                if ruler in planet_scores:
                    planet_scores[ruler]["total"] += 2
                    planet_scores[ruler]["breakdown"][f"{point_name}_term"] = 2
                break
    
    # 尋找最高分的行星
    if not planet_scores:
        return AlmutenFiguris(
            planet="Sun",
            planet_cn="太陽",
            total_score=0,
            reason="無足夠行星數據"
        )
    
    best_planet = max(planet_scores, key=lambda x: planet_scores[x]["total"])
    best_score = planet_scores[best_planet]["total"]
    
    return AlmutenFiguris(
        planet=best_planet,
        planet_cn=PLANET_CN.get(best_planet, best_planet),
        total_score=best_score,
        dignity_scores=planet_scores[best_planet]["breakdown"],
        reason=f"在關鍵點 (上升、天頂、日月、幸運點) 的尊嚴總分最高"
    )


def get_royal_stars_prominence(planets: List[SassanianPlanet], orb_limit: float = 3.0) -> List[RoyalStarProminence]:
    """
    計算四顆皇家恆星的顯著度
    
    Parameters
    ----------
    planets : List[SassanianPlanet]
        行星列表
    orb_limit : float
        允許的容許度 (度數)
    
    Returns
    -------
    List[RoyalStarProminence]
        皇家恆星顯著度列表
    
    References
    ----------
    - Firmicus Maternus, "Mathesis"
    - Persian astronomical tradition
    """
    PLANET_CN = {
        "Sun": "太陽", "Moon": "月亮", "Saturn": "土星",
        "Jupiter": "木星", "Mars": "火星", "Venus": "金星", "Mercury": "水星"
    }
    
    ROYAL_STAR_MEANINGS = {
        "Aldebaran": ("Spring Equinox marker, honor, wealth", "春分點標記，榮譽，財富"),
        "Regulus": ("Royal star, leadership, power", "帝王之星，領導力，權力"),
        "Antares": ("Autumn Equinox marker, challenge, transformation", "秋分點標記，挑戰，轉化"),
        "Fomalhaut": ("Winter Solstice marker, spirituality, magic", "冬至點標記，靈性，魔法"),
    }
    
    results = []
    
    for star_name, star_data in ROYAL_STARS.items():
        star_lon = star_data["longitude"]
        star_cn = star_data["name_cn"]
        meaning_en, meaning_cn = ROYAL_STAR_MEANINGS.get(star_name, ("", ""))
        
        # 尋找與該恆星有合相的行星
        conjunction_found = False
        conjunction_planet = None
        conjunction_planet_cn = None
        min_orb = orb_limit + 1
        
        for p in planets:
            orb = abs(p.longitude - star_lon)
            if orb > 180:
                orb = 360 - orb
            
            if orb <= orb_limit and orb < min_orb:
                conjunction_found = True
                conjunction_planet = p.name
                conjunction_planet_cn = PLANET_CN.get(p.name, p.name)
                min_orb = orb
        
        if conjunction_found:
            results.append(RoyalStarProminence(
                star_name=star_name,
                star_name_cn=star_cn,
                star_longitude=star_lon,
                conjunction_planet=conjunction_planet,
                conjunction_planet_cn=conjunction_planet_cn,
                orb=round(min_orb, 2),
                is_prominent=True,
                meaning_en=meaning_en,
                meaning_cn=meaning_cn,
            ))
        else:
            results.append(RoyalStarProminence(
                star_name=star_name,
                star_name_cn=star_cn,
                star_longitude=star_lon,
                conjunction_planet=None,
                conjunction_planet_cn=None,
                orb=0,
                is_prominent=False,
                meaning_en=meaning_en,
                meaning_cn=meaning_cn,
            ))
    
    return results


def calculate_persian_lots(ascendant: float, sun: float, moon: float, 
                            is_day_birth: bool) -> List[PersianLot]:
    """
    計算波斯敏感點 (Persian Lots / Arabic Parts)
    
    Parameters
    ----------
    ascendant : float
        上升點經度
    sun : float
        太陽經度
    moon : float
        月亮經度
    is_day_birth : bool
        是否為白天出生
    
    Returns
    -------
    List[PersianLot]
        波斯敏感點列表
    
    References
    ----------
    - Masha'allah, "On Reception"
    - Umar al-Tabari, "Three Books"
    """
    def calc_lot(a: float, b: float, reverse: bool = False) -> float:
        """計算敏感點：ASC + A - B"""
        if reverse:
            return _normalize_longitude(ascendant + b - a)
        else:
            return _normalize_longitude(ascendant + a - b)
    
    lots_data = [
        ("Part of Fortune", "幸運點", "سهم السعادة", 
         calc_lot(sun, moon, not is_day_birth)),
        ("Part of Spirit", "精神點", "سهم الروح", 
         calc_lot(moon, sun, not is_day_birth)),
        ("Part of Love", "愛情點", "سهم الحب", 
         calc_lot(sun, next((p.longitude for p in [] if p.name == "Venus"), 0), not is_day_birth) if False else _normalize_longitude(ascendant + moon.longitude - Venus if False else ascendant)),
    ]
    
    # 簡化版本：只計算主要的幾個點
    lots = []
    
    # 幸運點
    lot_fortune = _normalize_longitude(ascendant + moon - sun) if is_day_birth else _normalize_longitude(ascendant + sun - moon)
    sign, glyph, sign_cn, degree = _get_sign_from_longitude(lot_fortune)
    lots.append(PersianLot(
        name_en="Part of Fortune",
        name_cn="幸運點",
        name_arabic="سهم السعادة",
        longitude=lot_fortune,
        sign=sign,
        sign_cn=sign_cn,
        degree=degree,
        house=1,  # 簡化：實際應根據宮位計算
    ))
    
    # 精神點
    lot_spirit = _normalize_longitude(ascendant + sun - moon) if is_day_birth else _normalize_longitude(ascendant + moon - sun)
    sign, glyph, sign_cn, degree = _get_sign_from_longitude(lot_spirit)
    lots.append(PersianLot(
        name_en="Part of Spirit",
        name_cn="精神點",
        name_arabic="سهم الروح",
        longitude=lot_spirit,
        sign=sign,
        sign_cn=sign_cn,
        degree=degree,
        house=1,
    ))
    
    return lots


def compute_sassanian_chart(year: int, month: int, day: int, 
                             hour: int, minute: int,
                             latitude: float, longitude: float,
                             timezone: float,
                             language: str = "zh") -> SassanianChart:
    """
    計算完整的波斯薩珊占星星盤
    
    Parameters
    ----------
    year : int
        出生年份
    month : int
        出生月份
    day : int
        出生日期
    hour : int
        出生時
    minute : int
        出生分
    latitude : float
        地理緯度
    longitude : float
        地理經度
    timezone : float
        時區
    language : str
        語言 ("zh" 或 "en")
    
    Returns
    -------
    SassanianChart
        完整的薩珊占星星盤
    """
    # 計算儒略日
    jd = swe.julday(year, month, day, hour + minute/60.0)
    
    # 設置星曆表
    swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)  # 使用 Fagan-Bradley ayanamsa
    
    # 計算上升點和天頂
    result = swe.houses(jd, latitude, longitude, b'P')
    houses = list(result[0])  # 12 宮宮頭
    asc = result[1][0]  # 上升點 (從第二个数组取得)
    mc = result[1][2]   # 天頂 (MC)
    
    # 計算行星位置
    PLANET_CN = {
        "Sun": "太陽", "Moon": "月亮", "Saturn": "土星",
        "Jupiter": "木星", "Mars": "火星", "Venus": "金星", "Mercury": "水星"
    }
    
    planets = []
    for planet_name, swe_id in SASSANIAN_PLANETS.items():
        # 計算行星位置 (使用 swe.calc)
        result = swe.calc(jd, swe_id)
        lon, lat = result[0][0], result[0][1]
        lon = _normalize_longitude(lon)
        
        # 計算逆行
        result_prev = swe.calc(jd - 1, swe_id)
        is_retro = result_prev[0][0] > lon if jd > 0 else False
        
        # 取得星座資訊
        sign, sign_glyph, sign_cn, sign_degree = _get_sign_from_longitude(lon)
        
        # 計算宮位
        def get_house(lon):
            for i, house_cusp in enumerate(houses):
                if i < 11:
                    if house_cusp <= lon < houses[i+1]:
                        return i + 1
                else:
                    if house_cusp <= lon or lon < houses[0]:
                        return i + 1
            return 1
        
        house_num = get_house(lon)
        
        # 計算尊嚴
        dignity = _calculate_dignity(lon, planet_name, True)  # 簡化：假設白天
        
        planets.append(SassanianPlanet(
            name=planet_name,
            name_cn=PLANET_CN.get(planet_name, planet_name),
            longitude=lon,
            latitude=lat,
            sign=sign,
            sign_glyph=sign_glyph,
            sign_cn=sign_cn,
            sign_degree=sign_degree,
            house=house_num,
            retrograde=is_retro,
            essential_dignity=dignity,
        ))
    
    # 判斷日夜出生
    sun = next((p for p in planets if p.name == "Sun"), None)
    moon = next((p for p in planets if p.name == "Moon"), None)
    
    # 古典占星日夜判斷：太陽在第 7-12 宮為白天（地平線以上），1-6 宮為夜晚（地平線以下）
    # 但這裡使用更簡單的方法：比較太陽和上升點的經度差
    # 如果太陽在 ASC 到 DSC 之間（第 7-12 宮），為白天
    if sun:
        sun_house = sun.house
        # 在 Placidus 宮位制中，7-12 宮是地平線以上（白天），1-6 宮是地平線以下（夜晚）
        is_day_birth = sun_house in [7, 8, 9, 10, 11, 12]
    else:
        is_day_birth = True  # 預設為白天
    
    # 計算 Firdar
    firdar = calculate_firdar(jd, is_day_birth)
    
    # 計算 Hyleg 和 Alcocoden
    hyleg, alcocoden = calculate_hyleg_alcocoden(planets, houses, asc, is_day_birth)
    
    # 計算 Profections
    profections = calculate_profections(asc, jd)
    
    # 計算 Almuten Figuris
    almuten = calculate_almuten_figuris(planets, asc, mc, is_day_birth)
    
    # 計算皇家恆星
    royal_stars = get_royal_stars_prominence(planets)
    
    # 計算波斯敏感點
    sun_lon = sun.longitude if sun else 0
    moon_lon = moon.longitude if moon else 0
    persian_lots = calculate_persian_lots(asc, sun_lon, moon_lon, is_day_birth)
    
    # 找出當前的 Firdar 和子週期
    current_firdar = None
    current_sub_period = None
    now_jd = swe.julday(datetime.now().year, datetime.now().month, datetime.now().day, 0)
    
    for fd in firdar:
        fd_start = swe.julday(int(fd.start_date[:4]), int(fd.start_date[5:7]), int(fd.start_date[8:10]), 0)
        fd_end = swe.julday(int(fd.end_date[:4]), int(fd.end_date[5:7]), int(fd.end_date[8:10]), 0)
        
        if fd_start <= now_jd <= fd_end:
            current_firdar = fd
            for sp in fd.sub_periods:
                sp_start = swe.julday(int(sp.start_date[:4]), int(sp.start_date[5:7]), int(sp.start_date[8:10]), 0)
                sp_end = swe.julday(int(sp.end_date[:4]), int(sp.end_date[5:7]), int(sp.end_date[8:10]), 0)
                if sp_start <= now_jd <= sp_end:
                    current_sub_period = sp
                    break
            break
    
    return SassanianChart(
        julian_day=jd,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        is_day_birth=is_day_birth,
        planets=planets,
        houses=houses,
        ascendant=asc,
        midheaven=mc,
        firdar=firdar,
        current_firdar=current_firdar,
        current_sub_period=current_sub_period,
        hyleg=hyleg,
        alcocoden=alcocoden,
        profections=profections,
        almuten_figuris=almuten,
        royal_stars=royal_stars,
        persian_lots=persian_lots,
    )


# ═══════════════════════════════════════════════════════════════
# 測試
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """測試波斯薩珊占星模組"""
    print("=" * 60)
    print("波斯薩珊占星模組測試")
    print("=" * 60)
    
    # 測試案例 1: 白天出生 (1990 年 1 月 15 日 12:00 台北)
    print("\n【測試案例 1: 白天出生】")
    print("1990 年 1 月 15 日 12:00 台北")
    
    chart_day = compute_sassanian_chart(
        year=1990, month=1, day=15,
        hour=12, minute=0,
        latitude=25.0330, longitude=121.5654,
        timezone=8.0
    )
    
    print(f"日夜判斷：{'白天' if chart_day.is_day_birth else '夜晚'}")
    print(f"上升點：{chart_day.ascendant:.2f}°")
    print(f"天頂：{chart_day.midheaven:.2f}°")
    
    print("\n【Firdar 生命週期】")
    for i, fd in enumerate(chart_day.firdar[:3]):
        print(f"  {i+1}. {fd.lord} ({fd.lord_cn}): {fd.start_date} - {fd.end_date} ({fd.duration_years:.1f}年)")
    
    if chart_day.current_firdar:
        print(f"\n當前 Firdar: {chart_day.current_firdar.lord} ({chart_day.current_firdar.lord_cn})")
        if chart_day.current_sub_period:
            print(f"當前子週期：{chart_day.current_sub_period.lord} ({chart_day.current_sub_period.lord_cn})")
    
    print("\n【Hyleg & Alcocoden】")
    if chart_day.hyleg:
        print(f"Hyleg: {chart_day.hyleg.hyleg_type} ({chart_day.hyleg.hyleg_name_cn})")
        print(f"  位置：{chart_day.hyleg.sign} {chart_day.hyleg.degree:.1f}°")
        print(f"  原因：{chart_day.hyleg.reason}")
    
    if chart_day.alcocoden:
        print(f"Alcocoden: {chart_day.alcocoden.alcocoden_lord} ({chart_day.alcocoden.alcocoden_lord_cn})")
        print(f"  基礎年數：{chart_day.alcocoden.planetary_years}年")
        print(f"  修正後年數：{chart_day.alcocoden.modified_years:.1f}年")
    
    print("\n【Almuten Figuris】")
    if chart_day.almuten_figuris:
        print(f"最強行星：{chart_day.almuten_figuris.planet} ({chart_day.almuten_figuris.planet_cn})")
        print(f"  總分：{chart_day.almuten_figuris.total_score}")
    
    print("\n【皇家恆星】")
    prominent = [rs for rs in chart_day.royal_stars if rs.is_prominent]
    if prominent:
        for rs in prominent:
            print(f"  {rs.star_name} ({rs.star_name_cn}) 與 {rs.conjunction_planet} ({rs.conjunction_planet_cn}) 合相 (容許度：{rs.orb}°)")
            print(f"    意義：{rs.meaning_cn}")
    else:
        print("  無顯著皇家恆星合相")
    
    # 測試案例 2: 夜晚出生
    print("\n" + "=" * 60)
    print("\n【測試案例 2: 夜晚出生】")
    print("1990 年 1 月 15 日 02:00 台北")
    
    chart_night = compute_sassanian_chart(
        year=1990, month=1, day=15,
        hour=2, minute=0,
        latitude=25.0330, longitude=121.5654,
        timezone=8.0
    )
    
    print(f"日夜判斷：{'白天' if chart_night.is_day_birth else '夜晚'}")
    print(f"Firdar 起始：{chart_night.firdar[0].lord} ({chart_night.firdar[0].lord_cn})")
    
    print("\n" + "=" * 60)
    print("測試完成！")
    print("=" * 60)
