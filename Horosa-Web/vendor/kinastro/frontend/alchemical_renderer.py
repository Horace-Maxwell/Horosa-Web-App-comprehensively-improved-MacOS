"""
frontend/alchemical_renderer.py
═══════════════════════════════════════════════════════════════════════════════
煉金占星學（Alchemical Astrology）— Streamlit 渲染器

提供：
    render_alchemical_tab   — Streamlit 頁面主入口
    _render_correspondence_table — 行星對應關係 HTML 表格
    _render_planets_svg          — 七星圓形 SVG 可視化
    _render_stage_wheel_svg      — 煉金四階段輪盤 SVG
    _render_personal_reading     — 個人星盤煉金解讀

視覺主題：
    - 深羊皮紙背景（#1C1008）：文藝復興時期煉金手稿風格
    - 黃金文字（#D4AF37）：煉金黃金象徵
    - 深紅點綴（#8B0000）：赤化（Rubedo）之色
    - Palatino/Georgia 字型：古典手稿質感

使用 t() 函數支援雙語（繁中/英）。
"""

from __future__ import annotations

from typing import Callable, Optional

import streamlit as st
import streamlit.components.v1 as components

from astro.alchemical_astrology import (
    ALCHEMICAL_STAGES,
    PLANET_CORRESPONDENCES,
    PLANET_KEYS,
    AlchemicalReading,
    AlchemicalStageInfo,
    PlanetCorrespondence,
    PlanetProfile,
    compute_reading,
)

try:
    from astro.i18n import auto_cn, t
except ImportError:
    import logging as _logging
    _logging.getLogger(__name__).warning(
        "astro.i18n not available; falling back to identity i18n stubs."
    )

    def t(key: str) -> str:  # type: ignore[misc]
        return key

    def auto_cn(text: str, en_text: str = "") -> str:  # type: ignore[misc]
        # fallback: return Chinese text when en_text not requested
        return text


# ─────────────────────────────────────────────────────────────────────────────
# 主題常數
# ─────────────────────────────────────────────────────────────────────────────

_BG_DARK      = "#1C1008"   # 深羊皮紙背景
_BG_CARD      = "#241508"   # 卡片背景
_GOLD_BRIGHT  = "#D4AF37"   # 亮金
_GOLD_DIM     = "#8C6E2A"   # 暗金
_GOLD_ACCENT  = "#F0C040"   # 強調金
_DEEP_RED     = "#8B0000"   # 深紅
_SILVER       = "#B8C4CC"   # 銀白
_PARCHMENT    = "#C8A96E"   # 羊皮紙
_INK          = "#D4B896"   # 墨水棕


# ─────────────────────────────────────────────────────────────────────────────
# CSS 主題
# ─────────────────────────────────────────────────────────────────────────────

def _theme_css() -> str:
    return f"""
<style>
.alch-header {{
  background: linear-gradient(135deg, {_BG_DARK} 0%, #2A1A08 55%, {_BG_DARK} 100%);
  border: 1px solid {_GOLD_DIM};
  border-radius: 10px;
  padding: 18px 24px;
  margin-bottom: 16px;
  text-align: center;
}}
.alch-title {{
  color: {_GOLD_BRIGHT};
  font-size: 1.7rem;
  font-family: "Palatino Linotype", "Book Antiqua", Palatino, Georgia, serif;
  font-weight: 700;
  margin: 0;
  letter-spacing: 3px;
  text-shadow: 0 0 16px rgba(212,175,55,0.6);
}}
.alch-subtitle {{
  color: {_GOLD_DIM};
  font-size: 0.9rem;
  margin: 6px 0 0 0;
  font-style: italic;
  letter-spacing: 1px;
}}
.alch-section-title {{
  color: {_GOLD_BRIGHT};
  font-family: Georgia, serif;
  font-size: 1.15rem;
  font-weight: bold;
  border-bottom: 1px solid {_GOLD_DIM};
  padding-bottom: 5px;
  margin: 20px 0 12px 0;
  letter-spacing: 1px;
}}
.alch-table {{
  width: 100%;
  border-collapse: collapse;
  font-family: Georgia, serif;
  font-size: 0.85rem;
  background: {_BG_DARK};
  color: {_INK};
}}
.alch-table th {{
  background: #2A1508;
  color: {_GOLD_BRIGHT};
  padding: 8px 10px;
  border: 1px solid {_GOLD_DIM};
  text-align: center;
  font-weight: bold;
  letter-spacing: 1px;
}}
.alch-table td {{
  padding: 7px 10px;
  border: 1px solid #3A2510;
  vertical-align: middle;
  text-align: center;
}}
.alch-table tr:hover td {{
  background: #2A1A08;
}}
.planet-glyph {{
  font-size: 1.4rem;
  text-shadow: 0 0 8px rgba(212,175,55,0.4);
}}
.alch-card {{
  background: linear-gradient(135deg, {_BG_CARD} 0%, #1C1008 100%);
  border: 1px solid {_GOLD_DIM};
  border-radius: 8px;
  padding: 16px 18px;
  margin: 10px 0;
}}
.alch-citation {{
  color: #7A6040;
  font-size: 0.78rem;
  font-style: italic;
  margin-top: 8px;
}}
.alch-dominant-badge {{
  background: linear-gradient(135deg, #2A1A00, #3D2800);
  border: 1px solid {_GOLD_BRIGHT};
  border-radius: 6px;
  padding: 4px 10px;
  color: {_GOLD_ACCENT};
  font-weight: bold;
  font-size: 0.9rem;
  display: inline-block;
}}
.alch-stage-badge {{
  display: inline-block;
  padding: 3px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: bold;
  margin: 2px;
}}
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# 頁頭
# ─────────────────────────────────────────────────────────────────────────────

def _render_header() -> None:
    """渲染文藝復興風格頁頭。"""
    st.markdown(_theme_css(), unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="alch-header">
  <p class="alch-title">⚗ 煉金占星學 &nbsp;·&nbsp; Alchemical Astrology</p>
  <p class="alch-subtitle">
    依帕拉塞爾蘇斯《天哲學》（Coelum Philosophorum, c.1525）及《偉大天文學》（Astronomia Magna, 1537–38）傳統<br>
    <em>Seven Planets · Seven Metals · Doctrine of Signatures · Opus Magnum</em>
  </p>
</div>
""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 行星對應關係 HTML 表格
# ─────────────────────────────────────────────────────────────────────────────

def _render_correspondence_table() -> None:
    """渲染七大行星對應關係精美 HTML 表格。"""
    st.markdown(
        '<p class="alch-section-title">⚷ 七大行星對應表（帕拉塞爾蘇斯傳統）</p>',
        unsafe_allow_html=True,
    )

    rows = []
    for key in PLANET_KEYS:
        c: PlanetCorrespondence = PLANET_CORRESPONDENCES[key]
        herbs_short = "；".join(c.herbs_zh[:2])
        minerals_short = "；".join(c.minerals_zh[:2])
        # 煉金階段標籤顏色
        stage_colors: dict[str, str] = {
            "nigredo": ("#1A1A1A", "#AAA"),
            "albedo": ("#E8E8F0", "#222"),
            "citrinitas": ("#DAA520", "#111"),
            "rubedo": ("#8B1A1A", "#FFD"),
        }
        stage_key = c.alchemical_stage.lower()
        sbg, sfg = stage_colors.get(stage_key, ("#333", "#CCC"))

        rows.append(f"""
<tr>
  <td><span class="planet-glyph" style="color:{c.color}">{c.symbol}</span><br>
      <span style="color:{_GOLD_DIM};font-size:0.8rem">{c.name_zh}</span></td>
  <td style="color:{_GOLD_BRIGHT}">{c.metal_zh}<br>
      <span style="color:#7A6040;font-size:0.78rem">{c.metal_latin}</span></td>
  <td style="color:{_SILVER}">{c.metal_symbol}</td>
  <td style="text-align:left;font-size:0.82rem">{herbs_short}</td>
  <td style="text-align:left;font-size:0.82rem">{minerals_short}</td>
  <td style="font-size:0.82rem;color:{_INK}">{c.body_part_zh}</td>
  <td><span class="alch-stage-badge" style="background:{sbg};color:{sfg}">{c.stage_zh}</span></td>
</tr>
""")

    table_html = f"""
<div style="overflow-x:auto">
<table class="alch-table">
<thead><tr>
  <th>行星</th>
  <th>金屬</th>
  <th>符號</th>
  <th>草本（Paracelsus）</th>
  <th>礦石</th>
  <th>人體部位</th>
  <th>煉金階段</th>
</tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</div>
<p class="alch-citation">
  ✦ 資料來源：Paracelsus, <em>Coelum Philosophorum</em> (c.1525)；
  <em>Astronomia Magna</em> (1537–38)；<em>De Natura Rerum</em> (1537)；
  Agrippa, <em>Three Books of Occult Philosophy</em>, Book I (1531)
</p>
"""
    st.markdown(table_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SVG：七星圓形可視化
# ─────────────────────────────────────────────────────────────────────────────

def _render_planets_svg() -> None:
    """渲染七大行星圓形 SVG 圖（帶金屬與草本標注）。"""
    st.markdown(
        '<p class="alch-section-title">🜔 七大行星天球（Paracelsus 煉金傳統）</p>',
        unsafe_allow_html=True,
    )

    import math

    W, H = 700, 700
    CX, CY, R = 350, 350, 240  # 中心與行星軌道半徑

    # 行星按 Chaldean 順序排列（從 Saturn 開始，逆時針/順時針）
    planet_order = ["saturn", "jupiter", "mars", "sun", "venus", "mercury", "moon"]
    n = len(planet_order)

    # SVG 元素構建
    svg_parts = [f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     style="background:{_BG_DARK};border-radius:12px;max-width:100%">
  <defs>
    <radialGradient id="bgGrad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#2A1A08;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:{_BG_DARK};stop-opacity:1"/>
    </radialGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- 背景 -->
  <rect width="{W}" height="{H}" fill="url(#bgGrad)" rx="12"/>

  <!-- 外裝飾圓 -->
  <circle cx="{CX}" cy="{CY}" r="{R+50}" fill="none" stroke="{_GOLD_DIM}" stroke-width="0.8" stroke-dasharray="4,6"/>
  <circle cx="{CX}" cy="{CY}" r="{R+30}" fill="none" stroke="#5A3A10" stroke-width="0.5"/>
  <circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{_GOLD_DIM}" stroke-width="1.5"/>
  <circle cx="{CX}" cy="{CY}" r="{R-60}" fill="none" stroke="#5A3A10" stroke-width="0.8" stroke-dasharray="2,4"/>

  <!-- 中心文字 -->
  <text x="{CX}" y="{CY-12}" text-anchor="middle" font-family="Georgia,serif"
        font-size="18" fill="{_GOLD_BRIGHT}" filter="url(#glow)">⚗</text>
  <text x="{CX}" y="{CY+10}" text-anchor="middle" font-family="Georgia,serif"
        font-size="11" fill="{_GOLD_DIM}">Opus</text>
  <text x="{CX}" y="{CY+25}" text-anchor="middle" font-family="Georgia,serif"
        font-size="11" fill="{_GOLD_DIM}">Magnum</text>
"""]

    for i, key in enumerate(planet_order):
        c: PlanetCorrespondence = PLANET_CORRESPONDENCES[key]
        # 角度：從頂部開始（-90°），順時針排列
        angle_deg = -90 + (360 / n) * i
        angle_rad = math.radians(angle_deg)
        px = CX + R * math.cos(angle_rad)
        py = CY + R * math.sin(angle_rad)

        # 連線從中心到行星位置（細虛線）
        svg_parts.append(
            f'  <line x1="{CX}" y1="{CY}" x2="{px:.1f}" y2="{py:.1f}" '
            f'stroke="{_GOLD_DIM}" stroke-width="0.6" stroke-dasharray="3,5" opacity="0.5"/>\n'
        )

        # 行星外圈
        svg_parts.append(
            f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="36" '
            f'fill="{_BG_CARD}" stroke="{c.color}" stroke-width="1.8"/>\n'
        )
        # 行星內圈（微光）
        svg_parts.append(
            f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="28" '
            f'fill="{_BG_DARK}" stroke="{c.color}" stroke-width="0.5" opacity="0.6"/>\n'
        )

        # 行星符號
        svg_parts.append(
            f'  <text x="{px:.1f}" y="{py+8:.1f}" text-anchor="middle" '
            f'font-size="22" fill="{c.color}" filter="url(#glow)" '
            f'font-family="serif">{c.symbol}</text>\n'
        )

        # 行星名稱（外側）
        label_r = R + 58
        lx = CX + label_r * math.cos(angle_rad)
        ly = CY + label_r * math.sin(angle_rad)
        svg_parts.append(
            f'  <text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'font-size="11" fill="{_GOLD_DIM}" font-family="Georgia,serif">{c.name_zh}</text>\n'
        )

        # 金屬名稱（行星下方或外側，偏移一點避免重疊）
        metal_r = R - 58
        mx = CX + metal_r * math.cos(angle_rad)
        my = CY + metal_r * math.sin(angle_rad)
        svg_parts.append(
            f'  <text x="{mx:.1f}" y="{my:.1f}" text-anchor="middle" '
            f'font-size="10" fill="{_PARCHMENT}" font-family="Georgia,serif" opacity="0.85">'
            f'{c.metal_latin}</text>\n'
        )

    # 標題
    svg_parts.append(f"""
  <text x="{CX}" y="30" text-anchor="middle" font-family="Palatino Linotype,Georgia,serif"
        font-size="15" fill="{_GOLD_BRIGHT}" letter-spacing="2">
    SEPTEM PLANETAE — 七大行星天球
  </text>
  <text x="{CX}" y="50" text-anchor="middle" font-family="Georgia,serif"
        font-size="10" fill="{_GOLD_DIM}" font-style="italic">
    Paracelsus · Coelum Philosophorum · c.1525
  </text>
</svg>
""")

    svg_html = "".join(svg_parts)
    components.html(svg_html, height=720, scrolling=False)


# ─────────────────────────────────────────────────────────────────────────────
# SVG：煉金四階段輪盤
# ─────────────────────────────────────────────────────────────────────────────

def _render_stage_wheel_svg(active_stage: str = "") -> None:
    """渲染煉金四階段輪盤 SVG（Nigredo→Albedo→Citrinitas→Rubedo）。

    Args:
        active_stage: 當前活躍的煉金階段鍵名（高亮顯示）
    """
    st.markdown(
        '<p class="alch-section-title">🜁 煉金大功四階段（Opus Magnum）</p>',
        unsafe_allow_html=True,
    )

    import math

    W, H = 600, 600
    CX, CY = 300, 300

    # 四個扇形（每個90°）
    stages_order = ["nigredo", "albedo", "citrinitas", "rubedo"]
    stage_vis: dict[str, dict] = {
        "nigredo":   {"color": "#222222", "text_color": "#AAAAAA", "label": "Nigredo\n黑化",   "symbol": "♄", "planet_zh": "土星・鉛"},
        "albedo":    {"color": "#C8D0D8", "text_color": "#334455", "label": "Albedo\n白化",    "symbol": "☽", "planet_zh": "月亮・銀"},
        "citrinitas":{"color": "#B8860B", "text_color": "#FFF8DC", "label": "Citrinitas\n黃化","symbol": "☉", "planet_zh": "太陽・黃金過渡"},
        "rubedo":    {"color": "#8B1A1A", "text_color": "#FFD700", "label": "Rubedo\n赤化",    "symbol": "☉", "planet_zh": "太陽・黃金"},
    }

    R_outer = 220
    R_inner = 90

    svg_parts = [f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     style="background:{_BG_DARK};border-radius:12px;max-width:100%">
  <defs>
    <filter id="glow2">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="{W}" height="{H}" fill="{_BG_DARK}" rx="12"/>
"""]

    for i, stage_key in enumerate(stages_order):
        vis = stage_vis[stage_key]
        start_angle = -90 + i * 90   # 從頂部開始，每段90°
        end_angle = start_angle + 90
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)

        # 扇形路徑（外圓弧 → 內圓弧）
        ox1 = CX + R_outer * math.cos(start_rad)
        oy1 = CY + R_outer * math.sin(start_rad)
        ox2 = CX + R_outer * math.cos(end_rad)
        oy2 = CY + R_outer * math.sin(end_rad)
        ix1 = CX + R_inner * math.cos(end_rad)
        iy1 = CY + R_inner * math.sin(end_rad)
        ix2 = CX + R_inner * math.cos(start_rad)
        iy2 = CY + R_inner * math.sin(start_rad)

        # 高亮活躍階段
        is_active = (stage_key == active_stage)
        stroke_w = "3" if is_active else "1"
        stroke_col = _GOLD_ACCENT if is_active else _GOLD_DIM
        opacity = "1.0" if is_active else "0.82"

        path_d = (
            f"M {ox1:.1f},{oy1:.1f} "
            f"A {R_outer},{R_outer} 0 0,1 {ox2:.1f},{oy2:.1f} "
            f"L {ix1:.1f},{iy1:.1f} "
            f"A {R_inner},{R_inner} 0 0,0 {ix2:.1f},{iy2:.1f} Z"
        )
        svg_parts.append(
            f'  <path d="{path_d}" fill="{vis["color"]}" stroke="{stroke_col}" '
            f'stroke-width="{stroke_w}" opacity="{opacity}"/>\n'
        )

        # 文字位置（扇形中間徑）
        mid_angle = math.radians(start_angle + 45)
        mid_r = (R_outer + R_inner) / 2
        tx = CX + mid_r * math.cos(mid_angle)
        ty = CY + mid_r * math.sin(mid_angle)

        # 行星符號
        svg_parts.append(
            f'  <text x="{tx:.1f}" y="{ty-20:.1f}" text-anchor="middle" '
            f'font-size="20" fill="{vis["text_color"]}" filter="url(#glow2)">'
            f'{vis["symbol"]}</text>\n'
        )

        # 階段名稱
        label_lines = vis["label"].split("\n")
        svg_parts.append(
            f'  <text x="{tx:.1f}" y="{ty+2:.1f}" text-anchor="middle" '
            f'font-size="13" fill="{vis["text_color"]}" font-family="Georgia,serif" font-weight="bold">'
            f'{label_lines[0]}</text>\n'
        )
        if len(label_lines) > 1:
            svg_parts.append(
                f'  <text x="{tx:.1f}" y="{ty+18:.1f}" text-anchor="middle" '
                f'font-size="11" fill="{vis["text_color"]}" font-family="Georgia,serif">'
                f'{label_lines[1]}</text>\n'
            )

        # 行星名稱（更小字體）
        svg_parts.append(
            f'  <text x="{tx:.1f}" y="{ty+35:.1f}" text-anchor="middle" '
            f'font-size="9" fill="{vis["text_color"]}" font-family="Georgia,serif" opacity="0.8">'
            f'{vis["planet_zh"]}</text>\n'
        )

        # 若為活躍階段，加高亮光環
        if is_active:
            svg_parts.append(
                f'  <path d="{path_d}" fill="none" stroke="{_GOLD_ACCENT}" '
                f'stroke-width="4" opacity="0.3" filter="url(#glow2)"/>\n'
            )

    # 中心圓
    svg_parts.append(
        f'  <circle cx="{CX}" cy="{CY}" r="{R_inner}" '
        f'fill="{_BG_DARK}" stroke="{_GOLD_DIM}" stroke-width="1.5"/>\n'
    )
    svg_parts.append(
        f'  <text x="{CX}" y="{CY-8}" text-anchor="middle" '
        f'font-size="18" fill="{_GOLD_BRIGHT}" filter="url(#glow2)">⚗</text>\n'
    )
    svg_parts.append(
        f'  <text x="{CX}" y="{CY+14}" text-anchor="middle" '
        f'font-size="10" fill="{_GOLD_DIM}" font-family="Georgia,serif">Opus Magnum</text>\n'
    )

    # 四個方向箭頭（順時針）
    arrow_r = R_outer + 28
    for i, (angle_deg, label) in enumerate(zip([0, 90, 180, 270], ["↓", "←", "↑", "→"])):
        ax = CX + arrow_r * math.cos(math.radians(angle_deg - 90))
        ay = CY + arrow_r * math.sin(math.radians(angle_deg - 90))
        svg_parts.append(
            f'  <text x="{ax:.1f}" y="{ay+4:.1f}" text-anchor="middle" '
            f'font-size="14" fill="{_GOLD_DIM}" opacity="0.6">{label}</text>\n'
        )

    # 標題
    svg_parts.append(f"""
  <text x="{CX}" y="28" text-anchor="middle" font-family="Palatino Linotype,Georgia,serif"
        font-size="14" fill="{_GOLD_BRIGHT}" letter-spacing="2">
    OPUS MAGNUM — 煉金大功四階段
  </text>
  <text x="{CX}" y="46" text-anchor="middle" font-family="Georgia,serif"
        font-size="9" fill="{_GOLD_DIM}" font-style="italic">
    Paracelsus · Coelum Philosophorum · Nigredo · Albedo · Citrinitas · Rubedo
  </text>
</svg>
""")

    svg_html = "".join(svg_parts)
    components.html(svg_html, height=620, scrolling=False)


# ─────────────────────────────────────────────────────────────────────────────
# 個人星盤煉金解讀
# ─────────────────────────────────────────────────────────────────────────────

def _render_personal_reading(reading: AlchemicalReading) -> None:
    """渲染個人星盤的煉金占星解讀。

    Args:
        reading: AlchemicalReading 解讀結果
    """
    st.markdown(
        '<p class="alch-section-title">✦ 個人煉金星盤解讀</p>',
        unsafe_allow_html=True,
    )

    dom = reading.dominant_profile
    if dom is None:
        st.warning("無法計算主導行星。")
        return

    # 主導行星卡片
    stage_colors_bg = {
        "nigredo": "#1A1A1A",
        "albedo": "#D0D8E0",
        "citrinitas": "#2A1E00",
        "rubedo": "#2A0000",
    }
    stage_bg = stage_colors_bg.get(reading.alchemical_stage_key, _BG_CARD)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            f"""
<div class="alch-card" style="text-align:center;border-color:{dom.color}">
  <div style="font-size:3rem;color:{dom.color};text-shadow:0 0 20px {dom.color}80">
    {dom.symbol}
  </div>
  <div style="color:{_GOLD_BRIGHT};font-size:1.1rem;font-weight:bold;margin:8px 0">
    {dom.name_zh}
  </div>
  <div class="alch-dominant-badge">主導行星</div>
  <div style="color:{_INK};margin-top:10px;font-size:0.85rem">
    尊貴評分：{dom.dignity_score}
  </div>
  <div style="color:{_GOLD_DIM};font-size:0.9rem;margin-top:6px">
    {dom.metal_symbol} {dom.metal_zh}
  </div>
  <div style="color:{_PARCHMENT};font-size:0.8rem;margin-top:4px">
    {dom.metal_latin}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col2:
        stage_info = reading.alchemical_stage_info
        stage_name = stage_info.name_zh if stage_info else reading.alchemical_stage_key
        st.markdown(
            f"""
<div class="alch-card" style="background:{stage_bg}80;border-color:{_GOLD_DIM}">
  <div style="color:{_GOLD_DIM};font-size:0.8rem;margin-bottom:4px">當前煉金階段</div>
  <div style="color:{_GOLD_BRIGHT};font-size:1.1rem;font-weight:bold">{stage_name}</div>
  <hr style="border-color:{_GOLD_DIM}30;margin:8px 0">
  <div style="color:{_INK};font-size:0.85rem;line-height:1.6">
    <b style="color:{_GOLD_DIM}">人體部位：</b>{dom.body_part_zh}<br>
    <b style="color:{_GOLD_DIM}">氣質類型：</b>{dom.temperament_zh}<br>
    <b style="color:{_GOLD_DIM}">草本建議：</b>{'、'.join(reading.herb_recommendations_zh[:3])}<br>
    <b style="color:{_GOLD_DIM}">礦石建議：</b>{'、'.join(reading.mineral_recommendations_zh[:3])}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    # 個人解讀摘要
    if reading.summary_zh:
        with st.expander("📜 詳細煉金解讀（帕拉塞爾蘇斯傳統）", expanded=True):
            st.markdown(reading.summary_zh)

    # 煉金階段解讀
    if reading.stage_reading_zh:
        with st.expander(f"🜔 {stage_name} 深度解讀", expanded=False):
            st.markdown(reading.stage_reading_zh)

    # 行星尊貴評分表
    with st.expander("⚖ 七大行星尊貴評分", expanded=False):
        score_cols = st.columns(len(PLANET_KEYS))
        for col, key in zip(score_cols, PLANET_KEYS):
            c = PLANET_CORRESPONDENCES[key]
            score = reading.dignity_scores.get(key, 1)
            is_dom = (key == reading.dominant_planet)
            border_style = f"2px solid {_GOLD_ACCENT}" if is_dom else f"1px solid {_GOLD_DIM}30"
            col.markdown(
                f"""
<div style="text-align:center;padding:8px 4px;border:{border_style};
            border-radius:6px;background:{_BG_CARD}">
  <div style="font-size:1.3rem;color:{c.color}">{c.symbol}</div>
  <div style="font-size:0.72rem;color:{_GOLD_DIM}">{c.name_zh.split('（')[0]}</div>
  <div style="font-size:1.1rem;font-weight:bold;color:{'#F0C040' if is_dom else _INK}">{score}</div>
</div>
""",
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# 物質印記說展示
# ─────────────────────────────────────────────────────────────────────────────

def _render_signatures_section(reading: Optional[AlchemicalReading] = None) -> None:
    """渲染物質印記說（Signatura Rerum）展示區。

    Args:
        reading: 若提供，則高亮主導行星的印記說；否則顯示所有行星。
    """
    st.markdown(
        '<p class="alch-section-title">🌿 物質印記說（Signatura Rerum）</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="alch-card" style="margin-bottom:16px">
  <div style="color:{_GOLD_DIM};font-size:0.85rem;line-height:1.7">
    帕拉塞爾蘇斯的「物質印記說」（Signatura Rerum）主張：宇宙中每個行星在自然界留下可辨識的「印記」。
    草藥的形狀、顏色、氣味、生長環境，乃至礦石的晶體結構，皆映射著對應行星的宇宙振動（<em>virtus</em>）。
    醫者應藉此辨識藥物歸屬，以「同性相療」原則運用草本治療對應行星失衡所引發的疾病。
  </div>
  <div class="alch-citation">
    ✦ 來源：Paracelsus, <em>Opus Paramirum</em> (1531)；<em>De Natura Rerum</em> (1537)；
    Jakob Boehme, <em>Signatura Rerum</em> (1621)
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # 若有解讀，優先展示主導行星的印記說
    dominant_key = reading.dominant_planet if reading else None
    display_keys = PLANET_KEYS

    for key in display_keys:
        c: PlanetCorrespondence = PLANET_CORRESPONDENCES[key]
        sig_text = reading.signature_descriptions.get(key, "") if reading else ""

        is_dominant = (key == dominant_key)
        border_col = _GOLD_ACCENT if is_dominant else f"{_GOLD_DIM}40"
        dom_badge = '<span class="alch-dominant-badge" style="margin-left:8px;font-size:0.78rem">主導</span>' if is_dominant else ""

        with st.expander(
            f"{c.symbol} {c.name_zh} — {c.metal_zh} · {c.metal_latin}{' ★' if is_dominant else ''}",
            expanded=is_dominant,
        ):
            if sig_text:
                st.markdown(
                    f"""
<div style="color:{_INK};line-height:1.75;font-size:0.9rem">{sig_text}</div>
<div class="alch-citation">✦ {c.source}</div>
""",
                    unsafe_allow_html=True,
                )
            else:
                st.info("印記說資料載入中…")


# ─────────────────────────────────────────────────────────────────────────────
# 文獻來源
# ─────────────────────────────────────────────────────────────────────────────

def _render_citations() -> None:
    """渲染學術文獻來源區。"""
    st.markdown(
        '<p class="alch-section-title">📚 歷史文獻來源</p>',
        unsafe_allow_html=True,
    )

    citations_html = f"""
<div class="alch-card">
  <div style="color:{_GOLD_DIM};font-size:0.82rem;line-height:2.0">
    <b style="color:{_GOLD_BRIGHT}">一手文獻（帕拉塞爾蘇斯 Paracelsus, 1493–1541）：</b><br>
    1. <em>Coelum Philosophorum</em>（天哲學）, c.1525 — 行星金屬與煉金階段<br>
    2. <em>Astronomia Magna</em>（偉大天文學）, 1537–38 — 行星藥草與人體對應<br>
    3. <em>De Natura Rerum</em>（自然之物論）, 1537 — 礦物與植物印記<br>
    4. <em>Concerning the Spirits of the Planets</em>（論行星靈）, c.1530 — 水星・金星對應<br>
    5. <em>Opus Paramirum</em>（超越奇蹟之作）, 1531 — 物質印記說核心<br>
    6. <em>De Mineralibus</em>（礦物論）— 土星・鉛對應<br>
    7. <em>Archidoxes of Magic</em>（神秘哲學七書）— 煉金草本實踐<br>
    <br>
    <b style="color:{_GOLD_BRIGHT}">二手文獻：</b><br>
    8. Cornelius Agrippa, <em>Three Books of Occult Philosophy</em>（神秘哲學三書）, 1531 — Book I, Ch. XXIII–XXIV<br>
    9. Marsilio Ficino, <em>De Vita Libri Tres</em>（三生命書）, 1489 — 行星醫學<br>
    10. Jakob Boehme, <em>Signatura Rerum</em>（物質印記論）, 1621 — 發展帕拉塞爾蘇斯概念<br>
  </div>
</div>
"""
    st.markdown(citations_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────────────────────────

def render_alchemical_tab(
    planet_longitudes: Optional[dict] = None,
    after_chart_hook: Optional[Callable] = None,
) -> None:
    """煉金占星學（Alchemical Astrology）Streamlit 標籤頁主入口。

    Args:
        planet_longitudes: 行星黃道度數字典（可選），
            鍵名為小寫行星名（"sun", "moon", "mars", "mercury",
            "jupiter", "venus", "saturn"）。
            若為 None，則僅顯示通用資訊（不計算個人解讀）。
        after_chart_hook: 可選的後鉤函數，在圖表後調用（可為 None）。
    """
    # 頁頭
    _render_header()

    # 七大行星對應關係表格
    _render_correspondence_table()

    # SVG 可視化（可摺疊）
    with st.expander("🌐 七大行星天球 SVG（點擊展開）", expanded=True):
        _render_planets_svg()

    # 煉金四階段輪盤
    # 若有個人星盤，先計算以確定活躍階段
    reading: Optional[AlchemicalReading] = None
    active_stage = ""

    if planet_longitudes and isinstance(planet_longitudes, dict):
        try:
            reading = compute_reading(planet_longitudes)
            active_stage = reading.alchemical_stage_key
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            st.warning(f"計算煉金解讀時出現錯誤：{e}")
            reading = None

    with st.expander("🜔 煉金大功四階段輪盤 SVG（點擊展開）", expanded=True):
        _render_stage_wheel_svg(active_stage=active_stage)

    # 個人解讀（若有星盤輸入）
    if reading is not None:
        _render_personal_reading(reading)
    else:
        st.info(
            "💡 **提示**：輸入您的出生星盤行星度數（planet_longitudes），"
            "即可獲得個人化的煉金占星解讀。"
        )

    # 物質印記說展示
    st.markdown("---")
    _render_signatures_section(reading=reading)

    # 文獻來源
    st.markdown("---")
    _render_citations()

    # 後鉤（若有）
    if after_chart_hook is not None:
        after_chart_hook()
