"""
astro/vedic_dasha.py — Vimshottari & Yogini Dasha 大運系統

Vimshottari: 120-year cycle based on Moon's nakshatra lord.
Yogini: 36-year cycle with 8 Yogini periods.
"""
import streamlit as st
import swisseph as swe
from dataclasses import dataclass, field

_YEAR_DAYS = 365.25

VIMSHOTTARI_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars",
                     "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10,
                     "Mars": 7, "Rahu": 18, "Jupiter": 16,
                     "Saturn": 19, "Mercury": 17}

GRAHA_CN = {
    "Ketu": "計都", "Venus": "金星", "Sun": "太陽", "Moon": "月亮",
    "Mars": "火星", "Rahu": "羅睺", "Jupiter": "木星", "Saturn": "土星",
    "Mercury": "水星",
}

YOGINI_NAMES = ["Mangala", "Pingala", "Dhanya", "Bhramari",
                "Bhadrika", "Ulka", "Siddha", "Sankata"]
YOGINI_YEARS = [1, 2, 3, 4, 5, 6, 7, 8]
YOGINI_CN = {
    "Mangala": "吉祥", "Pingala": "紅光", "Dhanya": "豐收",
    "Bhramari": "蜜蜂", "Bhadrika": "吉祥母", "Ulka": "流星",
    "Siddha": "成就", "Sankata": "障礙",
}


def jd_to_date_str(jd: float) -> str:
    y, m, d, h = swe.revjul(jd)
    return f"{y:04d}-{m:02d}-{int(d):02d}"


@dataclass
class DashaPeriod:
    lord: str
    lord_cn: str
    start_jd: float
    end_jd: float
    start_date: str
    end_date: str
    years: float
    sub_periods: list = field(default_factory=list)


@dataclass
class VimshottariResult:
    moon_nakshatra: str
    moon_nakshatra_lord: str
    balance_years: float
    mahadasha_periods: list = field(default_factory=list)


@dataclass
class YoginiResult:
    moon_nakshatra: str
    starting_yogini: str
    periods: list = field(default_factory=list)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_vimshottari(moon_longitude: float, birth_jd: float) -> VimshottariResult:
    """Compute Vimshottari Dasha (120-year cycle) from Moon's longitude."""
    nak_span = 13.333333333333334  # 360/27
    nak_idx = int(moon_longitude / nak_span) % 27
    nak_names = [
        "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
        "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
        "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha",
        "Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
        "Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati",
    ]
    nak_name = nak_names[nak_idx]
    lord_idx = nak_idx % 9
    starting_lord = VIMSHOTTARI_LORDS[lord_idx]

    # Balance: how much of the first dasha remains
    pos_in_nak = moon_longitude % nak_span
    fraction_elapsed = pos_in_nak / nak_span
    first_years = VIMSHOTTARI_YEARS[starting_lord]
    balance = first_years * (1.0 - fraction_elapsed)

    # Build 9 mahadasha periods (one full cycle starting from lord)
    idx = VIMSHOTTARI_LORDS.index(starting_lord)
    current_jd = birth_jd
    periods = []
    for i in range(9):
        lord = VIMSHOTTARI_LORDS[(idx + i) % 9]
        yrs = balance if i == 0 else VIMSHOTTARI_YEARS[lord]
        end_jd = current_jd + yrs * _YEAR_DAYS
        # Sub-periods (Antardasha)
        subs = _compute_antardasha(lord, current_jd, end_jd, idx + i)
        periods.append(DashaPeriod(
            lord=lord, lord_cn=GRAHA_CN[lord],
            start_jd=current_jd, end_jd=end_jd,
            start_date=jd_to_date_str(current_jd),
            end_date=jd_to_date_str(end_jd),
            years=round(yrs, 4), sub_periods=subs,
        ))
        current_jd = end_jd

    return VimshottariResult(
        moon_nakshatra=nak_name, moon_nakshatra_lord=starting_lord,
        balance_years=round(balance, 4), mahadasha_periods=periods,
    )


def _compute_antardasha(maha_lord: str, start_jd: float, end_jd: float,
                        maha_offset: int) -> list:
    total_days = end_jd - start_jd
    total_years_cycle = 120.0
    idx = VIMSHOTTARI_LORDS.index(maha_lord)
    subs = []
    cur = start_jd
    for j in range(9):
        sub_lord = VIMSHOTTARI_LORDS[(idx + j) % 9]
        sub_yrs = (VIMSHOTTARI_YEARS[maha_lord] *
                   VIMSHOTTARI_YEARS[sub_lord] / total_years_cycle)
        sub_days = sub_yrs * _YEAR_DAYS
        # Scale to fit actual maha period duration
        sub_days_scaled = sub_days * (total_days / (VIMSHOTTARI_YEARS[maha_lord] * _YEAR_DAYS))
        sub_end = cur + sub_days_scaled
        subs.append(DashaPeriod(
            lord=sub_lord, lord_cn=GRAHA_CN[sub_lord],
            start_jd=cur, end_jd=sub_end,
            start_date=jd_to_date_str(cur),
            end_date=jd_to_date_str(sub_end),
            years=round(sub_days_scaled / _YEAR_DAYS, 4),
        ))
        cur = sub_end
    return subs


@st.cache_data(ttl=3600, show_spinner=False)
def compute_yogini(moon_longitude: float, birth_jd: float) -> YoginiResult:
    """Compute Yogini Dasha (36-year cycle)."""
    nak_span = 13.333333333333334
    nak_idx = int(moon_longitude / nak_span) % 27
    nak_names = [
        "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
        "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
        "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha",
        "Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
        "Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati",
    ]
    starting_idx = (nak_idx + 3) % 8
    starting_yogini = YOGINI_NAMES[starting_idx]

    pos_in_nak = moon_longitude % nak_span
    fraction_elapsed = pos_in_nak / nak_span
    first_years = YOGINI_YEARS[starting_idx]
    balance = first_years * (1.0 - fraction_elapsed)

    current_jd = birth_jd
    periods = []
    for i in range(8):
        y_idx = (starting_idx + i) % 8
        name = YOGINI_NAMES[y_idx]
        yrs = balance if i == 0 else YOGINI_YEARS[y_idx]
        end_jd = current_jd + yrs * _YEAR_DAYS
        periods.append(DashaPeriod(
            lord=name, lord_cn=YOGINI_CN[name],
            start_jd=current_jd, end_jd=end_jd,
            start_date=jd_to_date_str(current_jd),
            end_date=jd_to_date_str(end_jd),
            years=round(yrs, 4),
        ))
        current_jd = end_jd

    return YoginiResult(
        moon_nakshatra=nak_names[nak_idx],
        starting_yogini=starting_yogini, periods=periods,
    )
