"""
astro/kp/kp_renderer.py — KP 占星術 Streamlit 渲染器

Krishnamurti Paddhati (KP Astrology) Chart Renderer

提供：
1. KP 命盤主界面渲染
2. 行星位置表格（含 Rasi/Star/Sub Lords）
3. 12 宮頭表格（含 Sub Lords）
4. Ruling Planets 顯示
5. Significators 分析面板
6. Horary（問卜）模式界面
7. SVG 星盤圖（KP 專用風格）

References
----------
- Krishnamurti, K.S. "KP Reader Vol. I: Fundamentals"
- Streamlit Documentation
"""

from typing import Dict, List, Optional, Any
import streamlit as st
from html import escape as html_escape

from astro.kp.kp_calculator import KPChart, KPPlanetPosition, KPCusp
from astro.kp.constants import KP_COLORS, PLANETS, HOUSES
from astro.kp.kp_utils import (
    planet_name_translate,
    house_name_translate,
    get_significators,
)

# ── SVG 星盤圖常數 ──────────────────────────────────────────────────────────
_CHART_FONT = "'PingFang TC','Noto Sans TC','Microsoft JhengHei','Segoe UI',sans-serif"
_CHART_PLANETS_PER_ROW = 3   # 每行最多顯示的行星數
_CHART_MAX_PLANETS = 6        # 每宮最多顯示的行星數（2 行 × 3 顆）


# ============================================================================
# MAIN RENDERING FUNCTION
# ============================================================================

def render_kp_chart(
    chart: KPChart,
    language: str = "zh",
    show_ruling_planets: bool = True,
    show_significators: bool = True,
    show_svg_chart: bool = True,
) -> None:
    """
    渲染完整的 KP 命盤界面
    
    Parameters
    ----------
    chart : KPChart
        KP 命盤物件
    language : str
        語言（"en" / "zh"）
    show_ruling_planets : bool
        是否顯示 Ruling Planets
    show_significators : bool
        是否顯示 Significators
    show_svg_chart : bool
        是否顯示 SVG 星盤圖
    """
    # 顯示模式標籤
    if chart.is_horary:
        st.info("📍 **問卜模式 (Horary)** — 使用提問時間與地點")
    else:
        st.info("👤 **本命模式 (Natal)** — 使用出生時間與地點")
    
    # KP SVG 星盤圖（放在最上方，最顯眼位置）
    if show_svg_chart:
        _render_kp_svg_chart(chart, language)
    
    # 分隔線
    st.divider()
    
    # 主要內容區域（兩欄布局）
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 行星位置表格
        _render_planet_table(chart.planets, language)
        
        # 12 宮頭表格
        _render_cusp_table(chart.cusps, chart.house_lords, language)
    
    with col2:
        # Ruling Planets
        if show_ruling_planets:
            _render_ruling_planets(chart.ruling_planets, language)
        
        # KP Ayanamsa 資訊
        _render_ayanamsa_info(chart.ayanamsa)
    
    # 詳細分析區域
    if show_significators:
        _render_significators_analysis(chart.significators, language)


# ============================================================================
# KP SVG CHART RENDERING (North Indian Style Diamond Chart)
# ============================================================================

def _render_kp_svg_chart(chart: KPChart, language: str = "zh") -> None:
    """
    渲染 KP 北印度式鑽石形星盤圖（響應式）
    """
    st.subheader("🔮 KP 星盤圖 (North Indian Diamond Style)")

    try:
        svg_content = _generate_kp_diamond_svg(chart, language)

        # 以完整 HTML 頁面包裝 SVG，實現響應式縮放
        html = f"""<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{ width: 100%; background: transparent; overflow: hidden; }}
    .chart-wrap {{
      width: 100%;
      max-width: 580px;
      margin: 0 auto;
      aspect-ratio: 1 / 1;
    }}
    .chart-wrap svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}
  </style>
</head>
<body>
  <div class="chart-wrap" id="chartWrap">
    {svg_content}
  </div>
  <script>
    function reportHeight() {{
      var h = document.getElementById('chartWrap').getBoundingClientRect().height;
      window.parent.postMessage({{type: 'streamlit:setFrameHeight', height: Math.ceil(h) + 4}}, '*');
    }}
    if (window.ResizeObserver) {{
      new ResizeObserver(reportHeight).observe(document.getElementById('chartWrap'));
    }} else {{
      window.addEventListener('resize', reportHeight);
    }}
    window.addEventListener('load', reportHeight);
    setTimeout(reportHeight, 150);
  </script>
</body>
</html>"""

        # 使用 st.components.v1.html 顯示響應式 SVG
        st.components.v1.html(html, height=600, scrolling=False)
    except Exception as e:
        st.error(f"星盤圖生成失敗：{str(e)}")
        import traceback
        st.code(traceback.format_exc())


def _generate_kp_diamond_svg(chart: KPChart, language: str = "zh") -> str:
    """
    生成 KP 北印度鑽石形星盤 SVG（響應式 + 美化版）
    SVG 使用 viewBox 而不固定 width/height，由外層 CSS 控制縮放。
    """
    FONT = _CHART_FONT

    def sign_index(longitude: float) -> int:
        return int(longitude // 30) % 12

    def planet_short(name: str) -> str:
        short_map = {
            "Sun": "Su", "Moon": "Mo", "Mars": "Ma",
            "Mercury": "Me", "Jupiter": "Ju", "Venus": "Ve",
            "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke",
            "Ascendant": "Asc"
        }
        return short_map.get(name, name[:3])

    def sign_name(index: int, lang: str = "zh") -> str:
        signs_zh = ["白羊", "金牛", "雙子", "巨蟹", "獅子", "處女",
                    "天秤", "天蠍", "射手", "摩羯", "水瓶", "雙魚"]
        signs_en = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
                    "Lib", "Sco", "Sag", "Cap", "Aqr", "Pis"]
        return signs_zh[index] if lang == "zh" else signs_en[index]

    # Ascendant 上升點所在星座
    asc_idx = sign_index(chart.cusps[0].longitude)

    # 行星按星座（Rashi）收集
    rashi_planets = {i: [] for i in range(12)}
    for p in chart.planets:
        if p.name != "Ascendant":
            idx = sign_index(p.longitude)
            rashi_planets[idx].append(planet_short(p.name))

    # SVG 邏輯尺寸（僅用於 viewBox，不作為實際像素）
    S = 480
    M = 40
    C = S / 2  # center

    # ── SVG 開頭：width/height 設為 100%，由外層 CSS aspect-ratio 控制比例 ──
    svg = [
        f'<svg viewBox="0 0 {S} {S}" xmlns="http://www.w3.org/2000/svg" '
        f'width="100%" height="100%" preserveAspectRatio="xMidYMid meet">'
    ]

    # ── defs：漸層背景 + 橘色光暈濾鏡 ──
    svg.append('<defs>')
    svg.append(
        '<linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" style="stop-color:#0e0e22;stop-opacity:1"/>'
        '<stop offset="100%" style="stop-color:#1c1c3a;stop-opacity:1"/>'
        '</linearGradient>'
    )
    svg.append(
        '<linearGradient id="innerGrad" x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" style="stop-color:#22224a;stop-opacity:1"/>'
        '<stop offset="100%" style="stop-color:#2a2a52;stop-opacity:1"/>'
        '</linearGradient>'
    )
    svg.append(
        '<filter id="glow" x="-25%" y="-25%" width="150%" height="150%">'
        '<feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>'
        '<feMerge>'
        '<feMergeNode in="coloredBlur"/>'
        '<feMergeNode in="SourceGraphic"/>'
        '</feMerge>'
        '</filter>'
    )
    svg.append(
        '<filter id="centerGlow" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="4" result="coloredBlur"/>'
        '<feMerge>'
        '<feMergeNode in="coloredBlur"/>'
        '<feMergeNode in="SourceGraphic"/>'
        '</feMerge>'
        '</filter>'
    )
    svg.append('</defs>')

    # ── 背景 ──
    svg.append(f'<rect width="{S}" height="{S}" fill="url(#bgGrad)"/>')

    # ── 外框 ──
    svg.append(
        f'<rect x="{M}" y="{M}" width="{S-2*M}" height="{S-2*M}" '
        f'fill="url(#innerGrad)" stroke="#E8632A" stroke-width="2.5" rx="6" '
        f'filter="url(#glow)"/>'
    )

    # ── 北印度式四對角線（帶光暈） ──
    diag_style = 'stroke="#D4622A" stroke-width="1.8" filter="url(#glow)"'
    svg.append(f'<line x1="{M}" y1="{M}" x2="{C}" y2="{C}" {diag_style}/>')
    svg.append(f'<line x1="{C}" y1="{C}" x2="{S-M}" y2="{M}" {diag_style}/>')
    svg.append(f'<line x1="{M}" y1="{S-M}" x2="{C}" y2="{C}" {diag_style}/>')
    svg.append(f'<line x1="{C}" y1="{C}" x2="{S-M}" y2="{S-M}" {diag_style}/>')

    # ── 十字中線 ──
    cross_style = 'stroke="#3a3a6a" stroke-width="1.5"'
    svg.append(f'<line x1="{M}" y1="{C}" x2="{S-M}" y2="{C}" {cross_style}/>')
    svg.append(f'<line x1="{C}" y1="{M}" x2="{C}" y2="{S-M}" {cross_style}/>')

    # ── 12 宮位文字座標 ──
    house_pos = {
        1:  (C,         M + 58),
        2:  (M + 68,    M + 115),
        3:  (M + 55,    C - 12),
        4:  (M + 68,    S - M - 72),
        5:  (C - 5,     S - M - 55),
        6:  (S-M - 68,  S - M - 72),
        7:  (S-M - 55,  C + 30),
        8:  (S-M - 68,  M + 115),
        9:  (C + 70,    M + 55),
        10: (S-M - 55,  M + 68),
        11: (S-M - 70,  M + 85),
        12: (C + 65,    M + 105),
    }

    for house_num in range(1, 13):
        sign_idx = (asc_idx + house_num - 1) % 12
        x, y = house_pos[house_num]

        # 星座名稱
        svg.append(
            f'<text x="{x}" y="{y}" '
            f'fill="#FFD966" font-size="14" font-weight="700" '
            f'font-family={FONT} '
            f'text-anchor="middle" dominant-baseline="middle">'
            f'{sign_name(sign_idx, language)}</text>'
        )

        # 宮位編號（小字，灰色）
        svg.append(
            f'<text x="{x}" y="{y + 20}" '
            f'fill="#888aaa" font-size="10" font-weight="600" '
            f'font-family={FONT} text-anchor="middle">'
            f'H{house_num}</text>'
        )

        # 行星列表：每行最多 _CHART_PLANETS_PER_ROW 個，最多顯示 _CHART_MAX_PLANETS 顆
        planets_list = rashi_planets.get(sign_idx, [])
        if planets_list:
            chunks = [
                planets_list[i:i + _CHART_PLANETS_PER_ROW]
                for i in range(0, min(len(planets_list), _CHART_MAX_PLANETS), _CHART_PLANETS_PER_ROW)
            ]
            for row_i, chunk in enumerate(chunks):
                py = y + 36 + row_i * 16
                svg.append(
                    f'<text x="{x}" y="{py}" '
                    f'fill="#7ecfff" font-size="11.5" font-weight="600" '
                    f'font-family={FONT} text-anchor="middle">'
                    f'{" ".join(chunk)}</text>'
                )

    # ── 中央 Lagna 資訊區（帶光暈） ──
    svg.append(
        f'<rect x="{C-56}" y="{C-38}" width="112" height="74" '
        f'rx="10" fill="#14143a" stroke="#E8632A" stroke-width="2" '
        f'filter="url(#centerGlow)"/>'
    )
    svg.append(
        f'<text x="{C}" y="{C-12}" fill="#E8632A" font-size="13" '
        f'font-weight="700" font-family={FONT} text-anchor="middle" '
        f'letter-spacing="1">Lagna</text>'
    )
    svg.append(
        f'<text x="{C}" y="{C+16}" fill="#FFE066" font-size="17" '
        f'font-weight="700" font-family={FONT} text-anchor="middle">'
        f'{sign_name(asc_idx, language)}</text>'
    )

    svg.append('</svg>')
    return '\n'.join(svg)


def _get_house_label_position(house_num: int, margin: float, center: float, half: float, size: float = 450) -> tuple:
    """
    獲取宮位標籤位置
    
    Parameters
    ----------
    house_num : int
        宮位編號 (1-12)
    margin : float
        邊距
    center : float
        中心點
    half : float
        半寬度
    size : float
        SVG 總尺寸
    
    Returns
    -------
    tuple
        (x, y) 座標
    """
    S = size
    # 簡化：根據宮位返回大致位置
    positions = {
        1: (margin + 40, margin + 30),
        2: (margin + 30, margin + 80),
        3: (margin + 30, center + 80),
        4: (margin + 40, S - margin - 30),
        5: (center, S - margin - 20),
        6: (S - margin - 40, S - margin - 30),
        7: (S - margin - 30, center + 80),
        8: (S - margin - 30, margin + 80),
        9: (S - margin - 40, margin + 30),
        10: (center, margin + 30),
        11: (S - margin - 60, margin + 30),
        12: (center + 60, margin + 30),
    }
    return positions.get(house_num, (center, center))


# ============================================================================
# PLANET TABLE
# ============================================================================

def _render_planet_table(
    planets: List[KPPlanetPosition],
    language: str = "zh",
) -> None:
    """
    渲染行星位置表格
    
    Parameters
    ----------
    planets : List[KPPlanetPosition]
        行星位置列表
    language : str
        語言
    """
    st.subheader("🪐 行星位置 (Planetary Positions)")
    
    # 準備表格數據
    table_data = []
    
    for planet in planets:
        # 行星符號和名稱
        if language == "zh":
            planet_name = f"{planet.name_cn} {planet.name}"
        else:
            planet_name = planet.name
        
        # 逆行標記
        retro = "℞" if planet.is_retrograde else ""
        
        # 宮位
        house_str = f"{planet.house}宮" if language == "zh" else f"H{planet.house}"
        
        # 星座
        sign_names = [
            "白羊", "金牛", "雙子", "巨蟹", "獅子", "處女",
            "天秤", "天蠍", "射手", "摩羯", "水瓶", "雙魚"
        ] if language == "zh" else [
            "Ari", "Tau", "Gem", "Can", "Leo", "Vir",
            "Lib", "Sco", "Sag", "Cap", "Aqr", "Pis"
        ]
        sign_str = f"{sign_names[planet.sign]} {planet.sign_degree:.1f}°"
        
        # 宿名
        nakshatra_str = f"{planet.nakshatra_cn}({planet.nakshatra})" if language == "zh" else planet.nakshatra
        pada_str = f"P{planet.nakshatra_pada}"
        
        # 主星
        rasi_lord_str = _translate_planet(planet.rasi_lord, language)
        star_lord_str = _translate_planet(planet.star_lord, language)
        sub_lord_str = _translate_planet(planet.sub_lord, language)
        sub_sub_lord_str = _translate_planet(planet.sub_sub_lord, language)
        
        table_data.append({
            "行星": f"{planet_name}{retro}",
            "經度": f"{planet.longitude:.2f}°",
            "星座": sign_str,
            "宮位": house_str,
            "宿": f"{nakshatra_str}\n{pada_str}",
            "星座主": rasi_lord_str,
            "宿度主": star_lord_str,
            "分主": sub_lord_str,
            "細分主": sub_sub_lord_str,
        })
    
    # 顯示表格
    st.dataframe(
        table_data,
        width="stretch",
        hide_index=True,
        column_config={
            "行星": st.column_config.TextColumn("行星", width="small"),
            "經度": st.column_config.TextColumn("經度", width="small"),
            "星座": st.column_config.TextColumn("星座", width="small"),
            "宮位": st.column_config.TextColumn("宮位", width="small"),
            "宿": st.column_config.TextColumn("宿", width="small"),
            "星座主": st.column_config.TextColumn("星座主", width="small"),
            "宿度主": st.column_config.TextColumn("宿度主", width="small"),
            "分主": st.column_config.TextColumn("分主", width="small"),
            "細分主": st.column_config.TextColumn("細分主", width="small"),
        }
    )
    
    # 圖例說明
    with st.expander("📖 KP 主星系統說明", expanded=False):
        st.markdown("""
        ### KP 主星系統（Lordship System）
        
        **Rasi Lord（星座主）**：行星所在星座的守護星
        - 決定事件的「性質」
        
        **Star Lord（宿度主）**：行星所在 Nakshatra 的守護星
        - 顯示事件的「來源」
        
        **Sub Lord（分主）**：行星所在 Sub 的守護星
        - **最重要**：決定事件「是否成立」
        
        **Sub-Sub Lord（細分主）**：更精細的時間劃分
        - 用於精確應期判斷
        
        ### 判讀鐵律
        > Sub Lord 指向的宮位決定事件結果
        > - 指向 1/5/9/10/11 宮 → 成功
        > - 指向 6/8/12 宮 → 失敗/阻礙
        """)


# ============================================================================
# CUSP TABLE
# ============================================================================

def _render_cusp_table(
    cusps: List[KPCusp],
    house_lords: Dict[int, str],
    language: str = "zh",
) -> None:
    """
    渲染 12 宮頭表格
    
    Parameters
    ----------
    cusps : List[KPCusp]
        12 宮頭列表
    house_lords : Dict[int, str]
        宮主星字典
    language : str
        語言
    """
    st.subheader("🏠 宮頭 (House Cusps)")
    
    table_data = []
    
    for cusp in cusps:
        # 宮位名稱
        if language == "zh":
            house_name = HOUSES[cusp.house_number]["cn"]
        else:
            house_name = HOUSES[cusp.house_number]["en"]
        
        house_str = f"{cusp.house_number}.{house_name}"
        
        # 星座
        sign_names = [
            "白羊", "金牛", "雙子", "巨蟹", "獅子", "處女",
            "天秤", "天蠍", "射手", "摩羯", "水瓶", "雙魚"
        ] if language == "zh" else [
            "Ari", "Tau", "Gem", "Can", "Leo", "Vir",
            "Lib", "Sco", "Sag", "Cap", "Aqr", "Pis"
        ]
        sign_str = f"{sign_names[cusp.sign]} {cusp.sign_degree:.1f}°"
        
        # 宿名
        nakshatra_str = f"{cusp.nakshatra_cn}({cusp.nakshatra})" if language == "zh" else cusp.nakshatra
        pada_str = f"P{cusp.nakshatra_pada}"
        
        # 主星
        rasi_lord_str = _translate_planet(cusp.rasi_lord, language)
        star_lord_str = _translate_planet(cusp.star_lord, language)
        sub_lord_str = _translate_planet(cusp.sub_lord, language)
        house_lord_str = _translate_planet(house_lords[cusp.house_number], language)
        
        table_data.append({
            "宮位": house_str,
            "經度": f"{cusp.longitude:.2f}°",
            "星座": sign_str,
            "宿": f"{nakshatra_str}\n{pada_str}",
            "宮主星": house_lord_str,
            "星座主": rasi_lord_str,
            "宿度主": star_lord_str,
            "分主": sub_lord_str,
        })
    
    # 顯示表格
    st.dataframe(
        table_data,
        width="stretch",
        hide_index=True,
    )


# ============================================================================
# RULING PLANETS
# ============================================================================

def _render_ruling_planets(
    ruling_planets: Any,
    language: str = "zh",
) -> None:
    """
    渲染 Ruling Planets（時辰主星）
    
    Parameters
    ----------
    ruling_planets : Any
        Ruling Planets 物件
    language : str
        語言
    """
    st.subheader("⏰ 時辰主星 (Ruling Planets)")
    
    # 星期
    day_names_zh = ["一", "二", "三", "四", "五", "六", "日"]
    day_names_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    if language == "zh":
        day_str = f"星期{day_names_zh[ruling_planets.day_of_week]}"
    else:
        day_str = day_names_en[ruling_planets.day_of_week]
    
    # 顯示 Ruling Planets
    rp_data = {
        "日主 (Day Lord)": _translate_planet(ruling_planets.day_lord, language),
        "月亮宿度主": _translate_planet(ruling_planets.moon_star_lord, language),
        "月亮星座主": _translate_planet(ruling_planets.moon_sign_lord, language),
        "上升宿度主": _translate_planet(ruling_planets.lagna_star_lord, language),
        "上升星座主": _translate_planet(ruling_planets.lagna_sign_lord, language),
    }
    
    # 使用 metrics 顯示
    cols = st.columns(5)
    
    for i, (key, value) in enumerate(rp_data.items()):
        with cols[i]:
            st.metric(label=key, value=value)
    
    # 詳細資訊（可折疊）
    with st.expander("📊 詳細天文數據", expanded=False):
        st.write(f"**{day_str}**")
        st.write(f"月亮經度：{ruling_planets.moon_longitude:.2f}°")
        st.write(f"上升點經度：{ruling_planets.ascendant_longitude:.2f}°")
        
        st.markdown("""
        ### Ruling Planets 應用
        
        **1. 驗證出生時間**
        - 如果命主的 Ruling Planets 與當前時辰的 Ruling Planets 一致
        - 表示出生時間準確
        
        **2. 擇時 (Muhurta)**
        - 選擇 Ruling Planets 指向吉宮的時辰
        - 避免指向 6/8/12 宮的時辰
        
        **3. 問卜 (Horary)**
        - 使用提問時的 Ruling Planets 判斷
        - Sub Lord 與 Ruling Planets 一致 → 事件成立
        """)


# ============================================================================
# AYANAMSA INFO
# ============================================================================

def _render_ayanamsa_info(ayanamsa: float) -> None:
    """
    顯示 KP Ayanamsa 資訊
    
    Parameters
    ----------
    ayanamsa : float
        KP Ayanamsa 值
    """
    st.subheader("📐 歲差 (Ayanamsa)")
    
    st.metric(
        label="KP New Ayanamsa",
        value=f"{ayanamsa:.5f}°",
        help="克里希納穆提新歲差（與 Lahiri 相差約 0°00'10\"）"
    )
    
    st.caption(f"計算基準：1900 年 1 月 1 日 12:00 GMT = 0°00'00\"")


# ============================================================================
# SIGNIFICATORS ANALYSIS
# ============================================================================

def _render_significators_analysis(
    significators: Dict[int, List[Any]],
    language: str = "zh",
) -> None:
    """
    渲染 Significators（徵兆星）分析
    
    Parameters
    ----------
    significators : Dict[int, List[Any]]
        12 宮的徵兆星字典
    language : str
        語言
    """
    st.subheader("🎯 徵兆星分析 (Significators)")
    
    # 選擇要查看的宮位
    selected_house = st.selectbox(
        "選擇宮位",
        options=range(1, 13),
        format_func=lambda x: f"{x}宮 - {HOUSES[x]['cn'] if language == 'zh' else HOUSES[x]['en']}",
    )
    
    house_significators = significators[selected_house]
    
    if not house_significators:
        st.warning("該宮位暫無徵兆星")
        return
    
    # 按強度分組
    very_strong = [s for s in house_significators if s.strength == "Very Strong"]
    strong = [s for s in house_significators if s.strength == "Strong"]
    weak = [s for s in house_significators if s.strength == "Weak"]
    
    # 顯示各強度等級
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"### 🟢 極強 ({len(very_strong)})")
        if very_strong:
            for s in very_strong:
                st.success(f"**{_translate_planet(s.planet, language)}**\n\n{s.reason}")
        else:
            st.caption("無")
    
    with col2:
        st.markdown(f"### 🟡 強 ({len(strong)})")
        if strong:
            for s in strong:
                st.info(f"**{_translate_planet(s.planet, language)}**\n\n{s.reason}")
        else:
            st.caption("無")
    
    with col3:
        st.markdown(f"### 🔵 弱 ({len(weak)})")
        if weak:
            for s in weak:
                st.warning(f"**{_translate_planet(s.planet, language)}**\n\n{s.reason}")
        else:
            st.caption("無")
    
    # 解讀說明
    with st.expander("📖 Significators 解讀指南", expanded=False):
        st.markdown("""
        ### 徵兆星強度等級
        
        **Very Strong（極強）**
        - 行星位於該宮
        - 直接主宰該宮
        
        **Strong（強）**
        - 行星的 Star Lord 主宰該宮
        - 行星的 Sub Lord 主宰該宮
        
        **Weak（弱）**
        - 行星與該宮主星同星座
        - 行星與該宮有相位
        
        ### 應用
        
        1. **事件判斷**：查看事件相關宮位的 Significators
        2. **時辰選擇**：選擇 Significators 強的時辰
        3. **應期推斷**：結合 Dasha/Bhukti/Antara
        """)


# ============================================================================
# HORARY INTERFACE
# ============================================================================

def render_horary_interface() -> Optional[Dict]:
    """
    渲染 Horary（問卜）輸入界面
    
    Returns
    -------
    Optional[Dict]
        提問時間資料字典，如果未提交則返回 None
    """
    st.subheader("🔮 KP 問卜 (Horary Astrology)")
    
    st.markdown("""
    **問卜占星術** — 通過提問時刻的星盤來解答問題
    
    KP 問卜系統被認為是最精確的占卜方法之一，
    關鍵在於 **Ruling Planets** 和 **Sub Lord** 的判斷。
    """)
    
    with st.form("horary_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            question_date = st.date_input("提問日期")
            question_time = st.time_input("提問時間")
        
        with col2:
            question_city = st.text_input("提問城市（可選）", placeholder="例如：Taipei")
            question_lat = st.number_input("緯度", value=25.0, step=0.1)
            question_lon = st.number_input("經度", value=121.5, step=0.1)
            question_tz = st.number_input("時區", value=8.0, step=0.5)
        
        question_text = st.text_area(
            "您的問題",
            placeholder="請清晰、具體地提出您的問題...",
            help="問題越具體，答案越準確。避免假設性問題。"
        )
        
        submitted = st.form_submit_button("🔮 開始問卜", width="stretch")
        
        if submitted:
            # 解析時間
            question_datetime = {
                "year": question_date.year,
                "month": question_date.month,
                "day": question_date.day,
                "hour": question_time.hour,
                "minute": question_time.minute,
                "latitude": question_lat,
                "longitude": question_lon,
                "timezone": question_tz,
                "question_text": question_text,
            }
            
            return question_datetime
    
    return None


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _translate_planet(planet: str, language: str) -> str:
    """
    翻譯行星名稱
    
    Parameters
    ----------
    planet : str
        行星英文名稱
    language : str
        語言
    
    Returns
    -------
    str
        翻譯後的名稱
    """
    if language == "zh":
        translations = {
            "Sun": "太陽",
            "Moon": "月亮",
            "Mars": "火星",
            "Mercury": "水星",
            "Jupiter": "木星",
            "Venus": "金星",
            "Saturn": "土星",
            "Rahu": "羅睺",
            "Ketu": "計都",
        }
        return translations.get(planet, planet)
    else:
        return planet


def _get_planet_color(planet: str) -> str:
    """
    獲取行星的 KP 專用顏色
    
    Parameters
    ----------
    planet : str
        行星名稱
    
    Returns
    -------
    str
        顏色代碼
    """
    color_map = {
        "Sun": KP_COLORS["planet_sun"],
        "Moon": KP_COLORS["planet_moon"],
        "Mars": KP_COLORS["planet_mars"],
        "Mercury": KP_COLORS["planet_mercury"],
        "Jupiter": KP_COLORS["planet_jupiter"],
        "Venus": KP_COLORS["planet_venus"],
        "Saturn": KP_COLORS["planet_saturn"],
        "Rahu": KP_COLORS["planet_rahu"],
        "Ketu": KP_COLORS["planet_ketu"],
    }
    return color_map.get(planet, KP_COLORS["text"])
