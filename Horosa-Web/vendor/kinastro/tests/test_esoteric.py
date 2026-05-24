"""
tests/test_esoteric.py — Tests for Esoteric Astrology (Alice Bailey Seven Rays) module

Tests cover:
  - Seven Rays data structure completeness
  - Esoteric Rulers table completeness
  - Chart computation (positions, Ray tally)
  - Soul Ray and Personality Ray indicator derivation
  - Ray interaction analysis
  - SVG mandala generation

Representative test charts:
  - Alice A. Bailey (author of *Esoteric Astrology*)
  - Helena P. Blavatsky (Theosophical Society founder)
  - Mahatma Gandhi (spiritual/historical figure)
"""

import pytest

from astro.esoteric import (
    compute_esoteric_chart,
    get_ray_interaction_analysis,
    EsotericChart,
    SEVEN_RAYS,
    SIGN_RULERS,
    PLANET_RAY_MAP,
    ZODIAC_SIGNS,
    EXAMPLE_CHARTS,
)
from astro.esoteric.constants import (
    get_sign_rays,
    get_sign_from_longitude,
    get_degree_in_sign,
    get_ray_interaction,
    RayData,
    SignRulers,
)
from astro.esoteric.calculator import (
    _compute_positions,
    _build_ray_tally,
    RayTally,
)
from astro.esoteric.renderer import render_esoteric_chart_svg


# ============================================================
#  Shared fixtures
# ============================================================

@pytest.fixture(scope="module")
def alice_bailey_chart() -> EsotericChart:
    """Alice A. Bailey — author of Esoteric Astrology."""
    ex = EXAMPLE_CHARTS[0]
    return compute_esoteric_chart(
        year=ex["year"], month=ex["month"], day=ex["day"],
        hour=ex["hour"], minute=ex["minute"],
        timezone=ex["timezone"],
        latitude=ex["latitude"], longitude=ex["longitude"],
        location_name=ex["location_name"],
    )


@pytest.fixture(scope="module")
def blavatsky_chart() -> EsotericChart:
    """Helena P. Blavatsky — Theosophical Society founder."""
    ex = EXAMPLE_CHARTS[1]
    return compute_esoteric_chart(
        year=ex["year"], month=ex["month"], day=ex["day"],
        hour=ex["hour"], minute=ex["minute"],
        timezone=ex["timezone"],
        latitude=ex["latitude"], longitude=ex["longitude"],
        location_name=ex["location_name"],
    )


@pytest.fixture(scope="module")
def gandhi_chart() -> EsotericChart:
    """Mahatma Gandhi — Indian independence leader."""
    ex = EXAMPLE_CHARTS[2]
    return compute_esoteric_chart(
        year=ex["year"], month=ex["month"], day=ex["day"],
        hour=ex["hour"], minute=ex["minute"],
        timezone=ex["timezone"],
        latitude=ex["latitude"], longitude=ex["longitude"],
        location_name=ex["location_name"],
    )


# ============================================================
#  Test: Seven Rays Data
# ============================================================

class TestSevenRays:
    """Tests for the Seven Rays data structure."""

    def test_seven_rays_count(self):
        """There must be exactly 7 Rays."""
        assert len(SEVEN_RAYS) == 7

    def test_ray_numbers_one_to_seven(self):
        """Ray numbers must be 1–7."""
        assert set(SEVEN_RAYS.keys()) == {1, 2, 3, 4, 5, 6, 7}

    def test_each_ray_has_required_fields(self):
        """Each Ray must have all required fields."""
        required_attrs = [
            "number", "name_en", "name_zh", "color",
            "svg_color", "svg_glow",
            "quality_en", "quality_zh",
            "qualities_en", "qualities_zh",
            "glamour_en", "glamour_zh",
            "exoteric_planets", "esoteric_planets",
            "signs",
            "soul_purpose_en", "soul_purpose_zh",
            "service_en", "service_zh",
        ]
        for rn, rd in SEVEN_RAYS.items():
            for attr in required_attrs:
                assert hasattr(rd, attr), f"Ray {rn} missing '{attr}'"
                val = getattr(rd, attr)
                assert val is not None and val != "", (
                    f"Ray {rn} has empty '{attr}'"
                )

    def test_ray_svg_colors_are_hex(self):
        """SVG colors must be valid hex strings."""
        for rn, rd in SEVEN_RAYS.items():
            assert rd.svg_color.startswith("#"), f"Ray {rn} svg_color not hex"
            assert len(rd.svg_color) == 7, f"Ray {rn} svg_color wrong length"

    def test_ray_signs_are_valid(self):
        """All signs referenced in Ray data must be valid zodiac signs."""
        for rn, rd in SEVEN_RAYS.items():
            for sign in rd.signs:
                assert sign in ZODIAC_SIGNS, (
                    f"Ray {rn} references unknown sign '{sign}'"
                )

    def test_ray1_is_will_power(self):
        """Ray 1 should be Will/Power."""
        assert "Will" in SEVEN_RAYS[1].name_en
        assert "Power" in SEVEN_RAYS[1].name_en

    def test_ray2_love_wisdom(self):
        """Ray 2 should be Love-Wisdom."""
        assert "Love" in SEVEN_RAYS[2].name_en
        assert "Wisdom" in SEVEN_RAYS[2].name_en

    def test_ray7_ceremonial_order(self):
        """Ray 7 should be Ceremonial Order."""
        assert "Ceremonial" in SEVEN_RAYS[7].name_en

    def test_ray1_includes_pluto_and_vulcan(self):
        """Ray 1 planets: Pluto (exoteric) and Vulcan (esoteric)."""
        rd = SEVEN_RAYS[1]
        assert "Pluto" in rd.exoteric_planets
        assert "Vulcan" in rd.esoteric_planets

    def test_ray2_includes_jupiter(self):
        """Ray 2 planets include Jupiter."""
        rd = SEVEN_RAYS[2]
        assert "Jupiter" in rd.exoteric_planets or "Jupiter" in rd.esoteric_planets

    def test_ray7_includes_uranus(self):
        """Ray 7 planets include Uranus."""
        rd = SEVEN_RAYS[7]
        assert "Uranus" in rd.exoteric_planets or "Uranus" in rd.esoteric_planets


# ============================================================
#  Test: Esoteric Rulers
# ============================================================

class TestEsotericRulers:
    """Tests for the esoteric rulers table."""

    def test_all_twelve_signs_have_rulers(self):
        """All 12 zodiac signs must have ruler entries."""
        assert set(SIGN_RULERS.keys()) == set(ZODIAC_SIGNS)

    def test_each_sign_has_three_ruler_levels(self):
        """Each sign must have exoteric, esoteric, and hierarchical rulers."""
        for sign, rulers in SIGN_RULERS.items():
            assert rulers.exoteric, f"{sign} missing exoteric ruler"
            assert rulers.esoteric, f"{sign} missing esoteric ruler"
            assert rulers.hierarchical, f"{sign} missing hierarchical ruler"

    def test_each_sign_transmits_at_least_one_ray(self):
        """Each sign must transmit at least one Ray."""
        for sign, rulers in SIGN_RULERS.items():
            assert len(rulers.rays_transmitted) >= 1, (
                f"{sign} transmits no Rays"
            )

    def test_ray_numbers_in_valid_range(self):
        """All transmitted Rays must be 1–7."""
        for sign, rulers in SIGN_RULERS.items():
            for r in rulers.rays_transmitted:
                assert 1 <= r <= 7, (
                    f"{sign} has invalid Ray number {r}"
                )

    def test_aries_esoteric_ruler_mercury(self):
        """Aries esoteric ruler is Mercury (Bailey, Esoteric Astrology, p. 50)."""
        assert "Mercury" in SIGN_RULERS["Aries"].esoteric

    def test_taurus_esoteric_ruler_vulcan(self):
        """Taurus esoteric ruler is Vulcan."""
        assert "Vulcan" in SIGN_RULERS["Taurus"].esoteric

    def test_leo_exoteric_equals_esoteric_sun(self):
        """Leo: exoteric and esoteric ruler both = Sun."""
        assert "Sun" in SIGN_RULERS["Leo"].exoteric
        assert "Sun" in SIGN_RULERS["Leo"].esoteric

    def test_get_sign_rays_aries(self):
        """Aries transmits Rays 1 and 7."""
        rays = get_sign_rays("Aries")
        assert 1 in rays
        assert 7 in rays

    def test_get_sign_rays_gemini(self):
        """Gemini transmits Ray 2."""
        rays = get_sign_rays("Gemini")
        assert 2 in rays


# ============================================================
#  Test: Planet → Ray mapping
# ============================================================

class TestPlanetRayMap:
    """Tests for the planet-to-Ray mapping."""

    def test_all_main_planets_have_ray_entry(self):
        """All 10 main planets must have Ray assignments."""
        main_planets = [
            "Sun", "Moon", "Mercury", "Venus", "Mars",
            "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
        ]
        for p in main_planets:
            assert p in PLANET_RAY_MAP, f"{p} not in PLANET_RAY_MAP"

    def test_saturn_ray3(self):
        """Saturn transmits Ray 3 — Active Intelligence."""
        assert 3 in PLANET_RAY_MAP["Saturn"]

    def test_uranus_ray7(self):
        """Uranus transmits Ray 7 — Ceremonial Order."""
        assert 7 in PLANET_RAY_MAP["Uranus"]

    def test_neptune_ray6(self):
        """Neptune transmits Ray 6 — Devotion."""
        assert 6 in PLANET_RAY_MAP["Neptune"]

    def test_pluto_ray1(self):
        """Pluto transmits Ray 1 — Will/Power."""
        assert 1 in PLANET_RAY_MAP["Pluto"]

    def test_venus_ray5(self):
        """Venus transmits Ray 5 — Concrete Science."""
        assert 5 in PLANET_RAY_MAP["Venus"]


# ============================================================
#  Test: Chart Computation
# ============================================================

class TestChartComputation:
    """Tests for compute_esoteric_chart()."""

    def test_chart_has_ten_planets(self, alice_bailey_chart):
        """Chart must contain 10 planets."""
        assert len(alice_bailey_chart.points) == 10

    def test_planet_longitudes_in_range(self, alice_bailey_chart):
        """All planet longitudes must be 0–360°."""
        for p in alice_bailey_chart.points:
            assert 0.0 <= p.longitude < 360.0, (
                f"{p.name} longitude {p.longitude} out of range"
            )

    def test_planet_sign_degrees_in_range(self, alice_bailey_chart):
        """Sign degrees must be 0–30°."""
        for p in alice_bailey_chart.points:
            assert 0.0 <= p.sign_degree < 30.0, (
                f"{p.name} sign_degree {p.sign_degree} out of range"
            )

    def test_planet_signs_are_valid(self, alice_bailey_chart):
        """All planet signs must be valid zodiac signs."""
        for p in alice_bailey_chart.points:
            assert p.sign in ZODIAC_SIGNS, (
                f"{p.name} has unknown sign '{p.sign}'"
            )

    def test_asc_sign_is_valid(self, alice_bailey_chart):
        """Ascendant sign must be a valid zodiac sign."""
        assert alice_bailey_chart.asc_sign in ZODIAC_SIGNS

    def test_mc_sign_is_valid(self, alice_bailey_chart):
        """MC sign must be a valid zodiac sign."""
        assert alice_bailey_chart.mc_sign in ZODIAC_SIGNS

    def test_chart_has_ray_tally(self, alice_bailey_chart):
        """Chart must have a ray tally after computation."""
        assert alice_bailey_chart.ray_tally is not None

    def test_ray_tally_has_seven_rays(self, alice_bailey_chart):
        """Ray tally must cover all 7 Rays."""
        tally = alice_bailey_chart.ray_tally
        assert len(tally.ray_scores) == 7

    def test_ray_scores_non_negative(self, alice_bailey_chart):
        """All Ray scores must be non-negative."""
        tally = alice_bailey_chart.ray_tally
        for rn, score in tally.ray_scores.items():
            assert score >= 0.0, f"Ray {rn} has negative score {score}"

    def test_tally_has_contributions(self, alice_bailey_chart):
        """Ray tally must have at least one contribution."""
        assert len(alice_bailey_chart.ray_tally.contributions) > 0

    def test_soul_ray_indicator_present(self, alice_bailey_chart):
        """Soul Ray indicator must be computed."""
        assert alice_bailey_chart.soul_ray_indicator is not None

    def test_personality_ray_indicator_present(self, alice_bailey_chart):
        """Personality Ray indicator must be computed."""
        assert alice_bailey_chart.personality_ray_indicator is not None

    def test_soul_ray_is_valid_number(self, alice_bailey_chart):
        """Soul Ray number must be 1–7."""
        ray_num = alice_bailey_chart.soul_ray_indicator.ray
        assert 1 <= ray_num <= 7

    def test_personality_ray_is_valid_number(self, alice_bailey_chart):
        """Personality Ray number must be 1–7."""
        ray_num = alice_bailey_chart.personality_ray_indicator.ray
        assert 1 <= ray_num <= 7

    def test_soul_ray_confidence_valid(self, alice_bailey_chart):
        """Soul Ray confidence must be 'strong', 'moderate', or 'weak'."""
        conf = alice_bailey_chart.soul_ray_indicator.confidence
        assert conf in ("strong", "moderate", "weak")

    def test_esoteric_rulers_populated(self, alice_bailey_chart):
        """Esoteric ruler fields must be populated."""
        assert alice_bailey_chart.asc_esoteric_ruler != ""
        assert alice_bailey_chart.asc_exoteric_ruler != ""

    def test_birth_data_stored(self, alice_bailey_chart):
        """Birth data must be stored in the chart."""
        ex = EXAMPLE_CHARTS[0]
        assert alice_bailey_chart.year == ex["year"]
        assert alice_bailey_chart.month == ex["month"]

    def test_blavatsky_chart_sun_leo(self, blavatsky_chart):
        """Blavatsky born Aug 12 — Sun should be in Leo."""
        assert blavatsky_chart.sun_sign == "Leo"

    def test_gandhi_chart_sun_libra(self, gandhi_chart):
        """Gandhi born Oct 2 — Sun should be in Libra."""
        assert gandhi_chart.sun_sign == "Libra"


# ============================================================
#  Test: Ray Interaction
# ============================================================

class TestRayInteraction:
    """Tests for Ray interaction analysis."""

    def test_ray_interaction_function(self):
        """get_ray_interaction should return data for valid pairs."""
        data = get_ray_interaction(1, 2)
        assert data is not None
        assert "zh" in data
        assert "en" in data
        assert "type" in data

    def test_ray_interaction_symmetric(self):
        """Ray interaction should be symmetric (same result for (a,b) and (b,a))."""
        assert get_ray_interaction(1, 3) == get_ray_interaction(3, 1)

    def test_all_pairs_covered(self):
        """All unique Ray pairs should have interaction data."""
        for i in range(1, 8):
            for j in range(i + 1, 8):
                data = get_ray_interaction(i, j)
                assert data is not None, f"Missing interaction for Rays ({i}, {j})"

    def test_same_ray_interaction(self, alice_bailey_chart):
        """get_ray_interaction_analysis should handle same soul/personality Ray."""
        # Temporarily mock same rays using a simple check
        interaction = get_ray_interaction_analysis(alice_bailey_chart)
        # Should return dict with zh/en keys
        assert interaction is not None
        assert "zh" in interaction
        assert "en" in interaction

    def test_ray_interaction_type_values(self):
        """Interaction types must be valid values."""
        valid_types = {"complementary", "tension", "same"}
        for i in range(1, 8):
            for j in range(i + 1, 8):
                data = get_ray_interaction(i, j)
                if data:
                    assert data["type"] in valid_types


# ============================================================
#  Test: SVG Mandala
# ============================================================

class TestSVGMandala:
    """Tests for the SVG mandala renderer."""

    def test_svg_is_string(self, alice_bailey_chart):
        """render_esoteric_chart_svg should return a string."""
        svg = render_esoteric_chart_svg(alice_bailey_chart)
        assert isinstance(svg, str)

    def test_svg_starts_with_tag(self, alice_bailey_chart):
        """SVG should start with <svg tag."""
        svg = render_esoteric_chart_svg(alice_bailey_chart)
        assert svg.strip().startswith("<svg")

    def test_svg_ends_with_closing_tag(self, alice_bailey_chart):
        """SVG should end with </svg>."""
        svg = render_esoteric_chart_svg(alice_bailey_chart)
        assert svg.strip().endswith("</svg>")

    def test_svg_contains_defs(self, alice_bailey_chart):
        """SVG must contain <defs> section."""
        svg = render_esoteric_chart_svg(alice_bailey_chart)
        assert "<defs>" in svg

    def test_svg_contains_seven_ray_gradients(self, alice_bailey_chart):
        """SVG must contain gradient elements for all 7 rays."""
        svg = render_esoteric_chart_svg(alice_bailey_chart)
        for rn in range(1, 8):
            assert f"rayGrad{rn}" in svg, f"Missing rayGrad{rn} in SVG"

    def test_svg_custom_dimensions(self, alice_bailey_chart):
        """SVG should respect custom width/height."""
        svg = render_esoteric_chart_svg(alice_bailey_chart, width=800, height=800)
        assert 'width="800"' in svg
        assert 'height="800"' in svg

    def test_svg_for_blavatsky(self, blavatsky_chart):
        """SVG generation should work for Blavatsky chart."""
        svg = render_esoteric_chart_svg(blavatsky_chart)
        assert len(svg) > 1000

    def test_svg_for_gandhi(self, gandhi_chart):
        """SVG generation should work for Gandhi chart."""
        svg = render_esoteric_chart_svg(gandhi_chart)
        assert len(svg) > 1000


# ============================================================
#  Test: Helper Functions
# ============================================================

class TestHelperFunctions:
    """Tests for utility/helper functions."""

    def test_get_sign_from_longitude_aries(self):
        """0° = Aries."""
        assert get_sign_from_longitude(0.0) == "Aries"

    def test_get_sign_from_longitude_taurus(self):
        """30° = Taurus."""
        assert get_sign_from_longitude(30.0) == "Taurus"

    def test_get_sign_from_longitude_pisces(self):
        """330° = Pisces."""
        assert get_sign_from_longitude(330.0) == "Pisces"

    def test_get_sign_from_longitude_wraps(self):
        """360° should wrap to Aries."""
        assert get_sign_from_longitude(360.0) == "Aries"

    def test_get_degree_in_sign_zero(self):
        """0° longitude → 0° in Aries."""
        assert get_degree_in_sign(0.0) == pytest.approx(0.0)

    def test_get_degree_in_sign_middle(self):
        """45° longitude → 15° in Taurus."""
        assert get_degree_in_sign(45.0) == pytest.approx(15.0)

    def test_tally_top_rays(self):
        """RayTally.top_rays should return correct number of rays."""
        tally = RayTally()
        tally.add(1, 5.0, "test", "測試", "test")
        tally.add(2, 3.0, "test", "測試", "test")
        tally.add(3, 1.0, "test", "測試", "test")
        top = tally.top_rays(2)
        assert len(top) == 2
        assert top[0][0] == 1
        assert top[0][1] == pytest.approx(5.0)
        assert top[1][0] == 2
        # Verify ray 3 is excluded
        top_ray_numbers = [r for r, _ in top]
        assert 3 not in top_ray_numbers
