"""Core casting and reading engine for European Geomancy."""

from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .chart import ShieldChart, build_house_chart, build_shield_chart
from .figures import FIGURES, GeomanticFigure, figure_from_pattern


QUESTION_HOUSE_MAP: Dict[str, int] = {
    "general": 1,
    "wealth": 2,
    "relationship": 7,
    "career": 10,
    "travel": 9,
    "health": 6,
}


@dataclass(frozen=True)
class GeomancyReading:
    """Complete European geomancy result."""

    question: str
    question_type: str
    cast_method: str
    seed: int
    created_at_utc: str
    mothers: List[GeomanticFigure]
    shield: ShieldChart
    houses: Dict[int, GeomanticFigure]
    focus_house: int

    def to_json(self) -> Dict[str, object]:
        """Lightweight serializable dict for history/export."""
        return {
            "question": self.question,
            "question_type": self.question_type,
            "cast_method": self.cast_method,
            "seed": self.seed,
            "created_at_utc": self.created_at_utc,
            "mothers": [m.latin for m in self.mothers],
            "judge": self.shield.judge.latin,
            "reconciler": self.shield.reconciler.latin,
            "focus_house": self.focus_house,
            "houses": {k: v.latin for k, v in self.houses.items()},
        }


def _figure_from_row_counts(row_counts: List[int]) -> GeomanticFigure:
    pattern = tuple((n % 2 == 1) for n in row_counts)
    return figure_from_pattern(pattern)


def _parse_manual_input(manual_input: str) -> List[List[int]]:
    """Parse four lines; each line contains four integers."""
    lines = [ln.strip() for ln in manual_input.strip().splitlines() if ln.strip()]
    if len(lines) != 4:
        raise ValueError("Manual input must contain exactly 4 lines.")

    out: List[List[int]] = []
    for line in lines:
        nums = [int(x) for x in re.findall(r"-?\d+", line)]
        if len(nums) != 4:
            raise ValueError("Each manual line must contain 4 integers.")
        out.append(nums)
    return out


def _generate_mother_rows(method: str, rng: random.Random, manual_input: Optional[str]) -> List[List[int]]:
    rows_for_four_mothers: List[List[int]] = []

    if method == "manual":
        if not manual_input:
            raise ValueError("Manual casting requires manual input.")
        return _parse_manual_input(manual_input)

    for _ in range(4):
        row_counts: List[int] = []
        for _row in range(4):
            if method == "coin":
                heads = sum(rng.randint(0, 1) for _ in range(3))
                row_counts.append(heads)
            elif method == "number":
                row_counts.append(rng.randint(1, 99))
            else:  # traditional
                row_counts.append(rng.randint(1, 17))
        rows_for_four_mothers.append(row_counts)
    return rows_for_four_mothers


def generate_reading(
    question: str,
    question_type: str = "general",
    cast_method: str = "traditional",
    seed: Optional[int] = None,
    manual_input: Optional[str] = None,
) -> GeomancyReading:
    """Generate a full European Geomancy reading."""
    actual_seed = seed if seed is not None else int(time.time() * 1000)
    rng = random.Random(actual_seed)

    mother_rows = _generate_mother_rows(cast_method, rng, manual_input)
    mothers = [_figure_from_row_counts(rows) for rows in mother_rows]

    shield = build_shield_chart(mothers, figure_from_pattern)
    houses = build_house_chart(shield)
    focus_house = QUESTION_HOUSE_MAP.get(question_type, 1)

    return GeomancyReading(
        question=question.strip() or "未提供問題",
        question_type=question_type,
        cast_method=cast_method,
        seed=actual_seed,
        created_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        mothers=mothers,
        shield=shield,
        houses=houses,
        focus_house=focus_house,
    )


def list_figure_names() -> List[str]:
    """Return all 16 Latin figure names."""
    return list(FIGURES.keys())
