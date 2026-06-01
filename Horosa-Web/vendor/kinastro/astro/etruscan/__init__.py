"""
astro/etruscan — Etruscan Astrology Module for KinAstro
========================================================

Implements the Etruscan divination framework centred on:
  • Templum — the sacred 16-region sky/liver division used by haruspices
  • Piacenza Liver — the bronze votive model dividing space into 16 named regions
  • Lightning divination (fulguratores) — interpreting Tinia's 9 types of thunderbolts
  • Haruspicy — reading planetary positions across the 16 celestial Templa

The Etruscan cosmological model divides the horizon circle into 16 sectors (22.5° each),
each governed by a specific deity. Planet positions are mapped to these sectors to
determine auspicious/inauspicious influences.

References:
  Pallottino (1975) *The Etruscans*
  van der Meer (1987) *The Bronze Liver of Piacenza*
  Turfa (2012) *Divining the Etruscan World*
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .calculator import EtruscanChart


def compute_etruscan_chart(*args, **kwargs) -> "EtruscanChart":
    """Lazy-load and call the Etruscan chart calculator."""
    from .calculator import compute_etruscan_chart as _fn
    return _fn(*args, **kwargs)


def render_streamlit(*args, **kwargs) -> None:
    """Lazy-load and call the Streamlit renderer."""
    from .renderer import render_streamlit as _fn
    return _fn(*args, **kwargs)


__all__ = ["compute_etruscan_chart", "render_streamlit"]
