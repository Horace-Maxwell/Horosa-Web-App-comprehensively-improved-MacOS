"""
astro/maya/renderer.py — 瑪雅占星排盤渲染器
(Maya Astrology Chart Renderer)

以分頁式 UI 呈現完整瑪雅占星體驗：
Tabbed UI delivering the full Maya astrology experience:

  Tab 1 🌀 Tzolk'in 出生盤  — day sign wheel + rich interpretation
  Tab 2 📅 Long Count 長紀年 — period display + historical timeline
  Tab 3 🏛️ Calendar Round   — 260+365 day combined calendar
  Tab 4 ⭐ 金星週期          — Venus synodic cycle in Tzolk'in
  Tab 5 🔄 跨系統對照        — Western zodiac + AI interpretation
"""

from __future__ import annotations
import streamlit as st

from .calculator import MayanChart
from .constants import TZOLKIN_DAY_DATA, TZOLKIN_NUMBERS, HAAB_MONTHS, PLANET_COLORS, DEGREES_PER_TZOLKIN_SIGN
from .mayan_glyphs import (
    generate_tzolkin_wheel_svg,
    generate_day_sign_card_html,
    generate_haab_grid_html,
    generate_tzolkin_mini_grid_html,
)
from .long_count import get_all_events_as_timeline, get_period_summary


# ============================================================
# 主渲染函數 (Main Render Function)
# ============================================================

def render_maya_chart(chart: MayanChart, after_chart_hook=None) -> None:
    """
    渲染完整瑪雅占星排盤（分頁式 UI）。
    Render the complete Maya astrology chart using a tabbed UI.

    Parameters
    ----------
    chart            : MayanChart  — computed chart data
    after_chart_hook : callable    — optional callback (used for AI button)
    """
    # Quick summary header
    _render_summary_header(chart)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌀 Tzolk'in 出生盤",
        "📅 Long Count 長紀年",
        "🏛️ Calendar Round",
        "⭐ 金星週期",
        "🔄 跨系統對照",
    ])

    with tab1:
        _render_tzolkin_tab(chart)

    with tab2:
        _render_long_count_tab(chart)

    with tab3:
        _render_calendar_round_tab(chart)

    with tab4:
        _render_venus_tab(chart)

    with tab5:
        _render_cross_system_tab(chart)
        if after_chart_hook:
            after_chart_hook()


# ============================================================
# 摘要標題 (Summary Header)
# ============================================================

def _render_summary_header(chart: MayanChart) -> None:
    """頂部摘要條 — 快速顯示最重要的資訊。"""
    tz = chart.tzolkin
    lc = chart.long_count

    header_html = f"""
    <div style="
        background: linear-gradient(135deg, #1a0a2e, #2a1040);
        border: 1px solid #6b3a00;
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 20px;
        flex-wrap: wrap;
    ">
        <div style="font-size: 48px; line-height: 1;">{tz.glyph_emoji}</div>
        <div>
            <div style="font-size: 22px; font-weight: bold; color: #FFD700; font-family: 'Georgia', serif;">
                {tz.number} {tz.sign_name} / {tz.sign_name_cn}
            </div>
            <div style="font-size: 14px; color: #d4b896; margin-top: 4px;">
                {tz.number_name_cn} · {tz.number_tone_cn} &nbsp;|&nbsp;
                {tz.direction_cn} · {tz.element_cn} &nbsp;|&nbsp; {tz.deity_cn}
            </div>
            <div style="font-size: 12px; color: #888; margin-top: 4px;">
                Long Count: <code style="color:#c8a060">{lc.date_str}</code>
                &nbsp;·&nbsp; Haab: {chart.haab.date_str}
                &nbsp;·&nbsp; G{chart.lord_of_night}
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


# ============================================================
# Tab 1: Tzolk'in 出生盤
# ============================================================

def _render_tzolkin_tab(chart: MayanChart) -> None:
    tz = chart.tzolkin

    col_wheel, col_info = st.columns([1, 1])

    with col_wheel:
        st.markdown("#### 🌀 Tzolk'in 輪盤")
        wheel_svg = generate_tzolkin_wheel_svg(tz.sign_index, tz.number)
        st.markdown(
            f'<div style="text-align:center">{wheel_svg}</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "外環：20 個日符號（黃金高亮 = 您的出生日符號）\n"
            "內環：13 個神聖數字（高亮 = 您的神聖數字）"
        )

    with col_info:
        st.markdown("#### 🔮 日符號詮釋")
        card_html = generate_day_sign_card_html(tz.sign_index, tz.number, highlighted=True)
        st.markdown(card_html, unsafe_allow_html=True)

        st.markdown("#### 🔢 神聖數字")
        num_data = TZOLKIN_NUMBERS[tz.number - 1]
        num_html = f"""
        <div style="
            background: linear-gradient(135deg, #1a0a0a, #2a1a00);
            border: 2px solid #FFD700;
            border-radius: 10px;
            padding: 14px;
            margin-top: 8px;
            color: white;
            font-family: 'Georgia', serif;
        ">
            <div style="font-size:28px;font-weight:bold;color:#FFD700;text-align:center;">
                {tz.number} — {num_data['name_cn']}
            </div>
            <div style="font-size:12px;color:#aaa;text-align:center;margin:4px 0;">
                {num_data['name_en']} · {num_data['tone_cn']} ({num_data['tone_en']})
            </div>
            <div style="font-size:13px;color:#d4b896;margin-top:8px;line-height:1.6;">
                {num_data['meaning_cn']}
            </div>
        </div>"""
        st.markdown(num_html, unsafe_allow_html=True)

    # Destiny & Mythology sections
    st.markdown("---")
    dest_col, myth_col = st.columns(2)
    with dest_col:
        st.markdown("#### 🌟 命運解讀")
        st.markdown(
            f'<div style="background:#1a1a2e;border-radius:10px;padding:14px;'
            f'color:#d4b896;font-family:Georgia,serif;line-height:1.7;font-size:13px;">'
            f'{tz.destiny_cn}</div>',
            unsafe_allow_html=True,
        )
    with myth_col:
        st.markdown("#### 📖 神話故事")
        st.markdown(
            f'<div style="background:#1a1a2e;border-radius:10px;padding:14px;'
            f'color:#d4b896;font-family:Georgia,serif;line-height:1.7;font-size:13px;">'
            f'{tz.mythology_cn}</div>',
            unsafe_allow_html=True,
        )

    # All 20 day signs mini-grid
    st.markdown("---")
    st.markdown("#### 📋 Tzolk'in 二十日符號（您的日符號高亮）")
    st.markdown(generate_tzolkin_mini_grid_html(tz.sign_index), unsafe_allow_html=True)


# ============================================================
# Tab 2: Long Count 長紀年
# ============================================================

def _render_long_count_tab(chart: MayanChart) -> None:
    lc = chart.long_count

    st.markdown("#### 📅 長紀年位置")

    # 5-unit display
    lc_cols = st.columns(5)
    lc_display = [
        ("B'ak'tun", lc.baktun, "#8B4513", "~394年", "文明時代"),
        ("K'atun",   lc.katun,  "#CD853F", "~20年",  "命運週期"),
        ("Tun",      lc.tun,    "#DAA520", "360天",  "年度週期"),
        ("Winal",    lc.winal,  "#6b6b6b", "20天",   "月份單元"),
        ("K'in",     lc.kin,    "#A0522D", "1天",    "單日"),
    ]
    for col, (name, val, color, duration, label) in zip(lc_cols, lc_display):
        col.markdown(
            f'<div style="background:{color};padding:12px;border-radius:10px;'
            f'text-align:center;color:white;border:1px solid {color}88;">'
            f'<div style="font-size:11px;color:#ddd;">{name}</div>'
            f'<div style="font-size:32px;font-weight:bold;">{val}</div>'
            f'<div style="font-size:10px;color:#eee;">{duration} · {label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div style="text-align:center;font-size:18px;font-weight:bold;'
        f'color:#FFD700;margin:12px 0;font-family:monospace;">'
        f'🗓️ {lc.date_str}</div>',
        unsafe_allow_html=True,
    )

    # Period progress bars
    st.markdown("---")
    st.markdown("#### ⏳ 週期進度")
    prog_col1, prog_col2 = st.columns(2)
    with prog_col1:
        st.markdown(f"**B'ak'tun {lc.baktun} 進度**")
        st.progress(lc.progress_in_baktun, text=f"{lc.progress_in_baktun*100:.1f}% 完成")
        st.caption(f"已過 {lc.days_in_baktun:,} 天 / 共 144,000 天（≈ 394 年）")
    with prog_col2:
        st.markdown(f"**K'atun {lc.katun} 進度**")
        st.progress(lc.progress_in_katun, text=f"{lc.progress_in_katun*100:.1f}% 完成")
        st.caption(f"已過 {lc.days_in_katun:,} 天 / 共 7,200 天（≈ 20 年）")

    # Current era interpretation
    st.markdown("---")
    st.markdown("#### 🌍 時代解讀")
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#1a0a0a,#2a1a00);'
        f'border:1px solid #8B4513;border-radius:12px;padding:16px;'
        f'color:#d4b896;font-family:Georgia,serif;line-height:1.7;">'
        f'<b style="color:#FFD700;font-size:15px;">{lc.katun_meaning_cn[:20] + ("…" if len(lc.katun_meaning_cn) > 20 else "")}</b><br>'
        f'{get_period_summary(lc, "zh")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Historical timeline
    st.markdown("---")
    st.markdown("#### 🏺 歷史 Long Count 時間軸")
    _render_historical_timeline(chart.julian_day)


def _render_historical_timeline(current_jd: float) -> None:
    """Plotly timeline of important Long Count events."""
    try:
        import plotly.graph_objects as go
        from .long_count import long_count_to_jd, parse_long_count
        from .constants import HISTORICAL_LONG_COUNT_EVENTS
    except ImportError:
        st.warning("需要安裝 plotly 才能顯示時間軸。")
        return

    events = get_all_events_as_timeline()
    if not events:
        return

    # Convert JD to approximate year (JD 2451545 = J2000.0 = 2000 CE)
    def jd_to_year(jd: float) -> float:
        return 2000.0 + (jd - 2451545.0) / 365.25

    x_vals, y_vals, texts, colors = [], [], [], []
    cat_colors = {
        "creation":     "#FFD700",
        "civilization": "#4169E1",
        "royalty":      "#9400D3",
        "astronomy":    "#00CED1",
        "decline":      "#DC143C",
        "conquest":     "#8B0000",
        "transition":   "#FF8C00",
        "modern":       "#32CD32",
    }

    for ev in events:
        yr = jd_to_year(ev["event_jd"])
        x_vals.append(yr)
        y_vals.append(0)
        texts.append(
            f"<b>{ev['long_count']}</b><br>"
            f"{ev['gregorian']}<br>"
            f"{ev['event_cn']}"
        )
        colors.append(cat_colors.get(ev.get("category", "modern"), "#888"))

    current_yr = jd_to_year(current_jd)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        mode="markers+text",
        marker=dict(size=14, color=colors, symbol="diamond",
                    line=dict(color="white", width=1)),
        text=[e["long_count"] for e in events],
        textposition="top center",
        textfont=dict(size=8, color="#d4b896"),
        hovertext=texts,
        hoverinfo="text",
        name="歷史事件",
    ))

    # Current date marker
    fig.add_vline(
        x=current_yr, line_dash="dash", line_color="#FFD700", line_width=2,
        annotation_text="今日", annotation_font_color="#FFD700",
    )

    fig.update_layout(
        plot_bgcolor="#0a0415",
        paper_bgcolor="#0a0415",
        font=dict(color="#d4b896"),
        xaxis=dict(
            title="公曆年份 (CE)",
            gridcolor="#2a1a4a",
            zerolinecolor="#4a3a6a",
        ),
        yaxis=dict(showticklabels=False, showgrid=False),
        showlegend=False,
        height=250,
        margin=dict(l=40, r=40, t=30, b=50),
    )
    st.plotly_chart(fig, width="stretch")

    # Table of events
    with st.expander("📋 查看完整歷史事件列表"):
        for ev in events:
            yr = jd_to_year(ev["event_jd"])
            col_lc, col_gr, col_ev = st.columns([1.5, 1.5, 3])
            col_lc.code(ev["long_count"])
            col_gr.caption(ev["gregorian"])
            col_ev.write(ev["event_cn"])


# ============================================================
# Tab 3: Calendar Round
# ============================================================

def _render_calendar_round_tab(chart: MayanChart) -> None:
    cr = chart.calendar_round
    tz = cr.tzolkin
    haab = cr.haab

    st.markdown("#### 🏛️ Calendar Round — 52年神聖輪迴")

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0a1a0a,#1a2a1a);'
        f'border:2px solid #4a7c4e;border-radius:14px;padding:18px;'
        f'text-align:center;color:white;font-family:Georgia,serif;">'
        f'<div style="font-size:14px;color:#aaa;">你的 Calendar Round 位置</div>'
        f'<div style="font-size:26px;font-weight:bold;color:#FFD700;margin:8px 0;">'
        f'{tz.number} {tz.sign_name} / {haab.date_str}</div>'
        f'<div style="font-size:13px;color:#d4b896;">'
        f'{tz.sign_name_cn} · {tz.number_name_cn} · {haab.month_name_cn}</div>'
        f'<div style="font-size:11px;color:#888;margin-top:8px;">'
        f'下次相同 Calendar Round 出現：約 52 年後（18,980 天）'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    tz_col, haab_col = st.columns(2)

    with tz_col:
        st.markdown("#### 🌀 Tzolk'in（神聖曆 260 天）")
        st.markdown(
            f'<div style="background:#2d1b4e;border-radius:10px;padding:14px;'
            f'text-align:center;color:white;">'
            f'<div style="font-size:36px">{tz.glyph_emoji}</div>'
            f'<div style="font-size:24px;font-weight:bold;">'
            f'{tz.number} {tz.sign_name}</div>'
            f'<div style="font-size:14px;color:#DDA0DD;">{tz.sign_name_cn}</div>'
            f'<div style="font-size:11px;color:#999;margin-top:6px;">'
            f'第 {tz.day_position + 1} / 260 天</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        # Progress in 260-day cycle
        st.progress((tz.day_position + 1) / 260, text=f"260天循環進度：{tz.day_position+1}/260")

    with haab_col:
        st.markdown("#### 🏛️ Haab（民用曆 365 天）")
        st.markdown(
            f'<div style="background:#2F4F4F;border-radius:10px;padding:14px;'
            f'text-align:center;color:white;">'
            f'<div style="font-size:36px">{haab.month_glyph}</div>'
            f'<div style="font-size:24px;font-weight:bold;">'
            f'{haab.day_of_month} {haab.month_name}</div>'
            f'<div style="font-size:14px;color:#aaa;">{haab.month_name_cn}</div>'
            f'<div style="font-size:11px;color:#999;margin-top:6px;">'
            f'第 {haab.day_of_year + 1} / 365 天</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.progress((haab.day_of_year + 1) / 365, text=f"365天循環進度：{haab.day_of_year+1}/365")

    # Haab months grid
    st.markdown("---")
    st.markdown("#### 🗓️ Haab 十九月份（您所在月份高亮）")
    st.markdown(generate_haab_grid_html(haab.month_index), unsafe_allow_html=True)
    if haab.month_index == 18:
        st.warning("⚠️ Wayeb（瓦耶布）是五個不吉利的無名日，被視為危險時期。")

    # 52-year cycle info
    st.markdown("---")
    st.markdown("#### 🔄 52 年神聖週期")
    st.info(
        "Calendar Round 是 Tzolk'in（260 天）與 Haab（365 天）的最小公倍數循環。\n\n"
        f"**LCM(260, 365) = 18,980 天 ≈ 52 年**\n\n"
        f"你的 Calendar Round「{tz.number} {tz.sign_name} / {haab.date_str}」"
        f"下一次重複出現約在 52 年後。\n\n"
        "對瑪雅文明而言，52 年是最重要的生命週期——「世紀」的結束與新生。"
    )


# ============================================================
# Tab 4: 金星週期
# ============================================================

def _render_venus_tab(chart: MayanChart) -> None:
    venus = chart.venus
    tz = chart.tzolkin

    st.markdown("#### ⭐ 金星週期——瑪雅最神聖的天文現象")

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0a0a2e,#1a1a40);'
        f'border:2px solid #c8a800;border-radius:14px;padding:18px;color:white;">'
        f'<div style="display:flex;gap:20px;align-items:center;flex-wrap:wrap;">'
        f'<div style="font-size:52px;">⭐</div>'
        f'<div>'
        f'<div style="font-size:20px;font-weight:bold;color:#FFD700;">'
        f'{venus.phase_name_cn}</div>'
        f'<div style="font-size:13px;color:#d4b896;margin:4px 0;">'
        f'{venus.phase_name_en}</div>'
        f'<div style="font-size:12px;color:#888;">'
        f'金星離角：{venus.elongation:.1f}° &nbsp;|&nbsp; '
        f'金星黃經：{venus.venus_longitude:.2f}°</div>'
        f'</div></div>'
        f'<div style="margin-top:12px;font-size:13px;color:#d4b896;line-height:1.7;">'
        f'{venus.phase_meaning_cn}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("#### 📊 金星 584 天週期圖")
    _render_venus_cycle_chart(venus)

    # Venus and Tzolk'in connection
    st.markdown("---")
    st.markdown("#### 🌀 金星在 Tzolk'in 中的位置")
    v_sign = TZOLKIN_DAY_DATA[int(venus.venus_longitude / DEGREES_PER_TZOLKIN_SIGN) % 20]
    st.markdown(
        f'<div style="background:#1a1a00;border:1px solid #c8a800;'
        f'border-radius:10px;padding:14px;color:white;">'
        f'<div style="font-size:24px;text-align:center;">{v_sign["glyph_emoji"]}</div>'
        f'<div style="font-size:16px;font-weight:bold;text-align:center;color:#FFD700;">'
        f'金星所在日符號：{v_sign["name"]} {v_sign["name_cn"]}</div>'
        f'<div style="font-size:12px;color:#aaa;text-align:center;">'
        f'{v_sign["element_cn"]} · {v_sign["direction_cn"]} · {v_sign["deity_cn"]}</div>'
        f'<div style="font-size:13px;color:#d4b896;margin-top:8px;line-height:1.6;">'
        f'{v_sign["personality_cn"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.info(
        "🌟 **瑪雅金星知識**\n\n"
        "瑪雅天文學家精確計算了金星的 584 天會合週期，誤差僅在幾秒以內。\n\n"
        "5 個金星週期 = 8 個太陽年 = 2920 天（每 8 年金星回到相同的黃道位置）。\n\n"
        "金星作為晨星升起時，瑪雅人會發動戰爭，因為此時是戰神顯現之刻。"
    )


def _render_venus_cycle_chart(venus) -> None:
    """Render a circular Venus synodic cycle diagram using Plotly."""
    try:
        import plotly.graph_objects as go
        import math
    except ImportError:
        st.caption("（需要 plotly 才能顯示金星週期圖）")
        return

    phases = [
        ("晨星\nMorning Star", 263, "#FFD700"),
        ("上合\nSup. Conj.", 50, "#888"),
        ("昏星\nEvening Star", 263, "#FF8C00"),
        ("下合\nInf. Conj.", 8, "#DC143C"),
    ]
    total = sum(p[1] for p in phases)
    values = [p[1] for p in phases]
    labels = [p[0] for p in phases]
    colors = [p[2] for p in phases]

    fig = go.Figure(go.Pie(
        values=values,
        labels=labels,
        marker=dict(colors=colors, line=dict(color="#0a0415", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="white"),
        hole=0.4,
    ))
    fig.update_layout(
        plot_bgcolor="#0a0415",
        paper_bgcolor="#0a0415",
        font=dict(color="#d4b896"),
        showlegend=False,
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        annotations=[dict(
            text=f"584天<br>週期",
            x=0.5, y=0.5,
            font=dict(size=13, color="#FFD700"),
            showarrow=False,
        )],
    )
    st.plotly_chart(fig, width="stretch")


# ============================================================
# Tab 5: 跨系統對照
# ============================================================

def _render_cross_system_tab(chart: MayanChart) -> None:
    st.markdown("#### 🔄 跨系統對照——瑪雅 × 西方占星")

    st.markdown("##### 🪐 行星在 Tzolk'in 的對應位置")

    # Planets table with Tzolk'in mapping
    header_html = """
    <table style="width:100%;border-collapse:collapse;font-size:12px;color:#d4b896;">
    <tr style="background:#1a0a2e;color:#FFD700;">
        <th style="padding:8px;text-align:left;">行星</th>
        <th style="padding:8px;">星座 (西方)</th>
        <th style="padding:8px;">黃經</th>
        <th style="padding:8px;">逆行</th>
        <th style="padding:8px;">Tzolk'in 日符號</th>
        <th style="padding:8px;">元素/方位</th>
    </tr>
    """
    rows = []
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        sign_data = TZOLKIN_DAY_DATA[p.tzolkin_sign_index]
        row = (
            f'<tr style="border-bottom:1px solid #2a1a4a;">'
            f'<td style="padding:8px;color:{color};font-weight:bold;">{p.name}</td>'
            f'<td style="padding:8px;text-align:center;">{p.sign_glyph} {p.sign} ({p.sign_chinese})</td>'
            f'<td style="padding:8px;text-align:center;">{p.sign_degree:.1f}°</td>'
            f'<td style="padding:8px;text-align:center;">{retro}</td>'
            f'<td style="padding:8px;text-align:center;">'
            f'{p.tzolkin_glyph} {p.tzolkin_sign_name} {p.tzolkin_sign_cn}</td>'
            f'<td style="padding:8px;text-align:center;color:#aaa;">'
            f'{sign_data["element_cn"]} · {sign_data["direction_cn"]}</td>'
            f'</tr>'
        )
        rows.append(row)

    st.markdown(
        header_html + "".join(rows) + "</table>",
        unsafe_allow_html=True,
    )

    # Visual planet-sign mapping
    st.markdown("---")
    st.markdown("##### 🌐 行星能量地圖")
    planet_grid = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">'
    for p in chart.planets:
        color = PLANET_COLORS.get(p.name, "#888")
        sign_data = TZOLKIN_DAY_DATA[p.tzolkin_sign_index]
        planet_grid += (
            f'<div style="background:linear-gradient(135deg,{color}22,#0a0415);'
            f'border:1px solid {color}44;border-radius:8px;padding:10px;'
            f'text-align:center;color:white;">'
            f'<div style="font-size:14px;font-weight:bold;color:{color};">{p.name.split()[0]}</div>'
            f'<div style="font-size:20px;">{sign_data["glyph_emoji"]}</div>'
            f'<div style="font-size:10px;color:#bbb;">{sign_data["name"]}</div>'
            f'<div style="font-size:9px;color:#888;">{sign_data["name_cn"]}</div>'
            f'</div>'
        )
    planet_grid += '</div>'
    st.markdown(planet_grid, unsafe_allow_html=True)

    # Summary comparison
    st.markdown("---")
    st.markdown("##### 📊 系統對照摘要")
    sum_col1, sum_col2 = st.columns(2)
    with sum_col1:
        tz = chart.tzolkin
        st.markdown(
            f'<div style="background:#1a0a2e;border:1px solid #6b3a00;'
            f'border-radius:10px;padding:14px;color:white;">'
            f'<div style="font-size:14px;font-weight:bold;color:#FFD700;margin-bottom:8px;">🌀 瑪雅視角</div>'
            f'<div style="font-size:12px;color:#d4b896;line-height:1.8;">'
            f'<b>出生日符號：</b>{tz.glyph_emoji} {tz.number} {tz.sign_name} ({tz.sign_name_cn})<br>'
            f'<b>元素/方位：</b>{tz.element_cn} · {tz.direction_cn}<br>'
            f'<b>守護神祇：</b>{tz.deity_cn}<br>'
            f'<b>神聖數字：</b>{tz.number} ({tz.number_name_cn})<br>'
            f'<b>Long Count：</b><code>{chart.long_count.date_str}</code>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    with sum_col2:
        sun_planet = next((p for p in chart.planets if "Sun" in p.name), None)
        if sun_planet:
            st.markdown(
                f'<div style="background:#0a1a0a;border:1px solid #2e6b2e;'
                f'border-radius:10px;padding:14px;color:white;">'
                f'<div style="font-size:14px;font-weight:bold;color:#FFD700;margin-bottom:8px;">⭐ 西方視角</div>'
                f'<div style="font-size:12px;color:#d4b896;line-height:1.8;">'
                f'<b>太陽星座：</b>{sun_planet.sign_glyph} {sun_planet.sign} ({sun_planet.sign_chinese})<br>'
                f'<b>太陽黃經：</b>{sun_planet.longitude:.2f}°<br>'
                f"<b>Tzolk'in 映射：</b>{sun_planet.tzolkin_glyph} {sun_planet.tzolkin_sign_name}<br>"
                f'<b>出生日期：</b>{chart.year}/{chart.month}/{chart.day}<br>'
                f'<b>Calendar Round：</b>{chart.calendar_round.round_str}'
                f'</div></div>',
                unsafe_allow_html=True,
            )
