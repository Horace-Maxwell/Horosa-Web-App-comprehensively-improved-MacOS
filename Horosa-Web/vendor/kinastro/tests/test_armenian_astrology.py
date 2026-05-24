import pytest

st = pytest.importorskip("streamlit")

from astro.systems.obscure.armenian import ArmenianChart


def test_haykian_date_conversion_smoke():
    d = ArmenianChart._to_haykian_date(2024, 5, 19, 40.17)
    assert d["hayk_year"] == 2575
    assert 1 <= d["hayk_month"] <= 13
    assert 1 <= d["hayk_day"] <= 30


def test_sign_mapping_boundaries():
    en0, hy0, _, deg0 = ArmenianChart._map_sign(0.0)
    en1, hy1, _, deg1 = ArmenianChart._map_sign(29.999)
    en2, hy2, _, deg2 = ArmenianChart._map_sign(30.0)
    assert en0 == "Aries" and hy0 == "Խոյ" and abs(deg0 - 0.0) < 1e-9
    assert en1 == "Aries" and hy1 == "Խոյ" and deg1 > 29.0
    assert en2 == "Taurus" and hy2 == "Ցուլ" and abs(deg2 - 0.0) < 1e-9
