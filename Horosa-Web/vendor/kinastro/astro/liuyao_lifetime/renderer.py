# -*- coding: utf-8 -*-
"""
六爻終身卦 — Streamlit 渲染模組
Lifetime Liu Yao Hexagram — Streamlit Renderer

與 KinAstro 其他中國傳統模組風格一致，提供：
  - 卦象視覺化板（六爻橫線顯示）
  - 納甲完整排盤表格
  - 終身解讀標籤頁
  - 合婚計算
  - 大限流年指引
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from astro.i18n import auto_cn, t
from .calculator import (
    HexagramLayout,
    LifetimeHexagramCalculator,
    LifetimeResult,
    YaoInfo,
    compute_lifetime_hexagram,
)
from .constants import (
    DONG_YAO_LIFE_PERIODS,
    HEXAGRAM_LIFETIME,
    LIUQIN_LIFETIME,
    LIUSHEN_LIFETIME,
    WUXING_COLORS,
    WUXING_EMOJI,
    YAO_NAMES,
)

# ──────────────────────────────────────────────────────────────────────────────
# 顯示輔助
# ──────────────────────────────────────────────────────────────────────────────

_YAO_LINE_YANG = "━━━━━━━━━━━━━━━━"
_YAO_LINE_YIN = "━━━━━━    ━━━━━━"
_YAO_LINE_YANG_DONG = "━━━━━━━━━━━━━━━━  ○"
_YAO_LINE_YIN_DONG = "━━━━━━    ━━━━━━  ×"

# 爻象緊湊符號（用於排盤板）
_YAO_COMPACT_YANG = "▅▅▅▅▅"
_YAO_COMPACT_YIN  = "▅▅ ▅▅"

# 六神縮寫
_LIUSHEN_ABBR: Dict[str, str] = {
    "青龍": "龍", "朱雀": "雀", "勾陳": "陳",
    "騰蛇": "蛇", "白虎": "虎", "玄武": "武",
}

# 六親縮寫
_LIUQIN_ABBR: Dict[str, str] = {
    "官鬼": "官", "父母": "父", "兄弟": "兄",
    "妻財": "妻", "子孫": "子",
}


def _yao_line(code: str) -> str:
    """根據爻碼回傳爻象線條字符串。"""
    if code == "9":   # 老陽→變
        return _YAO_LINE_YANG_DONG
    elif code == "6":  # 老陰→變
        return _YAO_LINE_YIN_DONG
    elif code == "7":  # 少陽
        return _YAO_LINE_YANG
    else:              # 少陰 "8"
        return _YAO_LINE_YIN


def _yao_line_base(code: str) -> str:
    """回傳固定長度的爻象線條（不含動爻符號，供視覺排版使用）。"""
    if code in ("9", "7"):
        return _YAO_LINE_YANG
    return _YAO_LINE_YIN


def _yao_dong_symbol(code: str) -> str:
    """回傳動爻符號：老陽為 ○，老陰為 ×，靜爻為空。"""
    if code == "9":
        return "○"
    if code == "6":
        return "×"
    return ""


def _wx_badge(wx: str) -> str:
    """五行帶顏色標籤 HTML。"""
    color = WUXING_COLORS.get(wx, "#888")
    emoji = WUXING_EMOJI.get(wx, "")
    return f'<span style="background:{color};color:white;padding:1px 6px;border-radius:4px;font-size:0.85em">{emoji}{wx}</span>'


def _liuqin_color(lq: str) -> str:
    """六親顏色映射。"""
    mapping = {
        "父母": "#1E90FF",
        "兄弟": "#FF8C00",
        "官鬼": "#DC143C",
        "妻財": "#228B22",
        "子孫": "#9932CC",
    }
    return mapping.get(lq, "#555")


def _liushen_color(ls: str) -> str:
    """六神顏色映射。"""
    mapping = {
        "青龍": "#2E8B57",
        "朱雀": "#DC143C",
        "勾陳": "#B8860B",
        "騰蛇": "#8B4513",
        "白虎": "#696969",
        "玄武": "#000080",
    }
    return mapping.get(ls, "#555")


# ──────────────────────────────────────────────────────────────────────────────
# 卦象視覺化
# ──────────────────────────────────────────────────────────────────────────────

def _render_hexagram_board(layout: HexagramLayout, title: str = "") -> None:
    """渲染六爻卦象板（由上爻到初爻，傳統顯示）。

    參數：
        layout (HexagramLayout): 排盤結果。
        title  (str): 標題文字。
    """
    gua_info = HEXAGRAM_LIFETIME.get(layout.gua_name, {})
    luck = gua_info.get("luck", "")
    symbol = gua_info.get("symbol", "☯")

    # 標題區
    if title:
        st.markdown(f"### {title}")

    col_board, col_info = st.columns([1, 2])

    with col_board:
        # 伏神爻位 (0-5) → 伏神描述
        fuyao_map: Dict[int, str] = {}
        if isinstance(layout.fuyao, dict):
            fp = layout.fuyao.get("伏神爻位")
            lq_abbr_fu = _LIUQIN_ABBR.get(layout.fuyao.get("伏神六親", ""), "")
            fu_tail = layout.fuyao.get("伏神天干地支五行", "")
            if fp is not None and fu_tail:
                fuyao_map[fp] = lq_abbr_fu + fu_tail

        # 身爻對應的 position (1-6)
        shen_pos = 0
        if layout.shen_str:
            for y in layout.yao_list:
                if layout.shen_str and y.najia in layout.shen_str:
                    shen_pos = y.position
                    break

        # 卦象顯示（從上爻到初爻）
        lines_html = []
        header = (
            "<div style='display:flex;align-items:center;color:#aaa;"
            "font-size:0.78em;line-height:1.8em;border-bottom:1px solid #4a4a8a;"
            "margin-bottom:4px;padding-bottom:2px'>"
            "<span style='display:inline-block;min-width:2em'>神</span>"
            "<span style='display:inline-block;min-width:7em'>伏神</span>"
            "<span style='display:inline-block;min-width:1.5em'>宿</span>"
            "<span style='display:inline-block;min-width:9em'>六親納甲五行</span>"
            "<span style='display:inline-block;min-width:4.5em'>長生</span>"
            "<span>爻象</span>"
            "</div>"
        )
        lines_html.append(header)

        for yao in reversed(layout.yao_list):
            i0 = yao.position - 1  # 0-based index

            # 六神縮寫
            ls_abbr = _LIUSHEN_ABBR.get(yao.liushen, yao.liushen[:1] if yao.liushen else "　")

            # 伏神
            fu_text = fuyao_map.get(i0, "")
            fu_span = (
                f"<span style='display:inline-block;min-width:7em;color:#b0c4de'>{fu_text}</span>"
            )

            # 二十八宿
            xiu_span = (
                f"<span style='display:inline-block;min-width:1.5em;color:#ffd700'>{yao.xiu}</span>"
            )

            # 六親縮寫 + 納甲 + 五行
            lq_abbr = _LIUQIN_ABBR.get(yao.liuqin, yao.liuqin)
            lq_color = _liuqin_color(yao.liuqin)
            info_span = (
                f"<span style='display:inline-block;min-width:9em'>"
                f"<span style='color:{lq_color}'>{lq_abbr}</span>"
                f"<span style='color:#e0e0ff'>{yao.najia}{yao.wuxing}</span>"
                f"</span>"
            )

            # 長生狀態
            cs = yao.changsheng or ""
            cs_span = (
                f"<span style='display:inline-block;min-width:4.5em;color:#90ee90'>{cs}</span>"
            )

            # 爻象 + 世應 + 身 + 動
            line_sym = _YAO_COMPACT_YANG if yao.code in ("9", "7") else _YAO_COMPACT_YIN
            color = "#FFD700" if yao.is_dong else "#e0e0ff"
            sy_text = yao.shiying or "　"
            dong_sym = "○" if yao.code == "9" else ("×" if yao.code == "6" else "")
            shen_mark = "身" if yao.position == shen_pos else ""

            yao_span = (
                f"<span style='color:#aaa'>{sy_text}</span>"
                f"<span style='color:{color}'>{line_sym}</span>"
                f"<span style='color:#ff9f43;margin-left:2px'>{shen_mark}</span>"
                f"<span style='color:#ff6b6b;margin-left:2px'>{dong_sym}</span>"
            )

            lines_html.append(
                f"<div style='display:flex;align-items:center;line-height:2.0em'>"
                f"<span style='display:inline-block;min-width:2em;color:#90caf9'>{ls_abbr}</span>"
                f"{fu_span}{xiu_span}{info_span}{cs_span}{yao_span}"
                f"</div>"
            )
        st.markdown(
            "<div style='font-family:monospace;font-size:0.85em;line-height:2.0em;"
            "background:#1a1a2e;color:#e0e0ff;padding:16px;border-radius:10px;"
            "border:1px solid #4a4a8a'>"
            + "".join(lines_html)
            + "</div>",
            unsafe_allow_html=True,
        )

    with col_info:
        wx_color = WUXING_COLORS.get(layout.palace_wx, "#888")
        st.markdown(
            f"""
            <div style='padding:12px;background:#1e2140;border-radius:10px;
                        border-left:4px solid {wx_color};color:#e0e0ff'>
              <h3 style='margin:0;color:{wx_color}'>{symbol} {layout.gua_name} 卦</h3>
              <p style='margin:4px 0;color:#b0b0cc'>之卦：{layout.biangua_name}　 動爻：第 {layout.dong_yao} 爻</p>
              <p style='margin:4px 0;color:#b0b0cc'>{_wx_badge(layout.palace_wx)} 宮　運勢：<b style='color:#e0e0ff'>{luck}</b></p>
              <hr style='margin:8px 0;border-top:1px solid #4a4a8a'>
              <p style='font-size:0.9em;color:#e0e0ff'>{layout.guaci}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# 納甲排盤表格
# ──────────────────────────────────────────────────────────────────────────────

def _render_najia_table(layout: HexagramLayout) -> None:
    """渲染完整納甲排盤表格。

    參數：
        layout (HexagramLayout): 排盤結果。
    """
    st.markdown(auto_cn("#### 📋 納甲排盤"))

    rows = []
    for yao in reversed(layout.yao_list):  # 從上爻到初爻顯示
        lq_c = _liuqin_color(yao.liuqin)
        ls_c = _liushen_color(yao.liushen)
        dong = "🔴 動爻" if yao.is_dong else ""
        rows.append({
            auto_cn("爻位"): yao.yao_name,
            auto_cn("爻象"): _yao_line(yao.code),
            auto_cn("六神"): yao.liushen,
            auto_cn("六親"): yao.liuqin,
            auto_cn("納甲"): yao.najia,
            auto_cn("五行"): yao.wuxing,
            auto_cn("二十八宿"): yao.xiu,
            auto_cn("長生"): yao.changsheng,
            auto_cn("世應"): yao.shiying,
            auto_cn("動"): dong,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch")

    # 之卦簡表
    if layout.biangua_layout:
        with st.expander(auto_cn(f"📌 之卦 {layout.biangua_name} 排盤")):
            rows2 = []
            for yao in reversed(layout.biangua_layout.yao_list):
                rows2.append({
                    auto_cn("爻位"): yao.yao_name,
                    auto_cn("六親"): yao.liuqin,
                    auto_cn("納甲"): yao.najia,
                    auto_cn("五行"): yao.wuxing,
                })
            df2 = pd.DataFrame(rows2)
            st.dataframe(df2, width="stretch")
            if layout.biangua_layout.guaci:
                st.markdown(f"**{auto_cn('卦辭')}：** {layout.biangua_layout.guaci}")


# ──────────────────────────────────────────────────────────────────────────────
# 終身解讀
# ──────────────────────────────────────────────────────────────────────────────

def _render_lifetime_interpretation(result: LifetimeResult) -> None:
    """渲染終身卦解讀。

    包含性格、事業、婚姻、財運、健康、晚年六大面向。

    參數：
        result (LifetimeResult): 計算結果。
    """
    interp = result.lifetime_interp
    if not interp:
        st.info(auto_cn("暫無此卦終身解讀資料。"))
        return

    gua = result.hexagram.gua_name
    wx = result.hexagram.palace_wx
    wx_c = WUXING_COLORS.get(wx, "#888")
    symbol = interp.get("symbol", "☯")
    summary = interp.get("summary", "")
    luck = interp.get("luck", "")

    # 總論
    st.markdown(
        f"""
        <div style='padding:16px;background:linear-gradient(135deg,#1a1a2e,#16213e);
                    color:#e0e0ff;border-radius:12px;margin-bottom:16px'>
          <h3 style='color:#FFD700;margin:0'>{symbol} {gua} — 終身命盤總論</h3>
          <p style='margin:8px 0;color:#aaa'>{summary}</p>
          <p style='margin:4px 0'>宮五行：{_wx_badge(wx)}　整體運勢：<b style='color:#FFD700'>{luck}</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 六大面向
    sections = [
        ("👤", auto_cn("終身性格"), interp.get("character", "")),
        ("💼", auto_cn("事業才能"), interp.get("career", "")),
        ("💑", auto_cn("感情婚姻"), interp.get("marriage", "")),
        ("💰", auto_cn("財運財帛"), interp.get("wealth", "")),
        ("🏥", auto_cn("健康狀況"), interp.get("health", "")),
        ("🌅", auto_cn("晚年運勢"), interp.get("old_age", "")),
    ]

    cols = st.columns(2)
    for idx, (icon, label, text) in enumerate(sections):
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div style='padding:12px;background:#1e2140;border-radius:8px;
                            margin-bottom:12px;border-left:3px solid {wx_c};color:#e0e0ff'>
                  <p style='margin:0;font-weight:bold;color:#f0f0ff'>{icon} {label}</p>
                  <p style='margin:4px 0;font-size:0.9em;color:#c0c0dd'>{text}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 動爻大限
    st.markdown(f"#### ⏳ {auto_cn('動爻大限')}")
    life_p = result.life_period
    if life_p:
        st.info(
            f"**{auto_cn('動爻')}：第 {result.hexagram.dong_yao} 爻**\n\n"
            f"📅 **{life_p.get('period', '')}** — {life_p.get('theme', '')}\n\n"
            f"{life_p.get('desc', '')}"
        )

    # 動爻爻辭
    dong_text = result.hexagram.dong_yao_text
    if dong_text:
        st.markdown(f"#### 📜 {auto_cn('動爻爻辭')}")
        st.markdown(
            f"""
            <div style='padding:12px;background:#2a2010;border-radius:8px;
                        border-left:4px solid #ffc107'>
              <p style='margin:0;font-style:italic;color:#ffe08a'>{dong_text}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 彖辭
    if result.hexagram.tuanci:
        with st.expander(auto_cn(f"📖 {gua}卦 彖辭")):
            st.markdown(result.hexagram.tuanci)


# ──────────────────────────────────────────────────────────────────────────────
# 六親六神詳解
# ──────────────────────────────────────────────────────────────────────────────

def _render_liuqin_detail(result: LifetimeResult) -> None:
    """渲染六親六神終身含義說明。"""
    st.markdown(f"#### 🔮 {auto_cn('六親在終身卦中的含義')}")

    # 提取卦中出現的六親
    all_lq = [y.liuqin for y in result.hexagram.yao_list if y.liuqin]
    unique_lq = list(dict.fromkeys(all_lq))  # 去重保序

    for lq in unique_lq:
        info = LIUQIN_LIFETIME.get(lq, {})
        if info:
            symbol = info.get("symbol", "")
            color = _liuqin_color(lq)
            with st.expander(f"{symbol} **{lq}** — {info.get('general', '')}"):
                st.markdown(
                    f"- **{auto_cn('事業')}**：{info.get('career', '')}\n"
                    f"- **{auto_cn('婚姻感情')}**：{info.get('marriage', '')}\n"
                    f"- **{auto_cn('財運')}**：{info.get('wealth', '')}\n"
                    f"- **{auto_cn('健康')}**：{info.get('health', '')}"
                )

    st.markdown(f"#### 🌟 {auto_cn('六神在終身卦中的含義')}")
    unique_ls = list(dict.fromkeys(
        [y.liushen for y in result.hexagram.yao_list if y.liushen]
    ))
    for ls in unique_ls:
        info = LIUSHEN_LIFETIME.get(ls, {})
        if info:
            symbol = info.get("symbol", "")
            with st.expander(f"{symbol} **{ls}** — {info.get('general', '')}"):
                st.markdown(
                    f"- **{auto_cn('性格')}**：{info.get('personality', '')}\n"
                    f"- **{auto_cn('事業')}**：{info.get('career', '')}\n"
                    f"- **{auto_cn('健康')}**：{info.get('health', '')}"
                )


# ──────────────────────────────────────────────────────────────────────────────
# 合婚計算
# ──────────────────────────────────────────────────────────────────────────────

def _render_compatibility(result: LifetimeResult) -> None:
    """渲染兩人終身卦合婚計算介面。

    參數：
        result (LifetimeResult): 甲方計算結果（已由主頁計算）。
    """
    st.markdown(f"### 💑 {auto_cn('終身卦合婚 — 六爻相性')}")
    st.info(auto_cn(
        "輸入乙方（另一半）出生資料，計算兩人終身卦宮五行生剋相性。"
    ))

    with st.form("compat_form"):
        st.markdown(f"**{auto_cn('乙方出生資料')}**")
        c1, c2, c3 = st.columns(3)
        with c1:
            y2 = st.number_input(auto_cn("年"), min_value=1, max_value=2100,
                                  value=1990, key="compat_year")
        with c2:
            m2 = st.number_input(auto_cn("月"), min_value=1, max_value=12,
                                  value=6, key="compat_month")
        with c3:
            d2 = st.number_input(auto_cn("日"), min_value=1, max_value=31,
                                  value=1, key="compat_day")
        h2 = st.selectbox(
            auto_cn("時辰"),
            options=list(range(0, 24)),
            format_func=lambda x: f"{x:02d}:00",
            key="compat_hour",
        )
        submitted = st.form_submit_button(auto_cn("計算合婚"))

    if submitted:
        try:
            result2 = compute_lifetime_hexagram(
                int(y2), int(m2), int(d2), int(h2)
            )
            compat = LifetimeHexagramCalculator.compute_compatibility(result, result2)

            c_color = compat["color"]
            st.markdown(
                f"""
                <div style='padding:16px;background:#1e2140;border-radius:12px;
                            border:2px solid {c_color};color:#e0e0ff'>
                  <h3 style='color:{c_color}'>{compat['level']} 相性結果</h3>
                  <p style='color:#e0e0ff'>甲方：<b>{compat['person1_gua']} 卦</b> 
                     ({_wx_badge(compat['person1_wx'])})</p>
                  <p style='color:#e0e0ff'>乙方：<b>{compat['person2_gua']} 卦</b> 
                     ({_wx_badge(compat['person2_wx'])})</p>
                  <p style='color:#e0e0ff'>五行關係：<b>{compat['compat_type']}</b></p>
                  <hr style='border-top:1px solid #4a4a8a'>
                  <p style='color:#c0c0dd'>{compat['desc']}</p>
                  <p style='color:#e0e0ff'><b>{auto_cn('建議')}：</b>{compat['advice']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # 乙方終身卦
            with st.expander(auto_cn(f"乙方終身卦詳情：{result2.hexagram.gua_name}")):
                _render_hexagram_board(result2.hexagram)
                interp2 = result2.lifetime_interp
                if interp2:
                    st.markdown(f"**{auto_cn('性格')}：** {interp2.get('character', '')}")
                    st.markdown(f"**{auto_cn('婚姻')}：** {interp2.get('marriage', '')}")

        except Exception as e:
            st.error(f"{auto_cn('計算出錯')}：{e}")


# ──────────────────────────────────────────────────────────────────────────────
# 大限流年
# ──────────────────────────────────────────────────────────────────────────────

def _render_life_periods(result: LifetimeResult) -> None:
    """渲染六大人生階段（動爻對應大限）。"""
    st.markdown(f"### ⏳ {auto_cn('六爻大限 — 人生六大階段')}")
    st.caption(auto_cn(
        "依據《六爻預測學》，六爻分別對應人生六個階段；動爻所在爻位標示本命最重要的人生主題。"
    ))

    for pos, info in DONG_YAO_LIFE_PERIODS.items():
        is_dong = (pos == result.hexagram.dong_yao)
        yao = result.hexagram.yao_list[pos - 1]
        lq = yao.liuqin
        najia = yao.najia
        wx = yao.wuxing
        wx_c = WUXING_COLORS.get(wx, "#888")

        border = "3px solid #FFD700" if is_dong else f"1px solid {wx_c}"
        bg = "#2a2515" if is_dong else "#1e2140"
        dong_badge = " 🔴 **本命動爻**" if is_dong else ""

        st.markdown(
            f"""
            <div style='padding:12px;background:{bg};border-radius:8px;
                        margin-bottom:10px;border-left:{border};color:#e0e0ff'>
              <p style='margin:0;color:#f0f0ff'><b>第{pos}爻 {info['period']}</b>{dong_badge}</p>
              <p style='margin:4px 0;color:#b0b0cc'>{info['theme']}</p>
              <p style='margin:4px 0;color:#888;font-size:0.85em'>{info['desc']}</p>
              <p style='margin:0;font-size:0.85em;color:#c0c0dd'>
                納甲：<b>{najia}</b> 五行：<b style='color:{wx_c}'>{wx}</b>
                六親：<b>{lq}</b>
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# What-if 模擬
# ──────────────────────────────────────────────────────────────────────────────

def _render_whatif(result: LifetimeResult) -> None:
    """渲染「假如換個時辰」模擬介面。"""
    st.markdown(f"### 🔄 {auto_cn('假如換個時辰 — What-if 模擬')}")
    st.caption(auto_cn(
        "改變出生時辰，觀察終身卦如何變化。適合時辰不確定者進行驗證。"
    ))

    base_y, base_m, base_d = result.year, result.month, result.day

    rows = []
    for h in range(0, 24, 2):
        try:
            r = compute_lifetime_hexagram(base_y, base_m, base_d, h)
            rows.append({
                auto_cn("時辰"): f"{h:02d}:00",
                auto_cn("本卦"): r.hexagram.gua_name,
                auto_cn("之卦"): r.hexagram.biangua_name,
                auto_cn("動爻"): f"第{r.hexagram.dong_yao}爻",
                auto_cn("宮五行"): r.hexagram.palace_wx,
                auto_cn("整體運勢"): HEXAGRAM_LIFETIME.get(r.hexagram.gua_name, {}).get("luck", ""),
                auto_cn("是本命"): "✅" if h == result.hour else "",
            })
        except Exception:
            pass

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch")
    st.caption(auto_cn("✅ 標示為您的實際出生時辰計算結果。"))


# ──────────────────────────────────────────────────────────────────────────────
# 文化介紹
# ──────────────────────────────────────────────────────────────────────────────

def _render_intro() -> None:
    """渲染六爻終身卦文化介紹。"""
    with st.expander(auto_cn("📖 什麼是六爻終身卦？"), expanded=False):
        st.markdown(auto_cn("""
**六爻終身卦**（又稱「本命六爻卦」）是以出生年月日時為基礎，
通過農曆干支數字演算，得出一個固定不變的終身本命卦象，
與隨機起卦的六爻占卜截然不同。

---

### 📌 起卦方法（農曆干支法）
```
上卦 = (年支數 + 農曆月 + 農曆日 + 時支數) ÷ 8 取餘
下卦 = (年支數 + 農曆月 + 農曆日) ÷ 8 取餘
動爻 = (年支數 + 農曆月 + 農曆日 + 時支數) ÷ 6 取餘
```

### 📌 與隨機占卜的區別
| 特徵 | 本命終身卦 | 隨機占卜卦 |
|------|-----------|-----------|
| 固定性 | 終身不變 | 每次不同 |
| 依據 | 出生時間 | 隨機/銅錢 |
| 用途 | 人生全局 | 特定事宜 |
| 核心 | 本命性格 | 當下趨勢 |

### 📌 納甲理論基礎
納甲（Najia）是六爻的精髓，將天干地支分配到六爻，
配合六親（父母、兄弟、官鬼、妻財、子孫）和六神（青龍、朱雀、勾陳、騰蛇、白虎、玄武），
形成一套完整的五行生剋分析體系。

### 📌 古籍依據
- 《卜筮正宗》（清·王洪緒）
- 《增刪卜易》（清·野鶴老人）
- 《六爻預測學》（邵偉華）
        """))


# ──────────────────────────────────────────────────────────────────────────────
# 主渲染入口
# ──────────────────────────────────────────────────────────────────────────────

def render_streamlit(result: LifetimeResult) -> None:
    """主渲染函數，接受 LifetimeResult 並渲染完整 Streamlit 頁面。

    此函數由 app.py 調用。

    參數：
        result (LifetimeResult): 由 compute_lifetime_hexagram() 產生的結果。
    """
    # 文化介紹（可折疊）
    _render_intro()

    # 頁頭基本信息
    st.markdown(
        f"""
        <div style='padding:10px 16px;background:#1e2140;border-radius:8px;margin-bottom:8px;color:#e0e0ff'>
          <b>{auto_cn('出生時間')}：</b>
          {result.year}/{result.month:02d}/{result.day:02d}
          {result.hour:02d}:00　
          <b>{auto_cn('農曆')}：</b>
          {result.lunar_year}年{result.lunar_month}月{result.lunar_day}日　
          <b>{auto_cn('四柱')}：</b>
          {result.year_gz}年 {result.month_gz}月 {result.day_gz}日 {result.hour_gz}時
          {f'　<b>📍</b> {result.location_name}' if result.location_name else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 卦象板
    _render_hexagram_board(
        result.hexagram,
        title=auto_cn(f"🔮 本命終身卦：{result.hexagram.gua_name} 之 {result.hexagram.biangua_name}"),
    )

    st.divider()

    # 六個標籤頁
    tab_labels = [
        auto_cn("📋 納甲排盤"),
        auto_cn("🌟 終身解讀"),
        auto_cn("🔮 六親六神"),
        auto_cn("⏳ 大限流年"),
        auto_cn("💑 合婚"),
        auto_cn("🔄 換時辰"),
    ]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        _render_najia_table(result.hexagram)

    with tabs[1]:
        _render_lifetime_interpretation(result)

    with tabs[2]:
        _render_liuqin_detail(result)

    with tabs[3]:
        _render_life_periods(result)

    with tabs[4]:
        _render_compatibility(result)

    with tabs[5]:
        _render_whatif(result)
