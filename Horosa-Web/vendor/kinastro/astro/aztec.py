"""
阿茲特克占星排盤模組 (Aztec Astrology Chart Module)

阿茲特克占星以中美洲阿茲特克文明的天文與曆法傳統為基礎，核心為：
- Tonalpohualli（神聖曆）：260天循環，20 個日徵（day signs）× 13 個數字
  結構與瑪雅 Tzolkin 高度相似，但使用 Nahuatl（納瓦特爾語）命名系統
- 每個日徵對應特定的守護神祇、方位與顏色
- Trecena：13天為一個週期，每個 Trecena 由第一天的日徵命名
- 與西洋行星位置做跨體系疊加比較

Tonalpohualli 計算公式：
  days_since_epoch = jd - AZTEC_EPOCH_JD
  number = (days_since_epoch % 13) + 1        → 1-13
  sign_index = days_since_epoch % 20           → 0-19

參考：https://www.azteccalendar.com/

使用 pyswisseph 計算行星位置。
"""

import swisseph as swe
import streamlit as st
from dataclasses import dataclass, field

# ============================================================
# 常量 (Constants)
# ============================================================

# GMT correlation: 與瑪雅長紀年使用相同的 GMT correlation constant
# Tonalpohualli 與 Tzolkin 高度重疊，共享同一 epoch Julian Day
AZTEC_EPOCH_JD = 584283.0  # Julian Day of Aztec/Mayan epoch

# Tonalpohualli (Sacred Calendar) - 20 day signs (日徵)
# 格式：(序號字串, Nahuatl 名稱, 中文名稱, 英文名稱)
AZTEC_TONALPOHUALLI_SIGNS = [
    ("0",  "Cipactli",      "鱷魚 / 鱷魚怪",   "Crocodile"),
    ("1",  "Ehēcatl",       "風",               "Wind"),
    ("2",  "Calli",         "房屋",             "House"),
    ("3",  "Cuetzpalin",    "蜥蜴",             "Lizard"),
    ("4",  "Cōātl",         "蛇",               "Snake"),
    ("5",  "Miquiztli",     "死亡",             "Death"),
    ("6",  "Mazātl",        "鹿",               "Deer"),
    ("7",  "Tōchtli",       "兔子",             "Rabbit"),
    ("8",  "Ātl",           "水",               "Water"),
    ("9",  "Itzcuintli",    "狗",               "Dog"),
    ("10", "Ozomatli",      "猴子",             "Monkey"),
    ("11", "Malinalli",     "草",               "Grass"),
    ("12", "Ācatl",         "蘆葦",             "Reed"),
    ("13", "Ocelotl",       "美洲豹",           "Jaguar"),
    ("14", "Cuāuhtli",      "老鷹",             "Eagle"),
    ("15", "Cozcacuauhtli", "禿鷲",             "Vulture"),
    ("16", "Ollin",         "地震 / 運動",      "Movement"),
    ("17", "Tecpatl",       "燧石刀",           "Flint"),
    ("18", "Quiahuitl",     "雨",               "Rain"),
    ("19", "Xōchitl",       "花",               "Flower"),
]

# 日徵表情符號（用於視覺化展示）
AZTEC_SIGN_GLYPHS = {
    0:  "🐊",   # Cipactli  - 鱷魚
    1:  "🌀",   # Ehēcatl   - 風
    2:  "🏠",   # Calli     - 房屋
    3:  "🦎",   # Cuetzpalin- 蜥蜴
    4:  "🐍",   # Cōātl     - 蛇
    5:  "💀",   # Miquiztli - 死亡
    6:  "🦌",   # Mazātl    - 鹿
    7:  "🐇",   # Tōchtli   - 兔子
    8:  "💧",   # Ātl       - 水
    9:  "🐕",   # Itzcuintli- 狗
    10: "🐒",   # Ozomatli  - 猴子
    11: "🌿",   # Malinalli - 草
    12: "🎋",   # Ācatl     - 蘆葦
    13: "🐆",   # Ocelotl   - 美洲豹
    14: "🦅",   # Cuāuhtli  - 老鷹
    15: "🦅",   # Cozcacuauhtli - 禿鷲
    16: "🌍",   # Ollin     - 地震/運動
    17: "🗡️",  # Tecpatl   - 燧石刀
    18: "🌧️",  # Quiahuitl - 雨
    19: "🌸",   # Xōchitl   - 花
}

# 阿茲特克行星（與瑪雅占星相同，使用西方占星行星疊加）
AZTEC_PLANETS = {
    "Sun ☉ (太陽)":     swe.SUN,
    "Moon ☽ (月亮)":    swe.MOON,
    "Venus ♀ (金星)":   swe.VENUS,
    "Mars ♂ (火星)":    swe.MARS,
    "Jupiter ♃ (木星)": swe.JUPITER,
    "Saturn ♄ (土星)":  swe.SATURN,
}

# 每個日徵對應的守護神祇 (Deities)
AZTEC_DEITIES = {
    0:  "Tonacatecuhtli（托納卡特庫特利 — 創世之主）",
    1:  "Quetzalcoatl（羽蛇神 — 風與智慧之神）",
    2:  "Tepeyollotl（特佩約洛特 — 山心之神）",
    3:  "Huehuecoyotl（老狼神 — 惡作劇之神）",
    4:  "Chalchiuhtlicue（玉裙女神 — 水與河流之神）",
    5:  "Tecciztecatl（月亮之神）",
    6:  "Tlaloc（特拉洛克 — 雨神）",
    7:  "Mayahuel（瑪雅韋爾 — 龍舌蘭女神）",
    8:  "Xiuhtecuhtli（火神）",
    9:  "Mictlantecuhtli（死亡之神 — 冥界之王）",
    10: "Xochipilli（花之王子 — 藝術與歡樂之神）",
    11: "Patecatl（帕特卡特爾 — 醫藥之神）",
    12: "Tezcatlipoca（黑曜石鏡 — 命運之神）",
    13: "Tlazolteotl（大地女神 — 淨化之神）",
    14: "Xipe Totec（剝皮之神 — 春天與重生之神）",
    15: "Itzpapalotl（黑曜蝶 — 戰士女神）",
    16: "Xolotl（索洛特 — 黃昏之神、雙胞胎）",
    17: "Tezcatlipoca（黑曜石鏡 — 命運之神）",
    18: "Tonatiuh（托納提烏 — 太陽神）",
    19: "Xochiquetzal（花羽女神 — 愛與美之神）",
}

# 四方位與顏色 (Directions & Colors)
# 阿茲特克宇宙觀中，20個日徵分為四個方位，每五個日徵一組
AZTEC_DIRECTIONS = {
    0:  ("East",  "東方", "Red",    "紅色",  "#DC143C"),   # Cipactli
    1:  ("North", "北方", "White",  "白色",  "#FFFFFF"),   # Ehēcatl
    2:  ("West",  "西方", "Blue",   "藍色",  "#4169E1"),   # Calli
    3:  ("South", "南方", "Yellow", "黃色",  "#FFD700"),   # Cuetzpalin
    4:  ("East",  "東方", "Red",    "紅色",  "#DC143C"),   # Cōātl
    5:  ("North", "北方", "White",  "白色",  "#FFFFFF"),   # Miquiztli
    6:  ("West",  "西方", "Blue",   "藍色",  "#4169E1"),   # Mazātl
    7:  ("South", "南方", "Yellow", "黃色",  "#FFD700"),   # Tōchtli
    8:  ("East",  "東方", "Red",    "紅色",  "#DC143C"),   # Ātl
    9:  ("North", "北方", "White",  "白色",  "#FFFFFF"),   # Itzcuintli
    10: ("West",  "西方", "Blue",   "藍色",  "#4169E1"),   # Ozomatli
    11: ("South", "南方", "Yellow", "黃色",  "#FFD700"),   # Malinalli
    12: ("East",  "東方", "Red",    "紅色",  "#DC143C"),   # Ācatl
    13: ("North", "北方", "White",  "白色",  "#FFFFFF"),   # Ocelotl
    14: ("West",  "西方", "Blue",   "藍色",  "#4169E1"),   # Cuāuhtli
    15: ("South", "南方", "Yellow", "黃色",  "#FFD700"),   # Cozcacuauhtli
    16: ("East",  "東方", "Red",    "紅色",  "#DC143C"),   # Ollin
    17: ("North", "北方", "White",  "白色",  "#FFFFFF"),   # Tecpatl
    18: ("West",  "西方", "Blue",   "藍色",  "#4169E1"),   # Quiahuitl
    19: ("South", "南方", "Yellow", "黃色",  "#FFD700"),   # Xōchitl
}

# 每個日徵的能量描述 (Energies)
AZTEC_ENERGIES = {
    0:  "創始 / 原初能量 / 大地之母",
    1:  "風 / 變化 / 靈性溝通",
    2:  "家庭 / 安全 / 內在反省",
    3:  "敏捷 / 適應 / 生存力",
    4:  "蛇 / 生命力 / 蛻變",
    5:  "死亡 / 轉化 / 祖先連結",
    6:  "優雅 / 直覺 / 自然和諧",
    7:  "豐盛 / 生育 / 月亮力量",
    8:  "情緒 / 淨化 / 流動",
    9:  "忠誠 / 引導 / 冥界嚮導",
    10: "創造 / 遊戲 / 藝術靈感",
    11: "堅韌 / 苦難中成長 / 治癒",
    12: "權威 / 正義 / 命運之箭",
    13: "神秘 / 力量 / 大地之心",
    14: "視野 / 自由 / 戰士精神",
    15: "智慧 / 長者 / 淨化業力",
    16: "運動 / 催化 / 宇宙平衡",
    17: "犧牲 / 純粹 / 真理之刃",
    18: "風暴 / 淨化 / 重生力量",
    19: "美 / 愛 / 花之靈性",
}

# 行星顏色（視覺化用）
AZTEC_PLANET_COLORS = {
    "Sun ☉ (太陽)":     "#FFD700",
    "Moon ☽ (月亮)":    "#C0C0C0",
    "Venus ♀ (金星)":   "#228B22",
    "Mars ♂ (火星)":    "#DC143C",
    "Jupiter ♃ (木星)": "#4169E1",
    "Saturn ♄ (土星)":  "#000080",
}

# 12 Zodiac signs (tropical) for planetary overlay
ZODIAC_SIGNS = [
    ("Aries",      "♈", "白羊座"),
    ("Taurus",     "♉", "金牛座"),
    ("Gemini",     "♊", "雙子座"),
    ("Cancer",     "♋", "巨蟹座"),
    ("Leo",        "♌", "獅子座"),
    ("Virgo",      "♍", "處女座"),
    ("Libra",      "♎", "天秤座"),
    ("Scorpio",    "♏", "天蠍座"),
    ("Sagittarius","♐", "射手座"),
    ("Capricorn",  "♑", "摩羯座"),
    ("Aquarius",   "♒", "水瓶座"),
    ("Pisces",     "♓", "雙魚座"),
]


# ============================================================
# 資料類 (Data Classes)
# ============================================================

@dataclass
class AztecPlanet:
    """行星位置資料（帶阿茲特克日徵對應）"""
    name: str
    longitude: float
    latitude: float
    sign: str            # Western zodiac sign
    sign_glyph: str
    sign_chinese: str
    sign_degree: float
    retrograde: bool
    aztec_day_lord: int   # Tonalpohualli sign index for this day
    aztec_energy: str     # Tonalpohualli energy description


@dataclass
class AztecChart:
    """阿茲特克占星排盤結果"""
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

    # Tonalpohualli（神聖曆）
    tonalpohualli_number: int     # 1-13
    tonalpohualli_sign_name: str  # Nahuatl name
    tonalpohualli_sign_cn: str    # 中文名稱
    tonalpohualli_sign_en: str    # English name
    tonalpohualli_glyph: str      # Emoji glyph
    tonalpohualli_energy: str     # 能量描述

    # Trecena（13天週期）
    trecena_number: int           # 此日在 Trecena 中的位置 (1-13)
    trecena_ruler_name: str       # Trecena 主宰日徵 (Nahuatl)
    trecena_ruler_cn: str         # Trecena 主宰日徵 (中文)

    # 守護神祇
    deity: str

    # 方位與顏色
    direction_en: str
    direction_cn: str
    color_en: str
    color_cn: str
    color_hex: str

    # Planetary positions
    planets: list


# ============================================================
# 輔助函數 (Helper Functions)
# ============================================================

def _normalize(deg):
    """將角度正規化到 0-360 範圍"""
    return deg % 360.0


def _sign_index(deg):
    """根據經度計算黃道星座索引（0-11）"""
    return int(_normalize(deg) / 30.0)


def _sign_degree(deg):
    """計算在星座內的度數（0-30）"""
    return _normalize(deg) % 30.0


def _format_deg(deg):
    """將角度格式化為度分秒字串"""
    deg = _normalize(deg)
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""


def get_tonalpohualli(jd):
    """
    計算 Tonalpohualli 日期（基於 GMT correlation）

    參數:
        jd: Julian Day 數值

    回傳:
        (number, sign_info) — number 為 1-13，sign_info 為 AZTEC_TONALPOHUALLI_SIGNS 中的 tuple
    """
    days_since_epoch = int(jd - AZTEC_EPOCH_JD)
    number = (days_since_epoch % 13) + 1        # 1-13
    sign_index = days_since_epoch % 20           # 0-19
    sign_info = AZTEC_TONALPOHUALLI_SIGNS[sign_index]
    return number, sign_info


def get_trecena(jd):
    """
    計算 Trecena（13天週期）資訊

    每個 Trecena 由其第一天的日徵命名。
    回傳:
        (position_in_trecena, ruler_sign_info) — position 為 1-13
    """
    days_since_epoch = int(jd - AZTEC_EPOCH_JD)
    # Trecena 中的位置 = number (1-13)
    position = (days_since_epoch % 13) + 1
    # Trecena 主宰日徵：回溯到此 Trecena 第一天的日徵
    trecena_start_day = days_since_epoch - (position - 1)
    ruler_index = trecena_start_day % 20
    ruler_info = AZTEC_TONALPOHUALLI_SIGNS[ruler_index]
    return position, ruler_info


def get_day_sign_meaning(sign_index):
    """
    取得日徵的能量描述

    參數:
        sign_index: 0-19 的日徵索引

    回傳:
        能量描述字串
    """
    return AZTEC_ENERGIES.get(sign_index, "")


def get_associated_deity(sign_index):
    """
    取得日徵對應的守護神祇

    參數:
        sign_index: 0-19 的日徵索引

    回傳:
        神祇名稱與描述字串
    """
    return AZTEC_DEITIES.get(sign_index, "")


def get_direction_color(sign_index):
    """
    取得日徵對應的方位與顏色

    參數:
        sign_index: 0-19 的日徵索引

    回傳:
        (direction_en, direction_cn, color_en, color_cn, color_hex) 元組
    """
    return AZTEC_DIRECTIONS.get(sign_index, ("", "", "", "", ""))


# ============================================================
# 計算函數 (Calculation Functions)
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_aztec_chart(year, month, day, hour, minute,
                        timezone, latitude, longitude, location_name=""):
    """
    計算阿茲特克占星排盤

    參數:
        year, month, day: 公曆出生日期
        hour, minute: 出生時間
        timezone: 時區（UTC 偏移量）
        latitude, longitude: 出生地點經緯度
        location_name: 地點名稱

    回傳:
        AztecChart 資料物件
    """
    swe.set_ephe_path("")

    # 計算 Julian Day
    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)

    # Tonalpohualli（神聖曆）計算
    days_since_epoch = int(jd - AZTEC_EPOCH_JD)
    tonalpohualli_number, sign_info = get_tonalpohualli(jd)
    sign_index = days_since_epoch % 20

    # Trecena（13天週期）
    trecena_position, trecena_ruler = get_trecena(jd)

    # 守護神祇
    deity = get_associated_deity(sign_index)

    # 方位與顏色
    dir_en, dir_cn, col_en, col_cn, col_hex = get_direction_color(sign_index)

    # 能量描述
    energy = get_day_sign_meaning(sign_index)

    # 日徵符號
    glyph = AZTEC_SIGN_GLYPHS.get(sign_index, "")

    # 宮位計算（用於行星位置）
    cusps, ascmc = swe.houses(jd, latitude, longitude, b"P")

    # 行星位置計算
    planets = []
    for name, planet_id in AZTEC_PLANETS.items():
        result, _ = swe.calc_ut(jd, planet_id)
        lon = _normalize(result[0])
        lat = result[1]
        speed = result[3]
        idx = _sign_index(lon)
        zodiac_info = ZODIAC_SIGNS[idx]

        # 此行星對應的 Tonalpohualli 日徵
        # 使用與 maya.py 相同的疊加方式：基礎日徵 + 行星經度映射到 20 日徵的偏移量
        # lon/360*20 將 0-360° 經度均勻映射到 0-19 的日徵偏移
        aztec_day_for_planet = int(jd - AZTEC_EPOCH_JD + int(lon / 360 * 20)) % 20
        aztec_energy = AZTEC_ENERGIES.get(aztec_day_for_planet, "")

        planets.append(AztecPlanet(
            name=name,
            longitude=lon,
            latitude=lat,
            sign=zodiac_info[0],
            sign_glyph=zodiac_info[1],
            sign_chinese=zodiac_info[2],
            sign_degree=_sign_degree(lon),
            retrograde=speed < 0,
            aztec_day_lord=aztec_day_for_planet,
            aztec_energy=aztec_energy,
        ))

    return AztecChart(
        year=year, month=month, day=day, hour=hour, minute=minute,
        timezone=timezone, latitude=latitude, longitude=longitude,
        location_name=location_name, julian_day=jd,
        tonalpohualli_number=tonalpohualli_number,
        tonalpohualli_sign_name=sign_info[1],
        tonalpohualli_sign_cn=sign_info[2],
        tonalpohualli_sign_en=sign_info[3],
        tonalpohualli_glyph=glyph,
        tonalpohualli_energy=energy,
        trecena_number=trecena_position,
        trecena_ruler_name=trecena_ruler[1],
        trecena_ruler_cn=trecena_ruler[2],
        deity=deity,
        direction_en=dir_en,
        direction_cn=dir_cn,
        color_en=col_en,
        color_cn=col_cn,
        color_hex=col_hex,
        planets=planets,
    )


# ============================================================
# 渲染函數 (Rendering Functions)
# ============================================================

def render_aztec_chart(chart, after_chart_hook=None):
    """渲染完整的阿茲特克占星排盤"""
    _render_tonalpohualli(chart)
    if after_chart_hook:
        after_chart_hook()
    st.divider()
    _render_info(chart)
    st.divider()
    _render_planet_table(chart)
    st.divider()
    _render_aztec_day_signs(chart)


def _render_info(chart):
    """渲染排盤基本資訊"""
    st.subheader("📋 排盤資訊 (Chart Information)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**日期:** {chart.year}/{chart.month}/{chart.day}")
        st.write(f"**時間:** {chart.hour:02d}:{chart.minute:02d}")
        st.write(f"**時區:** UTC{chart.timezone:+.1f}")
    with col2:
        st.write(f"**地點:** {chart.location_name}")
        st.write(f"**緯度:** {chart.latitude:.4f}°")
        st.write(f"**經度:** {chart.longitude:.4f}°")
    with col3:
        st.write(f"**儒略日:** {chart.julian_day:.2f}")
        st.write(f"**Tonalpohualli:** "
                 f"`{chart.tonalpohualli_number} {chart.tonalpohualli_sign_name}`")
        st.write(f"**Trecena:** "
                 f"{chart.trecena_ruler_name}（{chart.trecena_ruler_cn}）")


def _render_tonalpohualli(chart):
    """渲染 Tonalpohualli 神聖曆主視覺區塊"""
    st.subheader("🗓️ 阿茲特克神聖曆 (Tonalpohualli)")

    # Tonalpohualli 與 Trecena 並排顯示
    tcol1, tcol2 = st.columns(2)

    # Tonalpohualli 日徵
    with tcol1:
        st.markdown("#### 🌀 Tonalpohualli（神聖曆 — 日徵）")
        sign_color = chart.color_hex if chart.color_hex != "#FFFFFF" else "#2F4F4F"
        st.markdown(
            f'<div style="background:{sign_color};padding:16px;border-radius:10px;'
            f'text-align:center;color:white;">'
            f'<div style="font-size:40px">{chart.tonalpohualli_glyph}</div>'
            f'<div style="font-size:32px;font-weight:bold">'
            f'{chart.tonalpohualli_number} {chart.tonalpohualli_sign_name}</div>'
            f'<div style="font-size:16px">'
            f'{chart.tonalpohualli_sign_cn} / {chart.tonalpohualli_sign_en}</div>'
            f'<div style="font-size:14px;margin-top:8px;color:#DDA0DD">'
            f'能量: {chart.tonalpohualli_energy}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"**Tonalpohualli 循環:** 每 260 天（13 數字 × 20 日徵）<br/>"
            f"**今日日徵:** {chart.tonalpohualli_sign_name}"
            f"（{chart.tonalpohualli_sign_cn}）<br/>"
            f"**能量含義:** {chart.tonalpohualli_energy}",
            unsafe_allow_html=True,
        )

    # Trecena & 守護神祇
    with tcol2:
        st.markdown("#### 🏛️ Trecena（13天週期）& 守護神祇")
        trecena_color = "#2F4F4F"
        st.markdown(
            f'<div style="background:{trecena_color};padding:16px;border-radius:10px;'
            f'text-align:center;color:white;">'
            f'<div style="font-size:32px;font-weight:bold">'
            f'Trecena: {chart.trecena_ruler_name}</div>'
            f'<div style="font-size:16px">{chart.trecena_ruler_cn}</div>'
            f'<div style="font-size:14px;margin-top:8px;color:#87CEEB">'
            f'第 {chart.trecena_number} / 13 天</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"**Trecena 週期:** 每 13 天為一個能量週期<br/>"
            f"**主宰日徵:** {chart.trecena_ruler_name}"
            f"（{chart.trecena_ruler_cn}）<br/>"
            f"**今日位置:** 第 {chart.trecena_number} 天",
            unsafe_allow_html=True,
        )

    # 守護神祇與方位顏色
    st.markdown("#### 🌙 守護神祇與宇宙方位")
    deity_col, dir_col = st.columns(2)
    with deity_col:
        st.info(f"**守護神祇 (Patron Deity):** {chart.deity}")
        st.caption("每個日徵由特定的阿茲特克神祇守護，影響此日出生者的性格與命運")
    with dir_col:
        dir_display = f"{chart.direction_cn} ({chart.direction_en})"
        color_display = f"{chart.color_cn} ({chart.color_en})"
        st.info(f"**宇宙方位:** {dir_display}  |  **聖色:** {color_display}")
        st.caption("阿茲特克宇宙觀中，四方位（東南西北）各有對應顏色與能量特質")


def _render_planet_table(chart):
    """渲染行星位置表格（西方占星疊加）"""
    st.subheader("🪐 行星位置（西方占星疊加）")
    header = (
        "| 行星 | 星座 | 度數 | 逆行 | 日徵 | 阿茲特克能量 |"
    )
    sep = "|:---:|:---:|:---:|:---:|:---:|:---:|"
    rows = [header, sep]
    for p in chart.planets:
        retro = "℞" if p.retrograde else ""
        color = AZTEC_PLANET_COLORS.get(p.name, "#c8c8c8")
        name_html = (
            f'<span style="color:{color};font-weight:bold">{p.name}</span>'
        )
        day_sign = AZTEC_TONALPOHUALLI_SIGNS[p.aztec_day_lord]
        rows.append(
            f"| {name_html} "
            f"| {p.sign_glyph} {p.sign} ({p.sign_chinese}) "
            f"| {p.sign_degree:.2f}° "
            f"| {retro} "
            f"| {day_sign[1]}（{day_sign[2]}） "
            f"| {p.aztec_energy} |"
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)


def _render_aztec_day_signs(chart):
    """渲染阿茲特克 20 日徵循環圖（今日高亮）"""
    st.subheader("🌀 Tonalpohualli 二十日徵循環（20 Day Signs）")

    # 20 日徵網格
    day_index = int(chart.julian_day - AZTEC_EPOCH_JD) % 20
    signs_html = (
        '<div style="display:grid;grid-template-columns:repeat(5,1fr);'
        'gap:6px;margin-bottom:20px;">'
    )
    for i in range(20):
        info = AZTEC_TONALPOHUALLI_SIGNS[i]
        glyph = AZTEC_SIGN_GLYPHS.get(i, "")
        dir_info = AZTEC_DIRECTIONS.get(i, ("", "", "", "", "#333"))
        is_today = "border:3px solid #FFD700;" if i == day_index else ""
        bg_color = dir_info[4] if i == day_index else "#1a0d2e"
        # 確保白色背景上的文字可讀
        text_color = "#333" if bg_color == "#FFFFFF" else "white"
        signs_html += (
            f'<div style="background:{bg_color};padding:8px;border-radius:6px;'
            f'text-align:center;color:{text_color};{is_today}">'
            f'<div style="font-size:20px">{glyph}</div>'
            f'<div style="font-size:12px;font-weight:bold">{info[1]}</div>'
            f'<div style="font-size:10px;color:#DDA0DD">{info[2]}</div>'
            f'</div>'
        )
    signs_html += '</div>'
    st.markdown("**今日日徵以金框高亮：**")
    st.markdown(signs_html, unsafe_allow_html=True)

    # 方位說明
    st.markdown("**四方位對應：**")
    dir_html = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;">'
    for dir_en, dir_cn, col_en, col_cn, col_hex in [
        ("East",  "東方", "Red",    "紅色",  "#DC143C"),
        ("North", "北方", "White",  "白色",  "#FFFFFF"),
        ("West",  "西方", "Blue",   "藍色",  "#4169E1"),
        ("South", "南方", "Yellow", "黃色",  "#FFD700"),
    ]:
        text_color = "#333" if col_hex == "#FFFFFF" else "white"
        dir_html += (
            f'<div style="background:{col_hex};padding:10px;border-radius:6px;'
            f'text-align:center;color:{text_color};">'
            f'<div style="font-size:14px;font-weight:bold">'
            f'{dir_cn} ({dir_en})</div>'
            f'<div style="font-size:12px">{col_cn} ({col_en})</div>'
            f'</div>'
        )
    dir_html += '</div>'
    st.markdown(dir_html, unsafe_allow_html=True)
    st.caption("⚡ 阿茲特克宇宙觀：東=紅=創始，北=白=死亡，西=藍=女性，南=黃=生命")
