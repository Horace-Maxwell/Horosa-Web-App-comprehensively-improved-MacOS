"""Kinketika 輪盤圖渲染。"""

from __future__ import annotations

from typing import Iterable, Tuple

import plotly.graph_objects as go

from .ketika_data import FORTUNE_LABELS, KetikaPeriod, time_to_minutes

try:
    from frontend.custom_theme import MANUSCRIPT_THEMES
except Exception:  # pragma: no cover
    MANUSCRIPT_THEMES = {}

INACTIVE_PERIOD_OPACITY = 0.42


def _period_span_degrees(period: KetikaPeriod) -> Tuple[float, float]:
    """24 小時映射為 360 度。"""
    start_minute = time_to_minutes(period.time_start)
    end_minute = time_to_minutes(period.time_end)
    if end_minute <= start_minute:
        span_minute = (24 * 60 - start_minute) + end_minute
    else:
        span_minute = end_minute - start_minute
    start_deg = start_minute / (24 * 60) * 360
    span_deg = span_minute / (24 * 60) * 360
    return start_deg, span_deg


def make_wheel(
    periods: Iterable[KetikaPeriod],
    *,
    lang: str = "zh",
    current_index: int | None = None,
    title: str = "",
) -> go.Figure:
    """建立 manuscript 風格互動輪盤。"""
    theme = MANUSCRIPT_THEMES.get(
        "nusantara_malay",
        {
            "paper": "rgba(255,248,230,0.84)",
            "grid": "#E8DCC8",
            "line": "#BFA97A",
            "title": "#3E2723",
            "legend": "rgba(255,248,230,0.88)",
        },
    )

    fig = go.Figure()
    for period in periods:
        start_deg, span_deg = _period_span_degrees(period)
        theta_center = start_deg + span_deg / 2
        period_name = period.name_zh if lang == "zh" else period.name_en
        fortune_label = FORTUNE_LABELS[period.fortune][lang]
        opacity = 1.0 if current_index in (None, period.index) else INACTIVE_PERIOD_OPACITY
        fig.add_trace(
            go.Barpolar(
                r=[1],
                theta=[theta_center],
                width=[span_deg],
                marker_color=period.colour,
                marker_line_color="#FFFFFF",
                marker_line_width=2,
                opacity=opacity,
                name=period_name,
                text=f"{period.emoji} {period_name}<br>{fortune_label}<br>{period.time_start}–{period.time_end}",
                hoverinfo="text",
            )
        )

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color=theme["title"])),
        polar=dict(
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                tickmode="array",
                tickvals=[0, 90, 180, 270],
                ticktext=["00:00", "06:00", "12:00", "18:00"],
                linecolor=theme["line"],
                gridcolor=theme["grid"],
            ),
            radialaxis=dict(visible=False),
            bgcolor=theme["paper"],
        ),
        showlegend=True,
        legend=dict(
            font=dict(size=11),
            bgcolor=theme["legend"],
            bordercolor=theme["line"],
            borderwidth=1,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=60, b=20, l=20, r=20),
        height=560,
    )
    return fig
