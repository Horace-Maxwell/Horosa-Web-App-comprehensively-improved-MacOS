# -*- coding: utf-8 -*-
"""
astro/nanji/renderer.py — 南極神數 Streamlit 渲染模組

視覺風格：
  - 仿古宣紙質感（米白底色）
  - 書法字體（Noto Serif SC）
  - 傳統四柱命盤排版
  - 整體呈現明清時期命書風格

主要函式：
    render_streamlit(year, month, day, hour, minute, gender, ...)
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

from astro.i18n import auto_cn, t

from .calculator import (
    NanJiShenShu,
    TiaowenDatabase,
    TiaowenEntry,
    calculate_da_yun,
    get_jianchu_huainan,
    get_xiu_group,
)
from .constants import (
    DIZHI,
    JIANCHU,
    PASSWORDS,
    SVG_BORDER_COLOR,
    SVG_INK_DARK,
    SVG_PAPER_BG,
    SVG_SEAL_RED,
    SVG_SUBTITLE_COLOR,
    WUXING_COLORS,
    WUXING_GAN,
    WUXING_ZHI,
    XIU28_ORDER,
    YINYANG_GAN,
)


# ============================================================
# SVG 命盤生成
# ============================================================

def _build_nanji_svg(njs: NanJiShenShu, width: int = 860, height: int = 420) -> str:
    """
    生成南極神數四柱命盤 SVG（仿古宣紙水墨風格）。
    布局：四柱並列（由右至左：年 月 日 時），右側大運序列。
    SVG 使用 viewBox 實現響應式縮放（不設固定像素寬高）。
    """
    pillars = [
        ("年", njs.year_pillar[:1], njs.year_pillar[1:] if len(njs.year_pillar) > 1 else "?"),
        ("月", njs.month_pillar[:1], njs.month_pillar[1:] if len(njs.month_pillar) > 1 else "?"),
        ("日", njs.day_gan or "?", njs.day_zhi or "?"),
        ("時", njs.hour_pillar[:1] if njs.hour_pillar else "?",
               njs.hour_pillar[1:] if njs.hour_pillar and len(njs.hour_pillar) > 1 else njs.hour_zhi),
    ]

    def wx_color(char: str) -> str:
        wx = WUXING_GAN.get(char) or WUXING_ZHI.get(char, "")
        return WUXING_COLORS.get(wx, SVG_INK_DARK)

    col_w = 120
    col_start = 60
    # 使用 viewBox，不設固定 width/height，由 CSS 控制縮放
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'style="width:100%;height:auto;display:block;">',
        # 背景
        f'<rect width="{width}" height="{height}" fill="{SVG_PAPER_BG}" rx="8"/>',
        f'<rect x="4" y="4" width="{width-8}" height="{height-8}" '
        f'fill="none" stroke="{SVG_BORDER_COLOR}" stroke-width="1.5" rx="6"/>',
        # 標題
        f'<text x="{width//2}" y="42" text-anchor="middle" '
        f'font-family="Noto Serif SC, serif" font-size="22" font-weight="bold" '
        f'fill="{SVG_SEAL_RED}" letter-spacing="6">南極神數</text>',
        f'<text x="{width//2}" y="66" text-anchor="middle" '
        f'font-family="Noto Serif SC, serif" font-size="12" '
        f'fill="{SVG_SUBTITLE_COLOR}">性別：{njs.gender}　宮部：{njs.palace_section}　'
        f'年干陰陽：{njs.year_yinyang}</text>',
        # 橫線
        f'<line x1="20" y1="78" x2="{width-20}" y2="78" '
        f'stroke="{SVG_BORDER_COLOR}" stroke-width="0.8"/>',
    ]

    # 四柱（由右至左，索引 0=年 1=月 2=日 3=時，但視覺上從右排）
    for i, (label, gan, zhi) in enumerate(pillars):
        # 由右至左排列：年在最右（i=0 → x 最大）
        x = col_start + (3 - i) * col_w + col_w // 2
        y_label = 110
        y_gan = 175
        y_zhi = 255
        y_wx = 315

        # 柱標籤（年月日時）
        svg_parts.append(
            f'<text x="{x}" y="{y_label}" text-anchor="middle" '
            f'font-family="Noto Serif SC, serif" font-size="14" '
            f'fill="{SVG_SUBTITLE_COLOR}">{label}柱</text>'
        )
        # 天干（大字，五行色）
        svg_parts.append(
            f'<text x="{x}" y="{y_gan}" text-anchor="middle" '
            f'font-family="Noto Serif SC, serif" font-size="52" font-weight="bold" '
            f'fill="{wx_color(gan)}">{gan}</text>'
        )
        # 地支（大字）
        svg_parts.append(
            f'<text x="{x}" y="{y_zhi}" text-anchor="middle" '
            f'font-family="Noto Serif SC, serif" font-size="52" font-weight="bold" '
            f'fill="{wx_color(zhi)}">{zhi}</text>'
        )
        # 五行小字
        wx_g = WUXING_GAN.get(gan, "")
        wx_z = WUXING_ZHI.get(zhi, "")
        svg_parts.append(
            f'<text x="{x}" y="{y_wx}" text-anchor="middle" '
            f'font-family="Noto Serif SC, serif" font-size="11" '
            f'fill="{SVG_SUBTITLE_COLOR}">{wx_g or "-"}  {wx_z or "-"}</text>'
        )

    # 大運列（右側區域）
    dayun_x = col_start + 4 * col_w + 30
    svg_parts.append(
        f'<text x="{dayun_x}" y="106" '
        f'font-family="Noto Serif SC, serif" font-size="13" font-weight="bold" '
        f'fill="{SVG_SEAL_RED}">大運</text>'
    )
    svg_parts.append(
        f'<line x1="{dayun_x - 10}" y1="112" x2="{width - 20}" y2="112" '
        f'stroke="{SVG_BORDER_COLOR}" stroke-width="0.6"/>'
    )
    for j, dy in enumerate(njs.da_yun[:6]):
        gy = 132 + j * 46
        svg_parts.append(
            f'<text x="{dayun_x}" y="{gy}" '
            f'font-family="Noto Serif SC, serif" font-size="15" font-weight="bold" '
            f'fill="{SVG_INK_DARK}">{dy.ganzhi}</text>'
        )
        svg_parts.append(
            f'<text x="{dayun_x + 38}" y="{gy}" '
            f'font-family="Noto Serif SC, serif" font-size="10" '
            f'fill="{SVG_SUBTITLE_COLOR}">{dy.start_age}歲</text>'
        )

    # 底部宮部印章
    seal_x = width - 55
    seal_y = height - 45
    svg_parts.append(
        f'<rect x="{seal_x - 28}" y="{seal_y - 22}" width="58" height="28" '
        f'fill="none" stroke="{SVG_SEAL_RED}" stroke-width="1.5" rx="3"/>'
    )
    svg_parts.append(
        f'<text x="{seal_x}" y="{seal_y}" text-anchor="middle" '
        f'font-family="Noto Serif SC, serif" font-size="13" '
        f'fill="{SVG_SEAL_RED}" font-weight="bold">{njs.palace_section}</text>'
    )

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


# ============================================================
# 條文瀏覽 UI
# ============================================================

def _render_tiaowen_browser(db: TiaowenDatabase) -> None:
    """條文資料庫瀏覽器"""
    st.markdown(f"**{auto_cn('條文資料庫瀏覽')}** — {db.total} 條")

    col_sec, col_code = st.columns([1, 2])
    with col_sec:
        sections = sorted({e.section for e in db.all_entries()})
        selected_section = st.selectbox(
            auto_cn("選擇宮部"),
            options=sections,
            key="nanji_browser_section",
        )
    with col_code:
        if selected_section:
            entries_in_sec = db.lookup_by_section(selected_section)
            codes = sorted({e.code for e in entries_in_sec})
            selected_code = st.selectbox(
                auto_cn("選擇密碼（建除+宿）"),
                options=["（全部）"] + codes,
                key="nanji_browser_code",
            )

    if selected_section:
        entries_in_sec = db.lookup_by_section(selected_section)
        if selected_code and selected_code != "（全部）":
            entries_in_sec = [e for e in entries_in_sec if e.code == selected_code]

        for entry in entries_in_sec:
            with st.expander(f"【{entry.section} · {entry.code}】", expanded=False):
                st.markdown(f"**條文：** {entry.verse}")
                st.caption(entry.comment)


# ============================================================
# 主渲染函式
# ============================================================

def render_streamlit(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    gender: str = "男",
    after_lichun: bool = True,
    day_gan: str = "",
    day_zhi: str = "",
    query_code: str = "",
    query_section: str = "",
    **_kwargs,
) -> None:
    """
    南極神數 Streamlit 主渲染函式

    Args:
        year: 出生年（公曆）
        month: 出生月（公曆，1-12）
        day: 出生日（公曆）
        hour: 出生小時（0-23）
        minute: 出生分鐘（不影響四柱計算）
        gender: 性別（男/女）
        after_lichun: 保留參數（由 sxtwl 自動判斷節氣）
        day_gan: 保留參數（sxtwl 已自動計算，無需手動傳入）
        day_zhi: 保留參數（同上）
        query_code: 欲查詢的密碼（建除+宿名，如「建張」）
        query_section: 欲查詢的宮部（留空則用年柱地支宮部）
    """
    # 建立命盤物件（使用 sxtwl 精確計算四柱）
    njs = NanJiShenShu.from_solar_datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        gender=gender,
    )
    # 保留對舊式手動日柱輸入的向下相容
    if day_gan and not njs.day_pillar:
        njs.set_day_pillar(day_gan, day_zhi if day_zhi else None)
        njs.set_hour_pillar()

    # ── 標題
    st.markdown(
        f"<h2 style='color:{SVG_SEAL_RED};font-family:Noto Serif SC,serif;"
        f"letter-spacing:4px;text-align:center;'>☰ 南極神數 ☰</h2>",
        unsafe_allow_html=True,
    )
    st.caption(auto_cn("《家傳秘法手稿》· 南極神數　圖為體，條文為用"))

    # ── 四柱 SVG 命盤
    st.markdown("---")
    svg_html = _build_nanji_svg(njs)
    st.markdown(
        f"<div style='width:100%;text-align:center'>{svg_html}</div>",
        unsafe_allow_html=True,
    )

    # ── 四柱文字摘要
    st.markdown(f"**{auto_cn('四柱八字')}：** `{njs.get_four_pillars_str()}`")
    st.markdown(
        f"**{auto_cn('大運序列')}：** {njs.get_da_yun_str()}"
    )
    st.caption(
        auto_cn(f"宮部：{njs.palace_section}　年干陰陽：{njs.year_yinyang}　"
                f"{'順排大運' if njs.year_yinyang == '陽' and gender == '男' or njs.year_yinyang == '陰' and gender == '女' else '逆排大運'}")
    )

    st.markdown("---")

    # ── 本宮部條文（命主宮部，起盤即顯示）
    palace_entries = njs.lookup_all_tiaowen_for_palace()
    st.subheader(
        auto_cn(f"📜 {njs.palace_section}條文（共 {len(palace_entries)} 條）")
    )
    st.caption(auto_cn("以下為本命宮部全部條文，需配合原書十八星圖定位密碼後查閱相應條文"))
    for entry in palace_entries:
        st.markdown(
            f"<div style='background:#fffbf0;border-left:3px solid {SVG_SEAL_RED};"
            f"padding:10px 14px;border-radius:4px;margin-bottom:8px;'>"
            f"<b style='color:{SVG_SEAL_RED}'>【{entry.section} · {entry.code}】</b><br/>"
            f"<span style='font-family:Noto Serif SC,serif;font-size:15px;color:{SVG_INK_DARK};'>"
            f"{entry.verse}</span><br/>"
            f"<small style='color:{SVG_SUBTITLE_COLOR};'>{entry.comment}</small>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── 按密碼精確查詢面板
    st.subheader(auto_cn("🔮 精確查詢條文"))
    st.caption(auto_cn("依手稿：以宮部（年支部）+ 密碼（建除+宿）查條文"))

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        _all_sections = ['子部', '丑部', '寅部', '卯部', '辰部', '巳部',
                         '午部', '未部', '申部', '酉部', '戌部', '亥部']
        default_sec = query_section or njs.palace_section
        sec_idx = _all_sections.index(default_sec) if default_sec in _all_sections else 0
        section_sel = st.selectbox(
            auto_cn("宮部"),
            options=_all_sections,
            index=sec_idx,
            key="nanji_query_section",
        )
    with col2:
        jianchu_sel = st.selectbox(
            auto_cn("建除"),
            options=JIANCHU,
            key="nanji_query_jianchu",
        )
    with col3:
        xiu_sel = st.selectbox(
            auto_cn("二十八宿"),
            options=XIU28_ORDER,
            key="nanji_query_xiu",
        )

    if st.button(auto_cn("查詢條文"), key="nanji_query_btn"):
        code = jianchu_sel + xiu_sel
        results = njs.lookup_tiaowen(section=section_sel, code=code)
        if results:
            st.success(auto_cn(f"找到 {len(results)} 條條文"))
            for entry in results:
                st.markdown(
                    f"<div style='background:#fffbf0;border-left:3px solid {SVG_SEAL_RED};"
                    f"padding:12px;border-radius:4px;margin-bottom:10px;'>"
                    f"<b style='color:{SVG_SEAL_RED}'>【{entry.section} · {entry.code}】</b><br/>"
                    f"<span style='font-family:Noto Serif SC,serif;font-size:15px;color:{SVG_INK_DARK};'>{entry.verse}</span><br/>"
                    f"<small style='color:{SVG_SUBTITLE_COLOR};'>{entry.comment}</small>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.warning(
                auto_cn(
                    f"【{section_sel} · {code}】未找到對應條文。\n\n"
                    "提示：需參照原書十八星圖，以圖為體自行參悟。\n"
                    "「圖不破則數難起」—— 手稿核心精神。"
                )
            )

    st.markdown("---")

    # ── 條文資料庫完整瀏覽
    with st.expander(auto_cn("📚 條文資料庫（全部 246 條）")):
        db = TiaowenDatabase.get_instance()
        _render_tiaowen_browser(db)

    # ── 密碼解說
    with st.expander(auto_cn("🔑 手稿密碼解說")):
        for code_key, meaning in PASSWORDS.items():
            st.markdown(f"**{code_key}** → {meaning}")

    # ── 手稿提示
    st.markdown("---")
    st.info(
        auto_cn(
            "**手稿核心提示**\n\n"
            "「圖為體，條文為用」「給人以黃金不如給人點金之術」\n\n"
            "完整功能需補充原書十八星圖數據，"
            "五星精確宮位計算建議結合天文曆法（如 astropy）。\n\n"
            "請研讀原書圖像與《果老星宗》，結合實踐自悟。"
        )
    )


def _render_tiaowen_browser_simple(njs: NanJiShenShu) -> None:
    """顯示命主宮部的所有條文（簡單列表）"""
    entries = njs.lookup_all_tiaowen_for_palace()
    if not entries:
        st.caption(auto_cn("本宮部暫無條文記錄。"))
        return
    for entry in entries:
        st.markdown(
            f"**【{entry.code}】** {entry.verse}  \n"
            f"<small style='color:#666;'>{entry.comment}</small>",
            unsafe_allow_html=True,
        )
        st.divider()
