from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional

import swisseph as swe

from astro.arabic_lots import compute_albiruni_lots
from astro.horary.calculator import WesternHoraryChart, compute_western_horary
from astro.horary.constants import DOMICILE_RULERS, ZODIAC_SIGNS
from astro.interpretations_base import JsonInterpretationEngine
from astro.swe_init import init_swisseph
from astro.western.western import WesternChart, compute_western_chart


@dataclass
class SportsTestimony:
    key: str
    value: float
    polarity: str
    description_zh: str
    description_en: str


@dataclass
class MatchAnalysis:
    team1_strength: float
    team2_strength: float
    key_testimonies: list[SportsTestimony] = field(default_factory=list)
    winner_probability: dict[str, float] = field(default_factory=dict)
    explanation: str = ""


@dataclass
class AdvancedPrediction:
    injury_risk_team1: float
    injury_risk_team2: float
    upset_indicator: float
    season_trend_hint: str
    electional_hint: str


@dataclass
class TeamNatalInput:
    team_name: str
    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0
    timezone: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    location_name: str = ""


@dataclass
class EventNatalComparison:
    team: str
    synastry_score: float
    key_aspects: list[str] = field(default_factory=list)


@dataclass
class SportsHoraryResult:
    mode: str
    match_name: str
    team1: str
    team2: str
    preferred_team: Optional[str]
    tradition: str
    chart: WesternHoraryChart
    match_analysis: MatchAnalysis
    advanced: AdvancedPrediction
    event_natal_dashboard: list[EventNatalComparison] = field(default_factory=list)
    timeline_transits: list[dict[str, Any]] = field(default_factory=list)


def _norm(deg: float) -> float:
    return deg % 360.0


def _sign_index(deg: float) -> int:
    return int(_norm(deg) / 30.0)


def _probabilities(score1: float, score2: float) -> tuple[float, float]:
    total = max(abs(score1) + abs(score2), 1.0)
    base = 0.5 + (score1 - score2) / (2.0 * total)
    p1 = min(0.9, max(0.1, base))
    return p1, 1.0 - p1


def _angular_separation(a: float, b: float) -> float:
    return abs((_norm(a - b) + 180.0) % 360.0 - 180.0)


def _team_significators(chart: WesternHoraryChart) -> tuple[str, str, int]:
    lord1 = chart.asc_lord
    seventh_cusp = chart.house_cusps[6]
    seventh_sign_idx = _sign_index(seventh_cusp)
    lord7 = DOMICILE_RULERS[seventh_sign_idx]
    return lord1, lord7, seventh_sign_idx


def _planet_by_name(chart: WesternHoraryChart, name: str):
    return next((p for p in chart.planets if p.name == name), None)


def _moon_flow_bonus(chart: WesternHoraryChart, lord1: str, lord7: str) -> tuple[float, float, list[SportsTestimony]]:
    bonus1 = 0.0
    bonus2 = 0.0
    notes: list[SportsTestimony] = []
    for a in chart.aspects:
        if not a.is_applying:
            continue
        pair = {a.planet1, a.planet2}
        if "Moon" not in pair:
            continue
        if lord1 in pair:
            bonus1 += 1.6
            notes.append(SportsTestimony(
                key="moon_to_l1",
                value=1.6,
                polarity="team1",
                description_zh="月亮入相主隊主星，流程偏向主隊。",
                description_en="Applying Moon to Lord 1 supports team 1 momentum.",
            ))
        if lord7 in pair:
            bonus2 += 1.6
            notes.append(SportsTestimony(
                key="moon_to_l7",
                value=1.6,
                polarity="team2",
                description_zh="月亮入相對手主星，流程偏向對手。",
                description_en="Applying Moon to Lord 7 supports team 2 momentum.",
            ))

    if chart.moon_voc.is_voc:
        bonus1 -= 0.8
        bonus2 -= 0.8
        notes.append(SportsTestimony(
            key="voc_moon",
            value=-0.8,
            polarity="both",
            description_zh="虛空月：比賽節奏容易停滯，結論置信度下降。",
            description_en="Void-of-course Moon indicates slower flow and lower certainty.",
        ))
    return bonus1, bonus2, notes


def _victory_house_bonus(chart: WesternHoraryChart, lord1: str, lord7: str) -> tuple[float, float, list[SportsTestimony]]:
    notes: list[SportsTestimony] = []
    tenth_cusp = chart.house_cusps[9]
    lord10 = DOMICILE_RULERS[_sign_index(tenth_cusp)]
    b1 = 0.0
    b2 = 0.0
    for a in chart.aspects:
        if not a.is_applying:
            continue
        pair = {a.planet1, a.planet2}
        if lord10 not in pair:
            continue
        if lord1 in pair:
            b1 += 1.2
            notes.append(SportsTestimony(
                key="l10_to_l1",
                value=1.2,
                polarity="team1",
                description_zh="10宮（勝利）主星連結主隊主星。",
                description_en="Lord 10 (victory) applies to Lord 1.",
            ))
        if lord7 in pair:
            b2 += 1.2
            notes.append(SportsTestimony(
                key="l10_to_l7",
                value=1.2,
                polarity="team2",
                description_zh="10宮（勝利）主星連結對手主星。",
                description_en="Lord 10 (victory) applies to Lord 7.",
            ))
    return b1, b2, notes


def _injury_risk(chart: WesternHoraryChart, lord1: str, lord7: str) -> tuple[float, float]:
    mars = _planet_by_name(chart, "Mars")
    saturn = _planet_by_name(chart, "Saturn")
    l1 = _planet_by_name(chart, lord1)
    l7 = _planet_by_name(chart, lord7)

    risk1 = 0.15
    risk2 = 0.15

    for p in [mars, saturn]:
        if not p:
            continue
        if p.house in (6, 12):
            risk1 += 0.08
            risk2 += 0.08

    if l1 and l1.house in (6, 12):
        risk1 += 0.12
    if l7 and l7.house in (6, 12):
        risk2 += 0.12

    return min(0.95, risk1), min(0.95, risk2)


def _upset_indicator(jd_ut: float) -> float:
    init_swisseph()
    try:
        uranus = swe.calc_ut(jd_ut, swe.URANUS)[0][0]
        node = swe.calc_ut(jd_ut, swe.TRUE_NODE)[0][0]
        # Smaller Uranus-Node separation implies higher disruption/upset potential.
        diff = _angular_separation(uranus, node)
        return max(0.05, min(0.95, 1.0 - (diff / 180.0)))
    except Exception:
        return 0.5


def _season_hint(jd_ut: float) -> str:
    try:
        init_swisseph()
        jup = swe.calc_ut(jd_ut, swe.JUPITER)[0][0]
        sat = swe.calc_ut(jd_ut, swe.SATURN)[0][0]
        phase = _angular_separation(jup, sat)
        if phase < 45:
            return "Jupiter-Saturn phase is tight: season trend favors disciplined teams."
        if phase < 90:
            return "Building phase: teams with tactical coherence gain edge over season."
        return "Dispersed phase: season volatility remains high; rotate risk exposure."
    except Exception:
        return "Season trend currently neutral; rely on weekly re-checks."


def _electional_hint(chart: WesternHoraryChart) -> str:
    moon = _planet_by_name(chart, "Moon")
    if moon and moon.house in (1, 10, 11):
        return "Prefer entering markets close to kickoff when Moon is angular."
    if chart.moon_voc.is_voc:
        return "Avoid aggressive entries during VOC Moon; prefer live confirmation."
    return "Use phased staking; add only after first in-play momentum confirmation."


def _timeline(chart_time: datetime) -> list[dict[str, Any]]:
    return [
        {"label": "-3h", "time": (chart_time - timedelta(hours=3)).isoformat(timespec="minutes")},
        {"label": "Kickoff", "time": chart_time.isoformat(timespec="minutes")},
        {"label": "+1h", "time": (chart_time + timedelta(hours=1)).isoformat(timespec="minutes")},
        {"label": "+3h", "time": (chart_time + timedelta(hours=3)).isoformat(timespec="minutes")},
    ]


def _event_synastry_score(event_chart: WesternChart, natal_chart: WesternChart) -> EventNatalComparison:
    event_focus = {"Sun", "Moon", "Mars", "Jupiter"}
    natal_focus = {"Sun", "Moon", "Mars"}
    score = 0.0
    aspects: list[str] = []
    for ep in event_chart.planets:
        if ep.name not in event_focus:
            continue
        for np in natal_chart.planets:
            if np.name not in natal_focus:
                continue
            diff = _angular_separation(ep.longitude, np.longitude)
            if diff <= 5:
                score += 1.0
                aspects.append(f"{ep.name} conjunct natal {np.name}")
            elif abs(diff - 120) <= 4 or abs(diff - 60) <= 3:
                score += 0.7
                aspects.append(f"{ep.name} harmonious to natal {np.name}")
            elif abs(diff - 90) <= 4 or abs(diff - 180) <= 5:
                score -= 0.6
                aspects.append(f"{ep.name} hard aspect natal {np.name}")

    return EventNatalComparison(
        team="",
        synastry_score=round(score, 2),
        key_aspects=aspects[:8],
    )


def analyze_sports_horary(
    *,
    match_name: str,
    team1: str,
    team2: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    preferred_team: Optional[str] = None,
    question_text: Optional[str] = None,
) -> SportsHoraryResult:
    """Frawley-style sports horary core analysis for match outcomes."""
    init_swisseph()
    q_text = question_text or f"Who wins: {team1} vs {team2}?"

    chart = compute_western_horary(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        question_text=q_text,
        question_type="general",
    )

    lord1, lord7, _ = _team_significators(chart)
    l1 = _planet_by_name(chart, lord1)
    l7 = _planet_by_name(chart, lord7)

    s1 = float(l1.total_strength if l1 else 0.0)
    s2 = float(l7.total_strength if l7 else 0.0)

    testimonies: list[SportsTestimony] = []
    testimonies.append(SportsTestimony(
        key="primary_significators",
        value=abs(s1 - s2),
        polarity="team1" if s1 >= s2 else "team2",
        description_zh=f"主判準：L1({lord1}) vs L7({lord7}) 以尊貴與偶然尊貴比較。",
        description_en=f"Primary testimony: Lord 1 ({lord1}) vs Lord 7 ({lord7}) by dignities and accidental strength.",
    ))

    m1, m2, moon_notes = _moon_flow_bonus(chart, lord1, lord7)
    v1, v2, v_notes = _victory_house_bonus(chart, lord1, lord7)
    s1 += m1 + v1
    s2 += m2 + v2
    testimonies.extend(moon_notes)
    testimonies.extend(v_notes)

    # Preferred team mapped to 1st-house side (light weighting only).
    if preferred_team and preferred_team.strip() in {team1, team2}:
        if preferred_team.strip() == team1:
            s1 += 0.4
        else:
            s2 += 0.4
        testimonies.append(SportsTestimony(
            key="preferred_side_mapping",
            value=0.4,
            polarity="team1" if preferred_team.strip() == team1 else "team2",
            description_zh="依 Frawley 問者偏好設定 1宮映射，給予輕度權重。",
            description_en="Querent preference mapped to 1st-house side with light weighting.",
        ))

    p1, p2 = _probabilities(s1, s2)

    predicted = team1 if p1 >= p2 else team2
    score_hint = "2-1" if abs(p1 - p2) > 0.15 else "1-1 / 2-2"

    explanation = (
        f"{predicted} has the edge by classical testimonies. "
        f"Strength gap is {abs(s1 - s2):.2f}. "
        f"Suggested score reference: {score_hint}. "
        f"This is probabilistic guidance only."
    )

    jd_ut = chart.julian_day
    injury1, injury2 = _injury_risk(chart, lord1, lord7)
    upset = _upset_indicator(jd_ut)

    result = SportsHoraryResult(
        mode="horary",
        match_name=match_name,
        team1=team1,
        team2=team2,
        preferred_team=preferred_team,
        tradition="frawley_traditional",
        chart=chart,
        match_analysis=MatchAnalysis(
            team1_strength=round(s1, 2),
            team2_strength=round(s2, 2),
            key_testimonies=testimonies,
            winner_probability={team1: round(p1, 4), team2: round(p2, 4)},
            explanation=explanation,
        ),
        advanced=AdvancedPrediction(
            injury_risk_team1=round(injury1, 4),
            injury_risk_team2=round(injury2, 4),
            upset_indicator=round(upset, 4),
            season_trend_hint=_season_hint(jd_ut),
            electional_hint=_electional_hint(chart),
        ),
        timeline_transits=_timeline(datetime(year, month, day, hour, minute)),
    )

    return result


def analyze_event_chart_with_team_natal(
    *,
    event_year: int,
    event_month: int,
    event_day: int,
    event_hour: int,
    event_minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str,
    teams: list[TeamNatalInput],
) -> list[EventNatalComparison]:
    """Build event chart and compare with team/player natal charts (synastry-like dashboard)."""
    init_swisseph()
    event_chart = compute_western_chart(
        year=event_year,
        month=event_month,
        day=event_day,
        hour=event_hour,
        minute=event_minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
    )

    dashboard: list[EventNatalComparison] = []
    for t in teams:
        natal = compute_western_chart(
            year=t.year,
            month=t.month,
            day=t.day,
            hour=t.hour,
            minute=t.minute,
            timezone=t.timezone,
            latitude=t.latitude,
            longitude=t.longitude,
            location_name=t.location_name,
        )
        comp = _event_synastry_score(event_chart, natal)
        comp.team = t.team_name
        dashboard.append(comp)

    dashboard.sort(key=lambda x: x.synastry_score, reverse=True)
    return dashboard


def build_ai_interpretation_prompt(result: SportsHoraryResult, lang: str = "zh") -> str:
    """Template for ai_analysis.py richer interpretation call."""
    engine = JsonInterpretationEngine("interpretations/sports_horary.json")
    extra = engine.get_reading("sports_horary_summary", lang=lang)

    top_team = max(result.match_analysis.winner_probability, key=result.match_analysis.winner_probability.get)
    top_prob = result.match_analysis.winner_probability[top_team]

    if lang == "zh":
        base = (
            "你是傳統運動占星顧問，請嚴格依 John Frawley 與 William Lilly 規則解讀。\n"
            f"比賽：{result.match_name} ({result.team1} vs {result.team2})\n"
            f"勝率傾向：{top_team} {top_prob:.1%}\n"
            f"關鍵證據：{[t.description_zh for t in result.match_analysis.key_testimonies[:8]]}\n"
            f"進階指標：傷病風險 {result.advanced.injury_risk_team1:.1%}/{result.advanced.injury_risk_team2:.1%}，"
            f"逆轉指標 {result.advanced.upset_indicator:.1%}\n"
            "請輸出：1) 勝負傾向 2) 比分區間 3) 盤中時間點提醒 4) 風險與免責聲明。"
        )
        return f"{base}\n補充素材：{extra}" if extra else base

    base = (
        "You are a traditional sports astrology consultant. Follow John Frawley and William Lilly strictly.\n"
        f"Match: {result.match_name} ({result.team1} vs {result.team2})\n"
        f"Win edge: {top_team} {top_prob:.1%}\n"
        f"Key testimonies: {[t.description_en for t in result.match_analysis.key_testimonies[:8]]}\n"
        f"Advanced: injury risk {result.advanced.injury_risk_team1:.1%}/{result.advanced.injury_risk_team2:.1%}, "
        f"upset index {result.advanced.upset_indicator:.1%}\n"
        "Output: 1) winner tendency 2) score band 3) live timing notes 4) risk disclaimer."
    )
    return f"{base}\nExtra context: {extra}" if extra else base


def top_lots_for_sports(
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
) -> list[dict[str, Any]]:
    """Arabic Lots helper for sports context (Lot of Victory / Fortune focus)."""
    lots = compute_albiruni_lots(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        zodiac_mode="tropical",
    )
    keep = {"Lot of Victory", "Lot of Fortune", "Lot of Spirit"}
    out: list[dict[str, Any]] = []
    for x in lots.lots:
        if x.name_en in keep:
            out.append({
                "name": x.name_en,
                "longitude": round(x.longitude, 4),
                "sign": x.sign_en,
                "house": x.house,
            })
    return out
