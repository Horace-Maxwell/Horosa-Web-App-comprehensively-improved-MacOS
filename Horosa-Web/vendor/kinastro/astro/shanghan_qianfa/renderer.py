# -*- coding: utf-8 -*-
"""
astro/shanghan_qianfa/renderer.py — Streamlit UI for 傷寒鈐法

Renders a 5-tab interface:
  Tab 1: 六經辨證結果    — Six-Channel diagnosis
  Tab 2: 經方推薦        — Classical formula recommendations
  Tab 3: 預後轉歸        — Prognosis & transmission days
  Tab 4: 五運六氣對照    — Wu Yun Liu Qi context
  Tab 5: 與其他系統對照  — Cross-reference notes
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .calculator import ShanghanResult
from .constants import SIX_CHANNELS, SHANGHAN_FORMULAS
from astro.i18n import auto_cn, t

# ────────────────────────────────────────────────
# CSS — jade/herbal medicine theme
# ────────────────────────────────────────────────

_CSS = """
<style>
.sq-header {
    background: linear-gradient(135deg, #0a1a0a 0%, #1a3a1a 50%, #0d2b0d 100%);
    border-left: 5px solid #4CAF50;
    padding: 14px 20px;
    border-radius: 8px;
    margin-bottom: 16px;
}
.sq-header h2 { color: #81C784; margin: 0; font-size: 1.4em; }
.sq-header p  { color: #a5d6a7; margin: 4px 0 0 0; font-size: 0.9em; }

.sq-channel-card {
    background: linear-gradient(135deg, #0a1a0a 0%, #142814 100%);
    border: 2px solid #4CAF50;
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 14px;
}
.sq-channel-card h3 { color: #81C784; margin: 0 0 8px 0; font-size: 1.5em; }
.sq-channel-card .en { color: #a5d6a7; font-size: 0.9em; margin-bottom: 10px; }
.sq-channel-card .nature { color: #C5A03F; font-size: 1.0em; margin-bottom: 8px; }

.sq-gz-pill {
    display: inline-block;
    background: rgba(76, 175, 80, 0.15);
    border: 1px solid #4CAF50;
    border-radius: 20px;
    padding: 4px 14px;
    margin: 3px;
    color: #81C784;
    font-size: 1.05em;
    font-weight: bold;
}

.sq-symptom-list li { color: #c8e6c9; margin-bottom: 4px; }

.sq-step {
    background: rgba(76, 175, 80, 0.06);
    border-left: 3px solid #4CAF50;
    border-radius: 4px;
    padding: 6px 12px;
    margin-bottom: 6px;
    color: #a5d6a7;
    font-family: monospace;
    font-size: 0.9em;
}

.sq-formula-primary {
    background: linear-gradient(135deg, #1a3a1a 0%, #2a5a2a 100%);
    border: 2px solid #C5A03F;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.sq-formula-primary h4 { color: #C5A03F; margin: 0 0 6px 0; font-size: 1.3em; }
.sq-formula-primary p  { color: #d4b896; margin: 0; }

.sq-formula-secondary {
    background: rgba(76, 175, 80, 0.08);
    border: 1px solid #4CAF5066;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 8px;
}
.sq-formula-secondary h5 { color: #81C784; margin: 0 0 4px 0; }
.sq-formula-secondary p  { color: #a5d6a7; margin: 0; font-size: 0.9em; }

.sq-article {
    background: rgba(76, 175, 80, 0.05);
    border-left: 3px solid #C5A03F;
    border-radius: 4px;
    padding: 8px 14px;
    margin-bottom: 8px;
}
.sq-article .no  { color: #C5A03F; font-weight: bold; font-size: 0.85em; }
.sq-article .txt { color: #c8e6c9; font-size: 0.95em; margin-top: 2px; }

.sq-prognosis-card {
    background: rgba(76, 175, 80, 0.08);
    border: 1px solid #4CAF5066;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.sq-prognosis-card h4 { color: #81C784; margin: 0 0 6px 0; }
.sq-prognosis-card p  { color: #a5d6a7; margin: 0; }

.sq-wuyun-card {
    background: rgba(197, 160, 63, 0.06);
    border: 1px solid #C5A03F44;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.sq-wuyun-card h5 { color: #C5A03F; margin: 0 0 4px 0; }
.sq-wuyun-card p  { color: #d4b896; margin: 0; font-size: 0.92em; }

.sq-cross-card {
    background: rgba(76, 175, 80, 0.05);
    border: 1px solid #4CAF5033;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 8px;
}
.sq-cross-card h5 { color: #81C784; margin: 0 0 4px 0; }
.sq-cross-card p  { color: #a5d6a7; margin: 0; font-size: 0.9em; }

.sq-ref-note { color: #666; font-size: 0.78em; font-style: italic; }
</style>
"""


# ────────────────────────────────────────────────
# Render helpers
# ────────────────────────────────────────────────

def _header(result: ShanghanResult) -> None:
    channel = result.channel
    info = result.channel_info
    icon = info.get("icon", "🌿")
    en = info.get("en", "")
    nature = info.get("nature", "")
    st.markdown(f"""
<div class="sq-header">
  <h2>{icon} 傷寒鈐法 — {channel}</h2>
  <p>{en} ｜ {nature}</p>
</div>
""", unsafe_allow_html=True)


def _gz_pills(label: str, year_gz: str, month_gz: str, day_gz: str) -> None:
    st.markdown(
        f"**{label}：**"
        f'<span class="sq-gz-pill">年 {year_gz}</span>'
        f'<span class="sq-gz-pill">月 {month_gz}</span>'
        f'<span class="sq-gz-pill">日 {day_gz}</span>',
        unsafe_allow_html=True,
    )


# ────────────────────────────────────────────────
# Tab 1 — 六經辨證結果
# ────────────────────────────────────────────────

def _tab_diagnosis(result: ShanghanResult) -> None:
    channel = result.channel
    info = result.channel_info
    icon = info.get("icon", "🌿")
    color = info.get("color", "#4CAF50")

    st.markdown(f"""
<div class="sq-channel-card">
  <h3>{icon} {channel}病</h3>
  <div class="en">{info.get("en", "")}</div>
  <div class="nature">性質：{info.get("nature", "")}</div>
  <div>陰陽：<strong style="color:{color}">{info.get("yin_yang","")}</strong>
  ｜ 五行：<strong style="color:#C5A03F">{info.get("element","")}</strong>
  ｜ 臟腑：<strong style="color:#81C784">{" / ".join(info.get("organs",[]))}</strong></div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {auto_cn('出生干支', 'Birth Ganzhi')}")
        _gz_pills(
            auto_cn("出生", "Birth"),
            result.birth_year_gz,
            result.birth_month_gz,
            result.birth_day_gz,
        )
        if result.birth_date:
            st.caption(f"📅 {result.birth_date.strftime('%Y-%m-%d')}")

    with col2:
        st.markdown(f"#### {auto_cn('發病干支', 'Onset Ganzhi')}")
        _gz_pills(
            auto_cn("發病", "Onset"),
            result.onset_year_gz,
            result.onset_month_gz,
            result.onset_day_gz,
        )
        if result.onset_date:
            st.caption(f"📅 {result.onset_date.strftime('%Y-%m-%d')}")

    st.markdown("---")

    st.markdown(f"#### {auto_cn('主要症狀', 'Key Symptoms')}")
    symptoms = info.get("symptoms", [])
    if symptoms:
        st.markdown(
            "<ul class='sq-symptom-list'>"
            + "".join(f"<li>{s}</li>" for s in symptoms)
            + "</ul>",
            unsafe_allow_html=True,
        )

    st.markdown(f"**{auto_cn('辨證要點', 'Key Signs')}**：{info.get('key_signs', '')}")

    st.markdown("---")

    version_label = (
        auto_cn("普濟方（雙支合算法）", "Puji Fang (Double-Branch Method)")
        if result.method_version == "v1"
        else auto_cn("薛氏醫案（日支直接法）", "Xue's Medical Cases (Day-Branch Method)")
    )
    st.markdown(f"**{auto_cn('鈐法版本', 'Qianfa Version')}**：{version_label}")

    with st.expander(auto_cn("📋 鈐法推算步驟", "📋 Calculation Steps")):
        for i, step in enumerate(result.calc_steps, 1):
            st.markdown(
                f'<div class="sq-step">{i}. {step}</div>',
                unsafe_allow_html=True,
            )


# ────────────────────────────────────────────────
# Tab 2 — 經方推薦
# ────────────────────────────────────────────────

def _tab_formulas(result: ShanghanResult) -> None:
    st.markdown(f"### {auto_cn('主方', 'Primary Formula')}")

    primary = result.primary_formula
    primary_desc = result.formula_descriptions.get(primary, "")
    st.markdown(f"""
<div class="sq-formula-primary">
  <h4>✦ {primary}</h4>
  <p>{primary_desc}</p>
</div>
""", unsafe_allow_html=True)

    if result.secondary_formulas:
        st.markdown(f"### {auto_cn('備選方劑', 'Secondary Formulas')}")
        for formula in result.secondary_formulas:
            desc = result.formula_descriptions.get(formula, "")
            st.markdown(f"""
<div class="sq-formula-secondary">
  <h5>◈ {formula}</h5>
  <p>{desc}</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### {auto_cn('傷寒論相關條文', 'Shanghan Lun Articles')}")

    for article in result.articles:
        no = article.get("no", "")
        text = article.get("text", "")
        st.markdown(f"""
<div class="sq-article">
  <div class="no">第 {no} 條</div>
  <div class="txt">{text}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown(
        '<p class="sq-ref-note">方劑及條文出自張仲景《傷寒論》（漢），'
        '方藥應用需在專業醫師指導下進行。</p>',
        unsafe_allow_html=True,
    )


# ────────────────────────────────────────────────
# Tab 3 — 預後轉歸
# ────────────────────────────────────────────────

def _tab_prognosis(result: ShanghanResult) -> None:
    st.markdown(f"### {auto_cn('預後分析', 'Prognosis')}")

    st.markdown(f"""
<div class="sq-prognosis-card">
  <h4>📋 {result.channel}病 — 預後</h4>
  <p>{result.prognosis}</p>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"### {auto_cn('傳經日程（十二日）', 'Transmission Schedule (12 days)')}")
    st.caption(auto_cn(
        "依《傷寒論》第7條六經傳變規律，以發病日為第一日起算。",
        "Based on Shanghan Lun Article 7 six-channel transmission. Day 1 = onset date.",
    ))

    rows = []
    for td in result.transmission_days:
        rows.append({
            auto_cn("第幾日", "Day"): td["day"],
            auto_cn("日期", "Date"): td["date"],
            auto_cn("當值六經", "Channel"): td["icon"] + " " + td["channel"],
            auto_cn("英文", "English"): td["channel_en"],
            auto_cn("條文備注", "Note"): td["note"],
        })
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch")

    st.markdown("---")
    st.markdown(f"### {auto_cn('關鍵轉折點', 'Critical Turning Points')}")

    turning_points = [
        (3, auto_cn("三陽已過，即將入三陰，需防正虛邪陷。", "Three Yang passed; watch for Yin-stage progression.")),
        (6, auto_cn("六日一周，正邪相搏最激烈，厥陰病危。", "Day 6 cycle peak; Jueyin crisis — most critical.")),
        (7, auto_cn("七日更始，太陽病衰，若正氣足則自愈。", "Day 7 renewal; if Taiyang, spontaneous recovery likely.")),
        (12, auto_cn("十二日完整周期，陰盡陽復，邪氣漸退。", "Full 12-day cycle; Yin exhausted, Yang resurging.")),
    ]
    for day_n, note in turning_points:
        st.markdown(f"- **第 {day_n} 日**：{note}")


# ────────────────────────────────────────────────
# Tab 4 — 五運六氣對照
# ────────────────────────────────────────────────

def _tab_wuyun(result: ShanghanResult) -> None:
    ctx = result.wuyun_context
    st.markdown(f"### {auto_cn('五運六氣背景', 'Wu Yun Liu Qi Context')}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {auto_cn('出生年', 'Birth Year')}")
        if result.birth_year_gz:
            st.markdown(f"""
<div class="sq-wuyun-card">
  <h5>🌱 {result.birth_year_gz} 年</h5>
  <p>五運：{ctx.get("birth_yun", "—")}</p>
  <p>六氣：{ctx.get("birth_qi", "—")}</p>
  <p>相關六經：{ctx.get("birth_channel", "—")}</p>
</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"#### {auto_cn('發病年', 'Onset Year')}")
        if result.onset_year_gz:
            st.markdown(f"""
<div class="sq-wuyun-card">
  <h5>🍃 {result.onset_year_gz} 年</h5>
  <p>五運：{ctx.get("onset_yun", "—")}</p>
  <p>六氣：{ctx.get("onset_qi", "—")}</p>
  <p>相關六經：{ctx.get("onset_channel", "—")}</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.info(auto_cn(
        "💡 五運六氣可與本模組交叉分析，請使用「五運六氣」分頁獲取詳細推算。",
        "💡 For detailed Wu Yun Liu Qi analysis, switch to the 'Wu Yun Liu Qi' tab.",
    ))

    st.markdown(f"### {auto_cn('六氣與六經對應', 'Six Qi ↔ Six Channels')}")
    st.markdown(auto_cn("""
| 六氣 | 對應六經 | 主氣特點 |
|------|----------|---------|
| 厥陰風木 | 厥陰 | 春初，風氣主令 |
| 少陰君火 | 少陰 | 仲春，君火化氣 |
| 少陽相火 | 少陽 | 夏初，相火炎上 |
| 太陰濕土 | 太陰 | 長夏，濕氣重濁 |
| 陽明燥金 | 陽明 | 秋，燥氣肅殺 |
| 太陽寒水 | 太陽 | 冬，寒水凜冽 |
""", """
| Six Qi | Channel | Seasonal Quality |
|--------|---------|-----------------|
| Jueyin Wind-Wood | Jueyin | Early spring, wind |
| Shaoyin Monarch-Fire | Shaoyin | Mid-spring, fire |
| Shaoyang Minister-Fire | Shaoyang | Early summer, heat |
| Taiyin Damp-Earth | Taiyin | Late summer, dampness |
| Yangming Dry-Metal | Yangming | Autumn, dryness |
| Taiyang Cold-Water | Taiyang | Winter, cold |
"""))


# ────────────────────────────────────────────────
# Tab 5 — 與其他系統對照
# ────────────────────────────────────────────────

def _tab_cross_reference(result: ShanghanResult) -> None:
    channel = result.channel
    info = result.channel_info

    st.markdown(f"### {auto_cn('六經與其他系統對照', 'Cross-Reference with Other Systems')}")

    cross_refs = [
        {
            "system": auto_cn("醫學占星 (Medical Astrology)", "Medical Astrology"),
            "icon": "⚕️",
            "notes": auto_cn(
                f"六經{channel}對應體質特徵可與西方四液質（血液質/黃膽汁/黑膽汁/黏液質）"
                "及黃道人體部位進行交叉分析。",
                f"The {channel} channel constitution may be cross-referenced with "
                "Western humoral temperament and Zodiac Man body mappings.",
            ),
            "tab": "tab_medical_astrology",
        },
        {
            "system": auto_cn("五運六氣 (Wu Yun Liu Qi)", "Wu Yun Liu Qi"),
            "icon": "🌀",
            "notes": auto_cn(
                f"發病年的五運六氣可以揭示當前氣候邪氣之性質，"
                f"印證{channel}病的發生原因。",
                f"The Wu Yun Liu Qi of the onset year reveals the climatic pathogen, "
                f"confirming the {channel} channel pattern.",
            ),
            "tab": "tab_wuyunliuqi",
        },
        {
            "system": auto_cn("八字 (BaZi)", "BaZi (Four Pillars)"),
            "icon": "🏮",
            "notes": auto_cn(
                "八字命盤中的日主五行強弱及用神喜忌，"
                "可與傷寒六經體質進行深度對照分析。",
                "The BaZi day master element strength and useful gods "
                "can be deeply correlated with the Shanghan six-channel constitution.",
            ),
            "tab": "tab_chinese",
        },
        {
            "system": auto_cn("達摩一掌經 (Damo)", "Damo Palm Scripture"),
            "icon": "✋",
            "notes": auto_cn(
                "掌紋五行與傷寒六經的臟腑定位可相互印證，"
                "特別是手掌寒熱區域對應寒熱虛實的辨別。",
                "Palm element lines and Shanghan organ localizations can be "
                "cross-validated, especially for cold/heat pattern discernment.",
            ),
            "tab": "tab_damo",
        },
    ]

    for ref in cross_refs:
        st.markdown(f"""
<div class="sq-cross-card">
  <h5>{ref['icon']} {ref['system']}</h5>
  <p>{ref['notes']}</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### {auto_cn('六經體質類型', 'Six-Channel Constitution Types')}")
    st.caption(auto_cn(
        "不同六經體質傾向影響先天易患病傾向，可作為養生保健參考。",
        "Constitutional channel tendencies inform preventive health approaches.",
    ))

    for ch_name, ch_data in SIX_CHANNELS.items():
        icon = ch_data.get("icon", "")
        is_current = "**（當前辨證）**" if ch_name == channel else ""
        organs_str = " / ".join(ch_data.get("organs", []))
        st.markdown(
            f"{icon} **{ch_name}** {is_current} — "
            f"{ch_data.get('yin_yang', '')} | {ch_data.get('element', '')} | "
            f"臟腑：{organs_str}"
        )


# ────────────────────────────────────────────────
# Main render entry point
# ────────────────────────────────────────────────

def render_streamlit(result: ShanghanResult) -> None:
    """Render the Shanghan Qianfa result as a Streamlit multi-tab UI."""
    st.markdown(_CSS, unsafe_allow_html=True)

    _header(result)

    tab_labels = [
        auto_cn("🏥 六經辨證", "🏥 Six-Channel Dx"),
        auto_cn("🌿 經方推薦", "🌿 Formulas"),
        auto_cn("📅 預後轉歸", "📅 Prognosis"),
        auto_cn("🌀 五運六氣", "🌀 Wu Yun Liu Qi"),
        auto_cn("🔗 系統對照", "🔗 Cross-Reference"),
    ]

    tabs = st.tabs(tab_labels)

    with tabs[0]:
        _tab_diagnosis(result)

    with tabs[1]:
        _tab_formulas(result)

    with tabs[2]:
        _tab_prognosis(result)

    with tabs[3]:
        _tab_wuyun(result)

    with tabs[4]:
        _tab_cross_reference(result)
