# -*- coding: utf-8 -*-
"""
astro/chunzi/renderer.py — 蠢子數 Streamlit 渲染模組

視覺風格：
  - 仿古宣紙質感（米白底色）
  - 書法字體（Noto Serif SC）
  - 傳統詩詞排版

主要函式：
    render_streamlit()
"""

from __future__ import annotations

import streamlit as st

from astro.i18n import auto_cn

from .chunzi import MANSIONS_28, ChunZiShu

# 顏色常數（與 nanji 風格一致）
_PAPER_BG = "#fdf8f0"
_SEAL_RED = "#8b1a1a"
_INK_DARK = "#1a1a2e"
_SUBTITLE = "#6b5e4e"
_BORDER = "#c4a882"


def _render_verse_card(verse_dict: dict) -> None:
    """渲染單條詩詞卡片"""
    code = verse_dict.get("code", "")
    verse = verse_dict.get("verse", "")
    category = verse_dict.get("category", "")
    star = verse_dict.get("star", "")
    degree = verse_dict.get("degree", "")
    branch = verse_dict.get("branch", "")
    st.markdown(
        f"<div style='background:{_PAPER_BG};border-left:3px solid {_SEAL_RED};"
        f"padding:12px 16px;border-radius:4px;margin-bottom:10px;'>"
        f"<b style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;font-size:16px;'>"
        f"【{code}】</b>"
        f"<span style='color:{_SUBTITLE};font-size:12px;margin-left:8px;'>"
        f"{category} · {star} · {degree}度 · {branch}</span><br/>"
        f"<span style='font-family:Noto Serif SC,serif;font-size:15px;color:{_INK_DARK};'>"
        f"{verse}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_streamlit() -> None:
    """
    蠢子數 Streamlit 主渲染函式（不需出生資料，為查詢工具）
    """
    czs = ChunZiShu()
    _verse_count = len(czs.df)

    # ── 標題
    st.markdown(
        f"<h2 style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;"
        f"letter-spacing:4px;text-align:center;'>☵ 蠢子數 ☵</h2>",
        unsafe_allow_html=True,
    )
    st.caption(auto_cn(f"蠢子數纏度 · 二十八宿 + 七政四餘 + 度數 · {_verse_count} 筆詩詞"))
    st.markdown("---")

    # ── 代碼查詢
    st.subheader(auto_cn("🔍 代碼查詢"))
    st.caption(auto_cn("輸入詩詞代碼，例如：室巨9未、角陰13酉、柳計6巳"))

    col_input, col_btn = st.columns([3, 1])
    with col_input:
        query_code = st.text_input(
            auto_cn("詩詞代碼"),
            placeholder="室巨9未",
            key="chunzi_code_input",
            label_visibility="collapsed",
        )
    with col_btn:
        do_lookup = st.button(auto_cn("查詢"), key="chunzi_lookup_btn", width="stretch")

    if do_lookup and query_code:
        result = czs.get_verse(query_code.strip())
        if result:
            _render_verse_card(result)
            # 結構化解析
            info = czs.explain(query_code.strip())
            if "error" not in info:
                with st.expander(auto_cn("📊 結構化解析"), expanded=True):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric(auto_cn("父親屬相"), info["father_zodiac"] or "—")
                        st.metric(auto_cn("母親屬相"), info["mother_zodiac"] or "—")
                    with c2:
                        st.metric(auto_cn("配偶屬相"), info["spouse_zodiac"] or "—")
                        st.metric(auto_cn("子息數"), str(info["children_count"]) if info["children_count"] is not None else "—")
                    with c3:
                        st.metric(auto_cn("出生時辰"), info["birth_hour"] or "—")
                        st.metric(auto_cn("壽元"), f"{info['longevity']}歲" if info["longevity"] else "—")
                    if info["flags"]:
                        st.warning(auto_cn("命理標記：") + "、".join(info["flags"]))
        else:
            st.warning(auto_cn(f"找不到代碼「{query_code}」，請確認格式，例如：室巨9未"))

    st.markdown("---")

    # ── 關鍵字搜尋
    st.subheader(auto_cn("🔎 關鍵字搜尋"))
    st.caption(auto_cn("在 4574 筆詩詞中全文搜尋"))

    col_kw, col_lim, col_kw_btn = st.columns([3, 1, 1])
    with col_kw:
        keyword = st.text_input(
            auto_cn("關鍵字"),
            placeholder="未時生人",
            key="chunzi_keyword_input",
            label_visibility="collapsed",
        )
    with col_lim:
        limit = st.number_input(
            auto_cn("筆數"),
            min_value=1,
            max_value=100,
            value=10,
            key="chunzi_search_limit",
            label_visibility="collapsed",
        )
    with col_kw_btn:
        do_search = st.button(auto_cn("搜尋"), key="chunzi_search_btn", width="stretch")

    if do_search and keyword:
        results = czs.search(keyword.strip(), limit=int(limit))
        if results:
            st.success(auto_cn(f"找到 {len(results)} 筆詩詞"))
            for r in results:
                _render_verse_card(r)
        else:
            st.info(auto_cn(f"未找到含「{keyword}」的詩詞"))

    st.markdown("---")

    # ── 二十八宿瀏覽
    st.subheader(auto_cn("🌟 二十八宿詩詞瀏覽"))
    mansion_sel = st.selectbox(
        auto_cn("選擇星宿"),
        options=MANSIONS_28,
        key="chunzi_mansion_sel",
    )

    if st.button(auto_cn("瀏覽"), key="chunzi_mansion_btn"):
        mansion_results = czs.get_verses_by_mansion(mansion_sel)
        if mansion_results:
            st.success(auto_cn(f"{mansion_sel}宿詩詞共 {len(mansion_results)} 筆"))
            for r in mansion_results[:30]:
                _render_verse_card(r)
            if len(mansion_results) > 30:
                st.caption(auto_cn(f"（僅顯示前 30 筆，共 {len(mansion_results)} 筆）"))
        else:
            st.info(auto_cn(f"{mansion_sel}宿暫無詩詞記錄"))

    st.markdown("---")

    # ── 多標籤 AND 搜尋
    with st.expander(auto_cn("🏷️ 多標籤 AND 搜尋")):
        st.caption(auto_cn("輸入多個關鍵字（換行分隔），所有關鍵字都必須出現在詩詞中"))
        tags_input = st.text_area(
            auto_cn("關鍵字（每行一個）"),
            placeholder="未時生人\n先去父",
            key="chunzi_tags_input",
            height=100,
            label_visibility="collapsed",
        )
        tag_limit = st.number_input(
            auto_cn("最多顯示筆數"),
            min_value=1,
            max_value=100,
            value=20,
            key="chunzi_tags_limit",
        )
        if st.button(auto_cn("AND 搜尋"), key="chunzi_tags_btn"):
            tags = [t.strip() for t in tags_input.splitlines() if t.strip()]
            if tags:
                tag_results = czs.search_by_tags(tags, limit=int(tag_limit))
                if tag_results:
                    st.success(auto_cn(f"找到 {len(tag_results)} 筆詩詞"))
                    for r in tag_results:
                        _render_verse_card(r)
                else:
                    st.info(auto_cn("未找到同時包含所有關鍵字的詩詞"))
            else:
                st.warning(auto_cn("請輸入至少一個關鍵字"))

    # ── 說明
    st.markdown("---")
    st.info(
        auto_cn(
            "**蠢子數纏度**\n\n"
            "以二十八宿 + 七政四餘 + 度數為核心的傳統詩詞命理系統，"
            "特別擅長女命婚姻、子息、父母、事業的交叉驗證。\n\n"
            f"資料庫收錄 {_verse_count} 筆詩詞，代碼格式：宿名 + 星曜 + 度數 + 地支，例如：室巨9未。"
        )
    )
