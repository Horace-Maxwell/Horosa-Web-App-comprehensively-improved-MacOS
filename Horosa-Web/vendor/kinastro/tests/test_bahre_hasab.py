from datetime import date

from astro.bahre_hasab import (
    EthiopianDate,
    analyze_bahre_hasab_date,
    compute_bahre_hasab_year,
    ethiopian_to_gregorian,
    gregorian_to_ethiopian,
)


def test_gregorian_to_ethiopian_new_year():
    et = gregorian_to_ethiopian(date(2024, 9, 11))
    assert et == EthiopianDate(2017, 1, 1)


def test_ethiopian_to_gregorian_new_year():
    g = ethiopian_to_gregorian(EthiopianDate(2017, 1, 1))
    assert g == date(2024, 9, 11)


def test_fasika_for_ethiopian_2017():
    y = compute_bahre_hasab_year(2017)
    assert y.fasika.gregorian == date(2025, 4, 20)


def test_movable_fast_offsets():
    y = compute_bahre_hasab_year(2016)
    f = {feast.key: feast for feast in y.movable_feasts}
    assert (y.fasika.gregorian - f["abiy_tsom_start"].gregorian).days == 55
    assert (y.fasika.gregorian - f["nenewe_start"].gregorian).days == 69


def test_date_analysis_contains_upcoming_feasts():
    analysis = analyze_bahre_hasab_date(date(2025, 1, 15))
    assert analysis.ethiopian_date.year == 2017
    assert len(analysis.upcoming_feasts) >= 1
