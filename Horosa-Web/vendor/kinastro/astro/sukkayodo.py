"""
日本宿曜道 (Yojōdō) 排盤模組

宿曜道由空海大師於 9 世紀自印度 Jyotish 傳入日本，
使用 28 宿（比印度 27 Nakshatra 多出 Abhijit/牛宿），
以 Moon 所在宿計算六曜 (Rokuyō)。
"""

import math

import streamlit as st

# 七曜名稱索引對照 (lord index → name string)
GRAHA_NAMES_BY_INDEX = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury",
]

# 日本宿曜道 28 宿
# (nak_name, japanese_name, chinese_name, lord_graha_index, symbol, deity, quality)
# lord: 0=Ketu, 1=Venus, 2=Sun, 3=Moon, 4=Mars, 5=Rahu, 6=Jupiter, 7=Saturn, 8=Mercury
SUKKAYODO_MANSION = [
    ("Ashwini",          "アシュヴィニ", "婁宿",   0, "馬", "Aswini Twins",   "Cheerful"),
    ("Bharani",          "バラニ",       "胃宿",   1, "彡", "Yami",            "Passionate"),
    ("Krittika",         "クリティカー", "昴宿",   2, "卍", "Agni",            "Fierce"),
    ("Rohini",           "ロヒニー",     "畢宿",   3, "兔", "Brahma",          "Stable"),
    ("Mrigashira",       "ミルガシラ",   "觜宿",   4, "蚯", "Soma",            "Curious"),
    ("Ardra",            "アルドラ",     "參宿",   5, "獅子","Rudra",           "Restless"),
    ("Punarvasu",        "プナルヴァス", "井宿",   6, "福", "Aditi",           "Renewing"),
    ("Pushya",           "プシュヤ",     "鬼宿",   7, "邪", "Brihaspati",      "Nurturing"),
    ("Ashlesha",         "アシュレーシャ","柳宿",  8, "毒", "Naga",             "Seductive"),
    ("Magha",            "メリカ",       "星宿",   0, "慢", "Pitris",          "Regal"),
    ("Purva Phalguni",   "プールヴァ",   "張宿",   1, "栄", "Bhaga",           "Loving"),
    ("Uttara Phalguni",  "ウッター",     "翼宿",   2, "双", "Aryaman",         "Dutiful"),
    ("Hasta",            "ハスタ",       "軫宿",   3, "智", "Savitri",         "Skillful"),
    ("Chitra",           "チトラ",       "角宿",   4, "勝", "Tvashtar",        "Radiant"),
    ("Swati",            "スヴァティ",   "亢宿",   5, "撃", "Vayu",            "Independent"),
    ("Vishakha",         "ヴィシャーカー", "氐宿",  6, "力", "Indra/Agni",      "Multi-faceted"),
    ("Anuradha",         "アヌラーダー", "房宿",   7, "喜", "Mitra",           "Balanced"),
    ("Jyeshtha",         "ジェーシタ",   "心宿",   8, "主", "Indra",           "Protective"),
    ("Mula",             "ムーラ",       "尾宿",   0, "死", "Nirriti",         "Deep"),
    ("Purva Ashadha",    "プールヴァ",   "箕宿",   1, "満", "Apah",            "Victorious"),
    ("Uttara Ashadha",   "ウッター",    "斗宿",   2, "生", "Vishwa Devas",    "Truthful"),
    ("Abhijit",          "アビジート",   "牛宿",   2, "織", "Brahma/Vega",     "Noble"),
    ("Shravana",         "シュラヴァナ", "女宿",   3, "虚", "Vishnu",          "Devoted"),
    ("Dhanishta",        "ダニスター",   "虛宿",   4, "危", "Vasudev",         "Wealthy"),
    ("Shatabhisha",      "シャタビシャ", "危宿",   5, "命", "Varuna",          "Mysterious"),
    ("Purva Bhadrapada", "プールヴァ",   "室宿",   6, "留", "Aja Ekapada",     "Heroic"),
    ("Uttara Bhadrapada","ウッター",     "壁宿",   7, "堅", "Ahir Budhya",     "Serene"),
    ("Revati",           "レヴァティー", "奎宿",   8, "開", "Pushan",          "Nurturing"),
]

# 六曜 (Rokuyō) — 順序：先勝 → 友引 → 先負 → 仏滅 → 大安 → 赤口
ROKUYO = [
    ("先勝",   "Senshō",   "吉(速)",  "#228B22"),
    ("友引",   "Tomoyuki", "小吉",    "#4169E1"),
    ("先負",   "Senku",    "末吉",    "#8B4513"),
    ("仏滅",   "Butsumetsu","凶",     "#DC143C"),
    ("大安",   "Taian",    "大吉",    "#FFD700"),
    ("赤口",   "Shakuchō", "凶(吉)",  "#FF4500"),
]

# 每宿對應六曜索引（每 6 宿一循環）
SUKKAYODO_NAKSHATRA_ROKUYO_MAP = [
    0, 1, 2, 3, 4, 5,
    0, 1, 2, 3, 4, 5,
    0, 1, 2, 3, 4, 5,
    0, 1, 2, 3, 4, 5,
    0, 1, 2, 3,
]

# 七曜顏色（深色主題）
GRAHA_COLORS = {
    "Ketu":     "#9B59B6",
    "Venus":    "#FF69B4",
    "Sun":      "#FF8C00",
    "Moon":     "#C0C0C0",
    "Mars":     "#DC143C",
    "Rahu":     "#8E44AD",
    "Jupiter":  "#FFD700",
    "Saturn":   "#8B4513",
    "Mercury":  "#4169E1",
}

PLANET_COLORS = {
    "Surya (太陽)": "#FF8C00",
    "Chandra (月亮)": "#C0C0C0",
    "Mangal (火星)": "#DC143C",
    "Budha (水星)": "#4169E1",
    "Guru (木星)": "#FFD700",
    "Shukra (金星)": "#FF69B4",
    "Shani (土星)": "#8B4513",
    "Rahu (羅睺)": "#8E44AD",
    "Ketu (計都)": "#9B59B6",
}

# 十二宮（黃道宮位）與二十八宿對應
# 每個宮包含 2-3 宿，索引對應 SUKKAYODO_MANSION
TWELVE_PALACES = [
    ("羊宮", [0, 1]),             # 婁, 胃 (Aries)
    ("牛宮", [2, 3]),             # 昴, 畢 (Taurus)
    ("夫宮", [4, 5]),             # 觜, 參 (Gemini)
    ("蟹宮", [6, 7, 8]),          # 井, 鬼, 柳 (Cancer)
    ("獅宮", [9, 10]),            # 星, 張 (Leo)
    ("女宮", [11, 12]),           # 翼, 軫 (Virgo)
    ("秤宮", [13, 14, 15]),       # 角, 亢, 氐 (Libra)
    ("蝎宮", [16, 17]),           # 房, 心 (Scorpio)
    ("弓宮", [18, 19]),           # 尾, 箕 (Sagittarius)
    ("磨宮", [20, 21]),           # 斗, 牛 (Capricorn)
    ("瓶宮", [22, 23, 24]),       # 女, 虛, 危 (Aquarius)
    ("魚宮", [25, 26, 27]),       # 室, 壁, 奎 (Pisces)
]

# 各宮中心角度（SVG 座標系：0°=右, 順時鐘增加）
# 牛宮(Taurus)在頂端(270°), 黃道逆時鐘排列
PALACE_CENTER_ANGLES = [300, 270, 240, 210, 180, 150, 120, 90, 60, 30, 0, 330]

# 九曜中文單字（對應 GRAHA_NAMES_BY_INDEX 索引 0-8）
LORD_CHARS = ["計", "金", "日", "月", "火", "羅", "木", "土", "水"]

# 四象分組（使用中國天文正統排序）
FOUR_SYMBOLS = [
    ("🌿 東方蒼龍", [13, 14, 15, 16, 17, 18, 19], "#228B22"),  # 角亢氐房心尾箕
    ("🐢 北方玄武", [20, 21, 22, 23, 24, 25, 26], "#4169E1"),  # 斗牛女虛危室壁
    ("🐅 西方白虎", [27, 0, 1, 2, 3, 4, 5],       "#DC143C"),  # 奎婁胃昴畢觜參
    ("🐦 南方朱雀", [6, 7, 8, 9, 10, 11, 12],     "#FF8C00"),  # 井鬼柳星張翼軫
]


# ============================================================
# 計算函數
# ============================================================

def _normalize(deg):
    return deg % 360.0


def sukkayodo_info(deg):
    """Return (sukkayodo_mansion_index, pada) for sidereal longitude.

    宿曜道 28 宿，每宿 12°51'26"（360°/28）。
    """
    deg = _normalize(deg)
    nak_span = 360.0 / 28.0
    idx = int(deg / nak_span) % 28
    pada = int((deg % nak_span) / (nak_span / 4.0)) + 1
    return idx, min(pada, 4)


def get_rokuyo(mansion_index):
    """根據宿曜道索引取得六曜資訊"""
    if mansion_index < 0 or mansion_index >= 28:
        return None
    return ROKUYO[SUKKAYODO_NAKSHATRA_ROKUYO_MAP[mansion_index % 28]]


# ============================================================
# 渲染函數
# ============================================================

def render_sukkayodo_chart(chart, after_chart_hook=None):
    """渲染日本宿曜道排盤"""
    st.subheader("🈳 日本宿曜道 (Yojōdō)")

    # 找出 Moon
    moon_planet = None
    for p in chart.planets:
        if "Moon" in p.name or "月亮" in p.name:
            moon_planet = p
            break

    moon_mansion_idx = -1
    if moon_planet and moon_planet.sukkayodo_mansion_index >= 0:
        moon_mansion_idx = moon_planet.sukkayodo_mansion_index
        rokuyo = get_rokuyo(moon_mansion_idx)
    else:
        rokuyo = None

    # 宿曜道圓環圖（先顯示）
    st.markdown("### 宿曜道圓環圖 (二十八宿)")
    _render_wheel(chart, moon_mansion_idx)

    if after_chart_hook:
        after_chart_hook()

    # 六曜卡片
    st.markdown("### 當日六曜 (Rokuyō)")
    cols = st.columns(6)
    for i, (jp, romaji, meaning, color) in enumerate(ROKUYO):
        active = (rokuyo and rokuyo[0] == jp)
        bg = color if active else "#1a1a2e"
        fg = "#fff" if active else "#aaa"
        border = f"2px solid {color}" if active else "1px solid #333"
        style = (
            f"background:{bg}; color:{fg}; padding:10px; "
            f"border-radius:8px; text-align:center; border:{border};"
        )
        with cols[i]:
            st.markdown(
                f'<div style="{style}">'
                f'<b>{jp}</b><br/><small>{romaji}</small><br/>'
                f'<small>{meaning}</small>{" ✅" if active else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )

    if moon_planet:
        st.caption(
            f"Moon 位於：{moon_planet.sukkayodo_mansion}"
            f"（{moon_planet.sukkayodo_mansion_chinese}）"
            f"　{moon_planet.sukkayodo_pada}足　"
            f"→ 六曜：{rokuyo[0] if rokuyo else '?'} ({rokuyo[1] if rokuyo else ''})"
        )

    # 行星宿曜道位置
    st.markdown("### 行星宿曜道位置")
    rows2 = [
        "| Graha | 宿名 | 中國 | Pada | 六曜 |",
        "|:-----:|:-----|:-----|:----:|:----:|",
    ]
    for p in chart.planets:
        if p.sukkayodo_mansion_index >= 0:
            m = SUKKAYODO_MANSION[p.sukkayodo_mansion_index]
            rk = get_rokuyo(p.sukkayodo_mansion_index)
            color = PLANET_COLORS.get(p.name, "#c8c8c8")
            rows2.append(
                f"| <span style='color:{color}'>{p.name}</span> | "
                f"**{p.sukkayodo_mansion}** ({m[1]}) | "
                f"{p.sukkayodo_mansion_chinese} | {p.sukkayodo_pada} | "
                f"<span style='color:{rk[3]}'>{rk[0]}</span> |"
            )
    st.markdown("\n".join(rows2), unsafe_allow_html=True)

    # 28 宿列表
    st.markdown("### 二十八宿 (28 Mansions)")
    rows = [
        "| # | 宿名 | 日名 | 中國 | 符 | 主曜 | 六曜 |",
        "|:--:|:-----|:-----|:-----|:--:|:-----|:----:|",
    ]
    for i, m in enumerate(SUKKAYODO_MANSION):
        nak_name, jp_name, chinese = m[0], m[1], m[2]
        lord_idx, symbol = m[3], m[4]
        lord_name = GRAHA_NAMES_BY_INDEX[lord_idx]
        lord_color = GRAHA_COLORS.get(lord_name, "#c8c8c8")
        is_moon = (i == moon_mansion_idx)
        rk = get_rokuyo(i)
        star = "⭐" if is_moon else ""
        rows.append(
            f"| {star}{i+1} | "
            f'<b>{"⭐" if is_moon else ""}{nak_name}</b> | '
            f'{jp_name} | {chinese} | {symbol} | '
            f'<span style="color:{lord_color}">{lord_name}</span> | '
            f'<span style="color:{rk[3]}">{rk[0]}</span> |'
        )
    st.markdown("\n".join(rows), unsafe_allow_html=True)

    # 三九秘宿法面板
    sansanju_result = _get_sansanju_table(chart.month, chart.day)
    _render_sansanju_panel(chart, sansanju_result)


def _render_wheel(chart, moon_mansion_idx):
    """渲染宿曜道圓環圖 — 十二宮 SVG 圓盤"""

    CX, CY = 350, 350
    SIZE = 700

    # 同心圓環半徑
    R_OUTER = 310       # 十二宮標籤環
    R_PALACE = 280      # 宮名與宿名分界
    R_MANSION = 230     # 宿名環
    R_LORD = 185        # 九曜主環
    R_PHASE = 145       # 月相環
    R_CENTER = 105      # 太極圓
    R_YINYANG = 70      # 太極圖半徑

    # 建立每宿行星列表
    mansion_planets = {i: [] for i in range(28)}
    for p in chart.planets:
        if p.sukkayodo_mansion_index >= 0:
            short = p.name.split(" ")[0]
            mansion_planets[p.sukkayodo_mansion_index].append(short)

    # 計算每個宿的中心角度
    mansion_angles = {}
    for pi, (_, indices) in enumerate(TWELVE_PALACES):
        center = PALACE_CENTER_ANGLES[pi]
        n = len(indices)
        span = 30.0
        sub_span = span / n
        start = center - span / 2
        for mi, idx in enumerate(indices):
            mansion_angles[idx] = start + sub_span * (mi + 0.5)

    # 計算每個宿的邊界角度
    mansion_boundaries = {}
    for pi, (_, indices) in enumerate(TWELVE_PALACES):
        center = PALACE_CENTER_ANGLES[pi]
        n = len(indices)
        span = 30.0
        sub_span = span / n
        start = center - span / 2
        for mi, idx in enumerate(indices):
            mansion_boundaries[idx] = (start + sub_span * mi,
                                       start + sub_span * (mi + 1))

    def polar(r, angle_deg):
        """角度 → SVG 座標"""
        rad = math.radians(angle_deg)
        return CX + r * math.cos(rad), CY + r * math.sin(rad)

    def _text_rotation(a):
        """計算文字旋轉角度（radial outward, 保持可讀）"""
        rot = (a + 90) % 360
        if 90 < rot < 270:
            rot = (rot + 180) % 360
        return rot

    def arc_path(r, a1, a2):
        """SVG 弧線路徑（從 a1 到 a2）"""
        x1, y1 = polar(r, a1)
        x2, y2 = polar(r, a2)
        sweep = a2 - a1
        if sweep < 0:
            sweep += 360
        large = 1 if sweep > 180 else 0
        return f"M {x1:.1f},{y1:.1f} A {r},{r} 0 {large},1 {x2:.1f},{y2:.1f}"

    def dodecagon_point(angle_deg):
        """取得正十二邊形上的點（與角度最近的頂點插值）"""
        return polar(R_OUTER, angle_deg)

    # 十二邊形頂點（宮界）
    boundary_angles = [PALACE_CENTER_ANGLES[i] - 15 for i in range(12)]

    # ==================== 開始 SVG ====================
    svg_parts = []
    svg_parts.append(
        f'<svg viewBox="0 0 {SIZE} {SIZE}" '
        f'width="{SIZE}" height="{SIZE}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'style="max-width:620px; margin:auto; display:block; '
        f'background:#0a0a1a; border-radius:12px;">'
    )

    # 背景
    svg_parts.append(
        f'<rect width="{SIZE}" height="{SIZE}" fill="#0a0a1a" rx="12"/>'
    )

    # --- 十二邊形外框改為圓形 ---
    svg_parts.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUTER}" '
        f'fill="none" stroke="#c8c8c8" stroke-width="1.5"/>'
    )

    # --- 同心圓 ---
    for r in [R_PALACE, R_MANSION, R_LORD, R_PHASE, R_CENTER]:
        svg_parts.append(
            f'<circle cx="{CX}" cy="{CY}" r="{r}" '
            f'fill="none" stroke="#444" stroke-width="0.8"/>'
        )

    # --- 十二宮分界線（R_CENTER → R_OUTER）---
    for ba in boundary_angles:
        x1, y1 = polar(R_CENTER, ba)
        x2, y2 = polar(R_OUTER, ba)
        svg_parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#666" stroke-width="0.8"/>'
        )

    # --- 宿分界線（R_CENTER → R_PALACE，虛線）---
    for pi, (_, indices) in enumerate(TWELVE_PALACES):
        center = PALACE_CENTER_ANGLES[pi]
        n = len(indices)
        if n <= 1:
            continue
        span = 30.0
        sub_span = span / n
        start = center - span / 2
        for mi in range(1, n):
            a = start + sub_span * mi
            x1, y1 = polar(R_CENTER, a)
            x2, y2 = polar(R_PALACE, a)
            svg_parts.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
                f'x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="#333" stroke-width="0.5" stroke-dasharray="4,3"/>'
            )

    # --- 十二宮標籤（十二邊形外框與宮名環之間）---
    for pi, (name, _) in enumerate(TWELVE_PALACES):
        a = PALACE_CENTER_ANGLES[pi]
        r_label = (R_OUTER + R_PALACE) / 2
        x, y = polar(r_label, a)
        rot = _text_rotation(a)
        svg_parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="#e0e0e0" '
            f'font-size="15" font-weight="bold" '
            f'font-family="serif" '
            f'transform="rotate({rot:.1f},{x:.1f},{y:.1f})">{name}</text>'
        )

    # --- 二十八宿名（宮名環與宿名環之間）---
    for idx in range(28):
        if idx not in mansion_angles:
            continue
        a = mansion_angles[idx]
        m = SUKKAYODO_MANSION[idx]
        chinese = m[2]
        char = chinese[0] if chinese else "?"

        r_text = (R_PALACE + R_MANSION) / 2
        x, y = polar(r_text, a)

        is_moon = (idx == moon_mansion_idx)
        fill = "#FFD700" if is_moon else "#e0e0e0"
        weight = "bold" if is_moon else "normal"
        fsize = "16" if is_moon else "14"

        # 月亮所在宿的背景高亮
        if is_moon:
            ba1, ba2 = mansion_boundaries[idx]
            svg_parts.append(
                f'<path d="{_annular_sector(CX, CY, R_PALACE, R_MANSION, ba1, ba2)}" '
                f'fill="#3d3010" fill-opacity="0.6"/>'
            )

        svg_parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{fill}" '
            f'font-size="{fsize}" font-weight="{weight}" '
            f'font-family="serif" '
            f'transform="rotate({_text_rotation(a):.1f},{x:.1f},{y:.1f})">'
            f'{char}</text>'
        )

    # --- 九曜主（宿名環與九曜環之間）---
    for idx in range(28):
        if idx not in mansion_angles:
            continue
        a = mansion_angles[idx]
        m = SUKKAYODO_MANSION[idx]
        lord_idx = m[3]
        lord_char = LORD_CHARS[lord_idx]
        lord_name = GRAHA_NAMES_BY_INDEX[lord_idx]
        lord_color = GRAHA_COLORS.get(lord_name, "#c8c8c8")

        r_text = (R_MANSION + R_LORD) / 2
        x, y = polar(r_text, a)
        svg_parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{lord_color}" '
            f'font-size="12" font-family="serif" '
            f'transform="rotate({_text_rotation(a):.1f},{x:.1f},{y:.1f})">'
            f'{lord_char}</text>'
        )

    # --- 月相（九曜環與月相環之間）---
    for idx in range(28):
        if idx not in mansion_angles:
            continue
        a = mansion_angles[idx]
        r_circ = (R_LORD + R_PHASE) / 2
        x, y = polar(r_circ, a)
        phase_r = 7

        # 28 宿對應月亮盈虧週期
        # 0-6: 新月→上弦, 7-13: 上弦→滿月, 14-20: 滿月→下弦, 21-27: 下弦→新月
        quarter = idx // 7
        pos = idx % 7
        if quarter == 0:  # 新月→上弦：逐漸填滿右半
            fill_pct = pos / 7.0
            svg_parts.append(_moon_phase_svg(x, y, phase_r, fill_pct, "waxing"))
        elif quarter == 1:  # 上弦→滿月
            fill_pct = 0.5 + pos / 14.0
            svg_parts.append(_moon_phase_svg(x, y, phase_r, fill_pct, "waxing"))
        elif quarter == 2:  # 滿月→下弦
            fill_pct = 1.0 - pos / 7.0
            svg_parts.append(_moon_phase_svg(x, y, phase_r, fill_pct, "waning"))
        else:  # 下弦→新月
            fill_pct = 0.5 - pos / 14.0
            svg_parts.append(_moon_phase_svg(x, y, phase_r, fill_pct, "waning"))

    # --- 行星標記（在宿名環外緣標記）---
    for idx in range(28):
        p_list = mansion_planets.get(idx, [])
        if not p_list or idx not in mansion_angles:
            continue
        a = mansion_angles[idx]
        # 在宿名文字外側放置行星符號
        for pi_offset, pname in enumerate(p_list):
            r_p = R_PALACE + 2
            # 同一宿多顆行星時，以 2.5° 間距排列避免重疊
            offset_angle = (pi_offset - (len(p_list) - 1) / 2) * 2.5
            px, py = polar(r_p, a + offset_angle)
            pcolor = "#c8c8c8"
            for key, val in PLANET_COLORS.items():
                if pname in key:
                    pcolor = val
                    break
            svg_parts.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" '
                f'fill="{pcolor}" stroke="#fff" stroke-width="0.5"/>'
            )

    # --- 太極圖 (yin-yang) ---
    svg_parts.append(_yin_yang_svg(CX, CY, R_YINYANG))

    svg_parts.append("</svg>")
    svg = "\n".join(svg_parts)
    st.markdown(svg, unsafe_allow_html=True)

    # 圖例說明
    st.markdown(
        '<p style="text-align:center; color:#888; font-size:12px; margin-top:6px;">'
        "外圈：十二宮　第二圈：二十八宿　第三圈：九曜主　"
        "內圈：月相　中心：太極"
        "</p>",
        unsafe_allow_html=True,
    )

    # 四象二十八宿
    st.markdown("### 四象二十八宿")
    cols = st.columns(4)
    for ci, (name, indices, color) in enumerate(FOUR_SYMBOLS):
        with cols[ci]:
            items = []
            for i in indices:
                m = SUKKAYODO_MANSION[i]
                symbol, chinese = m[4], m[2]
                rk = get_rokuyo(i)
                is_moon = (i == moon_mansion_idx)
                star = "⭐" if is_moon else ""
                lord_color = GRAHA_COLORS.get(
                    GRAHA_NAMES_BY_INDEX[m[3]], "#c8c8c8"
                )
                items.append(
                    f"<b>{star}{chinese[0] if chinese else '?'}</b> "
                    f'<span style="color:{lord_color}">'
                    f"{LORD_CHARS[m[3]]}</span> "
                    f'<span style="color:{rk[3]}">({rk[0]})</span>'
                )
            st.markdown(
                f'<div style="background:#1a1a2e; border:1px solid {color}; '
                f'border-radius:8px; padding:10px; color:#e0e0e0;">'
                f'<b style="color:{color}">{name}</b><br/>'
                f'<small>{"　".join(items)}</small>'
                f'</div>',
                unsafe_allow_html=True,
            )


def _annular_sector(cx, cy, r_outer, r_inner, a1, a2):
    """SVG path for an annular sector between two radii and two angles."""
    rad1 = math.radians(a1)
    rad2 = math.radians(a2)
    sweep = a2 - a1
    if sweep < 0:
        sweep += 360
    large = 1 if sweep > 180 else 0

    ox1 = cx + r_outer * math.cos(rad1)
    oy1 = cy + r_outer * math.sin(rad1)
    ox2 = cx + r_outer * math.cos(rad2)
    oy2 = cy + r_outer * math.sin(rad2)
    ix1 = cx + r_inner * math.cos(rad1)
    iy1 = cy + r_inner * math.sin(rad1)
    ix2 = cx + r_inner * math.cos(rad2)
    iy2 = cy + r_inner * math.sin(rad2)

    return (
        f"M {ox1:.1f},{oy1:.1f} "
        f"A {r_outer},{r_outer} 0 {large},1 {ox2:.1f},{oy2:.1f} "
        f"L {ix2:.1f},{iy2:.1f} "
        f"A {r_inner},{r_inner} 0 {large},0 {ix1:.1f},{iy1:.1f} Z"
    )


def _moon_phase_svg(cx, cy, r, fill_pct, direction):
    """Generate SVG for a moon phase circle.

    fill_pct: 0.0 = new moon, 1.0 = full moon
    direction: 'waxing' or 'waning'
    """
    parts = []
    # Outer circle (dark background)
    parts.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" '
        f'fill="#1a1a2e" stroke="#555" stroke-width="0.5"/>'
    )

    if fill_pct <= 0.02:
        # New moon — empty circle
        return "\n".join(parts)
    if fill_pct >= 0.98:
        # Full moon — filled circle
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" '
            f'fill="#e8e8d0" stroke="#555" stroke-width="0.5"/>'
        )
        return "\n".join(parts)

    # Partial moon using two arcs
    # Map fill_pct to the terminator curve
    # When fill=0.5, the terminator is a straight line (half moon)
    # When fill<0.5, the lit area is a crescent
    # When fill>0.5, the lit area is gibbous
    t = (fill_pct - 0.5) * 2  # -1 to 1
    # t=-1: new, t=0: half, t=1: full
    # The terminator ellipse x-radius = abs(t) * r
    tx = t * r

    top_y = cy - r
    bot_y = cy + r

    if direction == "waxing":
        # Lit area on the right side
        lit_edge_x = cx + r  # right edge
        # Terminator at cx + tx
        sweep_outer = 1  # right arc (convex)
        # The lit path: from top, right arc to bottom, then terminator back
        parts.append(
            f'<path d="M {cx:.1f},{top_y:.1f} '
            f'A {r},{r} 0 0,1 {cx:.1f},{bot_y:.1f} '
            f'A {abs(tx) if tx != 0 else 0.01:.1f},{r} 0 0,'
            f'{"1" if tx >= 0 else "0"} {cx:.1f},{top_y:.1f}" '
            f'fill="#e8e8d0"/>'
        )
    else:
        # Lit area on the left side
        parts.append(
            f'<path d="M {cx:.1f},{top_y:.1f} '
            f'A {r},{r} 0 0,0 {cx:.1f},{bot_y:.1f} '
            f'A {abs(tx) if tx != 0 else 0.01:.1f},{r} 0 0,'
            f'{"0" if tx >= 0 else "1"} {cx:.1f},{top_y:.1f}" '
            f'fill="#e8e8d0"/>'
        )

    return "\n".join(parts)


def _yin_yang_svg(cx, cy, r):
    """Generate SVG for a yin-yang (太極) symbol."""
    hr = r / 2  # half radius
    dr = r / 6  # dot radius

    return (
        # White half (right/bottom)
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#e8e8e0" '
        f'stroke="#888" stroke-width="1"/>'
        # Black half (left/top)
        f'<path d="M {cx},{cy - r} A {r},{r} 0 0,0 {cx},{cy + r} '
        f'A {hr},{hr} 0 0,0 {cx},{cy} '
        f'A {hr},{hr} 0 0,1 {cx},{cy - r}" fill="#1a1a2e"/>'
        # White dot in black area
        f'<circle cx="{cx}" cy="{cy - hr}" r="{dr}" fill="#e8e8e0"/>'
        # Black dot in white area
        f'<circle cx="{cx}" cy="{cy + hr}" r="{dr}" fill="#1a1a2e"/>'
    )


# ============================================================
# 三九秘宿法 (San-Jiu Bi-Su Method)
# ============================================================

# 三九秘宿法使用的二十七星宿（去除牛宿 Abhijit = SUKKAYODO_MANSION index 20）
# 從婁宿(0)循環，去除牛宿(20)後共27宿
# SANSANJU_27_MANSIONS[i] = SUKKAYODO_MANSION index（position 0-26）
SANSANJU_27_MANSIONS = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,   # 婁→軫 (0-11)
    12, 13, 14, 15, 16, 17, 18, 19,          # 角→箕 (12-19)
    21, 22, 23, 24, 25, 26, 0,                # 斗→奎→婁 (20-26, 26 wraps to 0)
]

# 每月起始宿在 SANSANJU_27_MANSIONS 中的 position（0-26）
# 正月=婁(0), 二月=奎(25), 三月=胃(1), 四月=畢(3),
# 五月=參(5), 六月=鬼(7), 七月=星(9), 八月=角(13),
# 九月=氐(15), 十月=心(17), 十一月=斗(20), 十二月=虛(22)
SANSANJU_MONTH_STARTS = [0, 25, 1, 3, 5, 7, 9, 13, 15, 17, 20, 22]

# 命、業、胎三本
THREE_ROOTS = ["命", "業", "胎"]

# 十一類星宿含義
SANSANJU_MEANINGS = {
    "命": "百事不宜",
    "業": "所作皆吉、吉祥",
    "胎": "百事不宜",
    "榮": "諸事適用，所作皆吉",
    "衰": "解惡、治病等可，不宜遠行、遷移、買賣、裁衣、剃頭、剪甲",
    "危": "歡聚吉利，宜交友、婚事、宴友，不宜遠行、遷移",
    "成": "宜求學、問道、合藥、訪師、延壽",
    "壞": "利於出征、討伐、壓鎮降伏，不宜同「衰」",
    "安": "適於遷徙、移動、遠行、修園宅臥具，可啟建壇場",
    "友": "結婚、交友大吉",
    "親": "結婚、交友大吉",
}

# 十一類顏色
SANSANJU_COLORS = {
    "命": "#DC143C",
    "業": "#228B22",
    "胎": "#DC143C",
    "榮": "#FFD700",
    "衰": "#8B4513",
    "危": "#FF4500",
    "成": "#4169E1",
    "壞": "#9B59B6",
    "安": "#228B22",
    "友": "#FF69B4",
    "親": "#FF69B4",
}


def _get_sansanju_table(birth_month, birth_day):
    """計算指定年月日的三九秘宿表。

    Returns:
        dict with keys:
          - "table": list of (mansion_index_27, category) for all 27 positions
          - "first_mansion_27": the starting 27-mansion index for this birth month
          - "first_category": the category at position (birth_day - 1) in the full 33-slot list
          - "day_category": the category for the birth day (命/業/胎/榮/...)
          - "day_mansion_27": mansion index in SANSANJU_27_MANSIONS for the birth day
          - "full_sequence": list of 33 categories (命/業/胎 + 8 + 命/業/胎 + 8 + 命/業/胎 + 8)
    """
    # 1. Find starting 27-mansion index for the birth month
    start_27 = SANSANJU_MONTH_STARTS[birth_month - 1]

    # 2. Build the 27-mansion list (circular) starting from birth month
    mansions_27 = []
    for i in range(27):
        mansions_27.append(SANSANJU_27_MANSIONS[(start_27 + i) % 27])

    # 3. Build the full 33-category sequence: [命/業/胎] + 8-categories repeated 3 times
    CATEGORIES_8 = ["榮", "衰", "安", "危", "成", "壞", "友", "親"]
    full_seq = THREE_ROOTS + CATEGORIES_8 + THREE_ROOTS + CATEGORIES_8 + THREE_ROOTS + CATEGORIES_8

    # 4. Position in the full sequence corresponding to birth_day
    # Count from 1 (1st day = first mansion's category = full_seq[0])
    pos = (birth_day - 1) % 33
    day_category = full_seq[pos]

    # 5. The mansion at this day position (in 27-mansion list)
    day_mansion_27 = mansions_27[pos % 27]

    # 6. Build the full table: 33 entries mapping mansion → category
    table = []
    seq_len = len(full_seq)  # 33
    for i in range(seq_len):
        m_idx = mansions_27[i % 27]
        cat = full_seq[i]
        table.append((m_idx, cat))

    return {
        "table": table,
        "first_mansion_27": mansions_27[0],
        "full_sequence": full_seq,
        "day_category": day_category,
        "day_mansion_27": day_mansion_27,
    }


def _get_daily_sansanju_category(birth_month, birth_day, daily_mansion_27_idx):
    """根據當日值日星宿，回推該日在三九秘宿表中的分類。

    Args:
        birth_month, birth_day: 出生月日
        daily_mansion_27_idx: 當日值日星宿的 27 宿索引（0-26對應SANSANJU_27_MANSIONS）

    Returns:
        str: 該日對應的三九秘宿分類（命/業/胎/榮/衰/安/危/成/壞/友/親）
    """
    result = _get_sansanju_table(birth_month, birth_day)
    for m27, cat in result["table"]:
        if m27 == daily_mansion_27_idx:
            return cat
    return "?"


def _get_sansanju_mansion_meaning(cat):
    """取得三九秘宿分類的含義說明"""
    return SANSANJU_MEANINGS.get(cat, "（含義待考）")


def _render_sansanju_panel(chart, result):
    """渲染三九秘宿法面板"""
    st.markdown("### 三九秘宿法")

    # 基本說明
    birth_month = chart.month
    birth_day = chart.day

    mansions_27 = []
    start_27 = SANSANJU_MONTH_STARTS[birth_month - 1]
    for i in range(27):
        mansions_27.append(SANSANJU_27_MANSIONS[(start_27 + i) % 27])

    first_mansion_idx = mansions_27[0]  # SUKKAYODO_MANSION index
    first_mansion = SUKKAYODO_MANSION[first_mansion_idx]
    day_mansion_idx = result["day_mansion_27"]
    day_mansion = SUKKAYODO_MANSION[day_mansion_idx]

    st.markdown(
        f"**命宿表（{birth_month}月）**：以 `{first_mansion[2]}` 宿為首，"
        f"共 27 宿（去牛宿）。{birth_month}月{birth_day}日生，"
        f"第一命宿為 `{day_mansion[2]}`（{result['day_category']}）。"
    )

    # ---- 分類說明 ----
    st.markdown("#### 各宿含義")
    meaning_cols = st.columns(3)
    cats = list(SANSANJU_MEANINGS.keys())
    for i, cat in enumerate(cats):
        col = meaning_cols[i % 3]
        color = SANSANJU_COLORS.get(cat, "#888")
        with col:
            st.markdown(
                f"<div style='border-left:4px solid {color}; padding:4px 8px; "
                f"background:#1a1a2e; border-radius:4px; margin-bottom:6px;'>"
                f"<b style='color:{color}'>{cat}</b>：{SANSANJU_MEANINGS[cat]}"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ---- 27宿命宿表 ----
    st.markdown("#### 27宿命宿表")
    CATEGORIES_8 = ["榮", "衰", "安", "危", "成", "壞", "友", "親"]

    # Build rows: 11 categories (命/業/胎 + 8) × shows mansion for each
    categories_11 = THREE_ROOTS + CATEGORIES_8  # 11 items

    # ---- 27宿命宿表 ----
    # Position i (0-26) → mansion index in SANSANJU_27_MANSIONS (0-26) + category
    # Categories repeat: [命,業,胎,榮,衰,安,危,成,壞,友,親, 榮,衰,..., 榮,...]
    # full_seq has 33 entries (3 × 11), cycling through 27 mansions
    full_seq_33 = THREE_ROOTS + CATEGORIES_8 + THREE_ROOTS + CATEGORIES_8 + THREE_ROOTS + CATEGORIES_8

    # Build position-based table: pos (0-26) → (m27_pos, category)
    # At position i: mansion is mansions_27[i], category is full_seq_33[i]
    pos_table = [(mansions_27[i % 27], full_seq_33[i]) for i in range(27)]

    # For each category, find which 27-position(s) carry it
    cat_to_pos = {cat: [] for cat in categories_11}
    for i, (m27, cat) in enumerate(pos_table):
        cat_to_pos[cat].append(i)

    # Render as a single HTML table inside a scrollable container for mobile
    cell_style = "padding:4px 6px;text-align:center;border:1px solid #333;font-size:0.75rem;"
    header_style = cell_style + "background:#1a1a2e;color:#aaa;white-space:nowrap;"
    th_cells = "".join(
        f"<th style='{header_style}'>"
        f"{SUKKAYODO_MANSION[mansions_27[(start_27 + i) % 27]][2]}</th>"
        for i in range(27)
    )
    html_rows = [
        f"<thead><tr><th style='{header_style}'>分類</th>{th_cells}</tr></thead><tbody>"
    ]
    for cat in categories_11:
        color = SANSANJU_COLORS.get(cat, "#888")
        td_cells = []
        for i in range(27):
            if i in cat_to_pos[cat]:
                td_cells.append(
                    f"<td style='{cell_style}color:{color};font-weight:bold'>{cat}</td>"
                )
            else:
                td_cells.append(f"<td style='{cell_style}color:#555'>·</td>")
        html_rows.append(
            f"<tr><td style='{cell_style}background:#1a1a2e;color:{color};"
            f"font-weight:bold;white-space:nowrap'>{cat}</td>"
            + "".join(td_cells)
            + "</tr>"
        )
    html_rows.append("</tbody>")
    table_html = (
        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;margin:8px 0;">'
        f'<table style="border-collapse:collapse;background:#0d1117;font-family:sans-serif;">'
        + "".join(html_rows)
        + "</table></div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)

    # ---- 當日分類高亮 ----
    day_cat = result["day_category"]
    day_color = SANSANJU_COLORS.get(day_cat, "#888")
    st.markdown(
        f"**今日（{birth_month}月{birth_day}日）命宿："
        f"<span style='color:{day_color}'>{day_mansion[2]}（{day_cat}）</span>**"
        f" — {_get_sansanju_mansion_meaning(day_cat)}",
        unsafe_allow_html=True,
    )

    # ---- 择日参考：查找某日属于哪个分类 ----
    st.markdown("#### 择日参考")
    st.caption("输入值日星宿（农民历记载的当日值日星宿），查询对命主之吉凶")

    col1, col2 = st.columns([1, 2])
    with col1:
        daily_input = st.text_input(
            "值日星宿（中國名）",
            placeholder="如：斗、室、壁",
            key="sansanju_daily_mansion",
        )
    if daily_input:
        # Find matching mansion by Chinese name (去除「宿」字)
        found_m27 = None
        found_m27_pos = None
        for pos_i, m28_idx in enumerate(mansions_27):
            sukk = SUKKAYODO_MANSION[m28_idx]
            # 去除「宿」後比對
            if sukk[2].replace("宿", "") == daily_input.replace("宿", "").strip():
                found_m28_idx = m28_idx
                found_m27_pos = pos_i
                found_sukk = sukk
                break
        if found_m27_pos is not None:
            # Find all category entries for this mansion at each occurrence
            entries = []
            for i, (m27, cat) in enumerate(pos_table):
                if m27 == found_m27_pos:
                    entries.append((i, cat))
            # Show each occurrence
            parts = []
            for i, cat in entries:
                color = SANSANJU_COLORS.get(cat, "#888")
                parts.append(
                    f"<span style='color:{color};font-weight:bold'>{cat}</span>"
                    f"（第{i+1}命宿 {_get_sansanju_mansion_meaning(cat)}）"
                )
            st.markdown(
                f"值日星宿 **`{found_sukk[2]}`** 在命宿表中為："
                f"{' | '.join(parts)}",
                unsafe_allow_html=True,
            )
        else:
            st.warning(
                f"未找到星宿：「{daily_input}」。"
                f"請輸入中國星名（如：斗、室、壁、婁、胃、昴、畢、參、井、鬼、柳、星、張、翼、軫、角、亢、氐、房、心、尾、箕、女、虛、危）。"
            )
