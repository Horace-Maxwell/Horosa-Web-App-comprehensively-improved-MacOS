"""European Geomancy figure definitions and SVG helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple


Pattern = Tuple[bool, bool, bool, bool]  # True=single dot, False=double dot


@dataclass(frozen=True)
class GeomanticFigure:
    """One classical geomantic figure."""

    latin: str
    zh: str
    pattern: Pattern
    element: str
    planet: str
    zodiac: str
    positive_keywords: Tuple[str, ...]
    negative_keywords: Tuple[str, ...]
    historical_meaning: str


# Canonical catalog used by the European Geomancy module.
FIGURES: Dict[str, GeomanticFigure] = {
    "Via": GeomanticFigure(
        latin="Via",
        zh="道路",
        pattern=(True, True, True, True),
        element="Water",
        planet="Moon",
        zodiac="Cancer",
        positive_keywords=("movement", "journey", "change"),
        negative_keywords=("instability", "drifting"),
        historical_meaning="Mutable lunar current; favorable for travel and transitions.",
    ),
    "Populus": GeomanticFigure(
        latin="Populus",
        zh="眾民",
        pattern=(False, False, False, False),
        element="Water",
        planet="Moon",
        zodiac="Cancer",
        positive_keywords=("community", "consensus", "adaptation"),
        negative_keywords=("passivity", "crowd pressure"),
        historical_meaning="The multitude; outcomes depend on environment and collective tide.",
    ),
    "Fortuna Major": GeomanticFigure(
        latin="Fortuna Major",
        zh="大福",
        pattern=(True, True, False, False),
        element="Fire",
        planet="Sun",
        zodiac="Leo",
        positive_keywords=("enduring success", "authority", "honor"),
        negative_keywords=("pride", "rigidity"),
        historical_meaning="Stable solar victory; durable gains and consolidated power.",
    ),
    "Fortuna Minor": GeomanticFigure(
        latin="Fortuna Minor",
        zh="小福",
        pattern=(False, False, True, True),
        element="Fire",
        planet="Sun",
        zodiac="Leo",
        positive_keywords=("timely help", "quick advantage", "momentum"),
        negative_keywords=("temporary luck", "dependency"),
        historical_meaning="Transient solar favor; success through support or opportunity windows.",
    ),
    "Acquisitio": GeomanticFigure(
        latin="Acquisitio",
        zh="獲得",
        pattern=(False, False, True, False),
        element="Air",
        planet="Jupiter",
        zodiac="Sagittarius",
        positive_keywords=("gain", "growth", "increase"),
        negative_keywords=("overexpansion", "greed"),
        historical_meaning="Jovial increase; acquisition of resources, status, or alliances.",
    ),
    "Amissio": GeomanticFigure(
        latin="Amissio",
        zh="失去",
        pattern=(True, False, False, True),
        element="Fire",
        planet="Venus",
        zodiac="Taurus",
        positive_keywords=("release", "detachment", "purging"),
        negative_keywords=("loss", "depletion"),
        historical_meaning="Venus inverted; relinquishment, expenditure, or emotional letting-go.",
    ),
    "Laetitia": GeomanticFigure(
        latin="Laetitia",
        zh="喜悅",
        pattern=(True, False, False, False),
        element="Fire",
        planet="Jupiter",
        zodiac="Pisces",
        positive_keywords=("joy", "blessing", "uplift"),
        negative_keywords=("naivety", "excess optimism"),
        historical_meaning="Ascending benefic form; grace, hope, and generosity.",
    ),
    "Tristitia": GeomanticFigure(
        latin="Tristitia",
        zh="悲傷",
        pattern=(False, False, False, True),
        element="Earth",
        planet="Saturn",
        zodiac="Aquarius",
        positive_keywords=("discipline", "endurance", "structure"),
        negative_keywords=("sorrow", "delay", "restriction"),
        historical_meaning="Descending saturnine force; heaviness, gravity, and hard lessons.",
    ),
    "Puella": GeomanticFigure(
        latin="Puella",
        zh="少女",
        pattern=(True, False, True, False),
        element="Air",
        planet="Venus",
        zodiac="Libra",
        positive_keywords=("harmony", "beauty", "diplomacy"),
        negative_keywords=("indecision", "avoidance"),
        historical_meaning="Venusian concord; social grace and reconciliatory tendency.",
    ),
    "Puer": GeomanticFigure(
        latin="Puer",
        zh="少年",
        pattern=(False, True, True, True),
        element="Fire",
        planet="Mars",
        zodiac="Aries",
        positive_keywords=("courage", "initiative", "combativeness"),
        negative_keywords=("impulse", "conflict", "recklessness"),
        historical_meaning="Martial eruption; forceful action and confrontation.",
    ),
    "Albus": GeomanticFigure(
        latin="Albus",
        zh="白",
        pattern=(True, False, True, True),
        element="Air",
        planet="Mercury",
        zodiac="Gemini",
        positive_keywords=("clarity", "learning", "communication"),
        negative_keywords=("cold detachment", "overanalysis"),
        historical_meaning="Mercurial purity; reasoned judgment and scholarly discourse.",
    ),
    "Rubeus": GeomanticFigure(
        latin="Rubeus",
        zh="赤",
        pattern=(False, True, False, True),
        element="Fire",
        planet="Mars",
        zodiac="Scorpio",
        positive_keywords=("intensity", "catharsis"),
        negative_keywords=("violence", "toxicity", "chaos"),
        historical_meaning="Corrupt martial form; often inauspicious except in destructive questions.",
    ),
    "Conjunctio": GeomanticFigure(
        latin="Conjunctio",
        zh="會合",
        pattern=(False, True, True, False),
        element="Air",
        planet="Mercury",
        zodiac="Virgo",
        positive_keywords=("meeting", "exchange", "agreement"),
        negative_keywords=("entanglement", "dependency"),
        historical_meaning="Mercurial joining; contracts, messages, crossroads, and negotiations.",
    ),
    "Carcer": GeomanticFigure(
        latin="Carcer",
        zh="囚禁",
        pattern=(True, True, False, True),
        element="Earth",
        planet="Saturn",
        zodiac="Capricorn",
        positive_keywords=("containment", "discipline", "preservation"),
        negative_keywords=("stagnation", "confinement"),
        historical_meaning="Saturn's enclosure; limits, walls, obligations, and delay.",
    ),
    "Caput Draconis": GeomanticFigure(
        latin="Caput Draconis",
        zh="龍首",
        pattern=(True, True, True, False),
        element="Earth",
        planet="North Node",
        zodiac="Virgo",
        positive_keywords=("entry", "new beginning", "opportunity"),
        negative_keywords=("restlessness", "overreach"),
        historical_meaning="Dragon's Head; opening gates and initiating cycles.",
    ),
    "Cauda Draconis": GeomanticFigure(
        latin="Cauda Draconis",
        zh="龍尾",
        pattern=(False, True, False, False),
        element="Fire",
        planet="South Node",
        zodiac="Sagittarius",
        positive_keywords=("closure", "purification", "release"),
        negative_keywords=("decay", "dissolution", "banishment"),
        historical_meaning="Dragon's Tail; endings, expulsions, and karmic discharge.",
    ),
}


def all_figures() -> Tuple[GeomanticFigure, ...]:
    """Return all 16 figures in stable insertion order."""
    return tuple(FIGURES.values())


def figure_from_pattern(pattern: Pattern) -> GeomanticFigure:
    """Return the figure matching a four-row dot pattern."""
    for fig in FIGURES.values():
        if fig.pattern == pattern:
            return fig
    raise ValueError(f"No geomantic figure for pattern: {pattern}")


def iter_figure_names() -> Iterable[str]:
    """Return all figure names in display order."""
    return FIGURES.keys()


def render_figure_svg(figure: GeomanticFigure, width: int = 120, with_title: bool = False) -> str:
    """Render one figure as a renaissance-styled SVG."""
    row_y = [28, 53, 78, 103]
    x_single = [width // 2]
    x_double = [width // 2 - 14, width // 2 + 14]
    dot_fill = "#D5B574"
    line = "#7A5A2A"
    bg = "#0F1118"

    h = width + (26 if with_title else 0)
    parts = [
        f'<svg viewBox="0 0 {width} {h}" width="{width}" height="{h}" xmlns="http://www.w3.org/2000/svg">',
        f'<rect x="1" y="1" width="{width-2}" height="{width-2}" rx="10" fill="{bg}" stroke="{line}" stroke-width="1.5"/>',
        f'<rect x="8" y="8" width="{width-16}" height="{width-16}" rx="8" fill="none" stroke="{line}" stroke-dasharray="5 3" opacity="0.7"/>',
    ]
    for i, single in enumerate(figure.pattern):
        y = row_y[i]
        for x in (x_single if single else x_double):
            parts.append(f'<circle cx="{x}" cy="{y}" r="5.2" fill="{dot_fill}"/>')
    if with_title:
        parts.append(
            f'<text x="{width/2:.1f}" y="{width+18}" text-anchor="middle" fill="#E8D7AE" font-size="11" font-family="serif">{figure.latin}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)
