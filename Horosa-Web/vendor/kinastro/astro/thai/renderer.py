"""Thai Duang Chata SVG renderers.

Renderer helpers are isolated from computation and can be used by Streamlit or API
output layers. Includes renderers for both Duang Chata wheels and Nine Palace grids.
"""

from __future__ import annotations

import html
import math
from typing import Any, Dict

PLANET_COLORS: Dict[str, str] = {
    "sun": "#ff9f1c",
    "moon": "#d8e2f2",
    "mars": "#ef476f",
    "mercury": "#5fa8d3",
    "jupiter": "#ffd166",
    "venus": "#ff7eb6",
    "saturn": "#8d6a9f",
    "rahu": "#9b5de5",
    "ketu": "#4361ee",
}

SIGNS = [
    {"en": "Aries", "zh": "白羊", "th": "เมษ", "glyph": "♈"},
    {"en": "Taurus", "zh": "金牛", "th": "พฤษภ", "glyph": "♉"},
    {"en": "Gemini", "zh": "雙子", "th": "เมถุน", "glyph": "♊"},
    {"en": "Cancer", "zh": "巨蟹", "th": "กรกฎ", "glyph": "♋"},
    {"en": "Leo", "zh": "獅子", "th": "สิงห์", "glyph": "♌"},
    {"en": "Virgo", "zh": "處女", "th": "กันย์", "glyph": "♍"},
    {"en": "Libra", "zh": "天秤", "th": "ตุลย์", "glyph": "♎"},
    {"en": "Scorpio", "zh": "天蠍", "th": "พิจิก", "glyph": "♏"},
    {"en": "Sagittarius", "zh": "射手", "th": "ธนู", "glyph": "♐"},
    {"en": "Capricorn", "zh": "摩羯", "th": "มกร", "glyph": "♑"},
    {"en": "Aquarius", "zh": "水瓶", "th": "กุมภ์", "glyph": "♒"},
    {"en": "Pisces", "zh": "雙魚", "th": "มีน", "glyph": "♓"},
]

_THAI_NUM = {"0": "๐", "1": "๑", "2": "๒", "3": "๓", "4": "๔", "5": "๕", "6": "๖", "7": "๗", "8": "๘", "9": "๙"}

_COPY: Dict[str, Dict[str, str]] = {
    "title": {"zh": "泰國 Duang Chata", "en": "Thai Duang Chata", "th": "ดวงชะตาไทย"},
    "fortune": {"zh": "命數", "en": "Fortune", "th": "เลขชะตา"},
    "house": {"zh": "宮", "en": "H", "th": "ภพ"},
    "nine_palace": {"zh": "九宮占", "en": "Nine Palace", "th": "เก้าช่องชะตา"},
    "strength": {"zh": "氣力", "en": "Strength", "th": "กำลัง"},
}


def _t(key: str, lang: str) -> str:
    data = _COPY.get(key, {})
    return data.get(lang) or data.get("zh") or key


def _to_thai_digits(value: int) -> str:
    return "".join(_THAI_NUM.get(ch, ch) for ch in str(value))


def _polar(cx: float, cy: float, r: float, angle_deg: float) -> tuple[float, float]:
    rad = math.radians(angle_deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def build_duang_chata_svg(chart: Any, *, lang: str = "zh", size: int = 680) -> str:
    """Build a Thai-style circular Duang Chata SVG."""
    cx = cy = size / 2
    r_outer = size * 0.43
    r_inner = size * 0.30
    r_planet = size * 0.35
    r_house_label = size * 0.385

    house_colors = [
        "#57241b", "#4d2030", "#3e2246", "#2f2450", "#252a5a", "#1f355e",
        "#1d3f58", "#1f494f", "#255144", "#315737", "#445b2f", "#555c2b",
    ]

    parts = [
        '<div style="width:100%;max-width:760px;margin:0 auto;overflow-x:auto;">',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" style="width:100%;height:auto;display:block;">',
        f'<rect x="0" y="0" width="{size}" height="{size}" fill="#121326" rx="20"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer + 10}" fill="none" stroke="#d4af37" stroke-width="2" opacity="0.7"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="#19142c" stroke="#d4af37" stroke-width="1.5"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="#120f21" stroke="#a8862d" stroke-width="1.2"/>',
    ]

    for i in range(12):
        start = i * 30
        end = start + 30
        a1 = math.radians(start - 90)
        a2 = math.radians(end - 90)

        x1o, y1o = cx + r_outer * math.cos(a1), cy + r_outer * math.sin(a1)
        x2o, y2o = cx + r_outer * math.cos(a2), cy + r_outer * math.sin(a2)
        x1i, y1i = cx + r_inner * math.cos(a1), cy + r_inner * math.sin(a1)
        x2i, y2i = cx + r_inner * math.cos(a2), cy + r_inner * math.sin(a2)

        path = (
            f"M {x1i:.2f} {y1i:.2f} L {x1o:.2f} {y1o:.2f} "
            f"A {r_outer:.2f} {r_outer:.2f} 0 0 1 {x2o:.2f} {y2o:.2f} "
            f"L {x2i:.2f} {y2i:.2f} "
            f"A {r_inner:.2f} {r_inner:.2f} 0 0 0 {x1i:.2f} {y1i:.2f} Z"
        )

        parts.append(
            f'<path d="{path}" fill="{house_colors[i]}" fill-opacity="0.55" stroke="#b08d2f" stroke-width="0.6"/>'
        )

        center_angle = start + 15
        hx, hy = _polar(cx, cy, r_house_label, center_angle)
        bhava_num = chart.houses[i].number
        sign = SIGNS[chart.houses[i].sign_index]
        parts.append(
            f'<text x="{hx:.2f}" y="{hy:.2f}" text-anchor="middle" dominant-baseline="middle" '
            f'fill="#f1d58a" font-size="11" font-weight="bold">'
            f'{_t("house", lang)}{_to_thai_digits(bhava_num)} {sign["glyph"]}</text>'
        )

    for planet in chart.planets:
        angle = planet.longitude
        px, py = _polar(cx, cy, r_planet, angle)
        color = PLANET_COLORS.get(planet.key, "#f0f0f0")
        sign_name = SIGNS[planet.sign_index].get(lang) or SIGNS[planet.sign_index]["zh"]
        label = html.escape(f"{planet.symbol} {sign_name} {planet.sign_degree:.1f}°")
        parts.append(
            f'<circle cx="{px:.2f}" cy="{py:.2f}" r="12" fill="#0b0b14" stroke="{color}" stroke-width="1.4">'
            f'<title>{label}</title></circle>'
        )
        parts.append(
            f'<text x="{px:.2f}" y="{py:.2f}" text-anchor="middle" dominant-baseline="middle" '
            f'fill="{color}" font-size="13" font-weight="bold">{planet.symbol}</text>'
        )

    parts.extend(
        [
            f'<circle cx="{cx}" cy="{cy}" r="{size * 0.115}" fill="#1d1420" stroke="#d4af37" stroke-width="1.6"/>',
            f'<text x="{cx}" y="{cy - 28}" text-anchor="middle" fill="#d4af37" font-size="14" font-weight="bold">{_t("title", lang)}</text>',
            f'<text x="{cx}" y="{cy - 8}" text-anchor="middle" fill="#f0d188" font-size="12">{chart.day:02d}/{chart.month:02d}/{chart.year}</text>',
            f'<text x="{cx}" y="{cy + 12}" text-anchor="middle" fill="#f0d188" font-size="12">{chart.hour:02d}:{chart.minute:02d} UTC{chart.timezone:+.1f}</text>',
            f'<text x="{cx}" y="{cy + 33}" text-anchor="middle" fill="#ffcf56" font-size="13" font-weight="bold">{_t("fortune", lang)}: {_to_thai_digits(chart.fortune_number)}</text>',
        ]
    )

    parts.append("</svg></div>")
    return "\n".join(parts)


def build_nine_palace_svg(grid: Any, *, lang: str = "zh", size: int = 540) -> str:
    """Build a 3×3 Nine Palace SVG from `compute_nine_palace_grid(...)` output."""
    cell = size // 3
    palace_map = {palace.palace_number: palace for palace in grid.palaces}
    width = cell * 3
    height = cell * 3 + 56

    parts = [
        '<div style="width:100%;max-width:620px;margin:0 auto;overflow-x:auto;">',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" style="width:100%;height:auto;display:block;">',
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="18" fill="#151427"/>',
        f'<text x="{width / 2:.1f}" y="30" text-anchor="middle" fill="#f4d47a" font-size="22" font-weight="bold">{_t("nine_palace", lang)}</text>',
        f'<text x="{width / 2:.1f}" y="50" text-anchor="middle" fill="#b9b8d1" font-size="11">{_t("fortune", lang)} {grid.fortune_activation_palace}</text>',
    ]

    for row in range(3):
        for col in range(3):
            palace_number = grid.layout[row][col]
            palace = palace_map[palace_number]
            x = col * cell
            y = row * cell + 56
            highlight = "#f3c969" if palace.is_brahma_jati_activated else ("#7bdff2" if palace.is_fortune_activated else "#2b2744")
            stroke = "#ffd166" if palace.is_brahma_jati_activated else ("#7bdff2" if palace.is_fortune_activated else "#5c5678")
            guardian_color = PLANET_COLORS.get(palace.guardian_planet, "#f0f0f0")
            title = html.escape(palace.title.get(lang) or palace.title.get("zh") or "")
            direction = html.escape(palace.direction.get(lang) or palace.direction.get("zh") or "")
            strength_label = html.escape(palace.strength_label.get(lang) or palace.strength_label.get("zh") or "")
            keywords = palace.keywords.get(lang) or palace.keywords.get("zh") or []
            keyword_text = html.escape(" · ".join(keywords[:2]))
            influence_symbols = " ".join(influence.symbol for influence in palace.main_influences)
            influence_title = html.escape(", ".join(
                influence.name.get(lang) or influence.name.get("zh") or influence.key
                for influence in palace.main_influences
            ))

            parts.append(
                f'<rect x="{x + 6}" y="{y + 6}" width="{cell - 12}" height="{cell - 12}" rx="14" fill="{highlight}" fill-opacity="0.12" stroke="{stroke}" stroke-width="2"/>'
            )
            parts.append(
                f'<text x="{x + 16}" y="{y + 24}" fill="#f3d58a" font-size="14" font-weight="bold">{palace_number}</text>'
            )
            parts.append(
                f'<text x="{x + cell - 16}" y="{y + 24}" text-anchor="end" fill="#d8d5ea" font-size="11">{direction}</text>'
            )
            parts.append(
                f'<text x="{x + cell / 2:.1f}" y="{y + 52}" text-anchor="middle" fill="#ffffff" font-size="15" font-weight="bold">{title}</text>'
            )
            parts.append(
                f'<text x="{x + cell / 2:.1f}" y="{y + 78}" text-anchor="middle" fill="{guardian_color}" font-size="24" font-weight="bold">{influence_symbols}<title>{influence_title}</title></text>'
            )
            parts.append(
                f'<text x="{x + cell / 2:.1f}" y="{y + 103}" text-anchor="middle" fill="#c7c2da" font-size="11">{keyword_text}</text>'
            )
            parts.append(
                f'<text x="{x + 18}" y="{y + cell - 34}" fill="#f4d47a" font-size="11">{_t("strength", lang)} {palace.strength}</text>'
            )
            parts.append(
                f'<text x="{x + cell - 18}" y="{y + cell - 34}" text-anchor="end" fill="#c7c2da" font-size="11">{strength_label}</text>'
            )
            if palace.activation_note:
                note = html.escape(palace.activation_note.get(lang) or palace.activation_note.get("zh") or "")
                parts.append(
                    f'<text x="{x + cell / 2:.1f}" y="{y + cell - 14}" text-anchor="middle" fill="#9bd1ff" font-size="9">★<title>{note}</title></text>'
                )

    parts.append("</svg></div>")
    return "\n".join(parts)


def render_streamlit(chart: Any, *, lang: str = "zh") -> None:
    """Streamlit entry (lazy import style compatible)."""
    import streamlit as st

    st.markdown(build_duang_chata_svg(chart, lang=lang), unsafe_allow_html=True)
    if getattr(chart, "nine_palace_grid", None):
        st.markdown(build_nine_palace_svg(chart.nine_palace_grid, lang=lang), unsafe_allow_html=True)
