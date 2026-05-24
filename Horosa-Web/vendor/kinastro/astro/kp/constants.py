"""
astro/kp/constants.py — KP 占星術專用常數與對照表

Krishnamurti Paddhati (KP Astrology) Constants and Lookup Tables

包含：
1. KP New Ayanamsa 數值
2. 27 Nakshatras（宿）詳細資料（名稱、度數範圍、主星）
3. 249 Sub Lords 對照表（每宿 9 個 Sub，按 Vimshottari Dasha 比例分割）
4. 行星編號與符號
5. 12 宮位定義
6. Rasi Lords（星座主）對照表
7. 房屋意義分類（House Groupings）

References
----------
- Krishnamurti, K.S. "KP Reader Vol. I: Fundamentals" - Appendix Tables
- "KP Ephemeris" published by K.S. Krishnamurti Publications
"""

from typing import Dict, List, Tuple

# ============================================================================
# KP NEW AYANAMSA
# ============================================================================

# KP New Ayanamsa 數值（相對於 Swiss Ephemeris 的 SE_SIDM_FAGAN_BRADLEY）
# KP Ayanamsa = 0°00'00" at 1900 AD Jan 1, 12:00 GMT
# 實際計算時使用：KP Ayanamsa = Lahiri Ayanamsa - 0°00'10.4"
KP_AYANAMSA = 23.852314814814815  # 2024 年的近似值，實際會動態計算

# Ayanamsa 名稱
KP_AYANAMSA_NAME = "KP New Ayanamsa"
KP_AYANAMSA_NAME_CN = "克里希納穆提新歲差"

# ============================================================================
# 27 NAKSHATRAS（二十七宿）
# ============================================================================

# 每宿的詳細資料：
# (名稱，起始經度，寬度，主星，梵文名稱，中文譯名)
# 起始經度從 0°（白羊座 0°）開始計算
# 每宿寬度 = 360° / 27 = 13°20' = 13.3333...度

NAKSHATRAS: List[Dict] = [
    # 白羊座 Aries
    {"name": "Ashwini", "start": 0.0, "width": 13.3333333333, "lord": "Ketu", 
     "sanskrit": "अश्विनी", "cn": "婁宿", "symbol": "🐴", "deity": "Ashwini Kumaras"},
    {"name": "Bharani", "start": 13.3333333333, "width": 13.3333333333, "lord": "Venus",
     "sanskrit": "भरणी", "cn": "婁宿", "symbol": "🔺", "deity": "Yama"},
    {"name": "Krittika", "start": 26.6666666667, "width": 13.3333333333, "lord": "Sun",
     "sanskrit": "कृत्तिका", "cn": "胃宿", "symbol": "🔪", "deity": "Agni"},
    
    # 金牛座 Taurus
    {"name": "Rohini", "start": 40.0, "width": 13.3333333333, "lord": "Moon",
     "sanskrit": "रोहिणी", "cn": "昴宿", "symbol": "🐂", "deity": "Brahma"},
    {"name": "Mrigashira", "start": 53.3333333333, "width": 13.3333333333, "lord": "Mars",
     "sanskrit": "मृगशिरा", "cn": "畢宿", "symbol": "🦌", "deity": "Soma"},
    {"name": "Ardra", "start": 66.6666666667, "width": 13.3333333333, "lord": "Rahu",
     "sanskrit": "आर्द्रा", "cn": "觜宿", "symbol": "💧", "deity": "Rudra"},
    
    # 雙子座 Gemini
    {"name": "Punarvasu", "start": 80.0, "width": 13.3333333333, "lord": "Jupiter",
     "sanskrit": "पुनर्वसु", "cn": "參宿", "symbol": "🏹", "deity": "Aditi"},
    {"name": "Pushya", "start": 93.3333333333, "width": 13.3333333333, "lord": "Saturn",
     "sanskrit": "पुष्य", "cn": "井宿", "symbol": "🌸", "deity": "Brihaspati"},
    {"name": "Ashlesha", "start": 106.6666666667, "width": 13.3333333333, "lord": "Mercury",
     "sanskrit": "आश्लेषा", "cn": "鬼宿", "symbol": "🐍", "deity": "Nagas"},
    
    # 巨蟹座 Cancer
    {"name": "Magha", "start": 120.0, "width": 13.3333333333, "lord": "Ketu",
     "sanskrit": "मघा", "cn": "柳宿", "symbol": "👑", "deity": "Pitris"},
    {"name": "Purva Phalguni", "start": 133.3333333333, "width": 13.3333333333, "lord": "Venus",
     "sanskrit": "पूर्व फाल्गुनी", "cn": "星宿", "symbol": "🛏️", "deity": "Bhaga"},
    {"name": "Uttara Phalguni", "start": 146.6666666667, "width": 13.3333333333, "lord": "Sun",
     "sanskrit": "उत्तर फाल्गुनी", "cn": "張宿", "symbol": "🛌", "deity": "Aryaman"},
    
    # 獅子座 Leo
    {"name": "Hasta", "start": 160.0, "width": 13.3333333333, "lord": "Moon",
     "sanskrit": "हस्त", "cn": "翼宿", "symbol": "✋", "deity": "Savitar"},
    {"name": "Chitra", "start": 173.3333333333, "width": 13.3333333333, "lord": "Mars",
     "sanskrit": "चित्रा", "cn": "軫宿", "symbol": "💎", "deity": "Vishvakarma"},
    {"name": "Swati", "start": 186.6666666667, "width": 13.3333333333, "lord": "Rahu",
     "sanskrit": "स्वाति", "cn": "角宿", "symbol": "🌾", "deity": "Vayu"},
    
    # 處女座 Virgo
    {"name": "Vishakha", "start": 200.0, "width": 13.3333333333, "lord": "Jupiter",
     "sanskrit": "विशाखा", "cn": "亢宿", "symbol": "🏮", "deity": "Indra-Agni"},
    {"name": "Anuradha", "start": 213.3333333333, "width": 13.3333333333, "lord": "Saturn",
     "sanskrit": "अनुराधा", "cn": "氐宿", "symbol": "🪷", "deity": "Mitra"},
    {"name": "Jyeshtha", "start": 226.6666666667, "width": 13.3333333333, "lord": "Mercury",
     "sanskrit": "ज्येष्ठा", "cn": "房宿", "symbol": "🛡️", "deity": "Indra"},
    
    # 天秤座 Libra
    {"name": "Mula", "start": 240.0, "width": 13.3333333333, "lord": "Ketu",
     "sanskrit": "मूल", "cn": "心宿", "symbol": "🌪️", "deity": "Nirriti"},
    {"name": "Purva Ashadha", "start": 253.3333333333, "width": 13.3333333333, "lord": "Venus",
     "sanskrit": "पूर्वाषाढ़ा", "cn": "尾宿", "symbol": "🌊", "deity": "Apas"},
    {"name": "Uttara Ashadha", "start": 266.6666666667, "width": 13.3333333333, "lord": "Sun",
     "sanskrit": "उत्तराषाढ़ा", "cn": "箕宿", "symbol": "🐘", "deity": "Vishvadevas"},
    
    # 天蠍座 Scorpio
    {"name": "Shravana", "start": 280.0, "width": 13.3333333333, "lord": "Moon",
     "sanskrit": "श्रवण", "cn": "斗宿", "symbol": "👂", "deity": "Vishnu"},
    {"name": "Dhanishta", "start": 293.3333333333, "width": 13.3333333333, "lord": "Mars",
     "sanskrit": "धनिष्ठा", "cn": "牛宿", "symbol": "🥁", "deity": "Vasus"},
    {"name": "Shatabhisha", "start": 306.6666666667, "width": 13.3333333333, "lord": "Rahu",
     "sanskrit": "शतभिषा", "cn": "女宿", "symbol": "💊", "deity": "Varuna"},
    
    # 水瓶座 Aquarius
    {"name": "Purva Bhadrapada", "start": 320.0, "width": 13.3333333333, "lord": "Jupiter",
     "sanskrit": "पूर्वभाद्रपदा", "cn": "虛宿", "symbol": "🗡️", "deity": "Aja Ekapada"},
    {"name": "Uttara Bhadrapada", "start": 333.3333333333, "width": 13.3333333333, "lord": "Saturn",
     "sanskrit": "उत्तरभाद्रपदा", "cn": "危宿", "symbol": "🐍", "deity": "Ahir Budhnya"},
    {"name": "Revati", "start": 346.6666666667, "width": 13.3333333333, "lord": "Mercury",
     "sanskrit": "रेवती", "cn": "室宿", "symbol": "🐚", "deity": "Pushan"},
]

# ============================================================================
# VIMSHOTTARI DASHA 週期（用於計算 Sub Lords）
# ============================================================================

# Vimshottari Dasha 週期（年數）
# 順序：Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury
VIMSHOTTARI_DASHA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

# 總週期 = 120 年
VIMSHOTTARI_TOTAL_YEARS = 120

# ============================================================================
# SUB LORDS 對照表（249 Sub）
# ============================================================================

# 每宿的 9 個 Sub，按照 Vimshottari Dasha 順序排列
# 格式：宿序號 (0-26) -> [(Sub 序號，主星，起始經度比例，結束經度比例)]
# Sub 寬度比例 = 該星 Dasha 年數 / 120

SUB_LORDS: Dict[int, List[Dict]] = {
    # 範例：Ashwini (宿 0) 的 9 個 Sub
    # Ketu (7 年) -> Venus (20 年) -> Sun (6 年) -> Moon (10 年) -> Mars (7 年) -> Rahu (18 年) -> Jupiter (16 年) -> Saturn (19 年) -> Mercury (17 年)
    0: [  # Ashwini
        {"lord": "Ketu", "start_ratio": 0.0, "end_ratio": 7/120},
        {"lord": "Venus", "start_ratio": 7/120, "end_ratio": (7+20)/120},
        {"lord": "Sun", "start_ratio": 27/120, "end_ratio": (27+6)/120},
        {"lord": "Moon", "start_ratio": 33/120, "end_ratio": (33+10)/120},
        {"lord": "Mars", "start_ratio": 43/120, "end_ratio": (43+7)/120},
        {"lord": "Rahu", "start_ratio": 50/120, "end_ratio": (50+18)/120},
        {"lord": "Jupiter", "start_ratio": 68/120, "end_ratio": (68+16)/120},
        {"lord": "Saturn", "start_ratio": 84/120, "end_ratio": (84+19)/120},
        {"lord": "Mercury", "start_ratio": 103/120, "end_ratio": 120/120},
    ],
    # 注意：實際使用時會動態計算所有 27 宿的 Sub Lords
    # 此處僅提供範例，完整計算見 kp_utils.py 的 get_sub_lord_table()
}

# ============================================================================
# PLANETS（行星）
# ============================================================================

# KP 使用的 9 顆行星（7 顆實星 + 2 顆虛星 Rahu/Ketu）
PLANETS = {
    "Sun": {"id": 0, "symbol": "☉", "cn": "太陽", "sanskrit": "Surya", "type": "luminary"},
    "Moon": {"id": 1, "symbol": "☽", "cn": "月亮", "sanskrit": "Chandra", "type": "luminary"},
    "Mars": {"id": 2, "symbol": "♂", "cn": "火星", "sanskrit": "Mangal", "type": "planet"},
    "Mercury": {"id": 3, "symbol": "☿", "cn": "水星", "sanskrit": "Budh", "type": "planet"},
    "Jupiter": {"id": 4, "symbol": "♃", "cn": "木星", "sanskrit": "Guru", "type": "planet"},
    "Venus": {"id": 5, "symbol": "♀", "cn": "金星", "sanskrit": "Shukra", "type": "planet"},
    "Saturn": {"id": 6, "symbol": "♄", "cn": "土星", "sanskrit": "Shani", "type": "planet"},
    "Rahu": {"id": 7, "symbol": "☊", "cn": "羅睺", "sanskrit": "Rahu", "type": "shadow"},
    "Ketu": {"id": 8, "symbol": "☋", "cn": "計都", "sanskrit": "Ketu", "type": "shadow"},
}

# 行星順序（用於計算 Sub Lords）
PLANET_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

# ============================================================================
# RASI LORDS（星座主）
# ============================================================================

# 12 星座的主星（傳統印度占星）
RASI_LORDS = {
    0: "Mars",     # Aries 白羊座
    1: "Venus",    # Taurus 金牛座
    2: "Mercury",  # Gemini 雙子座
    3: "Moon",     # Cancer 巨蟹座
    4: "Sun",      # Leo 獅子座
    5: "Mercury",  # Virgo 處女座
    6: "Venus",    # Libra 天秤座
    7: "Mars",     # Scorpio 天蠍座
    8: "Jupiter",  # Sagittarius 射手座
    9: "Saturn",   # Capricorn 摩羯座
    10: "Saturn",  # Aquarius 水瓶座
    11: "Jupiter", # Pisces 雙魚座
}

# 星座名稱對照
RASI_NAMES = {
    0: {"en": "Aries", "cn": "白羊座", "sanskrit": "Mesha"},
    1: {"en": "Taurus", "cn": "金牛座", "sanskrit": "Vrishabha"},
    2: {"en": "Gemini", "cn": "雙子座", "sanskrit": "Mithuna"},
    3: {"en": "Cancer", "cn": "巨蟹座", "sanskrit": "Karka"},
    4: {"en": "Leo", "cn": "獅子座", "sanskrit": "Simha"},
    5: {"en": "Virgo", "cn": "處女座", "sanskrit": "Kanya"},
    6: {"en": "Libra", "cn": "天秤座", "sanskrit": "Tula"},
    7: {"en": "Scorpio", "cn": "天蠍座", "sanskrit": "Vrishchika"},
    8: {"en": "Sagittarius", "cn": "射手座", "sanskrit": "Dhanu"},
    9: {"en": "Capricorn", "cn": "摩羯座", "sanskrit": "Makara"},
    10: {"en": "Aquarius", "cn": "水瓶座", "sanskrit": "Kumbha"},
    11: {"en": "Pisces", "cn": "雙魚座", "sanskrit": "Meena"},
}

# ============================================================================
# HOUSES（宮位）
# ============================================================================

# 12 宮位定義
HOUSES = {
    1: {"en": "Ascendant", "cn": "命宮", "sanskrit": "Lagna", "meaning": "自我、外貌、個性"},
    2: {"en": "Wealth", "cn": "財帛宮", "sanskrit": "Dhana", "meaning": "財富、言語、家庭"},
    3: {"en": "Siblings", "cn": "兄弟宮", "sanskrit": "Sahaja", "meaning": "兄弟、勇氣、溝通"},
    4: {"en": "Mother", "cn": "田宅宮", "sanskrit": "Bandhu", "meaning": "母親、家宅、內心"},
    5: {"en": "Children", "cn": "男女宮", "sanskrit": "Putra", "meaning": "子女、戀愛、智慧"},
    6: {"en": "Enemies", "cn": "疾厄宮", "sanskrit": "Ari", "meaning": "敵人、疾病、債務"},
    7: {"en": "Spouse", "cn": "夫妻宮", "sanskrit": "Yuvati", "meaning": "配偶、合作、公開敵人"},
    8: {"en": "Death", "cn": "遷移宮", "sanskrit": "Randhra", "meaning": "死亡、變故、神秘"},
    9: {"en": "Fortune", "cn": "人馬宮", "sanskrit": "Dharma", "meaning": "幸運、宗教、長途旅行"},
    10: {"en": "Career", "cn": "官祿宮", "sanskrit": "Karma", "meaning": "事業、地位、名譽"},
    11: {"en": "Gains", "cn": "福德宮", "sanskrit": "Labha", "meaning": "收益、願望、朋友"},
    12: {"en": "Loss", "cn": "相貌宮", "sanskrit": "Vyaya", "meaning": "損失、靈性、解脫"},
}

# ============================================================================
# HOUSE GROUPINGS（房屋分類）
# ============================================================================

# KP 房屋分組（用於 Significators 計算）

# 1. 角宮（Kendra Houses）— 強力宮位
KENDRA_HOUSES = [1, 4, 7, 10]

# 2. 三合宮（Trikona Houses）— 吉祥宮位
TRIKONA_HOUSES = [1, 5, 9]

# 3. 上行宮（Upachaya Houses）— 成長宮位
UPACHAYA_HOUSES = [3, 6, 10, 11]

# 4. 吉祥宮（Dharma Karmadhipati Houses）
DHARMA_KARMA_HOUSES = [9, 10]

# 5. 凶宮（Dusthana Houses）
DUSTHANA_HOUSES = [6, 8, 12]

# 6. 死亡宮（Maraka Houses）
MARAKA_HOUSES = [2, 7]

# ============================================================================
# SIGNIFICATORS 強度分類
# ============================================================================

SIGNIFICATOR_STRENGTH = {
    "Very Strong": {"en": "Very Strong", "cn": "極強", "description": "星體位於該宮或主宰該宮"},
    "Strong": {"en": "Strong", "cn": "強", "description": "星體與該宮主星有相位或位於其星座"},
    "Weak": {"en": "Weak", "cn": "弱", "description": "星體與該宮僅有間接關聯"},
    "Very Weak": {"en": "Very Weak", "cn": "極弱", "description": "星體與該宮幾乎無關聯"},
}

# ============================================================================
# KP HORARY（問卜）專用常數
# ============================================================================

# Ruling Planets 計算時間容差（分鐘）
HORARY_TIME_TOLERANCE = 5

# 問卜圖默认使用提問時間
HORARY_DEFAULT_USE_QUESTION_TIME = True

# ============================================================================
# KP AYANAMSA CALCULATION
# ============================================================================

def get_kp_ayanamsa(julian_day: float) -> float:
    """
    計算指定儒略日的 KP New Ayanamsa 值
    
    KP Ayanamsa 公式：
    KP Ayanamsa = (Julian Year - 1900) * 50.2388475" + 0°00'10.4"
    
    Parameters
    ----------
    julian_day : float
        儒略日
    
    Returns
    -------
    float
        KP Ayanamsa 值（度數）
    """
    # 計算從 1900 年起的年數
    # 1900 年 1 月 1 日 12:00 GMT 的儒略日 = 2415020.3125
    jd_1900 = 2415020.3125
    years_since_1900 = (julian_day - jd_1900) / 365.2425
    
    # KP Ayanamsa 增長率：每年 50.2388475 角秒
    # 轉換為度數：50.2388475 / 3600 = 0.0139552354 度/年
    ayanamsa_seconds = years_since_1900 * 50.2388475
    
    # 加上初始偏移 0°00'10.4" = 10.4 角秒
    ayanamsa_seconds += 10.4
    
    # 轉換為度數
    ayanamsa_degrees = ayanamsa_seconds / 3600.0
    
    return ayanamsa_degrees


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_nakshatra_index(longitude: float) -> int:
    """
    根據經度計算所屬宿序號（0-26）
    
    Parameters
    ----------
    longitude : float
        經度（0-360 度）
    
    Returns
    -------
    int
        宿序號（0-26）
    """
    # 每宿寬度 = 360 / 27 = 13.3333...度
    nakshatra_width = 360.0 / 27.0
    return int(longitude / nakshatra_width) % 27


def get_sub_index(longitude: float) -> int:
    """
    根據經度計算所屬 Sub 序號（0-248）
    
    Parameters
    ----------
    longitude : float
        經度（0-360 度）
    
    Returns
    -------
    int
        Sub 序號（0-248）
    """
    # 每宿 9 個 Sub，共 243 個 Sub（實際使用 249 個）
    # 每個 Sub 寬度 = 360 / 249 ≈ 1.4457831325 度
    sub_width = 360.0 / 249.0
    return int(longitude / sub_width) % 249


# ============================================================================
# COLOR SCHEME（KP 專用配色）
# ============================================================================

KP_COLORS = {
    "primary": "#FF6B35",      # 橘紅色（KP 主題色）
    "secondary": "#004E89",    # 深藍色
    "accent": "#FFD23F",       # 金黃色
    "background": "#F7F7F7",   # 淺灰背景
    "text": "#2D3142",         # 深灰文字
    "border": "#B5B5B5",       # 邊框色
    "success": "#00C853",      # 成功（綠色）
    "warning": "#FFAB00",      # 警告（琥珀色）
    "error": "#D50000",        # 錯誤（紅色）
    "planet_sun": "#FF6B35",
    "planet_moon": "#E0E0E0",
    "planet_mars": "#D50000",
    "planet_mercury": "#00C853",
    "planet_jupiter": "#FFD23F",
    "planet_venus": "#FF69B4",
    "planet_saturn": "#424242",
    "planet_rahu": "#8B4513",
    "planet_ketu": "#800080",
}
