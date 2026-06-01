from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BaseChart:
    """Shared base fields for chart result dataclasses."""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str = ""
    julian_day: float = 0.0
