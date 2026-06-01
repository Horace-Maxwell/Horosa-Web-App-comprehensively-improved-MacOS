"""
astro/western_synastry.py — 合盤 (Synastry Chart Comparison)

Calculates cross-aspects between two natal charts with interpretation text.
"""
import streamlit as st
from dataclasses import dataclass, field
from astro.interpretations import get_synastry_reading

ASPECT_TYPES = [
    {"name": "Conjunction (合)", "symbol": "☌", "angle": 0, "orb": 8},
    {"name": "Opposition (沖)", "symbol": "☍", "angle": 180, "orb": 8},
    {"name": "Trine (三合)", "symbol": "△", "angle": 120, "orb": 6},
    {"name": "Square (刑)", "symbol": "□", "angle": 90, "orb": 6},
    {"name": "Sextile (六合)", "symbol": "⚹", "angle": 60, "orb": 4},
]

BASE_HARMONY = {"Conjunction (合)": 0.5, "Opposition (沖)": -0.3,
                "Trine (三合)": 1.0, "Square (刑)": -0.5, "Sextile (六合)": 0.7}

SIGN_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}


def _angle_diff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


@dataclass
class SynastryAspect:
    planet_a: str
    planet_b: str
    aspect_name: str
    aspect_symbol: str
    aspect_angle: float
    orb: float
    harmony_score: float
    interpretation_en: str
    interpretation_cn: str


@dataclass
class SynastryResult:
    person_a_name: str
    person_b_name: str
    inter_aspects: list = field(default_factory=list)
    harmony_summary: float = 0.0
    element_compatibility: str = ""
    summary_en: str = ""
    summary_cn: str = ""


@st.cache_data(ttl=3600, show_spinner=False)
def compute_synastry(chart_a, chart_b,
                     name_a="Person A", name_b="Person B"):
    """Compute cross-aspects between two WesternChart objects."""
    aspects = []
    for pa in chart_a.planets:
        for pb in chart_b.planets:
            diff = _angle_diff(pa.longitude, pb.longitude)
            for asp in ASPECT_TYPES:
                orb = abs(diff - asp["angle"])
                if orb <= asp["orb"]:
                    score = BASE_HARMONY.get(asp["name"], 0) * (1 - orb / asp["orb"])
                    aspects.append(SynastryAspect(
                        planet_a=pa.name, planet_b=pb.name,
                        aspect_name=asp["name"], aspect_symbol=asp["symbol"],
                        aspect_angle=asp["angle"], orb=round(orb, 2),
                        harmony_score=round(score, 3),
                        interpretation_en=get_synastry_reading(pa.name, pb.name, asp["name"], "en"),
                        interpretation_cn=get_synastry_reading(pa.name, pb.name, asp["name"], "zh"),
                    ))
    aspects.sort(key=lambda a: a.orb)

    avg = sum(a.harmony_score for a in aspects) / max(len(aspects), 1)

    # Element compatibility
    a_sun = next((p for p in chart_a.planets if p.name.startswith("Sun")), None)
    b_sun = next((p for p in chart_b.planets if p.name.startswith("Sun")), None)
    compat = ""
    if a_sun and b_sun:
        e_a = SIGN_ELEMENTS.get(a_sun.sign, "")
        e_b = SIGN_ELEMENTS.get(b_sun.sign, "")
        same_elem = e_a == e_b
        compat_pairs = {("Fire","Air"), ("Air","Fire"), ("Earth","Water"), ("Water","Earth")}
        if same_elem:
            compat = f"Same element ({e_a}) — very harmonious"
        elif (e_a, e_b) in compat_pairs:
            compat = f"{e_a} + {e_b} — naturally compatible"
        else:
            compat = f"{e_a} + {e_b} — requires adjustment"

    if avg > 0.5:
        s_en = "Highly harmonious relationship with strong natural affinity."
        s_cn = "高度和諧的關係，具有強烈的天然親和力。"
    elif avg > 0.2:
        s_en = "Generally compatible with some areas of creative tension."
        s_cn = "大體相容，有些創造性張力的領域。"
    elif avg > -0.2:
        s_en = "Mixed dynamics requiring mutual understanding."
        s_cn = "動態混合，需要相互理解。"
    else:
        s_en = "Challenging dynamics requiring conscious effort and growth."
        s_cn = "具有挑戰性的動態，需要有意識的努力和成長。"

    return SynastryResult(
        person_a_name=name_a, person_b_name=name_b,
        inter_aspects=aspects, harmony_summary=round(avg, 3),
        element_compatibility=compat, summary_en=s_en, summary_cn=s_cn,
    )
