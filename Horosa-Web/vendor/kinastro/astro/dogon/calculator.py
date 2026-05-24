"""Dogon Sirius Cosmology calculation engine (pure computation)."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, field
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional


@dataclass
class DogonBodyPoint:
    key: str
    label: str
    dogon_name: str
    longitude: float
    declination: float
    orbit_phase: float
    cultural_note_zh: str
    cultural_note_en: str
    # Sirius B-specific: angular separation from A in arcsec (0 for A/C)
    separation_arcsec: float = 0.0


@dataclass
class SiguiCycleInfo:
    anchor_year: int
    cycle_years: int
    previous_year: int
    next_year: int
    years_since_previous: float
    years_until_next: float
    life_phase: int = 1
    life_phase_label_zh: str = ""
    life_phase_label_en: str = ""
    life_phase_desc_zh: str = ""
    life_phase_desc_en: str = ""


@dataclass
class DogonZoneResult:
    zone_id: Optional[str]
    label: str
    in_zone: bool
    meaning_zh: str
    meaning_en: str


@dataclass
class HeliacalRisingInfo:
    """Approximate heliacal rising date for Sirius at the given location/year."""
    julian_day: float
    date_str: str          # ISO date string "YYYY-MM-DD"
    days_until: float      # days until next heliacal rising from query date


@dataclass
class SiriusBirthAspect:
    """Aspect between Sirius and a natal planet."""
    planet: str
    planet_longitude: float
    sirius_longitude: float
    aspect_name: str
    orb: float
    nommo_resonance: bool   # true if trine/sextile (Nommo harmonics)
    meaning_zh: str
    meaning_en: str


@dataclass
class DogonSiriusChart:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    julian_day: float
    sirius_longitude: float
    sirius_declination: float
    overlay_real_position: bool
    bodies: list[DogonBodyPoint]
    zone_result: DogonZoneResult
    sigui: SiguiCycleInfo
    personal_influence_zh: str
    personal_influence_en: str
    disclaimer_zh: str
    disclaimer_en: str
    references: list[str]
    cross_cultural: list[dict[str, str]]
    heliacal_rising: Optional[HeliacalRisingInfo] = None
    birth_aspects: list[SiriusBirthAspect] = field(default_factory=list)


@lru_cache(maxsize=1)
def load_dogon_constants() -> dict[str, Any]:
    p = Path(__file__).parent / "data" / "constants.json"
    return json.loads(p.read_text(encoding="utf-8"))


def _normalize_360(value: float) -> float:
    return value % 360.0


def _decimal_year(year: int, month: int, day: int) -> float:
    start = datetime(year, 1, 1)
    current = datetime(year, month, day)
    next_start = datetime(year + 1, 1, 1)
    total_days = (next_start - start).days
    elapsed_days = (current - start).days
    return year + (elapsed_days / max(1, total_days))


def _compute_jd(year: int, month: int, day: int, hour: int, minute: int, timezone_offset: float) -> float:
    try:
        import swisseph as swe
    except Exception:
        ut_hour = hour + minute / 60.0 - timezone_offset
        # Meeus-like approximation fallback for environments without swisseph
        a = (14 - month) // 12
        y = year + 4800 - a
        m = month + 12 * a - 3
        jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        return jdn + (ut_hour - 12.0) / 24.0
    ut_hour = hour + minute / 60.0 - timezone_offset
    return swe.julday(year, month, day, ut_hour)


def _init_swe() -> None:
    try:
        from astro.swe_init import init_swisseph

        init_swisseph()
    except Exception:
        pass


def _compute_sirius_real_position(jd: float) -> tuple[float, float]:
    """Return (ecliptic_lon, declination)."""
    try:
        import swisseph as swe

        _init_swe()
        ecl, _ = swe.fixstar2_ut("Sirius", jd)
        eq, _ = swe.fixstar2_ut("Sirius", jd, swe.FLG_EQUATORIAL)
        return _normalize_360(float(ecl[0])), float(eq[1])
    except Exception:
        # Stable fallback: approximate Sirius around tropical Cancer with southern declination
        days = jd - 2451545.0
        drift = (days / 36525.0) * 1.4
        lon = _normalize_360(104.0 + drift)
        dec = -16.7 + 0.05 * math.sin(days / 365.25)
        return lon, dec


def _sigui_info(decimal_year: float, anchor: int, cycle: int, phases: list[dict[str, Any]]) -> SiguiCycleInfo:
    elapsed = decimal_year - anchor
    idx = math.floor(elapsed / cycle)
    prev_year = anchor + idx * cycle
    next_year = prev_year + cycle
    years_since = max(0.0, decimal_year - prev_year)

    # Determine life phase from offset within the cycle
    phase_num, phase_label_zh, phase_label_en, phase_desc_zh, phase_desc_en = 1, "", "", "", ""
    for p in phases:
        lo, hi = p["range_years"]
        if lo <= years_since < hi:
            phase_num = p["phase"]
            phase_label_zh = p["label_zh"]
            phase_label_en = p["label_en"]
            phase_desc_zh = p["desc_zh"]
            phase_desc_en = p["desc_en"]
            break
    # fallback: last phase if past end
    if not phase_label_zh and phases:
        last = phases[-1]
        phase_num = last["phase"]
        phase_label_zh = last["label_zh"]
        phase_label_en = last["label_en"]
        phase_desc_zh = last["desc_zh"]
        phase_desc_en = last["desc_en"]

    return SiguiCycleInfo(
        anchor_year=anchor,
        cycle_years=cycle,
        previous_year=prev_year,
        next_year=next_year,
        years_since_previous=years_since,
        years_until_next=max(0.0, next_year - decimal_year),
        life_phase=phase_num,
        life_phase_label_zh=phase_label_zh,
        life_phase_label_en=phase_label_en,
        life_phase_desc_zh=phase_desc_zh,
        life_phase_desc_en=phase_desc_en,
    )


def _resolve_zone(declination: float, zones: list[dict[str, Any]]) -> DogonZoneResult:
    for z in zones:
        dmin = float(z["declination_min"])
        dmax = float(z["declination_max"])
        if dmin <= declination < dmax:
            return DogonZoneResult(
                zone_id=z["id"],
                label=z["label"],
                in_zone=True,
                meaning_zh=z["meaning_zh"],
                meaning_en=z["meaning_en"],
            )
    return DogonZoneResult(
        zone_id=None,
        label="Out-of-band",
        in_zone=False,
        meaning_zh="位於定義區域之外，重點看週期與儀式節律。",
        meaning_en="Outside predefined bands; emphasize cycle timing and ritual rhythm.",
    )


def _solve_kepler(M: float, e: float, tol: float = 1e-9) -> float:
    """Solve Kepler's equation M = E - e*sin(E) for eccentric anomaly E (radians)."""
    E = M if e < 0.8 else math.pi
    for _ in range(100):
        dE = (M - E + e * math.sin(E)) / (1.0 - e * math.cos(E))
        E += dE
        if abs(dE) < tol:
            break
    return E


def _sirius_b_angular_separation(jd: float, constants: dict[str, Any]) -> tuple[float, float]:
    """Compute Sirius B position angle and angular separation (arcsec) from Sirius A.

    Uses Thiele-Innes orbital elements from constants.json.  The result is the
    projected on-sky separation in arcseconds and position angle in degrees.
    """
    sys = constants["system"]
    P = float(sys.get("sigui_b_orbital_period_years", 50.09))  # years
    e = float(sys.get("sirius_b_eccentricity", 0.5914))
    a = float(sys.get("sirius_b_semimajor_arcsec", 7.56))      # arcsec
    i = math.radians(float(sys.get("sirius_b_inclination_deg", 136.5)))
    omega = math.radians(float(sys.get("sirius_b_omega_deg", 147.3)))   # argument of periapsis
    Omega = math.radians(float(sys.get("sirius_b_Omega_deg", 44.6)))    # longitude of ascending node
    T_peri_jd = float(sys.get("sirius_b_T_peri_jd", 2446000.5))

    # Mean anomaly
    P_days = P * 365.25
    M = (2 * math.pi / P_days) * ((jd - T_peri_jd) % P_days)

    # Eccentric anomaly
    E = _solve_kepler(M, e)

    # True anomaly
    nu = 2.0 * math.atan2(
        math.sqrt(1 + e) * math.sin(E / 2),
        math.sqrt(1 - e) * math.cos(E / 2),
    )

    # Radius (arcsec)
    r = a * (1 - e * math.cos(E))

    # On-sky projected position (X = East, Y = North convention)
    x = r * (math.cos(Omega) * math.cos(omega + nu) - math.sin(Omega) * math.sin(omega + nu) * math.cos(i))
    y = r * (math.sin(Omega) * math.cos(omega + nu) + math.cos(Omega) * math.sin(omega + nu) * math.cos(i))

    sep = math.hypot(x, y)
    pa = math.degrees(math.atan2(x, y)) % 360.0  # position angle E of N

    return sep, pa


def _build_bodies(
    constants: dict[str, Any],
    sirius_lon: float,
    sirius_dec: float,
    decimal_year: float,
    jd: float,
) -> list[DogonBodyPoint]:
    bodies_cfg = constants["bodies"]
    cfg_a = bodies_cfg["sirius_a"]
    cfg_b = bodies_cfg["sirius_b"]
    cfg_c = bodies_cfg["sirius_c"]

    # Sirius B: use precise orbital elements
    sep_b, pa_b = _sirius_b_angular_separation(jd, constants)
    # Convert angular separation to degree offset on ecliptic (approximation)
    deg_offset_b = sep_b / 3600.0  # arcsec → degrees (very small correction on ecliptic)
    pa_rad = math.radians(pa_b)
    lon_b = _normalize_360(sirius_lon + deg_offset_b * math.sin(pa_rad))
    dec_b = sirius_dec + deg_offset_b * math.cos(pa_rad)

    # Orbital phase for Sirius B
    P_b = float(cfg_b["period_years"])
    T_peri_jd = float(constants["system"].get("sirius_b_T_peri_jd", 2446000.5))
    phase_b = ((jd - T_peri_jd) % (P_b * 365.25)) / (P_b * 365.25)

    # Sirius C (Emme Ya): cultural body, simple phase model
    P_c = float(cfg_c["period_years"])
    phase_c = ((decimal_year - 1900.0) % P_c) / P_c
    lon_c = _normalize_360(sirius_lon + 18.0 * math.sin(2 * math.pi * phase_c + 1.2))
    dec_c = sirius_dec + 5.0 * math.cos(2 * math.pi * phase_c + 0.7)

    return [
        DogonBodyPoint(
            key="sirius_a",
            label=cfg_a["label"],
            dogon_name=cfg_a["dogon_name"],
            longitude=sirius_lon,
            declination=sirius_dec,
            orbit_phase=0.0,
            cultural_note_zh=cfg_a["cultural"]["zh"],
            cultural_note_en=cfg_a["cultural"]["en"],
            separation_arcsec=0.0,
        ),
        DogonBodyPoint(
            key="sirius_b",
            label=cfg_b["label"],
            dogon_name=cfg_b["dogon_name"],
            longitude=lon_b,
            declination=dec_b,
            orbit_phase=phase_b,
            cultural_note_zh=cfg_b["cultural"]["zh"],
            cultural_note_en=cfg_b["cultural"]["en"],
            separation_arcsec=sep_b,
        ),
        DogonBodyPoint(
            key="sirius_c",
            label=cfg_c["label"],
            dogon_name=cfg_c["dogon_name"],
            longitude=lon_c,
            declination=dec_c,
            orbit_phase=phase_c,
            cultural_note_zh=cfg_c["cultural"]["zh"],
            cultural_note_en=cfg_c["cultural"]["en"],
            separation_arcsec=0.0,
        ),
    ]


def _compute_heliacal_rising(
    jd: float,
    latitude: float,
    longitude: float,
) -> Optional[HeliacalRisingInfo]:
    """Approximate the next heliacal rising date of Sirius for the given location.

    Strategy: step forward in one-day increments from the current JD until Sirius
    rises before the Sun and is above the horizon at astronomical dawn.
    Uses pyswisseph heliacal rising if available; falls back to an analytical
    approximation based on Sirius's known mid-July heliacal rising at lat ~30°N.
    """
    try:
        import swisseph as swe
        _init_swe()

        # swe.heliacal_ut(startjd, geopos, atmo, observer, star, event_type, helflag)
        geopos = [longitude, latitude, 0.0]
        atmo = [1013.25, 15.0, 0.15, 0.15]   # pressure, temp, humidity, visibility
        observer = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        result, err = swe.heliacal_ut(jd, geopos, atmo, observer, "Sirius", swe.HELIACAL_RISING, 0)
        if result and len(result) > 0:
            rise_jd = float(result[0])
            days_until = rise_jd - jd
            # Convert JD to date
            y, m, d, _ = swe.revjul(rise_jd)
            date_str = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
            return HeliacalRisingInfo(julian_day=rise_jd, date_str=date_str, days_until=days_until)
    except Exception:
        pass

    # Analytical fallback: Sirius heliacal rising ~July 17 at lat 28°N (Cairo/Dogon region)
    # Shifts ~1 day per degree of latitude. For other latitudes approximate linearly.
    try:
        import swisseph as _swe_mod
        base_year = int(_swe_mod.revjul(jd)[0])
    except Exception:
        base_year = int(jd / 365.25) + 1970

    lat_shift = int((latitude - 28.0) * 1.0)   # crude: 1 day per degree
    base_doy = 198 + lat_shift  # ~July 17 = DOY 198

    for yr_offset in range(2):
        yr = base_year + yr_offset
        try:
            rise_doy = max(1, min(365, base_doy))
            import datetime as _dt
            rise_date = _dt.date(yr, 1, 1) + _dt.timedelta(days=rise_doy - 1)
            # Convert date to JD
            rise_jd = (
                _compute_jd(rise_date.year, rise_date.month, rise_date.day, 6, 0, 0.0)
            )
            days_until = rise_jd - jd
            if days_until >= 0:
                return HeliacalRisingInfo(
                    julian_day=rise_jd,
                    date_str=rise_date.isoformat(),
                    days_until=days_until,
                )
        except Exception:
            continue

    return None


def _angular_diff(a: float, b: float) -> float:
    """Smallest signed angular difference b - a, in range (-180, 180]."""
    d = (b - a) % 360.0
    return d - 360.0 if d > 180.0 else d


_ASPECT_DEFS = [
    ("Conjunction",  0.0),
    ("Opposition",  180.0),
    ("Trine",       120.0),
    ("Square",       90.0),
    ("Sextile",      60.0),
]


def _compute_birth_aspects(
    sirius_lon: float,
    natal_planets: dict[str, float],
    orb_cfg: dict[str, float],
    nommo_harmonics: list[int],
) -> list[SiriusBirthAspect]:
    """Detect aspects between Sirius A and natal planets."""
    aspects: list[SiriusBirthAspect] = []
    for planet, p_lon in natal_planets.items():
        diff = abs(_angular_diff(sirius_lon, p_lon))
        for asp_name, asp_angle in _ASPECT_DEFS:
            orb_limit = orb_cfg.get(asp_name.lower(), 6.0)
            orb_val = abs(diff - asp_angle)
            if orb_val <= orb_limit:
                is_nommo = int(asp_angle) in nommo_harmonics
                if asp_name == "Conjunction":
                    meaning_zh = f"Sirius 合相 {planet}：祖靈能量直接注入此星原力。"
                    meaning_en = f"Sirius conjunct {planet}: ancestral star-force infuses this planet directly."
                elif asp_name == "Opposition":
                    meaning_zh = f"Sirius 對分 {planet}：Nommo 二元性張力，召喚整合與更新。"
                    meaning_en = f"Sirius opposite {planet}: Nommo polarity tension, calling for integration and renewal."
                elif asp_name == "Trine":
                    meaning_zh = f"Sirius 三分 {planet}：宇宙秩序（Amma）以和諧水流貫通此星。"
                    meaning_en = f"Sirius trine {planet}: Amma's cosmic order flows harmoniously through this planet."
                elif asp_name == "Square":
                    meaning_zh = f"Sirius 四分 {planet}：儀式衝突，需透過行動轉化星際張力。"
                    meaning_en = f"Sirius square {planet}: ritual friction; tension transforms through purposeful action."
                else:
                    meaning_zh = f"Sirius 六分 {planet}：輕柔的 Nommo 共鳴，滋養創造性連結。"
                    meaning_en = f"Sirius sextile {planet}: gentle Nommo resonance nourishing creative connection."
                aspects.append(SiriusBirthAspect(
                    planet=planet,
                    planet_longitude=p_lon,
                    sirius_longitude=sirius_lon,
                    aspect_name=asp_name,
                    orb=round(orb_val, 2),
                    nommo_resonance=is_nommo,
                    meaning_zh=meaning_zh,
                    meaning_en=meaning_en,
                ))
                break  # one aspect per planet
    return aspects


def format_dogon_sirius_for_prompt(chart: DogonSiriusChart, lang: str = "zh") -> str:
    is_zh = lang in ("zh", "zh_cn")
    zone_meaning = chart.zone_result.meaning_zh if is_zh else chart.zone_result.meaning_en
    influence = chart.personal_influence_zh if is_zh else chart.personal_influence_en
    rows = [
        f"Dogon Sirius Cosmology @ {chart.location_name}",
        f"Date: {chart.year:04d}-{chart.month:02d}-{chart.day:02d} {chart.hour:02d}:{chart.minute:02d} (UTC{chart.timezone:+.1f})",
        f"Sirius lon/dec: {chart.sirius_longitude:.2f}° / {chart.sirius_declination:.2f}°",
        f"Zone: {chart.zone_result.label} ({zone_meaning})",
        f"Sigui previous/next: {chart.sigui.previous_year} / {chart.sigui.next_year}",
        f"Years until next Sigui: {chart.sigui.years_until_next:.2f}",
        f"Life Phase: {chart.sigui.life_phase} — {chart.sigui.life_phase_label_zh if is_zh else chart.sigui.life_phase_label_en}",
        "Bodies:",
    ]
    for b in chart.bodies:
        line = f"- {b.label} ({b.dogon_name}): lon {b.longitude:.2f}°, dec {b.declination:.2f}°"
        if b.key == "sirius_b" and b.separation_arcsec > 0:
            line += f", sep {b.separation_arcsec:.2f}\""
        rows.append(line)
    if chart.heliacal_rising:
        rows.append(f"Heliacal Rising: {chart.heliacal_rising.date_str} ({chart.heliacal_rising.days_until:.0f} days)")
    if chart.birth_aspects:
        rows.append("Birth Aspects with Sirius:")
        for asp in chart.birth_aspects:
            rows.append(f"  - {asp.aspect_name} {asp.planet} (orb {asp.orb}°): {asp.meaning_zh if is_zh else asp.meaning_en}")
    rows.append("Interpretation:")
    rows.append(influence)
    rows.append("Disclaimer:")
    rows.append(chart.disclaimer_zh if is_zh else chart.disclaimer_en)
    return "\n".join(rows)


def compute_dogon_sirius_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    overlay_real_position: bool = True,
    natal_planets: Optional[dict[str, float]] = None,
) -> DogonSiriusChart:
    """Compute Dogon Sirius cosmology chart for given birth data.

    Args:
        natal_planets: Optional dict mapping planet names to their ecliptic
            longitudes (degrees) in the natal chart.  When provided, aspects
            between Sirius and natal planets are calculated.
    """
    from .interpretations import build_dogon_personal_influence

    constants = load_dogon_constants()

    lat = max(-90.0, min(90.0, float(latitude)))
    lon = ((float(longitude) + 180.0) % 360.0) - 180.0

    jd = _compute_jd(year, month, day, hour, minute, timezone)
    sirius_lon, sirius_dec = _compute_sirius_real_position(jd)

    dyear = _decimal_year(year, month, day)
    cycle = int(constants["system"]["sigui_cycle_years"])
    anchor = int(constants["system"]["sigui_anchor_year"])
    phases = constants.get("sigui_life_phases", [])

    zone_result = _resolve_zone(sirius_dec, constants["zones"])
    sigui = _sigui_info(dyear, anchor, cycle, phases)
    bodies = _build_bodies(constants, sirius_lon, sirius_dec, dyear, jd)

    heliacal = _compute_heliacal_rising(jd, lat, lon)

    orb_cfg = constants.get("aspects", {}).get("orbs", {})
    nommo_harmonics = constants.get("aspects", {}).get("nommo_harmonics", [120, 240])
    birth_aspects: list[SiriusBirthAspect] = []
    if natal_planets:
        birth_aspects = _compute_birth_aspects(sirius_lon, natal_planets, orb_cfg, nommo_harmonics)

    influence_zh, influence_en = build_dogon_personal_influence(
        sirius_declination=sirius_dec,
        zone_result=zone_result,
        sigui=sigui,
        latitude=lat,
        longitude=lon,
    )

    cross = [
        {
            "system": row["system"],
            "zh": row["focus"]["zh"],
            "en": row["focus"]["en"],
        }
        for row in constants.get("cross_cultural", [])
    ]

    return DogonSiriusChart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=lat,
        longitude=lon,
        location_name=location_name,
        julian_day=jd,
        sirius_longitude=sirius_lon if overlay_real_position else bodies[0].longitude,
        sirius_declination=sirius_dec if overlay_real_position else bodies[0].declination,
        overlay_real_position=overlay_real_position,
        bodies=bodies,
        zone_result=zone_result,
        sigui=sigui,
        personal_influence_zh=influence_zh,
        personal_influence_en=influence_en,
        disclaimer_zh=constants["system"]["disclaimer"]["zh"],
        disclaimer_en=constants["system"]["disclaimer"]["en"],
        references=constants.get("references", []),
        cross_cultural=cross,
        heliacal_rising=heliacal,
        birth_aspects=birth_aspects,
    )
