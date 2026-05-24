"""Data loading utilities for KaiYuan Five Planets Divination."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

import requests


PlanetOmenDict = Dict[str, Dict[str, str]]


@dataclass
class KaiyuanDataLoader:
    """Load KaiYuan planetary omen texts from GitHub raw JSON files."""

    base_raw_url: str = "https://raw.githubusercontent.com/kentang2017/kinastro/main/astro/kaiyuan"
    timeout_seconds: int = 20
    session: requests.Session = field(default_factory=requests.Session)

    # Canonical planet name -> possible JSON file names.
    planet_file_candidates: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "歲星": ["歲星.json", "岁星.json", "wood_star.json"],
            "太白": ["太白.json", "gold_star.json"],
            "熒惑": ["熒惑.json", "荧惑.json", "fire_star.json"],
            "填星": ["填星.json", "earth_star.json"],
            "辰星": ["辰星.json", "water_star.json"],
            "月": ["月.json", "moon_28_mansion.json"],
        }
    )

    _cache: PlanetOmenDict = field(default_factory=dict)

    PLANET_ALIASES: Dict[str, str] = field(
        default_factory=lambda: {
            "岁星": "歲星",
            "木星": "歲星",
            "荧惑": "熒惑",
            "火星": "熒惑",
            "金星": "太白",
            "土星": "填星",
            "水星": "辰星",
            "月亮": "月",
            "月球": "月",
        }
    )

    def load_all(self, force_reload: bool = False) -> PlanetOmenDict:
        """Load all planet omen tables into a unified dict: planet -> mansion -> omen_text."""
        if self._cache and not force_reload:
            return self._cache

        merged: PlanetOmenDict = {}
        for planet in self.planet_file_candidates:
            merged[planet] = self.load_planet_data(planet, force_reload=force_reload)

        self._cache = merged
        return merged

    def close(self) -> None:
        """Close underlying HTTP session."""
        self.session.close()

    def __enter__(self) -> "KaiyuanDataLoader":
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        self.close()

    def load_planet_data(self, planet: str, force_reload: bool = False) -> Dict[str, str]:
        """Load one planet's mansion omen map from GitHub raw."""
        canonical = self.normalize_planet_name(planet)
        if canonical in self._cache and self._cache[canonical] and not force_reload:
            return self._cache[canonical]

        last_error: Optional[Exception] = None
        for filename in self.planet_file_candidates.get(canonical, []):
            url = f"{self.base_raw_url}/{filename}"
            try:
                payload = self._fetch_json(url)
                mansion_map = self._extract_mansion_map(payload, canonical)
                if mansion_map:
                    self._cache[canonical] = mansion_map
                    return mansion_map
            except (requests.RequestException, ValueError) as exc:  # pragma: no cover - network/path fallback
                last_error = exc

        raise RuntimeError(
            f"無法載入 {canonical} 的占文資料，候選檔案：{self.planet_file_candidates.get(canonical, [])}"
        ) from last_error

    def query_omen(self, planet: str, mansion: str) -> Optional[str]:
        """Query one omen text by planet and mansion."""
        canonical_planet = self.normalize_planet_name(planet)
        mansion_key = self.normalize_mansion_name(mansion)

        if canonical_planet not in self._cache:
            self.load_planet_data(canonical_planet)

        planet_map = self._cache.get(canonical_planet, {})
        if mansion_key in planet_map:
            return planet_map[mansion_key]
        return planet_map.get(mansion.strip())

    def search(self, keyword: str, planets: Optional[Iterable[str]] = None) -> List[Dict[str, str]]:
        """Keyword search across loaded omen texts."""
        if not keyword:
            return []

        data = self.load_all()
        target_planets = (
            [self.normalize_planet_name(p) for p in planets]
            if planets
            else list(data.keys())
        )

        results: List[Dict[str, str]] = []
        for planet in target_planets:
            for mansion, omen in data.get(planet, {}).items():
                if keyword in omen:
                    results.append(
                        {
                            "planet": planet,
                            "mansion": mansion,
                            "omen": omen,
                        }
                    )
        return results

    def available_planets(self) -> List[str]:
        return list(self.planet_file_candidates.keys())

    def available_mansions(self, planet: str) -> List[str]:
        canonical = self.normalize_planet_name(planet)
        if canonical not in self._cache:
            self.load_planet_data(canonical)
        return list(self._cache.get(canonical, {}).keys())

    def normalize_planet_name(self, planet: str) -> str:
        name = (planet or "").strip()
        return self.PLANET_ALIASES.get(name, name)

    @staticmethod
    def normalize_mansion_name(mansion: str) -> str:
        return (mansion or "").replace("宿", "").strip()

    def _fetch_json(self, url: str) -> dict:
        response = self.session.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.json()

    def _extract_mansion_map(self, payload: dict, canonical_planet: str) -> Dict[str, str]:
        if not isinstance(payload, dict):
            return {}

        if canonical_planet in payload and isinstance(payload[canonical_planet], dict):
            return {self.normalize_mansion_name(k): str(v) for k, v in payload[canonical_planet].items()}

        # fallback: payload may use variant top-level keys.
        for alias, canonical in self.PLANET_ALIASES.items():
            if canonical == canonical_planet and alias in payload and isinstance(payload[alias], dict):
                return {self.normalize_mansion_name(k): str(v) for k, v in payload[alias].items()}

        # fallback: some files may store directly as mansion->text.
        if payload and all(isinstance(v, str) for v in payload.values()):
            return {self.normalize_mansion_name(k): v for k, v in payload.items()}

        return {}
