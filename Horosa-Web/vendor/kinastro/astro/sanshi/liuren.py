"""
astro/sanshi/liuren.py — 大六壬排盤模組 (Da Liu Ren Divination Module)

大六壬為古代三式之一，以日干支及月將為基礎，
排列天地盤、四課、三傳，推斷吉凶。

此模組封裝 kinliuren 庫，提供 compute / render 介面。
"""

from __future__ import annotations

import sxtwl
import streamlit as st

from astro.i18n import t, auto_cn

# ============================================================
# 常量
# ============================================================

TIANGAN = list("甲乙丙丁戊己庚辛壬癸")
DIZHI = list("子丑寅卯辰巳午未申酉戌亥")

# 天將顏色（用於盤式著色）— 柔和典雅風格
JIANG_COLORS: dict[str, str] = {
    "貴": "#F0C674",  # 柔金
    "蛇": "#CC6666",  # 暗紅
    "雀": "#DE935F",  # 橘褐
    "合": "#7EB889",  # 翠綠
    "勾": "#A1887F",  # 赭褐
    "龍": "#5DADE2",  # 天藍
    "空": "#95A5A6",  # 灰色
    "虎": "#D5D8DC",  # 銀白
    "常": "#FFAB40",  # 琥珀
    "玄": "#7986CB",  # 靛青
    "陰": "#B39DDB",  # 藤紫
    "后": "#F06292",  # 玫紅
}

# 天將全名
JIANG_FULLNAME: dict[str, str] = {
    "貴": "貴人", "蛇": "騰蛇", "雀": "朱雀", "合": "六合",
    "勾": "勾陳", "龍": "青龍", "空": "天空", "虎": "白虎",
    "常": "太常", "玄": "玄武", "陰": "太陰", "后": "天后",
}

# 六親簡稱顏色 — 淡雅明亮、與天將色系分離
LIUQIN_COLORS: dict[str, str] = {
    "父": "#81D4FA",  # 淺天藍
    "財": "#80CBC4",  # 碧綠
    "官": "#EF9A9A",  # 淺珊瑚
    "兄": "#FFF176",  # 鵝黃
    "子": "#CE93D8",  # 淺藍紫
}

# 十二宮名稱
TWELVE_PALACES: list[str] = [
    "命宮", "兄弟", "夫妻", "子女",
    "財帛", "疾厄", "遷移", "奴僕",
    "官祿", "田宅", "福德", "相貌",
]

# 24 節氣名（sxtwl 的索引順序，index 0 = 冬至）
JIEQI_NAMES = [
    "冬至", "小寒", "大寒", "立春", "雨水", "驚蟄",
    "春分", "清明", "穀雨", "立夏", "小滿", "芒種",
    "夏至", "小暑", "大暑", "立秋", "處暑", "白露",
    "秋分", "寒露", "霜降", "立冬", "小雪", "大雪",
]

# 月份中文名（正月 ~ 十二月）
CHINESE_MONTHS = list("正二三四五六七八九十") + ["十一", "十二"]


def _get_jieqi(year: int, month: int, day: int) -> str:
    """根據公曆日期推算當前所在節氣。"""
    try:
        d = sxtwl.fromSolar(year, month, day)
        # 若當天剛好是節氣日，直接返回
        if d.hasJieQi():
            jq_idx = d.getJieQi()
            if 0 <= jq_idx < 24:
                return JIEQI_NAMES[jq_idx]
        # 往前逐日搜尋最近的節氣（最多回溯 45 天）
        for offset in range(1, 46):
            check_day = d.before(offset)
            if check_day.hasJieQi():
                jq_idx = check_day.getJieQi()
                if 0 <= jq_idx < 24:
                    return JIEQI_NAMES[jq_idx]
    except Exception:
        pass
    # 最後兜底：按月份粗略對應
    month_jieqi = {
        1: "小寒", 2: "立春", 3: "驚蟄", 4: "清明",
        5: "立夏", 6: "芒種", 7: "小暑", 8: "立秋",
        9: "白露", 10: "寒露", 11: "立冬", 12: "大雪",
    }
    return month_jieqi.get(month, "小寒")


def _get_gangzhi(year: int, month: int, day: int, hour: int) -> dict:
    """取得年月日時干支。"""
    d = sxtwl.fromSolar(year, month, day)
    gz_day = d.getDayGZ()

    day_tg = gz_day.tg
    day_dz = gz_day.dz
    day_gz = TIANGAN[day_tg] + DIZHI[day_dz]

    # 時干支
    hour_zhi_idx = ((hour + 1) // 2) % 12
    hour_tg = (day_tg * 2 + hour_zhi_idx) % 10
    hour_gz = TIANGAN[hour_tg] + DIZHI[hour_zhi_idx]

    # 農曆月
    lunar_month = d.getLunarMonth()

    return {
        "day_gz": day_gz,
        "hour_gz": hour_gz,
        "lunar_month": lunar_month,
    }


@st.cache_data(ttl=3600, show_spinner=False)
def compute_liuren_chart(
    year: int, month: int, day: int,
    hour: int, minute: int,
    timezone: float = 8.0,
    **kwargs,
) -> dict:
    """計算大六壬排盤。

    Returns
    -------
    dict
        包含三傳、四課、天地盤、格局等完整排盤資訊。
    """
    from astro.sanshi.kinliuren.kinliuren import Liuren

    gz = _get_gangzhi(year, month, day, hour)
    jieqi = _get_jieqi(year, month, day)
    lunar_month_str = CHINESE_MONTHS[gz["lunar_month"] - 1] if 1 <= gz["lunar_month"] <= 12 else "正"

    lr = Liuren(jieqi, lunar_month_str, gz["day_gz"], gz["hour_gz"])
    result = lr.result(0)
    result["_jieqi"] = jieqi
    result["_lunar_month"] = lunar_month_str
    result["_day_gz"] = gz["day_gz"]
    result["_hour_gz"] = gz["hour_gz"]
    return result


def _liuqin_label(ri_gan: str, target_zhi: str) -> str:
    """以日干為主，求 *target_zhi* 地支的六親簡稱。

    Parameters
    ----------
    ri_gan : str
        日干（如 ``'壬'``）。
    target_zhi : str
        待判定六親的地支（如 ``'午'``）。

    Returns
    -------
    str
        六親簡稱：``'父'``/``'財'``/``'官'``/``'兄'``/``'子'``，
        若無法判定則回傳空字串。
    """
    GANZHI_WX = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火",
        "戊": "土", "己": "土", "庚": "金", "辛": "金",
        "壬": "水", "癸": "水",
        "子": "水", "丑": "土", "寅": "木", "卯": "木",
        "辰": "土", "巳": "火", "午": "火", "未": "土",
        "申": "金", "酉": "金", "戌": "土", "亥": "水",
    }
    WX_SHENGKE = {
        ("木", "火"): "生", ("火", "土"): "生", ("土", "金"): "生",
        ("金", "水"): "生", ("水", "木"): "生",
        ("木", "土"): "剋", ("土", "水"): "剋", ("水", "火"): "剋",
        ("火", "金"): "剋", ("金", "木"): "剋",
        ("火", "木"): "被生", ("土", "火"): "被生", ("金", "土"): "被生",
        ("水", "金"): "被生", ("木", "水"): "被生",
        ("土", "木"): "被剋", ("水", "土"): "被剋", ("火", "水"): "被剋",
        ("金", "火"): "被剋", ("木", "金"): "被剋",
    }
    LQ = {"生": "子", "剋": "財", "被生": "父", "被剋": "官", "比和": "兄"}
    wa = GANZHI_WX.get(ri_gan, "")
    wb = GANZHI_WX.get(target_zhi, "")
    if wa == wb:
        return "兄"
    rel = WX_SHENGKE.get((wa, wb), "")
    return LQ.get(rel, "")


def _build_liuren_board_html(
    chart: dict,
    benming_zhi: str | None = None,
) -> str:
    """產生傳統六壬盤式 HTML（方盤 + 四課三傳 + 十二宮）。

    Parameters
    ----------
    chart : dict
        ``compute_liuren_chart()`` 的回傳值，需包含
        ``地轉天盤``、``地轉天將``、``三傳``、``四課`` 等鍵。
    benming_zhi : str, optional
        本命地支（如 ``'寅'``），若提供則在各位置標註十二宮宮名。

    Returns
    -------
    str
        可嵌入 ``streamlit.components.v1.html()`` 的 HTML 字串。
    """
    di_to_tian = chart.get("地轉天盤", {})
    di_to_jiang = chart.get("地轉天將", {})
    san_chuan = chart.get("三傳", {})
    si_ke = chart.get("四課", {})
    day_gz = chart.get("_day_gz", chart.get("日期", "")[:2])
    ri_gan = day_gz[0] if day_gz else ""

    # 十二宮映射: 地支 → 宮名
    palace_map: dict[str, str] = {}
    if benming_zhi and benming_zhi in DIZHI:
        start = DIZHI.index(benming_zhi)
        for i, pname in enumerate(TWELVE_PALACES):
            palace_map[DIZHI[(start + i) % 12]] = pname

    # 方盤位置 (4×4 外框，中間空心)
    # 行列安排：
    #   (0,0)=巳 (0,1)=午 (0,2)=未 (0,3)=申
    #   (1,0)=辰                   (1,3)=酉
    #   (2,0)=卯                   (2,3)=戌
    #   (3,0)=寅 (3,1)=丑 (3,2)=子 (3,3)=亥
    GRID: list[list[str | None]] = [
        ["巳", "午", "未", "申"],
        ["辰", None, None, "酉"],
        ["卯", None, None, "戌"],
        ["寅", "丑", "子", "亥"],
    ]

    def _cell(branch: str) -> str:
        """產生單一地盤位置的 HTML。"""
        tian = di_to_tian.get(branch, "")
        jiang = di_to_jiang.get(branch, "")
        jiang_full = JIANG_FULLNAME.get(jiang, jiang)
        jcolor = JIANG_COLORS.get(jiang, "#CCC")
        lq = _liuqin_label(ri_gan, tian) if ri_gan else ""
        lq_color = LIUQIN_COLORS.get(lq, "#CCC")
        palace = palace_map.get(branch, "")

        palace_html = (
            f'<div style="font-size:10px;color:#9E9E9E;line-height:1.2;'
            f'letter-spacing:1px;">{palace}</div>'
            if palace else ""
        )
        lq_html = (
            f'<span style="color:{lq_color};font-size:12px;font-weight:600;">'
            f'{lq}</span>'
            if lq else ""
        )

        return (
            f'<td style="border:1px solid rgba(120,120,140,0.35);'
            f'text-align:center;vertical-align:middle;'
            f'padding:6px 4px;'
            f'background:rgba(30,30,45,0.45);">'
            f'{palace_html}'
            f'<div style="color:{jcolor};font-size:12px;line-height:1.4;'
            f'opacity:0.85;">{jiang_full}</div>'
            f'<div style="font-size:16px;font-weight:bold;line-height:1.4;'
            f'color:#E8E8F0;">'
            f'{tian}&thinsp;{lq_html}</div>'
            f'<div style="border-top:1px dashed rgba(120,120,140,0.4);'
            f'margin:2px 8px;"></div>'
            f'<div style="font-size:14px;color:#9E9E9E;line-height:1.4;">'
            f'{branch}</div>'
            f'</td>'
        )

    # ── 四課 HTML（顯示在中央上方）──
    si_ke_names = ["四課", "三課", "二課", "一課"]
    sk_rows_top = ""   # 上面一行：天盤支
    sk_rows_btm = ""   # 下面一行：地盤支 / 日干
    sk_rows_jiang = ""  # 天將
    sk_rows_lq = ""     # 六親
    for name in si_ke_names:
        vals = si_ke.get(name, [])
        pair = vals[0] if len(vals) > 0 else ""
        jiang = vals[1] if len(vals) > 1 else ""
        top_char = pair[0] if len(pair) > 0 else ""
        btm_char = pair[1] if len(pair) > 1 else ""
        jcolor = JIANG_COLORS.get(jiang, "#CCC")
        lq = _liuqin_label(ri_gan, top_char) if ri_gan and top_char else ""
        lq_color = LIUQIN_COLORS.get(lq, "#CCC")
        sk_rows_jiang += (
            f'<td style="text-align:center;padding:2px 8px;'
            f'color:{jcolor};font-size:12px;opacity:0.85;">{jiang}</td>'
        )
        sk_rows_lq += (
            f'<td style="text-align:center;padding:2px 8px;'
            f'color:{lq_color};font-size:12px;font-weight:600;">{lq}</td>'
        )
        sk_rows_top += (
            f'<td style="text-align:center;padding:2px 8px;'
            f'font-size:15px;color:#E8E8F0;">{top_char}</td>'
        )
        sk_rows_btm += (
            f'<td style="text-align:center;padding:2px 8px;'
            f'font-size:14px;color:#9E9E9E;">{btm_char}</td>'
        )

    si_ke_html = (
        f'<table style="margin:auto;border-collapse:collapse;">'
        f'<tr><td colspan="4" style="text-align:center;font-size:11px;'
        f'color:#9E9E9E;padding-bottom:4px;letter-spacing:2px;">'
        f'{auto_cn("四課")}</td></tr>'
        f'<tr>{sk_rows_jiang}</tr>'
        f'<tr>{sk_rows_lq}</tr>'
        f'<tr>{sk_rows_top}</tr>'
        f'<tr>{sk_rows_btm}</tr>'
        f'</table>'
    )

    # ── 三傳 HTML（顯示在中央下方）──
    sc_html_rows = ""
    for name in ("初傳", "中傳", "末傳"):
        vals = san_chuan.get(name, [])
        zhi = vals[0] if len(vals) > 0 else ""
        jiang = vals[1] if len(vals) > 1 else ""
        lq_raw = vals[2] if len(vals) > 2 else ""
        kong = vals[3] if len(vals) > 3 else ""
        jcolor = JIANG_COLORS.get(jiang, "#CCC")
        lq_color = LIUQIN_COLORS.get(lq_raw, "#CCC")
        kong_mark = (
            '<span style="color:#EF9A9A;font-size:10px;'
            'border:1px solid rgba(239,154,154,0.4);border-radius:3px;'
            'padding:0 2px;">空</span>'
            if kong == "空" else ""
        )
        sc_html_rows += (
            f'<tr>'
            f'<td style="font-size:11px;color:#9E9E9E;padding:2px 6px;">'
            f'{auto_cn(name)}</td>'
            f'<td style="font-size:15px;padding:2px 6px;color:#E8E8F0;'
            f'font-weight:bold;">{zhi}</td>'
            f'<td style="color:{jcolor};font-size:12px;padding:2px 6px;'
            f'opacity:0.85;">{jiang}</td>'
            f'<td style="color:{lq_color};font-size:12px;padding:2px 6px;'
            f'font-weight:600;">{lq_raw}</td>'
            f'<td style="padding:2px 4px;">{kong_mark}</td>'
            f'</tr>'
        )

    san_chuan_html = (
        f'<table style="margin:auto;border-collapse:collapse;">'
        f'<tr><td colspan="5" style="text-align:center;font-size:11px;'
        f'color:#9E9E9E;padding-bottom:4px;letter-spacing:2px;">'
        f'{auto_cn("三傳")}</td></tr>'
        f'{sc_html_rows}'
        f'</table>'
    )

    center_html = (
        f'<td colspan="2" rowspan="2" style="border:1px solid rgba(120,120,140,0.35);'
        f'vertical-align:middle;text-align:center;'
        f'background:rgba(20,20,35,0.55);padding:8px;">'
        f'{si_ke_html}'
        f'<div style="border-top:1px solid rgba(120,120,140,0.3);'
        f'margin:6px 0;"></div>'
        f'{san_chuan_html}'
        f'</td>'
    )

    # ── 組裝完整方盤 ──
    day_label = chart.get("_day_gz", "")
    hour_label = chart.get("_hour_gz", "")
    geju = chart.get("格局", [])
    geju_str = "、".join(geju) if isinstance(geju, list) else str(geju)
    dayma = chart.get("日馬", "")

    header_info = f'{auto_cn("日課")}：{day_label}日{hour_label}時'
    if geju_str:
        header_info += f'　{auto_cn("格局")}：{geju_str}'
    if dayma:
        header_info += f'　{auto_cn("日馬")}：{dayma}'

    rows_html = ""
    for r, row in enumerate(GRID):
        rows_html += "<tr>"
        for c, branch in enumerate(row):
            if branch is not None:
                rows_html += _cell(branch)
            elif r == 1 and c == 1:
                # 中央區塊（佔 2×2）
                rows_html += center_html
            # r=1,c=2 / r=2,c=1 / r=2,c=2 被 colspan/rowspan 覆蓋
        rows_html += "</tr>"

    table_html = (
        f'<div style="width:100%;">'
        f'<div style="text-align:center;font-size:13px;color:#B0B0C8;'
        f'margin-bottom:8px;letter-spacing:1px;">{header_info}</div>'
        f'<table style="width:100%;table-layout:fixed;border-collapse:collapse;'
        f'border:1px solid rgba(120,120,140,0.4);'
        f'border-radius:4px;overflow:hidden;">'
        f'{rows_html}'
        f'</table>'
        f'</div>'
    )
    return table_html


def render_liuren_chart(chart: dict, after_chart_hook=None, benming_zhi: str | None = None):
    """在 Streamlit 中渲染大六壬排盤結果。"""
    import streamlit.components.v1 as components

    st.markdown(f"### 🔮 {auto_cn('大六壬排盤')}")

    # ── 六壬盤式（方盤）── 移到最前面
    st.markdown(f"#### {auto_cn('六壬盤式')}")
    board_html = _build_liuren_board_html(chart, benming_zhi=benming_zhi)
    # 增加高度並添加響應式設計，確保完整顯示方盤
    components.html(
        f'''
        <div style="background:#1E1E2E;padding:16px;border-radius:12px;
                    overflow:hidden;width:100%;min-height:480px;">
            <div style="width:100%;">
                {board_html}
            </div>
        </div>
        ''',
        height=520,
        scrolling=False,
    )

    st.divider()

    # ── 基本資訊 ── 移到盤式之後
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(auto_cn("節氣"), chart.get("_jieqi", ""))
    with col2:
        st.metric(auto_cn("農曆月"), chart.get("_lunar_month", ""))
    with col3:
        st.metric(auto_cn("日干支"), chart.get("_day_gz", ""))
    with col4:
        st.metric(auto_cn("時干支"), chart.get("_hour_gz", ""))

    st.divider()

    # ── 格局 ──
    geju = chart.get("格局", [])
    if geju:
        st.markdown(f"**{auto_cn('格局')}**：{'、'.join(geju) if isinstance(geju, list) else geju}")

    # ── 日馬 ──
    dayma = chart.get("日馬", "")
    if dayma:
        st.markdown(f"**{auto_cn('日馬')}**：{dayma}")

    st.divider()

    # ── 三傳 ──
    st.markdown(f"#### {auto_cn('三傳')}")
    san_chuan = chart.get("三傳", {})
    if san_chuan:
        sc_cols = st.columns(3)
        for i, (name, vals) in enumerate(san_chuan.items()):
            with sc_cols[i % 3]:
                if isinstance(vals, list) and len(vals) >= 3:
                    st.markdown(
                        f"**{auto_cn(name)}**\n\n"
                        f"- {auto_cn('地支')}：{vals[0]}\n"
                        f"- {auto_cn('天將')}：{vals[1]}\n"
                        f"- {auto_cn('六親')}：{vals[2]}\n"
                        + (f"- {auto_cn('旬空')}：{vals[3]}" if len(vals) > 3 and vals[3] else "")
                    )

    st.divider()

    # ── 四課 ──
    st.markdown(f"#### {auto_cn('四課')}")
    si_ke = chart.get("四課", {})
    if si_ke:
        sk_cols = st.columns(4)
        for i, (name, val) in enumerate(si_ke.items()):
            with sk_cols[i % 4]:
                if isinstance(val, list) and len(val) >= 1:
                    st.markdown(f"**{auto_cn(name)}**\n\n{val[0]}")
                    if len(val) > 1:
                        st.caption(val[1])
                else:
                    st.markdown(f"**{auto_cn(name)}**：{val}")

    st.divider()

    # ── 天地盤 ──
    st.markdown(f"#### {auto_cn('天地盤')}")
    tiandipal = chart.get("天地盤", {})
    if tiandipal:
        tp = tiandipal.get("天盤", [])
        dp = tiandipal.get("地盤", [])
        tj = tiandipal.get("天將", [])
        if tp and dp:
            import pandas as pd
            data = {"地盤": dp, "天盤": tp}
            if tj:
                data["天將"] = tj
            df = pd.DataFrame(data)
            st.dataframe(df, width="stretch", hide_index=True)

    # ── 地轉天盤 / 地轉天將 ──
    for key in ("地轉天盤", "地轉天將"):
        mapping = chart.get(key, {})
        if mapping:
            with st.expander(auto_cn(key), expanded=False):
                import pandas as pd
                df = pd.DataFrame(
                    [{"地支": k, "對應": v} for k, v in mapping.items()]
                )
                st.dataframe(df, width="stretch", hide_index=True)

    # ── 十二宮（需要本命地支）──
    if benming_zhi and benming_zhi in DIZHI:
        st.divider()
        st.markdown(f"#### {auto_cn('十二宮')}")
        di_to_tian = chart.get("地轉天盤", {})
        di_to_jiang = chart.get("地轉天將", {})
        day_gz = chart.get("_day_gz", "")
        ri_gan = day_gz[0] if day_gz else ""
        start = DIZHI.index(benming_zhi)
        p_cols = st.columns(4)
        for i, pname in enumerate(TWELVE_PALACES):
            zhi = DIZHI[(start + i) % 12]
            tian = di_to_tian.get(zhi, "")
            jiang = di_to_jiang.get(zhi, "")
            jiang_full = JIANG_FULLNAME.get(jiang, jiang)
            jcolor = JIANG_COLORS.get(jiang, "#CCC")
            lq = _liuqin_label(ri_gan, tian) if ri_gan and tian else ""
            with p_cols[i % 4]:
                lq_color = LIUQIN_COLORS.get(lq, "#CCC")
                st.markdown(
                    f"<div style='border:1px solid rgba(120,120,140,0.35);"
                    f"border-radius:8px;padding:8px;text-align:center;"
                    f"margin-bottom:6px;min-height:90px;"
                    f"background:rgba(30,30,45,0.3);'>"
                    f"<b style='color:#D0D0E0;'>{auto_cn(pname)}</b><br>"
                    f"<span style='font-size:13px;color:#9E9E9E;'>"
                    f"{zhi}（{tian}）</span><br>"
                    f"<span style='color:{jcolor};opacity:0.85;'>"
                    f"{jiang_full}</span>"
                    + (
                        f"<br><span style='font-size:12px;color:{lq_color};"
                        f"font-weight:600;'>{lq}</span>"
                        if lq else ""
                    )
                    + f"</div>",
                    unsafe_allow_html=True,
                )

    if after_chart_hook:
        after_chart_hook()


# ============================================================
# 論命分析便利介面
# ============================================================

def compute_lunming(
    chart: dict,
    benming_zhi: str,
    liunian_zhi: str | None = None,
) -> dict:
    """對已排好的大六壬盤進行論命分析。

    Parameters
    ----------
    chart : dict
        ``compute_liuren_chart()`` 的回傳值。
    benming_zhi : str
        本命地支（如 ``'子'``）。
    liunian_zhi : str, optional
        流年地支，用於流年禍福分析。

    Returns
    -------
    dict
        完整結構化論命報告。
    """
    from astro.sanshi.lunming import LunMingAnalyzer

    analyzer = LunMingAnalyzer(chart, benming_zhi)
    report = analyzer.analyze_all()
    # 若有指定流年，重新分析流年部分
    if liunian_zhi:
        report["流年壽夭"] = analyzer.analyze_flow_year_month(liunian_zhi)
    return report


def render_lunming_report(report: dict) -> None:
    """在 Streamlit 中渲染論命分析報告。"""
    st.markdown(f"### 📜 {auto_cn('大六壬論命分析')}")

    # ── 身命總則 ──
    shenming = report.get("身命總則", {})
    if shenming:
        st.markdown(f"#### {auto_cn('身命總則')}")
        for section_name, section_data in shenming.items():
            if isinstance(section_data, dict):
                with st.expander(auto_cn(section_name), expanded=True):
                    for k, v in section_data.items():
                        if k == "論斷" and isinstance(v, list):
                            for comment in v:
                                st.markdown(f"- {comment}")
                        else:
                            st.markdown(f"**{auto_cn(k)}**：{v}")
            elif isinstance(section_data, list):
                with st.expander(auto_cn(section_name), expanded=False):
                    for item in section_data:
                        if isinstance(item, dict):
                            st.markdown(f"**{item.get('傳名', '')}**")
                            for k2, v2 in item.items():
                                if k2 == "傳名":
                                    continue
                                if k2 == "論斷" and isinstance(v2, list):
                                    for c in v2:
                                        st.markdown(f"  - {c}")
                                else:
                                    st.markdown(f"  - **{auto_cn(k2)}**：{v2}")
                        else:
                            st.markdown(f"- {item}")
            elif isinstance(section_data, str):
                st.info(section_data)

    st.divider()

    # ── 五節總決 ──
    five = report.get("五節總決", {})
    if five:
        st.markdown(f"#### {auto_cn('五節總決')}")
        for sec_name, sec_items in five.items():
            with st.expander(auto_cn(sec_name), expanded=False):
                if isinstance(sec_items, list):
                    for item in sec_items:
                        st.markdown(f"- {item}")
                else:
                    st.markdown(str(sec_items))

    st.divider()

    # ── 十二宮論 ──
    palaces = report.get("十二宮論", {})
    if palaces:
        st.markdown(f"#### {auto_cn('十二宮論')}")
        cols = st.columns(3)
        for i, (pname, pdata) in enumerate(palaces.items()):
            with cols[i % 3]:
                with st.expander(auto_cn(pname), expanded=False):
                    if isinstance(pdata, dict):
                        for k, v in pdata.items():
                            if k == "論斷" and isinstance(v, list):
                                for c in v:
                                    st.markdown(f"- {c}")
                            else:
                                st.markdown(f"**{auto_cn(k)}**：{v}")

    st.divider()

    # ── 二十四格 & 十六局 ──
    ge24 = report.get("二十四格", [])
    ju16 = report.get("十六局", [])
    if ge24 or ju16:
        st.markdown(f"#### {auto_cn('格局判斷')}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**{auto_cn('二十四格')}**")
            if ge24:
                for g in ge24:
                    st.markdown(f"- {g}")
            else:
                st.caption(auto_cn("未入任何格"))
        with col_b:
            st.markdown(f"**{auto_cn('十六局')}**")
            if ju16:
                for j in ju16:
                    st.markdown(f"- {j}")
            else:
                st.caption(auto_cn("未入任何局"))

    st.divider()

    # ── 女命專論 ──
    female = report.get("女命專論", {})
    if female:
        with st.expander(auto_cn("女命專論"), expanded=False):
            for k, v in female.items():
                if isinstance(v, list):
                    for c in v:
                        st.markdown(f"- {c}")
                else:
                    st.markdown(f"**{auto_cn(k)}**：{v}")

    # ── 流年壽夭 ──
    flow = report.get("流年壽夭", {})
    if flow:
        st.markdown(f"#### {auto_cn('流年壽夭')}")
        for sec_name, sec_items in flow.items():
            with st.expander(auto_cn(sec_name), expanded=False):
                if isinstance(sec_items, list):
                    for item in sec_items:
                        st.markdown(f"- {item}")
                else:
                    st.markdown(str(sec_items))

