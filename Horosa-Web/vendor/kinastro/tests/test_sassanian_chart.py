"""
tests/test_sassanian_chart.py — 薩珊傳統占星星盤測試

Test Suite for Sassanian Traditional Star Chart
使用歷史星盤資料（281 CE 和 381 CE）進行測試

References
----------
- Pingree, D. (1976). Dorotheus of Sidon, Pahlavi translation
- Historical Sassanian horoscopes from 281 CE and 381 CE
"""

import pytest
from datetime import datetime
import swisseph as swe

from astro.persian.sassanian_astronomy import (
    compute_sassanian_planet_positions,
    get_sassanian_houses,
    get_royal_stars_positions,
    calculate_sassanian_ayanamsa,
    HISTORICAL_HOROSCOPES,
)
from astro.persian.sassanian_chart_renderer import (
    generate_sassanian_chart,
    render_sassanian_banner_chart,
)
from astro.persian.sassanian_symbols import (
    get_sassanian_color_palette,
    get_pahlavi_name,
    get_royal_star_pahlavi,
)


class TestSassanianAstronomy:
    """薩珊天文計算測試"""

    def test_sassanian_ayanamsa_modern(self):
        """測試現代日期的薩珊 Ayanamsa"""
        julian_day = swe.julday(2000, 1, 1, 12, 0)
        ayanamsa = calculate_sassanian_ayanamsa(julian_day)

        # 薩珊 Ayanamsa 在 J2000 應約為 22°
        assert 21.0 < ayanamsa < 23.0, f"Expected ~22°, got {ayanamsa:.2f}°"

    def test_sassanian_ayanamsa_historical(self):
        """測試歷史日期的薩珊 Ayanamsa"""
        # 500 CE 的薩珊 Ayanamsa 應約為 21.5°
        julian_day = swe.julday(500, 1, 1, 12, 0)
        ayanamsa = calculate_sassanian_ayanamsa(julian_day)

        assert 20.0 < ayanamsa < 22.0, f"Expected ~21.5°, got {ayanamsa:.2f}°"

    def test_royal_stars_positions(self):
        """測試皇家恆星位置"""
        julian_day = swe.julday(2000, 1, 1, 12, 0)
        royal_stars = get_royal_stars_positions(julian_day)

        # 應有四顆皇家恆星
        assert len(royal_stars) == 4

        # 檢查 Aldebaran (Tascheter)
        assert "Aldebaran" in royal_stars
        assert royal_stars["Aldebaran"]["name_pahlavi"] == "Tascheter"
        assert royal_stars["Aldebaran"]["constellation"] == "Taurus"

        # 檢查 Regulus (Vanand)
        assert "Regulus" in royal_stars
        assert royal_stars["Regulus"]["name_pahlavi"] == "Vanand"
        assert royal_stars["Regulus"]["constellation"] == "Leo"

        # 檢查 Antares (Satevis)
        assert "Antares" in royal_stars
        assert royal_stars["Antares"]["name_pahlavi"] == "Satevis"
        assert royal_stars["Antares"]["constellation"] == "Scorpio"

        # 檢查 Fomalhaut (Hastorang)
        assert "Fomalhaut" in royal_stars
        assert royal_stars["Fomalhaut"]["name_pahlavi"] == "Hastorang"
        assert royal_stars["Fomalhaut"]["constellation"] == "Pisces"

    def test_planet_positions(self):
        """測試行星位置計算"""
        positions = compute_sassanian_planet_positions(
            year=1980, month=1, day=15, hour=10, minute=30,
            longitude=121.5, latitude=25.0, timezone=8.0
        )

        # 應有 7 顆傳統行星
        assert len(positions) == 7

        # 檢查行星名稱
        planet_names = [p.name for p in positions]
        expected = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        assert planet_names == expected

        # 檢查 Pahlavi 名稱
        for pos in positions:
            assert pos.name_pahlavi is not None
            assert pos.sign_pahlavi is not None

        # 檢查宮位範圍（1-12）
        for pos in positions:
            assert 1 <= pos.house <= 12

    def test_sassanian_houses(self):
        """測試薩珊整宮制宮位"""
        houses = get_sassanian_houses(
            year=1980, month=1, day=15, hour=10, minute=30,
            longitude=121.5, latitude=25.0, timezone=8.0
        )

        # 應有 12 個宮位
        assert len(houses) == 12

        # 檢查宮位編號
        house_numbers = [h["house_number"] for h in houses]
        assert house_numbers == list(range(1, 13))

        # 檢查宮位意義（Pahlavi）
        assert houses[0]["meaning_pahlavi"] == "Jan"  # 第 1 宮
        assert houses[3]["meaning_pahlavi"] == "Pidar"  # 第 4 宮
        assert houses[9]["meaning_pahlavi"] == "Kar"  # 第 10 宮

        # 檢查宮位經度範圍（整宮制：每宮 30°）
        for i, house in enumerate(houses):
            expected_start = i * 30
            expected_end = (i + 1) * 30
            # 注意：實際起始點取決於上升點
            assert house["longitude_end"] - house["longitude_start"] == 30


class TestHistoricalHoroscopes:
    """歷史星盤測試（281 CE 和 381 CE）"""

    def test_281_ce_horoscope(self):
        """測試 281 CE 歷史星盤"""
        horoscope = HISTORICAL_HOROSCOPES["281_CE"]

        # 計算行星位置
        date = horoscope["date"]
        loc = horoscope["location"]

        positions = compute_sassanian_planet_positions(
            year=date.year, month=date.month, day=date.day,
            hour=date.hour, minute=date.minute,
            longitude=loc["longitude"], latitude=loc["latitude"],
            timezone=loc["timezone"]
        )

        # 應成功計算 7 顆行星
        assert len(positions) == 7

        # 計算宮位
        houses = get_sassanian_houses(
            year=date.year, month=date.month, day=date.day,
            hour=date.hour, minute=date.minute,
            longitude=loc["longitude"], latitude=loc["latitude"],
            timezone=loc["timezone"]
        )

        assert len(houses) == 12

    def test_381_ce_horoscope(self):
        """測試 381 CE 歷史星盤"""
        horoscope = HISTORICAL_HOROSCOPES["381_CE"]

        # 計算行星位置
        date = horoscope["date"]
        loc = horoscope["location"]

        positions = compute_sassanian_planet_positions(
            year=date.year, month=date.month, day=date.day,
            hour=date.hour, minute=date.minute,
            longitude=loc["longitude"], latitude=loc["latitude"],
            timezone=loc["timezone"]
        )

        # 應成功計算 7 顆行星
        assert len(positions) == 7

        # 計算宮位
        houses = get_sassanian_houses(
            year=date.year, month=date.month, day=date.day,
            hour=date.hour, minute=date.minute,
            longitude=loc["longitude"], latitude=loc["latitude"],
            timezone=loc["timezone"]
        )

        assert len(houses) == 12


class TestSassanianChartRenderer:
    """薩珊星盤渲染器測試"""

    def test_generate_sassanian_chart(self):
        """測試生成薩珊星盤"""
        chart_data = {
            "year": 1980,
            "month": 1,
            "day": 15,
            "hour": 10,
            "minute": 30,
            "longitude": 121.5,
            "latitude": 25.0,
            "timezone": 8.0,
        }

        fig = generate_sassanian_chart(chart_data)

        # 檢查圖表屬性
        assert fig is not None
        assert fig.layout.width == 1200
        assert fig.layout.height == 900
        assert fig.layout.plot_bgcolor == "#F5E6D3"  # parchment

    def test_generate_sassanian_chart_with_firdar(self):
        """測試生成帶 Firdar 時間線的薩珊星盤"""
        chart_data = {
            "year": 1980,
            "month": 1,
            "day": 15,
            "hour": 10,
            "minute": 30,
            "longitude": 121.5,
            "latitude": 25.0,
            "timezone": 8.0,
        }

        fig = generate_sassanian_chart(chart_data, show_firdar=True)

        # 帶 Firdar 時應有 2 行子圖
        assert len(fig subplot specs) == 2

    def test_render_sassanian_banner_chart(self):
        """測試渲染橫幅格式薩珊星盤"""
        chart_data = {
            "year": 1980,
            "month": 1,
            "day": 15,
            "hour": 10,
            "minute": 30,
            "longitude": 121.5,
            "latitude": 25.0,
            "timezone": 8.0,
        }

        fig = render_sassanian_banner_chart(chart_data)

        # 檢查橫幅格式尺寸
        assert fig is not None
        assert fig.layout.width == 1400
        assert fig.layout.height == 600

    def test_historical_chart_281_ce(self):
        """測試 281 CE 歷史星盤渲染"""
        chart_data = {
            "year": 281,
            "month": 3,
            "day": 15,
            "hour": 12,
            "minute": 0,
            "longitude": 44.5,
            "latitude": 33.3,
            "timezone": 3.0,
        }

        fig = generate_sassanian_chart(chart_data)
        assert fig is not None

    def test_historical_chart_381_ce(self):
        """測試 381 CE 歷史星盤渲染"""
        chart_data = {
            "year": 381,
            "month": 7,
            "day": 22,
            "hour": 6,
            "minute": 0,
            "longitude": 44.5,
            "latitude": 33.3,
            "timezone": 3.0,
        }

        fig = generate_sassanian_chart(chart_data)
        assert fig is not None


class TestSassanianSymbols:
    """薩珊符號系統測試"""

    def test_color_palette(self):
        """測試薩珊色彩調色盤"""
        palette = get_sassanian_color_palette()

        # 檢查關鍵顏色
        assert "crimson" in palette
        assert "gold_leaf" in palette
        assert "turquoise" in palette
        assert "dark_indigo" in palette
        assert "parchment" in palette

        # 檢查顏色格式（HEX）
        for color_name, color_hex in palette.items():
            assert color_hex.startswith("#")
            assert len(color_hex) == 7

    def test_pahlavi_planet_names(self):
        """測試 Pahlavi 行星名稱"""
        expected_names = {
            "Sun": "Khwarshid",
            "Moon": "Mah",
            "Mercury": "Tir",
            "Venus": "Anahid",
            "Mars": "Warhran",
            "Jupiter": "Ohrmazd",
            "Saturn": "Keyvan",
        }

        for planet_en, expected_pahlavi in expected_names.items():
            info = get_pahlavi_name("planets", planet_en)
            assert info is not None
            assert info["pahlavi"] == expected_pahlavi

    def test_pahlavi_zodiac_names(self):
        """測試 Pahlavi 星座名稱"""
        # 測試部分星座
        info = get_pahlavi_name("zodiac_signs", "Aries")
        assert info is not None
        assert info["pahlavi"] == "Warz"

        info = get_pahlavi_name("zodiac_signs", "Leo")
        assert info is not None
        assert info["pahlavi"] == "Sher"

    def test_royal_star_pahlavi(self):
        """測試皇家恆星 Pahlavi 名稱"""
        expected = {
            "Aldebaran": "Tascheter",
            "Regulus": "Vanand",
            "Antares": "Satevis",
            "Fomalhaut": "Hastorang",
        }

        for star_en, expected_pahlavi in expected.items():
            info = get_royal_star_pahlavi(star_en)
            assert info is not None
            assert info["name_pahlavi"] == expected_pahlavi


class TestSassanianIntegration:
    """薩珊系統整合測試"""

    def test_full_chart_workflow(self):
        """測試完整星盤工作流程"""
        # 1. 計算行星位置
        positions = compute_sassanian_planet_positions(
            year=1980, month=1, day=15, hour=10, minute=30,
            longitude=121.5, latitude=25.0, timezone=8.0
        )

        # 2. 計算宮位
        houses = get_sassanian_houses(
            year=1980, month=1, day=15, hour=10, minute=30,
            longitude=121.5, latitude=25.0, timezone=8.0
        )

        # 3. 獲取皇家恆星
        julian_day = swe.julday(1980, 1, 15, 10.5)
        royal_stars = get_royal_stars_positions(julian_day)

        # 4. 生成星盤
        chart_data = {
            "year": 1980,
            "month": 1,
            "day": 15,
            "hour": 10,
            "minute": 30,
            "longitude": 121.5,
            "latitude": 25.0,
            "timezone": 8.0,
        }

        fig = generate_sassanian_chart(chart_data)

        # 5. 驗證所有組件
        assert len(positions) == 7
        assert len(houses) == 12
        assert len(royal_stars) == 4
        assert fig is not None

    def test_bilingual_support(self):
        """測試雙語支援（Pahlavi 開關）"""
        chart_data = {
            "year": 1980,
            "month": 1,
            "day": 15,
            "hour": 10,
            "minute": 30,
            "longitude": 121.5,
            "latitude": 25.0,
            "timezone": 8.0,
        }

        # 帶 Pahlavi
        fig_with_pahlavi = generate_sassanian_chart(chart_data, show_pahlavi=True)
        assert fig_with_pahlavi is not None

        # 不帶 Pahlavi
        fig_without_pahlavi = generate_sassanian_chart(chart_data, show_pahlavi=False)
        assert fig_without_pahlavi is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
