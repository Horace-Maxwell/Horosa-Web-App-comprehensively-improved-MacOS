"""
astro/amazigh/amazigh.py — Amazigh (Berber) astrology phase-1 core.

Phase 1 scope:
1. Core data structures and compute helpers
2. Fixed star + planetary Lots rule loading from JSON tables
3. Basic SVG sky/compass rendering

Note:
This module provides a modern interpretation informed by traditional knowledge.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, TypedDict

import swisseph as swe


DATA_DIR = Path(__file__).resolve().parent / "data"

_PLANET_IDS: Dict[str, int] = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
}

_ZODIAC_SIGNS = [
    ("Aries", "牡羊座"),
    ("Taurus", "金牛座"),
    ("Gemini", "雙子座"),
    ("Cancer", "巨蟹座"),
    ("Leo", "獅子座"),
    ("Virgo", "處女座"),
    ("Libra", "天秤座"),
    ("Scorpio", "天蠍座"),
    ("Sagittarius", "射手座"),
    ("Capricorn", "摩羯座"),
    ("Aquarius", "水瓶座"),
    ("Pisces", "雙魚座"),
]

class DirectionSector(TypedDict):
    key: str
    name_en: str
    name_zh: str
    az_start: float
    az_end: float
    season_en: str
    season_zh: str


_DIRECTION_SECTORS: List[DirectionSector] = [
    {"key": "N", "name_en": "North", "name_zh": "北方", "az_start": 337.5, "az_end": 22.5, "season_en": "Winter", "season_zh": "冬季"},
    {"key": "NE", "name_en": "Northeast", "name_zh": "東北", "az_start": 22.5, "az_end": 67.5, "season_en": "Spring", "season_zh": "春季"},
    {"key": "E", "name_en": "East", "name_zh": "東方", "az_start": 67.5, "az_end": 112.5, "season_en": "Spring", "season_zh": "春季"},
    {"key": "SE", "name_en": "Southeast", "name_zh": "東南", "az_start": 112.5, "az_end": 157.5, "season_en": "Summer", "season_zh": "夏季"},
    {"key": "S", "name_en": "South", "name_zh": "南方", "az_start": 157.5, "az_end": 202.5, "season_en": "Summer", "season_zh": "夏季"},
    {"key": "SW", "name_en": "Southwest", "name_zh": "西南", "az_start": 202.5, "az_end": 247.5, "season_en": "Autumn", "season_zh": "秋季"},
    {"key": "W", "name_en": "West", "name_zh": "西方", "az_start": 247.5, "az_end": 292.5, "season_en": "Autumn", "season_zh": "秋季"},
    {"key": "NW", "name_en": "Northwest", "name_zh": "西北", "az_start": 292.5, "az_end": 337.5, "season_en": "Winter", "season_zh": "冬季"},
]

_SVG_BG_INNER = "#162238"
_SVG_BG_OUTER = "#0b1220"
_SVG_BORDER = "#7FA2C8"
_SVG_CARDINAL = "#D8E6F4"
_SVG_STAR = "#F5D38B"
_SVG_LOT = "#7BC8A4"
_SVG_CENTER_FILL = "#101a2d"
_SVG_CENTER_STROKE = "#8CAFD0"
_SVG_CENTER_TEXT = "#E8EEF7"
_SVG_CENTER_SUBTEXT = "#A6C3E0"
_SVG_SECTOR_COLORS = ["#203046", "#273754", "#2D3D5B", "#334462"]
_MIN_STAR_RADIUS = 2.0
_STAR_RADIUS_BASE = 5.4
_STAR_MAGNITUDE_CLAMP = 3.5


@dataclass
class AmazighPlanet:
    name_en: str
    name_zh: str
    longitude: float
    speed: float
    retrograde: bool


@dataclass
class AmazighFixedStar:
    key: str
    swe_name: str
    name_en: str
    name_zh: str
    longitude: float
    magnitude: float
    constellation: str
    meaning_en: str
    meaning_zh: str


@dataclass
class AmazighLotRule:
    lot_id: str
    name_en: str
    name_zh: str
    day_formula: Tuple[str, str]
    night_formula: Tuple[str, str]
    meaning_en: str
    meaning_zh: str


@dataclass
class AmazighLot:
    lot_id: str
    name_en: str
    name_zh: str
    longitude: float
    sign_en: str
    sign_zh: str
    degree_in_sign: float
    meaning_en: str
    meaning_zh: str


@dataclass
class AmazighDirection:
    key: str
    name_en: str
    name_zh: str
    season_en: str
    season_zh: str
    azimuth: float


@dataclass
class AmazighChart:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude_birth: float
    location_name: str = ""
    tribal_element: str = ""
    julian_day: float = 0.0
    ascendant: float = 0.0
    is_day_chart: bool = True
    planets: List[AmazighPlanet] = field(default_factory=list)
    fixed_stars: List[AmazighFixedStar] = field(default_factory=list)
    lots: List[AmazighLot] = field(default_factory=list)
    direction: Optional[AmazighDirection] = None
    cultural_note: str = "基於傳統知識的現代詮釋 / Modern interpretation based on traditional knowledge."


def _load_json(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_fixed_star_rules() -> List[Dict]:
    return _load_json(DATA_DIR / "fixed_stars.json")


def load_lot_rules() -> List[AmazighLotRule]:
    raw = _load_json(DATA_DIR / "lots_rules.json")
    rules: List[AmazighLotRule] = []
    for item in raw:
        rules.append(
            AmazighLotRule(
                lot_id=item["id"],
                name_en=item["name_en"],
                name_zh=item["name_zh"],
                day_formula=(item["day_formula"]["add"], item["day_formula"]["subtract"]),
                night_formula=(item["night_formula"]["add"], item["night_formula"]["subtract"]),
                meaning_en=item["meaning_en"],
                meaning_zh=item["meaning_zh"],
            )
        )
    return rules


def _norm(deg: float) -> float:
    return deg % 360.0


def _sign_from_lon(lon: float) -> Tuple[str, str, float]:
    idx = int(_norm(lon) / 30.0) % 12
    return _ZODIAC_SIGNS[idx][0], _ZODIAC_SIGNS[idx][1], _norm(lon) % 30.0


def _is_day_chart(sun_lon: float, asc: float) -> bool:
    return _norm(sun_lon - asc) < 180.0


def _resolve_direction(azimuth: float) -> AmazighDirection:
    azimuth = _norm(azimuth)
    for sec in _DIRECTION_SECTORS:
        start = float(sec["az_start"])
        end = float(sec["az_end"])
        hit = (azimuth >= start or azimuth < end) if start > end else (start <= azimuth < end)
        if hit:
            return AmazighDirection(
                key=str(sec["key"]),
                name_en=str(sec["name_en"]),
                name_zh=str(sec["name_zh"]),
                season_en=str(sec["season_en"]),
                season_zh=str(sec["season_zh"]),
                azimuth=azimuth,
            )
    fallback = _DIRECTION_SECTORS[0]
    return AmazighDirection(
        key=str(fallback["key"]),
        name_en=str(fallback["name_en"]),
        name_zh=str(fallback["name_zh"]),
        season_en=str(fallback["season_en"]),
        season_zh=str(fallback["season_zh"]),
        azimuth=azimuth,
    )


def compute_amazigh_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    direction_azimuth: Optional[float] = None,
    tribal_element: str = "",
) -> AmazighChart:
    """
    Compute a phase-1 Amazigh astrology chart.

    Returns:
        AmazighChart with planets, fixed stars, lots, and direction/season mapping.
    """
    swe.set_ephe_path("")
    ut_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, ut_hour)
    house_cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")
    asc = _norm(ascmc[0])

    planets: List[AmazighPlanet] = []
    lon_map: Dict[str, float] = {}
    for name, pid in _PLANET_IDS.items():
        xx, _ = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_SPEED)
        lon = _norm(float(xx[0]))
        speed = float(xx[3])
        lon_map[name] = lon
        planets.append(
            AmazighPlanet(
                name_en=name,
                name_zh={
                    "Sun": "太陽",
                    "Moon": "月亮",
                    "Mercury": "水星",
                    "Venus": "金星",
                    "Mars": "火星",
                    "Jupiter": "木星",
                    "Saturn": "土星",
                }[name],
                longitude=lon,
                speed=speed,
                retrograde=speed < 0,
            )
        )

    fixed_stars: List[AmazighFixedStar] = []
    for row in load_fixed_star_rules():
        star_lon = float(row.get("fallback_longitude", 0.0))
        try:
            star_xx, _ = swe.fixstar2(str(row["swe_name"]), jd, swe.FLG_SWIEPH)
            star_lon = _norm(float(star_xx[0]))
        except Exception:
            star_lon = _norm(star_lon)
        fixed_stars.append(
            AmazighFixedStar(
                key=row["key"],
                swe_name=row["swe_name"],
                name_en=row["name_en"],
                name_zh=row["name_zh"],
                longitude=star_lon,
                magnitude=float(row["magnitude"]),
                constellation=row["constellation"],
                meaning_en=row["meaning_en"],
                meaning_zh=row["meaning_zh"],
            )
        )

    is_day = _is_day_chart(lon_map["Sun"], asc)
    lots: List[AmazighLot] = []
    for rule in load_lot_rules():
        add_key, sub_key = rule.day_formula if is_day else rule.night_formula
        if add_key not in lon_map or sub_key not in lon_map:
            continue
        lot_lon = _norm(asc + lon_map[add_key] - lon_map[sub_key])
        sign_en, sign_zh, deg_in_sign = _sign_from_lon(lot_lon)
        lots.append(
            AmazighLot(
                lot_id=rule.lot_id,
                name_en=rule.name_en,
                name_zh=rule.name_zh,
                longitude=lot_lon,
                sign_en=sign_en,
                sign_zh=sign_zh,
                degree_in_sign=deg_in_sign,
                meaning_en=rule.meaning_en,
                meaning_zh=rule.meaning_zh,
            )
        )

    direction = _resolve_direction(direction_azimuth if direction_azimuth is not None else asc)

    return AmazighChart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude_birth=longitude,
        location_name=location_name,
        tribal_element=tribal_element,
        julian_day=jd,
        ascendant=asc,
        is_day_chart=is_day,
        planets=planets,
        fixed_stars=fixed_stars,
        lots=lots,
        direction=direction,
    )


def render_amazigh_sky_svg(chart: AmazighChart, size: int = 520) -> str:
    """Build a basic Amazigh-inspired sky SVG (phase-1)."""
    cx = cy = size // 2
    r_outer = size // 2 - 18
    r_ring = r_outer * 0.86
    r_star = r_outer * 0.64

    svg: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        "<defs>",
        '<radialGradient id="amazighBg" cx="50%" cy="50%" r="50%">',
        f'<stop offset="0%" stop-color="{_SVG_BG_INNER}" />',
        f'<stop offset="100%" stop-color="{_SVG_BG_OUTER}" />',
        "</radialGradient>",
        '<filter id="glow"><feGaussianBlur stdDeviation="1.6" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        "</defs>",
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="url(#amazighBg)" stroke="{_SVG_BORDER}" stroke-width="1.5"/>',
    ]

    for i in range(8):
        a0 = math.radians(i * 45 - 90)
        a1 = math.radians((i + 1) * 45 - 90)
        x1, y1 = cx + r_ring * math.cos(a0), cy + r_ring * math.sin(a0)
        x2, y2 = cx + r_ring * math.cos(a1), cy + r_ring * math.sin(a1)
        svg.append(
            f'<path d="M {cx} {cy} L {x1:.1f} {y1:.1f} A {r_ring:.1f} {r_ring:.1f} 0 0 1 {x2:.1f} {y2:.1f} Z" '
            f'fill="{_SVG_SECTOR_COLORS[i % len(_SVG_SECTOR_COLORS)]}" fill-opacity="0.22" />'
        )

    for cardinal, deg in [("N", 270), ("E", 0), ("S", 90), ("W", 180)]:
        rad = math.radians(deg)
        tx, ty = cx + (r_outer - 20) * math.cos(rad), cy + (r_outer - 20) * math.sin(rad)
        svg.append(
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" dominant-baseline="middle" fill="{_SVG_CARDINAL}" '
            f'font-size="13" font-weight="700">{cardinal}</text>'
        )

    for star in chart.fixed_stars:
        ang = math.radians(star.longitude - 90.0)
        px, py = cx + r_star * math.cos(ang), cy + r_star * math.sin(ang)
        radius = max(_MIN_STAR_RADIUS, _STAR_RADIUS_BASE - min(star.magnitude, _STAR_MAGNITUDE_CLAMP))
        svg.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{radius:.1f}" fill="{_SVG_STAR}" fill-opacity="0.95" filter="url(#glow)" />'
        )

    for lot in chart.lots[:4]:
        ang = math.radians(lot.longitude - 90.0)
        px, py = cx + (r_star * 0.84) * math.cos(ang), cy + (r_star * 0.84) * math.sin(ang)
        svg.append(f'<rect x="{px-2:.1f}" y="{py-2:.1f}" width="4" height="4" fill="{_SVG_LOT}" />')

    svg.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer*0.22:.1f}" fill="{_SVG_CENTER_FILL}" stroke="{_SVG_CENTER_STROKE}" stroke-width="1.1"/>'
    )
    svg.append(
        f'<text x="{cx}" y="{cy-4}" text-anchor="middle" fill="{_SVG_CENTER_TEXT}" font-size="12">Amazigh Sky</text>'
    )
    if chart.direction:
        svg.append(
            f'<text x="{cx}" y="{cy+12}" text-anchor="middle" fill="{_SVG_CENTER_SUBTEXT}" font-size="10">'
            f'{chart.direction.name_en} · {chart.direction.season_en}</text>'
        )
    svg.append("</svg>")
    return "".join(svg)


def render_amazigh_chart(chart: AmazighChart, after_chart_hook=None) -> None:
    """Render a full Amazigh astrology chart in Streamlit."""
    import streamlit as st

    sect = "☀️ 日盤 (Day Chart)" if chart.is_day_chart else "🌙 夜盤 (Night Chart)"
    st.info(f"**盤型 (Sect)**: {sect}")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**日期 (Date):** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**時間 (Time):** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**時區 (Timezone):** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**地點 (Location):** {chart.location_name or '—'}")
        asc_sign_en, asc_sign_zh, asc_deg = _sign_from_lon(chart.ascendant)
        st.write(f"**上升點 (ASC):** {asc_sign_en} ({asc_sign_zh}) {asc_deg:.2f}°")
        if chart.direction:
            st.write(
                f"**方位 (Direction):** {chart.direction.name_zh} / {chart.direction.name_en}"
                f" · {chart.direction.season_zh} / {chart.direction.season_en}"
            )

    if after_chart_hook:
        after_chart_hook()

    st.divider()

    # ── Planet positions ──────────────────────────────────────
    st.markdown("#### 🪐 七曜位置 (Planet Positions)")
    if chart.planets:
        planet_rows = []
        for p in chart.planets:
            sign_en, sign_zh, deg_in_sign = _sign_from_lon(p.longitude)
            retro = "℞" if p.retrograde else ""
            planet_rows.append({
                "星體 Planet": f"{p.name_zh} / {p.name_en}",
                "星座 Sign": f"{sign_en} ({sign_zh})",
                "度數 Degree": f"{deg_in_sign:.2f}°{retro}",
                "黃道度 Longitude": f"{p.longitude:.2f}°",
            })
        st.dataframe(planet_rows, width="stretch", hide_index=True)

    st.divider()

    # ── Lots (Fortune Points) ─────────────────────────────────
    st.markdown("#### ✦ 命運點 (Lots)")
    if chart.lots:
        lot_rows = []
        for lot in chart.lots:
            lot_rows.append({
                "名稱 Name": f"{lot.name_zh} / {lot.name_en}",
                "星座 Sign": f"{lot.sign_en} ({lot.sign_zh})",
                "度數 Degree": f"{lot.degree_in_sign:.2f}°",
                "含義 Meaning": lot.meaning_zh,
            })
        st.dataframe(lot_rows, width="stretch", hide_index=True)

    st.divider()

    # ── Fixed Stars ───────────────────────────────────────────
    st.markdown("#### ⭐ 固定星 (Fixed Stars)")
    if chart.fixed_stars:
        star_rows = []
        for star in chart.fixed_stars:
            sign_en, sign_zh, deg_in_sign = _sign_from_lon(star.longitude)
            star_rows.append({
                "星名 Star": f"{star.name_zh} / {star.name_en}",
                "星座 Constellation": star.constellation,
                "黃道位置 Position": f"{sign_en} ({sign_zh}) {deg_in_sign:.2f}°",
                "星等 Magnitude": f"{star.magnitude:.2f}",
                "含義 Meaning": star.meaning_zh,
            })
        st.dataframe(star_rows, width="stretch", hide_index=True)

    st.caption(chart.cultural_note)
