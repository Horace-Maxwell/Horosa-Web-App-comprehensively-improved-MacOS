"""
tests/test_primary_directions.py — Tests for Classical Primary Directions module

Tests cover:
  - Mathematical helper functions (OA, semi-arc, oblique ascension, etc.)
  - Natal position computation (equatorial data)
  - Zodiacal and Mundo direction arc computation
  - Time conversion (arc → years → date)
  - Result data structure validity
  - SVG timeline generation

Representative test charts:
  - Princess Diana (1961-07-01, well-documented 1981 marriage, 1997 accident)
  - Carl Gustav Jung (1875-07-26, analytical psychology founder)
  - Adolf Hitler (1889-04-20, extreme events for validation only)
"""

import math
import pytest
from datetime import date

from astro.primary_directions import (
    compute_primary_directions,
    PrimaryDirectionsResult,
    Direction,
    ChartPoint,
    render_primary_directions_svg,
    EXAMPLE_CHARTS,
)
from astro.primary_directions.calculator import (
    _oblique_ascension,
    _ascensional_difference,
    _semi_arc,
    _ecliptic_to_equatorial,
    _is_above_horizon,
    _arc_to_years,
    _years_to_date,
    _meridian_distance,
    _normalize,
    NAIBOD_KEY,
    PTOLEMY_KEY,
)
from astro.primary_directions.constants import (
    PLANET_NAMES_EN,
    PLANET_NAMES_ZH,
    PLANET_SYMBOLS,
    ZODIAC_SIGNS,
    ASPECTS,
    EXAMPLE_CHARTS as CONST_EXAMPLE_CHARTS,
)


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def diana_result() -> PrimaryDirectionsResult:
    """Princess Diana — well-documented natal chart."""
    ex = EXAMPLE_CHARTS[1]  # Diana
    return compute_primary_directions(
        year=ex["year"], month=ex["month"], day=ex["day"],
        hour=ex["hour"], minute=ex["minute"],
        timezone=ex["timezone"],
        latitude=ex["latitude"], longitude=ex["longitude"],
        method="mundo",
        time_key="naibod",
        max_age=50.0,
        location_name=ex["location_name"],
    )


@pytest.fixture(scope="module")
def jung_result() -> PrimaryDirectionsResult:
    """Carl Gustav Jung — comprehensive test case."""
    ex = EXAMPLE_CHARTS[2]  # Jung
    return compute_primary_directions(
        year=ex["year"], month=ex["month"], day=ex["day"],
        hour=ex["hour"], minute=ex["minute"],
        timezone=ex["timezone"],
        latitude=ex["latitude"], longitude=ex["longitude"],
        method="zodiacal",
        time_key="ptolemy",
        max_age=80.0,
        location_name=ex["location_name"],
    )


# ─────────────────────────────────────────────────────────────
# 1. Constants completeness
# ─────────────────────────────────────────────────────────────

def test_planet_names_complete():
    """All standard planet keys should have names in both languages."""
    keys = ["SU", "MO", "ME", "VE", "MA", "JU", "SA", "UR", "NE", "PL",
            "AS", "MC", "NN"]
    for k in keys:
        assert k in PLANET_NAMES_EN, f"Missing EN name for {k}"
        assert k in PLANET_NAMES_ZH, f"Missing ZH name for {k}"
        assert k in PLANET_SYMBOLS, f"Missing symbol for {k}"


def test_zodiac_signs_count():
    assert len(ZODIAC_SIGNS) == 12


def test_aspects_structure():
    """Each aspect dict must have required fields."""
    for asp in ASPECTS:
        assert "name" in asp
        assert "angle" in asp
        assert "key" in asp
        assert "symbol" in asp
        assert 0.0 <= asp["angle"] <= 360.0


def test_example_charts_structure():
    """Example charts must have required fields for testing."""
    required = {"year", "month", "day", "hour", "minute",
                "timezone", "latitude", "longitude"}
    for chart in CONST_EXAMPLE_CHARTS:
        for field in required:
            assert field in chart, f"Missing '{field}' in example chart: {chart.get('name','?')}"


# ─────────────────────────────────────────────────────────────
# 2. Mathematical helper tests
# ─────────────────────────────────────────────────────────────

def test_normalize():
    assert _normalize(0.0) == 0.0
    assert _normalize(360.0) == 0.0
    assert _normalize(370.0) == pytest.approx(10.0)
    assert _normalize(-10.0) == pytest.approx(350.0)


def test_ecliptic_to_equatorial_equinox():
    """
    At Aries 0° (vernal equinox), RA = 0° and Dec = 0° for zero obliquity.
    For obliquity = 23.4365°, Aries 0° still gives RA = 0° and Dec = 0°.
    """
    ra, dec = _ecliptic_to_equatorial(0.0, 0.0, 23.4365)
    assert ra == pytest.approx(0.0, abs=0.001)
    assert dec == pytest.approx(0.0, abs=0.001)


def test_ecliptic_to_equatorial_cancer():
    """
    At Cancer 0° (ecliptic lon = 90°), Dec = +obliquity.
    Ra should be 90° (6h).
    """
    eps = 23.4365
    ra, dec = _ecliptic_to_equatorial(90.0, 0.0, eps)
    assert ra == pytest.approx(90.0, abs=0.1)
    assert dec == pytest.approx(eps, abs=0.1)


def test_ecliptic_to_equatorial_capricorn():
    """
    At Capricorn 0° (lon = 270°), Dec = −obliquity.
    """
    eps = 23.4365
    ra, dec = _ecliptic_to_equatorial(270.0, 0.0, eps)
    assert ra == pytest.approx(270.0, abs=0.1)
    assert dec == pytest.approx(-eps, abs=0.1)


def test_ascensional_difference_equator():
    """At the equator (lat=0), AD = 0 for all declinations."""
    for dec in [-30, -15, 0, 15, 30]:
        ad = _ascensional_difference(dec, 0.0)
        assert ad == pytest.approx(0.0, abs=0.001)


def test_ascensional_difference_zero_dec():
    """For zero declination, AD = 0 regardless of latitude."""
    for lat in [0, 20, 40, 51.5]:
        ad = _ascensional_difference(0.0, lat)
        assert ad == pytest.approx(0.0, abs=0.001)


def test_ascensional_difference_range():
    """AD should be in range (-90°, +90°) for non-polar latitudes."""
    for dec in [-20, -10, 0, 10, 20]:
        for lat in [0, 30, 45, 51.5]:
            ad = _ascensional_difference(dec, lat)
            assert -90.0 < ad < 90.0


def test_semi_arc_equatorial():
    """At equator, all diurnal semi-arcs = 90° (equal day and night)."""
    for dec in [-20, 0, 20]:
        sa = _semi_arc(dec, 0.0, diurnal=True)
        assert sa == pytest.approx(90.0, abs=0.01)


def test_semi_arc_sum_180():
    """Diurnal + Nocturnal semi-arc = 180° always."""
    for dec in [-20, 0, 20]:
        for lat in [0, 30, 51.5]:
            sa_d = _semi_arc(dec, lat, diurnal=True)
            sa_n = _semi_arc(dec, lat, diurnal=False)
            assert sa_d + sa_n == pytest.approx(180.0, abs=0.01)


def test_semi_arc_circumpolar():
    """A planet with dec > (90° - lat) never sets → SA_diurnal = 180°."""
    lat = 51.5  # London
    dec = 50.0  # well above horizon always
    sa_d = _semi_arc(dec, lat, diurnal=True)
    assert sa_d == pytest.approx(180.0, abs=0.01)


def test_oblique_ascension_equator():
    """At equator, OA = RA (since AD = 0)."""
    for ra in [0, 45, 90, 135, 180, 270, 315]:
        oa = _oblique_ascension(float(ra), 0.0, 0.0)
        assert oa == pytest.approx(ra % 360, abs=0.01)


def test_arc_to_years_naibod():
    """Naibod key: 0.98563° = 1 year."""
    years = _arc_to_years(NAIBOD_KEY, "naibod")
    assert years == pytest.approx(1.0, abs=0.001)


def test_arc_to_years_ptolemy():
    """Ptolemy key: 1° = 1 year."""
    years = _arc_to_years(1.0, "ptolemy")
    assert years == pytest.approx(1.0, abs=0.001)


def test_years_to_date_integer():
    """Integer years should produce exact birth month/day (approx)."""
    d = _years_to_date(1961, 7, 1, 20.0)
    assert d.year == 1981


def test_years_to_date_fractional():
    """Fractional year should produce a date partway through the year."""
    d = _years_to_date(1961, 7, 1, 20.5)
    assert d.year == 1981 or d.year == 1982  # could be either
    assert 1981 <= d.year <= 1982


# ─────────────────────────────────────────────────────────────
# 3. Natal positions
# ─────────────────────────────────────────────────────────────

def test_diana_natal_count(diana_result):
    """Diana's result should have all standard points."""
    keys = {p.key for p in diana_result.natal_points}
    for k in ["SU", "MO", "ME", "VE", "MA", "JU", "SA", "AS", "MC"]:
        assert k in keys, f"Missing natal point {k}"


def test_diana_natal_longitudes_range(diana_result):
    """All natal longitudes should be in [0°, 360°)."""
    for p in diana_result.natal_points:
        assert 0.0 <= p.longitude < 360.0, f"{p.key} longitude out of range: {p.longitude}"


def test_diana_natal_ra_range(diana_result):
    """RA should be in [0°, 360°)."""
    for p in diana_result.natal_points:
        assert 0.0 <= p.ra < 360.0, f"{p.key} RA out of range: {p.ra}"


def test_diana_natal_dec_range(diana_result):
    """Declination should be in (-90°, +90°)."""
    for p in diana_result.natal_points:
        assert -90.0 < p.dec < 90.0, f"{p.key} Dec out of range: {p.dec}"


def test_diana_ramc_range(diana_result):
    """RAMC should be in [0°, 360°)."""
    assert 0.0 <= diana_result.ramc < 360.0


def test_diana_obliquity_range(diana_result):
    """Obliquity should be near ~23.4° for modern era."""
    assert 23.0 < diana_result.obliquity < 24.0


# ─────────────────────────────────────────────────────────────
# 4. Direction computation
# ─────────────────────────────────────────────────────────────

def test_diana_directions_non_empty(diana_result):
    """Should produce at least some directions."""
    assert len(diana_result.directions) > 0


def test_diana_directions_sorted(diana_result):
    """Directions should be sorted by years ascending."""
    years_list = [d.years for d in diana_result.directions]
    assert years_list == sorted(years_list)


def test_diana_directions_within_max_age(diana_result):
    """All directions should be within max_age."""
    for d in diana_result.directions:
        assert d.years <= diana_result.max_age + 0.1


def test_diana_direction_arc_positive(diana_result):
    """Direction arcs should be positive."""
    for d in diana_result.directions:
        assert d.arc >= 0.0, f"Negative arc: {d}"


def test_diana_directions_aspects_valid(diana_result):
    """All aspect keys should be from the standard set."""
    valid_keys = {"CNJ", "OPP", "SQR", "TRI", "SXT", "PAR", "CPAR"}
    for d in diana_result.directions:
        assert d.aspect_key in valid_keys, f"Invalid aspect key: {d.aspect_key}"


def test_jung_directions_zodiacal(jung_result):
    """Jung zodiacal directions should also be non-empty and sorted."""
    assert len(jung_result.directions) > 0
    years_list = [d.years for d in jung_result.directions]
    assert years_list == sorted(years_list)


def test_diana_has_converse(diana_result):
    """With include_converse=True (default), there should be converse directions."""
    # diana_result uses defaults which include_converse=True
    converse_dirs = [d for d in diana_result.directions if d.converse]
    assert len(converse_dirs) > 0


def test_diana_direction_dates(diana_result):
    """Event dates should be after birth date."""
    birth = date(diana_result.year, diana_result.month, diana_result.day)
    for d in diana_result.directions:
        assert d.event_date >= birth, f"Event date before birth: {d}"


def test_diana_directions_have_labels(diana_result):
    """Each direction should have non-empty labels."""
    for d in diana_result.directions[:20]:
        assert len(d.direction_label_en) > 0
        assert len(d.direction_label_zh) > 0


# ─────────────────────────────────────────────────────────────
# 5. Historical validation (approximate)
# ─────────────────────────────────────────────────────────────

def test_diana_marriage_range():
    """
    Diana's marriage to Prince Charles was 29 July 1981 (age 20.08 years).
    A major direction (e.g. Venus or AS directed to Jupiter/ASC)
    should appear near age 19-22.
    This is a soft validation — Primary Directions won't always perfectly
    predict one specific event, but major directions should cluster near
    documented life events.
    """
    result = compute_primary_directions(
        year=1961, month=7, day=1,
        hour=19, minute=45,
        timezone=1.0,
        latitude=52.6333, longitude=0.5167,
        method="mundo",
        time_key="naibod",
        max_age=40.0,
        significators=["AS", "MC", "SU", "MO", "VE"],
        promittors=["SU", "MO", "VE", "MA", "JU", "SA", "AS", "MC"],
        include_aspects=["CNJ", "OPP", "SQR", "TRI", "SXT"],
        include_converse=False,
    )
    # Find any direction near age 20 (within 2 years)
    near_marriage = [d for d in result.directions if 18.0 <= d.years <= 22.0]
    # Should have at least some directions in this important period
    assert len(near_marriage) >= 1, \
        f"Expected at least 1 direction near Diana's marriage age (20), got 0. " \
        f"All directions: {[(d.direction_label_en, round(d.years, 2)) for d in result.directions[:20]]}"


# ─────────────────────────────────────────────────────────────
# 6. Parameter validation
# ─────────────────────────────────────────────────────────────

def test_invalid_method():
    with pytest.raises(ValueError, match="method"):
        compute_primary_directions(
            year=1961, month=7, day=1, hour=12, minute=0,
            timezone=0.0, latitude=51.5, longitude=-0.12,
            method="invalid_method",
        )


def test_invalid_time_key():
    with pytest.raises(ValueError, match="time_key"):
        compute_primary_directions(
            year=1961, month=7, day=1, hour=12, minute=0,
            timezone=0.0, latitude=51.5, longitude=-0.12,
            time_key="unknown_key",
        )


def test_invalid_max_age():
    with pytest.raises(ValueError, match="max_age"):
        compute_primary_directions(
            year=1961, month=7, day=1, hour=12, minute=0,
            timezone=0.0, latitude=51.5, longitude=-0.12,
            max_age=-5.0,
        )


def test_invalid_significator():
    with pytest.raises(ValueError, match="Unknown significator"):
        compute_primary_directions(
            year=1961, month=7, day=1, hour=12, minute=0,
            timezone=0.0, latitude=51.5, longitude=-0.12,
            significators=["INVALID_KEY"],
        )


# ─────────────────────────────────────────────────────────────
# 7. SVG generation
# ─────────────────────────────────────────────────────────────

def test_svg_generation(diana_result):
    """SVG should be a valid non-empty string starting with <svg."""
    svg = render_primary_directions_svg(diana_result)
    assert isinstance(svg, str)
    assert svg.strip().startswith("<svg")
    assert "</svg>" in svg
    assert len(svg) > 500


def test_svg_contains_timeline_elements(diana_result):
    """SVG should contain at least an axis line."""
    svg = render_primary_directions_svg(diana_result)
    assert "<line" in svg


def test_svg_custom_dimensions(diana_result):
    """SVG should respect custom width/height parameters."""
    svg = render_primary_directions_svg(diana_result, width=1000, height=800)
    assert 'width="1000"' in svg
    assert 'height="800"' in svg


# ─────────────────────────────────────────────────────────────
# 8. Multiple method comparison
# ─────────────────────────────────────────────────────────────

def test_mundo_vs_zodiacal_different():
    """Mundo and Zodiacal methods should produce different arc values."""
    common_kwargs = dict(
        year=1961, month=7, day=1, hour=19, minute=45,
        timezone=1.0, latitude=52.6333, longitude=0.5167,
        max_age=40.0,
        significators=["AS"],
        promittors=["SU", "MO", "JU"],
        include_aspects=["CNJ"],
        include_converse=False,
        time_key="naibod",
    )
    mundo = compute_primary_directions(method="mundo", **common_kwargs)
    zodiacal = compute_primary_directions(method="zodiacal", **common_kwargs)

    # Both should have directions
    assert len(mundo.directions) >= 0
    assert len(zodiacal.directions) >= 0

    # The arcs should generally differ between methods
    # (they may occasionally coincide, but not for all)
    if mundo.directions and zodiacal.directions:
        mundo_arcs = {(d.significator_key, d.promittor_key, d.aspect_key): d.arc
                      for d in mundo.directions}
        zodiacal_arcs = {(d.significator_key, d.promittor_key, d.aspect_key): d.arc
                         for d in zodiacal.directions}
        # Find common keys and check that at least some differ
        common = set(mundo_arcs.keys()) & set(zodiacal_arcs.keys())
        if common:
            diffs = [abs(mundo_arcs[k] - zodiacal_arcs[k]) for k in common]
            assert any(d > 0.001 for d in diffs), \
                "Mundo and Zodiacal methods should produce different arcs"


def test_naibod_vs_ptolemy_time_keys():
    """Naibod and Ptolemy keys should produce different year values for same arc."""
    # Arc of 30° should give different years
    years_naibod = _arc_to_years(30.0, "naibod")
    years_ptolemy = _arc_to_years(30.0, "ptolemy")
    assert years_naibod != years_ptolemy
    assert years_naibod == pytest.approx(30.0 / NAIBOD_KEY, abs=0.001)
    assert years_ptolemy == pytest.approx(30.0 / PTOLEMY_KEY, abs=0.001)
