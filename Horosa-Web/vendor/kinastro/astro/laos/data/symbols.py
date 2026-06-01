# astro/lao/data/symbols.py
"""
老撾占星術 (ໄທຣາສາດລາວ) 符號與圖示映射模組
提供 Unicode 符號、Lao 文字描述、SVG 友好符號，供 renderer.py 與 UI 使用
"""

from typing import Dict, Any

# ==================== 1. 十二生肖 / 十二宮 (ຣາສີ) ====================
LAO_ZODIAC_SYMBOLS: Dict[str, Dict[str, str]] = {
    "ມືງ":     {"unicode": "🐀", "name": "ມືງ (鼠)", "element": "ດິນ"},
    "ວົງ":     {"unicode": "🐂", "name": "ວົງ (牛)", "element": "ດິນ"},
    "ຄຳ":     {"unicode": "🐅", "name": "ຄຳ (虎)", "element": "ໄຟ"},
    "ທົ່ວ":    {"unicode": "🐇", "name": "ທົ່ວ (兔)", "element": "ໄຟ"},
    "ມະສິງ":  {"unicode": "🐉", "name": "ມະສິງ (龍)", "element": "ໄຟ"},
    "ມະສິງນ້ອຍ": {"unicode": "🐍", "name": "ມະສິງນ້ອຍ (蛇)", "element": "ໄຟ"},
    "ມ້າ":     {"unicode": "🐎", "name": "ມ້າ (馬)", "element": "ໄຟ"},
    "ແກະ":     {"unicode": "🐐", "name": "ແກະ (羊)", "element": "ດິນ"},
    "ລີງ":     {"unicode": "🐒", "name": "ລີງ (猴)", "element": "ໄຟ"},
    "ໄກ່":     {"unicode": "🐔", "name": "ໄກ່ (雞)", "element": "ໄຟ"},
    "ໝາ":     {"unicode": "🐶", "name": "ໝາ (狗)", "element": "ດິນ"},
    "ໝູ":     {"unicode": "🐷", "name": "ໝູ (豬)", "element": "ດິນ"},
}

# ==================== 2. 婆羅門占星輪核心符號 (封面大圓盤) ====================
BRAHMAN_WHEEL_SYMBOLS: Dict[str, Dict[str, str]] = {
    "center": {"unicode": "🌀", "name": "ສູນກາງ (中央)", "description": "ພະບາງມະຫາເທວະ"},
    "0": {"unicode": "☉", "name": "ສຸຣິຍະ", "description": "太陽"},
    "1": {"unicode": "☾", "name": "ຈັນ", "description": "月亮"},
    "2": {"unicode": "☿", "name": "ພຸດ", "description": "水星"},
    "3": {"unicode": "♀", "name": "ສຸກ", "description": "金星"},
    "4": {"unicode": "♂", "name": "ອັງຄານ", "description": "火星"},
    "5": {"unicode": "♃", "name": "ພະຫັດ", "description": "木星"},
    "6": {"unicode": "♄", "name": "ເສົາ", "description": "土星"},
    "good": {"unicode": "✅", "name": "ດີ", "description": "吉"},
    "bad": {"unicode": "❌", "name": "ເປັນອຸບັດເຫດ", "description": "凶"},
    "neutral": {"unicode": "⚖️", "name": "ປານກາງ", "description": "中性"},
}

# ==================== 3. 七曜與時辰符號 ====================
PLANET_SYMBOLS: Dict[str, str] = {
    "ສຸຣິຍະ": "☉",
    "ຈັນ": "☾",
    "ພຸດ": "☿",
    "ສຸກ": "♀",
    "ອັງຄານ": "♂",
    "ພະຫັດ": "♃",
    "ເສົາ": "♄",
}

# ==================== 4. 吉凶與活動通用符號 ====================
LAO_ASTRO_EMOJIS: Dict[str, str] = {
    "good": "✅ ດີ",
    "very_good": "🌟 ດີຫຼາຍ",
    "neutral": "⚖️ ປານກາງ",
    "bad": "❌ ອັນຕະລາຍ",
    "wheel": "🌀",
    "calendar": "📅",
    "house": "🏠",
    "wedding": "💒",
    "travel": "🛤️",
    "business": "🏪",
    "ritual": "🙏",
}

# ==================== 5. 工具函數 ====================
def get_zodiac_symbol(zodiac_lao: str) -> Dict[str, str]:
    """取得單一生肖符號"""
    return LAO_ZODIAC_SYMBOLS.get(zodiac_lao, {"unicode": "❓", "name": "未知", "element": "未知"})


def get_brahman_symbol(key: str) -> Dict[str, str]:
    """取得婆羅門輪符號"""
    return BRAHMAN_WHEEL_SYMBOLS.get(key, {"unicode": "❓", "name": "未知", "description": "未知"})


def get_planet_symbol(planet: str) -> str:
    """取得行星符號"""
    return PLANET_SYMBOLS.get(planet, "🌟")


# ==================== 公開介面 ====================
__all__ = [
    "LAO_ZODIAC_SYMBOLS",
    "BRAHMAN_WHEEL_SYMBOLS",
    "PLANET_SYMBOLS",
    "LAO_ASTRO_EMOJIS",
    "get_zodiac_symbol",
    "get_brahman_symbol",
    "get_planet_symbol",
]


# ==================== 測試與開發用 ====================
if __name__ == "__main__":
    print("=== Lao Horasat Symbols Test ===")
    print("鼠:", get_zodiac_symbol("ມືງ"))
    print("太陽:", get_planet_symbol("ສຸຣິຍະ"))
    print("婆羅門輪中心:", get_brahman_symbol("center"))
    print("吉:", LAO_ASTRO_EMOJIS["good"])
    print("\n所有支援生肖：", list(LAO_ZODIAC_SYMBOLS.keys()))
