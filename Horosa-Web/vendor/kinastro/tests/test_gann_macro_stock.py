from datetime import date, datetime

import pytest

from astro.qizheng.financial.gann_macro_stock import (
    build_gann_macro_timing,
    compute_anniversary_dates,
    compute_biblical_cycle_dates,
    find_nearest_square_of_nine_levels,
    compute_square_of_nine_levels,
    evaluate_qizheng_resonance,
    scale_cycle_to_days,
    compute_time_price_squaring,
    compute_gann_angles,
    get_gann_angle_at_date,
    compute_natural_squares_vibration,
    compute_solar_ingress_gann_confluence,
    build_gann_full_confluence,
)


def test_scale_cycle_to_days_basic():
    days = scale_cycle_to_days(3.5, scale=1.0, year_basis_days=360.0)
    assert days == int(round(3.5 * 360.0 * 1.0))  # 3.5 年 × 360 天 = 1260


def test_compute_biblical_cycle_dates_includes_scaled_day_for_year():
    rows = compute_biblical_cycle_dates(
        anchor_date=date(2020, 1, 1),
        as_of_date=date(2020, 2, 10),
        scale=0.1,
        year_basis_days=365.0,
        lookback_years=1.0,
        lookahead_years=1.0,
        max_multiple=3,
    )
    assert rows
    assert any(r["cycle_key"] == "day_for_year" for r in rows)


def test_evaluate_qizheng_resonance_scores():
    natal = {"木星": 10.0, "土星": 20.0}
    transit = {"木星": 10.5, "土星": 110.0}
    rows = evaluate_qizheng_resonance(natal, transit, orb=3.0)
    assert len(rows) == 2
    jupiter = next(r for r in rows if r["star"] == "木星")
    saturn = next(r for r in rows if r["star"] == "土星")
    assert jupiter["aspect"] == "合"
    assert jupiter["score"] == 3
    assert saturn["aspect"] == "刑"
    assert saturn["score"] == -2


def test_build_gann_macro_timing_with_injected_maps():
    result = build_gann_macro_timing(
        market_natal_date=date(2020, 1, 1),
        as_of_datetime=datetime(2020, 2, 10, 12, 0),
        timezone=8.0,
        cycle_scale=0.1,
        cycle_orb_days=30,
        natal_longitudes={"木星": 10.0, "土星": 20.0},
        transit_longitudes={"木星": 10.2, "土星": 20.0},
    )
    assert "scores" in result
    assert result["scores"]["total_score"] > 0
    assert result["near_cycle_hits"]


def test_compute_square_of_nine_levels():
    levels = compute_square_of_nine_levels(reference_price=100.0, max_ring=1)
    assert len(levels) == 16
    assert levels[0]["target_price"] > 0
    assert any(row["angle"] == 45 for row in levels)


def test_compute_square_of_nine_levels_invalid():
    with pytest.raises(ValueError):
        compute_square_of_nine_levels(reference_price=0.0)


def test_compute_square_of_nine_levels_descending_and_step():
    levels = compute_square_of_nine_levels(
        reference_price=100.0,
        max_ring=1,
        angle_step=90,
        include_descending=True,
    )
    assert levels
    assert any(row["direction"] == "down" for row in levels)
    assert any(row["angle"] == 270 for row in levels)


def test_compute_square_of_nine_levels_cardinal_current_price():
    levels = compute_square_of_nine_levels(
        reference_price=100.0,
        current_price=121.0,
        max_ring=1,
        angle_step=45,
        angle_system="cardinal",
        include_descending=True,
    )
    assert levels
    assert all(row["angle"] in {0, 90, 180, 270} for row in levels)
    assert any(row["direction"] == "up" for row in levels)
    assert any(row["direction"] == "down" for row in levels)
    assert all("turn" in row for row in levels)


def test_find_nearest_square_of_nine_levels():
    result = find_nearest_square_of_nine_levels(current_price=123.0, reference_price=100.0, max_ring=2)
    assert result["nearest_level"] is not None
    assert result["support_level"]["target_price"] <= 123.0
    assert result["resistance_level"]["target_price"] >= 123.0
    assert result["distance_to_nearest"] >= 0


def test_compute_anniversary_dates_basic():
    rows = compute_anniversary_dates(
        anchor_date=date(2020, 1, 1),
        as_of_date=date(2022, 1, 1),
        lookback_years=1.0,
        lookahead_years=1.0,
        monthly_step=6,
    )
    assert rows
    assert any(x["type"] == "yearly_anniversary" for x in rows)
    assert any(x["type"] == "monthly_anniversary" for x in rows)


def test_compute_anniversary_dates_supports_multiple_anchors_and_day_windows():
    rows = compute_anniversary_dates(
        anchor_date=date(2020, 1, 1),
        anchor_dates=[date(2020, 1, 1), date(2020, 3, 1)],
        as_of_date=date(2020, 5, 30),
        lookback_years=0.5,
        lookahead_years=0.5,
        monthly_step=3,
    )
    assert any(row["type"] == "gann_day_window" and row["base_days"] == 45 for row in rows)
    assert any(row["anchor_date"] == "2020-03-01" for row in rows)
    assert any(row["gann_harmonic"] == "1/4年" for row in rows if row["base_days"] in {90, 91, 92})


def test_compute_anniversary_dates_trading_day_alignment():
    rows = compute_anniversary_dates(
        anchor_date=date(2020, 1, 31),
        as_of_date=date(2020, 4, 30),
        lookback_years=0.5,
        lookahead_years=0.5,
        monthly_step=1,
        use_trading_days=True,
        include_day_windows=False,
    )
    monthly = next(row for row in rows if row["type"] == "monthly_anniversary")
    assert monthly["use_trading_days"] is True
    assert date.fromisoformat(monthly["due_date"]).weekday() < 5


def test_build_gann_macro_timing_contains_anniversary_scores():
    result = build_gann_macro_timing(
        market_natal_date=date(2020, 1, 1),
        as_of_datetime=datetime(2020, 2, 10, 12, 0),
        timezone=8.0,
        cycle_scale=0.1,
        cycle_orb_days=30,
        natal_longitudes={"木星": 10.0, "土星": 20.0},
        transit_longitudes={"木星": 10.2, "土星": 20.0},
    )
    assert "anniversary_hits" in result
    assert "anniversary_score" in result["scores"]


def test_build_gann_macro_timing_coerces_mixed_score_types(monkeypatch):
    from astro.qizheng.financial import gann_macro_stock as gms

    monkeypatch.setattr(gms, "compute_biblical_cycle_dates", lambda *args, **kwargs: [])
    monkeypatch.setattr(gms, "compute_anniversary_dates", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        gms,
        "evaluate_qizheng_resonance",
        lambda *args, **kwargs: [
            {"score": "3"},
            {"score": -1},
            {"score": "-2"},
            {"score": "invalid"},
            {"score": 0},
        ],
    )

    result = build_gann_macro_timing(
        market_natal_date=date(2020, 1, 1),
        as_of_datetime=datetime(2020, 2, 10, 12, 0),
        natal_longitudes={"木星": 10.0},
        transit_longitudes={"木星": 10.2},
    )

    assert result["scores"]["astro_score"] == 0
    assert result["scores"]["total_score"] == 0
    assert result["scores"]["positive_aspect_count"] == 1
    assert result["scores"]["negative_aspect_count"] == 2


# ============================================================
# 新增函數測試（Time-Price Squaring, Gann Fan, Natural Squares,
# Solar Ingress, Full Confluence）
# ============================================================

def test_compute_time_price_squaring_basic():
    results = compute_time_price_squaring(
        anchor_price=100.0,
        anchor_date=date(2020, 1, 1),
        as_of_date=date(2020, 6, 1),
        lookahead_days=365,
        orb_days=10,
    )
    assert isinstance(results, list)
    # 應有未來的共振點
    future = [r for r in results if r["distance_days"] >= 0]
    assert future
    # 每筆都有必要欄位
    for r in results:
        assert "resonant_date" in r
        assert "resonant_price" in r
        assert "strength" in r
        assert "in_orb" in r
        assert r["resonant_price"] > 0


def test_compute_time_price_squaring_invalid():
    with pytest.raises(ValueError):
        compute_time_price_squaring(
            anchor_price=0.0,
            anchor_date=date(2020, 1, 1),
            as_of_date=date(2020, 6, 1),
        )


def test_compute_time_price_squaring_primary_strength():
    results = compute_time_price_squaring(
        anchor_price=100.0,
        anchor_date=date(2020, 1, 1),
        as_of_date=date(2020, 6, 1),
        lookahead_days=730,
        orb_days=5,
    )
    primary = [r for r in results if r["strength"] == "主要共振"]
    secondary = [r for r in results if "次要" in r["strength"]]
    assert primary or secondary  # 至少有一種


def test_compute_gann_angles_basic():
    results = compute_gann_angles(
        pivot_price=100.0,
        pivot_date=date(2020, 1, 1),
        as_of_date=date(2020, 6, 1),
        lookahead_days=180,
        trend="up",
    )
    assert isinstance(results, list)
    assert results
    angle_names = {r["angle"] for r in results}
    assert "1×1" in angle_names
    assert "2×1" in angle_names
    # 所有價格都為正
    for r in results:
        assert r["price_target"] > 0


def test_compute_gann_angles_down_trend():
    results = compute_gann_angles(
        pivot_price=200.0,
        pivot_date=date(2020, 1, 1),
        as_of_date=date(2020, 3, 1),
        lookahead_days=180,
        trend="down",
    )
    assert results
    # 下跌趨勢：未來價格應低於樞紐
    future_1x1 = [r for r in results if r["angle"] == "1×1" and r["days_from_now"] > 0]
    if future_1x1:
        assert future_1x1[0]["price_target"] < 200.0


def test_compute_gann_angles_invalid():
    with pytest.raises(ValueError):
        compute_gann_angles(
            pivot_price=-10.0,
            pivot_date=date(2020, 1, 1),
            as_of_date=date(2020, 6, 1),
        )
    with pytest.raises(ValueError):
        compute_gann_angles(
            pivot_price=100.0,
            pivot_date=date(2020, 1, 1),
            as_of_date=date(2020, 6, 1),
            trend="sideways",
        )


def test_get_gann_angle_at_date():
    angles = get_gann_angle_at_date(
        pivot_price=100.0,
        pivot_date=date(2020, 1, 1),
        target_date=date(2020, 4, 10),
        trend="up",
    )
    assert isinstance(angles, dict)
    assert "1×1" in angles
    assert angles["1×1"] > 100.0  # 上升趨勢


def test_compute_natural_squares_vibration_basic():
    result = compute_natural_squares_vibration(
        reference_price=100.0,
        num_squares=10,
    )
    assert "natural_squares" in result
    assert "vibration_level" in result
    assert "cross_levels" in result
    assert "octagon_levels" in result
    squares = result["natural_squares"]
    assert len(squares) == 10
    assert squares[0]["n"] == 1
    assert squares[0]["square"] == 1.0
    assert squares[9]["n"] == 10
    assert squares[9]["square"] == 100.0


def test_compute_natural_squares_vibration_current_price():
    result = compute_natural_squares_vibration(
        reference_price=100.0,
        num_squares=15,
        current_price=99.5,
        proximity_pct=0.02,
    )
    # 99.5 在 100 附近（10²=100），應找到最近節點
    nearest = result.get("nearest_natural_square")
    assert nearest is not None
    assert nearest["n"] == 10


def test_compute_natural_squares_vibration_invalid():
    with pytest.raises(ValueError):
        compute_natural_squares_vibration(reference_price=0.0)


def test_compute_solar_ingress_gann_confluence_basic():
    results = compute_solar_ingress_gann_confluence(
        market_natal_date=date(1969, 11, 24),
        year=2024,
        cycle_scale=0.1,
        cycle_orb_days=15,
    )
    assert isinstance(results, list)
    # 應有 4 個節氣
    assert len(results) == 4
    ingress_names = {r["ingress_name"] for r in results}
    assert any("春分" in n for n in ingress_names)
    assert any("夏至" in n for n in ingress_names)
    # 每筆都有評分
    for r in results:
        assert "total_score" in r
        assert "ingress_date" in r
        assert "confluence" in r
        assert r["total_score"] >= 0


def test_build_gann_full_confluence_basic():
    result = build_gann_full_confluence(
        market_natal_date=date(1969, 11, 24),
        as_of_datetime=datetime(2024, 3, 20, 12, 0),
        current_price=16000.0,
        reference_price=16000.0,
        timezone=8.0,
        cycle_scale=0.1,
        use_trading_days=False,
        cycle_orb_days=15,
        natal_longitudes={"木星": 10.0, "土星": 20.0},
        transit_longitudes={"木星": 10.5, "土星": 110.0},
    )
    assert "confluence_scores" in result
    cs = result["confluence_scores"]
    assert "total_confluence_score" in cs
    assert "classification" in cs
    assert "biblical_cycle_score" in cs
    assert "time_price_squaring_score" in cs
    assert "solar_ingress_score" in cs
    assert "natural_square_score" in cs
    assert "time_price_squaring" in result
    assert "solar_ingress_confluence" in result
    assert "natural_squares_vibration" in result


def test_build_gann_full_confluence_with_pivot():
    result = build_gann_full_confluence(
        market_natal_date=date(1969, 11, 24),
        as_of_datetime=datetime(2024, 3, 20, 12, 0),
        current_price=16000.0,
        pivot_price=14000.0,
        pivot_date=date(2023, 10, 1),
        trend="up",
        cycle_scale=0.1,
        natal_longitudes={"木星": 10.0},
        transit_longitudes={"木星": 10.5},
    )
    assert "confluence_scores" in result
    assert result["trend"] == "up"
