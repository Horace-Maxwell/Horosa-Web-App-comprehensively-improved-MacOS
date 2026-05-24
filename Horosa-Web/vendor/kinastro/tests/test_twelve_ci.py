"""Tests for 十二星次 (Twelve Ci) — Jupiter station system."""

import pytest
from astro.twelve_ci import (
    TWELVE_CI,
    CI_NAMES_ZH,
    CI_NAMES_EN,
    CI_BRANCHES,
    _normalize,
    _tropical_to_ci_lon,
    _ci_index,
    _compute_planet_ci,
    compute_twelve_ci_chart,
    format_twelve_ci_chart,
    build_twelve_ci_svg,
    TwelveCiChart,
    TwelveCiPlanet,
)


class TestTwelveCiData:
    """Tests for the Twelve Ci data constants."""

    def test_twelve_ci_count(self):
        assert len(TWELVE_CI) == 12

    def test_ci_names_zh_count(self):
        assert len(CI_NAMES_ZH) == 12

    def test_ci_names_en_count(self):
        assert len(CI_NAMES_EN) == 12

    def test_ci_branches_count(self):
        assert len(CI_BRANCHES) == 12

    def test_ci_indices(self):
        for i, ci in enumerate(TWELVE_CI):
            assert ci["index"] == i

    def test_ci_names_unique(self):
        assert len(set(CI_NAMES_ZH)) == 12
        assert len(set(CI_NAMES_EN)) == 12

    def test_first_ci_is_xingji(self):
        assert TWELVE_CI[0]["name_zh"] == "星紀"
        assert TWELVE_CI[0]["name_en"] == "Xing Ji"
        assert TWELVE_CI[0]["branch"] == "丑"

    def test_last_ci_is_ximu(self):
        assert TWELVE_CI[11]["name_zh"] == "析木"
        assert TWELVE_CI[11]["name_en"] == "Xi Mu"
        assert TWELVE_CI[11]["branch"] == "寅"

    def test_all_ci_have_required_keys(self):
        required = {
            "index", "name_zh", "name_en", "name_pinyin", "range",
            "branch", "mansions", "fenye", "solar_approx", "element",
            "interpretation_zh", "interpretation_en",
        }
        for ci in TWELVE_CI:
            assert required.issubset(ci.keys()), f"Missing keys in {ci['name_zh']}"


class TestNormalize:
    """Tests for the _normalize helper."""

    def test_zero(self):
        assert _normalize(0) == 0.0

    def test_positive(self):
        assert _normalize(360.0) == 0.0

    def test_negative(self):
        assert _normalize(-90.0) == 270.0

    def test_large(self):
        assert _normalize(720.0) == 0.0


class TestTropicalToCiLon:
    """Tests for _tropical_to_ci_lon conversion."""

    def test_winter_solstice(self):
        """Capricorn 0° (tropical 270°) → CI lon 0°."""
        assert _tropical_to_ci_lon(270.0) == 0.0

    def test_vernal_equinox(self):
        """Aries 0° (tropical 0°) → CI lon 90°."""
        assert _tropical_to_ci_lon(0.0) == 90.0

    def test_summer_solstice(self):
        """Cancer 0° (tropical 90°) → CI lon 180°."""
        assert _tropical_to_ci_lon(90.0) == 180.0

    def test_autumnal_equinox(self):
        """Libra 0° (tropical 180°) → CI lon 270°."""
        assert _tropical_to_ci_lon(180.0) == 270.0


class TestCiIndex:
    """Tests for _ci_index calculation."""

    def test_index_0(self):
        assert _ci_index(0.0) == 0

    def test_index_0_upper(self):
        assert _ci_index(29.99) == 0

    def test_index_1(self):
        assert _ci_index(30.0) == 1

    def test_index_11(self):
        assert _ci_index(330.0) == 11

    def test_index_boundary(self):
        assert _ci_index(359.99) == 11


class TestComputePlanetCi:
    """Tests for _compute_planet_ci using swisseph."""

    def test_jupiter_returns_valid(self):
        """Compute Jupiter for J2000.0 epoch and verify structure."""
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(2000, 1, 1, 12.0)
        p = _compute_planet_ci("Jupiter", jd)
        assert p.name == "Jupiter"
        assert p.name_zh == "木星"
        assert 0 <= p.longitude < 360
        assert 0 <= p.ci_longitude < 360
        assert 0 <= p.ci_index < 12
        assert 0 <= p.degree_in_ci < 30
        assert p.ci_name_zh in CI_NAMES_ZH
        assert p.ci_name_en in CI_NAMES_EN

    def test_sun_returns_valid(self):
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(2024, 6, 21, 12.0)
        p = _compute_planet_ci("Sun", jd)
        assert p.name == "Sun"
        assert p.name_zh == "太陽"
        assert 0 <= p.ci_index < 12


class TestComputeChart:
    """Tests for compute_twelve_ci_chart."""

    def test_chart_basic(self):
        chart = compute_twelve_ci_chart(
            year=1990, month=6, day=15,
            hour=12, minute=0, timezone=8.0,
            latitude=25.0, longitude=121.5,
            location_name="Taipei",
        )
        assert isinstance(chart, TwelveCiChart)
        assert chart.year == 1990
        assert chart.location_name == "Taipei"
        assert len(chart.planets) == 7
        assert chart.jupiter is not None
        assert chart.jupiter_ci is not None
        assert chart.transit_jupiter is not None
        assert chart.transit_jupiter_ci is not None

    def test_chart_planet_names(self):
        chart = compute_twelve_ci_chart(
            year=2000, month=1, day=1,
            hour=0, minute=0, timezone=0.0,
            latitude=0.0, longitude=0.0,
        )
        names = {p.name for p in chart.planets}
        assert names == {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}


class TestFormatChart:
    """Tests for format_twelve_ci_chart (AI prompt formatter)."""

    def test_format_contains_key_info(self):
        chart = compute_twelve_ci_chart(
            year=1990, month=6, day=15,
            hour=12, minute=0, timezone=8.0,
            latitude=25.0, longitude=121.5,
        )
        text = format_twelve_ci_chart(chart)
        assert "十二星次" in text
        assert "木星" in text
        assert "Jupiter" in text
        assert "星次" in text


class TestBuildSvg:
    """Tests for build_twelve_ci_svg."""

    def test_svg_basic(self):
        chart = compute_twelve_ci_chart(
            year=1990, month=6, day=15,
            hour=12, minute=0, timezone=8.0,
            latitude=25.0, longitude=121.5,
        )
        svg = build_twelve_ci_svg(chart)
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "十二星次" in svg
        assert "星紀" in svg
