"""
astro/harmonic — Harmonic Astrology (John Addey tradition)

Implements the complete Harmonic Astrology system as described in:
  - John Addey, "Harmonics in Astrology" (1976, L.N. Fowler & Co.)
  - David Hamblin, "Harmonic Charts" (1983, Aquarian Press)

Core principle (Addey, 1976, Chapter 2):
  The Nth Harmonic Chart is obtained by multiplying all planetary longitudes
  by N (mod 360°).  Conjunctions in the result correspond to natal aspects
  of 360°/N (and their multiples).

Public API:
    compute_harmonic_chart    — single harmonic chart
    compute_multi_harmonic    — multiple harmonics simultaneously
    render_harmonic           — Streamlit renderer
    render_harmonic_chart_svg — SVG mandala (standalone)
"""

from .calculator import compute_harmonic_chart, compute_multi_harmonic, HarmonicChart, MultiHarmonicResult
from .renderer import render_harmonic, render_harmonic_chart_svg

__all__ = [
    "compute_harmonic_chart",
    "compute_multi_harmonic",
    "HarmonicChart",
    "MultiHarmonicResult",
    "render_harmonic",
    "render_harmonic_chart_svg",
]
