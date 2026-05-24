"""Cache key helpers for birth-chart computations.

Use deterministic tuple keys based on birth moment + options.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def _stable_options_hash(options: Mapping[str, Any]) -> str:
    """Hash options dict deterministically (JSON canonical form)."""

    payload = json.dumps(options, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def build_birth_cache_key(
    *,
    system_id: str,
    julian_day_utc: float,
    latitude: float,
    longitude: float,
    timezone: float,
    gender: str,
    options: Mapping[str, Any] | None = None,
    algo_version: str = "v1",
) -> tuple[Any, ...]:
    """Build canonical cache key tuple.

    核心 key: (system_id, julian_day_utc, lat, lon, tz, gender, options_hash, algo_version)
    """

    options_hash = _stable_options_hash(options or {})
    return (
        system_id,
        round(float(julian_day_utc), 8),
        round(float(latitude), 6),
        round(float(longitude), 6),
        round(float(timezone), 4),
        str(gender),
        options_hash,
        algo_version,
    )
