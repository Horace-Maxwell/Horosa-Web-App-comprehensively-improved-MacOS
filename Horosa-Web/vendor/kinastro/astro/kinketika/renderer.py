"""Kinketika Streamlit 介面。"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from astro.i18n import auto_cn

from .engine import KinketikaEngine, SystemKey
from .interpretations import get_cultural_disclaimer, get_system_background
from .ketika_data import ACTIVITY_CATALOGUE, FORTUNE_LABELS
from .wheel_chart import make_wheel


def _system_label(system: SystemKey) -> str:
    if system == "ketika_lima":
        return auto_cn("五時刻（Ketika Lima）", "Ketika Lima (Five Periods)")
    return auto_cn("七星時刻（Bintang Tujuh）", "Bintang Tujuh (Seven-Star Periods)")


def render_streamlit(default_birth_datetime: datetime | None = None) -> dict[str, object]:
    """渲染 Kinketika，並回傳 AI 結構化資料。"""
    engine = KinketikaEngine()

    st.markdown("## 🌙 馬來七星五刻占卜（Kinketika）")
    st.caption(
        auto_cn(
            "Nusantara 傳統時間占卜工具：同時支援 Ketika Lima（五時刻）與 Bintang Tujuh（七星時刻）。",
            "Nusantara time divination tool supporting both Ketika Lima and Bintang Tujuh.",
        )
    )

    st.info(get_cultural_disclaimer("zh" if st.session_state.get("lang", "zh") == "zh" else "en"))

    default_dt = default_birth_datetime or datetime.now()
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        system: SystemKey = st.selectbox(
            auto_cn("占卜系統", "Divination System"),
            options=["ketika_lima", "bintang_tujuh"],
            format_func=_system_label,
            key="kinketika_system",
        )
    with col_b:
        selected_date = st.date_input(auto_cn("日期", "Date"), value=default_dt.date(), key="kinketika_date")
    with col_c:
        selected_time = st.time_input(auto_cn("時間", "Time"), value=default_dt.time(), key="kinketika_time")

    selected_activity = st.selectbox(
        auto_cn("活動規劃器", "Activity Planner"),
        options=list(ACTIVITY_CATALOGUE.keys()),
        format_func=lambda key: ACTIVITY_CATALOGUE[key]["zh"] if st.session_state.get("lang", "zh") == "zh" else ACTIVITY_CATALOGUE[key]["en"],
        key="kinketika_activity",
    )

    moment = datetime.combine(selected_date, selected_time)
    current_period = engine.get_current_period(system, moment)
    periods = engine.get_periods(system)
    stats = engine.get_daily_stats(system)
    plan = engine.get_activity_plan(system, selected_activity)

    st.markdown(f"**{auto_cn('體系背景', 'Background')}**：{get_system_background(system, 'zh' if st.session_state.get('lang', 'zh') == 'zh' else 'en')}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(auto_cn("吉時", "Auspicious"), stats["baik"])
    col2.metric(auto_cn("凶時", "Inauspicious"), stats["nahas"])
    col3.metric(auto_cn("中平", "Neutral"), stats["sederhana"])
    col4.metric(auto_cn("總時段", "Total"), stats["total"])

    current_name = current_period.name_zh if st.session_state.get("lang", "zh") == "zh" else current_period.name_en
    lang_key = "zh" if st.session_state.get("lang", "zh") == "zh" else "en"
    st.success(
        auto_cn(
            f"當前時段：{current_period.emoji} {current_name}（{current_period.time_start}–{current_period.time_end}）｜{FORTUNE_LABELS[current_period.fortune][lang_key]}",
            f"Current period: {current_period.emoji} {current_name} ({current_period.time_start}–{current_period.time_end}) | {FORTUNE_LABELS[current_period.fortune][lang_key]}",
        )
    )

    wheel_title = auto_cn("傳統 manuskript 輪盤", "Traditional manuscript-style wheel")
    st.plotly_chart(
        make_wheel(periods, lang=lang_key, current_index=current_period.index, title=wheel_title),
        width="stretch",
        key="kinketika_wheel",
    )

    st.markdown(f"### {auto_cn('活動規劃結果', 'Activity Planner Result')}")
    st.markdown(f"**{auto_cn('活動', 'Activity')}**：{ACTIVITY_CATALOGUE[selected_activity][lang_key]}")

    good_label = auto_cn("推薦時段", "Recommended periods")
    bad_label = auto_cn("禁忌時段", "Discouraged periods")

    if plan["good"]:
        st.markdown(f"**✅ {good_label}**")
        for p in plan["good"]:
            name = p.name_zh if lang_key == "zh" else p.name_en
            st.write(f"- {p.emoji} {name} ({p.time_start}–{p.time_end})")
    else:
        st.info(auto_cn("此活動無明確推薦時段。", "No clearly recommended periods for this activity."))

    if plan["bad"]:
        st.markdown(f"**❌ {bad_label}**")
        for p in plan["bad"]:
            name = p.name_zh if lang_key == "zh" else p.name_en
            st.write(f"- {p.emoji} {name} ({p.time_start}–{p.time_end})")

    with st.expander(auto_cn("每日吉凶總覽", "Daily Summary"), expanded=True):
        st.write(engine.get_daily_summary_text(system, lang_key))

    return engine.build_structured_report(system, moment, selected_activity)
