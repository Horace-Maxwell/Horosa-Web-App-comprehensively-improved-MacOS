import importlib.util
import sys
import types
from pathlib import Path

import pytest


@pytest.fixture
def financial_modules():
    fake_st = types.ModuleType("streamlit")
    fake_st.markdown = lambda *args, **kwargs: None
    sys.modules["streamlit"] = fake_st

    package_roots = [
        ("astro", Path(__file__).resolve().parents[1] / "astro"),
        ("astro.qizheng", Path(__file__).resolve().parents[1] / "astro" / "qizheng"),
        (
            "astro.qizheng.financial",
            Path(__file__).resolve().parents[1] / "astro" / "qizheng" / "financial",
        ),
    ]
    for package_name, package_path in package_roots:
        package = types.ModuleType(package_name)
        package.__path__ = [str(package_path)]
        sys.modules[package_name] = package

    loaded_modules = {}
    for module_name, file_name in (
        ("astro.qizheng.financial.name_wuxing", "name_wuxing.py"),
        ("astro.qizheng.financial.stock_renderer", "stock_renderer.py"),
    ):
        file_path = (
            Path(__file__).resolve().parents[1]
            / "astro"
            / "qizheng"
            / "financial"
            / file_name
        )
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        loaded_modules[module_name] = module

    yield loaded_modules

    for module_name in (
        "streamlit",
        "astro",
        "astro.qizheng",
        "astro.qizheng.financial",
        "astro.qizheng.financial.name_wuxing",
        "astro.qizheng.financial.stock_renderer",
    ):
        sys.modules.pop(module_name, None)


def test_merge_wuxing_distributions_sums_each_element(financial_modules):
    stock_renderer = financial_modules["astro.qizheng.financial.stock_renderer"]

    merged = stock_renderer._merge_wuxing_distributions(
        {"木": 2, "火": 1, "土": 0, "金": 0, "水": 0},
        {"木": 0, "火": 0, "土": 1, "金": 2, "水": 1},
    )

    assert merged == {"木": 2, "火": 1, "土": 1, "金": 2, "水": 1}


def test_composite_compatibility_grade_with_merged_distributions(financial_modules):
    name_wuxing = financial_modules["astro.qizheng.financial.name_wuxing"]
    stock_renderer = financial_modules["astro.qizheng.financial.stock_renderer"]

    personal_distribution = {"木": 3, "火": 0, "土": 0, "金": 0, "水": 0}
    combined_stock_distribution = stock_renderer._merge_wuxing_distributions(
        {"木": 0, "火": 0, "土": 0, "金": 0, "水": 1},
        {"木": 0, "火": 0, "土": 0, "金": 0, "水": 2},
    )

    comparison = name_wuxing.compare_wuxing(
        personal_distribution,
        "命主",
        combined_stock_distribution,
        "股票綜合能量",
    )
    grade = stock_renderer._compatibility_grade(
        comparison,
        personal_distribution,
        combined_stock_distribution,
        day_master_element="木",
        user_profile_note="身旺",
    )

    assert comparison["relationship_code"] == "stock_feeds_you"
    assert comparison["dominant_b"] == "水"
    assert grade == {
        "grade": "S",
        "title_zh": "絕對配合",
        "title_en": "Absolute Match",
        "score_value": "100.0",
        "fit_note_zh": "對用戶木日元身旺：喜用比重 100%，忌神壓力 0%。",
        "advice_zh": "推薦買賣建議：可分批布局／偏買進。",
    }


def test_weak_fire_profile_heavily_penalises_metal_water(financial_modules):
    stock_renderer = financial_modules["astro.qizheng.financial.stock_renderer"]

    comparison = {
        "score": -2,
        "relationship_code": "stock_overcomes_you",
    }
    personal_distribution = {"木": 1, "火": 1, "土": 1, "金": 2, "水": 2}
    stock_distribution = {"木": 0.0, "火": 0.0, "土": 0.5, "金": 2.5, "水": 2.5}

    grade = stock_renderer._compatibility_grade(
        comparison,
        personal_distribution,
        stock_distribution,
        day_master_element="火",
        numerology_score=-2.0,
        user_profile_note="身弱",
    )

    assert grade["grade"] == "F"
    assert "身弱" in grade["fit_note_zh"]
    assert "迴避或嚴格止損" in grade["advice_zh"]


def test_weak_fire_profile_rewards_wood_fire_setup(financial_modules):
    stock_renderer = financial_modules["astro.qizheng.financial.stock_renderer"]

    comparison = {
        "score": 2,
        "relationship_code": "stock_feeds_you",
    }
    personal_distribution = {"木": 2, "火": 1, "土": 1, "金": 1, "水": 1}
    stock_distribution = {"木": 2.4, "火": 3.1, "土": 0.5, "金": 0.2, "水": 0.1}

    grade = stock_renderer._compatibility_grade(
        comparison,
        personal_distribution,
        stock_distribution,
        day_master_element="火",
        numerology_score=3.0,
        user_profile_note="身弱",
    )

    assert grade["grade"] in {"A", "S"}
    assert "偏買進" in grade["advice_zh"]


def test_compare_wuxing_accepts_string_distribution_values(financial_modules):
    name_wuxing = financial_modules["astro.qizheng.financial.name_wuxing"]

    comparison = name_wuxing.compare_wuxing(
        {"木": "3", "火": "0", "土": "0", "金": "0", "水": "0"},
        "命主",
        {"木": "0", "火": "0", "土": "0", "金": "0", "水": "2"},
        "股票綜合能量",
    )

    assert comparison["relationship_code"] == "stock_feeds_you"


def test_compatibility_grade_accepts_string_distribution_values(financial_modules):
    stock_renderer = financial_modules["astro.qizheng.financial.stock_renderer"]

    grade = stock_renderer._compatibility_grade(
        {"score": "2", "relationship_code": "stock_feeds_you"},
        {"木": "3", "火": "0", "土": "0", "金": "0", "水": "0"},
        {"木": "0.0", "火": "0.0", "土": "0.0", "金": "0.0", "水": "2.0"},
        day_master_element="木",
        user_profile_note="身旺",
    )

    assert grade["grade"] in {"A", "S"}


def test_price_forecast_profile_detects_bullish_regime(financial_modules):
    stock_renderer = financial_modules["astro.qizheng.financial.stock_renderer"]

    forecast = stock_renderer._build_price_forecast_profile(
        current=120.0,
        high=150.0,
        low=90.0,
        ratio=78.0,
        total_score=8,
        gann_context={
            "near_cycle_hits": [{}, {}],
            "scores": {
                "total_score": 7,
                "classification": "高共振",
                "positive_aspect_count": 3,
                "negative_aspect_count": 0,
            },
        },
    )

    prices = [row["price"] for row in forecast["targets"]]
    assert forecast["regime_key"] == "bullish"
    assert forecast["regime_zh"] == "上行趨勢"
    assert prices == sorted(prices)
    assert prices[-1] > 120.0


def test_price_forecast_profile_detects_bearish_regime(financial_modules):
    stock_renderer = financial_modules["astro.qizheng.financial.stock_renderer"]

    forecast = stock_renderer._build_price_forecast_profile(
        current=80.0,
        high=110.0,
        low=70.0,
        ratio=22.0,
        total_score=-9,
        gann_context={
            "near_cycle_hits": [{}],
            "scores": {
                "total_score": -6,
                "classification": "低共振",
                "positive_aspect_count": 0,
                "negative_aspect_count": 3,
            },
        },
    )

    prices = [row["price"] for row in forecast["targets"]]
    assert forecast["regime_key"] == "bearish"
    assert forecast["regime_zh"] == "下行趨勢"
    assert prices == sorted(prices, reverse=True)
    assert prices[-1] < 80.0


def test_price_forecast_profile_detects_sideways_regime(financial_modules):
    stock_renderer = financial_modules["astro.qizheng.financial.stock_renderer"]

    forecast = stock_renderer._build_price_forecast_profile(
        current=100.0,
        high=108.0,
        low=92.0,
        ratio=51.0,
        total_score=1,
        gann_context={
            "near_cycle_hits": [],
            "scores": {
                "total_score": 0,
                "classification": "弱共振",
                "positive_aspect_count": 1,
                "negative_aspect_count": 1,
            },
        },
    )

    prices = [row["price"] for row in forecast["targets"]]
    assert forecast["regime_key"] == "sideways"
    assert forecast["regime_zh"] == "橫行整理"
    assert any(price > 100.0 for price in prices)
    assert any(price < 100.0 for price in prices)
