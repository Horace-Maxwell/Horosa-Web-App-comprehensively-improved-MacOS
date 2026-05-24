"""
tests/test_etruscan.py — Tests for the Etruscan Astrology module
================================================================

Covers:
  • TEMPLUM_16 constants integrity
  • _azimuth_to_templum() boundary values
  • compute_etruscan_chart() basic ranges and extreme coordinates
  • EtruscanChart.to_json() serialisation
  • format_etruscan_for_prompt() output content
  • SVG / HTML renderer (no Streamlit required)

測試伊特魯里亞占星模組的核心邏輯，包含極端座標與歷史日期。
"""

from __future__ import annotations

import pytest

from astro.etruscan.constants import TEMPLUM_16, ETRUSCAN_PLANETS, LIGHTNING_INTERPRETATIONS
from astro.etruscan.calculator import (
    compute_etruscan_chart,
    format_etruscan_for_prompt,
    _azimuth_to_templum,
)
from astro.etruscan.renderer import build_piacenza_liver_svg


# ─────────────────────────────────────────────────────────────────────────────
# Constants tests
# ─────────────────────────────────────────────────────────────────────────────

def test_templum_16_count():
    """Should have exactly 16 Templum regions."""
    assert len(TEMPLUM_16) == 16


def test_templum_16_region_numbers():
    """Region numbers should be 1–16 without gaps."""
    nums = [t["region"] for t in TEMPLUM_16]
    assert sorted(nums) == list(range(1, 17))


def test_templum_16_azimuth_coverage():
    """All 16 regions should cover exactly 360° without overlap."""
    total = sum(t["azimuth_end"] - t["azimuth_start"] for t in TEMPLUM_16)
    assert abs(total - 360.0) < 1e-6


def test_templum_16_nature_valid():
    """Every region nature must be one of the three valid values."""
    valid = {"favorable", "unfavorable", "neutral"}
    for t in TEMPLUM_16:
        assert t["nature"] in valid, f"Region {t['region']} has invalid nature {t['nature']!r}"


def test_templum_16_required_keys():
    """Each Templum entry must contain all required keys."""
    required = {
        "region", "name_etruscan", "name_en", "name_zh",
        "deity_zh", "deity_en", "nature", "nature_zh",
        "azimuth_start", "azimuth_end", "color",
        "interpretation_zh", "interpretation_en",
    }
    for t in TEMPLUM_16:
        missing = required - set(t.keys())
        assert not missing, f"Region {t['region']} missing keys: {missing}"


def test_etruscan_planets_count():
    """Should have exactly 7 classical planets (Sun to Saturn)."""
    assert len(ETRUSCAN_PLANETS) == 7


def test_lightning_interpretations_count():
    """Should have exactly 9 lightning types (Tinia's nine thunderbolts)."""
    assert len(LIGHTNING_INTERPRETATIONS) == 9


def test_lightning_interpretations_severity_range():
    """All severity values should be in 1–5."""
    for lt in LIGHTNING_INTERPRETATIONS:
        assert 1 <= lt["severity"] <= 5, (
            f"Lightning type {lt['type_num']} has invalid severity {lt['severity']}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# _azimuth_to_templum() tests
# ─────────────────────────────────────────────────────────────────────────────

def test_azimuth_to_templum_north():
    """0° (North) should map to region 1."""
    assert _azimuth_to_templum(0.0) == 1


def test_azimuth_to_templum_region_boundary():
    """22.5° should start region 2."""
    assert _azimuth_to_templum(22.5) == 2


def test_azimuth_to_templum_east():
    """90° (East) should map to region 5 (4×22.5 = 90)."""
    assert _azimuth_to_templum(90.0) == 5


def test_azimuth_to_templum_south():
    """180° (South) should map to region 9 (8×22.5 = 180)."""
    assert _azimuth_to_templum(180.0) == 9


def test_azimuth_to_templum_west():
    """270° (West) should map to region 13."""
    assert _azimuth_to_templum(270.0) == 13


def test_azimuth_to_templum_wrap():
    """360° should wrap to region 1 (same as 0°)."""
    assert _azimuth_to_templum(360.0) == 1


def test_azimuth_to_templum_negative_wrap():
    """Negative azimuth should be normalised (e.g. -22.5° → 337.5° → region 16)."""
    assert _azimuth_to_templum(-22.5) == 16


def test_azimuth_to_templum_all_regions():
    """Every region (1–16) should be reachable via azimuth."""
    regions_seen = set()
    for i in range(16):
        az = i * 22.5 + 11.25  # midpoint of each sector
        r = _azimuth_to_templum(az)
        regions_seen.add(r)
    assert regions_seen == set(range(1, 17))


# ─────────────────────────────────────────────────────────────────────────────
# compute_etruscan_chart() tests
# ─────────────────────────────────────────────────────────────────────────────

def _basic_chart():
    """Return a chart computed for a well-known date / location."""
    return compute_etruscan_chart(
        year=2000, month=1, day=1,
        hour=12, minute=0,
        timezone=0.0,
        latitude=0.0, longitude=0.0,
        location_name="Test",
    )


def test_compute_basic_planet_count():
    """Chart should contain exactly 7 planet positions."""
    chart = _basic_chart()
    assert len(chart.planet_positions) == 7


def test_compute_templum_regions_in_range():
    """All Templum region numbers should be 1–16."""
    chart = _basic_chart()
    for pos in chart.planet_positions:
        assert 1 <= pos.templum_region <= 16, (
            f"{pos.planet_name_en} has out-of-range region {pos.templum_region}"
        )


def test_compute_longitude_in_range():
    """All ecliptic longitudes should be 0–360°."""
    chart = _basic_chart()
    for pos in chart.planet_positions:
        assert 0.0 <= pos.longitude < 360.0, (
            f"{pos.planet_name_en} longitude {pos.longitude} out of range"
        )


def test_compute_dominant_nature_valid():
    """dominant_nature should be one of the three valid values."""
    chart = _basic_chart()
    assert chart.dominant_nature in {"favorable", "unfavorable", "neutral"}


def test_compute_lightning_region_valid():
    """lightning_region (Sun's Templum) should be in 1–16."""
    chart = _basic_chart()
    assert 1 <= chart.lightning_region <= 16


def test_compute_jd_ut_reasonable():
    """J2000.0 JD_UT should be near 2451545."""
    chart = _basic_chart()
    assert abs(chart.jd_ut - 2451545.0) < 1.0


def test_compute_to_json():
    """to_json() should return a dict with expected top-level keys."""
    chart = _basic_chart()
    d = chart.to_json()
    required = {"year", "month", "day", "hour", "minute", "timezone",
                "latitude", "longitude", "jd_ut", "planet_positions",
                "lightning_region", "dominant_nature", "ritual_type"}
    missing = required - set(d.keys())
    assert not missing, f"to_json() missing keys: {missing}"


def test_compute_to_json_planet_count():
    """to_json() planets list should have 7 entries."""
    chart = _basic_chart()
    d = chart.to_json()
    assert len(d["planet_positions"]) == 7


def test_compute_summary_zh_contains_date():
    """summary_zh() should mention the year."""
    chart = _basic_chart()
    assert "2000" in chart.summary_zh()


def test_compute_summary_en_contains_date():
    """summary_en() should mention the year."""
    chart = _basic_chart()
    assert "2000" in chart.summary_en()


# ─────────────────────────────────────────────────────────────────────────────
# Extreme coordinate / historical date tests
# ─────────────────────────────────────────────────────────────────────────────

def test_compute_north_pole():
    """North Pole (lat=90°) should not raise an error."""
    chart = compute_etruscan_chart(
        year=2024, month=6, day=21,
        hour=12, minute=0,
        timezone=0.0,
        latitude=90.0, longitude=0.0,
    )
    assert len(chart.planet_positions) == 7


def test_compute_south_pole():
    """South Pole (lat=-90°) should not raise an error."""
    chart = compute_etruscan_chart(
        year=2024, month=12, day=21,
        hour=12, minute=0,
        timezone=0.0,
        latitude=-90.0, longitude=0.0,
    )
    assert len(chart.planet_positions) == 7


def test_compute_historical_ancient_rome():
    """Historical date near Etruscan period (100 BCE) should compute without error."""
    # Julian Calendar proleptic Gregorian approximation: 100 BCE = year -99
    chart = compute_etruscan_chart(
        year=-99, month=7, day=4,
        hour=6, minute=0,
        timezone=0.0,
        latitude=43.7, longitude=11.2,   # Approximate Etruscan Italy
        location_name="Etruria",
    )
    assert len(chart.planet_positions) == 7
    for pos in chart.planet_positions:
        assert 1 <= pos.templum_region <= 16


def test_compute_ritual_type_stored():
    """ritual_type parameter should be stored in the chart."""
    chart = compute_etruscan_chart(
        year=2024, month=3, day=15,
        hour=10, minute=0,
        timezone=1.0,
        latitude=43.7, longitude=11.2,
        ritual_type="national",
    )
    assert chart.ritual_type == "national"


def test_compute_extreme_west_longitude():
    """Extreme west longitude (-180°) should not raise an error."""
    chart = compute_etruscan_chart(
        year=2000, month=6, day=15,
        hour=0, minute=0,
        timezone=-12.0,
        latitude=0.0, longitude=-180.0,
    )
    assert len(chart.planet_positions) == 7


# ─────────────────────────────────────────────────────────────────────────────
# format_etruscan_for_prompt() tests
# ─────────────────────────────────────────────────────────────────────────────

def test_prompt_zh_contains_region_info():
    """Chinese prompt should contain region information."""
    chart = _basic_chart()
    prompt = format_etruscan_for_prompt(chart, lang="zh")
    assert "Templum" in prompt or "天宮" in prompt or "第" in prompt


def test_prompt_en_contains_region_info():
    """English prompt should contain region information."""
    chart = _basic_chart()
    prompt = format_etruscan_for_prompt(chart, lang="en")
    assert "Region" in prompt or "Templum" in prompt


def test_prompt_zh_contains_lightning():
    """Chinese prompt should mention the lightning region."""
    chart = _basic_chart()
    prompt = format_etruscan_for_prompt(chart, lang="zh")
    assert "閃電" in prompt or "Lightning" in prompt


def test_prompt_en_contains_nature():
    """English prompt should mention the dominant nature."""
    chart = _basic_chart()
    prompt = format_etruscan_for_prompt(chart, lang="en")
    assert any(n in prompt for n in ["favorable", "unfavorable", "neutral",
                                      "Favorable", "Unfavorable", "Neutral"])


# ─────────────────────────────────────────────────────────────────────────────
# SVG / HTML renderer tests (no Streamlit)
# ─────────────────────────────────────────────────────────────────────────────

def test_svg_returns_string():
    """build_piacenza_liver_svg() should return a non-empty string."""
    chart = _basic_chart()
    html = build_piacenza_liver_svg(chart, lang="zh")
    assert isinstance(html, str)
    assert len(html) > 500


def test_svg_contains_liver_element():
    """HTML output should contain the liver SVG element."""
    chart = _basic_chart()
    html = build_piacenza_liver_svg(chart, lang="zh")
    assert "piacenza-liver-svg" in html


def test_svg_contains_all_16_regions():
    """HTML output should reference all 16 region numbers."""
    chart = _basic_chart()
    html = build_piacenza_liver_svg(chart, lang="zh")
    for region_num in range(1, 17):
        assert f'data-region="{region_num}"' in html, (
            f"Region {region_num} not found in SVG output"
        )


def test_svg_contains_planet_markers():
    """HTML output should contain planet marker elements."""
    chart = _basic_chart()
    html = build_piacenza_liver_svg(chart, lang="zh")
    assert "planet-marker" in html


def test_svg_en_label():
    """English SVG should use English labels."""
    chart = _basic_chart()
    html = build_piacenza_liver_svg(chart, lang="en")
    assert "Piacenza Liver" in html or "Templum" in html


def test_svg_zh_label():
    """Chinese SVG should use Chinese labels."""
    chart = _basic_chart()
    html = build_piacenza_liver_svg(chart, lang="zh")
    assert "皮亞琴察" in html or "天宮" in html or "伊特魯里亞" in html


def test_svg_tooltip_javascript():
    """HTML output should include JavaScript for tooltips."""
    chart = _basic_chart()
    html = build_piacenza_liver_svg(chart, lang="zh")
    assert "<script>" in html
    assert "showTooltip" in html
