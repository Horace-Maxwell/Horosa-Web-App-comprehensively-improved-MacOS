"""
巴厘傳統 Wariga 常量定義 (Constants for Balinese Wariga Calendar System)

定義巴厘傳統曆法中使用的所有 Wuku、Wewaran、Neptu/Urip 數值表格。
所有數值嚴格依照古典 Lontar Wariga / Dasar Wariga 傳統規則硬編碼，
不使用任何現代天文簡化公式或近似值。

古法依據：Lontar Wariga / Dasar Wariga
"""

# ============================================================
# 基準日 (Epoch) — 1969年12月31日（星期三）= Wuku Sinta 第1天
# 巴厘傳統 Pawukon 210 天週期的計算基準
# 依據傳統文獻，此日為已知的 Wuku Sinta 起點
# ============================================================
EPOCH_YEAR = 1969
EPOCH_MONTH = 12
EPOCH_DAY = 31

# ============================================================
# 210天 Pawukon 週期中的 30 個 Wuku
# 每個 Wuku 持續 7 天，30 × 7 = 210 天
# 格式：(名稱, Neptu/Urip 值)
# 古法依據：Lontar Wariga — Wuku Neptu 表
# ============================================================
WUKU_TABLE = [
    ("Sinta",       7),
    ("Landep",      1),
    ("Ukir",        4),
    ("Kulantir",    6),
    ("Tolu",        5),
    ("Gumbreg",     8),
    ("Wariga",      9),
    ("Warigadian",  3),
    ("Julungwangi", 7),
    ("Sungsang",    1),
    ("Dungulan",    4),
    ("Kuningan",    6),
    ("Langkir",     5),
    ("Medangsia",   8),
    ("Pujut",       9),
    ("Pahang",      3),
    ("Krulut",      7),
    ("Merakih",     1),
    ("Tambir",      4),
    ("Medangkungan", 6),
    ("Matal",       5),
    ("Uye",         8),
    ("Menail",      9),
    ("Prangbakat",  3),
    ("Bala",        7),
    ("Ugu",         1),
    ("Wayang",      4),
    ("Klawu",       6),
    ("Dukut",       5),
    ("Watugunung",  8),
]

# ============================================================
# Eka Wara (1 天週期) — 只有一個值，不分日
# 古法依據：Lontar Wariga — Eka Wara 表
# ============================================================
EKA_WARA = [
    ("Luang", 1),
]

# ============================================================
# Dwi Wara (2 天週期)
# 古法依據：Lontar Wariga — Dwi Wara 表
# ============================================================
DWI_WARA = [
    ("Menga",  0),
    ("Pepet",  5),
]

# ============================================================
# Tri Wara (3 天週期)
# 古法依據：Lontar Wariga — Tri Wara 表
# ============================================================
TRI_WARA = [
    ("Pasah",   9),
    ("Beteng",  4),
    ("Kajeng",  7),
]

# ============================================================
# Catur Wara (4 天週期)
# 注意：非線性取模，第6、7天特殊處理（Jaya 和 Menala 跳過）
# 古法依據：Lontar Wariga — Catur Wara 表
# ============================================================
CATUR_WARA = [
    ("Sri",    6),
    ("Laba",   5),
    ("Jaya",   1),
    ("Menala", 8),
]

# ============================================================
# Panca Wara (5 天週期)
# 古法依據：Lontar Wariga — Panca Wara Urip 表
# ============================================================
PANCA_WARA = [
    ("Umanis",  5),
    ("Paing",   9),
    ("Pon",     7),
    ("Wage",    4),
    ("Kliwon",  8),
]

# ============================================================
# Sad Wara (6 天週期)
# 古法依據：Lontar Wariga — Sad Wara 表
# ============================================================
SAD_WARA = [
    ("Tungleh",  7),
    ("Aryang",   6),
    ("Urukung",  5),
    ("Paniron",  8),
    ("Was",      9),
    ("Maulu",    3),
]

# ============================================================
# Sapta Wara (7 天週期) — 星期
# 古法依據：Lontar Wariga — Sapta Wara Urip 表
# ============================================================
SAPTA_WARA = [
    ("Redite",      5),   # 星期日 (Sunday)
    ("Soma",        4),   # 星期一 (Monday)
    ("Anggara",     3),   # 星期二 (Tuesday)
    ("Buda",        7),   # 星期三 (Wednesday)
    ("Wraspati",    8),   # 星期四 (Thursday)
    ("Sukra",       6),   # 星期五 (Friday)
    ("Saniscara",   9),   # 星期六 (Saturday)
]

# ============================================================
# Asta Wara (8 天週期)
# 注意：非線性取模，第6、7、8天特殊處理
# （Kala 跳過 Wuku 的第6天，因此需要特殊偏移規則）
# 古法依據：Lontar Wariga — Asta Wara 表
# ============================================================
ASTA_WARA = [
    ("Sri",        6),
    ("Indra",      5),
    ("Guru",       8),
    ("Yama",       9),
    ("Ludra",      3),
    ("Brahma",     7),
    ("Kala",       1),
    ("Uma",        4),
]

# ============================================================
# Sanga Wara (9 天週期)
# 注意：非線性取模，特殊跳過規則
# 古法依據：Lontar Wariga — Sanga Wara 表
# ============================================================
SANGA_WARA = [
    ("Dangu",       5),
    ("Jangur",      8),
    ("Gigis",       9),
    ("Nohan",       3),
    ("Ogan",        7),
    ("Erangan",     1),
    ("Urungan",     4),
    ("Tulus",       6),
    ("Dadi",        8),
]

# ============================================================
# Dasa Wara (10 天週期)
# 取模方式：(Panca Wara Urip + Sapta Wara Urip) mod 10
# 即由 Panca Wara 和 Sapta Wara 的組合計算
# 古法依據：Lontar Wariga — Dasa Wara 表
# ============================================================
DASA_WARA = [
    ("Pandita",   5),
    ("Pati",      7),
    ("Suka",     10),
    ("Duka",      4),
    ("Sri",       6),
    ("Manuh",     2),
    ("Manusa",    3),
    ("Raja",      8),
    ("Dewa",      9),
    ("Raksasa",   1),
]

# ============================================================
# Ingkel（5 類動物分類，42 天為一週期，每類持續 7 天 × 6 = 42 天？）
# 實際上 Ingkel 以 Wuku 為基準，每 6 個 Wuku 一組
# 古法依據：Lontar Wariga — Ingkel 分類表
# ============================================================
INGKEL = [
    "Wong",      # 人 (0-5 Wuku)
    "Sato",      # 獸 (6-11 Wuku)
    "Mina",      # 魚 (12-17 Wuku)
    "Manuk",     # 鳥 (18-23 Wuku)
    "Taru",      # 樹 (24-29 Wuku)
]

# ============================================================
# Watek（兩組：Watek Alit 4類 和 Watek Madya 5類）
# 古法依據：Lontar Wariga
# ============================================================
WATEK_ALIT = [
    "Lembut",
    "Mider",
    "Uler",
    "Gajah",
]

WATEK_MADYA = [
    "Wong",
    "Suku Empat",
    "Paksi",
    "Ikan (Mina)",
    "Taru",
]

# ============================================================
# Pawatekan — Wuku 對應的 Watek Alit 和 Watek Madya 索引
# 格式：(Watek Alit 索引, Watek Madya 索引)
# 古法依據：Lontar Wariga — Pawatekan 對照表
# ============================================================
PAWATEKAN = [
    (3, 0),  # Sinta       → Gajah, Wong
    (2, 1),  # Landep      → Uler, Suku Empat
    (1, 2),  # Ukir        → Mider, Paksi
    (0, 3),  # Kulantir    → Lembut, Ikan
    (3, 4),  # Tolu        → Gajah, Taru
    (2, 0),  # Gumbreg     → Uler, Wong
    (1, 1),  # Wariga      → Mider, Suku Empat
    (0, 2),  # Warigadian  → Lembut, Paksi
    (3, 3),  # Julungwangi → Gajah, Ikan
    (2, 4),  # Sungsang    → Uler, Taru
    (1, 0),  # Dungulan    → Mider, Wong
    (0, 1),  # Kuningan    → Lembut, Suku Empat
    (3, 2),  # Langkir     → Gajah, Paksi
    (2, 3),  # Medangsia   → Uler, Ikan
    (1, 4),  # Pujut       → Mider, Taru
    (0, 0),  # Pahang      → Lembut, Wong
    (3, 1),  # Krulut      → Gajah, Suku Empat
    (2, 2),  # Merakih     → Uler, Paksi
    (1, 3),  # Tambir      → Mider, Ikan
    (0, 4),  # Medangkungan→ Lembut, Taru
    (3, 0),  # Matal       → Gajah, Wong
    (2, 1),  # Uye         → Uler, Suku Empat
    (1, 2),  # Menail      → Mider, Paksi
    (0, 3),  # Prangbakat  → Lembut, Ikan
    (3, 4),  # Bala        → Gajah, Taru
    (2, 0),  # Ugu         → Uler, Wong
    (1, 1),  # Wayang      → Mider, Suku Empat
    (0, 2),  # Klawu       → Lembut, Paksi
    (3, 3),  # Dukut       → Gajah, Ikan
    (2, 4),  # Watugunung  → Uler, Taru
]

# ============================================================
# Lintang（35 星宿，與 Wuku 日相關的星座分類）
# Pawukon 日序 mod 35 → 對應一個 Lintang
# 共 35 個 Lintang（取模 35）
# 古法依據：Lontar Wariga — Lintang 表
# ============================================================
LINTANG = [
    "Kartika",          # 0
    "Sungsang",         # 1
    "Uluku (Waluku)",   # 2 — Orion/犁星
    "Lumbung",          # 3
    "Kumba",            # 4
    "Udang",            # 5
    "Asu",              # 6
    "Begoong",          # 7
    "Tiruan (Magelut)", # 8
    "Sangka Tikel",     # 9
    "Bubu Bolong",      # 10
    "Sugenge (Sungenge)", # 11
    "Tangis",           # 12
    "Salah Ukur",       # 13
    "Perahu Pegat",     # 14
    "Puwuh Atarung",    # 15
    "Lair",             # 16
    "Kelapa (Klapa)",   # 17
    "Yuyu",             # 18
    "Lontong",          # 19
    "Udan (Angsa)",     # 20
    "Pedati",           # 21
    "Megantung (Kuda)", # 22
    "Bade (Mangelut)",  # 23
    "Macan (Harimau)",  # 24
    "Lembu",            # 25
    "Jaran (Kuda)",     # 26
    "Ikan",             # 27
    "Panah",            # 28
    "Patrem",           # 29
    "Lembu",            # 30
    "Buku Sema (Gelung Naga)", # 31
    "Dasba (Swamba)",   # 32
    "Mintuna",          # 33
    "Naga Ngadeg",      # 34
]

# ============================================================
# Sasih（巴厘傳統 12 個月，基於陰陽合曆）
# 古法依據：Lontar Wariga — Sasih 表
# ============================================================
SASIH_NAMES = [
    "Kasa",         # 1  — 約格里高利曆 7月
    "Karo",         # 2  — 約 8月
    "Katiga",       # 3  — 約 9月
    "Kapat",        # 4  — 約 10月
    "Kalima",       # 5  — 約 11月
    "Kanem",        # 6  — 約 12月
    "Kapitu",       # 7  — 約 1月
    "Kawolu",       # 8  — 約 2月
    "Kasanga",      # 9  — 約 3月
    "Kadasa",       # 10 — 約 4月
    "Desta",        # 11 — 約 5月
    "Sada",         # 12 — 約 6月
]

# ============================================================
# 季節 (Kala / Season)
# 巴厘傳統分為兩大季節：
# - Lahru (乾季/Kemarau) — Sasih Kasa (1) 到 Kanem (6)
# - Rengreng (雨季/Penghujan) — Sasih Kapitu (7) 到 Sada (12)
#
# Ayana（太陽行程）：
# - Uttarayana（北行，太陽北移）— 約 Sasih Kapitu (7) 到 Sada (12)
# - Dakshinayana（南行，太陽南移）— 約 Sasih Kasa (1) 到 Kanem (6)
#
# 古法依據：Lontar Wariga — 季節劃分
# ============================================================
SEASON_LAHRU_RANGE = (1, 6)    # Sasih 1-6: 乾季 (Lahru / Kemarau)
SEASON_RENGRENG_RANGE = (7, 12)  # Sasih 7-12: 雨季 (Rengreng / Penghujan)

# ============================================================
# Dewasa Ayu (吉日) 與 Dewasa Ala (凶日) 規則
# 傳統判斷日期好壞的基本規則，基於 Wewaran 組合
#
# 常見吉日組合 (Dewasa Ayu)：
#   - Sapta Wara Neptu + Panca Wara Neptu 合計為特定值
#   - 某些 Wuku + Wara 的固定組合被視為大吉
#
# 常見凶日組合 (Dewasa Ala)：
#   - Kajeng Kliwon（Tri Wara Kajeng + Panca Wara Kliwon）= 大忌日
#   - Anggara Kasih（Sapta Wara Anggara + Panca Wara Kliwon）= 火曜凶日
#   - 特定的 Neptu 總和為凶數
#
# 古法依據：Lontar Wariga — Dewasa Ayu / Ala 章節
# ============================================================

# 吉日條件列表 — (名稱, 描述, 判斷函數名)
DEWASA_AYU_RULES = [
    ("Dewasa Ayu",
     "Panca Wara + Sapta Wara Neptu 總和 ≤ 9，且不在凶日列表中",
     "check_dewasa_ayu"),
    ("Beteng (均衡日)",
     "Tri Wara = Beteng 的日子，主平衡穩定",
     "check_beteng"),
]

# 凶日條件列表 — (名稱, 印尼名, 描述)
DEWASA_ALA_RULES = [
    ("Kajeng Kliwon",
     "Kajeng Kliwon",
     "Tri Wara=Kajeng + Panca Wara=Kliwon 之日，忌一切重要活動"),
    ("Anggara Kasih",
     "Anggara Kasih",
     "Sapta Wara=Anggara + Panca Wara=Kliwon 之日，火曜凶日"),
    ("Buda Cemeng",
     "Buda Cemeng",
     "Sapta Wara=Buda + Panca Wara=Kliwon 之日，水曜凶日"),
    ("Tumpek",
     "Tumpek",
     "Sapta Wara=Saniscara + Panca Wara=Kliwon 之日，土曜特殊日（某些類別視為吉）"),
    ("Buda Kliwon Pahang",
     "Buda Kliwon Pahang",
     "Buda+Kliwon 在 Wuku Pahang，大凶"),
]

# ============================================================
# Pancasuda — 由 Panca Wara Urip + Sapta Wara Urip 決定
# 總和 mod 7 → 7 種結果
# 古法依據：Lontar Wariga — Pancasuda 表
# ============================================================
PANCASUDA = [
    ("Wisesa Segara",   "如大海般的智慧力量"),    # 0 (mod 7)
    ("Tunggak Semi",    "枯木逢春，否極泰來"),    # 1
    ("Satria Wibawa",   "武士之威，尊貴高尚"),    # 2
    ("Sumur Sinaba",    "被棄之井，孤獨落寞"),    # 3
    ("Satria Wirang",   "武士之恥，受辱遭難"),    # 4
    ("Bumi Kapetak",    "大地開裂，基礎動搖"),    # 5
    ("Lebu Katiup Angin", "塵土隨風，飄搖不定"),  # 6
]

# ============================================================
# Eka Jala Rsi — 由 Eka Wara 計算得出
# 用於判斷靈性品質
# 古法依據：Lontar Wariga
# ============================================================
EKA_JALA_RSI = [
    ("Bagna Mapasah",   "分離之水，心靈清淨"),   # Eka Wara = Luang
]

# ============================================================
# 吉凶 Neptu 總和閾值
# 傳統上認為 Panca + Sapta Neptu 合計數值的吉凶分界
# 古法依據：Dasar Wariga
# ============================================================
NEPTU_SUM_AUSPICIOUS_MAX = 9    # Neptu 合計 ≤ 9 視為吉
NEPTU_SUM_INAUSPICIOUS_MIN = 10  # Neptu 合計 ≥ 10 需進一步審查

# ============================================================
# Catur Wara 特殊取模規則
# 在 210 天週期中，Catur Wara 的索引不是簡單的 day % 4
# 而是需要跳過特定日數（第 70 天和第 71 天重複 Jaya 和 Menala）
# 古法依據：Lontar Wariga — Catur Wara 排序法
# ============================================================
# Catur Wara 索引表：按 Pawukon day (0-209) 對應
# 簡化規則：day_in_pawukon 先去除特殊偏移後取 mod 4
CATUR_WARA_SKIP_DAYS = {70, 71}

# ============================================================
# Asta Wara 特殊取模規則
# 類似 Catur Wara，Asta Wara 也有跳過規則
# 在 Pawukon 週期中的第 0、6、7 天有特殊處理
# 古法依據：Lontar Wariga — Asta Wara 排序法
# ============================================================
# Asta Wara 的索引計算不使用簡單的 day % 8
# 而是使用修正後的日序

# ============================================================
# Sanga Wara 特殊取模規則
# Sanga Wara 同樣非簡單 day % 9
# 古法依據：Lontar Wariga — Sanga Wara 排序法
# ============================================================

# ============================================================
# Gregorian ↔ Pawukon 日數差
# 從 epoch (1969-12-31) 到目標日期的天數 mod 210
# 即可得到在 Pawukon 週期中的位置
# ============================================================
PAWUKON_CYCLE = 210

# ============================================================
# Panca Dauh — 5 時辰劃分（每 Dauh 約 4.8 小時）
# 巴厘傳統將一日分為 5 個 Dauh，每 Dauh 歸屬特定神明
# 格式：(名稱, 起始小時(含), 終止小時(不含), 神明/主宰, 吉凶, 說明)
# 範圍使用半開區間 [start, end)，無邊界重疊
# 古法依據：Lontar Wariga — Panca Dauh 時辰表
# ============================================================
PANCA_DAUH = [
    ("Pagi",       0,   6,  "Dewa Surya",    "中性", "日出前，萬物甦醒"),
    ("Tengai",     6,  11,  "Dewa Brahma",   "吉",   "上午，創造之時"),
    ("Tangeh",    11,  16,  "Dewa Wisnu",    "吉",   "正午，維護之時"),
    ("Sandikala", 16,  20,  "Dewa Siwa",     "凶",   "黃昏，轉化之時"),
    ("Wengi",     20,  24,  "Dewa Yama",     "凶",   "夜間，靜思之時"),
]

# ============================================================
# Asta Dauh — 8 時辰劃分（每 Dauh 3 小時）
# 更精細的時辰系統，嚴格按照 Lontar Wariga Gemet 傳統
# 格式：(名稱, 起始小時(含), 終止小時(不含), 方位, 吉凶, 說明)
# 範圍使用半開區間 [start, end)，無邊界重疊
# 古法依據：Lontar Wariga Gemet — Asta Dauh 時辰劃分
# ============================================================
ASTA_DAUH = [
    ("Pagi",        0,  3,  "Timur",        "中性",  "黎明前，Dewa Iswara 方，宜靜修"),
    ("Kala Pagi",   3,  6,  "Tenggara",     "凶",    "Dewa Maheswara 方，忌出行"),
    ("Tengai",      6,  9,  "Selatan",      "吉",    "Dewa Brahma 方，宜開始重要事"),
    ("Kala Tengai", 9, 12,  "Barat Daya",   "凶",    "Dewa Rudra 方，忌簽約"),
    ("Tangeh",     12, 15,  "Barat",        "吉",    "Dewa Mahadewa 方，宜農耕"),
    ("Kala Tangeh",15, 18,  "Barat Laut",   "凶",    "Dewa Sangkara 方，忌動土"),
    ("Sandikala",  18, 21,  "Utara",        "中性",  "Dewa Wisnu 方，宜祭祀"),
    ("Wengi",      21, 24,  "Timur Laut",   "凶",    "Dewa Sambu 方，宜休息"),
]

# ============================================================
# Penanggal — 月盈期 (1-15)，從新月到滿月
# 格式：(序號, 巴厘名稱, 梵語名, Neptu/Urip)
# 古法依據：Lontar Wariga — Penanggal 數值表
# ============================================================
PENANGGAL_NAMES = [
    (1,  "Penanggal Ping Pisan",   "Pratipada",  5),
    (2,  "Penanggal Ping Dua",     "Dvitiya",    4),
    (3,  "Penanggal Ping Tiga",    "Tritiya",    3),
    (4,  "Penanggal Ping Empat",   "Caturthi",   7),
    (5,  "Penanggal Ping Lima",    "Pancami",    1),
    (6,  "Penanggal Ping Enam",    "Sashti",     8),
    (7,  "Penanggal Ping Pitu",    "Saptami",    9),
    (8,  "Penanggal Ping Wolu",    "Ashtami",    6),
    (9,  "Penanggal Ping Songo",   "Navami",     5),
    (10, "Penanggal Ping Dasa",    "Dashami",    4),
    (11, "Penanggal Ping Sewelas", "Ekadashi",   3),
    (12, "Penanggal Ping Rolas",   "Dvadashi",   7),
    (13, "Penanggal Ping Telulas", "Trayodashi", 1),
    (14, "Penanggal Ping Pat Blas","Caturdashi", 8),
    (15, "Penanggal Ping Limolas", "Purnama",    9),
]

# ============================================================
# Panglong — 月虧期 (1-15)，從滿月到新月
# 格式：(序號, 巴厘名稱, 梵語名, Neptu/Urip)
# 古法依據：Lontar Wariga — Panglong 數值表
# ============================================================
PANGLONG_NAMES = [
    (1,  "Panglong Ping Pisan",    "Pratipada",  5),
    (2,  "Panglong Ping Dua",      "Dvitiya",    4),
    (3,  "Panglong Ping Tiga",     "Tritiya",    3),
    (4,  "Panglong Ping Empat",    "Caturthi",   7),
    (5,  "Panglong Ping Lima",     "Pancami",    1),
    (6,  "Panglong Ping Enam",     "Sashti",     8),
    (7,  "Panglong Ping Pitu",     "Saptami",    9),
    (8,  "Panglong Ping Wolu",     "Ashtami",    6),
    (9,  "Panglong Ping Songo",    "Navami",     5),
    (10, "Panglong Ping Dasa",     "Dashami",    4),
    (11, "Panglong Ping Sewelas",  "Ekadashi",   3),
    (12, "Panglong Ping Rolas",    "Dvadashi",   7),
    (13, "Panglong Ping Telulas",  "Trayodashi", 1),
    (14, "Panglong Ping Pat Blas", "Caturdashi", 8),
    (15, "Panglong Ping Limolas",  "Tilem",      9),
]

# ============================================================
# 特殊聖日 — Purnama（滿月）與 Tilem（新月）
# 古法依據：Lontar Wariga — 月相聖日
# ============================================================
PURNAMA_TILEM = {
    "Purnama": "滿月聖日（Penanggal 15），宜祈福祭神",
    "Tilem":   "新月聖日（Panglong 15），宜靜修內觀",
}

# ============================================================
# Wuku 符號對應 — 用於傳統視覺呈現
# 格式：(Wuku名稱, 方位神, 顏色, 動物象徵, 吉凶傾向)
# 古法依據：Palalintangan 傳統對應表
# ============================================================
WUKU_ATTRIBUTES = [
    ("Sinta",        "Timur",     "#FF6B6B", "獅子", "大吉"),
    ("Landep",       "Tenggara",  "#4ECDC4", "鹿",   "吉"),
    ("Ukir",         "Selatan",   "#FFE66D", "牛",   "吉"),
    ("Kulantir",     "Barat Daya","#A8E6CF", "孔雀", "中"),
    ("Tolu",         "Barat",     "#FF8B94", "蛇",   "中"),
    ("Gumbreg",      "Barat Laut","#C3A6FF", "象",   "吉"),
    ("Wariga",       "Utara",     "#85E89D", "猴",   "吉"),
    ("Warigadian",   "Timur Laut","#FFC3A0", "鳥",   "中"),
    ("Julungwangi",  "Timur",     "#FF6B6B", "龜",   "大吉"),
    ("Sungsang",     "Tenggara",  "#4ECDC4", "魚",   "凶"),
    ("Dungulan",     "Selatan",   "#FFE66D", "豬",   "中"),
    ("Kuningan",     "Barat Daya","#A8E6CF", "鳳凰", "大吉"),
    ("Langkir",      "Barat",     "#FF8B94", "牛",   "凶"),
    ("Medangsia",    "Barat Laut","#C3A6FF", "鱷魚", "凶"),
    ("Pujut",        "Utara",     "#85E89D", "獅子", "吉"),
    ("Pahang",       "Timur Laut","#FFC3A0", "蜈蚣", "凶"),
    ("Krulut",       "Timur",     "#FF6B6B", "蜘蛛", "凶"),
    ("Merakih",      "Tenggara",  "#4ECDC4", "犀牛", "中"),
    ("Tambir",       "Selatan",   "#FFE66D", "象",   "吉"),
    ("Medangkungan", "Barat Daya","#A8E6CF", "蜜蜂", "吉"),
    ("Matal",        "Barat",     "#FF8B94", "牛",   "中"),
    ("Uye",          "Barat Laut","#C3A6FF", "蝴蝶", "吉"),
    ("Menail",       "Utara",     "#85E89D", "鷹",   "中"),
    ("Prangbakat",   "Timur Laut","#FFC3A0", "蝙蝠", "凶"),
    ("Bala",         "Timur",     "#FF6B6B", "虎",   "凶"),
    ("Ugu",          "Tenggara",  "#4ECDC4", "鸚鵡", "中"),
    ("Wayang",       "Selatan",   "#FFE66D", "猴",   "吉"),
    ("Klawu",        "Barat Daya","#A8E6CF", "蛙",   "中"),
    ("Dukut",        "Barat",     "#FF8B94", "蚯蚓", "凶"),
    ("Watugunung",   "Barat Laut","#C3A6FF", "龍",   "大吉"),
]

# ============================================================
# 完整 Ala Ayuning Dewasa 規則表
# 嚴格依照 Lontar Wariga Dewasa 的傳統吉凶組合
# 格式：(名稱, 觸發條件說明, 吉/凶, Lontar古法描述)
# 古法依據：Lontar Wariga Dewasa
# ============================================================
ALA_AYUNING_DEWASA = [
    # === 吉日 (Dewasa Ayu) ===
    ("Hari Raya Galungan",
     "Wuku Dungulan，Sapta Wara=Buda，Panca Wara=Kliwon",
     "大吉", "天神降臨人間之聖日，宜祭典慶祝"),
    ("Hari Raya Kuningan",
     "Wuku Kuningan，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "大吉", "天神返回天界前最後護佑之日，宜獻供"),
    ("Sugihan Bali",
     "Wuku Sungsang，Sapta Wara=Saniscara",
     "吉", "淨化巴厘島大地之日，宜清掃祭所"),
    ("Sugihan Jawa",
     "Wuku Sungsang，Sapta Wara=Wraspati",
     "吉", "淨化自身靈魂之日，宜沐浴冥想"),
    ("Purnama",
     "月相=滿月（Penanggal 15）",
     "大吉", "滿月聖日，宜祈福禱告，忌不潔之事"),
    ("Buda Cemeng Klawu",
     "Wuku Klawu，Sapta Wara=Buda，Panca Wara=Kliwon",
     "吉", "依 Lontar Wariga，此日宜靜心修行"),
    ("Tumpek Landep",
     "Wuku Landep，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "吉", "祝福器具、武器之日，宜磨刀器"),
    ("Tumpek Uduh",
     "Wuku Wariga，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "吉", "祝福植物、農作之日，宜種植"),
    ("Tumpek Kuningan",
     "Wuku Kuningan，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "大吉", "祖靈降臨之日，宜祭拜先祖"),
    ("Tumpek Krulut",
     "Wuku Krulut，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "吉", "祝福音樂藝術之日，宜演奏歌詠"),
    ("Tumpek Kandang",
     "Wuku Uye，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "吉", "祝福牲畜家禽之日，宜照料動物"),
    ("Tumpek Wayang",
     "Wuku Wayang，Sapta Wara=Saniscara，Panca Wara=Kliwon",
     "吉", "祝福皮影藝術之日，宜觀賞 Wayang"),
    # === 凶日 (Dewasa Ala) ===
    ("Kajeng Kliwon",
     "Tri Wara=Kajeng + Panca Wara=Kliwon",
     "凶", "傳統大忌日，惡靈出沒，忌一切重要活動"),
    ("Anggara Kasih",
     "Sapta Wara=Anggara + Panca Wara=Kliwon",
     "凶", "火曜凶日，忌重大決定、訴訟、出行"),
    ("Buda Cemeng",
     "Sapta Wara=Buda + Panca Wara=Kliwon（非 Wuku Klawu）",
     "凶", "水曜凶日，宜謹慎行事，忌簽約"),
    ("Tilem",
     "月相=新月（Panglong 15）",
     "凶", "新月聖日，靈界活躍，忌出行冒險"),
    ("Buda Kliwon Pahang",
     "Wuku Pahang，Sapta Wara=Buda，Panca Wara=Kliwon",
     "大凶", "Lontar 記載最凶之日，萬事皆忌"),
    ("Manis Galungan",
     "Wuku Dungulan，Sapta Wara=Kamis（Wraspati）",
     "中", "Galungan 翌日，宜訪問親友"),
    ("Penampahan Galungan",
     "Wuku Dungulan，Sapta Wara=Anggara",
     "中", "Galungan 前一日，宜準備祭品"),
]

# ============================================================
# Dewasa Ayu 詳細說明 — 各 Wewaran 組合的吉日描述
# 格式：(分類, 傳統活動描述)
# 古法依據：Lontar Wariga Dewasa — 宜事章節
# ============================================================
DEWASA_AYU_ACTIVITIES = {
    "pernikahan":  ("宜婚嫁", "Pahing Umanis、Sukra Umanis、Soma Umanis 為婚嫁吉日"),
    "perniagaan":  ("宜經商", "Wraspati Pon 為最宜開業之日"),
    "pertanian":   ("宜農耕", "Redite Wage 宜播種，Soma Pon 宜收割"),
    "pembangunan": ("宜建築", "Buda Kliwon Sinta 宜動土，Wraspati Pahing 宜上梁"),
    "perjalanan":  ("宜出行", "Sukra Umanis 宜長途旅行"),
    "pengobatan":  ("宜醫療", "Soma Kliwon 宜開始治療"),
}

# ============================================================
# Pangider-ider — 八方位神明（風向玫瑰）
# 巴厘傳統九宮格方位體系，中央 + 八方
# 古法依據：Lontar Wariga — Nawa Sanga（九聖）
# ============================================================
PANGIDER_IDER = {
    "Timur":      ("Dewa Iswara",   "白色", "besi",   "♁"),
    "Tenggara":   ("Dewa Maheswara","pink",  "perak",  "☽"),
    "Selatan":    ("Dewa Brahma",   "Merah", "tembaga","☀"),
    "Barat Daya": ("Dewa Rudra",    "Jingga","besi",   "♂"),
    "Barat":      ("Dewa Mahadewa", "Kuning","emas",   "♃"),
    "Barat Laut": ("Dewa Sangkara", "Hijau", "besi",   "♄"),
    "Utara":      ("Dewa Wisnu",    "Hitam", "besi",   "♆"),
    "Timur Laut": ("Dewa Sambu",    "Biru",  "besi",   "♅"),
    "Tengah":     ("Dewa Siwa",     "Pancawarna","emas","☯"),
}

# ============================================================
# WUKU_DETAILS — 30 個 Wuku 完整性格/宜忌檔案
# 索引與 WUKU_TABLE 對應 (0-29)
# 格式：每條目包含 deity, animal, plant, personality,
#       career, marriage, health, tabu, auspicious_act
# 古法依據：Lontar Palalintangan / Lontar Catur Aji / 傳統巴厘祭司口傳
# ============================================================
WUKU_DETAILS = [
    {   # 0 — Sinta
        "deity": "Hyang Yamadipati", "deity_cn": "亞瑪帝帕提（法官神）",
        "animal": "🦁 獅子", "plant": "🌳 Beringin（榕樹）",
        "personality": "剛毅勇敢、天生領導者，性格急躁衝動，骨子裡仁慈",
        "career": "政治領袖、軍官、運動員、法官",
        "marriage": "與 Wariga、Julungwangi 最相配；忌 Langkir",
        "health": "注意心臟、血壓，宜靜心冥想",
        "tabu": "此週忌興建新房、忌遷葬；勿與 Sungsang 週人衝突",
        "auspicious_act": "宜出征求勝、舉辦慶典、武器祝福（Tumpek Landep）",
        "lucky_day_in_wuku": 1, "color": "#FF6B6B",
    },
    {   # 1 — Landep
        "deity": "Hyang Mahadewa", "deity_cn": "摩訶提婆（偉大之神）",
        "animal": "🦌 鹿", "plant": "🌿 Andong（竹葉蘭）",
        "personality": "思維敏銳、聰慧好學，心靈純淨，但易多慮",
        "career": "學者、研究員、鐵匠、武器製造師、律師",
        "marriage": "與 Kulantir、Medangsia 相配；忌 Pujut",
        "health": "注意神經系統、睡眠品質",
        "tabu": "此週忌動土建房；Tumpek Landep（Saniscara Kliwon）為特殊聖日，宜磨利器具",
        "auspicious_act": "宜學習、淬煉技藝、祝福武器、開啟新計劃",
        "lucky_day_in_wuku": 5, "color": "#4ECDC4",
    },
    {   # 2 — Ukir
        "deity": "Hyang Maheswara", "deity_cn": "摩醯首羅（藝術之神）",
        "animal": "🐂 牛", "plant": "🪵 Pilang（雕刻木）",
        "personality": "藝術天分極高，心靈手巧，性格溫和持重",
        "career": "雕刻師、藝術家、木匠、工程師、建築師",
        "marriage": "與 Wariga、Dungulan 相配；忌 Prangbakat",
        "health": "注意腸胃、脊背；宜規律飲食",
        "tabu": "此週忌辦喪事；忌無故砍伐古樹",
        "auspicious_act": "宜動工建設、開始藝術創作、建房打基礎",
        "lucky_day_in_wuku": 3, "color": "#FFE66D",
    },
    {   # 3 — Kulantir
        "deity": "Hyang Brahma", "deity_cn": "梵天（創造之神）",
        "animal": "🦚 孔雀", "plant": "🌺 Sandat（緬梔花）",
        "personality": "熱情奔放、野心勃勃，富有魅力，但衝動易怒",
        "career": "演員、舞蹈家、教師、政治家、社區領袖",
        "marriage": "與 Landep、Tambir 相配；忌 Krulut",
        "health": "注意情緒管理、肝臟保健；宜練習呼吸法",
        "tabu": "此週忌爭吵訴訟；忌辦葬禮；忌做重大財務決定",
        "auspicious_act": "宜藝術表演、慶典儀式、宣揚善事",
        "lucky_day_in_wuku": 4, "color": "#A8E6CF",
    },
    {   # 4 — Tolu
        "deity": "Hyang Siwa", "deity_cn": "濕婆（靈性之神）",
        "animal": "🐍 蛇", "plant": "🪷 Padma（蓮花）",
        "personality": "內斂深沉、靈性敏銳，充滿神秘感，擅長保守秘密",
        "career": "神職人員、醫師、占卜師、哲學家、靈媒",
        "marriage": "與 Julungwangi、Kuningan 相配；忌 Medangsia",
        "health": "注意腎臟、生殖系統；宜靜坐冥想",
        "tabu": "此週忌遷移新居；忌揭露他人秘密；忌參加凶事後即辦吉事",
        "auspicious_act": "宜靈性修行、學習神聖典籍、治病祛邪",
        "lucky_day_in_wuku": 5, "color": "#FF8B94",
    },
    {   # 5 — Gumbreg
        "deity": "Hyang Sangkara", "deity_cn": "桑卡拉（豐饒之神）",
        "animal": "🐘 象", "plant": "🌳 Nangka（菠蘿蜜樹）",
        "personality": "慷慨大方、生命力旺盛，性格穩重，善於積累財富",
        "career": "農夫、商人、廚師、藥材師、林業工作者",
        "marriage": "與 Wariga、Pujut 相配；忌 Wayang",
        "health": "注意消化系統、體重管理",
        "tabu": "此週忌浪費食物；忌砍伐果樹；Tumpek Uduh 宜祝福植物",
        "auspicious_act": "宜農耕種植、祝福牲畜、儲糧備豐",
        "lucky_day_in_wuku": 6, "color": "#C3A6FF",
    },
    {   # 6 — Wariga
        "deity": "Hyang Wisnu", "deity_cn": "毘濕奴（維護之神）",
        "animal": "🐒 猴", "plant": "🎋 Bambu（竹）",
        "personality": "善良保護者、敏捷機智，對家人忠誠，但有時過於保守",
        "career": "醫療工作者、環保人士、護士、社工、藥劑師",
        "marriage": "與 Sinta、Ukir 最相配；忌 Dukut",
        "health": "注意呼吸系統、過敏；宜在自然中活動",
        "tabu": "此週忌傷害動物；忌砍竹；Tumpek Uduh（Saniscara Kliwon）為植物聖日",
        "auspicious_act": "宜種植、醫療、環保、守護儀式",
        "lucky_day_in_wuku": 4, "color": "#85E89D",
    },
    {   # 7 — Warigadian
        "deity": "Hyang Sambu", "deity_cn": "桑布（吉祥之神）",
        "animal": "🐦 鳥", "plant": "🌾 Padi（稻穗）",
        "personality": "適應力強、靈活多變，樂於助人，但有時優柔寡斷",
        "career": "農業技術員、廚師、教師、旅遊業、翻譯員",
        "marriage": "與 Tolu、Gumbreg 相配；忌 Menail",
        "health": "注意關節、筋骨；宜勤運動",
        "tabu": "此週忌更改既定計劃；忌輕率做決定",
        "auspicious_act": "宜收穫農作物、感恩祭祀、調解糾紛",
        "lucky_day_in_wuku": 1, "color": "#FFC3A0",
    },
    {   # 8 — Julungwangi
        "deity": "Hyang Candra", "deity_cn": "月神（月亮之神）",
        "animal": "🐢 龜", "plant": "🌸 Teratai（睡蓮）",
        "personality": "美麗優雅、情感豐富，直覺敏銳，心地善良且充滿詩意",
        "career": "藝術家、詩人、音樂家、護理師、美容師",
        "marriage": "與 Sinta、Tolu 最相配；忌 Bala",
        "health": "注意心理健康、荷爾蒙平衡；宜在月光下冥想",
        "tabu": "此週忌爭鬥；忌在水邊進行危險活動；Purnama 最忌邪念",
        "auspicious_act": "宜婚嫁、文藝創作、水神祭祀、淨化儀式",
        "lucky_day_in_wuku": 5, "color": "#FF6B6B",
    },
    {   # 9 — Sungsang
        "deity": "Hyang Rudra", "deity_cn": "如陀羅（風暴之神）",
        "animal": "🐟 魚", "plant": "🌿 Pandan（香蘭葉）",
        "personality": "個性強烈、變化莫測，充滿激情，善於變革但也易惹麻煩",
        "career": "改革家、創業者、探險家、消防員、革命者",
        "marriage": "與 Kuningan 相配；忌 Sinta",
        "health": "注意腎上腺、腎臟；宜冥想控制情緒",
        "tabu": "此週忌輕舉妄動；忌辦婚禮；Sugihan Bali（Saniscara）宜大掃除淨化",
        "auspicious_act": "宜大掃除、淨化儀式、清除障礙",
        "lucky_day_in_wuku": 6, "color": "#4ECDC4",
    },
    {   # 10 — Dungulan
        "deity": "Hyang Indra", "deity_cn": "因陀羅（雷神/勝利之神）",
        "animal": "🐗 豬", "plant": "🌿 Ketapang（欖仁樹）",
        "personality": "意志力超強、無所畏懼，勇於面對挑戰，骨子裡善良",
        "career": "武士、競技選手、警察、外科醫師",
        "marriage": "與 Ukir、Medangsia 相配；忌 Pahang",
        "health": "注意關節、膝蓋；宜武術鍛煉",
        "tabu": "此週 Buda Kliwon（Galungan）為最大聖日，萬事皆吉；忌殺生",
        "auspicious_act": "宜舉辦 Galungan 慶典、祈福、驅邪、慶祝勝利",
        "lucky_day_in_wuku": 4, "color": "#FFE66D",
    },
    {   # 11 — Kuningan
        "deity": "Hyang Siwa (Pitara)", "deity_cn": "濕婆（祖靈形態）",
        "animal": "🦅 鳳凰", "plant": "🌻 Bungan Sandat（夜來香）",
        "personality": "高貴純潔、祖靈守護，天生具有靈性感知力，為人正直",
        "career": "神職人員、祭司、靈媒、傳統醫者、教育者",
        "marriage": "與 Tolu、Sungsang 相配；忌 Bala",
        "health": "注意能量場管理，宜定期淨化身體與靈魂",
        "tabu": "此週 Saniscara Kliwon（Kuningan）為最大聖日，宜獻供祖靈；忌世俗娛樂",
        "auspicious_act": "宜祭拜祖先、Kuningan 獻供、靜坐祈福",
        "lucky_day_in_wuku": 6, "color": "#A8E6CF",
    },
    {   # 12 — Langkir
        "deity": "Hyang Kala", "deity_cn": "卡拉（時間/危險之神）",
        "animal": "🐄 牛", "plant": "🌵 Cacah（帶刺植物）",
        "personality": "堅韌不拔但固執，面對逆境能挺過，但容易陷入困境",
        "career": "農民、木匠、勞工、礦工、安全人員",
        "marriage": "與 Pahang 相配（互補）；忌 Sinta",
        "health": "注意骨骼、牙齒；宜補鈣",
        "tabu": "此週萬事宜謹慎；忌冒進；忌大規模動工；為全年最需謹慎的 Wuku 之一",
        "auspicious_act": "宜靜守待機、維護修繕、鞏固基礎",
        "lucky_day_in_wuku": 3, "color": "#FF8B94",
    },
    {   # 13 — Medangsia
        "deity": "Hyang Bayu", "deity_cn": "巴尤（風神）",
        "animal": "🐊 鱷魚", "plant": "🌿 Anggur Laut（海葡萄）",
        "personality": "喜愛自由、天生旅人，行動迅速，思維開闊但難以定居",
        "career": "旅遊業、飛行員、水手、運動員、外交官",
        "marriage": "與 Landep、Dungulan 相配；忌 Tolu",
        "health": "注意呼吸道、肺部；忌過度奔波消耗體力",
        "tabu": "此週忌長途遠行（容易迷失）；忌在水邊輕率行動",
        "auspicious_act": "宜短途旅行、商業拓展、運動競技",
        "lucky_day_in_wuku": 1, "color": "#C3A6FF",
    },
    {   # 14 — Pujut
        "deity": "Hyang Wisesa", "deity_cn": "威塞薩（至高神格）",
        "animal": "🦁 獅子", "plant": "🌴 Kelapa（椰子樹）",
        "personality": "高貴自信、天生權威，具有領袖魅力，但有時過於自大",
        "career": "政治家、法官、企業主管、教授、宗教領袖",
        "marriage": "與 Gumbreg、Watugunung 相配；忌 Landep",
        "health": "注意脊背、心臟；宜保持身姿挺拔",
        "tabu": "此週忌卑躬屈膝、忌接受不義之財",
        "auspicious_act": "宜宣示主權、開創事業、舉辦重大儀式",
        "lucky_day_in_wuku": 7, "color": "#85E89D",
    },
    {   # 15 — Pahang
        "deity": "Hyang Kuwera", "deity_cn": "俱毘羅（財富之神）",
        "animal": "🐛 蜈蚣", "plant": "🍈 Durian（榴槤）",
        "personality": "財運極佳但命途多舛，擁有隱藏財富，內心複雜",
        "career": "金融業、珠寶商、房地產、挖掘業",
        "marriage": "與 Langkir 相配（互補）；忌 Dungulan",
        "health": "注意毒素積累、解毒排毒；宜定期禁食",
        "tabu": "此週 Buda Kliwon 為全年最凶之日（Buda Kliwon Pahang）；忌任何重大活動；忌貪婪",
        "auspicious_act": "宜守財護財、淨化業障、佈施功德",
        "lucky_day_in_wuku": 2, "color": "#FFC3A0",
    },
    {   # 16 — Krulut
        "deity": "Hyang Asmara", "deity_cn": "愛之神",
        "animal": "🕷️ 蜘蛛", "plant": "🌸 Melati（茉莉花）",
        "personality": "藝術氣質濃厚、浪漫多情，充滿魅力，但感情不穩定",
        "career": "音樂家、詩人、畫家、戀愛顧問、表演藝術家",
        "marriage": "與 Merakih 相配；忌 Kulantir",
        "health": "注意情緒健康，勿過度迷戀；宜音樂療癒",
        "tabu": "此週忌輕率訂婚；忌過度放縱感情；Tumpek Krulut 宜音樂祝福",
        "auspicious_act": "宜音樂演奏、藝術創作、戀愛告白（謹慎）",
        "lucky_day_in_wuku": 4, "color": "#FF6B6B",
    },
    {   # 17 — Merakih
        "deity": "Hyang Sedana", "deity_cn": "塞達納（財神）",
        "animal": "🦏 犀牛", "plant": "🌿 Cengkeh（丁香）",
        "personality": "勤勞踏實、財運興旺，意志堅定，處事圓滑",
        "career": "貿易商、銀行家、農場主、香料貿易商",
        "marriage": "與 Krulut、Uye 相配；忌 Matal",
        "health": "注意血脂、心血管；宜多活動",
        "tabu": "此週忌做虧本生意；忌辦喪事後立即辦喜事",
        "auspicious_act": "宜開市、商業洽談、農業投資、計算盈虧",
        "lucky_day_in_wuku": 5, "color": "#4ECDC4",
    },
    {   # 18 — Tambir
        "deity": "Hyang Gana", "deity_cn": "象頭神（移除障礙）",
        "animal": "🐘 象", "plant": "🎃 Labu（南瓜）",
        "personality": "足智多謀、善於解決難題，記憶力超強，忠誠可靠",
        "career": "工程師、問題解決專家、傳統醫者、會計師",
        "marriage": "與 Kulantir、Matal 相配；忌 Menail",
        "health": "注意頭部、鼻竇；宜按摩太陽穴",
        "tabu": "此週忌輕率放棄；忌中途而廢",
        "auspicious_act": "宜啟動新專案、突破障礙、建房奠基、學習新技能",
        "lucky_day_in_wuku": 6, "color": "#FFE66D",
    },
    {   # 19 — Medangkungan
        "deity": "Hyang Mahadewa", "deity_cn": "大神",
        "animal": "🐝 蜜蜂", "plant": "🌸 Anggrek（蘭花）",
        "personality": "辛勤工作、秩序感強，但常感覺負擔沉重，需要釋放",
        "career": "蜂農、研究員、製藥師、工廠管理員",
        "marriage": "與 Tambir、Prangbakat 相配；忌 Ugu",
        "health": "注意過勞、免疫系統；宜充分休息",
        "tabu": "此週忌加重他人負擔；忌過度苛責自己",
        "auspicious_act": "宜整理倉庫、清算帳目、完成未完之事",
        "lucky_day_in_wuku": 3, "color": "#A8E6CF",
    },
    {   # 20 — Matal
        "deity": "Hyang Iswara", "deity_cn": "伊斯瓦拉（東方之神）",
        "animal": "🐂 牛", "plant": "🌺 Kembang Sepatu（扶桑花）",
        "personality": "純潔正直、秩序井然，崇尚傳統，做事一絲不苟",
        "career": "行政管理、宗教事務、祭司助理、圖書管理員",
        "marriage": "與 Tambir、Uye 相配；忌 Merakih",
        "health": "注意腸道健康；宜保持規律作息",
        "tabu": "此週忌打破傳統規範；忌不敬神明",
        "auspicious_act": "宜新開始、淨化身心、辦理文件手續、婚禮登記",
        "lucky_day_in_wuku": 1, "color": "#FF8B94",
    },
    {   # 21 — Uye
        "deity": "Hyang Uma", "deity_cn": "烏瑪（大地母神）",
        "animal": "🦋 蝴蝶", "plant": "🌼 Jepun Putih（白緬梔）",
        "personality": "溫柔細膩、藝術氣質，與自然和動物相通，心靈純淨",
        "career": "護理師、植物學家、藝術家、獸醫、環保鬥士",
        "marriage": "與 Merakih、Matal 相配；忌 Bala",
        "health": "注意婦科、荷爾蒙；宜接地氣、在花園勞動",
        "tabu": "此週忌虐待動物植物；Tumpek Kandang（Saniscara Kliwon）為牲畜聖日",
        "auspicious_act": "宜照料動植物、農耕、感恩大地、婦幼祈福",
        "lucky_day_in_wuku": 7, "color": "#C3A6FF",
    },
    {   # 22 — Menail
        "deity": "Hyang Garuda", "deity_cn": "迦樓羅（神鷹）",
        "animal": "🦅 鷹", "plant": "🌲 Pinus（松樹）",
        "personality": "行動敏捷、眼界高遠，追求自由，但有時過於驕傲",
        "career": "飛行員、偵探、獵人、武道家、山岳探險家",
        "marriage": "與 Menail、Wayang 相配；忌 Warigadian",
        "health": "注意眼睛、高空適應；宜瑜伽強化核心",
        "tabu": "此週忌驕傲自大；忌下攻決策；忌傷害飛禽",
        "auspicious_act": "宜高空活動、偵察、競速、眼科手術",
        "lucky_day_in_wuku": 4, "color": "#85E89D",
    },
    {   # 23 — Prangbakat
        "deity": "Hyang Durga", "deity_cn": "難近母（保護女神）",
        "animal": "🦇 蝙蝠", "plant": "🌙 Kembang Bangkai（屍花）",
        "personality": "神秘難測、業力深重，具有強大的保護能量，但需要靈性修行化解業障",
        "career": "靈媒、驅魔師、傳統醫者、心理諮詢師",
        "marriage": "與 Medangkungan 相配；忌 Ukir",
        "health": "注意心理健康、業障影響；宜定期淨化能量場",
        "tabu": "此週忌做有負面業力之事；忌傷害他人；宜懺悔過失",
        "auspicious_act": "宜驅邪淨化、靈性修行、業力解除儀式",
        "lucky_day_in_wuku": 2, "color": "#FFC3A0",
    },
    {   # 24 — Bala
        "deity": "Hyang Brahma (火)", "deity_cn": "梵天火焰形態",
        "animal": "🐅 虎", "plant": "🌺 Flamboyant（鳳凰木）",
        "personality": "精力充沛、充滿熱忱，勇敢無畏，但衝動易燃",
        "career": "消防員、廚師（火候大師）、鍛造師、武術家、創業者",
        "marriage": "與 Ugu 相配；忌 Julungwangi、Uye",
        "health": "注意炎症、發燒；宜多喝水、控制火氣",
        "tabu": "此週忌用火不慎；忌與人正面衝突；忌辦婚禮喜事",
        "auspicious_act": "宜淬鍊技藝、競技比賽、火神祭祀、鍛造新器",
        "lucky_day_in_wuku": 3, "color": "#FF6B6B",
    },
    {   # 25 — Ugu
        "deity": "Hyang Wisnu (守護)", "deity_cn": "毘濕奴守護形態",
        "animal": "🦜 鸚鵡", "plant": "🌴 Lontar（棕櫚葉）",
        "personality": "忠誠可靠、穩若磐石，善於保護他人，但有時過於保守",
        "career": "圖書館員、守衛、農夫、傳統知識保管者",
        "marriage": "與 Bala、Wayang 相配；忌 Medangkungan",
        "health": "注意膝關節、消化系統；宜走路散步",
        "tabu": "此週忌輕率改變傳統；忌辜負他人信任",
        "auspicious_act": "宜守護傳統、記錄典籍、植樹種林",
        "lucky_day_in_wuku": 5, "color": "#4ECDC4",
    },
    {   # 26 — Wayang
        "deity": "Hyang Kala (暗)", "deity_cn": "卡拉（暗影之神）",
        "animal": "🐒 猴", "plant": "🌿 Kepah（皮影戲植物）",
        "personality": "才華橫溢、善於表演，思維獨特，內心世界豐富而複雜",
        "career": "表演藝術家、皮影戲師（Dalang）、作家、導演",
        "marriage": "與 Menail、Ugu 相配；忌 Gumbreg",
        "health": "注意眼睛疲勞、腦部健康；宜減少熬夜",
        "tabu": "此週 Tumpek Wayang（Saniscara Kliwon）為皮影戲聖日；忌侮辱藝術",
        "auspicious_act": "宜皮影戲演出、創意寫作、藝術展覽",
        "lucky_day_in_wuku": 4, "color": "#FFE66D",
    },
    {   # 27 — Klawu
        "deity": "Hyang Ninigsari", "deity_cn": "寧薩里（自然女神）",
        "animal": "🐸 蛙", "plant": "🌿 Kangkung（空心菜）",
        "personality": "直覺敏銳、親近自然，情感細膩，善於感知周遭變化",
        "career": "農夫、漁夫、傳統草藥師、水利工程師",
        "marriage": "與 Dukut、Watugunung 相配；忌 Prangbakat",
        "health": "注意腎臟、水份代謝；宜多喝天然泉水",
        "tabu": "此週 Buda Kliwon Klawu 為特殊吉日（非凶）；忌污染水源",
        "auspicious_act": "宜護水儀式、農業灌溉、靜心靈修、接地冥想",
        "lucky_day_in_wuku": 6, "color": "#A8E6CF",
    },
    {   # 28 — Dukut
        "deity": "Hyang Maheswara (持)", "deity_cn": "摩醯首羅持久形態",
        "animal": "🪱 蚯蚓", "plant": "🌿 Rumput (草)",
        "personality": "謙遜低調、持之以恆，默默耕耘，但容易被忽視",
        "career": "園丁、農民、清潔工、靜修者、服務業",
        "marriage": "與 Klawu、Sinta 相配；忌 Wariga",
        "health": "注意腸道、皮膚；宜接觸大自然、土壤療癒",
        "tabu": "此週忌輕視卑微者；忌浪費、糟蹋自然資源",
        "auspicious_act": "宜持續耕耘、施肥種植、堅持日常功課",
        "lucky_day_in_wuku": 2, "color": "#FF8B94",
    },
    {   # 29 — Watugunung
        "deity": "Hyang Siwa (終)", "deity_cn": "濕婆終結形態（大圓滿）",
        "animal": "🐉 龍", "plant": "🌿 Preh (石榕)",
        "personality": "充滿傳奇、業力深厚，是週期的終結者與更新者，個性難以捉摸",
        "career": "哲學家、宗教改革者、周期研究者、神學家",
        "marriage": "與 Pujut、Klawu 相配；忌 Sungsang",
        "health": "注意整體能量更新；宜儀式性淨化與整合",
        "tabu": "此週忌開始新事物（週期將盡）；Watugunung 週為 Pawukon 最後一週，宜結束、總結",
        "auspicious_act": "宜結算、感恩祈福、業障總清、大齋戒禁食",
        "lucky_day_in_wuku": 7, "color": "#C3A6FF",
    },
]

# ============================================================
# ACTIVITY_RULES — 各類活動的傳統擇日規則
# 格式：活動識別碼 → 詳細規則字典
# 古法依據：Lontar Wariga Dewasa — 宜忌章節
# ============================================================
ACTIVITY_RULES = {
    "wedding": {
        "name_cn": "婚禮/訂婚 (Pawiwahan)",
        "name_bal": "Pawiwahan",
        "icon": "💍",
        "best_panca": ["Umanis", "Paing"],
        "best_sapta": ["Sukra", "Soma", "Wraspati"],
        "best_sasih": [0, 1, 2, 3, 9, 11],   # Kasa, Karo, Katiga, Kapat, Kadasa, Sada
        "avoid_panca": ["Pon", "Wage"],
        "avoid_sapta": ["Anggara"],
        "avoid_wuku": ["Watugunung", "Krulut", "Pahang", "Bala", "Langkir"],
        "avoid_tri": ["Kajeng"],
        "best_combo": [("Sukra", "Umanis"), ("Soma", "Umanis"), ("Sukra", "Kliwon")],
        "notes": "宜選 Sukra Umanis 或 Soma Umanis；避 Kajeng Kliwon 與 Tilem；Purnama 為大吉",
        "ritual": "選定吉日後，需請 Pemangku（廟祭司）確認，並辦 Mabiyakala 淨化儀式",
    },
    "ngaben": {
        "name_cn": "火葬典禮 (Ngaben)",
        "name_bal": "Ngaben / Pelebon",
        "icon": "🕯️",
        "best_panca": ["Umanis", "Kliwon"],
        "best_sapta": ["Wraspati", "Sukra", "Buda"],
        "best_sasih": [3, 4, 5, 6],  # Kapat, Kalima, Kanem, Kapitu
        "avoid_panca": [],
        "avoid_sapta": [],
        "avoid_wuku": ["Dungulan", "Kuningan"],  # 不在 Galungan/Kuningan 週辦
        "avoid_tri": [],
        "best_combo": [("Wraspati", "Umanis"), ("Sukra", "Kliwon")],
        "notes": "Ngaben 日期需由 Pedanda（高僧）根據往生者生辰特別推算；某些 Kajeng Kliwon 可接受",
        "ritual": "需先請示 Pedanda，進行 Ngaroras（三日後）、Ngelungah（12日後）等前置儀式",
    },
    "metatah": {
        "name_cn": "鋸牙禮/成人禮 (Mepandes/Metatah)",
        "name_bal": "Mepandes / Metatah",
        "icon": "✨",
        "best_panca": ["Umanis", "Paing"],
        "best_sapta": ["Sukra", "Soma", "Wraspati"],
        "best_sasih": [0, 1, 2, 3],
        "avoid_panca": ["Wage"],
        "avoid_sapta": ["Anggara"],
        "avoid_wuku": ["Pahang", "Langkir", "Bala"],
        "avoid_tri": ["Kajeng"],
        "best_combo": [("Sukra", "Umanis"), ("Soma", "Umanis")],
        "notes": "宜選 Sukra Umanis；此儀式關乎靈魂完整，需格外謹慎選日",
        "ritual": "儀式前需齋戒，由 Pemangku 主持，親屬全程陪伴",
    },
    "house_blessing": {
        "name_cn": "房屋祝福/喬遷 (Melaspas/Madengen-dengen)",
        "name_bal": "Melaspas / Madengen-dengen",
        "icon": "🏠",
        "best_panca": ["Umanis", "Paing"],
        "best_sapta": ["Wraspati", "Buda", "Sukra"],
        "best_sasih": [0, 2, 3, 9],  # Kasa, Katiga, Kapat, Kadasa
        "avoid_panca": ["Kliwon"],  # Kajeng Kliwon 特別忌
        "avoid_sapta": ["Anggara"],
        "avoid_wuku": ["Pahang", "Watugunung", "Sungsang"],
        "avoid_tri": ["Kajeng"],
        "best_combo": [("Wraspati", "Umanis"), ("Buda", "Umanis"), ("Wraspati", "Paing")],
        "notes": "動土宜選 Wraspati Umanis；入住喬遷宜 Purnama；忌 Kajeng Kliwon",
        "ritual": "需辦 Mlaspas（房屋淨化）與 Macaru（大地安撫）儀式",
    },
    "business": {
        "name_cn": "開業/商業 (Ngempas Linggih Dagangan)",
        "name_bal": "Ngatep / Ngempas Linggih",
        "icon": "💼",
        "best_panca": ["Umanis", "Paing"],
        "best_sapta": ["Wraspati", "Sukra", "Buda"],
        "best_sasih": [0, 1, 9, 11],  # Kasa, Karo, Kadasa, Sada
        "avoid_panca": ["Pon", "Wage"],
        "avoid_sapta": ["Anggara"],
        "avoid_wuku": ["Pahang", "Langkir", "Bala", "Krulut"],
        "avoid_tri": ["Kajeng"],
        "best_combo": [("Wraspati", "Umanis"), ("Wraspati", "Paing"), ("Sukra", "Umanis")],
        "notes": "Wraspati（木星/財富）Umanis 為開業最佳；避 Kajeng Kliwon 與凶 Wuku",
        "ritual": "開業前需辦 Ngehaturang Canang（獻供儀式），請求 Dewi Sri（豐收女神）庇佑",
    },
    "farming": {
        "name_cn": "農耕/播種 (Pertanian/Tandur)",
        "name_bal": "Tandur / Manyi",
        "icon": "🌾",
        "best_panca": ["Umanis", "Paing"],
        "best_sapta": ["Redite", "Soma"],
        "best_sasih": [6, 7, 8, 9],  # 雨季 Kapitu-Kadasa
        "avoid_panca": ["Kliwon"],
        "avoid_sapta": ["Anggara"],
        "avoid_wuku": ["Pahang", "Langkir"],
        "avoid_tri": ["Kajeng"],
        "best_combo": [("Soma", "Umanis"), ("Redite", "Umanis"), ("Soma", "Paing")],
        "notes": "Tumpek Uduh（Wuku Wariga Saniscara Kliwon）為植物祝福聖日，宜祈禱豐收",
        "ritual": "播種前辦 Ngerasakin（土地祝福），收割前辦 Manyi 感恩儀式",
    },
    "travel": {
        "name_cn": "出行/旅行 (Lunga Ngalain)",
        "name_bal": "Lunga Ngalain",
        "icon": "✈️",
        "best_panca": ["Umanis"],
        "best_sapta": ["Sukra", "Wraspati", "Soma"],
        "best_sasih": [0, 1, 2, 3],
        "avoid_panca": ["Kliwon", "Pon"],
        "avoid_sapta": ["Anggara"],
        "avoid_wuku": ["Pahang", "Langkir"],
        "avoid_tri": ["Kajeng"],
        "best_combo": [("Sukra", "Umanis"), ("Wraspati", "Umanis")],
        "notes": "Sukra Umanis 為遠行最佳吉日；避 Tilem、Kajeng Kliwon；注意 Dauh 時辰",
        "ritual": "出行前需獻簡單供品，向 Dewa Bayu（風神）祈求平安",
    },
    "spiritual": {
        "name_cn": "靈性修行/冥想 (Yoga/Tapa/Brata)",
        "name_bal": "Yoga / Tapa / Brata",
        "icon": "🧘",
        "best_panca": ["Kliwon", "Umanis"],
        "best_sapta": ["Buda", "Wraspati", "Saniscara"],
        "best_sasih": [0, 5, 6, 11],
        "avoid_panca": [],
        "avoid_sapta": [],
        "avoid_wuku": [],
        "avoid_tri": [],
        "best_combo": [("Buda", "Kliwon"), ("Wraspati", "Kliwon"), ("Saniscara", "Kliwon")],
        "notes": "Kajeng Kliwon、Purnama、Tilem、Tumpek 皆為靈修聖日；反常規的大吉之日",
        "ritual": "宜齋戒、誦經、觀想、在神廟冥想；Kajeng Kliwon 適合獻供驅邪",
    },
}

# ============================================================
# GOOD_WEWARAN_COMBOS — 傳統吉祥 Sapta+Panca Wara 組合
# 格式：(Sapta Wara 名稱, Panca Wara 名稱) → (描述, 適用活動)
# 古法依據：Lontar Wariga Dewasa — Wewaran 吉日章節
# ============================================================
GOOD_WEWARAN_COMBOS = {
    ("Soma",     "Umanis"):  ("Soma Umanis — 理想通用吉日",         "婚禮、旅行、開業、所有重要事"),
    ("Sukra",    "Umanis"):  ("Sukra Umanis — 婚嫁旅行首選",        "婚嫁、旅行、藝術、出行"),
    ("Wraspati", "Umanis"):  ("Wraspati Umanis — 商業學業大吉",     "開業、學業、動土、大事決策"),
    ("Buda",     "Umanis"):  ("Buda Umanis — 溝通協商吉日",         "協商、合約、溝通、談判"),
    ("Redite",   "Umanis"):  ("Redite Umanis — 農耕旅行吉日",       "農耕、旅行、新開始"),
    ("Soma",     "Kliwon"):  ("Soma Kliwon — 醫療靈性吉日",         "醫療、靈修、治療、祈禱"),
    ("Sukra",    "Kliwon"):  ("Sukra Kliwon — 婚嫁聖日",            "婚嫁、愛情、藝術、慶典"),
    ("Wraspati", "Kliwon"):  ("Wraspati Kliwon — 祭祀吉日",         "祭祀、靈修、開業、求財"),
    ("Wraspati", "Paing"):   ("Wraspati Paing — 商業繁榮吉日",      "開業、商業、財運、擴張"),
    ("Soma",     "Paing"):   ("Soma Paing — 農業豐收吉日",          "農耕、收割、家事、育兒"),
    ("Saniscara","Kliwon"):  ("Tumpek（Saniscara Kliwon）— 聖日",   "視 Wuku 而定的特殊祭祀"),
    ("Buda",     "Kliwon"):  ("Buda Kliwon — 靈修聖日",             "靈修（非 Pahang 週）、祭祀"),
}

# ============================================================
# UTTAMA_WUKU — 傳統視為天生大吉的 Wuku（索引）
# 古法依據：Lontar Wariga — Wuku 吉凶傾向
# ============================================================
UTTAMA_WUKU = {0, 8, 11, 29}    # Sinta, Julungwangi, Kuningan, Watugunung

# ============================================================
# MADYA_WUKU — 傳統視為中性或小吉的 Wuku
# ============================================================
MADYA_WUKU = {1, 2, 5, 6, 10, 13, 14, 17, 18, 21, 25, 26}

# ============================================================
# ALA_WUKU — 傳統視為需謹慎的 Wuku（索引）
# 古法依據：Lontar Wariga — Wuku 凶險提示
# ============================================================
ALA_WUKU = {12, 15, 16, 23, 24, 28}    # Langkir, Pahang, Krulut, Prangbakat, Bala, Dukut

# ============================================================
# OTONAN_RITUALS — 各 Wuku 的 Otonan（210天生日）推薦儀式
# 古法依據：Lontar Tattwa Krama — Otonan 儀式指南
# ============================================================
OTONAN_RITUALS = [
    "Otonan Sinta：獻供 Pejati、誦 Kekidung Sinta，宜穿紅色衣物，請 Pemangku 祝福",
    "Otonan Landep：獻利器（刀、劍）祝福，誦 Kekidung Landep，宜磨礪技藝",
    "Otonan Ukir：獻雕刻品或手工藝，誦 Kekidung Ukir，宜創作感恩",
    "Otonan Kulantir：獻鮮花（尤其橙色），誦 Kekidung Kulantir，宜表演藝術",
    "Otonan Tolu：獻蓮花與香，靜坐冥想，誦 Gayatri Mantra，宜靈性深化",
    "Otonan Gumbreg：獻五穀與果實，感謝豐收，宜在農地舉行，誦豐收讚頌",
    "Otonan Wariga：獻竹製品與草藥，誦 Kekidung Wariga，宜在竹林中舉行",
    "Otonan Warigadian：獻稻穗與鳥食，感謝生命轉化，宜戶外舉行",
    "Otonan Julungwangi：獻白色鮮花與聖水，在月光下誦讚月神，宜女性主持",
    "Otonan Sungsang：獻紅花與香茅水，進行大淨化儀式，誦清淨咒",
    "Otonan Dungulan：獻豐盛供品，慶祝勝利，誦 Puja Galungan，宜全家共慶",
    "Otonan Kuningan：獻黃色供品（nasi kuning），誦 Puja Kuningan，呼請祖靈保佑",
    "Otonan Langkir：特別獻供強化護符，請高僧淨化業障，誦防護咒",
    "Otonan Medangsia：獻旅行護符，請 Bayu 風神保佑旅途平安",
    "Otonan Pujut：獻椰子製品，誦威儀咒，宜在廟宇接受長老祝福",
    "Otonan Pahang：特別舉行業障清除儀式（Pecaruan），誦解厄咒，宜齋戒一日",
    "Otonan Krulut：獻鮮花茉莉，在音樂伴奏下舉行，誦音樂祝福咒",
    "Otonan Merakih：獻金銀飾品，祈求財運，誦 Sedana（財神）讚歌",
    "Otonan Tambir：獻南瓜與大米，請 Gana 象頭神移除生命障礙，誦去障咒",
    "Otonan Medangkungan：獻蜂蜜與蘭花，感謝辛勤付出，宜放鬆身心",
    "Otonan Matal：獻白花與聖水，進行純潔儀式，誦新生咒",
    "Otonan Uye：獻動植物祭品，在花園舉行，感謝大地母神",
    "Otonan Menail：獻羽毛與鮮花，在高處（廟宇高台）舉行，誦飛翔讚頌",
    "Otonan Prangbakat：特別舉行業力清理（Caru Panca Sata），請驅邪專家主持",
    "Otonan Bala：獻燃燒物（蠟燭）與紅色供品，誦火神讚歌，宜鍛煉身體",
    "Otonan Ugu：獻棕櫚葉製品，誦守護咒，感謝 Wisnu 的持續守護",
    "Otonan Wayang：舉行小型 Wayang Kulit（皮影戲）表演，獻影偶祭品",
    "Otonan Klawu：在水邊舉行，獻水草與花，誦水神讚頌，飲聖泉水",
    "Otonan Dukut：獻泥土與草，腳踏大地舉行，感謝持續努力的力量",
    "Otonan Watugunung：盛大終結與更新儀式，感謝整個 Pawukon 週期，誦大讚歌",
]
