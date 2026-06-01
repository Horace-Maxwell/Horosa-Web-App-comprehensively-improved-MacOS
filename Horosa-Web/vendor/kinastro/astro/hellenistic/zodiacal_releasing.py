"""astro/hellenistic/zodiacal_releasing.py
Zodiacal Releasing (黃道釋放 / Aphesis)

Multi-level Hellenistic time-lord technique releasing from:
  • Lot of Fortune (body, health, material events)
  • Lot of Spirit   (career, mind, active will)

Level hierarchy:
  L1 — Major periods (years)
  L2 — Sub-periods (months within each L1)
  L3 — Sub-sub-periods (days within each L2, computed on demand)

Period lengths follow the planetary minor years:
  Sun 19 · Moon 25 · Mercury 20 · Venus 8 · Mars 15 · Jupiter 12 · Saturn 30

References:
  Vettius Valens, *Anthologies* Book IV.
  Chris Brennan, *Hellenistic Astrology* ch. 19-20.
"""

from __future__ import annotations

import swisseph as swe
from dataclasses import dataclass, field

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_CN = {
    "Aries": "白羊", "Taurus": "金牛", "Gemini": "雙子",
    "Cancer": "巨蟹", "Leo": "獅子", "Virgo": "處女",
    "Libra": "天秤", "Scorpio": "天蠍", "Sagittarius": "射手",
    "Capricorn": "摩羯", "Aquarius": "水瓶", "Pisces": "雙魚",
}

SIGN_GLYPHS = {
    "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
    "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
    "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓",
}

SIGN_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

PLANET_CN = {
    "Sun": "太陽", "Moon": "月亮", "Mercury": "水星",
    "Venus": "金星", "Mars": "火星", "Jupiter": "木星", "Saturn": "土星",
}

PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿",
    "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
}

# Planetary minor years → sign period lengths
# L1 = years, L2 = months, L3 = days (using the same number, different unit)
SIGN_MINOR_YEARS: dict[str, int] = {
    "Aries": 15,        # Mars
    "Taurus": 8,        # Venus
    "Gemini": 20,       # Mercury
    "Cancer": 25,       # Moon
    "Leo": 19,          # Sun
    "Virgo": 20,        # Mercury
    "Libra": 8,         # Venus
    "Scorpio": 15,      # Mars
    "Sagittarius": 12,  # Jupiter
    "Capricorn": 27,    # Saturn — Valens uses 27 for Capricorn (vs 30 for Aquarius;
                        # traditional distinction: Capricorn gets "lesser" Saturn years)
    "Aquarius": 30,     # Saturn — 30 "greater" years assigned to Saturn's airy domicile
    "Pisces": 12,       # Jupiter
}

_JD_PER_YEAR = 365.25
_JD_PER_MONTH = 30.0          # 360-day year / 30-day month (Valens standard)
_JD_PER_DAY = 1.0

# How many JD days around target_jd to expand sub-periods in detail.
# Periods outside this window only compute L1; those inside get L2 and L3.
_NEAR_TARGET_WINDOW_DAYS = 365 * 10


# ─────────────────────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────────────────────

@dataclass
class ZRPeriod:
    """A single Zodiacal Releasing period at any level (L1 / L2 / L3)."""
    level: int                  # 1, 2, or 3
    sign: str
    sign_cn: str
    sign_glyph: str
    ruler: str
    ruler_cn: str
    ruler_glyph: str
    start_jd: float
    end_jd: float
    start_date: str             # ISO date string "YYYY-MM-DD"
    end_date: str
    duration_years: float       # approximate duration in years
    house_from_lot: int         # 1–12 (position relative to Lot's sign)
    is_current: bool            # True if target_jd falls within this period
    is_peak: bool               # True if angular from Lot (houses 1, 4, 7, 10)
    is_loosening: bool          # True if same sign as parent L1 (Loosening of Bonds)
    sub_periods: list["ZRPeriod"] = field(default_factory=list)

    def to_dict(self, include_subs: bool = False) -> dict:
        d = {
            "level": f"L{self.level}",
            "sign": f"{self.sign_glyph} {self.sign}",
            "sign_cn": self.sign_cn,
            "ruler": f"{self.ruler_glyph} {self.ruler}",
            "ruler_cn": f"{self.ruler_glyph} {self.ruler_cn}",
            "start": self.start_date,
            "end": self.end_date,
            "duration": f"{self.duration_years:.2f}y",
            "house_from_lot": self.house_from_lot,
            "is_current": self.is_current,
            "is_peak": self.is_peak,
            "is_loosening": self.is_loosening,
        }
        if include_subs and self.sub_periods:
            d["sub_periods"] = [s.to_dict() for s in self.sub_periods]
        return d


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _jd_to_date(jd: float) -> str:
    y, m, d, _ = swe.revjul(jd)
    return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"


def _sign_of(lon: float) -> str:
    return ZODIAC_SIGNS[int(lon / 30) % 12]


def _degree_in_sign(lon: float) -> float:
    return lon % 30


# ─────────────────────────────────────────────────────────────
# Core Computation
# ─────────────────────────────────────────────────────────────

def _compute_periods(
    start_sign_idx: int,
    lot_sign_idx: int,
    l1_sign_idx: int,
    start_jd: float,
    end_jd: float,
    target_jd: float,
    level: int,
    degree_offset: float,
    jd_per_unit: float,
    max_periods: int,
    compute_sub: bool,
) -> list[ZRPeriod]:
    """Generic period-chain builder for L1 / L2 / L3.

    Parameters
    ----------
    start_sign_idx:
        Index of the sign where this chain starts.
    lot_sign_idx:
        Index of the Lot's sign (for house-from-lot and peak/loosening).
    l1_sign_idx:
        Index of the current L1 sign (for loosening-of-bonds detection).
    start_jd:
        Julian Day when this chain begins.
    end_jd:
        Julian Day when the parent period ends (chain stops here).
    target_jd:
        The target date to mark ``is_current``.
    level:
        1, 2, or 3.
    degree_offset:
        Degrees already elapsed in the starting sign (0–30).
        Creates a proportionally shorter first period.
    jd_per_unit:
        JD units per "minor year" count (_JD_PER_YEAR / _JD_PER_MONTH / _JD_PER_DAY).
    max_periods:
        Maximum number of periods to generate.
    compute_sub:
        Whether to recursively compute L(level+1) sub-periods.
    """
    periods: list[ZRPeriod] = []
    cur_jd = start_jd

    for i in range(max_periods):
        sign_idx = (start_sign_idx + i) % 12
        sign = ZODIAC_SIGNS[sign_idx]
        minor_years = SIGN_MINOR_YEARS[sign]

        # First period may be proportionally shorter
        if i == 0 and degree_offset > 0:
            fraction = (30.0 - degree_offset) / 30.0
            duration_jd = minor_years * jd_per_unit * fraction
        else:
            duration_jd = minor_years * jd_per_unit

        period_end_jd = min(cur_jd + duration_jd, end_jd)
        if cur_jd >= end_jd:
            break

        ruler = SIGN_RULERS[sign]
        house_from_lot = (sign_idx - lot_sign_idx) % 12 + 1
        is_peak = house_from_lot in (1, 4, 7, 10)
        is_loosening = (sign_idx == l1_sign_idx) and (level == 2)
        is_current = cur_jd <= target_jd < period_end_jd

        # Compute sub-periods (L2→L3) only when needed
        sub_periods: list[ZRPeriod] = []
        if compute_sub and level < 3:
            sub_jd_unit = _JD_PER_MONTH if level == 1 else _JD_PER_DAY
            sub_max = 200
            # Only expand sub-periods near target to avoid combinatorial explosion
            near_target = abs(target_jd - cur_jd) < _NEAR_TARGET_WINDOW_DAYS
            if near_target or is_current:
                sub_periods = _compute_periods(
                    start_sign_idx=sign_idx,
                    lot_sign_idx=lot_sign_idx,
                    l1_sign_idx=sign_idx if level == 1 else l1_sign_idx,
                    start_jd=cur_jd,
                    end_jd=period_end_jd,
                    target_jd=target_jd,
                    level=level + 1,
                    degree_offset=degree_offset if i == 0 else 0.0,
                    jd_per_unit=sub_jd_unit,
                    max_periods=sub_max,
                    compute_sub=(level == 1),  # only L1→L2→L3; stop at L3
                )

        periods.append(ZRPeriod(
            level=level,
            sign=sign,
            sign_cn=SIGN_CN[sign],
            sign_glyph=SIGN_GLYPHS[sign],
            ruler=ruler,
            ruler_cn=PLANET_CN.get(ruler, ruler),
            ruler_glyph=PLANET_GLYPHS.get(ruler, ""),
            start_jd=cur_jd,
            end_jd=period_end_jd,
            start_date=_jd_to_date(cur_jd),
            end_date=_jd_to_date(period_end_jd),
            duration_years=(period_end_jd - cur_jd) / _JD_PER_YEAR,
            house_from_lot=house_from_lot,
            is_current=is_current,
            is_peak=is_peak,
            is_loosening=is_loosening,
            sub_periods=sub_periods,
        ))

        cur_jd = period_end_jd
        if cur_jd >= end_jd:
            break

    return periods


def compute_zodiacal_releasing_full(
    lot_lon: float,
    birth_jd: float,
    target_jd: float,
    source: str = "fortune",
    max_l1: int = 25,
) -> list[ZRPeriod]:
    """Compute Zodiacal Releasing from a Lot longitude.

    黃道釋放多層級時主計算

    Parameters
    ----------
    lot_lon:
        Longitude of the releasing Lot (Lot of Fortune or Lot of Spirit).
    birth_jd:
        Julian Day of birth.
    target_jd:
        Target date (usually today) used to mark ``is_current`` periods.
    source:
        ``"fortune"`` or ``"spirit"`` — purely informational label.
    max_l1:
        Maximum number of L1 periods to generate.

    Returns
    -------
    list[ZRPeriod]
        L1 periods, each containing nested L2 sub-periods (and L3 inside the
        L2 periods close to *target_jd*).
    """
    lot_sign_idx = int(lot_lon / 30) % 12
    degree_offset = lot_lon % 30

    # The L1 chain runs from birth until max_l1 periods are computed or
    # we have covered at least 5 years past target_jd.
    far_future_jd = target_jd + 365.25 * 5

    l1_periods = _compute_periods(
        start_sign_idx=lot_sign_idx,
        lot_sign_idx=lot_sign_idx,
        l1_sign_idx=lot_sign_idx,
        start_jd=birth_jd,
        end_jd=birth_jd + max_l1 * 30 * _JD_PER_YEAR,  # generous upper bound
        target_jd=target_jd,
        level=1,
        degree_offset=degree_offset,
        jd_per_unit=_JD_PER_YEAR,
        max_periods=max_l1,
        compute_sub=True,
    )

    # Trim to just past target + a few years buffer
    trimmed: list[ZRPeriod] = []
    for p in l1_periods:
        trimmed.append(p)
        if p.end_jd > far_future_jd and len(trimmed) >= 5:
            break

    return trimmed


# ─────────────────────────────────────────────────────────────
# Flat Period Extraction (for table display)
# ─────────────────────────────────────────────────────────────

def flatten_periods(periods: list[ZRPeriod], max_level: int = 2) -> list[ZRPeriod]:
    """Flatten nested periods up to *max_level* into a single list."""
    result: list[ZRPeriod] = []
    for p in periods:
        result.append(p)
        if p.level < max_level and p.sub_periods:
            result.extend(flatten_periods(p.sub_periods, max_level))
    return result


def get_current_periods(periods: list[ZRPeriod]) -> dict[str, ZRPeriod | None]:
    """Return the current L1 and L2 periods (if any).

    Returns a dict with keys ``"L1"`` and ``"L2"``.
    """
    result: dict[str, ZRPeriod | None] = {"L1": None, "L2": None, "L3": None}
    for p in periods:
        if p.is_current:
            result["L1"] = p
            for sub in p.sub_periods:
                if sub.is_current:
                    result["L2"] = sub
                    for subsub in sub.sub_periods:
                        if subsub.is_current:
                            result["L3"] = subsub
                            break
                    break
            break
    return result


# ─────────────────────────────────────────────────────────────
# Valens Spirit-Fortune Same-Sign Rule
# ─────────────────────────────────────────────────────────────

def apply_spirit_fortune_rule(fortune_lon: float, spirit_lon: float) -> tuple[float, float]:
    """Apply Valens' same-sign rule for Fortune and Spirit.

    若幸運點與精神點同宮（同一星座），精神點往前移動一宮（+30°）。
    幸運點不動。

    Per Vettius Valens *Anthologies*: when Lot of Fortune and Lot of Spirit
    fall in the same sign, Spirit is moved forward by one whole sign so that
    the two Lots are separated.  Fortune remains unchanged.

    Parameters
    ----------
    fortune_lon:
        Longitude of the Lot of Fortune (0–360°).
    spirit_lon:
        Longitude of the Lot of Spirit (0–360°).

    Returns
    -------
    tuple[float, float]
        ``(fortune_lon, adjusted_spirit_lon)``
    """
    fortune_sign_idx = int(fortune_lon / 30) % 12
    spirit_sign_idx = int(spirit_lon / 30) % 12

    if fortune_sign_idx == spirit_sign_idx:
        # Advance Spirit to next sign — keep degree-within-sign the same
        adjusted = (spirit_lon + 30.0) % 360.0
        return fortune_lon, adjusted

    return fortune_lon, spirit_lon


# ─────────────────────────────────────────────────────────────
# High-Level Convenience Wrapper
# ─────────────────────────────────────────────────────────────

def get_current_periods_for_natal(
    fortune_lon: float,
    spirit_lon: float,
    birth_jd: float,
    target_jd: float,
    apply_same_sign_rule: bool = True,
    max_l1: int = 25,
) -> dict[str, dict[str, ZRPeriod | None]]:
    """Compute current L1/L2/L3 periods for both Fortune and Spirit lots.

    方便日常使用的高階包裝函數：一次返回 Fortune 和 Spirit 的當前時主。

    Parameters
    ----------
    fortune_lon:
        Longitude of the Lot of Fortune.
    spirit_lon:
        Longitude of the Lot of Spirit.
    birth_jd:
        Julian Day of birth.
    target_jd:
        Target Julian Day (usually today).
    apply_same_sign_rule:
        Whether to apply Valens' Spirit-Fortune same-sign adjustment.
    max_l1:
        Maximum number of L1 periods to generate per lot.

    Returns
    -------
    dict with keys ``"fortune"`` and ``"spirit"``, each containing a
    ``{"L1": ZRPeriod|None, "L2": ZRPeriod|None, "L3": ZRPeriod|None}`` dict.
    """
    if apply_same_sign_rule:
        fortune_lon, spirit_lon = apply_spirit_fortune_rule(fortune_lon, spirit_lon)

    fortune_periods = compute_zodiacal_releasing_full(
        lot_lon=fortune_lon,
        birth_jd=birth_jd,
        target_jd=target_jd,
        source="fortune",
        max_l1=max_l1,
    )
    spirit_periods = compute_zodiacal_releasing_full(
        lot_lon=spirit_lon,
        birth_jd=birth_jd,
        target_jd=target_jd,
        source="spirit",
        max_l1=max_l1,
    )

    return {
        "fortune": get_current_periods(fortune_periods),
        "spirit": get_current_periods(spirit_periods),
    }
