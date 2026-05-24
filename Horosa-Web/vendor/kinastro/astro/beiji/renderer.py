# -*- coding: utf-8 -*-
"""
北極神數 — Streamlit 渲染模組
Beiji Shenshu — Streamlit Renderer

提供：
  - 出生資料摘要卡片
  - 多宮條文查詢與展示
  - 大運推算表格
  - 直接條文搜尋
"""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import streamlit as st

from astro.i18n import auto_cn, t
from .calculator import (
    BeijiInput,
    BeijiResult,
    BeijiShenshu,
    QueryResult,
    compute_beiji,
    compute_ke,
    get_calculator,
    get_hour_branch,
    get_year_ganzhi,
)
from .constants import (
    DIZHI_HOUR_NAME,
    DIZHI_SHENGXIAO,
    KE_LABELS,
    PALACE_INFO,
    QUERY_TYPES,
)


# ──────────────────────────────────────────────────────────────────────────────
# 顏色配置（北極神數配色）
# ──────────────────────────────────────────────────────────────────────────────

_COLORS = {
    "primary": "#C9A84C",    # 金色
    "accent": "#E94560",     # 紅色
    "blue": "#4E9AF1",       # 藍色
    "green": "#6BCB77",      # 綠色
    "purple": "#9B72CF",     # 紫色
    "bg_card": "rgba(201,168,76,0.08)",
    "border": "rgba(201,168,76,0.3)",
    "text_muted": "#9090b0",
}

_PALACE_COLORS: dict[int, str] = {
    1: "#C9A84C",  # 乾 金
    2: "#C9A84C",  # 兌 金
    3: "#E94560",  # 離 火
    4: "#6BCB77",  # 震 木
    5: "#6BCB77",  # 巽 木
    6: "#4E9AF1",  # 坎 水
    7: "#FFD93D",  # 艮 土
    8: "#FFD93D",  # 坤 土
}


def _card(title: str, value: str, color: str = "#C9A84C") -> str:
    """生成 HTML 資訊卡片。"""
    return (
        f'<div style="flex:1 1 120px;min-width:120px;'
        f"background:rgba({_hex_to_rgb(color)},0.08);border:1px solid rgba({_hex_to_rgb(color)},0.3);"
        f'border-radius:12px;padding:10px 12px;text-align:center;">'
        f'<div style="font-size:11px;color:{_COLORS["text_muted"]};margin-bottom:4px;">{title}</div>'
        f'<div style="font-size:18px;font-weight:700;color:{color};">{value}</div>'
        f"</div>"
    )


def _hex_to_rgb(hex_color: str) -> str:
    """將 #RRGGBB 轉為 'R,G,B' 字串。"""
    h = hex_color.lstrip("#")
    if len(h) == 6:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"{r},{g},{b}"
    return "201,168,76"


def _verse_block(code: str, verse: str, color: str = "#C9A84C") -> str:
    """生成條文展示 HTML 區塊。"""
    return (
        f'<div style="background:rgba({_hex_to_rgb(color)},0.06);'
        f"border-left:4px solid {color};"
        f'border-radius:0 12px 12px 0;padding:14px 18px;'
        f'margin:8px 0;font-size:14px;color:#f0d9c8;line-height:1.9;letter-spacing:0.5px;">'
        f'<span style="font-size:11px;color:{_COLORS["text_muted"]};margin-right:8px;">[{code}]</span>'
        f"{verse}</div>"
    )


# ──────────────────────────────────────────────────────────────────────────────
# 主渲染函式
# ──────────────────────────────────────────────────────────────────────────────

def render_beiji_chart(result: BeijiResult) -> None:
    """渲染北極神數完整起盤結果。"""
    inp = result.birth_input

    # ── 出生資料摘要 ──────────────────────────────────────────────────────────
    st.markdown(auto_cn("### 📊 出生資料摘要"))
    cards_html = (
        '<div style="display:flex;flex-wrap:wrap;gap:8px;margin:0 0 16px 0;">'
        + _card(auto_cn("出生年"), f"{result.year_stem}{result.year_branch}年", _COLORS["primary"])
        + _card(auto_cn("生肖"), result.year_shengxiao, _COLORS["accent"])
        + _card(auto_cn("時辰"), result.hour_branch + auto_cn("時"), _COLORS["blue"])
        + _card(auto_cn("刻"), result.ke_label, _COLORS["purple"])
        + _card(auto_cn("性別"), inp.gender, _COLORS["green"])
        + "</div>"
    )
    st.markdown(cards_html, unsafe_allow_html=True)

    birth_str = f"{inp.year}年{inp.month}月{inp.day}日 {inp.hour:02d}:{inp.minute:02d}"
    st.caption(auto_cn(f"公曆：{birth_str}"))
    st.divider()

    # ── 各宮查詢結果 ─────────────────────────────────────────────────────────
    if not result.queries:
        st.warning(auto_cn("未能計算任何查詢結果，請確認輸入資料。"))
        return

    # 按宮位分組展示
    palace_groups: dict[int, list[QueryResult]] = {}
    for qr in result.queries:
        palace_groups.setdefault(qr.palace_code, []).append(qr)

    for palace_code in sorted(palace_groups):
        palace = PALACE_INFO[palace_code]
        color = _PALACE_COLORS.get(palace_code, _COLORS["primary"])
        qrs = palace_groups[palace_code]

        with st.expander(
            f"{palace['hex']} {palace['name']}宮 — {palace['topic']}",
            expanded=True,
        ):
            for qr in qrs:
                _render_query_result(qr, color)

    st.divider()

    # ── 大運推算 ─────────────────────────────────────────────────────────────
    st.markdown(auto_cn("### 🌊 大運推算"))
    _render_dayun(result)


def _render_query_result(qr: QueryResult, color: str) -> None:
    """渲染單一查詢結果。"""
    # 標題行
    header_parts = [f"**{qr.query_label}**"]
    if qr.surname:
        header_parts.append(
            f'<span style="background:{color};color:#1a1a2e;'
            f'border-radius:6px;padding:2px 8px;font-size:13px;font-weight:700;">'
            f"姓：{qr.surname}</span>"
        )
    if qr.extra.get("siblings_desc"):
        header_parts.append(
            f'<span style="background:{color};color:#1a1a2e;'
            f'border-radius:6px;padding:2px 8px;font-size:13px;">'
            f'{qr.extra["siblings_desc"]}</span>'
        )

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
        + "".join(header_parts)
        + "</div>",
        unsafe_allow_html=True,
    )

    # 起盤說明（可展開）
    extra_parts = []
    if qr.extra.get("hour_branch"):
        extra_parts.append(f"時辰：{qr.extra['hour_branch']}時")
    if qr.extra.get("year_branch"):
        extra_parts.append(f"年支：{qr.extra['year_branch']}")
    if qr.extra.get("col_index"):
        extra_parts.append(f"列號：{qr.extra['col_index']}")
    if extra_parts:
        st.caption(auto_cn("起盤：") + " · ".join(extra_parts) + f" → 代碼 {qr.code}")

    # 條文內容
    st.markdown(_verse_block(qr.code, qr.verse, color), unsafe_allow_html=True)


def _render_dayun(result: BeijiResult) -> None:
    """渲染大運推算表格。"""
    calc = get_calculator()
    try:
        dayun_list = calc.calculate_dayun(result.birth_input)
    except Exception as exc:
        st.warning(auto_cn(f"大運計算失敗：{exc}"))
        return

    if not dayun_list:
        st.info(auto_cn("無法計算大運，請確認出生年份。"))
        return

    direction = dayun_list[0].get("direction", "")
    st.caption(auto_cn(f"大運方向：{direction}行 · 每10年一運"))

    rows = []
    for dy in dayun_list:
        rows.append({
            auto_cn("大運"): f"第{dy['index']}運",
            auto_cn("干支"): dy["stem_branch"],
            auto_cn("年齡"): f"{dy['start_age']}-{dy['end_age']}歲",
            auto_cn("代碼"): dy["code"],
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)

    # 展開顯示各運條文
    with st.expander(auto_cn("📖 查看各大運條文"), expanded=False):
        for dy in dayun_list:
            color = _COLORS["blue"]
            st.markdown(
                f"**第{dy['index']}運 {dy['stem_branch']}**（{dy['start_age']}-{dy['end_age']}歲）",
            )
            st.markdown(_verse_block(dy["code"], dy["verse"], color), unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 搜尋介面（直接查代碼 / 搜尋關鍵字）
# ──────────────────────────────────────────────────────────────────────────────

def render_beiji_search() -> None:
    """渲染北極神數條文搜尋/查詢介面。"""
    calc = get_calculator()

    st.markdown(auto_cn("### 🔍 條文直接查詢"))

    col1, col2 = st.columns([1, 1])
    with col1:
        code_input = st.text_input(
            auto_cn("輸入4位代碼（如 1111）"),
            max_chars=4,
            placeholder="1111",
            key="beiji_code_input",
        )
    with col2:
        keyword_input = st.text_input(
            auto_cn("關鍵字搜尋條文"),
            placeholder=auto_cn("例如：屬鼠、再婚"),
            key="beiji_keyword_input",
        )

    if code_input and len(code_input) == 4 and code_input.isdigit():
        verse = calc.lookup(code_input)
        st.markdown(auto_cn("**查詢結果：**"))
        color = _PALACE_COLORS.get(int(code_input[0]), _COLORS["primary"])
        st.markdown(_verse_block(code_input, verse, color), unsafe_allow_html=True)

    if keyword_input and len(keyword_input) >= 2:
        results = calc.search_verses(keyword_input)
        if results:
            st.markdown(auto_cn(f"**搜尋「{keyword_input}」共找到 {len(results)} 條：**"))
            if len(results) > 20:
                st.caption(auto_cn(f"（顯示前 20 條，共 {len(results)} 條）"))
                results = results[:20]
            for code, verse in results:
                color = _PALACE_COLORS.get(int(code[0]), _COLORS["primary"])
                st.markdown(_verse_block(code, verse, color), unsafe_allow_html=True)
        else:
            st.info(auto_cn(f"未找到包含「{keyword_input}」的條文。"))


# ──────────────────────────────────────────────────────────────────────────────
# 完整 Streamlit 入口（供 app.py 呼叫）
# ──────────────────────────────────────────────────────────────────────────────

def render_streamlit(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    gender: str = "男",
) -> None:
    """
    北極神數 Streamlit 主渲染入口。

    Parameters
    ----------
    year, month, day, hour, minute : int
        公曆出生年月日時分
    gender : str
        性別 "男" 或 "女"
    """
    tab_chart, tab_search = st.tabs([
        auto_cn("🔮 命盤"), auto_cn("🔍 條文查詢"),
    ])

    with tab_chart:
        # 刻的輸入（精細化）
        # options=range(1,9) 確保 ke 值始終在 1-8 合法範圍內
        ke = st.select_slider(
            auto_cn("出生刻（每時辰8刻，每刻15分鐘）"),
            options=list(range(1, 9)),
            value=max(1, min(8, compute_ke(hour, minute))),
            format_func=lambda x: KE_LABELS[x - 1],
            key="beiji_ke_slider",
        )

        with st.spinner(auto_cn("計算北極神數中…")):
            result = compute_beiji(
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                gender=gender,
                ke=ke,
            )

        render_beiji_chart(result)

    with tab_search:
        render_beiji_search()
