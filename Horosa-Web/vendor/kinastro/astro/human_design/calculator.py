# -*- coding: utf-8 -*-
"""
astro/human_design/calculator.py — Human Design 人間圖核心計算模組

Core Human Design calculation engine (Ra Uru Hu system).

計算流程 / Calculation flow:
  1. Personality chart: planetary positions at exact birth time.
  2. Design chart: positions when the Sun was ~88° behind birth-time Sun
     (Solar Arc ~88°, approximately 88 days before birth).
     Computed via bisection search on the Sun's longitude.
  3. Gate activations: each planet's ecliptic longitude → gate + line
     via the Rave Mandala (64-gate wheel, 5.625° per gate).
  4. Defined centers: a center is defined if at least one complete channel
     (both gate endpoints active in either chart) is activated.
  5. Type, Strategy, Authority from defined-center pattern.
  6. Profile from Personality Sun line / Design Sun line.
  7. Definition type from connected-component analysis of defined centers.
  8. Incarnation Cross from the 4 gate activations of Sun/Earth (P+D).

All planet positions use pyswisseph with FLG_SWIEPH | FLG_SPEED flags.

Test charts:
  - Ra Uru Hu (1948-04-09 08:00 Montreal)
  - Example Generator (1985-03-15 14:30 Taipei)
  - Example Projector (1990-07-22 06:45 Hong Kong)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

import swisseph as swe

from .constants import (
    CENTER_GATES,
    CHANNELS,
    CROSS_ANGLE_BY_LINE,
    CROSS_ANGLE_ZH,
    DEFINITION_EN,
    DEFINITION_ZH,
    EXAMPLE_CHARTS,
    GATE_CHANNELS,
    GATE_SEQUENCE,
    GATE_TO_CENTER,
    HD_PLANET_NAMES,
    MOTOR_CENTERS,
    OPPOSITE_LINE,
    PLANET_ZH,
    PROFILE_INFO,
    STRATEGY_ZH,
    SWE_PLANET_IDS,
    TYPE_INFO,
    TYPE_ZH,
    AUTHORITY_ZH,
    AUTHORITY_INFO,
    ChannelDef,
    longitude_to_gate_line,
)

# pyswisseph flags
_SWE_FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED


# ============================================================
#  Data classes
# ============================================================

@dataclass
class GateActivation:
    """A single gate + line activation from a planet."""
    planet: str          # planet name
    gate: int            # 1–64
    line: int            # 1–6
    longitude: float     # ecliptic longitude
    retrograde: bool = False
    is_personality: bool = True  # True = Personality (conscious), False = Design (unconscious)

    @property
    def gate_line(self) -> str:
        return f"{self.gate}.{self.line}"

    @property
    def chart_label(self) -> str:
        return "P" if self.is_personality else "D"


@dataclass
class ChannelActivation:
    """An active channel (both gates triggered)."""
    channel: ChannelDef
    gate_a_source: str   # planet name activating gate_a (e.g. "P:Sun" or "D:Moon")
    gate_b_source: str   # planet name activating gate_b
    center_a: str
    center_b: str

    @property
    def name_en(self) -> str:
        return self.channel.name_en

    @property
    def name_zh(self) -> str:
        return self.channel.name_zh

    @property
    def gates(self) -> Tuple[int, int]:
        return self.channel.gates


@dataclass
class HumanDesignChart:
    """Complete Human Design chart result."""

    # --- Birth data
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude_birth: float
    location_name: str

    # --- Design date (Julian Day when Sun was ~88° behind natal Sun)
    design_jd: float
    design_year: int
    design_month: int
    design_day: int

    # --- Gate activations (13 planets × 2 charts = up to 26 activations)
    personality_activations: List[GateActivation] = field(default_factory=list)
    design_activations: List[GateActivation] = field(default_factory=list)

    # --- Derived: all active gates (set)
    active_gates: Set[int] = field(default_factory=set)

    # --- Channels and centers
    active_channels: List[ChannelActivation] = field(default_factory=list)
    defined_centers: Set[str] = field(default_factory=set)
    undefined_centers: Set[str] = field(default_factory=set)

    # --- Type, Strategy, Authority, Profile
    type_name: str = ""
    strategy: str = ""
    authority: str = ""
    profile: str = ""                # e.g. "1/3"
    definition: str = ""             # Single / Split / Triple Split / Quad Split / No Definition

    # --- Incarnation Cross
    cross_angle: str = ""            # Right Angle / Juxtaposition / Left Angle
    cross_gates: Tuple[int, int, int, int] = field(default_factory=lambda: (0, 0, 0, 0))
    # (P_Sun_gate, P_Earth_gate, D_Sun_gate, D_Earth_gate)
    cross_name_en: str = ""
    cross_name_zh: str = ""

    # --- Personality and Design Sun/Earth gate lines (for profile + cross)
    p_sun_gate: int = 0
    p_sun_line: int = 0
    p_earth_gate: int = 0
    p_earth_line: int = 0
    d_sun_gate: int = 0
    d_sun_line: int = 0
    d_earth_gate: int = 0
    d_earth_line: int = 0

    def get_personality_gate(self, planet: str) -> Optional[GateActivation]:
        for a in self.personality_activations:
            if a.planet == planet:
                return a
        return None

    def get_design_gate(self, planet: str) -> Optional[GateActivation]:
        for a in self.design_activations:
            if a.planet == planet:
                return a
        return None


# ============================================================
#  Julian Day helpers
# ============================================================

def _datetime_to_jd(year: int, month: int, day: int,
                    hour: int, minute: int, timezone: float) -> float:
    """Convert local birth datetime to Julian Day (Universal Time)."""
    ut_hour = hour + minute / 60.0 - timezone
    return swe.julday(year, month, day, ut_hour)


def _jd_to_date(jd: float) -> Tuple[int, int, int]:
    """Convert Julian Day to (year, month, day) Gregorian."""
    y, m, d, _ = swe.revjul(jd)
    return int(y), int(m), int(d)


# ============================================================
#  Planet position helpers
# ============================================================

def _get_sun_longitude(jd: float) -> float:
    """Return Sun's ecliptic longitude at given Julian Day."""
    result, _ = swe.calc_ut(jd, swe.SUN, _SWE_FLAGS)
    return result[0] % 360.0


def _find_design_jd(birth_jd: float) -> float:
    """
    Find the Julian Day when the Sun was exactly 88° behind the natal Sun
    (Solar Arc = 88°). Uses bisection on the Sun's longitudinal position.

    The Design chart is calculated when the prenatal Sun position equals:
      natal_sun_longitude - 88° (mod 360°)

    We search backwards ~85–95 days from birth.

    Args:
        birth_jd: Julian Day of birth (UT)

    Returns:
        Julian Day of the Design moment
    """
    natal_sun = _get_sun_longitude(birth_jd)
    target_lon = (natal_sun - 88.0) % 360.0

    # Search in window [birth - 95 days, birth - 80 days]
    jd_lo = birth_jd - 95.0
    jd_hi = birth_jd - 80.0

    def _sun_minus_target(jd: float) -> float:
        """Return angular difference Sun(jd) - target_lon, normalised to (-180, 180]."""
        lon = _get_sun_longitude(jd)
        diff = (lon - target_lon + 360.0) % 360.0
        if diff > 180.0:
            diff -= 360.0
        return diff

    # Bisection (50 iterations → ~10^-15 day precision, well within 1 second)
    for _ in range(50):
        jd_mid = (jd_lo + jd_hi) / 2.0
        f_mid = _sun_minus_target(jd_mid)
        if abs(f_mid) < 1e-10:
            break
        f_lo = _sun_minus_target(jd_lo)
        if f_lo * f_mid < 0:
            jd_hi = jd_mid
        else:
            jd_lo = jd_mid

    return (jd_lo + jd_hi) / 2.0


# ============================================================
#  Planet activation computation
# ============================================================

def _compute_activations(jd: float, is_personality: bool) -> List[GateActivation]:
    """
    Compute gate/line activations for all 13 HD planets at the given Julian Day.

    The 13 planets are: Sun, Earth (= Sun + 180°), North Node, South Node
    (= North Node + 180°), Moon, Mercury, Venus, Mars, Jupiter, Saturn,
    Uranus, Neptune, Pluto.

    Args:
        jd: Julian Day (UT)
        is_personality: True for Personality (birth) chart, False for Design chart

    Returns:
        List of GateActivation (one per planet)
    """
    activations: List[GateActivation] = []

    for planet_name in HD_PLANET_NAMES:
        if planet_name == "Earth":
            # Earth = Sun + 180°
            result, _ = swe.calc_ut(jd, swe.SUN, _SWE_FLAGS)
            lon = (result[0] + 180.0) % 360.0
            retrograde = False
        elif planet_name == "South Node":
            # South Node = North Node + 180°
            result, _ = swe.calc_ut(jd, swe.TRUE_NODE, _SWE_FLAGS)
            lon = (result[0] + 180.0) % 360.0
            retrograde = False
        else:
            pid = SWE_PLANET_IDS[planet_name]
            result, _ = swe.calc_ut(jd, pid, _SWE_FLAGS)
            lon = result[0] % 360.0
            retrograde = result[3] < 0  # speed < 0 → retrograde

        gate, line = longitude_to_gate_line(lon)
        activations.append(GateActivation(
            planet=planet_name,
            gate=gate,
            line=line,
            longitude=lon,
            retrograde=retrograde,
            is_personality=is_personality,
        ))

    return activations


# ============================================================
#  Channel and center determination
# ============================================================

def _find_active_channels(
    all_gates: Set[int],
    p_gates: Set[int],
    d_gates: Set[int],
    p_activations: List[GateActivation],
    d_activations: List[GateActivation],
) -> List[ChannelActivation]:
    """
    Identify all active channels (both gate endpoints present in all_gates).

    A channel is active when BOTH its gate endpoints are activated by any
    planet in either the Personality or Design chart.

    Returns list of ChannelActivation.
    """
    active: List[ChannelActivation] = []

    # Map gate → source label for display
    def _source_label(gate: int) -> str:
        labels = []
        for act in p_activations:
            if act.gate == gate:
                labels.append(f"P:{act.planet}")
        for act in d_activations:
            if act.gate == gate:
                labels.append(f"D:{act.planet}")
        return ", ".join(labels) if labels else "?"

    for ch in CHANNELS:
        if ch.gate_a in all_gates and ch.gate_b in all_gates:
            ca = GATE_TO_CENTER.get(ch.gate_a, "?")
            cb = GATE_TO_CENTER.get(ch.gate_b, "?")
            active.append(ChannelActivation(
                channel=ch,
                gate_a_source=_source_label(ch.gate_a),
                gate_b_source=_source_label(ch.gate_b),
                center_a=ca,
                center_b=cb,
            ))
    return active


def _compute_defined_centers(
    active_channels: List[ChannelActivation],
) -> Tuple[Set[str], Set[str]]:
    """
    Determine which centers are defined (connected by at least one active channel).

    Returns (defined_centers, undefined_centers).
    """
    defined: Set[str] = set()
    for ch_act in active_channels:
        defined.add(ch_act.center_a)
        defined.add(ch_act.center_b)
    all_centers = set(CENTER_GATES.keys())
    undefined = all_centers - defined
    return defined, undefined


# ============================================================
#  Connected-component analysis for Definition type
# ============================================================

def _compute_definition_type(defined_centers: Set[str],
                               active_channels: List[ChannelActivation]) -> str:
    """
    Determine Definition type by counting connected components among defined centers.

    Single Definition   = 1 component
    Split Definition    = 2 components
    Triple Split        = 3 components
    Quad Split          = 4 components
    No Definition       = 0 (Reflector)
    """
    if not defined_centers:
        return "No Definition"

    # Build adjacency for defined centers
    adj: Dict[str, Set[str]] = {c: set() for c in defined_centers}
    for ch_act in active_channels:
        ca, cb = ch_act.center_a, ch_act.center_b
        if ca in adj and cb in adj:
            adj[ca].add(cb)
            adj[cb].add(ca)

    # BFS/DFS connected components
    visited: Set[str] = set()
    components = 0
    for start in defined_centers:
        if start not in visited:
            components += 1
            stack = [start]
            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                stack.extend(adj[node] - visited)

    return {1: "Single", 2: "Split", 3: "Triple Split", 4: "Quad Split"}.get(
        components, "No Definition"
    )


# ============================================================
#  Type determination
# ============================================================

def _is_throat_motor_connected(
    defined_centers: Set[str],
    active_channels: List[ChannelActivation],
    exclude_sacral: bool = False,
) -> bool:
    """
    Check whether the Throat is reachable from any motor center
    via defined channels (BFS on defined center graph).

    If exclude_sacral is True, the Sacral center is treated as absent
    (used for Manifestor check: motor connection excluding Sacral).
    """
    if "Throat" not in defined_centers:
        return False

    targets = MOTOR_CENTERS & defined_centers
    if exclude_sacral:
        targets -= {"Sacral"}
    if not targets:
        return False

    # Build adjacency
    adj: Dict[str, Set[str]] = {c: set() for c in defined_centers}
    for ch_act in active_channels:
        ca, cb = ch_act.center_a, ch_act.center_b
        if ca in adj and cb in adj:
            adj[ca].add(cb)
            adj[cb].add(ca)

    # BFS from Throat toward any motor
    visited: Set[str] = {"Throat"}
    queue = ["Throat"]
    while queue:
        node = queue.pop(0)
        for neighbour in adj.get(node, set()):
            if neighbour in targets:
                return True
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
    return False


def _determine_type(
    defined_centers: Set[str],
    active_channels: List[ChannelActivation],
) -> str:
    """
    Determine the Human Design Type from defined centers.

    Rules:
      Reflector              — all centers undefined
      Generator              — Sacral defined, Throat NOT connected to Sacral via motors
      Manifesting Generator  — Sacral defined, Throat connected (via defined path) to Sacral
      Manifestor             — Sacral NOT defined, Throat connected to a non-Sacral motor
      Projector              — Sacral NOT defined, no motor drives Throat (or no Throat at all)
    """
    if not defined_centers:
        return "Reflector"

    sacral_defined = "Sacral" in defined_centers

    if sacral_defined:
        # Check if Throat is connected to Sacral (directly or via other defined centers)
        if _sacral_reaches_throat(defined_centers, active_channels):
            return "Manifesting Generator"
        return "Generator"
    else:
        # No Sacral
        if _is_throat_motor_connected(defined_centers, active_channels, exclude_sacral=True):
            return "Manifestor"
        return "Projector"


def _sacral_reaches_throat(
    defined_centers: Set[str],
    active_channels: List[ChannelActivation],
) -> bool:
    """Return True if Sacral center can reach Throat via defined channels (BFS)."""
    if "Sacral" not in defined_centers or "Throat" not in defined_centers:
        return False
    adj: Dict[str, Set[str]] = {c: set() for c in defined_centers}
    for ch_act in active_channels:
        ca, cb = ch_act.center_a, ch_act.center_b
        if ca in adj and cb in adj:
            adj[ca].add(cb)
            adj[cb].add(ca)
    visited: Set[str] = {"Sacral"}
    queue = ["Sacral"]
    while queue:
        node = queue.pop(0)
        for nb in adj.get(node, set()):
            if nb == "Throat":
                return True
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return False


# ============================================================
#  Authority determination
# ============================================================

def _determine_authority(
    hd_type: str,
    defined_centers: Set[str],
) -> str:
    """
    Determine Inner Authority in priority order:

    1. Solar Plexus (Emotional) — if SolarPlexus defined
    2. Sacral — if Sacral defined (and SolarPlexus not)
    3. Splenic — if Spleen defined (SolarPlexus + Sacral not)
    4. Ego — if Ego defined (above not)
       → "Ego Manifested" for Manifestors, "Ego Projected" for Projectors
    5. Self-Projected (G center) — Projector only (above not)
    6. Environmental (Mental Projector) — Head/Ajna defined only
    7. Lunar — Reflector
    """
    if hd_type == "Reflector":
        return "Lunar"
    if "SolarPlexus" in defined_centers:
        return "Emotional"
    if "Sacral" in defined_centers:
        return "Sacral"
    if "Spleen" in defined_centers:
        return "Splenic"
    if "Ego" in defined_centers:
        if hd_type == "Manifestor":
            return "Ego Manifested"
        return "Ego Projected"
    if "G" in defined_centers and hd_type == "Projector":
        return "Self-Projected"
    return "Environmental"


# ============================================================
#  Profile computation
# ============================================================

def _compute_profile(p_sun_line: int, d_sun_line: int) -> str:
    """
    Compute the Profile string (e.g. "1/3") from Personality and Design Sun lines.

    The Profile is simply "{p_sun_line}/{d_sun_line}". In a correctly computed
    chart the Design Sun line should be the "opposite" (complementary) of the
    Personality Sun line (1↔4, 2↔5, 3↔6), but we return the raw combination
    for accuracy and leave validation to the caller.
    """
    return f"{p_sun_line}/{d_sun_line}"


# ============================================================
#  Incarnation Cross
# ============================================================

def _compute_incarnation_cross(
    p_sun_gate: int, p_sun_line: int,
    p_earth_gate: int,
    d_sun_gate: int,
    d_earth_gate: int,
) -> Tuple[str, str, str, str]:
    """
    Determine the Incarnation Cross angle and construct a name.

    Cross angle is determined by the Personality Sun line:
      Lines 1-3 → Right Angle Cross
      Line 4    → Juxtaposition Cross
      Lines 5-6 → Left Angle Cross

    The cross name combines the 4 gate activations:
      "{angle} Cross of {P_Sun_gate}.{P_Sun_line} / {P_Earth_gate} / {D_Sun_gate} / {D_Earth_gate}"

    Returns: (cross_angle_en, cross_angle_zh, cross_name_en, cross_name_zh)
    """
    angle_en = CROSS_ANGLE_BY_LINE.get(p_sun_line, "Right Angle")
    angle_zh = CROSS_ANGLE_ZH.get(angle_en, "右角度")

    name_en = (
        f"{angle_en} Cross of the {p_sun_gate}.{p_sun_line} "
        f"({p_earth_gate}/{d_sun_gate}/{d_earth_gate})"
    )
    name_zh = (
        f"{angle_zh}十字架：閘門 {p_sun_gate}.{p_sun_line} "
        f"/ {p_earth_gate} / {d_sun_gate} / {d_earth_gate}"
    )
    return angle_en, angle_zh, name_en, name_zh


# ============================================================
#  Main compute function
# ============================================================

def compute_human_design_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
) -> HumanDesignChart:
    """
    Compute a complete Human Design chart.

    Args:
        year, month, day: Birth date (Gregorian)
        hour, minute: Local birth time (24h)
        timezone: UTC offset in hours (e.g. 8.0 for UTC+8)
        latitude: Birth latitude (decimal degrees, N positive)
        longitude: Birth longitude (decimal degrees, E positive)
        location_name: Optional label for the birth location

    Returns:
        HumanDesignChart — complete chart with activations, centers, type, etc.
    """
    # 1. Birth Julian Day (Personality)
    birth_jd = _datetime_to_jd(year, month, day, hour, minute, timezone)

    # 2. Design Julian Day (~88° Solar Arc before birth)
    design_jd = _find_design_jd(birth_jd)
    d_year, d_month, d_day = _jd_to_date(design_jd)

    # 3. Compute activations
    p_acts = _compute_activations(birth_jd, is_personality=True)
    d_acts = _compute_activations(design_jd, is_personality=False)

    # 4. All active gates (union)
    p_gates = {a.gate for a in p_acts}
    d_gates = {a.gate for a in d_acts}
    all_gates = p_gates | d_gates

    # 5. Active channels
    active_channels = _find_active_channels(all_gates, p_gates, d_gates, p_acts, d_acts)

    # 6. Defined centers
    defined_centers, undefined_centers = _compute_defined_centers(active_channels)

    # 7. Type, strategy, authority
    hd_type = _determine_type(defined_centers, active_channels)
    type_data = TYPE_INFO.get(hd_type, {})
    strategy = type_data.get("strategy", "")
    authority = _determine_authority(hd_type, defined_centers)

    # 8. Profile
    p_sun = next((a for a in p_acts if a.planet == "Sun"), None)
    d_sun = next((a for a in d_acts if a.planet == "Sun"), None)
    p_earth = next((a for a in p_acts if a.planet == "Earth"), None)
    d_earth = next((a for a in d_acts if a.planet == "Earth"), None)

    p_sun_gate  = p_sun.gate  if p_sun   else 0
    p_sun_line  = p_sun.line  if p_sun   else 0
    d_sun_gate  = d_sun.gate  if d_sun   else 0
    d_sun_line  = d_sun.line  if d_sun   else 0
    p_earth_gate = p_earth.gate if p_earth else 0
    d_earth_gate = d_earth.gate if d_earth else 0

    profile = _compute_profile(p_sun_line, d_sun_line)

    # 9. Definition type
    definition = _compute_definition_type(defined_centers, active_channels)

    # 10. Incarnation Cross
    angle_en, _angle_zh, cross_name_en, cross_name_zh = _compute_incarnation_cross(
        p_sun_gate, p_sun_line, p_earth_gate, d_sun_gate, d_earth_gate
    )

    return HumanDesignChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute, timezone=timezone,
        latitude=latitude, longitude_birth=longitude,
        location_name=location_name,
        design_jd=design_jd,
        design_year=d_year, design_month=d_month, design_day=d_day,
        personality_activations=p_acts,
        design_activations=d_acts,
        active_gates=all_gates,
        active_channels=active_channels,
        defined_centers=defined_centers,
        undefined_centers=undefined_centers,
        type_name=hd_type,
        strategy=strategy,
        authority=authority,
        profile=profile,
        definition=definition,
        cross_angle=angle_en,
        cross_gates=(p_sun_gate, p_earth_gate, d_sun_gate, d_earth_gate),
        cross_name_en=cross_name_en,
        cross_name_zh=cross_name_zh,
        p_sun_gate=p_sun_gate, p_sun_line=p_sun_line,
        p_earth_gate=p_earth_gate, p_earth_line=p_earth.line if p_earth else 0,
        d_sun_gate=d_sun_gate, d_sun_line=d_sun_line,
        d_earth_gate=d_earth_gate, d_earth_line=d_earth.line if d_earth else 0,
    )
