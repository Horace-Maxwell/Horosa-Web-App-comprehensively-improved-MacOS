import pytest

from astro.huangji import compute_huangji_pan
from astro.huangji.huangji import EXPECTED_GUA_KEYS
from astro.i18n import TRANSLATIONS
from astro.system_registry import get_system, search_systems


def test_huangji_compute_basic_structure() -> None:
    chart = compute_huangji_pan(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        timezone=8.0,
        latitude=25.033,
        longitude=121.565,
        location_name="Taipei",
        include_cross_system=False,
        reference_year=2025,
    )

    assert chart.system == "huangji"
    pan = chart.huangji_pan
    assert pan.yuan >= 1
    assert 1 <= pan.hui <= 12
    assert 1 <= pan.yun <= 30
    assert 1 <= pan.shi <= 12
    assert set(EXPECTED_GUA_KEYS).issubset(set(pan.gua.keys()))
    payload = chart.to_dict()
    assert "huangji_pan" in payload


def test_huangji_registry_and_i18n() -> None:
    system = get_system("tab_huangji")
    assert system is not None
    assert system.category == "cat_chinese"
    assert system.tab_key == "tab_huangji"

    hits = [system.id for system in search_systems("huangji")]
    assert "tab_huangji" in hits

    zh_hits = [system.id for system in search_systems("皇極")]
    assert "tab_huangji" in zh_hits

    for key in (
        "tab_huangji",
        "desc_huangji",
        "spinner_huangji",
        "sys_hint_huangji",
        "info_huangji_prompt",
    ):
        assert key in TRANSLATIONS
        assert TRANSLATIONS[key]["zh"]
        assert TRANSLATIONS[key]["en"]
