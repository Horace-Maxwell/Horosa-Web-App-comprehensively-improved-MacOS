"""
frontend/fludd_rota_renderer.py
═══════════════════════════════════════════════════════════════════════════════
弗拉德命運輪盤（Fludd Rota Simulator）— Streamlit 渲染器

提供：
    render_fludd_rota_html   — 生成含 HTML5 Canvas 的完整互動式輪盤 HTML
    render_fludd_rota        — Streamlit 頁面入口（含表單、計算、解讀）

視覺風格：
    - 17 世紀古典銅版雕刻風格：深棕黑背景、金色刻印線條、羊皮紙質感
    - 四層同心圓 Canvas 輪盤，各層可滑鼠拖曳旋轉
    - 頂部金色指針固定，標示當前解讀位置
    - 動態陰影、漸層填色、細線裝飾，模擬金屬銘刻感

互動：
    - 每層輪盤可獨立以滑鼠拖曳旋轉
    - 「根據星盤設定輪盤」按鈕：依行星度數自動旋轉各層
    - 解讀結果顯示在輪盤下方
"""

from __future__ import annotations

import json
from typing import Callable, Optional

import streamlit as st
import streamlit.components.v1 as components

from astro.fludd_rota import (
    RING1_SYMBOLS,
    RING2_NUMBERS,
    RING3_PLANETS,
    RING4_ZONE_NAMES,
    RING4_ZONES,
    VISUAL,
    RotaConfig,
    RotaReading,
    compute_reading,
    config_from_dict,
)

try:
    from astro.i18n import auto_cn, t
except ImportError:
    def t(key: str) -> str:  # type: ignore[misc]
        return key
    def auto_cn(text: str, en_text: str = "") -> str:  # type: ignore[misc]
        return text


# Maximum characters to preview for Ring 4 text in the compact reading panel
_RING4_PREVIEW_LEN = 80
# Base canvas drawing size; CSS scales it down responsively on narrow screens.
_FLUDD_CANVAS_BASE_WIDTH = 520


# ─────────────────────────────────────────────────────────────────────────────
# CSS 主題
# ─────────────────────────────────────────────────────────────────────────────

def _theme_css() -> str:
    return """
<style>
.fr-header {
  background: linear-gradient(135deg, #0D0A06 0%, #1A1208 55%, #0D0A06 100%);
  border: 1px solid #8C6E2A;
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 14px;
}
.fr-title {
  color: #D4A843;
  font-size: 1.5rem;
  font-family: "Palatino Linotype", "Book Antiqua", Palatino, Georgia, serif;
  font-weight: 700;
  margin: 0;
  letter-spacing: 2px;
  text-shadow: 0 0 12px rgba(212,168,67,0.5);
}
.fr-sub {
  color: #8C6E2A;
  font-size: 0.88rem;
  margin: 5px 0 0 0;
  font-style: italic;
}
.fr-reading-card {
  background: linear-gradient(135deg, #0D0A06 0%, #140E07 100%);
  border: 1px solid #8C6E2A;
  border-radius: 8px;
  padding: 16px 18px;
  margin-top: 12px;
}
.fr-reading-title {
  color: #D4A843;
  font-family: Georgia, serif;
  font-size: 1.1rem;
  font-weight: bold;
  border-bottom: 1px solid #8C6E2A;
  padding-bottom: 6px;
  margin-bottom: 10px;
}
.fr-ring-label {
  color: #8C6E2A;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-top: 8px;
}
.fr-ring-sym {
  color: #F0C040;
  font-size: 1.6rem;
  font-family: Georgia, serif;
}
.fr-ring-text {
  color: #C8A96E;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-top: 2px;
}
.fr-summary {
  color: #D4B896;
  font-size: 0.95rem;
  line-height: 1.65;
}
.fr-divider {
  border: none;
  border-top: 1px solid #8C6E2A;
  margin: 12px 0;
  opacity: 0.5;
}
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# HTML5 Canvas 輪盤生成
# ─────────────────────────────────────────────────────────────────────────────

def render_fludd_rota_html(
    ring1_offset: float = 0.0,
    ring2_offset: float = 0.0,
    ring3_offset: float = 0.0,
    ring4_offset: float = 0.0,
    width: int = 520,
) -> str:
    """生成弗拉德命運輪盤的完整互動式 HTML。

    Args:
        ring1_offset: 最外層（字母）旋轉偏移角（度）
        ring2_offset: 第二層（數字）旋轉偏移角
        ring3_offset: 第三層（行星符號）旋轉偏移角
        ring4_offset: 最內層（命運區域）旋轉偏移角
        width:        Canvas 寬度（px）

    Returns:
        完整 HTML 字串，可直接傳入 components.html()
    """
    r1_json = json.dumps(RING1_SYMBOLS)
    r2_json = json.dumps(RING2_NUMBERS)
    r3_json = json.dumps(RING3_PLANETS)
    r4_json = json.dumps(RING4_ZONES)

    v = VISUAL
    height = width + 20  # 留下底部空間

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background: {v['background']};
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px;
    font-family: "Palatino Linotype", Georgia, serif;
    width: 100%;
    overflow-x: hidden;
  }}
  .rota-wrap {{
    width: 100%;
    max-width: {width}px;
    display: flex;
    justify-content: center;
  }}
  #rotaCanvas {{
    cursor: grab;
    border-radius: 50%;
    box-shadow:
      0 0 40px rgba(212,168,67,0.15),
      0 0 80px rgba(212,168,67,0.05),
      inset 0 0 30px rgba(0,0,0,0.8);
    display: block;
    width: 100%;
    max-width: {width}px;
    height: auto;
  }}
  #rotaCanvas:active {{ cursor: grabbing; }}
  .ring-info {{
    color: {v['gold_dim']};
    font-size: 11px;
    text-align: center;
    margin-top: 8px;
    letter-spacing: 1px;
    opacity: 0.7;
  }}
</style>
</head>
<body>
<div class="rota-wrap">
  <canvas id="rotaCanvas" width="{width}" height="{width}"></canvas>
</div>
<div class="ring-info">✦ ROTA FORTUNAE · FLUDD 1617 · 拖曳各層以旋轉 ✦</div>

<script>
(function() {{
  const canvas = document.getElementById('rotaCanvas');
  const ctx = canvas.getContext('2d');
  const W = {width};
  const cx = W / 2, cy = W / 2;

  // ── 顏色常數 ────────────────────────────────────────────
  const C = {{
    bg:         '{v["background"]}',
    goldBright: '{v["gold_bright"]}',
    goldDim:    '{v["gold_dim"]}',
    goldAccent: '{v["gold_accent"]}',
    silver:     '{v["silver"]}',
    copper:     '{v["copper"]}',
    parchment:  '{v["parchment"]}',
    ink:        '{v["ink"]}',
  }};

  // ── 四層輪盤配置 ────────────────────────────────────────
  // radii: [outer, inner] 各層的外半徑與內半徑
  const totalR = W * 0.48;

  // 由外向內：Ring1 最外層，Ring4 最內層
  // Ring1: 外徑 totalR，內徑 totalR - ring1_width
  // Ring4 內部為中心圓
  const RING_CONFIG = [
    // Ring 1 (outermost): 字母層
    {{
      symbols: {r1_json},
      offset:  {ring1_offset},   // 旋轉偏移角（度），可被拖曳修改
      outerR:  totalR,
      innerR:  totalR * 0.84,
      bgColor: '{v["ring1_bg"]}',
      symColor: C.parchment,
      lineColor: C.goldDim,
      symSize:  Math.max(10, W * 0.024),
      label:   'I · 太陽+上升',
    }},
    // Ring 2: 數字層
    {{
      symbols: {r2_json},
      offset:  {ring2_offset},
      outerR:  totalR * 0.84,
      innerR:  totalR * 0.67,
      bgColor: '{v["ring2_bg"]}',
      symColor: C.goldBright,
      lineColor: C.copper,
      symSize:  Math.max(9, W * 0.022),
      label:   'II · 月亮',
    }},
    // Ring 3: 行星符號層
    {{
      symbols: {r3_json},
      offset:  {ring3_offset},
      outerR:  totalR * 0.67,
      innerR:  totalR * 0.50,
      bgColor: '{v["ring3_bg"]}',
      symColor: C.goldAccent,
      lineColor: C.goldDim,
      symSize:  Math.max(12, W * 0.030),
      label:   'III · 水星+金星',
    }},
    // Ring 4 (innermost): 命運區域層
    {{
      symbols: {r4_json},
      offset:  {ring4_offset},
      outerR:  totalR * 0.50,
      innerR:  totalR * 0.30,
      bgColor: '{v["ring4_bg"]}',
      symColor: C.goldAccent,
      lineColor: C.copper,
      symSize:  Math.max(12, W * 0.030),
      label:   'IV · 火星+木星+土星',
    }},
  ];

  const CENTER_R = totalR * 0.30;

  // ── 互動狀態 ────────────────────────────────────────────
  let dragging = -1;     // 正在拖曳的層索引（-1 = 無）
  let dragStartAngle = 0;
  let dragStartOffset = 0;

  // ── 繪製函數 ────────────────────────────────────────────

  function toRad(deg) {{ return deg * Math.PI / 180; }}

  function drawBackground() {{
    // 深色背景
    ctx.fillStyle = C.bg;
    ctx.fillRect(0, 0, W, W);

    // 外圓裝飾
    ctx.beginPath();
    ctx.arc(cx, cy, totalR + 6, 0, Math.PI * 2);
    ctx.strokeStyle = C.goldDim;
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(cx, cy, totalR + 3, 0, Math.PI * 2);
    ctx.strokeStyle = C.copper;
    ctx.lineWidth = 0.5;
    ctx.stroke();
  }}

  function drawRing(ring) {{
    const n = ring.symbols.length;
    const segAngle = (2 * Math.PI) / n;
    const offsetRad = toRad(ring.offset);

    for (let i = 0; i < n; i++) {{
      const startAngle = i * segAngle - offsetRad - Math.PI / 2;
      const endAngle   = startAngle + segAngle;
      const midAngle   = startAngle + segAngle / 2;

      // ── 扇形背景 ──
      // 奇偶交替深淺
      const isEven = i % 2 === 0;
      const alpha = isEven ? 0.85 : 0.70;

      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, ring.outerR, startAngle, endAngle);
      ctx.arc(cx, cy, ring.innerR, endAngle, startAngle, true);
      ctx.closePath();

      // 漸層填色（模擬金屬光澤）
      const grad = ctx.createRadialGradient(cx, cy, ring.innerR, cx, cy, ring.outerR);
      grad.addColorStop(0, hexAlpha(ring.bgColor, alpha));
      grad.addColorStop(0.5, hexAlpha(ring.bgColor, alpha * 0.9));
      grad.addColorStop(1, hexAlpha('#000000', 0.3));
      ctx.fillStyle = grad;
      ctx.fill();

      // ── 分隔線 ──
      ctx.beginPath();
      ctx.moveTo(
        cx + ring.innerR * Math.cos(startAngle),
        cy + ring.innerR * Math.sin(startAngle)
      );
      ctx.lineTo(
        cx + ring.outerR * Math.cos(startAngle),
        cy + ring.outerR * Math.sin(startAngle)
      );
      ctx.strokeStyle = ring.lineColor;
      ctx.lineWidth = 0.6;
      ctx.stroke();

      // ── 符號文字 ──
      const symR = (ring.outerR + ring.innerR) / 2;
      const sx = cx + symR * Math.cos(midAngle);
      const sy = cy + symR * Math.sin(midAngle);

      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(midAngle + Math.PI / 2);
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.font = `${{ring.symSize}}px "Palatino Linotype", Georgia, serif`;
      ctx.fillStyle = ring.symColor;
      ctx.shadowColor = 'rgba(212,168,67,0.4)';
      ctx.shadowBlur = 4;
      ctx.fillText(ring.symbols[i], 0, 0);
      ctx.shadowBlur = 0;
      ctx.restore();
    }}

    // ── 輪廓圓圈 ──
    ctx.beginPath();
    ctx.arc(cx, cy, ring.outerR, 0, Math.PI * 2);
    ctx.strokeStyle = C.goldDim;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(cx, cy, ring.innerR, 0, Math.PI * 2);
    ctx.strokeStyle = ring.lineColor;
    ctx.lineWidth = 0.8;
    ctx.stroke();
  }}

  function drawCenter() {{
    // 中心圓 — 眼睛 / 太陽象徵
    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, CENTER_R);
    grad.addColorStop(0, '#1A1208');
    grad.addColorStop(0.6, '#0D0A06');
    grad.addColorStop(1, '#060402');
    ctx.beginPath();
    ctx.arc(cx, cy, CENTER_R, 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.fill();

    ctx.beginPath();
    ctx.arc(cx, cy, CENTER_R, 0, Math.PI * 2);
    ctx.strokeStyle = C.goldDim;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // 中心太陽符號
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.font = `${{Math.max(16, W * 0.05)}}px serif`;
    ctx.fillStyle = C.goldAccent;
    ctx.shadowColor = 'rgba(240,192,64,0.6)';
    ctx.shadowBlur = 8;
    ctx.fillText('☉', cx, cy);
    ctx.shadowBlur = 0;

    // 裝飾小圓點
    for (let i = 0; i < 8; i++) {{
      const a = (i / 8) * Math.PI * 2 - Math.PI / 8;
      const r = CENTER_R * 0.75;
      ctx.beginPath();
      ctx.arc(cx + r * Math.cos(a), cy + r * Math.sin(a), 1.5, 0, Math.PI * 2);
      ctx.fillStyle = C.goldDim;
      ctx.fill();
    }}
  }}

  function drawPointer() {{
    // 頂部指針（北方，12點位置）
    const pLen = totalR + 14;
    const pWidth = 5;

    // 外三角指針
    ctx.beginPath();
    ctx.moveTo(cx, cy - pLen);
    ctx.lineTo(cx - pWidth, cy - totalR + 8);
    ctx.lineTo(cx + pWidth, cy - totalR + 8);
    ctx.closePath();
    ctx.fillStyle = C.goldAccent;
    ctx.fill();
    ctx.strokeStyle = '#F8E070';
    ctx.lineWidth = 0.8;
    ctx.stroke();

    // 指針小圓
    ctx.beginPath();
    ctx.arc(cx, cy - totalR + 8, 3, 0, Math.PI * 2);
    ctx.fillStyle = C.goldAccent;
    ctx.fill();

    // N 標記
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.font = `bold ${{Math.max(9, W * 0.022)}}px serif`;
    ctx.fillStyle = C.goldAccent;
    ctx.fillText('N', cx, cy - pLen - 8);
  }}

  function drawDecorations() {{
    // 四方位標記
    const markers = [
      {{ label: 'N', a: -Math.PI/2, r: totalR + 28 }},
      {{ label: 'E', a: 0,           r: totalR + 28 }},
      {{ label: 'S', a: Math.PI/2,   r: totalR + 28 }},
      {{ label: 'W', a: Math.PI,     r: totalR + 28 }},
    ];
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.font = `${{Math.max(8, W * 0.018)}}px serif`;
    ctx.fillStyle = C.goldDim;
    markers.forEach(m => {{
      if (m.label === 'N') return; // 已有指針
      ctx.fillText(m.label, cx + m.r * Math.cos(m.a), cy + m.r * Math.sin(m.a));
    }});

    // 四角裝飾星號
    const cornerDist = totalR * 0.96;
    const corners = [
      Math.PI * 0.25, Math.PI * 0.75, Math.PI * 1.25, Math.PI * 1.75,
    ];
    ctx.font = `${{Math.max(8, W * 0.016)}}px serif`;
    ctx.fillStyle = C.copper;
    corners.forEach(a => {{
      ctx.fillText('✦', cx + cornerDist * Math.cos(a), cy + cornerDist * Math.sin(a));
    }});
  }}

  function draw() {{
    ctx.clearRect(0, 0, W, W);
    drawBackground();
    // 由外向內繪製各層
    for (let i = 0; i < RING_CONFIG.length; i++) {{
      drawRing(RING_CONFIG[i]);
    }}
    drawCenter();
    drawDecorations();
    drawPointer();
  }}

  // ── 輔助：hex + alpha → rgba ─────────────────────────────
  function hexAlpha(hex, alpha) {{
    const r = parseInt(hex.slice(1,3), 16);
    const g = parseInt(hex.slice(3,5), 16);
    const b = parseInt(hex.slice(5,7), 16);
    return `rgba(${{r}},${{g}},${{b}},${{alpha}})`;
  }}

  // ── 命中測試：返回滑鼠所在輪盤層索引 ───────────────────────
  function hitTestRing(x, y) {{
    const dx = x - cx, dy = y - cy;
    const r = Math.sqrt(dx*dx + dy*dy);
    for (let i = 0; i < RING_CONFIG.length; i++) {{
      const ring = RING_CONFIG[i];
      if (r >= ring.innerR && r <= ring.outerR) return i;
    }}
    return -1;
  }}

  // ── 滑鼠事件 ─────────────────────────────────────────────
  function getAngle(e) {{
    const rect = canvas.getBoundingClientRect();
    const scaleX = W / rect.width;
    const scaleY = W / rect.height;
    const mx = (e.clientX - rect.left) * scaleX;
    const my = (e.clientY - rect.top) * scaleY;
    return Math.atan2(my - cy, mx - cx) * 180 / Math.PI;
  }}

  canvas.addEventListener('mousedown', function(e) {{
    const rect = canvas.getBoundingClientRect();
    const scaleX = W / rect.width;
    const scaleY = W / rect.height;
    const mx = (e.clientX - rect.left) * scaleX;
    const my = (e.clientY - rect.top) * scaleY;
    const ringIdx = hitTestRing(mx, my);
    if (ringIdx >= 0) {{
      dragging = ringIdx;
      dragStartAngle = getAngle(e);
      dragStartOffset = RING_CONFIG[ringIdx].offset;
    }}
    e.preventDefault();
  }});

  canvas.addEventListener('mousemove', function(e) {{
    if (dragging < 0) return;
    const currentAngle = getAngle(e);
    let delta = currentAngle - dragStartAngle;
    // 處理跨越 ±180° 邊界
    if (delta > 180) delta -= 360;
    if (delta < -180) delta += 360;
    RING_CONFIG[dragging].offset = (dragStartOffset - delta + 360) % 360;
    draw();
    e.preventDefault();
  }});

  canvas.addEventListener('mouseup', function(e) {{
    dragging = -1;
  }});

  canvas.addEventListener('mouseleave', function(e) {{
    dragging = -1;
  }});

  // ── 觸控事件支援（行動裝置）────────────────────────────────
  canvas.addEventListener('touchstart', function(e) {{
    if (e.touches.length === 1) {{
      const touch = e.touches[0];
      const rect = canvas.getBoundingClientRect();
      const scaleX = W / rect.width;
      const scaleY = W / rect.height;
      const mx = (touch.clientX - rect.left) * scaleX;
      const my = (touch.clientY - rect.top) * scaleY;
      const ringIdx = hitTestRing(mx, my);
      if (ringIdx >= 0) {{
        dragging = ringIdx;
        dragStartAngle = Math.atan2(my - cy, mx - cx) * 180 / Math.PI;
        dragStartOffset = RING_CONFIG[ringIdx].offset;
      }}
      e.preventDefault();
    }}
  }}, {{ passive: false }});

  canvas.addEventListener('touchmove', function(e) {{
    if (dragging < 0 || e.touches.length !== 1) return;
    const touch = e.touches[0];
    const rect = canvas.getBoundingClientRect();
    const scaleX = W / rect.width;
    const scaleY = W / rect.height;
    const mx = (touch.clientX - rect.left) * scaleX;
    const my = (touch.clientY - rect.top) * scaleY;
    const currentAngle = Math.atan2(my - cy, mx - cx) * 180 / Math.PI;
    let delta = currentAngle - dragStartAngle;
    if (delta > 180) delta -= 360;
    if (delta < -180) delta += 360;
    RING_CONFIG[dragging].offset = (dragStartOffset - delta + 360) % 360;
    draw();
    e.preventDefault();
  }}, {{ passive: false }});

  canvas.addEventListener('touchend', function(e) {{
    dragging = -1;
  }});

  // ── 初始繪製 ─────────────────────────────────────────────
  draw();

}})();
</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# 解讀面板渲染
# ─────────────────────────────────────────────────────────────────────────────

def _render_reading_panel(reading: RotaReading) -> None:
    """在 Streamlit 中渲染解讀結果面板。"""
    st.markdown(_theme_css(), unsafe_allow_html=True)

    node_badge = ""
    if reading.node_modifier_key == "north_node":
        node_badge = '<span style="color:#F0C040;font-size:0.8rem;">☊ 北交點加持</span>'
    elif reading.node_modifier_key == "south_node":
        node_badge = '<span style="color:#8C6E2A;font-size:0.8rem;">☋ 南交點課題</span>'

    st.markdown(
        f'<div class="fr-reading-card">'
        f'<div class="fr-reading-title">✦ 輪盤解讀結果 {node_badge}</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div class="fr-ring-label">第一層 · 字母符號（太陽+上升）</div>'
            f'<div class="fr-ring-sym">{reading.ring1_symbol}</div>'
            f'<div class="fr-ring-text">{reading.ring1_text}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<hr class="fr-divider">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="fr-ring-label">第三層 · 行星力量（水星+金星）</div>'
            f'<div class="fr-ring-sym">{reading.ring3_planet}</div>'
            f'<div class="fr-ring-text">{reading.ring3_text}</div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f'<div class="fr-ring-label">第二層 · 命運之宮（月亮）</div>'
            f'<div class="fr-ring-sym">{reading.ring2_number}</div>'
            f'<div class="fr-ring-text">{reading.ring2_text}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<hr class="fr-divider">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="fr-ring-label">第四層 · 命運區域（火星+木星+土星）</div>'
            f'<div class="fr-ring-sym">{reading.ring4_zone} {reading.ring4_zone_name}</div>'
            f'<div class="fr-ring-text">{reading.ring4_text[:_RING4_PREVIEW_LEN]}…</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="fr-divider">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="fr-ring-label">壽命趨勢（靈性參考）</div>'
        f'<div class="fr-ring-sym">{reading.lifespan_level} · {reading.lifespan_score}/100</div>'
        f'<div class="fr-ring-text">{reading.lifespan_text}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # 綜合解讀
    with st.expander("✦ 展開完整綜合解讀", expanded=True):
        st.markdown(reading.summary)


# ─────────────────────────────────────────────────────────────────────────────
# 主要 Streamlit 渲染入口
# ─────────────────────────────────────────────────────────────────────────────

def render_fludd_rota(
    after_chart_hook: Optional[Callable[[], None]] = None,
    auto_config: Optional[RotaConfig] = None,
) -> None:
    """渲染弗拉德命運輪盤完整頁面（Streamlit 入口）。

    Args:
        after_chart_hook: 可選回調，在輪盤下方插入額外 UI（如 AI 按鈕）。
        auto_config: 可選的行星配置，由外部星盤自動傳入。
            若提供且使用者尚未手動提交表單，則自動根據此配置計算並顯示解讀。
    """
    st.markdown(_theme_css(), unsafe_allow_html=True)

    # ── 標題 ─────────────────────────────────────────────────
    st.markdown(
        '<div class="fr-header">'
        '<p class="fr-title">⚙ 弗拉德命運輪盤（Fludd Rota Simulator）</p>'
        '<p class="fr-sub">'
        '靈感來自 Robert Fludd《Utriusque Cosmi Historia》(1617) 占卜輪盤 · '
        '四層同心圓 · 由出生星盤行星度數驅動 · 可拖曳旋轉各層'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── 行星度數輸入表單 ──────────────────────────────────────
    with st.expander("✦ 輸入行星黃道度數（0–360°）", expanded=False):
        st.caption(
            "請輸入出生星盤各行星的黃道度數（熱帶黃道，0° = 牡羊0°）。"
            "也可直接使用預設值探索輪盤。"
        )

        sun_deg = st.number_input(
            "☉ 太陽（Ring 1 主控）", 0.0, 360.0, 0.0, 1.0, key="fr_sun"
        )
        moon_deg = st.number_input(
            "☽ 月亮（Ring 2 主控）", 0.0, 360.0, 45.0, 1.0, key="fr_moon"
        )
        mercury_deg = st.number_input(
            "☿ 水星（Ring 3 共控）", 0.0, 360.0, 90.0, 1.0, key="fr_mercury"
        )
        venus_deg = st.number_input(
            "♀ 金星（Ring 3 共控）", 0.0, 360.0, 120.0, 1.0, key="fr_venus"
        )
        mars_deg = st.number_input(
            "♂ 火星（Ring 4 共控）", 0.0, 360.0, 180.0, 1.0, key="fr_mars"
        )
        jupiter_deg = st.number_input(
            "♃ 木星（Ring 4 共控）", 0.0, 360.0, 240.0, 1.0, key="fr_jupiter"
        )
        saturn_deg = st.number_input(
            "♄ 土星（Ring 4 共控）", 0.0, 360.0, 300.0, 1.0, key="fr_saturn"
        )
        asc_deg = st.number_input(
            "ASC 上升點（Ring 1 次控）", 0.0, 360.0, 30.0, 1.0, key="fr_asc"
        )
        north_node_deg = st.number_input(
            "☊ 北交點（解讀調節）", 0.0, 360.0, 60.0, 1.0, key="fr_nn"
        )

        south_node_deg = (north_node_deg + 180.0) % 360.0
        st.caption(f"☋ 南交點（自動計算）：{south_node_deg:.1f}°")

        submitted = st.button(
            "⚙ 根據星盤設定輪盤並解讀",
            type="primary",
            use_container_width=True,
            key="fr_submit",
        )

    # ── 計算與狀態管理 ────────────────────────────────────────
    _key = "fludd_rota_reading"
    _src_key = "fludd_rota_source"

    if submitted:
        cfg = RotaConfig(
            sun=sun_deg,
            moon=moon_deg,
            mercury=mercury_deg,
            venus=venus_deg,
            mars=mars_deg,
            jupiter=jupiter_deg,
            saturn=saturn_deg,
            ascendant=asc_deg,
            north_node=north_node_deg,
            south_node=south_node_deg,
        )
        reading: RotaReading = compute_reading(cfg)
        st.session_state[_key] = reading
        st.session_state[_src_key] = "manual_input"

    if _key in st.session_state and _src_key not in st.session_state:
        # Backward compatibility: historical readings in session came from this form.
        st.session_state[_src_key] = "manual_input"

    # Auto-compute from chart data when provided and no manual reading exists.
    # Always refresh the chart-based reading so it stays in sync with the
    # sidebar date / location selection.
    if auto_config is not None and st.session_state.get(_src_key) != "manual_input":
        st.session_state[_key] = compute_reading(auto_config)
        st.session_state[_src_key] = "chart"

    reading: Optional[RotaReading] = None
    if st.session_state.get(_src_key) in ("manual_input", "chart"):
        reading = st.session_state.get(_key)

    # ── 決定輪盤偏移 ─────────────────────────────────────────
    if reading is not None:
        r1_off = reading.ring1_offset
        r2_off = reading.ring2_offset
        r3_off = reading.ring3_offset
        r4_off = reading.ring4_offset
    else:
        r1_off = r2_off = r3_off = r4_off = 0.0

    # ── 渲染輪盤 ─────────────────────────────────────────────
    canvas_width = _FLUDD_CANVAS_BASE_WIDTH
    html_content = render_fludd_rota_html(
        ring1_offset=r1_off,
        ring2_offset=r2_off,
        ring3_offset=r3_off,
        ring4_offset=r4_off,
        width=canvas_width,
    )
    components.html(html_content, height=canvas_width + 50, scrolling=False)

    # ── After-chart 鉤子（如 AI 按鈕）────────────────────────
    if after_chart_hook is not None:
        after_chart_hook()

    # ── 解讀面板 ─────────────────────────────────────────────
    if reading is not None:
        st.markdown("---")
        _render_reading_panel(reading)
    else:
        st.info(
            t("info_fludd_rota_prompt")
            if t("info_fludd_rota_prompt") != "info_fludd_rota_prompt"
            else "✦ 輸入出生星盤行星度數，點擊「根據星盤設定輪盤並解讀」以啟動弗拉德命運輪盤占卜。"
        )

    # ── 功能說明 ─────────────────────────────────────────────
    with st.expander("✦ 關於弗拉德命運輪盤", expanded=False):
        st.markdown(t("desc_fludd_rota") or _DEFAULT_DESC)


# 備用說明（若 i18n 尚未載入）
_DEFAULT_DESC = """
### ⚙ 弗拉德命運輪盤（Fludd Rota Simulator）

**靈感來源**：Robert Fludd（1574–1637）——英國著名的玫瑰十字會醫生、神秘哲學家，
其 1617 年著作《Utriusque Cosmi Historia》（宇宙兩界史）中描繪了多種宇宙
占卜輪盤（Rota），融合了新柏拉圖主義、赫密士哲學與古典占星。

**四層輪盤結構：**

| 層級 | 內容 | 控制行星 | 象徵 |
|------|------|----------|------|
| 第一層（最外）| 古典字母 + 符號 | ☉ 太陽 + ASC 上升點 | 宇宙語言、意識表達 |
| 第二層 | 羅馬數字 I–XII | ☽ 月亮 | 命運之宮、情感週期 |
| 第三層 | 七古典行星符號 | ☿ 水星 + ♀ 金星 | 溝通、美感、智識 |
| 第四層（最內）| 十二星座命運區域 | ♂ ♃ ♄ | 宏觀命運走向 |

**月交點調節**：☊ 北交點（業力加持）、☋ 南交點（業力課題），
影響解讀的吉凶傾向，但不直接控制輪盤旋轉。

**使用方法**：
1. 輸入出生星盤各行星黃道度數（0–360°）
2. 點擊「根據星盤設定輪盤並解讀」
3. 各層自動旋轉至星盤決定的位置
4. 也可手動拖曳任一層輪盤以自由探索
5. 閱讀四層解讀與綜合天機

*此工具融合古典弗拉德神秘哲學與占星學，僅作靈性探索與冥想之用。*
"""
