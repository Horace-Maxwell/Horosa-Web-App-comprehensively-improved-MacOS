"""
astro/icons.py — 體系圖示與文化色彩對應 (System Icons & Cultural Colors)

Maps each astrology system tab key to an emoji icon and a representative
cultural accent colour, used by the sidebar card grid and theme switcher.
"""

# ═══════════════════════════════════════════════════════════════
# System Icon Mapping — 體系圖示字典
# ═══════════════════════════════════════════════════════════════
SYSTEM_ICONS: dict[str, str] = {
    # ── Popular ──
    "tab_western":      "🪐",
    "tab_ziwei":        "🌟",
    # ── Chinese ──
    "tab_chinese":      "☯️",
    "tab_chinstar":     "✨",
    "tab_cetian_ziwei": "🏯",
    # ── Western / Hellenistic ──
    "tab_hellenistic":  "🏛️",
    "tab_kabbalistic":  "✡️",
    # ── Asian ──
    "tab_indian":       "🙏",
    "tab_nadi":         "🍃",
    "tab_jaimini":      "🔱",
    "tab_sukkayodo":    "📿",
    "tab_thai":         "🪷",
    "tab_mahabote":     "🐘",
    "tab_zurkhai":      "🐎",
    "tab_tibetan":      "🗻",
    # ── Middle East ──
    "tab_arabic":       "🕌",
    "tab_yemeni":       "🌙",
    # ── Chinese (additional) ──
    "tab_damo":         "🤚",
    "tab_diqiyijue":   "🌀",
    # ── Ancient / Mesoamerican ──
    "tab_maya":         "🐍",
    "tab_dogon_sirius": "🜂",
    "tab_aztec":        "🦅",
    "tab_decans":       "🏺",
    "tab_babylonian":   "📜",
    # ── KP Astrology ──
    "tab_kp":           "🔮",
    # ── Tie Ban Shen Shu ──
    "tab_tieban":       "🔮",
    # ── Ghost Valley Fen Ding Jing ──
    "tab_fendjing":     "🔮",
}

# ═══════════════════════════════════════════════════════════════
# Cultural Accent Colors — 文化代表色
# ═══════════════════════════════════════════════════════════════
SYSTEM_ACCENT_COLORS: dict[str, str] = {
    # ── Chinese systems → purple-gold 紫金 ──
    "tab_chinese":      "#C9A84C",
    "tab_chinstar":     "#C9A84C",
    "tab_cetian_ziwei": "#C9A84C",
    "tab_ziwei":        "#C9A84C",
    "tab_damo":         "#C9A84C",
    "tab_diqiyijue":   "#C9A84C",
    # ── Western / Hellenistic → blue-silver 藍銀 ──
    "tab_western":      "#7B9ED9",
    "tab_hellenistic":  "#7B9ED9",
    "tab_kabbalistic":  "#9B8EC4",
    # ── Asian → lotus / saffron ──
    "tab_indian":       "#FF9933",
    "tab_nadi":         "#E8A838",
    "tab_jaimini":      "#E8A838",
    "tab_sukkayodo":    "#D4A017",
    "tab_thai":         "#E0A526",
    "tab_mahabote":     "#C9934A",
    "tab_zurkhai":      "#6B9F5E",
    "tab_tibetan":      "#B24747",
    # ── Middle East → turquoise / gold ──
    "tab_arabic":       "#3AB09E",
    "tab_yemeni":       "#3AB09E",
    # ── Ancient / Mesoamerican ──
    "tab_maya":         "#4AA068",
    "tab_dogon_sirius": "#8F6B3F",
    "tab_aztec":        "#C44D2A",
    "tab_decans":       "#D4A04A",
    "tab_babylonian":   "#B8956A",
    # ── KP Astrology → orange-red ──
    "tab_kp":           "#FF6B35",
    # ── Tie Ban Shen Shu → traditional red-gold ──
    "tab_tieban":       "#C9A84C",
    # ── Ghost Valley Fen Ding Jing → traditional red-gold ──
    "tab_fendjing":     "#C9A84C",
    # ── Huangji Jingshi → classical earth-gold ──
    "tab_huangji":      "#8E6B3D",
}

# ═══════════════════════════════════════════════════════════════
# Cultural CSS Class Mapping — 文化風格 CSS class
# ═══════════════════════════════════════════════════════════════
SYSTEM_CSS_CLASS: dict[str, str] = {
    "tab_chinese":      "chinese-chart",
    "tab_chinstar":     "chinese-chart",
    "tab_cetian_ziwei": "chinese-chart",
    "tab_ziwei":        "chinese-chart",
    "tab_damo":         "chinese-chart",
    "tab_diqiyijue":   "chinese-chart",
    "tab_huangji":      "chinese-chart",
    "tab_western":      "western-chart",
    "tab_hellenistic":  "western-chart",
    "tab_kabbalistic":  "western-chart",
    "tab_indian":       "vedic-chart",
    "tab_nadi":         "vedic-chart",
    "tab_jaimini":      "vedic-chart",
    "tab_sukkayodo":    "vedic-chart",
    "tab_thai":         "thai-chart",
    "tab_mahabote":     "vedic-chart",
    "tab_zurkhai":      "vedic-chart",
    "tab_tibetan":      "tibetan-chart",
    "tab_arabic":       "arabic-chart",
    "tab_yemeni":       "arabic-chart",
    "tab_maya":         "maya-chart",
    "tab_dogon_sirius": "maya-chart",
    "tab_aztec":        "aztec-chart",
    "tab_decans":       "egyptian-chart",
    "tab_babylonian":   "babylonian-chart",
    "tab_celtic_tree":  "western-chart",
    # ── KP Astrology ──
    "tab_kp":           "kp-chart",
    # ── Tie Ban Shen Shu ──
    "tab_tieban":       "chinese-chart",
    # ── Ghost Valley Fen Ding Jing ──
    "tab_fendjing":     "chinese-chart",
}
