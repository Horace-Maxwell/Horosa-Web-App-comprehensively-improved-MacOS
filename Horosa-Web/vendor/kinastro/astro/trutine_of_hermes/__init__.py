"""
astro/trutine_of_hermes — 赫密士出生前世盤（Trutine of Hermes / Prenatal Epoch）

Implements the classical Hellenistic Prenatal Epoch technique attributed to
Hermes Trismegistus and described in Ptolemy's *Centiloquium* (Karpos),
as well as the systematic treatment by E.H. Bailey in
*The Prenatal Epoch* (1916).

Public API:
    compute_epoch_chart   — compute the Prenatal Epoch and Natal charts
    render_streamlit      — Streamlit UI renderer
    PrenatalEpochChart    — result dataclass
    TrutineVariant        — enum of supported calculation variants
"""

from .calculator import (
    compute_epoch_chart,
    PrenatalEpochChart,
    EpochPlanetPosition,
    TrutineVariant,
)
from .renderer import render_streamlit

__all__ = [
    "compute_epoch_chart",
    "PrenatalEpochChart",
    "EpochPlanetPosition",
    "TrutineVariant",
    "render_streamlit",
]
