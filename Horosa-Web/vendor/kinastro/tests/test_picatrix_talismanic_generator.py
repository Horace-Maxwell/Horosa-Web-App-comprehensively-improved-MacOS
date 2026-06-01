from __future__ import annotations

from datetime import datetime, timezone

import pytest

from astro.picatrix import generate_picatrix_talisman, select_picatrix_images


def test_select_picatrix_images_has_planetary_options():
    candidates = select_picatrix_images("wealth")
    assert candidates
    assert any(c.source_type == "planet" for c in candidates)


def test_generate_picatrix_harm_needs_explicit_flag():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError):
        generate_picatrix_talisman(
            purpose="harm",
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            timezone_offset=0.0,
            latitude=25.03,
            longitude=121.56,
            include_harmful=False,
            days_ahead=2,
        )


def test_generate_picatrix_talisman_structured_output():
    result = generate_picatrix_talisman(
        purpose="wealth",
        year=2026,
        month=5,
        day=20,
        hour=10,
        minute=0,
        timezone_offset=8.0,
        latitude=25.03,
        longitude=121.56,
        days_ahead=3,
    )

    assert result.election_details.score >= 0
    assert "en" in result.blueprint.invocation
    assert "zh" in result.blueprint.invocation
    assert "ar" in result.blueprint.invocation
    assert "planetary" in result.blueprint.materia
    assert result.blueprint.chart_snapshot_svg.startswith("<svg")
