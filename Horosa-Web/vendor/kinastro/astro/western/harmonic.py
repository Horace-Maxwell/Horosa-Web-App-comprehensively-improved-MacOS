"""
astro/western/harmonic.py — 諧波盤 / 調和盤 (Harmonic Chart)

Implements John M. Addey's harmonic chart methodology as set forth in
"Harmonics in Astrology: An Introductory Textbook to the New Understanding
of an Old Science" (1976).

The fundamental operation is simple yet profound:
  Harmonic position = (absolute longitude × k) mod 360°

where k is the harmonic number (the number by which the circle is divided).
The resulting chart reveals the wave-pattern of the k-th cosmic rhythm,
exposing how each planet participates in that particular vibration of
Number and Cycle.

As Addey writes: "The picture that has so emerged is one of the harmonics,
that is, the rhythms and sub-rhythms of cosmic periods… which can be
demonstrated to provide the basis of all astrological doctrine both
ancient and modern."

Reference implementation: https://horoscopes.astro-seek.com/calculate-harmonic-chart
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List

import streamlit as st

from .western import (
    ZODIAC_SIGNS,
    ASPECT_TYPES,
    PLANET_COLORS,
    WesternChart,
    _normalize,
    _sign_index,
    _sign_degree,
    _format_deg,
)
from ..chart_theme import (
    CHART_BG,
    BG_LIGHT,
    CHART_GRID_LINE,
    CHART_RING_STROKE,
    CHART_TEXT_COLOR,
    TEXT_SECONDARY,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    FONT_FAMILY,
)

# ============================================================
# Number symbolism — drawn directly from Addey (1976)
# Each entry: (prime factors label, symbolism zh_trad, symbolism zh_simp, symbolism en)
# ============================================================
HARMONIC_SYMBOLISM: dict[int, dict] = {
    1: {
        "factors": "1",
        "zh": "第一諧波 — 整體圓圈本身；行星在黃道上的實際位置，一切諧波的根基。",
        "zh_cn": "第一谐波 — 整体圆圈本身；行星在黄道上的实际位置，一切谐波的根基。",
        "en": (
            "1st Harmonic — The whole circle itself; the actual positions on the zodiac. "
            "The unity from which all harmonics spring. All planets conjoin at 0°."
        ),
    },
    2: {
        "factors": "2",
        "zh": (
            "第二諧波（2） — 二分之道：圓圈被一分為二，形成對立的兩極。"
            "象徵衝突、對立、互補；傳統對沖相位（Opposition）之基礎。"
            "正負兩極交替出現，體現自然界陰陽、日夜、生死之二元律動。"
        ),
        "zh_cn": (
            "第二谐波（2） — 二分之道：圆圈被一分为二，形成对立的两极。"
            "象征冲突、对立、互补；传统对冲相位（Opposition）之基础。"
        ),
        "en": (
            "2nd Harmonic (H2) — The circle divided by 2. Two poles at 180° intervals. "
            "Symbolises opposition, polarity, and complementary duality. "
            "The wave pattern reveals which planets share the rhythm of opposition. "
            "Orb diminishes to half that of H1."
        ),
    },
    3: {
        "factors": "3",
        "zh": (
            "第三諧波（3） — 三分之道：圓圈被三等分，形成三個正極（120°間距）。"
            "象徵表達、心智活動、溝通；傳統三合相位（Trine）之波動根源。"
            "畢達哥拉斯視「三」為完成之數，天地人三才之象。"
        ),
        "zh_cn": (
            "第三谐波（3） — 三分之道：圆圈被三等分，形成三个正极（120°间距）。"
            "象征表达、心智活动、沟通；传统三合相位（Trine）之波动根源。"
        ),
        "en": (
            "3rd Harmonic (H3) — The circle divided by 3. Three poles at 120° intervals. "
            "Symbolises expression, communication, and mental activity. "
            "Pythagorean triad: the number of completion. "
            "Planets conjunct in H3 share the rhythm of the trine."
        ),
    },
    4: {
        "factors": "2²",
        "zh": (
            "第四諧波（4＝2²） — 四分之道：兩次二分，形成四個正極（90°間距）。"
            "象徵行動力、意志、物質顯化與挑戰；傳統刑相位（Square）之基礎。"
            "Addey 研究中，職業軍人群體的第四諧波呈現顯著的火星集群。"
        ),
        "zh_cn": (
            "第四谐波（4＝2²） — 四分之道：两次二分，形成四个正极（90°间距）。"
            "象征行动力、意志、物质显化与挑战；传统刑相位（Square）之基础。"
            "Addey研究中，职业军人群体的第四谐波呈现显著的火星集群。"
        ),
        "en": (
            "4th Harmonic (H4 = 2²) — Circle divided by 4. Four poles at 90° intervals. "
            "Symbolises action, will, material manifestation, and challenge. "
            "Basis of the square aspect. "
            "Addey's research on military men revealed notable Mars clusters in H4."
        ),
    },
    5: {
        "factors": "5",
        "zh": (
            "第五諧波（5） — 五分之道：圓圈被五等分，形成五個正極（72°間距）。"
            "象徵創造力、藝術、智識的精粹與靈感；五芒星之數。"
            "柏拉圖《蒂邁歐篇》中五正多面體的原型能量。"
        ),
        "zh_cn": (
            "第五谐波（5） — 五分之道：圆圈被五等分，形成五个正极（72°间距）。"
            "象征创造力、艺术、智识的精粹与灵感；五芒星之数。"
        ),
        "en": (
            "5th Harmonic (H5) — Circle divided by 5. Five poles at 72° intervals. "
            "Symbolises creativity, artistry, and intellectual inspiration. "
            "The quintile series; the number of the pentagram. "
            "Platonic resonance with the five regular solids."
        ),
    },
    6: {
        "factors": "2×3",
        "zh": (
            "第六諧波（6＝2×3） — 六分之道：兩、三之積，形成六個正極（60°間距）。"
            "象徵和諧、合作、服務；傳統六合相位（Sextile）之波動基礎。"
            "六邊形之象，天地之間和平共處之節奏。"
        ),
        "zh_cn": (
            "第六谐波（6＝2×3） — 六分之道：两、三之积，形成六个正极（60°间距）。"
            "象征和谐、合作、服务；传统六合相位（Sextile）之波动基础。"
        ),
        "en": (
            "6th Harmonic (H6 = 2×3) — Circle divided by 6. Six poles at 60° intervals. "
            "Product of 2 (polarity) and 3 (expression). "
            "Symbolises harmony, cooperation, and service. Basis of the sextile."
        ),
    },
    7: {
        "factors": "7",
        "zh": (
            "第七諧波（7） — 七分之道：圓圈被七等分，形成七個正極（約51.4°間距）。"
            "七是神聖之數（七曜）；象徵靈性洞見、命運業力、隱藏之循環。"
            "Addey 認為第七諧波與精神層面的啟示及業力緣份相關。"
        ),
        "zh_cn": (
            "第七谐波（7） — 七分之道：圆圈被七等分，形成七个正极（约51.4°间距）。"
            "七是神圣之数（七曜）；象征灵性洞见、命运业力、隐藏之循环。"
        ),
        "en": (
            "7th Harmonic (H7) — Circle divided by 7. Seven poles at ~51.4° intervals. "
            "The sacred number of the seven planets; symbolises spiritual insight, "
            "karmic patterns, and hidden cycles. "
            "Addey associated H7 with inspiration and the inspirational artist."
        ),
    },
    8: {
        "factors": "2³",
        "zh": (
            "第八諧波（8＝2³） — 三次二分，形成八個正極（45°間距）。"
            "象徵再生、轉化、深層意志與危機中的力量。"
            "半刑（45°，Semisquare）及倍半刑（135°，Sesquisquare）之基礎。"
        ),
        "zh_cn": (
            "第八谐波（8＝2³） — 三次二分，形成八个正极（45°间距）。"
            "象征再生、转化、深层意志与危机中的力量。"
        ),
        "en": (
            "8th Harmonic (H8 = 2³) — Circle divided by 8. Eight poles at 45° intervals. "
            "Threefold division by 2; symbolises transformation, regeneration, and "
            "deep-seated will. Basis of the semisquare (45°) and sesquisquare (135°)."
        ),
    },
    9: {
        "factors": "3²",
        "zh": (
            "第九諧波（9＝3²） — 三之自乘，形成九個正極（40°間距）。"
            "象徵智慧的圓滿、哲學洞察與精神整合；"
            "諾文星（Novile, 40°）系列之基礎。"
            "在道家思想中，九為極陽之數，天道之象徵。"
        ),
        "zh_cn": (
            "第九谐波（9＝3²） — 三之自乘，形成九个正极（40°间距）。"
            "象征智慧的圆满、哲学洞察与精神整合。"
        ),
        "en": (
            "9th Harmonic (H9 = 3²) — Circle divided by 9. Nine poles at 40° intervals. "
            "The square of three; symbolises the completion of wisdom, philosophical "
            "insight, and spiritual integration. Basis of the novile (40°) series."
        ),
    },
    10: {
        "factors": "2×5",
        "zh": (
            "第十諧波（10＝2×5） — 二與五之積，形成十個正極（36°間距）。"
            "象徵人性的圓滿（十誡、十全十美）；"
            "畢達哥拉斯四面體之10點完整性。"
        ),
        "zh_cn": (
            "第十谐波（10＝2×5） — 二与五之积，形成十个正极（36°间距）。"
            "象征人性的圆满；毕达哥拉斯四面体之10点完整性。"
        ),
        "en": (
            "10th Harmonic (H10 = 2×5) — Circle divided by 10. Ten poles at 36° intervals. "
            "Product of duality (2) and creativity (5). "
            "Symbolises human perfection and the Pythagorean tetractys."
        ),
    },
    11: {
        "factors": "11",
        "zh": (
            "第十一諧波（11） — 十一等分（約32.7°間距）。"
            "11是超越十（人之完滿）的靈性躍升，象徵預知、洞察未來與宇宙靈感。"
        ),
        "zh_cn": (
            "第十一谐波（11） — 十一等分（约32.7°间距）。"
            "象征超越完满之灵性跃升、预知与宇宙灵感。"
        ),
        "en": (
            "11th Harmonic (H11) — Circle divided by 11. ~32.7° intervals. "
            "Beyond the perfection of 10; symbolises transcendence, prophetic insight, "
            "and cosmic inspiration."
        ),
    },
    12: {
        "factors": "2²×3",
        "zh": (
            "第十二諧波（12＝2²×3） — 最重要的複合諧波之一。"
            "象徵隱藏之苦難、服務、奉獻，以及超越形式的解脫。"
            "Addey 著名研究：醫師群體的第十二諧波呈現顯著的太陽與土星集群。"
            "十二宮十二星座之完整週期在此諧波中一覽無遺。"
        ),
        "zh_cn": (
            "第十二谐波（12＝2²×3） — 最重要的复合谐波之一。"
            "象征隐藏之苦难、服务、奉献，以及超越形式的解脱。"
            "Addey著名研究：医师群体的第十二谐波呈现显著的太阳与土星集群。"
        ),
        "en": (
            "12th Harmonic (H12 = 2²×3) — One of the most significant compound harmonics. "
            "Symbolises hidden suffering, service, sacrifice, and transcendence. "
            "Addey's landmark research: physicians showed a remarkable cluster of Sun "
            "and Saturn in H12, validating the wave-theory of astrological effects."
        ),
    },
}


def _prime_factors(n: int) -> List[int]:
    """Return prime factors of n (with repetition)."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def _factor_meaning(factors: List[int], lang: str) -> str:
    """Build a brief string summarising the meaning of prime factors."""
    _MEANINGS = {
        2: {"zh": "對立/陰陽", "zh_cn": "对立/阴阳", "en": "polarity/duality"},
        3: {"zh": "表達/溝通", "zh_cn": "表达/沟通", "en": "expression/communication"},
        5: {"zh": "創造/靈感", "zh_cn": "创造/灵感", "en": "creativity/inspiration"},
        7: {"zh": "靈性/業力", "zh_cn": "灵性/业力", "en": "spirit/karma"},
        11: {"zh": "先知/超越", "zh_cn": "先知/超越", "en": "prophecy/transcendence"},
        13: {"zh": "變革/更新", "zh_cn": "变革/更新", "en": "transformation/renewal"},
    }
    parts = []
    for f in sorted(set(factors)):
        m = _MEANINGS.get(f, {})
        parts.append(m.get(lang, m.get("en", str(f))))
    return " × ".join(parts) if parts else "—"


def get_harmonic_symbolism(k: int, lang: str = "zh") -> str:
    """Return Addey-style number symbolism for harmonic k in the given language."""
    if k in HARMONIC_SYMBOLISM:
        entry = HARMONIC_SYMBOLISM[k]
        return entry.get(lang, entry.get("en", ""))
    # Fallback: build a description from prime factors
    factors = _prime_factors(k)
    factors_str = "×".join(str(f) for f in factors)
    interval = 360.0 / k
    factor_meaning = _factor_meaning(factors, lang)
    if lang in ("zh", "zh_cn"):
        return (
            f"第{k}諧波（{factors_str}） — "
            f"以{k}等分黃道，每 {interval:.1f}° 一個正極。"
            f"素因子象徵：{factor_meaning}。"
        )
    return (
        f"{k}th Harmonic ({factors_str}) — "
        f"Circle divided by {k}; {k} poles at {interval:.1f}° intervals. "
        f"Prime factors symbolism: {factor_meaning}."
    )


# ============================================================
# Data Classes
# ============================================================

@dataclass
class HarmonicPlanet:
    """行星在諧波盤中的位置"""
    name: str
    natal_longitude: float      # 本命黃道經度
    harmonic_longitude: float   # 諧波盤經度
    sign: str
    sign_glyph: str
    sign_chinese: str
    sign_degree: float
    element: str
    retrograde: bool
    house: int = 0


@dataclass
class HarmonicAspect:
    """諧波盤相位（合相為主）"""
    planet1: str
    planet2: str
    orb: float                  # 合相分離度（°）
    aspect_type: str = "Conjunction"
    aspect_symbol: str = "☌"


@dataclass
class HarmonicChart:
    """諧波盤完整資料"""
    harmonic_number: int
    natal_chart: WesternChart
    planets: List[HarmonicPlanet] = field(default_factory=list)
    aspects: List[HarmonicAspect] = field(default_factory=list)
    ascendant: float = 0.0
    midheaven: float = 0.0


# ============================================================
# Calculation
# ============================================================

def _harmonic_longitude(natal_lon: float, k: int) -> float:
    """Apply Addey's harmonic transformation: (lon × k) mod 360."""
    return (natal_lon * k) % 360.0


def _harmonic_orb(k: int) -> float:
    """
    Orb for the harmonic conjunction diminishes in direct proportion to k.
    Base orb of 1° per harmonic is a practical approximation used in the
    tradition deriving from Addey's work.
    """
    # Base orb for H1 conjunction ~8°; reduce proportionally
    return max(0.5, 8.0 / k)


def _find_harmonic_aspects(planets: List[HarmonicPlanet], k: int) -> List[HarmonicAspect]:
    """
    Find conjunctions in the harmonic chart.
    In Addey's system, all traditional aspects in the natal chart become
    conjunctions in the appropriate harmonic chart.  Here we detect
    any pair whose harmonic longitudes are within the harmonic orb.
    """
    orb_limit = _harmonic_orb(k)
    aspects = []
    n = len(planets)
    for i in range(n):
        for j in range(i + 1, n):
            diff = abs(planets[i].harmonic_longitude - planets[j].harmonic_longitude)
            if diff > 180:
                diff = 360 - diff
            if diff <= orb_limit:
                aspects.append(HarmonicAspect(
                    planet1=planets[i].name,
                    planet2=planets[j].name,
                    orb=round(diff, 2),
                ))
    aspects.sort(key=lambda a: a.orb)
    return aspects


@st.cache_data(ttl=3600, show_spinner=False)
def compute_harmonic_chart(
    natal_longitudes: tuple,   # tuple of (name, lon, lat, retrograde) — hashable for cache
    natal_ascendant: float,
    natal_midheaven: float,
    k: int,
) -> HarmonicChart:
    """
    Compute the k-th harmonic chart.

    Following Addey (1976): for each planet with absolute longitude L,
    the harmonic position is (L × k) mod 360°.
    The same transformation is applied to the Ascendant and Midheaven.

    Args:
        natal_longitudes: tuple of (name, lon, lat, retrograde, house) tuples
        natal_ascendant: natal Ascendant longitude
        natal_midheaven: natal Midheaven longitude
        k: harmonic number (positive integer ≥ 1)
    """
    if k < 1:
        k = 1

    h_planets = []
    for item in natal_longitudes:
        name, lon, lat, retrograde, house = item
        h_lon = _harmonic_longitude(lon, k)
        idx = _sign_index(h_lon)
        sign_info = ZODIAC_SIGNS[idx]
        h_planets.append(HarmonicPlanet(
            name=name,
            natal_longitude=lon,
            harmonic_longitude=h_lon,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            sign_chinese=sign_info[2],
            sign_degree=_sign_degree(h_lon),
            element=sign_info[3],
            retrograde=retrograde,
            house=house,
        ))

    aspects = _find_harmonic_aspects(h_planets, k)

    h_asc = _harmonic_longitude(natal_ascendant, k)
    h_mc = _harmonic_longitude(natal_midheaven, k)

    # We pass None for natal_chart here to avoid caching issues;
    # caller should attach natal_chart reference separately.
    chart = HarmonicChart(
        harmonic_number=k,
        natal_chart=None,   # type: ignore[arg-type]
        planets=h_planets,
        aspects=aspects,
        ascendant=h_asc,
        midheaven=h_mc,
    )
    return chart


# ============================================================
# Rendering
# ============================================================

def _esc(text: str) -> str:
    """Escape special XML characters for SVG text."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )


def _render_harmonic_wheel(hchart: HarmonicChart):
    """
    Render the harmonic wheel using a 4×4 grid SVG,
    mirroring the natal wheel layout in western.py.
    """
    k = hchart.harmonic_number

    # Map planets to harmonic houses (which sign they land in divides to house-like cells)
    # For simplicity we use the harmonic Ascendant as 1st-house cusp,
    # spacing 30° per harmonic "sign" cell.
    h_asc = hchart.ascendant

    # Build house cusps for harmonic wheel (equal houses from H-ASC)
    h_cusps = [_normalize(h_asc + i * 30.0) for i in range(12)]

    def _find_h_house(lon: float) -> int:
        lon = _normalize(lon)
        for i in range(12):
            start = h_cusps[i]
            end = h_cusps[(i + 1) % 12]
            if start < end:
                if start <= lon < end:
                    return i + 1
            else:
                if lon >= start or lon < end:
                    return i + 1
        return 1

    # Assign harmonic houses
    house_planets: dict[int, list] = {i: [] for i in range(1, 13)}
    for p in hchart.planets:
        h = _find_h_house(p.harmonic_longitude)
        house_planets[h].append(p)

    # SVG dimensions (same grid as natal wheel)
    W = 560
    CAP_H = 50
    CW = W / 4
    CH = 110
    H_SVG = CAP_H + CH * 4

    wheel_grid = [
        [10, 11, 12, 1],
        [9, -1, -1, 2],
        [8, -1, -1, 3],
        [7, 6, 5, 4],
    ]

    asc_sign_idx = _sign_index(h_asc)
    asc_sign_info = ZODIAC_SIGNS[asc_sign_idx]
    mc_sign_idx = _sign_index(hchart.midheaven)
    mc_sign_info = ZODIAC_SIGNS[mc_sign_idx]

    # Theme-derived colour aliases for readability
    _bg = CHART_BG                    # "#0F172A" deep indigo background
    _cell_bg = BG_LIGHT               # "#1e1b4b" regular house cells
    _asc_bg = "#251c00"               # warm dark gold tint for ASC cell
    _mc_bg = "#160d30"                # cool dark purple tint for MC cell
    _center_bg = CHART_BG             # same as overall background
    _stroke = CHART_GRID_LINE         # "#2a2a5a"
    _ring_stroke = CHART_RING_STROKE  # "#5a5a9a"
    _text = CHART_TEXT_COLOR          # "#e0e0ff"
    _text2 = TEXT_SECONDARY           # "#b0b0d0"
    _text_muted = "#7070a0"
    _gold = SECONDARY_COLOR           # "#EAB308"
    _purple = PRIMARY_COLOR           # "#a78bfa"
    _font = FONT_FAMILY

    parts: list[str] = []
    parts.append(
        f'<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'class="chart-wheel" '
        f'viewBox="0 0 {W} {H_SVG}" '
        f'style="width:100%;max-width:{W}px;display:block;margin:auto;'
        f'background:{_bg};border-radius:12px;'
        f'border:1px solid rgba(167,139,250,0.15);'
        f'font-family:{_font};">'
    )

    # Title
    parts.append(
        f'<text x="{W / 2}" y="18" text-anchor="middle" '
        f'fill="{_text}" font-size="14" font-weight="bold">'
        f'H{k} Harmonic Wheel — {k}th Harmonic (諧波盤)</text>'
    )
    parts.append(
        f'<text x="{W / 2}" y="36" text-anchor="middle" '
        f'fill="{_text2}" font-size="11">'
        f'▲ H-ASC {_esc(asc_sign_info[1])}{_esc(asc_sign_info[0])} '
        f'{_sign_degree(h_asc):.1f}°'
        f'  ⬡ H-MC {_esc(mc_sign_info[1])}{_esc(mc_sign_info[0])} '
        f'{_sign_degree(hchart.midheaven):.1f}°'
        f'</text>'
    )

    center_rendered = False
    for row_i, row_data in enumerate(wheel_grid):
        for col_i, house_num in enumerate(row_data):
            x = col_i * CW
            y = CAP_H + row_i * CH
            cx = x + CW / 2

            if house_num == -1:
                if center_rendered:
                    continue
                center_rendered = True
                mx = 1 * CW
                my = CAP_H + 1 * CH
                mw = CW * 2
                mh = CH * 2
                mcx = mx + mw / 2
                mcy = my + mh / 2

                parts.append(
                    f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" '
                    f'fill="{_center_bg}" stroke="{_ring_stroke}" stroke-width="1" rx="4"/>'
                )
                parts.append(
                    f'<text x="{mcx}" y="{mcy - 20}" text-anchor="middle" '
                    f'fill="{_gold}" font-size="28" font-weight="bold">H{k}</text>'
                )
                parts.append(
                    f'<text x="{mcx}" y="{mcy + 8}" text-anchor="middle" '
                    f'fill="{_text2}" font-size="11">Harmonic {k}</text>'
                )
                parts.append(
                    f'<text x="{mcx}" y="{mcy + 26}" text-anchor="middle" '
                    f'fill="{_text_muted}" font-size="10">360° ÷ {k} = {360/k:.2f}°/pole</text>'
                )
                continue

            cusp_lon = h_cusps[house_num - 1]
            sign_idx = _sign_index(cusp_lon)
            sign_info = ZODIAC_SIGNS[sign_idx]
            is_asc = house_num == 1
            is_mc = house_num == 10
            fill = _asc_bg if is_asc else (_mc_bg if is_mc else _cell_bg)

            parts.append(
                f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" '
                f'fill="{fill}" stroke="{_stroke}" stroke-width="1" rx="2"/>'
            )

            marker = " ▲" if is_asc else (" ⬡" if is_mc else "")
            marker_color = _gold if is_asc else (_purple if is_mc else _text)
            parts.append(
                f'<text x="{cx}" y="{y + 18}" text-anchor="middle" '
                f'fill="{marker_color}" font-size="13" font-weight="bold">'
                f'{house_num}{_esc(marker)}</text>'
            )
            parts.append(
                f'<text x="{cx}" y="{y + 34}" text-anchor="middle" '
                f'fill="{_text}" font-size="11">'
                f'{_esc(sign_info[1])} {_esc(sign_info[0])}</text>'
            )
            parts.append(
                f'<text x="{cx}" y="{y + 48}" text-anchor="middle" '
                f'fill="{_text2}" font-size="10">{_esc(_format_deg(cusp_lon))}</text>'
            )

            planets_in_house = house_planets.get(house_num, [])
            if planets_in_house:
                n_p = len(planets_in_house)
                font_sz = 11 if n_p <= 2 else (10 if n_p <= 3 else 9)
                per_row = min(n_p, 3)
                p_spacing = 44
                p_base_y = 66
                p_row_h = 16
                for pi, planet in enumerate(planets_in_house):
                    short = planet.name.split(" ")[0]
                    row_idx = pi // per_row
                    col_idx = pi % per_row
                    row_count = min(per_row, n_p - row_idx * per_row)
                    px = cx + (col_idx - (row_count - 1) / 2) * p_spacing
                    py = y + p_base_y + row_idx * p_row_h
                    color = PLANET_COLORS.get(planet.name, _text2)
                    parts.append(
                        f'<text x="{px}" y="{py}" text-anchor="middle" '
                        f'fill="{color}" font-size="{font_sz}" '
                        f'font-weight="bold">{_esc(short)}</text>'
                    )
            else:
                parts.append(
                    f'<text x="{cx}" y="{y + 68}" text-anchor="middle" '
                    f'fill="{_text_muted}" font-size="11">—</text>'
                )

    parts.append("</svg></div>")
    st.markdown("".join(parts), unsafe_allow_html=True)
    st.caption("▲ = H-ASC (Harmonic Ascendant)   ⬡ = H-MC (Harmonic Midheaven)")


def _render_harmonic_planet_table(hchart: HarmonicChart, lang: str = "zh"):
    """Render planet positions table for the harmonic chart."""
    if lang == "en":
        st.subheader(f"🪐 H{hchart.harmonic_number} Planet Positions")
    else:
        st.subheader(f"🪐 第{hchart.harmonic_number}諧波行星位置")

    header = (
        "| Planet / 行星 | Natal Lon. / 本命經度 "
        "| H{k} Lon. / 諧波經度 | Sign / 星座 | Degree / 度數 |"
    ).replace("{k}", str(hchart.harmonic_number))
    sep = "|:------:|:-------:|:-------:|:----:|:------:|"
    rows = [header, sep]
    for p in hchart.planets:
        retro = " ℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        rows.append(
            f"| {name_html}{retro} "
            f"| {p.natal_longitude:.3f}° "
            f"| **{p.harmonic_longitude:.3f}°** "
            f"| {p.sign_glyph} {p.sign} ({p.sign_chinese}) "
            f"| {p.sign_degree:.2f}° |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_harmonic_aspects(hchart: HarmonicChart, lang: str = "zh"):
    """Render harmonic conjunctions (planets clustered in the harmonic chart)."""
    k = hchart.harmonic_number
    orb = _harmonic_orb(k)

    if lang == "en":
        st.subheader(f"🔗 H{k} Conjunctions (Orb ≤ {orb:.1f}°)")
        st.caption(
            "In Addey's system, planets conjunct in the harmonic chart share "
            "the wave-rhythm of that harmonic number. Tight orbs indicate "
            "strong participation in this cosmic cycle."
        )
    else:
        st.subheader(f"🔗 第{k}諧波合相（容許度 ≤ {orb:.1f}°）")
        st.caption(
            "在Addey（1976）諧波理論中，諧波盤中的合相代表兩顆行星共振於"
            f"第{k}宇宙波動節律。緊密的合相揭示強烈的諧波共鳴。"
        )

    if not hchart.aspects:
        if lang == "en":
            st.info(f"No conjunctions found within the H{k} orb ({orb:.1f}°).")
        else:
            st.info(f"在第{k}諧波容許度（{orb:.1f}°）內未發現合相。")
        return

    header = "| Planet 1 | ☌ | Planet 2 | Orb |"
    sep = "|:--------:|:-:|:--------:|:---:|"
    rows = [header, sep]
    for a in hchart.aspects:
        rows.append(
            f"| {a.planet1} | ☌ | {a.planet2} | {a.orb:.2f}° |"
        )
    st.markdown("\n".join(rows))


def _render_harmonic_formula(hchart: HarmonicChart, lang: str = "zh"):
    """Show the transformation formula and a worked example."""
    k = hchart.harmonic_number
    if hchart.planets:
        example = hchart.planets[0]
        ex_name = example.name
        ex_natal = example.natal_longitude
        ex_harm = example.harmonic_longitude
    else:
        ex_name = "Sun ☉"
        ex_natal = 0.0
        ex_harm = 0.0

    if lang == "en":
        st.markdown(
            f"**Addey's Harmonic Formula** (from *Harmonics in Astrology*, 1976):\n\n"
            f"$$H_{{k}}(L) = (L \\times k) \\bmod 360°$$\n\n"
            f"**Example** — {ex_name}:\n"
            f"- Natal longitude: **{ex_natal:.3f}°**\n"
            f"- H{k}: $({ex_natal:.3f}° \\times {k}) \\bmod 360° = "
            f"\\mathbf{{{ex_harm:.3f}°}}$\n\n"
            f"Orb for H{k} conjunctions: **≤ {_harmonic_orb(k):.1f}°** "
            f"(diminishes in direct proportion to k)."
        )
    else:
        st.markdown(
            f"**Addey諧波轉換公式**（出自《Harmonics in Astrology》1976年）：\n\n"
            f"$$H_{{k}}(L) = (L \\times k) \\bmod 360°$$\n\n"
            f"**示例** — {ex_name}：\n"
            f"- 本命黃道經度：**{ex_natal:.3f}°**\n"
            f"- 第{k}諧波：$({ex_natal:.3f}° \\times {k}) \\bmod 360° = "
            f"\\mathbf{{{ex_harm:.3f}°}}$\n\n"
            f"第{k}諧波合相容許度：**≤ {_harmonic_orb(k):.1f}°**"
            f"（容許度與諧波數成反比）。"
        )


def render_harmonic_chart(natal_chart: WesternChart, lang: str = "zh"):
    """
    Full Streamlit rendering of the harmonic chart feature,
    embodying Addey's 1976 methodology.

    Args:
        natal_chart: The natal WesternChart to derive harmonics from.
        lang: UI language ('zh', 'zh_cn', 'en').
    """
    # k is determined by the UI selector below

    # ── 1. Harmonic number selector ──────────────────────────────────────────
    if lang == "en":
        st.markdown(
            "### \u267e\ufe0f Harmonic Chart \u2014 Addey (1976)\n\n"
            "> *\u201cThe picture that has so emerged is one of the harmonics, that is, "
            "the rhythms and sub-rhythms of cosmic periods\u2026 which can be demonstrated "
            "to provide the basis of all astrological doctrine both ancient and modern.\u201d*\n\n"
            "Select a harmonic number **k** to transform all planetary longitudes "
            "via the Addey formula: **(L \xd7 k) mod 360\xb0**."
        )
    elif lang == "zh_cn":
        st.markdown(
            "### \u267e\ufe0f \u8c10\u6ce2\u76d8 \u2014 Addey\uff081976\uff09\n\n"
            "> *\u201c\u6240\u5c55\u73b0\u7684\u56fe\u666f\u6b63\u662f\u8c10\u6ce2"
            "\u2014\u2014\u5373\u5b87\u5b99\u5468\u671f\u7684\u8282\u5f8b\u4e0e\u5b50\u8282\u5f8b\u2026\u2026"
            "\u53ef\u4ee5\u8bc1\u660e\uff0c\u8fd9\u4e3a\u53e4\u4eca\u4e00\u5207\u5360\u661f\u5b66\u8bf4\u63d0\u4f9b\u4e86\u57fa\u7840\u3002\u201d*\n\n"
            "\u9009\u62e9\u8c10\u6ce2\u6570 **k**\uff0c\u4ee5Addey\u516c\u5f0f\u53d8\u6362\u6240\u6709\u884c\u661f\u7ecf\u5ea6\uff1a**(L \xd7 k) mod 360\xb0**\u3002"
        )
    else:
        st.markdown(
            "### \u267e\ufe0f \u8ae7\u6ce2\u76e4 \u2014 Addey\uff081976\uff09\n\n"
            "> *\u300c\u6240\u547c\u73fe\u7684\u5716\u666f\u6b63\u662f\u8ae7\u6ce2"
            "\u2014\u2014\u5373\u5b87\u5b99\u9031\u671f\u7684\u7bc0\u5f8b\u8207\u5b50\u7bc0\u5f8b\u2026\u2026"
            "\u53ef\u4ee5\u8b49\u660e\uff0c\u9019\u70ba\u53e4\u4eca\u4e00\u5207\u5360\u661f\u5b78\u8aaa\u63d0\u4f9b\u4e86\u57fa\u790e\u3002\u300d*\n\n"
            "\u9078\u64c7\u8ae7\u6ce2\u6578 **k**\uff0c\u4ee5Addey\u516c\u5f0f\u8b8a\u63db\u6240\u6709\u884c\u661f\u9ec3\u9053\u7d93\u5ea6\uff1a**(L \xd7 k) mod 360\xb0**\u3002"
        )

    col_k, col_preset = st.columns([1, 2])
    with col_k:
        k = st.number_input(
            "Harmonic k" if lang == "en" else "諧波數 k",
            min_value=1, max_value=36, value=4, step=1,
            key="harmonic_k",
            help=(
                "Enter harmonic number (1–36). "
                "Notable: H4=action/square, H5=creativity, H7=spirit, H12=physicians/service."
            ) if lang == "en" else (
                "輸入諧波數（1–36）。"
                "重要諧波：H4=行動力/刑, H5=創造力, H7=靈性, H12=醫師/服務。"
            ),
        )
    with col_preset:
        _presets = {
            "H1 — 本命 Natal": 1,
            "H2 — 對立 Opposition": 2,
            "H3 — 三合 Trine": 3,
            "H4 — 刑合 Square (軍人)": 4,
            "H5 — 創造 Creativity": 5,
            "H7 — 靈感 Inspiration": 7,
            "H9 — 智慧 Wisdom": 9,
            "H12 — 醫師 Physicians": 12,
        }
        _preset_label = (
            "Quick Select / 快速選擇" if lang == "en" else "快速選擇常用諧波"
        )
        _chosen = st.selectbox(
            _preset_label,
            options=list(_presets.keys()),
            key="harmonic_preset",
        )
        if st.button("Apply / 套用" if lang == "en" else "套用", key="harmonic_apply"):
            k = _presets[_chosen]
            st.session_state["harmonic_k"] = k
            st.rerun()

    k = int(k)

    # ── 2. Number symbolism ───────────────────────────────────────────────────
    symbolism_lang = "en" if lang == "en" else ("zh_cn" if lang == "zh_cn" else "zh")
    symbolism_text = get_harmonic_symbolism(k, symbolism_lang)
    if lang == "en":
        with st.expander(f"📖 Number Symbolism of H{k} (Addey 1976)", expanded=True):
            st.info(symbolism_text)
    else:
        with st.expander(f"📖 第{k}諧波的數字象徵（Addey 1976）", expanded=True):
            st.info(symbolism_text)

    # ── 3. Compute harmonic chart ─────────────────────────────────────────────
    # Package natal longitudes as a hashable tuple for caching
    _natal_tuple = tuple(
        (p.name, p.longitude, p.latitude, p.retrograde, p.house)
        for p in natal_chart.planets
    )

    hchart = compute_harmonic_chart(
        natal_longitudes=_natal_tuple,
        natal_ascendant=natal_chart.ascendant,
        natal_midheaven=natal_chart.midheaven,
        k=k,
    )
    hchart.natal_chart = natal_chart

    # ── 4. Wheel ──────────────────────────────────────────────────────────────
    _render_harmonic_wheel(hchart)

    st.divider()

    # ── 5. Formula ────────────────────────────────────────────────────────────
    if lang == "en":
        with st.expander("🧮 Transformation Formula", expanded=False):
            _render_harmonic_formula(hchart, lang)
    else:
        with st.expander("🧮 轉換公式", expanded=False):
            _render_harmonic_formula(hchart, lang)

    st.divider()

    # ── 6. Planet positions ───────────────────────────────────────────────────
    _render_harmonic_planet_table(hchart, lang)

    st.divider()

    # ── 7. Aspects (conjunctions) ─────────────────────────────────────────────
    _render_harmonic_aspects(hchart, lang)

    st.divider()

    # ── 8. Addey wave-theory interpretation ──────────────────────────────────
    factors = _prime_factors(k)
    factors_str = "×".join(str(f) for f in factors)
    interval = 360.0 / k

    if lang == "en":
        st.subheader(f"🌊 Wave Theory Analysis — H{k}")
        st.markdown(
            f"**Following the method set forth in *Harmonics in Astrology* (Addey, 1976):**\n\n"
            f"The {k}th harmonic divides the zodiac circle into **{k} equal arcs** "
            f"of **{interval:.2f}°** each, producing {k} positive poles "
            f"(peak phases) and {k} negative poles (trough phases) "
            f"at equidistant intervals around the circle.\n\n"
            f"**Prime factors:** {factors_str} → {_factor_meaning(factors, 'en')}\n\n"
            f"As shown in the study of harmonics, when two or more planets are "
            f"conjunct in the H{k} chart (within the {_harmonic_orb(k):.1f}° orb), "
            f"they participate together in the same phase of the {k}th cosmic rhythm. "
            f"This is the astrological meaning of the {k}th harmonic: "
            f"the characteristic vibration of Number {k} expresses itself "
            f"through those planetary combinations."
        )
        if hchart.aspects:
            st.markdown("**Key harmonic configurations in this chart:**")
            for asp in hchart.aspects[:8]:
                st.markdown(
                    f"- **{asp.planet1} ☌ {asp.planet2}** "
                    f"(orb {asp.orb:.2f}°) — "
                    f"these planets share the H{k} rhythm; "
                    f"their themes blend in the domain of {_factor_meaning(factors, 'en')}."
                )
    elif lang == "zh_cn":
        st.subheader(f"🌊 波动理论分析 — 第{k}谐波")
        st.markdown(
            f"**遵循《Harmonics in Astrology》（Addey, 1976）所阐述的方法：**\n\n"
            f"第{k}谐波将黄道圆圈等分为 **{k} 段**，每段 **{interval:.2f}°**，"
            f"形成{k}个正极（波峰相位）与{k}个负极（波谷相位），均匀分布于圆圈之上。\n\n"
            f"**素因子：** {factors_str} → {_factor_meaning(factors, 'zh_cn')}\n\n"
            f"如谐波研究所示，当两颗或多颗行星在第{k}谐波盘中形成合相"
            f"（容许度 {_harmonic_orb(k):.1f}°以内），"
            f"它们共同参与第{k}宇宙节律的同一相位，"
            f"体现了数字{k}的特征振动。"
        )
        if hchart.aspects:
            st.markdown(f"**本盘关键谐波合相：**")
            for asp in hchart.aspects[:8]:
                st.markdown(
                    f"- **{asp.planet1} ☌ {asp.planet2}** "
                    f"（容差 {asp.orb:.2f}°）— "
                    f"两星共振于第{k}节律，主题交融于{_factor_meaning(factors, 'zh_cn')}之域。"
                )
    else:
        st.subheader(f"🌊 波動理論分析 — 第{k}諧波")
        st.markdown(
            f"**遵循《Harmonics in Astrology》（Addey, 1976）所闡述的方法：**\n\n"
            f"第{k}諧波將黃道圓圈等分為 **{k} 段**，每段 **{interval:.2f}°**，"
            f"形成{k}個正極（波峰相位）與{k}個負極（波谷相位），均勻分布於圓圈之上。\n\n"
            f"**素因子：** {factors_str} → {_factor_meaning(factors, 'zh')}\n\n"
            f"如諧波研究所示，當兩顆或多顆行星在第{k}諧波盤中形成合相"
            f"（容許度 {_harmonic_orb(k):.1f}°以內），"
            f"它們共同參與第{k}宇宙節律的同一相位，"
            f"體現了數字{k}的特徵振動。\n\n"
            f"在柏拉圖《蒂邁歐篇》的傳統中，圓圈是永恆依數流動的映象；"
            f"數字的象徵性在此諧波圓圈中得以展開。"
        )
        if hchart.aspects:
            st.markdown(f"**本盤關鍵諧波合相：**")
            for asp in hchart.aspects[:8]:
                st.markdown(
                    f"- **{asp.planet1} ☌ {asp.planet2}** "
                    f"（容差 {asp.orb:.2f}°）— "
                    f"兩星共振於第{k}節律，主題交融於{_factor_meaning(factors, 'zh')}之域。"
                )

    st.divider()

    # ── 9. Addey research notes ───────────────────────────────────────────────
    _render_addey_research_note(k, lang)


def _render_addey_research_note(k: int, lang: str):
    """Render Addey's specific research findings when relevant to k."""
    notes = {
        4: {
            "zh": (
                "📚 **Addey研究筆記（H4）：** 在《Harmonics in Astrology》（1976）中，"
                "Addey引用了職業軍人群體的統計研究，發現其第四諧波盤中火星（Mars）"
                "呈現顯著的集群現象，印證了H4作為「行動力、意志與物質挑戰」之象徵。"
            ),
            "zh_cn": (
                "📚 **Addey研究笔记（H4）：** 在《Harmonics in Astrology》（1976）中，"
                "Addey引用了职业军人群体的统计研究，发现其第四谐波盘中火星（Mars）"
                "呈现显著的集群现象，印证了H4作为「行动力、意志与物质挑战」之象征。"
            ),
            "en": (
                "📚 **Addey Research Note (H4):** In *Harmonics in Astrology* (1976), "
                "Addey cites statistical studies of professional military men, finding "
                "a significant cluster of Mars in the H4 chart, confirming H4's "
                "symbolism of action, will, and material challenge."
            ),
        },
        12: {
            "zh": (
                "📚 **Addey研究筆記（H12）：** 《Harmonics in Astrology》（1976）最著名的"
                "實證研究之一：醫師群體的第十二諧波盤中，太陽（Sun）與土星（Saturn）"
                "呈現統計上顯著的集群，揭示H12「服務、犧牲、超越苦難」的深層含義。"
                "此研究直接支持了諧波理論的科學有效性。"
            ),
            "zh_cn": (
                "📚 **Addey研究笔记（H12）：** 《Harmonics in Astrology》（1976）最著名的"
                "实证研究之一：医师群体的第十二谐波盘中，太阳（Sun）与土星（Saturn）"
                "呈现统计上显著的集群，揭示H12「服务、牺牲、超越苦难」的深层含义。"
            ),
            "en": (
                "📚 **Addey Research Note (H12):** One of the landmark empirical studies "
                "in *Harmonics in Astrology* (1976): physicians showed a statistically "
                "significant cluster of Sun and Saturn in the H12 chart, "
                "revealing H12's deep symbolism of service, sacrifice, and transcendence. "
                "This research directly supports the scientific validity of harmonic theory."
            ),
        },
        7: {
            "zh": (
                "📚 **Addey研究筆記（H7）：** Addey將第七諧波與靈感藝術家和神秘洞察相關聯。"
                "七是七政（古典七星）之數，在《蒂邁歐篇》傳統中是靈魂下降時所穿越的七個天球。"
            ),
            "zh_cn": (
                "📚 **Addey研究笔记（H7）：** Addey将第七谐波与灵感艺术家和神秘洞察相关联。"
                "七是七政（古典七星）之数，在《蒂迈欧篇》传统中是灵魂下降时所穿越的七个天球。"
            ),
            "en": (
                "📚 **Addey Research Note (H7):** Addey associated the 7th harmonic with "
                "inspirational artists and mystical insight. Seven is the number of the "
                "seven classical planets; in the *Timaeus* tradition it represents the "
                "seven spheres through which the soul descends."
            ),
        },
        5: {
            "zh": (
                "📚 **Addey研究筆記（H5）：** 第五諧波與創造力、藝術才能和智識靈感相關聯。"
                "五倍星（Quintile, 72°）系列在古典占星中關聯天才特質與非凡能力。"
            ),
            "zh_cn": (
                "📚 **Addey研究笔记（H5）：** 第五谐波与创造力、艺术才能和智识灵感相关联。"
                "五倍星（Quintile, 72°）系列在古典占星中关联天才特质与非凡能力。"
            ),
            "en": (
                "📚 **Addey Research Note (H5):** The 5th harmonic is associated with "
                "creativity, artistic talent, and intellectual inspiration. "
                "The quintile series (72° and its multiples) has been linked in "
                "the harmonic tradition to exceptional abilities and genius."
            ),
        },
    }

    note_entry = notes.get(k)
    if note_entry:
        note_text = note_entry.get(lang, note_entry.get("en", ""))
        if note_text:
            st.markdown(note_text)
