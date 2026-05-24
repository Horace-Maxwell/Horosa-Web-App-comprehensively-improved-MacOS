"""
Tests for the shaozi integration: 64 keys, Yuan Hui Yun Shi, and ShaoziFullShenShu.
"""

import pytest

from astro.shaozi import (
    ShaoziShenShu,
    ShaoziFullShenShu,
    YuanHuiYunShi,
    SHAOZI_64_KEYS,
    get_key_name,
    get_key_info,
    get_special_notes,
    get_detailed_key,
)


# ============================================================
# 64 Keys table tests
# ============================================================

class TestShaozi64Keys:
    def test_all_64_keys_present(self):
        assert len(SHAOZI_64_KEYS) == 64
        for i in range(1, 65):
            assert i in SHAOZI_64_KEYS, f"Key {i} missing from SHAOZI_64_KEYS"

    def test_get_key_name(self):
        name = get_key_name(1)
        assert isinstance(name, str)
        assert len(name) > 0

    def test_get_key_name_unknown(self):
        name = get_key_name(99)
        assert "99" in name

    def test_get_special_notes(self):
        specials = get_special_notes(1)
        assert isinstance(specials, list)
        assert "克妻" in specials

    def test_get_detailed_key(self):
        data = get_detailed_key(1)
        assert isinstance(data, dict)
        assert "名稱" in data
        assert "特殊" in data

    def test_get_detailed_key_unknown(self):
        data = get_detailed_key(99)
        assert "error" in data

    def test_get_key_info_shichen(self):
        info = get_key_info(1, ke="子初", category="時辰")
        assert info is not None

    def test_get_key_info_unknown_category(self):
        result = get_key_info(1, category="不存在")
        assert result == "查無此類別資料"


# ============================================================
# YuanHuiYunShi tests
# ============================================================

class TestYuanHuiYunShi:
    def test_basic_cycles(self):
        yhy = YuanHuiYunShi(1990)
        info = yhy.get_cycle_info()
        assert "元" in info
        assert "會" in info
        assert "運" in info
        assert "世" in info
        assert info["birth_year"] == 1990

    def test_cycles_are_positive(self):
        for year in [1960, 1985, 2000, 2025]:
            yhy = YuanHuiYunShi(year)
            info = yhy.get_cycle_info()
            assert info["元"] >= 1
            assert info["會"] >= 1
            assert info["運"] >= 1
            assert info["世"] >= 1

    def test_get_life_stage_returns_string(self):
        yhy = YuanHuiYunShi(1990)
        stage = yhy.get_life_stage()
        assert isinstance(stage, str)
        assert len(stage) > 0

    def test_get_era_description_returns_string(self):
        yhy = YuanHuiYunShi(1990)
        era = yhy.get_era_description()
        assert isinstance(era, str)
        assert len(era) > 0

    def test_get_summary_contains_year(self):
        yhy = YuanHuiYunShi(1990)
        summary = yhy.get_summary()
        assert "1990" in summary


# ============================================================
# ShaoziFullShenShu tests
# ============================================================

class TestShaoziFullShenShu:
    def setup_method(self):
        self.engine = ShaoziFullShenShu()

    def test_cast_plate_returns_dict(self):
        result = self.engine.cast_plate(
            year_gz="甲子", month_gz="丙寅",
            day_gz="戊辰", hour_gz="庚午",
            ke="初刻"
        )
        assert isinstance(result, dict)

    def test_cast_plate_has_required_keys(self):
        result = self.engine.cast_plate(
            year_gz="甲子", month_gz="丙寅",
            day_gz="戊辰", hour_gz="庚午"
        )
        assert "base_number" in result
        assert "tiaowen_id" in result
        assert "gua" in result
        assert "calculation" in result
        assert "input" in result

    def test_cast_plate_base_number_in_range(self):
        result = self.engine.cast_plate(
            year_gz="甲子", month_gz="丙寅",
            day_gz="戊辰", hour_gz="庚午"
        )
        assert 1 <= result["base_number"] <= 64

    def test_cast_plate_includes_64key(self):
        result = self.engine.cast_plate(
            year_gz="甲子", month_gz="丙寅",
            day_gz="戊辰", hour_gz="庚午",
            use_key=True
        )
        assert "key" in result
        assert "名稱" in result["key"]

    def test_cast_plate_includes_yuanhui(self):
        result = self.engine.cast_plate(
            year_gz="甲子", month_gz="丙寅",
            day_gz="戊辰", hour_gz="庚午"
        )
        assert "yuanhui" in result

    def test_cast_plate_no_key(self):
        result = self.engine.cast_plate(
            year_gz="甲子", month_gz="丙寅",
            day_gz="戊辰", hour_gz="庚午",
            use_key=False
        )
        assert "key" not in result

    def test_get_key_detail(self):
        detail = self.engine.get_key_detail(1)
        assert isinstance(detail, dict)
        assert "名稱" in detail

    def test_get_key_detail_unknown(self):
        detail = self.engine.get_key_detail(99)
        assert "error" in detail

    def test_get_key_summary(self):
        summary = self.engine.get_key_summary(1)
        assert isinstance(summary, str)
        assert len(summary) > 0


# ============================================================
# Backward-compatibility: original ShaoziShenShu still importable
# ============================================================

class TestShaoziShenShuBackwardCompat:
    def test_import_original(self):
        from astro.shaozi import ShaoziShenShu
        assert ShaoziShenShu is not None

    def test_original_is_calculator_class(self):
        from astro.shaozi.calculator import ShaoziShenShu as CalcShenShu
        from astro.shaozi import ShaoziShenShu
        assert ShaoziShenShu is CalcShenShu
