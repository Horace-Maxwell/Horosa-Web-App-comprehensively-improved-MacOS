"""
七政四餘流時對盤模組 (Transit Chart Comparison Module)

計算指定時間（預設為當前時刻）的七政四餘星曜位置，
與本命盤對照顯示。
"""

import streamlit as st
import swisseph as swe
from dataclasses import dataclass, field
from datetime import datetime

from .calculator import (
    _normalize_degree, _get_western_sign, _get_chinese_sign,
    _degree_to_sign_degree, PlanetPosition,
)
from .constants import SEVEN_GOVERNORS, FOUR_REMAINDERS, FIVE_ELEMENTS


@dataclass
class TransitData:
    """流時盤資料"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    julian_day: float
    planets: list = field(default_factory=list)   # List[PlanetPosition]


@st.cache_data(ttl=3600, show_spinner=False)
def compute_transit(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
) -> TransitData:
    """
    計算指定時間的星曜位置（流時盤）。

    Parameters:
        year, month, day, hour, minute: 時間
        timezone: 時區偏移

    Returns:
        TransitData
    """
    swe.set_ephe_path("")

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    planets = []

    # 七政
    for name, planet_id in SEVEN_GOVERNORS.items():
        result, flags = swe.calc_ut(jd, planet_id)
        lon = _normalize_degree(result[0])
        lat = result[1]
        speed = result[3]
        retrograde = speed < 0

        pos = PlanetPosition(
            name=name,
            longitude=lon,
            latitude=lat,
            sign_western=_get_western_sign(lon),
            sign_chinese=_get_chinese_sign(lon),
            sign_degree=_degree_to_sign_degree(lon),
            element=FIVE_ELEMENTS.get(name, ""),
            retrograde=retrograde,
        )
        planets.append(pos)

    # 四餘
    # 計都 (Ketu) = 升交點 / North Node
    ketu_result, _ = swe.calc_ut(jd, FOUR_REMAINDERS["計都"])
    ketu_lon = _normalize_degree(ketu_result[0])
    # 羅睺 (Rahu) = 降交點 / South Node = 計都 + 180°
    rahu_lon = _normalize_degree(ketu_lon + 180.0)
    planets.append(PlanetPosition(
        name="羅睺", longitude=rahu_lon, latitude=-ketu_result[1],
        sign_western=_get_western_sign(rahu_lon),
        sign_chinese=_get_chinese_sign(rahu_lon),
        sign_degree=_degree_to_sign_degree(rahu_lon),
        element=FIVE_ELEMENTS.get("羅睺", ""), retrograde=False,
    ))

    planets.append(PlanetPosition(
        name="計都", longitude=ketu_lon, latitude=ketu_result[1],
        sign_western=_get_western_sign(ketu_lon),
        sign_chinese=_get_chinese_sign(ketu_lon),
        sign_degree=_degree_to_sign_degree(ketu_lon),
        element=FIVE_ELEMENTS.get("計都", ""), retrograde=False,
    ))

    yuebei_result, _ = swe.calc_ut(jd, FOUR_REMAINDERS["月孛"])
    yuebei_lon = _normalize_degree(yuebei_result[0])
    planets.append(PlanetPosition(
        name="月孛", longitude=yuebei_lon, latitude=yuebei_result[1],
        sign_western=_get_western_sign(yuebei_lon),
        sign_chinese=_get_chinese_sign(yuebei_lon),
        sign_degree=_degree_to_sign_degree(yuebei_lon),
        element=FIVE_ELEMENTS.get("月孛", ""), retrograde=False,
    ))

    # 紫氣 (Ziqi) = Osculating Apogee (True Apogee)
    ziqi_result, _ = swe.calc_ut(jd, FOUR_REMAINDERS["紫氣"])
    ziqi_lon = _normalize_degree(ziqi_result[0])
    planets.append(PlanetPosition(
        name="紫氣", longitude=ziqi_lon, latitude=ziqi_result[1],
        sign_western=_get_western_sign(ziqi_lon),
        sign_chinese=_get_chinese_sign(ziqi_lon),
        sign_degree=_degree_to_sign_degree(ziqi_lon),
        element=FIVE_ELEMENTS.get("紫氣", ""), retrograde=False,
    ))

    return TransitData(
        year=year, month=month, day=day,
        hour=hour, minute=minute, timezone=timezone,
        julian_day=jd, planets=planets,
    )


def compute_transit_now(timezone: float = 8.0) -> TransitData:
    """計算當前時間的流時盤"""
    from datetime import timedelta, timezone as tz_cls
    utc_now = datetime.now(tz=tz_cls.utc)
    local_now = utc_now + timedelta(hours=timezone)
    return compute_transit(
        year=local_now.year,
        month=local_now.month,
        day=local_now.day,
        hour=local_now.hour,
        minute=local_now.minute,
        timezone=timezone,
    )
