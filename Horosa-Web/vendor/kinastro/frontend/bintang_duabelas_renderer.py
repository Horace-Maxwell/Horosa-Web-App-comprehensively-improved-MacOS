"""
frontend/bintang_duabelas_renderer.py
=====================================

Bintang Duabelas 文化視覺化渲染器：
- 十二星宮圓形輪盤（12 Rumah）
- 行星時辰日夜輪（Planetary Hours 12+12）
"""

from __future__ import annotations

import math
from typing import Any

import plotly.graph_objects as go
import streamlit as st

from astro.bintang_duabelas.visuals import (
    DisplayScript,
    HouseWheelSegment,
    PlanetaryHourSegment,
    build_house_wheel_segments,
    build_planetary_hour_segments,
)
from astro.chart_theme import apply_chart_theme

_GREEN_DEEP = "#006400"
_GOLD = "#D4AF77"
_NIGHT_BLUE = "#0F172A"
_RING_DAY = "rgba(0, 100, 0, 0.20)"
_RING_NIGHT = "rgba(17, 42, 64, 0.30)"


def _extract_selected_house(selection_event: Any) -> int | None:
    """從 Streamlit Plotly selection 事件提取被點擊宮位。"""
    if not selection_event:
        return None
    selection = selection_event.get("selection") if isinstance(selection_event, dict) else None
    if not isinstance(selection, dict):
        return None
    points = selection.get("points")
    if not isinstance(points, list) or not points:
        return None
    customdata = points[0].get("customdata", [])
    if isinstance(customdata, list) and customdata:
        try:
            return int(customdata[0])
        except (TypeError, ValueError):
            return None
    return None


def _house_ring_trace(segments: list[HouseWheelSegment]) -> go.Barpolar:
    """建立十二宮輪盤扇區 trace。"""
    return go.Barpolar(
        r=[1.0] * len(segments),
        theta=[segment.theta_deg for segment in segments],
        width=[segment.width_deg for segment in segments],
        marker=dict(
            color=[segment.fill_color for segment in segments],
            line=dict(color=[segment.border_color for segment in segments], width=2),
        ),
        customdata=[[segment.house_number] for segment in segments],
        text=[f"{segment.label}<br>{segment.subtitle}" for segment in segments],
        hovertext=[segment.hover_html for segment in segments],
        hovertemplate="%{hovertext}<extra></extra>",
        opacity=0.95,
    )


def _render_house_annotations(fig: go.Figure, segments: list[HouseWheelSegment]) -> None:
    """在輪盤中央周圍補上 Rumah 文字。"""
    for segment in segments:
        fig.add_annotation(
            x=0.5 + 0.30 * math.cos(math.radians(segment.theta_deg)),
            y=0.5 + 0.30 * math.sin(math.radians(segment.theta_deg)),
            xref="paper",
            yref="paper",
            text=segment.label,
            showarrow=False,
            font=dict(size=10, color="#F5DEB3"),
        )


def _build_house_wheel_figure(segments: list[HouseWheelSegment]) -> go.Figure:
    """建立十二宮圓盤圖。"""
    fig = go.Figure()
    fig.add_trace(_house_ring_trace(segments))
    _render_house_annotations(fig, segments)
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        text="☪ 12 Rumah",
        showarrow=False,
        font=dict(size=18, color=_GOLD, family="Noto Naskh Arabic, serif"),
    )
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=False, range=[0, 1.2]),
            angularaxis=dict(showgrid=False, ticks="", direction="clockwise", rotation=90),
        ),
        paper_bgcolor=_NIGHT_BLUE,
        height=560,
        margin=dict(l=12, r=12, t=24, b=12),
    )
    apply_chart_theme(fig)
    return fig


def render_twelve_houses_wheel(
    houses: list[dict[str, Any]],
    *,
    highlight_house: int | None = None,
    script: DisplayScript = "zh",
    chart_key: str = "bd_house_wheel",
) -> int | None:
    """渲染十二星宮圓盤，並回傳點擊選中的宮位編號。"""
    segments = build_house_wheel_segments(houses, highlight_house=highlight_house, script=script)
    fig = _build_house_wheel_figure(segments)
    try:
        event = st.plotly_chart(fig, width="stretch", key=chart_key, on_select="rerun")
    except TypeError:
        st.plotly_chart(fig, width="stretch", key=chart_key)
        return None
    return _extract_selected_house(event)


def _hour_ring_trace(
    segments: list[PlanetaryHourSegment],
    phase: str,
) -> go.Barpolar:
    """建立日時/夜時的同心圓 trace。"""
    phase_segments = [segment for segment in segments if segment.phase == phase]
    radius = 0.82
    base = 0.95 if phase == "day" else 2.0
    return go.Barpolar(
        r=[radius] * len(phase_segments),
        base=[base] * len(phase_segments),
        theta=[segment.theta_deg for segment in phase_segments],
        width=[segment.width_deg for segment in phase_segments],
        marker=dict(
            color=[segment.fill_color for segment in phase_segments],
            line=dict(color=[segment.border_color for segment in phase_segments], width=1.8),
        ),
        text=[
            (
                f"{segment.planet_symbol} {segment.planet_name}<br>"
                f"{segment.fortune_label}<br>"
                f"{'日' if phase == 'day' else '夜'}時辰 {segment.hour_number}"
            )
            for segment in phase_segments
        ],
        hovertext=[segment.hover_html for segment in phase_segments],
        customdata=[[segment.absolute_index, segment.hour_number, segment.phase] for segment in phase_segments],
        hovertemplate="%{hovertext}<extra></extra>",
        opacity=0.92,
    )


def _build_planetary_hours_figure(segments: list[PlanetaryHourSegment]) -> go.Figure:
    """建立行星時辰日夜輪。"""
    fig = go.Figure()
    fig.add_trace(_hour_ring_trace(segments, "day"))
    fig.add_trace(_hour_ring_trace(segments, "night"))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=False, range=[0, 3.0]),
            angularaxis=dict(showgrid=False, ticks="", direction="clockwise", rotation=90),
        ),
        paper_bgcolor=_NIGHT_BLUE,
        height=640,
        margin=dict(l=12, r=12, t=22, b=12),
        showlegend=False,
    )
    fig.add_shape(
        type="circle",
        xref="paper",
        yref="paper",
        x0=0.22,
        y0=0.22,
        x1=0.78,
        y1=0.78,
        fillcolor=_RING_DAY,
        line=dict(color=_GREEN_DEEP, width=1),
    )
    fig.add_shape(
        type="circle",
        xref="paper",
        yref="paper",
        x0=0.10,
        y0=0.10,
        x1=0.90,
        y1=0.90,
        fillcolor=_RING_NIGHT,
        line=dict(color=_GOLD, width=1),
    )
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        text="☾ Planetary<br>Hours",
        showarrow=False,
        font=dict(size=16, color="#F8E9B8"),
    )
    apply_chart_theme(fig)
    return fig


def render_planetary_hours_wheel(
    daytime_hours: list[dict[str, Any]],
    nighttime_hours: list[dict[str, Any]],
    *,
    current_hour: dict[str, Any] | None = None,
    chart_key: str = "bd_planetary_hours_wheel",
) -> None:
    """渲染行星時辰同心輪（12+12）。"""
    segments = build_planetary_hour_segments(daytime_hours, nighttime_hours, current_hour=current_hour)
    fig = _build_planetary_hours_figure(segments)
    st.plotly_chart(fig, width="stretch", key=chart_key)


__all__ = [
    "render_planetary_hours_wheel",
    "render_twelve_houses_wheel",
]
