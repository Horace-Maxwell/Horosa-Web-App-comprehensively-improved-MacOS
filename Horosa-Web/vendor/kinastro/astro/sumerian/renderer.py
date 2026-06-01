"""
astro/sumerian/renderer.py — Streamlit UI for Sumerian / Mesopotamian Astrology

Renders a multi-tab interface:
  Tab 1: 泥板星圖 K.8538 Planisphere — 8-sector SVG visualization
  Tab 2: 行星列表 Planet Table — deity, sign, path, condition
  Tab 3: 三路星座 Three Paths — Enlil / Anu / Ea classification
  Tab 4: 預兆解讀 Omen Readings — Enūma Anu Enlil style
  Tab 5: MUL.APIN 星表 — heliacal rising stars for birth month

Sources:
- Hunger & Pingree, "MUL.APIN" (1989)
- Koch-Westenholz, "Mesopotamian Astrology" (1995)
- Rochberg, "The Heavenly Writing" (2004)
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

import streamlit as st

from .calculator import MesopotamianChart, MesopotamianPlanet, compute_sumerian_chart
from .constants import (
    MESOPOTAMIAN_DEITIES,
    MULAPIN_PATHS,
    MULAPIN_36_STARS,
    K8538_SECTORS,
    SUMER_GOLD,
    SUMER_GOLD_LIGHT,
    SUMER_LAPIS,
    SUMER_LAPIS_LIGHT,
    SUMER_TERRACOTTA,
    SUMER_TERRACOTTA_LIGHT,
    SUMER_SANDSTONE,
    SUMER_SANDSTONE_DARK,
    SUMER_CLAY,
    SUMER_BG,
    SUMER_BG2,
    SUMER_BORDER,
    ZODIAC_SIGN_ORDER,
    AKKADIAN_NAME,
    SIGN_CN,
    SIGN_EN,
)
from astro.i18n import auto_cn, get_lang, t

# ============================================================
# CSS
# ============================================================

_CSS = f"""
<style>
/* ── Sumerian / Mesopotamian Module Styles ── */
.sumer-hero {{
    background: linear-gradient(135deg,
        #0D0A02 0%, #1A1200 45%, #0D0A02 100%);
    border: 1px solid {SUMER_BORDER};
    border-radius: 14px;
    padding: 1.6rem 2rem 1.2rem;
    margin-bottom: 1.4rem;
    position: relative;
    overflow: hidden;
}}
.sumer-hero::before {{
    content: "𒀭𒌓 𒀭𒂗 𒀭𒊩𒌆 𒀭𒈾 𒀭𒀭";
    position: absolute; top: 10px; right: 16px;
    color: rgba(201,162,39,0.18); font-size: 0.9rem; letter-spacing: 6px;
}}
.sumer-hero-title {{
    font-size: 1.55rem; font-weight: 700; color: {SUMER_GOLD};
    font-family: 'Georgia', serif; margin: 0 0 0.25rem 0;
}}
.sumer-hero-sub {{
    color: {SUMER_SANDSTONE}; font-size: 0.88rem; margin: 0;
}}
.sumer-card {{
    border: 1px solid {SUMER_BORDER};
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
    background: rgba(201,162,39,0.05);
}}
.sumer-card h4 {{ color: {SUMER_GOLD}; margin: 0 0 6px 0; }}
.sumer-omen-auspicious {{
    background: rgba(21,101,192,0.15);
    border-left: 3px solid {SUMER_LAPIS_LIGHT};
    border-radius: 5px; padding: 10px 14px; margin-bottom: 8px;
}}
.sumer-omen-inauspicious {{
    background: rgba(160,82,45,0.18);
    border-left: 3px solid {SUMER_TERRACOTTA};
    border-radius: 5px; padding: 10px 14px; margin-bottom: 8px;
}}
.sumer-omen-neutral {{
    background: rgba(201,162,39,0.09);
    border-left: 3px solid {SUMER_GOLD};
    border-radius: 5px; padding: 10px 14px; margin-bottom: 8px;
}}
.sumer-section-title {{
    color: {SUMER_GOLD}; font-size: 1.05rem;
    font-weight: 600; border-bottom: 1px solid {SUMER_BORDER};
    padding-bottom: 4px; margin: 1rem 0 0.6rem 0;
}}
.sumer-path-enlil {{
    background: rgba(42,82,152,0.15);
    border: 1px solid rgba(42,82,152,0.4);
    border-radius: 6px; padding: 8px 12px; margin-bottom: 6px;
}}
.sumer-path-anu {{
    background: rgba(201,162,39,0.10);
    border: 1px solid rgba(201,162,39,0.35);
    border-radius: 6px; padding: 8px 12px; margin-bottom: 6px;
}}
.sumer-path-ea {{
    background: rgba(160,82,45,0.12);
    border: 1px solid rgba(160,82,45,0.35);
    border-radius: 6px; padding: 8px 12px; margin-bottom: 6px;
}}
</style>
"""

# ============================================================
# SVG helpers — K.8538 Planisphere
# ============================================================

def _build_planisphere_svg(chart: MesopotamianChart, size: int = 540) -> str:
    """Build an SVG of the K.8538 planisphere (8-sector circular chart).

    The disk shows 8 equal sectors (45° each), Akkadian cuneiform labels,
    and planetary glyphs plotted by sidereal longitude.
    """
    cx = cy = size // 2
    r_outer = size // 2 - 20
    r_inner = r_outer * 0.22
    r_zodiac_band_outer = r_outer * 0.92
    r_zodiac_band_inner = r_outer * 0.65
    r_planet = r_outer * 0.45

    svg_parts: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}" style="background:#0D0A02;border-radius:50%;">'
    ]

    # Background gradient
    svg_parts.append(
        f'<defs>'
        f'<radialGradient id="bgGrad" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="#1A1200"/>'
        f'<stop offset="100%" stop-color="#0A0800"/>'
        f'</radialGradient>'
        f'<filter id="glow"><feGaussianBlur stdDeviation="2" result="coloredBlur"/>'
        f'<feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        f'</filter>'
        f'</defs>'
    )
    svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="url(#bgGrad)" '
                     f'stroke="{SUMER_GOLD}" stroke-width="2"/>')

    # 8 sector wedges
    for sec in chart.sectors:
        idx = sec["index"]
        start_angle = idx * 45 - 90      # start from top (north)
        end_angle = start_angle + 45

        sa_r = math.radians(start_angle)
        ea_r = math.radians(end_angle)
        # Sector wedge path
        x1 = cx + r_inner * math.cos(sa_r)
        y1 = cy + r_inner * math.sin(sa_r)
        x2 = cx + r_zodiac_band_outer * math.cos(sa_r)
        y2 = cy + r_zodiac_band_outer * math.sin(sa_r)
        x3 = cx + r_zodiac_band_outer * math.cos(ea_r)
        y3 = cy + r_zodiac_band_outer * math.sin(ea_r)
        x4 = cx + r_inner * math.cos(ea_r)
        y4 = cy + r_inner * math.sin(ea_r)
        color = sec["color"]

        path = (
            f"M {x1:.1f} {y1:.1f} "
            f"L {x2:.1f} {y2:.1f} "
            f"A {r_zodiac_band_outer:.1f} {r_zodiac_band_outer:.1f} 0 0 1 {x3:.1f} {y3:.1f} "
            f"L {x4:.1f} {y4:.1f} "
            f"A {r_inner:.1f} {r_inner:.1f} 0 0 0 {x1:.1f} {y1:.1f} Z"
        )
        svg_parts.append(
            f'<path d="{path}" fill="{color}" fill-opacity="0.28" '
            f'stroke="{SUMER_GOLD}" stroke-width="0.8" stroke-opacity="0.6"/>'
        )

        # Sector direction label
        mid_angle_r = math.radians(start_angle + 22.5)
        lx = cx + r_zodiac_band_inner * math.cos(mid_angle_r)
        ly = cy + r_zodiac_band_inner * math.sin(mid_angle_r)
        dir_label = sec["direction_cn"] if get_lang() in ("zh", "zh_cn") else sec["direction"]
        svg_parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="{SUMER_SANDSTONE}" font-size="10" '
            f'font-family="sans-serif" opacity="0.85">{dir_label}</text>'
        )

        # Akkadian cuneiform glyph at outer edge
        gx = cx + (r_zodiac_band_outer - 12) * math.cos(mid_angle_r)
        gy = cy + (r_zodiac_band_outer - 12) * math.sin(mid_angle_r)
        svg_parts.append(
            f'<text x="{gx:.1f}" y="{gy:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="{SUMER_GOLD}" font-size="12" '
            f'opacity="0.7">{sec["akkadian_label"]}</text>'
        )

    # Zodiac sign arcs (12 equal 30° divisions)
    r_sign_mid = (r_zodiac_band_inner * 0.72 + r_zodiac_band_outer * 0.28)
    for i in range(12):
        angle_start = i * 30 - 90
        angle_mid = angle_start + 15
        mid_r = math.radians(angle_mid)

        # Tick lines
        t_r1 = math.radians(angle_start)
        tx1 = cx + r_zodiac_band_inner * math.cos(t_r1)
        ty1 = cy + r_zodiac_band_inner * math.sin(t_r1)
        tx2 = cx + r_zodiac_band_outer * math.cos(t_r1)
        ty2 = cy + r_zodiac_band_outer * math.sin(t_r1)
        svg_parts.append(
            f'<line x1="{tx1:.1f}" y1="{ty1:.1f}" x2="{tx2:.1f}" y2="{ty2:.1f}" '
            f'stroke="{SUMER_GOLD}" stroke-width="0.5" stroke-opacity="0.5"/>'
        )

        # Sign label
        sx = cx + r_sign_mid * math.cos(mid_r)
        sy = cy + r_sign_mid * math.sin(mid_r)
        sign_name = ZODIAC_SIGN_ORDER[i]
        label = AKKADIAN_NAME[sign_name][:6]   # truncate long names
        svg_parts.append(
            f'<text x="{sx:.1f}" y="{sy:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="{SUMER_GOLD_LIGHT}" font-size="7" '
            f'font-family="sans-serif" opacity="0.9">{label}</text>'
        )

    # Planet positions
    for p in chart.planets:
        angle_r = math.radians(p.longitude - 90)  # 0° Aries at top
        px_ = cx + r_planet * math.cos(angle_r)
        py_ = cy + r_planet * math.sin(angle_r)
        svg_parts.append(
            f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="9" '
            f'fill="{p.color}" fill-opacity="0.85" '
            f'stroke="#ffffff" stroke-width="1" filter="url(#glow)"/>'
        )
        svg_parts.append(
            f'<text x="{px_:.1f}" y="{py_:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="#ffffff" font-size="10" '
            f'font-weight="bold">{p.glyph}</text>'
        )

    # Centre disc with cuneiform
    svg_parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" '
        f'fill="#1A1200" stroke="{SUMER_GOLD}" stroke-width="1.5"/>'
    )
    svg_parts.append(
        f'<text x="{cx}" y="{cy-6}" text-anchor="middle" '
        f'fill="{SUMER_GOLD}" font-size="14" opacity="0.9">𒀭</text>'
    )
    svg_parts.append(
        f'<text x="{cx}" y="{cy+10}" text-anchor="middle" '
        f'fill="{SUMER_SANDSTONE}" font-size="8" opacity="0.7">MUL.APIN</text>'
    )

    # Outer ring caption
    svg_parts.append(
        f'<text x="{cx}" y="{size - 8}" text-anchor="middle" '
        f'fill="{SUMER_SANDSTONE_DARK}" font-size="9" opacity="0.6">'
        f'K.8538 Planisphere · Sidereal · MUL.APIN</text>'
    )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


# ============================================================
# Condition display helpers
# ============================================================

_CONDITION_ICON = {
    "domicile":  "🏛️",
    "exalt":     "⬆️",
    "detriment": "⚠️",
    "fall":      "⬇️",
    "neutral":   "·",
}

_CONDITION_CN = {
    "domicile":  "廟旺",
    "exalt":     "升揚",
    "detriment": "弱陷",
    "fall":      "落陷",
    "neutral":   "平常",
}

_CONDITION_EN = {
    "domicile":  "Domicile",
    "exalt":     "Exaltation",
    "detriment": "Detriment",
    "fall":      "Fall",
    "neutral":   "Neutral",
}


def _condition_label(cond: str) -> str:
    icon = _CONDITION_ICON.get(cond, "·")
    label_cn = _CONDITION_CN.get(cond, cond)
    label_en = _CONDITION_EN.get(cond, cond)
    return f"{icon} {auto_cn(label_cn, label_en)}"


# ============================================================
# Main render function
# ============================================================

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
    """Render the complete Sumerian / Mesopotamian Astrology UI in Streamlit."""
    st.markdown(_CSS, unsafe_allow_html=True)

    # Hero banner
    st.markdown(
        f'<div class="sumer-hero">'
        f'<div class="sumer-hero-title">'
        f'𒀭𒌓 {auto_cn("蘇美 / 美索不達米亞占星", "Sumerian / Mesopotamian Astrology")}'
        f'</div>'
        f'<div class="sumer-hero-sub">'
        f'{auto_cn("MUL.APIN 星表 · Enūma Anu Enlil 預兆集 · K.8538 尼尼微星盤", "MUL.APIN Star Catalogue · Enūma Anu Enlil Omen Series · K.8538 Nineveh Planisphere")}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Compute chart
    with st.spinner(t("spinner_sumerian")):
        chart = compute_sumerian_chart(
            year=year, month=month, day=day,
            hour=hour, minute=minute,
            timezone=timezone,
            lat=latitude, lon=longitude,
            location_name=location_name,
        )

    # Tabs
    tab_labels = [
        auto_cn("泥板星圖", "Planisphere"),
        auto_cn("行星神靈", "Planet Deities"),
        auto_cn("三路分佈", "Three Paths"),
        auto_cn("預兆解讀", "Omen Readings"),
        auto_cn("MUL.APIN 星表", "MUL.APIN Stars"),
    ]
    tabs = st.tabs(tab_labels)

    # ── Tab 1: K.8538 Planisphere ─────────────────────────────
    with tabs[0]:
        _render_planisphere_tab(chart)

    # ── Tab 2: Planet Deities ─────────────────────────────────
    with tabs[1]:
        _render_planets_tab(chart)

    # ── Tab 3: Three Paths ────────────────────────────────────
    with tabs[2]:
        _render_paths_tab(chart)

    # ── Tab 4: Omen Readings ──────────────────────────────────
    with tabs[3]:
        _render_omens_tab(chart)

    # ── Tab 5: MUL.APIN Star Catalogue ───────────────────────
    with tabs[4]:
        _render_mulapin_tab(chart)


# ============================================================
# Tab renderers
# ============================================================

def _render_planisphere_tab(chart: MesopotamianChart) -> None:
    """Tab 1 — K.8538 Planisphere SVG + sector table."""
    st.markdown(
        f'<p class="sumer-section-title">'
        f'{auto_cn("K.8538 尼尼微泥板星盤", "K.8538 Nineveh Planisphere")}'
        f'</p>',
        unsafe_allow_html=True,
    )

    col_svg, col_info = st.columns([1, 1])
    with col_svg:
        svg = _build_planisphere_svg(chart, size=480)
        st.markdown(svg, unsafe_allow_html=True)
        st.caption(
            auto_cn(
                "K.8538 尼尼微泥板（約公元前 650 年）· 8 區間圓形星盤 · 側恆黃道 · MUL.APIN 宮名",
                "K.8538 Nineveh Planisphere (~650 BCE) · 8-sector disc · Sidereal zodiac · MUL.APIN sign names",
            )
        )

    with col_info:
        st.markdown(
            f'<p class="sumer-section-title">'
            f'{auto_cn("區間行星分佈", "Sector Planet Distribution")}'
            f'</p>',
            unsafe_allow_html=True,
        )
        for sec in chart.sectors:
            planets_str = "  ".join(sec["planets_present"]) if sec["planets_present"] else "—"
            dir_label = sec["direction_cn"] if get_lang() in ("zh", "zh_cn") else sec["direction"]
            constellations = "、".join(sec["constellations"]) if get_lang() in ("zh", "zh_cn") else ", ".join(sec["constellations"])
            st.markdown(
                f'<div class="sumer-card">'
                f'<h4>{sec["akkadian_label"]} {dir_label} ({sec["season_cn"] if get_lang() in ("zh","zh_cn") else sec["season_en"]})</h4>'
                f'<small style="color:{SUMER_SANDSTONE};">{constellations}</small><br>'
                f'<span style="color:{SUMER_GOLD_LIGHT}; font-size:1.1em;">{planets_str}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Venus phase note
    venus_phase_cn = {"morning_star": "🌅 Ištar 晨星（dINANNA）升起", "evening_star": "🌇 Ištar 夕星（dINANNA）現身"}.get(
        chart.venus_phase, "")
    venus_phase_en = {"morning_star": "🌅 Ištar as Morning Star rises", "evening_star": "🌇 Ištar appears as Evening Star"}.get(
        chart.venus_phase, "")
    if venus_phase_cn:
        st.info(auto_cn(venus_phase_cn, venus_phase_en))


def _render_planets_tab(chart: MesopotamianChart) -> None:
    """Tab 2 — Planet deity table with Akkadian names & conditions."""
    st.markdown(
        f'<p class="sumer-section-title">'
        f'{auto_cn("七大行星神 — Enūma Anu Enlil 標準", "Seven Planetary Deities — Enūma Anu Enlil Standard")}'
        f'</p>',
        unsafe_allow_html=True,
    )

    for p in chart.planets:
        cond_label = _condition_label(p.condition)
        retro = auto_cn(" ℞ 逆行", " ℞ Rx") if p.is_retrograde else ""
        path_info = MULAPIN_PATHS.get(p.path, {})
        path_cn = path_info.get("cn", p.path)
        path_en = path_info.get("en", p.path)
        path_label = auto_cn(path_cn, path_en)

        st.markdown(
            f'<div class="sumer-card">'
            f'<h4>{p.glyph} {p.akkadian} <span style="color:{SUMER_SANDSTONE};font-weight:normal;font-size:0.85em;">({p.sumerian})</span> — '
            f'{auto_cn(p.role_cn, p.role_en)}</h4>'
            f'<div style="display:flex;gap:1.5rem;flex-wrap:wrap;">'
            f'<span><b style="color:{SUMER_SANDSTONE};">{auto_cn("宮位","Sign")}:</b> '
            f'{p.sign_akkadian} ({auto_cn(p.sign_cn, p.sign_en)}) {p.degree_in_sign:.1f}°</span>'
            f'<span><b style="color:{SUMER_SANDSTONE};">{auto_cn("宮室","House")}:</b> {p.house}</span>'
            f'<span><b style="color:{SUMER_SANDSTONE};">{auto_cn("狀態","Condition")}:</b> {cond_label}{retro}</span>'
            f'<span><b style="color:{SUMER_SANDSTONE};">{auto_cn("天路","Path")}:</b> '
            f'<span style="color:{path_info.get("color","#C9A227")}">{path_label}</span></span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Aspects
    if chart.aspects:
        st.markdown(
            f'<p class="sumer-section-title" style="margin-top:1.2rem;">'
            f'{auto_cn("行星相位", "Planetary Aspects")}</p>',
            unsafe_allow_html=True,
        )
        _asp_rows = []
        for asp in chart.aspects:
            d1 = MESOPOTAMIAN_DEITIES.get(asp["planet1"], {})
            d2 = MESOPOTAMIAN_DEITIES.get(asp["planet2"], {})
            _asp_rows.append({
                auto_cn("行星1", "Planet 1"): f'{d1.get("glyph","")} {d1.get("akkadian", asp["planet1"])}',
                auto_cn("行星2", "Planet 2"): f'{d2.get("glyph","")} {d2.get("akkadian", asp["planet2"])}',
                auto_cn("相位", "Aspect"): asp["aspect"],
                auto_cn("角度", "Angle"): f'{asp["angle"]}°',
                auto_cn("容差", "Orb"): f'{asp["orb"]}°',
            })
        if _asp_rows:
            import pandas as pd
            st.dataframe(pd.DataFrame(_asp_rows), width="stretch")


def _render_paths_tab(chart: MesopotamianChart) -> None:
    """Tab 3 — MUL.APIN three sky paths (Enlil / Anu / Ea)."""
    st.markdown(
        f'<p class="sumer-section-title">'
        f'{auto_cn("MUL.APIN 天路三分", "MUL.APIN Three Sky Paths")}'
        f'</p>',
        unsafe_allow_html=True,
    )

    # Explanatory note
    st.info(
        auto_cn(
            "MUL.APIN 泥板記載天球分三路：恩利爾之路（北帶赤緯 >+17°）、安努之路（赤道帶 ±17°）、"
            "埃阿之路（南帶赤緯 <-17°）。行星所在天路影響其預兆含義與吉凶判斷。",
            "MUL.APIN divides the sky into three paths: Path of Enlil (northern band, dec >+17°), "
            "Path of Anu (equatorial band, dec ±17°), Path of Ea (southern band, dec <-17°). "
            "A planet's path influences its omen meaning and auspiciousness.",
        )
    )

    path_planets: Dict[str, List[MesopotamianPlanet]] = {"Enlil": [], "Anu": [], "Ea": []}
    for p in chart.planets:
        if p.path in path_planets:
            path_planets[p.path].append(p)

    for path_key, path_data in MULAPIN_PATHS.items():
        planets_in = path_planets.get(path_key, [])
        css_class = f"sumer-path-{path_key.lower()}"
        planet_strs = "  ".join(
            f'{p.glyph} {p.akkadian} ({p.sign_akkadian})' for p in planets_in
        ) if planets_in else auto_cn("（此路無行星）", "(no planets in this path)")

        st.markdown(
            f'<div class="{css_class}">'
            f'<b style="color:{path_data["color"]};">{auto_cn(path_data["cn"], path_data["en"])}</b>'
            f'<span style="color:{SUMER_SANDSTONE};font-size:0.82em;"> — '
            f'{auto_cn(path_data["desc_cn"], path_data["desc_en"])}</span><br>'
            f'<span style="font-size:1.05em;">{planet_strs}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Declination table
    st.markdown(
        f'<p class="sumer-section-title" style="margin-top:1rem;">'
        f'{auto_cn("行星赤緯詳表", "Planet Declination Details")}</p>',
        unsafe_allow_html=True,
    )
    import pandas as pd
    rows = []
    for p in chart.planets:
        path_data = MULAPIN_PATHS.get(p.path, {})
        rows.append({
            auto_cn("行星神", "Deity"): f'{p.glyph} {p.akkadian}',
            auto_cn("赤緯", "Declination"): f'{p.declination:+.2f}°',
            auto_cn("天路", "Path"): auto_cn(path_data.get("cn", p.path), path_data.get("en", p.path)),
        })
    st.dataframe(pd.DataFrame(rows), width="stretch")


def _render_omens_tab(chart: MesopotamianChart) -> None:
    """Tab 4 — Enūma Anu Enlil omen readings."""
    st.markdown(
        f'<p class="sumer-section-title">'
        f'{auto_cn("Enūma Anu Enlil 預兆解讀", "Enūma Anu Enlil Omen Readings")}'
        f'</p>',
        unsafe_allow_html=True,
    )
    st.info(
        auto_cn(
            "以下預兆依據《Enūma Anu Enlil》泥板集傳統（約公元前 2000–500 年）推衍，"
            "結合行星在黃道宮的強弱狀態（廟旺/升揚/弱陷/落陷）與特殊天象（晨星/夕星/逆行）。",
            "The following omens are derived from the Enūma Anu Enlil tablet series (~2000–500 BCE), "
            "based on each planet's dignitary condition (domicile/exaltation/detriment/fall) "
            "and special phenomena (morning star, evening star, retrograde).",
        )
    )

    if not chart.omens:
        st.write(auto_cn("目前無顯著預兆記錄。", "No significant omens recorded at this time."))
        return

    # Group by planet
    planet_order = ["Sun", "Moon", "Venus", "Mercury", "Mars", "Jupiter", "Saturn"]
    omens_by_planet: Dict[str, list] = {k: [] for k in planet_order}
    for omen in chart.omens:
        if omen.planet in omens_by_planet:
            omens_by_planet[omen.planet].append(omen)

    for planet_name in planet_order:
        omens = omens_by_planet[planet_name]
        if not omens:
            continue
        deity = MESOPOTAMIAN_DEITIES.get(planet_name, {})
        glyph = deity.get("glyph", "★")
        akkadian = deity.get("akkadian", planet_name)
        sumerian = deity.get("sumerian", "")
        role = auto_cn(deity.get("role_cn", ""), deity.get("role_en", ""))

        st.markdown(
            f'**{glyph} {akkadian}** <span style="color:{SUMER_SANDSTONE};font-size:0.88em;">({sumerian}) — {role}</span>',
            unsafe_allow_html=True,
        )
        for omen in omens:
            css_class = {
                "auspicious": "sumer-omen-auspicious",
                "inauspicious": "sumer-omen-inauspicious",
            }.get(omen.severity, "sumer-omen-neutral")
            icon = {"auspicious": "🌟", "inauspicious": "⚠️", "neutral": "📜"}.get(omen.severity, "📜")
            text = auto_cn(omen.text_cn, omen.text_en)
            sign_note = f" ({auto_cn(SIGN_CN.get(omen.sign,''), SIGN_EN.get(omen.sign,''))})" if omen.sign else ""
            cond_label = auto_cn(
                _CONDITION_CN.get(omen.condition, omen.condition),
                _CONDITION_EN.get(omen.condition, omen.condition),
            )
            st.markdown(
                f'<div class="{css_class}">'
                f'{icon} <b>[{cond_label}{sign_note}]</b> {text}'
                f'</div>',
                unsafe_allow_html=True,
            )


def _render_mulapin_tab(chart: MesopotamianChart) -> None:
    """Tab 5 — MUL.APIN 36 heliacal rising stars for the birth month."""
    st.markdown(
        f'<p class="sumer-section-title">'
        f'{auto_cn("MUL.APIN 出生月份昏旦星表", "MUL.APIN Heliacal Rising Stars for Birth Month")}'
        f'</p>',
        unsafe_allow_html=True,
    )

    month_names_cn = ["一月 Nisannu", "二月 Ayyaru", "三月 Simanu",
                      "四月 Du'uzu", "五月 Abu", "六月 Ululu",
                      "七月 Tashritu", "八月 Arahsamnu", "九月 Kislimu",
                      "十月 Tebetu", "十一月 Shabatu", "十二月 Addaru"]
    month_names_en = ["Month I Nisannu", "Month II Ayyaru", "Month III Simanu",
                      "Month IV Du'uzu", "Month V Abu", "Month VI Ululu",
                      "Month VII Tashritu", "Month VIII Arahsamnu", "Month IX Kislimu",
                      "Month X Tebetu", "Month XI Shabatu", "Month XII Addaru"]

    st.info(
        auto_cn(
            "MUL.APIN 泥板記載每月昏旦初現的 36 顆星座（每月三顆），是美索不達米亞曆法與農業的核心。"
            "以下為你出生月份可觀測的昏旦星。",
            "MUL.APIN lists 36 heliacal rising stars — three per month — as the core of the Mesopotamian "
            "calendar and agricultural cycle. Below are the stars visible in your birth month.",
        )
    )

    if chart.heliacal_stars:
        bab_month_idx = (chart.month - 4) % 12
        month_label = month_names_cn[bab_month_idx] if get_lang() in ("zh", "zh_cn") else month_names_en[bab_month_idx]
        st.markdown(f"**{auto_cn('出生月份', 'Birth Month')}:** {month_label}")

        for star in chart.heliacal_stars:
            path_data = MULAPIN_PATHS.get(star["path"], {})
            path_label = auto_cn(path_data.get("cn", star["path"]), path_data.get("en", star["path"]))
            star_name = auto_cn(star["cn"], star["en"])
            st.markdown(
                f'<div class="sumer-card">'
                f'<b style="color:{SUMER_GOLD};">{star["akkadian"]}</b> — {star_name}'
                f'<span style="float:right;color:{path_data.get("color", SUMER_SANDSTONE)};font-size:0.85em;">{path_label}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.write(auto_cn("此月份無昏旦星記錄。", "No heliacal rising stars recorded for this month."))

    # Full 36-star table
    with st.expander(auto_cn("📋 完整 36 顆星表", "📋 Full 36-Star MUL.APIN List"), expanded=False):
        import pandas as pd
        from .constants import MULAPIN_36_STARS as _ALL_STARS
        rows = []
        month_labels = month_names_cn if get_lang() in ("zh", "zh_cn") else month_names_en
        for star in sorted(_ALL_STARS, key=lambda s: s["month"]):
            path_data = MULAPIN_PATHS.get(star["path"], {})
            rows.append({
                auto_cn("巴比倫月份", "Bab. Month"): month_labels[star["month"]],
                auto_cn("阿卡德名", "Akkadian Name"): star["akkadian"],
                auto_cn("名稱", "Name"): auto_cn(star["cn"], star["en"]),
                auto_cn("天路", "Path"): auto_cn(path_data.get("cn", star["path"]), path_data.get("en", star["path"])),
            })
        st.dataframe(pd.DataFrame(rows), width="stretch")
