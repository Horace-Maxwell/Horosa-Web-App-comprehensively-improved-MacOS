"""
astro/export.py — 匯出功能 (Chart Export)

Text summary, CSV, and SVG→PNG export for chart data.
"""
import csv
import io
import logging

logger = logging.getLogger(__name__)


def generate_chart_summary(chart_data):
    """Generate text summary from a standardized chart dict.

    chart_data: {system, datetime, location, planets, houses, ascendant, extra_sections}
    """
    lines = []
    lines.append(f"=== {chart_data.get('system', 'Chart')} ===")
    lines.append(f"Date/Time: {chart_data.get('datetime', '—')}")
    lines.append(f"Location: {chart_data.get('location', '—')}")
    if chart_data.get('ascendant'):
        lines.append(f"Ascendant: {chart_data['ascendant']}")
    lines.append("")
    lines.append("--- Planets ---")
    for p in chart_data.get("planets", []):
        retro = " (R)" if p.get("retrograde") else ""
        lines.append(f"  {p['name']:20s} {p.get('sign',''):14s} {p.get('degree', 0):7.2f}°{retro}")
    if chart_data.get("houses"):
        lines.append("")
        lines.append("--- Houses ---")
        for h in chart_data["houses"]:
            lines.append(f"  House {h.get('number', '?'):2s}  {h.get('sign', ''):14s}  {h.get('cusp', 0):7.2f}°")
    for sec in chart_data.get("extra_sections", []):
        lines.append("")
        lines.append(f"--- {sec['title']} ---")
        lines.append(sec["content"])
    return "\n".join(lines)


def generate_planet_csv(planets):
    """Generate CSV string from list of planet dicts."""
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Name", "Longitude", "Sign", "Degree", "Retrograde"])
    for p in planets:
        writer.writerow([p.get("name",""), f"{p.get('longitude',0):.4f}",
                         p.get("sign",""), f"{p.get('degree',0):.2f}",
                         p.get("retrograde", False)])
    return out.getvalue()


def generate_asteroids_csv(asteroids) -> str:
    """Generate CSV string from a list of AsteroidPosition objects."""
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow([
        "Name", "CN Name", "Symbol", "Group",
        "Longitude", "Latitude", "Speed (°/d)",
        "Sign", "Sign Degree", "Retrograde", "Heliocentric",
        "Meaning (EN)", "Meaning (CN)",
    ])
    for a in asteroids:
        writer.writerow([
            a.name, a.name_cn, a.symbol, a.group,
            f"{a.longitude:.4f}", f"{a.latitude:.4f}", f"{a.speed:+.6f}",
            a.sign, f"{a.sign_degree:.2f}",
            "Yes" if a.retrograde else "No",
            "Yes" if a.heliocentric else "No",
            a.meaning_en, a.meaning_cn,
        ])
    return out.getvalue()


def generate_fixed_stars_csv(stars) -> str:
    """Generate CSV string from a list of FixedStarPosition objects."""
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow([
        "Name", "CN Name", "Constellation",
        "Longitude", "Latitude", "Sign", "Sign Degree",
        "Magnitude", "Nature",
        "Meaning (EN)", "Meaning (CN)",
    ])
    for s in stars:
        writer.writerow([
            s.name, getattr(s, "cn_name", s.name), s.constellation,
            f"{s.longitude:.4f}", f"{s.latitude:.4f}",
            s.sign, f"{s.sign_degree:.2f}",
            s.magnitude, s.nature,
            s.meaning_en, s.meaning_cn,
        ])
    return out.getvalue()


def svg_to_png(svg_string: str, width: int = 800) -> bytes | None:
    """Convert SVG string to PNG bytes. Returns None if cairosvg is unavailable."""
    try:
        import cairosvg
        return cairosvg.svg2png(
            bytestring=svg_string.encode("utf-8"),
            output_width=width,
        )
    except ImportError:
        return None
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("SVG to PNG conversion failed: %s", exc)
        return None


def western_chart_to_dict(chart):
    """Convert WesternChart to standardized dict."""
    planets = [{"name": p.name, "longitude": p.longitude, "sign": p.sign,
                "degree": p.sign_degree, "retrograde": p.retrograde}
               for p in chart.planets]
    houses = [{"number": str(h.number), "sign": h.sign, "cusp": h.cusp}
              for h in chart.houses]
    return {"system": "Western Astrology", "datetime": f"{chart.year}-{chart.month:02d}-{chart.day:02d}",
            "location": chart.location_name, "ascendant": chart.asc_sign,
            "planets": planets, "houses": houses}


def vedic_chart_to_dict(chart):
    planets = [{"name": p.name, "longitude": p.longitude, "sign": p.rashi,
                "degree": round(p.longitude % 30, 2), "retrograde": p.retrograde}
               for p in chart.planets]
    return {"system": "Vedic Astrology", "datetime": f"{chart.year}-{chart.month:02d}-{chart.day:02d}",
            "location": chart.location_name, "ascendant": getattr(chart, 'asc_rashi', ''),
            "planets": planets, "houses": []}


def chinese_chart_to_dict(chart):
    planets = [{"name": p.name, "longitude": p.longitude,
                "sign": getattr(p, 'sign_chinese', ''),
                "degree": round(p.longitude % 30, 2), "retrograde": False}
               for p in chart.planets]
    return {"system": "Chinese Astrology (七政四餘)", "datetime": f"{chart.year}-{chart.month:02d}-{chart.day:02d}",
            "location": chart.location_name, "ascendant": "",
            "planets": planets, "houses": []}


def generic_chart_to_dict(chart_obj, system_name=""):
    """Convert any chart object to the standardized dict expected by export.

    Works with all 15 astrology systems by introspecting common attributes.
    Falls back gracefully when attributes are missing.
    """
    d = {
        "system": system_name,
        "datetime": "",
        "location": getattr(chart_obj, "location_name", ""),
        "ascendant": "",
        "planets": [],
        "houses": [],
        "extra_sections": [],
    }

    # Date / time
    _y = getattr(chart_obj, "year", None)
    _m = getattr(chart_obj, "month", None)
    _day = getattr(chart_obj, "day", None)
    if _y and _m and _day:
        _hr = getattr(chart_obj, "hour", 0)
        _mi = getattr(chart_obj, "minute", 0)
        d["datetime"] = f"{_y}-{_m:02d}-{_day:02d} {_hr:02d}:{_mi:02d}"

    # Ascendant
    for attr in ("asc_sign", "asc_rashi", "ascendant"):
        val = getattr(chart_obj, attr, None)
        if val and isinstance(val, str):
            d["ascendant"] = val
            break

    # Planets (most systems)
    raw_planets = getattr(chart_obj, "planets", None)
    if raw_planets and isinstance(raw_planets, (list, tuple)):
        for p in raw_planets:
            entry = {
                "name": getattr(p, "name", str(p)),
                "longitude": getattr(p, "longitude", 0),
                "sign": (
                    getattr(p, "sign", None)
                    or getattr(p, "rashi", None)
                    or getattr(p, "sign_chinese", None)
                    or ""
                ),
                "degree": round(
                    getattr(p, "sign_degree", None)
                    if getattr(p, "sign_degree", None) is not None
                    else (getattr(p, "longitude", 0) % 30),
                    2,
                ),
                "retrograde": getattr(p, "retrograde", False),
            }
            d["planets"].append(entry)

    # Hellenistic: planet_longitudes dict
    if not d["planets"]:
        _plongs = getattr(chart_obj, "planet_longitudes", None)
        if _plongs and isinstance(_plongs, dict):
            for name, lon in _plongs.items():
                d["planets"].append({
                    "name": name,
                    "longitude": lon,
                    "sign": "",
                    "degree": round(lon % 30, 2),
                    "retrograde": False,
                })

    # Ziwei palaces
    _palaces = getattr(chart_obj, "palaces", None)
    if _palaces and isinstance(_palaces, (list, tuple)) and not d["planets"]:
        lines = []
        for pal in _palaces:
            _pname = getattr(pal, "name", "")
            _pbranch = getattr(pal, "branch", "")
            _stars = getattr(pal, "stars", [])
            star_str = ", ".join(str(s) for s in _stars) if _stars else "—"
            lines.append(f"{_pname} ({_pbranch}): {star_str}")
        d["extra_sections"].append({"title": "Palaces / 宮位", "content": "\n".join(lines)})

    # Mahabote houses
    _mhouses = getattr(chart_obj, "houses", None)
    if _mhouses and isinstance(_mhouses, (list, tuple)) and not d["planets"]:
        lines = []
        for h in _mhouses:
            _hname = getattr(h, "name_en", "") or getattr(h, "name", "")
            _hmeaning = getattr(h, "meaning", "") or getattr(h, "name_myanmar", "")
            lines.append(f"{_hname}: {_hmeaning}")
        if lines:
            d["extra_sections"].append({"title": "Houses", "content": "\n".join(lines)})

    # Zurkhai animal/element info
    _ba = getattr(chart_obj, "birth_animal", None)
    _be = getattr(chart_obj, "birth_element", None)
    if _ba or _be:
        parts = []
        if _ba:
            parts.append(f"Birth Animal: {_ba}")
        if _be:
            parts.append(f"Birth Element: {_be}")
        _rel_cn = getattr(chart_obj, "year_element_relation_cn", "")
        _rel_en = getattr(chart_obj, "year_element_relation_en", "")
        if _rel_cn or _rel_en:
            parts.append(f"Year Element Relation: {_rel_cn} / {_rel_en}")
        d["extra_sections"].append({"title": "Zurkhai Info", "content": "\n".join(parts)})

    # Mayan calendar info
    _lcs = getattr(chart_obj, "long_count_str", None)
    if _lcs:
        parts = [f"Long Count: {_lcs}"]
        _tzn = getattr(chart_obj, "tzolkin_number", "")
        _tzd = getattr(chart_obj, "tzolkin_day_name", "")
        if _tzn and _tzd:
            parts.append(f"Tzolkin: {_tzn} {_tzd}")
        _hd = getattr(chart_obj, "haab_day", "")
        _hm = getattr(chart_obj, "haab_month", "")
        if _hm:
            parts.append(f"Haab: {_hd} {_hm}")
        d["extra_sections"].append({"title": "Mayan Calendar", "content": "\n".join(parts)})

    return d


def generate_share_url(chart_data):
    """Generate a share URL containing chart parameters as query string.

    The URL encodes the basic chart parameters so others can reproduce the
    same chart.  It uses base-64 encoded JSON to keep the URL compact.
    """
    import base64
    import json as _json
    params = {
        "s": chart_data.get("system", ""),
        "d": chart_data.get("datetime", ""),
        "l": chart_data.get("location", ""),
        "a": chart_data.get("ascendant", ""),
    }
    payload = base64.urlsafe_b64encode(
        _json.dumps(params, ensure_ascii=False).encode("utf-8")
    ).decode("ascii")
    return f"?chart={payload}"


def render_download_buttons(chart_data, svg_string=None, key_prefix=""):
    """Render one-click export row: TXT · CSV · PNG · Share link."""
    import streamlit as st

    st.markdown('<div class="export-btn-row">', unsafe_allow_html=True)
    cols = st.columns(4 if svg_string else 3)

    with cols[0]:
        txt = generate_chart_summary(chart_data)
        st.download_button("📄 TXT", data=txt,
                          file_name="chart_summary.txt",
                          mime="text/plain", key=f"{key_prefix}_txt")
    with cols[1]:
        csv_str = generate_planet_csv(chart_data.get("planets", []))
        st.download_button("📊 CSV", data=csv_str,
                          file_name="planet_data.csv",
                          mime="text/csv", key=f"{key_prefix}_csv")

    _png_col_idx = 2 if svg_string else None
    _share_col_idx = 3 if svg_string else 2

    if svg_string:
        with cols[_png_col_idx]:
            png_bytes = svg_to_png(svg_string)
            if png_bytes:
                st.download_button("🖼️ PNG", data=png_bytes,
                                  file_name="chart_image.png",
                                  mime="image/png", key=f"{key_prefix}_png")
            else:
                st.caption("PNG unavailable")

    with cols[_share_col_idx]:
        share_url = generate_share_url(chart_data)
        st.code(share_url, language=None)
        st.caption("📋 Share link")

    st.markdown('</div>', unsafe_allow_html=True)


def render_unified_export(chart_dict, system_name="", key_prefix="export",
                          svg_string=None):
    """Unified export buttons: TXT · CSV · JSON (+ PNG if SVG provided).

    A more comprehensive version of ``render_download_buttons`` that adds
    JSON export and uses ``width="stretch"`` per project conventions.
    """
    import json as _json
    import streamlit as st

    _has_svg = svg_string is not None
    _ncols = 4 if _has_svg else 3
    cols = st.columns(_ncols)

    with cols[0]:
        _txt = generate_chart_summary(chart_dict)
        st.download_button(
            "📄 TXT", data=_txt,
            file_name=f"{key_prefix}_chart.txt",
            mime="text/plain",
            key=f"{key_prefix}_u_txt",
            width="stretch",
        )
    with cols[1]:
        _csv = generate_planet_csv(chart_dict.get("planets", []))
        st.download_button(
            "📊 CSV", data=_csv,
            file_name=f"{key_prefix}_chart.csv",
            mime="text/csv",
            key=f"{key_prefix}_u_csv",
            width="stretch",
        )

    _json_col = 2 if not _has_svg else 3
    if _has_svg:
        with cols[2]:
            _png = svg_to_png(svg_string)
            if _png:
                st.download_button(
                    "🖼️ PNG", data=_png,
                    file_name=f"{key_prefix}_chart.png",
                    mime="image/png",
                    key=f"{key_prefix}_u_png",
                    width="stretch",
                )
            else:
                st.caption("PNG unavailable")

    with cols[_json_col]:
        _json_str = _json.dumps(chart_dict, ensure_ascii=False, indent=2)
        st.download_button(
            "🔧 JSON", data=_json_str,
            file_name=f"{key_prefix}_chart.json",
            mime="application/json",
            key=f"{key_prefix}_u_json",
            width="stretch",
        )
