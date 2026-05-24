"""
七政四餘計算模組測試 (Tests for Seven Governors and Four Remainders Calculator)
"""

import pytest
from astro.qizheng.calculator import (
    compute_chart,
    format_degree,
    get_mansion_for_degree,
    get_mansion_index_for_degree,
    _normalize_degree,
    _degree_to_sign_index,
    _degree_to_sign_degree,
    _get_western_sign,
    _get_chinese_sign,
    _get_hour_branch,
    _get_solar_month,
    _get_ming_gong_branch,
    _branch_to_cusp,
    _get_sign_element,
    _get_mansion_info,
    _get_mansion_info_for_system,
    _check_qidu,
    _get_mansion_width,
)
from astro.qizheng.constants import (
    TWENTY_EIGHT_MANSIONS,
    TWENTY_EIGHT_MANSIONS_LIMING,
    TWENTY_EIGHT_MANSIONS_ANCIENT,
    ZODIAC_SIGN_ELEMENTS,
    FOUR_REMAINDERS,
)


class TestNormalizeDegree:
    """測試角度標準化"""

    def test_normal_range(self):
        assert _normalize_degree(180.0) == 180.0

    def test_zero(self):
        assert _normalize_degree(0.0) == 0.0

    def test_negative(self):
        assert _normalize_degree(-90.0) == 270.0

    def test_over_360(self):
        assert _normalize_degree(450.0) == 90.0

    def test_exactly_360(self):
        assert _normalize_degree(360.0) == 0.0


class TestDegreeConversions:
    """測試度數轉換"""

    def test_sign_index_aries(self):
        assert _degree_to_sign_index(15.0) == 0  # 白羊

    def test_sign_index_capricorn(self):
        assert _degree_to_sign_index(280.0) == 9  # 摩羯

    def test_sign_index_pisces(self):
        assert _degree_to_sign_index(350.0) == 11  # 雙魚

    def test_sign_degree(self):
        assert abs(_degree_to_sign_degree(280.5) - 10.5) < 0.001

    def test_western_sign(self):
        assert _get_western_sign(280.0) == "摩羯"
        assert _get_western_sign(0.0) == "白羊"
        assert _get_western_sign(120.0) == "獅子"

    def test_chinese_sign(self):
        assert _get_chinese_sign(280.0) == "丑宮(星紀)"
        assert _get_chinese_sign(0.0) == "戌宮(降婁)"


class TestFormatDegree:
    """測試度數格式化"""

    def test_basic_format(self):
        result = format_degree(280.5)
        assert "280°" in result
        assert "30'" in result

    def test_zero(self):
        result = format_degree(0.0)
        assert "0°" in result


class TestGetMansion:
    """測試二十八宿對應"""

    def test_returns_dict(self):
        mansion = get_mansion_for_degree(0.0)
        assert "name" in mansion
        assert "element" in mansion
        assert "group" in mansion

    def test_different_degrees(self):
        m1 = get_mansion_for_degree(0.0)
        m2 = get_mansion_for_degree(180.0)
        assert m1["name"] != m2["name"]


class TestComputeChart:
    """測試排盤計算"""

    @pytest.fixture
    def sample_chart(self):
        """建立測試用排盤 (1990-01-01 12:00 北京)"""
        return compute_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_chart_metadata(self, sample_chart):
        assert sample_chart.year == 1990
        assert sample_chart.month == 1
        assert sample_chart.day == 1
        assert sample_chart.location_name == "北京"

    def test_has_eleven_planets(self, sample_chart):
        """應有 11 顆星曜 (七政 + 四餘)"""
        assert len(sample_chart.planets) == 11

    def test_seven_governors_names(self, sample_chart):
        names = [p.name for p in sample_chart.planets[:7]]
        assert "太陽" in names
        assert "太陰" in names
        assert "水星" in names
        assert "金星" in names
        assert "火星" in names
        assert "木星" in names
        assert "土星" in names

    def test_four_remainders_names(self, sample_chart):
        names = [p.name for p in sample_chart.planets[7:]]
        assert "羅睺" in names
        assert "計都" in names
        assert "月孛" in names
        assert "紫氣" in names

    def test_twelve_houses(self, sample_chart):
        assert len(sample_chart.houses) == 12

    def test_house_names(self, sample_chart):
        names = [h.name for h in sample_chart.houses]
        assert "命宮" in names
        assert "夫妻宮" in names
        assert "官祿宮" in names

    def test_planet_longitudes_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.longitude < 360

    def test_planet_sign_degrees_in_range(self, sample_chart):
        for p in sample_chart.planets:
            assert 0 <= p.sign_degree < 30

    def test_ketu_opposite_rahu(self, sample_chart):
        """計都應在羅睺對面 (相差 180°)"""
        rahu = next(p for p in sample_chart.planets if p.name == "羅睺")
        ketu = next(p for p in sample_chart.planets if p.name == "計都")
        diff = abs(rahu.longitude - ketu.longitude)
        assert abs(diff - 180.0) < 0.01

    def test_ziqi_independent_of_yuebei(self, sample_chart):
        """紫氣使用真實遠地點（oscillating apogee），與月孛（平均遠地點）不同，不要求相差 180°"""
        yuebei = next(p for p in sample_chart.planets if p.name == "月孛")
        ziqi = next(p for p in sample_chart.planets if p.name == "紫氣")
        # Both should be valid longitudes
        assert 0 <= yuebei.longitude < 360
        assert 0 <= ziqi.longitude < 360
        # They are computed independently (mean vs osculating apogee), so are NOT 180° apart
        diff = abs(yuebei.longitude - ziqi.longitude) % 360
        if diff > 180:
            diff = 360 - diff
        assert diff != 180.0, "紫氣 and 月孛 should NOT be exactly 180° apart (different formulas)"

    def test_ascendant_in_range(self, sample_chart):
        assert 0 <= sample_chart.ascendant < 360

    def test_midheaven_in_range(self, sample_chart):
        assert 0 <= sample_chart.midheaven < 360

    def test_sun_in_capricorn_for_jan1(self, sample_chart):
        """1月1日太陽應在摩羯座"""
        sun = sample_chart.planets[0]
        assert sun.sign_western == "摩羯"

    def test_all_planets_assigned_to_houses(self, sample_chart):
        """所有星曜都應被分配到宮位"""
        for p in sample_chart.planets:
            assert 0 <= p.palace_index < 12

    def test_different_dates_produce_different_results(self):
        """不同日期應產生不同結果"""
        chart1 = compute_chart(
            year=2000, month=6, day=15, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
        )
        chart2 = compute_chart(
            year=2020, month=12, day=25, hour=8, minute=30,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
        )
        sun1 = chart1.planets[0].longitude
        sun2 = chart2.planets[0].longitude
        assert abs(sun1 - sun2) > 1.0


class TestGetHourBranch:
    """測試時辰地支計算"""

    def test_zi_hour_midnight(self):
        assert _get_hour_branch(0, 0) == 0   # 子時

    def test_zi_hour_2300(self):
        assert _get_hour_branch(23, 0) == 0  # 子時

    def test_chou_hour(self):
        assert _get_hour_branch(1, 0) == 1   # 丑時

    def test_yin_hour(self):
        assert _get_hour_branch(3, 0) == 2   # 寅時

    def test_wu_hour_noon(self):
        assert _get_hour_branch(12, 0) == 6  # 午時

    def test_hai_hour(self):
        assert _get_hour_branch(21, 0) == 11  # 亥時


class TestGetSolarMonth:
    """測試節氣月計算"""

    def test_month1_lichun(self):
        # 立春 ~ 315° ecliptic
        assert _get_solar_month(315.0) == 1

    def test_month1_upper(self):
        assert _get_solar_month(344.9) == 1

    def test_month2_jingzhe(self):
        # 驚蟄 ~ 345°
        assert _get_solar_month(345.0) == 2

    def test_month2_crosses_zero(self):
        # 0° ecliptic is within month 2
        assert _get_solar_month(0.0) == 2

    def test_month7_liqiu(self):
        # 立秋 ~ 135°
        assert _get_solar_month(135.0) == 7

    def test_month12_xiaohan(self):
        # 小寒 ~ 285°
        assert _get_solar_month(285.0) == 12


class TestGetMingGongBranch:
    """測試命宮地支計算"""

    def test_month1_zi_hour(self):
        # 正月子時: (1+1-0)%12 = 2 (寅)
        assert _get_ming_gong_branch(1, 0) == 2

    def test_month7_zi_hour(self):
        # 七月子時: (1+7-0)%12 = 8 (申) — user's example
        assert _get_ming_gong_branch(7, 0) == 8

    def test_month1_wu_hour(self):
        # 正月午時: (1+1-6)%12 = (-4)%12 = 8 (申) — Python mod always non-negative
        assert _get_ming_gong_branch(1, 6) == 8

    def test_month12_hai_hour(self):
        # 十二月亥時: (1+12-11)%12 = 2 (寅)
        assert _get_ming_gong_branch(12, 11) == 2


class TestBranchToCusp:
    """測試地支到宮頭度數轉換"""

    def test_xu_branch(self):
        # 戌(10) → 0°
        assert _branch_to_cusp(10) == 0.0

    def test_you_branch(self):
        # 酉(9) → 30°
        assert _branch_to_cusp(9) == 30.0

    def test_shen_branch(self):
        # 申(8) → 60°
        assert _branch_to_cusp(8) == 60.0

    def test_yin_branch(self):
        # 寅(2) → 240°
        assert _branch_to_cusp(2) == 240.0

    def test_zi_branch(self):
        # 子(0) → 300°
        assert _branch_to_cusp(0) == 300.0


class TestComputeChartMingGong:
    """測試排盤命宮計算與性別方向"""

    def test_1985_aug26_zi_hour_ming_gong_shen(self):
        """1985-8-26 子時 命宮應在申"""
        chart = compute_chart(
            1985, 8, 26, 0, 0, 8.0, 22.3193, 114.1694, "香港",
        )
        assert chart.ming_gong_branch == 8  # 申

    def test_male_clockwise_direction(self):
        """男命宮位按順時針(地支遞減)排列"""
        chart = compute_chart(
            1985, 8, 26, 0, 0, 8.0, 22.3193, 114.1694, "香港",
            gender="male",
        )
        for i, h in enumerate(chart.houses):
            assert h.branch == (chart.ming_gong_branch - i) % 12

    def test_female_counterclockwise_direction(self):
        """女命宮位按逆時針(地支遞增)排列"""
        chart = compute_chart(
            1985, 8, 26, 0, 0, 8.0, 22.3193, 114.1694, "香港",
            gender="female",
        )
        for i, h in enumerate(chart.houses):
            assert h.branch == (chart.ming_gong_branch + i) % 12

    def test_houses_have_branch_info(self):
        """每個宮位應有地支資訊"""
        chart = compute_chart(
            1990, 1, 1, 12, 0, 8.0, 39.9042, 116.4074, "北京",
        )
        for h in chart.houses:
            assert 0 <= h.branch <= 11
            assert h.branch_name in [
                "子", "丑", "寅", "卯", "辰", "巳",
                "午", "未", "申", "酉", "戌", "亥",
            ]

    def test_all_branches_covered(self):
        """十二個宮位應覆蓋所有十二地支"""
        chart = compute_chart(
            1990, 1, 1, 12, 0, 8.0, 39.9042, 116.4074, "北京",
        )
        branches = {h.branch for h in chart.houses}
        assert branches == set(range(12))

    def test_default_gender_is_male(self):
        """預設性別應為男"""
        chart = compute_chart(
            1990, 1, 1, 12, 0, 8.0, 39.9042, 116.4074, "北京",
        )
        assert chart.gender == "male"

    def test_chart_has_solar_month(self):
        """排盤結果應包含節氣月"""
        chart = compute_chart(
            1990, 1, 1, 12, 0, 8.0, 39.9042, 116.4074, "北京",
        )
        assert 1 <= chart.solar_month <= 12

    def test_chart_has_hour_branch(self):
        """排盤結果應包含時辰"""
        chart = compute_chart(
            1990, 1, 1, 12, 0, 8.0, 39.9042, 116.4074, "北京",
        )
        assert 0 <= chart.hour_branch <= 11

    def test_different_hours_different_ming_gong(self):
        """不同時辰應產生不同命宮"""
        chart_zi = compute_chart(
            1990, 6, 15, 0, 0, 8.0, 39.9042, 116.4074, "北京",
        )
        chart_wu = compute_chart(
            1990, 6, 15, 12, 0, 8.0, 39.9042, 116.4074, "北京",
        )
        assert chart_zi.ming_gong_branch != chart_wu.ming_gong_branch


# ============================================================
# 新增測試：MOIRA 參考精確度改進
# ============================================================

class TestMOIRAMansionBoundaries:
    """測試二十八宿邊界（參考 MOIRA 精確值）"""

    def test_28_mansions_count(self):
        """應有 28 個宿位"""
        assert len(TWENTY_EIGHT_MANSIONS) == 28

    def test_mansions_ascending_except_wrap(self):
        """除了跨越 0° 的宿位外，start_lon 應大致遞增"""
        wraps = 0
        for i in range(27):
            if TWENTY_EIGHT_MANSIONS[i + 1]["start_lon"] < TWENTY_EIGHT_MANSIONS[i]["start_lon"]:
                wraps += 1
        # Only one decreasing transition where the sequence crosses 0° (室→壁)
        assert wraps == 1

    def test_jiao_mansion_moira_boundary(self):
        """角宿起始度數應匹配 MOIRA 值 (≈203.84°)"""
        jiao = TWENTY_EIGHT_MANSIONS[0]
        assert jiao["name"] == "角"
        assert abs(jiao["start_lon"] - 203.8375) < 0.01

    def test_dou_mansion_moira_boundary(self):
        """斗宿起始度數應匹配 MOIRA 值 (≈280.18°)"""
        dou = TWENTY_EIGHT_MANSIONS[7]
        assert dou["name"] == "斗"
        assert abs(dou["start_lon"] - 280.1775) < 0.01

    def test_kui_mansion_moira_boundary(self):
        """奎宿起始度數應匹配 MOIRA 值 (≈22.37°)"""
        kui = next(m for m in TWENTY_EIGHT_MANSIONS if m["name"] == "奎")
        assert abs(kui["start_lon"] - 22.3721) < 0.01

    def test_jing_mansion_moira_boundary(self):
        """井宿起始度數應匹配 MOIRA 值 (≈95.30°)"""
        jing = next(m for m in TWENTY_EIGHT_MANSIONS if m["name"] == "井")
        assert abs(jing["start_lon"] - 95.2980) < 0.01

    def test_zhen_precedes_jiao(self):
        """軫宿 start_lon 應小於角宿 start_lon"""
        zhen = TWENTY_EIGHT_MANSIONS[27]
        jiao = TWENTY_EIGHT_MANSIONS[0]
        assert zhen["name"] == "軫"
        assert abs(zhen["start_lon"] - 190.7218) < 0.01
        assert zhen["start_lon"] < jiao["start_lon"]

    def test_mansion_lookup_at_0_degrees(self):
        """0° 應落在室宿（室 starts at 353.49°, 壁 starts at 9.15°, so 0° is in 室）"""
        mansion = get_mansion_for_degree(0.0)
        assert mansion["name"] == "室"

    def test_mansion_lookup_at_10_degrees(self):
        """10° 應落在壁宿 (壁 starts at 9.15°)"""
        mansion = get_mansion_for_degree(10.0)
        assert mansion["name"] == "壁"

    def test_shi_mansion_boundary(self):
        """室宿起始度數應在 α Pegasi 附近 (≈353.49°)"""
        shi = next(m for m in TWENTY_EIGHT_MANSIONS if m["name"] == "室")
        assert abs(shi["start_lon"] - 353.49) < 0.1

    def test_all_mansions_have_valid_elements(self):
        """所有宿位應有有效的七曜屬性"""
        valid_elements = {"木", "金", "土", "日", "月", "火", "水"}
        for m in TWENTY_EIGHT_MANSIONS:
            assert m["element"] in valid_elements, f"{m['name']}宿元素 '{m['element']}' 無效"


class TestMeanNodeUsage:
    """測試使用平均交點 (MEAN_NODE) 而非真交點，符合傳統七政四餘做法"""

    def test_four_remainders_ketu_uses_mean_node(self):
        """計都應使用 MEAN_NODE（升交點/北交點，傳統七政四餘使用平均交點）"""
        import swisseph as swe
        assert FOUR_REMAINDERS["計都"] == swe.MEAN_NODE

    def test_rahu_mean_node_vs_true_node_differ(self):
        """平均交點與真交點應有差異"""
        import swisseph as swe
        swe.set_ephe_path("")
        jd = swe.julday(1990, 1, 1, 4.0)
        true_result, _ = swe.calc_ut(jd, swe.TRUE_NODE)
        mean_result, _ = swe.calc_ut(jd, swe.MEAN_NODE)
        # They should differ (typically by up to ~1.5°)
        diff = abs(true_result[0] - mean_result[0])
        assert diff > 0.01, "TRUE_NODE and MEAN_NODE should differ"
        assert diff < 5.0, "Difference should be reasonable (< 5°)"


class TestFourRemaindersCorrectness:
    """回歸測試：驗證四餘計算符合傳統七政四餘定義
    參考盤: 1985年8月26日2:55 香港 (UTC+8)
    計都(升交點)=酉宮, 羅睺(降交點)=卯宮, 月孛=酉宮, 紫氣=戌宮, 木星=子宮
    """

    @pytest.fixture
    def hk_1985_chart(self):
        return compute_chart(
            year=1985, month=8, day=26, hour=2, minute=55,
            timezone=8.0, latitude=22.2728, longitude=114.1722,
            location_name="香港",
        )

    def test_rahu_in_mao_gong(self, hk_1985_chart):
        """羅睺（降交點/南交點）應在卯宮"""
        rahu = next(p for p in hk_1985_chart.planets if p.name == "羅睺")
        assert "卯宮" in rahu.sign_chinese, f"羅睺應在卯宮，實得 {rahu.sign_chinese}"

    def test_ketu_in_you_gong(self, hk_1985_chart):
        """計都（升交點/北交點）應在酉宮"""
        ketu = next(p for p in hk_1985_chart.planets if p.name == "計都")
        assert "酉宮" in ketu.sign_chinese, f"計都應在酉宮，實得 {ketu.sign_chinese}"

    def test_yuebei_in_you_gong(self, hk_1985_chart):
        """月孛（平均遠地點）應在酉宮"""
        yuebei = next(p for p in hk_1985_chart.planets if p.name == "月孛")
        assert "酉宮" in yuebei.sign_chinese, f"月孛應在酉宮，實得 {yuebei.sign_chinese}"

    def test_ziqi_in_xu_gong(self, hk_1985_chart):
        """紫氣（真實遠地點）應在戌宮"""
        ziqi = next(p for p in hk_1985_chart.planets if p.name == "紫氣")
        assert "戌宮" in ziqi.sign_chinese, f"紫氣應在戌宮，實得 {ziqi.sign_chinese}"

    def test_jupiter_in_zi_gong(self, hk_1985_chart):
        """木星應在子宮"""
        jupiter = next(p for p in hk_1985_chart.planets if p.name == "木星")
        assert "子宮" in jupiter.sign_chinese, f"木星應在子宮，實得 {jupiter.sign_chinese}"


class TestMingGongClassicalFormula:
    """測試命宮使用天文上升點（MOIRA 方式）"""

    def test_ming_gong_uses_ascendant(self):
        """命宮應依天文上升點所在星座確定（MOIRA 方式）"""
        chart = compute_chart(
            1990, 1, 1, 12, 0, 8.0, 39.9042, 116.4074, "北京",
        )
        # 上升點所在星座索引決定命宮地支: (10 - sign_index) % 12
        expected = (10 - _degree_to_sign_index(chart.ascendant)) % 12
        assert chart.ming_gong_branch == expected

    def test_ming_gong_1900_hk_is_wu(self):
        """1900-04-19 13:30 香港，上升點在 137.6°(Leo/午), 命宮應為午(6)"""
        chart = compute_chart(
            1900, 4, 19, 13, 30, 8.0, 22.3193, 114.1694, "香港",
        )
        # Ascendant ≈ 137.6° → Leo (sign index 4) → branch (10-4)%12 = 6 (午)
        assert chart.ming_gong_branch == 6  # 午

    def test_ming_gong_month1_zi(self):
        """正月子時命宮應在寅 (索引2)"""
        # Solar month 1 (around Feb 4): Sun ≈ 315°
        # 子時 = hour_branch 0
        # (1 + 1 - 0) % 12 = 2 (寅)
        assert _get_ming_gong_branch(1, 0) == 2

    def test_ming_gong_varies_by_hour(self):
        """不同時辰同月應產生不同命宮"""
        # Same month, different hours
        mg1 = _get_ming_gong_branch(6, 0)   # 午月子時
        mg2 = _get_ming_gong_branch(6, 6)   # 午月午時
        assert mg1 != mg2


class TestZodiacSignElements:
    """測試十二宮五行屬性（參考 MOIRA）"""

    def test_zodiac_elements_count(self):
        """應有 12 個星座五行"""
        assert len(ZODIAC_SIGN_ELEMENTS) == 12

    def test_aries_fire(self):
        assert ZODIAC_SIGN_ELEMENTS[0] == "火"   # 白羊=火

    def test_taurus_metal(self):
        assert ZODIAC_SIGN_ELEMENTS[1] == "金"   # 金牛=金

    def test_gemini_water(self):
        assert ZODIAC_SIGN_ELEMENTS[2] == "水"   # 雙子=水

    def test_cancer_moon(self):
        assert ZODIAC_SIGN_ELEMENTS[3] == "月"   # 巨蟹=月

    def test_leo_sun(self):
        assert ZODIAC_SIGN_ELEMENTS[4] == "日"   # 獅子=日

    def test_get_sign_element_aries(self):
        """白羊座 (0°–30°) 五行屬火"""
        assert _get_sign_element(15.0) == "火"

    def test_get_sign_element_capricorn(self):
        """摩羯座 (270°–300°) 五行屬土"""
        assert _get_sign_element(280.0) == "土"


class TestMansionInfo:
    """測試宿內度數計算"""

    def test_mansion_name_for_known_degree(self):
        """已知度數應返回正確宿名"""
        name, deg, _, _ = _get_mansion_info(210.0)
        assert name == "角"

    def test_mansion_degree_in_range(self):
        """宿內度數應為正值"""
        name, deg, _, _ = _get_mansion_info(215.0)
        assert name == "亢"
        assert deg >= 0

    def test_mansion_degree_precision(self):
        """角宿起始點度數應為 0"""
        name, deg, _, _ = _get_mansion_info(203.8375)
        assert name == "角"
        assert abs(deg) < 0.01

    def test_mansion_width(self):
        """宿寬度應在合理範圍 (0.5°-36°)"""
        for i in range(28):
            w = _get_mansion_width(i)
            assert 0.5 < w < 36.0, f"宿 {TWENTY_EIGHT_MANSIONS[i]['name']} 寬度 {w}° 超出範圍"


class TestQidu:
    """測試岐度檢查（宮/宿交界 ±1.5°）"""

    def test_qidu_at_sign_boundary_start(self):
        """星座起始邊界 1° 應為岐度"""
        assert _check_qidu(1.0, 10.0, 20.0) is True

    def test_qidu_at_sign_boundary_end(self):
        """星座結束邊界 29° 應為岐度"""
        assert _check_qidu(29.0, 10.0, 20.0) is True

    def test_no_qidu_at_middle(self):
        """星座中間 15° 不應為岐度"""
        assert _check_qidu(15.0, 10.0, 20.0) is False

    def test_qidu_at_mansion_boundary_start(self):
        """宿起始邊界 1° 應為岐度"""
        assert _check_qidu(15.0, 1.0, 20.0) is True

    def test_qidu_at_mansion_boundary_end(self):
        """宿結束邊界附近應為岐度"""
        assert _check_qidu(15.0, 19.0, 20.0) is True

    def test_no_qidu_mansion_middle(self):
        """宿中間 10° 不應為岐度"""
        assert _check_qidu(15.0, 10.0, 20.0) is False


class TestPlanetNewFields:
    """測試星曜新增欄位"""

    @pytest.fixture
    def sample_chart(self):
        return compute_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=39.9042, longitude=116.4074,
            location_name="北京",
        )

    def test_planets_have_mansion_name(self, sample_chart):
        """所有星曜應有二十八宿名稱"""
        valid_names = {m["name"] for m in TWENTY_EIGHT_MANSIONS}
        for p in sample_chart.planets:
            assert p.mansion_name in valid_names, f"{p.name} 的宿名 '{p.mansion_name}' 無效"

    def test_planets_have_mansion_degree(self, sample_chart):
        """所有星曜應有宿內度數（非負）"""
        for p in sample_chart.planets:
            assert p.mansion_degree >= 0, f"{p.name} 的宿內度數為負"

    def test_planets_have_sign_element(self, sample_chart):
        """所有星曜應有所在星座五行"""
        valid_elements = {"日", "月", "火", "水", "木", "金", "土"}
        for p in sample_chart.planets:
            assert p.sign_element in valid_elements, f"{p.name} 的宮五行 '{p.sign_element}' 無效"

    def test_planets_have_is_qidu(self, sample_chart):
        """所有星曜應有岐度布林值"""
        for p in sample_chart.planets:
            assert isinstance(p.is_qidu, bool)


class TestLimingMansionCalculation:
    """迴歸測試：立命二十八宿宿度計算

    參考案例：1985-08-26 02:55 Tai Po (HK), UTC+8, 男命
    今制立命應為「參水八度立命」，古制立命應為「井木十一度立命」。
    """

    # Reference liming_lon calibrated for this birth data
    # (tropical ascendant ≈ 109.83° with Tang-epoch ayanamsa ≈ 28.985°)
    REFERENCE_LIMING_LON = 80.843

    def test_liming_modern_mansion(self):
        """今制立命：應落在參宿"""
        name, deg, idx, _ = _get_mansion_info_for_system(
            self.REFERENCE_LIMING_LON, TWENTY_EIGHT_MANSIONS_LIMING
        )
        assert name == "參", f"今制立命宿名應為「參」，實得「{name}」"

    def test_liming_modern_degree(self):
        """今制立命：應為八度（參水八度立命）"""
        _, deg, _, _ = _get_mansion_info_for_system(
            self.REFERENCE_LIMING_LON, TWENTY_EIGHT_MANSIONS_LIMING
        )
        assert round(deg) == 8, f"今制立命度數應為8，實得{round(deg)}"

    def test_liming_modern_element(self):
        """今制立命：參宿屬水"""
        _, _, idx, _ = _get_mansion_info_for_system(
            self.REFERENCE_LIMING_LON, TWENTY_EIGHT_MANSIONS_LIMING
        )
        assert TWENTY_EIGHT_MANSIONS_LIMING[idx]["element"] == "水"

    def test_liming_ancient_mansion(self):
        """古制立命：應落在井宿"""
        name, deg, idx, _ = _get_mansion_info_for_system(
            self.REFERENCE_LIMING_LON, TWENTY_EIGHT_MANSIONS_ANCIENT
        )
        assert name == "井", f"古制立命宿名應為「井」，實得「{name}」"

    def test_liming_ancient_degree(self):
        """古制立命：應為十一度（井木十一度立命）"""
        _, deg, _, _ = _get_mansion_info_for_system(
            self.REFERENCE_LIMING_LON, TWENTY_EIGHT_MANSIONS_ANCIENT
        )
        assert round(deg) == 11, f"古制立命度數應為11，實得{round(deg)}"

    def test_liming_ancient_element(self):
        """古制立命：井宿屬木"""
        _, _, idx, _ = _get_mansion_info_for_system(
            self.REFERENCE_LIMING_LON, TWENTY_EIGHT_MANSIONS_ANCIENT
        )
        assert TWENTY_EIGHT_MANSIONS_ANCIENT[idx]["element"] == "木"

    def test_compute_liming_lon_for_reference_case(self):
        """_compute_liming_lon 對參考案例應回傳約 80.8°（以 compute_chart 驗證）"""
        chart = compute_chart(
            year=1985, month=8, day=26, hour=2, minute=55,
            timezone=8.0, latitude=22.4501, longitude=114.1688,
            location_name="Tai Po (HK)",
        )
        # Should be close to 80.8° (±0.6° tolerance for coordinate variation)
        assert 80.0 < chart.liming_lon < 81.5, (
            f"liming_lon 應約為 80.8°，實得 {chart.liming_lon:.3f}°"
        )

    def test_full_chart_liming_labels(self):
        """透過 compute_chart 驗證今制=參水八度立命，古制=井木十一度立命"""
        from astro.qizheng.chart_renderer import _format_liming_mansion
        chart = compute_chart(
            year=1985, month=8, day=26, hour=2, minute=55,
            timezone=8.0, latitude=22.4501, longitude=114.1688,
            location_name="Tai Po (HK)",
        )
        modern = _format_liming_mansion(chart.liming_lon, TWENTY_EIGHT_MANSIONS_LIMING)
        ancient = _format_liming_mansion(chart.liming_lon, TWENTY_EIGHT_MANSIONS_ANCIENT)
        assert modern == "參水八度立命", f"今制立命標籤應為「參水八度立命」，實得「{modern}」"
        assert ancient == "井木十一度立命", f"古制立命標籤應為「井木十一度立命」，實得「{ancient}」"
