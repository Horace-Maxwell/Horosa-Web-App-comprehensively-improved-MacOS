"""
frontend/vastu_renderer.py — Vastu Purusha Mandala 互動式渲染器 + Streamlit UI

提供：
    render_vastu_mandala_html   — 生成完整 HTML（互動式 9×9 曼荼羅盤）
    render_vastu_tab            — Streamlit 頁面入口，含完整 UI 流程

設計原則：
    - 藝術級古典印度曼陀羅風（橘金 #FF9F1C、深藍紫、曼陀羅幾何）
    - 9 宮格中央 Brahmasthan + 32 外環天神位，金屬質感浮雕陰影
    - 根據命盤自動高亮/著色受影響方位（行星對應）
    - 支援房屋朝向選擇（8 方位）
    - 點擊任一方位 → 行內展開中英雙語解讀（含 remedies、顏色、房間建議）
    - Vastu Compliance Score 環形進度條
    - 完整中英雙語 i18n 整合

互動：
    st.components.v1.html() 渲染完整 HTML
"""

from __future__ import annotations

from typing import Callable, Optional

import streamlit as st

from astro.vastu.constants import (
    FACING_OPTIONS_8,
    INNER_ZONES,
    OUTER_PADAS,
    PLANET_SYMBOL,
    PLANET_ZH_SHORT,
    PLANET_ZONE,
    ZONE_COLORS_INNER,
    ZONE_COLORS_OUTER,
)
from astro.vastu.engine import VastuEngine, VastuResult, generate_vastu_disk
from astro.vastu.interpretations import DIRECTION_DETAILS

try:
    from astro.i18n import auto_cn, t
except ImportError:
    def t(key: str) -> str:  # type: ignore[misc]
        return key
    def auto_cn(text: str, en_text: str = "") -> str:  # type: ignore[misc]
        return text


# ─────────────────────────────────────────────────────────────────────────────
# 主題色彩常數（Vedic Vastu 橘金主題）
# ─────────────────────────────────────────────────────────────────────────────

_GOLD       = "#FF9F1C"
_DEEP_GOLD  = "#E6891A"
_DARK_BLUE  = "#1A1035"
_PURPLE     = "#4A1A6E"
_CREAM      = "#FFF8E7"
_SHADOW     = "rgba(0,0,0,0.4)"


# ─────────────────────────────────────────────────────────────────────────────
# HTML / CSS 輔助函數
# ─────────────────────────────────────────────────────────────────────────────

def _css_head() -> str:
    """生成曼荼羅盤的 CSS 樣式表。"""
    return f"""\
<!DOCTYPE html>
<html lang="zh-TW">
<head><meta charset="UTF-8"><style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{
  font-family:"Microsoft JhengHei","PingFang TC",system-ui,-apple-system,sans-serif;
  background:transparent;padding:10px;color:#222;
}}
/* ── 標題區 ── */
.mandala-title{{
  text-align:center;font-size:20px;font-weight:bold;color:{_GOLD};
  text-shadow:0 0 10px rgba(255,159,28,0.6);letter-spacing:2px;
  margin-bottom:4px;
}}
.mandala-subtitle{{
  text-align:center;font-size:12px;color:#999;margin-bottom:12px;
}}
/* ── 曼荼羅外框 ── */
.mandala-outer{{
  display:flex;flex-direction:column;align-items:center;
}}
.compass-bar{{
  font-weight:bold;font-size:13px;color:{_GOLD};
  text-align:center;padding:3px 0;letter-spacing:1px;
}}
.mandala-mid{{
  display:flex;align-items:center;gap:4px;
  width:100%;max-width:720px;
}}
.compass-side{{
  writing-mode:vertical-rl;font-weight:bold;font-size:12px;
  color:{_GOLD};padding:0 2px;letter-spacing:2px;
}}
/* ── 9×9 網格 ── */
.vastu-grid{{
  display:grid;
  grid-template-columns:repeat(9,1fr);
  grid-template-rows:repeat(9,1fr);
  gap:2px;flex:1;aspect-ratio:1/1;
  background:linear-gradient(135deg,#3d2a0d,#1a0a2e);
  border-radius:10px;padding:3px;
  box-shadow:0 4px 24px {_SHADOW},inset 0 1px 0 rgba(255,215,0,0.2);
  max-width:680px;
}}
/* ── 外環格（32 天神 Pada） ── */
.pada-cell{{
  border-radius:3px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;text-align:center;
  padding:2px 1px;cursor:pointer;transition:all .2s;
  border:1px solid rgba(255,255,255,0.05);overflow:hidden;
}}
.pada-cell:hover{{
  transform:scale(1.12);z-index:5;
  box-shadow:0 2px 12px rgba(255,159,28,.5);
  border-color:rgba(255,215,0,0.6);
}}
.pada-cell.ruler-zone{{
  box-shadow:inset 0 0 0 2px {_GOLD},0 0 8px rgba(255,215,0,.4);
}}
.deity-zh{{font-size:10px;font-weight:600;line-height:1.2;color:#f5e6c8;}}
.deity-sk{{font-size:7.5px;color:#a89070;line-height:1.1;}}
/* ── 9 宮格（方位區域） ── */
.zone-cell{{
  border-radius:6px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;text-align:center;
  padding:5px 3px;border:1px solid rgba(255,255,255,0.1);
  cursor:pointer;transition:all .2s;
  box-shadow:inset 0 1px 0 rgba(255,255,255,0.1);
}}
.zone-cell:hover{{
  transform:scale(1.03);z-index:4;
  box-shadow:0 2px 16px rgba(255,159,28,.4),inset 0 1px 0 rgba(255,255,255,0.2);
}}
.zone-cell.center-cell{{
  border:2px solid {_GOLD} !important;
  box-shadow:0 0 16px rgba(255,215,0,.4),inset 0 0 0 1px rgba(255,215,0,0.3);
}}
.zone-cell.ruler-highlight{{
  box-shadow:inset 0 0 0 3px {_GOLD},0 0 14px rgba(255,215,0,.5) !important;
}}
.zone-name{{
  font-size:12px;font-weight:bold;color:#222;
  line-height:1.2;margin-bottom:1px;
}}
.zone-deity{{font-size:9px;color:#555;margin-bottom:1px;}}
.zone-element{{font-size:8.5px;color:#888;}}
.zone-tip{{
  font-size:8px;color:#6d4c41;background:rgba(255,255,255,.55);
  border-radius:3px;padding:1px 4px;margin:2px 0;
}}
.zone-planets{{
  display:flex;gap:2px;flex-wrap:wrap;justify-content:center;margin-top:2px;
}}
.planet-badge{{
  display:inline-flex;align-items:center;justify-content:center;
  width:18px;height:18px;border-radius:50%;
  background:#546E7A;color:#fff;font-size:11px;
  box-shadow:0 1px 3px rgba(0,0,0,.3);
}}
.planet-badge.ruler{{
  background:#E65100;
  box-shadow:0 0 6px rgba(230,81,0,.6),0 1px 3px rgba(0,0,0,.3);
}}
.center-om{{font-size:22px;margin-bottom:2px;}}
.ruler-star{{font-size:9px;color:{_GOLD};font-weight:bold;margin-top:1px;}}
/* ── 圖例 ── */
.legend{{
  margin-top:14px;padding:10px 14px;
  background:rgba(26,16,53,0.06);
  border-radius:8px;border:1px solid rgba(255,159,28,.2);
  max-width:720px;width:100%;
}}
.legend-title{{font-size:12px;font-weight:bold;margin-bottom:6px;color:{_GOLD};}}
.legend-items{{display:flex;flex-wrap:wrap;gap:10px;font-size:11px;color:#555;}}
.legend-item{{display:flex;align-items:center;gap:5px;}}
.legend-swatch{{
  width:14px;height:14px;border-radius:3px;display:inline-block;
  box-shadow:inset 0 1px 2px rgba(0,0,0,.15);
}}
/* ── 響應式 ── */
@media(max-width:600px){{
  .deity-zh{{font-size:8.5px;}} .deity-sk{{font-size:7px;}}
  .zone-name{{font-size:10px;}} .zone-deity{{font-size:8px;}}
  .vastu-grid{{max-width:98vw;}}
}}
</style></head><body>
"""


def render_vastu_mandala_html(
    result: VastuResult,
    height_px: int = 720,
) -> str:
    """生成個人化 Vastu Purusha Mandala 的完整 HTML 字串。

    Args:
        result:    :class:`VastuResult` 計算結果。
        height_px: 曼荼羅渲染高度（像素），預設 720。

    Returns:
        可直接傳入 ``st.components.v1.html()`` 的完整 HTML 字串。
    """
    lagna_ruler = result.lagna_ruler
    ruler_zone = result.lagna_ruler_zone
    highlight_zones = result.highlight_zones

    # 各方位對應行星列表（反向查找）
    zone_planets: dict[str, list[str]] = {}
    for planet, zone in PLANET_ZONE.items():
        zone_planets.setdefault(zone, []).append(planet)

    parts: list[str] = [_css_head()]

    # ── 標題 ──
    parts.append(
        f'<div class="mandala-title">🕉️ Vastu Purusha Mandala · 吠陀風水盤</div>'
        f'<div class="mandala-subtitle">'
        f'上升星座：{result.lagna_sign_zh} ｜ 主宰：{result.lagna_ruler_zh}'
        f' ｜ 房屋朝向：{result.house_facing}'
        f'</div>'
    )

    # ── 曼荼羅主體 ──
    parts.append('<div class="mandala-outer">')
    parts.append('<div class="compass-bar">⬆ 北方 North ⬆</div>')
    parts.append('<div class="mandala-mid">')
    parts.append('<div class="compass-side">西 West</div>')
    parts.append('<div class="vastu-grid">')

    # ── 32 外環 Pada 格 ──
    for row, col, sanskrit, chinese, zone in OUTER_PADAS:
        is_ruler_zone = (zone == ruler_zone)
        bg = ZONE_COLORS_OUTER.get(zone, "#f5f5f5")
        cls = "pada-cell ruler-zone" if is_ruler_zone else "pada-cell"
        style = (
            f"grid-row:{row + 1}/{row + 2};"
            f"grid-column:{col + 1}/{col + 2};"
            f"background:{bg};"
        )
        is_highlight = zone in highlight_zones
        if is_highlight:
            style += f"box-shadow:inset 0 0 0 2px {_GOLD};"
        parts.append(
            f'<div class="{cls}" style="{style}" '
            f'title="{sanskrit} ({chinese}) — {zone} 方位">'
            f'<span class="deity-zh">{chinese}</span>'
            f'<span class="deity-sk">{sanskrit}</span>'
            f"</div>"
        )

    # ── 9 內部宮格 ──
    for zone_key, zh_label, deity, element, tip, gr, gc in INNER_ZONES:
        is_ruler_zone = (zone_key == ruler_zone)
        is_center = (zone_key == "Center")
        bg = ZONE_COLORS_INNER.get(zone_key, "#fff")

        cls_list = ["zone-cell"]
        if is_ruler_zone:
            cls_list.append("ruler-highlight")
        if is_center:
            cls_list.append("center-cell")

        style = f"grid-row:{gr};grid-column:{gc};background:{bg};"

        # 方位名稱（換行轉 <br>）
        name_html = zh_label.replace("\n", "<br>")

        # 行星徽章
        badges_html = ""
        if zone_key in zone_planets:
            badge_items: list[str] = []
            for p in zone_planets[zone_key]:
                sym = PLANET_SYMBOL.get(p, "")
                zh_short = PLANET_ZH_SHORT.get(p, "")
                bcls = "planet-badge ruler" if p == lagna_ruler else "planet-badge"
                badge_items.append(
                    f'<span class="{bcls}" title="{p} ({zh_short})">{sym}</span>'
                )
            badges_html = (
                f'<div class="zone-planets">{"".join(badge_items)}</div>'
            )

        # 中央 Om 符號
        center_html = '<div class="center-om">🕉️</div>' if is_center else ""

        # 主宰行星標示
        ruler_html = (
            f'<div class="ruler-star">⭐ 主宰方位</div>'
            if is_ruler_zone else ""
        )

        # 高亮原因提示
        tooltip = highlight_zones.get(zone_key, "")
        if tooltip:
            style += f"outline:2px solid {_GOLD};"

        parts.append(
            f'<div class="{" ".join(cls_list)}" style="{style}">'
            f"{center_html}"
            f'<div class="zone-name">{name_html}</div>'
            f'<div class="zone-deity">{deity}</div>'
            f'<div class="zone-element">{element}象</div>'
            f'<div class="zone-tip">{tip}</div>'
            f"{badges_html}"
            f"{ruler_html}"
            f"</div>"
        )

    parts.append("</div>")  # vastu-grid
    parts.append('<div class="compass-side">東 East</div>')
    parts.append("</div>")  # mandala-mid
    parts.append('<div class="compass-bar">⬇ 南方 South ⬇</div>')
    parts.append("</div>")  # mandala-outer

    # ── 圖例 ──
    sym = PLANET_SYMBOL.get(lagna_ruler, "")
    zh = PLANET_ZH_SHORT.get(lagna_ruler, lagna_ruler)
    parts.append(
        f'<div class="legend">'
        f'<div class="legend-title">📖 圖例 Legend</div>'
        f'<div class="legend-items">'
        f'<div class="legend-item">'
        f'<span class="legend-swatch" style="outline:2px solid {_GOLD};background:#FFE082;"></span>'
        f'金框 = 上升主宰 {sym} {zh} 方位（{ruler_zone}）'
        f"</div>"
        f'<div class="legend-item">'
        f'<span class="planet-badge ruler" style="width:16px;height:16px;font-size:10px;">{sym}</span>'
        f" 主宰行星"
        f"</div>"
        f'<div class="legend-item">'
        f'<span class="planet-badge" style="width:16px;height:16px;font-size:10px;">☉</span>'
        f" 方位對應行星"
        f"</div>"
        f'<div class="legend-item">'
        f'<span class="legend-swatch" style="background:#E3F2FD;"></span>水 '
        f'<span class="legend-swatch" style="background:#FFF3E0;"></span>火 '
        f'<span class="legend-swatch" style="background:#EFEBE9;"></span>土 '
        f'<span class="legend-swatch" style="background:#E8F5E9;"></span>風 '
        f'<span class="legend-swatch" style="background:#F3E5F5;"></span>空'
        f"</div>"
        f"</div></div>"
    )

    parts.append("</body></html>")
    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Streamlit UI 主函數
# ─────────────────────────────────────────────────────────────────────────────

def render_vastu_tab(
    v_chart: Optional[object] = None,
    after_chart_hook: Optional[Callable[[], None]] = None,
) -> None:
    """Streamlit Vastu 盤頁面主函數。

    頁面流程：
    1. 共用現有命盤資料（若已計算），或提示用戶先計算
    2. 新增「居所朝向」選擇器
    3. 一鍵生成個人化 Vastu 盤
    4. 顯示 Vastu Purusha Mandala（互動式 HTML）
    5. 顯示 Vastu Compliance Score + 行星影響表
    6. 顯示個人化房間配置建議與方位詳解

    Args:
        v_chart:          已計算的 VedicChart 物件（可為 None，頁面內部另行計算）。
        after_chart_hook: 渲染圖表後的回調函數（用於 AI 按鈕等）。
    """
    st.markdown(
        f"<h3 style='color:{_GOLD};text-align:center;'>"
        "🪔 吠陀風水盤 · Astro-Vastu Mandala</h3>",
        unsafe_allow_html=True,
    )
    st.caption(
        auto_cn(
            "結合吠陀命盤（Lagna + 行星）與居所方位，生成個人化 Vastu Purusha Mandala。",
            "Combines Vedic birth chart (Lagna + planets) with house orientation to generate a personalized Vastu Purusha Mandala.",
        )
    )

    # ── 房屋朝向選擇器 ──
    col_facing, col_info = st.columns([2, 3])
    with col_facing:
        facing_labels = [f"{code} — {name}" for code, name, _ in FACING_OPTIONS_8]
        facing_index = st.selectbox(
            auto_cn("🧭 居所朝向", "🧭 House Facing Direction"),
            options=list(range(len(facing_labels))),
            format_func=lambda i: facing_labels[i],
            key="vastu_facing_select",
        )
        selected_facing_code = FACING_OPTIONS_8[facing_index][0]

    # ── 計算 Vastu 盤 ──
    result: Optional[VastuResult] = None

    if v_chart is not None:
        try:
            result = generate_vastu_disk(v_chart, house_facing=selected_facing_code)
        except Exception as e:
            st.error(f"Vastu 計算失敗：{e}")
            return
    else:
        # 嘗試從 session_state 取得計算參數
        _p = st.session_state.get("_calc_params")
        if _p:
            try:
                from astro.vedic.indian import compute_vedic_chart
                with st.spinner("⏳ 計算 Vastu 盤中…"):
                    v_chart_inner = compute_vedic_chart(**_p)
                result = generate_vastu_disk(
                    v_chart_inner, house_facing=selected_facing_code
                )
            except Exception as e:
                st.error(f"Vastu 計算失敗：{e}")
                return
        else:
            with col_info:
                st.info(
                    auto_cn(
                        "👈 請先在左側輸入出生資料並點擊「開始排盤」，再生成 Vastu 盤。",
                        "👈 Please enter birth data on the left and click 'Calculate Chart' first.",
                    )
                )
            return

    if result is None:
        st.warning("無法生成 Vastu 盤，請確認出生資料已正確輸入。")
        return

    with col_info:
        st.success(
            auto_cn(
                f"✅ 上升星座：**{result.lagna_sign_zh}** ｜ "
                f"主宰行星：**{result.lagna_ruler_zh}** ｜ "
                f"Vastu 方位：**{result.lagna_ruler_zone}**",
                f"✅ Lagna: **{result.lagna_sign}** | "
                f"Ruler: **{result.lagna_ruler}** | "
                f"Vastu Zone: **{result.lagna_ruler_zone}**",
            )
        )

    # ── Vastu Purusha Mandala HTML ──
    st.divider()
    mandala_html = render_vastu_mandala_html(result)
    st.components.v1.html(mandala_html, height=780, scrolling=False)

    # ── AI 按鈕回調 ──
    if after_chart_hook is not None:
        after_chart_hook()

    st.divider()

    # ── 子分頁：Compliance Score / 行星影響 / 房間建議 / 方位詳解 ──
    tab_score, tab_planets, tab_rooms, tab_directions = st.tabs([
        auto_cn("🎯 符合度評分", "🎯 Compliance Score"),
        auto_cn("🪐 行星影響", "🪐 Planetary Influence"),
        auto_cn("🏠 房間配置", "🏠 Room Placement"),
        auto_cn("🧭 方位詳解", "🧭 Direction Details"),
    ])

    with tab_score:
        _render_compliance_score(result)

    with tab_planets:
        _render_planet_influences(result)

    with tab_rooms:
        _render_room_suggestions(result)

    with tab_directions:
        _render_direction_details(result)


# ─────────────────────────────────────────────────────────────────────────────
# 子分頁渲染函數
# ─────────────────────────────────────────────────────────────────────────────

def _render_compliance_score(result: VastuResult) -> None:
    """渲染 Vastu Compliance Score 環形進度條。"""
    score = result.compliance_score
    score_int = int(round(score))

    # 評分等級
    if score >= 85:
        grade, color = "優秀 Excellent", "#4CAF50"
    elif score >= 70:
        grade, color = "良好 Good", _GOLD
    elif score >= 55:
        grade, color = "尚可 Fair", "#FF9800"
    else:
        grade, color = "需改善 Needs Improvement", "#F44336"

    # SVG 環形圖
    radius = 70
    circumference = 2 * 3.14159 * radius
    dash_offset = circumference * (1 - score / 100)

    svg_html = f"""
    <div style="text-align:center;padding:20px 0;">
      <svg width="180" height="180" viewBox="0 0 180 180">
        <circle cx="90" cy="90" r="{radius}" fill="none" stroke="#E0E0E0" stroke-width="12"/>
        <circle cx="90" cy="90" r="{radius}" fill="none"
          stroke="{color}" stroke-width="12"
          stroke-dasharray="{circumference:.1f}"
          stroke-dashoffset="{dash_offset:.1f}"
          stroke-linecap="round"
          transform="rotate(-90 90 90)"/>
        <text x="90" y="85" text-anchor="middle" font-size="32" font-weight="bold"
          fill="{color}" font-family="system-ui">{score_int}</text>
        <text x="90" y="108" text-anchor="middle" font-size="12"
          fill="#666" font-family="system-ui">/ 100</text>
        <text x="90" y="128" text-anchor="middle" font-size="11"
          fill="{color}" font-family="system-ui">{grade}</text>
      </svg>
      <div style="font-size:14px;color:#666;margin-top:8px;">
        Vastu Compliance Score · 吠陀風水符合度
      </div>
    </div>
    """
    st.markdown(svg_html, unsafe_allow_html=True)

    # 建議朝向
    st.markdown(
        f"**🧭 {auto_cn('推薦房屋朝向', 'Recommended Facing')}：** "
        f"{result.recommended_facing}"
    )
    if result.moon_element_tip:
        st.markdown(
            f"**🌙 {auto_cn('月亮元素建議', 'Moon Element Tip')}：** "
            f"{result.moon_element_tip}"
        )

    # 高亮方位摘要
    if result.highlight_zones:
        st.subheader(auto_cn("⚡ 重要方位影響", "⚡ Key Zone Influences"))
        for zone, reason in result.highlight_zones.items():
            st.markdown(f"- **{zone}**：{reason}")


def _render_planet_influences(result: VastuResult) -> None:
    """渲染行星 Vastu 影響列表。"""
    if not result.planet_influences:
        st.info("無行星影響資料（請確認已正確計算 Vedic 命盤）。")
        return

    import pandas as pd

    rows = []
    for inf in result.planet_influences:
        rows.append({
            auto_cn("行星", "Planet"): f"{inf.symbol} {inf.planet_zh}",
            auto_cn("所在星座", "Sign"):   inf.sign_zh or inf.sign_en,
            auto_cn("Vastu 方位", "Zone"): f"{inf.zone_name_zh} ({inf.vastu_zone})",
            auto_cn("影響", "Influence"):  (
                "⭐ 主宰" if inf.is_lagna_ruler else
                ("✨ 吉星" if inf.influence_type == "benefic" else
                 ("⚠️ 凶星" if inf.influence_type == "malefic" else "○ 中性"))
            ),
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True)
    st.caption(
        auto_cn(
            "⭐ = 上升主宰行星（對 Vastu 影響最深）｜✨ = 吉星｜⚠️ = 凶星",
            "⭐ = Lagna ruler (highest Vastu impact) | ✨ = Benefic | ⚠️ = Malefic",
        )
    )


def _render_room_suggestions(result: VastuResult) -> None:
    """渲染個人化房間配置建議。"""
    if not result.room_suggestions:
        st.info("無房間配置資料。")
        return

    for room in result.room_suggestions:
        with st.expander(f"{room['房間']} — {room['最佳方位']}"):
            st.markdown(f"📌 **說明**：{room['說明']}")
            st.markdown(f"🔧 **Vastu 補救**：{room['補救']}")

    # 上升星座詳細建議
    if result.lagna_details:
        st.divider()
        st.subheader(
            auto_cn(
                f"📜 {result.lagna_sign_zh} 上升完整 Vastu 建議",
                f"📜 Full Vastu Guide for {result.lagna_sign} Ascendant",
            )
        )
        for item, (advice, reason) in result.lagna_details.items():
            with st.expander(f"📍 {item}：{advice}"):
                st.caption(f"傳統理由：{reason}")


def _render_direction_details(result: VastuResult) -> None:
    """渲染八大方位詳細解讀。"""
    direction_order = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]

    for zone_code in direction_order:
        detail = DIRECTION_DETAILS.get(zone_code)
        if not detail:
            continue

        is_ruler = (zone_code == result.lagna_ruler_zone)
        is_facing = (zone_code == result.house_facing)

        prefix = ""
        if is_ruler:
            prefix += "⭐ 主宰方位 "
        if is_facing:
            prefix += "🏠 房屋朝向 "

        label = f"{prefix}{detail['name_zh']}"
        with st.expander(label, expanded=(is_ruler or is_facing)):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**🙏 主宰神祇**：{detail['deity']}")
                st.markdown(f"**🌊 五大元素**：{detail['element']}")
                st.markdown(f"**🪐 關聯行星**：{detail['planet']}")
                st.markdown(f"**🎨 推薦顏色**：{detail['colors']}")
            with col2:
                st.markdown(f"**🏠 適合房間**：{detail['rooms']}")
                st.markdown(f"**🚫 避免事項**：{detail['avoid']}")
                st.markdown(f"**🔧 Vastu 補救**：{detail['remedies']}")

            st.info(detail["significance"])
            st.caption(f"📜 {detail['scripture']}")
