"""
astro/ashtakavarga.py — Ashtakavarga 八分力量系統

Bhinnashtakavarga for 7 planets + Sarvashtakavarga.
"""
import streamlit as st
from dataclasses import dataclass

PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
PLANET_CN = {
    "Sun": "太陽", "Moon": "月亮", "Mars": "火星", "Mercury": "水星",
    "Jupiter": "木星", "Venus": "金星", "Saturn": "土星",
}

# BAV rules: for each planet's BAV, houses from each contributor that give a bindu
BAV_RULES = {
    "Sun": {
        "Sun": [1,2,4,7,8,9,10,11], "Moon": [3,6,10,11],
        "Mars": [1,2,4,7,8,9,10,11], "Mercury": [3,5,6,9,10,11,12],
        "Jupiter": [5,6,9,11], "Venus": [6,7,12],
        "Saturn": [1,2,4,7,8,9,10,11], "Asc": [3,4,6,10,11,12],
    },
    "Moon": {
        "Sun": [3,6,7,8,10,11], "Moon": [1,3,6,7,10,11],
        "Mars": [2,3,5,6,9,10,11], "Mercury": [1,3,4,5,7,8,10,11],
        "Jupiter": [1,4,7,8,10,11,12], "Venus": [3,4,5,7,9,10,11],
        "Saturn": [3,5,6,11], "Asc": [3,6,10,11],
    },
    "Mars": {
        "Sun": [3,5,6,10,11], "Moon": [3,6,11],
        "Mars": [1,2,4,7,8,10,11], "Mercury": [3,5,6,11],
        "Jupiter": [6,10,11,12], "Venus": [6,8,11,12],
        "Saturn": [1,4,7,8,9,10,11], "Asc": [1,3,6,10,11],
    },
    "Mercury": {
        "Sun": [5,6,9,11,12], "Moon": [2,4,6,8,10,11],
        "Mars": [1,2,4,7,8,9,10,11], "Mercury": [1,3,5,6,9,10,11,12],
        "Jupiter": [6,8,11,12], "Venus": [1,2,3,4,5,8,9,11],
        "Saturn": [1,2,4,7,8,9,10,11], "Asc": [1,2,4,6,8,10,11],
    },
    "Jupiter": {
        "Sun": [1,2,3,4,7,8,9,10,11], "Moon": [2,5,7,9,11],
        "Mars": [1,2,4,7,8,10,11], "Mercury": [1,2,4,5,6,9,10,11],
        "Jupiter": [1,2,3,4,7,8,10,11], "Venus": [2,5,6,9,10,11],
        "Saturn": [3,5,6,12], "Asc": [1,2,4,5,6,7,9,10,11],
    },
    "Venus": {
        "Sun": [8,11,12], "Moon": [1,2,3,4,5,8,9,11,12],
        "Mars": [3,5,6,9,11,12], "Mercury": [3,5,6,9,11],
        "Jupiter": [5,8,9,10,11], "Venus": [1,2,3,4,5,8,9,10,11],
        "Saturn": [3,4,5,8,9,10,11], "Asc": [1,2,3,4,5,8,9,11],
    },
    "Saturn": {
        "Sun": [1,2,4,7,8,10,11], "Moon": [3,6,11],
        "Mars": [3,5,6,10,11,12], "Mercury": [6,8,9,10,11,12],
        "Jupiter": [5,6,11,12], "Venus": [6,11,12],
        "Saturn": [3,5,6,11], "Asc": [1,3,4,6,10,11],
    },
}


def _house_from(from_sign: int, to_sign: int) -> int:
    """1-based house of *to_sign* counted from *from_sign*."""
    return (to_sign - from_sign) % 12 + 1


@dataclass
class BhinnashtakavargaRow:
    planet: str
    planet_cn: str
    bindus: list   # 12 ints (0/1)
    total: int


@dataclass
class AshtakavargaResult:
    bav: list          # List[BhinnashtakavargaRow]
    sarva: list        # 12 ints
    sarva_total: int


@st.cache_data(ttl=3600, show_spinner=False)
def compute_ashtakavarga(planet_longitudes: dict,
                         ascendant: float) -> AshtakavargaResult:
    """Compute Ashtakavarga from planet longitudes (canonical names) + Asc.

    planet_longitudes: {"Sun": 45.2, "Moon": 120.5, ...} (at least 7 planets)
    ascendant: longitude in degrees
    """
    signs = {p: int(lon / 30) % 12 for p, lon in planet_longitudes.items()}
    asc_sign = int(ascendant / 30) % 12

    bav_rows = []
    sarva = [0] * 12

    for planet in PLANET_ORDER:
        rules = BAV_RULES[planet]
        bindus = [0] * 12
        for to_sign in range(12):
            count = 0
            for contrib in PLANET_ORDER:
                if contrib in signs and contrib in rules:
                    h = _house_from(signs[contrib], to_sign)
                    if h in rules[contrib]:
                        count += 1
            # Ascendant contribution
            if "Asc" in rules:
                h = _house_from(asc_sign, to_sign)
                if h in rules["Asc"]:
                    count += 1
            bindus[to_sign] = count
        total = sum(bindus)
        bav_rows.append(BhinnashtakavargaRow(
            planet=planet, planet_cn=PLANET_CN[planet],
            bindus=bindus, total=total,
        ))
        for i in range(12):
            sarva[i] += bindus[i]

    return AshtakavargaResult(bav=bav_rows, sarva=sarva,
                              sarva_total=sum(sarva))
