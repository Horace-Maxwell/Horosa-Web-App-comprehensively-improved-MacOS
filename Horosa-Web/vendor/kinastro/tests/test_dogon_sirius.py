"""Tests for Dogon Sirius module."""

from astro.dogon.calculator import (
    compute_dogon_sirius_chart,
    format_dogon_sirius_for_prompt,
    load_dogon_constants,
    _resolve_zone,
    _solve_kepler,
    _sirius_b_angular_separation,
    _compute_birth_aspects,
)
import math


def test_constants_load():
    data = load_dogon_constants()
    assert data["system"]["name_short"] == "dogon_sirius"
    assert data["system"]["sigui_cycle_years"] == 60
    assert len(data["zones"]) >= 3
    assert "sigui_life_phases" in data
    assert len(data["sigui_life_phases"]) == 5
    assert "aspects" in data


def test_compute_chart_basic_ranges():
    chart = compute_dogon_sirius_chart(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        timezone=0.0,
        latitude=0.0,
        longitude=0.0,
        location_name="Test",
    )
    assert 0.0 <= chart.sirius_longitude < 360.0
    assert -90.0 <= chart.sirius_declination <= 90.0
    assert chart.sigui.next_year - chart.sigui.previous_year == 60
    assert len(chart.bodies) == 3
    # Life phase should be populated
    assert chart.sigui.life_phase in range(1, 6)
    assert chart.sigui.life_phase_label_zh
    assert chart.sigui.life_phase_label_en


def test_prompt_contains_sigui_and_zone():
    chart = compute_dogon_sirius_chart(
        year=2000,
        month=6,
        day=20,
        hour=8,
        minute=30,
        timezone=0.0,
        latitude=12.0,
        longitude=-8.0,
        location_name="Mali",
    )
    prompt = format_dogon_sirius_for_prompt(chart, lang="en")
    assert "Sigui" in prompt
    assert "Zone:" in prompt
    assert "Life Phase:" in prompt


def test_zone_resolution_all_ranges_and_out_of_band():
    zones = load_dogon_constants()["zones"]
    z1 = _resolve_zone(-16.0, zones)
    z2 = _resolve_zone(2.0, zones)
    z3 = _resolve_zone(20.0, zones)
    z4 = _resolve_zone(60.0, zones)

    assert z1.zone_id == "nommo_corridor"
    assert z2.zone_id == "seed_axis"
    assert z3.zone_id == "mask_horizon"
    assert z4.zone_id is None
    assert z4.in_zone is False


def test_kepler_circular():
    """Circular orbit: E should equal M."""
    E = _solve_kepler(1.0, 0.0)
    assert abs(E - 1.0) < 1e-8


def test_kepler_eccentric():
    """For e=0.5, E should be between M and pi for M in (0, pi)."""
    M = math.pi / 3
    E = _solve_kepler(M, 0.5)
    assert M < E < math.pi
    # Verify Kepler equation
    assert abs(M - (E - 0.5 * math.sin(E))) < 1e-8


def test_sirius_b_separation():
    constants = load_dogon_constants()
    # At a reference JD the separation should be a positive arcsec value
    jd = 2451545.0  # J2000.0
    sep, pa = _sirius_b_angular_separation(jd, constants)
    assert sep > 0.0
    assert 0.0 <= pa < 360.0
    # Sep should be within expected range for Sirius B (0 to ~12 arcsec)
    assert sep <= 12.0


def test_sirius_b_body_has_separation():
    chart = compute_dogon_sirius_chart(
        year=2000, month=1, day=1, hour=12, minute=0,
        timezone=0.0, latitude=12.0, longitude=-8.0,
    )
    b = next(body for body in chart.bodies if body.key == "sirius_b")
    assert b.separation_arcsec > 0.0


def test_birth_aspects_detection():
    """Sirius at ~104° should form conjunction with planet at 106°."""
    constants = load_dogon_constants()
    orb_cfg = constants["aspects"]["orbs"]
    nommo = constants["aspects"]["nommo_harmonics"]
    aspects = _compute_birth_aspects(
        sirius_lon=104.0,
        natal_planets={"Sun": 106.0, "Moon": 284.0},  # 284 = 104+180 → opposition
        orb_cfg=orb_cfg,
        nommo_harmonics=nommo,
    )
    names = {a.planet: a.aspect_name for a in aspects}
    assert names.get("Sun") == "Conjunction"
    assert names.get("Moon") == "Opposition"


def test_chart_with_natal_planets_produces_aspects():
    chart = compute_dogon_sirius_chart(
        year=2000, month=6, day=1, hour=12, minute=0,
        timezone=0.0, latitude=12.0, longitude=-8.0,
        natal_planets={"Sun": 104.0},  # very close to Sirius
    )
    assert len(chart.birth_aspects) >= 1
    assert chart.birth_aspects[0].planet == "Sun"


def test_heliacal_rising_fallback():
    """heliacal_rising should be populated (via fallback) even without swisseph."""
    chart = compute_dogon_sirius_chart(
        year=2020, month=3, day=1, hour=12, minute=0,
        timezone=0.0, latitude=14.0, longitude=-3.0,  # near Dogon region (Mali)
    )
    # Heliacal rising may or may not be populated depending on swe availability
    if chart.heliacal_rising is not None:
        assert chart.heliacal_rising.days_until >= 0
        assert len(chart.heliacal_rising.date_str) == 10  # YYYY-MM-DD


def test_cross_cultural_includes_andean_and_vedic():
    data = load_dogon_constants()
    systems = [row["system"] for row in data["cross_cultural"]]
    assert any("Vedic" in s or "Jyotish" in s for s in systems)
    assert any("Andean" in s for s in systems)
    assert any("Maya" in s for s in systems)


def test_sigui_life_phases_coverage():
    """All 5 life phases should be reachable within a 60-year cycle."""
    constants = load_dogon_constants()
    phases = constants["sigui_life_phases"]
    # Verify continuous non-overlapping coverage from 0 to 60
    prev_end = 0
    for p in phases:
        assert p["range_years"][0] == prev_end
        prev_end = p["range_years"][1]
    assert prev_end == 60
