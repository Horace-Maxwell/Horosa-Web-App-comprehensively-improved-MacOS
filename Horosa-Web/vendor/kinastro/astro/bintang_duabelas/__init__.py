"""KinAstro Bintang Duabelas public API."""

from __future__ import annotations

from .abjad import AbjadCalculator
from .azimat import AzimatGenerator
from .core import BintangDuabelas, BintangDuabelasEngine, BintangDuabelasRequest
from .hisab import HisabNama
from .hours import PlanetaryHours
from .houses import TwelveHouses
from .normalization import NameNormalization, normalize_name, roman_to_jawi
from .yearly import YearlyFortune


def render_streamlit(*args, **kwargs) -> None:
    """Lazy-load and call the Streamlit renderer."""
    from .renderer import render_streamlit as _fn

    return _fn(*args, **kwargs)

__all__ = [
    "AbjadCalculator",
    "AzimatGenerator",
    "BintangDuabelas",
    "BintangDuabelasEngine",
    "BintangDuabelasRequest",
    "HisabNama",
    "NameNormalization",
    "PlanetaryHours",
    "TwelveHouses",
    "YearlyFortune",
    "normalize_name",
    "roman_to_jawi",
    "render_streamlit",
]
