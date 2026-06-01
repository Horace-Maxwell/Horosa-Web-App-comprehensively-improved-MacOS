"""astro/burmese/renderer.py

Phase-1 renderer for Burmese Mahabote wheel.
"""

from __future__ import annotations

import math
from html import escape

from .mahabote import BurmeseMahaboteChart, Language

WHEEL_START_ANGLE_DEGREES = -157.5  # Centers the NE segment at top-right, then clockwise.


def build_mahabote_wheel_svg(chart: BurmeseMahaboteChart, lang: Language = "zh", size: int = 520) -> str:
    """Build a phase-1 Burmese Mahabote 8-segment wheel SVG.

    Parameters
    ----------
    chart : BurmeseMahaboteChart
        Precomputed Mahabote phase-1 chart data.
    lang : {"zh", "en"}
        Output label language for direction/planet/house text.
    size : int
        SVG canvas size in pixels (width = height = size).
    """
    cx, cy = size / 2, size / 2
    r_outer = size * 0.46
    r_inner = size * 0.2
    r_symbol = size * 0.34
    r_label = size * 0.41
    r_animal = size * 0.27

    title = "緬甸 Mahabote 八曜輪盤" if lang == "zh" else "Burmese Mahabote 8-Symbol Wheel"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" role="img" aria-label="{escape(title)}" style="max-width:100%;height:auto;">',
        f'<rect x="0" y="0" width="{size}" height="{size}" fill="#101426" rx="16"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="#1A2038" stroke="#D4AF37" stroke-width="3"/>',
    ]

    for idx, sec in enumerate(chart.wheel_symbols):
        a0 = math.radians(WHEEL_START_ANGLE_DEGREES + idx * 45)
        a1 = math.radians(WHEEL_START_ANGLE_DEGREES + (idx + 1) * 45)
        am = math.radians(WHEEL_START_ANGLE_DEGREES + idx * 45 + 22.5)

        x0o, y0o = cx + r_outer * math.cos(a0), cy + r_outer * math.sin(a0)
        x1o, y1o = cx + r_outer * math.cos(a1), cy + r_outer * math.sin(a1)
        x0i, y0i = cx + r_inner * math.cos(a0), cy + r_inner * math.sin(a0)
        x1i, y1i = cx + r_inner * math.cos(a1), cy + r_inner * math.sin(a1)

        color = str(sec["color"])
        is_birth = idx == chart.symbol_index
        is_birth_house_marker = idx == chart.birth_house_index

        path = (
            f"M {x0i:.2f} {y0i:.2f} L {x0o:.2f} {y0o:.2f} "
            f"A {r_outer:.2f} {r_outer:.2f} 0 0 1 {x1o:.2f} {y1o:.2f} "
            f"L {x1i:.2f} {y1i:.2f} "
            f"A {r_inner:.2f} {r_inner:.2f} 0 0 0 {x0i:.2f} {y0i:.2f} Z"
        )

        stroke = "#FFD700" if is_birth else "#7A6A3A"
        stroke_w = "3" if is_birth else "1.2"
        fill_opacity = "0.50" if is_birth else "0.20"

        parts.append(
            f'<path d="{path}" fill="{escape(color)}" fill-opacity="{fill_opacity}" stroke="{stroke}" stroke-width="{stroke_w}"/>'
        )

        if is_birth_house_marker:
            bx = cx + (r_outer + 10) * math.cos(am)
            by = cy + (r_outer + 10) * math.sin(am)
            parts.append(f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="4" fill="#FFD700"/>')

        lx = cx + r_label * math.cos(am)
        ly = cy + r_label * math.sin(am)
        sx = cx + r_symbol * math.cos(am)
        sy = cy + r_symbol * math.sin(am)
        ax = cx + r_animal * math.cos(am)
        ay = cy + r_animal * math.sin(am)

        direction = sec["direction_zh"] if lang == "zh" else sec["direction"]
        animal = sec["animal_zh"] if lang == "zh" else sec["animal"]

        parts.append(
            f'<text x="{lx:.2f}" y="{ly:.2f}" fill="#EAC57A" font-size="11" text-anchor="middle" dominant-baseline="middle" font-weight="700">{escape(str(direction))}</text>'
        )
        parts.append(
            f'<text x="{sx:.2f}" y="{sy:.2f}" fill="{escape(color)}" font-size="24" text-anchor="middle" dominant-baseline="middle">{escape(str(sec["planet_symbol"]))}</text>'
        )
        parts.append(
            f'<text x="{ax:.2f}" y="{ay:.2f}" fill="#FFFFFF" font-size="9" text-anchor="middle" dominant-baseline="middle">{escape(str(sec["animal_icon"]))} {escape(str(animal))}</text>'
        )

    center_symbol = chart.wheel_symbols[chart.symbol_index]
    center_planet = center_symbol["planet_zh"] if lang == "zh" else center_symbol["planet"]
    center_house = chart.houses[chart.birth_house_index].house_name_zh if lang == "zh" else chart.houses[chart.birth_house_index].house_name_en
    parts.extend([
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="#0D1224" stroke="#D4AF37" stroke-width="2"/>',
        f'<text x="{cx}" y="{cy - 20}" fill="#EAC57A" font-size="10" text-anchor="middle">{escape(title)}</text>',
        f'<text x="{cx}" y="{cy + 4}" fill="#FFD700" font-size="30" text-anchor="middle">{escape(str(center_symbol["planet_symbol"]))}</text>',
        f'<text x="{cx}" y="{cy + 24}" fill="#FFFFFF" font-size="12" text-anchor="middle">{escape(str(center_planet))}</text>',
        f'<text x="{cx}" y="{cy + 40}" fill="#B8C2D9" font-size="10" text-anchor="middle">{escape(str(center_house))} · ME {chart.myanmar_year}</text>',
        "</svg>",
    ])
    return "\n".join(parts)


def render_mahabote_basic(chart: BurmeseMahaboteChart, lang: Language = "zh", wheel_size: int = 520) -> None:
    import streamlit as st

    st.markdown(build_mahabote_wheel_svg(chart, lang=lang, size=wheel_size), unsafe_allow_html=True)

    title = "八宮位對應" if lang == "zh" else "Eight House Mapping"
    st.subheader(title)

    rows = []
    for house in chart.houses:
        rows.append(
            {
                "宮位" if lang == "zh" else "House": house.house_name_zh if lang == "zh" else house.house_name_en,
                "主題" if lang == "zh" else "Theme": house.theme_zh if lang == "zh" else house.theme_en,
                "方向" if lang == "zh" else "Direction": house.direction_zh if lang == "zh" else house.direction,
                "星曜" if lang == "zh" else "Planet": house.planet_zh if lang == "zh" else house.planet,
                "動物" if lang == "zh" else "Animal": f"{house.animal_icon} {house.animal_zh if lang == 'zh' else house.animal}",
                "命宮" if lang == "zh" else "Birth": "✓" if house.is_birth_house else "",
            }
        )

    st.dataframe(rows, width="stretch", hide_index=True)


__all__ = ["build_mahabote_wheel_svg", "render_mahabote_basic"]
