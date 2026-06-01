"""
frontend/custom_theme.py — KinAstro 全域美學設計系統 (Global Aesthetic Design System)

定義主色調、字體、光暈效果常量，供整個應用統一使用。
Defines primary colors, fonts, and glow constants for the entire application.
"""

# ═══════════════════════════════════════════════════════════════
# Color Palette — 主色調系統
# ═══════════════════════════════════════════════════════════════
COLORS = {
    # Primary palette
    "deep_indigo": "#0F172A",       # 深靛藍 — 主背景
    "stardust_gold": "#EAB308",     # 星塵金 — 高光與強調
    "soft_purple": "#7C3AED",       # 柔和紫霧 — 互動元素
    "deep_space_black": "#020617",  # 深空黑 — 極深背景

    # Extended palette
    "cosmic_violet": "#A78BFA",     # 宇宙紫 — 次要互動
    "nebula_blue": "#1E1B4B",      # 星雲藍 — 卡片背景
    "aurora_teal": "#2DD4BF",      # 極光青 — 成功狀態
    "stellar_silver": "#E0E0FF",   # 星銀 — 主文字
    "dim_starlight": "#B0B0D0",    # 暗星光 — 次要文字
    "midnight_purple": "#581C87",   # 午夜紫 — 漸層用

    # Functional colors
    "success": "#34D399",
    "warning": "#FBBF24",
    "error": "#EF4444",
    "info": "#60A5FA",
}

# ═══════════════════════════════════════════════════════════════
# Typography — 字體系統
# ═══════════════════════════════════════════════════════════════
FONTS = {
    "heading": "'Cinzel', 'Noto Sans TC', serif",
    "body": "'Space Grotesk', 'Inter', 'Noto Sans TC', sans-serif",
    "monospace": "'JetBrains Mono', 'Fira Code', monospace",
    "chinese": "'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', sans-serif",

    # Google Fonts import URL
    "import_url": (
        "https://fonts.googleapis.com/css2?"
        "family=Cinzel:wght@400;500;600;700;900"
        "&family=Space+Grotesk:wght@300;400;500;600;700"
        "&family=Inter:wght@300;400;500;600"
        "&family=Noto+Sans+TC:wght@300;400;500;700"
        "&display=swap"
    ),
}

# ═══════════════════════════════════════════════════════════════
# Glow & Visual Effects — 光暈與視覺效果常量
# ═══════════════════════════════════════════════════════════════
GLOW = {
    # Box shadow glow presets
    "subtle": "0 0 15px rgba(124, 58, 237, 0.15)",
    "medium": "0 0 25px rgba(124, 58, 237, 0.25)",
    "strong": "0 0 40px rgba(124, 58, 237, 0.35)",
    "gold": "0 0 30px rgba(234, 179, 8, 0.3)",
    "cosmic": (
        "0 0 20px rgba(124, 58, 237, 0.2), "
        "0 0 40px rgba(234, 179, 8, 0.1), "
        "0 0 60px rgba(124, 58, 237, 0.05)"
    ),

    # Text glow
    "text_subtle": "0 0 10px rgba(167, 139, 250, 0.3)",
    "text_gold": "0 0 15px rgba(234, 179, 8, 0.4)",

    # Border glow
    "border_purple": "rgba(124, 58, 237, 0.3)",
    "border_gold": "rgba(234, 179, 8, 0.2)",
}

# ═══════════════════════════════════════════════════════════════
# Gradient Presets — 漸層預設
# ═══════════════════════════════════════════════════════════════
GRADIENTS = {
    "cosmic_bg": (
        "radial-gradient(ellipse at 20% 50%, rgba(88, 28, 135, 0.18) 0%, transparent 60%), "
        "radial-gradient(ellipse at 80% 20%, rgba(30, 27, 75, 0.45) 0%, transparent 50%), "
        "radial-gradient(ellipse at 50% 80%, rgba(59, 7, 100, 0.15) 0%, transparent 50%), "
        "linear-gradient(180deg, #0F172A 0%, #0d0d35 50%, #020617 100%)"
    ),
    "title_text": "linear-gradient(135deg, #A78BFA 0%, #EAB308 50%, #A78BFA 100%)",
    "button_primary": "linear-gradient(135deg, #7C3AED 0%, #A78BFA 100%)",
    "card_bg": "linear-gradient(135deg, rgba(30, 27, 75, 0.8) 0%, rgba(88, 28, 135, 0.6) 50%, rgba(30, 27, 75, 0.8) 100%)",
    "sidebar": "linear-gradient(180deg, #0F172A 0%, #1E1B4B 100%)",
}

# ═══════════════════════════════════════════════════════════════
# Manuscript Themes — 手稿風主題
# ═══════════════════════════════════════════════════════════════
MANUSCRIPT_THEMES = {
    "nusantara_malay": {
        "paper": "rgba(255, 248, 230, 0.84)",      # 羊皮紙背景
        "grid": "#E8DCC8",                         # 細格線
        "line": "#BFA97A",                         # 金棕描邊
        "title": "#3E2723",                        # 深棕標題
        "legend": "rgba(255, 248, 230, 0.88)",     # 圖例底色
        "accent_gold": "#D4AF37",
        "accent_green": "#2E7D32",
        "accent_red": "#8B0000",
        "accent_neutral": "#DAA520",
    },
}

# ═══════════════════════════════════════════════════════════════
# Astrology System Categories — 占星體系分類
# ═══════════════════════════════════════════════════════════════
SYSTEM_CATEGORY_ICONS = {
    "cat_popular": "⭐",
    "cat_chinese": "🏮",
    "cat_western": "🏛️",
    "cat_asian": "🪷",
    "cat_middle_east": "🕌",
    "cat_ancient": "🏺",
}

# ═══════════════════════════════════════════════════════════════
# Chart Visual Constants — 星盤視覺常量
# ═══════════════════════════════════════════════════════════════
CHART_VISUAL = {
    "outer_ring_stroke": "#EAB308",
    "inner_ring_stroke": "#7C3AED",
    "zodiac_ring_bg": "rgba(30, 27, 75, 0.6)",
    "house_line_color": "rgba(167, 139, 250, 0.3)",
    "aspect_line_alpha": 0.6,
    "hover_glow_color": "rgba(234, 179, 8, 0.4)",
    "hover_rotation_deg": 2,
}
