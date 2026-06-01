"""
Decanic Astrology 計算與渲染模組 (Decanic Astrology Computation & Rendering Module)

基於古埃及三十六十度區間 (36 Decans) 系統，結合迦勒底行星序 (Chaldean Order)、
三分主星 (Triplicity Rulers)、金色黎明塔羅對應 (Golden Dawn Tarot Correspondences)
以及本質尊貴 (Essential Dignities) 技法，提供出生圖 Decan 分析。

Sources: Neugebauer & Parker "Egyptian Astronomical Texts",
         Dendera zodiac ceiling, Ptolemy "Tetrabiblos",
         Golden Dawn tradition.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field

import swisseph as swe
import streamlit as st
import plotly.graph_objects as go

from .decans_data import (
    DECANS_DATA,
    ZODIAC_SIGNS_DECAN,
    CHALDEAN_ORDER,
    CHALDEAN_ORDER_CN,
    CHALDEAN_ORDER_GLYPHS,
    ESSENTIAL_DIGNITIES,
    FACE_DIGNITY_SCORE,
    get_decan_by_longitude,
    get_decan_by_sign_and_degree,
)

# ============================================================
# 常量 (Constants)
# ============================================================

# 古典七星 + 現代三星 (Classical 7 + modern outer planets)
DECAN_PLANETS = {
    "Sun ☉": swe.SUN,
    "Moon ☽": swe.MOON,
    "Mercury ☿": swe.MERCURY,
    "Venus ♀": swe.VENUS,
    "Mars ♂": swe.MARS,
    "Jupiter ♃": swe.JUPITER,
    "Saturn ♄": swe.SATURN,
    "Uranus ♅": swe.URANUS,
    "Neptune ♆": swe.NEPTUNE,
    "Pluto ♇": swe.PLUTO,
}

# 行星英文短名映射 (planet display name -> bare English name for dignity lookups)
_PLANET_SHORT = {
    "Sun ☉": "Sun",
    "Moon ☽": "Moon",
    "Mercury ☿": "Mercury",
    "Venus ♀": "Venus",
    "Mars ♂": "Mars",
    "Jupiter ♃": "Jupiter",
    "Saturn ♄": "Saturn",
    "Uranus ♅": "Uranus",
    "Neptune ♆": "Neptune",
    "Pluto ♇": "Pluto",
}

# 埃及主題色彩 (Egyptian-themed colour palette)
EGYPTIAN_GOLD = "#C5A03F"
EGYPTIAN_BLUE = "#1B2A4A"
EGYPTIAN_TURQUOISE = "#40E0D0"
EGYPTIAN_PAPYRUS = "#F5E6C8"

# 元素對應花色 (Element -> Tarot suit)
ELEMENT_SUIT = {
    "Fire": ("Wands", "權杖"),
    "Water": ("Cups", "聖杯"),
    "Air": ("Swords", "寶劍"),
    "Earth": ("Pentacles", "錢幣"),
}

# ============================================================
# 資料類 (Data Classes)
# ============================================================


@dataclass
class DecanPlanetInfo:
    """A planet's decan placement (行星 Decan 位置)"""
    planet_name: str       # e.g. "Sun ☉"
    longitude: float
    sign_en: str
    sign_cn: str
    sign_glyph: str
    degree_in_sign: float
    decan_number: int
    decan_data: dict       # reference to the DECANS_DATA entry
    chaldean_ruler: str
    triplicity_ruler: str
    face_dignity: bool     # True if planet rules this Face
    retrograde: bool


@dataclass
class DecanChart:
    """Complete Decan chart (完整 Decan 排盤)"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location_name: str
    planets: list          # list of DecanPlanetInfo
    ascendant_decan: dict  # DECANS_DATA entry for ASC
    asc_longitude: float
    today_sun_decan: dict  # today's Sun decan
    today_sun_longitude: float
    essential_dignities_summary: list = field(default_factory=list)


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _normalize(deg: float) -> float:
    return deg % 360.0


def _sign_index(deg: float) -> int:
    return int(_normalize(deg) / 30.0)


def _degree_in_sign(deg: float) -> float:
    return _normalize(deg) % 30.0


def _format_deg(deg: float) -> str:
    deg = _normalize(deg)
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""


def _check_face_dignity(planet_name: str, decan_data: dict) -> bool:
    """行星是否位於自己的 Face (Chaldean ruler == planet)"""
    short = _PLANET_SHORT.get(planet_name, planet_name.split(" ")[0])
    return decan_data["chaldean_ruler_en"] == short


def _build_dignity_row(planet_name: str, sign_idx: int, decan_data: dict) -> dict:
    """為一顆行星建立本質尊貴摘要行"""
    short = _PLANET_SHORT.get(planet_name, planet_name.split(" ")[0])
    dig = ESSENTIAL_DIGNITIES.get(sign_idx, {})

    domicile = (dig.get("domicile") == short)
    exaltation = (dig.get("exaltation") == short)
    detriment = (dig.get("detriment") == short)
    fall = (dig.get("fall") == short)
    triplicity_day = (dig.get("triplicity_day") == short)
    triplicity_night = (dig.get("triplicity_night") == short)
    face = (decan_data["chaldean_ruler_en"] == short)

    score = 0
    if domicile:
        score += 5
    if exaltation:
        score += 4
    if triplicity_day or triplicity_night:
        score += 3
    if face:
        score += FACE_DIGNITY_SCORE
    if detriment:
        score -= 5
    if fall:
        score -= 4

    return {
        "planet": planet_name,
        "domicile": domicile,
        "exaltation": exaltation,
        "detriment": detriment,
        "fall": fall,
        "triplicity_day": triplicity_day,
        "triplicity_night": triplicity_night,
        "face": face,
        "score": score,
    }


# ============================================================
# 計算函數 (Computation Function)
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_decan_chart(year, month, day, hour, minute, timezone,
                        latitude, longitude, location_name="", **kwargs):
    """計算 Decan 排盤

    Args:
        year, month, day, hour, minute: 出生日期時間
        timezone: UTC 時差 (e.g. +8 for CST)
        latitude, longitude: 出生地座標
        location_name: 地點名稱
        **kwargs: 保留給未來擴展
    Returns:
        DecanChart 資料類實例
    """
    swe.set_ephe_path("")

    # Julian day
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)

    # Ascendant
    cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")
    asc = _normalize(ascmc[0])
    asc_decan = get_decan_by_longitude(asc)

    # 行星計算
    planets: list[DecanPlanetInfo] = []
    for name, planet_id in DECAN_PLANETS.items():
        pos, _ = swe.calc_ut(jd, planet_id)
        lon = _normalize(pos[0])
        speed = pos[3]
        sidx = _sign_index(lon)
        deg_in = _degree_in_sign(lon)
        decan = get_decan_by_longitude(lon)
        sign_info = ZODIAC_SIGNS_DECAN[sidx]

        planets.append(DecanPlanetInfo(
            planet_name=name,
            longitude=lon,
            sign_en=sign_info[0],
            sign_cn=sign_info[1],
            sign_glyph=sign_info[2],
            degree_in_sign=deg_in,
            decan_number=decan["decan_number"],
            decan_data=decan,
            chaldean_ruler=decan["chaldean_ruler_en"],
            triplicity_ruler=decan["triplicity_ruler_en"],
            face_dignity=_check_face_dignity(name, decan),
            retrograde=(speed < 0),
        ))

    # 今日太陽 Decan
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    now_jd = swe.julday(now.year, now.month, now.day,
                        now.hour + now.minute / 60.0)
    sun_now, _ = swe.calc_ut(now_jd, swe.SUN)
    today_sun_lon = _normalize(sun_now[0])
    today_sun_decan = get_decan_by_longitude(today_sun_lon)

    # 本質尊貴摘要
    dignities: list[dict] = []
    for p in planets:
        sidx = _sign_index(p.longitude)
        dignities.append(_build_dignity_row(p.planet_name, sidx, p.decan_data))

    return DecanChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        location_name=location_name,
        planets=planets,
        ascendant_decan=asc_decan,
        asc_longitude=asc,
        today_sun_decan=today_sun_decan,
        today_sun_longitude=today_sun_lon,
        essential_dignities_summary=dignities,
    )


# ============================================================
# 渲染：CSS 樣式 (Rendering: CSS Styles)
# ============================================================

_EGYPTIAN_CSS = f"""
<style>
.decan-card {{
    background: linear-gradient(135deg, {EGYPTIAN_BLUE} 0%, #2a3d5a 100%);
    border: 1px solid {EGYPTIAN_GOLD};
    border-radius: 8px;
    padding: 12px;
    margin: 4px 0;
    color: {EGYPTIAN_PAPYRUS};
}}
.decan-card h4 {{
    color: {EGYPTIAN_GOLD};
    margin: 0 0 6px 0;
}}
.decan-card .meta {{
    font-size: 0.85em;
    opacity: 0.9;
}}
.decan-highlight {{
    border: 2px solid {EGYPTIAN_TURQUOISE};
    box-shadow: 0 0 8px {EGYPTIAN_TURQUOISE}44;
}}
.decan-today {{
    background: linear-gradient(135deg, #2a3d1a 0%, #1a2a0a 100%);
    border: 2px solid {EGYPTIAN_GOLD};
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
    color: {EGYPTIAN_PAPYRUS};
}}
.decan-today h3 {{
    color: {EGYPTIAN_GOLD};
    margin: 0 0 8px 0;
}}
.color-swatch {{
    display: inline-block;
    width: 16px; height: 16px;
    border-radius: 3px;
    border: 1px solid #888;
    vertical-align: middle;
    margin-right: 4px;
}}
</style>
"""


# ============================================================
# 渲染：Plotly 輪圖 (Rendering: Plotly Wheel Chart)
# ============================================================

def _render_decan_wheel(highlight_index: int | None = None):
    """繪製三十六 Decan 甜甜圈輪圖"""
    labels = []
    colors = []
    hover_texts = []
    pulls = []
    for d in DECANS_DATA:
        lbl = f"{d['sign_glyph']} {d['decan_number']}"
        labels.append(lbl)
        colors.append(d["color"])
        hover_texts.append(
            f"{d['sign_en']} ({d['sign_cn']}) Decan {d['decan_number']}<br>"
            f"{d['degree_start']}°–{d['degree_end']}°<br>"
            f"Egyptian: {d['egyptian_hieroglyphic']} {d['egyptian_name']}"
            f" ({d['egyptian_transliteration']})<br>"
            f"Deity: {d['egyptian_deity']}<br>"
            f"Chaldean Ruler: {d['chaldean_ruler_en']} {d['chaldean_ruler_glyph']}"
        )
        pulls.append(0.06 if d["index"] == highlight_index else 0)

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=[1] * 36,
        hole=0.45,
        marker=dict(colors=colors, line=dict(color=EGYPTIAN_GOLD, width=1)),
        textinfo="label",
        textfont=dict(size=10, color=EGYPTIAN_PAPYRUS),
        hovertext=hover_texts,
        hoverinfo="text",
        pull=pulls,
        direction="clockwise",
        sort=False,
    )])
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        height=480,
        title=dict(
            text="𓂀 Dendera Decan Wheel — 丹德拉十度區間輪",
            font=dict(color=EGYPTIAN_GOLD, size=14),
        ),
        annotations=[dict(
            text="36<br>Decans",
            x=0.5, y=0.5,
            font=dict(size=16, color=EGYPTIAN_GOLD),
            showarrow=False,
        )],
    )
    st.plotly_chart(fig, width='stretch')


# ============================================================
# 渲染：今日 Decan 卡片 (Today's Decan Card)
# ============================================================

def _render_today_card(sun_lon: float, decan: dict, lang: str = "cn"):
    """顯示今日太陽 Decan 卡片"""
    deg_str = f"{sun_lon:.2f}°"
    if lang == "cn":
        sign = decan["sign_cn"]
        ruler = f"{decan['chaldean_ruler_cn']} {decan['chaldean_ruler_glyph']}"
        trip = decan["triplicity_ruler_cn"]
        personality = decan["personality_cn"]
    else:
        sign = decan["sign_en"]
        ruler = f"{decan['chaldean_ruler_en']} {decan['chaldean_ruler_glyph']}"
        trip = decan["triplicity_ruler_en"]
        personality = decan["personality_en"]

    html = f"""
    <div class="decan-today">
        <h3>☀️ {"今日 Decan" if lang == "cn" else "Today's Decan"}
            — {decan['sign_glyph']} {sign} Decan {decan['decan_number']}</h3>
        <p><b>{"太陽經度" if lang == "cn" else "Sun Longitude"}:</b> {deg_str} &nbsp;
           <b>{"度數範圍" if lang == "cn" else "Degree Range"}:</b>
           {decan['degree_start']}°–{decan['degree_end']}°</p>
        <p><b>{"迦勒底主星" if lang == "cn" else "Chaldean Ruler"}:</b> {ruler} &nbsp;
           <b>{"三分主星" if lang == "cn" else "Triplicity Ruler"}:</b> {trip}</p>
        <p><b>{"埃及名稱" if lang == "cn" else "Egyptian Name"}:</b>
           <span style="font-size:1.3em;">{decan['egyptian_hieroglyphic']}</span>
           {decan['egyptian_name']} ({decan['egyptian_transliteration']})
           &nbsp; <b>{"守護神" if lang == "cn" else "Deity"}:</b> {decan['egyptian_deity']}</p>
        <p><b>{"塔羅" if lang == "cn" else "Tarot"}:</b>
           {decan['tarot_card_cn'] if lang == "cn" else decan['tarot_card_en']}</p>
        <p style="font-style:italic; opacity:0.9;">{personality}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# 渲染：Decan 網格 (Decan Grid)
# ============================================================

def _render_decan_grid(lang: str = "cn", highlight_index: int | None = None):
    """以 3 欄網格顯示全部 36 Decans"""
    cols_per_row = 3
    for i in range(0, 36, cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= 36:
                break
            d = DECANS_DATA[idx]
            hl_class = " decan-highlight" if d["index"] == highlight_index else ""
            if lang == "cn":
                sign = d["sign_cn"]
                ruler = f"{d['chaldean_ruler_cn']} {d['chaldean_ruler_glyph']}"
                trip = d["triplicity_ruler_cn"]
                tarot = d["tarot_card_cn"]
            else:
                sign = d["sign_en"]
                ruler = f"{d['chaldean_ruler_en']} {d['chaldean_ruler_glyph']}"
                trip = d["triplicity_ruler_en"]
                tarot = d["tarot_card_en"]

            card_html = f"""
            <div class="decan-card{hl_class}">
                <h4>{d['sign_glyph']} {sign} — Decan {d['decan_number']}</h4>
                <div class="meta">
                    {d['degree_start']}°–{d['degree_end']}° &nbsp;
                    <span class="color-swatch" style="background:{d['color']};"></span>
                    {d['color']}<br/>
                    <b>{"迦勒底" if lang == "cn" else "Chaldean"}:</b> {ruler}<br/>
                    <b>{"三分" if lang == "cn" else "Triplicity"}:</b> {trip}<br/>
                    <b>{"埃及" if lang == "cn" else "Egyptian"}:</b>
                    <span style="font-size:1.2em;">{d['egyptian_hieroglyphic']}</span>
                    {d['egyptian_name']} ({d['egyptian_transliteration']})
                    · {d['egyptian_deity']}<br/>
                    <b>{"礦石" if lang == "cn" else "Mineral"}:</b> {d['mineral']}
                    &nbsp; <b>{"植物" if lang == "cn" else "Plant"}:</b> {d['plant']}<br/>
                    <b>{"塔羅" if lang == "cn" else "Tarot"}:</b> {tarot}
                </div>
            </div>
            """
            with col:
                st.markdown(card_html, unsafe_allow_html=True)
                hist_label = (
                    f"📜 {d['sign_glyph']} {sign} D{d['decan_number']} "
                    f"{'歷史' if lang == 'cn' else 'History'}"
                )
                with st.expander(hist_label):
                    if lang == "cn":
                        st.write(d["history_cn"])
                        st.write(f"**性格：** {d['personality_cn']}")
                        st.write(f"**優勢：** {d['strengths_cn']}")
                        st.write(f"**挑戰：** {d['challenges_cn']}")
                    else:
                        st.write(d["history_en"])
                        st.write(f"**Personality:** {d['personality_en']}")
                        st.write(f"**Strengths:** {d['strengths_en']}")
                        st.write(f"**Challenges:** {d['challenges_en']}")


# ============================================================
# 渲染：行星 Decan 表格 (Planet Decan Table)
# ============================================================

def _render_planet_table(chart: DecanChart, ruler_system: str, lang: str = "cn"):
    """渲染行星 Decan 位置表"""
    if lang == "cn":
        st.subheader("🪐 行星 Decan 位置")
        hdr = (
            "| 行星 | 經度 | 星座 | Decan | "
            f"{'迦勒底主星' if ruler_system == 'Chaldean' else '三分主星'} | "
            "Face 尊貴 | 塔羅牌 |"
        )
    else:
        st.subheader("🪐 Planet Decan Positions")
        hdr = (
            "| Planet | Longitude | Sign | Decan | "
            f"{'Chaldean Ruler' if ruler_system == 'Chaldean' else 'Triplicity Ruler'} | "
            "Face Dignity | Tarot Card |"
        )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [hdr, sep]

    for p in chart.planets:
        retro = " ℞" if p.retrograde else ""
        face_str = f"✦ +{FACE_DIGNITY_SCORE}" if p.face_dignity else "—"
        if ruler_system == "Chaldean":
            ruler = (p.decan_data["chaldean_ruler_cn"] if lang == "cn"
                     else p.decan_data["chaldean_ruler_en"])
            ruler += f" {p.decan_data['chaldean_ruler_glyph']}"
        else:
            ruler = (p.decan_data["triplicity_ruler_cn"] if lang == "cn"
                     else p.decan_data["triplicity_ruler_en"])

        sign = p.sign_cn if lang == "cn" else p.sign_en
        tarot = (p.decan_data["tarot_card_cn"] if lang == "cn"
                 else p.decan_data["tarot_card_en"])

        rows.append(
            f"| {p.planet_name}{retro} "
            f"| {p.longitude:.2f}° "
            f"| {p.sign_glyph} {sign} {p.degree_in_sign:.1f}° "
            f"| {p.decan_number} "
            f"| {ruler} "
            f"| {face_str} "
            f"| {tarot} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


# ============================================================
# 渲染：上升 Decan 卡片 (Ascendant Decan Card)
# ============================================================

def _render_ascendant_card(chart: DecanChart, lang: str = "cn"):
    """顯示上升點 Decan 資訊卡"""
    d = chart.ascendant_decan
    deg_str = f"{chart.asc_longitude:.2f}°"
    if lang == "cn":
        st.subheader("🔺 上升 Decan")
        sign = d["sign_cn"]
        ruler = f"{d['chaldean_ruler_cn']} {d['chaldean_ruler_glyph']}"
        personality = d["personality_cn"]
    else:
        st.subheader("🔺 Ascendant Decan")
        sign = d["sign_en"]
        ruler = f"{d['chaldean_ruler_en']} {d['chaldean_ruler_glyph']}"
        personality = d["personality_en"]

    html = f"""
    <div class="decan-card decan-highlight">
        <h4>{d['sign_glyph']} {sign} — Decan {d['decan_number']}</h4>
        <div class="meta">
            <b>ASC:</b> {deg_str} &nbsp;
            <b>{"迦勒底主星" if lang == "cn" else "Chaldean Ruler"}:</b> {ruler}<br/>
            <b>{"埃及" if lang == "cn" else "Egyptian"}:</b>
            <span style="font-size:1.2em;">{d['egyptian_hieroglyphic']}</span>
            {d['egyptian_name']} ({d['egyptian_transliteration']})
            · {d['egyptian_deity']}<br/>
            <b>{"塔羅" if lang == "cn" else "Tarot"}:</b>
            {d['tarot_card_cn'] if lang == "cn" else d['tarot_card_en']}<br/>
            <p style="font-style:italic; margin-top:6px;">{personality}</p>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# 渲染：本質尊貴摘要 (Essential Dignities Summary)
# ============================================================

def _render_dignities_table(chart: DecanChart, lang: str = "cn"):
    """渲染本質尊貴分數表"""
    if lang == "cn":
        st.subheader("🏛️ 本質尊貴摘要 (Essential Dignities)")
        hdr = "| 行星 | 入廟 | 入旺 | 落陷 | 入弱 | 日三分 | 夜三分 | Face | 總分 |"
    else:
        st.subheader("🏛️ Essential Dignities Summary")
        hdr = "| Planet | Domicile | Exaltation | Detriment | Fall | Trip Day | Trip Night | Face | Score |"
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [hdr, sep]

    def yn(v):
        return "✓" if v else "—"

    for row in chart.essential_dignities_summary:
        rows.append(
            f"| {row['planet']} "
            f"| {yn(row['domicile'])} "
            f"| {yn(row['exaltation'])} "
            f"| {yn(row['detriment'])} "
            f"| {yn(row['fall'])} "
            f"| {yn(row['triplicity_day'])} "
            f"| {yn(row['triplicity_night'])} "
            f"| {yn(row['face'])} "
            f"| **{row['score']:+d}** |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


# ============================================================
# 渲染：日月 Decan 性格解讀 (Sun & Moon Decan Personality)
# ============================================================

def _render_personality(chart: DecanChart, lang: str = "cn"):
    """顯示太陽與月亮 Decan 性格解讀"""
    if lang == "cn":
        st.subheader("🌟 日月 Decan 性格解讀")
    else:
        st.subheader("🌟 Sun & Moon Decan Personality")

    for p in chart.planets:
        if p.planet_name not in ("Sun ☉", "Moon ☽"):
            continue
        d = p.decan_data
        if lang == "cn":
            label = "太陽" if "Sun" in p.planet_name else "月亮"
            sign = d["sign_cn"]
            personality = d["personality_cn"]
            strengths = d["strengths_cn"]
            challenges = d["challenges_cn"]
        else:
            label = "Sun" if "Sun" in p.planet_name else "Moon"
            sign = d["sign_en"]
            personality = d["personality_en"]
            strengths = d["strengths_en"]
            challenges = d["challenges_en"]

        html = f"""
        <div class="decan-card">
            <h4>{p.planet_name} — {d['sign_glyph']} {sign} Decan {d['decan_number']}</h4>
            <div class="meta">
                <p>{personality}</p>
                <p><b>{"優勢" if lang == "cn" else "Strengths"}:</b> {strengths}</p>
                <p><b>{"挑戰" if lang == "cn" else "Challenges"}:</b> {challenges}</p>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)


# ============================================================
# 渲染：塔羅對應 (Tarot Correspondences)
# ============================================================

def _render_tarot_tab(chart: DecanChart | None, lang: str = "cn"):
    """顯示 36 Decans 與小阿爾卡那塔羅牌對應"""
    if lang == "cn":
        st.subheader("🃏 Decan 塔羅對應 (Minor Arcana)")
    else:
        st.subheader("🃏 Decan ↔ Tarot Minor Arcana")

    # Build set of decan indices where user has planets
    user_indices: set[int] = set()
    if chart is not None:
        for p in chart.planets:
            user_indices.add(p.decan_data["index"])

    for element, (suit_en, suit_cn) in ELEMENT_SUIT.items():
        suit_label = suit_cn if lang == "cn" else suit_en
        st.markdown(f"#### {suit_label} ({element})")
        matching = [d for d in DECANS_DATA if d["element"] == element]
        cols = st.columns(min(len(matching), 3))
        for i, d in enumerate(matching):
            col = cols[i % 3]
            hl_class = " decan-highlight" if d["index"] in user_indices else ""
            if lang == "cn":
                sign = d["sign_cn"]
                tarot = d["tarot_card_cn"]
                ruler = f"{d['chaldean_ruler_cn']} {d['chaldean_ruler_glyph']}"
            else:
                sign = d["sign_en"]
                tarot = d["tarot_card_en"]
                ruler = f"{d['chaldean_ruler_en']} {d['chaldean_ruler_glyph']}"

            # Show which planets the user has in this decan
            planet_badges = ""
            if chart is not None:
                in_this = [p.planet_name for p in chart.planets
                           if p.decan_data["index"] == d["index"]]
                if in_this:
                    planet_badges = (
                        "<br/><b>"
                        + ("你的行星" if lang == "cn" else "Your planets")
                        + ":</b> " + ", ".join(in_this)
                    )

            card_html = f"""
            <div class="decan-card{hl_class}">
                <h4>🃏 {tarot}</h4>
                <div class="meta">
                    {d['sign_glyph']} {sign} Decan {d['decan_number']}<br/>
                    {d['degree_start']}°–{d['degree_end']}°<br/>
                    <b>{"主星" if lang == "cn" else "Ruler"}:</b> {ruler}
                    {planet_badges}
                </div>
            </div>
            """
            with col:
                st.markdown(card_html, unsafe_allow_html=True)


# ============================================================
# 渲染：文化尊重聲明 (Cultural Respect Footer)
# ============================================================

def _render_footer(lang: str = "cn"):
    st.divider()
    if lang == "cn":
        st.caption(
            "𓂀 本模組所呈現之古埃及 Decan 資料係基於學術文獻（Neugebauer & Parker、"
            "丹德拉黃道天花板）進行彙整，旨在教育與文化傳承。"
            "我們尊重古埃及文明的歷史遺產，使用資料時請懷抱敬意。"
        )
    else:
        st.caption(
            "𓂀 The ancient Egyptian Decan data presented here is compiled from academic "
            "sources (Neugebauer & Parker, Dendera Zodiac ceiling) for educational and "
            "cultural purposes. We respect the heritage of ancient Egyptian civilisation "
            "and encourage respectful engagement with this material."
        )


# ============================================================
# 公開渲染函數：完整排盤 (Public: Full Chart Rendering)
# ============================================================

def render_decan_chart(chart: DecanChart, lang: str = "cn"):
    """渲染完整 Decan 排盤 UI（含三個子分頁）"""
    st.markdown(_EGYPTIAN_CSS, unsafe_allow_html=True)

    tab_labels = (
        ["古埃及 Decans 瀏覽", "個人出生圖 Decan 計算", "塔羅連結"]
        if lang == "cn"
        else ["Browse Ancient Egyptian Decans", "Birth Chart Decan Analysis",
              "Tarot Correspondences"]
    )
    tab_browse, tab_birth, tab_tarot = st.tabs(tab_labels)

    # --------------------------------------------------
    # Sub-tab 1: Browse Decans
    # --------------------------------------------------
    with tab_browse:
        _render_today_card(chart.today_sun_longitude, chart.today_sun_decan, lang)
        _render_decan_wheel(highlight_index=chart.today_sun_decan["index"])
        _render_decan_grid(lang=lang,
                           highlight_index=chart.today_sun_decan["index"])

    # --------------------------------------------------
    # Sub-tab 2: Birth Chart Analysis
    # --------------------------------------------------
    with tab_birth:
        ruler_system = st.radio(
            "⚙️ " + ("主星系統" if lang == "cn" else "Ruler System"),
            ["Chaldean", "Triplicity"],
            horizontal=True,
            key="decan_ruler_system",
        )
        _render_planet_table(chart, ruler_system, lang)
        st.divider()
        _render_ascendant_card(chart, lang)
        st.divider()
        _render_dignities_table(chart, lang)
        st.divider()
        _render_personality(chart, lang)

    # --------------------------------------------------
    # Sub-tab 3: Tarot Correspondences
    # --------------------------------------------------
    with tab_tarot:
        _render_tarot_tab(chart, lang)

    _render_footer(lang)


# ============================================================
# 公開渲染函數：獨立瀏覽模式 (Public: Standalone Browse)
# ============================================================

def render_decan_browse(lang: str = "cn"):
    """渲染 Decan 瀏覽器（不需要出生資料）"""
    st.markdown(_EGYPTIAN_CSS, unsafe_allow_html=True)

    # 計算今日太陽位置
    swe.set_ephe_path("")
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    now_jd = swe.julday(now.year, now.month, now.day,
                        now.hour + now.minute / 60.0)
    sun_now, _ = swe.calc_ut(now_jd, swe.SUN)
    today_sun_lon = _normalize(sun_now[0])
    today_sun_decan = get_decan_by_longitude(today_sun_lon)

    _render_today_card(today_sun_lon, today_sun_decan, lang)
    _render_decan_wheel(highlight_index=today_sun_decan["index"])
    _render_decan_grid(lang=lang, highlight_index=today_sun_decan["index"])
    _render_footer(lang)
