"""金融占星資料載入器（JSON + 快取 + fallback）。"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

_DATA_DIR = Path(__file__).resolve().parent / "data"
_HISTORICAL_EVENTS_FILE = _DATA_DIR / "historical_events.json"
_GREAT_CONJUNCTIONS_FILE = _DATA_DIR / "great_conjunctions.json"


_DEFAULT_HISTORICAL_EVENTS: list[dict] = [
    {
        "year": 1929,
        "month": 10,
        "day": 24,
        "label_zh": "1929 大蕭條（黑色星期四）",
        "label_en": "1929 Great Depression (Black Thursday)",
        "jup_lon_approx": 60.0,
        "sat_lon_approx": 240.0,
        "note_zh": "木土呈120度，但景氣後期泡沫破裂",
        "note_en": "Jupiter-Saturn trine, but late-cycle bubble burst",
        "market_impact": "crash",
    }
]

_DEFAULT_GREAT_CONJUNCTIONS: list[dict] = [
    {
        "year": 2020,
        "month": 12,
        "day": 21,
        "lon": 300.1,
        "sign": "水瓶/Aquarius",
        "note_zh": "風象時代新週期",
        "note_en": "Air Age New Cycle",
    }
]


def _load_json(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, list):
        raise ValueError(f"Invalid JSON schema in {path}: expected list, got {type(payload).__name__}")
    rows = [x for x in payload if isinstance(x, dict)]
    if not rows:
        raise ValueError(f"No valid dict rows in {path}")
    return rows


def _validate_fields(rows: list[dict], required_fields: set[str]) -> list[dict]:
    valid_rows = []
    for row in rows:
        if required_fields.issubset(set(row.keys())):
            valid_rows.append(row)
    if not valid_rows:
        raise ValueError("No row satisfies required fields")
    return valid_rows


@st.cache_data(ttl=3600, show_spinner=False)
def load_historical_events() -> list[dict]:
    """載入歷史金融事件資料。"""
    required = {
        "year",
        "month",
        "day",
        "label_zh",
        "label_en",
        "jup_lon_approx",
        "sat_lon_approx",
        "note_zh",
        "note_en",
        "market_impact",
    }
    try:
        rows = _load_json(_HISTORICAL_EVENTS_FILE)
        rows = _validate_fields(rows, required)
        return sorted(rows, key=lambda x: (int(x["year"]), int(x["month"]), int(x["day"])))
    except Exception:
        return _DEFAULT_HISTORICAL_EVENTS


@st.cache_data(ttl=3600, show_spinner=False)
def load_great_conjunctions() -> list[dict]:
    """載入木土大合相資料。"""
    required = {"year", "month", "day", "lon", "sign", "note_zh", "note_en"}
    try:
        rows = _load_json(_GREAT_CONJUNCTIONS_FILE)
        rows = _validate_fields(rows, required)
        return sorted(rows, key=lambda x: (int(x["year"]), int(x["month"]), int(x["day"])))
    except Exception:
        return _DEFAULT_GREAT_CONJUNCTIONS
