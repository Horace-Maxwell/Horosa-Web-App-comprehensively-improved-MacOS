"""
astro/harmonic/calculator.py — Harmonic Astrology computation engine

Faithfully implements John Addey's Harmonic Astrology system as described in:
  - John Addey, "Harmonics in Astrology" (1976, L.N. Fowler & Co.)
  - David Hamblin, "Harmonic Charts" (1983, Aquarian Press)

Core principle (Addey, Chapter 2):
  The Nth Harmonic Chart is obtained by multiplying all planetary longitudes
  by N and reducing modulo 360°.  Conjunctions in the resulting chart
  correspond to aspects of 360°/N (and their multiples) in the natal chart.

Mathematical basis:
  H_N(λ) = (N × λ) mod 360°

  A conjunction in H_N (orb ε) corresponds to:
    |N × λ_A − N × λ_B| ≡ 0 (mod 360°)  within ε degrees
  ⟺  |λ_A − λ_B| ≡ k × (360°/N) (mod 360°)  for some integer k,  within ε/N degrees

Public API:
    compute_harmonic_chart(...)    → HarmonicChart
    compute_multi_harmonic(...)   → MultiHarmonicResult
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from .constants import (
    PLANET_SWE_IDS,
    PLANET_NAMES_EN,
    PLANET_NAMES_ZH,
    PLANET_SYMBOLS,
    PLANET_ORDER,
    ZODIAC_SIGNS,
    SIGN_ZH,
    SIGN_SYMBOLS,
    HARMONIC_DEFS,
    SUPPORTED_HARMONICS,
    DEFAULT_CONJUNCTION_ORB,
    get_harmonic_specific_meaning,
)


# ──────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────

@dataclass
class NatalPlanet:
    """A planet/point with its natal (H1) position."""

    key: str
    name_en: str
    name_zh: str
    symbol: str
    natal_longitude: float      # 0–360°, absolute ecliptic
    sign: str
    sign_zh: str
    sign_symbol: str
    sign_degree: float          # degree within sign, 0–30°
    retrograde: bool = False


@dataclass
class HarmonicPlanet:
    """A planet in a specific harmonic chart."""

    key: str
    name_en: str
    name_zh: str
    symbol: str
    harmonic_longitude: float   # (N × natal_lon) mod 360°
    natal_longitude: float      # Original natal longitude
    sign: str
    sign_zh: str
    sign_symbol: str
    sign_degree: float
    retrograde: bool = False


@dataclass
class HarmonicConjunction:
    """
    A conjunction in a harmonic chart (Addey: the primary aspect to study).

    In H_N, a conjunction between planets A and B means that their natal
    longitudes differ by a multiple of (360°/N) within orb/N.
    This is the central analytical tool in Addey's system.
    """

    planet_a: str
    planet_b: str
    harmonic_lon_a: float       # position of A in harmonic chart
    harmonic_lon_b: float       # position of B in harmonic chart
    harmonic_orb: float         # |H_N(A) − H_N(B)| reduced to min arc (degrees)
    natal_aspect: float         # Corresponding natal aspect (360°/N × k)
    natal_aspect_name: str      # e.g. "quintile (72°)" for H5
    meaning_zh: str
    meaning_en: str


@dataclass
class HarmonicChart:
    """
    A complete Nth Harmonic chart.

    Contains all planet positions multiplied by N and all conjunctions
    found within the specified orb.

    Ref: Addey (1976), Chapter 2 — "The Harmonic Chart".
    """

    harmonic_number: int
    name_zh: str
    name_en: str
    theme_zh: str
    theme_en: str
    addey_note_zh: str
    addey_note_en: str
    natal_planets: List[NatalPlanet]
    harmonic_planets: List[HarmonicPlanet]
    conjunctions: List[HarmonicConjunction]
    conjunction_orb: float

    # Birth data (stored for display)
    year: int = 0
    month: int = 0
    day: int = 0
    hour: int = 0
    minute: int = 0
    timezone: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    location_name: str = ""

    def get_planet(self, key: str) -> Optional[HarmonicPlanet]:
        for p in self.harmonic_planets:
            if p.key == key:
                return p
        return None


@dataclass
class MultiHarmonicResult:
    """Results from analyzing multiple harmonics simultaneously."""

    natal_planets: List[NatalPlanet]
    harmonic_charts: Dict[int, HarmonicChart]

    # Cross-harmonic summary: planets that appear in conjunctions
    # across multiple harmonics (Hamblin: "multiple harmonic emphasis")
    multi_emphasis: List[Dict]   # [{key, harmonics_active, count}]

    year: int = 0
    month: int = 0
    day: int = 0
    hour: int = 0
    minute: int = 0
    timezone: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    location_name: str = ""


# ──────────────────────────────────────────────────────────────
# Low-level geometry helpers
# ──────────────────────────────────────────────────────────────

def _normalize(deg: float) -> float:
    """Reduce angle to [0°, 360°)."""
    return deg % 360.0


def _arc_diff(a: float, b: float) -> float:
    """Minimum absolute arc between two longitudes on a circle."""
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def _sign_from_lon(lon: float) -> Tuple[str, str, str, float]:
    """Return (sign_en, sign_zh, sign_symbol, degree_in_sign) for a longitude."""
    idx = int(lon / 30.0) % 12
    return ZODIAC_SIGNS[idx], SIGN_ZH[idx], SIGN_SYMBOLS[idx], lon % 30.0


def _harmonic_longitude(natal_lon: float, n: int) -> float:
    """
    Compute the Nth harmonic longitude.

    H_N(λ) = (N × λ) mod 360°    [Addey 1976, p. 21]
    """
    return _normalize(n * natal_lon)


def _corresponding_natal_aspect(n: int) -> Tuple[float, str]:
    """
    The natal aspect (in degrees) corresponding to a conjunction in H_N.

    A conjunction in H_N means the planets are separated by 360°/N in the natal.
    For multiples: k × 360°/N for k = 1, 2, ..., N-1.
    Returns the smallest (fundamental) aspect and its name.
    """
    base_deg = 360.0 / n
    names: Dict[int, str] = {
        1: "conjunction (0°)",
        2: "opposition (180°)",
        3: "trine (120°)",
        4: "square (90°)",
        5: "quintile (72°)",
        6: "sextile (60°)",
        7: "septile (51.4°)",
        8: "semi-square (45°)",
        9: "novile (40°)",
        10: "decile (36°)",
        12: "semi-sextile (30°)",
    }
    name = names.get(n, f"{base_deg:.2f}°-aspect")
    return base_deg, name


# ──────────────────────────────────────────────────────────────
# Position computation (Swiss Ephemeris)
# ──────────────────────────────────────────────────────────────

def _compute_natal_positions(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float,
    latitude: float, longitude: float,
) -> List[NatalPlanet]:
    """
    Compute all standard planet + house-point positions.

    Uses Swiss Ephemeris (swe) for high-precision positions.
    Includes: SU MO ME VE MA JU SA UR NE PL AS MC NN
    """
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)

    # Houses (Placidus) for AS and MC
    houses, ascmc = swe.houses(jd, latitude, longitude, b"P")
    asc_lon = _normalize(ascmc[0])
    mc_lon = _normalize(ascmc[1])

    planets: List[NatalPlanet] = []

    # 10 standard planets
    for key, pid in PLANET_SWE_IDS.items():
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        result, _ = swe.calc_ut(jd, pid, flags)
        lon = _normalize(result[0])
        retrograde = result[3] < 0  # negative speed = retrograde
        sign_en, sign_zh, sign_sym, sdeg = _sign_from_lon(lon)
        planets.append(NatalPlanet(
            key=key,
            name_en=PLANET_NAMES_EN[key],
            name_zh=PLANET_NAMES_ZH[key],
            symbol=PLANET_SYMBOLS[key],
            natal_longitude=lon,
            sign=sign_en,
            sign_zh=sign_zh,
            sign_symbol=sign_sym,
            sign_degree=sdeg,
            retrograde=retrograde,
        ))

    # Ascendant
    sign_en, sign_zh, sign_sym, sdeg = _sign_from_lon(asc_lon)
    planets.append(NatalPlanet(
        key="AS",
        name_en=PLANET_NAMES_EN["AS"],
        name_zh=PLANET_NAMES_ZH["AS"],
        symbol=PLANET_SYMBOLS["AS"],
        natal_longitude=asc_lon,
        sign=sign_en, sign_zh=sign_zh, sign_symbol=sign_sym, sign_degree=sdeg,
    ))

    # Midheaven
    sign_en, sign_zh, sign_sym, sdeg = _sign_from_lon(mc_lon)
    planets.append(NatalPlanet(
        key="MC",
        name_en=PLANET_NAMES_EN["MC"],
        name_zh=PLANET_NAMES_ZH["MC"],
        symbol=PLANET_SYMBOLS["MC"],
        natal_longitude=mc_lon,
        sign=sign_en, sign_zh=sign_zh, sign_symbol=sign_sym, sign_degree=sdeg,
    ))

    # True North Node
    result_node, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH)
    node_lon = _normalize(result_node[0])
    sign_en, sign_zh, sign_sym, sdeg = _sign_from_lon(node_lon)
    planets.append(NatalPlanet(
        key="NN",
        name_en=PLANET_NAMES_EN["NN"],
        name_zh=PLANET_NAMES_ZH["NN"],
        symbol=PLANET_SYMBOLS["NN"],
        natal_longitude=node_lon,
        sign=sign_en, sign_zh=sign_zh, sign_symbol=sign_sym, sign_degree=sdeg,
    ))

    # Return in standard order
    order_map = {k: i for i, k in enumerate(PLANET_ORDER)}
    planets.sort(key=lambda p: order_map.get(p.key, 99))
    return planets


# ──────────────────────────────────────────────────────────────
# Harmonic chart construction
# ──────────────────────────────────────────────────────────────

def _build_harmonic_planets(
    natal: List[NatalPlanet],
    n: int,
) -> List[HarmonicPlanet]:
    """
    Convert natal positions to harmonic chart positions.

    H_N(λ) = (N × λ) mod 360°   [Addey 1976, p. 21]
    """
    result = []
    for np_ in natal:
        h_lon = _harmonic_longitude(np_.natal_longitude, n)
        sign_en, sign_zh, sign_sym, sdeg = _sign_from_lon(h_lon)
        result.append(HarmonicPlanet(
            key=np_.key,
            name_en=np_.name_en,
            name_zh=np_.name_zh,
            symbol=np_.symbol,
            harmonic_longitude=h_lon,
            natal_longitude=np_.natal_longitude,
            sign=sign_en,
            sign_zh=sign_zh,
            sign_symbol=sign_sym,
            sign_degree=sdeg,
            retrograde=np_.retrograde,
        ))
    return result


def _find_conjunctions(
    harmonic_planets: List[HarmonicPlanet],
    n: int,
    orb: float,
) -> List[HarmonicConjunction]:
    """
    Find all conjunctions in the harmonic chart.

    Conjunction criterion (Addey): arc between H_N positions ≤ orb degrees.
    Conjunctions in H_N correspond to natal aspects of k × (360°/N).

    Sorted by orb (tightest first).
    """
    natal_aspect_deg, natal_aspect_name = _corresponding_natal_aspect(n)
    conjunctions: List[HarmonicConjunction] = []

    for i in range(len(harmonic_planets)):
        for j in range(i + 1, len(harmonic_planets)):
            pa = harmonic_planets[i]
            pb = harmonic_planets[j]
            arc = _arc_diff(pa.harmonic_longitude, pb.harmonic_longitude)
            if arc <= orb:
                meaning = get_harmonic_specific_meaning(n, pa.key, pb.key)
                conjunctions.append(HarmonicConjunction(
                    planet_a=pa.key,
                    planet_b=pb.key,
                    harmonic_lon_a=pa.harmonic_longitude,
                    harmonic_lon_b=pb.harmonic_longitude,
                    harmonic_orb=arc,
                    natal_aspect=natal_aspect_deg,
                    natal_aspect_name=natal_aspect_name,
                    meaning_zh=meaning["zh"],
                    meaning_en=meaning["en"],
                ))

    conjunctions.sort(key=lambda c: c.harmonic_orb)
    return conjunctions


# ──────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────

def compute_harmonic_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    harmonic_number: int = 5,
    conjunction_orb: Optional[float] = None,
    location_name: str = "",
    **_kwargs,
) -> HarmonicChart:
    """
    Compute a Harmonic Chart following John Addey's method.

    The core operation: multiply all planetary longitudes by harmonic_number
    (mod 360°) and then identify conjunctions in the resulting chart.

    Args:
        year, month, day: Birth date.
        hour, minute: Local birth time.
        timezone: UTC offset in hours.
        latitude, longitude: Geographic coordinates.
        harmonic_number: The harmonic to compute (default: 5).
            Supported: 1, 2, 3, 4, 5, 7, 9, 12 (and any positive integer).
        conjunction_orb: Orb in degrees for harmonic conjunctions.
            Defaults to the traditional value for this harmonic.
        location_name: Optional city name for display.

    Returns:
        HarmonicChart with full Addey-tradition analysis.

    Reference:
        Addey (1976), Chapter 2, pp. 20–35.
    """
    if harmonic_number < 1:
        raise ValueError(f"harmonic_number must be >= 1, got {harmonic_number}")

    if conjunction_orb is None:
        conjunction_orb = DEFAULT_CONJUNCTION_ORB.get(
            harmonic_number,
            max(1.0, 8.0 / math.sqrt(harmonic_number)),  # fallback: scale by sqrt
        )

    # Get harmonic definition (or generate generic one)
    hdef = HARMONIC_DEFS.get(harmonic_number, {
        "name_zh": f"{harmonic_number}諧波",
        "name_en": f"{harmonic_number}th Harmonic",
        "theme_zh": f"{harmonic_number}分相的能量模式",
        "theme_en": f"Energy pattern of the {harmonic_number}-th aspect",
        "addey_note_zh": f"H{harmonic_number}：將所有行星經度乘以{harmonic_number}後取模360°。",
        "addey_note_en": f"H{harmonic_number}: Multiply all longitudes by {harmonic_number} mod 360°.",
    })

    natal_planets = _compute_natal_positions(
        year, month, day, hour, minute, timezone, latitude, longitude
    )
    harmonic_planets = _build_harmonic_planets(natal_planets, harmonic_number)
    conjunctions = _find_conjunctions(harmonic_planets, harmonic_number, conjunction_orb)

    return HarmonicChart(
        harmonic_number=harmonic_number,
        name_zh=hdef["name_zh"],
        name_en=hdef["name_en"],
        theme_zh=hdef["theme_zh"],
        theme_en=hdef["theme_en"],
        addey_note_zh=hdef["addey_note_zh"],
        addey_note_en=hdef["addey_note_en"],
        natal_planets=natal_planets,
        harmonic_planets=harmonic_planets,
        conjunctions=conjunctions,
        conjunction_orb=conjunction_orb,
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
    )


def compute_multi_harmonic(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    harmonics: Optional[List[int]] = None,
    location_name: str = "",
    **_kwargs,
) -> MultiHarmonicResult:
    """
    Compute multiple harmonic charts simultaneously for comparative analysis.

    Hamblin (1983): Analyzing multiple harmonics together reveals which planets
    carry the most overall harmonic emphasis — these are the most powerful
    indicators of talent and spiritual quality.

    Args:
        harmonics: List of harmonic numbers to compute.
            Defaults to SUPPORTED_HARMONICS = [1, 2, 3, 4, 5, 7, 9, 12].

    Returns:
        MultiHarmonicResult with individual charts and cross-harmonic analysis.
    """
    if harmonics is None:
        harmonics = SUPPORTED_HARMONICS

    natal_planets = _compute_natal_positions(
        year, month, day, hour, minute, timezone, latitude, longitude
    )

    harmonic_charts: Dict[int, HarmonicChart] = {}
    for n in harmonics:
        orb = DEFAULT_CONJUNCTION_ORB.get(n, max(1.0, 8.0 / math.sqrt(n)))
        hdef = HARMONIC_DEFS.get(n, {
            "name_zh": f"{n}諧波",
            "name_en": f"{n}th Harmonic",
            "theme_zh": "",
            "theme_en": "",
            "addey_note_zh": "",
            "addey_note_en": "",
        })
        h_planets = _build_harmonic_planets(natal_planets, n)
        conjs = _find_conjunctions(h_planets, n, orb)
        harmonic_charts[n] = HarmonicChart(
            harmonic_number=n,
            name_zh=hdef["name_zh"],
            name_en=hdef["name_en"],
            theme_zh=hdef["theme_zh"],
            theme_en=hdef["theme_en"],
            addey_note_zh=hdef["addey_note_zh"],
            addey_note_en=hdef["addey_note_en"],
            natal_planets=natal_planets,
            harmonic_planets=h_planets,
            conjunctions=conjs,
            conjunction_orb=orb,
            year=year, month=month, day=day,
            hour=hour, minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
        )

    # Cross-harmonic emphasis (Hamblin): count conjunctions per planet across all harmonics
    planet_emphasis: Dict[str, set] = {k: set() for k in PLANET_ORDER}
    for n, chart in harmonic_charts.items():
        for conj in chart.conjunctions:
            planet_emphasis[conj.planet_a].add(n)
            planet_emphasis[conj.planet_b].add(n)

    multi_emphasis = sorted(
        [
            {"key": k, "harmonics_active": sorted(v), "count": len(v)}
            for k, v in planet_emphasis.items()
            if v
        ],
        key=lambda x: -x["count"],
    )

    return MultiHarmonicResult(
        natal_planets=natal_planets,
        harmonic_charts=harmonic_charts,
        multi_emphasis=multi_emphasis,
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
    )
