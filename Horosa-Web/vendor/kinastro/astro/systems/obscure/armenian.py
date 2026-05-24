from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple
import json

import streamlit as st

from astro.swe_init import init_swisseph
from astro.western.western import compute_western_chart
from astro.western.western_transit import compute_western_transits
from astro.western.predictive import compute_secondary_progressions
from astro.western.western_return import compute_solar_return as compute_western_solar_return
from astro.systems.base import BaseChart


_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "armenian"


@st.cache_data(show_spinner=False)
def _load_signs() -> List[Dict[str, Any]]:
    return json.loads((_DATA_DIR / "armenian_signs.json").read_text(encoding="utf-8"))["signs"]


@st.cache_data(show_spinner=False)
def _load_keywords() -> Dict[str, List[str]]:
    return json.loads((_DATA_DIR / "armenian_keywords.json").read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def _load_cultural_sources() -> List[Dict[str, str]]:
    return json.loads((_DATA_DIR / "cultural_sources.json").read_text(encoding="utf-8"))


@dataclass
class ArmenianPlanet:
    name: str
    longitude: float
    sign_en: str
    sign_hy: str
    sign_translit: str
    sign_degree: float
    retrograde: bool
    house: int = 0


@dataclass
class ArmenianChart(BaseChart):
    system: str = "Armenian Astrology"
    zodiac_mode: str = "tropical"
    sidereal: bool = False
    planets: List[ArmenianPlanet] = field(default_factory=list)
    haykian_date: Dict[str, Any] = field(default_factory=dict)
    ancestral_keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def _map_sign(lon: float) -> Tuple[str, str, str, float]:
        signs = _load_signs()
        idx = int(lon // 30) % 12
        s = signs[idx]
        return s["en"], s["hy"], s["translit"], lon % 30.0

    @staticmethod
    def _to_haykian_date(year: int, month: int, day: int, latitude: float) -> Dict[str, Any]:
        # MVP approximation:
        # - Converts Gregorian day-of-year into 30-day blocks (1..13)
        # - Intended for interpretive UI context only, not strict historical chronology
        # - Replace with a full Haykian epoch/overflow-day model in a future revision
        day_of_year = date(year, month, day).timetuple().tm_yday
        hayk_year = year + 551
        hayk_month = ((day_of_year - 1) // 30) + 1
        hayk_day = ((day_of_year - 1) % 30) + 1
        orion_visible = month in (11, 12, 1, 2, 3)
        return {
            "hayk_year": hayk_year,
            "hayk_month": hayk_month,
            "hayk_day": hayk_day,
            "orion_hayk_visible": orion_visible,
            "observer_latitude": latitude,
        }

    @staticmethod
    def _derive_ancestral_keywords(planets: List[ArmenianPlanet]) -> List[str]:
        kw_map = _load_keywords()
        picked: List[str] = []
        luminaries = [p for p in planets if ("Sun" in p.name or "Moon" in p.name)]
        for p in luminaries:
            picked.extend(kw_map.get(p.sign_hy, []))
            if p.house in {1, 4, 7, 10}:
                picked.extend(kw_map.get("angular_house", []))
        if not picked and planets:
            picked.extend(kw_map.get(planets[0].sign_hy, []))
        dedup = []
        for item in picked:
            if item not in dedup:
                dedup.append(item)
        return dedup

    @classmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def compute_natal(
        cls,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        timezone: float,
        latitude: float,
        longitude: float,
        location_name: str = "",
        sidereal: bool = False,
    ) -> "ArmenianChart":
        init_swisseph()
        base = compute_western_chart(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            sidereal=sidereal,
        )

        planets: List[ArmenianPlanet] = []
        for p in base.planets:
            en, hy, tr, deg = cls._map_sign(float(p.longitude))
            planets.append(
                ArmenianPlanet(
                    name=p.name,
                    longitude=float(p.longitude),
                    sign_en=en,
                    sign_hy=hy,
                    sign_translit=tr,
                    sign_degree=deg,
                    retrograde=bool(getattr(p, "retrograde", False)),
                    house=int(getattr(p, "house", 0) or 0),
                )
            )

        return cls(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            julian_day=float(base.julian_day),
            planets=planets,
            haykian_date=cls._to_haykian_date(year, month, day, latitude),
            ancestral_keywords=cls._derive_ancestral_keywords(planets),
            sidereal=sidereal,
            zodiac_mode="sidereal" if sidereal else "tropical",
            metadata={
                "source_engine": "swisseph + western core remap",
                "cultural_sources": _load_cultural_sources(),
                "ai_prompt": {
                    "system": (
                        "You are an Armenian astrology reader. Use Armenian cultural framing only "
                        "(Hayk, Armenian Highlands, manuscript cosmology, Arevakhach symbolism). "
                        "Do not default to standard Western symbol language. Mention computation "
                        "basis as tropical/sidereal only when needed."
                    ),
                    "instructions": (
                        "Return sections in order: Armenian Natal Reading, Transit/Progression/Solar Return, "
                        "Cultural Context Notes, Cross-system comparison with Zi Wei and Hellenistic. "
                        "Include uncertainty labels when historical evidence is sparse."
                    ),
                },
            },
        )

    @staticmethod
    @st.cache_data(ttl=1800, show_spinner=False)
    def compute_transit(
        natal_chart: "ArmenianChart",
        year: int,
        month: int,
        day: int,
        hour: int = 12,
        minute: int = 0,
        timezone: float = 0.0,
    ) -> Dict[str, Any]:
        return compute_western_transits(
            natal_chart=natal_chart,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
        ).__dict__

    @staticmethod
    @st.cache_data(ttl=1800, show_spinner=False)
    def compute_progression(
        natal_chart: "ArmenianChart",
        target_age: float,
    ) -> Dict[str, Any]:
        natal_lons = {p.name: p.longitude for p in natal_chart.planets}
        return compute_secondary_progressions(
            birth_jd=natal_chart.julian_day,
            target_age=target_age,
            latitude=natal_chart.latitude,
            longitude=natal_chart.longitude,
            natal_planets=natal_lons,
            sidereal=natal_chart.sidereal,
        ).__dict__

    @staticmethod
    @st.cache_data(ttl=1800, show_spinner=False)
    def compute_solar_return(
        natal_chart: "ArmenianChart",
        target_year: int,
    ) -> Dict[str, Any]:
        natal_sun = next((p for p in natal_chart.planets if "Sun" in p.name), None)
        natal_sun_lon = natal_sun.longitude if natal_sun else 0.0
        return compute_western_solar_return(
            natal_sun_lon=natal_sun_lon,
            target_year=target_year,
            latitude=natal_chart.latitude,
            longitude=natal_chart.longitude,
            timezone=natal_chart.timezone,
            location_name=natal_chart.location_name,
        ).__dict__


def compute_armenian_chart(*args, **kwargs) -> ArmenianChart:
    return ArmenianChart.compute_natal(*args, **kwargs)


def render_streamlit(chart: ArmenianChart, after_chart_hook=None) -> None:
    from frontend.armenian_renderer import render_armenian_page

    render_armenian_page(chart, after_chart_hook=after_chart_hook)
