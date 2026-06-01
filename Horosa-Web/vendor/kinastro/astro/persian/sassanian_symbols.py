"""
astro/sassanian/sassanian_symbols.py — 薩珊符號與視覺元素模組

Sassanian Symbols and Visual Elements
基於薩珊王朝藝術風格（3-7 世紀）

References
----------
- Sassanian silver plates (Metropolitan Museum, Louvre)
- Taq-e Bostan rock reliefs
- Sassanian seals and coins
- Greater Bundahishn illustrations
"""

from typing import Dict, Optional
import json
import os

# 獲取當前檔案所在目錄
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


# 薩珊色彩調色盤
# 基於薩珊銀盤、泰西封宮殿壁畫、塔克布斯坦浮雕
SASSANIAN_COLOR_PALETTE = {
    # 主色
    "crimson": "#8B1538",        # 深紅（皇室色彩）
    "gold_leaf": "#D4AF37",      # 金箔（神聖、皇家）
    "turquoise": "#40E0D0",      # 綠松石（天空、神聖）
    "dark_indigo": "#1A237E",    # 深靛藍（夜空、神秘）
    "white": "#F5F5F5",          # 白色（純潔）
    "black": "#1C1C1C",          # 黑色（邊框、文字）

    # 輔助色
    "burnt_orange": "#CC5500",   #  burnt orange（火焰）
    "deep_purple": "#4B0082",    # 深紫（皇室）
    "silver": "#C0C0C0",         # 銀色（月亮）
    "bronze": "#CD7F32",         # 青銅（火星）

    # 背景色
    "parchment": "#F5E6D3",      # 羊皮紙背景
    "lapis_lazuli": "#26619C",   # 青金石藍

    # 漸層色
    "gold_gradient_start": "#FFD700",
    "gold_gradient_end": "#B8860B",
}


def get_sassanian_color_palette() -> Dict[str, str]:
    """
    獲取薩珊色彩調色盤

    Returns
    -------
    Dict[str, str]
        色彩名稱到 HEX 值的映射
    """
    return SASSANIAN_COLOR_PALETTE.copy()


def get_pahlavi_name(category: str, name: str) -> Optional[Dict]:
    """
    獲取 Pahlavi 名稱和相關資訊

    Parameters
    ----------
    category : str
        類別："planets", "zodiac_signs", 或 "houses"
    name : str
        英文名稱（如 "Sun", "Aries", "1"）

    Returns
    -------
    Optional[Dict]
        包含 Pahlavi 名稱、轉寫、符號的字典

    References
    ----------
    - Dorotheus of Sidon, Pahlavi translation (Pingree, 1976)
    - Greater Bundahishn
    """
    pahlavi_path = os.path.join(_CURRENT_DIR, "data", "pahlavi_names.json")

    try:
        with open(pahlavi_path, "r", encoding="utf-8") as f:
            pahlavi_data = json.load(f)

        if category in pahlavi_data:
            if name in pahlavi_data[category]:
                return pahlavi_data[category][name]

        return None
    except Exception as e:
        print(f"Error loading Pahlavi names: {e}")
        return None


def get_royal_star_pahlavi(star_name: str) -> Optional[Dict]:
    """
    獲取皇家恆星的 Pahlavi 名稱和資訊

    Parameters
    ----------
    star_name : str
        恆星英文名稱（"Aldebaran", "Regulus", "Antares", "Fomalhaut"）

    Returns
    -------
    Optional[Dict]
        皇家恆星資訊

    References
    ----------
    - Greater Bundahishn, Chapter II
    - Al-Biruni, "The Chronology of Ancient Nations"
    """
    royal_stars_path = os.path.join(_CURRENT_DIR, "data", "royal_stars.json")

    try:
        with open(royal_stars_path, "r", encoding="utf-8") as f:
            royal_stars_data = json.load(f)

        if star_name in royal_stars_data["royal_stars"]:
            return royal_stars_data["royal_stars"][star_name]

        return None
    except Exception as e:
        print(f"Error loading royal stars: {e}")
        return None


def render_faravahar_element(x: float, y: float, size: float = 50) -> str:
    """
    渲染 Faravahar 翅膀元素（SVG 格式）

    Faravahar 是瑣羅亞斯德教的象徵，在薩珊藝術中常見
    此處簡化為翅膀元素用於角落裝飾

    Parameters
    ----------
    x : float
        X 座標
    y : float
        Y 座標
    size : float
        尺寸

    Returns
    -------
    str
        SVG 路徑字串

    References
    ----------
    - Faravahar symbol from Persepolis reliefs
    - Sassanian rock art at Taq-e Bostan
    """
    palette = get_sassanian_color_palette()

    # Faravahar 翅膀簡化 SVG 路徑
    svg = f'''
    <g class="faravahar-element" transform="translate({x}, {y})">
        <!-- 左翼 -->
        <path d="M 0,0 Q -{size*0.8},{size*0.3} -{size*1.2},{size*0.8}
                 Q -{size*0.8},{size*0.6} -{size*0.4},{size*0.2}
                 Q -{size*0.6},{size*0.4} -{size*0.2},{size*0.1} Z"
              fill="{palette['gold_leaf']}" 
              stroke="{palette['crimson']}" 
              stroke-width="2"
              opacity="0.7"/>
        <!-- 右翼 -->
        <path d="M 0,0 Q {size*0.8},{size*0.3} {size*1.2},{size*0.8}
                 Q {size*0.8},{size*0.6} {size*0.4},{size*0.2}
                 Q {size*0.6},{size*0.4} {size*0.2},{size*0.1} Z"
              fill="{palette['gold_leaf']}" 
              stroke="{palette['crimson']}" 
              stroke-width="2"
              opacity="0.7"/>
        <!-- 中央圓環 -->
        <circle cx="0" cy="0" r="{size*0.15}" 
                fill="{palette['turquoise']}" 
                stroke="{palette['gold_leaf']}" 
                stroke-width="2"/>
    </g>
    '''
    return svg


def render_eight_pointed_star(x: float, y: float, size: float = 30) -> str:
    """
    渲染八瓣玫瑰星（薩珊恆星標記）

    八芒星是薩珊藝術中常見的恆星象徵

    Parameters
    ----------
    x : float
        X 座標
    y : float
        Y 座標
    size : float
        尺寸

    Returns
    -------
    str
        SVG 路徑字串

    References
    ----------
    - Sassanian silver plates with star motifs
    - Early Persian manuscript illuminations
    """
    palette = get_sassanian_color_palette()

    # 八芒星 SVG
    svg = f'''
    <g class="eight-pointed-star" transform="translate({x}, {y})">
        <!-- 外層四角星 -->
        <path d="M 0,-{size} L {size*0.4},-{size*0.4} L {size},0 L {size*0.4},{size*0.4}
                 L 0,{size} L -{size*0.4},{size*0.4} L -{size},0 L -{size*0.4},-{size*0.4} Z"
              fill="{palette['gold_leaf']}" 
              stroke="{palette['crimson']}" 
              stroke-width="2"/>
        <!-- 內層四角星 -->
        <path d="M 0,-{size*0.6} L {size*0.6},0 L 0,{size*0.6} L -{size*0.6},0 Z"
              fill="{palette['turquoise']}" 
              stroke="{palette['gold_leaf']}" 
              stroke-width="1.5"/>
        <!-- 中央圓點 -->
        <circle cx="0" cy="0" r="{size*0.15}" fill="{palette['white']}"/>
    </g>
    '''
    return svg


def render_fire_altar(x: float, y: float, size: float = 40) -> str:
    """
    渲染火壇符號（上升點標記）

    火壇是瑣羅亞斯德教的神聖象徵

    Parameters
    ----------
    x : float
        X 座標
    y : float
        Y 座標
    size : float
        尺寸

    Returns
    -------
    str
        SVG 路徑字串

    References
    ----------
    - Sassanian fire temples
    - Fire altar depictions on Sassanian coins
    """
    palette = get_sassanian_color_palette()

    svg = f'''
    <g class="fire-altar" transform="translate({x}, {y})">
        <!-- 基座 -->
        <rect x="-{size*0.4}" y="{size*0.3}" width="{size*0.8}" height="{size*0.4}"
              fill="{palette['bronze']}" stroke="{palette['crimson']}" stroke-width="2"/>
        <!-- 火壇主體 -->
        <rect x="-{size*0.3}" y="-{size*0.2}" width="{size*0.6}" height="{size*0.5}"
              fill="{palette['burnt_orange']}" stroke="{palette['gold_leaf']}" stroke-width="2"/>
        <!-- 火焰 -->
        <path d="M 0,-{size*0.2} Q -{size*0.2},-{size*0.5} 0,-{size*0.8}
                 Q {size*0.2},-{size*0.5} 0,-{size*0.2}"
              fill="{palette['gold_leaf']}" stroke="{palette['crimson']}" stroke-width="1"/>
        <path d="M 0,-{size*0.3} Q -{size*0.15},-{size*0.5} 0,-{size*0.7}
                 Q {size*0.15},-{size*0.5} 0,-{size*0.3}"
              fill="{palette['turquoise']}" opacity="0.6"/>
    </g>
    '''
    return svg


def render_pomegranate_border(x: float, y: float, width: float, height: float) -> str:
    """
    渲染石榴/葡萄藤邊框

    Parameters
    ----------
    x : float
        X 座標（左上角）
    y : float
        Y 座標（左上角）
    width : float
        寬度
    height : float
        高度

    Returns
    -------
    str
        SVG 路徑字串

    References
    ----------
    - Sassanian textile patterns
    - Pomegranate motifs in Persian art
    """
    palette = get_sassanian_color_palette()

    # 簡化的石榴圖案邊框
    border_thickness = 8
    pattern_size = 30

    svg = f'''
    <g class="pomegranate-border">
        <!-- 外框 -->
        <rect x="{x}" y="{y}" width="{width}" height="{height}"
              fill="none" stroke="{palette['gold_leaf']}" stroke-width="{border_thickness}"/>
        <!-- 內框 -->
        <rect x="{x+border_thickness}" y="{y+border_thickness}" 
              width="{width-border_thickness*2}" height="{height-border_thickness*2}"
              fill="none" stroke="{palette['crimson']}" stroke-width="2"/>
        <!-- 角落裝飾（石榴） -->
        <circle cx="{x+border_thickness*2}" cy="{y+border_thickness*2}" r="10"
                fill="{palette['crimson']}" stroke="{palette['gold_leaf']}" stroke-width="2"/>
        <circle cx="{x+width-border_thickness*2}" cy="{y+border_thickness*2}" r="10"
                fill="{palette['crimson']}" stroke="{palette['gold_leaf']}" stroke-width="2"/>
        <circle cx="{x+border_thickness*2}" cy="{y+height-border_thickness*2}" r="10"
                fill="{palette['crimson']}" stroke="{palette['gold_leaf']}" stroke-width="2"/>
        <circle cx="{x+width-border_thickness*2}" cy="{y+height-border_thickness*2}" r="10"
                fill="{palette['crimson']}" stroke="{palette['gold_leaf']}" stroke-width="2"/>
    </g>
    '''
    return svg


def get_zodiac_glyph(sign: str) -> str:
    """
    獲取星座符號

    Parameters
    ----------
    sign : str
        星座英文名稱

    Returns
    -------
    str
        星座符號（Unicode）
    """
    glyphs = {
        "Aries": "♈",
        "Taurus": "♉",
        "Gemini": "♊",
        "Cancer": "♋",
        "Leo": "♌",
        "Virgo": "♍",
        "Libra": "♎",
        "Scorpio": "♏",
        "Sagittarius": "♐",
        "Capricorn": "♑",
        "Aquarius": "♒",
        "Pisces": "♓",
    }
    return glyphs.get(sign, "")


def get_planet_glyph(planet: str) -> str:
    """
    獲取行星符號

    Parameters
    ----------
    planet : str
        行星英文名稱

    Returns
    -------
    str
        行星符號（Unicode）
    """
    glyphs = {
        "Sun": "☉",
        "Moon": "☽",
        "Mercury": "☿",
        "Venus": "♀",
        "Mars": "♂",
        "Jupiter": "♃",
        "Saturn": "♄",
    }
    return glyphs.get(planet, "")


if __name__ == "__main__":
    # 測試薩珊符號系統
    print("=" * 60)
    print("薩珊符號系統測試 (Sassanian Symbols Test)")
    print("=" * 60)

    # 測試色彩調色盤
    print("\n薩珊色彩調色盤:")
    palette = get_sassanian_color_palette()
    for color_name, color_hex in palette.items():
        print(f"  {color_name:<20}: {color_hex}")

    # 測試 Pahlavi 名稱
    print("\n行星 Pahlavi 名稱:")
    for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        info = get_pahlavi_name("planets", planet)
        if info:
            print(f"  {planet:<10}: {info['pahlavi']} ({info['transliteration']})")

    print("\n星座 Pahlavi 名稱:")
    for sign in ["Aries", "Taurus", "Leo", "Scorpio"]:
        info = get_pahlavi_name("zodiac_signs", sign)
        if info:
            print(f"  {sign:<12}: {info['pahlavi']} ({info['transliteration']})")

    # 測試皇家恆星
    print("\n四顆皇家恆星:")
    for star in ["Aldebaran", "Regulus", "Antares", "Fomalhaut"]:
        info = get_royal_star_pahlavi(star)
        if info:
            print(f"  {info['name_pahlavi']:>12} ({info['name_en']:>10}): "
                  f"{info['sassanian_longitude']:.1f}° in {info['constellation']}")

    # 測試 SVG 元素生成
    print("\nSVG 元素生成測試:")
    faravahar = render_faravahar_element(100, 100, 50)
    print(f"  Faravahar element: {len(faravahar)} chars")

    star = render_eight_pointed_star(200, 200, 30)
    print(f"  Eight-pointed star: {len(star)} chars")

    fire_altar = render_fire_altar(150, 150, 40)
    print(f"  Fire altar: {len(fire_altar)} chars")

    border = render_pomegranate_border(0, 0, 400, 400)
    print(f"  Pomegranate border: {len(border)} chars")

    print("\n" + "=" * 60)
    print("測試完成")
