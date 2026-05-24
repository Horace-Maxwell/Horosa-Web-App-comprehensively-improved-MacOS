from astro.arabic.picatrix_invocations import (
    Planet,
    PICATRIX_SPIRITS,
    perfect_nature_invocation,
    generate_talisman_invocation,
)
from astro.arabic.talisman_generator import generate_talisman_recipe


def test_perfect_nature_structure():
    ritual = perfect_nature_invocation()
    assert ritual["timing"]
    assert ritual["repetitions"] == 7
    assert len(ritual["names"]["arabic"]) == 4
    assert len(ritual["step"]) >= 3


def test_planetary_spirits_complete():
    assert len(PICATRIX_SPIRITS) == 7
    assert Planet.SATURN in PICATRIX_SPIRITS
    assert PICATRIX_SPIRITS[Planet.VENUS].invocation_text["zh"]


def test_generate_invocation_text():
    text = generate_talisman_invocation(Planet.MARS, purpose="protection", language="zh")
    assert "火星" in text
    assert "祈請文" in text


def test_talisman_recipe_includes_spirit_steps():
    talisman = {
        "planet": "Saturn",
        "timing": "土星日時 + 上升摩羯座第二面相",
        "materials": "鉛板 + 戴勝鳥腦",
        "procedure": "埋於目標地點",
    }
    with_spirit = generate_talisman_recipe(talisman, spirit_invocation=True, language="zh")
    without_spirit = generate_talisman_recipe(talisman, spirit_invocation=False, language="zh")
    assert len(with_spirit["ritual_steps"]) > len(without_spirit["ritual_steps"])
    assert any("朗誦靈名" in step for step in with_spirit["ritual_steps"])
