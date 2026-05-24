"""
Tests for Astrocartography (地點占星) module — astro/astrocartography.py
"""

import math
import pytest

from astro.astrocartography import (
    compute_astrocartography,
    compute_astrocartography_transit,
    compute_obliquity,
    compute_gast,
    compute_planet_longitudes,
    compute_mc_line,
    compute_ic_line,
    compute_ac_line,
    compute_dc_line,
    find_parans,
    format_acg_for_prompt,
    AcgResult,
    PLANET_GLYPHS,
    ACG_PLANETS,
    LINE_COLORS,
    PLANET_LINE_MEANINGS,
    _normalize,
    _normalize_lon,
)


# ── Test parameters: 1990-01-15 10:30 UTC+8, Taipei ────────────
TEST_YEAR, TEST_MONTH, TEST_DAY = 1990, 1, 15
TEST_HOUR, TEST_MINUTE = 10, 30
TEST_TZ = 8.0
TEST_LAT, TEST_LON = 25.03, 121.56


class TestHelpers:
    """Test helper / normalisation functions."""

    def test_normalize_positive(self):
        assert _normalize(370.0) == pytest.approx(10.0)

    def test_normalize_negative(self):
        assert _normalize(-10.0) == pytest.approx(350.0)

    def test_normalize_zero(self):
        assert _normalize(0.0) == pytest.approx(0.0)

    def test_normalize_360(self):
        assert _normalize(360.0) == pytest.approx(0.0)

    def test_normalize_lon_positive(self):
        assert _normalize_lon(200.0) == pytest.approx(-160.0)

    def test_normalize_lon_negative(self):
        assert _normalize_lon(-200.0) == pytest.approx(160.0)

    def test_normalize_lon_zero(self):
        assert _normalize_lon(0.0) == pytest.approx(0.0)


class TestObliquity:
    """Test obliquity computation."""

    def test_obliquity_range(self):
        """Obliquity should be approximately 23.44° for modern epochs."""
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(2000, 1, 1, 12.0)
        eps = compute_obliquity(jd)
        assert 23.0 < eps < 24.0

    def test_obliquity_returns_float(self):
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(1990, 6, 15, 0.0)
        eps = compute_obliquity(jd)
        assert isinstance(eps, float)


class TestGAST:
    """Test Greenwich Apparent Sidereal Time computation."""

    def test_gast_range(self):
        """GAST should be in [0, 360) degrees."""
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(2000, 3, 20, 12.0)
        gast = compute_gast(jd)
        assert 0.0 <= gast < 360.0

    def test_gast_returns_float(self):
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(2025, 7, 4, 0.0)
        gast = compute_gast(jd)
        assert isinstance(gast, float)


class TestPlanetLongitudes:
    """Test planet longitude computation."""

    def test_returns_dict(self):
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(TEST_YEAR, TEST_MONTH, TEST_DAY,
                        TEST_HOUR + TEST_MINUTE / 60.0 - TEST_TZ)
        lons = compute_planet_longitudes(jd)
        assert isinstance(lons, dict)
        # At least Sun through Pluto should be present (10 planets)
        assert len(lons) >= 10

    def test_all_longitudes_in_range(self):
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(2000, 1, 1, 12.0)
        lons = compute_planet_longitudes(jd)
        for name, lon in lons.items():
            assert 0.0 <= lon < 360.0, f"{name} longitude out of range: {lon}"


class TestMcLine:
    """Test MC (Midheaven) line computation."""

    def test_mc_line_length(self):
        """MC line should have at least 100 points."""
        pts = compute_mc_line(120.0, 90.0, 23.44)
        assert len(pts) >= 100

    def test_mc_line_vertical(self):
        """MC line should be a vertical line (same longitude for all latitudes)."""
        pts = compute_mc_line(120.0, 90.0, 23.44)
        lons = set(round(p[0], 6) for p in pts)
        # All points should share the same longitude
        assert len(lons) == 1

    def test_mc_line_lat_range(self):
        """MC line should span from LAT_MIN to LAT_MAX."""
        pts = compute_mc_line(0.0, 0.0, 23.44)
        lats = [p[1] for p in pts]
        assert min(lats) == pytest.approx(-70.0)
        assert max(lats) == pytest.approx(70.0)


class TestIcLine:
    """Test IC (Imum Coeli) line computation."""

    def test_ic_line_offset_from_mc(self):
        """IC should be 180° away from MC."""
        mc_pts = compute_mc_line(90.0, 45.0, 23.44)
        ic_pts = compute_ic_line(90.0, 45.0, 23.44)
        # Check that the longitude is offset by ~180°
        mc_lon = mc_pts[0][0]
        ic_lon = ic_pts[0][0]
        diff = abs(mc_lon - ic_lon)
        if diff > 180:
            diff = 360 - diff
        assert diff == pytest.approx(180.0, abs=1.0)


class TestAcLine:
    """Test AC (Ascendant) line computation."""

    def test_ac_line_length(self):
        """AC line should have at least 100 points."""
        pts = compute_ac_line(90.0, 45.0, 23.44)
        assert len(pts) >= 100

    def test_ac_line_not_vertical(self):
        """AC line should NOT be a vertical line (longitude varies with latitude)."""
        pts = compute_ac_line(90.0, 45.0, 23.44)
        lons = set(round(p[0], 2) for p in pts)
        # Should have varying longitudes
        assert len(lons) > 1

    def test_ac_line_longitude_range(self):
        """All longitudes should be in [-180, 180]."""
        pts = compute_ac_line(45.0, 120.0, 23.44)
        for lon, lat in pts:
            assert -180.0 <= lon <= 180.0


class TestDcLine:
    """Test DC (Descendant) line computation."""

    def test_dc_line_length(self):
        pts = compute_dc_line(45.0, 120.0, 23.44)
        assert len(pts) >= 100


class TestComputeAstrocartography:
    """Test the main compute_astrocartography function."""

    def test_returns_acg_result(self):
        result = compute_astrocartography(
            year=TEST_YEAR, month=TEST_MONTH, day=TEST_DAY,
            hour=TEST_HOUR, minute=TEST_MINUTE, timezone=TEST_TZ,
            latitude=TEST_LAT, longitude=TEST_LON,
        )
        assert isinstance(result, AcgResult)

    def test_has_all_line_types(self):
        result = compute_astrocartography(
            year=TEST_YEAR, month=TEST_MONTH, day=TEST_DAY,
            hour=TEST_HOUR, minute=TEST_MINUTE, timezone=TEST_TZ,
        )
        for planet, line_dict in result.lines.items():
            assert "AC" in line_dict, f"{planet} missing AC"
            assert "MC" in line_dict, f"{planet} missing MC"
            assert "IC" in line_dict, f"{planet} missing IC"
            assert "DC" in line_dict, f"{planet} missing DC"

    def test_line_point_count(self):
        """Each line should have at least 100 points."""
        result = compute_astrocartography(
            year=2000, month=6, day=21,
            hour=12, minute=0, timezone=0.0,
        )
        for planet, line_dict in result.lines.items():
            for lt, pts in line_dict.items():
                assert len(pts) >= 100, f"{planet} {lt} has only {len(pts)} points"

    def test_obliquity_populated(self):
        result = compute_astrocartography(
            year=2000, month=1, day=1,
            hour=12, minute=0, timezone=0.0,
        )
        assert 23.0 < result.obliquity < 24.0

    def test_gast_populated(self):
        result = compute_astrocartography(
            year=2000, month=1, day=1,
            hour=12, minute=0, timezone=0.0,
        )
        assert 0.0 <= result.gast_deg < 360.0

    def test_parans_is_list(self):
        result = compute_astrocartography(
            year=TEST_YEAR, month=TEST_MONTH, day=TEST_DAY,
            hour=TEST_HOUR, minute=TEST_MINUTE, timezone=TEST_TZ,
        )
        assert isinstance(result.parans, list)

    def test_meanings_populated(self):
        result = compute_astrocartography(
            year=TEST_YEAR, month=TEST_MONTH, day=TEST_DAY,
            hour=TEST_HOUR, minute=TEST_MINUTE, timezone=TEST_TZ,
        )
        assert "Sun" in result.meanings
        assert "AC" in result.meanings["Sun"]


class TestTransitAstrocartography:
    """Test transit ACG computation."""

    def test_transit_returns_result(self):
        result = compute_astrocartography_transit(
            natal_year=TEST_YEAR, natal_month=TEST_MONTH,
            natal_day=TEST_DAY, natal_hour=TEST_HOUR,
            natal_minute=TEST_MINUTE, natal_timezone=TEST_TZ,
            transit_year=2025, transit_month=6, transit_day=15,
        )
        assert isinstance(result, AcgResult)
        assert len(result.lines) >= 10


class TestFindParans:
    """Test Paran detection."""

    def test_finds_parans_in_close_lines(self):
        """Two lines at similar lat/lon should produce a paran."""
        lines = {
            "Sun": {"AC": [(10.0, 30.0), (10.0, 31.0)]},
            "Moon": {"MC": [(11.0, 30.0), (11.0, 31.0)]},
        }
        parans = find_parans(lines, lat_tolerance=2.0, lon_tolerance=5.0)
        assert len(parans) > 0

    def test_no_paran_for_same_planet(self):
        """Same planet lines should not produce parans."""
        lines = {
            "Sun": {
                "AC": [(10.0, 30.0)],
                "MC": [(10.0, 30.0)],
            },
        }
        parans = find_parans(lines)
        assert len(parans) == 0


class TestFormatPrompt:
    """Test AI prompt formatting."""

    def test_prompt_contains_planet_names(self):
        result = compute_astrocartography(
            year=TEST_YEAR, month=TEST_MONTH, day=TEST_DAY,
            hour=TEST_HOUR, minute=TEST_MINUTE, timezone=TEST_TZ,
        )
        prompt = format_acg_for_prompt(result)
        assert "Sun" in prompt
        assert "Moon" in prompt
        assert "Julian Day" in prompt

    def test_prompt_is_nonempty_string(self):
        result = compute_astrocartography(
            year=2000, month=1, day=1,
            hour=12, minute=0, timezone=0.0,
        )
        prompt = format_acg_for_prompt(result)
        assert isinstance(prompt, str)
        assert len(prompt) > 100


class TestConstants:
    """Test module-level constants."""

    def test_planet_glyphs_complete(self):
        for planet in ACG_PLANETS:
            assert planet in PLANET_GLYPHS

    def test_line_colors_complete(self):
        for lt in ("AC", "MC", "IC", "DC"):
            assert lt in LINE_COLORS

    def test_meanings_complete(self):
        for planet in ACG_PLANETS:
            if planet in PLANET_LINE_MEANINGS:
                for lt in ("AC", "MC", "IC", "DC"):
                    assert lt in PLANET_LINE_MEANINGS[planet]
