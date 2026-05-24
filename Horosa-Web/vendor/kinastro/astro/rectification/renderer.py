"""
astro/rectification/renderer.py — 出生時間校正 Streamlit 前端介面

Birth Chart Rectification — Streamlit UI

美學風格：深色玄秘主題、金色點綴、古典占星印象
Provides a step-by-step wizard:
  Tab 1 — 事件輸入 (Event Input)
  Tab 2 — 校正結果 (Rectification Results)
  Tab 3 — 技術細節 (Technique Details)
  Tab 4 — 校正後圖盤 (Rectified Chart)
"""

from __future__ import annotations

import math
from datetime import datetime, date, time
from typing import Dict, List, Optional

import streamlit as st

from .calculator import (
    LifeEvent,
    CandidateResult,
    EventMatch,
    TechniqueHit,
    run_rectification,
    _sign_name,
    _jd_to_year,
    _normalize,
    _ZODIAC_SIGNS,
    _SIGN_CHINESE,
)
from .constants import (
    TECHNIQUE_INFO,
    TECHNIQUE_WEIGHTS,
    EVENT_CATEGORIES,
    AI_EVENT_SUGGESTIONS,
    RECTIFICATION_HISTORY,
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_LOW,
    RECT_GOLD,
    RECT_PURPLE,
    RECT_BLUE,
    RECT_TEAL,
    RECT_ORANGE,
    RECT_CRIMSON,
    RECT_BG_DARK,
    RECT_BORDER,
    DEFAULT_SEARCH_WINDOW_MINUTES,
)
from astro.i18n import auto_cn, get_ui_lang, t

# ============================================================
# CSS
# ============================================================

RECT_CSS = """
<style>
/* ── Rectification Module Styles ── */
.rect-hero {
    background: linear-gradient(135deg,
        rgba(10,5,35,0.98) 0%,
        rgba(25,10,55,0.96) 45%,
        rgba(8,20,45,0.98) 100%);
    border: 1px solid rgba(167,139,250,0.28);
    border-radius: 18px;
    padding: 2rem 2.5rem 1.6rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 48px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.04);
}
.rect-hero::before {
    content: "✦ ✧ ✦ ✧ ✦";
    position: absolute; top: 12px; right: 20px;
    color: rgba(234,179,8,0.22); font-size: 0.85rem; letter-spacing: 4px;
}
.rect-hero-title {
    font-family: 'Cinzel', 'Noto Serif TC', serif;
    font-size: clamp(1.4rem, 3vw, 2rem);
    font-weight: 700;
    background: linear-gradient(135deg, #EAB308 0%, #A78BFA 60%, #7DD3FC 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.35rem; letter-spacing: 0.06em;
}
.rect-hero-sub {
    color: rgba(200,185,255,0.7); font-size: 0.88rem; letter-spacing: 0.07em;
}
.rect-step-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(167,139,250,0.18) 0%, rgba(234,179,8,0.1) 100%);
    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 20px; padding: 0.15rem 0.8rem;
    font-size: 0.78rem; color: #A78BFA;
    font-weight: 600; letter-spacing: 0.06em; margin-bottom: 0.6rem;
}
.rect-candidate-card {
    background: linear-gradient(135deg, rgba(15,10,40,0.95) 0%, rgba(30,15,55,0.92) 100%);
    border: 1px solid rgba(167,139,250,0.22);
    border-radius: 14px; padding: 1.2rem 1.5rem; margin-bottom: 1rem;
    position: relative; overflow: hidden;
    transition: border-color 0.2s;
}
.rect-candidate-card.top {
    border-color: rgba(234,179,8,0.45);
    box-shadow: 0 0 18px rgba(234,179,8,0.08);
}
.rect-candidate-rank {
    font-family: 'Cinzel', serif; font-size: 1.1rem; font-weight: 700;
    color: #EAB308; margin-right: 0.5rem;
}
.rect-candidate-time {
    font-size: 1.3rem; font-weight: 700; color: #E0E0FF;
    font-family: 'Cinzel', monospace;
}
.rect-confidence-bar-bg {
    background: rgba(255,255,255,0.06); border-radius: 99px;
    height: 8px; width: 100%; margin: 0.5rem 0;
}
.rect-confidence-bar-fill {
    height: 8px; border-radius: 99px;
    background: linear-gradient(90deg, #A78BFA 0%, #EAB308 100%);
    transition: width 0.4s ease;
}
.rect-event-hit {
    background: rgba(167,139,250,0.08);
    border-left: 3px solid #A78BFA;
    border-radius: 0 8px 8px 0;
    padding: 0.4rem 0.8rem; margin: 0.3rem 0;
    font-size: 0.84rem; color: rgba(220,210,255,0.85);
}
.rect-technique-tag {
    display: inline-block;
    border-radius: 12px; padding: 0.1rem 0.6rem;
    font-size: 0.72rem; font-weight: 600; margin-right: 0.3rem;
}
.rect-info-card {
    background: rgba(20,15,45,0.7);
    border: 1px solid rgba(167,139,250,0.18);
    border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.8rem;
}
.rect-ai-suggestion {
    background: rgba(59,130,246,0.08);
    border: 1px dashed rgba(59,130,246,0.35);
    border-radius: 10px; padding: 0.7rem 1rem;
    font-size: 0.85rem; color: rgba(147,197,253,0.9);
    margin: 0.3rem 0;
}
.rect-history-box {
    background: rgba(10,8,30,0.8);
    border: 1px solid rgba(167,139,250,0.15);
    border-radius: 12px; padding: 1.2rem 1.5rem;
    font-size: 0.9rem; line-height: 1.75;
    color: rgba(200,195,240,0.88);
}
.rect-export-btn {
    background: linear-gradient(135deg, #EAB308 0%, #A78BFA 100%);
    border: none; border-radius: 8px;
    padding: 0.5rem 1.2rem; color: #0a0820;
    font-weight: 700; cursor: pointer; font-size: 0.9rem;
}
</style>
"""

# ============================================================
# Helpers
# ============================================================

_TECH_COLORS = {
    "primary_direction": RECT_BLUE,
    "solar_arc": RECT_GOLD,
    "secondary_progression": RECT_PURPLE,
    "profection": RECT_TEAL,
    "zodiacal_releasing": RECT_TEAL,
    "transit_outer": RECT_ORANGE,
    "transit_inner": RECT_ORANGE,
}

_TECH_LABELS_ZH = {
    "primary_direction": "初級方向",
    "solar_arc": "太陽弧",
    "secondary_progression": "次進法",
    "profection": "小限",
    "zodiacal_releasing": "黃道釋放",
    "transit_outer": "過境",
    "transit_inner": "過境",
}

_TECH_LABELS_EN = {
    "primary_direction": "Prim.Dir",
    "solar_arc": "Sol.Arc",
    "secondary_progression": "Sec.Prog",
    "profection": "Profection",
    "zodiacal_releasing": "ZR",
    "transit_outer": "Transit",
    "transit_inner": "Transit",
}


def _lang() -> str:
    return get_ui_lang()


def _is_zh() -> bool:
    return _lang() in ("zh", "zh_cn")


def _confidence_color(pct: float) -> str:
    if pct >= CONFIDENCE_HIGH:
        return "#22c55e"   # green
    if pct >= CONFIDENCE_MEDIUM:
        return RECT_GOLD
    return RECT_ORANGE


def _confidence_label(pct: float) -> str:
    if _is_zh():
        if pct >= CONFIDENCE_HIGH:
            return auto_cn("高可信度")
        if pct >= CONFIDENCE_MEDIUM:
            return auto_cn("中等可信度")
        return auto_cn("低可信度")
    else:
        if pct >= CONFIDENCE_HIGH:
            return "High Confidence"
        if pct >= CONFIDENCE_MEDIUM:
            return "Moderate Confidence"
        return "Low Confidence"


def _sign_display(sign: str) -> str:
    if _is_zh():
        return auto_cn(_SIGN_CHINESE.get(sign, sign))
    return sign


# ============================================================
# Sub-renderers
# ============================================================

def _render_hero() -> None:
    """Render the hero banner for the rectification page."""
    st.markdown(RECT_CSS, unsafe_allow_html=True)
    if _is_zh():
        title = auto_cn("🔮 出生時間校正 Birth Chart Rectification")
        sub = auto_cn("多技術古典占星校正引擎 · 初級方向 · 太陽弧 · 次進法 · 流年小限 · 黃道釋放")
    else:
        title = "🔮 Birth Chart Rectification"
        sub = "Multi-technique classical engine · Primary Directions · Solar Arcs · Progressions · Profections · ZR"

    st.markdown(
        f'<div class="rect-hero">'
        f'<div class="rect-hero-title">{title}</div>'
        f'<div class="rect-hero-sub">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_event_input_tab() -> List[LifeEvent]:
    """Render the event input wizard step.

    Returns:
        List of LifeEvent objects entered by the user.
    """
    if _is_zh():
        st.markdown(
            '<div class="rect-step-badge">' + auto_cn("步驟 1 — 輸入重大生命事件") + '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(auto_cn(
            "請輸入您人生中的重大事件（至少 3–5 個），系統將以多種古典技術匹配最可能的出生時間。"
        ))
    else:
        st.markdown('<div class="rect-step-badge">Step 1 — Enter Major Life Events</div>',
                    unsafe_allow_html=True)
        st.markdown(
            "Enter at least 3–5 major life events. "
            "The engine will match them against six classical techniques to find the best birth time."
        )

    # Event counter in session state
    if "rect_events" not in st.session_state:
        st.session_state["rect_events"] = [
            {"date": "", "desc": "", "category": "other"},
        ]

    events_raw = st.session_state["rect_events"]

    # Add / Remove buttons
    col_add, col_clr = st.columns([1, 1])
    with col_add:
        if st.button(
            auto_cn("➕ 新增事件") if _is_zh() else "➕ Add Event",
            key="_rect_add_event",
        ):
            events_raw.append({"date": "", "desc": "", "category": "other"})
            st.rerun()
    with col_clr:
        if st.button(
            auto_cn("🗑 清除全部") if _is_zh() else "🗑 Clear All",
            key="_rect_clear_events",
            type="secondary",
        ):
            st.session_state["rect_events"] = [{"date": "", "desc": "", "category": "other"}]
            st.rerun()

    st.divider()

    # Category options
    cat_options = {k: f"{v['emoji']} {auto_cn(v['zh']) if _is_zh() else v['en']}"
                   for k, v in EVENT_CATEGORIES.items()}

    to_delete: List[int] = []
    for i, ev in enumerate(events_raw):
        with st.container():
            c1, c2, c3, c4 = st.columns([2, 3, 2, 1])
            with c1:
                date_val = ev.get("date", "")
                new_date = st.text_input(
                    auto_cn("日期 (YYYY-MM-DD)") if _is_zh() else "Date (YYYY-MM-DD)",
                    value=date_val,
                    key=f"_rect_ev_date_{i}",
                    placeholder="2015-03-12",
                )
                events_raw[i]["date"] = new_date
            with c2:
                new_desc = st.text_input(
                    auto_cn("事件描述") if _is_zh() else "Event Description",
                    value=ev.get("desc", ""),
                    key=f"_rect_ev_desc_{i}",
                    placeholder=auto_cn("結婚 / 升職 / 父親過世") if _is_zh() else "Marriage / Promotion / Death of father",
                )
                events_raw[i]["desc"] = new_desc
            with c3:
                cur_cat = ev.get("category", "other")
                cat_keys = list(cat_options.keys())
                cur_idx = cat_keys.index(cur_cat) if cur_cat in cat_keys else 0
                new_cat = st.selectbox(
                    auto_cn("類別") if _is_zh() else "Category",
                    options=cat_keys,
                    index=cur_idx,
                    format_func=lambda k: cat_options[k],
                    key=f"_rect_ev_cat_{i}",
                )
                events_raw[i]["category"] = new_cat
            with c4:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✕", key=f"_rect_del_ev_{i}", type="secondary"):
                    to_delete.append(i)

    for idx in sorted(to_delete, reverse=True):
        if len(events_raw) > 1:
            events_raw.pop(idx)
    if to_delete:
        st.rerun()

    # AI-assisted suggestions
    st.divider()
    if _is_zh():
        st.markdown(f"**{auto_cn('💡 AI 建議補充的事件類型：')}**")
    else:
        st.markdown("**💡 AI-Suggested Event Types:**")

    for suggestion in AI_EVENT_SUGGESTIONS:
        text = auto_cn(suggestion["zh"]) if _is_zh() else suggestion["en"]
        st.markdown(f'<div class="rect-ai-suggestion">{text}</div>', unsafe_allow_html=True)

    # Build LifeEvent list
    parsed_events: List[LifeEvent] = []
    for ev in events_raw:
        d = ev.get("date", "").strip()
        desc = ev.get("desc", "").strip()
        cat = ev.get("category", "other")
        if d and desc:
            try:
                le = LifeEvent(date_str=d, description=desc, category=cat)
                if le.year > 0:
                    parsed_events.append(le)
            except Exception:
                pass

    return parsed_events


def _truncate(text: str, max_len: int = 28) -> str:
    """Truncate text with ellipsis if it exceeds max_len."""
    return text[:max_len] + "…" if len(text) > max_len else text


def _tech_short_label(info: Dict[str, str]) -> str:
    """Return a short display label for a technique info dict."""
    if _is_zh():
        return auto_cn(info["zh_name"].split()[0])
    # English: extract first phrase before first colon or em-dash
    en = info.get("en_desc", "")
    for sep in (":", "—", " -"):
        if sep in en:
            return _truncate(en.split(sep)[0].strip())
    return _truncate(en)


def _render_technique_selector() -> List[str]:
    """Render technique toggle checkboxes and return selected technique keys."""
    if _is_zh():
        st.subheader(auto_cn("🔧 選擇校正技術"))
    else:
        st.subheader("🔧 Select Rectification Techniques")

    selected: List[str] = []
    cols = st.columns(3)
    items = list(TECHNIQUE_INFO.items())
    for i, (key, info) in enumerate(items):
        with cols[i % 3]:
            label_short = _tech_short_label(info)
            weight = info["weight_label"]
            enabled = st.checkbox(
                f"{label_short} ({weight})",
                value=True,
                key=f"_rect_tech_{key}",
                help=auto_cn(info["zh_desc"]) if _is_zh() else info["en_desc"],
            )
            if enabled:
                # Map technique info keys to TECHNIQUE_WEIGHTS keys
                if key == "transit":
                    selected.append("transit_outer")
                else:
                    selected.append(key)
    return selected


def _render_search_settings() -> tuple:
    """Render search window / step settings.

    Returns:
        (search_window_minutes, step_minutes)
    """
    if _is_zh():
        st.subheader(auto_cn("⏱ 搜尋設定"))
    else:
        st.subheader("⏱ Search Settings")

    col1, col2 = st.columns(2)
    with col1:
        window = st.select_slider(
            auto_cn("搜尋時間窗口") if _is_zh() else "Search Window",
            options=[30, 60, 90, 120, 180, 240],
            value=DEFAULT_SEARCH_WINDOW_MINUTES,
            format_func=lambda v: f"±{v} " + (auto_cn("分鐘") if _is_zh() else "min"),
            key="_rect_window",
        )
    with col2:
        step = st.select_slider(
            auto_cn("時間步長") if _is_zh() else "Time Step",
            options=[2, 4, 5, 10, 15],
            value=4,
            format_func=lambda v: f"{v} " + (auto_cn("分鐘") if _is_zh() else "min"),
            key="_rect_step",
        )

    n_candidates = (window // step) * 2 + 1
    if _is_zh():
        st.caption(auto_cn(f"共將計算 {n_candidates} 個候選時間"))
    else:
        st.caption(f"Will evaluate {n_candidates} candidate birth times")

    return window, step


def _render_candidate_card(res: CandidateResult, rank: int, is_zh: bool) -> None:
    """Render a result card for a single candidate birth time."""
    is_top = rank == 1
    card_class = "rect-candidate-card top" if is_top else "rect-candidate-card"

    conf_color = _confidence_color(res.confidence)
    conf_label = _confidence_label(res.confidence)
    asc_disp = _sign_display(res.asc_sign)
    mc_disp = _sign_display(res.mc_sign)

    rank_label = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")

    asc_deg = int(res.asc_lon % 30)
    mc_deg = int(res.mc_lon % 30)

    st.markdown(
        f'<div class="{card_class}">'
        f'<span class="rect-candidate-rank">{rank_label}</span>'
        f'<span class="rect-candidate-time">{res.hour:02d}:{res.minute:02d}</span>'
        f'&nbsp;&nbsp;<span style="color:{conf_color};font-weight:600;">'
        f'{res.confidence:.0f}% — {conf_label}</span>'
        f'<div style="margin-top:0.6rem;color:rgba(180,170,220,0.8);font-size:0.85rem;">'
        f'ASC: <b style="color:#EAB308">{asc_disp} {asc_deg}°</b> &nbsp;|&nbsp; '
        f'MC: <b style="color:#EAB308">{mc_disp} {mc_deg}°</b>'
        f'</div>'
        f'<div class="rect-confidence-bar-bg">'
        f'<div class="rect-confidence-bar-fill" style="width:{res.confidence:.0f}%;"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Per-technique score summary
    if res.technique_scores:
        score_html = '<div style="margin:0.4rem 0;">'
        for tkey, tscore in sorted(res.technique_scores.items(),
                                    key=lambda x: -x[1]):
            if tscore <= 0:
                continue
            color = _TECH_COLORS.get(tkey, RECT_GOLD)
            label = _TECH_LABELS_ZH.get(tkey, tkey) if is_zh else _TECH_LABELS_EN.get(tkey, tkey)
            label = auto_cn(label) if is_zh else label
            score_html += (
                f'<span class="rect-technique-tag" '
                f'style="background:rgba(0,0,0,0.3);border:1px solid {color}40;color:{color};">'
                f'{label} {tscore:.1f}'
                f'</span>'
            )
        score_html += '</div>'
        st.markdown(score_html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Event matches in expander
    if res.event_matches:
        matched = [em for em in res.event_matches if em.hits]
        if matched:
            expander_label = (
                auto_cn(f"📋 查看 {len(matched)} 個事件匹配詳情") if is_zh
                else f"📋 {len(matched)} Event Matches"
            )
            with st.expander(expander_label, expanded=(rank == 1)):
                for em in matched:
                    ev_label = f"**{em.event.date_str}** — {em.event.description}"
                    cat_info = EVENT_CATEGORIES.get(em.event.category, {})
                    emoji = cat_info.get("emoji", "⭐")
                    st.markdown(f"{emoji} {ev_label} &nbsp; (score: {em.total_score:.2f})")
                    for hit in sorted(em.hits, key=lambda h: -h.score)[:5]:
                        color = hit.color
                        tech_label = (
                            _TECH_LABELS_ZH.get(hit.technique, hit.technique) if is_zh
                            else _TECH_LABELS_EN.get(hit.technique, hit.technique)
                        )
                        desc = (hit.description_zh if is_zh else hit.description_en)
                        st.markdown(
                            f'<div class="rect-event-hit">'
                            f'<span class="rect-technique-tag" '
                            f'style="background:{color}22;border:1px solid {color}55;color:{color};">'
                            f'{auto_cn(tech_label) if is_zh else tech_label}</span> '
                            f'{auto_cn(desc) if is_zh else desc} '
                            f'<span style="color:{RECT_GOLD};font-size:0.78rem;">'
                            f'+{hit.score:.2f}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )


def _render_results_tab(
    results: List[CandidateResult],
    birth_date: date,
    parsed_events: List[LifeEvent],
) -> Optional[CandidateResult]:
    """Render the rectification results tab.

    Returns:
        The user-selected CandidateResult for export, or None.
    """
    is_zh = _is_zh()

    if not results:
        if is_zh:
            st.warning(auto_cn("尚未執行校正計算，請先在「事件輸入」標籤填寫事件並點擊「開始校正」。"))
        else:
            st.warning("No results yet. Fill in events and click 'Start Rectification' first.")
        return None

    if is_zh:
        st.markdown(
            f'<div class="rect-step-badge">'
            + auto_cn(f"找到 {len(results)} 個最佳候選出生時間")
            + '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(auto_cn(
            "以下結果按多技術加權得分排序，排名第一者最符合您的生命事件時間軸。"
            "可信度越高，表示越多技術在該候選時間點附近有激活。"
        ))
    else:
        st.markdown(
            f'<div class="rect-step-badge">'
            f'Top {len(results)} Candidate Birth Times Ranked</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            "Results are sorted by multi-technique weighted score. "
            "Higher confidence means more techniques activate near that birth time."
        )

    for i, res in enumerate(results):
        _render_candidate_card(res, i + 1, is_zh)

    # Export / Use section
    st.divider()
    if is_zh:
        st.subheader(auto_cn("📤 使用校正後時間"))
    else:
        st.subheader("📤 Use Rectified Time")

    opts = [
        f"{r.hour:02d}:{r.minute:02d}  (ASC {r.asc_sign} {int(r.asc_lon%30)}°, "
        f"{r.confidence:.0f}%)"
        for r in results
    ]
    chosen_idx = st.selectbox(
        auto_cn("選擇要使用的校正時間") if is_zh else "Select rectified time to use",
        options=range(len(opts)),
        format_func=lambda i: opts[i],
        key="_rect_chosen_time",
    )
    chosen = results[chosen_idx]

    if st.button(
        auto_cn("✅ 將此時間用於其他模組") if is_zh else "✅ Use This Time in Other Modules",
        key="_rect_export_btn",
        type="primary",
    ):
        st.session_state["_rect_exported_hour"] = chosen.hour
        st.session_state["_rect_exported_minute"] = chosen.minute
        if is_zh:
            st.success(auto_cn(
                f"已設定校正出生時間為 {chosen.hour:02d}:{chosen.minute:02d}。"
                "請在左側側邊欄更新出生時間，然後重新計算星盤。"
            ))
        else:
            st.success(
                f"Rectified birth time set to {chosen.hour:02d}:{chosen.minute:02d}. "
                "Update the birth time in the sidebar and recompute."
            )

    return chosen


def _render_technique_details_tab() -> None:
    """Render educational content about each rectification technique."""
    is_zh = _is_zh()

    if is_zh:
        st.markdown(
            '<div class="rect-step-badge">' + auto_cn("技術說明與古典文獻") + '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="rect-step-badge">Technique Details & Classical References</div>',
            unsafe_allow_html=True,
        )

    # Historical intro
    if is_zh:
        st.markdown(auto_cn("### 📜 出生時間校正的歷史"))
        st.markdown(
            '<div class="rect-history-box">' + auto_cn(RECTIFICATION_HISTORY["zh"]) + '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown("### 📜 History of Rectification")
        st.markdown(
            '<div class="rect-history-box">' + RECTIFICATION_HISTORY["en"] + '</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Individual technique cards
    for key, info in TECHNIQUE_INFO.items():
        name = auto_cn(info["zh_name"]) if is_zh else info["zh_name"]
        desc = auto_cn(info["zh_desc"]) if is_zh else info["en_desc"]
        weight = info["weight_label"]
        color = _TECH_COLORS.get(key, RECT_GOLD)

        with st.expander(f"**{name}** — {auto_cn('權重') if is_zh else 'Weight'} {weight}",
                         expanded=False):
            st.markdown(
                f'<div class="rect-info-card">'
                f'<div style="color:{color};font-weight:600;margin-bottom:0.5rem;">'
                f'{name}</div>'
                f'<div style="color:rgba(200,195,240,0.85);font-size:0.9rem;line-height:1.7;">'
                f'{desc}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Scoring formula
    st.divider()
    if is_zh:
        st.markdown(auto_cn("### 📊 評分算法"))
        st.markdown(auto_cn(
            "**總分 = Σ (技術命中得分 × 技術權重 × 角宮加成 × 日月加成 × 精確度因子)**\n\n"
            "- 角宮加成：涉及 ASC/MC/DSC/IC 時乘以 **2.0×**\n"
            "- 日月加成：涉及太陽或月亮時乘以 **1.5×**\n"
            "- 精確度因子：誤差越小得分越高，超出容許度則不計分\n"
            "- 可信度 = 候選時間得分 ÷ 最高得分 × 100%"
        ))
    else:
        st.markdown("### 📊 Scoring Algorithm")
        st.markdown(
            "**Total Score = Σ (technique hit score × technique weight × angle bonus × luminary bonus × precision factor)**\n\n"
            "- Angle bonus: ×**2.0** when ASC/MC/DSC/IC is involved\n"
            "- Luminary bonus: ×**1.5** when Sun or Moon is involved\n"
            "- Precision factor: higher score the closer to exact; zero outside orb\n"
            "- Confidence = candidate score ÷ top score × 100%"
        )


def _render_rectified_chart_tab(
    chosen: Optional[CandidateResult],
    birth_date: date,
    lat: float,
    lon: float,
    tz: float,
) -> None:
    """Render a mini natal chart for the chosen candidate birth time."""
    is_zh = _is_zh()

    if chosen is None:
        if is_zh:
            st.info(auto_cn("請先在「校正結果」標籤選擇並確認一個候選出生時間。"))
        else:
            st.info("Please select a candidate time in the 'Results' tab first.")
        return

    if is_zh:
        st.markdown(
            '<div class="rect-step-badge">' + auto_cn("校正後星盤概覽") + '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(auto_cn(f"**候選出生時間：{chosen.hour:02d}:{chosen.minute:02d}**"))
    else:
        st.markdown('<div class="rect-step-badge">Rectified Chart Overview</div>',
                    unsafe_allow_html=True)
        st.markdown(f"**Candidate birth time: {chosen.hour:02d}:{chosen.minute:02d}**")

    # Planet positions table
    col1, col2 = st.columns(2)
    with col1:
        if is_zh:
            st.markdown(auto_cn("#### 🌟 行星位置"))
        else:
            st.markdown("#### 🌟 Planet Positions")

        rows = []
        from .constants import PLANET_CHINESE as _PC
        for pname, plon in chosen.planet_positions.items():
            sign = _sign_name(plon)
            deg = int(plon % 30)
            mins = int((plon % 30 - deg) * 60)
            short = pname.split()[0]
            glyph = pname.split()[-1] if len(pname.split()) > 1 else ""
            if is_zh:
                cn_name = _PC.get(short, short)
                rows.append({
                    auto_cn("行星"): f"{glyph} {auto_cn(cn_name)}".strip(),
                    auto_cn("位置"): auto_cn(f"{_SIGN_CHINESE.get(sign, sign)} {deg}°{mins:02d}'"),
                })
            else:
                rows.append({
                    "Planet": pname,
                    "Position": f"{sign} {deg}°{mins:02d}'",
                })

        if rows:
            st.dataframe(rows, width="stretch")

    with col2:
        if is_zh:
            st.markdown(auto_cn("#### 🏠 宮位軸"))
        else:
            st.markdown("#### 🏠 Chart Angles")

        angles_data = [
            {
                (auto_cn("軸點") if is_zh else "Angle"): auto_cn("上升點 ASC") if is_zh else "ASC",
                (auto_cn("位置") if is_zh else "Position"): (
                    auto_cn(f"{_SIGN_CHINESE.get(chosen.asc_sign, chosen.asc_sign)} {int(chosen.asc_lon % 30)}°")
                    if is_zh else f"{chosen.asc_sign} {int(chosen.asc_lon % 30)}°"
                ),
            },
            {
                (auto_cn("軸點") if is_zh else "Angle"): auto_cn("中天 MC") if is_zh else "MC",
                (auto_cn("位置") if is_zh else "Position"): (
                    auto_cn(f"{_SIGN_CHINESE.get(chosen.mc_sign, chosen.mc_sign)} {int(chosen.mc_lon % 30)}°")
                    if is_zh else f"{chosen.mc_sign} {int(chosen.mc_lon % 30)}°"
                ),
            },
        ]
        st.dataframe(angles_data, width="stretch")

        if is_zh:
            st.info(auto_cn(
                "💡 若要查看完整校正後星盤，請在左側側邊欄將出生時間更新為上方顯示的校正時間，"
                "然後選擇西洋占星或其他體系重新計算。"
            ))
        else:
            st.info(
                "💡 To view the full rectified chart, update the birth time in the sidebar "
                "to the rectified time above, then recompute using the Western or other system tabs."
            )

    # Quick technique score chart
    st.divider()
    try:
        import plotly.graph_objects as go

        tech_labels: List[str] = []
        tech_scores: List[float] = []
        tech_colors: List[str] = []

        for tkey, tscore in sorted(chosen.technique_scores.items(),
                                    key=lambda x: -x[1]):
            if tscore > 0:
                info = TECHNIQUE_INFO.get(tkey)
                if info:
                    raw_label = info["zh_name"].split()[0] if is_zh else tkey
                else:
                    raw_label = _TECH_LABELS_ZH.get(tkey, tkey) if is_zh else _TECH_LABELS_EN.get(tkey, tkey)
                label = auto_cn(raw_label) if is_zh else raw_label
                tech_labels.append(label)
                tech_scores.append(tscore)
                tech_colors.append(_TECH_COLORS.get(tkey, RECT_GOLD))

        if tech_labels:
            fig = go.Figure(go.Bar(
                x=tech_labels,
                y=tech_scores,
                marker_color=tech_colors,
                marker_line_color="rgba(255,255,255,0.1)",
                marker_line_width=1,
                text=[f"{s:.1f}" for s in tech_scores],
                textposition="outside",
                textfont_color="#E0E0FF",
            ))
            fig.update_layout(
                title={
                    "text": auto_cn("各技術得分貢獻") if is_zh else "Score Contribution by Technique",
                    "font": {"color": "#E0E0FF", "size": 14},
                },
                paper_bgcolor="rgba(10,8,30,0.0)",
                plot_bgcolor="rgba(10,8,30,0.0)",
                font_color="#E0E0FF",
                height=280,
                margin=dict(t=40, b=20, l=10, r=10),
                xaxis=dict(
                    gridcolor="rgba(255,255,255,0.05)",
                    tickfont_color="#A78BFA",
                ),
                yaxis=dict(
                    gridcolor="rgba(255,255,255,0.06)",
                    tickfont_color="#A78BFA",
                ),
                showlegend=False,
            )
            st.plotly_chart(fig, width="stretch")
    except ImportError:
        pass


# ============================================================
# Main Entry Point
# ============================================================

def render_streamlit(
    default_date: Optional[date] = None,
    default_lat: float = 22.3193,
    default_lon: float = 114.1694,
    default_tz: float = 8.0,
) -> None:
    """Render the full Birth Chart Rectification page.

    Called from app.py when the user selects the rectification system.

    Args:
        default_date: Pre-populated birth date (from sidebar)
        default_lat:  Pre-populated latitude
        default_lon:  Pre-populated longitude
        default_tz:   Pre-populated timezone offset
    """
    is_zh = _is_zh()

    _render_hero()

    # ── Tabs ──────────────────────────────────────────────────
    if is_zh:
        tab_labels = [
            auto_cn("📋 事件輸入"),
            auto_cn("🏆 校正結果"),
            auto_cn("📚 技術說明"),
            auto_cn("🌟 校正後圖盤"),
        ]
    else:
        tab_labels = [
            "📋 Event Input",
            "🏆 Results",
            "📚 Technique Details",
            "🌟 Rectified Chart",
        ]

    tab_events, tab_results, tab_tech, tab_chart = st.tabs(tab_labels)

    # ── Tab 1: Event Input + birth params ────────────────────
    with tab_events:
        # Birth date / time
        if is_zh:
            st.markdown(f'<div class="rect-step-badge">{auto_cn("出生資訊")}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="rect-step-badge">Birth Information</div>',
                        unsafe_allow_html=True)

        col_d, col_t = st.columns(2)
        with col_d:
            birth_date_val = st.date_input(
                auto_cn("出生日期") if is_zh else "Birth Date",
                value=default_date or date(1990, 1, 1),
                key="_rect_birth_date",
            )
        with col_t:
            approx_time_val = st.time_input(
                auto_cn("大約出生時間（或最佳猜測）") if is_zh else "Approximate Birth Time",
                value=time(12, 0),
                key="_rect_approx_time",
            )

        col_la, col_lo, col_tz = st.columns(3)
        with col_la:
            lat_val = st.number_input(
                auto_cn("緯度") if is_zh else "Latitude",
                value=default_lat, format="%.4f",
                min_value=-90.0, max_value=90.0,
                key="_rect_lat",
            )
        with col_lo:
            lon_val = st.number_input(
                auto_cn("經度") if is_zh else "Longitude",
                value=default_lon, format="%.4f",
                min_value=-180.0, max_value=180.0,
                key="_rect_lon",
            )
        with col_tz:
            tz_val = st.number_input(
                auto_cn("時區 (UTC)") if is_zh else "Timezone (UTC)",
                value=default_tz, format="%.1f",
                min_value=-12.0, max_value=14.0, step=0.5,
                key="_rect_tz",
            )

        st.divider()
        parsed_events = _render_event_input_tab()

        st.divider()
        selected_techniques = _render_technique_selector()
        search_window, step_mins = _render_search_settings()

        st.divider()
        # Run button
        run_label = auto_cn("🔮 開始校正計算") if is_zh else "🔮 Start Rectification"
        run_btn = st.button(run_label, key="_rect_run_btn", type="primary", width="stretch")

        if run_btn:
            if len(parsed_events) < 2:
                if is_zh:
                    st.error(auto_cn("請至少輸入 2 個有效的生命事件（含日期和描述）。"))
                else:
                    st.error("Please enter at least 2 valid life events with date and description.")
            else:
                approx_dt = datetime.combine(birth_date_val, approx_time_val)
                progress_bar = st.progress(0)
                spinner_text = auto_cn("正在計算候選時間…") if is_zh else "Computing candidate times…"

                with st.spinner(spinner_text):
                    try:
                        results = run_rectification(
                            approx_birth_datetime=approx_dt,
                            lat=lat_val,
                            lon=lon_val,
                            timezone_offset=tz_val,
                            events=parsed_events,
                            search_window_minutes=search_window,
                            step_minutes=step_mins,
                            techniques=selected_techniques,
                            top_n=5,
                        )
                        st.session_state["_rect_results"] = results
                        st.session_state["_rect_events_parsed"] = parsed_events
                        st.session_state["_rect_birth_date"] = birth_date_val
                        st.session_state["_rect_lat"] = lat_val
                        st.session_state["_rect_lon"] = lon_val
                        st.session_state["_rect_tz"] = tz_val
                    except Exception as exc:
                        st.error(f"{'校正計算出錯：' if is_zh else 'Rectification error: '}{exc}")
                        results = []
                    progress_bar.progress(100)

                if results:
                    if is_zh:
                        st.success(auto_cn(
                            f"✅ 校正完成！找到 {len(results)} 個候選時間，"
                            "請切換至「校正結果」標籤查看。"
                        ))
                    else:
                        st.success(
                            f"✅ Rectification complete! Found {len(results)} candidates. "
                            "Switch to the 'Results' tab to view."
                        )

    # ── Tab 2: Results ────────────────────────────────────────
    with tab_results:
        results_data = st.session_state.get("_rect_results", [])
        bd = st.session_state.get("_rect_birth_date", default_date or date(1990, 1, 1))
        evts = st.session_state.get("_rect_events_parsed", [])
        chosen = _render_results_tab(results_data, bd, evts)
        if chosen:
            st.session_state["_rect_chosen"] = chosen

    # ── Tab 3: Technique Details ──────────────────────────────
    with tab_tech:
        _render_technique_details_tab()

    # ── Tab 4: Rectified Chart ────────────────────────────────
    with tab_chart:
        chosen_stored = st.session_state.get("_rect_chosen")
        _render_rectified_chart_tab(
            chosen_stored,
            birth_date=st.session_state.get("_rect_birth_date", default_date or date(1990, 1, 1)),
            lat=st.session_state.get("_rect_lat", default_lat),
            lon=st.session_state.get("_rect_lon", default_lon),
            tz=st.session_state.get("_rect_tz", default_tz),
        )
