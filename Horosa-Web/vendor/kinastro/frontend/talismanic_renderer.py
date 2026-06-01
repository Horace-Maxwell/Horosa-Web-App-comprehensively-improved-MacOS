"""
frontend/talismanic_renderer.py — Picatrix 占星魔法護符 SVG 渲染器 + Streamlit UI

提供：
  1. ``generate_talisman_svg``    — 生成高品質古抄本風格護符 SVG
  2. ``render_talisman_wizard``   — 互動式 Talisman 製作嚮導（Streamlit）
  3. ``render_electional_calc``   — 即時電擇計算器（Streamlit）
  4. ``render_talisman_database`` — 完整護符資料庫瀏覽（Streamlit）

美學風格：
  - 古羊皮紙黃褐 + 深紅墨 + 金箔 + 黑墨（Picatrix 手抄本風格）
  - 行星符號、魔法方陣（Kamea）、幾何圖案
  - 中世紀魔法書沉浸感
"""

from __future__ import annotations

import base64
import math
from datetime import datetime, timezone
from typing import Optional

# ── Streamlit: import lazily so SVG-only functions work without st ────────────
try:
    import streamlit as st
    _ST_AVAILABLE = True
except ImportError:
    st = None  # type: ignore[assignment]
    _ST_AVAILABLE = False

# ── 有條件引入計算模組 ────────────────────────────────────────
try:
    from astro.talismanic_magic import (
        evaluate_electional_moment,
        find_talisman_windows,
        recommend_talisman,
        get_moon_condition,
        get_planet_position,
        PLANET_CN, PLANET_GLYPHS, ZODIAC_SIGNS_CN,
        ElectionalScore, MoonCondition, ElectionalWindow,
        _jd_from_dt, _compute_all_planets,
    )
    _CALC_AVAILABLE = True
except ImportError:
    _CALC_AVAILABLE = False

try:
    from interpretations.talismanic import (
        PLANETARY_TALISMANS,
        DECAN_TALISMANS,
        PLANETARY_TALISMAN_BY_PLANET,
        ALL_PURPOSES,
        PURPOSE_LABELS_CN,
        get_planetary_talisman,
        get_decan_by_number,
        PlanetaryTalisman,
        DecanTalisman,
    )
    _DATA_AVAILABLE = True
except ImportError:
    _DATA_AVAILABLE = False

try:
    from astro.i18n import auto_cn, get_ui_lang
except ImportError:
    def auto_cn(t: str) -> str:  # type: ignore[misc]
        return t
    def get_ui_lang() -> str:  # type: ignore[misc]
        return "zh"


# ============================================================
# 顏色常量（羊皮紙魔法書主題）
# ============================================================

_C_PARCHMENT    = "#F5E6C8"   # 羊皮紙底色
_C_PARCHMENT_DK = "#E8D5A0"   # 深羊皮紙
_C_INK          = "#1A0A00"   # 古墨黑
_C_RED_INK      = "#8B1A1A"   # 深紅墨
_C_GOLD         = "#C9A227"   # 金箔
_C_GOLD_BRIGHT  = "#F5D060"   # 亮金
_C_SILVER       = "#C0C0C0"   # 銀
_C_DEEP_BG      = "#1a1228"   # 深色頁面背景
_C_CARD         = "#231a36"   # 卡片背景
_C_BORDER       = "#C9A227"   # 金邊框
_C_TEXT         = "#E8D5A3"   # 暖奶油文字
_C_SUBTLE       = "#9a7c3e"   # 次要文字
_C_HEADER       = "#F5D060"   # 標題文字
_C_GOOD         = "#5ba553"   # 吉利綠
_C_WARN         = "#c0392b"   # 警告紅
_C_NEUTRAL      = "#7b6fa0"   # 中性紫灰

# 行星顏色
_PLANET_COLORS: dict[str, str] = {
    "Sun":     "#FFD700",
    "Moon":    "#C0D8F0",
    "Mercury": "#9370DB",
    "Venus":   "#32CD32",
    "Mars":    "#DC143C",
    "Jupiter": "#4169E1",
    "Saturn":  "#696969",
}

# 行星符文圖案（SVG 內使用）
_PLANET_SIGILS: dict[str, str] = {
    "Sun":     "☉",
    "Moon":    "☽",
    "Mercury": "☿",
    "Venus":   "♀",
    "Mars":    "♂",
    "Jupiter": "♃",
    "Saturn":  "♄",
}

# 行星 Kamea 尺寸（N×N 幻方）
_PLANET_KAMEA: dict[str, int] = {
    "Saturn":  3,
    "Jupiter": 4,
    "Mars":    5,
    "Sun":     6,
    "Venus":   7,
    "Mercury": 8,
    "Moon":    9,
}

# 分數顏色
_GRADE_COLORS: dict[str, str] = {
    "Excellent": "#FFD700",
    "Good":      "#5ba553",
    "Acceptable":"#F5A623",
    "Poor":      "#c0392b",
    "Forbidden": "#8B0000",
}


# ============================================================
# SVG 護符生成器
# ============================================================

def _generate_kamea_svg_grid(planet: str, size: int = 180, x0: float = 0, y0: float = 0) -> str:
    """
    生成行星魔法方陣（Kamea）的 SVG 格線與數字。

    Parameters
    ----------
    planet : str
        行星名稱
    size : int
        SVG 方陣總尺寸（px）
    x0, y0 : float
        方陣左上角座標

    Returns
    -------
    str
        SVG 片段
    """
    n = _PLANET_KAMEA.get(planet, 3)
    cell = size / n
    color = _PLANET_COLORS.get(planet, _C_GOLD)
    lines = []

    # 格線
    for i in range(n + 1):
        x = x0 + i * cell
        y = y0 + i * cell
        lines.append(
            f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x0+size:.1f}" y2="{y:.1f}" '
            f'stroke="{color}" stroke-width="0.8" opacity="0.6"/>'
        )
        lines.append(
            f'<line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y0+size:.1f}" '
            f'stroke="{color}" stroke-width="0.8" opacity="0.6"/>'
        )

    # 生成 Lo Shu / 行星幻方數字（使用傳統 siamese 法近似）
    def siamese_square(n: int) -> list[list[int]]:
        sq = [[0] * n for _ in range(n)]
        r, c = 0, n // 2
        for num in range(1, n * n + 1):
            sq[r][c] = num
            nr, nc = (r - 1) % n, (c + 1) % n
            if sq[nr][nc] != 0:
                nr = (r + 1) % n
                nc = c
            r, c = nr, nc
        return sq

    if n % 2 == 1:  # 奇數階使用 siamese 法
        sq = siamese_square(n)
    else:
        # 偶數階（4×4, 6×6, 8×8）使用簡化數列
        sq = [[0] * n for _ in range(n)]
        vals = list(range(1, n * n + 1))
        idx = 0
        for i in range(n):
            for j in range(n):
                sq[i][j] = vals[idx]
                idx += 1

    for i in range(n):
        for j in range(n):
            cx = x0 + (j + 0.5) * cell
            cy = y0 + (i + 0.5) * cell
            lines.append(
                f'<text x="{cx:.1f}" y="{cy + 3:.1f}" '
                f'text-anchor="middle" font-size="{max(6, int(cell * 0.35))}" '
                f'fill="{color}" opacity="0.7" font-family="serif">{sq[i][j]}</text>'
            )

    return "\n".join(lines)


def _draw_pentagon(cx: float, cy: float, r: float, color: str) -> str:
    """繪製五角形（金星護符幾何圖案）。"""
    points = []
    for i in range(5):
        angle = math.pi * (2 * i / 5 - 0.5)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append(f"{x:.1f},{y:.1f}")
    pts = " ".join(points)
    return (
        f'<polygon points="{pts}" fill="none" stroke="{color}" '
        f'stroke-width="1.2" opacity="0.7"/>'
    )


def _draw_hexagram(cx: float, cy: float, r: float, color: str) -> str:
    """繪製六芒星（太陽/木星護符）。"""
    lines = []
    # 上三角形
    pts1 = []
    for i in range(3):
        angle = math.pi * (2 * i / 3 - 0.5)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        pts1.append(f"{x:.1f},{y:.1f}")
    # 下三角形
    pts2 = []
    for i in range(3):
        angle = math.pi * (2 * i / 3 + 0.5)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        pts2.append(f"{x:.1f},{y:.1f}")
    lines.append(f'<polygon points="{" ".join(pts1)}" fill="none" stroke="{color}" stroke-width="1.2" opacity="0.7"/>')
    lines.append(f'<polygon points="{" ".join(pts2)}" fill="none" stroke="{color}" stroke-width="1.2" opacity="0.7"/>')
    return "\n".join(lines)


def _draw_octagram(cx: float, cy: float, r: float, color: str) -> str:
    """繪製八芒星（水星護符）。"""
    points = []
    for i in range(8):
        angle = math.pi * i / 4
        ir = r * 0.5 if i % 2 == 1 else r
        x = cx + ir * math.cos(angle)
        y = cy + ir * math.sin(angle)
        points.append(f"{x:.1f},{y:.1f}")
    pts = " ".join(points)
    return (
        f'<polygon points="{pts}" fill="none" stroke="{color}" '
        f'stroke-width="1.2" opacity="0.7"/>'
    )


def _decorative_border_svg(width: float, height: float, color: str) -> str:
    """生成古典裝飾邊框 SVG。"""
    margin = 15
    corner = 25
    x1, y1 = margin, margin
    x2, y2 = width - margin, height - margin
    w = x2 - x1
    h = y2 - y1

    lines = []
    # 外框
    lines.append(
        f'<rect x="{x1}" y="{y1}" width="{w}" height="{h}" '
        f'fill="none" stroke="{color}" stroke-width="2.5" rx="4"/>'
    )
    # 內框（略小）
    lines.append(
        f'<rect x="{x1+6}" y="{y1+6}" width="{w-12}" height="{h-12}" '
        f'fill="none" stroke="{color}" stroke-width="0.8" opacity="0.5" rx="2"/>'
    )
    # 四角裝飾
    for cx, cy in [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]:
        lines.append(
            f'<circle cx="{cx}" cy="{cy}" r="5" '
            f'fill="{color}" opacity="0.8"/>'
        )
        lines.append(
            f'<circle cx="{cx}" cy="{cy}" r="8" '
            f'fill="none" stroke="{color}" stroke-width="1" opacity="0.5"/>'
        )

    # 頂部中央花飾
    mx = width / 2
    for ox in [-30, 0, 30]:
        lines.append(
            f'<circle cx="{mx + ox}" cy="{y1}" r="3" '
            f'fill="{color}" opacity="0.7"/>'
        )
    lines.append(
        f'<line x1="{mx-45}" y1="{y1}" x2="{mx+45}" y2="{y1}" '
        f'stroke="{color}" stroke-width="1.5" opacity="0.6"/>'
    )

    return "\n".join(lines)


def generate_talisman_svg(
    planet: str,
    width: int = 400,
    height: int = 480,
    show_kamea: bool = True,
    planet_lon: Optional[float] = None,
    moon_phase: Optional[str] = None,
) -> str:
    """
    生成指定行星的高品質古抄本風格護符 SVG。

    Parameters
    ----------
    planet : str
        行星英文名稱
    width, height : int
        SVG 尺寸（px）
    show_kamea : bool
        是否顯示行星魔法方陣
    planet_lon : float, optional
        行星當前經度（用於標示）
    moon_phase : str, optional
        當前月相（用於標示）

    Returns
    -------
    str
        完整 SVG 字串
    """
    pcolor = _PLANET_COLORS.get(planet, _C_GOLD)
    sigil  = _PLANET_SIGILS.get(planet, "✦")
    glyph_color = pcolor

    cx = width / 2
    # 羊皮紙背景漸層
    bg_id = f"parchment_{planet}"
    circle_r = min(width, height) * 0.3

    talisman_data = PLANETARY_TALISMAN_BY_PLANET.get(planet) if _DATA_AVAILABLE else None
    planet_cn = PLANET_CN.get(planet, planet) if _CALC_AVAILABLE else planet
    metal_cn  = talisman_data.metal_cn if talisman_data else "金屬"

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',

        # ── 定義區 ────────────────────────────────────────────
        '<defs>',
        # 羊皮紙漸層
        f'<radialGradient id="{bg_id}" cx="50%" cy="45%" r="60%">',
        f'  <stop offset="0%" stop-color="#FDF0D5"/>',
        f'  <stop offset="60%" stop-color="{_C_PARCHMENT}"/>',
        f'  <stop offset="100%" stop-color="{_C_PARCHMENT_DK}"/>',
        '</radialGradient>',
        # 金屬光澤濾鏡
        '<filter id="emboss" x="-20%" y="-20%" width="140%" height="140%">',
        '  <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="blur"/>',
        '  <feOffset in="blur" dx="2" dy="2" result="shadow"/>',
        '  <feFlood flood-color="#00000088" result="color"/>',
        '  <feComposite in="color" in2="shadow" operator="in" result="shadow_colored"/>',
        '  <feMerge>',
        '    <feMergeNode in="shadow_colored"/>',
        '    <feMergeNode in="SourceGraphic"/>',
        '  </feMerge>',
        '</filter>',
        # 金箔光澤
        '<filter id="gold_glow">',
        f'  <feGaussianBlur stdDeviation="4" result="blur"/>',
        f'  <feFlood flood-color="{pcolor}" flood-opacity="0.5" result="color"/>',
        '  <feComposite in="color" in2="blur" operator="in" result="glow"/>',
        '  <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>',
        '</filter>',
        '</defs>',

        # ── 背景 ──────────────────────────────────────────────
        f'<rect width="{width}" height="{height}" fill="url(#{bg_id})" rx="8"/>',

        # 細微羊皮紙紋理（橫線模擬）
        *[
            f'<line x1="0" y1="{30 + i * 22}" x2="{width}" y2="{30 + i * 22}" '
            f'stroke="#C8B06088" stroke-width="0.4" opacity="0.3"/>'
            for i in range(height // 22)
        ],

        # ── 裝飾邊框 ──────────────────────────────────────────
        _decorative_border_svg(width, height, _C_GOLD),
    ]

    # ── 頂部標題帶 ────────────────────────────────────────────
    title_y = 52
    parts += [
        f'<rect x="25" y="35" width="{width-50}" height="28" '
        f'fill="{_C_RED_INK}" opacity="0.85" rx="3"/>',
        f'<text x="{cx}" y="{title_y}" text-anchor="middle" '
        f'font-size="13" font-weight="bold" fill="{_C_PARCHMENT}" '
        f'font-family="serif" letter-spacing="3">'
        f'✦ {planet.upper()} TALISMAN · {planet_cn}護符 ✦</text>',
    ]

    # ── 中央行星符文圓 ────────────────────────────────────────
    main_cy = height * 0.38
    parts += [
        # 外圓（凸紋效果）
        f'<circle cx="{cx}" cy="{main_cy}" r="{circle_r + 10}" '
        f'fill="none" stroke="{pcolor}" stroke-width="2" opacity="0.3"/>',
        f'<circle cx="{cx}" cy="{main_cy}" r="{circle_r + 5}" '
        f'fill="none" stroke="{pcolor}" stroke-width="1" opacity="0.5"/>',
        f'<circle cx="{cx}" cy="{main_cy}" r="{circle_r}" '
        f'fill="{pcolor}18" stroke="{pcolor}" stroke-width="2.5" '
        f'filter="url(#gold_glow)"/>',
        # 內圓（深色填充）
        f'<circle cx="{cx}" cy="{main_cy}" r="{circle_r * 0.75}" '
        f'fill="{_C_INK}22" stroke="{pcolor}" stroke-width="1" opacity="0.6"/>',
    ]

    # 幾何圖案（依行星）
    gr = circle_r * 0.55
    if planet == "Venus":
        parts.append(_draw_pentagon(cx, main_cy, gr, pcolor))
    elif planet in ("Sun", "Jupiter"):
        parts.append(_draw_hexagram(cx, main_cy, gr, pcolor))
    elif planet == "Mercury":
        parts.append(_draw_octagram(cx, main_cy, gr, pcolor))
    elif planet == "Saturn":
        # 三角形（土星）
        tri_pts = []
        for i in range(3):
            angle = math.pi * (2 * i / 3 - 0.5)
            x = cx + gr * math.cos(angle)
            y = main_cy + gr * math.sin(angle)
            tri_pts.append(f"{x:.1f},{y:.1f}")
        parts.append(
            f'<polygon points="{" ".join(tri_pts)}" fill="none" '
            f'stroke="{pcolor}" stroke-width="1.2" opacity="0.7"/>'
        )
    elif planet == "Mars":
        # 四角形（火星）
        sq_pts = []
        for i in range(4):
            angle = math.pi * (2 * i / 4 - 0.25)
            x = cx + gr * math.cos(angle)
            y = main_cy + gr * math.sin(angle)
            sq_pts.append(f"{x:.1f},{y:.1f}")
        parts.append(
            f'<polygon points="{" ".join(sq_pts)}" fill="none" '
            f'stroke="{pcolor}" stroke-width="1.2" opacity="0.7"/>'
        )
    elif planet == "Moon":
        # 新月形
        parts.append(
            f'<path d="M {cx-gr*0.5},{main_cy-gr*0.6} '
            f'A {gr*0.7},{gr*0.7} 0 1,1 {cx-gr*0.5},{main_cy+gr*0.6} '
            f'A {gr*0.4},{gr*0.4} 0 1,0 {cx-gr*0.5},{main_cy-gr*0.6}" '
            f'fill="{pcolor}30" stroke="{pcolor}" stroke-width="1.5" opacity="0.7"/>'
        )

    # 大行星符文
    parts += [
        f'<text x="{cx}" y="{main_cy + 22}" text-anchor="middle" '
        f'font-size="72" fill="{pcolor}" opacity="0.9" '
        f'filter="url(#emboss)" font-family="serif">{sigil}</text>',
    ]

    # 環形文字（拉丁名）
    ring_r = circle_r + 2
    text_count = len(planet) + 1
    for k, char in enumerate(planet.upper() + " "):
        angle = math.pi * (2 * k / text_count - 0.5)
        tx = cx + ring_r * math.cos(angle)
        ty = main_cy + ring_r * math.sin(angle)
        parts.append(
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" '
            f'font-size="8" fill="{_C_RED_INK}" opacity="0.8" '
            f'transform="rotate({math.degrees(angle)+90:.1f},{tx:.1f},{ty:.1f})" '
            f'font-family="serif">{char}</text>'
        )

    # ── 魔法方陣（Kamea）────────────────────────────────────
    if show_kamea:
        kamea_y = height * 0.63
        kamea_size = min(width * 0.4, 160)
        kamea_x = cx - kamea_size / 2
        # Kamea 背景
        parts += [
            f'<rect x="{kamea_x - 5}" y="{kamea_y - 5}" '
            f'width="{kamea_size + 10}" height="{kamea_size + 10}" '
            f'fill="{_C_INK}22" stroke="{pcolor}" stroke-width="1" opacity="0.5" rx="4"/>',
            _generate_kamea_svg_grid(planet, int(kamea_size), kamea_x, kamea_y),
            f'<text x="{cx}" y="{kamea_y + kamea_size + 16}" text-anchor="middle" '
            f'font-size="9" fill="{_C_SUBTLE}" opacity="0.8" '
            f'font-family="serif" font-style="italic">Kamea of {planet}</text>',
        ]

    # ── 底部資訊帶 ────────────────────────────────────────────
    info_y = height - 52
    parts += [
        f'<rect x="25" y="{info_y - 5}" width="{width-50}" height="36" '
        f'fill="{_C_INK}33" stroke="{pcolor}" stroke-width="0.8" opacity="0.5" rx="3"/>',
        f'<text x="{cx}" y="{info_y + 10}" text-anchor="middle" '
        f'font-size="9" fill="{_C_GOLD}" opacity="0.9" font-family="serif">'
        f'⚗ {metal_cn} · {(talisman_data.day_of_week_cn if talisman_data else "")} '
        f'· {(talisman_data.incense_cn if talisman_data else "")} ⚗</text>',
    ]

    if planet_lon is not None:
        parts.append(
            f'<text x="{cx}" y="{info_y + 23}" text-anchor="middle" '
            f'font-size="8" fill="{_C_SUBTLE}" opacity="0.8" font-family="monospace">'
            f'{_PLANET_SIGILS.get(planet, "✦")} Lon: {planet_lon:.2f}°</text>'
        )

    if moon_phase:
        parts.append(
            f'<text x="{cx}" y="{info_y + 33}" text-anchor="middle" '
            f'font-size="8" fill="{_C_SUBTLE}" opacity="0.7" font-family="serif">'
            f'☽ {moon_phase}</text>'
        )

    # 印記行星數字字母
    signature_chars = {
        "Sun": "①", "Moon": "②", "Mercury": "③",
        "Venus": "④", "Mars": "⑤", "Jupiter": "⑥", "Saturn": "⑦",
    }
    sig = signature_chars.get(planet, "✦")
    parts.append(
        f'<text x="{width - 30}" y="{height - 25}" text-anchor="middle" '
        f'font-size="14" fill="{pcolor}" opacity="0.5" font-family="serif">{sig}</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


def _svg_to_b64(svg: str) -> str:
    """將 SVG 字串編碼為 base64 data URI（用於下載）。"""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


# ============================================================
# 評分顯示輔助函式
# ============================================================

def _score_bar_html(score: float, max_score: float = 100.0, color: str = _C_GOLD) -> str:
    """渲染分數進度條 HTML。"""
    pct = min(100, max(0, score / max_score * 100))
    bg_color = (
        _C_GOOD  if pct >= 70 else
        "#F5A623" if pct >= 50 else
        _C_WARN
    )
    return (
        f'<div style="background:{_C_CARD};border-radius:6px;height:12px;'
        f'width:100%;border:1px solid {_C_BORDER}44;">'
        f'<div style="background:{bg_color};border-radius:6px;height:100%;'
        f'width:{pct:.1f}%;transition:width 0.5s;"></div></div>'
        f'<div style="font-size:11px;color:{_C_SUBTLE};margin-top:2px;">'
        f'{score:.1f} / {max_score:.0f} ({pct:.0f}%)</div>'
    )


def _planet_card_html(planet: str, t: Optional["PlanetaryTalisman"] = None) -> str:
    """渲染行星護符資訊卡 HTML。"""
    if t is None and _DATA_AVAILABLE:
        t = PLANETARY_TALISMAN_BY_PLANET.get(planet)

    pcolor = _PLANET_COLORS.get(planet, _C_GOLD)
    sigil  = _PLANET_SIGILS.get(planet, "✦")
    planet_cn = PLANET_CN.get(planet, planet) if _CALC_AVAILABLE else planet

    uses_html = ""
    if t:
        uses_html = "".join(
            f'<span style="display:inline-block;padding:2px 8px;margin:2px;'
            f'border-radius:12px;background:{pcolor}22;border:1px solid {pcolor}66;'
            f'font-size:11px;color:{_C_TEXT};">{auto_cn(u)}</span>'
            for u in (t.purposes_cn or [])
        )

    materials_html = ""
    if t:
        materials_html = (
            f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:8px 0;">'
            f'<div style="background:{_C_CARD};border-radius:6px;padding:6px 8px;border:1px solid {_C_BORDER}33;">'
            f'<div style="font-size:10px;color:{_C_SUBTLE};">⚗ {auto_cn("金屬")}</div>'
            f'<div style="font-size:12px;color:{_C_TEXT};">{auto_cn(t.metal_cn)}</div></div>'
            f'<div style="background:{_C_CARD};border-radius:6px;padding:6px 8px;border:1px solid {_C_BORDER}33;">'
            f'<div style="font-size:10px;color:{_C_SUBTLE};">💎 {auto_cn("寶石")}</div>'
            f'<div style="font-size:12px;color:{_C_TEXT};">{auto_cn(t.gemstone_cn)}</div></div>'
            f'<div style="background:{_C_CARD};border-radius:6px;padding:6px 8px;border:1px solid {_C_BORDER}33;">'
            f'<div style="font-size:10px;color:{_C_SUBTLE};">🕯 {auto_cn("薰香")}</div>'
            f'<div style="font-size:12px;color:{_C_TEXT};">{auto_cn(t.incense_cn)}</div></div>'
            f'</div>'
        )

    return f"""
<div style="border:1px solid {pcolor}88;border-radius:12px;
     background:{_C_CARD};padding:16px 20px;margin:8px 0;
     box-shadow:0 4px 20px rgba(0,0,0,0.4);">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
    <div style="font-size:40px;color:{pcolor};">{sigil}</div>
    <div>
      <div style="font-size:20px;font-weight:900;color:{pcolor};">{planet}</div>
      <div style="font-size:13px;color:{_C_TEXT};">{auto_cn(planet_cn)}</div>
      {f'<div style="font-size:11px;color:{_C_SUBTLE};">⚗ {auto_cn(t.metal_cn)} · 📅 {auto_cn(t.day_of_week_cn)}</div>' if t else ''}
    </div>
  </div>
  {materials_html}
  <div style="margin-bottom:8px;">
    <div style="font-size:11px;color:{_C_SUBTLE};margin-bottom:4px;">{auto_cn("護符用途")}</div>
    <div>{uses_html}</div>
  </div>
  {f'<div style="background:{_C_INK}22;border-left:3px solid {pcolor};border-radius:4px;padding:8px 12px;margin-top:8px;font-size:12px;color:{_C_TEXT};">{auto_cn(t.effects_cn)}</div>' if t else ''}
</div>
"""


def _electional_score_html(score: "ElectionalScore") -> str:
    """渲染電擇評分 HTML 卡片。"""
    grade_color = _GRADE_COLORS.get(score.grade, _C_NEUTRAL)
    planet_cn = score.planet_cn
    sigil = _PLANET_SIGILS.get(score.planet, "✦")

    passed_html = "".join(
        f'<div style="display:flex;gap:6px;align-items:flex-start;margin:3px 0;">'
        f'<span style="color:{_C_GOOD};font-size:13px;">✓</span>'
        f'<span style="font-size:12px;color:{_C_TEXT};">{auto_cn(c)}</span></div>'
        for c in score.checks_passed
    )
    failed_html = "".join(
        f'<div style="display:flex;gap:6px;align-items:flex-start;margin:3px 0;">'
        f'<span style="color:{_C_WARN};font-size:13px;">✗</span>'
        f'<span style="font-size:12px;color:{_C_TEXT};">{auto_cn(c)}</span></div>'
        for c in score.checks_failed
    )
    warn_html = "".join(
        f'<div style="display:flex;gap:6px;align-items:flex-start;margin:3px 0;">'
        f'<span style="color:#F5A623;font-size:13px;">⚠</span>'
        f'<span style="font-size:12px;color:{_C_TEXT};">{auto_cn(w)}</span></div>'
        for w in score.warnings
    )

    moon = score.moon_condition
    moon_html = (
        f'<div style="display:flex;gap:8px;flex-wrap:wrap;">'
        f'<span style="font-size:12px;color:{_C_TEXT};">☽ {auto_cn(moon.sign_cn)} {moon.degree_in_sign:.1f}°</span>'
        f'<span style="font-size:12px;color:{_C_TEXT};">{auto_cn(moon.phase_cn)}</span>'
        f'{"<span style=\"color:#F5A623;font-size:11px;\">⚠ Via Combusta</span>" if moon.is_via_combusta else ""}'
        f'{"<span style=\"color:#c0392b;font-size:11px;\">🔥 Combust</span>" if moon.is_combust else ""}'
        f'{"<span style=\"color:#FFD700;font-size:11px;\">✦ Cazimi</span>" if moon.is_cazimi else ""}'
        f'</div>'
    )

    return f"""
<div style="border:2px solid {grade_color};border-radius:12px;
     background:{_C_CARD};padding:18px 22px;margin:10px 0;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
    <div style="font-size:18px;font-weight:900;color:{grade_color};">
      {sigil} {planet_cn} 電擇評分
    </div>
    <div style="font-size:28px;font-weight:900;color:{grade_color};">
      {score.grade_cn}
    </div>
  </div>

  <div style="margin-bottom:12px;">
    {_score_bar_html(score.total_score)}
  </div>

  <div style="margin-bottom:10px;">
    <div style="font-size:11px;color:{_C_SUBTLE};margin-bottom:4px;">{auto_cn("月亮狀態")}</div>
    {moon_html}
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
    <div>
      <div style="font-size:11px;color:{_C_GOOD};font-weight:700;margin-bottom:4px;">{auto_cn("✓ 通過條件")}</div>
      {passed_html if passed_html else f'<div style="font-size:12px;color:{_C_SUBTLE};">—</div>'}
    </div>
    <div>
      <div style="font-size:11px;color:{_C_WARN};font-weight:700;margin-bottom:4px;">{auto_cn("✗ 未通過條件")}</div>
      {failed_html if failed_html else f'<div style="font-size:12px;color:{_C_SUBTLE};">—</div>'}
    </div>
  </div>
  {f'<div style="margin-top:10px;">{warn_html}</div>' if warn_html else ''}
</div>
"""


# ============================================================
# Streamlit 互動式嚮導
# ============================================================

def render_talisman_wizard() -> None:
    """
    渲染互動式 Talisman 製作嚮導 Streamlit 頁面。

    流程：
      1. 使用者選擇目的（愛情、財富、保護等）
      2. 系統推薦最適行星
      3. 顯示對應護符資料（材質、圖像、祈請文）
      4. 生成 SVG 護符預覽
    """
    st.markdown(f"""
<style>
.talisman-hero {{
    background: linear-gradient(135deg, {_C_DEEP_BG} 0%, #2d1b4e 50%, #1a0a00 100%);
    border: 2px solid {_C_GOLD};
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
    text-align: center;
}}
.talisman-hero h2 {{
    font-size: 26px;
    font-weight: 900;
    color: {_C_HEADER};
    letter-spacing: 3px;
    margin: 0 0 8px;
    font-family: serif;
}}
.talisman-hero p {{
    font-size: 13px;
    color: {_C_SUBTLE};
    margin: 0;
    font-style: italic;
}}
</style>
<div class="talisman-hero">
  <h2>⚗ Picatrix 護符製作嚮導</h2>
  <p>{auto_cn("依據《賢者之目的》(Picatrix / Ghayat al-Hakim) 卷二第十章 · Agrippa《神秘哲學三書》傳統")}</p>
</div>
""", unsafe_allow_html=True)

    if not (_CALC_AVAILABLE and _DATA_AVAILABLE):
        st.error(auto_cn("計算模組載入失敗，請確認 astro/talismanic_magic.py 已正確安裝。"))
        return

    # ── 步驟一：選擇目的 ──────────────────────────────────────
    st.markdown(
        f'<div style="font-size:16px;font-weight:700;color:{_C_HEADER};margin-bottom:8px;">'
        + auto_cn("第一步：選擇護符目的")
        + "</div>",
        unsafe_allow_html=True,
    )

    purpose_options = {p["cn"]: p["key"] for p in ALL_PURPOSES}
    purpose_options_display = list(purpose_options.keys())

    # 按類別分組顯示
    category_groups = {
        auto_cn("愛情與關係"): ["愛情", "吸引力", "和解"],
        auto_cn("財富與商業"): ["財富", "好運", "商業"],
        auto_cn("保護與驅邪"): ["保護", "驅逐", "束縛"],
        auto_cn("健康與生育"): ["健康", "療癒", "生育"],
        auto_cn("智慧與知識"): ["智慧", "學習", "占卜"],
        auto_cn("權力與勝利"): ["權力", "權威", "勝利"],
        auto_cn("其他"): ["旅行", "溝通", "競技", "農業"],
    }

    col_purpose, col_preview = st.columns([3, 2])
    with col_purpose:
        chosen_cn = st.radio(
            auto_cn("請選擇您的目的："),
            options=purpose_options_display,
            horizontal=False,
            key="_wizard_purpose",
        )
        chosen_key = purpose_options.get(chosen_cn, "wealth")

    with col_preview:
        # 即時預覽選擇的目的說明
        talisman_info = PLANETARY_TALISMAN_BY_PLANET.get(
            (PURPOSE_TO_PLANETS if _CALC_AVAILABLE else {}).get(chosen_key, ["Jupiter"])[0]
            if _CALC_AVAILABLE else "Jupiter",
        )
        if talisman_info:
            recommended_planet_key = list(
                (PURPOSE_TO_PLANETS if _CALC_AVAILABLE else {}).get(chosen_key, ["Jupiter"])
            )[0] if _CALC_AVAILABLE else "Jupiter"
            pcolor = _PLANET_COLORS.get(recommended_planet_key, _C_GOLD)
            sigil  = _PLANET_SIGILS.get(recommended_planet_key, "✦")
            planet_cn_disp = PLANET_CN.get(recommended_planet_key, "")
            st.markdown(
                f'<div style="border:1px solid {pcolor}66;border-radius:10px;'
                f'background:{_C_CARD};padding:14px 16px;text-align:center;">'
                f'<div style="font-size:48px;color:{pcolor};">{sigil}</div>'
                f'<div style="font-size:16px;font-weight:700;color:{pcolor};">'
                f'{recommended_planet_key} · {auto_cn(planet_cn_disp)}</div>'
                f'<div style="font-size:11px;color:{_C_SUBTLE};margin-top:4px;">'
                f'{auto_cn("推薦行星")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── 步驟二：取得推薦 ──────────────────────────────────────
    st.divider()
    st.markdown(
        f'<div style="font-size:16px;font-weight:700;color:{_C_HEADER};margin-bottom:8px;">'
        + auto_cn("第二步：推薦護符")
        + "</div>",
        unsafe_allow_html=True,
    )

    if st.button(auto_cn("🔮 生成護符推薦"), key="_wizard_generate", type="primary"):
        with st.spinner(auto_cn("正在計算推薦護符……")):
            try:
                rec = recommend_talisman(chosen_key)
            except Exception as e:
                st.error(f"計算錯誤：{e}")
                return

        st.success(auto_cn(f"為「{chosen_cn}」找到 {len(rec.planetary_talismans)} 種護符推薦"))

        # 顯示推薦護符
        for i, (p_name, p_tal) in enumerate(
            zip(rec.recommended_planets, rec.planetary_talismans)
        ):
            with st.expander(
                f"{_PLANET_SIGILS.get(p_name, '✦')} {p_name} · {auto_cn(PLANET_CN.get(p_name, p_name))}"
                + (" ★ 首選" if i == 0 else ""),
                expanded=(i == 0),
            ):
                col_info, col_svg = st.columns([3, 2])

                with col_info:
                    st.markdown(_planet_card_html(p_name, p_tal), unsafe_allow_html=True)

                    # 擇時規則
                    st.markdown(
                        f'<div style="font-size:13px;font-weight:700;color:{_C_HEADER};'
                        f'margin:10px 0 6px;">{auto_cn("📅 Picatrix 擇時規則")}</div>',
                        unsafe_allow_html=True,
                    )
                    for rule in (p_tal.electional_rules_cn or []):
                        st.markdown(
                            f'<div style="font-size:12px;color:{_C_TEXT};'
                            f'padding:2px 0;border-left:2px solid {_C_GOLD};padding-left:8px;margin:3px 0;">'
                            f'{auto_cn(rule)}</div>',
                            unsafe_allow_html=True,
                        )

                    # 刻印圖像
                    if p_tal.image_description_cn:
                        st.markdown(
                            f'<div style="background:{_C_CARD};border-left:3px solid {_PLANET_COLORS.get(p_name, _C_GOLD)};'
                            f'border-radius:4px;padding:10px 14px;margin-top:10px;">'
                            f'<div style="font-size:11px;color:{_C_SUBTLE};margin-bottom:4px;">'
                            f'{auto_cn("🖋 護符刻印圖像（Picatrix 原典）")}</div>'
                            f'<div style="font-size:12px;color:{_C_TEXT};">{auto_cn(p_tal.image_description_cn)}</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                    # 祈請文
                    if p_tal.invocation_cn:
                        with st.expander(auto_cn("📜 祈請文 / Invocation"), expanded=False):
                            st.markdown(
                                f'<div style="font-size:13px;color:{_C_TEXT};line-height:1.7;'
                                f'font-style:italic;">{auto_cn(p_tal.invocation_cn)}</div>'
                                f'<hr style="border-color:{_C_BORDER}44;"/>'
                                f'<div style="font-size:12px;color:{_C_SUBTLE};">'
                                f'{p_tal.invocation_en}</div>',
                                unsafe_allow_html=True,
                            )

                with col_svg:
                    # SVG 護符預覽
                    svg = generate_talisman_svg(p_name, width=300, height=360)
                    st.markdown(
                        f'<div style="text-align:center;">{svg}</div>',
                        unsafe_allow_html=True,
                    )
                    # 下載按鈕
                    b64 = _svg_to_b64(svg)
                    st.markdown(
                        f'<div style="text-align:center;margin-top:8px;">'
                        f'<a href="{b64}" download="{p_name.lower()}_talisman.svg" '
                        f'style="background:{_PLANET_COLORS.get(p_name, _C_GOLD)};'
                        f'color:{_C_INK};padding:6px 16px;border-radius:20px;'
                        f'font-size:12px;font-weight:700;text-decoration:none;">'
                        f'⬇ {auto_cn("下載 SVG")}</a></div>',
                        unsafe_allow_html=True,
                    )

        # 月亮 Decan 護符
        if rec.decan_talisman:
            st.divider()
            d = rec.decan_talisman
            st.markdown(
                f'<div style="font-size:14px;font-weight:700;color:{_C_HEADER};margin-bottom:8px;">'
                + auto_cn(f"🌙 當前月亮 Decan 護符（{d.sign_cn} {d.degrees_start}°–{d.degrees_end}°，{d.ruler_cn}主）")
                + "</div>",
                unsafe_allow_html=True,
            )
            ruler_color = _PLANET_COLORS.get(d.ruler, _C_GOLD)
            st.markdown(
                f'<div style="border:1px solid {ruler_color}66;border-radius:10px;'
                f'background:{_C_CARD};padding:14px 18px;">'
                f'<div style="font-size:14px;font-weight:700;color:{ruler_color};margin-bottom:6px;">'
                f'{auto_cn(d.sign_cn)} 第 {d.decan_in_sign} Decan · {d.ruler_cn}主</div>'
                f'<div style="font-size:12px;color:{_C_TEXT};margin-bottom:8px;">'
                f'{auto_cn(d.image_description_cn)}</div>'
                f'<div style="display:flex;flex-wrap:wrap;gap:4px;">'
                + "".join(
                    f'<span style="background:{ruler_color}22;border:1px solid {ruler_color}66;'
                    f'border-radius:12px;padding:2px 8px;font-size:11px;color:{_C_TEXT};">'
                    f'{auto_cn(p)}</span>'
                    for p in (d.powers_cn or [])
                )
                + "</div></div>",
                unsafe_allow_html=True,
            )

        # 未來最佳時機
        if rec.next_windows:
            st.divider()
            st.markdown(
                f'<div style="font-size:14px;font-weight:700;color:{_C_HEADER};margin-bottom:8px;">'
                + auto_cn(f"📅 未來最佳製符時機（{rec.primary_recommendation_cn}護符，14 天內）")
                + "</div>",
                unsafe_allow_html=True,
            )
            for w in rec.next_windows[:5]:
                grade_c = _GRADE_COLORS.get(w.grade, _C_NEUTRAL)
                pcolor  = _PLANET_COLORS.get(w.planet, _C_GOLD)
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'border:1px solid {grade_c}55;border-radius:8px;'
                    f'background:{_C_CARD};padding:10px 14px;margin:4px 0;">'
                    f'<div>'
                    f'<span style="font-size:13px;font-weight:700;color:{_C_HEADER};">'
                    f'{w.dt_utc.strftime("%Y-%m-%d %H:%M")} UTC · {auto_cn(w.day_of_week_cn)}</span><br>'
                    f'<span style="font-size:11px;color:{_C_SUBTLE};">'
                    f'☽ {auto_cn(w.moon_sign_cn)} · {auto_cn(w.moon_phase_cn)} · '
                    f'{"漸盈" if w.is_waxing else "漸虧"}</span>'
                    f'</div>'
                    f'<div style="text-align:right;">'
                    f'<span style="font-size:16px;font-weight:900;color:{grade_c};">{auto_cn(w.grade_cn)}</span><br>'
                    f'<span style="font-size:11px;color:{_C_SUBTLE};">{w.score:.0f}/100</span>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )


# ============================================================
# 即時電擇計算器
# ============================================================

def render_electional_calc() -> None:
    """
    渲染即時電擇計算器 Streamlit 頁面。

    使用者輸入日期時間，選擇目標行星，
    系統依據 Picatrix 嚴格規則評估製符適宜程度。
    """
    st.markdown(
        f'<div style="font-size:13px;color:{_C_SUBTLE};margin-bottom:12px;font-style:italic;">'
        + auto_cn("依據 Picatrix 卷二第十章 · Lilly《基督教占星》擇日規則，精確評估製符時機")
        + "</div>",
        unsafe_allow_html=True,
    )

    if not _CALC_AVAILABLE:
        st.error(auto_cn("計算模組未載入。"))
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        _date = st.date_input(
            auto_cn("📅 製符日期"),
            value=datetime.now().date(),
            key="_elect_date",
        )
    with col2:
        _time = st.time_input(
            auto_cn("🕐 製符時間"),
            value=datetime.now().time(),
            key="_elect_time",
        )
    with col3:
        _tz = st.number_input(
            auto_cn("🌍 時區 (UTC±)"),
            value=8.0, min_value=-12.0, max_value=14.0, step=0.5,
            format="%.1f", key="_elect_tz",
        )

    # 行星選擇
    _planet_options = list(PLANET_CN.keys()) if _CALC_AVAILABLE else []
    _planet_display = [f"{_PLANET_SIGILS.get(p, '')} {PLANET_CN.get(p, p)} ({p})" for p in _planet_options]
    _chosen_idx = st.selectbox(
        auto_cn("⚗ 目標行星"),
        options=range(len(_planet_options)),
        format_func=lambda i: _planet_display[i],
        key="_elect_planet",
    )
    chosen_planet = _planet_options[_chosen_idx]

    if st.button(auto_cn("⚡ 計算電擇評分"), key="_elect_calc", type="primary"):
        # 計算 JD
        dt_local = datetime(_date.year, _date.month, _date.day, _time.hour, _time.minute)
        dt_utc = datetime(_date.year, _date.month, _date.day,
                          _time.hour, _time.minute, tzinfo=timezone.utc)
        jd = _jd_from_dt(dt_utc) - _tz / 24.0

        with st.spinner(auto_cn("計算中……")):
            try:
                score = evaluate_electional_moment(chosen_planet, jd)
            except Exception as e:
                st.error(f"計算錯誤：{e}")
                return

        # 顯示評分
        st.markdown(
            _electional_score_html(score),
            unsafe_allow_html=True,
        )

        # SVG 護符預覽（帶當前行星位置）
        col_svg, col_detail = st.columns([2, 3])
        with col_svg:
            svg = generate_talisman_svg(
                chosen_planet,
                planet_lon=score.planet_position.longitude,
                moon_phase=score.moon_condition.phase_cn,
            )
            st.markdown(svg, unsafe_allow_html=True)

        with col_detail:
            p = score.planet_position
            m = score.moon_condition
            pcolor = _PLANET_COLORS.get(chosen_planet, _C_GOLD)

            st.markdown(
                f'<div style="border:1px solid {pcolor}55;border-radius:10px;'
                f'background:{_C_CARD};padding:14px 18px;margin-bottom:10px;">'
                f'<div style="font-size:13px;font-weight:700;color:{pcolor};margin-bottom:8px;">'
                f'{auto_cn("行星位置")}</div>'
                f'<div style="font-size:12px;color:{_C_TEXT};">'
                f'{PLANET_GLYPHS.get(chosen_planet, "")} {p.sign_cn} {p.degree_in_sign:.2f}° · '
                f'{auto_cn(p.dignity)} · '
                f'{"逆行 ℞" if p.is_retrograde else "順行"}</div>'
                f'</div>'
                f'<div style="border:1px solid {_C_GOLD}44;border-radius:10px;'
                f'background:{_C_CARD};padding:14px 18px;">'
                f'<div style="font-size:13px;font-weight:700;color:{_C_GOLD};margin-bottom:8px;">'
                f'{auto_cn("月亮狀態")}</div>'
                f'<div style="font-size:12px;color:{_C_TEXT};">'
                f'☽ {m.sign_cn} {m.degree_in_sign:.2f}° · {auto_cn(m.phase_cn)} · '
                f'{"漸盈" if m.is_waxing else "漸虧"}</div>'
                + (f'<div style="color:#c0392b;font-size:11px;margin-top:4px;">'
                   f'⚠ Via Combusta！</div>' if m.is_via_combusta else "")
                + (f'<div style="color:#c0392b;font-size:11px;margin-top:4px;">'
                   f'🔥 Combust！</div>' if m.is_combust else "")
                + "</div>",
                unsafe_allow_html=True,
            )

            # 護符資料庫資訊
            if _DATA_AVAILABLE:
                t = PLANETARY_TALISMAN_BY_PLANET.get(chosen_planet)
                if t:
                    st.markdown(
                        f'<div style="border:1px solid {_C_GOLD}44;border-radius:10px;'
                        f'background:{_C_CARD};padding:14px 18px;margin-top:10px;">'
                        f'<div style="font-size:13px;font-weight:700;color:{_C_GOLD};margin-bottom:8px;">'
                        f'{auto_cn("製符材質（Picatrix）")}</div>'
                        f'<div style="font-size:12px;color:{_C_TEXT};">'
                        f'⚗ {auto_cn(t.metal_cn)} · 💎 {auto_cn(t.gemstone_cn)}<br>'
                        f'🕯 {auto_cn(t.incense_cn)} · 🎨 {auto_cn(t.color_cn)}'
                        f'</div></div>',
                        unsafe_allow_html=True,
                    )


# ============================================================
# 護符資料庫瀏覽
# ============================================================

def render_talisman_database() -> None:
    """
    渲染完整護符資料庫瀏覽頁面。
    包含七行星護符與 36 Decan 護符。
    """
    if not _DATA_AVAILABLE:
        st.error(auto_cn("資料模組未載入。"))
        return

    db_tab_planets, db_tab_decans = st.tabs([
        auto_cn("🪐 七行星護符"),
        auto_cn("🌀 36 Decan 護符"),
    ])

    with db_tab_planets:
        st.markdown(
            f'<div style="font-size:13px;color:{_C_SUBTLE};margin-bottom:12px;font-style:italic;">'
            + auto_cn("七顆傳統行星護符完整資料 · 源自 Picatrix《賢者之目的》與 Agrippa《神秘哲學三書》")
            + "</div>",
            unsafe_allow_html=True,
        )

        # 行星選擇格
        col_grid = st.columns(7)
        for i, talisman in enumerate(PLANETARY_TALISMANS):
            pcolor = _PLANET_COLORS.get(talisman.planet, _C_GOLD)
            sigil  = _PLANET_SIGILS.get(talisman.planet, "✦")
            with col_grid[i]:
                st.markdown(
                    f'<div style="border:1px solid {pcolor}88;border-radius:10px;'
                    f'background:{_C_CARD};padding:10px;text-align:center;cursor:pointer;">'
                    f'<div style="font-size:24px;color:{pcolor};">{sigil}</div>'
                    f'<div style="font-size:12px;font-weight:700;color:{pcolor};">{talisman.planet}</div>'
                    f'<div style="font-size:10px;color:{_C_SUBTLE};">{auto_cn(talisman.planet_cn)}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.divider()

        # 完整資料
        for talisman in PLANETARY_TALISMANS:
            pcolor = _PLANET_COLORS.get(talisman.planet, _C_GOLD)
            sigil  = _PLANET_SIGILS.get(talisman.planet, "✦")
            with st.expander(
                f"{sigil} {talisman.planet} · {auto_cn(talisman.planet_cn)} "
                f"({auto_cn(talisman.metal_cn)} · {auto_cn(talisman.day_of_week_cn)})",
                expanded=False,
            ):
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.markdown(_planet_card_html(talisman.planet, talisman), unsafe_allow_html=True)

                    # 電擇規則
                    st.markdown(
                        f'<div style="font-size:13px;font-weight:700;color:{_C_HEADER};'
                        f'margin:10px 0 6px;">{auto_cn("📅 Picatrix 擇時規則")}</div>',
                        unsafe_allow_html=True,
                    )
                    for rule in (talisman.electional_rules_cn or []):
                        st.markdown(
                            f'<div style="font-size:12px;color:{_C_TEXT};'
                            f'border-left:2px solid {pcolor};padding-left:8px;margin:3px 0;">'
                            f'{auto_cn(rule)}</div>',
                            unsafe_allow_html=True,
                        )

                    # 圖像描述
                    if talisman.image_description_cn:
                        st.markdown(
                            f'<div style="background:{_C_CARD};border-left:3px solid {pcolor};'
                            f'border-radius:4px;padding:10px 14px;margin-top:10px;">'
                            f'<div style="font-size:11px;color:{_C_SUBTLE};margin-bottom:4px;">'
                            f'{auto_cn("🖋 Picatrix 護符圖像")}</div>'
                            f'<div style="font-size:12px;color:{_C_TEXT};">'
                            f'{auto_cn(talisman.image_description_cn)}</div></div>',
                            unsafe_allow_html=True,
                        )

                    # 祈請文
                    with st.expander(auto_cn("📜 祈請文"), expanded=False):
                        st.markdown(
                            f'<div style="font-size:13px;color:{_C_TEXT};line-height:1.7;font-style:italic;">'
                            f'{auto_cn(talisman.invocation_cn)}</div>'
                            f'<hr style="border-color:{_C_BORDER}44;"/>'
                            f'<div style="font-size:12px;color:{_C_SUBTLE};">'
                            f'{talisman.invocation_en}</div>',
                            unsafe_allow_html=True,
                        )

                with col2:
                    svg = generate_talisman_svg(talisman.planet, width=280, height=340)
                    st.markdown(
                        f'<div style="text-align:center;">{svg}</div>',
                        unsafe_allow_html=True,
                    )
                    # 出處
                    st.markdown(
                        f'<div style="font-size:10px;color:{_C_SUBTLE};text-align:center;'
                        f'margin-top:4px;font-style:italic;">'
                        f'{talisman.picatrix_source}</div>',
                        unsafe_allow_html=True,
                    )

    with db_tab_decans:
        st.markdown(
            f'<div style="font-size:13px;color:{_C_SUBTLE};margin-bottom:12px;font-style:italic;">'
            + auto_cn("36 Decan 護符 · 源自 Picatrix《賢者之目的》卷二第十一章")
            + "</div>",
            unsafe_allow_html=True,
        )

        # 按星座分組
        sign_filter = st.selectbox(
            auto_cn("篩選星座"),
            options=[auto_cn("全部")] + [
                d.sign_cn for d in DECAN_TALISMANS[::3]
            ],
            key="_decan_sign_filter",
        )

        for decan in DECAN_TALISMANS:
            if sign_filter != auto_cn("全部") and auto_cn(decan.sign_cn) != sign_filter:
                continue

            ruler_color = _PLANET_COLORS.get(decan.ruler, _C_GOLD)
            with st.expander(
                f"Decan {decan.decan_number} · {auto_cn(decan.sign_cn)} "
                f"{decan.degrees_start}°–{decan.degrees_end}° · {auto_cn(decan.ruler_cn)}主",
                expanded=False,
            ):
                st.markdown(
                    f'<div style="border:1px solid {ruler_color}55;border-radius:10px;'
                    f'background:{_C_CARD};padding:14px 18px;">'
                    f'<div style="font-size:14px;font-weight:700;color:{ruler_color};margin-bottom:8px;">'
                    f'{auto_cn(decan.sign_cn)} {decan.degrees_start}°–{decan.degrees_end}°'
                    f' · 第 {decan.decan_in_sign} Decan · {auto_cn(decan.ruler_cn)}主星</div>'
                    f'<div style="font-size:12px;color:{_C_TEXT};margin-bottom:8px;'
                    f'border-left:2px solid {ruler_color};padding-left:8px;">'
                    f'{auto_cn(decan.image_description_cn)}</div>'
                    f'<div style="margin-bottom:6px;">'
                    + "".join(
                        f'<span style="background:{ruler_color}22;border:1px solid {ruler_color}55;'
                        f'border-radius:12px;padding:2px 8px;font-size:11px;color:{_C_TEXT};margin:2px;">'
                        f'{auto_cn(p)}</span>'
                        for p in (decan.powers_cn or [])
                    )
                    + f'</div>'
                    f'<div style="font-size:10px;color:{_C_SUBTLE};font-style:italic;">'
                    f'🕯 {auto_cn(decan.incense_cn)} · {decan.picatrix_source}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# ============================================================
# 公開匯出函式（供 picatrix_behenian/renderer.py 呼叫）
# ============================================================

__all__ = [
    "generate_talisman_svg",
    "render_talisman_wizard",
    "render_electional_calc",
    "render_talisman_database",
]
