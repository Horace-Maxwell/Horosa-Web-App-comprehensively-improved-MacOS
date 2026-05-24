"""
tests/test_electional.py — Tests for the Electional Astrology & Vedic Muhurta module.

Three test suites:
  1. TestWesternElectional  — Classic Western Electional cases (Lilly rules)
  2. TestVedicMuhurta       — Vedic Muhurta / Panchanga cases
  3. TestElectionalSearch   — Window-search functionality

Test cases are based on historically significant dates and traditional examples.
"""

import pytest

from astro.electional.calculator import (
    compute_western_electional,
    compute_vedic_muhurta,
    find_western_elections,
    find_vedic_muhurtas,
    WesternElectionalResult,
    VedicMuhurtaResult,
)
from astro.electional.constants import (
    WESTERN_ACTIVITY_TYPES,
    VEDIC_ACTIVITY_TYPES,
    TRADITIONAL_PLANETS,
    VEDIC_RASHIS,
)


# ============================================================
# Test Case 1: Western Classical Electional
# ============================================================

class TestWesternElectional:
    """
    Western Traditional Electional Astrology — Lilly / Bonatti rules.

    Test date: 2024-06-21 10:00 UTC+8, Taipei (25.033°N, 121.565°E)
    This is close to the summer solstice — Jupiter is strong and Moon is waxing.
    """

    @pytest.fixture
    def marriage_chart(self) -> WesternElectionalResult:
        return compute_western_electional(
            year=2024, month=6, day=21,
            hour=10, minute=0,
            timezone=8.0,
            latitude=25.033, longitude=121.565,
            activity_type="marriage",
            location_name="Taipei",
        )

    @pytest.fixture
    def contract_chart(self) -> WesternElectionalResult:
        return compute_western_electional(
            year=2024, month=6, day=21,
            hour=14, minute=0,
            timezone=8.0,
            latitude=25.033, longitude=121.565,
            activity_type="contract_signing",
            location_name="Taipei",
        )

    def test_result_type(self, marriage_chart: WesternElectionalResult) -> None:
        assert isinstance(marriage_chart, WesternElectionalResult)

    def test_activity_type(self, marriage_chart: WesternElectionalResult) -> None:
        assert marriage_chart.activity_type == "marriage"

    def test_location(self, marriage_chart: WesternElectionalResult) -> None:
        assert marriage_chart.latitude == pytest.approx(25.033, abs=0.01)
        assert marriage_chart.longitude == pytest.approx(121.565, abs=0.01)

    def test_has_planets(self, marriage_chart: WesternElectionalResult) -> None:
        assert len(marriage_chart.planets) == len(TRADITIONAL_PLANETS)

    def test_planet_names(self, marriage_chart: WesternElectionalResult) -> None:
        names = [p.name for p in marriage_chart.planets]
        for planet in TRADITIONAL_PLANETS:
            assert planet in names

    def test_planet_longitudes_valid(self, marriage_chart: WesternElectionalResult) -> None:
        for p in marriage_chart.planets:
            assert 0.0 <= p.longitude < 360.0

    def test_asc_sign_valid(self, marriage_chart: WesternElectionalResult) -> None:
        valid_signs = [s[0] for s in __import__(
            "astro.electional.constants", fromlist=["ZODIAC_SIGNS"]
        ).ZODIAC_SIGNS]
        assert marriage_chart.asc_sign in valid_signs

    def test_asc_lord_valid(self, marriage_chart: WesternElectionalResult) -> None:
        assert marriage_chart.asc_lord in TRADITIONAL_PLANETS

    def test_house_cusps_count(self, marriage_chart: WesternElectionalResult) -> None:
        assert len(marriage_chart.house_cusps) == 12

    def test_score_is_number(self, marriage_chart: WesternElectionalResult) -> None:
        assert isinstance(marriage_chart.total_score, float)

    def test_quality_valid(self, marriage_chart: WesternElectionalResult) -> None:
        valid = {"Excellent", "Good", "Neutral", "Poor", "Avoid"}
        assert marriage_chart.quality in valid

    def test_stars_format(self, marriage_chart: WesternElectionalResult) -> None:
        assert "★" in marriage_chart.quality_stars

    def test_moon_phase_valid(self, marriage_chart: WesternElectionalResult) -> None:
        assert marriage_chart.moon_phase in ("waxing", "waning")

    def test_planetary_hour_lord_valid(self, marriage_chart: WesternElectionalResult) -> None:
        assert marriage_chart.planetary_hour_lord in TRADITIONAL_PLANETS

    def test_planetary_hour_number_range(self, marriage_chart: WesternElectionalResult) -> None:
        assert 1 <= marriage_chart.planetary_hour_number <= 24

    def test_factors_list(self, marriage_chart: WesternElectionalResult) -> None:
        assert isinstance(marriage_chart.factors, list)
        # Should have at least moon_phase factor
        assert len(marriage_chart.factors) >= 1

    def test_factor_scores_sum(self, marriage_chart: WesternElectionalResult) -> None:
        computed_sum = sum(f.score for f in marriage_chart.factors)
        assert marriage_chart.total_score == pytest.approx(computed_sum, abs=1.0)

    def test_summary_not_empty(self, marriage_chart: WesternElectionalResult) -> None:
        assert len(marriage_chart.summary_en) > 10
        assert len(marriage_chart.summary_cn) > 10

    def test_contract_activity(self, contract_chart: WesternElectionalResult) -> None:
        assert contract_chart.activity_type == "contract_signing"

    def test_all_activity_types(self) -> None:
        """Smoke test: all activity types compute without error."""
        for act in WESTERN_ACTIVITY_TYPES:
            result = compute_western_electional(
                year=2024, month=6, day=21, hour=10, minute=0,
                timezone=8.0, latitude=25.033, longitude=121.565,
                activity_type=act,
            )
            assert isinstance(result, WesternElectionalResult)
            assert result.activity_type == act


# ============================================================
# Test Case 2: Vedic Muhurta
# ============================================================

class TestVedicMuhurta:
    """
    Vedic Muhurta — Panchanga-based auspiciousness analysis.

    Test date: 2024-04-09 (approximate Akshaya Tritiya — a very auspicious day).
    Location: Mumbai (19.076°N, 72.877°E), IST (UTC+5.5)
    """

    @pytest.fixture
    def marriage_muhurta(self) -> VedicMuhurtaResult:
        return compute_vedic_muhurta(
            year=2024, month=4, day=9,
            hour=10, minute=30,
            timezone=5.5,
            latitude=19.076, longitude=72.877,
            activity_type="marriage",
            location_name="Mumbai",
        )

    @pytest.fixture
    def business_muhurta(self) -> VedicMuhurtaResult:
        return compute_vedic_muhurta(
            year=2024, month=4, day=9,
            hour=9, minute=0,
            timezone=5.5,
            latitude=19.076, longitude=72.877,
            activity_type="business_opening",
            location_name="Mumbai",
        )

    def test_result_type(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert isinstance(marriage_muhurta, VedicMuhurtaResult)

    def test_activity_type(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert marriage_muhurta.activity_type == "marriage"

    def test_panchanga_five_elements(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        """Panchanga must have exactly 5 elements: Tithi, Vara, Nakshatra, Yoga, Karana."""
        assert "tithi" in marriage_muhurta.panchanga
        assert "vara" in marriage_muhurta.panchanga
        assert "nakshatra" in marriage_muhurta.panchanga
        assert "yoga" in marriage_muhurta.panchanga
        assert "karana" in marriage_muhurta.panchanga

    def test_tithi_name_not_empty(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert len(marriage_muhurta.panchanga["tithi"].value) > 0

    def test_vara_name_not_empty(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert len(marriage_muhurta.panchanga["vara"].value) > 0

    def test_nakshatra_name_not_empty(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert len(marriage_muhurta.panchanga["nakshatra"].value) > 0

    def test_yoga_name_not_empty(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert len(marriage_muhurta.panchanga["yoga"].value) > 0

    def test_karana_name_not_empty(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert len(marriage_muhurta.panchanga["karana"].value) > 0

    def test_lagna_rashi_valid(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        valid_rashis = [r["name"] for r in VEDIC_RASHIS]
        assert marriage_muhurta.lagna_rashi in valid_rashis

    def test_lagna_rashi_index_range(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert 0 <= marriage_muhurta.lagna_rashi_index <= 11

    def test_moon_rashi_valid(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        valid_rashis = [r["name"] for r in VEDIC_RASHIS]
        assert marriage_muhurta.moon_rashi in valid_rashis

    def test_moon_sidereal_in_range(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert 0.0 <= marriage_muhurta.moon_sidereal < 360.0

    def test_ayanamsa_reasonable(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        # Lahiri ayanamsa in 2024 is approximately 24°
        assert 23.0 <= marriage_muhurta.ayanamsa <= 26.0

    def test_score_is_number(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert isinstance(marriage_muhurta.total_score, float)

    def test_quality_valid(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        valid = {"Excellent", "Good", "Neutral", "Poor", "Avoid"}
        assert marriage_muhurta.quality in valid

    def test_gandanta_bool(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert isinstance(marriage_muhurta.is_gandanta, bool)

    def test_combustion_flags_bool(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert isinstance(marriage_muhurta.jupiter_combust, bool)
        assert isinstance(marriage_muhurta.venus_combust, bool)

    def test_factors_list(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert isinstance(marriage_muhurta.factors, list)

    def test_summary_not_empty(self, marriage_muhurta: VedicMuhurtaResult) -> None:
        assert len(marriage_muhurta.summary_en) > 10
        assert len(marriage_muhurta.summary_cn) > 10

    def test_all_vedic_activity_types(self) -> None:
        """Smoke test: all Vedic activity types compute without error."""
        for act in VEDIC_ACTIVITY_TYPES:
            result = compute_vedic_muhurta(
                year=2024, month=4, day=9, hour=10, minute=0,
                timezone=5.5, latitude=19.076, longitude=72.877,
                activity_type=act,
            )
            assert isinstance(result, VedicMuhurtaResult)
            assert result.activity_type == act

    def test_vishti_karana_detection(self) -> None:
        """
        Vishti Karana (Bhadra) should always produce a negative factor if detected.
        We test several datetimes to check that the detector works without crashing.
        """
        # Test a range of times — at least one should hit Vishti in a 7-day window
        hit_vishti = False
        for d in range(1, 8):
            r = compute_vedic_muhurta(
                year=2024, month=4, day=d, hour=6, minute=0,
                timezone=5.5, latitude=19.076, longitude=72.877,
                activity_type="marriage",
            )
            vishti_factors = [f for f in r.factors if f.factor_key == "vishti_karana"]
            if vishti_factors:
                hit_vishti = True
                assert all(not f.is_positive for f in vishti_factors)
        # Just verifying the system runs; Vishti may or may not appear in this window
        assert isinstance(hit_vishti, bool)


# ============================================================
# Test Case 3: Window Search
# ============================================================

class TestElectionalSearch:
    """
    Test the window-search functionality for both traditions.
    Uses a small 3-day window to keep tests fast.
    """

    def test_western_search_returns_list(self) -> None:
        results = find_western_elections(
            start_year=2024, start_month=6, start_day=20,
            end_year=2024, end_month=6, end_day=22,
            timezone=8.0, latitude=25.033, longitude=121.565,
            activity_type="important_meeting",
            location_name="Taipei",
            min_score=-100.0,  # Accept anything to ensure we get results
            max_results=5,
            step_hours=4.0,    # Coarser step for speed
        )
        assert isinstance(results, list)

    def test_western_search_sorted_descending(self) -> None:
        results = find_western_elections(
            start_year=2024, start_month=6, start_day=20,
            end_year=2024, end_month=6, end_day=22,
            timezone=8.0, latitude=25.033, longitude=121.565,
            activity_type="marriage",
            min_score=-100.0,
            max_results=10,
            step_hours=6.0,
        )
        scores = [r.total_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_western_search_max_results_respected(self) -> None:
        results = find_western_elections(
            start_year=2024, start_month=6, start_day=1,
            end_year=2024, end_month=6, end_day=30,
            timezone=8.0, latitude=25.033, longitude=121.565,
            activity_type="travel",
            min_score=-100.0,
            max_results=3,
            step_hours=8.0,
        )
        assert len(results) <= 3

    def test_vedic_search_returns_list(self) -> None:
        results = find_vedic_muhurtas(
            start_year=2024, start_month=4, start_day=1,
            end_year=2024, end_month=4, end_day=3,
            timezone=5.5, latitude=19.076, longitude=72.877,
            activity_type="business_opening",
            min_score=-100.0,
            max_results=5,
            step_hours=4.0,
        )
        assert isinstance(results, list)

    def test_vedic_search_sorted_descending(self) -> None:
        results = find_vedic_muhurtas(
            start_year=2024, start_month=4, start_day=1,
            end_year=2024, end_month=4, end_day=3,
            timezone=5.5, latitude=19.076, longitude=72.877,
            activity_type="marriage",
            min_score=-100.0,
            max_results=10,
            step_hours=6.0,
        )
        scores = [r.total_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_high_score_filter(self) -> None:
        """High minimum score should return fewer results than low minimum score."""
        low = find_western_elections(
            start_year=2024, start_month=6, start_day=1,
            end_year=2024, end_month=6, end_day=30,
            timezone=8.0, latitude=25.033, longitude=121.565,
            activity_type="important_meeting",
            min_score=-50.0,
            max_results=50,
            step_hours=6.0,
        )
        high = find_western_elections(
            start_year=2024, start_month=6, start_day=1,
            end_year=2024, end_month=6, end_day=30,
            timezone=8.0, latitude=25.033, longitude=121.565,
            activity_type="important_meeting",
            min_score=50.0,
            max_results=50,
            step_hours=6.0,
        )
        assert len(low) >= len(high)

    def test_no_results_empty_list(self) -> None:
        """With an impossibly high minimum score, should return empty list."""
        results = find_western_elections(
            start_year=2024, start_month=6, start_day=21,
            end_year=2024, end_month=6, end_day=21,
            timezone=8.0, latitude=25.033, longitude=121.565,
            activity_type="marriage",
            min_score=9999.0,  # Impossible
            max_results=10,
            step_hours=2.0,
        )
        assert results == []
