"""Bahre Hasab orchestrator (calendar + hasabe kewakibit)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .astrology import KewakibitResult, compute_kewakibit_cycles
from .calendar import (
    BahreHasabYear,
    EthiopianDate,
    FeastDay,
    compute_bahre_hasab_year,
    gregorian_to_ethiopian,
)


@dataclass(frozen=True)
class BahreHasabDateAnalysis:
    input_gregorian: date
    ethiopian_date: EthiopianDate
    bahre_year: BahreHasabYear
    kewakibit: KewakibitResult
    upcoming_feasts: tuple[FeastDay, ...]


def analyze_bahre_hasab_date(gregorian_date: date) -> BahreHasabDateAnalysis:
    et_date = gregorian_to_ethiopian(gregorian_date)
    year_data = compute_bahre_hasab_year(et_date.year)
    kewakibit = compute_kewakibit_cycles(et_date, year_data)

    upcoming = tuple(
        feast for feast in year_data.movable_feasts if feast.gregorian >= gregorian_date
    )

    return BahreHasabDateAnalysis(
        input_gregorian=gregorian_date,
        ethiopian_date=et_date,
        bahre_year=year_data,
        kewakibit=kewakibit,
        upcoming_feasts=upcoming,
    )


def annual_bahre_hasab_overview(ethiopian_year: int) -> dict[str, object]:
    y = compute_bahre_hasab_year(ethiopian_year)
    return {
        "ethiopian_year": y.ethiopian_year,
        "amete_alem": y.amete_alem,
        "wenber": y.wenber,
        "abekte": y.abekte,
        "metqi": y.metqi,
        "evangelist": y.evangelist,
        "feasts": y.movable_feasts,
    }
