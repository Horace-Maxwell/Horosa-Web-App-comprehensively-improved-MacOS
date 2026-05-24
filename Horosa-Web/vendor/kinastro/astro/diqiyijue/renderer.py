"""Streamlit renderer for the Di Qi Yi Jue module."""

from __future__ import annotations

from datetime import date
import math
from typing import Any

from astro.chart_renderer_v2 import build_cultural_svg
from astro.i18n import t

from .calculator import BAGONG_NAMES, DiQiYiJue, DiqiyijueChart


_WUXING_COLORS = {
    "水": "#60A5FA",
    "火": "#F97316",
    "木": "#34D399",
    "金": "#FBBF24",
    "土": "#A78BFA",
    "未知": "#94A3B8",
}


def _build_bagong_svg(chart: DiqiyijueChart) -> str:
    cx, cy, radius = 260, 250, 170
    destiny_name = chart.destiny_palace.get("宮名", "")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 500" style="width:100%;height:auto;font-family:Inter,Noto Sans TC,sans-serif;">',
        '<rect width="520" height="500" rx="18" fill="#0F172A" stroke="#C9A84C" stroke-width="2"/>',
        '<text x="260" y="34" text-anchor="middle" fill="#F8FAFC" font-size="20" font-weight="700">滌器遺訣八宮盤</text>',
        f'<text x="260" y="64" text-anchor="middle" fill="#CBD5E1" font-size="12">觀空：{chart.guankong.get("卦名", "-")} · 體變：{chart.bagua_tibian.get("卦名", "-")}{chart.bagua_tibian.get("本變", "")}</text>',
    ]
    for idx, palace in enumerate(BAGONG_NAMES):
        angle = math.radians(-90 + idx * 45)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        fill = _WUXING_COLORS.get(chart.eight_palaces_wuxing[idx], "#94A3B8")
        stroke = "#F8FAFC" if palace == destiny_name else "#C9A84C"
        stroke_width = "3" if palace == destiny_name else "1.5"
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="42" fill="{fill}" fill-opacity="0.18" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{y - 12:.1f}" text-anchor="middle" fill="#F8FAFC" font-size="18" font-weight="700">{palace}</text>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{y + 8:.1f}" text-anchor="middle" fill="#E2E8F0" font-size="18">{chart.eight_palaces_numbers[idx]}</text>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{y + 24:.1f}" text-anchor="middle" fill="#CBD5E1" font-size="11">{chart.eight_palaces_wuxing[idx]}</text>'
        )
    parts.extend(
        [
            '<circle cx="260" cy="250" r="78" fill="#111827" stroke="#C9A84C" stroke-width="1.5"/>',
            f'<text x="260" y="224" text-anchor="middle" fill="#F8FAFC" font-size="16" font-weight="700">命宮 {destiny_name or "-"}</text>',
            f'<text x="260" y="248" text-anchor="middle" fill="#CBD5E1" font-size="13">都數 {chart.full_chart.get("都數", "-")}</text>',
            f'<text x="260" y="272" text-anchor="middle" fill="#CBD5E1" font-size="13">胎月 {chart.tai_month}</text>',
            f'<text x="260" y="296" text-anchor="middle" fill="#CBD5E1" font-size="13">數尾 {chart.shu_wei.get("零數", "-")} · {chart.shu_wei.get("五行", "-")}</text>',
            "</svg>",
        ]
    )
    return "\n".join(parts)


def _table_rows_from_dict(
    payload: dict[str, Any],
    label_key: str = "項目",
    value_key: str = "內容",
) -> list[dict[str, str]]:
    return [{label_key: str(key), value_key: str(value)} for key, value in payload.items()]


def render_diqiyijue_chart(
    chart: DiqiyijueChart,
    *,
    after_chart_hook=None,
) -> None:
    import streamlit as st

    st.subheader(t("diqiyijue_chart_title"))
    pillars_text = " ".join(f"{name}{value}" for name, value in chart.four_pillars.items())
    st.info(
        f"📅 {chart.year}-{chart.month:02d}-{chart.day:02d} "
        f"{chart.hour:02d}:{chart.minute:02d} "
        f"(UTC{chart.timezone:+.1f}) · {chart.location_name or '—'}\n\n"
        f"{t('diqiyijue_birth_pillars')}: {pillars_text} · "
        f"{t('diqiyijue_birth_gender')}: {chart.gender}"
    )

    tab_chart, tab_analysis, tab_flow, tab_classic = st.tabs(
        [
            t("diqiyijue_subtab_chart"),
            t("diqiyijue_subtab_analysis"),
            t("diqiyijue_subtab_flow"),
            t("diqiyijue_subtab_classic"),
        ]
    )

    with tab_chart:
        st.markdown(
            build_cultural_svg(_build_bagong_svg(chart), "tab_diqiyijue", title="滌器遺訣"),
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(t("diqiyijue_metric_tai"), chart.tai_month)
        col2.metric(t("diqiyijue_metric_guankong"), chart.guankong.get("卦名", "-"))
        col3.metric(
            t("diqiyijue_metric_tibian"),
            f"{chart.bagua_tibian.get('卦名', '-')} {chart.bagua_tibian.get('本變', '')}".strip(),
        )
        col4.metric(t("diqiyijue_metric_destiny"), chart.destiny_palace.get("宮名", "-"))

        st.markdown(f"### {t('diqiyijue_section_five_lines')}")
        st.dataframe(
            [
                {"位次": key, "干支": value["干支"], "納音": value["納音"]}
                for key, value in chart.five_lines.items()
            ],
            width="stretch",
        )

        st.markdown(f"### {t('diqiyijue_section_core')}")
        st.dataframe(
            [
                {"項目": t("diqiyijue_row_yuan"), "內容": str(chart.yuan_numbers)},
                {"項目": t("diqiyijue_row_ying"), "內容": str(chart.ying_numbers)},
                {"項目": t("diqiyijue_row_bengong"), "內容": str(chart.core_four_positions)},
                {"項目": t("diqiyijue_row_biefa"), "內容": str(chart.alternate_four_positions)},
                {
                    "項目": t("diqiyijue_row_shuwei"),
                    "內容": f"{chart.shu_wei.get('零數', '-')} / {chart.shu_wei.get('五行', '-')}",
                },
            ],
            width="stretch",
        )

        if after_chart_hook is not None:
            after_chart_hook()

    with tab_analysis:
        st.markdown(f"### {t('diqiyijue_section_eight_palaces')}")
        st.dataframe(chart.eight_palaces_details, width="stretch")

        st.markdown(f"### {t('diqiyijue_section_qipao')}")
        qipao_col1, qipao_col2 = st.columns(2)
        with qipao_col1:
            st.caption(t("diqiyijue_qipao_bagong"))
            st.dataframe(chart.qipao_bagong, width="stretch")
        with qipao_col2:
            st.caption(t("diqiyijue_qipao_bengong"))
            st.dataframe(chart.qipao_bengong, width="stretch")

        left, right = st.columns(2)
        with left:
            st.markdown(f"### {t('diqiyijue_section_relationships')}")
            st.dataframe(_table_rows_from_dict(chart.he_yun), width="stretch")
            st.markdown(f"### {t('diqiyijue_section_mingzhu')}")
            st.json(chart.ming_zhu)
        with right:
            st.markdown(f"### {t('diqiyijue_section_patterns')}")
            st.write(
                f"**{t('diqiyijue_label_guige')}**: "
                f"{', '.join(chart.gui_ge) if chart.gui_ge else t('diqiyijue_none')}"
            )
            st.write(
                f"**{t('diqiyijue_label_xiongxing')}**: "
                f"{', '.join(chart.xiong_xing) if chart.xiong_xing else t('diqiyijue_none')}"
            )
            st.write(
                f"**{t('diqiyijue_label_guansha')}**: "
                f"{', '.join(chart.guan_sha) if chart.guan_sha else t('diqiyijue_none')}"
            )
            st.dataframe(_table_rows_from_dict(chart.ke_shu), width="stretch")
            st.dataframe(_table_rows_from_dict(chart.shou_xian), width="stretch")

        st.markdown(f"### {t('diqiyijue_section_fate_cycles')}")
        st.dataframe(chart.dayun, width="stretch")
        st.dataframe(chart.xiaoyun_preview, width="stretch")

    with tab_flow:
        default_age = max(1, date.today().year - chart.year + 1)
        age = st.number_input(
            t("diqiyijue_flow_age"),
            min_value=1,
            max_value=120,
            value=int(default_age),
            step=1,
        )
        current_year_gz = st.text_input(t("diqiyijue_flow_year_ganzhi"), value="")
        engine = DiQiYiJue(chart.four_pillars, chart.gender)
        flow_data = engine.flow_year(year_ganzhi=current_year_gz or None, age=int(age))
        flow_biefa = engine.flow_year_biefa(age=int(age))

        st.markdown(f"### {t('diqiyijue_section_flow_year')}")
        st.dataframe(_table_rows_from_dict(flow_data), width="stretch")
        st.markdown(f"### {t('diqiyijue_section_biefa_flow')}")
        st.dataframe(_table_rows_from_dict(flow_biefa), width="stretch")

    with tab_classic:
        st.markdown(t("desc_diqiyijue"))
        st.markdown(f"### {t('diqiyijue_section_method_summary')}")
        st.markdown(
            "\n".join(
                [
                    f"- {t('diqiyijue_method_1')}",
                    f"- {t('diqiyijue_method_2')}",
                    f"- {t('diqiyijue_method_3')}",
                    f"- {t('diqiyijue_method_4')}",
                ]
            )
        )
        st.markdown(f"### {t('diqiyijue_section_classic_points')}")
        st.write(f"• {t('diqiyijue_classic_point_1')}")
        st.write(f"• {t('diqiyijue_classic_point_2')}")
        st.write(f"• {t('diqiyijue_classic_point_3')}")
