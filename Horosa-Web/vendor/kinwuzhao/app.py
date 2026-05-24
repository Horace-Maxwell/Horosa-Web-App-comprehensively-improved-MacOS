# -*- coding: utf-8 -*-
"""堅五兆 Streamlit 應用主程式。

移除 urllib.request raw github 載入，改為本地 import。
加強輸入驗證、錯誤處理與 session_state 管理。
增加「手動輸入分裂數」功能。
"""

from __future__ import annotations

import datetime
import html
import logging
from pathlib import Path

import pendulum as pdlm
import streamlit as st
import streamlit.components.v1 as components
from sxtwl import fromSolar

import config
import jieqi
import kinwuzhao

logging.basicConfig(level=logging.ERROR)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Initialize session state to control rendering
if "render_default" not in st.session_state:
    st.session_state.render_default = True


def _read_local_md(filename: str) -> str:
    """讀取專案根目錄下的 Markdown 文件。"""
    path = Path(__file__).parent / filename
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"⚠️ 找不到檔案: {filename}。請確認檔案存在於專案根目錄。"


def render_svg(svg: str, num: int) -> None:
    """將 SVG 標記渲染為 Streamlit HTML 元件。"""
    if not svg or "svg" not in svg.lower():
        st.error("Invalid SVG content provided")
        return

    svg = svg.replace("\n", '</tspan><tspan x="0" dy="1.2em">')
    svg = svg.replace("<text", '<text x="0"')

    html_content = f"""
    <div style="display: flex; justify-content: center; align-items: center;">
        {svg}
    </div>
    """
    components.html(html_content, height=num, width=num)


def lunar_date_d(y: int, m: int, d: int) -> dict[str, str]:
    """取得農曆月日資訊。"""
    day = fromSolar(y, m, d)
    return {"月": f"{day.getLunarMonth()}月", "日": str(day.getLunarDay())}


# ---------------------------------------------------------------------------
# Page config & custom CSS
# ---------------------------------------------------------------------------

st.set_page_config(
    layout="wide",
    page_title="堅五兆 - 五兆排盘",
    page_icon="icon.png",
)

st.markdown(
    """
    <style>
    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1C23 0%, #252730 100%);
    }
    section[data-testid="stSidebar"] hr {
        border-color: #3A3D4A;
    }

    /* ---- Info card (used for metrics above the grid) ---- */
    div.info-card {
        background: #252730;
        border: 1px solid #3A3D4A;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 6px;
    }
    div.info-card .label {
        font-size: 0.78rem;
        color: #9E9E9E;
        margin-bottom: 2px;
        letter-spacing: 0.5px;
    }
    div.info-card .value {
        font-size: 1.05rem;
        font-weight: 600;
        color: #E0E0E0;
    }

    /* ---- Tab content area ---- */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        font-size: 1rem;
        padding: 10px 20px;
    }

    /* ---- Links list in 連結 tab ---- */
    .link-card {
        background: #252730;
        border: 1px solid #3A3D4A;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 10px;
        transition: border-color 0.2s;
    }
    .link-card:hover {
        border-color: #FF4B4B;
    }
    .link-card a {
        color: #FF4B4B;
        text-decoration: none;
        font-weight: 600;
        font-size: 1.05rem;
    }
    .link-card .link-desc {
        color: #9E9E9E;
        font-size: 0.85rem;
        margin-top: 4px;
    }

    /* ---- Update log timeline ---- */
    .update-entry {
        border-left: 3px solid #FF4B4B;
        padding: 10px 16px;
        margin-bottom: 14px;
        background: #252730;
        border-radius: 0 8px 8px 0;
    }
    .update-entry .update-date {
        font-weight: 700;
        color: #FF4B4B;
        font-size: 0.95rem;
        margin-bottom: 4px;
    }
    .update-entry .update-content {
        color: #BDBDBD;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    /* ---- Footer ---- */
    .app-footer {
        text-align: center;
        color: #666;
        font-size: 0.78rem;
        padding: 20px 0 8px 0;
        border-top: 1px solid #3A3D4A;
        margin-top: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

tab_pan, tab_example, tab_guji, tab_links, tab_update = st.tabs(
    ["🧮 排盤", "📜 案例", "📚 古籍", "🔗 連結", "🆕 更新"]
)

# ---------------------------------------------------------------------------
# SVG grid builder
# ---------------------------------------------------------------------------

grid = [
    ("兆", 0, 0),    ("火鄉", 1, 0), ("", 2, 0),
    ("木鄉", 0, 1),  ("土鄉", 1, 1), ("金鄉", 2, 1),
    ("", 0, 2),      ("水鄉", 1, 2), ("", 2, 2),
]

CELL_SIZE = 140
SVG_SIZE = CELL_SIZE * 3

ELEMENT_COLORS = {
    "木": "#4CAF50",
    "火": "#FF5252",
    "土": "#FFD740",
    "金": "#E0E0E0",
    "水": "#42A5F5",
}


def build_svg(data: dict) -> str:
    """組裝九宮格 SVG 排盤圖。"""
    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_SIZE} {SVG_SIZE}" '
        f'width="{SVG_SIZE}" height="{SVG_SIZE}">'
    )
    parts.append(
        f'<rect x="0" y="0" width="{SVG_SIZE}" height="{SVG_SIZE}" fill="#1A1C23" rx="8"/>'
    )

    by_palace = {v.get("宮位"): v for v in data.values()}

    for i in range(1, 3):
        parts.append(
            f'<line x1="{i * CELL_SIZE}" y1="0" x2="{i * CELL_SIZE}" y2="{SVG_SIZE}" '
            f'stroke="#444" stroke-width="1"/>'
        )
        parts.append(
            f'<line x1="0" y1="{i * CELL_SIZE}" x2="{SVG_SIZE}" y2="{i * CELL_SIZE}" '
            f'stroke="#444" stroke-width="1"/>'
        )

    parts.append(
        f'<rect x="0" y="0" width="{SVG_SIZE}" height="{SVG_SIZE}" '
        f'fill="none" stroke="#666" stroke-width="2" rx="8"/>'
    )

    for name, col, row in grid:
        cx = col * CELL_SIZE + CELL_SIZE / 2
        cy = row * CELL_SIZE + 20
        cell = by_palace.get(name, {})
        element = cell.get("五行", "")
        element_color = ELEMENT_COLORS.get(element, "#E0E0E0")

        texts = [
            name,
            f"{element}{cell.get('旺相', '')}",
            f"{cell.get('六獸', '')}{cell.get('六獸死', '')}{cell.get('六獸害', '')}",
            cell.get("六親", ""),
            f"{cell.get('關', '')}{cell.get('籥', '')}{cell.get('孤', '')}{cell.get('虛', '')}",
        ]

        parts.append(
            f'<text x="{cx}" y="{cy}" text-anchor="middle" '
            f'dominant-baseline="hanging" font-size="14" fill="#E0E0E0">'
        )
        for i, line in enumerate(texts):
            if line:
                dy = "1.4em" if i > 0 else "0"
                if i == 0:
                    parts.append(
                        f'<tspan x="{cx}" dy="{dy}" font-size="15" '
                        f'font-weight="bold" fill="#BDBDBD">{line}</tspan>'
                    )
                elif i == 1:
                    parts.append(
                        f'<tspan x="{cx}" dy="{dy}" font-size="18" '
                        f'font-weight="bold" fill="{element_color}">{line}</tspan>'
                    )
                else:
                    parts.append(f'<tspan x="{cx}" dy="{dy}">{line}</tspan>')
        parts.append("</text>")

    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    if Path("icon.png").is_file():
        st.image("icon.png", width=64)
    st.markdown("#### 堅五兆 排盤設定")

    default_datetime = pdlm.now(tz="Asia/Hong_Kong")

    # -- 快捷按鈕 --
    if st.button("⏱ 使用現在時間", use_container_width=True, type="primary"):
        now = pdlm.now(tz="Asia/Hong_Kong")
        st.session_state["input_date"] = datetime.date(now.year, now.month, now.day)
        st.session_state["input_time"] = datetime.time(now.hour, now.minute)
        st.rerun()

    st.divider()

    # -- 日期輸入 --
    st.markdown("##### 📅 日期")
    default_date = datetime.date(
        default_datetime.year, default_datetime.month, default_datetime.day
    )
    date_val = st.date_input(
        "選擇日期",
        value=st.session_state.get("input_date", default_date),
        min_value=datetime.date(1, 1, 1),
        max_value=datetime.date(2100, 12, 31),
        help="選擇日期",
        label_visibility="collapsed",
    )
    y = date_val.year
    m = date_val.month
    d_input = date_val.day

    # -- 時間輸入 --
    st.markdown("##### 🕐 時間")
    default_time = datetime.time(default_datetime.hour, default_datetime.minute)
    time_val = st.time_input(
        "選擇時間",
        value=st.session_state.get("input_time", default_time),
        step=datetime.timedelta(minutes=1),
        help="選擇時間",
        label_visibility="collapsed",
    )
    h = time_val.hour
    mi = time_val.minute

    # -- 數字 --
    st.markdown("##### 🔢 數字")
    number = st.number_input(
        "數字",
        min_value=0,
        max_value=90,
        value=0,
        step=1,
        help="輸入數字 (0-90)",
        label_visibility="collapsed",
    )

    st.divider()

    # Date validation
    valid_date = True
    try:
        selected_datetime = pdlm.datetime(y, m, d_input, h, mi, tz="Asia/Hong_Kong")
        st.success(f"📆 {y}年{m}月{d_input}日 {h:02d}:{mi:02d}", icon="✅")
    except ValueError:
        st.error("請輸入有效的日期和時間！", icon="🚨")
        valid_date = False

    # 起盤方式選擇
    st.markdown("##### 🔮 起盤方式")
    pan_mode = st.radio(
        "起盤方式",
        ["日干起盤", "時干起盤", "分干起盤", "干支起盤", "唐代正法揲筮"],
        index=0,
        label_visibility="collapsed",
    )

    # 手動折竹輸入（僅在隨機/唐代正法模式下顯示）
    manual_splits: list[int] | None = None
    if pan_mode in ("日干起盤", "時干起盤", "分干起盤", "唐代正法揲筮"):
        use_manual = st.checkbox("🎋 手動輸入分裂數（傳統折竹體驗）")
        if use_manual:
            st.caption("依序輸入 6 次折竹數（每次從剩餘算子中取走的數量）")
            split_cols = st.columns(6)
            manual_splits = []
            labels = ["兆", "木鄉", "火鄉", "土鄉", "金鄉", "水鄉"]
            for i, sc in enumerate(split_cols):
                with sc:
                    val = st.number_input(
                        labels[i],
                        min_value=1,
                        max_value=35,
                        value=6,
                        step=1,
                        key=f"split_{i}",
                    )
                    manual_splits.append(val)

    st.divider()
    st.caption("🌏 時區: Asia/Hong_Kong")


# ---------------------------------------------------------------------------
# Content tabs (local file reads, no urllib)
# ---------------------------------------------------------------------------

with tab_links:
    st.markdown("### 🔗 相關連結")
    links = [
        ("堅六壬 Kinliuren", "https://github.com/kentang2017/kinliuren", "六壬排盤工具"),
        ("堅奇門 Kinqimen", "https://github.com/kentang2017/kinqimen", "奇門遁甲排盤工具"),
        ("堅太乙 Kintaiyi", "https://github.com/kentang2017/kintaiyi", "太乙神數排盤工具"),
    ]
    for name, url, desc in links:
        st.markdown(
            f'<div class="link-card">'
            f'<a href="{url}" target="_blank">{name}</a>'
            f'<div class="link-desc">{desc}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

with tab_example:
    st.markdown("### 📜 案例")
    st.markdown(_read_local_md("example.md"))

with tab_guji:
    st.markdown("### 📚 五兆古籍")
    st.markdown(_read_local_md("guji.md"))

with tab_update:
    st.markdown("### 🆕 更新日誌")
    raw_log = _read_local_md("log.md")
    # Parse the log into timeline entries
    _LOG_SEPARATOR = "=" * 45
    entries = [e.strip() for e in raw_log.split(_LOG_SEPARATOR) if e.strip()]
    if entries:
        for entry in entries:
            lines = entry.strip().splitlines()
            date_line = html.escape(lines[0].strip()) if lines else ""
            body_lines = [html.escape(ln.strip()) for ln in lines[1:] if ln.strip()]
            body_html = "<br>".join(body_lines)
            st.markdown(
                f'<div class="update-entry">'
                f'<div class="update-date">{date_line}</div>'
                f'<div class="update-content">{body_html}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(raw_log)


# ---------------------------------------------------------------------------
# Main divination panel
# ---------------------------------------------------------------------------

with tab_pan:
    st.markdown("### 🧮 堅五兆 排盤")

    if not valid_date:
        st.warning("請先在側邊欄輸入有效的日期與時間。", icon="⚠️")
        st.stop()

    try:
        cm = dict(
            zip(range(1, 13), list("正二三四五六七八九十") + ["十一", "十二"])
        ).get(int(lunar_date_d(y, m, d_input).get("月", "1月").replace("月", "")))

        qgz = config.gangzhi(y, m, d_input, h, mi)
        jq_val = jieqi.jq(y, m, d_input, h, mi)
        lunar_month = config.lunar_date_d(y, m, d_input)["農曆月"][0]

        if number > 9:
            number = number % 9

        result: dict = {}

        if pan_mode == "干支起盤":
            result = kinwuzhao.gangzhi_paipan(qgz, number, jq_val, lunar_month)
        elif pan_mode == "日干起盤":
            result = kinwuzhao.five_zhao_paipan(
                number, jq_val, lunar_month, qgz[1], qgz[2],
                manual_splits=manual_splits,
            )
        elif pan_mode == "時干起盤":
            result = kinwuzhao.five_zhao_paipan(
                number, jq_val, lunar_month, qgz[2], qgz[3],
                manual_splits=manual_splits,
            )
        elif pan_mode == "分干起盤":
            result = kinwuzhao.five_zhao_paipan(
                number, jq_val, lunar_month, qgz[3], qgz[4],
                manual_splits=manual_splits,
            )
        elif pan_mode == "唐代正法揲筮":
            div = kinwuzhao.WuzhaoDivination(
                jq=jq_val,
                cm=lunar_month,
                gz1=qgz[2],
                gz2=qgz[3],
                manual_splits=manual_splits,
            )
            result = div.divine()

        if "錯誤" in result:
            st.error(result["錯誤"])
            st.stop()

        svg_markup = build_svg(result)

        # -- Styled info cards --
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                '<div class="info-card">'
                '<div class="label">起盤模式</div>'
                f'<div class="value">🔮 {pan_mode}</div>'
                "</div>",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                '<div class="info-card">'
                '<div class="label">日期時間</div>'
                f'<div class="value">📆 {y}/{m}/{d_input} {h:02d}:{mi:02d}</div>'
                "</div>",
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                '<div class="info-card">'
                '<div class="label">節氣</div>'
                f'<div class="value">🌿 {jq_val}</div>'
                "</div>",
                unsafe_allow_html=True,
            )
        with c4:
            gz_text = f"{qgz[0]}年 {qgz[1]}月 {qgz[2]}日 {qgz[3]}時 {qgz[4]}分"
            st.markdown(
                '<div class="info-card">'
                '<div class="label">干支</div>'
                f'<div class="value">🔢 {gz_text}</div>'
                "</div>",
                unsafe_allow_html=True,
            )

        st.divider()
        render_svg(svg_markup, 600)

    except Exception as e:
        logging.exception("排盤過程發生錯誤")
        st.error(f"排盤過程發生錯誤：{e}")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="app-footer">堅五兆 Kinwuzhao &copy; kentang2017</div>',
    unsafe_allow_html=True,
)
