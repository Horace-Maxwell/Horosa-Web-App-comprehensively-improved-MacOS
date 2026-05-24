"""
tests/test_alchemical_astrology.py
═══════════════════════════════════════════════════════════════════════════════
煉金占星學（Alchemical Astrology）模組測試

涵蓋：
  • AlchemicalEngine 可以被實例化
  • compute_reading() 返回有效的 AlchemicalReading
  • 所有 7 顆行星有金屬、至少 2 種草本、1 種礦石、人體部位
  • 所有對應關係有非空的文獻來源字串
  • 煉金階段正確映射到行星
  • signatures.get_planet_signature() 返回非空文本
  • engine.compute_reading() 處理缺失行星（預設 0.0°）
  • 尊貴評分計算正確
  • 主導行星選取邏輯
  • AlchemicalReading 欄位完整性
"""

from __future__ import annotations

import pytest

from astro.alchemical_astrology.correspondences import (
    ALCHEMICAL_STAGES,
    PLANET_CORRESPONDENCES,
    PLANET_KEYS,
    longitude_to_sign_index,
)
from astro.alchemical_astrology.engine import (
    AlchemicalEngine,
    AlchemicalReading,
    PlanetProfile,
    _compute_dignity_score,
    _find_dominant_planet,
    compute_reading,
)
from astro.alchemical_astrology.interpretations import (
    get_planet_reading,
    get_stage_reading,
)
from astro.alchemical_astrology.signatures import (
    PLANET_SIGNATURES,
    get_planet_signature,
    get_signature_text_zh,
)


# ─────────────────────────────────────────────────────────────────────────────
# 測試資料
# ─────────────────────────────────────────────────────────────────────────────

# 典型行星度數（太陽在獅子座、月亮在巨蟹座等，各行星在統治宮）
_SAMPLE_LONGITUDES_DIGNITY: dict[str, float] = {
    "sun":     125.0,   # 獅子座 (120–150°) — 太陽統治宮
    "moon":    95.0,    # 巨蟹座 (90–120°)  — 月亮統治宮
    "mars":    5.0,     # 白羊座 (0–30°)    — 火星統治宮
    "mercury": 65.0,    # 雙子座 (60–90°)   — 水星統治宮
    "jupiter": 245.0,   # 射手座 (240–270°) — 木星統治宮
    "venus":   185.0,   # 天秤座 (180–210°) — 金星統治宮
    "saturn":  275.0,   # 摩羯座 (270–300°) — 土星統治宮
}

# 普通度數（無特殊尊貴）
_SAMPLE_LONGITUDES_NEUTRAL: dict[str, float] = {
    "sun":     45.0,    # 金牛座
    "moon":    200.0,   # 天秤座
    "mars":    100.0,   # 巨蟹座
    "mercury": 300.0,   # 水瓶座
    "jupiter": 150.0,   # 處女座
    "venus":   270.0,   # 摩羯座
    "saturn":  60.0,    # 雙子座
}

# 空輸入（全部預設 0.0°）
_SAMPLE_EMPTY: dict[str, float] = {}


# ─────────────────────────────────────────────────────────────────────────────
# 1. AlchemicalEngine 實例化
# ─────────────────────────────────────────────────────────────────────────────

class TestEngineInstantiation:
    """測試 AlchemicalEngine 可以被實例化。"""

    def test_engine_can_be_instantiated(self) -> None:
        """AlchemicalEngine 應可在不帶參數的情況下實例化。"""
        engine = AlchemicalEngine()
        assert engine is not None

    def test_module_level_compute_reading_exists(self) -> None:
        """模組級 compute_reading 便捷函數應存在。"""
        assert callable(compute_reading)


# ─────────────────────────────────────────────────────────────────────────────
# 2. compute_reading() 返回有效的 AlchemicalReading
# ─────────────────────────────────────────────────────────────────────────────

class TestComputeReading:
    """測試 compute_reading() 返回有效的 AlchemicalReading。"""

    def test_returns_alchemical_reading_instance(self) -> None:
        """compute_reading() 應返回 AlchemicalReading 實例。"""
        engine = AlchemicalEngine()
        result = engine.compute_reading(_SAMPLE_LONGITUDES_DIGNITY)
        assert isinstance(result, AlchemicalReading)

    def test_module_level_compute_reading(self) -> None:
        """模組級 compute_reading() 也應返回 AlchemicalReading。"""
        result = compute_reading(_SAMPLE_LONGITUDES_DIGNITY)
        assert isinstance(result, AlchemicalReading)

    def test_handles_empty_input(self) -> None:
        """空輸入應能正常處理（使用預設 0.0°）。"""
        result = compute_reading(_SAMPLE_EMPTY)
        assert isinstance(result, AlchemicalReading)

    def test_handles_partial_input(self) -> None:
        """部分輸入（缺少某些行星）應能正常處理。"""
        result = compute_reading({"sun": 125.0, "moon": 95.0})
        assert isinstance(result, AlchemicalReading)

    def test_planetary_profiles_count(self) -> None:
        """planetary_profiles 應包含 7 顆行星。"""
        result = compute_reading(_SAMPLE_LONGITUDES_DIGNITY)
        assert len(result.planetary_profiles) == 7

    def test_dominant_planet_is_valid_key(self) -> None:
        """dominant_planet 應為有效的行星鍵名。"""
        result = compute_reading(_SAMPLE_LONGITUDES_DIGNITY)
        assert result.dominant_planet in PLANET_KEYS

    def test_dominant_profile_not_none(self) -> None:
        """dominant_profile 不應為 None。"""
        result = compute_reading(_SAMPLE_LONGITUDES_DIGNITY)
        assert result.dominant_profile is not None

    def test_alchemical_stage_key_is_valid(self) -> None:
        """alchemical_stage_key 應為有效的煉金階段鍵名。"""
        result = compute_reading(_SAMPLE_LONGITUDES_DIGNITY)
        assert result.alchemical_stage_key in ALCHEMICAL_STAGES

    def test_herb_recommendations_not_empty(self) -> None:
        """草本建議不應為空。"""
        result = compute_reading(_SAMPLE_LONGITUDES_DIGNITY)
        assert len(result.herb_recommendations) > 0
        assert len(result.herb_recommendations_zh) > 0

    def test_mineral_recommendations_not_empty(self) -> None:
        """礦石建議不應為空。"""
        result = compute_reading(_SAMPLE_LONGITUDES_DIGNITY)
        assert len(result.mineral_recommendations) > 0
        assert len(result.mineral_recommendations_zh) > 0

    def test_herb_recommendations_max_three(self) -> None:
        """草本建議最多三項。"""
        result = compute_reading(_SAMPLE_LONGITUDES_DIGNITY)
        assert len(result.herb_recommendations) <= 3

    def test_signature_descriptions_all_planets(self) -> None:
        """signature_descriptions 應包含所有 7 顆行星。"""
        result = compute_reading(_SAMPLE_LONGITUDES_DIGNITY)
        for key in PLANET_KEYS:
            assert key in result.signature_descriptions

    def test_summary_zh_not_empty(self) -> None:
        """summary_zh 不應為空。"""
        result = compute_reading(_SAMPLE_LONGITUDES_DIGNITY)
        assert result.summary_zh.strip() != ""

    def test_dignity_scores_all_planets(self) -> None:
        """dignity_scores 應包含所有 7 顆行星。"""
        result = compute_reading(_SAMPLE_LONGITUDES_DIGNITY)
        for key in PLANET_KEYS:
            assert key in result.dignity_scores

    def test_planet_longitudes_preserved(self) -> None:
        """planet_longitudes 應保留原始輸入（填充後）。"""
        result = compute_reading(_SAMPLE_LONGITUDES_DIGNITY)
        assert set(result.planet_longitudes.keys()) == set(PLANET_KEYS)


# ─────────────────────────────────────────────────────────────────────────────
# 3. 行星對應關係完整性
# ─────────────────────────────────────────────────────────────────────────────

class TestPlanetCorrespondences:
    """測試所有 7 顆行星有完整的對應關係。"""

    def test_all_seven_planets_present(self) -> None:
        """PLANET_CORRESPONDENCES 應包含 7 顆行星。"""
        assert len(PLANET_CORRESPONDENCES) == 7
        for key in PLANET_KEYS:
            assert key in PLANET_CORRESPONDENCES

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_planet_has_metal(self, planet_key: str) -> None:
        """每顆行星應有金屬對應（非空）。"""
        c = PLANET_CORRESPONDENCES[planet_key]
        assert c.metal_en.strip() != ""
        assert c.metal_zh.strip() != ""
        assert c.metal_latin.strip() != ""

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_planet_has_at_least_two_herbs(self, planet_key: str) -> None:
        """每顆行星應有至少 2 種草本。"""
        c = PLANET_CORRESPONDENCES[planet_key]
        assert len(c.herbs) >= 2
        assert len(c.herbs_zh) >= 2

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_planet_has_at_least_one_mineral(self, planet_key: str) -> None:
        """每顆行星應有至少 1 種礦石。"""
        c = PLANET_CORRESPONDENCES[planet_key]
        assert len(c.minerals) >= 1
        assert len(c.minerals_zh) >= 1

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_planet_has_body_part(self, planet_key: str) -> None:
        """每顆行星應有人體部位對應（非空）。"""
        c = PLANET_CORRESPONDENCES[planet_key]
        assert c.body_part_en.strip() != ""
        assert c.body_part_zh.strip() != ""

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_planet_has_non_empty_source(self, planet_key: str) -> None:
        """每顆行星應有非空的文獻來源字串。"""
        c = PLANET_CORRESPONDENCES[planet_key]
        assert c.source.strip() != ""
        # 來源應提及 Paracelsus 或 Agrippa
        assert any(
            author in c.source for author in ["Paracelsus", "Agrippa", "Ficino"]
        ), f"Planet {planet_key} source does not cite Paracelsus or Agrippa: {c.source}"

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_planet_has_symbol(self, planet_key: str) -> None:
        """每顆行星應有天文符號。"""
        c = PLANET_CORRESPONDENCES[planet_key]
        assert c.symbol.strip() != ""

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_planet_has_color(self, planet_key: str) -> None:
        """每顆行星應有代表色（十六進位格式）。"""
        c = PLANET_CORRESPONDENCES[planet_key]
        assert c.color.startswith("#")
        assert len(c.color) == 7  # #RRGGBB

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_herbs_zh_count_matches_herbs(self, planet_key: str) -> None:
        """中文草本列表數量應與英文相同。"""
        c = PLANET_CORRESPONDENCES[planet_key]
        assert len(c.herbs) == len(c.herbs_zh)

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_minerals_zh_count_matches_minerals(self, planet_key: str) -> None:
        """中文礦石列表數量應與英文相同。"""
        c = PLANET_CORRESPONDENCES[planet_key]
        assert len(c.minerals) == len(c.minerals_zh)


# ─────────────────────────────────────────────────────────────────────────────
# 4. 煉金階段映射正確性
# ─────────────────────────────────────────────────────────────────────────────

class TestAlchemicalStages:
    """測試煉金階段正確映射到行星。"""

    def test_four_stages_defined(self) -> None:
        """應定義四個煉金階段。"""
        assert len(ALCHEMICAL_STAGES) == 4
        for key in ["nigredo", "albedo", "citrinitas", "rubedo"]:
            assert key in ALCHEMICAL_STAGES

    def test_saturn_maps_to_nigredo(self) -> None:
        """土星應對應黑化（nigredo）階段。"""
        c = PLANET_CORRESPONDENCES["saturn"]
        assert c.alchemical_stage.lower() == "nigredo"

    def test_moon_maps_to_albedo(self) -> None:
        """月亮應對應白化（albedo）階段。"""
        c = PLANET_CORRESPONDENCES["moon"]
        assert c.alchemical_stage.lower() == "albedo"

    def test_sun_maps_to_citrinitas(self) -> None:
        """太陽應對應黃化（citrinitas）階段。"""
        c = PLANET_CORRESPONDENCES["sun"]
        assert c.alchemical_stage.lower() == "citrinitas"

    def test_jupiter_maps_to_rubedo(self) -> None:
        """木星應對應赤化（rubedo）階段。"""
        c = PLANET_CORRESPONDENCES["jupiter"]
        assert c.alchemical_stage.lower() == "rubedo"

    def test_mars_maps_to_nigredo(self) -> None:
        """火星應對應黑化（nigredo）階段。"""
        c = PLANET_CORRESPONDENCES["mars"]
        assert c.alchemical_stage.lower() == "nigredo"

    @pytest.mark.parametrize("stage_key", ["nigredo", "albedo", "citrinitas", "rubedo"])
    def test_stage_has_source(self, stage_key: str) -> None:
        """每個煉金階段應有文獻來源。"""
        stage = ALCHEMICAL_STAGES[stage_key]
        assert stage.source.strip() != ""

    @pytest.mark.parametrize("stage_key", ["nigredo", "albedo", "citrinitas", "rubedo"])
    def test_stage_has_planets(self, stage_key: str) -> None:
        """每個煉金階段應關聯至少一顆行星。"""
        stage = ALCHEMICAL_STAGES[stage_key]
        assert len(stage.planets) >= 1

    @pytest.mark.parametrize("stage_key", ["nigredo", "albedo", "citrinitas", "rubedo"])
    def test_stage_names_not_empty(self, stage_key: str) -> None:
        """每個煉金階段應有非空的名稱。"""
        stage = ALCHEMICAL_STAGES[stage_key]
        assert stage.name_la.strip() != ""
        assert stage.name_zh.strip() != ""

    def test_stage_reading_in_ruling_sign(self) -> None:
        """行星在統治宮時，主導行星應為該行星。"""
        # 太陽在獅子座（統治宮，score=5），其他行星在中性位置 (score=1)
        # 太陽應為主導行星，且對應 citrinitas 階段
        result = compute_reading({
            "sun": 125.0,    # 獅子座統治宮
            "moon": 200.0,
            "mars": 200.0,
            "mercury": 200.0,
            "jupiter": 200.0,
            "venus": 200.0,
            "saturn": 200.0,
        })
        assert result.dominant_planet == "sun"
        assert result.alchemical_stage_key == "citrinitas"


# ─────────────────────────────────────────────────────────────────────────────
# 5. 物質印記說測試
# ─────────────────────────────────────────────────────────────────────────────

class TestSignatures:
    """測試物質印記說（Signatura Rerum）資料完整性。"""

    def test_all_seven_planets_have_signatures(self) -> None:
        """所有 7 顆行星應有物質印記說。"""
        assert len(PLANET_SIGNATURES) == 7
        for key in PLANET_KEYS:
            assert key in PLANET_SIGNATURES

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_get_planet_signature_returns_non_none(self, planet_key: str) -> None:
        """get_planet_signature() 應為所有行星返回非 None 值。"""
        sig = get_planet_signature(planet_key)
        assert sig is not None

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_signature_text_not_empty(self, planet_key: str) -> None:
        """物質印記說文本不應為空。"""
        sig = get_planet_signature(planet_key)
        assert sig is not None
        assert sig.signature_text.strip() != ""
        assert sig.signature_text_zh.strip() != ""

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_get_signature_text_zh_not_empty(self, planet_key: str) -> None:
        """get_signature_text_zh() 應返回非空字串。"""
        text = get_signature_text_zh(planet_key)
        assert text.strip() != ""

    def test_invalid_planet_returns_none(self) -> None:
        """無效的行星鍵名應返回 None。"""
        sig = get_planet_signature("invalid_planet")
        assert sig is None

    def test_invalid_planet_signature_text_returns_empty(self) -> None:
        """無效的行星鍵名的印記說應返回空字串。"""
        text = get_signature_text_zh("invalid_planet")
        assert text == ""

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_signature_has_visual_signs(self, planet_key: str) -> None:
        """每個印記說應有視覺印記特徵（至少 2 個）。"""
        sig = get_planet_signature(planet_key)
        assert sig is not None
        assert len(sig.visual_signs) >= 2
        assert len(sig.visual_signs_zh) >= 2

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_signature_has_source(self, planet_key: str) -> None:
        """每個印記說應有文獻來源。"""
        sig = get_planet_signature(planet_key)
        assert sig is not None
        assert sig.source.strip() != ""

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_signature_has_healing_principle(self, planet_key: str) -> None:
        """每個印記說應有治療原則。"""
        sig = get_planet_signature(planet_key)
        assert sig is not None
        assert sig.healing_principle.strip() != ""
        assert sig.healing_principle_zh.strip() != ""


# ─────────────────────────────────────────────────────────────────────────────
# 6. 尊貴評分計算測試
# ─────────────────────────────────────────────────────────────────────────────

class TestDignityScoring:
    """測試行星尊貴評分計算邏輯。"""

    def test_sun_ruling_sign_score_five(self) -> None:
        """太陽在獅子座（統治宮）應得 5 分。"""
        score = _compute_dignity_score("sun", 125.0)  # 獅子座 120–150°
        assert score == 5

    def test_moon_ruling_sign_score_five(self) -> None:
        """月亮在巨蟹座（統治宮）應得 5 分。"""
        score = _compute_dignity_score("moon", 95.0)  # 巨蟹座 90–120°
        assert score == 5

    def test_saturn_ruling_sign_score_five(self) -> None:
        """土星在摩羯座（統治宮）應得 5 分。"""
        score = _compute_dignity_score("saturn", 280.0)  # 摩羯座 270–300°
        assert score == 5

    def test_neutral_position_score_one(self) -> None:
        """太陽在中性位置應得 1 分（最低值）。"""
        score = _compute_dignity_score("sun", 45.0)  # 金牛座
        assert score == 1

    def test_longitude_to_sign_index_correct(self) -> None:
        """黃道度數到星座索引轉換應正確。"""
        assert longitude_to_sign_index(0.0) == 0    # 白羊座
        assert longitude_to_sign_index(30.0) == 1   # 金牛座
        assert longitude_to_sign_index(90.0) == 3   # 巨蟹座
        assert longitude_to_sign_index(120.0) == 4  # 獅子座
        assert longitude_to_sign_index(359.9) == 11 # 雙魚座


# ─────────────────────────────────────────────────────────────────────────────
# 7. 主導行星選取邏輯
# ─────────────────────────────────────────────────────────────────────────────

class TestDominantPlanetSelection:
    """測試主導行星選取邏輯。"""

    def test_highest_dignity_score_wins(self) -> None:
        """尊貴評分最高的行星應被選為主導行星。"""
        scores = {
            "sun": 5, "moon": 1, "mars": 1,
            "mercury": 1, "jupiter": 1, "venus": 1, "saturn": 1,
        }
        dominant = _find_dominant_planet(scores)
        assert dominant == "sun"

    def test_chaldean_tiebreak(self) -> None:
        """同分時依 Chaldean 順序（土星優先）。"""
        # 土星和太陽同分，依 Chaldean 順序土星應獲勝
        scores = {
            "sun": 5, "moon": 1, "mars": 1,
            "mercury": 1, "jupiter": 1, "venus": 1, "saturn": 5,
        }
        dominant = _find_dominant_planet(scores)
        assert dominant == "saturn"

    def test_all_neutral_selects_chaldean_first(self) -> None:
        """所有行星同分時，應選 Chaldean 序最優先（土星）。"""
        scores = {key: 1 for key in PLANET_KEYS}
        dominant = _find_dominant_planet(scores)
        assert dominant == "saturn"

    def test_multiple_rulers_choose_highest(self) -> None:
        """多顆行星在統治宮時，選取評分最高者（分數相同時 Chaldean 優先）。"""
        result = compute_reading({
            "sun": 125.0,     # 獅子座 — score 5
            "moon": 95.0,     # 巨蟹座 — score 5
            "mars": 5.0,      # 白羊座 — score 5
            "mercury": 65.0,  # 雙子座 — score 5
            "jupiter": 245.0, # 射手座 — score 5
            "venus": 185.0,   # 天秤座 — score 5
            "saturn": 275.0,  # 摩羯座 — score 5
        })
        # 所有行星評分相同，Chaldean 順序 → 土星獲勝
        assert result.dominant_planet == "saturn"


# ─────────────────────────────────────────────────────────────────────────────
# 8. 解讀文本測試
# ─────────────────────────────────────────────────────────────────────────────

class TestInterpretations:
    """測試解讀文本庫完整性。"""

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_planet_reading_zh_not_empty(self, planet_key: str) -> None:
        """每顆行星應有非空的中文解讀。"""
        text = get_planet_reading(planet_key, "zh")
        assert text.strip() != ""

    @pytest.mark.parametrize("planet_key", PLANET_KEYS)
    def test_planet_reading_en_not_empty(self, planet_key: str) -> None:
        """每顆行星應有非空的英文解讀。"""
        text = get_planet_reading(planet_key, "en")
        assert text.strip() != ""

    @pytest.mark.parametrize("stage_key", ["nigredo", "albedo", "citrinitas", "rubedo"])
    def test_stage_reading_zh_not_empty(self, stage_key: str) -> None:
        """每個煉金階段應有非空的中文解讀。"""
        text = get_stage_reading(stage_key, "zh")
        assert text.strip() != ""

    @pytest.mark.parametrize("stage_key", ["nigredo", "albedo", "citrinitas", "rubedo"])
    def test_stage_reading_en_not_empty(self, stage_key: str) -> None:
        """每個煉金階段應有非空的英文解讀。"""
        text = get_stage_reading(stage_key, "en")
        assert text.strip() != ""

    def test_invalid_planet_reading_returns_empty(self) -> None:
        """無效的行星鍵名應返回空字串。"""
        text = get_planet_reading("invalid_planet", "zh")
        assert text == ""


# ─────────────────────────────────────────────────────────────────────────────
# 9. PlanetProfile 欄位完整性
# ─────────────────────────────────────────────────────────────────────────────

class TestPlanetProfile:
    """測試 PlanetProfile 資料類別欄位完整性。"""

    @pytest.fixture
    def sample_reading(self) -> AlchemicalReading:
        """返回樣本解讀結果。"""
        return compute_reading(_SAMPLE_LONGITUDES_DIGNITY)

    def test_all_profiles_have_correct_type(self, sample_reading: AlchemicalReading) -> None:
        """所有輪廓應為 PlanetProfile 類型。"""
        for profile in sample_reading.planetary_profiles:
            assert isinstance(profile, PlanetProfile)

    def test_profiles_cover_all_planets(self, sample_reading: AlchemicalReading) -> None:
        """輪廓應覆蓋所有 7 顆行星。"""
        keys = {p.planet_key for p in sample_reading.planetary_profiles}
        assert keys == set(PLANET_KEYS)

    def test_profile_longitude_preserved(self, sample_reading: AlchemicalReading) -> None:
        """輪廓應保留原始黃道度數。"""
        for profile in sample_reading.planetary_profiles:
            expected = _SAMPLE_LONGITUDES_DIGNITY.get(profile.planet_key, 0.0)
            assert abs(profile.longitude - expected) < 1e-9

    def test_profile_has_source(self, sample_reading: AlchemicalReading) -> None:
        """每個輪廓應有文獻來源。"""
        for profile in sample_reading.planetary_profiles:
            assert profile.source.strip() != ""

    def test_profile_has_reading_zh(self, sample_reading: AlchemicalReading) -> None:
        """每個輪廓應有中文解讀。"""
        for profile in sample_reading.planetary_profiles:
            assert profile.reading_zh.strip() != ""
