"""
Tests for the Trutine of Hermes / Prenatal Epoch module.

Covers:
- Basic epoch calculation and Trutine rule verification
- Moon phase/horizon detection helpers
- Cross-aspect computation
- Multiple variants
- Edge cases
"""

import math
import pytest

from astro.trutine_of_hermes.calculator import (
    compute_epoch_chart,
    PrenatalEpochChart,
    TrutineVariant,
    _normalize,
    _sign_index,
    _sign_name,
    _deg_in_sign,
    _is_moon_above_horizon,
    _moon_phase_info,
    _angular_diff,
)
from astro.trutine_of_hermes.constants import (
    GESTATION_DAYS_STANDARD,
    GESTATION_DAYS_SHORT,
    GESTATION_DAYS_LONG,
    ZODIAC_SIGNS,
    TRUTINE_VARIANTS,
)


# ============================================================
# Sample chart fixtures
# ============================================================

@pytest.fixture(scope="module")
def taipei_chart():
    """Standard test chart: Taipei, 1990-01-15 14:30 UTC+8."""
    return compute_epoch_chart(
        year=1990, month=1, day=15,
        hour=14, minute=30,
        timezone=8.0,
        latitude=25.033, longitude=121.565,
        location_name="Taipei",
    )


@pytest.fixture(scope="module")
def london_chart():
    """Secondary test chart: London, 1985-06-21 08:00 UTC+1."""
    return compute_epoch_chart(
        year=1985, month=6, day=21,
        hour=8, minute=0,
        timezone=1.0,
        latitude=51.509, longitude=-0.118,
        location_name="London",
    )


# ============================================================
# Tests: Basic Calculation
# ============================================================

class TestBasicCalculation:
    """基本計算測試"""

    def test_no_error(self, taipei_chart):
        """Chart computation should not produce an error."""
        assert taipei_chart.error is None

    def test_birth_datetime_set(self, taipei_chart):
        """Birth datetime string should contain the birth year."""
        assert "1990" in taipei_chart.birth_datetime_str

    def test_epoch_before_birth(self, taipei_chart):
        """Epoch Julian Day should be before birth Julian Day."""
        assert taipei_chart.epoch_jd < taipei_chart.birth_jd

    def test_gestation_within_range(self, taipei_chart):
        """Gestation should be between 250 and 300 days."""
        assert 250.0 <= taipei_chart.gestation_days <= 300.0

    def test_natal_planets_present(self, taipei_chart):
        """All 10 major planets should be present in natal chart."""
        expected = {"Sun", "Moon", "Mercury", "Venus", "Mars",
                    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"}
        assert expected.issubset(set(taipei_chart.natal_planets.keys()))

    def test_epoch_planets_present(self, taipei_chart):
        """All 10 major planets should be present in epoch chart."""
        expected = {"Sun", "Moon", "Mercury", "Venus", "Mars",
                    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"}
        assert expected.issubset(set(taipei_chart.epoch_planets.keys()))

    def test_natal_asc_valid(self, taipei_chart):
        """Natal ASC should be a valid longitude (0–360°)."""
        assert 0.0 <= taipei_chart.natal_asc < 360.0

    def test_epoch_asc_valid(self, taipei_chart):
        """Epoch ASC should be a valid longitude (0–360°)."""
        assert 0.0 <= taipei_chart.epoch_asc < 360.0

    def test_house_cusps_count(self, taipei_chart):
        """Should have exactly 12 house cusps for both charts."""
        assert len(taipei_chart.natal_house_cusps) == 12
        assert len(taipei_chart.epoch_house_cusps) == 12


# ============================================================
# Tests: Trutine Rule Verification
# ============================================================

class TestTrutineRule:
    """赫密士法則核心驗證測試"""

    def test_epoch_angle_is_asc_or_dsc(self, taipei_chart):
        """Epoch angle should be either 'ASC' or 'DSC'."""
        assert taipei_chart.epoch_angle in ("ASC", "DSC")

    def test_trutine_orb_is_finite(self, taipei_chart):
        """Trutine orb should be a finite positive number."""
        assert math.isfinite(taipei_chart.trutine_match_orb)
        assert taipei_chart.trutine_match_orb >= 0.0

    def test_trutine_orb_reasonable(self, taipei_chart):
        """Trutine orb should be less than 10° (reasonable match)."""
        assert taipei_chart.trutine_match_orb < 10.0

    def test_trutine_match_rule(self, taipei_chart):
        """Epoch ASC or DSC should closely match Natal Moon."""
        moon_lon = taipei_chart.natal_moon_lon
        if taipei_chart.epoch_angle == "ASC":
            angle_lon = taipei_chart.epoch_asc
        else:
            angle_lon = taipei_chart.epoch_dsc
        orb = _angular_diff(angle_lon, moon_lon)
        assert orb == pytest.approx(taipei_chart.trutine_match_orb, abs=0.01)

    def test_moon_horizon_rule(self, taipei_chart):
        """Trutine rule: above horizon → ASC, below → DSC."""
        if taipei_chart.moon_above_horizon:
            assert taipei_chart.epoch_angle == "ASC"
        else:
            assert taipei_chart.epoch_angle == "DSC"

    def test_verified_flag_consistency(self, taipei_chart):
        """trutine_verified should be True iff orb < 1°."""
        expected_verified = taipei_chart.trutine_match_orb < 1.0
        assert taipei_chart.trutine_verified == expected_verified


# ============================================================
# Tests: Moon Phase Helpers
# ============================================================

class TestMoonPhaseHelpers:
    """月相計算輔助函式測試"""

    def test_new_moon(self):
        """Sun-Moon at same position → new moon, waxing."""
        phase, elon, waxing = _moon_phase_info(100.0, 100.0)
        assert phase == "new_moon"
        assert elon == pytest.approx(0.0, abs=0.1)
        assert waxing is True

    def test_full_moon(self):
        """Moon 180° ahead of Sun → full moon."""
        phase, elon, waxing = _moon_phase_info(0.0, 180.0)
        assert phase == "full_moon"
        assert elon == pytest.approx(180.0, abs=0.1)
        assert waxing is False  # 180° = boundary, elongation 157.5–202.5 is full

    def test_first_quarter(self):
        """Moon 90° ahead → first quarter, waxing."""
        phase, elon, waxing = _moon_phase_info(0.0, 90.0)
        assert phase == "first_quarter"
        assert waxing is True

    def test_last_quarter(self):
        """Moon 270° ahead (= 90° behind) → last quarter, waning."""
        phase, elon, waxing = _moon_phase_info(0.0, 270.0)
        assert phase == "last_quarter"
        assert waxing is False

    def test_moon_elongation_range(self):
        """Elongation should always be in [0, 360)."""
        for sun in [0, 45, 90, 180, 270, 315]:
            for moon_offset in [10, 90, 170, 185, 270, 350]:
                _, elon, _ = _moon_phase_info(sun, (sun + moon_offset) % 360)
                assert 0.0 <= elon < 360.0


# ============================================================
# Tests: Moon Horizon Detection
# ============================================================

class TestMoonHorizonDetection:
    """月亮地平線位置測試"""

    def test_moon_on_dsc_above_horizon(self):
        """Moon at DSC (ASC + 180) → exactly above horizon."""
        asc = 45.0
        dsc = 225.0
        assert _is_moon_above_horizon(dsc, asc) is True

    def test_moon_on_asc_below_horizon(self):
        """Moon at ASC → exactly below horizon (in house 1)."""
        asc = 45.0
        assert _is_moon_above_horizon(asc, asc) is False

    def test_moon_halfway_above(self):
        """Moon 270° from ASC → above horizon (house 10)."""
        asc = 0.0
        moon = 270.0  # arc from ASC = 270 ≥ 180 → above
        assert _is_moon_above_horizon(moon, asc) is True

    def test_moon_halfway_below(self):
        """Moon 90° from ASC → below horizon (house 4)."""
        asc = 0.0
        moon = 90.0  # arc from ASC = 90 < 180 → below
        assert _is_moon_above_horizon(moon, asc) is False


# ============================================================
# Tests: Low-level Helpers
# ============================================================

class TestLowLevelHelpers:
    """低階輔助函式測試"""

    def test_normalize_wraps_360(self):
        assert _normalize(360.0) == pytest.approx(0.0)
        assert _normalize(361.5) == pytest.approx(1.5)
        assert _normalize(-10.0) == pytest.approx(350.0)

    def test_sign_index(self):
        assert _sign_index(0.0) == 0    # Aries
        assert _sign_index(30.0) == 1   # Taurus
        assert _sign_index(359.9) == 11  # Pisces

    def test_sign_name(self):
        assert _sign_name(0.0) == "Aries"
        assert _sign_name(60.0) == "Gemini"
        assert _sign_name(210.0) == "Scorpio"

    def test_deg_in_sign(self):
        assert _deg_in_sign(30.0) == pytest.approx(0.0)
        assert _deg_in_sign(45.0) == pytest.approx(15.0)
        assert _deg_in_sign(359.0) == pytest.approx(29.0)

    def test_angular_diff_max_180(self):
        """Shortest arc should never exceed 180°."""
        for a in range(0, 360, 30):
            for b in range(0, 360, 30):
                diff = _angular_diff(float(a), float(b))
                assert 0.0 <= diff <= 180.0


# ============================================================
# Tests: Constants
# ============================================================

class TestConstants:
    """常量測試"""

    def test_zodiac_signs_count(self):
        assert len(ZODIAC_SIGNS) == 12

    def test_gestation_ordering(self):
        """Short < Standard < Long."""
        assert GESTATION_DAYS_SHORT < GESTATION_DAYS_STANDARD < GESTATION_DAYS_LONG

    def test_trutine_variants_present(self):
        """All three variants should be present."""
        assert "hermes_ptolemy" in TRUTINE_VARIANTS
        assert "bailey_standard" in TRUTINE_VARIANTS
        assert "sepharial" in TRUTINE_VARIANTS

    def test_variant_has_required_keys(self):
        for vk, vdata in TRUTINE_VARIANTS.items():
            assert "zh_name" in vdata, f"{vk} missing zh_name"
            assert "en_name" in vdata, f"{vk} missing en_name"
            assert "gestation_days" in vdata, f"{vk} missing gestation_days"
            assert "source" in vdata, f"{vk} missing source"


# ============================================================
# Tests: Cross-Aspects
# ============================================================

class TestCrossAspects:
    """跨盤相位測試"""

    def test_has_cross_aspects(self, taipei_chart):
        """Should produce at least some cross-aspects."""
        assert len(taipei_chart.cross_aspects) > 0

    def test_cross_aspect_orbs_positive(self, taipei_chart):
        """All cross-aspect orbs should be non-negative."""
        for asp in taipei_chart.cross_aspects:
            assert asp.orb >= 0.0

    def test_cross_aspects_sorted_by_orb(self, taipei_chart):
        """Cross-aspects should be sorted tightest first."""
        orbs = [a.orb for a in taipei_chart.cross_aspects]
        assert orbs == sorted(orbs)

    def test_cross_aspect_names_valid(self, taipei_chart):
        """Aspect names should be non-empty strings."""
        for asp in taipei_chart.cross_aspects:
            assert isinstance(asp.aspect_name, str)
            assert len(asp.aspect_name) > 0


# ============================================================
# Tests: Planet Position Dataclass
# ============================================================

class TestEpochPlanetPosition:
    """EpochPlanetPosition dataclass 測試"""

    def test_dms_str_format(self, taipei_chart):
        """dms_str should contain the sign name."""
        moon = taipei_chart.natal_planets.get("Moon")
        assert moon is not None
        assert moon.sign in moon.dms_str

    def test_sign_index_matches_sign(self, taipei_chart):
        for name, pos in taipei_chart.natal_planets.items():
            expected_idx = int(pos.longitude / 30.0) % 12
            assert pos.sign_index == expected_idx

    def test_degree_in_sign_range(self, taipei_chart):
        for name, pos in taipei_chart.natal_planets.items():
            assert 0.0 <= pos.degree_in_sign < 30.0


# ============================================================
# Tests: Multiple Variants
# ============================================================

class TestMultipleVariants:
    """多種計算方法測試"""

    def test_hermes_ptolemy_variant(self):
        """Hermes/Ptolemy variant should compute without error."""
        chart = compute_epoch_chart(
            year=1975, month=9, day=5,
            hour=10, minute=0,
            timezone=0.0,
            latitude=51.509, longitude=-0.118,
            variant=TrutineVariant.HERMES_PTOLEMY,
        )
        assert chart.error is None
        assert chart.epoch_jd < chart.birth_jd

    def test_sepharial_variant(self):
        """Sepharial variant should compute without error."""
        chart = compute_epoch_chart(
            year=1975, month=9, day=5,
            hour=10, minute=0,
            timezone=0.0,
            latitude=51.509, longitude=-0.118,
            variant=TrutineVariant.SEPHARIAL,
        )
        assert chart.error is None
        assert chart.epoch_jd < chart.birth_jd

    def test_custom_gestation_override(self):
        """Custom gestation override should be used as search center."""
        chart = compute_epoch_chart(
            year=1990, month=6, day=15,
            hour=12, minute=0,
            timezone=8.0,
            latitude=25.033, longitude=121.565,
            gestation_override=273.0,
        )
        assert chart.error is None
        # The search centers on the override value (±20 days), so actual
        # gestation is anywhere within that window
        assert 250.0 <= chart.gestation_days <= 295.0
