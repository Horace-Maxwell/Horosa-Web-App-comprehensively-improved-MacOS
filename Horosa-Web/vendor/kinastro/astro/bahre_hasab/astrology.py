"""Traditional Bahre Hasab Hasabe Kewakibit cycle helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .calendar import BahreHasabYear, EthiopianDate


_WEEKDAY_GEEZ = ["እሑድ", "ሰኞ", "ማክሰኞ", "ረቡዕ", "ሐሙስ", "ዓርብ", "ቅዳሜ"]
_PLANETARY_LORDS = ["☉", "☽", "♂", "☿", "♃", "♀", "♄"]


@dataclass(frozen=True)
class KewakibitResult:
    weekday_name_geez: str
    weekday_name_en: str
    weekday_planet_lord: str
    solar_cycle_index: int
    lunar_cycle_index: int
    metqi: int
    abekte: int


def compute_kewakibit_cycles(ethiopian_date: EthiopianDate, bahre_year: BahreHasabYear) -> KewakibitResult:
    ordinal = (ethiopian_date.month - 1) * 30 + ethiopian_date.day
    weekday_index = (bahre_year.amete_alem + ordinal) % 7

    weekday_en = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][weekday_index]

    return KewakibitResult(
        weekday_name_geez=_WEEKDAY_GEEZ[weekday_index],
        weekday_name_en=weekday_en,
        weekday_planet_lord=_PLANETARY_LORDS[weekday_index],
        solar_cycle_index=bahre_year.ethiopian_year % 4,
        lunar_cycle_index=bahre_year.wenber,
        metqi=bahre_year.metqi,
        abekte=bahre_year.abekte,
    )
