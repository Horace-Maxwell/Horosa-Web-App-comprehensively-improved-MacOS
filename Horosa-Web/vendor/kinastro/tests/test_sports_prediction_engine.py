from __future__ import annotations

from astro.sports.models import (
    HouseInfo,
    MatchInput,
    PlanetInfo,
    TeamProfile,
    VedicChartData,
    VedicPlanetInfo,
    WesternChartData,
)
from astro.sports.prediction_engine import predict_match
from astro.sports.storage import list_team_profiles, save_team_profile


def _fake_western_chart() -> WesternChartData:
    planets = [
        PlanetInfo(
            name="Sun",
            longitude=10.0,
            latitude=0.0,
            sign_index=0,
            sign_name="Aries",
            sign_degree=10.0,
            house=1,
            retrograde=False,
        ),
    ]
    houses = [
        HouseInfo(number=i + 1, cusp=float(i * 30), sign_index=i % 12, sign_name="X", lord="Mars")
        for i in range(12)
    ]
    return WesternChartData(
        ascendant=0.0,
        midheaven=90.0,
        planets=planets,
        houses=houses,
        julian_day=2460000.0,
    )


def _fake_vedic_chart() -> VedicChartData:
    vp = VedicPlanetInfo(
        name="Sun",
        longitude=10.0,
        rashi_index=0,
        rashi_name="Mesha",
        rashi_lord="Mars",
        sign_degree=10.0,
        nakshatra="Ashwini",
        nakshatra_pada=1,
        house=1,
        retrograde=False,
    )
    houses = [
        HouseInfo(number=i + 1, cusp=float(i * 30), sign_index=i % 12, sign_name="X", lord="Mars")
        for i in range(12)
    ]
    return VedicChartData(
        ascendant=0.0,
        asc_rashi_index=0,
        planets=[vp],
        houses=houses,
        navamsa_ascendant=0.0,
        navamsa_asc_rashi_index=0,
        navamsa_planets=[vp],
        julian_day=2460000.0,
        ayanamsa=24.0,
    )


def test_predict_match_returns_structured_sports_prediction(monkeypatch):
    monkeypatch.setattr("astro.sports.prediction_engine.compute_western_chart", lambda _m: _fake_western_chart())
    monkeypatch.setattr("astro.sports.prediction_engine.compute_vedic_chart", lambda _m: _fake_vedic_chart())
    monkeypatch.setattr(
        "astro.sports.prediction_engine.frawley_judgment",
        lambda *_args, **_kwargs: {
            "home_score": 8.0,
            "away_score": 4.0,
            "summary": "home edge",
            "evidences": [],
            "testimonies": {"leader": "home", "margin": 4.0},
            "injury_risk": {"home": 0.2, "away": 0.3},
            "reversal_indicator": 0.4,
        },
    )
    monkeypatch.setattr(
        "astro.sports.prediction_engine.vedic_judgment",
        lambda *_args, **_kwargs: {
            "home_points": 60.0,
            "away_points": 40.0,
            "summary": "vedic ok",
            "evidences": [],
        },
    )

    result = predict_match(
        MatchInput(
            year=2025,
            month=6,
            day=1,
            hour=20,
            minute=0,
            timezone=0.0,
            latitude=51.5,
            longitude=-0.1,
            home_team="Home",
            away_team="Away",
            analysis_mode="event",
        )
    )

    assert result.sports_prediction is not None
    assert result.sports_prediction.mode == "event"
    assert "Home" in result.sports_prediction.winner_prob
    assert 0 <= result.sports_prediction.confidence <= 1
    assert result.sports_prediction.reversal_indicator == 0.4


def test_storage_team_profile_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setattr("astro.sports.storage._DB_PATH", str(tmp_path / "sports_history.db"))
    row_id = save_team_profile(
        TeamProfile(
            name="Arsenal",
            sport="football",
            country="England",
            founded_year=1886,
            home_stadium="Emirates",
            tags=["epl", "london"],
        )
    )
    assert row_id > 0
    rows = list_team_profiles(sport="football")
    assert rows
    assert rows[0]["name"] == "Arsenal"
