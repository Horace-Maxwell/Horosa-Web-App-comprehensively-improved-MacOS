"""Interpretation helpers for European Geomancy."""

from __future__ import annotations

from typing import Dict

from .chart import HOUSE_TOPICS
from .engine import GeomancyReading


def structured_interpretation(reading: GeomancyReading, lang: str = "zh") -> Dict[str, str]:
    """Return structured reading blocks."""
    focus = reading.focus_house
    focus_figure = reading.houses[focus]
    judge = reading.shield.judge
    left_witness, right_witness = reading.shield.witnesses

    if lang == "en":
        return {
            "current_state": (
                f"Current state is ruled by House {focus} ({HOUSE_TOPICS[focus]}) with {focus_figure.latin}, "
                f"showing {', '.join(focus_figure.positive_keywords)}."
            ),
            "development": (
                f"The witnesses {left_witness.latin} and {right_witness.latin} describe the process tension "
                "between available support and pressure."
            ),
            "aids_obstacles": (
                f"Helpful vectors: {', '.join(reading.shield.reconciler.positive_keywords)}; "
                f"obstacles: {', '.join(judge.negative_keywords)}."
            ),
            "outcome": (
                f"Final outcome leans toward {judge.latin}: {judge.historical_meaning}"
            ),
        }

    return {
        "current_state": (
            f"現況以第{focus}宮（{HOUSE_TOPICS[focus]}）為主，落入 {focus_figure.latin}，"
            f"主題偏向：{', '.join(focus_figure.positive_keywords)}。"
        ),
        "development": (
            f"左右見證 {left_witness.latin} / {right_witness.latin} 代表事件推進中的拉扯與轉折。"
        ),
        "aids_obstacles": (
            f"助力可取 {', '.join(reading.shield.reconciler.positive_keywords)}；"
            f"阻力需防 {', '.join(judge.negative_keywords)}。"
        ),
        "outcome": f"最終判官為 {judge.latin}：{judge.historical_meaning}",
    }


def astrology_bridge_interpretation(reading: GeomancyReading, lang: str = "zh") -> str:
    """Bridge geomancy with astrological correspondences."""
    asc = reading.mothers[0]
    judge = reading.shield.judge
    if lang == "en":
        return (
            f"Astrological bridge: Ascendant figure {asc.latin} links to {asc.planet} in {asc.zodiac}, "
            f"while the Judge {judge.latin} points to {judge.planet}/{judge.zodiac}. "
            "Read timing through planetary hours and the relevant house rulers for stronger Renaissance-style judgement."
        )
    return (
        f"占星連結：上升圖形 {asc.latin} 對應 {asc.planet}（{asc.zodiac}），"
        f"判官 {judge.latin} 對應 {judge.planet}（{judge.zodiac}）。"
        "建議配合行星時與宮主星進一步判時，符合文藝復興地占—占星合參傳統。"
    )


def build_ai_prompt(reading: GeomancyReading, lang: str = "zh") -> str:
    """Build AI prompt context text."""
    s = structured_interpretation(reading, lang=lang)
    lines = [
        "European Geomancy Reading",
        f"Question: {reading.question}",
        f"Casting method: {reading.cast_method}",
        f"Seed: {reading.seed}",
        f"Judge: {reading.shield.judge.latin}",
        f"Reconciler: {reading.shield.reconciler.latin}",
        "",
        "Structured interpretation:",
        f"- Current state: {s['current_state']}",
        f"- Development: {s['development']}",
        f"- Aids/Obstacles: {s['aids_obstacles']}",
        f"- Outcome: {s['outcome']}",
        "",
        astrology_bridge_interpretation(reading, lang=lang),
    ]
    return "\n".join(lines)
