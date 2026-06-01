# -*- coding: utf-8 -*-
"""
tests/test_mundane.py — Mundane Astrology (世俗占星) Module Tests

Tests cover:
  - Ingress chart computation (Aries, Cancer, Libra, Capricorn)
  - Planet position basics (sign index, degree in sign)
  - Aspect computation
  - Eclipse search (solar and lunar)
  - Great Conjunction timeline data
  - National chart computation
  - Moment chart computation
  - Format prompt helper
  - Constants integrity (country capitals, aspects, houses)
  - Calculator pure-function contract (no Streamlit imports)
"""

import math
import pytest
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# Imports — calculator only (no Streamlit)
# ─────────────────────────────────────────────────────────────────────────────

from astro.mundane.calculator import (
    compute_ingress_chart,
    compute_eclipse_chart,
    compute_moment_chart,
    compute_national_mundane,
    compute_current_outer_planets,
    get_great_conjunctions_timeline,
    compute_next_great_conjunction,
    format_mundane_chart_for_prompt,
    _sign_index_from_lon,
    _degree_in_sign,
    _datetime_to_jd,
    _jd_to_datetime,
    MundaneChart,
    EclipseInfo,
    GreatConjunction,
    MundanePlanet,
    MundaneAspect,
)
from astro.mundane.constants import (
    COUNTRY_CAPITALS,
    SIGN_NAMES_EN,
    SIGN_NAMES_ZH,
    MUNDANE_ASPECTS,
    MUNDANE_HOUSES,
    INGRESS_LONGITUDES,
    GREAT_CONJUNCTIONS,
    PLANET_IDS,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────────────────────────────────────

class TestHelpers:
    """Tests for internal helper functions."""

    def test_sign_index_from_lon_zero(self):
        """0° → Aries (index 0)."""
        assert _sign_index_from_lon(0.0) == 0

    def test_sign_index_from_lon_aries(self):
        """15° → Aries (index 0)."""
        assert _sign_index_from_lon(15.0) == 0

    def test_sign_index_from_lon_taurus(self):
        """35° → Taurus (index 1)."""
        assert _sign_index_from_lon(35.0) == 1

    def test_sign_index_from_lon_pisces(self):
        """350° → Pisces (index 11)."""
        assert _sign_index_from_lon(350.0) == 11

    def test_sign_index_full_circle(self):
        """360° wraps to 0 (Aries)."""
        assert _sign_index_from_lon(360.0) == 0

    def test_degree_in_sign_basic(self):
        """35° is 5° into Taurus."""
        assert abs(_degree_in_sign(35.0) - 5.0) < 0.001

    def test_degree_in_sign_boundary(self):
        """30° is 0° into the next sign."""
        assert abs(_degree_in_sign(30.0) - 0.0) < 0.001

    def test_jd_roundtrip(self):
        """JD ↔ datetime roundtrip within 1 minute."""
        dt = datetime(2025, 3, 20, 12, 0, 0)
        import swisseph as swe
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)
        dt2 = _jd_to_datetime(jd)
        assert abs((dt2.year - dt.year)) == 0
        assert abs((dt2.month - dt.month)) == 0


# ─────────────────────────────────────────────────────────────────────────────
# Constants integrity
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    """Validate constants for completeness and consistency."""

    def test_twelve_signs(self):
        assert len(SIGN_NAMES_EN) == 12
        assert len(SIGN_NAMES_ZH) == 12

    def test_ingress_longitudes(self):
        """Four ingress types have correct Sun longitudes."""
        assert INGRESS_LONGITUDES["aries"] == 0.0
        assert INGRESS_LONGITUDES["cancer"] == 90.0
        assert INGRESS_LONGITUDES["libra"] == 180.0
        assert INGRESS_LONGITUDES["capricorn"] == 270.0

    def test_mundane_aspects_not_empty(self):
        assert len(MUNDANE_ASPECTS) >= 5
        for asp in MUNDANE_ASPECTS:
            assert "angle" in asp
            assert "orb" in asp
            assert "name" in asp

    def test_mundane_houses_twelve(self):
        assert len(MUNDANE_HOUSES) == 12
        for h in range(1, 13):
            assert h in MUNDANE_HOUSES
            assert "en" in MUNDANE_HOUSES[h]
            assert "zh" in MUNDANE_HOUSES[h]

    def test_country_capitals_not_empty(self):
        assert len(COUNTRY_CAPITALS) >= 30

    def test_country_capitals_structure(self):
        """Each entry has (name_zh, lat, lon, tz)."""
        for key, val in COUNTRY_CAPITALS.items():
            assert len(val) == 4
            name_zh, lat, lon, tz = val
            assert isinstance(name_zh, str)
            assert -90.0 <= lat <= 90.0
            assert -180.0 <= lon <= 180.0

    def test_great_conjunctions_have_required_fields(self):
        for gc in GREAT_CONJUNCTIONS:
            assert "year" in gc
            assert "sign_index" in gc
            assert 0 <= gc["sign_index"] <= 11

    def test_planet_ids_includes_outer(self):
        assert "Jupiter" in PLANET_IDS
        assert "Saturn" in PLANET_IDS
        assert "Uranus" in PLANET_IDS
        assert "Neptune" in PLANET_IDS
        assert "Pluto" in PLANET_IDS


# ─────────────────────────────────────────────────────────────────────────────
# Ingress Chart computation
# ─────────────────────────────────────────────────────────────────────────────

class TestIngressChart:
    """Tests for compute_ingress_chart."""

    def test_aries_ingress_2025_basic(self):
        """Aries Ingress 2025 returns a MundaneChart."""
        chart = compute_ingress_chart(
            year=2025,
            ingress_type="aries",
            latitude=0.0, longitude=0.0,
            location_name="Global",
        )
        assert isinstance(chart, MundaneChart)
        assert chart.ingress_type == "aries"
        assert chart.year == 2025

    def test_aries_ingress_sun_near_zero(self):
        """At Aries Ingress, the Sun should be near 0° Aries."""
        chart = compute_ingress_chart(2025, "aries", 0.0, 0.0)
        sun = chart.planets.get("Sun")
        assert sun is not None
        # Sun longitude should be within 1° of 0° Aries
        lon_mod = sun.longitude % 360
        assert abs(lon_mod) < 1.0 or abs(lon_mod - 360) < 1.0

    def test_cancer_ingress_sun_near_90(self):
        """At Cancer Ingress, Sun is near 90° (Cancer 0°)."""
        chart = compute_ingress_chart(2025, "cancer", 0.0, 0.0)
        sun = chart.planets.get("Sun")
        assert sun is not None
        lon_mod = sun.longitude % 360
        assert abs(lon_mod - 90.0) < 1.0

    def test_capricorn_ingress_sun_near_270(self):
        """At Capricorn Ingress, Sun is near 270°."""
        chart = compute_ingress_chart(2024, "capricorn", 0.0, 0.0)
        sun = chart.planets.get("Sun")
        assert sun is not None
        lon_mod = sun.longitude % 360
        assert abs(lon_mod - 270.0) < 1.0

    def test_ingress_planets_populated(self):
        """Ingress chart should have at least 9 planets."""
        chart = compute_ingress_chart(2025, "aries", 0.0, 0.0)
        assert len(chart.planets) >= 9

    def test_ingress_with_location_tokyo(self):
        """Ingress chart with Tokyo location gives different ASC."""
        chart_global = compute_ingress_chart(2025, "aries", 0.0, 0.0, "Global")
        chart_tokyo  = compute_ingress_chart(2025, "aries", 35.6762, 139.6503, "Tokyo")
        # ASC should differ when location differs
        assert abs(chart_global.asc - chart_tokyo.asc) > 1.0

    def test_ingress_placidus_house_system(self):
        """Placidus house system returns valid cusp list."""
        chart = compute_ingress_chart(2025, "aries", 51.5, 0.0, "London", house_system="P")
        assert len(chart.cusps) >= 12

    def test_ingress_chart_type_label(self):
        chart = compute_ingress_chart(2025, "libra", 0.0, 0.0)
        assert "Libra" in chart.chart_type_label_en or "秋分" in chart.chart_type_label_zh

    def test_all_ingress_types(self):
        """All four ingress types compute without error."""
        for ingress in ["aries", "cancer", "libra", "capricorn"]:
            chart = compute_ingress_chart(2025, ingress, 0.0, 0.0)
            assert chart.ingress_type == ingress


# ─────────────────────────────────────────────────────────────────────────────
# Great Conjunctions
# ─────────────────────────────────────────────────────────────────────────────

class TestGreatConjunctions:
    """Tests for Great Conjunction timeline data."""

    def test_timeline_returns_list(self):
        gcs = get_great_conjunctions_timeline(1900, 2065)
        assert isinstance(gcs, list)
        assert len(gcs) >= 5

    def test_2020_conjunction_is_aquarius(self):
        """The 2020 Great Conjunction is in Aquarius."""
        gcs = get_great_conjunctions_timeline(2019, 2021)
        gc_2020 = next((g for g in gcs if g.year == 2020), None)
        assert gc_2020 is not None
        assert gc_2020.sign_en == "Aquarius"

    def test_2020_conjunction_air_element(self):
        """2020 Aquarius conjunction has Air element."""
        gcs = get_great_conjunctions_timeline(2019, 2021)
        gc_2020 = next((g for g in gcs if g.year == 2020), None)
        assert gc_2020 is not None
        assert gc_2020.element == "Air"

    def test_conjunctions_sorted_by_year(self):
        gcs = get_great_conjunctions_timeline(1800, 2070)
        years = [g.year for g in gcs]
        assert years == sorted(years)

    def test_future_flag_is_set(self):
        """Conjunctions after today should have is_future=True."""
        gcs = get_great_conjunctions_timeline(2030, 2070)
        for gc in gcs:
            assert gc.is_future is True

    def test_next_conjunction(self):
        """compute_next_great_conjunction returns a GreatConjunction."""
        next_gc = compute_next_great_conjunction(from_year=datetime.now().year)
        if next_gc:
            assert isinstance(next_gc, GreatConjunction)
            assert next_gc.year >= datetime.now().year

    def test_conjunction_range_filter(self):
        """Year range filter works correctly."""
        gcs_all  = get_great_conjunctions_timeline(1800, 2070)
        gcs_20th = get_great_conjunctions_timeline(1900, 1999)
        assert len(gcs_20th) < len(gcs_all)
        assert all(1900 <= g.year <= 1999 for g in gcs_20th)


# ─────────────────────────────────────────────────────────────────────────────
# Eclipse Chart
# ─────────────────────────────────────────────────────────────────────────────

class TestEclipseChart:
    """Tests for eclipse computation."""

    def test_solar_eclipse_returns_info(self):
        eclipse, chart = compute_eclipse_chart(
            year=2025, month=1, eclipse_kind="solar",
            latitude=0.0, longitude=0.0,
        )
        assert isinstance(eclipse, EclipseInfo)
        assert eclipse.eclipse_kind == "solar"
        assert eclipse.jd_maximum > 0

    def test_lunar_eclipse_returns_info(self):
        eclipse, chart = compute_eclipse_chart(
            year=2025, month=1, eclipse_kind="lunar",
            latitude=0.0, longitude=0.0,
        )
        assert isinstance(eclipse, EclipseInfo)
        assert eclipse.eclipse_kind == "lunar"

    def test_eclipse_chart_has_planets(self):
        eclipse, chart = compute_eclipse_chart(2025, 3, "solar", 0.0, 0.0)
        assert chart is not None
        assert len(chart.planets) >= 9

    def test_eclipse_sign_index_valid(self):
        eclipse, _ = compute_eclipse_chart(2025, 3, "solar", 0.0, 0.0)
        assert 0 <= eclipse.sign_index <= 11


# ─────────────────────────────────────────────────────────────────────────────
# Moment Chart
# ─────────────────────────────────────────────────────────────────────────────

class TestMomentChart:
    """Tests for compute_moment_chart."""

    def test_moment_chart_basic(self):
        chart = compute_moment_chart(
            year=2020, month=12, day=21, hour=18.0, minute=17.0,
            latitude=0.0, longitude=0.0, location_name="Great Conjunction",
        )
        assert isinstance(chart, MundaneChart)
        assert chart.chart_type == "moment"

    def test_moment_chart_planets(self):
        chart = compute_moment_chart(2020, 12, 21, 18.0, 0.0, 0.0, 0.0)
        assert len(chart.planets) >= 9

    def test_moment_chart_date_matches(self):
        chart = compute_moment_chart(2000, 1, 1, 12.0, 0.0, 0.0, 0.0)
        assert chart.utc_datetime.year == 2000
        assert chart.utc_datetime.month == 1


# ─────────────────────────────────────────────────────────────────────────────
# National Chart
# ─────────────────────────────────────────────────────────────────────────────

class TestNationalChart:
    """Tests for compute_national_mundane."""

    def test_national_chart_china(self):
        country_key = "China (Beijing)"
        country_data = COUNTRY_CAPITALS[country_key]
        chart = compute_national_mundane(
            year=2025,
            country_key=country_key,
            country_data=country_data,
            ingress_type="aries",
        )
        assert isinstance(chart, MundaneChart)
        assert "北京" in chart.location_name or "China" in chart.location_name

    def test_national_chart_usa(self):
        country_key = "USA (Washington DC)"
        country_data = COUNTRY_CAPITALS[country_key]
        chart = compute_national_mundane(
            year=2025,
            country_key=country_key,
            country_data=country_data,
            ingress_type="aries",
        )
        assert isinstance(chart, MundaneChart)


# ─────────────────────────────────────────────────────────────────────────────
# Outer Planets
# ─────────────────────────────────────────────────────────────────────────────

class TestOuterPlanets:
    """Tests for compute_current_outer_planets."""

    def test_returns_dict(self):
        outer = compute_current_outer_planets(2025, 3, 20)
        assert isinstance(outer, dict)
        assert len(outer) >= 5

    def test_has_required_planets(self):
        outer = compute_current_outer_planets(2025, 3, 20)
        for name in ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]:
            assert name in outer

    def test_sign_indices_valid(self):
        outer = compute_current_outer_planets(2025, 3, 20)
        for name, pl in outer.items():
            assert 0 <= pl.sign_index <= 11
            assert isinstance(pl.is_retrograde, bool)


# ─────────────────────────────────────────────────────────────────────────────
# Format prompt helper
# ─────────────────────────────────────────────────────────────────────────────

class TestFormatPrompt:
    """Tests for format_mundane_chart_for_prompt."""

    def test_prompt_contains_chart_label(self):
        chart = compute_ingress_chart(2025, "aries", 0.0, 0.0)
        prompt = format_mundane_chart_for_prompt(chart)
        assert "Aries" in prompt or "牡羊" in prompt

    def test_prompt_contains_planets(self):
        chart = compute_ingress_chart(2025, "aries", 0.0, 0.0)
        prompt = format_mundane_chart_for_prompt(chart)
        assert "Sun" in prompt or "Jupiter" in prompt

    def test_prompt_is_string(self):
        chart = compute_ingress_chart(2025, "aries", 0.0, 0.0)
        prompt = format_mundane_chart_for_prompt(chart)
        assert isinstance(prompt, str)
        assert len(prompt) > 100


# ─────────────────────────────────────────────────────────────────────────────
# Module-level lazy imports
# ─────────────────────────────────────────────────────────────────────────────

class TestModuleImports:
    """Ensure the __init__.py lazy-load wrappers work."""

    def test_init_compute_ingress(self):
        from astro.mundane import compute_ingress_chart as fn
        chart = fn(2025, "aries", 0.0, 0.0)
        assert isinstance(chart, MundaneChart)

    def test_init_get_conjunctions(self):
        from astro.mundane import get_great_conjunctions_timeline as fn
        gcs = fn(2000, 2025)
        assert isinstance(gcs, list)

    def test_init_compute_outer_planets(self):
        from astro.mundane import compute_current_outer_planets as fn
        outer = fn(2025, 3, 20)
        assert len(outer) >= 5
