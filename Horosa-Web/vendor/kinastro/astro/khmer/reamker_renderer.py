# -*- coding: utf-8 -*-
"""
Reamker Astrology Renderer - HTML + SVG Charts
高棉占星渲染器 - HTML + SVG 星盤圖
基於 Bizot 2013 TK480 手稿（Prochom Horasastra）
"""

from typing import Dict, List, Optional


def _html_escape(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def render_khmer_zodiac_svg(zodiac_data: Dict, language: str = "zh") -> str:
    """
    渲染高棉 12 生肖 SVG（緊湊橫幅格式）
    """
    kh = zodiac_data.get("kh", "ជូត")
    en = zodiac_data.get("en", "Rat")
    zh = zodiac_data.get("zh", "鼠")
    element_kh = zodiac_data.get("element", {}).get("kh", "ធាតុទឹក")
    element_zh = zodiac_data.get("element", {}).get("zh", "水")
    element_color = zodiac_data.get("element", {}).get("color", "#3b82f6")

    if language == "zh":
        zodiac_name = f"{zh} / {kh}"
        element_name = f"{element_zh}（{element_kh}）"
        label_zodiac = "生肖 / ឆ្នាំ"
        label_element = "五行元素"
    else:
        zodiac_name = f"{en} / {kh}"
        element_name = element_kh
        label_zodiac = "Zodiac / ឆ្នាំ"
        label_element = "Element"

    svg = f'''<svg viewBox="0 0 520 110" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:560px;display:block;margin:0 auto">
  <defs>
    <linearGradient id="zodBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f172a"/>
      <stop offset="100%" style="stop-color:#1e293b"/>
    </linearGradient>
  </defs>
  <rect width="520" height="110" rx="14" fill="url(#zodBg)"/>
  <rect x="4" y="4" width="512" height="102" rx="11" fill="none" stroke="{element_color}" stroke-width="2.5"/>

  <!-- 左側：生肖Khmer大字 -->
  <rect x="16" y="14" width="130" height="82" rx="8" fill="{element_color}" opacity="0.15"/>
  <text x="81" y="48" text-anchor="middle" font-family="Khmer OS, serif" font-size="30"
        fill="{element_color}" font-weight="bold">ឆ្នាំ {kh}</text>
  <text x="81" y="78" text-anchor="middle" font-family="Noto Serif, serif" font-size="13"
        fill="#94a3b8">{label_zodiac}</text>

  <!-- 中央分隔線 -->
  <line x1="158" y1="20" x2="158" y2="90" stroke="{element_color}" stroke-width="1" opacity="0.4"/>

  <!-- 中段：生肖名稱 -->
  <text x="280" y="45" text-anchor="middle" font-family="Noto Sans, Khmer OS, serif" font-size="22"
        fill="#ffffff" font-weight="bold">{_html_escape(zodiac_name)}</text>
  <text x="280" y="76" text-anchor="middle" font-family="Noto Sans, Khmer OS, serif" font-size="15"
        fill="{element_color}">{_html_escape(element_name)}</text>
  <text x="280" y="96" text-anchor="middle" font-family="Arial, sans-serif" font-size="11"
        fill="#64748b">{label_element}</text>

  <!-- 右側：裝飾圓點 -->
  <circle cx="455" cy="35" r="18" fill="{element_color}" opacity="0.2" stroke="{element_color}" stroke-width="2"/>
  <circle cx="455" cy="35" r="10" fill="{element_color}" opacity="0.5"/>
  <circle cx="455" cy="75" r="10" fill="{element_color}" opacity="0.2" stroke="{element_color}" stroke-width="1.5"/>
  <circle cx="490" cy="55" r="7"  fill="{element_color}" opacity="0.3"/>
</svg>'''

    return svg


def render_reamker_grid_html(reamker_data: Dict, language: str = "zh") -> str:
    """
    渲染 Reamker 32 格命盤（HTML 格式，支援 Khmer 文字換行）
    基於 Bizot TK480 / Prochom Horasastra 手稿
    """
    character = reamker_data.get("character", {})
    stage_zh = reamker_data.get("stage_zh", "童年期")
    stage_kh = reamker_data.get("stage_kh", "កុមារភាព")
    stage_en = reamker_data.get("stage_en", "Childhood")
    prophecy_zh = reamker_data.get("prophecy_zh", "預言內容")
    prophecy_kh = reamker_data.get("prophecy_kh", "ព្យាករណ៍")
    remedy_zh = reamker_data.get("remedy_zh", "化解儀式")
    remedy_kh = reamker_data.get("remedy_kh", "ពិធីសង្គ្រោះ")
    direction = reamker_data.get("direction", {})
    cell = reamker_data.get("cell", 0)
    age = reamker_data.get("age", 0)

    char_kh = character.get("kh", "ពិភេក")
    char_en = character.get("en", "Bibhek")
    char_zh = character.get("zh", "比布赫克")
    char_meaning = character.get("meaning", "")
    char_clan = character.get("clan", "human")

    clan_colors = {
        "god":    ("#fbbf24", "#78350f"),   # 神族 - 金色
        "human":  ("#60a5fa", "#1e3a8a"),   # 人族 - 藍色
        "yaksha": ("#f87171", "#7f1d1d"),   # 夜叉族 - 紅色
    }
    clan_color, clan_bg = clan_colors.get(char_clan, ("#60a5fa", "#1e3a8a"))

    clan_label_zh = {"god": "神族", "human": "人族", "yaksha": "夜叉族"}.get(char_clan, char_clan)

    if language == "zh":
        title = "羅摩衍那占星命盤"
        subtitle = "ហោរាសាស្ត្រ Reamker"
        stage_display = f"{stage_kh}（{stage_zh}）"
        dir_display = f"{direction.get('zh', '東北')}（{direction.get('kh', 'ឦសាន')}）"
        char_display = f"{char_kh}（{char_zh} / {char_en}）"
        prophecy_text = prophecy_zh
        remedy_text = remedy_zh
        cell_label = "格數"
        age_label = "年齡"
        clan_label = f"{clan_label_zh} / {char_clan.upper()}"
        stage_label = "人生階段 / ដំណាក់ជីវិត"
        dir_label = "吉祥方位 / ទិស"
        prophecy_label = "🔮 預言（ព្យាករណ៍）"
        remedy_label = "🙏 化解儀式（ពិធីសង្គ្រោះ）"
        source_note = "資料來源：Bizot TK480 手稿 · Prochom Horasastra"
    else:
        title = "Reamker Astrology Chart"
        subtitle = "ហោរាសាស្ត្រ Reamker"
        stage_display = f"{stage_kh} ({stage_en})"
        dir_display = f"{direction.get('en', 'Northeast')} ({direction.get('kh', 'ឦសាន')})"
        char_display = f"{char_kh} ({char_en})"
        prophecy_text = prophecy_kh
        remedy_text = remedy_kh
        cell_label = "Cell"
        age_label = "Age"
        clan_label = f"{char_clan.upper()}"
        stage_label = "Life Stage / ដំណាក់ជីវិត"
        dir_label = "Direction / ទិស"
        prophecy_label = "🔮 Prophecy (ព្យាករណ៍)"
        remedy_label = "🙏 Remedy Ritual (ពិធីសង្គ្រោះ)"
        source_note = "Source: Bizot TK480 · Prochom Horasastra"

    html = f'''<div style="
        font-family: 'Noto Sans', 'Khmer OS', Arial, sans-serif;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 2.5px solid {clan_color};
        border-radius: 18px;
        overflow: hidden;
        max-width: 560px;
        margin: 0 auto 8px;
    ">
      <!-- 標題區 -->
      <div style="
          background: linear-gradient(90deg, {clan_color}33 0%, {clan_bg}aa 100%);
          border-bottom: 2px solid {clan_color}66;
          padding: 14px 20px 10px;
          text-align: center;
      ">
        <div style="font-size:1.25rem;font-weight:700;color:#fff;letter-spacing:1px">{_html_escape(title)}</div>
        <div style="font-size:0.95rem;color:{clan_color};font-family:'Khmer OS',serif;margin-top:3px">{subtitle}</div>
      </div>

      <!-- 命主資訊 -->
      <div style="
          background: {clan_bg}55;
          border-bottom: 1px solid {clan_color}44;
          padding: 12px 20px;
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 10px;
      ">
        <div style="flex:1;min-width:180px">
          <div style="font-size:1.1rem;font-weight:700;color:{clan_color};font-family:'Khmer OS',serif">
            {_html_escape(char_display)}
          </div>
          <div style="font-size:0.82rem;color:#94a3b8;margin-top:2px">{_html_escape(char_meaning)} · {clan_label}</div>
        </div>
        <div style="display:flex;gap:16px;flex-wrap:wrap">
          <div style="text-align:center">
            <div style="font-size:1.3rem;font-weight:700;color:#fbbf24">{cell}</div>
            <div style="font-size:0.72rem;color:#64748b">{cell_label}</div>
          </div>
          <div style="text-align:center">
            <div style="font-size:1.3rem;font-weight:700;color:#fbbf24">{age}</div>
            <div style="font-size:0.72rem;color:#64748b">{age_label}</div>
          </div>
        </div>
      </div>

      <!-- 人生階段 & 方位 (兩欄) -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px;background:{clan_color}22;border-bottom:1px solid {clan_color}33">
        <div style="padding:10px 16px;background:#1e293b">
          <div style="font-size:0.75rem;color:#fbbf24;font-weight:600;margin-bottom:4px">{stage_label}</div>
          <div style="font-size:0.95rem;color:#fff;font-family:'Khmer OS','Noto Sans',serif;line-height:1.5">
            {_html_escape(stage_display)}
          </div>
        </div>
        <div style="padding:10px 16px;background:#1e293b">
          <div style="font-size:0.75rem;color:#fbbf24;font-weight:600;margin-bottom:4px">{dir_label}</div>
          <div style="font-size:0.95rem;color:#fff;font-family:'Khmer OS','Noto Sans',serif;line-height:1.5">
            {_html_escape(dir_display)}
          </div>
        </div>
      </div>

      <!-- 預言區 -->
      <div style="padding:14px 20px;border-bottom:1px solid {clan_color}33">
        <div style="font-size:0.85rem;font-weight:700;color:{clan_color};margin-bottom:8px">{prophecy_label}</div>
        <!-- Khmer 原典 -->
        <div style="
            font-family:'Khmer OS',serif;
            font-size:0.92rem;
            color:#fbbf24;
            line-height:1.85;
            padding:10px 14px;
            background:#0f172a88;
            border-left:3px solid {clan_color};
            border-radius:0 8px 8px 0;
            margin-bottom:8px;
            word-break:break-word;
        ">{_html_escape(prophecy_kh)}</div>
        <!-- 譯文 -->
        <div style="
            font-size:0.88rem;
            color:#cbd5e1;
            line-height:1.7;
            padding:8px 14px;
            background:#1e293b88;
            border-radius:8px;
            word-break:break-word;
        ">{_html_escape(prophecy_zh)}</div>
      </div>

      <!-- 化解儀式區 -->
      <div style="padding:14px 20px;border-bottom:1px solid #22c55e33">
        <div style="font-size:0.85rem;font-weight:700;color:#22c55e;margin-bottom:8px">{remedy_label}</div>
        <!-- Khmer 原典 -->
        <div style="
            font-family:'Khmer OS',serif;
            font-size:0.92rem;
            color:#86efac;
            line-height:1.85;
            padding:10px 14px;
            background:#0f172a88;
            border-left:3px solid #22c55e;
            border-radius:0 8px 8px 0;
            margin-bottom:8px;
            word-break:break-word;
        ">{_html_escape(remedy_kh)}</div>
        <!-- 譯文 -->
        <div style="
            font-size:0.88rem;
            color:#86efac;
            line-height:1.7;
            padding:8px 14px;
            background:#1e293b88;
            border-radius:8px;
            word-break:break-word;
        ">{_html_escape(remedy_zh)}</div>
      </div>

      <!-- 底部說明 -->
      <div style="padding:8px 20px;text-align:center">
        <span style="font-size:0.72rem;color:#475569">{source_note}</span>
      </div>
    </div>'''

    return html


def render_reamker_grid_svg(reamker_data: Dict, language: str = "zh") -> str:
    """向後兼容：返回 HTML 格式的命盤（原 SVG 版已改為 HTML 以支援 Khmer 文字換行）"""
    return render_reamker_grid_html(reamker_data, language)


def render_rama_arrows_svg(arrows_data: Dict, language: str = "zh") -> str:
    """
    渲染羅摩之箭（HTML 卡片格式）
    """
    arrow = arrows_data.get("arrow", 1)
    age = arrows_data.get("age", 0)
    data = arrows_data.get("data", {})

    arrow_kh = data.get("kh", "ព្រួញទី ១")
    arrow_en = data.get("en", "Arrow 1")
    arrow_zh = data.get("zh", "第一箭")
    interp_kh = data.get("interpretation_kh", "")
    interp_zh = data.get("interpretation_zh", "")
    remedy_kh = data.get("remedy_kh", "")
    remedy_zh = data.get("remedy_zh", "")

    good_arrows = [1, 3, 7, 8, 9]
    is_good = arrow in good_arrows
    color = "#22c55e" if is_good else "#ef4444"
    bg_color = "#052e16" if is_good else "#450a0a"

    if language == "zh":
        title = "羅摩之箭 / ព្រួញព្រះរាម"
        arrow_label = arrow_zh
        fortune_label = "吉兆 ✨" if is_good else "凶兆 ⚠️"
        age_label = f"年齡：{age} 歲"
        interp_text = interp_zh
        remedy_text = remedy_zh
    else:
        title = "Rama Arrows / ព្រួញព្រះរាម"
        arrow_label = arrow_en
        fortune_label = "Auspicious ✨" if is_good else "Inauspicious ⚠️"
        age_label = f"Age: {age}"
        interp_text = interp_kh
        remedy_text = remedy_kh

    html = f'''<div style="
        font-family:'Noto Sans','Khmer OS',Arial,sans-serif;
        background:linear-gradient(135deg,#0f172a,{bg_color});
        border:2px solid {color};
        border-radius:14px;
        overflow:hidden;
        max-width:560px;
        margin:0 auto 8px;
    ">
      <div style="display:flex;align-items:center;gap:14px;padding:12px 18px;border-bottom:1px solid {color}44">
        <!-- 箭頭圖示 (SVG) -->
        <svg viewBox="0 0 40 80" width="28" height="56" xmlns="http://www.w3.org/2000/svg">
          <polygon points="20,4 10,24 15,24 15,56 10,56 20,72 30,56 25,56 25,24 30,24"
                   fill="{color}" opacity="0.85"/>
        </svg>
        <div style="flex:1">
          <div style="font-size:0.75rem;color:#94a3b8;margin-bottom:2px">{title}</div>
          <div style="font-size:1.1rem;font-weight:700;color:{color};font-family:'Khmer OS',serif">
            {_html_escape(arrow_kh)}
          </div>
          <div style="font-size:0.9rem;color:#fff">{_html_escape(arrow_label)}</div>
        </div>
        <div style="text-align:center">
          <div style="font-size:1.8rem;font-weight:900;color:{color}">{arrow}</div>
          <div style="font-size:0.72rem;color:#94a3b8">{age_label}</div>
          <div style="font-size:0.8rem;font-weight:600;color:{color};margin-top:2px">{fortune_label}</div>
        </div>
      </div>
      {f"""
      <div style="padding:10px 18px;font-size:0.88rem;color:#d1fae5;line-height:1.65;border-bottom:1px solid {color}33;word-break:break-word">
        {_html_escape(interp_text)}
      </div>""" if interp_text else ""}
      {f"""
      <div style="padding:8px 18px 10px">
        <div style="font-size:0.72rem;color:{color};font-weight:600;margin-bottom:4px">化解 / ការដោះស្រាយ</div>
        <div style="font-size:0.85rem;color:#86efac;line-height:1.65;word-break:break-word">
          {_html_escape(remedy_zh)}<br>
          <span style="font-family:'Khmer OS',serif;color:#6ee7b7">{_html_escape(remedy_kh)}</span>
        </div>
      </div>""" if remedy_zh or remedy_kh else ""}
    </div>'''

    return html


def render_khmer_chart(chart_data: Dict, language: str = "zh") -> str:
    """
    渲染完整高棉占星報告（HTML + SVG 混合）
    """
    zodiac_svg = render_khmer_zodiac_svg(chart_data.get("zodiac", {}), language)
    reamker_html = render_reamker_grid_html(chart_data.get("reamker", {}), language)
    arrows_html = render_rama_arrows_svg(chart_data.get("rama_arrows", {}), language)

    note_zh = chart_data.get("note_zh", "")
    note_kh = chart_data.get("note_kh", "")

    note_block = ""
    if note_zh or note_kh:
        note_block = f'''<div style="
            margin-top:8px;
            padding:10px 16px;
            background:#1e293b;
            border-radius:10px;
            font-size:0.8rem;
            color:#64748b;
            max-width:560px;
            margin-left:auto;
            margin-right:auto;
            word-break:break-word;
        ">
          <span style="font-family:'Khmer OS',serif;color:#475569">{_html_escape(note_kh)}</span><br>
          {_html_escape(note_zh)}
        </div>'''

    html = f'''<div style="display:flex;flex-direction:column;gap:10px;padding:4px;box-sizing:border-box;width:100%">
  {zodiac_svg}
  {reamker_html}
  {arrows_html}
  {note_block}
</div>'''

    return html
