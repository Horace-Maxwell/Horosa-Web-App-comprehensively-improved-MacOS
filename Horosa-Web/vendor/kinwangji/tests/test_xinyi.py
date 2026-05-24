"""Unit tests for the kinwangji.xinyi module.

Tests cover:
- Pre-Heaven number method (number_qigua)
- Date-time method (datetime_qigua)
- Post-Heaven direction method (direction_qigua)
- Character stroke method (character_qigua)
- Internal helpers (_num_to_trigram, _moving_line, _hu_gua, _build_result)
"""

import pytest

from kinwangji.xinyi import (
    DIRECTION_GUA,
    GUA_WUXING,
    HOUTIAN_NUM,
    TRIGRAM_CODE,
    XIANTIAN_NUM,
    _build_result,
    _hu_gua,
    _moving_line,
    _num_to_trigram,
    _trigram_at,
    character_qigua,
    datetime_qigua,
    direction_qigua,
    number_qigua,
)
from kinwangji.wanji import sixtyfourgua


# ---------------------------------------------------------------------------
# _num_to_trigram()
# ---------------------------------------------------------------------------


class TestNumToTrigram:
    """Tests for the number-to-trigram conversion helper."""

    def test_xiantian_1_to_8(self):
        """Numbers 1–8 should map directly to Pre-Heaven trigrams."""
        expected = ["乾", "兌", "離", "震", "巽", "坎", "艮", "坤"]
        for i, name in enumerate(expected, 1):
            assert _num_to_trigram(i, "xiantian") == name

    def test_xiantian_mod_8(self):
        """Numbers > 8 should be reduced mod 8."""
        assert _num_to_trigram(9, "xiantian") == "乾"   # 9 % 8 = 1
        assert _num_to_trigram(16, "xiantian") == "坤"   # 16 % 8 = 0 → 8
        assert _num_to_trigram(10, "xiantian") == "兌"   # 10 % 8 = 2

    def test_houtian_1_to_8(self):
        """Numbers 1–8 should map directly to Post-Heaven trigrams."""
        expected = ["坎", "坤", "震", "巽", "坤", "乾", "兌", "艮"]
        for i, name in enumerate(expected, 1):
            assert _num_to_trigram(i, "houtian") == name

    def test_invalid_zero_raises(self):
        with pytest.raises(ValueError):
            _num_to_trigram(0, "xiantian")

    def test_invalid_system_raises(self):
        with pytest.raises(ValueError):
            _num_to_trigram(1, "invalid")


# ---------------------------------------------------------------------------
# _moving_line()
# ---------------------------------------------------------------------------


class TestMovingLine:
    """Tests for the moving-line position helper."""

    def test_values_1_to_6(self):
        assert _moving_line(1) == 1
        assert _moving_line(2) == 2
        assert _moving_line(5) == 5
        assert _moving_line(6) == 6   # 6 % 6 = 0 → 6

    def test_mod_6(self):
        assert _moving_line(7) == 1   # 7 % 6 = 1
        assert _moving_line(12) == 6  # 12 % 6 = 0 → 6
        assert _moving_line(15) == 3  # 15 % 6 = 3


# ---------------------------------------------------------------------------
# _trigram_at()
# ---------------------------------------------------------------------------


class TestTrigramAt:
    """Tests for extracting trigram from hexagram code."""

    def test_lower_trigram(self):
        assert _trigram_at("777888", "lower") == "乾"

    def test_upper_trigram(self):
        assert _trigram_at("777888", "upper") == "坤"


# ---------------------------------------------------------------------------
# _hu_gua()
# ---------------------------------------------------------------------------


class TestHuGua:
    """Tests for the interlocking hexagram (互卦) derivation."""

    def test_known_hu_gua(self):
        # 泰 (乾下坤上) = 777888 → 互卦 lines 2-3-4 and 3-4-5
        # lines: 7,7,7,8,8,8 → hu_lower = 7,7,8 = 兌, hu_upper = 7,8,8 = 震
        # 兌下震上 = 歸妹
        result = _hu_gua("777888")
        assert result is not None

    def test_qian_hu_gua(self):
        # 乾 (777777) → hu_lower = 777 = 乾, hu_upper = 777 = 乾
        assert _hu_gua("777777") == "乾"

    def test_kun_hu_gua(self):
        # 坤 (888888) → hu_lower = 888 = 坤, hu_upper = 888 = 坤
        assert _hu_gua("888888") == "坤"


# ---------------------------------------------------------------------------
# _build_result()
# ---------------------------------------------------------------------------


class TestBuildResult:
    """Tests for the result builder."""

    def test_returns_expected_keys(self):
        result = _build_result("乾", "坤", 1)
        expected_keys = {
            "本卦", "變卦", "動爻", "上卦", "下卦",
            "體卦", "用卦", "互卦", "體用五行",
        }
        assert set(result.keys()) == expected_keys

    def test_qian_shang_kun_xia(self):
        """乾上坤下 = 否卦."""
        result = _build_result("乾", "坤", 1)
        assert result["本卦"] == "否"
        assert result["上卦"] == "乾"
        assert result["下卦"] == "坤"

    def test_moving_line_lower_body_is_upper(self):
        """When moving line is in lower trigram (1–3), body = upper."""
        result = _build_result("乾", "坤", 2)
        assert result["體卦"] == "乾"
        assert result["用卦"] == "坤"

    def test_moving_line_upper_body_is_lower(self):
        """When moving line is in upper trigram (4–6), body = lower."""
        result = _build_result("乾", "坤", 5)
        assert result["體卦"] == "坤"
        assert result["用卦"] == "乾"

    def test_bian_gua_differs_from_ben_gua(self):
        """Changed hexagram should differ from original."""
        result = _build_result("離", "坎", 1)
        assert result["變卦"] != result["本卦"]


# ---------------------------------------------------------------------------
# number_qigua()
# ---------------------------------------------------------------------------


class TestNumberQigua:
    """Tests for the Pre-Heaven number method."""

    def test_basic(self):
        """number_qigua(5, 10) → 巽 upper, 兌 lower."""
        r = number_qigua(5, 10)
        assert r["上卦"] == "巽"       # 5 → 巽
        assert r["下卦"] == "兌"       # 10 % 8 = 2 → 兌
        assert r["動爻"] == 3          # (5 + 10) % 6 = 3
        assert r["本卦"] == "中孚"     # 兌下巽上

    def test_large_numbers(self):
        """Large numbers should be correctly reduced mod 8."""
        r = number_qigua(100, 200)
        assert r["上卦"] == "震"       # 100 % 8 = 4 → 震
        assert r["下卦"] == "坤"       # 200 % 8 = 0 → 8 → 坤
        assert r["動爻"] == 6          # (100 + 200) % 6 = 0 → 6

    def test_invalid_zero_raises(self):
        with pytest.raises(ValueError):
            number_qigua(0, 5)
        with pytest.raises(ValueError):
            number_qigua(5, 0)

    def test_same_numbers(self):
        """Same number for both should produce a doubled trigram."""
        r = number_qigua(1, 1)
        assert r["上卦"] == "乾"
        assert r["下卦"] == "乾"
        assert r["本卦"] == "乾"

    def test_result_has_all_keys(self):
        r = number_qigua(3, 7)
        for key in ["本卦", "變卦", "動爻", "上卦", "下卦",
                     "體卦", "用卦", "互卦", "體用五行"]:
            assert key in r


# ---------------------------------------------------------------------------
# datetime_qigua()
# ---------------------------------------------------------------------------


class TestDatetimeQigua:
    """Tests for the date-time method."""

    def test_returns_valid_result(self):
        r = datetime_qigua(2025, 6, 15, 10)
        assert r["本卦"] is not None
        assert 1 <= r["動爻"] <= 6

    def test_different_hours_can_differ(self):
        """Different hours may produce different hexagrams."""
        r1 = datetime_qigua(2025, 6, 15, 8)
        r2 = datetime_qigua(2025, 6, 15, 14)
        # At least the lower trigram or moving line should differ
        assert r1["下卦"] != r2["下卦"] or r1["動爻"] != r2["動爻"]

    def test_result_has_all_keys(self):
        r = datetime_qigua(2025, 1, 1, 0)
        for key in ["本卦", "變卦", "動爻", "上卦", "下卦",
                     "體卦", "用卦", "互卦", "體用五行"]:
            assert key in r


# ---------------------------------------------------------------------------
# direction_qigua()
# ---------------------------------------------------------------------------


class TestDirectionQigua:
    """Tests for the Post-Heaven direction method."""

    def test_basic(self):
        r = direction_qigua("離", "南", 14)
        assert r["上卦"] == "離"
        assert r["下卦"] == "離"  # 南 → 離
        assert r["本卦"] == "離"  # 離上離下 = 重離

    def test_different_directions(self):
        r1 = direction_qigua("乾", "北", 10)
        r2 = direction_qigua("乾", "南", 10)
        assert r1["下卦"] != r2["下卦"]

    def test_invalid_trigram_raises(self):
        with pytest.raises(ValueError, match="Invalid trigram"):
            direction_qigua("天", "北", 10)

    def test_invalid_direction_raises(self):
        with pytest.raises(ValueError, match="Invalid direction"):
            direction_qigua("乾", "上", 10)

    def test_all_directions_valid(self):
        """All defined directions should produce valid results."""
        for direction in DIRECTION_GUA:
            r = direction_qigua("乾", direction, 12)
            assert r["本卦"] is not None

    def test_result_has_all_keys(self):
        r = direction_qigua("坎", "東", 8)
        for key in ["本卦", "變卦", "動爻", "上卦", "下卦",
                     "體卦", "用卦", "互卦", "體用五行"]:
            assert key in r


# ---------------------------------------------------------------------------
# character_qigua()
# ---------------------------------------------------------------------------


class TestCharacterQigua:
    """Tests for the character stroke-count method."""

    def test_basic(self):
        r = character_qigua(5, 8)
        assert r["上卦"] == "巽"  # 5 → 巽
        assert r["下卦"] == "坤"  # 8 → 坤

    def test_delegates_to_number_qigua(self):
        """character_qigua should produce the same result as number_qigua."""
        r1 = character_qigua(3, 7)
        r2 = number_qigua(3, 7)
        assert r1 == r2


# ---------------------------------------------------------------------------
# Constants integrity
# ---------------------------------------------------------------------------


class TestConstants:
    """Tests for module-level constant tables."""

    def test_xiantian_has_8_entries(self):
        assert len(XIANTIAN_NUM) == 8

    def test_houtian_has_10_entries(self):
        assert len(HOUTIAN_NUM) == 10

    def test_trigram_code_has_8_entries(self):
        assert len(TRIGRAM_CODE) == 8

    def test_all_trigram_codes_valid(self):
        """Each trigram code should be 3 chars of 7/8."""
        for name, code in TRIGRAM_CODE.items():
            assert len(code) == 3, f"{name} code length != 3"
            assert all(c in "78" for c in code), f"{name} code has invalid chars"

    def test_direction_covers_8_directions(self):
        assert len(DIRECTION_GUA) >= 8

    def test_wuxing_covers_all_trigrams(self):
        for name in TRIGRAM_CODE:
            assert name in GUA_WUXING, f"Missing five-element for {name}"
