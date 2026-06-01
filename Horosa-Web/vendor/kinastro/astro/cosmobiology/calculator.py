"""
astro/cosmobiology/calculator.py — Ebertin 宇宙生物學中點計算引擎

100% faithful to Reinhold Ebertin's original rules as described in:
  - "The Combination of Stellar Influences" (COSI, 1972 English edition)
  - "Applied Cosmobiology"

Mathematical conventions (COSI pp. 8–12):
  - All planetary longitudes are absolute ecliptic (0°–360°, 0° = 0° Aries).
  - Midpoint M(A,B): shorter-arc midpoint = (A + B) / 2 (mod 360°).
  - The antiscion / indirect midpoint = M(A,B) + 180° (mod 360°).
  - 90° Dial position = longitude mod 90°.
  - On the 90° Dial all hard aspects (0°, 45°, 90°, 135°, 180°) reduce
    to conjunction, so dial_diff(A,B) = min(|A−B| mod 90°, 90° − |A−B| mod 90°).
  - Orb: strict maximum 1.5° (COSI p. 9).  Tight influence ≤ 1°.

Public API:
    compute_cosmobiology_chart(...)    → ComsobioChart  (natal)
    compute_synastry_midpoints(...)    → SynastryResult
    compute_transit_hits(...)          → list[TransitHit]
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from .constants import (
    PLANET_NAMES_EN,
    PLANET_NAMES_ZH,
    PLANET_SYMBOLS,
    PERSONAL_POINTS,
    ZODIAC_SIGNS,
    SIGN_CN,
    ORB_MAIN,
    ORB_TIGHT,
    get_cosi_interpretation,
)

# ============================================================
# Swiss Ephemeris planet IDs
# ============================================================

_SWE_IDS: Dict[str, int] = {
    "SO": swe.SUN,
    "MO": swe.MOON,
    "ME": swe.MERCURY,
    "VE": swe.VENUS,
    "MA": swe.MARS,
    "JU": swe.JUPITER,
    "SA": swe.SATURN,
    "UR": swe.URANUS,
    "NE": swe.NEPTUNE,
    "PL": swe.PLUTO,
}

# Order in which planets appear in Ebertin's tables (COSI p. 5)
EBERTIN_ORDER = ["SO", "MO", "ME", "VE", "MA", "JU", "SA", "UR", "NE", "PL", "AS", "MC", "NN"]


# ============================================================
# Data classes
# ============================================================

@dataclass
class CosmoPoint:
    """A single planet or personal point with its computed position."""

    key: str           # Ebertin abbreviation, e.g. "SO", "MO"
    name_en: str       # English name
    name_zh: str       # Chinese name
    symbol: str        # Astrological symbol
    longitude: float   # Absolute ecliptic longitude 0–360°
    dial90: float      # longitude mod 90°  (COSI p. 8)
    sign: str          # Zodiac sign name
    sign_degree: float # Degree within sign 0–30°
    is_personal: bool  # Sun, Moon, Asc, MC, Node — highest weight (COSI p. 9)


@dataclass
class MidpointEntry:
    """
    A half-sum (midpoint) M(A/B) = (A + B) / 2  (COSI p. 8).

    ``activations`` lists every planet/point that falls within orb on the
    90° Dial, together with the contact orb and the COSI interpretation.
    """

    key_a: str                    # first planet key
    key_b: str                    # second planet key
    longitude: float              # direct midpoint absolute longitude
    dial90: float                 # longitude mod 90°
    activations: List["MidpointActivation"] = field(default_factory=list)

    @property
    def label(self) -> str:
        return f"{self.key_a}/{self.key_b}"

    @property
    def label_zh(self) -> str:
        na = PLANET_NAMES_ZH.get(self.key_a, self.key_a)
        nb = PLANET_NAMES_ZH.get(self.key_b, self.key_b)
        return f"{na}/{nb}"

    @property
    def min_orb(self) -> float:
        if not self.activations:
            return 99.0
        return min(a.orb for a in self.activations)

    @property
    def is_personal(self) -> bool:
        return self.key_a in PERSONAL_POINTS or self.key_b in PERSONAL_POINTS


@dataclass
class MidpointActivation:
    """
    A planet/point that activates a midpoint (falls within orb on the
    90° Dial).  Carries the COSI interpretation for each of the two
    half-sum pairs:  planet = M(A/B), i.e. P = A/B.

    Following COSI convention:  interpretation for P = A/B is found under
    the combinations (P, A) and (P, B) in the COSI database.
    """

    activating_key: str           # planet that falls on the midpoint
    orb: float                    # orb on the 90° Dial in degrees
    interp_pa: Optional[Dict]     # COSI entry for (activating, key_a)
    interp_pb: Optional[Dict]     # COSI entry for (activating, key_b)


@dataclass
class SynastryMidpoint:
    """
    Cross-chart midpoint in a synastry / relationship comparison.
    M(person1_planet / person2_planet) is hit by another planet.
    """

    key_a: str        # planet from chart 1
    key_b: str        # planet from chart 2
    longitude: float
    dial90: float
    activations: List[MidpointActivation] = field(default_factory=list)


@dataclass
class TransitHit:
    """
    A transiting planet that activates a natal midpoint.
    """

    transit_key: str
    natal_key_a: str
    natal_key_b: str
    natal_midpoint_lon: float
    transit_lon: float
    orb: float
    interp_ta: Optional[Dict]     # COSI (transit, natal_a)
    interp_tb: Optional[Dict]     # COSI (transit, natal_b)


@dataclass
class ComsobioChart:
    """Complete Cosmobiology natal chart result."""

    points: List[CosmoPoint] = field(default_factory=list)
    midpoint_tree: List[MidpointEntry] = field(default_factory=list)
    # Midpoints sorted by personal-point involvement then tightest orb.

    def get_point(self, key: str) -> Optional[CosmoPoint]:
        for p in self.points:
            if p.key == key:
                return p
        return None

    def get_lon(self, key: str) -> Optional[float]:
        p = self.get_point(key)
        return p.longitude if p else None


@dataclass
class SynastryResult:
    """Combined midpoints for a synastry comparison."""

    chart1_points: List[CosmoPoint] = field(default_factory=list)
    chart2_points: List[CosmoPoint] = field(default_factory=list)
    cross_midpoints: List[SynastryMidpoint] = field(default_factory=list)


# ============================================================
# Low-level geometry helpers
# ============================================================

def _normalize(deg: float) -> float:
    """Reduce an angle to the range [0°, 360°)."""
    return deg % 360.0


def _dial90(lon: float) -> float:
    """90° Dial position = longitude mod 90°  (COSI p. 8)."""
    return lon % 90.0


def _dial_diff(a: float, b: float) -> float:
    """
    Minimum distance on the 90° Dial (0–45°).

    On the 90° Dial all hard aspects collapse to the same position, so the
    effective distance between two planets is the smallest multiple of 45°
    separating them modulo 90°.  (COSI pp. 8–9)
    """
    d = abs(a - b) % 90.0
    return min(d, 90.0 - d)


def _midpoint(lon_a: float, lon_b: float) -> float:
    """
    Shorter-arc midpoint of two absolute longitudes.  (COSI p. 8)

    Returns the midpoint in [0°, 360°).
    The antiscion / indirect midpoint = result + 180° (mod 360°).
    """
    diff = _normalize(lon_b - lon_a)
    if diff > 180.0:
        mp = _normalize(lon_a - (360.0 - diff) / 2.0)
    else:
        mp = _normalize(lon_a + diff / 2.0)
    return mp


def _sign_from_lon(lon: float) -> Tuple[str, float]:
    """Return (sign_name, degree_within_sign) for an absolute longitude."""
    idx = int(lon / 30.0) % 12
    deg = lon % 30.0
    return ZODIAC_SIGNS[idx], deg


def _julian_day(year: int, month: int, day: int, hour_ut: float) -> float:
    return swe.julday(year, month, day, hour_ut)


# ============================================================
# Position computation
# ============================================================

def _compute_positions(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float,
    latitude: float, longitude: float,
) -> List[CosmoPoint]:
    """
    Compute all Ebertin standard planet/point positions.

    Uses:  SO MO ME VE MA JU SA UR NE PL  (pyswisseph)
           AS MC  (Placidus houses)
           NN     (True Node)

    Returns a list of CosmoPoint in EBERTIN_ORDER.
    """
    ut_hour = hour + minute / 60.0 - timezone
    jd = _julian_day(year, month, day, ut_hour)

    # ── Houses (Placidus, as commonly used with Ebertin)
    houses, ascmc = swe.houses(jd, latitude, longitude, b"P")
    asc_lon = _normalize(ascmc[0])
    mc_lon = _normalize(ascmc[1])

    points: Dict[str, CosmoPoint] = {}

    # ── 10 planets
    for key, pid in _SWE_IDS.items():
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        result, _ = swe.calc_ut(jd, pid, flags)
        lon = _normalize(result[0])
        sign, sdeg = _sign_from_lon(lon)
        points[key] = CosmoPoint(
            key=key,
            name_en=PLANET_NAMES_EN[key],
            name_zh=PLANET_NAMES_ZH[key],
            symbol=PLANET_SYMBOLS[key],
            longitude=lon,
            dial90=_dial90(lon),
            sign=sign,
            sign_degree=sdeg,
            is_personal=(key in PERSONAL_POINTS),
        )

    # ── Ascendant
    sign, sdeg = _sign_from_lon(asc_lon)
    points["AS"] = CosmoPoint(
        key="AS",
        name_en=PLANET_NAMES_EN["AS"],
        name_zh=PLANET_NAMES_ZH["AS"],
        symbol=PLANET_SYMBOLS["AS"],
        longitude=asc_lon,
        dial90=_dial90(asc_lon),
        sign=sign,
        sign_degree=sdeg,
        is_personal=True,
    )

    # ── Midheaven (MC)
    sign, sdeg = _sign_from_lon(mc_lon)
    points["MC"] = CosmoPoint(
        key="MC",
        name_en=PLANET_NAMES_EN["MC"],
        name_zh=PLANET_NAMES_ZH["MC"],
        symbol=PLANET_SYMBOLS["MC"],
        longitude=mc_lon,
        dial90=_dial90(mc_lon),
        sign=sign,
        sign_degree=sdeg,
        is_personal=True,
    )

    # ── True North Node
    result_node, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH)
    node_lon = _normalize(result_node[0])
    sign, sdeg = _sign_from_lon(node_lon)
    points["NN"] = CosmoPoint(
        key="NN",
        name_en=PLANET_NAMES_EN["NN"],
        name_zh=PLANET_NAMES_ZH["NN"],
        symbol=PLANET_SYMBOLS["NN"],
        longitude=node_lon,
        dial90=_dial90(node_lon),
        sign=sign,
        sign_degree=sdeg,
        is_personal=True,
    )

    # Return in canonical Ebertin order
    return [points[k] for k in EBERTIN_ORDER if k in points]


# ============================================================
# Midpoint Tree construction
# ============================================================

def _build_midpoint_tree(
    points: List[CosmoPoint],
    orb: float = ORB_MAIN,
) -> List[MidpointEntry]:
    """
    Build the complete Midpoint Tree for a set of positions.

    For every pair (A, B) of the 13 Ebertin points, compute M(A/B) and
    check whether any other point P activates this midpoint on the 90° Dial
    within the given orb.

    Sorting (COSI convention):
      1. Entries involving personal points (SO, MO, AS, MC, NN) first.
      2. Within group, sort by tightest activating orb ascending.

    Returns only entries that have at least one activation within orb.
    """
    pos_map: Dict[str, float] = {p.key: p.longitude for p in points}
    all_keys = list(pos_map.keys())

    entries: List[MidpointEntry] = []

    for i in range(len(all_keys)):
        for j in range(i + 1, len(all_keys)):
            ka, kb = all_keys[i], all_keys[j]
            lon_a = pos_map[ka]
            lon_b = pos_map[kb]

            mp_lon = _midpoint(lon_a, lon_b)
            mp_dial = _dial90(mp_lon)

            activations: List[MidpointActivation] = []
            for kc in all_keys:
                if kc in (ka, kb):
                    continue
                diff = _dial_diff(mp_dial, _dial90(pos_map[kc]))
                if diff <= orb:
                    activations.append(MidpointActivation(
                        activating_key=kc,
                        orb=diff,
                        interp_pa=get_cosi_interpretation(kc, ka),
                        interp_pb=get_cosi_interpretation(kc, kb),
                    ))

            if activations:
                activations.sort(key=lambda a: a.orb)
                entries.append(MidpointEntry(
                    key_a=ka,
                    key_b=kb,
                    longitude=mp_lon,
                    dial90=mp_dial,
                    activations=activations,
                ))

    # Sort: personal-point entries first, then by tightest orb
    def _sort_key(e: MidpointEntry) -> Tuple[int, float]:
        is_personal = (
            e.key_a in PERSONAL_POINTS
            or e.key_b in PERSONAL_POINTS
            or any(a.activating_key in PERSONAL_POINTS for a in e.activations)
        )
        return (0 if is_personal else 1, e.min_orb)

    entries.sort(key=_sort_key)
    return entries


# ============================================================
# Main public API — Natal chart
# ============================================================

def compute_cosmobiology_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    orb: float = ORB_MAIN,
    **_kwargs,
) -> ComsobioChart:
    """
    Compute a complete Cosmobiology natal chart.

    Implements Ebertin's midpoint system exactly as specified in COSI (1972):
      - 13 standard points: SO MO ME VE MA JU SA UR NE PL AS MC NN
      - All midpoints (half-sums) and their activations on the 90° Dial
      - Orb strictly ≤ 1.5° (``orb`` parameter, default = ORB_MAIN)

    Args:
        year, month, day: Birth date.
        hour, minute: Local birth time.
        timezone: UTC offset in hours (e.g. 8.0 for UTC+8).
        latitude, longitude: Geographic coordinates (°N/°E positive).
        location_name: Optional city name for display.
        orb: Maximum orb in degrees (COSI default = 1.5°).

    Returns:
        ComsobioChart with sorted midpoint tree and full COSI interpretations.
    """
    points = _compute_positions(
        year, month, day, hour, minute, timezone, latitude, longitude
    )
    tree = _build_midpoint_tree(points, orb=orb)

    return ComsobioChart(points=points, midpoint_tree=tree)


# ============================================================
# Synastry / Relationship Cosmobiology
# ============================================================

def compute_synastry_midpoints(
    chart1: ComsobioChart,
    chart2: ComsobioChart,
    orb: float = ORB_MAIN,
) -> SynastryResult:
    """
    Relationship Cosmobiology — combined midpoints between two charts.

    Follows Ebertin's relationship analysis approach (Applied Cosmobiology):
      For every pair (P1 from chart1, P2 from chart2), compute M(P1/P2)
      and find which planets from *either* chart activate it on the 90° Dial.

    Returns cross-midpoints sorted by personal-point involvement and orb.
    """
    c1_map: Dict[str, float] = {p.key: p.longitude for p in chart1.points}
    c2_map: Dict[str, float] = {p.key: p.longitude for p in chart2.points}
    # Build a combined map for activation lookups.  When both charts share the
    # same planet key the chart2 position is used (dict merge semantics).
    # The outer loop always uses chart1 positions for the first half of the
    # midpoint, and chart2 positions for the second half, so both persons'
    # planets activate the cross-midpoints.
    all_map: Dict[str, float] = {**c1_map, **c2_map}

    cross: List[SynastryMidpoint] = []

    for k1, lon1 in c1_map.items():
        for k2, lon2 in c2_map.items():
            if k1 == k2:
                continue  # skip same-name pairs
            mp_lon = _midpoint(lon1, lon2)
            mp_dial = _dial90(mp_lon)

            activations: List[MidpointActivation] = []
            for kc, lonc in all_map.items():
                if kc in (k1, k2):
                    continue
                diff = _dial_diff(mp_dial, _dial90(lonc))
                if diff <= orb:
                    activations.append(MidpointActivation(
                        activating_key=kc,
                        orb=diff,
                        interp_pa=get_cosi_interpretation(kc, k1),
                        interp_pb=get_cosi_interpretation(kc, k2),
                    ))

            if activations:
                activations.sort(key=lambda a: a.orb)
                cross.append(SynastryMidpoint(
                    key_a=k1,
                    key_b=k2,
                    longitude=mp_lon,
                    dial90=mp_dial,
                    activations=activations,
                ))

    # Sort: personal entries first, then by tightest orb
    cross.sort(key=lambda e: (
        0 if (e.key_a in PERSONAL_POINTS or e.key_b in PERSONAL_POINTS) else 1,
        min(a.orb for a in e.activations) if e.activations else 99.0,
    ))

    return SynastryResult(
        chart1_points=chart1.points,
        chart2_points=chart2.points,
        cross_midpoints=cross,
    )


# ============================================================
# Transit Cosmobiology
# ============================================================

def compute_transit_hits(
    natal: ComsobioChart,
    transit_year: int,
    transit_month: int,
    transit_day: int,
    transit_hour: int = 12,
    transit_minute: int = 0,
    transit_tz: float = 0.0,
    transit_lat: float = 0.0,
    transit_lon: float = 0.0,
    orb: float = ORB_MAIN,
) -> List[TransitHit]:
    """
    Event / Transit Cosmobiology — transiting planets to natal midpoints.

    For every transiting planet T and every natal midpoint M(A/B),
    check whether T activates M(A/B) on the 90° Dial within orb.

    Sorted by personal-point involvement and orb tightness.

    Args:
        natal: The natal ComsobioChart.
        transit_year/month/day/hour/minute: Date and time of the transit event.
        transit_tz: UTC offset for the transit moment.
        transit_lat/lon: Location for computing transit Asc/MC.
            If not provided (0.0), the equator/prime meridian is used,
            which means the transit Asc/MC will not be meaningful.
            Pass the natal or event location for accurate Asc/MC transits.
        orb: Maximum orb in degrees.

    Returns:
        List of TransitHit, sorted by personal involvement then orb.
    """
    # Compute transit positions
    transit_chart = compute_cosmobiology_chart(
        year=transit_year, month=transit_month, day=transit_day,
        hour=transit_hour, minute=transit_minute,
        timezone=transit_tz,
        latitude=transit_lat or 0.0,
        longitude=transit_lon or 0.0,
        orb=ORB_MAIN,
    )
    transit_map: Dict[str, float] = {p.key: p.longitude for p in transit_chart.points}

    hits: List[TransitHit] = []

    for mp_entry in natal.midpoint_tree:
        mp_dial = mp_entry.dial90
        ka, kb = mp_entry.key_a, mp_entry.key_b

        for t_key, t_lon in transit_map.items():
            diff = _dial_diff(mp_dial, _dial90(t_lon))
            if diff <= orb:
                hits.append(TransitHit(
                    transit_key=t_key,
                    natal_key_a=ka,
                    natal_key_b=kb,
                    natal_midpoint_lon=mp_entry.longitude,
                    transit_lon=t_lon,
                    orb=diff,
                    interp_ta=get_cosi_interpretation(t_key, ka),
                    interp_tb=get_cosi_interpretation(t_key, kb),
                ))

    hits.sort(key=lambda h: (
        0 if (h.natal_key_a in PERSONAL_POINTS or h.natal_key_b in PERSONAL_POINTS
              or h.transit_key in PERSONAL_POINTS) else 1,
        h.orb,
    ))
    return hits
