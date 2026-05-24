# Contributing to Kin Astro (堅占星)

Thank you for your interest in contributing! This guide explains how to add new astrology systems, write tests, and follow our conventions.

## Project Structure

```
kinastro/
├── app.py                    # Main Streamlit app (tab routing)
├── requirements.txt          # Python dependencies
├── astro/                    # Computation & rendering modules
│   ├── i18n.py               # Translation keys (zh/en)
│   ├── chart_theme.py        # Unified colour theme
│   ├── calculator.py         # Chinese (七政四餘) chart engine
│   ├── western.py            # Western astrology
│   ├── indian.py             # Vedic (Jyotish) astrology
│   ├── hellenistic.py        # Hellenistic astrology
│   ├── ...                   # Other systems
│   └── data/                 # JSON data files
└── tests/
    ├── test_calculator.py    # Chinese calculator tests
    ├── test_new_astrology.py # Multi-system tests
    └── test_advanced_features.py  # Advanced feature tests
```

## Adding a New Astrology System

Follow these 5 steps:

### 1. Create the computation module

Create `astro/new_system.py` with:

```python
"""
astro/new_system.py — Description
"""
from dataclasses import dataclass, field

@dataclass
class NewSystemChart:
    year: int
    month: int
    # ... fields ...

def compute_new_system_chart(year, month, day, hour, minute,
                             timezone, latitude, longitude,
                             location_name=""):
    """Compute chart. Use same parameter signature as other systems."""
    # ... computation ...
    return NewSystemChart(...)

def render_new_system_chart(chart):
    """Render in Streamlit."""
    import streamlit as st
    # ... rendering ...
```

### 2. Add translation keys

In `astro/i18n.py`, add entries to `TRANSLATIONS`:

```python
"tab_new_system": {"zh": "新體系", "en": "New System"},
"desc_new_system": {"zh": "描述...", "en": "Description..."},
"spinner_new_system": {"zh": "計算中...", "en": "Computing..."},
```

### 3. Wire into app.py

- Import: `from astro.new_system import compute_new_system_chart, render_new_system_chart`
- Add tab name to `st.tabs()` line
- Add tab content in both `if calculate:` and `else:` blocks

### 4. Write tests

Create `tests/test_new_system.py` or add a class to existing test file:

```python
class TestNewSystem(unittest.TestCase):
    def test_compute_returns_chart(self):
        chart = compute_new_system_chart(...)
        self.assertIsInstance(chart, NewSystemChart)
```

### 5. Run tests

```bash
python -m pytest tests/ -v --tb=short
```

## Conventions

### Naming
- Modules: `astro/<system_name>.py` (lowercase, underscores)
- Dataclasses: `PascalCase` (e.g., `WesternChart`, `VedicPlanet`)
- Compute functions: `compute_<system>_chart()`
- Render functions: `render_<system>_chart()`

### Dataclasses
- Use `@dataclass` for all structured data
- Include type hints
- Use `field(default_factory=list)` for mutable defaults

### i18n
- Every user-visible string goes through `t("key")`
- Always provide both `zh` and `en` translations

### Dependencies
- Swiss Ephemeris: `import swisseph as swe`
- Streamlit imports only in render functions, not at module level
- Add new dependencies to `requirements.txt`

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Questions?

Open an issue on GitHub.
