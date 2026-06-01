"""
七政四餘常量定義 (Constants for Seven Governors and Four Remainders)

定義中國傳統占星術中使用的星曜、宮位、二十八宿等常量。
"""

import swisseph as swe

# ============================================================
# 七政 (Seven Governors) - 七顆主要星曜
# ============================================================
SEVEN_GOVERNORS = {
    "太陽": swe.SUN,
    "太陰": swe.MOON,
    "水星": swe.MERCURY,
    "金星": swe.VENUS,
    "火星": swe.MARS,
    "木星": swe.JUPITER,
    "土星": swe.SATURN,
}

# ============================================================
# 四餘 (Four Remainders) - 四顆虛星
# 傳統七政四餘定義 (Traditional Chinese 七政四餘 definitions):
# 羅睺 (Rahu) = 降交點 / South Node (= 計都 + 180°，計算時由 calculator 推導)
# 計都 (Ketu) = 升交點 / North Node (Mean Node，傳統七政四餘使用平均交點)
# 月孛 (Yuebei) = 平均遠地點 (Mean Apogee / Lilith)
# 紫氣 (Ziqi) = 真實遠地點 (Osculating / True Apogee)
# ============================================================
FOUR_REMAINDERS = {
    "羅睺": None,                 # 降交點 / South Node = MEAN_NODE + 180° (computed in calculator)
    "計都": swe.MEAN_NODE,       # 升交點 / North Node (Mean Node)
    "月孛": swe.MEAN_APOG,       # Mean Apogee / Lilith
    "紫氣": swe.OSCU_APOG,       # Osculating Apogee (True Apogee)
}

# ============================================================
# 十二地支 (Twelve Earthly Branches)
# ============================================================
EARTHLY_BRANCHES = [
    "子", "丑", "寅", "卯", "辰", "巳",
    "午", "未", "申", "酉", "戌", "亥",
]

# ============================================================
# 十二宮 (Twelve Houses/Palaces)
# ============================================================
TWELVE_PALACES = [
    "命宮", "財帛宮", "兄弟宮", "田宅宮",
    "男女宮", "奴僕宮", "夫妻宮", "疾厄宮",
    "遷移宮", "官祿宮", "福德宮", "相貌宮",
]

# ============================================================
# 十二星次 (Twelve Star Stations) - 中國黃道十二宮
# 對應西方黃道十二宮，但起始點和名稱不同
# ============================================================
TWELVE_SIGNS_CHINESE = [
    "戌宮(降婁)", "酉宮(大梁)", "申宮(實沈)", "未宮(鶉首)",
    "午宮(鶉火)", "巳宮(鶉尾)", "辰宮(壽星)", "卯宮(大火)",
    "寅宮(析木)", "丑宮(星紀)", "子宮(玄枵)", "亥宮(娵訾)",
]

TWELVE_SIGNS_WESTERN = [
    "白羊", "金牛", "雙子", "巨蟹",
    "獅子", "處女", "天秤", "天蠍",
    "射手", "摩羯", "水瓶", "雙魚",
]

# ============================================================
# 二十八宿 (Twenty-Eight Lunar Mansions)
# 每宿對應的黃經度數範圍
# 宿界參考 MOIRA (BahnAstro/MOIRA_chinese_astrology) 精確距星黃經
# 注意: MOIRA 使用 27 個邊界點，缺少 室宿距星(α Pegasi)，
# 此處依傳統取 α Pegasi ≈ 353.49° 補全為 28 個邊界。
# ============================================================
TWENTY_EIGHT_MANSIONS = [
    # 東方青龍七宿
    {"name": "角", "element": "木", "animal": "蛟", "group": "東方青龍", "start_lon": 203.8375},
    {"name": "亢", "element": "金", "animal": "龍", "group": "東方青龍", "start_lon": 214.4899},
    {"name": "氐", "element": "土", "animal": "貉", "group": "東方青龍", "start_lon": 225.0216},
    {"name": "房", "element": "日", "animal": "兔", "group": "東方青龍", "start_lon": 242.9360},
    {"name": "心", "element": "月", "animal": "狐", "group": "東方青龍", "start_lon": 249.7584},
    {"name": "尾", "element": "火", "animal": "虎", "group": "東方青龍", "start_lon": 256.1517},
    {"name": "箕", "element": "水", "animal": "豹", "group": "東方青龍", "start_lon": 271.2576},
    # 北方玄武七宿
    {"name": "斗", "element": "木", "animal": "獬", "group": "北方玄武", "start_lon": 280.1775},
    {"name": "牛", "element": "金", "animal": "牛", "group": "北方玄武", "start_lon": 304.0435},
    {"name": "女", "element": "土", "animal": "蝠", "group": "北方玄武", "start_lon": 311.7193},
    {"name": "虛", "element": "日", "animal": "鼠", "group": "北方玄武", "start_lon": 323.3912},
    {"name": "危", "element": "月", "animal": "燕", "group": "北方玄武", "start_lon": 333.3486},
    {"name": "室", "element": "火", "animal": "豬", "group": "北方玄武", "start_lon": 353.49},
    {"name": "壁", "element": "水", "animal": "貐", "group": "北方玄武", "start_lon": 9.1522},
    # 西方白虎七宿
    {"name": "奎", "element": "木", "animal": "狼", "group": "西方白虎", "start_lon": 22.3721},
    {"name": "婁", "element": "金", "animal": "狗", "group": "西方白虎", "start_lon": 33.9661},
    {"name": "胃", "element": "土", "animal": "雉", "group": "西方白虎", "start_lon": 46.9312},
    {"name": "昴", "element": "日", "animal": "雞", "group": "西方白虎", "start_lon": 59.4080},
    {"name": "畢", "element": "月", "animal": "烏", "group": "西方白虎", "start_lon": 68.4612},
    {"name": "觜", "element": "火", "animal": "猴", "group": "西方白虎", "start_lon": 83.7030},
    {"name": "參", "element": "水", "animal": "猿", "group": "西方白虎", "start_lon": 84.6775},
    # 南方朱雀七宿
    {"name": "井", "element": "木", "animal": "犴", "group": "南方朱雀", "start_lon": 95.2980},
    {"name": "鬼", "element": "金", "animal": "羊", "group": "南方朱雀", "start_lon": 125.7246},
    {"name": "柳", "element": "土", "animal": "獐", "group": "南方朱雀", "start_lon": 130.3005},
    {"name": "星", "element": "日", "animal": "馬", "group": "南方朱雀", "start_lon": 147.2753},
    {"name": "張", "element": "月", "animal": "鹿", "group": "南方朱雀", "start_lon": 155.6874},
    {"name": "翼", "element": "火", "animal": "蛇", "group": "南方朱雀", "start_lon": 173.6856},
    {"name": "軫", "element": "水", "animal": "蚓", "group": "南方朱雀", "start_lon": 190.7218},
]

# ============================================================
# 二十八宿今制（立命用）(Twenty-Eight Lunar Mansions — Modern 立命 System)
# 用於七政四餘「今制」立命計算，宿界依傳統立命曆法校正。
# 以實測生辰案例反推校準，與天文 MOIRA 位置有別。
#
# 校準說明：以 1985-08-26 02:55 香港男命為參考案例（今制=參水八度立命），
# 在 _TANG_EPOCH_AYANAMSA_AT_J2000=29.185 條件下，liming_lon≈80.825°。
# 各宿界在 MOIRA 原始值基礎上統一平移 +1.5764°（即參宿起始從 71.2486° 校正至
# 72.8250°，使 liming_lon - 參起始 = 8°），以符合傳統今制立命算法。
# ============================================================
TWENTY_EIGHT_MANSIONS_LIMING = [
    # 東方青龍七宿
    {"name": "角", "element": "木", "animal": "蛟", "group": "東方青龍", "start_lon": 181.6044},
    {"name": "亢", "element": "金", "animal": "龍", "group": "東方青龍", "start_lon": 205.6564},
    {"name": "氐", "element": "土", "animal": "貉", "group": "東方青龍", "start_lon": 211.0925},
    {"name": "房", "element": "日", "animal": "兔", "group": "東方青龍", "start_lon": 220.8775},
    {"name": "心", "element": "月", "animal": "狐", "group": "東方青龍", "start_lon": 223.0520},
    {"name": "尾", "element": "火", "animal": "虎", "group": "東方青龍", "start_lon": 227.4008},
    {"name": "箕", "element": "水", "animal": "豹", "group": "東方青龍", "start_lon": 235.0114},
    # 北方玄武七宿
    {"name": "斗", "element": "木", "animal": "獬", "group": "北方玄武", "start_lon": 243.3424},
    {"name": "牛", "element": "金", "animal": "牛", "group": "北方玄武", "start_lon": 265.5584},
    {"name": "女", "element": "土", "animal": "蝠", "group": "北方玄武", "start_lon": 273.7085},
    {"name": "虛", "element": "日", "animal": "鼠", "group": "北方玄武", "start_lon": 285.9337},
    {"name": "危", "element": "月", "animal": "燕", "group": "北方玄武", "start_lon": 296.1214},
    {"name": "室", "element": "火", "animal": "豬", "group": "北方玄武", "start_lon": 322.6570},
    {"name": "壁", "element": "水", "animal": "貐", "group": "北方玄武", "start_lon": 345.0027},
    # 西方白虎七宿
    {"name": "奎", "element": "木", "animal": "狼", "group": "西方白虎", "start_lon": 1.7621},
    {"name": "婁", "element": "金", "animal": "狗", "group": "西方白虎", "start_lon": 17.1248},
    {"name": "胃", "element": "土", "animal": "雉", "group": "西方白虎", "start_lon": 33.8841},
    {"name": "昴", "element": "日", "animal": "雞", "group": "西方白虎", "start_lon": 50.6434},
    {"name": "畢", "element": "月", "animal": "烏", "group": "西方白虎", "start_lon": 58.3216},
    {"name": "觜", "element": "火", "animal": "猴", "group": "西方白虎", "start_lon": 71.9719},
    {"name": "參", "element": "水", "animal": "猿", "group": "西方白虎", "start_lon": 72.8250},
    # 南方朱雀七宿
    {"name": "井", "element": "木", "animal": "犴", "group": "南方朱雀", "start_lon": 81.3564},
    {"name": "鬼", "element": "金", "animal": "羊", "group": "南方朱雀", "start_lon": 111.2764},
    {"name": "柳", "element": "土", "animal": "獐", "group": "南方朱雀", "start_lon": 115.5747},
    {"name": "星", "element": "日", "animal": "馬", "group": "南方朱雀", "start_lon": 129.3294},
    {"name": "張", "element": "月", "animal": "鹿", "group": "南方朱雀", "start_lon": 135.8294},
    {"name": "翼", "element": "火", "animal": "蛇", "group": "南方朱雀", "start_lon": 153.9364},
    {"name": "軫", "element": "水", "animal": "蚓", "group": "南方朱雀", "start_lon": 169.6149},
]

# ============================================================
# 二十八宿古制 (Twenty-Eight Lunar Mansions — Classical System)
# 依傳統古籍距星黃經（約漢唐曆元），以實測生辰案例反推校準。
# 格式同 TWENTY_EIGHT_MANSIONS，但 start_lon 使用古典度數。
# ============================================================
TWENTY_EIGHT_MANSIONS_ANCIENT = [
    # 東方青龍七宿
    {"name": "角", "element": "木", "animal": "蛟", "group": "東方青龍", "start_lon": 165.2075},
    {"name": "亢", "element": "金", "animal": "龍", "group": "東方青龍", "start_lon": 177.0998},
    {"name": "氐", "element": "土", "animal": "貉", "group": "東方青龍", "start_lon": 185.0280},
    {"name": "房", "element": "日", "animal": "兔", "group": "東方青龍", "start_lon": 202.6473},
    {"name": "心", "element": "月", "animal": "狐", "group": "東方青龍", "start_lon": 208.1533},
    {"name": "尾", "element": "火", "animal": "虎", "group": "東方青龍", "start_lon": 213.6594},
    {"name": "箕", "element": "水", "animal": "豹", "group": "東方青龍", "start_lon": 233.4811},
    # 北方玄武七宿
    {"name": "斗", "element": "木", "animal": "獬", "group": "北方玄武", "start_lon": 244.4932},
    {"name": "牛", "element": "金", "animal": "牛", "group": "北方玄武", "start_lon": 269.8209},
    {"name": "女", "element": "土", "animal": "蝠", "group": "北方玄武", "start_lon": 278.6306},
    {"name": "虛", "element": "日", "animal": "鼠", "group": "北方玄武", "start_lon": 290.7439},
    {"name": "危", "element": "月", "animal": "燕", "group": "北方玄武", "start_lon": 300.6547},
    {"name": "室", "element": "火", "animal": "豬", "group": "北方玄武", "start_lon": 317.1728},
    {"name": "壁", "element": "水", "animal": "貐", "group": "北方玄武", "start_lon": 333.6910},
    # 西方白虎七宿
    {"name": "奎", "element": "木", "animal": "狼", "group": "西方白虎", "start_lon": 343.6018},
    {"name": "婁", "element": "金", "animal": "狗", "group": "西方白虎", "start_lon": 2.3223},
    {"name": "胃", "element": "土", "animal": "雉", "group": "西方白虎", "start_lon": 13.3344},
    {"name": "昴", "element": "日", "animal": "雞", "group": "西方白虎", "start_lon": 29.8525},
    {"name": "畢", "element": "月", "animal": "烏", "group": "西方白虎", "start_lon": 43.0670},
    {"name": "觜", "element": "火", "animal": "猴", "group": "西方白虎", "start_lon": 58.6746},
    {"name": "參", "element": "水", "animal": "猿", "group": "西方白虎", "start_lon": 58.6850},
    # 南方朱雀七宿
    {"name": "井", "element": "木", "animal": "犴", "group": "南方朱雀", "start_lon": 69.8250},
    {"name": "鬼", "element": "金", "animal": "羊", "group": "南方朱雀", "start_lon": 97.2405},
    {"name": "柳", "element": "土", "animal": "獐", "group": "南方朱雀", "start_lon": 99.9820},
    {"name": "星", "element": "日", "animal": "馬", "group": "南方朱雀", "start_lon": 114.4398},
    {"name": "張", "element": "月", "animal": "鹿", "group": "南方朱雀", "start_lon": 119.2591},
    {"name": "翼", "element": "火", "animal": "蛇", "group": "南方朱雀", "start_lon": 132.7530},
    {"name": "軫", "element": "水", "animal": "蚓", "group": "南方朱雀", "start_lon": 148.3600},
]

# ============================================================
# 星曜顏色 (Planet Colors for Display)
# ============================================================
PLANET_COLORS = {
    "太陽": "#FF4500",
    "太陰": "#C0C0C0",
    "水星": "#4169E1",
    "金星": "#FFD700",
    "火星": "#DC143C",
    "木星": "#228B22",
    "土星": "#8B4513",
    "羅睺": "#800080",
    "計都": "#4B0082",
    "月孛": "#2F4F4F",
    "紫氣": "#9400D3",
}

# ============================================================
# 五行 (Five Elements)
# ============================================================
FIVE_ELEMENTS = {
    "太陽": "日",
    "太陰": "月",
    "水星": "水",
    "金星": "金",
    "火星": "火",
    "木星": "木",
    "土星": "土",
    "羅睺": "火",
    "計都": "土",
    "月孛": "水",
    "紫氣": "木",
}

# ============================================================
# 十二宮五行屬性 (Zodiac Sign Elements)
# 參考 MOIRA (BahnAstro/MOIRA_chinese_astrology) 五行分配
# 索引對應西方星座: 0=白羊, 1=金牛, ..., 11=雙魚
# ============================================================
ZODIAC_SIGN_ELEMENTS = [
    "火",   # 白羊 (Aries) — fire
    "金",   # 金牛 (Taurus) — metal
    "水",   # 雙子 (Gemini) — water
    "月",   # 巨蟹 (Cancer) — moon
    "日",   # 獅子 (Leo) — sun
    "水",   # 處女 (Virgo) — water
    "金",   # 天秤 (Libra) — metal
    "火",   # 天蠍 (Scorpio) — fire
    "木",   # 射手 (Sagittarius) — wood
    "土",   # 摩羯 (Capricorn) — earth
    "土",   # 水瓶 (Aquarius) — earth
    "木",   # 雙魚 (Pisces) — wood
]
