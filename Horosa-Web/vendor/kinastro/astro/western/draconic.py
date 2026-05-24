"""
astro/western/draconic.py — 龍頭星盤 / 靈魂星盤 (Draconic Chart)

Implements the classical Draconic Chart methodology as pioneered by
Ronald C. Davison and most comprehensively developed by Rev. Pamela Crane
in her seminal works on the Draconic Chart.

The Draconic Chart is the authentic "Soul Chart" or "Higher Self Chart" —
the zodiac reoriented to the soul's evolutionary axis (the Moon's Nodes),
revealing the soul's pre-birth intention, karmic blueprint, and spiritual
mission for this incarnation.

Core Formula (Crane / Davison):
    Draconic Longitude = (Tropical Longitude − North Node Longitude) mod 360°

In every Draconic Chart:
    • The North Node is fixed at 0° Aries (Dragon's Head / 龍頭)
    • The South Node is fixed at 0° Libra (Dragon's Tail / 龍尾)
    • All planets, angles, and house cusps shift by the same arc

Reference:
    Crane, Pamela (1987). *The Draconic Chart*. Wessex Astrologer.
    Davison, Ronald C. (1975). *Astrology*. Arco Publishing.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional

import streamlit as st

from .western import (
    ZODIAC_SIGNS,
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
# Aspect definitions used for Draconic–Natal overlay
# Orb ≤ 3° as prescribed by Crane for meaningful soul–personality linkages
# ============================================================

DRACONIC_ASPECTS = [
    {"name": "Conjunction",   "symbol": "☌", "angle": 0,   "orb": 3.0, "zh": "合相", "zh_cn": "合相"},
    {"name": "Opposition",    "symbol": "☍", "angle": 180, "orb": 3.0, "zh": "對沖", "zh_cn": "对冲"},
    {"name": "Trine",         "symbol": "△", "angle": 120, "orb": 3.0, "zh": "三合", "zh_cn": "三合"},
    {"name": "Square",        "symbol": "□", "angle": 90,  "orb": 3.0, "zh": "刑相", "zh_cn": "刑相"},
    {"name": "Sextile",       "symbol": "⚹", "angle": 60,  "orb": 3.0, "zh": "六合", "zh_cn": "六合"},
]

# Soul-significance priority for overlay display (personal points first)
SOUL_PRIORITY = [
    "Sun ☉", "Moon ☽", "Mercury ☿", "Venus ♀", "Mars ♂",
    "Jupiter ♃", "Saturn ♄", "Uranus ♅", "Neptune ♆", "Pluto ♇",
    "North Node ☊",
]

# Draconic planet interpretations (soul-level meanings per Crane)
DRACONIC_MEANINGS: dict[str, dict] = {
    "Sun ☉": {
        "zh": "靈魂認同與核心使命（龍頭太陽）：揭示靈魂此生化身的本質身份、目的與光之表達。",
        "zh_cn": "灵魂认同与核心使命（龙头太阳）：揭示灵魂此生化身的本质身份、目的与光之表达。",
        "en": "Soul identity and core mission (Draconic Sun): reveals the soul's essential identity, its purpose and expression of light in this incarnation.",
    },
    "Moon ☽": {
        "zh": "靈魂最深層的情感需求（龍頭月亮）：揭示靈魂內在感受的本質、本能的情感回應模式，以及跨越輪迴的根本需要。",
        "zh_cn": "灵魂最深层的情感需求（龙头月亮）：揭示灵魂内在感受的本质、本能的情感回应模式，以及跨越轮回的根本需要。",
        "en": "Soul's deepest emotional needs (Draconic Moon): the soul's essential feeling nature, instinctive emotional responses, and fundamental needs carried across lifetimes.",
    },
    "Mercury ☿": {
        "zh": "靈魂思維模式（龍頭水星）：靈魂層面的思考方式、學習風格與溝通意圖。",
        "zh_cn": "灵魂思维模式（龙头水星）：灵魂层面的思考方式、学习风格与沟通意图。",
        "en": "Soul's mental pattern (Draconic Mercury): the soul-level thinking style, learning mode, and communication intent.",
    },
    "Venus ♀": {
        "zh": "靈魂愛與美的渴望（龍頭金星）：靈魂層面對美、關係、和諧與價值觀的深層嚮往。",
        "zh_cn": "灵魂爱与美的渴望（龙头金星）：灵魂层面对美、关系、和谐与价值观的深层向往。",
        "en": "Soul's longing for love and beauty (Draconic Venus): the soul-level desire for beauty, relationship harmony, and values.",
    },
    "Mars ♂": {
        "zh": "靈魂意志與行動驅力（龍頭火星）：靈魂最深層的行動方向、勇氣與業力驅動力量。",
        "zh_cn": "灵魂意志与行动驱力（龙头火星）：灵魂最深层的行动方向、勇气与业力驱动力量。",
        "en": "Soul's will and drive (Draconic Mars): the soul's deepest direction of action, courage, and karmic motivating force.",
    },
    "Jupiter ♃": {
        "zh": "靈魂智慧與擴展（龍頭木星）：靈魂在此生尋求成長、哲學領悟與靈性擴展的方向。",
        "zh_cn": "灵魂智慧与扩展（龙头木星）：灵魂在此生寻求成长、哲学领悟与灵性扩展的方向。",
        "en": "Soul's wisdom and expansion (Draconic Jupiter): the direction in which the soul seeks growth, philosophical understanding, and spiritual expansion.",
    },
    "Saturn ♄": {
        "zh": "靈魂業力結構（龍頭土星）：揭示靈魂最深的業力責任、考驗與必須掌握的學習課題。",
        "zh_cn": "灵魂业力结构（龙头土星）：揭示灵魂最深的业力责任、考验与必须掌握的学习课题。",
        "en": "Soul's karmic structure (Draconic Saturn): the soul's deepest karmic responsibilities, tests, and lessons that must be mastered.",
    },
    "Uranus ♅": {
        "zh": "靈魂革命衝動（龍頭天王星）：靈魂層面的革新使命、突破慣性的靈感，與集體業力的覺醒節點。",
        "zh_cn": "灵魂革命冲动（龙头天王星）：灵魂层面的革新使命、突破惯性的灵感，与集体业力的觉醒节点。",
        "en": "Soul's revolutionary impulse (Draconic Uranus): the soul-level mission of innovation, inspiration to break patterns, and collective karmic awakening.",
    },
    "Neptune ♆": {
        "zh": "靈魂靈性理想（龍頭海王星）：靈魂對神聖合一、慈悲與靈性融合的最深渴望。",
        "zh_cn": "灵魂灵性理想（龙头海王星）：灵魂对神圣合一、慈悲与灵性融合的最深渴望。",
        "en": "Soul's spiritual ideal (Draconic Neptune): the soul's deepest longing for divine unity, compassion, and spiritual dissolution.",
    },
    "Pluto ♇": {
        "zh": "靈魂轉化力量（龍頭冥王星）：靈魂最深層的死亡與重生循環、業力蛻變的核心動力。",
        "zh_cn": "灵魂转化力量（龙头冥王星）：灵魂最深层的死亡与重生循环、业力蜕变的核心动力。",
        "en": "Soul's transformative power (Draconic Pluto): the soul's deepest death-rebirth cycles and the core engine of karmic transformation.",
    },
}

# Sign meanings for Draconic placement context
SIGN_SOUL_MEANINGS: dict[str, dict] = {
    "Aries":       {"zh": "白羊座 ♈ — 靈魂的先驅精神、勇氣與新開端的純粹推動力。", "en": "Aries ♈ — the soul's pioneering spirit, courage, and pure impulse toward new beginnings."},
    "Taurus":      {"zh": "金牛座 ♉ — 靈魂對物質安全、身體滋養與永恆美的渴望。", "en": "Taurus ♉ — the soul's desire for material security, physical nourishment, and enduring beauty."},
    "Gemini":      {"zh": "雙子座 ♊ — 靈魂對知識多元、溝通連結與靈活適應的渴求。", "en": "Gemini ♊ — the soul's thirst for diverse knowledge, communication, and flexible adaptation."},
    "Cancer":      {"zh": "巨蟹座 ♋ — 靈魂的滋養本能、情感根源與家族業力。", "en": "Cancer ♋ — the soul's nurturing instinct, emotional roots, and ancestral karmic bonds."},
    "Leo":         {"zh": "獅子座 ♌ — 靈魂的創造性自我表達、光輝顯化與心靈慷慨。", "en": "Leo ♌ — the soul's creative self-expression, radiant manifestation, and generous heart."},
    "Virgo":       {"zh": "處女座 ♍ — 靈魂的辨別智慧、淨化服務與實際精進的使命。", "en": "Virgo ♍ — the soul's discerning wisdom, purifying service, and mission of practical refinement."},
    "Libra":       {"zh": "天秤座 ♎ — 靈魂對平衡、公正、美與和諧關係的深層追求。", "en": "Libra ♎ — the soul's deep pursuit of balance, justice, beauty, and harmonious relationships."},
    "Scorpio":     {"zh": "天蠍座 ♏ — 靈魂的蛻變深度、業力解謎與死亡重生的核心課題。", "en": "Scorpio ♏ — the soul's transformative depth, karmic mystery-solving, and death-rebirth core themes."},
    "Sagittarius": {"zh": "射手座 ♐ — 靈魂對真理、哲學探索、遠方視野與靈性自由的渴求。", "en": "Sagittarius ♐ — the soul's quest for truth, philosophical exploration, far horizons, and spiritual freedom."},
    "Capricorn":   {"zh": "摩羯座 ♑ — 靈魂的責任承擔、紀律修煉與世間成就的業力使命。", "en": "Capricorn ♑ — the soul's karmic mission of taking responsibility, disciplined mastery, and worldly achievement."},
    "Aquarius":    {"zh": "水瓶座 ♒ — 靈魂的人道覺醒、集體革新與超越個人自我的宇宙視野。", "en": "Aquarius ♒ — the soul's humanitarian awakening, collective innovation, and cosmic vision beyond personal ego."},
    "Pisces":      {"zh": "雙魚座 ♓ — 靈魂的萬物合一感知、慈悲奉獻與靈性解脫的最終渴望。", "en": "Pisces ♓ — the soul's perception of universal oneness, compassionate devotion, and longing for spiritual liberation."},
}


# ============================================================
# Data Classes
# ============================================================

@dataclass
class DraconicPlanet:
    """行星在龍頭星盤中的位置"""
    name: str
    natal_longitude: float      # 本命黃道經度
    draconic_longitude: float   # 龍頭星盤經度
    sign: str
    sign_glyph: str
    sign_chinese: str
    sign_degree: float
    element: str
    retrograde: bool
    house: int = 0


@dataclass
class OverlayAspect:
    """龍頭盤與本命盤之間的相位（靈魂—性格連結）"""
    draconic_planet: str        # 龍頭盤行星
    natal_point: str            # 本命盤行星/軸點
    aspect_name: str
    aspect_symbol: str
    angle: float
    orb: float
    is_exact: bool = False      # True if orb ≤ 1°


@dataclass
class DraconicChart:
    """龍頭星盤完整資料"""
    natal_chart: WesternChart
    north_node_longitude: float     # 本命北交點黃道經度（基準點）
    planets: List[DraconicPlanet] = field(default_factory=list)
    overlay_aspects: List[OverlayAspect] = field(default_factory=list)
    ascendant: float = 0.0          # 龍頭上升點
    midheaven: float = 0.0          # 龍頭中天


# ============================================================
# Calculation
# ============================================================

def _draconic_longitude(natal_lon: float, north_node_lon: float) -> float:
    """
    Apply Crane's Draconic transformation:
        Draconic Longitude = (Natal Longitude − North Node Longitude) mod 360°
    """
    return _normalize(natal_lon - north_node_lon)


def _angular_diff(lon_a: float, lon_b: float) -> float:
    """Minimum angular difference between two longitudes (0–180°)."""
    diff = abs(lon_a - lon_b) % 360.0
    if diff > 180.0:
        diff = 360.0 - diff
    return diff


def _find_overlay_aspects(
    draconic_planets: List[DraconicPlanet],
    natal_chart: WesternChart,
) -> List[OverlayAspect]:
    """
    Find aspects (orb ≤ 3°) between Draconic planets and Natal planets/angles.
    Following Crane: tight conjunctions, oppositions, and major aspects reveal
    the most significant Soul–Personality linkages.
    """
    aspects: List[OverlayAspect] = []

    # Build natal reference points: planets + ASC + MC
    natal_points: list[tuple[str, float]] = [
        (p.name, p.longitude) for p in natal_chart.planets
    ]
    natal_points.append(("ASC (上升)", natal_chart.ascendant))
    natal_points.append(("MC (中天)", natal_chart.midheaven))

    for dp in draconic_planets:
        for natal_name, natal_lon in natal_points:
            for asp_def in DRACONIC_ASPECTS:
                target_angle = asp_def["angle"]
                diff = _angular_diff(dp.draconic_longitude, natal_lon)
                orb = abs(diff - target_angle)
                if orb <= asp_def["orb"]:
                    aspects.append(OverlayAspect(
                        draconic_planet=dp.name,
                        natal_point=natal_name,
                        aspect_name=asp_def["name"],
                        aspect_symbol=asp_def["symbol"],
                        angle=target_angle,
                        orb=round(orb, 2),
                        is_exact=(orb <= 1.0),
                    ))

    # Sort: exact first, then by orb
    aspects.sort(key=lambda a: (not a.is_exact, a.orb))
    return aspects


@st.cache_data(ttl=3600, show_spinner=False)
def compute_draconic_chart(
    natal_longitudes: tuple,   # tuple of (name, lon, lat, retrograde, house) — hashable
    natal_ascendant: float,
    natal_midheaven: float,
    north_node_longitude: float,
) -> DraconicChart:
    """
    Compute the Draconic Chart.

    Following Crane (1987): for each planet with absolute tropical longitude L
    and North Node longitude N, the Draconic position is (L − N) mod 360°.

    Args:
        natal_longitudes: tuple of (name, lon, lat, retrograde, house) tuples
        natal_ascendant: natal Ascendant longitude
        natal_midheaven: natal Midheaven longitude
        north_node_longitude: natal True/Mean North Node longitude (Dragon's Head)
    """
    nn = north_node_longitude

    d_planets: List[DraconicPlanet] = []
    for item in natal_longitudes:
        name, lon, lat, retrograde, house = item
        d_lon = _draconic_longitude(lon, nn)
        idx = _sign_index(d_lon)
        sign_info = ZODIAC_SIGNS[idx]
        d_planets.append(DraconicPlanet(
            name=name,
            natal_longitude=lon,
            draconic_longitude=d_lon,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            sign_chinese=sign_info[2],
            sign_degree=_sign_degree(d_lon),
            element=sign_info[3],
            retrograde=retrograde,
            house=house,
        ))

    d_asc = _draconic_longitude(natal_ascendant, nn)
    d_mc = _draconic_longitude(natal_midheaven, nn)

    # Return without natal_chart and overlay_aspects (cannot be cached)
    chart = DraconicChart(
        natal_chart=None,  # type: ignore[arg-type]
        north_node_longitude=nn,
        planets=d_planets,
        overlay_aspects=[],
        ascendant=d_asc,
        midheaven=d_mc,
    )
    return chart


# ============================================================
# SVG Rendering helpers
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


def _render_draconic_wheel(dchart: DraconicChart):
    """
    Render the Draconic wheel using a 4×4 grid SVG,
    mirroring the harmonic / natal wheel layout.
    """
    d_asc = dchart.ascendant

    # Equal-house cusps from Draconic Ascendant
    d_cusps = [_normalize(d_asc + i * 30.0) for i in range(12)]

    def _find_d_house(lon: float) -> int:
        lon = _normalize(lon)
        for i in range(12):
            start = d_cusps[i]
            end = d_cusps[(i + 1) % 12]
            if start < end:
                if start <= lon < end:
                    return i + 1
            else:
                if lon >= start or lon < end:
                    return i + 1
        return 1

    house_planets: dict[int, list] = {i: [] for i in range(1, 13)}
    for p in dchart.planets:
        h = _find_d_house(p.draconic_longitude)
        house_planets[h].append(p)

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

    asc_sign_idx = _sign_index(d_asc)
    asc_sign_info = ZODIAC_SIGNS[asc_sign_idx]
    mc_sign_idx = _sign_index(dchart.midheaven)
    mc_sign_info = ZODIAC_SIGNS[mc_sign_idx]
    nn_sign_idx = _sign_index(dchart.north_node_longitude)
    nn_sign_info = ZODIAC_SIGNS[nn_sign_idx]

    _bg = CHART_BG
    _cell_bg = BG_LIGHT
    _asc_bg = "#251c00"
    _mc_bg = "#160d30"
    _nn_bg = "#0d2510"          # dark green tint for North Node emphasis
    _center_bg = CHART_BG
    _stroke = CHART_GRID_LINE
    _ring_stroke = CHART_RING_STROKE
    _text = CHART_TEXT_COLOR
    _text2 = TEXT_SECONDARY
    _text_muted = "#7070a0"
    _gold = SECONDARY_COLOR
    _purple = PRIMARY_COLOR
    _teal = "#2dd4bf"           # dragon colour for draconic elements
    _font = FONT_FAMILY

    parts: list[str] = []
    parts.append(
        f'<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'class="chart-wheel" '
        f'viewBox="0 0 {W} {H_SVG}" '
        f'style="width:100%;max-width:{W}px;display:block;margin:auto;'
        f'background:{_bg};border-radius:12px;'
        f'border:1px solid rgba(45,212,191,0.20);'
        f'font-family:{_font};">'
    )

    # Title
    parts.append(
        f'<text x="{W / 2}" y="18" text-anchor="middle" '
        f'fill="{_teal}" font-size="14" font-weight="bold">'
        f'☊ Draconic Chart 龍頭星盤 (Soul Chart / 靈魂盤)</text>'
    )
    nn_deg = _sign_degree(dchart.north_node_longitude)
    parts.append(
        f'<text x="{W / 2}" y="36" text-anchor="middle" '
        f'fill="{_text2}" font-size="11">'
        f'▲ D-ASC {_esc(asc_sign_info[1])}{_esc(asc_sign_info[0])} '
        f'{_sign_degree(d_asc):.1f}°'
        f'  ⬡ D-MC {_esc(mc_sign_info[1])}{_esc(mc_sign_info[0])} '
        f'{_sign_degree(dchart.midheaven):.1f}°'
        f'  ☊NN {_esc(nn_sign_info[1])}{_esc(nn_sign_info[0])} '
        f'{nn_deg:.1f}°'
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
                    f'<text x="{mcx}" y="{mcy - 26}" text-anchor="middle" '
                    f'fill="{_teal}" font-size="22" font-weight="bold">☊</text>'
                )
                parts.append(
                    f'<text x="{mcx}" y="{mcy - 6}" text-anchor="middle" '
                    f'fill="{_gold}" font-size="12" font-weight="bold">龍頭星盤</text>'
                )
                parts.append(
                    f'<text x="{mcx}" y="{mcy + 12}" text-anchor="middle" '
                    f'fill="{_text2}" font-size="10">Draconic</text>'
                )
                parts.append(
                    f'<text x="{mcx}" y="{mcy + 28}" text-anchor="middle" '
                    f'fill="{_text_muted}" font-size="10">'
                    f'NN = 0° ♈ (Soul Axis)</text>'
                )
                continue

            cusp_lon = d_cusps[house_num - 1]
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
    st.caption("▲ = D-ASC (Draconic Ascendant / 龍頭上升)   ⬡ = D-MC (Draconic Midheaven / 龍頭中天)   ☊ = North Node (北交點，固定於0°♈)")


# ============================================================
# Planet table
# ============================================================

def _render_draconic_planet_table(dchart: DraconicChart, lang: str = "zh"):
    """Render planet positions table for the Draconic chart."""
    if lang == "en":
        st.subheader("🪐 Draconic Planet Positions")
        st.caption(
            "Formula: Draconic Longitude = (Tropical Longitude − North Node) mod 360°  |  "
            f"North Node = {dchart.north_node_longitude:.3f}°"
        )
    else:
        label = "龍頭星盤行星位置" if lang == "zh" else "龙头星盘行星位置"
        st.subheader(f"🪐 {label}")
        nn_label = "北交點" if lang == "zh" else "北交点"
        st.caption(
            f"公式：龍頭黃道度 = （本命黃道度 − 北交點度數）mod 360°  |  "
            f"{nn_label} = {dchart.north_node_longitude:.3f}°"
        )

    if lang == "en":
        header = "| Planet | Tropical Lon. | Draconic Lon. | Sign | Degree |"
    elif lang == "zh_cn":
        header = "| 行星 | 本命黄道经度 | 龙头盘经度 | 星座 | 度数 |"
    else:
        header = "| 行星 | 本命黃道經度 | 龍頭盤經度 | 星座 | 度數 |"

    sep = "|:------:|:-------:|:-------:|:----:|:------:|"
    rows = [header, sep]
    for p in dchart.planets:
        retro = " ℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        rows.append(
            f"| {name_html}{retro} "
            f"| {p.natal_longitude:.3f}° "
            f"| **{p.draconic_longitude:.3f}°** "
            f"| {p.sign_glyph} {p.sign} ({p.sign_chinese}) "
            f"| {p.sign_degree:.2f}° |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


# ============================================================
# Overlay aspects (Draconic–Natal)
# ============================================================

def _render_overlay_aspects(dchart: DraconicChart, lang: str = "zh"):
    """Render Draconic–Natal overlay aspects (Soul–Personality linkages)."""
    if lang == "en":
        st.subheader("🔗 Soul–Personality Linkages (Draconic ↔ Natal, orb ≤ 3°)")
        st.caption(
            "According to Crane (1987), the most revealing insights arise when Draconic "
            "planets form tight aspects (especially conjunctions and oppositions, orb ≤ 3°) "
            "with personal natal points (Sun, Moon, ASC, MC). "
            "★ marks exact aspects (orb ≤ 1°)."
        )
    elif lang == "zh_cn":
        st.subheader("🔗 灵魂—性格连结（龙头盘 ↔ 本命盘，容差 ≤ 3°）")
        st.caption(
            "根据Crane（1987），当龙头盘行星与本命盘个人点（太阳、月亮、上升、中天）"
            "形成紧密相位（特别是合相与对冲，容差≤3°）时，灵魂意图与性格表达之间最深层的"
            "联结便得以揭示。★ 标记精准相位（容差≤1°）。"
        )
    else:
        st.subheader("🔗 靈魂—性格連結（龍頭盤 ↔ 本命盤，容差 ≤ 3°）")
        st.caption(
            "根據Crane（1987），當龍頭盤行星與本命盤個人點（太陽、月亮、上升、中天）"
            "形成緊密相位（特別是合相與對沖，容差≤3°）時，靈魂意圖與性格表達之間最深層的"
            "連結便得以揭示。★ 標記精準相位（容差≤1°）。"
        )

    if not dchart.overlay_aspects:
        if lang == "en":
            st.info("No significant overlay aspects found within 3° orb.")
        elif lang == "zh_cn":
            st.info("在3°容差内未发现显著的灵魂—性格连结相位。")
        else:
            st.info("在3°容差內未發現顯著的靈魂—性格連結相位。")
        return

    if lang == "en":
        header = "| ★ | Draconic Planet | Asp | Natal Point | Orb | Soul–Personality Meaning |"
    elif lang == "zh_cn":
        header = "| ★ | 龙头盘行星 | 相位 | 本命点 | 容差 | 灵魂—性格意义 |"
    else:
        header = "| ★ | 龍頭盤行星 | 相位 | 本命點 | 容差 | 靈魂—性格意義 |"

    sep = "|:-:|:------:|:--:|:------:|:---:|:-------------|"
    rows = [header, sep]
    for a in dchart.overlay_aspects[:30]:
        star = "★" if a.is_exact else ""
        d_color = PLANET_COLORS.get(a.draconic_planet, "#c8c8c8")
        n_color = PLANET_COLORS.get(a.natal_point, "#c8c8c8")
        d_html = f'<span style="color:{d_color};font-weight:bold">D-{a.draconic_planet}</span>'
        n_html = f'<span style="color:{n_color};font-weight:bold">{a.natal_point}</span>'

        # Build meaning label
        d_pname = a.draconic_planet.split(" ")[0]  # e.g. "Sun"
        n_pname = a.natal_point.split(" ")[0]       # e.g. "Moon"

        if lang == "en":
            meaning = (
                f"Your Draconic {d_pname} {a.aspect_name.lower()}s the Natal {n_pname}, "
                f"showing the soul's {d_pname.lower()} mission directly touches "
                f"your personality's {n_pname.lower()} expression."
            )
        elif lang == "zh_cn":
            meaning = (
                f"龙头{d_pname}{a.aspect_symbol}本命{n_pname}：灵魂的{d_pname}使命"
                f"与性格层面的{n_pname}表达形成深层共鸣。"
            )
        else:
            meaning = (
                f"龍頭{d_pname}{a.aspect_symbol}本命{n_pname}：靈魂的{d_pname}使命"
                f"與性格層面的{n_pname}表達形成深層共鳴。"
            )

        rows.append(
            f"| {star} | {d_html} | {a.aspect_symbol} | {n_html} "
            f"| {a.orb:.2f}° | {meaning} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


# ============================================================
# Formula explanation
# ============================================================

def _render_draconic_formula(dchart: DraconicChart, lang: str = "zh"):
    """Show the Draconic transformation formula and a worked example."""
    if dchart.planets:
        example = dchart.planets[0]
        ex_name = example.name
        ex_natal = example.natal_longitude
        ex_drac = example.draconic_longitude
    else:
        ex_name = "Sun ☉"
        ex_natal = 0.0
        ex_drac = 0.0

    nn = dchart.north_node_longitude

    if lang == "en":
        st.markdown(
            f"**Crane's Draconic Formula** (from *The Draconic Chart*, 1987):\n\n"
            f"$$D(L) = (L - N_{{\\text{{node}}}}) \\bmod 360°$$\n\n"
            f"where $L$ = tropical longitude and $N_{{\\text{{node}}}}$ = North Node longitude\n\n"
            f"**Example** — {ex_name}:\n"
            f"- Tropical longitude: **{ex_natal:.3f}°**\n"
            f"- North Node: **{nn:.3f}°**\n"
            f"- Draconic: $({ex_natal:.3f}° - {nn:.3f}°) \\bmod 360° = "
            f"\\mathbf{{{ex_drac:.3f}°}}$\n\n"
            f"In every Draconic Chart the North Node falls at **exactly 0° Aries ♈** "
            f"and the South Node at **0° Libra ♎**."
        )
    elif lang == "zh_cn":
        st.markdown(
            f"**Crane龙头盘转换公式**（出自《The Draconic Chart》1987年）：\n\n"
            f"$$D(L) = (L - N_{{\\text{{node}}}}) \\bmod 360°$$\n\n"
            f"其中 $L$ = 本命黄道经度，$N_{{\\text{{node}}}}$ = 北交点经度\n\n"
            f"**示例** — {ex_name}：\n"
            f"- 本命黄道经度：**{ex_natal:.3f}°**\n"
            f"- 北交点：**{nn:.3f}°**\n"
            f"- 龙头盘经度：$({ex_natal:.3f}° - {nn:.3f}°) \\bmod 360° = "
            f"\\mathbf{{{ex_drac:.3f}°}}$\n\n"
            f"在每张龙头星盘中，北交点固定于 **0° 白羊座 ♈**，南交点固定于 **0° 天秤座 ♎**。"
        )
    else:
        st.markdown(
            f"**Crane龍頭盤轉換公式**（出自《The Draconic Chart》1987年）：\n\n"
            f"$$D(L) = (L - N_{{\\text{{node}}}}) \\bmod 360°$$\n\n"
            f"其中 $L$ = 本命黃道經度，$N_{{\\text{{node}}}}$ = 北交點黃道經度\n\n"
            f"**示例** — {ex_name}：\n"
            f"- 本命黃道經度：**{ex_natal:.3f}°**\n"
            f"- 北交點：**{nn:.3f}°**\n"
            f"- 龍頭盤經度：$({ex_natal:.3f}° - {nn:.3f}°) \\bmod 360° = "
            f"\\mathbf{{{ex_drac:.3f}°}}$\n\n"
            f"在每張龍頭星盤中，北交點固定於 **0° 白羊座 ♈**，南交點固定於 **0° 天秤座 ♎**。"
        )


# ============================================================
# Soul interpretation panel
# ============================================================

def _render_soul_interpretation(dchart: DraconicChart, lang: str = "zh"):
    """
    Render soul-level interpretation of key Draconic positions,
    following the classical Crane / Davison tradition.
    """
    if lang == "en":
        st.subheader("🌟 Soul Chart Interpretation")
        st.markdown(
            "> **According to the Draconic Chart (the Soul Chart)…**\n\n"
            "The Draconic Chart reveals the soul's pre-birth intention, karmic blueprint, "
            "and deeper purpose for this incarnation. All interpretations below reflect "
            "soul-level qualities — **not** personality expression (which belongs to the Tropical Chart)."
        )
    elif lang == "zh_cn":
        st.subheader("🌟 灵魂星盘解读")
        st.markdown(
            "> **根据龙头星盘（灵魂盘）……**\n\n"
            "龙头星盘揭示灵魂在降生前的意图、业力蓝图，以及此生化身的深层目的。"
            "以下解读皆反映灵魂层面的特质——**非**性格表达（性格属于本命热带盘的范畴）。"
        )
    else:
        st.subheader("🌟 靈魂星盤解讀")
        st.markdown(
            "> **根據龍頭星盤（靈魂盤）……**\n\n"
            "龍頭星盤揭示靈魂在降生前的意圖、業力藍圖，以及此生化身的深層目的。"
            "以下解讀皆反映靈魂層面的特質——**非**性格表達（性格屬於本命熱帶盤的範疇）。"
        )

    # Build planet lookup by name
    planet_map = {p.name: p for p in dchart.planets}

    # Key planets to interpret
    key_planets = [
        "Sun ☉", "Moon ☽", "Mercury ☿", "Venus ♀", "Mars ♂",
        "Jupiter ♃", "Saturn ♄",
    ]

    for pname in key_planets:
        p = planet_map.get(pname)
        if not p:
            continue
        meaning = DRACONIC_MEANINGS.get(pname, {})
        sign_meaning = SIGN_SOUL_MEANINGS.get(p.sign, {})

        meaning_text = meaning.get(lang, meaning.get("en", ""))
        sign_text = sign_meaning.get("zh" if lang in ("zh", "zh_cn") else "en", "")
        if lang == "zh_cn":
            sign_text = sign_meaning.get("zh", "").replace("龍頭", "龙头").replace("靈魂", "灵魂")

        retro = " ℞" if p.retrograde else ""
        label = f'{pname}{retro} → {p.sign_glyph} {p.sign} ({p.sign_chinese}) {p.sign_degree:.1f}°'
        with st.expander(f"{'🌟' if pname == 'Sun ☉' else ('🌙' if pname == 'Moon ☽' else '🔮')} {label}", expanded=(pname in ("Sun ☉", "Moon ☽"))):
            if meaning_text:
                st.info(meaning_text)
            if sign_text:
                if lang == "en":
                    st.markdown(f"**In {p.sign}:** {sign_text}")
                else:
                    st.markdown(f"**落入 {p.sign_chinese}：** {sign_text}")

    # ASC and MC
    d_asc = dchart.ascendant
    d_mc = dchart.midheaven
    asc_sign_info = ZODIAC_SIGNS[_sign_index(d_asc)]
    mc_sign_info = ZODIAC_SIGNS[_sign_index(d_mc)]

    if lang == "en":
        with st.expander(f"▲ Draconic ASC → {asc_sign_info[1]} {asc_sign_info[0]} {_sign_degree(d_asc):.1f}°", expanded=True):
            st.info(
                f"**Draconic Ascendant (Soul's intended approach to self-expression):**\n\n"
                f"Your Draconic Ascendant falls in **{asc_sign_info[0]}** — "
                f"this is the soul's intended mode of approaching the world and initiating "
                f"new beginnings. When this point conjuncts your Natal Ascendant or Sun, "
                f"the soul's mission is directly expressed through your outer personality."
            )
            sign_text = SIGN_SOUL_MEANINGS.get(asc_sign_info[0], {}).get("en", "")
            if sign_text:
                st.markdown(f"**Soul approach in {asc_sign_info[0]}:** {sign_text}")

        with st.expander(f"⬡ Draconic MC → {mc_sign_info[1]} {mc_sign_info[0]} {_sign_degree(d_mc):.1f}°", expanded=True):
            st.info(
                f"**Draconic Midheaven (Soul's public/spiritual purpose):**\n\n"
                f"Your Draconic MC falls in **{mc_sign_info[0]}** — "
                f"this reveals the soul's highest aspiration, its intended public role "
                f"and spiritual vocation in this lifetime."
            )
            sign_text = SIGN_SOUL_MEANINGS.get(mc_sign_info[0], {}).get("en", "")
            if sign_text:
                st.markdown(f"**Soul vocation in {mc_sign_info[0]}:** {sign_text}")
    else:
        asc_label = "龍頭上升（靈魂預定的自我表達方式）" if lang == "zh" else "龙头上升（灵魂预定的自我表达方式）"
        mc_label = "龍頭中天（靈魂的公共/靈性使命）" if lang == "zh" else "龙头中天（灵魂的公共/灵性使命）"

        with st.expander(f"▲ {asc_label} → {asc_sign_info[1]} {asc_sign_info[0]} ({asc_sign_info[2]}) {_sign_degree(d_asc):.1f}°", expanded=True):
            if lang == "zh":
                st.info(
                    f"**龍頭上升（靈魂預定的自我表達方式）：**\n\n"
                    f"您的龍頭上升落入 **{asc_sign_info[2]}（{asc_sign_info[0]}）** — "
                    f"這是靈魂預定的接觸世界與開創新局的方式。"
                    f"當此點與本命盤上升或太陽形成精密合相時，靈魂使命直接透過您的外在人格呈現。"
                )
            else:
                st.info(
                    f"**龙头上升（灵魂预定的自我表达方式）：**\n\n"
                    f"您的龙头上升落入 **{asc_sign_info[2]}（{asc_sign_info[0]}）** — "
                    f"这是灵魂预定的接触世界与开创新局的方式。"
                    f"当此点与本命盘上升或太阳形成精密合相时，灵魂使命直接通过您的外在人格呈现。"
                )
            sign_text = SIGN_SOUL_MEANINGS.get(asc_sign_info[0], {}).get("zh", "")
            if sign_text:
                label_in = "靈魂接觸方式於" if lang == "zh" else "灵魂接触方式于"
                st.markdown(f"**{label_in} {asc_sign_info[2]}：** {sign_text}")

        with st.expander(f"⬡ {mc_label} → {mc_sign_info[1]} {mc_sign_info[0]} ({mc_sign_info[2]}) {_sign_degree(d_mc):.1f}°", expanded=True):
            if lang == "zh":
                st.info(
                    f"**龍頭中天（靈魂的公共/靈性使命）：**\n\n"
                    f"您的龍頭中天落入 **{mc_sign_info[2]}（{mc_sign_info[0]}）** — "
                    f"揭示靈魂此生最高的志向、公共角色與靈性職志。"
                )
            else:
                st.info(
                    f"**龙头中天（灵魂的公共/灵性使命）：**\n\n"
                    f"您的龙头中天落入 **{mc_sign_info[2]}（{mc_sign_info[0]}）** — "
                    f"揭示灵魂此生最高的志向、公共角色与灵性职志。"
                )
            sign_text = SIGN_SOUL_MEANINGS.get(mc_sign_info[0], {}).get("zh", "")
            if sign_text:
                label_in = "靈魂職志於" if lang == "zh" else "灵魂职志于"
                st.markdown(f"**{label_in} {mc_sign_info[2]}：** {sign_text}")

    # Key Soul–Personality linkages (top 3 exact or close aspects)
    if dchart.overlay_aspects:
        close = [a for a in dchart.overlay_aspects if a.orb <= 2.0][:5]
        if close:
            if lang == "en":
                st.subheader("✨ Key Soul–Personality Linkages")
                st.caption("Draconic–Natal aspects within 2° reveal the clearest soul-personality bridges.")
            elif lang == "zh_cn":
                st.subheader("✨ 关键灵魂—性格连结")
                st.caption("龙头盘与本命盘2°以内的相位揭示最清晰的灵魂—性格桥梁。")
            else:
                st.subheader("✨ 關鍵靈魂—性格連結")
                st.caption("龍頭盤與本命盤2°以內的相位揭示最清晰的靈魂—性格橋梁。")

            for a in close:
                d_color = PLANET_COLORS.get(a.draconic_planet, "#c8c8c8")
                n_color = PLANET_COLORS.get(a.natal_point, "#c8c8c8")
                exact_star = "★ " if a.is_exact else ""
                if lang == "en":
                    msg = (
                        f"{exact_star}**Draconic {a.draconic_planet}** "
                        f"{a.aspect_symbol} "
                        f"**Natal {a.natal_point}** (orb {a.orb:.2f}°) — "
                        f"Your soul's {a.draconic_planet.split()[0].lower()} intention is "
                        f"directly linked to your natal {a.natal_point.split()[0].lower()} expression, "
                        f"showing this is a key soul-personality bridge in your chart."
                    )
                elif lang == "zh_cn":
                    msg = (
                        f"{exact_star}**龙头{a.draconic_planet}** "
                        f"{a.aspect_symbol} "
                        f"**本命{a.natal_point}** （容差 {a.orb:.2f}°）— "
                        f"您灵魂层面的{a.draconic_planet.split()[0]}意图与性格层面的{a.natal_point.split()[0]}表达"
                        f"形成深层连结，这是您星盘中最重要的灵魂—性格桥梁之一。"
                    )
                else:
                    msg = (
                        f"{exact_star}**龍頭{a.draconic_planet}** "
                        f"{a.aspect_symbol} "
                        f"**本命{a.natal_point}** （容差 {a.orb:.2f}°）— "
                        f"您靈魂層面的{a.draconic_planet.split()[0]}意圖與性格層面的{a.natal_point.split()[0]}表達"
                        f"形成深層連結，這是您星盤中最重要的靈魂—性格橋梁之一。"
                    )
                st.success(msg)


# ============================================================
# Main render entry point
# ============================================================

def render_draconic_chart(natal_chart: WesternChart, lang: str = "zh"):
    """
    Full Streamlit rendering of the Draconic Chart feature,
    embodying the classical Crane (1987) / Davison (1975) methodology.

    Args:
        natal_chart: The natal WesternChart to derive the Draconic chart from.
        lang: UI language ('zh', 'zh_cn', 'en').
    """

    # ── 1. Introduction ───────────────────────────────────────────────────────
    if lang == "en":
        st.markdown(
            "### ☊ Draconic Chart — The Soul Chart\n\n"
            "> *\"The Draconic Chart is the chart of the soul… "
            "the celestial pattern that existed before birth, "
            "the blueprint the soul carries into incarnation.\"*  \n"
            "> — Rev. Pamela Crane, *The Draconic Chart* (1987)\n\n"
            "The Draconic Chart is calculated by **reorienting the entire zodiac "
            "to the Moon's North Node (Dragon's Head)**. "
            "Setting the North Node to exactly 0° Aries shifts all planets and angles "
            "by the same arc, revealing their positions relative to the soul's evolutionary axis.\n\n"
            "**Key distinction:** The Tropical/Natal Chart shows *personality expression* "
            "and life circumstances; the Draconic Chart shows *soul intention* and karmic purpose."
        )
    elif lang == "zh_cn":
        st.markdown(
            "### ☊ 龙头星盘 — 灵魂盘\n\n"
            "> *「龙头星盘是灵魂的星盘……是降生之前存在的天象蓝图，"
            "是灵魂携入此生的业力模板。」*  \n"
            "> — Rev. Pamela Crane，《The Draconic Chart》（1987）\n\n"
            "龙头星盘通过将**整个黄道重新定向于月亮北交点（龙头）**来计算。"
            "将北交点固定于0°白羊座，使所有行星和轴点偏移相同弧度，"
            "从而揭示它们相对于灵魂进化轴的位置。\n\n"
            "**关键区别：** 本命热带盘呈现*性格表达*与生命境遇；龙头星盘呈现*灵魂意图*与业力使命。"
        )
    else:
        st.markdown(
            "### ☊ 龍頭星盤 — 靈魂盤\n\n"
            "> *「龍頭星盤是靈魂的星盤……是降生之前存在的天象藍圖，"
            "是靈魂攜入此生的業力模板。」*  \n"
            "> — Rev. Pamela Crane，《The Draconic Chart》（1987）\n\n"
            "龍頭星盤通過將**整個黃道重新定向於月亮北交點（龍頭）**來計算。"
            "將北交點固定於0°白羊座，使所有行星和軸點偏移相同弧度，"
            "從而揭示它們相對於靈魂進化軸的位置。\n\n"
            "**關鍵區別：** 本命熱帶盤呈現*性格表達*與生命境遇；龍頭星盤呈現*靈魂意圖*與業力使命。"
        )

    # ── 2. Compute ────────────────────────────────────────────────────────────
    # Retrieve North Node from the natal chart's planet list
    north_node_planet = next(
        (p for p in natal_chart.planets if "North Node" in p.name),
        None,
    )
    if north_node_planet is None:
        st.error("North Node not found in natal chart. Cannot compute Draconic Chart.")
        return

    nn_lon = north_node_planet.longitude
    nn_sign_info = ZODIAC_SIGNS[_sign_index(nn_lon)]

    if lang == "en":
        st.info(
            f"**Natal North Node (Dragon's Head / 龍頭):** "
            f"{nn_sign_info[1]} {nn_sign_info[0]} {_sign_degree(nn_lon):.2f}° "
            f"({nn_lon:.3f}° absolute)  \n"
            f"All Draconic positions are shifted by **−{nn_lon:.3f}°** "
            f"so that the North Node aligns with 0° Aries."
        )
    elif lang == "zh_cn":
        st.info(
            f"**本命北交点（龙头）：**"
            f"{nn_sign_info[1]} {nn_sign_info[2]}（{nn_sign_info[0]}）{_sign_degree(nn_lon):.2f}°"
            f"（绝对经度 {nn_lon:.3f}°）  \n"
            f"所有龙头盘度数偏移 **−{nn_lon:.3f}°**，使北交点对准0°白羊座。"
        )
    else:
        st.info(
            f"**本命北交點（龍頭）：**"
            f"{nn_sign_info[1]} {nn_sign_info[2]}（{nn_sign_info[0]}）{_sign_degree(nn_lon):.2f}°"
            f"（絕對經度 {nn_lon:.3f}°）  \n"
            f"所有龍頭盤度數偏移 **−{nn_lon:.3f}°**，使北交點對準0°白羊座。"
        )

    # Package natal longitudes as a hashable tuple for caching
    _natal_tuple = tuple(
        (p.name, p.longitude, p.latitude, p.retrograde, p.house)
        for p in natal_chart.planets
    )

    dchart = compute_draconic_chart(
        natal_longitudes=_natal_tuple,
        natal_ascendant=natal_chart.ascendant,
        natal_midheaven=natal_chart.midheaven,
        north_node_longitude=nn_lon,
    )
    dchart.natal_chart = natal_chart

    # Compute overlay aspects (cannot be cached due to natal_chart reference)
    dchart.overlay_aspects = _find_overlay_aspects(dchart.planets, natal_chart)

    # ── 3. Wheel ──────────────────────────────────────────────────────────────
    _render_draconic_wheel(dchart)

    st.divider()

    # ── 4. Soul interpretation ────────────────────────────────────────────────
    _render_soul_interpretation(dchart, lang)

    st.divider()

    # ── 5. Formula ────────────────────────────────────────────────────────────
    label_formula = "🧮 Transformation Formula (Crane 1987)" if lang == "en" else (
        "🧮 转换公式（Crane 1987）" if lang == "zh_cn" else "🧮 轉換公式（Crane 1987）"
    )
    with st.expander(label_formula, expanded=False):
        _render_draconic_formula(dchart, lang)

    st.divider()

    # ── 6. Planet positions table ─────────────────────────────────────────────
    _render_draconic_planet_table(dchart, lang)

    st.divider()

    # ── 7. Overlay aspects ────────────────────────────────────────────────────
    _render_overlay_aspects(dchart, lang)

    st.divider()

    # ── 8. Classical reference note ───────────────────────────────────────────
    if lang == "en":
        with st.expander("📖 Classical References — Draconic Astrology", expanded=False):
            st.markdown(
                "**Foundational works on the Draconic Chart:**\n\n"
                "- **Crane, Rev. Pamela** (1987). *The Draconic Chart*. Wessex Astrologer. — "
                "The definitive modern treatment; establishes the Soul Chart interpretation.\n"
                "- **Davison, Ronald C.** (1975). *Astrology*. Arco Publishing. — "
                "Early formulation of the Draconic technique.\n"
                "- **Brady, Bernadette** (1999). *Predictive Astrology*. Weiser Books. — "
                "Extended use of Draconic chart in predictive work.\n\n"
                "**Core principle:** The Draconic Chart must never be interpreted in isolation. "
                "Its true power emerges through overlay and comparison with the Tropical Natal Chart. "
                "Tight conjunctions (orb ≤ 3°) between Draconic planets and Natal personal points "
                "(Sun, Moon, ASC, MC, Nodes) reveal the clearest soul–personality bridges."
            )
    elif lang == "zh_cn":
        with st.expander("📖 经典文献 — 龙头占星", expanded=False):
            st.markdown(
                "**龙头星盘奠基著作：**\n\n"
                "- **Crane, Rev. Pamela**（1987）《The Draconic Chart》Wessex Astrologer —— "
                "现代权威著作，建立灵魂盘诠释体系。\n"
                "- **Davison, Ronald C.**（1975）《Astrology》Arco Publishing —— "
                "龙头技法的早期表述。\n"
                "- **Brady, Bernadette**（1999）《Predictive Astrology》Weiser Books —— "
                "扩展了龙头盘在预测占星中的运用。\n\n"
                "**核心原则：** 龙头星盘绝不能单独诠释；"
                "其真正力量在于与本命热带盘的叠合比较。"
                "龙头盘行星与本命个人点（太阳、月亮、上升、中天、交点）"
                "形成的紧密合相（容差≤3°）揭示最清晰的灵魂—性格桥梁。"
            )
    else:
        with st.expander("📖 經典文獻 — 龍頭占星", expanded=False):
            st.markdown(
                "**龍頭星盤奠基著作：**\n\n"
                "- **Crane, Rev. Pamela**（1987）《The Draconic Chart》Wessex Astrologer —— "
                "現代權威著作，建立靈魂盤詮釋體系。\n"
                "- **Davison, Ronald C.**（1975）《Astrology》Arco Publishing —— "
                "龍頭技法的早期表述。\n"
                "- **Brady, Bernadette**（1999）《Predictive Astrology》Weiser Books —— "
                "擴展了龍頭盤在預測占星中的運用。\n\n"
                "**核心原則：** 龍頭星盤絕不能單獨詮釋；"
                "其真正力量在於與本命熱帶盤的疊合比較。"
                "龍頭盤行星與本命個人點（太陽、月亮、上升、中天、交點）"
                "形成的緊密合相（容差≤3°）揭示最清晰的靈魂—性格橋梁。"
            )
