# -*- coding: utf-8 -*-
"""
Utility for loading and querying Chinese historical dynasty / ruler data.

The data originates from ``history.pkl`` which encodes a comma-separated
string of records.  Each record has seven fields::

    start_year, duration, field3, dynasty, title, name, era

The module exposes two helpers used by the Streamlit front-end:

* :func:`load_history` – parse the raw pickle into a list of dicts.
* :func:`history_for_year` – return all dynasty/ruler records covering a
  given year.
"""

from __future__ import annotations

import os
import pickle
from typing import Any, Dict, List

_BASE: str = os.path.abspath(os.path.dirname(__file__))
_HISTORY_PATH: str = os.path.join(_BASE, "data", "history.pkl")


def load_history() -> List[Dict[str, Any]]:
    """Parse *history.pkl* into a list of record dicts.

    Each dict contains:
        * ``start_year`` (int) – first year of the reign/era
        * ``duration``   (int) – how many years it lasted
        * ``dynasty``    (str) – dynasty name (e.g. 唐, 宋)
        * ``title``      (str) – ruler title
        * ``name``       (str) – personal name (may be empty)
        * ``era``        (str) – era / reign name
    """
    with open(_HISTORY_PATH, "rb") as fh:
        raw: str = pickle.load(fh)

    fields = raw.split(",")
    records: List[Dict[str, Any]] = []
    for i in range(0, len(fields), 7):
        if i + 6 >= len(fields):
            break
        records.append(
            {
                "start_year": int(fields[i]),
                "duration": int(fields[i + 1]),
                "dynasty": fields[i + 3],
                "title": fields[i + 4],
                "name": fields[i + 5],
                "era": fields[i + 6],
            }
        )
    return records


def history_for_year(year: int) -> List[Dict[str, Any]]:
    """Return every record whose reign/era covers *year*."""
    records = load_history()
    return [
        r
        for r in records
        if r["start_year"] <= year < r["start_year"] + r["duration"]
    ]
