# -*- coding: utf-8 -*-
"""
tests/test_human_design.py — Human Design 人間圖模組測試

Tests cover:
  - Gate/line mapping from ecliptic longitude (Rave Mandala)
  - Design date calculation (Solar Arc ~88°)
  - Planet activation computation
  - Channel and center determination
  - Type, Strategy, Authority derivation
  - Profile computation
  - Definition type analysis
  - Full chart computation with known test cases
  - BodyGraph SVG generation
"""

import math
import pytest

from astro.human_design import (
    compute_human_design_chart,
    HumanDesignChart,
    GateActivation,
    ChannelActivation,
    EXAMPLE_CHARTS,
    CHANNELS,
    CENTER_GATES,
    GATE_SEQUENCE,
    longitude_to_gate_line,
)
from astro.human_design.constants import (
    GATE_TO_CENTER,
    DEGREES_PER_GATE,
    DEGREES_PER_LINE,
    HD_PLANET_NAMES,
    TYPE_ZH,
    AUTHORITY_ZH,
    STRATEGY_ZH,
    PROFILE_INFO,
    VALID_PROFILES,
    MOTOR_CENTERS,
    CENTER_GATES,
)
from astro.human_design.calculator import (
    _datetime_to_jd,
    _find_design_jd,
    _compute_activations,
    _find_active_channels,
    _compute_defined_centers,
    _compute_definition_type,
    _determine_type,
    _determine_authority,
    _compute_profile,
)


# ============================================================
#  Shared fixtures
# ============================================================

@pytest.fixture(scope="module")
def ra_uru_hu_chart() -> HumanDesignChart:
    """Ra Uru Hu — founder of Human Design."""
    ex = EXAMPLE_CHARTS[0]
    return compute_human_design_chart(
        year=ex["year"], month=ex["month"], day=ex["day"],
        hour=ex["hour"], minute=ex["minute"],
        timezone=ex["timezone"],
        latitude=ex["latitude"], longitude=ex["longitude"],
        location_name=ex["location_name"],
    )


@pytest.fixture(scope="module")
def generator_chart() -> HumanDesignChart:
    """Example Generator chart."""
    ex = EXAMPLE_CHARTS[1]
    return compute_human_design_chart(
        year=ex["year"], month=ex["month"], day=ex["day"],
        hour=ex["hour"], minute=ex["minute"],
        timezone=ex["timezone"],
        latitude=ex["latitude"], longitude=ex["longitude"],
        location_name=ex["location_name"],
    )


# ============================================================
#  1. Gate/Line Mapping
# ============================================================

class TestGateLineMapping:
    """Test Rave Mandala gate and line mapping from ecliptic longitude."""

    def test_gate_sequence_length(self):
        assert len(GATE_SEQUENCE) == 64

    def test_gate_sequence_contains_all_gates(self):
        """All 64 gate numbers 1-64 should appear exactly once."""
        assert sorted(GATE_SEQUENCE) == list(range(1, 65))

    def test_zero_degrees_aries_is_gate_25(self):
        gate, _ = longitude_to_gate_line(0.0)
        assert gate == 25, f"0° Aries should be Gate 25, got {gate}"

    def test_gate_at_303_75_is_41(self):
        """303.75° should map to Gate 41 (traditional Rave Mandala start)."""
        gate, _ = longitude_to_gate_line(303.75)
        assert gate == 41, f"303.75° should be Gate 41, got {gate}"

    def test_line_range(self):
        """Lines should always be in [1, 6]."""
        for lon in range(0, 360, 5):
            _, line = longitude_to_gate_line(float(lon))
            assert 1 <= line <= 6, f"Line {line} out of range at {lon}°"

    def test_gate_range(self):
        """Gates should always be in [1, 64]."""
        for lon in range(0, 360):
            gate, _ = longitude_to_gate_line(float(lon))
            assert 1 <= gate <= 64, f"Gate {gate} out of range at {lon}°"

    def test_degrees_per_gate(self):
        """Each gate should span exactly 5.625°."""
        assert abs(DEGREES_PER_GATE - 5.625) < 1e-10

    def test_degrees_per_line(self):
        """Each line should span exactly 0.9375°."""
        assert abs(DEGREES_PER_LINE - 0.9375) < 1e-10

    def test_360_wraps_to_0(self):
        """360° should map the same as 0°."""
        g1, l1 = longitude_to_gate_line(0.0)
        g2, l2 = longitude_to_gate_line(360.0)
        assert g1 == g2
        assert l1 == l2

    def test_continuous_coverage(self):
        """Consecutive 1° steps should always resolve to a valid gate."""
        seen = set()
        for i in range(360):
            gate, _ = longitude_to_gate_line(float(i))
            seen.add(gate)
        # Many gates should be covered in 360 x 1° steps
        assert len(seen) >= 60  # all or nearly all 64 gates

    def test_line_1_at_gate_start(self):
        """Line 1 should be at the very start of each gate."""
        for slot, gate in enumerate(GATE_SEQUENCE):
            lon_start = slot * DEGREES_PER_GATE + 0.001  # just inside the gate
            g, line = longitude_to_gate_line(lon_start)
            assert g == gate
            assert line == 1, f"Gate {gate} slot {slot} start should be line 1, got {line}"


# ============================================================
#  2. Constants integrity
# ============================================================

class TestConstantsIntegrity:
    """Validate consistency of constants tables."""

    def test_all_gates_in_center_map(self):
        """All 64 gates should be assigned to exactly one center."""
        assert len(GATE_TO_CENTER) == 64
        for g in range(1, 65):
            assert g in GATE_TO_CENTER, f"Gate {g} missing from GATE_TO_CENTER"

    def test_center_gates_cover_all_64(self):
        """All gates across all centers should cover 1-64 exactly once."""
        all_gates = [g for gates in CENTER_GATES.values() for g in gates]
        assert len(all_gates) == 64
        assert sorted(all_gates) == list(range(1, 65))

    def test_channel_count(self):
        """There should be exactly 36 channels."""
        assert len(CHANNELS) == 36

    def test_channels_reference_valid_gates(self):
        """Both gates in each channel should be in range 1-64."""
        for ch in CHANNELS:
            assert 1 <= ch.gate_a <= 64, f"Channel {ch} gate_a invalid"
            assert 1 <= ch.gate_b <= 64, f"Channel {ch} gate_b invalid"

    def test_channels_connect_different_centers(self):
        """Each channel must connect two different centers."""
        for ch in CHANNELS:
            ca = GATE_TO_CENTER.get(ch.gate_a)
            cb = GATE_TO_CENTER.get(ch.gate_b)
            assert ca is not None, f"Gate {ch.gate_a} has no center"
            assert cb is not None, f"Gate {ch.gate_b} has no center"
            assert ca != cb, f"Channel {ch.gate_a}-{ch.gate_b} both in center {ca}"

    def test_no_duplicate_channels(self):
        """No duplicate (gate_a, gate_b) or (gate_b, gate_a) pairs."""
        seen = set()
        for ch in CHANNELS:
            pair = tuple(sorted([ch.gate_a, ch.gate_b]))
            assert pair not in seen, f"Duplicate channel: {pair}"
            seen.add(pair)

    def test_valid_profiles_count(self):
        """There should be exactly 12 profiles."""
        assert len(VALID_PROFILES) == 12

    def test_motor_centers_subset(self):
        """Motor centers should be a subset of all centers."""
        all_centers = set(CENTER_GATES.keys())
        assert MOTOR_CENTERS.issubset(all_centers)


# ============================================================
#  3. Design Date Calculation
# ============================================================

class TestDesignDate:
    """Test Solar Arc ~88° design date bisection."""

    def test_design_date_is_before_birth(self):
        """Design JD must be before birth JD."""
        birth_jd = _datetime_to_jd(1985, 3, 15, 14, 30, 8.0)
        design_jd = _find_design_jd(birth_jd)
        assert design_jd < birth_jd

    def test_design_date_roughly_88_days_before(self):
        """Design date should be approximately 88 days before birth (±10 days)."""
        birth_jd = _datetime_to_jd(1985, 3, 15, 14, 30, 8.0)
        design_jd = _find_design_jd(birth_jd)
        days_before = birth_jd - design_jd
        assert 78 <= days_before <= 98, f"Design date {days_before:.1f} days before birth, expected ~88"

    def test_design_sun_is_88_degrees_behind(self):
        """Sun at design JD should be ~88° behind natal Sun."""
        import swisseph as swe
        birth_jd = _datetime_to_jd(1990, 7, 22, 6, 45, 8.0)
        design_jd = _find_design_jd(birth_jd)
        natal_sun = swe.calc_ut(birth_jd, swe.SUN, swe.FLG_SWIEPH)[0][0] % 360
        design_sun = swe.calc_ut(design_jd, swe.SUN, swe.FLG_SWIEPH)[0][0] % 360
        diff = (natal_sun - design_sun) % 360
        assert abs(diff - 88.0) < 0.1, f"Solar Arc diff = {diff:.3f}°, expected ~88°"


# ============================================================
#  4. Activation computation
# ============================================================

class TestActivations:
    """Test planet activation computation."""

    def test_activation_count(self):
        """Should produce exactly 13 activations (one per HD planet)."""
        birth_jd = _datetime_to_jd(1985, 3, 15, 14, 30, 8.0)
        acts = _compute_activations(birth_jd, is_personality=True)
        assert len(acts) == len(HD_PLANET_NAMES) == 13

    def test_personality_flag(self):
        birth_jd = _datetime_to_jd(1985, 3, 15, 14, 30, 8.0)
        acts = _compute_activations(birth_jd, is_personality=True)
        assert all(a.is_personality for a in acts)

    def test_design_flag(self):
        birth_jd = _datetime_to_jd(1985, 3, 15, 14, 30, 8.0)
        design_jd = _find_design_jd(birth_jd)
        acts = _compute_activations(design_jd, is_personality=False)
        assert all(not a.is_personality for a in acts)

    def test_earth_opposite_sun(self):
        """Earth longitude should be approximately Sun + 180°."""
        birth_jd = _datetime_to_jd(1985, 3, 15, 14, 30, 8.0)
        acts = _compute_activations(birth_jd, is_personality=True)
        sun = next(a for a in acts if a.planet == "Sun")
        earth = next(a for a in acts if a.planet == "Earth")
        diff = (earth.longitude - sun.longitude) % 360
        assert abs(diff - 180.0) < 0.01, f"Earth-Sun diff = {diff:.3f}°, expected 180°"

    def test_south_node_opposite_north_node(self):
        """South Node longitude should be approximately North Node + 180°."""
        birth_jd = _datetime_to_jd(1985, 3, 15, 14, 30, 8.0)
        acts = _compute_activations(birth_jd, is_personality=True)
        nn = next(a for a in acts if a.planet == "North Node")
        sn = next(a for a in acts if a.planet == "South Node")
        diff = (sn.longitude - nn.longitude) % 360
        assert abs(diff - 180.0) < 0.01, f"SN-NN diff = {diff:.3f}°, expected 180°"

    def test_activation_gate_in_range(self):
        """All activation gates should be in [1, 64]."""
        birth_jd = _datetime_to_jd(1985, 3, 15, 14, 30, 8.0)
        acts = _compute_activations(birth_jd, is_personality=True)
        for a in acts:
            assert 1 <= a.gate <= 64, f"{a.planet} gate {a.gate} out of range"

    def test_activation_line_in_range(self):
        """All activation lines should be in [1, 6]."""
        birth_jd = _datetime_to_jd(1985, 3, 15, 14, 30, 8.0)
        acts = _compute_activations(birth_jd, is_personality=True)
        for a in acts:
            assert 1 <= a.line <= 6, f"{a.planet} line {a.line} out of range"


# ============================================================
#  5. Full chart computation
# ============================================================

class TestFullChart:
    """Test full HumanDesignChart computation."""

    def test_chart_has_type(self, generator_chart):
        """Chart should have a valid type."""
        valid_types = {"Manifestor", "Generator", "Manifesting Generator", "Projector", "Reflector"}
        assert generator_chart.type_name in valid_types

    def test_chart_has_strategy(self, generator_chart):
        """Chart should have a valid strategy."""
        valid_strategies = {
            "To Inform", "To Respond", "To Respond + Inform",
            "To Wait for Invitation", "To Wait & Reflect",
        }
        assert generator_chart.strategy in valid_strategies

    def test_chart_has_authority(self, generator_chart):
        """Chart should have a valid authority."""
        valid_authorities = {
            "Emotional", "Sacral", "Splenic", "Ego Manifested",
            "Ego Projected", "Self-Projected", "Environmental", "Lunar",
        }
        assert generator_chart.authority in valid_authorities

    def test_chart_has_profile(self, generator_chart):
        """Chart should have a valid profile."""
        profile = generator_chart.profile
        parts = profile.split("/")
        assert len(parts) == 2
        assert 1 <= int(parts[0]) <= 6
        assert 1 <= int(parts[1]) <= 6

    def test_chart_has_definition(self, generator_chart):
        """Chart should have a valid definition type."""
        valid_defs = {"Single", "Split", "Triple Split", "Quad Split", "No Definition"}
        assert generator_chart.definition in valid_defs

    def test_personality_activations_count(self, generator_chart):
        assert len(generator_chart.personality_activations) == 13

    def test_design_activations_count(self, generator_chart):
        assert len(generator_chart.design_activations) == 13

    def test_design_date_is_earlier(self, generator_chart):
        birth_jd = _datetime_to_jd(
            generator_chart.year, generator_chart.month, generator_chart.day,
            generator_chart.hour, generator_chart.minute, generator_chart.timezone,
        )
        assert generator_chart.design_jd < birth_jd

    def test_defined_centers_subset(self, generator_chart):
        """Defined centers must be a subset of all centers."""
        all_centers = set(CENTER_GATES.keys())
        assert generator_chart.defined_centers.issubset(all_centers)

    def test_defined_and_undefined_partition_centers(self, generator_chart):
        """Defined + Undefined should equal all 9 centers."""
        all_centers = set(CENTER_GATES.keys())
        assert generator_chart.defined_centers | generator_chart.undefined_centers == all_centers
        assert generator_chart.defined_centers & generator_chart.undefined_centers == set()

    def test_active_channels_reference_valid_centers(self, generator_chart):
        """All active channel centers should be in the defined set."""
        for ch_act in generator_chart.active_channels:
            assert ch_act.center_a in generator_chart.defined_centers
            assert ch_act.center_b in generator_chart.defined_centers

    def test_cross_gates_are_valid(self, generator_chart):
        """Incarnation cross gates should be valid gate numbers."""
        for g in generator_chart.cross_gates:
            assert 1 <= g <= 64

    def test_sacral_authority_for_generator(self, generator_chart):
        """If type is Generator and Sacral is defined (without SolarPlexus), authority = Sacral."""
        if generator_chart.type_name == "Generator":
            if "Sacral" in generator_chart.defined_centers and \
               "SolarPlexus" not in generator_chart.defined_centers:
                assert generator_chart.authority == "Sacral"

    def test_reflector_has_no_defined_centers(self):
        """A Reflector chart should have no defined centers (all 9 open)."""
        # Synthetic test: if all centers undefined → Reflector
        defined: set = set()
        hd_type = _determine_type(defined, [])
        assert hd_type == "Reflector"
        authority = _determine_authority("Reflector", defined)
        assert authority == "Lunar"

    def test_generator_has_sacral_defined(self, generator_chart):
        """Generator type must always have Sacral defined."""
        if generator_chart.type_name in ("Generator", "Manifesting Generator"):
            assert "Sacral" in generator_chart.defined_centers


# ============================================================
#  6. Profile logic
# ============================================================

class TestProfile:
    def test_profile_format(self, generator_chart):
        parts = generator_chart.profile.split("/")
        assert len(parts) == 2

    def test_profile_line_1_6(self, generator_chart):
        p1, p2 = generator_chart.profile.split("/")
        assert 1 <= int(p1) <= 6
        assert 1 <= int(p2) <= 6

    def test_compute_profile_1_4(self):
        assert _compute_profile(1, 4) == "1/4"

    def test_compute_profile_6_2(self):
        assert _compute_profile(6, 2) == "6/2"


# ============================================================
#  7. SVG generation
# ============================================================

class TestBodygraphSVG:
    def test_svg_is_string(self, generator_chart):
        from astro.human_design.renderer import render_bodygraph_svg
        svg = render_bodygraph_svg(generator_chart)
        assert isinstance(svg, str)

    def test_svg_contains_svg_tag(self, generator_chart):
        from astro.human_design.renderer import render_bodygraph_svg
        svg = render_bodygraph_svg(generator_chart)
        assert "<svg" in svg
        assert "</svg>" in svg

    def test_svg_contains_center_labels(self, generator_chart):
        from astro.human_design.renderer import render_bodygraph_svg
        svg = render_bodygraph_svg(generator_chart)
        assert "HEAD" in svg
        assert "AJNA" in svg
        assert "SAC" in svg

    def test_svg_with_custom_size(self, generator_chart):
        from astro.human_design.renderer import render_bodygraph_svg
        svg = render_bodygraph_svg(generator_chart, width=400, height=500)
        assert 'width="400"' in svg
        assert 'height="500"' in svg
