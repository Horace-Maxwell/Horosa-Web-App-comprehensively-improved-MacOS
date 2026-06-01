"""
astro/cross_compare.py — 跨體系比較 (Cross-System Comparison)

Unified planet positions across Western, Vedic, and Chinese systems.
Includes Sabian Symbols integration for degree-level interpretation.
"""
from dataclasses import dataclass, field
from typing import Optional

# Sabian Symbols integration
try:
    from astro.sabian import get_sabian_symbol, get_sabian_for_planet
    SABIAN_AVAILABLE = True
except ImportError:
    SABIAN_AVAILABLE = False

PLANET_NAME_MAP = {
    "Sun": ("太陽", "Sun ☉", "Surya (太陽)"),
    "Moon": ("太陰", "Moon ☽", "Chandra (月亮)"),
    "Mercury": ("水星", "Mercury ☿", "Budha (水星)"),
    "Venus": ("金星", "Venus ♀", "Shukra (金星)"),
    "Mars": ("火星", "Mars ♂", "Mangal (火星)"),
    "Jupiter": ("木星", "Jupiter ♃", "Guru (木星)"),
    "Saturn": ("土星", "Saturn ♄", "Shani (土星)"),
}

WESTERN_SIGNS_CN = {
    "Aries": "白羊座", "Taurus": "金牛座", "Gemini": "雙子座",
    "Cancer": "巨蟹座", "Leo": "獅子座", "Virgo": "處女座",
    "Libra": "天秤座", "Scorpio": "天蠍座", "Sagittarius": "射手座",
    "Capricorn": "摩羯座", "Aquarius": "水瓶座", "Pisces": "雙魚座",
}

ARMENIAN_SIGNS_HY = {
    "Aries": "Խոյ", "Taurus": "Ցուլ", "Gemini": "Երկվորյակ",
    "Cancer": "Խեցգետին", "Leo": "Առյուծ", "Virgo": "Կույս",
    "Libra": "Կշեռք", "Scorpio": "Կարիճ", "Sagittarius": "Աղեղնավոր",
    "Capricorn": "Այծեղջյուր", "Aquarius": "Ջրհոս", "Pisces": "Ձկներ",
}


@dataclass
class UnifiedPlanetPosition:
    canonical_name: str
    canonical_cn: str
    tropical_lon: float = 0.0
    sidereal_lon: float = 0.0
    western_sign: str = ""
    western_sign_cn: str = ""
    western_degree: float = 0.0
    armenian_sign_hy: str = ""
    vedic_rashi: str = ""
    vedic_rashi_cn: str = ""
    nakshatra: str = ""
    chinese_sign: str = ""
    mansion_chinese: str = ""
    # Sabian Symbol fields
    sabian_degree: int = 0
    sabian_symbol: str = ""
    sabian_keyword: str = ""


@dataclass
class CrossCompareResult:
    planets: list = field(default_factory=list)
    ayanamsa: float = 0.0
    tropical_asc: str = ""
    sidereal_asc: str = ""
    chinese_ming: str = ""
    summary_en: str = ""
    summary_cn: str = ""
    # Sabian Symbols summary
    sabian_summary: Optional[str] = None


def _find_planet(planets, target_names):
    """Find planet by name substring matching."""
    for p in planets:
        for t in target_names:
            if t in p.name:
                return p
    return None


def compute_cross_comparison(chinese_chart, western_chart, vedic_chart, include_sabian: bool = True):
    """Unify planet positions across three chart systems.
    
    Parameters
    ----------
    chinese_chart : Any
        Chinese astrology chart data.
    western_chart : Any
        Western astrology chart data.
    vedic_chart : Any
        Vedic astrology chart data.
    include_sabian : bool, optional
        If True, include Sabian Symbols for each planet. Default is True.
    
    Returns
    -------
    CrossCompareResult
        Unified comparison result with optional Sabian Symbols.
    """
    results = []
    sabian_notes = []

    for canonical, (cn_name, w_name, v_name) in PLANET_NAME_MAP.items():
        w_planet = _find_planet(western_chart.planets, [w_name, canonical])
        v_planet = _find_planet(vedic_chart.planets, [v_name, canonical])
        c_planet = _find_planet(chinese_chart.planets, [cn_name])

        up = UnifiedPlanetPosition(
            canonical_name=canonical, canonical_cn=cn_name,
        )
        if w_planet:
            up.tropical_lon = round(w_planet.longitude, 4)
            up.western_sign = getattr(w_planet, 'sign', '')
            up.western_sign_cn = WESTERN_SIGNS_CN.get(up.western_sign, '')
            up.western_degree = round(w_planet.longitude % 30, 2)
            up.armenian_sign_hy = ARMENIAN_SIGNS_HY.get(up.western_sign, "")
            
            # Add Sabian Symbol
            if include_sabian and SABIAN_AVAILABLE:
                sabian = get_sabian_symbol(w_planet.longitude)
                up.sabian_degree = sabian.get('degree', 0)
                up.sabian_symbol = sabian.get('symbol', '')
                up.sabian_keyword = sabian.get('keyword', '')
                sabian_notes.append(f"{canonical}: {sabian.get('keyword', '')}")
        if v_planet:
            up.sidereal_lon = round(v_planet.longitude, 4)
            up.vedic_rashi = getattr(v_planet, 'rashi', '')
            up.nakshatra = getattr(v_planet, 'nakshatra', '')
        if c_planet:
            up.chinese_sign = getattr(c_planet, 'sign_chinese', '')
            up.mansion_chinese = getattr(c_planet, 'mansion', '')

        results.append(up)

    ayanamsa = getattr(vedic_chart, 'ayanamsa', 0.0)

    return CrossCompareResult(
        planets=results, ayanamsa=round(ayanamsa, 4),
        tropical_asc=getattr(western_chart, 'asc_sign', ''),
        sidereal_asc=getattr(vedic_chart, 'asc_rashi', ''),
        chinese_ming="",
        summary_en=f"Comparing {len(results)} planets across 3 systems (ayanamsa={ayanamsa:.2f}°)",
        summary_cn=f"跨 3 個體系比較 {len(results)} 顆行星（歲差={ayanamsa:.2f}°）",
        sabian_summary="; ".join(sabian_notes) if sabian_notes else None,
    )


def render_cross_comparison(result):
    """Render cross-comparison in Streamlit."""
    import streamlit as st

    st.subheader("🔀 Cross-System Comparison / 跨體系比較")
    st.info(result.summary_cn if st.session_state.get("lang") == "zh" else result.summary_en)

    data = []
    for p in result.planets:
        data.append({
            "Planet": f"{p.canonical_name} ({p.canonical_cn})",
            "Western": f"{p.western_sign} {p.western_degree:.1f}°" if p.western_sign else "—",
            "Vedic": p.vedic_rashi or "—",
            "Nakshatra": p.nakshatra or "—",
            "Chinese": p.chinese_sign or "—",
            "Armenian": p.armenian_sign_hy or "—",
        })
    if data:
        st.dataframe(data, width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Ayanamsa", f"{result.ayanamsa:.4f}°")
    with col2:
        st.metric("Western Asc", result.tropical_asc)


# ============================================================
# Babylonian cross-comparison helper
# ============================================================
BABYLONIAN_AKKADIAN_SIGNS = [
    "LU.HUN.GA", "GU4.AN.NA", "MAŠ.TAB.BA.GAL.GAL", "ALLA",
    "UR.GU.LA", "AB.SIN", "ZI.BA.AN.NA", "GIR.TAB",
    "PA.BIL.SAG", "SUḪUR.MAŠ", "GU", "ZIB.ME",
]

BABYLONIAN_PLANET_GODS_MAP = {
    "Sun": "Shamash", "Moon": "Sin", "Mercury": "Nabu",
    "Venus": "Ishtar", "Mars": "Nergal", "Jupiter": "Marduk",
    "Saturn": "Ninurta",
}


def add_babylonian_to_comparison(result, babylonian_chart):
    """Augment a CrossCompareResult with Babylonian sidereal positions.

    Parameters
    ----------
    result : CrossCompareResult
    babylonian_chart : BabylonianChart (from astro.babylonian)

    Returns
    -------
    CrossCompareResult — same object, with Babylonian columns added to each
    UnifiedPlanetPosition (attributes: ``babylonian_akkadian``,
    ``babylonian_degree``, ``babylonian_god``).
    """
    if babylonian_chart is None:
        return result

    planet_map = {}
    for pos in getattr(babylonian_chart, "positions", []):
        planet_map[pos.name] = pos

    for up in result.planets:
        bpos = planet_map.get(up.canonical_name)
        if bpos:
            up.babylonian_akkadian = bpos.sign_akkadian
            up.babylonian_degree = bpos.sign_degree
            up.babylonian_god = BABYLONIAN_PLANET_GODS_MAP.get(
                up.canonical_name, "")
        else:
            up.babylonian_akkadian = ""
            up.babylonian_degree = 0.0
            up.babylonian_god = ""

    bab_asc_idx = int(getattr(babylonian_chart, "ascendant", 0) / 30) % 12  # 30° per sign
    result.babylonian_asc = BABYLONIAN_AKKADIAN_SIGNS[bab_asc_idx]
    return result


# ============================================================
# Celtic Tree Calendar cross-comparison helper (Graves 1948)
# ============================================================

def add_celtic_tree_to_comparison(result, celtic_chart):
    """Augment a CrossCompareResult with Celtic Tree Calendar data (Graves 1948).

    Adds a ``celtic_tree`` attribute to the result containing a summary
    dict for display alongside planet positions.

    Parameters
    ----------
    result : CrossCompareResult
    celtic_chart : CelticTreeChart (from astro.celtic.celtic_tree_graves)

    Returns
    -------
    CrossCompareResult — same object, with ``celtic_tree`` attribute added.
    """
    if celtic_chart is None:
        return result

    result.celtic_tree = {
        "month_number": celtic_chart.month_number,
        "gaelic": celtic_chart.tree_name_gaelic,
        "english": celtic_chart.tree_name_english,
        "chinese": celtic_chart.tree_name_chinese,
        "ogham": celtic_chart.ogham_letter,
        "date_range_en": celtic_chart.date_range_en,
        "date_range_zh": celtic_chart.date_range_zh,
        "qualities_en": celtic_chart.qualities_en,
        "qualities_zh": celtic_chart.qualities_zh,
        "western_overlap_en": celtic_chart.western_overlap_en,
        "western_overlap_zh": celtic_chart.western_overlap_zh,
        "note_en": celtic_chart.note_en,
        "note_zh": celtic_chart.note_zh,
    }
    return result


def render_celtic_tree_comparison(celtic_chart) -> None:
    """Render a Celtic Tree Calendar cross-comparison section in Streamlit.

    Shows how the birth tree-month aligns with Western zodiac signs and
    provides a clear Graves attribution notice.

    Parameters
    ----------
    celtic_chart : CelticTreeChart
    """
    import streamlit as st

    lang = st.session_state.get("lang", "zh")
    is_zh = lang in ("zh", "zh_cn")

    st.subheader(
        "🌿 凱爾特樹木曆 × 西洋占星 交叉比對 (Graves 1948)"
        if is_zh else
        "🌿 Celtic Tree Calendar × Western Astrology Cross-Reference (Graves 1948)"
    )

    st.caption(
        celtic_chart.note_zh if is_zh else celtic_chart.note_en
    )

    col1, col2 = st.columns(2)
    with col1:
        if is_zh:
            st.metric(
                "樹木月份 Tree Month",
                f"#{celtic_chart.month_number} {celtic_chart.tree_name_gaelic}",
                help=f"{celtic_chart.tree_name_english} / {celtic_chart.tree_name_chinese}",
            )
        else:
            st.metric(
                "Tree Month",
                f"#{celtic_chart.month_number} {celtic_chart.tree_name_gaelic}",
                help=f"{celtic_chart.tree_name_english} / {celtic_chart.tree_name_chinese}",
            )
    with col2:
        if is_zh:
            st.metric(
                "西洋占星重疊 Western Zodiac Overlap",
                celtic_chart.western_overlap_zh or "—",
                help=celtic_chart.western_overlap_en,
            )
        else:
            st.metric(
                "Western Zodiac Overlap",
                celtic_chart.western_overlap_en or "—",
            )

    import pandas as pd
    data = {
        ("歐甘字 / Ogham" if is_zh else "Ogham Letter"): celtic_chart.ogham_letter,
        ("格里曆日期 / Date Range" if is_zh else "Date Range"): (
            celtic_chart.date_range_zh if is_zh else celtic_chart.date_range_en
        ),
        ("詩意屬性 / Qualities" if is_zh else "Poetic Qualities"): (
            celtic_chart.qualities_zh if is_zh else celtic_chart.qualities_en
        ),
    }
    st.table(pd.DataFrame.from_dict(data, orient="index", columns=["值" if is_zh else "Value"]))



# TODO: Call this helper from the multi-system UI pipeline when Armenian chart
# data is included in a comparison payload.
def add_armenian_to_comparison(result, armenian_chart):
    """Augment CrossCompareResult with Armenian sign labels from ArmenianChart."""
    if armenian_chart is None:
        return result

    planet_map = {}
    for p in getattr(armenian_chart, "planets", []):
        k = p.name.split(" ")[0]
        planet_map[k] = p

    for up in result.planets:
        ap = planet_map.get(up.canonical_name)
        if ap:
            up.armenian_sign_hy = getattr(ap, "sign_hy", up.armenian_sign_hy)
    return result
