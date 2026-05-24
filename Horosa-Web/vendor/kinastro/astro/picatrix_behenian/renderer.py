"""
astro/picatrix_behenian/renderer.py — Streamlit UI for Picatrix + Behenian Stars

Provides the main ``render_streamlit`` function which renders a multi-tab
Streamlit page with:
  1. 星盤激活 (Chart Activations) — detect conjunctions with natal/transit chart
  2. 護符製作 (Talisman Making)   — recommendations per activated star
  3. 擇日器  (Electional Finder) — scan for future Moon–star windows
  4. 今日魔法 (Today's Magic)     — quick query for current sky activations
  5. 星典瀏覽 (Star Compendium)   — full browse of all 15 Behenian stars

Visual style: dark celestial gold palette inspired by medieval manuscript
illuminations (consistent with the Arabic / Picatrix mansion module palette).
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Optional

import streamlit as st

from .constants import (
    BEHENIAN_STARS,
    BEHENIAN_BY_NAME,
    BEHENIAN_ORB,
    MAGIC_CATEGORIES,
    MAGIC_CATEGORIES_CN,
    RULER_CN,
    RULER_COLORS,
    BehenianStar,
)
from .calculator import (
    BehenianActivation,
    TodayMagicResult,
    ElectionalWindow,
    detect_activations,
    compute_today_magic,
    find_electional_windows,
    activations_from_chart,
)

# ── try to import i18n helpers; fall back gracefully ────────────────────────
try:
    from astro.i18n import auto_cn, get_ui_lang
except ImportError:
    def auto_cn(t: str) -> str:  # type: ignore[misc]
        return t

    def get_ui_lang() -> str:  # type: ignore[misc]
        return "zh"


# ============================================================
# Colour Palette — Medieval Manuscript / Celestial Gold
# ============================================================

_C_BG       = "#1a1228"   # deep violet-black background
_C_CARD     = "#231a36"   # card background
_C_BORDER   = "#c9a227"   # gold border
_C_HEADER   = "#f5d060"   # bright gold header text
_C_TEXT     = "#e8d5a3"   # warm cream text
_C_SUBTLE   = "#9a7c3e"   # muted gold secondary text
_C_ACCENT   = "#d4a017"   # accent gold
_C_GOOD     = "#5ba553"   # green for benefic
_C_WARN     = "#c0392b"   # red for malefic
_C_NEUTRAL  = "#7b6fa0"   # purple-grey neutral
_C_STRONG   = "#ff9f43"   # orange for strong activations
_C_MOON     = "#a8c6e8"   # moon blue

# Nature colour map
_NATURE_COLORS: dict[str, str] = {
    "Benefic":             _C_GOOD,
    "Moderately Benefic":  "#88cc77",
    "Malefic":             _C_WARN,
    "Moderately Malefic":  "#e67e22",
}


def _esc(text: str) -> str:
    """Minimal HTML escape."""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


# ============================================================
# SVG / HTML helpers
# ============================================================

def _star_badge_html(star: BehenianStar, orb: float | None = None) -> str:
    """Render a compact HTML badge for one Behenian star."""
    nature_color = _NATURE_COLORS.get(star.nature, _C_NEUTRAL)
    ruler_color  = RULER_COLORS.get(star.primary_ruler, "#aaa")
    orb_html = f'<span style="font-size:11px;color:{_C_SUBTLE}"> ({orb:.2f}°)</span>' if orb is not None else ""
    return (
        f'<span style="display:inline-flex;align-items:center;gap:6px;'
        f'padding:4px 10px;border-radius:20px;border:1px solid {_C_BORDER};'
        f'background:{_C_CARD};font-size:14px;">'
        f'<span style="color:{_C_ACCENT}">{_esc(star.sigil)}</span> '
        f'<span style="color:{_C_HEADER};font-weight:700">{_esc(star.name)}</span> '
        f'<span style="color:{_C_TEXT};font-size:12px">{auto_cn(_esc(star.cn_name))}</span>'
        f'{orb_html}'
        f'<span style="width:8px;height:8px;border-radius:50%;'
        f'background:{nature_color};display:inline-block;" '
        f'title="{_esc(star.nature)}"></span>'
        f'</span>'
    )


def _activation_banner_html(activations: list[BehenianActivation]) -> str:
    """Render a 'Picatrix Magic Activation' banner."""
    strong = [a for a in activations if a.is_strong]
    level_text = auto_cn("🔥 強烈激活！") if strong else auto_cn("✨ 魔法激活")
    level_color = _C_STRONG if strong else _C_ACCENT
    stars_html = " ".join(_star_badge_html(a.star, a.orb) for a in activations[:6])
    count = len(activations)
    return f"""
<div style="border:2px solid {level_color};border-radius:12px;
     background:linear-gradient(135deg,{_C_BG},{_C_CARD});
     padding:18px 22px;margin:12px 0;">
  <div style="font-size:22px;font-weight:900;color:{level_color};
       letter-spacing:2px;margin-bottom:8px;">{level_text}</div>
  <div style="font-size:13px;color:{_C_TEXT};margin-bottom:10px;">
    {auto_cn(f'共 {count} 個 Behenian 恆星被激活（容許度 {BEHENIAN_ORB}°）')}
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:8px;">{stars_html}</div>
</div>
"""


def _star_card_html(star: BehenianStar) -> str:
    """Full detail HTML card for one Behenian star."""
    nature_color = _NATURE_COLORS.get(star.nature, _C_NEUTRAL)
    ruler_color  = RULER_COLORS.get(star.primary_ruler, "#aaa")
    ruler2_color = RULER_COLORS.get(star.secondary_ruler, "#aaa")

    uses_html = "".join(
        f'<span style="padding:2px 8px;border-radius:12px;'
        f'background:{_C_ACCENT}22;border:1px solid {_C_ACCENT}55;'
        f'color:{_C_TEXT};font-size:12px;margin:2px;">{auto_cn(u)}</span>'
        for u in star.magic_uses_cn
    )

    return f"""
<div style="border:1px solid {_C_BORDER};border-radius:14px;
     background:{_C_CARD};padding:20px 24px;margin:10px 0;
     box-shadow:0 4px 24px rgba(0,0,0,0.4);">
  <!-- Header -->
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">
    <div style="font-size:44px;line-height:1;">{_esc(star.sigil)}</div>
    <div>
      <div style="font-size:24px;font-weight:900;color:{_C_HEADER};">
        {_esc(star.name)}
      </div>
      <div style="font-size:14px;color:{_C_TEXT};">
        {auto_cn(_esc(star.cn_name))} · {_esc(star.modern_name)}
      </div>
      <div style="font-size:13px;color:{_C_SUBTLE};">
        {auto_cn(f'{star.sign} {star.sign_degree:.1f}°')}
        &nbsp;·&nbsp;{auto_cn(star.nature)}
      </div>
    </div>
    <div style="margin-left:auto;text-align:right;">
      <div style="font-size:12px;color:{ruler_color};">
        ★ {auto_cn(RULER_CN.get(star.primary_ruler, star.primary_ruler))}
      </div>
      <div style="font-size:12px;color:{ruler2_color};">
        ☆ {auto_cn(RULER_CN.get(star.secondary_ruler, star.secondary_ruler))}
      </div>
    </div>
  </div>

  <!-- Correspondences grid -->
  <div style="display:grid;grid-template-columns:repeat(3,1fr);
       gap:10px;margin-bottom:14px;">
    {_corr_item(auto_cn("💎 寶石"), f"{auto_cn(star.gemstone_cn)} ({star.gemstone})")
     + _corr_item(auto_cn("🌿 草藥"), f"{auto_cn(star.herb_cn)} ({star.herb})")
     + _corr_item(auto_cn("🎨 顏色"), auto_cn(star.color_cn))
     + _corr_item(auto_cn("🕯️ 薰香"), auto_cn(star.incense_cn))
     + _corr_item(auto_cn("🔭 位置"), f"{star.sign} {star.sign_degree:.1f}°")
     + _corr_item(auto_cn("✨ 性質"), auto_cn(star.nature))}
  </div>

  <!-- Magic uses -->
  <div style="margin-bottom:12px;">
    <div style="font-size:12px;font-weight:700;color:{_C_SUBTLE};
         margin-bottom:6px;">{auto_cn("魔法用途 / Magic Uses")}</div>
    <div style="display:flex;flex-wrap:wrap;gap:4px;">{uses_html}</div>
  </div>

  <!-- Talisman power -->
  <div style="background:{_C_BG};border-radius:8px;padding:10px 14px;
       margin-bottom:10px;border-left:3px solid {_C_ACCENT};">
    <div style="font-size:12px;color:{_C_SUBTLE};">{auto_cn("護符功效")}</div>
    <div style="font-size:14px;color:{_C_TEXT};">{auto_cn(_esc(star.talisman_power_cn))}</div>
  </div>

  <!-- Image to engrave -->
  <div style="background:{_C_BG};border-radius:8px;padding:10px 14px;
       margin-bottom:10px;border-left:3px solid {_C_BORDER};">
    <div style="font-size:12px;color:{_C_SUBTLE};">{auto_cn("護符圖像（刻印）")}</div>
    <div style="font-size:13px;color:{_C_TEXT};">{auto_cn(_esc(star.image_description_cn))}</div>
  </div>
</div>
"""


def _corr_item(label: str, value: str) -> str:
    return (
        f'<div style="background:{_C_BG};border-radius:8px;'
        f'padding:8px 10px;border:1px solid {_C_BORDER}33;">'
        f'<div style="font-size:11px;color:{_C_SUBTLE};">{label}</div>'
        f'<div style="font-size:13px;color:{_C_TEXT};">{value}</div>'
        f'</div>'
    )


def _invocation_html(star: BehenianStar) -> str:
    """Render the invocation text card."""
    return f"""
<div style="border:1px solid {_C_BORDER}66;border-radius:12px;
     background:{_C_BG};padding:18px 22px;margin:10px 0;">
  <div style="font-size:15px;font-weight:700;color:{_C_HEADER};
       margin-bottom:10px;">{auto_cn("📜 召喚詞 / Invocation")}</div>
  <div style="font-size:12px;color:{_C_SUBTLE};font-style:italic;
       margin-bottom:8px;">{_esc(star.invocation_latin)}</div>
  <div style="font-size:13px;color:{_C_TEXT};margin-bottom:8px;">
    {_esc(star.invocation_en)}
  </div>
  <div style="font-size:14px;color:{_C_ACCENT};font-weight:600;">
    {auto_cn(_esc(star.invocation_cn))}
  </div>
</div>
"""


def _talisman_instructions_html(star: BehenianStar) -> str:
    """Step-by-step talisman making instructions."""
    steps = [
        (auto_cn("選擇吉時"),
         auto_cn(f"月亮正在接近 {star.name}（施加相位），並處於{star.sign}座。"
                 f"確認行星時為{RULER_CN.get(star.primary_ruler, star.primary_ruler)}時。")),
        (auto_cn("準備材料"),
         auto_cn(f"寶石：{star.gemstone_cn}（{star.gemstone}）；"
                 f"草藥：{star.herb_cn}（{star.herb}）；"
                 f"顏色：{star.color_cn}；薰香：{star.incense_cn}。")),
        (auto_cn("製作護符"),
         auto_cn(f"在{star.gemstone_cn}或金屬片上刻印：{star.image_description_cn}。"
                 f"以{star.color_cn}布包裹，放置{star.herb_cn}於旁。")),
        (auto_cn("點燃薰香"),
         auto_cn(f"燃燒{star.incense_cn}，面向{star.name}所在方向，朗誦召喚詞三遍。")),
        (auto_cn("完成封印"),
         auto_cn("護符封印完成。保存於乾淨容器中，避免污染。"
                 "需要時取出使用，效力持續至下一次月亮離開本星座為止。")),
    ]
    steps_html = ""
    for i, (title, body) in enumerate(steps, 1):
        steps_html += (
            f'<div style="display:flex;gap:12px;margin-bottom:12px;">'
            f'<div style="min-width:28px;height:28px;border-radius:50%;'
            f'background:{_C_ACCENT};color:{_C_BG};display:flex;'
            f'align-items:center;justify-content:center;font-weight:900;'
            f'font-size:13px;">{i}</div>'
            f'<div>'
            f'<div style="font-size:13px;font-weight:700;color:{_C_HEADER};">{title}</div>'
            f'<div style="font-size:13px;color:{_C_TEXT};">{body}</div>'
            f'</div></div>'
        )
    return (
        f'<div style="border:1px solid {_C_BORDER}66;border-radius:12px;'
        f'background:{_C_CARD};padding:18px 22px;margin:10px 0;">'
        f'<div style="font-size:15px;font-weight:700;color:{_C_HEADER};'
        f'margin-bottom:14px;">{auto_cn("🔮 護符製作步驟 / Talisman Making Steps")}</div>'
        f'{steps_html}'
        f'</div>'
    )


# ============================================================
# Sub-tab renderers
# ============================================================

def _render_activations_tab(chart=None,
                             year: int = 2025, month: int = 1, day: int = 1,
                             hour: int = 12, minute: int = 0,
                             tz: float = 8.0) -> None:
    """Render the chart activations tab."""
    import swisseph as swe

    st.markdown(
        f'<div style="font-size:13px;color:{_C_SUBTLE};margin-bottom:12px;">'
        + auto_cn(f"容許度：{BEHENIAN_ORB}° · 資料來源：Agrippa《神秘哲學三書》· Hermes Trismegistus《十五星書》")
        + "</div>",
        unsafe_allow_html=True,
    )

    if chart is not None:
        # Use provided chart
        activations = activations_from_chart(chart, orb=BEHENIAN_ORB)
        jd = chart.julian_day
    else:
        # Compute from input date
        try:
            ut_hour = hour + minute / 60.0 - tz
            jd_val, _ = swe.utc_to_jd(year, month, day,
                                       int(ut_hour),
                                       int((ut_hour % 1) * 60),
                                       0.0, swe.GREG_CAL)
        except Exception:
            jd_val = swe.julday(year, month, day, hour + minute / 60.0)

        # Compute planet positions
        _PLANET_IDS = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
            "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
            "Saturn": swe.SATURN,
        }
        point_positions: dict[str, float] = {}
        point_speeds: dict[str, float] = {}
        for pname, pid in _PLANET_IDS.items():
            try:
                flags = swe.FLG_SWIEPH | swe.FLG_SPEED
                xx, _ = swe.calc_ut(jd_val, pid, flags)
                point_positions[pname] = float(xx[0])
                point_speeds[pname] = float(xx[3])
            except Exception:
                pass
        activations = detect_activations(
            point_positions, jd_val, orb=BEHENIAN_ORB,
            point_speeds=point_speeds,
            ruler_positions=point_positions,
        )
        jd = jd_val

    if not activations:
        st.info(auto_cn("目前沒有行星在 Behenian 恆星的 6° 容許度內。請換一個日期或查看擇日器。"))
        return

    # Activation banner
    st.markdown(_activation_banner_html(activations), unsafe_allow_html=True)

    # Detail rows
    for a in activations:
        with st.expander(
            f"{a.star.sigil}  {a.star.name}  ({auto_cn(a.star.cn_name)})  ·  "
            f"{a.point_name}  ·  orb {a.orb:.2f}°  ·  {a.activation_level}",
            expanded=(a.orb <= 2.0),
        ):
            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown(_star_card_html(a.star), unsafe_allow_html=True)
            with col2:
                _apply = (auto_cn("🌙 施加（應用）相位") if a.applying
                          else auto_cn("↩️ 分離相位") if a.applying is False
                          else auto_cn("—"))
                st.metric(auto_cn("相位狀態"), _apply)
                st.metric(auto_cn("容許度"), f"{a.orb:.2f}°")
                ruler_cn = RULER_CN.get(a.star.primary_ruler, a.star.primary_ruler)
                st.metric(auto_cn("主星"), auto_cn(ruler_cn))
                st.metric(auto_cn("護符功效"), auto_cn(a.star.talisman_power_cn))

                if a.ruler_active:
                    st.success(auto_cn("✅ 主星強力激活 — 絕佳製符時機！"))

            st.markdown(_invocation_html(a.star), unsafe_allow_html=True)
            st.markdown(_talisman_instructions_html(a.star), unsafe_allow_html=True)


def _render_talisman_tab() -> None:
    """Render talisman recommendation panel."""
    st.markdown(
        f'<div style="font-size:14px;color:{_C_SUBTLE};margin-bottom:12px;">'
        + auto_cn("根據您的需求選擇對應的 Behenian 恆星護符")
        + "</div>",
        unsafe_allow_html=True,
    )

    # Category selector
    lang = get_ui_lang()
    cat_map = MAGIC_CATEGORIES_CN if lang in ("zh", "zh_cn") else MAGIC_CATEGORIES
    cat_options = list(cat_map.keys())
    chosen_cat = st.selectbox(
        auto_cn("選擇魔法目標 / Select Magic Purpose"),
        options=cat_options,
        key="_behenian_cat",
    )
    relevant_names = cat_map.get(chosen_cat, [])
    relevant_stars = [BEHENIAN_BY_NAME[n] for n in relevant_names if n in BEHENIAN_BY_NAME]

    if not relevant_stars:
        st.info(auto_cn("此分類暫無對應恆星。"))
        return

    st.markdown(
        f'<div style="font-size:13px;color:{_C_TEXT};margin-bottom:8px;">'
        + auto_cn(f"以下 {len(relevant_stars)} 顆 Behenian 恆星對應您的需求：")
        + "</div>",
        unsafe_allow_html=True,
    )

    for star in relevant_stars:
        with st.expander(
            f"{star.sigil} {star.name} — {auto_cn(star.talisman_power_cn)}",
            expanded=False,
        ):
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown(_star_card_html(star), unsafe_allow_html=True)
            with col2:
                st.markdown(_invocation_html(star), unsafe_allow_html=True)
                st.markdown(_talisman_instructions_html(star), unsafe_allow_html=True)


def _render_electional_tab(
    year: int = 2025, month: int = 1, day: int = 1,
    hour: int = 12, minute: int = 0,
) -> None:
    """Render electional astrology window finder."""
    st.markdown(
        f'<div style="font-size:13px;color:{_C_SUBTLE};margin-bottom:12px;">'
        + auto_cn("尋找月亮施加接近 Behenian 恆星的最佳時機，依據 Picatrix《賢者之目的》卷二第十二章")
        + "</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        _start_date = st.date_input(
            auto_cn("搜尋起始日期"),
            value=datetime(year, month, day).date(),
            key="_elect_start",
        )
    with col2:
        _days = st.slider(
            auto_cn("搜尋天數"),
            min_value=7, max_value=60, value=30,
            key="_elect_days",
        )
    with col3:
        _orb = st.slider(
            auto_cn("月亮容許度 (°)"),
            min_value=1.0, max_value=6.0, value=4.0, step=0.5,
            key="_elect_orb",
        )

    # Star filter
    _star_options = ["All / 全部"] + [s.name for s in BEHENIAN_STARS]
    _chosen_stars = st.multiselect(
        auto_cn("篩選恆星（留空 = 全部）"),
        options=_star_options[1:],
        default=[],
        key="_elect_stars",
    )
    _target_names = _chosen_stars if _chosen_stars else None

    if st.button(auto_cn("🔍 搜尋最佳製符時機"), key="_elect_search"):
        start_dt = datetime(
            _start_date.year, _start_date.month, _start_date.day,
            tzinfo=timezone.utc,
        )
        with st.spinner(auto_cn("搜尋中……")):
            windows = find_electional_windows(
                star_names=_target_names,
                start_dt=start_dt,
                days_ahead=_days,
                orb=_orb,
            )

        if not windows:
            st.warning(auto_cn("未找到符合條件的時機。請擴大搜尋範圍或增加容許度。"))
        else:
            st.success(auto_cn(f"找到 {len(windows)} 個製符時機"))
            import pandas as pd
            rows = []
            for w in windows[:50]:  # cap display at 50
                rows.append({
                    auto_cn("日期時間 (UTC)"): w.dt_utc.strftime("%Y-%m-%d %H:%M"),
                    auto_cn("恆星"): f"{w.star.sigil} {w.star.name}",
                    auto_cn("中文"): auto_cn(w.star.cn_name),
                    auto_cn("月亮容許度"): f"{w.orb:.2f}°",
                    auto_cn("月亮位置"): f"{w.moon_longitude:.1f}°",
                    auto_cn("主星位置"): f"{auto_cn(RULER_CN.get(w.star.primary_ruler, ''))} {w.ruler_sign} {w.ruler_longitude:.1f}°",
                    auto_cn("護符功效"): auto_cn(w.star.talisman_power_cn),
                })
            st.dataframe(pd.DataFrame(rows), width="stretch")

            # Show detail for first 3 windows
            st.markdown(
                f'<div style="font-size:14px;font-weight:700;color:{_C_HEADER};'
                f'margin:16px 0 8px;">'
                + auto_cn("前三個最近時機詳情：")
                + "</div>",
                unsafe_allow_html=True,
            )
            for w in windows[:3]:
                with st.expander(
                    f"📅 {w.dt_utc.strftime('%Y-%m-%d %H:%M')} UTC — "
                    f"{w.star.sigil} {w.star.name}",
                    expanded=True,
                ):
                    st.markdown(_star_card_html(w.star), unsafe_allow_html=True)
                    st.markdown(_talisman_instructions_html(w.star), unsafe_allow_html=True)


def _render_today_magic_tab(
    year: int = 2025, month: int = 1, day: int = 1,
    hour: int = 12, minute: int = 0,
    timezone_offset: float = 8.0,
) -> None:
    """Render the Today's Magic quick query tab."""
    st.markdown(
        f'<div style="font-size:13px;color:{_C_SUBTLE};margin-bottom:12px;">'
        + auto_cn("快速查詢：今日天象中哪些 Behenian 恆星正在魔法激活狀態？")
        + "</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        _q_date = st.date_input(
            auto_cn("查詢日期"),
            value=datetime.now().date(),
            key="_today_date",
        )
    with col2:
        _q_time = st.time_input(
            auto_cn("查詢時間"),
            value=datetime.now().time(),
            key="_today_time",
        )
    with col3:
        _q_tz = st.number_input(
            auto_cn("時區"),
            value=float(timezone_offset),
            format="%.1f",
            min_value=-12.0, max_value=14.0, step=0.5,
            key="_today_tz",
        )

    if st.button(auto_cn("⚡ 立即查詢今日魔法"), key="_today_query"):
        with st.spinner(auto_cn("計算天象……")):
            result = compute_today_magic(
                year=_q_date.year, month=_q_date.month, day=_q_date.day,
                hour=_q_time.hour, minute=_q_time.minute,
                timezone_offset=float(_q_tz),
            )

        # Moon info banner
        moon_sign_cn = _ZODIAC_CN.get(result.moon_sign, result.moon_sign)
        st.markdown(
            f'<div style="background:{_C_CARD};border:1px solid {_C_MOON}55;'
            f'border-radius:10px;padding:12px 16px;margin-bottom:12px;">'
            f'<span style="font-size:18px;">🌙</span> '
            f'<span style="color:{_C_MOON};font-weight:700;">'
            + auto_cn(f"月亮：{moon_sign_cn} {result.moon_sign_degree:.1f}°")
            + f'</span></div>',
            unsafe_allow_html=True,
        )

        if not result.activations:
            st.info(auto_cn("今日無 Behenian 恆星激活。宜休息靜養，等待良機。"))
        else:
            st.markdown(_activation_banner_html(result.activations), unsafe_allow_html=True)
            for a in result.activations:
                with st.expander(
                    f"{a.star.sigil} {a.star.name} — {a.point_name} — {a.orb:.2f}°",
                    expanded=(a.orb <= 2.0),
                ):
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.markdown(_star_card_html(a.star), unsafe_allow_html=True)
                    with col2:
                        st.markdown(_invocation_html(a.star), unsafe_allow_html=True)


_ZODIAC_CN = {
    "Aries": "牡羊座", "Taurus": "金牛座", "Gemini": "雙子座",
    "Cancer": "巨蟹座", "Leo": "獅子座", "Virgo": "處女座",
    "Libra": "天秤座", "Scorpio": "天蠍座", "Sagittarius": "射手座",
    "Capricorn": "摩羯座", "Aquarius": "水瓶座", "Pisces": "雙魚座",
}


def _render_compendium_tab() -> None:
    """Render the full star compendium (browse all 15)."""
    st.markdown(
        f'<div style="font-size:13px;color:{_C_SUBTLE};margin-bottom:12px;">'
        + auto_cn("全部十五顆 Behenian 根源恆星 — Agrippa《神秘哲學三書》· Picatrix《賢者之目的》")
        + "</div>",
        unsafe_allow_html=True,
    )

    # Summary grid
    _cols = st.columns(3)
    for i, star in enumerate(BEHENIAN_STARS):
        with _cols[i % 3]:
            nature_color = _NATURE_COLORS.get(star.nature, _C_NEUTRAL)
            st.markdown(
                f'<div style="border:1px solid {_C_BORDER}55;border-radius:10px;'
                f'background:{_C_CARD};padding:10px 12px;margin-bottom:8px;'
                f'cursor:pointer;">'
                f'<div style="font-size:20px;">{_esc(star.sigil)}</div>'
                f'<div style="font-size:14px;font-weight:700;color:{_C_HEADER};">'
                f'{_esc(star.name)}</div>'
                f'<div style="font-size:12px;color:{_C_TEXT};">'
                f'{auto_cn(_esc(star.cn_name))}</div>'
                f'<div style="font-size:11px;color:{_C_SUBTLE};">'
                f'{star.sign} {star.sign_degree:.1f}°</div>'
                f'<div style="font-size:11px;color:{nature_color};">'
                f'{_esc(star.nature)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # Full detail for each star
    for star in BEHENIAN_STARS:
        with st.expander(
            f"{star.sigil} {star.name} ({auto_cn(star.cn_name)}) — "
            f"{star.sign} {star.sign_degree:.1f}°",
            expanded=False,
        ):
            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown(_star_card_html(star), unsafe_allow_html=True)
            with col2:
                st.markdown(_invocation_html(star), unsafe_allow_html=True)
                st.markdown(_talisman_instructions_html(star), unsafe_allow_html=True)


# ============================================================
# Main Entry Point
# ============================================================

def render_streamlit(
    chart=None,
    year: int = 2025, month: int = 1, day: int = 1,
    hour: int = 12, minute: int = 0,
    timezone_offset: float = 8.0,
) -> None:
    """
    Render the full Picatrix + Behenian Stars Streamlit page.

    Parameters
    ----------
    chart : WesternChart, optional
        Pre-computed western chart.  If provided, activations are derived
        from the natal planet positions.  If None, positions are computed
        from the date/time parameters.
    year, month, day : int
        Date for calculations (when chart is None or for electional/today tabs).
    hour, minute : int
        Time of day.
    timezone_offset : float
        UTC offset in hours.
    """
    # Inject scoped styles
    st.markdown(f"""
<style>
.behenian-hero {{
    background: linear-gradient(135deg, {_C_BG} 0%, #2d1b4e 100%);
    border: 1px solid {_C_BORDER};
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
}}
.behenian-hero h2 {{
    font-size: 28px;
    font-weight: 900;
    color: {_C_HEADER};
    letter-spacing: 2px;
    margin: 0 0 8px;
}}
.behenian-hero p {{
    font-size: 14px;
    color: {_C_SUBTLE};
    margin: 0;
}}
</style>
""", unsafe_allow_html=True)

    # Hero banner
    st.markdown(f"""
<div class="behenian-hero">
  <h2>✦ Picatrix 占星魔法 · Behenian 固定星</h2>
  <p>
    {auto_cn("十五顆根源恆星魔法系統 · 源自《賢者之目的》(Picatrix / Ghayat al-Hakim) 與 Agrippa《神秘哲學三書》")}
  </p>
</div>
""", unsafe_allow_html=True)

    # Main tabs
    (tab_activations, tab_talisman, tab_electional, tab_today,
     tab_compendium, tab_wizard, tab_elect_calc, tab_talisman_db) = st.tabs([
        auto_cn("⚡ 星盤激活"),
        auto_cn("🔮 護符製作"),
        auto_cn("📅 擇日器"),
        auto_cn("🌟 今日魔法"),
        auto_cn("📚 星典瀏覽"),
        auto_cn("⚗ 製符嚮導"),
        auto_cn("🗓 電擇計算器"),
        auto_cn("📖 護符資料庫"),
    ])

    with tab_activations:
        st.subheader(auto_cn("⚡ Behenian 恆星激活檢測"))
        st.caption(auto_cn("檢查星盤中的行星、上升點、中天等是否在 Behenian 恆星的 6° 容許度內"))
        _render_activations_tab(
            chart=chart,
            year=year, month=month, day=day,
            hour=hour, minute=minute, tz=timezone_offset,
        )

    with tab_talisman:
        st.subheader(auto_cn("🔮 Picatrix 護符製作推薦"))
        st.caption(auto_cn("根據您的目標選擇對應的 Behenian 恆星護符，包含完整製作步驟與召喚詞"))
        _render_talisman_tab()

    with tab_electional:
        st.subheader(auto_cn("📅 擇日器 — 最佳製符時機"))
        st.caption(auto_cn("掃描未來時間，找到月亮施加接近目標 Behenian 恆星的最佳製符窗口"))
        _render_electional_tab(
            year=year, month=month, day=day,
            hour=hour, minute=minute,
        )

    with tab_today:
        st.subheader(auto_cn("🌟 今日魔法快速查詢"))
        st.caption(auto_cn("查詢任意時刻天象中激活的 Behenian 恆星與對應魔法建議"))
        _render_today_magic_tab(
            year=year, month=month, day=day,
            hour=hour, minute=minute,
            timezone_offset=timezone_offset,
        )

    with tab_compendium:
        st.subheader(auto_cn("📚 十五 Behenian 恆星全典"))
        st.caption(auto_cn("完整瀏覽十五顆 Behenian 根源恆星的古典對應與魔法傳統"))
        _render_compendium_tab()

    # ── 新增模組：互動式嚮導 + 電擇計算器 + 護符資料庫 ──────
    with tab_wizard:
        st.subheader(auto_cn("⚗ 互動式 Talisman 製作嚮導"))
        st.caption(auto_cn(
            "選擇目的 → 系統推薦最適行星護符 → 生成古抄本風格 SVG 護符 · "
            "依據 Picatrix《賢者之目的》傳統"
        ))
        try:
            from frontend.talismanic_renderer import render_talisman_wizard
            render_talisman_wizard()
        except Exception as _e:
            st.error(auto_cn(f"嚮導模組載入失敗：{_e}"))
            st.exception(_e)

    with tab_elect_calc:
        st.subheader(auto_cn("🗓 Picatrix 電擇計算器"))
        st.caption(auto_cn(
            "精確評估任意時刻製作指定行星護符的適宜程度 · "
            "嚴格遵循 Picatrix 卷二第十章 + Lilly 擇日規則"
        ))
        try:
            from frontend.talismanic_renderer import render_electional_calc
            render_electional_calc()
        except Exception as _e:
            st.error(auto_cn(f"電擇模組載入失敗：{_e}"))
            st.exception(_e)

    with tab_talisman_db:
        st.subheader(auto_cn("📖 完整護符資料庫"))
        st.caption(auto_cn(
            "七行星護符 + 36 Decan 護符完整資料 · "
            "源自 Picatrix、Agrippa、Hermes Trismegistus 三大傳統"
        ))
        try:
            from frontend.talismanic_renderer import render_talisman_database
            render_talisman_database()
        except Exception as _e:
            st.error(auto_cn(f"資料庫模組載入失敗：{_e}"))
            st.exception(_e)
