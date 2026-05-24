"""
astro/twelve_ci.py — 十二星次占星 (Twelve Ci / Jupiter Station Astrology)

中國古代木星分野系統。以冬至點為黃道 0° 起點，將 360° 等分為十二次，
每次 30°，依木星所在黃道位置判定星次歸屬。

Twelve Ci is the ancient Chinese Jupiter-station system.  Starting from
the winter-solstice point as 0° ecliptic longitude, the ecliptic is
divided into twelve equal 30° sections (次).  The position of Jupiter
along the *tropical* ecliptic determines the active Ci.

100% follows the architectural patterns of babylonian.py / yemeni.py:
  - dataclass for the chart object
  - compute function  → compute_twelve_ci_chart()
  - render function   → render_twelve_ci_chart()
  - SVG builder       → build_twelve_ci_svg()
"""

from __future__ import annotations

import math
import streamlit as st
import swisseph as swe
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional

from astro.i18n import t, get_lang

# ============================================================
# 十二星次定義 — 冬至 0° 起、每 30° 一次
# Twelve Ci definitions — winter solstice = 0°, 30° each
# ============================================================

# The tropical ecliptic longitude of the winter solstice (Capricorn 0°)
# is 270° in standard Western reckoning.  We convert Jupiter's tropical
# longitude to a "Ci longitude" measured from the winter-solstice point:
#   ci_lon = (tropical_lon - 270) % 360
# Then ci_index = int(ci_lon / 30).
_WINTER_SOLSTICE_LON = 270.0

TWELVE_CI = [
    {
        "index": 0,
        "name_zh": "星紀",
        "name_en": "Xing Ji",
        "name_pinyin": "Xīng Jì",
        "range": "0°–30°",
        "branch": "丑",
        "mansions": "斗牛女",
        "fenye": "吳／揚州",
        "solar_approx": "約 12/22 – 1/20",
        "element": "土",
        "interpretation_zh": (
            "星紀之人穩重務實，如大地承載萬物。木星入星紀，主沈穩、勤勉、"
            "有耐心與責任感。事業上適合金融、地產、公務等需要長期耕耘的領域。"
            "感情深沉內斂，重承諾，需注意過於保守而錯失機緣。"
        ),
        "interpretation_en": (
            "Xing Ji natives are grounded and pragmatic, like the earth "
            "supporting all things.  Jupiter in Xing Ji indicates steadiness, "
            "diligence, patience and responsibility.  Suited to finance, real "
            "estate or civil service.  In love, deeply loyal but may miss "
            "opportunities due to excessive caution."
        ),
    },
    {
        "index": 1,
        "name_zh": "玄枵",
        "name_en": "Xuan Xiao",
        "name_pinyin": "Xuán Xiāo",
        "range": "30°–60°",
        "branch": "子",
        "mansions": "女虛危",
        "fenye": "齊／青州",
        "solar_approx": "約 1/20 – 2/19",
        "element": "水",
        "interpretation_zh": (
            "玄枵如深淵之水，廣納百川。木星入玄枵，主聰穎靈動、善於謀略，"
            "擅長外交與溝通。事業適合科技、傳媒、國際貿易。"
            "感情上富魅力但易飄忽不定，需修煉專注力。"
        ),
        "interpretation_en": (
            "Xuan Xiao resembles deep water that gathers all streams.  "
            "Jupiter here indicates intelligence, strategic thinking and "
            "skill in diplomacy.  Career in tech, media or trade suits well.  "
            "Charming in love but may be fickle — cultivate focus."
        ),
    },
    {
        "index": 2,
        "name_zh": "娵訾",
        "name_en": "Ju Zi",
        "name_pinyin": "Jū Zī",
        "range": "60°–90°",
        "branch": "亥",
        "mansions": "室壁",
        "fenye": "衛／并州",
        "solar_approx": "約 2/19 – 3/21",
        "element": "水",
        "interpretation_zh": (
            "娵訾象徵雲水之間的變幻，富創造力與想像力。木星入娵訾，主藝術天份、"
            "靈性修為與直覺力。事業適合文藝、設計、宗教、心理學。"
            "感情上浪漫多情，需防沉溺幻想。"
        ),
        "interpretation_en": (
            "Ju Zi symbolises shifting clouds and water — creative and "
            "imaginative.  Jupiter here grants artistic talent, spirituality "
            "and intuition.  Suits arts, design, religion or psychology.  "
            "Romantic but must beware illusions."
        ),
    },
    {
        "index": 3,
        "name_zh": "降婁",
        "name_en": "Jiang Lou",
        "name_pinyin": "Jiàng Lóu",
        "range": "90°–120°",
        "branch": "戌",
        "mansions": "奎婁",
        "fenye": "魯／徐州",
        "solar_approx": "約 3/21 – 4/20",
        "element": "土",
        "interpretation_zh": (
            "降婁如春雷破土，具行動力與開創精神。木星入降婁，主勇敢進取、"
            "領導才能強。事業適合創業、軍事、體育。"
            "感情上熱烈直率，需注意急躁與控制慾。"
        ),
        "interpretation_en": (
            "Jiang Lou is like spring thunder breaking ground — active and "
            "pioneering.  Jupiter here indicates courage, leadership and "
            "initiative.  Business, military or sports suit well.  "
            "Passionate in love but watch for impatience."
        ),
    },
    {
        "index": 4,
        "name_zh": "大梁",
        "name_en": "Da Liang",
        "name_pinyin": "Dà Liáng",
        "range": "120°–150°",
        "branch": "酉",
        "mansions": "胃昴畢",
        "fenye": "趙／冀州",
        "solar_approx": "約 4/20 – 5/21",
        "element": "金",
        "interpretation_zh": (
            "大梁如棟樑之材，穩固而有氣度。木星入大梁，主品味高雅、"
            "務實能幹，善於累積財富。事業適合建築、金融、管理。"
            "感情上重品質與安全感，需防固執己見。"
        ),
        "interpretation_en": (
            "Da Liang is the great beam — solid and dignified.  Jupiter "
            "here indicates refined taste, pragmatic competence and wealth "
            "accumulation.  Architecture, finance, management suit well.  "
            "Values quality in love; avoid stubbornness."
        ),
    },
    {
        "index": 5,
        "name_zh": "實沈",
        "name_en": "Shi Chen",
        "name_pinyin": "Shí Chén",
        "range": "150°–180°",
        "branch": "申",
        "mansions": "觜參",
        "fenye": "晉／益州",
        "solar_approx": "約 5/21 – 6/21",
        "element": "金",
        "interpretation_zh": (
            "實沈主雙面之才，靈活善變、口才出眾。木星入實沈，主多元才華、"
            "溝通能力強、善於學習新事物。事業適合教育、寫作、貿易。"
            "感情上風趣幽默但易分心。"
        ),
        "interpretation_en": (
            "Shi Chen denotes dual talent — versatile, eloquent and quick-"
            "witted.  Jupiter here grants diverse abilities, strong "
            "communication and love of learning.  Suits education, writing "
            "or trade.  Witty in love but easily distracted."
        ),
    },
    {
        "index": 6,
        "name_zh": "鶉首",
        "name_en": "Chun Shou",
        "name_pinyin": "Chún Shǒu",
        "range": "180°–210°",
        "branch": "未",
        "mansions": "井鬼",
        "fenye": "秦／雍州",
        "solar_approx": "約 6/21 – 7/23",
        "element": "土",
        "interpretation_zh": (
            "鶉首如慈母護幼，重視家庭與情感羈絆。木星入鶉首，主情感豐沛、"
            "直覺敏銳、護家意識強。事業適合餐飲、醫護、教育。"
            "感情上深情專一，需防情緒化。"
        ),
        "interpretation_en": (
            "Chun Shou is like a mother protecting her young — family and "
            "emotional bonds are paramount.  Jupiter here gives rich "
            "emotions, keen intuition and strong protective instincts.  "
            "Suits food/health/education.  Devoted in love; guard against "
            "moodiness."
        ),
    },
    {
        "index": 7,
        "name_zh": "鶉火",
        "name_en": "Chun Huo",
        "name_pinyin": "Chún Huǒ",
        "range": "210°–240°",
        "branch": "午",
        "mansions": "柳星張",
        "fenye": "周／三河",
        "solar_approx": "約 7/23 – 8/23",
        "element": "火",
        "interpretation_zh": (
            "鶉火如烈日當空，光芒四射。木星入鶉火，主自信、慷慨、"
            "領袖魅力。事業適合演藝、政治、管理。"
            "感情上熱情大方，需防驕傲自滿。"
        ),
        "interpretation_en": (
            "Chun Huo is the blazing midday sun — radiant and commanding.  "
            "Jupiter here gives confidence, generosity and leadership "
            "charisma.  Suits performance, politics, management.  "
            "Warm and generous in love; avoid arrogance."
        ),
    },
    {
        "index": 8,
        "name_zh": "鶉尾",
        "name_en": "Chun Wei",
        "name_pinyin": "Chún Wěi",
        "range": "240°–270°",
        "branch": "巳",
        "mansions": "翼軫",
        "fenye": "楚／荊州",
        "solar_approx": "約 8/23 – 9/23",
        "element": "火",
        "interpretation_zh": (
            "鶉尾主精密分析與服務精神。木星入鶉尾，主勤奮、注重細節、"
            "追求完美。事業適合醫學、研究、會計。"
            "感情上含蓄內斂，需學會表達與放鬆。"
        ),
        "interpretation_en": (
            "Chun Wei denotes precise analysis and service.  Jupiter here "
            "indicates diligence, attention to detail and perfectionism.  "
            "Medicine, research, accounting suit well.  Reserved in love — "
            "learn to express and relax."
        ),
    },
    {
        "index": 9,
        "name_zh": "壽星",
        "name_en": "Shou Xing",
        "name_pinyin": "Shòu Xīng",
        "range": "270°–300°",
        "branch": "辰",
        "mansions": "角亢",
        "fenye": "鄭／兗州",
        "solar_approx": "約 9/23 – 10/23",
        "element": "木",
        "interpretation_zh": (
            "壽星主和諧平衡、人際圓融。木星入壽星，主公正、優雅、"
            "善於合作。事業適合法律、外交、藝術。"
            "感情上追求平等與美感，需防優柔寡斷。"
        ),
        "interpretation_en": (
            "Shou Xing signifies harmony, balance and social grace.  Jupiter "
            "here gives fairness, elegance and cooperative ability.  Law, "
            "diplomacy and art suit well.  Seeks equality in love — avoid "
            "indecisiveness."
        ),
    },
    {
        "index": 10,
        "name_zh": "大火",
        "name_en": "Da Huo",
        "name_pinyin": "Dà Huǒ",
        "range": "300°–330°",
        "branch": "卯",
        "mansions": "氐房心",
        "fenye": "宋／豫州",
        "solar_approx": "約 10/23 – 11/22",
        "element": "木",
        "interpretation_zh": (
            "大火如深秋烈焰，洞察力與意志力極強。木星入大火，主深邃、"
            "果斷、善於轉化困境。事業適合偵查、心理、金融投資。"
            "感情上熱烈而專注，需注意佔有慾。"
        ),
        "interpretation_en": (
            "Da Huo is the autumn blaze — intense insight and willpower.  "
            "Jupiter here grants depth, decisiveness and the ability to "
            "transform adversity.  Investigation, psychology and finance "
            "suit well.  Intense in love; guard against possessiveness."
        ),
    },
    {
        "index": 11,
        "name_zh": "析木",
        "name_en": "Xi Mu",
        "name_pinyin": "Xī Mù",
        "range": "330°–360°",
        "branch": "寅",
        "mansions": "尾箕",
        "fenye": "燕／幽州",
        "solar_approx": "約 11/22 – 12/22",
        "element": "火",
        "interpretation_zh": (
            "析木如遠行之箭，追求自由與真理。木星入析木，主樂觀、"
            "冒險精神、哲學思維。事業適合教育、旅遊、出版。"
            "感情上開朗豁達，需防承諾恐懼。"
        ),
        "interpretation_en": (
            "Xi Mu is the arrow in flight — freedom-seeking and truth-"
            "loving.  Jupiter here gives optimism, adventurous spirit and "
            "philosophical thinking.  Education, travel, publishing suit "
            "well.  Open-hearted in love but may fear commitment."
        ),
    },
]

# Quick lookup helpers
CI_NAMES_ZH = [c["name_zh"] for c in TWELVE_CI]
CI_NAMES_EN = [c["name_en"] for c in TWELVE_CI]
CI_BRANCHES = [c["branch"] for c in TWELVE_CI]

# Mapping from ci_index to branch
CI_BRANCH_MAP = {c["index"]: c["branch"] for c in TWELVE_CI}

# ============================================================
# 行星名稱 (for tropical planet calculation)
# ============================================================
_PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
}

_PLANET_ZH = {
    "Sun": "太陽", "Moon": "太陰", "Mercury": "水星",
    "Venus": "金星", "Mars": "火星", "Jupiter": "木星",
    "Saturn": "土星",
}


# ============================================================
# 資料結構 — Chart dataclass
# ============================================================

@dataclass
class TwelveCiPlanet:
    """One planet's position in the Twelve Ci system."""
    name: str           # English name
    name_zh: str        # Chinese name
    longitude: float    # tropical ecliptic longitude 0–360
    ci_longitude: float  # longitude measured from winter solstice 0–360
    ci_index: int       # 0–11
    ci_name_zh: str     # e.g. "星紀"
    ci_name_en: str     # e.g. "Xing Ji"
    degree_in_ci: float  # 0–30
    retrograde: bool
    speed: float


@dataclass
class TwelveCiChart:
    """Complete Twelve Ci natal chart."""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str = ""
    julian_day: float = 0.0
    planets: list = field(default_factory=list)       # list[TwelveCiPlanet]
    jupiter: Optional[TwelveCiPlanet] = None         # convenience reference
    jupiter_ci: Optional[dict] = None                # full CI dict for Jupiter
    transit_jupiter: Optional[TwelveCiPlanet] = None  # current transit Jupiter
    transit_jupiter_ci: Optional[dict] = None


# ============================================================
# 核心計算函數 (Core Computation)
# ============================================================

def _normalize(lon: float) -> float:
    """Normalize longitude to [0, 360)."""
    return lon % 360.0


def _tropical_to_ci_lon(tropical_lon: float) -> float:
    """Convert tropical ecliptic longitude to CI longitude (winter solstice = 0°)."""
    return (tropical_lon - _WINTER_SOLSTICE_LON) % 360.0


def _ci_index(ci_lon: float) -> int:
    """Return the 0-based Ci index for a given Ci longitude."""
    idx = int(ci_lon / 30.0)
    if idx >= 12:
        idx = 11
    return idx


def _compute_planet_ci(name: str, jd: float) -> TwelveCiPlanet:
    """Compute one planet's tropical position and map to Twelve Ci."""
    result, _ = swe.calc_ut(jd, _PLANET_IDS[name])
    lon = _normalize(result[0])
    speed = result[3]
    ci_lon = _tropical_to_ci_lon(lon)
    idx = _ci_index(ci_lon)
    ci = TWELVE_CI[idx]
    return TwelveCiPlanet(
        name=name,
        name_zh=_PLANET_ZH[name],
        longitude=round(lon, 4),
        ci_longitude=round(ci_lon, 4),
        ci_index=idx,
        ci_name_zh=ci["name_zh"],
        ci_name_en=ci["name_en"],
        degree_in_ci=round(ci_lon % 30.0, 4),
        retrograde=speed < 0,
        speed=round(speed, 6),
    )


@st.cache_data(ttl=3600, show_spinner=False)
def compute_twelve_ci_chart(
    year: int, month: int, day: int,
    hour: int, minute: int, timezone: float,
    latitude: float, longitude: float,
    location_name: str = "",
) -> TwelveCiChart:
    """
    計算十二星次排盤（Tropical / 熱帶黃道）

    Parameters match the standard compute interface used by all systems.

    Returns
    -------
    TwelveCiChart
        Contains all planet positions mapped to 12 Ci, plus Jupiter detail.
    """
    swe.set_ephe_path("")

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    planets = []
    jupiter_planet = None

    for name in _PLANET_IDS:
        p = _compute_planet_ci(name, jd)
        planets.append(p)
        if name == "Jupiter":
            jupiter_planet = p

    jupiter_ci = TWELVE_CI[jupiter_planet.ci_index] if jupiter_planet else None

    # Transit Jupiter (current moment)
    now = datetime.now(tz=None)  # UTC-naive datetime; swisseph expects UT
    jd_now = swe.julday(now.year, now.month, now.day,
                        now.hour + now.minute / 60.0)
    transit_jup = _compute_planet_ci("Jupiter", jd_now)
    transit_ci = TWELVE_CI[transit_jup.ci_index]

    return TwelveCiChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute, timezone=timezone,
        latitude=latitude, longitude=longitude,
        location_name=location_name,
        julian_day=jd,
        planets=planets,
        jupiter=jupiter_planet,
        jupiter_ci=jupiter_ci,
        transit_jupiter=transit_jup,
        transit_jupiter_ci=transit_ci,
    )


# ============================================================
# SVG 視覺化 — 十二星次輪盤
# ============================================================

def build_twelve_ci_svg(
    chart: TwelveCiChart,
    *,
    size: int = 520,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    hour: int | None = None,
    minute: int | None = None,
    tz: float | None = None,
    location: str = "",
) -> str:
    """Build an SVG wheel for the Twelve Ci system.

    The wheel has:
    - An outer ring of 12 × 30° sectors labelled with Ci names (Chinese).
    - A second ring showing the corresponding Earthly Branch (地支).
    - Planet glyphs placed at their Ci-longitude on the inner part.
    - Jupiter highlighted in gold.

    Returns raw HTML ``<div>…<svg>…</svg></div>`` suitable for
    ``st.markdown(..., unsafe_allow_html=True)``.
    """
    cx = cy = size / 2
    r_outer = size / 2 - 10
    r_mid = r_outer - 36
    r_inner = r_mid - 30
    r_planet = r_inner - 28

    parts: list[str] = []
    parts.append(
        f'<div style="display:flex;justify-content:center;margin:12px 0;">'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}" '
        f'style="max-width:100%;height:auto;">'
    )

    # Background
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" '
        f'fill="#0d1117" stroke="#4a3f6b" stroke-width="2"/>'
    )

    # Draw 12 sectors
    _SECTOR_COLORS = [
        "#1a1a3e", "#1e2a3e", "#1a2e2e", "#1e3a2a",
        "#2a2a1a", "#3a2a1a", "#3e1a1a", "#3e1a2a",
        "#2e1a3e", "#1a1a3e", "#1a2a3e", "#1e1a2e",
    ]

    for i in range(12):
        # Sectors go clockwise from top.  In SVG, 0° is right (3 o'clock).
        # We rotate so that Ci 0 (星紀) starts at the top-left.
        # Angle in SVG: start from -90° (12 o'clock), clockwise.
        a_start = math.radians(-90 + i * 30)
        a_end = math.radians(-90 + (i + 1) * 30)

        x1 = cx + r_outer * math.cos(a_start)
        y1 = cy + r_outer * math.sin(a_start)
        x2 = cx + r_outer * math.cos(a_end)
        y2 = cy + r_outer * math.sin(a_end)
        x3 = cx + r_inner * math.cos(a_end)
        y3 = cy + r_inner * math.sin(a_end)
        x4 = cx + r_inner * math.cos(a_start)
        y4 = cy + r_inner * math.sin(a_start)

        # Sector path (arc + lines)
        large_arc = 0
        path_d = (
            f"M {x4:.1f} {y4:.1f} "
            f"L {x1:.1f} {y1:.1f} "
            f"A {r_outer:.1f} {r_outer:.1f} 0 {large_arc} 1 {x2:.1f} {y2:.1f} "
            f"L {x3:.1f} {y3:.1f} "
            f"A {r_inner:.1f} {r_inner:.1f} 0 {large_arc} 0 {x4:.1f} {y4:.1f} Z"
        )
        fill_color = _SECTOR_COLORS[i % len(_SECTOR_COLORS)]
        # Highlight Jupiter's natal Ci sector
        if chart.jupiter and chart.jupiter.ci_index == i:
            fill_color = "#3d3200"
        parts.append(
            f'<path d="{path_d}" fill="{fill_color}" '
            f'stroke="#555" stroke-width="0.8" opacity="0.85"/>'
        )

        # Ci name label (outer ring)
        a_mid = math.radians(-90 + i * 30 + 15)
        lx = cx + (r_outer - 18) * math.cos(a_mid)
        ly = cy + (r_outer - 18) * math.sin(a_mid)
        ci = TWELVE_CI[i]
        parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" '
            f'fill="#e0c878" font-size="11" font-weight="bold" '
            f'text-anchor="middle" dominant-baseline="central">'
            f'{ci["name_zh"]}</text>'
        )

        # Branch label (middle ring)
        bx = cx + (r_mid - 14) * math.cos(a_mid)
        by = cy + (r_mid - 14) * math.sin(a_mid)
        parts.append(
            f'<text x="{bx:.1f}" y="{by:.1f}" '
            f'fill="#aaa" font-size="9" '
            f'text-anchor="middle" dominant-baseline="central">'
            f'{ci["branch"]}</text>'
        )

    # Inner circle
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" '
        f'fill="#0d1117" stroke="#4a3f6b" stroke-width="1"/>'
    )

    # Planet glyphs
    _GLYPHS = {
        "Sun": "☉", "Moon": "☽", "Mercury": "☿",
        "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
    }

    for p in chart.planets:
        angle = math.radians(-90 + p.ci_longitude)
        px = cx + r_planet * math.cos(angle)
        py = cy + r_planet * math.sin(angle)
        glyph = _GLYPHS.get(p.name, "?")
        color = "#FFD700" if p.name == "Jupiter" else "#ccc"
        font_size = 16 if p.name == "Jupiter" else 12
        parts.append(
            f'<text x="{px:.1f}" y="{py:.1f}" '
            f'fill="{color}" font-size="{font_size}" font-weight="bold" '
            f'text-anchor="middle" dominant-baseline="central">'
            f'{glyph}</text>'
        )
        # Retrograde marker
        if p.retrograde:
            parts.append(
                f'<text x="{px + 8:.1f}" y="{py - 6:.1f}" '
                f'fill="#f66" font-size="8" '
                f'text-anchor="middle" dominant-baseline="central">℞</text>'
            )

    # Centre text
    parts.append(
        f'<text x="{cx}" y="{cy - 8}" fill="#e0c878" font-size="13" '
        f'font-weight="bold" text-anchor="middle">十二星次</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy + 8}" fill="#999" font-size="9" '
        f'text-anchor="middle">Twelve Ci</text>'
    )

    # Title line below chart
    _y = year or chart.year
    _m = month or chart.month
    _d = day or chart.day
    _h = hour or chart.hour
    _mi = minute or chart.minute
    _loc = location or chart.location_name or ""
    title_text = f"{_y}/{_m:02d}/{_d:02d} {_h:02d}:{_mi:02d}"
    if _loc:
        title_text += f" · {_loc}"

    parts.append(
        f'<text x="{cx}" y="{size - 4}" fill="#888" font-size="9" '
        f'text-anchor="middle">{title_text}</text>'
    )

    parts.append("</svg></div>")
    return "\n".join(parts)


# ============================================================
# Streamlit 渲染函數
# ============================================================

def render_twelve_ci_chart(
    chart: TwelveCiChart,
    after_chart_hook=None,
):
    """Render Twelve Ci chart details in Streamlit.

    Parameters
    ----------
    chart : TwelveCiChart
    after_chart_hook : callable, optional
        Called after the SVG is rendered (used for AI button injection).
    """
    st.subheader(t("twelve_ci_chart_title"))

    # ── SVG wheel ────────────────────────────────────────────
    svg = build_twelve_ci_svg(chart)
    st.markdown(svg, unsafe_allow_html=True)

    if after_chart_hook:
        after_chart_hook()

    st.divider()

    # ── Jupiter natal detail ──────────────────────────────────
    if chart.jupiter and chart.jupiter_ci:
        jup = chart.jupiter
        ci = chart.jupiter_ci
        st.markdown(f"### 🪐 {t('twelve_ci_natal_jupiter')}")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(t("twelve_ci_ci_name"), f"{ci['name_zh']} ({ci['name_en']})")
        with c2:
            st.metric(t("twelve_ci_branch"), ci["branch"])
        with c3:
            st.metric(t("twelve_ci_mansions"), ci["mansions"])

        c4, c5 = st.columns(2)
        with c4:
            st.metric(t("twelve_ci_fenye"), ci["fenye"])
        with c5:
            retro_str = " ℞" if jup.retrograde else ""
            st.metric(
                t("twelve_ci_jupiter_degree"),
                f"{jup.degree_in_ci:.2f}° ({ci['name_zh']}){retro_str}",
            )

        lang = get_lang()
        interp_key = "interpretation_zh" if lang == "zh" else "interpretation_en"
        st.info(ci[interp_key])

    st.divider()

    # ── All planets table ─────────────────────────────────────
    st.markdown(f"### 🌟 {t('twelve_ci_planet_table')}")
    rows = []
    for p in chart.planets:
        ci_info = TWELVE_CI[p.ci_index]
        retro = " ℞" if p.retrograde else ""
        rows.append({
            t("twelve_ci_col_planet"): f"{p.name_zh} ({p.name})",
            t("twelve_ci_col_ci"): ci_info["name_zh"],
            t("twelve_ci_col_branch"): ci_info["branch"],
            t("twelve_ci_col_degree"): f"{p.degree_in_ci:.2f}°{retro}",
            t("twelve_ci_col_mansions"): ci_info["mansions"],
            t("twelve_ci_col_fenye"): ci_info["fenye"],
        })
    st.table(rows)

    st.divider()

    # ── Transit Jupiter (流年木星) ─────────────────────────────
    st.markdown(f"### 🔄 {t('twelve_ci_transit_title')}")
    if chart.transit_jupiter and chart.transit_jupiter_ci:
        tj = chart.transit_jupiter
        tc = chart.transit_jupiter_ci
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(t("twelve_ci_transit_ci"), f"{tc['name_zh']} ({tc['name_en']})")
        with c2:
            retro_str = " ℞" if tj.retrograde else ""
            st.metric(t("twelve_ci_transit_degree"), f"{tj.degree_in_ci:.2f}°{retro_str}")
        with c3:
            st.metric(t("twelve_ci_transit_branch"), tc["branch"])

        lang = get_lang()
        interp_key = "interpretation_zh" if lang == "zh" else "interpretation_en"
        st.success(tc[interp_key])

    st.divider()

    # ── Twelve Ci reference table ─────────────────────────────
    with st.expander(t("twelve_ci_reference_title"), expanded=False):
        ref_rows = []
        for ci in TWELVE_CI:
            ref_rows.append({
                t("twelve_ci_col_ci"): ci["name_zh"],
                "English": ci["name_en"],
                t("twelve_ci_col_range"): ci["range"],
                t("twelve_ci_col_branch"): ci["branch"],
                t("twelve_ci_col_mansions"): ci["mansions"],
                t("twelve_ci_col_fenye"): ci["fenye"],
                t("twelve_ci_col_solar"): ci["solar_approx"],
            })
        st.table(ref_rows)


# ============================================================
# AI prompt formatter — for ai_analysis.py integration
# ============================================================

def format_twelve_ci_chart(chart: TwelveCiChart) -> str:
    """Format a TwelveCiChart into text for AI analysis prompts."""
    lines = ["=== 十二星次排盤 (Twelve Ci Chart) ==="]
    lines.append(
        f"出生時間: {chart.year}/{chart.month:02d}/{chart.day:02d} "
        f"{chart.hour:02d}:{chart.minute:02d} (UTC{chart.timezone:+.1f})"
    )
    if chart.location_name:
        lines.append(f"地點: {chart.location_name}")
    lines.append(f"經緯度: {chart.latitude:.4f}, {chart.longitude:.4f}")
    lines.append("")

    if chart.jupiter and chart.jupiter_ci:
        jup = chart.jupiter
        ci = chart.jupiter_ci
        lines.append("【本命木星星次】")
        lines.append(f"  星次: {ci['name_zh']} ({ci['name_en']})")
        lines.append(f"  地支: {ci['branch']}")
        lines.append(f"  二十八宿: {ci['mansions']}")
        lines.append(f"  分野: {ci['fenye']}")
        retro = "（逆行）" if jup.retrograde else ""
        lines.append(f"  木星度數: {jup.degree_in_ci:.2f}° {retro}")
        lines.append(f"  星次含義: {ci['interpretation_zh']}")
        lines.append("")

    lines.append("【全部行星星次位置】")
    for p in chart.planets:
        ci_info = TWELVE_CI[p.ci_index]
        retro = " ℞" if p.retrograde else ""
        lines.append(
            f"  {p.name_zh}({p.name}): {ci_info['name_zh']} "
            f"{p.degree_in_ci:.2f}°{retro} | "
            f"地支={ci_info['branch']} 宿={ci_info['mansions']}"
        )
    lines.append("")

    if chart.transit_jupiter and chart.transit_jupiter_ci:
        tj = chart.transit_jupiter
        tc = chart.transit_jupiter_ci
        retro = "（逆行）" if tj.retrograde else ""
        lines.append("【流年木星（當前行運）】")
        lines.append(f"  星次: {tc['name_zh']} ({tc['name_en']})")
        lines.append(f"  度數: {tj.degree_in_ci:.2f}° {retro}")
        lines.append(f"  分野: {tc['fenye']}")
        lines.append(f"  含義: {tc['interpretation_zh']}")

    return "\n".join(lines)
