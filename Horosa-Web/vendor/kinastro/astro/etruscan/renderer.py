"""
astro/etruscan/renderer.py — Streamlit renderer for Etruscan Astrology
=======================================================================

Renders the complete Etruscan astrology UI including:
  • Piacenza Liver SVG — interactive 16-sector bronze liver visualisation
  • Lightning Divination — fulguratores interpretation of the Sun's Templum
  • Planetary Templum table — all 7 classical planets with region details
  • Oracle Reading cards — per-planet deity interpretation cards

IMPORTANT: All ``import streamlit`` statements are inside function bodies,
per CONTRIBUTING.md convention, so this module can be safely imported in
unit-test contexts where Streamlit is not present.

伊特魯里亞占星 Streamlit 渲染模組。
所有 streamlit import 均在函數體內，符合 CONTRIBUTING.md 規範。
"""

from __future__ import annotations

import math
from typing import Any, Callable, Optional

from .constants import BRONZE_THEME, LIGHTNING_INTERPRETATIONS, TEMPLUM_16
from .models import EtruscanChart, EtruscanPlanetPosition


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _region_lookup() -> dict[int, dict]:
    """Build a dict mapping region number (1–16) to its TEMPLUM_16 entry."""
    return {t["region"]: t for t in TEMPLUM_16}


def _nature_color(nature: str) -> str:
    """Return the hex colour for a nature string."""
    return {
        "favorable":   BRONZE_THEME["favorable"],
        "unfavorable": BRONZE_THEME["unfavorable"],
        "neutral":     BRONZE_THEME["neutral"],
    }.get(nature, BRONZE_THEME["neutral"])


def _nature_icon(nature: str) -> str:
    """Return an icon character for a nature string."""
    return {"favorable": "✦", "unfavorable": "✖", "neutral": "◆"}.get(nature, "◆")


# ─────────────────────────────────────────────────────────────────────────────
# SVG / HTML builder — Piacenza Liver
# ─────────────────────────────────────────────────────────────────────────────

def build_piacenza_liver_svg(
    chart: Any,
    lang: str = "zh",
    width: int = 900,  # kept for backward compatibility; ignored (responsive layout used instead)
) -> str:
    """Generate an interactive HTML string with the Piacenza Liver visualisation.

    生成皮亞琴察青銅肝臟的互動式 SVG/HTML 字串。
    包含16個 Templum 扇形、行星標記、Bronze 風格裝飾及懸停工具提示。

    The Piacenza Liver (c. 100 BCE) is a bronze sheep liver divided into
    regions corresponding to the Etruscan Templum sky-division. Each region
    is labelled with the presiding deity, allowing haruspices to read divine
    messages from the organ's condition.

    Args:
        chart:  An EtruscanChart instance.
        lang:   "zh" or "en" for label language.
        width:  SVG viewBox width in pixels (height is 600).

    Returns:
        A complete self-contained HTML string (SVG + inline CSS + JS).
    """
    cx, cy = 430, 295          # liver centre
    rx, ry = 360, 230          # liver ellipse radii
    height = 600
    _SECTOR_RADIUS = 420.0     # exaggerated radius for sector wedge lines, clipped by liver ellipse

    region_map = _region_lookup()

    # ── Build planet → region mapping (multiple planets can share a region) ──
    planet_by_region: dict[int, list[EtruscanPlanetPosition]] = {}
    for pos in chart.planet_positions:
        planet_by_region.setdefault(pos.templum_region, []).append(pos)

    # ── SVG sector wedges ──
    # Each sector is a 22.5° wedge from the liver centre.
    # We clip the wedge to the liver ellipse using a large radius (400px).
    sector_paths: list[str] = []
    label_elements: list[str] = []
    planet_markers: list[str] = []

    for t in TEMPLUM_16:
        r_num = t["region"]
        az_start = t["azimuth_start"]
        az_end = t["azimuth_end"]
        color = t["color"]
        nature = t["nature"]
        name_label = t["name_zh"] if lang == "zh" else t["name_etruscan"]
        deity_label = t["deity_zh"] if lang == "zh" else t["deity_en"]
        nature_label = t["nature_zh"] if lang == "zh" else t["nature"]

        # Sector wedge — use a large radius clipped by ellipse viewBox
        # Convert azimuth (0=N, clockwise) to SVG angle (0=right, counter-clockwise maths)
        # SVG: angle 0° = right (+x), increasing clockwise in screen coords.
        # Azimuth: 0° = North (up = -y in SVG), increasing clockwise.
        # Conversion: svg_angle = azimuth - 90°

        def az_to_svg(az: float) -> tuple[float, float]:
            """Convert azimuth to SVG x,y at _SECTOR_RADIUS from centre."""
            svg_ang = math.radians(az - 90.0)
            x = cx + _SECTOR_RADIUS * math.cos(svg_ang)
            y = cy + _SECTOR_RADIUS * math.sin(svg_ang)
            return x, y

        x1, y1 = az_to_svg(az_start)
        x2, y2 = az_to_svg(az_end)

        # Build sector path: M centre, L x1 y1, A (large arc), L centre Z
        large_arc = 0  # always < 180°
        r_str = f"{_SECTOR_RADIUS:.0f}"
        path_d = (
            f"M {cx},{cy} "
            f"L {x1:.1f},{y1:.1f} "
            f"A {r_str},{r_str} 0 {large_arc},1 {x2:.1f},{y2:.1f} "
            f"Z"
        )

        # Fill opacity varies by nature
        opacity = "0.45" if nature == "favorable" else ("0.40" if nature == "unfavorable" else "0.30")

        # Build tooltip data attributes
        interp = t["interpretation_zh"] if lang == "zh" else t["interpretation_en"]
        tooltip_title = f"第{r_num}區 {t['name_zh']}" if lang == "zh" else f"Region {r_num}: {t['name_en']}"

        sector_paths.append(
            f'<path d="{path_d}" fill="{color}" fill-opacity="{opacity}" '
            f'stroke="{BRONZE_THEME["border"]}" stroke-width="0.8" '
            f'class="sector" data-region="{r_num}" '
            f'data-title="{tooltip_title}" '
            f'data-deity="{deity_label}" '
            f'data-nature="{nature_label}" '
            f'data-interp="{interp}" />'
        )

        # ── Region label ──
        # Place text at the midpoint angle, at ~70% of the ellipse radius
        mid_az = (az_start + az_end) / 2.0
        mid_svg_ang = math.radians(mid_az - 90.0)
        label_r = 230.0
        lx = cx + label_r * math.cos(mid_svg_ang)
        ly = cy + label_r * math.sin(mid_svg_ang)

        # Short label: region number + short deity name
        short_name = name_label.split("/")[0] if "/" in name_label else name_label
        # Limit label to ~10 chars for readability
        short_name = short_name[:10]

        label_elements.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" '
            f'text-anchor="middle" dominant-baseline="middle" '
            f'font-size="8.5" fill="{BRONZE_THEME["text"]}" '
            f'font-family="serif" pointer-events="none" opacity="0.9">'
            f'{r_num}·{short_name}</text>'
        )

        # ── Planet markers for this region ──
        planets_here = planet_by_region.get(r_num, [])
        for i, pos in enumerate(planets_here):
            # Stagger multiple planets in the same region
            marker_r = 160.0 + i * 22.0
            mx = cx + marker_r * math.cos(mid_svg_ang)
            my = cy + marker_r * math.sin(mid_svg_ang)

            p_name = pos.planet_name_zh if lang == "zh" else pos.planet_name_en
            p_tooltip = (
                f"{pos.glyph} {p_name} | "
                + (f"方位角:{pos.azimuth:.1f}° 高度:{pos.altitude:.1f}°" if lang == "zh"
                   else f"Az:{pos.azimuth:.1f}° Alt:{pos.altitude:.1f}°")
            )

            above_stroke = BRONZE_THEME["gold"] if pos.is_above_horizon else BRONZE_THEME["neutral"]

            planet_markers.append(
                f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="10" '
                f'fill="{BRONZE_THEME["black_gold"]}" '
                f'stroke="{above_stroke}" stroke-width="2" '
                f'class="planet-marker" data-planet="{p_tooltip}" />'
            )
            planet_markers.append(
                f'<text x="{mx:.1f}" y="{my:.1f}" '
                f'text-anchor="middle" dominant-baseline="middle" '
                f'font-size="11" fill="{BRONZE_THEME["gold"]}" '
                f'pointer-events="none">{pos.glyph}</text>'
            )

    # ── Spiral decoration (porta hepatis) — centre-left ──
    spiral_parts: list[str] = []
    for step in range(72):
        angle = math.radians(step * 5)
        r_spiral = 12 + step * 0.4
        sx = cx - 100 + r_spiral * math.cos(angle)
        sy = cy - 30 + r_spiral * math.sin(angle)
        if step == 0:
            spiral_parts.append(f"M {sx:.1f},{sy:.1f}")
        else:
            spiral_parts.append(f"L {sx:.1f},{sy:.1f}")
    spiral_d = " ".join(spiral_parts)

    # ── Assemble SVG ──
    sectors_svg = "\n    ".join(sector_paths)
    labels_svg = "\n    ".join(label_elements)
    markers_svg = "\n    ".join(planet_markers)

    # Build planet legend lines for JS tooltip context
    legend_data_lines: list[str] = []
    for pos in chart.planet_positions:
        t_data = region_map.get(pos.templum_region, {})
        lbl = (
            f"{pos.glyph} {pos.planet_name_zh}: 第{pos.templum_region}區 {t_data.get('name_zh','')}"
            if lang == "zh" else
            f"{pos.glyph} {pos.planet_name_en}: Region {pos.templum_region} {t_data.get('name_en','')}"
        )
        legend_data_lines.append(lbl)
    legend_text = "&#10;".join(legend_data_lines)

    html = f"""
<div style="background:{BRONZE_THEME['bg']};padding:20px;border-radius:12px;
     border:1px solid {BRONZE_THEME['border']};position:relative;
     width:100%;box-sizing:border-box">

  <!-- Tooltip overlay -->
  <div id="etruscan-tooltip" style="
    display:none;position:fixed;z-index:9999;max-width:320px;
    background:{BRONZE_THEME['bg_card']};border:1px solid {BRONZE_THEME['gold']};
    border-radius:8px;padding:12px 16px;pointer-events:none;
    color:{BRONZE_THEME['text']};font-family:serif;font-size:13px;
    box-shadow:0 4px 24px rgba(0,0,0,0.7);">
    <div id="etruscan-tt-title" style="color:{BRONZE_THEME['gold']};font-size:15px;
         font-weight:bold;margin-bottom:6px"></div>
    <div id="etruscan-tt-deity" style="margin-bottom:4px"></div>
    <div id="etruscan-tt-nature" style="margin-bottom:4px"></div>
    <div id="etruscan-tt-interp" style="font-style:italic;color:{BRONZE_THEME['text']};
         opacity:0.85;font-size:12px"></div>
  </div>

  <div style="width:100%;max-width:900px;margin:0 auto">
  <svg viewBox="0 0 900 600" width="100%"
       xmlns="http://www.w3.org/2000/svg" id="piacenza-liver-svg"
       style="display:block">

    <defs>
      <!-- Radial gradient: warm bronze centre → dark edge -->
      <radialGradient id="liver-grad" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#C89A5A" stop-opacity="0.85"/>
        <stop offset="60%"  stop-color="#6B4A28" stop-opacity="0.70"/>
        <stop offset="100%" stop-color="#2A1510" stop-opacity="0.90"/>
      </radialGradient>

      <!-- Ellipse clip path for the liver shape -->
      <clipPath id="liver-clip">
        <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/>
      </clipPath>

      <!-- Outer parchment background gradient -->
      <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%"   stop-color="#1A0F06"/>
        <stop offset="100%" stop-color="#0D0804"/>
      </linearGradient>
    </defs>

    <!-- Outer background -->
    <rect width="900" height="600" fill="url(#bg-grad)"/>

    <!-- Liver base ellipse -->
    <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"
             fill="url(#liver-grad)" stroke="{BRONZE_THEME['border']}" stroke-width="3"/>

    <!-- Sector wedges (clipped to liver ellipse) -->
    <g clip-path="url(#liver-clip)">
      {sectors_svg}
    </g>

    <!-- Liver ellipse border overlay (on top of wedges) -->
    <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"
             fill="none" stroke="{BRONZE_THEME['gold']}" stroke-width="2.5" opacity="0.7"/>

    <!-- Inner circle to represent the pyramidal process / gallbladder -->
    <circle cx="{cx}" cy="{cy}" r="48"
            fill="{BRONZE_THEME['bg_card']}" stroke="{BRONZE_THEME['gold']}"
            stroke-width="2" opacity="0.8"/>
    <text x="{cx}" y="{cy - 6}" text-anchor="middle" font-size="13"
          fill="{BRONZE_THEME['gold']}" font-family="serif">TVRAN</text>
    <text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="9"
          fill="{BRONZE_THEME['text']}" font-family="serif" opacity="0.7">Templum</text>

    <!-- Spiral decoration (porta hepatis) -->
    <path d="{spiral_d}" fill="none" stroke="{BRONZE_THEME['bronze']}"
          stroke-width="0.8" opacity="0.4"/>

    <!-- North direction indicator -->
    <text x="{cx}" y="52" text-anchor="middle" font-size="11"
          fill="{BRONZE_THEME['gold']}" font-family="serif" opacity="0.8">N ↑</text>
    <text x="{cx}" y="562" text-anchor="middle" font-size="11"
          fill="{BRONZE_THEME['gold']}" font-family="serif" opacity="0.8">S ↓</text>
    <text x="28" y="{cy + 4}" text-anchor="middle" font-size="11"
          fill="{BRONZE_THEME['gold']}" font-family="serif" opacity="0.8">W</text>
    <text x="866" y="{cy + 4}" text-anchor="middle" font-size="11"
          fill="{BRONZE_THEME['gold']}" font-family="serif" opacity="0.8">E</text>

    <!-- Region labels -->
    {labels_svg}

    <!-- Planet markers -->
    {markers_svg}

    <!-- Title -->
    <text x="450" y="26" text-anchor="middle" font-size="16"
          fill="{BRONZE_THEME['header']}" font-family="serif" font-weight="bold">
      🏺 {"皮亞琴察肝臟 — 伊特魯里亞天宮16區" if lang == "zh" else "Piacenza Liver — Etruscan Templum XVI"}
    </text>

  </svg>
  </div><!-- end responsive wrapper -->

  <script>
  (function() {{
    var tt = document.getElementById('etruscan-tooltip');
    var ttTitle  = document.getElementById('etruscan-tt-title');
    var ttDeity  = document.getElementById('etruscan-tt-deity');
    var ttNature = document.getElementById('etruscan-tt-nature');
    var ttInterp = document.getElementById('etruscan-tt-interp');

    function showTooltip(e, title, deity, nature, interp) {{
      ttTitle.textContent  = title;
      ttDeity.textContent  = deity;
      ttNature.textContent = nature;
      ttInterp.textContent = interp;
      tt.style.display = 'block';
      moveTooltip(e);
    }}
    function moveTooltip(e) {{
      var x = e.clientX + 14;
      var y = e.clientY - 14;
      if (x + 346 > window.innerWidth) x = e.clientX - 346;
      tt.style.left = x + 'px';
      tt.style.top  = y + 'px';
    }}
    function hideTooltip() {{
      tt.style.display = 'none';
    }}

    // Sector hover
    document.querySelectorAll('#piacenza-liver-svg .sector').forEach(function(el) {{
      el.addEventListener('mouseenter', function(e) {{
        el.style.fillOpacity = '0.75';
        showTooltip(e,
          el.dataset.title,
          el.dataset.deity,
          el.dataset.nature,
          el.dataset.interp
        );
      }});
      el.addEventListener('mousemove', moveTooltip);
      el.addEventListener('mouseleave', function() {{
        el.style.fillOpacity = '';
        hideTooltip();
      }});
    }});

    // Planet marker hover
    document.querySelectorAll('#piacenza-liver-svg .planet-marker').forEach(function(el) {{
      el.addEventListener('mouseenter', function(e) {{
        showTooltip(e, el.dataset.planet, '', '', '');
      }});
      el.addEventListener('mousemove', moveTooltip);
      el.addEventListener('mouseleave', hideTooltip);
    }});

    // Responsive iframe height — notify Streamlit parent
    function notifyHeight() {{
      var svg = document.getElementById('piacenza-liver-svg');
      if (!svg) return;
      var rect = svg.getBoundingClientRect();
      var h = Math.round(rect.height) + 60;  // +60 for outer div padding/border
      window.parent.postMessage({{type: 'streamlit:setFrameHeight', height: h}}, '*');
    }}
    setTimeout(notifyHeight, 120);  // wait for layout to settle before measuring
    window.addEventListener('resize', notifyHeight);
  }})();
  </script>
</div>
"""
    return html


# ─────────────────────────────────────────────────────────────────────────────
# Streamlit card builders
# ─────────────────────────────────────────────────────────────────────────────

def _region_card_html(
    t_data: dict,
    planets_here: list[EtruscanPlanetPosition],
    lang: str = "zh",
) -> str:
    """Build an HTML card for a single Templum region."""
    nature = t_data.get("nature", "neutral")
    color = _nature_color(nature)
    icon = _nature_icon(nature)
    r_num = t_data.get("region", "?")
    name = t_data.get("name_zh" if lang == "zh" else "name_en", "")
    deity = t_data.get("deity_zh" if lang == "zh" else "deity_en", "")
    interp = t_data.get("interpretation_zh" if lang == "zh" else "interpretation_en", "")
    nature_label = t_data.get("nature_zh" if lang == "zh" else "nature", "")

    planet_badges = ""
    for pos in planets_here:
        p_name = pos.planet_name_zh if lang == "zh" else pos.planet_name_en
        planet_badges += (
            f'<span style="background:{BRONZE_THEME["black_gold"]};'
            f'border:1px solid {color};border-radius:4px;'
            f'padding:2px 8px;margin:2px;display:inline-block;font-size:12px;">'
            f'{pos.glyph} {p_name}</span>'
        )

    return f"""
<div style="background:{BRONZE_THEME['bg_card']};border-left:4px solid {color};
     border-radius:8px;padding:14px 18px;margin:8px 0;
     border:1px solid {BRONZE_THEME['border']};">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
    <span style="color:{color};font-size:18px">{icon}</span>
    <span style="color:{color};font-size:16px;font-weight:bold">
      {("第" + str(r_num) + "區") if lang == "zh" else ("Region " + str(r_num))} — {name}
    </span>
    <span style="background:{color};color:{BRONZE_THEME['bg']};
          border-radius:4px;padding:1px 8px;font-size:11px;margin-left:auto">
      {nature_label}
    </span>
  </div>
  <div style="color:{BRONZE_THEME['text']};font-size:13px;margin-bottom:6px">{deity}</div>
  <div style="color:{BRONZE_THEME['text']};font-size:12px;opacity:0.85;
       font-style:italic;margin-bottom:6px">{interp}</div>
  {('<div style="margin-top:6px">' + planet_badges + '</div>') if planet_badges else ''}
</div>
"""


def _planet_detail_card_html(
    pos: EtruscanPlanetPosition,
    t_data: dict,
    lang: str = "zh",
) -> str:
    """Build a detailed HTML interpretation card for one planet."""
    nature = t_data.get("nature", "neutral")
    color = _nature_color(nature)
    r_num = pos.templum_region
    p_name = pos.planet_name_zh if lang == "zh" else pos.planet_name_en
    t_name = t_data.get("name_zh" if lang == "zh" else "name_en", "")
    deity = t_data.get("deity_zh" if lang == "zh" else "deity_en", "")
    interp = t_data.get("interpretation_zh" if lang == "zh" else "interpretation_en", "")
    nature_label = t_data.get("nature_zh" if lang == "zh" else "nature", "")
    above_label = ("地平線上方" if lang == "zh" else "Above horizon") if pos.is_above_horizon else (
        "地平線下方" if lang == "zh" else "Below horizon"
    )
    above_color = BRONZE_THEME["favorable"] if pos.is_above_horizon else BRONZE_THEME["neutral"]

    region_label = f"第{r_num}區" if lang == "zh" else f"Templum {r_num}"
    az_label = "方位角" if lang == "zh" else "Azimuth"
    alt_label = "高度角" if lang == "zh" else "Altitude"
    sign_label = "星座" if lang == "zh" else "Sign"

    return f"""
<div style="background:{BRONZE_THEME['bg_card']};
     border:1px solid {color};border-radius:10px;
     padding:16px 20px;margin:10px 0;">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
    <span style="font-size:26px">{pos.glyph}</span>
    <div>
      <div style="color:{BRONZE_THEME['header']};font-size:17px;font-weight:bold">
        {p_name}
      </div>
      <div style="color:{color};font-size:13px">
        {region_label} — {t_name}
        <span style="background:{color};color:{BRONZE_THEME['bg']};
              border-radius:4px;padding:1px 7px;font-size:11px;margin-left:8px">
          {nature_label}
        </span>
      </div>
    </div>
  </div>
  <div style="color:{BRONZE_THEME['text']};font-size:13px;margin-bottom:8px;
       border-left:3px solid {color};padding-left:10px">{deity}</div>
  <div style="color:{BRONZE_THEME['text']};font-size:12px;font-style:italic;
       margin-bottom:10px;opacity:0.88">{interp}</div>
  <div style="display:flex;gap:16px;flex-wrap:wrap;font-size:12px;
       color:{BRONZE_THEME['bronze']}">
    <span>{az_label}: {pos.azimuth:.1f}°</span>
    <span>{alt_label}: {pos.altitude:.1f}°</span>
    <span>{sign_label}: {pos.sign}</span>
    <span style="color:{above_color}">{above_label}</span>
  </div>
</div>
"""


def _lightning_card_html(
    chart: EtruscanChart,
    t_data: dict,
    lang: str = "zh",
) -> str:
    """Build the lightning divination HTML card."""
    nature = t_data.get("nature", "neutral")
    color = _nature_color(nature)
    r_num = chart.lightning_region
    t_name = t_data.get("name_zh" if lang == "zh" else "name_en", "")
    deity = t_data.get("deity_zh" if lang == "zh" else "deity_en", "")
    interp = t_data.get("interpretation_zh" if lang == "zh" else "interpretation_en", "")
    thunder = t_data.get("thunder_type") or ("—" if lang == "zh" else "—")
    nature_label = t_data.get("nature_zh" if lang == "zh" else "nature", "")

    # Lightning interpretation based on region mod 9 → 1–9 type
    lt_idx = (r_num - 1) % 9
    lt = LIGHTNING_INTERPRETATIONS[lt_idx]
    lt_desc = lt["description_zh"] if lang == "zh" else lt["description_en"]
    severity = lt["severity"]
    severity_bars = "⚡" * severity + "·" * (5 - severity)

    title_zh = "⚡ 閃電占卜 — 太陽天宮區域"
    title_en = "⚡ Lightning Divination — Sun's Templum Region"
    region_label = f"第{r_num}區" if lang == "zh" else f"Region {r_num}"
    thunder_label = "雷霆類型" if lang == "zh" else "Thunder type"
    lt_num_label = f"廷尼亞第{lt['type_num']}雷" if lang == "zh" else f"Tinia's Bolt #{lt['type_num']}"
    severity_label = "強度" if lang == "zh" else "Severity"

    return f"""
<div style="background:{BRONZE_THEME['bg_card']};
     border:2px solid {color};border-radius:12px;
     padding:20px 24px;margin:12px 0;">
  <div style="color:{BRONZE_THEME['header']};font-size:18px;font-weight:bold;
       margin-bottom:12px">
    {title_zh if lang == "zh" else title_en}
  </div>
  <div style="display:flex;align-items:baseline;gap:12px;margin-bottom:10px">
    <span style="color:{color};font-size:22px;font-weight:bold">{region_label}</span>
    <span style="color:{BRONZE_THEME['text']};font-size:16px">{t_name}</span>
    <span style="background:{color};color:{BRONZE_THEME['bg']};
          border-radius:4px;padding:2px 10px;font-size:12px">{nature_label}</span>
  </div>
  <div style="color:{BRONZE_THEME['text']};font-size:14px;margin-bottom:8px;
       border-left:4px solid {color};padding-left:12px">{deity}</div>
  <div style="color:{BRONZE_THEME['text']};font-size:13px;font-style:italic;
       margin-bottom:12px;opacity:0.88">{interp}</div>
  <div style="background:{BRONZE_THEME['black_gold']};border-radius:8px;
       padding:12px 16px;border:1px solid {BRONZE_THEME['border']}">
    <div style="color:{BRONZE_THEME['gold']};font-size:13px;font-weight:bold;
         margin-bottom:4px">
      {thunder_label}: {thunder} | {lt_num_label}
    </div>
    <div style="color:{BRONZE_THEME['text']};font-size:13px;margin-bottom:6px">
      {lt_desc}
    </div>
    <div style="color:{BRONZE_THEME['bronze']};font-size:13px">
      {severity_label}: {severity_bars}
    </div>
  </div>
</div>
"""


def _planet_table_html(
    chart: EtruscanChart,
    region_map: dict[int, dict],
    lang: str = "zh",
) -> str:
    """Build an HTML table of all planet positions."""
    headers = (
        ["行星", "符號", "區域", "神祇", "天性", "方位角", "高度角", "星座"]
        if lang == "zh" else
        ["Planet", "Glyph", "Region", "Deity", "Nature", "Azimuth", "Altitude", "Sign"]
    )
    th_style = (
        f'style="background:{BRONZE_THEME["black_gold"]};'
        f'color:{BRONZE_THEME["gold"]};padding:8px 10px;'
        f'border:1px solid {BRONZE_THEME["border"]};font-family:serif"'
    )
    rows = ""
    for pos in chart.planet_positions:
        t_data = region_map.get(pos.templum_region, {})
        nature = t_data.get("nature", "neutral")
        nature_color = _nature_color(nature)
        p_name = pos.planet_name_zh if lang == "zh" else pos.planet_name_en
        t_name = t_data.get("name_zh" if lang == "zh" else "name_en", "")
        deity = t_data.get("deity_zh" if lang == "zh" else "deity_en", "")
        nature_label = t_data.get("nature_zh" if lang == "zh" else "nature", "")
        r_label = f"第{pos.templum_region}區" if lang == "zh" else f"T{pos.templum_region}"
        above = "▲" if pos.is_above_horizon else "▽"
        above_c = BRONZE_THEME["favorable"] if pos.is_above_horizon else BRONZE_THEME["neutral"]
        td = f'style="padding:7px 10px;border:1px solid {BRONZE_THEME["border"]};color:{BRONZE_THEME["text"]};font-family:serif"'
        deity_short = (deity[:30] + "…") if len(deity) > 30 else deity
        rows += f"""
<tr style="background:{BRONZE_THEME['bg_card']}">
  <td {td}>{p_name}</td>
  <td {td} style="padding:7px 10px;border:1px solid {BRONZE_THEME['border']};text-align:center;font-size:16px">{pos.glyph}</td>
  <td {td} style="padding:7px 10px;border:1px solid {BRONZE_THEME['border']};color:{nature_color};font-weight:bold">{r_label}</td>
  <td {td} style="padding:7px 10px;border:1px solid {BRONZE_THEME['border']};color:{BRONZE_THEME['text']};font-size:12px">{t_name} — {deity_short}</td>
  <td {td} style="padding:7px 10px;border:1px solid {BRONZE_THEME['border']};color:{nature_color}">{nature_label}</td>
  <td {td}>{pos.azimuth:.1f}°</td>
  <td {td}><span style="color:{above_c}">{above}</span> {pos.altitude:.1f}°</td>
  <td {td}>{pos.sign}</td>
</tr>"""

    headers_html = "".join(f"<th {th_style}>{h}</th>" for h in headers)
    return f"""
<div style="overflow-x:auto">
<table style="width:100%;border-collapse:collapse;font-size:13px">
  <thead><tr>{headers_html}</tr></thead>
  <tbody>{rows}</tbody>
</table>
</div>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Main Streamlit render function
# ─────────────────────────────────────────────────────────────────────────────

def render_streamlit(
    chart: EtruscanChart,
    after_chart_hook: Optional[Callable] = None,
    lang: Optional[str] = None,
) -> None:
    """Render the complete Etruscan astrology UI in Streamlit.

    伊特魯里亞占星 Streamlit 主渲染函數。
    包含4個標籤頁：肝臟圖、閃電占卜、行星天宮、占卜解讀。

    Args:
        chart:            Computed EtruscanChart.
        after_chart_hook: Optional callable invoked after the main header,
                          before the tabs (e.g. for sharing / export buttons).
        lang:             Language override ("zh" | "en"). Defaults to "zh".
    """
    import streamlit as st
    import streamlit.components.v1 as components

    if lang is None:
        lang = "zh"

    region_map = _region_lookup()

    # ── Decorative header ──
    gold = BRONZE_THEME["gold"]
    bronze = BRONZE_THEME["bronze"]
    header_bg = BRONZE_THEME["bg_card"]
    header_border = BRONZE_THEME["border"]

    date_str = (
        f"{chart.year}年{chart.month}月{chart.day}日 {chart.hour:02d}:{chart.minute:02d}"
        if lang == "zh" else
        f"{chart.year}-{chart.month:02d}-{chart.day:02d} {chart.hour:02d}:{chart.minute:02d}"
    )
    loc_str = chart.location_name or (
        f"緯度{chart.latitude:.2f}°, 經度{chart.longitude:.2f}°"
        if lang == "zh" else
        f"lat {chart.latitude:.2f}°, lon {chart.longitude:.2f}°"
    )

    nature_color = _nature_color(chart.dominant_nature)
    nature_label_map = {
        "zh":  {"favorable": "吉", "unfavorable": "凶", "neutral": "中性"},
        "en":  {"favorable": "Favorable", "unfavorable": "Unfavorable", "neutral": "Neutral"},
    }
    nature_display = nature_label_map[lang].get(chart.dominant_nature, chart.dominant_nature)

    ritual_labels = {
        "zh": {"birth": "出生命盤", "national": "國事占卜",
               "personal": "個人占卜", "weather": "天氣占卜"},
        "en": {"birth": "Birth Chart", "national": "National Divination",
               "personal": "Personal Reading", "weather": "Weather Divination"},
    }
    ritual_display = ritual_labels[lang].get(chart.ritual_type, chart.ritual_type)

    subtitle = (
        "青銅肝臟占卜 · 天宮十六區 · 閃電神諭"
        if lang == "zh" else
        "Bronze Liver Divination · XVI Templa · Lightning Oracle"
    )

    st.markdown(
        f"""
<div style="background:{header_bg};border:1px solid {header_border};
     border-radius:12px;padding:20px 28px;margin-bottom:16px;
     border-top:4px solid {gold}">
  <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
    <div>
      <div style="color:{gold};font-size:24px;font-weight:bold;font-family:serif">
        🏺 伊特魯里亞占星 / Etruscan Astrology
      </div>
      <div style="color:{bronze};font-size:13px;margin-top:4px">{subtitle}</div>
    </div>
    <div style="margin-left:auto;text-align:right">
      <div style="color:{BRONZE_THEME['text']};font-size:14px">{date_str}</div>
      <div style="color:{bronze};font-size:12px">{loc_str}</div>
      <div style="margin-top:4px">
        <span style="background:{nature_color};color:{BRONZE_THEME['bg']};
              border-radius:4px;padding:2px 10px;font-size:12px;font-weight:bold">
          {nature_display}
        </span>
        <span style="color:{bronze};font-size:12px;margin-left:8px">{ritual_display}</span>
      </div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if after_chart_hook is not None:
        after_chart_hook()

    # ── Tab labels ──
    if lang == "zh":
        tab_labels = [
            "🏺 皮亞琴察肝臟 / Piacenza Liver",
            "⚡ 閃電占卜 / Lightning Divination",
            "🌟 行星天宮 / Planetary Templum",
            "📖 占卜解讀 / Oracle Reading",
        ]
    else:
        tab_labels = [
            "🏺 Piacenza Liver",
            "⚡ Lightning Divination",
            "🌟 Planetary Templum",
            "📖 Oracle Reading",
        ]

    tab1, tab2, tab3, tab4 = st.tabs(tab_labels)

    # ─────────────────────────────────────────────────────────────────────────
    # Tab 1 — Piacenza Liver SVG
    # ─────────────────────────────────────────────────────────────────────────
    with tab1:
        svg_html = build_piacenza_liver_svg(chart, lang=lang)
        components.html(svg_html, height=700)

        # Legend cards for occupied Templum regions
        occupied_regions = sorted(
            {pos.templum_region for pos in chart.planet_positions}
        )
        if occupied_regions:
            legend_title = "占用區域" if lang == "zh" else "Occupied Regions"
            st.markdown(
                f'<div style="color:{gold};font-size:15px;font-weight:bold;'
                f'margin-top:16px;margin-bottom:8px">{legend_title}</div>',
                unsafe_allow_html=True,
            )
            planet_by_region: dict[int, list] = {}
            for pos in chart.planet_positions:
                planet_by_region.setdefault(pos.templum_region, []).append(pos)

            cols = st.columns(2)
            for idx, r_num in enumerate(occupied_regions):
                t_data = region_map.get(r_num, {})
                planets_here = planet_by_region.get(r_num, [])
                with cols[idx % 2]:
                    st.markdown(
                        _region_card_html(t_data, planets_here, lang=lang),
                        unsafe_allow_html=True,
                    )

    # ─────────────────────────────────────────────────────────────────────────
    # Tab 2 — Lightning Divination
    # ─────────────────────────────────────────────────────────────────────────
    with tab2:
        t_data = region_map.get(chart.lightning_region, {})
        st.markdown(
            _lightning_card_html(chart, t_data, lang=lang),
            unsafe_allow_html=True,
        )

        # Sun and Moon positions in detail
        st.markdown(
            f'<div style="color:{gold};font-size:15px;font-weight:bold;'
            f'margin-top:16px;margin-bottom:8px">'
            + ("日月占卜詳情" if lang == "zh" else "Sun & Moon Detail")
            + "</div>",
            unsafe_allow_html=True,
        )
        for pos in chart.planet_positions:
            if pos.planet_id in (0, 1):  # Sun and Moon
                t_data_p = region_map.get(pos.templum_region, {})
                st.markdown(
                    _planet_detail_card_html(pos, t_data_p, lang=lang),
                    unsafe_allow_html=True,
                )

    # ─────────────────────────────────────────────────────────────────────────
    # Tab 3 — Planetary Templum table
    # ─────────────────────────────────────────────────────────────────────────
    with tab3:
        table_title = "七星天宮位置表" if lang == "zh" else "Seven Planets — Templum Positions"
        st.markdown(
            f'<div style="color:{gold};font-size:15px;font-weight:bold;'
            f'margin-bottom:10px">{table_title}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            _planet_table_html(chart, region_map, lang=lang),
            unsafe_allow_html=True,
        )

        # Nature distribution summary
        nature_counts: dict[str, int] = {"favorable": 0, "unfavorable": 0, "neutral": 0}
        for pos in chart.planet_positions:
            n = region_map.get(pos.templum_region, {}).get("nature", "neutral")
            nature_counts[n] = nature_counts.get(n, 0) + 1

        summary_title = "天性分布" if lang == "zh" else "Nature Distribution"
        st.markdown(
            f'<div style="color:{gold};font-size:14px;font-weight:bold;'
            f'margin-top:18px;margin-bottom:8px">{summary_title}</div>',
            unsafe_allow_html=True,
        )
        fav_label = "吉" if lang == "zh" else "Favorable"
        unf_label = "凶" if lang == "zh" else "Unfavorable"
        neu_label = "中性" if lang == "zh" else "Neutral"
        col_a, col_b, col_c = st.columns(3)
        col_a.metric(fav_label, nature_counts["favorable"])
        col_b.metric(unf_label, nature_counts["unfavorable"])
        col_c.metric(neu_label, nature_counts["neutral"])

    # ─────────────────────────────────────────────────────────────────────────
    # Tab 4 — Oracle Reading (per-planet interpretation cards)
    # ─────────────────────────────────────────────────────────────────────────
    with tab4:
        oracle_title = "占卜解讀" if lang == "zh" else "Oracle Reading"
        oracle_sub = (
            "每顆行星在其 Templum 區域的神意解讀"
            if lang == "zh" else
            "Divine interpretation of each planet in its Templum region"
        )
        st.markdown(
            f'<div style="color:{gold};font-size:16px;font-weight:bold">{oracle_title}</div>'
            f'<div style="color:{bronze};font-size:12px;margin-bottom:12px">{oracle_sub}</div>',
            unsafe_allow_html=True,
        )
        for pos in chart.planet_positions:
            t_data_p = region_map.get(pos.templum_region, {})
            st.markdown(
                _planet_detail_card_html(pos, t_data_p, lang=lang),
                unsafe_allow_html=True,
            )

        # Full chart summary at bottom
        st.markdown(
            f'<div style="color:{gold};font-size:14px;font-weight:bold;'
            f'margin-top:18px;margin-bottom:8px">'
            + ("命盤整體摘要" if lang == "zh" else "Chart Summary")
            + "</div>",
            unsafe_allow_html=True,
        )
        summary_text = chart.summary_zh() if lang == "zh" else chart.summary_en()
        st.code(summary_text, language=None)
