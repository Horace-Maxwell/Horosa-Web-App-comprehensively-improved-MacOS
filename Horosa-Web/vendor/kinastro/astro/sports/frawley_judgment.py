"""
Frawley 判斷引擎 (Frawley Judgment Engine)

實作 John Frawley《Sports Astrology》的核心規則：

規則摘要 (依 Frawley 工作表順序)：
1. 選擇適當宮位：主隊=1宮，客隊=7宮 (或 Favorite=1st)
2. 檢查宮位狀態：宮內行星吉凶影響
3. 找出宮位主星 (Lords)：Lord 1 代表主隊，Lord 7 代表客隊
4. 檢查燃燒 (Combustion)：距太陽 8.5° 內且同星座 → 極度削弱
5. 日光之下 (Under the Sunbeams)：距太陽 17.5° 內 → 輕微削弱
6. 宮位配置 (House Placement)：角宮=強，續宮=中，果宮=弱
7. 月交點 (Lunar Nodes)：合北交=增強，合南交=削弱
8. 相位 (Aspects)：來自尊貴行星=吉，來自衰弱行星=凶
9. 接納 (Reception)：影響相位的效果
10. 本質尊貴 (Essential Dignity)：作為決勝依據
11. 月亮宮位 (Moon house position)：月亮落入1/10宮有利主隊，7/4宮有利客隊
12. 月亮最終相位 (Moon applying aspects)：月亮最後形成的相位決定勝負
13. 福運對點 (Antiscion of Fortuna)：靠近1宮/7宮宮頭為極強證據
14. 福運點相位 (Lot of Fortune aspects)：月亮/主星與福運點的相位
15. 恆星 (Fixed Stars)：Regulus (增強)、Spica (保護)、Algol (削弱)
16. 土星凶性 (Saturn malefic)：土星非1/7宮主時觸及任何事物皆損害
17. 月亮光量 (Moon phase)：越接近滿月光越強，越接近新月光越弱
"""

from .models import FrawleyEvidence, TeamAssignment, PlanetInfo, HouseInfo
from .chart_calculator import (
    WesternChartData, _normalize, _sign_index, _angle_diff,
    TRADITIONAL_RULERS, ZODIAC_SIGNS,
    DOMICILE, EXALTATION, DETRIMENT, FALL,
    SPEED_FAST, SPEED_SLOW,
    get_planet_by_name,
)

# Combustion orb constants
CAZIMI_ORB = 17.0 / 60.0  # 0°17' — within Sun's heart
COMBUSTION_ORB = 8.5       # degrees, same sign required
SUNBEAMS_ORB = 17.5        # degrees, any sign

# Fixed stars (tropical longitudes, calculated for J2000 epoch).
# Due to precession (~50"/year), these shift ~1° every 72 years.
# At orb 1° these values remain valid through ~2070.
# Frawley: only 3 stars matter; orb ~1°
FIXED_STARS = {
    "Regulus": {"longitude": 150.0, "effect": "boost",
                "description": "軒轅十四 — 大幅增強"},       # Leo ~29°50'
    "Spica":   {"longitude": 203.8, "effect": "protect",
                "description": "角宿一 — 提供保護"},         # Libra ~23°50'
    "Algol":   {"longitude": 56.2, "effect": "weaken",
                "description": "大陵五 — 中等負面影響"},     # Taurus ~26°10'
}
FIXED_STAR_ORB = 1.0  # degrees

# Moon applying aspect orb for football (Frawley: ~5° for 80+ min games)
MOON_APPLYING_ORB = 5.0

# Antiscion: mirror across the solstice axis (Cancer 0° / Capricorn 0°)
# antiscion(L) = (180 - L) mod 360
# e.g. Aries 10° → Virgo 20°; Leo 29° → Taurus 1°


# ============================================================
# 宮位分配
# ============================================================

def assign_teams(
    chart: WesternChartData,
    home_team: str,
    away_team: str,
    favorite: str = None,
) -> tuple:
    """分配球隊宮位

    Frawley 規則：
    - 若有明確偏好的隊伍 (favorite)，favorite=1宮，underdog=7宮
    - 若無偏好，主隊=1宮，客隊=7宮
    - 支援宮位：1宮隊伍的支援宮=10宮，7宮隊伍的支援宮=4宮

    Returns: (home_assignment, away_assignment)
    """
    h1_lord = chart.houses[0].lord  # Lord of 1st house
    h7_lord = chart.houses[6].lord  # Lord of 7th house

    if favorite == "home":
        home_primary, home_support = 1, 10
        away_primary, away_support = 7, 4
    elif favorite == "away":
        home_primary, home_support = 7, 4
        away_primary, away_support = 1, 10
    else:
        # Default: home=1st, away=7th
        home_primary, home_support = 1, 10
        away_primary, away_support = 7, 4

    home_lord = chart.houses[home_primary - 1].lord
    away_lord = chart.houses[away_primary - 1].lord

    home_lord_info = get_planet_by_name(chart.planets, home_lord)
    away_lord_info = get_planet_by_name(chart.planets, away_lord)

    home_assign = TeamAssignment(
        team_name=home_team,
        primary_house=home_primary,
        supporting_house=home_support,
        lord_planet=home_lord,
        lord_info=home_lord_info,
    )
    away_assign = TeamAssignment(
        team_name=away_team,
        primary_house=away_primary,
        supporting_house=away_support,
        lord_planet=away_lord,
        lord_info=away_lord_info,
    )
    return home_assign, away_assign


# ============================================================
# 核心判斷函數
# ============================================================

def check_combustion(planet: PlanetInfo, sun: PlanetInfo) -> dict:
    """檢查燃燒狀態 (Combustion)

    Frawley 規則：
    - 距太陽 8.5° 內且同星座 → 燃燒 (combust)
    - 距太陽 0°17' 內 → Cazimi (極度增強)
    - 若行星在自己的 domicile/exaltation 中燃燒 → 不受影響

    Returns: dict with 'status', 'distance', 'severity'
    """
    if planet.name == "Sun":
        return {"status": "none", "distance": 0, "severity": 0}

    dist = _angle_diff(planet.longitude, sun.longitude)
    same_sign = (planet.sign_index == sun.sign_index)

    # Cazimi: within 0°17'
    if dist <= CAZIMI_ORB:
        return {"status": "cazimi", "distance": dist, "severity": 0}

    # Combustion: within 8.5° AND same sign
    if dist <= COMBUSTION_ORB and same_sign:
        # Check if planet is in own domicile or exaltation → immune
        if planet.essential_dignity in ("domicile", "exaltation"):
            return {"status": "combust_immune", "distance": dist, "severity": 0}
        severity = (COMBUSTION_ORB - dist) / COMBUSTION_ORB  # closer = worse
        return {"status": "combust", "distance": dist, "severity": severity}

    # Under the Sunbeams: within 17.5° (any sign)
    if dist <= SUNBEAMS_ORB:
        severity = (SUNBEAMS_ORB - dist) / SUNBEAMS_ORB * 0.3  # mild effect
        return {"status": "under_sunbeams", "distance": dist, "severity": severity}

    return {"status": "none", "distance": dist, "severity": 0}


def evaluate_house_placement(planet: PlanetInfo, own_house: int,
                             enemy_house: int) -> dict:
    """評估宮位配置 (House Placement)

    Frawley 規則 (最重要的證據):
    - 角宮 (1,4,7,10): 強 — 但若在敵方角宮則極弱
    - 續宮 (2,3,5,9,11): 中性
    - 果宮 (6,8,12): 弱
    """
    h = planet.house
    angular = {1, 4, 7, 10}
    succedent = {2, 3, 5, 9, 11}
    cadent = {6, 8, 12}

    # Own angular houses (excluding enemy's angular house)
    friendly_angular = angular - {enemy_house}

    if h == enemy_house:
        return {"strength": "imprisoned", "score": -3.0,
                "description": f"落入敵方第{enemy_house}宮 — 如囚犯般極度削弱"}

    if h in friendly_angular:
        return {"strength": "strong", "score": 2.0,
                "description": f"落入友方角宮第{h}宮 — 力量強大"}

    if h == own_house:
        return {"strength": "very_strong", "score": 2.5,
                "description": f"落入自己的第{h}宮 — 力量極強"}

    if h in succedent:
        return {"strength": "neutral", "score": 0.0,
                "description": f"落入續宮第{h}宮 — 中性"}

    if h in cadent:
        return {"strength": "weak", "score": -1.0,
                "description": f"落入果宮第{h}宮 — 力量削弱"}

    return {"strength": "neutral", "score": 0.0,
            "description": f"落入第{h}宮 — 中性"}


def check_node_conjunction(planet: PlanetInfo,
                           north_node_lon: float,
                           south_node_lon: float) -> dict:
    """檢查月交點合相

    Frawley: 合北交 ≤5° → 大幅增強; 合南交 ≤5° → 大幅削弱
    """
    dist_nn = _angle_diff(planet.longitude, north_node_lon)
    dist_sn = _angle_diff(planet.longitude, south_node_lon)

    if dist_nn <= 5.0:
        strength = (5.0 - dist_nn) / 5.0
        return {"node": "north", "distance": dist_nn,
                "effect": "boost", "strength": strength}
    if dist_sn <= 5.0:
        strength = (5.0 - dist_sn) / 5.0
        return {"node": "south", "distance": dist_sn,
                "effect": "weaken", "strength": strength}
    return {"node": "none", "distance": 999, "effect": "none", "strength": 0}


def evaluate_aspects_to_planet(target: PlanetInfo, all_planets: list) -> list:
    """評估其他行星對目標行星的相位

    Frawley 規則：
    - 行星的本質尊貴決定相位吉凶（非相位類型）
    - 對沖永遠是災難
    - 容許度: 一般 ≤5°, 太陽對沖 ≤8°
    - 相位必須在正確星座內
    """
    PTOLEMAIC_ASPECTS = [
        (0, "conjunction", 5),
        (60, "sextile", 4),
        (90, "square", 5),
        (120, "trine", 5),
        (180, "opposition", 8),
    ]

    aspects = []
    for p in all_planets:
        if p.name == target.name or p.name == "Sun":
            continue  # Sun handled by combustion

        diff = _angle_diff(target.longitude, p.longitude)
        for angle, asp_name, orb in PTOLEMAIC_ASPECTS:
            if abs(diff - angle) <= orb:
                # Verify sign-based aspect (Frawley insists on sign boundaries)
                sign_diff = abs(target.sign_index - p.sign_index) % 12
                expected_signs = {
                    0: {0}, 60: {2, 10}, 90: {3, 9},
                    120: {4, 8}, 180: {6},
                }
                if sign_diff not in expected_signs.get(angle, set()):
                    continue

                # Determine if aspecting planet is benefic or malefic
                if p.essential_dignity in ("domicile", "exaltation"):
                    is_benefic = True
                elif p.essential_dignity in ("detriment", "fall"):
                    is_benefic = False
                else:
                    is_benefic = None  # peregrine: mild

                # Opposition is always bad
                if asp_name == "opposition":
                    is_benefic = False

                closeness = 1.0 - abs(diff - angle) / orb

                aspects.append({
                    "planet": p.name,
                    "aspect": asp_name,
                    "angle_diff": diff,
                    "orb": abs(diff - angle),
                    "is_benefic": is_benefic,
                    "closeness": closeness,
                    "dignity": p.essential_dignity,
                })
    return aspects


def evaluate_reception(planet: PlanetInfo, other: PlanetInfo) -> dict:
    """評估接納關係 (Reception)

    Frawley: 若 planet 落在 other 主宰的星座 → other 接納 planet
    互容 (mutual reception) = 兩者互相落入對方主宰的星座
    """
    planet_ruler = TRADITIONAL_RULERS.get(planet.sign_index)
    other_ruler = TRADITIONAL_RULERS.get(other.sign_index)

    planet_received = (planet_ruler == other.name)
    other_received = (other_ruler == planet.name)

    if planet_received and other_received:
        return {"type": "mutual_reception", "description": "互容 — 雙方力量增強"}
    if planet_received:
        return {"type": "received", "description": f"{planet.name} 被 {other.name} 接納"}
    if other_received:
        return {"type": "receives", "description": f"{other.name} 被 {planet.name} 接納"}
    return {"type": "none", "description": "無接納關係"}


def evaluate_speed(planet: PlanetInfo) -> dict:
    """評估行星速度 (Frawley's speed table)"""
    fast_thresh = SPEED_FAST.get(planet.name, 999)
    slow_thresh = SPEED_SLOW.get(planet.name, 0)
    speed = abs(planet.speed)

    if speed >= fast_thresh:
        return {"status": "fast", "score": 0.5,
                "description": f"{planet.name} 速度極快 ({speed:.3f}°/日)"}
    if speed <= slow_thresh:
        return {"status": "slow", "score": -0.5,
                "description": f"{planet.name} 速度極慢 ({speed:.3f}°/日) — 近停駐"}
    if speed <= 0.01:
        return {"status": "stationary", "score": -1.0,
                "description": f"{planet.name} 幾乎靜止 — 力量極弱"}
    return {"status": "normal", "score": 0.0,
            "description": f"{planet.name} 速度正常 ({speed:.3f}°/日)"}


def check_planets_in_houses(chart: WesternChartData,
                            home_house: int, away_house: int) -> list:
    """檢查宮位內行星對宮位的影響

    Frawley: 尊貴行星在宮內 → 有利; 衰弱行星 → 不利
    距宮頭越近影響越大; 不同星座則效力大減
    """
    evidences = []
    for p in chart.planets:
        if p.house == home_house:
            if p.essential_dignity in ("domicile", "exaltation"):
                evidences.append(FrawleyEvidence(
                    description=f"{p.name} (尊貴/{p.essential_dignity}) 落入主隊第{home_house}宮 — 有利主隊",
                    favors="home", weight=1.0, category="house_planet"))
            elif p.essential_dignity in ("detriment", "fall"):
                evidences.append(FrawleyEvidence(
                    description=f"{p.name} (衰弱/{p.essential_dignity}) 落入主隊第{home_house}宮 — 不利主隊",
                    favors="away", weight=1.0, category="house_planet"))
        elif p.house == away_house:
            if p.essential_dignity in ("domicile", "exaltation"):
                evidences.append(FrawleyEvidence(
                    description=f"{p.name} (尊貴/{p.essential_dignity}) 落入客隊第{away_house}宮 — 有利客隊",
                    favors="away", weight=1.0, category="house_planet"))
            elif p.essential_dignity in ("detriment", "fall"):
                evidences.append(FrawleyEvidence(
                    description=f"{p.name} (衰弱/{p.essential_dignity}) 落入客隊第{away_house}宮 — 不利客隊",
                    favors="home", weight=1.0, category="house_planet"))
    return evidences


# ============================================================
# 月亮宮位 (Moon House Position) — Frawley
# ============================================================

def evaluate_moon_position(chart: WesternChartData,
                           home_house: int, away_house: int,
                           home_support: int, away_support: int) -> list:
    """月亮落入的宮位暗示比賽流向

    Frawley:
    - 月亮靠近或進入第1宮或第10宮 → 勝利歸於主隊
    - 月亮靠近或進入第7宮或第4宮 → 勝利歸於客隊
    - 月亮本身不代表任何一方，但顯示事件流動趨勢
    """
    evidences = []
    moon = get_planet_by_name(chart.planets, "Moon")
    if not moon:
        return evidences

    if moon.house in (home_house, home_support):
        evidences.append(FrawleyEvidence(
            description=f"月亮落入第{moon.house}宮 (主隊方) — 比賽流向有利主隊",
            favors="home", weight=1.5, category="moon_position"))
    elif moon.house in (away_house, away_support):
        evidences.append(FrawleyEvidence(
            description=f"月亮落入第{moon.house}宮 (客隊方) — 比賽流向有利客隊",
            favors="away", weight=1.5, category="moon_position"))

    return evidences


# ============================================================
# 月亮最終相位 (Moon Applying Aspects) — Frawley
# ============================================================

def evaluate_moon_applying_aspects(chart: WesternChartData,
                                   home_lord: PlanetInfo,
                                   away_lord: PlanetInfo) -> list:
    """月亮最後形成的應用相位決定勝負

    Frawley:
    - 只看「尚未發生的相位」(applying)
    - 月亮最後的相位獲勝
    - 足球: 月亮移動上限 ~5° (80+ 分鐘比賽)
    - 星座終點即相位極限 — 不考慮跨星座相位
    - 身體相位 (bodily aspect) 通常是最終相位
    """
    evidences = []
    moon = get_planet_by_name(chart.planets, "Moon")
    if not moon:
        return evidences

    # Remaining degrees in current sign for the Moon
    remaining_in_sign = 30.0 - moon.sign_degree
    max_orb = min(MOON_APPLYING_ORB, remaining_in_sign)

    if max_orb <= 0:
        return evidences

    # Ptolemaic aspects Moon can form
    ASPECT_ANGLES = [0, 60, 90, 120, 180]

    # Find all applying aspects within orb
    applying = []
    for target in [home_lord, away_lord]:
        for angle in ASPECT_ANGLES:
            # Check forward aspect (Moon is applying)
            target_point = _normalize(target.longitude + angle)
            diff = _normalize(target_point - moon.longitude)
            if 0 < diff <= max_orb:
                # Verify sign-based aspect
                moon_sign = moon.sign_index
                target_sign = target.sign_index
                sign_diff = (target_sign - moon_sign) % 12
                expected = {0: {0}, 60: {2, 10}, 90: {3, 9},
                            120: {4, 8}, 180: {6}}
                if sign_diff in expected.get(angle, set()):
                    applying.append({
                        "target": target.name,
                        "aspect_angle": angle,
                        "distance": diff,
                        "is_home_lord": target.name == home_lord.name,
                    })

            # Also check the reverse direction
            target_point2 = _normalize(target.longitude - angle)
            diff2 = _normalize(target_point2 - moon.longitude)
            if angle != 0 and 0 < diff2 <= max_orb:
                moon_sign = moon.sign_index
                target_sign = target.sign_index
                sign_diff = (moon_sign - target_sign) % 12
                expected = {60: {2, 10}, 90: {3, 9},
                            120: {4, 8}, 180: {6}}
                if sign_diff in expected.get(angle, set()):
                    applying.append({
                        "target": target.name,
                        "aspect_angle": angle,
                        "distance": diff2,
                        "is_home_lord": target.name == home_lord.name,
                    })

    if not applying:
        return evidences

    # The final (farthest) aspect wins — Frawley's rule
    applying.sort(key=lambda x: x["distance"])
    final = applying[-1]

    asp_names = {0: "合相", 60: "六分相", 90: "四分相",
                 120: "三分相", 180: "對沖"}
    asp_name = asp_names.get(final["aspect_angle"], "相位")

    if final["is_home_lord"]:
        evidences.append(FrawleyEvidence(
            description=f"月亮最終相位: 對 {final['target']} (主隊主星) "
                        f"形成{asp_name} (距 {final['distance']:.1f}°) — 主隊獲勝信號",
            favors="home", weight=2.0, category="moon_final_aspect"))
    else:
        evidences.append(FrawleyEvidence(
            description=f"月亮最終相位: 對 {final['target']} (客隊主星) "
                        f"形成{asp_name} (距 {final['distance']:.1f}°) — 客隊獲勝信號",
            favors="away", weight=2.0, category="moon_final_aspect"))

    return evidences


# ============================================================
# 福運對點 (Antiscion of Fortuna) — Frawley
# ============================================================

def _antiscion(lon: float) -> float:
    """計算某黃經度的 Antiscion (以巨蟹-摩羯軸即夏至/冬至軸為鏡像)

    antiscion(L) = (180 - L) mod 360
    例: 白羊 10° → 處女 20°; 獅子 29° → 金牛 1°
    """
    return _normalize(180.0 - lon)


def evaluate_antiscion_fortuna(chart: WesternChartData,
                               home_house: int, away_house: int) -> list:
    """福運對點靠近宮頭為極強證據

    Frawley:
    - 福運對點靠近第1宮宮頭 → 主隊勝
    - 福運對點靠近第7宮宮頭 → 客隊勝
    - 「如果福運對點位於重要位置，它便是最強大的單一證據之一」
    - 容許度約 5°
    """
    evidences = []
    anti_fort = _antiscion(chart.lot_of_fortune)

    cusp_home = chart.houses[home_house - 1].cusp
    cusp_away = chart.houses[away_house - 1].cusp

    dist_home = _angle_diff(anti_fort, cusp_home)
    dist_away = _angle_diff(anti_fort, cusp_away)

    if dist_home <= 5.0:
        weight = 3.0 * (1.0 - dist_home / 5.0)
        evidences.append(FrawleyEvidence(
            description=f"福運對點 (Antiscion of Fortuna) 距第{home_house}宮宮頭 "
                        f"{dist_home:.1f}° — 極強有利主隊信號",
            favors="home", weight=weight, category="antiscion_fortuna"))

    if dist_away <= 5.0:
        weight = 3.0 * (1.0 - dist_away / 5.0)
        evidences.append(FrawleyEvidence(
            description=f"福運對點 (Antiscion of Fortuna) 距第{away_house}宮宮頭 "
                        f"{dist_away:.1f}° — 極強有利客隊信號",
            favors="away", weight=weight, category="antiscion_fortuna"))

    return evidences


# ============================================================
# 福運點相位 (Lot of Fortune Aspects) — Frawley
# ============================================================

def evaluate_fortuna_aspects(chart: WesternChartData,
                             home_lord: PlanetInfo,
                             away_lord: PlanetInfo) -> list:
    """福運點與月亮、主星的相位

    Frawley:
    - 月亮與福運點合/三合/六分 → 有利主隊 (favored)
    - 月亮與福運點四分/對沖 → 有利客隊 (underdog)
    - Lord 1 合福運點 → 有利主隊
    - Lord 7 合福運點 → 有利客隊
    - Lord 1 對沖福運點 → 有利客隊
    - Lord 7 對沖福運點 → 有利主隊
    - 福運點主宰星合福運點 → 有利主隊; 對沖 → 有利客隊
    """
    evidences = []
    fortuna = chart.lot_of_fortune
    anti_fort = _antiscion(fortuna)
    moon = get_planet_by_name(chart.planets, "Moon")

    # Moon aspects to Fortuna (including antiscion)
    if moon:
        for target_lon, target_label in [
            (fortuna, "福運點"), (anti_fort, "福運對點")
        ]:
            diff = _angle_diff(moon.longitude, target_lon)
            if diff <= 5.0:
                # Conjunction — favors home (favored)
                evidences.append(FrawleyEvidence(
                    description=f"月亮合{target_label} ({diff:.1f}°) — 有利主隊",
                    favors="home", weight=1.0, category="fortuna_aspect"))
            elif abs(diff - 60) <= 5.0 or abs(diff - 120) <= 5.0:
                evidences.append(FrawleyEvidence(
                    description=f"月亮與{target_label}呈和諧相位 ({diff:.1f}°) — 有利主隊",
                    favors="home", weight=0.8, category="fortuna_aspect"))
            elif abs(diff - 90) <= 5.0:
                evidences.append(FrawleyEvidence(
                    description=f"月亮與{target_label}呈四分相 ({diff:.1f}°) — 有利客隊",
                    favors="away", weight=0.8, category="fortuna_aspect"))
            elif abs(diff - 180) <= 5.0:
                evidences.append(FrawleyEvidence(
                    description=f"月亮與{target_label}呈對沖 ({diff:.1f}°) — 有利客隊",
                    favors="away", weight=1.0, category="fortuna_aspect"))

    # Lord aspects to Fortuna
    for lord, lord_label, is_home in [
        (home_lord, "主隊主星", True),
        (away_lord, "客隊主星", False),
    ]:
        diff = _angle_diff(lord.longitude, fortuna)
        if diff <= 5.0:
            # Lord conjunct Fortuna → favors that lord's team
            favors = "home" if is_home else "away"
            evidences.append(FrawleyEvidence(
                description=f"{lord.name} ({lord_label}) 合福運點 ({diff:.1f}°) "
                            f"— 有利{'主' if is_home else '客'}隊",
                favors=favors, weight=1.5, category="fortuna_aspect"))
        elif abs(diff - 180) <= 5.0:
            # Lord opposition Fortuna → favors opposite team
            favors = "away" if is_home else "home"
            evidences.append(FrawleyEvidence(
                description=f"{lord.name} ({lord_label}) 對沖福運點 ({diff:.1f}°) "
                            f"— 有利{'客' if is_home else '主'}隊",
                favors=favors, weight=1.5, category="fortuna_aspect"))

    # Fortuna ruler aspects to Fortuna
    fortuna_sign_idx = _sign_index(fortuna)
    fortuna_ruler_name = TRADITIONAL_RULERS.get(fortuna_sign_idx)
    if fortuna_ruler_name:
        # Skip if the ruler is also Lord 1 or Lord 7 or Moon
        skip = fortuna_ruler_name in (
            home_lord.name, away_lord.name, "Moon")
        if not skip:
            fort_ruler = get_planet_by_name(chart.planets, fortuna_ruler_name)
            if fort_ruler:
                diff = _angle_diff(fort_ruler.longitude, fortuna)
                if diff <= 5.0:
                    evidences.append(FrawleyEvidence(
                        description=f"福運點主宰星 {fort_ruler.name} 合福運點 "
                                    f"({diff:.1f}°) — 有利主隊",
                        favors="home", weight=1.0,
                        category="fortuna_aspect"))
                elif abs(diff - 180) <= 5.0:
                    evidences.append(FrawleyEvidence(
                        description=f"福運點主宰星 {fort_ruler.name} 對沖福運點 "
                                    f"({diff:.1f}°) — 有利客隊",
                        favors="away", weight=1.0,
                        category="fortuna_aspect"))

    return evidences


# ============================================================
# 恆星 (Fixed Stars) — Frawley
# ============================================================

def evaluate_fixed_stars(home_lord: PlanetInfo,
                         away_lord: PlanetInfo) -> list:
    """恆星對主星的影響

    Frawley:
    - Regulus (獅子座 ~29°): 大幅增強命主星
    - Spica (天秤座 ~23°): 提供保護
    - Algol (金牛座 ~26°): 中等負面
    - 容許度 ~1°
    """
    evidences = []
    for lord, team_label, is_home in [
        (home_lord, "主隊主星", True),
        (away_lord, "客隊主星", False),
    ]:
        for star_name, star_data in FIXED_STARS.items():
            dist = _angle_diff(lord.longitude, star_data["longitude"])
            if dist <= FIXED_STAR_ORB:
                effect = star_data["effect"]
                desc = star_data["description"]
                if effect == "boost":
                    favors = "home" if is_home else "away"
                    evidences.append(FrawleyEvidence(
                        description=f"{lord.name} ({team_label}) 合 {star_name} "
                                    f"({desc}, 距 {dist:.2f}°) — "
                                    f"{'主' if is_home else '客'}隊力量大增",
                        favors=favors, weight=2.0,
                        category="fixed_stars"))
                elif effect == "protect":
                    favors = "home" if is_home else "away"
                    evidences.append(FrawleyEvidence(
                        description=f"{lord.name} ({team_label}) 合 {star_name} "
                                    f"({desc}, 距 {dist:.2f}°) — "
                                    f"保護{'主' if is_home else '客'}隊",
                        favors=favors, weight=1.0,
                        category="fixed_stars"))
                elif effect == "weaken":
                    favors = "away" if is_home else "home"
                    evidences.append(FrawleyEvidence(
                        description=f"{lord.name} ({team_label}) 合 {star_name} "
                                    f"({desc}, 距 {dist:.2f}°) — "
                                    f"不利{'主' if is_home else '客'}隊",
                        favors=favors, weight=1.5,
                        category="fixed_stars"))
    return evidences


# ============================================================
# 土星凶性 (Saturn as General Malefic) — Frawley
# ============================================================

def evaluate_saturn_malefic(chart: WesternChartData,
                            home_lord: PlanetInfo,
                            away_lord: PlanetInfo,
                            home_house: int,
                            away_house: int) -> list:
    """土星非1/7宮主時的凶性影響

    Frawley:
    - 除非土星是第1宮主或第7宮主，否則它觸及之物皆受折磨
    - 此凶性優先於其他角色 (如第10宮主)
    - 合相容許度 ~5°
    """
    evidences = []
    saturn = get_planet_by_name(chart.planets, "Saturn")
    if not saturn:
        return evidences

    # If Saturn IS Lord 1 or Lord 7, skip this — it has a team role
    if saturn.name in (home_lord.name, away_lord.name):
        return evidences

    # Check if Saturn is conjunct either lord
    for lord, team_label, is_home in [
        (home_lord, "主隊主星", True),
        (away_lord, "客隊主星", False),
    ]:
        dist = _angle_diff(saturn.longitude, lord.longitude)
        if dist <= 5.0:
            favors = "away" if is_home else "home"
            evidences.append(FrawleyEvidence(
                description=f"土星 (非宮主, 通用凶星) 合 {lord.name} ({team_label}) "
                            f"(距 {dist:.1f}°) — 損害{'主' if is_home else '客'}隊",
                favors=favors, weight=1.5, category="saturn_malefic"))

    # Check if Saturn is on a relevant cusp
    for house_num, team_label, is_home in [
        (home_house, "主隊宮", True),
        (away_house, "客隊宮", False),
    ]:
        cusp = chart.houses[house_num - 1].cusp
        dist = _angle_diff(saturn.longitude, cusp)
        if dist <= 3.0:
            favors = "away" if is_home else "home"
            evidences.append(FrawleyEvidence(
                description=f"土星 (通用凶星) 落在第{house_num}宮 ({team_label}) "
                            f"宮頭 (距 {dist:.1f}°) — 損害{'主' if is_home else '客'}隊",
                favors=favors, weight=1.5, category="saturn_malefic"))

    return evidences


# ============================================================
# 月亮光量 (Moon Phase / Light) — Frawley
# ============================================================

def evaluate_moon_light(chart: WesternChartData) -> list:
    """月亮光量 (光的多寡)

    Frawley:
    - 月亮距太陽 >120° → 大量光線 (強)
    - 月亮距太陽 <60° → 光線較少 (弱)
    - 月亮距太陽 <30° → 非常弱
    - 月亮在燃燒之路 (天秤座15° ~ 天蠍座15°) → 嚴重受克
    - 作為一般性強弱指標影響整盤判斷
    """
    evidences = []
    moon = get_planet_by_name(chart.planets, "Moon")
    sun = get_planet_by_name(chart.planets, "Sun")
    if not moon or not sun:
        return evidences

    sep = _angle_diff(moon.longitude, sun.longitude)

    if sep > 120:
        evidences.append(FrawleyEvidence(
            description=f"月亮光量充足 (距太陽 {sep:.1f}°, >120°) — 盤面能量強",
            favors="neutral", weight=0.0, category="moon_light"))
    elif sep < 30:
        evidences.append(FrawleyEvidence(
            description=f"月亮光量極弱 (距太陽 {sep:.1f}°, <30°) — 盤面能量不足, "
                        f"比賽可能缺乏進球",
            favors="draw", weight=0.5, category="moon_light"))
    elif sep < 60:
        evidences.append(FrawleyEvidence(
            description=f"月亮光量偏弱 (距太陽 {sep:.1f}°, <60°) — 盤面能量中等偏弱",
            favors="neutral", weight=0.0, category="moon_light"))

    # Via Combusta / Burning Path: Libra 15° ~ Scorpio 15° (195° ~ 225°)
    moon_lon = _normalize(moon.longitude)
    if 195.0 <= moon_lon <= 225.0:
        evidences.append(FrawleyEvidence(
            description=f"月亮在燃燒之路 (天秤座15°~天蠍座15°) — 嚴重受克, "
                        f"增加比賽不確定性",
            favors="draw", weight=0.8, category="moon_light"))

    return evidences


def _lord_testimonies_summary(
    evidences: list[FrawleyEvidence],
    home_score: float,
    away_score: float,
) -> dict:
    """彙整 Lord 1 vs Lord 7 證據分布。"""
    categories: dict[str, dict[str, float]] = {}
    for ev in evidences:
        bucket = categories.setdefault(
            ev.category,
            {"home": 0.0, "away": 0.0, "draw": 0.0, "neutral": 0.0},
        )
        if ev.favors in bucket:
            bucket[ev.favors] += ev.weight
        else:
            bucket["neutral"] += ev.weight

    margin = home_score - away_score
    return {
        "leader": "home" if margin > 0 else "away" if margin < 0 else "draw",
        "home_score": round(home_score, 3),
        "away_score": round(away_score, 3),
        "margin": round(margin, 3),
        "categories": categories,
    }


def _injury_risk_indicator(
    home_lord: PlanetInfo,
    away_lord: PlanetInfo,
    home_house: int,
    away_house: int,
) -> dict[str, float]:
    """以 6/12 宮與落陷條件生成傷病風險。"""
    home_risk = 0.14
    away_risk = 0.14

    if home_lord.house in (6, 12):
        home_risk += 0.18
    if away_lord.house in (6, 12):
        away_risk += 0.18
    if home_lord.essential_dignity in ("fall", "detriment"):
        home_risk += 0.10
    if away_lord.essential_dignity in ("fall", "detriment"):
        away_risk += 0.10
    if home_house in (6, 12):
        home_risk += 0.07
    if away_house in (6, 12):
        away_risk += 0.07

    return {
        "home": round(min(home_risk, 0.95), 4),
        "away": round(min(away_risk, 0.95), 4),
    }


def _reversal_indicator(
    chart: WesternChartData,
    home_lord: PlanetInfo,
    away_lord: PlanetInfo,
) -> float:
    """以天王星/交點/恆星生成逆轉指標。"""
    uranus_dist = 90.0
    uranus = get_planet_by_name(chart.planets, "Uranus")
    if uranus:
        uranus_dist = min(
            _angle_diff(uranus.longitude, home_lord.longitude),
            _angle_diff(uranus.longitude, away_lord.longitude),
        )

    node_dist = min(
        _angle_diff(home_lord.longitude, chart.north_node_lon),
        _angle_diff(away_lord.longitude, chart.north_node_lon),
        _angle_diff(home_lord.longitude, chart.south_node_lon),
        _angle_diff(away_lord.longitude, chart.south_node_lon),
    )
    star_hits = len(evaluate_fixed_stars(home_lord, away_lord))

    uranus_score = max(0.0, 1.0 - min(uranus_dist, 90.0) / 90.0) * 0.35
    node_score = max(0.0, 1.0 - min(node_dist, 15.0) / 15.0) * 0.45
    star_score = min(star_hits, 2) / 2.0 * 0.20
    return round(min(0.99, uranus_score + node_score + star_score), 4)


# ============================================================
# 綜合 Frawley 判斷
# ============================================================

def frawley_judgment(chart: WesternChartData,
                     home_team: str, away_team: str,
                     favorite: str = None) -> dict:
    """執行完整的 Frawley 判斷流程

    Returns: dict with 'evidences', 'home_score', 'away_score', 'summary'
    """
    home_assign, away_assign = assign_teams(
        chart, home_team, away_team, favorite)

    evidences = []
    home_score = 0.0
    away_score = 0.0

    sun = get_planet_by_name(chart.planets, "Sun")
    home_lord = home_assign.lord_info
    away_lord = away_assign.lord_info

    if not home_lord or not away_lord:
        return {
            "evidences": [],
            "home_score": 0, "away_score": 0,
            "summary": "無法找到宮位主星",
            "home_assign": home_assign, "away_assign": away_assign,
        }

    # --- Step 1: Check planets in houses ---
    house_planet_ev = check_planets_in_houses(
        chart, home_assign.primary_house, away_assign.primary_house)
    evidences.extend(house_planet_ev)
    for ev in house_planet_ev:
        if ev.favors == "home":
            home_score += ev.weight
        elif ev.favors == "away":
            away_score += ev.weight

    # --- Step 2: Combustion ---
    for lord, team_name, is_home in [
        (home_lord, home_team, True),
        (away_lord, away_team, False),
    ]:
        comb = check_combustion(lord, sun)
        if comb["status"] == "combust":
            weight = 3.0 * comb["severity"]
            ev = FrawleyEvidence(
                description=f"{lord.name} (代表 {team_name}) 燃燒 — 距太陽 {comb['distance']:.1f}° — 極度不利",
                favors="away" if is_home else "home",
                weight=weight, category="combustion")
            evidences.append(ev)
            if is_home:
                away_score += weight
            else:
                home_score += weight
        elif comb["status"] == "cazimi":
            ev = FrawleyEvidence(
                description=f"{lord.name} (代表 {team_name}) 位於 Cazimi — 極度增強",
                favors="home" if is_home else "away",
                weight=2.0, category="combustion")
            evidences.append(ev)
            if is_home:
                home_score += 2.0
            else:
                away_score += 2.0
        elif comb["status"] == "under_sunbeams":
            weight = comb["severity"]
            ev = FrawleyEvidence(
                description=f"{lord.name} (代表 {team_name}) 在日光之下 — 輕微削弱",
                favors="away" if is_home else "home",
                weight=weight, category="combustion")
            evidences.append(ev)
            if is_home:
                away_score += weight
            else:
                home_score += weight

    # --- Step 3: House Placement (most important!) ---
    for lord, team_name, is_home, own_h, enemy_h in [
        (home_lord, home_team, True,
         home_assign.primary_house, away_assign.primary_house),
        (away_lord, away_team, False,
         away_assign.primary_house, home_assign.primary_house),
    ]:
        hp = evaluate_house_placement(lord, own_h, enemy_h)
        if hp["score"] != 0:
            favors = ("home" if is_home else "away") if hp["score"] > 0 \
                else ("away" if is_home else "home")
            weight = abs(hp["score"])
            ev = FrawleyEvidence(
                description=f"{lord.name} (代表 {team_name}): {hp['description']}",
                favors=favors, weight=weight, category="house_placement")
            evidences.append(ev)
            if favors == "home":
                home_score += weight
            else:
                away_score += weight

    # --- Step 4: Lunar Nodes ---
    for lord, team_name, is_home in [
        (home_lord, home_team, True),
        (away_lord, away_team, False),
    ]:
        node = check_node_conjunction(
            lord, chart.north_node_lon, chart.south_node_lon)
        if node["effect"] == "boost":
            weight = 2.0 * node["strength"]
            ev = FrawleyEvidence(
                description=f"{lord.name} (代表 {team_name}) 合北交點 — 距離 {node['distance']:.1f}° — 大幅增強",
                favors="home" if is_home else "away",
                weight=weight, category="nodes")
            evidences.append(ev)
            if is_home:
                home_score += weight
            else:
                away_score += weight
        elif node["effect"] == "weaken":
            weight = 2.0 * node["strength"]
            ev = FrawleyEvidence(
                description=f"{lord.name} (代表 {team_name}) 合南交點 — 距離 {node['distance']:.1f}° — 大幅削弱",
                favors="away" if is_home else "home",
                weight=weight, category="nodes")
            evidences.append(ev)
            if is_home:
                away_score += weight
            else:
                home_score += weight

    # --- Step 5: Aspects ---
    for lord, team_name, is_home in [
        (home_lord, home_team, True),
        (away_lord, away_team, False),
    ]:
        aspects = evaluate_aspects_to_planet(lord, chart.planets)
        for asp in aspects:
            if asp["is_benefic"] is True:
                weight = 1.0 * asp["closeness"]
                ev = FrawleyEvidence(
                    description=f"{asp['planet']} ({asp['dignity']}) 對 {lord.name} "
                                f"形成 {asp['aspect']} — 有利 {team_name}",
                    favors="home" if is_home else "away",
                    weight=weight, category="aspect")
                evidences.append(ev)
                if is_home:
                    home_score += weight
                else:
                    away_score += weight
            elif asp["is_benefic"] is False:
                weight = 1.0 * asp["closeness"]
                ev = FrawleyEvidence(
                    description=f"{asp['planet']} ({asp['dignity']}) 對 {lord.name} "
                                f"形成 {asp['aspect']} — 不利 {team_name}",
                    favors="away" if is_home else "home",
                    weight=weight, category="aspect")
                evidences.append(ev)
                if is_home:
                    away_score += weight
                else:
                    home_score += weight

    # --- Step 6: Reception between Lords ---
    recep = evaluate_reception(home_lord, away_lord)
    if recep["type"] == "received":
        ev = FrawleyEvidence(
            description=f"接納: {recep['description']}",
            favors="home", weight=0.5, category="reception")
        evidences.append(ev)
        home_score += 0.5
    elif recep["type"] == "receives":
        ev = FrawleyEvidence(
            description=f"接納: {recep['description']}",
            favors="away", weight=0.5, category="reception")
        evidences.append(ev)
        away_score += 0.5

    # --- Step 7: Speed ---
    for lord, team_name, is_home in [
        (home_lord, home_team, True),
        (away_lord, away_team, False),
    ]:
        spd = evaluate_speed(lord)
        if spd["score"] != 0:
            favors = ("home" if is_home else "away") if spd["score"] > 0 \
                else ("away" if is_home else "home")
            ev = FrawleyEvidence(
                description=f"{spd['description']}",
                favors=favors, weight=abs(spd["score"]),
                category="speed")
            evidences.append(ev)
            if favors == "home":
                home_score += abs(spd["score"])
            else:
                away_score += abs(spd["score"])

    # --- Step 8: Essential Dignity (tiebreaker) ---
    dignity_order = {"exaltation": 4, "domicile": 3, "peregrine": 0,
                     "detriment": -2, "fall": -3}
    home_dig = dignity_order.get(home_lord.essential_dignity, 0)
    away_dig = dignity_order.get(away_lord.essential_dignity, 0)
    if home_dig != away_dig:
        diff = abs(home_dig - away_dig) * 0.3
        if home_dig > away_dig:
            ev = FrawleyEvidence(
                description=f"本質尊貴: {home_lord.name} ({home_lord.essential_dignity}) "
                            f"優於 {away_lord.name} ({away_lord.essential_dignity})",
                favors="home", weight=diff, category="essential_dignity")
            evidences.append(ev)
            home_score += diff
        else:
            ev = FrawleyEvidence(
                description=f"本質尊貴: {away_lord.name} ({away_lord.essential_dignity}) "
                            f"優於 {home_lord.name} ({home_lord.essential_dignity})",
                favors="away", weight=diff, category="essential_dignity")
            evidences.append(ev)
            away_score += diff

    # --- Step 9: Retrograde ---
    for lord, team_name, is_home in [
        (home_lord, home_team, True),
        (away_lord, away_team, False),
    ]:
        if lord.retrograde:
            ev = FrawleyEvidence(
                description=f"{lord.name} (代表 {team_name}) 逆行 — 輕微削弱",
                favors="away" if is_home else "home",
                weight=0.3, category="retrograde")
            evidences.append(ev)
            if is_home:
                away_score += 0.3
            else:
                home_score += 0.3

    # --- Step 10: Moon House Position ---
    moon_pos_ev = evaluate_moon_position(
        chart,
        home_assign.primary_house, away_assign.primary_house,
        home_assign.supporting_house, away_assign.supporting_house)
    evidences.extend(moon_pos_ev)
    for ev in moon_pos_ev:
        if ev.favors == "home":
            home_score += ev.weight
        elif ev.favors == "away":
            away_score += ev.weight

    # --- Step 11: Moon Applying Aspects (Final Aspect Rule) ---
    moon_asp_ev = evaluate_moon_applying_aspects(chart, home_lord, away_lord)
    evidences.extend(moon_asp_ev)
    for ev in moon_asp_ev:
        if ev.favors == "home":
            home_score += ev.weight
        elif ev.favors == "away":
            away_score += ev.weight

    # --- Step 12: Antiscion of Fortuna ---
    anti_ev = evaluate_antiscion_fortuna(
        chart, home_assign.primary_house, away_assign.primary_house)
    evidences.extend(anti_ev)
    for ev in anti_ev:
        if ev.favors == "home":
            home_score += ev.weight
        elif ev.favors == "away":
            away_score += ev.weight

    # --- Step 13: Lot of Fortune Aspects ---
    fort_ev = evaluate_fortuna_aspects(chart, home_lord, away_lord)
    evidences.extend(fort_ev)
    for ev in fort_ev:
        if ev.favors == "home":
            home_score += ev.weight
        elif ev.favors == "away":
            away_score += ev.weight

    # --- Step 14: Fixed Stars ---
    star_ev = evaluate_fixed_stars(home_lord, away_lord)
    evidences.extend(star_ev)
    for ev in star_ev:
        if ev.favors == "home":
            home_score += ev.weight
        elif ev.favors == "away":
            away_score += ev.weight

    # --- Step 15: Saturn as General Malefic ---
    saturn_ev = evaluate_saturn_malefic(
        chart, home_lord, away_lord,
        home_assign.primary_house, away_assign.primary_house)
    evidences.extend(saturn_ev)
    for ev in saturn_ev:
        if ev.favors == "home":
            home_score += ev.weight
        elif ev.favors == "away":
            away_score += ev.weight

    # --- Step 16: Moon Light / Phase ---
    light_ev = evaluate_moon_light(chart)
    evidences.extend(light_ev)
    # Moon light affects draw probability; scoring handled in summary

    # Build summary
    total = home_score + away_score
    if total == 0:
        total = 1
    home_pct = home_score / total * 100
    away_pct = away_score / total * 100

    if home_score > away_score * 1.5:
        summary = f"Frawley 判斷: {home_team} 明顯優勢 ({home_pct:.0f}% vs {away_pct:.0f}%)"
    elif away_score > home_score * 1.5:
        summary = f"Frawley 判斷: {away_team} 明顯優勢 ({away_pct:.0f}% vs {home_pct:.0f}%)"
    elif abs(home_score - away_score) < 0.5:
        summary = f"Frawley 判斷: 勢均力敵，可能平局 ({home_pct:.0f}% vs {away_pct:.0f}%)"
    elif home_score > away_score:
        summary = f"Frawley 判斷: {home_team} 略佔優勢 ({home_pct:.0f}% vs {away_pct:.0f}%)"
    else:
        summary = f"Frawley 判斷: {away_team} 略佔優勢 ({away_pct:.0f}% vs {home_pct:.0f}%)"

    testimonies = _lord_testimonies_summary(evidences, home_score, away_score)
    injury_risk = _injury_risk_indicator(
        home_lord=home_lord,
        away_lord=away_lord,
        home_house=home_assign.primary_house,
        away_house=away_assign.primary_house,
    )
    reversal_indicator = _reversal_indicator(chart, home_lord, away_lord)

    return {
        "evidences": evidences,
        "home_score": home_score,
        "away_score": away_score,
        "summary": summary,
        "home_assign": home_assign,
        "away_assign": away_assign,
        "testimonies": testimonies,
        "injury_risk": injury_risk,
        "reversal_indicator": reversal_indicator,
    }
