"""Unit tests for the kinwangji.wanji module.

Tests cover:
- Hexagram change (line toggling)
- Cycle decomposition (accumulated-year → 會/運/世)
- Stems-branches (gangzhi) calculation
- Month-hexagram derivation
- Full wanji_four_gua computation with known-good values
- Input validation / error handling
- Display formatting (display_pan)
"""

import pytest

from kinwangji import wanji_four_gua, gangzhi, jiazi, jq
from kinwangji.wanji import (
    _compute_cycles,
    _derive_month_hexagrams,
    change,
    closest,
    closest2,
    display_pan,
    liujiashun_dict,
    minutes_jiazi_d,
    one2two,
    sixtyfourgua,
    wangji_gua,
)


# ---------------------------------------------------------------------------
# change() — hexagram line toggling
# ---------------------------------------------------------------------------


class TestChange:
    """Tests for the hexagram line-toggle function."""

    def test_toggle_yang_to_yin(self):
        """Toggling a yang line (7) should produce yin (8)."""
        result = change("777777", 1)
        assert result[0] == "8"  # Position 1 maps to index 0

    def test_toggle_yin_to_yang(self):
        """Toggling a yin line (8) should produce yang (7)."""
        result = change("888888", 3)
        assert result[2] == "7"  # Position 3 maps to index 2

    def test_only_targeted_line_changes(self):
        """Only the specified line should change; others remain the same."""
        original = "778877"
        result = change(original, 6)
        # Position 6 → index 5
        assert result[5] != original[5]
        assert result[:5] == original[:5]

    def test_invalid_yao_raises(self):
        """Passing yao outside 1-6 should raise ValueError."""
        with pytest.raises(ValueError):
            change("777777", 0)
        with pytest.raises(ValueError):
            change("777777", 7)


# ---------------------------------------------------------------------------
# _compute_cycles() — accumulated-year decomposition
# ---------------------------------------------------------------------------


class TestComputeCycles:
    """Tests for the cycle decomposition helper."""

    def test_positive_year_2025(self):
        """Year 2025 should decompose into known 會/運/世 values."""
        acum, hui, yun, shi = _compute_cycles(2025)
        assert acum == 67017 + 2025  # = 69042
        # 會 = 69042 // 10800 + 1 = 6 + 1 = 7
        assert hui == 7
        # 運 = 69042 // 360 + 1 = 191 + 1 = 192
        assert yun == 192
        # 世 = 69042 // 30 + 1 = 2301 + 1 = 2302
        assert shi == 2302

    def test_year_1(self):
        """Year 1 CE should give acum = 67018."""
        acum, hui, yun, shi = _compute_cycles(1)
        assert acum == 67018

    def test_negative_year(self):
        """Negative years use the formula: 67017 + year + 1."""
        acum, _, _, shi = _compute_cycles(-100)
        assert acum == 67017 + (-100) + 1  # = 66918
        # shi has +2 offset for negative years
        assert shi == acum // 30 + 2


# ---------------------------------------------------------------------------
# one2two() — display padding
# ---------------------------------------------------------------------------


class TestOne2Two:
    def test_single_char_padded(self):
        assert one2two("乾") == "乾　"
        assert len(one2two("乾")) == 2

    def test_two_char_unchanged(self):
        assert one2two("大過") == "大過"


# ---------------------------------------------------------------------------
# minutes_jiazi_d() — minute-level stems-branches
# ---------------------------------------------------------------------------


class TestMinutesJiaziD:
    def test_returns_1440_entries(self):
        """24 hours × 60 minutes = 1440 entries."""
        d = minutes_jiazi_d()
        assert len(d) == 1440

    def test_first_entry(self):
        """The entry for 0:0 should be 甲子."""
        d = minutes_jiazi_d()
        assert d["0:0"] == "甲子"

    def test_values_are_jiazi(self):
        """All values should be valid sexagenary cycle entries."""
        d = minutes_jiazi_d()
        cycle = set(jiazi())
        for v in d.values():
            assert v in cycle


# ---------------------------------------------------------------------------
# liujiashun_dict() — 10-day cycle mapping
# ---------------------------------------------------------------------------


class TestLiujiashunDict:
    def test_has_six_entries(self):
        """There are 6 甲-day groups in the 60-day cycle."""
        d = liujiashun_dict()
        assert len(d) == 6

    def test_all_values_start_with_jia(self):
        """Each leading day should start with 甲."""
        for v in liujiashun_dict().values():
            assert v.startswith("甲")


# ---------------------------------------------------------------------------
# closest() — nearest-value lookup
# ---------------------------------------------------------------------------


class TestClosest:
    def test_returns_previous_element(self):
        lst = [10, 20, 30, 40, 50]
        # Closest to 31 is 30 (index 2), so returns lst[1] = 20
        assert closest(lst, 31) == 20

    def test_exact_match(self):
        lst = [10, 20, 30, 40, 50]
        # Closest to 30 is 30 (index 2), returns lst[1] = 20
        assert closest(lst, 30) == 20


class TestClosest2:
    def test_returns_exact_element(self):
        lst = [10, 20, 30, 40, 50]
        assert closest2(lst, 30) == 30

    def test_returns_nearest(self):
        lst = [10, 20, 30, 40, 50]
        assert closest2(lst, 31) == 30


# ---------------------------------------------------------------------------
# gangzhi() — stems-branches
# ---------------------------------------------------------------------------


class TestGangzhi:
    def test_returns_five_elements(self):
        """gangzhi should return [year, month, day, hour, minute]."""
        result = gangzhi(2025, 6, 15, 10, 30)
        assert isinstance(result, list)
        assert len(result) == 5

    def test_year_zero_invalid(self):
        """Year 0 is invalid in the Chinese calendar."""
        result = gangzhi(0, 1, 1, 0, 0)
        assert result == ["無效"]

    def test_all_elements_are_strings(self):
        result = gangzhi(2025, 1, 1, 12, 0)
        for elem in result:
            assert isinstance(elem, str)


# ---------------------------------------------------------------------------
# wanji_four_gua() — full hexagram computation
# ---------------------------------------------------------------------------


class TestWanjiFourGua:
    def test_returns_expected_keys(self):
        result = wanji_four_gua(2025, 6, 15, 10, 30)
        expected_keys = {
            "日期", "干支", "會", "運", "世",
            "運卦動爻", "世卦動爻", "旬卦動爻",
            "正卦", "運卦", "世卦", "旬卦",
            "年卦", "月卦", "日卦", "時卦", "分卦",
        }
        assert set(result.keys()) == expected_keys

    def test_hui_yun_shi_types(self):
        """會, 運, 世 should all be positive integers."""
        result = wanji_four_gua(2025, 6, 15, 10, 30)
        assert isinstance(result["會"], int) and result["會"] > 0
        assert isinstance(result["運"], int) and result["運"] > 0
        assert isinstance(result["世"], int) and result["世"] > 0

    def test_all_gua_are_valid_names(self):
        """All hexagram values should be valid 60-gua names."""
        result = wanji_four_gua(2025, 6, 15, 10, 30)
        valid_gua = set(wangji_gua.values())
        for key in ["正卦", "運卦", "世卦", "旬卦", "年卦", "月卦", "日卦", "時卦", "分卦"]:
            assert result[key] in valid_gua, f"{key}={result[key]} not in valid gua set"

    def test_different_minutes_produce_different_fen_gua(self):
        """Changing the minute should change the 分卦."""
        r1 = wanji_four_gua(2025, 6, 15, 10, 0)
        r2 = wanji_four_gua(2025, 6, 15, 10, 30)
        # 分卦 should differ for minute 0 vs 30
        assert r1["分卦"] != r2["分卦"]

    def test_known_value_2025(self):
        """Spot-check: 2025-06-15 10:30 should produce 會=7."""
        result = wanji_four_gua(2025, 6, 15, 10, 30)
        assert result["會"] == 7

    def test_gangzhi_list_length(self):
        """干支 should be a list of 5 elements."""
        result = wanji_four_gua(2025, 6, 15, 10, 30)
        assert len(result["干支"]) == 5

    @pytest.mark.parametrize(
        "year,month,day,hour,expected_special",
        [
            (2026, 5, 1, 12, "乾"),
            (2021, 8, 15, 0, "離"),
            (2029, 2, 15, 0, "坎"),
            (2024, 12, 1, 0, "離"),
        ],
    )
    def test_special_hexagram_month_no_crash(self, year, month, day, hour, expected_special):
        """Dates whose month hexagram is 乾/坤/離/坎 must not raise ValueError."""
        result = wanji_four_gua(year, month, day, hour, 0)
        assert result["月卦"] == expected_special
        # All returned hexagrams must be valid names
        valid = set(wangji_gua.values()) | {"乾", "坤", "離", "坎"}
        for key in ["正卦", "運卦", "世卦", "旬卦", "年卦", "月卦", "日卦", "時卦", "分卦"]:
            assert result[key] in valid, f"{key}={result[key]} not valid"


# ---------------------------------------------------------------------------
# _derive_month_hexagrams() — month-hexagram derivation
# ---------------------------------------------------------------------------


class TestDeriveMonthHexagrams:
    def test_returns_12_months(self):
        """Should return a dict with keys 1–12."""
        # Use a known hexagram code
        code = sixtyfourgua.inverse["復"][0]
        result = _derive_month_hexagrams(code)
        assert set(result.keys()) == set(range(1, 13))

    def test_values_are_valid_gua_or_none(self):
        """Each month should map to a valid hexagram name."""
        code = sixtyfourgua.inverse["復"][0]
        valid = set(wangji_gua.values()) | set(sixtyfourgua.values())
        result = _derive_month_hexagrams(code)
        for m, gua in result.items():
            assert gua is None or gua in valid, f"Month {m}: {gua} not valid"


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


class TestInputValidation:
    def test_invalid_month_raises(self):
        with pytest.raises(ValueError, match="Month"):
            wanji_four_gua(2025, 13, 1, 0, 0)

    def test_invalid_hour_raises(self):
        with pytest.raises(ValueError, match="Hour"):
            wanji_four_gua(2025, 1, 1, 25, 0)

    def test_invalid_minute_raises(self):
        with pytest.raises(ValueError, match="Minute"):
            wanji_four_gua(2025, 1, 1, 0, 60)

    def test_jq_invalid_month_raises(self):
        with pytest.raises(ValueError):
            jq(2025, 0, 1, 0, 0)


# ---------------------------------------------------------------------------
# display_pan() — smoke test
# ---------------------------------------------------------------------------


class TestDisplayPan:
    def test_returns_string(self):
        result = display_pan(2025, 6, 15, 10, 30)
        assert isinstance(result, str)

    def test_contains_key_sections(self):
        result = display_pan(2025, 6, 15, 10, 30)
        assert "起卦時間" in result
        assert "農曆" in result
        assert "干支" in result
        assert "節氣" in result
        assert "正卦" in result
