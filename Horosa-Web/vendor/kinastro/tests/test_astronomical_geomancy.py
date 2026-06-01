"""
tests/test_astronomical_geomancy.py
════════════════════════════════════
Unit tests for the Astronomical Geomancy module
(Gerardus Cremonensis, 地占占星).
"""

from __future__ import annotations

import pytest

from astro.astronomical_geomancy.calculator import (
    compute_geomancy_chart,
    format_geomancy_for_prompt,
    _generate_figure,
    _build_houses,
    _place_planets,
)
from astro.astronomical_geomancy.constants import (
    FIGURES,
    PLANETS,
    ZODIAC_SIGNS,
    QUESTION_TYPES,
)
from astro.astronomical_geomancy.models import (
    GeomancyChart,
    GeomancyFigure,
    HouseInfo,
    PlanetInHouse,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

def test_figures_count():
    """There must be exactly 16 geomantic figures."""
    assert len(FIGURES) == 16


def test_all_figures_have_required_keys():
    required = {"name_en", "name_zh", "dots", "element", "planet", "sign", "sign_num", "quality"}
    for name, data in FIGURES.items():
        missing = required - set(data.keys())
        assert not missing, f"Figure '{name}' missing keys: {missing}"


def test_figure_dots_are_4_booleans():
    for name, data in FIGURES.items():
        dots = data["dots"]
        assert len(dots) == 4, f"Figure '{name}' has {len(dots)} rows, expected 4"
        assert all(isinstance(d, bool) for d in dots), f"Figure '{name}' dots must be bools"


def test_zodiac_signs_count():
    assert len(ZODIAC_SIGNS) == 12


def test_planets_count():
    """Must have exactly 9 bodies (7 planets + Caput + Cauda)."""
    assert len(PLANETS) == 9


def test_question_types_count():
    assert len(QUESTION_TYPES) >= 10


def test_all_signs_covered():
    """Every zodiac sign must appear in at least one figure's mapping."""
    sign_nums_covered = {d["sign_num"] for d in FIGURES.values()}
    for i in range(12):
        assert i in sign_nums_covered, f"Sign index {i} ({ZODIAC_SIGNS[i]['en']}) not covered"


# ─────────────────────────────────────────────────────────────────────────────
# Figure generation
# ─────────────────────────────────────────────────────────────────────────────

def test_generate_figure_returns_valid_figure():
    import random
    rng = random.Random(42)
    fig = _generate_figure(rng)
    assert isinstance(fig, GeomancyFigure)
    assert fig.name_en in {d["name_en"] for d in FIGURES.values()}
    assert len(fig.dots) == 4


def test_generate_figure_deterministic_with_seed():
    import random
    rng1 = random.Random(123)
    rng2 = random.Random(123)
    fig1 = _generate_figure(rng1)
    fig2 = _generate_figure(rng2)
    assert fig1.name_en == fig2.name_en
    assert fig1.dots == fig2.dots


# ─────────────────────────────────────────────────────────────────────────────
# House building
# ─────────────────────────────────────────────────────────────────────────────

def test_build_houses_returns_12_houses():
    houses = _build_houses(0)
    assert len(houses) == 12


def test_build_houses_sequential_signs():
    """Starting at sign 0 (Aries), house 2 should be Taurus, etc."""
    houses = _build_houses(0)
    for i, house in enumerate(houses):
        expected_sign = ZODIAC_SIGNS[i]["en"]
        assert house.sign == expected_sign, (
            f"House {i+1}: expected {expected_sign}, got {house.sign}"
        )


def test_build_houses_wraps_around():
    """Starting at sign 11 (Pisces), house 2 should be Aries (index 0)."""
    houses = _build_houses(11)
    assert houses[0].sign == "Pisces"
    assert houses[1].sign == "Aries"
    assert houses[11].sign == "Aquarius"


def test_build_houses_numbering():
    houses = _build_houses(3)
    for i, h in enumerate(houses):
        assert h.house == i + 1


# ─────────────────────────────────────────────────────────────────────────────
# Planet placement
# ─────────────────────────────────────────────────────────────────────────────

def test_place_planets_returns_9_entries():
    import random
    rng = random.Random(1)
    houses = _build_houses(0)
    placements = _place_planets(rng, houses)
    assert len(placements) == 9


def test_planet_houses_in_range():
    import random
    rng = random.Random(7)
    houses = _build_houses(0)
    placements = _place_planets(rng, houses)
    for p in placements:
        assert 1 <= p.house <= 12, f"{p.planet_en} has invalid house {p.house}"


def test_planet_placements_assigned_to_house_planets():
    import random
    rng = random.Random(99)
    houses = _build_houses(0)
    placements = _place_planets(rng, houses)
    # All planet placements should be reflected in house.planets
    for p in placements:
        house = houses[p.house - 1]
        assert any(hp.planet_key == p.planet_key for hp in house.planets), (
            f"{p.planet_en} not found in house {p.house}.planets"
        )


# ─────────────────────────────────────────────────────────────────────────────
# compute_geomancy_chart
# ─────────────────────────────────────────────────────────────────────────────

def test_compute_basic():
    chart = compute_geomancy_chart(
        question="Test question",
        question_type="wealth",
        seed_mode="manual",
        manual_seed=42,
    )
    assert isinstance(chart, GeomancyChart)
    assert len(chart.houses) == 12
    assert len(chart.planet_placements) == 9
    assert len(chart.mother_figures) == 4
    assert chart.question == "Test question"
    assert chart.question_type == "wealth"


def test_compute_deterministic():
    """Same seed should produce identical charts."""
    chart1 = compute_geomancy_chart(seed_mode="manual", manual_seed=555)
    chart2 = compute_geomancy_chart(seed_mode="manual", manual_seed=555)
    assert chart1.ascendant_sign == chart2.ascendant_sign
    assert chart1.ascendant_figure.name_en == chart2.ascendant_figure.name_en
    for p1, p2 in zip(chart1.planet_placements, chart2.planet_placements):
        assert p1.house == p2.house


def test_compute_different_seeds_differ():
    """Different seeds should (almost always) produce different results."""
    chart1 = compute_geomancy_chart(seed_mode="manual", manual_seed=1)
    chart2 = compute_geomancy_chart(seed_mode="manual", manual_seed=99999)
    # At least one planet should be in a different house
    diffs = sum(
        1 for p1, p2 in zip(chart1.planet_placements, chart2.planet_placements)
        if p1.house != p2.house
    )
    assert diffs > 0 or chart1.ascendant_sign != chart2.ascendant_sign


def test_ascendant_sign_is_valid():
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=123)
    valid_signs = [s["en"] for s in ZODIAC_SIGNS]
    assert chart.ascendant_sign in valid_signs


def test_houses_use_consecutive_signs():
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=7)
    asc_idx = chart.ascendant_sign_num
    for i, house in enumerate(chart.houses):
        expected_idx = (asc_idx + i) % 12
        assert house.sign_num == expected_idx, (
            f"House {i+1}: expected sign index {expected_idx}, got {house.sign_num}"
        )


def test_time_seed_mode():
    """time_seed mode should produce a valid chart."""
    chart = compute_geomancy_chart(seed_mode="time_seed")
    assert isinstance(chart, GeomancyChart)
    assert chart.seed_mode == "time_seed"
    assert chart.seed > 0


def test_random_mode():
    chart = compute_geomancy_chart(seed_mode="random")
    assert isinstance(chart, GeomancyChart)
    assert chart.seed_mode == "random"


def test_to_json():
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=10)
    d = chart.to_json()
    assert "question" in d
    assert "houses" in d
    assert "planet_placements" in d
    assert len(d["houses"]) == 12
    assert len(d["planet_placements"]) == 9


# ─────────────────────────────────────────────────────────────────────────────
# Prompt formatting
# ─────────────────────────────────────────────────────────────────────────────

def test_format_prompt_zh():
    chart = compute_geomancy_chart(
        question="我今年財運如何",
        question_type="wealth",
        seed_mode="manual",
        manual_seed=42,
    )
    prompt = format_geomancy_for_prompt(chart, lang="zh")
    assert "地占占星" in prompt
    assert "我今年財運如何" in prompt
    assert "第1宮" in prompt
    assert "上升圖形" in prompt


def test_format_prompt_en():
    chart = compute_geomancy_chart(
        question="What is my fortune this year?",
        question_type="wealth",
        seed_mode="manual",
        manual_seed=42,
    )
    prompt = format_geomancy_for_prompt(chart, lang="en")
    assert "Astronomical Geomancy" in prompt
    assert "What is my fortune" in prompt
    assert "House 1" in prompt
    assert "Ascendant Figure" in prompt


# ─────────────────────────────────────────────────────────────────────────────
# Question types
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("qtype", [
    "life", "health", "wealth", "marriage", "career",
    "children", "journey", "religion", "enemy", "death", "custom",
])
def test_question_type_maps_to_primary_house(qtype):
    chart = compute_geomancy_chart(
        question_type=qtype,
        seed_mode="manual",
        manual_seed=1,
    )
    assert 1 <= chart.primary_house <= 12


def test_unknown_question_type_defaults_to_custom():
    chart = compute_geomancy_chart(
        question_type="nonexistent_type",
        seed_mode="manual",
        manual_seed=1,
    )
    # Should not raise, primary_house should be valid
    assert 1 <= chart.primary_house <= 12


# ─────────────────────────────────────────────────────────────────────────────
# Timestamp
# ─────────────────────────────────────────────────────────────────────────────

def test_chart_has_timestamp():
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=1)
    assert "UTC" in chart.timestamp
    assert len(chart.timestamp) > 10


# ─────────────────────────────────────────────────────────────────────────────
# geomancy_figures module
# ─────────────────────────────────────────────────────────────────────────────

from astro.astronomical_geomancy.geomancy_figures import (
    FIGURE_CATALOG,
    FIGURE_SVG_ROWS,
    get_figure_catalog,
    get_figure_svg_rows,
    CELL_W,
    CELL_H,
    X_SINGLE,
    X_DOUBLE,
)


def test_figure_catalog_has_16_entries():
    """FIGURE_CATALOG must cover all 16 geomantic figures."""
    catalog = get_figure_catalog()
    assert len(catalog) == 16


def test_figure_catalog_required_keys():
    """Every catalog entry must have latin, zh, wiki, omen_zh, omen_en, astrology_zh, astrology_en."""
    required = {"latin", "zh", "wiki", "omen_zh", "omen_en", "astrology_zh", "astrology_en"}
    for name, info in get_figure_catalog().items():
        missing = required - info.keys()
        assert not missing, f"Figure '{name}' catalog entry missing keys: {missing}"


def test_figure_svg_rows_has_16_entries():
    """FIGURE_SVG_ROWS must contain all 16 figures."""
    rows = get_figure_svg_rows()
    assert len(rows) == 16


def test_figure_svg_rows_geometry():
    """Each figure must have exactly 4 rows, each row having 1 or 2 x-positions."""
    for name, spec in get_figure_svg_rows().items():
        assert len(spec["rows_y"]) == 4, f"{name}: expected 4 rows_y"
        assert len(spec["rows_x"]) == 4, f"{name}: expected 4 rows_x"
        for xs in spec["rows_x"]:
            assert xs in (X_SINGLE, X_DOUBLE) or sorted(xs) in (
                sorted(X_SINGLE), sorted(X_DOUBLE)
            ), f"{name}: unexpected x positions {xs}"


def test_figure_svg_rows_matches_constants():
    """SVG rows derived from FIGURES must match dot patterns in FIGURES."""
    rows = get_figure_svg_rows()
    for key, data in FIGURES.items():
        name = data["name_en"]
        assert name in rows, f"Figure '{name}' missing from SVG rows"
        spec = rows[name]
        for row_idx, single in enumerate(data["dots"]):
            expected_xs = X_SINGLE if single else X_DOUBLE
            assert spec["rows_x"][row_idx] == expected_xs, (
                f"Figure '{name}' row {row_idx}: "
                f"expected {expected_xs}, got {spec['rows_x'][row_idx]}"
            )


def test_figure_catalog_names_match_constants():
    """All figure names in catalog must match name_en values in FIGURES."""
    constant_names = {data["name_en"] for data in FIGURES.values()}
    catalog_names = set(get_figure_catalog().keys())
    assert catalog_names == constant_names, (
        f"Catalog names differ from constants: "
        f"extra={catalog_names - constant_names}, "
        f"missing={constant_names - catalog_names}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Shield chain (calculator)
# ─────────────────────────────────────────────────────────────────────────────

import random as _random_module
from astro.astronomical_geomancy.calculator import (
    _build_shield_chain,
    _combine_figures,
    _compute_daughters,
    _make_figure,
    _make_figure_from_dots,
)


def test_build_shield_chain_structure():
    """Shield chain must return all expected keys with correct counts."""
    rng = _random_module.Random(42)
    mothers = [_generate_figure(rng) for _ in range(4)]
    chain = _build_shield_chain(mothers, rng)

    assert "daughters" in chain
    assert "nieces" in chain
    assert "witnesses" in chain
    assert "judge" in chain
    assert "reconciler" in chain
    assert "figures_16" in chain

    assert len(chain["daughters"]) == 4
    assert len(chain["nieces"]) == 4
    assert len(chain["witnesses"]) == 2
    assert isinstance(chain["judge"], GeomancyFigure)
    assert isinstance(chain["reconciler"], GeomancyFigure)
    assert len(chain["figures_16"]) == 16


def test_build_shield_chain_figures_16_layout():
    """figures_16 must be in row-major order: mothers, daughters, nieces, W/J/R."""
    rng = _random_module.Random(7)
    mothers = [_generate_figure(rng) for _ in range(4)]
    chain = _build_shield_chain(mothers, rng)

    figs = chain["figures_16"]
    # First 4 = mothers
    for i, m in enumerate(mothers):
        assert figs[i].name_en == m.name_en, f"figures_16[{i}] should be Mother {i+1}"
    # Daughters at indices 4-7
    for i, d in enumerate(chain["daughters"]):
        assert figs[4 + i].name_en == d.name_en
    # Nieces at indices 8-11
    for i, n in enumerate(chain["nieces"]):
        assert figs[8 + i].name_en == n.name_en
    # Witnesses at 12, 13
    assert figs[12].name_en == chain["witnesses"][0].name_en
    assert figs[13].name_en == chain["witnesses"][1].name_en
    # Judge at 14, Reconciler at 15
    assert figs[14].name_en == chain["judge"].name_en
    assert figs[15].name_en == chain["reconciler"].name_en


def test_daughters_transpose_mothers():
    """Daughter n row_k == Mother k row_n (transpose property)."""
    rng = _random_module.Random(99)
    mothers = [_generate_figure(rng) for _ in range(4)]
    daughters = _compute_daughters(mothers, rng)
    for d_idx, d in enumerate(daughters):
        for m_idx, m in enumerate(mothers):
            assert d.dots[m_idx] == m.dots[d_idx], (
                f"Daughter {d_idx} dot[{m_idx}] != Mother {m_idx} dot[{d_idx}]"
            )


def test_combine_figures_xor_rule():
    """Combining a figure with itself should yield Populus (all-double/even=False)."""
    rng = _random_module.Random(1)
    via = _make_figure("Via")        # [T,T,T,T]
    populus = _make_figure("Populus")  # [F,F,F,F]

    # Via XOR Via = [F,F,F,F] = Populus
    result = _combine_figures(via, via, rng)
    assert result.dots == [False, False, False, False]

    # Populus XOR Via = [T,T,T,T] = Via
    result2 = _combine_figures(populus, via, rng)
    assert result2.dots == [True, True, True, True]


def test_make_figure_from_dots_returns_valid_figure():
    rng = _random_module.Random(1)
    for key, data in FIGURES.items():
        fig = _make_figure_from_dots(list(data["dots"]), rng)
        assert isinstance(fig, GeomancyFigure)
        assert fig.dots == list(data["dots"])


def test_build_shield_chain_all_valid_figures():
    """All 16 figures in shield chain must be valid GeomancyFigure instances."""
    rng = _random_module.Random(123)
    mothers = [_generate_figure(rng) for _ in range(4)]
    chain = _build_shield_chain(mothers, rng)
    for fig in chain["figures_16"]:
        assert isinstance(fig, GeomancyFigure)
        assert len(fig.dots) == 4
        assert all(isinstance(d, bool) for d in fig.dots)


# ─────────────────────────────────────────────────────────────────────────────
# compute_geomancy_chart — new fields
# ─────────────────────────────────────────────────────────────────────────────

def test_compute_with_mode_and_layout():
    """Chart must carry mode and layout fields."""
    chart = compute_geomancy_chart(
        seed_mode="manual", manual_seed=5,
        mode="horary", layout="square",
    )
    assert chart.mode == "horary"
    assert chart.layout == "square"


def test_compute_figures_16_has_16_entries():
    """figures_16 must have exactly 16 GeomancyFigure entries."""
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=77)
    assert len(chart.figures_16) == 16
    for fig in chart.figures_16:
        assert isinstance(fig, GeomancyFigure)


def test_compute_judge_and_reconciler_populated():
    """judge and reconciler must be set after computation."""
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=10)
    assert isinstance(chart.judge, GeomancyFigure)
    assert isinstance(chart.reconciler, GeomancyFigure)


def test_compute_summary_text_from_question():
    """summary_text must incorporate (part of) the question."""
    q = "我今年事業如何"
    chart = compute_geomancy_chart(
        question=q, seed_mode="manual", manual_seed=1
    )
    assert q in chart.summary_text or chart.summary_text.startswith(q[:10])


def test_compute_figures_16_all_valid_names():
    """All figures in figures_16 must have name_en present in FIGURES."""
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=33)
    known_names = {data["name_en"] for data in FIGURES.values()}
    for fig in chart.figures_16:
        assert fig.name_en in known_names, f"Unknown figure name: {fig.name_en}"


def test_compute_layout_defaults_to_square():
    """Default layout must be 'square'."""
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=1)
    assert chart.layout == "square"


def test_compute_mode_defaults_to_horary():
    """Default mode must be 'horary'."""
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=1)
    assert chart.mode == "horary"


# ─────────────────────────────────────────────────────────────────────────────
# chart_renderer_geomancy SVG builder
# ─────────────────────────────────────────────────────────────────────────────

from astro.astronomical_geomancy.chart_renderer_geomancy import (
    build_square_chart_svg,
    get_theme,
)


def test_build_square_chart_svg_returns_svg():
    """SVG output must start with <svg and end with </svg>."""
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=1)
    fig_names = [f.name_en for f in chart.figures_16]
    svg = build_square_chart_svg(fig_names, center_text="test", theme="parchment")
    assert svg.strip().startswith("<svg"), "SVG must start with <svg"
    assert svg.strip().endswith("</svg>"), "SVG must end with </svg>"


def test_build_square_chart_svg_both_themes():
    """Both parchment and dark themes must produce valid SVG without errors."""
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=42)
    fig_names = [f.name_en for f in chart.figures_16]
    for theme in ("parchment", "dark"):
        svg = build_square_chart_svg(fig_names, theme=theme)
        assert "<svg" in svg, f"Theme '{theme}' did not produce SVG"


def test_build_square_chart_svg_both_langs():
    """Both zh and en lang settings must produce valid SVG."""
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=5)
    fig_names = [f.name_en for f in chart.figures_16]
    for lang in ("zh", "en"):
        svg = build_square_chart_svg(fig_names, lang=lang)
        assert "<svg" in svg, f"Lang '{lang}' did not produce SVG"


def test_build_square_chart_svg_contains_all_figures():
    """SVG must contain the Latin name of every rendered figure."""
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=11)
    fig_names = [f.name_en for f in chart.figures_16]
    svg = build_square_chart_svg(fig_names)
    for name in fig_names:
        catalog = get_figure_catalog()
        latin = catalog.get(name, {}).get("latin", name)
        assert latin in svg, f"Latin name '{latin}' missing from SVG"


def test_build_square_chart_svg_center_text():
    """A supplied center_text must appear in the SVG."""
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=2)
    fig_names = [f.name_en for f in chart.figures_16]
    center = "Testing centre"
    svg = build_square_chart_svg(fig_names, center_text=center)
    assert center in svg


def test_build_square_chart_svg_zodiac_and_planets():
    """SVG must include zodiac and planet glyphs."""
    chart = compute_geomancy_chart(seed_mode="manual", manual_seed=3)
    fig_names = [f.name_en for f in chart.figures_16]
    svg = build_square_chart_svg(fig_names)
    assert "♈" in svg, "SVG missing zodiac glyph ♈"
    assert "☉" in svg, "SVG missing planet glyph ☉"


def test_get_theme_fallback():
    """Unknown theme name must fall back to parchment."""
    t = get_theme("unknown_theme")
    parchment = get_theme("parchment")
    assert t == parchment


# ─────────────────────────────────────────────────────────────────────────────
# models — new enums and dataclasses
# ─────────────────────────────────────────────────────────────────────────────

from astro.astronomical_geomancy.models import (
    GeomancyMode,
    GeomancyLayout,
    FigureMeaning,
)


def test_geomancy_mode_values():
    assert GeomancyMode.horary == "horary"
    assert GeomancyMode.natal_transcode == "natal_transcode"


def test_geomancy_layout_values():
    assert GeomancyLayout.square == "square"
    assert GeomancyLayout.shield == "shield"


def test_figure_meaning_dataclass():
    fm = FigureMeaning(
        latin="Via",
        zh="道路",
        en="Road",
        astrology="Leo / Moon",
        omen_zh="中。流動變化。",
        wiki_url="/wiki/via",
    )
    assert fm.latin == "Via"
    assert fm.zh == "道路"
