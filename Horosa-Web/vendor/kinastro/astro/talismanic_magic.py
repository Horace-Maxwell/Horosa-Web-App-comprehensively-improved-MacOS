"""
astro/talismanic_magic.py — Picatrix 占星魔法護符製作嚮導計算引擎

實作互動式 Talisman 製作嚮導的後端計算邏輯：
  1. ``evaluate_electional_moment`` — 評估某時刻製作護符的適宜程度
  2. ``find_talisman_windows``       — 掃描未來時間，尋找最佳製符時機
  3. ``get_planet_dignity``          — 計算行星在某時刻的尊貴狀態
  4. ``get_moon_condition``          — 評估月亮狀態（相位、光照等）
  5. ``recommend_talisman``          — 根據目的推薦最適護符

資料來源（Sources）：
  - *Ghayat al-Hakim* (Picatrix), Bk I–IV
  - William Lilly, *Christian Astrology* (1647), Ch. on Elections
  - Guido Bonatti, *Liber Astronomiae* (~1277)
  - Marsilio Ficino, *De Vita Coelitus Comparanda* (1489)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from interpretations.talismanic import (
    PLANETARY_TALISMANS,
    DECAN_TALISMANS,
    DECAN_TALISMAN_BY_NUMBER,
    PLANETARY_TALISMAN_BY_PLANET,
    PURPOSE_TO_PLANETS,
    PURPOSE_LABELS_CN,
    PlanetaryTalisman,
    DecanTalisman,
    get_recommended_planets,
    get_decan_by_longitude,
)


# ============================================================
# 星座與行星常量
# ============================================================

ZODIAC_SIGNS: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

ZODIAC_SIGNS_CN: Dict[str, str] = {
    "Aries": "牡羊座", "Taurus": "金牛座", "Gemini": "雙子座",
    "Cancer": "巨蟹座", "Leo": "獅子座", "Virgo": "處女座",
    "Libra": "天秤座", "Scorpio": "天蠍座", "Sagittarius": "射手座",
    "Capricorn": "摩羯座", "Aquarius": "水瓶座", "Pisces": "雙魚座",
}

# 行星 Swiss Ephemeris ID
PLANET_IDS: Dict[str, int] = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
}

PLANET_CN: Dict[str, str] = {
    "Sun": "太陽", "Moon": "月亮", "Mercury": "水星",
    "Venus": "金星", "Mars": "火星", "Jupiter": "木星", "Saturn": "土星",
}

PLANET_GLYPHS: Dict[str, str] = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿",
    "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
}

# 尊貴表（本位 / 擢升 / 落陷 / 入廟失）
DOMICILE: Dict[str, List[int]] = {
    "Sun":     [4],             # Leo
    "Moon":    [3],             # Cancer
    "Mercury": [2, 5],          # Gemini, Virgo
    "Venus":   [1, 6],          # Taurus, Libra
    "Mars":    [0, 7],          # Aries, Scorpio
    "Jupiter": [8, 11],         # Sagittarius, Pisces
    "Saturn":  [9, 10],         # Capricorn, Aquarius
}

EXALTATION: Dict[str, int] = {
    "Sun":     0,   # Aries
    "Moon":    1,   # Taurus
    "Mercury": 5,   # Virgo
    "Venus":   11,  # Pisces
    "Mars":    9,   # Capricorn
    "Jupiter": 3,   # Cancer
    "Saturn":  6,   # Libra
}

DETRIMENT: Dict[str, List[int]] = {
    "Sun":     [10],
    "Moon":    [9],
    "Mercury": [8, 11],
    "Venus":   [0, 7],
    "Mars":    [1, 6],
    "Jupiter": [2, 5],
    "Saturn":  [3, 4],
}

FALL: Dict[str, int] = {
    "Sun":     6,
    "Moon":    7,
    "Mercury": 11,
    "Venus":   5,
    "Mars":    3,
    "Jupiter": 9,
    "Saturn":  0,
}

# 行星本命日
PLANET_DAYS: Dict[str, int] = {
    "Sun": 6, "Moon": 0, "Mars": 1, "Mercury": 2,
    "Jupiter": 3, "Venus": 4, "Saturn": 5,
}  # 0=週一 … 6=週日

# Cazimi / Combustion 容許度
CAZIMI_ORB: float = 0.283   # 17'
COMBUSTION_ORB: float = 8.5  # 8°30'
UNDER_BEAMS_ORB: float = 17.0

# Via Combusta（焦灼帶）
VIA_COMBUSTA_START: float = 195.0   # Libra 15°
VIA_COMBUSTA_END: float = 225.0     # Scorpio 15°


# ============================================================
# 資料類
# ============================================================

@dataclass
class PlanetPosition:
    """行星位置資料。"""
    name: str
    longitude: float
    sign_index: int
    sign: str
    sign_cn: str
    degree_in_sign: float
    speed: float          # 度/天，負值 = 逆行
    is_retrograde: bool
    dignity: str          # "Domicile" / "Exaltation" / "Triplicity" / "Peregrine" / "Detriment" / "Fall"
    dignity_score: int    # +5=Domicile, +4=Exaltation, 0=Peregrine, -2=Detriment, -4=Fall


@dataclass
class MoonCondition:
    """月亮狀態評估。"""
    longitude: float
    sign_index: int
    sign: str
    sign_cn: str
    degree_in_sign: float
    phase: str            # "New", "Waxing Crescent", "First Quarter", "Waxing Gibbous", "Full", "Waning Gibbous", "Last Quarter", "Waning Crescent"
    phase_cn: str
    phase_degrees: float  # 與太陽的角度差（0-360）
    is_waxing: bool
    is_via_combusta: bool
    is_combust: bool
    is_cazimi: bool
    sun_aspect_name: str  # 與太陽的相位名稱
    speed: float
    afflictions: List[str] = field(default_factory=list)   # 凶相描述
    benefic_aspects: List[str] = field(default_factory=list)  # 吉相描述
    overall_quality: str = "Neutral"  # "Excellent" / "Good" / "Neutral" / "Poor" / "Afflicted"


@dataclass
class ElectionalScore:
    """製符時機評分。"""
    total_score: float
    max_score: float
    percentage: float
    grade: str            # "Excellent" / "Good" / "Acceptable" / "Poor" / "Forbidden"
    grade_cn: str
    planet: str
    planet_cn: str
    planet_position: PlanetPosition
    moon_condition: MoonCondition
    checks_passed: List[str]     # 通過的條件（中文描述）
    checks_failed: List[str]     # 未通過的條件（中文描述）
    warnings: List[str]          # 警告（中文）
    is_suitable: bool            # 是否適合製符


@dataclass
class TalismanRecommendation:
    """護符推薦結果。"""
    purpose: str
    purpose_cn: str
    recommended_planets: List[str]
    recommended_planet_cn: List[str]
    planetary_talismans: List[PlanetaryTalisman]
    decan_talisman: Optional[DecanTalisman]       # 目前月亮所在 Decan
    next_windows: List["ElectionalWindow"]         # 未來最佳時機
    primary_recommendation: str                    # 首選行星
    primary_recommendation_cn: str


@dataclass
class ElectionalWindow:
    """未來製符時機窗口。"""
    dt_utc: datetime
    jd: float
    planet: str
    planet_cn: str
    score: float
    grade: str
    grade_cn: str
    moon_longitude: float
    moon_sign: str
    moon_sign_cn: str
    planet_longitude: float
    planet_sign: str
    planet_dignity: str
    moon_phase: str
    moon_phase_cn: str
    is_waxing: bool
    day_of_week: str
    day_of_week_cn: str


# ============================================================
# 計算輔助函式
# ============================================================

def _normalize(deg: float) -> float:
    """正規化至 0–360°。"""
    return deg % 360.0


def _sign_index(lon: float) -> int:
    return int(_normalize(lon) / 30) % 12


def _sign_name(lon: float) -> str:
    return ZODIAC_SIGNS[_sign_index(lon)]


def _arc_sep(a: float, b: float) -> float:
    """最短弧距（0–180°）。"""
    diff = abs(_normalize(a) - _normalize(b))
    return min(diff, 360.0 - diff)


def _jd_from_dt(dt: datetime) -> float:
    """將 UTC datetime 轉換為儒略日。"""
    return swe.julday(
        dt.year, dt.month, dt.day,
        dt.hour + dt.minute / 60.0 + dt.second / 3600.0,
    )


def _planet_lon_speed(planet_id: int, jd: float) -> Tuple[float, float]:
    """返回 (longitude, speed_deg/day)。"""
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    xx, _ = swe.calc_ut(jd, planet_id, flags)
    return float(xx[0]), float(xx[3])


def _compute_all_planets(jd: float) -> Dict[str, Tuple[float, float]]:
    """計算所有七行星的 (longitude, speed)。"""
    result: Dict[str, Tuple[float, float]] = {}
    for pname, pid in PLANET_IDS.items():
        try:
            lon, spd = _planet_lon_speed(pid, jd)
            result[pname] = (lon, spd)
        except Exception:
            pass
    return result


# ============================================================
# 行星尊貴計算
# ============================================================

def get_planet_dignity(planet: str, longitude: float) -> Tuple[str, int]:
    """
    計算行星在指定黃道經度的尊貴狀態。

    Parameters
    ----------
    planet : str
        行星英文名稱
    longitude : float
        黃道經度（0-360°）

    Returns
    -------
    Tuple[str, int]
        (尊貴名稱, 分數)
        分數：Domicile=+5, Exaltation=+4, Peregrine=0, Detriment=-2, Fall=-4
    """
    sign_idx = _sign_index(longitude)

    if sign_idx in DOMICILE.get(planet, []):
        return "Domicile", 5
    if sign_idx == EXALTATION.get(planet, -1):
        return "Exaltation", 4
    if sign_idx in DETRIMENT.get(planet, []):
        return "Detriment", -2
    if sign_idx == FALL.get(planet, -1):
        return "Fall", -4
    return "Peregrine", 0


def get_planet_position(planet: str, jd: float) -> PlanetPosition:
    """
    取得行星在指定時刻的完整位置資料。

    Parameters
    ----------
    planet : str
        行星英文名稱
    jd : float
        儒略日

    Returns
    -------
    PlanetPosition
    """
    pid = PLANET_IDS[planet]
    lon, spd = _planet_lon_speed(pid, jd)
    sign_idx = _sign_index(lon)
    sign = ZODIAC_SIGNS[sign_idx]
    dignity, score = get_planet_dignity(planet, lon)

    return PlanetPosition(
        name=planet,
        longitude=lon,
        sign_index=sign_idx,
        sign=sign,
        sign_cn=ZODIAC_SIGNS_CN.get(sign, sign),
        degree_in_sign=round(lon % 30, 4),
        speed=round(spd, 6),
        is_retrograde=(spd < 0),
        dignity=dignity,
        dignity_score=score,
    )


# ============================================================
# 月亮狀態評估
# ============================================================

def get_moon_condition(jd: float, planet_positions: Optional[Dict[str, Tuple[float, float]]] = None) -> MoonCondition:
    """
    評估月亮在指定時刻的魔法狀態。

    Parameters
    ----------
    jd : float
        儒略日
    planet_positions : dict, optional
        預計算的行星位置 {planet_name: (lon, speed)}

    Returns
    -------
    MoonCondition
    """
    if planet_positions is None:
        planet_positions = _compute_all_planets(jd)

    moon_lon = planet_positions["Moon"][0] if "Moon" in planet_positions else 0.0
    moon_spd = planet_positions["Moon"][1] if "Moon" in planet_positions else 13.0
    sun_lon  = planet_positions["Sun"][0]  if "Sun"  in planet_positions else 0.0

    sign_idx = _sign_index(moon_lon)
    sign = ZODIAC_SIGNS[sign_idx]

    # 月相計算
    phase_deg = _normalize(moon_lon - sun_lon)
    is_waxing = phase_deg < 180.0

    if phase_deg < 15:
        phase, phase_cn = "New Moon", "新月"
    elif phase_deg < 90:
        phase, phase_cn = "Waxing Crescent", "漸盈眉月"
    elif phase_deg < 105:
        phase, phase_cn = "First Quarter", "上弦月"
    elif phase_deg < 180:
        phase, phase_cn = "Waxing Gibbous", "漸盈凸月"
    elif phase_deg < 195:
        phase, phase_cn = "Full Moon", "望月"
    elif phase_deg < 270:
        phase, phase_cn = "Waning Gibbous", "漸虧凸月"
    elif phase_deg < 285:
        phase, phase_cn = "Last Quarter", "下弦月"
    else:
        phase, phase_cn = "Waning Crescent", "漸虧眉月"

    # Via Combusta 判斷
    is_via_combusta = VIA_COMBUSTA_START <= moon_lon < VIA_COMBUSTA_END

    # Combust / Cazimi 判斷
    sun_sep = _arc_sep(moon_lon, sun_lon)
    is_cazimi    = sun_sep <= CAZIMI_ORB
    is_combust   = (not is_cazimi) and (sun_sep <= COMBUSTION_ORB)

    # 太陽相位名稱
    if is_cazimi:
        sun_aspect_name = "Cazimi（心合）"
    elif is_combust:
        sun_aspect_name = "Combust（焦傷）"
    elif sun_sep <= UNDER_BEAMS_ORB:
        sun_aspect_name = "Under the Beams（光束下）"
    elif phase_deg < 10 or phase_deg > 350:
        sun_aspect_name = "Conjunction（合相）"
    elif 56 <= phase_deg <= 64:
        sun_aspect_name = "Sextile（六合）"
    elif 86 <= phase_deg <= 94:
        sun_aspect_name = "Square（四分）"
    elif 116 <= phase_deg <= 124:
        sun_aspect_name = "Trine（三合）"
    elif 170 <= phase_deg <= 190:
        sun_aspect_name = "Opposition（對分）"
    else:
        sun_aspect_name = "—"

    # 評估凶吉相位（與其他行星）
    afflictions: List[str] = []
    benefic_aspects_list: List[str] = []
    malefics = ["Mars", "Saturn"]
    benefics = ["Venus", "Jupiter"]

    for pname, (plon, _) in planet_positions.items():
        if pname in ("Moon", "Sun"):
            continue
        sep = _arc_sep(moon_lon, plon)
        diff = _normalize(moon_lon - plon)
        aspect_name = None
        if sep <= 8:
            aspect_name = "合相"
        elif 52 <= sep <= 68:
            aspect_name = "六合"
        elif 82 <= sep <= 98:
            aspect_name = "四分"
        elif 112 <= sep <= 128:
            aspect_name = "三合"
        elif 172 <= sep <= 188:
            aspect_name = "對分"

        if aspect_name:
            is_applying = (diff * moon_spd) > 0
            applying_str = "施加" if is_applying else "分離"
            desc = f"月亮-{PLANET_CN.get(pname, pname)} {applying_str}{aspect_name}（{sep:.1f}°）"
            if pname in malefics and aspect_name in ("四分", "對分", "合相"):
                afflictions.append(desc)
            elif pname in benefics and aspect_name in ("三合", "六合", "合相"):
                benefic_aspects_list.append(desc)

    # Via Combusta
    if is_via_combusta:
        afflictions.append(f"月亮在焦灼帶（Libra 15°–Scorpio 15°，位置 {moon_lon:.1f}°）")
    if is_combust:
        afflictions.append(f"月亮焦傷（與太陽相距 {sun_sep:.1f}°）")

    # 落陷
    moon_dig, _ = get_planet_dignity("Moon", moon_lon)
    if moon_dig in ("Detriment", "Fall"):
        afflictions.append(f"月亮{moon_dig}（位於{ZODIAC_SIGNS_CN.get(sign, sign)}）")

    # 整體評質
    if is_cazimi:
        overall = "Excellent"
    elif len(afflictions) >= 3 or is_combust or is_via_combusta:
        overall = "Afflicted"
    elif len(afflictions) >= 2:
        overall = "Poor"
    elif len(afflictions) == 1 and len(benefic_aspects_list) == 0:
        overall = "Neutral"
    elif len(benefic_aspects_list) >= 2:
        overall = "Excellent"
    elif len(benefic_aspects_list) >= 1:
        overall = "Good"
    else:
        overall = "Neutral"

    return MoonCondition(
        longitude=moon_lon,
        sign_index=sign_idx,
        sign=sign,
        sign_cn=ZODIAC_SIGNS_CN.get(sign, sign),
        degree_in_sign=round(moon_lon % 30, 4),
        phase=phase,
        phase_cn=phase_cn,
        phase_degrees=round(phase_deg, 2),
        is_waxing=is_waxing,
        is_via_combusta=is_via_combusta,
        is_combust=is_combust,
        is_cazimi=is_cazimi,
        sun_aspect_name=sun_aspect_name,
        speed=round(moon_spd, 4),
        afflictions=afflictions,
        benefic_aspects=benefic_aspects_list,
        overall_quality=overall,
    )


# ============================================================
# 電擇評分（核心 Picatrix 規則）
# ============================================================

def evaluate_electional_moment(
    planet: str,
    jd: float,
    latitude: float = 22.28,
    longitude_geo: float = 114.17,
    check_rising: bool = True,
) -> ElectionalScore:
    """
    評估某時刻製作指定行星護符的電擇適宜程度。

    嚴格遵循 Picatrix 卷二第十章與 Lilly《基督教占星》規則。

    Parameters
    ----------
    planet : str
        目標行星（護符主星）
    jd : float
        儒略日（UT）
    latitude : float
        觀測地緯度（度）
    longitude_geo : float
        觀測地經度（度）
    check_rising : bool
        是否檢查行星升降（需要地理座標）

    Returns
    -------
    ElectionalScore
    """
    # 取得行星位置
    positions = _compute_all_planets(jd)

    if planet not in positions:
        # 回退計算
        try:
            lon, spd = _planet_lon_speed(PLANET_IDS[planet], jd)
            positions[planet] = (lon, spd)
        except Exception:
            positions[planet] = (0.0, 1.0)

    p_lon, p_spd = positions[planet]
    p_pos = get_planet_position(planet, jd)
    moon_cond = get_moon_condition(jd, positions)

    checks_passed: List[str] = []
    checks_failed: List[str] = []
    warnings: List[str] = []
    score = 0.0
    max_score = 100.0

    # ── 規則 1：行星尊貴（最重要，40分）────────────────────
    dignity = p_pos.dignity
    if dignity == "Domicile":
        score += 40
        checks_passed.append(f"{PLANET_CN.get(planet, planet)}位於本位（{p_pos.sign_cn}）✦✦✦")
    elif dignity == "Exaltation":
        score += 35
        checks_passed.append(f"{PLANET_CN.get(planet, planet)}位於擢升（{p_pos.sign_cn}）✦✦")
    elif dignity == "Peregrine":
        score += 15
        warnings.append(f"{PLANET_CN.get(planet, planet)}漂泊（Peregrine），尊貴較弱")
    elif dignity == "Detriment":
        score += 0
        checks_failed.append(f"{PLANET_CN.get(planet, planet)}落陷（{p_pos.sign_cn}），不宜製符")
    elif dignity == "Fall":
        score += 0
        checks_failed.append(f"{PLANET_CN.get(planet, planet)}入廟失（{p_pos.sign_cn}），強烈不宜")

    # ── 規則 2：行星逆行（-15分 penalty）──────────────────────
    if p_pos.is_retrograde:
        score -= 10
        warnings.append(f"{PLANET_CN.get(planet, planet)}逆行中（Rx），護符效力減弱")
    else:
        score += 10
        checks_passed.append(f"{PLANET_CN.get(planet, planet)}順行✓")

    # ── 規則 3：行星是否在光束下（Combust / Under Beams）───────
    if planet != "Moon":
        sun_lon = positions.get("Sun", (0.0, 0.0))[0]
        sep_sun = _arc_sep(p_lon, sun_lon)
        if sep_sun <= CAZIMI_ORB:
            score += 8
            checks_passed.append(f"{PLANET_CN.get(planet, planet)}心合太陽（Cazimi），力量加強！")
        elif sep_sun <= COMBUSTION_ORB:
            score -= 8
            checks_failed.append(f"{PLANET_CN.get(planet, planet)}焦傷（Combust，{sep_sun:.1f}°），不宜")
        elif sep_sun <= UNDER_BEAMS_ORB:
            score -= 3
            warnings.append(f"{PLANET_CN.get(planet, planet)}在太陽光束下（{sep_sun:.1f}°），略微減弱")

    # ── 規則 4：月亮狀態（20分）──────────────────────────────
    moon_quality = moon_cond.overall_quality
    if moon_quality == "Excellent":
        score += 20
        checks_passed.append(f"月亮狀態：絕佳（{moon_cond.phase_cn}，{moon_cond.sign_cn}）✦✦")
    elif moon_quality == "Good":
        score += 15
        checks_passed.append(f"月亮狀態：良好（{moon_cond.phase_cn}）✦")
    elif moon_quality == "Neutral":
        score += 8
        warnings.append(f"月亮狀態：一般（{moon_cond.phase_cn}）")
    elif moon_quality == "Poor":
        score += 3
        checks_failed.append(f"月亮狀態欠佳：{'; '.join(moon_cond.afflictions[:2])}")
    else:  # Afflicted
        score -= 5
        checks_failed.append(f"月亮受凶：{'; '.join(moon_cond.afflictions[:2])}")

    # ── 規則 5：月亮是否漸盈（+5分）──────────────────────────
    if moon_cond.is_waxing:
        score += 5
        checks_passed.append("月亮漸盈（有利護符製作）✓")
    else:
        warnings.append("月亮漸虧（製作護符需謹慎，護符效力可能較弱）")

    # ── 規則 6：月亮非在焦灼帶（Via Combusta）───────────────
    if moon_cond.is_via_combusta:
        score -= 10
        checks_failed.append("月亮在焦灼帶（Via Combusta，Libra 15°–Scorpio 15°），Picatrix 嚴格禁止！")
    else:
        score += 5
        checks_passed.append("月亮不在焦灼帶✓")

    # ── 規則 7：吉利相位加分（+5至+10）────────────────────
    if moon_cond.benefic_aspects:
        score += min(10, len(moon_cond.benefic_aspects) * 5)
        checks_passed.append(f"月亮吉相：{'; '.join(moon_cond.benefic_aspects[:2])}")

    # ── 規則 8：凶星凶相減分（-5至-15）────────────────────
    if moon_cond.afflictions:
        score -= min(15, len(moon_cond.afflictions) * 5)

    # 正規化分數
    score = max(0.0, min(100.0, score))
    percentage = score

    # 評級
    if percentage >= 85:
        grade, grade_cn = "Excellent", "絕佳"
    elif percentage >= 70:
        grade, grade_cn = "Good", "良好"
    elif percentage >= 50:
        grade, grade_cn = "Acceptable", "可用"
    elif percentage >= 30:
        grade, grade_cn = "Poor", "欠佳"
    else:
        grade, grade_cn = "Forbidden", "禁忌"

    is_suitable = percentage >= 50 and not moon_cond.is_via_combusta

    return ElectionalScore(
        total_score=round(score, 1),
        max_score=max_score,
        percentage=round(percentage, 1),
        grade=grade,
        grade_cn=grade_cn,
        planet=planet,
        planet_cn=PLANET_CN.get(planet, planet),
        planet_position=p_pos,
        moon_condition=moon_cond,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
        warnings=warnings,
        is_suitable=is_suitable,
    )


# ============================================================
# 最佳製符時機搜尋
# ============================================================

def find_talisman_windows(
    planet: str,
    start_dt: Optional[datetime] = None,
    days_ahead: int = 30,
    step_hours: int = 4,
    min_score: float = 60.0,
) -> List[ElectionalWindow]:
    """
    掃描未來時間，找到最佳製作指定行星護符的時機。

    Parameters
    ----------
    planet : str
        目標行星
    start_dt : datetime, optional
        搜尋起始時間（UTC），預設為現在
    days_ahead : int
        向前搜尋天數（預設 30 天）
    step_hours : int
        時間步長（小時）
    min_score : float
        最低分數門檻（0-100）

    Returns
    -------
    list[ElectionalWindow]
        按時間排序
    """
    if start_dt is None:
        start_dt = datetime.now(tz=timezone.utc)
    elif start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)

    windows: List[ElectionalWindow] = []
    step = timedelta(hours=step_hours)
    total_steps = int(days_ahead * 24 / step_hours)

    # 星期幾中文
    weekday_cn = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
    weekday_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for i in range(total_steps):
        dt = start_dt + i * step
        jd = _jd_from_dt(dt)

        try:
            escore = evaluate_electional_moment(planet, jd)
        except Exception:
            continue

        if escore.percentage < min_score:
            continue

        p_pos = escore.planet_position
        moon = escore.moon_condition
        dow = dt.weekday()  # 0=Monday

        windows.append(ElectionalWindow(
            dt_utc=dt,
            jd=jd,
            planet=planet,
            planet_cn=PLANET_CN.get(planet, planet),
            score=escore.percentage,
            grade=escore.grade,
            grade_cn=escore.grade_cn,
            moon_longitude=moon.longitude,
            moon_sign=moon.sign,
            moon_sign_cn=moon.sign_cn,
            planet_longitude=p_pos.longitude,
            planet_sign=p_pos.sign,
            planet_dignity=p_pos.dignity,
            moon_phase=moon.phase,
            moon_phase_cn=moon.phase_cn,
            is_waxing=moon.is_waxing,
            day_of_week=weekday_en[dow],
            day_of_week_cn=weekday_cn[dow],
        ))

    # 按分數排序，再按時間排序
    windows.sort(key=lambda w: (-w.score, w.jd))
    return windows[:20]   # 最多返回 20 個


# ============================================================
# 護符推薦引擎
# ============================================================

def recommend_talisman(
    purpose: str,
    jd: Optional[float] = None,
) -> TalismanRecommendation:
    """
    根據目的推薦最適護符及製符資訊。

    Parameters
    ----------
    purpose : str
        目的關鍵字（英文，如 "love", "wealth", "protection" 等）
    jd : float, optional
        查詢時的儒略日（用於計算當前月亮 Decan）

    Returns
    -------
    TalismanRecommendation
    """
    if jd is None:
        jd = _jd_from_dt(datetime.now(tz=timezone.utc))

    recommended_planets = get_recommended_planets(purpose)
    purpose_cn = PURPOSE_LABELS_CN.get(purpose, purpose)

    # 取得行星護符資料
    planetary_talismans: List[PlanetaryTalisman] = [
        PLANETARY_TALISMAN_BY_PLANET[p]
        for p in recommended_planets
        if p in PLANETARY_TALISMAN_BY_PLANET
    ]

    # 取得當前月亮所在 Decan
    positions = _compute_all_planets(jd)
    moon_lon = positions.get("Moon", (0.0, 0.0))[0]
    decan_talisman = get_decan_by_longitude(moon_lon)

    # 尋找未來最佳時機（用第一推薦行星）
    primary_planet = recommended_planets[0] if recommended_planets else "Jupiter"
    next_windows = find_talisman_windows(primary_planet, days_ahead=14, step_hours=6)

    primary_cn = PLANET_CN.get(primary_planet, primary_planet)

    return TalismanRecommendation(
        purpose=purpose,
        purpose_cn=purpose_cn,
        recommended_planets=recommended_planets,
        recommended_planet_cn=[PLANET_CN.get(p, p) for p in recommended_planets],
        planetary_talismans=planetary_talismans,
        decan_talisman=decan_talisman,
        next_windows=next_windows,
        primary_recommendation=primary_planet,
        primary_recommendation_cn=primary_cn,
    )
