"""
astro/astronomical_geomancy/renderer.py
══════════════════════════════════════════════════════════════
Streamlit renderer for Astronomical Geomancy (地占占星).

Renders:
  - Input panel (question, question type, seed mode)
  - 12-house wheel SVG / visual chart
  - Mother figures panel
  - Planet placements table
  - House-by-house interpretation
  - AI reading button hook

IMPORTANT: Streamlit is imported only inside function bodies,
per CONTRIBUTING.md convention.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Optional

from .constants import (
    DOT_DOUBLE,
    DOT_SINGLE,
    GEOMANCY_THEME,
    QUESTION_TYPES,
    SYSTEM_NAME_EN,
    SYSTEM_NAME_ZH,
    ZODIAC_SIGNS,
)
from .models import GeomancyChart, GeomancyFigure, HouseInfo
from .chart_renderer_geomancy import render_geomancy_svg_chart, build_square_chart_svg
from .geomancy_figures import get_figure_catalog


# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────

_CSS = """
<style>
.geo-header {
    background: linear-gradient(135deg,#050a14 0%,#0d1a35 50%,#050a14 100%);
    border:1px solid #C8A24A;
    border-radius:10px;
    padding:20px 28px;
    margin-bottom:16px;
    box-shadow:0 0 30px rgba(200,162,74,0.18);
}
.geo-header h2 { color:#EDD88A; margin:0; font-size:1.4rem; }
.geo-header p  { color:#B0B8C8; margin:4px 0 0; font-size:0.9rem; }

.geo-figure-card {
    background:#111827;
    border:1px solid #2A3A50;
    border-radius:8px;
    padding:14px;
    text-align:center;
}
.geo-figure-card .fig-name { color:#EDD88A; font-size:1rem; font-weight:600; }
.geo-figure-card .fig-zh   { color:#B0B8C8; font-size:0.85rem; }
.geo-figure-card .fig-dots { font-size:1.4rem; letter-spacing:4px; color:#C8A24A; font-family:monospace; }
.geo-figure-card .fig-sign { color:#7BAFD4; font-size:0.85rem; margin-top:4px; }
.geo-figure-card .fig-qual-fortunate   { color:#4CAF50; font-weight:600; }
.geo-figure-card .fig-qual-unfortunate { color:#EF5350; font-weight:600; }
.geo-figure-card .fig-qual-neutral     { color:#9E9E9E; font-weight:600; }

.geo-planet-row {
    display:flex; align-items:center; gap:10px;
    background:#111827; border:1px solid #1E2845;
    border-radius:6px; padding:8px 14px; margin:4px 0;
}
.geo-planet-glyph { font-size:1.3rem; width:30px; text-align:center; }
.geo-planet-name  { color:#EDD88A; font-size:0.95rem; min-width:80px; }
.geo-planet-house { color:#7BAFD4; font-size:0.9rem; }
.geo-planet-sign  { color:#B0B8C8; font-size:0.85rem; }

.geo-house-card {
    background:#111827;
    border:1px solid #1E2845;
    border-left:4px solid #C8A24A;
    border-radius:6px;
    padding:12px 16px;
    margin:6px 0;
}
.geo-house-title { color:#EDD88A; font-size:1rem; font-weight:600; }
.geo-house-sign  { color:#7BAFD4; font-size:0.9rem; }
.geo-house-topics{ color:#B0B8C8; font-size:0.85rem; margin-top:4px; }
.geo-house-gerard{ color:#A0907A; font-size:0.82rem; font-style:italic; margin-top:4px; }
.geo-house-planets{ color:#C8A24A; font-size:0.88rem; margin-top:4px; }
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# SVG wheel builder / 星盤輪圖
# ─────────────────────────────────────────────────────────────────────────────

def build_geomancy_wheel_svg(chart: GeomancyChart) -> str:
    """Build a classical-style astrology wheel SVG for geomantic charting."""
    cx, cy = 320, 320
    r_outer = 286
    r_sign = 250
    r_house_outer = 226
    r_house_inner = 146
    r_planet = 112
    r_hub = 70

    def _polar(radius: float, angle_deg: float) -> tuple[float, float]:
        rad = math.radians(angle_deg)
        return cx + radius * math.cos(rad), cy - radius * math.sin(rad)

    svg_parts = [
        (
            '<svg viewBox="0 0 640 640" xmlns="http://www.w3.org/2000/svg" '
            'style="max-width:560px;width:100%;display:block;margin:auto;'
            'border-radius:14px;background:#090f1f">'
        ),
        "<defs>",
        '<radialGradient id="geoSky" cx="50%" cy="45%" r="70%">'
        '<stop offset="0%" stop-color="#162744"/>'
        '<stop offset="55%" stop-color="#0e1730"/>'
        '<stop offset="100%" stop-color="#070c18"/>'
        "</radialGradient>",
        '<radialGradient id="geoInner" cx="50%" cy="50%" r="75%">'
        '<stop offset="0%" stop-color="#0f1f3b"/>'
        '<stop offset="100%" stop-color="#060b15"/>'
        "</radialGradient>",
        '<filter id="softGlow">'
        '<feGaussianBlur stdDeviation="1.4" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        "</filter>",
        "</defs>",
        '<rect x="0" y="0" width="640" height="640" fill="url(#geoSky)"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" '
        'stroke="#D3AF58" stroke-width="2.2"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_sign}" fill="none" '
        'stroke="#C8A24A" stroke-width="1"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_house_outer}" fill="none" '
        'stroke="#324565" stroke-width="1"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_house_inner}" fill="url(#geoInner)" '
        'stroke="#3D5478" stroke-width="1.1"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_planet}" fill="none" '
        'stroke="#6E87A8" stroke-width="0.9" stroke-dasharray="3 5" opacity="0.75"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_hub}" fill="#071022" '
        'stroke="#D3AF58" stroke-width="1.6"/>',
    ]

    element_colors = {
        "Fire": "#ED8479",
        "Earth": "#A3CF74",
        "Air": "#8CBFFF",
        "Water": "#7FD9DF",
    }

    for i in range(12):
        angle_deg = 180.0 - i * 30.0
        mid_angle = angle_deg - 15.0
        x1, y1 = _polar(r_house_inner, angle_deg)
        x2, y2 = _polar(r_outer, angle_deg)
        divider_color = "#D3AF58" if i == 0 else "#2B4060"
        divider_width = "2.1" if i == 0 else "1"
        svg_parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{divider_color}" stroke-width="{divider_width}"/>'
        )

        hx, hy = _polar((r_house_outer + r_house_inner) / 2, mid_angle)
        svg_parts.append(
            f'<text x="{hx:.1f}" y="{hy:.1f}" text-anchor="middle" '
            'dominant-baseline="middle" fill="#9FC2EA" font-size="13" '
            'font-family="serif" font-weight="bold">'
            f"{i + 1}</text>"
        )

        house_info = chart.houses[i]
        sx, sy = _polar(r_sign, mid_angle)
        sign_color = element_colors.get(house_info.element, "#E7CD84")
        svg_parts.append(
            f'<text x="{sx:.1f}" y="{sy:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="{sign_color}" '
            'font-size="22" font-family="Noto Sans Symbols2, serif" '
            'filter="url(#softGlow)">'
            f'{house_info.glyph}</text>'
        )

        if house_info.planets:
            shown_planets = house_info.planets[:3]
            pcount = len(shown_planets)
            for pi, planet in enumerate(shown_planets):
                offset = (pi - (pcount - 1) / 2.0) * 7.0
                px, py = _polar(r_planet - (pi * 7), mid_angle + offset)
                svg_parts.append(
                    f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" '
                    'dominant-baseline="middle" fill="#E2BC63" '
                    'font-size="15" font-family="Noto Sans Symbols2, serif">'
                    f"{planet.glyph}</text>"
                )

    ax, ay = _polar(r_outer + 16, 180.0)
    svg_parts.append(
        f'<text x="{ax:.1f}" y="{ay:.1f}" text-anchor="middle" '
        'dominant-baseline="middle" fill="#D3AF58" font-size="12" '
        'font-weight="bold" font-family="serif">ASC</text>'
    )
    svg_parts.append(
        f'<text x="{cx}" y="{cy-12}" text-anchor="middle" fill="#E9D38C" '
        f'font-size="13" font-family="serif" font-weight="bold">{SYSTEM_NAME_ZH}</text>'
    )
    svg_parts.append(
        f'<text x="{cx}" y="{cy+10}" text-anchor="middle" fill="#CCAA58" '
        f'font-size="9.5" font-family="serif">{SYSTEM_NAME_EN}</text>'
    )
    svg_parts.append(
        f'<text x="{cx}" y="{cy+30}" text-anchor="middle" fill="#AFC3DE" '
        'font-size="10" font-family="serif">'
        f"{chart.ascendant_sign_zh} {chart.houses[0].glyph}</text>"
    )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


# ─────────────────────────────────────────────────────────────────────────────
# Figure dot SVG
# ─────────────────────────────────────────────────────────────────────────────

def _figure_dots_svg(figure: GeomancyFigure, size: int = 80) -> str:
    """Render a geomantic figure as a small SVG dot pattern."""
    gold = GEOMANCY_THEME["gold"]
    bg = GEOMANCY_THEME["card"]
    row_h = size // 5
    svg = [
        f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" '
        f'xmlns="http://www.w3.org/2000/svg">',
        f'<rect width="{size}" height="{size}" rx="6" fill="{bg}"/>',
    ]
    for row_idx, single in enumerate(figure.dots):
        y = row_h * (row_idx + 1) - row_h // 4
        if single:
            # One dot, centred
            svg.append(
                f'<circle cx="{size//2}" cy="{y}" r="5" fill="{gold}"/>'
            )
        else:
            # Two dots
            svg.append(
                f'<circle cx="{size//2 - 10}" cy="{y}" r="5" fill="{gold}"/>'
            )
            svg.append(
                f'<circle cx="{size//2 + 10}" cy="{y}" r="5" fill="{gold}"/>'
            )
    svg.append("</svg>")
    return "".join(svg)


# ─────────────────────────────────────────────────────────────────────────────
# Input panel / 輸入面板
# ─────────────────────────────────────────────────────────────────────────────

def render_input_panel() -> Optional[dict]:
    """
    Render the input panel for the geomancy reading.
    Returns dict with user inputs, or None if not submitted yet.
    """
    import streamlit as st
    from astro.i18n import t, auto_cn

    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(
        f'<div class="geo-header">'
        f'<h2>🔮 {auto_cn(SYSTEM_NAME_ZH, SYSTEM_NAME_EN)}</h2>'
        f'<p>{auto_cn("Gerardus Cremonensis 地占占星系統（12世紀）", "Gerardus Cremonensis Geomantic Astrology System (12th c.)")}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.form("geo_input_form"):
        question = st.text_area(
            auto_cn("你的問題", "Your Question"),
            placeholder=auto_cn(
                "請輸入你想問的問題，例如：我今年的財運如何？",
                "Enter your question, e.g.: What is my financial fortune this year?",
            ),
            height=90,
        )

        qt_labels = [f"{q['zh']}  /  {q['en']}" for q in QUESTION_TYPES]
        qt_keys = [q["key"] for q in QUESTION_TYPES]
        qt_idx = st.selectbox(
            auto_cn("問題類型", "Question Type"),
            options=range(len(qt_labels)),
            format_func=lambda i: qt_labels[i],
        )
        question_type = qt_keys[qt_idx]

        seed_mode = st.radio(
            auto_cn("起卦模式", "Casting Mode"),
            options=["random", "time_seed"],
            format_func=lambda v: {
                "random": auto_cn("🎲 純隨機（傳統方式）", "🎲 Pure Random (Traditional)"),
                "time_seed": auto_cn("🕐 時間種子（現代增強）", "🕐 Time Seed (Modern Enhanced)"),
            }[v],
            horizontal=True,
        )

        col_m, col_l = st.columns(2)
        with col_m:
            mode = st.selectbox(
                auto_cn("起卦方式", "Casting Mode"),
                options=["horary", "natal_transcode"],
                format_func=lambda v: {
                    "horary": auto_cn("📖 卜卦地占（Horary）", "📖 Horary Geomancy"),
                    "natal_transcode": auto_cn("🌟 出生圖轉換（Natal）", "🌟 Natal Transcode"),
                }[v],
            )
        with col_l:
            layout = st.selectbox(
                auto_cn("圖盤佈局", "Chart Layout"),
                options=["square", "shield"],
                format_func=lambda v: {
                    "square": auto_cn("🗺️ 古典方形盤", "🗺️ Square Chart"),
                    "shield": auto_cn("🛡️ 盾牌盤", "🛡️ Shield Chart"),
                }[v],
            )

        submitted = st.form_submit_button(
            auto_cn("🔮 起卦占卜", "🔮 Cast the Chart"),
            use_container_width=True,
        )

    if submitted:
        return {
            "question": question.strip() or auto_cn("未提供問題", "No question provided"),
            "question_type": question_type,
            "seed_mode": seed_mode,
            "mode": mode,
            "layout": layout,
        }
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Square chart tab / 古典方形圖盤
# ─────────────────────────────────────────────────────────────────────────────

def _render_square_chart_tab(chart: GeomancyChart) -> None:
    """Render the classical 4×4 square geomancy chart with controls."""
    import streamlit as st
    from astro.i18n import auto_cn

    # Controls row
    ctl1, ctl2, ctl3 = st.columns(3)
    with ctl1:
        theme = st.radio(
            auto_cn("主題", "Theme"),
            options=["parchment", "dark"],
            format_func=lambda v: {
                "parchment": auto_cn("📜 羊皮紙", "📜 Parchment"),
                "dark": auto_cn("🌑 暗色", "🌑 Dark"),
            }[v],
            horizontal=True,
            key="geo_sq_theme",
        )
    with ctl2:
        lang = st.radio(
            auto_cn("語言", "Language"),
            options=["zh", "en"],
            format_func=lambda v: {"zh": "中文", "en": "English"}[v],
            horizontal=True,
            key="geo_sq_lang",
        )
    with ctl3:
        st.markdown(
            f'<div style="padding-top:12px;font-size:0.85rem;color:#9E9E9E">'
            f'16 Figures · {chart.mode} · {chart.layout}</div>',
            unsafe_allow_html=True,
        )

    # Render the SVG chart
    if chart.figures_16:
        fig_names = [f.name_en for f in chart.figures_16]
        render_geomancy_svg_chart(
            figures_16=fig_names,
            center_text=chart.summary_text or chart.question[:40],
            theme=theme,
            lang=lang,
            chart_title=(
                auto_cn("地占神聖方形圖盤", "The Sacred Square of Geomancy")
            ),
            height=940,
        )
    else:
        st.info(auto_cn(
            "未找到16個圖形，請重新起卦。",
            "No figures found. Please cast the chart again.",
        ))

    # Judge & Reconciler info
    if chart.judge or chart.reconciler:
        st.markdown(
            f'<h4 style="color:#EDD88A">⚖️ {auto_cn("判官與調解者", "Judge & Reconciler")}</h4>',
            unsafe_allow_html=True,
        )
        c_j, c_r = st.columns(2)
        catalog = get_figure_catalog()
        for col, fig, role_zh, role_en in [
            (c_j, chart.judge, "判官", "Judge"),
            (c_r, chart.reconciler, "調解者", "Reconciler"),
        ]:
            if fig is None:
                continue
            info = catalog.get(fig.name_en, {})
            omen = info.get("omen_zh" if lang == "zh" else "omen_en", "")
            with col:
                st.markdown(
                    f'<div class="geo-figure-card" style="border:2px solid #C8A24A">'
                    f'<div style="font-size:0.8rem;color:#7BAFD4">'
                    f'{role_zh if lang == "zh" else role_en}</div>'
                    f'<div class="fig-name">{fig.name_en}</div>'
                    f'<div class="fig-zh">{fig.name_zh}</div>'
                    f'<div style="font-size:0.8rem;color:#C8A24A;margin-top:4px">'
                    f'{info.get("astrology_zh" if lang == "zh" else "astrology_en", "")}</div>'
                    f'<div style="font-size:0.82rem;color:#B0B8C8;margin-top:6px;font-style:italic">'
                    f'{omen}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# ─────────────────────────────────────────────────────────────────────────────
# Figure Oracle & comparison / 圖形神諭與對比
# ─────────────────────────────────────────────────────────────────────────────

def _render_figure_oracle(chart: GeomancyChart) -> None:
    """Figure oracle panel: select any figure and view its traditional meaning."""
    import streamlit as st
    from astro.i18n import auto_cn

    catalog = get_figure_catalog()
    lang = st.session_state.get("geo_sq_lang", "zh")

    st.markdown(
        f'<h3 style="color:#EDD88A">🔯 {auto_cn("圖形神諭", "Figure Oracle")}</h3>',
        unsafe_allow_html=True,
    )

    fig_options = list(catalog.keys())
    selected = st.selectbox(
        auto_cn("選擇圖形查詢", "Select a figure to consult"),
        options=fig_options,
        format_func=lambda n: f"{catalog[n]['latin']} / {catalog[n]['zh']}",
        key="geo_oracle_select",
    )

    if selected:
        info = catalog[selected]
        omen_key = "omen_zh" if lang == "zh" else "omen_en"
        astro_key = "astrology_zh" if lang == "zh" else "astrology_en"
        wiki = info.get("wiki", "")

        st.markdown(
            f'<div class="geo-figure-card" style="text-align:left;padding:20px">'
            f'<div class="fig-name" style="font-size:1.3rem">{info["latin"]}</div>'
            f'<div class="fig-zh" style="font-size:1rem;margin-top:4px">{info["zh"]}</div>'
            f'<hr style="border-color:#2A3A50;margin:10px 0"/>'
            f'<div style="color:#C8A24A;font-size:0.88rem">⭐ {info.get(astro_key, "")}</div>'
            f'<div style="color:#B0B8C8;font-size:0.9rem;margin-top:10px;font-style:italic">'
            f'"{info.get(omen_key, "")}"</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if wiki:
            st.markdown(f'🔗 [{auto_cn("開啟 Wiki 詳頁", "Open Wiki page")}]({wiki})')

    # Comparison buttons
    st.markdown("---")
    st.markdown(
        f'<h4 style="color:#EDD88A">🔀 {auto_cn("對比分析", "Compare Systems")}</h4>',
        unsafe_allow_html=True,
    )
    bc1, bc2 = st.columns(2)
    with bc1:
        if st.button(
            auto_cn("🌟 與西方占星對比", "🌟 Compare with Western Astrology"),
            key="geo_cmp_western",
            width="stretch",
        ):
            if selected:
                info = catalog[selected]
                st.info(
                    auto_cn(
                        f"**{info['latin']}** 占星對應：{info.get('astrology_zh', '')}。"
                        f"在西方占星中，此符號的守護行星掌管相應的宮位與星座特質。",
                        f"**{info['latin']}** astrological correspondence: {info.get('astrology_en', '')}. "
                        f"In Western Astrology, the ruling planet governs the associated house and sign qualities.",
                    )
                )
    with bc2:
        if st.button(
            auto_cn("🪬 與七政四餘/紫微對比", "🪬 Compare with Qizheng/Ziwei"),
            key="geo_cmp_qizheng",
            width="stretch",
        ):
            if selected:
                info = catalog[selected]
                st.info(
                    auto_cn(
                        f"**{info['latin']}**（{info['zh']}）在七政四餘傳統中："
                        f"可對應 {info.get('astrology_zh', '').split('·')[0].strip()} 之宮位能量；"
                        f"在紫微斗數中，可與同元素星系相互印證。",
                        f"**{info['latin']}** ({info['zh']}) in the Qizheng tradition: "
                        f"corresponds to the energy of {info.get('astrology_en', '').split('·')[0].strip()}. "
                        f"In Ziwei Doushu, cross-reference with stars of the same elemental affinity.",
                    )
                )

    # Medieval-tone master interpretation
    st.markdown("---")
    st.markdown(
        f'<h4 style="color:#EDD88A">📜 {auto_cn("中世紀地占師斷語", "Medieval Geomancer’s Oracle")}</h4>',
        unsafe_allow_html=True,
    )
    _render_agrippa_interpretation(chart)


def _render_agrippa_interpretation(chart: GeomancyChart) -> None:
    """Render a medieval-toned geomantic interpretation."""
    import streamlit as st
    from astro.i18n import auto_cn

    lang = st.session_state.get("geo_sq_lang", "zh")
    catalog = get_figure_catalog()
    asc = chart.ascendant_figure
    ph = chart.primary_house
    house_info = chart.houses[ph - 1]
    asc_info = catalog.get(asc.name_en, {})
    omen = asc_info.get("omen_zh" if lang == "zh" else "omen_en", "")
    judge = chart.judge
    judge_info = catalog.get(judge.name_en, {}) if judge else {}
    judge_omen = judge_info.get("omen_zh" if lang == "zh" else "omen_en", "") if judge else ""

    if lang == "zh":
        interpretation = (
            f"以 Agrippa 之名，以 Al-Zanātī 之智，吾今論斷此卦：\n\n"
            f"**上升圖形** *{asc.name_en}*（{asc.name_zh}）臨第一宮。"
            f"{omen}\n\n"
            f"**第 {ph} 宮**（{house_info.name_zh}）為此問之主宮，"
            f"其星座為 {house_info.sign_zh} {house_info.glyph}，"
            f"主題：{house_info.topics_zh}。"
        )
        if judge:
            interpretation += (
                f"\n\n**判官圖形** *{judge.name_en}*（{judge.name_zh}）乃此卦之終局判斷。"
                f"{judge_omen}"
            )
    else:
        interpretation = (
            f"In the name of Agrippa and by the wisdom of Al-Zanātī, I now pronounce judgment:\n\n"
            f"The **Ascendant Figure** *{asc.name_en}* rises in the First House. "
            f"{omen}\n\n"
            f"**House {ph}** ({house_info.name_en}) is the primary house for this question. "
            f"Its sign is {house_info.sign} {house_info.glyph}, "
            f"governing: {house_info.topics_en}."
        )
        if judge:
            interpretation += (
                f"\n\nThe **Judge** *{judge.name_en}* ({judge.name_zh}) reveals the final outcome. "
                f"{judge_omen}"
            )

    st.markdown(
        f'<div class="geo-house-card" style="border-left-color:#C8A24A;font-style:italic">'
        f'<div style="color:#EDD88A;font-size:0.88rem">{interpretation}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Mother figures panel / 母親圖形展示
# ─────────────────────────────────────────────────────────────────────────────

def _render_mother_figures(chart: GeomancyChart) -> None:
    import streamlit as st
    from astro.i18n import auto_cn

    st.markdown(
        f'<h3 style="color:#EDD88A">🌿 {auto_cn("母親圖形 / 上升圖形", "Mother Figures / Ascendant Figure")}</h3>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    qual_class = {"fortunate": "fig-qual-fortunate",
                  "unfortunate": "fig-qual-unfortunate",
                  "neutral": "fig-qual-neutral"}
    qual_label = {
        "fortunate": auto_cn("吉", "Fortunate"),
        "unfortunate": auto_cn("凶", "Unfortunate"),
        "neutral": auto_cn("中", "Neutral"),
    }
    for i, fig in enumerate(chart.mother_figures):
        with cols[i]:
            is_asc = (i == 0)
            label = auto_cn(f"母親 {i+1}", f"Mother {i+1}")
            if is_asc:
                label = auto_cn(f"母親 1 ★ 上升", "Mother 1 ★ ASC")
            dots_svg = _figure_dots_svg(fig, size=72)
            qc = qual_class.get(fig.quality, "fig-qual-neutral")
            ql = qual_label.get(fig.quality, "")
            border = "border:2px solid #C8A24A;" if is_asc else ""
            st.markdown(
                f'<div class="geo-figure-card" style="{border}">'
                f'<div style="font-size:0.75rem;color:#7BAFD4">{label}</div>'
                f'{dots_svg}'
                f'<div class="fig-name">{fig.name_en}</div>'
                f'<div class="fig-zh">{fig.name_zh}</div>'
                f'<div class="fig-sign">{fig.sign_zh} {ZODIAC_SIGNS[fig.sign_num]["glyph"]}</div>'
                f'<div class="{qc}">{ql}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Planet placements table / 行星落宮
# ─────────────────────────────────────────────────────────────────────────────

def _render_planet_table(chart: GeomancyChart) -> None:
    import streamlit as st
    from astro.i18n import auto_cn

    st.markdown(
        f'<h3 style="color:#EDD88A">🪐 {auto_cn("行星落宮", "Planet House Placements")}</h3>',
        unsafe_allow_html=True,
    )
    rows_html = []
    for p in chart.planet_placements:
        house_info = chart.houses[p.house - 1]
        house_name = auto_cn(house_info.name_zh, house_info.name_en)
        rows_html.append(
            f'<div class="geo-planet-row">'
            f'<span class="geo-planet-glyph">{p.glyph}</span>'
            f'<span class="geo-planet-name">{p.planet_zh} / {p.planet_en}</span>'
            f'<span class="geo-planet-house">第{p.house}宮 &nbsp;{house_name}</span>'
            f'<span class="geo-planet-sign">{p.sign_zh} {ZODIAC_SIGNS[p.sign_num]["glyph"]}</span>'
            f'</div>'
        )
    st.markdown("\n".join(rows_html), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# House detail panel / 宮位詳解
# ─────────────────────────────────────────────────────────────────────────────

def _render_house_details(chart: GeomancyChart) -> None:
    import streamlit as st
    from astro.i18n import auto_cn

    primary = chart.primary_house
    st.markdown(
        f'<h3 style="color:#EDD88A">🏛️ {auto_cn("十二宮詳解", "12 House Details")}</h3>'
        f'<p style="color:#B0B8C8;font-size:0.88rem">'
        f'{auto_cn(f"主要考察宮位：第{primary}宮（{chart.question_type_zh}）", f"Primary house: {primary} ({chart.question_type})")}'
        f'</p>',
        unsafe_allow_html=True,
    )

    for h in chart.houses:
        border_color = "#C8A24A" if h.house == primary else "#2A3A50"
        planet_names = "、".join(
            f"{p.glyph}{p.planet_zh}" for p in h.planets
        ) if h.planets else auto_cn("（空宮）", "(empty)")

        topics = auto_cn(h.topics_zh, h.topics_en)
        name = auto_cn(h.name_zh, h.name_en)
        st.markdown(
            f'<div class="geo-house-card" style="border-left-color:{border_color}">'
            f'<div class="geo-house-title">🏠 第{h.house}宮 — {name}</div>'
            f'<div class="geo-house-sign">{h.sign_zh} {h.glyph} ({h.sign}) · {h.element} · {h.quality}</div>'
            f'<div class="geo-house-topics">{topics}</div>'
            f'<div class="geo-house-gerard">{h.gerard_zh}</div>'
            f'<div class="geo-house-planets">🪐 {planet_names}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Primary house interpretation / 主要宮位解讀
# ─────────────────────────────────────────────────────────────────────────────

def _render_primary_interpretation(chart: GeomancyChart) -> None:
    import streamlit as st
    from astro.i18n import auto_cn

    ph = chart.primary_house
    house_info = chart.houses[ph - 1]
    asc_fig = chart.ascendant_figure

    st.markdown(
        f'<h3 style="color:#EDD88A">📖 {auto_cn("核心解讀", "Core Interpretation")}</h3>',
        unsafe_allow_html=True,
    )

    # Ascendant figure interpretation
    quality_map = {
        "fortunate": auto_cn("吉象", "Fortunate Omen"),
        "unfortunate": auto_cn("凶象", "Unfortunate Omen"),
        "neutral": auto_cn("中性", "Neutral"),
    }
    q_label = quality_map.get(asc_fig.quality, "")
    st.markdown(
        f"""
**{auto_cn("上升圖形", "Ascendant Figure")}**: {asc_fig.name_en} / {asc_fig.name_zh}
- {auto_cn("星座：", "Sign: ")}{asc_fig.sign_zh} ({asc_fig.sign})
- {auto_cn("元素：", "Element: ")}{asc_fig.element_zh} ({asc_fig.element})
- {auto_cn("行星：", "Planet: ")}{asc_fig.planet_zh} ({asc_fig.planet})
- {auto_cn("吉凶：", "Quality: ")}{q_label}
- {auto_cn("關鍵詞：", "Keywords: ")}{asc_fig.keywords_zh}
"""
    )

    # Primary house details
    planet_in_primary = [
        p for p in chart.planet_placements if p.house == ph
    ]
    st.markdown(
        f"""
**{auto_cn(f"第{ph}宮（{house_info.name_zh}）", f"House {ph} ({house_info.name_en})")}**

- {auto_cn("星座：", "Sign: ")}{house_info.sign_zh} ({house_info.sign})
- {auto_cn("主題：", "Topics: ")}{auto_cn(house_info.topics_zh, house_info.topics_en)}
- {auto_cn("Gerard解說：", "Gerard's gloss: ")}{house_info.gerard_zh}
- {auto_cn("落宮行星：", "Planets in house: ")}{
    "、".join(f"{p.glyph}{p.planet_zh}" for p in planet_in_primary)
    if planet_in_primary else auto_cn("（空宮）", "(empty)")
}
"""
    )

    # Gerard general rules
    with st.expander(auto_cn("📜 Gerard Cremonensis 傳統判斷規則", "📜 Gerard Cremonensis Traditional Rules")):
        _zh_rules = (
            "**壽命判斷**：觀第1宮上升星座與上升圖形的吉凶，搭配第8宮（死亡宮）行星情況。\n"
            "若上升為吉象（Fortuna Major / Laetitia / Acquisitio），命宮穩固，壽元充足；\n"
            "若上升為凶象（Tristitia / Cauda Draconis / Rubeus），需特別留意健康與生命力。\n\n"
            "**財富判斷**：第2宮星座與落宮行星決定財富豐寡。\n"
            "木星（♃）在第2宮為大吉；土星（♄）在第2宮阻礙財運；金星（♀）帶來穩定收入。\n\n"
            "**婚姻判斷**：第7宮主婚姻，觀上升（第1宮）與第7宮的行星關係。\n"
            "若為友星（如木星↔金星），則婚姻和諧；若為敵星（如火星↔金星），則婚姻多波折。\n\n"
            "**子女判斷**：第5宮主子女，木星在第5宮為多子多福；土星在第5宮則子嗣艱難。\n\n"
            "**事業判斷**：第10宮主事業名譽，太陽（☉）在此宮位大吉，土星（♄）則阻礙晉升。\n\n"
            "**旅行判斷**：第9宮主長途旅行，第3宮主短途。\n"
            "月亮（☽）在旅行宮表示旅途順利；火星（♂）則有危險。"
        )
        _en_rules = (
            "**Lifespan**: Observe House 1 sign and figure quality, combined with House 8 (Death).\n"
            "Fortunate figures (Fortuna Major / Laetitia / Acquisitio) = strong vitality;\n"
            "Unfortunate figures (Tristitia / Cauda Draconis / Rubeus) = health concerns.\n\n"
            "**Wealth**: House 2 sign and planets determine financial fortune.\n"
            "Jupiter (♃) in House 2 = great gain; Saturn (♄) = restriction; Venus (♀) = steady income.\n\n"
            "**Marriage**: House 7 governs marriage. Check planet relationships between Houses 1 and 7.\n"
            "Friendly planets = harmonious union; Hostile planets = turbulent relationship.\n\n"
            "**Children**: House 5 governs offspring. Jupiter in House 5 = abundant children; Saturn = difficulty.\n\n"
            "**Career**: House 10 governs career. Sun (☉) there is very fortunate; Saturn obstructs promotion.\n\n"
            "**Travel**: House 9 = long journeys, House 3 = short journeys.\n"
            "Moon (☽) = smooth travels; Mars (♂) = danger."
        )
        st.markdown(auto_cn(_zh_rules, _en_rules))


# ─────────────────────────────────────────────────────────────────────────────
# Main render entry point / 主渲染入口
# ─────────────────────────────────────────────────────────────────────────────

def render_streamlit(
    chart: GeomancyChart,
    after_chart_hook: Optional[Callable] = None,
) -> None:
    """
    Render the full Astronomical Geomancy reading UI.

    Args:
        chart:            Computed GeomancyChart instance.
        after_chart_hook: Optional callback rendered after the wheel
                          (used for the AI reading button).
    """
    import streamlit as st
    from astro.i18n import auto_cn, t

    st.markdown(_CSS, unsafe_allow_html=True)

    # Header
    st.markdown(
        f'<div class="geo-header">'
        f'<h2>🔮 {auto_cn(SYSTEM_NAME_ZH, SYSTEM_NAME_EN)} — '
        f'Gerardus Cremonensis</h2>'
        f'<p>{auto_cn(f"問題：{chart.question} ｜ {chart.timestamp}", f"Question: {chart.question} | {chart.timestamp}")}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Tabs
    tab_labels = [
        auto_cn("🗺️ 古典方形盤", "🗺️ Square Chart"),
        auto_cn("🌐 星盤輪圖", "🌐 Wheel Chart"),
        auto_cn("🌿 母親圖形", "🌿 Mother Figures"),
        auto_cn("🪐 行星落宮", "🪐 Planet Placements"),
        auto_cn("🏛️ 宮位詳解", "🏛️ House Details"),
        auto_cn("🔯 圖形神諭", "🔯 Figure Oracle"),
        auto_cn("📖 解讀", "📖 Reading"),
    ]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        _render_square_chart_tab(chart)

        if after_chart_hook:
            after_chart_hook()

    with tabs[1]:
        wheel_svg = build_geomancy_wheel_svg(chart)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(wheel_svg, unsafe_allow_html=True)
        with col2:
            st.markdown(
                f"**{auto_cn('上升圖形', 'Ascendant Figure')}**: "
                f"{chart.ascendant_figure.name_en} / {chart.ascendant_figure.name_zh}"
            )
            st.markdown(
                f"**{auto_cn('上升星座', 'Ascendant Sign')}**: "
                f"{chart.ascendant_sign_zh} {chart.houses[0].glyph} ({chart.ascendant_sign})"
            )
            st.markdown(f"**{auto_cn('問題類型', 'Question Type')}**: {chart.question_type_zh}")
            st.markdown(
                f"**{auto_cn('主要考察宮位', 'Primary House')}**: "
                f"{auto_cn(f'第{chart.primary_house}宮', f'House {chart.primary_house}')}"
            )
            # House-sign quick reference
            st.markdown(f"**{auto_cn('十二宮星座一覽', 'House-Sign Overview')}**")
            for h in chart.houses:
                planet_txt = "  " + " ".join(p.glyph for p in h.planets) if h.planets else ""
                st.markdown(
                    f"- {auto_cn(f'第{h.house}宮', f'H{h.house}')} "
                    f"{h.sign_zh} {h.glyph}{planet_txt}"
                )

    with tabs[2]:
        _render_mother_figures(chart)

    with tabs[3]:
        _render_planet_table(chart)

    with tabs[4]:
        _render_house_details(chart)

    with tabs[5]:
        _render_figure_oracle(chart)

    with tabs[6]:
        _render_primary_interpretation(chart)
