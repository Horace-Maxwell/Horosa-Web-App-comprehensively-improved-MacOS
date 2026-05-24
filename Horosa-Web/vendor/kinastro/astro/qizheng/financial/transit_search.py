"""精確 transit 事件搜尋工具。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


JDFunc = Callable[[float], float]


@dataclass(frozen=True)
class SearchResult:
    """單次事件搜尋結果。"""

    jd: float
    value: float
    converged: bool
    iterations: int
    method: str


def normalize_degree(value: float) -> float:
    """將角度標準化至 [0, 360)。"""
    return value % 360.0


def signed_angle_to_target(value: float, target: float) -> float:
    """回傳 value 對 target 的有號角差（[-180, 180)）。"""
    return ((normalize_degree(value - target) + 180.0) % 360.0) - 180.0


def angle_diff(a: float, b: float) -> float:
    """最小夾角。"""
    diff = abs(normalize_degree(a - b))
    return 360.0 - diff if diff > 180.0 else diff


def _coarse_grid(start_jd: float, end_jd: float, step: float) -> list[float]:
    values: list[float] = []
    x = float(start_jd)
    while x <= end_jd:
        values.append(x)
        x += step
    if not values or values[-1] < end_jd:
        values.append(float(end_jd))
    return values


def bisection_root(
    func: JDFunc,
    left: float,
    right: float,
    *,
    tol: float = 1e-6,
    max_iter: int = 80,
) -> SearchResult:
    """對符號相異區間做二分搜尋。"""
    fl = func(left)
    fr = func(right)
    if fl == 0.0:
        return SearchResult(left, 0.0, True, 0, "bisection")
    if fr == 0.0:
        return SearchResult(right, 0.0, True, 0, "bisection")
    if fl * fr > 0:
        candidate = left if abs(fl) <= abs(fr) else right
        return SearchResult(candidate, func(candidate), False, 0, "bisection-no-bracket")

    a, b = left, right
    fa, fb = fl, fr
    for i in range(1, max_iter + 1):
        mid = 0.5 * (a + b)
        fm = func(mid)
        if abs(fm) <= tol or abs(b - a) <= tol:
            return SearchResult(mid, fm, True, i, "bisection")
        if fa * fm <= 0:
            b, fb = mid, fm
        else:
            a, fa = mid, fm
    mid = 0.5 * (a + b)
    fm = func(mid)
    return SearchResult(mid, fm, False, max_iter, "bisection")


def refine_minimum(
    func: JDFunc,
    left: float,
    right: float,
    *,
    tol: float = 1e-5,
    max_iter: int = 80,
) -> SearchResult:
    """以三分法最小化 |func|。"""
    a, b = left, right
    iterations = 0
    for iterations in range(1, max_iter + 1):
        if abs(b - a) <= tol:
            break
        m1 = a + (b - a) / 3.0
        m2 = b - (b - a) / 3.0
        f1 = abs(func(m1))
        f2 = abs(func(m2))
        if f1 <= f2:
            b = m2
        else:
            a = m1
    x = 0.5 * (a + b)
    fx = func(x)
    return SearchResult(x, fx, abs(b - a) <= tol, iterations, "ternary-min")


def find_closest_event(
    func: JDFunc,
    *,
    start_jd: float,
    end_jd: float,
    coarse_step: float,
    tolerance: float = 1e-4,
) -> SearchResult:
    """在區間內搜尋最接近 target 的時刻。"""
    grid = _coarse_grid(start_jd, end_jd, coarse_step)
    best_jd = grid[0]
    best_abs = abs(func(best_jd))
    values: list[tuple[float, float]] = []

    for jd in grid:
        v = func(jd)
        values.append((jd, v))
        av = abs(v)
        if av < best_abs:
            best_abs = av
            best_jd = jd

    # 優先用符號變化做 root finding。
    candidates: list[SearchResult] = []
    for i in range(len(values) - 1):
        j0, v0 = values[i]
        j1, v1 = values[i + 1]
        if v0 == 0.0:
            candidates.append(SearchResult(j0, 0.0, True, 0, "grid-zero"))
            continue
        if v0 * v1 <= 0:
            candidates.append(bisection_root(func, j0, j1, tol=tolerance))

    if candidates:
        return min(candidates, key=lambda r: abs(r.value))

    left = max(start_jd, best_jd - coarse_step)
    right = min(end_jd, best_jd + coarse_step)
    return refine_minimum(func, left, right, tol=tolerance)


def find_all_aspect_hits(
    angle_func: JDFunc,
    *,
    target_angle: float,
    start_jd: float,
    end_jd: float,
    orb: float,
    coarse_step: float = 1.0,
    precision: float = 1e-4,
    merge_gap_days: float = 0.5,
) -> list[SearchResult]:
    """在時間窗中找出所有相位命中時刻。"""

    def event_func(jd: float) -> float:
        return signed_angle_to_target(angle_func(jd), target_angle)

    grid = _coarse_grid(start_jd, end_jd, coarse_step)
    values = [(jd, event_func(jd)) for jd in grid]

    candidates: list[SearchResult] = []
    for i in range(len(values) - 1):
        j0, v0 = values[i]
        j1, v1 = values[i + 1]

        within_orb = abs(v0) <= orb or abs(v1) <= orb
        sign_change = v0 * v1 <= 0
        if not (within_orb or sign_change):
            continue

        left = j0
        right = j1
        if sign_change:
            r = bisection_root(event_func, left, right, tol=precision)
        else:
            r = refine_minimum(event_func, left, right, tol=precision)
        if abs(r.value) <= orb:
            candidates.append(r)

    if not candidates:
        return []

    candidates.sort(key=lambda x: x.jd)
    # 儒略日差值單位即「日」，因此 merge_gap_days 直接使用 JD 差值比較。
    merged: list[SearchResult] = [candidates[0]]
    for item in candidates[1:]:
        prev = merged[-1]
        if abs(item.jd - prev.jd) <= merge_gap_days:
            if abs(item.value) < abs(prev.value):
                merged[-1] = item
        else:
            merged.append(item)
    return merged
