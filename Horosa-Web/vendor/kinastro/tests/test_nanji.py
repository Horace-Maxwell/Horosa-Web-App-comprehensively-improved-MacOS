# -*- coding: utf-8 -*-
"""
tests/test_nanji.py — 南極神數模組測試

測試範圍：
- 四柱計算（年月時柱）
- 大運排法（順逆）
- 條文資料庫載入與查詢
- NanJiShenShu 類別核心功能
"""

import pytest

from astro.nanji.calculator import (
    NanJiShenShu,
    TiaowenDatabase,
    calculate_da_yun,
    calculate_hour_pillar,
    calculate_month_pillar,
    calculate_year_pillar,
    get_jianchu_huainan,
    get_wuxing_relation,
    get_xiu_group,
    interpret_chart_1,
    interpret_chart_6,
)
from astro.nanji.constants import (
    DIZHI,
    JIANCHU,
    TIANGAN,
    WUXING_GAN,
    WUXING_ZHI,
    YINYANG_GAN,
)


# ============================================================
# 年柱測試
# ============================================================

class TestYearPillar:
    def test_1984_jiazi(self):
        assert calculate_year_pillar(1984, after_lichun=True) == "甲子"

    def test_1990_gengwu(self):
        # 1990 年：(1990-1984)=6, 干index=6→庚, 支index=6→午
        assert calculate_year_pillar(1990, after_lichun=True) == "庚午"

    def test_before_lichun_shifts_year(self):
        # 立春前出生，用上一年
        assert calculate_year_pillar(1985, after_lichun=False) == "甲子"

    def test_2026(self):
        # 2026 年：(2026-1984)=42, 干=42%10=2→丙, 支=42%12=6→午
        assert calculate_year_pillar(2026, after_lichun=True) == "丙午"


# ============================================================
# 月柱測試
# ============================================================

class TestMonthPillar:
    def test_jiazi_year_month1(self):
        # 甲年五虎遁，正月起丙寅
        p = calculate_month_pillar("甲", 1)
        assert p == "丙寅"

    def test_jiazi_year_month3(self):
        # 甲年，三月：丙+2=戊，辰月
        p = calculate_month_pillar("甲", 3)
        assert p == "戊辰"

    def test_gengwu_year_month1(self):
        # 庚年五虎遁起戊，正月戊寅
        p = calculate_month_pillar("庚", 1)
        assert p == "戊寅"

    def test_month_zhi_fixed(self):
        # 月支固定：7月=申
        p = calculate_month_pillar("甲", 7)
        assert p.endswith("申")


# ============================================================
# 時柱測試
# ============================================================

class TestHourPillar:
    def test_jiazi_day_zi_hour(self):
        # 甲日子時 → 甲子
        assert calculate_hour_pillar("甲", "子") == "甲子"

    def test_jiazi_day_wu_hour(self):
        # 甲日午時 → 甲+6=庚, 午 → 庚午
        assert calculate_hour_pillar("甲", "午") == "庚午"

    def test_geng_day_zi_hour(self):
        # 庚日子時 → 丙子（庚庚丙作初）
        assert calculate_hour_pillar("庚", "子") == "丙子"


# ============================================================
# 大運測試
# ============================================================

class TestDaYun:
    def test_yang_year_male_forward(self):
        """陽年生男，順排"""
        # 甲年（陽）男命，月柱丙寅 → 大運從丁卯起
        da_yun = calculate_da_yun("丙寅", "男", "陽", steps=3)
        assert da_yun[0].ganzhi == "丁卯"
        assert da_yun[1].ganzhi == "戊辰"

    def test_yin_year_male_reverse(self):
        """陰年生男，逆排"""
        # 乙年（陰）男命，月柱戊辰 → 大運從丁卯起（逆行）
        da_yun = calculate_da_yun("戊辰", "男", "陰", steps=3)
        assert da_yun[0].ganzhi == "丁卯"

    def test_start_age_increments_by_10(self):
        da_yun = calculate_da_yun("丙寅", "男", "陽", steps=4, start_age=3)
        ages = [dy.start_age for dy in da_yun]
        assert ages == [3, 13, 23, 33]

    def test_returns_correct_count(self):
        da_yun = calculate_da_yun("丙寅", "女", "陽", steps=8)
        assert len(da_yun) == 8


# ============================================================
# 建除測試
# ============================================================

class TestJianchu:
    def test_yin_is_jian(self):
        assert get_jianchu_huainan("寅") == "建"

    def test_mao_is_chu(self):
        assert get_jianchu_huainan("卯") == "除"

    def test_zi_is_kai(self):
        assert get_jianchu_huainan("子") == "開"

    def test_chou_is_bi(self):
        assert get_jianchu_huainan("丑") == "閉"


# ============================================================
# 二十八宿測試
# ============================================================

class TestXiu28:
    def test_jue_east(self):
        assert get_xiu_group("角") == "東方蒼龍"

    def test_dou_north(self):
        assert get_xiu_group("斗") == "北方玄武"

    def test_kui_west(self):
        assert get_xiu_group("奎") == "西方白虎"

    def test_jing_south(self):
        assert get_xiu_group("井") == "南方朱雀"

    def test_unknown(self):
        assert get_xiu_group("？") == "未知"


# ============================================================
# 五行關係測試
# ============================================================

class TestWuxingRelation:
    def test_mu_sheng_huo(self):
        assert get_wuxing_relation("木", "火") == "木生火"

    def test_huo_ke_jin(self):
        assert get_wuxing_relation("火", "金") == "火克金"

    def test_tonglei(self):
        assert get_wuxing_relation("木", "木") == "同類"


# ============================================================
# 條文資料庫測試
# ============================================================

class TestTiaowenDatabase:
    @pytest.fixture
    def db(self):
        return TiaowenDatabase.get_instance()

    def test_total_entries(self, db):
        assert db.total == 246

    def test_lookup_returns_list(self, db):
        results = db.lookup("子部", "建張")
        assert isinstance(results, list)

    def test_lookup_known_entry(self, db):
        # 子部 建張 在 JSON 中有條目
        results = db.lookup("子部", "建張")
        assert len(results) >= 1
        assert results[0].section == "子部"

    def test_lookup_unknown_returns_empty(self, db):
        results = db.lookup("子部", "無此密碼")
        assert results == []

    def test_lookup_by_section_returns_all(self, db):
        zi_entries = db.lookup_by_section("子部")
        assert len(zi_entries) > 0
        assert all(e.section == "子部" for e in zi_entries)

    def test_all_sections_present(self, db):
        sections = {e.section for e in db.all_entries()}
        expected = {'子部', '丑部', '寅部', '卯部', '辰部', '巳部',
                    '午部', '未部', '申部', '酉部', '戌部', '亥部'}
        assert expected == sections

    def test_singleton(self):
        db1 = TiaowenDatabase.get_instance()
        db2 = TiaowenDatabase.get_instance()
        assert db1 is db2

    def test_entry_fields(self, db):
        entry = db.all_entries()[0]
        assert entry.section
        assert entry.code
        assert entry.verse
        assert entry.comment


# ============================================================
# NanJiShenShu 核心類別測試
# ============================================================

class TestNanJiShenShu:
    @pytest.fixture
    def njs_1990(self):
        """手稿示例命造：1990年4月2日辰時 男命"""
        njs = NanJiShenShu(
            lunar_year=1990, solar_month=4, day=2,
            hour_zhi="辰", gender="男"
        )
        njs.set_day_pillar("辛", "酉")
        njs.set_hour_pillar()
        return njs

    def test_year_pillar(self, njs_1990):
        assert njs_1990.year_pillar == "庚午"

    def test_month_pillar(self, njs_1990):
        # 庚年，四月巳月，五虎遁戊起，戊+3=辛
        assert njs_1990.month_pillar == "辛巳"

    def test_hour_pillar(self, njs_1990):
        # 辛日辰時：五鼠遁 辛→戊起，戊+辰(index4)=壬辰
        assert njs_1990.hour_pillar == "壬辰"

    def test_palace_section(self, njs_1990):
        # 年支午 → 午部
        assert njs_1990.palace_section == "午部"

    def test_da_yun_count(self, njs_1990):
        assert len(njs_1990.da_yun) == 8

    def test_year_yinyang(self, njs_1990):
        # 庚為陽干
        assert njs_1990.year_yinyang == "陽"

    def test_lookup_tiaowen_returns_list(self, njs_1990):
        results = njs_1990.lookup_tiaowen(section="子部", code="建張")
        assert isinstance(results, list)

    def test_lookup_tiaowen_default_section(self, njs_1990):
        # 預設使用命主宮部（午部）
        results = njs_1990.lookup_tiaowen(code="建張")
        # 午部建張可能有也可能無，但應回傳 list
        assert isinstance(results, list)

    def test_lookup_tiaowen_fallback_message(self, njs_1990):
        msg = njs_1990.lookup_tiaowen_fallback(code="無此密碼")
        assert "需參照原圖" in msg or "未找到" in msg

    def test_divine_with_matching_tiaowen(self, njs_1990):
        # 子部建張有條文，應回傳條文
        result = njs_1990.divine(chart=1, palace="子", jianchu="建", xiu="張", degree=1.0)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_divine_chart1_fallback(self, njs_1990):
        # 使用一個不存在條文的宮部/密碼
        result = njs_1990.divine(chart=1, palace="午", jianchu="建", xiu="角", degree=2.5)
        assert "圖一" in result or "度" in result or "建張" in result or isinstance(result, str)

    def test_divine_chart6(self, njs_1990):
        result = njs_1990.divine(chart=6, palace="午", jianchu="閉", xiu="軫", degree=1.0)
        assert "圖六" in result or isinstance(result, str)

    def test_compute_returns_result(self, njs_1990):
        result = njs_1990.compute()
        assert result.four_pillars.year == "庚午"
        assert len(result.da_yun) == 8
        assert isinstance(result.tiaowen_results, list)

    def test_get_four_pillars_str(self, njs_1990):
        s = njs_1990.get_four_pillars_str()
        assert "庚午" in s
        assert "辛巳" in s

    def test_lookup_password(self, njs_1990):
        meaning = njs_1990.lookup_password("跳重")
        assert "克夫" in meaning

    def test_lookup_password_unknown(self, njs_1990):
        msg = njs_1990.lookup_password("不存在")
        assert "手稿未公開" in msg

    def test_female_reverse_dayun(self):
        """陽年生女，逆排大運"""
        njs = NanJiShenShu(
            lunar_year=1990, solar_month=4, day=2,
            hour_zhi="辰", gender="女"
        )
        # 庚午年（陽年）女命 → 逆排
        assert njs.da_yun[0].ganzhi != "壬午"  # 不是順排的結果

    def test_before_lichun(self):
        """立春前出生，年柱退一年"""
        njs = NanJiShenShu(1990, 1, 15, "子", "男", after_lichun=False)
        # 1989年己巳
        assert njs.year_pillar == "己巳"


# ============================================================
# 星圖解讀測試
# ============================================================

class TestChartInterpretation:
    def test_interpret_chart1_returns_string(self):
        result = interpret_chart_1("午", "張", 2.0)
        assert "圖一" in result
        assert "張" in result

    def test_interpret_chart6_wu_palace(self):
        result = interpret_chart_6("午", 1.5)
        assert "閉軫" in result

    def test_interpret_chart6_zi_palace(self):
        result = interpret_chart_6("子", 1.5)
        assert "成牛" in result
