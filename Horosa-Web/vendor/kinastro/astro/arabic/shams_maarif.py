"""
Shams al-Maʻārif al-Kubrā (太陽知識大全) — Streamlit rendering module

Renders all data from the five Shams al-Maʻārif modules as interactive
Streamlit sub-tabs:
  1. 七大行星特性 (Planetary Properties)
  2. 十二星座徵兆 (Zodiac Signs)
  3. 方陣與神名 (Wafq & Asmāʼ al-Ḥusnā)
  4. 修持法 (Riyāḍa)
  5. 祈禱文 (Duas)
"""

import streamlit as st
from typing import Optional

from .arabic_planetaries import PlanetaryProperties
from .arabic_zodiacsigns import ZodiacSigns
from .arabic_spells import IslamicDuas
from .riyada import ShamsRiyada
from .wafq import IslamicWafqGenerator


# ── singletons ──────────────────────────────────────────────────────────────
_planets = PlanetaryProperties()
_zodiac = ZodiacSigns()
_duas = IslamicDuas()
_riyada = ShamsRiyada()
_wafq = IslamicWafqGenerator()


# ============================================================
# Public API — called from app.py
# ============================================================

def render_shams_browse():
    """Render all Shams al-Maʻārif reference material (no birth chart needed)."""
    stab_planets, stab_zodiac, stab_wafq, stab_riyada, stab_duas = st.tabs([
        "☪ 七大行星特性",
        "🔯 十二星座徵兆",
        "🔢 方陣與神名",
        "🕌 修持法 (Riyāḍa)",
        "📿 祈禱文 (Du'a)",
    ])

    with stab_planets:
        _render_planetary_properties()
    with stab_zodiac:
        _render_zodiac_signs()
    with stab_wafq:
        _render_wafq_tools()
    with stab_riyada:
        _render_riyada()
    with stab_duas:
        _render_duas()


def render_shams_chart(chart_planets: Optional[dict] = None,
                       birth_sign_idx: Optional[int] = None):
    """Render Shams al-Maʻārif with optional birth chart context.

    Parameters
    ----------
    chart_planets : dict, optional
        Mapping ``{english_name: longitude}`` from the Arabic chart, used to
        highlight birth-relevant planetary properties and zodiac signs.
    birth_sign_idx : int, optional
        Index (0-11) of the birth-chart Sun sign, used to highlight the
        corresponding zodiac sign entry.
    """
    stab_planets, stab_zodiac, stab_wafq, stab_riyada, stab_duas = st.tabs([
        "☪ 七大行星特性",
        "🔯 十二星座徵兆",
        "🔢 方陣與神名",
        "🕌 修持法 (Riyāḍa)",
        "📿 祈禱文 (Du'a)",
    ])

    with stab_planets:
        _render_planetary_properties(chart_planets)
    with stab_zodiac:
        _render_zodiac_signs(birth_sign_idx)
    with stab_wafq:
        _render_wafq_tools()
    with stab_riyada:
        _render_riyada()
    with stab_duas:
        _render_duas()


# ============================================================
# Internal renderers
# ============================================================

def _render_planetary_properties(chart_planets: Optional[dict] = None):
    """七大行星詳細特性 — 來自《Laṭāʼif al-Ishāra fī Khaṣāʼiṣ al-Kawākib al-Sayyāra》"""
    st.markdown("#### ☪ 七大行星特性 (Seven Planetary Properties)")
    st.caption("資料來源：《Shams al-Maʻārif al-Kubrā》附錄《لطائف الإشارة في خصائص الكواكب السيارة》")

    for p in _planets.list_all():
        label = f"**{p['arabic']}** {p['english']}"
        if chart_planets and p["english"].lower() in {k.lower() for k in chart_planets}:
            label += "  ⭐ _（出生盤行星）_"

        with st.expander(label):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**阿拉伯名 (Arabic):** {p['arabic']}")
                st.write(f"**英文名 (English):** {p['english']}")
                st.write(f"**體質 (Temperament):** {p['temp']}")
                st.write(f"**元素 (Element):** {p['element']}")
                st.write(f"**顏色 (Colour):** {p['color']}")
            with c2:
                st.write(f"**對應字母 (Letter):** {p['letter']}")
                st.write(f"**推薦方陣 (Wafq):** {p['wafq_size']}×{p['wafq_size']}")
                st.write(f"**建議時辰 (Timing):** {p['timing']}")
            st.write(f"**徵兆 (Omens):** {p['omens']}")
            st.write(f"**護符用途 (Talisman Use):** {p['talisman_use']}")
            st.info(f"📝 {p['note']}")


def _render_zodiac_signs(birth_sign_idx: Optional[int] = None):
    """十二星座徵兆 — 來自《Zahr al-Murūj fī Dalā'il al-Burūj》"""
    st.markdown("#### 🔯 十二星座徵兆 (Twelve Zodiac Sign Omens)")
    st.caption("資料來源：《Shams al-Maʻārif al-Kubrā》附錄《زهر المروج في دلائل البروج》")

    for s in _zodiac.list_all():
        idx = s["no"] - 1
        label = f"**{s['no']}. {s['arabic']}** ({s['english']})"
        if birth_sign_idx is not None and idx == birth_sign_idx:
            label += "  ⭐ _（出生太陽星座）_"

        with st.expander(label):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**阿拉伯名 (Arabic):** {s['arabic']}")
                st.write(f"**英文名 (English):** {s['english']}")
                st.write(f"**元素 (Element):** {s['element']}")
            with c2:
                st.write(f"**主宰行星 (Ruler):** {s['ruler']}")
                st.write(f"**建議時辰 (Timing):** {s['timing']}")
            st.write(f"**徵兆 (Omens):** {s['omens']}")
            st.write(f"**護符用途 (Talisman Use):** {s['talisman_use']}")


def _render_wafq_tools():
    """方陣與神名 — 書中核心技法"""
    st.markdown("#### 🔢 方陣與九十九美名 (Wafq & Asmāʼ al-Ḥusnā)")
    st.caption("資料來源：《Shams al-Maʻārif al-Kubrā》第16章起")

    # ── Abjad calculator ────────────────────────────────────────────────────
    st.markdown("##### 📐 Abjad 數值計算器")
    arabic_input = st.text_input(
        "輸入阿拉伯文 (Arabic text)",
        placeholder="例如：ودود",
        key="shams_abjad_input",
    )
    if arabic_input:
        val = _wafq.get_abjad_value(arabic_input)
        st.success(f"「{arabic_input}」的 Abjad 數值 = **{val}**")

    st.divider()

    # ── Magic square generator ──────────────────────────────────────────────
    st.markdown("##### 🔲 方陣生成器 (Magic Square Generator)")
    sq_size = st.selectbox(
        "方陣階數 (Square size)",
        options=[3, 4, 5, 7, 9],
        index=1,
        key="shams_sq_size",
    )
    if st.button("生成方陣", key="shams_gen_sq"):
        try:
            square = _wafq.generate_magic_square(sq_size)
            # Render as markdown table
            header = "| " + " | ".join(f"**{i+1}**" for i in range(sq_size)) + " |"
            sep = "| " + " | ".join(":---:" for _ in range(sq_size)) + " |"
            rows = [header, sep]
            for row in square:
                rows.append("| " + " | ".join(str(n) for n in row) + " |")
            st.markdown("\n".join(rows))
            magic_const = sq_size * (sq_size * sq_size + 1) // 2
            st.caption(f"魔術常數 (Magic constant) = {magic_const}")
        except ValueError as exc:
            st.error(str(exc))

    st.divider()

    # ── 99 Names browser ────────────────────────────────────────────────────
    st.markdown("##### 📿 九十九美名速查 (99 Beautiful Names)")

    search_name = st.text_input(
        "搜尋美名 (Search by Arabic or Roman name)",
        placeholder="例如：الودود 或 al-Wadud",
        key="shams_asma_search",
    )

    names_to_show = _wafq.ASMA_HUSNA
    if search_name:
        query = search_name.lower().strip()
        names_to_show = {
            k: v for k, v in _wafq.ASMA_HUSNA.items()
            if query in k or query in v.get("roman", "").lower()
        }

    if not names_to_show:
        st.info("沒有找到符合的美名。")
    else:
        header = "| 阿拉伯名 | 羅馬拼音 | 對應行星 | 用途 | 建議時辰 |"
        sep = "|:---:|:---:|:---:|:---|:---:|"
        rows = [header, sep]
        for arabic, info in names_to_show.items():
            rows.append(
                f"| {arabic} | {info['roman']} | {info['planet']} "
                f"| {info['use']} | {info['timing']} |"
            )
        st.markdown("\n".join(rows))
        st.caption(f"共 {len(names_to_show)} 個美名")


def _render_riyada():
    """修持法 (Riyāḍa) 與香料配方"""
    st.markdown("#### 🕌 修持法 (Riyāḍa Practices)")
    st.caption("資料來源：《Shams al-Maʻārif al-Kubrā》")

    # ── Riyada list ─────────────────────────────────────────────────────────
    st.markdown("##### 📖 修持法目錄")
    for r in _riyada.list_all_riyada():
        with st.expander(f"**{r['name']}** — {r['chapter']}"):
            st.write(f"**描述 (Description):** {r['description']}")
            st.write(f"**阿拉伯文 (Arabic):** {r['arabic']}")
            st.write(f"**用途 (Use):** {r['use']}")
            st.write(f"**香料 (Incense):** {r['incense']}")
            st.markdown("**步驟 (Steps):**")
            for i, step in enumerate(r["steps"], 1):
                st.write(f"  {i}. {step}")
            st.info(f"📝 {r['note']}")

    st.divider()

    # ── Incense formulas ────────────────────────────────────────────────────
    st.markdown("##### 💨 香料配方速查 (Incense Formulas)")
    header = "| 名稱 | 配方 | 用途 | 備註 |"
    sep = "|:---:|:---|:---|:---|"
    rows = [header, sep]
    for inc in _riyada.list_all_incense():
        rows.append(
            f"| {inc['name']} | {inc['formula']} | {inc['use']} | {inc['note']} |"
        )
    st.markdown("\n".join(rows))


def _render_duas():
    """祈禱文 (Du'a) 瀏覽器"""
    st.markdown("#### 📿 祈禱文 (Du'a / Invocations)")
    st.caption("資料來源：《Shams al-Maʻārif al-Kubrā》")

    search_dua = st.text_input(
        "搜尋祈禱文 (Search du'a by keyword)",
        placeholder="例如：حماية 或 保護",
        key="shams_dua_search",
    )

    all_duas = _duas.DUAS
    if search_dua:
        query = search_dua.lower().strip()
        all_duas = {
            k: v for k, v in _duas.DUAS.items()
            if (query in k.lower()
                or query in v.get("arabic", "").lower()
                or query in v.get("use", "").lower()
                or query in v.get("description", "").lower())
        }

    if not all_duas:
        st.info("沒有找到符合的祈禱文。")
        return

    st.caption(f"共 {len(all_duas)} 條祈禱文")
    for key, dua in all_duas.items():
        with st.expander(f"**{key}** — {dua.get('description', '')}"):
            if "arabic" in dua:
                st.markdown(f"> {dua['arabic']}")
            if "transliteration" in dua:
                st.write(f"**拉丁轉寫 (Transliteration):** {dua['transliteration']}")
            if "use" in dua:
                st.write(f"**用途 (Use):** {dua['use']}")
            if "source" in dua:
                st.write(f"**出處 (Source):** {dua['source']}")
            if "timing" in dua:
                st.write(f"**建議時辰 (Timing):** {dua['timing']}")
            if "note" in dua:
                st.info(f"📝 {dua['note']}")
