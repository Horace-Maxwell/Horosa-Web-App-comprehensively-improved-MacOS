"""astro/huangji/huangji.py — 皇極經世（Huangji Jingshi）wrapper for KinAstro."""

from __future__ import annotations

import json
import logging
import os
import random
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any

import swisseph as swe

from astro.swe_init import init_swisseph

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "wangji", "data")

_LIFETIME_CYCLE_COUNT = 5  # Number of 30-year 世 periods to show

logger = logging.getLogger(__name__)


def _load_classics_json(filename: str) -> dict[str, Any]:
    """Load a classics JSON file from the wangji data directory."""
    path = os.path.join(_DATA_DIR, filename)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.debug("Classics JSON not found: %s", path)
        return {}
    except json.JSONDecodeError as exc:
        logger.warning("Classics JSON decode error in %s: %s", path, exc)
        return {}


# Cached classics data loaded once at import time
_XINYI_FAWEI: dict[str, Any] = _load_classics_json("xinyi_fawei.json")
_HUANGJI_JINGSHI_SHU: dict[str, Any] = _load_classics_json("huangji_jingshi_shu.json")
_GUANWU_YANYI: dict[str, Any] = _load_classics_json("guanwu_yanyi.json")

_SOLAR_TERMS_BY_LON = [
    (315.0, "立春", "Start of Spring"),
    (330.0, "雨水", "Rain Water"),
    (345.0, "驚蟄", "Awakening of Insects"),
    (0.0, "春分", "Spring Equinox"),
    (15.0, "清明", "Pure Brightness"),
    (30.0, "穀雨", "Grain Rain"),
    (45.0, "立夏", "Start of Summer"),
    (60.0, "小滿", "Lesser Fullness"),
    (75.0, "芒種", "Grain in Ear"),
    (90.0, "夏至", "Summer Solstice"),
    (105.0, "小暑", "Lesser Heat"),
    (120.0, "大暑", "Greater Heat"),
    (135.0, "立秋", "Start of Autumn"),
    (150.0, "處暑", "Limit of Heat"),
    (165.0, "白露", "White Dew"),
    (180.0, "秋分", "Autumn Equinox"),
    (195.0, "寒露", "Cold Dew"),
    (210.0, "霜降", "Frost's Descent"),
    (225.0, "立冬", "Start of Winter"),
    (240.0, "小雪", "Lesser Snow"),
    (255.0, "大雪", "Greater Snow"),
    (270.0, "冬至", "Winter Solstice"),
    (285.0, "小寒", "Lesser Cold"),
    (300.0, "大寒", "Greater Cold"),
]

EXPECTED_GUA_KEYS = ("正卦", "運卦", "世卦", "旬卦", "年卦", "月卦", "日卦", "時卦", "分卦")


@dataclass
class HistoricalContext:
    start_year: int
    duration: int
    dynasty: str
    title: str
    era: str
    name: str = ""


@dataclass
class CrossSystemSnapshot:
    zodiacal_releasing_l1: str = ""
    annual_profection: str = ""
    vedic_dasha: str = ""
    ziwei_daxian: str = ""


@dataclass
class HuangjiPan:
    yuan: int
    hui: int
    yun: int
    shi: int
    year_in_shi: int
    year_in_yun: int
    year_in_hui: int
    year_in_yuan: int
    total_years_from_epoch: int
    hui_global: int
    yun_global: int
    shi_global: int
    gua: dict[str, str] = field(default_factory=dict)
    moving_lines: dict[str, int] = field(default_factory=dict)
    ganzhi: list[str] = field(default_factory=list)
    jieqi_kinwangji: str = ""
    jieqi_swiss: str = ""
    historical_context: list[HistoricalContext] = field(default_factory=list)
    major_cycle_milestones: list[dict[str, Any]] = field(default_factory=list)
    lifetime_cycles: list[dict[str, Any]] = field(default_factory=list)
    bagua_xiang: dict[str, Any] = field(default_factory=dict)
    philosophy_quote: dict[str, str] = field(default_factory=dict)
    hui_gua: str = ""


@dataclass
class HuangjiPanResult:
    system: str
    location_name: str
    datetime_local: str
    board_text: str
    huangji_pan: HuangjiPan
    cross_system: CrossSystemSnapshot = field(default_factory=CrossSystemSnapshot)

    def to_dict(self) -> dict[str, Any]:
        return {
            "system": self.system,
            "location_name": self.location_name,
            "datetime_local": self.datetime_local,
            "board_text": self.board_text,
            "huangji_pan": asdict(self.huangji_pan),
            "cross_system": asdict(self.cross_system),
        }


def _get_wangji_exports() -> tuple[Any, Any, Any, Any]:
    from astro.wangji.history import history_for_year
    from astro.wangji.jieqi import jq
    from astro.wangji.wanji import display_pan, wanji_four_gua

    return wanji_four_gua, display_pan, jq, history_for_year


def _solar_term_from_swiss(jd_ut: float) -> tuple[str, str, float]:
    sun_lon = swe.calc_ut(jd_ut, swe.SUN)[0][0] % 360.0
    best = min(
        _SOLAR_TERMS_BY_LON,
        key=lambda item: min(abs(sun_lon - item[0]), 360.0 - abs(sun_lon - item[0])),
    )
    return best[1], best[2], round(sun_lon, 6)


def _accumulated_year(adjusted_year: int) -> int:
    return 67017 + adjusted_year + (1 if adjusted_year < 0 else 0)


def _calc_cycle_hierarchy(adjusted_year: int) -> tuple[int, int, int, int, int, int, int, int]:
    total = _accumulated_year(adjusted_year)
    yuan = total // 129600 + 1
    year_in_yuan = total % 129600 + 1
    hui = (year_in_yuan - 1) // 10800 + 1
    year_in_hui = (year_in_yuan - 1) % 10800 + 1
    yun = (year_in_hui - 1) // 360 + 1
    year_in_yun = (year_in_hui - 1) % 360 + 1
    shi = (year_in_yun - 1) // 30 + 1
    year_in_shi = (year_in_yun - 1) % 30 + 1
    return total, yuan, hui, yun, shi, year_in_shi, year_in_yun, year_in_hui


def _build_milestones(adjusted_year: int, year_in_shi: int, year_in_yun: int, year_in_hui: int) -> list[dict[str, Any]]:
    return [
        {"label": "下個世起點", "year": adjusted_year + (31 - year_in_shi)},
        {"label": "下個運起點", "year": adjusted_year + (361 - year_in_yun)},
        {"label": "下個會起點", "year": adjusted_year + (10801 - year_in_hui)},
    ]


def _build_lifetime_cycles(birth_year: int, current_year: int) -> list[dict[str, Any]]:
    """Build personal lifetime positioning in 30-year 世 cycles.

    Divides a person's life into ``_LIFETIME_CYCLE_COUNT`` 30-year 世 periods
    from birth onward, marking the current period and providing a macro-cycle
    life view akin to the Huangji 大限 concept.

    Args:
        birth_year: The person's birth year.
        current_year: The reference year to determine the current cycle.

    Returns:
        List of dicts with ``period``, ``age_range``, ``year_range``,
        ``is_current``, ``current_age``, and ``shi_num`` keys.
    """
    cycles: list[dict[str, Any]] = []
    age = max(0, current_year - birth_year)
    for i in range(_LIFETIME_CYCLE_COUNT):
        start_age = i * 30
        end_age = start_age + 29
        start_year = birth_year + start_age
        end_year = birth_year + end_age
        is_current = start_age <= age <= end_age
        _, _, _, _, shi_num, _, _, _ = _calc_cycle_hierarchy(start_year)
        cycles.append({
            "period": i + 1,
            "age_range": f"{start_age}–{end_age}歲",
            "year_range": f"{start_year}–{end_year}",
            "is_current": is_current,
            "current_age": age if is_current else None,
            "shi_num": shi_num,
        })
    return cycles


def _get_hui_gua(hui: int) -> str:
    """Return the hexagram associated with the given 會 number (1–12)."""
    hui_gua_map = _XINYI_FAWEI.get("yuan_hui_yun_shi", {}).get("hui_gua", {})
    entry = hui_gua_map.get(str(hui), {})
    return entry.get("gua", "")


def _get_bagua_xiang_for_gua(gua_name: str) -> dict[str, Any]:
    """Return the 八卦取象 description for a given trigram name.

    The ``bagua_xiang`` table in xinyi_fawei.json is keyed by trigram name
    (乾, 兌, 離, …), so this directly matches when the caller supplies a
    trigram name, or returns an empty dict for compound hexagrams.

    Args:
        gua_name: Trigram or hexagram name.

    Returns:
        Attribute dict from 八卦取象, or an empty dict if not found.
    """
    bagua = _XINYI_FAWEI.get("bagua_xiang", {})
    return bagua.get(gua_name, {})


def _random_philosophy_quote() -> dict[str, str]:
    """Return a random philosophy quote from the three classics JSON files.

    Draws from xinyi_fawei, huangji_jingshi_shu, and guanwu_yanyi.
    Returns a dict with ``source``, ``text``, and ``theme`` keys.
    """
    quotes: list[dict[str, Any]] = []
    quotes.extend(_XINYI_FAWEI.get("philosophy_quotes", []))
    quotes.extend(_HUANGJI_JINGSHI_SHU.get("philosophy_quotes", []))
    for vol in _GUANWU_YANYI.get("volumes", []):
        for passage in vol.get("passages", [])[:3]:
            quotes.append({
                "id": passage.get("id", ""),
                "source": "觀物外篇衍義",
                "text": passage.get("text", "")[:120],
                "theme": "象數",
            })
    if not quotes:
        return {"source": "", "text": "", "theme": ""}
    chosen = random.choice(quotes)
    return {
        "source": chosen.get("source", ""),
        "text": chosen.get("text", ""),
        "theme": chosen.get("theme", ""),
    }


def _build_cross_system_snapshot(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str,
    reference_year: int,
    gender: str,
) -> CrossSystemSnapshot:
    out = CrossSystemSnapshot()

    try:
        from astro.western.western import compute_western_chart
        from astro.western.hellenistic import compute_hellenistic_chart
        from astro.hellenistic import get_current_periods_for_natal, get_current_profection

        western_chart = compute_western_chart(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
        )
        prof = get_current_profection(western_chart.ascendant, year, target_date=date(reference_year, 1, 1))
        out.annual_profection = f"{prof.calendar_year}｜{prof.sign_cn}宮（{prof.lord_cn}）"

        hchart = compute_hellenistic_chart(western_chart, birth_year=year, current_year=reference_year)
        fortune_lon = next((l.longitude for l in hchart.lots if "Fortune" in l.name), 0.0)
        spirit_lon = next((l.longitude for l in hchart.lots if "Spirit" in l.name), 0.0)
        target_jd = western_chart.julian_day + max(0, reference_year - year) * 365.25
        zr = get_current_periods_for_natal(fortune_lon, spirit_lon, western_chart.julian_day, target_jd)
        l1 = zr.get("spirit", {}).get("L1")
        if l1:
            out.zodiacal_releasing_l1 = f"Spirit L1：{l1.sign}（{l1.start_year}-{l1.end_year}）"
    except Exception as exc:
        logger.debug("Huangji cross-system western/hellenistic snapshot skipped: %s", exc)

    try:
        from astro.vedic.indian import compute_vedic_chart
        from astro.vedic.vedic_dasha import compute_vimshottari

        vedic_chart = compute_vedic_chart(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
        )
        moon = next((p for p in vedic_chart.planets if "Chandra" in p.name), None)
        if moon:
            vim = compute_vimshottari(moon.longitude, vedic_chart.julian_day)
            ref_y = int(reference_year)
            current = next(
                (
                    p
                    for p in vim.mahadasha_periods
                    if int(p.start_date.split("-", 1)[0]) <= ref_y <= int(p.end_date.split("-", 1)[0])
                ),
                vim.mahadasha_periods[0] if vim.mahadasha_periods else None,
            )
            if current:
                out.vedic_dasha = f"{current.lord_cn}大運（{current.start_date}～{current.end_date}）"
    except Exception as exc:
        logger.debug("Huangji cross-system vedic snapshot skipped: %s", exc)

    try:
        from astro.ziwei import compute_ziwei_chart

        zw = compute_ziwei_chart(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            gender=gender,
        )
        age = max(0, reference_year - year)
        palace = next(
            (p for p in zw.palaces if p.da_xian_start <= age <= p.da_xian_start + 9),
            zw.palaces[0] if zw.palaces else None,
        )
        if palace:
            out.ziwei_daxian = f"{age}歲｜{palace.name}（{palace.da_xian}）"
    except Exception as exc:
        logger.debug("Huangji cross-system ziwei snapshot skipped: %s", exc)

    return out


def compute_huangji_pan(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    reference_year: int | None = None,
    include_cross_system: bool = True,
    gender: str = "男",
) -> HuangjiPanResult:
    """Compute Huangji Jingshi cycle position and cross-system snapshots."""
    init_swisseph()
    wanji_four_gua, display_pan, jq, history_for_year = _get_wangji_exports()

    pan = wanji_four_gua(year, month, day, hour, minute)
    board_text = display_pan(year, month, day, hour, minute)
    kinwangji_jieqi = jq(year, month, day, hour, minute)

    adjusted_year = int(str(pan.get("日期", f"{year}")).split("-")[0])
    total, yuan, hui, yun, shi, year_in_shi, year_in_yun, year_in_hui = _calc_cycle_hierarchy(adjusted_year)

    ut_hour = hour + minute / 60.0 - timezone
    jd_ut = swe.julday(year, month, day, ut_hour)
    swiss_jq_zh, _, _ = _solar_term_from_swiss(jd_ut)

    history_rows = [HistoricalContext(**row) for row in history_for_year(reference_year or year)]
    ref_year = reference_year or datetime.now().year
    hui_gua_name = _get_hui_gua(hui)
    shi_gua_name = pan.get("世卦", "")
    huangji_pan = HuangjiPan(
        yuan=yuan,
        hui=hui,
        yun=yun,
        shi=shi,
        year_in_shi=year_in_shi,
        year_in_yun=year_in_yun,
        year_in_hui=year_in_hui,
        year_in_yuan=(total % 129600) + 1,
        total_years_from_epoch=total,
        hui_global=int(pan.get("會", 0)),
        yun_global=int(pan.get("運", 0)),
        shi_global=int(pan.get("世", 0)),
        gua={k: pan.get(k, "") for k in EXPECTED_GUA_KEYS},
        moving_lines={
            "運卦動爻": int(pan.get("運卦動爻", 0) or 0),
            "世卦動爻": int(pan.get("世卦動爻", 0) or 0),
            "旬卦動爻": int(pan.get("旬卦動爻", 0) or 0),
        },
        ganzhi=list(pan.get("干支", [])),
        jieqi_kinwangji=kinwangji_jieqi,
        jieqi_swiss=swiss_jq_zh,
        historical_context=history_rows,
        major_cycle_milestones=_build_milestones(adjusted_year, year_in_shi, year_in_yun, year_in_hui),
        lifetime_cycles=_build_lifetime_cycles(year, ref_year),
        bagua_xiang=_get_bagua_xiang_for_gua(shi_gua_name),
        philosophy_quote=_random_philosophy_quote(),
        hui_gua=hui_gua_name,
    )
    cross = CrossSystemSnapshot()
    if include_cross_system:
        cross = _build_cross_system_snapshot(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            reference_year=ref_year,
            gender=gender,
        )

    return HuangjiPanResult(
        system="huangji",
        location_name=location_name,
        datetime_local=f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} (UTC{timezone:+g})",
        board_text=board_text,
        huangji_pan=huangji_pan,
        cross_system=cross,
    )
