"""
astro/vedic_yogas.py — 吠陀瑜伽組合檢測 (Vedic Yoga Detection)

Detects Gajakesari, Kemdruma, Gandanta, Pancha Mahapurusha, etc.
"""
import streamlit as st
from dataclasses import dataclass

EXALTATION = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5,
              "Jupiter": 3, "Venus": 11, "Saturn": 6}
DEBILITATION = {"Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11,
                "Jupiter": 9, "Venus": 5, "Saturn": 0}
OWN_SIGNS = {
    "Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
    "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10],
}
SIGN_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon",
    4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars",
    8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}


def _sign(lon: float) -> int:
    return int(lon / 30) % 12


def _is_kendra(from_sign: int, to_sign: int) -> bool:
    return (to_sign - from_sign) % 12 in (0, 3, 6, 9)


def _house_from(from_sign: int, to_sign: int) -> int:
    return (to_sign - from_sign) % 12 + 1


@dataclass
class YogaResult:
    name: str
    name_cn: str
    is_present: bool
    strength: str
    description: str
    description_cn: str


@st.cache_data(ttl=3600, show_spinner=False)
def compute_yogas(planet_longitudes: dict, ascendant_lon: float) -> list:
    """Detect Vedic yogas from planet longitudes + ascendant.

    planet_longitudes: {"Sun": 45.2, "Moon": 120.5, "Mars": 200.1, ...}
    Returns list of YogaResult.
    """
    results = []
    signs = {p: _sign(lon) for p, lon in planet_longitudes.items()}
    asc_sign = _sign(ascendant_lon)
    moon_sign = signs.get("Moon")
    sun_sign = signs.get("Sun")
    jup_sign = signs.get("Jupiter")

    # 1. Gajakesari Yoga
    if moon_sign is not None and jup_sign is not None:
        present = _is_kendra(moon_sign, jup_sign)
        results.append(YogaResult(
            "Gajakesari Yoga", "象獅瑜伽", present,
            "Strong" if present else "—",
            "Jupiter in kendra from Moon — wisdom, wealth, fame." if present
            else "Not present.",
            "木星與月亮成角宮關係——智慧、財富、聲望。" if present
            else "不存在。",
        ))

    # 2. Kemdruma Yoga
    if moon_sign is not None:
        excluded = {"Sun", "Rahu", "Ketu"}
        h2 = (moon_sign + 1) % 12
        h12 = (moon_sign - 1) % 12
        has_planet_2_or_12 = any(
            s in (h2, h12) for p, s in signs.items()
            if p not in excluded and p != "Moon"
        )
        present = not has_planet_2_or_12
        results.append(YogaResult(
            "Kemdruma Yoga", "空月瑜伽", present,
            "Strong" if present else "—",
            "Moon isolated — emotional challenges, self-reliance." if present
            else "Not present.",
            "月亮孤立——情感挑戰、自力更生。" if present else "不存在。",
        ))

    # 3. Budha-Aditya Yoga
    if sun_sign is not None and signs.get("Mercury") is not None:
        present = sun_sign == signs["Mercury"]
        results.append(YogaResult(
            "Budha-Aditya Yoga", "日水瑜伽", present,
            "Moderate" if present else "—",
            "Sun-Mercury conjunction — intellect, communication." if present
            else "Not present.",
            "日水合——智力、溝通能力。" if present else "不存在。",
        ))

    # 4. Chandra-Mangal Yoga
    if moon_sign is not None and signs.get("Mars") is not None:
        present = moon_sign == signs["Mars"]
        results.append(YogaResult(
            "Chandra-Mangal Yoga", "月火瑜伽", present,
            "Moderate" if present else "—",
            "Moon-Mars conjunction — wealth through courage." if present
            else "Not present.",
            "月火合——以勇氣致富。" if present else "不存在。",
        ))

    # 5. Gandanta check
    if "Moon" in planet_longitudes:
        moon_lon = planet_longitudes["Moon"]
        # Water/Fire junctions: Cancer→Leo (120°), Scorpio→Sagittarius (240°), Pisces→Aries (0°/360°)
        gandanta_zones = [(116.667, 123.333), (236.667, 243.333), (356.667, 363.333)]
        present = False
        for lo, hi in gandanta_zones:
            if lo <= (moon_lon % 360) <= (hi % 360):
                present = True
                break
            if lo > 360:
                if moon_lon <= (hi % 360) or moon_lon >= (lo % 360):
                    present = True
                    break
        # Also check 0° boundary
        if moon_lon <= 3.333 or moon_lon >= 356.667:
            present = True
        results.append(YogaResult(
            "Gandanta", "甘丹塔", present,
            "Strong" if present else "—",
            "Moon at water-fire junction — karmic transformation." if present
            else "Not present.",
            "月亮在水火交界——業力轉化。" if present else "不存在。",
        ))

    # 6-10. Pancha Mahapurusha Yogas
    mahapurusha = [
        ("Mars", [0, 7, 9], "Ruchaka", "勇武瑜伽", "Courage, leadership, martial prowess.", "勇氣、領導力、武術。"),
        ("Mercury", [2, 5], "Bhadra", "智慧瑜伽", "Eloquence, intellect, business acumen.", "口才、智力、商業才能。"),
        ("Jupiter", [8, 11, 3], "Hamsa", "天鵝瑜伽", "Wisdom, spirituality, good fortune.", "智慧、靈性、好運。"),
        ("Venus", [1, 6, 11], "Malavya", "花環瑜伽", "Beauty, luxury, artistic talent.", "美麗、奢華、藝術天賦。"),
        ("Saturn", [9, 10, 6], "Sasa", "兔子瑜伽", "Authority, discipline, endurance.", "權威、紀律、耐力。"),
    ]
    for planet, strong_signs, name, name_cn, desc_en, desc_cn in mahapurusha:
        if planet in signs:
            in_strong = signs[planet] in strong_signs
            in_kendra = _is_kendra(asc_sign, signs[planet])
            present = in_strong and in_kendra
            results.append(YogaResult(
                f"{name} Yoga", name_cn, present,
                "Strong" if present else "—",
                f"{name}: {desc_en}" if present else "Not present.",
                f"{name_cn}：{desc_cn}" if present else "不存在。",
            ))

    # 11. Vesi Yoga (planet in 2nd from Sun, not Moon/Rahu/Ketu)
    if sun_sign is not None:
        h2_from_sun = (sun_sign + 1) % 12
        excluded = {"Moon", "Rahu", "Ketu", "Sun"}
        present = any(s == h2_from_sun for p, s in signs.items() if p not in excluded)
        results.append(YogaResult(
            "Vesi Yoga", "日前瑜伽", present,
            "Moderate" if present else "—",
            "Planet in 2nd from Sun — strong will, fame." if present else "Not present.",
            "行星在太陽後一宮——意志堅強、聲望。" if present else "不存在。",
        ))

    # 12. Vosi Yoga (planet in 12th from Sun)
    if sun_sign is not None:
        h12_from_sun = (sun_sign - 1) % 12
        excluded_vosi = {"Moon", "Rahu", "Ketu", "Sun"}
        present = any(s == h12_from_sun for p, s in signs.items() if p not in excluded_vosi)
        results.append(YogaResult(
            "Vosi Yoga", "日後瑜伽", present,
            "Moderate" if present else "—",
            "Planet in 12th from Sun — charitable, learned." if present else "Not present.",
            "行星在太陽前一宮——慈善、博學。" if present else "不存在。",
        ))

    return results
