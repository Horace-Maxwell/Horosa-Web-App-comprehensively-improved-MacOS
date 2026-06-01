"""
astro/andean — Inca / Andean Astrology Module for KinAstro
==========================================================

Implements the Andean cosmological framework centred on:
  • Mayu (天河 / Milky Way) — the sacred river connecting the three worlds
  • Yana Phuyu (暗星宿 / Dark Cloud Constellations) — living animal spirits in the
    dark rifts of the Milky Way, the primary "zodiac" of Andean culture
  • Bright markers: Pleiades (Collca), Southern Cross (Chakana), Orion belt
  • Birth chart reading via galactic visibility, heliacal events, and seasonal omens

References:
  Gary Urton (1981) *At the Crossroads of the Earth and Sky*
  Urton & Aveni (1983) *Ethnoastronomy in the Andes*
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .calculator import AndeanChart


def compute_andean_chart(*args, **kwargs) -> "AndeanChart":
    """Lazy-load and call the Andean chart calculator."""
    from .calculator import compute_andean_chart as _fn
    return _fn(*args, **kwargs)


def render_streamlit(*args, **kwargs) -> None:
    """Lazy-load and call the Streamlit renderer."""
    from .renderer import render_streamlit as _fn
    return _fn(*args, **kwargs)


__all__ = ["compute_andean_chart", "render_streamlit"]
