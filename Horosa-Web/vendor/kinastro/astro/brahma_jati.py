"""
พรหมชาติ (Brahma Jati) — 泰國傳統命理模組

根據出生年份（12 生肖）、出生月份、出生星期提供：
  • 出生年人格與命理基礎
  • 月份細分變體（白腹鼠/條紋鼠/鬼鼠…等）
  • 星期細分變體（天神鼠/水神鼠/火神鼠…等）
  • 12 ราศี 年運輪（佛塔→銀傘→斷頸…）
  • 符咒改運法（顏色、護身符、儀式）
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Optional

import streamlit as st

_DATA_DIR = os.path.join(os.path.dirname(__file__), "thai", "data")

# ── 泰國 12 生肖 Thai → numeric id mapping ──────────────────────────────
_THAI_YEAR_NAMES = [
    "ปีชวด", "ปีฉลู", "ปีขาล", "ปีเถาะ",
    "ปีมะโรง", "ปีมะเส็ง", "ปีมะเมีย", "ปีมะแม",
    "ปีวอก", "ปีระกา", "ปีจอ", "ปีกุน",
]

# CE year → Thai zodiac index (0‑based, Rat=0).  Thai cycle follows Chinese
# zodiac but shifted: CE year 4 ≡ Rat (ปีชวด).
_CYCLE_OFFSET = 4


def _thai_zodiac_index(ce_year: int) -> int:
    """Return 0‑based Thai zodiac index for a CE year (0=Rat … 11=Pig)."""
    return (ce_year - _CYCLE_OFFSET) % 12


_DAY_NAMES_EN = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]

# Python weekday() returns 0=Mon … 6=Sun
_WEEKDAY_TO_EN = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
    4: "Friday", 5: "Saturday", 6: "Sunday",
}


# ── JSON Loaders (cached) ───────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _load_json(filename: str) -> dict:
    path = os.path.join(_DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_birthyear_data() -> dict:
    return _load_json("brahma_jati_birthyear.json")


def load_12rasi_data() -> dict:
    return _load_json("brahma_jati_12rasi.json")


def load_monthly_variants() -> dict:
    return _load_json("brahma_jati_monthly_variants.json")


def load_weekly_variants() -> dict:
    return _load_json("brahma_jati_weekly_variants.json")


def load_spells_remedies() -> dict:
    return _load_json("brahma_jati_spells_remedies.json")


# ── Computation helpers ──────────────────────────────────────────────────

@dataclass
class BrahmaJatiReading:
    """Aggregated Brahma Jati reading for a person."""
    ce_year: int
    zodiac_index: int          # 0‑based
    thai_year_name: str        # e.g. "ปีชวด"
    year_zh: str               # e.g. "鼠年"
    year_en: str               # e.g. "Rat Year"
    # Birthyear personality
    birthyear: dict            # full entry from birthyear JSON
    # Monthly variant (may be None if month not matched)
    monthly_variant: Optional[dict] = None
    monthly_variant_months: Optional[str] = None
    # Weekly variant (may be None if weekday unknown)
    weekly_variant: Optional[dict] = None
    weekly_day: Optional[str] = None
    # 12 rasi annual position
    rasi_position: Optional[dict] = None
    rasi_pos_number: Optional[int] = None
    # Gender for rasi calculation
    gender: Optional[str] = None
    age: Optional[int] = None
    # Spells & remedies
    color_of_day: Optional[dict] = None
    zodiac_remedy: Optional[dict] = None
    general_remedies: Optional[dict] = None


def _find_monthly_variant(monthly_data: dict, thai_year: str, month: int):
    """Find the monthly variant for a given Thai year and birth month."""
    year_entry = monthly_data.get("years", {}).get(thai_year)
    if not year_entry:
        return None, None
    for month_range_str, variant in year_entry.get("variants", {}).items():
        months = [int(m) for m in month_range_str.split("-")]
        if month in months:
            return variant, month_range_str
    return None, None


def _compute_rasi_position(age: int, gender: str, rasi_data: dict):
    """
    Compute the 12-rasi position for a given age and gender.
    Male: count clockwise from position 1.
    Female: count counter-clockwise from position 1.
    Returns (position_number, position_dict).
    """
    if age < 1:
        return None, None
    positions = rasi_data.get("positions", {})
    n = len(positions)  # 12
    if n == 0:
        return None, None
    if gender == "male":
        idx = ((age - 1) % n) + 1
    else:
        idx = (-(age - 1) % n) + 1
        if idx < 1:
            idx += n
    pos = positions.get(str(idx))
    return idx, pos


def compute_brahma_jati(
    ce_year: int,
    month: int,
    weekday: int,  # Python weekday: 0=Mon … 6=Sun
    age: Optional[int] = None,
    gender: Optional[str] = None,  # "male" or "female"
) -> BrahmaJatiReading:
    """Compute a full Brahma Jati reading."""
    zi = _thai_zodiac_index(ce_year)
    thai_name = _THAI_YEAR_NAMES[zi]

    by_data = load_birthyear_data()
    by_entry = by_data.get("years", {}).get(str(zi + 1), {})

    # Monthly
    mv_data = load_monthly_variants()
    mv, mv_months = _find_monthly_variant(mv_data, thai_name, month)

    # Weekly
    wv_data = load_weekly_variants()
    day_en = _WEEKDAY_TO_EN.get(weekday, "Monday")
    wv_year = wv_data.get("years", {}).get(thai_name, {})
    wv = wv_year.get("weekly", {}).get(day_en)

    # 12 Rasi position
    rasi_data = load_12rasi_data()
    rasi_pos_num, rasi_pos = None, None
    if age is not None and gender is not None:
        rasi_pos_num, rasi_pos = _compute_rasi_position(age, gender, rasi_data)

    # Spells & remedies
    sr_data = load_spells_remedies()
    color = sr_data.get("color_by_day", {}).get(day_en)
    zodiac_remedy = sr_data.get("per_zodiac", {}).get(thai_name)
    general_remedies = sr_data.get("general_remedies")

    return BrahmaJatiReading(
        ce_year=ce_year,
        zodiac_index=zi,
        thai_year_name=thai_name,
        year_zh=by_entry.get("name_zh", ""),
        year_en=by_entry.get("name_en", ""),
        birthyear=by_entry,
        monthly_variant=mv,
        monthly_variant_months=mv_months,
        weekly_variant=wv,
        weekly_day=day_en,
        rasi_position=rasi_pos,
        rasi_pos_number=rasi_pos_num,
        gender=gender,
        age=age,
        color_of_day=color,
        zodiac_remedy=zodiac_remedy,
        general_remedies=general_remedies,
    )


# ── Rendering ────────────────────────────────────────────────────────────

def render_brahma_jati(reading: BrahmaJatiReading) -> None:
    """Render the full Brahma Jati reading in Streamlit."""
    _render_birthyear_section(reading)
    st.divider()
    _render_monthly_section(reading)
    st.divider()
    _render_weekly_section(reading)
    st.divider()
    _render_rasi_section(reading)
    st.divider()
    _render_remedies_section(reading)


def _render_birthyear_section(r: BrahmaJatiReading) -> None:
    by = r.birthyear
    if not by:
        return
    st.subheader(f"🐾 出生年命格：{r.thai_year_name} {r.year_zh} ({r.year_en})")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("五行 (ธาตุ)", f"{by.get('element_zh', '')} / {by.get('element_thai', '')}")
    with col2:
        st.metric("神性 (ชันยา)", f"{by.get('chanya_zh', '')} / {by.get('chanya_thai', '')}")
    with col3:
        st.metric("靈樹 (มิ่งขวัญ)", by.get("mingkwan_zh", ""))

    st.markdown(f"**個性解讀：** {by.get('personality_zh', '')}")
    if by.get("personality_en"):
        st.caption(by["personality_en"])
    if by.get("note"):
        st.info(f"📌 {by['note']}")


def _render_monthly_section(r: BrahmaJatiReading) -> None:
    st.subheader("📅 月份細分變體")
    if r.monthly_variant:
        mv = r.monthly_variant
        st.markdown(
            f"**出生月份 {r.monthly_variant_months} → "
            f"{mv.get('type_zh', '')} ({mv.get('type_en', '')})**"
        )
        st.markdown(f"🔮 {mv.get('meaning_zh', '')}")
        if mv.get("meaning_en"):
            st.caption(mv["meaning_en"])
    else:
        st.info("未能匹配到月份變體資料。")

    # Show all variants in expander for reference
    mv_data = load_monthly_variants()
    year_entry = mv_data.get("years", {}).get(r.thai_year_name)
    if year_entry:
        with st.expander(f"📋 {r.year_zh}全部月份變體", expanded=False):
            for months_str, v in year_entry.get("variants", {}).items():
                st.markdown(
                    f"- **月份 {months_str}** → {v.get('type_zh', '')} "
                    f"({v.get('type_en', '')}): {v.get('meaning_zh', '')}"
                )


def _render_weekly_section(r: BrahmaJatiReading) -> None:
    st.subheader("📆 星期細分變體")
    if r.weekly_variant:
        wv = r.weekly_variant
        st.markdown(
            f"**出生星期 {r.weekly_day} → "
            f"{wv.get('type_zh', '')} ({wv.get('type_en', '')})**"
        )
        st.markdown(f"🔮 {wv.get('meaning_zh', '')}")
        if wv.get("meaning_en"):
            st.caption(wv["meaning_en"])
    else:
        st.info("未能匹配到星期變體資料。")

    # Show all weekly variants in expander
    wv_data = load_weekly_variants()
    year_entry = wv_data.get("years", {}).get(r.thai_year_name)
    if year_entry:
        with st.expander(f"📋 {r.year_zh}全部星期變體", expanded=False):
            for day_en, v in year_entry.get("weekly", {}).items():
                st.markdown(
                    f"- **{day_en}** → {v.get('type_zh', '')} "
                    f"({v.get('type_en', '')}): {v.get('meaning_zh', '')}"
                )


def _render_rasi_section(r: BrahmaJatiReading) -> None:
    st.subheader("🔄 12 ราศี 年運輪")
    if r.rasi_position and r.rasi_pos_number:
        pos = r.rasi_position
        level = pos.get("level", "")
        level_icon = {"大吉": "🎉", "吉": "✨", "凶": "⚠️", "大凶": "💀"}.get(level, "")
        st.markdown(
            f"### {level_icon} 第 {r.rasi_pos_number} 宮 — "
            f"{pos.get('name_zh', '')} ({pos.get('thai', '')} / {pos.get('name_en', '')})"
        )
        st.markdown(f"**吉凶等級：** {level}")
        st.markdown(f"**解讀：** {pos.get('meaning_zh', '')}")
        if pos.get("meaning_en"):
            st.caption(pos["meaning_en"])
    else:
        st.info("需要年齡與性別才能計算年運輪位置。")

    # Show all 12 positions
    rasi_data = load_12rasi_data()
    with st.expander("📋 12 ราศี 完整列表", expanded=False):
        st.markdown(f"**規則：** {rasi_data.get('rules', {}).get('male', '')} / {rasi_data.get('rules', {}).get('female', '')}")
        for k, pos in rasi_data.get("positions", {}).items():
            lvl = pos.get("level", "")
            icon = {"大吉": "🎉", "吉": "✨", "凶": "⚠️", "大凶": "💀"}.get(lvl, "")
            st.markdown(
                f"**{k}. {pos.get('name_zh', '')}** ({pos.get('thai', '')}) "
                f"— {icon} {lvl}: {pos.get('meaning_zh', '')}"
            )


def _render_remedies_section(r: BrahmaJatiReading) -> None:
    st.subheader("🔮 改運法（符咒、護身物、顏色）")

    # Lucky color for birth weekday
    if r.color_of_day:
        c = r.color_of_day
        st.markdown(
            f"**{r.weekly_day} 幸運色：** {c.get('zh', '')} ({c.get('en', '')}) "
            f"— {c.get('meaning', '')}"
        )

    # Zodiac-specific remedy
    if r.zodiac_remedy:
        zr = r.zodiac_remedy
        st.markdown(f"**{r.year_zh}專屬護身符：** {zr.get('talisman', '')}")
        st.markdown(f"**{r.year_zh}專屬儀式：** {zr.get('ritual', '')}")

    # General remedies
    if r.general_remedies:
        with st.expander("📋 通用改運法", expanded=False):
            for k, v in r.general_remedies.items():
                st.markdown(f"{k}. {v}")

    # Color reference table
    sr_data = load_spells_remedies()
    colors = sr_data.get("color_by_day", {})
    if colors:
        with st.expander("🌈 星期幸運色一覽", expanded=False):
            for day, info in colors.items():
                st.markdown(
                    f"- **{day}**: {info.get('zh', '')} ({info.get('en', '')}) "
                    f"— {info.get('meaning', '')}"
                )


def render_brahma_jati_browse() -> None:
    """Render a browse-only view (no birth data required)."""
    st.subheader("📖 พรหมชาติ 命理參考瀏覽 (Brahma Jati Reference)")
    st.caption("泰國傳統พรหมชาติ 12 生肖命理完整參考。無需排盤資料。")

    browse_tabs = st.tabs([
        "🐾 12 生肖命格", "📅 月份變體", "📆 星期變體",
        "🔄 12 年運輪", "🔮 改運法",
    ])

    with browse_tabs[0]:
        by_data = load_birthyear_data()
        for k, v in by_data.get("years", {}).items():
            with st.expander(
                f"{v.get('name_zh', '')} {v.get('thai', '')} ({v.get('name_en', '')})",
                expanded=False,
            ):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**五行：** {v.get('element_zh', '')}")
                with col2:
                    st.markdown(f"**神性：** {v.get('chanya_zh', '')}")
                with col3:
                    st.markdown(f"**靈樹：** {v.get('mingkwan_zh', '')}")
                st.markdown(f"**個性：** {v.get('personality_zh', '')}")
                if v.get("personality_en"):
                    st.caption(v["personality_en"])

    with browse_tabs[1]:
        mv_data = load_monthly_variants()
        for thai_name, year_entry in mv_data.get("years", {}).items():
            with st.expander(
                f"{year_entry.get('name_zh', '')} ({thai_name})", expanded=False,
            ):
                for months_str, variant in year_entry.get("variants", {}).items():
                    st.markdown(
                        f"- **月份 {months_str}** → {variant.get('type_zh', '')} "
                        f"({variant.get('type_en', '')}): {variant.get('meaning_zh', '')}"
                    )

    with browse_tabs[2]:
        wv_data = load_weekly_variants()
        for thai_name, year_entry in wv_data.get("years", {}).items():
            with st.expander(
                f"{year_entry.get('name_zh', '')} ({thai_name})", expanded=False,
            ):
                for day_en, variant in year_entry.get("weekly", {}).items():
                    st.markdown(
                        f"- **{day_en}** → {variant.get('type_zh', '')} "
                        f"({variant.get('type_en', '')}): {variant.get('meaning_zh', '')}"
                    )

    with browse_tabs[3]:
        rasi_data = load_12rasi_data()
        rules = rasi_data.get("rules", {})
        st.info(f"📌 男性：{rules.get('male', '')} ｜ 女性：{rules.get('female', '')}")
        for k, pos in rasi_data.get("positions", {}).items():
            lvl = pos.get("level", "")
            icon = {"大吉": "🎉", "吉": "✨", "凶": "⚠️", "大凶": "💀"}.get(lvl, "")
            st.markdown(
                f"**{k}. {pos.get('name_zh', '')}** ({pos.get('thai', '')}) "
                f"— {icon} {lvl}: {pos.get('meaning_zh', '')}"
            )

    with browse_tabs[4]:
        sr_data = load_spells_remedies()
        st.markdown("### 🌈 星期幸運色")
        for day, info in sr_data.get("color_by_day", {}).items():
            st.markdown(
                f"- **{day}**: {info.get('zh', '')} ({info.get('en', '')}) "
                f"— {info.get('meaning', '')}"
            )
        st.markdown("### 🔮 通用改運法")
        for k, v in sr_data.get("general_remedies", {}).items():
            st.markdown(f"{k}. {v}")
        st.markdown("### 🐾 各生肖專屬改運")
        for thai_name, zr in sr_data.get("per_zodiac", {}).items():
            st.markdown(f"- **{thai_name}**: 護身符 — {zr.get('talisman', '')} ｜ 儀式 — {zr.get('ritual', '')}")
