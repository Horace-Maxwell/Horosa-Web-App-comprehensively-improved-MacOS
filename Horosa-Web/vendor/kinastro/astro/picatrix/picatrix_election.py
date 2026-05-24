from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from html import escape
from typing import Any

import swisseph as swe

from astro.arabic_lots import compute_albiruni_lots
from astro.arabic.picatrix_data import PICATRIX_MANSIONS
from astro.arabic.picatrix_invocations import Planet, build_spirit_invocation_steps, get_spirit
from astro.chart_renderer_v2 import build_cultural_svg, inject_svg_enhancements
from astro.chart_theme import CHART_BG, PLANET_COLORS, PRIMARY_COLOR, SECONDARY_COLOR
from astro.electional.calculator import compute_western_electional
from astro.picatrix_behenian.constants import BEHENIAN_STARS
from interpretations.talismanic import (
    DECAN_TALISMANS,
    PLANETARY_TALISMAN_BY_PLANET,
    PURPOSE_TO_PLANETS,
    get_decan_by_longitude,
)

_PURPOSE_ZH = {
    "love": "愛情",
    "wealth": "財富",
    "protection": "防護",
    "healing": "療癒",
    "success": "成功",
    "harm": "傷害",
}

_PURPOSE_AR = {
    "love": "المحبة",
    "wealth": "الثروة",
    "protection": "الحماية",
    "healing": "الشفاء",
    "success": "النجاح",
    "harm": "الإيذاء",
}

_HARMFUL_PURPOSES = {"harm", "enmity", "separation", "curse"}
REALTIME_WINDOW_SECONDS = 12 * 3600
DEFAULT_MIN_SCORE = 62.0

_ACTIVITY_BY_PURPOSE = {
    "love": "marriage",
    "wealth": "trade",
    "protection": "important_meeting",
    "healing": "medical_treatment",
    "success": "important_meeting",
    "harm": "litigation",
}


@dataclass
class PicatrixImageCandidate:
    source_type: str
    source_id: str
    source_name_en: str
    source_name_zh: str
    source_name_ar: str
    celestial_source: str
    image_description: dict[str, str]
    purposes_en: list[str] = field(default_factory=list)
    purposes_zh: list[str] = field(default_factory=list)


@dataclass
class PicatrixElectionDetails:
    dt_utc: datetime
    dt_local: datetime
    julian_day: float
    purpose: str
    target_planet: str
    target_planet_house: int
    target_planet_dignity: str
    target_planet_retrograde: bool
    planetary_day_lord: str
    planetary_hour_lord: str
    moon_longitude: float
    moon_sign: str
    moon_phase: str
    moon_applying_to_target: bool
    lunar_mansion_index: int
    lunar_mansion_name_en: str
    lunar_mansion_name_zh: str
    decan_number: int
    decan_ruler: str
    ascendant: float
    mc: float
    part_of_fortune: float
    part_of_fortune_house: int
    score: float
    quality: str
    matched_rules: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    is_realtime_window: bool = False


@dataclass
class PicatrixBlueprint:
    election_details: PicatrixElectionDetails
    image_description: dict[str, Any]
    materia: dict[str, Any]
    invocation: dict[str, str]
    ritual_steps: dict[str, list[str]]
    warnings: list[str]
    chart_snapshot_svg: str
    blueprint_html: str


@dataclass
class PicatrixGenerationResult:
    purpose: str
    purpose_zh: str
    purpose_ar: str
    selected_image: PicatrixImageCandidate
    election_details: PicatrixElectionDetails
    blueprint: PicatrixBlueprint
    alternatives: list[PicatrixElectionDetails] = field(default_factory=list)


def _normalize(lon: float) -> float:
    return lon % 360.0


def _decan_number(moon_lon: float) -> int:
    return int(_normalize(moon_lon) // 10) + 1


def _planetary_day_lord(dt_local: datetime) -> str:
    day_to_lord = {
        0: "Moon",
        1: "Mars",
        2: "Mercury",
        3: "Jupiter",
        4: "Venus",
        5: "Saturn",
        6: "Sun",
    }
    return day_to_lord[dt_local.weekday()]


def _moon_lunar_mansion(moon_lon: float) -> tuple[int, dict[str, Any]]:
    width = 360.0 / 28.0
    idx = int(_normalize(moon_lon) / width)
    idx = min(max(idx, 0), 27)
    return idx + 1, PICATRIX_MANSIONS[idx]


def _house_from_lon(lon: float, cusps: list[float]) -> int:
    lon = _normalize(lon)
    for i in range(12):
        start = _normalize(cusps[i])
        end = _normalize(cusps[(i + 1) % 12])
        if start < end:
            if start <= lon < end:
                return i + 1
        else:
            if lon >= start or lon < end:
                return i + 1
    return 1


def _planet_from_name(name: str) -> Planet:
    return Planet(name)


def _fixed_star_candidates(purpose: str) -> list[PicatrixImageCandidate]:
    p_lower = purpose.lower()
    out: list[PicatrixImageCandidate] = []
    for star in BEHENIAN_STARS:
        uses = [u.lower() for u in star.magic_uses]
        if any(p_lower in u for u in uses) or p_lower in star.talisman_power.lower():
            out.append(
                PicatrixImageCandidate(
                    source_type="fixed_star",
                    source_id=star.name.lower(),
                    source_name_en=star.name,
                    source_name_zh=star.cn_name,
                    source_name_ar=star.name,
                    celestial_source=f"Behenian Star · {star.primary_ruler}/{star.secondary_ruler}",
                    image_description={
                        "en": star.image_description,
                        "zh": star.image_description_cn,
                        "ar": star.image_description,
                    },
                    purposes_en=star.magic_uses,
                    purposes_zh=star.magic_uses_cn,
                )
            )
    return out[:4]


def select_picatrix_images(purpose: str) -> list[PicatrixImageCandidate]:
    purpose_key = purpose.lower().strip()
    planets = PURPOSE_TO_PLANETS.get(purpose_key, ["Jupiter", "Venus", "Sun"])
    results: list[PicatrixImageCandidate] = []

    for p in planets:
        talisman = PLANETARY_TALISMAN_BY_PLANET.get(p)
        if not talisman:
            continue
        results.append(
            PicatrixImageCandidate(
                source_type="planet",
                source_id=p.lower(),
                source_name_en=p,
                source_name_zh=talisman.planet_cn,
                source_name_ar=p,
                celestial_source="Planetary Image (Picatrix Book II–III)",
                image_description={
                    "en": talisman.image_description_en,
                    "zh": talisman.image_description_cn,
                    "ar": talisman.image_description_en,
                },
                purposes_en=talisman.purposes_en,
                purposes_zh=talisman.purposes_cn,
            )
        )

    for mansion in PICATRIX_MANSIONS:
        purpose_hits = [p for p in mansion.get("purposes", []) if purpose_key in p.lower()]
        if purpose_hits:
            results.append(
                PicatrixImageCandidate(
                    source_type="lunar_mansion",
                    source_id=f"mansion_{mansion['index'] + 1}",
                    source_name_en=mansion["english_name"],
                    source_name_zh=mansion["chinese_name"],
                    source_name_ar=mansion["arabic_script"],
                    celestial_source=f"Lunar Mansion {mansion['index'] + 1}",
                    image_description={
                        "en": mansion["magic_image"],
                        "zh": mansion["magic_image_cn"],
                        "ar": mansion["magic_image"],
                    },
                    purposes_en=mansion.get("purposes", []),
                    purposes_zh=mansion.get("purposes_cn", []),
                )
            )

    for decan in DECAN_TALISMANS:
        if any(purpose_key in p.lower() for p in decan.powers_en):
            results.append(
                PicatrixImageCandidate(
                    source_type="decan",
                    source_id=f"decan_{decan.decan_number}",
                    source_name_en=f"Decan {decan.decan_number}",
                    source_name_zh=f"第{decan.decan_number}面",
                    source_name_ar=f"وجه {decan.decan_number}",
                    celestial_source=f"Decan ({decan.sign} {decan.degrees_start}°-{decan.degrees_end}°)",
                    image_description={
                        "en": decan.image_description_en,
                        "zh": decan.image_description_cn,
                        "ar": decan.image_description_en,
                    },
                    purposes_en=decan.powers_en,
                    purposes_zh=decan.powers_cn,
                )
            )

    results.extend(_fixed_star_candidates(purpose_key))
    return results[:12]


def _score_picatrix_rules(
    *,
    election_result: Any,
    target_planet: str,
    purpose: str,
    mansion: dict[str, Any],
    moon_applying: bool,
    part_of_fortune_house: int,
) -> tuple[float, list[str], list[str]]:
    score = 0.0
    matched: list[str] = []
    warnings: list[str] = []
    harmful = purpose.lower() in _HARMFUL_PURPOSES

    planet_data = next((p for p in election_result.planets if p.name == target_planet), None)

    if planet_data:
        if planet_data.essential_dignity in {"domicile", "exaltation"}:
            score += 28
            matched.append("Target planet in essential dignity")
        elif planet_data.essential_dignity == "peregrine":
            score += 12
            warnings.append("Target planet peregrine")
        else:
            warnings.append("Target planet debilitated")

        if planet_data.house in {1, 10}:
            score += 12
            matched.append("Target planet angular (1st/10th)")

        if not planet_data.retrograde:
            score += 6
            matched.append("Target planet direct")
        else:
            warnings.append("Target planet retrograde")

    if election_result.planetary_hour_lord == target_planet:
        score += 10
        matched.append("Correct planetary hour")
    else:
        warnings.append("Planetary hour not matching target planet")

    if _planetary_day_lord(election_result.datetime_local) == target_planet:
        score += 8
        matched.append("Correct planetary day")

    if moon_applying:
        score += 14
        matched.append("Moon applying to target planet")
    else:
        warnings.append("Moon not applying to target planet")

    if mansion.get("fortunate", False) or harmful:
        score += 8
        matched.append("Lunar mansion suitable for intent")
    else:
        warnings.append("Current lunar mansion is not classically fortunate")

    if part_of_fortune_house in {1, 10, 11}:
        score += 6
        matched.append("Part of Fortune in supportive house")

    return max(0.0, min(100.0, score)), matched, warnings


def evaluate_picatrix_election(
    *,
    dt_utc: datetime,
    timezone_offset: float,
    latitude: float,
    longitude: float,
    purpose: str,
    target_planet: str,
    location_name: str = "",
) -> PicatrixElectionDetails:
    local_dt = (dt_utc + timedelta(hours=timezone_offset)).replace(tzinfo=None)
    activity = _ACTIVITY_BY_PURPOSE.get(purpose.lower(), "important_meeting")

    election = compute_western_electional(
        year=local_dt.year,
        month=local_dt.month,
        day=local_dt.day,
        hour=local_dt.hour,
        minute=local_dt.minute,
        timezone=timezone_offset,
        latitude=latitude,
        longitude=longitude,
        activity_type=activity,
        location_name=location_name,
    )

    moon = next((p for p in election.planets if p.name == "Moon"), None)
    target = next((p for p in election.planets if p.name == target_planet), None)
    mc = election.house_cusps[9] if len(election.house_cusps) >= 10 else 0.0

    moon_apply_text = (election.moon_applies_to or "").lower()
    moon_applying = target_planet.lower() in moon_apply_text

    mansion_index, mansion = _moon_lunar_mansion(moon.longitude if moon else 0.0)
    decan = get_decan_by_longitude(moon.longitude if moon else 0.0)

    lots = compute_albiruni_lots(
        year=local_dt.year,
        month=local_dt.month,
        day=local_dt.day,
        hour=local_dt.hour,
        minute=local_dt.minute,
        timezone=timezone_offset,
        latitude=latitude,
        longitude=longitude,
    )
    lot_fortune = next((lot for lot in lots.lots if lot.id == "lot_fortune"), None)
    part_of_fortune = lot_fortune.longitude if lot_fortune else 0.0
    part_of_fortune_house = lot_fortune.house if lot_fortune else _house_from_lon(part_of_fortune, election.house_cusps)

    score, matched_rules, warnings = _score_picatrix_rules(
        election_result=election,
        target_planet=target_planet,
        purpose=purpose,
        mansion=mansion,
        moon_applying=moon_applying,
        part_of_fortune_house=part_of_fortune_house,
    )

    quality = "Excellent" if score >= 80 else "Good" if score >= 65 else "Usable" if score >= 50 else "Weak"

    now_utc = datetime.now(timezone.utc)
    realtime = 0 <= (dt_utc - now_utc).total_seconds() <= REALTIME_WINDOW_SECONDS and score >= 70

    return PicatrixElectionDetails(
        dt_utc=dt_utc,
        dt_local=local_dt,
        julian_day=election.julian_day,
        purpose=purpose,
        target_planet=target_planet,
        target_planet_house=target.house if target else 0,
        target_planet_dignity=target.essential_dignity if target else "unknown",
        target_planet_retrograde=bool(target.retrograde) if target else False,
        planetary_day_lord=_planetary_day_lord(local_dt),
        planetary_hour_lord=election.planetary_hour_lord,
        moon_longitude=moon.longitude if moon else 0.0,
        moon_sign=moon.sign if moon else "Aries",
        moon_phase=election.moon_phase,
        moon_applying_to_target=moon_applying,
        lunar_mansion_index=mansion_index,
        lunar_mansion_name_en=mansion["english_name"],
        lunar_mansion_name_zh=mansion["chinese_name"],
        decan_number=decan.decan_number if decan else _decan_number(moon.longitude if moon else 0.0),
        decan_ruler=decan.ruler if decan else "Unknown",
        ascendant=election.ascendant,
        mc=mc,
        part_of_fortune=part_of_fortune,
        part_of_fortune_house=part_of_fortune_house,
        score=round(score, 2),
        quality=quality,
        matched_rules=matched_rules,
        warnings=warnings,
        is_realtime_window=realtime,
    )


def find_picatrix_elections(
    *,
    start_dt_utc: datetime,
    timezone_offset: float,
    latitude: float,
    longitude: float,
    purpose: str,
    target_planet: str,
    location_name: str = "",
    days_ahead: int = 30,
    step_hours: int = 2,
    min_score: float = 65.0,
) -> list[PicatrixElectionDetails]:
    if start_dt_utc.tzinfo is None:
        start_dt_utc = start_dt_utc.replace(tzinfo=timezone.utc)

    results: list[PicatrixElectionDetails] = []
    for i in range(int((days_ahead * 24) / step_hours) + 1):
        dt = start_dt_utc + timedelta(hours=i * step_hours)
        try:
            detail = evaluate_picatrix_election(
                dt_utc=dt,
                timezone_offset=timezone_offset,
                latitude=latitude,
                longitude=longitude,
                purpose=purpose,
                target_planet=target_planet,
                location_name=location_name,
            )
        except Exception:
            continue
        if detail.score >= min_score:
            results.append(detail)

    results.sort(key=lambda r: (-r.score, r.dt_utc))
    return results[:18]


def _svg_line(text: str, limit: int) -> str:
    safe = escape(text or "")
    if len(safe) <= limit:
        return safe
    clip = safe[: limit - 1].rstrip()
    if " " in clip:
        clip = clip.rsplit(" ", 1)[0]
    return f"{clip}…"


def _build_chart_snapshot_svg(detail: PicatrixElectionDetails, image: PicatrixImageCandidate) -> str:
    p_color = PLANET_COLORS.get(detail.target_planet, PRIMARY_COLOR)
    tz_offset = (detail.dt_local - detail.dt_utc.replace(tzinfo=None)).total_seconds() / 3600
    purpose_text = _svg_line(detail.purpose, 64)
    planet_text = _svg_line(detail.target_planet, 48)
    mansion_en = _svg_line(detail.lunar_mansion_name_en, 64)
    mansion_zh = _svg_line(detail.lunar_mansion_name_zh, 64)
    img_en = _svg_line(image.image_description.get("en", ""), 110)
    img_zh = _svg_line(image.image_description.get("zh", ""), 110)
    matched_text = _svg_line("; ".join(detail.matched_rules[:4]), 120)
    warnings_text = _svg_line("; ".join(detail.warnings[:3]) or "None", 120)
    decan_ruler = _svg_line(detail.decan_ruler, 40)
    svg = f"""
<svg width="980" height="620" viewBox="0 0 980 620" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="980" height="620" fill="{CHART_BG}"/>
  <rect x="24" y="24" width="932" height="572" rx="20" fill="rgba(20,16,36,0.92)" stroke="{SECONDARY_COLOR}" stroke-width="1.5"/>
  <text x="58" y="78" fill="{SECONDARY_COLOR}" font-size="30" font-family="serif">Picatrix Talisman Blueprint</text>
  <text x="58" y="118" fill="#d2c5a5" font-size="20">Purpose: {purpose_text} · Planet: {planet_text} · Score: {detail.score:.1f}</text>
  <text x="58" y="160" fill="#c8bddf" font-size="17">Election: {detail.dt_local.strftime('%Y-%m-%d %H:%M')} (UTC{tz_offset:+.1f})</text>
  <circle cx="768" cy="190" r="88" fill="none" stroke="{escape(p_color)}" stroke-width="2"/>
  <text x="768" y="196" text-anchor="middle" fill="{escape(p_color)}" font-size="42">{escape(detail.target_planet[:2].upper())}</text>
  <text x="58" y="228" fill="#e4ddcc" font-size="18">Lunar Mansion {detail.lunar_mansion_index}: {mansion_en} / {mansion_zh}</text>
  <text x="58" y="264" fill="#e4ddcc" font-size="18">Decan {detail.decan_number} ({decan_ruler}) · Moon applying: {detail.moon_applying_to_target}</text>
  <text x="58" y="300" fill="#e4ddcc" font-size="18">Asc: {detail.ascendant:.2f}° · MC: {detail.mc:.2f}° · Part of Fortune: {detail.part_of_fortune:.2f}°</text>
  <text x="58" y="352" fill="#d8ceb8" font-size="19">Image (EN): {img_en}</text>
  <text x="58" y="384" fill="#d8ceb8" font-size="19">Image (ZH): {img_zh}</text>
  <text x="58" y="430" fill="#ab9dd0" font-size="17">Matched rules: {matched_text}</text>
  <text x="58" y="468" fill="#bcaecc" font-size="16">Warnings: {warnings_text}</text>
</svg>
""".strip()
    return inject_svg_enhancements(svg)


def _blueprint_html(svg: str) -> str:
    return build_cultural_svg(
        svg,
        "tab_picatrix_behenian",
        title="✶ Picatrix Talismanic Magic Blueprint",
        animate_spin=False,
        extra_class="picatrix-manuscript",
    )


def _invocation_for_planet(planet_name: str, purpose: str) -> dict[str, str]:
    spirit = get_spirit(_planet_from_name(planet_name))
    return {
        "en": f"Purpose: {purpose}. {spirit.invocation_text.get('en', '')}",
        "zh": f"目的：{_PURPOSE_ZH.get(purpose, purpose)}。{spirit.invocation_text.get('zh', '')}",
        "ar": spirit.arabic_name or spirit.invocation_text.get("en", ""),
    }


def _ritual_steps(planet_name: str) -> dict[str, list[str]]:
    zh = build_spirit_invocation_steps(_planet_from_name(planet_name), language="zh")
    en = build_spirit_invocation_steps(_planet_from_name(planet_name), language="en")
    return {
        "zh": [
            "於選定時刻潔淨場所與器具。",
            "刻製圖像並配合對應香料與金屬。",
            *zh,
            "完成後將護符依用途佩戴、收藏或安置。",
        ],
        "en": [
            "Purify the place and tools at the elected time.",
            "Engrave the image with the proper metal and suffumigation.",
            *en,
            "Seal, conceal, and carry/place the talisman according to intent.",
        ],
        "ar": [
            "طهّر المكان والأدوات في وقت الاختيار.",
            "انقش الصورة مع المعدن والبخور الموافقين.",
            "اختم الطلسم واحفظه وفق المقصد.",
        ],
    }


def _materia(planet_name: str, image: PicatrixImageCandidate, detail: PicatrixElectionDetails) -> dict[str, Any]:
    talisman = PLANETARY_TALISMAN_BY_PLANET.get(planet_name)
    mansion = PICATRIX_MANSIONS[detail.lunar_mansion_index - 1]
    return {
        "planetary": {
            "metal": talisman.metal if talisman else mansion.get("metal", ""),
            "stone": talisman.gemstone if talisman else "",
            "color": talisman.color if talisman else mansion.get("color", ""),
            "incense": talisman.incense if talisman else mansion.get("incense", ""),
        },
        "mansion": {
            "name_en": mansion["english_name"],
            "name_zh": mansion["chinese_name"],
            "ruling_planet": mansion["ruling_planet"],
            "image_hint": mansion["magic_image"],
        },
        "image_source": {
            "type": image.source_type,
            "id": image.source_id,
            "description": image.image_description,
        },
    }


def generate_picatrix_talisman(
    *,
    purpose: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone_offset: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    days_ahead: int = 60,
    include_harmful: bool = False,
) -> PicatrixGenerationResult:
    swe.set_ephe_path("")
    candidates = select_picatrix_images(purpose)
    if not candidates:
        raise ValueError("No Picatrix image candidate found for purpose")

    purpose_key = purpose.lower().strip()
    if purpose_key in _HARMFUL_PURPOSES and not include_harmful:
        raise ValueError("Harmful intents require include_harmful=True and explicit research warning")

    selected = candidates[0]
    target_planet = PURPOSE_TO_PLANETS.get(purpose_key, ["Jupiter"])[0]

    start_local = datetime(year, month, day, hour, minute)
    start_utc = (start_local - timedelta(hours=timezone_offset)).replace(tzinfo=timezone.utc)

    elections = find_picatrix_elections(
        start_dt_utc=start_utc,
        timezone_offset=timezone_offset,
        latitude=latitude,
        longitude=longitude,
        purpose=purpose_key,
        target_planet=target_planet,
        location_name=location_name,
        days_ahead=max(1, min(days_ahead, 90)),
        step_hours=2,
        min_score=DEFAULT_MIN_SCORE,
    )

    if elections:
        primary = elections[0]
        alternatives = elections[1:4]
    else:
        primary = evaluate_picatrix_election(
            dt_utc=start_utc,
            timezone_offset=timezone_offset,
            latitude=latitude,
            longitude=longitude,
            purpose=purpose_key,
            target_planet=target_planet,
            location_name=location_name,
        )
        alternatives = []

    base_warnings = [
        "For research and historical study only.",
        "Picatrix includes benefic and malefic operations; use legal and ethical discretion.",
        "This module does not replace spiritual, medical, legal, or psychological advice.",
    ]

    if purpose_key in _HARMFUL_PURPOSES:
        base_warnings.append("Harm-related intention detected: explicit ethical red-flag applied.")

    invocation = _invocation_for_planet(target_planet, purpose_key)
    ritual_steps = _ritual_steps(target_planet)
    materia = _materia(target_planet, selected, primary)

    svg = _build_chart_snapshot_svg(primary, selected)
    html = _blueprint_html(svg)

    blueprint = PicatrixBlueprint(
        election_details=primary,
        image_description=selected.image_description,
        materia=materia,
        invocation=invocation,
        ritual_steps=ritual_steps,
        warnings=[*primary.warnings, *base_warnings],
        chart_snapshot_svg=svg,
        blueprint_html=html,
    )

    return PicatrixGenerationResult(
        purpose=purpose_key,
        purpose_zh=_PURPOSE_ZH.get(purpose_key, purpose_key),
        purpose_ar=_PURPOSE_AR.get(purpose_key, purpose_key),
        selected_image=selected,
        election_details=primary,
        blueprint=blueprint,
        alternatives=alternatives,
    )


__all__ = [
    "PicatrixBlueprint",
    "PicatrixElectionDetails",
    "PicatrixGenerationResult",
    "PicatrixImageCandidate",
    "evaluate_picatrix_election",
    "find_picatrix_elections",
    "generate_picatrix_talisman",
    "select_picatrix_images",
]
