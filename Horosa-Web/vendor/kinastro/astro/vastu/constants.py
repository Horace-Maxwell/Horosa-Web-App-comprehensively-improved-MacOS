"""
astro/vastu/constants.py — Vastu Shastra 靜態方位常數

包含：
  - 8 主方位（DIRECTIONS_8）
  - 8 子方位（DIRECTIONS_SUB8）
  - 行星 → 方位對應（PLANET_ZONE）
  - 行星 Unicode 符號（PLANET_SYMBOL）
  - 32 外環 Pada 天神（OUTER_PADAS）
  - 9 內部宮格區域（INNER_ZONES）
  - 各種顏色映射

資料來源：Mayamata、Bṛhat Saṃhitā、Manasara 吠陀建築典籍。
"""

from __future__ import annotations

# ── 行星 → Vastu 方位區域（英文代碼） ─────────────────────
PLANET_ZONE: dict[str, str] = {
    "Sun":     "E",
    "Moon":    "NW",
    "Mars":    "S",
    "Mercury": "N",
    "Jupiter": "NE",
    "Venus":   "SE",
    "Saturn":  "W",
    "Rahu":    "SW",
    "Ketu":    "SW",
}

# ── 行星 Unicode 占星符號 ─────────────────────────────────
PLANET_SYMBOL: dict[str, str] = {
    "Sun":     "☉",
    "Moon":    "☽",
    "Mars":    "♂",
    "Mercury": "☿",
    "Jupiter": "♃",
    "Venus":   "♀",
    "Saturn":  "♄",
    "Rahu":    "☊",
    "Ketu":    "☋",
}

# ── 行星中文短名 ──────────────────────────────────────────
PLANET_ZH_SHORT: dict[str, str] = {
    "Sun":     "日",
    "Moon":    "月",
    "Mars":    "火",
    "Mercury": "水",
    "Jupiter": "木",
    "Venus":   "金",
    "Saturn":  "土",
    "Rahu":    "羅",
    "Ketu":    "計",
}

# ── 行星 → 中文全名（含梵文音譯） ───────────────────────
PLANET_ZH: dict[str, str] = {
    "Sun":     "太陽 (Sūrya)",
    "Moon":    "月亮 (Chandra)",
    "Mars":    "火星 (Maṅgala)",
    "Mercury": "水星 (Budha)",
    "Jupiter": "木星 (Bṛhaspati)",
    "Venus":   "金星 (Śukra)",
    "Saturn":  "土星 (Śani)",
    "Rahu":    "羅睺 (Rāhu)",
    "Ketu":    "計都 (Ketu)",
}

# ── 行星 → Vastu 方位全稱 ─────────────────────────────────
PLANET_DIRECTION: dict[str, str] = {
    "Sun":     "東方 (East)",
    "Moon":    "西北 (North-West)",
    "Mars":    "南方 (South)",
    "Mercury": "北方 (North)",
    "Jupiter": "東北 (North-East)",
    "Venus":   "東南 (South-East)",
    "Saturn":  "西方 (West)",
    "Rahu":    "西南 (South-West)",
    "Ketu":    "西南偏南 (South-SouthWest)",
}

# ── 方位代碼 → 中文名稱 ───────────────────────────────────
ZONE_NAMES_ZH: dict[str, str] = {
    "N":  "北方",
    "NE": "東北",
    "E":  "東方",
    "SE": "東南",
    "S":  "南方",
    "SW": "西南",
    "W":  "西方",
    "NW": "西北",
}

# ── 房屋朝向選項（8 方位 + 精確度數） ───────────────────
FACING_OPTIONS_8: list[tuple[str, str, float]] = [
    # (代碼, 中文名稱, 中心角度)
    ("N",  "北方 (North)",      0.0),
    ("NE", "東北 (North-East)", 45.0),
    ("E",  "東方 (East)",       90.0),
    ("SE", "東南 (South-East)", 135.0),
    ("S",  "南方 (South)",      180.0),
    ("SW", "西南 (South-West)", 225.0),
    ("W",  "西方 (West)",       270.0),
    ("NW", "西北 (North-West)", 315.0),
]

# ── 星座 → 主宰行星 ───────────────────────────────────────
LAGNA_RULER: dict[str, str] = {
    "Aries":       "Mars",
    "Taurus":      "Venus",
    "Gemini":      "Mercury",
    "Cancer":      "Moon",
    "Leo":         "Sun",
    "Virgo":       "Mercury",
    "Libra":       "Venus",
    "Scorpio":     "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn":   "Saturn",
    "Aquarius":    "Saturn",
    "Pisces":      "Jupiter",
}

# ── 星座 → 中文名稱 ───────────────────────────────────────
ZODIAC_ZH: dict[str, str] = {
    "Aries":       "牡羊座 (Meṣa)",
    "Taurus":      "金牛座 (Vṛṣabha)",
    "Gemini":      "雙子座 (Mithuna)",
    "Cancer":      "巨蟹座 (Karkaṭa)",
    "Leo":         "獅子座 (Siṃha)",
    "Virgo":       "處女座 (Kanyā)",
    "Libra":       "天秤座 (Tulā)",
    "Scorpio":     "天蠍座 (Vṛścika)",
    "Sagittarius": "射手座 (Dhanus)",
    "Capricorn":   "摩羯座 (Makara)",
    "Aquarius":    "水瓶座 (Kumbha)",
    "Pisces":      "雙魚座 (Mīna)",
}

# ── 星座 → 五大元素屬性 ───────────────────────────────────
SIGN_ELEMENT: dict[str, str] = {
    "Aries":       "火",
    "Taurus":      "土",
    "Gemini":      "風",
    "Cancer":      "水",
    "Leo":         "火",
    "Virgo":       "土",
    "Libra":       "風",
    "Scorpio":     "水",
    "Sagittarius": "火",
    "Capricorn":   "土",
    "Aquarius":    "風",
    "Pisces":      "水",
}

# ── 方位 → 外環背景色（淡） ───────────────────────────────
ZONE_COLORS_OUTER: dict[str, str] = {
    "NW": "#E8F5E9",
    "N":  "#E3F2FD",
    "NE": "#F3E5F5",
    "E":  "#FFF3E0",
    "SE": "#FBE9E7",
    "S":  "#EFEBE9",
    "SW": "#E8E0D8",
    "W":  "#E1F5FE",
}

# ── 方位 → 內部宮格背景色（飽和） ────────────────────────
ZONE_COLORS_INNER: dict[str, str] = {
    "NW":     "#C8E6C9",
    "N":      "#BBDEFB",
    "NE":     "#E1BEE7",
    "E":      "#FFE0B2",
    "SE":     "#FFCCBC",
    "S":      "#D7CCC8",
    "SW":     "#BCAAA4",
    "W":      "#B3E5FC",
    "Center": "#FFF9C4",
}

# ── 32 外環格天神 Pada ─────────────────────────────────────
# (row_0based, col_0based, sanskrit_name, chinese_name, zone_key)
OUTER_PADAS: list[tuple[int, int, str, str, str]] = [
    # 北側（頂行，左=西北 → 右=東北）
    (0, 0, "Roga",        "羅伽",   "NW"),
    (0, 1, "Nāga",        "那伽",   "N"),
    (0, 2, "Mukhya",      "穆克耶", "N"),
    (0, 3, "Bhallāṭa",    "跋羅陀", "N"),
    (0, 4, "Soma",        "蘇摩",   "N"),
    (0, 5, "Bhujaga",     "蛇神",   "N"),
    (0, 6, "Aditi",       "阿底提", "N"),
    (0, 7, "Diti",        "底提",   "N"),
    (0, 8, "Āpa",         "水天",   "NE"),
    # 東側（右列，行 1→7）
    (1, 8, "Āpavatsa",    "水子",   "E"),
    (2, 8, "Parjanya",    "雨神",   "E"),
    (3, 8, "Jayanta",     "勝天",   "E"),
    (4, 8, "Indra",       "因陀羅", "E"),
    (5, 8, "Sūrya",       "太陽",   "E"),
    (6, 8, "Satya",       "薩提耶", "E"),
    (7, 8, "Bhṛśa",       "布利沙", "E"),
    # 南側（底行，右=東南 → 左=西南）
    (8, 8, "Antarikṣa",   "虛空天", "SE"),
    (8, 7, "Agni",        "火神",   "S"),
    (8, 6, "Pūṣan",       "布善",   "S"),
    (8, 5, "Vitatha",     "維塔塔", "S"),
    (8, 4, "Gṛhakṣata",   "護宅",   "S"),
    (8, 3, "Yama",        "閻摩",   "S"),
    (8, 2, "Gandharva",   "乾闥婆", "S"),
    (8, 1, "Bhṛṅgarāja",  "蜂王",   "S"),
    (8, 0, "Mṛga",        "鹿神",   "SW"),
    # 西側（左列，行 7→1）
    (7, 0, "Pitṛgaṇa",    "祖靈",   "W"),
    (6, 0, "Dauvārika",   "門神",   "W"),
    (5, 0, "Sugrīva",     "善頸",   "W"),
    (4, 0, "Puṣpadanta",  "花齒",   "W"),
    (3, 0, "Varuṇa",      "水神",   "W"),
    (2, 0, "Asura",       "阿修羅", "W"),
    (1, 0, "Śoṣa",        "乾燥神", "W"),
]

# ── 9 內部宮格區域 ────────────────────────────────────────
# (zone_key, zh_label, deity_zh, element, vastu_tip, css_grid_row, css_grid_col)
INNER_ZONES: list[tuple[str, str, str, str, str, str, str]] = [
    ("NW",     "西北\nVāyavya",        "風神 Vāyu",      "風", "客房·車庫",   "2/4", "2/4"),
    ("N",      "北方\nUttara",          "財神 Kubera",    "水", "財位·客廳",   "2/4", "4/7"),
    ("NE",     "東北\nĪśānya",          "伊舍那天",       "空", "祈禱·冥想",   "2/4", "7/9"),
    ("W",      "西方\nPaścima",         "水神 Varuṇa",    "水", "餐廳·學習",   "4/7", "2/4"),
    ("Center", "中央\nBrahmasthan",     "梵天 Brahmā",    "以太","保持空曠",   "4/7", "4/7"),
    ("E",      "東方\nPūrva",           "天帝 Indra",     "火", "起居·窗戶",   "4/7", "7/9"),
    ("SW",     "西南\nNairṛtya",        "尼律提 Nirṛti",  "土", "主臥·重物",   "7/9", "2/4"),
    ("S",      "南方\nDakṣiṇa",        "閻摩 Yama",      "土", "臥室·儲藏",   "7/9", "4/7"),
    ("SE",     "東南\nĀgneya",          "火神 Agni",      "火", "廚房·電器",   "7/9", "7/9"),
]

# ── 上升星座 → 推薦房屋朝向 ──────────────────────────────
LAGNA_FACING: dict[str, str] = {
    "Aries":       "東方 — 火象上升適合迎接晨曦能量",
    "Taurus":      "北方 — 金牛上升需穩定財運能量",
    "Gemini":      "北方 — 風象上升適合北方流動能量",
    "Cancer":      "西北（最佳）或東方（次佳）— 月亮主宰巨蟹，西北為月亮方位",
    "Leo":         "東方 — 太陽主宰，面東迎日最吉",
    "Virgo":       "北方 — 水星主宰，北方為水星方位",
    "Libra":       "西方 — 金星主宰，西方為社交方位",
    "Scorpio":     "南方 — 火星主宰，南方能量穩固",
    "Sagittarius": "東北 — 木星主宰，東北為最靈性方位",
    "Capricorn":   "西方或南方 — 土星主宰，沉穩方位為佳",
    "Aquarius":    "西方或北方 — 土星共主，風象需流動空間",
    "Pisces":      "東北 — 木星主宰，靈性能量最強方位",
}

# ── 月亮元素 → 額外 Vastu 建議 ──────────────────────────
MOON_ELEMENT_TIPS: dict[str, str] = {
    "火": (
        "月亮在火象星座：情緒充滿樂觀、探索與行動力。"
        "適合在東北方或東方加強活力空間，顏色以暖色調（金色、橙黃、赤銅色）為主。"
        "避免過度沉重陰暗的裝飾，保持空間開闊明亮以呼應火象能量。"
    ),
    "土": (
        "月亮在土象星座：情緒穩定，適合在西南方加強根基能量。"
        "可在北方放置綠色植物增添生機。家中宜多使用天然石材與木質材料。"
    ),
    "風": (
        "月亮在風象星座：思緒活躍，需在北方設置安靜的閱讀或冥想空間。"
        "避免家中過多的風鈴或流動裝飾。東北方可放置水晶以穩定心智。"
    ),
    "水": (
        "月亮在水象星座：直覺敏銳但情緒起伏大，東北方的祈禱室對您格外重要。"
        "西北方可放置銀色或白色物品以安撫月亮能量。避免家中有漏水或積水現象。"
    ),
}

# ── Vastu Compliance Score — 方位評分基準 ────────────────
# 各方位的「吉利性」基準分（0–100），加總後計算符合度
ZONE_BASE_SCORE: dict[str, float] = {
    "NE": 95.0,  # 最吉祥，靈性之門
    "N":  90.0,  # 財神方位
    "E":  85.0,  # 太陽方位，知識與健康
    "NW": 75.0,  # 風神方位，過渡空間
    "SE": 70.0,  # 火神方位，廚房最佳
    "W":  65.0,  # 水神方位，社交
    "SW": 60.0,  # 穩定但需謹慎
    "S":  55.0,  # 需保持厚重
}
