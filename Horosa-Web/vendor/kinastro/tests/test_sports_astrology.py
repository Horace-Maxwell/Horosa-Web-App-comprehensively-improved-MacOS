from astro.sports import analyze_sports_horary


def test_sports_horary_returns_structured_match_analysis():
    result = analyze_sports_horary(
        match_name="Test Match",
        team1="Team A",
        team2="Team B",
        year=2025,
        month=6,
        day=1,
        hour=20,
        minute=0,
        timezone=0.0,
        latitude=51.5074,
        longitude=-0.1278,
        location_name="London",
        preferred_team="Team A",
    )

    ma = result.match_analysis
    assert isinstance(ma.team1_strength, float)
    assert isinstance(ma.team2_strength, float)
    assert isinstance(ma.key_testimonies, list)
    assert "Team A" in ma.winner_probability
    assert "Team B" in ma.winner_probability
    assert 0.0 <= ma.winner_probability["Team A"] <= 1.0
    assert 0.0 <= ma.winner_probability["Team B"] <= 1.0
    assert ma.explanation


def test_api_sports_horary_endpoint_exists():
    import pytest

    pytest.importorskip("fastapi")
    pytest.importorskip("plotly")
    import api_server

    routes = [r.path for r in api_server.app.routes]
    assert "/api/sports-horary" in routes
