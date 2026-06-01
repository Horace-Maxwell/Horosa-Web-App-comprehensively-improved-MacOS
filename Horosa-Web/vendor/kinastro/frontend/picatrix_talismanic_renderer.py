"""
Streamlit example renderer for the Picatrix talismanic generator.
"""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from astro.picatrix import generate_picatrix_talisman, select_picatrix_images


def render_picatrix_talismanic_generator() -> None:
    st.subheader("🜏 Picatrix Talismanic Magic Chart Generator")
    st.caption("For historical research only · 僅供研究參考 · للاستخدام البحثي فقط")

    purpose = st.selectbox(
        "Purpose / 目的",
        ["love", "wealth", "protection", "healing", "success", "harm"],
        index=1,
    )
    include_harmful = st.checkbox("Allow harmful intent (research mode)", value=False)

    with st.expander("Image candidates", expanded=True):
        for candidate in select_picatrix_images(purpose)[:6]:
            st.markdown(
                f"- **{candidate.source_type}** · {candidate.source_name_en} / {candidate.source_name_zh} · {candidate.celestial_source}"
            )

    now = datetime.now(timezone.utc)
    col1, col2, col3 = st.columns(3)
    with col1:
        latitude = st.number_input("Latitude", value=25.0330)
    with col2:
        longitude = st.number_input("Longitude", value=121.5654)
    with col3:
        timezone_offset = st.number_input("Timezone", value=8.0)

    if st.button("Generate Talisman Blueprint", type="primary"):
        result = generate_picatrix_talisman(
            purpose=purpose,
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            timezone_offset=timezone_offset,
            latitude=latitude,
            longitude=longitude,
            include_harmful=include_harmful,
        )

        st.success(
            f"Selected: {result.selected_image.source_name_en} · score={result.election_details.score:.1f} · {result.election_details.quality}"
        )

        tab_blueprint, tab_invocation, tab_warnings = st.tabs(["Blueprint", "Invocation", "Warnings"])
        with tab_blueprint:
            st.markdown(result.blueprint.blueprint_html, unsafe_allow_html=True)
            st.json(result.blueprint.materia)
        with tab_invocation:
            st.code(result.blueprint.invocation["en"])
            st.code(result.blueprint.invocation["zh"])
            st.code(result.blueprint.invocation["ar"])
        with tab_warnings:
            for warning in result.blueprint.warnings:
                st.warning(warning)

