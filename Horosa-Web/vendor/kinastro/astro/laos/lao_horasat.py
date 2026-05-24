"""Unified public interface for Laos Horasat.

此檔案是老撾占星模組對外唯一主入口，
提供與現有體系一致的「計算 + 查詢 + 渲染」API。
"""

from __future__ import annotations

from datetime import datetime, timezone as dt_timezone
from typing import Any, Dict, List

from .calculator import (
    LaoChart,
    chart_to_dict,
    compute_lao_chart,
    find_best_dates as calc_find_best_dates,
    get_lao_auspicious_time,
    get_monthly_fortune,
)
from .renderer import build_lao_brahma_wheel_svg, render_lao_horasat


class LaoHorasat:
    """老撾占星統一入口。"""

    def get_chart(
        self,
        *,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        timezone: float,
        latitude: float,
        longitude: float,
        location_name: str = "",
        sangkhom_activity: str = "ການແຕ່ງງານ",
        sikarat_type: str = "ສີກາດລາວ",
    ) -> Dict[str, Any]:
        """計算完整老撾出生盤並回傳 dict。"""

        chart = compute_lao_chart(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            sangkhom_activity=sangkhom_activity,
            sikarat_type=sikarat_type,
        )
        return chart_to_dict(chart)

    def get_chart_from_iso(
        self,
        iso_datetime: str,
        *,
        timezone: float,
        latitude: float,
        longitude: float,
        location_name: str = "",
        sangkhom_activity: str = "ການແຕ່ງງານ",
        sikarat_type: str = "ສີກາດລາວ",
    ) -> Dict[str, Any]:
        """由 ISO 時間字串建立盤（便於 API 呼叫）。"""

        dt = _parse_iso_datetime(iso_datetime)

        return self.get_chart(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            sangkhom_activity=sangkhom_activity,
            sikarat_type=sikarat_type,
        )

    def get_sangkhom(
        self,
        target_dt: datetime,
        *,
        activity: str = "ການແຕ່ງງານ",
        sikarat_type: str = "ສີກາດລາວ",
    ) -> Dict[str, Any]:
        """查詢單一時刻的 ສັງຄົມ / ສີກາດ。"""

        return get_lao_auspicious_time(target_dt, activity=activity, sikarat_type=sikarat_type)

    def find_best_dates(
        self,
        start_dt: datetime,
        *,
        days: int = 30,
        activity: str = "ການແຕ່ງງານ",
    ) -> List[Dict[str, Any]]:
        """搜尋近期吉日。"""

        return calc_find_best_dates(start_dt, days=days, activity=activity)

    def get_monthly_fortune(
        self,
        year: int,
        month: int,
        *,
        activity: str = "ການແຕ່ງງານ",
    ) -> List[Dict[str, Any]]:
        """取得月度吉凶摘要。"""

        return get_monthly_fortune(year, month, activity=activity)

    def render_wheel(self, chart: LaoChart | Dict[str, Any], *, size: int = 700) -> str:
        """單獨渲染婆羅門輪 SVG。"""

        return build_lao_brahma_wheel_svg(chart, size=size)

    def render_panel(self, chart: LaoChart | Dict[str, Any], *, lang: str = "zh") -> None:
        """在 Streamlit 渲染 Laos 專屬頁面。"""

        render_lao_horasat(chart, lang=lang)


# 便捷函式（與專案其他模組風格一致）
def create_lao_horasat() -> LaoHorasat:
    """建立 LaoHorasat 實例。"""

    return LaoHorasat()


def compute_lao_horasat_chart(**kwargs: Any) -> Dict[str, Any]:
    """函式風格入口：計算並回傳 dict。"""

    return LaoHorasat().get_chart(**kwargs)


def _parse_iso_datetime(value: str) -> datetime:
    """穩健解析 ISO-8601 日期字串，兼容 Z 與偏移格式。"""

    try:
        if value.endswith("Z"):
            return datetime.fromisoformat(value[:-1]).replace(tzinfo=dt_timezone.utc)
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("iso_datetime 格式錯誤，請使用 ISO-8601") from exc
