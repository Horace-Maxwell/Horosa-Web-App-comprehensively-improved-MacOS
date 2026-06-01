"""Shield chart and House chart generation/rendering for European Geomancy."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List

from .figures import GeomanticFigure, render_figure_svg


HOUSE_TOPICS: Dict[int, str] = {
    1: "Querent, body, temperament",
    2: "Wealth, movable goods",
    3: "Siblings, short travel, messages",
    4: "Home, foundations, endings",
    5: "Children, joy, creativity",
    6: "Illness, labor, service",
    7: "Marriage, partners, open rivals",
    8: "Death, fear, inheritances",
    9: "Faith, law, long journeys",
    10: "Authority, career, reputation",
    11: "Friends, patrons, hopes",
    12: "Secrets, exile, hidden enemies",
}


@dataclass(frozen=True)
class ShieldChart:
    """Classical 16-figure shield chain."""

    mothers: List[GeomanticFigure]
    daughters: List[GeomanticFigure]
    nieces: List[GeomanticFigure]
    witnesses: List[GeomanticFigure]
    judge: GeomanticFigure
    reconciler: GeomanticFigure

    @property
    def figures_16(self) -> List[GeomanticFigure]:
        return [
            *self.mothers,
            *self.daughters,
            *self.nieces,
            self.witnesses[0],
            self.witnesses[1],
            self.judge,
            self.reconciler,
        ]


def combine_figures(a: GeomanticFigure, b: GeomanticFigure, figure_from_pattern) -> GeomanticFigure:
    """Geomantic addition rule: odd+even -> single, parity represented by XOR."""
    pattern = tuple(x ^ y for x, y in zip(a.pattern, b.pattern))
    return figure_from_pattern(pattern)


def derive_daughters(mothers: List[GeomanticFigure], figure_from_pattern) -> List[GeomanticFigure]:
    """Transpose mother rows into four daughters."""
    daughters: List[GeomanticFigure] = []
    for row_idx in range(4):
        pattern = tuple(m.pattern[row_idx] for m in mothers)
        daughters.append(figure_from_pattern(pattern))
    return daughters


def build_shield_chart(mothers: List[GeomanticFigure], figure_from_pattern) -> ShieldChart:
    """Build complete shield chain from four mothers."""
    daughters = derive_daughters(mothers, figure_from_pattern)
    nieces = [
        combine_figures(mothers[0], mothers[1], figure_from_pattern),
        combine_figures(mothers[2], mothers[3], figure_from_pattern),
        combine_figures(daughters[0], daughters[1], figure_from_pattern),
        combine_figures(daughters[2], daughters[3], figure_from_pattern),
    ]
    witnesses = [
        combine_figures(nieces[0], nieces[1], figure_from_pattern),
        combine_figures(nieces[2], nieces[3], figure_from_pattern),
    ]
    judge = combine_figures(witnesses[0], witnesses[1], figure_from_pattern)
    reconciler = combine_figures(judge, mothers[0], figure_from_pattern)
    return ShieldChart(
        mothers=mothers,
        daughters=daughters,
        nieces=nieces,
        witnesses=witnesses,
        judge=judge,
        reconciler=reconciler,
    )


def build_house_chart(shield: ShieldChart) -> Dict[int, GeomanticFigure]:
    """Map 12 houses from shield chain (M1-4, D1-4, N1-4)."""
    first_twelve = shield.figures_16[:12]
    return {house: first_twelve[house - 1] for house in range(1, 13)}


def render_shield_chart_svg(shield: ShieldChart) -> str:
    """Render shield chart as SVG."""
    labels = [
        "Mother I", "Mother II", "Mother III", "Mother IV",
        "Daughter I", "Daughter II", "Daughter III", "Daughter IV",
        "Niece I", "Niece II", "Niece III", "Niece IV",
        "Right Witness", "Left Witness", "Judge", "Reconciler",
    ]
    figures = shield.figures_16
    cell_w = 186
    cell_h = 160
    cols = 4
    rows = 4
    width = cell_w * cols + 40
    height = cell_h * rows + 80

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#0A0E16"/>',
        f'<rect x="10" y="10" width="{width-20}" height="{height-20}" fill="none" stroke="#8D6B39" stroke-width="2"/>',
        '<text x="50%" y="32" text-anchor="middle" fill="#D9BC7A" font-family="serif" font-size="22">European Geomancy Shield Chart</text>',
    ]

    for idx, figure in enumerate(figures):
        r, c = divmod(idx, 4)
        x = 20 + c * cell_w
        y = 50 + r * cell_h
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cell_w-8}" height="{cell_h-8}" rx="8" fill="#101828" stroke="#5E4725" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x+10}" y="{y+20}" fill="#BFA06A" font-size="12" font-family="serif">{labels[idx]}</text>'
        )
        inner = render_figure_svg(figure, width=96, with_title=False)
        parts.append(f'<g transform="translate({x+40},{y+28}) scale(0.95)">{inner}</g>')
        parts.append(
            f'<text x="{x + (cell_w-8)/2:.1f}" y="{y+140}" text-anchor="middle" fill="#E8D8B1" font-size="12" font-family="serif">{figure.latin}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


def render_house_chart_svg(houses: Dict[int, GeomanticFigure]) -> str:
    """Render 12-house radial chart with geomantic placements."""
    width = 860
    height = 860
    cx = width / 2
    cy = height / 2
    r_outer = 360
    r_mid = 285
    r_inner = 175

    def polar(radius: float, deg: float) -> tuple[float, float]:
        rad = math.radians(deg)
        return cx + radius * math.cos(rad), cy - radius * math.sin(rad)

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        f'<rect width="{width}" height="{height}" fill="#0B101A"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" stroke="#A88447" stroke-width="2"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_mid}" fill="none" stroke="#6E5631" stroke-width="1.2"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="#111A2A" stroke="#4D3B22" stroke-width="1"/>',
        '<text x="50%" y="46" text-anchor="middle" fill="#D9BC7A" font-family="serif" font-size="22">European Geomancy House Chart</text>',
    ]

    for house in range(1, 13):
        start = 180 - (house - 1) * 30
        mid = start - 15
        x1, y1 = polar(r_inner, start)
        x2, y2 = polar(r_outer, start)
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#5A4528" stroke-width="1"/>')

        hx, hy = polar((r_outer + r_mid) / 2, mid)
        parts.append(f'<text x="{hx:.1f}" y="{hy:.1f}" text-anchor="middle" fill="#CBAE74" font-size="16" font-family="serif">{house}</text>')

        tx, ty = polar((r_mid + r_inner) / 2, mid)
        topic = HOUSE_TOPICS[house]
        parts.append(f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" fill="#9EB0CC" font-size="9" font-family="serif">{topic}</text>')

        figure = houses[house]
        fx, fy = polar(r_inner - 65, mid)
        parts.append(f'<g transform="translate({fx-42:.1f},{fy-48:.1f}) scale(0.72)">{render_figure_svg(figure, width=96, with_title=False)}</g>')
        parts.append(f'<text x="{fx:.1f}" y="{fy+46:.1f}" text-anchor="middle" fill="#E4D2A8" font-size="11" font-family="serif">{figure.latin}</text>')

    parts.append("</svg>")
    return "".join(parts)
