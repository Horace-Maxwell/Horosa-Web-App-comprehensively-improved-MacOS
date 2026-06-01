"""astro/burmese/mahabote.py

Phase-1 Burmese Mahabote core computation.

Design goals:
- Traditional-first calculation for Myanmar year and 8-symbol weekday logic.
- Wednesday split into AM / PM symbols.
- Fixed 8-direction symbol wheel and 8-house mapping.
- Pure compute module (no Streamlit import).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Literal, Optional, TypedDict

Language = Literal["zh", "en"]
DEFAULT_THINGYAN_CUTOFF_DAY = 17

THINGYAN_CUTOFF_OVERRIDES: Dict[int, int] = {
    # Optional year-specific override for Myanmar New Year day in April.
    # Default behavior (no override): DEFAULT_THINGYAN_CUTOFF_DAY (April 17).
    # Example: {2024: 16}
}

class SymbolInfo(TypedDict):
    key: str
    weekday: str
    weekday_number: int
    direction: str
    direction_zh: str
    planet: str
    planet_symbol: str
    planet_zh: str
    animal: str
    animal_zh: str
    animal_icon: str
    color: str


MAHABOTE_HOUSES: List[Dict[str, str]] = [
    {"key": "bhin", "name_zh": "本命宮", "name_en": "Bhin", "theme_zh": "性格", "theme_en": "Character"},
    {"key": "ayu", "name_zh": "壽命宮", "name_en": "Ayu", "theme_zh": "健康", "theme_en": "Vitality"},
    {"key": "winya", "name_zh": "意識宮", "name_en": "Winya", "theme_zh": "學習", "theme_en": "Mind"},
    {"key": "kiya", "name_zh": "身體宮", "name_en": "Kiya", "theme_zh": "生活", "theme_en": "Body"},
    {"key": "hein", "name_zh": "權勢宮", "name_en": "Hein", "theme_zh": "事業", "theme_en": "Career"},
    {"key": "marana", "name_zh": "死亡宮", "name_en": "Marana", "theme_zh": "挑戰", "theme_en": "Trials"},
    {"key": "thila", "name_zh": "道德宮", "name_en": "Thila", "theme_zh": "德行", "theme_en": "Virtue"},
    {"key": "kamma", "name_zh": "業力宮", "name_en": "Kamma", "theme_zh": "業力", "theme_en": "Karma"},
]

SYMBOLS_8: List[SymbolInfo] = [
    {
        "key": "sun",
        "weekday": "sunday",
        "weekday_number": 1,
        "direction": "NE",
        "direction_zh": "東北",
        "planet": "Sun",
        "planet_symbol": "☉",
        "planet_zh": "太陽",
        "animal": "Garuda",
        "animal_zh": "迦樓羅",
        "animal_icon": "🦅",
        "color": "#D4AF37",
    },
    {
        "key": "moon",
        "weekday": "monday",
        "weekday_number": 2,
        "direction": "E",
        "direction_zh": "東",
        "planet": "Moon",
        "planet_symbol": "☽",
        "planet_zh": "月亮",
        "animal": "Tiger",
        "animal_zh": "虎",
        "animal_icon": "🐅",
        "color": "#B0C4DE",
    },
    {
        "key": "mars",
        "weekday": "tuesday",
        "weekday_number": 3,
        "direction": "SE",
        "direction_zh": "東南",
        "planet": "Mars",
        "planet_symbol": "♂",
        "planet_zh": "火星",
        "animal": "Lion",
        "animal_zh": "獅",
        "animal_icon": "🦁",
        "color": "#C0392B",
    },
    {
        "key": "mercury_am",
        "weekday": "wednesday_am",
        "weekday_number": 4,
        "direction": "S",
        "direction_zh": "南",
        "planet": "Mercury",
        "planet_symbol": "☿",
        "planet_zh": "水星",
        "animal": "Tusked Elephant",
        "animal_zh": "有牙象",
        "animal_icon": "🐘",
        "color": "#2E8B57",
    },
    {
        "key": "rahu_pm",
        "weekday": "wednesday_pm",
        "weekday_number": 5,
        "direction": "SW",
        "direction_zh": "西南",
        "planet": "Rahu",
        "planet_symbol": "☊",
        "planet_zh": "羅睺",
        "animal": "Tuskless Elephant",
        "animal_zh": "無牙象",
        "animal_icon": "🐘",
        "color": "#8E44AD",
    },
    {
        "key": "jupiter",
        "weekday": "thursday",
        "weekday_number": 6,
        "direction": "W",
        "direction_zh": "西",
        "planet": "Jupiter",
        "planet_symbol": "♃",
        "planet_zh": "木星",
        "animal": "Rat",
        "animal_zh": "鼠",
        "animal_icon": "🐀",
        "color": "#4169E1",
    },
    {
        "key": "venus",
        "weekday": "friday",
        "weekday_number": 7,
        "direction": "NW",
        "direction_zh": "西北",
        "planet": "Venus",
        "planet_symbol": "♀",
        "planet_zh": "金星",
        "animal": "Guinea Pig",
        "animal_zh": "天竺鼠",
        "animal_icon": "🐹",
        "color": "#DB7093",
    },
    {
        "key": "saturn",
        "weekday": "saturday",
        "weekday_number": 8,
        "direction": "N",
        "direction_zh": "北",
        "planet": "Saturn",
        "planet_symbol": "♄",
        "planet_zh": "土星",
        "animal": "Naga",
        "animal_zh": "那伽",
        "animal_icon": "🐉",
        "color": "#5D6D7E",
    },
]

WEEKDAY_TO_SYMBOL_KEY = {
    "sunday": "sun",
    "monday": "moon",
    "tuesday": "mars",
    "wednesday_am": "mercury_am",
    "wednesday_pm": "rahu_pm",
    "thursday": "jupiter",
    "friday": "venus",
    "saturday": "saturn",
}

SYMBOL_INDEX = {item["key"]: i for i, item in enumerate(SYMBOLS_8)}
SYMBOL_BY_KEY = {item["key"]: item for item in SYMBOLS_8}
WEEKDAY_BASE_KEY = {
    0: "sunday",
    1: "monday",
    2: "tuesday",
    4: "thursday",
    5: "friday",
    6: "saturday",
}


class BirthWeekdayInfo(TypedDict):
    weekday_index: int
    is_wednesday_pm: bool
    weekday_key: str
    weekday_name_en: str
    weekday_name_zh: str


@dataclass(frozen=True)
class HousePlacement:
    index: int
    house_key: str
    house_name_zh: str
    house_name_en: str
    theme_zh: str
    theme_en: str
    symbol_key: str
    direction: str
    direction_zh: str
    planet: str
    planet_zh: str
    planet_symbol: str
    animal: str
    animal_zh: str
    animal_icon: str
    is_birth_house: bool


@dataclass
class BurmeseMahaboteChart:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str = ""

    myanmar_year: int = 0
    weekday_index: int = 0
    weekday_name: str = ""
    is_wednesday_pm: bool = False
    symbol_key: str = ""
    symbol_index: int = 0
    symbol_weekday_number: int = 0
    mahabote_value: int = 0
    birth_house_index: int = 0

    houses: List[HousePlacement] = field(default_factory=list)
    wheel_symbols: List[SymbolInfo] = field(default_factory=list)

    def summary(self, lang: Language = "zh") -> str:
        if lang == "en":
            house = MAHABOTE_HOUSES[self.birth_house_index]["name_en"]
            symbol = SYMBOL_BY_KEY[self.symbol_key]
            return (
                f"Myanmar Year {self.myanmar_year}, {self.weekday_name} birth, "
                f"symbol {symbol['planet']} ({symbol['direction']}), birth house {house}."
            )
        house = MAHABOTE_HOUSES[self.birth_house_index]["name_zh"]
        symbol = SYMBOL_BY_KEY[self.symbol_key]
        return (
            f"緬曆 {self.myanmar_year} 年，{self.weekday_name} 出生，"
            f"命曜為{symbol['planet_zh']}（{symbol['direction_zh']}），命宮在{house}。"
        )


def _thingyan_cutoff_day(year: int) -> int:
    """Return the Myanmar New Year day in April used for traditional conversion."""
    return THINGYAN_CUTOFF_OVERRIDES.get(year, DEFAULT_THINGYAN_CUTOFF_DAY)


def gregorian_to_myanmar_year(year: int, month: int, day: int) -> int:
    """Traditional Myanmar Era conversion with configurable Thingyan cutoff.

    - On/after Thingyan cutoff in April: ME = Gregorian - 638
    - Before cutoff: ME = Gregorian - 639
    """
    cutoff = _thingyan_cutoff_day(year)
    if month > 4 or (month == 4 and day >= cutoff):
        return year - 638
    return year - 639


def birth_weekday_info(year: int, month: int, day: int, hour: int) -> BirthWeekdayInfo:
    """Return weekday split into 8 Mahabote symbols (Wednesday AM/PM split)."""
    wd = date(year, month, day).weekday()  # Mon=0..Sun=6
    idx = (wd + 1) % 7  # Sun=0..Sat=6
    names_en = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    names_zh = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]

    is_wed_pm = idx == 3 and hour >= 12
    if idx == 3 and is_wed_pm:
        key = "wednesday_pm"
        name_en = "Wednesday PM"
        name_zh = "星期三下午"
    elif idx == 3:
        key = "wednesday_am"
        name_en = "Wednesday AM"
        name_zh = "星期三上午"
    else:
        key = WEEKDAY_BASE_KEY[idx]
        name_en = names_en[idx]
        name_zh = names_zh[idx]

    return {
        "weekday_index": idx,
        "is_wednesday_pm": is_wed_pm,
        "weekday_key": key,
        "weekday_name_en": name_en,
        "weekday_name_zh": name_zh,
    }


def _build_houses(symbol_index: int, birth_house_index: int) -> List[HousePlacement]:
    houses: List[HousePlacement] = []
    for house_idx, house in enumerate(MAHABOTE_HOUSES):
        shift = (house_idx - birth_house_index) % 8
        resident_idx = (symbol_index + shift) % 8
        symbol = SYMBOLS_8[resident_idx]
        houses.append(
            HousePlacement(
                index=house_idx,
                house_key=str(house["key"]),
                house_name_zh=str(house["name_zh"]),
                house_name_en=str(house["name_en"]),
                theme_zh=str(house["theme_zh"]),
                theme_en=str(house["theme_en"]),
                symbol_key=str(symbol["key"]),
                direction=str(symbol["direction"]),
                direction_zh=str(symbol["direction_zh"]),
                planet=str(symbol["planet"]),
                planet_zh=str(symbol["planet_zh"]),
                planet_symbol=str(symbol["planet_symbol"]),
                animal=str(symbol["animal"]),
                animal_zh=str(symbol["animal_zh"]),
                animal_icon=str(symbol["animal_icon"]),
                is_birth_house=(house_idx == birth_house_index),
            )
        )
    return houses


def compute_burmese_mahabote(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    language: Optional[Language] = None,
) -> BurmeseMahaboteChart:
    """Compute phase-1 Burmese Mahabote chart (traditional method only)."""
    weekday_info = birth_weekday_info(year, month, day, hour)
    symbol_key = WEEKDAY_TO_SYMBOL_KEY[str(weekday_info["weekday_key"])]
    symbol = SYMBOL_BY_KEY[symbol_key]
    symbol_index = SYMBOL_INDEX[symbol_key]

    me_year = gregorian_to_myanmar_year(year, month, day)
    weekday_number = int(symbol["weekday_number"])
    mahabote_value = (me_year + weekday_number) % 8
    birth_house_index = mahabote_value

    houses = _build_houses(symbol_index=symbol_index, birth_house_index=birth_house_index)
    weekday_name = str(weekday_info["weekday_name_zh"])
    if language == "en":
        weekday_name = str(weekday_info["weekday_name_en"])

    return BurmeseMahaboteChart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        myanmar_year=me_year,
        weekday_index=int(weekday_info["weekday_index"]),
        weekday_name=weekday_name,
        is_wednesday_pm=bool(weekday_info["is_wednesday_pm"]),
        symbol_key=symbol_key,
        symbol_index=symbol_index,
        symbol_weekday_number=weekday_number,
        mahabote_value=mahabote_value,
        birth_house_index=birth_house_index,
        houses=houses,
        wheel_symbols=[dict(x) for x in SYMBOLS_8],
    )


__all__ = [
    "BurmeseMahaboteChart",
    "HousePlacement",
    "MAHABOTE_HOUSES",
    "SYMBOLS_8",
    "compute_burmese_mahabote",
    "gregorian_to_myanmar_year",
    "birth_weekday_info",
]
