"""
astro/astronomical_geomancy/models.py
══════════════════════════════════════════════════════════════
Data-classes for Astronomical Geomancy chart results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


@dataclass
class GeomancyFigure:
    """One geomantic figure generated for a reading."""
    name_en: str
    name_zh: str
    dots: List[bool]          # True = single dot, False = double dots (4 rows)
    element: str
    element_zh: str
    planet: str
    planet_zh: str
    sign: str
    sign_zh: str
    sign_num: int             # 0-based index into ZODIAC_SIGNS
    quality: str              # "fortunate" | "neutral" | "unfortunate"
    quality_zh: str
    keywords_zh: str
    keywords_en: str

    def dot_pattern_str(self) -> str:
        """Return ASCII dot pattern (4 lines)."""
        lines = []
        for single in self.dots:
            lines.append("•" if single else "∶")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Geomancy mode and layout enumerations
# ─────────────────────────────────────────────────────────────────────────────

class GeomancyMode(str, Enum):
    """Casting mode: horary question or natal-chart transcoding."""
    horary = "horary"
    natal_transcode = "natal_transcode"


class GeomancyLayout(str, Enum):
    """Chart layout: classical 4×4 square or linear shield."""
    square = "square"
    shield = "shield"


# ─────────────────────────────────────────────────────────────────────────────
# Extended figure meaning (typed catalog entry)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class FigureMeaning:
    """Bilingual meaning record for a geomantic figure."""
    latin: str
    zh: str
    en: str
    astrology: str
    omen_zh: str
    wiki_url: str


@dataclass
class PlanetInHouse:
    """One planet placed in a specific house."""
    planet_key: str
    planet_en: str
    planet_zh: str
    glyph: str
    house: int                # 1-12
    sign: str
    sign_zh: str
    sign_num: int
    nature: str
    nature_zh: str
    remainder: int            # raw remainder value used to determine house


@dataclass
class HouseInfo:
    """One house in the geomantic chart."""
    house: int                # 1-12
    sign: str                 # e.g. "Aries"
    sign_zh: str              # e.g. "白羊座"
    sign_num: int             # 0-11
    glyph: str                # ♈ etc.
    element: str
    quality: str
    name_en: str
    name_zh: str
    topics_zh: str
    topics_en: str
    gerard_zh: str
    planets: List[PlanetInHouse] = field(default_factory=list)


@dataclass
class GeomancyChart:
    """Complete Astronomical Geomancy reading."""
    # Input parameters
    question: str
    question_type: str
    question_type_zh: str
    seed_mode: str            # "random" | "time_seed"
    seed: int

    # Mother figures (4 generated, first = ascendant figure)
    mother_figures: List[GeomancyFigure]

    # Ascendant figure → Ascendant sign
    ascendant_figure: GeomancyFigure
    ascendant_sign: str
    ascendant_sign_zh: str
    ascendant_sign_num: int   # 0-11

    # 12 houses
    houses: List[HouseInfo]   # index 0 = house 1

    # Planet placements
    planet_placements: List[PlanetInHouse]

    # Primary house for the question (1-12)
    primary_house: int

    # Timestamp
    timestamp: str

    # ── Shield chain / Square chart fields (populated by _build_shield_chain) ─
    # Casting mode and layout (default: horary / square)
    mode: str = "horary"
    layout: str = "square"

    # All 16 figures in row-major order for the square chart
    # (Mothers 1-4, Daughters 1-4, Nieces 1-4, Witnesses + Judge + Reconciler)
    figures_16: List[GeomancyFigure] = field(default_factory=list)

    # Derived special figures
    judge: Optional[GeomancyFigure] = None
    reconciler: Optional[GeomancyFigure] = None

    # Short summary text (displayed in the centre of the square chart)
    summary_text: str = ""

    def to_json(self) -> dict:
        """Serialise to plain dict for JSON export / AI prompt."""
        return {
            "question": self.question,
            "question_type": self.question_type,
            "seed_mode": self.seed_mode,
            "ascendant_sign": self.ascendant_sign,
            "ascendant_figure": self.ascendant_figure.name_en,
            "houses": [
                {
                    "house": h.house,
                    "sign": h.sign,
                    "sign_zh": h.sign_zh,
                    "planets": [p.planet_en for p in h.planets],
                }
                for h in self.houses
            ],
            "planet_placements": [
                {
                    "planet": p.planet_en,
                    "house": p.house,
                    "sign": p.sign,
                }
                for p in self.planet_placements
            ],
        }
