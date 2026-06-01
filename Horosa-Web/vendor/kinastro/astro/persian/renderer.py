"""
astro/persian/renderer.py — 薩珊波斯高階占星 Streamlit 渲染器

Advanced Sassanian / Persian Astrology Streamlit Renderer
波斯傳統風格界面：深靛藍、金色、藏紅花色、綠松石色

Features:
- 菱形 12 宮 SVG 星盤
- Firdaria 互動時間軸
- Hyleg & Alcocoden 壽命計算
- Almuten Figuris 命主星
- 年度 + 月度主限
- 埃及界 / 三分守護星
- 多德卡特摩里亞 / 反射點
- 擴展波斯阿拉伯點
- Dorotheus 風格解讀

Color Palette: Deep Indigo, Antique Gold, Saffron, Persian Turquoise
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Any

import streamlit as st

from .calculator import (
    DeepSassanianChart,
    DeepPlanetPos,
    DeepFirdarPeriod,
    DeepFirdarSubPeriod,
    DeepHylegResult,
    DeepAlcocodenResult,
    DeepAlmutenResult,
    DeepProfectionYear,
    DeepArabicPart,
    DeepRoyalStar,
    TriplicityInfo,
    DorotheusSummary,
    compute_deep_sassanian_chart,
)
from .constants import (
    PERSIAN_COLORS,
    PLANET_COLORS,
    PLANET_NAMES_CN,
    PLANET_GLYPHS,
    ZODIAC_SIGNS,
    PLANET_NATURE,
    HOUSE_SIGNIFICATIONS,
)
from astro.i18n import auto_cn, get_lang, t

# ═══════════════════════════════════════════════════════════════
# CSS — Persian Gold & Indigo Aesthetic
# ═══════════════════════════════════════════════════════════════

_CSS = """
<style>
/* ── Persian Header ───────────────────────────────────── */
.per-header {
    background: linear-gradient(135deg, #0d0d1a 0%, #1a1040 40%, #0d0d1a 100%);
    border: 2px solid #D4AF37;
    border-radius: 8px;
    padding: 18px 24px;
    margin-bottom: 18px;
    box-shadow: 0 0 28px rgba(212,175,55,0.22);
    position: relative;
    overflow: hidden;
}
.per-header::before {
    content: '✦';
    position: absolute;
    right: 22px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 3.5em;
    color: rgba(212,175,55,0.12);
    pointer-events: none;
}
.per-header h2 { color: #D4AF37; margin: 0 0 4px 0; font-size: 1.45em; letter-spacing: 0.06em; }
.per-header p  { color: #c4a46a; margin: 0; font-size: 0.86em; }

/* ── Gold Divider ───────────────────────────────────── */
.per-divider { border: none; border-top: 1px solid #D4AF3744; margin: 14px 0; }

/* ── Planet Cards ───────────────────────────────────── */
.per-planet-card {
    background: rgba(13, 10, 26, 0.92);
    border: 1px solid #D4AF3740;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 7px;
    transition: border-color 0.2s;
}
.per-planet-card:hover { border-color: #D4AF37; }
.per-planet-card h4 { color: #D4AF37; margin: 0 0 3px 0; font-size: 1em; }
.per-planet-card .pos { color: #e8d4a8; font-size: 0.9em; }
.per-planet-card .dig { font-size: 0.78em; padding: 2px 7px; border-radius: 3px; margin-top: 3px; display: inline-block; }
.dig-domicile    { background: rgba(46,204,113,0.2);  color: #2ecc71; }
.dig-exaltation  { background: rgba(212,175,55,0.2);  color: #D4AF37; }
.dig-detriment   { background: rgba(231,76,60,0.2);   color: #e74c3c; }
.dig-fall        { background: rgba(155,89,182,0.2);  color: #9b59b6; }
.dig-triplicity  { background: rgba(26,188,156,0.2);  color: #1abc9c; }
.dig-bound       { background: rgba(52,152,219,0.2);  color: #3498db; }
.dig-face        { background: rgba(149,165,166,0.2); color: #95a5a6; }
.dig-peregrine   { background: rgba(100,100,100,0.15); color: #888; }

/* ── Firdaria ─────────────────────────────────────────── */
.per-firdar-current {
    background: linear-gradient(90deg, rgba(212,175,55,0.18), rgba(212,175,55,0.04));
    border: 1px solid #D4AF37;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
}
.per-firdar-regular {
    background: rgba(13, 10, 26, 0.85);
    border: 1px solid #D4AF3730;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
}
.per-firdar-lord { color: #D4AF37; font-weight: bold; font-size: 1.05em; }
.per-firdar-dates { color: #c4a46a; font-size: 0.82em; }

/* ── Hyleg / Alcocoden ──────────────────────────────── */
.per-hyleg-card {
    background: linear-gradient(135deg, rgba(13,10,26,0.95), rgba(26,16,64,0.95));
    border: 2px solid #D4AF37;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.per-hyleg-card h3 { color: #D4AF37; margin: 0 0 6px 0; }
.per-alcocoden-card {
    background: linear-gradient(135deg, rgba(13,10,26,0.95), rgba(16,26,26,0.95));
    border: 2px solid #1ABC9C;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.per-alcocoden-card h3 { color: #1ABC9C; margin: 0 0 6px 0; }

/* ── Almuten ─────────────────────────────────────────── */
.per-almuten-card {
    background: linear-gradient(135deg, rgba(13,10,26,0.98), rgba(26,10,26,0.98));
    border: 3px solid #E67E22;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
    margin-bottom: 14px;
}
.per-almuten-card h2 { color: #E67E22; margin: 0; font-size: 2em; }
.per-almuten-card p  { color: #c4a46a; margin: 4px 0 0 0; font-size: 0.9em; }

/* ── Profection ──────────────────────────────────────── */
.per-prof-current {
    background: linear-gradient(90deg, rgba(26,188,156,0.15), rgba(26,188,156,0.04));
    border: 1px solid #1ABC9C;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.per-prof-regular {
    background: rgba(13, 10, 26, 0.8);
    border: 1px solid #1ABC9C30;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 5px;
}

/* ── Arabic Parts ─────────────────────────────────────── */
.per-lot-card {
    background: rgba(10, 8, 20, 0.9);
    border: 1px solid #8B691455;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 5px;
}
.per-lot-card h5 { color: #C9A84C; margin: 0 0 3px 0; font-size: 0.9em; }
.per-lot-card .arabic { color: #6b5b35; font-size: 0.8em; font-style: italic; }

/* ── Royal Stars ─────────────────────────────────────── */
.per-star-prominent {
    background: linear-gradient(90deg, rgba(212,175,55,0.14), rgba(230,126,34,0.08));
    border: 1px solid #D4AF37;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
}
.per-star-inactive {
    background: rgba(13, 10, 26, 0.75);
    border: 1px solid #D4AF3725;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 5px;
    opacity: 0.6;
}

/* ── Dorotheus Interpretation ────────────────────────── */
.per-dorotheus {
    background: linear-gradient(135deg, rgba(13,10,26,0.98), rgba(26,20,10,0.98));
    border: 2px solid #E67E22;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 14px;
}
.per-dorotheus h3 { color: #E67E22; margin: 0 0 8px 0; font-size: 1.2em; }
.per-dorotheus .topic { color: #D4AF37; font-weight: bold; margin-top: 10px; margin-bottom: 3px; }
.per-dorotheus .text { color: #c4a46a; font-size: 0.88em; line-height: 1.55; }

/* ── Section Badge ───────────────────────────────────── */
.per-badge {
    display: inline-block;
    background: rgba(212,175,55,0.15);
    border: 1px solid #D4AF3760;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78em;
    color: #D4AF37;
    margin-left: 8px;
    vertical-align: middle;
}

/* ── Source Reference ────────────────────────────────── */
.per-source { color: #4a4232; font-size: 0.72em; font-style: italic; margin-top: 4px; }
</style>
"""

# ═══════════════════════════════════════════════════════════════
# SVG Diamond Chart
# ═══════════════════════════════════════════════════════════════

def _build_diamond_chart_svg(chart: DeepSassanianChart) -> str:
    """
    Build a diamond (菱形) 12-house SVG chart in the traditional South-Asian /
    Persian manuscript style.

    Layout (clockwise from top):
    Top triangle = house 10, right = house 1 (ASC), bottom = house 4, left = house 7
    """
    W, H = 480, 480
    cx, cy = 240, 240
    half = 200  # half-size of outer square

    C = PERSIAN_COLORS
    SIGN_GLYPHS = [z[1] for z in ZODIAC_SIGNS]

    asc_sign_idx = int(chart.ascendant // 30) % 12

    # Build planet-by-house mapping
    house_planets: Dict[int, List[DeepPlanetPos]] = {i: [] for i in range(1, 13)}
    for p in chart.planets:
        house_planets[p.house].append(p)

    # Arabic parts in houses
    part_houses: Dict[int, List[DeepArabicPart]] = {i: [] for i in range(1, 13)}
    for ap in chart.arabic_parts[:6]:  # show first 6 parts
        part_houses[ap.house].append(ap)

    def planet_color(name: str) -> str:
        return PLANET_COLORS.get(name, C["text_primary"])

    def house_to_sign_idx(house: int) -> int:
        return (asc_sign_idx + house - 1) % 12

    # Diamond chart geometry:
    # House positions (center of each triangle sector):
    # Standard Indian/Persian diamond: 12 houses in 4 corners + 8 edges
    # House 1 = right corner (ASC), House 10 = top, House 7 = bottom, House 4 = left
    # We use the standard South/East Asian 12-cell diamond layout.

    # Standard diamond (12-cell) layout used in Indian/Persian astrology:
    # Outer diamond vertices (tilted square):
    OT = (cx,        cy - half)   # top
    OR = (cx + half, cy)          # right
    OB = (cx,        cy + half)   # bottom
    OL = (cx - half, cy)          # left
    center = (cx, cy)

    # Edge midpoints of outer diamond:
    MT = ((OT[0]+OR[0])//2, (OT[1]+OR[1])//2)  # top-right edge mid
    MR = ((OR[0]+OB[0])//2, (OR[1]+OB[1])//2)  # right-bottom edge mid
    MB = ((OB[0]+OL[0])//2, (OB[1]+OL[1])//2)  # bottom-left edge mid
    ML = ((OL[0]+OT[0])//2, (OL[1]+OT[1])//2)  # left-top edge mid

    # Inner diamond (half size):
    IT = (cx,        cy - half//2)
    IR = (cx + half//2, cy)
    IB = (cx,        cy + half//2)
    IL = (cx - half//2, cy)

    # 12 cells (standard Indian diamond layout):
    cells: Dict[int, Dict] = {
        1:  {"poly": [OR, MT, IT, IR],           "tc": ((OR[0]+MT[0]+IT[0]+IR[0])//4, (OR[1]+MT[1]+IT[1]+IR[1])//4)},
        2:  {"poly": [OT, MT, IT, center],        "tc": ((OT[0]+MT[0])//2,            (OT[1]+MT[1])//2 - 10)},
        3:  {"poly": [OT, ML, center, IT],         "tc": ((OT[0]+ML[0])//2,            (OT[1]+ML[1])//2 - 10)},
        4:  {"poly": [OL, ML, IL, center],         "tc": ((OL[0]+ML[0]+IL[0]+center[0])//4, (OL[1]+ML[1]+IL[1]+center[1])//4)},
        5:  {"poly": [OL, MB, center, IL],         "tc": ((OL[0]+MB[0])//2 - 8,        (OL[1]+MB[1])//2)},
        6:  {"poly": [OB, MB, IB, center],         "tc": ((OB[0]+MB[0])//2 - 8,        (OB[1]+MB[1])//2)},
        7:  {"poly": [OB, MB, IB, MR],             "tc": ((OB[0]+MB[0]+IB[0]+MR[0])//4,(OB[1]+MB[1]+IB[1]+MR[1])//4)},
        8:  {"poly": [OB, MR, center, IB],         "tc": ((OB[0]+MR[0])//2 + 8,        (OB[1]+MR[1])//2)},
        9:  {"poly": [OR, MR, center, IR],         "tc": ((OR[0]+MR[0])//2 + 8,        (OR[1]+MR[1])//2)},
        10: {"poly": [OT, MT, center, IT],         "tc": (cx,                           cy - half*3//4)},
        11: {"poly": [OT, center, IL, OL],         "tc": ((OT[0]+OL[0])//2,            (OT[1]+OL[1])//2 - 5)},
        12: {"poly": [OT, IT, center, MT],         "tc": (cx,                           cy - half//2 - 15)},
    }

    # Generate SVG
    lines: List[str] = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
                 f'width="{W}" height="{H}" style="background:{C["background"]};">')

    # Defs: subtle radial glow
    lines.append('<defs>')
    lines.append('<radialGradient id="bgGlow" cx="50%" cy="50%" r="50%">')
    lines.append(f'<stop offset="0%" style="stop-color:{C["card_bg"]};stop-opacity:0.6"/>')
    lines.append(f'<stop offset="100%" style="stop-color:{C["background"]};stop-opacity:0"/>')
    lines.append('</radialGradient>')
    lines.append('</defs>')
    lines.append(f'<ellipse cx="{cx}" cy="{cy}" rx="220" ry="220" fill="url(#bgGlow)"/>')

    # Draw 12 house cells
    HOUSE_FILL = "rgba(13,10,26,0.85)"
    HOUSE_STROKE = C["card_border"]

    for h_num in range(1, 13):
        cell = cells[h_num]
        pts = cell["poly"]
        poly_str = " ".join(f"{int(p[0])},{int(p[1])}" for p in pts)
        is_asc_house = (h_num == 1)
        fill = f"rgba(26,16,64,0.9)" if is_asc_house else HOUSE_FILL
        stroke_w = "1.5" if is_asc_house else "1"
        lines.append(f'<polygon points="{poly_str}" '
                     f'fill="{fill}" stroke="{HOUSE_STROKE}" stroke-width="{stroke_w}"/>')

    # House numbers and sign glyphs
    for h_num in range(1, 13):
        cell = cells[h_num]
        tx, ty = int(cell["tc"][0]), int(cell["tc"][1])
        sign_idx = house_to_sign_idx(h_num)
        sign_glyph = SIGN_GLYPHS[sign_idx]

        # House number (small)
        lines.append(f'<text x="{tx}" y="{ty-12}" text-anchor="middle" '
                     f'font-size="10" fill="{C["text_muted"]}">{h_num}</text>')
        # Sign glyph
        lines.append(f'<text x="{tx}" y="{ty+2}" text-anchor="middle" '
                     f'font-size="14" fill="{C["accent_gold"]}">{sign_glyph}</text>')

        # Planet glyphs
        planets_in_house = house_planets.get(h_num, [])
        for pi, p in enumerate(planets_in_house):
            col = planet_color(p.name)
            px = tx + (pi - len(planets_in_house)//2) * 12
            py = ty + 16 + pi * 12
            retro_marker = "℞" if p.is_retrograde else ""
            lines.append(f'<text x="{px}" y="{py}" text-anchor="middle" '
                         f'font-size="11" fill="{col}">{p.glyph}{retro_marker}</text>')

    # ASC marker
    asc_tx, asc_ty = int(cells[1]["tc"][0]), int(cells[1]["tc"][1])
    lines.append(f'<text x="{asc_tx}" y="{asc_ty - 28}" text-anchor="middle" '
                 f'font-size="9" fill="{C["accent_saffron"]}" font-weight="bold">ASC</text>')

    # Title
    lines.append(f'<text x="{cx}" y="22" text-anchor="middle" '
                 f'font-size="13" fill="{C["accent_gold"]}" font-weight="bold">'
                 f'薩珊波斯 進階版</text>')

    # Day/Night indicator
    sect_text = "☀ 日間盤" if chart.is_day_chart else "☽ 夜間盤"
    sect_color = C["sun_color"] if chart.is_day_chart else C["moon_color"]
    lines.append(f'<text x="{cx}" y="{H-8}" text-anchor="middle" '
                 f'font-size="10" fill="{sect_color}">{sect_text}</text>')

    lines.append('</svg>')
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# Section Renderers
# ═══════════════════════════════════════════════════════════════

def _render_header(chart: DeepSassanianChart) -> None:
    """Render the Persian-style page header."""
    sect = "☀️ 日間盤 (Diurnal)" if chart.is_day_chart else "🌙 夜間盤 (Nocturnal)"
    st.markdown(f"""
<div class="per-header">
  <h2>🏛️ {t('tab_persian_deep')} — 薩珊波斯・進階版</h2>
  <p>{chart.year}-{chart.month:02d}-{chart.day:02d}
     &nbsp;|&nbsp; ASC: {chart.asc_sign} ({chart.asc_sign_cn})
     &nbsp;|&nbsp; {sect}
  </p>
</div>
""", unsafe_allow_html=True)


def _render_planet_table(chart: DeepSassanianChart) -> None:
    """Render planet positions as styled HTML cards."""
    DIGNITY_CSS = {
        "Domicile":       "dig-domicile",
        "Exaltation":     "dig-exaltation",
        "Detriment":      "dig-detriment",
        "Fall":           "dig-fall",
        "Triplicity":     "dig-triplicity",
        "Bound (Egyptian)":"dig-bound",
        "Face (Decan)":   "dig-face",
        "Peregrine":      "dig-peregrine",
    }

    cards = []
    for p in chart.planets:
        d_css = DIGNITY_CSS.get(p.dignity, "dig-peregrine")
        retro = " ℞" if p.is_retrograde else ""
        sect_mark = "⊙" if p.is_in_sect else "⊗"
        col = PLANET_COLORS.get(p.name, "#D4AF37")
        cards.append(f"""
<div class="per-planet-card">
  <h4 style="color:{col}">{p.glyph} {p.name} / {p.name_cn}{retro}</h4>
  <div class="pos">{p.sign} {p.degree_in_sign:.1f}° ({p.sign_cn}) &nbsp;· 第{p.house}宮 &nbsp;· {sect_mark}</div>
  <span class="dig {d_css}">{p.dignity} ({p.dignity_cn})</span>
  <span style="font-size:0.75em;color:#666;margin-left:8px;">
    Antiscion: {p.antiscion_sign} &nbsp;| Dodec: {p.dodecatemoria_sign}
  </span>
</div>""")

    cols = st.columns(2)
    half = len(cards) // 2
    with cols[0]:
        st.markdown("".join(cards[:half]), unsafe_allow_html=True)
    with cols[1]:
        st.markdown("".join(cards[half:]), unsafe_allow_html=True)


def _render_firdaria(chart: DeepSassanianChart) -> None:
    """Render Firdaria timeline with sub-periods."""
    st.markdown(f"""
<div style="background:rgba(13,10,26,0.8);border:1px solid #D4AF3740;border-radius:8px;padding:12px 16px;margin-bottom:12px;">
  <span style="color:#D4AF37;font-weight:bold;font-size:1.05em;">序列 / Sequence: </span>
  <span style="color:#c4a46a;font-size:0.9em;">
    {'☀ 日間盤：太陽→金星→水星→月亮→土星→木星→火星' if chart.is_day_chart
     else '🌙 夜間盤：月亮→土星→木星→火星→太陽→金星→水星'}
  </span>
</div>""", unsafe_allow_html=True)

    # Show current period prominently
    if chart.current_firdaria:
        cf = chart.current_firdaria
        csub = chart.current_sub
        sub_info = f" / {csub.sub_glyph} {csub.sub_lord} ({csub.sub_lord_cn})" if csub else ""
        st.markdown(f"""
<div class="per-firdar-current">
  <span class="per-firdar-lord">🔮 {cf.major_glyph} {cf.major_lord} ({cf.major_lord_cn}){sub_info}</span><br>
  <span class="per-firdar-dates">{cf.start_date} → {cf.end_date} ({cf.duration_years:.0f} 年)</span>
</div>""", unsafe_allow_html=True)

    # Full timeline
    for i, fp in enumerate(chart.firdaria):
        css_class = "per-firdar-current" if fp.is_current else "per-firdar-regular"
        mark = "🔮 " if fp.is_current else ""
        with st.expander(
            f"{mark}{fp.major_glyph} {fp.major_lord} ({fp.major_lord_cn}) · "
            f"{fp.start_date[:4]}–{fp.end_date[:4]} · {fp.duration_years:.0f}yr",
            expanded=fp.is_current,
        ):
            sub_rows = []
            for sp in fp.sub_periods:
                cur_m = "🔮 " if sp.is_current else ""
                sub_rows.append({
                    "子週期": f"{cur_m}{sp.sub_glyph} {sp.sub_lord} ({sp.sub_lord_cn})",
                    "起始": sp.start_date,
                    "結束": sp.end_date,
                    "年數": f"{sp.duration_years:.2f}",
                })
            if sub_rows:
                st.dataframe(sub_rows, width="stretch")


def _render_hyleg_alcocoden(chart: DeepSassanianChart) -> None:
    """Render Hyleg & Alcocoden."""
    col1, col2 = st.columns(2)

    with col1:
        h = chart.hyleg
        if h:
            st.markdown(f"""
<div class="per-hyleg-card">
  <h3>🌟 Hyleg (生命給予者)</h3>
  <p style="font-size:1.3em;color:#D4AF37;margin:4px 0">{h.hyleg_glyph} {h.hyleg_planet} ({h.hyleg_cn})</p>
  <p style="color:#e8d4a8;font-size:0.9em;">
    {h.sign} {h.degree:.1f}° ({h.sign_cn})<br>
    第 {h.house} 宮<br>
    {h.reason_cn}
  </p>
</div>""", unsafe_allow_html=True)

    with col2:
        a = chart.alcocoden
        if a:
            st.markdown(f"""
<div class="per-alcocoden-card">
  <h3>⏳ Alcocoden (壽命給予者)</h3>
  <p style="font-size:1.3em;color:#1ABC9C;margin:4px 0">{a.lord_glyph} {a.lord} ({a.lord_cn})</p>
  <p style="color:#e8d4a8;font-size:0.9em;">
    最短年數 (Minor): {a.base_years_minor} 年<br>
    中等年數 (Middle): {a.base_years_middle} 年<br>
    最長年數 (Major): {a.base_years_major} 年<br>
    修正後估算: <strong style="color:#1ABC9C">{a.modified_years:.1f} 年</strong>
  </p>
  {f'<p style="color:#888;font-size:0.78em;">相位修正: {" ".join(a.aspect_modifiers)}</p>' if a.aspect_modifiers else ""}
</div>""", unsafe_allow_html=True)

    if chart.alcocoden:
        st.caption(chart.alcocoden.reason_cn)


def _render_almuten(chart: DeepSassanianChart) -> None:
    """Render Almuten Figuris (chart ruler)."""
    alm = chart.almuten
    if not alm:
        st.warning("無法計算 Almuten Figuris")
        return

    col_main, col_scores = st.columns([1, 2])

    with col_main:
        st.markdown(f"""
<div class="per-almuten-card">
  <h2>{alm.planet_glyph}</h2>
  <p><strong>{alm.planet}</strong><br>{alm.planet_cn}</p>
  <p style="color:#D4AF37;font-size:1.1em;">總分 {alm.total_score:.1f}</p>
</div>""", unsafe_allow_html=True)
        st.caption(alm.reason_cn)

    with col_scores:
        st.subheader("所有行星尊嚴分數")
        score_rows = []
        for pname in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
            sc = alm.all_scores.get(pname, 0.0)
            is_best = pname == alm.planet
            score_rows.append({
                "行星": f"{'👑 ' if is_best else ''}{PLANET_GLYPHS.get(pname,'')} {pname} ({PLANET_NAMES_CN.get(pname,'')})",
                "分數": f"{sc:.1f}",
            })
        st.dataframe(score_rows, width="stretch")

        if alm.breakdown:
            st.subheader(f"{alm.planet} 尊嚴細項")
            bkd_rows = [{"關鍵點": k, "貢獻分數": f"{v:.1f}"} for k, v in alm.breakdown.items()]
            st.dataframe(bkd_rows, width="stretch")


def _render_profections(chart: DeepSassanianChart) -> None:
    """Render annual and monthly profections."""
    # Current highlights
    if chart.current_annual_prof:
        ap = chart.current_annual_prof
        st.markdown(f"""
<div class="per-prof-current">
  <strong style="color:#1ABC9C">📅 當前年度主限 (Age {ap.age})</strong>
  &nbsp; {ap.sign_glyph} {ap.sign_cn} ({ap.sign}) &nbsp;·&nbsp;
  {ap.lord_glyph} {ap.lord} ({ap.lord_cn})
  <br><span style="color:#888;font-size:0.82em;">{ap.start_date} → {ap.end_date}
  &nbsp;| 宮位含義: {ap.signification_cn}</span>
</div>""", unsafe_allow_html=True)

    if chart.current_monthly_prof:
        mp = chart.current_monthly_prof
        st.markdown(f"""
<div class="per-prof-current" style="border-color:#E67E22;">
  <strong style="color:#E67E22">🗓️ 當前月度主限 (Month {mp.month})</strong>
  &nbsp; {mp.sign_glyph} {mp.sign_cn} ({mp.sign}) &nbsp;·&nbsp;
  {mp.lord_glyph} {mp.lord} ({mp.lord_cn})
  <br><span style="color:#888;font-size:0.82em;">{mp.start_date} → {mp.end_date}</span>
</div>""", unsafe_allow_html=True)

    tab_ann, tab_mon = st.tabs(["年度主限 Annual", "月度主限 Monthly"])

    with tab_ann:
        rows = []
        for ap in chart.annual_profections[:60]:
            cur = "🔮 " if ap.is_current else ""
            rows.append({
                "年齡": ap.age,
                "星座": f"{cur}{ap.sign_glyph} {ap.sign_cn}",
                "守護星": f"{ap.lord_glyph} {ap.lord_cn}",
                "宮位含義": ap.signification_cn[:25],
                "起始": ap.start_date,
                "結束": ap.end_date,
            })
        st.dataframe(rows, width="stretch")

    with tab_mon:
        if chart.monthly_profections:
            rows = []
            for mp in chart.monthly_profections:
                cur = "🔮 " if mp.is_current else ""
                rows.append({
                    "月份": f"Month {mp.month}",
                    "星座": f"{cur}{mp.sign_glyph} {mp.sign_cn}",
                    "守護星": f"{mp.lord_glyph} {mp.lord_cn}",
                    "起始": mp.start_date,
                    "結束": mp.end_date,
                })
            st.dataframe(rows, width="stretch")
        else:
            st.info("月度主限僅在當前年齡週期內計算。")


def _render_triplicity(chart: DeepSassanianChart) -> None:
    """Render Triplicity Lords for each element."""
    cols = st.columns(4)
    elem_colors = {
        "Fire":  "#E74C3C",
        "Earth": "#27AE60",
        "Air":   "#3498DB",
        "Water": "#1ABC9C",
    }
    elem_icons = {"Fire": "🔥", "Earth": "🌍", "Air": "💨", "Water": "💧"}

    for i, tl in enumerate(chart.triplicity_lords):
        with cols[i]:
            col = elem_colors.get(tl.element, "#D4AF37")
            icon = elem_icons.get(tl.element, "✦")
            active_note = "(當前生效)" if tl.active_lord == tl.day_lord and chart.is_day_chart else \
                          "(當前生效)" if tl.active_lord == tl.night_lord and not chart.is_day_chart else ""
            st.markdown(f"""
<div style="background:rgba(13,10,26,0.9);border:1px solid {col}55;
     border-radius:8px;padding:10px 12px;margin-bottom:8px;">
  <div style="color:{col};font-weight:bold;margin-bottom:4px;">
    {icon} {tl.element} ({tl.element_cn})
  </div>
  <div style="font-size:0.82em;color:#c4a46a;">
    <b>日間</b>: {PLANET_GLYPHS.get(tl.day_lord,'')} {tl.day_lord_cn}<br>
    <b>夜間</b>: {PLANET_GLYPHS.get(tl.night_lord,'')} {tl.night_lord_cn}<br>
    <b>參與</b>: {PLANET_GLYPHS.get(tl.part_lord,'')} {tl.part_lord_cn}
  </div>
  <div style="font-size:0.78em;color:{col};margin-top:4px;">{active_note}</div>
</div>""", unsafe_allow_html=True)


def _render_arabic_parts(chart: DeepSassanianChart) -> None:
    """Render extended Arabic Parts / Persian Lots."""
    cols = st.columns(2)
    for i, ap in enumerate(chart.arabic_parts):
        with cols[i % 2]:
            lord_col = PLANET_COLORS.get(ap.lord, "#D4AF37")
            st.markdown(f"""
<div class="per-lot-card">
  <h5>{ap.name_en}</h5>
  <div class="arabic">{ap.name_cn} / {ap.name_arabic}</div>
  <div style="color:#e8d4a8;font-size:0.85em;margin-top:4px;">
    {ap.sign_glyph} {ap.sign_cn} {ap.degree:.1f}° &nbsp;· 第{ap.house}宮
    &nbsp;· 守護 <span style="color:{lord_col}">{ap.lord_glyph} {ap.lord_cn}</span>
  </div>
</div>""", unsafe_allow_html=True)


def _render_royal_stars(chart: DeepSassanianChart) -> None:
    """Render Royal Stars section."""
    prominent = [rs for rs in chart.royal_stars if rs.is_prominent]

    if prominent:
        st.success(f"⭐ 發現 {len(prominent)} 顆顯著皇家恆星合相")
        for rs in prominent:
            conj_col = PLANET_COLORS.get(rs.conjunction_planet or "", "#D4AF37")
            st.markdown(f"""
<div class="per-star-prominent">
  <strong style="color:#D4AF37">⭐ {rs.star_name} ({rs.star_name_cn}) — {rs.star_pahlavi}</strong><br>
  <span style="color:#c4a46a;font-size:0.85em;">
    守護: {rs.guardian} &nbsp;|&nbsp;
    合相行星: <span style="color:{conj_col}">{rs.conjunction_glyph} {rs.conjunction_planet}</span>
    (容許度: {rs.orb:.1f}°)
  </span><br>
  <span style="font-size:0.82em;color:#888;">
    {rs.meaning_cn}<br>
    <em>{rs.meaning_en}</em>
  </span>
</div>""", unsafe_allow_html=True)
    else:
        st.info("目前無行星與皇家恆星形成顯著合相（容許度 2.5°以內）。")

    st.subheader("四顆波斯皇家恆星")
    star_rows = []
    for rs in chart.royal_stars:
        star_rows.append({
            "恆星": f"{rs.star_name} ({rs.star_name_cn})",
            "Pahlavi名": rs.star_pahlavi,
            "守護": rs.guardian,
            "經度": f"{rs.star_longitude:.1f}°",
            "合相行星": rs.conjunction_planet or "—",
            "容許度": f"{rs.orb:.1f}°" if rs.is_prominent else "—",
            "顯著": "⭐" if rs.is_prominent else "",
        })
    st.dataframe(star_rows, width="stretch")


def _render_antiscia(chart: DeepSassanianChart) -> None:
    """Render Antiscia and Contra-antiscia table."""
    rows = []
    for p in chart.planets:
        col = PLANET_COLORS.get(p.name, "#D4AF37")
        rows.append({
            "行星": f"{p.glyph} {p.name_cn}",
            "本體位置": f"{p.sign} {p.degree_in_sign:.1f}°",
            "反射點 (Antiscia)": f"{p.antiscion_sign} {p.antiscion_longitude % 30:.1f}°",
            "對射點 (Contra-antiscia)": f"{p.contra_antiscion_sign} {p.contra_antiscion_longitude % 30:.1f}°",
            "多德卡 (Dodecatemoria)": f"{p.dodecatemoria_sign} ({p.dodecatemoria_sign_cn})",
        })
    st.dataframe(rows, width="stretch")
    st.caption("反射點：以巨蟹/摩羯軸為鏡射軸 | 對射點：以白羊/天秤軸為鏡射軸 | 多德卡：星座內度數 × 12")


def _render_dorotheus(chart: DeepSassanianChart) -> None:
    """Render Dorotheus-style interpretation."""
    d = chart.dorotheus
    if not d:
        return

    is_cn = get_lang() != "en"

    topics = [
        ("⚕️ 壽命 / Longevity",   d.longevity_cn if is_cn else d.longevity_en),
        ("💑 婚姻 / Marriage",     d.marriage_cn  if is_cn else d.marriage_en),
        ("👶 子女 / Children",     d.children_cn  if is_cn else d.children_en),
        ("💼 事業 / Career",       d.career_cn    if is_cn else d.career_en),
        ("🌟 總論 / General",      d.general_cn   if is_cn else d.general_en),
    ]

    st.markdown('<div class="per-dorotheus"><h3>📜 波斯古典解讀 (Carmen Astrologicum 風格)</h3>', unsafe_allow_html=True)
    for topic, text in topics:
        st.markdown(f'<div class="topic">{topic}</div><div class="text">{text}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def _render_egyptian_bounds(chart: DeepSassanianChart) -> None:
    """Show Egyptian bound lord for each planet."""
    rows = []
    for p in chart.planets:
        rows.append({
            "行星": f"{p.glyph} {p.name_cn}",
            "位置": f"{p.sign} {p.degree_in_sign:.1f}°",
            "三分守護星 (三分)": f"{PLANET_GLYPHS.get(p.triplicity_day_lord,'')} {p.triplicity_day_lord} (日) / "
                              f"{PLANET_GLYPHS.get(p.triplicity_night_lord,'')} {p.triplicity_night_lord} (夜)",
            "埃及界 (界)": f"{PLANET_GLYPHS.get(p.egyptian_bound_lord,'')} {PLANET_NAMES_CN.get(p.egyptian_bound_lord,p.egyptian_bound_lord)}",
            "面 (Decan)": f"{PLANET_GLYPHS.get(p.decan_lord,'')} {PLANET_NAMES_CN.get(p.decan_lord,p.decan_lord)}",
        })
    st.dataframe(rows, width="stretch")


# ═══════════════════════════════════════════════════════════════
# Main Renderer Entry Point
# ═══════════════════════════════════════════════════════════════

def render_streamlit(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
) -> None:
    """
    Main Streamlit renderer for advanced Sassanian Persian astrology.
    Called from app.py when tab_persian_deep is selected.
    """
    # Inject CSS
    st.markdown(_CSS, unsafe_allow_html=True)

    # Compute chart
    chart = compute_deep_sassanian_chart(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        latitude=latitude, longitude=longitude,
        timezone=timezone,
    )

    # Header
    _render_header(chart)

    # Diamond chart + current status side by side
    col_chart, col_info = st.columns([1, 1])
    with col_chart:
        svg = _build_diamond_chart_svg(chart)
        st.components.v1.html(
            f'<div style="background:{PERSIAN_COLORS["background"]};border-radius:8px;padding:6px;">{svg}</div>',
            height=496,
            scrolling=False,
        )

    with col_info:
        # Quick summary cards
        if chart.current_firdaria:
            cf = chart.current_firdaria
            st.markdown(f"""
<div class="per-firdar-current">
  <div style="color:#D4AF37;font-size:0.8em;margin-bottom:3px;">當前 Firdaria</div>
  <strong>{cf.major_glyph} {cf.major_lord} ({cf.major_lord_cn})</strong>
  <div style="color:#888;font-size:0.78em;">{cf.start_date} → {cf.end_date}</div>
</div>""", unsafe_allow_html=True)
            if chart.current_sub:
                cs = chart.current_sub
                st.markdown(f"""
<div class="per-firdar-regular">
  <div style="color:#c4a46a;font-size:0.8em;">子週期</div>
  <strong>{cs.sub_glyph} {cs.sub_lord} ({cs.sub_lord_cn})</strong>
  <div style="color:#888;font-size:0.78em;">{cs.start_date} → {cs.end_date}</div>
</div>""", unsafe_allow_html=True)

        if chart.almuten:
            alm = chart.almuten
            st.markdown(f"""
<div style="background:rgba(230,126,34,0.1);border:1px solid #E67E2260;
     border-radius:8px;padding:10px 14px;margin-bottom:8px;">
  <div style="color:#E67E22;font-size:0.8em;">Almuten 命主星</div>
  <strong style="color:#E67E22;font-size:1.1em;">{alm.planet_glyph} {alm.planet} ({alm.planet_cn})</strong>
  <div style="color:#888;font-size:0.78em;">尊嚴分 {alm.total_score:.1f}</div>
</div>""", unsafe_allow_html=True)

        if chart.current_annual_prof:
            ap = chart.current_annual_prof
            st.markdown(f"""
<div style="background:rgba(26,188,156,0.1);border:1px solid #1ABC9C60;
     border-radius:8px;padding:10px 14px;margin-bottom:8px;">
  <div style="color:#1ABC9C;font-size:0.8em;">年度主限 Age {ap.age}</div>
  <strong style="color:#1ABC9C;">{ap.sign_glyph} {ap.sign_cn} · {ap.lord_glyph} {ap.lord_cn}</strong>
</div>""", unsafe_allow_html=True)

    st.markdown('<hr class="per-divider">', unsafe_allow_html=True)

    # Main content tabs
    (tab_planets, tab_firdar, tab_hyleg, tab_almuten,
     tab_profections, tab_bounds, tab_antiscia,
     tab_lots, tab_stars, tab_dorotheus) = st.tabs([
        "🪐 行星",
        "📅 Firdaria",
        "🌟 Hyleg",
        "👑 Almuten",
        "🔄 主限",
        "📊 界與三分",
        "🔁 反射點",
        "📍 波斯敏感點",
        "⭐ 皇家恆星",
        "📜 Dorotheus 解讀",
    ])

    with tab_planets:
        st.header("行星位置 Planet Positions")
        st.caption("使用整宮制 (Whole Sign Houses)，熱帶黃道 (Tropical Zodiac)")
        _render_planet_table(chart)

    with tab_firdar:
        st.header("Firdar 生命週期 Time Lords")
        st.caption(
            "日間盤：太陽(10y)→金星(8y)→水星(13y)→月亮(9y)→土星(11y)→木星(12y)→火星(7y)→北交(3y)→南交(2y)" if chart.is_day_chart
            else "夜間盤：月亮(9y)→土星(11y)→木星(12y)→火星(7y)→太陽(10y)→金星(8y)→水星(13y)→南交(2y)→北交(3y)"
        )
        _render_firdaria(chart)

    with tab_hyleg:
        st.header("Hyleg & Alcocoden — 壽命計算")
        st.caption("Hyleg 為生命給予者，Alcocoden 為壽命給予者，二者共同指示壽命範圍。")
        _render_hyleg_alcocoden(chart)

    with tab_almuten:
        st.header("Almuten Figuris — 命主星 Chart Ruler")
        st.caption("Almuten 是在五個關鍵點（上升、天頂、太陽、月亮、幸運點）積累最高尊嚴分數的行星。")
        _render_almuten(chart)

    with tab_profections:
        st.header("主限法 Profections")
        st.caption("年度主限：每年上升點前進一個星座 | 月度主限：在當前年份的月度細分")
        _render_profections(chart)

    with tab_bounds:
        st.header("三分守護星 & 埃及界 Triplicity Lords & Egyptian Bounds")
        st.subheader("三分守護星 (Triplicity Lords)")
        st.caption("Dorotheus of Sidon《Carmen Astrologicum》傳統")
        _render_triplicity(chart)
        st.divider()
        st.subheader("行星的三分 / 界 / 面")
        _render_egyptian_bounds(chart)

    with tab_antiscia:
        st.header("反射點 Antiscia & 多德卡特摩里亞 Dodecatemoria")
        st.caption(
            "**反射點 Antiscia**: 以夏至/冬至軸（巨蟹/摩羯0°）為鏡射軸的等光週期點\n\n"
            "**對射點 Contra-antiscia**: 以春/秋分軸（白羊/天秤0°）為鏡射軸\n\n"
            "**多德卡特摩里亞**: 每個度數放大12倍，等同在星座小輪盤中的位置"
        )
        _render_antiscia(chart)

    with tab_lots:
        st.header("波斯阿拉伯點 Persian Lots / Arabic Parts")
        st.caption("依據 Masha'allah、Umar al-Tabari 等波斯傳統天文學家的計算方法")
        _render_arabic_parts(chart)

    with tab_stars:
        st.header("四顆波斯皇家恆星 Royal Stars of Persia")
        st.caption("波斯 Pahlavi 傳統的天空四維守護者：Tascheter、Vanant、Satevis、Hastorang")
        _render_royal_stars(chart)

    with tab_dorotheus:
        st.header("波斯古典解讀 Persian Classical Interpretation")
        st.caption("基於多羅修斯《卡門天文學》(Carmen Astrologicum) 和薩珊波斯 Pahlavi 傳統")
        _render_dorotheus(chart)

    # Register chart with AI analysis
    try:
        from astro.i18n import t as _t
        st.session_state["_global_chat_system"] = "tab_persian_deep"
        st.session_state["_global_chat_chart"] = chart.to_dict()
    except Exception:
        pass
