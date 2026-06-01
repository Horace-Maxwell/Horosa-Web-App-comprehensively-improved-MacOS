"""Session state constants and initialization helpers for KinAstro UI.

集中管理 session_state key，降低 key 分散造成的維護成本。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SessionKeys:
    """Canonical Streamlit session-state keys.

    統一 key 命名，避免在各檔案散落硬編碼字串。
    """

    LANG: str = "lang"
    SYSTEM_SELECT: str = "_system_select"
    BIRTH_CONFIRMED: str = "_birth_confirmed"
    CONFIRMED_PARAMS: str = "_confirmed_params"
    CONFIRMED_GENDER: str = "_confirmed_gender"
    CALC_PARAMS: str = "_calc_params"
    CALC_GENDER: str = "_calc_gender"
    CALCULATED: str = "_calculated"
    STAR_PARTICLES: str = "_star_particles"
    CROSS_SYSTEM_ENABLED: str = "_cross_system_enabled"


def init_session_state_defaults(st_module: Any) -> None:
    """Initialize stable defaults for app-level state.

    Args:
        st_module: Streamlit module (`streamlit as st`).
    """

    defaults = {
        SessionKeys.LANG: "zh",
        SessionKeys.STAR_PARTICLES: True,
        SessionKeys.CROSS_SYSTEM_ENABLED: False,
    }
    for key, value in defaults.items():
        if key not in st_module.session_state:
            st_module.session_state[key] = value
