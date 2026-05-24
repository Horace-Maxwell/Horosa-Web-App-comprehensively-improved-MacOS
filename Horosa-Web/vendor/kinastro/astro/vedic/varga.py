"""
astro/vedic/varga.py — Shodasa Varga 分盤計算模組
Divisional Chart Computation Module (D1–D60)

根據 BPHS (Brihat Parashara Hora Shastra) 第9章的規則計算所有
16種分盤 (Shodasa Varga) 以及額外常用分盤 (D5, D6, D8, D11, D27)。

Each varga function takes a sidereal longitude (0–360) and returns
the rashi index (0–11) in which the planet falls in that divisional chart.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ============================================================
# 星座 (Rashi) 常量 — mirrors indian.py RASHIS
# ============================================================
RASHIS = [
    ("Mesha", "♈", "白羊", "Mars"),
    ("Vrishabha", "♉", "金牛", "Venus"),
    ("Mithuna", "♊", "雙子", "Mercury"),
    ("Karka", "♋", "巨蟹", "Moon"),
    ("Simha", "♌", "獅子", "Sun"),
    ("Kanya", "♍", "處女", "Mercury"),
    ("Tula", "♎", "天秤", "Venus"),
    ("Vrischika", "♏", "天蠍", "Mars"),
    ("Dhanu", "♐", "射手", "Jupiter"),
    ("Makara", "♑", "摩羯", "Saturn"),
    ("Kumbha", "♒", "水瓶", "Saturn"),
    ("Meena", "♓", "雙魚", "Jupiter"),
]

# ============================================================
# 分盤資訊表 (Varga Information)
# ============================================================
VARGA_INFO: Dict[str, Dict] = {
    "D1":  {"zh": "本命盤 Rasi",       "en": "Rasi (Natal)",             "division": 1,  "use_zh": "整體人生、性格、身體"},
    "D2":  {"zh": "財富盤 Hora",        "en": "Hora (Wealth)",            "division": 2,  "use_zh": "財富、收入"},
    "D3":  {"zh": "兄弟盤 Drekkana",    "en": "Drekkana (Siblings)",      "division": 3,  "use_zh": "兄弟姊妹、勇氣"},
    "D4":  {"zh": "家宅盤 Chaturthamsa","en": "Chaturthamsa (Property)",  "division": 4,  "use_zh": "房產、車輛、母親"},
    "D5":  {"zh": "後裔盤 Panchamsa",   "en": "Panchamsa (Progeny)",      "division": 5,  "use_zh": "子女、功德"},
    "D6":  {"zh": "疾病盤 Shashthamsa", "en": "Shashthamsa (Health)",     "division": 6,  "use_zh": "疾病、敵人、債務"},
    "D7":  {"zh": "子嗣盤 Saptamsa",    "en": "Saptamsa (Children)",      "division": 7,  "use_zh": "子女、子嗣、創造力"},
    "D8":  {"zh": "障礙盤 Ashtamsa",    "en": "Ashtamsa (Obstacles)",     "division": 8,  "use_zh": "障礙、突發事件、壽命"},
    "D9":  {"zh": "九分盤 Navamsa",     "en": "Navamsa (Marriage)",       "division": 9,  "use_zh": "配偶、婚姻、業力、晚年"},
    "D10": {"zh": "事業盤 Dasamsa",     "en": "Dasamsa (Career)",         "division": 10, "use_zh": "事業、地位、名聲"},
    "D11": {"zh": "成就盤 Ekadasamsa",  "en": "Ekadasamsa (Gains)",       "division": 11, "use_zh": "收益、成就、願望"},
    "D12": {"zh": "父母盤 Dwadasamsa",  "en": "Dwadasamsa (Parents)",     "division": 12, "use_zh": "父母、祖先"},
    "D16": {"zh": "享樂盤 Shodasamsa",  "en": "Shodasamsa (Pleasures)",   "division": 16, "use_zh": "快樂、車輛、舒適"},
    "D20": {"zh": "修行盤 Vimsamsa",    "en": "Vimsamsa (Spirituality)",  "division": 20, "use_zh": "宗教、靈性、修行"},
    "D24": {"zh": "學業盤 Chaturvimsamsa","en": "Chaturvimsamsa (Education)","division": 24, "use_zh": "學業、教育、知識"},
    "D27": {"zh": "強弱盤 Bhamsa",      "en": "Bhamsa (Strength)",        "division": 27, "use_zh": "整體強弱、行星力量"},
    "D30": {"zh": "災厄盤 Trimsamsa",   "en": "Trimsamsa (Misfortune)",   "division": 30, "use_zh": "不幸、疾病、災厄"},
    "D40": {"zh": "母福盤 Khavedamsa",  "en": "Khavedamsa (Mother)",      "division": 40, "use_zh": "母親福祉、祖產"},
    "D45": {"zh": "父福盤 Akshavedamsa","en": "Akshavedamsa (Father)",    "division": 45, "use_zh": "父親福祉、整體福報"},
    "D60": {"zh": "微果盤 Shashtiamsa", "en": "Shashtiamsa (Past Life)",  "division": 60, "use_zh": "前世業力、極細微果報"},
}

# The list of varga keys to display as individual tabs
VARGA_KEYS = [
    "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9",
    "D10", "D11", "D12", "D16", "D20", "D24", "D27",
    "D30", "D40", "D45", "D60",
]


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class VargaPlanet:
    """A planet's position in a specific divisional chart."""
    name: str
    natal_longitude: float      # original sidereal longitude
    varga_rashi_index: int      # rashi index (0–11) in this varga
    varga_rashi: str            # rashi name
    varga_glyph: str            # rashi glyph
    varga_chinese: str          # rashi Chinese name
    varga_lord: str             # rashi lord
    retrograde: bool = False


@dataclass
class VargaChart:
    """A single divisional chart."""
    key: str                    # e.g. "D9"
    name_zh: str
    name_en: str
    use_zh: str
    division: int
    planets: List[VargaPlanet] = field(default_factory=list)
    ascendant_rashi_index: int = 0  # ascendant's varga rashi


# ============================================================
# 核心分盤計算 (Core Varga Computation)
# ============================================================

def _normalize(deg: float) -> float:
    """Normalize degree to 0–360."""
    return deg % 360.0


def _sign_index(deg: float) -> int:
    """Get the sign index (0–11) from a longitude."""
    return int(_normalize(deg) / 30.0)


def _sign_degree(deg: float) -> float:
    """Get degree within sign (0–30)."""
    return _normalize(deg) % 30.0


# --- Individual Varga calculations ---
# Each function returns the rashi index (0–11) for a given sidereal longitude.

def _varga_d1(lon: float) -> int:
    """D1 — Rasi (Natal chart): sign = floor(lon / 30)."""
    return _sign_index(lon)


def _varga_d2(lon: float) -> int:
    """D2 — Hora: each sign split into 2 halves (15° each).
    Odd signs: 0–15° → Leo (Sun Hora), 15–30° → Cancer (Moon Hora).
    Even signs: 0–15° → Cancer, 15–30° → Leo.
    """
    sign = _sign_index(lon)
    half = 0 if _sign_degree(lon) < 15.0 else 1
    odd = (sign % 2 == 0)  # 0-based: Aries=0 is odd sign
    if odd:
        return 4 if half == 0 else 3   # Leo, Cancer
    else:
        return 3 if half == 0 else 4   # Cancer, Leo


def _varga_d3(lon: float) -> int:
    """D3 — Drekkana: each sign split into 3 parts (10° each).
    Part 1 (0–10°) → same sign
    Part 2 (10–20°) → 5th from sign
    Part 3 (20–30°) → 9th from sign
    """
    sign = _sign_index(lon)
    part = int(_sign_degree(lon) / 10.0)
    part = min(part, 2)
    offsets = [0, 4, 8]  # same, 5th, 9th
    return (sign + offsets[part]) % 12


def _varga_d4(lon: float) -> int:
    """D4 — Chaturthamsa: each sign split into 4 parts (7°30' each).
    Parts map to sign, 4th, 7th, 10th from sign.
    """
    sign = _sign_index(lon)
    part = int(_sign_degree(lon) / 7.5)
    part = min(part, 3)
    offsets = [0, 3, 6, 9]
    return (sign + offsets[part]) % 12


def _varga_d5(lon: float) -> int:
    """D5 — Panchamsa: each sign split into 5 parts (6° each).
    Odd signs start from same sign; even signs start from opposite.
    """
    sign = _sign_index(lon)
    part = int(_sign_degree(lon) / 6.0)
    part = min(part, 4)
    odd = (sign % 2 == 0)  # 0-based
    if odd:
        # Odd signs: parts map to sign, sign+1, sign+2, ...
        return (sign + part) % 12
    else:
        # Even signs: start from sign+6
        return (sign + 6 + part) % 12


def _varga_d6(lon: float) -> int:
    """D6 — Shashthamsa: each sign split into 6 parts (5° each).
    Odd signs start from same sign; even signs start from 7th.
    """
    sign = _sign_index(lon)
    part = int(_sign_degree(lon) / 5.0)
    part = min(part, 5)
    odd = (sign % 2 == 0)
    if odd:
        return (sign + part) % 12
    else:
        return (sign + 6 + part) % 12


def _varga_d7(lon: float) -> int:
    """D7 — Saptamsa: each sign split into 7 parts (4°17'8.57" each).
    Odd signs start from same sign; even signs start from 7th sign.
    """
    sign = _sign_index(lon)
    span = 30.0 / 7.0
    part = int(_sign_degree(lon) / span)
    part = min(part, 6)
    odd = (sign % 2 == 0)
    if odd:
        return (sign + part) % 12
    else:
        return (sign + 6 + part) % 12


def _varga_d8(lon: float) -> int:
    """D8 — Ashtamsa: each sign split into 8 parts (3°45' each).
    Movable signs start from Aries; Fixed from Sagittarius; Dual from Leo.
    """
    sign = _sign_index(lon)
    span = 30.0 / 8.0
    part = int(_sign_degree(lon) / span)
    part = min(part, 7)
    modality = sign % 3  # 0=movable, 1=fixed, 2=dual
    if modality == 0:
        start = 0   # Aries
    elif modality == 1:
        start = 8   # Sagittarius
    else:
        start = 4   # Leo
    return (start + part) % 12


def _varga_d9(lon: float) -> int:
    """D9 — Navamsa: each sign split into 9 parts (3°20' each).
    Fire signs start from Aries, Earth from Capricorn,
    Air from Libra, Water from Cancer.
    """
    sign = _sign_index(lon)
    span = 30.0 / 9.0
    part = int(_sign_degree(lon) / span)
    part = min(part, 8)
    # Element: Fire=0,3,6,9; Earth=1,4,7,10; Air=2,5,8,11; Water=3,6,9,0
    element = sign % 4  # 0=fire(Ari,Leo,Sag), 1=earth(Tau,Vir,Cap),
                          # 2=air(Gem,Lib,Aqu), 3=water(Can,Sco,Pis)
    starts = [0, 9, 6, 3]  # Aries, Capricorn, Libra, Cancer
    return (starts[element] + part) % 12


def _varga_d10(lon: float) -> int:
    """D10 — Dasamsa: each sign split into 10 parts (3° each).
    Odd signs start from same sign; even signs start from 9th sign.
    """
    sign = _sign_index(lon)
    span = 30.0 / 10.0
    part = int(_sign_degree(lon) / span)
    part = min(part, 9)
    odd = (sign % 2 == 0)
    if odd:
        return (sign + part) % 12
    else:
        return (sign + 8 + part) % 12


def _varga_d11(lon: float) -> int:
    """D11 — Ekadasamsa (Rudramsa): each sign split into 11 parts.
    Starts from same sign for all.
    """
    sign = _sign_index(lon)
    span = 30.0 / 11.0
    part = int(_sign_degree(lon) / span)
    part = min(part, 10)
    return (sign + part) % 12


def _varga_d12(lon: float) -> int:
    """D12 — Dwadasamsa: each sign split into 12 parts (2°30' each).
    Always starts from the same sign.
    """
    sign = _sign_index(lon)
    span = 30.0 / 12.0
    part = int(_sign_degree(lon) / span)
    part = min(part, 11)
    return (sign + part) % 12


def _varga_d16(lon: float) -> int:
    """D16 — Shodasamsa: each sign split into 16 parts (1°52'30" each).
    Movable signs start from Aries; Fixed from Leo; Dual from Sagittarius.
    """
    sign = _sign_index(lon)
    span = 30.0 / 16.0
    part = int(_sign_degree(lon) / span)
    part = min(part, 15)
    modality = sign % 3
    if modality == 0:
        start = 0   # Aries
    elif modality == 1:
        start = 4   # Leo
    else:
        start = 8   # Sagittarius
    return (start + part) % 12


def _varga_d20(lon: float) -> int:
    """D20 — Vimsamsa: each sign split into 20 parts (1°30' each).
    Movable signs start from Aries; Fixed from Sagittarius; Dual from Leo.
    """
    sign = _sign_index(lon)
    span = 30.0 / 20.0
    part = int(_sign_degree(lon) / span)
    part = min(part, 19)
    modality = sign % 3
    if modality == 0:
        start = 0   # Aries
    elif modality == 1:
        start = 8   # Sagittarius
    else:
        start = 4   # Leo
    return (start + part) % 12


def _varga_d24(lon: float) -> int:
    """D24 — Chaturvimsamsa (Siddhamsa): each sign split into 24 parts (1°15' each).
    Odd signs start from Leo; even signs start from Cancer.
    """
    sign = _sign_index(lon)
    span = 30.0 / 24.0
    part = int(_sign_degree(lon) / span)
    part = min(part, 23)
    odd = (sign % 2 == 0)
    if odd:
        return (4 + part) % 12   # Leo
    else:
        return (3 + part) % 12   # Cancer


def _varga_d27(lon: float) -> int:
    """D27 — Bhamsa (Nakshatramsa): each sign split into 27 parts.
    Fire signs start from Aries; Earth from Capricorn;
    Air from Libra; Water from Cancer.
    """
    sign = _sign_index(lon)
    span = 30.0 / 27.0
    part = int(_sign_degree(lon) / span)
    part = min(part, 26)
    element = sign % 4
    starts = [0, 9, 6, 3]  # Fire→Aries, Earth→Capricorn, Air→Libra, Water→Cancer
    return (starts[element] + part) % 12


def _varga_d30(lon: float) -> int:
    """D30 — Trimsamsa: unequal divisions for odd/even signs.
    Odd signs: Mars(5°), Saturn(5°), Jupiter(8°), Mercury(7°), Venus(5°)
    Even signs: Venus(5°), Mercury(7°), Jupiter(8°), Saturn(5°), Mars(5°)
    Each ruler maps to a specific sign.
    """
    sign = _sign_index(lon)
    deg = _sign_degree(lon)
    odd = (sign % 2 == 0)

    # Ruler → sign mapping
    ruler_sign = {
        "Mars": 0,     # Aries
        "Saturn": 10,  # Aquarius
        "Jupiter": 8,  # Sagittarius
        "Mercury": 2,  # Gemini
        "Venus": 6,    # Libra
    }

    if odd:
        bounds = [(5, "Mars"), (10, "Saturn"), (18, "Jupiter"),
                  (25, "Mercury"), (30, "Venus")]
    else:
        bounds = [(5, "Venus"), (12, "Mercury"), (20, "Jupiter"),
                  (25, "Saturn"), (30, "Mars")]

    for upper, ruler in bounds:
        if deg < upper:
            return ruler_sign[ruler]
    return ruler_sign[bounds[-1][1]]


def _varga_d40(lon: float) -> int:
    """D40 — Khavedamsa: each sign split into 40 parts (0°45' each).
    Odd signs start from Aries; even signs start from Libra.
    """
    sign = _sign_index(lon)
    span = 30.0 / 40.0
    part = int(_sign_degree(lon) / span)
    part = min(part, 39)
    odd = (sign % 2 == 0)
    if odd:
        return (0 + part) % 12   # Aries
    else:
        return (6 + part) % 12   # Libra


def _varga_d45(lon: float) -> int:
    """D45 — Akshavedamsa: each sign split into 45 parts (0°40' each).
    Movable signs start from Aries; Fixed from Leo; Dual from Sagittarius.
    """
    sign = _sign_index(lon)
    span = 30.0 / 45.0
    part = int(_sign_degree(lon) / span)
    part = min(part, 44)
    modality = sign % 3
    if modality == 0:
        start = 0   # Aries
    elif modality == 1:
        start = 4   # Leo
    else:
        start = 8   # Sagittarius
    return (start + part) % 12


def _varga_d60(lon: float) -> int:
    """D60 — Shashtiamsa: each sign split into 60 parts (0°30' each).
    Always starts from the same sign.
    """
    sign = _sign_index(lon)
    span = 30.0 / 60.0
    part = int(_sign_degree(lon) / span)
    part = min(part, 59)
    return (sign + part) % 12


# Dispatch table: varga key → computation function
_VARGA_FUNCS = {
    "D1":  _varga_d1,
    "D2":  _varga_d2,
    "D3":  _varga_d3,
    "D4":  _varga_d4,
    "D5":  _varga_d5,
    "D6":  _varga_d6,
    "D7":  _varga_d7,
    "D8":  _varga_d8,
    "D9":  _varga_d9,
    "D10": _varga_d10,
    "D11": _varga_d11,
    "D12": _varga_d12,
    "D16": _varga_d16,
    "D20": _varga_d20,
    "D24": _varga_d24,
    "D27": _varga_d27,
    "D30": _varga_d30,
    "D40": _varga_d40,
    "D45": _varga_d45,
    "D60": _varga_d60,
}


# ============================================================
# 公用 API (Public API)
# ============================================================

def compute_varga_position(lon: float, varga_key: str) -> int:
    """Compute the rashi index (0–11) for a longitude in a specific varga.

    Parameters
    ----------
    lon : float
        Sidereal longitude in degrees (0–360).
    varga_key : str
        Divisional chart key, e.g. "D9", "D10".

    Returns
    -------
    int
        Rashi index (0 = Aries/Mesha, 11 = Pisces/Meena).
    """
    func = _VARGA_FUNCS.get(varga_key)
    if func is None:
        raise ValueError(f"Unknown varga key: {varga_key}")
    return func(_normalize(lon))


def compute_varga_chart(varga_key: str, planets, ascendant: float) -> VargaChart:
    """Compute a complete divisional chart for all planets.

    Parameters
    ----------
    varga_key : str
        Divisional chart key, e.g. "D9".
    planets : list
        List of VedicPlanet objects from compute_vedic_chart().
    ascendant : float
        Sidereal ascendant longitude.

    Returns
    -------
    VargaChart
        The divisional chart with all planets placed.
    """
    info = VARGA_INFO.get(varga_key, {})
    varga_planets = []
    for p in planets:
        ri = compute_varga_position(p.longitude, varga_key)
        rashi = RASHIS[ri]
        varga_planets.append(VargaPlanet(
            name=p.name,
            natal_longitude=p.longitude,
            varga_rashi_index=ri,
            varga_rashi=rashi[0],
            varga_glyph=rashi[1],
            varga_chinese=rashi[2],
            varga_lord=rashi[3],
            retrograde=getattr(p, 'retrograde', False),
        ))

    asc_ri = compute_varga_position(ascendant, varga_key)

    return VargaChart(
        key=varga_key,
        name_zh=info.get("zh", varga_key),
        name_en=info.get("en", varga_key),
        use_zh=info.get("use_zh", ""),
        division=info.get("division", 0),
        planets=varga_planets,
        ascendant_rashi_index=asc_ri,
    )


def compute_all_vargas(planets, ascendant: float) -> Dict[str, VargaChart]:
    """Compute all divisional charts (D2–D60).

    Returns
    -------
    Dict[str, VargaChart]
        Mapping from varga key to VargaChart.
    """
    result = {}
    for key in VARGA_KEYS:
        result[key] = compute_varga_chart(key, planets, ascendant)
    return result


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_varga_south_indian(varga_chart: VargaChart):
    """Render a South Indian grid for a divisional chart (SVG)."""
    import streamlit as st
    from html import escape as _esc

    si_cells = [
        (0, 0, 3), (1, 0, 2), (2, 0, 1), (3, 0, 0),
        (0, 1, 4),                         (3, 1, 11),
        (0, 2, 5),                         (3, 2, 10),
        (0, 3, 6), (1, 3, 7), (2, 3, 8), (3, 3, 9),
    ]

    # Planet colors (same as indian.py)
    PLANET_COLORS = {
        "Surya (太陽)": "#FF8C00",
        "Chandra (月亮)": "#C0C0C0",
        "Mangal (火星)": "#DC143C",
        "Budha (水星)": "#4169E1",
        "Guru (木星)": "#FFD700",
        "Shukra (金星)": "#FF69B4",
        "Shani (土星)": "#8B4513",
        "Rahu (羅睺)": "#800080",
        "Ketu (計都)": "#4B0082",
    }

    rashi_planets: Dict[int, list] = {i: [] for i in range(12)}
    for p in varga_chart.planets:
        short = p.name.split(" ")[0]
        rashi_planets[p.varga_rashi_index].append((short, p.name))

    asc_idx = varga_chart.ascendant_rashi_index
    S = 400
    cell = S // 4

    svg = [
        f'<svg viewBox="0 0 {S} {S}" xmlns="http://www.w3.org/2000/svg"'
        f' style="width:100%;max-width:{S}px;height:auto;font-family:sans-serif;">'
    ]
    svg.append(f'<rect width="{S}" height="{S}" fill="#1a1a2e" rx="4"/>')

    for i in range(5):
        svg.append(f'<line x1="{i * cell}" y1="0" x2="{i * cell}" y2="{S}" stroke="#555" stroke-width="1"/>')
        svg.append(f'<line x1="0" y1="{i * cell}" x2="{S}" y2="{i * cell}" stroke="#555" stroke-width="1"/>')

    svg.append(
        f'<rect x="{cell}" y="{cell}" width="{cell * 2}" height="{cell * 2}"'
        f' fill="#2a2a4a" stroke="#555" stroke-width="1"/>'
    )

    for col, row, ri in si_cells:
        x, y = col * cell, row * cell
        is_asc = (ri == asc_idx)
        if is_asc:
            svg.append(
                f'<rect x="{x + 1}" y="{y + 1}" width="{cell - 2}" height="{cell - 2}" fill="#3d3010"/>'
            )
        rashi = RASHIS[ri]
        cx = x + cell // 2
        marker = " ▲" if is_asc else ""
        svg.append(
            f'<text x="{cx}" y="{y + 20}" text-anchor="middle" font-size="11"'
            f' font-weight="bold" fill="#e0e0e0">{_esc(rashi[0])}{marker}</text>'
        )
        svg.append(
            f'<text x="{cx}" y="{y + 35}" text-anchor="middle" font-size="10"'
            f' fill="#888">{rashi[1]} {rashi[2]}</text>'
        )
        p_list = rashi_planets[ri]
        if p_list:
            for pi, (short, full) in enumerate(p_list):
                color = PLANET_COLORS.get(full, "#c8c8c8")
                py = y + 52 + pi * 14
                if py < y + cell - 5:
                    svg.append(
                        f'<text x="{cx}" y="{py}" text-anchor="middle" font-size="11"'
                        f' font-weight="bold" fill="{color}">{_esc(short)}</text>'
                    )
        else:
            svg.append(
                f'<text x="{cx}" y="{y + 55}" text-anchor="middle" font-size="11" fill="#666">—</text>'
            )

    # Center info
    info_cx = S // 2
    info_lines = [
        (f"{varga_chart.key} {varga_chart.name_zh}", 13, "bold", "#e0e0e0"),
        (varga_chart.name_en, 11, "normal", "#bbb"),
        (f"用途: {varga_chart.use_zh}", 10, "normal", "#999"),
    ]
    for i, (text, size, weight, color) in enumerate(info_lines):
        svg.append(
            f'<text x="{info_cx}" y="{cell + 45 + i * 25}" text-anchor="middle"'
            f' font-size="{size}" font-weight="{weight}" fill="{color}">'
            f'{_esc(text)}</text>'
        )

    svg.append('</svg>')

    st.markdown(
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        + '\n'.join(svg) + '</div>',
        unsafe_allow_html=True,
    )


def render_varga_north_indian(varga_chart: VargaChart):
    """Render a North Indian diamond chart for a divisional chart (SVG)."""
    import streamlit as st
    from html import escape as _esc

    PLANET_COLORS = {
        "Surya (太陽)": "#FF8C00",
        "Chandra (月亮)": "#C0C0C0",
        "Mangal (火星)": "#DC143C",
        "Budha (水星)": "#4169E1",
        "Guru (木星)": "#FFD700",
        "Shukra (金星)": "#FF69B4",
        "Shani (土星)": "#8B4513",
        "Rahu (羅睺)": "#800080",
        "Ketu (計都)": "#4B0082",
    }

    rashi_planets: Dict[int, list] = {i: [] for i in range(12)}
    for p in varga_chart.planets:
        short = p.name.split(" ")[0]
        rashi_planets[p.varga_rashi_index].append((short, p.name))

    asc_idx = varga_chart.ascendant_rashi_index

    S = 400
    M = S // 2
    Q = S // 4

    TL, TR, BR, BL = (0, 0), (S, 0), (S, S), (0, S)
    T, R, B, L = (M, 0), (S, M), (M, S), (0, M)
    P1, P2 = (Q, Q), (S - Q, Q)
    P3, P4 = (S - Q, S - Q), (Q, S - Q)

    _houses = [
        (0,  [T, P2, (M, M), P1],  (M, M // 2),              True),
        (1,  [TL, T, P1],          (Q - 5, Q // 3 + 4),      False),
        (2,  [TL, P1, L],          (Q // 3 + 4, Q - 5),      False),
        (3,  [P1, (M, M), P4, L],  (M // 2, M),              True),
        (4,  [L, BL, P4],          (Q // 3 + 4, S - Q + 5),  False),
        (5,  [BL, B, P4],          (Q - 5, S - Q // 3 - 4),  False),
        (6,  [(M, M), P4, B, P3],  (M, S - M // 2),          True),
        (7,  [B, BR, P3],          (S - Q + 5, S - Q // 3 - 4), False),
        (8,  [BR, R, P3],          (S - Q // 3 - 4, S - Q + 5), False),
        (9,  [(M, M), P3, R, P2],  (S - M // 2, M),          True),
        (10, [R, TR, P2],          (S - Q // 3 - 4, Q - 5),  False),
        (11, [TR, T, P2],          (S - Q + 5, Q // 3 + 4),  False),
    ]

    svg = [
        f'<svg viewBox="0 0 {S} {S}" xmlns="http://www.w3.org/2000/svg"'
        f' style="width:100%;max-width:{S}px;height:auto;font-family:sans-serif;">'
    ]
    svg.append(f'<rect width="{S}" height="{S}" fill="#1a1a2e" rx="4"/>')

    for house_num, poly, (cx, cy), is_large in _houses:
        ri = (asc_idx + house_num) % 12
        rashi = RASHIS[ri]
        is_lagna = (house_num == 0)
        fill = "#3d3010" if is_lagna else "#1e1e3a"

        pts = " ".join(f"{px},{py}" for px, py in poly)
        svg.append(
            f'<polygon points="{pts}" fill="{fill}" stroke="#555" stroke-width="1.5"/>'
        )

        fs = 11 if is_large else 9
        fs2 = 10 if is_large else 8
        lh = 14 if is_large else 12

        marker = " ▲" if is_lagna else ""
        svg.append(
            f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="{fs}"'
            f' font-weight="bold" fill="#e0e0e0">{_esc(rashi[0])}{marker}</text>'
        )
        svg.append(
            f'<text x="{cx}" y="{cy + 9}" text-anchor="middle" font-size="{fs2}"'
            f' fill="#888">{rashi[1]} {rashi[2]}</text>'
        )

        p_list = rashi_planets[ri]
        if p_list:
            tspans = " ".join(
                f'<tspan fill="{PLANET_COLORS.get(full, "#c8c8c8")}">{_esc(short)}</tspan>'
                for short, full in p_list
            )
            svg.append(
                f'<text x="{cx}" y="{cy + 9 + lh}" text-anchor="middle"'
                f' font-size="{fs}" font-weight="bold">{tspans}</text>'
            )
        else:
            svg.append(
                f'<text x="{cx}" y="{cy + 9 + lh}" text-anchor="middle"'
                f' font-size="{fs}" fill="#666">—</text>'
            )

    svg.append('</svg>')

    st.markdown(
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        + '\n'.join(svg) + '</div>',
        unsafe_allow_html=True,
    )


def render_varga_planet_table(varga_chart: VargaChart):
    """Render a planet position table for a divisional chart."""
    import streamlit as st

    header = "| Graha | Natal Longitude | Varga Rashi | Lord | R |"
    sep = "|:-----:|:---------------:|:-----------:|:----:|:-:|"
    rows = [header, sep]

    PLANET_COLORS = {
        "Surya (太陽)": "#FF8C00",
        "Chandra (月亮)": "#C0C0C0",
        "Mangal (火星)": "#DC143C",
        "Budha (水星)": "#4169E1",
        "Guru (木星)": "#FFD700",
        "Shukra (金星)": "#FF69B4",
        "Shani (土星)": "#8B4513",
        "Rahu (羅睺)": "#800080",
        "Ketu (計都)": "#4B0082",
    }

    for p in varga_chart.planets:
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        deg = _normalize(p.natal_longitude)
        d = int(deg)
        m = int((deg - d) * 60)
        s = int(((deg - d) * 60 - m) * 60)
        lon_str = f"{d}°{m:02d}'{s:02d}\""
        rows.append(
            f"| {name_html} | {lon_str} "
            f"| {p.varga_glyph} {p.varga_rashi} ({p.varga_chinese}) "
            f"| {p.varga_lord} | {retro} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def render_single_varga(varga_chart: VargaChart):
    """Render a complete single divisional chart view."""
    import streamlit as st

    st.subheader(f"📊 {varga_chart.key} — {varga_chart.name_zh}")
    st.caption(f"{varga_chart.name_en} | 用途: {varga_chart.use_zh}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**南印度盤 (South Indian)**")
        render_varga_south_indian(varga_chart)
    with col2:
        st.markdown("**北印度盤 (North Indian)**")
        render_varga_north_indian(varga_chart)

    st.divider()
    render_varga_planet_table(varga_chart)
