"""
astro/byzantine_astrology — 拜占庭占星 / Byzantine Astrology

Byzantine Astrology module covering the 4th–15th century Eastern Roman Empire
tradition, bridging Hellenistic and Arabic astrology with unique innovations:

- Political horoscopes (emperors, cities, religions)
- Christian-astrological syncretism
- Seismologia, Selenodromia, Vrontologia omen tables
- Key figures: Rhetorius, Hephaestion of Thebes, Paulus Alexandrinus,
  Theophilus of Edessa, John Abramius

Primary Sources:
- Catalogus Codicum Astrologorum Graecorum (CCAG)
- Rhetorius of Egypt, "Compendium" (ca. 6th c.)
- Hephaestion of Thebes, "Apotelesmatika" (ca. 415 CE)
- Paulus Alexandrinus, "Eisagogika" (378 CE)
- Theophilus of Edessa, "Apotelesmatics" (ca. 8th c.)
- John Abramius (11th c. Constantinople)
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .calculator import ByzantineChart


def compute_byzantine_chart(*args, **kwargs):  # type: ignore[override]
    """Lazy-load and call the Byzantine chart calculator."""
    from .calculator import compute_byzantine_chart as _fn
    return _fn(*args, **kwargs)


def render_streamlit(*args, **kwargs):  # type: ignore[override]
    """Lazy-load and call the Streamlit renderer."""
    from .renderer import render_streamlit as _fn
    return _fn(*args, **kwargs)


__all__ = ["compute_byzantine_chart", "render_streamlit"]
