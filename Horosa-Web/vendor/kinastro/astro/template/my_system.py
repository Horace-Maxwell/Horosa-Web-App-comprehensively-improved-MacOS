"""
astro/template/my_system.py — 新占星體系模板 (New Astrology System Template)

使用方法：
  1. 複製此檔案到 astro/ 或 astro/<子目錄>/
  2. 重新命名並實作 compute_xxx_chart() 和 render_xxx_chart()
  3. 在 app.py 的 _SYSTEM_KEYS 加入新 tab key
  4. 在 astro/i18n.py 加入翻譯 key
  5. 在 tests/test_new_astrology.py 加入測試
"""

from dataclasses import dataclass, field
from typing import List

import streamlit as st


# ============================================================
# 資料模型 (Data Models)
# ============================================================

@dataclass
class MyPlanet:
    """行星 / 星體資料。"""
    name: str = ""
    name_cn: str = ""
    longitude: float = 0.0
    sign: str = ""
    sign_degree: float = 0.0
    retrograde: bool = False
    house: int = 0


@dataclass
class MySystemChart:
    """排盤結果資料類。

    所有體系共用的基本欄位放在前面，
    體系特有的欄位放在後面。
    """
    # ── 共用欄位 (Common fields) ──
    year: int = 0
    month: int = 0
    day: int = 0
    hour: int = 0
    minute: int = 0
    timezone: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    location_name: str = ""
    julian_day: float = 0.0
    planets: List[MyPlanet] = field(default_factory=list)

    # ── 體系特有欄位 (System-specific fields) ──
    # my_special_field: str = ""
    # my_houses: list = field(default_factory=list)


# ============================================================
# 核心計算 (Core Computation)
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_my_system_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
) -> MySystemChart:
    """核心計算函式。

    注意事項：
    - 必須是純函式（無副作用）以支援 @st.cache_data 快取
    - 參數必須是基本型別（int, float, str, bool）
    - 返回值必須是可序列化的 dataclass
    """
    chart = MySystemChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )

    # TODO: 在此實作計算邏輯
    # 如需使用 pyswisseph:
    #   import swisseph as swe
    #   decimal_hour = hour + minute / 60.0 - timezone
    #   jd = swe.julday(year, month, day, decimal_hour)
    #   chart.julian_day = jd

    return chart


# ============================================================
# Streamlit 渲染 (UI Rendering)
# ============================================================

def render_my_system_chart(chart: MySystemChart):
    """Streamlit 渲染函式。

    此函式負責把計算結果以視覺化的方式呈現在 Streamlit 頁面上。
    """
    st.subheader("我的占星體系")

    # ── 基本資料 ──
    st.info(
        f"📅 {chart.year}-{chart.month:02d}-{chart.day:02d} "
        f"{chart.hour:02d}:{chart.minute:02d} "
        f"(UTC{chart.timezone:+.1f})"
    )

    # ── 行星表格 ──
    if chart.planets:
        st.dataframe(
            [
                {
                    "Name": f"{p.name} ({p.name_cn})",
                    "Sign": p.sign,
                    "Degree": f"{p.sign_degree:.2f}°",
                    "R": "R" if p.retrograde else "",
                }
                for p in chart.planets
            ],
            width="stretch",
        )

    # ── 匯出按鈕 (可選) ──
    # from astro.export import render_download_buttons
    # render_download_buttons(my_chart_to_dict(chart), key_prefix="my_system")
