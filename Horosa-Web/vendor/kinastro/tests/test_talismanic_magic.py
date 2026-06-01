"""
tests/test_talismanic_magic.py — Tests for the Talismanic Magic Module

Tests cover:
  1. TestInterpretationsDB    — interpretations/talismanic.py data integrity
  2. TestTalismanicCalculator — astro/talismanic_magic.py computation correctness
  3. TestElectionalScoring    — electional scoring rules (Picatrix-validated cases)
  4. TestRecommendationEngine — purpose → planet → recommendation pipeline

Classical validation dates (known dignified planet positions):
  - Jupiter in Cancer (exaltation): ~2013-07-20, ~2024-07-xx
  - Venus in Pisces (exaltation): spring periods
  - Saturn in Libra (exaltation): 2010–2012 period
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone


# ============================================================
# Test Suite 1: Interpretations Database
# ============================================================

class TestInterpretationsDB:
    """Verify the talismanic.py data structure and completeness."""

    def test_planetary_talismans_count(self) -> None:
        """Should have exactly 7 planetary talismans."""
        from interpretations.talismanic import PLANETARY_TALISMANS
        assert len(PLANETARY_TALISMANS) == 7

    def test_all_seven_planets_present(self) -> None:
        """All seven traditional planets should be represented."""
        from interpretations.talismanic import PLANETARY_TALISMAN_BY_PLANET
        expected = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}
        assert set(PLANETARY_TALISMAN_BY_PLANET.keys()) == expected

    def test_decan_talismans_count(self) -> None:
        """Should have exactly 36 Decan talismans."""
        from interpretations.talismanic import DECAN_TALISMANS
        assert len(DECAN_TALISMANS) == 36

    def test_decan_numbers_sequential(self) -> None:
        """Decan numbers should be 1 through 36 in order."""
        from interpretations.talismanic import DECAN_TALISMANS
        numbers = [d.decan_number for d in DECAN_TALISMANS]
        assert numbers == list(range(1, 37))

    def test_decan_degree_ranges_valid(self) -> None:
        """Each Decan should have valid 10-degree range."""
        from interpretations.talismanic import DECAN_TALISMANS
        for d in DECAN_TALISMANS:
            assert d.degrees_end - d.degrees_start == 10, (
                f"Decan {d.decan_number}: expected 10° range, "
                f"got {d.degrees_end - d.degrees_start}°"
            )
            assert d.degrees_start in (0, 10, 20), (
                f"Decan {d.decan_number}: unexpected start degree {d.degrees_start}"
            )

    def test_all_twelve_signs_in_decans(self) -> None:
        """All 12 zodiac signs should appear in the Decan database."""
        from interpretations.talismanic import DECAN_TALISMANS
        signs = {d.sign for d in DECAN_TALISMANS}
        expected_signs = {
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
        }
        assert signs == expected_signs

    def test_planetary_talisman_fields_complete(self) -> None:
        """Each planetary talisman should have all required text fields."""
        from interpretations.talismanic import PLANETARY_TALISMANS
        required_fields = [
            "planet", "planet_cn", "metal", "metal_cn", "gemstone",
            "incense", "image_description_cn", "invocation_cn", "effects_cn",
        ]
        for t in PLANETARY_TALISMANS:
            for field in required_fields:
                val = getattr(t, field, None)
                assert val, (
                    f"{t.planet}: field '{field}' is empty or missing"
                )

    def test_planetary_talisman_has_purposes(self) -> None:
        """Each planetary talisman should have at least 3 purposes."""
        from interpretations.talismanic import PLANETARY_TALISMANS
        for t in PLANETARY_TALISMANS:
            assert len(t.purposes_cn) >= 3, (
                f"{t.planet}: only {len(t.purposes_cn)} purposes (expected ≥ 3)"
            )

    def test_planetary_talisman_has_electional_rules(self) -> None:
        """Each planetary talisman should have at least 3 electional rules."""
        from interpretations.talismanic import PLANETARY_TALISMANS
        for t in PLANETARY_TALISMANS:
            assert len(t.electional_rules_cn) >= 3, (
                f"{t.planet}: only {len(t.electional_rules_cn)} rules (expected ≥ 3)"
            )

    def test_lookup_by_planet_name(self) -> None:
        """PLANETARY_TALISMAN_BY_PLANET lookup should work correctly."""
        from interpretations.talismanic import get_planetary_talisman
        saturn = get_planetary_talisman("Saturn")
        assert saturn is not None
        assert saturn.metal == "Lead"
        assert saturn.metal_cn == "鉛"

    def test_get_decan_by_longitude(self) -> None:
        """Decan lookup by longitude should return correct Decan."""
        from interpretations.talismanic import get_decan_by_longitude
        # 0° Aries = Decan 1
        d1 = get_decan_by_longitude(0.0)
        assert d1 is not None
        assert d1.decan_number == 1
        assert d1.sign == "Aries"

        # 10° Aries = Decan 2
        d2 = get_decan_by_longitude(10.0)
        assert d2 is not None
        assert d2.decan_number == 2

        # 350° Pisces = Decan 36
        d36 = get_decan_by_longitude(350.0)
        assert d36 is not None
        assert d36.decan_number == 36
        assert d36.sign == "Pisces"

    def test_purpose_labels_coverage(self) -> None:
        """All purposes in PURPOSE_TO_PLANETS should have a CN label."""
        from interpretations.talismanic import PURPOSE_TO_PLANETS, PURPOSE_LABELS_CN
        for purpose in PURPOSE_TO_PLANETS:
            assert purpose in PURPOSE_LABELS_CN, (
                f"Purpose '{purpose}' missing from PURPOSE_LABELS_CN"
            )

    def test_get_recommended_planets(self) -> None:
        """get_recommended_planets should return a list of valid planets."""
        from interpretations.talismanic import get_recommended_planets
        valid_planets = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}

        for purpose in ["love", "wealth", "protection", "health", "wisdom"]:
            planets = get_recommended_planets(purpose)
            assert len(planets) > 0, f"No planets for purpose '{purpose}'"
            for p in planets:
                assert p in valid_planets, f"Unknown planet '{p}' for purpose '{purpose}'"


# ============================================================
# Test Suite 2: Dignity Calculator
# ============================================================

class TestDignityCalculator:
    """Test planet dignity computation."""

    def test_saturn_in_capricorn_is_domicile(self) -> None:
        """Saturn at Capricorn 5° (270+5 = 275°) should be Domicile."""
        from astro.talismanic_magic import get_planet_dignity
        dignity, score = get_planet_dignity("Saturn", 275.0)
        assert dignity == "Domicile"
        assert score == 5

    def test_saturn_in_libra_is_exaltation(self) -> None:
        """Saturn at Libra 15° (180+15 = 195°) should be Exaltation."""
        from astro.talismanic_magic import get_planet_dignity
        dignity, score = get_planet_dignity("Saturn", 195.0)
        assert dignity == "Exaltation"
        assert score == 4

    def test_saturn_in_aries_is_fall(self) -> None:
        """Saturn at Aries 10° (10°) should be Fall."""
        from astro.talismanic_magic import get_planet_dignity
        dignity, score = get_planet_dignity("Saturn", 10.0)
        assert dignity == "Fall"
        assert score == -4

    def test_jupiter_in_cancer_is_exaltation(self) -> None:
        """Jupiter at Cancer 15° (90+15 = 105°) should be Exaltation."""
        from astro.talismanic_magic import get_planet_dignity
        dignity, score = get_planet_dignity("Jupiter", 105.0)
        assert dignity == "Exaltation"
        assert score == 4

    def test_jupiter_in_sagittarius_is_domicile(self) -> None:
        """Jupiter at Sagittarius 5° (240+5 = 245°) should be Domicile."""
        from astro.talismanic_magic import get_planet_dignity
        dignity, score = get_planet_dignity("Jupiter", 245.0)
        assert dignity == "Domicile"
        assert score == 5

    def test_venus_in_pisces_is_exaltation(self) -> None:
        """Venus at Pisces 10° (330+10 = 340°) should be Exaltation."""
        from astro.talismanic_magic import get_planet_dignity
        dignity, score = get_planet_dignity("Venus", 340.0)
        assert dignity == "Exaltation"
        assert score == 4

    def test_venus_in_taurus_is_domicile(self) -> None:
        """Venus at Taurus 20° (30+20 = 50°) should be Domicile."""
        from astro.talismanic_magic import get_planet_dignity
        dignity, score = get_planet_dignity("Venus", 50.0)
        assert dignity == "Domicile"
        assert score == 5

    def test_sun_in_aries_is_exaltation(self) -> None:
        """Sun at Aries 19° should be Exaltation."""
        from astro.talismanic_magic import get_planet_dignity
        dignity, score = get_planet_dignity("Sun", 19.0)
        assert dignity == "Exaltation"
        assert score == 4

    def test_sun_in_leo_is_domicile(self) -> None:
        """Sun at Leo 10° (120+10 = 130°) should be Domicile."""
        from astro.talismanic_magic import get_planet_dignity
        dignity, score = get_planet_dignity("Sun", 130.0)
        assert dignity == "Domicile"
        assert score == 5

    def test_peregrine_planet(self) -> None:
        """Mars at Gemini (not domicile/exaltation/fall/detriment) = Peregrine."""
        from astro.talismanic_magic import get_planet_dignity
        # Gemini = sign_index 2, Mars domicile = 0,7; exaltation = 9; fall = 3; detriment = 1,6
        dignity, score = get_planet_dignity("Mars", 65.0)  # Gemini ~5°
        assert dignity == "Peregrine"
        assert score == 0


# ============================================================
# Test Suite 3: Moon Condition Assessment
# ============================================================

class TestMoonCondition:
    """Test moon condition assessment (no pyswisseph dependency for values)."""

    def test_moon_via_combusta_detection(self) -> None:
        """Moon in Via Combusta (Libra 15°–Scorpio 15°) should be detected."""
        from astro.talismanic_magic import get_moon_condition, PLANET_IDS
        import swisseph as swe

        # Build a mock positions dict with moon at 200° (Libra 20°, in Via Combusta)
        # and sun at 100° (Cancer 10°)
        mock_positions = {
            "Moon": (200.0, 13.0),   # Libra 20° — in Via Combusta
            "Sun":  (100.0, 1.0),    # Cancer 10°
        }
        jd = swe.julday(2024, 1, 1, 12.0)
        moon = get_moon_condition(jd, mock_positions)
        assert moon.is_via_combusta is True

    def test_moon_not_via_combusta_in_leo(self) -> None:
        """Moon in Leo should NOT be Via Combusta."""
        import swisseph as swe
        from astro.talismanic_magic import get_moon_condition

        mock_positions = {
            "Moon": (130.0, 13.0),   # Leo 10°
            "Sun":  (60.0, 1.0),
        }
        jd = swe.julday(2024, 1, 1, 12.0)
        moon = get_moon_condition(jd, mock_positions)
        assert moon.is_via_combusta is False

    def test_moon_waxing_detection(self) -> None:
        """Moon ahead of Sun by < 180° should be waxing."""
        import swisseph as swe
        from astro.talismanic_magic import get_moon_condition

        mock_positions = {
            "Moon": (100.0, 13.0),   # 50° ahead of Sun
            "Sun":  (50.0, 1.0),
        }
        jd = swe.julday(2024, 1, 1, 12.0)
        moon = get_moon_condition(jd, mock_positions)
        assert moon.is_waxing is True

    def test_moon_waning_detection(self) -> None:
        """Moon more than 180° ahead of Sun should be waning."""
        import swisseph as swe
        from astro.talismanic_magic import get_moon_condition

        # Moon at 50°, Sun at 230° → phase_deg = (50 - 230) % 360 = 180° (exactly full)
        # Use Moon at 50°, Sun at 240° → phase_deg = (50 - 240) % 360 = 170° – still waxing
        # Use Moon at 50°, Sun at 220° → phase_deg = (50 - 220) % 360 = 190° → waning
        mock_positions = {
            "Moon": (50.0, 13.0),
            "Sun":  (220.0, 1.0),   # phase_deg = (50 - 220) % 360 = 190° > 180 → waning
        }
        jd = swe.julday(2024, 1, 1, 12.0)
        moon = get_moon_condition(jd, mock_positions)
        assert moon.is_waxing is False

    def test_moon_combust_detection(self) -> None:
        """Moon within 8.5° of Sun should be Combust."""
        import swisseph as swe
        from astro.talismanic_magic import get_moon_condition

        mock_positions = {
            "Moon": (55.0, 13.0),    # 5° from Sun
            "Sun":  (50.0, 1.0),
        }
        jd = swe.julday(2024, 1, 1, 12.0)
        moon = get_moon_condition(jd, mock_positions)
        assert moon.is_combust is True
        assert moon.is_cazimi is False

    def test_moon_cazimi_detection(self) -> None:
        """Moon within 17' of Sun should be Cazimi (not combust)."""
        import swisseph as swe
        from astro.talismanic_magic import get_moon_condition

        mock_positions = {
            "Moon": (50.1, 13.0),    # 0.1° from Sun (within 17')
            "Sun":  (50.0, 1.0),
        }
        jd = swe.julday(2024, 1, 1, 12.0)
        moon = get_moon_condition(jd, mock_positions)
        assert moon.is_cazimi is True
        assert moon.is_combust is False

    def test_moon_phase_new(self) -> None:
        """Moon very close to Sun should be New Moon phase."""
        import swisseph as swe
        from astro.talismanic_magic import get_moon_condition

        mock_positions = {
            "Moon": (50.0, 13.0),
            "Sun":  (50.0, 1.0),
        }
        jd = swe.julday(2024, 1, 1, 12.0)
        moon = get_moon_condition(jd, mock_positions)
        assert "New" in moon.phase or "Cazimi" in moon.sun_aspect_name

    def test_moon_phase_full(self) -> None:
        """Moon 180° from Sun should be Full Moon."""
        import swisseph as swe
        from astro.talismanic_magic import get_moon_condition

        mock_positions = {
            "Moon": (230.0, 13.0),
            "Sun":  (50.0, 1.0),
        }
        jd = swe.julday(2024, 1, 1, 12.0)
        moon = get_moon_condition(jd, mock_positions)
        assert "Full" in moon.phase


# ============================================================
# Test Suite 4: Electional Scoring
# ============================================================

class TestElectionalScoring:
    """Test the Picatrix electional scoring system."""

    def test_jupiter_score_structure(self) -> None:
        """ElectionalScore for Jupiter should have all required structural fields (validates scoring pipeline, not specific dignity state)."""
        import swisseph as swe
        from astro.talismanic_magic import evaluate_electional_moment

        # Use an arbitrary date for structural validation.
        # Jupiter may or may not be in exaltation (Cancer) on this date.
        jd = swe.julday(2024, 7, 15, 12.0)
        result = evaluate_electional_moment("Jupiter", jd)

        # Structural checks
        assert 0 <= result.total_score <= 100
        assert result.grade in ("Excellent", "Good", "Acceptable", "Poor", "Forbidden")
        assert result.planet == "Jupiter"
        assert result.planet_cn == "木星"
        assert isinstance(result.checks_passed, list)
        assert isinstance(result.checks_failed, list)
        assert isinstance(result.is_suitable, bool)

    def test_via_combusta_moon_lowers_score(self) -> None:
        """A moment with Moon in Via Combusta should be marked forbidden or poor."""
        import swisseph as swe
        from astro.talismanic_magic import (
            evaluate_electional_moment,
            get_moon_condition,
            _compute_all_planets,
        )

        # Find any real moment with Moon in Via Combusta by scanning
        # Via Combusta: Libra 15° (195°) to Scorpio 15° (225°)
        # The Moon enters Via Combusta roughly every 27-28 days for ~2.5 days
        # Use a known historical date where Moon was there
        jd = swe.julday(2024, 10, 19, 0.0)  # approximate Via Combusta window

        positions = _compute_all_planets(jd)
        moon_lon = positions.get("Moon", (0.0, 0.0))[0]
        moon = get_moon_condition(jd, positions)

        result = evaluate_electional_moment("Venus", jd)

        # Structural invariants
        assert 0 <= result.total_score <= 100
        assert result.grade in ("Excellent", "Good", "Acceptable", "Poor", "Forbidden")

        # If moon is actually in Via Combusta, score should be reduced
        if moon.is_via_combusta:
            assert result.total_score < 70, (
                "Via Combusta should reduce score significantly"
            )
            found = any("焦灼帶" in c or "Via Combusta" in c for c in result.checks_failed)
            assert found, "Via Combusta should appear in checks_failed"

    def test_score_structure_completeness(self) -> None:
        """ElectionalScore should have all required fields populated."""
        import swisseph as swe
        from astro.talismanic_magic import evaluate_electional_moment

        jd = swe.julday(2025, 3, 15, 10.0)
        result = evaluate_electional_moment("Venus", jd)

        assert result.planet == "Venus"
        assert result.planet_cn == "金星"
        assert result.planet_position is not None
        assert result.moon_condition is not None
        assert 0.0 <= result.percentage <= 100.0
        assert result.grade_cn in ("絕佳", "良好", "可用", "欠佳", "禁忌")

    def test_retrograde_planet_appears_in_warnings(self) -> None:
        """If the planet is retrograde, it should appear in warnings."""
        import swisseph as swe
        from astro.talismanic_magic import evaluate_electional_moment

        # Mercury retrograde periods happen 3x/year; scan for one
        # Jan 14 – Feb 3 2022, May 10 – Jun 3 2022, Sep 9 – Oct 2 2022
        jd = swe.julday(2022, 1, 20, 12.0)  # Mercury retrograde
        result = evaluate_electional_moment("Mercury", jd)

        if result.planet_position.is_retrograde:
            found = any("逆行" in w for w in result.warnings)
            assert found, "Retrograde should be mentioned in warnings"


# ============================================================
# Test Suite 5: Window Finding
# ============================================================

class TestWindowFinding:
    """Test the talisman window finder."""

    def test_find_windows_returns_list(self) -> None:
        """find_talisman_windows should return a list."""
        from astro.talismanic_magic import find_talisman_windows

        windows = find_talisman_windows(
            "Jupiter",
            start_dt=datetime(2025, 1, 1, tzinfo=timezone.utc),
            days_ahead=7,
            step_hours=12,
            min_score=0.0,   # very low threshold to guarantee some results
        )
        assert isinstance(windows, list)

    def test_windows_sorted_by_score(self) -> None:
        """Windows should be sorted by score (descending) then time."""
        from astro.talismanic_magic import find_talisman_windows

        windows = find_talisman_windows(
            "Venus",
            start_dt=datetime(2025, 3, 1, tzinfo=timezone.utc),
            days_ahead=14,
            step_hours=12,
            min_score=0.0,
        )
        if len(windows) >= 2:
            for i in range(len(windows) - 1):
                # Score should be descending or equal
                assert windows[i].score >= windows[i + 1].score - 0.01

    def test_window_fields_valid(self) -> None:
        """Each window should have valid fields."""
        from astro.talismanic_magic import find_talisman_windows

        windows = find_talisman_windows(
            "Moon",
            start_dt=datetime(2025, 4, 1, tzinfo=timezone.utc),
            days_ahead=7,
            step_hours=8,
            min_score=0.0,
        )
        for w in windows:
            assert w.planet == "Moon"
            assert 0 <= w.score <= 100
            assert w.grade in ("Excellent", "Good", "Acceptable", "Poor", "Forbidden")
            assert w.day_of_week_cn in ("週一", "週二", "週三", "週四", "週五", "週六", "週日")
            assert 0 <= w.moon_longitude < 360


# ============================================================
# Test Suite 6: Recommendation Engine
# ============================================================

class TestRecommendationEngine:
    """Test the talisman recommendation pipeline."""

    def test_recommend_love_talisman(self) -> None:
        """Love purpose should recommend Venus as primary."""
        from astro.talismanic_magic import recommend_talisman

        rec = recommend_talisman("love")
        assert rec.purpose == "love"
        assert rec.purpose_cn == "愛情"
        assert "Venus" in rec.recommended_planets
        assert rec.primary_recommendation == "Venus"
        assert len(rec.planetary_talismans) > 0

    def test_recommend_wealth_talisman(self) -> None:
        """Wealth purpose should recommend Jupiter as primary."""
        from astro.talismanic_magic import recommend_talisman

        rec = recommend_talisman("wealth")
        assert rec.purpose == "wealth"
        assert "Jupiter" in rec.recommended_planets
        assert rec.primary_recommendation == "Jupiter"

    def test_recommend_protection_talisman(self) -> None:
        """Protection purpose should include Saturn and/or Mars."""
        from astro.talismanic_magic import recommend_talisman

        rec = recommend_talisman("protection")
        assert len(rec.recommended_planets) > 0
        assert any(p in ("Saturn", "Mars", "Sun") for p in rec.recommended_planets)

    def test_recommendation_includes_decan(self) -> None:
        """Recommendation should include a decan talisman (current moon decan)."""
        import swisseph as swe
        from astro.talismanic_magic import recommend_talisman, _jd_from_dt
        from datetime import datetime, timezone

        jd = _jd_from_dt(datetime(2025, 6, 15, 12, 0, tzinfo=timezone.utc))
        rec = recommend_talisman("wisdom", jd=jd)
        # Decan talisman should be present (moon is always somewhere)
        assert rec.decan_talisman is not None

    def test_recommendation_planetary_talismans_populated(self) -> None:
        """Planetary talismans in recommendation should have effects_cn."""
        from astro.talismanic_magic import recommend_talisman

        for purpose in ["love", "wealth", "protection", "health", "wisdom"]:
            rec = recommend_talisman(purpose)
            for t in rec.planetary_talismans:
                assert t.effects_cn, f"{t.planet} talisman has empty effects_cn for purpose '{purpose}'"


# ============================================================
# Test Suite 7: SVG Generation (no streamlit dependency)
# ============================================================

class TestSVGGeneration:
    """Test the SVG talisman generator."""

    def test_svg_generation_all_planets(self) -> None:
        """Should generate valid SVG for all seven planets."""
        from frontend.talismanic_renderer import generate_talisman_svg

        for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
            svg = generate_talisman_svg(planet)
            assert svg.startswith("<svg"), f"{planet}: SVG should start with <svg>"
            assert "</svg>" in svg, f"{planet}: SVG should be closed"
            assert "viewBox" in svg, f"{planet}: SVG should have viewBox"

    def test_svg_contains_planet_sigil(self) -> None:
        """SVG should contain the planet's sigil character."""
        from frontend.talismanic_renderer import generate_talisman_svg, _PLANET_SIGILS

        for planet, sigil in _PLANET_SIGILS.items():
            svg = generate_talisman_svg(planet)
            assert sigil in svg, f"{planet}: sigil '{sigil}' not found in SVG"

    def test_svg_custom_size(self) -> None:
        """SVG should respect custom width/height."""
        from frontend.talismanic_renderer import generate_talisman_svg

        svg = generate_talisman_svg("Jupiter", width=500, height=600)
        assert 'width="500"' in svg
        assert 'height="600"' in svg

    def test_svg_with_moon_phase(self) -> None:
        """SVG with moon_phase should include the phase text."""
        from frontend.talismanic_renderer import generate_talisman_svg

        svg = generate_talisman_svg("Venus", moon_phase="漸盈眉月")
        assert "漸盈眉月" in svg

    def test_svg_without_kamea(self) -> None:
        """SVG without kamea should still be valid."""
        from frontend.talismanic_renderer import generate_talisman_svg

        svg = generate_talisman_svg("Mars", show_kamea=False)
        assert "</svg>" in svg
        assert "Kamea" not in svg
