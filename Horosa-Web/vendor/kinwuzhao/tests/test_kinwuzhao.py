# -*- coding: utf-8 -*-
"""五兆核心揲筮函數與類別的綜合測試。

涵蓋 FiveElementsMapper、SixBeastsArranger、WuzhaoCalculator、
GuxuJudge、InterpretationEngine、WuzhaoDivination 以及
向後相容的 five_zhao_paipan、gangzhi_paipan 函數。
"""

from __future__ import annotations

import pytest

import config
import jieqi
import kinwuzhao
from kinwuzhao import (
    FiveElementsMapper,
    GuxuJudge,
    InterpretationEngine,
    SixBeastsArranger,
    WuzhaoCalculator,
    WuzhaoDivination,
)


# ---------------------------------------------------------------------------
# FiveElementsMapper
# ---------------------------------------------------------------------------

class TestFiveElementsMapper:
    """五行對映與六親關係。"""

    @pytest.mark.parametrize(
        "num, expected",
        [(1, "水"), (2, "火"), (3, "木"), (4, "金"), (5, "土")],
    )
    def test_element_for(self, num: int, expected: str) -> None:
        assert FiveElementsMapper.element_for(num) == expected

    def test_element_for_invalid(self) -> None:
        with pytest.raises(KeyError):
            FiveElementsMapper.element_for(0)

    def test_relation_same(self) -> None:
        assert FiveElementsMapper.relation("水", "水") == "兄弟"

    def test_relation_different(self) -> None:
        # 水生木 → 子孫
        result = FiveElementsMapper.relation("水", "木")
        assert result in ("子孫", "父母", "官鬼", "妻財", "兄弟")


# ---------------------------------------------------------------------------
# SixBeastsArranger
# ---------------------------------------------------------------------------

class TestSixBeastsArranger:
    """六獸排列。"""

    def test_arrange_jia(self) -> None:
        seq = SixBeastsArranger.arrange("甲")
        assert len(seq) == 6
        assert seq[0] == "青龍"

    def test_arrange_ren(self) -> None:
        seq = SixBeastsArranger.arrange("壬")
        assert seq[0] == "玄武"

    def test_arrange_invalid(self) -> None:
        with pytest.raises(ValueError):
            SixBeastsArranger.arrange("X")

    def test_check_death(self) -> None:
        # 青龍死在坤宮
        assert SixBeastsArranger.check_death("青龍", "坤") == "死"
        assert SixBeastsArranger.check_death("青龍", "震") == ""

    def test_check_harm(self) -> None:
        # 青龍害在兌宮
        assert SixBeastsArranger.check_harm("青龍", "兌") == "害"
        assert SixBeastsArranger.check_harm("青龍", "震") == ""


# ---------------------------------------------------------------------------
# WuzhaoCalculator
# ---------------------------------------------------------------------------

class TestWuzhaoCalculator:
    """揲筮計算核心。"""

    def test_mod5_nonzero(self) -> None:
        assert WuzhaoCalculator._mod5_nonzero(5) == 5
        assert WuzhaoCalculator._mod5_nonzero(10) == 5
        assert WuzhaoCalculator._mod5_nonzero(7) == 2
        assert WuzhaoCalculator._mod5_nonzero(1) == 1

    def test_random_split_range(self) -> None:
        for _ in range(100):
            result = WuzhaoCalculator.random_split(10)
            assert 1 <= result <= 9

    def test_random_split_minimum(self) -> None:
        assert WuzhaoCalculator.random_split(1) == 1

    def test_tang_shi_divination_length(self) -> None:
        results = WuzhaoCalculator.tang_shi_divination()
        assert len(results) == 6
        assert all(1 <= r <= 5 for r in results)

    def test_tang_shi_divination_manual(self) -> None:
        results = WuzhaoCalculator.tang_shi_divination(
            manual_splits=[7, 6, 5, 4, 3, 2]
        )
        assert len(results) == 6
        # 7 % 5 = 2
        assert results[0] == 2

    def test_gangzhi_calculation(self) -> None:
        jz2num = dict(zip(config.jiazi(), range(1, 61)))
        # 甲子 = 1, mod 5 = 1
        result = WuzhaoCalculator.gangzhi_calculation(["甲子"], jz2num)
        assert result == 1


# ---------------------------------------------------------------------------
# GuxuJudge
# ---------------------------------------------------------------------------

class TestGuxuJudge:
    """孤虛判斷。"""

    def test_judge_returns_two(self) -> None:
        gu, xu = GuxuJudge.judge("甲子")
        assert isinstance(gu, str)
        assert isinstance(xu, str)


# ---------------------------------------------------------------------------
# InterpretationEngine
# ---------------------------------------------------------------------------

class TestInterpretationEngine:
    """排盤結果組裝。"""

    def test_positions_count(self) -> None:
        assert len(InterpretationEngine.POSITIONS) == 6

    def test_get_wangxiang(self) -> None:
        result = InterpretationEngine.get_wangxiang("夏至", "離")
        assert result != ""


# ---------------------------------------------------------------------------
# five_zhao_paipan (宋代簡化)
# ---------------------------------------------------------------------------

class TestFiveZhaoPaipan:
    """五兆排盤（宋代折竹法）。"""

    @pytest.fixture()
    def test_params(self) -> dict:
        gz = config.gangzhi(2025, 6, 27, 11, 24)
        jq_val = jieqi.jq(2025, 6, 27, 11, 24)
        cm = config.lunar_date_d(2025, 6, 27)["農曆月"][0]
        return {"gz": gz, "jq": jq_val, "cm": cm}

    def test_always_six_positions(self, test_params: dict) -> None:
        gz, jq_val, cm = test_params["gz"], test_params["jq"], test_params["cm"]
        for _ in range(50):
            result = kinwuzhao.five_zhao_paipan(0, jq_val, cm, gz[1], gz[2])
            assert len(result) == 6, f"Only {len(result)} positions"

    def test_zhao_position_present(self, test_params: dict) -> None:
        gz, jq_val, cm = test_params["gz"], test_params["jq"], test_params["cm"]
        result = kinwuzhao.five_zhao_paipan(0, jq_val, cm, gz[1], gz[2])
        assert "兆" in result
        assert result["兆"]["宮位"] == "兆"

    def test_invalid_day_gan(self, test_params: dict) -> None:
        jq_val, cm = test_params["jq"], test_params["cm"]
        result = kinwuzhao.five_zhao_paipan(0, jq_val, cm, "X午", "丁卯")
        assert "錯誤" in result

    def test_manual_splits(self, test_params: dict) -> None:
        gz, jq_val, cm = test_params["gz"], test_params["jq"], test_params["cm"]
        result = kinwuzhao.five_zhao_paipan(
            0, jq_val, cm, gz[1], gz[2],
            manual_splits=[7, 6, 5, 4, 3, 2],
        )
        assert len(result) == 6
        assert result["兆"]["數字"] == 2  # 7 % 5 = 2


# ---------------------------------------------------------------------------
# gangzhi_paipan (干支法)
# ---------------------------------------------------------------------------

class TestGangzhiPaipan:
    """干支起盤。"""

    def test_basic(self) -> None:
        gz = config.gangzhi(2025, 6, 27, 11, 24)
        jq_val = jieqi.jq(2025, 6, 27, 11, 24)
        cm = config.lunar_date_d(2025, 6, 27)["農曆月"][0]
        result = kinwuzhao.gangzhi_paipan(gz, 0, jq_val, cm)
        assert len(result) == 6
        assert "兆" in result

    def test_insufficient_gangzhi(self) -> None:
        result = kinwuzhao.gangzhi_paipan(["甲子", "乙丑"], 0, "夏至", "六")
        assert "錯誤" in result


# ---------------------------------------------------------------------------
# WuzhaoDivination (唐代正法)
# ---------------------------------------------------------------------------

class TestWuzhaoDivination:
    """唐代正法揲筮。"""

    def test_basic(self) -> None:
        gz = config.gangzhi(2025, 6, 27, 11, 24)
        jq_val = jieqi.jq(2025, 6, 27, 11, 24)
        cm = config.lunar_date_d(2025, 6, 27)["農曆月"][0]
        div = WuzhaoDivination(jq=jq_val, cm=cm, gz1=gz[1], gz2=gz[2])
        result = div.divine()
        assert len(result) == 6
        for label in ["兆", "木鄉", "火鄉", "土鄉", "金鄉", "水鄉"]:
            assert label in result
            assert 1 <= result[label]["數字"] <= 5

    def test_manual_splits(self) -> None:
        gz = config.gangzhi(2025, 6, 27, 11, 24)
        jq_val = jieqi.jq(2025, 6, 27, 11, 24)
        cm = config.lunar_date_d(2025, 6, 27)["農曆月"][0]
        div = WuzhaoDivination(
            jq=jq_val, cm=cm, gz1=gz[1], gz2=gz[2],
            manual_splits=[7, 6, 5, 4, 3, 2],
        )
        result = div.divine()
        assert len(result) == 6


# ---------------------------------------------------------------------------
# jieqi boundary tests
# ---------------------------------------------------------------------------

class TestJieqi:
    """節氣邊界處理。"""

    def test_always_returns_value(self) -> None:
        """節氣函數不應返回 None。"""
        test_cases = [
            (2025, 1, 1, 0, 0),
            (2025, 3, 20, 12, 0),
            (2025, 6, 21, 0, 0),
            (2025, 9, 23, 12, 0),
            (2025, 12, 21, 18, 0),
        ]
        for args in test_cases:
            result = jieqi.jq(*args)
            assert result is not None, f"jq{args} returned None"

    def test_known_jieqi(self) -> None:
        """已知日期的節氣驗證。"""
        # 2025-06-27 在夏至之後
        assert jieqi.jq(2025, 6, 27, 11, 24) == "夏至"

    def test_find_season(self) -> None:
        assert jieqi.find_season("春分") == "春"
        assert jieqi.find_season("夏至") == "夏"
        assert jieqi.find_season("秋分") == "秋"
        assert jieqi.find_season("冬至") == "冬"
