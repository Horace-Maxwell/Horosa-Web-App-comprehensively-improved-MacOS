"""Birth input data model and resolution helpers.

此模組只處理資料結構與轉換，不直接依賴具體占星系統。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Any, Mapping


@dataclass(frozen=True)
class BirthChartParams:
    """Unified birth chart parameters used across systems.

    統一管理出生參數，作為 app 內單一真相來源。
    """

    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    gender: str = "male"

    def to_dict(self) -> dict[str, Any]:
        """Return legacy dict format used by existing compute functions."""
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "timezone": self.timezone,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_name": self.location_name,
        }

    @classmethod
    def from_dict(cls, params: Mapping[str, Any], *, gender: str = "male") -> "BirthChartParams":
        """Create params from legacy mapping.

        Args:
            params: Existing dict-like params from session state.
            gender: Optional gender used by specific systems.
        """

        return cls(
            year=int(params.get("year", 1990)),
            month=int(params.get("month", 1)),
            day=int(params.get("day", 1)),
            hour=int(params.get("hour", 12)),
            minute=int(params.get("minute", 0)),
            timezone=float(params.get("timezone", 8.0)),
            latitude=float(params.get("latitude", 22.3193)),
            longitude=float(params.get("longitude", 114.1694)),
            location_name=str(params.get("location_name", "")),
            gender=str(gender or "male"),
        )


def build_birth_params(
    *,
    birth_date: date,
    birth_time: time,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str,
    gender: str,
) -> BirthChartParams:
    """Build `BirthChartParams` from current widget values."""

    return BirthChartParams(
        year=birth_date.year,
        month=birth_date.month,
        day=birth_date.day,
        hour=birth_time.hour,
        minute=birth_time.minute,
        timezone=float(timezone),
        latitude=float(latitude),
        longitude=float(longitude),
        location_name=location_name,
        gender=gender,
    )
