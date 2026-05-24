"""Shared result rendering shell helpers.

共通模式：AI 按鈕代理與結果 tab 佈局。Phase 1 先提供穩定 API。
"""

from __future__ import annotations

from typing import Any, Callable, Sequence


def render_ai_analysis_button(
    *,
    ai_sink: Callable[[str, Any, str, str], None],
    system_key: str,
    chart_obj: Any,
    btn_key: str = "",
    page_content: str = "",
) -> None:
    """Forward AI analysis context to existing global chat sink."""

    ai_sink(system_key, chart_obj, btn_key, page_content)


def render_result_tabs(st_module, labels: Sequence[str]):
    """Thin wrapper for Streamlit tabs to centralize future enhancements."""

    return st_module.tabs(list(labels))
