"""Streamlit renderer for Huangji Jingshi (皇極經世)."""

from __future__ import annotations

import math
from typing import Callable

from astro.chart_renderer_v2 import build_cultural_svg

# Pre-transition binary codes for the 64 hexagrams (先天序)
_GUA_BINARY: dict[str, str] = {
    "乾": "111111", "夬": "111110", "大有": "111101", "大壯": "111100",
    "小畜": "111011", "需": "111010", "大畜": "111001", "泰": "111000",
    "履": "110111", "兌": "110110", "睽": "110101", "歸妹": "110100",
    "中孚": "110011", "節": "110010", "損": "110001", "臨": "110000",
    "同人": "101111", "革": "101110", "離": "101101", "豐": "101100",
    "家人": "101011", "既濟": "101010", "賁": "101001", "明夷": "101000",
    "無妄": "100111", "隨": "100110", "噬嗑": "100101", "震": "100100",
    "益": "100011", "屯": "100010", "頤": "100001", "復": "100000",
    "姤": "011111", "大過": "011110", "鼎": "011101", "恆": "011100",
    "巽": "011011", "井": "011010", "蠱": "011001", "升": "011000",
    "訟": "010111", "困": "010110", "未濟": "010101", "解": "010100",
    "渙": "010011", "坎": "010010", "蒙": "010001", "師": "010000",
    "遯": "001111", "咸": "001110", "旅": "001101", "小過": "001100",
    "漸": "001011", "蹇": "001010", "艮": "001001", "謙": "001000",
    "否": "000111", "萃": "000110", "晉": "000101", "豫": "000100",
    "觀": "000011", "比": "000010", "剝": "000001", "坤": "000000",
}


def _gua_svg(name: str, width: int = 60, height: int = 80) -> str:
    """Render a hexagram as compact SVG lines.

    Yang (1) → solid bar; Yin (0) → broken bar.
    Lines are read from bottom (line 1) to top (line 6).

    Args:
        name: Hexagram name, e.g. ``'乾'``, ``'坤'``.  If not in the
              :data:`_GUA_BINARY` table a fallback text element is returned.
        width: Width of the SVG viewport in pixels (default 60).
        height: Height of the SVG viewport in pixels (default 80).

    Returns:
        SVG fragment (without ``<svg>`` wrapper) containing ``<rect>`` and
        ``<text>`` elements.
    """
    binary = _GUA_BINARY.get(name, "")
    if not binary:
        return f'<text fill="#e6d4a1" font-size="18" x="{width//2}" y="{height//2}" text-anchor="middle">{name}</text>'

    lines: list[str] = []
    line_h = (height - 20) // 6
    bar_w = width - 12
    gap = 8

    for idx, bit in enumerate(reversed(binary)):
        y = height - 14 - (idx + 1) * line_h
        if bit == "1":
            lines.append(f'<rect x="6" y="{y}" width="{bar_w}" height="{line_h - 4}" fill="#c8a84b" rx="1"/>')
        else:
            half = (bar_w - gap) // 2
            lines.append(f'<rect x="6" y="{y}" width="{half}" height="{line_h - 4}" fill="#7a6535" rx="1"/>')
            lines.append(f'<rect x="{6 + half + gap}" y="{y}" width="{half}" height="{line_h - 4}" fill="#7a6535" rx="1"/>')

    lines.append(f'<text x="{width//2}" y="{height - 3}" text-anchor="middle" fill="#e6d4a1" font-size="11">{name}</text>')
    return "\n".join(lines)


def _build_huangji_concentric_svg(
    p,
    width: int = 560,
    height: int = 560,
) -> str:
    """Build a concentric-ring 皇極時間輪 SVG.

    Rings from outside-in: 元 → 會 → 運 → 世
    Centre shows current hexagram configuration.
    """
    cx, cy = width // 2, height // 2

    # Ring radii
    r_yuan = 255
    r_hui = 210
    r_yun = 165
    r_shi = 120
    r_core = 75

    parts: list[str] = []

    # Background
    parts.append(f'<rect width="{width}" height="{height}" fill="#0d0b14"/>')

    # Decorative background radial gradient
    parts.append(
        '<defs>'
        f'<radialGradient id="rg_core" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#2a1f0d" stop-opacity="0.9"/>'
        '<stop offset="100%" stop-color="#0d0b14" stop-opacity="0"/>'
        '</radialGradient>'
        '<radialGradient id="rg_glow" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#c8a84b" stop-opacity="0.08"/>'
        '<stop offset="100%" stop-color="#c8a84b" stop-opacity="0"/>'
        '</radialGradient>'
        '</defs>'
    )
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_yuan}" fill="url(#rg_glow)"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_core}" fill="url(#rg_core)"/>')

    # Outer decorative ring
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_yuan + 6}" fill="none" stroke="#3d2e0e" stroke-width="12" stroke-opacity="0.5"/>')

    # Ring borders
    ring_params = [
        (r_yuan,  "#7a6030", "2",   "元", p.yuan,  "1元＝129,600年"),
        (r_hui,   "#6c5426", "1.5", "會", p.hui,   f"第{p.hui}會（{p.year_in_hui}/10800年）"),
        (r_yun,   "#5e471e", "1.2", "運", p.yun,   f"第{p.yun}運（{p.year_in_yun}/360年）"),
        (r_shi,   "#4e3a16", "1",   "世", p.shi,   f"第{p.shi}世（{p.year_in_shi}/30年）"),
    ]
    for r, stroke, sw, label, val, detail in ring_params:
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{stroke}" stroke-width="{sw}"/>')

    # Ring labels at 12 o'clock on each ring
    label_data = [
        (r_yuan - 18,  "元", str(p.yuan), "#d4b86a"),
        (r_hui - 18,   "會", str(p.hui),  "#c8a84b"),
        (r_yun - 18,   "運", str(p.yun),  "#bc9836"),
        (r_shi - 18,   "世", str(p.shi),  "#b08826"),
    ]
    for ry, ch, val, color in label_data:
        parts.append(f'<text x="{cx}" y="{cy - ry}" text-anchor="middle" fill="{color}" font-size="13" font-family="serif">{ch}{val}</text>')

    # 12 tick marks around the outermost ring (12 會)
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        x1 = cx + (r_yuan - 2) * math.cos(ang)
        y1 = cy + (r_yuan - 2) * math.sin(ang)
        x2 = cx + (r_yuan + 10) * math.cos(ang)
        y2 = cy + (r_yuan + 10) * math.sin(ang)
        active = (i + 1) == p.hui
        color = "#c8a84b" if active else "#4a3a1a"
        sw = "2" if active else "1"
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{sw}"/>')

    # 30 tick marks on the 世 ring
    for i in range(30):
        ang = math.radians(i * 12 - 90)
        x1 = cx + (r_shi - 2) * math.cos(ang)
        y1 = cy + (r_shi - 2) * math.sin(ang)
        x2 = cx + (r_shi + 8) * math.cos(ang)
        y2 = cy + (r_shi + 8) * math.sin(ang)
        active = (i + 1) == p.year_in_shi
        color = "#c8a84b" if active else "#3a2c10"
        sw = "2.5" if active else "0.8"
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{sw}"/>')

    # Centre core: current gua glyphs arranged as a star
    gua_items = [
        ("世", p.gua.get("世卦", ""), 0),
        ("運", p.gua.get("運卦", ""), 90),
        ("旬", p.gua.get("旬卦", ""), 180),
        ("正", p.gua.get("正卦", ""), 270),
    ]
    gua_r = 96
    for label, gua_name, ang_deg in gua_items:
        ang = math.radians(ang_deg - 90)
        gx = cx + gua_r * math.cos(ang) - 24
        gy = cy + gua_r * math.sin(ang) - 30
        parts.append(f'<g transform="translate({gx:.1f},{gy:.1f})">')
        parts.append(_gua_svg(gua_name, 48, 56))
        parts.append(f'<text x="24" y="-4" text-anchor="middle" fill="#8a7040" font-size="10" font-family="serif">{label}</text>')
        parts.append('</g>')

    # Central title
    parts.append(f'<text x="{cx}" y="{cy - 8}" text-anchor="middle" fill="#d8c59a" font-size="18" font-family="serif" font-weight="bold">皇極</text>')
    parts.append(f'<text x="{cx}" y="{cy + 12}" text-anchor="middle" fill="#a89050" font-size="12" font-family="serif">經世</text>')

    # Subtitle band
    hui_gua = getattr(p, "hui_gua", "")
    if hui_gua:
        parts.append(f'<text x="{cx}" y="{height - 20}" text-anchor="middle" fill="#7a6030" font-size="11" font-family="serif">第{p.hui}會卦：{hui_gua}</text>')

    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">'
        + "".join(parts)
        + '</svg>'
    )


def _build_lifetime_timeline_svg(lifetime_cycles: list[dict], width: int = 540, height: int = 100) -> str:
    """Build a horizontal lifetime 世 timeline SVG."""
    if not lifetime_cycles:
        return ""

    n = len(lifetime_cycles)
    seg_w = width / n
    parts = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">']
    parts.append(f'<rect width="{width}" height="{height}" fill="#0d0b14" rx="6"/>')

    for i, cyc in enumerate(lifetime_cycles):
        x = i * seg_w
        is_cur = cyc.get("is_current", False)
        fill = "#2a1f0d" if is_cur else "#14110a"
        stroke = "#c8a84b" if is_cur else "#3d2e0e"
        sw = "2" if is_cur else "1"
        parts.append(f'<rect x="{x:.1f}" y="8" width="{seg_w - 2:.1f}" height="{height - 16}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="3"/>')
        tx = x + seg_w / 2
        label_col = "#e6d4a1" if is_cur else "#7a6030"
        parts.append(f'<text x="{tx:.1f}" y="35" text-anchor="middle" fill="{label_col}" font-size="11" font-family="serif">第{i + 1}世</text>')
        parts.append(f'<text x="{tx:.1f}" y="52" text-anchor="middle" fill="{label_col}" font-size="10" font-family="serif">{cyc.get("age_range","")}</text>')
        if is_cur and cyc.get("current_age") is not None:
            age_x = x + (cyc["current_age"] % 30) / 30.0 * seg_w
            parts.append(f'<line x1="{age_x:.1f}" y1="8" x2="{age_x:.1f}" y2="{height - 8}" stroke="#c8a84b" stroke-width="2" stroke-dasharray="3 2"/>')
            parts.append(f'<text x="{age_x:.1f}" y="{height - 4}" text-anchor="middle" fill="#c8a84b" font-size="9">▲</text>')

    parts.append('</svg>')
    return "".join(parts)


def _gua_panel_html(gua_name: str, bagua_xiang: dict) -> str:
    """Build an HTML card for a hexagram with its attributes.

    Args:
        gua_name: Hexagram name used in the fallback message.
        bagua_xiang: Attribute dict from xinyi_fawei.json ``bagua_xiang``.
            Expected keys (all optional): ``definition``, ``seasons``,
            ``body``, ``human_events``, ``nature``, ``geography``,
            ``people``, ``animals``, ``plants``, ``wuxing_element``,
            ``wuyin``, ``color``, ``numbers``, ``tiangan``, ``dizhi``.

    Returns:
        HTML string with a styled table of attributes.
    """
    if not bagua_xiang:
        return f'<p style="color:#a89050">（{gua_name}卦無詳細取象資料）</p>'

    attrs = {
        "定義": bagua_xiang.get("definition", ""),
        "時序": bagua_xiang.get("seasons", ""),
        "身體": bagua_xiang.get("body", ""),
        "人事": bagua_xiang.get("human_events", ""),
        "天文": bagua_xiang.get("nature", ""),
        "地理": bagua_xiang.get("geography", ""),
        "人物": bagua_xiang.get("people", ""),
        "動物": bagua_xiang.get("animals", ""),
        "植物": bagua_xiang.get("plants", ""),
        "五行": bagua_xiang.get("wuxing_element", ""),
        "五音": bagua_xiang.get("wuyin", ""),
        "五色": bagua_xiang.get("color", ""),
        "數目": bagua_xiang.get("numbers", ""),
        "天干": bagua_xiang.get("tiangan", ""),
        "地支": bagua_xiang.get("dizhi", ""),
    }
    rows = "".join(
        f'<tr><td style="color:#8a7040;padding:2px 8px;white-space:nowrap">{k}</td>'
        f'<td style="color:#d4c490;padding:2px 8px">{v}</td></tr>'
        for k, v in attrs.items()
        if v
    )
    return (
        f'<div style="background:#14110a;border:1px solid #3d2e0e;border-radius:6px;padding:12px">'
        f'<table style="width:100%;border-collapse:collapse">{rows}</table>'
        f'</div>'
    )


def render_streamlit(chart, *, lang: str = "zh", after_chart_hook: Callable[[], None] | None = None) -> None:
    import streamlit as st

    t_basic = "基本盤" if lang == "zh" else "Core Pan"
    t_cycles = "大週期" if lang == "zh" else "Macro Cycles"
    t_gua = "卦象解讀" if lang == "zh" else "Gua Reading"
    t_cross = "跨體系對照" if lang == "zh" else "Cross-System"
    t_history = "歷史年表" if lang == "zh" else "Historical Timeline"

    t_title = "### 🏮 皇極經世（邵雍先天易數）" if lang == "zh" else "### 🏮 Huangji Jingshi (Shao Yong's Prenatal Number Doctrine)"
    t_caption = (
        "宋代書卷氣 × 現代極簡神秘風，觀物取象，推宇宙大數。"
        if lang == "zh"
        else "Song literati aesthetics × modern minimal mystery, observing macro-cycles through symbols."
    )

    p = chart.huangji_pan

    st.markdown(t_title)
    st.caption(t_caption)

    # Philosophy quote banner
    quote = getattr(p, "philosophy_quote", {})
    if quote and quote.get("text"):
        st.markdown(
            f'<blockquote style="border-left:3px solid #c8a84b;padding:6px 12px;'
            f'background:#14110a;color:#d4c490;font-size:13px;margin:8px 0;font-style:italic">'
            f'{quote["text"]}'
            f'<span style="color:#7a6030;font-size:11px;display:block;margin-top:4px">── {quote.get("source","")}</span>'
            f'</blockquote>',
            unsafe_allow_html=True,
        )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([t_basic, t_cycles, t_gua, t_cross, t_history])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("元", p.yuan)
        c2.metric("會", p.hui)
        c3.metric("運", p.yun)
        c4.metric("世", p.shi)

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("世內年份", f"{p.year_in_shi}/30")
        c6.metric("運內年份", f"{p.year_in_yun}/360")
        c7.metric("會內年份", f"{p.year_in_hui}/10800")
        hui_gua = getattr(p, "hui_gua", "")
        c8.metric("會卦", hui_gua or "—")

        st.caption(f"節氣（kinwangji）：{p.jieqi_kinwangji} ｜ 節氣（Swiss）：{p.jieqi_swiss}")

        st.dataframe(
            [{"層位": k, "卦": v, "動爻": p.moving_lines.get(f"{k}動爻", "")} for k, v in p.gua.items()],
            use_container_width=True,
            hide_index=True,
        )

        wheel_inner = _build_huangji_concentric_svg(p)
        wheel = build_cultural_svg(wheel_inner, "tab_huangji", title="皇極時間輪", animate_spin=False)
        st.markdown(wheel, unsafe_allow_html=True)
        if after_chart_hook:
            after_chart_hook()

    with tab2:
        st.markdown("#### 元會運世時間軸")
        st.dataframe(p.major_cycle_milestones, use_container_width=True, hide_index=True)

        # Lifetime 世 cycles
        lifetime = getattr(p, "lifetime_cycles", [])
        if lifetime:
            st.markdown("#### 個人一生皇極定位（30年一世）")
            timeline_svg = _build_lifetime_timeline_svg(lifetime)
            if timeline_svg:
                st.markdown(
                    f'<div style="background:#0d0b14;padding:8px;border-radius:6px">{timeline_svg}</div>',
                    unsafe_allow_html=True,
                )
            lifetime_display = [
                {
                    "世序": c["period"],
                    "年齡段": c["age_range"],
                    "年份": c["year_range"],
                    "世號": c["shi_num"],
                    "當前": "◉ 當前" if c["is_current"] else "",
                }
                for c in lifetime
            ]
            st.dataframe(lifetime_display, use_container_width=True, hide_index=True)

        st.code(chart.board_text, language="text")

    with tab3:
        st.markdown("#### 世卦取象（觀物分析）")
        shi_gua = p.gua.get("世卦", "")
        yun_gua = p.gua.get("運卦", "")
        nian_gua = p.gua.get("年卦", "")

        bagua_xiang = getattr(p, "bagua_xiang", {})
        col_gua, col_info = st.columns([1, 3])
        with col_gua:
            # Render hexagram glyph
            gua_svg_str = _gua_svg(shi_gua, 80, 100)
            st.markdown(
                f'<div style="display:flex;flex-direction:column;align-items:center;background:#14110a;'
                f'padding:12px;border-radius:6px;border:1px solid #3d2e0e">'
                f'<svg viewBox="0 0 80 100" width="80" height="100">{gua_svg_str}</svg>'
                f'<p style="color:#d4c490;text-align:center;font-size:16px;margin-top:4px">{shi_gua}卦</p>'
                f'<p style="color:#7a6030;font-size:11px">世卦</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with col_info:
            st.markdown(_gua_panel_html(shi_gua, bagua_xiang), unsafe_allow_html=True)

        # Year/month/day gua summary
        st.markdown("#### 年月日時卦覽")
        gua_cols = st.columns(4)
        for i, (level, key) in enumerate([("年卦", "年卦"), ("月卦", "月卦"), ("日卦", "日卦"), ("時卦", "時卦")]):
            gua_val = p.gua.get(key, "—")
            binary = _GUA_BINARY.get(gua_val, "")
            mini_svg = f'<svg viewBox="0 0 40 60" width="40" height="60">{_gua_svg(gua_val, 40, 60)}</svg>' if binary else ""
            with gua_cols[i]:
                st.markdown(
                    f'<div style="background:#14110a;border:1px solid #3d2e0e;border-radius:4px;'
                    f'text-align:center;padding:8px">'
                    f'<p style="color:#8a7040;font-size:10px;margin:0">{level}</p>'
                    f'{mini_svg}'
                    f'<p style="color:#d4c490;font-size:15px;margin:2px 0">{gua_val}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with tab4:
        rows = [
            {"系統": "Hellenistic Zodiacal Releasing", "當前定位": chart.cross_system.zodiacal_releasing_l1 or "—"},
            {"系統": "Annual Profections", "當前定位": chart.cross_system.annual_profection or "—"},
            {"系統": "Vedic Dasha", "當前定位": chart.cross_system.vedic_dasha or "—"},
            {"系統": "紫微大限", "當前定位": chart.cross_system.ziwei_daxian or "—"},
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
        current_gua = p.gua.get("世卦") or p.gua.get("運卦") or "—"
        if lang == "zh":
            ai_hint = (
                f"AI 交叉解讀模板：你當前位於皇極第{p.yun}運第{p.shi}世（{current_gua}卦），"
                "可與西方釋放期、紫微大限、Vedic 大運形成同頻綜合判讀。"
            )
        else:
            ai_hint = (
                f"AI synthesis template: you are currently in Huangji Yun {p.yun}, Shi {p.shi} "
                f"({current_gua} hexagram), aligned with Zodiacal Releasing, Ziwei Daxian, and Vedic Dasha."
            )
        st.info(ai_hint)

    with tab5:
        if p.historical_context:
            st.dataframe([
                {
                    "朝代/時代": h.dynasty,
                    "年號/政權": h.era,
                    "稱號": h.title,
                    "起始": h.start_year,
                    "年數": h.duration,
                }
                for h in p.historical_context
            ], use_container_width=True, hide_index=True)
        else:
            st.caption("該年份無可用歷史對照資料。")

