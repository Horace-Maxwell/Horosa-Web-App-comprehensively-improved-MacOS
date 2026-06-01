"""七政四餘財富能量分層評分引擎。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..calculator import PlanetPosition


ASPECT_WEIGHTS = {
    0.0: 2.0,
    60.0: 1.0,
    90.0: -1.8,
    120.0: 1.6,
    180.0: -1.8,
}

WEALTH_BASE_SCORES = {
    "太陽": 1.0,
    "太陰": 1.0,
    "木星": 3.0,
    "金星": 2.0,
    "水星": 1.0,
    "火星": -1.0,
    "土星": -1.0,
    "羅睺": 2.0,
    "計都": -1.0,
    "月孛": 1.0,
    "紫氣": 3.0,
}

DIGNITY_MAP = {
    "木星": {"射手": 2, "雙魚": 2, "巨蟹": 1, "雙子": -1, "處女": -2},
    "土星": {"摩羯": 2, "水瓶": 2, "天秤": 1, "牡羊": -2, "巨蟹": -1},
    "金星": {"金牛": 2, "天秤": 2, "雙魚": 1, "牡羊": -2, "天蠍": -2},
    "火星": {"牡羊": 2, "天蠍": 2, "摩羯": 1, "金牛": -2, "巨蟹": -2},
    "水星": {"處女": 2, "雙子": 2, "水瓶": 1, "射手": -1, "雙魚": -2},
    "太陽": {"獅子": 2, "牡羊": 1, "水瓶": -1, "天秤": -2},
    "太陰": {"巨蟹": 2, "金牛": 1, "摩羯": -2, "天蠍": -1},
}

SIGN_RULER = {
    0: "火星",  # 牡羊
    1: "金星",  # 金牛
    2: "水星",  # 雙子
    3: "太陰",  # 巨蟹
    4: "太陽",  # 獅子
    5: "水星",  # 處女
    6: "金星",  # 天秤
    7: "火星",  # 天蠍
    8: "木星",  # 射手
    9: "土星",  # 摩羯
    10: "土星",  # 水瓶
    11: "木星",  # 雙魚
}

KEY_HOUSES = (2, 8, 10, 11)
PLANET_STRENGTH_NORMALIZER = 4.0


@dataclass
class WealthScoreBreakdown:
    base_score: float
    dignity_score: float
    aspect_score: float
    house_lord_score: float

    @property
    def total_score(self) -> float:
        return self.base_score + self.dignity_score + self.aspect_score + self.house_lord_score


def _normalize_degree(value: float) -> float:
    return value % 360.0


def _angle_diff(a: float, b: float) -> float:
    diff = abs(_normalize_degree(a - b))
    return 360.0 - diff if diff > 180.0 else diff


def _orb_decay(diff_to_aspect: float, orb: float) -> float:
    if diff_to_aspect >= orb:
        return 0.0
    return max(0.0, 1.0 - (diff_to_aspect / orb))


def _planet_dignity_score(p: PlanetPosition) -> float:
    mapping = DIGNITY_MAP.get(p.name, {})
    for sign_zh, score in mapping.items():
        if sign_zh in p.sign_chinese:
            return float(score)
    return 0.0


def _get_house_no(lon: float, cusps: Iterable[float]) -> int:
    cusp_values = tuple(cusps)
    lon = _normalize_degree(lon)
    for i in range(12):
        start = _normalize_degree(cusp_values[i])
        end = _normalize_degree(cusp_values[(i + 1) % 12])
        if start < end:
            if start <= lon < end:
                return i + 1
        elif lon >= start or lon < end:
            return i + 1
    return 1


def _find_planet(planets: list[PlanetPosition], name: str) -> PlanetPosition | None:
    return next((p for p in planets if p.name == name), None)


def compute_wealth_score_breakdown(
    planets: list[PlanetPosition],
    cusps: Iterable[float],
    *,
    orb: float = 4.0,
) -> WealthScoreBreakdown:
    """計算分層財富能量分數。"""
    base_score = 0.0
    dignity_score = 0.0

    for p in planets:
        base_score += WEALTH_BASE_SCORES.get(p.name, 0.0)
        dignity_score += _planet_dignity_score(p)

    aspect_score = 0.0
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1 = planets[i]
            p2 = planets[j]
            if p1.name not in WEALTH_BASE_SCORES and p2.name not in WEALTH_BASE_SCORES:
                continue
            diff = _angle_diff(p1.longitude, p2.longitude)
            for target, w in ASPECT_WEIGHTS.items():
                d = abs(diff - target)
                if d <= orb:
                    influence = _orb_decay(d, orb)
                    # 以 4.0 正規化雙星本質強度，使相位權重落在穩定可比區間。
                    planet_strength_factor = (
                        abs(WEALTH_BASE_SCORES.get(p1.name, 0.0)) + abs(WEALTH_BASE_SCORES.get(p2.name, 0.0))
                    ) / PLANET_STRENGTH_NORMALIZER
                    aspect_score += w * influence * max(0.6, planet_strength_factor)
                    break

    house_lord_score = 0.0
    for h in KEY_HOUSES:
        sign_idx = int(_normalize_degree(tuple(cusps)[h - 1]) / 30.0)
        lord = SIGN_RULER[sign_idx]
        lord_planet = _find_planet(planets, lord)
        if lord_planet is None:
            continue
        lord_strength = WEALTH_BASE_SCORES.get(lord_planet.name, 0.0) + _planet_dignity_score(lord_planet)
        lord_house = _get_house_no(lord_planet.longitude, tuple(cusps))
        # 宮主星落入角宮 / 財務關聯宮時加權
        if lord_house in (1, 2, 4, 7, 10, 11):
            lord_strength += 1.0
        if lord_house in KEY_HOUSES:
            lord_strength += 0.8
        house_lord_score += lord_strength * 0.35

    return WealthScoreBreakdown(
        base_score=base_score,
        dignity_score=dignity_score,
        aspect_score=aspect_score,
        house_lord_score=house_lord_score,
    )


def classify_wealth_score(total_score: float) -> tuple[str, str]:
    """將分數映射為中英文字段。"""
    if total_score >= 12:
        return "財富能量強勁", "Strong wealth momentum"
    if total_score >= 6:
        return "財富能量偏強", "Moderately bullish wealth"
    if total_score >= 1:
        return "財富能量中性偏多", "Neutral to mildly positive"
    if total_score > -4:
        return "財富能量偏弱", "Mildly weak wealth momentum"
    return "財富能量受壓", "Suppressed wealth momentum"
