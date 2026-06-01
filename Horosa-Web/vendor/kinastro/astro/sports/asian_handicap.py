"""
亞洲讓球盤分析 (Asian Handicap Analysis)

根據歐賠 (1X2 decimal odds) 計算隱含概率，結合占星預測結果，
推導讓球盤盤口並分析主客優劣。

核心功能:
1. 歐賠轉換隱含概率 (含去除莊家水位)
2. 推導亞盤盤口 (handicap line)
3. 與占星預測交叉比較，尋找價值投注
"""

from dataclasses import dataclass
from typing import Optional

# ============================================================
# 亞盤盤口對照表 — 主隊隱含勝率區間 → 建議盤口
# ============================================================
# 隱含概率差 = P(home) - P(away)
# 正值表示主隊較強，負值表示客隊較強
_HANDICAP_TABLE = [
    # (prob_diff_lower, prob_diff_upper, handicap_line, label)
    (0.35, 1.00, -2.0, "主隊讓兩球"),
    (0.28, 0.35, -1.75, "主隊讓球半/兩球"),
    (0.22, 0.28, -1.5, "主隊讓球半"),
    (0.17, 0.22, -1.25, "主隊讓一球/球半"),
    (0.12, 0.17, -1.0, "主隊讓一球"),
    (0.07, 0.12, -0.75, "主隊讓半球/一球"),
    (0.03, 0.07, -0.5, "主隊讓半球"),
    (0.00, 0.03, -0.25, "主隊讓平手/半球"),
    (-0.03, 0.00, 0.0, "平手盤"),
    (-0.07, -0.03, 0.25, "客隊讓平手/半球"),
    (-0.12, -0.07, 0.5, "客隊讓半球"),
    (-0.17, -0.12, 0.75, "客隊讓半球/一球"),
    (-0.22, -0.17, 1.0, "客隊讓一球"),
    (-0.28, -0.22, 1.25, "客隊讓一球/球半"),
    (-0.35, -0.28, 1.5, "客隊讓球半"),
    (-1.00, -0.35, 2.0, "客隊讓兩球"),
]


# Threshold for determining odds favorite (percentage points difference)
ODDS_FAVORITE_THRESHOLD = 3.0

# Minimum edge (%) for identifying a value bet opportunity
VALUE_THRESHOLD = 5.0


@dataclass
class HandicapAnalysis:
    """亞盤分析結果"""

    # 歐賠輸入
    home_odds: float
    draw_odds: float
    away_odds: float

    # 莊家水位 (overround)
    bookmaker_margin: float  # e.g. 0.05 = 5%

    # 去除水位後的隱含概率
    implied_home_pct: float
    implied_draw_pct: float
    implied_away_pct: float

    # 推導的亞盤盤口
    handicap_line: float  # e.g. -0.5, -1.0, +0.5
    handicap_label: str  # 中文描述

    # 佔優方
    odds_favorite: str  # "home", "away", "even"
    odds_favorite_label: str  # 中文描述

    # 占星 vs 賠率比較
    astro_home_pct: float
    astro_away_pct: float
    astro_draw_pct: float
    value_bet: Optional[str]  # 如有價值投注的描述
    value_bet_side: Optional[str]  # "home", "away", "draw" or None
    value_edge: float  # 占星概率 - 隱含概率的差值

    # 綜合建議
    summary: str


def compute_implied_probabilities(
    home_odds: float,
    draw_odds: float,
    away_odds: float,
) -> tuple[float, float, float, float]:
    """將歐賠轉換為去除水位的隱含概率。

    Args:
        home_odds: 主勝歐賠
        draw_odds: 和局歐賠
        away_odds: 客勝歐賠

    Returns:
        (implied_home, implied_draw, implied_away, margin)
        各概率為 0~100 的百分比，margin 為莊家水位
    """
    raw_home = 1.0 / home_odds
    raw_draw = 1.0 / draw_odds
    raw_away = 1.0 / away_odds
    total = raw_home + raw_draw + raw_away

    margin = total - 1.0  # overround

    # 去除水位：按比例分配
    implied_home = (raw_home / total) * 100.0
    implied_draw = (raw_draw / total) * 100.0
    implied_away = (raw_away / total) * 100.0

    return implied_home, implied_draw, implied_away, margin


def derive_handicap_line(implied_home_pct: float, implied_away_pct: float) -> tuple[float, str]:
    """從隱含概率推導亞盤盤口。

    Args:
        implied_home_pct: 主隊隱含勝率 (0~100)
        implied_away_pct: 客隊隱含勝率 (0~100)

    Returns:
        (handicap_line, label) — 盤口數值及中文描述
    """
    prob_diff = (implied_home_pct - implied_away_pct) / 100.0

    for lower, upper, line, label in _HANDICAP_TABLE:
        if lower <= prob_diff < upper:
            return line, label

    # Fallback for extreme cases
    if prob_diff >= 0:
        return -2.5, "主隊讓兩球半或以上"
    return 2.5, "客隊讓兩球半或以上"


def analyze_handicap(
    home_odds: float,
    draw_odds: float,
    away_odds: float,
    astro_home_pct: float,
    astro_away_pct: float,
    astro_draw_pct: float,
    home_team: str,
    away_team: str,
) -> HandicapAnalysis:
    """執行完整亞盤分析。

    Args:
        home_odds: 主勝歐賠 (decimal)
        draw_odds: 和局歐賠 (decimal)
        away_odds: 客勝歐賠 (decimal)
        astro_home_pct: 占星預測主隊勝率 (%)
        astro_away_pct: 占星預測客隊勝率 (%)
        astro_draw_pct: 占星預測平局概率 (%)
        home_team: 主隊名稱
        away_team: 客隊名稱

    Returns:
        HandicapAnalysis 完整分析結果
    """
    # 1. 隱含概率
    imp_home, imp_draw, imp_away, margin = compute_implied_probabilities(
        home_odds, draw_odds, away_odds
    )

    # 2. 推導盤口
    handicap_line, handicap_label = derive_handicap_line(imp_home, imp_away)

    # 3. 盤口佔優方
    if imp_home > imp_away + ODDS_FAVORITE_THRESHOLD:
        odds_favorite = "home"
        odds_favorite_label = f"{home_team} (主隊) 佔優"
    elif imp_away > imp_home + ODDS_FAVORITE_THRESHOLD:
        odds_favorite = "away"
        odds_favorite_label = f"{away_team} (客隊) 佔優"
    else:
        odds_favorite = "even"
        odds_favorite_label = "雙方均勢"

    # 4. 價值投注分析 — 占星概率 vs 隱含概率
    home_edge = astro_home_pct - imp_home
    away_edge = astro_away_pct - imp_away
    draw_edge = astro_draw_pct - imp_draw

    value_bet = None
    value_bet_side = None
    value_edge = 0.0

    edges = [
        ("home", home_edge, f"{home_team} (主勝)"),
        ("away", away_edge, f"{away_team} (客勝)"),
        ("draw", draw_edge, "和局"),
    ]
    best_side, best_edge, best_label = max(edges, key=lambda x: x[1])

    if best_edge >= VALUE_THRESHOLD:
        value_bet_side = best_side
        value_edge = best_edge
        value_bet = (
            f"占星預測 {best_label} 概率 ({_get_astro_pct(best_side, astro_home_pct, astro_away_pct, astro_draw_pct):.1f}%) "
            f"高於賠率隱含概率 ({_get_imp_pct(best_side, imp_home, imp_away, imp_draw):.1f}%)，"
            f"存在 {best_edge:.1f}% 的價值優勢"
        )

    # 5. 綜合建議摘要
    summary = _build_summary(
        home_team, away_team,
        imp_home, imp_draw, imp_away,
        handicap_line, handicap_label,
        odds_favorite, odds_favorite_label,
        astro_home_pct, astro_away_pct, astro_draw_pct,
        value_bet, value_bet_side, value_edge,
        margin,
    )

    return HandicapAnalysis(
        home_odds=home_odds,
        draw_odds=draw_odds,
        away_odds=away_odds,
        bookmaker_margin=round(margin * 100, 2),
        implied_home_pct=round(imp_home, 1),
        implied_draw_pct=round(imp_draw, 1),
        implied_away_pct=round(imp_away, 1),
        handicap_line=handicap_line,
        handicap_label=handicap_label,
        odds_favorite=odds_favorite,
        odds_favorite_label=odds_favorite_label,
        astro_home_pct=round(astro_home_pct, 1),
        astro_away_pct=round(astro_away_pct, 1),
        astro_draw_pct=round(astro_draw_pct, 1),
        value_bet=value_bet,
        value_bet_side=value_bet_side,
        value_edge=round(value_edge, 1),
        summary=summary,
    )


# ============================================================
# 內部工具函式
# ============================================================

def _get_astro_pct(side: str, home: float, away: float, draw: float) -> float:
    return {"home": home, "away": away, "draw": draw}.get(side, 0.0)


def _get_imp_pct(side: str, home: float, away: float, draw: float) -> float:
    return {"home": home, "away": away, "draw": draw}.get(side, 0.0)


def _build_summary(
    home_team: str,
    away_team: str,
    imp_home: float,
    imp_draw: float,
    imp_away: float,
    handicap_line: float,
    handicap_label: str,
    odds_favorite: str,
    odds_favorite_label: str,
    astro_home: float,
    astro_away: float,
    astro_draw: float,
    value_bet: Optional[str],
    value_bet_side: Optional[str],
    value_edge: float,
    margin: float,
) -> str:
    """建構亞盤分析摘要。"""

    lines = []

    # --- 賠率隱含概率 ---
    lines.append("**📊 賠率隱含概率 (去除水位後):**")
    lines.append(
        f"- {home_team} (主勝): {imp_home:.1f}% ｜ "
        f"和局: {imp_draw:.1f}% ｜ "
        f"{away_team} (客勝): {imp_away:.1f}%"
    )
    lines.append(f"- 莊家水位 (overround): {margin * 100:.1f}%")
    lines.append("")

    # --- 亞盤盤口 ---
    if handicap_line < 0:
        giving_team = home_team
        receiving_team = away_team
        abs_line = abs(handicap_line)
    elif handicap_line > 0:
        giving_team = away_team
        receiving_team = home_team
        abs_line = abs(handicap_line)
    else:
        giving_team = None
        receiving_team = None
        abs_line = 0

    lines.append(f"**🎯 推導亞盤盤口: {handicap_label}**")
    if giving_team:
        lines.append(
            f"- {giving_team} 讓 {abs_line} 球給 {receiving_team}"
        )
    else:
        lines.append("- 雙方平手盤，不讓球")
    lines.append("")

    # --- 佔優方 ---
    lines.append(f"**⚖️ 賠率判斷: {odds_favorite_label}**")
    lines.append("")

    # --- 占星 vs 賠率比較 ---
    lines.append("**🔮 占星預測 vs 賠率比較:**")
    lines.append(f"| | 占星預測 | 賠率隱含 | 差值 |")
    lines.append(f"|---|---|---|---|")

    home_diff = astro_home - imp_home
    away_diff = astro_away - imp_away
    draw_diff = astro_draw - imp_draw
    lines.append(
        f"| {home_team} (主勝) | {astro_home:.1f}% | {imp_home:.1f}% | "
        f"{home_diff:+.1f}% |"
    )
    lines.append(
        f"| {away_team} (客勝) | {astro_away:.1f}% | {imp_away:.1f}% | "
        f"{away_diff:+.1f}% |"
    )
    lines.append(
        f"| 和局 | {astro_draw:.1f}% | {imp_draw:.1f}% | "
        f"{draw_diff:+.1f}% |"
    )
    lines.append("")

    # --- 價值投注 ---
    if value_bet:
        lines.append(f"**💎 價值投注提示:**")
        lines.append(f"- {value_bet}")

        # 亞盤建議
        if value_bet_side == "home":
            if handicap_line <= 0:
                lines.append(
                    f"- 亞盤建議: 買入 {home_team} ({handicap_line}) 讓球盤"
                )
            else:
                lines.append(
                    f"- 亞盤建議: 買入 {home_team} 受讓 (+{abs(handicap_line)}) 盤"
                )
        elif value_bet_side == "away":
            if handicap_line >= 0:
                lines.append(
                    f"- 亞盤建議: 買入 {away_team} ({-handicap_line}) 讓球盤"
                )
            else:
                lines.append(
                    f"- 亞盤建議: 買入 {away_team} 受讓 (+{abs(handicap_line)}) 盤"
                )
        else:
            lines.append("- 亞盤建議: 占星傾向和局，考慮平手盤或觀望")
    else:
        lines.append("**💎 價值投注提示:**")
        lines.append("- 占星預測與賠率大致一致，暫無明顯價值投注機會")
        lines.append("- 建議觀望或按賠率盤口投注")

    return "\n".join(lines)
