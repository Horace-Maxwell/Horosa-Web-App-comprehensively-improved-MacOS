from astro.i18n import TRANSLATIONS
from astro.system_registry import get_system, search_systems


def test_kinketika_is_registered_for_sidebar() -> None:
    system = get_system("tab_kinketika")
    assert system is not None
    assert system.category == "cat_asian"
    assert system.tab_key == "tab_kinketika"


def test_kinketika_search_and_translations_exist() -> None:
    hits = [system.id for system in search_systems("kinketika")]
    assert "tab_kinketika" in hits

    zh_hits = [system.id for system in search_systems("七星五刻")]
    assert "tab_kinketika" in zh_hits

    for key in (
        "tab_kinketika",
        "desc_kinketika",
        "spinner_kinketika",
        "sys_hint_kinketika",
        "info_kinketika_prompt",
    ):
        assert key in TRANSLATIONS
        assert TRANSLATIONS[key]["zh"]
        assert TRANSLATIONS[key]["en"]
