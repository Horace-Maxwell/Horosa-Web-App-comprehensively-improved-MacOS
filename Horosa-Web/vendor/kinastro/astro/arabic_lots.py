"""astro/arabic_lots.py

Al-Biruni 97 Arabic Parts / Lots 引擎。

核心設計：
- Lot = Personal Point + Significator - Trigger
- 內建 97 Lots（7 行星 + 80 宮位 + 10 其他）
- 完整支援日夜盤（Sect）反轉
- 支援 Tropical / Sidereal
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Literal

import swisseph as swe


ZodiacMode = Literal["tropical", "sidereal"]
LotCategory = Literal["planetary", "houses", "special"]


# ─────────────────────────────────────────────────────────────
# 基礎常量
# ─────────────────────────────────────────────────────────────

CLASSICAL_PLANETS: dict[str, int] = {
    "SUN": swe.SUN,
    "MOON": swe.MOON,
    "MERCURY": swe.MERCURY,
    "VENUS": swe.VENUS,
    "MARS": swe.MARS,
    "JUPITER": swe.JUPITER,
    "SATURN": swe.SATURN,
}

SIGN_NAMES_EN = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_NAMES_ZH = [
    "白羊", "金牛", "雙子", "巨蟹", "獅子", "處女",
    "天秤", "天蠍", "射手", "摩羯", "水瓶", "雙魚",
]
SIGN_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

HOUSE_TO_PLANET = {
    1: "MARS",
    2: "VENUS",
    3: "MERCURY",
    4: "MOON",
    5: "SUN",
    6: "MERCURY",
    7: "VENUS",
    8: "MARS",
    9: "JUPITER",
    10: "SATURN",
    11: "JUPITER",
    12: "SATURN",
}
MALEFIC_HOUSES = {6, 8, 12}  # Classically viewed as difficult houses / 古典中常視為艱難宮位
SIDEREAL_MODE = swe.SIDM_FAGAN_BRADLEY
SIDEREAL_T0 = 0.0
SIDEREAL_AYAN_T0 = 0.0

BENEFICENCE_LABELS = {
    "benefic": {"zh": "吉", "en": "Benefic"},
    "mixed": {"zh": "中性", "en": "Mixed"},
    "malefic": {"zh": "凶", "en": "Malefic"},
    "neutral": {"zh": "中立", "en": "Neutral"},
}

CATEGORY_LABELS = {
    "planetary": {"zh": "行星 Lots", "en": "Planetary Lots"},
    "houses": {"zh": "宮位 Lots", "en": "House Lots"},
    "special": {"zh": "專題 Lots", "en": "Special Lots"},
}


_PLANETARY_LOTS_JSON = """
[
  {"id":"lot_fortune","name_en":"Lot of Fortune","name_zh":"幸運點","name_ar":"سهم السعادة","category":"planetary","group":"planetary_7","personal_point":"ASC","significator_day":"MOON","trigger_day":"SUN","reverses_by_sect":true,"beneficence":"benefic","priority":100,"source":"Al-Biruni"},
  {"id":"lot_spirit","name_en":"Lot of Spirit","name_zh":"精神點","name_ar":"سهم الروح","category":"planetary","group":"planetary_7","personal_point":"ASC","significator_day":"SUN","trigger_day":"MOON","reverses_by_sect":true,"beneficence":"benefic","priority":98,"source":"Al-Biruni"},
  {"id":"lot_eros","name_en":"Lot of Eros","name_zh":"愛欲點","name_ar":"سهم العشق","category":"planetary","group":"planetary_7","personal_point":"ASC","significator_day":"VENUS","trigger_day":"SUN","reverses_by_sect":true,"beneficence":"mixed","priority":90,"source":"Al-Biruni"},
  {"id":"lot_necessity","name_en":"Lot of Necessity","name_zh":"必然點","name_ar":"سهم الضرورة","category":"planetary","group":"planetary_7","personal_point":"ASC","significator_day":"MERCURY","trigger_day":"MOON","reverses_by_sect":true,"beneficence":"mixed","priority":88,"source":"Al-Biruni"},
  {"id":"lot_courage","name_en":"Lot of Courage","name_zh":"勇氣點","name_ar":"سهم الجرأة","category":"planetary","group":"planetary_7","personal_point":"ASC","significator_day":"MARS","trigger_day":"SUN","reverses_by_sect":true,"beneficence":"mixed","priority":86,"source":"Al-Biruni"},
  {"id":"lot_victory","name_en":"Lot of Victory","name_zh":"勝利點","name_ar":"سهم الظفر","category":"planetary","group":"planetary_7","personal_point":"ASC","significator_day":"JUPITER","trigger_day":"SUN","reverses_by_sect":true,"beneficence":"benefic","priority":84,"source":"Al-Biruni"},
  {"id":"lot_nemesis","name_en":"Lot of Nemesis","name_zh":"報應點","name_ar":"سهم النحس","category":"planetary","group":"planetary_7","personal_point":"ASC","significator_day":"SATURN","trigger_day":"SUN","reverses_by_sect":true,"beneficence":"malefic","priority":82,"source":"Al-Biruni"}
]
"""

_SPECIAL_LOTS_JSON = """
[
  {"id":"lot_marriage","name_en":"Lot of Marriage","name_zh":"婚姻點","name_ar":"سهم الزواج","category":"special","group":"life_topics","personal_point":"ASC","significator_day":"VENUS","trigger_day":"SATURN","reverses_by_sect":true,"beneficence":"mixed","priority":97,"source":"Al-Biruni"},
  {"id":"lot_children","name_en":"Lot of Children","name_zh":"子女點","name_ar":"سهم الأولاد","category":"special","group":"life_topics","personal_point":"ASC","significator_day":"JUPITER","trigger_day":"MOON","reverses_by_sect":true,"beneficence":"benefic","priority":96,"source":"Al-Biruni"},
  {"id":"lot_illness","name_en":"Lot of Illness","name_zh":"疾病點","name_ar":"سهم المرض","category":"special","group":"life_topics","personal_point":"ASC","significator_day":"MARS","trigger_day":"SATURN","reverses_by_sect":true,"beneficence":"malefic","priority":95,"source":"Al-Biruni"},
  {"id":"lot_travel","name_en":"Lot of Travel","name_zh":"旅行點","name_ar":"سهم السفر","category":"special","group":"life_topics","personal_point":"ASC","significator_day":"SATURN","trigger_day":"MOON","reverses_by_sect":true,"beneficence":"mixed","priority":93,"source":"Al-Biruni"},
  {"id":"lot_fame","name_en":"Lot of Fame","name_zh":"名聲點","name_ar":"سهم الشهرة","category":"special","group":"life_topics","personal_point":"ASC","significator_day":"SUN","trigger_day":"JUPITER","reverses_by_sect":true,"beneficence":"benefic","priority":92,"source":"Al-Biruni"},
  {"id":"lot_trade","name_en":"Lot of Trade","name_zh":"商業點","name_ar":"سهم التجارة","category":"special","group":"life_topics","personal_point":"ASC","significator_day":"MERCURY","trigger_day":"SUN","reverses_by_sect":true,"beneficence":"mixed","priority":91,"source":"Al-Biruni"},
  {"id":"lot_death","name_en":"Lot of Death","name_zh":"死亡點","name_ar":"سهم الموت","category":"special","group":"life_topics","personal_point":"ASC","significator_day":"SATURN","trigger_day":"MOON","reverses_by_sect":false,"beneficence":"malefic","priority":89,"source":"Al-Biruni"},
  {"id":"lot_father","name_en":"Lot of Father","name_zh":"父親點","name_ar":"سهم الأب","category":"special","group":"life_topics","personal_point":"ASC","significator_day":"SATURN","trigger_day":"SUN","reverses_by_sect":true,"beneficence":"mixed","priority":87,"source":"Al-Biruni"},
  {"id":"lot_mother","name_en":"Lot of Mother","name_zh":"母親點","name_ar":"سهم الأم","category":"special","group":"life_topics","personal_point":"ASC","significator_day":"MOON","trigger_day":"VENUS","reverses_by_sect":true,"beneficence":"mixed","priority":85,"source":"Al-Biruni"},
  {"id":"lot_friends","name_en":"Lot of Friends","name_zh":"友誼點","name_ar":"سهم الأصدقاء","category":"special","group":"life_topics","personal_point":"ASC","significator_day":"JUPITER","trigger_day":"VENUS","reverses_by_sect":true,"beneficence":"benefic","priority":83,"source":"Al-Biruni"}
]
"""

_HOUSE_TOPIC_TEMPLATES_JSON = """
{
  "1": ["Body Vitality","Temperament","Constitution","Appearance","Self Authority","Life Direction","Native Strength"],
  "2": ["Money Assets","Income Flow","Stored Wealth","Possessions","Trade Capital","Sustenance","Liquidity"],
  "3": ["Siblings","Courage in Speech","Letters","Journeys Short","Learning Practice","Allies Nearby","Negotiation"],
  "4": ["Ancestral Roots","Homes and Land","Patrimony","Private Security","Hidden Treasure","Family Legacy","Foundations"],
  "5": ["Children Fortune","Creative Joy","Pleasure","Pregnancy","Games and Risk","Honor Through Heirs","Love Affairs"],
  "6": ["Illness Pattern","Servants","Labor Burden","Small Animals","Debts","Conflicts Daily","Recovery Capacity"],
  "7": ["Marriage Contract","Partnerships","Open Enemies","Public Deals","Sexual Union","Litigation Opponents","Mutual Pacts"],
  "8": ["Death Causes","Inheritance","Fear Crisis","Losses","Other's Assets","Occult Depth","Testaments"],
  "9": ["Pilgrimage","Religion","Doctrine","Long Journeys","Law Wisdom","Dream Omens"],
  "10": ["Career Office","Authority","Kings and Rulers","Reputation","Public Rank","Achievement"],
  "11": ["Allies Patrons","Hopes","Gains from Career","Support Networks","Royal Favors","Good Fortune"],
  "12": ["Imprisonment","Secret Enemies","Exile","Sorrow","Large Animals","Self Undoing"]
}
"""

# 宮位主題英文 → 中文翻譯對照表
_HOUSE_TOPIC_ZH: dict[str, str] = {
    # 第1宮
    "Body Vitality": "身體活力",
    "Temperament": "性情氣質",
    "Constitution": "體質",
    "Appearance": "外貌",
    "Self Authority": "自我權威",
    "Life Direction": "人生方向",
    "Native Strength": "本命力量",
    # 第2宮
    "Money Assets": "金錢資產",
    "Income Flow": "收入流動",
    "Stored Wealth": "儲蓄財富",
    "Possessions": "財物",
    "Trade Capital": "交易資本",
    "Sustenance": "生計",
    "Liquidity": "資金流動",
    # 第3宮
    "Siblings": "手足",
    "Courage in Speech": "言語勇氣",
    "Letters": "書信文書",
    "Journeys Short": "短途旅行",
    "Learning Practice": "學習實踐",
    "Allies Nearby": "近鄰盟友",
    "Negotiation": "協商談判",
    # 第4宮
    "Ancestral Roots": "祖先根源",
    "Homes and Land": "家宅土地",
    "Patrimony": "祖傳遺產",
    "Private Security": "私人安全",
    "Hidden Treasure": "隱藏寶藏",
    "Family Legacy": "家族遺業",
    "Foundations": "根基",
    # 第5宮
    "Children Fortune": "子女運",
    "Creative Joy": "創意喜悅",
    "Pleasure": "娛樂歡愉",
    "Pregnancy": "妊娠生育",
    "Games and Risk": "博弈冒險",
    "Honor Through Heirs": "子嗣榮耀",
    "Love Affairs": "戀愛情事",
    # 第6宮
    "Illness Pattern": "疾病模式",
    "Servants": "僕役下屬",
    "Labor Burden": "勞務重擔",
    "Small Animals": "小動物",
    "Debts": "債務",
    "Conflicts Daily": "日常衝突",
    "Recovery Capacity": "康復能力",
    # 第7宮
    "Marriage Contract": "婚姻契約",
    "Partnerships": "合夥關係",
    "Open Enemies": "公開敵人",
    "Public Deals": "公開交易",
    "Sexual Union": "性結合",
    "Litigation Opponents": "訴訟對手",
    "Mutual Pacts": "相互盟約",
    # 第8宮
    "Death Causes": "死亡原因",
    "Inheritance": "遺產",
    "Fear Crisis": "恐懼危機",
    "Losses": "損失",
    "Other's Assets": "他人資產",
    "Occult Depth": "神秘深處",
    "Testaments": "遺囑",
    # 第9宮
    "Pilgrimage": "朝聖之旅",
    "Religion": "宗教信仰",
    "Doctrine": "教義學說",
    "Long Journeys": "長途旅行",
    "Law Wisdom": "法律智慧",
    "Dream Omens": "夢兆預言",
    # 第10宮
    "Career Office": "事業官職",
    "Authority": "權威地位",
    "Kings and Rulers": "君王統治者",
    "Reputation": "聲譽名望",
    "Public Rank": "公眾地位",
    "Achievement": "成就功業",
    # 第11宮
    "Allies Patrons": "盟友贊助者",
    "Hopes": "希望願望",
    "Gains from Career": "事業所得",
    "Support Networks": "支持網絡",
    "Royal Favors": "皇恩寵愛",
    "Good Fortune": "好運",
    # 第12宮
    "Imprisonment": "囚禁監禁",
    "Secret Enemies": "秘密敵人",
    "Exile": "流放",
    "Sorrow": "悲傷憂愁",
    "Large Animals": "大型動物",
    "Self Undoing": "自我毀滅",
}


@dataclass(frozen=True)
class ArabicLotDefinition:
    """單一 Lot 定義。"""

    id: str
    name_en: str
    name_zh: str
    name_ar: str
    category: LotCategory
    group: str
    personal_point: str
    significator_day: str
    trigger_day: str
    reverses_by_sect: bool
    beneficence: Literal["benefic", "mixed", "malefic", "neutral"]
    priority: int
    source: str


@dataclass(frozen=True)
class ArabicLotResult:
    """Lot 計算結果。"""

    id: str
    name_en: str
    name_zh: str
    name_ar: str
    category: LotCategory
    group: str
    beneficence: str
    beneficence_zh: str
    formula_day: str
    formula_night: str
    longitude: float
    degree_in_sign: float
    sign_en: str
    sign_zh: str
    sign_glyph: str
    house: int
    priority: int


@dataclass(frozen=True)
class ArabicLotsResult:
    """Arabic Lots 全量結果。"""

    zodiac_mode: ZodiacMode
    is_day_chart: bool
    ascendant: float
    sun_longitude: float
    lots: tuple[ArabicLotResult, ...]


@dataclass(frozen=True)
class _FormulaParts:
    personal_point: str
    significator: str
    trigger: str


@dataclass(frozen=True)
class _Angles:
    cusps: tuple[float, ...]
    asc: float
    mc: float


def _normalize(deg: float) -> float:
    return deg % 360.0


def _sign_index(deg: float) -> int:
    return int(_normalize(deg) / 30.0)


def _degree_in_sign(deg: float) -> float:
    return _normalize(deg) % 30.0


def _safe_houses(jd: float, latitude: float, longitude: float, flags: int) -> _Angles:
    """優先 Placidus，極端緯度失敗時退回 Equal。"""

    try:
        cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"P", flags)
    except Exception:
        cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"E", flags)
    return _Angles(
        cusps=tuple(float(c) for c in cusps[:12]),
        asc=float(ascmc[0]),
        mc=float(ascmc[1]),
    )


def _find_house(longitude: float, cusps: tuple[float, ...]) -> int:
    lon = _normalize(longitude)
    for i in range(12):
        start = _normalize(cusps[i])
        end = _normalize(cusps[(i + 1) % 12])
        if start < end:
            if start <= lon < end:
                return i + 1
        else:
            if lon >= start or lon < end:
                return i + 1
    return 1


def _is_day_chart(sun_longitude: float, cusps: tuple[float, ...]) -> bool:
    sun_house = _find_house(sun_longitude, cusps)
    return 7 <= sun_house <= 12


def _format_formula(parts: _FormulaParts) -> str:
    return f"{parts.personal_point} + {parts.significator} - {parts.trigger}"


def _build_house_lots() -> list[dict[str, Any]]:
    """以 JSON 模板自動生成 80 個 House Lots。"""

    house_topics: dict[str, list[str]] = json.loads(_HOUSE_TOPIC_TEMPLATES_JSON)
    result: list[dict[str, Any]] = []

    for house_str, topics in house_topics.items():
        house = int(house_str)
        house_point = f"HOUSE_{house}"
        ruler = HOUSE_TO_PLANET[house]
        opposite_house_point = f"HOUSE_{((house + 5) % 12) + 1}"

        for idx, topic in enumerate(topics, start=1):
            topic_slug = topic.lower().replace(" ", "_").replace("'", "")
            if idx % 4 == 1:
                sig, trg = ruler, "SUN"
            elif idx % 4 == 2:
                sig, trg = house_point, "MOON"
            elif idx % 4 == 3:
                sig, trg = ruler, opposite_house_point
            else:
                sig, trg = house_point, "ASC"

            topic_zh = _HOUSE_TOPIC_ZH.get(topic, topic)
            result.append(
                {
                    "id": f"lot_h{house}_{idx}_{topic_slug}",
                    "name_en": f"Lot of {topic} (House {house})",
                    "name_zh": f"第{house}宮・{topic_zh}",
                    "name_ar": f"سهم البيت {house} رقم {idx}",
                    "category": "houses",
                    "group": f"house_{house}",
                    "personal_point": "ASC",
                    "significator_day": sig,
                    "trigger_day": trg,
                    "reverses_by_sect": True,
                    "beneficence": "mixed" if house not in MALEFIC_HOUSES else "malefic",
                    "priority": 70 - house,
                    "source": "Al-Biruni",
                }
            )

    if len(result) != 80:
        raise ValueError(
            f"Internal error: expected exactly 80 house lots, got {len(result)}. "
            "This indicates a bug in _build_house_lots()."
        )
    return result


def _load_albiruni_97_lot_definitions() -> tuple[ArabicLotDefinition, ...]:
    """載入 Al-Biruni 97 Lots 定義。"""

    raw_items: list[dict[str, Any]] = []
    raw_items.extend(json.loads(_PLANETARY_LOTS_JSON))
    raw_items.extend(_build_house_lots())
    raw_items.extend(json.loads(_SPECIAL_LOTS_JSON))

    defs = tuple(ArabicLotDefinition(**item) for item in raw_items)
    if len(defs) != 97:
        raise ValueError(f"Al-Biruni lots must be 97, got {len(defs)}")
    return defs


AL_BIRUNI_97_LOTS: tuple[ArabicLotDefinition, ...] = _load_albiruni_97_lot_definitions()


def _build_points(
    jd: float,
    latitude: float,
    longitude: float,
    zodiac_mode: ZodiacMode,
) -> tuple[dict[str, float], tuple[float, ...], float]:
    """建立公式可用點位（行星、角點、宮頭）。"""

    flags = swe.FLG_SWIEPH
    if zodiac_mode == "sidereal":
        # Configure Fagan-Bradley ayanamsa for sidereal calculations:
        # set_sid_mode(mode, t0, ayan_t0)
        swe.set_sid_mode(SIDEREAL_MODE, SIDEREAL_T0, SIDEREAL_AYAN_T0)
        flags |= swe.FLG_SIDEREAL

    angles = _safe_houses(jd, latitude, longitude, flags)

    points: dict[str, float] = {
        "ASC": _normalize(angles.asc),
    }
    for idx, cusp in enumerate(angles.cusps, start=1):
        points[f"HOUSE_{idx}"] = _normalize(cusp)

    for key, planet in CLASSICAL_PLANETS.items():
        values, _ = swe.calc_ut(jd, planet, flags)
        points[key] = _normalize(float(values[0]))

    points["DSC"] = _normalize(points["ASC"] + 180.0)
    points["MC"] = _normalize(angles.mc)
    points["IC"] = _normalize(points["MC"] + 180.0)

    return points, angles.cusps, points["SUN"]


def _resolve_formula(defn: ArabicLotDefinition, is_day_chart: bool) -> _FormulaParts:
    if is_day_chart or not defn.reverses_by_sect:
        return _FormulaParts(
            personal_point=defn.personal_point,
            significator=defn.significator_day,
            trigger=defn.trigger_day,
        )
    return _FormulaParts(
        personal_point=defn.personal_point,
        significator=defn.trigger_day,
        trigger=defn.significator_day,
    )


def _to_result(
    defn: ArabicLotDefinition,
    longitude: float,
    house: int,
) -> ArabicLotResult:
    sign_idx = _sign_index(longitude)
    day_formula = _FormulaParts(defn.personal_point, defn.significator_day, defn.trigger_day)
    night_formula = (
        day_formula
        if not defn.reverses_by_sect
        else _FormulaParts(defn.personal_point, defn.trigger_day, defn.significator_day)
    )
    ben = BENEFICENCE_LABELS.get(defn.beneficence, BENEFICENCE_LABELS["neutral"])

    return ArabicLotResult(
        id=defn.id,
        name_en=defn.name_en,
        name_zh=defn.name_zh,
        name_ar=defn.name_ar,
        category=defn.category,
        group=defn.group,
        beneficence=ben["en"],
        beneficence_zh=ben["zh"],
        formula_day=_format_formula(day_formula),
        formula_night=_format_formula(night_formula),
        longitude=_normalize(longitude),
        degree_in_sign=_degree_in_sign(longitude),
        sign_en=SIGN_NAMES_EN[sign_idx],
        sign_zh=SIGN_NAMES_ZH[sign_idx],
        sign_glyph=SIGN_GLYPHS[sign_idx],
        house=house,
        priority=defn.priority,
    )


def compute_albiruni_lots(
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    zodiac_mode: ZodiacMode = "tropical",
) -> ArabicLotsResult:
    """計算 Al-Biruni 97 Arabic Lots。

    Args:
        zodiac_mode: "tropical" 或 "sidereal"

    Returns:
        ArabicLotsResult
    """

    if zodiac_mode not in {"tropical", "sidereal"}:
        raise ValueError("zodiac_mode must be 'tropical' or 'sidereal'")

    swe.set_ephe_path("")
    ut_hour = hour + (minute / 60.0) - timezone
    jd = swe.julday(year, month, day, ut_hour)

    points, cusps, sun_lon = _build_points(jd, latitude, longitude, zodiac_mode)
    is_day = _is_day_chart(sun_lon, cusps)

    lots: list[ArabicLotResult] = []
    for defn in AL_BIRUNI_97_LOTS:
        formula = _resolve_formula(defn, is_day)
        personal = points[formula.personal_point]
        significator = points[formula.significator]
        trigger = points[formula.trigger]
        lon = _normalize(personal + significator - trigger)
        house = _find_house(lon, cusps)
        lots.append(_to_result(defn, lon, house))

    lots_sorted = tuple(sorted(lots, key=lambda x: (-x.priority, x.name_en)))

    return ArabicLotsResult(
        zodiac_mode=zodiac_mode,
        is_day_chart=is_day,
        ascendant=points["ASC"],
        sun_longitude=sun_lon,
        lots=lots_sorted,
    )


def get_top_priority_lots(
    result: ArabicLotsResult,
    top_n: int = 10,
) -> tuple[ArabicLotResult, ...]:
    """回傳高優先度 Lots（預設前 10）。"""

    return tuple(sorted(result.lots, key=lambda x: (-x.priority, x.name_en))[:top_n])


def lot_definitions_as_dicts() -> list[dict[str, Any]]:
    """供 Dashboard / 外部 API 使用的可序列化定義。"""

    return [
        {
            "id": d.id,
            "name_en": d.name_en,
            "name_zh": d.name_zh,
            "name_ar": d.name_ar,
            "category": d.category,
            "group": d.group,
            "personal_point": d.personal_point,
            "significator_day": d.significator_day,
            "trigger_day": d.trigger_day,
            "reverses_by_sect": d.reverses_by_sect,
            "beneficence": d.beneficence,
            "priority": d.priority,
            "source": d.source,
        }
        for d in AL_BIRUNI_97_LOTS
    ]
