"""
Polynesian / Hawaiian Star Lore — Streamlit Renderer

Renders the full multi-tab UI for the Polynesian / Hawaiian star lore module.
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING

import streamlit as st

from astro.i18n import auto_cn

if TYPE_CHECKING:
    from .calculator import PolynesianResult

# ============================================================
# Theme colours
# ============================================================

_HAW_BG = "#0A2540"
_HAW_CARD = "#0D3461"
_HAW_BORDER = "#D4A017"   # gold
_HAW_HEADER = "#F5D06A"   # soft gold
_HAW_TEXT = "#E8F4FD"
_HAW_TEAL = "#0B8FA8"
_HAW_OCEAN = "#1A6BA0"
_HAW_RED = "#C0392B"

# ============================================================
# Compass plot coordinate constants
# ============================================================
# Stars with altitude 0°–90° are mapped to radius 0.9 (horizon) → 0.05 (zenith).
_COMPASS_RADIUS_HORIZON: float = 0.9   # radius for a star on the horizon
_COMPASS_RADIUS_ZENITH: float = 0.05   # radius for a star at zenith (alt=90°)
_COMPASS_ALT_MAX: float = 90.0         # degrees; full scale for altitude mapping

# Star marker sizes (matplotlib scatter `s` units)
_MARKER_SIZE_MIN: float = 20.0         # minimum marker area
_MARKER_SIZE_BASE: float = 120.0       # base area (magnitude 0 star)
_MARKER_SIZE_MAG_SCALE: float = 30.0   # area reduction per magnitude unit

# ============================================================
# Internal helpers
# ============================================================

def _card(title: str, body: str, border_color: str = _HAW_BORDER) -> None:
    """Render a styled markdown card."""
    st.markdown(
        f"""<div style="
            background:{_HAW_CARD};border-left:4px solid {border_color};
            border-radius:6px;padding:14px 18px;margin:8px 0;">
            <b style="color:{_HAW_HEADER};">{title}</b>
            <div style="color:{_HAW_TEXT};margin-top:6px;">{body}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def _status_badge(status: str) -> str:
    colours = {
        "rising": _HAW_TEAL,
        "setting": _HAW_OCEAN,
        "culminating": _HAW_BORDER,
        "above": "#4A7C59",
        "below": "#5A5A6A",
    }
    labels_zh = {
        "rising": "升起", "setting": "落下",
        "culminating": "中天", "above": "高空", "below": "地平線下",
    }
    labels_en = {
        "rising": "Rising", "setting": "Setting",
        "culminating": "Culminating", "above": "Above", "below": "Below",
    }
    c = colours.get(status, "#888")
    lbl = auto_cn(labels_zh.get(status, status), labels_en.get(status, status))
    return (f'<span style="background:{c};color:white;'
            f'padding:2px 8px;border-radius:10px;font-size:0.82em;">{lbl}</span>')


# ============================================================
# Tab 1 — 32-House Star Compass (matplotlib polar)
# ============================================================

def _render_compass_tab(result: "PolynesianResult") -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        import numpy as np
    except ImportError:
        st.warning("matplotlib is required for the compass visualisation.")
        return

    from .constants import COMPASS_HOUSES

    fig = plt.figure(figsize=(9, 9), facecolor=_HAW_BG)
    ax = fig.add_subplot(111, polar=True)
    ax.set_facecolor(_HAW_BG)

    n_houses = len(COMPASS_HOUSES)
    house_angle = 2 * math.pi / n_houses  # radians per house

    highlight_idx = result.compass_house_highlight

    for h in COMPASS_HOUSES:
        idx = h["index"]
        # Polar plot: 0 = East, angles go counter-clockwise
        # We want N at top, clockwise → convert:  θ = π/2 - azimuth_rad
        az_rad = math.radians(h["direction_deg"])
        theta = math.pi / 2 - az_rad

        # Draw sector
        theta_start = theta - house_angle / 2
        theta_end = theta + house_angle / 2
        thetas = np.linspace(theta_start, theta_end, 20)
        r_inner, r_outer = 0.35, 1.0

        if idx == highlight_idx:
            fc = "#D4A017"
            alpha = 0.55
        elif idx % 6 == 0:  # cardinal / semi-cardinal
            fc = "#1A3A5C"
            alpha = 0.9
        else:
            fc = "#0D2540"
            alpha = 0.7

        verts_x = (list(r_inner * np.cos(thetas))
                   + list(r_outer * np.cos(thetas[::-1])))
        verts_y = (list(r_inner * np.sin(thetas))
                   + list(r_outer * np.sin(thetas[::-1])))
        ax.fill(verts_x + [verts_x[0]], verts_y + [verts_y[0]],
                color=fc, alpha=alpha, transform=ax.transData)
        ax.plot(list(thetas) + [thetas[0]],
                [r_outer] * len(thetas) + [r_outer],
                color=_HAW_BORDER, lw=0.4, alpha=0.6)

        # Label for cardinal/semi-cardinal houses and highlighted
        if idx % 6 == 0 or idx == highlight_idx:
            label_r = 1.12
            ax.text(theta, label_r, h["hawaiian"],
                    ha="center", va="center", fontsize=6.5,
                    color=_HAW_HEADER if idx == highlight_idx else _HAW_TEXT,
                    fontweight="bold" if idx == highlight_idx else "normal",
                    rotation=0,
                    transform=ax.transData)

    # Plot stars
    for sp in result.star_positions:
        if sp["status"] == "below":
            continue
        az_rad = math.radians(sp["azimuth"])
        theta = math.pi / 2 - az_rad
        alt = sp["altitude"]
        # Map altitude 0°–90° linearly to radius _COMPASS_RADIUS_HORIZON–_COMPASS_RADIUS_ZENITH
        r = max(
            _COMPASS_RADIUS_ZENITH,
            _COMPASS_RADIUS_HORIZON - alt / _COMPASS_ALT_MAX * (_COMPASS_RADIUS_HORIZON - _COMPASS_RADIUS_ZENITH),
        )

        mag = sp.get("magnitude", 2.0)
        # Larger magnitude (dimmer) → smaller marker; clamp to minimum
        size = max(_MARKER_SIZE_MIN, _MARKER_SIZE_BASE - mag * _MARKER_SIZE_MAG_SCALE)
        color = _HAW_BORDER if sp["status"] == "culminating" else _HAW_TEAL

        ax.scatter([theta], [r], s=size, color=color, zorder=5,
                   transform=ax.transData)
        ax.text(theta, r - 0.07, sp["hawaiian_name"],
                ha="center", va="center", fontsize=5.5,
                color=_HAW_HEADER, zorder=6,
                transform=ax.transData)

    # Compass labels for N/S/E/W
    for direction, az_d, label in [
        ("N", 0, "N\nHema Ko Luna"),
        ("E", 90, "E\nHikina"),
        ("S", 180, "S\nHema Ko Lalo"),
        ("W", 270, "W\nKomohana"),
    ]:
        az_rad = math.radians(az_d)
        theta = math.pi / 2 - az_rad
        ax.text(theta, 1.28, label, ha="center", va="center",
                fontsize=8, color=_HAW_BORDER, fontweight="bold",
                transform=ax.transData)

    ax.set_ylim(0, 1.4)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines["polar"].set_visible(False)

    guardian_name = result.guardian_house.get("hawaiian", "—")
    fig.suptitle(
        f"32-House Star Compass  ·  Guardian House: {guardian_name}",
        color=_HAW_HEADER, fontsize=11, y=0.98,
    )

    st.pyplot(fig, width="content")
    plt.close(fig)

    # Table of all compass houses
    st.markdown(
        f"<h4 style='color:{_HAW_TEAL};'>"
        + auto_cn("32星屋列表", "32-House Compass Index")
        + "</h4>",
        unsafe_allow_html=True,
    )
    import pandas as pd
    rows = []
    for h in COMPASS_HOUSES:
        rows.append({
            auto_cn("星屋", "House"): h["hawaiian"],
            auto_cn("英文", "English"): h["english"],
            auto_cn("中文", "Chinese"): h["cn"],
            auto_cn("方位角", "Azimuth°"): f"{h['direction_deg']:.2f}°",
            auto_cn("象限", "Quadrant"): h["quadrant"],
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, width=800)


# ============================================================
# Tab 2 — Star Lines
# ============================================================

def _render_star_lines_tab(result: "PolynesianResult") -> None:
    from .constants import STAR_LINES
    import pandas as pd

    st.markdown(
        f"<h4 style='color:{_HAW_TEAL};'>"
        + auto_cn("主要星線", "Major Star Lines")
        + "</h4>",
        unsafe_allow_html=True,
    )

    rows = []
    for line_name, info in STAR_LINES.items():
        rows.append({
            auto_cn("星線", "Star Line"): line_name,
            auto_cn("中文名", "Chinese"): info["cn"],
            auto_cn("描述", "Description"): auto_cn(
                info["description_cn"], info["description"]
            ),
            auto_cn("主要星辰", "Key Stars"): ", ".join(info["stars"]),
        })

    st.dataframe(pd.DataFrame(rows), width=900)

    st.markdown("---")
    for line_name, info in STAR_LINES.items():
        with st.expander(f"✦ {line_name} — {info['cn']}"):
            st.markdown(
                f"**{auto_cn('描述', 'Description')}:** "
                + auto_cn(info["description_cn"], info["description"])
            )
            st.markdown(
                f"**{auto_cn('意義', 'Significance')}:** "
                + auto_cn(
                    info.get("significance_cn", ""),
                    info.get("significance", ""),
                )
            )
            star_list = info.get("stars_western", info["stars"])
            known = [
                sp for sp in result.star_positions
                if sp["western_name"] in star_list
            ]
            if known:
                st.markdown(
                    f"**{auto_cn('現在位置', 'Current Positions')}:**"
                )
                for sp in known:
                    st.markdown(
                        f"- **{sp['hawaiian_name']}** ({sp['western_name']}): "
                        f"Alt {sp['altitude']:.1f}°, Az {sp['azimuth']:.1f}° "
                        + _status_badge(sp["status"]),
                        unsafe_allow_html=True,
                    )


# ============================================================
# Tab 3 — Mythology
# ============================================================

def _render_mythology_tab(result: "PolynesianResult") -> None:
    from .constants import HAWAIIAN_STARS

    st.markdown(
        f"<h4 style='color:{_HAW_TEAL};'>"
        + auto_cn("星辰神話故事", "Star Mythology Stories")
        + "</h4>",
        unsafe_allow_html=True,
    )

    for sp in result.star_positions:
        wname = sp["western_name"]
        info = HAWAIIAN_STARS.get(wname, {})
        myth = auto_cn(info.get("mythology_cn", ""), info.get("mythology", ""))
        if not myth:
            continue

        with st.expander(
            f"🌟 {sp['hawaiian_name']} ({wname}) — "
            + auto_cn(sp["meaning_cn"], sp["meaning"])
        ):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric(
                    auto_cn("高度", "Altitude"),
                    f"{sp['altitude']:.1f}°",
                )
                st.metric(
                    auto_cn("方位角", "Azimuth"),
                    f"{sp['azimuth']:.1f}°",
                )
                st.metric(
                    auto_cn("星屋", "House"),
                    sp["compass_house"].get("hawaiian", "—"),
                )
            with col2:
                st.markdown(
                    f"<div style='color:{_HAW_TEXT};line-height:1.7;'>"
                    f"{myth}</div>",
                    unsafe_allow_html=True,
                )
                pron = info.get("pronunciation", "")
                if pron:
                    st.caption(f"🔊 {pron}")


# ============================================================
# Tab 4 — Personal Guardian Star
# ============================================================

def _render_guardian_tab(result: "PolynesianResult") -> None:
    gh = result.guardian_house
    gs = result.guardian_star

    st.markdown(
        f"<h4 style='color:{_HAW_BORDER};'>"
        + auto_cn("🌺 個人守護星屋", "🌺 Personal Guardian Star House")
        + "</h4>",
        unsafe_allow_html=True,
    )

    if not gh:
        st.info(auto_cn("無法計算守護星屋。", "Guardian house could not be computed."))
        return

    # Use actual computed guardian star data; fall back to Hōkūleʻa defaults
    gs_hawaiian = gs.get("hawaiian_name", "Hōkūleʻa") if gs else "Hōkūleʻa"
    gs_western = gs.get("western_name", "Arcturus") if gs else "Arcturus"
    gs_meaning = auto_cn(
        gs.get("meaning_cn", "喜悅之星") if gs else "喜悅之星",
        gs.get("meaning", "Star of Gladness") if gs else "Star of Gladness",
    )
    gs_key_use = auto_cn(
        gs.get("key_use_cn", "夏威夷天頂星") if gs else "夏威夷天頂星",
        gs.get("key_use", "Zenith Star of Hawaiʻi") if gs else "Zenith Star of Hawaiʻi",
    )

    st.markdown(
        f"""<div style="
            background:linear-gradient(135deg,{_HAW_CARD},{_HAW_BG});
            border:2px solid {_HAW_BORDER};border-radius:12px;
            padding:20px 24px;margin:10px 0;">
            <div style="font-size:2.2em;text-align:center;
                color:{_HAW_BORDER};margin-bottom:8px;">⭐</div>
            <h3 style="color:{_HAW_HEADER};text-align:center;margin:0;">
                {gs_hawaiian} ({gs_western})
            </h3>
            <p style="color:{_HAW_TEXT};text-align:center;margin:4px 0 16px;">
                {gs_meaning} · {gs_key_use}
            </p>
            <div style="display:flex;justify-content:space-around;flex-wrap:wrap;gap:12px;">
                <div style="text-align:center;">
                    <div style="color:{_HAW_TEAL};font-size:0.85em;">
                        {auto_cn("守護星屋", "Guardian House")}
                    </div>
                    <div style="color:{_HAW_HEADER};font-size:1.4em;font-weight:bold;">
                        {gh.get("hawaiian","—")}
                    </div>
                    <div style="color:{_HAW_TEXT};font-size:0.85em;">
                        {gh.get("english","—")}
                    </div>
                </div>
                <div style="text-align:center;">
                    <div style="color:{_HAW_TEAL};font-size:0.85em;">
                        {auto_cn("方位角", "Azimuth")}
                    </div>
                    <div style="color:{_HAW_HEADER};font-size:1.4em;font-weight:bold;">
                        {gh.get("direction_deg",0):.1f}°
                    </div>
                </div>
                <div style="text-align:center;">
                    <div style="color:{_HAW_TEAL};font-size:0.85em;">
                        {auto_cn("象限", "Quadrant")}
                    </div>
                    <div style="color:{_HAW_HEADER};font-size:1.4em;font-weight:bold;">
                        {gh.get("quadrant","—")}
                    </div>
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Interpretation
    quadrant = gh.get("quadrant", "")
    interpretations_zh = {
        "Koʻolau": (
            "Koʻolau（東北）象限的守護者——你生於東北信風吹拂之時。"
            "Koʻolau 風帶來清新、生機與探索精神。你的本質如朝陽般充滿活力，"
            "引領他人走向新的旅程。Hōkūleʻa 在東北方升起，賜予你開拓前路的能量。"
        ),
        "Malanai": (
            "Malanai（東南）象限的守護者——你生於溫和東南貿易風之時。"
            "Malanai 風溫柔而持續，象徵恆心與細膩。"
            "Hōkūleʻa 在東南方為你照路，帶來深思熟慮與向南探索新世界的勇氣。"
        ),
        "Kona": (
            "Kona（西南）象限的守護者——你生於 Kona 暖風之時。"
            "Kona 風來自西南，帶來溫暖、滋養與創造力。"
            "Hōkūleʻa 在西南落下，象徵智慧的沉澱與對傳統的珍視。"
        ),
        "Hoʻolua": (
            "Hoʻolua（西北）象限的守護者——你生於西北風暴之時。"
            "Hoʻolua 風強勁而不可預測，象徵力量與轉化。"
            "Hōkūleʻa 在西北方指引，賜予你面對挑戰的韌性與深遠的遠見。"
        ),
    }
    interpretations_en = {
        "Koʻolau": (
            "You are born under the Koʻolau (Northeast) quadrant — the refreshing "
            "northeast trade winds. Koʻolau brings vitality, discovery, and the "
            "pioneering spirit. With Hōkūleʻa rising in the northeast, you carry "
            "the energy to chart new paths for others."
        ),
        "Malanai": (
            "You are born under the Malanai (Southeast) quadrant — the gentle "
            "southeast trade winds. Malanai brings steadiness and subtlety. "
            "Hōkūleʻa illuminates your way from the southeast, granting deep "
            "reflection and courage to explore new southern worlds."
        ),
        "Kona": (
            "You are born under the Kona (Southwest) quadrant — the warm Kona "
            "winds from the southwest. Kona brings warmth, nurturing, and creativity. "
            "Hōkūleʻa setting in the southwest symbolises the distillation of "
            "wisdom and deep respect for tradition."
        ),
        "Hoʻolua": (
            "You are born under the Hoʻolua (Northwest) quadrant — the powerful "
            "northwest storms. Hoʻolua brings strength and transformation. "
            "Hōkūleʻa guides from the northwest, granting resilience in challenges "
            "and far-reaching foresight."
        ),
    }

    interp = auto_cn(
        interpretations_zh.get(quadrant, ""),
        interpretations_en.get(quadrant, ""),
    )
    if interp:
        _card(
            auto_cn("守護星屋解讀", "Guardian House Reading"),
            interp,
            _HAW_TEAL,
        )

    # Season at birth
    season_info = result.season_info
    _card(
        auto_cn(f"出生季節：{result.season}", f"Birth Season: {result.season}"),
        auto_cn(season_info.get("description_cn", ""), season_info.get("description", "")),
        season_info.get("color", _HAW_BORDER),
    )

    # Hōkūleʻa position at birth
    alt = gs.get("altitude", 0.0)
    az = gs.get("azimuth", 0.0)
    st.markdown(
        f"**{auto_cn('出生時 Hōkūleʻa 的位置', 'Hōkūleʻa Position at Birth')}:** "
        f"{auto_cn('高度', 'Alt')} {alt:.1f}°, "
        f"{auto_cn('方位角', 'Az')} {az:.1f}°"
    )


# ============================================================
# Tab 5 — Today's Star Guidance
# ============================================================

def _render_guidance_tab(result: "PolynesianResult") -> None:
    st.markdown(
        f"<h4 style='color:{_HAW_TEAL};'>"
        + auto_cn("今日星辰指引", "Today's Star Guidance")
        + "</h4>",
        unsafe_allow_html=True,
    )

    date_str = f"{result.year}-{result.month:02d}-{result.day:02d} {result.hour:02d}:{result.minute:02d}"
    location_suffix = f"  ·  {result.location_name}" if result.location_name else ""
    st.caption(auto_cn(f"計算時刻：{date_str}{location_suffix}", f"Chart time: {date_str}{location_suffix}"))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            auto_cn("升起中的星", "Rising Stars"),
            len(result.rising_stars),
        )
    with col2:
        st.metric(
            auto_cn("落下中的星", "Setting Stars"),
            len(result.setting_stars),
        )
    with col3:
        st.metric(
            auto_cn("中天的星", "Culminating Stars"),
            len(result.culminating_stars),
        )

    def _star_block(stars: list, title: str, color: str) -> None:
        if not stars:
            return
        st.markdown(
            f"<h5 style='color:{color};margin-top:14px;'>{title}</h5>",
            unsafe_allow_html=True,
        )
        for sp in stars:
            st.markdown(
                f"- **{sp['hawaiian_name']}** ({sp['western_name']}) — "
                f"{auto_cn(sp['meaning_cn'], sp['meaning'])} · "
                f"Az {sp['azimuth']:.1f}° · {sp['compass_house'].get('hawaiian','—')}",
            )

    _star_block(
        result.rising_stars,
        auto_cn("⬆ 正在升起的星辰", "⬆ Rising Stars"),
        _HAW_TEAL,
    )
    _star_block(
        result.culminating_stars,
        auto_cn("✦ 正在中天的星辰", "✦ Culminating Stars"),
        _HAW_BORDER,
    )
    _star_block(
        result.setting_stars,
        auto_cn("⬇ 正在落下的星辰", "⬇ Setting Stars"),
        _HAW_OCEAN,
    )

    # All visible stars
    st.markdown("---")
    st.markdown(
        f"<h5 style='color:{_HAW_TEXT};'>"
        + auto_cn("所有可見星辰", "All Visible Stars")
        + "</h5>",
        unsafe_allow_html=True,
    )
    import pandas as pd

    rows = []
    for sp in result.star_positions:
        if sp["status"] == "below":
            continue
        rows.append({
            auto_cn("夏威夷名稱", "Hawaiian Name"): sp["hawaiian_name"],
            auto_cn("西方名稱", "Western Name"): sp["western_name"],
            auto_cn("高度", "Altitude"): f"{sp['altitude']:.1f}°",
            auto_cn("方位角", "Azimuth"): f"{sp['azimuth']:.1f}°",
            auto_cn("星屋", "House"): sp["compass_house"].get("hawaiian", "—"),
            auto_cn("狀態", "Status"): sp["status"],
        })

    if rows:
        st.dataframe(pd.DataFrame(rows), width=850)
    else:
        st.info(auto_cn("目前無可見星辰。", "No visible stars at this time."))


# ============================================================
# Main entry point
# ============================================================

def render_streamlit(result: "PolynesianResult") -> None:
    """Render the full Polynesian / Hawaiian star lore UI."""
    from .constants import CULTURAL_INTRO, CULTURAL_INTRO_CN

    # ── Header ──────────────────────────────────────────────
    st.markdown(
        f"""<div style="
            background:linear-gradient(135deg,{_HAW_BG},{_HAW_CARD});
            border:2px solid {_HAW_BORDER};border-radius:12px;
            padding:20px 28px;margin-bottom:16px;text-align:center;">
            <h2 style="color:{_HAW_HEADER};margin:0 0 6px;">
                🌺 {auto_cn(
                    "玻里尼西亞 / 夏威夷星辰知識",
                    "Polynesian / Hawaiian Star Lore"
                )}
            </h2>
            <p style="color:{_HAW_TEAL};margin:0;font-size:1em;">
                {auto_cn(
                    "32星屋羅盤 · 星辰神話 · 個人守護星",
                    "32-House Star Compass · Star Mythology · Guardian Star"
                )}
            </p>
        </div>""",
        unsafe_allow_html=True,
    )

    # Quick metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            auto_cn("守護星屋", "Guardian House"),
            result.guardian_house.get("hawaiian", "—"),
        )
    with col2:
        st.metric(
            auto_cn("出生季節", "Birth Season"),
            auto_cn(
                result.season_info.get("cn", result.season),
                result.season,
            ),
        )
    with col3:
        st.metric(
            auto_cn("升起星辰", "Rising Stars"),
            len(result.rising_stars),
        )
    with col4:
        st.metric(
            auto_cn("可見星辰", "Visible Stars"),
            sum(1 for s in result.star_positions if s["status"] != "below"),
        )

    # Cultural intro (collapsible)
    with st.expander(
        auto_cn("📖 夏威夷星辰知識簡介", "📖 Introduction to Hawaiian Star Lore"),
        expanded=False,
    ):
        st.markdown(
            auto_cn(CULTURAL_INTRO_CN, CULTURAL_INTRO),
            unsafe_allow_html=False,
        )

    # ── Tabs ────────────────────────────────────────────────
    tab_labels = [
        auto_cn("🧭 星羅盤", "🧭 Star Compass"),
        auto_cn("⭐ 主要星線", "⭐ Star Lines"),
        auto_cn("📖 神話故事", "📖 Mythology"),
        auto_cn("🌟 個人守護星", "🌟 Guardian Star"),
        auto_cn("🌊 今日星指引", "🌊 Today's Guidance"),
    ]
    t1, t2, t3, t4, t5 = st.tabs(tab_labels)

    with t1:
        _render_compass_tab(result)
    with t2:
        _render_star_lines_tab(result)
    with t3:
        _render_mythology_tab(result)
    with t4:
        _render_guardian_tab(result)
    with t5:
        _render_guidance_tab(result)
