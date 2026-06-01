"""
astro/natal_summary.py — 命盤摘要生成器 (Natal Chart Summary Generator)

Generates a narrative summary of a natal chart based on planet positions,
houses, and aspects. Supports English and Chinese.
"""

from .interpretations import ASC_READINGS, SUN_SIGN_READINGS, MOON_SIGN_READINGS

ELEMENT_NAMES = {
    "en": {"Fire": "Fire", "Earth": "Earth", "Air": "Air", "Water": "Water"},
    "zh": {"Fire": "火", "Earth": "土", "Air": "風", "Water": "水"},
}

SIGN_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}


def _find_planet(planets, target: str):
    """Find a planet object by canonical name substring."""
    for p in planets:
        name = getattr(p, 'name', '') or ''
        if target in name:
            return p
    return None


def _get_sign(planet) -> str:
    """Extract sign from planet object, trying common attribute names."""
    for attr in ('sign', 'rashi', 'sign_western'):
        val = getattr(planet, attr, None)
        if val:
            return val
    return ""


def _element_distribution(planets, lang: str) -> str:
    """Analyze element distribution of planets."""
    counts = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    for p in planets:
        sign = _get_sign(p)
        elem = SIGN_ELEMENTS.get(sign, "")
        if elem:
            counts[elem] += 1

    total = sum(counts.values())
    if total == 0:
        return ""

    dominant = max(counts, key=counts.get)
    dom_pct = counts[dominant] / total * 100
    missing = [e for e, c in counts.items() if c == 0]

    if lang == "zh":
        elem_cn = ELEMENT_NAMES["zh"]
        parts = [f"{elem_cn[e]}象{c}顆" for e, c in counts.items() if c > 0]
        line = f"**元素分布：** {', '.join(parts)}。"
        if dom_pct >= 40:
            line += f" {elem_cn[dominant]}象主導（{dom_pct:.0f}%），"
            _traits = {
                "Fire": "個性積極、熱情、行動導向",
                "Earth": "個性務實、穩定、注重物質",
                "Air": "個性理性、善溝通、重視思考",
                "Water": "個性感性、直覺強、情感豐富",
            }
            line += _traits.get(dominant, "")
            line += "。"
        if missing:
            line += f" 缺乏{'、'.join(elem_cn[e] for e in missing)}象元素，可留意此方面的平衡。"
        return line
    else:
        parts = [f"{e}: {c}" for e, c in counts.items() if c > 0]
        line = f"**Element Distribution:** {', '.join(parts)}."
        if dom_pct >= 40:
            line += f" {dominant} dominant ({dom_pct:.0f}%)."
        if missing:
            line += f" Lacking {', '.join(missing)} element(s)."
        return line


HEMISPHERE_THRESHOLD = 0.7


def _hemisphere_analysis(planets, lang: str) -> str:
    """Analyze hemisphere distribution based on longitudes."""
    upper = 0  # Libra–Pisces (180–360)
    lower = 0  # Aries–Virgo (0–180)

    for p in planets:
        lon = getattr(p, 'longitude', None)
        if lon is None:
            continue
        if lon < 180:
            lower += 1
        else:
            upper += 1

    total = upper + lower
    if total == 0:
        return ""

    if lang == "zh":
        if lower > total * HEMISPHERE_THRESHOLD:
            return "**半球分布：** 行星集中於東半球（白羊─處女），個人意志和自我驅動力強。"
        elif upper > total * HEMISPHERE_THRESHOLD:
            return "**半球分布：** 行星集中於西半球（天秤─雙魚），注重他人關係和社會互動。"
        return "**半球分布：** 行星分布較為均勻，內外生活趨向平衡。"
    else:
        if lower > total * HEMISPHERE_THRESHOLD:
            return "**Hemisphere:** Planets concentrated in eastern hemisphere — strong personal drive."
        elif upper > total * HEMISPHERE_THRESHOLD:
            return "**Hemisphere:** Planets concentrated in western hemisphere — relationship-oriented."
        return "**Hemisphere:** Planets fairly evenly distributed — balanced inner/outer life."


def generate_natal_summary(planets, houses, asc_sign: str, lang: str = "zh") -> str:
    """Generate a narrative natal chart summary (200–400 characters).

    Parameters:
        planets: list of planet objects (must have .name, .longitude, .sign)
        houses: list of house objects (optional)
        asc_sign: Ascendant sign name (e.g. "Aries")
        lang: "zh" or "en"

    Returns:
        Markdown-formatted summary text.
    """
    sections = []

    # 1. Ascendant reading
    asc_entry = ASC_READINGS.get(asc_sign)
    if asc_entry:
        sections.append(asc_entry.get("cn" if lang == "zh" else "en", ""))

    # 2. Sun sign reading
    sun = _find_planet(planets, "Sun")
    if sun:
        sun_sign = _get_sign(sun)
        sun_entry = SUN_SIGN_READINGS.get(sun_sign)
        if sun_entry:
            sections.append(sun_entry.get("cn" if lang == "zh" else "en", ""))

    # 3. Moon sign reading
    moon = _find_planet(planets, "Moon")
    if moon:
        moon_sign = _get_sign(moon)
        moon_entry = MOON_SIGN_READINGS.get(moon_sign)
        if moon_entry:
            sections.append(moon_entry.get("cn" if lang == "zh" else "en", ""))

    # 4. Element distribution
    elem = _element_distribution(planets, lang)
    if elem:
        sections.append(elem)

    # 5. Hemisphere analysis
    hemi = _hemisphere_analysis(planets, lang)
    if hemi:
        sections.append(hemi)

    if not sections:
        return "—"

    return "\n\n".join(sections)
