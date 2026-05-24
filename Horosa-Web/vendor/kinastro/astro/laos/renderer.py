"""Laos Horasat renderer.

提供老撾占星專屬的金色＋深藍宇宙風格渲染：
- 婆羅門占星輪 SVG（🌀）
- Streamlit 分頁展示（老撾日期、特殊年份、ສັງຄົມ、ສີກາດ）
"""

from __future__ import annotations

import math
from html import escape as html_escape
from typing import Any, Callable, Dict, List

from .calculator import LaoChart, chart_to_dict
from .data.symbols import BRAHMAN_WHEEL_SYMBOLS
from .data.sikarat import get_sikarat_by_hour

# BRAHMAN_WHEEL_SYMBOLS 中 0~6 分別代表七曜順序鍵值。
_WHEEL_SYMBOL_KEYS: Dict[str, str] = {
    "sun": "0",
    "moon": "1",
    "mercury": "2",
    "venus": "3",
    "mars": "4",
    "jupiter": "5",
    "saturn": "6",
}

# ==================== 中文翻譯對照表 ====================

_WEEKDAY_ZH: Dict[str, str] = {
    "ວັນອາທິດ": "星期日",
    "ວັນຈັນ": "星期一",
    "ວັນອັງຄານ": "星期二",
    "ວັນພຸດ": "星期三",
    "ວັນພະຫັດ": "星期四",
    "ວັນສຸກ": "星期五",
    "ວັນສົບ": "星期六",
}

_SEASON_ZH: Dict[str, str] = {
    "ລະດູໜາວ": "冷季（11–2月）",
    "ລະດູຝົນ": "雨季（5–10月）",
    "ລະດູແຫ້ງ": "旱季（3–4月）",
}

_SIKARAT_ZH: Dict[str, str] = {
    "ສີກາດລາວ": "老撾色嘎",
    "ສີກາດຝຣັ່ງ": "法國色嘎",
    "ສີກາດຈູລະ": "小色嘎",
    "ສີກາດມະຫາ": "大色嘎",
}

_SIKARAT_DESC_ZH: Dict[str, str] = {
    "ສີກາດລາວ": "老撾傳統時段，凌晨最吉，適合祈福供奉。",
    "ສີກາດຝຣັ່ງ": "法式色嘎，上午時段最旺，適合婚禮與求財。",
    "ສີກາດຈູລະ": "小色嘎，中午時段最吉，適合學業與祭祀。",
    "ສີກາດມະຫາ": "大色嘎，下午為佳，需避開凌晨危險時段。",
}

_ACTIVITY_ZH: Dict[str, str] = {
    "ການແຕ່ງງານ": "婚禮",
    "ການສ້າງເຮືອນ": "建房／動土",
    "ການເດີນທາງ": "出行",
    "ການເປີດກິຈະການ": "開業",
    "ການບູຊາບູຊາ": "祭祀／做功德",
}

_PLANET_ZH: Dict[str, str] = {
    "sun": "太陽",
    "moon": "月亮",
    "mars": "火星",
    "mercury": "水星",
    "jupiter": "木星",
    "venus": "金星",
    "saturn": "土星",
    "rahu": "羅睺",
    "ketu": "計都",
}

_PLANET_LAO: Dict[str, str] = {
    "sun": "ພຣະອາທິດ",
    "moon": "ພຣະຈັນ",
    "mars": "ພຣະອັງຄານ",
    "mercury": "ພຣະພຸດ",
    "jupiter": "ພຣະພະຫັດ",
    "venus": "ພຣະສຸກ",
    "saturn": "ພຣະເສົາ",
    "rahu": "ຣາຫູ",
    "ketu": "ເກດຸ",
}

_LAO_SIGNS_ZH: Dict[str, str] = {
    "ເມສ": "白羊座",
    "ພຶດສະພາ": "金牛座",
    "ມິຖຸນ": "雙子座",
    "ກະກົດ": "巨蟹座",
    "ສິງ": "獅子座",
    "ກັນຍາ": "處女座",
    "ຕຸລາ": "天秤座",
    "ພະຈິກ": "天蠍座",
    "ທະນູ": "射手座",
    "ມັງກອນ": "摩羯座",
    "ກຸມພາ": "水瓶座",
    "ມີນ": "雙魚座",
}

_SIGN_NAMES_LAO: List[str] = [
    "ເມສ", "ພຶດສະພາ", "ມິຖຸນ", "ກະກົດ", "ສິງ", "ກັນຍາ",
    "ຕຸລາ", "ພະຈິກ", "ທະນູ", "ມັງກອນ", "ກຸມພາ", "ມີນ",
]

_NUM_ZODIAC_SIGNS = len(_SIGN_NAMES_LAO)

_SIGN_STAR_LORD_KEYS: List[str] = [
    "mars", "venus", "mercury", "moon", "sun", "mercury",
    "venus", "mars", "jupiter", "saturn", "saturn", "jupiter",
]

_LAO_ZODIAC_ANIMALS: List[str] = [
    "🐀 ໜູ", "🐂 ງົວ", "🐅 ເສືອ", "🐇 ກະຕ່າຍ", "🐉 ພະຍານາກ", "🐍 ງູ",
    "🐎 ມ້າ", "🐐 ແບ້", "🐒 ລີງ", "🐓 ໄກ່", "🐕 ໝາ", "🐖 ໝູ",
]

_PLANET_TRAD_MEANING: Dict[str, str] = {
    "sun": "代表權威與生命力（待補完整傳統詮釋）",
    "moon": "代表情感與心性（待補完整傳統詮釋）",
    "mars": "代表行動與競爭（待補完整傳統詮釋）",
    "mercury": "代表學習與溝通（待補完整傳統詮釋）",
    "jupiter": "代表福德與智慧（待補完整傳統詮釋）",
    "venus": "代表人緣與財喜（待補完整傳統詮釋）",
    "saturn": "代表責任與考驗（待補完整傳統詮釋）",
    "rahu": "代表突變與執著（待補完整傳統詮釋）",
    "ketu": "代表出離與業力（待補完整傳統詮釋）",
}

_LAO_SVG_FONT_FAMILY = "Noto Sans Lao, Phetsarath OT, sans-serif"
_HOUSE_LABEL_Y_OFFSETS = (-8, 4, 16)
_PLANET_STAR_LABEL_OFFSET = 21
_CENTER_DEFAULT_STATUS = "ສະຖານະປະຈຸບັນ: ປົກກະຕິ"
_CENTER_SPECIAL_YEAR_TAG = "⚑ ປີພິເສດ"
_CENTER_NORMAL_YEAR_TAG = "◉ ປີປົກກະຕິ"
_TRADITIONAL_MEANING_PLACEHOLDER = "傳統義理待補"
_DEGREES_PER_SIGN = 30


def _zh(lao_text: str, mapping: Dict[str, str], fallback: str = "") -> str:
    """查詢 Lao→中文對照，找不到則回傳 fallback 或原文。"""
    return mapping.get(lao_text, fallback or lao_text)


def _polar(cx: float, cy: float, r: float, angle_deg: float) -> tuple[float, float]:
    """極座標轉平面座標。"""

    rad = math.radians(angle_deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def _star_lord_key(sign_index: int) -> str:
    """回傳星座對應星主（Star Lord）鍵值。"""

    if 0 <= sign_index < len(_SIGN_STAR_LORD_KEYS):
        return _SIGN_STAR_LORD_KEYS[sign_index]
    return "sun"


def _planet_symbol(key: str) -> str:
    """回傳行星符號，優先使用 symbols.py。"""

    if key in ("rahu", "ketu"):
        return "☊" if key == "rahu" else "☋"
    mapped = BRAHMAN_WHEEL_SYMBOLS.get(_WHEEL_SYMBOL_KEYS.get(key, ""), {})
    return mapped.get("unicode", "✶")


def _to_dict(chart: LaoChart | Dict[str, Any]) -> Dict[str, Any]:
    """統一 chart 輸入格式，支援 dataclass 與 dict。"""

    if isinstance(chart, LaoChart):
        return chart_to_dict(chart)
    if isinstance(chart, dict):
        return chart
    raise TypeError("chart 必須是 LaoChart 或 dict")


def build_lao_brahma_wheel_svg(chart: LaoChart | Dict[str, Any], *, size: int = 700) -> str:
    """建立老撾婆羅門占星輪 SVG。"""

    data = _to_dict(chart)
    planets = data.get("planets", [])
    lao_date = data.get("lao_date", {})
    sangkhom = data.get("sangkhom", {})
    special_year = data.get("special_year", {})

    cx = cy = size / 2
    r_outer = size * 0.43
    r_inner = size * 0.18
    r_planet = size * 0.34
    r_house_label = size * 0.382

    lao_houses = [
        "ເມສ", "ພຶດສະພາ", "ມິຖຸນ", "ກະກົດ", "ສິງ", "ກັນຍາ",
        "ຕຸລາ", "ພະຈິກ", "ທະນູ", "ມັງກອນ", "ກຸມພາ", "ມີນ",
    ]

    center_special = str(special_year.get("description", "")).strip()
    center_sangkhom = str(sangkhom.get("status", "")).strip()
    center_status = center_special or center_sangkhom or _CENTER_DEFAULT_STATUS
    center_year_tag = _CENTER_SPECIAL_YEAR_TAG if special_year.get("is_special") else _CENTER_NORMAL_YEAR_TAG

    parts = [
        '<div style="width:100%;max-width:820px;margin:0 auto;overflow-x:auto;">',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" style="width:100%;height:auto;display:block;">',
        "<defs>",
        "<radialGradient id='laoCosmic' cx='50%' cy='50%' r='60%'>",
        "<stop offset='0%' stop-color='#2b1b3f'/>",
        "<stop offset='100%' stop-color='#0c1025'/>",
        "</radialGradient>",
        "<linearGradient id='laoGold' x1='0%' y1='0%' x2='100%' y2='100%'>",
        "<stop offset='0%' stop-color='#f8e8b8'/>",
        "<stop offset='100%' stop-color='#be8e2d'/>",
        "</linearGradient>",
        "</defs>",
        f"<rect x='0' y='0' width='{size}' height='{size}' fill='url(#laoCosmic)' rx='20'/>",
        f"<circle cx='{cx}' cy='{cy}' r='{r_outer + 14}' fill='none' stroke='url(#laoGold)' stroke-width='3.0' opacity='0.95'/>",
        f"<circle cx='{cx}' cy='{cy}' r='{r_outer + 6}' fill='none' stroke='#9f7828' stroke-width='1.2' stroke-dasharray='2 6' opacity='0.8'/>",
        f"<circle cx='{cx}' cy='{cy}' r='{r_outer}' fill='none' stroke='#d6ac53' stroke-width='1.8' opacity='0.93'/>",
        f"<circle cx='{cx}' cy='{cy}' r='{r_inner}' fill='#14193a' stroke='#e0bc66' stroke-width='2.0'/>",
    ]

    # 12 宮分割（雙語：Lao + 中文）
    for i in range(12):
        angle = i * 30
        x1, y1 = _polar(cx, cy, r_inner, angle)
        x2, y2 = _polar(cx, cy, r_outer, angle)
        lx, ly = _polar(cx, cy, r_house_label, angle + 15)
        animal = _LAO_ZODIAC_ANIMALS[i]
        sign_lao = lao_houses[i]
        sign_zh = _LAO_SIGNS_ZH.get(sign_lao, "")
        offset_top, offset_mid, offset_bottom = _HOUSE_LABEL_Y_OFFSETS
        parts.append(
            f"<line x1='{x1:.2f}' y1='{y1:.2f}' x2='{x2:.2f}' y2='{y2:.2f}' stroke='#caa24b' stroke-width='1.25' opacity='0.9'/>"
        )
        parts.append(
            f"<text x='{lx:.2f}' y='{ly + offset_top:.2f}' text-anchor='middle' fill='#f6df9e' font-size='10' font-weight='bold' font-family='{_LAO_SVG_FONT_FAMILY}'>ຮືອນ {i + 1}</text>"
        )
        parts.append(
            f"<text x='{lx:.2f}' y='{ly + offset_mid:.2f}' text-anchor='middle' fill='#f0d187' font-size='10' font-family='{_LAO_SVG_FONT_FAMILY}'>{sign_lao}</text>"
        )
        parts.append(
            f"<text x='{lx:.2f}' y='{ly + offset_mid + 12:.2f}' text-anchor='middle' fill='#d0e8ff' font-size='9' font-family='sans-serif'>{sign_zh}</text>"
        )
        parts.append(
            f"<text x='{lx:.2f}' y='{ly + offset_bottom + 4:.2f}' text-anchor='middle' fill='#d7c7a0' font-size='9' font-family='{_LAO_SVG_FONT_FAMILY}'>{animal}</text>"
        )

    # 行星標記
    for p in planets:
        key = str(p.get("key", "")).lower()
        lon = float(p.get("longitude", 0.0))
        sign_idx = int(p.get("sign_index", int(lon // _DEGREES_PER_SIGN) % 12))
        house_no = int(p.get("house", 0))
        retrograde = bool(p.get("retrograde"))
        sign_lao = _SIGN_NAMES_LAO[sign_idx] if 0 <= sign_idx < _NUM_ZODIAC_SIGNS else "—"
        sign_animal = _LAO_ZODIAC_ANIMALS[sign_idx] if 0 <= sign_idx < _NUM_ZODIAC_SIGNS else "—"
        star_lord = _star_lord_key(sign_idx)
        star_lord_symbol = _planet_symbol(star_lord)
        star_lord_lao = _PLANET_LAO.get(star_lord, star_lord.upper())
        symbol = _planet_symbol(key)
        px, py = _polar(cx, cy, r_planet, lon)
        label_dx = _PLANET_STAR_LABEL_OFFSET if px < cx else -_PLANET_STAR_LABEL_OFFSET
        label_anchor = "start" if px < cx else "end"
        planet_name_zh = _PLANET_ZH.get(key, key.upper())
        planet_name_lao = _PLANET_LAO.get(key, key.upper())
        retro_text = "是 ℞" if retrograde else "否"
        meaning = _PLANET_TRAD_MEANING.get(key, _TRADITIONAL_MEANING_PLACEHOLDER)
        tooltip_title = html_escape(f"{planet_name_zh} · {planet_name_lao}")
        tooltip_desc = html_escape(
            f"度數/星座：{lon:.2f}° {sign_lao}；"
            f"宮位：第 {house_no} 宮；"
            f"逆行：{retro_text}；"
            f"星主：{star_lord_symbol} {_PLANET_ZH.get(star_lord, star_lord.upper())}；"
            f"生肖：{sign_animal}；"
            f"傳統意義：{meaning}"
        )
        parts.append("<g>")
        parts.append(f"<title>{tooltip_title}</title>")
        parts.append(f"<desc>{tooltip_desc}</desc>")
        parts.append(
            f"<circle cx='{px:.2f}' cy='{py:.2f}' r='13.2' fill='#120f2c' stroke='#efd18a' stroke-width='1.35'/>"
        )
        if retrograde:
            parts.append(
                f"<circle cx='{px:.2f}' cy='{py:.2f}' r='16.5' fill='none' stroke='#ff8173' stroke-width='1.8' opacity='0.95'/>"
            )
        parts.append(
            f"<text x='{px:.2f}' y='{py:.2f}' text-anchor='middle' dominant-baseline='middle' fill='#ffe8ad' font-size='16'>{symbol}</text>"
        )
        parts.append(
            f"<text x='{px + label_dx:.2f}' y='{py + 3:.2f}' text-anchor='{label_anchor}' fill='#f3d88f' font-size='9.4' font-family='{_LAO_SVG_FONT_FAMILY}'>ນາຍດາວ {star_lord_symbol} {star_lord_lao}</text>"
        )
        if retrograde:
            parts.append(
                f"<text x='{px + (12 if px < cx else -12):.2f}' y='{py - 12:.2f}' text-anchor='middle' fill='#ff9b90' font-size='10' font-weight='bold'>℞</text>"
            )
        parts.append(
            f"<text x='{px:.2f}' y='{py + 24:.2f}' text-anchor='middle' fill='#cdb784' font-size='8.8' font-family='{_LAO_SVG_FONT_FAMILY}'>{sign_animal}</text>"
        )
        parts.append("</g>")

    # 中心資訊（雙語）
    parts.extend(
        [
            f"<text x='{cx}' y='{cy - 32}' text-anchor='middle' fill='#f4de9a' font-size='24' font-family='Noto Sans Lao, sans-serif'>🌀</text>",
            f"<text x='{cx}' y='{cy - 10}' text-anchor='middle' fill='#f0d080' font-size='14' font-family='{_LAO_SVG_FONT_FAMILY}'>ໄທຣາສາດລາວ</text>",
            f"<text x='{cx}' y='{cy + 7}' text-anchor='middle' fill='#a8d4f5' font-size='11' font-family='sans-serif'>老撾占星</text>",
            f"<text x='{cx}' y='{cy + 23}' text-anchor='middle' fill='#d9bc76' font-size='10' font-family='{_LAO_SVG_FONT_FAMILY}'>{lao_date.get('full_lao_date', '')}</text>",
            f"<text x='{cx}' y='{cy + 38}' text-anchor='middle' fill='#ffdf8d' font-size='11' font-weight='bold' font-family='{_LAO_SVG_FONT_FAMILY}'>{html_escape(center_year_tag)}</text>",
            f"<text x='{cx}' y='{cy + 53}' text-anchor='middle' fill='#f5ce80' font-size='9' font-family='{_LAO_SVG_FONT_FAMILY}'>{html_escape(center_status)}</text>",
        ]
    )

    parts.append("</svg></div>")
    return "\n".join(parts)


def render_lao_horasat(
    chart: LaoChart | Dict[str, Any],
    *,
    lang: str = "zh",
    after_chart_hook: Callable[[], None] | None = None,
) -> None:
    """Streamlit 老撾占星頁面渲染。"""

    import streamlit as st

    _ = lang  # 保留未來多語擴充介面
    data = _to_dict(chart)
    lao_date = data.get("lao_date", {})
    special_year = data.get("special_year", {})
    sangkhom = data.get("sangkhom", {})
    sikarat = data.get("sikarat", {})

    st.markdown(
        """
        <style>
        .lao-cosmic-panel {
            background: linear-gradient(135deg, #09153a 0%, #0e1d4f 55%, #14235a 100%);
            border: 1px solid rgba(232, 193, 84, 0.55);
            border-radius: 14px;
            padding: 14px 16px;
            color: #f5df9d;
            box-shadow: 0 0 24px rgba(10, 20, 60, 0.42);
            margin-bottom: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="lao-cosmic-panel">
          <h3 style="margin:0;color:#f5df9d;">🇱🇦 老撾占星（ໄທຣາສາດລາວ）</h3>
          <p style="margin:6px 0 0 0;color:#d7b96e;">金色古典 × 深藍宇宙 · ປະຕິທິນ · ສັງຄົມ · ສີກາດ · ພຣະລໍ້ບຣາຮມັນ</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(build_lao_brahma_wheel_svg(data), unsafe_allow_html=True)

    if after_chart_hook:
        after_chart_hook()

    tab_date, tab_sangkhom, tab_sikarat, tab_planets, tab_interp = st.tabs(
        ["📅 Laos 日期", "🧿 ສັງຄົມ", "⏰ ສີກາດ", "🪐 星曜", "📖 傳統解讀"]
    )

    with tab_date:
        weekday_lao = lao_date.get("weekday_lao", "")
        weekday_zh = lao_date.get("weekday_zh") or _zh(weekday_lao, _WEEKDAY_ZH)
        season_lao = lao_date.get("season", "—")
        season_zh = lao_date.get("season_zh") or _zh(season_lao, _SEASON_ZH)
        lao_year = special_year.get("lao_year", "—")
        greg_year = special_year.get("gregorian_year", "—")
        year_desc = special_year.get("description", "普通年份")
        is_special = special_year.get("is_special", False)

        st.markdown(
            f"""
            <div class="lao-cosmic-panel" style="padding:12px 16px;">
              <p style="margin:4px 0;font-size:15px;">
                📅 <b>老撾日期</b>：{lao_date.get('full_lao_date_with_weekday', '—')}
              </p>
              <p style="margin:4px 0;font-size:14px;color:#d7c080;">
                &nbsp;&nbsp;&nbsp;&nbsp;（{weekday_zh}）{lao_date.get('full_lao_date_with_weekday_zh', '')}
              </p>
              <p style="margin:4px 0;font-size:14px;">
                🗓️ <b>老撾佛曆年</b>：ພ.ສ. {lao_year}　|　<b>西元年</b>：{greg_year}
              </p>
              <p style="margin:4px 0;font-size:14px;">
                🌿 <b>季節</b>：{season_lao}（{season_zh}）
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("#### 🔖 特殊年份資訊")
        col_a, col_b = st.columns(2)
        col_a.metric("老撾佛曆年", f"ພ.ສ. {lao_year}")
        col_b.metric("西元年", str(greg_year))
        is_special_label = "⚠️ 特殊年份" if is_special else "✅ 普通年份"
        st.info(f"**年份類型**：{is_special_label}　{year_desc}")
        if is_special and special_year.get("special_types"):
            st.markdown("**特殊年份說明：**")
            for name, rule in special_year["special_types"].items():
                desc = rule.get("description", name)
                st.markdown(f"- **{name}**：{desc}")

    with tab_sangkhom:
        activity_lao = sangkhom.get("activity", "—")
        activity_zh = _zh(activity_lao, _ACTIVITY_ZH)
        status = sangkhom.get("status", "—")
        note = sangkhom.get("note", "")
        recommendation = sangkhom.get("recommendation_zh") or sangkhom.get("recommendation", "—")
        month_note = sangkhom.get("month_note_zh") or sangkhom.get("month_note", "")
        overall = sangkhom.get("overall", "")

        st.markdown(
            f"""
            <div class="lao-cosmic-panel" style="padding:12px 16px;">
              <p style="margin:4px 0;font-size:15px;">
                🎯 <b>活動</b>：{activity_lao}（{activity_zh}）
              </p>
              <p style="margin:6px 0;font-size:20px;font-weight:bold;">
                {status}
              </p>
              <p style="margin:4px 0;font-size:14px;">
                💬 <b>詳細說明</b>：{note}　{sangkhom.get('note_zh', '')}
              </p>
              <p style="margin:4px 0;font-size:14px;">
                📋 <b>建議</b>：{recommendation}
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if month_note:
            st.caption(f"🌙 月份備注：{month_note}")
        if overall:
            is_positive = overall.startswith("✅")
            if is_positive:
                st.success(f"**整體評估**：{overall}")
            else:
                st.warning(f"**整體評估**：{overall}")

    with tab_sikarat:
        sikarat_type = sikarat.get("sikarat_type", "ສີກາດລາວ")
        sikarat_zh = _zh(sikarat_type, _SIKARAT_ZH)
        sikarat_desc = _SIKARAT_DESC_ZH.get(sikarat_type, "")
        current_period = sikarat.get("period_name", "—")
        current_period_zh = _zh(current_period, _SIKARAT_ZH)
        current_status = sikarat.get("status", "—")
        current_hour = sikarat.get("hour", 0)

        st.markdown(
            f"""
            <div class="lao-cosmic-panel" style="padding:12px 16px;">
              <p style="margin:4px 0;font-size:15px;">
                ⏰ <b>時段體系</b>：{sikarat_type}（{sikarat_zh}）
              </p>
              <p style="margin:4px 0;font-size:13px;color:#c9b86c;">{sikarat_desc}</p>
              <p style="margin:6px 0;font-size:15px;">
                🕐 <b>當前時段</b>（{current_hour:02d}:xx）：
                {current_period}（{current_period_zh}）· {current_status}
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 🕰️ 全日 24 小時吉凶一覽")
        rows_s = []
        for h in range(24):
            info = get_sikarat_by_hour(h, sikarat_type)
            period_lao = info["period_name"]
            period_zh = _zh(period_lao, _SIKARAT_ZH)
            s = info["status"]
            is_current = (h == current_hour)
            rows_s.append(
                {
                    "時刻": f"{'▶ ' if is_current else ''}{h:02d}:00",
                    "色嘎時段": f"{period_lao}（{period_zh}）",
                    "吉凶": s,
                    "中文說明": info.get("note_zh", ""),
                }
            )
        st.dataframe(rows_s, width="stretch")

    with tab_planets:
        rows = []
        for p in data.get("planets", []):
            key = p.get("key", "")
            sign_idx = p.get("sign_index", 0)
            sign_lao = _SIGN_NAMES_LAO[sign_idx] if 0 <= sign_idx < _NUM_ZODIAC_SIGNS else "—"
            sign_zh = _zh(sign_lao, _LAO_SIGNS_ZH)
            rows.append(
                {
                    "星曜": f"{p.get('symbol', '')} {_PLANET_ZH.get(key, key.upper())}",
                    "黃經": f"{float(p.get('longitude', 0.0)):.2f}°",
                    "星座（Lao）": sign_lao,
                    "星座（中）": sign_zh,
                    "宮位": p.get("house", "-"),
                    "逆行": "是 ℞" if p.get("retrograde") else "否",
                }
            )
        st.dataframe(rows, width="stretch")

    with tab_interp:
        from .interpreter import interpret_chart

        interp = interpret_chart(data)

        asc_sign_zh = interp.get("ascendant_sign_zh", "—")
        asc_trait_zh = interp.get("ascendant_sign_trait_zh", "")
        summary_zh = interp.get("summary_zh", "")

        st.markdown(
            f"""
            <div class="lao-cosmic-panel" style="padding:12px 16px;">
              <p style="margin:4px 0;font-size:15px;">
                🌅 <b>上升星座</b>：{asc_sign_zh}
                （{interp.get('ascendant_sign_lao', '')}）
              </p>
              <p style="margin:4px 0;font-size:13px;color:#d4be80;">{asc_trait_zh}</p>
              <p style="margin:8px 0 4px 0;font-size:14px;">{summary_zh}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 🪐 逐星曜傳統解讀")
        for reading in interp.get("planet_readings", []):
            planet_zh = reading.get("planet_zh", "")
            house_note_zh = reading.get("house_note_zh", "")
            planet_note_zh = reading.get("planet_note_zh", "")
            retro_note = reading.get("retrograde_note_zh", "")
            retrograde = reading.get("retrograde", False)
            sign_zh = reading.get("sign_zh", "")
            house = reading.get("house", "")
            retro_label = " ℞" if retrograde else ""

            with st.expander(
                f"{planet_zh}{retro_label}　第 {house} 宮　{sign_zh}"
            ):
                st.markdown(f"**傳統義理**：{planet_note_zh}")
                st.markdown(f"**宮位詮釋**：{house_note_zh}")
                if retro_note:
                    st.warning(retro_note)


def render_streamlit(
    chart: LaoChart | Dict[str, Any],
    *,
    lang: str = "zh",
    after_chart_hook: Callable[[], None] | None = None,
) -> None:
    """相容命名：供 app.py 直接使用。"""

    render_lao_horasat(chart, lang=lang, after_chart_hook=after_chart_hook)
