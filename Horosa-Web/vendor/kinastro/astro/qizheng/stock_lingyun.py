"""
七政四餘金融占星：宏觀股市股票靈運計算模組。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone as tz_cls
from typing import Optional

import swisseph as swe

from .constants import FOUR_REMAINDERS, SEVEN_GOVERNORS, TWELVE_PALACES
from .financial.transit_search import find_closest_event


REGION_PRESETS = {
    "香港 Hong Kong": {"lat": 22.3, "lon": 114.2},
    "美國 New York": {"lat": 40.7128, "lon": -74.0060},
    "中國內地 Shanghai": {"lat": 31.2304, "lon": 121.4737},
    "日本 Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "歐洲 London": {"lat": 51.5074, "lon": -0.1278},
}

_KEY_HOUSES = (2, 5, 3, 4)
_BENEFICS = {"木星", "金星", "太陽", "太陰"}
_MALEFICS = {"火星", "土星", "天王", "海王", "冥王"}

# 吳師青《天運占星學》十二宮含義
_WU_TWELVE_HOUSES: dict[int, dict] = {
    1:  {"wu_name": "人民宮", "summary": "代表地區、民衆", "keywords": ["社會康樂", "地區繁榮"], "verb": "增強"},
    2:  {"wu_name": "經濟宮", "summary": "代表財富、貨幣", "keywords": ["銀行", "證券", "股市", "珠寶", "物資", "工商業"], "verb": "拓展"},
    3:  {"wu_name": "新聞宮", "summary": "代表正義、公理", "keywords": ["報業", "交通", "運輸", "鐵路", "電話", "倉塢", "汽車", "織造", "航空", "公用事業", "無線電"], "verb": "躍進"},
    4:  {"wu_name": "地產宮", "summary": "代表裕民、厚生", "keywords": ["石油", "礦產", "地產", "房屋", "建築", "酒店", "橡膠"], "verb": "繁榮"},
    5:  {"wu_name": "娛樂宮", "summary": "代表樂育、健強", "keywords": ["教育", "文化", "股票", "賽馬", "賽球", "音樂", "戲劇", "電影", "出生率", "體育"], "verb": "擴展"},
    6:  {"wu_name": "勞動宮", "summary": "代表生計、安定", "keywords": ["員工利益", "公共衛生", "調整工作", "保持秩序"], "verb": "改進"},
    7:  {"wu_name": "國際宮", "summary": "代表親仁、睦鄰", "keywords": ["考察業務", "推廣外貿", "出入口商", "加強活躍", "訂立條約", "增進友誼"], "verb": "計劃"},
    8:  {"wu_name": "遺產宮", "summary": "代表課稅、處置", "keywords": ["充實稅收", "人口生死", "保險商", "代理商"], "verb": "措施"},
    9:  {"wu_name": "船務宮", "summary": "代表旅遊、利濟", "keywords": ["宗教", "旅業", "船務", "運輸"], "verb": "發揚"},
    10: {"wu_name": "官商宮", "summary": "代表統治、貿易", "keywords": ["國王", "總統", "首相", "總督", "工商", "經濟", "財團", "巨賈"], "verb": "推進"},
    11: {"wu_name": "議會宮", "summary": "代表民意、羣情", "keywords": ["辯論", "選舉", "會議", "立法", "行政"], "verb": "興革"},
    12: {"wu_name": "救濟宮", "summary": "代表卹災、賑貧", "keywords": ["慈善機構", "福利事業", "公共醫院", "津貼學校", "育嬰院", "養老院"], "verb": "加強"},
}
_PLANET_SWISS = {
    "天王": swe.URANUS,
    "海王": swe.NEPTUNE,
    "冥王": swe.PLUTO,
}
_SEASONAL_MARKS = (
    ("春分", 0.0, (3, 15), (4, 5)),
    ("夏至", 90.0, (6, 15), (7, 5)),
    ("秋分", 180.0, (9, 15), (10, 5)),
    ("冬至", 270.0, (12, 15), (1, 5)),
)


@dataclass
class _PlanetRow:
    name: str
    longitude: float
    house: int


def _normalize_degree(deg: float) -> float:
    return deg % 360.0


def _angle_diff(a: float, b: float) -> float:
    diff = abs(_normalize_degree(a - b))
    return 360.0 - diff if diff > 180.0 else diff


def _signed_angle_to_target(value: float, target: float) -> float:
    return ((_normalize_degree(value - target) + 180.0) % 360.0) - 180.0


def _find_house(lon: float, cusps: tuple) -> int:
    lon = _normalize_degree(lon)
    for i in range(12):
        start = _normalize_degree(cusps[i])
        end = _normalize_degree(cusps[(i + 1) % 12])
        if start < end:
            if start <= lon < end:
                return i + 1
        elif lon >= start or lon < end:
            return i + 1
    return 1


def _planet_longitudes(jd: float) -> dict[str, float]:
    planets: dict[str, float] = {}
    for name, pid in SEVEN_GOVERNORS.items():
        result, _ = swe.calc_ut(jd, pid)
        planets[name] = _normalize_degree(result[0])

    ketu_result, _ = swe.calc_ut(jd, FOUR_REMAINDERS["計都"])
    ketu_lon = _normalize_degree(ketu_result[0])
    planets["計都"] = ketu_lon
    planets["羅睺"] = _normalize_degree(ketu_lon + 180.0)

    for name in ("月孛", "紫氣"):
        result, _ = swe.calc_ut(jd, FOUR_REMAINDERS[name])
        planets[name] = _normalize_degree(result[0])

    for name, pid in _PLANET_SWISS.items():
        result, _ = swe.calc_ut(jd, pid)
        planets[name] = _normalize_degree(result[0])
    return planets


def _sun_lon(jd: float) -> float:
    result, _ = swe.calc_ut(jd, swe.SUN)
    return _normalize_degree(result[0])


def _moon_sun_phase(jd: float) -> float:
    moon, _ = swe.calc_ut(jd, swe.MOON)
    sun, _ = swe.calc_ut(jd, swe.SUN)
    return _normalize_degree(moon[0] - sun[0])


def _search_minimum(start_jd: float, end_jd: float, eval_func) -> float:
    result = find_closest_event(
        eval_func,
        start_jd=start_jd,
        end_jd=end_jd,
        coarse_step=0.5,
        tolerance=1e-5,
    )
    return result.jd


def _find_ingress_jd(year: int, target_lon: float, window_start: tuple, window_end: tuple) -> float:
    start_jd = swe.julday(year, window_start[0], window_start[1], 0.0)
    end_year = year + 1 if window_end[0] < window_start[0] else year
    end_jd = swe.julday(end_year, window_end[0], window_end[1], 23.99)
    return _search_minimum(start_jd, end_jd, lambda jd: _signed_angle_to_target(_sun_lon(jd), target_lon))


def _jd_to_iso(jd: float) -> str:
    y, m, d, hour = swe.revjul(jd)
    h = int(hour)
    minute = int((hour - h) * 60)
    return f"{y:04d}-{m:02d}-{int(d):02d} {h:02d}:{minute:02d} UTC"


def _build_ingress_chart(year: int, name: str, target_lon: float, lat: float, lon: float, w_start: tuple, w_end: tuple) -> dict:
    jd = _find_ingress_jd(year, target_lon, w_start, w_end)
    cusps, _ = swe.houses(jd, lat, lon, b"P")
    planet_map = _planet_longitudes(jd)
    rows: list[dict] = []
    for pname, plon in planet_map.items():
        house = _find_house(plon, cusps)
        rows.append(
            {
                "planet": pname,
                "longitude": round(plon, 4),
                "degree_in_sign": round(plon % 30.0, 2),
                "house": house,
                "house_name": TWELVE_PALACES[house - 1],
            }
        )
    return {
        "ingress_name": name,
        "target_solar_longitude": target_lon,
        "datetime_utc": _jd_to_iso(jd),
        "julian_day": jd,
        "cusps": [round(_normalize_degree(c), 4) for c in cusps],
        "planets": rows,
    }


def _pick_chart_by_month(charts: dict, month: Optional[int]) -> dict:
    if month is None:
        now = datetime.now(tz=tz_cls.utc)
        month = now.month
    if month in (3, 4, 5):
        return charts["春分"]
    if month in (6, 7, 8):
        return charts["夏至"]
    if month in (9, 10, 11):
        return charts["秋分"]
    return charts["冬至"]


def _classify_score(score: int) -> str:
    if score >= 4:
        return "強烈看漲 (Bullish)"
    if score >= 1:
        return "偏多"
    if score <= -4:
        return "強烈看跌 (Bearish)"
    if score <= -1:
        return "偏空"
    return "中性"


def _find_lunation(year: int, month: int, target: float) -> Optional[float]:
    start_jd = swe.julday(year, month, 1, 0.0)
    if month == 12:
        end_jd = swe.julday(year + 1, 1, 1, 0.0)
    else:
        end_jd = swe.julday(year, month + 1, 1, 0.0)
    best = _search_minimum(start_jd, end_jd, lambda jd: _signed_angle_to_target(_moon_sun_phase(jd), target))
    if abs(_signed_angle_to_target(_moon_sun_phase(best), target)) > 5.0:
        return None
    return best


def _monthly_moon_house_scores(year: int, month: int, cusps: list[float]) -> list[dict]:
    scores: list[dict] = []
    start = swe.julday(year, month, 1, 12.0)
    if month == 12:
        end = swe.julday(year + 1, 1, 1, 12.0)
    else:
        end = swe.julday(year, month + 1, 1, 12.0)

    jd = start
    while jd < end:
        moon, _ = swe.calc_ut(jd, swe.MOON)
        house = _find_house(moon[0], tuple(cusps))
        if house in (2, 5):
            s = 1
        elif house in (3, 4):
            s = 0
        else:
            s = -1
        y, m, d, _ = swe.revjul(jd)
        scores.append({"date": f"{y:04d}-{m:02d}-{int(d):02d}", "moon_house": house, "score": s})
        jd += 1.0
    return scores


def _detect_conjunctions(planets: list[dict], orb: float = 3.0) -> list[dict]:
    conjs: list[dict] = []
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1 = planets[i]
            p2 = planets[j]
            diff = _angle_diff(p1["longitude"], p2["longitude"])
            if diff <= orb:
                conjs.append(
                    {
                        "planets": f"{p1['planet']}-{p2['planet']}",
                        "orb": round(diff, 2),
                        "house_1": p1["house"],
                        "house_2": p2["house"],
                        "in_key_house": p1["house"] in (2, 5) or p2["house"] in (2, 5),
                    }
                )
    return conjs


def calculate_stock_score(solar_chart: dict) -> dict:
    """
    吳師青理論：關鍵宮位（2/5/3/4）以行星角度評分，並輸出完整十二宮資訊。
    """
    planets = solar_chart.get("planets", [])
    if not planets:
        return {
            "total_score": 0,
            "market_view": "中性",
            "house_scores": {},
            "sector_scores": [],
            "twelve_houses": [],
            "aspects": [],
        }

    # 建立宮位 → 行星清單的對照表（全 12 宮）
    house_planets: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    for p in planets:
        h = p["house"]
        if 1 <= h <= 12:
            house_planets[h].append(p["planet"])

    # 關鍵宮位評分（2/5/3/4）
    house_scores: dict[int, int] = {2: 0, 5: 0, 3: 0, 4: 0}
    aspect_rows = []
    for focus in [p for p in planets if p["house"] in _KEY_HOUSES]:
        for other in planets:
            if other["planet"] == focus["planet"]:
                continue
            diff = _angle_diff(focus["longitude"], other["longitude"])
            aspect = None
            score = 0
            if other["planet"] in _BENEFICS and any(abs(diff - a) <= 4.0 for a in (0, 60, 120)):
                score = 2
                aspect = "吉角"
            elif other["planet"] in _MALEFICS and any(abs(diff - a) <= 4.0 for a in (90, 180)):
                score = -2
                aspect = "凶角"
            if score == 0:
                continue
            house_scores[focus["house"]] += score
            aspect_rows.append(
                {
                    "focus_planet": focus["planet"],
                    "focus_house": focus["house"],
                    "other_planet": other["planet"],
                    "angle": round(diff, 2),
                    "score": score,
                    "aspect_type": aspect,
                }
            )

    total = sum(house_scores.values())

    # 關鍵宮位板塊對照
    key_sectors = {
        2: ["金融", "銀行", "證券", "保險", "地產"],
        5: ["娛樂", "遊戲", "科技成長", "消費可選"],
        3: ["交通", "物流", "通訊", "媒體"],
        4: ["能源", "建築", "公用事業", "內需民生"],
    }
    sector_scores = []
    for house, names in key_sectors.items():
        sector_scores.append(
            {
                "house": house,
                "house_name": TWELVE_PALACES[house - 1],
                "score": house_scores.get(house, 0),
                "view": _classify_score(house_scores.get(house, 0)),
                "sectors": names,
            }
        )

    # 完整十二宮資訊（含吳師青含義）
    twelve_houses = []
    for h in range(1, 13):
        wu = _WU_TWELVE_HOUSES[h]
        score = house_scores.get(h, None)
        twelve_houses.append(
            {
                "house": h,
                "palace_name": TWELVE_PALACES[h - 1],
                "wu_name": wu["wu_name"],
                "summary": wu["summary"],
                "keywords": wu["keywords"],
                "verb": wu["verb"],
                "planets": house_planets[h],
                "score": score,
                "view": _classify_score(score) if score is not None else "—",
                "is_key_house": h in _KEY_HOUSES,
            }
        )

    return {
        "total_score": total,
        "market_view": _classify_score(total),
        "house_scores": house_scores,
        "sector_scores": sector_scores,
        "twelve_houses": twelve_houses,
        "aspects": aspect_rows,
    }


def get_four_great_transits(year: int, lat: float = 22.3, lon: float = 114.2) -> str:
    """
    四大天運統運（土星、木星、天王、海王）進關鍵宮位長期趨勢。
    """
    spring_name, spring_target, spring_start, spring_end = _SEASONAL_MARKS[0]
    spring = _build_ingress_chart(year, spring_name, spring_target, lat, lon, spring_start, spring_end)
    planets = {p["planet"]: p for p in spring["planets"]}
    lines = []
    wording = {
        "土星": {2: "土星入第2宮 → 地產、證券長期繁盛但估值偏保守", 5: "土星入第5宮 → 投機降溫，娛樂題材分化", 3: "土星入第3宮 → 物流、通訊走向規範化", 4: "土星入第4宮 → 基建與公用事業偏穩健"},
        "木星": {2: "木星入第2宮 → 金融與資產市場擴張", 5: "木星入第5宮 → 成長股與娛樂板塊活躍", 3: "木星入第3宮 → 交易量與資訊流增強", 4: "木星入第4宮 → 地產、民生消費回暖"},
        "天王": {2: "天王入第2宮 → 金融科技、數位資產波動放大", 5: "天王入第5宮 → 新題材與高波動投機潮", 3: "天王入第3宮 → 通訊科技創新加速", 4: "天王入第4宮 → 能源/基建結構重組"},
        "海王": {2: "海王入第2宮 → 資產定價偏虛，題材化走勢增強", 5: "海王入第5宮 → 娛樂與概念股情緒行情突出", 3: "海王入第3宮 → 資訊真假混雜，需控風險", 4: "海王入第4宮 → 地產與公用事業政策預期主導"},
    }
    for name in ("土星", "木星", "天王", "海王"):
        p = planets.get(name)
        if not p:
            continue
        house = p["house"]
        line = wording.get(name, {}).get(house, f"{name}入第{house}宮 → 對宏觀股市形成中長期結構影響")
        lines.append(line)
    return "\n".join(lines)


def get_stock_lingyun_chart(year: int, month: int = None, lat: float = 22.3, lon: float = 114.2) -> dict:
    """
    回傳宏觀股市股票靈運主資料：
    - 春分/夏至/秋分/冬至太陽圖表
    - 關鍵宮位評分
    - 四大天運統運
    - 新月/滿月與本月趨勢
    - 主要會合
    """
    swe.set_ephe_path("")
    charts = {}
    for name, target, w_start, w_end in _SEASONAL_MARKS:
        charts[name] = _build_ingress_chart(year, name, target, lat, lon, w_start, w_end)

    selected = _pick_chart_by_month(charts, month)
    score = calculate_stock_score(selected)
    conjunctions = _detect_conjunctions(selected["planets"])

    if month is None:
        month = datetime.now(tz=tz_cls.utc).month
    new_moon_jd = _find_lunation(year, month, 0.0)
    full_moon_jd = _find_lunation(year, month, 180.0)
    spring_sun = next((p["longitude"] for p in charts["春分"]["planets"] if p["planet"] == "太陽"), 0.0)

    def _lunation_payload(name: str, jd: Optional[float]) -> Optional[dict]:
        if jd is None:
            return None
        moon, _ = swe.calc_ut(jd, swe.MOON)
        moon_lon = _normalize_degree(moon[0])
        diff_to_solar = _angle_diff(moon_lon, spring_sun)
        if any(abs(diff_to_solar - x) <= 4.0 for x in (0, 60, 120)):
            trend_score = 1
        elif any(abs(diff_to_solar - x) <= 4.0 for x in (90, 180)):
            trend_score = -1
        else:
            trend_score = 0
        return {
            "event": name,
            "datetime_utc": _jd_to_iso(jd),
            "moon_longitude": round(moon_lon, 4),
            "aspect_to_spring_sun": round(diff_to_solar, 2),
            "trend_score": trend_score,
        }

    new_moon = _lunation_payload("新月", new_moon_jd)
    full_moon = _lunation_payload("滿月", full_moon_jd)
    month_trend_score = (new_moon or {}).get("trend_score", 0) + (full_moon or {}).get("trend_score", 0)
    month_trend = _classify_score(month_trend_score)
    moon_house_daily = _monthly_moon_house_scores(year, month, selected["cusps"])

    return {
        "year": year,
        "month": month,
        "location": {"lat": lat, "lon": lon},
        "solar_ingress_charts": charts,
        "selected_chart": selected,
        "stock_score": score,
        "four_great_transits": get_four_great_transits(year, lat=lat, lon=lon),
        "lunation": {
            "new_moon": new_moon,
            "full_moon": full_moon,
            "monthly_trend_score": month_trend_score,
            "monthly_trend_view": month_trend,
            "daily_moon_house_scores": moon_house_daily,
        },
        "major_conjunctions": conjunctions,
    }
