"""
astro/tieban/tieban_renderer.py — 鐵板神數 SVG 渲染器

Tie Ban Shen Shu Chart SVG Renderer

純 SVG 星盤圖渲染（非 Plotly），遵循用戶偏好
參考 Sassanian/Persian 鑽石盤設計，融合鐵板神數特色

特點：
- 外層正方形 + 內層菱形（鑽石盤）
- 12 宮位環繞排列
- 鐵板神數號碼、刻分、密碼表可视化
- 支援繁體中文 UI

使用方式：
    svg = render_tieban_chart_svg(result, language='zh')
    st.components.v1.html(svg, height=600)
"""

from typing import Dict, Any, Optional
from astro.tieban.tieban_calculator import TieBanResult, EARTHLY_BRANCHES, PALACE_NAMES

# 十二宮名稱翻譯 (Palace Names Translation)
PALACE_NAMES_EN = {
    "命宮": "Life",
    "兄弟宮": "Siblings",
    "夫妻宮": "Spouse",
    "子女宮": "Children",
    "財帛宮": "Wealth",
    "疾厄宮": "Health",
    "遷移宮": "Travel",
    "交友宮": "Friends",
    "官祿宮": "Career",
    "田宅宮": "Property",
    "福德宮": "Fortune",
    "父母宮": "Parents",
}

def get_palace_name(palace_name: str, language: str = 'zh') -> str:
    """獲取宮位名稱（支持中英文）"""
    if language == 'en':
        return PALACE_NAMES_EN.get(palace_name, palace_name)
    return palace_name


def render_tieban_chart_svg(result: TieBanResult, 
                             language: str = 'zh',
                             width: int = 520,
                             height: int = 740) -> str:
    """
    渲染鐵板神數 SVG 星盤圖（響應式設計，手機優先）
    
    Parameters
    ----------
    result : TieBanResult
        鐵板神數推算結果
    language : str
        語言 ('zh' 繁體中文 或 'en' 英文)
    width : int
        SVG 參考寬度（實際由容器控制）
    height : int
        SVG 參考高度（實際由容器控制）
    
    Returns
    -------
    str
        SVG XML 字符串（包含響應式 HTML 容器）
    """
    # 顏色配置（鐵板神數傳統配色）
    colors = {
        'bg': '#1a1a2e',
        'bg_card': '#16213e',
        'outer_square': '#FF6B35',
        'inner_diamond': '#FFD93D',
        'text_primary': '#FFFFFF',
        'text_secondary': '#9090b0',
        'accent': '#6BCB77',
        'palace_bg': '#16213e',
        'highlight': '#E94560',
        'gold': '#C9A84C',
    }

    # 版面常數（手機優先，確保宮位不超出 viewBox）
    cx = width // 2           # 260
    cy = 295                  # 垂直中心稍偏上，留空間給底部資訊

    square_size = 254         # 外框正方形邊長
    palace_w = 80             # 宮位卡片寬
    palace_h = 56             # 宮位卡片高
    palace_gap = 8            # 宮位卡片與正方形邊框的間距（與 _calculate_palace_positions 中的 pad 保持一致）

    outer_x = cx - square_size // 2   # 133
    outer_y = cy - square_size // 2   # 168

    # 底部資訊卡起始 Y（確保在宮位下方，不重疊）
    # 底宮下緣 = outer_y + square_size + palace_gap + palace_h; 再加 34px 留白
    info_y = outer_y + square_size + palace_gap + palace_h + 34   # ≈ 520

    # 菱形半對角線（內層裝飾菱形）
    diamond_half = 78

    # 計算 12 宮位位置
    palace_positions = _calculate_palace_positions(
        result.ming_palace, outer_x, outer_y, square_size,
        palace_w, palace_h
    )

    svg_parts = []

    # ── SVG 開頭 ──────────────────────────────────────────────────────────────
    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {width} {height}"
     preserveAspectRatio="xMidYMid meet"
     style="width:100%;height:auto;max-width:100%;display:block;">

  <!-- 背景 -->
  <rect width="{width}" height="{height}" fill="{colors['bg']}"/>

  <!-- 頂部裝飾光帶 -->
  <rect x="0" y="0" width="{width}" height="3"
        fill="url(#topGlow)"/>

  <!-- 漸層定義 -->
  <defs>
    <linearGradient id="topGlow" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FF6B35" stop-opacity="0"/>
      <stop offset="50%" stop-color="#FFD93D" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#FF6B35" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="numberGlow" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FF6B35"/>
      <stop offset="100%" stop-color="#E94560"/>
    </linearGradient>
    <filter id="softGlow">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- 標題區 -->
  <text x="{cx}" y="30" text-anchor="middle"
        font-size="22" font-weight="bold" fill="{colors['text_primary']}"
        letter-spacing="4">
    {"鐵板神數" if language == 'zh' else "Iron Plate Divine Numbers"}
  </text>
  <text x="{cx}" y="50" text-anchor="middle"
        font-size="11" fill="{colors['text_secondary']}" letter-spacing="1">
    Tie Ban Shen Shu · Iron Plate Divine Numbers
  </text>
  <!-- 標題分隔線 -->
  <line x1="{cx - 100}" y1="58" x2="{cx + 100}" y2="58"
        stroke="{colors['outer_square']}" stroke-width="0.8" opacity="0.5"/>
''')

    # ── 外層正方形 ────────────────────────────────────────────────────────────
    svg_parts.append(f'''
  <!-- 外層正方形 -->
  <rect x="{outer_x}" y="{outer_y}"
        width="{square_size}" height="{square_size}"
        fill="rgba(22,33,62,0.6)" stroke="{colors['outer_square']}" stroke-width="2.5" rx="2"/>
''')

    # ── 對角線 ────────────────────────────────────────────────────────────────
    svg_parts.append(f'''
  <!-- 對角線 -->
  <line x1="{outer_x}" y1="{outer_y}" x2="{outer_x + square_size}" y2="{outer_y + square_size}"
        stroke="{colors['text_secondary']}" stroke-width="1" opacity="0.35"/>
  <line x1="{outer_x + square_size}" y1="{outer_y}" x2="{outer_x}" y2="{outer_y + square_size}"
        stroke="{colors['text_secondary']}" stroke-width="1" opacity="0.35"/>
''')

    # ── 內層菱形 ──────────────────────────────────────────────────────────────
    svg_parts.append(f'''
  <!-- 內層菱形 -->
  <polygon points="{cx},{cy - diamond_half} {cx + diamond_half},{cy} {cx},{cy + diamond_half} {cx - diamond_half},{cy}"
           fill="none" stroke="{colors['inner_diamond']}" stroke-width="1.8" opacity="0.85"/>
  <!-- 菱形中心點 -->
  <circle cx="{cx}" cy="{cy}" r="4" fill="{colors['inner_diamond']}" opacity="0.6"/>
''')

    # ── 12 宮位卡片 ───────────────────────────────────────────────────────────
    svg_parts.append('  <!-- 12 宮位 -->\n')

    for i, (palace_name, branch) in enumerate(result.palaces.items()):
        pos = palace_positions[i]
        is_ming = (palace_name == '命宮')

        border_color = colors['highlight'] if is_ming else colors['outer_square']
        bg_fill = 'rgba(233,69,96,0.18)' if is_ming else 'rgba(22,33,62,0.9)'
        name_color = '#FF9999' if is_ming else colors['text_secondary']
        branch_color = '#FF8888' if is_ming else colors['inner_diamond']

        palace_verse_info = result.palace_verses.get(palace_name, {})
        verse_text = palace_verse_info.get('verse', '')
        verse_number = palace_verse_info.get('number', '')
        verse_preview = verse_text[:9] + "…" if len(verse_text) > 9 else verse_text

        palace_display_name = get_palace_name(palace_name, language)
        px, py = pos['x'], pos['y']

        svg_parts.append(f'''  <!-- {palace_name} -->
  <rect x="{px}" y="{py}" width="{palace_w}" height="{palace_h}"
        fill="{bg_fill}" stroke="{border_color}" stroke-width="{2 if is_ming else 1}" rx="6"/>
  <text x="{px + palace_w // 2}" y="{py + 13}" text-anchor="middle"
        font-size="9" font-weight="bold" fill="{name_color}">{palace_display_name}</text>
  <text x="{px + palace_w // 2}" y="{py + 30}" text-anchor="middle"
        font-size="16" font-weight="bold" fill="{branch_color}" filter="url(#softGlow)">{branch}</text>
  <text x="{px + palace_w // 2}" y="{py + 43}" text-anchor="middle"
        font-size="7" fill="{colors['text_secondary']}">{verse_preview}</text>
  <text x="{px + 4}" y="{py + 53}" text-anchor="start"
        font-size="6" fill="{colors['highlight']}" opacity="0.8">#{verse_number}</text>
''')

    # ── 命宮 / 身宮 / 五行局 標註 ────────────────────────────────────────────
    label_y = info_y - 14
    svg_parts.append(f'''
  <!-- 命宮身宮五行局標籤列 -->
  <text x="{cx - square_size // 2 + 10}" y="{label_y}" text-anchor="start"
        font-size="11" fill="{colors['accent']}">命：{result.ming_palace}</text>
  <text x="{cx}" y="{label_y}" text-anchor="middle"
        font-size="11" fill="{colors['gold']}">{result.wuxing_ju}</text>
  <text x="{cx + square_size // 2 - 10}" y="{label_y}" text-anchor="end"
        font-size="11" fill="{colors['accent']}">身：{result.shen_palace}</text>
''')

    # ── 底部資訊卡 ────────────────────────────────────────────────────────────
    card_w = width - 40
    card_x = 20
    card_h = 110
    svg_parts.append(f'''
  <!-- 底部資訊卡 -->
  <rect x="{card_x}" y="{info_y}" width="{card_w}" height="{card_h}"
        fill="{colors['bg_card']}" stroke="{colors['accent']}" stroke-width="1.5" rx="12"/>

  <!-- 神數號碼標籤 -->
  <text x="{cx}" y="{info_y + 22}" text-anchor="middle"
        font-size="11" fill="{colors['text_secondary']}" letter-spacing="1">
    {"鐵板神數號碼" if language == 'zh' else "Divine Number"}
  </text>
  <!-- 神數號碼大字 -->
  <text x="{cx}" y="{info_y + 54}" text-anchor="middle"
        font-size="30" font-weight="bold" fill="url(#numberGlow)"
        filter="url(#softGlow)" letter-spacing="4">
    {result.tieban_number}
  </text>

  <!-- 刻 / 分 / 河洛數 三欄 -->
  <line x1="{cx - card_w // 2 + 20}" y1="{info_y + 66}" x2="{cx + card_w // 2 - 20}" y2="{info_y + 66}"
        stroke="{colors['accent']}" stroke-width="0.6" opacity="0.5"/>

  <text x="{cx - 100}" y="{info_y + 83}" text-anchor="middle"
        font-size="11" fill="{colors['text_primary']}">{"刻" if language == "zh" else "Ke"}</text>
  <text x="{cx - 100}" y="{info_y + 100}" text-anchor="middle"
        font-size="16" font-weight="bold" fill="{colors['inner_diamond']}">{result.ke}</text>

  <text x="{cx}" y="{info_y + 83}" text-anchor="middle"
        font-size="11" fill="{colors['text_primary']}">{"分" if language == "zh" else "Fen"}</text>
  <text x="{cx}" y="{info_y + 100}" text-anchor="middle"
        font-size="16" font-weight="bold" fill="{colors['inner_diamond']}">{result.fen}</text>

  <text x="{cx + 100}" y="{info_y + 83}" text-anchor="middle"
        font-size="11" fill="{colors['text_primary']}">{"河洛數" if language == "zh" else "HeLuo"}</text>
  <text x="{cx + 100}" y="{info_y + 100}" text-anchor="middle"
        font-size="16" font-weight="bold" fill="{colors['accent']}">{result.he_luo_number}</text>
''')

    # ── 條文預覽 ──────────────────────────────────────────────────────────────
    verse_preview_full = result.verse[:44] + "…" if len(result.verse) > 44 else result.verse
    verse_y = info_y + card_h + 18
    category = result.verse_data.get('category', '') if isinstance(result.verse_data, dict) else ''
    tags = result.verse_data.get('tags', []) if isinstance(result.verse_data, dict) else []

    svg_parts.append(f'''
  <!-- 條文預覽 -->
  <text x="{cx}" y="{verse_y}" text-anchor="middle"
        font-size="11" fill="{colors['text_secondary']}">{verse_preview_full}</text>
''')
    if category:
        svg_parts.append(f'''  <text x="{cx}" y="{verse_y + 17}" text-anchor="middle"
        font-size="10" fill="{colors['accent']}">【{category}】</text>
''')
    if tags:
        svg_parts.append(f'''  <text x="{cx}" y="{verse_y + 31}" text-anchor="middle"
        font-size="9" fill="{colors['text_secondary']}">{" · ".join(tags[:3])}</text>
''')

    svg_parts.append('</svg>\n')
    svg_content = ''.join(svg_parts)

    # ── 響應式 HTML 容器 ──────────────────────────────────────────────────────
    html = f'''<style>
.tieban-wrap {{
  width: 100%;
  max-width: 540px;
  margin: 0 auto;
  padding: 4px;
  box-sizing: border-box;
}}
.tieban-wrap svg {{
  width: 100%;
  height: auto;
  display: block;
}}
@media (max-width: 480px) {{
  .tieban-wrap {{ padding: 2px; }}
}}
</style>
<div class="tieban-wrap">{svg_content}</div>
'''
    return html


def _calculate_palace_positions(ming_palace_branch: str,
                                 outer_x: int,
                                 outer_y: int,
                                 square_size: int,
                                 palace_width: int = 80,
                                 palace_height: int = 56) -> list:
    """
    計算 12 宮位位置（環繞外層正方形，手機優先）

    排列方式：
    - 上方 3 宮（從右到左）
    - 左方 3 宮（從上到下）
    - 下方 3 宮（從左到右）
    - 右方 3 宮（從下到上）

    Returns
    -------
    list
        [{'x': int, 'y': int}, ...] 12 個位置
    """
    positions = []
    gap = square_size // 3          # 每段間距
    pad = 8                          # 宮位卡片與正方形邊框的間距

    # 上方 3 宮（從右到左）
    for i in range(3):
        x = outer_x + (2 - i) * gap + gap // 2 - palace_width // 2
        y = outer_y - palace_height - pad
        positions.append({'x': x, 'y': y})

    # 左方 3 宮（從上到下）
    for i in range(3):
        x = outer_x - palace_width - pad
        y = outer_y + (i * gap) + gap // 2 - palace_height // 2
        positions.append({'x': x, 'y': y})

    # 下方 3 宮（從左到右）
    for i in range(3):
        x = outer_x + (i * gap) + gap // 2 - palace_width // 2
        y = outer_y + square_size + pad
        positions.append({'x': x, 'y': y})

    # 右方 3 宮（從下到上）
    for i in range(3):
        x = outer_x + square_size + pad
        y = outer_y + (2 - i) * gap + gap // 2 - palace_height // 2
        positions.append({'x': x, 'y': y})

    # 根據命宮地支旋轉位置列表
    if ming_palace_branch:
        ming_idx = EARTHLY_BRANCHES.index(ming_palace_branch)
        positions = positions[ming_idx:] + positions[:ming_idx]

    return positions


def render_tieban_number_card(result: TieBanResult, 
                               language: str = 'zh') -> str:
    """
    渲染鐵板神數號碼卡片（簡化版）
    
    用於 Streamlit 側邊欄或信息卡片
    """
    colors = {
        'bg': '#16213e',
        'text': '#FFFFFF',
        'accent': '#FF6B35',
        'highlight': '#FFD93D',
    }
    
    html = f'''
<div style="background: {colors['bg']}; padding: 20px; border-radius: 10px; border: 2px solid {colors['accent']};">
    <h3 style="color: {colors['text']}; margin: 0 0 15px 0; text-align: center;">
        🔮 鐵板神數
    </h3>
    
    <div style="text-align: center; margin: 20px 0;">
        <div style="font-size: 32px; font-weight: bold; color: {colors['highlight']};">
            {result.tieban_number}
        </div>
        <div style="font-size: 12px; color: {colors['text']}; opacity: 0.7;">
            萬千百十號
        </div>
    </div>
    
    <div style="display: flex; justify-content: space-around; margin: 15px 0;">
        <div style="text-align: center;">
            <div style="font-size: 18px; color: {colors['text']};">{result.ke}</div>
            <div style="font-size: 11px; color: {colors['text']}; opacity: 0.7;">刻</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 18px; color: {colors['text']};">{result.fen}</div>
            <div style="font-size: 11px; color: {colors['text']}; opacity: 0.7;">分</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 18px; color: {colors['text']};">{result.he_luo_number}</div>
            <div style="font-size: 11px; color: {colors['text']}; opacity: 0.7;">河洛數</div>
        </div>
    </div>
    
    <div style="border-top: 1px solid {colors['accent']}; margin: 15px 0; padding-top: 15px;">
        <div style="font-size: 12px; color: {colors['text']}; opacity: 0.7; margin-bottom: 5px;">
            命宮 / 身宮
        </div>
        <div style="font-size: 16px; color: {colors['highlight']};">
            {result.ming_palace} / {result.shen_palace}
        </div>
    </div>
    
    <div style="border-top: 1px solid {colors['accent']}; margin: 15px 0; padding-top: 15px;">
        <div style="font-size: 12px; color: {colors['text']}; opacity: 0.7; margin-bottom: 5px;">
            五行局
        </div>
        <div style="font-size: 16px; color: {colors['accent']};">
            {result.wuxing_ju}
        </div>
    </div>
    
    <div style="border-top: 1px solid {colors['accent']}; margin: 15px 0; padding-top: 15px;">
        <div style="font-size: 12px; color: {colors['text']}; opacity: 0.7; margin-bottom: 5px;">
            條文
        </div>
        <div style="font-size: 13px; color: {colors['text']}; line-height: 1.6;">
            {result.verse}
        </div>
        {f'<div style="font-size: 11px; color: {colors["accent"]}; margin-top: 8px;">【{result.verse_data.get("category", "")}】</div>' if isinstance(result.verse_data, dict) and result.verse_data.get('category') else ''}
        {f'<div style="font-size: 10px; color: {colors["text"]}; opacity: 0.6; margin-top: 4px;">{" · ".join(result.verse_data.get("tags", [])[:3])}</div>' if isinstance(result.verse_data, dict) and result.verse_data.get('tags') else ''}
    </div>
</div>
'''
    
    return html
