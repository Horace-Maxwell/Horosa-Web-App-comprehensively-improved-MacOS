"""
astro/world_map.py — Interactive SVG world map for the Kin Astro homepage.

Regions are highlighted on hover and display popup buttons for the astrology
systems associated with each region.  Clicking a button sets the sidebar
dropdown via Streamlit's ``st.session_state``.
"""

from __future__ import annotations

import streamlit as st
from astro.i18n import get_lang

# ── Region → astrology systems mapping ─────────────────────────────────────
# Each entry: region_id → { "zh": label, "en": label, "color": hex,
#   "systems": [ (session_key, zh_label, en_label), … ] }
REGIONS: dict[str, dict] = {
    "china": {
        "zh": "中國",
        "en": "China",
        "color": "#e74c3c",
        "systems": [
            ("tab_chinese", "🀄 七政四餘", "🀄 Seven Governors"),
            ("tab_ziwei", "🌟 紫微斗數", "🌟 Zi Wei Dou Shu"),
        ],
    },
    "india": {
        "zh": "印度",
        "en": "India",
        "color": "#f39c12",
        "systems": [
            ("tab_indian", "🙏 印度占星", "🙏 Indian Astrology"),
            ("tab_nadi", "🔱 納迪占星", "🔱 Nadi Jyotish"),
        ],
    },
    "japan": {
        "zh": "日本",
        "en": "Japan",
        "color": "#e84393",
        "systems": [
            ("tab_sukkayodo", "🈳 宿曜道", "🈳 Sukkayodo"),
        ],
    },
    "thailand": {
        "zh": "泰國",
        "en": "Thailand",
        "color": "#00b894",
        "systems": [
            ("tab_thai", "🐘 泰國占星", "🐘 Thai Astrology"),
        ],
    },
    "myanmar": {
        "zh": "緬甸",
        "en": "Myanmar",
        "color": "#6c5ce7",
        "systems": [
            ("tab_mahabote", "🇲🇲 緬甸占星", "🇲🇲 Myanmar (Mahabote)"),
        ],
    },
    "mongolia": {
        "zh": "蒙古",
        "en": "Mongolia",
        "color": "#0984e3",
        "systems": [
            ("tab_zurkhai", "🇲🇳 蒙古祖爾海", "🇲🇳 Mongolian Zurkhai"),
        ],
    },
    "europe": {
        "zh": "歐洲",
        "en": "Europe",
        "color": "#2ecc71",
        "systems": [
            ("tab_western", "🌍 西洋占星", "🌍 Western Astrology"),
            ("tab_hellenistic", "🏛️ 希臘占星", "🏛️ Hellenistic"),
        ],
    },
    "middleeast": {
        "zh": "中東",
        "en": "Middle East",
        "color": "#d35400",
        "systems": [
            ("tab_arabic", "☪ 阿拉伯占星", "☪ Arabic Astrology"),
            ("tab_kabbalistic", "✡ 卡巴拉占星", "✡ Kabbalistic"),
        ],
    },
    "mesoamerica": {
        "zh": "中美洲",
        "en": "Mesoamerica",
        "color": "#8e44ad",
        "systems": [
            ("tab_maya", "🏺 瑪雅占星", "🏺 Maya Astrology"),
            ("tab_aztec", "🦅 阿茲特克占星", "🦅 Aztec Astrology"),
        ],
    },
    "egypt": {
        "zh": "古埃及",
        "en": "Ancient Egypt",
        "color": "#f1c40f",
        "systems": [
            ("tab_decans", "🏛️ 古埃及十度區間", "🏛️ Egyptian Decans"),
        ],
    },
}


def _build_map_html(lang: str) -> str:
    """Return a self-contained HTML/SVG/JS snippet for the interactive map."""

    # Build the JavaScript region data from REGIONS
    js_regions = []
    for rid, info in REGIONS.items():
        label = info["zh"] if lang == "zh" else info["en"]
        btns = []
        for sys_key, zh, en in info["systems"]:
            btn_label = zh if lang == "zh" else en
            btns.append(f'{{"key":"{sys_key}","label":"{btn_label}"}}')
        js_regions.append(
            f'"{rid}":{{"label":"{label}","color":"{info["color"]}",'
            f'"systems":[{",".join(btns)}]}}'
        )
    js_data = "{" + ",".join(js_regions) + "}"

    # Simplified SVG world map paths — recognisable continent outlines
    # Each path has a data-region attribute linking it to the REGIONS dict
    svg_paths = """
    <!-- East Asia: China -->
    <path data-region="china" d="M640,160 L680,140 L720,145 L740,155 L760,170 L755,190 L740,210 L720,225 L700,230 L680,225 L660,235 L640,230 L625,215 L620,195 L625,175 Z" />

    <!-- South Asia: India -->
    <path data-region="india" d="M620,230 L640,235 L650,250 L655,270 L650,290 L640,305 L625,315 L610,305 L605,285 L610,265 L615,245 Z" />

    <!-- Japan -->
    <path data-region="japan" d="M770,160 L775,150 L780,155 L785,170 L780,185 L775,195 L770,190 L768,175 Z" />

    <!-- Southeast Asia: Thailand -->
    <path data-region="thailand" d="M680,250 L695,245 L700,255 L698,270 L690,280 L680,275 L675,265 Z" />

    <!-- Myanmar -->
    <path data-region="myanmar" d="M660,240 L675,235 L680,250 L675,265 L665,270 L655,260 L655,248 Z" />

    <!-- Mongolia -->
    <path data-region="mongolia" d="M660,130 L700,120 L740,125 L750,140 L735,150 L700,148 L670,145 Z" />

    <!-- Europe -->
    <path data-region="europe" d="M440,100 L480,90 L520,95 L540,105 L560,120 L570,140 L560,160 L540,170 L510,175 L480,170 L460,160 L440,150 L430,130 Z" />

    <!-- Middle East -->
    <path data-region="middleeast" d="M540,180 L570,170 L600,180 L620,195 L615,215 L600,230 L580,235 L560,225 L545,210 L540,195 Z" />

    <!-- Mesoamerica -->
    <path data-region="mesoamerica" d="M200,230 L230,225 L250,235 L260,250 L250,265 L235,275 L215,270 L200,255 L195,240 Z" />

    <!-- Egypt (North Africa) -->
    <path data-region="egypt" d="M490,195 L520,185 L540,195 L545,210 L535,225 L515,230 L495,225 L485,210 Z" />

    <!-- Background continents (non-interactive) -->
    <!-- North America -->
    <path class="bg-land" d="M80,60 L160,40 L240,50 L280,80 L290,120 L280,160 L260,190 L230,210 L200,220 L160,210 L120,180 L90,140 L75,100 Z" />
    <!-- South America -->
    <path class="bg-land" d="M220,280 L260,270 L290,290 L310,330 L300,370 L280,400 L250,410 L230,395 L215,360 L210,320 Z" />
    <!-- Africa (sub-Saharan) -->
    <path class="bg-land" d="M470,240 L510,235 L540,250 L560,280 L555,320 L540,355 L515,370 L490,360 L475,330 L465,295 L460,265 Z" />
    <!-- Australia -->
    <path class="bg-land" d="M720,340 L760,330 L790,340 L800,360 L790,380 L760,390 L730,380 L715,360 Z" />
    <!-- Russia / North Asia filler -->
    <path class="bg-land" d="M560,60 L620,50 L700,55 L760,65 L790,80 L800,100 L790,120 L760,130 L700,125 L640,130 L580,125 L560,110 L555,85 Z" />
    """

    html = f"""
<div id="kinastro-map-container" style="position:relative;width:100%;max-width:900px;margin:0 auto;">
  <svg viewBox="0 0 900 440" xmlns="http://www.w3.org/2000/svg"
       style="width:100%;height:auto;font-family:sans-serif;">
    <defs>
      <filter id="glow">
        <feGaussianBlur stdDeviation="3" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>
    <!-- Ocean background -->
    <rect width="900" height="440" rx="12" fill="#1a2332"/>
    {svg_paths}
  </svg>

  <!-- Tooltip popup -->
  <div id="km-tooltip" style="
    display:none;position:absolute;
    background:rgba(30,30,50,0.96);color:#fff;
    border-radius:10px;padding:14px 18px;
    box-shadow:0 4px 24px rgba(0,0,0,0.4);
    z-index:1000;pointer-events:auto;
    min-width:160px;text-align:center;
    font-size:14px;transition:opacity 0.15s;
  ">
    <div id="km-tooltip-title" style="font-weight:bold;font-size:16px;margin-bottom:8px;"></div>
    <div id="km-tooltip-buttons"></div>
  </div>
</div>

<style>
  #kinastro-map-container svg path[data-region] {{
    fill: #2c3e50;
    stroke: #4a6785;
    stroke-width: 1.2;
    cursor: pointer;
    transition: fill 0.25s, filter 0.25s, transform 0.15s;
    transform-origin: center;
  }}
  #kinastro-map-container svg path[data-region]:hover {{
    filter: url(#glow);
    stroke-width: 2;
  }}
  #kinastro-map-container svg path.bg-land {{
    fill: #233040;
    stroke: #3a5060;
    stroke-width: 0.8;
    pointer-events: none;
  }}
  #km-tooltip button {{
    display:block;width:100%;
    margin:5px 0;padding:8px 12px;
    border:none;border-radius:6px;
    background:#3498db;color:#fff;
    font-size:14px;cursor:pointer;
    transition:background 0.2s;
  }}
  #km-tooltip button:hover {{
    background:#2980b9;
  }}
</style>

<script>
(function() {{
  const REGIONS = {js_data};
  const container = document.getElementById('kinastro-map-container');
  const tooltip = document.getElementById('km-tooltip');
  const tooltipTitle = document.getElementById('km-tooltip-title');
  const tooltipButtons = document.getElementById('km-tooltip-buttons');
  let activeRegion = null;
  let hideTimer = null;

  function showTooltip(regionEl, rid) {{
    if (hideTimer) {{ clearTimeout(hideTimer); hideTimer = null; }}
    const info = REGIONS[rid];
    if (!info) return;

    // Highlight region
    if (activeRegion && activeRegion !== regionEl) {{
      activeRegion.style.fill = '#2c3e50';
    }}
    activeRegion = regionEl;
    regionEl.style.fill = info.color;

    // Position tooltip near the region
    const svgRect = container.querySelector('svg').getBoundingClientRect();
    const pathRect = regionEl.getBoundingClientRect();
    const cx = pathRect.left + pathRect.width / 2 - svgRect.left;
    const cy = pathRect.top - svgRect.top;

    // Build tooltip content (informational labels only; actual navigation
    // is handled by the Streamlit button grid below the map)
    tooltipTitle.textContent = info.label;
    tooltipButtons.innerHTML = '';
    info.systems.forEach(function(sys) {{
      const lbl = document.createElement('div');
      lbl.textContent = sys.label;
      lbl.style.cssText = 'padding:4px 8px;margin:3px 0;background:#3498db22;border-radius:4px;font-size:14px;';
      tooltipButtons.appendChild(lbl);
    }});

    // Show tooltip
    tooltip.style.display = 'block';
    let left = cx - tooltip.offsetWidth / 2;
    let top = cy - tooltip.offsetHeight - 10;
    if (top < 0) top = cy + pathRect.height + 10;
    if (left < 0) left = 5;
    const containerWidth = container.offsetWidth;
    if (left + tooltip.offsetWidth > containerWidth) {{
      left = containerWidth - tooltip.offsetWidth - 5;
    }}
    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
  }}

  function scheduleHide() {{
    hideTimer = setTimeout(function() {{
      tooltip.style.display = 'none';
      if (activeRegion) {{
        activeRegion.style.fill = '#2c3e50';
        activeRegion = null;
      }}
    }}, 400);
  }}

  // Attach events to region paths
  container.querySelectorAll('path[data-region]').forEach(function(el) {{
    el.addEventListener('mouseenter', function() {{
      showTooltip(el, el.getAttribute('data-region'));
    }});
    el.addEventListener('mouseleave', scheduleHide);
    el.addEventListener('click', function() {{
      showTooltip(el, el.getAttribute('data-region'));
    }});
  }});

  // Keep tooltip visible when hovering over it
  tooltip.addEventListener('mouseenter', function() {{
    if (hideTimer) {{ clearTimeout(hideTimer); hideTimer = null; }}
  }});
  tooltip.addEventListener('mouseleave', scheduleHide);

  // Close tooltip on click outside
  document.addEventListener('click', function(e) {{
    if (!tooltip.contains(e.target) && !e.target.hasAttribute('data-region')) {{
      tooltip.style.display = 'none';
      if (activeRegion) {{
        activeRegion.style.fill = '#2c3e50';
        activeRegion = null;
      }}
    }}
  }});
}})();
</script>
"""
    return html


def render_world_map() -> None:
    """Render the interactive world map and handle system selection.

    The map uses ``st.components.v1.html`` for the SVG visualisation and
    ``st.button`` widgets below the map for reliable Streamlit integration.
    Button clicks set ``st.session_state["_selected_system"]`` and trigger
    a rerun.
    """
    lang = get_lang()

    # Render the SVG map
    map_html = _build_map_html(lang)
    st.components.v1.html(map_html, height=500, scrolling=False)

    # --- Fallback / always-visible button grid below the map ---
    st.markdown("---")
    # Group by region
    cols_per_row = 3
    region_items = list(REGIONS.items())
    for row_start in range(0, len(region_items), cols_per_row):
        row_regions = region_items[row_start : row_start + cols_per_row]
        cols = st.columns(len(row_regions))
        for col, (rid, info) in zip(cols, row_regions):
            region_label = info["zh"] if lang == "zh" else info["en"]
            with col:
                st.markdown(
                    f'<div style="background:{info["color"]}20;border:2px solid {info["color"]}; '
                    f'border-radius:10px;padding:10px;margin-bottom:8px;text-align:center;">'
                    f'<b style="color:{info["color"]};font-size:15px;">{region_label}</b></div>',
                    unsafe_allow_html=True,
                )
                for sys_key, zh, en in info["systems"]:
                    btn_label = zh if lang == "zh" else en
                    if st.button(btn_label, key=f"map_{sys_key}", width='stretch'):
                        st.session_state["_selected_system"] = sys_key
                        st.rerun()
