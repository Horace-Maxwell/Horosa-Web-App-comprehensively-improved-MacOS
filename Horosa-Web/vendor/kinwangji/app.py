import os
import random
import urllib.request
import datetime

import streamlit as st
import pendulum as pdlm
import pytz

from kinwangji.wanji import display_pan, wanji_four_gua, one2two
from kinwangji.jieqi import jq, gong_wangzhuai
from kinwangji.history import history_for_year
from kinwangji.classics import list_classics, load_classic, get_sections
from kinwangji.xinyi import (
    number_qigua,
    datetime_qigua,
    direction_qigua,
    character_qigua,
    XIANTIAN_NUM,
    DIRECTION_GUA,
    TRIGRAM_CODE,
)

# ---------------------------------------------------------------------------
# Translations
# ---------------------------------------------------------------------------

_TEXTS = {
    "zh": {
        "page_title": "堅皇極 — 皇極經世排盤",
        "sidebar_title": "堅皇極",
        "sidebar_intro": (
            "**皇極經世**是北宋邵雍所創的象數易學體系，"
            "以元會運世的時間框架推演天地萬物之變化。\n\n"
            "本工具根據明黃粵洲的皇極經世起盤公式，"
            "將任意日期時間轉換為對應的卦象排盤。"
        ),
        "language": "🌐 Language / 語言",
        "date_time": "📅 日期時間選擇",
        "select_date": "選擇日期",
        "select_time": "⏰ 選擇時間",
        "hour": "時",
        "minute": "分",
        "tab_pan": "🔮 排盤",
        "tab_detail": "📋 詳細排盤",
        "tab_links": "🔗 連結",
        "header": "堅皇極 — 排盤結果",
        "subtitle": "暫時以明黃粵洲的皇極經世起盤公式起盤。",
        "datetime_label": "起卦時間",
        "gangzhi_label": "干支",
        "solar_term": "節氣",
        "prosperous": "旺",
        "supportive": "相",
        "hui": "會",
        "yun": "運",
        "shi": "世",
        "cycle_title": "📊 元會運世定位",
        "cycle_desc": "當前日期在皇極經世時間框架中的位置",
        "hui_desc": "一元 = 12會 (每會 10,800 年)",
        "yun_desc": "一會 = 30運 (每運 360 年)",
        "shi_desc": "一運 = 12世 (每世 30 年)",
        "hexagram_title": "🔮 卦象總覽",
        "main_gua": "正卦",
        "yun_gua": "運卦",
        "shi_gua": "世卦",
        "xun_gua": "旬卦",
        "year_gua": "年卦",
        "month_gua": "月卦",
        "day_gua": "日卦",
        "hour_gua": "時卦",
        "minute_gua": "分卦",
        "cosmic_gua": "⬆ 天道卦 (宏觀)",
        "temporal_gua": "⬇ 人事卦 (微觀)",
        "changing_line": "動爻",
        "full_board": "完整排盤文本",
        "links_header": "連結",
        "project_links": "📎 相關連結",
        "github_link": "GitHub 源碼",
        "pypi_link": "PyPI 頁面",
        "wiki_link": "維基百科：皇極經世",
        "image_caption": "皇極經世示意圖",
        "tab_history": "📜 隨機歷史年卦",
        "history_title": "📜 隨機歷史年卦",
        "history_desc": "隨機抽取一年，顯示該年的年卦及當時的朝代歷史。",
        "history_year": "年份",
        "history_year_gua": "年卦",
        "history_dynasty": "朝代",
        "history_title_lbl": "稱號",
        "history_name": "名諱",
        "history_era": "年號",
        "history_refresh": "🔄 再抽一年",
        "history_no_data": "該年暫無歷史資料。",
        "tab_classics": "📖 經典原文",
        "classics_title": "📖 經典原文",
        "classics_desc": "收錄三部皇極經世相關經典原文，可按卷瀏覽。",
        "classics_select_text": "選擇經典",
        "classics_select_section": "選擇章節",
        "classics_full_text": "顯示完整原文",
        "tab_xinyi": "🌸 心易發微",
        "xinyi_title": "🌸 心易發微起盤",
        "xinyi_desc": "心易發微（梅花易數）起卦法，根據楊向春《皇極經世心易發微》。",
        "xinyi_method": "起卦方法",
        "xinyi_number": "先天數起卦",
        "xinyi_datetime": "年月日時起卦",
        "xinyi_direction": "後天方位起卦",
        "xinyi_character": "字數起卦",
        "xinyi_upper_num": "上卦數",
        "xinyi_lower_num": "下卦數",
        "xinyi_upper_strokes": "上（左）筆劃數",
        "xinyi_lower_strokes": "下（右）筆劃數",
        "xinyi_object": "物象（八卦）",
        "xinyi_direction_label": "方位",
        "xinyi_hour": "時辰（0-23）",
        "xinyi_date": "選擇日期",
        "xinyi_hour_input": "時辰（0-23時）",
        "xinyi_calculate": "起卦",
        "xinyi_ben_gua": "本卦",
        "xinyi_bian_gua": "變卦",
        "xinyi_dong_yao": "動爻",
        "xinyi_upper_gua": "上卦",
        "xinyi_lower_gua": "下卦",
        "xinyi_ti_gua": "體卦",
        "xinyi_yong_gua": "用卦",
        "xinyi_hu_gua": "互卦",
        "xinyi_tiyong_wx": "體用五行",
        "xinyi_result_title": "起卦結果",
    },
    "en": {
        "page_title": "KinWangJi — Huangji Jingshi Divination",
        "sidebar_title": "KinWangJi",
        "sidebar_intro": (
            "**Huangji Jingshi** (皇極經世) is a numerological system "
            "created by Shao Yong (1011–1077) of the Northern Song dynasty.\n\n"
            "It uses yuan-hui-yun-shi cosmic cycles to map "
            "any date/time into a set of I Ching hexagrams."
        ),
        "language": "🌐 Language / 語言",
        "date_time": "📅 Date & Time",
        "select_date": "Select date",
        "select_time": "⏰ Select time",
        "hour": "Hour",
        "minute": "Min",
        "tab_pan": "🔮 Board",
        "tab_detail": "📋 Full Text",
        "tab_links": "🔗 Links",
        "header": "KinWangJi — Divination Result",
        "subtitle": "Based on Ming-dynasty Huang Yuezhou's formula.",
        "datetime_label": "Date / Time",
        "gangzhi_label": "Stems-Branches",
        "solar_term": "Solar Term",
        "prosperous": "Prosperous",
        "supportive": "Supportive",
        "hui": "Huì (會)",
        "yun": "Yùn (運)",
        "shi": "Shì (世)",
        "cycle_title": "📊 Cosmic Cycle Position",
        "cycle_desc": "Position within the Huangji Jingshi time framework",
        "hui_desc": "1 Yuán = 12 Huì (10,800 yr each)",
        "yun_desc": "1 Huì = 30 Yùn (360 yr each)",
        "shi_desc": "1 Yùn = 12 Shì (30 yr each)",
        "hexagram_title": "🔮 Hexagram Overview",
        "main_gua": "Main (正卦)",
        "yun_gua": "Yùn (運卦)",
        "shi_gua": "Shì (世卦)",
        "xun_gua": "Xún (旬卦)",
        "year_gua": "Year (年卦)",
        "month_gua": "Month (月卦)",
        "day_gua": "Day (日卦)",
        "hour_gua": "Hour (時卦)",
        "minute_gua": "Min (分卦)",
        "cosmic_gua": "⬆ Cosmic Hexagrams (macro)",
        "temporal_gua": "⬇ Temporal Hexagrams (micro)",
        "changing_line": "Changing line",
        "full_board": "Full Divination Board (text)",
        "links_header": "Links",
        "project_links": "📎 Related Links",
        "github_link": "GitHub Source",
        "pypi_link": "PyPI Page",
        "wiki_link": "Wikipedia: Huangji Jingshi",
        "image_caption": "Huangji Jingshi Diagram",
        "tab_history": "📜 Historical Year",
        "history_title": "📜 Random Historical Year Hexagram",
        "history_desc": "A random year is drawn to display its year hexagram and the dynasty in power.",
        "history_year": "Year",
        "history_year_gua": "Year Hexagram",
        "history_dynasty": "Dynasty",
        "history_title_lbl": "Title",
        "history_name": "Name",
        "history_era": "Era",
        "history_refresh": "🔄 Draw Again",
        "history_no_data": "No historical data available for this year.",
        "tab_classics": "📖 Classics",
        "classics_title": "📖 Classical Texts",
        "classics_desc": "Browse three classical texts related to Huangji Jingshi.",
        "classics_select_text": "Select text",
        "classics_select_section": "Select section",
        "classics_full_text": "Show full text",
        "tab_xinyi": "🌸 Xinyi Fawei",
        "xinyi_title": "🌸 Xinyi Fawei Divination",
        "xinyi_desc": "Hexagram-raising methods from Yang Xiangjun's *Huangji Jingshi Xinyi Fawei* (Plum Blossom Numerology).",
        "xinyi_method": "Method",
        "xinyi_number": "Pre-Heaven Numbers",
        "xinyi_datetime": "Date & Time",
        "xinyi_direction": "Post-Heaven Direction",
        "xinyi_character": "Character Strokes",
        "xinyi_upper_num": "Upper number",
        "xinyi_lower_num": "Lower number",
        "xinyi_upper_strokes": "Upper/left strokes",
        "xinyi_lower_strokes": "Lower/right strokes",
        "xinyi_object": "Object (trigram)",
        "xinyi_direction_label": "Direction",
        "xinyi_hour": "Hour (0-23)",
        "xinyi_date": "Select date",
        "xinyi_hour_input": "Hour (0-23)",
        "xinyi_calculate": "Cast hexagram",
        "xinyi_ben_gua": "Original (本卦)",
        "xinyi_bian_gua": "Changed (變卦)",
        "xinyi_dong_yao": "Moving line",
        "xinyi_upper_gua": "Upper trigram",
        "xinyi_lower_gua": "Lower trigram",
        "xinyi_ti_gua": "Body (體卦)",
        "xinyi_yong_gua": "Use (用卦)",
        "xinyi_hu_gua": "Interlocking (互卦)",
        "xinyi_tiyong_wx": "Five-Element relation",
        "xinyi_result_title": "Divination Result",
    },
}


def _t(key: str) -> str:
    """Return the translated text for *key* in the current language."""
    lang = st.session_state.get("lang", "zh")
    return _TEXTS[lang][key]


def _cycle_position(value: int, cycle_length: int) -> int:
    """Normalize a 1-based cycle value into its position within a parent cycle."""
    return ((value - 1) % cycle_length) + 1


# ---------------------------------------------------------------------------
# I Ching hexagram Unicode symbols (U+4DC0–U+4DFF, King Wen sequence)
# ---------------------------------------------------------------------------

_GUA_UNICODE = {
    "乾": "䷀", "坤": "䷁", "屯": "䷂", "蒙": "䷃", "需": "䷄",
    "訟": "䷅", "師": "䷆", "比": "䷇", "小畜": "䷈", "履": "䷉",
    "泰": "䷊", "否": "䷋", "同人": "䷌", "大有": "䷍", "謙": "䷎",
    "豫": "䷏", "隨": "䷐", "蠱": "䷑", "臨": "䷒", "觀": "䷓",
    "噬嗑": "䷔", "賁": "䷕", "剝": "䷖", "復": "䷗", "無妄": "䷘",
    "大畜": "䷙", "頤": "䷚", "大過": "䷛", "坎": "䷜", "離": "䷝",
    "咸": "䷞", "恆": "䷟", "遯": "䷠", "大壯": "䷡", "晉": "䷢",
    "明夷": "䷣", "家人": "䷤", "睽": "䷥", "蹇": "䷦", "解": "䷧",
    "損": "䷨", "益": "䷩", "夬": "䷪", "姤": "䷫", "萃": "䷬",
    "升": "䷭", "困": "䷮", "井": "䷯", "革": "䷰", "鼎": "䷱",
    "震": "䷲", "艮": "䷳", "漸": "䷴", "歸妹": "䷵", "豐": "䷶",
    "旅": "䷷", "巽": "䷸", "兌": "䷹", "渙": "䷺", "節": "䷻",
    "中孚": "䷼", "小過": "䷽", "既濟": "䷾", "未濟": "䷿",
}


def _gua_symbol(name: str) -> str:
    """Return the Unicode hexagram symbol for a given hexagram *name*."""
    return _GUA_UNICODE.get(name, "☰")


def _hexagram_card(icon: str, gua_name: str, label: str) -> str:
    """Return an HTML snippet for a centred hexagram display card."""
    return (
        f"<div style='text-align:center;'>"
        f"<span style='font-size:2rem;'>{icon}</span><br>"
        f"<b style='font-size:1.3rem;'>{gua_name}</b><br>"
        f"<span style='color:gray;'>{label}</span>"
        f"</div>"
    )


# ---------------------------------------------------------------------------
# Helper – fetch remote Markdown (used by the Links tab)
# ---------------------------------------------------------------------------

def _fetch_remote_md(url: str) -> str:
    """Fetch a remote Markdown file; return empty string on failure."""
    try:
        response = urllib.request.urlopen(url, timeout=5)
        return response.read().decode("utf-8")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    layout="wide",
    page_title="堅皇極 — Huangji Jingshi",
    page_icon="☯",
)

# Initialise language in session state
if "lang" not in st.session_state:
    st.session_state["lang"] = "zh"

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    # Language toggle
    lang_choice = st.selectbox(
        "🌐 Language / 語言",
        options=["中文", "English"],
        index=0 if st.session_state["lang"] == "zh" else 1,
    )
    st.session_state["lang"] = "zh" if lang_choice == "中文" else "en"

    st.divider()

    # Project image
    img_path = os.path.join(os.path.dirname(__file__), "pic", "kwj.png")
    if os.path.isfile(img_path):
        try:
            st.image(img_path, caption=_t("image_caption"), use_container_width=True)
        except TypeError:
            st.image(img_path, caption=_t("image_caption"), use_column_width=True)

    # Introduction
    st.subheader(_t("sidebar_title"))
    st.markdown(_t("sidebar_intro"))
    st.divider()

    # Date / time input
    now_shanghai = pdlm.now(tz="Asia/Shanghai")
    st.subheader(_t("date_time"))
    idate = st.date_input(
        _t("select_date"),
        now_shanghai.date(),
        min_value=datetime.date(1900, 1, 1),
        max_value=datetime.date(2100, 12, 31),
    )
    st.markdown(f"**{_t('select_time')}**")
    col1, col2 = st.columns(2)
    with col1:
        sel_hour = st.number_input(
            _t("hour"), min_value=0, max_value=23,
            value=now_shanghai.hour, step=1,
        )
    with col2:
        sel_minute = st.number_input(
            _t("minute"), min_value=0, max_value=59,
            value=now_shanghai.minute, step=1,
        )
    pp_time = datetime.time(int(sel_hour), int(sel_minute))

    st.divider()

    # Project links
    st.subheader(_t("project_links"))
    st.markdown(
        "- [🐙 GitHub](https://github.com/kentang2017/kinwangji)\n"
        "- [📦 PyPI](https://pypi.org/project/kinwangji/)\n"
        "- [📖 Wikipedia](https://zh.wikipedia.org/wiki/皇極經世)"
    )

# ---------------------------------------------------------------------------
# Compute results
# ---------------------------------------------------------------------------

y, m, d = idate.year, idate.month, idate.day
h, mi = pp_time.hour, pp_time.minute

try:
    result = wanji_four_gua(y, m, d, h, mi)
    pan_text = display_pan(y, m, d, h, mi)
    solar_term = jq(y, m, d, h, mi)
    wz = gong_wangzhuai(solar_term)
except Exception:
    now = datetime.datetime.now(pytz.timezone("Asia/Hong_Kong"))
    y, m, d, h, mi = now.year, now.month, now.day, now.hour, now.minute
    try:
        result = wanji_four_gua(y, m, d, h, mi)
        pan_text = display_pan(y, m, d, h, mi)
        solar_term = jq(y, m, d, h, mi)
        wz = gong_wangzhuai(solar_term)
    except Exception as e:
        st.error(f"無法計算排盤 / Unable to compute divination board: {e}")
        st.stop()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_pan, tab_xinyi, tab_history, tab_classics, tab_detail, tab_links = st.tabs(
    [_t("tab_pan"), _t("tab_xinyi"), _t("tab_history"), _t("tab_classics"), _t("tab_detail"), _t("tab_links")]
)

# ---- Tab 1: Visual Board -------------------------------------------------
with tab_pan:
    st.header(_t("header"))
    st.caption(_t("subtitle"))

    # -- Basic info row (date, gangzhi, solar term) -------------------------
    info_cols = st.columns(3)
    with info_cols[0]:
        st.metric(_t("datetime_label"), f"{y}-{m:02d}-{d:02d}  {h:02d}:{mi:02d}")
    with info_cols[1]:
        gz = result["干支"]
        st.metric(_t("gangzhi_label"), "  ".join(gz))
    with info_cols[2]:
        # gong_wangzhuai returns (trigram_to_state, state_to_trigram)
        _, state_to_trigram = wz
        wang_str = state_to_trigram.get("旺", "")
        xiang_str = state_to_trigram.get("相", "")
        term_display = f"{solar_term}  ({_t('prosperous')}: {wang_str}, {_t('supportive')}: {xiang_str})"
        st.metric(_t("solar_term"), term_display)

    st.divider()

    # -- Yuan-Hui-Yun-Shi cycle visualization -------------------------------
    st.subheader(_t("cycle_title"))
    st.caption(_t("cycle_desc"))

    hui_val = result["會"]
    yun_val = result["運"]
    shi_val = result["世"]

    # Compute positions within their parent cycle
    hui_in_yuan = _cycle_position(hui_val, 12)   # 1–12
    yun_in_hui = _cycle_position(yun_val, 30)    # 1–30
    shi_in_yun = _cycle_position(shi_val, 12)    # 1–12

    cyc_cols = st.columns(3)
    with cyc_cols[0]:
        st.metric(_t("hui"), f"{hui_val}  ({hui_in_yuan}/12)")
        st.progress(hui_in_yuan / 12)
        st.caption(_t("hui_desc"))
    with cyc_cols[1]:
        st.metric(_t("yun"), f"{yun_val}  ({yun_in_hui}/30)")
        st.progress(yun_in_hui / 30)
        st.caption(_t("yun_desc"))
    with cyc_cols[2]:
        st.metric(_t("shi"), f"{shi_val}  ({shi_in_yun}/12)")
        st.progress(shi_in_yun / 12)
        st.caption(_t("shi_desc"))

    st.divider()

    # -- Hexagram overview --------------------------------------------------
    st.subheader(_t("hexagram_title"))

    # Cosmic-level hexagrams (macro)
    with st.expander(_t("cosmic_gua"), expanded=True):
        gcols = st.columns(4)
        gua_keys = [
            ("main_gua", "正卦", None),
            ("yun_gua", "運卦", "運卦動爻"),
            ("shi_gua", "世卦", "世卦動爻"),
            ("xun_gua", "旬卦", "旬卦動爻"),
        ]
        for col, (label_key, gua_key, line_key) in zip(gcols, gua_keys):
            with col:
                gua_name = one2two(result[gua_key])
                st.markdown(
                    _hexagram_card(_gua_symbol(result[gua_key]), gua_name, _t(label_key)),
                    unsafe_allow_html=True,
                )
                if line_key:
                    st.caption(f"{_t('changing_line')}: {result[line_key]}")

    # Temporal hexagrams (micro)
    with st.expander(_t("temporal_gua"), expanded=True):
        tcols = st.columns(5)
        temporal_keys = [
            ("year_gua", "年卦"),
            ("month_gua", "月卦"),
            ("day_gua", "日卦"),
            ("hour_gua", "時卦"),
            ("minute_gua", "分卦"),
        ]
        for col, (label_key, gua_key) in zip(tcols, temporal_keys):
            with col:
                gua_name = one2two(result[gua_key])
                st.markdown(
                    _hexagram_card(_gua_symbol(result[gua_key]), gua_name, _t(label_key)),
                    unsafe_allow_html=True,
                )

# ---- Tab 2: Xinyi Fawei 心易發微起盤 ----------------------------------------
with tab_xinyi:
    st.header(_t("xinyi_title"))
    st.caption(_t("xinyi_desc"))

    method_options = {
        _t("xinyi_number"): "number",
        _t("xinyi_datetime"): "datetime",
        _t("xinyi_direction"): "direction",
        _t("xinyi_character"): "character",
    }
    selected_method_label = st.selectbox(
        _t("xinyi_method"),
        options=list(method_options.keys()),
    )
    selected_method = method_options[selected_method_label]

    xinyi_result = None

    if selected_method == "number":
        nc1, nc2 = st.columns(2)
        with nc1:
            xy_upper = st.number_input(_t("xinyi_upper_num"), min_value=1, value=5, step=1)
        with nc2:
            xy_lower = st.number_input(_t("xinyi_lower_num"), min_value=1, value=10, step=1)
        if st.button(_t("xinyi_calculate"), key="xinyi_btn"):
            xinyi_result = number_qigua(int(xy_upper), int(xy_lower))

    elif selected_method == "datetime":
        dc1, dc2 = st.columns(2)
        with dc1:
            xy_date = st.date_input(
                _t("xinyi_date"),
                now_shanghai.date(),
                min_value=datetime.date(1900, 1, 1),
                max_value=datetime.date(2100, 12, 31),
                key="xinyi_date_input",
            )
        with dc2:
            xy_hour = st.number_input(
                _t("xinyi_hour_input"),
                min_value=0, max_value=23,
                value=now_shanghai.hour, step=1,
                key="xinyi_hour_input",
            )
        if st.button(_t("xinyi_calculate"), key="xinyi_btn"):
            xinyi_result = datetime_qigua(
                xy_date.year, xy_date.month, xy_date.day, int(xy_hour),
            )

    elif selected_method == "direction":
        dc1, dc2, dc3 = st.columns(3)
        trigram_names = list(TRIGRAM_CODE.keys())
        direction_names = list(DIRECTION_GUA.keys())
        with dc1:
            xy_obj = st.selectbox(_t("xinyi_object"), options=trigram_names)
        with dc2:
            xy_dir = st.selectbox(_t("xinyi_direction_label"), options=direction_names)
        with dc3:
            xy_hr = st.number_input(
                _t("xinyi_hour"),
                min_value=0, max_value=23,
                value=now_shanghai.hour, step=1,
                key="xinyi_dir_hour",
            )
        if st.button(_t("xinyi_calculate"), key="xinyi_btn"):
            xinyi_result = direction_qigua(xy_obj, xy_dir, int(xy_hr))

    elif selected_method == "character":
        cc1, cc2 = st.columns(2)
        with cc1:
            xy_us = st.number_input(_t("xinyi_upper_strokes"), min_value=1, value=5, step=1)
        with cc2:
            xy_ls = st.number_input(_t("xinyi_lower_strokes"), min_value=1, value=8, step=1)
        if st.button(_t("xinyi_calculate"), key="xinyi_btn"):
            xinyi_result = character_qigua(int(xy_us), int(xy_ls))

    # Display result
    if xinyi_result:
        st.divider()
        st.subheader(_t("xinyi_result_title"))

        # Main hexagrams row
        r1, r2, r3 = st.columns(3)
        with r1:
            ben = xinyi_result["本卦"]
            st.markdown(
                _hexagram_card(_gua_symbol(ben), one2two(ben), _t("xinyi_ben_gua")),
                unsafe_allow_html=True,
            )
        with r2:
            bian = xinyi_result["變卦"]
            st.markdown(
                _hexagram_card(_gua_symbol(bian), one2two(bian), _t("xinyi_bian_gua")),
                unsafe_allow_html=True,
            )
        with r3:
            hu = xinyi_result["互卦"]
            st.markdown(
                _hexagram_card(_gua_symbol(hu), one2two(hu), _t("xinyi_hu_gua")),
                unsafe_allow_html=True,
            )

        st.divider()

        # Detail metrics
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.metric(_t("xinyi_dong_yao"), f"第 {xinyi_result['動爻']} 爻")
        with d2:
            st.metric(_t("xinyi_ti_gua"), xinyi_result["體卦"])
        with d3:
            st.metric(_t("xinyi_yong_gua"), xinyi_result["用卦"])
        with d4:
            st.metric(_t("xinyi_tiyong_wx"), xinyi_result["體用五行"])

# ---- Tab 3: Random Historical Year Hexagram --------------------------------
with tab_history:
    st.header(_t("history_title"))
    st.caption(_t("history_desc"))

    # Initialise or refresh the random year stored in session state
    if "random_year" not in st.session_state:
        st.session_state["random_year"] = random.randint(1900, 2100)

    if st.button(_t("history_refresh")):
        st.session_state["random_year"] = random.randint(1900, 2100)

    rand_year = st.session_state["random_year"]

    # Compute year hexagram using a fixed mid-year date
    try:
        rand_result = wanji_four_gua(rand_year, 6, 15, 12, 0)
        rand_year_gua = rand_result["年卦"]
    except Exception:
        rand_year_gua = "—"

    # Display year and hexagram
    hcol1, hcol2 = st.columns(2)
    with hcol1:
        st.metric(_t("history_year"), str(rand_year))
    with hcol2:
        if rand_year_gua and rand_year_gua != "—":
            gua_display = f"{_gua_symbol(rand_year_gua)} {one2two(rand_year_gua)}"
        else:
            gua_display = "—"
        st.metric(_t("history_year_gua"), gua_display)

    st.divider()

    # Historical records for the random year
    hist_records = history_for_year(rand_year)
    if hist_records:
        for rec in hist_records:
            cols = st.columns(4)
            with cols[0]:
                st.markdown(f"**{_t('history_dynasty')}**: {rec['dynasty']}")
            with cols[1]:
                st.markdown(f"**{_t('history_title_lbl')}**: {rec['title']}")
            with cols[2]:
                st.markdown(f"**{_t('history_name')}**: {rec['name'] or '—'}")
            with cols[3]:
                st.markdown(f"**{_t('history_era')}**: {rec['era']}")
    else:
        st.info(_t("history_no_data"))

# ---- Tab 4: Classical Texts -----------------------------------------------
with tab_classics:
    st.header(_t("classics_title"))
    st.caption(_t("classics_desc"))

    classics_meta = list_classics()
    classic_options = {c["title"]: c["key"] for c in classics_meta}
    selected_title = st.selectbox(
        _t("classics_select_text"),
        options=list(classic_options.keys()),
    )
    selected_key = classic_options[selected_title]

    # Show author & description
    meta = next(c for c in classics_meta if c["key"] == selected_key)
    st.markdown(f"**{meta['author']}**　—　{meta['description']}")

    st.divider()

    sections = get_sections(selected_key)
    if sections:
        section_titles = [s["title"] for s in sections]
        selected_section = st.selectbox(
            _t("classics_select_section"),
            options=section_titles,
        )
        idx = section_titles.index(selected_section)
        sec = sections[idx]
        st.subheader(sec["title"])
        if sec["content"]:
            st.markdown(sec["content"])
        else:
            st.info("（本節無正文內容）")

    with st.expander(_t("classics_full_text"), expanded=False):
        full_text = load_classic(selected_key)
        st.markdown(full_text)

# ---- Tab 5: Full text board -----------------------------------------------
with tab_detail:
    st.subheader(_t("full_board"))
    st.code(pan_text, language=None)

# ---- Tab 6: Links ---------------------------------------------------------
with tab_links:
    st.header(_t("links_header"))
    content = _fetch_remote_md(
        "https://raw.githubusercontent.com/kentang2017/kinliuren/master/update.md"
    )
    if content:
        st.markdown(content, unsafe_allow_html=True)
    else:
        st.info("Unable to load remote content. Check your internet connection.")

