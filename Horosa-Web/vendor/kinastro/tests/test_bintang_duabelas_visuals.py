from __future__ import annotations

from datetime import datetime

from astro.bintang_duabelas import BintangDuabelasEngine
from astro.bintang_duabelas.visuals import (
    build_house_wheel_segments,
    build_planetary_hour_segments,
)


def test_house_wheel_segments_returns_12_and_highlight() -> None:
    engine = BintangDuabelasEngine()
    houses = engine.get_all_houses()
    segments = build_house_wheel_segments(houses, highlight_house=7, script="zh")
    assert len(segments) == 12
    highlighted = [segment for segment in segments if segment.is_highlighted]
    assert len(highlighted) == 1
    assert highlighted[0].house_number == 7


def test_house_wheel_segments_jawi_uses_arabic_name() -> None:
    engine = BintangDuabelasEngine()
    segments = build_house_wheel_segments(engine.get_all_houses(), highlight_house=None, script="jawi")
    first = next(segment for segment in segments if segment.house_number == 1)
    assert "بيت" in first.subtitle


def test_planetary_hour_segments_returns_24_and_marks_current() -> None:
    engine = BintangDuabelasEngine()
    daytime = engine.hours.get_hours_for_date(datetime(2026, 5, 14), is_night=False)
    nighttime = engine.hours.get_hours_for_date(datetime(2026, 5, 14), is_night=True)
    current = daytime[2]
    segments = build_planetary_hour_segments(daytime, nighttime, current_hour=current)
    assert len(segments) == 24
    current_hits = [segment for segment in segments if segment.is_current]
    assert len(current_hits) == 1
    assert current_hits[0].hour_number == 3
    assert current_hits[0].phase == "day"
