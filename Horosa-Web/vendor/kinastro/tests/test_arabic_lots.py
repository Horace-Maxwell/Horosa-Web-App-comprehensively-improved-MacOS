"""Tests for astro.arabic_lots Al-Biruni 97 engine."""

from __future__ import annotations

from collections import Counter

from astro.arabic_lots import (
    AL_BIRUNI_97_LOTS,
    compute_albiruni_lots,
    get_top_priority_lots,
)


def _sample_kwargs() -> dict:
    return {
        "year": 1990,
        "month": 1,
        "day": 1,
        "hour": 12,
        "minute": 0,
        "timezone": 8.0,
        "latitude": 22.3193,
        "longitude": 114.1694,
    }


def test_albiruni_lot_definition_count_and_categories():
    assert len(AL_BIRUNI_97_LOTS) == 97
    counts = Counter(d.category for d in AL_BIRUNI_97_LOTS)
    assert counts["planetary"] == 7
    assert counts["houses"] == 80
    assert counts["special"] == 10


def test_compute_albiruni_lots_basic_ranges():
    result = compute_albiruni_lots(**_sample_kwargs(), zodiac_mode="tropical")
    assert len(result.lots) == 97
    assert isinstance(result.is_day_chart, bool)
    assert 0 <= result.ascendant < 360
    assert 0 <= result.sun_longitude < 360

    for lot in result.lots:
        assert 0 <= lot.longitude < 360
        assert 0 <= lot.degree_in_sign < 30
        assert 1 <= lot.house <= 12


def test_day_and_night_charts_are_distinct_for_sect_sensitive_lots():
    day_result = compute_albiruni_lots(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        timezone=8.0,
        latitude=22.3193,
        longitude=114.1694,
        zodiac_mode="tropical",
    )
    night_result = compute_albiruni_lots(
        year=1990,
        month=1,
        day=1,
        hour=0,
        minute=30,
        timezone=8.0,
        latitude=22.3193,
        longitude=114.1694,
        zodiac_mode="tropical",
    )

    assert day_result.is_day_chart is True
    assert night_result.is_day_chart is False

    day_fortune = next((l for l in day_result.lots if l.id == "lot_fortune"), None)
    night_fortune = next((l for l in night_result.lots if l.id == "lot_fortune"), None)
    assert day_fortune is not None
    assert night_fortune is not None
    assert day_fortune.formula_day == "ASC + MOON - SUN"
    assert day_fortune.formula_night == "ASC + SUN - MOON"
    assert night_fortune.formula_day == "ASC + MOON - SUN"
    assert night_fortune.formula_night == "ASC + SUN - MOON"
    assert abs(day_fortune.longitude - night_fortune.longitude) > 0.1


def test_tropical_and_sidereal_results_differ():
    tropical = compute_albiruni_lots(**_sample_kwargs(), zodiac_mode="tropical")
    sidereal = compute_albiruni_lots(**_sample_kwargs(), zodiac_mode="sidereal")

    tropical_first = next(l for l in tropical.lots if l.id == "lot_fortune")
    sidereal_first = next(l for l in sidereal.lots if l.id == "lot_fortune")
    assert abs(tropical_first.longitude - sidereal_first.longitude) > 0.1


def test_edge_latitude_still_computes():
    result = compute_albiruni_lots(
        year=1998,
        month=6,
        day=21,
        hour=3,
        minute=45,
        timezone=0.0,
        latitude=69.6492,
        longitude=18.9553,
        zodiac_mode="tropical",
    )
    assert len(result.lots) == 97


def test_top_priority_lots_size_and_order():
    result = compute_albiruni_lots(**_sample_kwargs())
    top10 = get_top_priority_lots(result, top_n=10)
    assert len(top10) == 10
    assert top10[0].priority >= top10[-1].priority
