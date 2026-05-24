"""
MS.164 手稿瀏覽器 — Dropsie College 阿拉伯占星與魔法手稿

載入並渲染以下 JSON 資料：
  • fal_divination.json   — 占卜問答表 (fāl)
  • female_appearances.json — 女性命盤外貌描述
  • female_horoscopes.json  — 女性完整命盤
  • magical_practices.json  — 魔法配方與護身符
  • metadata.json           — 手稿後設資料
"""

from __future__ import annotations

import json
import os

import streamlit as st

_DATA_DIR = os.path.join(
    os.path.dirname(__file__), os.pardir, "data", "arabic", "ms164"
)


@st.cache_data(show_spinner=False)
def _load_ms164(filename: str) -> dict:
    path = os.path.join(_DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_metadata() -> dict:
    return _load_ms164("metadata.json")


def load_fal_divination() -> dict:
    return _load_ms164("fal_divination.json")


def load_female_appearances() -> dict:
    return _load_ms164("female_appearances.json")


def load_female_horoscopes() -> dict:
    return _load_ms164("female_horoscopes.json")


def load_magical_practices() -> dict:
    return _load_ms164("magical_practices.json")


# ── Rendering ────────────────────────────────────────────────────────────

def render_ms164_browse() -> None:
    """Render the full MS.164 manuscript browser (no chart data needed)."""
    meta = load_metadata()
    st.subheader(f"📜 {meta.get('title_zh', 'MS.164 手稿')} ({meta.get('title_en', '')})")
    st.caption(
        f"來源：{meta.get('source', '')} · "
        f"語言：{meta.get('language', '')} · "
        f"約 {meta.get('approx_date', '')} · "
        f"{meta.get('total_pages', '')} 頁"
    )
    st.markdown(f"_{meta.get('description_zh', '')}_")

    tabs = st.tabs([
        "🔮 占卜問答 (Fāl)", "👩 女性外貌", "♀️ 女性命盤",
        "🧙 魔法配方",
    ])

    with tabs[0]:
        _render_fal_divination()

    with tabs[1]:
        _render_female_appearances()

    with tabs[2]:
        _render_female_horoscopes()

    with tabs[3]:
        _render_magical_practices()


def _render_fal_divination() -> None:
    data = load_fal_divination()
    meta = data.get("metadata", {})
    st.markdown(f"**{meta.get('description_zh', '')}**")
    st.caption(f"頁碼：{meta.get('pages', '')}")

    for planet in data.get("planets", []):
        planet_label = f"{planet.get('planet_zh', '')} ({planet.get('planet_ar', '')})"
        with st.expander(f"🪐 {planet_label}", expanded=False):
            for q in planet.get("questions", []):
                st.markdown(
                    f"**問：** {q.get('question_zh', '')}  \n"
                    f"**答：** {q.get('answer_zh', '')}  \n"
                    f"<small>阿拉伯文問：{q.get('question_ar', '')} · "
                    f"答：{q.get('answer_ar', '')} · "
                    f"p.{q.get('page_ref', '')}</small>",
                    unsafe_allow_html=True,
                )
                st.markdown("---")


def _render_female_appearances() -> None:
    data = load_female_appearances()
    meta = data.get("metadata", {})
    st.markdown(f"**{meta.get('description_zh', '')}**")

    for entry in data.get("appearances", []):
        zodiac = entry.get("zodiac_zh", "")
        planet = entry.get("planet_zh", "")
        with st.expander(f"♈ {zodiac} / {planet}", expanded=False):
            st.markdown(entry.get("appearance_zh", ""))
            details = entry.get("appearance_details", {})
            if details:
                for k, v in details.items():
                    st.markdown(f"- **{k}**: {v}")
            if entry.get("page_ref"):
                st.caption(f"頁碼：{entry['page_ref']}")


def _render_female_horoscopes() -> None:
    data = load_female_horoscopes()
    meta = data.get("metadata", {})
    st.markdown(f"**{meta.get('description_zh', '')}**")

    for h in data.get("horoscopes", []):
        zodiac = h.get("zodiac_zh", "")
        planet = h.get("planet_zh", "")
        with st.expander(f"♈ {zodiac} / {planet}", expanded=False):
            st.markdown(f"**描述：** {h.get('description_zh', '')}")

            appearance = h.get("appearance", {})
            if appearance:
                st.markdown("**外貌特徵：**")
                for k, v in appearance.items():
                    st.markdown(f"- {k}: {v}")

            personality = h.get("personality", [])
            if personality:
                st.markdown(f"**性格：** {', '.join(personality)}")

            fortune = h.get("fortune", [])
            if fortune:
                st.markdown(f"**命運：** {', '.join(fortune)}")

            advice = h.get("advice", [])
            if advice:
                st.markdown("**建議：**")
                for a in advice:
                    st.markdown(f"- {a}")

            if h.get("page_ref"):
                st.caption(f"頁碼：{h['page_ref']}")


def _render_magical_practices() -> None:
    data = load_magical_practices()
    meta = data.get("metadata", {})
    st.markdown(f"**{meta.get('description_zh', '')}**")

    for p in data.get("practices", []):
        purpose = p.get("purpose_zh", "未知")
        with st.expander(f"🔮 {purpose}", expanded=False):
            st.markdown(f"**配方：** {p.get('recipe_zh', '')}")

            ingredients = p.get("ingredients", [])
            if ingredients:
                st.markdown(f"**材料：** {', '.join(ingredients)}")

            if p.get("timing"):
                st.markdown(f"**時機：** {p['timing']}")

            if p.get("method"):
                st.markdown(f"**方法：** {p['method']}")

            talisman_names = p.get("talisman_names", [])
            if talisman_names:
                st.markdown(f"**護身符銘刻名號：** {', '.join(talisman_names)}")

            if p.get("page_ref"):
                st.caption(f"頁碼：{p['page_ref']}")
