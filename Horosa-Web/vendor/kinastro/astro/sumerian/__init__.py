"""
astro/sumerian — Sumerian / Mesopotamian Astrology

Ancient Mesopotamian astrology module implementing:
- MUL.APIN star catalogue & heliacal rising stars
- 12 Akkadian zodiac signs (MUL.APIN tradition)
- Seven planetary deities (Enūma Anu Enlil standard)
- Three sky paths: Path of Enlil / Anu / Ea
- K.8538 Nineveh planisphere 8-sector visualization
- Enūma Anu Enlil omen interpretation engine (30+ rules)
- Venus morning/evening star classification

Sources:
- Hunger & Pingree, "MUL.APIN: An Astronomical Compendium in Cuneiform" (1989)
- Koch-Westenholz, "Mesopotamian Astrology" (1995)
- Rochberg, "The Heavenly Writing" (2004)
"""

from .calculator import compute_sumerian_chart, MesopotamianChart


def _lazy_renderer():
    from .renderer import render_streamlit
    return render_streamlit


__all__ = ["compute_sumerian_chart", "MesopotamianChart"]
