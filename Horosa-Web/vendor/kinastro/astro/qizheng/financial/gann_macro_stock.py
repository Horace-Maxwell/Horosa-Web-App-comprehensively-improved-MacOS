"""
江恩占星（Gann Astrology）x 七政四餘宏觀股市模組。

核心原則：
1) 時間先於價格（Time first, then price）
2) 聖經周期縮放後用於市場時間窗
3) 聖經周期 + 七政四餘流時守照 + 江恩振動（Square of 9）多重共振才採信

新增模組（v2）：
4) 時間＝價格共振（Time-Price Squaring）
5) 江恩角度 / 江恩扇形（Gann Angles / Gann Fan）
6) 江恩自然方格 + 振動（Gann Natural Squares + Vibration）
7) 多重共振 Confluence 評分系統
8) 與 Solar Ingress（節氣入境）結合
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable, Optional, Sequence

import swisseph as swe


_IMPORTANT_STARS = ("木星", "土星", "羅睺", "計都", "月孛", "紫氣")
_ALL_QIZHENG_STARS = ("太陽", "太陰", "水星", "金星", "火星", "木星", "土星", "羅睺", "計都", "月孛", "紫氣")
_IMPORTANT_STAR_BONUS = 1
_CYCLE_SCORE_WEIGHT = 2
_HIGH_RESONANCE_THRESHOLD = 8
_MEDIUM_RESONANCE_THRESHOLD = 4
_WEAK_RESONANCE_THRESHOLD = 1
_SQ9_ANGLE_TO_SQRT_STEP = 1.0 / 180.0
_TRADING_YEAR_DAYS = 252
_TRADING_MONTH_DAYS = 21
_ASPECT_WEIGHTS = {
    0.0: ("合", 2),
    60.0: ("六合", 1),
    90.0: ("刑", -2),
    120.0: ("拱", 2),
    180.0: ("沖", -2),
}

# 常見指數「出生圖」建議（宏觀應用）
GANN_NATAL_PRESETS = {
    "Dow Jones（1896-05-26）": date(1896, 5, 26),
    "S&P 500（1957-03-04）": date(1957, 3, 4),
    "Hang Seng（1969-11-24）": date(1969, 11, 24),
    "TSEC 台灣加權（1967-02-09）": date(1967, 2, 9),
    "SSE Composite（1990-12-19）": date(1990, 12, 19),
}
GANN_NATAL_DEFAULT = "Hang Seng（1969-11-24）"
GANN_NATAL_REFERENCE_PRICES = {
    "Dow Jones（1896-05-26）": 40000.0,
    "S&P 500（1957-03-04）": 5000.0,
    "Hang Seng（1969-11-24）": 20000.0,
    "TSEC 台灣加權（1967-02-09）": 20000.0,
    "SSE Composite（1990-12-19）": 3500.0,
}


@dataclass(frozen=True)
class BiblicalCycle:
    """聖經時間周期定義。"""

    key: str
    name: str
    base_years: float
    source: str
    note: str


_BIBLICAL_CYCLES: tuple[BiblicalCycle, ...] = (
    BiblicalCycle(
        key="day_for_year",
        name="一日頂一年（Ezek. 4:6 / Num. 14:34）",
        base_years=1.0,
        source="《但以理書》《以西結書》與 Gann Robert Gordon 信件",
        note="可映射為 1 年、1 交易年或其比例縮放。",
    ),
    BiblicalCycle(
        key="daniel_70_weeks",
        name="但以理七十個七（490）",
        base_years=490.0,
        source="Dan. 9:24-27 + Gann biblical timing",
        note="常縮放為 49 年、7 年、3.5 年等分形節奏。",
    ),
    BiblicalCycle(
        key="seven_years",
        name="七年周期（7）",
        base_years=7.0,
        source="七數循環（Sabbatic rhythm）",
        note="常見於政策/景氣切換。",
    ),
    BiblicalCycle(
        key="time_times_half",
        name="一載二載半載（3.5 年）",
        base_years=3.5,
        source="Dan. 7:25, 12:7; Rev. 12:14",
        note="中期轉折核心窗。",
    ),
    BiblicalCycle(
        key="prophetic_1260",
        name="1260 預言日（3.5 年）",
        base_years=1260.0 / 360.0,
        source="Rev. 12:6 + 360 天預言年",
        note="可直接轉為 1260 日或比例縮放。",
    ),
    BiblicalCycle(
        key="jubilee_49",
        name="禧年週期（49）",
        base_years=49.0,
        source="Lev. 25",
        note="長期結構性頂底參考。",
    ),
    BiblicalCycle(
        key="jubilee_50",
        name="禧年釋放（50）",
        base_years=50.0,
        source="Lev. 25",
        note="制度切換、流動性再定價。",
    ),
)


def _normalize_degree(value: float) -> float:
    return value % 360.0


def _angle_diff(a: float, b: float) -> float:
    diff = abs(_normalize_degree(a - b))
    return 360.0 - diff if diff > 180.0 else diff


def _to_date(value: date | datetime) -> date:
    return value.date() if isinstance(value, datetime) else value


def _add_business_days(start_date: date, days: int) -> date:
    if days == 0:
        return start_date
    current = start_date
    remaining = days
    step = 1 if days > 0 else -1
    while remaining != 0:
        current += timedelta(days=step)
        if current.weekday() < 5:
            remaining -= step
    return current


def _align_to_business_day(target_date: date, *, direction: int = 1) -> date:
    """將日期對齊至最近的交易日（目前以週一至週五近似）。"""
    aligned = target_date
    step = 1 if direction >= 0 else -1
    while aligned.weekday() >= 5:
        aligned += timedelta(days=step)
    return aligned


def _add_months(anchor: date, months: int) -> date:
    """加減月份，月底日期自動壓至該月最後有效日。"""
    month_index = (anchor.month - 1) + months
    year = anchor.year + month_index // 12
    month = month_index % 12 + 1
    last_day = 31
    while True:
        try:
            return date(year, month, min(anchor.day, last_day))
        except ValueError:
            last_day -= 1
            if last_day < 28:
                raise ValueError(
                    f"unable to add months for anchor day {anchor.day} in target {year:04d}-{month:02d}"
                ) from None


def _coerce_anchor_dates(anchor_date: date | datetime | Sequence[date | datetime]) -> list[date]:
    if isinstance(anchor_date, (date, datetime)):
        return [_to_date(anchor_date)]
    return [_to_date(item) for item in anchor_date]


def _gann_harmonic_label(days: int | None = None, months: int | None = None, years: int | None = None) -> str:
    """將常見 Gann 週期轉為容易閱讀的 harmonic 標籤。"""
    supplied_units = sum(value is not None for value in (days, months, years))
    if supplied_units > 1:
        raise ValueError("only one of days, months, or years may be specified")
    if years is not None:
        return "1年" if years == 1 else f"{years}年"
    if months is not None:
        month_labels = {
            1: "1/12年",
            2: "1/6年",
            3: "1/4年",
            4: "1/3年",
            6: "1/2年",
            9: "3/4年",
            12: "1年",
        }
        return month_labels.get(months, f"{months}個月")
    if days is None:
        return "未分類"
    day_labels = {
        30: "1/12年",
        45: "1/8年",
        52: "52天",
        60: "1/6年",
        90: "1/4年",
        91: "1/4年",
        92: "1/4年",
        120: "1/3年",
        144: "144天",
        180: "1/2年",
        182: "1/2年",
        360: "1年",
        365: "1年",
    }
    return day_labels.get(days, f"{days}天")


def _build_anniversary_row(
    *,
    anchor: date,
    as_of: date,
    due: date,
    window_type: str,
    multiple: int,
    harmonic: str,
    label: str,
    base_days: int | None = None,
    months: int | None = None,
    years: int | None = None,
    use_trading_days: bool = False,
) -> dict:
    return {
        "type": window_type,
        "anchor_date": anchor.isoformat(),
        "due_date": due.isoformat(),
        "distance_days": (due - as_of).days,
        "multiple": multiple,
        "gann_harmonic": harmonic,
        "label": label,
        "base_days": base_days,
        "months": months,
        "years": years,
        "use_trading_days": use_trading_days,
        "note": f"{label}（{harmonic}）",
    }


def _iter_square_of_nine_angles(angle_step: int, angle_system: str) -> list[int]:
    if angle_step <= 0 or 360 % angle_step != 0:
        raise ValueError("angle_step must be a positive divisor of 360")
    valid_angles = list(range(0, 360, angle_step))
    angle_system = angle_system.lower()
    if angle_system == "all":
        return valid_angles
    if angle_system == "cardinal":
        return [angle for angle in valid_angles if angle % 90 == 0]
    if angle_system == "ordinal":
        return [angle for angle in valid_angles if angle % 90 == 45]
    raise ValueError("angle_system must be one of: all, cardinal, ordinal")


def scale_cycle_to_days(
    cycle_years: float,
    *,
    scale: float = 1.0,
    year_basis_days: float = 365.2425,
) -> int:
    """將聖經週期（年）縮放為日數。"""
    return max(1, int(round(cycle_years * year_basis_days * scale)))


def compute_biblical_cycle_dates(
    anchor_date: date | datetime,
    *,
    as_of_date: date | datetime,
    scale: float = 1.0,
    year_basis_days: float = 365.2425,
    use_trading_days: bool = False,
    lookback_years: float = 2.0,
    lookahead_years: float = 2.0,
    max_multiple: int = 12,
) -> list[dict]:
    """
    計算 Gann 聖經周期到期點（可縮放、可切換自然日/交易日）。
    """
    anchor = _to_date(anchor_date)
    as_of = _to_date(as_of_date)
    window_start = as_of - timedelta(days=int(lookback_years * year_basis_days))
    window_end = as_of + timedelta(days=int(lookahead_years * year_basis_days))

    rows: list[dict] = []
    for cycle in _BIBLICAL_CYCLES:
        cycle_days = scale_cycle_to_days(cycle.base_years, scale=scale, year_basis_days=year_basis_days)
        for multiple in range(1, max_multiple + 1):
            total_days = cycle_days * multiple
            if use_trading_days:
                due = _add_business_days(anchor, total_days)
            else:
                due = anchor + timedelta(days=total_days)
            if window_start <= due <= window_end:
                rows.append(
                    {
                        "cycle_key": cycle.key,
                        "cycle_name": cycle.name,
                        "multiple": multiple,
                        "cycle_days": cycle_days,
                        "due_date": due.isoformat(),
                        "distance_days": (due - as_of).days,
                        "source": cycle.source,
                        "note": cycle.note,
                    }
                )
    rows.sort(key=lambda r: abs(r["distance_days"]))
    return rows


def build_market_natal_longitudes(
    market_natal_date: date | datetime,
    *,
    timezone: float = 0.0,
) -> dict[str, float]:
    """建立市場出生圖（七政四餘）星曜經度。"""
    from ..constants import FOUR_REMAINDERS, SEVEN_GOVERNORS

    d = _to_date(market_natal_date)
    local_noon_as_utc = datetime(d.year, d.month, d.day, 12, 0) - timedelta(hours=timezone)
    decimal_hour = local_noon_as_utc.hour + local_noon_as_utc.minute / 60.0
    jd = swe.julday(local_noon_as_utc.year, local_noon_as_utc.month, local_noon_as_utc.day, decimal_hour)

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
    return planets


def get_transit_longitudes(transit_dt: datetime, *, timezone: float = 8.0) -> dict[str, float]:
    """由現有 qizheng_transit 取得流時盤星曜經度。"""
    from ..qizheng_transit import compute_transit

    t = compute_transit(
        year=transit_dt.year,
        month=transit_dt.month,
        day=transit_dt.day,
        hour=transit_dt.hour,
        minute=transit_dt.minute,
        timezone=timezone,
    )
    return {p.name: p.longitude for p in t.planets}


def evaluate_qizheng_resonance(
    natal_longitudes: dict[str, float],
    transit_longitudes: dict[str, float],
    *,
    orb: float = 3.0,
) -> list[dict]:
    """評估七政四餘本命 vs 流時在關鍵星上的守照/相位共振。"""
    rows: list[dict] = []
    for star in _ALL_QIZHENG_STARS:
        natal = natal_longitudes.get(star)
        transit = transit_longitudes.get(star)
        if natal is None or transit is None:
            continue
        diff = _angle_diff(transit, natal)
        matched = None
        for target, (aspect_name, base_score) in _ASPECT_WEIGHTS.items():
            if abs(diff - target) <= orb:
                bonus = _IMPORTANT_STAR_BONUS if star in _IMPORTANT_STARS and base_score > 0 else 0
                score = base_score + bonus
                matched = (aspect_name, score, target)
                break
        if not matched:
            continue
        aspect_name, score, target = matched
        rows.append(
            {
                "star": star,
                "aspect": aspect_name,
                "target_angle": target,
                "actual_angle": round(diff, 2),
                "score": score,
                "is_important_star": star in _IMPORTANT_STARS,
            }
        )
    rows.sort(key=lambda r: (-r["score"], r["actual_angle"]))
    return rows


def compute_square_of_nine_levels(
    reference_price: float,
    *,
    max_ring: int = 2,
    angle_step: int = 45,
    include_descending: bool = False,
    current_price: float | None = None,
    angle_system: str = "all",
    include_metadata: bool = True,
) -> list[dict]:
    """
    以標準平方根螺旋計算 Gann Square of 9 價格層級。

    - 360° = sqrt 軸 +2
    - angle_system 支援 all / cardinal / ordinal
    - current_price 可指定目前價格，回傳相對當前價的上下層級
    """
    if reference_price <= 0:
        raise ValueError("reference_price must be positive")
    if current_price is not None and current_price <= 0:
        raise ValueError("current_price must be positive when provided")

    root = math.sqrt(reference_price)
    center_price = current_price if current_price is not None else reference_price
    center_root = math.sqrt(center_price)
    center_turn = math.floor((center_root - root) / 2.0)
    angles = _iter_square_of_nine_angles(angle_step, angle_system)
    levels: list[dict] = []
    seen: set[tuple[int, int]] = set()
    min_turn = center_turn - max_ring if include_descending else max(0, center_turn)
    max_turn = center_turn + max_ring

    for turn in range(min_turn, max_turn + 1):
        ring = abs(turn - center_turn)
        for angle in angles:
            key = (turn, angle)
            if key in seen:
                continue
            seen.add(key)
            sqrt_value = root + (2.0 * turn) + (angle * _SQ9_ANGLE_TO_SQRT_STEP)
            if sqrt_value <= 0:
                continue
            target = round(sqrt_value * sqrt_value, 4)
            direction = "neutral"
            if target > center_price:
                direction = "up"
            elif target < center_price:
                direction = "down"
            row = {
                "ring": ring,
                "angle": angle,
                "direction": direction,
                "target_price": target,
            }
            if include_metadata:
                if angle % 90 == 0:
                    angle_family = "cardinal"
                elif angle % 90 == 45:
                    angle_family = "ordinal"
                else:
                    angle_family = "other"
                row["angle_system"] = angle_family
                row["turn"] = turn
                row["reference_price"] = round(reference_price, 4)
                row["center_price"] = round(center_price, 4)
                row["price_delta"] = round(target - center_price, 4)
            levels.append(row)

    levels.sort(key=lambda r: (r["target_price"], r["angle"], r["ring"]))
    return levels


def compute_anniversary_dates(
    anchor_date: date | datetime,
    *,
    as_of_date: date | datetime,
    use_trading_days: bool = False,
    lookback_years: float = 2.0,
    lookahead_years: float = 2.0,
    monthly_step: int = 3,
    anchor_dates: Sequence[date | datetime] | None = None,
    include_yearly: bool = True,
    include_monthly: bool = True,
    include_day_windows: bool = True,
    extra_day_windows: Sequence[int] | None = None,
) -> list[dict]:
    """
    計算強化版江恩 Anniversary Dates。

    支援：
    - 多個 anchor dates
    - 年/月份周年窗
    - Gann 常見日數窗口（45/52/90/120/144/180/360 等）
    - 自然日或交易日
    - harmonic 標註
    """
    as_of = _to_date(as_of_date)
    window_start = as_of - timedelta(days=int(lookback_years * 365.2425))
    window_end = as_of + timedelta(days=int(lookahead_years * 365.2425))
    anchors = _coerce_anchor_dates(anchor_dates if anchor_dates is not None else anchor_date)
    day_windows = sorted({45, 52, 90, 91, 92, 120, 144, 180, 182, 360, *(extra_day_windows or ())})

    rows: list[dict] = []

    for anchor in anchors:
        if include_yearly:
            max_year_multiple = max(1, int(math.ceil(lookback_years + lookahead_years)) + 2)
            for multiple in range(1, max_year_multiple + 1):
                if use_trading_days:
                    due = _add_business_days(anchor, multiple * _TRADING_YEAR_DAYS)
                else:
                    try:
                        due = date(anchor.year + multiple, anchor.month, anchor.day)
                    except ValueError:
                        due = date(anchor.year + multiple, anchor.month, 28)
                if window_start <= due <= window_end:
                    rows.append(
                        _build_anniversary_row(
                            anchor=anchor,
                            as_of=as_of,
                            due=due,
                            window_type="yearly_anniversary",
                            multiple=multiple,
                            harmonic=_gann_harmonic_label(years=multiple),
                            label="年度週年時間窗",
                            years=multiple,
                            base_days=_TRADING_YEAR_DAYS if use_trading_days else 365,
                            use_trading_days=use_trading_days,
                        )
                    )

        if include_monthly and monthly_step > 0:
            max_month_multiple = int(math.ceil((lookback_years + lookahead_years + 2) * 12 / monthly_step))
            for multiple in range(1, max_month_multiple + 1):
                total_months = monthly_step * multiple
                due = _add_months(anchor, total_months)
                if use_trading_days:
                    due = _align_to_business_day(due)
                if window_start <= due <= window_end:
                    rows.append(
                        _build_anniversary_row(
                            anchor=anchor,
                            as_of=as_of,
                            due=due,
                            window_type="monthly_anniversary",
                            multiple=multiple,
                            harmonic=_gann_harmonic_label(months=total_months),
                            label=f"每 {monthly_step} 個月週年窗",
                            months=total_months,
                            base_days=total_months * (_TRADING_MONTH_DAYS if use_trading_days else 30),
                            use_trading_days=use_trading_days,
                        )
                    )

        if include_day_windows:
            for base_days in day_windows:
                max_multiple = max(1, int(math.ceil((lookback_years + lookahead_years + 2) * 365.2425 / base_days)))
                for multiple in range(1, max_multiple + 1):
                    total_days = base_days * multiple
                    due = _add_business_days(anchor, total_days) if use_trading_days else anchor + timedelta(days=total_days)
                    if due > window_end:
                        break
                    if due < window_start:
                        continue
                    rows.append(
                        _build_anniversary_row(
                            anchor=anchor,
                            as_of=as_of,
                            due=due,
                            window_type="gann_day_window",
                            multiple=multiple,
                            harmonic=_gann_harmonic_label(days=base_days),
                            label=f"{base_days} 天 Gann 時間窗",
                            base_days=base_days,
                            use_trading_days=use_trading_days,
                        )
                    )

    rows.sort(
        key=lambda r: (
            abs(r["distance_days"]),
            r["due_date"],
            r["anchor_date"],
            r["type"],
            r["base_days"] or 0,
        )
    )
    return rows


def find_nearest_square_of_nine_levels(
    current_price: float,
    reference_price: float,
    *,
    max_ring: int = 3,
    angle_step: int = 45,
    angle_system: str = "all",
) -> dict:
    """找出最接近當前價格的 Square of 9 支撐/壓力位。"""
    if current_price <= 0:
        raise ValueError("current_price must be positive")
    levels = compute_square_of_nine_levels(
        reference_price=reference_price,
        current_price=current_price,
        max_ring=max_ring,
        angle_step=angle_step,
        include_descending=True,
        angle_system=angle_system,
        include_metadata=True,
    )
    if not levels:
        raise ValueError("no Square of 9 levels available")

    support = max((row for row in levels if row["target_price"] <= current_price), key=lambda row: row["target_price"], default=None)
    resistance = min(
        (row for row in levels if row["target_price"] >= current_price),
        key=lambda row: row["target_price"],
        default=None,
    )
    if support is None and resistance is None:
        raise ValueError("no support or resistance levels found near current_price")

    def _distance(row: dict | None) -> float:
        if row is None:
            return float("inf")
        return abs(row["target_price"] - current_price)

    nearest_candidates = [row for row in (support, resistance) if row is not None]
    nearest = min(nearest_candidates, key=_distance)
    return {
        "current_price": round(current_price, 4),
        "reference_price": round(reference_price, 4),
        "nearest_level": nearest,
        "support_level": support,
        "resistance_level": resistance,
        "distance_to_nearest": round(abs(nearest["target_price"] - current_price), 4),
        "distance_percent": round(abs(nearest["target_price"] - current_price) / current_price * 100.0, 4),
    }


def _classify_resonance(score: int) -> str:
    if score >= _HIGH_RESONANCE_THRESHOLD:
        return "高共振（時間窗 + 星曜守照齊備）"
    if score >= _MEDIUM_RESONANCE_THRESHOLD:
        return "中度共振（可觀察，等待確認）"
    if score >= _WEAK_RESONANCE_THRESHOLD:
        return "弱共振（僅作輔助）"
    return "低共振（不建議單獨採信）"


def _coerce_score_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def build_gann_macro_timing(
    *,
    market_natal_date: date | datetime,
    as_of_datetime: datetime,
    timezone: float = 8.0,
    cycle_scale: float = 0.1,
    use_trading_days: bool = False,
    cycle_orb_days: int = 12,
    year_basis_days: float = 365.2425,
    natal_longitudes: Optional[dict[str, float]] = None,
    transit_longitudes: Optional[dict[str, float]] = None,
) -> dict:
    """
    江恩宏觀 timing：
    - 聖經周期到期點
    - 七政四餘流時守照
    - 多重共振分數與進出場條件
    """
    cycle_hits = compute_biblical_cycle_dates(
        market_natal_date,
        as_of_date=as_of_datetime,
        scale=cycle_scale,
        year_basis_days=year_basis_days,
        use_trading_days=use_trading_days,
        lookback_years=2.0,
        lookahead_years=2.0,
    )
    anniversary_hits = compute_anniversary_dates(
        market_natal_date,
        as_of_date=as_of_datetime,
        use_trading_days=use_trading_days,
        lookback_years=2.0,
        lookahead_years=2.0,
    )
    near_hits = [x for x in cycle_hits if abs(x["distance_days"]) <= cycle_orb_days]
    near_anniversaries = [x for x in anniversary_hits if abs(x["distance_days"]) <= cycle_orb_days]

    natal_map = natal_longitudes or build_market_natal_longitudes(market_natal_date, timezone=timezone)
    transit_map = transit_longitudes or get_transit_longitudes(as_of_datetime, timezone=timezone)
    qizheng_hits = evaluate_qizheng_resonance(natal_map, transit_map, orb=3.0)

    cycle_score = _CYCLE_SCORE_WEIGHT * len(near_hits)
    anniversary_score = len(near_anniversaries)
    astro_score = sum(_coerce_score_int(x.get("score", 0)) for x in qizheng_hits)
    total_score = cycle_score + anniversary_score + astro_score

    positive_aspects = [x for x in qizheng_hits if _coerce_score_int(x.get("score", 0)) > 0]
    negative_aspects = [x for x in qizheng_hits if _coerce_score_int(x.get("score", 0)) < 0]
    entry_conditions = [
        "至少 1 個聖經周期在容差窗內",
        "七政四餘關鍵星曜（木星/土星/羅睺/計都/月孛/紫氣）出現至少 1 個正向守照",
        "總共振分數達中度（>=4）",
    ]
    exit_conditions = [
        "關鍵周期窗結束且未出現延伸共振",
        "負向守照（刑/沖）數量高於正向守照",
        "總共振分數降至 <=0",
    ]

    return {
        "market_natal_date": _to_date(market_natal_date).isoformat(),
        "as_of": as_of_datetime.isoformat(),
        "cycle_scale": cycle_scale,
        "use_trading_days": use_trading_days,
        "cycle_orb_days": cycle_orb_days,
        "cycle_hits": cycle_hits,
        "near_cycle_hits": near_hits,
        "anniversary_hits": anniversary_hits,
        "near_anniversaries": near_anniversaries,
        "qizheng_resonance_hits": qizheng_hits,
        "scores": {
            "cycle_score": cycle_score,
            "anniversary_score": anniversary_score,
            "astro_score": astro_score,
            "total_score": total_score,
            "classification": _classify_resonance(total_score),
            "positive_aspect_count": len(positive_aspects),
            "negative_aspect_count": len(negative_aspects),
        },
        "entry_conditions": entry_conditions,
        "exit_conditions": exit_conditions,
        "notes": [
            "Gann 原則：時間先於價格，必須等待多重共振。",
            "市場實務建議：先以宏觀指數做時窗，再下鑽板塊與風險控制。",
        ],
    }


def build_gann_macro_with_dasha_context(
    *,
    market_natal_date: date | datetime,
    as_of_datetime: datetime,
    timezone: float = 8.0,
    cycle_scale: float = 0.1,
    use_trading_days: bool = False,
    dasha_context: Optional[dict] = None,
) -> dict:
    """
    與 qizheng_dasha 整合的示例封裝。

    dasha_context 需包含：
    - birth_year, ming_gong_branch, gender, houses
    """
    payload = build_gann_macro_timing(
        market_natal_date=market_natal_date,
        as_of_datetime=as_of_datetime,
        timezone=timezone,
        cycle_scale=cycle_scale,
        use_trading_days=use_trading_days,
    )
    if not dasha_context:
        payload["dasha"] = None
        return payload

    from ..qizheng_dasha import compute_dasha

    d = compute_dasha(
        birth_year=dasha_context["birth_year"],
        ming_gong_branch=dasha_context["ming_gong_branch"],
        gender=dasha_context["gender"],
        houses=dasha_context["houses"],
        current_year=as_of_datetime.year,
    )
    payload["dasha"] = {
        "current_period_idx": d.current_period_idx,
        "current_age": d.current_age,
        "flow_year_branch": d.flow_year_branch,
        "flow_year_palace": d.flow_year_palace,
    }
    return payload


# ============================================================
# 時間＝價格共振（Time-Price Squaring）
# ============================================================

# Gann 角度比率：(名稱, 時間單位, 價格單位)
_GANN_ANGLE_RATIOS: tuple[tuple[str, int, int], ...] = (
    ("8×1", 1, 8),
    ("4×1", 1, 4),
    ("3×1", 1, 3),
    ("2×1", 1, 2),
    ("1×1", 1, 1),
    ("1×2", 2, 1),
    ("1×3", 3, 1),
    ("1×4", 4, 1),
    ("1×8", 8, 1),
)

_SOLAR_INGRESS_LONGITUDES: tuple[tuple[str, float], ...] = (
    ("春分 Vernal Equinox", 0.0),
    ("夏至 Summer Solstice", 90.0),
    ("秋分 Autumnal Equinox", 180.0),
    ("冬至 Winter Solstice", 270.0),
)


def compute_time_price_squaring(
    anchor_price: float,
    anchor_date: date | datetime,
    *,
    as_of_date: date | datetime,
    price_unit: float = 1.0,
    time_unit_days: int = 1,
    lookahead_days: int = 365,
    orb_days: int = 5,
    orb_price_pct: float = 0.02,
) -> list[dict]:
    """
    計算時間＝價格共振點（Time-Price Squaring）。

    江恩理論核心：當「時間（天數）」在平方根螺旋上與「價格」
    落在相同角度時，市場出現共振轉折。

    計算方式：
    - 以 anchor_price 的平方根 root0 為基礎
    - 每完整旋轉 360° = 2 個平方根單位
    - 當天數（按 time_unit_days 縮放）的平方根 ≈ 價格的平方根時
      → 「時間 = 價格」共振窗口

    回傳：各共振節點列表（日期、對應價格、共振強度）。
    """
    if anchor_price <= 0:
        raise ValueError("anchor_price must be positive")
    if price_unit <= 0:
        raise ValueError("price_unit must be positive")
    if time_unit_days <= 0:
        raise ValueError("time_unit_days must be positive")

    anchor = _to_date(anchor_date)
    as_of = _to_date(as_of_date)
    root0 = math.sqrt(anchor_price / price_unit)

    results: list[dict] = []
    # 掃描各平方根整數 / 半整數節點
    # 每一「旋轉圈數」n 對應價格 = (root0 + n)² × price_unit
    max_n = int(root0) + int(math.ceil(math.sqrt(anchor_price + 50 * price_unit) - root0)) + 10
    for n in range(-4, max_n + 1):
        # 對應價格共振節點
        resonant_root = root0 + n
        if resonant_root <= 0:
            continue
        resonant_price = round((resonant_root ** 2) * price_unit, 4)

        # 對應天數：天數縮放後的平方根 = resonant_root
        # → days / time_unit_days = resonant_root² → days = resonant_root² × time_unit_days
        resonant_days = int(round((resonant_root ** 2) * time_unit_days))
        if resonant_days < 0:
            continue
        resonant_date = anchor + timedelta(days=resonant_days)

        # 只保留 as_of 附近 ± orb_days 或未來 lookahead_days
        days_from_now = (resonant_date - as_of).days
        if days_from_now < -orb_days or days_from_now > lookahead_days:
            continue

        # 計算強度：半整數節點（n = k/2）為次要，整數節點為主要
        is_primary = isinstance(n, int)
        strength = "主要共振" if is_primary else "次要共振"
        orb_check = abs(days_from_now) <= orb_days

        results.append({
            "resonant_date": resonant_date.isoformat(),
            "distance_days": days_from_now,
            "resonant_price": resonant_price,
            "resonant_root": round(resonant_root, 4),
            "n_step": n,
            "strength": strength,
            "in_orb": orb_check,
            "note": f"時間={resonant_days}日，對應價格共振位 {resonant_price}（root={resonant_root:.4f}）",
        })

    # 也加入半步節點（0.5 旋轉）
    for n_half in range(-8, (max_n + 1) * 2):
        resonant_root = root0 + n_half * 0.5
        if resonant_root <= 0 or n_half % 2 == 0:  # 整數已加，跳過
            continue
        resonant_price = round((resonant_root ** 2) * price_unit, 4)
        resonant_days = int(round((resonant_root ** 2) * time_unit_days))
        if resonant_days < 0:
            continue
        resonant_date = anchor + timedelta(days=resonant_days)
        days_from_now = (resonant_date - as_of).days
        if days_from_now < -orb_days or days_from_now > lookahead_days:
            continue

        results.append({
            "resonant_date": resonant_date.isoformat(),
            "distance_days": days_from_now,
            "resonant_price": resonant_price,
            "resonant_root": round(resonant_root, 4),
            "n_step": n_half * 0.5,
            "strength": "次要共振（180°）",
            "in_orb": abs(days_from_now) <= orb_days,
            "note": f"時間={resonant_days}日，對應半步共振位 {resonant_price}",
        })

    results.sort(key=lambda r: r["distance_days"])
    return results


# ============================================================
# 江恩角度 / 江恩扇形（Gann Angles / Gann Fan）
# ============================================================

def compute_gann_angles(
    pivot_price: float,
    pivot_date: date | datetime,
    *,
    as_of_date: date | datetime,
    price_unit: float = 1.0,
    time_unit_days: int = 1,
    lookahead_days: int = 365,
    trend: str = "up",
) -> list[dict]:
    """
    計算江恩扇形角度線（Gann Fan Angles）。

    以樞紐高低點為起點，計算各角度線在未來日期的價格目標。

    角度線：
    - 1×1（45°）：每 time_unit_days 移動 1×price_unit
    - 2×1、3×1、4×1、8×1（更陡峭）
    - 1×2、1×3、1×4、1×8（更平緩）

    Parameters:
        pivot_price: 樞紐價格（支撐高點或低點）
        pivot_date: 樞紐日期
        as_of_date: 計算基準日
        price_unit: 每格價格單位
        time_unit_days: 每格時間單位（天）
        lookahead_days: 向前看天數
        trend: "up"（從低點向上）或 "down"（從高點向下）

    回傳：各角度線在各時間點的價格目標。
    """
    if pivot_price <= 0:
        raise ValueError("pivot_price must be positive")
    if price_unit <= 0:
        raise ValueError("price_unit must be positive")
    if time_unit_days <= 0:
        raise ValueError("time_unit_days must be positive")
    if trend not in ("up", "down"):
        raise ValueError("trend must be 'up' or 'down'")

    pivot = _to_date(pivot_date)
    as_of = _to_date(as_of_date)
    direction = 1 if trend == "up" else -1

    # 從樞紐日到 as_of 的天數
    days_elapsed = (as_of - pivot).days

    results: list[dict] = []
    # 時間節點：當前 + 每 30 天一個節點到 lookahead
    time_nodes = sorted({0, 30, 60, 90, 120, 180, 270, 360} |
                         {d for d in range(0, lookahead_days + 1, 30)})

    for angle_name, t_units, p_units in _GANN_ANGLE_RATIOS:
        # 斜率：每 time_unit_days 天移動 (p_units/t_units) × price_unit
        slope = (p_units / t_units) * price_unit / time_unit_days  # price per day

        # as_of 當天的角度線價格
        current_angle_price = pivot_price + direction * slope * days_elapsed

        for days_ahead in time_nodes:
            target_days = days_elapsed + days_ahead
            angle_price = pivot_price + direction * slope * target_days
            if angle_price <= 0:
                continue
            target_date = pivot + timedelta(days=target_days)
            results.append({
                "angle": angle_name,
                "trend": trend,
                "date": target_date.isoformat(),
                "days_from_pivot": target_days,
                "days_from_now": days_ahead,
                "price_target": round(angle_price, 4),
                "current_angle_price": round(current_angle_price, 4),
                "slope_per_day": round(slope, 6),
                "note": f"{angle_name}角度線（{trend}）在 {target_date.isoformat()} 對應 {angle_price:.2f}",
            })

    results.sort(key=lambda r: (r["days_from_now"], r["angle"]))
    return results


def get_gann_angle_at_date(
    pivot_price: float,
    pivot_date: date | datetime,
    target_date: date | datetime,
    *,
    price_unit: float = 1.0,
    time_unit_days: int = 1,
    trend: str = "up",
) -> dict[str, float]:
    """
    取得指定日期各江恩角度線的價格。

    回傳 {angle_name: price} 字典，適合與實際收盤價對照。
    """
    pivot = _to_date(pivot_date)
    target = _to_date(target_date)
    days_elapsed = (target - pivot).days
    direction = 1 if trend == "up" else -1

    output: dict[str, float] = {}
    for angle_name, t_units, p_units in _GANN_ANGLE_RATIOS:
        slope = (p_units / t_units) * price_unit / time_unit_days
        price = pivot_price + direction * slope * days_elapsed
        if price > 0:
            output[angle_name] = round(price, 4)
    return output


# ============================================================
# 江恩自然方格 + 振動（Gann Natural Squares + Vibration）
# ============================================================

def compute_natural_squares_vibration(
    reference_price: float,
    *,
    num_squares: int = 20,
    include_octagon: bool = True,
    include_cross: bool = True,
    current_price: float | None = None,
    proximity_pct: float = 0.05,
) -> dict:
    """
    計算江恩自然方格（Gann Natural Squares）及振動層級。

    自然方格：n² 序列（1, 4, 9, 16, 25, ...）
    振動原理：任意價格都可在方格螺旋上找到「共振節點」，
    即最接近的自然方格或其十字/八卦延伸點。

    Parameters:
        reference_price: 基準價格（如當前價或歷史高低點）
        num_squares: 計算至第幾個自然方格
        include_octagon: 是否包含八卦延伸（每 45° 一個節點）
        include_cross: 是否包含十字延伸（每 90° 一個節點）
        current_price: 當前價格（用於計算接近度）
        proximity_pct: 接近度閾值（百分比）

    回傳：{squares, vibration_level, nearest_square, cross_levels, octagon_levels}
    """
    if reference_price <= 0:
        raise ValueError("reference_price must be positive")

    root_ref = math.sqrt(reference_price)

    # 自然方格序列
    squares = []
    for n in range(1, num_squares + 1):
        val = float(n * n)
        squares.append({
            "n": n,
            "square": val,
            "root": float(n),
            "distance_from_ref": round(abs(val - reference_price), 4),
            "pct_from_ref": round(abs(val - reference_price) / reference_price * 100.0, 4),
        })

    # 以 reference_price 計算振動層級
    # 振動層級 = floor(sqrt(reference_price))
    vibration_n = int(math.floor(root_ref))
    vibration_remainder = root_ref - vibration_n  # 0 ~ 1 之間的小數部分
    vibration_angle = round(vibration_remainder * 360.0, 2)  # 轉換為角度（0~360°）
    vibration_level = {
        "reference_price": round(reference_price, 4),
        "sqrt_ref": round(root_ref, 6),
        "vibration_n": vibration_n,
        "vibration_remainder": round(vibration_remainder, 6),
        "vibration_angle_deg": vibration_angle,
        "lower_square": vibration_n ** 2,
        "upper_square": (vibration_n + 1) ** 2,
        "position_in_cycle": f"{vibration_angle:.1f}° / 360°",
        "description": (
            f"價格 {reference_price} 位於第 {vibration_n} 圈"
            f"（{vibration_n}²={vibration_n**2} ～ {vibration_n+1}²={(vibration_n+1)**2}），"
            f"角度 {vibration_angle:.1f}°"
        ),
    }

    # 十字延伸（+0°, +90°, +180°, +270°）
    cross_levels: list[dict] = []
    if include_cross:
        for n in range(1, num_squares + 1):
            for angle_offset in (0, 90, 180, 270):
                frac = angle_offset / 360.0
                extended_root = n + frac
                val = round(extended_root ** 2, 4)
                cross_levels.append({
                    "base_n": n,
                    "angle_offset": angle_offset,
                    "extended_root": round(extended_root, 4),
                    "price": val,
                    "type": "cross",
                })

    # 八卦延伸（+0°, +45°, +90°, +135°, +180°, +225°, +270°, +315°）
    octagon_levels: list[dict] = []
    if include_octagon:
        for n in range(1, num_squares + 1):
            for angle_offset in (0, 45, 90, 135, 180, 225, 270, 315):
                frac = angle_offset / 360.0
                extended_root = n + frac
                val = round(extended_root ** 2, 4)
                octagon_levels.append({
                    "base_n": n,
                    "angle_offset": angle_offset,
                    "extended_root": round(extended_root, 4),
                    "price": val,
                    "type": "octagon",
                })

    # 尋找最接近當前價格的節點
    nearest_square: dict | None = None
    nearest_vibration: dict | None = None
    if current_price is not None and current_price > 0:
        all_levels = [{"price": sq["square"], "type": "natural_square", "n": sq["n"]} for sq in squares]
        all_levels += [{"price": lvl["price"], "type": lvl["type"], "n": lvl["base_n"]} for lvl in octagon_levels]

        near = [
            lvl for lvl in all_levels
            if abs(lvl["price"] - current_price) / current_price <= proximity_pct
        ]
        near.sort(key=lambda x: abs(x["price"] - current_price))
        nearest_vibration = near[:5] if near else None

        ns_candidates = [sq for sq in squares if abs(sq["square"] - current_price) / current_price <= proximity_pct * 2]
        ns_candidates.sort(key=lambda x: abs(x["square"] - current_price))
        nearest_square = ns_candidates[0] if ns_candidates else None

    return {
        "reference_price": round(reference_price, 4),
        "natural_squares": squares,
        "vibration_level": vibration_level,
        "cross_levels": cross_levels,
        "octagon_levels": octagon_levels,
        "nearest_natural_square": nearest_square,
        "nearest_vibration_nodes": nearest_vibration,
    }


# ============================================================
# 與 Solar Ingress（節氣入境）結合
# ============================================================

_YEAR_BASIS_DAYS: float = 365.2425


def _find_solar_ingress_jd(year: int, target_lon: float) -> float:
    """Calculate the Julian Day when the Sun enters the specified ecliptic longitude.

    Args:
        year: Year to calculate the ingress for.
        target_lon: Target ecliptic longitude in degrees (0=Aries, 90=Cancer, 180=Libra, 270=Capricorn).

    Returns:
        Julian Day number of the solar ingress.
    """
    # 估算初始時刻（以春分為基準）
    # 春分約在 3 月 20 日
    approx_day = {0.0: (3, 20), 90.0: (6, 21), 180.0: (9, 23), 270.0: (12, 21)}.get(
        target_lon, (3, 20)
    )
    jd_start = swe.julday(year, approx_day[0], approx_day[1], 0.0)

    def _sun_lon(jd: float) -> float:
        result, _ = swe.calc_ut(jd, swe.SUN)
        return _normalize_degree(result[0])

    # 二分法搜尋
    jd0 = jd_start - 20.0
    jd1 = jd_start + 20.0
    for _ in range(50):
        jd_mid = (jd0 + jd1) / 2.0
        lon = _sun_lon(jd_mid)
        diff = _normalize_degree(lon - target_lon)
        if diff > 180.0:
            diff -= 360.0
        if abs(diff) < 1e-6:
            break
        if diff < 0:
            jd0 = jd_mid
        else:
            jd1 = jd_mid
    return (jd0 + jd1) / 2.0


def _jd_to_date(jd: float) -> date:
    y, m, d, _ = swe.revjul(jd)
    return date(int(y), int(m), int(d))


def compute_solar_ingress_gann_confluence(
    market_natal_date: date | datetime,
    *,
    year: int,
    cycle_scale: float = 0.1,
    use_trading_days: bool = False,
    cycle_orb_days: int = 12,
    year_basis_days: float = _YEAR_BASIS_DAYS,
) -> list[dict]:
    """
    計算 Solar Ingress（節氣入境）與江恩周期/週年窗的合相（Confluence）。

    四個關鍵節氣入境日（春分、夏至、秋分、冬至）若落在江恩周期容差窗內，
    視為強力時間共振確認信號。

    Parameters:
        market_natal_date: 市場出生日期（指數/股票上市日）
        year: 計算年份
        cycle_scale: 聖經周期縮放倍率
        use_trading_days: 是否以交易日計算
        cycle_orb_days: 周期容差（天）
        year_basis_days: 年度天數基準

    回傳：各節氣入境日的江恩共振評分與詳情列表。
    """
    swe.set_ephe_path("")
    natal = _to_date(market_natal_date)

    results: list[dict] = []
    for ingress_name, target_lon in _SOLAR_INGRESS_LONGITUDES:
        try:
            jd = _find_solar_ingress_jd(year, target_lon)
        except Exception:
            continue
        ingress_date = _jd_to_date(jd)

        # 計算聖經周期共振
        cycle_hits = compute_biblical_cycle_dates(
            natal,
            as_of_date=ingress_date,
            scale=cycle_scale,
            year_basis_days=year_basis_days,
            use_trading_days=use_trading_days,
            lookback_years=0.1,
            lookahead_years=0.1,
            max_multiple=20,
        )
        near_cycles = [h for h in cycle_hits if abs(h["distance_days"]) <= cycle_orb_days]

        # 計算週年窗共振
        ann_hits = compute_anniversary_dates(
            natal,
            as_of_date=ingress_date,
            use_trading_days=use_trading_days,
            lookback_years=0.1,
            lookahead_years=0.1,
        )
        near_ann = [h for h in ann_hits if abs(h["distance_days"]) <= cycle_orb_days]

        cycle_score = _CYCLE_SCORE_WEIGHT * len(near_cycles)
        ann_score = len(near_ann)
        total_score = cycle_score + ann_score

        confluence_label = _classify_resonance(total_score)

        results.append({
            "ingress_name": ingress_name,
            "ingress_date": ingress_date.isoformat(),
            "solar_longitude": target_lon,
            "year": year,
            "near_cycle_hits": len(near_cycles),
            "near_anniversary_hits": len(near_ann),
            "cycle_score": cycle_score,
            "anniversary_score": ann_score,
            "total_score": total_score,
            "confluence": confluence_label,
            "cycle_details": near_cycles[:3],
            "anniversary_details": near_ann[:3],
            "note": (
                f"{ingress_name}（{ingress_date.isoformat()}）"
                f"周期命中 {len(near_cycles)} 個，週年命中 {len(near_ann)} 個，"
                f"總共振分 {total_score}→{confluence_label}"
            ),
        })

    results.sort(key=lambda r: -r["total_score"])
    return results


# ============================================================
# 多重共振 Confluence 評分系統（整合版）
# ============================================================

_CONFLUENCE_TIME_PRICE_WEIGHT: int = 3
_CONFLUENCE_SOLAR_INGRESS_WEIGHT: int = 2
_CONFLUENCE_NATURAL_SQUARE_WEIGHT: int = 2
_CONFLUENCE_GANN_ANGLE_WEIGHT: int = 1


def build_gann_full_confluence(
    *,
    market_natal_date: date | datetime,
    as_of_datetime: datetime,
    current_price: float,
    reference_price: float | None = None,
    pivot_price: float | None = None,
    pivot_date: date | datetime | None = None,
    timezone: float = 8.0,
    cycle_scale: float = 0.1,
    use_trading_days: bool = False,
    cycle_orb_days: int = 12,
    year_basis_days: float = _YEAR_BASIS_DAYS,
    natal_longitudes: dict[str, float] | None = None,
    transit_longitudes: dict[str, float] | None = None,
    time_price_orb_days: int = 7,
    price_proximity_pct: float = 0.03,
    trend: str = "up",
) -> dict:
    """
    江恩全維度多重共振 Confluence 評分系統。

    整合層次：
    1. 聖經周期 + 週年窗（時間層）
    2. 七政四餘守照共振（星象層）
    3. 時間＝價格共振（T=P 層）
    4. Solar Ingress 節氣入境（節氣層）
    5. 江恩自然方格振動（價格振動層）
    6. 江恩角度線支撐壓力（角度層）

    Parameters:
        market_natal_date: 市場出生日期
        as_of_datetime: 評估時刻
        current_price: 當前價格
        reference_price: Square of 9 基準價格（預設同 current_price）
        pivot_price: 江恩扇形基準高低點價格（可選）
        pivot_date: 江恩扇形基準高低點日期（可選）
        trend: 當前趨勢方向（"up" 或 "down"）

    回傳：含各層共振分數與彙總的完整評估結果。
    """
    ref_price = reference_price if reference_price and reference_price > 0 else current_price

    # ── 層次 1：基礎 Gann 宏觀 timing ────────────────────────
    base = build_gann_macro_timing(
        market_natal_date=market_natal_date,
        as_of_datetime=as_of_datetime,
        timezone=timezone,
        cycle_scale=cycle_scale,
        use_trading_days=use_trading_days,
        cycle_orb_days=cycle_orb_days,
        year_basis_days=year_basis_days,
        natal_longitudes=natal_longitudes,
        transit_longitudes=transit_longitudes,
    )
    base_scores = base.get("scores", {})

    # ── 層次 2：時間＝價格共振 ──────────────────────────────
    tp_squaring = compute_time_price_squaring(
        anchor_price=ref_price,
        anchor_date=market_natal_date,
        as_of_date=as_of_datetime,
        lookahead_days=90,
        orb_days=time_price_orb_days,
    )
    tp_hits_in_orb = [r for r in tp_squaring if r["in_orb"]]
    tp_primary_hits = [r for r in tp_hits_in_orb if r["strength"] == "主要共振"]
    tp_score = _CONFLUENCE_TIME_PRICE_WEIGHT * len(tp_primary_hits) + len(tp_hits_in_orb) - len(tp_primary_hits)

    # ── 層次 3：Solar Ingress 節氣共振 ──────────────────────
    ingress_data = compute_solar_ingress_gann_confluence(
        market_natal_date,
        year=as_of_datetime.year,
        cycle_scale=cycle_scale,
        use_trading_days=use_trading_days,
        cycle_orb_days=cycle_orb_days,
        year_basis_days=year_basis_days,
    )
    high_ingress = [r for r in ingress_data if r["total_score"] >= _MEDIUM_RESONANCE_THRESHOLD]
    ingress_score = _CONFLUENCE_SOLAR_INGRESS_WEIGHT * len(high_ingress)

    # ── 層次 4：自然方格振動 ────────────────────────────────
    nat_sq = compute_natural_squares_vibration(
        ref_price,
        num_squares=30,
        current_price=current_price,
        proximity_pct=price_proximity_pct,
    )
    nat_sq_hits = nat_sq.get("nearest_vibration_nodes") or []
    nat_sq_score = _CONFLUENCE_NATURAL_SQUARE_WEIGHT * min(len(nat_sq_hits), 3)

    # ── 層次 5：江恩角度線 ───────────────────────────────────
    angle_hits: list[dict] = []
    if pivot_price and pivot_price > 0 and pivot_date:
        angles_data = compute_gann_angles(
            pivot_price=pivot_price,
            pivot_date=pivot_date,
            as_of_date=as_of_datetime,
            trend=trend,
            lookahead_days=0,
        )
        # 僅取 days_from_now == 0 的當前值
        current_angles = [a for a in angles_data if a["days_from_now"] == 0]
        for ang in current_angles:
            if abs(ang["current_angle_price"] - current_price) / current_price <= price_proximity_pct:
                angle_hits.append(ang)
    angle_score = _CONFLUENCE_GANN_ANGLE_WEIGHT * len(angle_hits)

    # ── 彙總分數 ─────────────────────────────────────────────
    base_total_score = _coerce_score_int(base_scores.get("total_score", 0))
    total_confluence = (
        base_total_score
        + tp_score
        + ingress_score
        + nat_sq_score
        + angle_score
    )

    confluence_layers = {
        "biblical_cycle_score": _coerce_score_int(base_scores.get("cycle_score", 0)),
        "anniversary_score": _coerce_score_int(base_scores.get("anniversary_score", 0)),
        "qizheng_astro_score": _coerce_score_int(base_scores.get("astro_score", 0)),
        "time_price_squaring_score": tp_score,
        "solar_ingress_score": ingress_score,
        "natural_square_score": nat_sq_score,
        "gann_angle_score": angle_score,
        "total_confluence_score": total_confluence,
        "classification": _classify_resonance(total_confluence),
    }

    return {
        "market_natal_date": _to_date(market_natal_date).isoformat(),
        "as_of": as_of_datetime.isoformat(),
        "current_price": current_price,
        "reference_price": ref_price,
        "trend": trend,
        # 各層原始資料
        "base_timing": base,
        "time_price_squaring": tp_squaring,
        "tp_hits_in_orb": tp_hits_in_orb,
        "solar_ingress_confluence": ingress_data,
        "natural_squares_vibration": nat_sq,
        "gann_angle_hits": angle_hits,
        # 彙總
        "confluence_scores": confluence_layers,
        "entry_conditions": base.get("entry_conditions", []) + [
            "T=P共振窗口：時間=價格共振在 ±7 日內出現",
            "節氣入境日與江恩周期重疊（春分/夏至/秋分/冬至）",
            "當前價格接近自然方格振動節點（±3%）",
        ],
        "exit_conditions": base.get("exit_conditions", []) + [
            "T=P共振窗口結束且無新信號",
            "角度線由支撐轉壓力（跌破 1×1 線）",
        ],
        "notes": [
            "Gann 全維度 Confluence：六層共振同時出現時，信號最強。",
            "時間=價格共振為最高優先級信號（T=P Squaring）。",
            "節氣入境日歷史上常為市場轉折窗。",
        ],
    }
