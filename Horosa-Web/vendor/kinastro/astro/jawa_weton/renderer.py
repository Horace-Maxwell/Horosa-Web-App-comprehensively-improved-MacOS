"""
爪哇 Weton / Primbon Streamlit 渲染模組 (Renderer)

提供四個主要頁籤的 Streamlit UI：
1. 本命分析 — 出生 Weton、Neptu、Primbon 性格詳解
2. 合婚計算 — 兩人 Weton Neptu 相容性
3. 擇日器 — 未來 35 天 Weton 吉凶日曆
4. 每日 Primbon — 今日 Weton 與活動建議

視覺風格：仿爪哇蠟染（Batik）風格，深棕金色調
古法依據：Primbon Betaljemur Adammakna
"""

from datetime import date, timedelta

import streamlit as st

from .calculator import (
    WetonResult, WetonInfo, MarriageCompatResult,
    WetonCalculator, compute_weton,
)
from .constants import (
    SAPTAWARA, PANCAWARA, WETON_PROFILES,
    MARRIAGE_COMPAT, WETON_CYCLE_ORDER,
    SPECIAL_WETONS, CULTURAL_INTRO,
    SAPTAWARA_NEPTU, PANCAWARA_NEPTU,
)


# ============================================================
# 色彩主題 — 仿爪哇蠟染（Batik）風格
# ============================================================
_BATIK_BG        = "#2C1810"   # 深棕底色
_BATIK_CARD      = "#3D2415"   # 卡片背景
_BATIK_BORDER    = "#8B6914"   # 金色邊框
_BATIK_HEADER    = "#F5D06A"   # 金色標題
_BATIK_TEXT      = "#EDD9A3"   # 米黃主文字
_BATIK_SUBTLE    = "#A08040"   # 深金次要文字
_BATIK_ACCENT    = "#D4A017"   # 亮金強調色
_BATIK_GOOD      = "#5BA553"   # 吉日綠
_BATIK_BAD       = "#C0392B"   # 凶日紅
_BATIK_NEUTRAL   = "#9B8B6E"   # 中性棕
_BATIK_CELL_ODD  = "#3D2415"   # 奇數行
_BATIK_CELL_EVEN = "#2C1810"   # 偶數行
_BATIK_HIGHLIGHT = "#D4A017"   # 高亮金色


def _escape_html(text: str) -> str:
    """HTML 轉義"""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _neptu_color(neptu: int) -> str:
    """依 Neptu 值回傳顏色"""
    if neptu >= 15:
        return _BATIK_GOOD
    elif neptu >= 10:
        return _BATIK_ACCENT
    return _BATIK_BAD


# ============================================================
# 主入口點 (Main Streamlit Entry Point)
# ============================================================

def render_streamlit(result: WetonResult) -> None:
    """
    Streamlit 主渲染函數 — 爪哇 Weton / Primbon 排盤

    參數：
        result (WetonResult): WetonCalculator 計算結果
    """
    w = result.weton

    # ── 頂部標題 ─────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
          background: linear-gradient(135deg, {_BATIK_BG}, #4A2C0A);
          border: 2px solid {_BATIK_BORDER};
          border-radius: 8px;
          padding: 20px;
          text-align: center;
          margin-bottom: 16px;
        ">
          <div style="font-size:0.9em; color:{_BATIK_SUBTLE}; letter-spacing:0.1em;">
            ⋆ PRIMBON ⋆ JAWA ⋆ 爪哇傳統命理 ⋆
          </div>
          <div style="font-size:2.2em; font-weight:bold; color:{_BATIK_HEADER};
                      letter-spacing:0.05em; margin: 8px 0;">
            {_escape_html(w.profile.get('symbol', '⭐'))} {_escape_html(w.weton_name)}
          </div>
          <div style="font-size:1.1em; color:{_BATIK_TEXT};">
            Neptu 命理數：
            <span style="font-size:1.8em; font-weight:bold;
                         color:{_neptu_color(w.neptu_total)};">
              {w.neptu_total}
            </span>
          </div>
          <div style="font-size:0.85em; color:{_BATIK_SUBTLE}; margin-top:6px;">
            {result.year}年{result.month}月{result.day}日
            {result.hour:02d}:{result.minute:02d}
            {(' · ' + _escape_html(result.location_name)) if result.location_name else ''}
          </div>
          {'<div style="background:#7B1FA2; color:#fff; padding:4px 12px; border-radius:12px; display:inline-block; margin-top:8px; font-size:0.85em;">✨ ' + _escape_html(w.special_cn) + ' — 神聖日</div>' if w.is_special else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── 四個主要頁籤 ──────────────────────────────────────────
    tab_natal, tab_compat, tab_elect, tab_daily = st.tabs([
        "🔮 本命分析",
        "💑 合婚計算",
        "📅 擇日器",
        "☀️ 每日 Primbon",
    ])

    with tab_natal:
        _render_natal_tab(result)

    with tab_compat:
        _render_compat_tab(result)

    with tab_elect:
        _render_electional_tab(result)

    with tab_daily:
        _render_daily_tab(result)


# ============================================================
# 頁籤 1：本命分析
# ============================================================

def _render_natal_tab(result: WetonResult) -> None:
    """渲染本命分析頁籤"""
    w = result.weton

    # ── Weton 核心資訊卡片區 ──
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""<div style="background:{_BATIK_CARD}; border:1px solid {_BATIK_BORDER};
                border-radius:6px; padding:12px; text-align:center;">
              <div style="color:{_BATIK_SUBTLE}; font-size:0.75em;">SAPTAWARA 七曜</div>
              <div style="color:{_BATIK_HEADER}; font-size:1.5em; font-weight:bold;">
                {_escape_html(w.saptawara.name)}
              </div>
              <div style="color:{_BATIK_TEXT}; font-size:0.85em;">
                {_escape_html(w.saptawara.cn)} · Neptu {w.saptawara.neptu}
              </div>
              <div style="color:{_BATIK_SUBTLE}; font-size:0.75em; margin-top:4px;">
                {_escape_html(w.saptawara.deity)}<br>
                顏色：{_escape_html(w.saptawara.color)}
              </div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div style="background:{_BATIK_CARD}; border:2px solid {_BATIK_ACCENT};
                border-radius:6px; padding:12px; text-align:center;">
              <div style="color:{_BATIK_SUBTLE}; font-size:0.75em;">WETON 完整命盤</div>
              <div style="color:{_BATIK_HEADER}; font-size:1.8em; font-weight:bold;">
                {_escape_html(w.profile.get('symbol', '⭐'))}
              </div>
              <div style="color:{_BATIK_ACCENT}; font-size:1.1em; font-weight:bold;">
                Neptu {w.neptu_total}
              </div>
              <div style="color:{_BATIK_TEXT}; font-size:0.85em;">
                {_escape_html(w.weton_name)}
              </div>
              <div style="color:{_BATIK_SUBTLE}; font-size:0.75em;">
                {_escape_html(w.profile.get('weton_nature', ''))}
              </div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div style="background:{_BATIK_CARD}; border:1px solid {_BATIK_BORDER};
                border-radius:6px; padding:12px; text-align:center;">
              <div style="color:{_BATIK_SUBTLE}; font-size:0.75em;">PANCAWARA 五曜</div>
              <div style="color:{_BATIK_HEADER}; font-size:1.5em; font-weight:bold;">
                {_escape_html(w.pancawara.name)}
              </div>
              <div style="color:{_BATIK_TEXT}; font-size:0.85em;">
                {_escape_html(w.pancawara.cn)} · Neptu {w.pancawara.neptu}
              </div>
              <div style="color:{_BATIK_SUBTLE}; font-size:0.75em; margin-top:4px;">
                方位：{_escape_html(w.pancawara.direction)}<br>
                顏色：{_escape_html(w.pancawara.color)}
              </div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Neptu 計算說明 ──
    st.markdown(
        f"""<div style="background:{_BATIK_CARD}; border-left:4px solid {_BATIK_ACCENT};
            border-radius:4px; padding:10px 14px; margin-bottom:12px;">
          <span style="color:{_BATIK_SUBTLE}; font-size:0.8em;">Neptu 計算：</span>
          <span style="color:{_BATIK_TEXT};">
            {_escape_html(w.saptawara.name)} ({w.saptawara.neptu})
            ＋ {_escape_html(w.pancawara.name)} ({w.pancawara.neptu})
            ＝
          </span>
          <span style="color:{_BATIK_HEADER}; font-size:1.2em; font-weight:bold;">
            {w.neptu_total}
          </span>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Primbon 性格分析 ──
    st.subheader("🎭 性格特質 (Watak / 個性)")
    st.markdown(
        f"""<div style="background:{_BATIK_CARD}; border:1px solid {_BATIK_BORDER};
            border-radius:6px; padding:14px; color:{_BATIK_TEXT}; line-height:1.7;">
          {_escape_html(w.profile.get('personality', ''))}
        </div>""",
        unsafe_allow_html=True,
    )

    # ── 事業傾向 ──
    col_c, col_h = st.columns(2)
    with col_c:
        st.subheader("💼 事業傾向 (Karir)")
        st.markdown(
            f"""<div style="background:{_BATIK_CARD}; border:1px solid {_BATIK_BORDER};
                border-radius:6px; padding:12px; color:{_BATIK_TEXT}; line-height:1.6;">
              {_escape_html(w.profile.get('career', ''))}
            </div>""",
            unsafe_allow_html=True,
        )
    with col_h:
        st.subheader("🌿 健康提示 (Kesehatan)")
        st.markdown(
            f"""<div style="background:{_BATIK_CARD}; border:1px solid {_BATIK_BORDER};
                border-radius:6px; padding:12px; color:{_BATIK_TEXT}; line-height:1.6;">
              {_escape_html(w.profile.get('health', ''))}
            </div>""",
            unsafe_allow_html=True,
        )

    # ── 幸運資訊 ──
    st.subheader("🍀 幸運資訊 (Keberuntungan)")
    lcol1, lcol2, lcol3 = st.columns(3)
    with lcol1:
        st.markdown(
            f"""<div style="background:{_BATIK_CARD}; border:1px solid {_BATIK_BORDER};
                border-radius:6px; padding:10px; text-align:center;">
              <div style="color:{_BATIK_SUBTLE}; font-size:0.75em;">🧭 幸運方位</div>
              <div style="color:{_BATIK_HEADER}; font-size:1.1em; font-weight:bold;">
                {_escape_html(w.profile.get('lucky_direction', ''))}
              </div>
            </div>""",
            unsafe_allow_html=True,
        )
    with lcol2:
        st.markdown(
            f"""<div style="background:{_BATIK_CARD}; border:1px solid {_BATIK_BORDER};
                border-radius:6px; padding:10px; text-align:center;">
              <div style="color:{_BATIK_SUBTLE}; font-size:0.75em;">🎨 幸運顏色</div>
              <div style="color:{_BATIK_HEADER}; font-size:1.1em; font-weight:bold;">
                {_escape_html(w.profile.get('lucky_color', ''))}
              </div>
            </div>""",
            unsafe_allow_html=True,
        )
    with lcol3:
        professions = w.profile.get('lucky_professions', [])
        profs_str = "、".join(professions[:3]) if professions else "—"
        st.markdown(
            f"""<div style="background:{_BATIK_CARD}; border:1px solid {_BATIK_BORDER};
                border-radius:6px; padding:10px; text-align:center;">
              <div style="color:{_BATIK_SUBTLE}; font-size:0.75em;">💼 適合職業</div>
              <div style="color:{_BATIK_HEADER}; font-size:0.95em; font-weight:bold;">
                {_escape_html(profs_str)}
              </div>
            </div>""",
            unsafe_allow_html=True,
        )

    if professions:
        st.markdown(
            f"**全部適合職業：** " + "、".join(professions),
        )

    # ── 35 天 Weton 循環矩陣 ──
    st.divider()
    st.subheader("🗓️ 35 天 Weton 循環矩陣")
    st.caption("7（Saptawara）× 5（Pancawara）= 35 種完整 Weton 組合；您的出生 Weton 以金框高亮顯示")
    _render_weton_cycle_grid(w)

    # ── 文化簡介 ──
    st.divider()
    with st.expander("📖 什麼是 Weton？— 文化與歷史背景", expanded=False):
        st.markdown(CULTURAL_INTRO["zh"])


def _render_weton_cycle_grid(weton: WetonInfo) -> None:
    """渲染 35 天 Weton 循環矩陣（7 行 × 5 列）"""
    saptawara_names = [row[0] for row in SAPTAWARA]
    pancawara_names = [row[0] for row in PANCAWARA]

    # 表頭
    header_cols = st.columns([1.5] + [1] * 5)
    header_cols[0].markdown(
        f"<div style='color:{_BATIK_SUBTLE}; font-size:0.8em; font-weight:bold; text-align:center;'>七曜 ↓ / 五曜 →</div>",
        unsafe_allow_html=True,
    )
    for pi, pname in enumerate(pancawara_names):
        nep = PANCAWARA[pi][1]
        header_cols[pi + 1].markdown(
            f"<div style='color:{_BATIK_ACCENT}; font-size:0.8em; font-weight:bold; text-align:center;'>"
            f"{pname}<br><span style='color:{_BATIK_SUBTLE}; font-size:0.85em;'>Nep {nep}</span></div>",
            unsafe_allow_html=True,
        )

    # 每行 = 一個 Saptawara
    for si, sname in enumerate(saptawara_names):
        row_cols = st.columns([1.5] + [1] * 5)
        sw_nep = SAPTAWARA[si][1]
        row_cols[0].markdown(
            f"<div style='color:{_BATIK_ACCENT}; font-size:0.8em; font-weight:bold; text-align:center;'>"
            f"{sname}<br><span style='color:{_BATIK_SUBTLE}; font-size:0.85em;'>Nep {sw_nep}</span></div>",
            unsafe_allow_html=True,
        )
        for pi, pname in enumerate(pancawara_names):
            neptu = SAPTAWARA[si][1] + PANCAWARA[pi][1]
            is_current = (sname == weton.saptawara.name and pname == weton.pancawara.name)
            is_special = (sname, pname) in SPECIAL_WETONS
            profile = WETON_PROFILES.get((sname, pname), {})
            symbol = profile.get("symbol", "")

            if is_current:
                bg = _BATIK_HIGHLIGHT
                fg = "#2C1810"
                border = "3px solid #FFF"
            elif is_special:
                bg = "#4A1060"
                fg = "#EDD9A3"
                border = f"1px solid {_BATIK_BORDER}"
            else:
                bg = _BATIK_CARD
                fg = _BATIK_TEXT
                border = f"1px solid {_BATIK_BORDER}"

            row_cols[pi + 1].markdown(
                f"""<div style="background:{bg}; border:{border}; border-radius:4px;
                    padding:4px 2px; text-align:center; color:{fg}; font-size:0.72em;
                    {'box-shadow:0 0 8px rgba(212,160,23,0.6);' if is_current else ''}">
                  <div style="font-size:0.9em;">{symbol}</div>
                  <div style="font-weight:{'bold' if is_current else 'normal'}; font-size:0.85em;">{pname}</div>
                  <div style="color:{'#2C1810' if is_current else _BATIK_ACCENT}; font-size:0.8em;">{neptu}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.caption("🔯 = 特殊聖日（Jumat Kliwon 等）  ·  金框 = 您的出生 Weton  ·  數字 = Neptu 值")


# ============================================================
# 頁籤 2：合婚計算
# ============================================================

def _render_compat_tab(result: WetonResult) -> None:
    """渲染合婚計算頁籤"""
    st.subheader("💑 合婚計算 (Hitungan Jodoh)")
    st.caption("根據古典 Primbon Betaljemur Adammakna 的合婚算法：兩人 Neptu 相加，取 mod 9 對照吉凶。")

    w1 = result.weton

    # ── 甲方資訊（本命）──
    st.markdown(
        f"""<div style="background:{_BATIK_CARD}; border:1px solid {_BATIK_ACCENT};
            border-radius:6px; padding:10px 14px; margin-bottom:12px;">
          <span style="color:{_BATIK_SUBTLE}; font-size:0.8em;">甲方（本命）</span>
          <span style="color:{_BATIK_HEADER}; font-size:1.1em; font-weight:bold; margin-left:8px;">
            {_escape_html(w1.weton_name)}
          </span>
          <span style="color:{_BATIK_ACCENT}; margin-left:8px;">Neptu {w1.neptu_total}</span>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── 乙方輸入 ──
    st.markdown("**乙方出生日期**")
    compat_col1, compat_col2 = st.columns(2)
    with compat_col1:
        p2_date = st.date_input(
            "乙方生日",
            value=date(1990, 6, 15),
            min_value=date(1, 1, 1),
            max_value=date(date.today().year, 12, 31),
            key="_weton_compat_date",
            label_visibility="collapsed",
        )
    with compat_col2:
        if st.button("💑 計算合婚", key="_btn_weton_compat", type="primary"):
            st.session_state["_weton_compat_computed"] = True

    # ── 計算並顯示結果 ──
    if st.session_state.get("_weton_compat_computed", False):
        try:
            w2 = WetonCalculator.compute_weton_for_date(p2_date)
            compat = WetonCalculator.compute_compatibility(w1, w2)
            _render_compat_result(compat)
        except Exception as e:
            st.error(f"計算出錯：{e}")
    else:
        # 顯示乙方 Weton 預覽
        try:
            w2_preview = WetonCalculator.compute_weton_for_date(p2_date)
            st.info(f"乙方 Weton：**{w2_preview.weton_name}** (Neptu {w2_preview.neptu_total})  ← 點擊「計算合婚」查看詳細結果")
        except Exception:
            pass

    # ── 所有相容組合預覽 ──
    st.divider()
    with st.expander("📊 所有 9 種合婚結果對照表", expanded=False):
        _render_all_compat_table()


def _render_compat_result(compat: MarriageCompatResult) -> None:
    """渲染合婚結果"""
    pct = compat.percentage
    is_good = pct >= 65

    st.markdown(
        f"""<div style="
          background: linear-gradient(135deg, {_BATIK_CARD}, {'#1A3A1A' if is_good else '#3A1A1A'});
          border: 2px solid {compat.color};
          border-radius: 8px;
          padding: 20px;
          text-align: center;
          margin: 12px 0;
        ">
          <div style="font-size:0.85em; color:{_BATIK_SUBTLE}; letter-spacing:0.08em;">
            HASIL PERJODOHAN · 合婚結果
          </div>
          <div style="font-size:2.5em; font-weight:bold; color:{compat.color}; margin:8px 0;">
            {_escape_html(compat.compat_name)}
          </div>
          <div style="font-size:1.2em; color:{_BATIK_TEXT}; font-weight:bold;">
            {_escape_html(compat.compat_cn)}
          </div>
          <div style="font-size:1.0em; color:{_BATIK_ACCENT}; margin-top:8px;">
            {_escape_html(compat.level)}
          </div>
          <div style="margin:12px auto; max-width:300px;">
            <div style="background:#333; border-radius:10px; height:16px; overflow:hidden;">
              <div style="background:{'linear-gradient(90deg, #4CAF50, #8BC34A)' if is_good else 'linear-gradient(90deg, #F44336, #FF5722)'};
                           height:100%; width:{pct}%; border-radius:10px; transition:width 0.5s;"></div>
            </div>
            <div style="color:{_BATIK_TEXT}; font-size:1.1em; margin-top:4px;">{pct}%</div>
          </div>
          <div style="color:{_BATIK_TEXT}; font-size:0.88em; line-height:1.7; text-align:left;
                       max-width:500px; margin:0 auto; padding:0 8px;">
            {_escape_html(compat.description)}
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Neptu 明細
    st.markdown(
        f"""<div style="background:{_BATIK_CARD}; border:1px solid {_BATIK_BORDER};
            border-radius:6px; padding:12px; margin-top:8px;">
          <table style="width:100%; color:{_BATIK_TEXT}; font-size:0.9em;">
            <tr>
              <td style="padding:4px 8px; color:{_BATIK_SUBTLE};">甲方 Weton</td>
              <td style="padding:4px 8px; font-weight:bold; color:{_BATIK_HEADER};">{_escape_html(compat.person1_weton)}</td>
              <td style="padding:4px 8px; color:{_BATIK_ACCENT};">Neptu {compat.neptu1}</td>
            </tr>
            <tr>
              <td style="padding:4px 8px; color:{_BATIK_SUBTLE};">乙方 Weton</td>
              <td style="padding:4px 8px; font-weight:bold; color:{_BATIK_HEADER};">{_escape_html(compat.person2_weton)}</td>
              <td style="padding:4px 8px; color:{_BATIK_ACCENT};">Neptu {compat.neptu2}</td>
            </tr>
            <tr style="border-top:1px solid {_BATIK_BORDER};">
              <td style="padding:4px 8px; color:{_BATIK_SUBTLE};">Neptu 總和</td>
              <td style="padding:4px 8px; font-weight:bold; color:{_BATIK_HEADER};">
                {compat.neptu1} ＋ {compat.neptu2} ＝ {compat.neptu_sum}
              </td>
              <td style="padding:4px 8px; color:{_BATIK_SUBTLE};">
                mod 9 ＝ {compat.remainder if compat.remainder != 0 else '0 (=9)'}
              </td>
            </tr>
          </table>
        </div>""",
        unsafe_allow_html=True,
    )


def _render_all_compat_table() -> None:
    """渲染所有合婚結果對照表"""
    rows = []
    for rem in [1, 2, 3, 4, 5, 6, 7, 8, 0]:
        compat = MARRIAGE_COMPAT[rem]
        name, cn, level, color, desc, pct = compat
        rows.append({
            "Mod": f"{rem if rem != 0 else '0(=9)'}",
            "名稱 (Javanese)": name,
            "中文": cn,
            "等級": level,
            "相容度": f"{pct}%",
            "說明（摘要）": desc[:40] + "…",
        })
    import pandas as pd
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


# ============================================================
# 頁籤 3：擇日器
# ============================================================

def _render_electional_tab(result: WetonResult) -> None:
    """渲染擇日器頁籤"""
    st.subheader("📅 擇日器 — 未來 Weton 日曆")
    st.caption("查看未來 35 天（完整一個 Weton 週期）的每日 Weton 與 Neptu 值，找出適合辦事的吉日。")

    elect_col1, elect_col2 = st.columns([2, 1])
    with elect_col1:
        start = st.date_input(
            "起始日期",
            value=date.today(),
            key="_weton_elect_start",
        )
    with elect_col2:
        n_days = st.selectbox(
            "天數",
            options=[7, 14, 35, 70],
            index=2,
            key="_weton_elect_days",
            format_func=lambda x: f"{x} 天{'（1個週期）' if x==35 else '（2個週期）' if x==70 else ''}",
        )

    # 活動類型篩選
    activity_filter = st.selectbox(
        "篩選適合的活動",
        options=["全部", "結婚", "開業", "重要決策", "出行", "修房建築", "搬家"],
        key="_weton_elect_activity",
    )

    # 生成日曆
    calendar = WetonCalculator.get_weton_calendar(start, n_days)

    # 建立表格資料
    rows = []
    for day_info in calendar:
        neptu = day_info.neptu
        if neptu >= 15:
            level = "🟢 高吉"
        elif neptu >= 12:
            level = "🟡 吉"
        elif neptu >= 10:
            level = "🟡 一般"
        else:
            level = "🔴 謹慎"

        special_mark = f" {day_info.special_name}" if day_info.is_special else ""

        row = {
            "日期": day_info.date.strftime("%Y-%m-%d"),
            "星期": day_info.date.strftime("%a"),
            "Weton": day_info.weton_name + special_mark,
            "Neptu": day_info.neptu,
            "吉凶": level,
        }

        # 活動篩選
        if activity_filter != "全部":
            # 簡化篩選：高 Neptu 適合重要活動
            if activity_filter in ("結婚", "開業", "重要決策") and neptu < 10:
                continue
            elif activity_filter == "搬家" and neptu < 10:
                continue

        rows.append(row)

    if rows:
        import pandas as pd
        df = pd.DataFrame(rows)
        st.dataframe(df, hide_index=True, width="stretch")
        st.caption(f"共顯示 {len(rows)} 天 / 總共 {n_days} 天")
    else:
        st.info("篩選條件下沒有符合的日期，請放寬條件。")

    # ── Weton 吉日摘要 ──
    st.divider()
    st.markdown("**🟢 本期最吉 Weton（Neptu ≥ 15）**")
    best_days = [d for d in calendar if d.neptu >= 15]
    if best_days:
        for d in best_days[:5]:
            st.markdown(
                f"- **{d.date.strftime('%Y-%m-%d %a')}** — {d.weton_name} (Neptu {d.neptu})"
                + (f" ✨ {d.special_name}" if d.is_special else "")
            )
    else:
        st.info("本期無 Neptu ≥ 15 的日期。")

    # ── Jumat Kliwon 提醒 ──
    jumat_kliwon = [d for d in calendar if d.weton_name == "Jumat Kliwon"]
    if jumat_kliwon:
        st.markdown("**🔯 Jumat Kliwon 聖日（靈性修持最佳日）**")
        for d in jumat_kliwon:
            st.markdown(f"- **{d.date.strftime('%Y-%m-%d')}** — Jumat Kliwon ✨")


# ============================================================
# 頁籤 4：每日 Primbon
# ============================================================

def _render_daily_tab(result: WetonResult) -> None:
    """渲染每日 Primbon 頁籤"""
    st.subheader("☀️ 今日 Primbon — 每日 Weton 指引")

    # 今日資訊
    today = date.today()
    today_weton = WetonCalculator.compute_weton_for_date(today)

    st.markdown(
        f"""<div style="
          background: linear-gradient(135deg, {_BATIK_CARD}, #2C1A30);
          border: 2px solid {_BATIK_ACCENT};
          border-radius: 8px;
          padding: 18px;
          text-align: center;
          margin-bottom: 16px;
        ">
          <div style="color:{_BATIK_SUBTLE}; font-size:0.8em;">今日 · {today.strftime('%Y年%m月%d日')}</div>
          <div style="color:{_BATIK_HEADER}; font-size:2em; font-weight:bold; margin:8px 0;">
            {_escape_html(today_weton.profile.get('symbol', '⭐'))} {_escape_html(today_weton.weton_name)}
          </div>
          <div style="color:{_neptu_color(today_weton.neptu_total)}; font-size:1.3em;">
            Neptu <strong>{today_weton.neptu_total}</strong>
          </div>
          {'<div style="background:#7B1FA2; color:#fff; padding:3px 10px; border-radius:10px; display:inline-block; margin-top:6px;">✨ ' + _escape_html(today_weton.special_cn) + ' 神聖日</div>' if today_weton.is_special else ''}
        </div>""",
        unsafe_allow_html=True,
    )

    # ── 今日活動建議 ──
    st.subheader("📋 今日宜忌 (Hari Ini)")
    advice = today_weton.daily_advice
    act_cols = st.columns(2)
    items = list(advice.items())
    half = len(items) // 2 + len(items) % 2
    for i, (act, status) in enumerate(items):
        col = act_cols[0] if i < half else act_cols[1]
        color = _BATIK_GOOD if "吉" in status else (_BATIK_BAD if "凶" in status or "不宜" in status else _BATIK_ACCENT)
        col.markdown(
            f"""<div style="background:{_BATIK_CARD}; border-left:3px solid {color};
                border-radius:4px; padding:6px 10px; margin-bottom:6px; color:{_BATIK_TEXT};">
              <span style="font-weight:bold;">{_escape_html(act)}</span>：
              <span style="color:{color};">{_escape_html(status)}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── 本命與今日 Weton 關係 ──
    st.divider()
    birth_weton = result.weton
    st.subheader("🔗 本命 vs 今日 Weton")
    rel_col1, rel_col2 = st.columns(2)
    with rel_col1:
        st.markdown(
            f"""<div style="background:{_BATIK_CARD}; border:1px solid {_BATIK_BORDER};
                border-radius:6px; padding:10px; text-align:center;">
              <div style="color:{_BATIK_SUBTLE}; font-size:0.75em;">本命 Weton</div>
              <div style="color:{_BATIK_HEADER}; font-size:1.3em; font-weight:bold;">
                {_escape_html(birth_weton.weton_name)}
              </div>
              <div style="color:{_BATIK_ACCENT};">Neptu {birth_weton.neptu_total}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with rel_col2:
        st.markdown(
            f"""<div style="background:{_BATIK_CARD}; border:1px solid {_BATIK_ACCENT};
                border-radius:6px; padding:10px; text-align:center;">
              <div style="color:{_BATIK_SUBTLE}; font-size:0.75em;">今日 Weton</div>
              <div style="color:{_BATIK_HEADER}; font-size:1.3em; font-weight:bold;">
                {_escape_html(today_weton.weton_name)}
              </div>
              <div style="color:{_neptu_color(today_weton.neptu_total)};">Neptu {today_weton.neptu_total}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── 本命與今日合鳴判斷 ──
    neptu_diff = abs(birth_weton.neptu_total - today_weton.neptu_total)
    if neptu_diff <= 2:
        resonance = ("🟢 共鳴強烈", "今日能量與本命高度共鳴，是採取重要行動的好時機！", _BATIK_GOOD)
    elif neptu_diff <= 5:
        resonance = ("🟡 適度共鳴", "今日能量與本命有一定共鳴，可以穩步推進計劃。", _BATIK_ACCENT)
    else:
        resonance = ("🔴 能量差異", "今日能量與本命有較大差異，宜謹慎行事，避免重大決策。", _BATIK_BAD)

    st.markdown(
        f"""<div style="background:{_BATIK_CARD}; border-left:4px solid {resonance[2]};
            border-radius:4px; padding:10px 14px; margin-top:10px;">
          <span style="color:{resonance[2]}; font-weight:bold;">{_escape_html(resonance[0])}</span>
          <span style="color:{_BATIK_TEXT}; margin-left:8px;">{_escape_html(resonance[1])}</span>
          <div style="color:{_BATIK_SUBTLE}; font-size:0.8em; margin-top:4px;">
            Neptu 差距：|{birth_weton.neptu_total} − {today_weton.neptu_total}| = {neptu_diff}
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── 本週 Weton 快覽 ──
    st.divider()
    st.subheader("📆 本週 Weton 一覽")
    week_start = today - timedelta(days=today.weekday())
    week_calendar = WetonCalculator.get_weton_calendar(week_start, 7)
    week_cols = st.columns(7)
    day_names_cn = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
    for i, day_info in enumerate(week_calendar):
        is_today = day_info.date == today
        bg = _BATIK_HIGHLIGHT if is_today else _BATIK_CARD
        fg = "#2C1810" if is_today else _BATIK_TEXT
        week_cols[i].markdown(
            f"""<div style="background:{bg}; border:1px solid {_BATIK_BORDER};
                border-radius:5px; padding:5px 2px; text-align:center; color:{fg};
                font-size:0.72em; {'font-weight:bold;' if is_today else ''}">
              <div>{day_names_cn[i]}</div>
              <div>{day_info.date.strftime('%m/%d')}</div>
              <div style="font-size:0.85em;">{day_info.saptawara[:4]}</div>
              <div style="font-size:0.85em;">{day_info.pancawara}</div>
              <div style="color:{'#2C1810' if is_today else _BATIK_ACCENT};">{day_info.neptu}</div>
              {'<div>✨</div>' if day_info.is_special else ''}
            </div>""",
            unsafe_allow_html=True,
        )
