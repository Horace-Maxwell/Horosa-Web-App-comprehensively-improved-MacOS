"""
astro/etruscan/models.py — Data models for the Etruscan Astrology module
=========================================================================

Defines frozen and mutable dataclasses representing:
  • TemplumRegion      — one of the 16 Etruscan celestial/hepatic sectors
  • EtruscanPlanetPosition — a single planet's computed position in the Templum
  • EtruscanChart      — the complete chart result returned by the calculator

All dataclasses use type hints throughout and include docstrings in both
English and Chinese as appropriate to the KinAstro project convention.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# TemplumRegion — one of the 16 Etruscan sky sectors
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TemplumRegion:
    """One of the 16 Templum sectors of the Etruscan celestial division.

    每個 Templum 區域代表天宮16分法中的一個22.5°扇形，
    從正北(0°)順時針排列，與伊特魯里亞青銅肝臟（皮亞琴察肝臟）
    外緣的銘文分區對應。

    Attributes:
        region:           Sector number 1–16 (1 = NNE, clockwise).
        name_etruscan:    Original Etruscan deity name for this sector.
        name_en:          English name / description.
        name_zh:          Chinese name.
        deity_zh:         Chinese description of the presiding deity.
        deity_en:         English description of the presiding deity.
        nature:           Auspicious quality: "favorable" | "unfavorable" | "neutral".
        nature_zh:        Chinese label for nature (吉 / 凶 / 中性).
        azimuth_start:    Start azimuth in degrees (0 = N, clockwise).
        azimuth_end:      End azimuth in degrees.
        color:            Hex colour for rendering this sector.
        interpretation_zh: Brief Chinese divination interpretation.
        interpretation_en: Brief English divination interpretation.
        thunder_type:     Thunderbolt type name for regions linked to lightning
                          divination (None for non-lightning sectors).
    """

    region: int
    name_etruscan: str
    name_en: str
    name_zh: str
    deity_zh: str
    deity_en: str
    nature: str                  # "favorable" | "unfavorable" | "neutral"
    nature_zh: str
    azimuth_start: float
    azimuth_end: float
    color: str
    interpretation_zh: str
    interpretation_en: str
    thunder_type: Optional[str]


# ─────────────────────────────────────────────────────────────────────────────
# EtruscanPlanetPosition — one planet's computed placement
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EtruscanPlanetPosition:
    """A single planet's computed position within the Etruscan Templum system.

    行星位置包含黃道經度、地平座標（方位角/高度角）及所屬的 Templum 區域。

    Attributes:
        planet_id:        pyswisseph planet constant (0=Sun … 6=Saturn).
        planet_name_zh:   Chinese + Etruscan deity name (e.g. "太陽/Usil").
        planet_name_en:   English + Etruscan deity name.
        glyph:            Unicode or emoji glyph for the planet.
        longitude:        Ecliptic longitude in degrees (0–360).
        azimuth:          Horizon azimuth in degrees (0=N, clockwise).
        altitude:         Horizon altitude in degrees (negative = below horizon).
        templum_region:   Which of the 16 Templum regions (1–16).
        is_above_horizon: True if altitude > 0.
        sign:             Western zodiac sign name (e.g. "Taurus").
    """

    planet_id: int
    planet_name_zh: str
    planet_name_en: str
    glyph: str
    longitude: float
    azimuth: float
    altitude: float
    templum_region: int
    is_above_horizon: bool
    sign: str


# ─────────────────────────────────────────────────────────────────────────────
# EtruscanChart — complete chart result
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EtruscanChart:
    """Complete Etruscan astrology chart result.

    完整伊特魯里亞占星命盤，包含行星位置、主導天性、閃電占卜區域及儀式類型。

    Attributes:
        year, month, day, hour, minute:  Input birth/event time (local).
        timezone:         UTC offset in hours.
        latitude:         Observer latitude (degrees; south is negative).
        longitude:        Observer longitude (degrees; west is negative).
        location_name:    Human-readable place name.
        jd_ut:            Julian Day number in Universal Time.
        planet_positions: List of EtruscanPlanetPosition for Sun–Saturn.
        lightning_region: Templum region (1–16) of the Sun (primary lightning zone).
        dominant_nature:  Overall chart nature: "favorable" | "unfavorable" | "neutral".
        ritual_type:      Context of the reading: "birth" | "national" | "personal" | "weather".
    """

    # ── Input parameters ──
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str

    # ── Computed core ──
    jd_ut: float
    planet_positions: list  # list[EtruscanPlanetPosition]
    lightning_region: int
    dominant_nature: str
    ritual_type: str

    # ─────────────────────────────────────────────────────────────────────────
    # Convenience methods
    # ─────────────────────────────────────────────────────────────────────────

    def to_json(self) -> dict:
        """Serialise the chart to a plain JSON-compatible dict.

        行星位置以 dict 形式儲存，其餘欄位直接序列化。
        """
        data = {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "timezone": self.timezone,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_name": self.location_name,
            "jd_ut": self.jd_ut,
            "lightning_region": self.lightning_region,
            "dominant_nature": self.dominant_nature,
            "ritual_type": self.ritual_type,
            "planet_positions": [asdict(p) for p in self.planet_positions],
        }
        return data

    def summary_zh(self) -> str:
        """Return a brief Chinese text summary of the chart.

        中文摘要，包含日期、地點、主導天性及閃電占卜區域。
        """
        nature_label = {"favorable": "吉", "unfavorable": "凶", "neutral": "中性"}.get(
            self.dominant_nature, self.dominant_nature
        )
        lines = [
            f"伊特魯里亞占星命盤 — {self.year}年{self.month}月{self.day}日",
            f"地點：{self.location_name or f'{self.latitude:.2f}°, {self.longitude:.2f}°'}",
            f"儀式類型：{self.ritual_type}",
            f"主導天性：{nature_label}",
            f"閃電占卜區域（太陽所在）：第 {self.lightning_region} 區",
        ]
        for pos in self.planet_positions:
            lines.append(
                f"  {pos.glyph} {pos.planet_name_zh} → 第{pos.templum_region}區 "
                f"({pos.sign}, Az={pos.azimuth:.1f}°)"
            )
        return "\n".join(lines)

    def summary_en(self) -> str:
        """Return a brief English text summary of the chart.

        English summary including date, location, dominant nature and lightning region.
        """
        lines = [
            f"Etruscan Astrology Chart — {self.year}-{self.month:02d}-{self.day:02d}",
            f"Location: {self.location_name or f'{self.latitude:.2f}°, {self.longitude:.2f}°'}",
            f"Ritual type: {self.ritual_type}",
            f"Dominant nature: {self.dominant_nature}",
            f"Lightning region (Sun): Templum {self.lightning_region}",
        ]
        for pos in self.planet_positions:
            lines.append(
                f"  {pos.glyph} {pos.planet_name_en} → Templum {pos.templum_region} "
                f"({pos.sign}, Az={pos.azimuth:.1f}°)"
            )
        return "\n".join(lines)
