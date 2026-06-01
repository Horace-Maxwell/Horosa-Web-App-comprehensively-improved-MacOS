"""
七政四餘排盤渲染模組 (Chart Renderer for Seven Governors and Four Remainders)

使用 Streamlit 元件渲染七政四餘排盤結果。
包含神煞、年限大運、流時對盤等功能。
"""

import math
from datetime import datetime

import streamlit as st
import swisseph as swe

from .calculator import (
    ChartData, format_degree, get_mansion_index_for_degree,
    _normalize_degree, _degree_to_sign_degree, _get_mansion_info,
    _get_mansion_info_for_system,
)
from .constants import (
    PLANET_COLORS, TWELVE_PALACES, TWENTY_EIGHT_MANSIONS,
    TWENTY_EIGHT_MANSIONS_ANCIENT, TWENTY_EIGHT_MANSIONS_LIMING,
    TWELVE_SIGNS_CHINESE, TWELVE_SIGNS_WESTERN, EARTHLY_BRANCHES,
    FIVE_ELEMENTS, ZODIAC_SIGN_ELEMENTS,
)
from .shensha import (
    ShenShaResult, compute_shensha, get_bazi_stems_branches,
    HEAVENLY_STEMS, TWELVE_LIFE_STAGES,
)
from .qizheng_dasha import (
    DashaResult, compute_dasha, PLANET_PERIOD_YEARS, BRANCH_LORD,
)
from .qizheng_transit import TransitData, compute_transit, compute_transit_now
from .zhangguo import ZhangguoResult, PLANET_TO_ZHANGGUO


# Western zodiac 3-letter abbreviations
_WESTERN_ABBR = [
    "Ari", "Tau", "Gem", "Can", "Leo", "Vir",
    "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis",
]

# 五行顏色
_ELEMENT_COLORS = {
    "木": "#228B22", "金": "#FFD700", "土": "#8B4513",
    "日": "#FF4500", "月": "#C0C0C0", "火": "#DC143C", "水": "#4169E1",
}

# 用度/恩用難仇 — 五行生剋對應表（依命度所在二十八宿元素）
# 難=克我者, 仇=我克者, 恩=生我者, 用=我生者
# 日/月 依五行屬性：日=火, 月=水
_YONGDU_MAP = {
    "日": {"恩": "木", "用": "土", "難": "水", "仇": "金"},  # 日=火: 木生火, 火生土, 水克火, 火克金
    "月": {"恩": "金", "用": "木", "難": "土", "仇": "火"},  # 月=水: 金生水, 水生木, 土克水, 水克火
    "木": {"恩": "水", "用": "火", "難": "金", "仇": "土"},  # 水生木, 木生火, 金克木, 木克土
    "火": {"恩": "木", "用": "土", "難": "水", "仇": "金"},  # 木生火, 火生土, 水克火, 火克金
    "土": {"恩": "火", "用": "金", "難": "木", "仇": "水"},  # 火生土, 土生金, 木克土, 土克水
    "金": {"恩": "土", "用": "水", "難": "火", "仇": "木"},  # 土生金, 金生水, 火克金, 金克木
    "水": {"恩": "金", "用": "木", "難": "土", "仇": "火"},  # 金生水, 水生木, 土克水, 水克火
}


def render_chart_info(chart: ChartData):
    """渲染排盤基本資訊"""
    st.subheader("📋 排盤資訊")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**日期：** {chart.year}年{chart.month}月{chart.day}日")
        st.write(f"**時間：** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**時區：** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**地點：** {chart.location_name}")
        st.write(f"**經度：** {chart.longitude:.4f}°")
        st.write(f"**緯度：** {chart.latitude:.4f}°")


def render_planet_table(chart: ChartData):
    """渲染星曜位置表格"""
    st.subheader("⭐ 七政四餘星曜位置")

    # 七政
    st.markdown("#### 七政（日月五星）")
    _render_planet_group(chart.planets[:7])

    # 四餘
    st.markdown("#### 四餘（虛星）")
    _render_planet_group(chart.planets[7:])


def _render_planet_group(planets: list):
    """渲染一組星曜的表格"""
    header = (
        "| 星曜 | 五行 | 黃經 | 星座 | 度數 | 宮五行 "
        "| 星次 | 二十八宿 | 入宿度 | 高度角 | 岐度 | 逆行 |"
    )
    separator = (
        "|:----:|:----:|:----:|:----:|:----:|:------:"
        "|:----:|:--------:|:------:|:------:|:----:|:----:|"
    )
    rows = [header, separator]

    for p in planets:
        retro = "℞" if p.retrograde else ""
        qidu = "⚠" if p.is_qidu else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_styled = f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        alt_val = getattr(p, "altitude", 0.0)
        alt_str = f"{alt_val:+.1f}°"
        rows.append(
            f"| {name_styled} | {p.element} | {format_degree(p.longitude)} "
            f"| {p.sign_western} | {p.sign_degree:.2f}° | {p.sign_element} "
            f"| {p.sign_chinese} | {p.mansion_name} | {p.mansion_degree:.2f}° "
            f"| {alt_str} | {qidu} | {retro} |"
        )

    st.markdown("\n".join(rows), unsafe_allow_html=True)


def render_house_table(chart: ChartData):
    """渲染十二宮位表格"""
    st.subheader("🏛️ 十二宮位")

    header = "| 宮位 | 地支 | 宮頭度數 | 星座 | 星次 | 入宮星曜 |"
    separator = "|:----:|:----:|:--------:|:----:|:----:|:--------:|"
    rows = [header, separator]

    for house in chart.houses:
        planet_str = "、".join(house.planets) if house.planets else "—"
        rows.append(
            f"| {house.name} | {house.branch_name} "
            f"| {format_degree(house.cusp)} "
            f"| {house.sign_western} | {house.sign_chinese} | {planet_str} |"
        )

    st.markdown("\n".join(rows))


def render_chart_grid(chart: ChartData):
    """
    渲染方形排盤圖（傳統中國式方盤）

    以 4×4 格局呈現，外圈 12 格為十二宮位，中央 2×2 合併為命主資訊：

        巳宮  |  午宮  |  未宮  |  申宮
        ------+--------+--------+------
        辰宮  |                  |  酉宮
        ------+  (中央合併格)   +------
        卯宮  |                  |  戌宮
        ------+--------+--------+------
        寅宮  |  丑宮  |  子宮  |  亥宮

    十二宮名稱根據命宮地支和性別方向輪轉到對應的地支位置。
    """
    st.subheader("📊 七政四餘盤")

    # 建立 地支 → 宮位資料 的映射
    branch_data: dict[int, tuple[str, list, str]] = {}
    for house in chart.houses:
        planet_list = house.planets if house.planets else []
        branch_data[house.branch] = (house.name, planet_list, house.sign_western)

    # 計算神煞
    shensha = compute_shensha(
        year=chart.year,
        solar_month=chart.solar_month,
        julian_day=chart.julian_day,
        hour_branch=chart.hour_branch,
        timezone=chart.timezone,
        ming_gong_branch=chart.ming_gong_branch,
    )

    # 方盤排列 (外圈12格，按固定地支位置排列)
    # 格子中的數字是地支索引: 子=0, 丑=1, 寅=2, ..., 亥=11
    grid_order = [
        [5, 6, 7, 8],          # 上排: 巳午未申
        [4, -1, -1, 9],        # 中上: 辰 [中央] 酉
        [3, -1, -1, 10],       # 中下: 卯 [中央] 戌
        [2, 1, 0, 11],         # 下排: 寅丑子亥
    ]

    # 使用 HTML/CSS 渲染方盤
    html = _build_grid_html(chart, branch_data, grid_order, shensha)
    st.html(html)


def _build_grid_html(
    chart: ChartData,
    branch_data: dict,
    grid_order: list,
    shensha: ShenShaResult | None = None,
) -> str:
    """建構排盤 HTML

    Parameters:
        chart: 排盤資料
        branch_data: 地支索引 → (宮名, 星曜列表, 西方星座) 映射
        grid_order: 4×4 格局，值為地支索引 (0-11)，-1 為中央
    """
    cell_style = (
        "border:1px solid #555; padding:6px; text-align:center; "
        "vertical-align:top; font-size:13px; "
        "background:#1a1a2e; color:#e0e0e0;"
    )
    ming_cell_style = (
        "border:2px solid #d4af37; padding:6px; text-align:center; "
        "vertical-align:top; font-size:13px; "
        "background:#2a2a1e; color:#e0e0e0;"
    )
    center_style = (
        "border:1px solid #666; padding:10px; text-align:center; "
        "vertical-align:middle; font-size:14px; background:#2a2a3e; "
        "color:#e0e0e0;"
    )

    gender_label = "男命" if chart.gender == "male" else "女命"
    direction_label = "順時針" if chart.gender == "male" else "逆時針"

    html = (
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
        '<table style="border-collapse:collapse; margin:auto; width:100%; '
        'table-layout:fixed; background:#1a1a2e; color:#e0e0e0;">'
    )

    for row_idx, row in enumerate(grid_order):
        html += "<tr>"
        col_idx = 0
        while col_idx < len(row):
            branch_idx = row[col_idx]
            if branch_idx == -1:
                # 中央區域（只在第一次遇到時渲染）
                if row_idx == 1 and col_idx == 1:
                    branch_name = EARTHLY_BRANCHES[chart.ming_gong_branch]
                    center_content = (
                        f"<b>七政四餘排盤</b><br/>"
                        f"{chart.year}年{chart.month}月{chart.day}日<br/>"
                        f"{chart.hour:02d}:{chart.minute:02d} "
                        f"UTC{chart.timezone:+.1f}<br/>"
                        f"{chart.location_name} ({gender_label})<br/>"
                        f"命宮: {branch_name} ({direction_label})<br/>"
                        f"命度: {format_degree(chart.ascendant)}<br/>"
                        f"中天: {format_degree(chart.midheaven)}"
                    )
                    html += (
                        f'<td colspan="2" rowspan="2" '
                        f'style="{center_style}">{center_content}</td>'
                    )
                    col_idx += 2
                    continue
                else:
                    col_idx += 1
                    continue
            else:
                is_ming = (branch_idx == chart.ming_gong_branch)
                style = ming_cell_style if is_ming else cell_style
                branch_label = EARTHLY_BRANCHES[branch_idx]
                if branch_idx in branch_data:
                    name, planets, sign = branch_data[branch_idx]
                    planets_html = ""
                    for p_name in planets:
                        color = PLANET_COLORS.get(p_name, "#c8c8c8")
                        planets_html += (
                            f'<span style="color:{color};font-weight:bold">'
                            f'{p_name}</span> '
                        )
                    if not planets_html:
                        planets_html = '<span style="color:#999">—</span>'
                    ming_mark = "【命】" if is_ming else ""
                    # 神煞
                    sha_html = ""
                    if shensha and branch_idx in shensha.branch_map:
                        sha_names = shensha.branch_map[branch_idx]
                        sha_parts = []
                        for sn in sha_names:
                            cat = "中"
                            for item in shensha.items:
                                if item.name == sn and item.branch == branch_idx:
                                    cat = item.category
                                    break
                            sc = ("#4caf50" if cat == "吉"
                                  else "#ef5350" if cat == "凶"
                                  else "#ffc107")
                            if sn in TWELVE_LIFE_STAGES:
                                sc = "#90caf9"
                            sha_parts.append(
                                f'<span style="color:{sc};font-size:10px">'
                                f'{sn}</span>'
                            )
                        sha_html = (
                            '<br/><span style="font-size:10px">'
                            + " ".join(sha_parts) + '</span>'
                        )
                    cell_content = (
                        f'<small style="color:#888">{branch_label}</small> '
                        f'<b>{name}</b>'
                        f'<span style="color:#d4af37">{ming_mark}</span>'
                        f"<br/>"
                        f'<small style="color:#888">{sign}</small><br/>'
                        f"{planets_html}"
                        f"{sha_html}"
                    )
                else:
                    cell_content = f'<small style="color:#888">{branch_label}</small>'
                html += f'<td style="{style}">{cell_content}</td>'
            col_idx += 1
        html += "</tr>"

    html += "</table></div>"
    return html


def render_aspect_summary(chart: ChartData):
    """渲染星曜相位摘要"""
    st.subheader("🔗 主要相位")

    aspects = _calculate_aspects(chart.planets)
    if not aspects:
        st.info("無顯著相位")
        return

    header = "| 星曜 1 | 相位 | 星曜 2 | 角距 |"
    separator = "|:------:|:----:|:------:|:----:|"
    rows = [header, separator]

    for a in aspects:
        rows.append(
            f"| {a['planet1']} | {a['aspect_name']} | {a['planet2']} "
            f"| {a['orb']:.1f}° |"
        )

    st.markdown("\n".join(rows))


def _calculate_aspects(planets: list) -> list:
    """計算星曜之間的主要相位"""
    aspect_types = [
        {"name": "合(0°)", "angle": 0, "orb": 8},
        {"name": "沖(180°)", "angle": 180, "orb": 8},
        {"name": "刑(90°)", "angle": 90, "orb": 6},
        {"name": "三合(120°)", "angle": 120, "orb": 6},
        {"name": "六合(60°)", "angle": 60, "orb": 4},
    ]

    aspects = []
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1 = planets[i]
            p2 = planets[j]
            diff = abs(p1.longitude - p2.longitude)
            if diff > 180:
                diff = 360 - diff

            for asp in aspect_types:
                orb = abs(diff - asp["angle"])
                if orb <= asp["orb"]:
                    aspects.append({
                        "planet1": p1.name,
                        "planet2": p2.name,
                        "aspect_name": asp["name"],
                        "orb": orb,
                    })
                    break

    return aspects


# ============================================================
# 八字四柱 (Four Pillars / Ba Zi)
# ============================================================

def render_bazi(chart: ChartData):
    """渲染八字四柱"""
    bazi = get_bazi_stems_branches(
        year=chart.year,
        solar_month=chart.solar_month,
        julian_day=chart.julian_day,
        hour_branch=chart.hour_branch,
        timezone=chart.timezone,
    )
    st.subheader("📜 八字四柱")
    header = "| 柱 | 天干 | 地支 | 干支 |"
    sep = "|:----:|:----:|:----:|:----:|"
    rows = [header, sep]
    for label, key_prefix in [("年柱", "year"), ("月柱", "month"),
                              ("日柱", "day"), ("時柱", "hour")]:
        s = HEAVENLY_STEMS[bazi[f"{key_prefix}_stem"]]
        b = EARTHLY_BRANCHES[bazi[f"{key_prefix}_branch"]]
        rows.append(f"| {label} | {s} | {b} | {bazi[f'{key_prefix}_pillar']} |")
    st.markdown("\n".join(rows))
    return bazi


# ============================================================
# 神煞 (Shen Sha / Divine Stars)
# ============================================================

def render_shensha(chart: ChartData, shensha: ShenShaResult):
    """渲染神煞表格（按宮位分組）"""
    st.subheader("🔮 神煞")

    # 按吉凶分色
    ji_color = "#4caf50"
    xiong_color = "#ef5350"
    zhong_color = "#ffc107"

    header = "| 地支 | 宮位 | 神煞 |"
    sep = "|:----:|:----:|:-----|"
    rows = [header, sep]

    branch_to_palace = {}
    for h in chart.houses:
        branch_to_palace[h.branch] = h.name

    for branch_idx in range(12):
        branch_name = EARTHLY_BRANCHES[branch_idx]
        palace = branch_to_palace.get(branch_idx, "")
        sha_names = shensha.branch_map.get(branch_idx, [])
        if sha_names:
            # Color-code by category
            styled = []
            for sname in sha_names:
                # Find category
                cat = "中"
                for item in shensha.items:
                    if item.name == sname and item.branch == branch_idx:
                        cat = item.category
                        break
                color = ji_color if cat == "吉" else xiong_color if cat == "凶" else zhong_color
                if sname in TWELVE_LIFE_STAGES:
                    color = "#90caf9"
                styled.append(
                    f'<span style="color:{color}">{sname}</span>'
                )
            sha_str = " ".join(styled)
        else:
            sha_str = "—"
        rows.append(f"| {branch_name} | {palace} | {sha_str} |")

    st.markdown("\n".join(rows), unsafe_allow_html=True)

    # Legend
    st.caption(
        f'<span style="color:{ji_color}">■ 吉星</span> '
        f'<span style="color:{xiong_color}">■ 凶煞</span> '
        f'<span style="color:{zhong_color}">■ 中性</span> '
        f'<span style="color:#90caf9">■ 十二長生</span>',
        unsafe_allow_html=True,
    )


# ============================================================
# 年限大運 (Planetary Period / Dasha)
# ============================================================

def render_dasha(chart: ChartData, dasha: DashaResult):
    """渲染年限大運表"""
    st.subheader("📅 年限大運")

    # 當前大運高亮
    if dasha.current_period_idx >= 0 and dasha.current_age >= 0:
        p = dasha.periods[dasha.current_period_idx]
        st.info(
            f"📍 現年 **{dasha.current_age}歲** — "
            f"行 **{p.palace_name}** ({p.branch_name}) 限 "
            f"({p.start_age}–{p.end_age}歲 / "
            f"{p.start_year}–{p.end_year}年)，"
            f"主星 **{p.lord}** ({PLANET_PERIOD_YEARS[p.lord]}年)"
        )

    if dasha.flow_year_branch >= 0:
        st.success(
            f"🗓️ 流年太歲: **{EARTHLY_BRANCHES[dasha.flow_year_branch]}** "
            f"→ **{dasha.flow_year_palace}**"
        )

    header = "| # | 宮位 | 地支 | 主星 | 年限 | 起始歲 | 結束歲 | 起始年 | 結束年 |"
    sep = "|:--:|:----:|:----:|:----:|:----:|:------:|:------:|:------:|:------:|"
    rows = [header, sep]

    for idx, p in enumerate(dasha.periods):
        mark = " 👈" if idx == dasha.current_period_idx else ""
        rows.append(
            f"| {idx+1} | {p.palace_name} | {p.branch_name} "
            f"| {p.lord} | {p.years} | {p.start_age} | {p.end_age} "
            f"| {p.start_year} | {p.end_year} |{mark}"
        )

    st.markdown("\n".join(rows))


# ============================================================
# 流時對盤 (Transit Chart Comparison)
# ============================================================

def render_transit_comparison(chart: ChartData, transit: TransitData):
    """渲染流時對盤（本命 vs 流時星曜位置對照表）"""
    st.subheader("🔄 流時對盤")
    st.caption(
        f"流時: {transit.year}年{transit.month}月{transit.day}日 "
        f"{transit.hour:02d}:{transit.minute:02d} UTC{transit.timezone:+.1f}"
    )

    header = "| 星曜 | 本命黃經 | 本命星座 | 流時黃經 | 流時星座 | 差距 |"
    sep = "|:----:|:--------:|:--------:|:--------:|:--------:|:----:|"
    rows = [header, sep]

    for np, tp in zip(chart.planets, transit.planets):
        diff = abs(np.longitude - tp.longitude)
        if diff > 180:
            diff = 360 - diff
        n_retro = "℞" if np.retrograde else ""
        t_retro = "℞" if tp.retrograde else ""
        color = PLANET_COLORS.get(np.name, "#c8c8c8")
        name_styled = f'<span style="color:{color};font-weight:bold">{np.name}</span>'
        rows.append(
            f"| {name_styled} "
            f"| {format_degree(np.longitude)}{n_retro} | {np.sign_chinese} "
            f"| {format_degree(tp.longitude)}{t_retro} | {tp.sign_chinese} "
            f"| {diff:.1f}° |"
        )

    st.markdown("\n".join(rows), unsafe_allow_html=True)


# ============================================================
# 二十八宿圓環圖 (28 Lunar Mansions Ring Chart)
# ============================================================

# 四象顏色 (Four Symbols / Directional Colors)
_GROUP_COLORS = {
    "東方青龍": ("#1a3a1a", "#4caf50"),   # (background, text/border) green
    "北方玄武": ("#1a1a3a", "#5c6bc0"),   # blue/indigo
    "西方白虎": ("#3a3a1a", "#e0e0e0"),   # white/light
    "南方朱雀": ("#3a1a1a", "#ef5350"),   # red
}


def _compute_sun_moon_rise_set(jd, lat, lon, tz):
    """Compute sunrise, sunset, moonrise, moonset using swisseph."""
    swe.set_ephe_path("")
    geopos = (lon, lat, 0.0)  # (longitude, latitude, altitude)
    results = {}
    for name, body, flag in [
        ("sunrise", swe.SUN, swe.CALC_RISE),
        ("sunset", swe.SUN, swe.CALC_SET),
        ("moonrise", swe.MOON, swe.CALC_RISE),
        ("moonset", swe.MOON, swe.CALC_SET),
    ]:
        try:
            res = swe.rise_trans(
                jd, body, flag | swe.BIT_DISC_CENTER,
                geopos, 0.0, 0.0,
            )
            rise_jd = res[1][0]
            y, m, d, h = swe.revjul(rise_jd + tz / 24.0)
            hour_val = h
            hh = int(hour_val)
            mm = int((hour_val - hh) * 60)
            results[name] = f"{hh:02d}:{mm:02d}"
        except Exception:
            results[name] = "--:--"
    return results


def _is_night_birth(chart: ChartData):
    """Determine if birth is at night (between sunset and sunrise)."""
    try:
        times = _compute_sun_moon_rise_set(
            chart.julian_day, chart.latitude, chart.longitude, chart.timezone,
        )
        birth_minutes = chart.hour * 60 + chart.minute
        # Parse sunrise/sunset
        sr_parts = times["sunrise"].split(":")
        ss_parts = times["sunset"].split(":")
        if "--" in times["sunrise"] or "--" in times["sunset"]:
            return chart.hour < 6 or chart.hour >= 18
        sr_min = int(sr_parts[0]) * 60 + int(sr_parts[1])
        ss_min = int(ss_parts[0]) * 60 + int(ss_parts[1])
        return birth_minutes < sr_min or birth_minutes >= ss_min
    except Exception:
        return chart.hour < 6 or chart.hour >= 18


def _to_chinese_numeral(n: int) -> str:
    """Convert integer 0-99 to Chinese numeral string (e.g. 8 → 八, 11 → 十一).

    Input is clamped to the range [0, 99].
    """
    UNITS = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    n = max(0, min(n, 99))
    if n == 0:
        return "零"
    if n < 10:
        return UNITS[n]
    if n == 10:
        return "十"
    tens, ones = divmod(n, 10)
    if ones == 0:
        return UNITS[tens] + "十"
    if tens == 1:
        return "十" + UNITS[ones]
    return UNITS[tens] + "十" + UNITS[ones]


def _format_liming_mansion(ascendant: float, mansion_list: list) -> str:
    """Format 立命 in classical style: 宿名+元素+度數(中文)+度立命.

    Degree within the mansion is rounded to the nearest integer following
    traditional Chinese astronomy notation (入宿幾度).
    Examples: 參水八度立命, 井木十一度立命
    """
    name, deg, idx, _ = _get_mansion_info_for_system(ascendant, mansion_list)
    element = mansion_list[idx]["element"]
    degree_cn = _to_chinese_numeral(round(deg))
    return f"{name}{element}{degree_cn}度立命"


def render_mansion_ring(chart: ChartData, transit: TransitData | None = None):
    """渲染二十八宿圓環圖 — 以 SVG 圓盤呈現完整七政四餘盤

    Enhanced version matching aizhanxing.com reference:
    - Dasha year ring (outermost) with year markers
    - Shensha ring
    - 28 Mansions ring with element + animal labels
    - 12 Chinese zodiac stations with Western abbreviations
    - 12 Palace Names ring
    - Degree tick marks
    - Planet positions with degree labels
    - Aspect lines in center
    - Transit overlay ring
    - 八字 display, sunrise/sunset info
    """
    st.subheader("🌕 七政四餘圓盤")

    # Compute shensha for the chart
    shensha = compute_shensha(
        year=chart.year,
        solar_month=chart.solar_month,
        julian_day=chart.julian_day,
        hour_branch=chart.hour_branch,
        timezone=chart.timezone,
        ming_gong_branch=chart.ming_gong_branch,
    )

    # Compute dasha for year ring
    current_year = datetime.now().year
    dasha = compute_dasha(
        birth_year=chart.year,
        ming_gong_branch=chart.ming_gong_branch,
        gender=chart.gender,
        houses=chart.houses,
        current_year=current_year,
    )

    # Compute bazi
    bazi = get_bazi_stems_branches(
        year=chart.year,
        solar_month=chart.solar_month,
        julian_day=chart.julian_day,
        hour_branch=chart.hour_branch,
        timezone=chart.timezone,
    )

    # Compute sun/moon rise/set
    sun_moon_times = _compute_sun_moon_rise_set(
        chart.julian_day, chart.latitude, chart.longitude, chart.timezone,
    )
    is_night = _is_night_birth(chart)

    SIZE = 960
    CX, CY = SIZE / 2, SIZE / 2

    # Concentric ring radii (from outside in)
    R_DASHA_OUT = 468      # 大運年環外沿
    R_DASHA_IN = 435       # 大運年環內沿
    R_SHENSHA_OUT = 435    # 神煞環外沿
    R_SHENSHA_IN = 395     # 神煞環內沿
    R_MANSION_OUT = 395    # 28 宿環外沿
    R_MANSION_IN = 355     # 28 宿環內沿
    R_SIGN_OUT = 355       # 十二星次環外沿
    R_SIGN_IN = 320        # 十二星次環內沿
    R_PALACE_OUT = 320     # 十二宮名環外沿
    R_PALACE_IN = 285      # 十二宮名環內沿
    R_DEGREE_OUT = 285     # 度數刻度環外沿
    R_DEGREE_IN = 275      # 度數刻度環內沿
    R_PLANET = 240         # 星曜環 (natal)
    R_TRANSIT = 175        # 流時星曜環
    R_CENTER = 130         # 中央圓

    NUM_MANSIONS = len(TWENTY_EIGHT_MANSIONS)
    PLANET_SPREAD_FACTOR = 0.7

    def _mansion_width(i):
        s = TWENTY_EIGHT_MANSIONS[i]["start_lon"]
        e = TWENTY_EIGHT_MANSIONS[(i + 1) % NUM_MANSIONS]["start_lon"]
        return (e - s) % 360.0

    def _mansion_chart_start(i):
        e = TWENTY_EIGHT_MANSIONS[(i + 1) % NUM_MANSIONS]["start_lon"]
        return ecl_to_chart(e)

    def polar(r, angle_deg):
        rad = math.radians(angle_deg)
        return CX + r * math.cos(rad), CY + r * math.sin(rad)

    def annular_sector(r_in, r_out, a1, a2):
        """SVG path for an annular sector (donut slice)."""
        a1r, a2r = math.radians(a1), math.radians(a2)
        x1o = CX + r_out * math.cos(a1r)
        y1o = CY + r_out * math.sin(a1r)
        x2o = CX + r_out * math.cos(a2r)
        y2o = CY + r_out * math.sin(a2r)
        x1i = CX + r_in * math.cos(a2r)
        y1i = CY + r_in * math.sin(a2r)
        x2i = CX + r_in * math.cos(a1r)
        y2i = CY + r_in * math.sin(a1r)
        sweep = a2 - a1
        large = 1 if sweep > 180 else 0
        return (
            f"M {x1o:.1f},{y1o:.1f} "
            f"A {r_out},{r_out} 0 {large},1 {x2o:.1f},{y2o:.1f} "
            f"L {x1i:.1f},{y1i:.1f} "
            f"A {r_in},{r_in} 0 {large},0 {x2i:.1f},{y2i:.1f} Z"
        )

    def ecl_to_chart(ecl_deg):
        """Convert ecliptic longitude to SVG chart angle.

        午(South) at top, 子(North) at bottom.
        """
        return (45.0 - ecl_deg) % 360.0

    def text_rotation(a):
        rot = (a + 90) % 360
        if 90 < rot < 270:
            rot = (rot + 180) % 360
        return rot

    svg = []
    svg.append(
        f'<svg viewBox="0 0 {SIZE} {SIZE}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%; max-width:960px; height:auto; margin:auto; '
        f'display:block; background:#0a0a1a; border-radius:12px;">'
    )
    svg.append(f'<rect width="{SIZE}" height="{SIZE}" fill="#0a0a1a" rx="12"/>')

    # === 大運年環 (Dasha year ring — outermost) ===
    for idx, period in enumerate(dasha.periods):
        # Map dasha palace branch to chart angle
        branch = period.branch
        sign_idx = (10 - branch) % 12
        a1 = ecl_to_chart((sign_idx + 1) * 30.0)
        a2 = a1 + 30.0
        is_current = (idx == dasha.current_period_idx)
        bg_fill = "#2a1a2a" if is_current else "#0d0d18"
        stroke_col = "#d4af37" if is_current else "#333"
        stroke_w = "1.5" if is_current else "0.5"
        svg.append(
            f'<path d="{annular_sector(R_DASHA_IN, R_DASHA_OUT, a1, a2)}" '
            f'fill="{bg_fill}" stroke="{stroke_col}" stroke-width="{stroke_w}"/>'
        )
        # Year label at center of sector
        mid_a = a1 + 15.0
        r_text = (R_DASHA_IN + R_DASHA_OUT) / 2
        x, y = polar(r_text, mid_a)
        rot = text_rotation(mid_a)
        year_label = str(period.start_year)
        text_fill = "#d4af37" if is_current else "#888"
        svg.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{text_fill}" '
            f'font-size="10" font-family="sans-serif" '
            f'transform="rotate({rot:.1f},{x:.1f},{y:.1f})">'
            f'{year_label}</text>'
        )

    # === 神煞環 (Shen Sha ring) ===
    for i in range(12):
        a1 = ecl_to_chart((i + 1) * 30.0)
        a2 = a1 + 30.0
        branch_idx = (10 - i) % 12
        svg.append(
            f'<path d="{annular_sector(R_SHENSHA_IN, R_SHENSHA_OUT, a1, a2)}" '
            f'fill="#0d0d1a" stroke="#333" stroke-width="0.5"/>'
        )
        sha_names = shensha.branch_map.get(branch_idx, [])
        if sha_names:
            display_names = sha_names[:6]
            mid_a = a1 + 15.0
            r_text = (R_SHENSHA_IN + R_SHENSHA_OUT) / 2
            n_rows = (len(display_names) + 2) // 3
            for row_i in range(n_rows):
                row_names = display_names[row_i * 3: (row_i + 1) * 3]
                offset = (row_i - (n_rows - 1) / 2) * 10
                r_adj = r_text + offset
                x, y = polar(r_adj, mid_a)
                rot = text_rotation(mid_a)
                txt = " ".join(row_names)
                svg.append(
                    f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
                    f'dominant-baseline="central" fill="#c0a0a0" '
                    f'font-size="7.5" font-family="serif" '
                    f'transform="rotate({rot:.1f},{x:.1f},{y:.1f})">'
                    f'{txt}</text>'
                )

    # === 28 宿環 (Mansion ring) with element + animal ===
    for i, m in enumerate(TWENTY_EIGHT_MANSIONS):
        w = _mansion_width(i)
        a1 = _mansion_chart_start(i)
        a2 = a1 + w
        bg, fg = _GROUP_COLORS[m["group"]]
        svg.append(
            f'<path d="{annular_sector(R_MANSION_IN, R_MANSION_OUT, a1, a2)}" '
            f'fill="{bg}" stroke="#555" stroke-width="0.5"/>'
        )
        mid_a = a1 + w / 2
        r_text_name = (R_MANSION_IN + R_MANSION_OUT) / 2 + 5
        r_text_elem = (R_MANSION_IN + R_MANSION_OUT) / 2 - 8
        x, y = polar(r_text_name, mid_a)
        rot = text_rotation(mid_a)
        # Mansion name
        svg.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{fg}" '
            f'font-size="12" font-weight="bold" font-family="serif" '
            f'transform="rotate({rot:.1f},{x:.1f},{y:.1f})">'
            f'{m["name"]}</text>'
        )
        # Element + animal label (smaller, below name)
        elem_color = _ELEMENT_COLORS.get(m["element"], "#999")
        x2, y2 = polar(r_text_elem, mid_a)
        svg.append(
            f'<text x="{x2:.1f}" y="{y2:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{elem_color}" '
            f'font-size="8" font-family="serif" '
            f'transform="rotate({rot:.1f},{x2:.1f},{y2:.1f})">'
            f'{m["element"]}{m["animal"]}</text>'
        )

    # === 十二星次環 (12 Chinese zodiac + Western abbreviation) ===
    for i in range(12):
        a1 = ecl_to_chart((i + 1) * 30.0)
        a2 = a1 + 30.0
        svg.append(
            f'<path d="{annular_sector(R_SIGN_IN, R_SIGN_OUT, a1, a2)}" '
            f'fill="#111122" stroke="#444" stroke-width="0.5"/>'
        )
        mid_a = a1 + 15.0
        # Chinese name (upper row)
        sign_name = TWELVE_SIGNS_CHINESE[i]
        short_name = sign_name.split("(")[0] if "(" in sign_name else sign_name
        r_text_cn = (R_SIGN_IN + R_SIGN_OUT) / 2 + 5
        x, y = polar(r_text_cn, mid_a)
        rot = text_rotation(mid_a)
        svg.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#b0b0d0" '
            f'font-size="12" font-weight="bold" font-family="serif" '
            f'transform="rotate({rot:.1f},{x:.1f},{y:.1f})">'
            f'{short_name}</text>'
        )
        # Western abbreviation (lower row)
        r_text_w = (R_SIGN_IN + R_SIGN_OUT) / 2 - 8
        x2, y2 = polar(r_text_w, mid_a)
        svg.append(
            f'<text x="{x2:.1f}" y="{y2:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#808090" '
            f'font-size="9" font-family="sans-serif" '
            f'transform="rotate({rot:.1f},{x2:.1f},{y2:.1f})">'
            f'{_WESTERN_ABBR[i]}</text>'
        )

    # === 十二宮名環 (12 Palace Names ring) ===
    branch_to_palace: dict[int, str] = {}
    for house in chart.houses:
        branch_to_palace[house.branch] = house.name

    for i in range(12):
        a1 = ecl_to_chart((i + 1) * 30.0)
        a2 = a1 + 30.0
        branch_idx = (10 - i) % 12
        is_ming = (branch_idx == chart.ming_gong_branch)
        bg_fill = "#2a2a1e" if is_ming else "#0f0f22"
        stroke_col = "#d4af37" if is_ming else "#444"
        stroke_w = "1" if is_ming else "0.5"
        svg.append(
            f'<path d="{annular_sector(R_PALACE_IN, R_PALACE_OUT, a1, a2)}" '
            f'fill="{bg_fill}" stroke="{stroke_col}" stroke-width="{stroke_w}"/>'
        )
        mid_a = a1 + 15.0
        # Palace name (top row)
        r_text = (R_PALACE_IN + R_PALACE_OUT) / 2 + 5
        x, y = polar(r_text, mid_a)
        rot = text_rotation(mid_a)
        palace_name = branch_to_palace.get(branch_idx, "")
        short_palace = palace_name.replace("宮", "") if palace_name else ""
        text_color = "#d4af37" if is_ming else "#c8b888"
        svg.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{text_color}" '
            f'font-size="11" font-weight="bold" font-family="serif" '
            f'transform="rotate({rot:.1f},{x:.1f},{y:.1f})">'
            f'{short_palace}</text>'
        )
        # Branch name + lord (bottom row)
        r_text2 = (R_PALACE_IN + R_PALACE_OUT) / 2 - 8
        x2, y2 = polar(r_text2, mid_a)
        branch_name = EARTHLY_BRANCHES[branch_idx]
        lord = BRANCH_LORD.get(branch_idx, "")
        svg.append(
            f'<text x="{x2:.1f}" y="{y2:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#808080" '
            f'font-size="8" font-family="serif" '
            f'transform="rotate({rot:.1f},{x2:.1f},{y2:.1f})">'
            f'{branch_name}·{lord}</text>'
        )

    # === 度數刻度 (Degree tick marks) ===
    for deg in range(360):
        a = ecl_to_chart(float(deg))
        if deg % 10 == 0:
            x1, y1 = polar(R_DEGREE_IN - 2, a)
            x2, y2 = polar(R_DEGREE_OUT, a)
            svg.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
                f'x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="#666" stroke-width="0.8"/>'
            )
        elif deg % 5 == 0:
            x1, y1 = polar(R_DEGREE_IN, a)
            x2, y2 = polar(R_DEGREE_OUT, a)
            svg.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
                f'x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="#555" stroke-width="0.5"/>'
            )

    # === Division lines for 12 signs ===
    for i in range(12):
        a = ecl_to_chart(i * 30.0)
        x1, y1 = polar(R_CENTER, a)
        x2, y2 = polar(R_DASHA_OUT, a)
        svg.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#555" stroke-width="0.8"/>'
        )

    # === 28 宿分界線 ===
    for i in range(28):
        a = ecl_to_chart(TWENTY_EIGHT_MANSIONS[i]["start_lon"])
        x1, y1 = polar(R_MANSION_IN, a)
        x2, y2 = polar(R_MANSION_OUT, a)
        svg.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#555" stroke-width="0.5"/>'
        )

    # === Inner circles ===
    svg.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_CENTER}" '
        f'fill="#1a1a2e" stroke="#555" stroke-width="1"/>'
    )

    # === 星曜位置 (natal planet positions) with degree labels ===
    mansion_planets: dict[int, list] = {}
    for p in chart.planets:
        lon = _normalize_degree(p.longitude)
        mansion_idx = get_mansion_index_for_degree(lon)
        if mansion_idx not in mansion_planets:
            mansion_planets[mansion_idx] = []
        mansion_planets[mansion_idx].append((p, lon))

    # Collect planet positions for aspect lines
    planet_angles = {}

    for mansion_idx, planet_data in mansion_planets.items():
        n = len(planet_data)
        w = _mansion_width(mansion_idx)
        a1_chart = _mansion_chart_start(mansion_idx)
        base_a = a1_chart + w / 2
        for pi, (p, lon) in enumerate(planet_data):
            if n == 1:
                a = ecl_to_chart(lon)
            else:
                span = w * PLANET_SPREAD_FACTOR
                a = base_a - span / 2 + span * pi / (n - 1)

            planet_angles[p.name] = a
            color = PLANET_COLORS.get(p.name, "#c8c8c8")
            x, y = polar(R_PLANET, a)

            # Planet dot
            svg.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" '
                f'fill="{color}" stroke="#fff" stroke-width="0.5"/>'
            )
            # Planet name + element
            x_t, y_t = polar(R_PLANET - 18, a)
            rot = text_rotation(a)
            retro = "℞" if p.retrograde else ""
            elem = FIVE_ELEMENTS.get(p.name, "")
            svg.append(
                f'<text x="{x_t:.1f}" y="{y_t:.1f}" text-anchor="middle" '
                f'dominant-baseline="central" fill="{color}" '
                f'font-size="10" font-weight="bold" font-family="serif" '
                f'transform="rotate({rot:.1f},{x_t:.1f},{y_t:.1f})">'
                f'{elem}·{p.name}{retro}</text>'
            )
            # Degree label
            deg_str = f"{_degree_to_sign_degree(lon):.1f}°"
            x_d, y_d = polar(R_PLANET + 15, a)
            svg.append(
                f'<text x="{x_d:.1f}" y="{y_d:.1f}" text-anchor="middle" '
                f'dominant-baseline="central" fill="{color}" '
                f'font-size="7" font-family="sans-serif" opacity="0.7" '
                f'transform="rotate({rot:.1f},{x_d:.1f},{y_d:.1f})">'
                f'{deg_str}</text>'
            )

    # === Aspect lines between planets (in center) ===
    aspects = _calculate_aspects(chart.planets)
    aspect_colors = {
        "合(0°)": "#FFD700",
        "沖(180°)": "#FF4444",
        "刑(90°)": "#FF8800",
        "三合(120°)": "#44FF44",
        "六合(60°)": "#4488FF",
    }
    for asp in aspects:
        p1_name = asp["planet1"]
        p2_name = asp["planet2"]
        if p1_name in planet_angles and p2_name in planet_angles:
            a1 = planet_angles[p1_name]
            a2 = planet_angles[p2_name]
            x1, y1 = polar(R_CENTER + 5, a1)
            x2, y2 = polar(R_CENTER + 5, a2)
            asp_color = aspect_colors.get(asp["aspect_name"], "#666")
            opacity = "0.3" if asp["orb"] > 4 else "0.5"
            svg.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
                f'x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{asp_color}" stroke-width="0.8" opacity="{opacity}"/>'
            )

    # === 流時星曜環 (transit planet positions) ===
    if transit is not None:
        svg.append(
            f'<circle cx="{CX}" cy="{CY}" r="{R_TRANSIT + 25}" '
            f'fill="none" stroke="#444" stroke-width="0.5" stroke-dasharray="4,4"/>'
        )
        t_mansion_planets: dict[int, list] = {}
        for p in transit.planets:
            lon = _normalize_degree(p.longitude)
            mansion_idx = get_mansion_index_for_degree(lon)
            if mansion_idx not in t_mansion_planets:
                t_mansion_planets[mansion_idx] = []
            t_mansion_planets[mansion_idx].append((p, lon))

        for mansion_idx, planet_data in t_mansion_planets.items():
            n = len(planet_data)
            w = _mansion_width(mansion_idx)
            a1_chart = _mansion_chart_start(mansion_idx)
            base_a = a1_chart + w / 2
            for pi, (p, lon) in enumerate(planet_data):
                if n == 1:
                    a = ecl_to_chart(lon)
                else:
                    span = w * PLANET_SPREAD_FACTOR
                    a = base_a - span / 2 + span * pi / (n - 1)

                color = PLANET_COLORS.get(p.name, "#c8c8c8")
                x, y = polar(R_TRANSIT, a)

                svg.append(
                    f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" '
                    f'fill="none" stroke="{color}" stroke-width="1.5"/>'
                )
                x_t, y_t = polar(R_TRANSIT - 16, a)
                rot = text_rotation(a)
                retro = "℞" if p.retrograde else ""
                svg.append(
                    f'<text x="{x_t:.1f}" y="{y_t:.1f}" text-anchor="middle" '
                    f'dominant-baseline="central" fill="{color}" '
                    f'font-size="9" font-family="serif" opacity="0.8" '
                    f'transform="rotate({rot:.1f},{x_t:.1f},{y_t:.1f})">'
                    f'{p.name}{retro}</text>'
                )

    # === 中央資訊 (center info) ===
    gender_label = "男命" if chart.gender == "male" else "女命"
    direction_label = "順至日出" if chart.gender == "male" else "逆至日出"
    ming_branch = EARTHLY_BRANCHES[chart.ming_gong_branch]
    svg.append(
        f'<text x="{CX}" y="{CY - 55}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#e0e0e0" '
        f'font-size="14" font-weight="bold" font-family="serif">'
        f'七政四餘</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY - 35}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#b0b0b0" '
        f'font-size="11" font-family="serif">'
        f'{chart.year}年{chart.month}月{chart.day}日 '
        f'{chart.hour:02d}:{chart.minute:02d}</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY - 18}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#b0b0b0" '
        f'font-size="10" font-family="serif">'
        f'{chart.location_name} ({gender_label})</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#d4af37" '
        f'font-size="10" font-family="serif">'
        f'命宮 {ming_branch} ({direction_label})</text>'
    )

    # 立命度數 — 今制 and 古制 mansion format (e.g. 參水八度立命 / 井木十一度立命)
    liming_modern = _format_liming_mansion(chart.liming_lon, TWENTY_EIGHT_MANSIONS_LIMING)
    liming_ancient = _format_liming_mansion(chart.liming_lon, TWENTY_EIGHT_MANSIONS_ANCIENT)
    svg.append(
        f'<text x="{CX}" y="{CY + 16}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#d4af37" '
        f'font-size="12" font-weight="bold" font-family="serif">'
        f'今：{liming_modern}</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY + 32}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#c8a060" '
        f'font-size="10" font-family="serif">'
        f'古：{liming_ancient}</text>'
    )
    svg.append(
        f'<text x="{CX}" y="{CY + 48}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#7ec8e3" '
        f'font-size="10" font-family="serif">'
        f'中天 {format_degree(chart.midheaven)}</text>'
    )

    # Dasha current period
    if dasha.current_period_idx >= 0:
        cp = dasha.periods[dasha.current_period_idx]
        svg.append(
            f'<text x="{CX}" y="{CY + 64}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#a080c0" '
            f'font-size="9" font-family="serif">'
            f'行限 {cp.palace_name} '
            f'({cp.start_age}-{cp.start_age + cp.years}歲)</text>'
        )

    svg.append(
        f'<text x="{CX}" y="{CY + 80}" text-anchor="middle" '
        f'dominant-baseline="central" fill="#888" '
        f'font-size="9" font-family="serif">'
        f'UTC{chart.timezone:+.1f}</text>'
    )

    # === 八字顯示 (Four Pillars — top-left corner) ===
    bazi_x = 15
    bazi_y = 18
    # Bazi: year, month, day, hour stems on top, branches on bottom
    pillars = [
        (bazi["year_pillar"], "年"),
        (bazi["month_pillar"], "月"),
        (bazi["day_pillar"], "日"),
        (bazi["hour_pillar"], "時"),
    ]
    for pi_idx, (pillar, label) in enumerate(pillars):
        px = bazi_x + pi_idx * 30
        stem_char = pillar[0]
        branch_char = pillar[1]
        svg.append(
            f'<text x="{px}" y="{bazi_y}" fill="#e0e0e0" '
            f'font-size="13" font-weight="bold" font-family="serif">'
            f'{stem_char}</text>'
        )
        svg.append(
            f'<text x="{px}" y="{bazi_y + 18}" fill="#c8b888" '
            f'font-size="13" font-weight="bold" font-family="serif">'
            f'{branch_char}</text>'
        )

    # 乾/坤 label for gender
    qk_label = "乾" if chart.gender == "male" else "坤"
    svg.append(
        f'<text x="{bazi_x + len(pillars) * 30}" y="{bazi_y + 9}" '
        f'fill="#d4af37" font-size="14" font-weight="bold" font-family="serif">'
        f'{qk_label}</text>'
    )

    # === 晝夜/日出日落 (bottom-left corner) ===
    night_label = "夜生" if is_night else "晝生"
    info_x = 15
    info_y = SIZE - 70
    svg.append(
        f'<text x="{info_x}" y="{info_y}" fill="#e0e0e0" '
        f'font-size="12" font-weight="bold" font-family="serif">'
        f'{night_label}</text>'
    )
    svg.append(
        f'<text x="{info_x}" y="{info_y + 18}" fill="#b0b0b0" '
        f'font-size="10" font-family="serif">'
        f'日出: {sun_moon_times.get("sunrise", "--:--")}  '
        f'日落: {sun_moon_times.get("sunset", "--:--")}</text>'
    )
    svg.append(
        f'<text x="{info_x}" y="{info_y + 34}" fill="#b0b0b0" '
        f'font-size="10" font-family="serif">'
        f'月出: {sun_moon_times.get("moonrise", "--:--")}  '
        f'月落: {sun_moon_times.get("moonset", "--:--")}</text>'
    )

    # === 用度恩仇 (bottom-right corner) ===
    # Show which elements are favourable/unfavourable based on the mansion element
    # at the 命宮 cusp position (二十八宿元素法)
    ming_element = ""
    for h in chart.houses:
        if h.branch == chart.ming_gong_branch:
            mansion_name, mansion_deg, mansion_idx, mansion_width = _get_mansion_info(h.cusp)
            ming_element = TWENTY_EIGHT_MANSIONS[mansion_idx]["element"]
            break

    if ming_element and ming_element in _YONGDU_MAP:
        yd = _YONGDU_MAP[ming_element]
        yd_x = SIZE - 150
        yd_y = SIZE - 55
        svg.append(
            f'<text x="{yd_x}" y="{yd_y}" fill="#b0b0b0" '
            f'font-size="9" font-family="serif">'
            f'難{yd["難"]}仇{yd["仇"]}用{yd["用"]}</text>'
        )
        svg.append(
            f'<text x="{yd_x}" y="{yd_y + 14}" fill="#b0b0b0" '
            f'font-size="9" font-family="serif">'
            f'恩{yd["恩"]} 度{ming_element}</text>'
        )

    # === 立命/安身 annotations (bottom-right) ===
    br_x = SIZE - 150
    br_y = SIZE - 25
    svg.append(
        f'<text x="{br_x}" y="{br_y}" fill="#d4af37" '
        f'font-size="10" font-weight="bold" font-family="serif">'
        f'立命 {direction_label}</text>'
    )

    svg.append("</svg>")

    svg_string = "\n".join(svg)
    st.markdown(svg_string, unsafe_allow_html=True)
    return svg_string


def render_chart_info_panel(chart: ChartData, transit: TransitData | None = None):
    """渲染右側資訊面板 — 包含基礎、本命、行運等分頁資訊

    Matches the reference aizhanxing.com info panel with tabs.
    """

    # Compute dependencies
    bazi = get_bazi_stems_branches(
        year=chart.year,
        solar_month=chart.solar_month,
        julian_day=chart.julian_day,
        hour_branch=chart.hour_branch,
        timezone=chart.timezone,
    )
    current_year = datetime.now().year
    dasha = compute_dasha(
        birth_year=chart.year,
        ming_gong_branch=chart.ming_gong_branch,
        gender=chart.gender,
        houses=chart.houses,
        current_year=current_year,
    )
    sun_moon_times = _compute_sun_moon_rise_set(
        chart.julian_day, chart.latitude, chart.longitude, chart.timezone,
    )
    is_night = _is_night_birth(chart)

    # Lunar date approximation from bazi
    lunar_year_pillar = bazi["year_pillar"]
    lunar_month_branch = EARTHLY_BRANCHES[bazi["month_branch"]]
    hour_branch_name = EARTHLY_BRANCHES[chart.hour_branch]
    night_day = "夜" if is_night else "晝"
    gender_label = "男命" if chart.gender == "male" else "女命"

    # Tabs
    tab_base, tab_natal, tab_transit, tab_dasha_tab = st.tabs(
        ["基礎", "本命", "行運", "大運"]
    )

    with tab_base:
        st.markdown("#### 本命信息")
        st.markdown(
            f"- **農曆：** {lunar_year_pillar}年 · {hour_branch_name}時（{night_day}）\n"
            f"- **生日：** {chart.year}-{chart.month:02d}-{chart.day:02d} "
            f"{chart.hour:02d}:{chart.minute:02d}:00\n"
            f"- **時區：** UTC{chart.timezone:+.1f}\n"
            f"- **地點：** {chart.location_name}\n"
            f"- **性別：** {gender_label}\n"
        )

        # 八字
        st.markdown("#### 八字四柱")
        bazi_str = (
            f"年柱 {bazi['year_pillar']} · "
            f"月柱 {bazi['month_pillar']} · "
            f"日柱 {bazi['day_pillar']} · "
            f"時柱 {bazi['hour_pillar']}"
        )
        st.markdown(f"- {bazi_str}")

        # 立命/安身
        ming_branch = EARTHLY_BRANCHES[chart.ming_gong_branch]
        ming_mansion = ""
        ming_degree = 0.0
        ming_mansion, ming_degree, _, _ = _get_mansion_info(chart.liming_lon)
        st.markdown(
            f"- **立命：** {ming_branch} {format_degree(chart.ascendant)} · "
            f"{ming_mansion} {ming_degree:.2f}°\n"
            f"- **中天：** {format_degree(chart.midheaven)}"
        )

        # Sunrise/sunset
        st.markdown(
            f"- **{night_day}生** — "
            f"日出 {sun_moon_times.get('sunrise', '--:--')} · "
            f"日落 {sun_moon_times.get('sunset', '--:--')} · "
            f"月出 {sun_moon_times.get('moonrise', '--:--')} · "
            f"月落 {sun_moon_times.get('moonset', '--:--')}"
        )

    with tab_natal:
        st.markdown("#### 七政位置")
        for p in chart.planets[:7]:
            color = PLANET_COLORS.get(p.name, "#c8c8c8")
            retro = " ℞" if p.retrograde else ""
            qidu = " ⚠岐度" if p.is_qidu else ""
            alt_val = getattr(p, "altitude", 0.0)
            alt_str = f" **{alt_val:+.1f}°**"
            st.markdown(
                f'<span style="color:{color};font-weight:bold">{p.name}</span> '
                f'{p.sign_chinese} {p.sign_degree:.2f}° · '
                f'{p.mansion_name} {p.mansion_degree:.2f}°'
                f'{retro}{qidu}{alt_str}',
                unsafe_allow_html=True,
            )

        st.markdown("#### 四餘位置")
        for p in chart.planets[7:]:
            color = PLANET_COLORS.get(p.name, "#c8c8c8")
            retro = " ℞" if p.retrograde else ""
            alt_val = getattr(p, "altitude", 0.0)
            alt_str = f" **{alt_val:+.1f}°**"
            st.markdown(
                f'<span style="color:{color};font-weight:bold">{p.name}</span> '
                f'{p.sign_chinese} {p.sign_degree:.2f}° · '
                f'{p.mansion_name} {p.mansion_degree:.2f}°{retro}{alt_str}',
                unsafe_allow_html=True,
            )

        st.markdown("#### 十二宮位")
        for house in chart.houses:
            planet_str = "、".join(house.planets) if house.planets else "—"
            is_ming = house.name == "命宮"
            marker = " 🟡" if is_ming else ""
            st.markdown(
                f"**{house.name}**{marker} ({house.branch_name}) · "
                f"{house.sign_chinese} · {planet_str}"
            )

    with tab_transit:
        if transit is not None:
            st.markdown("#### 行運信息")
            st.markdown(
                f"- **流時：** {transit.year}-{transit.month:02d}-{transit.day:02d} "
                f"{transit.hour:02d}:{transit.minute:02d}"
            )
            st.markdown("#### 流時星曜")
            for np_item, tp in zip(chart.planets, transit.planets):
                diff = abs(np_item.longitude - tp.longitude)
                if diff > 180:
                    diff = 360 - diff
                color = PLANET_COLORS.get(np_item.name, "#c8c8c8")
                t_retro = " ℞" if tp.retrograde else ""
                st.markdown(
                    f'<span style="color:{color};font-weight:bold">{np_item.name}'
                    f'</span> 本命 {format_degree(np_item.longitude)} → '
                    f'流時 {format_degree(tp.longitude)}{t_retro} '
                    f'(差距 {diff:.1f}°)',
                    unsafe_allow_html=True,
                )
        else:
            st.info("勾選「顯示流時對盤」以查看行運資訊")

    with tab_dasha_tab:
        st.markdown("#### 年限大運")
        if dasha.current_period_idx >= 0:
            cp = dasha.periods[dasha.current_period_idx]
            st.success(
                f"📍 現年 **{dasha.current_age}歲** — "
                f"行 **{cp.palace_name}** ({cp.branch_name}) 限 "
                f"({cp.start_age}–{cp.end_age}歲)"
            )
        for idx, p in enumerate(dasha.periods):
            mark = " 👈" if idx == dasha.current_period_idx else ""
            st.markdown(
                f"{idx+1}. **{p.palace_name}** ({p.branch_name}) · "
                f"{p.lord} {p.years}年 · "
                f"{p.start_age}–{p.end_age}歲 "
                f"({p.start_year}–{p.end_year}){mark}"
            )


def render_full_chart(chart: ChartData, transit: TransitData | None = None):
    """渲染完整的七政四餘盤 — 圓盤 + 右側資訊面板

    Layout: Left column (chart SVG) + Right column (info panel)
    Matches the aizhanxing.com reference layout.
    """
    col_chart, col_info = st.columns([3, 2])

    with col_chart:
        render_mansion_ring(chart, transit=transit)

    with col_info:
        render_chart_info_panel(chart, transit=transit)


# ============================================================
# 張果星宗 (Zhang Guo Xing Zong Star Readings)
# ============================================================

def render_zhangguo(chart: ChartData, result: ZhangguoResult):
    """渲染張果星宗斷語與格局。"""
    st.subheader("📜 張果星宗")

    # --- 1. 星曜落宮斷語 ---
    readings = result.matched_readings
    if readings:
        st.markdown(f"**十一曜宮位斷語** — 共匹配 {len(readings)} 條")

        # Group by star
        from collections import OrderedDict
        grouped: dict[str, list] = OrderedDict()
        for r in readings:
            key = f"{r.star}（{r.branch}宮）"
            grouped.setdefault(key, []).append(r)

        ji_color = "#4caf50"
        ji_bg = "#1b3a1b"
        xiong_color = "#ef5350"
        xiong_bg = "#3a1a1a"

        for star_key, items in grouped.items():
            first_is_ji = items[0].reading_type == "合格"
            with st.expander(f"{'🟢' if first_is_ji else '🔴'} {star_key}  ({len(items)}條)", expanded=False):
                for r in items:
                    is_ji = r.reading_type == "合格"
                    color = ji_color if is_ji else xiong_color
                    bg = ji_bg if is_ji else xiong_bg
                    badge = f'<span style="color:white;background:{color};padding:1px 6px;border-radius:3px;font-size:0.8em">{r.reading_type}</span>'
                    note_tag = f' <span style="color:#bbb;font-size:0.85em">({r.note})</span>' if r.note else ""
                    gender_tag = ""
                    if r.gender == "male":
                        gender_tag = ' <span style="color:#42a5f5;font-size:0.8em">♂男命</span>'
                    elif r.gender == "female":
                        gender_tag = ' <span style="color:#ec407a;font-size:0.8em">♀女命</span>'
                    st.markdown(
                        f'<div style="background:{bg};color:#fff;padding:8px 12px;border-radius:6px;margin:4px 0">'
                        f'{badge}{gender_tag}{note_tag}<br/>'
                        f'<span style="font-size:0.95em">{r.description}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
    else:
        st.info("此命盤暫無匹配的張果星宗宮位斷語。")

    st.divider()

    # --- 2. 格局總表 ---
    patterns = result.all_patterns
    if patterns:
        st.markdown("**格局總表** — 張果星宗十一曜定格·諸格·八格賦")

        # Group patterns by category
        cat_order = []
        cat_map: dict[str, list] = {}
        for p in patterns:
            if p.category not in cat_map:
                cat_order.append(p.category)
                cat_map[p.category] = []
            cat_map[p.category].append(p)

        for cat in cat_order:
            items = cat_map[cat]
            with st.expander(f"📋 {cat}（{len(items)}格）", expanded=False):
                header = "| # | 格名 | 類型 | 條件 | 說明 |"
                sep = "|:--:|:-----|:----:|:-----|:-----|"
                rows = [header, sep]
                for p in items:
                    ptype_color = "#4caf50" if p.pattern_type == "合格" else (
                        "#ef5350" if p.pattern_type == "忌格" else "#ffc107"
                    )
                    ptype_html = f'<span style="color:{ptype_color}">{p.pattern_type}</span>'
                    rows.append(
                        f"| {p.pattern_id} | {p.name} | {ptype_html} | {p.condition} | {p.note} |"
                    )
                st.markdown("\n".join(rows), unsafe_allow_html=True)


# ============================================================
# 命宮特徵解讀 (Life Palace Interpretations from 七政.txt)
# ============================================================

_MING_GONG_INDEX = 0  # palace_index of 命宮 is always 0

def render_ming_gong_interpretations(chart: ChartData):
    """渲染命宮特徵文字描述（依七政.txt）。

    顯示兩類解讀：
    1. 立命X宮 — 命宮所在地支的推命文字
    2. X入本命宮 — 各星曜入命宮的文字描述
    """
    from .ming_gong_interp import get_li_ming_text, get_planet_in_ming_text

    st.subheader("🔮 命宮特徵解讀")

    ming_house = chart.houses[_MING_GONG_INDEX]
    branch_char = ming_house.branch_name  # e.g. "子", "丑", …
    planets_in_ming = ming_house.planets  # list of planet name strings

    # ── 1. 立命X宮 ─────────────────────────────────────────────────────────
    li_ming_text = get_li_ming_text(branch_char)
    if li_ming_text:
        with st.expander(f"📖 立命{branch_char}宮（推命文字）", expanded=True):
            st.markdown(li_ming_text)

    # ── 2. 星曜入命宮 ──────────────────────────────────────────────────────
    if planets_in_ming:
        st.markdown(
            f"**命宮（{branch_char}宮）入宮星曜：** {'、'.join(planets_in_ming)}"
        )
        for planet_name in planets_in_ming:
            text = get_planet_in_ming_text(planet_name)
            if text:
                with st.expander(f"⭐ {planet_name}入本命宮", expanded=True):
                    st.markdown(text)
    else:
        st.info("命宮無入宮星曜。")


# ============================================================
# 二十八宿文字顯示 (Twenty-Eight Mansions Text Display)
# ============================================================

# 黃道宮索引 (0=白羊/戌) → 地支索引
_SIGN_IDX_TO_BRANCH = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 11]
# 地支名稱
_BRANCHES_DISPLAY = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def _ecl_to_mansion_text(lon: float) -> str:
    """
    將黃經度數轉換為七政四餘傳統文字格式。

    例如: 33.79° → '03酉金47'24'
    格式: [sign_deg:02d][branch][sign_elem][arc_min:02d]'[arc_sec:02d]

    Returns:
        格式化字串，如 '03酉金47'24'
    """
    lon = _normalize_degree(lon)
    sign_idx = int(lon / 30.0)
    sign_deg_float = lon - sign_idx * 30.0
    branch_idx = _SIGN_IDX_TO_BRANCH[sign_idx]
    branch_name = _BRANCHES_DISPLAY[branch_idx]
    sign_elem = ZODIAC_SIGN_ELEMENTS[sign_idx]

    deg_int = int(sign_deg_float)
    remaining = (sign_deg_float - deg_int) * 60.0
    arc_min = int(remaining)
    arc_sec = round((remaining - arc_min) * 60.0)
    if arc_sec == 60:
        arc_sec = 0
        arc_min += 1
    if arc_min == 60:
        arc_min = 0
        deg_int += 1
    if deg_int >= 30:
        deg_int = 0

    return f"{deg_int:02d}{branch_name}{sign_elem}{arc_min:02d}'{arc_sec:02d}"


def _build_mansion_boundary_text(mansion_list: list) -> str:
    """
    為指定宿界列表建立28宿位置文字，格式類似 MOIRA 輸出：
    婁金: 03酉金47'24  胃土: 16酉金45'39  ...（每行4宿）
    """
    lines = []
    items = []
    for m in mansion_list:
        lon = m["start_lon"]
        pos_text = _ecl_to_mansion_text(lon)
        items.append(f"{m['name']}{m['element']}: {pos_text}")

    # Output 4 mansions per line
    for i in range(0, len(items), 4):
        lines.append("  ".join(items[i:i + 4]))
    return "\n".join(lines)


def _build_planet_mansion_rows(chart: ChartData, mansion_list: list) -> list[dict]:
    """
    計算每顆星曜在指定宿界制下的入宿位置，
    返回 list of dict with keys: name, element, mansion, mansion_deg_text, sign_text, altitude, retrograde
    """
    rows = []
    # Build a lookup dict for fast mansion start_lon and element access
    mansion_lookup: dict[str, tuple[float, str]] = {
        m["name"]: (m["start_lon"], m["element"]) for m in mansion_list
    }
    for p in chart.planets:
        lon = _normalize_degree(p.longitude)
        mansion_name, mansion_deg, _, _ = _get_mansion_info_for_system(lon, mansion_list)

        mansion_start_lon, mansion_elem = mansion_lookup.get(mansion_name, (lon, ""))
        sign_text = _ecl_to_mansion_text(lon)
        mansion_deg_text = _ecl_to_mansion_text(mansion_start_lon + mansion_deg) if mansion_name else sign_text

        rows.append({
            "name": p.name,
            "element": p.element,
            "mansion": mansion_name,
            "mansion_elem": mansion_elem,
            "mansion_deg_text": mansion_deg_text,
            "sign_text": sign_text,
            "altitude": getattr(p, "altitude", 0.0),
            "retrograde": p.retrograde,
        })
    return rows


def render_mansion_text_panel(chart: ChartData):
    """渲染二十八宿文字內容面板 — 以今制和古制分頁顯示。

    顯示內容：
    1. 28宿宿界位置（以傳統中文格式）
    2. 各星曜所在宿及入宿度（今制 / 古制）
    """
    st.subheader("🌟 二十八宿宿界與星曜入宿")

    tab_modern, tab_ancient = st.tabs(["今制", "古制"])

    for tab, mansion_list, label in [
        (tab_modern, TWENTY_EIGHT_MANSIONS_LIMING, "今制"),
        (tab_ancient, TWENTY_EIGHT_MANSIONS_ANCIENT, "古制"),
    ]:
        with tab:
            st.markdown(f"**{label}二十八宿宿界（距星黃經）**")
            boundary_text = _build_mansion_boundary_text(mansion_list)
            st.code(boundary_text, language=None)

            st.markdown(f"**{label}各星曜入宿位置**")
            rows = _build_planet_mansion_rows(chart, mansion_list)

            header = "| 星曜 | 五行 | 入宿 | 宿元素 | 入宿度 | 黃道位置 | 高度角 | 逆行 |"
            sep = "|:----:|:----:|:----:|:------:|:------:|:--------:|:------:|:----:|"
            md_rows = [header, sep]
            for r in rows:
                color = PLANET_COLORS.get(r["name"], "#c8c8c8")
                name_html = (
                    f'<span style="color:{color};font-weight:bold">{r["name"]}</span>'
                )
                retro = "℞" if r["retrograde"] else ""
                alt_str = f'{r["altitude"]:+.1f}°'
                md_rows.append(
                    f"| {name_html} | {r['element']} | {r['mansion']} "
                    f"| {r['mansion_elem']} | {r['mansion_deg_text']} "
                    f"| {r['sign_text']} | {alt_str} | {retro} |"
                )
            st.markdown("\n".join(md_rows), unsafe_allow_html=True)

