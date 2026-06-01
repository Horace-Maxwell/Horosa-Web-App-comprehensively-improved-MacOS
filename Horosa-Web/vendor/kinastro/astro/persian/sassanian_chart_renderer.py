"""
astro/persian/sassanian_chart_renderer.py — 薩珊傳統占星星盤渲染器（純 SVG 版本）

Sassanian Traditional Star Chart Renderer (Pure SVG)
基於用戶提供的菱形 12 宮設計，完全按照參考 SVG 結構

References
----------
- Sassanian silver plates (Metropolitan Museum, Louvre)
- Taq-e Bostan rock reliefs (6th-7th century CE)
- Greater Bundahishn illustrations
- Dorotheus of Sidon, Pahlavi translation (Pingree, 1976)
"""

from typing import Dict, List, Optional
import swisseph as swe
import json
import os
import base64

from astro.persian.sassanian_astronomy import (
    compute_sassanian_planet_positions,
    get_sassanian_houses,
    get_royal_stars_positions,
    SassanianPlanetPosition,
)
from astro.persian.sassanian_symbols import (
    get_sassanian_color_palette,
    get_pahlavi_name,
    get_royal_star_pahlavi,
    get_zodiac_glyph,
    get_planet_glyph,
)

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_sassanian_svg(
    chart_data: Dict,
    width: int = 500,
    height: int = 650,
    show_pahlavi: bool = True,
    show_royal_stars: bool = True,
    show_firdar: bool = True,
) -> str:
    """
    生成薩珊傳統占星星盤（純 SVG 格式）
    
    完全按照用戶提供的菱形 12 宮設計：
    - 外框正方形
    - 內框正方形（菱形）
    - 對角線連接形成 12 宮
    - 星座符號在外圍 12 個位置

    Parameters
    ----------
    chart_data : Dict
        星盤資料
    width : int
        SVG 寬度（像素）
    height : int
        SVG 高度（像素）
    show_pahlavi : bool
        是否顯示 Pahlavi 文字
    show_royal_stars : bool
        是否顯示皇家恆星
    show_firdar : bool
        是否顯示 Firdar 時間線

    Returns
    -------
    str
        SVG 字串
    """
    palette = get_sassanian_color_palette()

    # 提取出生資料
    year = chart_data.get("year")
    month = chart_data.get("month")
    day = chart_data.get("day")
    hour = chart_data.get("hour", 12)
    minute = chart_data.get("minute", 0)
    longitude = chart_data.get("longitude", 0)
    latitude = chart_data.get("latitude", 0)
    timezone = chart_data.get("timezone", 0)

    # 計算儒略日
    julian_day = swe.julday(year, month, day, hour + minute / 60.0)

    # 計算薩珊行星位置
    planet_positions = compute_sassanian_planet_positions(
        year, month, day, hour, minute,
        longitude, latitude, timezone
    )

    # 計算薩珊宮位
    houses = get_sassanian_houses(
        year, month, day, hour, minute,
        longitude, latitude, timezone
    )

    # 獲取皇家恆星位置
    royal_stars = get_royal_stars_positions(julian_day) if show_royal_stars else {}

    # 計算縮放比例（基於 viewBox 500x650）
    base_width = 500
    base_height = 650
    scale_x = width / base_width
    scale_y = height / base_height
    scale = min(scale_x, scale_y)
    
    # viewBox 始終保持 500x650 座標系統（增加 50px 給 Firdar 時間線）
    viewBox = f"0 0 {base_width} {base_height}"
    
    # 計算幾何結構（完全按照參考 SVG，使用 500x650 座標系統）
    # 外框：x=50, y=100, width=400, height=400
    outer_x = 50
    outer_y = 100
    outer_width = 400
    outer_height = 400
    
    # 內框（菱形）：x=150, y=200, width=200, height=200
    inner_x = 150
    inner_y = 200
    inner_width = 200
    inner_height = 200
    
    # 中心點
    center_x = outer_x + outer_width / 2  # 250
    center_y = outer_y + outer_height / 2  # 300

    # 12 宮位區域的星座位置（按照參考 SVG 的 12 個位置）
    # 從頂部開始，順時針方向（使用固定座標，不需縮放）
    zodiac_positions = [
        # 頂部（3 個）
        {"sign_index": 7, "x": center_x, "y": outer_y - 15, "label": "top_center"},  # ♏ Scorpio
        {"sign_index": 8, "x": center_x - outer_width/4, "y": outer_y - 15, "label": "top_left"},  # ♐ Sagittarius
        {"sign_index": 6, "x": center_x + outer_width/4, "y": outer_y - 15, "label": "top_right"},  # ♎ Libra
        
        # 左側（3 個）
        {"sign_index": 9, "x": outer_x - 15, "y": outer_y + outer_height/4, "label": "left_top"},  # ♑ Capricorn
        {"sign_index": 10, "x": outer_x - 15, "y": center_y, "label": "left_center"},  # ♒ Aquarius
        {"sign_index": 11, "x": outer_x - 15, "y": outer_y + outer_height*3/4, "label": "left_bottom"},  # ♓ Pisces
        
        # 底部（3 個）
        {"sign_index": 0, "x": center_x - outer_width/4, "y": outer_y + outer_height + 15, "label": "bottom_left"},  # ♈ Aries
        {"sign_index": 1, "x": center_x, "y": outer_y + outer_height + 15, "label": "bottom_center"},  # ♉ Taurus
        {"sign_index": 2, "x": center_x + outer_width/4, "y": outer_y + outer_height + 15, "label": "bottom_right"},  # ♊ Gemini
        
        # 右側（3 個）
        {"sign_index": 3, "x": outer_x + outer_width + 15, "y": outer_y + outer_height*3/4, "label": "right_bottom"},  # ♋ Cancer
        {"sign_index": 4, "x": outer_x + outer_width + 15, "y": center_y, "label": "right_center"},  # ♌ Leo
        {"sign_index": 5, "x": outer_x + outer_width + 15, "y": outer_y + outer_height/4, "label": "right_top"},  # ♍ Virgo
    ]

    # 宮位元素顏色（薩珊傳統：火土風水輪流，從牡羊起）
    element_colors = [
        palette["burnt_orange"],  # 火 - 牡羊、獅子、射手
        palette["bronze"],        # 土 - 金牛、處女、摩羯
        palette["turquoise"],     # 風 - 雙子、天秤、水瓶
        palette["lapis_lazuli"],  # 水 - 巨蟹、天蠍、雙魚
    ]
    # 每個星座的元素索引 (0=火, 1=土, 2=風, 3=水)
    sign_element = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]

    # 開始構建 SVG
    svg_parts = []

    # SVG 開頭（使用 viewBox 確保正確縮放）
    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="{viewBox}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
  <defs>
    <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{palette['gold_gradient_start']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{palette['gold_gradient_end']};stop-opacity:1" />
    </linearGradient>
    <linearGradient id="parchmentGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{palette['parchment']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#EDD9C0;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{palette['crimson']};stop-opacity:0.12" />
      <stop offset="100%" style="stop-color:{palette['gold_gradient_end']};stop-opacity:0.18" />
    </linearGradient>
    <!-- 裝飾紋樣濾鏡 -->
    <filter id="softGlow">
      <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- 背景（羊皮紙） -->
  <rect width="{base_width}" height="{base_height}" fill="url(#parchmentGradient)" />

  <!-- 外裝飾框（雙層金邊） -->
  <rect x="6" y="6" width="{base_width-12}" height="{base_height-12}"
        rx="4" fill="none" stroke="{palette['gold_leaf']}" stroke-width="3" opacity="0.7"/>
  <rect x="11" y="11" width="{base_width-22}" height="{base_height-22}"
        rx="2" fill="none" stroke="{palette['crimson']}" stroke-width="1.2" opacity="0.5"/>

  <!-- 四角裝飾：八芒星（薩珊皇室紋章） -->
  {_sassanian_corner_star(14, 14, 14, palette['gold_leaf'], palette['crimson'])}
  {_sassanian_corner_star(base_width-14, 14, 14, palette['gold_leaf'], palette['crimson'])}
  {_sassanian_corner_star(14, base_height-14, 14, palette['gold_leaf'], palette['crimson'])}
  {_sassanian_corner_star(base_width-14, base_height-14, 14, palette['gold_leaf'], palette['crimson'])}
''')

    # 標題區（帶裝飾背景）
    title_text = "薩珊傳統占星星盤"
    pahlavi_subtitle = "𐭮𐭠𐭮𐭠𐭭 𐭲𐭠𐭫𐭹𐭹𐭠 · Sassanian Astrology" if show_pahlavi else "Sassanian Astrology · Bundahishn"

    svg_parts.append(f'''
  <!-- 標題背景 -->
  <rect x="30" y="22" width="{base_width-60}" height="70" rx="8" fill="url(#headerGrad)"
        stroke="{palette['gold_leaf']}" stroke-width="1.5"/>
  <!-- 標題裝飾橫線 -->
  <line x1="50" y1="48" x2="{base_width-50}" y2="48"
        stroke="{palette['gold_leaf']}" stroke-width="0.8" opacity="0.6"/>
  <line x1="50" y1="84" x2="{base_width-50}" y2="84"
        stroke="{palette['gold_leaf']}" stroke-width="0.8" opacity="0.6"/>

  <!-- 標題文字 -->
  <text x="{base_width/2}" y="44" font-family="'Noto Serif', serif" font-size="22" font-weight="bold"
        fill="{palette['crimson']}" text-anchor="middle" letter-spacing="4">
    {title_text}
  </text>
  <text x="{base_width/2}" y="78" font-family="serif" font-size="13"
        fill="{palette['dark_indigo']}" text-anchor="middle" letter-spacing="2" font-style="italic">
    {pahlavi_subtitle}
  </text>
''')

    # 12 宮三角形填色（先填色，再畫框線）
    # 定義 12 個三角形的頂點（順時針）
    # 外框四角：(50,100), (450,100), (450,500), (50,500)
    # 外框中點：(250,100), (50,300), (250,500), (450,300)
    # 內框四角：(150,200), (350,200), (350,400), (150,400)
    ox, oy = outer_x, outer_y
    ow, oh = outer_width, outer_height
    cx2, cy2 = center_x, center_y
    ix, iy = inner_x, inner_y
    iw, ih = inner_width, inner_height

    # 12 個宮位三角形頂點（從頂部開始，順時針）
    house_triangles = [
        # 宮位 1 (頂中→頂左角→內左上)
        [(cx2, oy), (ox, oy), (ix, iy)],
        # 宮位 2 (頂左角→左中→內左上)
        [(ox, oy), (ox, cy2), (ix, iy)],
        # 宮位 3 (左中→底左角→內左下)
        [(ox, cy2), (ox, oy+oh), (ix, iy+ih)],
        # 宮位 4 (底左角→底中→內左下)
        [(ox, oy+oh), (cx2, oy+oh), (ix, iy+ih)],
        # 宮位 5 (底中→底右角→內右下)
        [(cx2, oy+oh), (ox+ow, oy+oh), (ix+iw, iy+ih)],
        # 宮位 6 (底右角→右中→內右下)
        [(ox+ow, oy+oh), (ox+ow, cy2), (ix+iw, iy+ih)],
        # 宮位 7 (右中→頂右角→內右上)
        [(ox+ow, cy2), (ox+ow, oy), (ix+iw, iy)],
        # 宮位 8 (頂右角→頂中→內右上)
        [(ox+ow, oy), (cx2, oy), (ix+iw, iy)],
        # 內框四個三角（菱形被對角線分割）
        # 宮位 9 (內上)
        [(ix, iy), (cx2, oy), (ix+iw, iy)],
        # 宮位 10 (內右)
        [(ix+iw, iy), (ox+ow, cy2), (ix+iw, iy+ih)],
        # 宮位 11 (內下)
        [(ix+iw, iy+ih), (cx2, oy+oh), (ix, iy+ih)],
        # 宮位 12 (內左)
        [(ix, iy+ih), (ox, cy2), (ix, iy)],
    ]

    svg_parts.append('\n  <!-- 12 宮位填色 -->\n')
    for i, triangle in enumerate(house_triangles):
        # zodiac_positions and house_triangles both have exactly 12 entries
        sign_idx = zodiac_positions[i]["sign_index"]
        elem_idx = sign_element[sign_idx % 12]
        fill_color = element_colors[elem_idx]
        pts = " ".join(f"{p[0]},{p[1]}" for p in triangle)
        svg_parts.append(
            f'  <polygon points="{pts}" fill="{fill_color}" opacity="0.12" stroke="none"/>\n'
        )

    # 星盤框架（完全按照參考 SVG）
    svg_parts.append(f'''
  <!-- 星盤框架 -->
  <g stroke="{palette['crimson']}" stroke-width="2" fill="none">
    <!-- 外框正方形（金色雙線） -->
    <rect x="{outer_x}" y="{outer_y}" width="{outer_width}" height="{outer_height}"
          stroke="{palette['gold_leaf']}" stroke-width="3"/>
    <rect x="{outer_x+3}" y="{outer_y+3}" width="{outer_width-6}" height="{outer_height-6}"
          stroke="{palette['crimson']}" stroke-width="1" opacity="0.5"/>

    <!-- 內框正方形（菱形，金色） -->
    <rect x="{inner_x}" y="{inner_y}" width="{inner_width}" height="{inner_height}"
          stroke="{palette['gold_leaf']}" stroke-width="2.5"/>

    <!-- 四角對角線 -->
    <line x1="{outer_x}" y1="{outer_y}" x2="{inner_x}" y2="{inner_y}" />
    <line x1="{outer_x + outer_width}" y1="{outer_y}" x2="{inner_x + inner_width}" y2="{inner_y}" />
    <line x1="{outer_x}" y1="{outer_y + outer_height}" x2="{inner_x}" y2="{inner_y + inner_height}" />
    <line x1="{outer_x + outer_width}" y1="{outer_y + outer_height}" x2="{inner_x + inner_width}" y2="{inner_y + inner_height}" />

    <!-- 菱形到外框的連接線（形成 12 宮） -->
    <line x1="{center_x}" y1="{outer_y}" x2="{outer_x}" y2="{outer_y + outer_height/2}" />
    <line x1="{outer_x}" y1="{outer_y + outer_height/2}" x2="{center_x}" y2="{outer_y + outer_height}" />
    <line x1="{center_x}" y1="{outer_y + outer_height}" x2="{outer_x + outer_width}" y2="{outer_y + outer_height/2}" />
    <line x1="{outer_x + outer_width}" y1="{outer_y + outer_height/2}" x2="{center_x}" y2="{outer_y}" />
  </g>

  <!-- 中心裝飾：Faravahar 圓環（薩珊王室標誌） -->
  <circle cx="{center_x}" cy="{center_y}" r="28" fill="{palette['parchment']}"
          stroke="{palette['gold_leaf']}" stroke-width="2.5"/>
  <circle cx="{center_x}" cy="{center_y}" r="20" fill="none"
          stroke="{palette['crimson']}" stroke-width="1.2" stroke-dasharray="4,3"/>
  <text x="{center_x}" y="{center_y + 7}" text-anchor="middle"
        font-family="serif" font-size="20" fill="{palette['crimson']}">𐩾</text>
''')

    # 12 星座符號（外圍 12 個位置）
    zodiac_signs = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

    svg_parts.append(f'''
  <!-- 12 星座符號 -->
  <g font-family="serif" text-anchor="middle">
''')

    for pos in zodiac_positions:
        sign_idx = pos["sign_index"]
        sign_glyph = zodiac_signs[sign_idx]
        elem_idx = sign_element[sign_idx % 12]
        sign_color = element_colors[elem_idx]
        # 星座符號背景小圓
        svg_parts.append(
            f'    <circle cx="{pos["x"]}" cy="{pos["y"]-8}" r="14" fill="{sign_color}" opacity="0.18"/>\n'
            f'    <text x="{pos["x"]}" y="{pos["y"]}" font-size="22" fill="{palette["crimson"]}">{sign_glyph}</text>\n'
        )

    svg_parts.append('  </g>\n')

    # 行星位置（在 12 宮區域內）
    svg_parts.append(f'''
  <!-- 行星位置 -->
  <g font-family="serif" font-size="20" text-anchor="middle">
''')

    for planet in planet_positions:
        sign_index = int(planet.longitude_sidereal // 30)

        for pos in zodiac_positions:
            if pos["sign_index"] == sign_index:
                planet_glyph = get_planet_glyph(planet.name)
                if not planet_glyph:
                    break

                offset_x = 0
                offset_y = 0
                if planet.house <= 4:
                    offset_y = 25
                elif planet.house <= 8:
                    offset_x = -20
                    offset_y = 15
                else:
                    offset_x = 20
                    offset_y = -15

                px = pos['x'] + offset_x
                py = pos['y'] + offset_y
                # 行星背景小圓
                svg_parts.append(
                    f'    <circle cx="{px}" cy="{py-8}" r="12" fill="{palette["dark_indigo"]}" opacity="0.25"/>\n'
                    f'    <text x="{px}" y="{py}" fill="{palette["dark_indigo"]}" font-weight="bold">{planet_glyph}</text>\n'
                )
                break

    svg_parts.append('  </g>\n')

    # 皇家恆星標記（如果有合相）
    if show_royal_stars and royal_stars:
        svg_parts.append(f'''
  <!-- 皇家恆星（八芒星標記） -->
  <g font-family="serif" font-size="13" text-anchor="middle">
''')

        for star_name, star_data in royal_stars.items():
            star_longitude = star_data["sassanian_longitude"]
            star_sign_index = int(star_longitude // 30)

            for pos in zodiac_positions:
                if pos["sign_index"] == star_sign_index:
                    s = 9
                    cx3, cy3 = pos['x'], pos['y'] - 32
                    svg_parts.append(f'''
    <!-- {star_data.get('name_pahlavi', star_name)} -->
    <g transform="translate({cx3}, {cy3})">
      <path d="M 0,-{s} L {s*0.4},-{s*0.4} L {s},0 L {s*0.4},{s*0.4}
               L 0,{s} L -{s*0.4},{s*0.4} L -{s},0 L -{s*0.4},-{s*0.4} Z"
            fill="url(#goldGradient)" stroke="{palette['crimson']}" stroke-width="1.2"/>
      <circle cx="0" cy="0" r="{s*0.28}" fill="{palette['turquoise']}"/>
    </g>
    <text x="{cx3}" y="{cy3 - 16}" font-size="11" fill="{palette['crimson']}"
          font-style="italic">{star_data.get('name_pahlavi', star_name)}</text>
''')
                    break

        svg_parts.append('  </g>\n')

    # Firdar 時間線（底部）
    if show_firdar:
        firdar_y = outer_y + outer_height + 52
        firdar_height = 42
        firdar_width = outer_width

        firdar_periods = [
            {"planet": "Sun",     "pahlavi": "Khwarshid", "years": 120, "glyph": "☉"},
            {"planet": "Moon",    "pahlavi": "Māh",       "years": 108, "glyph": "☽"},
            {"planet": "Saturn",  "pahlavi": "Kēwān",     "years": 135, "glyph": "♄"},
            {"planet": "Jupiter", "pahlavi": "Ohrmazd",   "years": 108, "glyph": "♃"},
            {"planet": "Mars",    "pahlavi": "Wahrām",    "years": 105, "glyph": "♂"},
            {"planet": "Venus",   "pahlavi": "Anāhīd",    "years": 108, "glyph": "♀"},
            {"planet": "Mercury", "pahlavi": "Tīr",       "years": 108, "glyph": "☿"},
        ]

        total_years = sum(p["years"] for p in firdar_periods)
        x_scale_firdar = firdar_width / total_years
        current_x = outer_x

        svg_parts.append(f'''
  <!-- Firdar 生命週期（Bundahishn 星主時系） -->
  <g>
    <!-- Firdar 標題 -->
    <rect x="{outer_x}" y="{firdar_y - 24}" width="{firdar_width}" height="20" rx="4"
          fill="{palette['crimson']}" opacity="0.12"/>
    <text x="{base_width/2}" y="{firdar_y - 9}" font-family="serif" font-size="13"
          fill="{palette['crimson']}" text-anchor="middle" font-weight="bold" letter-spacing="2">
      Firdar 星主生命週期 · Bundahishn
    </text>
''')

        firdar_planet_colors = [
            palette['gold_leaf'], palette['silver'],   palette['dark_indigo'],
            palette['turquoise'], palette['burnt_orange'], palette['gold_gradient_start'],
            palette['turquoise'],
        ]

        for i, period in enumerate(firdar_periods):
            period_width = period["years"] * x_scale_firdar
            fill_color = firdar_planet_colors[i % len(firdar_planet_colors)]

            svg_parts.append(f'''
    <rect x="{current_x}" y="{firdar_y}" width="{period_width - 1}" height="{firdar_height}"
          fill="{fill_color}" opacity="0.25" stroke="{palette['crimson']}" stroke-width="1" rx="2"/>
    <text x="{current_x + period_width/2}" y="{firdar_y + 16}"
          font-family="serif" font-size="14" fill="{palette['dark_indigo']}"
          text-anchor="middle" font-weight="bold">
      {period['glyph']}
    </text>
    <text x="{current_x + period_width/2}" y="{firdar_y + 34}"
          font-family="serif" font-size="10" fill="{palette['dark_indigo']}"
          text-anchor="middle">
      {period['years']}yr
    </text>
''')
            current_x += period_width

        svg_parts.append('  </g>\n')

    # 歷史說明
    disclaimer_y = base_height - 10
    svg_parts.append(f'''
  <!-- 歷史說明 -->
  <text x="{base_width/2}" y="{disclaimer_y}" font-family="serif" font-size="11"
        fill="{palette['crimson']}" text-anchor="middle" font-style="italic" opacity="0.7">
    薩珊傳統占星 · Bundahishn · Dorotheus Pahlavi Translation (Pingree 1976)
  </text>
''')

    # SVG 結尾
    svg_parts.append('</svg>')

    return ''.join(svg_parts)


def _sassanian_corner_star(cx: float, cy: float, size: float, fill: str, stroke: str) -> str:
    """渲染角落裝飾八芒星（內聯 SVG 元素字串）"""
    s = size
    return (
        f'<path d="M {cx},{cy-s} L {cx+s*0.38},{cy-s*0.38} L {cx+s},{cy} L {cx+s*0.38},{cy+s*0.38} '
        f'L {cx},{cy+s} L {cx-s*0.38},{cy+s*0.38} L {cx-s},{cy} L {cx-s*0.38},{cy-s*0.38} Z" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1" opacity="0.75"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{s*0.28}" fill="{stroke}" opacity="0.6"/>'
    )


def generate_sassanian_chart(
    chart_data: Dict,
    width: int = 400,
    height: int = 450,
    show_pahlavi: bool = True,
    show_royal_stars: bool = True,
    show_firdar: bool = True,
):
    """
    生成薩珊傳統占星星盤（返回 Plotly Figure，使用 SVG 作為底圖）
    """
    import plotly.graph_objects as go

    svg_content = generate_sassanian_svg(
        chart_data, width, height,
        show_pahlavi, show_royal_stars, show_firdar
    )

    svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')

    fig = go.Figure()

    fig.add_layout_image(
        dict(
            source=f"data:image/svg+xml;base64,{svg_base64}",
            xref="paper",
            yref="paper",
            x=0,
            y=1,
            sizex=1,
            sizey=1,
            sizing="contain",
            opacity=1,
            layer="below"
        )
    )

    fig.update_layout(
        width=width,
        height=height,
        xaxis=dict(visible=False, range=[0, 1]),
        yaxis=dict(visible=False, range=[0, 1], scaleanchor="x"),
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig


def save_sassanian_svg(
    chart_data: Dict,
    output_path: str,
    width: int = 400,
    height: int = 450,
    show_pahlavi: bool = True,
    show_royal_stars: bool = True,
    show_firdar: bool = True,
) -> None:
    """保存薩珊星盤 SVG 到檔案"""
    svg_content = generate_sassanian_svg(
        chart_data, width, height,
        show_pahlavi, show_royal_stars, show_firdar
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)


def render_sassanian_banner_chart(
    chart_data: Dict,
    width: int = 500,
    height: int = 650,
    show_pahlavi: bool = True,
) -> str:
    """
    渲染橫幅格式薩珊星盤（純 SVG）
    
    Parameters
    ----------
    chart_data : Dict
        星盤資料
    width : int
        寬度
    height : int
        高度
    show_pahlavi : bool
        是否顯示 Pahlavi 文字
    
    Returns
    -------
    str
        SVG 字串
    """
    return generate_sassanian_svg(
        chart_data=chart_data,
        width=width,
        height=height,
        show_pahlavi=show_pahlavi,
        show_royal_stars=True,
        show_firdar=False,
    )


if __name__ == "__main__":
    print("=" * 60)
    print("薩珊星盤渲染測試（菱形 12 宮設計）")
    print("=" * 60)

    test_chart = {
        "year": 1980,
        "month": 1,
        "day": 15,
        "hour": 10,
        "minute": 30,
        "longitude": 121.5,
        "latitude": 25.0,
        "timezone": 8.0,
    }

    print("\n生成薩珊星盤 SVG...")
    svg_content = generate_sassanian_svg(test_chart, width=500, height=650)
    print(f"  SVG 長度：{len(svg_content)} 字元")
    print(f"  SVG 尺寸：500x650 (viewBox)")

    output_path = "/tmp/sassanian_chart.svg"
    save_sassanian_svg(test_chart, output_path, width=500, height=650)
    print(f"  已保存至：{output_path}")

    print("\n" + "=" * 60)
    print("測試完成")
