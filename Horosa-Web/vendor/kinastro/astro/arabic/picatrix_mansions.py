"""
Picatrix 星體魔法模組 (Picatrix Stellar Magic Module)
資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
Greer & Warnock 2011 translation / Attrell & Porreca 2019

功能：
- 28 阿拉伯月宿（Manazil al-Qamar）計算與查詢
- 行星時（Planetary Hours）計算（含日出日落調整）
- 護符推薦（Talisman Recommendation）

程式碼風格與 arabic.py、decans.py 一致。
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from datetime import timezone as timezone_module

import swisseph as swe
import streamlit as st
import plotly.graph_objects as go

from .picatrix_data import (
    PICATRIX_MANSIONS,
    CHALDEAN_ORDER,
    PLANET_GLYPHS,
    PLANET_NAMES_CN,
    DAY_PLANETS,
    DAY_NAMES_EN,
    DAY_NAMES_CN,
    TALISMAN_INTENTS,
    PICATRIX_TALISMANS,
    PICATRIX_CORRESPONDENCES,
)
from .talisman_generator import generate_talisman_recipe


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class PicatrixMansion:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    A Picatrix lunar mansion with all classical attributes.
    Enriched with Greer & Warnock 2011 detailed notes.
    """
    index: int
    arabic_name: str
    arabic_script: str
    english_name: str
    chinese_name: str
    ruling_planet: str
    fortunate: bool
    magic_image: str
    magic_image_cn: str
    purposes: list
    purposes_cn: list
    incense: str
    color: str
    metal: str
    invocation_summary: str
    start_degree: float
    end_degree: float = field(default=0.0)
    good_uses: list = field(default_factory=list)
    bad_uses: list = field(default_factory=list)
    greer_notes: str = ""


@dataclass
class PlanetaryHour:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book III, Ch. 9
    A single planetary hour entry.
    """
    hour_number: int        # 1-24 (1-12 day hours, 13-24 night hours)
    is_day: bool
    planet: str
    planet_glyph: str
    planet_cn: str
    start_time: datetime
    end_time: datetime
    duration_minutes: float


@dataclass
class PlanetaryHoursResult:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    Result of planetary hours calculation for a given day and location.
    """
    date_str: str
    weekday_en: str
    weekday_cn: str
    day_planet: str
    latitude: float
    longitude: float
    timezone: float
    sunrise: datetime
    sunset: datetime
    day_length_minutes: float
    night_length_minutes: float
    hours: list  # list[PlanetaryHour]


@dataclass
class TalismanRecommendation:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book II, Ch. 10-12
    A Picatrix talisman recommendation based on user intent.
    """
    intent_key: str
    intent_cn: str
    intent_en: str
    planet: str
    planet_glyph: str
    planet_cn: str
    mansion_indices: list
    mansion_names_cn: list
    metal: str
    incense: str
    color: str
    hour_planet: str
    description_cn: str
    description_en: str


# ============================================================
# 月亮黃經計算 (Moon Longitude Computation)
# ============================================================

def compute_moon_longitude(
    year: int, month: int, day: int,
    hour: int, minute: int, timezone: float,
) -> float:
    """
    計算指定出生時間的月亮黃道經度。

    Args:
        year, month, day: 出生日期
        hour, minute: 出生時間（當地時間）
        timezone: 時區偏移（UTC+N）

    Returns:
        float: 月亮黃經度數（0–360°）
    """
    swe.set_ephe_path("")
    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)
    result, _ = swe.calc_ut(jd, swe.MOON)
    return float(result[0]) % 360.0


# ============================================================
# 月宿計算函數 (Mansion Calculation Functions)
# ============================================================

def get_mansion_index(moon_lon: float) -> int:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    根據月亮黃經度數回傳 Picatrix 月宿索引（0-27）。

    每宿跨距 360/28 ≈ 12.857°，從 0° 牡羊座起算。

    Args:
        moon_lon: 月亮黃經度數（0-360）

    Returns:
        int: 月宿索引 0-27
    """
    lon = moon_lon % 360.0
    mansion_width = 360.0 / 28
    idx = int(lon / mansion_width)
    return min(idx, 27)


def get_mansion(moon_lon: float) -> PicatrixMansion:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    根據月亮黃經度數回傳 Picatrix 月宿物件。

    Args:
        moon_lon: 月亮黃經度數（0-360）

    Returns:
        PicatrixMansion: 對應的月宿資料
    """
    idx = get_mansion_index(moon_lon)
    return _build_mansion(PICATRIX_MANSIONS[idx])


def get_mansion_by_index(index: int) -> PicatrixMansion:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    根據索引（0-27）回傳 Picatrix 月宿物件。

    Args:
        index: 月宿索引 0-27

    Returns:
        PicatrixMansion: 對應的月宿資料

    Raises:
        IndexError: if index is out of range 0-27
    """
    if not (0 <= index <= 27):
        raise IndexError(f"Mansion index must be 0-27, got {index}")
    return _build_mansion(PICATRIX_MANSIONS[index])


def get_all_mansions() -> list:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    回傳全部 28 個月宿物件列表。

    Returns:
        list[PicatrixMansion]
    """
    return [_build_mansion(d) for d in PICATRIX_MANSIONS]


def _build_mansion(d: dict) -> PicatrixMansion:
    """Build a PicatrixMansion dataclass from a raw dict (with enriched Greer fields)."""
    mansion_width = 360.0 / 28
    idx = d["index"]
    default_end = (idx + 1) * mansion_width
    return PicatrixMansion(
        index=idx,
        arabic_name=d["arabic_name"],
        arabic_script=d["arabic_script"],
        english_name=d["english_name"],
        chinese_name=d["chinese_name"],
        ruling_planet=d["ruling_planet"],
        fortunate=d["fortunate"],
        magic_image=d["magic_image"],
        magic_image_cn=d["magic_image_cn"],
        purposes=d["purposes"],
        purposes_cn=d["purposes_cn"],
        incense=d["incense"],
        color=d["color"],
        metal=d["metal"],
        invocation_summary=d["invocation_summary"],
        start_degree=d["start_degree"],
        end_degree=d.get("end_degree", default_end),
        good_uses=d.get("good_uses", []),
        bad_uses=d.get("bad_uses", []),
        greer_notes=d.get("notes", ""),
    )


# ============================================================
# 行星時計算函數 (Planetary Hours Calculation)
# ============================================================

def _chaldean_index(planet_name: str) -> int:
    """Return the 0-based index of a planet in the Chaldean order."""
    return CHALDEAN_ORDER.index(planet_name)


def _planet_for_hour(day_planet: str, hour_offset: int) -> str:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book III, Ch. 9
    Return the ruling planet for a given hour offset from day start.

    Args:
        day_planet: The planet ruling the day (from DAY_PLANETS)
        hour_offset: 0-based offset from first hour of day (0-23)

    Returns:
        str: Planet name
    """
    start_idx = _chaldean_index(day_planet)
    return CHALDEAN_ORDER[(start_idx + hour_offset) % 7]


def _julian_day(year: int, month: int, day: int, hour_ut: float) -> float:
    """Calculate Julian Day from UTC date and hour."""
    return swe.julday(year, month, day, hour_ut)


def _sun_rise_set(
    jd_date_start: float, latitude: float, longitude: float
) -> tuple[float, float]:
    """
    Calculate sunrise and sunset Julian Days for a given date and location.

    Args:
        jd_date_start: Julian Day at 00:00 UT for the requested date
        latitude: Geographic latitude
        longitude: Geographic longitude

    Returns:
        tuple: (sunrise_jd, sunset_jd) in Julian Days (UT)
    """
    geopos = (longitude, latitude, 0.0)
    # Search from half a day before start to catch early-timezone sunrises
    search_start = jd_date_start - 0.5
    try:
        ret_rise, t_rise = swe.rise_trans(
            search_start, swe.SUN, swe.CALC_RISE, geopos
        )
        # Search for sunset after sunrise
        ret_set, t_set = swe.rise_trans(
            t_rise[0], swe.SUN, swe.CALC_SET, geopos
        )
    except Exception as exc:  # noqa: BLE001
        # Fallback for polar regions or ephemeris errors:
        # approximate sunrise at 06:00 UT, sunset at 18:00 UT.
        import warnings
        warnings.warn(
            f"Sunrise/sunset calculation failed ({exc}); "
            "using fallback values (06:00/18:00 UT).",
            RuntimeWarning,
            stacklevel=2,
        )
        t_rise = [jd_date_start + 6.0 / 24.0]
        t_set = [jd_date_start + 18.0 / 24.0]

    return float(t_rise[0]), float(t_set[0])


def _jd_to_local_datetime(jd: float, timezone: float) -> datetime:
    """Convert Julian Day (UT) to local datetime given timezone offset."""
    y, m, d, h = swe.revjul(jd)
    # h is decimal hours in UT; add timezone offset
    h_local = h + timezone
    # Base datetime in UT and apply offset
    base = datetime(int(y), int(m), int(d), 0, 0, 0)
    dt = base + timedelta(hours=h_local)
    return dt


def get_planetary_hours(
    year: int,
    month: int,
    day: int,
    timezone: float,
    latitude: float,
    longitude: float,
) -> PlanetaryHoursResult:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book III, Ch. 9
    計算指定日期和地點的 24 行星時（12 日間時 + 12 夜間時）。

    行星時依迦勒底序（Chaldean order）輪轉，每一日的第一時辰由當日主星管轄。
    日間時長 = 日出到日落 / 12；夜間時長 = 日落到次日日出 / 12。

    Args:
        year: 年
        month: 月
        day: 日
        timezone: 時區偏移（UTC+N）
        latitude: 緯度
        longitude: 經度

    Returns:
        PlanetaryHoursResult
    """
    swe.set_ephe_path("")

    # Build Julian Day at 00:00 UT for this date (used as search start)
    jd_day_start = _julian_day(year, month, day, 0.0)

    # Get sunrise / sunset in JD (UT)
    jd_rise, jd_set = _sun_rise_set(jd_day_start, latitude, longitude)

    # If sunset is before sunrise (polar edge case), fallback
    if jd_set <= jd_rise:
        jd_set = jd_rise + 0.5  # assume 12h day

    # Next sunrise: search after sunset
    geopos = (longitude, latitude, 0.0)
    try:
        _, t_next = swe.rise_trans(jd_set, swe.SUN, swe.CALC_RISE, geopos)
        jd_next_rise = float(t_next[0])
    except Exception as exc:  # noqa: BLE001
        # Fallback for polar regions or ephemeris errors.
        import warnings
        warnings.warn(
            f"Next sunrise calculation failed ({exc}); "
            "using sunset + 12h as fallback.",
            RuntimeWarning,
            stacklevel=2,
        )
        jd_next_rise = jd_set + 0.5
    if jd_next_rise <= jd_set:
        jd_next_rise = jd_set + 0.5

    # Weekday from local noon
    jd_noon = _julian_day(year, month, day, 12.0 - timezone)

    day_len_min = (jd_set - jd_rise) * 24 * 60
    night_len_min = (jd_next_rise - jd_set) * 24 * 60
    day_hour_len = day_len_min / 12
    night_hour_len = night_len_min / 12

    # Weekday (0=Sunday) at local noon
    dt_local_noon = _jd_to_local_datetime(jd_noon, timezone)
    weekday = dt_local_noon.weekday()  # Python: 0=Monday ... 6=Sunday
    # Convert Python weekday (Mon=0) to classical weekday (Sun=0)
    classical_weekday = (weekday + 1) % 7
    day_planet = DAY_PLANETS[classical_weekday]

    # Build 24 hours
    hours: list[PlanetaryHour] = []
    hour_offset = 0

    # 12 day hours
    for i in range(12):
        start_jd = jd_rise + i * (day_hour_len / (24 * 60))
        end_jd = jd_rise + (i + 1) * (day_hour_len / (24 * 60))
        planet = _planet_for_hour(day_planet, hour_offset)
        hours.append(PlanetaryHour(
            hour_number=i + 1,
            is_day=True,
            planet=planet,
            planet_glyph=PLANET_GLYPHS[planet],
            planet_cn=PLANET_NAMES_CN[planet],
            start_time=_jd_to_local_datetime(start_jd, timezone),
            end_time=_jd_to_local_datetime(end_jd, timezone),
            duration_minutes=day_hour_len,
        ))
        hour_offset += 1

    # 12 night hours
    for i in range(12):
        start_jd = jd_set + i * (night_hour_len / (24 * 60))
        end_jd = jd_set + (i + 1) * (night_hour_len / (24 * 60))
        planet = _planet_for_hour(day_planet, hour_offset)
        hours.append(PlanetaryHour(
            hour_number=i + 13,
            is_day=False,
            planet=planet,
            planet_glyph=PLANET_GLYPHS[planet],
            planet_cn=PLANET_NAMES_CN[planet],
            start_time=_jd_to_local_datetime(start_jd, timezone),
            end_time=_jd_to_local_datetime(end_jd, timezone),
            duration_minutes=night_hour_len,
        ))
        hour_offset += 1

    sunrise_dt = _jd_to_local_datetime(jd_rise, timezone)
    sunset_dt = _jd_to_local_datetime(jd_set, timezone)

    return PlanetaryHoursResult(
        date_str=f"{year}/{month:02d}/{day:02d}",
        weekday_en=DAY_NAMES_EN[classical_weekday],
        weekday_cn=DAY_NAMES_CN[classical_weekday],
        day_planet=day_planet,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        sunrise=sunrise_dt,
        sunset=sunset_dt,
        day_length_minutes=day_len_min,
        night_length_minutes=night_len_min,
        hours=hours,
    )


# ============================================================
# 護符推薦函數 (Talisman Recommendation)
# ============================================================

def get_picatrix_talisman_recommendation(intent: str) -> TalismanRecommendation | None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book II, Ch. 10-12
    根據使用者意圖推薦 Picatrix 護符配方。

    Args:
        intent: 意圖關鍵字，支援：
            "love" 愛情, "wealth" 財富, "health" 治病,
            "travel" 旅行, "protection" 保護,
            "knowledge" 知識, "power" 權力, "agriculture" 農業

    Returns:
        TalismanRecommendation | None: 護符推薦，若意圖不識別則回傳 None
    """
    intent_lower = intent.strip().lower()
    # Also match Chinese intents
    cn_map = {
        "愛情": "love", "財富": "wealth", "治病": "health",
        "旅行": "travel", "保護": "protection",
        "知識": "knowledge", "權力": "power", "農業": "agriculture",
    }
    if intent_lower in cn_map:
        intent_lower = cn_map[intent_lower]

    for t in TALISMAN_INTENTS:
        if t["intent_key"] == intent_lower:
            planet = t["planet"]
            mansion_names = [
                PICATRIX_MANSIONS[i]["chinese_name"]
                for i in t["mansion_indices"]
            ]
            return TalismanRecommendation(
                intent_key=t["intent_key"],
                intent_cn=t["intent_cn"],
                intent_en=t["intent_en"],
                planet=planet,
                planet_glyph=PLANET_GLYPHS[planet],
                planet_cn=PLANET_NAMES_CN[planet],
                mansion_indices=t["mansion_indices"],
                mansion_names_cn=mansion_names,
                metal=t["metal"],
                incense=t["incense"],
                color=t["color"],
                hour_planet=t["hour_planet"],
                description_cn=t["description_cn"],
                description_en=t["description_en"],
            )
    return None


def get_all_talisman_intents() -> list[str]:
    """Return all supported intent keys."""
    return [t["intent_key"] for t in TALISMAN_INTENTS]


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_mansion_lookup(moon_lon: float | None = None) -> None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    渲染月宿查詢器（Mansion Lookup Tool）。

    Args:
        moon_lon: 月亮黃經度數（可選；若提供則直接顯示對應月宿）
    """
    st.subheader("🌙 月宿查詢器 (Lunar Mansion Lookup)")
    st.caption("資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) — Greer & Warnock 2011 translation")

    all_mansions = get_all_mansions()

    # Interactive selector
    mansion_options = [
        f"{m.index + 1}. {m.arabic_name} ({m.chinese_name})"
        for m in all_mansions
    ]

    if moon_lon is not None:
        default_idx = get_mansion_index(moon_lon)
    else:
        default_idx = 0

    selected_label = st.selectbox(
        "選擇月宿 (Select Mansion)",
        options=mansion_options,
        index=default_idx,
        key="picatrix_mansion_select",
    )
    selected_idx = mansion_options.index(selected_label)
    mansion = all_mansions[selected_idx]

    _render_single_mansion(mansion)

    st.divider()
    _render_mansion_wheel(all_mansions, highlight_index=mansion.index)


def _render_single_mansion(m: PicatrixMansion) -> None:
    """Render a styled HTML card for a single mansion."""
    fortune_text = "✨ 吉宿" if m.fortunate else "⚠️ 凶宿"
    fortune_bg = "#1a5c35" if m.fortunate else "#6b1a1a"
    border_color = "#2e8b57" if m.fortunate else "#8b0000"
    planet_color = {
        "Saturn": "#4169E1", "Jupiter": "#9400D3", "Mars": "#DC143C",
        "Sun": "#FFD700", "Venus": "#228B22", "Mercury": "#FF8C00", "Moon": "#C0C0C0",
    }.get(m.ruling_planet, "#c8c8c8")

    good_html = "".join(
        f'<li style="color:#a8d8a8;">{u}</li>' for u in m.good_uses
    ) if m.good_uses else ""
    bad_html = "".join(
        f'<li style="color:#f08080;">{u}</li>' for u in m.bad_uses
    ) if m.bad_uses else ""
    purposes_html = "".join(
        f'<span style="background:rgba(255,255,255,0.1);border-radius:4px;'
        f'padding:2px 8px;margin:2px;display:inline-block;color:#e0e0e0;">{p}</span>'
        for p in m.purposes_cn
    )

    notes_html = (
        f'<div style="background:rgba(255,215,0,0.08);border-left:3px solid #FFD700;'
        f'padding:8px 12px;border-radius:0 6px 6px 0;margin-top:10px;">'
        f'<span style="color:#aaa;font-size:0.85em;">📖 注意事項：</span>'
        f'<span style="color:#ddd;font-size:0.9em;"> {m.greer_notes}</span></div>'
        if m.greer_notes else ""
    )

    html = f"""
    <div style="
        background:linear-gradient(135deg,#1a1a2e 0%,#0d1117 100%);
        border:2px solid {border_color};border-radius:12px;
        padding:20px;margin:8px 0;
        box-shadow:0 4px 20px rgba(0,0,0,0.5);
        font-family:'Segoe UI',sans-serif;
    ">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <h3 style="color:#FFD700;margin:0;font-size:1.2em;">
          {m.index+1}. {m.arabic_name}
          <span style="color:#aaa;font-size:0.8em;margin-left:8px;">{m.arabic_script}</span>
        </h3>
        <span style="background:{fortune_bg};color:#fff;padding:3px 12px;
                     border-radius:20px;font-size:0.85em;">{fortune_text}</span>
      </div>
      <p style="color:#ccc;margin:0 0 12px 0;font-size:1em;">
        <strong style="color:#ddd;">{m.chinese_name}</strong>
        &nbsp;·&nbsp; {m.english_name}
      </p>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;">
        <div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:12px;">
          <p style="margin:4px 0;color:#aaa;font-size:0.85em;">統治行星</p>
          <p style="margin:0;color:{planet_color};font-size:1.1em;font-weight:bold;">
            {PLANET_GLYPHS[m.ruling_planet]} {m.ruling_planet} ({PLANET_NAMES_CN[m.ruling_planet]})
          </p>
          <p style="margin:8px 0 4px 0;color:#aaa;font-size:0.85em;">起始度數</p>
          <p style="margin:0;color:#e0e0e0;">{m.start_degree:.3f}° → {m.end_degree:.3f}°</p>
        </div>
        <div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:12px;">
          <p style="margin:4px 0 2px 0;color:#aaa;font-size:0.85em;">
            🎨 顏色：<span style="color:#e0e0e0;">{m.color}</span>
          </p>
          <p style="margin:4px 0 2px 0;color:#aaa;font-size:0.85em;">
            ⚙️ 金屬：<span style="color:#e0e0e0;">{m.metal}</span>
          </p>
          <p style="margin:4px 0 2px 0;color:#aaa;font-size:0.85em;">
            🌿 香料：<span style="color:#e0e0e0;">{m.incense}</span>
          </p>
        </div>
      </div>
      <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:12px;margin-bottom:10px;">
        <p style="color:#aaa;margin:0 0 6px 0;font-size:0.85em;">🖼️ 魔法圖像</p>
        <p style="color:#e0e0e0;margin:0 0 4px 0;">{m.magic_image_cn}</p>
        <p style="color:#888;margin:0;font-style:italic;font-size:0.9em;">{m.magic_image}</p>
      </div>
      <div style="margin-bottom:10px;">
        <p style="color:#aaa;margin:0 0 6px 0;font-size:0.85em;">✦ 用途</p>
        <div>{purposes_html}</div>
      </div>
      {'<div style="margin-bottom:10px;"><p style="color:#aaa;margin:0 0 4px 0;font-size:0.85em;">✅ 吉用</p><ul style="margin:0;padding-left:18px;">' + good_html + '</ul></div>' if good_html else ''}
      {'<div style="margin-bottom:10px;"><p style="color:#aaa;margin:0 0 4px 0;font-size:0.85em;">⚠️ 凶用</p><ul style="margin:0;padding-left:18px;">' + bad_html + '</ul></div>' if bad_html else ''}
      <div style="background:rgba(255,255,255,0.04);border-radius:6px;padding:10px;margin-bottom:8px;">
        <span style="color:#aaa;font-size:0.85em;">📜 咒語摘要：</span>
        <span style="color:#ddd;">{m.invocation_summary}</span>
      </div>
      {notes_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def _render_mansion_wheel(mansions: list, highlight_index: int = -1) -> None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    使用 Plotly Barpolar 繪製 28 月宿輪圖（正圓扇形佈局）。
    """
    st.subheader("🌐 月宿輪圖 (Lunar Mansion Wheel)")
    st.caption("資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)")

    n = 28
    angle_step = 360.0 / n

    colors = []
    line_colors = []
    for m in mansions:
        if m.index == highlight_index:
            colors.append("#FFD700")
            line_colors.append("#fff")
        elif m.fortunate:
            colors.append("#2E8B57")
            line_colors.append("#1a5c35")
        else:
            colors.append("#8B0000")
            line_colors.append("#4a0000")

    thetas = [m.start_degree + angle_step / 2 for m in mansions]
    hover_texts = [
        f"<b>{m.index+1}. {m.arabic_name}</b><br>{m.chinese_name}<br>"
        f"Planet: {PLANET_GLYPHS[m.ruling_planet]} {PLANET_NAMES_CN[m.ruling_planet]}<br>"
        f"{'✨ 吉宿' if m.fortunate else '⚠️ 凶宿'}<br>"
        f"{m.start_degree:.2f}° – {m.end_degree:.2f}°<extra></extra>"
        for m in mansions
    ]

    fig = go.Figure(go.Barpolar(
        r=[1] * n,
        theta=thetas,
        width=[angle_step * 0.92] * n,
        marker_color=colors,
        marker_line_color=line_colors,
        marker_line_width=1.5,
        hovertemplate=hover_texts,
        showlegend=False,
    ))

    fig.update_layout(
        title="Picatrix 28 Lunar Mansions — 阿拉伯月宿輪圖",
        polar=dict(
            radialaxis=dict(
                showticklabels=False, ticks="", range=[0, 1.4],
                showgrid=False, showline=False,
            ),
            angularaxis=dict(
                tickvals=thetas,
                ticktext=[
                    f"{m.index+1}.<br>{m.chinese_name}" for m in mansions
                ],
                direction="clockwise",
                rotation=90,
                tickfont=dict(size=8, color="#c8c8c8"),
                gridcolor="rgba(255,255,255,0.08)",
            ),
            bgcolor="#0d1117",
        ),
        showlegend=False,
        height=620,
        paper_bgcolor="#1a1a2e",
        font=dict(color="#e0e0e0", size=9),
        margin=dict(t=60, b=30, l=30, r=30),
    )

    # Legend
    fig.add_trace(go.Scatterpolar(
        r=[None], theta=[None], mode="markers",
        marker=dict(color="#2E8B57", size=10, symbol="square"),
        name="✨ 吉宿", showlegend=True,
    ))
    fig.add_trace(go.Scatterpolar(
        r=[None], theta=[None], mode="markers",
        marker=dict(color="#8B0000", size=10, symbol="square"),
        name="⚠️ 凶宿", showlegend=True,
    ))
    if highlight_index >= 0:
        fig.add_trace(go.Scatterpolar(
            r=[None], theta=[None], mode="markers",
            marker=dict(color="#FFD700", size=10, symbol="square"),
            name="📍 當前月宿", showlegend=True,
        ))
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.12,
            xanchor="center", x=0.5,
            font=dict(color="#e0e0e0", size=10),
        ),
    )
    st.plotly_chart(fig, width='stretch')


def render_planetary_hours_tool(
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    timezone: float = 8.0,
    latitude: float = 25.0,
    longitude: float = 121.5,
) -> None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book III, Ch. 9
    渲染行星時計算器（Planetary Hours Tool）。

    若未提供 year/month/day，使用今日日期。

    Args:
        year, month, day: Date (optional; defaults to today)
        timezone: UTC offset (default 8.0)
        latitude, longitude: Location coordinates
    """
    st.subheader("⏰ 行星時計算器 (Planetary Hours Calculator)")
    st.caption("資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book III, Ch. 9")

    today = datetime.now(tz=timezone_module.utc)
    year = year or today.year
    month = month or today.month
    day = day or today.day

    with st.spinner("正在計算行星時..."):
        result = get_planetary_hours(year, month, day, timezone, latitude, longitude)

    planet_colors = {
        "Saturn": "#4169E1", "Jupiter": "#9400D3", "Mars": "#DC143C",
        "Sun": "#FFD700", "Venus": "#228B22", "Mercury": "#FF8C00", "Moon": "#C0C0C0",
    }
    day_planet_color = planet_colors.get(result.day_planet, "#c8c8c8")

    # Summary header card
    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,#1a1a2e 0%,#0d1117 100%);
        border:1px solid #333;border-radius:10px;padding:16px 20px;margin-bottom:12px;
        display:grid;grid-template-columns:repeat(3,1fr);gap:10px;
    ">
      <div>
        <p style="color:#888;margin:0 0 2px 0;font-size:0.82em;">📅 日期</p>
        <p style="color:#e0e0e0;margin:0;font-size:1em;font-weight:bold;">{result.date_str}</p>
        <p style="color:#aaa;margin:2px 0 0 0;font-size:0.85em;">{result.weekday_cn} ({result.weekday_en})</p>
      </div>
      <div>
        <p style="color:#888;margin:0 0 2px 0;font-size:0.82em;">🪐 當日主星</p>
        <p style="color:{day_planet_color};margin:0;font-size:1.1em;font-weight:bold;">
          {PLANET_GLYPHS[result.day_planet]} {result.day_planet} ({PLANET_NAMES_CN[result.day_planet]})
        </p>
      </div>
      <div>
        <p style="color:#888;margin:0 0 2px 0;font-size:0.82em;">🌅 日出 / 日落</p>
        <p style="color:#e0e0e0;margin:0;">
          {result.sunrise.strftime('%H:%M:%S')} → {result.sunset.strftime('%H:%M:%S')}
        </p>
        <p style="color:#aaa;margin:2px 0 0 0;font-size:0.82em;">
          日時 {result.day_length_minutes/12:.1f} 分 · 夜時 {result.night_length_minutes/12:.1f} 分
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Build styled HTML table
    rows_html = ""
    for h in result.hours:
        bg = "rgba(255,255,255,0.03)" if h.is_day else "rgba(0,0,0,0.3)"
        icon = "☀️" if h.is_day else "🌙"
        color = planet_colors.get(h.planet, "#c8c8c8")
        session_num = h.hour_number if h.is_day else h.hour_number - 12
        rows_html += f"""
        <tr style="background:{bg};border-bottom:1px solid #2a2a3e;">
          <td style="text-align:center;padding:6px 8px;color:#888;font-size:0.85em;">{h.hour_number}</td>
          <td style="text-align:center;padding:6px 8px;">{icon}</td>
          <td style="text-align:center;padding:6px 8px;color:{color};font-weight:bold;font-size:1.1em;">
            {h.planet_glyph}
          </td>
          <td style="padding:6px 10px;color:{color};font-weight:600;">{h.planet} ({h.planet_cn})</td>
          <td style="text-align:center;padding:6px 8px;color:#aaa;font-size:0.85em;">{session_num}</td>
          <td style="text-align:center;padding:6px 8px;color:#e0e0e0;">{h.start_time.strftime('%H:%M')}</td>
          <td style="text-align:center;padding:6px 8px;color:#e0e0e0;">{h.end_time.strftime('%H:%M')}</td>
          <td style="text-align:center;padding:6px 8px;color:#aaa;font-size:0.85em;">{h.duration_minutes:.1f}</td>
        </tr>"""

    table_html = f"""
    <div style="overflow-x:auto;margin:8px 0;">
    <table style="
        width:100%;border-collapse:collapse;
        background:#0d1117;border-radius:8px;overflow:hidden;
        font-family:'Segoe UI',sans-serif;font-size:0.9em;
    ">
      <thead>
        <tr style="background:#1a1a2e;border-bottom:2px solid #333;">
          <th style="padding:8px;color:#888;font-weight:600;">#</th>
          <th style="padding:8px;color:#888;font-weight:600;">日/夜</th>
          <th style="padding:8px;color:#888;font-weight:600;">符</th>
          <th style="padding:8px;color:#888;font-weight:600;text-align:left;">行星 (Planet)</th>
          <th style="padding:8px;color:#888;font-weight:600;">時辰</th>
          <th style="padding:8px;color:#888;font-weight:600;">開始</th>
          <th style="padding:8px;color:#888;font-weight:600;">結束</th>
          <th style="padding:8px;color:#888;font-weight:600;">時長(分)</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

    # Plotly bar chart
    _render_planetary_hours_chart(result)


def _render_planetary_hours_chart(result: PlanetaryHoursResult) -> None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    Draw a Plotly timeline bar chart for planetary hours.
    """
    st.subheader("📊 行星時圖 (Planetary Hours Chart)")
    planet_colors = {
        "Saturn": "#4169E1", "Jupiter": "#9400D3", "Mars": "#DC143C",
        "Sun": "#FFD700", "Venus": "#228B22", "Mercury": "#FF8C00", "Moon": "#C0C0C0",
    }

    fig = go.Figure()
    for h in result.hours:
        start_str = h.start_time.strftime("%H:%M")
        end_str = h.end_time.strftime("%H:%M")
        label = f"{h.planet_glyph} {h.planet}<br>({h.planet_cn})"
        fig.add_trace(go.Bar(
            x=[h.duration_minutes],
            y=[f"{'☀️' if h.is_day else '🌙'} H{h.hour_number}"],
            orientation="h",
            marker_color=planet_colors.get(h.planet, "#888"),
            name=h.planet,
            hovertemplate=(
                f"<b>Hour {h.hour_number}</b><br>"
                f"Planet: {h.planet} ({h.planet_cn})<br>"
                f"Start: {start_str}<br>End: {end_str}<br>"
                f"Duration: {h.duration_minutes:.1f} min<br>"
                "<extra></extra>"
            ),
            showlegend=False,
        ))
        # Add text annotation in bar
        fig.add_annotation(
            x=h.duration_minutes / 2,
            y=f"{'☀️' if h.is_day else '🌙'} H{h.hour_number}",
            text=f"{h.planet_glyph}",
            showarrow=False,
            font=dict(size=12, color="white"),
        )

    fig.update_layout(
        title=f"Picatrix 行星時 — {result.date_str} ({result.weekday_cn})",
        xaxis_title="時長（分鐘）",
        yaxis_title="時辰",
        barmode="stack",
        height=700,
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#1a1a2e",
        font=dict(color="#e0e0e0"),
    )
    st.plotly_chart(fig, width='stretch')


def render_talisman_generator() -> None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book II, Ch. 10-12
    渲染護符生成器（Talisman Generator）。
    """
    st.subheader("🔮 護符生成器 (Talisman Generator)")
    st.caption("資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book II, Ch. 10-12")

    intent_options = {
        "愛情 (Love & Romance)": "love",
        "財富 (Wealth & Prosperity)": "wealth",
        "治病 (Health & Healing)": "health",
        "旅行 (Safe Travel)": "travel",
        "保護 (Protection & Warding)": "protection",
        "知識 (Knowledge & Wisdom)": "knowledge",
        "權力 (Power & Authority)": "power",
        "農業 (Agriculture & Planting)": "agriculture",
    }

    selected_intent_label = st.selectbox(
        "選擇意圖 (Select Intent)",
        options=list(intent_options.keys()),
        key="picatrix_talisman_intent",
    )
    intent_key = intent_options[selected_intent_label]

    rec = get_picatrix_talisman_recommendation(intent_key)
    if rec is None:
        st.warning("未找到對應護符配方。")
        return

    st.markdown(
        f"### {PLANET_GLYPHS[rec.planet]} {rec.intent_cn} — "
        f"{rec.intent_en} 護符"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**守護行星 (Planet):** "
                 f"{rec.planet_glyph} {rec.planet} ({rec.planet_cn})")
        st.write(f"**金屬 (Metal):** {rec.metal}")
        st.write(f"**顏色 (Color):** {rec.color}")
        st.write(f"**香料 (Incense):** {rec.incense}")
        st.write(f"**施咒時辰行星 (Hour Planet):** "
                 f"{PLANET_GLYPHS[rec.hour_planet]} {rec.hour_planet} "
                 f"({PLANET_NAMES_CN[rec.hour_planet]})")
    with col2:
        st.write("**適合月宿 (Favorable Mansions):**")
        for i, (idx, cn) in enumerate(
            zip(rec.mansion_indices, rec.mansion_names_cn)
        ):
            m = PICATRIX_MANSIONS[idx]
            fortune = "✨" if m["fortunate"] else "⚠️"
            st.write(
                f"  {fortune} 第 {idx + 1} 宿：{m['arabic_name']} ({cn})"
            )

    st.markdown("---")
    st.markdown(f"**施作指引（中文）:** {rec.description_cn}")
    st.markdown(f"**Instructions (English):** {rec.description_en}")

    ritual = generate_talisman_recipe(
        {
            "planet": rec.planet,
            "purpose": rec.intent_cn,
            "timing": rec.description_cn,
            "materials": rec.metal,
            "procedure": rec.description_cn,
        },
        spirit_invocation=True,
        language="zh",
    )
    ritual_steps = ritual.get("ritual_steps", [])
    if ritual_steps:
        st.markdown("#### 🙏 靈體祈請儀式步驟（spirit_invocation=True）")
        for i, step in enumerate(ritual_steps, start=1):
            st.write(f"{i}. {step}")

    # Show mansion images for recommended mansions
    st.markdown("#### 月宿魔法圖像 (Magic Images for Recommended Mansions)")
    for idx in rec.mansion_indices:
        m = PICATRIX_MANSIONS[idx]
        fortune_icon = "✨" if m["fortunate"] else "⚠️"
        st.markdown(
            f"**{m['index'] + 1}. {m['arabic_name']} ({m['chinese_name']})** "
            f"{fortune_icon}"
        )
        st.write(f"  🖼️ {m['magic_image_cn']}")
        st.write(f"  🖼️ _{m['magic_image']}_")


# ============================================================
# 瀏覽函數 (Browse / Reference Functions)
# ============================================================

def render_picatrix_browse() -> None:
    """
    資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
    渲染 Picatrix 完整參考瀏覽器（不需要排盤資料）。
    包含：今日月宿、28 月宿總覽表、月宿輪圖、迦勒底行星序、護符意圖總覽。
    """
    st.subheader("📜 Picatrix 星體魔法參考 (Reference)")
    st.caption(
        "資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) "
        "— Greer & Warnock 2011 / Attrell & Porreca 2019"
    )

    # --- 今日月宿 ---
    swe.set_ephe_path("")
    now = datetime.now(tz=timezone_module.utc)
    now_jd = swe.julday(now.year, now.month, now.day,
                        now.hour + now.minute / 60.0)
    moon_now, _ = swe.calc_ut(now_jd, swe.MOON)
    today_moon_lon = float(moon_now[0]) % 360.0
    today_idx = get_mansion_index(today_moon_lon)
    today_mansion = get_mansion_by_index(today_idx)

    _render_today_mansion_card(today_moon_lon, today_mansion)

    # Sub-tabs for browsing
    browse_tabs = st.tabs([
        "🌐 月宿輪圖", "📋 28 月宿總覽", "🪐 迦勒底行星序",
        "🔮 護符意圖總覽", "🙏 行星祈禱文",
    ])

    all_mansions = get_all_mansions()

    with browse_tabs[0]:
        _render_mansion_wheel(all_mansions, highlight_index=today_idx)

    with browse_tabs[1]:
        _render_mansion_grid(all_mansions, highlight_index=today_idx)

    with browse_tabs[2]:
        _render_chaldean_reference()

    with browse_tabs[3]:
        _render_talisman_intents_table()

    with browse_tabs[4]:
        _render_planetary_prayers()


def _render_today_mansion_card(
    moon_lon: float, mansion: PicatrixMansion
) -> None:
    """渲染今日月宿速覽卡片。"""
    fortune_icon = "✨ 吉宿" if mansion.fortunate else "⚠️ 凶宿"
    st.markdown(
        f"### 🌙 今日月宿：{mansion.index + 1}. {mansion.arabic_name} "
        f"— {mansion.chinese_name} {fortune_icon}"
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("月亮黃經", f"{moon_lon:.2f}°")
    with col2:
        st.metric(
            "統治行星",
            f"{PLANET_GLYPHS[mansion.ruling_planet]} "
            f"{PLANET_NAMES_CN[mansion.ruling_planet]}",
        )
    with col3:
        st.metric("吉凶", fortune_icon)
    st.write(f"**魔法圖像:** {mansion.magic_image_cn}")
    st.write(
        f"**用途:** {' · '.join(mansion.purposes_cn)}"
    )
    st.divider()


def _render_mansion_grid(
    mansions: list, highlight_index: int = -1
) -> None:
    """渲染 28 月宿總覽表格。"""
    st.subheader("📋 28 月宿總覽 (Complete Mansions Reference)")
    st.caption(
        "資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book I, Ch. 4"
    )

    # Summary table
    header = (
        "| # | 中文名 | 阿拉伯名 (Arabic) | 英文名 | "
        "統治行星 | 吉凶 | 顏色 | 金屬 | 香料 |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    for m in mansions:
        fortune = "✨ 吉" if m.fortunate else "⚠️ 凶"
        highlight = " **→**" if m.index == highlight_index else ""
        rows.append(
            f"| {m.index + 1}{highlight} "
            f"| {m.chinese_name} "
            f"| {m.arabic_name} ({m.arabic_script}) "
            f"| {m.english_name} "
            f"| {PLANET_GLYPHS[m.ruling_planet]} {PLANET_NAMES_CN[m.ruling_planet]} "
            f"| {fortune} "
            f"| {m.color} "
            f"| {m.metal} "
            f"| {m.incense} |"
        )
    st.markdown("\n".join(rows))

    # Expandable detail cards
    st.divider()
    st.subheader("🔍 月宿詳細資料 (Detailed Mansion Cards)")
    for m in mansions:
        fortune_icon = "✨ 吉宿" if m.fortunate else "⚠️ 凶宿"
        with st.expander(
            f"{m.index + 1}. {m.arabic_name} — {m.chinese_name} "
            f"({m.english_name}) {fortune_icon}",
            expanded=(m.index == highlight_index),
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**阿拉伯文:** {m.arabic_script}")
                st.write(
                    f"**統治行星:** {PLANET_GLYPHS[m.ruling_planet]} "
                    f"{m.ruling_planet} ({PLANET_NAMES_CN[m.ruling_planet]})"
                )
                st.write(f"**起始度數:** {m.start_degree:.3f}°")
                st.write(f"**顏色:** {m.color}")
            with col2:
                st.write(f"**金屬:** {m.metal}")
                st.write(f"**香料:** {m.incense}")
                st.write(f"**吉凶:** {fortune_icon}")
            st.write(f"**魔法圖像:** {m.magic_image_cn}")
            st.write(f"**Magic Image:** _{m.magic_image}_")
            st.write(
                f"**用途:** {' · '.join(m.purposes_cn)} "
                f"/ {' · '.join(m.purposes)}"
            )
            st.write(f"**咒語摘要:** {m.invocation_summary}")


def _render_chaldean_reference() -> None:
    """渲染迦勒底行星序參考表。"""
    st.subheader("🪐 迦勒底行星序 (Chaldean Planetary Order)")
    st.caption(
        "資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book III, Ch. 9"
    )
    st.markdown(
        """
        **迦勒底序**是古代占星術中行星的基本排列順序，由最慢（土星）
        到最快（月亮），用於決定每日每時辰的行星主宰：

        > ♄ 土星 → ♃ 木星 → ♂ 火星 → ☉ 太陽 → ♀ 金星 → ☿ 水星 → ☽ 月亮

        每一日的**第一時辰**由該日的主星管轄，之後每時辰按迦勒底序輪轉。
        """
    )

    # Planet table
    st.markdown("#### 七曜與星期對應 (Planets & Weekdays)")
    header = "| 星期 | Weekday | 主星 | 符號 | 金屬 | 顏色 |"
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|"
    planet_metals = {
        "Saturn": "鉛 (Lead)", "Jupiter": "錫 (Tin)",
        "Mars": "鐵 (Iron)", "Sun": "金 (Gold)",
        "Venus": "銅 (Copper)", "Mercury": "水銀 (Quicksilver)",
        "Moon": "銀 (Silver)",
    }
    planet_colors = {
        "Saturn": "黑色 (Black)", "Jupiter": "藍紫色 (Purple)",
        "Mars": "紅色 (Red)", "Sun": "金色 (Golden)",
        "Venus": "綠色 (Green)", "Mercury": "橙色 (Orange)",
        "Moon": "銀白色 (Silver)",
    }
    rows = [header, sep]
    for i in range(7):
        planet = DAY_PLANETS[i]
        rows.append(
            f"| {DAY_NAMES_CN[i]} "
            f"| {DAY_NAMES_EN[i]} "
            f"| {PLANET_NAMES_CN[planet]} ({planet}) "
            f"| {PLANET_GLYPHS[planet]} "
            f"| {planet_metals[planet]} "
            f"| {planet_colors[planet]} |"
        )
    st.markdown("\n".join(rows))

    # Chaldean order visual
    st.markdown("#### 迦勒底序環 (Chaldean Circle)")
    order_display = " → ".join(
        f"{PLANET_GLYPHS[p]} {PLANET_NAMES_CN[p]}" for p in CHALDEAN_ORDER
    )
    st.markdown(f"> {order_display} → (循環)")


def _render_talisman_intents_table() -> None:
    """渲染護符意圖總覽表。"""
    st.subheader("🔮 護符意圖總覽 (Talisman Intents Reference)")
    st.caption(
        "資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) Book II, Ch. 10-12"
    )
    st.markdown(
        """
        Picatrix 記載了八種主要護符意圖，每種有對應的守護行星、
        適合施作的月宿、使用材質和儀式指引：
        """
    )

    header = (
        "| 意圖 | Intent | 守護行星 | 金屬 | 香料 | 顏色 | "
        "適合月宿 | 施作時辰 |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    for t in TALISMAN_INTENTS:
        planet = t["planet"]
        mansion_names = [
            f"{PICATRIX_MANSIONS[i]['chinese_name']}({i + 1})"
            for i in t["mansion_indices"]
        ]
        rows.append(
            f"| {t['intent_cn']} "
            f"| {t['intent_en']} "
            f"| {PLANET_GLYPHS[planet]} {PLANET_NAMES_CN[planet]} "
            f"| {t['metal']} "
            f"| {t['incense']} "
            f"| {t['color']} "
            f"| {'、'.join(mansion_names)} "
            f"| {PLANET_GLYPHS[t['hour_planet']]} "
            f"{PLANET_NAMES_CN[t['hour_planet']]} |"
        )
    st.markdown("\n".join(rows))

    # Detailed expanders for each intent
    st.divider()
    st.markdown("#### 📖 護符詳細指引 (Detailed Talisman Instructions)")
    for t in TALISMAN_INTENTS:
        planet = t["planet"]
        with st.expander(
            f"{PLANET_GLYPHS[planet]} {t['intent_cn']} — {t['intent_en']}"
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.write(
                    f"**守護行星:** {PLANET_GLYPHS[planet]} "
                    f"{planet} ({PLANET_NAMES_CN[planet]})"
                )
                st.write(f"**金屬:** {t['metal']}")
                st.write(f"**香料:** {t['incense']}")
                st.write(f"**顏色:** {t['color']}")
                st.write(
                    f"**施咒時辰:** {PLANET_GLYPHS[t['hour_planet']]} "
                    f"{t['hour_planet']} ({PLANET_NAMES_CN[t['hour_planet']]})"
                )
            with col2:
                st.write("**適合月宿:**")
                for i in t["mansion_indices"]:
                    m = PICATRIX_MANSIONS[i]
                    fortune = "✨" if m["fortunate"] else "⚠️"
                    st.write(
                        f"  {fortune} 第 {i + 1} 宿："
                        f"{m['arabic_name']} ({m['chinese_name']})"
                    )
            st.markdown(f"**施作指引（中文）:** {t['description_cn']}")
            st.markdown(f"**Instructions:** {t['description_en']}")


# ── Planetary Prayers (Book II) ──────────────────────────────────────────

def _load_planetary_prayers() -> dict:
    """Load and return the Picatrix planetary prayers/invocations data.

    Returns a dict with keys: source, description, prayers (list of 7),
    usage_notes, license_suggestion.
    """
    _prayers_path = os.path.join(
        os.path.dirname(__file__), os.pardir, "data", "picatrix_planetary_prayers.json"
    )
    with open(_prayers_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _render_planetary_prayers() -> None:
    """渲染 Picatrix 行星祈禱文（Planetary Invocations）。"""
    data = _load_planetary_prayers()
    st.markdown("### 🙏 行星祈禱文 (Planetary Invocations)")
    st.caption(data.get("source", ""))
    st.markdown(f"_{data.get('description', '')}_")

    for prayer in data.get("prayers", []):
        planet_label = (
            f"{prayer.get('name_zh', '')} "
            f"({prayer.get('name_en', '')} / {prayer.get('arabic_name', '')})"
        )
        glyph = PLANET_GLYPHS.get(prayer.get("planet", ""), "")
        with st.expander(f"{glyph} {planet_label}", expanded=False):
            spirits = prayer.get("spirit_names", [])
            if spirits:
                st.markdown(f"**靈名 (Spirit Names):** {', '.join(spirits)}")
            st.markdown(f"**祈禱文：** {prayer.get('prayer_text', '')}")
            if prayer.get("notes"):
                st.info(f"📌 {prayer['notes']}")
            if prayer.get("source"):
                st.caption(f"出處：{prayer['source']}")

    usage = data.get("usage_notes")
    if usage:
        with st.expander("📖 使用須知 (Usage Notes)", expanded=False):
            if isinstance(usage, list):
                for note in usage:
                    st.markdown(f"- {note}")
            else:
                st.markdown(str(usage))
