"""
卡巴拉占星排盤模組 (Kabbalistic Astrology Chart Module)

卡巴拉占星以猶太神祕主義（Kabbalah）為基礎，結合生命之樹（Tree of Life）
十質點（Sephiroth）與行星對應、希伯來字母與黃道星座對應、塔羅牌路徑等，
使用回歸黃道（tropical zodiac）搭配 pyswisseph 計算行星位置。
"""

import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

# ============================================================
# 常量 (Constants)
# ============================================================

# Planets used in Kabbalistic astrology (tropical, same IDs as Western)
KABBALISTIC_PLANETS = {
    "Sun ☉ (太陽)": swe.SUN,
    "Moon ☽ (月亮)": swe.MOON,
    "Mercury ☿ (水星)": swe.MERCURY,
    "Venus ♀ (金星)": swe.VENUS,
    "Mars ♂ (火星)": swe.MARS,
    "Jupiter ♃ (木星)": swe.JUPITER,
    "Saturn ♄ (土星)": swe.SATURN,
    "Uranus ♅ (天王星)": swe.URANUS,
    "Neptune ♆ (海王星)": swe.NEPTUNE,
    "Pluto ♇ (冥王星)": swe.PLUTO,
}

# 12 Zodiac signs with Hebrew letter correspondences (Golden Dawn tradition)
# (English name, glyph, Chinese name, element, Hebrew letter, Tarot Major Arcana)
ZODIAC_SIGNS = [
    ("Aries", "♈", "白羊座", "Fire 火", "ה (Heh)", "The Emperor 皇帝"),
    ("Taurus", "♉", "金牛座", "Earth 土", "ו (Vav)", "The Hierophant 教皇"),
    ("Gemini", "♊", "雙子座", "Air 風", "ז (Zayin)", "The Lovers 戀人"),
    ("Cancer", "♋", "巨蟹座", "Water 水", "ח (Cheth)", "The Chariot 戰車"),
    ("Leo", "♌", "獅子座", "Fire 火", "ט (Teth)", "Strength 力量"),
    ("Virgo", "♍", "處女座", "Earth 土", "י (Yod)", "The Hermit 隱者"),
    ("Libra", "♎", "天秤座", "Air 風", "ל (Lamed)", "Justice 正義"),
    ("Scorpio", "♏", "天蠍座", "Water 水", "נ (Nun)", "Death 死神"),
    ("Sagittarius", "♐", "射手座", "Fire 火", "ס (Samekh)", "Temperance 節制"),
    ("Capricorn", "♑", "摩羯座", "Earth 土", "ע (Ayin)", "The Devil 惡魔"),
    ("Aquarius", "♒", "水瓶座", "Air 風", "צ (Tzaddi)", "The Star 星星"),
    ("Pisces", "♓", "雙魚座", "Water 水", "ק (Qoph)", "The Moon 月亮"),
]

# Sephiroth (10 emanations on the Tree of Life) with planetary correspondences
# (Hebrew name, transliteration, Chinese name, meaning, ruling planet)
SEPHIROTH = [
    ("כתר", "Keter", "王冠", "Crown", "Neptune ♆"),
    ("חכמה", "Chokmah", "智慧", "Wisdom", "Uranus ♅"),
    ("בינה", "Binah", "理解", "Understanding", "Saturn ♄"),
    ("חסד", "Chesed", "慈悲", "Mercy", "Jupiter ♃"),
    ("גבורה", "Gevurah", "嚴厲", "Severity", "Mars ♂"),
    ("תפארת", "Tiferet", "美麗", "Beauty", "Sun ☉"),
    ("נצח", "Netzach", "勝利", "Victory", "Venus ♀"),
    ("הוד", "Hod", "榮耀", "Splendor", "Mercury ☿"),
    ("יסוד", "Yesod", "基礎", "Foundation", "Moon ☽"),
    ("מלכות", "Malkuth", "王國", "Kingdom", "Earth 🜨"),
]

# Map planet names to their Sephirah index (0-based)
PLANET_SEPHIRAH = {
    "Sun ☉ (太陽)": 5,       # Tiferet
    "Moon ☽ (月亮)": 8,      # Yesod
    "Mercury ☿ (水星)": 7,   # Hod
    "Venus ♀ (金星)": 6,     # Netzach
    "Mars ♂ (火星)": 4,      # Gevurah
    "Jupiter ♃ (木星)": 3,   # Chesed
    "Saturn ♄ (土星)": 2,    # Binah
    "Uranus ♅ (天王星)": 1,  # Chokmah
    "Neptune ♆ (海王星)": 0,  # Keter
    "Pluto ♇ (冥王星)": None,  # Da'at (not a Sephirah)
    "North Node ☊ (北交點)": None,
}

# Hebrew double letters for planets (Sefer Yetzirah tradition)
PLANET_HEBREW_LETTER = {
    "Sun ☉ (太陽)": "כ (Kaph)",
    "Moon ☽ (月亮)": "ת (Tav)",
    "Mercury ☿ (水星)": "ר (Resh)",
    "Venus ♀ (金星)": "פ (Pe)",
    "Mars ♂ (火星)": "ד (Dalet)",
    "Jupiter ♃ (木星)": "ג (Gimel)",
    "Saturn ♄ (土星)": "ב (Bet)",
    "Uranus ♅ (天王星)": "—",
    "Neptune ♆ (海王星)": "—",
    "Pluto ♇ (冥王星)": "—",
    "North Node ☊ (北交點)": "—",
}

PLANET_COLORS = {
    "Sun ☉ (太陽)": "#FFD700",
    "Moon ☽ (月亮)": "#C0C0C0",
    "Mercury ☿ (水星)": "#FFA500",
    "Venus ♀ (金星)": "#228B22",
    "Mars ♂ (火星)": "#DC143C",
    "Jupiter ♃ (木星)": "#4169E1",
    "Saturn ♄ (土星)": "#000080",
    "Uranus ♅ (天王星)": "#00CED1",
    "Neptune ♆ (海王星)": "#7B68EE",
    "Pluto ♇ (冥王星)": "#800080",
    "North Node ☊ (北交點)": "#556B2F",
}


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class KabbalisticPlanet:
    """Kabbalistic planet position with Tree of Life correspondences"""
    name: str
    longitude: float
    latitude: float
    sign: str
    sign_glyph: str
    sign_chinese: str
    element: str
    sign_degree: float
    retrograde: bool
    hebrew_letter_sign: str   # Hebrew letter of the zodiac sign
    tarot: str                # Tarot Major Arcana of the sign
    sephirah: str             # Corresponding Sephirah name
    hebrew_letter_planet: str  # Hebrew double letter of the planet
    house: int = 0


@dataclass
class KabbalisticHouse:
    """Kabbalistic house data"""
    number: int
    cusp: float
    sign: str
    sign_glyph: str
    planets: list = field(default_factory=list)


@dataclass
class KabbalisticChart:
    """Kabbalistic astrology chart"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    julian_day: float
    planets: list
    houses: list
    ascendant: float
    midheaven: float
    asc_sign: str
    mc_sign: str


# ============================================================
# 計算函數 (Calculation Functions)
# ============================================================

def _normalize(deg):
    return deg % 360.0


def _sign_index(deg):
    return int(_normalize(deg) / 30.0)


def _sign_degree(deg):
    return _normalize(deg) % 30.0


def _format_deg(deg):
    deg = _normalize(deg)
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""


def _find_house(lon, cusps):
    lon = _normalize(lon)
    for i in range(12):
        start = _normalize(cusps[i])
        end = _normalize(cusps[(i + 1) % 12])
        if start < end:
            if start <= lon < end:
                return i + 1
        else:
            if lon >= start or lon < end:
                return i + 1
    return 1


@st.cache_data(ttl=3600, show_spinner=False)
def compute_kabbalistic_chart(year, month, day, hour, minute, timezone,
                              latitude, longitude, location_name=""):
    """計算卡巴拉占星排盤 (Tropical Zodiac, Placidus Houses)"""
    swe.set_ephe_path("")

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")
    ascendant = ascmc[0]
    midheaven = ascmc[1]

    planets = []
    for name, planet_id in KABBALISTIC_PLANETS.items():
        result, _ = swe.calc_ut(jd, planet_id)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        sign_info = ZODIAC_SIGNS[idx]

        seph_idx = PLANET_SEPHIRAH.get(name)
        sephirah_name = (
            f"{SEPHIROTH[seph_idx][1]} {SEPHIROTH[seph_idx][0]} "
            f"({SEPHIROTH[seph_idx][2]})"
            if seph_idx is not None
            else "Da'at דעת (知識)"
        )

        planets.append(KabbalisticPlanet(
            name=name,
            longitude=lon,
            latitude=lat,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            sign_chinese=sign_info[2],
            element=sign_info[3],
            sign_degree=_sign_degree(lon),
            retrograde=speed < 0,
            hebrew_letter_sign=sign_info[4],
            tarot=sign_info[5],
            sephirah=sephirah_name,
            hebrew_letter_planet=PLANET_HEBREW_LETTER.get(name, "—"),
        ))

    # North Node (Rahu)
    rahu, _ = swe.calc_ut(jd, swe.MEAN_NODE)
    rahu_lon = _normalize(rahu[0])
    idx = _sign_index(rahu_lon)
    sign_info = ZODIAC_SIGNS[idx]
    node_name = "North Node ☊ (北交點)"
    planets.append(KabbalisticPlanet(
        name=node_name,
        longitude=rahu_lon,
        latitude=rahu[1],
        sign=sign_info[0],
        sign_glyph=sign_info[1],
        sign_chinese=sign_info[2],
        element=sign_info[3],
        sign_degree=_sign_degree(rahu_lon),
        retrograde=False,
        hebrew_letter_sign=sign_info[4],
        tarot=sign_info[5],
        sephirah="Da'at דעת (知識)",
        hebrew_letter_planet=PLANET_HEBREW_LETTER.get(node_name, "—"),
    ))

    # Build houses
    houses = []
    for i in range(12):
        cusp = cusps[i]
        idx = _sign_index(cusp)
        sign_info = ZODIAC_SIGNS[idx]
        houses.append(KabbalisticHouse(
            number=i + 1,
            cusp=cusp,
            sign=sign_info[0],
            sign_glyph=sign_info[1],
            planets=[],
        ))

    for p in planets:
        h = _find_house(p.longitude, cusps)
        p.house = h
        houses[h - 1].planets.append(p.name)

    asc_idx = _sign_index(ascendant)
    mc_idx = _sign_index(midheaven)

    return KabbalisticChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd,
        planets=planets, houses=houses,
        ascendant=ascendant, midheaven=midheaven,
        asc_sign=ZODIAC_SIGNS[asc_idx][0],
        mc_sign=ZODIAC_SIGNS[mc_idx][0],
    )


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_kabbalistic_chart(chart, after_chart_hook=None):
    """渲染完整的卡巴拉占星排盤"""
    _render_tree_of_life(chart)
    if after_chart_hook:
        after_chart_hook()
    st.divider()
    _render_info(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_house_table(chart)


def _render_info(chart):
    st.subheader("📋 排盤資訊 (Chart Information)")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**日期 (Date):** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**時間 (Time):** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**時區 (Timezone):** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**地點 (Location):** {chart.location_name}")
        asc_info = ZODIAC_SIGNS[_sign_index(chart.ascendant)]
        mc_info = ZODIAC_SIGNS[_sign_index(chart.midheaven)]
        st.write(
            f"**上升點 (Ascendant):** {chart.asc_sign} "
            f"{_format_deg(chart.ascendant)} — "
            f"希伯來字母 {asc_info[4]}"
        )
        st.write(
            f"**天頂 (Midheaven):** {chart.mc_sign} "
            f"{_format_deg(chart.midheaven)} — "
            f"希伯來字母 {mc_info[4]}"
        )


def _render_tree_of_life(chart):
    """渲染生命之樹（Tree of Life）行星對應圖"""
    st.subheader("🕎 生命之樹 (Tree of Life)")

    # Build planet lookup by Sephirah index
    seph_planets = {i: [] for i in range(10)}
    for p in chart.planets:
        idx = PLANET_SEPHIRAH.get(p.name)
        if idx is not None:
            short_name = p.name.split(" (")[0]
            color = PLANET_COLORS.get(p.name, "#c8c8c8")
            seph_planets[idx].append(
                f'<span style="color:{color};font-weight:bold">'
                f'{short_name}</span> '
                f'{p.sign_glyph} {p.sign_degree:.1f}°'
            )

    def _seph_cell(idx):
        s = SEPHIROTH[idx]
        planet_html = "<br/>".join(seph_planets[idx]) if seph_planets[idx] else ""
        return (
            f'<td class="tol-seph">'
            f'<b>{s[1]}</b><br/>'
            f'<span class="tol-hebrew">{s[0]}</span><br/>'
            f'<small class="tol-meaning">{s[2]} ({s[3]})</small><br/>'
            f'{planet_html}'
            f'</td>'
        )

    spacer = '<td class="tol-spacer"></td>'

    # Responsive CSS
    css = """<style>
.tol-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%}
.tol-table{border-collapse:separate;border-spacing:6px;margin:auto;width:100%;min-width:0;table-layout:fixed}
.tol-seph{border:2px solid #9370DB;padding:8px;text-align:center;vertical-align:top;
  background:#1a0d2e;border-radius:8px;color:#e0d0ff;font-size:14px;word-break:break-word}
.tol-hebrew{font-size:16px;color:#c8b8f0}
.tol-meaning{color:#a090c0}
.tol-spacer{border:none;width:5%;padding:0}
.tol-empty{border:none;padding:0}

@media(max-width:600px){
  .tol-table{border-spacing:3px}
  .tol-seph{padding:4px;font-size:11px;border-radius:5px}
  .tol-hebrew{font-size:13px}
  .tol-meaning{font-size:10px}
  .tol-spacer{width:2%}
}
@media(min-width:601px) and (max-width:900px){
  .tol-table{border-spacing:4px}
  .tol-seph{padding:6px;font-size:13px;border-radius:6px}
  .tol-hebrew{font-size:15px}
}
</style>"""

    html = css
    html += '<div class="tol-wrap">'
    html += '<table class="tol-table">'

    # Row 1: Keter (centered)
    html += (
        f'<tr><td class="tol-empty"></td>{spacer}'
        f'{_seph_cell(0)}'
        f'{spacer}<td class="tol-empty"></td></tr>'
    )

    # Row 2: Binah — Chokmah
    html += (
        f'<tr>{_seph_cell(2)}{spacer}'
        f'<td class="tol-empty"></td>'
        f'{spacer}{_seph_cell(1)}</tr>'
    )

    # Row 3: Gevurah — Chesed
    html += (
        f'<tr>{_seph_cell(4)}{spacer}'
        f'<td class="tol-empty"></td>'
        f'{spacer}{_seph_cell(3)}</tr>'
    )

    # Row 4: Tiferet (centered)
    html += (
        f'<tr><td class="tol-empty"></td>{spacer}'
        f'{_seph_cell(5)}'
        f'{spacer}<td class="tol-empty"></td></tr>'
    )

    # Row 5: Hod — Netzach
    html += (
        f'<tr>{_seph_cell(7)}{spacer}'
        f'<td class="tol-empty"></td>'
        f'{spacer}{_seph_cell(6)}</tr>'
    )

    # Row 6: Yesod (centered)
    html += (
        f'<tr><td class="tol-empty"></td>{spacer}'
        f'{_seph_cell(8)}'
        f'{spacer}<td class="tol-empty"></td></tr>'
    )

    # Row 7: Malkuth (centered)
    html += (
        f'<tr><td class="tol-empty"></td>{spacer}'
        f'{_seph_cell(9)}'
        f'{spacer}<td class="tol-empty"></td></tr>'
    )

    html += '</table></div>'
    st.markdown(html, unsafe_allow_html=True)


def _render_planet_table(chart):
    st.subheader("🪐 行星位置與卡巴拉對應 (Planet Positions & Kabbalistic Correspondences)")
    header = (
        "| 行星 (Planet) | 星座 (Sign) | 度數 (Degree) | 元素 (Element) "
        "| 宮位 (House) | 質點 (Sephirah) | 希伯來字母 (Hebrew) | 塔羅 (Tarot) | ℞ |"
    )
    sep = (
        "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    )
    rows = [header, sep]
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = (
            f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        )
        rows.append(
            f"| {name_html} "
            f"| {p.sign_glyph} {p.sign} ({p.sign_chinese}) "
            f"| {p.sign_degree:.2f}° "
            f"| {p.element} "
            f"| {p.house} "
            f"| {p.sephirah} "
            f"| {p.hebrew_letter_planet} "
            f"| {p.tarot} "
            f"| {retro} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_house_table(chart):
    st.subheader("🏛️ 宮位 (House Cusps)")
    header = (
        "| 宮位 (House) | 宮頭 (Cusp) | 星座 (Sign) "
        "| 希伯來字母 (Hebrew) | 塔羅 (Tarot) | 行星 (Planets) |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    for h in chart.houses:
        idx = _sign_index(h.cusp)
        sign_info = ZODIAC_SIGNS[idx]
        planets_str = ", ".join(h.planets) if h.planets else "—"
        rows.append(
            f"| {h.number} "
            f"| {_format_deg(h.cusp)} "
            f"| {h.sign_glyph} {h.sign} "
            f"| {sign_info[4]} "
            f"| {sign_info[5]} "
            f"| {planets_str} |"
        )
    st.markdown("\n".join(rows))
