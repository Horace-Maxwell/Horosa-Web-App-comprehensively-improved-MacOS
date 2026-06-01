"""
astro/picatrix_behenian — Picatrix + Behenian 15 Fixed Stars Magic Module

Implements Agrippa / Hermes Trismegistus correspondences for the fifteen
Behenian stars as described in Heinrich Cornelius Agrippa's *Three Books of
Occult Philosophy* (De Occulta Philosophia, 1531) and ultimately derived from
the *Ghayat al-Hakim* (Picatrix, 10th–11th c. CE).

Exports
-------
BEHENIAN_STARS      : list[BehenianStar]
detect_activations  : detect planet–star conjunctions within the magic orb
compute_today_magic : find which Behenian stars are active right now
render_streamlit    : Streamlit page renderer
"""

from .constants import BEHENIAN_STARS, BehenianStar
from .calculator import (
    BehenianActivation,
    detect_activations,
    compute_today_magic,
    find_electional_windows,
)
from .renderer import render_streamlit

__all__ = [
    "BEHENIAN_STARS",
    "BehenianStar",
    "BehenianActivation",
    "detect_activations",
    "compute_today_magic",
    "find_electional_windows",
    "render_streamlit",
]
