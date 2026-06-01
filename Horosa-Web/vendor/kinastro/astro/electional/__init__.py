"""
astro/electional — Electional Astrology & Vedic Muhurta Module

Implements both Western Traditional Electional (William Lilly / Guido Bonatti /
Al-Biruni) and Vedic Muhurta (Muhurta Chintamani / Kalaprakashika / BPHS).

Western Electional:
  - Planetary Hours (Chaldean order, Lilly CA p. 483)
  - Moon state: Void of Course, Via Combusta, applying aspects, phase
  - Essential dignities: domicile, exaltation, detriment, fall, peregrine
  - Activity-specific rules for 9 common event types
  - Time-window search for best elections

Vedic Muhurta:
  - Panchanga (Tithi, Vara, Nakshatra, Yoga, Karana)
  - Gandanta detection (water/fire sign junctions)
  - Lagna (sidereal ascendant) quality assessment
  - Jupiter/Venus combustion check (vital for marriage)
  - Vishti Karana (Bhadra) detection

Sources:
  - William Lilly, "Christian Astrology" (1647) [CA]
  - Guido Bonatti, "Liber Astronomiae" (~1277) [LA]
  - Al-Biruni, "Book of Instruction in the Elements of the Art of Astrology" [BI]
  - Muhurta Chintamani [MC]
  - Kalaprakashika [KP]
  - Brihat Parashara Hora Shastra [BPHS]
"""

from .calculator import (
    compute_western_electional,
    compute_vedic_muhurta,
    compute_electional_chart,
    find_western_elections,
    find_vedic_muhurtas,
    WesternElectionalResult,
    VedicMuhurtaResult,
    ElectionalPlanet,
    WesternElectionalFactor,
    VedicMuhurtaFactor,
    PanchangaElement,
)
from .renderer import (
    render_streamlit,
    render_western_electional_svg,
    render_vedic_muhurta_svg,
)

__all__ = [
    "compute_western_electional",
    "compute_vedic_muhurta",
    "compute_electional_chart",
    "find_western_elections",
    "find_vedic_muhurtas",
    "WesternElectionalResult",
    "VedicMuhurtaResult",
    "ElectionalPlanet",
    "WesternElectionalFactor",
    "VedicMuhurtaFactor",
    "PanchangaElement",
    "render_streamlit",
    "render_western_electional_svg",
    "render_vedic_muhurta_svg",
]
