# -*- coding: utf-8 -*-
"""
astro/human_design/renderer.py — Human Design 人間圖 Streamlit UI + BodyGraph SVG

Includes:
  - render_streamlit(): Full Streamlit UI for Human Design chart
  - render_bodygraph_svg(): High-quality SVG BodyGraph visualization with
    defined/undefined centers, active channels, gate activations.

BodyGraph Visual Design:
  The BodyGraph is the standard Human Design chart diagram showing 9 centers
  connected by channels in a specific anatomical layout. Defined (activated)
  centers and channels are shown in color; undefined ones in outline only.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Set, Tuple

import streamlit as st
import streamlit.components.v1 as components

from .calculator import (
    GateActivation,
    HumanDesignChart,
    compute_human_design_chart,
)
from .constants import (
    AUTHORITY_INFO,
    AUTHORITY_ZH,
    CENTER_EN,
    CENTER_ZH,
    CHANNELS,
    DEFINITION_EN,
    DEFINITION_ZH,
    EXAMPLE_CHARTS,
    GATE_TO_CENTER,
    PLANET_ZH,
    PROFILE_INFO,
    STRATEGY_ZH,
    TYPE_INFO,
    TYPE_ZH,
    CROSS_ANGLE_ZH,
)
from astro.i18n import auto_cn, t


# ============================================================
#  Color palette
# ============================================================

_CENTER_COLORS: Dict[str, str] = {
    "Head":         "#c8a8e8",   # lavender
    "Ajna":         "#8ab4f8",   # blue
    "Throat":       "#f8c8a8",   # peach
    "G":            "#f8e8a8",   # gold
    "Ego":          "#f8a8a8",   # rose
    "SolarPlexus":  "#a8d8f8",   # sky blue
    "Sacral":       "#c8f8a8",   # lime green
    "Spleen":       "#f8d8a8",   # warm amber
    "Root":         "#d8a8f8",   # mauve
}

_CENTER_COLORS_UNDEFINED = "#e8e8e8"
_CENTER_STROKE_DEFINED   = "#555555"
_CENTER_STROKE_UNDEFINED = "#aaaaaa"

_CHANNEL_COLOR_P  = "#d44"    # personality channel — red
_CHANNEL_COLOR_D  = "#44d"    # design channel — blue
_CHANNEL_COLOR_PD = "#d4d"    # mixed (P+D) — purple
_CHANNEL_COLOR_UNDEF = "#ddd" # undefined

# CSS for the UI
_HD_CSS = """
<style>
.hd-header {
    background: linear-gradient(135deg, #0d1a2b 0%, #1a2a4d 40%, #2d0a4e 100%);
    border-left: 4px solid #6b8cff;
    padding: 14px 20px;
    border-radius: 8px;
    margin-bottom: 14px;
}
.hd-type-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 1.1em;
    margin: 4px 0;
}
.hd-section {
    background: rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    border: 1px solid rgba(255,255,255,0.1);
}
.hd-gate-p { color: #ff6666; font-weight: bold; }
.hd-gate-d { color: #6688ff; font-weight: bold; }
.hd-gate-pd { color: #cc44cc; font-weight: bold; }
.hd-center-defined { color: #44cc44; font-weight: bold; }
.hd-center-undef { color: #888888; }
</style>
"""


# ============================================================
#  BodyGraph SVG generation
# ============================================================

# Center positions in the SVG (cx, cy, shape)
# Layout follows the standard Human Design BodyGraph anatomical positions
_CENTER_POSITIONS: Dict[str, Tuple[float, float, str]] = {
    # (cx, cy, shape)  shape: "diamond" | "square" | "triangle"
    "Head":        (250, 60,  "diamond"),
    "Ajna":        (250, 130, "diamond"),
    "Throat":      (250, 220, "diamond"),
    "G":           (250, 340, "diamond"),
    "Ego":         (195, 295, "diamond"),
    "SolarPlexus": (305, 400, "square"),
    "Sacral":      (250, 450, "square"),
    "Spleen":      (165, 370, "diamond"),
    "Root":        (250, 550, "square"),
}

# Channel paths between centers (pairs of center names)
_CHANNEL_PATHS: List[Tuple[str, str]] = [
    ("Head", "Ajna"),
    ("Ajna", "Throat"),
    ("Throat", "G"),
    ("Throat", "Ego"),
    ("Throat", "SolarPlexus"),
    ("Throat", "Spleen"),
    ("Throat", "Sacral"),
    ("G", "Sacral"),
    ("G", "Spleen"),
    ("G", "Ego"),
    ("Ego", "SolarPlexus"),
    ("Ego", "Spleen"),
    ("SolarPlexus", "Sacral"),
    ("SolarPlexus", "Root"),
    ("Sacral", "Spleen"),
    ("Sacral", "Root"),
    ("Spleen", "Root"),
]

_CENTER_SIZE = 38   # half-width of diamond / square
_GATE_FONT   = 9


def _center_shape_path(cx: float, cy: float, size: float, shape: str) -> str:
    """Return SVG path for a center shape."""
    s = size
    if shape == "diamond":
        return (
            f"M {cx},{cy - s} "
            f"L {cx + s},{cy} "
            f"L {cx},{cy + s} "
            f"L {cx - s},{cy} Z"
        )
    else:  # square / rectangle
        hw = s * 0.88
        return (
            f"M {cx - hw},{cy - hw} "
            f"H {cx + hw} V {cy + hw} H {cx - hw} Z"
        )


def render_bodygraph_svg(
    chart: HumanDesignChart,
    width: int = 500,
    height: int = 650,
) -> str:
    """
    Generate a BodyGraph SVG for the given Human Design chart.

    Defined centers are filled with their characteristic color; undefined centers
    are shown as outlines. Active channels are colored by origin:
      Red (Personality only), Blue (Design only), Purple (both).

    Args:
        chart: Computed HumanDesignChart
        width, height: SVG dimensions

    Returns:
        SVG XML string suitable for components.html()
    """
    defined = chart.defined_centers

    # Determine channel color — which channels are active and which chart they come from
    p_gates = {a.gate for a in chart.personality_activations}
    d_gates = {a.gate for a in chart.design_activations}

    # For each pair of connected centers, determine activation color
    center_channel_status: Dict[Tuple[str, str], str] = {}
    for ch_act in chart.active_channels:
        ca = ch_act.center_a
        cb = ch_act.center_b
        key = (min(ca, cb), max(ca, cb))
        ga, gb = ch_act.channel.gate_a, ch_act.channel.gate_b
        a_in_p = ga in p_gates or gb in p_gates
        a_in_d = ga in d_gates or gb in d_gates
        if a_in_p and a_in_d:
            color = _CHANNEL_COLOR_PD
        elif a_in_p:
            color = _CHANNEL_COLOR_P
        else:
            color = _CHANNEL_COLOR_D
        center_channel_status[key] = color

    lines: List[str] = []
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'style="background:#111827;border-radius:12px;">'
    )

    # Background gradient
    lines.append("""
    <defs>
      <radialGradient id="bg_grad" cx="50%" cy="40%" r="60%">
        <stop offset="0%" style="stop-color:#1e2a4a;stop-opacity:1"/>
        <stop offset="100%" style="stop-color:#0d1117;stop-opacity:1"/>
      </radialGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#bg_grad)" rx="12"/>
    """)

    # Title
    hd_type = chart.type_name
    type_zh = TYPE_ZH.get(hd_type, hd_type)
    lines.append(
        f'<text x="{width//2}" y="22" text-anchor="middle" '
        f'font-size="13" font-family="sans-serif" fill="#aac8ff" '
        f'font-weight="bold">人間圖 Human Design BodyGraph</text>'
    )
    lines.append(
        f'<text x="{width//2}" y="38" text-anchor="middle" '
        f'font-size="11" font-family="sans-serif" fill="#88aacc">'
        f'{type_zh} · {hd_type} · {chart.profile} · {chart.authority}</text>'
    )

    # ── Draw channel connections (lines between centers)
    for ca, cb in _CHANNEL_PATHS:
        pos_a = _CENTER_POSITIONS.get(ca)
        pos_b = _CENTER_POSITIONS.get(cb)
        if not pos_a or not pos_b:
            continue
        key = (min(ca, cb), max(ca, cb))
        color = center_channel_status.get(key, _CHANNEL_COLOR_UNDEF)
        stroke_w = 5 if key in center_channel_status else 2
        opacity = "1.0" if key in center_channel_status else "0.25"
        lines.append(
            f'<line x1="{pos_a[0]}" y1="{pos_a[1]}" '
            f'x2="{pos_b[0]}" y2="{pos_b[1]}" '
            f'stroke="{color}" stroke-width="{stroke_w}" '
            f'opacity="{opacity}" stroke-linecap="round"/>'
        )

    # ── Draw centers
    for center_name, (cx, cy, shape) in _CENTER_POSITIONS.items():
        is_defined = center_name in defined
        fill = _CENTER_COLORS.get(center_name, "#888") if is_defined else _CENTER_COLORS_UNDEFINED
        stroke = _CENTER_STROKE_DEFINED if is_defined else _CENTER_STROKE_UNDEFINED
        stroke_w = 2 if is_defined else 1.5
        opacity = "1.0" if is_defined else "0.5"

        path_d = _center_shape_path(cx, cy, _CENTER_SIZE, shape)
        lines.append(
            f'<path d="{path_d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{stroke_w}" opacity="{opacity}"/>'
        )

        # Center label (short name)
        short_names = {
            "Head": "HEAD", "Ajna": "AJNA", "Throat": "THROAT",
            "G": "G", "Ego": "EGO", "SolarPlexus": "SP",
            "Sacral": "SAC", "Spleen": "SPL", "Root": "ROOT",
        }
        label = short_names.get(center_name, center_name[:3].upper())
        txt_color = "#111" if is_defined else "#888"
        lines.append(
            f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" '
            f'font-size="10" font-family="sans-serif" '
            f'font-weight="bold" fill="{txt_color}">{label}</text>'
        )

    # ── Draw active gate numbers near their center
    _draw_gate_labels(lines, chart, p_gates, d_gates)

    # ── Legend
    legend_y = height - 65
    lines.append(
        f'<text x="10" y="{legend_y}" font-size="9" fill="#888" font-family="sans-serif">'
        f'● Personality (有意識)</text>'
    )
    lines.append(
        f'<rect x="135" y="{legend_y - 7}" width="12" height="12" fill="{_CHANNEL_COLOR_P}" rx="2"/>'
    )
    lines.append(
        f'<text x="10" y="{legend_y + 14}" font-size="9" fill="#888" font-family="sans-serif">'
        f'● Design (無意識)</text>'
    )
    lines.append(
        f'<rect x="135" y="{legend_y + 7}" width="12" height="12" fill="{_CHANNEL_COLOR_D}" rx="2"/>'
    )
    lines.append(
        f'<text x="155" y="{legend_y}" font-size="9" fill="#888" font-family="sans-serif">'
        f'Mixed P+D</text>'
    )
    lines.append(
        f'<rect x="210" y="{legend_y - 7}" width="12" height="12" fill="{_CHANNEL_COLOR_PD}" rx="2"/>'
    )

    lines.append("</svg>")
    return "\n".join(lines)


def _draw_gate_labels(
    lines: List[str],
    chart: HumanDesignChart,
    p_gates: Set[int],
    d_gates: Set[int],
) -> None:
    """Add small gate number labels near each center for active gates."""
    from .constants import CENTER_GATES

    # Collect per-center active gates with label info
    center_gate_info: Dict[str, List[Tuple[int, str, str]]] = {}
    # (gate, "P"/"D"/"PD", label_color)

    for center, gates in CENTER_GATES.items():
        entries = []
        for g in gates:
            in_p = g in p_gates
            in_d = g in d_gates
            if in_p and in_d:
                entries.append((g, "PD", _CHANNEL_COLOR_PD))
            elif in_p:
                entries.append((g, "P", _CHANNEL_COLOR_P))
            elif in_d:
                entries.append((g, "D", _CHANNEL_COLOR_D))
        if entries:
            center_gate_info[center] = entries

    for center, entries in center_gate_info.items():
        if center not in _CENTER_POSITIONS:
            continue
        cx, cy, _ = _CENTER_POSITIONS[center]

        # Spread gate labels in a small arc around the center
        n = len(entries)
        radius = _CENTER_SIZE + 14
        for i, (gate, src, color) in enumerate(entries):
            angle = math.pi * (i / max(n - 1, 1)) if n > 1 else 0
            angle -= math.pi / 2  # start from top
            gx = cx + radius * math.cos(angle)
            gy = cy + radius * math.sin(angle)
            lines.append(
                f'<text x="{gx:.1f}" y="{gy:.1f}" text-anchor="middle" '
                f'font-size="{_GATE_FONT}" font-family="sans-serif" '
                f'fill="{color}" font-weight="bold">{gate}</text>'
            )


# ============================================================
#  Main Streamlit renderer
# ============================================================

def render_streamlit(chart: HumanDesignChart) -> None:
    """
    Render a complete Human Design chart in Streamlit.

    Sections:
    1. Type + Strategy + Authority (core)
    2. Profile + Definition
    3. Incarnation Cross
    4. BodyGraph SVG visualization
    5. Defined centers + active channels table
    6. Planet activations table (Personality + Design)
    """
    import streamlit as st
    lang = st.session_state.get("lang", "zh")

    st.markdown(_HD_CSS, unsafe_allow_html=True)

    hd_type = chart.type_name
    type_zh = TYPE_ZH.get(hd_type, hd_type)
    strategy_zh = STRATEGY_ZH.get(chart.strategy, chart.strategy)
    authority_zh = AUTHORITY_ZH.get(chart.authority, chart.authority)
    profile_data = PROFILE_INFO.get(chart.profile, {})
    definition_zh = DEFINITION_ZH.get(chart.definition, chart.definition)
    definition_en = DEFINITION_EN.get(chart.definition, chart.definition)

    # ── Header
    st.markdown(
        f'<div class="hd-header">'
        f'<b style="font-size:1.2em;color:#aac8ff">☯ 人間圖 / Human Design</b><br>'
        f'<span style="color:#ccc">{chart.location_name} · '
        f'{chart.year}-{chart.month:02d}-{chart.day:02d} '
        f'{chart.hour:02d}:{chart.minute:02d} UTC{chart.timezone:+.1f}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Type badge
    TYPE_BADGE_COLORS = {
        "Manifestor":            "#c0392b",
        "Generator":             "#27ae60",
        "Manifesting Generator": "#2980b9",
        "Projector":             "#8e44ad",
        "Reflector":             "#16a085",
    }
    badge_color = TYPE_BADGE_COLORS.get(hd_type, "#555")
    st.markdown(
        f'<div class="hd-type-badge" style="background:{badge_color};color:white;'
        f'border-radius:8px;padding:8px 18px;">'
        f'🎯 類型 Type：{type_zh} / {hd_type}</div>',
        unsafe_allow_html=True,
    )

    # ── Core triplet: Type / Strategy / Authority
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label=auto_cn("策略 Strategy", en_text="Strategy"),
            value=strategy_zh if lang == "zh" else chart.strategy,
        )
    with col2:
        st.metric(
            label=auto_cn("內在權威 Authority", en_text="Authority"),
            value=authority_zh if lang == "zh" else chart.authority,
        )
    with col3:
        profile_label = profile_data.get("name_zh" if lang == "zh" else "name_en", chart.profile)
        st.metric(
            label=auto_cn("輪廓 Profile", en_text="Profile"),
            value=f"{chart.profile} · {profile_label}",
        )

    # Type description
    type_info = TYPE_INFO.get(hd_type, {})
    desc_key = "desc_zh" if lang == "zh" else "desc_en"
    if desc_key in type_info:
        with st.expander(auto_cn("🎯 類型與策略詳解", en_text="Type & Strategy Details"), expanded=False):
            st.markdown(type_info[desc_key])
            not_self_key = "not_self_zh" if lang == "zh" else "not_self_en"
            sig_key = "signature_zh" if lang == "zh" else "signature_en"
            col_a, col_b = st.columns(2)
            with col_a:
                st.error(
                    f"⚠️ " +
                    auto_cn("非我主題 (Not-Self): ", en_text="Not-Self Theme: ") +
                    type_info.get(not_self_key, "")
                )
            with col_b:
                st.success(
                    f"✅ " +
                    auto_cn("簽名主題 (Signature): ", en_text="Signature Theme: ") +
                    type_info.get(sig_key, "")
                )

    # Authority description
    auth_info = AUTHORITY_INFO.get(chart.authority, {})
    auth_desc = auth_info.get("desc_zh" if lang == "zh" else "desc_en", "")
    if auth_desc:
        with st.expander(auto_cn("⚡ 內在權威詳解", en_text="Authority Details"), expanded=False):
            st.markdown(f"**{authority_zh}**：{auth_desc}")

    st.divider()

    # ── Profile + Definition + Cross
    col_p, col_d, col_c = st.columns(3)
    with col_p:
        st.markdown(f"**{auto_cn('輪廓', en_text='Profile')}**")
        st.markdown(
            f"**{chart.profile}** — "
            + (profile_data.get("name_zh") if lang == "zh" else profile_data.get("name_en", ""))
        )
        if "theme_zh" in profile_data:
            st.caption(profile_data["theme_zh"])
    with col_d:
        st.markdown(f"**{auto_cn('定義', en_text='Definition')}**")
        st.markdown(definition_zh if lang == "zh" else definition_en)
    with col_c:
        st.markdown(f"**{auto_cn('人生十字架', en_text='Incarnation Cross')}**")
        angle_zh = CROSS_ANGLE_ZH.get(chart.cross_angle, chart.cross_angle)
        st.markdown(angle_zh if lang == "zh" else chart.cross_angle)
        st.caption(chart.cross_name_zh if lang == "zh" else chart.cross_name_en)

    st.divider()

    # ── BodyGraph SVG + Centers/Channels side by side
    col_svg, col_info = st.columns([1, 1])

    with col_svg:
        st.markdown(f"**{auto_cn('人體圖 BodyGraph', en_text='BodyGraph')}**")
        svg_html = render_bodygraph_svg(chart, width=480, height=640)
        components.html(svg_html, height=660, scrolling=False)

    with col_info:
        # Defined centers
        st.markdown(f"**{auto_cn('九大中心 — 定義/開放', en_text='Nine Centers — Defined/Open')}**")
        from .constants import CENTER_GATES
        center_rows = []
        for center in [
            "Head", "Ajna", "Throat", "G", "Ego",
            "SolarPlexus", "Sacral", "Spleen", "Root"
        ]:
            is_def = center in chart.defined_centers
            status_zh = "✅ 定義" if is_def else "⬜ 開放"
            status_en = "✅ Defined" if is_def else "⬜ Open"
            cname = CENTER_ZH.get(center, center) if lang == "zh" else CENTER_EN.get(center, center)
            center_rows.append({
                auto_cn("中心", en_text="Center"):  cname,
                auto_cn("狀態", en_text="Status"): status_zh if lang == "zh" else status_en,
            })
        import pandas as pd
        df_centers = pd.DataFrame(center_rows)
        st.dataframe(df_centers, width="stretch", hide_index=True)

        # Active channels
        st.markdown(f"**{auto_cn('活躍通道', en_text='Active Channels')}**")
        if chart.active_channels:
            ch_rows = []
            for ch_act in chart.active_channels:
                gate_a, gate_b = ch_act.channel.gates
                name = ch_act.channel.name_zh if lang == "zh" else ch_act.channel.name_en
                ch_rows.append({
                    auto_cn("通道", en_text="Channel"): f"{gate_a}–{gate_b}",
                    auto_cn("名稱", en_text="Name"): name,
                    auto_cn("來源", en_text="Source"): f"{ch_act.gate_a_source} / {ch_act.gate_b_source}",
                })
            df_channels = pd.DataFrame(ch_rows)
            st.dataframe(df_channels, width="stretch", hide_index=True)
        else:
            st.info(auto_cn("無活躍通道（全開放命盤）", en_text="No active channels (all centers open)."))

    st.divider()

    # ── Planet activations table
    with st.expander(
        auto_cn("🪐 行星閘門啟動（有意識/無意識）",
                en_text="🪐 Planet Gate Activations (Personality/Design)"),
        expanded=False,
    ):
        rows = []
        for p_act, d_act in zip(chart.personality_activations, chart.design_activations):
            pname = PLANET_ZH.get(p_act.planet, p_act.planet) if lang == "zh" else p_act.planet
            p_src = "P" if p_act.is_personality else "D"
            rows.append({
                auto_cn("行星", en_text="Planet"): pname,
                auto_cn("有意識閘門 (P)", en_text="Personality Gate (P)"): (
                    f"{p_act.gate}.{p_act.line} "
                    f"({'R' if p_act.retrograde else ''})"
                ).strip(),
                auto_cn("有意識黃道", en_text="Personality Lon."): f"{p_act.longitude:.2f}°",
                auto_cn("無意識閘門 (D)", en_text="Design Gate (D)"): (
                    f"{d_act.gate}.{d_act.line} "
                    f"({'R' if d_act.retrograde else ''})"
                ).strip(),
                auto_cn("無意識黃道", en_text="Design Lon."): f"{d_act.longitude:.2f}°",
            })
        import pandas as pd
        df_acts = pd.DataFrame(rows)
        st.dataframe(df_acts, width="stretch", hide_index=True)

    # ── Design date info
    st.caption(
        auto_cn(
            f"設計時間 Design Date（太陽弧約88°前）："
            f"{chart.design_year}-{chart.design_month:02d}-{chart.design_day:02d}",
            en_text=(
                f"Design Date (Solar Arc ~88° before birth): "
                f"{chart.design_year}-{chart.design_month:02d}-{chart.design_day:02d}"
            ),
        )
    )
