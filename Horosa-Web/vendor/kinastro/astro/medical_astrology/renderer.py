"""
astro/medical_astrology/renderer.py — Streamlit UI for Medical Astrology

Renders a multi-tab interface for classical Iatromathematics:
  Tab 1: 本命體質分析  — Natal Temperament & Zodiac Man
  Tab 2: 健康易損區域  — Body Zone Health Report
  Tab 3: 療癒擇時      — Medical Electional Timing
  Tab 4: 危機期分析    — Critical Day Analysis
  Tab 5: 旬星身體對照  — Egyptian Decan Body Mapping

Sources:
- Medieval "Zodiac Man" manuscripts (Très Riches Heures du Duc de Berry, MS. 65)
- Culpeper "Astrological Judgement of Diseases" (1655)
- Lilly "Christian Astrology" (1647) pp. 252–260
"""

from __future__ import annotations

import math
from datetime import datetime, date
from typing import Dict, List, Optional

import streamlit as st
import swisseph as swe

from .calculator import (
    MedicalChart,
    ElectionalWindow,
    CriticalDayInfo,
    PlanetPosition,
    compute_medical_chart,
    compute_electional_windows,
    _sign_from_lon,
    _moon_phase_angle,
    _moon_phase_name,
    _get_planetary_hour,
    _julian_day,
)
from .constants import (
    ZODIAC_BODY_PARTS,
    ZODIAC_SIGN_ORDER,
    FOUR_HUMORS,
    PLANET_MEDICAL,
    DECAN_BODY_PARTS,
    CRITICAL_DAYS,
    ELECTIONAL_RULES,
    TEMPERAMENT_DESCRIPTIONS,
    MOON_PHASE_MEDICAL,
)
from astro.i18n import auto_cn, get_lang, t

# ============================================================
# CSS
# ============================================================

_CSS = """
<style>
.med-header {
    background: linear-gradient(135deg, #1a0a00 0%, #3d1a00 50%, #5c2800 100%);
    border-left: 5px solid #C5A03F;
    padding: 14px 20px;
    border-radius: 8px;
    margin-bottom: 16px;
}
.med-header h2 { color: #C5A03F; margin: 0; font-size: 1.4em; }
.med-header p  { color: #d4b896; margin: 4px 0 0 0; font-size: 0.9em; }
.humor-card {
    border: 1px solid #C5A03F44;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    background: rgba(197,160,63,0.06);
}
.humor-card h4 { color: #C5A03F; margin: 0 0 6px 0; }
.body-zone-high   { background: rgba(220,53,69,0.18);  border-left: 3px solid #dc3545; border-radius:4px; padding: 8px 12px; margin-bottom:6px; }
.body-zone-mod    { background: rgba(255,193,7,0.18);  border-left: 3px solid #ffc107; border-radius:4px; padding: 8px 12px; margin-bottom:6px; }
.body-zone-low    { background: rgba(40,167,69,0.18);  border-left: 3px solid #28a745; border-radius:4px; padding: 8px 12px; margin-bottom:6px; }
.elect-card {
    background: rgba(197,160,63,0.08);
    border: 1px solid #C5A03F66;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.elect-card .score { font-size: 1.3em; font-weight: bold; color: #C5A03F; }
.crisis-critical { background: rgba(220,53,69,0.15); border-left: 3px solid #dc3545; border-radius:4px; padding:8px 12px; margin-bottom:6px; }
.crisis-indicator { background: rgba(255,193,7,0.15); border-left: 3px solid #ffc107; border-radius:4px; padding:8px 12px; margin-bottom:6px; }
.decan-body-card {
    background: rgba(26, 42, 74, 0.7);
    border: 1px solid #40E0D044;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
}
.decan-body-card h5 { color: #40E0D0; margin: 0 0 4px 0; }
.ref-note { color: #888; font-size: 0.78em; font-style: italic; }
</style>
"""

# ============================================================
# Zodiac Man SVG (Homo Signorum)
# Stylized ASCII-art-inspired SVG showing sign locations on body
# ============================================================


def _build_zodiac_man_svg(
    highlighted_zones: Optional[List[str]] = None,
    risk_colors: Optional[Dict[str, str]] = None,
) -> str:
    """Build a classical Zodiac Man (Homo Signorum) SVG.

    Layout inspired by medieval manuscripts: human figure in center with
    zodiac signs arranged around it (Aries at top, Pisces at bottom,
    five signs each on left and right), connected by lines to body zones.

    Args:
        highlighted_zones: list of zone names to highlight
        risk_colors: zone -> CSS color string for risk visualization

    Returns:
        HTML div containing an inline SVG suitable for st.markdown()
        with unsafe_allow_html=True
    """
    highlighted_zones = highlighted_zones or []
    risk_colors = risk_colors or {}

    # ViewBox: 300 wide x 430 tall
    # Figure centre x=150, figure spans x=108..192
    W, H = 300, 430

    # Body zone highlight rectangles in figure coordinates
    # Each zone: (x, y, w, h) within the figure
    zone_rects = {
        "head":     (127, 22, 46, 40),
        "neck":     (135, 62, 30, 18),
        "arms":     (75,  80, 150, 55),
        "chest":    (118, 80, 64, 40),
        "heart":    (120, 118, 60, 30),
        "abdomen":  (118, 148, 64, 35),
        "kidneys":  (120, 178, 60, 28),
        "genitals": (125, 205, 50, 28),
        "hips":     (116, 230, 68, 30),
        "knees":    (120, 295, 60, 30),
        "ankles":   (122, 345, 56, 25),
        "feet":     (114, 368, 72, 28),
    }

    def _zone_color(zone: str) -> str:
        if zone in risk_colors:
            return risk_colors[zone]
        if zone in highlighted_zones:
            return "#C5A03F"
        return "none"

    zone_svg = ""
    for zone, (rx, ry, rw, rh) in zone_rects.items():
        c = _zone_color(zone)
        if c != "none":
            zone_svg += (
                f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="4"'
                f' fill="{c}" opacity="0.45" stroke="{c}" stroke-width="1"/>\n'
            )

    # ── Human silhouette ──────────────────────────────────────────────────
    # Drawn as a series of SVG paths; no XML comments to avoid parser issues
    gold = "#C5A03F"
    fig_fill = "#1c2b45"

    figure_svg = (
        # Head
        f'<ellipse cx="150" cy="42" rx="23" ry="24"'
        f' fill="{fig_fill}" stroke="{gold}" stroke-width="1.5"/>'
        # Face details
        f'<circle cx="143" cy="40" r="2.5" fill="{gold}" opacity="0.6"/>'
        f'<circle cx="157" cy="40" r="2.5" fill="{gold}" opacity="0.6"/>'
        f'<path d="M145,50 Q150,54 155,50" fill="none" stroke="{gold}" stroke-width="1" opacity="0.6"/>'
        # Neck
        f'<rect x="142" y="65" width="16" height="18" rx="4"'
        f' fill="{fig_fill}" stroke="{gold}" stroke-width="1"/>'
        # Torso
        f'<path d="M120,83 Q114,115 114,148 Q113,175 115,200 Q118,220 125,232'
        f' Q137,242 150,242 Q163,242 175,232 Q182,220 185,200'
        f' Q187,175 186,148 Q186,115 180,83 Z"'
        f' fill="{fig_fill}" stroke="{gold}" stroke-width="1.5"/>'
        # Left arm
        f'<path d="M120,88 Q96,98 80,118 Q70,132 72,148 Q79,145 84,134 Q94,116 122,103 Z"'
        f' fill="{fig_fill}" stroke="{gold}" stroke-width="1"/>'
        # Right arm
        f'<path d="M180,88 Q204,98 220,118 Q230,132 228,148 Q221,145 216,134 Q206,116 178,103 Z"'
        f' fill="{fig_fill}" stroke="{gold}" stroke-width="1"/>'
        # Left hand
        f'<ellipse cx="70" cy="150" rx="10" ry="7"'
        f' fill="{fig_fill}" stroke="{gold}" stroke-width="0.8"/>'
        # Right hand
        f'<ellipse cx="230" cy="150" rx="10" ry="7"'
        f' fill="{fig_fill}" stroke="{gold}" stroke-width="0.8"/>'
        # Left leg
        f'<path d="M128,242 Q122,278 124,315 Q125,345 126,370 Q128,385 132,396 L144,396'
        f' Q140,382 139,368 Q138,340 136,315 Q135,278 138,242 Z"'
        f' fill="{fig_fill}" stroke="{gold}" stroke-width="1"/>'
        # Right leg
        f'<path d="M172,242 Q178,278 176,315 Q175,345 174,370 Q172,385 168,396 L156,396'
        f' Q160,382 161,368 Q162,340 164,315 Q165,278 162,242 Z"'
        f' fill="{fig_fill}" stroke="{gold}" stroke-width="1"/>'
        # Left foot
        f'<ellipse cx="132" cy="398" rx="15" ry="7"'
        f' fill="{fig_fill}" stroke="{gold}" stroke-width="0.8"/>'
        # Right foot
        f'<ellipse cx="168" cy="398" rx="15" ry="7"'
        f' fill="{fig_fill}" stroke="{gold}" stroke-width="0.8"/>'
    )

    # ── Sign label positions and connecting line anchors ──────────────────
    # Layout mirrors the reference: Aries top-center, Pisces bottom-center,
    # left column (5): Gemini, Leo, Libra, Sagittarius, Aquarius
    # right column (5): Taurus, Cancer, Virgo, Scorpio, Capricorn
    #
    # Each entry: (sign, glyph, cn_name, body_part_cn, body_part_en,
    #              label_x, label_y, anchor, line_x1, line_y1, line_x2, line_y2)

    sign_rows = [
        # Aries — top center
        ("Aries",       "♈", "白羊", "頭面", "Head & Face",
         150,  8, "middle", 150, 18, 150, 32),
        # Taurus — right, neck
        ("Taurus",      "♉", "金牛", "頸喉", "Neck & Throat",
         278, 72, "end",    237, 72, 166, 72),
        # Gemini — left, arms/shoulders
        ("Gemini",      "♊", "雙子", "臂膊", "Arms & Shoulders",
         22, 110, "start",  63, 110,  98, 110),
        # Cancer — right, chest/stomach/lungs
        ("Cancer",      "♋", "巨蟹", "胸肺", "Chest & Lungs",
         278, 128, "end",   237, 128, 184, 120),
        # Leo — left, heart/back
        ("Leo",         "♌", "獅子", "心背", "Heart & Back",
         22, 148, "start",  63, 148,  118, 138),
        # Virgo — right, abdomen/belly
        ("Virgo",       "♍", "處女", "腹腸", "Abdomen & Bowels",
         278, 168, "end",   237, 168, 184, 162),
        # Libra — left, kidneys/loins
        ("Libra",       "♎", "天秤", "腎腰", "Kidneys & Loins",
         22, 192, "start",  63, 192,  118, 190),
        # Scorpio — right, genitals/bladder
        ("Scorpio",     "♏", "天蠍", "生殖", "Genitals & Bladder",
         278, 218, "end",   237, 218, 177, 218),
        # Sagittarius — left, thighs/hips
        ("Sagittarius", "♐", "射手", "髖腿", "Hips & Thighs",
         22, 248, "start",  63, 248,  118, 248),
        # Capricorn — right, knees
        ("Capricorn",   "♑", "摩羯", "膝蓋", "Knees",
         278, 308, "end",   237, 308, 182, 310),
        # Aquarius — left, legs/ankles
        ("Aquarius",    "♒", "水瓶", "小腿", "Legs & Ankles",
         22, 358, "start",  63, 358,  122, 358),
        # Pisces — bottom center
        ("Pisces",      "♓", "雙魚", "足部", "Feet",
         150, 422, "middle", 150, 412, 150, 396),
    ]

    labels_svg = ""
    for row in sign_rows:
        (sign, glyph, cn_name, body_cn, body_en,
         lx, ly, anchor, lx1, ly1, lx2, ly2) = row
        color = ZODIAC_BODY_PARTS[sign]["color"]
        labels_svg += (
            f'<line x1="{lx1}" y1="{ly1}" x2="{lx2}" y2="{ly2}"'
            f' stroke="{color}" stroke-width="1" opacity="0.75" stroke-dasharray="3,2"/>\n'
            f'<text x="{lx}" y="{ly}" text-anchor="{anchor}"'
            f' font-size="9" fill="{color}" font-family="serif" font-weight="bold">'
            f'{glyph} {cn_name}</text>\n'
            f'<text x="{lx}" y="{ly + 11}" text-anchor="{anchor}"'
            f' font-size="7.5" fill="#d4c08a" font-family="sans-serif">'
            f'{body_cn} {body_en}</text>\n'
        )

    # ── Decorative border ─────────────────────────────────────────────────
    border_svg = (
        f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="6"'
        f' fill="none" stroke="{gold}" stroke-width="1.2" opacity="0.4"/>'
        f'<rect x="5" y="5" width="{W-10}" height="{H-10}" rx="4"'
        f' fill="none" stroke="{gold}" stroke-width="0.5" opacity="0.2"/>'
    )

    # ── Title ────────────────────────────────────────────────────────────
    title_svg = (
        f'<text x="{W//2}" y="14" text-anchor="middle"'
        f' font-size="10" fill="{gold}" font-family="serif" font-weight="bold">'
        f'黃道人 Homo Signorum</text>'
    )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"'
        f' width="{W}" height="{H}"'
        f' style="background:linear-gradient(180deg,#0d1220 0%,#1a1000 100%);'
        f'border-radius:10px;display:block;max-width:100%;">'
        f'<defs>'
        f'<radialGradient id="zmGlow" cx="50%" cy="40%" r="45%">'
        f'<stop offset="0%" stop-color="#C5A03F" stop-opacity="0.07"/>'
        f'<stop offset="100%" stop-color="#000000" stop-opacity="0"/>'
        f'</radialGradient>'
        f'</defs>'
        f'<rect width="{W}" height="{H}" fill="url(#zmGlow)"/>'
        f'{border_svg}'
        f'{title_svg}'
        f'{zone_svg}'
        f'{figure_svg}'
        f'{labels_svg}'
        f'</svg>'
    )

    return f'<div style="display:flex;justify-content:center;margin:8px 0">{svg}</div>'


# ============================================================
# Helper renderers
# ============================================================

def _render_temperament_wheel(scores: Dict[str, float]) -> None:
    """Render a simple bar chart for the four humors."""
    try:
        import plotly.graph_objects as go  # type: ignore
    except ImportError:
        # Fallback to Streamlit metrics
        cols = st.columns(4)
        for i, (humor, score) in enumerate(scores.items()):
            hdata = FOUR_HUMORS.get(humor, {})
            cn = hdata.get("cn", humor)
            cols[i].metric(auto_cn(cn, humor), f"{score:.1f}")
        return

    lang = get_lang()
    labels = []
    values = []
    colors = []
    for humor, score in scores.items():
        hdata = FOUR_HUMORS.get(humor, {})
        cn = hdata.get("cn", humor)
        label = cn if lang == "zh" else humor
        labels.append(label)
        values.append(score)
        colors.append(hdata.get("color", "#888888"))

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        marker_line_color="#C5A03F",
        marker_line_width=1.5,
        text=[f"{v:.1f}" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        plot_bgcolor="#0d0d1a",
        paper_bgcolor="#0d0d1a",
        font=dict(color="#d4b896", size=12),
        height=280,
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        xaxis=dict(showgrid=False),
        showlegend=False,
        title=dict(
            text=auto_cn("四液體質平衡", "Four Humors Balance"),
            font=dict(color="#C5A03F", size=14),
            x=0.5,
        ),
    )
    st.plotly_chart(fig, width="stretch")


def _render_body_zone_table(body_zones: list, lang: str) -> None:
    """Render body zone health risk table."""
    import pandas as pd  # type: ignore

    rows = []
    for zone in body_zones:
        sign_data = ZODIAC_BODY_PARTS.get(zone.sign, {})
        glyph = sign_data.get("glyph", "")
        sign_cn = sign_data.get("sign_cn", zone.sign)

        if lang == "zh":
            sign_label = f"{glyph} {sign_cn}"
            parts = "、".join(zone.body_parts_cn[:3])
            risk_label = {"high": "⚠️ 高風險", "moderate": "⚡ 中風險", "low": "✅ 低風險"}.get(zone.risk_level, zone.risk_level)
            afflicting = "、".join(zone.afflicting_planets) if zone.afflicting_planets else "—"
            supporting = "、".join(zone.supporting_planets) if zone.supporting_planets else "—"
        else:
            sign_label = f"{glyph} {zone.sign}"
            parts = ", ".join(zone.body_parts_en[:3])
            risk_label = {"high": "⚠️ High", "moderate": "⚡ Moderate", "low": "✅ Low"}.get(zone.risk_level, zone.risk_level)
            afflicting = ", ".join(zone.afflicting_planets) if zone.afflicting_planets else "—"
            supporting = ", ".join(zone.supporting_planets) if zone.supporting_planets else "—"

        rows.append({
            auto_cn("星座", "Sign"): sign_label,
            auto_cn("身體部位", "Body Parts"): parts,
            auto_cn("風險", "Risk"): risk_label,
            auto_cn("受困行星", "Afflicting"): afflicting,
            auto_cn("保護行星", "Supporting"): supporting,
            auto_cn("得分", "Score"): f"{zone.net_score:+.1f}",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch")


def _planet_glyph(name: str) -> str:
    glyphs = {
        "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
        "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
        "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
    }
    return glyphs.get(name, name)


# ============================================================
# Main render function
# ============================================================

def render_streamlit(chart: MedicalChart) -> None:
    """Render the full Medical Astrology page."""
    st.markdown(_CSS, unsafe_allow_html=True)
    lang = get_lang()

    # Header
    st.markdown(
        f"""<div class="med-header">
        <h2>⚕️ {auto_cn("醫學占星 Medical Astrology", "Medical Astrology (Iatromathematics)")}</h2>
        <p>{auto_cn(
            "希臘・阿拉伯・中世紀歐洲傳統醫學占星 — 體質・身體易損區域・療癒擇時・危機日分析",
            "Classical Greek · Arabic · Medieval European Medical Astrology — Temperament · Body Vulnerabilities · Electional Timing · Crisis Days"
        )}</p>
        </div>""",
        unsafe_allow_html=True,
    )

    # Tabs
    tab_labels = [
        auto_cn("🧬 本命體質分析", "🧬 Natal Temperament"),
        auto_cn("🩻 健康易損區域", "🩻 Body Zone Health"),
        auto_cn("🗓️ 療癒擇時", "🗓️ Electional Timing"),
        auto_cn("⚡ 危機期分析", "⚡ Crisis Day Analysis"),
        auto_cn("🏛️ 旬星身體對照", "🏛️ Decan Body Mapping"),
    ]
    tabs = st.tabs(tab_labels)

    # ── Tab 1: Natal Temperament + Zodiac Man ──
    with tabs[0]:
        _render_tab_temperament(chart, lang)

    # ── Tab 2: Body Zone Health ──
    with tabs[1]:
        _render_tab_body_zones(chart, lang)

    # ── Tab 3: Electional Timing ──
    with tabs[2]:
        _render_tab_electional(chart, lang)

    # ── Tab 4: Critical Days ──
    with tabs[3]:
        _render_tab_critical_days(chart, lang)

    # ── Tab 5: Egyptian Decan Body Mapping ──
    with tabs[4]:
        _render_tab_decan_body(chart, lang)


# ============================================================
# Tab 1: Natal Temperament
# ============================================================

def _render_tab_temperament(chart: MedicalChart, lang: str) -> None:
    col_svg, col_info = st.columns([1, 1])

    # Build risk colors for Zodiac Man
    risk_colors: Dict[str, str] = {}
    for zone in chart.body_zones:
        body_zone = ZODIAC_BODY_PARTS.get(zone.sign, {}).get("zodiac_man_position", "")
        if zone.risk_level == "high":
            risk_colors[body_zone] = "#dc3545"
        elif zone.risk_level == "moderate":
            risk_colors[body_zone] = "#ffc107"
        else:
            risk_colors[body_zone] = "#28a745"

    with col_svg:
        st.markdown(
            auto_cn("### 🏛️ 黃道人圖 Zodiac Man", "### 🏛️ Homo Signorum — Zodiac Man"),
        )
        svg = _build_zodiac_man_svg(risk_colors=risk_colors)
        st.markdown(svg, unsafe_allow_html=True)
        st.caption(
            auto_cn(
                "🔴 高風險  🟡 中風險  🟢 低風險 — 顏色反映本命星盤中各身體區域的易損程度",
                "🔴 High risk  🟡 Moderate  🟢 Low risk — colors reflect natal chart vulnerability per body zone",
            )
        )

    with col_info:
        st.markdown(auto_cn("### 🧬 本命體質（四液質）", "### 🧬 Natal Temperament (Four Humors)"))

        temp = chart.temperament
        norm = temp.normalized()
        scores = temp.as_dict()

        # Dominant & secondary
        dominant = temp.dominant
        secondary = temp.secondary
        dom_data = TEMPERAMENT_DESCRIPTIONS.get(dominant, {})
        dom_cn = dom_data.get("cn", dominant)
        sec_data = TEMPERAMENT_DESCRIPTIONS.get(secondary, {})
        sec_cn = sec_data.get("cn", secondary)

        asc_data = ZODIAC_BODY_PARTS.get(chart.asc_sign, {})
        asc_cn = asc_data.get("sign_cn", chart.asc_sign)
        asc_glyph = asc_data.get("glyph", "")

        st.markdown(
            f"""<div class="humor-card">
            <h4>{auto_cn("主要體質", "Dominant Temperament")}: {auto_cn(dom_cn, dominant)} 
            &nbsp;|&nbsp; {auto_cn("次要體質", "Secondary")}: {auto_cn(sec_cn, secondary)}</h4>
            <p style="color:#d4b896;margin:0">
            {auto_cn("上升星座", "Ascendant")}: {asc_glyph} {auto_cn(asc_cn, chart.asc_sign)} &nbsp;|&nbsp;
            {auto_cn("元素", "Element")}: {auto_cn(asc_data.get("element","")+" 象", asc_data.get("element",""))}
            </p>
            </div>""",
            unsafe_allow_html=True,
        )

        _render_temperament_wheel(scores)

        # Dominant temperament description
        st.markdown(f"**{auto_cn('體質描述', 'Temperament Profile')}**")
        dom_desc = dom_data.get("health_cn" if lang == "zh" else "health_en", "")
        st.info(dom_desc)

        dom_lifestyle = dom_data.get("lifestyle_cn" if lang == "zh" else "lifestyle_en", "")
        with st.expander(auto_cn("💡 養生建議", "💡 Classical Lifestyle Advice")):
            st.write(dom_lifestyle)
            st.caption(
                auto_cn(
                    f"古典文獻: {dom_data.get('classical_ref','')}",
                    f"Classical ref: {dom_data.get('classical_ref','')}",
                )
            )

        # Planet placements overview
        st.markdown(f"**{auto_cn('行星位置摘要', 'Planet Positions Summary')}**")
        rows = []
        for p in chart.planets:
            if p.name not in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
                continue
            pmed = PLANET_MEDICAL.get(p.name, {})
            glyph = pmed.get("glyph", "")
            pname = f"{glyph} {auto_cn(pmed.get('cn', p.name), p.name)}"
            sign_data = ZODIAC_BODY_PARTS.get(p.sign, {})
            sign_label = (
                f"{sign_data.get('glyph','')} {sign_data.get('sign_cn', p.sign)}"
                if lang == "zh" else
                f"{sign_data.get('glyph','')} {p.sign}"
            )
            retro = "℞" if p.is_retrograde else ""
            rows.append({
                auto_cn("行星", "Planet"): pname,
                auto_cn("星座", "Sign"): sign_label,
                auto_cn("宮位", "House"): p.house,
                auto_cn("度數", "Degree"): f"{p.degree_in_sign:.1f}°{retro}",
                auto_cn("旬星", "Decan"): p.decan_number,
            })
        if rows:
            import pandas as pd
            df = pd.DataFrame(rows)
            st.dataframe(df, width="stretch")

        # Planetary medical info expanders
        st.markdown(f"**{auto_cn('行星醫療主管', 'Planetary Medical Rulerships')}**")
        for planet_name in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
            pmed = PLANET_MEDICAL.get(planet_name, {})
            glyph = pmed.get("glyph", "")
            cn_name = pmed.get("cn", planet_name)
            humor = pmed.get("humor_cn" if lang == "zh" else "humor", "")
            temp_q = pmed.get("temperament_cn" if lang == "zh" else "temperament", "")
            body_parts = pmed.get("body_parts_cn" if lang == "zh" else "body_parts_en", [])
            herbs = pmed.get("herbs_cn" if lang == "zh" else "herbs_en", [])
            with st.expander(f"{glyph} {auto_cn(cn_name, planet_name)} — {auto_cn(humor, pmed.get('humor',''))}"):
                st.write(
                    f"**{auto_cn('體液質','Humor')}**: {auto_cn(humor, pmed.get('humor',''))}  "
                    f"**{auto_cn('氣質','Temperament')}**: {auto_cn(temp_q, pmed.get('temperament',''))}"
                )
                bp_str = auto_cn("、".join(body_parts), ", ".join(pmed.get("body_parts_en", [])))
                st.write(f"**{auto_cn('主管身體','Body Parts')}**: {bp_str}")
                herb_str = auto_cn("、".join(herbs), ", ".join(pmed.get("herbs_en", [])))
                st.write(f"**{auto_cn('主管草藥','Ruling Herbs')}**: {herb_str}")
                st.caption(
                    auto_cn(
                        f"文獻: {pmed.get('classical_ref','')}",
                        f"Ref: {pmed.get('classical_ref','')}",
                    )
                )


# ============================================================
# Tab 2: Body Zone Health
# ============================================================

def _render_tab_body_zones(chart: MedicalChart, lang: str) -> None:
    st.markdown(auto_cn("### 🩻 各身體區域健康評估", "### 🩻 Body Zone Health Assessment"))
    st.caption(
        auto_cn(
            "依據托勒密《四書》及卡爾佩伯《疾病占星判斷》——惡星位置及刑衝相位提升易損度，吉星三合六分相提供保護。",
            "Based on Ptolemy Tetrabiblos & Culpeper — malefic positions and hard aspects increase vulnerability; benefic trines/sextiles provide protection.",
        )
    )

    # Sort: highest risk first
    sorted_zones = sorted(chart.body_zones, key=lambda z: z.net_score)

    # Risk summary at top
    high_risk = [z for z in sorted_zones if z.risk_level == "high"]
    mod_risk = [z for z in sorted_zones if z.risk_level == "moderate"]

    if high_risk:
        sign_names_cn = "、".join(
            ZODIAC_BODY_PARTS.get(z.sign, {}).get("sign_cn", z.sign) for z in high_risk
        )
        sign_names_en = ", ".join(z.sign for z in high_risk)
        parts_en = ", ".join(
            ", ".join(z.body_parts_en[:2]) for z in high_risk
        )
        parts_cn = "、".join(
            "、".join(z.body_parts_cn[:2]) for z in high_risk
        )
        st.error(
            auto_cn(
                f"⚠️ **高風險區域**: {sign_names_cn} — 主管 {parts_cn}",
                f"⚠️ **High-risk zones**: {sign_names_en} — governing {parts_en}",
            )
        )

    _render_body_zone_table(sorted_zones, lang)

    st.divider()

    # Detailed view per sign
    st.markdown(auto_cn("#### 各星座詳細分析", "#### Detailed Sign Analysis"))
    for zone in sorted_zones:
        sign_data = ZODIAC_BODY_PARTS.get(zone.sign, {})
        glyph = sign_data.get("glyph", "")
        sign_cn = sign_data.get("sign_cn", zone.sign)
        css_class = f"body-zone-{zone.risk_level}"

        if lang == "zh":
            title = f"{glyph} **{sign_cn}** ({zone.sign})"
            parts_str = "、".join(zone.body_parts_cn[:4])
            disease_str = "、".join(zone.diseases_cn[:3])
            afflic_str = "、".join(zone.afflicting_planets) if zone.afflicting_planets else "無"
            support_str = "、".join(zone.supporting_planets) if zone.supporting_planets else "無"
        else:
            title = f"{glyph} **{zone.sign}**"
            parts_str = ", ".join(zone.body_parts_en[:4])
            disease_str = ", ".join(zone.diseases_en[:3])
            afflic_str = ", ".join(zone.afflicting_planets) if zone.afflicting_planets else "None"
            support_str = ", ".join(zone.supporting_planets) if zone.supporting_planets else "None"

        desc = sign_data.get(
            "classical_desc_cn" if lang == "zh" else "classical_desc_en", ""
        )

        with st.expander(f"{title}  |  {auto_cn('得分','Score')}: {zone.net_score:+.1f}"):
            st.markdown(
                f"<div class='{css_class}'>"
                f"<strong>{auto_cn('主管部位', 'Body Parts')}:</strong> {parts_str}<br/>"
                f"<strong>{auto_cn('相關疾患', 'Related Diseases')}:</strong> {disease_str}<br/>"
                f"<strong>{auto_cn('受困行星', 'Afflicting Planets')}:</strong> {afflic_str}&nbsp;&nbsp;"
                f"<strong>{auto_cn('保護行星', 'Supporting Planets')}:</strong> {support_str}"
                f"</div>",
                unsafe_allow_html=True,
            )
            if desc:
                st.caption(desc)


# ============================================================
# Tab 3: Electional Timing
# ============================================================

def _render_tab_electional(chart: MedicalChart, lang: str) -> None:
    st.markdown(auto_cn("### 🗓️ 療癒擇時（Electional Astrology）", "### 🗓️ Medical Electional Timing"))
    st.caption(
        auto_cn(
            "依據蓋倫《醫療方法》、阿維森納《醫典》及卡爾佩伯《疾病占星判斷》的選時法則，為各類醫療操作尋找最佳時機。",
            "Based on Galen 'Method of Medicine', Avicenna 'Canon', & Culpeper — finding optimal times for medical procedures.",
        )
    )

    col1, col2 = st.columns(2)
    with col1:
        procedure_options = list(ELECTIONAL_RULES.keys())
        if lang == "zh":
            proc_labels = [
                f"{ELECTIONAL_RULES[p]['icon']} {ELECTIONAL_RULES[p]['name_cn']}"
                for p in procedure_options
            ]
        else:
            proc_labels = [
                f"{ELECTIONAL_RULES[p]['icon']} {ELECTIONAL_RULES[p]['name_en']}"
                for p in procedure_options
            ]
        proc_idx = st.selectbox(
            auto_cn("選擇醫療操作", "Select Medical Procedure"),
            range(len(procedure_options)),
            format_func=lambda i: proc_labels[i],
            key="med_elect_proc",
        )
    with col2:
        search_date = st.date_input(
            auto_cn("從此日期開始搜尋", "Search from date"),
            value=date.today(),
            key="med_elect_date",
        )
        search_days = st.slider(
            auto_cn("搜尋天數", "Search days"),
            min_value=3, max_value=28, value=14,
            key="med_elect_days",
        )

    procedure = procedure_options[proc_idx]
    proc_data = ELECTIONAL_RULES[procedure]
    proc_name = proc_data.get("name_cn" if lang == "zh" else "name_en", procedure)

    # Show classical rules
    with st.expander(auto_cn(f"📜 {proc_name} 古典擇時規則", f"📜 Classical Rules for {proc_name}")):
        favorable_list = proc_data.get("favorable_cn" if lang == "zh" else "favorable_en", [])
        avoid_list = proc_data.get("avoid_cn" if lang == "zh" else "avoid_en", [])
        st.markdown(auto_cn("**✅ 有利條件：**", "**✅ Favorable conditions:**"))
        for item in favorable_list:
            st.write(f"• {item}")
        st.markdown(auto_cn("**⚠️ 避免事項：**", "**⚠️ Avoid:**"))
        for item in avoid_list:
            st.write(f"• {item}")
        st.caption(auto_cn(f"文獻: {proc_data.get('classical_ref','')}", f"Ref: {proc_data.get('classical_ref','')}"))

    if st.button(
        auto_cn(f"🔍 搜尋最佳擇時", "🔍 Find Best Windows"),
        key="med_elect_search",
    ):
        with st.spinner(auto_cn("搜尋中…", "Searching…")):
            search_dt = datetime(search_date.year, search_date.month, search_date.day, 6, 0)
            windows = compute_electional_windows(
                procedure=procedure,
                search_from=search_dt,
                search_days=search_days,
                timezone=chart.timezone,
            )

        if not windows:
            st.warning(auto_cn(
                "在此期間內未找到符合條件的吉時，請延長搜尋天數。",
                "No favorable windows found in this period. Try extending the search range.",
            ))
        else:
            st.success(auto_cn(
                f"找到 {len(windows)} 個吉時（評分 ≥ 6.0）",
                f"Found {len(windows)} favorable windows (score ≥ 6.0)",
            ))
            for w in windows:
                moon_data = ZODIAC_BODY_PARTS.get(w.moon_sign, {})
                moon_cn = moon_data.get("sign_cn", w.moon_sign)
                moon_glyph = moon_data.get("glyph", "")
                phase_data = MOON_PHASE_MEDICAL.get(w.moon_phase, {})
                phase_name = phase_data.get("name_cn" if lang == "zh" else "name_en", w.moon_phase)

                fav_str = "  \n".join(f"✅ {f}" for f in w.favorable_factors)
                warn_str = "  \n".join(f"⚠️ {ww}" for ww in w.warning_factors)

                score_color = "#28a745" if w.score >= 8 else "#ffc107" if w.score >= 6 else "#dc3545"

                st.markdown(
                    f"""<div class="elect-card">
                    <span class="score" style="color:{score_color}">⭐ {w.score}/10</span>
                    &nbsp;&nbsp;
                    <strong>{w.start_dt.strftime("%Y-%m-%d %H:%M")} – {w.end_dt.strftime("%H:%M")}</strong>
                    &nbsp;|&nbsp; 
                    {auto_cn(f"月亮 {moon_glyph} {moon_cn}", f"Moon {moon_glyph} {w.moon_sign}")}
                    &nbsp;|&nbsp;
                    {auto_cn(f"月相: {phase_name}", f"Phase: {phase_name}")}
                    &nbsp;|&nbsp;
                    {auto_cn(f"行星時辰: {w.planetary_hour}", f"Planetary hour: {w.planetary_hour}")}
                    </div>""",
                    unsafe_allow_html=True,
                )
                if w.favorable_factors or w.warning_factors:
                    with st.expander(auto_cn("詳細因素", "Details")):
                        if fav_str:
                            st.write(fav_str)
                        if warn_str:
                            st.warning(warn_str)

    # Moon phase overview for today
    st.divider()
    st.markdown(auto_cn("#### 🌙 今日月相醫療意義", "#### 🌙 Today's Moon Phase — Medical Significance"))
    today_dt = datetime.now()
    today_jd = _julian_day(today_dt.year, today_dt.month, today_dt.day,
                           today_dt.hour, today_dt.minute, chart.timezone)
    today_phase_angle = _moon_phase_angle(today_jd)
    today_phase_key = _moon_phase_name(today_phase_angle)
    today_moon_lon = swe.calc_ut(today_jd, swe.MOON)[0][0]
    today_moon_sign = _sign_from_lon(today_moon_lon)
    today_hour_planet, _ = _get_planetary_hour(today_dt, chart.timezone)

    phase_info = MOON_PHASE_MEDICAL.get(today_phase_key, {})
    moon_data = ZODIAC_BODY_PARTS.get(today_moon_sign, {})

    col_a, col_b, col_c = st.columns(3)
    col_a.metric(
        auto_cn("今日月相", "Today Moon Phase"),
        phase_info.get("name_cn" if lang == "zh" else "name_en", today_phase_key),
        f"{today_phase_angle:.0f}°",
    )
    col_b.metric(
        auto_cn("月亮星座", "Moon Sign"),
        f"{moon_data.get('glyph','')} {moon_data.get('sign_cn', today_moon_sign) if lang=='zh' else today_moon_sign}",
    )
    col_c.metric(
        auto_cn("當前行星時辰", "Current Planetary Hour"),
        _planet_glyph(today_hour_planet) + " " + today_hour_planet,
    )

    med_sig = phase_info.get("medical_cn" if lang == "zh" else "medical_en", "")
    if med_sig:
        st.info(f"🌙 {med_sig}")


# ============================================================
# Tab 4: Critical Days
# ============================================================

def _render_tab_critical_days(chart: MedicalChart, lang: str) -> None:
    st.markdown(auto_cn("### ⚡ 疾病危機期分析", "### ⚡ Critical Day Analysis for Acute Illness"))
    st.caption(
        auto_cn(
            "依據希波克拉底《格言》第四卷36–40條、蓋倫《論危機日》、阿維森納《醫典》第一冊第三帖：急性疾病的月亮危機日計算。",
            "Based on Hippocrates 'Aphorisms' IV.36–40, Galen 'On Critical Days', Avicenna 'Canon' Book I, Fen 3.",
        )
    )

    with st.expander(auto_cn("📖 危機日理論說明", "📖 Theory of Critical Days")):
        st.markdown(
            auto_cn(
                """
**危機日（Critical Days）理論** — 希波克拉底與蓋倫傳統

急性疾病的發展遵循月亮的運行週期。月亮每約28天完成一次朔望週期，
在特定天數觸發疾病轉捩點（危機）或預示性變化（指示日）：

| 天數 | 類型 | 重要性 |
|------|------|--------|
| 第4天 | 指示日 | 月亮四分相 — 初步症狀指示 |
| 第7天 | **危機日** | 月亮對衝 — 主要轉捩點 |
| 第11天 | 指示日 | 月亮三合 — 好轉跡象 |
| 第14天 | **危機日** | 月亮回歸 — 第二轉捩點 |
| 第17天 | 指示日 | 第三象限 — 慢性化指示 |
| 第20天 | **危機日** | 最終急性危機 |
| 第24天 | 指示日 | 最終解除指示 |
| 第28天 | **危機日** | 最終判斷 — 痊癒或慢性化 |

*若疾病超過第20天仍未解除，蓋倫認為將轉為慢性疾患。*
                """,
                """
**Theory of Critical Days** — Hippocrates & Galen tradition

Acute illness follows the Moon's orbital cycle. As the Moon completes its ~28-day lunation,
it triggers crisis points (true critical days) and indicator days at specific intervals:

| Day | Type | Significance |
|-----|------|-------------|
| 4th | Indicator | Moon square — first symptom indicator |
| 7th | **Critical** | Moon opposition — major turning point |
| 11th | Indicator | Moon trine — watch for improvement |
| 14th | **Critical** | Moon return — second turning point |
| 17th | Indicator | 3rd quarter — indicates chronic development |
| 20th | **Critical** | Final acute crisis |
| 24th | Indicator | Final resolution indicator |
| 28th | **Critical** | Final judgment — recovery or chronic |

*If illness persists beyond day 20, Galen indicates transition to chronic disease.*
                """,
            )
        )

    st.markdown(auto_cn("#### 輸入疾病發作日期", "#### Enter Illness Onset Date"))
    onset_input = st.date_input(
        auto_cn("發病日期", "Illness Onset Date"),
        value=date.today(),
        key="med_crisis_onset",
    )

    if st.button(auto_cn("計算危機日", "Calculate Critical Days"), key="med_crisis_calc"):
        import swisseph as _swe
        jd_onset = _swe.julday(onset_input.year, onset_input.month, onset_input.day, 12.0)

        from .calculator import _compute_critical_days
        crisis_days = _compute_critical_days(onset_input, jd_onset)

        st.success(
            auto_cn(
                f"以 {onset_input.strftime('%Y年%m月%d日')} 為發病日計算得 {len(crisis_days)} 個危機/指示日",
                f"Computed {len(crisis_days)} crisis/indicator days from onset {onset_input.strftime('%Y-%m-%d')}",
            )
        )

        for cd in crisis_days:
            moon_at_onset_sign = _sign_from_lon(cd.moon_longitude_at_onset)
            moon_at_crisis_sign = _sign_from_lon(cd.moon_longitude_at_crisis)

            css_class = "crisis-critical" if cd.crisis_type == "critical" else "crisis-indicator"
            type_label = (
                auto_cn("⚡ 危機日", "⚡ Critical Day")
                if cd.crisis_type == "critical"
                else auto_cn("🔹 指示日", "🔹 Indicator Day")
            )
            onset_moon_glyph = ZODIAC_BODY_PARTS.get(moon_at_onset_sign, {}).get("glyph", "")
            crisis_moon_glyph = ZODIAC_BODY_PARTS.get(moon_at_crisis_sign, {}).get("glyph", "")

            significance = cd.significance_cn if lang == "zh" else cd.significance_en

            st.markdown(
                f"""<div class="{css_class}">
                <strong>{type_label}</strong> — 
                {auto_cn(f"第 {cd.crisis_day_number} 天", f"Day {cd.crisis_day_number}")}:
                <strong>{cd.crisis_date.strftime("%Y-%m-%d")}</strong>
                &nbsp;|&nbsp;
                {auto_cn("發病時月亮", "Moon at onset")}: {onset_moon_glyph} {moon_at_onset_sign}
                &nbsp;→&nbsp;
                {auto_cn("危機日月亮", "Moon at crisis")}: {crisis_moon_glyph} {moon_at_crisis_sign}
                <br/><small>{significance}</small>
                <br/><small class="ref-note">{cd.classical_ref}</small>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.info(auto_cn(
            "點擊「計算危機日」以計算疾病危機期。",
            "Click 'Calculate Critical Days' to compute illness crisis periods.",
        ))

        # Still show classical critical day reference table
        st.markdown(auto_cn("#### 📋 危機日參考表", "#### 📋 Critical Day Reference Table"))
        import pandas as pd
        rows = []
        for key, info in CRITICAL_DAYS.items():
            rows.append({
                auto_cn("天數", "Day"): info["day"],
                auto_cn("類型", "Type"): auto_cn(info["type_cn"], info["type"]),
                auto_cn("醫療意義", "Significance"): (
                    info["significance_cn"] if lang == "zh" else info["significance_en"]
                ),
                auto_cn("古典文獻", "Classical Ref"): info["classical_ref"],
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch")


# ============================================================
# Tab 5: Egyptian Decan Body Mapping
# ============================================================

def _render_tab_decan_body(chart: MedicalChart, lang: str) -> None:
    st.markdown(
        auto_cn("### 🏛️ 古埃及三十六旬星身體對照", "### 🏛️ Egyptian 36-Decan Body Zone Mapping")
    )
    st.caption(
        auto_cn(
            "依據馬尼利烏斯《天文學》、赫菲斯提奧《占星結果》、費爾米庫斯·馬特努斯《數學》——三十六旬星各自主管人體精細部位。",
            "Based on Manilius 'Astronomica', Hephaestio 'Apotelesmatika', Firmicus Maternus 'Mathesis' — each of the 36 decans governs specific body sub-zones.",
        )
    )

    # Show natal decan placements
    st.markdown(auto_cn("#### 🔑 本命三大旬星", "#### 🔑 Key Natal Decan Positions"))
    col1, col2, col3 = st.columns(3)

    def _decan_body_info(decan_idx: int, label_cn: str, label_en: str) -> None:
        body_info = DECAN_BODY_PARTS.get(decan_idx, {})
        body_en = body_info.get("body_en", "Unknown")
        body_cn = body_info.get("body_cn", "未知")
        ref = body_info.get("classical_ref", "")
        sign_idx = decan_idx // 3
        sign = ZODIAC_SIGN_ORDER[sign_idx]
        decan_num = (decan_idx % 3) + 1
        sign_data = ZODIAC_BODY_PARTS.get(sign, {})
        glyph = sign_data.get("glyph", "")
        sign_cn_label = sign_data.get("sign_cn", sign)

        st.metric(
            auto_cn(label_cn, label_en),
            auto_cn(body_cn, body_en),
            auto_cn(f"{glyph} {sign_cn_label} 第{decan_num}旬", f"{glyph} {sign} Decan {decan_num}"),
        )
        st.caption(auto_cn(f"文獻: {ref}", f"Ref: {ref}"))

    with col1:
        _decan_body_info(chart.asc_decan_index, "上升旬星主管", "ASC Decan Rules")
    with col2:
        _decan_body_info(chart.sun_decan_index, "太陽旬星主管", "Sun Decan Rules")
    with col3:
        _decan_body_info(chart.moon_decan_index, "月亮旬星主管", "Moon Decan Rules")

    st.divider()

    # Full 36-decan body mapping table
    st.markdown(auto_cn("#### 📋 三十六旬星完整身體對照", "#### 📋 Complete 36-Decan Body Reference"))

    # Group by sign
    for sign_idx, sign in enumerate(ZODIAC_SIGN_ORDER):
        sign_data = ZODIAC_BODY_PARTS.get(sign, {})
        glyph = sign_data.get("glyph", "")
        sign_cn = sign_data.get("sign_cn", sign)
        element = sign_data.get("element", "")

        with st.expander(
            f"{glyph} {auto_cn(sign_cn, sign)} ({element})"
        ):
            # Major sign body parts
            parts_cn = "、".join(sign_data.get("body_parts_cn", []))
            parts_en = ", ".join(sign_data.get("body_parts_en", []))
            st.write(
                f"**{auto_cn('星座主管', 'Sign rules')}**: "
                f"{auto_cn(parts_cn, parts_en)}"
            )

            # Three decans
            for decan_num in range(3):
                d_idx = sign_idx * 3 + decan_num
                body_info = DECAN_BODY_PARTS.get(d_idx, {})
                body_en = body_info.get("body_en", "")
                body_cn = body_info.get("body_cn", "")
                ref = body_info.get("classical_ref", "")

                # Check if any natal planet is in this decan
                natal_planets = [
                    p.name for p in chart.planets
                    if p.decan_index == d_idx
                ]
                planet_str = ""
                if natal_planets:
                    planet_strs = [
                        f"{_planet_glyph(p)} {auto_cn(PLANET_MEDICAL.get(p,{}).get('cn',p), p)}"
                        for p in natal_planets
                    ]
                    planet_str = " 🔴 " + auto_cn(
                        "本命行星: " + "、".join(planet_strs),
                        "Natal planet: " + ", ".join(planet_strs),
                    )

                st.markdown(
                    f"""<div class="decan-body-card">
                    <h5>{auto_cn(f"第{decan_num+1}旬", f"Decan {decan_num+1}")} 
                    ({sign_idx*30 + decan_num*10}°–{sign_idx*30 + decan_num*10 + 10}°)
                    {planet_str}</h5>
                    <strong>{auto_cn('主管', 'Rules')}:</strong> 
                    {auto_cn(body_cn, body_en)}<br/>
                    <small class="ref-note">{ref}</small>
                    </div>""",
                    unsafe_allow_html=True,
                )

    # Link to Egyptian Decans module
    st.divider()
    st.info(
        auto_cn(
            "💡 **深度分析**: 點擊左側側欄的「🏛️ 古埃及十度區間」模組，查看完整埃及旬星排盤，"
            "包含迦勒底主星、三分主星、塔羅對應及個人特質分析。",
            "💡 **Deep Analysis**: Navigate to '🏛️ Egyptian Decans' in the sidebar for the full decan chart, "
            "including Chaldean rulers, triplicity rulers, Tarot correspondences, and personality profiles.",
        )
    )
