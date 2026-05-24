"""
astro/fixed_stars.py — 固定星模組 (Fixed Stars)

Computes positions of classical fixed stars and finds conjunctions with planets.
The star catalogue is stored in data/fixed_stars.json (100+ entries).
"""
import json
import os
from functools import lru_cache
import swisseph as swe
from dataclasses import dataclass, field

ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Sentinel value meaning "all stars in the catalogue".
# Must be kept in sync with the length of data/fixed_stars.json.
STAR_CATALOG_ALL = -1

_DATA_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "data")


@lru_cache(maxsize=1)
def load_star_catalog() -> list[dict]:
    """Load fixed star catalogue from JSON (cached)."""
    path = os.path.join(_DATA_DIR, "fixed_stars.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class FixedStarPosition:
    name: str
    swe_name: str          # Swiss Ephemeris lookup name
    longitude: float
    latitude: float
    magnitude: float
    nature: str
    meaning_en: str
    meaning_cn: str
    cn_name: str           # Traditional Chinese star name
    constellation: str
    sign: str
    sign_degree: float


@dataclass
class StarConjunction:
    star_name: str
    star_cn: str
    star_longitude: float
    planet_name: str
    planet_longitude: float
    orb: float
    nature: str
    meaning_en: str
    meaning_cn: str


def compute_fixed_star_positions(jd: float, limit: int | None = None) -> list[FixedStarPosition]:
    """Compute ecliptic positions of catalogued fixed stars.

    Parameters
    ----------
    jd:
        Julian Day (UT).
    limit:
        Maximum number of stars to compute.  None means all.

    Returns
    -------
    List of FixedStarPosition sorted by ecliptic longitude.
    """
    catalog = load_star_catalog()
    if limit is not None:
        catalog = catalog[:limit]

    results: list[FixedStarPosition] = []
    for star in catalog:
        swe_name = star.get("swe_name", star["name"])
        try:
            _name_out, xx = swe.fixstar_ut(swe_name, jd)
            lon, lat = float(xx[0]), float(xx[1])
            idx = int(lon / 30) % 12
            results.append(FixedStarPosition(
                name=star["name"],
                swe_name=swe_name,
                longitude=lon,
                latitude=lat,
                magnitude=star.get("magnitude", 99.0),
                nature=star.get("nature", ""),
                meaning_en=star.get("meaning_en", ""),
                meaning_cn=star.get("meaning_cn", ""),
                cn_name=star.get("cn_name", star["name"]),
                constellation=star.get("constellation", ""),
                sign=ZODIAC_SIGNS[idx],
                sign_degree=round(lon % 30, 4),
            ))
        except Exception:
            pass
    results.sort(key=lambda s: s.longitude)
    return results


def find_conjunctions(
    stars: list[FixedStarPosition],
    planet_positions: dict[str, float],
    orb: float = 1.5,
) -> list[StarConjunction]:
    """Find fixed stars within *orb* degrees of any planet.

    Parameters
    ----------
    stars:
        Output of ``compute_fixed_star_positions()``.
    planet_positions:
        Dict of {planet_name: ecliptic_longitude}.
    orb:
        Conjunction orb in degrees (default 1.5°).
    """
    results: list[StarConjunction] = []
    for star in stars:
        for p_name, p_lon in planet_positions.items():
            diff = abs(star.longitude - p_lon) % 360.0
            actual_orb = min(diff, 360.0 - diff)
            if actual_orb <= orb:
                results.append(StarConjunction(
                    star_name=star.name,
                    star_cn=star.cn_name,
                    star_longitude=star.longitude,
                    planet_name=p_name,
                    planet_longitude=p_lon,
                    orb=round(actual_orb, 4),
                    nature=star.nature,
                    meaning_en=star.meaning_en,
                    meaning_cn=star.meaning_cn,
                ))
    results.sort(key=lambda c: c.orb)
    return results
