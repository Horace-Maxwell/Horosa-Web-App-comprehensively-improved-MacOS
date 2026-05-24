# Contributing to 堅占星 Kin Astro

感謝你對 Kin Astro 的興趣！以下是參與開發的指南。

## 開發環境

```bash
# 安裝依賴
pip install -r requirements.txt
pip install pytest

# 運行 Streamlit 前端
streamlit run app.py

# 運行 FastAPI 後端
uvicorn api_server:app --reload

# 運行測試
python -m pytest tests/ -q
```

## 專案結構

```
kinastro/
├── app.py                  # Streamlit 主應用 (UI 層)
├── api_server.py           # FastAPI 後端 (計算 API)
├── astro/
│   ├── calculator.py       # 核心天文計算 (pyswisseph)
│   ├── chart_renderer.py   # 中國七政四餘盤面渲染
│   ├── chart_theme.py      # 統一主題色、CSS、SVG 樣式
│   ├── export.py           # 匯出功能 (TXT/CSV/PDF/PNG/分享連結)
│   ├── i18n.py             # 中英雙語翻譯字典
│   ├── interpretations.py  # 文字解讀 (流年/合盤/大限)
│   ├── natal_summary.py    # 命盤摘要生成
│   ├── constants.py        # 七政四餘常量定義
│   ├── western.py          # 西洋占星
│   ├── indian.py           # 印度占星 (Vedic/Jyotish)
│   ├── thai.py             # 泰國占星
│   ├── ...                 # 其他占星體系
│   ├── classic/            # 古典文獻 (百論等)
│   ├── reference/          # 參考資料 (markdown)
│   └── data/               # JSON 資料檔 (恆星、Picatrix 等)
├── tests/
│   ├── test_calculator.py
│   ├── test_advanced_features.py
│   └── test_new_astrology.py
└── requirements.txt
```

## 如何新增一個新的占星體系

以下是新增占星體系的完整步驟模板，以「XX 占星」為例：

### 步驟 1：建立計算模組

在 `astro/` 目錄下新建 `xx_astro.py`：

```python
"""
astro/xx_astro.py — XX 占星計算模組
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class XXPlanet:
    """單顆星曜的資料結構"""
    name: str
    name_cn: str
    longitude: float
    sign: str = ""
    sign_degree: float = 0.0
    retrograde: bool = False


@dataclass
class XXChart:
    """完整排盤結果"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    julian_day: float = 0.0
    planets: List[XXPlanet] = field(default_factory=list)
    # ... 體系特有欄位


def compute_xx_chart(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float, latitude: float, longitude: float,
    location_name: str = "",
) -> XXChart:
    """核心計算函式 — 必須是純計算，不可依賴 Streamlit。"""
    import swisseph as swe

    # 1. 計算 Julian Day
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)

    # 2. 計算星曜位置
    planets = []
    # ... 你的計算邏輯

    return XXChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
        julian_day=jd,
        planets=planets,
    )


def render_xx_chart(chart: XXChart):
    """Streamlit 渲染函式 — 僅在此處 import streamlit。"""
    import streamlit as st

    st.subheader(f"XX 占星 — {chart.location_name}")
    # ... 你的 UI 渲染邏輯
    if chart.planets:
        st.dataframe(
            [{"Name": p.name, "Sign": p.sign, "Degree": f"{p.sign_degree:.2f}°"}
             for p in chart.planets],
            width="stretch",
        )
```

### 步驟 2：加入 i18n 翻譯

在 `astro/i18n.py` 的 `TRANSLATIONS` 字典中加入：

```python
# Tab 標題
"tab_xx": {"zh": "XX占星", "en": "XX Astrology"},
# 描述文字（未排盤時顯示）
"desc_xx": {
    "zh": "**XX占星**\n\n此體系的簡介...",
    "en": "**XX Astrology**\n\nBrief introduction...",
},
# Loading spinner
"spinner_xx": {"zh": "計算 XX 占星中...", "en": "Computing XX chart…"},
```

### 步驟 3：在 app.py 中加入 Tab

```python
# 1. 頂部加入 import
from astro.xx_astro import compute_xx_chart, render_xx_chart

# 2. 在 st.tabs() 列表中加入新 tab
tab_..., tab_xx = st.tabs([..., t("tab_xx")])

# 3. 加入 tab 內容
with tab_xx:
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_xx")):
                xx_chart = compute_xx_chart(**_p)
            render_xx_chart(xx_chart)
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_xx"))
```

### 步驟 4：在 api_server.py 中加入 API endpoint

```python
@app.post("/api/xx")
async def api_xx(params: BirthParams):
    try:
        chart = compute_xx_chart(**_base_kwargs(params))
        return {"status": "ok", "data": _make_serializable(chart)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
```

### 步驟 5：加入測試

在 `tests/test_new_astrology.py` 中新建測試類別：

```python
class TestXXAstrology(unittest.TestCase):
    """Tests for XX astrology module."""

    def test_compute_chart_basic(self):
        chart = compute_xx_chart(
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone=8.0, latitude=22.3193, longitude=114.1694,
            location_name="Hong Kong",
        )
        self.assertIsNotNone(chart)
        self.assertGreater(len(chart.planets), 0)

    def test_planet_longitudes_in_range(self):
        chart = compute_xx_chart(...)
        for p in chart.planets:
            self.assertGreaterEqual(p.longitude, 0.0)
            self.assertLess(p.longitude, 360.0)
```

### 步驟 6：更新文件

- 在 `README.md` 的體系列表中加入新體系
- 在 `CHANGELOG.md` 中記錄新增

## 提交規範

- Commit message 使用英文，簡潔描述改動
- 每個 PR 專注一個功能或修復
- 確保所有測試通過：`python -m pytest tests/ -q`
- 不要移除或修改無關的測試

## 程式碼風格

- 計算函式（`compute_*`）必須是純函式，不依賴 Streamlit
- 渲染函式（`render_*`）內部 `import streamlit as st`
- 使用 `@dataclass` 定義資料結構
- 使用 `astro/i18n.py` 管理所有 UI 文字
- 圖表主題使用 `astro/chart_theme.py` 中的統一色彩

## 回報問題

在 GitHub Issues 中提交問題時請附上：
1. 使用的出生資料（日期、時間、地點）
2. 出錯的體系名稱
3. 錯誤訊息截圖或文字
