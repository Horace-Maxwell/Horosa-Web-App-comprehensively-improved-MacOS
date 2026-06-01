"""
tests/test_maya.py — 瑪雅占星模組測試
(Maya Astrology Module Tests)

測試 Tzolk'in、Long Count、Haab、Calendar Round 計算的正確性。
Tests correctness of Tzolk'in, Long Count, Haab, and Calendar Round calculations.

GMT correlation verification:
  JD 584283 = Long Count 0.0.0.0.0 = 4 Ajaw 8 Kumku
"""

import math
import pytest
import swisseph as swe

from astro.maya.tzolkin import compute_tzolkin, compute_haab, compute_calendar_round
from astro.maya.long_count import jd_to_long_count, long_count_to_jd, parse_long_count
from astro.maya.constants import MAYAN_EPOCH_JD, TZOLKIN_DAY_DATA, HAAB_MONTHS


# ============================================================
# Long Count Tests
# ============================================================

class TestLongCount:
    """Long Count 計算測試"""

    def test_epoch_is_zero(self):
        """JD 584283 should give 0.0.0.0.0"""
        lc = jd_to_long_count(MAYAN_EPOCH_JD)
        assert lc.baktun == 0
        assert lc.katun == 0
        assert lc.tun == 0
        assert lc.winal == 0
        assert lc.kin == 0
        assert lc.date_str == "0.0.0.0.0"

    def test_one_day(self):
        """JD 584284 should give 0.0.0.0.1"""
        lc = jd_to_long_count(MAYAN_EPOCH_JD + 1)
        assert lc.kin == 1
        assert lc.date_str == "0.0.0.0.1"

    def test_one_winal(self):
        """20 days from epoch = 0.0.0.1.0"""
        lc = jd_to_long_count(MAYAN_EPOCH_JD + 20)
        assert lc.winal == 1
        assert lc.kin == 0

    def test_one_tun(self):
        """360 days from epoch = 0.0.1.0.0"""
        lc = jd_to_long_count(MAYAN_EPOCH_JD + 360)
        assert lc.tun == 1
        assert lc.winal == 0
        assert lc.kin == 0

    def test_one_katun(self):
        """7200 days from epoch = 0.1.0.0.0"""
        lc = jd_to_long_count(MAYAN_EPOCH_JD + 7200)
        assert lc.katun == 1
        assert lc.tun == 0

    def test_one_baktun(self):
        """144000 days from epoch = 1.0.0.0.0"""
        lc = jd_to_long_count(MAYAN_EPOCH_JD + 144000)
        assert lc.baktun == 1
        assert lc.katun == 0

    def test_13_baktun(self):
        """Long Count at 13.0.0.0.0 (Dec 21 2012 transition)"""
        lc = jd_to_long_count(MAYAN_EPOCH_JD + 13 * 144000)
        assert lc.baktun == 13
        assert lc.katun == 0
        assert lc.date_str == "13.0.0.0.0"

    def test_round_trip(self):
        """jd_to_long_count and long_count_to_jd are inverse operations"""
        test_cases = [
            (0, 0, 0, 0, 0),
            (13, 0, 0, 0, 0),
            (9, 12, 11, 5, 18),
            (13, 0, 11, 4, 1),
        ]
        for baktun, katun, tun, winal, kin in test_cases:
            jd = long_count_to_jd(baktun, katun, tun, winal, kin)
            lc = jd_to_long_count(jd)
            assert lc.baktun == baktun
            assert lc.katun == katun
            assert lc.tun == tun
            assert lc.winal == winal
            assert lc.kin == kin

    def test_parse_long_count(self):
        """parse_long_count correctly parses string format"""
        result = parse_long_count("13.0.7.15.3")
        assert result == (13, 0, 7, 15, 3)

    def test_parse_long_count_invalid(self):
        """parse_long_count returns None for invalid input"""
        assert parse_long_count("bad") is None
        assert parse_long_count("1.2.3") is None
        assert parse_long_count("") is None

    def test_total_kins(self):
        """total_kins field is correct"""
        lc = jd_to_long_count(MAYAN_EPOCH_JD + 12345)
        assert lc.total_kins == 12345

    def test_progress_bounds(self):
        """Progress values are between 0 and 1"""
        lc = jd_to_long_count(MAYAN_EPOCH_JD + 50000)
        assert 0.0 <= lc.progress_in_baktun <= 1.0
        assert 0.0 <= lc.progress_in_katun <= 1.0


# ============================================================
# Tzolk'in Tests
# ============================================================

class TestTzolkin:
    """Tzolk'in 計算測試（GMT Correlation 驗證）"""

    def test_epoch_is_4_ajaw(self):
        """At JD 584283, Tzolk'in should be 4 Ajaw (GMT correlation)"""
        tz = compute_tzolkin(MAYAN_EPOCH_JD)
        assert tz.number == 4, f"Expected number=4 (Ajaw), got {tz.number}"
        assert tz.sign_name == "Ajaw", f"Expected sign=Ajaw, got {tz.sign_name}"
        assert tz.sign_index == 19

    def test_next_day_is_5_imix(self):
        """Day after 4 Ajaw should be 5 Imix"""
        tz = compute_tzolkin(MAYAN_EPOCH_JD + 1)
        assert tz.number == 5
        assert tz.sign_name == "Imix"
        assert tz.sign_index == 0

    def test_260_day_cycle(self):
        """260 days after epoch gives same Tzolk'in position"""
        tz0 = compute_tzolkin(MAYAN_EPOCH_JD)
        tz1 = compute_tzolkin(MAYAN_EPOCH_JD + 260)
        assert tz0.number == tz1.number
        assert tz0.sign_index == tz1.sign_index

    def test_number_range(self):
        """Numbers cycle 1–13"""
        for d in range(26):
            tz = compute_tzolkin(MAYAN_EPOCH_JD + d)
            assert 1 <= tz.number <= 13

    def test_sign_index_range(self):
        """Sign index cycles 0–19"""
        for d in range(40):
            tz = compute_tzolkin(MAYAN_EPOCH_JD + d)
            assert 0 <= tz.sign_index <= 19

    def test_day_position_range(self):
        """Day position is always 0–259"""
        for d in range(520):
            tz = compute_tzolkin(MAYAN_EPOCH_JD + d)
            assert 0 <= tz.day_position <= 259

    def test_known_date_verification(self):
        """
        Verify known historical dates using GMT correlation.

        Pakal's birth: LC 9.8.9.13.0 = 8 Ajaw 13 Pop
        (recorded on the Palenque sarcophagus lid inscriptions)
        """
        jd_pakal = long_count_to_jd(9, 8, 9, 13, 0)
        tz = compute_tzolkin(jd_pakal)
        assert tz.sign_name == "Ajaw", f"Expected sign=Ajaw, got {tz.sign_name}"
        assert tz.number == 8, f"Expected number=8 (8 Ajaw), got {tz.number}"

    def test_13_baktun_transition_is_4_ajaw(self):
        """13.0.0.0.0 (Dec 21 2012 transition) should be 4 Ajaw"""
        jd = long_count_to_jd(13, 0, 0, 0, 0)
        tz = compute_tzolkin(jd)
        assert tz.number == 4
        assert tz.sign_name == "Ajaw"

    def test_rich_data_populated(self):
        """TzolkinDay dataclass has all rich interpretation fields"""
        tz = compute_tzolkin(MAYAN_EPOCH_JD)
        assert tz.personality_cn
        assert tz.destiny_cn
        assert tz.mythology_cn
        assert tz.color.startswith("#")
        assert tz.deity
        assert tz.number_name_cn
        assert tz.number_tone_cn


# ============================================================
# Haab Tests
# ============================================================

class TestHaab:
    """Haab 民用曆計算測試"""

    def test_epoch_is_8_kumku(self):
        """At JD 584283, Haab should be 8 Kumku (GMT correlation)"""
        haab = compute_haab(MAYAN_EPOCH_JD)
        assert haab.day_of_month == 8
        assert haab.month_name == "KUMKU"
        assert haab.month_index == 17

    def test_365_day_cycle(self):
        """365 days after epoch gives same Haab position"""
        h0 = compute_haab(MAYAN_EPOCH_JD)
        h1 = compute_haab(MAYAN_EPOCH_JD + 365)
        assert h0.day_of_month == h1.day_of_month
        assert h0.month_index == h1.month_index

    def test_day_of_year_range(self):
        """Day of year is always 0–364"""
        for d in range(730):
            haab = compute_haab(MAYAN_EPOCH_JD + d)
            assert 0 <= haab.day_of_year <= 364

    def test_wayeb_detection(self):
        """Wayeb (5 unlucky days) is month index 18"""
        # Find a Wayeb day: haab_pos = 360..364
        # (d + 348) % 365 >= 360 → d ≡ 12..16 (mod 365)
        for d in range(365):
            haab = compute_haab(MAYAN_EPOCH_JD + d)
            if haab.month_index == 18:
                assert haab.day_of_month <= 4
                break
        else:
            pytest.fail("No Wayeb day found in 365-day cycle")

    def test_date_str_format(self):
        """date_str is formatted correctly"""
        haab = compute_haab(MAYAN_EPOCH_JD)
        assert haab.date_str == "8 KUMKU"


# ============================================================
# Calendar Round Tests
# ============================================================

class TestCalendarRound:
    """Calendar Round 測試"""

    def test_epoch_calendar_round(self):
        """At epoch: Calendar Round = 4 Ajaw 8 Kumku"""
        cr = compute_calendar_round(MAYAN_EPOCH_JD)
        assert cr.tzolkin.number == 4
        assert cr.tzolkin.sign_name == "Ajaw"
        assert cr.haab.day_of_month == 8
        assert cr.haab.month_name == "KUMKU"

    def test_18980_day_repeat(self):
        """Calendar Round repeats every 18,980 days"""
        cr0 = compute_calendar_round(MAYAN_EPOCH_JD)
        cr1 = compute_calendar_round(MAYAN_EPOCH_JD + 18980)
        assert cr0.tzolkin.number == cr1.tzolkin.number
        assert cr0.tzolkin.sign_index == cr1.tzolkin.sign_index
        assert cr0.haab.day_of_month == cr1.haab.day_of_month
        assert cr0.haab.month_index == cr1.haab.month_index

    def test_round_str_format(self):
        """Calendar Round string contains both Tzolk'in and Haab"""
        cr = compute_calendar_round(MAYAN_EPOCH_JD)
        assert "Ajaw" in cr.round_str
        assert "KUMKU" in cr.round_str


# ============================================================
# Constants Integrity Tests
# ============================================================

class TestConstants:
    """常量完整性測試"""

    def test_tzolkin_day_data_count(self):
        """TZOLKIN_DAY_DATA has exactly 20 entries"""
        assert len(TZOLKIN_DAY_DATA) == 20

    def test_tzolkin_indices_sequential(self):
        """Day sign indices are 0–19 in order"""
        for i, d in enumerate(TZOLKIN_DAY_DATA):
            assert d["index"] == i

    def test_haab_months_count(self):
        """HAAB_MONTHS has exactly 19 entries (18 + Wayeb)"""
        assert len(HAAB_MONTHS) == 19

    def test_tzolkin_day_data_fields(self):
        """All TZOLKIN_DAY_DATA entries have required fields"""
        required = {
            "index", "name", "name_cn", "name_en", "glyph_emoji",
            "element", "element_cn", "direction", "direction_cn", "color",
            "deity", "deity_cn", "personality_cn", "personality_en",
            "destiny_cn", "destiny_en", "mythology_cn", "mythology_en",
        }
        for d in TZOLKIN_DAY_DATA:
            for field in required:
                assert field in d, f"Missing field '{field}' in day sign {d.get('name')}"

    def test_colors_are_hex(self):
        """All day sign colors are valid hex strings"""
        for d in TZOLKIN_DAY_DATA:
            assert d["color"].startswith("#"), f"Invalid color {d['color']} for {d['name']}"
            assert len(d["color"]) in (4, 7), f"Invalid hex length for {d['name']}"


# ============================================================
# Integration Test (no Streamlit dependency)
# ============================================================

class TestIntegration:
    """統合測試（無 Streamlit 依賴）"""

    @pytest.fixture
    def sample_jd(self):
        """A sample Julian Day for 1990-01-15 noon UTC (chosen as a modern date
        within B'ak'tun 12 to test full chart computation without edge cases)."""
        return swe.julday(1990, 1, 15, 12.0)

    def test_full_chart_computation(self, sample_jd):
        """compute_maya_chart returns a valid MayanChart"""
        from astro.maya.calculator import compute_maya_chart
        chart = compute_maya_chart(
            year=1990, month=1, day=15, hour=12, minute=0,
            timezone=0, latitude=0, longitude=0, location_name="Test",
        )
        assert chart.long_count.baktun == 12
        assert 1 <= chart.tzolkin.number <= 13
        assert 0 <= chart.tzolkin.sign_index <= 19
        assert 0 <= chart.haab.day_of_year <= 364
        assert len(chart.planets) == 6

    def test_backward_compat_properties(self, sample_jd):
        """MayanChart backward-compat properties work"""
        from astro.maya.calculator import compute_maya_chart
        chart = compute_maya_chart(
            year=1990, month=1, day=15, hour=12, minute=0,
            timezone=0, latitude=0, longitude=0,
        )
        # These properties must match their underlying data
        assert chart.baktun == chart.long_count.baktun
        assert chart.tzolkin_number == chart.tzolkin.number
        assert chart.tzolkin_day_name == chart.tzolkin.sign_name
        assert chart.haab_day == chart.haab.day_of_month
