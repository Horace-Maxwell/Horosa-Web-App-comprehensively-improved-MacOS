"""
astro/bintang_duabelas/visuals.py
=================================

Bintang Duabelas 視覺化資料建模工具。

本模組只負責將核心引擎輸出的資料轉成可繪圖的結構，
不依賴 Streamlit，方便前端渲染與單元測試共用。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

DisplayScript = Literal["zh", "en", "jawi"]


@dataclass(frozen=True)
class HouseWheelSegment:
    """十二宮圓盤單一扇區資料。"""

    house_number: int
    theta_deg: float
    width_deg: float
    label: str
    subtitle: str
    border_color: str
    fill_color: str
    is_highlighted: bool
    hover_html: str


@dataclass(frozen=True)
class PlanetaryHourSegment:
    """行星時辰輪單一扇區資料。"""

    absolute_index: int
    hour_number: int
    phase: Literal["day", "night"]
    theta_deg: float
    width_deg: float
    label: str
    planet_symbol: str
    planet_name: str
    fortune_label: str
    fill_color: str
    border_color: str
    is_current: bool
    hover_html: str


_FORTUNE_COLORS: dict[str, tuple[str, str]] = {
    "baik": ("rgba(46, 176, 114, 0.82)", "#2EB072"),
    "nahs": ("rgba(191, 76, 61, 0.82)", "#BF4C3D"),
    "bercampur": ("rgba(212, 175, 119, 0.82)", "#D4AF77"),
}

_FORTUNE_LABELS: dict[str, str] = {
    "baik": "吉 / Auspicious / Baik",
    "nahs": "凶 / Inauspicious / Nahs",
    "bercampur": "混合 / Mixed / Bercampur",
}

_PLANET_SYMBOLS: dict[str, str] = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
}


def _house_title(house: dict[str, Any], script: DisplayScript) -> str:
    """依顯示腳本回傳宮位標題。"""
    if script == "jawi":
        return str(house.get("name_ar", house.get("name_malay", "")))
    if script == "en":
        return str(house.get("name_en", house.get("name_malay", "")))
    return str(house.get("name_zh", house.get("name_malay", "")))


def build_house_wheel_segments(
    houses: list[dict[str, Any]],
    *,
    highlight_house: int | None = None,
    script: DisplayScript = "zh",
) -> list[HouseWheelSegment]:
    """建立十二宮圓盤扇區資料。"""
    ordered = sorted(houses, key=lambda item: int(item.get("house_number", 0)))
    segments: list[HouseWheelSegment] = []
    for idx, house in enumerate(ordered):
        house_number = int(house["house_number"])
        is_highlighted = house_number == highlight_house
        theta_deg = 90 - idx * 30
        name_zh = str(house.get("name_zh", "—"))
        name_en = str(house.get("name_en", "—"))
        name_ar = str(house.get("name_ar", "—"))
        planet = str(house.get("planet", "—"))
        domain_zh = str(house.get("domain_zh", "—"))
        label = f"R{house_number}"
        subtitle = _house_title(house, script)
        fill_color = "rgba(212, 175, 119, 0.88)" if is_highlighted else "rgba(0, 100, 0, 0.54)"
        border_color = "#F6D88A" if is_highlighted else "#D4AF77"
        hover_html = (
            f"<b>Rumah {house_number}</b><br>"
            f"{name_zh} / {name_en}<br>"
            f"{name_ar}<br>"
            f"Planet: {planet}<br>"
            f"Domain: {domain_zh}"
        )
        segments.append(
            HouseWheelSegment(
                house_number=house_number,
                theta_deg=theta_deg,
                width_deg=30.0,
                label=label,
                subtitle=subtitle,
                border_color=border_color,
                fill_color=fill_color,
                is_highlighted=is_highlighted,
                hover_html=hover_html,
            )
        )
    return segments


def _is_current_hour(
    candidate: dict[str, Any],
    current_hour: dict[str, Any] | None,
) -> bool:
    """判斷扇區是否為當前時辰。"""
    if not current_hour:
        return False
    return (
        int(candidate.get("hour", -1)) == int(current_hour.get("hour", -2))
        and str(candidate.get("sequence", "")) == str(current_hour.get("sequence", ""))
    )


def build_planetary_hour_segments(
    daytime_hours: list[dict[str, Any]],
    nighttime_hours: list[dict[str, Any]],
    *,
    current_hour: dict[str, Any] | None = None,
) -> list[PlanetaryHourSegment]:
    """建立 24 小時（12+12）行星時辰輪資料。"""
    all_hours = [("day", item) for item in daytime_hours] + [("night", item) for item in nighttime_hours]
    segments: list[PlanetaryHourSegment] = []
    for index, (phase, item) in enumerate(all_hours):
        hour_number = int(item.get("hour", index + 1))
        theta_deg = 90 - index * 15
        planet_name = str(item.get("planet_en", ""))
        fortune_key = str(item.get("fortune", "bercampur"))
        fill_color, border_color = _FORTUNE_COLORS.get(fortune_key, _FORTUNE_COLORS["bercampur"])
        current = _is_current_hour(item, current_hour)
        if current:
            fill_color = "rgba(246, 216, 138, 0.96)"
            border_color = "#FDF2C0"
        start_dt = item.get("start")
        end_dt = item.get("end")
        time_span = ""
        if isinstance(start_dt, datetime) and isinstance(end_dt, datetime):
            time_span = f"{start_dt.strftime('%H:%M')}–{end_dt.strftime('%H:%M')}"
        hover_html = (
            f"<b>{'日時辰' if phase == 'day' else '夜時辰'} #{hour_number}</b><br>"
            f"{item.get('planet_zh', '')} / {planet_name} {item.get('planet_ar', '')}<br>"
            f"{_FORTUNE_LABELS.get(fortune_key, _FORTUNE_LABELS['bercampur'])}<br>"
            f"{time_span}"
        )
        segments.append(
            PlanetaryHourSegment(
                absolute_index=index + 1,
                hour_number=hour_number,
                phase=phase,
                theta_deg=theta_deg,
                width_deg=15.0,
                label=f"{hour_number:02d}",
                planet_symbol=_PLANET_SYMBOLS.get(planet_name, "✶"),
                planet_name=planet_name,
                fortune_label=_FORTUNE_LABELS.get(fortune_key, _FORTUNE_LABELS["bercampur"]),
                fill_color=fill_color,
                border_color=border_color,
                is_current=current,
                hover_html=hover_html,
            )
        )
    return segments


__all__ = [
    "DisplayScript",
    "HouseWheelSegment",
    "PlanetaryHourSegment",
    "build_house_wheel_segments",
    "build_planetary_hour_segments",
]
