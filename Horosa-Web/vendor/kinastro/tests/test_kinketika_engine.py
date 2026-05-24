from __future__ import annotations

from datetime import datetime

from astro.kinketika.engine import KinketikaEngine


def test_ketika_lima_current_period_lookup() -> None:
    engine = KinketikaEngine()
    current = engine.get_current_period("ketika_lima", datetime(2026, 5, 19, 13, 20))
    assert current.name_malay.startswith("Sri")
    assert current.fortune == "baik"


def test_bintang_tujuh_current_period_lookup() -> None:
    engine = KinketikaEngine()
    current = engine.get_current_period("bintang_tujuh", datetime(2026, 5, 19, 23, 0))
    assert current.name_en == "Star of Venus"
    assert current.fortune == "baik"


def test_activity_planner_returns_good_and_bad_periods() -> None:
    engine = KinketikaEngine()
    result = engine.get_activity_plan("bintang_tujuh", "marriage")
    assert len(result["good"]) >= 1
    assert len(result["bad"]) >= 1


def test_daily_stats_counts_match_period_length() -> None:
    engine = KinketikaEngine()
    stats_lima = engine.get_daily_stats("ketika_lima")
    assert stats_lima["total"] == 5
    assert stats_lima["baik"] + stats_lima["nahas"] + stats_lima["sederhana"] == 5

    stats_tujuh = engine.get_daily_stats("bintang_tujuh")
    assert stats_tujuh["total"] == 7
    assert stats_tujuh["baik"] + stats_tujuh["nahas"] + stats_tujuh["sederhana"] == 7
