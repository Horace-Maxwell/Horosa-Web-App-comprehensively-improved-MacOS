# -*- coding: utf-8 -*-
"""
astro/bazi/renderer.py — 子平八字 Streamlit 渲染模組 + 傳統命盤 SVG
Ziping Bazi — Streamlit Renderer & Traditional Chart SVG

SVG 視覺風格：
  - 仿古宣紙質感（米白底色 + 細微水墨渲染）
  - 書法字體（Noto Serif SC）
  - 朱印風格印章（圓形與方形，鮮豔朱砂紅）
  - 傳統四柱命盤排版（年｜月｜日｜時）
  - 整體呈現明清時期手寫命書風格
"""
from __future__ import annotations

import textwrap
from datetime import date
from typing import Any, Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components

from astro.i18n import auto_cn, t

from .calculator import BaziChart, DayunStep, compute_bazi, _get_kongwang
from .constants import (
    SHISHEN_COLORS,
    SVG_BORDER_COLOR,
    SVG_INK_DARK,
    SVG_PAPER_BG,
    SVG_SEAL_RED,
    SVG_SUBTITLE_COLOR,
    WUXING_COLORS,
    WUXING_COLORS_LIGHT,
)


# ──────────────────────────────────────────────────────────────────────────────
# SVG 生成（SVG Generation）
# ──────────────────────────────────────────────────────────────────────────────

def render_bazi_chart_svg(chart: BaziChart, width: int = 900, height: int = 780) -> str:
    """生成傳統子平命盤水墨畫風格 SVG。

    視覺規格：
    - 宣紙質感背景（米白 + 細微紙纖維紋理）
    - 傳統四柱並列（由右至左：年月日時，依中國傳統書寫習慣）
    - 書法字體天干地支
    - 朱印印章（圓形「子平正宗」+ 方形格局/用神標籤）
    - 墨線邊框 + 古典裝飾
    - 側欄大運排例

    Args:
        chart: BaziChart 命盤資料
        width: SVG 寬度（像素）
        height: SVG 高度（像素）

    Returns:
        SVG XML 字串，可直接在 Streamlit 中以 components.html 呈現
    """
    yp = chart.year_pillar
    mp = chart.month_pillar
    dp = chart.day_pillar
    hp = chart.hour_pillar

    wc = WUXING_COLORS
    wc_light = WUXING_COLORS_LIGHT

    # ── 五行顏色映射（供各柱天干地支著色）
    def wx_color(wx: str, light: bool = False) -> str:
        d = wc_light if light else wc
        return d.get(wx, "#666")

    def ss_color(ss: str) -> str:
        return SHISHEN_COLORS.get(ss, "#555")

    # ── 各柱資料整理（右至左：年、月、日、時）
    pillars = [
        ("年", yp),
        ("月", mp),
        ("日", dp),
        ("時", hp),
    ]

    # ── 佈局常數
    margin_left = 30
    margin_top = 50
    header_h = 90        # 標題區高度
    pillar_area_w = 540  # 四柱區域寬度
    sidebar_w = width - pillar_area_w - margin_left - 20
    pillar_w = pillar_area_w // 4  # 每柱寬度 = 135
    pillar_h = 360        # 四柱格子高度
    bottom_area_y = header_h + pillar_h + 30
    bottom_area_h = height - bottom_area_y - 20

    # ────────────────────────────────────────────────────────────────────────
    # SVG 開始
    # ────────────────────────────────────────────────────────────────────────
    parts: List[str] = []

    parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg"
     width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     font-family="'Noto Serif SC', 'Source Han Serif CN', 'STSong', 'SimSun', serif">''')

    # ── SVG 濾鏡定義
    parts.append('''<defs>
  <!-- 宣紙質感濾鏡 -->
  <filter id="paper-texture" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.65 0.75"
                  numOctaves="4" seed="2" result="noise"/>
    <feColorMatrix type="matrix"
      values="0 0 0 0 0.96  0 0 0 0 0.94  0 0 0 0 0.88  0 0 0 0.08 0"
      in="noise" result="coloredNoise"/>
    <feComposite in="SourceGraphic" in2="coloredNoise" operator="in"/>
    <feBlend in="SourceGraphic" in2="coloredNoise" mode="multiply"/>
  </filter>
  <!-- 墨跡暈染濾鏡 -->
  <filter id="ink-blur" x="-5%" y="-5%" width="110%" height="110%">
    <feGaussianBlur stdDeviation="0.8"/>
  </filter>
  <!-- 印章模糊（手蓋真實感）-->
  <filter id="seal-blur" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="turbulence" baseFrequency="0.05" numOctaves="2"
                  seed="5" result="noise"/>
    <feDisplacementMap in="SourceGraphic" in2="noise"
                       scale="1.5" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <!-- 淡水墨陰影 -->
  <filter id="ink-shadow">
    <feDropShadow dx="1" dy="1" stdDeviation="1.5" flood-color="#4A3728" flood-opacity="0.25"/>
  </filter>
  <!-- 朱印陰影 -->
  <filter id="seal-shadow">
    <feDropShadow dx="2" dy="2" stdDeviation="2" flood-color="#8B0000" flood-opacity="0.3"/>
  </filter>
  <!-- 宣紙底色漸層 -->
  <linearGradient id="paper-grad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#F7F2E3"/>
    <stop offset="30%" stop-color="#F5EED8"/>
    <stop offset="70%" stop-color="#F3ECD5"/>
    <stop offset="100%" stop-color="#EFE8D0"/>
  </linearGradient>
  <!-- 柱欄分隔線漸層 -->
  <linearGradient id="divider-grad" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#C8B090" stop-opacity="0.2"/>
    <stop offset="50%" stop-color="#A08060" stop-opacity="0.6"/>
    <stop offset="100%" stop-color="#C8B090" stop-opacity="0.2"/>
  </linearGradient>
  <!-- 標題漸層（深墨色） -->
  <linearGradient id="title-grad" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#2A1A0A"/>
    <stop offset="100%" stop-color="#1A0A00"/>
  </linearGradient>
</defs>''')

    # ── 宣紙背景
    parts.append(f'''
<!-- 宣紙底色 -->
<rect width="{width}" height="{height}" fill="url(#paper-grad)" filter="url(#paper-texture)"/>
<!-- 邊框（外框） -->
<rect x="8" y="8" width="{width-16}" height="{height-16}"
      fill="none" stroke="{SVG_BORDER_COLOR}" stroke-width="2.5" opacity="0.7"/>
<rect x="13" y="13" width="{width-26}" height="{height-26}"
      fill="none" stroke="{SVG_BORDER_COLOR}" stroke-width="0.8" opacity="0.4"/>
<!-- 細微水墨角裝飾 -->
<line x1="8" y1="8" x2="45" y2="8" stroke="{SVG_INK_DARK}" stroke-width="3" opacity="0.5"/>
<line x1="8" y1="8" x2="8" y2="45" stroke="{SVG_INK_DARK}" stroke-width="3" opacity="0.5"/>
<line x1="{width-8}" y1="8" x2="{width-45}" y2="8" stroke="{SVG_INK_DARK}" stroke-width="3" opacity="0.5"/>
<line x1="{width-8}" y1="8" x2="{width-8}" y2="45" stroke="{SVG_INK_DARK}" stroke-width="3" opacity="0.5"/>
<line x1="8" y1="{height-8}" x2="45" y2="{height-8}" stroke="{SVG_INK_DARK}" stroke-width="3" opacity="0.5"/>
<line x1="8" y1="{height-8}" x2="8" y2="{height-45}" stroke="{SVG_INK_DARK}" stroke-width="3" opacity="0.5"/>
<line x1="{width-8}" y1="{height-8}" x2="{width-45}" y2="{height-8}" stroke="{SVG_INK_DARK}" stroke-width="3" opacity="0.5"/>
<line x1="{width-8}" y1="{height-8}" x2="{width-8}" y2="{height-45}" stroke="{SVG_INK_DARK}" stroke-width="3" opacity="0.5"/>
''')

    # ── 標題區
    title_y = 28
    gender_str = chart.gender
    birth_str = f"{chart.birth_year}年{chart.birth_month}月{chart.birth_day}日  {chart.birth_hour:02d}:{chart.birth_minute:02d}"
    loc_str = chart.location_name or ""

    parts.append(f'''
<!-- 標題 -->
<text x="{margin_left + 10}" y="{title_y + 20}" font-size="24" font-weight="bold"
      fill="url(#title-grad)" filter="url(#ink-shadow)" letter-spacing="4">子平八字命盤</text>
<text x="{margin_left + 10}" y="{title_y + 44}" font-size="11"
      fill="{SVG_SUBTITLE_COLOR}" letter-spacing="1">
  {birth_str}　{gender_str}命　{loc_str}
</text>
<!-- 標題下分隔線 -->
<line x1="{margin_left}" y1="{title_y + 55}" x2="{width - 20}" y2="{title_y + 55}"
      stroke="{SVG_BORDER_COLOR}" stroke-width="1.2" opacity="0.5"/>
<line x1="{margin_left}" y1="{title_y + 57}" x2="{width - 20}" y2="{title_y + 57}"
      stroke="{SVG_BORDER_COLOR}" stroke-width="0.5" opacity="0.3"/>
''')

    # ── 「子平正宗」圓形朱印（右上角）
    seal_cx = width - 55
    seal_cy = 55
    parts.append(f'''
<!-- 「子平正宗」圓形朱印 -->
<g filter="url(#seal-shadow)" opacity="0.88" transform="rotate(-5, {seal_cx}, {seal_cy})">
  <circle cx="{seal_cx}" cy="{seal_cy}" r="38"
          fill="none" stroke="{SVG_SEAL_RED}" stroke-width="2.5"/>
  <circle cx="{seal_cx}" cy="{seal_cy}" r="34"
          fill="none" stroke="{SVG_SEAL_RED}" stroke-width="0.8"/>
  <text x="{seal_cx}" y="{seal_cy - 12}" text-anchor="middle" font-size="11"
        fill="{SVG_SEAL_RED}" font-weight="bold" letter-spacing="2">子平</text>
  <text x="{seal_cx}" y="{seal_cy + 4}" text-anchor="middle" font-size="11"
        fill="{SVG_SEAL_RED}" font-weight="bold" letter-spacing="2">正宗</text>
  <text x="{seal_cx}" y="{seal_cy + 18}" text-anchor="middle" font-size="8"
        fill="{SVG_SEAL_RED}" letter-spacing="1">命學</text>
</g>
''')

    # ── 四柱區域主框
    pillar_x0 = margin_left
    pillar_y0 = header_h
    total_pillar_w = pillar_w * 4

    parts.append(f'''
<!-- 四柱主框 -->
<rect x="{pillar_x0}" y="{pillar_y0}" width="{total_pillar_w}" height="{pillar_h}"
      fill="rgba(250,246,235,0.6)" stroke="{SVG_BORDER_COLOR}" stroke-width="1.5" opacity="0.9"/>
''')

    # ── 柱頭標籤行
    header_row_h = 32
    for i, (label, pillar) in enumerate(pillars):
        col_x = pillar_x0 + i * pillar_w
        # 柱頭背景（交替淡色）
        bg_color = "rgba(190,160,100,0.12)" if i % 2 == 0 else "rgba(180,150,90,0.07)"
        parts.append(f'''
<rect x="{col_x}" y="{pillar_y0}" width="{pillar_w}" height="{header_row_h}"
      fill="{bg_color}"/>
<text x="{col_x + pillar_w // 2}" y="{pillar_y0 + 22}"
      text-anchor="middle" font-size="15" font-weight="bold"
      fill="{SVG_INK_DARK}" letter-spacing="3">{label}　柱</text>
''')

    # ── 柱分隔線
    for i in range(1, 4):
        lx = pillar_x0 + i * pillar_w
        parts.append(f'''
<line x1="{lx}" y1="{pillar_y0}" x2="{lx}" y2="{pillar_y0 + pillar_h}"
      stroke="url(#divider-grad)" stroke-width="1.2"/>
''')

    # 柱頭底線
    parts.append(f'''
<line x1="{pillar_x0}" y1="{pillar_y0 + header_row_h}"
      x2="{pillar_x0 + total_pillar_w}" y2="{pillar_y0 + header_row_h}"
      stroke="{SVG_BORDER_COLOR}" stroke-width="0.8" opacity="0.5"/>
''')

    # ── 各柱內容
    row_y_offsets = {
        "shishen":  header_row_h + 24,
        "stem":     header_row_h + 72,
        "branch":   header_row_h + 135,
        "canggan":  header_row_h + 195,
        "wuxing":   header_row_h + 230,
        "changsheng": header_row_h + 260,
        "label_ss": header_row_h + 14,
        "label_cg": header_row_h + 185,
    }

    for i, (label, pillar) in enumerate(pillars):
        col_x = pillar_x0 + i * pillar_w
        cx = col_x + pillar_w // 2

        # 十神標籤
        ss = pillar.shishen
        ss_col = ss_color(ss)
        if ss == "日主":
            ss_display = "日主"
            ss_col = "#8B4513"
        else:
            ss_display = ss

        # 十神小標籤背景
        ss_badge_w = 52
        ss_badge_h = 20
        parts.append(f'''
<rect x="{cx - ss_badge_w//2}" y="{pillar_y0 + row_y_offsets['shishen'] - 16}"
      width="{ss_badge_w}" height="{ss_badge_h}" rx="3"
      fill="{ss_col}" opacity="0.18"/>
<text x="{cx}" y="{pillar_y0 + row_y_offsets['shishen']}"
      text-anchor="middle" font-size="13" fill="{ss_col}" font-weight="bold"
      letter-spacing="1">{ss_display}</text>
''')

        # 天干（大字，書法感）
        stem_wx = pillar.wuxing_stem
        stem_color = wx_color(stem_wx)
        parts.append(f'''
<text x="{cx}" y="{pillar_y0 + row_y_offsets['stem']}"
      text-anchor="middle" font-size="46" font-weight="bold"
      fill="{stem_color}" filter="url(#ink-shadow)" letter-spacing="0"
      >{pillar.stem}</text>
''')

        # 天干五行小字
        parts.append(f'''
<text x="{cx}" y="{pillar_y0 + row_y_offsets['stem'] + 18}"
      text-anchor="middle" font-size="10" fill="{stem_color}" opacity="0.7"
      >{stem_wx}{'陽' if pillar.yinyang_stem else '陰'}</text>
''')

        # 地支（大字）
        branch_wx = pillar.wuxing_branch
        branch_color = wx_color(branch_wx)
        # 日主柱地支用朱砂紅框線標示
        if label == "日":
            parts.append(f'''
<rect x="{cx - 28}" y="{pillar_y0 + row_y_offsets['branch'] - 44}"
      width="56" height="52" rx="4"
      fill="none" stroke="{SVG_SEAL_RED}" stroke-width="1.5" opacity="0.45"/>
''')
        parts.append(f'''
<text x="{cx}" y="{pillar_y0 + row_y_offsets['branch']}"
      text-anchor="middle" font-size="46" font-weight="bold"
      fill="{branch_color}" filter="url(#ink-shadow)">{pillar.branch}</text>
''')

        # 地支五行小字
        parts.append(f'''
<text x="{cx}" y="{pillar_y0 + row_y_offsets['branch'] + 18}"
      text-anchor="middle" font-size="10" fill="{branch_color}" opacity="0.7"
      >{branch_wx}{'陽' if pillar.yinyang_branch else '陰'}</text>
''')

        # 藏干（小字，橫排）
        cg_str = "　".join(pillar.canggan[:3])
        parts.append(f'''
<text x="{cx}" y="{pillar_y0 + row_y_offsets['canggan']}"
      text-anchor="middle" font-size="11" fill="{SVG_SUBTITLE_COLOR}"
      letter-spacing="2">藏：{cg_str}</text>
''')

        # 藏干十神（更小字）
        cg_ss_str = " ".join(pillar.canggan_shishen[:3])
        parts.append(f'''
<text x="{cx}" y="{pillar_y0 + row_y_offsets['canggan'] + 18}"
      text-anchor="middle" font-size="9.5" fill="#7A5C3A" opacity="0.8"
      >{cg_ss_str}</text>
''')

        # 十二長生
        cs = pillar.changsheng
        cs_important = cs in ("帝旺", "長生", "墓", "絕", "死")
        cs_color = SVG_SEAL_RED if cs_important else SVG_SUBTITLE_COLOR
        parts.append(f'''
<text x="{cx}" y="{pillar_y0 + row_y_offsets['changsheng']}"
      text-anchor="middle" font-size="11" fill="{cs_color}"
      font-style="italic" letter-spacing="1">{cs}</text>
''')

    # ── 四柱底部補充資訊行（空亡、沖等）
    kw1, kw2 = _get_kongwang_for_chart(chart)
    info_row_y = pillar_y0 + pillar_h - 22
    parts.append(f'''
<text x="{pillar_x0 + total_pillar_w // 2}" y="{info_row_y}"
      text-anchor="middle" font-size="10" fill="{SVG_SUBTITLE_COLOR}" opacity="0.7"
      letter-spacing="1">旬空：{kw1}、{kw2}</text>
''')

    # ── 大運側欄
    sidebar_x = pillar_x0 + total_pillar_w + 20
    sidebar_y = pillar_y0

    # 大運標題
    parts.append(f'''
<!-- 大運側欄 -->
<rect x="{sidebar_x - 5}" y="{sidebar_y}" width="{sidebar_w + 10}" height="{pillar_h}"
      fill="rgba(245,238,220,0.5)" stroke="{SVG_BORDER_COLOR}" stroke-width="1" opacity="0.7"/>
<text x="{sidebar_x + sidebar_w // 2}" y="{sidebar_y + 24}"
      text-anchor="middle" font-size="14" font-weight="bold"
      fill="{SVG_INK_DARK}" letter-spacing="3">大　運</text>
<line x1="{sidebar_x - 5}" y1="{sidebar_y + 32}" x2="{sidebar_x + sidebar_w + 5}" y2="{sidebar_y + 32}"
      stroke="{SVG_BORDER_COLOR}" stroke-width="0.7" opacity="0.5"/>
''')

    # 大運起運資訊
    parts.append(f'''
<text x="{sidebar_x + 5}" y="{sidebar_y + 48}" font-size="10" fill="{SVG_SUBTITLE_COLOR}">
  {chart.dayun_direction}　起運：約{chart.dayun_start_age}歲</text>
''')

    # 大運各步（最多顯示8步）
    dy_item_h = 30
    for idx, step in enumerate(chart.dayun_steps[:8]):
        dy_y = sidebar_y + 58 + idx * dy_item_h
        is_current = (chart.current_dayun and step.ganzhi == chart.current_dayun.ganzhi)
        bg_col = "rgba(196,30,58,0.12)" if is_current else "rgba(0,0,0,0)"
        text_col = SVG_SEAL_RED if is_current else SVG_INK_DARK
        parts.append(f'''
<rect x="{sidebar_x}" y="{dy_y - 18}" width="{sidebar_w}" height="{dy_item_h - 2}"
      fill="{bg_col}" rx="2"/>
<text x="{sidebar_x + 5}" y="{dy_y - 2}" font-size="13" font-weight="bold"
      fill="{text_col}" letter-spacing="2">{step.ganzhi}</text>
<text x="{sidebar_x + 45}" y="{dy_y - 2}" font-size="9.5" fill="{SVG_SUBTITLE_COLOR}">
  {step.age_start:.0f}–{step.age_end:.0f}歲</text>
<text x="{sidebar_x + 45}" y="{dy_y + 10}" font-size="9" fill="#8B6914" opacity="0.8">
  {step.year_start}年</text>
''')
        if is_current:
            parts.append(f'''
<text x="{sidebar_x + sidebar_w - 2}" y="{dy_y - 2}" text-anchor="end"
      font-size="9" fill="{SVG_SEAL_RED}" font-weight="bold">◄ 當運</text>
''')

    # ── 大運「大運」方形朱印
    seal_x2 = sidebar_x + sidebar_w - 28
    seal_y2 = sidebar_y + pillar_h - 42
    parts.append(f'''
<!-- 「大運」方形朱印 -->
<g filter="url(#seal-blur)" opacity="0.82" transform="rotate(6, {seal_x2}, {seal_y2})">
  <rect x="{seal_x2 - 20}" y="{seal_y2 - 20}" width="42" height="42"
        fill="none" stroke="{SVG_SEAL_RED}" stroke-width="2"/>
  <text x="{seal_x2 + 1}" y="{seal_y2 - 2}" text-anchor="middle"
        font-size="11" fill="{SVG_SEAL_RED}" font-weight="bold">大運</text>
  <text x="{seal_x2 + 1}" y="{seal_y2 + 12}" text-anchor="middle"
        font-size="11" fill="{SVG_SEAL_RED}" font-weight="bold">起例</text>
</g>
''')

    # ── 下方資訊區
    info_x = margin_left
    info_y = bottom_area_y

    # 資訊區背景框
    parts.append(f'''
<!-- 下方資訊區 -->
<rect x="{info_x}" y="{info_y}" width="{width - 40}" height="{bottom_area_h}"
      fill="rgba(248,243,228,0.5)" stroke="{SVG_BORDER_COLOR}" stroke-width="1" opacity="0.6"/>
''')

    # 日主、格局、用神資訊行
    dm_col = wx_color(chart.day_master_wuxing)
    strength_col = SVG_SEAL_RED if "強" in chart.day_master_strength else "#1565C0"

    row1_y = info_y + 22
    parts.append(f'''
<text x="{info_x + 10}" y="{row1_y}" font-size="12" fill="{SVG_INK_DARK}" letter-spacing="1">
  <tspan font-weight="bold">日主：</tspan>
  <tspan fill="{dm_col}" font-size="14" font-weight="bold">{chart.day_master}</tspan>
  <tspan fill="{SVG_SUBTITLE_COLOR}"> ({chart.day_master_wuxing})</tspan>
  <tspan>　</tspan>
  <tspan font-weight="bold">強弱：</tspan>
  <tspan fill="{strength_col}">{chart.day_master_strength}</tspan>
  <tspan fill="{SVG_SUBTITLE_COLOR}">（月令{chart.day_master_vitality}，分值{chart.day_master_strength_score}）</tspan>
</text>
''')

    row2_y = row1_y + 24
    yong_col = wx_color(chart.yongshen)
    ji_col = wx_color(chart.jishen)
    parts.append(f'''
<text x="{info_x + 10}" y="{row2_y}" font-size="12" fill="{SVG_INK_DARK}" letter-spacing="1">
  <tspan font-weight="bold">格局：</tspan>
  <tspan fill="{SVG_SEAL_RED}" font-weight="bold">{chart.pattern}</tspan>
  <tspan fill="{SVG_SUBTITLE_COLOR}">（{chart.pattern_type}）</tspan>
  <tspan>　</tspan>
  <tspan font-weight="bold">用神：</tspan>
  <tspan fill="{yong_col}" font-weight="bold">{chart.yongshen}</tspan>
  <tspan>　忌神：</tspan>
  <tspan fill="{ji_col}">{chart.jishen}</tspan>
  <tspan>　調候：</tspan>
  <tspan fill="#5C3D11">{chart.tiaohoushen}</tspan>
</text>
''')

    # 神煞列
    row3_y = row2_y + 22
    shensha_display = "　".join(
        f"{ss.name}({ss.pillar})" for ss in chart.shensha_list[:6]
    )
    parts.append(f'''
<text x="{info_x + 10}" y="{row3_y}" font-size="11" fill="{SVG_SUBTITLE_COLOR}" letter-spacing="0.5">
  <tspan font-weight="bold" fill="{SVG_INK_DARK}">神煞：</tspan>
  <tspan>{shensha_display}</tspan>
</text>
''')

    # 沖合資訊
    row4_y = row3_y + 20
    chong_str = "　".join(f"{a}沖{b}" for a, b in chart.interactions.liuchong[:3])
    he_str = "　".join(f"{a}合{b}→{c}" for a, b, c in chart.interactions.liuhe[:3])
    sanhe_str = "　".join(
        f"{''.join(b)}三合{c}" for b, c in chart.interactions.sanhe[:2]
    )
    xing_str = "　".join(
        f"{''.join(b)}{c}" for b, c in chart.interactions.sanxing[:2]
    )
    interaction_display = "　|　".join(filter(None, [chong_str, he_str, sanhe_str]))
    if xing_str:
        interaction_display += f"　|　三刑：{xing_str}"
    if not interaction_display:
        interaction_display = "（無顯著沖合刑害）"

    parts.append(f'''
<text x="{info_x + 10}" y="{row4_y}" font-size="10.5" fill="{SVG_SUBTITLE_COLOR}">
  <tspan font-weight="bold" fill="{SVG_INK_DARK}">沖合：</tspan>
  <tspan>{interaction_display[:80]}</tspan>
</text>
''')

    # 流年當運
    row5_y = row4_y + 20
    ly_col = SVG_SEAL_RED
    parts.append(f'''
<text x="{info_x + 10}" y="{row5_y}" font-size="11" fill="{SVG_SUBTITLE_COLOR}">
  <tspan font-weight="bold" fill="{SVG_INK_DARK}">當前：</tspan>
  <tspan fill="{ly_col}" font-weight="bold">{chart.current_liunian_year}年{chart.current_liunian}流年</tspan>
  <tspan>　當運大運：</tspan>
  <tspan fill="{ly_col}" font-weight="bold">{chart.current_dayun.ganzhi if chart.current_dayun else '—'}</tspan>
  <tspan>（{'—' if not chart.current_dayun else f'{chart.current_dayun.age_start:.0f}–{chart.current_dayun.age_end:.0f}歲'}）</tspan>
</text>
''')

    # ── 格局方形朱印
    seal2_x = width - 60
    seal2_y = bottom_area_y + bottom_area_h - 55
    # 截短格局名（最多4字）
    pattern_short = chart.pattern[:4] if len(chart.pattern) > 4 else chart.pattern
    parts.append(f'''
<!-- 「格局」方形朱印 -->
<g filter="url(#seal-blur)" opacity="0.80" transform="rotate(-4, {seal2_x}, {seal2_y})">
  <rect x="{seal2_x - 24}" y="{seal2_y - 24}" width="50" height="50"
        fill="rgba(196,30,58,0.1)" stroke="{SVG_SEAL_RED}" stroke-width="2.2"/>
  <rect x="{seal2_x - 21}" y="{seal2_y - 21}" width="44" height="44"
        fill="none" stroke="{SVG_SEAL_RED}" stroke-width="0.7"/>
  <text x="{seal2_x + 1}" y="{seal2_y - 4}" text-anchor="middle"
        font-size="12" fill="{SVG_SEAL_RED}" font-weight="bold">{pattern_short[:2]}</text>
  <text x="{seal2_x + 1}" y="{seal2_y + 12}" text-anchor="middle"
        font-size="12" fill="{SVG_SEAL_RED}" font-weight="bold">{pattern_short[2:] if len(pattern_short) > 2 else ""}</text>
</g>
''')

    # ── 用神橢圓朱印
    seal3_x = width - 120
    seal3_y = bottom_area_y + bottom_area_h - 48
    parts.append(f'''
<!-- 「用神」橢圓朱印 -->
<g filter="url(#seal-blur)" opacity="0.75" transform="rotate(3, {seal3_x}, {seal3_y})">
  <ellipse cx="{seal3_x}" cy="{seal3_y}" rx="26" ry="20"
           fill="none" stroke="{SVG_SEAL_RED}" stroke-width="2"/>
  <text x="{seal3_x}" y="{seal3_y - 5}" text-anchor="middle"
        font-size="10" fill="{SVG_SEAL_RED}" font-weight="bold" letter-spacing="1">用神</text>
  <text x="{seal3_x}" y="{seal3_y + 8}" text-anchor="middle"
        font-size="13" fill="{SVG_SEAL_RED}" font-weight="bold">{chart.yongshen}</text>
</g>
''')

    # ── 底部版本小字
    parts.append(f'''
<text x="{width // 2}" y="{height - 10}" text-anchor="middle"
      font-size="9" fill="{SVG_SUBTITLE_COLOR}" opacity="0.5" letter-spacing="1">
  子平八字 · KinAstro · 傳統推命
</text>
''')

    # SVG 結束
    parts.append("</svg>")

    return "\n".join(parts)


def _get_kongwang_for_chart(chart: BaziChart) -> tuple:
    """取命盤日柱空亡。"""
    return _get_kongwang(chart.day_pillar.ganzhi)


# ──────────────────────────────────────────────────────────────────────────────
# Streamlit 渲染（Streamlit Renderer）
# ──────────────────────────────────────────────────────────────────────────────

def render_streamlit(chart: BaziChart) -> None:
    """在 Streamlit 中完整渲染子平八字命盤。

    包含：
    - 傳統水墨風格 SVG 命盤
    - 四柱詳細表格
    - 日主強弱分析
    - 格局用神說明
    - 大運詳細排例
    - 神煞列表
    - 沖合刑害分析
    - 古典文字解讀（中英雙語）
    """
    import pandas as pd

    # ── SVG 命盤
    st.subheader(auto_cn("📜 傳統水墨命盤", "Traditional Ink-Style Bazi Chart"))
    svg_html = render_bazi_chart_svg(chart, width=900, height=780)
    components.html(
        f'<div style="overflow-x:auto;background:#F5F0E0;padding:10px;border-radius:8px;">{svg_html}</div>',
        height=800,
        scrolling=True,
    )

    # ── 命盤概覽
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(auto_cn("日主"), chart.day_master,
                  help=auto_cn(f"五行：{chart.day_master_wuxing}"))
    with col2:
        st.metric(auto_cn("強弱"), chart.day_master_strength,
                  help=auto_cn(f"月令{chart.day_master_vitality}，分值{chart.day_master_strength_score}"))
    with col3:
        st.metric(auto_cn("格局"), chart.pattern,
                  help=auto_cn(chart.pattern_type))
    with col4:
        st.metric(auto_cn("用神"), chart.yongshen,
                  help=auto_cn(f"忌神：{chart.jishen}"))

    # ── 四柱詳細表格
    st.subheader(auto_cn("🏛 四柱干支詳表", "Four Pillars Detail"))
    yp, mp, dp, hp = chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar
    pillars_data = []
    for label, p in [("年柱", yp), ("月柱", mp), ("日柱", dp), ("時柱", hp)]:
        pillars_data.append({
            auto_cn("柱"): label,
            auto_cn("天干"): p.stem,
            auto_cn("地支"): p.branch,
            auto_cn("干五行"): p.wuxing_stem,
            auto_cn("支五行"): p.wuxing_branch,
            auto_cn("十神"): p.shishen,
            auto_cn("藏干"): "、".join(p.canggan),
            auto_cn("藏干十神"): "、".join(p.canggan_shishen),
            auto_cn("長生"): p.changsheng,
        })
    df_pillars = pd.DataFrame(pillars_data)
    st.dataframe(df_pillars, width="stretch")

    # ── 日主強弱分析
    st.subheader(auto_cn("⚖️ 日主強弱分析", "Day Master Strength Analysis"))
    st.markdown(f"""
**{auto_cn('日主')}：** {chart.day_master}（{chart.day_master_wuxing}）　
**{auto_cn('月令')}：** {chart.month_pillar.branch}（{chart.day_master_vitality}）　
**{auto_cn('強弱')}：** {chart.day_master_strength}（{auto_cn('分值')} {chart.day_master_strength_score}）

> *《滴天髓》云：「先觀月令，再察四柱，以定日主強弱。」*
""")

    # ── 格局用神
    st.subheader(auto_cn("🎯 格局與用神", "Pattern & Use God"))

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**{auto_cn('格局')}：** {chart.pattern}（{chart.pattern_type}）")
        st.caption(chart.pattern_description_zh)
    with col_b:
        st.markdown(
            f"**{auto_cn('用神')}：** `{chart.yongshen}` ｜ "
            f"**{auto_cn('喜神')}：** `{chart.xishen}` ｜ "
            f"**{auto_cn('忌神')}：** `{chart.jishen}` ｜ "
            f"**{auto_cn('仇神')}：** `{chart.jiaoshen}`"
        )
        st.caption(f"{auto_cn('調候用神')}：{chart.tiaohoushen}")
        st.caption(chart.yongshen_description_zh)

    # ── 大運
    st.subheader(auto_cn("📅 大運排例", "Great Fortune Cycles"))
    kw1, kw2 = _get_kongwang_for_chart(chart)
    st.caption(
        f"{auto_cn('大運方向')}：{chart.dayun_direction}　"
        f"{auto_cn('起運歲數')}：約 **{chart.dayun_start_age}** 歲　"
        f"{auto_cn('起運日期')}：{chart.dayun_start_date}　"
        f"{auto_cn('旬空')}：{kw1}、{kw2}"
    )
    dayun_data = []
    for step in chart.dayun_steps:
        is_current = (chart.current_dayun and step.ganzhi == chart.current_dayun.ganzhi)
        marker = " ◄ 當運" if is_current else ""
        dayun_data.append({
            auto_cn("大運"): step.ganzhi + marker,
            auto_cn("天干"): step.stem,
            auto_cn("地支"): step.branch,
            auto_cn("干十神"): step.shishen_stem,
            auto_cn("支藏干十神"): step.shishen_branch,
            auto_cn("年齡"): f"{step.age_start:.0f}–{step.age_end:.0f}",
            auto_cn("起運年份"): step.year_start,
        })
    df_dayun = pd.DataFrame(dayun_data)
    st.dataframe(df_dayun, width="stretch")

    # 當前流年
    st.info(
        f"🗓️ **{auto_cn('當前流年')}：** {chart.current_liunian_year} 年　"
        f"流年干支：**{chart.current_liunian}**　｜　"
        f"{auto_cn('當前大運')}：**{chart.current_dayun.ganzhi if chart.current_dayun else '—'}**"
    )

    # ── 神煞
    st.subheader(auto_cn("✨ 神煞列表", "Shen Sha Stars"))
    if chart.shensha_list:
        shensha_data = []
        for ss in chart.shensha_list:
            shensha_data.append({
                auto_cn("神煞"): ss.name,
                "English": ss.name_en,
                auto_cn("所在柱"): ss.pillar,
                auto_cn("地支"): ss.branch,
                auto_cn("吉/凶"): "✅ 吉" if ss.is_auspicious else "⚠️ 凶",
                auto_cn("說明"): ss.description_zh,
            })
        df_ss = pd.DataFrame(shensha_data)
        st.dataframe(df_ss, width="stretch")
    else:
        st.caption(auto_cn("無顯著神煞"))

    # ── 沖合刑害
    st.subheader(auto_cn("⚡ 沖合刑害", "Branch Interactions"))
    inter = chart.interactions
    cols = st.columns(3)
    with cols[0]:
        if inter.liuhe:
            st.markdown(f"**{auto_cn('六合')}**")
            for a, b, wx in inter.liuhe:
                st.write(f"  {a} ＋ {b} → {wx}")
        if inter.tiangan_he:
            st.markdown(f"**{auto_cn('天干相合')}**")
            for a, b, wx in inter.tiangan_he:
                st.write(f"  {a} ＋ {b} → {wx}")
    with cols[1]:
        if inter.sanhe:
            st.markdown(f"**{auto_cn('三合')}**")
            for bs, wx in inter.sanhe:
                st.write(f"  {''.join(bs)} → {wx}")
        if inter.sanhui:
            st.markdown(f"**{auto_cn('三會')}**")
            for bs, wx in inter.sanhui:
                st.write(f"  {''.join(bs)} → {wx}")
    with cols[2]:
        if inter.liuchong:
            st.markdown(f"**{auto_cn('六冲')}**")
            for a, b in inter.liuchong:
                st.write(f"  {a} ↔ {b}")
        if inter.liuhai:
            st.markdown(f"**{auto_cn('六害')}**")
            for a, b in inter.liuhai:
                st.write(f"  {a} ✕ {b}")
        if inter.sanxing:
            st.markdown(f"**{auto_cn('三刑')}**")
            for bs, xtype in inter.sanxing:
                st.write(f"  {''.join(bs)}（{xtype}）")
    if not any([inter.liuhe, inter.sanhe, inter.sanhui,
                inter.liuchong, inter.liuhai, inter.sanxing,
                inter.tiangan_he]):
        st.caption(auto_cn("四柱間無顯著沖合刑害"))

    # ── 盲派八字
    st.subheader(auto_cn("🕯️ 盲派八字分析", "Blind School Bazi Analysis"))
    blind_report = getattr(chart, "blind_school_report", None) or {}
    if not blind_report:
        # 後備路徑：兼容由舊版快取或外部程式建立、尚未附帶 blind_school_report 的 chart。
        try:
            from .bazi_blind_school_logic import BlindSchoolBazi
            blind_report = BlindSchoolBazi.from_bazi_chart(chart).full_report()
        except (ImportError, ValueError, AttributeError, TypeError, KeyError) as e:
            blind_report = {}
            st.caption(auto_cn(f"盲派分析暫不可用：{e}", f"Blind-school analysis unavailable: {e}"))

    if blind_report:
        st.markdown(f"**{auto_cn('命局總述')}：** {blind_report.get('summary', '—')}")
        illness_raw = blind_report.get("illness", {})
        use_god_raw = blind_report.get("use_god", {})
        illness = illness_raw if isinstance(illness_raw, dict) else {}
        use_god = use_god_raw if isinstance(use_god_raw, dict) else {}
        col_bs1, col_bs2 = st.columns(2)
        with col_bs1:
            st.caption(auto_cn("病處", "Illness"))
            st.write(illness.get("總述", "—"))
        with col_bs2:
            st.caption(auto_cn("以病取用", "Use-God Recommendation"))
            st.write(use_god.get("總結", "—"))
        with st.expander(auto_cn("查看完整盲派結構化報告", "View Full Blind-School Structured Report")):
            tab_vis, tab_struct, tab_raw = st.tabs([
                auto_cn("視覺總覽", "Visual Overview"),
                auto_cn("分項結構", "Structured Sections"),
                auto_cn("原始 JSON", "Raw JSON"),
            ])

            with tab_vis:
                def _list_count(key: str) -> int:
                    value = illness.get(key, [])
                    return len(value) if isinstance(value, list) else 0

                risk_counts = {
                    auto_cn("穿破", "Pierce/Break"): _list_count("穿破"),
                    auto_cn("入墓", "Tomb"): _list_count("入墓"),
                    auto_cn("偏枯", "Element Bias"): _list_count("五行偏枯"),
                    auto_cn("三刑", "Punishment"): _list_count("三刑"),
                }
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                with col_m1:
                    st.metric(auto_cn("穿破", "Pierce/Break"), risk_counts[auto_cn("穿破", "Pierce/Break")])
                with col_m2:
                    st.metric(auto_cn("入墓", "Tomb"), risk_counts[auto_cn("入墓", "Tomb")])
                with col_m3:
                    st.metric(auto_cn("偏枯", "Element Bias"), risk_counts[auto_cn("偏枯", "Element Bias")])
                with col_m4:
                    st.metric(auto_cn("三刑", "Punishment"), risk_counts[auto_cn("三刑", "Punishment")])

                risks_df = pd.DataFrame(
                    [{auto_cn("項目", "Category"): k, auto_cn("數量", "Count"): v} for k, v in risk_counts.items()]
                )
                st.bar_chart(risks_df.set_index(auto_cn("項目", "Category"))[auto_cn("數量", "Count")])

                st.caption(auto_cn("病情分級", "Severity"))
                st.write(illness.get("病情輕重", "—"))

            with tab_struct:
                pb_details = blind_report.get("pierce_break_detail", [])
                if isinstance(pb_details, list) and pb_details:
                    st.markdown(f"**{auto_cn('穿破明細', 'Pierce/Break Details')}**")
                    st.dataframe(pd.DataFrame(pb_details), width="stretch")

                limits = blind_report.get("limits", [])
                if isinstance(limits, list) and limits:
                    st.markdown(f"**{auto_cn('盲派大限', 'Blind-School Limits')}**")
                    limits_df = pd.DataFrame(limits)
                    desired_cols = [
                        auto_cn("限段", "Segment"),
                        auto_cn("虛歲", "Age"),
                        auto_cn("限干支", "Pillar"),
                        auto_cn("十神", "Ten God"),
                        auto_cn("運勢初判", "Preliminary Fortune"),
                    ]
                    show_cols = [c for c in desired_cols if c in limits_df.columns]
                    st.dataframe(limits_df[show_cols] if show_cols else limits_df, width="stretch")

                marriage = blind_report.get("marriage", {})
                wealth = blind_report.get("wealth", {})
                liunian = blind_report.get("liunian_framework", {})
                six_qin = blind_report.get("six_qin_palaces", {})

                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    st.markdown(f"**{auto_cn('婚姻總評', 'Marriage Summary')}**")
                    st.write(marriage.get("總評", "—") if isinstance(marriage, dict) else "—")
                with col_s2:
                    st.markdown(f"**{auto_cn('財運總評', 'Wealth Summary')}**")
                    st.write(wealth.get("總評", "—") if isinstance(wealth, dict) else "—")

                if isinstance(liunian, dict):
                    rules = liunian.get("應期規則", [])
                    if isinstance(rules, list) and rules:
                        st.markdown(f"**{auto_cn('流年應期規則', 'Annual Timing Rules')}**")
                        for r in rules:
                            st.write(f"• {r}")

                if isinstance(six_qin, dict) and six_qin:
                    st.markdown(f"**{auto_cn('六親宮位重點', 'Six-Kin Palace Highlights')}**")
                    for palace, detail in six_qin.items():
                        with st.expander(str(palace)):
                            if isinstance(detail, dict):
                                st.write(f"{auto_cn('宮位職司', 'Role')}: {detail.get('宮位職司', '—')}")
                                st.write(f"{auto_cn('干支', 'Pillar')}: {detail.get('干支', '—')}")
                                notes = detail.get("注意事項", [])
                                if isinstance(notes, list):
                                    for note in notes:
                                        st.write(f"• {note}")
                            else:
                                st.write(detail)

            with tab_raw:
                st.json(blind_report)

    # ── 文字解讀
    st.subheader(auto_cn("📖 古典命盤解讀", "Classical Bazi Interpretation"))
    tab_zh, tab_en = st.tabs([auto_cn("中文古典解讀"), "English Reading"])
    with tab_zh:
        st.markdown(
            f'<div style="font-family:\'Noto Serif SC\',serif;line-height:2;'
            f'color:#2A1A0A;background:#FDFAF3;padding:20px;border-radius:8px;'
            f'border-left:4px solid #C41E3A;">{chart.reading_zh.replace(chr(10), "<br/>")}</div>',
            unsafe_allow_html=True,
        )
    with tab_en:
        st.text(chart.reading_en)
