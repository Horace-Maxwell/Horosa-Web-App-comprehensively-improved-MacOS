"""
astro/andean/constants.py — Constants for the Andean Astrology module
====================================================================

Includes:
  • MAYU_SAMPLE_POINTS   — galactic (l, b) pairs that outline the visible Milky Way
    (used for background rendering; coarse but sufficient for a sky-map display)
  • ANDEAN_ANIMALS_WHEEL — simplified 12-window seasonal animal guardians derived from
    sun's galactic position; a rough analogue to a zodiac for "birth season" reading
  • GUARDIAN_THRESHOLD   — altitude (degrees) above which a constellation is "alive"
  • HELIACAL_ARC         — elongation from Sun (degrees) required for heliacal rising

The Mayu sample points below follow the orientation used at Cusco (lat ≈ −13.5°):
the "head" of the llama lies toward the Scorpius-Centaurus region, and the river
flows through Sagittarius, Aquila, and Cygnus.
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# Astronomy thresholds
# ─────────────────────────────────────────────────────────────────────────────

# Altitude above horizon (degrees) for a constellation to be considered visible
HORIZON_ALT_DEG: float = 5.0

# Elongation from Sun (degrees) for heliacal rising visibility
HELIACAL_ARC_DEG: float = 12.0

# Maximum absolute galactic latitude (degrees) used when filtering Milky Way points
MAYU_LAT_MAX_DEG: float = 20.0

# ─────────────────────────────────────────────────────────────────────────────
# Mayu (Milky Way) spine sample points — galactic coords (l, b)
# Used to draw the Milky Way band in the chart renderer.
# Sampled every ~5° along the galactic equator plane l=0→360 at b≈0.
# ─────────────────────────────────────────────────────────────────────────────

MAYU_SPINE_L: list[float] = list(range(0, 361, 5))
MAYU_SPINE_B: list[float] = [0.0] * len(MAYU_SPINE_L)

# Broader band — two offset strips to give the appearance of width
MAYU_BAND_OFFSETS: list[float] = [-4.0, -2.0, 0.0, 2.0, 4.0]

# ─────────────────────────────────────────────────────────────────────────────
# Seasonal Animal Guardians (Simplified Andean "Zodiac")
# Maps calendar months 1–12 to primary Andean animal spirit guardians.
# Based on approximate heliacal / zenith passages at Cusco.
# ─────────────────────────────────────────────────────────────────────────────

MONTHLY_GUARDIAN: dict[int, dict[str, str]] = {
    1:  {"qu": "Atoq",      "zh": "狐狸",       "en": "Fox"},
    2:  {"qu": "Atoq",      "zh": "狐狸",       "en": "Fox"},
    3:  {"qu": "Lluthu",    "zh": "山鶉",       "en": "Partridge"},
    4:  {"qu": "Kuntur",    "zh": "兀鷹",       "en": "Condor"},
    5:  {"qu": "Kuntur",    "zh": "兀鷹",       "en": "Condor"},
    6:  {"qu": "Michiq",    "zh": "牧羊人",     "en": "Shepherd"},
    7:  {"qu": "Michiq",    "zh": "牧羊人",     "en": "Shepherd"},
    8:  {"qu": "Qatachillay","zh": "母駱馬",    "en": "Llama"},
    9:  {"qu": "Qatachillay","zh": "母駱馬",    "en": "Llama"},
    10: {"qu": "Hamp'atu",  "zh": "蟾蜍",       "en": "Toad"},
    11: {"qu": "Hamp'atu",  "zh": "蟾蜍",       "en": "Toad"},
    12: {"qu": "Mach'aqway","zh": "蛇",         "en": "Serpent"},
}

# ─────────────────────────────────────────────────────────────────────────────
# Andean historical persons (birth data for the "famous charts" sub-tab)
# ─────────────────────────────────────────────────────────────────────────────

HISTORICAL_PERSONS: list[dict] = [
    {
        "name": "Pachacuti Inca Yupanqui",
        "name_zh": "帕恰庫提·印卡·尤潘基",
        "year": 1418, "month": 8, "day": 1,
        "hour": 6, "minute": 0,
        "timezone": -5.0,
        "latitude": -13.5167, "longitude": -71.9788,
        "location_name": "Cusco, Peru",
        "note_zh": "第九代薩帕印卡，Machu Picchu 建造者，Tahuantinsuyu 帝國奠基者。出生日期為估算。",
        "note_en": "9th Sapa Inca, builder of Machu Picchu, founder of Tahuantinsuyu. Birth date is estimated.",
    },
    {
        "name": "Atahualpa",
        "name_zh": "阿塔瓦爾帕",
        "year": 1497, "month": 1, "day": 1,
        "hour": 6, "minute": 0,
        "timezone": -5.0,
        "latitude": 0.3516, "longitude": -78.1228,
        "location_name": "Quito (Tomebamba), Ecuador",
        "note_zh": "最後一位薩帕印卡，1532 年被西班牙征服者俘虜。出生日期為估算。",
        "note_en": "Last Sapa Inca, captured by Spanish conquistadors in 1532. Birth date is estimated.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Theme colours (used by renderer)
# ─────────────────────────────────────────────────────────────────────────────

ANDEAN_THEME: dict[str, str] = {
    "bg":        "#0B0F1E",   # deep night sky
    "bg_card":   "#131A2E",   # card background
    "gold":      "#C8A24A",   # Inca gold
    "ochre":     "#A65A2A",   # earth ochre (赭紅)
    "green":     "#2F5D3A",   # deep Andean green
    "milky":     "#BFD3FF",   # Milky Way light blue-white
    "border":    "#C8A24A",
    "header":    "#EDD88A",
    "text":      "#E8E2D0",
    "alive":     "#FFD700",   # "alive" constellation highlight
    "dormant":   "#5A5A7A",   # below-horizon colour
    "sun":       "#FFA500",
    "moon":      "#D4E8FF",
}
