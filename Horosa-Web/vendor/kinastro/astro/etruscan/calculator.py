"""
astro/etruscan/calculator.py — Etruscan Chart Calculator
=========================================================

Pure computation module (no Streamlit dependency) for the Etruscan
astrology system.

Core functions:
  1. compute_etruscan_chart() — main entry point
  2. _azimuth_to_templum()   — convert horizon azimuth to Templum region (1–16)
  3. _sign_from_longitude()  — ecliptic longitude → Western sign name
  4. _determine_dominant_nature() — aggregate planet placements → dominant nature
  5. format_etruscan_for_prompt() — format chart data for AI prompt generation

Astronomy backend: pyswisseph
  • swe.calc_ut()  for ecliptic planetary positions
  • swe.azalt()    for horizon azimuth/altitude
  • swe.julday()   for Julian Day number

Fallback: if azimuth computation fails (e.g. polar coordinates), the
ecliptic longitude is used to derive an approximate azimuth.

伊特魯里亞占星計算模組，純函數，不依賴 Streamlit。
使用 pyswisseph 計算行星的黃道經度與地平坐標，
再對應到16區 Templum 系統。
"""

from __future__ import annotations

import math
from typing import Optional

import swisseph as swe

from .constants import ETRUSCAN_PLANETS, TEMPLUM_16
from .models import EtruscanChart, EtruscanPlanetPosition


# ─────────────────────────────────────────────────────────────────────────────
# Swiss Ephemeris initialisation (lazy, safe for unit-test import)
# ─────────────────────────────────────────────────────────────────────────────

def _init_swe() -> None:
    """初始化 pyswisseph，優先使用集中管理的 init_swisseph()。

    Falls back to swe.set_ephe_path("") if Streamlit is not present
    (e.g. in unit-test contexts where @st.cache_resource is unavailable).
    """
    try:
        from astro.swe_init import init_swisseph
        init_swisseph()
    except Exception:
        swe.set_ephe_path("")


# ─────────────────────────────────────────────────────────────────────────────
# Zodiac sign helpers
# ─────────────────────────────────────────────────────────────────────────────

# Standard atmospheric conditions for swe.azalt() computations
_STANDARD_TEMPERATURE_CELSIUS: float = 15.0   # 標準大氣溫度 (°C)
_STANDARD_PRESSURE_HPA: float = 1013.0        # 標準大氣壓 (hPa)

_SIGN_NAMES: list[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def _sign_from_longitude(longitude: float) -> str:
    """Return the Western zodiac sign name for an ecliptic longitude.

    從黃道經度（0-360°）推算所在星座名稱。

    Args:
        longitude: Ecliptic longitude in degrees (0–360).

    Returns:
        Sign name string, e.g. "Taurus".
    """
    idx = int(longitude / 30.0) % 12
    return _SIGN_NAMES[idx]


# ─────────────────────────────────────────────────────────────────────────────
# Templum region helper
# ─────────────────────────────────────────────────────────────────────────────

def _azimuth_to_templum(azimuth: float) -> int:
    """Convert a horizon azimuth to a Templum region number (1–16).

    方位角轉換為 Templum 區域編號：
    從正北(0°)順時針每22.5°為一區，共16區。
    區域1 = 0°–22.5°，區域16 = 337.5°–360°。

    Args:
        azimuth: Horizon azimuth in degrees (0 = N, clockwise).  Any value
                 is normalised to [0, 360) before mapping.

    Returns:
        Integer region number 1–16.
    """
    normalised = azimuth % 360.0
    region = int(normalised / 22.5) % 16 + 1
    return region


# ─────────────────────────────────────────────────────────────────────────────
# Dominant nature determination
# ─────────────────────────────────────────────────────────────────────────────

def _determine_dominant_nature(planet_positions: list[EtruscanPlanetPosition]) -> str:
    """Determine the overall dominant nature of the chart.

    統計各行星所在 Templum 區域的天性，以最多的天性作為主導。
    吉 > 凶 > 中性（同票時按此優先順序）。

    Scoring:
      • favorable   +2
      • unfavorable −2
      • neutral      0

    If the total score > 0 → "favorable"
    If the total score < 0 → "unfavorable"
    Else → "neutral"

    Args:
        planet_positions: list of computed planet positions.

    Returns:
        "favorable" | "unfavorable" | "neutral"
    """
    # Build a lookup of region → nature from TEMPLUM_16
    region_nature: dict[int, str] = {
        t["region"]: t["nature"] for t in TEMPLUM_16
    }

    score = 0
    for pos in planet_positions:
        nature = region_nature.get(pos.templum_region, "neutral")
        if nature == "favorable":
            score += 2
        elif nature == "unfavorable":
            score -= 2

    if score > 0:
        return "favorable"
    if score < 0:
        return "unfavorable"
    return "neutral"


# ─────────────────────────────────────────────────────────────────────────────
# Main computation
# ─────────────────────────────────────────────────────────────────────────────

def compute_etruscan_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    ritual_type: str = "birth",
) -> EtruscanChart:
    """Compute a complete Etruscan astrology chart.

    計算完整伊特魯里亞占星命盤，包含七星（太陽至土星）的位置、
    Templum 區域分配、閃電占卜區域及主導天性。

    Pure function — no Streamlit dependency.  Streamlit callers should wrap
    this with @st.cache_data in the app layer.

    Args:
        year, month, day:  Event/birth date (civil calendar, proleptic Gregorian).
        hour, minute:      Local time of event.
        timezone:          UTC offset in hours (e.g. +1 for CET, −5 for EST).
        latitude:          Observer latitude (degrees; south is negative).
        longitude:         Observer longitude (degrees; west is negative).
        location_name:     Human-readable place name (optional).
        ritual_type:       Purpose of the reading:
                           "birth" | "national" | "personal" | "weather".

    Returns:
        EtruscanChart dataclass with all computed data.

    Raises:
        RuntimeError: Re-raised from swisseph if Julian Day computation fails
                      (e.g. invalid date).
    """
    _init_swe()

    # ── Julian Day (Universal Time) ──
    # 將本地時間轉換為 UT，再計算儒略日
    ut_hour = hour + minute / 60.0 - timezone
    jd_ut = swe.julday(year, month, day, ut_hour)

    # ── Observer position array for swe.azalt ──
    # [geographic_longitude, geographic_latitude, altitude_above_sea_m]
    geopos = [longitude, latitude, 0.0]

    planet_positions: list[EtruscanPlanetPosition] = []

    for planet_id, planet_info in ETRUSCAN_PLANETS.items():
        # ── Ecliptic position ──
        try:
            ecl_result, _ = swe.calc_ut(jd_ut, planet_id, swe.FLG_SWIEPH)
            ecl_lon: float = ecl_result[0]
        except Exception:
            ecl_lon = 0.0

        sign = _sign_from_longitude(ecl_lon)

        # ── Horizon azimuth and altitude ──
        # swe.azalt() returns [azimuth, true_altitude, apparent_altitude]
        # The XIN array for ECL2HOR is [ecl_lon, ecl_lat, distance].
        # 溫度設定為15°C，氣壓1013 hPa（標準大氣條件）
        azimuth: float = 0.0
        altitude: float = 0.0
        try:
            hor_result = swe.azalt(
                jd_ut,
                swe.ECL2HOR,
                geopos,
                _STANDARD_TEMPERATURE_CELSIUS,
                _STANDARD_PRESSURE_HPA,
                [ecl_lon, 0.0, 1.0],  # [ecl_lon, ecl_lat, distance]
            )
            # swe.azalt returns (azimuth, true_altitude, apparent_altitude)
            azimuth = float(hor_result[0])
            altitude = float(hor_result[1])
        except Exception:
            # 備援：若方位角計算失敗，以黃道經度近似方位角
            # Fallback: approximate azimuth from ecliptic longitude
            azimuth = ecl_lon % 360.0
            altitude = 0.0

        templum_region = _azimuth_to_templum(azimuth)
        is_above_horizon = altitude > 0.0

        planet_positions.append(
            EtruscanPlanetPosition(
                planet_id=planet_id,
                planet_name_zh=planet_info["zh"],
                planet_name_en=planet_info["en"],
                glyph=planet_info["glyph"],
                longitude=round(ecl_lon, 4),
                azimuth=round(azimuth, 4),
                altitude=round(altitude, 4),
                templum_region=templum_region,
                is_above_horizon=is_above_horizon,
                sign=sign,
            )
        )

    # ── Lightning region — the Templum of the Sun (planet_id=0) ──
    # 閃電占卜區域：太陽所在的 Templum 區域
    sun_pos = next((p for p in planet_positions if p.planet_id == 0), None)
    lightning_region = sun_pos.templum_region if sun_pos is not None else 1

    # ── Dominant nature ──
    dominant_nature = _determine_dominant_nature(planet_positions)

    return EtruscanChart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        jd_ut=round(jd_ut, 6),
        planet_positions=planet_positions,
        lightning_region=lightning_region,
        dominant_nature=dominant_nature,
        ritual_type=ritual_type,
    )


# ─────────────────────────────────────────────────────────────────────────────
# AI Prompt Formatter
# ─────────────────────────────────────────────────────────────────────────────

def format_etruscan_for_prompt(chart: EtruscanChart, lang: str = "zh") -> str:
    """Format an EtruscanChart for use in an AI language-model prompt.

    將 EtruscanChart 格式化為 AI 提示詞字串，供 GPT/Claude 等模型解讀。

    Args:
        chart: Computed EtruscanChart.
        lang:  "zh" for Chinese output, "en" for English output.

    Returns:
        A multi-line string suitable for inclusion in an AI prompt.
    """
    # Build a lookup of region → Templum data
    region_map: dict[int, dict] = {t["region"]: t for t in TEMPLUM_16}

    if lang == "zh":
        lines = [
            "【伊特魯里亞占星命盤資料】",
            f"日期：{chart.year}年{chart.month}月{chart.day}日 "
            f"{chart.hour:02d}:{chart.minute:02d}",
            f"地點：{chart.location_name or f'緯度{chart.latitude:.2f}° 經度{chart.longitude:.2f}°'}",
            f"時區：UTC{chart.timezone:+.1f}",
            f"儀式類型：{chart.ritual_type}",
            f"主導天性：{chart.dominant_nature}",
            f"太陽閃電占卜區域：第{chart.lightning_region}區",
            "",
            "【行星 Templum 位置】",
        ]
        for pos in chart.planet_positions:
            t_data = region_map.get(pos.templum_region, {})
            nature_zh = t_data.get("nature_zh", "")
            deity_zh = t_data.get("deity_zh", "")
            lines.append(
                f"  {pos.glyph} {pos.planet_name_zh} → "
                f"第{pos.templum_region}區（{t_data.get('name_zh', '')}）"
                f"[{nature_zh}] — {deity_zh}"
            )
        lines += [
            "",
            "請根據以上資料，從伊特魯里亞占卜傳統解讀此命盤的吉凶與人生指引。",
        ]
    else:
        lines = [
            "=== ETRUSCAN ASTROLOGY CHART DATA ===",
            f"Date: {chart.year}-{chart.month:02d}-{chart.day:02d} "
            f"{chart.hour:02d}:{chart.minute:02d} UTC{chart.timezone:+.1f}",
            f"Location: {chart.location_name or f'lat {chart.latitude:.2f}°, lon {chart.longitude:.2f}°'}",
            f"Ritual type: {chart.ritual_type}",
            f"Dominant nature: {chart.dominant_nature}",
            f"Sun lightning-divination region: Templum {chart.lightning_region}",
            "",
            "=== PLANETARY TEMPLUM POSITIONS ===",
        ]
        for pos in chart.planet_positions:
            t_data = region_map.get(pos.templum_region, {})
            nature = t_data.get("nature", "")
            deity_en = t_data.get("deity_en", "")
            lines.append(
                f"  {pos.glyph} {pos.planet_name_en} → "
                f"Templum {pos.templum_region} ({t_data.get('name_en', '')})"
                f" [{nature}] — {deity_en}"
            )
        lines += [
            "",
            "Please interpret this chart according to Etruscan divination tradition, "
            "providing guidance on auspicious/inauspicious influences and life counsel.",
        ]

    return "\n".join(lines)
