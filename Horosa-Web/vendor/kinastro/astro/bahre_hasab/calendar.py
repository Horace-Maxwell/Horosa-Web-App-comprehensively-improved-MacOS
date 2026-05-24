"""Traditional Bahre Hasab calendar core for Ethiopian Orthodox computation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


ETHIOPIAN_EPOCH_JDN = 1724221  # 1 Mäskäräm 1 (E.C.) in proleptic Gregorian JDN mapping


@dataclass(frozen=True)
class EthiopianDate:
    year: int
    month: int
    day: int

    def iso(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"


@dataclass(frozen=True)
class FeastDay:
    key: str
    name_geez: str
    name_en: str
    gregorian: date
    ethiopian: EthiopianDate
    is_fast: bool = False


@dataclass(frozen=True)
class BahreHasabYear:
    ethiopian_year: int
    amete_alem: int
    wenber: int
    abekte: int
    metqi: int
    evangelist: str
    fasika: FeastDay
    movable_feasts: tuple[FeastDay, ...]


def _gregorian_to_jdn(g: date) -> int:
    a = (14 - g.month) // 12
    y = g.year + 4800 - a
    m = g.month + 12 * a - 3
    return g.day + ((153 * m + 2) // 5) + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _jdn_to_gregorian(jdn: int) -> date:
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + (m // 10)
    return date(year, month, day)


def _julian_to_jdn(year: int, month: int, day: int) -> int:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + ((153 * m + 2) // 5) + 365 * y + y // 4 - 32083


def ethiopian_to_gregorian(ethiopian: EthiopianDate) -> date:
    jdn = (
        ETHIOPIAN_EPOCH_JDN
        + 365 * (ethiopian.year - 1)
        + (ethiopian.year // 4)
        + 30 * (ethiopian.month - 1)
        + (ethiopian.day - 1)
    )
    return _jdn_to_gregorian(jdn)


def gregorian_to_ethiopian(gregorian: date) -> EthiopianDate:
    jdn = _gregorian_to_jdn(gregorian)

    approx_year = max(1, ((jdn - ETHIOPIAN_EPOCH_JDN) // 366) + 1)
    while ethiopian_to_gregorian(EthiopianDate(approx_year + 1, 1, 1)) <= gregorian:
        approx_year += 1
    while ethiopian_to_gregorian(EthiopianDate(approx_year, 1, 1)) > gregorian:
        approx_year -= 1

    start_jdn = _gregorian_to_jdn(ethiopian_to_gregorian(EthiopianDate(approx_year, 1, 1)))
    day_of_year = jdn - start_jdn
    month = day_of_year // 30 + 1
    day = day_of_year % 30 + 1
    return EthiopianDate(approx_year, month, day)


def _orthodox_easter_gregorian(gregorian_year: int) -> date:
    """Compute Orthodox Easter by Julian Paschalion and convert to Gregorian."""
    a = gregorian_year % 4
    b = gregorian_year % 7
    c = gregorian_year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month = (d + e + 114) // 31
    day = ((d + e + 114) % 31) + 1

    jdn_julian = _julian_to_jdn(gregorian_year, month, day)
    return _jdn_to_gregorian(jdn_julian)


def _feast(key: str, geez: str, en: str, g: date, is_fast: bool = False) -> FeastDay:
    return FeastDay(
        key=key,
        name_geez=geez,
        name_en=en,
        gregorian=g,
        ethiopian=gregorian_to_ethiopian(g),
        is_fast=is_fast,
    )


def compute_bahre_hasab_year(ethiopian_year: int) -> BahreHasabYear:
    amete_alem = ethiopian_year + 5500
    wenber = amete_alem % 19
    abekte = (11 * wenber) % 30
    metqi = 0 if abekte == 0 else 30 - abekte

    evangelists = ["ዮሐንስ", "ማቴዎስ", "ማርቆስ", "ሉቃስ"]
    evangelist = evangelists[ethiopian_year % 4]

    fasika_g = _orthodox_easter_gregorian(ethiopian_year + 8)

    movable = (
        _feast("nenewe_start", "ጾመ ነነዌ መጀመሪያ", "Fast of Nineveh (Start)", fasika_g - timedelta(days=69), is_fast=True),
        _feast("abiy_tsom_start", "ዐቢይ ጾም መጀመሪያ", "Great Lent (Start)", fasika_g - timedelta(days=55), is_fast=True),
        _feast("holy_week_start", "ሰሙነ ሕማማት መጀመሪያ", "Holy Week (Start)", fasika_g - timedelta(days=6), is_fast=True),
        _feast("hosaena", "ሆሳዕና", "Palm Sunday", fasika_g - timedelta(days=7)),
        _feast("siqlet", "ስቅለት", "Good Friday", fasika_g - timedelta(days=2), is_fast=True),
        _feast("fasika", "ፋሲካ", "Fasika (Easter)", fasika_g),
        _feast("rikbe_kahinat", "ርክበ ካህናት", "Ascension", fasika_g + timedelta(days=39)),
        _feast("peraklitos", "ጰራቅሊጦስ", "Pentecost", fasika_g + timedelta(days=49)),
        _feast("tsome_hawariat_start", "ጾመ ሐዋርያት መጀመሪያ", "Apostles' Fast (Start)", fasika_g + timedelta(days=50), is_fast=True),
    )

    return BahreHasabYear(
        ethiopian_year=ethiopian_year,
        amete_alem=amete_alem,
        wenber=wenber,
        abekte=abekte,
        metqi=metqi,
        evangelist=evangelist,
        fasika=next(f for f in movable if f.key == "fasika"),
        movable_feasts=movable,
    )
