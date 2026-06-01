"""
astro/shaozi/renderer.py — 邵子神數 Streamlit 渲染器

提供邵子神數起盤結果的 Streamlit 介面渲染，
包含：條文卡片、四柱配卦表、條文庫瀏覽。
"""

from __future__ import annotations

import streamlit as st
from typing import TYPE_CHECKING

from astro.i18n import auto_cn, get_lang

if TYPE_CHECKING:
    from astro.shaozi.calculator import ShaoziResult, ShaoziShenShu

# 主色調（邵子神數：深藍紫星空配色，有別於鐵板神數橙色）
_COLORS = {
    "accent":      "#7C5CBF",   # 紫
    "accent_light": "#A989E0",  # 淺紫
    "gold":        "#C9A84C",   # 金
    "green":       "#5BD4A0",   # 翠
    "bg_card":     "rgba(124,92,191,0.10)",
    "bg_card_border": "rgba(124,92,191,0.35)",
    "text_dim":    "#9090b0",
    "text_main":   "#e8e0ff",
    "text_verse":  "#d0c8f0",
}


# ============================================================================
# 主命盤渲染
# ============================================================================

def render_shaozi_result(result: "ShaoziResult") -> None:
    """渲染邵子神數起盤結果（Streamlit）"""
    lang = get_lang()
    is_en = (lang == "en")

    _render_header_card(result, is_en)
    _render_digit_cards(result, is_en)
    st.divider()
    _render_tiaowen_card(result, is_en)
    st.divider()
    _render_ganzhi_table(result, is_en)


def _render_header_card(result: "ShaoziResult", is_en: bool) -> None:
    title = "Shao Zi Shen Shu" if is_en else auto_cn("邵子神數")
    subtitle = "Shaozi Divine Numbers · Shao Kangjie" if is_en else auto_cn("邵康節神數 · 洛陽派")
    coll_label = "Collection" if is_en else auto_cn("集")
    gua_label = "Hexagram" if is_en else auto_cn("卦")

    c = _COLORS
    st.markdown(
        f"""
<div style="
    background:linear-gradient(135deg,#120822 0%,#0d1a30 100%);
    border:1px solid {c['bg_card_border']};
    border-radius:16px;
    padding:24px 22px 20px 22px;
    margin-bottom:16px;
    text-align:center;
">
  <div style="font-size:42px;margin-bottom:8px;">🔯</div>
  <div style="font-size:20px;font-weight:700;color:{c['accent_light']};letter-spacing:3px;margin-bottom:4px;">
    {title}
  </div>
  <div style="font-size:12px;color:{c['text_dim']};letter-spacing:1.5px;margin-bottom:14px;">
    {subtitle}
  </div>
  <div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;">
    <div style="background:{c['bg_card']};border:1px solid {c['bg_card_border']};
         border-radius:10px;padding:8px 18px;font-size:13px;color:{c['accent_light']};">
      {coll_label}：{auto_cn(result.collection)}
    </div>
    <div style="background:rgba(201,168,76,0.10);border:1px solid rgba(201,168,76,0.3);
         border-radius:10px;padding:8px 18px;font-size:13px;color:{c['gold']};">
      {gua_label}：{result.gua_name or "—"}
    </div>
  </div>
</div>""",
        unsafe_allow_html=True,
    )


def _render_digit_cards(result: "ShaoziResult", is_en: bool) -> None:
    c = _COLORS
    id_label    = "Divine Number"  if is_en else auto_cn("神數號碼")
    year_label  = "Year Palace"    if is_en else auto_cn("年位（集）")
    month_label = "Month Palace"   if is_en else auto_cn("月位")
    day_label   = "Day Palace"     if is_en else auto_cn("日位")
    hour_label  = "Hour Palace"    if is_en else auto_cn("時位")
    heluo_label = "He Luo (Year)"  if is_en else auto_cn("河洛（年）")
    nayin_label = "NaYin (Day)"    if is_en else auto_cn("納音（日）")

    st.markdown(
        f"""
<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:4px;">
  <div style="flex:1 1 160px;min-width:140px;
      background:{c['bg_card']};border:1px solid {c['bg_card_border']};
      border-radius:12px;padding:12px 14px;text-align:center;">
    <div style="font-size:11px;color:{c['text_dim']};margin-bottom:4px;">{id_label}</div>
    <div style="font-size:28px;font-weight:700;color:{c['accent_light']};letter-spacing:5px;">
      {result.tiaowen_id}
    </div>
  </div>
  <div style="flex:1 1 80px;min-width:80px;
      background:{c['bg_card']};border:1px solid {c['bg_card_border']};
      border-radius:12px;padding:12px 14px;text-align:center;">
    <div style="font-size:11px;color:{c['text_dim']};margin-bottom:4px;">{year_label}</div>
    <div style="font-size:22px;font-weight:700;color:{c['accent_light']};">{result.year_digit}</div>
    <div style="font-size:11px;color:{c['text_dim']};margin-top:2px;">{auto_cn(result.gua_year)}</div>
  </div>
  <div style="flex:1 1 80px;min-width:80px;
      background:rgba(91,212,160,0.08);border:1px solid rgba(91,212,160,0.25);
      border-radius:12px;padding:12px 14px;text-align:center;">
    <div style="font-size:11px;color:{c['text_dim']};margin-bottom:4px;">{month_label}</div>
    <div style="font-size:22px;font-weight:700;color:{c['green']};">{result.month_digit}</div>
    <div style="font-size:11px;color:{c['text_dim']};margin-top:2px;">{auto_cn(result.gua_month)}</div>
  </div>
  <div style="flex:1 1 80px;min-width:80px;
      background:rgba(91,212,160,0.08);border:1px solid rgba(91,212,160,0.25);
      border-radius:12px;padding:12px 14px;text-align:center;">
    <div style="font-size:11px;color:{c['text_dim']};margin-bottom:4px;">{day_label}</div>
    <div style="font-size:22px;font-weight:700;color:{c['green']};">{result.day_digit}</div>
    <div style="font-size:11px;color:{c['text_dim']};margin-top:2px;">{auto_cn(result.gua_day)}</div>
  </div>
  <div style="flex:1 1 80px;min-width:80px;
      background:rgba(91,212,160,0.08);border:1px solid rgba(91,212,160,0.25);
      border-radius:12px;padding:12px 14px;text-align:center;">
    <div style="font-size:11px;color:{c['text_dim']};margin-bottom:4px;">{hour_label}</div>
    <div style="font-size:22px;font-weight:700;color:{c['green']};">{result.hour_digit}</div>
    <div style="font-size:11px;color:{c['text_dim']};margin-top:2px;">{auto_cn(result.gua_hour)}</div>
  </div>
  <div style="flex:1 1 100px;min-width:100px;
      background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.25);
      border-radius:12px;padding:12px 14px;text-align:center;">
    <div style="font-size:11px;color:{c['text_dim']};margin-bottom:4px;">{heluo_label}</div>
    <div style="font-size:20px;font-weight:700;color:{c['gold']};">{result.he_luo_year}</div>
  </div>
  <div style="flex:1 1 100px;min-width:100px;
      background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.25);
      border-radius:12px;padding:12px 14px;text-align:center;">
    <div style="font-size:11px;color:{c['text_dim']};margin-bottom:4px;">{nayin_label}</div>
    <div style="font-size:13px;font-weight:700;color:{c['gold']};">{auto_cn(result.nayin_day) or "—"}</div>
  </div>
</div>""",
        unsafe_allow_html=True,
    )


def _render_tiaowen_card(result: "ShaoziResult", is_en: bool) -> None:
    c = _COLORS
    verse_title = "Divine Verse" if is_en else auto_cn("🔯 邵子神數條文")
    st.markdown(f"**{verse_title}**")

    gua_badge = (
        f'<span style="background:rgba(201,168,76,0.15);border:1px solid rgba(201,168,76,0.4);'
        f'border-radius:6px;padding:2px 10px;font-size:12px;color:{c["gold"]};margin-right:8px;">'
        f'{auto_cn(result.gua_name)}</span>'
        if result.gua_name else ""
    )
    id_badge = (
        f'<span style="background:{c["bg_card"]};border:1px solid {c["bg_card_border"]};'
        f'border-radius:6px;padding:2px 10px;font-size:12px;color:{c["accent_light"]};">'
        f'#{result.tiaowen_id}</span>'
    )
    st.markdown(
        f'<div style="margin-bottom:10px;">{id_badge} {gua_badge}</div>',
        unsafe_allow_html=True,
    )

    # 條文逐句換行展示（以空格分隔四句）
    lines = result.tiaowen_text.split(" ") if " " in result.tiaowen_text else [result.tiaowen_text]
    verse_html = "<br>".join(f"　{line}" for line in lines if line)

    st.markdown(
        f'<div style="background:rgba(124,92,191,0.08);'
        f'border-left:4px solid {c["accent"]};'
        f'border-radius:0 12px 12px 0;'
        f'padding:16px 20px;font-size:16px;'
        f'color:{c["text_verse"]};line-height:2.0;letter-spacing:1px;">'
        f'{verse_html}</div>',
        unsafe_allow_html=True,
    )

    if result.note:
        st.caption(auto_cn(result.note))


def _render_ganzhi_table(result: "ShaoziResult", is_en: bool) -> None:
    title = "Four Pillars" if is_en else auto_cn("📊 四柱配卦")
    st.markdown(f"**{title}**")

    if is_en:
        rows = [
            {"Pillar": "Year", "Ganzhi": result.year_gz, "Gua": result.gua_year,
             "Digit": result.year_digit, "HeLuo": result.he_luo_year, "NaYin": result.nayin_year},
            {"Pillar": "Month", "Ganzhi": result.month_gz, "Gua": result.gua_month,
             "Digit": result.month_digit, "HeLuo": "—", "NaYin": "—"},
            {"Pillar": "Day", "Ganzhi": result.day_gz, "Gua": result.gua_day,
             "Digit": result.day_digit, "HeLuo": result.he_luo_day, "NaYin": result.nayin_day},
            {"Pillar": "Hour", "Ganzhi": result.hour_gz, "Gua": result.gua_hour,
             "Digit": result.hour_digit, "HeLuo": "—", "NaYin": "—"},
        ]
    else:
        rows = [
            {"柱": auto_cn("年"), "干支": result.year_gz, "配卦": auto_cn(result.gua_year),
             "位數": result.year_digit, "河洛": result.he_luo_year, "納音": auto_cn(result.nayin_year)},
            {"柱": auto_cn("月"), "干支": result.month_gz, "配卦": auto_cn(result.gua_month),
             "位數": result.month_digit, "河洛": "—", "納音": "—"},
            {"柱": auto_cn("日"), "干支": result.day_gz, "配卦": auto_cn(result.gua_day),
             "位數": result.day_digit, "河洛": result.he_luo_day, "納音": auto_cn(result.nayin_day)},
            {"柱": auto_cn("時"), "干支": result.hour_gz, "配卦": auto_cn(result.gua_hour),
             "位數": result.hour_digit, "河洛": "—", "納音": "—"},
        ]
    st.dataframe(rows, width="stretch", hide_index=True)


# ============================================================================
# 條文庫瀏覽器
# ============================================================================

def render_shaozi_tiaowen_browser() -> None:
    """邵子神數完整條文庫瀏覽"""
    from astro.shaozi.calculator import ShaoziTiaowenDatabase
    from astro.shaozi.constants import COLLECTIONS

    db = ShaoziTiaowenDatabase.get_instance()
    c = _COLORS

    st.markdown(f"**{auto_cn('📚 邵子神數條文庫')}**")
    st.caption(auto_cn(f"共 {db.count} 條條文"))

    col1, col2 = st.columns([1, 2])
    with col1:
        coll_options = ["全部"] + [f"{k} {v}" for k, v in COLLECTIONS.items()]
        selected_coll = st.selectbox(
            auto_cn("選擇集"),
            coll_options,
            key="shaozi_browser_coll",
        )
    with col2:
        search_kw = st.text_input(
            auto_cn("搜尋條文"),
            placeholder=auto_cn("輸入關鍵字…"),
            key="shaozi_browser_search",
        )

    all_entries = list(db.all().values())

    # Filter by collection
    if selected_coll != "全部":
        coll_digit = selected_coll.split(" ")[0]
        all_entries = [e for e in all_entries if e["id"].startswith(coll_digit)]

    # Filter by keyword
    if search_kw.strip():
        kw = search_kw.strip()
        all_entries = [e for e in all_entries if kw in e["text"] or kw in e["gua"]]

    st.caption(auto_cn(f"顯示 {len(all_entries)} 條"))

    # Paginate
    page_size = 20
    total_pages = max(1, (len(all_entries) + page_size - 1) // page_size)
    page = st.number_input(
        auto_cn("頁碼"),
        min_value=1, max_value=total_pages, value=1, step=1,
        key="shaozi_browser_page",
    )
    start = (page - 1) * page_size
    page_entries = all_entries[start: start + page_size]

    rows = [
        {
            auto_cn("條文號"): e["id"],
            auto_cn("卦"): auto_cn(e["gua"]),
            auto_cn("條文"): auto_cn(e["text"]),
        }
        for e in page_entries
    ]
    st.dataframe(rows, width="stretch", hide_index=True)


# ============================================================================
# 64鑰匙進階細調（shaozi_full_structure 整合）
# ============================================================================

def render_shaozi_64key_section(full_result: dict) -> None:
    """
    渲染邵子神數 64鑰匙進階細調結果。

    Parameters
    ----------
    full_result : dict
        由 astro.shaozi.shaozi_full_structure.ShaoziShenShu.cast_plate() 回傳的字典，
        包含 base_number、calculation、key 等欄位。
    """
    c = _COLORS
    lang = get_lang()
    is_en = (lang == "en")

    base_number = full_result.get("base_number", "—")
    gua = full_result.get("gua", "")
    calc = full_result.get("calculation", {})
    key_info = full_result.get("key")

    # ── 計算過程摘要 ──────────────────────────────────────────────────────────
    st.markdown(f"**{auto_cn('🧮 64鑰匙起數過程')}**" if not is_en else "**🧮 64-Key Calculation**")

    tg_total   = calc.get("天干總數", "—")
    dz_total   = calc.get("地支總數", "—")
    heluo      = calc.get("河洛數", "—")
    tian_gua   = calc.get("天數成卦", "—")
    di_gua_val = calc.get("地數成卦", "—")

    if is_en:
        calc_rows = [
            {"Item": "Stem Sum (天干總數)",   "Value": str(tg_total)},
            {"Item": "Branch Sum (地支總數)", "Value": str(dz_total)},
            {"Item": "He-Luo Number (河洛數)", "Value": str(heluo)},
            {"Item": "Heaven Gua (天數成卦)", "Value": str(tian_gua)},
            {"Item": "Earth Gua (地數成卦)",  "Value": str(di_gua_val)},
            {"Item": "Base Number (基礎數)",   "Value": str(base_number)},
            {"Item": "Gua (卦象)",             "Value": gua},
        ]
    else:
        calc_rows = [
            {auto_cn("項目"): auto_cn("天干總數"),  auto_cn("數值"): str(tg_total)},
            {auto_cn("項目"): auto_cn("地支總數"),  auto_cn("數值"): str(dz_total)},
            {auto_cn("項目"): auto_cn("河洛數"),    auto_cn("數值"): str(heluo)},
            {auto_cn("項目"): auto_cn("天數成卦"),  auto_cn("數值"): str(tian_gua)},
            {auto_cn("項目"): auto_cn("地數成卦"),  auto_cn("數值"): str(di_gua_val)},
            {auto_cn("項目"): auto_cn("基礎數"),    auto_cn("數值"): str(base_number)},
            {auto_cn("項目"): auto_cn("卦象"),      auto_cn("數值"): auto_cn(gua)},
        ]
    st.dataframe(calc_rows, width="stretch", hide_index=True)

    # ── 64鑰匙詳細資訊 ────────────────────────────────────────────────────────
    if not key_info:
        st.info(auto_cn(f"第 {base_number} 數暫無64鑰匙資料") if not is_en else f"No 64-Key data for number {base_number}")
        return

    key_name   = key_info.get("名稱", "")
    specials   = key_info.get("特殊事項", [])
    shichen_info = key_info.get("時辰資訊", "—")
    yunxian_info = key_info.get("運限資訊", "—")

    st.markdown(
        f"""
<div style="
    background:{c['bg_card']};
    border:1px solid {c['bg_card_border']};
    border-radius:14px;
    padding:16px 20px 14px 20px;
    margin:12px 0;
">
  <div style="font-size:11px;color:{c['text_dim']};margin-bottom:6px;">
    {'64-Key Number' if is_en else auto_cn('64鑰匙')} · {'No.' if is_en else '第'} {base_number} {'Key' if is_en else '數'}
  </div>
  <div style="font-size:17px;font-weight:700;color:{c['accent_light']};margin-bottom:10px;">
    {auto_cn(key_name)}
  </div>
  {'<div style="font-size:12px;color:' + c['text_dim'] + ';margin-bottom:6px;">' + ('Special Notes' if is_en else auto_cn('特殊事項')) + '</div>' if specials else ''}
  <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:4px;">
    {''.join(
        f'<span style="background:rgba(201,168,76,0.12);border:1px solid rgba(201,168,76,0.35);'
        f'border-radius:6px;padding:3px 10px;font-size:12px;color:{c["gold"]};">'
        f'{auto_cn(s)}</span>'
        for s in specials
    )}
  </div>
</div>""",
        unsafe_allow_html=True,
    )

    # ── 快速特殊事項指標 ──────────────────────────────────────────────────────
    flag_keys = [
        ("克妻", "Ke Qi"),
        ("過房", "Guo Fang"),
        ("填房", "Tian Fang"),
        ("貴子", "Gui Zi"),
        ("孤",   "Gu"),
    ]
    # build flag display
    flag_html_parts = []
    for (cn_label, en_label) in flag_keys:
        val = key_info.get(f"has_{cn_label}", False)
        if val:
            flag_html_parts.append(
                f'<span style="background:rgba(91,212,160,0.12);border:1px solid rgba(91,212,160,0.35);'
                f'border-radius:6px;padding:3px 10px;font-size:12px;color:{c["green"]};">✓ '
                f'{en_label if is_en else auto_cn(cn_label)}</span>'
            )
        else:
            flag_html_parts.append(
                f'<span style="background:rgba(144,144,176,0.08);border:1px solid rgba(144,144,176,0.2);'
                f'border-radius:6px;padding:3px 10px;font-size:12px;color:{c["text_dim"]};">✗ '
                f'{en_label if is_en else auto_cn(cn_label)}</span>'
            )

    if flag_html_parts:
        indicator_title = "Key Indicators" if is_en else auto_cn("命格指標")
        st.markdown(f"**{indicator_title}**")
        st.markdown(
            '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;">'
            + "".join(flag_html_parts)
            + "</div>",
            unsafe_allow_html=True,
        )

    # ── 時辰與運限資訊 ────────────────────────────────────────────────────────
    if shichen_info and shichen_info not in ("—", "無資料", "查無此類別"):
        shichen_title = "Hour Info" if is_en else auto_cn("時辰資訊")
        st.markdown(f"**{shichen_title}**")
        if isinstance(shichen_info, dict):
            shichen_rows = [{auto_cn("項目"): auto_cn(k), auto_cn("內容"): auto_cn(str(v))} for k, v in shichen_info.items()]
            st.dataframe(shichen_rows, width="stretch", hide_index=True)
        else:
            st.markdown(
                f'<div style="background:rgba(124,92,191,0.06);border-left:3px solid {c["accent"]}; '
                f'border-radius:0 8px 8px 0;padding:8px 14px;font-size:13px;color:{c["text_verse"]};">'
                f'{auto_cn(str(shichen_info))}</div>',
                unsafe_allow_html=True,
            )

    if yunxian_info and yunxian_info not in ("—", "無資料", "查無此類別"):
        yunxian_title = "Yun Xian (Major/Annual Cycles)" if is_en else auto_cn("運限資訊")
        st.markdown(f"**{yunxian_title}**")
        if isinstance(yunxian_info, dict):
            yunxian_rows = [{auto_cn("干支"): auto_cn(k), auto_cn("運勢"): auto_cn(str(v))} for k, v in yunxian_info.items()]
            st.dataframe(yunxian_rows, width="stretch", hide_index=True)
        else:
            st.markdown(
                f'<div style="background:rgba(201,168,76,0.06);border-left:3px solid {c["gold"]}; '
                f'border-radius:0 8px 8px 0;padding:8px 14px;font-size:13px;color:{c["text_verse"]};">'
                f'{auto_cn(str(yunxian_info))}</div>',
                unsafe_allow_html=True,
            )


# ============================================================================
# 不需起盤時的說明佔位卡
# ============================================================================

def render_shaozi_placeholder() -> None:
    """未輸入出生資料時顯示的說明卡"""
    c = _COLORS
    st.markdown(
        f"""
<div style="
    background:linear-gradient(135deg,#120822 0%,#0d1a30 100%);
    border:1px solid {c['bg_card_border']};
    border-radius:16px;
    padding:28px 24px 24px 24px;
    margin-bottom:20px;
    text-align:center;
">
  <div style="font-size:52px;margin-bottom:12px;">🔯</div>
  <div style="font-size:22px;font-weight:700;color:{c['accent_light']};letter-spacing:2px;margin-bottom:6px;">
    {auto_cn('邵子神數')}
  </div>
  <div style="font-size:12px;color:{c['text_dim']};margin-bottom:14px;letter-spacing:1px;">
    Shao Zi Shen Shu &middot; Shaozi Divine Numbers
  </div>
  <div style="font-size:13px;color:#8888aa;line-height:1.9;max-width:380px;margin:0 auto 18px auto;">
    {auto_cn('源自北宋邵雍（邵康節）易學體系')}<br>
    {auto_cn('洛書九宮配天干起集，後天八卦配卦取位')}<br>
    {auto_cn('四位數條文號，查閱命運詩讖')}<br>
    {auto_cn('與鐵板神數同源，各具獨立配卦體系')}
  </div>
  <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-bottom:18px;">
    <div style="background:{c['bg_card']};border:1px solid {c['bg_card_border']};
         border-radius:8px;padding:7px 13px;font-size:12px;color:{c['accent_light']};">
      {auto_cn('📅 輸入出生年月日時')}
    </div>
    <div style="background:{c['bg_card']};border:1px solid {c['bg_card_border']};
         border-radius:8px;padding:7px 13px;font-size:12px;color:{c['accent_light']};">
      {auto_cn('⚡ 一鍵起邵子神數')}
    </div>
    <div style="background:{c['bg_card']};border:1px solid {c['bg_card_border']};
         border-radius:8px;padding:7px 13px;font-size:12px;color:{c['accent_light']};">
      {auto_cn('📜 查閱命運條文')}
    </div>
  </div>
  <div style="
    display:inline-block;
    background:rgba(124,92,191,0.15);
    border:1px solid rgba(124,92,191,0.4);
    border-radius:8px;
    padding:8px 20px;
    font-size:13px;
    color:#b89fff;
  ">{auto_cn('👈 請在左側填寫出生年月日時，即可起盤')}</div>
</div>""",
        unsafe_allow_html=True,
    )
