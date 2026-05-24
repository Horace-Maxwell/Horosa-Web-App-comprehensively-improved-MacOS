"""
堅占星 (Kin Astro) — FastAPI Backend
Separates compute-heavy astrology calculations from the Streamlit frontend
for better stability, performance, and reusability.

Run with:
    uvicorn api_server:app --reload

All endpoints accept birth parameters and return JSON-serializable chart data.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import logging
from datetime import date, datetime
from functools import lru_cache
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Astro compute imports (no render functions — they depend on Streamlit UI)
# ---------------------------------------------------------------------------
from astro.qizheng.calculator import compute_chart
from astro.western.western import compute_western_chart
from astro.vedic.indian import compute_vedic_chart
from astro.thai import compute_thai_chart
from astro.kabbalistic import compute_kabbalistic_chart
from astro.arabic.arabic import compute_arabic_chart
from astro.maya import compute_maya_chart
from astro.ziwei import compute_ziwei_chart
from astro.mahabote import compute_mahabote_chart
from astro.egyptian.decans import compute_decan_chart
from astro.vedic.nadi import compute_nadi_chart
from astro.zurkhai import compute_zurkhai_chart
from astro.huangji import compute_huangji_pan
from astro.western.hellenistic import compute_hellenistic_chart
from astro.hellenistic import (
    compute_profections_table,
    compute_monthly_profections,
    get_current_profection,
    compute_zodiacal_releasing_full,
    get_current_periods,
    apply_spirit_fortune_rule,
    get_current_periods_for_natal,
)
from astro.damo import compute_damo_chart
from astro.sanshi.liuren import compute_liuren_chart
from astro.sanshi.taiyi import compute_taiyi_chart
from astro.bazi import compute_bazi
from astro.horary.calculator import compute_western_horary, compute_vedic_prashna
from astro.sports import analyze_sports_horary
from astro.esoteric import compute_esoteric_chart
from astro.harmonic import compute_multi_harmonic
from astro.primary_directions import compute_primary_directions
from astro.electional.calculator import (
    compute_western_electional,
    compute_vedic_muhurta,
    find_western_elections,
    find_vedic_muhurtas,
)
from astro.picatrix import generate_picatrix_talisman
from astro.astronomical_geomancy.calculator import (
    compute_geomancy_chart,
    format_geomancy_for_prompt,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("kinastro.api")

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="堅占星 Kin Astro API",
    description=(
        "Multi-system astrology chart computation backend. "
        "Supports Chinese (七政四餘), Zi Wei Dou Shu (紫微斗數), Western, "
        "Vedic (Jyotish), Thai, Kabbalistic, Arabic, Mayan, Mahabote, "
        "Egyptian Decans, Nadi, Zurkhai, Hellenistic, "
        "Da Liu Ren (大六壬) and Taiyi (太乙命法) systems."
    ),
    version="1.0.0",
)

# =========================================================================
#  Pydantic request / response models
# =========================================================================


class BirthParams(BaseModel):
    """Common birth parameters shared by all astrology systems."""

    year: int = Field(..., ge=1, le=3000, description="Birth year")
    month: int = Field(..., ge=1, le=12, description="Birth month")
    day: int = Field(..., ge=1, le=31, description="Birth day")
    hour: int = Field(..., ge=0, le=23, description="Birth hour (0-23)")
    minute: int = Field(..., ge=0, le=59, description="Birth minute (0-59)")
    timezone: float = Field(
        ..., ge=-12.0, le=14.0, description="UTC offset (e.g. 8.0 for UTC+8)"
    )
    latitude: float = Field(
        ..., ge=-90.0, le=90.0, description="Birth latitude"
    )
    longitude: float = Field(
        ..., ge=-180.0, le=180.0, description="Birth longitude"
    )
    location_name: str = Field(
        default="", description="Human-readable location name"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "year": 1990,
                    "month": 6,
                    "day": 15,
                    "hour": 14,
                    "minute": 30,
                    "timezone": 8.0,
                    "latitude": 25.033,
                    "longitude": 121.565,
                    "location_name": "Taipei",
                }
            ]
        }
    }


class ChineseParams(BirthParams):
    """Chinese system additionally requires gender."""

    gender: str = Field(
        default="male",
        pattern=r"^(male|female)$",
        description="Gender: 'male' or 'female'",
    )


class WesternParams(BirthParams):
    """Western system supports an optional sidereal flag."""

    sidereal: bool = Field(
        default=False,
        description="Use sidereal zodiac (Lahiri ayanamsa) instead of tropical",
    )


class HellenisticParams(BirthParams):
    """Hellenistic system additionally needs birth_year and current_year."""

    current_year: Optional[int] = Field(
        default=None,
        description="Current year for profections (defaults to now)",
    )


class HuangjiParams(BirthParams):
    """Huangji system optional reference year for timeline/cross-system view."""

    reference_year: Optional[int] = Field(
        default=None,
        description="Reference year for timeline and cross-system snapshot (defaults to now)",
    )


class ProfectionsParams(BaseModel):
    """Parameters for the Annual Profections endpoint."""

    asc_lon: float = Field(
        description="Natal Ascendant longitude in degrees (0–360).",
        ge=0.0, lt=360.0,
    )
    birth_year: int = Field(description="Birth year (e.g. 1990).")
    birth_month: int = Field(default=1, description="Birth month (1–12).", ge=1, le=12)
    birth_day: int = Field(default=1, description="Birth day (1–31).", ge=1, le=31)
    num_years: int = Field(default=48, description="Number of years to compute.", ge=1, le=120)
    include_monthly: bool = Field(
        default=False,
        description="Also compute monthly profections for the current annual year.",
    )
    target_date: Optional[str] = Field(
        default=None,
        description="ISO date string 'YYYY-MM-DD' to evaluate (defaults to today).",
    )


class ZodiacalReleasingParams(BaseModel):
    """Parameters for the Zodiacal Releasing endpoint."""

    fortune_lon: float = Field(
        description="Longitude of the Lot of Fortune (0–360).",
        ge=0.0, lt=360.0,
    )
    spirit_lon: float = Field(
        description="Longitude of the Lot of Spirit (0–360).",
        ge=0.0, lt=360.0,
    )
    birth_jd: float = Field(description="Julian Day of birth.")
    target_jd: Optional[float] = Field(
        default=None,
        description="Target Julian Day (defaults to today's JD).",
    )
    source: str = Field(
        default="fortune",
        description="Which lot to release from: 'fortune' or 'spirit'.",
    )
    apply_same_sign_rule: bool = Field(
        default=True,
        description="Apply Valens' Spirit-Fortune same-sign adjustment.",
    )
    max_l1: int = Field(default=25, description="Maximum L1 periods to generate.", ge=1, le=100)


class ComputeAllParams(BirthParams):
    """Parameters for the /api/compute endpoint that runs all systems."""

    gender: str = Field(
        default="male",
        pattern=r"^(male|female)$",
        description="Gender for Chinese chart",
    )
    sidereal: bool = Field(
        default=False,
        description="Use sidereal zodiac for the Western chart",
    )
    current_year: Optional[int] = Field(
        default=None,
        description="Current year for Hellenistic profections",
    )


class PicatrixTalismanParams(BirthParams):
    """Parameters for Picatrix talismanic blueprint generation."""

    purpose: str = Field(
        default="wealth",
        description="Intent such as love, wealth, protection, healing, success, harm.",
    )
    days_ahead: int = Field(
        default=60,
        ge=1,
        le=90,
        description="Election search window in days.",
    )
    include_harmful: bool = Field(
        default=False,
        description="Allow harm-related intents in research mode only.",
    )



class TaiyiParams(BirthParams):
    """Taiyi Life Method additionally requires gender."""

    gender: str = Field(
        default="male",
        pattern=r"^(male|female)$",
        description="Gender: 'male' or 'female'",
    )


class ChartResponse(BaseModel):
    """Generic envelope for a single chart result."""

    system: str
    ok: bool = True
    data: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class ComputeAllResponse(BaseModel):
    """Response from the /api/compute endpoint (all systems)."""

    ok: bool = True
    charts: dict[str, ChartResponse] = Field(default_factory=dict)


# =========================================================================
#  Serialisation helpers
# =========================================================================

def _make_serializable(obj: Any) -> Any:
    """Recursively convert an object tree to JSON-safe primitives."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: _make_serializable(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, dict):
        return {str(k): _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(item) for item in obj]
    # Fallback: convert to string
    return str(obj)


def _chart_to_dict(chart_obj: Any) -> dict[str, Any]:
    """Convert a chart dataclass (or plain dict) to a JSON-safe dict."""
    if dataclasses.is_dataclass(chart_obj) and not isinstance(chart_obj, type):
        raw = dataclasses.asdict(chart_obj)
    elif isinstance(chart_obj, dict):
        raw = chart_obj
    else:
        raw = {"repr": str(chart_obj)}
    return _make_serializable(raw)


# =========================================================================
#  Cached computation layer
# =========================================================================

def _cache_key(params: BirthParams, **extra: Any) -> str:
    """Build a deterministic hash key from request parameters."""
    key_data = params.model_dump()
    key_data.update(extra)
    raw = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


# lru_cache requires hashable arguments, so we use the hash key string.

@lru_cache(maxsize=256)
def _cached_chinese(key: str, year: int, month: int, day: int, hour: int,
                    minute: int, timezone: float, latitude: float,
                    longitude: float, location_name: str, gender: str) -> dict:
    chart = compute_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, gender=gender,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_western(key: str, year: int, month: int, day: int, hour: int,
                    minute: int, timezone: float, latitude: float,
                    longitude: float, location_name: str,
                    sidereal: bool) -> dict:
    chart = compute_western_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, sidereal=sidereal,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_vedic(key: str, year: int, month: int, day: int, hour: int,
                  minute: int, timezone: float, latitude: float,
                  longitude: float, location_name: str) -> dict:
    chart = compute_vedic_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_thai(key: str, year: int, month: int, day: int, hour: int,
                 minute: int, timezone: float, latitude: float,
                 longitude: float, location_name: str) -> dict:
    chart = compute_thai_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_kabbalistic(key: str, year: int, month: int, day: int, hour: int,
                        minute: int, timezone: float, latitude: float,
                        longitude: float, location_name: str) -> dict:
    chart = compute_kabbalistic_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_arabic(key: str, year: int, month: int, day: int, hour: int,
                   minute: int, timezone: float, latitude: float,
                   longitude: float, location_name: str) -> dict:
    chart = compute_arabic_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_maya(key: str, year: int, month: int, day: int, hour: int,
                 minute: int, timezone: float, latitude: float,
                 longitude: float, location_name: str) -> dict:
    chart = compute_maya_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_ziwei(key: str, year: int, month: int, day: int, hour: int,
                  minute: int, timezone: float, latitude: float,
                  longitude: float, location_name: str) -> dict:
    chart = compute_ziwei_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_mahabote(key: str, year: int, month: int, day: int, hour: int,
                     minute: int, timezone: float, latitude: float,
                     longitude: float, location_name: str) -> dict:
    chart = compute_mahabote_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_decans(key: str, year: int, month: int, day: int, hour: int,
                   minute: int, timezone: float, latitude: float,
                   longitude: float, location_name: str) -> dict:
    chart = compute_decan_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_nadi(key: str, year: int, month: int, day: int, hour: int,
                 minute: int, timezone: float, latitude: float,
                 longitude: float, location_name: str) -> dict:
    chart = compute_nadi_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_zurkhai(key: str, year: int, month: int, day: int, hour: int,
                    minute: int, timezone: float, latitude: float,
                    longitude: float, location_name: str) -> dict:
    chart = compute_zurkhai_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_damo(key: str, year: int, month: int, day: int, hour: int,
                 minute: int, timezone: float, latitude: float,
                 longitude: float, location_name: str,
                 gender: str) -> dict:
    chart = compute_damo_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, gender=gender,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_huangji(
    key: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str,
    reference_year: Optional[int] = None,
) -> dict:
    chart = compute_huangji_pan(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        reference_year=reference_year,
        include_cross_system=True,
    )
    if hasattr(chart, "to_dict"):
        return _make_serializable(chart.to_dict())
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_liuren(key: str, year: int, month: int, day: int, hour: int,
                   minute: int, timezone: float, latitude: float,
                   longitude: float, location_name: str) -> dict:
    chart = compute_liuren_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_taiyi(key: str, year: int, month: int, day: int, hour: int,
                  minute: int, timezone: float, latitude: float,
                  longitude: float, location_name: str,
                  gender: str) -> dict:
    chart = compute_taiyi_chart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        gender=gender,
    )
    return _chart_to_dict(chart)


@lru_cache(maxsize=256)
def _cached_bazi(key: str, year: int, month: int, day: int, hour: int,
                 minute: int, timezone: float, latitude: float,
                 longitude: float, location_name: str,
                 gender: str, reference_date_iso: str) -> dict:
    ref_date = date.fromisoformat(reference_date_iso)
    chart = compute_bazi(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, gender=gender,
        reference_date=ref_date,
    )
    return _chart_to_dict(chart)


# Hellenistic depends on a WesternChart object, so handle specially.
def _compute_hellenistic(params: BirthParams,
                         current_year: Optional[int]) -> dict:
    """Compute Hellenistic chart (requires a Western chart first)."""
    w_chart = compute_western_chart(
        year=params.year, month=params.month, day=params.day,
        hour=params.hour, minute=params.minute, timezone=params.timezone,
        latitude=params.latitude, longitude=params.longitude,
        location_name=params.location_name,
    )
    cy = current_year if current_year is not None else datetime.now().year
    h_chart = compute_hellenistic_chart(
        w_chart, birth_year=params.year, current_year=cy,
    )
    return _chart_to_dict(h_chart)


# ---------------------------------------------------------------------------
#  Internal helpers for calling cached functions with BirthParams
# ---------------------------------------------------------------------------

def _base_kwargs(p: BirthParams) -> dict:
    """Extract the 9 common kwargs from a BirthParams model."""
    return dict(
        year=p.year, month=p.month, day=p.day,
        hour=p.hour, minute=p.minute, timezone=p.timezone,
        latitude=p.latitude, longitude=p.longitude,
        location_name=p.location_name,
    )


# =========================================================================
#  Individual system endpoints
# =========================================================================


@app.post("/api/chinese", response_model=ChartResponse, tags=["Systems"])
async def chinese_chart(params: ChineseParams) -> ChartResponse:
    """Compute a Chinese 七政四餘 chart."""
    try:
        key = _cache_key(params, gender=params.gender)
        data = _cached_chinese(key, **_base_kwargs(params), gender=params.gender)
        return ChartResponse(system="chinese", data=data)
    except Exception as exc:
        logger.exception("Chinese chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/western", response_model=ChartResponse, tags=["Systems"])
async def western_chart(params: WesternParams) -> ChartResponse:
    """Compute a Western astrology chart (tropical or sidereal)."""
    try:
        key = _cache_key(params, sidereal=params.sidereal)
        data = _cached_western(
            key, **_base_kwargs(params), sidereal=params.sidereal,
        )
        return ChartResponse(system="western", data=data)
    except Exception as exc:
        logger.exception("Western chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/vedic", response_model=ChartResponse, tags=["Systems"])
async def vedic_chart(params: BirthParams) -> ChartResponse:
    """Compute a Vedic (Jyotish) chart."""
    try:
        key = _cache_key(params)
        data = _cached_vedic(key, **_base_kwargs(params))
        return ChartResponse(system="vedic", data=data)
    except Exception as exc:
        logger.exception("Vedic chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/thai", response_model=ChartResponse, tags=["Systems"])
async def thai_chart(params: BirthParams) -> ChartResponse:
    """Compute a Thai astrology chart."""
    try:
        key = _cache_key(params)
        data = _cached_thai(key, **_base_kwargs(params))
        return ChartResponse(system="thai", data=data)
    except Exception as exc:
        logger.exception("Thai chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/kabbalistic", response_model=ChartResponse, tags=["Systems"])
async def kabbalistic_chart(params: BirthParams) -> ChartResponse:
    """Compute a Kabbalistic astrology chart."""
    try:
        key = _cache_key(params)
        data = _cached_kabbalistic(key, **_base_kwargs(params))
        return ChartResponse(system="kabbalistic", data=data)
    except Exception as exc:
        logger.exception("Kabbalistic chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/arabic", response_model=ChartResponse, tags=["Systems"])
async def arabic_chart(params: BirthParams) -> ChartResponse:
    """Compute an Arabic/Islamic astrology chart."""
    try:
        key = _cache_key(params)
        data = _cached_arabic(key, **_base_kwargs(params))
        return ChartResponse(system="arabic", data=data)
    except Exception as exc:
        logger.exception("Arabic chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/picatrix/talisman", response_model=ChartResponse, tags=["Systems"])
async def picatrix_talisman_chart(params: PicatrixTalismanParams) -> ChartResponse:
    """Generate a Picatrix talismanic election + blueprint payload."""
    try:
        data = generate_picatrix_talisman(
            purpose=params.purpose,
            year=params.year,
            month=params.month,
            day=params.day,
            hour=params.hour,
            minute=params.minute,
            timezone_offset=params.timezone,
            latitude=params.latitude,
            longitude=params.longitude,
            location_name=params.location_name,
            days_ahead=params.days_ahead,
            include_harmful=params.include_harmful,
        )
        return ChartResponse(system="picatrix_talisman", data=_chart_to_dict(data))
    except Exception as exc:
        logger.exception("Picatrix talisman computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/maya", response_model=ChartResponse, tags=["Systems"])
async def maya_chart(params: BirthParams) -> ChartResponse:
    """Compute a Mayan astrology chart."""
    try:
        key = _cache_key(params)
        data = _cached_maya(key, **_base_kwargs(params))
        return ChartResponse(system="maya", data=data)
    except Exception as exc:
        logger.exception("Mayan chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/ziwei", response_model=ChartResponse, tags=["Systems"])
async def ziwei_chart(params: BirthParams) -> ChartResponse:
    """Compute a Zi Wei Dou Shu (紫微斗數) chart."""
    try:
        key = _cache_key(params)
        data = _cached_ziwei(key, **_base_kwargs(params))
        return ChartResponse(system="ziwei", data=data)
    except Exception as exc:
        logger.exception("Zi Wei chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/mahabote", response_model=ChartResponse, tags=["Systems"])
async def mahabote_chart(params: BirthParams) -> ChartResponse:
    """Compute a Myanmar Mahabote chart."""
    try:
        key = _cache_key(params)
        data = _cached_mahabote(key, **_base_kwargs(params))
        return ChartResponse(system="mahabote", data=data)
    except Exception as exc:
        logger.exception("Mahabote chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/decans", response_model=ChartResponse, tags=["Systems"])
async def decans_chart(params: BirthParams) -> ChartResponse:
    """Compute an Egyptian Decans chart."""
    try:
        key = _cache_key(params)
        data = _cached_decans(key, **_base_kwargs(params))
        return ChartResponse(system="decans", data=data)
    except Exception as exc:
        logger.exception("Decans chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/nadi", response_model=ChartResponse, tags=["Systems"])
async def nadi_chart(params: BirthParams) -> ChartResponse:
    """Compute a Nadi Jyotish chart."""
    try:
        key = _cache_key(params)
        data = _cached_nadi(key, **_base_kwargs(params))
        return ChartResponse(system="nadi", data=data)
    except Exception as exc:
        logger.exception("Nadi chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/zurkhai", response_model=ChartResponse, tags=["Systems"])
async def zurkhai_chart(params: BirthParams) -> ChartResponse:
    """Compute a Mongolian Zurkhai chart."""
    try:
        key = _cache_key(params)
        data = _cached_zurkhai(key, **_base_kwargs(params))
        return ChartResponse(system="zurkhai", data=data)
    except Exception as exc:
        logger.exception("Zurkhai chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/damo", response_model=ChartResponse, tags=["Systems"])
async def damo_chart(params: ChineseParams) -> ChartResponse:
    """Compute a Damo One Palm Scripture chart (達摩一掌經)."""
    try:
        key = _cache_key(params, gender=params.gender)
        kwargs = _base_kwargs(params)
        kwargs["gender"] = params.gender
        data = _cached_damo(key, **kwargs)
        return ChartResponse(system="damo", data=data)
    except Exception as exc:
        logger.exception("Damo One Palm chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/huangji", response_model=ChartResponse, tags=["Systems"])
async def huangji_chart(params: HuangjiParams) -> ChartResponse:
    """Compute a Huangji Jingshi chart (皇極經世)."""
    try:
        key = _cache_key(params, reference_year=params.reference_year)
        data = _cached_huangji(
            key,
            **_base_kwargs(params),
            reference_year=params.reference_year,
        )
        return ChartResponse(system="huangji", data=data)
    except Exception as exc:
        logger.exception("Huangji chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/hellenistic", response_model=ChartResponse, tags=["Systems"])
async def hellenistic_chart(params: HellenisticParams) -> ChartResponse:
    """Compute a Hellenistic Greek astrology chart (derived from Western)."""
    try:
        data = _compute_hellenistic(params, params.current_year)
        return ChartResponse(system="hellenistic", data=data)
    except Exception as exc:
        logger.exception("Hellenistic chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/hellenistic/profections", response_model=ChartResponse, tags=["Hellenistic"])
async def hellenistic_profections(params: ProfectionsParams) -> ChartResponse:
    """Compute Annual (and optionally Monthly) Profections.

    年度守護星（Annual Profections）API。

    Returns a full profection table from birth up to *num_years*, plus an
    optional monthly breakdown for the current year.  All periods include
    house-from-ASC, Lord of the Year, element colour, and bilingual themes.
    """
    try:
        from datetime import date as _date

        target = _date.fromisoformat(params.target_date) if params.target_date else _date.today()
        current_age = target.year - params.birth_year

        annual = compute_profections_table(
            asc_lon=params.asc_lon,
            birth_year=params.birth_year,
            num_years=params.num_years,
            current_age=current_age,
        )

        result: dict[str, Any] = {
            "annual": [r.to_dict() for r in annual],
            "current": next((r.to_dict() for r in annual if r.is_current), None),
        }

        if params.include_monthly:
            monthly = compute_monthly_profections(
                asc_lon=params.asc_lon,
                birth_year=params.birth_year,
                birth_month=params.birth_month,
                birth_day=params.birth_day,
                target_date=target,
                num_years=max(3, current_age + 1),
            )
            result["monthly"] = [m.to_dict() for m in monthly]
            result["current_month"] = next((m.to_dict() for m in monthly if m.is_current), None)

        return ChartResponse(system="hellenistic_profections", data=result)
    except Exception as exc:
        logger.exception("Profections computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/hellenistic/zodiacal-releasing", response_model=ChartResponse, tags=["Hellenistic"])
async def hellenistic_zodiacal_releasing(params: ZodiacalReleasingParams) -> ChartResponse:
    """Compute Zodiacal Releasing (L1 / L2 / L3) from a Lot longitude.

    黃道釋放（Zodiacal Releasing）API，支援 L1/L2/L3 層級，
    可從幸運點（Fortune）或精神點（Spirit）起算。

    - Automatically applies the Valens Spirit-Fortune same-sign rule when
      ``apply_same_sign_rule=true`` and ``source="spirit"``.
    - Returns nested period data with ``is_current``, ``is_peak`` (angular
      houses 1, 4, 7, 10 from the Lot), and ``is_loosening`` flags.
    """
    try:
        import swisseph as _swe

        target_jd = params.target_jd
        if target_jd is None:
            from datetime import date as _date
            td = _date.today()
            target_jd = _swe.julday(td.year, td.month, td.day)

        fortune_lon = params.fortune_lon
        spirit_lon = params.spirit_lon

        if params.apply_same_sign_rule:
            fortune_lon, spirit_lon = apply_spirit_fortune_rule(fortune_lon, spirit_lon)

        lot_lon = fortune_lon if params.source == "fortune" else spirit_lon

        l1_periods = compute_zodiacal_releasing_full(
            lot_lon=lot_lon,
            birth_jd=params.birth_jd,
            target_jd=target_jd,
            source=params.source,
            max_l1=params.max_l1,
        )

        current = get_current_periods(l1_periods)

        return ChartResponse(
            system="hellenistic_zodiacal_releasing",
            data={
                "source": params.source,
                "lot_lon": lot_lon,
                "fortune_lon_used": fortune_lon,
                "spirit_lon_used": spirit_lon,
                "same_sign_rule_applied": params.apply_same_sign_rule,
                "periods": [p.to_dict(include_subs=True) for p in l1_periods],
                "current": {
                    k: v.to_dict(include_subs=False) if v else None
                    for k, v in current.items()
                },
            },
        )
    except Exception as exc:
        logger.exception("Zodiacal Releasing computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/liuren", response_model=ChartResponse, tags=["Systems"])
async def liuren_chart(params: BirthParams) -> ChartResponse:
    """Compute a Da Liu Ren chart (大六壬)."""
    try:
        key = _cache_key(params)
        data = _cached_liuren(key, **_base_kwargs(params))
        return ChartResponse(system="liuren", data=data)
    except Exception as exc:
        logger.exception("Da Liu Ren chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/taiyi", response_model=ChartResponse, tags=["Systems"])
async def taiyi_chart(params: TaiyiParams) -> ChartResponse:
    """Compute a Taiyi Life Method chart (太乙命法)."""
    try:
        key = _cache_key(params, gender=params.gender)
        kwargs = _base_kwargs(params)
        kwargs["gender"] = params.gender
        data = _cached_taiyi(key, **kwargs)
        return ChartResponse(system="taiyi", data=data)
    except Exception as exc:
        logger.exception("Taiyi Life Method chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/bazi", response_model=ChartResponse, tags=["Systems"])
async def bazi_chart(params: ChineseParams) -> ChartResponse:
    """Compute a traditional Ziping Bazi (子平八字) chart.

    Strictly follows classical Ziping method (子平正宗) as described in:
    - 淵海子平 (Yuanhai Ziping)
    - 子平真詮 (Ziping Zhenquan)
    - 三命通會 (Sanming Tonghui)
    - 滴天髓 (Ditianshui)

    Returns the full BaziChart including four pillars, ten gods, day master
    strength, pattern (格局), use god (用神), great fortune cycles (大運),
    current year fortune (流年), and shen sha (神煞).
    """
    try:
        today_iso = date.today().isoformat()
        key = _cache_key(params, gender=params.gender, reference_date=today_iso)
        kwargs = _base_kwargs(params)
        kwargs["gender"] = params.gender
        kwargs["reference_date_iso"] = today_iso
        data = _cached_bazi(key, **kwargs)
        return ChartResponse(system="bazi", data=data)
    except Exception as exc:
        logger.exception("Ziping Bazi chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


class HoraryParams(BirthParams):
    """Parameters for Traditional Horary Astrology chart."""

    question_text: str = Field(
        default="",
        description="The horary question being asked",
    )
    question_type: str = Field(
        default="general",
        description=(
            "Question type: 'marriage', 'career', 'wealth', 'lost_item', "
            "'illness', 'travel', 'missing_person', 'property', 'general'"
        ),
    )
    tradition: str = Field(
        default="western",
        description="Tradition: 'western' (Lilly/Bonatti) or 'vedic' (Prashna Marga)",
    )
    prashna_number: Optional[int] = Field(
        default=None,
        ge=1, le=108,
        description="Optional 1-108 querent number for Vedic Prashna tradition",
    )


@app.post("/api/horary", response_model=ChartResponse, tags=["Systems"])
async def horary_chart(params: HoraryParams) -> ChartResponse:
    """Compute a Traditional Horary chart.

    Supports both Western (Lilly/Bonatti) and Vedic (Prashna Marga) traditions.
    The ``tradition`` field selects the system; ``question_type`` and
    ``question_text`` are used for the judgment.

    Western tradition applies strict Lilly/Bonatti rules including:
    - Essential and Accidental Dignities
    - Applying/separating aspects, Reception
    - Void of Course Moon (with Lilly's exception signs)
    - Translation and Collection of Light
    - Strictures Against Judgment

    Vedic Prashna follows Prasna Marga with Arudha Lagna computation.
    """
    try:
        kw = _base_kwargs(params)
        if params.tradition == "vedic":
            chart = compute_vedic_prashna(
                question_text=params.question_text,
                question_type=params.question_type,
                prashna_number=params.prashna_number,
                **kw,
            )
        else:
            chart = compute_western_horary(
                question_text=params.question_text,
                question_type=params.question_type,
                **kw,
            )
        return ChartResponse(system=f"horary_{params.tradition}", data=_chart_to_dict(chart))
    except Exception as exc:
        logger.exception("Horary chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


class SportsHoraryParams(BirthParams):
    """Parameters for Sports Astrology horary analysis."""

    match_name: str = Field(default="Sports Match", description="Match title")
    team1: str = Field(..., description="Home team / team 1")
    team2: str = Field(..., description="Away team / team 2")
    preferred_team: Optional[str] = Field(
        default=None,
        description="Preferred side mapped to querent side (optional)",
    )
    question_text: Optional[str] = Field(
        default=None,
        description="Optional explicit horary question",
    )


@app.post("/api/sports-horary", response_model=ChartResponse, tags=["Systems"])
async def sports_horary_chart(params: SportsHoraryParams) -> ChartResponse:
    """Compute Frawley-style sports horary analysis with probabilistic output."""
    try:
        result = analyze_sports_horary(
            match_name=params.match_name,
            team1=params.team1,
            team2=params.team2,
            year=params.year,
            month=params.month,
            day=params.day,
            hour=params.hour,
            minute=params.minute,
            timezone=params.timezone,
            latitude=params.latitude,
            longitude=params.longitude,
            location_name=params.location_name,
            preferred_team=params.preferred_team,
            question_text=params.question_text,
        )
        return ChartResponse(system="sports_astrology", data=_chart_to_dict(result))
    except Exception as exc:
        logger.exception("Sports horary computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/esoteric", response_model=ChartResponse, tags=["Systems"])
async def esoteric_chart(params: BirthParams) -> ChartResponse:
    """Compute an Esoteric Astrology chart using Alice Bailey's Seven Rays system.

    Performs:
    - Seven Rays analysis (Rays 1–7 with full Bailey data)
    - Esoteric Rulers for all 12 signs (exoteric, esoteric, hierarchical)
    - Soul Ray indicator (via esoteric rulers, ASC, Sun sign, transpersonal planets)
    - Personality Ray indicator (via exoteric rulers, Moon, personal planets)
    - Ray distribution tally across all chart factors
    - Ray interaction analysis (Soul–Personality ray relationship)

    Note: Soul Ray and Personality Ray values are indicative tendency indicators,
    not mechanically deterministic. Alice Bailey emphasises that spiritual
    discernment is required for final Ray determination.

    Ref: Bailey, *Esoteric Astrology* (Lucis Publishing, 1951), pp. 3–65.
    """
    try:
        kw = _base_kwargs(params)
        chart = compute_esoteric_chart(**kw)
        return ChartResponse(system="esoteric", data=_chart_to_dict(chart))
    except Exception as exc:
        logger.exception("Esoteric Astrology chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


class ElectionalParams(BirthParams):
    """Parameters for Electional Astrology / Vedic Muhurta."""

    tradition: str = Field(
        default="western",
        description="Tradition: 'western' (Lilly/Bonatti) or 'vedic' (Muhurta Chintamani)",
    )
    activity_type: str = Field(
        default="important_meeting",
        description=(
            "Activity type: 'marriage', 'business_opening', 'contract_signing', "
            "'relocation', 'travel', 'surgery', 'property_purchase', "
            "'litigation', 'important_meeting'"
        ),
    )


@app.post("/api/electional", response_model=ChartResponse, tags=["Systems"])
async def electional_chart(params: ElectionalParams) -> ChartResponse:
    """Compute an Electional Astrology or Vedic Muhurta chart.

    Supports both Western Electional (Lilly/Bonatti) and Vedic Muhurta
    (Muhurta Chintamani / Kalaprakashika / BPHS) traditions.

    Western Electional (``tradition='western'``):
    - Planetary Hours (Chaldean order, Lilly CA p. 483)
    - Moon Void of Course, Via Combusta, applying aspects, phase
    - Essential dignities: domicile, exaltation, detriment, fall
    - Activity-specific rules for 9 event types

    Vedic Muhurta (``tradition='vedic'``):
    - Panchanga: Tithi, Vara, Nakshatra, Yoga, Karana
    - Gandanta detection (water/fire sign junctions)
    - Vishti Karana (Bhadra) detection
    - Lagna suitability, Jupiter/Venus visibility for marriage

    Sources:
    - Lilly, *Christian Astrology* (1647); Bonatti, *Liber Astronomiae* (~1277)
    - *Muhurta Chintamani*; *Kalaprakashika*; *Brihat Parashara Hora Shastra*
    """
    try:
        kw = _base_kwargs(params)
        if params.tradition == "vedic":
            chart = compute_vedic_muhurta(activity_type=params.activity_type, **kw)
        else:
            chart = compute_western_electional(activity_type=params.activity_type, **kw)
        return ChartResponse(
            system=f"electional_{params.tradition}",
            data=_chart_to_dict(chart),
        )
    except Exception as exc:
        logger.exception("Electional / Muhurta chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


class HarmonicParams(BirthParams):
    """Parameters for Harmonic Astrology (John Addey)."""

    harmonics: list[int] = Field(
        default_factory=lambda: [1, 2, 3, 4, 5, 7, 9, 12],
        description=(
            "List of harmonic numbers to compute. "
            "Defaults to the standard set: [1, 2, 3, 4, 5, 7, 9, 12]. "
            "Any positive integer is supported."
        ),
    )


@app.post("/api/harmonic", response_model=ChartResponse, tags=["Systems"])
async def harmonic_chart(params: HarmonicParams) -> ChartResponse:
    """Compute Harmonic Astrology charts following John Addey's method.

    Implements:
    - Nth Harmonic Chart: H_N(λ) = (N × λ) mod 360°  (Addey 1976, Ch. 2)
    - Conjunctions in the harmonic chart (= natal N-th aspect within orb)
    - Multi-harmonic analysis (Hamblin 1983: planetary emphasis across harmonics)

    Supported harmonics (default): H1 H2 H3 H4 H5 H7 H9 H12
    Custom harmonics: pass any list of positive integers.

    Sources:
    - Addey, *Harmonics in Astrology* (L.N. Fowler, 1976)
    - Hamblin, *Harmonic Charts* (Aquarian Press, 1983)
    """
    try:
        kw = _base_kwargs(params)
        result = compute_multi_harmonic(harmonics=params.harmonics, **kw)
        # Serialize to dict
        data: dict = {
            "harmonics": {},
            "multi_emphasis": result.multi_emphasis,
            "natal_planets": [
                {
                    "key": p.key,
                    "name_en": p.name_en,
                    "name_zh": p.name_zh,
                    "symbol": p.symbol,
                    "natal_longitude": round(p.natal_longitude, 4),
                    "sign": p.sign,
                    "sign_degree": round(p.sign_degree, 4),
                    "retrograde": p.retrograde,
                }
                for p in result.natal_planets
            ],
        }
        for n, chart in result.harmonic_charts.items():
            data["harmonics"][str(n)] = {
                "harmonic_number": n,
                "name_en": chart.name_en,
                "name_zh": chart.name_zh,
                "theme_en": chart.theme_en,
                "theme_zh": chart.theme_zh,
                "conjunction_orb": chart.conjunction_orb,
                "planets": [
                    {
                        "key": hp.key,
                        "symbol": hp.symbol,
                        "harmonic_longitude": round(hp.harmonic_longitude, 4),
                        "natal_longitude": round(hp.natal_longitude, 4),
                        "sign": hp.sign,
                        "sign_degree": round(hp.sign_degree, 4),
                    }
                    for hp in chart.harmonic_planets
                ],
                "conjunctions": [
                    {
                        "planet_a": c.planet_a,
                        "planet_b": c.planet_b,
                        "harmonic_orb": round(c.harmonic_orb, 4),
                        "natal_aspect": round(c.natal_aspect, 4),
                        "natal_aspect_name": c.natal_aspect_name,
                        "meaning_zh": c.meaning_zh,
                        "meaning_en": c.meaning_en,
                    }
                    for c in chart.conjunctions
                ],
            }
        return ChartResponse(system="harmonic", data=data)
    except Exception as exc:
        logger.exception("Harmonic Astrology chart computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


class PrimaryDirectionsParams(BirthParams):
    """Parameters for Classical Primary Directions."""

    method: str = Field(
        default="mundo",
        description=(
            "Direction method: 'mundo' (Placidus Semi-Arc, default) or "
            "'zodiacal' (Ptolemy Oblique Ascension)."
        ),
    )
    time_key: str = Field(
        default="naibod",
        description=(
            "Time conversion key: 'naibod' (0.98563°/yr, default), "
            "'ptolemy' (1°/yr), or 'solar_arc'."
        ),
    )
    max_age: float = Field(
        default=90.0,
        description="Maximum age in years to compute directions for.",
    )
    significators: list[str] = Field(
        default_factory=lambda: ["AS", "MC", "SU", "MO"],
        description="Points to direct (e.g. AS, MC, SU, MO, VE, MA).",
    )
    promittors: list[str] = Field(
        default_factory=lambda: ["SU", "MO", "ME", "VE", "MA", "JU", "SA", "AS", "MC"],
        description="Natal points to be aspected.",
    )
    include_aspects: list[str] = Field(
        default_factory=lambda: ["CNJ", "OPP", "SQR", "TRI", "SXT"],
        description="Aspect keys: CNJ OPP SQR TRI SXT PAR CPAR.",
    )
    include_converse: bool = Field(
        default=True,
        description="If true, also compute converse (backward) directions.",
    )


@app.post("/api/primary_directions", response_model=ChartResponse, tags=["Systems"])
async def primary_directions_chart(params: PrimaryDirectionsParams) -> ChartResponse:
    """Compute Classical Primary Directions following Ptolemy and Placidus.

    Implements two canonical methods:

    - **Mundo / Placidus Semi-Arc** (method="mundo", default):
      Uses the Placidus proportional pole method for each significator.
      Ref: Placidus de Titis, *Primum Mobile* (1657).

    - **Zodiacal / Ptolemy OA** (method="zodiacal"):
      Uses Oblique Ascension differences in the horizon system.
      Ref: Ptolemy, *Tetrabiblos* (c. 150 CE), Book III.

    Time keys:
      - naibod    — 1 yr = 0.98563° (Naibod 1560, most traditional)
      - ptolemy   — 1 yr = 1.00000°
      - solar_arc — 1 yr = Sun's actual daily motion at birth

    Returns directions sorted by age (years from birth).
    """
    try:
        kw = _base_kwargs(params)
        result = compute_primary_directions(
            method=params.method,
            time_key=params.time_key,
            max_age=params.max_age,
            significators=params.significators,
            promittors=params.promittors,
            include_aspects=params.include_aspects,
            include_converse=params.include_converse,
            **kw,
        )
        data: dict = {
            "method": result.method,
            "time_key": result.time_key,
            "max_age": result.max_age,
            "ramc": round(result.ramc, 4),
            "obliquity": round(result.obliquity, 6),
            "natal_points": [
                {
                    "key": p.key,
                    "name_en": p.name_en,
                    "name_zh": p.name_zh,
                    "symbol": p.symbol,
                    "longitude": round(p.longitude, 4),
                    "sign": p.sign,
                    "sign_degree": round(p.sign_degree, 4),
                    "ra": round(p.ra, 4),
                    "dec": round(p.dec, 4),
                    "oa": round(p.oa, 4),
                    "sa_diurnal": round(p.sa_diurnal, 4),
                    "above_horizon": p.above_horizon,
                    "retrograde": p.retrograde,
                }
                for p in result.natal_points
            ],
            "directions": [
                {
                    "significator": d.significator_key,
                    "promittor": d.promittor_key,
                    "aspect": d.aspect_key,
                    "converse": d.converse,
                    "arc": round(d.arc, 4),
                    "years": round(d.years, 3),
                    "event_date": d.event_date.isoformat(),
                    "label_en": d.direction_label_en,
                    "label_zh": d.direction_label_zh,
                    "nature_zh": d.nature_zh,
                    "nature_en": d.nature_en,
                }
                for d in result.directions
            ],
        }
        return ChartResponse(system="primary_directions", data=data)
    except Exception as exc:
        logger.exception("Primary Directions computation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# Map of system name → (cached_fn, extra_params_builder)
_SYSTEMS_BASIC: list[tuple[str, Any]] = [
    ("huangji", _cached_huangji),
    ("vedic", _cached_vedic),
    ("thai", _cached_thai),
    ("kabbalistic", _cached_kabbalistic),
    ("arabic", _cached_arabic),
    ("maya", _cached_maya),
    ("ziwei", _cached_ziwei),
    ("mahabote", _cached_mahabote),
    ("decans", _cached_decans),
    ("nadi", _cached_nadi),
    ("zurkhai", _cached_zurkhai),
    ("liuren", _cached_liuren),
]

# Damo requires gender parameter and is handled separately in compute_all
# endpoint rather than being included in _SYSTEMS_BASIC.


@app.post("/api/compute", response_model=ComputeAllResponse, tags=["Aggregate"])
async def compute_all(params: ComputeAllParams) -> ComputeAllResponse:
    """Compute charts for **all** astrology systems in a single request.

    Individual system failures are captured in the per-system ``error``
    field; the overall response still returns HTTP 200 so that partial
    results are available.
    """
    charts: dict[str, ChartResponse] = {}
    kw = _base_kwargs(params)

    # --- Chinese (needs gender) ---
    try:
        key = _cache_key(params, gender=params.gender)
        data = _cached_chinese(key, **kw, gender=params.gender)
        charts["chinese"] = ChartResponse(system="chinese", data=data)
    except Exception as exc:
        logger.exception("Chinese chart failed in /api/compute")
        charts["chinese"] = ChartResponse(
            system="chinese", ok=False, error=str(exc),
        )

    # --- Western (needs sidereal) ---
    try:
        key = _cache_key(params, sidereal=params.sidereal)
        data = _cached_western(key, **kw, sidereal=params.sidereal)
        charts["western"] = ChartResponse(system="western", data=data)
    except Exception as exc:
        logger.exception("Western chart failed in /api/compute")
        charts["western"] = ChartResponse(
            system="western", ok=False, error=str(exc),
        )

    # --- Basic systems (common params only) ---
    for name, fn in _SYSTEMS_BASIC:
        try:
            key = _cache_key(params)
            data = fn(key, **kw)
            charts[name] = ChartResponse(system=name, data=data)
        except Exception as exc:
            logger.exception("%s chart failed in /api/compute", name)
            charts[name] = ChartResponse(
                system=name, ok=False, error=str(exc),
            )

    # --- Hellenistic (derived from Western) ---
    try:
        data = _compute_hellenistic(params, params.current_year)
        charts["hellenistic"] = ChartResponse(system="hellenistic", data=data)
    except Exception as exc:
        logger.exception("Hellenistic chart failed in /api/compute")
        charts["hellenistic"] = ChartResponse(
            system="hellenistic", ok=False, error=str(exc),
        )

    # --- Damo (needs gender) ---
    try:
        key = _cache_key(params, gender=params.gender)
        data = _cached_damo(key, **kw, gender=params.gender)
        charts["damo"] = ChartResponse(system="damo", data=data)
    except Exception as exc:
        logger.exception("Damo chart failed in /api/compute")
        charts["damo"] = ChartResponse(
            system="damo", ok=False, error=str(exc),
        )

    return ComputeAllResponse(charts=charts)


# =========================================================================
#  Health / info endpoints
# =========================================================================


@app.get("/api/health", tags=["Meta"])
async def health() -> dict[str, str]:
    """Simple liveness check."""
    return {"status": "ok"}


@app.get("/api/systems", tags=["Meta"])
async def list_systems() -> dict[str, list[str]]:
    """List all supported astrology systems."""
    return {
        "systems": [
            "chinese",
            "western",
            "huangji",
            "vedic",
            "thai",
            "kabbalistic",
            "arabic",
            "maya",
            "ziwei",
            "mahabote",
            "decans",
            "nadi",
            "zurkhai",
            "hellenistic",
            "damo",
            "liuren",
            "taiyi",
            "bazi",
            "horary_western",
            "horary_vedic",
            "astronomical_geomancy",
        ]
    }


# =========================================================================
#  Astronomical Geomancy endpoint
# =========================================================================


class GeomancyParams(BaseModel):
    """Parameters for the Astronomical Geomancy endpoint."""

    question: str = Field(default="", description="The querent's question")
    question_type: str = Field(
        default="custom",
        description=(
            "Question category key: life, health, wealth, marriage, career, "
            "children, journey, religion, enemy, death, or custom"
        ),
    )
    seed_mode: str = Field(
        default="random",
        description="Seed mode: 'random', 'time_seed', or 'manual'",
    )
    manual_seed: Optional[int] = Field(
        default=None,
        description="Deterministic seed (used when seed_mode='manual')",
    )
    lang: str = Field(default="zh", description="Output language: 'zh' or 'en'")


@app.post("/api/astronomical_geomancy", response_model=ChartResponse, tags=["Divination"])
async def astronomical_geomancy(params: GeomancyParams) -> ChartResponse:
    """
    Cast an Astronomical Geomancy chart per Gerardus Cremonensis (12th c.).

    Generates 4 mother figures, assigns zodiac signs to 12 houses,
    and places 7 classical planets + Caput/Cauda Draconis in houses.
    Returns the full chart data and an AI-ready text prompt.
    """
    try:
        chart = compute_geomancy_chart(
            question=params.question,
            question_type=params.question_type,
            seed_mode=params.seed_mode,
            manual_seed=params.manual_seed,
        )
        chart_dict = chart.to_json()
        chart_dict["prompt"] = format_geomancy_for_prompt(chart, lang=params.lang)
        return ChartResponse(system="astronomical_geomancy", data=chart_dict)
    except Exception as exc:
        logger.exception("Astronomical Geomancy chart failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
