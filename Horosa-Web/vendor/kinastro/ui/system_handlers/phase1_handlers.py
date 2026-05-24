"""Phase 1 representative handlers.

目前先遷移 `tab_ziwei`，其餘仍走 legacy fallback 以保證相容。
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.birth_form import BirthChartParams
from ui.system_engine import SystemHandler


def build_ziwei_handler(*, compute_ziwei_chart, render_ziwei_chart, ai_button_sink) -> SystemHandler:
    """Create executable handler for ZiWei system."""

    @st.cache_data(show_spinner=False)
    def _cached_compute(params_payload: dict[str, Any], vietnam_mode: bool):
        return compute_ziwei_chart(**params_payload, gender=params_payload.get("gender", "male"), vietnam_mode=vietnam_mode)

    def _compute(params: BirthChartParams, options: dict[str, Any]):
        # `to_dict()` intentionally preserves legacy compute kwargs only.
        # Gender is injected separately for systems that need it.
        payload = {**params.to_dict(), "gender": params.gender}
        return _cached_compute(payload, bool(options.get("vietnam_mode", False)))

    def _render(result: Any, params: BirthChartParams, options: dict[str, Any]) -> None:
        render_ziwei_chart(
            result,
            after_chart_hook=lambda: ai_button_sink("tab_ziwei", result, "ziwei", ""),
        )

    return SystemHandler(
        system_id="tab_ziwei",
        compute=_compute,
        render=_render,
        options_schema={"vietnam_mode": bool},
    )
