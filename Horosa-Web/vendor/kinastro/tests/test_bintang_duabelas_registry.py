from astro.i18n import TRANSLATIONS
from astro.system_registry import get_system, search_systems


def test_bintang_duabelas_is_registered_for_sidebar() -> None:
    system = get_system("tab_bintang_duabelas")
    assert system is not None
    assert system.category == "cat_asian"
    assert system.tab_key == "tab_bintang_duabelas"


def test_bintang_duabelas_search_and_translations_exist() -> None:
    hits = [system.id for system in search_systems("bintang")]
    assert "tab_bintang_duabelas" in hits
    zh_hits = [system.id for system in search_systems("馬來伊斯蘭")]
    assert "tab_bintang_duabelas" in zh_hits

    for key in (
        "tab_bintang_duabelas",
        "desc_bintang_duabelas",
        "spinner_bintang_duabelas",
        "sys_hint_bintang_duabelas",
        "info_bintang_duabelas_prompt",
    ):
        assert key in TRANSLATIONS
        assert TRANSLATIONS[key]["zh"]
        assert TRANSLATIONS[key]["en"]

    assert "十二星" in TRANSLATIONS["tab_bintang_duabelas"]["zh"]
