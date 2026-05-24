"""
astro/celtic/__init__.py — Celtic Tree Calendar package

Implements Robert Graves' 1948 Beth-Luis-Nion tree-alphabet calendar
as described in "The White Goddess: A Historical Grammar of Poetic Myth".

NOTE: This is a modern scholarly reconstruction — not ancient Celtic
tradition.  Graves presented it as a poetic/mythic calendar-alphabet
based on Ogham.  All code and UI copy clearly labels it as such.
"""

from .celtic_tree_graves import (
    CelticTreeChart,
    compute_celtic_tree_chart,
    render_celtic_tree_chart,
    format_celtic_tree_for_prompt,
    TREE_MONTHS,
    DAY_OF_CREATION,
)

__all__ = [
    "CelticTreeChart",
    "compute_celtic_tree_chart",
    "render_celtic_tree_chart",
    "format_celtic_tree_for_prompt",
    "TREE_MONTHS",
    "DAY_OF_CREATION",
]
