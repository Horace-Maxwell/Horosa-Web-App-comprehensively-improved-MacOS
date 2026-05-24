"""
土亭數渲染器 (Tojeong Shu Renderer)

響應式命盤渲染 — 先圖後字，手機優先
包含：
- 四柱 SVG 視覺圖（先圖）
- 格局代碼視覺展示
- 三元/卞元斷語卡片
- 計算過程（可折疊）
- 129 格局斷語（三元/卞元）
"""

import streamlit as st
from typing import Dict, Any, Optional


# ── 韓式配色方案 ─────────────────────────────────────────────
_KR_RED    = "#CD2E3A"   # 韓國傳統紅
_KR_BLUE   = "#003478"   # 韓國傳統藍
_KR_GOLD   = "#C9A84C"   # 朝鮮金色
_KR_GOLD2  = "#EAB308"   # 亮金
_BG_DARK   = "#0d1420"   # 深夜藍背景
_BG_CARD   = "#1a1030"   # 柱子卡底色
_TEXT_DIM  = "#8888aa"   # 淡化文字
_TEXT_SIL  = "#c8c8e8"   # 銀白文字


def _pillar_svg(cx: float, label: str, tg: str, dz: str,
                shi_val: Any, fa_val: Any, prod_val: Any) -> str:
    """生成單柱 SVG 群組（以中心 x 座標定位）"""
    _cjk_font = "'Noto Serif TC','Noto Serif SC','Source Han Serif','SimSun',serif"
    w, h = 78, 220
    x0 = cx - w / 2
    return f"""
  <g transform="translate({x0:.1f}, 82)">
    <rect width="{w}" height="{h}" rx="10"
          fill="{_BG_CARD}" stroke="{_KR_GOLD}" stroke-width="1.2" opacity="0.95"/>
    <!-- 柱標籤 -->
    <text x="{w/2:.1f}" y="22" text-anchor="middle"
          font-family="{_cjk_font}" font-size="13" font-weight="bold"
          fill="{_KR_RED}">{label}</text>
    <line x1="8" y1="30" x2="{w-8:.0f}" y2="30"
          stroke="{_KR_GOLD}" stroke-width="0.6" opacity="0.5"/>
    <!-- 天干 -->
    <text x="{w/2:.1f}" y="85" text-anchor="middle"
          font-family="{_cjk_font}" font-size="46" font-weight="bold"
          fill="#FFFFFF">{tg}</text>
    <!-- 地支 -->
    <text x="{w/2:.1f}" y="142" text-anchor="middle"
          font-family="{_cjk_font}" font-size="46" font-weight="bold"
          fill="{_KR_GOLD2}">{dz}</text>
    <!-- 數字行 -->
    <line x1="8" y1="154" x2="{w-8:.0f}" y2="154"
          stroke="{_KR_GOLD}" stroke-width="0.5" opacity="0.35"/>
    <text x="{w/2:.1f}" y="170" text-anchor="middle"
          font-family="monospace" font-size="10" fill="{_TEXT_DIM}">&#x5BE6; {shi_val}</text>
    <text x="{w/2:.1f}" y="184" text-anchor="middle"
          font-family="monospace" font-size="10" fill="{_TEXT_DIM}">&#x6CD5; {fa_val}</text>
    <text x="{w/2:.1f}" y="200" text-anchor="middle"
          font-family="monospace" font-size="11" font-weight="bold"
          fill="{_KR_GOLD}">&#xD7; {prod_val}</text>
  </g>"""


def _build_tojeong_svg(four_pillars: Dict, calculation: Dict,
                       pattern_name: str, code: str,
                       birth_label: str, yuan: str) -> str:
    """
    生成完整土亭數四柱 SVG 命盤

    - viewBox 480×360，width="100%" 自動縮放至手機寬度
    - 四柱等間距排列，天干白字 / 地支金字
    - 底部顯示格局代碼
    """
    shi  = calculation.get("shi",  [0, 0, 0, 0])
    fa   = calculation.get("fa",   [0, 0, 0, 0])
    prod = calculation.get("products", [0, 0, 0, 0])

    gz_keys  = ["year_gz", "month_gz", "day_gz", "hour_gz"]
    labels   = ["年柱", "月柱", "日柱", "時柱"]
    pillars  = [four_pillars.get(k, "??") for k in gz_keys]
    tg_list  = [p[0] if len(p) > 0 else "?" for p in pillars]
    dz_list  = [p[1] if len(p) > 1 else "?" for p in pillars]

    # 四柱橫向均分（480px 寬，兩邊各留 20px）
    vw = 480
    pad = 20
    step = (vw - 2 * pad) / 4
    cx_list = [pad + step * i + step / 2 for i in range(4)]

    pillar_svgs = "".join(
        _pillar_svg(cx_list[i], labels[i], tg_list[i], dz_list[i],
                    shi[i] if i < len(shi) else "?",
                    fa[i]  if i < len(fa)  else "?",
                    prod[i] if i < len(prod) else "?")
        for i in range(4)
    )

    # 格局代碼文字（去空格，每位間隔顯示）
    code_display = "  ".join(str(c) for c in str(code)) if code else "—"

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {vw} 400"
     style="width:100%;max-width:540px;display:block;margin:0 auto;">
  <defs>
    <linearGradient id="tj_bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#0f1e35"/>
      <stop offset="100%" stop-color="#1a0d28"/>
    </linearGradient>
    <linearGradient id="tj_gold_h" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="{_KR_GOLD}"/>
      <stop offset="50%"  stop-color="{_KR_GOLD2}"/>
      <stop offset="100%" stop-color="{_KR_GOLD}"/>
    </linearGradient>
  </defs>

  <!-- 背景 -->
  <rect width="{vw}" height="400" fill="url(#tj_bg)" rx="14"/>
  <!-- 外框 -->
  <rect x="2" y="2" width="{vw-4}" height="396"
        fill="none" stroke="{_KR_GOLD}" stroke-width="1.2" rx="12" opacity="0.45"/>

  <!-- 頂部裝飾線 -->
  <line x1="{pad}" y1="76" x2="{vw-pad}" y2="76"
        stroke="url(#tj_gold_h)" stroke-width="0.8" opacity="0.6"/>

  <!-- 主標題裝飾菱形 -->
  <polygon points="{vw/2:.0f},18 {vw/2-8:.0f},28 {vw/2:.0f},38 {vw/2+8:.0f},28"
           fill="none" stroke="{_KR_GOLD2}" stroke-width="1.2" opacity="0.7"/>
  <circle cx="{vw/2:.0f}" cy="28" r="3" fill="{_KR_GOLD2}" opacity="0.9"/>

  <!-- 主標題 -->
  <text x="{vw/2:.0f}" y="54" text-anchor="middle"
        font-family="'Noto Serif TC','Noto Serif SC','Source Han Serif','SimSun',serif"
        font-size="17" font-weight="bold"
        fill="{_KR_GOLD2}">&#x571F;&#x4EAD;&#x6578;&#x547D;&#x76E4;</text>

  <!-- 出生資訊 -->
  <text x="{vw/2:.0f}" y="68" text-anchor="middle"
        font-family="'Noto Serif TC','Noto Serif SC','Source Han Serif','SimSun',serif"
        font-size="11" fill="{_TEXT_SIL}">{birth_label}</text>

  <!-- 四柱 -->
  {pillar_svgs}

  <!-- 底部分隔 -->
  <line x1="{pad}" y1="318" x2="{vw-pad}" y2="318"
        stroke="url(#tj_gold_h)" stroke-width="0.8" opacity="0.5"/>

  <!-- 格局代碼標籤 -->
  <text x="{vw/2:.0f}" y="339" text-anchor="middle"
        font-family="'Noto Serif TC','Noto Serif SC','SimSun',serif"
        font-size="12" fill="{_TEXT_DIM}">&#x683C;&#x5C40;&#x4EE3;&#x78BC;</text>

  <!-- 格局代碼值 -->
  <text x="{vw/2:.0f}" y="374" text-anchor="middle"
        font-family="monospace" font-size="28" font-weight="bold"
        letter-spacing="6" fill="{_KR_GOLD2}">{code_display}</text>

  <!-- 三元標籤 (右下) -->
  <text x="{vw - pad}" y="393" text-anchor="end"
        font-family="'Noto Serif TC','Noto Serif SC','SimSun',serif"
        font-size="10" fill="{_KR_GOLD}" opacity="0.8">{yuan}</text>
</svg>"""


def _yuan_card_html(yuan_label: str, text: str,
                    is_active: bool, is_female_extra: bool = False) -> str:
    """生成單個三元斷語卡 HTML"""
    if is_active:
        border  = f"2px solid {_KR_GOLD2}"
        bg      = "rgba(201,168,76,0.12)"
        label_c = _KR_GOLD2
        badge   = f'<span style="background:{_KR_GOLD2};color:#1a1030;font-size:10px;padding:2px 7px;border-radius:10px;font-weight:700;margin-left:6px;">當前</span>'
    elif is_female_extra:
        border  = f"2px solid {_KR_BLUE}"
        bg      = "rgba(0,52,120,0.15)"
        label_c = "#6699cc"
        badge   = ""
    else:
        border  = f"1px solid rgba(201,168,76,0.25)"
        bg      = "rgba(255,255,255,0.03)"
        label_c = _TEXT_SIL
        badge   = ""

    text_html = (
        f'<p style="margin:8px 0 0 0;font-size:14px;line-height:1.7;color:#d0d0e8;">{text}</p>'
        if text else
        f'<p style="margin:8px 0 0 0;font-size:13px;color:{_TEXT_DIM};font-style:italic;">暫無斷語</p>'
    )
    return f"""<div style="
        background:{bg};
        border:{border};
        border-radius:12px;
        padding:14px 16px;
        margin-bottom:12px;
        box-sizing:border-box;
    ">
      <div style="font-size:15px;font-weight:700;color:{label_c};">{yuan_label}{badge}</div>
      {text_html}
    </div>"""


def _format_birth_label(birth_info: Dict[str, Any], yuan: str) -> str:
    """格式化出生資訊標籤（處理缺失值）"""
    year  = birth_info.get("year",  "?")
    month = birth_info.get("month", "?")
    day   = birth_info.get("day",   "?")
    hour  = birth_info.get("hour",  "?")
    gender_ch = "男" if birth_info.get("gender") != "female" else "女"
    try:
        m_str = f"{int(month):02d}"
        d_str = f"{int(day):02d}"
    except (TypeError, ValueError):
        m_str = str(month)
        d_str = str(day)
    return f"{year}年{m_str}月{d_str}日  {hour}時  {gender_ch}命  {yuan}"


def render_tojeong_chart(chart: Dict[str, Any],
                         after_chart_hook: Optional[callable] = None):
    """
    渲染土亭數命盤（先圖後字，手機優先）

    參數：
    - chart: compute_tojeong_chart() 返回的命盤數據
    - after_chart_hook: 渲染完成後的回調函數（用於 AI 按鈕等）
    """
    import streamlit.components.v1 as components

    birth_info  = chart.get("birth_info", {})
    four_pillars = chart.get("four_pillars", {})
    calculation  = chart.get("calculation", {})
    pattern      = chart.get("pattern")
    yuan         = chart.get("yuan", "上元")

    is_male   = birth_info.get("gender") != "female"
    birth_label = _format_birth_label(birth_info, yuan)

    pattern_name = "未知格局"
    if pattern:
        pattern_name = pattern.get("name", "未知格局")

    code = calculation.get("code", "")

    # ── ① SVG 命盤圖（先圖）─────────────────────────────────
    svg_html = _build_tojeong_svg(
        four_pillars=four_pillars,
        calculation=calculation,
        pattern_name=pattern_name,
        code=code,
        birth_label=birth_label,
        yuan=yuan,
    )
    # 使用 components.html 渲染 SVG，避免 Streamlit markdown 淨化器剝除 SVG defs/gradient 和 style 屬性
    html_doc = f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ background:transparent; overflow:hidden; }}
svg {{ width:100%; height:auto; display:block; max-width:540px; margin:0 auto; }}
</style>
</head><body>{svg_html}</body></html>"""
    components.html(html_doc, height=430, scrolling=False)

    # ── ② 格局名稱橫幅 ──────────────────────────────────────
    status     = pattern.get("status", "unknown") if pattern else "unknown"
    status_map = {
        "complete":    ("✅ 完整格局", _KR_GOLD2),
        "partial":     ("⚠️ 部分斷語", "#f59e0b"),
        "missing":     ("❌ 待補完格局", _KR_RED),
        "approximate": ("ℹ️ 近似格局", "#60a5fa"),
    }
    status_label, status_color = status_map.get(status, ("", _TEXT_DIM))

    if pattern:
        st.markdown(
            f"""<div style="
                text-align:center;
                background:linear-gradient(135deg,rgba(205,46,58,0.18),rgba(0,52,120,0.18));
                border:1px solid rgba(201,168,76,0.4);
                border-radius:12px;
                padding:14px 20px;
                margin:0 0 16px 0;
            ">
              <div style="font-size:20px;font-weight:700;color:{_KR_GOLD2};
                          letter-spacing:2px;margin-bottom:6px;">
                &#x1F4DC; {pattern_name}
              </div>
              <div style="font-size:13px;color:{status_color};">{status_label}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.warning("❌ 未找到對應格局")

    # ── ③ 三元斷語卡片（後字）──────────────────────────────
    st.markdown(
        f'<div style="font-size:15px;font-weight:600;color:{_TEXT_SIL};'
        f'margin:0 0 10px 0;">&#x1F4D6; 格局斷語</div>',
        unsafe_allow_html=True,
    )

    yuan_labels = ["上元", "中元", "下元"]
    cards_html  = ""
    for yl in yuan_labels:
        text  = pattern.get(yl, "") if pattern else ""
        cards_html += _yuan_card_html(
            yuan_label=yl,
            text=text,
            is_active=(yl == yuan),
        )

    # 卞元（女命）
    if not is_male:
        bian_text = pattern.get("卞元", "") if pattern else ""
        cards_html += _yuan_card_html(
            yuan_label="卞元（女命）",
            text=bian_text,
            is_active=False,
            is_female_extra=True,
        )

    st.markdown(
        f'<div style="width:100%;">{cards_html}</div>',
        unsafe_allow_html=True,
    )

    # ── ④ 計算過程（可折疊）────────────────────────────────
    with st.expander("🔢 計算過程詳情"):
        shi  = calculation.get("shi",      [])
        fa   = calculation.get("fa",       [])
        prod = calculation.get("products", [])

        labels = ["年", "月", "日", "時"]
        rows   = "".join(
            f"<tr>"
            f"<td style='padding:8px 14px;font-weight:700;color:{_KR_GOLD};'>{labels[i]}</td>"
            f"<td style='padding:8px 14px;color:{_TEXT_SIL};'>{shi[i] if i < len(shi) else '—'}</td>"
            f"<td style='padding:8px 14px;color:{_TEXT_SIL};'>{fa[i] if i < len(fa) else '—'}</td>"
            f"<td style='padding:8px 14px;font-weight:700;color:{_KR_GOLD2};'>"
            f"  {prod[i] if i < len(prod) else '—'}"
            f"</td>"
            f"</tr>"
            for i in range(4)
        )
        table_html = f"""
        <div style="overflow-x:auto;">
          <table style="width:100%;border-collapse:collapse;
                        background:rgba(255,255,255,0.04);border-radius:10px;
                        font-size:14px;">
            <thead>
              <tr style="border-bottom:1px solid rgba(201,168,76,0.3);">
                <th style="padding:8px 14px;color:{_KR_GOLD};text-align:left;">柱</th>
                <th style="padding:8px 14px;color:{_TEXT_DIM};text-align:left;">先天數（實）</th>
                <th style="padding:8px 14px;color:{_TEXT_DIM};text-align:left;">後天數（法）</th>
                <th style="padding:8px 14px;color:{_TEXT_DIM};text-align:left;">乘積</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <p style="margin-top:12px;font-size:13px;color:{_TEXT_DIM};">
          格局代碼 ▸
          <span style="font-family:monospace;font-size:15px;font-weight:700;
                       color:{_KR_GOLD2};letter-spacing:4px;">&nbsp;{code}</span>
        </p>"""
        st.markdown(table_html, unsafe_allow_html=True)

    # ── ⑤ 土亭數簡介（可折疊）─────────────────────────────
    with st.expander("📖 土亭數簡介"):
        st.markdown("""
        **土亭數**（土亭子數）是朝鮮時代土亭李先生所創的占數系統。

        **核心算法**：
        1. **先天數**：甲己子午九、乙庚丑未八、丙辛寅申七、丁壬卯酉六、戊癸辰戌五、己亥四
           - 干順支逆，除十取零 → 置上為實
        2. **後天數**：壬子一、丁巳二、甲寅三、辛酉四、戊辰戊五、癸亥六、丙午七、乙卯八、庚申九、丑未十、己百
           - 順計干支，除百十取零 → 置下為法
        3. **位位相乘**：實 × 法，位位相乘
        4. **去首尾**：去首尾兩位，得格局代碼
        5. **查格局**：查 129 格局斷語

        **三元**：
        - 上元：冬至、小寒、大寒
        - 中元：春分、清明、穀雨
        - 下元：其他節氣

        **卞元**：女命專用，參考卞元斷語
        """)

    # ── ⑥ 回調鉤子（AI 按鈕等）────────────────────────────
    if after_chart_hook:
        after_chart_hook()


def render_tojeong_svg(chart: Dict[str, Any]) -> str:
    """
    生成土亭數命盤的純 SVG（供匯出使用）

    返回 SVG 字符串
    """
    four_pillars = chart.get("four_pillars", {})
    calculation  = chart.get("calculation",  {})
    pattern      = chart.get("pattern")
    yuan         = chart.get("yuan", "上元")
    birth_info   = chart.get("birth_info", {})

    pattern_name = "未知格局"
    if pattern:
        pattern_name = pattern.get("name", "未知格局")

    code = calculation.get("code", "")
    birth_label = _format_birth_label(birth_info, yuan)

    return _build_tojeong_svg(
        four_pillars=four_pillars,
        calculation=calculation,
        pattern_name=pattern_name,
        code=code,
        birth_label=birth_label,
        yuan=yuan,
    )
