"""Executable system registry and rendering engine.

描述層（astro.system_registry）與執行層分離：
- 描述層：名稱、分類、i18n、特性
- 執行層：compute/render/options/caching policy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from ui.components.birth_form import BirthChartParams


ComputeFunc = Callable[[BirthChartParams, dict[str, Any]], Any]
RenderFunc = Callable[[Any, BirthChartParams, dict[str, Any]], None]


@dataclass
class SystemHandler:
    """Executable handler for one astrology system."""

    system_id: str
    compute: ComputeFunc
    render: RenderFunc
    options_schema: dict[str, Any] = field(default_factory=dict)


class SystemEngine:
    """Registry-driven execution engine with legacy fallback."""

    def __init__(self) -> None:
        self._registry: dict[str, SystemHandler] = {}

    def register(self, handler: SystemHandler) -> None:
        """Register a system handler."""

        self._registry[handler.system_id] = handler

    def has_handler(self, system_id: str) -> bool:
        """Return whether a system has a registered handler."""

        return system_id in self._registry

    def run_system(
        self,
        *,
        system_id: str,
        params: BirthChartParams,
        options: dict[str, Any],
        spinner_text: str,
        st_module,
        on_error: Callable[[Exception], None],
    ) -> bool:
        """Execute and render a system. Returns True when handled."""

        handler = self._registry.get(system_id)
        if handler is None:
            return False

        try:
            with st_module.spinner(spinner_text):
                result = handler.compute(params, options)
            handler.render(result, params, options)
            return True
        except Exception as exc:  # pragma: no cover - UI runtime safety
            on_error(exc)
            return True


EXECUTION_REGISTRY = SystemEngine()
