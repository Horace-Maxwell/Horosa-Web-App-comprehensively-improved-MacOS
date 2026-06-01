"""
astro/western_return.py — 返照盤 (Solar & Lunar Return)

Finds the exact moment Sun/Moon returns to natal position,
then casts a full chart.
"""
import streamlit as st
import swisseph as swe
from dataclasses import dataclass
from .western import compute_western_chart

SUN_DAILY_MOTION = 0.9856   # degrees per day
MOON_DAILY_MOTION = 13.2    # degrees per day


def _normalize(deg):
    return deg % 360.0


def _angle_diff_signed(target, current):
    d = (target - current) % 360
    return d - 360 if d > 180 else d


def _jd_to_datetime_str(jd):
    y, m, d, h = swe.revjul(jd)
    hrs = int(h)
    mins = int((h - hrs) * 60)
    secs = int(((h - hrs) * 60 - mins) * 60)
    return f"{y:04d}-{m:02d}-{int(d):02d} {hrs:02d}:{mins:02d}:{secs:02d}"


@dataclass
class SolarReturnResult:
    natal_sun_longitude: float
    return_year: int
    return_jd: float
    return_date: str
    return_chart: object


@dataclass
class LunarReturnResult:
    natal_moon_longitude: float
    return_jd: float
    return_date: str
    return_chart: object


@st.cache_data(ttl=3600, show_spinner=False)
def compute_solar_return(natal_sun_lon, target_year, latitude, longitude,
                         timezone=0.0, location_name=""):
    """Find when Sun returns to natal longitude in target_year."""
    # Start estimate: target_year birthday
    jd_start = swe.julday(target_year, 3, 21, 12.0)
    jd = jd_start

    for _ in range(50):
        xx, _ = swe.calc_ut(jd, swe.SUN)
        current_lon = xx[0]
        diff = _angle_diff_signed(natal_sun_lon, current_lon)
        if abs(diff) < 0.00001:
            break
        jd += diff / SUN_DAILY_MOTION

    # Convert JD to date components for chart
    y, m, d, h = swe.revjul(jd)

    chart = compute_western_chart(
        year=y, month=m, day=int(d), hour=int(h),
        minute=int((h - int(h)) * 60),
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )

    return SolarReturnResult(
        natal_sun_longitude=natal_sun_lon, return_year=target_year,
        return_jd=jd, return_date=_jd_to_datetime_str(jd),
        return_chart=chart,
    )


@st.cache_data(ttl=3600, show_spinner=False)
def compute_lunar_return(natal_moon_lon, after_jd, latitude, longitude,
                         timezone=0.0, location_name=""):
    """Find next Moon return to natal longitude after given JD."""
    jd = after_jd

    for _ in range(50):
        xx, _ = swe.calc_ut(jd, swe.MOON)
        current_lon = xx[0]
        diff = _angle_diff_signed(natal_moon_lon, current_lon)
        if abs(diff) < 0.00001:
            break
        jd += diff / MOON_DAILY_MOTION

    y, m, d, h = swe.revjul(jd)
    chart = compute_western_chart(
        year=y, month=m, day=int(d), hour=int(h),
        minute=int((h - int(h)) * 60),
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )

    return LunarReturnResult(
        natal_moon_longitude=natal_moon_lon,
        return_jd=jd, return_date=_jd_to_datetime_str(jd),
        return_chart=chart,
    )
