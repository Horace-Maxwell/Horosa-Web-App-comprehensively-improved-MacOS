"""
astro/western/advanced_bodies.py — 進階天體技法
(Advanced Celestial Techniques)

Provides:
  - calculate_parans()   : Paranatellonta — stars & planets sharing the
                            same horizon / meridian circle simultaneously.
  - calculate_heliacal() : Heliacal rising / setting for planets & fixed
                            stars via Swiss Ephemeris heliacal_ut().
  - get_asteroid_aspects(): Aspects between asteroids and traditional planets.

All functions accept a Julian Day (UT) and observer latitude / longitude.
"""

from __future__ import annotations

import math
import logging
from dataclasses import dataclass, field

import swisseph as swe

logger = logging.getLogger(__name__)

# ── Traditional western planets used for parans / aspects ──────────────────
_TRAD_PLANETS = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
    "Uranus":  swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto":   swe.PLUTO,
    "ASC":     None,   # synthetic — handled separately
    "MC":      None,   # synthetic — handled separately
}

# ── Paran event labels ───────────────────────────────────────────────────────
PARAN_EVENTS = {
    "rising":          {"en": "Rising",         "cn": "上升"},
    "culminating":     {"en": "Culminating",    "cn": "中天"},
    "setting":         {"en": "Setting",        "cn": "下降"},
    "anti_culminating":{"en": "Anti-Culm.",     "cn": "天底"},
}

# ── Heliacal event type names ────────────────────────────────────────────────
HELIACAL_EVENTS = {
    swe.HELIACAL_RISING:        {"en": "Heliacal Rising",       "cn": "偕日升"},
    swe.HELIACAL_SETTING:       {"en": "Heliacal Setting",      "cn": "偕日沒"},
    swe.EVENING_FIRST:          {"en": "Evening First",         "cn": "黃昏初見"},
    swe.MORNING_LAST:           {"en": "Morning Last",          "cn": "晨光最後"},
}


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class ParanResult:
    """One paran event between a fixed star and a planet / angle."""
    star_name: str
    star_cn: str
    planet_name: str
    star_event: str        # 'rising' | 'culminating' | 'setting' | 'anti_culminating'
    planet_event: str
    orb: float             # degrees of right ascension difference
    star_meaning_cn: str = ""
    star_meaning_en: str = ""
    star_nature: str = ""

    @property
    def star_event_en(self) -> str:
        return PARAN_EVENTS.get(self.star_event, {}).get("en", self.star_event)

    @property
    def planet_event_en(self) -> str:
        return PARAN_EVENTS.get(self.planet_event, {}).get("en", self.planet_event)

    @property
    def star_event_cn(self) -> str:
        return PARAN_EVENTS.get(self.star_event, {}).get("cn", self.star_event)

    @property
    def planet_event_cn(self) -> str:
        return PARAN_EVENTS.get(self.planet_event, {}).get("cn", self.planet_event)


@dataclass
class HeliacalResult:
    """Result of a heliacal phenomenon calculation."""
    body_name: str
    body_cn: str
    event_type: int         # swe.HELIACAL_RISING etc.
    event_jd: float         # Julian Day of the event
    event_date: str         # ISO-8601 date string
    visibility_mag: float = 0.0
    is_star: bool = False

    @property
    def event_name_en(self) -> str:
        return HELIACAL_EVENTS.get(self.event_type, {}).get("en", str(self.event_type))

    @property
    def event_name_cn(self) -> str:
        return HELIACAL_EVENTS.get(self.event_type, {}).get("cn", str(self.event_type))


@dataclass
class AsteroidAspect:
    """One aspect between an asteroid and a planet."""
    asteroid_name: str
    planet_name: str
    aspect_name: str
    aspect_symbol: str
    angle: float
    orb: float
    is_applying: bool


# ── Internal helpers ─────────────────────────────────────────────────────────

def _get_equatorial(jd: float, body_id: int) -> tuple[float, float] | None:
    """Return (RA, Dec) in degrees for a planetary body, or None on error."""
    try:
        flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL | swe.FLG_SPEED
        xx, _ = swe.calc_ut(jd, body_id, flags)
        return float(xx[0]), float(xx[1])
    except Exception:
        return None


def _get_star_equatorial(swe_name: str, jd: float) -> tuple[float, float] | None:
    """Return (RA, Dec) in degrees for a fixed star, or None on error."""
    try:
        flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
        _, xx = swe.fixstar2_ut(swe_name, jd, flags)
        return float(xx[0]), float(xx[1])
    except Exception:
        try:
            _, xx = swe.fixstar_ut(swe_name, jd, flags)
            return float(xx[0]), float(xx[1])
        except Exception:
            return None


def _paran_times(ra: float, dec: float, lat: float) -> dict[str, float] | None:
    """Compute the 4 ARMC (sidereal time in degrees) values at which a body
    with right ascension *ra* and declination *dec* is at the horizon
    (rising / setting) or meridian (culminating / anti-culminating), as seen
    from geographic latitude *lat*.

    Returns a dict with keys 'rising', 'culminating', 'setting',
    'anti_culminating', or None for circumpolar / never-rises bodies.
    """
    lat_r  = math.radians(lat)
    dec_r  = math.radians(dec)
    cos_ha = -math.tan(lat_r) * math.tan(dec_r)
    if abs(cos_ha) > 1.0:
        # Circumpolar or never rises — no horizon crossing
        return None
    ha_deg = math.degrees(math.acos(cos_ha))   # semi-diurnal arc

    # Oblique ascension: OA = RA - AD,  AD = arcsin(sin(lat) * sin(dec) / cos(lat))
    # Simplified: OA = RA - arctan(cos(lat) ... ) — the standard formula gives:
    # AD = arcsin(tan(lat) * tan(dec))  [only valid when |cos_ha| < 1]
    ad_deg = math.degrees(math.asin(math.sin(lat_r) * math.sin(dec_r)
                                    / math.cos(lat_r))) if abs(lat) < 89.9 else 0.0

    oa = (ra - ad_deg) % 360.0  # oblique ascension

    return {
        "rising":           oa,
        "culminating":      ra % 360.0,
        "setting":          (oa + 180.0) % 360.0,
        "anti_culminating": (ra + 180.0) % 360.0,
    }


def _jd_to_date(jd: float) -> str:
    """Convert a Julian Day to an ISO-8601 date string."""
    try:
        y, m, d, _ = swe.revjul(jd)
        return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
    except Exception:
        return "unknown"


# ── Public API ───────────────────────────────────────────────────────────────

def calculate_parans(
    jd: float,
    lat: float,
    lon: float,
    stars,               # list of FixedStarPosition objects
    orb: float = 1.5,
    planet_ids: dict | None = None,
) -> list[ParanResult]:
    """Calculate Paranatellonta (parans): fixed stars that are simultaneously
    rising, culminating, setting, or anti-culminating with a planet or angle.

    Parameters
    ----------
    jd:
        Julian Day (UT) for the chart moment.
    lat, lon:
        Geographic latitude / longitude of the observer (degrees).
    stars:
        Iterable of FixedStarPosition-like objects with attributes
        ``.name``, ``.swe_name`` (via the catalog), and optional
        ``.meaning_cn``, ``.meaning_en``, ``.nature``.  The function
        accepts the raw catalog list or compute_fixed_star_positions() output.
    orb:
        Maximum RA difference (degrees) to count as a paran.
    planet_ids:
        Mapping of {display_name: swe_body_id}.  Defaults to the
        10 traditional planets.

    Returns
    -------
    List of ParanResult sorted by orb (closest first).
    """
    if planet_ids is None:
        planet_ids = {k: v for k, v in _TRAD_PLANETS.items()
                      if v is not None}  # exclude synthetic ASC/MC

    # --- equatorial coordinates for planets --------------------------------
    planet_paran: dict[str, dict] = {}
    for pname, pid in planet_ids.items():
        eq = _get_equatorial(jd, pid)
        if eq is None:
            continue
        ra, dec = eq
        times = _paran_times(ra, dec, lat)
        if times:
            planet_paran[pname] = {"ra": ra, "dec": dec, "times": times}

    if not planet_paran:
        return []

    # --- equatorial coordinates for fixed stars ----------------------------
    # stars may be FixedStarPosition dataclass objects or raw catalog dicts
    from astro.western.fixed_stars import load_star_catalog

    catalog = {s["name"]: s["swe_name"] for s in load_star_catalog()}

    results: list[ParanResult] = []
    for star in stars:
        swe_name = getattr(star, "swe_name", None) or catalog.get(star.name)
        if swe_name is None:
            continue
        eq = _get_star_equatorial(swe_name, jd)
        if eq is None:
            continue
        ra, dec = eq
        s_times = _paran_times(ra, dec, lat)
        if s_times is None:
            continue

        for pname, pdata in planet_paran.items():
            for s_event, s_armc in s_times.items():
                for p_event, p_armc in pdata["times"].items():
                    diff = abs(s_armc - p_armc) % 360.0
                    actual_orb = min(diff, 360.0 - diff)
                    if actual_orb <= orb:
                        results.append(ParanResult(
                            star_name=star.name,
                            star_cn=getattr(star, "name_cn", star.name),
                            planet_name=pname,
                            star_event=s_event,
                            planet_event=p_event,
                            orb=round(actual_orb, 3),
                            star_meaning_cn=getattr(star, "meaning_cn", ""),
                            star_meaning_en=getattr(star, "meaning_en", ""),
                            star_nature=getattr(star, "nature", ""),
                        ))

    results.sort(key=lambda r: r.orb)
    return results


def calculate_heliacal(
    jd: float,
    lat: float,
    lon: float,
    altitude: float = 0.0,
    stars: list | None = None,
    look_ahead_days: int = 365,
) -> list[HeliacalResult]:
    """Calculate heliacal rising / setting events for planets and optionally
    fixed stars within a look-ahead window.

    Uses ``swe.heliacal_ut()`` (available in pyswisseph ≥ 2.x).

    Parameters
    ----------
    jd:
        Start Julian Day (UT).
    lat, lon:
        Geographic latitude / longitude.
    altitude:
        Observer altitude in metres above sea level.
    stars:
        Optional list of FixedStarPosition objects.  Pass None to skip
        fixed-star heliacal events (saves computation time).
    look_ahead_days:
        How many days ahead to search for each event.

    Returns
    -------
    List of HeliacalResult sorted chronologically.
    """
    results: list[HeliacalResult] = []
    geo = [lon, lat, altitude]
    atmo = [1013.25, 15.0, 0.25, 0.0]   # pressure hPa, temp °C, humidity, TBC
    observer = [0.0, 0.0, 0.0]           # eye height, telescope aperture, etc.

    heliacal_planet_names = {
        swe.MOON:    ("Moon", "月亮"),
        swe.VENUS:   ("Venus", "金星"),
        swe.MARS:    ("Mars", "火星"),
        swe.JUPITER: ("Jupiter", "木星"),
        swe.SATURN:  ("Saturn", "土星"),
        swe.MERCURY: ("Mercury", "水星"),
    }

    for event_type in (swe.HELIACAL_RISING, swe.HELIACAL_SETTING,
                       swe.EVENING_FIRST,   swe.MORNING_LAST):
        for pid, (en_name, cn_name) in heliacal_planet_names.items():
            try:
                ret = swe.heliacal_ut(
                    jd, geo, atmo, observer, "",
                    event_type, swe.FLG_SWIEPH, pid,
                )
                if ret and ret[0] and ret[0][0] > 0:
                    evt_jd = float(ret[0][0])
                    if evt_jd - jd <= look_ahead_days:
                        results.append(HeliacalResult(
                            body_name=en_name,
                            body_cn=cn_name,
                            event_type=event_type,
                            event_jd=evt_jd,
                            event_date=_jd_to_date(evt_jd),
                            is_star=False,
                        ))
            except Exception:
                pass

    if stars:
        from astro.western.fixed_stars import load_star_catalog
        catalog = {s["name"]: s["swe_name"] for s in load_star_catalog()}
        cn_catalog = {s["name"]: s.get("cn_name", s["name"])
                      for s in load_star_catalog()}

        for star in stars[:30]:   # limit to top 30 stars for performance
            swe_name = getattr(star, "swe_name", None) or catalog.get(star.name)
            if not swe_name:
                continue
            cn_name = cn_catalog.get(star.name, star.name)
            for event_type in (swe.HELIACAL_RISING, swe.HELIACAL_SETTING):
                try:
                    ret = swe.heliacal_ut(
                        jd, geo, atmo, observer, swe_name,
                        event_type, swe.FLG_SWIEPH | swe.FIXSTAR,
                    )
                    if ret and ret[0] and ret[0][0] > 0:
                        evt_jd = float(ret[0][0])
                        if evt_jd - jd <= look_ahead_days:
                            results.append(HeliacalResult(
                                body_name=star.name,
                                body_cn=cn_name,
                                event_type=event_type,
                                event_jd=evt_jd,
                                event_date=_jd_to_date(evt_jd),
                                is_star=True,
                            ))
                except Exception:
                    pass

    results.sort(key=lambda r: r.event_jd)
    return results


# Aspect table for asteroid-to-planet aspects
_ASPECT_DEFS = [
    ("Conjunction",  "☌",   0,  8),
    ("Opposition",   "☍", 180,  8),
    ("Trine",        "△", 120,  6),
    ("Square",       "□",  90,  6),
    ("Sextile",      "⚹",  60,  4),
    ("Quincunx",     "⚻", 150,  2),
    ("Semi-square",  "∠",  45,  2),
    ("Sesquiquadrate","⊼", 135,  2),
]


def get_asteroid_aspects(
    asteroid_positions,    # list of AsteroidPosition
    planet_longitudes: dict[str, float],
    include_minor: bool = False,
) -> list[AsteroidAspect]:
    """Find aspects between asteroids and traditional planets.

    Parameters
    ----------
    asteroid_positions:
        List of AsteroidPosition objects.
    planet_longitudes:
        Dict of {planet_name: ecliptic_longitude}.
    include_minor:
        If True, also check quincunx, semi-square, sesquiquadrate.

    Returns
    -------
    List of AsteroidAspect sorted by orb.
    """
    aspect_defs = _ASPECT_DEFS if include_minor else _ASPECT_DEFS[:5]
    results: list[AsteroidAspect] = []

    for ast in asteroid_positions:
        for pname, p_lon in planet_longitudes.items():
            diff = abs(ast.longitude - p_lon) % 360.0
            diff = min(diff, 360.0 - diff)
            for asp_name, symbol, angle, max_orb in aspect_defs:
                orb = abs(diff - angle)
                if orb <= max_orb:
                    # Determine applying vs separating:
                    # Compute the signed angular separation (ast - planet), then
                    # check whether the asteroid's motion (speed sign) is closing
                    # or opening that gap toward the exact aspect angle.
                    # This is an approximation assuming the planet is much slower.
                    signed_diff = (ast.longitude - p_lon) % 360.0
                    # For conjunction (angle=0): applying if signed_diff < 180 and ast moving forward (positive speed)
                    # or signed_diff > 180 and ast retrograde.
                    # General rule: reducing |diff - angle| over time = applying.
                    is_applying = False
                    if ast.speed != 0:
                        # Estimate how diff changes with asteroid moving by a small step
                        step = 0.001  # degrees
                        future_lon = (ast.longitude + ast.speed * step) % 360.0
                        future_diff = abs(future_lon - p_lon) % 360.0
                        future_diff = min(future_diff, 360.0 - future_diff)
                        future_orb = abs(future_diff - angle)
                        is_applying = future_orb < orb
                    results.append(AsteroidAspect(
                        asteroid_name=ast.name,
                        planet_name=pname,
                        aspect_name=asp_name,
                        aspect_symbol=symbol,
                        angle=angle,
                        orb=round(orb, 3),
                        is_applying=is_applying,
                    ))
                    break   # take the first matching aspect

    results.sort(key=lambda a: a.orb)
    return results
