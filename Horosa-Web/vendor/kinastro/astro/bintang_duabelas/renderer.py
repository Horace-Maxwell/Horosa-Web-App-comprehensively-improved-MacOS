"""Streamlit renderer for the Bintang Duabelas module."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any

import streamlit as st

from astro.i18n import auto_cn
from frontend.bintang_duabelas_renderer import (
    render_planetary_hours_wheel,
    render_twelve_houses_wheel,
)

from .core import BintangDuabelasEngine

_DAY_OPTIONS = ("ahad", "isnin", "selasa", "rabu", "khamis", "jumaat", "sabtu")


def _day_label(day_key: str) -> str:
    labels = {
        "ahad": auto_cn("星期日 / Sunday / Ahad"),
        "isnin": auto_cn("星期一 / Monday / Isnin"),
        "selasa": auto_cn("星期二 / Tuesday / Selasa"),
        "rabu": auto_cn("星期三 / Wednesday / Rabu"),
        "khamis": auto_cn("星期四 / Thursday / Khamis"),
        "jumaat": auto_cn("星期五 / Friday / Jumaat"),
        "sabtu": auto_cn("星期六 / Saturday / Sabtu"),
    }
    return labels.get(day_key, day_key)


def _script_label(script_hint: str) -> str:
    labels = {
        "auto": auto_cn("自動判斷 / Auto"),
        "roman": auto_cn("羅馬字 / Romanized"),
        "arabic": auto_cn("阿拉伯字 / Arabic"),
    }
    return labels.get(script_hint, script_hint)


def _render_metrics(result: dict[str, Any], keys: list[tuple[str, str]]) -> None:
    cols = st.columns(len(keys))
    for col, (label, key) in zip(cols, keys):
        with col:
            st.metric(label, result.get(key, "—"))


def _render_mapping(data: dict[str, Any], *, skip: set[str] | None = None) -> None:
    skip = skip or set()
    for key, value in data.items():
        if key in skip:
            continue
        title = key.replace("_", " ").title()
        if isinstance(value, dict):
            with st.expander(title, expanded=False):
                _render_mapping(value)
        elif isinstance(value, list):
            if value and all(isinstance(item, str) for item in value):
                st.markdown(f"**{title}**")
                for item in value:
                    st.markdown(f"- {item}")
            else:
                with st.expander(title, expanded=False):
                    st.write(value)
        else:
            st.markdown(f"**{title}**: {value}")


def _render_hour_list(hours: list[dict[str, Any]]) -> None:
    for item in hours:
        st.markdown(
            auto_cn(
                f"- 第 {item['hour']} 時辰 · {item['planet_zh']} / {item['planet_en']} · "
                f"{item['fortune_zh']} · {item['start'].strftime('%H:%M')}–{item['end'].strftime('%H:%M')}"
            )
        )


def _house_script_label(script: str) -> str:
    labels = {
        "zh": auto_cn("中文 / Chinese"),
        "en": auto_cn("英文 / English"),
        "jawi": auto_cn("Jawi / Arabic"),
    }
    return labels.get(script, script)


def _script_house_name(house: dict[str, Any], script: str) -> str:
    if script == "jawi":
        return str(house.get("name_ar", house.get("name_malay", "—")))
    if script == "en":
        return str(house.get("name_en", house.get("name_malay", "—")))
    return str(house.get("name_zh", house.get("name_malay", "—")))


def render_streamlit(default_birth_datetime: datetime | None = None) -> None:
    """Render the Bintang Duabelas tools page."""
    engine = BintangDuabelasEngine()

    st.markdown(
        "<h2 style='text-align:center;'>⭐ 馬來伊斯蘭占星 · Bintang Duabelas（十二星）⭐</h2>",
        unsafe_allow_html=True,
    )
    st.caption(
        auto_cn(
            "馬來－伊斯蘭傳統數理與十二宮工具：Abjad、Hisab Nama、十二星宮、行星時辰與 Azimat。"
        )
    )
    st.info(
        auto_cn(
            "可先從 Abjad / Hisab 輸入姓名開始，再切換到十二星宮、相合占、行星時辰與 Azimat 分頁；支援 Jawi、阿拉伯字與 Romanized 名稱。"
        )
    )

    tab_abjad, tab_stars, tab_relationships, tab_timing, tab_azimat = st.tabs(
        [
            auto_cn("🔤 Abjad / Hisab"),
            auto_cn("⭐ 十二星宮"),
            auto_cn("💞 相合占"),
            auto_cn("🕒 行星時辰"),
            auto_cn("🧿 Azimat"),
        ]
    )

    with tab_abjad:
        name = st.text_input(auto_cn("姓名 / Name"), key="bd_name")
        script_hint = st.selectbox(
            auto_cn("文字提示"),
            options=["auto", "roman", "arabic"],
            format_func=_script_label,
            key="bd_script_hint",
        )
        day_name = st.selectbox(
            auto_cn("星期"),
            options=list(_DAY_OPTIONS),
            format_func=_day_label,
            key="bd_day_name",
        )

        if name.strip():
            normalized = engine.normalize_name(name, script_hint=script_hint)
            abjad_total = engine.name_to_abjad(name, script_hint=script_hint)
            hisab_total, hisab_remainder = engine.hisab_nama(name, script_hint=script_hint)
            disease = engine.diagnose_disease(name, day_name=day_name, script_hint=script_hint)
            missing = engine.check_missing_person(name, day_name=day_name, script_hint=script_hint)

            _render_metrics(
                {
                    "abjad_total": abjad_total,
                    "hisab_remainder": hisab_remainder,
                    "day_name": _day_label(day_name),
                },
                [
                    (auto_cn("Abjad 總值"), "abjad_total"),
                    (auto_cn("Hisab 餘數（mod 9）"), "hisab_remainder"),
                    (auto_cn("使用星期"), "day_name"),
                ],
            )

            st.markdown(f"**{auto_cn('正規化')}**: `{normalized.normalized or '—'}`")
            st.caption(
                auto_cn(
                    f"原始：{normalized.original}｜來源：{normalized.source_script}｜轉寫覆蓋：{'是' if normalized.used_override else '否'}"
                )
            )

            breakdown = engine.get_letter_breakdown(name, script_hint=script_hint)
            with st.expander(auto_cn("字母拆解"), expanded=True):
                if breakdown:
                    for letter, value in breakdown:
                        st.markdown(f"- `{letter}` → {value}")
                else:
                    st.info(auto_cn("沒有可顯示的字母拆解。"))

            col1, col2 = st.columns(2)
            with col1:
                st.subheader(auto_cn("疾病來源"))
                _render_mapping(disease)
            with col2:
                st.subheader(auto_cn("失蹤 / 遠行者"))
                _render_mapping(missing)
        else:
            st.info(auto_cn("輸入姓名後即可查看 Abjad、Hisab、疾病來源與失蹤占斷。"))

    with tab_stars:
        person_name = st.text_input(auto_cn("本人姓名"), key="bd_person_name")
        mother_name = st.text_input(auto_cn("母親姓名"), key="bd_mother_name")
        house_script = st.selectbox(
            auto_cn("宮位顯示語言"),
            options=["zh", "en", "jawi"],
            format_func=_house_script_label,
            key="bd_house_script",
        )
        house_number = st.selectbox(
            auto_cn("查看宮位"),
            options=list(range(1, 13)),
            key="bd_house_number",
        )

        houses = engine.get_all_houses()
        highlight_house: int | None = None
        if person_name.strip() and mother_name.strip():
            sign = engine.determine_star_sign(person_name, mother_name)
            reading = engine.get_full_reading(person_name, mother_name)
            highlight_house = int(reading["house"]["house_number"])
            _render_metrics(
                {
                    "sign_number": sign["sign_number"],
                    "house_number": reading["house"]["house_number"],
                    "planet": sign["planet"],
                },
                [
                    (auto_cn("星宮編號"), "sign_number"),
                    (auto_cn("對應宮位"), "house_number"),
                    (auto_cn("主宰行星"), "planet"),
                ],
            )
            st.subheader(auto_cn("星宮結果"))
            _render_mapping(sign)
            st.subheader(auto_cn("對應十二宮"))
            _render_mapping(reading["house"])
        else:
            st.info(auto_cn("輸入本人與母親姓名可推算十二星宮與落宮。"))

        st.subheader(auto_cn("十二星宮文化圓盤"))
        st.caption(auto_cn("點擊輪盤扇區可快速切換下方宮位詳解。"))
        clicked_house = render_twelve_houses_wheel(
            houses,
            highlight_house=highlight_house,
            script=house_script,
            chart_key="bd_house_wheel_chart",
        )
        current_house_number = int(st.session_state.get("bd_house_number", house_number))
        if clicked_house is not None and clicked_house != current_house_number:
            st.session_state["bd_house_number"] = clicked_house
            st.rerun()

        selected_house = engine.get_house(int(st.session_state.get("bd_house_number", house_number)))
        st.markdown(
            auto_cn(
                f"**{auto_cn('當前宮位')}**：Rumah {selected_house.get('house_number')} · "
                f"{_script_house_name(selected_house, house_script)}"
            )
        )

        with st.expander(auto_cn("宮位資料"), expanded=not (person_name.strip() and mother_name.strip())):
            _render_mapping(selected_house)

    with tab_relationships:
        partner_name = st.text_input(auto_cn("伴侶 / 對象姓名"), key="bd_partner_name")
        father_name = st.text_input(auto_cn("父親姓名（胎兒占用）"), key="bd_father_name")
        relationship_day = st.selectbox(
            auto_cn("星期（胎兒占）"),
            options=list(_DAY_OPTIONS),
            format_func=_day_label,
            key="bd_relationship_day",
        )

        if person_name.strip() and partner_name.strip():
            marriage = engine.check_marriage_compatibility(person_name, partner_name)
            st.subheader(auto_cn("婚姻相合"))
            _render_metrics(
                marriage,
                [
                    (auto_cn("合計值"), "combined"),
                    (auto_cn("餘數"), "remainder"),
                    (auto_cn("結果"), "result"),
                ],
            )
            st.markdown(f"**{auto_cn('說明')}**: {marriage.get('description_zh') or marriage.get('description')}")
        else:
            st.info(auto_cn("輸入兩個姓名可查看婚姻相合結果。"))

        if mother_name.strip() and father_name.strip():
            fetal = engine.predict_fetal_gender(
                mother_name,
                father_name,
                day_name=relationship_day,
            )
            st.subheader(auto_cn("胎兒占"))
            _render_mapping(fetal)

    with tab_timing:
        default_dt = default_birth_datetime or datetime.now()
        moment_date = st.date_input(auto_cn("日期"), value=default_dt.date(), key="bd_date")
        moment_time = st.time_input(auto_cn("時間"), value=default_dt.time(), key="bd_time")
        sunrise = st.time_input(auto_cn("日出"), value=time(6, 0), key="bd_sunrise")
        sunset = st.time_input(auto_cn("日落"), value=time(18, 0), key="bd_sunset")

        moment = datetime.combine(moment_date, moment_time)
        hour_result = engine.get_planetary_hours(moment, sunrise=sunrise, sunset=sunset)
        yearly = engine.get_yearly_fortune(birth_datetime=moment)
        current_hour = hour_result["current_hour"]
        day_key = engine.hours.weekday_to_day_key(moment.weekday())
        daytime_hours = engine.hours.get_hours_for_date(moment.date(), is_night=False, sunrise=sunrise, sunset=sunset)
        nighttime_hours = engine.hours.get_hours_for_date(moment.date(), is_night=True, sunrise=sunrise, sunset=sunset)

        _render_metrics(
            {
                "phase": hour_result["phase"],
                "sequence": current_hour["sequence"],
                "planet": current_hour["planet_en"],
            },
            [
                (auto_cn("時段"), "phase"),
                (auto_cn("序列"), "sequence"),
                (auto_cn("當前行星"), "planet"),
            ],
        )
        st.markdown(
            auto_cn(
                f"**當前時辰**：第 {current_hour['hour']} 時辰 · {current_hour['fortune_zh']} · "
                f"{current_hour['start'].strftime('%H:%M')}–{current_hour['end'].strftime('%H:%M')}"
            )
        )
        st.subheader(auto_cn("行星時辰輪（24 小時）"))
        st.caption(auto_cn("內圈為日時辰，外圈為夜時辰；顏色區分吉凶屬性。"))
        render_planetary_hours_wheel(
            daytime_hours,
            nighttime_hours,
            current_hour=current_hour,
            chart_key="bd_planetary_hours_chart",
        )
        with st.expander(auto_cn("十二時辰排程"), expanded=True):
            _render_hour_list(hour_result["hours"])

        st.subheader(auto_cn("年度主宰"))
        st.markdown(f"**{auto_cn('星期')}**: {_day_label(day_key)}")
        _render_mapping(yearly, skip={"day"})

    with tab_azimat:
        azimat_types = engine.list_azimat_types()
        azimat_lookup = {item["type"]: item for item in azimat_types}
        purpose = st.selectbox(
            auto_cn("Azimat 類型"),
            options=[item["type"] for item in azimat_types],
            format_func=lambda item: f"{azimat_lookup[item]['name_zh']} / {azimat_lookup[item]['name_en']}",
            key="bd_azimat_purpose",
        )
        azimat_person = st.text_input(auto_cn("代入姓名（可選）"), key="bd_azimat_person")
        azimat_target = st.text_input(auto_cn("對象姓名（可選）"), key="bd_azimat_target")
        azimat_day = st.selectbox(
            auto_cn("查看當日推薦"),
            options=list(_DAY_OPTIONS),
            format_func=_day_label,
            key="bd_azimat_day",
        )

        azimat = engine.generate_azimat(purpose, person_name=azimat_person, target_name=azimat_target)
        recommended = engine.get_azimat_for_day(azimat_day)

        st.subheader(auto_cn("Azimat 內容"))
        st.markdown(f"**{auto_cn('名稱')}**: {azimat.get('name_zh')} / {azimat.get('name_en')}")
        st.code(str(azimat.get("verse_ar", "")), language="text")
        st.markdown(f"**{auto_cn('中文指引')}**: {azimat.get('instructions_zh')}")
        st.markdown(f"**{auto_cn('英文指引')}**: {azimat.get('instructions_en')}")
        _render_mapping({"timing": azimat.get("timing", {})})

        with st.expander(auto_cn("該日推薦 Azimat"), expanded=True):
            if recommended:
                for item in recommended:
                    st.markdown(f"- {item['name_zh']} / {item['name_en']} · {item['timing']['planet_hour']}")
            else:
                st.info(auto_cn("此日沒有匹配的推薦 Azimat。"))
