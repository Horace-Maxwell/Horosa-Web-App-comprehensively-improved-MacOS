"""Tests for the European Geomancy module."""

from __future__ import annotations

from astro.european_geomancy import (
    FIGURES,
    all_figures,
    build_house_chart,
    build_shield_chart,
    figure_from_pattern,
    generate_reading,
    structured_interpretation,
)


def test_figures_count_is_16() -> None:
    assert len(FIGURES) == 16
    assert len(all_figures()) == 16


def test_each_figure_has_complete_correspondence() -> None:
    for fig in all_figures():
        assert len(fig.pattern) == 4
        assert all(isinstance(x, bool) for x in fig.pattern)
        assert fig.element
        assert fig.planet
        assert fig.zodiac
        assert fig.positive_keywords
        assert fig.negative_keywords
        assert fig.historical_meaning


def test_shield_chart_chain_sizes() -> None:
    mothers = list(all_figures())[:4]
    shield = build_shield_chart(mothers, figure_from_pattern)
    assert len(shield.mothers) == 4
    assert len(shield.daughters) == 4
    assert len(shield.nieces) == 4
    assert len(shield.witnesses) == 2
    assert len(shield.figures_16) == 16


def test_house_chart_has_12_houses() -> None:
    mothers = list(all_figures())[:4]
    shield = build_shield_chart(mothers, figure_from_pattern)
    houses = build_house_chart(shield)
    assert len(houses) == 12
    assert set(houses.keys()) == set(range(1, 13))


def test_generate_reading_all_methods() -> None:
    for method in ("traditional", "coin", "number"):
        r = generate_reading(question="test", cast_method=method, seed=42)
        assert len(r.mothers) == 4
        assert len(r.houses) == 12
        assert r.shield.judge.latin


def test_generate_reading_manual() -> None:
    r = generate_reading(
        question="manual",
        cast_method="manual",
        manual_input="1 1 1 1\n2 2 2 2\n1 2 1 2\n2 1 2 1",
        seed=42,
    )
    assert r.mothers[0].latin == "Via"
    assert r.mothers[1].latin == "Populus"


def test_structured_interpretation_sections() -> None:
    r = generate_reading(question="career", question_type="career", seed=123)
    interp = structured_interpretation(r, lang="zh")
    assert set(interp.keys()) == {"current_state", "development", "aids_obstacles", "outcome"}
