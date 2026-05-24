"""
astro/damo/renderer.py — 達摩一掌經 Streamlit 渲染模組
(Damo One Palm Scripture — UI Rendering Module)

包含：
- 互動手掌 SVG 圖（12 宮標示 + 四宮高亮 + 星名）
- 詳細報告：前世六道分析、四宮個別解讀、總性格總論
- 各階段建議、改運法
- 掌經原文說明頁
"""

from __future__ import annotations

import streamlit as st

from astro.damo.calculator import (
    DamoChart,
    EARTHLY_BRANCHES,
    PALACE_MAP,
    load_damo_data,
)
from astro.chart_renderer_v2 import build_cultural_svg
from astro.i18n import t


# ============================================================
# 手掌 SVG 生成 (Palm SVG Generation)
# ============================================================

def _build_palm_svg(chart: DamoChart) -> str:
    """生成互動手掌 SVG 圖，標示 12 宮位與四宮高亮。

    Layout: 12 宮位環繞圓形排列，類似時鐘佈局。
    子在正下方（6 點鐘），順時針排列。
    """
    # 四宮高亮的地支索引
    highlight_indices = set()
    palace_labels = {}
    if chart.year_palace:
        highlight_indices.add(chart.year_palace.branch_index)
        palace_labels[chart.year_palace.branch_index] = "年"
    if chart.month_palace:
        highlight_indices.add(chart.month_palace.branch_index)
        palace_labels[chart.month_palace.branch_index] = "月"
    if chart.day_palace:
        highlight_indices.add(chart.day_palace.branch_index)
        palace_labels[chart.day_palace.branch_index] = "日"
    if chart.hour_palace:
        highlight_indices.add(chart.hour_palace.branch_index)
        palace_labels[chart.hour_palace.branch_index] = "時"

    # SVG 參數
    cx, cy = 250, 260  # 圓心
    r_outer = 200       # 外圈半徑
    r_inner = 130       # 內圈半徑
    r_text = 170        # 文字半徑

    import math

    parts = []
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 530" '
        'style="max-width:500px;width:100%;height:auto;font-family:sans-serif;">'
    )

    # 背景
    parts.append(
        '<rect width="500" height="530" rx="16" '
        'fill="#1a1a2e" stroke="#C9A84C" stroke-width="2"/>'
    )

    # 標題
    parts.append(
        '<text x="250" y="35" text-anchor="middle" '
        'fill="#C9A84C" font-size="18" font-weight="bold">'
        '🤚 達摩一掌經 · 掌中乾坤</text>'
    )

    # 外圈
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" '
        f'fill="none" stroke="#C9A84C" stroke-width="1.5" opacity="0.6"/>'
    )
    # 內圈
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" '
        f'fill="none" stroke="#C9A84C" stroke-width="1" opacity="0.3"/>'
    )

    # 六道顏色
    realm_colors = {
        "佛道": "#FFD700",
        "仙道": "#7DF9FF",
        "人道": "#90EE90",
        "修羅道": "#FF6347",
        "畜道": "#DDA0DD",
        "鬼道": "#A0A0A0",
    }

    # 12 宮位排列（子在正下方，順時針）
    # 達摩一掌經以左手掌為盤，子位於掌底（6 點鐘方向），
    # 順時針排列至亥。此佈局與傳統掌中排列一致。
    # 角度：子=180°(下), 丑=210°, 寅=240° ... 亥=150°
    for i, branch in enumerate(EARTHLY_BRANCHES):
        # 角度計算：子(index=0)在180°(正下方)，順時針每宮30°
        angle_deg = 180 + i * 30
        angle_rad = math.radians(angle_deg)

        # 宮位位置
        px = cx + r_text * math.sin(angle_rad)
        py = cy - r_text * math.cos(angle_rad)

        # 外圈位置（標籤）
        ox = cx + (r_outer + 15) * math.sin(angle_rad)
        oy = cy - (r_outer + 15) * math.cos(angle_rad)

        star, realm = PALACE_MAP[branch]
        color = realm_colors.get(realm, "#FFFFFF")
        is_highlight = i in highlight_indices

        # 圓點
        dot_r = 22 if is_highlight else 16
        opacity = "1.0" if is_highlight else "0.5"
        sw = "3" if is_highlight else "1"
        stroke = f'stroke="{color}" stroke-width="{sw}"'
        fill = f'fill="{color}"' if is_highlight else 'fill="#2a2a4a"'

        parts.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{dot_r}" '
            f'{fill} {stroke} opacity="{opacity}"/>'
        )

        # 地支文字
        parts.append(
            f'<text x="{px:.1f}" y="{py - 3:.1f}" text-anchor="middle" '
            f'fill="{"#1a1a2e" if is_highlight else "#e0e0e0"}" '
            f'font-size="{"13" if is_highlight else "11"}" '
            f'font-weight="{"bold" if is_highlight else "normal"}">'
            f'{branch}</text>'
        )

        # 星名（小字）
        parts.append(
            f'<text x="{px:.1f}" y="{py + 10:.1f}" text-anchor="middle" '
            f'fill="{"#1a1a2e" if is_highlight else color}" '
            f'font-size="8">{star}</text>'
        )

        # 宮位標籤（年/月/日/時）
        if i in palace_labels:
            label = palace_labels[i]
            parts.append(
                f'<text x="{ox:.1f}" y="{oy:.1f}" text-anchor="middle" '
                f'fill="{color}" font-size="14" font-weight="bold">'
                f'【{label}】</text>'
            )

        # 輻射線
        ix = cx + r_inner * math.sin(angle_rad)
        iy = cy - r_inner * math.cos(angle_rad)
        parts.append(
            f'<line x1="{ix:.1f}" y1="{iy:.1f}" '
            f'x2="{px:.1f}" y2="{py:.1f}" '
            f'stroke="{color}" stroke-width="0.5" opacity="0.3"/>'
        )

    # 中心文字
    parts.append(
        f'<text x="{cx}" y="{cy - 10}" text-anchor="middle" '
        f'fill="#C9A84C" font-size="14" font-weight="bold">'
        f'掌中十二宮</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy + 10}" text-anchor="middle" '
        f'fill="#888" font-size="11">'
        f'{"男命順行" if chart.gender == "male" else "女命逆行"}</text>'
    )

    # 六道圖例
    legend_y = 500
    legend_items = list(realm_colors.items())
    for j, (realm_name, rcolor) in enumerate(legend_items):
        lx = 30 + j * 78
        parts.append(
            f'<circle cx="{lx}" cy="{legend_y}" r="5" fill="{rcolor}"/>'
        )
        parts.append(
            f'<text x="{lx + 10}" y="{legend_y + 4}" '
            f'fill="{rcolor}" font-size="10">{realm_name}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


# ============================================================
# Streamlit 渲染主函式 (Main Render Function)
# ============================================================

def render_damo_chart(
    chart: DamoChart,
    *,
    after_chart_hook=None,
):
    """達摩一掌經 Streamlit 渲染函式。

    Parameters
    ----------
    chart : DamoChart
        排盤計算結果
    after_chart_hook : callable, optional
        圖表後的回呼函式（通常用於 AI 按鈕）
    """
    st.subheader(t("damo_chart_title"))

    # ── 基本資料 ──
    gender_text = "男命" if chart.gender == "male" else "女命"
    lunar_info = (
        f"農曆 {chart.lunar_year} 年 "
        f"{_lunar_month_text(chart.lunar_month, chart.lunar_leap)} "
        f"{_lunar_day_text(chart.lunar_day)} "
        f"{chart.birth_shichen}"
    )
    st.info(
        f"📅 {chart.year}-{chart.month:02d}-{chart.day:02d} "
        f"{chart.hour:02d}:{chart.minute:02d} "
        f"(UTC{chart.timezone:+.1f}) · {gender_text}\n\n"
        f"🌙 {lunar_info} · 年支：{chart.birth_branch}"
    )

    # ── Tabs ──
    tab_chart, tab_detail, tab_advice, tab_classic = st.tabs([
        t("damo_subtab_chart"),
        t("damo_subtab_detail"),
        t("damo_subtab_advice"),
        t("damo_subtab_classic"),
    ])

    # ──────────── Tab 1: 手掌圖 + 四宮速覽 ──────────────
    with tab_chart:
        # SVG 手掌圖
        svg_raw = _build_palm_svg(chart)
        wrapped = build_cultural_svg(svg_raw, "tab_damo", title="達摩一掌經")
        st.markdown(wrapped, unsafe_allow_html=True)

        # 四宮速覽表
        st.markdown("### " + t("damo_four_palaces"))
        cols = st.columns(4)
        palaces = [chart.year_palace, chart.month_palace,
                   chart.day_palace, chart.hour_palace]
        palace_emojis = ["👨‍👩‍👦", "💼", "💕", "🌟"]

        for i, (p, emoji) in enumerate(zip(palaces, palace_emojis)):
            if p is None:
                continue
            with cols[i]:
                realm_color = _realm_color(p.realm)
                st.markdown(
                    f'<div style="background:#2a2a4a;border:2px solid {realm_color};'
                    f'border-radius:12px;padding:12px;text-align:center;">'
                    f'<div style="font-size:24px;">{emoji}</div>'
                    f'<div style="color:{realm_color};font-weight:bold;font-size:16px;">'
                    f'{p.palace_name}</div>'
                    f'<div style="color:#aaa;font-size:12px;">（{p.palace_alias}·{p.past_life_era}）</div>'
                    f'<div style="color:#FFD700;font-size:20px;margin:6px 0;">{p.star}</div>'
                    f'<div style="color:{realm_color};font-size:14px;">{p.branch}宮 · {p.realm}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        if after_chart_hook:
            after_chart_hook()

    # ──────────── Tab 2: 詳細解讀 ──────────────
    with tab_detail:
        data = load_damo_data()
        stars_data = data.get("stars", {})
        realms_data = data.get("realms", {})
        palaces_data = data.get("palaces", {})

        # 六道綜合分析
        st.markdown("### " + t("damo_realm_analysis"))
        st.markdown(chart.realm_summary)
        st.divider()

        # 總性格總論
        st.markdown("### " + t("damo_overall_summary"))
        st.markdown(chart.overall_summary)
        st.divider()

        # 四宮詳細解讀
        palace_list = [
            ("year_palace", chart.year_palace),
            ("month_palace", chart.month_palace),
            ("day_palace", chart.day_palace),
            ("hour_palace", chart.hour_palace),
        ]

        for palace_key, palace in palace_list:
            if palace is None:
                continue

            star_info = stars_data.get(palace.star, {})
            palace_meta = palaces_data.get(palace_key, {})

            st.markdown(
                f"### {palace.palace_name}（{palace.palace_alias}）— "
                f"{palace.star} · {palace.realm}"
            )

            # 宮位意義
            if palace_meta:
                st.markdown(f"**{palace_meta.get('meaning', '')}**")

            if star_info:
                # 性格
                with st.expander(f"🧭 {palace.star}性格特質", expanded=(palace_key == "hour_palace")):
                    st.markdown(star_info.get("personality", ""))
                    st.markdown(f"**關鍵字：** {star_info.get('keywords', '')}")
                    st.markdown(f"**優點：** {star_info.get('strengths', '')}")
                    st.markdown(f"**缺點：** {star_info.get('weaknesses', '')}")

                # 前世
                with st.expander(f"🔮 前世因果（{palace.past_life_era}）"):
                    st.markdown(star_info.get("past_life", ""))

                # 事業財運婚姻健康
                col1, col2 = st.columns(2)
                with col1:
                    with st.expander("💼 事業"):
                        st.markdown(star_info.get("career", ""))
                    with st.expander("💰 財運"):
                        st.markdown(star_info.get("wealth", ""))
                with col2:
                    with st.expander("💕 感情"):
                        st.markdown(star_info.get("love", ""))
                    with st.expander("🏥 健康"):
                        st.markdown(star_info.get("health", ""))

            # 六道解析
            realm_info = realms_data.get(palace.realm, {})
            if realm_info:
                with st.expander(f"☸️ {palace.realm}解析"):
                    st.markdown(realm_info.get("description", ""))
                    st.markdown(f"**特質：** {realm_info.get('characteristics', '')}")
                    st.markdown(f"**修行建議：** {realm_info.get('practice', '')}")

            st.divider()

    # ──────────── Tab 3: 建議與改運 ──────────────
    with tab_advice:
        data = load_damo_data()
        stars_data = data.get("stars", {})

        # 命宮（時宮）為主要分析對象
        main_star = chart.hour_palace.star if chart.hour_palace else ""
        main_info = stars_data.get(main_star, {})

        st.markdown("### " + t("damo_life_stages"))

        if main_info:
            st.markdown("#### 🌱 少年期建議")
            st.markdown(main_info.get("advice_youth", ""))

            st.markdown("#### 🌿 中年期建議")
            st.markdown(main_info.get("advice_middle", ""))

            st.markdown("#### 🍂 晚年期建議")
            st.markdown(main_info.get("advice_elder", ""))

        st.divider()
        st.markdown("### " + t("damo_remedy"))

        # 綜合所有四宮的改運方法
        seen_remedies = set()
        for palace in [chart.year_palace, chart.month_palace,
                       chart.day_palace, chart.hour_palace]:
            if palace is None:
                continue
            star_info = stars_data.get(palace.star, {})
            remedy = star_info.get("remedy", "")
            if remedy and remedy not in seen_remedies:
                seen_remedies.add(remedy)
                st.markdown(f"**{palace.palace_name}（{palace.star}）改運法：**")
                st.markdown(remedy)
                st.markdown("")

        # 正面結語
        st.success(t("damo_positive_ending"))

    # ──────────── Tab 4: 掌經原文 ──────────────
    with tab_classic:
        data = load_damo_data()
        classic = data.get("classic_text", {})

        st.markdown(f"### {classic.get('title', '達摩一掌經原文概要')}")
        st.markdown(classic.get("introduction", ""))
        st.divider()

        st.markdown("#### 📖 排盤方法")
        st.markdown(classic.get("method", ""))
        st.divider()

        st.markdown("#### 🧘 掌經精義")
        st.markdown(classic.get("philosophy", ""))
        st.divider()

        # 十二星速查表
        st.markdown("#### 📋 十二宮星速查表")
        table_data = []
        for branch in EARTHLY_BRANCHES:
            star, realm = PALACE_MAP[branch]
            stars_data = data.get("stars", {})
            info = stars_data.get(star, {})
            table_data.append({
                "地支": branch,
                "星名": star,
                "六道": realm,
                "五行": info.get("element", ""),
                "吉凶": info.get("nature", ""),
                "關鍵字": info.get("keywords", ""),
            })
        st.dataframe(table_data, width="stretch", hide_index=True)


# ============================================================
# 輔助函式 (Helper Functions)
# ============================================================

def _lunar_month_text(month: int, leap: bool) -> str:
    """格式化農曆月份文字。"""
    names = [
        "正月", "二月", "三月", "四月", "五月", "六月",
        "七月", "八月", "九月", "十月", "十一月", "十二月",
    ]
    prefix = "閏" if leap else ""
    if 1 <= month <= 12:
        return f"{prefix}{names[month - 1]}"
    return f"{prefix}{month}月"


def _lunar_day_text(day: int) -> str:
    """格式化農曆日文字。"""
    special = {
        1: "初一", 2: "初二", 3: "初三", 4: "初四", 5: "初五",
        6: "初六", 7: "初七", 8: "初八", 9: "初九", 10: "初十",
        11: "十一", 12: "十二", 13: "十三", 14: "十四", 15: "十五",
        16: "十六", 17: "十七", 18: "十八", 19: "十九", 20: "二十",
        21: "廿一", 22: "廿二", 23: "廿三", 24: "廿四", 25: "廿五",
        26: "廿六", 27: "廿七", 28: "廿八", 29: "廿九", 30: "三十",
    }
    return special.get(day, str(day))


def _realm_color(realm: str) -> str:
    """取得六道對應顏色。"""
    colors = {
        "佛道": "#FFD700",
        "仙道": "#7DF9FF",
        "人道": "#90EE90",
        "修羅道": "#FF6347",
        "畜道": "#DDA0DD",
        "鬼道": "#A0A0A0",
    }
    return colors.get(realm, "#FFFFFF")
