from __future__ import annotations

from datetime import datetime, time

from astro.bintang_duabelas import (
    AbjadCalculator,
    BintangDuabelasEngine,
    BintangDuabelasRequest,
    normalize_name,
)


def test_abjad_arabic_reference_value() -> None:
    calc = AbjadCalculator()
    assert calc.name_to_abjad("عثمان") == 661


def test_abjad_jawi_special_letters_are_supported() -> None:
    calc = AbjadCalculator()
    assert calc.name_to_abjad("ڤڽڠ") == 1090


def test_roman_name_override_matches_arabic_value() -> None:
    calc = AbjadCalculator()
    assert calc.name_to_abjad("Ahmad") == calc.name_to_abjad("احمد")


def test_normalize_name_detects_roman_and_uses_override() -> None:
    normalized = normalize_name("Uthman")
    assert normalized.normalized == "عثمان"
    assert normalized.used_override is True


def test_hisab_disease_reference_example() -> None:
    engine = BintangDuabelasEngine()
    result = engine.diagnose_disease("عثمان", day_name="isnin")
    assert result["total"] == 673
    assert result["remainder"] == 1
    assert result["source"] == "Jin (精靈)"


def test_marriage_compatibility_accepts_romanized_names() -> None:
    engine = BintangDuabelasEngine()
    result = engine.check_marriage_compatibility("Ahmad", "Fatimah")
    assert result["combined"] > 0
    assert "result" in result


def test_full_reading_maps_star_sign_to_house() -> None:
    engine = BintangDuabelasEngine()
    result = engine.get_full_reading("Ahmad", "Khadijah")
    assert result["star_sign"]["sign_number"] == result["house"]["house_number"]


def test_planetary_hours_day_schedule_uses_birth_datetime_weekday() -> None:
    engine = BintangDuabelasEngine()
    result = engine.get_planetary_hours(
        datetime(2026, 5, 14, 10, 15),
        sunrise=time(6, 0),
        sunset=time(18, 0),
    )
    assert result["phase"] == "day"
    assert len(result["hours"]) == 12
    assert result["hours"][0]["sequence"] == "khamis"
    assert result["hours"][0]["planet_en"] == "Jupiter"
    assert result["current_hour"]["hour"] == 5


def test_planetary_hours_night_schedule_after_sunset_rolls_to_next_malay_day() -> None:
    engine = BintangDuabelasEngine()
    result = engine.get_planetary_hours(
        datetime(2026, 5, 14, 20, 30),
        sunrise=time(6, 0),
        sunset=time(18, 0),
    )
    assert result["phase"] == "night"
    assert result["hours"][0]["sequence"] == "malam_jumaat"
    assert result["hours"][0]["planet_en"] == "Moon"


def test_planetary_hours_predawn_uses_previous_evening_sequence() -> None:
    engine = BintangDuabelasEngine()
    result = engine.get_planetary_hours(
        datetime(2026, 5, 14, 2, 30),
        sunrise=time(6, 0),
        sunset=time(18, 0),
    )
    assert result["phase"] == "night"
    assert result["hours"][0]["sequence"] == "malam_khamis"
    assert result["current_hour"]["hour"] == 9


def test_run_question_dispatches_azimat_request() -> None:
    engine = BintangDuabelasEngine()
    request = BintangDuabelasRequest(
        question_type="azimat",
        primary_name="Ahmad",
        azimat_purpose="protection",
    )
    response = engine.run_question(request)
    assert response["day_name"] == "ahad"
    assert response["result"]["purpose"] == "protection"
    assert response["normalized_inputs"]["primary_name"]["normalized"] == "احمد"
