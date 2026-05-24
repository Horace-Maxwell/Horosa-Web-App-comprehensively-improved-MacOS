"""
astro/sabian.py — Sabian Symbols (Marc Edmund Jones, 1953 Original)

薩比恩符號：360 個黃道度數的象徵圖像
嚴格按照 Marc Edmund Jones《The Sabian Symbols in Astrology》(1953) 原著

核心功能：
1. get_sabian_symbol(longitude) — 根據行星經度獲取對應符號
2. get_sabian_for_planet(chart_data, planet) — 獲取特定行星的 Sabian Symbol
3. render_sabian_svg(longitude) — 生成 SVG 符號卡片
4. to_context_sabian() — 與 context_serializer.py 整合

References
----------
- Jones, Marc Edmund (1953). "The Sabian Symbols in Astrology"
- NOT Lynda Hill or modern reinterpretations
"""

import json
import math
import os
from typing import Dict, List, Optional, Any
from pathlib import Path


# ============================================================================
# CONSTANTS
# ============================================================================

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

ZODIAC_SIGNS_ZH = [
    "白羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座",
    "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座"
]

# Path to Sabian symbols JSON data
SABIAN_DATA_PATH = Path(__file__).parent / "data" / "sabian_symbols.json"


# ============================================================================
# DATA LOADING
# ============================================================================

def load_sabian_symbols() -> List[Dict[str, Any]]:
    """
    載入 360 個 Sabian Symbols（Jones 1953 原著）
    
    Returns
    -------
    List[Dict[str, Any]]
        包含 360 個符號的列表，每個符號包含：
        - degree: 1-360
        - sign: 星座英文名
        - degree_in_sign: 星座內度數 (1-30)
        - symbol: 象徵圖像（Jones 原著 exact wording）
        - keyword: 關鍵詞
        - positive: 正面意義
        - negative: 負面意義
        - formula: Jones 公式
        - interpretation: 心理意義簡述
    """
    if not SABIAN_DATA_PATH.exists():
        raise FileNotFoundError(f"Sabian symbols data not found: {SABIAN_DATA_PATH}")
    
    with open(SABIAN_DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if len(data) != 360:
        raise ValueError(f"Expected 360 symbols, got {len(data)}")
    
    return data


# Cache loaded symbols
_SABIAN_SYMBOLS_CACHE: Optional[List[Dict[str, Any]]] = None


def _get_symbols() -> List[Dict[str, Any]]:
    """Get cached symbols."""
    global _SABIAN_SYMBOLS_CACHE
    if _SABIAN_SYMBOLS_CACHE is None:
        _SABIAN_SYMBOLS_CACHE = load_sabian_symbols()
    return _SABIAN_SYMBOLS_CACHE


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def get_sabian_symbol(longitude: float) -> Dict[str, Any]:
    """
    根據行星經度獲取對應的 Sabian Symbol
    
    Parameters
    ----------
    longitude : float
        行星經度（0-360 度）
    
    Returns
    -------
    Dict[str, Any]
        符號資料，包含 symbol, keyword, positive, negative, formula, interpretation
    
    Raises
    ------
    ValueError
        如果經度不在 0-360 範圍內
    
    Examples
    --------
    >>> get_sabian_symbol(0.5)  # Aries 1°
    {'degree': 1, 'sign': 'Aries', 'symbol': 'A woman has risen out of the ocean...'}
    """
    if not 0 <= longitude < 360:
        raise ValueError(f"Longitude must be 0-360, got {longitude}")
    
    # Convert to 1-indexed degree (1-360)
    degree_index = int(longitude) + 1
    if degree_index > 360:
        degree_index = 360
    
    symbols = _get_symbols()
    return symbols[degree_index - 1]


def get_sabian_for_planet(chart_data: Dict[str, Any], planet: str) -> Dict[str, Any]:
    """
    獲取特定行星的 Sabian Symbol
    
    Parameters
    ----------
    chart_data : Dict[str, Any]
        星盤資料，必須包含行星經度資訊
        格式：{'planets': [{'name': 'Sun', 'longitude': 45.5}, ...]}
    planet : str
        行星名稱（英文或中文）
        支援：Sun/Moon/Mercury/Venus/Mars/Jupiter/Saturn/Uranus/Neptune/Pluto
        或中文：太陽/月亮/水星/金星/火星/木星/土星/天王星/海王星/冥王星
    
    Returns
    -------
    Dict[str, Any]
        該行星的 Sabian Symbol 資料
    
    Raises
    ------
    ValueError
        如果找不到該行星
    
    Examples
    --------
    >>> chart = {'planets': [{'name': 'Sun', 'longitude': 45.5}]}
    >>> get_sabian_for_planet(chart, 'Sun')
    {'degree': 46, 'sign': 'Taurus', 'symbol': '...'}
    """
    # Planet name mapping
    planet_map = {
        'sun': 'Sun', '太陽': 'Sun',
        'moon': 'Moon', '月亮': 'Moon',
        'mercury': 'Mercury', '水星': 'Mercury',
        'venus': 'Venus', '金星': 'Venus',
        'mars': 'Mars', '火星': 'Mars',
        'jupiter': 'Jupiter', '木星': 'Jupiter',
        'saturn': 'Saturn', '土星': 'Saturn',
        'uranus': 'Uranus', '天王星': 'Uranus',
        'neptune': 'Neptune', '海王星': 'Neptune',
        'pluto': 'Pluto', '冥王星': 'Pluto',
        'ascendant': 'Ascendant', '上升': 'Ascendant', 'asc': 'Ascendant',
        'midheaven': 'Midheaven', '中天': 'Midheaven', 'mc': 'Midheaven',
    }
    
    planet_std = planet_map.get(planet.lower(), planet)
    
    # Handle Ascendant and Midheaven specially
    if planet_std in ['Ascendant', 'Midheaven']:
        # Try to find in chart_data directly
        if planet_std == 'Ascendant' and 'ascendant' in chart_data:
            asc_lon = chart_data.get('ascendant', 0)
            result = get_sabian_symbol(asc_lon)
            result['planet_longitude'] = asc_lon
            return result
        elif planet_std == 'Midheaven' and 'midheaven' in chart_data:
            mc_lon = chart_data.get('midheaven', 0)
            result = get_sabian_symbol(mc_lon)
            result['planet_longitude'] = mc_lon
            return result
        # Try to get from WesternChart object attributes
        if hasattr(chart_data, 'ascendant') and planet_std == 'Ascendant':
            result = get_sabian_symbol(chart_data.ascendant)
            result['planet_longitude'] = chart_data.ascendant
            return result
        if hasattr(chart_data, 'midheaven') and planet_std == 'Midheaven':
            result = get_sabian_symbol(chart_data.midheaven)
            result['planet_longitude'] = chart_data.midheaven
            return result
        raise ValueError(f"{planet_std} not found in chart data")
    
    planets = chart_data.get('planets', [])
    for p in planets:
        # Handle both dict and WesternPlanet dataclass
        if hasattr(p, 'name'):
            # WesternPlanet dataclass object
            p_name = p.name
            p_longitude = p.longitude
        else:
            # Dictionary
            p_name = p.get('name')
            p_longitude = p.get('longitude')
        
        # Match planet name with or without glyph symbols
        # e.g., "Sun ☉" matches "Sun", "Moon ☽" matches "Moon"
        p_name_clean = p_name.split()[0] if p_name else None
        
        if p_name_clean == planet_std or p_name == planet_std:
            result = get_sabian_symbol(p_longitude)
            # Add planet longitude to result for SVG rendering
            result['planet_longitude'] = p_longitude
            return result
    
    raise ValueError(f"Planet not found: {planet}")


def get_sign_longitudinal_degree(longitude: float) -> tuple:
    """
    將經度轉換為星座和星座內度數
    
    Parameters
    ----------
    longitude : float
        行星經度（0-360 度）
    
    Returns
    -------
    tuple
        (sign_index, degree_in_sign, sign_name, sign_name_zh)
        sign_index: 0-11
        degree_in_sign: 1-30
        sign_name: 星座英文名
        sign_name_zh: 星座中文名
    """
    sign_index = int(longitude) // 30
    degree_in_sign = int(longitude) % 30 + 1
    return (
        sign_index,
        degree_in_sign,
        ZODIAC_SIGNS[sign_index],
        ZODIAC_SIGNS_ZH[sign_index]
    )


# ============================================================================
# SVG RENDERING
# ============================================================================

def render_sabian_svg(longitude: float, size: int = 300, language: str = "zh") -> str:
    """
    生成 Sabian Symbol SVG 卡片（響應式，適配各種螢幕寬度）
    """
    symbol_data = get_sabian_symbol(longitude)
    sign_idx, deg_in_sign, sign_en, sign_zh = get_sign_longitudinal_degree(longitude)

    # Color scheme based on element
    element_colors = {
        "fire":  {"bg": "#FFF5F0", "accent": "#C84B1A", "text": "#6B1700", "light": "#FFDDD0"},
        "earth": {"bg": "#F5F8F0", "accent": "#4A7C3F", "text": "#2D4A22", "light": "#D6EDCC"},
        "air":   {"bg": "#F0F5FC", "accent": "#3A6DAE", "text": "#1A3560", "light": "#D0E4F8"},
        "water": {"bg": "#EFF5FB", "accent": "#1F6E8C", "text": "#0D3D52", "light": "#C8E6F4"},
    }

    elements = ["fire", "earth", "air", "water", "fire", "earth",
                "air", "water", "fire", "earth", "air", "water"]
    element = elements[sign_idx]
    colors = element_colors[element]

    element_label = {"fire": "🔥 火象", "earth": "🌿 土象", "air": "💨 風象", "water": "💧 水象"}
    element_en    = {"fire": "Fire", "earth": "Earth", "air": "Air", "water": "Water"}

    # 星座符號
    zodiac_glyphs = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
    sign_glyph = zodiac_glyphs[sign_idx]

    if language == "zh":
        sign_display = f"{sign_zh} {deg_in_sign}°"
        keyword_label = "關鍵詞"
        elem_display = element_label[element]
        source_text = "Marc Edmund Jones (1953)"
    else:
        sign_display = f"{sign_en} {deg_in_sign}°"
        keyword_label = "Keyword"
        elem_display = element_en[element]
        source_text = "Marc Edmund Jones (1953)"

    # SVG 尺寸（響應式：viewBox 固定，width="100%"）
    vw, vh = 300, 420

    # 分割符號文字（每行最多 32 字符）
    symbol_text = symbol_data['symbol']
    words = symbol_text.split()
    lines: List[str] = []
    current_line = ""
    for word in words:
        test = (current_line + " " + word).strip()
        if len(test) <= 32:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # 動態計算文字區高度
    line_h = 24
    symbol_block_h = max(70, len(lines) * line_h + 20)
    total_content_h = 130 + symbol_block_h + 80  # header + symbol + keyword+footer
    vh = max(380, total_content_h)

    # 黃道輪弧形裝飾（頂部）：顯示度數在 360° 中的位置
    arc_deg = (longitude / 360) * 340  # 映射到 340° 弧
    # SVG arc 計算：從 -170° 到 170° (以 top 為 0°)
    r = 28
    angle_start = math.radians(-170)
    angle_end   = math.radians(-170 + arc_deg)
    ax1 = vw/2 + r * math.sin(angle_start)
    ay1 = 38  + r * (-math.cos(angle_start))
    ax2 = vw/2 + r * math.sin(angle_end)
    ay2 = 38  + r * (-math.cos(angle_end))
    large_arc = 1 if arc_deg > 180 else 0

    svg = f'''<svg width="100%" viewBox="0 0 {vw} {vh}" xmlns="http://www.w3.org/2000/svg"
     style="max-width:{size}px;display:block;margin:0 auto">
  <defs>
    <linearGradient id="sabGrad{sign_idx}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   style="stop-color:{colors['bg']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#FFFFFF;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="arcGrad{sign_idx}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   style="stop-color:{colors['accent']};stop-opacity:0.3"/>
      <stop offset="100%" style="stop-color:{colors['accent']};stop-opacity:1"/>
    </linearGradient>
  </defs>

  <!-- 背景 -->
  <rect width="{vw}" height="{vh}" fill="url(#sabGrad{sign_idx})" rx="14" ry="14"/>
  <!-- 外框 -->
  <rect width="{vw}" height="{vh}" fill="none" stroke="{colors['accent']}" stroke-width="2.5"
        rx="14" ry="14"/>
  <!-- 頂部裝飾色帶 -->
  <rect width="{vw}" height="76" fill="{colors['accent']}" opacity="0.12" rx="14" ry="14"/>
  <rect width="{vw}" height="5" y="71" fill="{colors['accent']}" opacity="0.3"/>

  <!-- 黃道輪弧（度數進度） -->
  <circle cx="{vw/2}" cy="38" r="{r}" fill="none" stroke="{colors['light']}" stroke-width="5"/>
  <path d="M {ax1:.1f},{ay1:.1f} A {r},{r} 0 {large_arc},1 {ax2:.1f},{ay2:.1f}"
        fill="none" stroke="url(#arcGrad{sign_idx})" stroke-width="5" stroke-linecap="round"/>
  <!-- 度數圓圈 -->
  <circle cx="{vw/2}" cy="38" r="18" fill="{colors['accent']}" opacity="0.92"/>
  <text x="{vw/2}" y="44" text-anchor="middle" font-family="Arial,sans-serif"
        font-size="16" font-weight="bold" fill="white">{deg_in_sign}</text>

  <!-- 星座符號（右上） -->
  <text x="{vw-28}" y="34" text-anchor="middle" font-family="serif"
        font-size="26" fill="{colors['accent']}" opacity="0.85">{sign_glyph}</text>

  <!-- 元素標籤（左上） -->
  <text x="14" y="20" font-family="Arial,sans-serif" font-size="10"
        fill="{colors['accent']}" opacity="0.8">{elem_display}</text>

  <!-- 星座 + 度數標題 -->
  <text x="{vw/2}" y="68" text-anchor="middle" font-family="'Noto Serif','Georgia',serif"
        font-size="18" font-weight="bold" fill="{colors['text']}">{sign_display}</text>

  <!-- 分隔線 -->
  <line x1="24" y1="82" x2="{vw-24}" y2="82" stroke="{colors['accent']}" stroke-width="1.5" opacity="0.5"/>

  <!-- 符號文字 -->
'''

    # 添加符號文字行
    text_y = 106
    for line in lines:
        # 轉義 HTML 特殊字符
        esc_line = (line.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace('"', "&quot;"))
        svg += (f'  <text x="{vw/2}" y="{text_y}" text-anchor="middle" '
                f'font-family="\'Georgia\',\'Noto Serif\',serif" font-size="14" '
                f'fill="{colors["text"]}" font-style="italic">{esc_line}</text>\n')
        text_y += line_h

    # 關鍵詞區
    kw_y = text_y + 22
    kw_box_h = 36
    svg += f'''
  <!-- 關鍵詞背景 -->
  <rect x="18" y="{kw_y - 22}" width="{vw - 36}" height="{kw_box_h}"
        rx="8" fill="{colors['accent']}" opacity="0.1"/>
  <text x="{vw/2}" y="{kw_y}" text-anchor="middle" font-family="Arial,sans-serif"
        font-size="12" fill="{colors['accent']}" opacity="0.75">{keyword_label}</text>
  <text x="{vw/2}" y="{kw_y + 16}" text-anchor="middle" font-family="Arial,sans-serif"
        font-size="15" font-weight="bold" fill="{colors['accent']}">{symbol_data['keyword']}</text>

  <!-- 正負面意義 -->
  <line x1="24" y1="{kw_y + 30}" x2="{vw-24}" y2="{kw_y + 30}"
        stroke="{colors['accent']}" stroke-width="1" opacity="0.3"/>

  <!-- 底部來源 -->
  <text x="{vw/2}" y="{vh - 10}" text-anchor="middle" font-family="Arial,sans-serif"
        font-size="9.5" fill="{colors['text']}" opacity="0.5">{source_text}</text>
</svg>'''

    return svg


# ============================================================================
# CONTEXT SERIALIZER INTEGRATION
# ============================================================================

def to_context_sabian(longitude: float, planet_name: str = "") -> str:
    """
    將 Sabian Symbol 轉換為 XML format，供 context_serializer.py 使用
    
    Parameters
    ----------
    longitude : float
        行星經度（0-360 度）
    planet_name : str
        行星名稱（可選）
    
    Returns
    -------
    str
        XML format 的 Sabian Symbol 資料
    
    Examples
    --------
    >>> xml = to_context_sabian(45.5, "Sun")
    >>> "<sabian_symbol" in xml
    True
    """
    symbol_data = get_sabian_symbol(longitude)
    sign_idx, deg_in_sign, sign_en, sign_zh = get_sign_longitudinal_degree(longitude)
    
    planet_xml = f' planet="{planet_name}"' if planet_name else ""
    
    xml = f'''<sabian_symbol{planet_xml} degree="{symbol_data['degree']}" 
    sign="{sign_en}" sign_zh="{sign_zh}" degree_in_sign="{deg_in_sign}">
    <symbol>{symbol_data['symbol']}</symbol>
    <keyword>{symbol_data['keyword']}</keyword>
    <positive>{symbol_data['positive']}</positive>
    <negative>{symbol_data['negative']}</negative>
    <formula>{symbol_data['formula']}</formula>
    <interpretation>{symbol_data['interpretation']}</interpretation>
</sabian_symbol>'''
    
    return xml


# ============================================================================
# CROSS-COMPARE INTEGRATION
# ============================================================================

def compare_sabian_with_western(western_data: Dict[str, Any], longitude: float) -> Dict[str, Any]:
    """
    將 Sabian Symbol 與西洋占星資料做對比
    
    Parameters
    ----------
    western_data : Dict[str, Any]
        西洋占星資料（行星位置、星座、宮位等）
    longitude : float
        行星經度
    
    Returns
    -------
    Dict[str, Any]
        包含西洋占星與 Sabian Symbol 的對比資料
    """
    sabian = get_sabian_symbol(longitude)
    sign_idx, deg_in_sign, sign_en, sign_zh = get_sign_longitudinal_degree(longitude)
    
    return {
        "longitude": longitude,
        "western": {
            "sign": sign_en,
            "sign_zh": sign_zh,
            "degree_in_sign": deg_in_sign,
            **western_data
        },
        "sabian": {
            "symbol": sabian['symbol'],
            "keyword": sabian['keyword'],
            "formula": sabian['formula'],
            "interpretation": sabian['interpretation'],
        }
    }


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == "__main__":
    # Test with sample birth data
    print("=" * 60)
    print("Sabian Symbols Test — Marc Edmund Jones (1953) Original")
    print("=" * 60)
    
    # Sample data: Sun at 15° Aries, Moon at 23° Cancer
    test_planets = [
        {"name": "Sun", "longitude": 15.0},    # Aries 16°
        {"name": "Moon", "longitude": 113.0},  # Cancer 24°
        {"name": "Mercury", "longitude": 5.5}, # Aries 6°
        {"name": "Venus", "longitude": 45.5},  # Taurus 16°
    ]
    
    print("\n🔮 Sample Birth Chart Sabian Symbols:\n")
    
    for planet in test_planets:
        symbol = get_sabian_symbol(planet["longitude"])
        sign_idx, deg_in_sign, sign_en, sign_zh = get_sign_longitudinal_degree(planet["longitude"])
        
        print(f"{'─' * 58}")
        print(f"{planet['name']} — {sign_zh} {deg_in_sign}° ({planet['longitude']:.1f}°)")
        print(f"{'─' * 58}")
        print(f"Symbol:   {symbol['symbol']}")
        print(f"Keyword:  {symbol['keyword']}")
        print(f"Formula:  {symbol['formula']}")
        print(f"Meaning:  {symbol['interpretation']}")
        print()
    
    # Test SVG rendering
    print("\n🎨 Testing SVG rendering...")
    svg = render_sabian_svg(15.0, size=300, language="zh")
    print(f"SVG generated: {len(svg)} characters")
    print(f"SVG preview: {svg[:200]}...")
    
    # Test XML serialization
    print("\n📄 Testing XML serialization...")
    xml = to_context_sabian(15.0, "Sun")
    print(f"XML generated: {len(xml)} characters")
    print(f"XML preview: {xml[:300]}...")
    
    # Test cross-compare
    print("\n🔍 Testing cross-compare...")
    western_data = {"house": 1, "aspect": "conjunct Ascendant"}
    comparison = compare_sabian_with_western(western_data, 15.0)
    print(f"Western sign: {comparison['western']['sign_zh']}")
    print(f"Sabian keyword: {comparison['sabian']['keyword']}")
    
    print("\n✅ All tests passed!")
