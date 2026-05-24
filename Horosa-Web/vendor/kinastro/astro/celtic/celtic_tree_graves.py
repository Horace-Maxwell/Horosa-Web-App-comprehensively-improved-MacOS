"""
astro/celtic/celtic_tree_graves.py — Celtic Tree Calendar (Graves 1948)

Implements the Beth-Luis-Nion tree-alphabet calendar exactly as devised
by Robert Graves in "The White Goddess: A Historical Grammar of Poetic
Myth" (Faber & Faber, London, 1948).

⚠️  IMPORTANT NOTICE
This is *not* historical ancient Celtic astrology.  It is a modern
scholarly/poetic reconstruction created by Robert Graves in 1948,
mapping the Ogham consonant-alphabet onto a 13-month lunar calendar.
Graves combined poetic myth, White Goddess theology, and speculative
etymology to produce this system.  All UI copy and docstrings clearly
label it as such.

Source:
    Graves, Robert. *The White Goddess: A Historical Grammar of Poetic
    Myth*. Faber & Faber, London, 1948 (revised 1961).
    Relevant chapters: "The Battle of the Trees", "Felling of the
    Sacred Grove", and "The Tree Calendar".

Calendar structure (from Graves 1948):
    13 months × ~28 days = 364 days.
    Extra 1-day intercalation: December 23 (Day of Creation / Day
    outside the year — no tree assigned, as per Graves).
    Total: 365 days (366 in leap years handled by convention — no
    canonical leap-year rule exists in the original text; Dec 23 is
    treated as a 2-day interval in leap years).

The calendar begins on the Winter Solstice eve (Dec 24) with Beth
(Birch), the month of new beginnings.
"""

from __future__ import annotations

import streamlit as st
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

# ════════════════════════════════════════════════════════════════════
# Tree Month Data (Graves 1948 — exact dates and names)
# ════════════════════════════════════════════════════════════════════
#
# Each entry is a dict with:
#   month_number : 1–13 (Beth=1, Ruis=13)
#   gaelic       : Ogham consonant name (Gaelic spelling, Graves 1948)
#   english      : English tree common name (Graves 1948)
#   chinese      : Chinese common name for the tree (translation)
#   ogham_letter : Unicode Ogham character (U+1681–U+168F range)
#   start_md     : (month, day) — Gregorian start date (inclusive)
#   end_md       : (month, day) — Gregorian end date (inclusive)
#   date_range_en: Human-readable Gregorian range (English)
#   date_range_zh: Human-readable Gregorian range (Chinese)
#   qualities_en : Short poetic quality/attribute (Graves 1948 themes)
#   qualities_zh : Chinese translation of qualities
#
# Note on Beth (month 1): spans Dec 24 – Jan 20, crossing the Gregorian
# year boundary.  The implementation handles this correctly for any date.

TREE_MONTHS: list[dict] = [
    # ── Month 1: Beth (Birch) ────────────────────────────────────────────
    # NOTE: This month wraps the Gregorian year boundary (Dec 24 → Jan 20).
    # The lookup function handles this via the `wraps_year` flag in
    # `_is_between_md`.  start_md > end_md signals the wrap to the caller.
    {
        "month_number": 1,
        "gaelic": "Beth",
        "english": "Birch",
        "chinese": "樺樹",
        "ogham_letter": "ᚁ",
        "start_md": (12, 24),
        "end_md": (1, 20),
        "date_range_en": "Dec 24 – Jan 20",
        "date_range_zh": "12月24日 – 1月20日",
        "qualities_en": "Inception, purification, new beginnings",
        "qualities_zh": "開創、淨化、新的開始",
    },
    {
        "month_number": 2,
        "gaelic": "Luis",
        "english": "Rowan",
        "chinese": "花楸",
        "ogham_letter": "ᚂ",
        "start_md": (1, 21),
        "end_md": (2, 17),
        "date_range_en": "Jan 21 – Feb 17",
        "date_range_zh": "1月21日 – 2月17日",
        "qualities_en": "Protection, quickening, vision",
        "qualities_zh": "守護、甦醒、洞見",
    },
    {
        "month_number": 3,
        "gaelic": "Nion",
        "english": "Ash",
        "chinese": "白蠟樹",
        "ogham_letter": "ᚅ",
        "start_md": (2, 18),
        "end_md": (3, 17),
        "date_range_en": "Feb 18 – Mar 17",
        "date_range_zh": "2月18日 – 3月17日",
        "qualities_en": "Expansion, connection, world-tree",
        "qualities_zh": "擴展、連結、世界之樹",
    },
    {
        "month_number": 4,
        "gaelic": "Fearn",
        "english": "Alder",
        "chinese": "赤楊",
        "ogham_letter": "ᚃ",
        "start_md": (3, 18),
        "end_md": (4, 14),
        "date_range_en": "Mar 18 – Apr 14",
        "date_range_zh": "3月18日 – 4月14日",
        "qualities_en": "Foundation, resurrection, fire-champion",
        "qualities_zh": "根基、復甦、火之英雄",
    },
    {
        "month_number": 5,
        "gaelic": "Saille",
        "english": "Willow",
        "chinese": "柳樹",
        "ogham_letter": "ᚄ",
        "start_md": (4, 15),
        "end_md": (5, 12),
        "date_range_en": "Apr 15 – May 12",
        "date_range_zh": "4月15日 – 5月12日",
        "qualities_en": "Moon-enchantment, poetry, water-magic",
        "qualities_zh": "月之魔法、詩歌、水之靈",
    },
    {
        "month_number": 6,
        "gaelic": "Uath",
        "english": "Hawthorn",
        "chinese": "山楂",
        "ogham_letter": "ᚆ",
        "start_md": (5, 13),
        "end_md": (6, 9),
        "date_range_en": "May 13 – Jun 9",
        "date_range_zh": "5月13日 – 6月9日",
        "qualities_en": "Restraint, cleansing, sacred boundary",
        "qualities_zh": "克制、淨化、神聖界限",
    },
    {
        "month_number": 7,
        "gaelic": "Duir",
        "english": "Oak",
        "chinese": "橡樹",
        "ogham_letter": "ᚇ",
        "start_md": (6, 10),
        "end_md": (7, 7),
        "date_range_en": "Jun 10 – Jul 7",
        "date_range_zh": "6月10日 – 7月7日",
        "qualities_en": "Sovereignty, midsummer king, door of the year",
        "qualities_zh": "王權、仲夏之王、年之門",
    },
    {
        "month_number": 8,
        "gaelic": "Tinne",
        "english": "Holly",
        "chinese": "冬青",
        "ogham_letter": "ᚈ",
        "start_md": (7, 8),
        "end_md": (8, 4),
        "date_range_en": "Jul 8 – Aug 4",
        "date_range_zh": "7月8日 – 8月4日",
        "qualities_en": "Challenge, trial, midyear battle",
        "qualities_zh": "挑戰、考驗、年中之戰",
    },
    {
        "month_number": 9,
        "gaelic": "Coll",
        "english": "Hazel",
        "chinese": "榛樹",
        "ogham_letter": "ᚉ",
        "start_md": (8, 5),
        "end_md": (9, 1),
        "date_range_en": "Aug 5 – Sep 1",
        "date_range_zh": "8月5日 – 9月1日",
        "qualities_en": "Wisdom, divination, poetic inspiration",
        "qualities_zh": "智慧、占卜、詩意靈感",
    },
    {
        "month_number": 10,
        "gaelic": "Muin",
        "english": "Vine",
        "chinese": "葡萄藤",
        "ogham_letter": "ᚋ",
        "start_md": (9, 2),
        "end_md": (9, 29),
        "date_range_en": "Sep 2 – Sep 29",
        "date_range_zh": "9月2日 – 9月29日",
        "qualities_en": "Harvest, prophecy, joy of intoxication",
        "qualities_zh": "豐收、預言、歡醉之喜",
    },
    {
        "month_number": 11,
        "gaelic": "Gort",
        "english": "Ivy",
        "chinese": "常春藤",
        "ogham_letter": "ᚌ",
        "start_md": (9, 30),
        "end_md": (10, 27),
        "date_range_en": "Sep 30 – Oct 27",
        "date_range_zh": "9月30日 – 10月27日",
        "qualities_en": "Tenacity, spiral journey, resurrection",
        "qualities_zh": "堅韌、螺旋之旅、復活",
    },
    {
        "month_number": 12,
        "gaelic": "Ngetal",
        "english": "Reed",
        "chinese": "蘆葦",
        "ogham_letter": "ᚍ",
        "start_md": (10, 28),
        "end_md": (11, 24),
        "date_range_en": "Oct 28 – Nov 24",
        "date_range_zh": "10月28日 – 11月24日",
        "qualities_en": "Death, regeneration, keeper of secrets",
        "qualities_zh": "死亡、再生、守護秘密",
    },
    {
        "month_number": 13,
        "gaelic": "Ruis",
        "english": "Elder",
        "chinese": "接骨木",
        "ogham_letter": "ᚏ",
        "start_md": (11, 25),
        "end_md": (12, 22),
        "date_range_en": "Nov 25 – Dec 22",
        "date_range_zh": "11月25日 – 12月22日",
        "qualities_en": "Ending, judgment, Crone wisdom",
        "qualities_zh": "終結、審判、老媼智慧",
    },
]

# ════════════════════════════════════════════════════════════════════
# Day of Creation (December 23) — outside the 13 months
# ════════════════════════════════════════════════════════════════════

DAY_OF_CREATION: dict = {
    "month_number": 0,
    "gaelic": "—",
    "english": "Day of Creation",
    "chinese": "創造之日",
    "ogham_letter": "—",
    "start_md": (12, 23),
    "end_md": (12, 23),
    "date_range_en": "Dec 23",
    "date_range_zh": "12月23日",
    "qualities_en": "The nameless day outside the calendar year",
    "qualities_zh": "遊離於年曆之外的無名之日",
}

# ════════════════════════════════════════════════════════════════════
# Graves' note as used in UI and prompt
# ════════════════════════════════════════════════════════════════════

GRAVES_NOTE_ZH = (
    "此為 Robert Graves 1948 年《The White Goddess》所重建的現代樹木曆法，"
    "非古代凱爾特傳統。"
)
GRAVES_NOTE_EN = (
    "Reconstructed by Robert Graves in The White Goddess (1948) — "
    "a poetic tree-alphabet calendar, not historical Celtic astrology."
)


# ════════════════════════════════════════════════════════════════════
# Internal helpers
# ════════════════════════════════════════════════════════════════════

def _date_to_md(d: date) -> tuple[int, int]:
    """Return (month, day) tuple for a date."""
    return (d.month, d.day)


def _is_between_md(
    target_md: tuple[int, int],
    start_md: tuple[int, int],
    end_md: tuple[int, int],
    wraps_year: bool = False,
) -> bool:
    """Check whether *target_md* falls within [start_md, end_md].

    When *wraps_year* is True the range crosses the Dec→Jan boundary
    (Beth: Dec 24 – Jan 20).
    """
    if wraps_year:
        # In range if ≥ start OR ≤ end
        return target_md >= start_md or target_md <= end_md
    return start_md <= target_md <= end_md


# ════════════════════════════════════════════════════════════════════
# Core lookup — O(n) over 13 months, negligible for this use case
# ════════════════════════════════════════════════════════════════════

def lookup_celtic_tree(birth_date: date) -> dict:
    """Return the tree-month dict for *birth_date* (Graves 1948).

    Parameters
    ----------
    birth_date : date
        Gregorian birth date (year is irrelevant — only month/day used).

    Returns
    -------
    dict
        The matching entry from :data:`TREE_MONTHS`, or
        :data:`DAY_OF_CREATION` for December 23.
        Returns an empty dict if no match (should not occur for valid dates).
    """
    md = _date_to_md(birth_date)

    # December 23 — Day of Creation (check before Beth to avoid overlap)
    if md == (12, 23):
        return DAY_OF_CREATION

    for entry in TREE_MONTHS:
        start = entry["start_md"]
        end = entry["end_md"]
        # Beth wraps the Gregorian year boundary
        wraps = start > end  # True only for Beth (Dec 24 → Jan 20)
        if _is_between_md(md, start, end, wraps_year=wraps):
            return entry

    # Fallback — should never be reached for valid calendar dates
    return {}


# ════════════════════════════════════════════════════════════════════
# Public chart dataclass
# ════════════════════════════════════════════════════════════════════

@dataclass
class CelticTreeChart:
    """Result of :func:`compute_celtic_tree_chart`.

    Attributes
    ----------
    birth_date : date
    month_number : int
        1–13, or 0 for Day of Creation.
    tree_name_gaelic : str
        Ogham/Gaelic month name (e.g. "Beth").
    tree_name_english : str
        English tree common name (e.g. "Birch").
    tree_name_chinese : str
        Chinese tree name (e.g. "樺樹").
    date_range_en : str
        Gregorian range string (English), e.g. "Dec 24 – Jan 20".
    date_range_zh : str
        Gregorian range string (Chinese).
    ogham_letter : str
        Unicode Ogham character.
    qualities_en : str
    qualities_zh : str
    note_en : str
        Graves attribution disclaimer (English).
    note_zh : str
        Graves attribution disclaimer (Chinese).
    western_overlap_en : str
        Which Western zodiac sign(s) overlap this month (informational).
    western_overlap_zh : str
    """
    birth_date: date
    month_number: int
    tree_name_gaelic: str
    tree_name_english: str
    tree_name_chinese: str
    date_range_en: str
    date_range_zh: str
    ogham_letter: str
    qualities_en: str
    qualities_zh: str
    note_en: str = GRAVES_NOTE_EN
    note_zh: str = GRAVES_NOTE_ZH
    western_overlap_en: str = ""
    western_overlap_zh: str = ""


# ════════════════════════════════════════════════════════════════════
# Western sign overlap (informational cross-reference)
# ════════════════════════════════════════════════════════════════════

_WESTERN_OVERLAP: dict[int, tuple[str, str]] = {
    1:  ("Capricorn / Aquarius",        "摩羯座 / 水瓶座"),
    2:  ("Aquarius",                    "水瓶座"),
    3:  ("Aquarius / Pisces",           "水瓶座 / 雙魚座"),
    4:  ("Pisces / Aries",              "雙魚座 / 白羊座"),
    5:  ("Aries / Taurus",              "白羊座 / 金牛座"),
    6:  ("Taurus / Gemini",             "金牛座 / 雙子座"),
    7:  ("Gemini / Cancer",             "雙子座 / 巨蟹座"),
    8:  ("Cancer / Leo",                "巨蟹座 / 獅子座"),
    9:  ("Leo / Virgo",                 "獅子座 / 處女座"),
    10: ("Virgo / Libra",               "處女座 / 天秤座"),
    11: ("Libra / Scorpio",             "天秤座 / 天蠍座"),
    12: ("Scorpio / Sagittarius",       "天蠍座 / 射手座"),
    13: ("Sagittarius / Capricorn",     "射手座 / 摩羯座"),
    0:  ("Sagittarius / Capricorn",     "射手座 / 摩羯座"),
}


# ════════════════════════════════════════════════════════════════════
# Public compute function (cached)
# ════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def compute_celtic_tree_chart(
    year: int, month: int, day: int,
    **_kwargs,
) -> CelticTreeChart:
    """Compute a Celtic Tree Calendar chart (Graves 1948) for a birth date.

    Parameters
    ----------
    year, month, day : int
        Gregorian birth date.  The year is only used to construct the
        ``birth_date`` attribute; tree-month lookup uses month/day only.
    **_kwargs
        Extra keyword arguments accepted but ignored (for API
        compatibility with other compute functions that receive location
        data, etc.).

    Returns
    -------
    CelticTreeChart
        Contains tree-month data and cross-reference notes.

    Notes
    -----
    Source: Graves, Robert. *The White Goddess: A Historical Grammar of
    Poetic Myth*. Faber & Faber, London, 1948.
    """
    bd = date(year, month, day)
    entry = lookup_celtic_tree(bd)
    if not entry:
        # Should never happen for a valid date, but guard gracefully
        entry = DAY_OF_CREATION

    mn = entry["month_number"]
    w_en, w_zh = _WESTERN_OVERLAP.get(mn, ("", ""))

    return CelticTreeChart(
        birth_date=bd,
        month_number=mn,
        tree_name_gaelic=entry["gaelic"],
        tree_name_english=entry["english"],
        tree_name_chinese=entry["chinese"],
        date_range_en=entry["date_range_en"],
        date_range_zh=entry["date_range_zh"],
        ogham_letter=entry["ogham_letter"],
        qualities_en=entry["qualities_en"],
        qualities_zh=entry["qualities_zh"],
        note_en=GRAVES_NOTE_EN,
        note_zh=GRAVES_NOTE_ZH,
        western_overlap_en=w_en,
        western_overlap_zh=w_zh,
    )


# ════════════════════════════════════════════════════════════════════
# AI prompt formatter
# ════════════════════════════════════════════════════════════════════

def format_celtic_tree_for_prompt(chart: CelticTreeChart) -> str:
    """Format a CelticTreeChart for the AI analysis prompt.

    Instructs the AI to interpret poetically and cross-reference with
    other systems without adding modern zodiac personality traits.
    """
    lines = [
        "【凱爾特樹木曆法 Celtic Tree Calendar (Robert Graves, The White Goddess 1948)】",
        f"Tree Month (月份): {chart.month_number} — {chart.tree_name_gaelic} ({chart.tree_name_english} / {chart.tree_name_chinese})",
        f"Ogham Letter (歐甘字): {chart.ogham_letter}",
        f"Gregorian Range (格里曆範圍): {chart.date_range_en} ({chart.date_range_zh})",
        f"Poetic Qualities (詩意屬性): {chart.qualities_en} / {chart.qualities_zh}",
        f"Western Zodiac Overlap (西洋占星對應): {chart.western_overlap_en} ({chart.western_overlap_zh})",
        f"Source Note: {chart.note_en}",
        "",
        "AI Instruction: Incorporate Robert Graves' 1948 Beth-Luis-Nion tree calendar "
        "insights poetically and cross-reference with other systems present in this "
        "chart (Western, Vedic, Chinese, etc.) without adding modern zodiac personality "
        "traits.  Treat this as a mythic/poetic layer that enriches — but does not "
        "replace — the other astrological systems.",
    ]
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════
# Streamlit rendering
# ════════════════════════════════════════════════════════════════════

def render_celtic_tree_chart(
    chart: CelticTreeChart,
    after_chart_hook=None,
    lang: str = "zh",
) -> None:
    """Render the Celtic Tree Calendar chart in Streamlit.

    Parameters
    ----------
    chart : CelticTreeChart
    after_chart_hook : callable, optional
        Called after the main chart display (e.g. to render AI button).
    lang : str
        "zh" (Traditional Chinese), "zh_cn" (Simplified), or "en".
    """
    import pandas as pd

    is_zh = lang in ("zh", "zh_cn")

    # ── Disclaimer banner ────────────────────────────────────────────
    if is_zh:
        st.warning(
            "⚠️ " + chart.note_zh,
            icon="🌿",
        )
    else:
        st.warning(
            "⚠️ " + chart.note_en,
            icon="🌿",
        )

    st.divider()

    # ── Main result card ─────────────────────────────────────────────
    is_doc = chart.month_number == 0  # Day of Creation

    col_a, col_b = st.columns([1, 2])
    with col_a:
        # Large ogham glyph display
        glyph = chart.ogham_letter if chart.ogham_letter != "—" else "✦"
        st.markdown(
            f'<div style="font-size:5rem;text-align:center;'
            f'line-height:1.1;padding:0.5rem 0;">{glyph}</div>',
            unsafe_allow_html=True,
        )
        if is_zh:
            st.caption("歐甘字 / Ogham Letter")
        else:
            st.caption("Ogham Letter")

    with col_b:
        if is_doc:
            title_zh = "🌑 創造之日"
            title_en = "🌑 Day of Creation (December 23)"
            desc_zh  = "遊離於13個月之外的無名之日，如 Graves 所言，乃年外之日。"
            desc_en  = ("The extra day outside the 13 tree-months, as described "
                        "by Graves — a nameless day standing outside the calendar year.")
        else:
            num   = chart.month_number
            gaelic  = chart.tree_name_gaelic
            eng   = chart.tree_name_english
            cn    = chart.tree_name_chinese
            title_zh = f"🌳 第{num}月 · {gaelic}（{cn}）"
            title_en = f"🌳 Month {num} · {gaelic} ({eng})"
            desc_zh  = chart.qualities_zh
            desc_en  = chart.qualities_en

        if is_zh:
            st.subheader(title_zh)
            st.markdown(f"**{desc_zh}**")
            st.caption(f"格里曆範圍：{chart.date_range_zh}")
        else:
            st.subheader(title_en)
            st.markdown(f"**{desc_en}**")
            st.caption(f"Gregorian range: {chart.date_range_en}")

    st.divider()

    # ── Full 13-month reference table ────────────────────────────────
    if is_zh:
        st.markdown("#### 🌿 13月樹木曆對照表 (Graves 1948)")
        st.caption(
            "Robert Graves《The White Goddess》1948年版 Beth-Luis-Nion 樹木字母曆。"
            "每月 ~28 天，以歐甘字母命名。"
        )
    else:
        st.markdown("#### 🌿 Full 13-Month Tree Calendar (Graves 1948)")
        st.caption(
            "Beth-Luis-Nion tree-alphabet calendar from Robert Graves' "
            "*The White Goddess* (1948).  Each month ~28 days, named after Ogham letters."
        )

    rows = []
    for entry in TREE_MONTHS:
        is_current = (entry["month_number"] == chart.month_number)
        marker = "✅ " if is_current else ""
        if is_zh:
            rows.append({
                "": marker,
                "月份 / Month": f"#{entry['month_number']}",
                "歐甘字": entry["ogham_letter"],
                "蓋爾語名": entry["gaelic"],
                "英文樹名": entry["english"],
                "中文樹名": entry["chinese"],
                "格里曆日期": entry["date_range_zh"],
                "詩意屬性": entry["qualities_zh"],
            })
        else:
            rows.append({
                "": marker,
                "Month #": f"#{entry['month_number']}",
                "Ogham": entry["ogham_letter"],
                "Gaelic Name": entry["gaelic"],
                "Tree (EN)": entry["english"],
                "Tree (CN)": entry["chinese"],
                "Date Range": entry["date_range_en"],
                "Qualities": entry["qualities_en"],
            })

    # Day of Creation row
    doc = DAY_OF_CREATION
    is_doc_row = (chart.month_number == 0)
    marker = "✅ " if is_doc_row else ""
    if is_zh:
        rows.append({
            "": marker,
            "月份 / Month": "—",
            "歐甘字": doc["ogham_letter"],
            "蓋爾語名": doc["gaelic"],
            "英文樹名": doc["english"],
            "中文樹名": doc["chinese"],
            "格里曆日期": doc["date_range_zh"],
            "詩意屬性": doc["qualities_zh"],
        })
    else:
        rows.append({
            "": marker,
            "Month #": "—",
            "Ogham": doc["ogham_letter"],
            "Gaelic Name": doc["gaelic"],
            "Tree (EN)": doc["english"],
            "Tree (CN)": doc["chinese"],
            "Date Range": doc["date_range_en"],
            "Qualities": doc["qualities_en"],
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, width="stretch")

    st.divider()

    # ── Cross-reference with Western zodiac ─────────────────────────
    if not is_doc:
        if is_zh:
            st.markdown("#### 🔀 跨系統對照 — 西洋占星重疊")
            st.info(
                f"**{chart.tree_name_gaelic}月**（{chart.tree_name_english} / "
                f"{chart.tree_name_chinese}）與西洋占星的"
                f"**{chart.western_overlap_zh}**時段重疊。\n\n"
                "注：樹木月份由格里曆固定日期劃定，與黃道12星座的季節能量有自然重疊，"
                "但兩套體系的分析邏輯不同，僅供參考。"
            )
        else:
            st.info(
                f"**{chart.tree_name_gaelic}** ({chart.tree_name_english}) "
                f"overlaps with the Western zodiac period of "
                f"**{chart.western_overlap_en}**.\n\n"
                "Note: The tree months use fixed Gregorian dates.  The overlap "
                "with Western signs is informational only — the two systems use "
                "different analytical frameworks."
            )

    st.divider()

    # ── About / tooltip expander ─────────────────────────────────────
    if is_zh:
        with st.expander("ℹ️ 關於凱爾特樹木曆法 — Robert Graves 1948", expanded=False):
            st.markdown("""
**凱爾特樹木曆法（Beth-Luis-Nion）** 是英國詩人兼學者 Robert Graves（1895–1985）
在其1948年著作《The White Goddess: A Historical Grammar of Poetic Myth》中提出的
詩意神話日曆體系。

### 主要特點
- **13個月**，每月約28天，對應13個歐甘字母（Ogham consonants）
- 以樹木命名，體現凱爾特神話中樹木崇拜的詩意傳統
- 每年12月23日為「**創造之日**」（Day of Creation），遊離於13個月之外
- 全年始於**12月24日**（Beth月 / 樺樹月）

### ⚠️ 重要說明
此體系**不是**古代凱爾特人的實際曆法或占星傳統。它是 Graves 根據歐甘字母、
白女神神話及詩意想象所**重建的現代詩意體系**。現代學術界對其歷史真實性存有爭議。

> *"The White Goddess"* — Robert Graves, Faber & Faber, London, 1948
""")
    else:
        with st.expander("ℹ️ About the Celtic Tree Calendar — Robert Graves 1948", expanded=False):
            st.markdown("""
The **Celtic Tree Calendar (Beth-Luis-Nion)** is a poetic/mythic calendar
devised by British poet and scholar Robert Graves (1895–1985) in his 1948
work *The White Goddess: A Historical Grammar of Poetic Myth*.

### Key Features
- **13 months** of ~28 days each, corresponding to 13 Ogham consonants
- Named after trees, reflecting the poetic tradition of tree-lore in
  Celtic mythology as interpreted by Graves
- December 23 is the **Day of Creation** — a day outside the 13 months
- The year begins on **December 24** (Beth / Birch month)

### ⚠️ Important Notice
This system is **not** an actual ancient Celtic calendar or astrological
tradition.  It is a **modern poetic reconstruction** by Graves, based on
Ogham letters, White Goddess mythology, and speculative etymology.
Its historical accuracy is disputed by modern scholarship.

> *The White Goddess* — Robert Graves, Faber & Faber, London, 1948
""")

    # ── After-chart hook (e.g. AI button) ───────────────────────────
    if after_chart_hook is not None:
        after_chart_hook()
