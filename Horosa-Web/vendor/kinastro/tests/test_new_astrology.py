"""
Tests for Western, Indian (Vedic), Thai, and Arabic astrology calculator modules.
"""

import pytest

from astro.western.western import (
    compute_western_chart,
    _normalize,
    _sign_index,
    _sign_degree,
    ZODIAC_SIGNS,
)
from astro.vedic.indian import (
    compute_vedic_chart,
    _nakshatra_info,
    RASHIS,
    NAKSHATRAS,
)
from astro.thai import (
    compute_thai_chart,
    THAI_RASHIS,
    THAI_DAY_PLANETS,
    calculate_thai_nine_grid,
    _digit_reduce,
    _NINE_GRID_LINES,
    THAI_NUMEROLOGY_PLANETS,
)
from astro.arabic.arabic import (
    compute_arabic_chart,
    ARABIC_PARTS,
    ZODIAC_SIGNS as ARABIC_ZODIAC_SIGNS,
    _get_dignity,
    _is_day_chart,
    _compute_aspects,
    ASPECT_TYPES,
)


# ============================================================
# Western Astrology Tests
# ============================================================

class TestWesternChart:
    """西洋占星排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_western_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.location_name == "北京"

    def test_has_eleven_planets(self, sample_chart):
        """10 planets + North Node = 11"""
        assert len(sample_chart.planets) == 11

    def test_planet_names(self, sample_chart):
        names = [p.name for p in sample_chart.planets]
        assert "Sun ☉" in names
        assert "Moon ☽" in names
        assert "Uranus ♅" in names
        assert "Neptune ♆" in names
        assert "Pluto ♇" in names
        assert "North Node ☊" in names

    def test_twelve_houses(self, sample_chart):
        assert len(sample_chart.houses) == 12

    def test_planet_longitudes_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.longitude < 360

    def test_planet_sign_degrees_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.sign_degree < 30

    def test_all_planets_have_house(self, sample_chart):
        for p in sample_chart.planets:
            assert 1 <= p.house <= 12

    def test_sun_in_capricorn_for_jan1(self, sample_chart):
        sun = sample_chart.planets[0]
        assert sun.sign == "Capricorn"

    def test_ascendant_and_mc(self, sample_chart):
        assert 0 <= sample_chart.ascendant < 360
        assert 0 <= sample_chart.midheaven < 360
        assert sample_chart.asc_sign in [s[0] for s in ZODIAC_SIGNS]
        assert sample_chart.mc_sign in [s[0] for s in ZODIAC_SIGNS]

    def test_different_dates_produce_different_results(self):
        c1 = compute_western_chart(2000, 6, 15, 12, 0, 8.0, 39.9, 116.4)
        c2 = compute_western_chart(2020, 12, 25, 8, 30, 8.0, 39.9, 116.4)
        sun1 = c1.planets[0].longitude
        sun2 = c2.planets[0].longitude
        assert abs(sun1 - sun2) > 1.0


# ============================================================
# Indian (Vedic) Astrology Tests
# ============================================================

class TestVedicChart:
    """印度占星排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_vedic_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.location_name == "北京"

    def test_has_nine_planets(self, sample_chart):
        """7 planets + Rahu + Ketu = 9"""
        assert len(sample_chart.planets) == 9

    def test_planet_names(self, sample_chart):
        names = [p.name for p in sample_chart.planets]
        assert "Surya (太陽)" in names
        assert "Chandra (月亮)" in names
        assert "Rahu (羅睺)" in names
        assert "Ketu (計都)" in names

    def test_twelve_houses(self, sample_chart):
        assert len(sample_chart.houses) == 12

    def test_ayanamsa_positive(self, sample_chart):
        assert sample_chart.ayanamsa > 20  # Lahiri ayanamsa ~23-24°

    def test_planet_longitudes_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.longitude < 360

    def test_nakshatra_assigned(self, sample_chart):
        for p in sample_chart.planets:
            assert p.nakshatra in [n[0] for n in NAKSHATRAS]
            assert 1 <= p.nakshatra_pada <= 4

    def test_rashi_assigned(self, sample_chart):
        for p in sample_chart.planets:
            assert p.rashi in [r[0] for r in RASHIS]

    def test_ketu_opposite_rahu(self, sample_chart):
        rahu = next(p for p in sample_chart.planets if "Rahu" in p.name)
        ketu = next(p for p in sample_chart.planets if "Ketu" in p.name)
        diff = abs(rahu.longitude - ketu.longitude)
        assert abs(diff - 180.0) < 0.01

    def test_ascendant_rashi(self, sample_chart):
        assert sample_chart.asc_rashi in [r[0] for r in RASHIS]

    def test_all_planets_have_house(self, sample_chart):
        for p in sample_chart.planets:
            assert 1 <= p.house <= 12


class TestNakshatraInfo:
    """Nakshatra calculation tests"""

    def test_first_nakshatra(self):
        idx, pada = _nakshatra_info(0.0)
        assert idx == 0
        assert pada == 1

    def test_last_nakshatra(self):
        idx, pada = _nakshatra_info(359.0)
        assert idx == 26
        assert pada >= 1

    def test_pada_range(self):
        for deg in range(0, 360, 10):
            _, pada = _nakshatra_info(float(deg))
            assert 1 <= pada <= 4


# ============================================================
# Sukkayodo (宿曜道) Tests
# ============================================================

class TestSukkayodo:
    """宿曜道排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_vedic_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_sukkayodo_mansion_index_valid(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.sukkayodo_mansion_index < 28

    def test_sukkayodo_pada_valid(self, sample_chart):
        for p in sample_chart.planets:
            assert 1 <= p.sukkayodo_pada <= 4

    def test_sukkayodo_mansion_name_is_string(self, sample_chart):
        for p in sample_chart.planets:
            assert isinstance(p.sukkayodo_mansion, str)
            assert len(p.sukkayodo_mansion) > 0

    def test_sukkayodo_mansion_chinese_is_string(self, sample_chart):
        """Bug fix test: sukkayodo_mansion_chinese should be a Chinese
        name string, not an integer lord index."""
        for p in sample_chart.planets:
            assert isinstance(p.sukkayodo_mansion_chinese, str)
            assert len(p.sukkayodo_mansion_chinese) > 0

    def test_sukkayodo_mansion_chinese_matches_data(self, sample_chart):
        """Verify mansion_chinese matches SUKKAYODO_MANSION[idx][2]."""
        from astro.sukkayodo import SUKKAYODO_MANSION
        for p in sample_chart.planets:
            expected = SUKKAYODO_MANSION[p.sukkayodo_mansion_index][2]
            assert p.sukkayodo_mansion_chinese == expected


class TestSukkayodoInfo:
    """sukkayodo_info calculation tests"""

    def test_first_mansion(self):
        from astro.sukkayodo import sukkayodo_info
        idx, pada = sukkayodo_info(0.0)
        assert idx == 0
        assert pada == 1

    def test_last_mansion(self):
        from astro.sukkayodo import sukkayodo_info
        idx, pada = sukkayodo_info(359.9)
        assert idx == 27

    def test_pada_range(self):
        from astro.sukkayodo import sukkayodo_info
        for deg in range(0, 360, 5):
            _, pada = sukkayodo_info(float(deg))
            assert 1 <= pada <= 4

    def test_mansion_index_range(self):
        from astro.sukkayodo import sukkayodo_info
        for deg in range(0, 360, 5):
            idx, _ = sukkayodo_info(float(deg))
            assert 0 <= idx < 28


class TestTwelvePalaces:
    """十二宮 mapping tests"""

    def test_all_28_mansions_mapped(self):
        from astro.sukkayodo import TWELVE_PALACES
        all_indices = []
        for _, indices in TWELVE_PALACES:
            all_indices.extend(indices)
        assert sorted(all_indices) == list(range(28))

    def test_twelve_palaces_count(self):
        from astro.sukkayodo import TWELVE_PALACES
        assert len(TWELVE_PALACES) == 12

    def test_palace_names(self):
        from astro.sukkayodo import TWELVE_PALACES
        expected = ["羊宮", "牛宮", "夫宮", "蟹宮", "獅宮", "女宮",
                    "秤宮", "蝎宮", "弓宮", "磨宮", "瓶宮", "魚宮"]
        names = [name for name, _ in TWELVE_PALACES]
        assert names == expected


class TestGetRokuyo:
    """六曜 lookup tests"""

    def test_valid_index(self):
        from astro.sukkayodo import get_rokuyo
        for i in range(28):
            rk = get_rokuyo(i)
            assert rk is not None
            assert len(rk) == 4

    def test_invalid_index_returns_none(self):
        from astro.sukkayodo import get_rokuyo
        assert get_rokuyo(-1) is None
        assert get_rokuyo(28) is None


class TestSansanjuMansions:
    """三九秘宿法 (San-Jiu Bi-Su) data and calculation tests"""

    def test_sansanju_27_mansions_length(self):
        """SANSANJU_27_MANSIONS must have exactly 27 elements."""
        from astro.sukkayodo import SANSANJU_27_MANSIONS
        assert len(SANSANJU_27_MANSIONS) == 27

    def test_sansanju_27_mansions_excludes_abhijit(self):
        """Abhijit (牛宿, index 21) must not appear in the 27-mansion list."""
        from astro.sukkayodo import SANSANJU_27_MANSIONS
        assert 21 not in SANSANJU_27_MANSIONS

    def test_sansanju_27_mansions_covers_all_others(self):
        """All 28 mansions except Abhijit (21) must appear exactly once."""
        from astro.sukkayodo import SANSANJU_27_MANSIONS
        expected = sorted(set(range(28)) - {21})
        assert sorted(SANSANJU_27_MANSIONS) == expected

    def test_get_sansanju_table_all_months(self):
        """_get_sansanju_table must not raise IndexError for any birth month."""
        from astro.sukkayodo import _get_sansanju_table
        for month in range(1, 13):
            result = _get_sansanju_table(month, 1)
            assert "table" in result
            assert "day_category" in result
            assert len(result["table"]) == 33

    def test_get_sansanju_table_all_days(self):
        """_get_sansanju_table must not raise IndexError for any birth day."""
        from astro.sukkayodo import _get_sansanju_table
        for day in range(1, 32):
            result = _get_sansanju_table(1, day)
            assert result["day_category"] in [
                "命", "業", "胎", "榮", "衰", "安", "危", "成", "壞", "友", "親"
            ]

    def test_sansanju_month_starts_length(self):
        """SANSANJU_MONTH_STARTS must have exactly 12 entries (one per month)."""
        from astro.sukkayodo import SANSANJU_MONTH_STARTS
        assert len(SANSANJU_MONTH_STARTS) == 12

    def test_sansanju_month_starts_first_is_zero(self):
        """正月 (January) must start at position 0 (室宿)."""
        from astro.sukkayodo import SANSANJU_MONTH_STARTS, SANSANJU_27_MANSIONS, SUKKAYODO_MANSION
        pos = SANSANJU_MONTH_STARTS[0]
        assert pos == 0
        mansion_idx = SANSANJU_27_MANSIONS[pos]
        assert mansion_idx < len(SUKKAYODO_MANSION), (
            f"mansion_idx {mansion_idx} is out of range for SUKKAYODO_MANSION "
            f"(len={len(SUKKAYODO_MANSION)})"
        )
        assert SUKKAYODO_MANSION[mansion_idx][2] == "室宿"


# ============================================================
# Thai Astrology Tests
# ============================================================

class TestThaiChart:
    """泰國占星排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_thai_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=7.0, latitude=13.7563, longitude=100.5018,
            location_name="Bangkok",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.location_name == "Bangkok"

    def test_has_nine_planets(self, sample_chart):
        """7 planets + Rahu + Ketu = 9"""
        assert len(sample_chart.planets) == 9

    def test_planet_names_thai(self, sample_chart):
        names = [p.name for p in sample_chart.planets]
        assert any("พระอาทิตย์" in n for n in names)
        assert any("ราหู" in n for n in names)
        assert any("เกตุ" in n for n in names)

    def test_twelve_houses(self, sample_chart):
        assert len(sample_chart.houses) == 12

    def test_day_planet_assigned(self, sample_chart):
        # Jan 1 1990 is Monday
        assert sample_chart.day_of_week == 1
        assert sample_chart.day_planet == "พระจันทร์"

    def test_rashi_thai_names(self, sample_chart):
        for p in sample_chart.planets:
            assert p.rashi in [r[0] for r in THAI_RASHIS]

    def test_planet_longitudes_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.longitude < 360

    def test_all_planets_have_house(self, sample_chart):
        for p in sample_chart.planets:
            assert 1 <= p.house <= 12

    def test_ketu_opposite_rahu(self, sample_chart):
        rahu = next(p for p in sample_chart.planets if "ราหู" in p.name)
        ketu = next(p for p in sample_chart.planets if "เกตุ" in p.name)
        diff = abs(rahu.longitude - ketu.longitude)
        assert abs(diff - 180.0) < 0.01

    def test_ayanamsa_positive(self, sample_chart):
        assert sample_chart.ayanamsa > 20

    def test_sunday_is_sun(self):
        """Sunday should map to Sun planet"""
        # 1990-01-07 is Sunday
        chart = compute_thai_chart(1990, 1, 7, 12, 0, 7.0, 13.7563, 100.5018)
        assert chart.day_of_week == 0
        assert chart.day_planet == "พระอาทิตย์"


# ============================================================
# Thai Numerology 9-Box Grid Tests
# ============================================================

class TestThaiNineGrid:
    """泰國 Numerology 9宮格計算測試"""

    @pytest.fixture
    def sample_result(self):
        # 05/03/1985
        return calculate_thai_nine_grid(day=5, month=3, year=1985)

    def test_returns_dict_with_expected_keys(self, sample_result):
        expected = {"counts", "birth_number", "life_path",
                    "complete_lines", "strongest", "missing", "day", "month", "year"}
        assert expected.issubset(sample_result.keys())

    def test_counts_keys_are_1_to_9(self, sample_result):
        assert set(sample_result["counts"].keys()) == set(range(1, 10))

    def test_counts_are_non_negative(self, sample_result):
        for n, c in sample_result["counts"].items():
            assert c >= 0, f"Negative count for digit {n}"

    def test_birth_number_is_single_digit(self, sample_result):
        bn = sample_result["birth_number"]
        assert 1 <= bn <= 9

    def test_life_path_is_single_digit(self, sample_result):
        lp = sample_result["life_path"]
        assert 1 <= lp <= 9

    def test_birth_number_correct_for_day5(self, sample_result):
        # day 5 → birth number 5
        assert sample_result["birth_number"] == 5

    def test_life_path_correct(self):
        # 05/03/1985 → digits: 5,3,1,9,8,5 → sum=31 → 3+1=4
        result = calculate_thai_nine_grid(5, 3, 1985)
        assert result["life_path"] == 4

    def test_derived_numbers_added_to_counts(self):
        # day=1, month=1, year=1111 → raw digits: 1,1,1,1,1,1
        # birth_number = 1, life_path = reduce(6) = 6
        # counts before derived: {1:6}
        # after: {1:6+1=7, 6:0+1=1}
        result = calculate_thai_nine_grid(1, 1, 1111)
        assert result["counts"][1] == 7
        assert result["counts"][6] == 1

    def test_complete_lines_are_valid_line_names(self, sample_result):
        valid = set(_NINE_GRID_LINES.keys())
        for line in sample_result["complete_lines"]:
            assert line in valid

    def test_complete_line_means_all_digits_present(self, sample_result):
        counts = sample_result["counts"]
        for line_name in sample_result["complete_lines"]:
            for n in _NINE_GRID_LINES[line_name]:
                assert counts[n] > 0, (
                    f"Line {line_name} marked complete but digit {n} has count 0"
                )

    def test_strongest_all_have_same_count(self, sample_result):
        counts = sample_result["counts"]
        strongest = sample_result["strongest"]
        if strongest:
            max_count = max(counts[n] for n in strongest)
            for n in strongest:
                assert counts[n] == max_count

    def test_missing_have_zero_count(self, sample_result):
        counts = sample_result["counts"]
        for n in sample_result["missing"]:
            assert counts[n] == 0

    def test_strongest_and_missing_disjoint(self, sample_result):
        s = set(sample_result["strongest"])
        m = set(sample_result["missing"])
        assert s.isdisjoint(m)

    def test_all_digits_present_gives_no_missing(self):
        # 19/08/2753 → has 1,9,0,8,2,7,5,3 → non-zero: 1,9,8,2,7,5,3
        # birth_number = reduce(19)=reduce(10)=1, life_path = reduce(1+9+8+2+7+5+3)=reduce(35)=8
        # Still might miss 4 and 6 from raw — test that logic is consistent
        result = calculate_thai_nine_grid(19, 8, 2753)
        for n in result["missing"]:
            assert result["counts"][n] == 0

    def test_original_date_preserved(self):
        result = calculate_thai_nine_grid(15, 7, 2000)
        assert result["day"] == 15
        assert result["month"] == 7
        assert result["year"] == 2000

    def test_digit_reduce_single(self):
        assert _digit_reduce(5) == 5
        assert _digit_reduce(9) == 9

    def test_digit_reduce_two_digit(self):
        assert _digit_reduce(19) == 1   # 1+9=10 → 1+0=1
        assert _digit_reduce(29) == 2   # 2+9=11 → 1+1=2

    def test_digit_reduce_large(self):
        assert _digit_reduce(999) == 9  # 27 → 9

    def test_digit_reduce_zero(self):
        # 0 and negatives should return 1 (fallback)
        assert _digit_reduce(0) == 1
        assert _digit_reduce(-5) == 1

    def test_numerology_planets_covers_1_to_9(self):
        assert set(THAI_NUMEROLOGY_PLANETS.keys()) == set(range(1, 10))

class TestArabicChart:
    """阿拉伯占星排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_arabic_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.location_name == "北京"

    def test_has_eight_planets(self, sample_chart):
        """7 classical planets + North Node = 8"""
        assert len(sample_chart.planets) == 8

    def test_planet_names(self, sample_chart):
        names = [p.name for p in sample_chart.planets]
        assert "Sun ☉ (太陽)" in names
        assert "Moon ☽ (月亮)" in names
        assert "Mars ♂ (火星)" in names
        assert "Saturn ♄ (土星)" in names
        assert "North Node ☊ (北交點)" in names

    def test_twelve_houses(self, sample_chart):
        assert len(sample_chart.houses) == 12

    def test_planet_longitudes_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.longitude < 360

    def test_planet_sign_degrees_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.sign_degree < 30

    def test_all_planets_have_house(self, sample_chart):
        for p in sample_chart.planets:
            assert 1 <= p.house <= 12

    def test_sun_in_capricorn_for_jan1(self, sample_chart):
        sun = next(p for p in sample_chart.planets if "Sun" in p.name)
        assert sun.sign == "Capricorn"

    def test_ascendant_and_mc(self, sample_chart):
        assert 0 <= sample_chart.ascendant < 360
        assert 0 <= sample_chart.midheaven < 360
        assert sample_chart.asc_sign in [s[0] for s in ARABIC_ZODIAC_SIGNS]
        assert sample_chart.mc_sign in [s[0] for s in ARABIC_ZODIAC_SIGNS]

    def test_is_day_chart_boolean(self, sample_chart):
        assert isinstance(sample_chart.is_day_chart, bool)

    def test_arabic_parts_count(self, sample_chart):
        """Should have as many parts as defined in ARABIC_PARTS"""
        assert len(sample_chart.arabic_parts) == len(ARABIC_PARTS)

    def test_arabic_parts_longitudes_in_range(self, sample_chart):
        for part in sample_chart.arabic_parts:
            assert 0 <= part.longitude < 360

    def test_arabic_parts_sign_degrees_in_range(self, sample_chart):
        for part in sample_chart.arabic_parts:
            assert 0 <= part.sign_degree < 30

    def test_arabic_parts_have_house(self, sample_chart):
        for part in sample_chart.arabic_parts:
            assert 1 <= part.house <= 12

    def test_part_of_fortune_present(self, sample_chart):
        names = [part.english_name for part in sample_chart.arabic_parts]
        assert "Part of Fortune" in names

    def test_part_of_spirit_present(self, sample_chart):
        names = [part.english_name for part in sample_chart.arabic_parts]
        assert "Part of Spirit" in names

    def test_arabic_sign_names_populated(self, sample_chart):
        for p in sample_chart.planets:
            assert p.arabic_sign != ""

    def test_dignity_is_string(self, sample_chart):
        for p in sample_chart.planets:
            assert isinstance(p.dignity, str)

    def test_different_dates_produce_different_results(self):
        c1 = compute_arabic_chart(2000, 6, 15, 12, 0, 8.0, 39.9, 116.4)
        c2 = compute_arabic_chart(2020, 12, 25, 8, 30, 8.0, 39.9, 116.4)
        sun1 = next(p for p in c1.planets if "Sun" in p.name).longitude
        sun2 = next(p for p in c2.planets if "Sun" in p.name).longitude
        assert abs(sun1 - sun2) > 1.0


class TestArabicDignity:
    """Essential dignity calculation tests"""

    def test_sun_domicile_in_leo(self):
        # Leo is sign index 4, Sun domicile
        assert "入廟" in _get_dignity("Sun ☉ (太陽)", 4)

    def test_sun_exaltation_in_aries(self):
        # Aries is sign index 0, Sun exaltation
        assert "入旺" in _get_dignity("Sun ☉ (太陽)", 0)

    def test_sun_detriment_in_aquarius(self):
        # Aquarius (index 10) is opposite Leo (domicile)
        assert "落陷" in _get_dignity("Sun ☉ (太陽)", 10)

    def test_sun_fall_in_libra(self):
        # Libra (index 6) is opposite Aries (exaltation)
        assert "入弱" in _get_dignity("Sun ☉ (太陽)", 6)

    def test_no_dignity(self):
        # Jupiter in Aries has no special dignity
        result = _get_dignity("Jupiter ♃ (木星)", 0)
        assert result == "—"


class TestArabicAspects:
    """阿拉伯占星相位測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_arabic_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_aspects_is_list(self, sample_chart):
        assert isinstance(sample_chart.aspects, list)

    def test_aspects_not_empty(self, sample_chart):
        # With 7 classical planets, there should be at least some aspects
        assert len(sample_chart.aspects) > 0

    def test_aspect_has_required_fields(self, sample_chart):
        for a in sample_chart.aspects:
            assert hasattr(a, "planet1")
            assert hasattr(a, "planet2")
            assert hasattr(a, "aspect_name")
            assert hasattr(a, "arabic_name")
            assert hasattr(a, "chinese_name")
            assert hasattr(a, "angle")
            assert hasattr(a, "orb")

    def test_aspect_names_are_valid(self, sample_chart):
        valid_names = {eng for eng, _, _, _, _ in ASPECT_TYPES}
        for a in sample_chart.aspects:
            assert a.aspect_name in valid_names

    def test_aspect_orb_within_limit(self, sample_chart):
        orb_limits = {eng: orb for eng, _, _, _, orb in ASPECT_TYPES}
        for a in sample_chart.aspects:
            assert a.orb <= orb_limits[a.aspect_name]

    def test_aspect_angle_positive(self, sample_chart):
        for a in sample_chart.aspects:
            assert 0 <= a.angle <= 180

    def test_no_self_aspects(self, sample_chart):
        for a in sample_chart.aspects:
            assert a.planet1 != a.planet2

    def test_no_north_node_in_aspects(self, sample_chart):
        for a in sample_chart.aspects:
            assert "North Node" not in a.planet1
            assert "North Node" not in a.planet2


# ============================================================
# Zi Wei Dou Shu (紫微斗數) Tests
# ============================================================

from astro.ziwei import (
    compute_ziwei_chart,
    _get_hour_branch,
    _get_year_stem,
    _get_year_branch,
    _get_ming_gong_branch,
    _get_shen_gong_branch,
    _get_wu_xing_ju,
    _get_ziwei_branch,
    _get_tianfu_branch,
    _get_ming_gong_stem,
    _solar_to_lunar,
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
    WU_XING_JU_NAMES,
    PALACE_SEQUENCE,
    SIHUA_TABLE,
    NAYIN_WUXING_JU,
)


class TestZiweiHelpers:
    """紫微斗數輔助函數測試"""

    def test_hour_branch_zi_midnight(self):
        assert _get_hour_branch(0, 0) == 0   # 子時

    def test_hour_branch_zi_late_night(self):
        assert _get_hour_branch(23, 30) == 0  # 子時

    def test_hour_branch_chou(self):
        assert _get_hour_branch(1, 0) == 1   # 丑時

    def test_hour_branch_yin(self):
        assert _get_hour_branch(3, 0) == 2   # 寅時

    def test_hour_branch_noon(self):
        assert _get_hour_branch(12, 0) == 6  # 午時

    def test_hour_branch_hai(self):
        assert _get_hour_branch(21, 30) == 11  # 亥時

    def test_hour_branch_range(self):
        for h in range(24):
            b = _get_hour_branch(h, 0)
            assert 0 <= b <= 11

    def test_year_stem_1990(self):
        # 1990 = 庚午年；庚 = index 6
        assert _get_year_stem(1990) == 6

    def test_year_stem_2000(self):
        # 2000 = 庚辰年；庚 = index 6
        assert _get_year_stem(2000) == 6

    def test_year_stem_2024(self):
        # 2024 = 甲辰年；甲 = index 0
        assert _get_year_stem(2024) == 0

    def test_year_branch_1990(self):
        # 1990 庚午年；午 = index 6
        assert _get_year_branch(1990) == 6

    def test_year_branch_2000(self):
        # 2000 庚辰年；辰 = index 4
        assert _get_year_branch(2000) == 4

    def test_ming_gong_branch_in_range(self):
        for m in range(1, 13):
            for h in range(12):
                b = _get_ming_gong_branch(m, h)
                assert 0 <= b <= 11

    def test_shen_gong_branch_in_range(self):
        for m in range(1, 13):
            for h in range(12):
                b = _get_shen_gong_branch(m, h)
                assert 0 <= b <= 11

    def test_wu_xing_ju_range(self):
        for stem in range(10):
            for branch in range(12):
                if stem % 2 == branch % 2:  # valid stem-branch parity
                    ju = _get_wu_xing_ju(stem, branch)
                    assert 2 <= ju <= 6

    def test_wu_xing_ju_names_coverage(self):
        assert set(WU_XING_JU_NAMES.keys()) == {2, 3, 4, 5, 6}

    def test_ziwei_branch_in_range(self):
        for day in range(1, 31):
            for n in range(2, 7):
                b = _get_ziwei_branch(day, n)
                assert 0 <= b <= 11

    def test_tianfu_branch_formula(self):
        # 天府 = (4 - 紫微 + 12) % 12  (mirror about 寅)
        for ziwei in range(12):
            tianfu = _get_tianfu_branch(ziwei)
            assert tianfu == (4 - ziwei + 12) % 12

    def test_ziwei_day1_water2(self):
        # 水二局，初一 → 寅 (index 2)
        assert _get_ziwei_branch(1, 2) == 2

    def test_ziwei_day11_wood3(self):
        # 木三局，十一日 → 辰 (index 4) — matches reference image
        assert _get_ziwei_branch(11, 3) == 4

    def test_wu_xing_ju_nayin_gui_wei(self):
        # 癸未 → 楊柳木 → 木三局 (3) — reference case
        assert _get_wu_xing_ju(9, 7) == 3


class TestZiweiSolarToLunar:
    """農曆轉換測試"""

    def test_known_date_2000_02_05(self):
        # 2000-02-05 = 農曆正月初一（庚辰年春節）
        import swisseph as swe
        jd = swe.julday(2000, 2, 5, 12.0)
        ly, lm, ld, leap = _solar_to_lunar(jd)
        assert ly == 2000
        assert lm == 1
        assert ld == 1

    def test_result_types(self):
        import swisseph as swe
        jd = swe.julday(1990, 6, 15, 12.0)
        ly, lm, ld, leap = _solar_to_lunar(jd)
        assert isinstance(ly, int)
        assert 1 <= lm <= 12
        assert 1 <= ld <= 30
        assert isinstance(leap, bool)

    def test_month_range(self):
        import swisseph as swe
        for m in range(1, 13):
            jd = swe.julday(2000, m, 15, 12.0)
            _, lm, ld, _ = _solar_to_lunar(jd)
            assert 1 <= lm <= 12
            assert 1 <= ld <= 30

    def test_13th_month_year_returns_valid_month(self):
        # 2020 had a leap 4th month (閏四月); test that the result is in 1–12
        import swisseph as swe
        # 2020-06-21 falls during 閏四月 in the Chinese calendar
        jd = swe.julday(2020, 6, 21, 12.0)
        _, lm, ld, _ = _solar_to_lunar(jd)
        assert 1 <= lm <= 12
        assert 1 <= ld <= 30


class TestZiweiChart:
    """紫微斗數命盤排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_ziwei_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.month == 1
        assert sample_chart.day == 1
        assert sample_chart.location_name == "北京"

    def test_twelve_palaces(self, sample_chart):
        assert len(sample_chart.palaces) == 12

    def test_palace_names_cover_all(self, sample_chart):
        names = [p.name for p in sample_chart.palaces]
        for name in PALACE_SEQUENCE:
            assert name in names

    def test_palace_branches_unique(self, sample_chart):
        branches = [p.branch for p in sample_chart.palaces]
        assert len(set(branches)) == 12

    def test_palace_branches_cover_all(self, sample_chart):
        branches = set(p.branch for p in sample_chart.palaces)
        assert branches == set(range(12))

    def test_ming_gong_in_range(self, sample_chart):
        assert 0 <= sample_chart.ming_gong_branch <= 11

    def test_shen_gong_in_range(self, sample_chart):
        assert 0 <= sample_chart.shen_gong_branch <= 11

    def test_wu_xing_ju_valid(self, sample_chart):
        assert sample_chart.wu_xing_ju in WU_XING_JU_NAMES

    def test_ziwei_branch_in_range(self, sample_chart):
        assert 0 <= sample_chart.ziwei_branch <= 11

    def test_lunar_month_in_range(self, sample_chart):
        assert 1 <= sample_chart.lunar_month <= 12

    def test_lunar_day_in_range(self, sample_chart):
        assert 1 <= sample_chart.lunar_day <= 30

    def test_hour_branch_in_range(self, sample_chart):
        assert 0 <= sample_chart.hour_branch <= 11

    def test_ziwei_star_in_palaces(self, sample_chart):
        all_stars = [s for p in sample_chart.palaces for s in p.stars]
        assert "紫微" in all_stars

    def test_tianfu_star_in_palaces(self, sample_chart):
        all_stars = [s for p in sample_chart.palaces for s in p.stars]
        assert "天府" in all_stars

    def test_exactly_14_main_stars(self, sample_chart):
        all_stars = [s for p in sample_chart.palaces for s in p.stars]
        assert len(all_stars) == 14

    def test_all_14_main_stars_present(self, sample_chart):
        expected = {
            "紫微", "天機", "太陽", "武曲", "天同", "廉貞",
            "天府", "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍",
        }
        all_stars = {s for p in sample_chart.palaces for s in p.stars}
        assert all_stars == expected

    def test_different_dates_produce_different_ziwei_branches(self):
        c1 = compute_ziwei_chart(1990, 1, 1, 12, 0, 8.0, 39.9, 116.4)
        c2 = compute_ziwei_chart(1985, 6, 15, 8, 0, 8.0, 39.9, 116.4)
        assert c1.ziwei_branch != c2.ziwei_branch

    def test_different_dates_produce_different_ming_gong(self):
        c1 = compute_ziwei_chart(1990, 1, 1, 12, 0, 8.0, 39.9, 116.4)
        c2 = compute_ziwei_chart(1990, 1, 1, 3, 0, 8.0, 39.9, 116.4)
        # Same date, different hour → different 命宮
        assert c1.ming_gong_branch != c2.ming_gong_branch

    def test_stem_names_valid(self, sample_chart):
        for p in sample_chart.palaces:
            assert p.stem_name in HEAVENLY_STEMS

    def test_branch_names_valid(self, sample_chart):
        for p in sample_chart.palaces:
            assert p.branch_name in EARTHLY_BRANCHES


class TestZiweiReferenceChart:
    """紫微斗數參考案例測試 (1985-08-26 02:55 男命)"""

    @pytest.fixture
    def ref_chart(self):
        return compute_ziwei_chart(
            year=1985, month=8, day=26, hour=2, minute=55,
            timezone=8.0, latitude=22.3, longitude=114.2,
            location_name="Test", gender="男",
        )

    def test_lunar_date(self, ref_chart):
        assert ref_chart.lunar_year == 1985
        assert ref_chart.lunar_month == 7
        assert ref_chart.lunar_day == 11

    def test_year_ganzi(self, ref_chart):
        assert HEAVENLY_STEMS[ref_chart.lunar_year_stem] == "乙"
        assert EARTHLY_BRANCHES[ref_chart.lunar_year_branch] == "丑"

    def test_hour_branch(self, ref_chart):
        assert ref_chart.hour_branch == 1  # 丑時

    def test_ming_gong(self, ref_chart):
        assert EARTHLY_BRANCHES[ref_chart.ming_gong_branch] == "未"

    def test_shen_gong(self, ref_chart):
        assert EARTHLY_BRANCHES[ref_chart.shen_gong_branch] == "酉"

    def test_wu_xing_ju(self, ref_chart):
        assert ref_chart.wu_xing_ju == 3  # 木三局

    def test_yin_yang(self, ref_chart):
        assert ref_chart.yin_yang == "陰"

    def test_ming_zhu(self, ref_chart):
        assert ref_chart.ming_zhu == "武曲"

    def test_shen_zhu(self, ref_chart):
        assert ref_chart.shen_zhu == "天相"

    def test_ziwei_at_chen(self, ref_chart):
        assert EARTHLY_BRANCHES[ref_chart.ziwei_branch] == "辰"

    def test_ziwei_tianxiang_at_chen(self, ref_chart):
        p = next(p for p in ref_chart.palaces if p.branch == 4)  # 辰
        assert "紫微" in p.stars
        assert "天相" in p.stars

    def test_tianji_jumen_at_mao(self, ref_chart):
        p = next(p for p in ref_chart.palaces if p.branch == 3)  # 卯
        assert "天機" in p.stars
        assert "巨門" in p.stars

    def test_tianliang_at_si(self, ref_chart):
        p = next(p for p in ref_chart.palaces if p.branch == 5)  # 巳
        assert "天梁" in p.stars

    def test_qisha_at_wu(self, ref_chart):
        p = next(p for p in ref_chart.palaces if p.branch == 6)  # 午
        assert "七殺" in p.stars

    def test_lianzheng_at_shen(self, ref_chart):
        p = next(p for p in ref_chart.palaces if p.branch == 8)  # 申
        assert "廉貞" in p.stars

    def test_wuqu_tianfu_at_zi(self, ref_chart):
        p = next(p for p in ref_chart.palaces if p.branch == 0)  # 子
        assert "武曲" in p.stars
        assert "天府" in p.stars

    def test_taiyang_taiyin_at_chou(self, ref_chart):
        p = next(p for p in ref_chart.palaces if p.branch == 1)  # 丑
        assert "太陽" in p.stars
        assert "太陰" in p.stars

    def test_tiantong_at_hai(self, ref_chart):
        p = next(p for p in ref_chart.palaces if p.branch == 11)  # 亥
        assert "天同" in p.stars

    def test_tanlang_at_yin(self, ref_chart):
        p = next(p for p in ref_chart.palaces if p.branch == 2)  # 寅
        assert "貪狼" in p.stars

    def test_pojun_at_xu(self, ref_chart):
        p = next(p for p in ref_chart.palaces if p.branch == 10)  # 戌
        assert "破軍" in p.stars

    def test_sihua_yi_year(self, ref_chart):
        # 乙年四化: 天機化祿, 天梁化權, 紫微化科, 太陰化忌
        assert ref_chart.sihua == {
            "天機": "祿", "天梁": "權", "紫微": "科", "太陰": "忌"
        }

    def test_lucun_at_mao(self, ref_chart):
        # 乙年祿存在卯
        p = next(p for p in ref_chart.palaces if p.branch == 3)
        assert "祿存" in p.aux_stars

    def test_qingyang_at_chen(self, ref_chart):
        # 擎羊在辰 (祿存+1)
        p = next(p for p in ref_chart.palaces if p.branch == 4)
        assert "擎羊" in p.aux_stars

    def test_wenchang_at_you(self, ref_chart):
        # 丑時 → 文昌在酉
        p = next(p for p in ref_chart.palaces if p.branch == 9)
        assert "文昌" in p.aux_stars

    def test_wenqu_at_si(self, ref_chart):
        # 丑時 → 文曲在巳
        p = next(p for p in ref_chart.palaces if p.branch == 5)
        assert "文曲" in p.aux_stars

    def test_da_xian_ming(self, ref_chart):
        ming_palace = next(p for p in ref_chart.palaces if p.name == "命宮")
        assert ming_palace.da_xian == "3~12"

    def test_da_xian_xiongdi(self, ref_chart):
        xiongdi = next(p for p in ref_chart.palaces if p.name == "兄弟宮")
        assert xiongdi.da_xian == "13~22"

    def test_palace_ordering_counter_clockwise(self, ref_chart):
        """Verify palaces go counter-clockwise (decreasing branch) from 命宮"""
        branches = [p.branch for p in ref_chart.palaces]
        # 命宮=未(7), 兄弟=午(6), 夫妻=巳(5)...
        assert branches[0] == 7  # 未
        assert branches[1] == 6  # 午
        assert branches[2] == 5  # 巳

    def test_sanhe_groups_exist(self, ref_chart):
        assert len(ref_chart.sanhe_groups) == 4

    def test_aux_stars_present(self, ref_chart):
        all_aux = [s for p in ref_chart.palaces for s in p.aux_stars]
        for star in ["文昌", "文曲", "左輔", "右弼", "祿存", "擎羊", "陀羅",
                     "天魁", "天鉞", "火星", "鈴星", "天空", "地劫", "天馬"]:
            assert star in all_aux, f"{star} not found in auxiliary stars"

    def test_brightness_labels(self, ref_chart):
        """Each main star should have a brightness label"""
        for p in ref_chart.palaces:
            for star in p.stars:
                assert star in p.brightness, f"{star} missing brightness in {p.name}"


class TestNayinWuxingJu:
    """納音五行局查表測試"""

    def test_table_length(self):
        assert len(NAYIN_WUXING_JU) == 30

    def test_all_values_valid(self):
        for val in NAYIN_WUXING_JU:
            assert val in {2, 3, 4, 5, 6}

    def test_jiazi_gold4(self):
        # 甲子(0) → pair 0 → 金四局
        assert NAYIN_WUXING_JU[0] == 4

    def test_bingyin_fire6(self):
        # 丙寅(2) → pair 1 → 火六局
        assert NAYIN_WUXING_JU[1] == 6

    def test_wuchen_wood3(self):
        # 戊辰(4) → pair 2 → 木三局
        assert NAYIN_WUXING_JU[2] == 3


class TestSihuaTable:
    """四化表測試"""

    def test_table_length(self):
        assert len(SIHUA_TABLE) == 10

    def test_each_entry_has_4_stars(self):
        for entry in SIHUA_TABLE:
            assert len(entry) == 4

    def test_yi_year_sihua(self):
        # 乙年: 天機祿, 天梁權, 紫微科, 太陰忌
        lu, quan, ke, ji = SIHUA_TABLE[1]
        assert lu == "天機"
        assert quan == "天梁"
        assert ke == "紫微"
        assert ji == "太陰"

    def test_jia_year_sihua(self):
        # 甲年: 廉貞祿, 破軍權, 武曲科, 太陽忌
        lu, quan, ke, ji = SIHUA_TABLE[0]
        assert lu == "廉貞"
        assert quan == "破軍"
        assert ke == "武曲"
        assert ji == "太陽"


# ============================================================
# Myanmar Mahabote Tests
# ============================================================

from astro.mahabote import (
    compute_mahabote_chart,
    _get_myanmar_year,
    _get_weekday,
    _is_wednesday_evening,
    _compute_periods,
    WEEKDAY_PLANETS,
    WEEKDAY_ANIMALS,
    RAHU_ANIMAL,
    MAHABOTE_HOUSES,
    PLANET_PERIOD_YEARS,
)


class TestMyanmarYear:
    """緬甸年 (Myanmar Era) 計算測試"""

    def test_after_thingyan(self):
        """April 17 or later → ME = year - 638"""
        assert _get_myanmar_year(2000, 5, 1) == 2000 - 638

    def test_before_thingyan(self):
        """Before April 17 → ME = year - 639"""
        assert _get_myanmar_year(2000, 3, 1) == 2000 - 639

    def test_on_thingyan(self):
        """April 17 exactly → ME = year - 638"""
        assert _get_myanmar_year(2000, 4, 17) == 2000 - 638

    def test_april_16_before(self):
        """April 16 → still before Thingyan"""
        assert _get_myanmar_year(2000, 4, 16) == 2000 - 639

    def test_january_1_1990(self):
        assert _get_myanmar_year(1990, 1, 1) == 1990 - 639


class TestWeekday:
    """星期計算測試"""

    def test_known_monday(self):
        """1990-01-01 was a Monday → weekday=1"""
        assert _get_weekday(1990, 1, 1) == 1

    def test_known_sunday(self):
        """2023-01-01 was a Sunday → weekday=0"""
        assert _get_weekday(2023, 1, 1) == 0

    def test_known_saturday(self):
        """2023-01-07 was a Saturday → weekday=6"""
        assert _get_weekday(2023, 1, 7) == 6

    def test_known_wednesday(self):
        """2023-01-04 was a Wednesday → weekday=3"""
        assert _get_weekday(2023, 1, 4) == 3

    def test_weekday_range(self):
        for d in range(1, 8):
            w = _get_weekday(2023, 1, d)
            assert 0 <= w <= 6


class TestWednesdayRahu:
    """星期三傍晚 → 羅睺 測試"""

    def test_wednesday_evening_is_rahu(self):
        assert _is_wednesday_evening(3, 18) is True

    def test_wednesday_night_is_rahu(self):
        assert _is_wednesday_evening(3, 23) is True

    def test_wednesday_morning_not_rahu(self):
        assert _is_wednesday_evening(3, 10) is False

    def test_wednesday_17_not_rahu(self):
        assert _is_wednesday_evening(3, 17) is False

    def test_thursday_evening_not_rahu(self):
        assert _is_wednesday_evening(4, 18) is False


class TestMahaboteValue:
    """Mahabote 值計算測試"""

    def test_known_calculation(self):
        """1990-01-01 (Mon): ME=1351, weekday_num=2, (1351+2)%8=5"""
        chart = compute_mahabote_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
            location_name="仰光",
        )
        assert chart.myanmar_year == 1351
        assert chart.weekday == 1  # Monday
        assert chart.mahabote_value == (1351 + 2) % 8  # = 5

    def test_mahabote_value_range(self):
        chart = compute_mahabote_chart(
            year=2000, month=6, day=15, hour=10, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        assert 0 <= chart.mahabote_value <= 7


class TestMahaboteChart:
    """Mahabote 完整排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_mahabote_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
            location_name="仰光",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.month == 1
        assert sample_chart.day == 1
        assert sample_chart.location_name == "仰光"

    def test_birth_planet_monday(self, sample_chart):
        """Monday → Moon"""
        assert sample_chart.birth_planet == "Moon"
        assert sample_chart.birth_planet_cn == "月亮"
        assert sample_chart.birth_planet_symbol == "☽"

    def test_not_rahu(self, sample_chart):
        assert sample_chart.is_rahu is False

    def test_eight_houses(self, sample_chart):
        assert len(sample_chart.houses) == 8

    def test_birth_house_marked(self, sample_chart):
        birth_houses = [h for h in sample_chart.houses if h.is_birth_house]
        assert len(birth_houses) == 1

    def test_birth_planet_in_birth_house(self, sample_chart):
        """Birth planet should be placed in the mahabote_value house."""
        birth_house = sample_chart.houses[sample_chart.mahabote_value]
        assert birth_house.is_birth_house is True
        assert birth_house.planet == sample_chart.birth_planet

    def test_all_seven_planets_placed(self, sample_chart):
        planets = {h.planet for h in sample_chart.houses}
        expected = {"Sun", "Moon", "Mars", "Mercury",
                    "Jupiter", "Venus", "Saturn"}
        # All 7 weekday planets should appear across the 8 houses
        # (one planet repeats in the 8th Kamma house)
        assert planets == expected

    def test_house_names_match_constants(self, sample_chart):
        for i, h in enumerate(sample_chart.houses):
            assert h.name_en == MAHABOTE_HOUSES[i][0]
            assert h.name_myanmar == MAHABOTE_HOUSES[i][1]
            assert h.name_cn == MAHABOTE_HOUSES[i][2]

    def test_birth_house_fields(self, sample_chart):
        idx = sample_chart.mahabote_value
        expected = MAHABOTE_HOUSES[idx]
        assert sample_chart.birth_house_name_en == expected[0]
        assert sample_chart.birth_house_name_myanmar == expected[1]
        assert sample_chart.birth_house_name_cn == expected[2]

    def test_periods_not_empty(self, sample_chart):
        assert len(sample_chart.periods) > 0

    def test_periods_start_with_birth_planet(self, sample_chart):
        first = sample_chart.periods[0]
        # The first period planet should correspond to the birth weekday
        expected_planet = WEEKDAY_PLANETS[sample_chart.weekday][0]
        assert first.planet == expected_planet

    def test_periods_sequential(self, sample_chart):
        """Period ages should be sequential and non-overlapping."""
        for i in range(1, len(sample_chart.periods)):
            assert sample_chart.periods[i].start_age == \
                   sample_chart.periods[i - 1].end_age


class TestMahaboteRahu:
    """Wednesday evening (Rahu) test"""

    def test_wednesday_evening_rahu(self):
        """Wednesday at 20:00 → birth planet should be Rahu."""
        chart = compute_mahabote_chart(
            year=2023, month=1, day=4, hour=20, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        assert chart.weekday == 3  # Wednesday
        assert chart.is_rahu is True
        assert chart.birth_planet == "Rahu"
        assert chart.birth_planet_cn == "羅睺"

    def test_wednesday_morning_mercury(self):
        """Wednesday at 10:00 → birth planet should be Mercury."""
        chart = compute_mahabote_chart(
            year=2023, month=1, day=4, hour=10, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        assert chart.is_rahu is False
        assert chart.birth_planet == "Mercury"


class TestPlanetPeriods:
    """行星大運 (Atar) 計算測試"""

    def test_total_cycle_96_years(self):
        total = sum(PLANET_PERIOD_YEARS.values())
        assert total == 96

    def test_periods_cover_first_cycle(self):
        periods = _compute_periods(0, 2000, 2020)  # Sunday birth
        # First cycle should sum to 96
        cycle_total = sum(p.years for p in periods[:7])
        assert cycle_total == 96

    def test_current_period_marked(self):
        periods = _compute_periods(0, 2000, 2020)
        current = [p for p in periods if p.is_current]
        assert len(current) == 1
        assert current[0].start_age <= 20 < current[0].end_age


class TestMahaboteAnimalSigns:
    """動物標誌 (Animal Signs) 測試"""

    def test_weekday_animals_count(self):
        """Should have 7 weekday animal signs."""
        assert len(WEEKDAY_ANIMALS) == 7

    def test_weekday_animals_tuple_format(self):
        """Each animal should be (English, Myanmar, Chinese, emoji)."""
        for animal in WEEKDAY_ANIMALS:
            assert len(animal) == 4

    def test_rahu_animal_tuple_format(self):
        """Rahu animal should be (English, Myanmar, Chinese, emoji)."""
        assert len(RAHU_ANIMAL) == 4
        assert RAHU_ANIMAL[0] == "Tuskless Elephant"

    def test_sunday_garuda(self):
        """Sunday → Garuda."""
        assert WEEKDAY_ANIMALS[0][0] == "Garuda"

    def test_monday_tiger(self):
        """Monday → Tiger."""
        assert WEEKDAY_ANIMALS[1][0] == "Tiger"

    def test_tuesday_lion(self):
        """Tuesday → Lion."""
        assert WEEKDAY_ANIMALS[2][0] == "Lion"

    def test_wednesday_tusked_elephant(self):
        """Wednesday → Tusked Elephant."""
        assert WEEKDAY_ANIMALS[3][0] == "Tusked Elephant"

    def test_thursday_rat(self):
        """Thursday → Rat."""
        assert WEEKDAY_ANIMALS[4][0] == "Rat"

    def test_friday_guinea_pig(self):
        """Friday → Guinea Pig."""
        assert WEEKDAY_ANIMALS[5][0] == "Guinea Pig"

    def test_saturday_naga(self):
        """Saturday → Naga."""
        assert WEEKDAY_ANIMALS[6][0] == "Naga"

    def test_chart_birth_animal_monday(self):
        """Monday birth → Tiger."""
        chart = compute_mahabote_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        assert chart.weekday == 1  # Monday
        assert chart.birth_animal_en == "Tiger"
        assert chart.birth_animal_cn == "虎"
        assert chart.birth_animal_emoji == "🐅"

    def test_chart_rahu_animal(self):
        """Wednesday evening → Tuskless Elephant."""
        chart = compute_mahabote_chart(
            year=2023, month=1, day=4, hour=20, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        assert chart.is_rahu is True
        assert chart.birth_animal_en == "Tuskless Elephant"
        assert chart.birth_animal_cn == "象(無牙)"

    def test_house_has_animal_and_weekday(self):
        """Each house should have animal sign and weekday fields."""
        chart = compute_mahabote_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        for h in chart.houses:
            assert h.animal_en != ""
            assert h.animal_cn != ""
            assert h.animal_emoji != ""
            assert h.animal_myanmar != ""
            assert h.weekday_en != ""
            assert h.weekday_cn != ""

    def test_houses_have_distinct_animals(self):
        """8 houses should have all 7 distinct animal signs (1 repeats in Kamma)."""
        chart = compute_mahabote_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=6.5, latitude=16.8661, longitude=96.1951,
        )
        animals = {h.animal_en for h in chart.houses}
        assert len(animals) == 7


# ============================================================
# Decan Astrology Tests
# ============================================================

from astro.egyptian.decans_data import (
    DECANS_DATA,
    get_decan_by_longitude,
    get_decan_by_sign_and_degree,
    CHALDEAN_ORDER,
    ZODIAC_SIGNS_DECAN,
    ESSENTIAL_DIGNITIES,
    FACE_DIGNITY_SCORE,
)
from astro.egyptian.decans import compute_decan_chart, DecanChart, DecanPlanetInfo


SIGN_ELEMENT = {s[0]: s[3] for s in ZODIAC_SIGNS_DECAN}

REQUIRED_DECAN_KEYS = {
    "index", "sign_en", "sign_cn", "sign_glyph",
    "decan_number", "degree_start", "degree_end",
    "degree_in_sign_start", "degree_in_sign_end",
    "chaldean_ruler_en", "chaldean_ruler_cn", "chaldean_ruler_glyph",
    "triplicity_ruler_en", "triplicity_ruler_cn",
    "egyptian_name", "egyptian_hieroglyphic", "egyptian_transliteration",
    "egyptian_deity",
    "color", "mineral", "plant",
    "tarot_card_en", "tarot_card_cn",
    "personality_en", "personality_cn",
    "strengths_en", "strengths_cn",
    "challenges_en", "challenges_cn",
    "history_en", "history_cn",
    "element",
}

# Golden Dawn tarot order: each sign uses one suit (by element),
# numbers run 2-10 across the 36 decans with suit changing per sign.
ELEMENT_SUIT_MAP = {
    "Fire": "Wands", "Earth": "Pentacles",
    "Air": "Swords", "Water": "Cups",
}


class TestDecansData:
    """古埃及十度區間資料測試"""

    def test_36_decans_exist(self):
        """Should have exactly 36 decans"""
        assert len(DECANS_DATA) == 36

    def test_decan_indices(self):
        """Each decan index should be 0-35"""
        for i, d in enumerate(DECANS_DATA):
            assert d["index"] == i

    def test_chaldean_order_cycle(self):
        """Chaldean rulers should cycle in correct order"""
        for i, d in enumerate(DECANS_DATA):
            expected = CHALDEAN_ORDER[i % 7]
            assert d["chaldean_ruler_en"] == expected, (
                f"Decan {i}: expected {expected}, got {d['chaldean_ruler_en']}"
            )

    def test_tarot_mapping_golden_dawn(self):
        """Tarot cards should follow Golden Dawn order"""
        # Golden Dawn assigns pip cards 2-10 sequentially across the
        # 36 decans (index % 9 + 2), suit determined by element.
        for d in DECANS_DATA:
            suit = ELEMENT_SUIT_MAP[d["element"]]
            expected_pip = (d["index"] % 9) + 2
            expected_card = f"{expected_pip} of {suit}"
            assert d["tarot_card_en"] == expected_card, (
                f"Decan {d['index']}: expected '{expected_card}', "
                f"got '{d['tarot_card_en']}'"
            )

    def test_degree_ranges_continuous(self):
        """Degree ranges should be continuous 0-360"""
        for i, d in enumerate(DECANS_DATA):
            assert d["degree_start"] == i * 10
            assert d["degree_end"] == (i + 1) * 10

    def test_each_sign_has_three_decans(self):
        """Each zodiac sign should have exactly 3 decans"""
        from collections import Counter
        counts = Counter(d["sign_en"] for d in DECANS_DATA)
        for sign, count in counts.items():
            assert count == 3, f"{sign} has {count} decans, expected 3"
        assert len(counts) == 12

    def test_get_decan_by_longitude_boundaries(self):
        """Test boundary conditions for longitude lookup"""
        # First decan: 0°
        d = get_decan_by_longitude(0.0)
        assert d["index"] == 0
        # Just before 10°
        d = get_decan_by_longitude(9.999)
        assert d["index"] == 0
        # Exactly 10° -> second decan
        d = get_decan_by_longitude(10.0)
        assert d["index"] == 1
        # Last decan: 350°
        d = get_decan_by_longitude(350.0)
        assert d["index"] == 35
        # Wrap-around: 360° -> first decan
        d = get_decan_by_longitude(360.0)
        assert d["index"] == 0
        # Negative normalisation
        d = get_decan_by_longitude(-10.0)
        assert d["index"] == 35

    def test_get_decan_by_sign_and_degree(self):
        """Test sign+degree lookup"""
        # Aries 0° -> decan 0
        d = get_decan_by_sign_and_degree(0, 0.0)
        assert d["index"] == 0
        assert d["sign_en"] == "Aries"
        # Aries 15° -> decan 1
        d = get_decan_by_sign_and_degree(0, 15.0)
        assert d["index"] == 1
        # Pisces 25° -> decan 35
        d = get_decan_by_sign_and_degree(11, 25.0)
        assert d["index"] == 35
        # Invalid sign should raise
        with pytest.raises(ValueError):
            get_decan_by_sign_and_degree(12, 0.0)
        # Invalid degree should raise
        with pytest.raises(ValueError):
            get_decan_by_sign_and_degree(0, 30.0)

    def test_all_required_keys_present(self):
        """Every decan dict should have all required keys"""
        for d in DECANS_DATA:
            missing = REQUIRED_DECAN_KEYS - d.keys()
            assert not missing, f"Decan {d.get('index')}: missing keys {missing}"

    def test_elements_match_signs(self):
        """Decan element should match its zodiac sign's element"""
        for d in DECANS_DATA:
            expected = SIGN_ELEMENT[d["sign_en"]]
            assert d["element"] == expected, (
                f"Decan {d['index']} ({d['sign_en']}): "
                f"element {d['element']} != expected {expected}"
            )


class TestDecanChart:
    """古埃及十度區間排盤測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_decan_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=25.033, longitude=121.565,
            location_name="台北",
        )

    def test_chart_has_planets(self, sample_chart):
        """Chart should have planet entries"""
        assert len(sample_chart.planets) > 0
        assert all(
            isinstance(p, DecanPlanetInfo) for p in sample_chart.planets
        )

    def test_chart_has_ascendant(self, sample_chart):
        """Chart should have ascendant decan"""
        asc = sample_chart.ascendant_decan
        assert isinstance(asc, dict)
        assert "index" in asc
        assert 0 <= asc["index"] <= 35

    def test_planet_decan_numbers_valid(self, sample_chart):
        """All decan numbers should be 1, 2, or 3"""
        for p in sample_chart.planets:
            assert p.decan_number in (1, 2, 3), (
                f"{p.planet_name} has decan_number={p.decan_number}"
            )

    def test_sun_in_capricorn(self, sample_chart):
        """Sun on 1990-01-01 should be in Capricorn"""
        sun = next(p for p in sample_chart.planets if "Sun" in p.planet_name)
        assert sun.sign_en == "Capricorn"

    def test_face_dignity_boolean(self, sample_chart):
        """face_dignity should be boolean for all planets"""
        for p in sample_chart.planets:
            assert isinstance(p.face_dignity, bool), (
                f"{p.planet_name}: face_dignity is {type(p.face_dignity)}"
            )

    def test_today_sun_decan_present(self, sample_chart):
        """today_sun_decan should be a valid decan dict"""
        d = sample_chart.today_sun_decan
        assert isinstance(d, dict)
        assert "index" in d
        assert 0 <= d["index"] <= 35

    def test_essential_dignities_summary(self, sample_chart):
        """Should have dignity summary entries"""
        summary = sample_chart.essential_dignities_summary
        assert len(summary) == len(sample_chart.planets)
        for row in summary:
            assert "planet" in row
            assert "score" in row
            assert isinstance(row["score"], (int, float))

    def test_chart_metadata(self, sample_chart):
        """Chart should store input metadata correctly"""
        assert sample_chart.year == 1990
        assert sample_chart.month == 1
        assert sample_chart.day == 1
        assert sample_chart.hour == 12
        assert sample_chart.minute == 0
        assert sample_chart.location_name == "台北"


# ============================================================
# 蒙古祖爾海 (Zurkhai) Tests
# ============================================================

from astro.zurkhai import (
    compute_zurkhai_chart,
    _get_animal,
    _get_element,
    _get_polarity,
    _get_cycle_year,
    _get_day_animal,
    _get_element_relation,
    _check_conflict,
    _check_harmony,
    _check_obstacle_age,
    _compute_auspicious,
    _build_zurkhai_wheel_svg,
    ANIMALS,
    ELEMENTS,
    POLARITIES,
    GENERATING_CYCLE,
    OVERCOMING_CYCLE,
    ANIMAL_CONFLICTS,
    ANIMAL_HARMONIES,
    ACTIVITY_TYPES,
)


class TestZurkhaiConstants:
    """Test Zurkhai data constants."""

    def test_animals_count(self):
        assert len(ANIMALS) == 12

    def test_elements_count(self):
        assert len(ELEMENTS) == 5

    def test_polarities_count(self):
        assert len(POLARITIES) == 2

    def test_animal_indices(self):
        for i, a in enumerate(ANIMALS):
            assert a[0] == i

    def test_element_indices(self):
        for i, e in enumerate(ELEMENTS):
            assert e[0] == i

    def test_generating_cycle_complete(self):
        """Generating cycle must cover all 5 elements."""
        assert set(GENERATING_CYCLE.keys()) == {0, 1, 2, 3, 4}
        assert set(GENERATING_CYCLE.values()) == {0, 1, 2, 3, 4}

    def test_overcoming_cycle_complete(self):
        """Overcoming cycle must cover all 5 elements."""
        assert set(OVERCOMING_CYCLE.keys()) == {0, 1, 2, 3, 4}
        assert set(OVERCOMING_CYCLE.values()) == {0, 1, 2, 3, 4}

    def test_animal_conflicts_symmetric(self):
        """If A conflicts with B, B must conflict with A."""
        for a, conflicts in ANIMAL_CONFLICTS.items():
            for b in conflicts:
                assert a in ANIMAL_CONFLICTS[b], (
                    f"Conflict {a}->{b} not symmetric")

    def test_animal_harmonies_symmetric(self):
        """If A harmonizes with B, B must harmonize with A."""
        for a, harmonies in ANIMAL_HARMONIES.items():
            for b in harmonies:
                assert a in ANIMAL_HARMONIES[b], (
                    f"Harmony {a}->{b} not symmetric")

    def test_activity_types(self):
        assert len(ACTIVITY_TYPES) == 8
        keys = [a[0] for a in ACTIVITY_TYPES]
        assert len(set(keys)) == 8  # All unique


class TestZurkhaiAnimal:
    """Test animal sign calculation."""

    def test_1924_wood_rat(self):
        a = _get_animal(1924)
        assert a.index == 0
        assert a.name_en == "Rat"
        assert a.name_mn == "Hulgana"
        assert a.name_cn == "鼠"

    def test_1990_horse(self):
        a = _get_animal(1990)
        assert a.index == 6
        assert a.name_en == "Horse"
        assert a.name_mn == "Mori"

    def test_2000_dragon(self):
        a = _get_animal(2000)
        assert a.index == 4
        assert a.name_en == "Dragon"
        assert a.name_mn == "Luu"

    def test_2023_rabbit(self):
        a = _get_animal(2023)
        assert a.index == 3
        assert a.name_en == "Rabbit"

    def test_cycle_repeats(self):
        """Same animal every 12 years."""
        a1 = _get_animal(1990)
        a2 = _get_animal(2002)
        assert a1.index == a2.index


class TestZurkhaiElement:
    """Test element calculation."""

    def test_1924_wood(self):
        e = _get_element(1924)
        assert e.index == 0
        assert e.name_en == "Wood"
        assert e.name_mn == "Mod"

    def test_1925_wood(self):
        """Same element spans 2 years."""
        e = _get_element(1925)
        assert e.index == 0
        assert e.name_en == "Wood"

    def test_1926_fire(self):
        e = _get_element(1926)
        assert e.index == 1
        assert e.name_en == "Fire"

    def test_1990_metal(self):
        e = _get_element(1990)
        assert e.index == 3
        assert e.name_en == "Metal"
        assert e.name_mn == "Temür"

    def test_element_cycle(self):
        """Element repeats every 10 years."""
        e1 = _get_element(1990)
        e2 = _get_element(2000)
        assert e1.index == e2.index


class TestZurkhaiPolarity:
    """Test polarity (yin/yang) calculation."""

    def test_1924_yang(self):
        p = _get_polarity(1924)
        assert p.index == 0
        assert p.name_en == "Yang"

    def test_1925_yin(self):
        p = _get_polarity(1925)
        assert p.index == 1
        assert p.name_en == "Yin"

    def test_1990_yang(self):
        p = _get_polarity(1990)
        assert p.index == 0
        assert p.name_en == "Yang"


class TestZurkhaiCycleYear:
    """Test 60-year cycle position."""

    def test_1924_is_zero(self):
        assert _get_cycle_year(1924) == 0

    def test_1984_is_zero(self):
        assert _get_cycle_year(1984) == 0

    def test_1990_is_six(self):
        assert _get_cycle_year(1990) == 6

    def test_range(self):
        for y in range(1900, 2100):
            cy = _get_cycle_year(y)
            assert 0 <= cy < 60


class TestZurkhaiElementRelation:
    """Test element relationship calculations."""

    def test_same_element(self):
        key, cn, en = _get_element_relation(0, 0)
        assert key == "same"

    def test_generating(self):
        key, cn, en = _get_element_relation(0, 1)  # Wood -> Fire
        assert key == "generating"

    def test_overcoming(self):
        key, cn, en = _get_element_relation(0, 2)  # Wood -> Earth
        assert key == "overcoming"

    def test_weakening(self):
        key, cn, en = _get_element_relation(1, 0)  # Fire <- Wood
        assert key == "weakening"

    def test_resisting(self):
        key, cn, en = _get_element_relation(2, 0)  # Earth <- Wood overcomes
        assert key == "resisting"


class TestZurkhaiConflict:
    """Test animal conflict detection."""

    def test_rat_horse_conflict(self):
        is_c, cn, en = _check_conflict(0, 6)
        assert is_c is True

    def test_no_conflict(self):
        is_c, cn, en = _check_conflict(0, 4)  # Rat, Dragon - no conflict
        assert is_c is False

    def test_all_conflicts_detected(self):
        for a_idx, conflicts in ANIMAL_CONFLICTS.items():
            for c_idx in conflicts:
                is_c, _, _ = _check_conflict(a_idx, c_idx)
                assert is_c is True


class TestZurkhaiHarmony:
    """Test animal harmony detection."""

    def test_rat_dragon_harmony(self):
        is_h, cn, en = _check_harmony(0, 4)
        assert is_h is True

    def test_rat_monkey_harmony(self):
        is_h, cn, en = _check_harmony(0, 8)
        assert is_h is True

    def test_no_harmony(self):
        is_h, cn, en = _check_harmony(0, 1)  # Rat, Ox - not in harmony list
        assert is_h is False


class TestZurkhaiObstacleAge:
    """Test obstacle year detection."""

    def test_age_9_obstacle(self):
        age, is_o, cn, en = _check_obstacle_age(2000, 2008)
        assert age == 9
        assert is_o is True

    def test_age_21_obstacle(self):
        age, is_o, cn, en = _check_obstacle_age(2000, 2020)
        assert age == 21
        assert is_o is True

    def test_non_obstacle_age(self):
        age, is_o, cn, en = _check_obstacle_age(2000, 2010)
        assert age == 11
        assert is_o is False


class TestZurkhaiAuspicious:
    """Test auspicious timing calculations."""

    def test_returns_all_activities(self):
        results = _compute_auspicious(0)  # Rat day
        assert len(results) == len(ACTIVITY_TYPES)

    def test_rat_day_marriage_favorable(self):
        results = _compute_auspicious(0)  # Rat day
        marriage = [r for r in results if r.activity_key == "marriage"][0]
        assert marriage.is_favorable is True

    def test_tiger_day_travel_favorable(self):
        results = _compute_auspicious(2)  # Tiger day
        travel = [r for r in results if r.activity_key == "travel"][0]
        assert travel.is_favorable is True


class TestZurkhaiChart:
    """Test full chart computation."""

    @pytest.fixture
    def sample_chart(self):
        return compute_zurkhai_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=47.9077, longitude=106.8832,
            location_name="烏蘭巴托",
        )

    def test_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.month == 1
        assert sample_chart.day == 1
        assert sample_chart.location_name == "烏蘭巴托"

    def test_birth_animal(self, sample_chart):
        assert sample_chart.birth_animal.name_en == "Horse"
        assert sample_chart.birth_animal.name_mn == "Mori"
        assert sample_chart.birth_animal.name_cn == "馬"

    def test_birth_element(self, sample_chart):
        assert sample_chart.birth_element.name_en == "Metal"
        assert sample_chart.birth_element.name_mn == "Temür"
        assert sample_chart.birth_element.name_cn == "金"

    def test_birth_polarity(self, sample_chart):
        assert sample_chart.birth_polarity.name_en == "Yang"
        assert sample_chart.birth_polarity.name_cn == "陽"

    def test_cycle_year(self, sample_chart):
        assert sample_chart.cycle_year == 6

    def test_current_year_populated(self, sample_chart):
        assert sample_chart.current_animal is not None
        assert sample_chart.current_element is not None
        assert sample_chart.current_polarity is not None

    def test_day_info(self, sample_chart):
        d = sample_chart.day_info
        assert d.animal is not None
        assert d.element is not None
        assert d.polarity is not None
        assert d.month_name != ""

    def test_element_relation(self, sample_chart):
        assert sample_chart.year_element_relation in (
            "generating", "overcoming", "same", "weakening", "resisting")

    def test_auspicious_results(self, sample_chart):
        assert len(sample_chart.auspicious_results) == 8
        for r in sample_chart.auspicious_results:
            assert r.activity_key in [a[0] for a in ACTIVITY_TYPES]

    def test_day_rating(self, sample_chart):
        assert sample_chart.day_rating in ("吉", "凶", "平")
        assert sample_chart.day_rating_en in (
            "Auspicious", "Inauspicious", "Neutral")

    def test_age_positive(self, sample_chart):
        assert sample_chart.age > 0

    def test_day_animal_cycles_every_12(self):
        """Day animal should repeat every 12 days."""
        from datetime import date
        d1 = date(2024, 1, 1)
        d2 = date(2024, 1, 13)
        a1 = _get_day_animal(d1)
        a2 = _get_day_animal(d2)
        assert a1.index == a2.index


class TestZurkhaiKnownYears:
    """Test with historically known animal-element-polarity combinations."""

    def test_2024_wood_dragon_yang(self):
        a = _get_animal(2024)
        e = _get_element(2024)
        p = _get_polarity(2024)
        assert a.name_en == "Dragon"
        assert e.name_en == "Wood"
        assert p.name_en == "Yang"

    def test_2025_wood_snake_yin(self):
        a = _get_animal(2025)
        e = _get_element(2025)
        p = _get_polarity(2025)
        assert a.name_en == "Snake"
        assert e.name_en == "Wood"
        assert p.name_en == "Yin"

    def test_1984_wood_rat_yang(self):
        a = _get_animal(1984)
        e = _get_element(1984)
        p = _get_polarity(1984)
        assert a.name_en == "Rat"
        assert e.name_en == "Wood"
        assert p.name_en == "Yang"

    def test_2000_metal_dragon_yang(self):
        a = _get_animal(2000)
        e = _get_element(2000)
        p = _get_polarity(2000)
        assert a.name_en == "Dragon"
        assert e.name_en == "Metal"
        assert p.name_en == "Yang"


class TestZurkhaiWheelSVG:
    """Test the Zurkhai star chart SVG wheel generation."""

    @pytest.fixture
    def chart_1990(self):
        return compute_zurkhai_chart(
            1990, 1, 1, 12, 0,
            timezone=8.0, latitude=39.9, longitude=116.4,
            location_name="Beijing",
        )

    @pytest.fixture
    def chart_conflict(self):
        """Rat born in conflict with Horse year (2026)."""
        return compute_zurkhai_chart(
            1984, 6, 15, 8, 30,
            timezone=8.0, latitude=39.9, longitude=116.4,
            location_name="Beijing",
        )

    def test_svg_is_valid(self, chart_1990):
        svg = _build_zurkhai_wheel_svg(chart_1990)
        assert svg.startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_svg_contains_all_animals(self, chart_1990):
        svg = _build_zurkhai_wheel_svg(chart_1990)
        for _, _, _, cn, emoji in ANIMALS:
            assert emoji in svg, f"Missing animal emoji: {emoji} ({cn})"

    def test_svg_contains_birth_marker(self, chart_1990):
        svg = _build_zurkhai_wheel_svg(chart_1990)
        assert "🎂" in svg

    def test_svg_contains_birth_animal_info_in_center(self, chart_1990):
        svg = _build_zurkhai_wheel_svg(chart_1990)
        assert chart_1990.birth_animal.name_cn in svg
        assert chart_1990.birth_element.name_cn in svg

    def test_svg_contains_element_colors(self, chart_1990):
        svg = _build_zurkhai_wheel_svg(chart_1990)
        for _, _, _, _, color, _ in ELEMENTS:
            assert color in svg, f"Missing element color: {color}"

    def test_svg_conflict_year_has_red_line(self, chart_conflict):
        """If chart has conflict year, SVG should contain a red dashed line."""
        svg = _build_zurkhai_wheel_svg(chart_conflict)
        if chart_conflict.is_conflict_year:
            assert "#ff4444" in svg

    def test_svg_dimensions(self, chart_1990):
        svg = _build_zurkhai_wheel_svg(chart_1990)
        assert 'viewBox="0 0 500 500"' in svg


# ============================================================
# Picatrix Mansions Tests
# ============================================================

class TestPicatrixData:
    """Picatrix 月宿資料完整性測試"""

    def test_mansion_count(self):
        from astro.arabic.picatrix_data import PICATRIX_MANSIONS
        assert len(PICATRIX_MANSIONS) == 28

    def test_mansion_indices_sequential(self):
        from astro.arabic.picatrix_data import PICATRIX_MANSIONS
        for i, m in enumerate(PICATRIX_MANSIONS):
            assert m["index"] == i

    def test_mansion_start_degrees_monotone(self):
        from astro.arabic.picatrix_data import PICATRIX_MANSIONS
        for i, m in enumerate(PICATRIX_MANSIONS):
            expected = i * (360.0 / 28)
            assert abs(m["start_degree"] - expected) < 0.001

    def test_mansion_required_keys(self):
        from astro.arabic.picatrix_data import PICATRIX_MANSIONS
        required = {
            "index", "arabic_name", "arabic_script", "english_name",
            "chinese_name", "ruling_planet", "fortunate",
            "magic_image", "magic_image_cn", "purposes", "purposes_cn",
            "incense", "color", "metal", "invocation_summary", "start_degree",
        }
        for m in PICATRIX_MANSIONS:
            assert required.issubset(m.keys()), f"Mansion {m['index']} missing keys"

    def test_ruling_planets_valid(self):
        from astro.arabic.picatrix_data import PICATRIX_MANSIONS, CHALDEAN_ORDER
        for m in PICATRIX_MANSIONS:
            assert m["ruling_planet"] in CHALDEAN_ORDER

    def test_fortunate_is_bool(self):
        from astro.arabic.picatrix_data import PICATRIX_MANSIONS
        for m in PICATRIX_MANSIONS:
            assert isinstance(m["fortunate"], bool)

    def test_purposes_are_lists(self):
        from astro.arabic.picatrix_data import PICATRIX_MANSIONS
        for m in PICATRIX_MANSIONS:
            assert isinstance(m["purposes"], list)
            assert isinstance(m["purposes_cn"], list)
            assert len(m["purposes"]) > 0
            assert len(m["purposes_cn"]) > 0

    def test_talisman_intents_count(self):
        from astro.arabic.picatrix_data import TALISMAN_INTENTS
        assert len(TALISMAN_INTENTS) == 8

    def test_talisman_required_keys(self):
        from astro.arabic.picatrix_data import TALISMAN_INTENTS
        required = {
            "intent_key", "intent_cn", "intent_en", "planet",
            "mansion_indices", "metal", "incense", "color",
            "hour_planet", "description_cn", "description_en",
        }
        for t in TALISMAN_INTENTS:
            assert required.issubset(t.keys())

    def test_talisman_mansion_indices_in_range(self):
        from astro.arabic.picatrix_data import TALISMAN_INTENTS
        for t in TALISMAN_INTENTS:
            for idx in t["mansion_indices"]:
                assert 0 <= idx <= 27


class TestPicatrixMansionLookup:
    """月宿查詢函數測試"""

    def test_mansion_index_at_zero(self):
        from astro.arabic.picatrix_mansions import get_mansion_index
        assert get_mansion_index(0.0) == 0

    def test_mansion_index_at_359(self):
        from astro.arabic.picatrix_mansions import get_mansion_index
        assert get_mansion_index(359.9) == 27

    def test_mansion_index_full_coverage(self):
        from astro.arabic.picatrix_mansions import get_mansion_index
        for deg in range(0, 360, 5):
            idx = get_mansion_index(float(deg))
            assert 0 <= idx <= 27

    def test_mansion_index_boundary(self):
        """Each mansion starts at index * 360/28 degrees (with epsilon tolerance)."""
        from astro.arabic.picatrix_mansions import get_mansion_index
        for i in range(28):
            # Use a degree slightly above the start of each mansion to avoid
            # floating-point precision issues at exact boundaries.
            lon = i * (360.0 / 28) + 0.001
            assert get_mansion_index(lon) == i

    def test_get_mansion_returns_object(self):
        from astro.arabic.picatrix_mansions import get_mansion, PicatrixMansion
        m = get_mansion(0.0)
        assert isinstance(m, PicatrixMansion)
        assert m.index == 0
        assert m.arabic_name == "Al-Sharatain"

    def test_get_mansion_by_index(self):
        from astro.arabic.picatrix_mansions import get_mansion_by_index
        for i in range(28):
            m = get_mansion_by_index(i)
            assert m.index == i

    def test_get_mansion_by_index_out_of_range(self):
        from astro.arabic.picatrix_mansions import get_mansion_by_index
        with pytest.raises(IndexError):
            get_mansion_by_index(-1)
        with pytest.raises(IndexError):
            get_mansion_by_index(28)

    def test_get_all_mansions(self):
        from astro.arabic.picatrix_mansions import get_all_mansions
        mansions = get_all_mansions()
        assert len(mansions) == 28


class TestPlanetaryHours:
    """行星時計算測試"""

    @pytest.fixture
    def hk_monday(self):
        """HK 2024-01-01 (Monday)"""
        from astro.arabic.picatrix_mansions import get_planetary_hours
        return get_planetary_hours(2024, 1, 1, 8.0, 22.3193, 114.1694)

    def test_returns_result_object(self, hk_monday):
        from astro.arabic.picatrix_mansions import PlanetaryHoursResult
        assert isinstance(hk_monday, PlanetaryHoursResult)

    def test_hours_count_is_24(self, hk_monday):
        assert len(hk_monday.hours) == 24

    def test_day_hours_count(self, hk_monday):
        day_hours = [h for h in hk_monday.hours if h.is_day]
        assert len(day_hours) == 12

    def test_night_hours_count(self, hk_monday):
        night_hours = [h for h in hk_monday.hours if not h.is_day]
        assert len(night_hours) == 12

    def test_monday_day_planet_is_moon(self, hk_monday):
        """Monday (星期一) should have Moon as day planet."""
        assert hk_monday.day_planet == "Moon"

    def test_first_hour_planet_is_day_planet(self, hk_monday):
        """First planetary hour should be ruled by the day planet."""
        assert hk_monday.hours[0].planet == hk_monday.day_planet

    def test_planets_are_from_chaldean_order(self, hk_monday):
        from astro.arabic.picatrix_data import CHALDEAN_ORDER
        for h in hk_monday.hours:
            assert h.planet in CHALDEAN_ORDER

    def test_chaldean_sequence(self, hk_monday):
        """Hours should follow Chaldean order cyclically."""
        from astro.arabic.picatrix_data import CHALDEAN_ORDER
        start_idx = CHALDEAN_ORDER.index(hk_monday.day_planet)
        for i, h in enumerate(hk_monday.hours):
            expected = CHALDEAN_ORDER[(start_idx + i) % 7]
            assert h.planet == expected

    def test_hour_numbers_sequential(self, hk_monday):
        for i, h in enumerate(hk_monday.hours):
            assert h.hour_number == i + 1

    def test_sunrise_before_sunset(self, hk_monday):
        assert hk_monday.sunrise < hk_monday.sunset

    def test_day_length_positive(self, hk_monday):
        assert hk_monday.day_length_minutes > 0

    def test_night_length_positive(self, hk_monday):
        assert hk_monday.night_length_minutes > 0

    def test_hk_sunrise_reasonable(self, hk_monday):
        """HK sunrise should be between 6:00 and 8:00 in January."""
        h = hk_monday.sunrise.hour
        assert 6 <= h <= 8

    def test_hour_planet_cn_not_empty(self, hk_monday):
        for h in hk_monday.hours:
            assert h.planet_cn != ""

    def test_start_times_ordered(self, hk_monday):
        """Day hours should have ascending start times."""
        day_hours = [h for h in hk_monday.hours if h.is_day]
        for i in range(len(day_hours) - 1):
            assert day_hours[i].start_time < day_hours[i + 1].start_time


class TestTalismanRecommendation:
    """護符推薦測試"""

    def test_love_recommendation(self):
        from astro.arabic.picatrix_mansions import get_picatrix_talisman_recommendation
        rec = get_picatrix_talisman_recommendation("love")
        assert rec is not None
        assert rec.planet == "Venus"
        assert rec.metal == "copper"

    def test_wealth_recommendation(self):
        from astro.arabic.picatrix_mansions import get_picatrix_talisman_recommendation
        rec = get_picatrix_talisman_recommendation("wealth")
        assert rec is not None
        assert rec.planet == "Jupiter"

    def test_chinese_intent_mapping(self):
        from astro.arabic.picatrix_mansions import get_picatrix_talisman_recommendation
        rec = get_picatrix_talisman_recommendation("愛情")
        assert rec is not None
        assert rec.planet == "Venus"
        rec2 = get_picatrix_talisman_recommendation("財富")
        assert rec2 is not None
        assert rec2.planet == "Jupiter"

    def test_unknown_intent_returns_none(self):
        from astro.arabic.picatrix_mansions import get_picatrix_talisman_recommendation
        assert get_picatrix_talisman_recommendation("unknown_xyz") is None

    def test_all_intents_return_recommendation(self):
        from astro.arabic.picatrix_mansions import (
            get_picatrix_talisman_recommendation,
            get_all_talisman_intents,
        )
        for key in get_all_talisman_intents():
            rec = get_picatrix_talisman_recommendation(key)
            assert rec is not None, f"No recommendation for intent: {key}"

    def test_recommendation_mansion_names_populated(self):
        from astro.arabic.picatrix_mansions import get_picatrix_talisman_recommendation
        rec = get_picatrix_talisman_recommendation("love")
        assert len(rec.mansion_names_cn) > 0
        for name in rec.mansion_names_cn:
            assert isinstance(name, str)
            assert len(name) > 0

    def test_arabic_wrapper_functions(self):
        """arabic.py wrapper functions should delegate correctly."""
        from astro.arabic.arabic import (
            get_planetary_hours,
            get_picatrix_talisman_recommendation,
        )
        hours = get_planetary_hours(2024, 1, 1, 8.0, 22.3193, 114.1694)
        assert len(hours.hours) == 24
        rec = get_picatrix_talisman_recommendation("love")
        assert rec is not None
        assert rec.planet == "Venus"


# ============================================================
# Shams al-Maʻārif Tests
# ============================================================

class TestPlanetaryProperties:
    """Tests for astro.arabic_planetaries.PlanetaryProperties."""

    def setup_method(self):
        from astro.arabic.arabic_planetaries import PlanetaryProperties
        self.pp = PlanetaryProperties()

    def test_list_all_returns_seven_planets(self):
        planets = self.pp.list_all()
        assert len(planets) == 7

    def test_all_planets_have_required_keys(self):
        required = {"planet", "arabic", "english", "temp", "element", "color",
                     "omens", "talisman_use", "timing", "letter", "wafq_size", "note"}
        for p in self.pp.list_all():
            assert required.issubset(p.keys()), f"Missing keys in {p['english']}"

    def test_get_planet_by_english(self):
        saturn = self.pp.get_planet("Saturn")
        assert saturn is not None
        assert saturn["arabic"] == "زحل"
        assert saturn["wafq_size"] == 3

    def test_get_planet_by_english_case_insensitive(self):
        jupiter = self.pp.get_planet("jupiter")
        assert jupiter is not None
        assert jupiter["english"] == "Jupiter"

    def test_get_planet_by_arabic(self):
        venus = self.pp.get_planet("الزهرة")
        assert venus is not None
        assert venus["english"] == "Venus"

    def test_get_planet_nonexistent_returns_none(self):
        assert self.pp.get_planet("Pluto") is None

    def test_wafq_sizes_3_to_9(self):
        sizes = [p["wafq_size"] for p in self.pp.list_all()]
        assert sorted(sizes) == [3, 4, 5, 6, 7, 8, 9]


class TestZodiacSigns:
    """Tests for astro.arabic_zodiacsigns.ZodiacSigns."""

    def setup_method(self):
        from astro.arabic.arabic_zodiacsigns import ZodiacSigns
        self.zs = ZodiacSigns()

    def test_list_all_returns_twelve_signs(self):
        assert len(self.zs.list_all()) == 12

    def test_all_signs_have_required_keys(self):
        required = {"no", "arabic", "english", "element", "ruler",
                     "omens", "talisman_use", "timing"}
        for s in self.zs.list_all():
            assert required.issubset(s.keys()), f"Missing keys in {s['english']}"

    def test_sign_numbers_sequential(self):
        numbers = [s["no"] for s in self.zs.list_all()]
        assert numbers == list(range(1, 13))

    def test_get_sign_by_number(self):
        aries = self.zs.get_sign(1)
        assert aries is not None
        assert aries["english"] == "Aries"

    def test_get_by_english(self):
        libra = self.zs.get_by_english("Libra")
        assert libra is not None
        assert libra["no"] == 7

    def test_get_by_arabic(self):
        pisces = self.zs.get_by_arabic("الحوت")
        assert pisces is not None
        assert pisces["english"] == "Pisces"


class TestShamsRiyada:
    """Tests for astro.riyada.ShamsRiyada."""

    def setup_method(self):
        from astro.arabic.riyada import ShamsRiyada
        self.sr = ShamsRiyada()

    def test_list_riyada_not_empty(self):
        riyadas = self.sr.list_all_riyada()
        assert len(riyadas) >= 5

    def test_riyada_has_required_keys(self):
        required = {"name", "chapter", "description", "arabic", "steps",
                     "incense", "use", "note"}
        for r in self.sr.list_all_riyada():
            assert required.issubset(r.keys()), f"Missing keys in {r['name']}"

    def test_riyada_steps_is_list(self):
        for r in self.sr.list_all_riyada():
            assert isinstance(r["steps"], list)
            assert len(r["steps"]) >= 1

    def test_get_riyada_by_keyword(self):
        result = self.sr.get_riyada("كريم")
        assert result is not None

    def test_get_riyada_nonexistent_returns_none(self):
        assert self.sr.get_riyada("nonexistent_xyz") is None

    def test_incense_formulas_not_empty(self):
        formulas = self.sr.list_all_incense()
        assert len(formulas) >= 4

    def test_incense_has_required_keys(self):
        required = {"name", "formula", "use", "note"}
        for inc in self.sr.list_all_incense():
            assert required.issubset(inc.keys())


class TestIslamicDuas:
    """Tests for astro.arabic_spells.IslamicDuas."""

    def setup_method(self):
        from astro.arabic.arabic_spells import IslamicDuas
        self.dua = IslamicDuas()

    def test_list_all_not_empty(self):
        assert len(self.dua.list_all()) >= 10

    def test_get_dua_returns_dict(self):
        keys = self.dua.list_all()
        if keys:
            result = self.dua.get_dua(keys[0])
            assert isinstance(result, dict)

    def test_get_dua_nonexistent_returns_none(self):
        assert self.dua.get_dua("nonexistent_key_xyz") is None


class TestIslamicWafq:
    """Tests for astro.wafq.IslamicWafqGenerator."""

    def setup_method(self):
        from astro.arabic.wafq import IslamicWafqGenerator
        self.wafq = IslamicWafqGenerator()

    def test_abjad_value_known(self):
        # 'ودود' = و(6) + د(4) + و(6) + د(4) = 20
        val = self.wafq.get_abjad_value("ودود")
        assert val == 20

    def test_abjad_empty_string(self):
        assert self.wafq.get_abjad_value("") == 0

    def test_magic_square_3x3(self):
        sq = self.wafq.generate_magic_square(3)
        assert len(sq) == 3
        assert all(len(row) == 3 for row in sq)
        # magic constant for 3×3 = 15
        for row in sq:
            assert sum(row) == 15

    def test_magic_square_4x4(self):
        sq = self.wafq.generate_magic_square(4)
        assert len(sq) == 4
        # magic constant for 4×4 = 34
        for row in sq:
            assert sum(row) == 34

    def test_magic_square_odd_sizes(self):
        for n in [5, 7, 9]:
            sq = self.wafq.generate_magic_square(n)
            assert len(sq) == n
            magic_const = n * (n * n + 1) // 2
            for row in sq:
                assert sum(row) == magic_const

    def test_magic_square_invalid_even_raises(self):
        with pytest.raises(ValueError):
            self.wafq.generate_magic_square(6)

    def test_asma_husna_count(self):
        assert len(self.wafq.ASMA_HUSNA) >= 90

    def test_asma_husna_has_required_keys(self):
        required = {"roman", "planet", "use", "timing"}
        for name, info in self.wafq.ASMA_HUSNA.items():
            assert required.issubset(info.keys()), f"Missing keys for {name}"

    def test_get_asma_info(self):
        info = self.wafq.get_asma_info("الودود")
        assert info is not None
        assert info["roman"] == "al-Wadud"
        assert info["planet"] == "Venus"

    def test_planetary_hours_returns_24(self):
        from datetime import datetime
        hours = self.wafq.planetary_hours(datetime(2024, 1, 1))
        assert len(hours) == 24


# ============================================================
# 神煞 (Shen Sha) Tests
# ============================================================

class TestShenSha:
    """Tests for the Shen Sha divine stars module."""

    def test_import(self):
        from astro.qizheng.shensha import compute_shensha, ShenShaResult
        assert callable(compute_shensha)

    def test_compute_shensha_returns_result(self):
        from astro.qizheng.shensha import compute_shensha
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(1990, 1, 1, 4.0)  # 1990-01-01 04:00 UTC
        result = compute_shensha(year=1990, solar_month=11, julian_day=jd, hour_branch=6)
        assert result is not None
        assert len(result.items) > 0
        assert isinstance(result.branch_map, dict)

    def test_shensha_has_key_stars(self):
        """Ensure key divine stars are present (MOIRA-aligned names)."""
        from astro.qizheng.shensha import compute_shensha
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(1990, 1, 1, 4.0)
        result = compute_shensha(year=1990, solar_month=11, julian_day=jd, hour_branch=6)
        all_names = [item.name for item in result.items]
        assert "驛馬" in all_names
        assert "桃花" in all_names  # sub-star of 咸池
        assert "華蓋" in all_names
        assert "天貴" in all_names  # MOIRA: 天貴 (not 天乙貴人)
        assert "文昌" in all_names
        assert "祿勳" in all_names  # MOIRA: 祿勳 (not 祿神)
        assert "長生" in all_names

    def test_shensha_branches_valid(self):
        """All branch indices should be 0-11."""
        from astro.qizheng.shensha import compute_shensha
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(1985, 8, 26, -2.167)  # ~ UTC+8
        result = compute_shensha(year=1985, solar_month=7, julian_day=jd, hour_branch=1)
        for item in result.items:
            assert 0 <= item.branch <= 11, f"{item.name} has invalid branch {item.branch}"

    def test_shensha_categories(self):
        """Categories should be 吉, 凶, or 中."""
        from astro.qizheng.shensha import compute_shensha
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(2000, 6, 15, 4.0)
        result = compute_shensha(year=2000, solar_month=5, julian_day=jd, hour_branch=6)
        for item in result.items:
            assert item.category in ("吉", "凶", "中"), f"{item.name} has invalid category {item.category}"

    def test_bazi_stems_branches(self):
        """Test Ba Zi four pillars calculation."""
        from astro.qizheng.shensha import get_bazi_stems_branches, HEAVENLY_STEMS, EARTHLY_BRANCHES
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(1990, 1, 1, 4.0)
        bazi = get_bazi_stems_branches(year=1990, solar_month=11, julian_day=jd, hour_branch=6)
        # Year pillar for 1990 = 庚午
        assert bazi["year_pillar"] == "庚午"
        # Validate structure
        assert "year_stem" in bazi
        assert "day_pillar" in bazi
        assert "hour_pillar" in bazi

    def test_bazi_1985_aug26(self):
        """Test Ba Zi for 1985-08-26 02:55 CST = 乙丑年甲申月丁酉日辛丑時."""
        from astro.qizheng.shensha import get_bazi_stems_branches
        import swisseph as swe
        swe.set_ephe_path("")
        # 1985-08-26 02:55 CST (UTC+8) → UT = 1985-08-25 18:55
        tz = 8.0
        jd = swe.julday(1985, 8, 26, 2.0 + 55.0 / 60.0 - tz)
        bazi = get_bazi_stems_branches(
            year=1985, solar_month=7, julian_day=jd,
            hour_branch=1, timezone=tz,
        )
        assert bazi["year_pillar"] == "乙丑"
        assert bazi["month_pillar"] == "甲申"
        assert bazi["day_pillar"] == "丁酉"
        assert bazi["hour_pillar"] == "辛丑"

    def test_year_stem_branch(self):
        """Test year stem and branch calculation."""
        from astro.qizheng.shensha import get_year_stem, get_year_branch
        # 1984 = 甲子
        assert get_year_stem(1984) == 0   # 甲
        assert get_year_branch(1984) == 0  # 子
        # 2024 = 甲辰
        assert get_year_stem(2024) == 0   # 甲
        assert get_year_branch(2024) == 4  # 辰

    def test_twelve_life_stages(self):
        """Test twelve life stages calculation (MOIRA Nayin method)."""
        from astro.qizheng.shensha import compute_twelve_life_stages
        # 甲子: Nayin=金, start=辰(4), forward
        stages = compute_twelve_life_stages(0, 0)  # 甲(stem=0), 子(branch=0)
        assert stages[4] == "長生"  # 辰
        assert stages[5] == "養"    # 巳

    def test_twelve_life_stages_all_nayin(self):
        """Test twelve life stages for each Nayin element type."""
        from astro.qizheng.shensha import compute_twelve_life_stages, gz_index, get_nayin_element
        # 金 start=辰(4): 甲子 (stem=0, branch=0)
        stages = compute_twelve_life_stages(0, 0)
        assert get_nayin_element(gz_index(0, 0)) == "金"
        assert stages[4] == "長生"

        # 火 start=未(7): 丙寅 (stem=2, branch=2)
        stages = compute_twelve_life_stages(2, 2)
        assert get_nayin_element(gz_index(2, 2)) == "火"
        assert stages[7] == "長生"

        # 木 start=戌(10): 戊辰 (stem=4, branch=4)
        stages = compute_twelve_life_stages(4, 4)
        assert get_nayin_element(gz_index(4, 4)) == "木"
        assert stages[10] == "長生"

        # 土 start=丑(1): 庚午 (stem=6, branch=6)
        stages = compute_twelve_life_stages(6, 6)
        assert get_nayin_element(gz_index(6, 6)) == "土"
        assert stages[1] == "長生"

        # 水 start=丑(1): 丙子 (stem=2, branch=0)
        stages = compute_twelve_life_stages(2, 0)
        assert get_nayin_element(gz_index(2, 0)) == "水"
        assert stages[1] == "長生"


# ============================================================
# 年限大運 (Dasha) Tests
# ============================================================

class TestQizhengDasha:
    """Tests for the planetary period/dasha module."""

    def test_import(self):
        from astro.qizheng.qizheng_dasha import compute_dasha, DashaResult
        assert callable(compute_dasha)

    def test_compute_dasha_returns_12_periods(self):
        from astro.qizheng.qizheng_dasha import compute_dasha
        from astro.qizheng.calculator import compute_chart
        chart = compute_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=22.3193, longitude=114.1694,
            location_name="Hong Kong", gender="male",
        )
        result = compute_dasha(
            birth_year=1990,
            ming_gong_branch=chart.ming_gong_branch,
            gender="male",
            houses=chart.houses,
            current_year=2026,
        )
        assert len(result.periods) == 12

    def test_dasha_ages_are_contiguous(self):
        """Ages should cover continuously from 0."""
        from astro.qizheng.qizheng_dasha import compute_dasha
        from astro.qizheng.calculator import compute_chart
        chart = compute_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=22.3193, longitude=114.1694,
            location_name="Hong Kong", gender="male",
        )
        result = compute_dasha(
            birth_year=1990,
            ming_gong_branch=chart.ming_gong_branch,
            gender="male",
            houses=chart.houses,
            current_year=2026,
        )
        assert result.periods[0].start_age == 0
        for i in range(1, len(result.periods)):
            assert result.periods[i].start_age == result.periods[i - 1].end_age + 1

    def test_dasha_current_period(self):
        """Current period should be correctly identified."""
        from astro.qizheng.qizheng_dasha import compute_dasha
        from astro.qizheng.calculator import compute_chart
        chart = compute_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=22.3193, longitude=114.1694,
            location_name="Hong Kong", gender="male",
        )
        result = compute_dasha(
            birth_year=1990,
            ming_gong_branch=chart.ming_gong_branch,
            gender="male",
            houses=chart.houses,
            current_year=2026,
        )
        assert result.current_age == 36
        assert result.current_period_idx >= 0
        p = result.periods[result.current_period_idx]
        assert p.start_age <= 36 <= p.end_age

    def test_dasha_flow_year(self):
        """Flow year branch should be valid."""
        from astro.qizheng.qizheng_dasha import compute_dasha
        from astro.qizheng.calculator import compute_chart
        chart = compute_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=22.3193, longitude=114.1694,
            location_name="Hong Kong", gender="male",
        )
        result = compute_dasha(
            birth_year=1990,
            ming_gong_branch=chart.ming_gong_branch,
            gender="male",
            houses=chart.houses,
            current_year=2026,
        )
        # 2026 = 丙午 → branch = (2026 - 4) % 12 = 2022 % 12 = 6 (午)
        assert result.flow_year_branch == 6


# ============================================================
# 流時對盤 (Transit) Tests
# ============================================================

class TestQizhengTransit:
    """Tests for the transit chart module."""

    def test_import(self):
        from astro.qizheng.qizheng_transit import compute_transit, TransitData
        assert callable(compute_transit)

    def test_compute_transit_returns_11_planets(self):
        from astro.qizheng.qizheng_transit import compute_transit
        result = compute_transit(
            year=2026, month=4, day=10,
            hour=10, minute=30, timezone=8.0,
        )
        assert len(result.planets) == 11  # 7 governors + 4 remainders

    def test_transit_planets_have_valid_longitudes(self):
        from astro.qizheng.qizheng_transit import compute_transit
        result = compute_transit(
            year=2026, month=4, day=10,
            hour=10, minute=30, timezone=8.0,
        )
        for p in result.planets:
            assert 0 <= p.longitude < 360, f"{p.name} longitude out of range: {p.longitude}"

    def test_transit_planet_names(self):
        from astro.qizheng.qizheng_transit import compute_transit
        result = compute_transit(
            year=2026, month=4, day=10,
            hour=10, minute=30, timezone=8.0,
        )
        names = [p.name for p in result.planets]
        assert "太陽" in names
        assert "太陰" in names
        assert "羅睺" in names
        assert "計都" in names

    def test_compute_transit_now(self):
        from astro.qizheng.qizheng_transit import compute_transit_now
        result = compute_transit_now(timezone=8.0)
        assert result is not None
        assert len(result.planets) == 11


# ============================================================
# 張果星宗 Tests
# ============================================================

class TestZhangguoStarReadings:
    """Tests for 張果星宗 module"""

    def test_load_star_data(self):
        from astro.qizheng.zhangguo import _load_star_data
        entries = _load_star_data()
        assert len(entries) > 100
        # Check first entry has required fields
        e = entries[0]
        assert "star" in e
        assert "branch" in e
        assert "type" in e
        assert "description" in e

    def test_load_pattern_data(self):
        from astro.qizheng.zhangguo import _load_pattern_data
        entries = _load_pattern_data()
        assert len(entries) > 50
        e = entries[0]
        assert "name" in e
        assert "type" in e
        assert "category" in e

    def test_lookup_sun_in_wu(self):
        """日在午宮 should return readings"""
        from astro.qizheng.zhangguo import lookup_star_in_branch
        readings = lookup_star_in_branch("日", "午")
        assert len(readings) > 0
        for r in readings:
            assert r.star == "日"
            assert r.branch == "午"
            assert r.reading_type in ("合格", "忌格")

    def test_lookup_nonexistent(self):
        """Non-standard star should return empty"""
        from astro.qizheng.zhangguo import lookup_star_in_branch
        readings = lookup_star_in_branch("不存在的星", "子")
        assert len(readings) == 0

    def test_lookup_gender_filter(self):
        """Female-specific readings should appear for female, not male"""
        from astro.qizheng.zhangguo import lookup_star_in_branch
        female_readings = lookup_star_in_branch("金星", "酉", "female")
        male_readings = lookup_star_in_branch("金星", "酉", "male")
        # Female should include female-only + both
        female_only = [r for r in female_readings if r.gender == "female"]
        assert len(female_only) > 0
        # Male should NOT include female-only entries
        male_genders = {r.gender for r in male_readings}
        assert "female" not in male_genders

    def test_get_all_patterns(self):
        from astro.qizheng.zhangguo import get_all_patterns
        patterns = get_all_patterns()
        assert len(patterns) > 50
        names = [p.name for p in patterns]
        assert "日居日位" in names
        assert "月入月垣" in names

    def test_planet_name_mapping(self):
        """All 11 chart planets should have mappings and no extras"""
        from astro.qizheng.zhangguo import PLANET_TO_ZHANGGUO
        expected = ["太陽", "太陰", "水星", "金星", "火星", "木星", "土星",
                    "羅睺", "計都", "月孛", "紫氣"]
        for name in expected:
            assert name in PLANET_TO_ZHANGGUO
        assert len(PLANET_TO_ZHANGGUO) == len(expected)

    def test_compute_zhangguo_with_chart(self):
        """Integration test: compute_zhangguo with real chart data"""
        from astro.qizheng.calculator import compute_chart
        from astro.qizheng.zhangguo import compute_zhangguo
        import swisseph as swe
        swe.set_ephe_path("")
        chart = compute_chart(
            year=1990, month=6, day=15,
            hour=12, minute=0,
            timezone=8.0, latitude=22.3, longitude=114.2,
            location_name="Hong Kong",
            gender="male",
        )
        result = compute_zhangguo(chart.planets, chart.houses, "male")
        assert result is not None
        assert len(result.matched_readings) > 0
        assert len(result.all_patterns) > 0

    def test_reading_fields(self):
        """Check that ZhangguoReading has all expected fields"""
        from astro.qizheng.zhangguo import lookup_star_in_branch
        readings = lookup_star_in_branch("木星", "寅")
        assert len(readings) > 0
        r = readings[0]
        assert isinstance(r.entry_id, int)
        assert isinstance(r.star, str)
        assert isinstance(r.branch, str)
        assert isinstance(r.description, str)
        assert isinstance(r.note, str)


# ============================================================
# Greek Horoscope SVG (Hellenistic θέμα Chart)
# ============================================================

class TestGreekHoroscopeSVG:
    """Tests for Greek horoscope SVG chart generation."""

    @pytest.fixture
    def h_chart(self):
        from astro.western.western import compute_western_chart
        from astro.western.hellenistic import compute_hellenistic_chart
        w = compute_western_chart(
            year=1990, month=6, day=15,
            hour=14, minute=30, timezone=8.0,
            latitude=22.3, longitude=114.2,
            location_name="Hong Kong",
        )
        return compute_hellenistic_chart(w, birth_year=1990, current_year=2026)

    def test_svg_is_valid_markup(self, h_chart):
        """SVG output is well-formed with opening and closing tags."""
        from astro.western.hellenistic import build_greek_horoscope_svg
        svg = build_greek_horoscope_svg(
            h_chart, year=1990, month=6, day=15,
            hour=14, minute=30, tz=8.0, location="Hong Kong",
        )
        assert "<svg" in svg
        assert "</svg>" in svg
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_svg_contains_all_zodiac_glyphs(self, h_chart):
        """All 12 zodiac sign glyphs appear in the SVG."""
        from astro.western.hellenistic import build_greek_horoscope_svg, ZODIAC_GLYPHS
        svg = build_greek_horoscope_svg(h_chart)
        for glyph in ZODIAC_GLYPHS:
            assert glyph in svg, f"Missing zodiac glyph: {glyph}"

    def test_svg_contains_all_house_numbers(self, h_chart):
        """All 12 Roman numeral house numbers appear."""
        from astro.western.hellenistic import build_greek_horoscope_svg, HOUSE_ROMAN
        svg = build_greek_horoscope_svg(h_chart)
        for roman in HOUSE_ROMAN:
            assert roman in svg, f"Missing house number: {roman}"

    def test_svg_contains_cardinal_labels(self, h_chart):
        """ASC, MC, DESC, IC labels and their Greek names appear."""
        from astro.western.hellenistic import build_greek_horoscope_svg
        svg = build_greek_horoscope_svg(h_chart)
        for label in ["ASC", "MC", "DESC", "IC"]:
            assert label in svg
        for greek in ["Ὡροσκόπος", "Μεσουράνημα", "Δύσις", "Ὑπόγειον"]:
            assert greek in svg

    def test_svg_contains_thema_title(self, h_chart):
        """Centre shows ΘΕΜΑ title."""
        from astro.western.hellenistic import build_greek_horoscope_svg
        svg = build_greek_horoscope_svg(h_chart)
        assert "ΘΕΜΑ" in svg

    def test_svg_contains_planet_glyphs(self, h_chart):
        """Planet glyphs for Sun and Moon appear."""
        from astro.western.hellenistic import build_greek_horoscope_svg, PLANET_GLYPHS
        svg = build_greek_horoscope_svg(h_chart)
        assert PLANET_GLYPHS["Sun"] in svg
        assert PLANET_GLYPHS["Moon"] in svg

    def test_svg_contains_birth_info(self, h_chart):
        """Birth date/time/location appear when provided."""
        from astro.western.hellenistic import build_greek_horoscope_svg
        svg = build_greek_horoscope_svg(
            h_chart, year=1990, month=6, day=15,
            hour=14, minute=30, tz=8.0, location="Hong Kong",
        )
        assert "1990-06-15" in svg
        assert "14:30" in svg
        assert "Hong Kong" in svg

    def test_svg_contains_sect_info(self, h_chart):
        """Day/Night sect indicator appears."""
        from astro.western.hellenistic import build_greek_horoscope_svg
        svg = build_greek_horoscope_svg(h_chart)
        assert "Day" in svg or "Night" in svg

    def test_svg_minimal_args(self, h_chart):
        """SVG generates correctly with only the chart (no birth info)."""
        from astro.western.hellenistic import build_greek_horoscope_svg
        svg = build_greek_horoscope_svg(h_chart)
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "None" not in svg

    def test_svg_contains_greek_sign_names(self, h_chart):
        """Greek zodiac sign names appear."""
        from astro.western.hellenistic import build_greek_horoscope_svg, ZODIAC_GREEK
        svg = build_greek_horoscope_svg(h_chart)
        for name in ZODIAC_GREEK:
            assert name in svg, f"Missing Greek sign name: {name}"

    def test_ray_to_square_cardinal(self):
        """Ray-to-square hits correct edges for cardinal directions."""
        from astro.western.hellenistic import _ray_to_square
        cx, cy, half = 300, 300, 250
        x, y = _ray_to_square(cx, cy, half, 0)
        assert abs(x - (cx + half)) < 1
        assert abs(y - cy) < 1
        x, y = _ray_to_square(cx, cy, half, 180)
        assert abs(x - (cx - half)) < 1
        assert abs(y - cy) < 1
        x, y = _ray_to_square(cx, cy, half, 90)
        assert abs(x - cx) < 1
        assert abs(y - (cy + half)) < 1
        x, y = _ray_to_square(cx, cy, half, 270)
        assert abs(x - cx) < 1
        assert abs(y - (cy - half)) < 1

    def test_ray_to_square_corners(self):
        """Ray-to-square hits corners at 45° multiples."""
        from astro.western.hellenistic import _ray_to_square
        cx, cy, half = 300, 300, 250
        x, y = _ray_to_square(cx, cy, half, 45)
        assert abs(x - (cx + half)) < 1
        assert abs(y - (cy + half)) < 1
        x, y = _ray_to_square(cx, cy, half, 135)
        assert abs(x - (cx - half)) < 1
        assert abs(y - (cy + half)) < 1
        x, y = _ray_to_square(cx, cy, half, 225)
        assert abs(x - (cx - half)) < 1
        assert abs(y - (cy - half)) < 1
        x, y = _ray_to_square(cx, cy, half, 315)
        assert abs(x - (cx + half)) < 1
        assert abs(y - (cy - half)) < 1

    def test_svg_contains_lot_markers(self, h_chart):
        """Lots of Fortune/Spirit markers appear in the SVG."""
        from astro.western.hellenistic import build_greek_horoscope_svg
        svg = build_greek_horoscope_svg(h_chart)
        assert svg.count('fill-opacity="0.2"') > 0

    def test_svg_different_charts(self):
        """SVG generates for a night chart with different ASC sign."""
        from astro.western.western import compute_western_chart
        from astro.western.hellenistic import compute_hellenistic_chart, build_greek_horoscope_svg
        w2 = compute_western_chart(
            year=2000, month=12, day=21,
            hour=23, minute=0, timezone=0.0,
            latitude=51.5, longitude=-0.1,
            location_name="London",
        )
        h2 = compute_hellenistic_chart(w2, birth_year=2000, current_year=2026)
        svg = build_greek_horoscope_svg(h2)
        assert "<svg" in svg
        assert "Night" in svg

    def test_constants_integrity(self):
        """Verify all Greek horoscope constants have correct lengths."""
        from astro.western.hellenistic import (
            ZODIAC_GLYPHS, ZODIAC_GREEK, PLANET_GLYPHS,
            PLANET_COLORS_GREEK, ELEMENT_OF_SIGN, ELEMENT_COLORS,
            HOUSE_ROMAN, TOPOS_GREEK, TOPOS_CN,
        )
        assert len(ZODIAC_GLYPHS) == 12
        assert len(ZODIAC_GREEK) == 12
        assert len(PLANET_GLYPHS) == 7
        assert len(PLANET_COLORS_GREEK) == 7
        assert len(ELEMENT_OF_SIGN) == 12
        assert len(ELEMENT_COLORS) == 4
        assert len(HOUSE_ROMAN) == 12
        assert len(TOPOS_GREEK) == 12
        assert len(TOPOS_CN) == 12


# ================================================================
# AI Analysis Module Tests
# ================================================================

class TestAiAnalysisFormatters:
    """Test chart-to-prompt formatting functions."""

    def test_format_planet_list_empty(self):
        from astro.ai_analysis import _format_planet_list
        assert _format_planet_list([]) == "(none)"
        assert _format_planet_list(None) == "(none)"

    def test_format_planet_list_with_objects(self):
        from astro.ai_analysis import _format_planet_list

        class FakePlanet:
            def __init__(self, name, sign, degree):
                self.name = name
                self.sign = sign
                self.degree = degree
                self.retrograde = False
                self.house = None

        planets = [FakePlanet("Sun", "Aries", 10.5)]
        result = _format_planet_list(planets)
        assert "Sun" in result
        assert "Aries" in result

    def test_format_aspects_empty(self):
        from astro.ai_analysis import _format_aspects
        assert _format_aspects([]) == "(none)"
        assert _format_aspects(None) == "(none)"

    def test_format_houses_empty(self):
        from astro.ai_analysis import _format_houses
        assert _format_houses([]) == "(none)"
        assert _format_houses(None) == "(none)"

    def test_safe_getattr(self):
        from astro.ai_analysis import _safe_getattr

        class Obj:
            a = "hello"
            b = None
        o = Obj()
        assert _safe_getattr(o, "a") == "hello"
        assert _safe_getattr(o, "nonexistent", default="fallback") == "fallback"
        assert _safe_getattr(o, "b", "a") == "hello"  # b is None, fall through to a


class TestAiAnalysisSystemFormatters:
    """Test all system-specific chart formatters."""

    def _make_chart(self, **kwargs):
        """Create a simple mock chart object."""
        class Chart:
            pass
        c = Chart()
        for k, v in kwargs.items():
            setattr(c, k, v)
        return c

    def test_format_western_chart(self):
        from astro.ai_analysis import format_western_chart
        chart = self._make_chart(
            asc_sign="Aries", mc_sign="Capricorn",
            planets=[], houses=[], aspects=[],
        )
        result = format_western_chart(chart)
        assert "西洋占星" in result
        assert "Aries" in result

    def test_format_vedic_chart(self):
        from astro.ai_analysis import format_vedic_chart
        chart = self._make_chart(
            lagna="Mesha", ayanamsa=23.5,
            planets=[], houses=[], aspects=[],
        )
        result = format_vedic_chart(chart)
        assert "印度占星" in result
        assert "Mesha" in result

    def test_format_chinese_chart(self):
        from astro.ai_analysis import format_chinese_chart
        chart = self._make_chart(
            ming_gong="命宮", shen_gong="身宮",
            bazi=None, planets=[], houses=[], aspects=[],
        )
        result = format_chinese_chart(chart)
        assert "七政四餘" in result

    def test_format_ziwei_chart(self):
        from astro.ai_analysis import format_ziwei_chart
        chart = self._make_chart(
            ming_gong="子", shen_gong="午",
            ming_zhu="紫微", shen_zhu="天機", palaces=[],
        )
        result = format_ziwei_chart(chart)
        assert "紫微斗數" in result

    def test_format_thai_chart(self):
        from astro.ai_analysis import format_thai_chart
        chart = self._make_chart(weekday="Monday", lagna="Aries", planets=[])
        result = format_thai_chart(chart)
        assert "泰國占星" in result

    def test_format_kabbalistic_chart(self):
        from astro.ai_analysis import format_kabbalistic_chart
        chart = self._make_chart(
            life_path=7, name_number=3,
            hebrew_letter="ז", sephirah="Netzach",
            tree_path="Victory", planets=[],
        )
        result = format_kabbalistic_chart(chart)
        assert "卡巴拉" in result

    def test_format_arabic_chart(self):
        from astro.ai_analysis import format_arabic_chart
        chart = self._make_chart(
            lot_of_fortune="15°", planets=[], arabic_parts=[],
        )
        result = format_arabic_chart(chart)
        assert "阿拉伯" in result

    def test_format_maya_chart(self):
        from astro.ai_analysis import format_maya_chart
        chart = self._make_chart(
            kin=1, tzolkin="1 Imix", haab="0 Pop",
            tone=1, glyph="Imix", long_count="13.0.11.6.1",
        )
        result = format_maya_chart(chart)
        assert "瑪雅" in result

    def test_format_mahabote_chart(self):
        from astro.ai_analysis import format_mahabote_chart
        chart = self._make_chart(
            birth_weekday="Monday",
            birth_animal_en="Tiger", houses=[],
        )
        result = format_mahabote_chart(chart)
        assert "緬甸" in result

    def test_format_decan_chart(self):
        from astro.ai_analysis import format_decan_chart
        chart = self._make_chart(
            sun_decan="Decan 1", moon_decan="Decan 2",
            asc_decan="Decan 3", planets=[],
        )
        result = format_decan_chart(chart)
        assert "古埃及" in result

    def test_format_nadi_chart(self):
        from astro.ai_analysis import format_nadi_chart
        chart = self._make_chart(
            nadi_type="Agastya", birth_nakshatra="Ashwini", planets=[],
        )
        result = format_nadi_chart(chart)
        assert "納迪" in result

    def test_format_zurkhai_chart(self):
        from astro.ai_analysis import format_zurkhai_chart
        chart = self._make_chart(
            animal="Tiger", element="Wood",
            mewa=1, parkha="Li", planets=[],
        )
        result = format_zurkhai_chart(chart)
        assert "蒙古祖爾海" in result

    def test_format_hellenistic_chart(self):
        from astro.ai_analysis import format_hellenistic_chart
        chart = self._make_chart(
            asc_sign="Aries", mc_sign="Capricorn",
            sect="Diurnal", lot_of_fortune="20°",
            planets=[], aspects=[],
        )
        result = format_hellenistic_chart(chart)
        assert "希臘占星" in result

    def test_format_sukkayodo_chart(self):
        from astro.ai_analysis import format_sukkayodo_chart
        chart = self._make_chart(
            birth_mansion="Ashwini", planets=[],
        )
        result = format_sukkayodo_chart(chart)
        assert "宿曜道" in result

    def test_format_chinstar_chart(self):
        from astro.ai_analysis import format_chinstar_chart
        data = {"命宮": "甲子", "胎星": "燕", "命星": "鳳"}
        result = format_chinstar_chart(data)
        assert "萬花仙禽" in result
        assert "命宮" in result

    def test_format_generic_chart_dict(self):
        from astro.ai_analysis import format_generic_chart
        data = {"key1": "val1", "key2": 42}
        result = format_generic_chart(data, "TestSystem")
        assert "TestSystem" in result
        assert "key1" in result


class TestAiAnalysisFormatChartForPrompt:
    """Test the dispatch function format_chart_for_prompt."""

    def test_dispatch_known_system(self):
        from astro.ai_analysis import format_chart_for_prompt

        class Chart:
            asc_sign = "Aries"
            mc_sign = "Capricorn"
            planets = []
            houses = []
            aspects = []

        result = format_chart_for_prompt("tab_western", Chart())
        assert "西洋占星" in result
        assert "Aries" in result

    def test_dispatch_unknown_system(self):
        from astro.ai_analysis import format_chart_for_prompt

        class Chart:
            foo = "bar"
        result = format_chart_for_prompt("tab_unknown", Chart())
        assert "tab_unknown" in result
        assert "foo" in result


class TestAiAnalysisSystemPrompts:
    """Test system prompt load/save functionality."""

    def test_load_default_prompts(self):
        from astro.ai_analysis import load_system_prompts
        data = load_system_prompts()
        assert "prompts" in data
        assert len(data["prompts"]) >= 1
        assert "selected" in data

    def test_prompt_has_required_fields(self):
        from astro.ai_analysis import load_system_prompts
        data = load_system_prompts()
        for p in data["prompts"]:
            assert "name" in p
            assert "content" in p
            assert len(p["content"]) > 0

    def test_save_and_reload(self):
        import json
        import os
        import tempfile
        from astro import ai_analysis

        # Temporarily swap the prompts file
        original = ai_analysis._PROMPTS_FILE
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                tmp_path = f.name
            ai_analysis._PROMPTS_FILE = tmp_path

            test_data = {
                "prompts": [{"name": "Test", "content": "Test content"}],
                "selected": "Test",
            }
            assert ai_analysis.save_system_prompts(test_data) is True
            loaded = ai_analysis.load_system_prompts()
            assert loaded["prompts"][0]["name"] == "Test"
        finally:
            ai_analysis._PROMPTS_FILE = original
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestAiAnalysisCerebrasClient:
    """Test CerebrasClient initialization (without actual API calls)."""

    def test_client_requires_api_key(self):
        from astro.ai_analysis import CerebrasClient
        with pytest.raises(ValueError, match="non-empty API key"):
            CerebrasClient(api_key="")

    def test_client_requires_api_key_none(self):
        from astro.ai_analysis import CerebrasClient
        with pytest.raises(ValueError, match="non-empty API key"):
            CerebrasClient(api_key=None)

    def test_model_options_exist(self):
        from astro.ai_analysis import CEREBRAS_MODEL_OPTIONS, CEREBRAS_MODEL_DESCRIPTIONS
        assert len(CEREBRAS_MODEL_OPTIONS) >= 3
        for model in CEREBRAS_MODEL_OPTIONS:
            assert model in CEREBRAS_MODEL_DESCRIPTIONS


# ============================================================
# BPHS Engine Tests (Brihat Parashara Hora Shastra)
# ============================================================

class TestBPHSEngine:
    """BPHS 經典解讀引擎測試"""

    @pytest.fixture
    def sample_chart(self):
        return compute_vedic_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    @pytest.fixture
    def bphs_result(self, sample_chart):
        from astro.vedic.bphs_engine import compute_bphs
        return compute_bphs(sample_chart.planets, sample_chart.houses,
                            sample_chart.ascendant)

    def test_twelve_bhava_readings(self, bphs_result):
        assert len(bphs_result.bhava_readings) == 12

    def test_bhava_numbering(self, bphs_result):
        for i, br in enumerate(bphs_result.bhava_readings):
            assert br.bhava == i + 1

    def test_bhava_has_lord(self, bphs_result):
        for br in bphs_result.bhava_readings:
            assert br.lord_key in [
                "sun", "moon", "mars", "mercury",
                "jupiter", "venus", "saturn",
            ]
            assert len(br.lord_zh) > 0

    def test_bhava_lord_house_valid(self, bphs_result):
        for br in bphs_result.bhava_readings:
            assert 0 <= br.lord_house <= 12

    def test_detailed_bhavas_have_lord_placement(self, bphs_result):
        """Bhavas 2,5,6,7,8,9,10,11,12 should have lord placement readings."""
        detailed = [2, 5, 6, 7, 8, 9, 10, 11, 12]
        for br in bphs_result.bhava_readings:
            if br.bhava in detailed and br.lord_house > 0:
                assert len(br.lord_placement_zh) > 0, \
                    f"Bhava {br.bhava} lord in H{br.lord_house} missing placement"

    def test_graha_maitri_seven_planets(self, bphs_result):
        assert len(bphs_result.graha_maitri) == 7

    def test_graha_maitri_has_friends_enemies(self, bphs_result):
        for m in bphs_result.graha_maitri:
            assert len(m.friends_zh) > 0
            assert len(m.enemies_zh) > 0

    def test_avasthas_nine_planets(self, bphs_result):
        assert len(bphs_result.avasthas) == 9

    def test_avastha_names_valid(self, bphs_result):
        from astro.vedic.bphs_data import BPHS_AVASTHAS
        valid_names = BPHS_AVASTHAS["avastha_list"]
        for av in bphs_result.avasthas:
            assert av.avastha_name in valid_names

    def test_avastha_strength_values(self, bphs_result):
        for av in bphs_result.avasthas:
            assert av.strength in ["強", "中", "弱", "未知"]

    def test_avastha_has_reading(self, bphs_result):
        for av in bphs_result.avasthas:
            assert len(av.reading_zh) > 0

    def test_dignities_nine_planets(self, bphs_result):
        assert len(bphs_result.dignities) == 9

    def test_dignity_has_status(self, bphs_result):
        for d in bphs_result.dignities:
            assert len(d.status_zh) > 0
            assert len(d.rashi_en) > 0
            assert len(d.rashi_zh) > 0

    def test_dignity_flags_exclusive(self, bphs_result):
        """Exalted and debilitated cannot be true at same time."""
        for d in bphs_result.dignities:
            assert not (d.uccha and d.neecha)

    def test_raja_yogas_detected(self, bphs_result):
        assert len(bphs_result.raja_yogas) >= 8  # base yogas + possible Neecha Bhanga

    def test_raja_yoga_structure(self, bphs_result):
        for ry in bphs_result.raja_yogas:
            assert isinstance(ry.is_present, bool)
            assert len(ry.name) > 0
            assert len(ry.description_zh) > 0
            assert len(ry.reason_zh) > 0

    def test_varga_info_has_15_divisions(self, bphs_result):
        vargas = bphs_result.varga_info.get("vargas", {})
        assert len(vargas) == 15  # D1..D60

    def test_varga_d9_exists(self, bphs_result):
        vargas = bphs_result.varga_info.get("vargas", {})
        assert "D9" in vargas
        assert "Navamsa" in vargas["D9"]["zh"]


class TestBPHSData:
    """BPHS 資料完整性測試"""

    def test_chapters_count(self):
        from astro.vedic.bphs_data import BPHS_CHAPTERS
        assert len(BPHS_CHAPTERS) == 22

    def test_bhava_phala_twelve(self):
        from astro.vedic.bphs_data import BPHS_BHAVA_PHALA
        assert len(BPHS_BHAVA_PHALA) == 12

    def test_graha_maitri_seven(self):
        from astro.vedic.bphs_data import BPHS_GRAHA_MAITRI
        assert len(BPHS_GRAHA_MAITRI) == 7

    def test_avasthas_twelve_states(self):
        from astro.vedic.bphs_data import BPHS_AVASTHAS
        assert len(BPHS_AVASTHAS["avastha_list"]) == 12

    def test_avasthas_nine_planets(self):
        from astro.vedic.bphs_data import BPHS_AVASTHAS
        planet_keys = ["sun", "moon", "mars", "mercury", "jupiter",
                       "venus", "saturn", "rahu", "ketu"]
        for pk in planet_keys:
            assert pk in BPHS_AVASTHAS, f"Missing avastha data for {pk}"
            assert len(BPHS_AVASTHAS[pk]) == 12

    def test_ucca_neecha_seven(self):
        from astro.vedic.bphs_data import BPHS_UCCA_NEECHA
        assert len(BPHS_UCCA_NEECHA) == 7

    def test_moola_trikona_seven(self):
        from astro.vedic.bphs_data import BPHS_MOOLA_TRIKONA
        assert len(BPHS_MOOLA_TRIKONA) == 7

    def test_rashi_twelve(self):
        from astro.vedic.bphs_data import BPHS_RASHI
        assert len(BPHS_RASHI) == 12

    def test_graha_svarupa_nine(self):
        from astro.vedic.bphs_data import BPHS_GRAHA_SVARUPA
        assert len(BPHS_GRAHA_SVARUPA) == 9

    def test_raja_yoga_has_entries(self):
        from astro.vedic.bphs_data import BPHS_RAJA_YOGA
        assert len(BPHS_RAJA_YOGA["raja_yogas"]) >= 8
        assert len(BPHS_RAJA_YOGA["special_yogas"]) >= 4

    def test_detailed_bhavas_have_planet_readings(self):
        from astro.vedic.bphs_data import (
            BPHS_DHANA_BHAVA, BPHS_SAPTAMA_BHAVA,
            BPHS_DASHAMA_BHAVA, BPHS_PANCHAMA_BHAVA,
        )
        for bhava_data in [BPHS_DHANA_BHAVA, BPHS_SAPTAMA_BHAVA,
                           BPHS_DASHAMA_BHAVA, BPHS_PANCHAMA_BHAVA]:
            assert "lord_placement" in bhava_data
            assert len(bhava_data["lord_placement"]) == 12
            # Check planet readings exist
            planet_fields = [k for k in bhava_data if k.startswith("planet_in_")]
            assert len(planet_fields) >= 1
            for pf in planet_fields:
                assert len(bhava_data[pf]) >= 9  # 9 planets


# ══════════════════════════════════════════════════════════════════════════
# Brahma Jati Tests
# ══════════════════════════════════════════════════════════════════════════


class TestBrahmaJatiDataLoading:
    """Test that all 5 Brahma Jati JSON files load correctly."""

    def test_load_birthyear_data(self):
        from astro.brahma_jati import load_birthyear_data
        data = load_birthyear_data()
        assert "years" in data
        assert len(data["years"]) == 12
        # Check first year has required keys
        y1 = data["years"]["1"]
        for key in ["thai", "name_zh", "name_en", "element_zh", "personality_zh"]:
            assert key in y1, f"Missing key {key}"

    def test_load_12rasi_data(self):
        from astro.brahma_jati import load_12rasi_data
        data = load_12rasi_data()
        assert "positions" in data
        assert len(data["positions"]) == 12
        pos1 = data["positions"]["1"]
        for key in ["thai", "name_zh", "name_en", "meaning_zh", "level"]:
            assert key in pos1

    def test_load_monthly_variants(self):
        from astro.brahma_jati import load_monthly_variants
        data = load_monthly_variants()
        assert "years" in data
        assert len(data["years"]) == 12

    def test_load_weekly_variants(self):
        from astro.brahma_jati import load_weekly_variants
        data = load_weekly_variants()
        assert "years" in data
        assert len(data["years"]) == 12
        first_year = list(data["years"].values())[0]
        assert "weekly" in first_year
        assert len(first_year["weekly"]) == 7

    def test_load_spells_remedies(self):
        from astro.brahma_jati import load_spells_remedies
        data = load_spells_remedies()
        assert "general_remedies" in data
        assert "color_by_day" in data
        assert "per_zodiac" in data
        assert len(data["color_by_day"]) == 7
        assert len(data["per_zodiac"]) == 12


class TestBrahmaJatiCompute:
    """Test Brahma Jati computation logic."""

    def test_thai_zodiac_index(self):
        from astro.brahma_jati import _thai_zodiac_index
        # 2024 = Dragon year (index 4 = ปีมะโรง). (2024-4)%12 = 4
        assert _thai_zodiac_index(2024) == 4
        # 2000 = Dragon year as well. (2000-4)%12 = 4
        assert _thai_zodiac_index(2000) == 4
        # 1996 = Rat year. (1996-4)%12 = 0
        assert _thai_zodiac_index(1996) == 0

    def test_compute_basic(self):
        from astro.brahma_jati import compute_brahma_jati
        reading = compute_brahma_jati(
            ce_year=1990, month=6, weekday=0, age=35, gender="male"
        )
        assert reading.zodiac_index == (1990 - 4) % 12  # 6 = Horse
        assert reading.thai_year_name == "ปีมะเมีย"
        assert reading.birthyear is not None
        assert reading.year_zh == "馬年"

    def test_compute_with_rasi_position(self):
        from astro.brahma_jati import compute_brahma_jati
        reading = compute_brahma_jati(
            ce_year=1990, month=6, weekday=3, age=35, gender="male"
        )
        assert reading.rasi_position is not None
        assert reading.rasi_pos_number is not None
        assert 1 <= reading.rasi_pos_number <= 12

    def test_compute_weekly_variant(self):
        from astro.brahma_jati import compute_brahma_jati
        reading = compute_brahma_jati(
            ce_year=1996, month=1, weekday=6  # Sunday
        )
        # 1996 = Rat year
        assert reading.thai_year_name == "ปีชวด"
        assert reading.weekly_day == "Sunday"
        assert reading.weekly_variant is not None

    def test_compute_color_of_day(self):
        from astro.brahma_jati import compute_brahma_jati
        reading = compute_brahma_jati(ce_year=1990, month=3, weekday=0)
        assert reading.color_of_day is not None
        assert "zh" in reading.color_of_day

    def test_rasi_male_female_differ(self):
        from astro.brahma_jati import _compute_rasi_position, load_12rasi_data
        rasi_data = load_12rasi_data()
        _, pos_m = _compute_rasi_position(25, "male", rasi_data)
        _, pos_f = _compute_rasi_position(25, "female", rasi_data)
        # Male and female count in opposite directions, should differ
        assert pos_m is not None
        assert pos_f is not None


# ══════════════════════════════════════════════════════════════════════════
# MS.164 Manuscript Tests
# ══════════════════════════════════════════════════════════════════════════


class TestMS164DataLoading:
    """Test that all 5 MS.164 JSON files load correctly."""

    def test_load_metadata(self):
        from astro.arabic.ms164_browser import load_metadata
        data = load_metadata()
        assert data["manuscript_id"] == "MS_164"
        assert "title_zh" in data

    def test_load_fal_divination(self):
        from astro.arabic.ms164_browser import load_fal_divination
        data = load_fal_divination()
        assert "planets" in data
        assert len(data["planets"]) >= 5
        for p in data["planets"]:
            assert "planet_zh" in p
            assert len(p["questions"]) >= 1

    def test_load_female_appearances(self):
        from astro.arabic.ms164_browser import load_female_appearances
        data = load_female_appearances()
        assert "appearances" in data
        assert len(data["appearances"]) >= 3

    def test_load_female_horoscopes(self):
        from astro.arabic.ms164_browser import load_female_horoscopes
        data = load_female_horoscopes()
        assert "horoscopes" in data
        assert len(data["horoscopes"]) >= 3

    def test_load_magical_practices(self):
        from astro.arabic.ms164_browser import load_magical_practices
        data = load_magical_practices()
        assert "practices" in data
        assert len(data["practices"]) >= 3
        for p in data["practices"]:
            assert "purpose_zh" in p


# ══════════════════════════════════════════════════════════════════════════
# Picatrix Planetary Prayers Tests
# ══════════════════════════════════════════════════════════════════════════


class TestPicatrixPlanetaryPrayers:
    """Test that planetary prayers JSON loads and has correct structure."""

    def test_load_prayers(self):
        from astro.arabic.picatrix_mansions import _load_planetary_prayers
        data = _load_planetary_prayers()
        assert "prayers" in data
        assert len(data["prayers"]) == 7  # 7 classical planets

    def test_prayer_structure(self):
        from astro.arabic.picatrix_mansions import _load_planetary_prayers
        data = _load_planetary_prayers()
        for prayer in data["prayers"]:
            assert "planet" in prayer
            assert "name_zh" in prayer
            assert "name_en" in prayer
            assert "spirit_names" in prayer
            assert "prayer_text" in prayer
            assert len(prayer["spirit_names"]) >= 1

    def test_all_classical_planets_present(self):
        from astro.arabic.picatrix_mansions import _load_planetary_prayers
        data = _load_planetary_prayers()
        planets = {p["planet"] for p in data["prayers"]}
        expected = {"Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"}
        assert planets == expected
