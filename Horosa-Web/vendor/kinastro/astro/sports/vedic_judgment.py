"""
Vedic 判斷引擎 (Vedic Judgment Engine)

實作 Simon Chokoisky《Gambler's Dharma》的核心規則：

三層級 (Tier) 體系：
- 第一層 (Tier 1, 2-4 分): 勝利宮位 (Victory Houses), Navamsa 組合
- 第二層 (Tier 2, 7-9 分): SKY/PKY, 宮主強度 (Lord Strength), 從屬技術,
                           行星戰爭 (Graha Yuddha), 互換接納 (Parivartana Yoga)
- 第三層 (Tier 3, 14-18 分): Navamsa 宮主強度 (最強), Navamsa 宮頭強度

核心技術：
1. 勝利宮位 (Victory Houses): 1,3,6,10,11 為有利宮位
2. 宮頭強度 (Cuspal Strength): 行星緊貼宮頭的影響
3. Navamsa (D9) 分析: 心智與靈性層面
4. 宮主比較 (Lord comparison): 1宮主 vs 7宮主
5. 從屬星分析 (Sublord analysis)
6. SKY/PKY (Shubha/Papa Kartari Yoga): 吉星/凶星夾持宮位
7. 行星戰爭 (Graha Yuddha): 1/7宮主距離≤1°時的戰爭
8. 互換接納 (Parivartana Yoga): 行星互換星座帶來額外力量
"""

from .models import VedicEvidence
from .chart_calculator import (
    VedicChartData, _normalize, _sign_index, _angle_diff,
    VEDIC_RULERS, RASHI_NAMES,
    DOMICILE, EXALTATION, DETRIMENT, FALL,
    get_planet_by_name,
)

# Victory houses for favorite (1st house team)
VICTORY_HOUSES_FAVORITE = {1, 3, 6, 10, 11}
# Victory houses for underdog (7th house team)
VICTORY_HOUSES_UNDERDOG = {4, 5, 7, 9, 12}
# Neutral houses
NEUTRAL_HOUSES = {2, 8}

# Benefic/Malefic classification in Vedic
VEDIC_BENEFICS = {"Jupiter", "Venus", "Moon", "Mercury"}
VEDIC_MALEFICS = {"Saturn", "Mars", "Sun", "Rahu", "Ketu"}


def _get_vedic_dignity(planet_name: str, rashi_index: int) -> str:
    """取得 Vedic 行星尊貴狀態"""
    name = planet_name
    if name in ("Rahu", "Ketu"):
        return "shadow"

    if rashi_index in DOMICILE.get(name, []):
        return "own_sign"
    if EXALTATION.get(name) == rashi_index:
        return "exalted"
    if rashi_index in DETRIMENT.get(name, []):
        return "detriment"
    if FALL.get(name) == rashi_index:
        return "debilitated"
    return "neutral"


# ============================================================
# 技術 1: 勝利宮位 (Victory Houses) — Tier 1
# ============================================================

def evaluate_victory_houses(chart: VedicChartData) -> list:
    """分析勝利宮位中的行星

    Gambler's Dharma:
    - 行星落入 1,3,6,10,11 宮 → 有利 favorite (1宮隊)
    - 行星落入 4,5,7,9,12 宮 → 有利 underdog (7宮隊)
    - 2,8 宮 → 中性
    - 吉星影響更正面, 凶星帶來身體力量

    Returns: list of VedicEvidence
    """
    evidences = []
    fav_count = 0
    und_count = 0

    for p in chart.planets:
        if p.name in ("Rahu", "Ketu"):
            continue  # Nodes handled separately

        if p.house in VICTORY_HOUSES_FAVORITE:
            fav_count += 1
        elif p.house in VICTORY_HOUSES_UNDERDOG:
            und_count += 1

    if fav_count > und_count:
        diff = fav_count - und_count
        pts = min(diff * 2, 4)  # Tier 1: 2-4 points
        evidences.append(VedicEvidence(
            description=f"勝利宮位: {fav_count} 顆行星在主隊有利宮位 vs "
                        f"{und_count} 顆在客隊有利宮位",
            favors="home", tier=1, points=pts,
            category="victory_houses"))
    elif und_count > fav_count:
        diff = und_count - fav_count
        pts = min(diff * 2, 4)
        evidences.append(VedicEvidence(
            description=f"勝利宮位: {und_count} 顆行星在客隊有利宮位 vs "
                        f"{fav_count} 顆在主隊有利宮位",
            favors="away", tier=1, points=pts,
            category="victory_houses"))
    else:
        evidences.append(VedicEvidence(
            description=f"勝利宮位: 雙方均等 ({fav_count} vs {und_count})",
            favors="neutral", tier=1, points=0,
            category="victory_houses"))

    return evidences


# ============================================================
# 技術 2: 宮頭強度 (Cuspal Strength) — Tier 2
# ============================================================

def evaluate_cuspal_strength(chart: VedicChartData) -> list:
    """分析宮頭行星影響

    Gambler's Dharma:
    - 行星緊貼第1宮或第7宮宮頭 (≤2.5°) → 強力影響
    - 吉星有利, 凶星不利
    - Tier 2 strength (7-9 pts)
    """
    evidences = []
    cusp_1 = chart.houses[0].cusp
    cusp_7 = chart.houses[6].cusp

    for p in chart.planets:
        # Check proximity to 1st house cusp
        dist_1 = _angle_diff(p.longitude, cusp_1)
        if dist_1 <= 2.5:
            is_benefic = p.name in VEDIC_BENEFICS
            dignity = _get_vedic_dignity(p.name, p.rashi_index)
            is_strong = dignity in ("own_sign", "exalted")

            if is_benefic or is_strong:
                pts = 8 if dist_1 <= 1.0 else 7
                evidences.append(VedicEvidence(
                    description=f"{p.name} (吉星/尊貴) 緊貼第1宮宮頭 "
                                f"({dist_1:.1f}°) — 有利主隊",
                    favors="home", tier=2, points=pts,
                    category="cuspal_strength"))
            else:
                pts = 8 if dist_1 <= 1.0 else 7
                evidences.append(VedicEvidence(
                    description=f"{p.name} (凶星/衰弱) 緊貼第1宮宮頭 "
                                f"({dist_1:.1f}°) — 不利主隊",
                    favors="away", tier=2, points=pts,
                    category="cuspal_strength"))

        # Check proximity to 7th house cusp
        dist_7 = _angle_diff(p.longitude, cusp_7)
        if dist_7 <= 2.5:
            is_benefic = p.name in VEDIC_BENEFICS
            dignity = _get_vedic_dignity(p.name, p.rashi_index)
            is_strong = dignity in ("own_sign", "exalted")

            if is_benefic or is_strong:
                pts = 8 if dist_7 <= 1.0 else 7
                evidences.append(VedicEvidence(
                    description=f"{p.name} (吉星/尊貴) 緊貼第7宮宮頭 "
                                f"({dist_7:.1f}°) — 有利客隊",
                    favors="away", tier=2, points=pts,
                    category="cuspal_strength"))
            else:
                pts = 8 if dist_7 <= 1.0 else 7
                evidences.append(VedicEvidence(
                    description=f"{p.name} (凶星/衰弱) 緊貼第7宮宮頭 "
                                f"({dist_7:.1f}°) — 不利客隊",
                    favors="home", tier=2, points=pts,
                    category="cuspal_strength"))

    return evidences


# ============================================================
# 技術 3: 宮主強度 (Lord Strength) — Tier 2
# ============================================================

def evaluate_lord_strength(chart: VedicChartData) -> list:
    """比較第1宮主與第7宮主的強度

    Gambler's Dharma:
    - 宮主在自己的宮位/擢升 → 強
    - 宮主在有利宮位 → 強
    - 宮主在衰弱宮位 → 弱
    """
    evidences = []

    lord_1_name = chart.houses[0].lord
    lord_7_name = chart.houses[6].lord

    lord_1 = get_planet_by_name(chart.planets, lord_1_name)
    lord_7 = get_planet_by_name(chart.planets, lord_7_name)

    if not lord_1 or not lord_7:
        return evidences

    # Score each lord
    def score_lord(lord, house_num):
        s = 0
        dignity = _get_vedic_dignity(lord.name, lord.rashi_index)
        if dignity == "exalted":
            s += 3
        elif dignity == "own_sign":
            s += 2
        elif dignity == "debilitated":
            s -= 3
        elif dignity == "detriment":
            s -= 2

        # House placement
        if lord.house in {1, 4, 7, 10}:  # Angular
            s += 2
        elif lord.house in {6, 8, 12}:  # Dusthana
            s -= 1

        # In own house
        if lord.house == house_num:
            s += 1

        return s

    score_1 = score_lord(lord_1, 1)
    score_7 = score_lord(lord_7, 7)

    if score_1 > score_7:
        pts = min((score_1 - score_7) * 3, 9)
        evidences.append(VedicEvidence(
            description=f"宮主強度: {lord_1_name} (1宮主, 分={score_1}) "
                        f"強於 {lord_7_name} (7宮主, 分={score_7})",
            favors="home", tier=2, points=pts,
            category="lord_strength"))
    elif score_7 > score_1:
        pts = min((score_7 - score_1) * 3, 9)
        evidences.append(VedicEvidence(
            description=f"宮主強度: {lord_7_name} (7宮主, 分={score_7}) "
                        f"強於 {lord_1_name} (1宮主, 分={score_1})",
            favors="away", tier=2, points=pts,
            category="lord_strength"))
    else:
        evidences.append(VedicEvidence(
            description=f"宮主強度: {lord_1_name} 與 {lord_7_name} 均等 (分={score_1})",
            favors="neutral", tier=2, points=0,
            category="lord_strength"))

    return evidences


# ============================================================
# 技術 4: Navamsa 宮主強度 (D9 Cuspal Strength) — Tier 3
# ============================================================

def evaluate_navamsa_cuspal(chart: VedicChartData) -> list:
    """分析 Navamsa (D9) 第1宮和第7宮的行星

    Gambler's Dharma:
    - D9 中行星落入第1宮或第7宮 → Tier 3 (最強) 影響
    - 吉星有利, 凶星不利
    - 容許度: 可見行星 2°30', 不可見行星 2°
    """
    evidences = []

    for np in chart.navamsa_planets:
        if np.name in ("Rahu", "Ketu"):
            continue

        if np.house == 1:
            is_benefic = np.name in VEDIC_BENEFICS
            dignity = _get_vedic_dignity(np.name, np.rashi_index)
            is_strong = dignity in ("own_sign", "exalted")

            if is_benefic or is_strong:
                evidences.append(VedicEvidence(
                    description=f"D9: {np.name} (吉/尊貴) 落入 Navamsa 第1宮 — "
                                f"主隊心智與靈性層面極強",
                    favors="home", tier=3, points=16,
                    category="navamsa_cuspal"))
            else:
                evidences.append(VedicEvidence(
                    description=f"D9: {np.name} (凶/衰弱) 落入 Navamsa 第1宮 — "
                                f"主隊心智與靈性層面受損",
                    favors="away", tier=3, points=16,
                    category="navamsa_cuspal"))

        elif np.house == 7:
            is_benefic = np.name in VEDIC_BENEFICS
            dignity = _get_vedic_dignity(np.name, np.rashi_index)
            is_strong = dignity in ("own_sign", "exalted")

            if is_benefic or is_strong:
                evidences.append(VedicEvidence(
                    description=f"D9: {np.name} (吉/尊貴) 落入 Navamsa 第7宮 — "
                                f"客隊心智與靈性層面極強",
                    favors="away", tier=3, points=16,
                    category="navamsa_cuspal"))
            else:
                evidences.append(VedicEvidence(
                    description=f"D9: {np.name} (凶/衰弱) 落入 Navamsa 第7宮 — "
                                f"客隊心智與靈性層面受損",
                    favors="home", tier=3, points=16,
                    category="navamsa_cuspal"))

    return evidences


# ============================================================
# 技術 5: Navamsa 宮主比較 — Tier 3
# ============================================================

def evaluate_navamsa_lords(chart: VedicChartData) -> list:
    """比較 Navamsa 第1宮主與第7宮主

    Gambler's Dharma:
    - D9 的1宮主 vs 7宮主比較
    - 在 D9 中尊貴 → 極強影響 (Tier 3)
    """
    evidences = []

    nav_asc_idx = chart.navamsa_asc_rashi_index
    nav_7th_idx = (nav_asc_idx + 6) % 12

    lord_1_name = VEDIC_RULERS[nav_asc_idx]
    lord_7_name = VEDIC_RULERS[nav_7th_idx]

    # Find these lords in navamsa
    lord_1 = get_planet_by_name(chart.navamsa_planets, lord_1_name)
    lord_7 = get_planet_by_name(chart.navamsa_planets, lord_7_name)

    if not lord_1 or not lord_7:
        return evidences

    dig_1 = _get_vedic_dignity(lord_1.name, lord_1.rashi_index)
    dig_7 = _get_vedic_dignity(lord_7.name, lord_7.rashi_index)

    dig_scores = {"exalted": 4, "own_sign": 3, "neutral": 0,
                  "detriment": -2, "debilitated": -3, "shadow": 0}

    s1 = dig_scores.get(dig_1, 0)
    s7 = dig_scores.get(dig_7, 0)

    if s1 > s7:
        pts = min((s1 - s7) * 4, 18)
        evidences.append(VedicEvidence(
            description=f"D9 宮主: {lord_1_name} ({dig_1}) 在 Navamsa 中"
                        f"強於 {lord_7_name} ({dig_7}) — 主隊靈性/運氣優勢",
            favors="home", tier=3, points=pts,
            category="navamsa_lords"))
    elif s7 > s1:
        pts = min((s7 - s1) * 4, 18)
        evidences.append(VedicEvidence(
            description=f"D9 宮主: {lord_7_name} ({dig_7}) 在 Navamsa 中"
                        f"強於 {lord_1_name} ({dig_1}) — 客隊靈性/運氣優勢",
            favors="away", tier=3, points=pts,
            category="navamsa_lords"))

    return evidences


# ============================================================
# 技術 6: 從屬星分析 (Sublord/Dispositor) — Tier 2
# ============================================================

def evaluate_dispositors(chart: VedicChartData) -> list:
    """分析從屬星 (Dispositor) 指向

    Gambler's Dharma:
    - 每顆行星的從屬星 (星座主宰星) 落入哪個宮位
    - 若從屬星在有利宮位 → 為該隊加分
    """
    evidences = []
    fav_count = 0
    und_count = 0

    for p in chart.planets:
        if p.name in ("Rahu", "Ketu"):
            continue
        dispositor_name = p.rashi_lord
        dispositor = get_planet_by_name(chart.planets, dispositor_name)
        if not dispositor:
            continue
        if dispositor.house in VICTORY_HOUSES_FAVORITE:
            fav_count += 1
        elif dispositor.house in VICTORY_HOUSES_UNDERDOG:
            und_count += 1

    if fav_count > und_count and (fav_count - und_count) >= 3:
        pts = min((fav_count - und_count) * 2, 9)
        evidences.append(VedicEvidence(
            description=f"從屬星: {fav_count} 顆指向主隊有利宮位 vs "
                        f"{und_count} 顆指向客隊",
            favors="home", tier=2, points=pts,
            category="dispositors"))
    elif und_count > fav_count and (und_count - fav_count) >= 3:
        pts = min((und_count - fav_count) * 2, 9)
        evidences.append(VedicEvidence(
            description=f"從屬星: {und_count} 顆指向客隊有利宮位 vs "
                        f"{fav_count} 顆指向主隊",
            favors="away", tier=2, points=pts,
            category="dispositors"))

    return evidences


# ============================================================
# 技術 7: 節點 (Rahu/Ketu) 影響
# ============================================================

def evaluate_nodes_vedic(chart: VedicChartData) -> list:
    """分析 Rahu 和 Ketu 的位置

    Rahu 在有利宮位 → 增強該隊
    Ketu 通常帶來不確定性
    """
    evidences = []

    rahu = get_planet_by_name(chart.planets, "Rahu")
    ketu = get_planet_by_name(chart.planets, "Ketu")

    if rahu:
        if rahu.house in VICTORY_HOUSES_FAVORITE:
            evidences.append(VedicEvidence(
                description=f"Rahu 落入第{rahu.house}宮 (主隊有利宮位) — "
                            f"增加主隊不確定性中的機遇",
                favors="home", tier=1, points=2,
                category="nodes_vedic"))
        elif rahu.house in VICTORY_HOUSES_UNDERDOG:
            evidences.append(VedicEvidence(
                description=f"Rahu 落入第{rahu.house}宮 (客隊有利宮位) — "
                            f"增加客隊不確定性中的機遇",
                favors="away", tier=1, points=2,
                category="nodes_vedic"))

    if ketu:
        if ketu.house in {1, 7}:
            team = "主隊" if ketu.house == 1 else "客隊"
            evidences.append(VedicEvidence(
                description=f"Ketu 落入第{ketu.house}宮 — "
                            f"{team}可能有意外狀況",
                favors="away" if ketu.house == 1 else "home",
                tier=1, points=2, category="nodes_vedic"))

    return evidences


# ============================================================
# 技術 8: SKY / PKY (Shubha/Papa Kartari Yoga) — Tier 2
# ============================================================

def evaluate_kartari_yoga(chart: VedicChartData) -> list:
    """分析 Shubha Kartari Yoga (SKY) 和 Papa Kartari Yoga (PKY)

    Gambler's Dharma:
    - SKY: 吉星夾持某宮 (落在該宮的第2宮和第12宮) → 保護該隊
    - PKY: 凶星夾持某宮 → 受外在不利因素影響
    - 只檢查第1宮和第7宮
    - 太陽在此情境中視為凶星
    """
    evidences = []

    for house_num, team_label, favors_team in [
        (1, "主隊 (第1宮)", "home"),
        (7, "客隊 (第7宮)", "away"),
    ]:
        # Houses flanking: 12th from house and 2nd from house
        house_12th = ((house_num - 2) % 12) + 1  # house before
        house_2nd = (house_num % 12) + 1          # house after

        planets_12th = set()
        planets_2nd = set()
        for p in chart.planets:
            if p.name in ("Rahu", "Ketu"):
                continue
            if p.house == house_12th:
                planets_12th.add(p.name)
            elif p.house == house_2nd:
                planets_2nd.add(p.name)

        if not planets_12th or not planets_2nd:
            continue

        benefics_12 = planets_12th & VEDIC_BENEFICS
        benefics_2 = planets_2nd & VEDIC_BENEFICS
        malefics_12 = planets_12th & VEDIC_MALEFICS
        malefics_2 = planets_2nd & VEDIC_MALEFICS

        if benefics_12 and benefics_2:
            evidences.append(VedicEvidence(
                description=f"SKY (吉星夾持): 吉星在第{house_12th}宮"
                            f"和第{house_2nd}宮夾持{team_label} — "
                            f"{'主' if favors_team == 'home' else '客'}隊受保護",
                favors=favors_team, tier=2, points=7,
                category="kartari_yoga"))

        if malefics_12 and malefics_2:
            opposite = "away" if favors_team == "home" else "home"
            evidences.append(VedicEvidence(
                description=f"PKY (凶星夾持): 凶星在第{house_12th}宮"
                            f"和第{house_2nd}宮夾持{team_label} — "
                            f"{'主' if favors_team == 'home' else '客'}隊受壓",
                favors=opposite, tier=2, points=7,
                category="kartari_yoga"))

    return evidences


# ============================================================
# 技術 9: Graha Yuddha (行星戰爭) — Tier 2
# ============================================================

def evaluate_graha_yuddha(chart: VedicChartData) -> list:
    """分析行星戰爭 (Planetary War)

    Gambler's Dharma:
    - 兩顆行星在實際黃經上距離 ≤1° → 構成行星戰爭
    - 通常會削弱雙方行星及其所主宰的宮位
    - 亮度較高者 (離地球較近/逆行者) 獲勝
    - 僅考慮 1宮/10宮主 (主隊) vs 7宮/4宮主 (客隊) 的戰爭
    - 金星幾乎總是贏得行星戰爭 (天空第三亮)
    """
    evidences = []
    GRAHA_YUDDHA_ORB = 1.0  # degrees

    lord_1_name = chart.houses[0].lord
    lord_10_name = chart.houses[9].lord
    lord_7_name = chart.houses[6].lord
    lord_4_name = chart.houses[3].lord

    home_lords = {lord_1_name, lord_10_name}
    away_lords = {lord_7_name, lord_4_name}

    # Brightness ranking (brighter = more likely to win war; lower = brighter)
    # Venus > Jupiter > Mars > Saturn > Mercury
    # Sun and Moon are excluded from planetary war (skipped below)
    brightness_rank = {
        "Venus": 1, "Jupiter": 2, "Mars": 3,
        "Saturn": 4, "Mercury": 5,
    }

    checked = set()
    for h_lord_name in home_lords:
        for a_lord_name in away_lords:
            pair = tuple(sorted([h_lord_name, a_lord_name]))
            if pair in checked or h_lord_name == a_lord_name:
                continue
            checked.add(pair)

            h_planet = get_planet_by_name(chart.planets, h_lord_name)
            a_planet = get_planet_by_name(chart.planets, a_lord_name)
            if not h_planet or not a_planet:
                continue

            # Skip Sun and Moon — they don't participate in planetary war
            if h_planet.name in ("Sun", "Moon", "Rahu", "Ketu"):
                continue
            if a_planet.name in ("Sun", "Moon", "Rahu", "Ketu"):
                continue

            dist = _angle_diff(h_planet.longitude, a_planet.longitude)
            if dist > GRAHA_YUDDHA_ORB:
                continue

            # Determine winner by brightness
            h_bright = brightness_rank.get(h_planet.name, 99)
            a_bright = brightness_rank.get(a_planet.name, 99)

            # Retrograde planets are brighter (closer to Earth)
            if h_planet.retrograde:
                h_bright -= 1
            if a_planet.retrograde:
                a_bright -= 1

            if h_bright < a_bright:
                # Home lord wins war
                evidences.append(VedicEvidence(
                    description=f"行星戰爭: {h_planet.name} (主隊方) vs "
                                f"{a_planet.name} (客隊方), 距離 {dist:.2f}° — "
                                f"{h_planet.name} 較亮, 主隊方勝出 (但雙方皆受削弱)",
                    favors="home", tier=2, points=5,
                    category="graha_yuddha"))
            elif a_bright < h_bright:
                # Away lord wins war
                evidences.append(VedicEvidence(
                    description=f"行星戰爭: {a_planet.name} (客隊方) vs "
                                f"{h_planet.name} (主隊方), 距離 {dist:.2f}° — "
                                f"{a_planet.name} 較亮, 客隊方勝出 (但雙方皆受削弱)",
                    favors="away", tier=2, points=5,
                    category="graha_yuddha"))
            else:
                # Tie — both weakened equally
                evidences.append(VedicEvidence(
                    description=f"行星戰爭: {h_planet.name} vs {a_planet.name}, "
                                f"距離 {dist:.2f}° — 雙方均受削弱",
                    favors="neutral", tier=2, points=0,
                    category="graha_yuddha"))

    return evidences


# ============================================================
# 技術 10: Parivartana Yoga (互換接納) — Tier 2
# ============================================================

def evaluate_parivartana_yoga(chart: VedicChartData) -> list:
    """分析 Parivartana Yoga (PY, 互換接納 / Mutual Reception)

    Gambler's Dharma:
    - 兩顆行星互換星座 (A在B主宰的星座, B在A主宰的星座) → Parivartana
    - 特別是在勝利宮位之間的互換，可為該隊增添力量
    """
    evidences = []

    # Check for Parivartana Yoga among all planet pairs
    planets = [p for p in chart.planets if p.name not in ("Rahu", "Ketu")]

    for i, p1 in enumerate(planets):
        for p2 in planets[i + 1:]:
            # p1 is in the sign ruled by p2, and p2 is in the sign ruled by p1
            if p1.rashi_lord == p2.name and p2.rashi_lord == p1.name:
                # We have a Parivartana Yoga
                # Determine if it benefits home or away based on house positions
                h1_in_fav = p1.house in VICTORY_HOUSES_FAVORITE
                h2_in_fav = p2.house in VICTORY_HOUSES_FAVORITE
                h1_in_und = p1.house in VICTORY_HOUSES_UNDERDOG
                h2_in_und = p2.house in VICTORY_HOUSES_UNDERDOG

                if (h1_in_fav and h2_in_fav):
                    evidences.append(VedicEvidence(
                        description=f"Parivartana Yoga: {p1.name} (第{p1.house}宮) ↔ "
                                    f"{p2.name} (第{p2.house}宮) 互換 — "
                                    f"兩者皆在主隊勝利宮位, 主隊力量增強",
                        favors="home", tier=2, points=7,
                        category="parivartana_yoga"))
                elif (h1_in_und and h2_in_und):
                    evidences.append(VedicEvidence(
                        description=f"Parivartana Yoga: {p1.name} (第{p1.house}宮) ↔ "
                                    f"{p2.name} (第{p2.house}宮) 互換 — "
                                    f"兩者皆在客隊勝利宮位, 客隊力量增強",
                        favors="away", tier=2, points=7,
                        category="parivartana_yoga"))
                elif (h1_in_fav or h2_in_fav) and (h1_in_und or h2_in_und):
                    evidences.append(VedicEvidence(
                        description=f"Parivartana Yoga: {p1.name} (第{p1.house}宮) ↔ "
                                    f"{p2.name} (第{p2.house}宮) 互換 — "
                                    f"跨越雙方宮位, 中性影響",
                        favors="neutral", tier=2, points=0,
                        category="parivartana_yoga"))

    return evidences

def vedic_judgment(chart: VedicChartData,
                   home_team: str, away_team: str) -> dict:
    """執行完整的 Vedic 判斷流程

    融合三個層面：
    - 身體層 (Physical): 勝利宮位, 宮主強度
    - 心智層 (Mental): Navamsa D9 分析
    - 靈性層 (Spiritual): Navamsa 宮主, 從屬星

    Returns: dict with 'evidences', 'home_points', 'away_points', 'summary'
    """
    all_evidences = []
    home_points = 0.0
    away_points = 0.0

    # Tier 1: Victory Houses (Physical strength)
    all_evidences.extend(evaluate_victory_houses(chart))

    # Tier 2: Cuspal Strength (Energy/Prana)
    all_evidences.extend(evaluate_cuspal_strength(chart))

    # Tier 2: Lord Strength
    all_evidences.extend(evaluate_lord_strength(chart))

    # Tier 2: Dispositors
    all_evidences.extend(evaluate_dispositors(chart))

    # Tier 3: Navamsa Cuspal (Mental/Spiritual — strongest)
    all_evidences.extend(evaluate_navamsa_cuspal(chart))

    # Tier 3: Navamsa Lords
    all_evidences.extend(evaluate_navamsa_lords(chart))

    # Tier 1: Nodes
    all_evidences.extend(evaluate_nodes_vedic(chart))

    # Tier 2: SKY/PKY (Kartari Yoga)
    all_evidences.extend(evaluate_kartari_yoga(chart))

    # Tier 2: Graha Yuddha (Planetary War)
    all_evidences.extend(evaluate_graha_yuddha(chart))

    # Tier 2: Parivartana Yoga (Mutual Reception)
    all_evidences.extend(evaluate_parivartana_yoga(chart))

    # Calculate scores
    for ev in all_evidences:
        if ev.favors == "home":
            home_points += ev.points
        elif ev.favors == "away":
            away_points += ev.points

    total = home_points + away_points
    if total == 0:
        total = 1

    home_pct = home_points / total * 100
    away_pct = away_points / total * 100

    # Determine which tier dominates
    tier3_home = sum(e.points for e in all_evidences
                     if e.tier == 3 and e.favors == "home")
    tier3_away = sum(e.points for e in all_evidences
                     if e.tier == 3 and e.favors == "away")

    if tier3_home > tier3_away and tier3_home > 0:
        summary = (f"Vedic 判斷: {home_team} 在靈性/心智層面佔優 "
                   f"(Tier 3: {tier3_home:.0f} vs {tier3_away:.0f})")
    elif tier3_away > tier3_home and tier3_away > 0:
        summary = (f"Vedic 判斷: {away_team} 在靈性/心智層面佔優 "
                   f"(Tier 3: {tier3_away:.0f} vs {tier3_home:.0f})")
    elif home_points > away_points:
        summary = (f"Vedic 判斷: {home_team} 總分領先 "
                   f"({home_points:.0f} vs {away_points:.0f})")
    elif away_points > home_points:
        summary = (f"Vedic 判斷: {away_team} 總分領先 "
                   f"({away_points:.0f} vs {home_points:.0f})")
    else:
        summary = f"Vedic 判斷: 雙方均等 ({home_points:.0f} vs {away_points:.0f})"

    return {
        "evidences": all_evidences,
        "home_points": home_points,
        "away_points": away_points,
        "summary": summary,
    }
