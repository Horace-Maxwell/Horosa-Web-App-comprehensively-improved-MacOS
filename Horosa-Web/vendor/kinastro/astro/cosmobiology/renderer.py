"""
astro/cosmobiology/renderer.py — Streamlit UI for Ebertin Cosmobiology

Renders a five-tab interface, strictly faithful to Reinhold Ebertin's
original Cosmobiology system as described in COSI (1972 English edition).

Tabs:
    1. 本命中點樹  — Natal Midpoint Tree
    2. 90° Dial   — Interactive 90° Dial visualization (plotly)
    3. 行星組合解讀 — COSI planetary combination interpretations
    4. 合盤        — Synastry / Relationship Cosmobiology
    5. 事件比對    — Transit / Event comparison
"""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

import streamlit as st

from .calculator import (
    ComsobioChart,
    CosmoPoint,
    MidpointEntry,
    MidpointActivation,
    SynastryResult,
    TransitHit,
    compute_cosmobiology_chart,
    compute_synastry_midpoints,
    compute_transit_hits,
    _sign_from_lon,
    EBERTIN_ORDER,
)
from .constants import (
    PLANET_NAMES_EN,
    PLANET_NAMES_ZH,
    PLANET_SYMBOLS,
    PERSONAL_POINTS,
    ZODIAC_SIGNS,
    SIGN_CN,
    ORB_MAIN,
    ORB_TIGHT,
    COSI_DB,
    get_cosi_interpretation,
)
from astro.i18n import auto_cn, get_ui_lang, get_lang, t

# ============================================================
# CSS
# ============================================================

_CSS = """
<style>
.cosmo-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-left: 4px solid #e94560;
    padding: 12px 18px;
    border-radius: 6px;
    margin-bottom: 12px;
}
.cosmo-disclaimer {
    background: #1a1a1a;
    border: 1px solid #e94560;
    border-radius: 6px;
    padding: 10px 16px;
    font-size: 0.85em;
    color: #ccc;
    margin-bottom: 14px;
}
.cosmo-mp-personal {
    background: rgba(233, 69, 96, 0.12);
    border-left: 3px solid #e94560;
    border-radius: 4px;
    padding: 8px 12px;
    margin-bottom: 6px;
}
.cosmo-mp-normal {
    background: rgba(79, 140, 255, 0.08);
    border-left: 3px solid #4f8cff;
    border-radius: 4px;
    padding: 8px 12px;
    margin-bottom: 6px;
}
.cosmo-interp-box {
    background: rgba(255, 255, 255, 0.04);
    border-radius: 6px;
    padding: 10px 14px;
    margin-top: 6px;
    font-size: 0.93em;
}
.cosmo-tight { color: #ff6b6b; font-weight: bold; }
.cosmo-normal { color: #79c0ff; }
.cosmo-page-ref { color: #888; font-size: 0.82em; }
</style>
"""


# ============================================================
# Helpers
# ============================================================

def _is_zh() -> bool:
    return get_lang() in ("zh", "zh_cn")


def _pname(key: str) -> str:
    if _is_zh():
        return PLANET_NAMES_ZH.get(key, key)
    return PLANET_NAMES_EN.get(key, key)


def _sym(key: str) -> str:
    return PLANET_SYMBOLS.get(key, key)


def _orb_class(orb: float) -> str:
    return "cosmo-tight" if orb <= ORB_TIGHT else "cosmo-normal"


def _lon_str(lon: float) -> str:
    sign, deg = _sign_from_lon(lon)
    cn = SIGN_CN.get(sign, "")
    return f"{deg:05.2f}° {sign}({cn})"


def _dial_str(d: float) -> str:
    return f"{d:.2f}°"


# ============================================================
# 90° Dial visualization (plotly)
# ============================================================

def _build_dial_plotly(points: List[CosmoPoint]) -> None:
    """
    Render an interactive 90° Dial using plotly.

    The 90° Dial maps longitudes → longitude mod 90°,
    which collapses all hard aspects into conjunction.
    Planets are shown at their dial position around a 360° circle
    (each 90° of the ecliptic is displayed as a full quadrant).
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        st.warning("plotly not available. Install plotly to see the 90° Dial chart.")
        return

    fig = go.Figure()

    # Background circle
    theta_bg = list(range(0, 361, 1))
    fig.add_trace(go.Scatterpolar(
        r=[1.0] * 361,
        theta=theta_bg,
        mode="lines",
        line=dict(color="#3a3a6a", width=1),
        showlegend=False,
        hoverinfo="skip",
    ))

    # Inner ring at r=0.85
    fig.add_trace(go.Scatterpolar(
        r=[0.85] * 361,
        theta=theta_bg,
        mode="lines",
        line=dict(color="#2a2a4a", width=1, dash="dot"),
        showlegend=False,
        hoverinfo="skip",
    ))

    # Degree marks: every 5° on 90° Dial → every 20° on 360° display
    for d90 in range(0, 90, 5):
        disp_deg = d90 * 4   # map 90° dial → 360° visual
        is_major = (d90 % 15 == 0)
        r_inner = 0.88 if is_major else 0.92
        fig.add_trace(go.Scatterpolar(
            r=[r_inner, 1.0],
            theta=[disp_deg, disp_deg],
            mode="lines",
            line=dict(color="#a78bfa" if is_major else "#3a3a7a", width=2 if is_major else 1),
            showlegend=False,
            hoverinfo="skip",
        ))

    # Planet markers
    for p in sorted(points, key=lambda x: x.dial90):
        disp_deg = p.dial90 * 4  # 0–90° → 0–360°
        if p.is_personal:
            col = "#ff6b6b"
            r_pos = 0.70
        elif p.key in ("SO", "MO", "ME", "VE", "MA", "JU", "SA", "UR", "NE", "PL"):
            col = "#79c0ff"
            r_pos = 0.68
        else:
            col = "#ffd700"
            r_pos = 0.72

        label = f"{_sym(p.key)} {_pname(p.key)}"
        hover = (
            f"{_sym(p.key)} {PLANET_NAMES_EN.get(p.key, p.key)}<br>"
            f"Abs: {p.longitude:.2f}°<br>"
            f"Dial: {p.dial90:.2f}°<br>"
            f"{p.sign} {p.sign_degree:.2f}°"
        )
        fig.add_trace(go.Scatterpolar(
            r=[r_pos],
            theta=[disp_deg],
            mode="markers+text",
            marker=dict(size=10, color=col, symbol="circle"),
            text=[label],
            textposition="middle right",
            textfont=dict(size=9, color=col),
            hovertext=hover,
            hoverinfo="text",
            showlegend=False,
        ))

    fig.update_layout(
        polar=dict(
            bgcolor="#0f0f1a",
            angularaxis=dict(
                tickmode="array",
                tickvals=[d * 4 for d in range(0, 90, 15)],
                ticktext=[f"{d}°" for d in range(0, 90, 15)],
                rotation=90,
                direction="clockwise",
                gridcolor="#2a2a4a",
                linecolor="#3a3a6a",
                tickfont=dict(color="#b0b0d0", size=10),
            ),
            radialaxis=dict(visible=False, range=[0, 1.15]),
        ),
        paper_bgcolor="#0f0f1a",
        margin=dict(l=40, r=40, t=40, b=40),
        height=520,
        title=dict(
            text="90° Dial — Ebertin Cosmobiology",
            font=dict(color="#e0e0ff", size=14),
            x=0.5,
        ),
    )

    st.plotly_chart(fig, width="stretch")


# ============================================================
# Midpoint Tree tab
# ============================================================

def _render_midpoint_tree(
    chart: ComsobioChart,
    is_zh: bool,
    max_entries: int = 40,
) -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    if is_zh:
        st.subheader(auto_cn("📐 本命中點樹"))
        st.caption(auto_cn(
            f"Ebertin 規則：M(A/B) = (A + B) / 2。"
            f"容許度：±{ORB_MAIN}°（COSI 第9頁）。"
            f"按個人點優先、然後緊密度排列。"
        ))
    else:
        st.subheader("📐 Natal Midpoint Tree")
        st.caption(
            f"Ebertin rule: M(A/B) = (A + B) / 2. "
            f"Orb: ±{ORB_MAIN}° (COSI p. 9). "
            f"Sorted by personal-point involvement, then tightest orb."
        )

    if not chart.midpoint_tree:
        msg = auto_cn("未找到容許度範圍內的中點激活。") if is_zh else "No midpoint activations within orb."
        st.info(msg)
        return

    for entry in chart.midpoint_tree[:max_entries]:
        sym_a = _sym(entry.key_a)
        sym_b = _sym(entry.key_b)
        label_a = _pname(entry.key_a)
        label_b = _pname(entry.key_b)

        box_class = "cosmo-mp-personal" if entry.is_personal else "cosmo-mp-normal"

        # Activation summary line
        act_parts = []
        for act in entry.activations[:4]:
            orb_str = f"{act.orb:.2f}°"
            oc = "cosmo-tight" if act.orb <= ORB_TIGHT else "cosmo-normal"
            act_parts.append(
                f'<span class="{oc}">{_sym(act.activating_key)}{_pname(act.activating_key)}'
                f'({orb_str})</span>'
            )
        acts_html = " · ".join(act_parts)

        html = (
            f'<div class="{box_class}">'
            f'<b>{sym_a}{label_a} / {sym_b}{label_b}</b> '
            f'= {_lon_str(entry.longitude)} '
            f'[dial {_dial_str(entry.dial90)}]<br>'
            f'↳ {acts_html}'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

        # Expander with COSI interpretations
        exp_label = (
            f"{sym_a}{label_a}/{sym_b}{label_b} "
            + ("— COSI 解讀" if is_zh else "— COSI Interpretation")
        )
        with st.expander(exp_label, expanded=False):
            for act in entry.activations[:6]:
                _render_activation_interp(act, entry, is_zh)


def _render_activation_interp(
    act: MidpointActivation,
    entry: MidpointEntry,
    is_zh: bool,
) -> None:
    """Render the COSI interpretation for one midpoint activation."""
    p_sym = _sym(act.activating_key)
    p_name = _pname(act.activating_key)
    a_sym = _sym(entry.key_a)
    a_name = _pname(entry.key_a)
    b_sym = _sym(entry.key_b)
    b_name = _pname(entry.key_b)

    tight_label = auto_cn("（緊密）") if act.orb <= ORB_TIGHT else ""
    if is_zh:
        st.markdown(
            f"**{p_sym}{p_name} = {a_sym}{a_name}/{b_sym}{b_name}** "
            f"容許度 `{act.orb:.2f}°`{tight_label}"
        )
    else:
        st.markdown(
            f"**{p_sym}{p_name} = {a_sym}{a_name}/{b_sym}{b_name}** "
            f"orb `{act.orb:.2f}°`{tight_label}"
        )

    # Interpretation for (activating, key_a)
    for interp, partner_key in [(act.interp_pa, entry.key_a), (act.interp_pb, entry.key_b)]:
        if interp is None:
            continue
        p2_sym = _sym(partner_key)
        p2_name = _pname(partner_key)
        key = f"<span class='cosmo-page-ref'>({interp.get('page', '')})</span>"
        if is_zh:
            with st.container():
                st.markdown(
                    f'<div class="cosmo-interp-box">'
                    f'<b>{p_sym}{p_name} ∿ {p2_sym}{p2_name}</b> {key}<br>'
                    f'<b>原則：</b>{interp.get("principle_zh", "")}<br>'
                    f'<b>正面：</b>{interp.get("positive_zh", "")}<br>'
                    f'<b>負面：</b>{interp.get("negative_zh", "")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            with st.container():
                st.markdown(
                    f'<div class="cosmo-interp-box">'
                    f'<b>{p_sym}{p_name} ∿ {p2_sym}{p2_name}</b> {key}<br>'
                    f'<b>Principle:</b> {interp.get("principle_en", "")}<br>'
                    f'<b>Positive:</b> {interp.get("positive_en", "")}<br>'
                    f'<b>Negative:</b> {interp.get("negative_en", "")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# ============================================================
# 90° Dial tab
# ============================================================

def _render_dial_tab(chart: ComsobioChart, is_zh: bool) -> None:
    if is_zh:
        st.subheader(auto_cn("🔵 90° 轉盤"))
        st.caption(auto_cn(
            "所有強相位（合、半刑、刑、倍半刑、沖）在90°轉盤上等同於合相。"
            "轉盤位置 = 黃經 mod 90°（COSI 第8頁）。"
        ))
    else:
        st.subheader("🔵 90° Dial")
        st.caption(
            "All hard aspects (0°, 45°, 90°, 135°, 180°) collapse to conjunction "
            "on the 90° Dial. Dial position = longitude mod 90° (COSI p. 8)."
        )

    _build_dial_plotly(chart.points)

    st.markdown("---")
    # Planet table
    rows = []
    for p in sorted(chart.points, key=lambda x: x.dial90):
        tag = "⭐" if p.is_personal else "🪐" if p.key in ("UR", "NE", "PL") else "🔵"
        if is_zh:
            rows.append({
                "": tag,
                "行星 / 點": f"{_sym(p.key)} {_pname(p.key)}",
                "絕對黃經": f"{p.longitude:.4f}°",
                "星座 / 度數": f"{p.sign}({SIGN_CN.get(p.sign, '')}) {p.sign_degree:.2f}°",
                "90°轉盤": f"{p.dial90:.4f}°",
            })
        else:
            rows.append({
                "": tag,
                "Planet / Point": f"{_sym(p.key)} {PLANET_NAMES_EN.get(p.key, p.key)}",
                "Abs. Longitude": f"{p.longitude:.4f}°",
                "Sign / Degree": f"{p.sign}({SIGN_CN.get(p.sign, '')}) {p.sign_degree:.2f}°",
                "90° Dial": f"{p.dial90:.4f}°",
            })
    st.dataframe(rows, hide_index=True, width="stretch")


# ============================================================
# COSI Interpretation tab
# ============================================================

def _render_cosi_interpretations(chart: ComsobioChart, is_zh: bool) -> None:
    if is_zh:
        st.subheader(auto_cn("📖 行星組合解讀 — Ebertin COSI 資料庫"))
        st.caption(auto_cn(
            "所有詮釋均直接取自 Reinhold Ebertin《行星影響力的組合》（COSI，1972年英文版）。"
        ))
    else:
        st.subheader("📖 Planetary Combinations — Ebertin COSI Database")
        st.caption(
            "All interpretations are taken directly from Reinhold Ebertin, "
            '"The Combination of Stellar Influences" (COSI, 1972 English edition).'
        )

    # Build list of all combinations that have COSI entries from this chart
    pos_keys = [p.key for p in chart.points]
    found_entries = []
    shown_keys = set()

    for i in range(len(pos_keys)):
        for j in range(i + 1, len(pos_keys)):
            ka, kb = pos_keys[i], pos_keys[j]
            interp = get_cosi_interpretation(ka, kb)
            if interp and (ka, kb) not in shown_keys:
                shown_keys.add((ka, kb))
                found_entries.append((ka, kb, interp))

    if not found_entries:
        st.info("No COSI entries found." if not is_zh else auto_cn("未找到 COSI 詮釋條目。"))
        return

    # Group by focal planet
    st.markdown(
        auto_cn("### 選擇組合瀏覽詳細解讀") if is_zh else "### Browse Combinations"
    )

    # Filter by personal-point involvement
    personal_entries = [(ka, kb, i) for ka, kb, i in found_entries
                        if ka in PERSONAL_POINTS or kb in PERSONAL_POINTS]
    other_entries = [(ka, kb, i) for ka, kb, i in found_entries
                     if ka not in PERSONAL_POINTS and kb not in PERSONAL_POINTS]

    if is_zh:
        group_label_p = auto_cn("⭐ 個人點組合（太陽、月亮、上升、天頂、北交點）")
        group_label_o = auto_cn("🔵 其他行星組合")
    else:
        group_label_p = "⭐ Personal Point Combinations (SO, MO, AS, MC, NN)"
        group_label_o = "🔵 Other Planetary Combinations"

    for group_label, group in [(group_label_p, personal_entries), (group_label_o, other_entries)]:
        if not group:
            continue
        with st.expander(group_label, expanded=(group is personal_entries)):
            for ka, kb, interp in group:
                sym_a, sym_b = _sym(ka), _sym(kb)
                name_a, name_b = _pname(ka), _pname(kb)
                with st.expander(
                    f"{sym_a}{name_a} ∿ {sym_b}{name_b}  —  {interp.get('page', '')}"
                ):
                    if is_zh:
                        st.markdown(f"**原則：** {interp.get('principle_zh', '')}")
                        st.markdown(f"**正面表現：** {interp.get('positive_zh', '')}")
                        st.markdown(f"**負面表現：** {interp.get('negative_zh', '')}")
                    else:
                        st.markdown(f"**Principle:** {interp.get('principle_en', '')}")
                        st.markdown(f"**Positive:** {interp.get('positive_en', '')}")
                        st.markdown(f"**Negative:** {interp.get('negative_en', '')}")
                    st.caption(interp.get("page", ""))


# ============================================================
# Synastry tab
# ============================================================

def _render_synastry_tab(natal_chart: ComsobioChart, calc_params: dict, is_zh: bool) -> None:
    if is_zh:
        st.subheader(auto_cn("💑 合盤 — 宇宙生物學關係分析"))
        st.caption(auto_cn(
            "依照 Ebertin《應用宇宙生物學》：計算兩盤之間的交叉中點，"
            "並在90°轉盤上查找任何行星的激活。"
        ))
    else:
        st.subheader("💑 Synastry — Cosmobiology Relationship Analysis")
        st.caption(
            "Following Ebertin, Applied Cosmobiology: "
            "cross-midpoints between two charts, activated on the 90° Dial."
        )

    st.markdown("---")
    if is_zh:
        st.markdown(auto_cn("#### 第二人出生資料"))
    else:
        st.markdown("#### Person B Birth Data")

    col1, col2, col3 = st.columns(3)
    with col1:
        b_date = st.date_input(
            auto_cn("出生日期 (B)") if is_zh else "Birth Date (B)",
            value=date(1990, 6, 15),
            key="cosmo_syn_date",
        )
    with col2:
        b_time = st.time_input(
            auto_cn("出生時間 (B)") if is_zh else "Birth Time (B)",
            value=datetime.strptime("12:00", "%H:%M").time(),
            key="cosmo_syn_time",
        )
    with col3:
        b_tz = st.number_input(
            auto_cn("時區 (B)") if is_zh else "Timezone (B)",
            value=8.0, min_value=-12.0, max_value=14.0, step=0.5,
            key="cosmo_syn_tz",
        )

    col4, col5 = st.columns(2)
    with col4:
        b_lat = st.number_input(
            auto_cn("緯度 (B)") if is_zh else "Latitude (B)",
            value=22.3, min_value=-90.0, max_value=90.0, step=0.01,
            key="cosmo_syn_lat",
        )
    with col5:
        b_lon = st.number_input(
            auto_cn("經度 (B)") if is_zh else "Longitude (B)",
            value=114.1, min_value=-180.0, max_value=180.0, step=0.01,
            key="cosmo_syn_lon",
        )

    if st.button(auto_cn("計算合盤") if is_zh else "Calculate Synastry",
                 key="cosmo_syn_calc"):
        try:
            chart_b = compute_cosmobiology_chart(
                year=b_date.year, month=b_date.month, day=b_date.day,
                hour=b_time.hour, minute=b_time.minute,
                timezone=b_tz,
                latitude=b_lat,
                longitude=b_lon,
            )
            synastry = compute_synastry_midpoints(natal_chart, chart_b)
            st.session_state["cosmo_synastry"] = synastry
        except Exception as e:
            st.error(f"Error: {e}")
            return

    if "cosmo_synastry" in st.session_state:
        _display_synastry(st.session_state["cosmo_synastry"], is_zh)


def _display_synastry(synastry: SynastryResult, is_zh: bool) -> None:
    if not synastry.cross_midpoints:
        msg = auto_cn("未找到交叉中點激活。") if is_zh else "No cross-midpoint activations found."
        st.info(msg)
        return

    st.markdown("---")
    if is_zh:
        st.markdown(auto_cn(f"**找到 {len(synastry.cross_midpoints)} 個交叉中點激活**"))
    else:
        st.markdown(f"**{len(synastry.cross_midpoints)} cross-midpoint activations found**")

    for mp in synastry.cross_midpoints[:30]:
        ka, kb = mp.key_a, mp.key_b
        min_orb = min(a.orb for a in mp.activations) if mp.activations else 99.0
        is_personal = ka in PERSONAL_POINTS or kb in PERSONAL_POINTS
        box_class = "cosmo-mp-personal" if is_personal else "cosmo-mp-normal"

        act_strs = [
            f'{_sym(a.activating_key)}{_pname(a.activating_key)}({a.orb:.2f}°)'
            for a in mp.activations[:3]
        ]
        html = (
            f'<div class="{box_class}">'
            f'<b>{_sym(ka)}{_pname(ka)}(A) / {_sym(kb)}{_pname(kb)}(B)</b> '
            f'= {_lon_str(mp.longitude)} [dial {_dial_str(mp.dial90)}]<br>'
            f'↳ {" · ".join(act_strs)}'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)
    st.markdown(_CSS, unsafe_allow_html=True)


# ============================================================
# Transit tab
# ============================================================

def _render_transit_tab(natal_chart: ComsobioChart, is_zh: bool) -> None:
    if is_zh:
        st.subheader(auto_cn("🌐 事件比對 — 過境激活本命中點"))
        st.caption(auto_cn(
            "過境行星過本命中點 = 觸發 COSI 行星組合的生命事件時機。"
        ))
    else:
        st.subheader("🌐 Transit / Event — Transiting Planets to Natal Midpoints")
        st.caption(
            "A transiting planet activating a natal midpoint triggers the "
            "COSI planetary combination as a life event timing indicator."
        )

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        t_date = st.date_input(
            auto_cn("過境日期") if is_zh else "Transit Date",
            value=date.today(),
            key="cosmo_tr_date",
        )
    with col2:
        t_time = st.time_input(
            auto_cn("過境時間") if is_zh else "Transit Time",
            value=datetime.strptime("12:00", "%H:%M").time(),
            key="cosmo_tr_time",
        )
    with col3:
        t_tz = st.number_input(
            auto_cn("時區") if is_zh else "Timezone",
            value=8.0, min_value=-12.0, max_value=14.0, step=0.5,
            key="cosmo_tr_tz",
        )

    if st.button(auto_cn("計算過境") if is_zh else "Calculate Transits",
                 key="cosmo_tr_calc"):
        try:
            hits = compute_transit_hits(
                natal=natal_chart,
                transit_year=t_date.year,
                transit_month=t_date.month,
                transit_day=t_date.day,
                transit_hour=t_time.hour,
                transit_minute=t_time.minute,
                transit_tz=t_tz,
            )
            st.session_state["cosmo_transit_hits"] = hits
        except Exception as e:
            st.error(f"Error: {e}")
            return

    if "cosmo_transit_hits" in st.session_state:
        _display_transit_hits(st.session_state["cosmo_transit_hits"], is_zh)


def _display_transit_hits(hits: List[TransitHit], is_zh: bool) -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    if not hits:
        msg = auto_cn("無過境激活本命中點。") if is_zh else "No transit activations of natal midpoints."
        st.info(msg)
        return

    if is_zh:
        st.markdown(auto_cn(f"**找到 {len(hits)} 個過境激活**"))
    else:
        st.markdown(f"**{len(hits)} transit activations found**")

    for hit in hits[:40]:
        ka, kb = hit.natal_key_a, hit.natal_key_b
        is_personal = (
            ka in PERSONAL_POINTS or kb in PERSONAL_POINTS
            or hit.transit_key in PERSONAL_POINTS
        )
        box_class = "cosmo-mp-personal" if is_personal else "cosmo-mp-normal"

        if is_zh:
            headline = (
                f"過境 {_sym(hit.transit_key)}{_pname(hit.transit_key)} "
                f"= {_sym(ka)}{_pname(ka)}/{_sym(kb)}{_pname(kb)} "
                f"容許度 {hit.orb:.2f}°"
            )
        else:
            headline = (
                f"Transit {_sym(hit.transit_key)}{_pname(hit.transit_key)} "
                f"= {_pname(ka)}/{_pname(kb)} "
                f"orb {hit.orb:.2f}°"
            )
        st.markdown(f'<div class="{box_class}"><b>{headline}</b></div>', unsafe_allow_html=True)

        # Show COSI interpretation
        for interp, partner_key in [(hit.interp_ta, ka), (hit.interp_tb, kb)]:
            if not interp:
                continue
            with st.expander(
                f"{_sym(hit.transit_key)}{_pname(hit.transit_key)} ∿ "
                f"{_sym(partner_key)}{_pname(partner_key)} — {interp.get('page', '')}"
            ):
                if is_zh:
                    st.markdown(f"**原則：** {interp.get('principle_zh', '')}")
                    st.markdown(f"**正面：** {interp.get('positive_zh', '')}")
                    st.markdown(f"**負面：** {interp.get('negative_zh', '')}")
                else:
                    st.markdown(f"**Principle:** {interp.get('principle_en', '')}")
                    st.markdown(f"**Positive:** {interp.get('positive_en', '')}")
                    st.markdown(f"**Negative:** {interp.get('negative_en', '')}")
                st.caption(interp.get("page", ""))


# ============================================================
# Main renderer
# ============================================================

def render_cosmobiology(chart: ComsobioChart) -> None:
    """
    Render the complete Cosmobiology analysis in Streamlit.

    Five tabs as per the COSI system:
        1. 本命中點樹  — Natal Midpoint Tree
        2. 90° Dial   — Interactive dial visualization
        3. 行星組合解讀 — COSI planetary combinations browser
        4. 合盤        — Synastry relationship analysis
        5. 事件比對    — Transit analysis
    """
    st.markdown(_CSS, unsafe_allow_html=True)

    is_zh = _is_zh()

    # ── Header
    if is_zh:
        st.markdown(
            '<div class="cosmo-header">'
            '<h3 style="margin:0;color:#e0e0ff;">🔬 宇宙生物學 Cosmobiology</h3>'
            '<p style="margin:4px 0 0 0;color:#aaa;font-size:0.9em;">'
            'Reinhold Ebertin — 中點樹占星 · 90° 轉盤 · COSI</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="cosmo-disclaimer">'
            '⚠️ <b>聲明：</b>本模組100%依照 Reinhold Ebertin 原著 '
            '<em>The Combination of Stellar Influences</em>（COSI，1972年英文版）'
            '及《應用宇宙生物學》設計，不添加任何後世心理學或進化性詮釋。'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="cosmo-header">'
            '<h3 style="margin:0;color:#e0e0ff;">🔬 Cosmobiology — Reinhold Ebertin</h3>'
            '<p style="margin:4px 0 0 0;color:#aaa;font-size:0.9em;">'
            'Midpoint Tree · 90° Dial · COSI Database</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="cosmo-disclaimer">'
            '⚠️ <b>Disclaimer:</b> This module is 100% faithful to Reinhold Ebertin\'s '
            'original <em>The Combination of Stellar Influences</em> (COSI, 1972 English edition) '
            'and <em>Applied Cosmobiology</em>. No modern psychological or evolutionary '
            'interpretations have been added.'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Tabs
    if is_zh:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            auto_cn("📐 本命中點樹"),
            "🔵 90° Dial",
            auto_cn("📖 行星組合解讀"),
            auto_cn("💑 合盤"),
            auto_cn("🌐 事件比對"),
        ])
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📐 Midpoint Tree",
            "🔵 90° Dial",
            "📖 COSI Interpretations",
            "💑 Synastry",
            "🌐 Transits",
        ])

    calc_params = st.session_state.get("_calc_params", {})

    with tab1:
        _render_midpoint_tree(chart, is_zh)

    with tab2:
        _render_dial_tab(chart, is_zh)

    with tab3:
        _render_cosi_interpretations(chart, is_zh)

    with tab4:
        _render_synastry_tab(chart, calc_params, is_zh)

    with tab5:
        _render_transit_tab(chart, is_zh)
