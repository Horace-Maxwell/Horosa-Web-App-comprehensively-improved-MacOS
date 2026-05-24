"""
astro/context_serializer.py — Structured XML Context Serializer for LLM Analysis

Converts kinastro chart data (any system) into well-formed, fact-only XML that
can be fed directly to LLMs (Cerebras / Grok / DeepSeek / etc.) as structured
context.  No interpretations are included; only raw computed facts.

Usage
-----
    from astro.context_serializer import to_context

    # Single system
    xml_str = to_context(chart, system="western")

    # All systems from a session-state-style dict
    xml_str = to_context({"western": western_chart, "ziwei": ziwei_chart}, system="all")

    # Auto-detect single object
    xml_str = to_context(western_chart)

Public API
----------
    to_context(chart_data, system="all") -> str
        Returns a well-formed UTF-8 XML string with root element <kinastro_context>.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SYSTEM_TAG_MAP = {
    # tab key → XML tag suffix
    "tab_western":     "western",
    "tab_chinese":     "qizheng",
    "tab_ziwei":       "ziwei",
    "tab_indian":      "vedic",
    "tab_sukkayodo":   "sukkayodo",
    "tab_thai":        "thai",
    "tab_kabbalistic": "kabbalistic",
    "tab_arabic":      "arabic",
    "tab_maya":        "maya",
    "tab_aztec":       "aztec",
    "tab_mahabote":    "mahabote",
    "tab_decans":      "decans",
    "tab_nadi":        "nadi",
    "tab_zurkhai":     "zurkhai",
    "tab_hellenistic": "hellenistic",
    "tab_chinstar":    "chinstar",
    "tab_twelve_ci":   "twelve_ci",
    "tab_acg":         "acg",
    "tab_nine_star_ki": "nine_star_ki",
    "tab_celtic_tree": "celtic_tree",
    "tab_sanshi":      "sanshi",
    "tab_qimen":       "qimen",
    "tab_liuren":      "liuren",
    "tab_fendjing":    "fendjing",
    "tab_tojeong":     "tojeong",
    "tab_taiyi":       "taiyi",
    # plain keys (without "tab_" prefix) are also accepted
    "western":     "western",
    "qizheng":     "qizheng",
    "ziwei":       "ziwei",
    "vedic":       "vedic",
    "sukkayodo":   "sukkayodo",
    "thai":        "thai",
    "kabbalistic": "kabbalistic",
    "arabic":      "arabic",
    "maya":        "maya",
    "aztec":       "aztec",
    "mahabote":    "mahabote",
    "decans":      "decans",
    "nadi":        "nadi",
    "zurkhai":     "zurkhai",
    "hellenistic": "hellenistic",
    "chinstar":    "chinstar",
    "twelve_ci":   "twelve_ci",
    "acg":         "acg",
    "nine_star_ki": "nine_star_ki",
    "celtic_tree": "celtic_tree",
    "sanshi":      "sanshi",
    "qimen":       "qimen",
    "liuren":      "liuren",
}


def _safe_str(value: Any) -> str:
    """Convert value to a clean string safe for XML attribute/text content."""
    if value is None:
        return ""
    if isinstance(value, float):
        # round to 4 decimal places to keep XML compact
        return f"{value:.4f}"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).strip()


def _set_attr(element: ET.Element, key: str, value: Any) -> None:
    """Set an XML attribute, skipping empty values."""
    v = _safe_str(value)
    if v:
        element.set(key, v)


def _sub(parent: ET.Element, tag: str, **attrs: Any) -> ET.Element:
    """Create a child element with optional attributes."""
    child = ET.SubElement(parent, tag)
    for k, v in attrs.items():
        _set_attr(child, k, v)
    return child


def _text_sub(parent: ET.Element, tag: str, text: Any, **attrs: Any) -> ET.Element:
    """Create a child element whose text content is *text*."""
    child = _sub(parent, tag, **attrs)
    s = _safe_str(text)
    if s:
        child.text = s
    return child


def _obj_to_elem(parent: ET.Element, tag: str, obj: Any, depth: int = 0) -> None:
    """Recursively serialise an arbitrary object/dict/list into XML children."""
    if depth > 6:
        _text_sub(parent, tag, obj)
        return

    if isinstance(obj, dict):
        elem = ET.SubElement(parent, tag)
        for k, v in obj.items():
            safe_key = _xml_tag(k)
            _obj_to_elem(elem, safe_key, v, depth + 1)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _obj_to_elem(parent, tag, item, depth + 1)
    elif hasattr(obj, "__dict__") and not callable(obj):
        elem = ET.SubElement(parent, tag)
        for attr, val in sorted(vars(obj).items()):
            if attr.startswith("_") or callable(val):
                continue
            safe_key = _xml_tag(attr)
            _obj_to_elem(elem, safe_key, val, depth + 1)
    else:
        _text_sub(parent, tag, obj)


def _xml_tag(name: str) -> str:
    """Convert arbitrary string to a valid XML element name."""
    # Replace spaces and common problematic chars
    tag = name.strip().replace(" ", "_").replace("/", "_").replace(".", "_")
    tag = tag.replace("(", "").replace(")", "").replace(":", "_").replace("-", "_")
    # XML tags cannot start with a digit
    if tag and tag[0].isdigit():
        tag = "n_" + tag
    # Fallback for empty
    return tag or "item"


# ---------------------------------------------------------------------------
# Per-system serialisers
# ---------------------------------------------------------------------------

def _serialize_planet_list(parent: ET.Element, planets: list, tag: str = "planets") -> None:
    """Serialise a list of planet objects under a <planets> element."""
    if not planets:
        return
    planets_elem = ET.SubElement(parent, tag)
    for p in planets:
        if isinstance(p, dict):
            pe = ET.SubElement(planets_elem, "planet")
            for k, v in p.items():
                _set_attr(pe, _xml_tag(k), v)
        elif hasattr(p, "__dict__"):
            pe = ET.SubElement(planets_elem, "planet")
            for attr, val in sorted(vars(p).items()):
                if attr.startswith("_") or callable(val):
                    continue
                _set_attr(pe, _xml_tag(attr), val)
        else:
            _text_sub(planets_elem, "planet", p)


def _serialize_house_list(parent: ET.Element, houses: list, tag: str = "houses") -> None:
    """Serialise a list of house objects under a <houses> element."""
    if not houses:
        return
    houses_elem = ET.SubElement(parent, tag)
    for h in houses:
        if isinstance(h, dict):
            he = ET.SubElement(houses_elem, "house")
            for k, v in h.items():
                if k == "planets":
                    _serialize_planet_list(he, v)
                else:
                    _set_attr(he, _xml_tag(k), v)
        elif hasattr(h, "__dict__"):
            he = ET.SubElement(houses_elem, "house")
            for attr, val in sorted(vars(h).items()):
                if attr.startswith("_") or callable(val):
                    continue
                if attr == "planets":
                    _serialize_planet_list(he, val)
                else:
                    _set_attr(he, _xml_tag(attr), val)
        else:
            _text_sub(houses_elem, "house", h)


def _serialize_aspect_list(parent: ET.Element, aspects: list) -> None:
    """Serialise a list of aspect objects under an <aspects> element."""
    if not aspects:
        return
    asp_elem = ET.SubElement(parent, "aspects")
    for a in aspects:
        if isinstance(a, dict):
            ae = ET.SubElement(asp_elem, "aspect")
            for k, v in a.items():
                _set_attr(ae, _xml_tag(k), v)
        elif hasattr(a, "__dict__"):
            ae = ET.SubElement(asp_elem, "aspect")
            for attr, val in sorted(vars(a).items()):
                if attr.startswith("_") or callable(val):
                    continue
                _set_attr(ae, _xml_tag(attr), val)
        else:
            _text_sub(asp_elem, "aspect", a)


def _g(obj: Any, *attrs: str, default: str = "") -> str:
    """Get first non-empty attribute from object or dict."""
    for attr in attrs:
        if isinstance(obj, dict):
            val = obj.get(attr)
        else:
            val = getattr(obj, attr, None)
        if val is not None and str(val).strip():
            return str(val).strip()
    return default


# ---- Western ---------------------------------------------------------------

def _serialize_western(parent: ET.Element, chart: Any) -> None:
    """Serialise a Western astrology chart."""
    _set_attr(parent, "asc_sign", _g(chart, "asc_sign"))
    _set_attr(parent, "mc_sign", _g(chart, "mc_sign"))
    _set_attr(parent, "ascendant", _g(chart, "ascendant"))
    _set_attr(parent, "midheaven", _g(chart, "midheaven"))
    _set_attr(parent, "julian_day", _g(chart, "julian_day"))
    _set_attr(parent, "latitude", _g(chart, "latitude"))
    _set_attr(parent, "longitude", _g(chart, "longitude"))
    _set_attr(parent, "timezone", _g(chart, "timezone"))
    _set_attr(parent, "sect", _g(chart, "sect"))
    _set_attr(parent, "zodiac_type", _g(chart, "zodiac_type"))

    _serialize_planet_list(parent, _g_list(chart, "planets"))
    _serialize_house_list(parent, _g_list(chart, "houses"))
    _serialize_aspect_list(parent, _g_list(chart, "aspects"))

    # Arabic parts
    arabic_parts = _g_list(chart, "arabic_parts")
    if arabic_parts:
        ap_elem = ET.SubElement(parent, "arabic_parts")
        for ap in arabic_parts:
            ape = ET.SubElement(ap_elem, "lot")
            if isinstance(ap, dict):
                for k, v in ap.items():
                    _set_attr(ape, _xml_tag(k), v)
            elif hasattr(ap, "__dict__"):
                for attr, val in sorted(vars(ap).items()):
                    if not attr.startswith("_") and not callable(val):
                        _set_attr(ape, _xml_tag(attr), val)


def _g_list(obj: Any, attr: str) -> list:
    """Safely get a list attribute."""
    if isinstance(obj, dict):
        val = obj.get(attr, [])
    else:
        val = getattr(obj, attr, [])
    return val if isinstance(val, (list, tuple)) else []


# ---- Vedic (Indian) --------------------------------------------------------

def _serialize_vedic(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "lagna", _g(chart, "lagna", "asc_rashi"))
    _set_attr(parent, "ayanamsa", _g(chart, "ayanamsa"))
    _set_attr(parent, "julian_day", _g(chart, "julian_day"))
    _set_attr(parent, "latitude", _g(chart, "latitude"))
    _set_attr(parent, "longitude", _g(chart, "longitude"))

    _serialize_planet_list(parent, _g_list(chart, "planets"))
    _serialize_house_list(parent, _g_list(chart, "houses"))
    _serialize_aspect_list(parent, _g_list(chart, "aspects"))

    # Nakshatras
    nakshatras = _g_list(chart, "nakshatras")
    if nakshatras:
        nk_elem = ET.SubElement(parent, "nakshatras")
        for nk in nakshatras:
            nke = ET.SubElement(nk_elem, "nakshatra")
            if isinstance(nk, dict):
                for k, v in nk.items():
                    _set_attr(nke, _xml_tag(k), v)
            elif hasattr(nk, "__dict__"):
                for attr, val in sorted(vars(nk).items()):
                    if not attr.startswith("_") and not callable(val):
                        _set_attr(nke, _xml_tag(attr), val)

    # Dasha
    dasha = _g(chart, "dasha")
    if dasha:
        _text_sub(parent, "dasha", dasha)
    dasha_sequence = _g_list(chart, "dasha_sequence")
    if dasha_sequence:
        ds_elem = ET.SubElement(parent, "dasha_sequence")
        for d in dasha_sequence:
            _obj_to_elem(ds_elem, "period", d)


# ---- Qizheng (七政四餘) ----------------------------------------------------

def _serialize_qizheng(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "ming_gong", _g(chart, "ming_gong", "ming_gong_branch"))
    _set_attr(parent, "shen_gong", _g(chart, "shen_gong", "shen_gong_branch"))
    _set_attr(parent, "year", _g(chart, "year"))
    _set_attr(parent, "month", _g(chart, "month"))
    _set_attr(parent, "day", _g(chart, "day"))
    _set_attr(parent, "hour", _g(chart, "hour"))
    _set_attr(parent, "gender", _g(chart, "gender"))
    _set_attr(parent, "location", _g(chart, "location_name"))

    bazi = _g_obj(chart, "bazi")
    if bazi:
        bazi_elem = ET.SubElement(parent, "bazi")
        _set_attr(bazi_elem, "year", _g(bazi, "year"))
        _set_attr(bazi_elem, "month", _g(bazi, "month"))
        _set_attr(bazi_elem, "day", _g(bazi, "day"))
        _set_attr(bazi_elem, "hour", _g(bazi, "hour"))

    _serialize_planet_list(parent, _g_list(chart, "planets"))
    _serialize_house_list(parent, _g_list(chart, "houses"))
    _serialize_aspect_list(parent, _g_list(chart, "aspects"))


def _g_obj(obj: Any, attr: str) -> Any:
    """Safely get a sub-object attribute."""
    if isinstance(obj, dict):
        return obj.get(attr)
    return getattr(obj, attr, None)


# ---- Ziwei (紫微斗數) -------------------------------------------------------

def _serialize_ziwei(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "ming_gong", _g(chart, "ming_gong"))
    _set_attr(parent, "shen_gong", _g(chart, "shen_gong"))
    _set_attr(parent, "ming_zhu", _g(chart, "ming_zhu"))
    _set_attr(parent, "shen_zhu", _g(chart, "shen_zhu"))
    _set_attr(parent, "wuxing_ju", _g(chart, "wuxing_ju"))
    _set_attr(parent, "year_stem", _g(chart, "year_stem"))
    _set_attr(parent, "year_branch", _g(chart, "year_branch"))
    _set_attr(parent, "gender", _g(chart, "gender"))

    palaces = _g_list(chart, "palaces")
    if palaces:
        palaces_elem = ET.SubElement(parent, "palaces")
        for pal in palaces:
            pe = ET.SubElement(palaces_elem, "palace")
            if isinstance(pal, dict):
                for k, v in pal.items():
                    if k in ("stars", "star_list", "minor_stars", "shensha"):
                        _obj_to_elem(pe, _xml_tag(k), v)
                    else:
                        _set_attr(pe, _xml_tag(k), v)
            elif hasattr(pal, "__dict__"):
                for attr, val in sorted(vars(pal).items()):
                    if attr.startswith("_") or callable(val):
                        continue
                    if attr in ("stars", "star_list", "minor_stars", "shensha"):
                        _obj_to_elem(pe, attr, val)
                    else:
                        _set_attr(pe, attr, val)

    # 四化
    sihua = _g_list(chart, "sihua")
    if sihua:
        sh_elem = ET.SubElement(parent, "sihua")
        for s in sihua:
            _obj_to_elem(sh_elem, "transformation", s)

    # 大運 / 小限
    dayun = _g_list(chart, "dayun")
    if dayun:
        dy_elem = ET.SubElement(parent, "dayun")
        for d in dayun:
            _obj_to_elem(dy_elem, "period", d)


# ---- Thai ------------------------------------------------------------------

def _serialize_thai(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "weekday", _g(chart, "weekday", "birth_weekday"))
    _set_attr(parent, "lagna", _g(chart, "lagna"))
    _serialize_planet_list(parent, _g_list(chart, "planets"))
    _serialize_house_list(parent, _g_list(chart, "houses"))


# ---- Kabbalistic -----------------------------------------------------------

def _serialize_kabbalistic(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "life_path", _g(chart, "life_path"))
    _set_attr(parent, "name_number", _g(chart, "name_number"))
    _set_attr(parent, "hebrew_letter", _g(chart, "hebrew_letter"))
    _set_attr(parent, "sephirah", _g(chart, "sephirah"))
    _set_attr(parent, "tree_path", _g(chart, "tree_path"))
    _serialize_planet_list(parent, _g_list(chart, "planets"))


# ---- Arabic ----------------------------------------------------------------

def _serialize_arabic(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "lot_of_fortune", _g(chart, "lot_of_fortune"))
    _serialize_planet_list(parent, _g_list(chart, "planets"))
    arabic_parts = _g_list(chart, "arabic_parts")
    if arabic_parts:
        ap_elem = ET.SubElement(parent, "arabic_parts")
        for ap in arabic_parts:
            ape = ET.SubElement(ap_elem, "lot")
            if isinstance(ap, dict):
                for k, v in ap.items():
                    _set_attr(ape, _xml_tag(k), v)
            elif hasattr(ap, "__dict__"):
                for attr, val in sorted(vars(ap).items()):
                    if not attr.startswith("_") and not callable(val):
                        _set_attr(ape, _xml_tag(attr), val)


# ---- Maya ------------------------------------------------------------------

def _serialize_maya(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "kin", _g(chart, "kin"))
    _set_attr(parent, "tzolkin", _g(chart, "tzolkin"))
    _set_attr(parent, "haab", _g(chart, "haab"))
    _set_attr(parent, "tone", _g(chart, "tone"))
    _set_attr(parent, "glyph", _g(chart, "glyph", "day_sign"))
    _set_attr(parent, "long_count", _g(chart, "long_count"))
    _set_attr(parent, "wavespell", _g(chart, "wavespell"))
    _set_attr(parent, "oracle", _g(chart, "oracle"))


# ---- Aztec -----------------------------------------------------------------

def _serialize_aztec(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "tonalpohualli_number", _g(chart, "tonalpohualli_number"))
    _set_attr(parent, "tonalpohualli_sign", _g(chart, "tonalpohualli_sign_name"))
    _set_attr(parent, "tonalpohualli_cn", _g(chart, "tonalpohualli_sign_cn"))
    _set_attr(parent, "tonalpohualli_en", _g(chart, "tonalpohualli_sign_en"))
    _set_attr(parent, "energy", _g(chart, "tonalpohualli_energy"))
    _set_attr(parent, "trecena_ruler", _g(chart, "trecena_ruler_name"))
    _set_attr(parent, "trecena_ruler_cn", _g(chart, "trecena_ruler_cn"))
    _set_attr(parent, "deity", _g(chart, "deity"))
    _set_attr(parent, "direction_cn", _g(chart, "direction_cn"))
    _set_attr(parent, "direction_en", _g(chart, "direction_en"))
    _set_attr(parent, "color_cn", _g(chart, "color_cn"))
    _set_attr(parent, "color_en", _g(chart, "color_en"))


# ---- Mahabote (Myanmar) ----------------------------------------------------

def _serialize_mahabote(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "birth_weekday", _g(chart, "birth_weekday"))
    _set_attr(parent, "birth_animal_en", _g(chart, "birth_animal_en"))
    _set_attr(parent, "birth_animal_cn", _g(chart, "birth_animal_cn"))
    _serialize_house_list(parent, _g_list(chart, "houses"))


# ---- Decans (Egyptian) -----------------------------------------------------

def _serialize_decans(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "sun_decan", _g(chart, "sun_decan"))
    _set_attr(parent, "moon_decan", _g(chart, "moon_decan"))
    _set_attr(parent, "asc_decan", _g(chart, "asc_decan"))
    _serialize_planet_list(parent, _g_list(chart, "planets"))
    decans = _g_list(chart, "decans")
    if decans:
        de_elem = ET.SubElement(parent, "decan_list")
        for d in decans:
            _obj_to_elem(de_elem, "decan", d)


# ---- Nadi ------------------------------------------------------------------

def _serialize_nadi(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "nadi_type", _g(chart, "nadi_type"))
    _set_attr(parent, "nakshatra", _g(chart, "birth_nakshatra", "nakshatra"))
    _serialize_planet_list(parent, _g_list(chart, "planets"))


# ---- Zurkhai (Mongolian) ---------------------------------------------------

def _serialize_zurkhai(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "animal", _g(chart, "animal", "birth_animal"))
    _set_attr(parent, "element", _g(chart, "element", "birth_element"))
    _set_attr(parent, "mewa", _g(chart, "mewa"))
    _set_attr(parent, "parkha", _g(chart, "parkha"))
    _serialize_planet_list(parent, _g_list(chart, "planets"))


# ---- Hellenistic -----------------------------------------------------------

def _serialize_hellenistic(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "asc_sign", _g(chart, "asc_sign"))
    _set_attr(parent, "mc_sign", _g(chart, "mc_sign"))
    _set_attr(parent, "sect", _g(chart, "sect"))
    _set_attr(parent, "lot_of_fortune", _g(chart, "lot_of_fortune"))
    _serialize_planet_list(parent, _g_list(chart, "planets"))
    _serialize_aspect_list(parent, _g_list(chart, "aspects"))
    # Lots
    lots = _g_list(chart, "lots")
    if lots:
        lots_elem = ET.SubElement(parent, "lots")
        for lot in lots:
            _obj_to_elem(lots_elem, "lot", lot)


# ---- Chinstar (萬花仙禽) ----------------------------------------------------

def _serialize_chinstar(parent: ET.Element, chart: Any) -> None:
    if isinstance(chart, dict):
        for k, v in chart.items():
            _obj_to_elem(parent, _xml_tag(k), v)
    else:
        _serialize_generic(parent, chart, "chinstar")


# ---- Sukkayodo (宿曜道) ----------------------------------------------------

def _serialize_sukkayodo(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "birth_mansion", _g(chart, "birth_mansion", "mansion"))
    _serialize_planet_list(parent, _g_list(chart, "planets"))
    mansions = _g_list(chart, "mansions")
    if mansions:
        ms_elem = ET.SubElement(parent, "mansions")
        for m in mansions:
            _obj_to_elem(ms_elem, "mansion", m)


# ---- Twelve Ci (十二次) -----------------------------------------------------

def _serialize_twelve_ci(parent: ET.Element, chart: Any) -> None:
    _serialize_generic(parent, chart, "twelve_ci")


# ---- Astrocartography (ACG) ------------------------------------------------

def _serialize_acg(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "query_location", _g(chart, "query_location", "location"))
    _set_attr(parent, "latitude", _g(chart, "latitude", "query_lat"))
    _set_attr(parent, "longitude", _g(chart, "longitude", "query_lon"))
    lines = _g_list(chart, "lines")
    if lines:
        lines_elem = ET.SubElement(parent, "lines")
        for line in lines:
            _obj_to_elem(lines_elem, "line", line)
    crossings = _g_list(chart, "crossings")
    if crossings:
        cx_elem = ET.SubElement(parent, "crossings")
        for cx in crossings:
            _obj_to_elem(cx_elem, "crossing", cx)


# ---- Nine Star Ki (九星氣學) ------------------------------------------------

def _serialize_nine_star_ki(parent: ET.Element, chart: Any) -> None:
    _set_attr(parent, "year_star", _g(chart, "year_star"))
    _set_attr(parent, "month_star", _g(chart, "month_star"))
    _set_attr(parent, "day_star", _g(chart, "day_star"))
    _set_attr(parent, "adjusted_year", _g(chart, "adjusted_year"))
    _set_attr(parent, "li_chun_date", _g(chart, "li_chun_date"))
    _set_attr(parent, "current_year_star", _g(chart, "current_year_star"))
    _set_attr(parent, "current_year_month_star", _g(chart, "current_year_month_star"))

    for star_key in ("year_star_info", "month_star_info", "day_star_info"):
        info = _g_obj(chart, star_key)
        if info and isinstance(info, dict):
            si_elem = ET.SubElement(parent, star_key)
            for k, v in info.items():
                _set_attr(si_elem, _xml_tag(k), v)

    compat = _g_list(chart, "compatibility")
    if compat:
        compat_elem = ET.SubElement(parent, "compatibility")
        for c in compat:
            _obj_to_elem(compat_elem, "entry", c)


# ---- Celtic Tree Calendar --------------------------------------------------

def _serialize_celtic_tree(parent: ET.Element, chart: Any) -> None:
    _serialize_generic(parent, chart, "celtic_tree")


# ---- Sanshi / Qimen / Liuren (三式) ----------------------------------------

def _serialize_sanshi(parent: ET.Element, chart: Any) -> None:
    _serialize_generic(parent, chart, "sanshi")


def _serialize_qimen(parent: ET.Element, chart: Any) -> None:
    _serialize_generic(parent, chart, "qimen")


def _serialize_liuren(parent: ET.Element, chart: Any) -> None:
    _serialize_generic(parent, chart, "liuren")


# ---- Generic fallback -------------------------------------------------------

def _serialize_generic(parent: ET.Element, chart: Any, system_name: str = "unknown") -> None:
    """Generic serialiser: dump all public attributes as XML children."""
    if isinstance(chart, dict):
        for k, v in chart.items():
            _obj_to_elem(parent, _xml_tag(k), v)
    else:
        for attr in sorted(dir(chart)):
            if attr.startswith("_"):
                continue
            val = getattr(chart, attr, None)
            if callable(val):
                continue
            _obj_to_elem(parent, _xml_tag(attr), val)


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

_SERIALIZERS = {
    "western":      _serialize_western,
    "qizheng":      _serialize_qizheng,
    "ziwei":        _serialize_ziwei,
    "vedic":        _serialize_vedic,
    "sukkayodo":    _serialize_sukkayodo,
    "thai":         _serialize_thai,
    "kabbalistic":  _serialize_kabbalistic,
    "arabic":       _serialize_arabic,
    "maya":         _serialize_maya,
    "aztec":        _serialize_aztec,
    "mahabote":     _serialize_mahabote,
    "decans":       _serialize_decans,
    "nadi":         _serialize_nadi,
    "zurkhai":      _serialize_zurkhai,
    "hellenistic":  _serialize_hellenistic,
    "chinstar":     _serialize_chinstar,
    "twelve_ci":    _serialize_twelve_ci,
    "acg":          _serialize_acg,
    "nine_star_ki": _serialize_nine_star_ki,
    "celtic_tree":  _serialize_celtic_tree,
    "sanshi":       _serialize_sanshi,
    "qimen":        _serialize_qimen,
    "liuren":       _serialize_liuren,
}


def _resolve_tag(key: str) -> str:
    """Map a user-supplied key to the canonical tag name."""
    return _SYSTEM_TAG_MAP.get(key, key.replace("tab_", "").lower())


def _indent(elem: ET.Element, level: int = 0) -> None:
    """Add pretty-print indentation to an ElementTree in-place (Python < 3.9 compat)."""
    indent = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        last_child = None
        for child in elem:
            _indent(child, level + 1)
            last_child = child
        # Fix last child tail
        if last_child is not None and (not last_child.tail or not last_child.tail.strip()):
            last_child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent
    if not level:
        elem.tail = "\n"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _serialize_sabian_symbols(parent: ET.Element, chart: Any) -> None:
    """Serialise Sabian Symbols for planets in the chart.
    
    Parameters
    ----------
    parent : ET.Element
        The parent XML element.
    chart : Any
        Chart data containing planet positions.
    """
    try:
        from astro.sabian import get_sabian_for_planet
    except ImportError:
        return
    
    planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", 
               "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    
    sabian_elem = ET.SubElement(parent, "sabian_symbols")
    
    for planet_name in planets:
        sabian = get_sabian_for_planet(chart, planet_name)
        if sabian:
            # Create sabian_symbol element directly
            ss_elem = ET.SubElement(sabian_elem, "sabian_symbol")
            _set_attr(ss_elem, "planet", sabian.get("planet", ""))
            _set_attr(ss_elem, "degree", str(sabian.get("degree", "")))
            _set_attr(ss_elem, "sign", sabian.get("sign", ""))
            _set_attr(ss_elem, "degree_in_sign", str(sabian.get("degree_in_sign", "")))
            _set_attr(ss_elem, "keyword", sabian.get("keyword", ""))
            _set_attr(ss_elem, "symbol", sabian.get("symbol", ""))
            _set_attr(ss_elem, "positive", sabian.get("positive", ""))
            _set_attr(ss_elem, "negative", sabian.get("negative", ""))
            _set_attr(ss_elem, "formula", sabian.get("formula", ""))
            _set_attr(ss_elem, "interpretation", sabian.get("interpretation", ""))
            _set_attr(ss_elem, "planet_longitude", str(sabian.get("planet_longitude", "")))


def to_context(
    chart_data: "dict | object",
    system: str = "all",
    include_sabian: bool = False,
) -> str:
    """Convert kinastro chart data to a well-formed XML string for LLM context.

    Parameters
    ----------
    chart_data : dict | object
        Either a single chart object (any system), or a dict mapping
        system keys to chart objects (e.g. ``{"western": w_chart,
        "ziwei": z_chart, ...}``).

        When *chart_data* is a dict its keys may be raw system names
        (``"western"``) or tab-style keys (``"tab_western"``).

    system : str
        Which system to include.  Use ``"all"`` to include all systems
        present in *chart_data* (the default), or pass a specific system
        name (e.g. ``"western"``, ``"ziwei"``) to extract only that one.

        When *chart_data* is not a dict this parameter names the system
        tag that wraps the output (default ``"all"`` maps to the
        generic serialiser).
    
    include_sabian : bool, optional
        If True, include Sabian Symbols for all planets. Default is False.

    Returns
    -------
    str
        A well-formed, UTF-8 encoded XML document as a Python string.
        The root element is ``<kinastro_context>``.

    Examples
    --------
    >>> xml_str = to_context(western_chart, system="western")
    >>> xml_str = to_context({"western": w, "ziwei": z})
    >>> xml_str = to_context(western_chart, include_sabian=True)
    """
    root = ET.Element("kinastro_context")
    root.set("version", "1.0")

    if isinstance(chart_data, dict):
        # Multi-system dict
        for key, chart_obj in chart_data.items():
            if chart_obj is None:
                continue
            tag = _resolve_tag(str(key))
            if system != "all" and tag != _resolve_tag(system):
                continue
            sys_elem = ET.SubElement(root, tag)
            serializer = _SERIALIZERS.get(tag, _serialize_generic)
            try:
                serializer(sys_elem, chart_obj)
            except Exception:
                # Fallback: generic dump so we never lose data
                _serialize_generic(sys_elem, chart_obj, tag)
            
            # Add Sabian Symbols if requested
            if include_sabian and tag == "western":
                _serialize_sabian_symbols(root, chart_obj)
    else:
        # Single chart object
        tag = _resolve_tag(system) if system != "all" else "chart"
        sys_elem = ET.SubElement(root, tag)
        serializer = _SERIALIZERS.get(tag, _serialize_generic)
        try:
            serializer(sys_elem, chart_data)
        except Exception:
            _serialize_generic(sys_elem, chart_data, tag)
        
        # Add Sabian Symbols if requested
        if include_sabian:
            _serialize_sabian_symbols(root, chart_data)

    _indent(root)
    return ET.tostring(root, encoding="unicode", xml_declaration=False)
