"""Overview dashboard component for quick multi-system snapshots."""

from __future__ import annotations

from typing import Callable

from ui.state import SessionKeys


def render_overview_dashboard(
    *,
    st_module,
    t: Callable[[str], str],
    items: list[dict],
    current_system: str | None,
) -> None:
    """Render post-calculation dashboard cards with one-click navigation."""

    if not items:
        return

    st_module.markdown(
        f'<div class="ka-overview-title">🧭 {t("overview_dashboard_title")}</div>',
        unsafe_allow_html=True,
    )
    cols = st_module.columns(2, gap="small")
    for idx, item in enumerate(items):
        with cols[idx % 2]:
            active = item.get("system_id") == current_system
            accent = item.get("accent", "#A78BFA")
            st_module.markdown(
                (
                    '<div class="ka-overview-card" '
                    f'style="--ka-system-accent:{accent};">'
                    f'<div class="ka-overview-card-title">{item.get("icon", "✨")} {item.get("title", "")}</div>'
                    f'<div class="ka-overview-card-metric">{item.get("metric_main", "")}</div>'
                    f'<div class="ka-overview-card-sub">{item.get("metric_sub", "")}</div>'
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
            btn_label = (
                t("overview_dashboard_current")
                if active
                else t("overview_dashboard_open")
            )
            if st_module.button(
                btn_label,
                key=f"_overview_open_{item.get('system_id', idx)}",
                width="stretch",
                type="primary" if active else "secondary",
            ):
                system_id = item.get("system_id")
                if system_id:
                    st_module.session_state[SessionKeys.SYSTEM_SELECT] = system_id
                    st_module.rerun()
