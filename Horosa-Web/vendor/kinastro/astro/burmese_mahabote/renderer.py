"""
緬甸／撣族 Mahabote 深度占星渲染模組
Burmese / Shan Mahabote Astrology — Renderer

提供完整的 Streamlit UI，包含：
  - Tab 1: 本命排盤（8 宮盤 SVG + 方位羅盤 + 性格詳解）
  - Tab 2: 大運小運（Atar 大運時間軸 + 年度小運表）
  - Tab 3: Year Chart 流年過運
  - Tab 4: 合婚相容性計算
  - Tab 5: 撣族文化 (Shan Cultural Notes)

UI 風格與 Wariga、Weton 模組保持一致。

古法依據：
  - Barbara Cameron, *The Little Key*
  - Traditional Shan (Tai Yai) oral calendar traditions
"""

from __future__ import annotations

import math
from datetime import date
from typing import Optional

import streamlit as st

from .calculator import (
    MahaboteChart,
    CompatibilityResult,
    YearChartEntry,
    compute_compatibility,
    compute_mahabote_chart,
    compute_year_chart_for_year,
)
from .constants import (
    BIRTH_SIGN_DATA,
    PLANET_COLORS,
    DIRECTIONS_8,
    MAHABOTE_HOUSES,
    COMPAT_PLANETS,
    SHAN_CALENDAR_INFO,
    WEEKDAY_TO_SIGN,
    HOSTILE_PAIRS,
    COMPAT_LABELS,
    COMPAT_PERCENT,
)


# ============================================================
# 色彩主題
# ============================================================
_BG         = "#1a1a2e"
_BORDER     = "#c9a96e"
_ACCENT     = "#c9a96e"
_TEXT_DIM   = "#aaaaaa"
_TEXT_WHITE = "#ffffff"
_CENTER_BG  = "#0d0d1a"

# Fortune quality → color mapping (used across multiple render functions)
_QUALITY_COLOR: dict = {
    "大吉": "#FFD700",
    "吉":   "#32CD32",
    "中性": "#87CEEB",
    "凶":   "#DC143C",
}


# ============================================================
# SVG 輪盤 (8-Sector Wheel)
# ============================================================

def _build_wheel_svg(chart: MahaboteChart, size: int = 480) -> str:
    """Build an 8-sector retro-style Mahabote wheel as inline SVG.

    Traditional Burmese compass-style wheel with 8 sectors (NE→N clockwise),
    each showing planet symbol, animal totem, and direction label.
    Birth planet sector is highlighted in gold.
    """
    cx, cy = size / 2, size / 2
    r_outer = size / 2 - 10
    r_inner = r_outer * 0.36
    r_mid   = (r_outer + r_inner) / 2
    r_label = r_outer * 0.80
    r_sym   = r_outer * 0.62
    r_anim  = r_outer * 0.48

    sectors = DIRECTIONS_8
    start_offset = -67.5 - 90  # NE sector top-right

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {size} {size}" '
        f'style="max-width:100%;height:auto;font-family:serif;">'
    ]

    # Outer ring
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" '
        f'fill="{_BG}" stroke="{_BORDER}" stroke-width="3"/>'
    )

    for idx, sec in enumerate(sectors):
        a_start = start_offset + idx * 45
        a_end   = a_start + 45
        a1 = math.radians(a_start)
        a2 = math.radians(a_end)
        a_mid = math.radians((a_start + a_end) / 2)

        # Pie-slice path (outer → inner arc)
        x1o = cx + r_outer * math.cos(a1)
        y1o = cy + r_outer * math.sin(a1)
        x2o = cx + r_outer * math.cos(a2)
        y2o = cy + r_outer * math.sin(a2)
        x1i = cx + r_inner * math.cos(a1)
        y1i = cy + r_inner * math.sin(a1)
        x2i = cx + r_inner * math.cos(a2)
        y2i = cy + r_inner * math.sin(a2)

        color = PLANET_COLORS.get(sec["planet"], "#888")
        is_birth = (sec["planet"] == chart.birth_planet)
        fill_op  = "0.40" if is_birth else "0.14"
        stk_w    = "3"    if is_birth else "1"
        stk_c    = "#FFD700" if is_birth else _BORDER

        path = (
            f'M {x1i:.1f} {y1i:.1f} L {x1o:.1f} {y1o:.1f} '
            f'A {r_outer:.1f} {r_outer:.1f} 0 0 1 {x2o:.1f} {y2o:.1f} '
            f'L {x2i:.1f} {y2i:.1f} '
            f'A {r_inner:.1f} {r_inner:.1f} 0 0 0 {x1i:.1f} {y1i:.1f} Z'
        )
        parts.append(
            f'<path d="{path}" fill="{color}" fill-opacity="{fill_op}" '
            f'stroke="{stk_c}" stroke-width="{stk_w}"/>'
        )

        # Direction label (outer)
        lx = cx + r_label * math.cos(a_mid)
        ly = cy + r_label * math.sin(a_mid)
        parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="{_BORDER}" '
            f'font-size="11" font-weight="bold">{sec["dir_cn"]}</text>'
        )

        # Planet symbol (mid ring)
        sx = cx + r_sym * math.cos(a_mid)
        sy = cy + r_sym * math.sin(a_mid)
        parts.append(
            f'<text x="{sx:.1f}" y="{sy:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="{color}" '
            f'font-size="20">{sec["symbol"]}</text>'
        )

        # Animal emoji + CN (inner ring)
        ax = cx + r_anim * math.cos(a_mid)
        ay = cy + r_anim * math.sin(a_mid)
        parts.append(
            f'<text x="{ax:.1f}" y="{ay:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="{_TEXT_WHITE}" '
            f'font-size="9">{sec["animal_emoji"]} {sec["animal_cn"]}</text>'
        )

    # Center circle
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" '
        f'fill="{_CENTER_BG}" stroke="{_BORDER}" stroke-width="2"/>'
    )
    birth_color = PLANET_COLORS.get(chart.birth_planet, _ACCENT)
    parts += [
        f'<text x="{cx}" y="{cy - 22}" text-anchor="middle" '
        f'fill="{_BORDER}" font-size="9">မဟာဘုတ်</text>',
        f'<text x="{cx}" y="{cy + 3}" text-anchor="middle" '
        f'fill="{birth_color}" font-size="28">{chart.birth_planet_symbol}</text>',
        f'<text x="{cx}" y="{cy + 22}" text-anchor="middle" '
        f'fill="{birth_color}" font-size="12" font-weight="bold">'
        f'{chart.birth_planet_cn}</text>',
        f'<text x="{cx}" y="{cy + 36}" text-anchor="middle" '
        f'fill="{_TEXT_DIM}" font-size="9">ME {chart.myanmar_year} · '
        f'{chart.weekday_name_cn}</text>',
    ]
    parts.append('</svg>')
    return '\n'.join(parts)


# ============================================================
# 八宮盤格線 (3×3 Grid)
# ============================================================

def _house_cell_html(house, *, star: bool = False) -> str:
    color = PLANET_COLORS.get(house.planet, "#888")
    border = "3px solid gold" if house.is_birth_house else "1px solid #555"
    bg     = f"{color}14"
    prefix = "⭐ " if star and house.is_birth_house else ""
    return (
        f'<td style="background:{bg};border:{border};padding:10px;'
        f'border-radius:8px;text-align:center;vertical-align:top;'
        f'color:white;width:33%;">'
        f'<div style="font-size:10px;color:#aaa;">'
        f'{house.name_en} ({house.meaning})</div>'
        f'<div style="font-size:14px;font-weight:bold;">'
        f'{prefix}{house.name_cn}</div>'
        f'<div style="font-size:10px;color:#ccc;">{house.weekday_cn}</div>'
        f'<div style="font-size:24px;margin:3px 0;">{house.planet_symbol}</div>'
        f'<div style="font-size:12px;color:{color};font-weight:bold;">'
        f'{house.planet_cn}</div>'
        f'<div style="font-size:11px;">{house.animal_emoji} {house.animal_cn}</div>'
        f'</td>'
    )


def _center_cell_html(chart: MahaboteChart) -> str:
    color = PLANET_COLORS.get(chart.birth_planet, _ACCENT)
    return (
        f'<td style="background:{_CENTER_BG};border:2px solid {color};'
        f'padding:10px;border-radius:8px;text-align:center;'
        f'vertical-align:middle;color:white;width:33%;">'
        f'<div style="font-size:10px;color:#aaa;">Mahabote</div>'
        f'<div style="font-size:28px;">{chart.birth_planet_symbol}</div>'
        f'<div style="font-size:13px;font-weight:bold;color:{color};">'
        f'{chart.birth_planet_cn}</div>'
        f'<div style="font-size:10px;color:#bbb;">'
        f'ME {chart.myanmar_year}</div>'
        f'</td>'
    )


def _render_house_grid(chart: MahaboteChart) -> None:
    st.subheader("🏛️ Mahabote 八宮盤")
    # Layout: Row0=[7,6,5] Row1=[4,center,0] Row2=[3,2,1]
    grid = [[7, 6, 5], [4, "c", 0], [3, 2, 1]]
    html = (
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        '<table style="border-collapse:separate;border-spacing:4px;'
        'margin:auto;width:100%;min-width:260px;table-layout:fixed;">'
    )
    for row in grid:
        html += '<tr>'
        for cell in row:
            if cell == "c":
                html += _center_cell_html(chart)
            else:
                html += _house_cell_html(chart.houses[cell], star=True)
        html += '</tr>'
    html += '</table></div>'
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# 方位羅盤 (Compass)
# ============================================================

def _compass_cell(sec: dict, birth_planet: str) -> str:
    is_birth = (sec["planet"] == birth_planet)
    color  = PLANET_COLORS.get(sec["planet"], "#888")
    border = f"3px solid {color}" if is_birth else "1px solid #555"
    bg     = f"{color}22" if is_birth else _BG
    return (
        f'<td style="background:{bg};border:{border};padding:8px;'
        f'border-radius:8px;text-align:center;color:white;width:33%;">'
        f'<div style="font-size:10px;color:#aaa;">{sec["dir_cn"]}</div>'
        f'<div style="font-size:22px;">{sec["symbol"]}</div>'
        f'<div style="font-size:12px;font-weight:bold;color:{color};">'
        f'{sec["planet_cn"]}</div>'
        f'<div style="font-size:10px;">{sec["animal_emoji"]} {sec["animal_cn"]}</div>'
        f'</td>'
    )


def _render_compass(chart: MahaboteChart) -> None:
    st.subheader("🧭 八方位行星羅盤")
    # Direction order: NW, N, NE / W, centre, E / SW, S, SE
    d = {s["dir_en"]: s for s in DIRECTIONS_8}
    birth = chart.birth_planet
    _c = _compass_cell
    center_td = (
        '<td style="text-align:center;vertical-align:middle;'
        'font-size:28px;">🧭</td>'
    )
    html = (
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        '<table style="border-collapse:separate;border-spacing:4px;'
        'margin:auto;width:80%;max-width:480px;table-layout:fixed;">'
        f'<tr>{_c(d["NW"],birth)}{_c(d["N"],birth)}{_c(d["NE"],birth)}</tr>'
        f'<tr>{_c(d["W"],birth)}{center_td}{_c(d["E"],birth)}</tr>'
        f'<tr>{_c(d["SW"],birth)}{_c(d["S"],birth)}{_c(d["SE"],birth)}</tr>'
        '</table></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# 本命資訊高亮框
# ============================================================

def _render_birth_highlight(chart: MahaboteChart) -> None:
    color = PLANET_COLORS.get(chart.birth_planet, "#888")
    rahu_note = " ⚠️ 星期三傍晚 → 羅睺" if chart.is_rahu else ""
    st.markdown(
        f'<div style="background:{color}22;border:2px solid {color};'
        f'padding:14px;border-radius:10px;margin-bottom:12px;color:white;">'
        f'<div style="font-size:20px;font-weight:bold;margin-bottom:6px;">'
        f'{chart.birth_planet_symbol} {chart.birth_planet_cn} '
        f'({chart.birth_planet}){rahu_note}</div>'
        f'<div>守護動物：{chart.birth_animal_emoji} '
        f'<b>{chart.birth_animal_cn}</b> ({chart.birth_animal_en} / '
        f'{chart.birth_animal_myanmar})</div>'
        f'<div>方位：{chart.birth_direction} ｜ '
        f'元素：{chart.birth_planet_element}</div>'
        f'<div>Mahabote 宮位：<b>{chart.birth_house_name_cn}</b> '
        f'({chart.birth_house_name_en}) — {chart.birth_house_meaning}</div>'
        f'<div style="font-size:12px;color:#bbb;margin-top:4px;">'
        f'{chart.birth_house_description}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# Tab 1 — 本命排盤
# ============================================================

def _render_tab_natal(chart: MahaboteChart) -> None:
    # Chart header info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**日期:** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**時間:** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**時區:** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**地點:** {chart.location_name or '—'}")
        st.write(f"**緯度:** {chart.latitude:.4f}°")
        st.write(f"**經度:** {chart.longitude:.4f}°")
    with col3:
        st.write(f"**緬甸紀年 (ME):** {chart.myanmar_year}")
        st.write(f"**撣曆年:** {chart.shan_year}")
        st.write(f"**出生星期:** {chart.weekday_name_cn} ({chart.weekday_name_myanmar})")

    _render_birth_highlight(chart)
    st.divider()

    # SVG wheel
    svg = _build_wheel_svg(chart)
    st.markdown(
        f'<div style="text-align:center;margin:0 auto;max-width:500px;">{svg}</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    _render_compass(chart)
    st.divider()

    _render_house_grid(chart)
    st.divider()

    # Sign profile detail
    _render_sign_profile(chart)
    st.divider()

    # House detail table
    _render_house_table(chart)
    st.divider()

    # Direction omens
    _render_direction_omens(chart)


def _render_sign_profile(chart: MahaboteChart) -> None:
    """Render full personality / career / health / love / remedies profile."""
    sd = chart.sign_profile
    color = PLANET_COLORS.get(chart.birth_planet, "#888")

    st.subheader(
        f"{sd['animal_emoji']} {sd['animal_cn']} — "
        f"{sd['planet_cn']} 守護者完整命格"
    )

    tab_pers, tab_career, tab_health, tab_love, tab_remedy = st.tabs(
        ["性格特質", "事業財運", "健康養生", "感情婚姻", "傳統化解"]
    )

    with tab_pers:
        _profile_box(sd["personality"], color)
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("**✅ 優勢**")
            for s in sd.get("strengths", []):
                st.markdown(f"- {s}")
        with col_w:
            st.markdown("**⚠️ 弱點**")
            for w in sd.get("weaknesses", []):
                st.markdown(f"- {w}")
        lcol1, lcol2 = st.columns(2)
        with lcol1:
            st.markdown(
                f"**幸運顏色:** "
                + "、".join(sd.get("lucky_colors", []))
            )
        with lcol2:
            st.markdown(
                f"**幸運數字:** "
                + "、".join(str(n) for n in sd.get("lucky_numbers", []))
            )

    with tab_career:
        _profile_box(sd["career"], color)

    with tab_health:
        _profile_box(sd["health"], color)

    with tab_love:
        _profile_box(sd["love"], color)

    with tab_remedy:
        _profile_box(sd["remedies"], color, icon="🙏")


def _profile_box(text: str, color: str, icon: str = "📖") -> None:
    st.markdown(
        f'<div style="background:{color}11;border-left:4px solid {color};'
        f'padding:12px 16px;border-radius:6px;color:white;font-size:14px;'
        f'line-height:1.7;">{icon} {text}</div>',
        unsafe_allow_html=True,
    )


def _render_house_table(chart: MahaboteChart) -> None:
    st.subheader("📊 八宮詳表")
    header = "| # | 宮位 | 緬甸文 | 含義 | 星期 | 行星 | 動物 | 描述 |"
    sep    = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|"
    rows   = [header, sep]
    for h in chart.houses:
        star  = "⭐" if h.is_birth_house else ""
        color = PLANET_COLORS.get(h.planet, "#888")
        p_html = (
            f'<span style="color:{color};font-weight:bold;">'
            f'{h.planet_symbol} {h.planet_cn}</span>'
        )
        rows.append(
            f"| {h.index} "
            f"| {star} {h.name_cn} ({h.name_en}) "
            f"| {h.name_myanmar} "
            f"| {h.meaning} "
            f"| {h.weekday_cn} "
            f"| {p_html} "
            f"| {h.animal_emoji} {h.animal_cn} "
            f"| {h.description} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_direction_omens(chart: MahaboteChart) -> None:
    st.subheader("🔮 八方位吉凶預兆")
    fortune_color = {**_QUALITY_COLOR, "凶中帶吉": "#FF8C00"}
    birth_dir = None
    for d in DIRECTIONS_8:
        if d["planet"] == chart.birth_planet:
            birth_dir = d
            break
    if birth_dir:
        fc = fortune_color.get(birth_dir["fortune"], "#888")
        color = PLANET_COLORS.get(birth_dir["planet"], "#888")
        st.markdown(
            f'<div style="background:{color}16;border:2px solid {color};'
            f'padding:14px;border-radius:10px;color:white;margin-bottom:10px;">'
            f'<h4 style="margin:0 0 6px 0;">⭐ 本命方位：'
            f'{birth_dir["dir_cn"]} — {birth_dir["planet_cn"]}</h4>'
            f'<span style="background:{fc};color:white;'
            f'padding:2px 10px;border-radius:4px;font-weight:bold;">'
            f'{birth_dir["fortune"]}</span>'
            f'<div style="margin-top:8px;">💼 {birth_dir["omen_career"]}</div>'
            f'<div>💕 {birth_dir["omen_marriage"]}</div>'
            f'<div>🏥 {birth_dir["omen_health"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with st.expander("📖 八方位完整預兆一覽"):
        for d in DIRECTIONS_8:
            is_b = d["planet"] == chart.birth_planet
            mk   = "⭐ " if is_b else ""
            c    = PLANET_COLORS.get(d["planet"], "#888")
            fc   = fortune_color.get(d["fortune"], "#888")
            st.markdown(
                f'**{mk}{d["dir_cn"]} ({d["dir_en"]})** '
                f'— <span style="color:{c};font-weight:bold;">'
                f'{d["planet_cn"]}</span> '
                f'<span style="background:{fc};color:white;'
                f'padding:1px 8px;border-radius:3px;font-size:12px;">'
                f'{d["fortune"]}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"  - 💼 {d['omen_career']}\n"
                f"  - 💕 {d['omen_marriage']}\n"
                f"  - 🏥 {d['omen_health']}"
            )


# ============================================================
# Tab 2 — 大運小運
# ============================================================

def _render_tab_periods(chart: MahaboteChart) -> None:
    # Major periods (Atar)
    st.subheader("📅 行星大運（Atar / Dasa）")
    st.markdown(
        "七星循環大運合計 **96 年**，從出生星期的行星開始，依序主宰人生各階段。"
    )

    header = "| 行星 | 動物 | 起始年齡 | 結束年齡 | 年數 | 當前 |"
    sep    = "|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows   = [header, sep]
    for p in chart.periods:
        if p.start_age > 110:
            break
        color   = PLANET_COLORS.get(p.planet, "#888")
        current = "👈 **現行大運**" if p.is_current else ""
        sd      = BIRTH_SIGN_DATA[p.sign_key]
        p_html  = (
            f'<span style="color:{color};font-weight:bold;">'
            f'{p.planet_symbol} {p.planet_cn}</span>'
        )
        rows.append(
            f"| {p_html} "
            f"| {sd['animal_emoji']} {sd['animal_cn']} "
            f"| {p.start_age} "
            f"| {p.end_age} "
            f"| {p.years} "
            f"| {current} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)
    _render_atar_timeline(chart)
    st.divider()

    # Current major period detail
    current_major = next((p for p in chart.periods if p.is_current), None)
    if current_major:
        color = PLANET_COLORS.get(current_major.planet, "#888")
        sd    = BIRTH_SIGN_DATA[current_major.sign_key]
        st.markdown(
            f'<div style="background:{color}20;border:2px solid {color};'
            f'padding:14px;border-radius:10px;color:white;">'
            f'<b>現行大運：{current_major.planet_symbol} '
            f'{current_major.planet_cn}（{current_major.start_age}–'
            f'{current_major.end_age} 歲）</b><br/>'
            f'{sd["animal_emoji"]} {sd["animal_cn"]} 守護 ｜ '
            f'方位：{BIRTH_SIGN_DATA[current_major.sign_key].get("direction_cn","")}<br/>'
            f'<span style="font-size:13px;">{sd["career"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Minor periods (annual)
    st.subheader("📆 年度小運（Annual Minor Periods）")
    st.markdown(
        "每年的小運依照**當前年齡 mod 8**推算，循環流轉於八宮之中。"
    )
    current_minor = next((m for m in chart.minor_periods if m.is_current), None)
    if current_minor:
        color = PLANET_COLORS.get(current_minor.planet, "#888")
        quality_color = _QUALITY_COLOR.get(current_minor.quality, "#888")
        st.markdown(
            f'<div style="background:{color}20;border:2px solid {color};'
            f'padding:12px;border-radius:10px;color:white;margin-bottom:10px;">'
            f'<b>本年小運（{current_minor.age} 歲）：'
            f'{current_minor.house_name_cn} 宮 — '
            f'{current_minor.planet_symbol} {current_minor.planet_cn}</b>'
            f'<span style="background:{quality_color};color:white;'
            f'padding:1px 8px;border-radius:3px;margin-left:8px;">'
            f'{current_minor.quality}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    header2 = "| 年齡 | 宮位 | 行星 | 動物 | 吉凶 | 當前 |"
    sep2    = "|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows2   = [header2, sep2]
    for m in chart.minor_periods:
        if m.age > 80:
            break
        color   = PLANET_COLORS.get(m.planet, "#888")
        current = "👈" if m.is_current else ""
        sd_m    = BIRTH_SIGN_DATA[m.sign_key]
        quality_color = _QUALITY_COLOR.get(m.quality, "#888")
        p_html  = (
            f'<span style="color:{color};font-weight:bold;">'
            f'{m.planet_symbol} {m.planet_cn}</span>'
        )
        q_html  = (
            f'<span style="background:{quality_color};color:white;'
            f'padding:1px 6px;border-radius:3px;font-size:12px;">'
            f'{m.quality}</span>'
        )
        rows2.append(
            f"| {m.age} "
            f"| {m.house_name_cn} "
            f"| {p_html} "
            f"| {sd_m['animal_emoji']} {sd_m['animal_cn']} "
            f"| {q_html} "
            f"| {current} |"
        )
    st.markdown("\n".join(rows2), unsafe_allow_html=True)


def _render_atar_timeline(chart: MahaboteChart) -> None:
    """Horizontal Atar period timeline bar."""
    max_age = 96
    html = (
        '<div style="display:flex;width:100%;height:36px;'
        'border-radius:6px;overflow:hidden;margin:10px 0;">'
    )
    for p in chart.periods:
        if p.start_age >= max_age:
            break
        end     = min(p.end_age, max_age)
        w_pct   = (end - p.start_age) / max_age * 100
        color   = PLANET_COLORS.get(p.planet, "#888")
        border  = "3px solid gold" if p.is_current else "none"
        html   += (
            f'<div style="width:{w_pct:.1f}%;background:{color};border:{border};'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:11px;color:white;font-weight:bold;min-width:20px;" '
            f'title="{p.planet_cn}: {p.start_age}–{end} 歲">'
            f'{p.planet_symbol}</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    st.caption("行星大運時間軸（0–96 歲），金框為現行大運")


# ============================================================
# Tab 3 — Year Chart 流年過運
# ============================================================

def _render_tab_year_chart(chart: MahaboteChart) -> None:
    st.subheader("🗓️ 流年盤（Year Chart）")
    st.markdown(
        "流年盤顯示特定年份的能量如何疊加在本命宮位上，"
        "以**當年年齡 mod 8** 推算流年起宮，再逐宮分析本命與流年的互動。"
    )

    current_year = date.today().year
    target_year = st.number_input(
        "選擇流年（年份）",
        min_value=chart.year,
        max_value=chart.year + 100,
        value=current_year,
        step=1,
        key="mahabote_year_chart_year",
    )

    entries = compute_year_chart_for_year(chart, int(target_year))
    age_in_year = int(target_year) - chart.year

    st.markdown(f"**{int(target_year)} 年流年盤** — 當年 {age_in_year} 歲，流年起宮 = {age_in_year % 8} 號宮位")
    st.divider()

    # Display as cards
    cols = st.columns(2)
    for i, entry in enumerate(entries):
        h_base    = chart.houses[entry.house_index]
        h_transit = chart.houses[(entry.house_index + age_in_year) % 8]
        base_c    = PLANET_COLORS.get(entry.base_planet, "#888")
        transit_c = PLANET_COLORS.get(entry.transit_planet, "#888")
        is_key    = h_base.is_birth_house

        card = (
            f'<div style="background:{"#2a2a4e" if is_key else "#1e1e36"};'
            f'border:{"3px solid gold" if is_key else "1px solid #555"};'
            f'padding:10px;border-radius:8px;color:white;margin-bottom:8px;'
            f'font-size:13px;">'
            f'<b>{"⭐ " if is_key else ""}{h_base.name_cn}</b><br/>'
            f'本命：<span style="color:{base_c};">{h_base.planet_symbol} {h_base.planet_cn}</span>'
            f' → 流年：<span style="color:{transit_c};">'
            f'{h_transit.planet_symbol} {h_transit.planet_cn}</span><br/>'
            f'<span style="font-size:12px;color:#ccc;">{entry.interaction}</span>'
            f'</div>'
        )
        with cols[i % 2]:
            st.markdown(card, unsafe_allow_html=True)

    st.divider()

    # Hostile aspects for this year
    if chart.hostile_aspects:
        st.subheader("⚠️ 敵對宮位提示")
        for p1, p2, note in chart.hostile_aspects:
            c1 = PLANET_COLORS.get(p1, "#888")
            c2 = PLANET_COLORS.get(p2, "#888")
            st.markdown(
                f'<div style="background:#2a1a1a;border-left:4px solid #DC143C;'
                f'padding:10px;border-radius:6px;color:white;margin-bottom:6px;">'
                f'<span style="color:{c1};font-weight:bold;">{p1}</span> ↔ '
                f'<span style="color:{c2};font-weight:bold;">{p2}</span>：{note}'
                f'</div>',
                unsafe_allow_html=True,
            )


# ============================================================
# Tab 4 — 合婚相容性
# ============================================================

def _render_tab_compatibility(chart: MahaboteChart) -> None:
    st.subheader("💑 合婚相容性（Mahabote Compatibility）")
    st.markdown(
        "輸入對方的出生資訊，依照古典緬甸 Mahabote 傳承計算雙方守護星的相容性。"
    )

    with st.form("mahabote_compat_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            p2_date = st.date_input(
                "對方出生日期",
                value=date(1990, 1, 1),
                key="mb_p2_date",
            )
        with col2:
            p2_hour = st.number_input("時 (0–23)", 0, 23, 12, key="mb_p2_h")
        with col3:
            p2_min  = st.number_input("分 (0–59)", 0, 59, 0, key="mb_p2_m")
        submitted = st.form_submit_button("✨ 計算合婚")

    if submitted:
        p2_y = p2_date.year
        p2_mo = p2_date.month
        p2_d  = p2_date.day

        # Compute second person's sign
        from .calculator import (
            _get_myanmar_year, _get_weekday, _local_solar_hour,
            _is_wednesday_evening, _get_sign_key,
        )
        p2_me  = _get_myanmar_year(p2_y, p2_mo, p2_d)
        p2_wd  = _get_weekday(p2_y, p2_mo, p2_d)
        p2_sol = _local_solar_hour(int(p2_hour), int(p2_min), chart.timezone, chart.longitude)
        p2_rahu = _is_wednesday_evening(p2_wd, p2_sol)
        p2_sign = _get_sign_key(p2_wd, p2_rahu)

        result = compute_compatibility(chart.sign_key, p2_sign)
        _render_compat_result(chart.sign_key, p2_sign, result)


def _render_compat_result(
    sign1: str,
    sign2: str,
    result: CompatibilityResult,
) -> None:
    sd1 = BIRTH_SIGN_DATA[sign1]
    sd2 = BIRTH_SIGN_DATA[sign2]
    c1  = PLANET_COLORS.get(result.person1_planet, "#888")
    c2  = PLANET_COLORS.get(result.person2_planet, "#888")
    pct = result.percent
    score_color = {
        5: "#FFD700", 4: "#32CD32", 3: "#87CEEB",
        2: "#FF8C00", 1: "#DC143C"
    }.get(result.score, "#888")

    st.markdown(
        f'<div style="background:#1e1e36;border:2px solid {score_color};'
        f'padding:18px;border-radius:12px;color:white;">'
        f'<div style="display:flex;justify-content:space-around;'
        f'align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:14px;">'

        f'<div style="text-align:center;">'
        f'<div style="font-size:28px;">{sd1["animal_emoji"]}</div>'
        f'<div style="font-size:14px;font-weight:bold;color:{c1};">'
        f'{sd1["animal_cn"]}</div>'
        f'<div style="font-size:12px;color:#ccc;">{sd1["planet_cn"]}</div>'
        f'</div>'

        f'<div style="text-align:center;font-size:40px;">{result.emoji}</div>'

        f'<div style="text-align:center;">'
        f'<div style="font-size:28px;">{sd2["animal_emoji"]}</div>'
        f'<div style="font-size:14px;font-weight:bold;color:{c2};">'
        f'{sd2["animal_cn"]}</div>'
        f'<div style="font-size:12px;color:#ccc;">{sd2["planet_cn"]}</div>'
        f'</div>'
        f'</div>'

        f'<div style="text-align:center;margin-bottom:12px;">'
        f'<span style="background:{score_color};color:white;'
        f'padding:4px 18px;border-radius:20px;font-size:16px;font-weight:bold;">'
        f'{result.label_cn} ({result.label_en}) — {pct}%</span>'
        f'</div>'

        f'<div style="margin-bottom:8px;">{result.description}</div>'
        + (
            f'<div style="background:#2a1a1a;border-left:4px solid #DC143C;'
            f'padding:8px 12px;border-radius:4px;font-size:13px;margin-top:8px;">'
            f'⚠️ {result.hostile_note}</div>'
            if result.hostile_note else ""
        )
        + f'</div>',
        unsafe_allow_html=True,
    )

    # Compatibility bar
    st.progress(pct / 100)

    # All-pairs overview
    with st.expander("📊 八星座完整相容性表"):
        _render_full_compat_table(sign1)


def _render_full_compat_table(my_sign: str) -> None:
    sd_me = BIRTH_SIGN_DATA[my_sign]
    header = "| 對方守護星 | 動物 | 相容性 | 類型 | 百分比 |"
    sep    = "|:---:|:---:|:---:|:---:|:---:|"
    rows   = [header, sep]
    for sk in list(WEEKDAY_TO_SIGN.values()) + ["Rahu"]:
        if sk == my_sign:
            continue
        sd_them = BIRTH_SIGN_DATA[sk]
        res = compute_compatibility(my_sign, sk)
        score_color = {
            5: "#FFD700", 4: "#32CD32", 3: "#87CEEB",
            2: "#FF8C00", 1: "#DC143C"
        }.get(res.score, "#888")
        c = PLANET_COLORS.get(res.person2_planet, "#888")
        rows.append(
            f"| <span style='color:{c};font-weight:bold;'>"
            f"{sd_them['planet_cn']}</span> "
            f"| {sd_them['animal_emoji']} {sd_them['animal_cn']} "
            f"| <span style='background:{score_color};color:white;"
            f"padding:1px 8px;border-radius:3px;'>{res.label_cn}</span> "
            f"| {res.label_en} "
            f"| {res.percent}% |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


# ============================================================
# Tab 5 — 撣族文化
# ============================================================

def _render_tab_shan(chart: MahaboteChart) -> None:
    st.subheader("🎋 撣族文化與 Mahabote 傳承（Shan / Tai Yai Culture）")

    sd = chart.sign_profile
    me_year = chart.myanmar_year
    shan_y  = chart.shan_year

    # Cultural intro
    st.markdown(
        f'<div style="background:#1e2e1e;border-left:4px solid #4CAF50;'
        f'padding:14px;border-radius:8px;color:white;margin-bottom:14px;">'
        f'<h4 style="margin:0 0 6px 0;">📖 Mahabote 起源與撣族聯繫</h4>'
        f'<p style="margin:0;font-size:13px;line-height:1.7;">'
        f'Mahabote（မဟာဘုတ်）源自古緬甸與印度天文-占星融合，意為「大創造」或「大決定」。'
        f'撣族（Shan / Tai Yai）作為緬甸最大的少數民族，深受緬甸曆法文化影響，'
        f'同時保有源自傣系（Tai）文明的獨特天文傳統。'
        f'撣族使用與緬甸紀年相近的曆法（撣曆 ≈ 緬甸紀年 − 450），'
        f'並在星期守護星、動物象徵和方位信仰上有其獨特的詮釋。'
        f'</p></div>',
        unsafe_allow_html=True,
    )

    # Calendar section
    st.markdown(f"**緬甸紀年 (ME)：** {me_year} ｜ **撣曆年（近似）：** {shan_y}")
    st.markdown(f"*{SHAN_CALENDAR_INFO['shan_year_note']}*")
    st.divider()

    # Personal Shan note
    shan_note = sd.get("shan_note", "")
    if shan_note:
        color = PLANET_COLORS.get(chart.birth_planet, "#888")
        st.markdown(
            f'<div style="background:{color}14;border:1px solid {color}55;'
            f'padding:14px;border-radius:8px;color:white;margin-bottom:12px;">'
            f'<b>{sd["animal_emoji"]} 您的守護星——撣族文化視角</b><br/>'
            f'<p style="margin:6px 0 0 0;font-size:13px;line-height:1.7;">'
            f'{shan_note}</p></div>',
            unsafe_allow_html=True,
        )

    # Direction beliefs
    st.subheader("🏠 撣族方位與建築信仰")
    st.markdown(SHAN_CALENDAR_INFO["shan_direction_beliefs"])
    st.divider()

    # Festivals
    st.subheader("🎉 撣族重要節日")
    for fest in SHAN_CALENDAR_INFO["festivals"]:
        st.markdown(
            f'<div style="background:#1e1e2e;border-left:4px solid #4169E1;'
            f'padding:10px 14px;border-radius:6px;color:white;margin-bottom:8px;">'
            f'<b>{fest["name_shan"]}</b> — {fest["name_cn"]}'
            f' （{fest["month"]} 月）<br/>'
            f'<span style="font-size:13px;color:#ccc;">{fest["note"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.divider()

    # Name giving
    st.subheader("📛 撣族命名傳統")
    st.info(SHAN_CALENDAR_INFO["name_giving"])

    # Cultural intro section
    st.divider()
    st.subheader("🔬 研究參考資料")
    st.markdown(
        """
**古典文獻與參考來源：**
- Barbara Cameron, *The Little Key* — 最廣為流傳的英文 Mahabote 入門手冊
- Myanmar Traditional Astrology Manuals (Pali-Burmese manuscript tradition)
- U Thaw Kaung, Burmese Calendar Studies, Myanmar Encyclopedia Commission
- สุจิตต์ วงษ์เทศ (Sujit Wongtes), *ปฏิทินไทย-ไท* — 傣系曆法比較研究
- Sao Saimong Mangrai, *The Padaeng Chronicle and the Jengtung State Chronicle* — 撣族史料
        """
    )


# ============================================================
# 主渲染入口 (Main Entry)
# ============================================================

def render_streamlit(
    chart: MahaboteChart,
    after_chart_hook=None,
) -> None:
    """Render the complete Burmese / Shan Mahabote deep astrology page.

    Parameters
    ----------
    chart : MahaboteChart
        Computed Mahabote chart from calculator.compute_mahabote_chart().
    after_chart_hook : callable, optional
        Called after the main chart render (used by app.py for AI button).
    """
    # Page title
    color = PLANET_COLORS.get(chart.birth_planet, "#888")
    st.markdown(
        f'<h2 style="color:{color};margin-bottom:4px;">'
        f'{chart.birth_planet_symbol} '
        f'緬甸／撣族 Mahabote 深度占星</h2>'
        f'<p style="color:#aaa;font-size:13px;margin-top:0;">'
        f'Burmese / Shan Mahabote Deep Astrology · မဟာဘုတ်</p>',
        unsafe_allow_html=True,
    )

    if after_chart_hook:
        after_chart_hook()

    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏛️ 本命排盤",
        "📅 大運小運",
        "🗓️ Year Chart",
        "💑 合婚",
        "🎋 撣族文化",
    ])

    with tab1:
        _render_tab_natal(chart)

    with tab2:
        _render_tab_periods(chart)

    with tab3:
        _render_tab_year_chart(chart)

    with tab4:
        _render_tab_compatibility(chart)

    with tab5:
        _render_tab_shan(chart)


# ── Backward-compatible alias (matches app.py's import) ───────────────────
render_mahabote_chart = render_streamlit
