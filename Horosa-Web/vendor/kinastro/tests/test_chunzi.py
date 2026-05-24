# -*- coding: utf-8 -*-
"""
tests/test_chunzi.py — 蠢子數模組單元測試

測試範圍：
  - ChunZiShu 基礎查詢（get_verse、batch_lookup、interpret）
  - search：關鍵字搜尋
  - get_verses_by_mansion：依 28 宿查詢
  - search_by_tags：多關鍵字 AND 搜尋
  - get_verses_by_hour：依時辰查詢
  - explain：詩詞結構化解析
"""

import pytest

from astro.chunzi import ChunZiShu


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture(scope="module")
def czs() -> ChunZiShu:
    """模組級 ChunZiShu 實例（共用，避免重複載入 CSV）。"""
    return ChunZiShu()


# ============================================================
# 初始化測試
# ============================================================


class TestInit:
    def test_loads_data(self, czs: ChunZiShu) -> None:
        """應成功載入超過 4000 筆資料。"""
        assert len(czs.df) >= 4000

    def test_code_index_built(self, czs: ChunZiShu) -> None:
        """code_index 應為非空字典。"""
        assert isinstance(czs.code_index, dict)
        assert len(czs.code_index) > 0

    def test_invalid_path_raises(self) -> None:
        """傳入不存在的路徑應拋出 FileNotFoundError。"""
        with pytest.raises(FileNotFoundError):
            ChunZiShu("/nonexistent/path/data.csv")


# ============================================================
# get_verse 測試
# ============================================================


class TestGetVerse:
    def test_known_code_returns_dict(self, czs: ChunZiShu) -> None:
        """已知代碼應回傳包含必要欄位的字典。"""
        result = czs.get_verse("畢龍6巳")
        assert result is not None
        assert result["code"] == "畢龍6巳"
        assert "verse" in result
        assert isinstance(result["verse"], str)
        assert len(result["verse"]) > 0

    def test_known_code_has_all_fields(self, czs: ChunZiShu) -> None:
        """回傳字典應包含全部標準欄位。"""
        result = czs.get_verse("畢龍6巳")
        assert result is not None
        for field in ("code", "category", "star", "degree", "branch", "verse"):
            assert field in result

    def test_unknown_code_returns_none(self, czs: ChunZiShu) -> None:
        """未知代碼應回傳 None。"""
        result = czs.get_verse("不存在的代碼XYZ")
        assert result is None

    def test_strips_whitespace(self, czs: ChunZiShu) -> None:
        """代碼兩端空白應被自動去除。"""
        result = czs.get_verse("  畢龍6巳  ")
        assert result is not None


# ============================================================
# search 測試
# ============================================================


class TestSearch:
    def test_keyword_returns_list(self, czs: ChunZiShu) -> None:
        """search 應回傳列表。"""
        results = czs.search("父")
        assert isinstance(results, list)

    def test_keyword_matches_verse(self, czs: ChunZiShu) -> None:
        """所有回傳結果的 verse 欄位應包含搜尋關鍵字。"""
        results = czs.search("先去父", limit=50)
        assert len(results) > 0
        for r in results:
            assert "先去父" in r["verse"]

    def test_limit_respected(self, czs: ChunZiShu) -> None:
        """回傳筆數不應超過 limit。"""
        results = czs.search("父", limit=5)
        assert len(results) <= 5

    def test_not_found_returns_empty(self, czs: ChunZiShu) -> None:
        """找不到時應回傳空列表。"""
        results = czs.search("XXXXXXXXXXXXXXX_NOT_FOUND")
        assert results == []


# ============================================================
# get_verses_by_mansion 測試
# ============================================================


class TestGetVersesByMansion:
    def test_known_mansion_returns_list(self, czs: ChunZiShu) -> None:
        """已知宿名應回傳非空列表。"""
        results = czs.get_verses_by_mansion("室")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_results_belong_to_mansion(self, czs: ChunZiShu) -> None:
        """回傳結果的 category 或 mansion28 應為查詢的宿名。"""
        results = czs.get_verses_by_mansion("角")
        for r in results:
            assert r.get("category") == "角" or r.get("mansion28") == "角"

    def test_unknown_mansion_returns_empty(self, czs: ChunZiShu) -> None:
        """未知宿名應回傳空列表。"""
        results = czs.get_verses_by_mansion("不存在的宿")
        assert results == []

    def test_strips_whitespace(self, czs: ChunZiShu) -> None:
        """宿名兩端空白應被自動去除。"""
        results = czs.get_verses_by_mansion("  室  ")
        assert len(results) > 0


# ============================================================
# search_by_tags 測試
# ============================================================


class TestSearchByTags:
    def test_single_tag(self, czs: ChunZiShu) -> None:
        """單標籤搜尋應與 search 結果一致（限制相同 limit）。"""
        tags_result = czs.search_by_tags(["先去父"], limit=50)
        single_result = czs.search("先去父", limit=50)
        assert len(tags_result) == len(single_result)

    def test_and_logic(self, czs: ChunZiShu) -> None:
        """所有回傳結果應同時包含所有標籤。"""
        tags = ["先去父", "父"]
        results = czs.search_by_tags(tags, limit=100)
        for r in results:
            for tag in tags:
                assert tag in r["verse"]

    def test_empty_tags_returns_empty(self, czs: ChunZiShu) -> None:
        """空標籤列表應回傳空列表。"""
        assert czs.search_by_tags([]) == []

    def test_no_match_returns_empty(self, czs: ChunZiShu) -> None:
        """不可能同時出現的標籤組合應回傳空列表。"""
        results = czs.search_by_tags(["先去父", "XXXXXXXXXXXXXXXXX_NOPE"])
        assert results == []


# ============================================================
# get_verses_by_hour 測試
# ============================================================


class TestGetVersesByHour:
    def test_returns_list(self, czs: ChunZiShu) -> None:
        """應回傳列表。"""
        results = czs.get_verses_by_hour("未")
        assert isinstance(results, list)

    def test_verse_contains_pattern(self, czs: ChunZiShu) -> None:
        """所有回傳結果的詩詞應包含「X時生人」。"""
        results = czs.get_verses_by_hour("未")
        assert len(results) > 0
        for r in results:
            assert "未時生人" in r["verse"]

    def test_unknown_hour_returns_empty(self, czs: ChunZiShu) -> None:
        """無效時辰應回傳空列表。"""
        results = czs.get_verses_by_hour("永")
        assert results == []


# ============================================================
# batch_lookup 測試
# ============================================================


class TestBatchLookup:
    def test_returns_list_of_same_length(self, czs: ChunZiShu) -> None:
        """批量查詢結果長度應與輸入代碼數相同。"""
        codes = ["畢龍6巳", "不存在999"]
        results = czs.batch_lookup(codes)
        assert len(results) == 2

    def test_missing_code_has_warning(self, czs: ChunZiShu) -> None:
        """找不到的代碼應在 verse 欄位含提示訊息。"""
        results = czs.batch_lookup(["不存在999"])
        assert "不存在999" in results[0]["verse"] or "無此代碼" in results[0]["verse"]


# ============================================================
# interpret 測試
# ============================================================


class TestInterpret:
    def test_known_code_returns_string(self, czs: ChunZiShu) -> None:
        """已知代碼應回傳非空字串。"""
        output = czs.interpret("畢龍6巳")
        assert isinstance(output, str)
        assert "畢龍6巳" in output

    def test_unknown_code_gives_hint(self, czs: ChunZiShu) -> None:
        """未知代碼應給出清楚提示，而非空白或例外。"""
        output = czs.interpret("不存在的代碼XYZ")
        assert "找不到" in output or "無此代碼" in output


# ============================================================
# explain 測試
# ============================================================


class TestExplain:
    def test_returns_dict(self, czs: ChunZiShu) -> None:
        """explain 應回傳字典。"""
        info = czs.explain("畢龍6巳")
        assert isinstance(info, dict)

    def test_has_required_keys(self, czs: ChunZiShu) -> None:
        """回傳字典應包含所有標準欄位。"""
        info = czs.explain("畢龍6巳")
        for key in (
            "code", "verse",
            "father_zodiac", "mother_zodiac", "spouse_zodiac",
            "children_count", "birth_hour", "birth_ke",
            "longevity", "flags",
        ):
            assert key in info

    def test_unknown_code_returns_error(self, czs: ChunZiShu) -> None:
        """未知代碼應在回傳字典中包含 error 欄位。"""
        info = czs.explain("不存在XYZ")
        assert "error" in info

    def test_parse_parents_from_verse(self, czs: ChunZiShu) -> None:
        """若詩詞含「父是屬X母屬Y」應正確解析父母屬相。"""
        from astro.chunzi import BRANCH_ZODIAC
        valid_zodiacs = set(BRANCH_ZODIAC.values())
        # 使用已知含父母屬相的詩詞
        result = czs.search("父是屬", limit=5)
        for r in result:
            info = czs.explain(r["code"])
            if info.get("father_zodiac"):
                # 解析出的屬相應為有效屬相
                assert info["father_zodiac"] in valid_zodiacs
                break

    def test_flags_is_list(self, czs: ChunZiShu) -> None:
        """flags 欄位應為列表。"""
        info = czs.explain("畢龍6巳")
        assert isinstance(info["flags"], list)

    def test_parse_longevity(self, czs: ChunZiShu) -> None:
        """若詩詞含「壽享X歲」應正確解析壽元。"""
        results = czs.search("壽享", limit=10)
        parsed_any = False
        for r in results:
            info = czs.explain(r["code"])
            if info.get("longevity") is not None:
                assert isinstance(info["longevity"], int)
                assert 40 <= info["longevity"] <= 120
                parsed_any = True
                break
        # 若有「壽享」詩詞存在，至少應能解析出一筆
        if results:
            assert parsed_any


# ============================================================
# get_hour_codes 測試
# ============================================================


class TestGetHourCodes:
    def test_returns_list(self, czs: ChunZiShu) -> None:
        """get_hour_codes 應回傳列表。"""
        results = czs.get_hour_codes("坤", "未")
        assert isinstance(results, list)

    def test_known_hour_returns_nonempty(self, czs: ChunZiShu) -> None:
        """已知時辰應回傳非空列表。"""
        results = czs.get_hour_codes("坤", "未")
        assert len(results) > 0

    def test_verse_contains_hour_pattern(self, czs: ChunZiShu) -> None:
        """所有回傳代碼的詩詞應包含「X時生人」文字。"""
        results = czs.get_hour_codes("乾", "子")
        for code in results:
            verse_row = czs.get_verse(code)
            assert verse_row is not None
            assert "子時生人" in verse_row["verse"]

    def test_accepts_full_pillar(self, czs: ChunZiShu) -> None:
        """get_hour_codes 應能接受完整八字柱（如「辛未」）並自動提取地支。"""
        by_branch = czs.get_hour_codes("坤", "未")
        by_pillar = czs.get_hour_codes("坤", "辛未")
        assert by_branch == by_pillar

    def test_invalid_branch_returns_empty(self, czs: ChunZiShu) -> None:
        """無效時辰應回傳空列表。"""
        results = czs.get_hour_codes("坤", "永")
        assert results == []

    def test_ke_intersection_filters(self, czs: ChunZiShu) -> None:
        """提供 ke 時，有時辰+刻數交集則應回傳更少的結果。"""
        without_ke = czs.get_hour_codes("坤", "未")
        with_ke = czs.get_hour_codes("坤", "未", ke=3)
        # ke 交集若非空，應比純時辰結果少（或相等，當所有時辰條文都匹配 ke 時）
        assert isinstance(with_ke, list)
        assert len(with_ke) <= len(without_ke)

    def test_ke_fallback_when_no_intersection(self, czs: ChunZiShu) -> None:
        """若時辰+刻數交集為空，應回退至純時辰匹配結果（非空）。"""
        # ke=99 必然無匹配，應回退
        results = czs.get_hour_codes("坤", "未", ke=99)
        # 回退結果應與不傳 ke 相同
        without_ke = czs.get_hour_codes("坤", "未")
        assert results == without_ke

    def test_female_priority(self, czs: ChunZiShu) -> None:
        """坤造結果應優先回傳 category == '女' 的詩詞代碼。"""
        results = czs.get_hour_codes("坤", "子")
        if not results:
            return  # 若無結果則跳過
        # 找第一個 category == "女" 的索引
        female_indices = []
        for i, code in enumerate(results):
            row = czs.get_verse(code)
            if row and row.get("category") == "女":
                female_indices.append(i)
        if female_indices:
            # 「女」分類詩詞應排在前面（索引較小）
            non_female_indices = [
                i for i, code in enumerate(results)
                if czs.get_verse(code) and czs.get_verse(code).get("category") != "女"
            ]
            if non_female_indices:
                assert min(female_indices) < max(non_female_indices) or \
                       min(female_indices) <= min(non_female_indices)


# ============================================================
# get_month_day_codes 測試
# ============================================================


class TestGetMonthDayCodes:
    def test_returns_list(self, czs: ChunZiShu) -> None:
        """get_month_day_codes 應回傳列表。"""
        results = czs.get_month_day_codes("坤", 5, 9)
        assert isinstance(results, list)

    def test_known_date_returns_nonempty(self, czs: ChunZiShu) -> None:
        """已知存在詩詞的月日組合應回傳非空列表。"""
        # 資料中存在「生辰五月初九日」的詩詞
        results = czs.get_month_day_codes("坤", 5, 9)
        assert len(results) > 0

    def test_invalid_month_returns_empty(self, czs: ChunZiShu) -> None:
        """月份超出範圍（13）應回傳空列表。"""
        results = czs.get_month_day_codes("坤", 13, 9)
        assert results == []

    def test_invalid_day_returns_empty(self, czs: ChunZiShu) -> None:
        """日期超出範圍（31）應回傳空列表。"""
        results = czs.get_month_day_codes("坤", 5, 31)
        assert results == []

    def test_verse_contains_month_pattern(self, czs: ChunZiShu) -> None:
        """回傳代碼的詩詞應同時包含月份與日期文字。"""
        results = czs.get_month_day_codes("坤", 5, 9)
        for code in results:
            row = czs.get_verse(code)
            assert row is not None
            assert "五月" in row["verse"]
            assert "初九" in row["verse"]


# ============================================================
# cast_chart 測試
# ============================================================


class TestCastChart:
    def test_returns_chart(self, czs: ChunZiShu) -> None:
        """cast_chart 應回傳 ChunZiChart 物件。"""
        from astro.chunzi import ChunZiChart
        chart = czs.cast_chart("坤", "丁丑", "乙巳", "甲子", "辛未", ke=3)
        assert isinstance(chart, ChunZiChart)

    def test_bazi_set_correctly(self, czs: ChunZiShu) -> None:
        """ChunZiChart.bazi 應為四柱空格連接的字串。"""
        chart = czs.cast_chart("坤", "丁丑", "乙巳", "甲子", "辛未", ke=3)
        assert chart.bazi == "丁丑 乙巳 甲子 辛未"

    def test_ke_set_correctly(self, czs: ChunZiShu) -> None:
        """ChunZiChart.ke 應與傳入值相同。"""
        chart = czs.cast_chart("坤", "丁丑", "乙巳", "甲子", "辛未", ke=3)
        assert chart.ke == 3

    def test_codes_nonempty_for_known_hour(self, czs: ChunZiShu) -> None:
        """有效時辰應產生至少一個候選代碼。"""
        chart = czs.cast_chart("坤", "丁丑", "乙巳", "甲子", "辛未")
        assert len(chart.codes) > 0

    def test_gender_validation(self, czs: ChunZiShu) -> None:
        """傳入無效 gender 應拋出 ValueError。"""
        import pytest
        with pytest.raises(ValueError):
            czs.cast_chart("男", "丁丑", "乙巳", "甲子", "辛未")

    def test_phase2_with_lunar_date(self, czs: ChunZiShu) -> None:
        """提供農曆月日時應合併月日條文。"""
        without_lunar = czs.cast_chart("坤", "癸丑", "壬戌", "庚寅", "丁丑", ke=6)
        with_lunar = czs.cast_chart(
            "坤", "癸丑", "壬戌", "庚寅", "丁丑", ke=6,
            lunar_month=5, lunar_day=9,
        )
        # 提供月日後，codes 應大於等於不提供時的數量
        assert len(with_lunar.codes) >= len(without_lunar.codes)

    def test_chart_has_analysis(self, czs: ChunZiShu) -> None:
        """cast_chart 回傳的 chart.analysis 應為非空字典。"""
        chart = czs.cast_chart("乾", "丁丑", "乙巳", "甲子", "辛未")
        assert isinstance(chart.analysis, dict)
        assert "parents" in chart.analysis

    def test_chart_summary_returns_string(self, czs: ChunZiShu) -> None:
        """chart.summary() 應回傳非空字串。"""
        chart = czs.cast_chart("坤", "丁丑", "乙巳", "甲子", "辛未", ke=3)
        summary = chart.summary()
        assert isinstance(summary, str)
        assert len(summary) > 0


# ============================================================
# ChunZiChart.to_json 測試
# ============================================================


class TestChunZiChartToJson:
    def test_returns_valid_json(self, czs: ChunZiShu) -> None:
        """to_json() 應回傳可解析的 JSON 字串。"""
        import json
        from astro.chunzi import ChunZiChart
        chart = ChunZiChart("坤", "丁丑 乙巳 甲子 辛未", ke=3)
        chart.add_codes(["室巨9未"], czs)
        data = json.loads(chart.to_json())
        assert data["gender"] == "坤"
        assert data["ke"] == 3

    def test_json_has_all_keys(self, czs: ChunZiShu) -> None:
        """to_json() 解析後應包含 gender、bazi、ke、codes、analysis 欄位。"""
        import json
        from astro.chunzi import ChunZiChart
        chart = ChunZiChart("坤", "丁丑 乙巳 甲子 辛未", ke=3)
        chart.add_codes(["室巨9未"], czs)
        data = json.loads(chart.to_json())
        for key in ("gender", "bazi", "ke", "codes", "analysis"):
            assert key in data

    def test_json_preserves_chinese(self, czs: ChunZiShu) -> None:
        """to_json() 預設應保留中文字元（ensure_ascii=False）。"""
        from astro.chunzi import ChunZiChart
        chart = ChunZiChart("坤", "丁丑 乙巳 甲子 辛未", ke=3)
        chart.add_codes(["室巨9未"], czs)
        result = chart.to_json()
        assert "坤" in result

