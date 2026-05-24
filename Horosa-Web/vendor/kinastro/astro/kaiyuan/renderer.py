# -*- coding: utf-8 -*-
"""
astro/kaiyuan/renderer.py — 開元占經 Streamlit 渲染模組

視覺風格：
  - 仿古宣紙質感（米白底色）
  - 書法字體（Noto Serif SC）
  - 傳統星占排版

主要函式：
    render_streamlit()
"""

from __future__ import annotations

import json
import math
import pathlib
from functools import lru_cache
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import streamlit as st

from astro.i18n import auto_cn
from astro.qizheng.calculator import _get_mansion_info, _normalize_degree
from astro.qizheng.constants import TWELVE_SIGNS_CHINESE, TWENTY_EIGHT_MANSIONS
from astro.swe_init import init_swisseph

# ─────────────────────────────────────────────────────────────────────────────
# 色彩常數
# ─────────────────────────────────────────────────────────────────────────────
_PAPER_BG = "#fdf8f0"
_SEAL_RED = "#8b1a1a"
_INK_DARK = "#1a1a2e"
_SUBTITLE = "#6b5e4e"
_BORDER = "#c4a882"
_GOLD = "#b8860b"

_DATA_DIR = pathlib.Path(__file__).parent


@dataclass(frozen=True)
class KaiyuanObservation:
    """即時星盤中的單一星曜觀測資料。"""

    key: str
    label: str
    short_label: str
    icon: str
    color: str
    longitude: float
    mansion_name: str
    mansion_degree: float
    retrograde: bool = False


_LIVE_BODIES = (
    ("moon", "月", "月", "☽", "#f6d365", 1),
    ("歲星（木）", "歲星（木）", "歲", "♃", "#4caf50", 5),
    ("熒惑（火）", "熒惑（火）", "熒", "♂", "#ef5350", 4),
    ("填星（土）", "填星（土）", "填", "♄", "#c0a36e", 6),
    ("太白（金）", "太白（金）", "太", "♀", "#ffd166", 3),
    ("辰星（水）", "辰星（水）", "辰", "☿", "#4fc3f7", 2),
)

_FOUR_SYMBOL_COLORS = {
    "東方青龍": "#2e8b57",
    "北方玄武": "#355c7d",
    "西方白虎": "#8d6e63",
    "南方朱雀": "#b83b5e",
}

# ─────────────────────────────────────────────────────────────────────────────
# 資料載入
# ─────────────────────────────────────────────────────────────────────────────

def _load_json(filename: str) -> Any:
    path = _DATA_DIR / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_five_planet_data() -> Dict[str, Dict[str, Any]]:
    """載入五星入宿占文，返回 {planet_name: {mansion: text}}"""
    file_map = {
        "歲星（木）": "wood_star.json",
        "熒惑（火）": "fire_star.json",
        "太白（金）": "gold_star.json",
        "填星（土）": "earth_star.json",
        "辰星（水）": "water_star.json",
    }
    result: Dict[str, Dict[str, Any]] = {}
    for label, fname in file_map.items():
        raw = _load_json(fname)
        # Each file has one top-level key (the planet canonical name)
        if isinstance(raw, dict):
            top_val = next(iter(raw.values())) if raw else {}
            result[label] = top_val if isinstance(top_val, dict) else {}
    return result


@lru_cache(maxsize=1)
def _load_moon_28_mansion() -> Dict[str, Any]:
    raw = _load_json("moon_28_mansion.json")
    if isinstance(raw, dict):
        return next(iter(raw.values())) if raw else {}
    return {}


def _load_moon_five_stars() -> Dict[str, Any]:
    raw = _load_json("moon_in_five_stars.json")
    if isinstance(raw, dict):
        return next(iter(raw.values())) if raw else {}
    return {}


def _load_moon_attack_28() -> Dict[str, Any]:
    raw = _load_json("kaiyuan_moon_attack.json")
    if isinstance(raw, dict):
        return next(iter(raw.values())) if raw else {}
    return {}


def _load_sun_eclipse_month() -> Dict[str, Any]:
    raw = _load_json("kaiyuan_sun_elipse_month.json")
    if isinstance(raw, dict):
        return next(iter(raw.values())) if raw else {}
    return {}


def _load_sun_eclipse_gz() -> Dict[str, Any]:
    raw = _load_json("kaiyuan_sun_elipse_gz.json")
    if isinstance(raw, dict):
        return next(iter(raw.values())) if raw else {}
    return {}


def _load_five_star_general() -> Dict[str, Any]:
    raw = _load_json("kaiyuan_five_star_rep.json")
    if isinstance(raw, dict):
        return next(iter(raw.values())) if raw else {}
    return {}


def _load_five_sounds() -> Dict[str, Any]:
    return _load_json("five_sounds.json")


def _load_jiazi_five_sounds() -> Dict[str, Any]:
    return _load_json("jiazi_five_sounds.json")


# ─────────────────────────────────────────────────────────────────────────────
# 即時星盤輔助
# ─────────────────────────────────────────────────────────────────────────────

def _resolve_calc_params() -> Dict[str, Any]:
    """從 session state 取得可用的排盤參數。"""
    params = st.session_state.get("_calc_params") or st.session_state.get("_confirmed_params") or {}
    return {
        "year": int(params.get("year", 0) or 0),
        "month": int(params.get("month", 0) or 0),
        "day": int(params.get("day", 0) or 0),
        "hour": int(params.get("hour", 0) or 0),
        "minute": int(params.get("minute", 0) or 0),
        "timezone": float(params.get("timezone", params.get("tz", 8.0)) or 0.0),
        "latitude": float(params.get("latitude", params.get("lat", 22.3193)) or 0.0),
        "longitude": float(params.get("longitude", params.get("lon", 114.1694)) or 0.0),
        "location_name": str(params.get("location_name", "") or ""),
    }


def _has_live_chart_params(params: Dict[str, Any]) -> bool:
    return all(params.get(k) for k in ("year", "month", "day"))


def _compute_live_observations(params: Dict[str, Any]) -> List[KaiyuanObservation]:
    """依據當前輸入資料計算月亮與五星所在宿度。"""
    if not _has_live_chart_params(params):
        return []

    swe = init_swisseph()
    decimal_hour = params["hour"] + params["minute"] / 60.0 - params["timezone"]
    jd = swe.julday(
        params["year"],
        params["month"],
        params["day"],
        decimal_hour,
    )

    observations: List[KaiyuanObservation] = []
    for key, label, short_label, icon, color, body_id in _LIVE_BODIES:
        result, _ = swe.calc_ut(jd, body_id)
        lon = _normalize_degree(result[0])
        speed = result[3] if len(result) > 3 else 0.0
        mansion_name, mansion_degree, _, _ = _get_mansion_info(lon)
        observations.append(
            KaiyuanObservation(
                key=key,
                label=label,
                short_label=short_label,
                icon=icon,
                color=color,
                longitude=lon,
                mansion_name=mansion_name,
                mansion_degree=mansion_degree,
                retrograde=speed < 0,
            )
        )
    return observations


def _build_mansion_ranges() -> List[Dict[str, Any]]:
    ranges: List[Dict[str, Any]] = []
    total = len(TWENTY_EIGHT_MANSIONS)
    for idx, mansion in enumerate(TWENTY_EIGHT_MANSIONS):
        start = float(mansion["start_lon"])
        end = float(TWENTY_EIGHT_MANSIONS[(idx + 1) % total]["start_lon"])
        width = (end - start) % 360.0
        start_angle = _ecl_to_chart_angle(end)
        ranges.append(
            {
                "name": mansion["name"],
                "group": mansion["group"],
                "start": start_angle,
                "end": start_angle + width,
                "mid": start_angle + width / 2.0,
            }
        )
    return ranges


def _build_twelve_palace_ranges() -> List[Dict[str, Any]]:
    ranges: List[Dict[str, Any]] = []
    for idx, palace in enumerate(TWELVE_SIGNS_CHINESE):
        start_lon = idx * 30.0
        end_lon = (idx + 1) * 30.0
        start = _ecl_to_chart_angle(end_lon)
        end = _ecl_to_chart_angle(start_lon)
        if end <= start:
            end += 360.0
        short_name, station_name = _split_palace_label(palace)
        ranges.append(
            {
                "name": short_name,
                "station": station_name,
                "start": start,
                "end": end,
                "mid": (start + end) / 2.0,
            }
        )
    return ranges


def _split_palace_label(label: str) -> tuple[str, str]:
    short_name, separator, station_name = label.partition("(")
    if not separator:
        return label, ""
    return short_name, station_name.rstrip(")")


def _ecl_to_chart_angle(ecl_deg: float) -> float:
    return (45.0 - float(ecl_deg)) % 360.0


def _polar_to_cartesian(cx: float, cy: float, radius: float, angle_deg: float) -> tuple[float, float]:
    angle_rad = math.radians(angle_deg - 90.0)
    return cx + radius * math.cos(angle_rad), cy + radius * math.sin(angle_rad)


def _ring_arc_path(
    cx: float,
    cy: float,
    inner_radius: float,
    outer_radius: float,
    start_angle: float,
    end_angle: float,
) -> str:
    start_outer = _polar_to_cartesian(cx, cy, outer_radius, start_angle)
    end_outer = _polar_to_cartesian(cx, cy, outer_radius, end_angle)
    end_inner = _polar_to_cartesian(cx, cy, inner_radius, end_angle)
    start_inner = _polar_to_cartesian(cx, cy, inner_radius, start_angle)
    large_arc = 1 if ((end_angle - start_angle) % 360.0) > 180.0 else 0
    return (
        f"M {start_outer[0]:.2f} {start_outer[1]:.2f} "
        f"A {outer_radius:.2f} {outer_radius:.2f} 0 {large_arc} 1 {end_outer[0]:.2f} {end_outer[1]:.2f} "
        f"L {end_inner[0]:.2f} {end_inner[1]:.2f} "
        f"A {inner_radius:.2f} {inner_radius:.2f} 0 {large_arc} 0 {start_inner[0]:.2f} {start_inner[1]:.2f} Z"
    )


def _build_astrolabe_svg(
    observations: List[KaiyuanObservation],
    params: Dict[str, Any],
    width: int = 760,
) -> str:
    """生成開元星盤 SVG。"""
    size = width
    center = size / 2.0
    outer_radius = size * 0.42
    mansion_inner_radius = size * 0.30
    palace_outer_radius = mansion_inner_radius - 10.0
    palace_inner_radius = palace_outer_radius - size * 0.08
    inner_radius = palace_inner_radius - 14.0
    marker_base_radius = size * 0.33
    mansion_ranges = _build_mansion_ranges()
    palace_ranges = _build_twelve_palace_ranges()
    location_name = params.get("location_name") or auto_cn("未命名地點", "Unknown location")
    date_line = (
        f"{params['year']:04d}-{params['month']:02d}-{params['day']:02d} "
        f"{params['hour']:02d}:{params['minute']:02d} UTC{params['timezone']:+.1f}"
    )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        "<defs>",
        '<radialGradient id="kaiyuanBg" cx="50%" cy="45%" r="65%">',
        f'<stop offset="0%" stop-color="{_PAPER_BG}"/>',
        '<stop offset="70%" stop-color="#f3ead7"/>',
        '<stop offset="100%" stop-color="#e7d5b4"/>',
        "</radialGradient>",
        '<filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">',
        '<feDropShadow dx="0" dy="12" stdDeviation="12" flood-color="#5b4630" flood-opacity="0.18"/>',
        "</filter>",
        "</defs>",
        f'<rect x="0" y="0" width="{size}" height="{size}" rx="28" fill="url(#kaiyuanBg)"/>',
        f'<circle cx="{center:.2f}" cy="{center:.2f}" r="{outer_radius + 18:.2f}" fill="none" stroke="{_BORDER}" stroke-width="2" opacity="0.8"/>',
    ]

    for mansion in mansion_ranges:
        fill = _FOUR_SYMBOL_COLORS.get(mansion["group"], "#7a6a58")
        path = _ring_arc_path(
            center,
            center,
            mansion_inner_radius,
            outer_radius,
            mansion["start"],
            mansion["end"],
        )
        lx, ly = _polar_to_cartesian(center, center, (mansion_inner_radius + outer_radius) / 2.0, mansion["mid"])
        parts.append(
            f'<path d="{path}" fill="{fill}" fill-opacity="0.14" stroke="#f8f1e3" stroke-width="1.3"/>'
        )
        parts.append(
            f'<text x="{lx:.2f}" y="{ly:.2f}" fill="{_INK_DARK}" font-size="{size * 0.022:.1f}" '
            'font-family="Noto Serif SC, serif" text-anchor="middle" dominant-baseline="middle">'
            f'{mansion["name"]}</text>'
        )

    for palace in palace_ranges:
        path = _ring_arc_path(
            center,
            center,
            palace_inner_radius,
            palace_outer_radius,
            palace["start"],
            palace["end"],
        )
        title_x, title_y = _polar_to_cartesian(
            center,
            center,
            (palace_inner_radius + palace_outer_radius) / 2.0 + 7.0,
            palace["mid"],
        )
        subtitle_x, subtitle_y = _polar_to_cartesian(
            center,
            center,
            (palace_inner_radius + palace_outer_radius) / 2.0 - 8.0,
            palace["mid"],
        )
        parts.append(
            f'<path d="{path}" fill="#fff8e8" fill-opacity="0.92" stroke="{_BORDER}" stroke-width="1.1"/>'
        )
        parts.append(
            f'<text x="{title_x:.2f}" y="{title_y:.2f}" fill="{_SEAL_RED}" font-size="{size * 0.017:.1f}" '
            'font-family="Noto Serif SC, serif" text-anchor="middle" dominant-baseline="middle">'
            f'{palace["name"]}</text>'
        )
        parts.append(
            f'<text x="{subtitle_x:.2f}" y="{subtitle_y:.2f}" fill="{_SUBTITLE}" font-size="{size * 0.014:.1f}" '
            'font-family="Noto Serif SC, serif" text-anchor="middle" dominant-baseline="middle">'
            f'{palace["station"]}</text>'
        )

    parts.extend(
        [
            f'<circle cx="{center:.2f}" cy="{center:.2f}" r="{inner_radius - 18:.2f}" fill="#fffaf0" stroke="{_BORDER}" stroke-width="1.5" filter="url(#softShadow)"/>',
            f'<text x="{center:.2f}" y="{center - 24:.2f}" fill="{_SEAL_RED}" font-size="{size * 0.04:.1f}" font-family="Noto Serif SC, serif" text-anchor="middle">開元星盤</text>',
            f'<text x="{center:.2f}" y="{center + 6:.2f}" fill="{_SUBTITLE}" font-size="{size * 0.019:.1f}" font-family="Noto Serif SC, serif" text-anchor="middle">{location_name}</text>',
            f'<text x="{center:.2f}" y="{center + 34:.2f}" fill="{_SUBTITLE}" font-size="{size * 0.015:.1f}" font-family="Noto Serif SC, serif" text-anchor="middle">{date_line}</text>',
        ]
    )

    for idx, obs in enumerate(observations):
        obs_angle = _ecl_to_chart_angle(obs.longitude)
        radius = marker_base_radius + (idx % 2) * 18.0
        x, y = _polar_to_cartesian(center, center, radius, obs_angle)
        lx, ly = _polar_to_cartesian(center, center, outer_radius + 26.0 + (idx % 2) * 10.0, obs_angle)
        anchor = "start" if math.cos(math.radians(obs_angle - 90.0)) >= 0 else "end"
        parts.append(
            f'<line x1="{center:.2f}" y1="{center:.2f}" x2="{x:.2f}" y2="{y:.2f}" '
            f'stroke="{obs.color}" stroke-width="2.2" stroke-opacity="0.65"/>'
        )
        parts.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="10" fill="{obs.color}" stroke="#fffaf0" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="{x:.2f}" y="{y + 0.5:.2f}" fill="#1f1a17" font-size="{size * 0.017:.1f}" '
            'font-family="Noto Serif SC, serif" text-anchor="middle" dominant-baseline="middle">'
            f"{obs.short_label}</text>"
        )
        parts.append(
            f'<text x="{lx:.2f}" y="{ly:.2f}" fill="{_INK_DARK}" font-size="{size * 0.016:.1f}" '
            f'font-family="Noto Serif SC, serif" text-anchor="{anchor}" dominant-baseline="middle">'
            f"{obs.icon} {obs.label}・{obs.mansion_name}</text>"
        )

    parts.append("</svg>")
    return "".join(parts)


def _inject_kaiyuan_theme() -> None:
    st.markdown(
        f"""
        <style>
        .kaiyuan-hero {{
            background: linear-gradient(135deg, rgba(139,26,26,0.95), rgba(88,55,33,0.92));
            border: 1px solid rgba(196,168,130,0.45);
            border-radius: 22px;
            padding: 1.25rem 1.35rem;
            color: #fff7ea;
            box-shadow: 0 20px 48px rgba(69, 45, 22, 0.18);
            margin-bottom: 1rem;
        }}
        .kaiyuan-hero h2 {{
            margin: 0 0 0.35rem 0;
            font-family: "Noto Serif SC", serif;
            letter-spacing: 0.18em;
            color: #fff4df;
        }}
        .kaiyuan-hero p {{
            margin: 0;
            color: rgba(255, 247, 234, 0.86);
            line-height: 1.65;
        }}
        .kaiyuan-card {{
            background: linear-gradient(180deg, rgba(253,248,240,0.98), rgba(245,235,218,0.95));
            border: 1px solid rgba(196,168,130,0.55);
            border-radius: 18px;
            padding: 0.95rem 1rem;
            min-height: 128px;
            box-shadow: 0 12px 32px rgba(88,55,33,0.08);
        }}
        .kaiyuan-card .eyebrow {{
            color: {_SEAL_RED};
            font-size: 0.78rem;
            letter-spacing: 0.12em;
            margin-bottom: 0.35rem;
        }}
        .kaiyuan-card .headline {{
            color: {_INK_DARK};
            font-size: 1.02rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }}
        .kaiyuan-card .meta {{
            color: {_SUBTITLE};
            font-size: 0.88rem;
            line-height: 1.55;
        }}
        .kaiyuan-chart-shell {{
            background: radial-gradient(circle at top, rgba(255,250,240,0.95), rgba(243,234,215,0.94));
            border: 1px solid rgba(196,168,130,0.55);
            border-radius: 24px;
            padding: 1rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.55), 0 16px 38px rgba(88,55,33,0.08);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _collect_live_omens(
    observations: List[KaiyuanObservation],
    five_planet_data: Dict[str, Dict[str, Any]],
    moon_28_data: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """收集即時星盤可直接對照的入宿占文。"""
    rows: List[Dict[str, Any]] = []
    for obs in observations:
        # moon_28_data is {宿名: 占文}; five_planet_data is {星曜: {宿名: 占文文本}}
        if obs.key == "moon":
            omen = moon_28_data.get(obs.mansion_name)
        else:
            omen = five_planet_data.get(obs.label, {}).get(obs.mansion_name)
        if not omen:
            continue
        rows.append(
            {
                "label": obs.label,
                "mansion": obs.mansion_name,
                "is_moon": obs.key == "moon",
                "omen": omen,
            }
        )
    return rows


def _render_live_chart_overview() -> Dict[str, KaiyuanObservation]:
    """渲染開元星盤總覽，並回傳即時定位結果供子頁使用。"""
    params = _resolve_calc_params()
    _section_header(auto_cn("✨ 開元星盤總覽", "✨ Kaiyuan Astrolabe"))
    st.caption(
        auto_cn(
            "依目前輸入的時間與地點，自動定位月亮與五星所在宿度，讓查詢占文不再只是資料庫，而是真正的觀測入口。",
            "Uses the current chart inputs to place the Moon and five planets into the 28 mansions for a more visual lookup experience.",
        )
    )

    if not _has_live_chart_params(params):
        st.info(
            auto_cn(
                "先在左側輸入日期、時間與地點後再返回此頁，即可看到即時開元星盤與對應宿度。",
                "Enter date, time, and location on the left to generate the live Kaiyuan astrolabe.",
            )
        )
        return {}

    observations = _compute_live_observations(params)
    if not observations:
        st.warning(auto_cn("暫時無法計算星盤。", "Unable to compute the live chart right now."))
        return {}

    st.markdown(
        (
            '<div class="kaiyuan-chart-shell">'
            f'<div style="display:flex;justify-content:center;">{_build_astrolabe_svg(observations, params)}</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    summary_cols = st.columns(3)
    for idx, obs in enumerate(observations):
        with summary_cols[idx % 3]:
            st.markdown(
                f"""
                <div class="kaiyuan-card">
                    <div class="eyebrow">{obs.icon} {obs.label}</div>
                    <div class="headline">{obs.mansion_name}宿 · {obs.mansion_degree:.1f}°</div>
                    <div class="meta">
                        黃經 {obs.longitude:.1f}° {'℞' if obs.retrograde else ''}<br>
                        {auto_cn('可直接對照本頁對應占文分頁', 'Use this to jump into the matching omen sections')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    live_omens = _collect_live_omens(
        observations=observations,
        five_planet_data=_load_five_planet_data(),
        moon_28_data=_load_moon_28_mansion(),
    )
    if live_omens:
        st.markdown("#### " + auto_cn("📜 即時入宿占文", "📜 Live Mansion Omens"))
        st.caption(
            auto_cn(
                "依當前月亮與五星位置，自動讀取《開元占經》對應條文。",
                "Automatically loaded from Kaiyuan JSON entries based on current Moon and five-planet mansion placements.",
            )
        )
        for row in live_omens:
            with st.expander(
                auto_cn(f"{row['label']} 入 {row['mansion']} 宿", f"{row['label']} in {row['mansion']} mansion"),
                expanded=row["is_moon"],
            ):
                if isinstance(row["omen"], dict):
                    _render_dict_omens(row["omen"])
                else:
                    st.markdown(str(row["omen"]))

    return {obs.key: obs for obs in observations}


# ─────────────────────────────────────────────────────────────────────────────
# 通用渲染輔助
# ─────────────────────────────────────────────────────────────────────────────

def _section_header(title: str) -> None:
    st.markdown(
        f"<h3 style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;"
        f"letter-spacing:3px;border-bottom:2px solid {_BORDER};padding-bottom:6px;'>"
        f"{title}</h3>",
        unsafe_allow_html=True,
    )


def _omen_card(source: str, text: Any) -> None:
    """渲染一條占文卡片（source = 典籍名稱, text = 占文內容）"""
    if isinstance(text, list):
        text_html = "".join(
            f"<p style='margin:4px 0;'>{t_}</p>" for t_ in text
        )
    elif isinstance(text, dict):
        text_html = "".join(
            f"<p style='margin:4px 0;'><b>{k}：</b>{v}</p>"
            for k, v in text.items()
        )
    else:
        text_html = f"<p style='margin:4px 0;'>{text}</p>"

    st.markdown(
        f"<div style='background:{_PAPER_BG};border-left:3px solid {_SEAL_RED};"
        f"padding:10px 14px;border-radius:4px;margin-bottom:8px;'>"
        f"<b style='color:{_GOLD};font-family:Noto Serif SC,serif;font-size:14px;'>"
        f"【{source}】</b>"
        f"<div style='font-family:Noto Serif SC,serif;font-size:14px;color:{_INK_DARK};"
        f"margin-top:4px;'>{text_html}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _render_dict_omens(data: Dict[str, Any]) -> None:
    """遞歸渲染占文字典（跳過空值）"""
    if not data:
        st.info(auto_cn("暫無資料"))
        return
    for source, text in data.items():
        if source == "歷史應驗":
            with st.expander(auto_cn("📜 歷史應驗")):
                if isinstance(text, list):
                    for item in text:
                        st.markdown(f"• {item}")
                else:
                    st.markdown(str(text))
        else:
            _omen_card(source, text)


# ─────────────────────────────────────────────────────────────────────────────
# 子頁面渲染
# ─────────────────────────────────────────────────────────────────────────────

def _render_five_planets_tab(live_obs: Optional[Dict[str, KaiyuanObservation]] = None) -> None:
    """五星入宿占文查詢"""
    _section_header("🪐 五星入二十八宿占")
    st.caption(auto_cn("選擇行星與宿名，查閱《開元占經》原文占辭"))

    planet_data = _load_five_planet_data()
    planet_names = list(planet_data.keys())
    live_obs = live_obs or {}
    default_planet = next(
        (obs.label for obs in live_obs.values() if obs.label in planet_names and obs.key != "moon"),
        planet_names[0] if planet_names else "",
    )
    default_planet_index = planet_names.index(default_planet) if default_planet in planet_names else 0

    col1, col2 = st.columns(2)
    with col1:
        selected_planet = st.selectbox(
            auto_cn("行星"),
            planet_names,
            index=default_planet_index,
            key="kaiyuan_planet_select",
        )
    with col2:
        mansions = list(planet_data.get(selected_planet, {}).keys())
        live_mansion = next(
            (obs.mansion_name for obs in live_obs.values() if obs.label == selected_planet),
            mansions[0] if mansions else "（無資料）",
        )
        default_mansion_index = mansions.index(live_mansion) if live_mansion in mansions else 0
        selected_mansion = st.selectbox(
            auto_cn("宿名"),
            mansions if mansions else ["（無資料）"],
            index=default_mansion_index,
            key="kaiyuan_mansion_select",
        )

    if st.button(auto_cn("查詢占文"), key="kaiyuan_planet_btn"):
        omen = planet_data.get(selected_planet, {}).get(selected_mansion)
        if omen:
            st.markdown(
                f"<h4 style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;'>"
                f"{selected_planet} 入 {selected_mansion} 宿</h4>",
                unsafe_allow_html=True,
            )
            if isinstance(omen, dict):
                _render_dict_omens(omen)
            else:
                st.markdown(
                    f"<div style='background:{_PAPER_BG};padding:12px;border-radius:4px;"
                    f"font-family:Noto Serif SC,serif;font-size:15px;color:{_INK_DARK};'>"
                    f"{omen}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.warning(auto_cn("暫無此條目資料"))


def _render_moon_28_tab(live_obs: Optional[Dict[str, KaiyuanObservation]] = None) -> None:
    """月犯二十八宿占（簡表）"""
    _section_header("🌙 月犯二十八宿占")
    st.caption(auto_cn("月亮經過二十八宿時的傳統占驗"))

    data = _load_moon_28_mansion()
    mansions = list(data.keys())
    if not mansions:
        st.info(auto_cn("暫無資料"))
        return

    live_mansion = (live_obs or {}).get("moon")
    default_index = mansions.index(live_mansion.mansion_name) if live_mansion and live_mansion.mansion_name in mansions else 0
    selected = st.selectbox(
        auto_cn("宿名"),
        mansions,
        index=default_index,
        key="kaiyuan_moon28_select",
    )
    if st.button(auto_cn("查詢"), key="kaiyuan_moon28_btn"):
        omen = data.get(selected)
        if omen:
            st.markdown(
                f"<h4 style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;'>"
                f"月犯 {selected} 宿</h4>",
                unsafe_allow_html=True,
            )
            if isinstance(omen, dict):
                _render_dict_omens(omen)
            else:
                st.markdown(str(omen))
        else:
            st.warning(auto_cn("暫無此條目資料"))


def _render_moon_attack_tab() -> None:
    """月犯二十八宿詳細占（kaiyuan_moon_attack）"""
    _section_header("🌙 月犯二十八宿詳占")
    st.caption(auto_cn("《開元占經》月犯二十八宿詳細占辭，含四方分組"))

    data = _load_moon_attack_28()
    if not data:
        st.info(auto_cn("暫無資料"))
        return

    # data is {region: {mansion: {source: text}}}
    for region, mansions in data.items():
        with st.expander(auto_cn(f"📌 {region}"), expanded=False):
            if not isinstance(mansions, dict):
                continue
            mansion_list = list(mansions.keys())
            sel = st.selectbox(
                auto_cn("宿名"),
                mansion_list,
                key=f"kaiyuan_attack_{region}",
            )
            omen = mansions.get(sel, {})
            if isinstance(omen, dict):
                _render_dict_omens(omen)
            else:
                st.markdown(str(omen))


def _render_moon_five_stars_tab() -> None:
    """月犯五星占"""
    _section_header("🌙 月犯五星占")
    st.caption(auto_cn("月亮與五大行星相犯的傳統占驗"))

    data = _load_moon_five_stars()
    if not data:
        st.info(auto_cn("暫無資料"))
        return

    # Show general section first
    if "總論" in data:
        with st.expander(auto_cn("📖 總論"), expanded=True):
            _render_dict_omens(data["總論"])

    planets = [k for k in data.keys() if k != "總論"]
    planet_map = {
        "歲星": "歲星（木）", "熒惑": "熒惑（火）", "太白": "太白（金）",
        "填星": "填星（土）", "辰星": "辰星（水）",
    }
    for p in planets:
        label = planet_map.get(p, p)
        with st.expander(auto_cn(f"🪐 月犯 {label}"), expanded=False):
            omen = data[p]
            if isinstance(omen, dict):
                _render_dict_omens(omen)
            else:
                st.markdown(str(omen))


def _render_sun_eclipse_tab() -> None:
    """日食占"""
    _section_header("☀️ 日食占")
    st.caption(auto_cn("《開元占經》日食逐月及干支占辭"))

    sub_tab1, sub_tab2 = st.tabs([
        auto_cn("按月份"),
        auto_cn("按干支"),
    ])

    with sub_tab1:
        month_data = _load_sun_eclipse_month()
        months = list(month_data.keys())
        if months:
            sel_month = st.selectbox(auto_cn("月份"), months, key="kaiyuan_sun_month_sel")
            if st.button(auto_cn("查詢"), key="kaiyuan_sun_month_btn"):
                omen = month_data.get(sel_month, {})
                st.markdown(
                    f"<h4 style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;'>"
                    f"{sel_month} 日食</h4>",
                    unsafe_allow_html=True,
                )
                if isinstance(omen, dict):
                    _render_dict_omens(omen)
                else:
                    st.markdown(str(omen))
        else:
            st.info(auto_cn("暫無資料"))

    with sub_tab2:
        gz_data = _load_sun_eclipse_gz()
        # First entry may be general notes
        gz_keys = list(gz_data.keys())
        _GZ_GENERAL_KEY = "甘氏总论"
        general_key = _GZ_GENERAL_KEY if _GZ_GENERAL_KEY in gz_data else None
        if general_key:
            with st.expander(auto_cn("📖 甘氏總論"), expanded=False):
                _render_dict_omens(gz_data[general_key])
            gz_keys = [k for k in gz_keys if k != general_key]

        if gz_keys:
            sel_gz = st.selectbox(auto_cn("干支"), gz_keys, key="kaiyuan_sun_gz_sel")
            if st.button(auto_cn("查詢"), key="kaiyuan_sun_gz_btn"):
                omen = gz_data.get(sel_gz, {})
                st.markdown(
                    f"<h4 style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;'>"
                    f"{sel_gz} 日食</h4>",
                    unsafe_allow_html=True,
                )
                if isinstance(omen, dict):
                    _render_dict_omens(omen)
                else:
                    st.markdown(str(omen))
        else:
            st.info(auto_cn("暫無資料"))


def _render_five_sounds_tab() -> None:
    """五音法"""
    _section_header("🎵 五音法")
    st.caption(auto_cn("《開元占經》五音占風法與六十甲子納音"))

    sub1, sub2 = st.tabs([auto_cn("地十二辰五音法"), auto_cn("六十甲子五音")])

    with sub1:
        sounds_data = _load_five_sounds()
        # sections: 地十二辰五音法 / 李先生註 / 五音相動風占
        for section_name, section_data in sounds_data.items():
            with st.expander(auto_cn(f"📌 {section_name}"), expanded=(section_name == "地十二辰五音法")):
                if isinstance(section_data, dict):
                    for key, val in section_data.items():
                        if isinstance(val, dict):
                            st.markdown(
                                f"<b style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;'>{key}</b>",
                                unsafe_allow_html=True,
                            )
                            cols = st.columns(3)
                            for i, (attr, v) in enumerate(val.items()):
                                with cols[i % 3]:
                                    if isinstance(v, list):
                                        st.markdown(f"**{attr}**：{'、'.join(str(x) for x in v)}")
                                    else:
                                        st.markdown(f"**{attr}**：{v}")
                        else:
                            st.markdown(f"**{key}**：{val}")
                else:
                    st.markdown(str(section_data))

    with sub2:
        jiazi_data = _load_jiazi_five_sounds()
        # 納音 and 總則
        nayin = jiazi_data.get("納音", {})
        zongze = jiazi_data.get("總則", {})

        if nayin:
            st.markdown(auto_cn("### 六十甲子納音分類"))
            for sound_type, gz_list in nayin.items():
                st.markdown(
                    f"<span style='color:{_SEAL_RED};font-family:Noto Serif SC,serif;"
                    f"font-weight:bold;'>{sound_type}</span>：{'　'.join(gz_list) if isinstance(gz_list, list) else gz_list}",
                    unsafe_allow_html=True,
                )
            st.markdown("---")

        if zongze:
            st.markdown(auto_cn("### 總則"))
            if isinstance(zongze, dict):
                for title, content in zongze.items():
                    with st.expander(auto_cn(f"📖 {title}"), expanded=False):
                        if isinstance(content, dict):
                            for src, text in content.items():
                                _omen_card(src, text)
                        else:
                            st.markdown(str(content))
            else:
                st.markdown(str(zongze))


def _render_five_star_general_tab() -> None:
    """五星總論"""
    _section_header("🌌 五星總論")
    st.caption(auto_cn("《開元占經》五星總論，集各家占辭"))

    data = _load_five_star_general()
    if not data:
        st.info(auto_cn("暫無資料"))
        return

    for section, content in data.items():
        with st.expander(auto_cn(f"📌 {section}"), expanded=False):
            if isinstance(content, dict):
                for src, text in content.items():
                    if isinstance(text, dict):
                        st.markdown(
                            f"<b style='color:{_GOLD};font-family:Noto Serif SC,serif;'>"
                            f"【{src}】</b>",
                            unsafe_allow_html=True,
                        )
                        for sub_src, sub_text in text.items():
                            _omen_card(sub_src, sub_text)
                    else:
                        _omen_card(src, text)
            else:
                st.markdown(str(content))


# ─────────────────────────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────────────────────────

def render_streamlit() -> None:
    """開元占經 Streamlit 主渲染函式（不需出生資料，為查詢工具）"""
    _inject_kaiyuan_theme()
    hero_title = auto_cn("開元占經", "Kaiyuan Zhanjing")
    hero_description = auto_cn(
        "唐·瞿曇悉達奉詔編纂的星占巨典，現以更精緻的 Streamlit 介面整合即時星盤、宿度定位與原典占文。",
        "A refined Streamlit reading room for Kaiyuan Zhanjing, combining a live astrolabe, mansion tracking, and classical omen texts.",
    )
    st.markdown(
        f"""
        <div class="kaiyuan-hero">
            <h2>📜 {hero_title}</h2>
            <p>{hero_description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(auto_cn("唐·瞿曇悉達 撰 · 五星入宿 · 月占 · 日食占 · 五音法"))
    st.markdown("---")
    live_obs = _render_live_chart_overview()
    st.markdown("---")

    tabs = st.tabs([
        auto_cn("🪐 五星入宿"),
        auto_cn("🌙 月犯五星"),
        auto_cn("🌙 月犯廿八宿"),
        auto_cn("🌙 月犯廿八宿詳"),
        auto_cn("☀️ 日食占"),
        auto_cn("🎵 五音法"),
        auto_cn("🌌 五星總論"),
    ])

    with tabs[0]:
        _render_five_planets_tab(live_obs)
    with tabs[1]:
        _render_moon_five_stars_tab()
    with tabs[2]:
        _render_moon_28_tab(live_obs)
    with tabs[3]:
        _render_moon_attack_tab()
    with tabs[4]:
        _render_sun_eclipse_tab()
    with tabs[5]:
        _render_five_sounds_tab()
    with tabs[6]:
        _render_five_star_general_tab()
