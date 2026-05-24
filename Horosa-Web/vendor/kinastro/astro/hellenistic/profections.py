"""astro/hellenistic/profections.py
Annual & Monthly Profections (年度/月度守護星 / Lord of the Year / Month)

Hellenistic technique: the Ascendant advances one Whole-Sign house per year,
activating that sign and its ruler as the Lord of the Year.
Monthly profections further subdivide each annual sign into 12 monthly signs.

References: Vettius Valens *Anthologies*, Chris Brennan *Hellenistic Astrology* ch. 18.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_CN = {
    "Aries": "白羊", "Taurus": "金牛", "Gemini": "雙子",
    "Cancer": "巨蟹", "Leo": "獅子", "Virgo": "處女",
    "Libra": "天秤", "Scorpio": "天蠍", "Sagittarius": "射手",
    "Capricorn": "摩羯", "Aquarius": "水瓶", "Pisces": "雙魚",
}

SIGN_GLYPHS = {
    "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
    "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
    "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓",
}

SIGN_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

PLANET_CN = {
    "Sun": "太陽", "Moon": "月亮", "Mercury": "水星",
    "Venus": "金星", "Mars": "火星", "Jupiter": "木星", "Saturn": "土星",
}

PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿",
    "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
}

# House themes per house number (Whole-Sign from ASC)
HOUSE_THEMES_EN = {
    1: ["Self", "Body", "Vitality", "Appearance", "Life Direction"],
    2: ["Finances", "Income", "Possessions", "Resources"],
    3: ["Siblings", "Short Journeys", "Communication", "Learning"],
    4: ["Home", "Family", "Roots", "Property", "Ancestors"],
    5: ["Children", "Creativity", "Pleasure", "Romance", "Recreation"],
    6: ["Health", "Work", "Daily Routine", "Servants", "Illness"],
    7: ["Marriage", "Partnerships", "Open Enemies", "Contracts"],
    8: ["Death", "Inheritance", "Transformation", "Other's Resources"],
    9: ["Travel", "Philosophy", "Religion", "Higher Education", "Law"],
    10: ["Career", "Reputation", "Authority", "Public Status"],
    11: ["Friends", "Hopes", "Gains", "Benefactors", "Social Groups"],
    12: ["Hidden Enemies", "Isolation", "Karma", "Self-Undoing"],
}

HOUSE_THEMES_ZH = {
    1: ["自我", "身體", "活力", "外貌", "人生方向"],
    2: ["財務", "收入", "財產", "資源"],
    3: ["手足", "短途旅行", "溝通", "學習"],
    4: ["家宅", "家族", "祖先", "不動產"],
    5: ["子女", "創意", "歡娛", "戀愛", "娛樂"],
    6: ["健康", "工作", "日常事務", "僕役", "疾病"],
    7: ["婚姻", "合夥", "公開敵人", "合約"],
    8: ["死亡", "遺產", "轉化", "他人資源"],
    9: ["遠行", "哲學", "宗教", "高等教育", "法律"],
    10: ["事業", "名聲", "權威", "公共地位"],
    11: ["朋友", "希望", "所得", "贊助者", "社群"],
    12: ["隱敵", "孤立", "業力", "自我毀滅"],
}


# ─────────────────────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────────────────────

@dataclass
class ProfectionYear:
    """One year's Annual Profection data."""
    age: int
    calendar_year: int          # approximate calendar year (birth_year + age)
    sign: str                   # profected sign name
    sign_cn: str
    sign_glyph: str
    house: int                  # house number from ASC (1–12)
    lord: str                   # Lord of the Year (planet name)
    lord_cn: str
    lord_glyph: str
    is_current: bool            # True if this is the current profection year
    house_themes_en: list[str] = field(default_factory=list)
    house_themes_zh: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "age": self.age,
            "year": self.calendar_year,
            "sign": f"{self.sign_glyph} {self.sign}",
            "sign_cn": self.sign_cn,
            "house": self.house,
            "lord": f"{self.lord_glyph} {self.lord}",
            "lord_cn": f"{self.lord_glyph} {self.lord_cn}",
            "is_current": self.is_current,
            "themes_en": ", ".join(self.house_themes_en[:3]),
            "themes_zh": "、".join(self.house_themes_zh[:3]),
        }


# ─────────────────────────────────────────────────────────────
# Core Computation
# ─────────────────────────────────────────────────────────────

def compute_profections_table(
    asc_lon: float,
    birth_year: int,
    num_years: int = 24,
    current_age: int | None = None,
) -> list[ProfectionYear]:
    """Compute Annual Profections for *num_years* starting from birth.

    年度守護星計算（從出生到 num_years 年後）

    Each year the Ascendant advances one Whole-Sign house.
    The ruler of that sign becomes the Lord of the Year.

    Parameters
    ----------
    asc_lon:
        Natal Ascendant longitude (0–360°).
    birth_year:
        Birth year (e.g. 1990).
    num_years:
        How many years to compute (default 24, covering two 12-year cycles).
    current_age:
        If provided, marks the matching entry as ``is_current=True``.
        If None, uses today's year to estimate current age.

    Returns
    -------
    list[ProfectionYear]
    """
    asc_sign_idx = int(asc_lon / 30) % 12

    if current_age is None:
        current_age = date.today().year - birth_year

    rows: list[ProfectionYear] = []
    for age in range(num_years):
        sign_idx = (asc_sign_idx + age) % 12
        sign = ZODIAC_SIGNS[sign_idx]
        lord = SIGN_RULERS[sign]
        house = age % 12 + 1

        rows.append(ProfectionYear(
            age=age,
            calendar_year=birth_year + age,
            sign=sign,
            sign_cn=SIGN_CN[sign],
            sign_glyph=SIGN_GLYPHS[sign],
            house=house,
            lord=lord,
            lord_cn=PLANET_CN.get(lord, lord),
            lord_glyph=PLANET_GLYPHS.get(lord, ""),
            is_current=(age == current_age),
            house_themes_en=HOUSE_THEMES_EN.get(house, []),
            house_themes_zh=HOUSE_THEMES_ZH.get(house, []),
        ))
    return rows


# ─────────────────────────────────────────────────────────────
# Monthly Profections
# ─────────────────────────────────────────────────────────────

@dataclass
class MonthlyProfection:
    """One month's Monthly Profection data within a profection year.

    月度守護星：在年度守護星宮位內，每個月再前進一個星座。
    """
    age: int
    month_index: int            # 0–11 within the profection year
    sign: str
    sign_cn: str
    sign_glyph: str
    house: int                  # house number from ASC (1–12)
    lord: str
    lord_cn: str
    lord_glyph: str
    start_date: str             # approximate ISO date "YYYY-MM-DD"
    is_current: bool

    def to_dict(self) -> dict:
        return {
            "age": self.age,
            "month_index": self.month_index,
            "sign": f"{self.sign_glyph} {self.sign}",
            "sign_cn": self.sign_cn,
            "house": self.house,
            "lord": f"{self.lord_glyph} {self.lord}",
            "lord_cn": f"{self.lord_glyph} {self.lord_cn}",
            "start_date": self.start_date,
            "is_current": self.is_current,
        }


def _birthday_for_age(birth_year: int, birth_month: int, birth_day: int, age: int) -> date:
    """Return the date of the birthday for a given age (handles Feb 29)."""
    target_year = birth_year + age
    try:
        return date(target_year, birth_month, birth_day)
    except ValueError:
        # Feb 29 in non-leap year → Mar 1
        return date(target_year, 3, 1)


def compute_monthly_profections(
    asc_lon: float,
    birth_year: int,
    birth_month: int,
    birth_day: int,
    target_date: date | None = None,
    num_years: int = 3,
) -> list[MonthlyProfection]:
    """Compute Monthly Profections for *num_years* starting from birth.

    月度守護星計算：年度守護星宮位內每月再前進一宮。

    Each annual profection sign subdivides into 12 monthly signs, cycling
    forward from the annual sign in lock-step with the calendar month after
    the birthday.

    Parameters
    ----------
    asc_lon:
        Natal Ascendant longitude (0–360°).
    birth_year, birth_month, birth_day:
        Date of birth components.
    target_date:
        Date to mark as ``is_current``.  Defaults to today.
    num_years:
        How many annual cycles (each with 12 months) to compute.

    Returns
    -------
    list[MonthlyProfection]
    """
    if target_date is None:
        target_date = date.today()

    asc_sign_idx = int(asc_lon / 30) % 12
    rows: list[MonthlyProfection] = []

    for age in range(num_years):
        annual_sign_idx = (asc_sign_idx + age) % 12
        birthday = _birthday_for_age(birth_year, birth_month, birth_day, age)

        for month_offset in range(12):
            monthly_sign_idx = (annual_sign_idx + month_offset) % 12
            sign = ZODIAC_SIGNS[monthly_sign_idx]
            lord = SIGN_RULERS[sign]
            # House is the position of the monthly sign relative to the natal Ascendant
            house = (monthly_sign_idx - asc_sign_idx) % 12 + 1

            # Approximate start date: birthday + ~30 days per month
            approx_start = birthday + timedelta(days=month_offset * 30)
            approx_end = birthday + timedelta(days=(month_offset + 1) * 30)

            is_current = approx_start <= target_date < approx_end

            rows.append(MonthlyProfection(
                age=age,
                month_index=month_offset,
                sign=sign,
                sign_cn=SIGN_CN[sign],
                sign_glyph=SIGN_GLYPHS[sign],
                house=house,
                lord=lord,
                lord_cn=PLANET_CN.get(lord, lord),
                lord_glyph=PLANET_GLYPHS.get(lord, ""),
                start_date=approx_start.isoformat(),
                is_current=is_current,
            ))
    return rows


def get_current_profection(
    asc_lon: float,
    birth_year: int,
    target_date: date | None = None,
) -> ProfectionYear:
    """Return the single current-year ProfectionYear for *target_date*.

    便利函數：取得指定日期的當前年度守護星。

    Parameters
    ----------
    asc_lon:
        Natal Ascendant longitude.
    birth_year:
        Birth year.
    target_date:
        Date to evaluate (defaults to today).

    Returns
    -------
    ProfectionYear
    """
    if target_date is None:
        target_date = date.today()
    current_age = target_date.year - birth_year
    rows = compute_profections_table(
        asc_lon=asc_lon,
        birth_year=birth_year,
        num_years=current_age + 2,
        current_age=current_age,
    )
    return next((r for r in rows if r.is_current), rows[current_age])
