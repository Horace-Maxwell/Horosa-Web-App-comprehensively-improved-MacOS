"""
預測引擎 (Prediction Engine)

融合 Frawley (Western) 與 Vedic 判斷結果，產出最終預測。

流程：
1. 起盤 (Chart Casting): 同時計算 Western + Vedic 星盤
2. 分別執行 Frawley 判斷 和 Vedic 判斷
3. 加權合併兩方結果
4. 輸出勝率、比分趨勢、投注建議
"""

from .models import MatchInput, PredictionResult, SportsPrediction
from .chart_calculator import (
    compute_western_chart, compute_vedic_chart,
    format_longitude, format_vedic_longitude,
)
from .frawley_judgment import frawley_judgment
from .vedic_judgment import vedic_judgment
from .asian_handicap import analyze_handicap

# Draw probability — smooth interpolation parameters
# In football, draws happen ~25% overall; even in lopsided matches ~18-20%.
DRAW_PCT_MAX = 35.0          # draw % when margin ≈ 0 (evenly matched)
DRAW_PCT_MIN = 18.0          # draw % floor even for very one-sided charts
MARGIN_CAP = 0.50            # margin at which draw % reaches its floor

# Bonus draw % when Frawley and Vedic disagree on the winner direction
DISAGREEMENT_DRAW_BONUS = 5.0

# Absolute ceiling for draw probability (even with disagreement bonus)
DRAW_PCT_ABSOLUTE_MAX = 40.0

# Home underdog advantage — in football the home team has a well-documented
# statistical edge (~46% home wins vs ~27% away wins).  When the away team is
# the astrological favourite and the home team is assigned as the underdog,
# shift some combined probability toward the home side.
HOME_UNDERDOG_BOOST = 0.08   # absolute probability shift toward home

# Confidence thresholds
CONFIDENCE_HIGH_THRESHOLD = 0.35
CONFIDENCE_MEDIUM_THRESHOLD = 0.15


def predict_match(match: MatchInput) -> PredictionResult:
    """對單場比賽進行完整預測

    Args:
        match: MatchInput 資料

    Returns:
        PredictionResult 包含所有分析結果
    """
    # Step 1: 起盤
    western_chart = compute_western_chart(match)
    vedic_chart = compute_vedic_chart(match)

    # Step 2: Frawley 判斷
    frawley_result = frawley_judgment(
        western_chart,
        match.home_team,
        match.away_team,
        match.favorite,
    )

    # Step 3: Vedic 判斷
    vedic_result = vedic_judgment(
        vedic_chart,
        match.home_team,
        match.away_team,
    )

    # Step 4: 合併結果
    # Normalize scores to percentages
    f_total = frawley_result["home_score"] + frawley_result["away_score"]
    if f_total == 0:
        f_total = 1
    f_home_pct = frawley_result["home_score"] / f_total
    f_away_pct = frawley_result["away_score"] / f_total

    v_total = vedic_result["home_points"] + vedic_result["away_points"]
    if v_total == 0:
        v_total = 1
    v_home_pct = vedic_result["home_points"] / v_total
    v_away_pct = vedic_result["away_points"] / v_total

    # Weighted combination: keep Frawley as dominant, with mode-specific tuning.
    mode = match.analysis_mode
    if mode == "event":
        frawley_weight = 0.55
        vedic_weight = 0.45
    else:
        frawley_weight = 0.60
        vedic_weight = 0.40

    combined_home = f_home_pct * frawley_weight + v_home_pct * vedic_weight
    combined_away = f_away_pct * frawley_weight + v_away_pct * vedic_weight

    # Home underdog advantage: when the away team is the favourite, the
    # home team still benefits from playing on their own ground (crowd,
    # no travel, pitch familiarity).  Apply an absolute probability shift
    # toward the home side, clamped so it never flips the order.
    if match.favorite == "away":
        boost = HOME_UNDERDOG_BOOST
        new_home = min(combined_home + boost, combined_away - 0.01)
        new_away = max(combined_away - boost, new_home + 0.01)
        pair_sum = new_home + new_away
        combined_home = new_home / pair_sum
        combined_away = new_away / pair_sum

    # Calculate draw probability — smooth linear interpolation
    margin = abs(combined_home - combined_away)
    t = min(margin / MARGIN_CAP, 1.0)          # 0 → 1
    draw_pct = DRAW_PCT_MAX - (DRAW_PCT_MAX - DRAW_PCT_MIN) * t

    # Disagreement bonus: if Frawley and Vedic favour different sides,
    # that signals genuine uncertainty → boost draw probability.
    frawley_favors_home = f_home_pct > f_away_pct
    vedic_favors_home = v_home_pct > v_away_pct
    if frawley_favors_home != vedic_favors_home:
        draw_pct += DISAGREEMENT_DRAW_BONUS

    # Cap draw_pct to a sensible maximum
    draw_pct = min(draw_pct, DRAW_PCT_ABSOLUTE_MAX)

    # Adjust home/away with draw
    remaining = 100.0 - draw_pct
    home_win_pct = combined_home * remaining
    away_win_pct = combined_away * remaining

    # Determine winner
    if home_win_pct > away_win_pct and (home_win_pct - away_win_pct) > 5:
        predicted_winner = "home"
    elif away_win_pct > home_win_pct and (away_win_pct - home_win_pct) > 5:
        predicted_winner = "away"
    else:
        predicted_winner = "draw"

    # Confidence level
    if margin > CONFIDENCE_HIGH_THRESHOLD:
        confidence = "high"
    elif margin > CONFIDENCE_MEDIUM_THRESHOLD:
        confidence = "medium"
    else:
        confidence = "low"
    confidence_score = round(min(0.99, max(0.10, 0.5 + margin * 0.9)), 3)

    # Score trend (Frawley: most games losers score ≤1, winners score 1-2)
    score_trend = _estimate_score_trend(
        home_win_pct, away_win_pct, draw_pct, predicted_winner)

    # Betting recommendation
    bet_recommendation = _bet_recommendation(
        home_win_pct, away_win_pct, draw_pct, confidence)

    # Step 5: 亞盤分析 (如有提供賠率)
    handicap_result = None
    if (match.home_odds is not None
            and match.draw_odds is not None
            and match.away_odds is not None):
        handicap_result = analyze_handicap(
            home_odds=match.home_odds,
            draw_odds=match.draw_odds,
            away_odds=match.away_odds,
            astro_home_pct=round(home_win_pct, 1),
            astro_away_pct=round(away_win_pct, 1),
            astro_draw_pct=round(draw_pct, 1),
            home_team=match.home_team,
            away_team=match.away_team,
        )

    injury_risk = frawley_result.get("injury_risk", {"home": 0.15, "away": 0.15})
    reversal_indicator = float(frawley_result.get("reversal_indicator", 0.5))
    key_factors = _extract_key_factors(
        frawley_result["evidences"], frawley_result.get("testimonies", {})
    )

    sports_prediction = SportsPrediction(
        mode=mode,
        winner_prob={
            match.home_team: round(home_win_pct / 100.0, 4),
            match.away_team: round(away_win_pct / 100.0, 4),
            "draw": round(draw_pct / 100.0, 4),
        },
        confidence=confidence_score,
        key_factors=key_factors,
        score_estimate=score_trend,
        injury_risk=injury_risk,
        reversal_indicator=reversal_indicator,
        disclaimers=[
            "Probabilistic astrology guidance only; not deterministic.",
            "Bet responsibly and combine with injuries, tactics, and market data.",
        ],
    )

    # Build summaries
    frawley_summary = frawley_result["summary"]
    vedic_summary = vedic_result["summary"]
    combined_summary = _build_combined_summary(
        match, home_win_pct, away_win_pct, draw_pct,
        predicted_winner, confidence, score_trend)

    return PredictionResult(
        home_team=match.home_team,
        away_team=match.away_team,
        home_win_pct=round(home_win_pct, 1),
        away_win_pct=round(away_win_pct, 1),
        draw_pct=round(draw_pct, 1),
        predicted_winner=predicted_winner,
        confidence=confidence,
        score_trend=score_trend,
        frawley_evidences=frawley_result["evidences"],
        vedic_evidences=vedic_result["evidences"],
        frawley_summary=frawley_summary,
        vedic_summary=vedic_summary,
        combined_summary=combined_summary,
        bet_recommendation=bet_recommendation,
        western_chart=western_chart,
        vedic_chart=vedic_chart,
        handicap_analysis=handicap_result,
        sports_prediction=sports_prediction,
    )


def _estimate_score_trend(
    home_pct: float,
    away_pct: float,
    draw_pct: float,
    winner: str,
) -> str:
    """估算比分趨勢

    Frawley 觀察: 大多數比賽中輸方 ≤1 球，勝方多 1-2 球
    """
    if winner == "draw":
        if draw_pct > 30:
            return "0-0 或 1-1 (低比分平局可能性高)"
        return "1-1 或 2-2 (平局)"

    dominant_pct = max(home_pct, away_pct)
    if dominant_pct > 55:
        return "2-0 或 2-1 (優勢方明顯領先)"
    if dominant_pct > 45:
        return "1-0 或 2-1 (小勝可能性高)"
    return "1-0 或 1-1 (接近的比賽)"


def _bet_recommendation(
    home_pct: float,
    away_pct: float,
    draw_pct: float,
    confidence: str,
) -> str:
    """投注建議"""
    if confidence == "low":
        return "⚠️ 信心不足，建議觀望。雙方實力接近，風險較高。"

    if confidence == "high":
        if home_pct > away_pct:
            return (f"✅ 可考慮投注主隊勝 (預估勝率 {home_pct:.1f}%)。"
                    f"信心較高，但請控制注碼。")
        else:
            return (f"✅ 可考慮投注客隊勝 (預估勝率 {away_pct:.1f}%)。"
                    f"信心較高，但請控制注碼。")

    # Medium confidence
    if home_pct > away_pct:
        return (f"🔄 主隊略佔優勢 (預估勝率 {home_pct:.1f}%)。"
                f"可小額嘗試，注意賠率是否值得。")
    elif away_pct > home_pct:
        return (f"🔄 客隊略佔優勢 (預估勝率 {away_pct:.1f}%)。"
                f"可小額嘗試，注意賠率是否值得。")
    return "🔄 雙方均等，考慮投注平局或觀望。"


def _build_combined_summary(match, home_pct, away_pct, draw_pct,
                            winner, confidence, score_trend):
    """建構綜合摘要"""
    lines = [
        f"{'='*60}",
        f"⚽ 足球比賽預測報告",
        f"{'='*60}",
        f"比賽: {match.home_team} (主) vs {match.away_team} (客)",
        f"時間: {match.year}/{match.month:02d}/{match.day:02d} "
        f"{match.hour:02d}:{match.minute:02d} (UTC{match.timezone:+.1f})",
        f"地點: {match.location_name} "
        f"({match.latitude:.4f}°, {match.longitude:.4f}°)",
        f"",
        f"📊 預測結果:",
        f"  主隊勝率: {home_pct:.1f}%",
        f"  客隊勝率: {away_pct:.1f}%",
        f"  平局機率: {draw_pct:.1f}%",
        f"",
        f"🏆 預測勝方: ",
    ]

    if winner == "home":
        lines[-1] += f"{match.home_team} (主隊)"
    elif winner == "away":
        lines[-1] += f"{match.away_team} (客隊)"
    else:
        lines[-1] += "平局"

    lines.extend([
        f"📈 信心等級: {confidence}",
        f"⚽ 比分趨勢: {score_trend}",
        f"{'='*60}",
    ])

    return "\n".join(lines)


def _extract_key_factors(evidences: list, testimonies: dict) -> list[str]:
    """抽取關鍵證據，優先輸出高權重 testimony。"""
    sorted_ev = sorted(evidences, key=lambda x: x.weight, reverse=True)
    factors = [f"[{ev.category}] {ev.description}" for ev in sorted_ev[:6]]
    leader = testimonies.get("leader")
    margin = testimonies.get("margin")
    if leader and margin is not None:
        factors.insert(0, f"Lord 1 vs Lord 7 leader={leader}, margin={margin:+.2f}")
    return factors


def format_prediction_report(result: PredictionResult) -> str:
    """格式化完整預測報告 (文字版)"""
    lines = [result.combined_summary, ""]

    # Frawley analysis
    lines.append("=" * 60)
    lines.append("📖 Frawley (西洋卜卦) 分析")
    lines.append("=" * 60)
    lines.append(result.frawley_summary)
    lines.append("")
    for i, ev in enumerate(result.frawley_evidences, 1):
        icon = "🏠" if ev.favors == "home" else "✈️" if ev.favors == "away" \
            else "⚖️"
        lines.append(f"  {i}. {icon} [{ev.category}] {ev.description} "
                     f"(權重: {ev.weight:.1f})")
    lines.append("")

    # Vedic analysis
    lines.append("=" * 60)
    lines.append("🕉️ Vedic (吠陀占星) 分析")
    lines.append("=" * 60)
    lines.append(result.vedic_summary)
    lines.append("")
    for i, ev in enumerate(result.vedic_evidences, 1):
        icon = "🏠" if ev.favors == "home" else "✈️" if ev.favors == "away" \
            else "⚖️"
        tier_label = f"T{ev.tier}"
        lines.append(f"  {i}. {icon} [{tier_label}/{ev.category}] "
                     f"{ev.description} (分數: {ev.points:.0f})")
    lines.append("")

    # Chart info
    if result.western_chart:
        lines.append("=" * 60)
        lines.append("🌍 Western Chart (Regiomontanus)")
        lines.append("=" * 60)
        lines.append(f"  ASC: {format_longitude(result.western_chart.ascendant)}")
        lines.append(f"  MC:  {format_longitude(result.western_chart.midheaven)}")
        lines.append("")
        lines.append("  行星位置:")
        for p in result.western_chart.planets:
            retro = " ℞" if p.retrograde else ""
            dig = f" [{p.essential_dignity}]" if p.essential_dignity != "peregrine" else ""
            lines.append(f"    {p.name:10s} {format_longitude(p.longitude):25s} "
                         f"H{p.house:2d}{retro}{dig}")
        lines.append("")

    if result.vedic_chart:
        lines.append("=" * 60)
        lines.append("🕉️ Vedic Chart (Sidereal/Lahiri)")
        lines.append("=" * 60)
        lines.append(f"  ASC: {format_vedic_longitude(result.vedic_chart.ascendant)}")
        lines.append(f"  Ayanamsa: {result.vedic_chart.ayanamsa:.4f}°")
        lines.append("")
        lines.append("  行星位置 (Rasi D1):")
        for p in result.vedic_chart.planets:
            retro = " ℞" if p.retrograde else ""
            lines.append(f"    {p.name:10s} {format_vedic_longitude(p.longitude):25s} "
                         f"H{p.house:2d} Nak:{p.nakshatra:18s} P{p.nakshatra_pada}{retro}")
        lines.append("")
        lines.append("  Navamsa (D9) 位置:")
        for p in result.vedic_chart.navamsa_planets:
            lines.append(f"    {p.name:10s} {format_vedic_longitude(p.longitude):25s} "
                         f"H{p.house:2d}")
        lines.append("")

    # Asian Handicap analysis (if available)
    if result.handicap_analysis:
        ha = result.handicap_analysis
        lines.append("=" * 60)
        lines.append("🎯 亞洲讓球盤 (Asian Handicap) 分析")
        lines.append("=" * 60)
        lines.append(f"  歐賠: 主勝 {ha.home_odds:.2f} / 和局 {ha.draw_odds:.2f} / 客勝 {ha.away_odds:.2f}")
        lines.append(f"  莊家水位: {ha.bookmaker_margin:.1f}%")
        lines.append(f"  隱含概率: 主勝 {ha.implied_home_pct:.1f}% / 和局 {ha.implied_draw_pct:.1f}% / 客勝 {ha.implied_away_pct:.1f}%")
        lines.append(f"  推導盤口: {ha.handicap_label} ({ha.handicap_line:+.2f})")
        lines.append(f"  賠率佔優: {ha.odds_favorite_label}")
        if ha.value_bet:
            lines.append(f"  💎 價值投注: {ha.value_bet}")
        else:
            lines.append("  📌 暫無明顯價值投注機會")
        lines.append("")

    if result.sports_prediction:
        sp = result.sports_prediction
        lines.append("=" * 60)
        lines.append("🧭 Structured SportsPrediction")
        lines.append("=" * 60)
        lines.append(f"  Mode: {sp.mode}")
        lines.append(f"  Confidence: {sp.confidence:.2f}")
        lines.append(
            f"  Injury risk: home {sp.injury_risk.get('home', 0.0):.2%} / "
            f"away {sp.injury_risk.get('away', 0.0):.2%}"
        )
        lines.append(f"  Reversal indicator: {sp.reversal_indicator:.2%}")
        lines.append("  Key factors:")
        for factor in sp.key_factors[:6]:
            lines.append(f"    - {factor}")
        lines.append("")

    # Betting
    lines.append("=" * 60)
    lines.append("💰 投注建議")
    lines.append("=" * 60)
    lines.append(result.bet_recommendation)
    lines.append("")
    lines.append("⚠️ 免責聲明: 本工具僅供娛樂與學習用途。")
    lines.append("   占星預測不保證準確，投注有風險，請謹慎理財。")
    lines.append("=" * 60)

    return "\n".join(lines)
