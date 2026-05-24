"""frontend/arabic_lots_dashboard.py

Arabic Lots 互動 Dashboard。
"""

from __future__ import annotations

import html
from typing import Callable

import streamlit as st

from astro.arabic_lots import ArabicLotsResult, CATEGORY_LABELS, get_top_priority_lots


def _theme_css() -> str:
    return """
    <style>
    .arabic-lots-card {
      border: 1px solid rgba(212, 175, 119, 0.35);
      border-radius: 12px;
      padding: 12px 14px;
      background:
        radial-gradient(circle at 85% 15%, rgba(212,175,119,0.16), transparent 42%),
        linear-gradient(135deg, rgba(10,37,64,0.94) 0%, rgba(18,46,74,0.95) 52%, rgba(15,35,54,0.98) 100%);
      box-shadow: 0 0 0.8rem rgba(212,175,119,0.15);
      color: #F5E6C8;
      margin-bottom: 10px;
    }
    .arabic-lots-title {
      color: #D4AF77;
      font-weight: 700;
      letter-spacing: 0.03em;
      font-family: "Cinzel", "Noto Serif TC", serif;
      margin-bottom: 2px;
    }
    .arabic-lots-meta {
      color: #D8DCE5;
      font-size: 0.88rem;
    }
    </style>
    """


def render_arabic_lots_dashboard(result: ArabicLotsResult, t: Callable[[str], str]) -> None:
    """渲染 Al-Biruni 97 Lots Dashboard。"""

    st.markdown(_theme_css(), unsafe_allow_html=True)

    sect_label = t("arabic_lots_day_chart") if result.is_day_chart else t("arabic_lots_night_chart")
    zodiac_label = t("arabic_lots_tropical") if result.zodiac_mode == "tropical" else t("arabic_lots_sidereal")
    title = html.escape(t("arabic_lots_dashboard_title"))
    total_label = html.escape(t("arabic_lots_total_count"))
    sect_title = html.escape(t("arabic_lots_sect"))
    zodiac_title = html.escape(t("arabic_lots_zodiac_mode"))
    sect_label_esc = html.escape(sect_label)
    zodiac_label_esc = html.escape(zodiac_label)
    st.markdown(
        (
            f'<div class="arabic-lots-card">'
            f'<div class="arabic-lots-title">{title}</div>'
            f'<div class="arabic-lots-meta">{total_label}: {len(result.lots)} ｜ '
            f'{sect_title}: {sect_label_esc} ｜ {zodiac_title}: {zodiac_label_esc}</div>'
            f'</div>'
        ),
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2.2, 1.3, 1.3])
    with col1:
        search = st.text_input(t("arabic_lots_search"), placeholder=t("arabic_lots_search_placeholder"))
    with col2:
        category_options = {
            t("arabic_lots_category_planetary"): "planetary",
            t("arabic_lots_category_houses"): "houses",
            t("arabic_lots_category_special"): "special",
        }
        selected_categories = st.multiselect(
            t("arabic_lots_filter_category"),
            options=list(category_options.keys()),
            default=list(category_options.keys()),
        )
    with col3:
        sort_mode = st.selectbox(
            t("arabic_lots_sort"),
            options=[
                t("arabic_lots_sort_priority"),
                t("arabic_lots_sort_longitude"),
                t("arabic_lots_sort_house"),
                t("arabic_lots_sort_name"),
            ],
            index=0,
        )

    category_values = {category_options[k] for k in selected_categories}
    query = search.strip().lower()

    filtered = []
    for lot in result.lots:
        if lot.category not in category_values:
            continue
        if query:
            search_blob = (
                f"{lot.name_en} {lot.name_zh} {lot.name_ar} "
                f"{lot.formula_day} {lot.formula_night}"
            ).lower()
            if query not in search_blob:
                continue
        filtered.append(lot)

    if sort_mode == t("arabic_lots_sort_priority"):
        filtered.sort(key=lambda x: (-x.priority, x.name_en))
    elif sort_mode == t("arabic_lots_sort_longitude"):
        filtered.sort(key=lambda x: x.longitude)
    elif sort_mode == t("arabic_lots_sort_house"):
        filtered.sort(key=lambda x: (x.house, -x.priority))
    else:
        filtered.sort(key=lambda x: x.name_en)

    st.caption(f"{t('arabic_lots_filtered_count')}: {len(filtered)}")

    rows = []
    for lot in filtered:
        category_label = CATEGORY_LABELS.get(lot.category, {}).get("zh", lot.category)
        rows.append(
            {
                t("arabic_lots_col_name"): f"{lot.name_zh} / {lot.name_en}",
                t("arabic_lots_col_arabic"): lot.name_ar,
                t("arabic_lots_col_category"): category_label,
                t("arabic_lots_col_formula"): lot.formula_day if result.is_day_chart else lot.formula_night,
                t("arabic_lots_col_position"): f"{lot.sign_glyph} {lot.sign_en} {lot.degree_in_sign:.2f}°",
                t("arabic_lots_col_house"): lot.house,
                t("arabic_lots_col_beneficence"): f"{lot.beneficence_zh} / {lot.beneficence}",
                t("arabic_lots_col_priority"): lot.priority,
            }
        )

    st.dataframe(rows, width="stretch", hide_index=True)

    with st.expander(t("arabic_lots_top10_title"), expanded=True):
        top_lots = get_top_priority_lots(result, 10)
        top_rows = [
            {
                t("arabic_lots_col_name"): f"{lot.name_zh} / {lot.name_en}",
                t("arabic_lots_col_position"): f"{lot.sign_glyph} {lot.sign_en} {lot.degree_in_sign:.2f}°",
                t("arabic_lots_col_house"): lot.house,
                t("arabic_lots_col_formula"): lot.formula_day if result.is_day_chart else lot.formula_night,
            }
            for lot in top_lots
        ]
        st.dataframe(top_rows, width="stretch", hide_index=True)
