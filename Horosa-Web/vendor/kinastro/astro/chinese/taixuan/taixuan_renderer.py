# -*- coding: utf-8 -*-
"""
taixuan_renderer.py — 太玄數占星 Streamlit 前端頁面
提供極致美觀的太玄 UI：本命排盤 + 即時問卜 + 行年時間軸 + AI 解讀
"""

from __future__ import annotations

import math
from typing import Optional, Dict, List
import streamlit as st

from .taixuan_calculator import (
    TaiXuanCalculator,
    TaiXuanResult,
    TaiXuanShou,
    ZHAN_NAMES,
    TWENTY_EIGHT_MANSIONS,
    TOTAL_SHOU_COUNT,
    _SORTED_KEYS,
    _TAIXUAN_DICT,
    _DEGREE_TO_ZH,
    _key_to_name,
)

# ── 色彩常數 ────────────────────────────────────────────────
_GOLD = "#C9A84C"
_GOLD_DIM = "rgba(201,168,76,0.18)"
_GOLD_BORDER = "rgba(201,168,76,0.45)"
_PURPLE = "#A78BFA"
_PURPLE_DIM = "rgba(167,139,250,0.12)"
_CYAN = "#38BDF8"
_CYAN_DIM = "rgba(56,189,248,0.10)"
_RED = "#F87171"
_RED_DIM = "rgba(248,113,113,0.10)"
_BG_DARK = "rgba(10,10,20,0.95)"

# 顯示常數
_MAX_ANNUAL_DISPLAY_YEARS: int = 18    # 聯動表最多顯示的行年數
_MAX_TEXT_DISPLAY_LENGTH: int = 30     # 完整表格卦辭截斷長度

# 方位顏色（三方：天/地/人）
_FANG_COLORS = {
    "一方": "#EAB308",   # 黃金（天）
    "二方": "#A78BFA",   # 紫（人）
    "三方": "#38BDF8",   # 青（地）
}


# ── SVG 太玄九宮圖 ───────────────────────────────────────────

def build_taixuan_svg(result: TaiXuanResult, width: int = 560) -> str:
    """
    渲染太玄 81 首九宮格 SVG，以 9×9 格顯示所有首，
    高亮命宮首，深色占星質感，漸層背景。
    """
    cell_size = width // 9
    height = cell_size * 9 + 60   # 頂部留 60px 標題
    serial = result.shou.serial

    _LEGEND_H = 30   # dedicated legend area below the grid
    height += _LEGEND_H

    svg_parts: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="auto" '
        f'viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet" '
        f'style="display:block;background:#080818;border-radius:16px;font-family:\'Noto Serif TC\',serif;">',
        # 漸層定義
        "<defs>",
        "<radialGradient id='bg-grad' cx='50%' cy='50%' r='70%'>",
        f"  <stop offset='0%' stop-color='#1a1040' stop-opacity='1'/>",
        f"  <stop offset='100%' stop-color='#06060f' stop-opacity='1'/>",
        "</radialGradient>",
        "<linearGradient id='active-grad' x1='0%' y1='0%' x2='100%' y2='100%'>",
        f"  <stop offset='0%' stop-color='{_GOLD}' stop-opacity='0.9'/>",
        f"  <stop offset='100%' stop-color='#FF8C42' stop-opacity='0.7'/>",
        "</linearGradient>",
        "<filter id='glow'>",
        "  <feGaussianBlur stdDeviation='3' result='coloredBlur'/>",
        "  <feMerge><feMergeNode in='coloredBlur'/><feMergeNode in='SourceGraphic'/></feMerge>",
        "</filter>",
        "</defs>",
        # 背景
        f'<rect width="{width}" height="{height}" fill="url(#bg-grad)"/>',
        # 標題
        f'<text x="{width//2}" y="38" text-anchor="middle" '
        f'font-size="18" font-weight="700" fill="{_GOLD}" '
        f'font-family="Noto Serif TC,serif" letter-spacing="4">'
        f'太玄八十首命宮星盤</text>',
    ]

    # 九宮格
    for row in range(9):
        for col in range(9):
            idx = row * 9 + col
            if idx >= len(_SORTED_KEYS):
                break
            key = _SORTED_KEYS[idx]
            cell_serial = idx + 1
            x = col * cell_size
            y = 60 + row * cell_size
            cs = cell_size

            # 卦名
            gua_dict = _TAIXUAN_DICT.get(key, {}).get("卦", {})
            gua_title = next(iter(gua_dict.keys()), "")

            # 命宮高亮
            is_active = (cell_serial == serial)
            fill_color = "url(#active-grad)" if is_active else f"rgba(255,255,255,{0.03 if (row+col)%2==0 else 0.01})"
            stroke_color = _GOLD if is_active else "rgba(201,168,76,0.15)"
            stroke_w = "2" if is_active else "0.5"
            text_color = "#080818" if is_active else _GOLD
            serial_color = "#080818" if is_active else "rgba(201,168,76,0.45)"
            glow_filter = 'filter="url(#glow)"' if is_active else ""

            # 方位顏色標記
            fang = int(str(key)[0])
            fang_colors = ["", "#EAB308", "#A78BFA", "#38BDF8"]
            dot_color = fang_colors[fang] if fang < len(fang_colors) else _GOLD

            svg_parts += [
                f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" '
                f'fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_w}" '
                f'rx="3" {glow_filter}/>',
                # 序號
                f'<text x="{x+5}" y="{y+14}" font-size="9" fill="{serial_color}" '
                f'font-family="sans-serif">{cell_serial}</text>',
                # 方位色點
                f'<circle cx="{x+cs-8}" cy="{y+8}" r="3" fill="{dot_color}" opacity="0.7"/>',
                # 卦名（居中，主要文字）
                f'<text x="{x+cs//2}" y="{y+cs//2+6}" '
                f'text-anchor="middle" font-size="14" font-weight="{"700" if is_active else "400"}" '
                f'fill="{text_color}" font-family="Noto Serif TC,serif">{gua_title}</text>',
            ]
            if is_active:
                # 加上發光外框
                svg_parts.append(
                    f'<rect x="{x+1}" y="{y+1}" width="{cs-2}" height="{cs-2}" '
                    f'fill="none" stroke="{_GOLD}" stroke-width="2.5" rx="3" opacity="0.8"/>'
                )

    # 圖例
    legend_y = height - 14
    legend_items = [
        ("命宮首", _GOLD, "url(#active-grad)"),
        ("天方", "#EAB308", "#EAB308"),
        ("人方", "#A78BFA", "#A78BFA"),
        ("地方", "#38BDF8", "#38BDF8"),
    ]
    lx = 10
    for label, color, dot_fill in legend_items:
        svg_parts += [
            f'<circle cx="{lx+6}" cy="{legend_y}" r="5" fill="{dot_fill}" opacity="0.85"/>',
            f'<text x="{lx+14}" y="{legend_y+4}" font-size="10" fill="{color}" '
            f'font-family="Noto Serif TC,serif">{label}</text>',
        ]
        lx += len(label) * 10 + 25

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


# ── 九贊圓形雷達圖 SVG ───────────────────────────────────────

def build_zhan_radar_svg(shou: TaiXuanShou, size: int = 320) -> str:
    """渲染九贊雷達圖（9 邊形，顯示當值贊）"""
    cx = size // 2
    cy = size // 2
    r = size // 2 - 48
    n = 9
    active_idx = ZHAN_NAMES.index(shou.zhan_name) if shou.zhan_name in ZHAN_NAMES else 0

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}" '
        f'style="display:block;background:#080818;border-radius:50%;">',
        "<defs>",
        f"<radialGradient id='zhan-bg' cx='50%' cy='50%' r='50%'>",
        f"  <stop offset='0%' stop-color='#1a1040'/>",
        f"  <stop offset='100%' stop-color='#06060f'/>",
        "</radialGradient>",
        "</defs>",
        f'<circle cx="{cx}" cy="{cy}" r="{r+40}" fill="url(#zhan-bg)"/>',
    ]

    # 同心圓
    for level in range(1, 4):
        lr = r * level / 3
        svg_parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{lr}" '
            f'fill="none" stroke="rgba(201,168,76,0.12)" stroke-width="0.8"/>'
        )

    # 從中心到頂點的輻射線 + 頂點標籤
    points_outer: List[tuple] = []
    for i in range(n):
        angle = math.pi * 2 * i / n - math.pi / 2
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        points_outer.append((px, py))
        # 輻射線
        svg_parts.append(
            f'<line x1="{cx}" y1="{cy}" x2="{px:.1f}" y2="{py:.1f}" '
            f'stroke="rgba(201,168,76,0.18)" stroke-width="0.8"/>'
        )
        # 贊名標籤
        lx = cx + (r + 24) * math.cos(angle)
        ly = cy + (r + 24) * math.sin(angle)
        is_active = (i == active_idx)
        fill_c = _GOLD if is_active else "rgba(201,168,76,0.55)"
        fw = "700" if is_active else "400"
        fs = "14" if is_active else "11"
        svg_parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'font-size="{fs}" font-weight="{fw}" fill="{fill_c}" '
            f'font-family="Noto Serif TC,serif" dominant-baseline="middle">'
            f'{ZHAN_NAMES[i]}</text>'
        )
        # 活躍點
        dot_r = 7 if is_active else 4
        dot_fill = _GOLD if is_active else "rgba(201,168,76,0.4)"
        svg_parts.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{dot_r}" fill="{dot_fill}"/>'
        )

    # 多邊形填充
    pts_str = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in points_outer)
    svg_parts.append(
        f'<polygon points="{pts_str}" '
        f'fill="rgba(201,168,76,0.05)" stroke="rgba(201,168,76,0.35)" stroke-width="1"/>'
    )

    # 中心卦名
    svg_parts += [
        f'<text x="{cx}" y="{cy-6}" text-anchor="middle" '
        f'font-size="22" font-weight="700" fill="{_GOLD}" '
        f'font-family="Noto Serif TC,serif">{shou.gua_title}</text>',
        f'<text x="{cx}" y="{cy+16}" text-anchor="middle" '
        f'font-size="10" fill="rgba(201,168,76,0.6)" '
        f'font-family="Noto Serif TC,serif">命宮首</text>',
        "</svg>",
    ]
    return "\n".join(svg_parts)


# ── 行年時間軸 (Plotly) ──────────────────────────────────────

def render_annual_timeline(result: TaiXuanResult) -> None:
    """使用 Plotly 渲染太玄行年大限時間軸"""
    try:
        import plotly.graph_objects as go
    except ImportError:
        st.warning("需要安裝 plotly：`pip install plotly`")
        return

    data = result.annual_shou_list
    if not data:
        st.info("無行年大限資料")
        return

    years = [d["年份"] for d in data]
    serials = [d["首序"] for d in data]
    names = [d["首卦名"] for d in data]
    ganzhi = [d["年干支"] for d in data]
    ages = [d["年齡"] for d in data]

    # 重要首（每 9 首一個大限節點）
    major_indices = [i for i in range(len(data)) if data[i]["年齡"] % 9 == 0]

    fig = go.Figure()

    # 主線
    fig.add_trace(go.Scatter(
        x=years,
        y=serials,
        mode="lines+markers",
        line=dict(color=_GOLD, width=2),
        marker=dict(
            color=[_GOLD if i in major_indices else "rgba(201,168,76,0.4)" for i in range(len(data))],
            size=[10 if i in major_indices else 5 for i in range(len(data))],
            symbol="diamond",
        ),
        text=[f"{ganzhi[i]}年 · 首{serials[i]} · {names[i]}" for i in range(len(data))],
        hovertemplate="%{text}<br>年份：%{x}<extra></extra>",
        name="行年大限",
    ))

    # 命宮首的出生年標注
    if result.birth_dt:
        birth_year = result.birth_dt.year
        if birth_year in years:
            birth_idx = years.index(birth_year)
            fig.add_vline(
                x=birth_year,
                line_dash="dot",
                line_color=_GOLD,
                annotation_text="出生年",
                annotation_font_color=_GOLD,
            )

    fig.update_layout(
        title=dict(
            text="太玄行年大限時間軸",
            font=dict(color=_GOLD, size=16, family="Noto Serif TC"),
        ),
        plot_bgcolor="rgba(8,8,24,0.98)",
        paper_bgcolor="rgba(8,8,24,0.98)",
        xaxis=dict(
            title="年份",
            color="rgba(201,168,76,0.6)",
            gridcolor="rgba(201,168,76,0.1)",
            linecolor="rgba(201,168,76,0.3)",
        ),
        yaxis=dict(
            title="首序號",
            color="rgba(201,168,76,0.6)",
            gridcolor="rgba(201,168,76,0.08)",
            range=[0, 82],
        ),
        font=dict(color="rgba(201,168,76,0.7)", family="Noto Serif TC"),
        hoverlabel=dict(
            bgcolor="#1a1040",
            font_color=_GOLD,
            bordercolor=_GOLD_BORDER,
        ),
        margin=dict(l=50, r=20, t=50, b=40),
        height=360,
    )
    st.plotly_chart(fig, width="stretch")


# ── 主頁渲染函數 ─────────────────────────────────────────────

def render_taixuan_chart(result: TaiXuanResult, after_chart_hook=None) -> None:
    """渲染完整太玄排盤介面"""
    shou = result.shou
    lang = st.session_state.get("lang", "zh")
    is_en = (lang == "en")

    # ── 頁首卡片 ────────────────────────────────────────────
    mode_label = "本命排盤" if result.mode == "natal" else "即時問卜"
    mode_label_en = "Natal Chart" if result.mode == "natal" else "Divination"
    date_str = result.birth_dt.strftime("%Y年%m月%d日 %H時") if result.birth_dt else "——"

    st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#120828 0%,#0a1428 60%,#0d0820 100%);
    border:1px solid {_GOLD_BORDER};
    border-radius:18px;padding:24px 28px 20px 28px;
    margin-bottom:20px;
">
  <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
    <div style="font-size:52px;line-height:1;">☰</div>
    <div style="flex:1;">
      <div style="font-size:10px;color:rgba(201,168,76,0.55);letter-spacing:3px;text-transform:uppercase;">
        {'Tai Xuan Shu Astrology' if is_en else '太玄數占星'}
      </div>
      <div style="font-size:26px;font-weight:800;color:{_GOLD};letter-spacing:2px;margin:2px 0;">
        {shou.gua_title}&ensp;·&ensp;{shou.name}
      </div>
      <div style="font-size:12px;color:rgba(201,168,76,0.6);">
        {'Serial' if is_en else '首序'}：#{shou.serial}&ensp;｜&ensp;
        {'Mode' if is_en else '模式'}：{mode_label_en if is_en else mode_label}&ensp;｜&ensp;
        {date_str}
      </div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:28px;color:{_GOLD};font-weight:700;">{shou.zhan_name}</div>
      <div style="font-size:11px;color:rgba(201,168,76,0.5);">
        {'Active Praise' if is_en else '當值贊'}
      </div>
      <div style="margin-top:6px;font-size:11px;color:rgba(167,139,250,0.8);">
        {shou.sishi}&ensp;·&ensp;{shou.mansion}宿{_DEGREE_TO_ZH.get(shou.mansion_degree, str(shou.mansion_degree))}度&ensp;·&ensp;{shou.planet}
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── 三欄核心資訊 ─────────────────────────────────────────
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        # 九宮星盤 SVG
        svg_chart = build_taixuan_svg(result)
        st.components.v1.html(
            f'<div style="background:#080818;border-radius:16px;width:100%;max-width:560px;">{svg_chart}</div>',
            height=700,
        )
    with c2:
        # 九贊雷達圖
        radar_svg = build_zhan_radar_svg(shou)
        st.components.v1.html(
            f'<div style="background:#080818;border-radius:50%;width:100%;display:flex;justify-content:center;">{radar_svg}</div>',
            height=360,
        )
        # 干支四柱（本命模式）
        if result.mode == "natal":
            _render_ganzhi_card(result, is_en)
    with c3:
        _render_shou_detail_card(shou, is_en)

    st.divider()

    # ── 首辭全文 & 九贊展開 ─────────────────────────────────
    _render_all_zhan(shou, is_en)

    st.divider()

    # ── 行年大限時間軸 ───────────────────────────────────────
    if result.mode == "natal" and result.annual_shou_list:
        st.markdown(
            f'<div style="font-size:16px;font-weight:700;color:{_GOLD};'
            f'letter-spacing:2px;margin-bottom:12px;">📅 行年大限 · Annual Limit</div>',
            unsafe_allow_html=True,
        )
        render_annual_timeline(result)
        st.divider()

    # ── 干支七政聯動表 ───────────────────────────────────────
    if result.mode == "natal":
        _render_linkage_table(result, is_en)
        st.divider()

    # ── 完整 81 首參考表 ─────────────────────────────────────
    with st.expander(
        "📖 完整八十首參考表 · Full 80-Shou Reference Table",
        expanded=False,
    ):
        _render_full_table(result.all_shou_table, shou.serial, is_en)

    # ── AI 分析鉤子 ──────────────────────────────────────────
    if after_chart_hook:
        after_chart_hook()


def _render_ganzhi_card(result: TaiXuanResult, is_en: bool) -> None:
    """渲染干支四柱卡片"""
    gz_rows = [
        ("年柱", result.year_gz, result.wuxing_year[:1] if result.wuxing_year else ""),
        ("月柱", result.month_gz, ""),
        ("日柱", result.day_gz, result.wuxing_day[:1] if result.wuxing_day else ""),
        ("時柱", result.hour_gz, ""),
    ]
    labels_en = ["Year", "Month", "Day", "Hour"]
    html_items = ""
    for i, (name, gz, wx) in enumerate(gz_rows):
        label = labels_en[i] if is_en else name
        wx_badge = f'<span style="font-size:9px;color:rgba(56,189,248,0.8);margin-left:4px;">{wx}</span>' if wx else ""
        html_items += f"""
<div style="flex:1 1 70px;min-width:64px;text-align:center;
    background:{_GOLD_DIM};border:1px solid {_GOLD_BORDER};
    border-radius:10px;padding:10px 6px;">
  <div style="font-size:10px;color:rgba(201,168,76,0.5);margin-bottom:4px;">{label}</div>
  <div style="font-size:20px;font-weight:700;color:{_GOLD};">{gz}{wx_badge}</div>
</div>"""
    st.markdown(
        f'<div style="margin-top:14px;">'
        f'<div style="font-size:12px;color:rgba(201,168,76,0.6);margin-bottom:8px;">干支四柱</div>'
        f'<div style="display:flex;gap:6px;flex-wrap:wrap;">{html_items}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_shou_detail_card(shou: TaiXuanShou, is_en: bool) -> None:
    """渲染首辭詳情卡片"""
    st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#0e0820 0%,#0a1020 100%);
    border:1px solid {_GOLD_BORDER};
    border-radius:14px;padding:18px 16px;height:100%;
">
  <div style="font-size:11px;color:rgba(201,168,76,0.5);letter-spacing:2px;margin-bottom:6px;">
    {'Shou Title' if is_en else '首名'}
  </div>
  <div style="font-size:20px;font-weight:800;color:{_GOLD};margin-bottom:2px;">
    {shou.name}
  </div>
  <div style="font-size:26px;font-weight:700;color:#EAB308;margin:8px 0 6px 0;">
    {shou.gua_title}
  </div>
  <div style="font-size:13px;color:rgba(224,224,255,0.75);line-height:1.8;margin-bottom:14px;">
    {shou.gua_text}
  </div>
  <hr style="border-color:rgba(201,168,76,0.15);margin:12px 0;"/>
  <div style="font-size:11px;color:rgba(201,168,76,0.5);margin-bottom:4px;">
    {'Active Zhan' if is_en else '當值贊'} — {shou.zhan_name}
  </div>
  <div style="font-size:13px;color:rgba(224,224,255,0.85);line-height:1.8;">
    {shou.zhan_text}
  </div>
  <hr style="border-color:rgba(201,168,76,0.15);margin:12px 0;"/>
  <div style="display:flex;gap:8px;flex-wrap:wrap;">
    <div style="background:{_PURPLE_DIM};border:1px solid rgba(167,139,250,0.3);
         border-radius:8px;padding:6px 12px;font-size:11px;color:{_PURPLE};">
      {shou.sishi}
    </div>
    <div style="background:{_CYAN_DIM};border:1px solid rgba(56,189,248,0.3);
         border-radius:8px;padding:6px 12px;font-size:11px;color:{_CYAN};">
      {shou.mansion}宿{_DEGREE_TO_ZH.get(shou.mansion_degree, str(shou.mansion_degree))}度
    </div>
    <div style="background:{_GOLD_DIM};border:1px solid {_GOLD_BORDER};
         border-radius:8px;padding:6px 12px;font-size:11px;color:{_GOLD};">
      {shou.planet}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


def _render_all_zhan(shou: TaiXuanShou, is_en: bool) -> None:
    """渲染九贊全文展開"""
    st.markdown(
        f'<div style="font-size:16px;font-weight:700;color:{_GOLD};'
        f'letter-spacing:2px;margin-bottom:12px;">☰ 九贊全文 · Nine Praises</div>',
        unsafe_allow_html=True,
    )
    items_html = ""
    for zn in ZHAN_NAMES:
        is_active = (zn == shou.zhan_name)
        text = shou.all_zhan.get(zn, "")
        border = _GOLD_BORDER if is_active else "rgba(201,168,76,0.12)"
        bg = _GOLD_DIM if is_active else "rgba(255,255,255,0.02)"
        label_color = _GOLD if is_active else "rgba(201,168,76,0.5)"
        active_badge = (
            f' <span style="font-size:9px;color:{_GOLD};'
            f'background:rgba(201,168,76,0.2);border-radius:4px;padding:1px 5px;">當值</span>'
            if is_active else ""
        )
        items_html += f"""
<div style="background:{bg};border:1px solid {border};
    border-radius:10px;padding:12px 14px;">
  <div style="font-size:12px;font-weight:700;color:{label_color};margin-bottom:6px;">
    {zn}{active_badge}
  </div>
  <div style="font-size:12px;color:rgba(220,220,240,0.75);line-height:1.7;">{text}</div>
</div>"""
    st.markdown(
        f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));'
        f'gap:10px;margin-bottom:10px;">{items_html}</div>',
        unsafe_allow_html=True,
    )


def _render_linkage_table(result: TaiXuanResult, is_en: bool) -> None:
    """渲染太玄↔干支↔七政聯動表"""
    import pandas as pd
    st.markdown(
        f'<div style="font-size:16px;font-weight:700;color:{_GOLD};'
        f'letter-spacing:2px;margin-bottom:12px;">🔗 太玄↔干支↔七政聯動 · Cross-System Linkage</div>',
        unsafe_allow_html=True,
    )
    rows = []
    for d in result.annual_shou_list[:_MAX_ANNUAL_DISPLAY_YEARS]:   # 顯示前 N 年
        rows.append({
            "年份" if not is_en else "Year": d["年份"],
            "年干支" if not is_en else "GanZhi": d["年干支"],
            "首序" if not is_en else "Shou#": d["首序"],
            "首名" if not is_en else "Name": d["首卦名"],
            "五行" if not is_en else "Element": d["五行"],
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def _render_full_table(all_table: List[Dict], active_serial: int, is_en: bool) -> None:
    """渲染完整 80 首參考表"""
    import pandas as pd
    rows = []
    for d in all_table:
        rows.append({
            "序" if not is_en else "#": d["序"],
            "首名" if not is_en else "Name": d["首名"],
            "卦名" if not is_en else "Gua": d["卦名"],
            "卦辭" if not is_en else "Text": d["卦辭"][:_MAX_TEXT_DISPLAY_LENGTH] + "…" if len(d["卦辭"]) > _MAX_TEXT_DISPLAY_LENGTH else d["卦辭"],
            "二十八宿" if not is_en else "Mansion": d["二十八宿"],
            "七政" if not is_en else "Planet": d["七政"],
        })
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, hide_index=True, width="stretch")


# ── 未起盤時的介紹卡片 ───────────────────────────────────────

def render_taixuan_intro() -> None:
    """顯示太玄數介紹卡片（未起盤時）"""
    st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#0e0828 0%,#0a1428 100%);
    border:1px solid {_GOLD_BORDER};
    border-radius:18px;
    padding:32px 28px 28px 28px;
    margin-bottom:20px;
    text-align:center;
">
  <div style="font-size:58px;margin-bottom:14px;">☰</div>
  <div style="font-size:26px;font-weight:800;color:{_GOLD};letter-spacing:3px;margin-bottom:6px;">
    太玄數占星
  </div>
  <div style="font-size:12px;color:rgba(201,168,76,0.5);margin-bottom:16px;letter-spacing:2px;">
    Tai Xuan Shu Astrology &middot; 揚雄《太玄》八十首
  </div>
  <div style="font-size:13px;color:rgba(200,200,220,0.75);line-height:1.9;
       max-width:460px;margin:0 auto 22px auto;">
    太玄數源自西漢揚雄《太玄經》，模仿《易》而作，以三才（天地人）三分取象，<br>
    八十一首×九贊，配二十八宿、七政四餘，是中國最獨特的三進制宇宙哲學體系。<br>
    支援<strong style="color:{_GOLD};">本命排盤</strong>（依出生年月日時推命宮首）
    與<strong style="color:{_GOLD};">即時問卜</strong>（蓍草亂數求首）雙模式。
  </div>
  <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-bottom:20px;">
    <div style="background:{_GOLD_DIM};border:1px solid {_GOLD_BORDER};
         border-radius:8px;padding:7px 14px;font-size:12px;color:{_GOLD};">
      📅 輸入出生年月日時
    </div>
    <div style="background:{_GOLD_DIM};border:1px solid {_GOLD_BORDER};
         border-radius:8px;padding:7px 14px;font-size:12px;color:{_GOLD};">
      ☰ 推算命宮首 &amp; 九贊
    </div>
    <div style="background:{_GOLD_DIM};border:1px solid {_GOLD_BORDER};
         border-radius:8px;padding:7px 14px;font-size:12px;color:{_GOLD};">
      🔗 干支七政聯動
    </div>
    <div style="background:{_GOLD_DIM};border:1px solid {_GOLD_BORDER};
         border-radius:8px;padding:7px 14px;font-size:12px;color:{_GOLD};">
      📊 行年大限時間軸
    </div>
  </div>
  <div style="
    display:inline-block;
    background:rgba(205,46,58,0.12);
    border:1px solid rgba(205,46,58,0.35);
    border-radius:8px;
    padding:8px 22px;
    font-size:13px;
    color:#f87171;
  ">👈 請在左側填寫出生年月日時，即可起盤</div>
</div>""", unsafe_allow_html=True)


# ── 即時問卜 UI ──────────────────────────────────────────────

def render_qigua_ui(after_chart_hook=None) -> None:
    """即時問卜：蓍草亂數求首介面"""
    lang = st.session_state.get("lang", "zh")
    is_en = (lang == "en")

    st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#0e0820 0%,#0a1428 100%);
    border:1px solid {_GOLD_BORDER};
    border-radius:16px;padding:22px 24px 18px 24px;margin-bottom:18px;
">
  <div style="font-size:22px;font-weight:700;color:{_GOLD};letter-spacing:2px;margin-bottom:8px;">
    🎴 即時問卜 · Real-Time Divination
  </div>
  <div style="font-size:13px;color:rgba(200,200,220,0.7);line-height:1.8;">
    以太玄蓍草策數法（三分法），<br>搖出命運之首與當下贊辭。
  </div>
</div>
""", unsafe_allow_html=True)

    question = st.text_input(
        "請輸入您的問題（可留空）" if not is_en else "Enter your question (optional)",
        placeholder="如：事業、感情、財運……" if not is_en else "e.g. career, love, finance...",
        key="_taixuan_qigua_question",
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button(
            "🎴 搖卦問卜" if not is_en else "🎴 Cast Divination",
            type="primary",
            width="stretch",
            key="_taixuan_qigua_btn",
        ):
            with st.spinner("蓍草演算中……"):
                calc = TaiXuanCalculator(mode="qigua")
                result = calc.calculate()
                st.session_state["_taixuan_qigua_result"] = result
                st.session_state["_taixuan_qigua_question_val"] = question

    qigua_result: Optional[TaiXuanResult] = st.session_state.get("_taixuan_qigua_result")
    if qigua_result:
        q_val = st.session_state.get("_taixuan_qigua_question_val", "")
        if q_val:
            st.markdown(
                f'<div style="font-size:13px;color:{_PURPLE};margin-bottom:12px;">'
                f'✦ 問題：{q_val}</div>',
                unsafe_allow_html=True,
            )
        render_taixuan_chart(qigua_result, after_chart_hook=after_chart_hook)
