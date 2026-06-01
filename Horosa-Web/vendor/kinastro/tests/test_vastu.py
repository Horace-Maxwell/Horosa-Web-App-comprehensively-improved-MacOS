"""
tests/test_vastu.py — Vastu Shastra 模組測試

涵蓋：
  • VastuEngine 基本計算（不同 Lagna + 房屋朝向）
  • PlanetVastuInfluence 欄位完整性
  • Compliance Score 範圍（0–100）
  • 高亮方位字典一致性
  • VastuEngine.from_vedic_chart() Mock 測試
  • generate_vastu_disk() 便利函數
  • constants.py 資料完整性
  • interpretations.py 資料完整性

測試 Vastu 模組，確保核心邏輯正確運作。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from astro.vastu.constants import (
    FACING_OPTIONS_8,
    INNER_ZONES,
    LAGNA_RULER,
    OUTER_PADAS,
    PLANET_ZONE,
    ZODIAC_ZH,
)
from astro.vastu.engine import (
    VastuEngine,
    VastuResult,
    PlanetVastuInfluence,
    _classify_influence,
    _facing_angle,
    generate_vastu_disk,
)
from astro.vastu.interpretations import (
    DIRECTION_DETAILS,
    LAGNA_VASTU_DETAILS,
    ROOM_PLACEMENT,
    get_direction_detail,
)


# ─────────────────────────────────────────────────────────────────────────────
# 測試資料輔助
# ─────────────────────────────────────────────────────────────────────────────

_SAMPLE_PLANETS = {
    "Sun":     "Leo",
    "Moon":    "Cancer",
    "Mars":    "Scorpio",
    "Mercury": "Virgo",
    "Jupiter": "Sagittarius",
    "Venus":   "Libra",
    "Saturn":  "Capricorn",
    "Rahu":    "Gemini",
    "Ketu":    "Sagittarius",
}

_ALL_SIGNS = list(ZODIAC_ZH.keys())
_ALL_FACINGS = [code for code, _, _ in FACING_OPTIONS_8]


@dataclass
class _MockPlanetData:
    """Mock VedicChart 行星資料（模擬 astro.vedic.indian.PlanetData）。"""
    name: str
    sign: str
    longitude: float = 0.0


@dataclass
class _MockVedicChart:
    """Mock VedicChart 物件（模擬 astro.vedic.indian.VedicChart）。"""
    asc_rashi: str
    planets: list[Any] = field(default_factory=list)
    ascendant: float = 0.0
    julian_day: float = 2451545.0


def _make_mock_chart(lagna: str = "Aries") -> _MockVedicChart:
    """建立 Mock VedicChart 物件。"""
    planets = [
        _MockPlanetData("Surya (太陽)", "Leo"),
        _MockPlanetData("Chandra (月亮)", "Cancer"),
        _MockPlanetData("Mangal (火星)", "Scorpio"),
        _MockPlanetData("Budha (水星)", "Virgo"),
        _MockPlanetData("Guru (木星)", "Sagittarius"),
        _MockPlanetData("Shukra (金星)", "Libra"),
        _MockPlanetData("Shani (土星)", "Capricorn"),
        _MockPlanetData("Rahu", "Gemini"),
        _MockPlanetData("Ketu", "Sagittarius"),
    ]
    return _MockVedicChart(asc_rashi=lagna, planets=planets)


# ─────────────────────────────────────────────────────────────────────────────
# constants.py 完整性測試
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    """測試 constants.py 資料完整性。"""

    def test_facing_options_8_count(self) -> None:
        """FACING_OPTIONS_8 應有恰好 8 個方位。"""
        assert len(FACING_OPTIONS_8) == 8

    def test_facing_angles_range(self) -> None:
        """所有方位角度應在 [0, 360) 範圍內。"""
        for code, name, angle in FACING_OPTIONS_8:
            assert 0.0 <= angle < 360.0, f"{code} 角度超出範圍：{angle}"

    def test_facing_codes_unique(self) -> None:
        """方位代碼不應重複。"""
        codes = [code for code, _, _ in FACING_OPTIONS_8]
        assert len(codes) == len(set(codes))

    def test_outer_padas_count(self) -> None:
        """外環 Pada 應有恰好 32 個。"""
        assert len(OUTER_PADAS) == 32

    def test_outer_padas_zone_keys_valid(self) -> None:
        """所有外環 Pada 的方位代碼應在 ZONE_COLORS_OUTER 鍵內。"""
        from astro.vastu.constants import ZONE_COLORS_OUTER
        valid_zones = set(ZONE_COLORS_OUTER.keys())
        for row, col, sk, zh, zone in OUTER_PADAS:
            assert zone in valid_zones, (
                f"外環格 {sk}（row={row}, col={col}）的方位 {zone} 無效"
            )

    def test_inner_zones_count(self) -> None:
        """INNER_ZONES 應有恰好 9 個（8 方位 + Center）。"""
        assert len(INNER_ZONES) == 9

    def test_planet_zone_all_planets(self) -> None:
        """PLANET_ZONE 應覆蓋所有九曜行星。"""
        expected = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
        assert set(PLANET_ZONE.keys()) == expected

    def test_lagna_ruler_all_signs(self) -> None:
        """LAGNA_RULER 應覆蓋所有 12 個星座。"""
        assert len(LAGNA_RULER) == 12


# ─────────────────────────────────────────────────────────────────────────────
# engine.py 輔助函數測試
# ─────────────────────────────────────────────────────────────────────────────

class TestHelperFunctions:
    """測試 engine.py 輔助函數。"""

    def test_classify_benefic(self) -> None:
        """Jupiter、Venus、Moon 應被分類為吉星。"""
        for planet in ["Jupiter", "Venus", "Moon"]:
            assert _classify_influence(planet) == "benefic"

    def test_classify_malefic(self) -> None:
        """Mars、Saturn、Rahu、Ketu、Sun 應被分類為凶星。"""
        for planet in ["Mars", "Saturn", "Rahu", "Ketu", "Sun"]:
            assert _classify_influence(planet) == "malefic"

    def test_classify_unknown(self) -> None:
        """未知行星應被分類為中性。"""
        assert _classify_influence("Unknown") == "neutral"

    def test_facing_angle_north(self) -> None:
        """北方的角度應為 0.0。"""
        assert _facing_angle("N") == 0.0

    def test_facing_angle_south(self) -> None:
        """南方的角度應為 180.0。"""
        assert _facing_angle("S") == 180.0

    def test_facing_angle_east(self) -> None:
        """東方的角度應為 90.0。"""
        assert _facing_angle("E") == 90.0

    def test_facing_angle_unknown(self) -> None:
        """未知方位代碼應回傳 0.0。"""
        assert _facing_angle("X") == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# VastuEngine 核心計算測試
# ─────────────────────────────────────────────────────────────────────────────

class TestVastuEngine:
    """測試 VastuEngine.compute() 核心邏輯。"""

    def test_basic_aries_north(self) -> None:
        """牡羊座上升、朝北，應回傳有效 VastuResult。"""
        engine = VastuEngine()
        result = engine.compute("Aries", _SAMPLE_PLANETS, house_facing="N")
        assert isinstance(result, VastuResult)
        assert result.lagna_sign == "Aries"
        assert result.lagna_ruler == "Mars"
        assert result.lagna_ruler_zone == "S"  # 火星 → 南方
        assert result.house_facing == "N"

    def test_compliance_score_range(self) -> None:
        """Vastu Compliance Score 應在 0–100 範圍內。"""
        engine = VastuEngine()
        for lagna in _ALL_SIGNS:
            for facing in _ALL_FACINGS:
                result = engine.compute(lagna, _SAMPLE_PLANETS, house_facing=facing)
                assert 0.0 <= result.compliance_score <= 100.0, (
                    f"Lagna={lagna}, Facing={facing} 分數超出範圍：{result.compliance_score}"
                )

    def test_planet_influences_populated(self) -> None:
        """行星影響列表應非空（提供行星位置時）。"""
        engine = VastuEngine()
        result = engine.compute("Leo", _SAMPLE_PLANETS, house_facing="E")
        assert len(result.planet_influences) > 0

    def test_planet_influence_fields(self) -> None:
        """每個 PlanetVastuInfluence 應有所有必要欄位。"""
        engine = VastuEngine()
        result = engine.compute("Aries", _SAMPLE_PLANETS, house_facing="N")
        for inf in result.planet_influences:
            assert inf.planet_en, "planet_en 不應為空"
            assert inf.planet_zh, "planet_zh 不應為空"
            assert inf.symbol, "symbol 不應為空"
            assert inf.vastu_zone in PLANET_ZONE.values(), f"zone {inf.vastu_zone} 無效"
            assert inf.influence_type in ("benefic", "malefic", "neutral")

    def test_lagna_ruler_is_highlighted(self) -> None:
        """上升主宰行星的 Vastu 方位應出現在 highlight_zones 中。"""
        engine = VastuEngine()
        result = engine.compute("Sagittarius", _SAMPLE_PLANETS, house_facing="NE")
        # 木星 → NE，NE 應在高亮方位中
        assert "NE" in result.highlight_zones

    def test_recommended_facing_provided(self) -> None:
        """所有星座的 recommended_facing 應非空字串。"""
        engine = VastuEngine()
        for lagna in _ALL_SIGNS:
            result = engine.compute(lagna, _SAMPLE_PLANETS, house_facing="N")
            assert result.recommended_facing, f"Lagna={lagna} 缺少推薦朝向"

    def test_room_suggestions_provided(self) -> None:
        """所有星座的 room_suggestions 應非空列表。"""
        engine = VastuEngine()
        for lagna in _ALL_SIGNS:
            result = engine.compute(lagna, _SAMPLE_PLANETS, house_facing="N")
            assert len(result.room_suggestions) > 0, f"Lagna={lagna} 缺少房間建議"

    def test_moon_element_tip(self) -> None:
        """月亮星座有元素對應時，應回傳非空建議。"""
        engine = VastuEngine()
        result = engine.compute("Leo", _SAMPLE_PLANETS, house_facing="E")
        # Moon in Cancer → 水象
        assert result.moon_element == "水"
        assert result.moon_element_tip

    def test_empty_planets(self) -> None:
        """空行星字典時應仍能正常回傳 VastuResult。"""
        engine = VastuEngine()
        result = engine.compute("Aries", {}, house_facing="N")
        assert isinstance(result, VastuResult)
        assert result.compliance_score >= 0.0

    @pytest.mark.parametrize("lagna,expected_ruler", [
        ("Aries",       "Mars"),
        ("Leo",         "Sun"),
        ("Cancer",      "Moon"),
        ("Sagittarius", "Jupiter"),
        ("Capricorn",   "Saturn"),
        ("Pisces",      "Jupiter"),
    ])
    def test_lagna_ruler_mapping(self, lagna: str, expected_ruler: str) -> None:
        """上升星座 → 主宰行星對應應正確。"""
        engine = VastuEngine()
        result = engine.compute(lagna, _SAMPLE_PLANETS, house_facing="N")
        assert result.lagna_ruler == expected_ruler, (
            f"Lagna={lagna}: 期望 {expected_ruler}, 得到 {result.lagna_ruler}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# VastuEngine.from_vedic_chart() 測試
# ─────────────────────────────────────────────────────────────────────────────

class TestFromVedicChart:
    """測試 VastuEngine.from_vedic_chart() 方法。"""

    def test_basic_mock_chart(self) -> None:
        """從 Mock VedicChart 生成結果，應正確解析 Lagna。"""
        mock_chart = _make_mock_chart("Aries")
        result = VastuEngine.from_vedic_chart(mock_chart, house_facing="N")
        assert result.lagna_sign == "Aries"
        assert result.lagna_ruler == "Mars"

    def test_leo_mock_chart(self) -> None:
        """獅子座上升 Mock 測試，主宰行星應為 Sun。"""
        mock_chart = _make_mock_chart("Leo")
        result = VastuEngine.from_vedic_chart(mock_chart, house_facing="E")
        assert result.lagna_sign == "Leo"
        assert result.lagna_ruler == "Sun"
        assert result.lagna_ruler_zone == "E"  # 太陽 → 東方

    def test_pisces_mock_chart(self) -> None:
        """雙魚座上升 Mock 測試，主宰行星應為 Jupiter。"""
        mock_chart = _make_mock_chart("Pisces")
        result = VastuEngine.from_vedic_chart(mock_chart, house_facing="NE")
        assert result.lagna_sign == "Pisces"
        assert result.lagna_ruler == "Jupiter"

    def test_planet_name_parsing(self) -> None:
        """行星名稱解析應正確處理「Surya (太陽)」格式。"""
        mock_chart = _make_mock_chart("Cancer")
        result = VastuEngine.from_vedic_chart(mock_chart, house_facing="NW")
        # Moon 應在行星列表中
        moon_infs = [i for i in result.planet_influences if i.planet_en == "Moon"]
        assert len(moon_infs) == 1
        assert moon_infs[0].vastu_zone == "NW"  # 月亮 → 西北

    def test_all_lagnas(self) -> None:
        """所有 12 個 Lagna 都應能生成有效結果。"""
        for lagna in _ALL_SIGNS:
            mock_chart = _make_mock_chart(lagna)
            result = VastuEngine.from_vedic_chart(mock_chart, house_facing="N")
            assert isinstance(result, VastuResult)
            assert result.lagna_sign == lagna


# ─────────────────────────────────────────────────────────────────────────────
# generate_vastu_disk() 便利函數測試
# ─────────────────────────────────────────────────────────────────────────────

class TestGenerateVastuDisk:
    """測試 generate_vastu_disk() 便利函數。"""

    def test_with_mock_chart(self) -> None:
        """傳入 Mock VedicChart（含 asc_rashi 屬性），應正常運作。"""
        mock_chart = _make_mock_chart("Scorpio")
        result = generate_vastu_disk(mock_chart, house_facing="S")
        assert result.lagna_sign == "Scorpio"
        assert result.house_facing == "S"

    def test_without_chart_returns_result(self) -> None:
        """無命盤資料時，應回傳空白 VastuResult（不崩潰）。"""
        result = generate_vastu_disk(None, house_facing="E")
        assert isinstance(result, VastuResult)
        assert result.house_facing == "E"

    def test_facing_stored_in_result(self) -> None:
        """房屋朝向應正確儲存在結果中。"""
        for facing in _ALL_FACINGS:
            mock_chart = _make_mock_chart("Aries")
            result = generate_vastu_disk(mock_chart, house_facing=facing)
            assert result.house_facing == facing


# ─────────────────────────────────────────────────────────────────────────────
# interpretations.py 完整性測試
# ─────────────────────────────────────────────────────────────────────────────

class TestInterpretations:
    """測試 interpretations.py 資料完整性。"""

    def test_direction_details_8_zones(self) -> None:
        """DIRECTION_DETAILS 應包含 8 個主方位。"""
        expected = {"E", "SE", "S", "SW", "W", "NW", "N", "NE"}
        assert set(DIRECTION_DETAILS.keys()) == expected

    def test_direction_detail_required_keys(self) -> None:
        """每個方位詳解應包含所有必要鍵。"""
        required_keys = {
            "zone_code", "name_zh", "deity", "element", "planet",
            "colors", "rooms", "avoid", "significance", "remedies", "scripture",
        }
        for zone, detail in DIRECTION_DETAILS.items():
            missing = required_keys - set(detail.keys())
            assert not missing, f"方位 {zone} 缺少鍵：{missing}"

    def test_get_direction_detail_returns_copy(self) -> None:
        """get_direction_detail() 應回傳字典副本（不可改動原資料）。"""
        d = get_direction_detail("NE")
        assert d == DIRECTION_DETAILS["NE"]
        d["test_key"] = "test"
        assert "test_key" not in DIRECTION_DETAILS["NE"]

    def test_get_direction_detail_unknown(self) -> None:
        """未知方位代碼應回傳空字典。"""
        result = get_direction_detail("XYZ")
        assert result == {}

    def test_lagna_vastu_details_all_signs(self) -> None:
        """LAGNA_VASTU_DETAILS 應覆蓋所有 12 個星座。"""
        for sign in _ALL_SIGNS:
            assert sign in LAGNA_VASTU_DETAILS, f"缺少星座 {sign} 的 Vastu 建議"

    def test_lagna_vastu_details_non_empty(self) -> None:
        """每個星座的 Vastu 建議應有至少 5 個項目。"""
        for sign, details in LAGNA_VASTU_DETAILS.items():
            assert len(details) >= 5, f"Lagna={sign} 的建議項目不足"

    def test_lagna_vastu_details_structure(self) -> None:
        """每個建議項目應為 (建議, 理由) 的 tuple。"""
        for sign, details in LAGNA_VASTU_DETAILS.items():
            for item, value in details.items():
                assert isinstance(value, tuple) and len(value) == 2, (
                    f"Lagna={sign}, 項目={item} 的格式應為 (建議, 理由) tuple"
                )

    def test_room_placement_all_signs(self) -> None:
        """ROOM_PLACEMENT 應覆蓋所有 12 個星座。"""
        for sign in _ALL_SIGNS:
            assert sign in ROOM_PLACEMENT, f"缺少星座 {sign} 的房間配置"

    def test_room_placement_required_keys(self) -> None:
        """每個房間建議應包含房間、最佳方位、說明、補救 4 個鍵。"""
        required = {"房間", "最佳方位", "說明", "補救"}
        for sign, rooms in ROOM_PLACEMENT.items():
            for room in rooms:
                missing = required - set(room.keys())
                assert not missing, f"Lagna={sign}, 缺少鍵：{missing}"
