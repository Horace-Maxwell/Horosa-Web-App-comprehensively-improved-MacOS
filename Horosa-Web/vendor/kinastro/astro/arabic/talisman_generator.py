"""
Picatrix Talisman utility helpers.
"""

from __future__ import annotations

from typing import Any
import re

from .picatrix_invocations import Planet, build_spirit_invocation_steps


PLANET_ALIASES = {
    "saturn": Planet.SATURN,
    "土星": Planet.SATURN,
    "jupiter": Planet.JUPITER,
    "木星": Planet.JUPITER,
    "mars": Planet.MARS,
    "火星": Planet.MARS,
    "sun": Planet.SUN,
    "太陽": Planet.SUN,
    "venus": Planet.VENUS,
    "金星": Planet.VENUS,
    "mercury": Planet.MERCURY,
    "水星": Planet.MERCURY,
    "moon": Planet.MOON,
    "月亮": Planet.MOON,
}

PLANET_SCAN_ORDER = [
    (re.compile(r"\bsaturn\b"), "土星", Planet.SATURN),
    (re.compile(r"\bjupiter\b"), "木星", Planet.JUPITER),
    (re.compile(r"\bmars\b"), "火星", Planet.MARS),
    (re.compile(r"\bsun\b"), "太陽", Planet.SUN),
    (re.compile(r"\bvenus\b"), "金星", Planet.VENUS),
    (re.compile(r"\bmercury\b"), "水星", Planet.MERCURY),
    (re.compile(r"\bmoon\b"), "月亮", Planet.MOON),
]


def _infer_planet_from_talisman(talisman: dict[str, Any]) -> Planet | None:
    if talisman.get("planet"):
        key = str(talisman["planet"]).strip().lower()
        if key in PLANET_ALIASES:
            return PLANET_ALIASES[key]
    timing = str(talisman.get("timing", ""))
    purpose = str(talisman.get("purpose", ""))
    payload = f"{timing} {purpose}".lower()
    for en_pattern, zh_token, planet in PLANET_SCAN_ORDER:
        if en_pattern.search(payload) or zh_token in payload:
            return planet
    return None


def build_talisman_ritual_steps(
    talisman: dict[str, Any],
    spirit_invocation: bool = True,
    language: str = "zh",
) -> list[str]:
    steps: list[str] = []
    if talisman.get("timing"):
        steps.append(f"選時：{talisman['timing']}")
    if talisman.get("materials"):
        steps.append(f"材質：{talisman['materials']}")
    if talisman.get("procedure"):
        steps.append(f"製作：{talisman['procedure']}")

    if spirit_invocation:
        planet = _infer_planet_from_talisman(talisman)
        if planet is not None:
            steps.extend(build_spirit_invocation_steps(planet, language=language))
    return steps


def generate_talisman_recipe(
    talisman: dict[str, Any],
    spirit_invocation: bool = True,
    language: str = "zh",
) -> dict[str, Any]:
    recipe = dict(talisman)
    recipe["ritual_steps"] = build_talisman_ritual_steps(
        talisman=talisman,
        spirit_invocation=spirit_invocation,
        language=language,
    )
    return recipe
