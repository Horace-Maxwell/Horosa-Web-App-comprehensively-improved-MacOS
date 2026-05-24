"""Burmese Mahabote phase-1 module."""

from .mahabote import (
    BurmeseMahaboteChart,
    HousePlacement,
    MAHABOTE_HOUSES,
    SYMBOLS_8,
    birth_weekday_info,
    compute_burmese_mahabote,
    gregorian_to_myanmar_year,
)


def _get_renderer():
    from .renderer import render_mahabote_basic

    return render_mahabote_basic


def render_mahabote_basic(*args, **kwargs):
    return _get_renderer()(*args, **kwargs)


__all__ = [
    "BurmeseMahaboteChart",
    "HousePlacement",
    "MAHABOTE_HOUSES",
    "SYMBOLS_8",
    "birth_weekday_info",
    "compute_burmese_mahabote",
    "gregorian_to_myanmar_year",
    "render_mahabote_basic",
]
