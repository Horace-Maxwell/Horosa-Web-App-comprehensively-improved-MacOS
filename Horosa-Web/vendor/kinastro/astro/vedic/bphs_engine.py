"""
astro/vedic/bphs_engine.py — BPHS 經典解讀引擎
(Brihat Parashara Hora Shastra Interpretation Engine)

根據出生盤行星位置，自動匹配 bphs_data.py 中的經典論述，
產生宮位果報、行星阿瓦斯塔、友敵關係、王者瑜伽等解讀。
"""

import streamlit as st
from dataclasses import dataclass, field

from astro.vedic.bphs_data import (
    BPHS_BHAVA_PHALA,
    BPHS_DHANA_BHAVA,
    BPHS_SAPTAMA_BHAVA,
    BPHS_DASHAMA_BHAVA,
    BPHS_PANCHAMA_BHAVA,
    BPHS_SHASHTA_BHAVA,
    BPHS_NAVAMA_BHAVA,
    BPHS_ASHTAMA_BHAVA,
    BPHS_EKADASA_BHAVA,
    BPHS_DVADASHA_BHAVA,
    BPHS_GRAHA_MAITRI,
    BPHS_AVASTHAS,
    BPHS_GRAHA_SVARUPA,
    BPHS_UCCA_NEECHA,
    BPHS_MOOLA_TRIKONA,
    BPHS_RAJA_YOGA,
    BPHS_SHODASA_VARGA,
    BPHS_RASHI,
)

# ============================================================
# Constants & helpers
# ============================================================

# Canonical planet key mapping (Vedic display name → lowercase key)
_VEDIC_TO_KEY = {
    "Surya": "sun", "Chandra": "moon", "Mangal": "mars",
    "Budha": "mercury", "Guru": "jupiter", "Shukra": "venus",
    "Shani": "saturn", "Rahu": "rahu", "Ketu": "ketu",
    "Sun": "sun", "Moon": "moon", "Mars": "mars",
    "Mercury": "mercury", "Jupiter": "jupiter", "Venus": "venus",
    "Saturn": "saturn",
}

_KEY_CN = {
    "sun": "太陽", "moon": "月亮", "mars": "火星",
    "mercury": "水星", "jupiter": "木星", "venus": "金星",
    "saturn": "土星", "rahu": "羅睺", "ketu": "計都",
}

# Rashi English name → 0-based index
_RASHI_IDX = {
    "Mesha": 0, "Vrishabha": 1, "Mithuna": 2, "Karka": 3,
    "Simha": 4, "Kanya": 5, "Tula": 6, "Vrischika": 7,
    "Dhanu": 8, "Makara": 9, "Kumbha": 10, "Meena": 11,
    "Aries": 0, "Taurus": 1, "Gemini": 2, "Cancer": 3,
    "Leo": 4, "Virgo": 5, "Libra": 6, "Scorpio": 7,
    "Sagittarius": 8, "Capricorn": 9, "Aquarius": 10, "Pisces": 11,
}

# Sign lord (0-11 index → canonical lowercase key)
_SIGN_LORD = {
    0: "mars", 1: "venus", 2: "mercury", 3: "moon",
    4: "sun", 5: "mercury", 6: "venus", 7: "mars",
    8: "jupiter", 9: "saturn", 10: "saturn", 11: "jupiter",
}

_RASHI_EN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def _planet_key(name: str) -> str:
    """Extract canonical lowercase key from a display name like 'Surya (太陽)'."""
    first = name.split("(")[0].strip().split()[0]
    return _VEDIC_TO_KEY.get(first, first.lower())


def _sign_index(lon: float) -> int:
    return int(lon % 360.0 / 30.0) % 12


def _house_from(from_sign: int, to_sign: int) -> int:
    """1-based house number of *to_sign* counted from *from_sign*."""
    return (to_sign - from_sign) % 12 + 1


# ============================================================
# Data classes for BPHS results
# ============================================================

@dataclass
class BhavaReading:
    """Single bhava (house) interpretation."""
    bhava: int
    bhava_zh: str
    signification: str
    lord_key: str
    lord_zh: str
    lord_house: int
    lord_placement_zh: str
    planets_in_bhava: list  # list of (key, zh, reading_zh, level)
    special_yogas: list     # list of dicts
    note_zh: str


@dataclass
class GrahaMaitriRow:
    """One planet's friendship table."""
    planet: str
    planet_zh: str
    friends_zh: str
    neutral_zh: str
    enemies_zh: str


@dataclass
class AvasthaPlanetRow:
    """A planet's avastha interpretation."""
    planet: str
    planet_zh: str
    avastha_name: str
    reading_zh: str
    strength: str


@dataclass
class DignityRow:
    """A planet's dignity status."""
    planet: str
    planet_zh: str
    rashi_en: str
    rashi_zh: str
    uccha: bool       # exalted
    neecha: bool      # debilitated
    moola_trikona: bool
    own_sign: bool
    status_zh: str


@dataclass
class RajaYogaHit:
    """Detected raja yoga."""
    name: str
    description_zh: str
    is_present: bool
    reason_zh: str


@dataclass
class BPHSResult:
    """Full BPHS interpretation result."""
    bhava_readings: list = field(default_factory=list)
    graha_maitri: list = field(default_factory=list)
    avasthas: list = field(default_factory=list)
    dignities: list = field(default_factory=list)
    raja_yogas: list = field(default_factory=list)
    varga_info: dict = field(default_factory=dict)


# ============================================================
# Detailed bhava data map (bhava_number → BPHS_XXX_BHAVA dict)
# ============================================================

_BHAVA_DETAIL = {
    2: BPHS_DHANA_BHAVA,
    5: BPHS_PANCHAMA_BHAVA,
    6: BPHS_SHASHTA_BHAVA,
    7: BPHS_SAPTAMA_BHAVA,
    8: BPHS_ASHTAMA_BHAVA,
    9: BPHS_NAVAMA_BHAVA,
    10: BPHS_DASHAMA_BHAVA,
    11: BPHS_EKADASA_BHAVA,
    12: BPHS_DVADASHA_BHAVA,
}


# ============================================================
# Core computation
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_bphs(planet_positions: list, houses: list,
                 ascendant_lon: float) -> BPHSResult:
    """Compute BPHS interpretations from a VedicChart.

    Parameters
    ----------
    planet_positions : list
        List of VedicPlanet (or any object with .name, .longitude, .house, .rashi).
    houses : list
        List of VedicHouse (or any object with .number, .cusp, .rashi).
    ascendant_lon : float
        Ascendant longitude in sidereal degrees.

    Returns
    -------
    BPHSResult
    """
    asc_sign = _sign_index(ascendant_lon)

    # Build helper structures
    # planet_key → (sign_index, house_number, rashi_vedic_name)
    planet_map = {}
    for p in planet_positions:
        key = _planet_key(p.name)
        sign = _sign_index(p.longitude)
        planet_map[key] = {
            "sign": sign,
            "house": p.house,
            "rashi": p.rashi,
            "lon": p.longitude,
            "name": p.name,
        }

    # planets_in_house[house_number] → list of (key, sign)
    planets_in_house = {i: [] for i in range(1, 13)}
    for key, info in planet_map.items():
        planets_in_house[info["house"]].append(key)

    result = BPHSResult()

    # 1. Bhava readings
    result.bhava_readings = _compute_bhava_readings(
        asc_sign, planet_map, planets_in_house)

    # 2. Graha Maitri
    result.graha_maitri = _compute_graha_maitri()

    # 3. Avasthas (simplified — uses nakshatra-based modular calculation)
    result.avasthas = _compute_avasthas(planet_map)

    # 4. Dignities
    result.dignities = _compute_dignities(planet_map)

    # 5. Raja Yogas
    result.raja_yogas = _compute_raja_yogas(asc_sign, planet_map)

    # 6. Varga info (reference)
    result.varga_info = BPHS_SHODASA_VARGA

    return result


# ============================================================
# Sub-computations
# ============================================================

def _compute_bhava_readings(asc_sign, planet_map, planets_in_house):
    """Generate readings for all 12 bhavas."""
    readings = []
    for bhava_num in range(1, 13):
        basic = BPHS_BHAVA_PHALA.get(bhava_num, {})
        bhava_zh = basic.get("zh", f"第{bhava_num}宮")
        signification = basic.get("signification", "")

        # Lord of this bhava
        bhava_sign = (asc_sign + bhava_num - 1) % 12
        lord_key = _SIGN_LORD[bhava_sign]
        lord_zh = _KEY_CN.get(lord_key, lord_key)

        # Where is the lord placed?
        lord_info = planet_map.get(lord_key)
        lord_house = lord_info["house"] if lord_info else 0

        # Lord placement reading from detailed bhava data
        lord_placement_zh = ""
        detail = _BHAVA_DETAIL.get(bhava_num)
        if detail and "lord_placement" in detail:
            lp = detail["lord_placement"].get(lord_house)
            if lp:
                lord_placement_zh = lp.get("zh", "")

        # Planets in this bhava
        planet_readings = []
        planet_keys_in = planets_in_house.get(bhava_num, [])
        if detail:
            # figure out the right planet_in_Xth key
            planet_field = None
            for candidate in [f"planet_in_{bhava_num}th",
                              f"planet_in_{bhava_num}nd",
                              f"planet_in_{bhava_num}st",
                              f"planet_in_{bhava_num}rd"]:
                if candidate in detail:
                    planet_field = candidate
                    break
            if planet_field is None:
                # Try all keys that start with "planet_in_"
                for k in detail:
                    if k.startswith("planet_in_"):
                        planet_field = k
                        break

            if planet_field:
                for pk in planet_keys_in:
                    reading_data = detail[planet_field].get(pk, {})
                    reading_zh = reading_data.get("zh", "")
                    # Get the level field (varies: wealth_level, marriage_level, etc.)
                    level = ""
                    for lk in reading_data:
                        if lk.endswith("_level") or lk == "level":
                            level = reading_data[lk]
                            break
                    planet_readings.append((
                        pk, _KEY_CN.get(pk, pk), reading_zh, level,
                    ))

        # Special yogas
        special_yogas = []
        if detail and "special_yogas" in detail:
            special_yogas = detail["special_yogas"]

        note_zh = detail.get("note_zh", "") if detail else ""

        readings.append(BhavaReading(
            bhava=bhava_num,
            bhava_zh=bhava_zh,
            signification=signification,
            lord_key=lord_key,
            lord_zh=lord_zh,
            lord_house=lord_house,
            lord_placement_zh=lord_placement_zh,
            planets_in_bhava=planet_readings,
            special_yogas=special_yogas,
            note_zh=note_zh,
        ))
    return readings


def _compute_graha_maitri():
    """Build friendship table for all 7 planets."""
    rows = []
    for pk, data in BPHS_GRAHA_MAITRI.items():
        rows.append(GrahaMaitriRow(
            planet=pk,
            planet_zh=_KEY_CN.get(pk, pk),
            friends_zh="、".join(_KEY_CN.get(f, f) for f in data["friends"]),
            neutral_zh="、".join(_KEY_CN.get(n, n) for n in data["neutral"]),
            enemies_zh="、".join(_KEY_CN.get(e, e) for e in data["enemies"]),
        ))
    return rows


def _compute_avasthas(planet_map):
    """Compute simplified avastha for each planet.

    Full BPHS avastha calculation requires nakshatra index × planet index ×
    navamsa index + birth nakshatra + birth time + ascendant index, divided by 12.
    Here we use a simplified version: (nakshatra_index × planet_serial) mod 12.
    """
    avastha_list = BPHS_AVASTHAS["avastha_list"]

    _PLANET_SERIAL = {
        "sun": 1, "moon": 2, "mars": 3, "mercury": 4,
        "jupiter": 5, "venus": 6, "saturn": 7, "rahu": 8, "ketu": 9,
    }

    rows = []
    for pk, info in planet_map.items():
        if pk not in _PLANET_SERIAL:
            continue
        serial = _PLANET_SERIAL[pk]
        lon = info["lon"]
        nak_idx = int((lon % 360.0) / (360.0 / 27.0)) % 27
        # Simplified: (nak_idx × serial) mod 12
        avastha_idx = (nak_idx * serial) % 12
        avastha_name = avastha_list[avastha_idx]

        planet_avasthas = BPHS_AVASTHAS.get(pk, {})
        av_data = planet_avasthas.get(avastha_name, {})
        reading_zh = av_data.get("zh", "無詳細資料")
        strength = av_data.get("strength", "未知")

        rows.append(AvasthaPlanetRow(
            planet=pk,
            planet_zh=_KEY_CN.get(pk, pk),
            avastha_name=avastha_name,
            reading_zh=reading_zh,
            strength=strength,
        ))
    return rows


def _compute_dignities(planet_map):
    """Evaluate each planet's dignity (exalted, debilitated, etc.)."""
    rows = []
    for pk, info in planet_map.items():
        sign_idx = info["sign"]
        rashi_en = _RASHI_EN_NAMES[sign_idx]
        rashi_zh_map = {
            0: "白羊", 1: "金牛", 2: "雙子", 3: "巨蟹",
            4: "獅子", 5: "處女", 6: "天秤", 7: "天蠍",
            8: "射手", 9: "摩羯", 10: "水瓶", 11: "雙魚",
        }
        rashi_zh = rashi_zh_map.get(sign_idx, "")

        uccha = False
        neecha = False
        mt = False
        own = False

        ucca_data = BPHS_UCCA_NEECHA.get(pk, {})
        if ucca_data:
            ucca_sign = ucca_data.get("ucca", "")
            neecha_sign = ucca_data.get("neecha", "")
            if _RASHI_IDX.get(ucca_sign) == sign_idx:
                uccha = True
            if _RASHI_IDX.get(neecha_sign) == sign_idx:
                neecha = True

        mt_sign = BPHS_MOOLA_TRIKONA.get(pk, "")
        if mt_sign and _RASHI_IDX.get(mt_sign) == sign_idx:
            mt = True

        # Own sign: planet is lord of this sign
        if _SIGN_LORD.get(sign_idx) == pk:
            own = True

        # Status summary
        statuses = []
        if uccha:
            statuses.append("曜旺 (Exalted)")
        if neecha:
            statuses.append("曜陷 (Debilitated)")
        if mt:
            statuses.append("根本三角 (Moola Trikona)")
        if own:
            statuses.append("自宮 (Own Sign)")
        if not statuses:
            statuses.append("普通 (Neutral)")

        rows.append(DignityRow(
            planet=pk,
            planet_zh=_KEY_CN.get(pk, pk),
            rashi_en=rashi_en,
            rashi_zh=rashi_zh,
            uccha=uccha,
            neecha=neecha,
            moola_trikona=mt,
            own_sign=own,
            status_zh="、".join(statuses),
        ))
    return rows


def _compute_raja_yogas(asc_sign, planet_map):
    """Detect BPHS raja yogas and special yogas."""
    results = []

    # Helper: get house number of a planet
    def _house(pk):
        info = planet_map.get(pk)
        return info["house"] if info else 0

    def _sign(pk):
        info = planet_map.get(pk)
        return info["sign"] if info else -1

    # 9th & 10th lord signs
    lord_9 = _SIGN_LORD[(asc_sign + 8) % 12]
    lord_10 = _SIGN_LORD[(asc_sign + 9) % 12]

    # 1. Dharma Karmadhipati Yoga: 9L and 10L conjunction or exchange
    if lord_9 in planet_map and lord_10 in planet_map:
        same_sign = _sign(lord_9) == _sign(lord_10)
        exchange = (_house(lord_9) == 10 and _house(lord_10) == 9)
        present = same_sign or exchange
        reason = ""
        if same_sign:
            reason = f"9宮主{_KEY_CN[lord_9]}與10宮主{_KEY_CN[lord_10]}同宮"
        elif exchange:
            reason = f"9宮主{_KEY_CN[lord_9]}與10宮主{_KEY_CN[lord_10]}互換"
        results.append(RajaYogaHit(
            name="Dharma Karmadhipati Yoga",
            description_zh="9宮主與10宮主互換位置或相合 → 極高地位、宗教與事業完美結合",
            is_present=present,
            reason_zh=reason if present else "9宮主與10宮主未相合或互換",
        ))

    # 2. Gaja Kesari Yoga: Jupiter in kendra from Moon
    if "jupiter" in planet_map and "moon" in planet_map:
        jup_sign = _sign("jupiter")
        moon_sign = _sign("moon")
        diff = (jup_sign - moon_sign) % 12
        present = diff in (0, 3, 6, 9)
        results.append(RajaYogaHit(
            name="Gaja Kesari Yoga",
            description_zh="木星與月亮相合或成角宮 → 智慧、名聲、財富、權力",
            is_present=present,
            reason_zh=f"木星在月亮{diff+1}宮" if present else "木星與月亮未成角宮關係",
        ))

    # 3. Pancha Mahapurusha: check each of 5 planets
    mahapurusha = [
        ("mars", [0, 7], "Ruchaka Yoga", "火星落自宮(白羊/天蠍)且在角宮 → 勇猛、領導力"),
        ("mercury", [2, 5], "Bhadra Yoga", "水星落自宮(雙子/處女)且在角宮 → 智慧、演說"),
        ("jupiter", [8, 11, 3], "Hamsa Yoga", "木星落自宮(射手/雙魚/巨蟹)且在角宮 → 智慧、靈性"),
        ("venus", [1, 6, 11], "Malavya Yoga", "金星落自宮(金牛/天秤/雙魚)且在角宮 → 美麗、藝術"),
        ("saturn", [9, 10, 6], "Sasa Yoga", "土星落自宮(摩羯/水瓶/天秤)且在角宮 → 權力、紀律"),
    ]
    for pk, strong_signs, name, desc in mahapurusha:
        if pk in planet_map:
            in_strong = _sign(pk) in strong_signs
            in_kendra = ((_sign(pk) - asc_sign) % 12) in (0, 3, 6, 9)
            present = in_strong and in_kendra
            results.append(RajaYogaHit(
                name=name,
                description_zh=desc,
                is_present=present,
                reason_zh=f"{_KEY_CN[pk]}在{_RASHI_EN_NAMES[_sign(pk)]}且為角宮"
                if present else f"{_KEY_CN[pk]}不滿足條件",
            ))

    # 4. Lakshmi Yoga: 2L and 9L strong or exchange
    lord_2 = _SIGN_LORD[(asc_sign + 1) % 12]
    if lord_2 in planet_map and lord_9 in planet_map:
        same_sign = _sign(lord_2) == _sign(lord_9)
        exchange = (_house(lord_2) == 9 and _house(lord_9) == 2)
        present = same_sign or exchange
        results.append(RajaYogaHit(
            name="Lakshmi Yoga",
            description_zh="第2宮主與第9宮主強旺或互換 → 極大財富與幸運",
            is_present=present,
            reason_zh=f"2宮主{_KEY_CN[lord_2]}與9宮主{_KEY_CN[lord_9]}同宮或互換"
            if present else "2宮主與9宮主未同宮或互換",
        ))

    # 5. Viparita Raja Yoga: 6L, 8L, 12L exchange or conjunction
    lord_6 = _SIGN_LORD[(asc_sign + 5) % 12]
    lord_8 = _SIGN_LORD[(asc_sign + 7) % 12]
    lord_12 = _SIGN_LORD[(asc_sign + 11) % 12]
    if all(k in planet_map for k in [lord_6, lord_8, lord_12]):
        s6, s8, s12 = _sign(lord_6), _sign(lord_8), _sign(lord_12)
        conj_any = (s6 == s8) or (s6 == s12) or (s8 == s12)
        results.append(RajaYogaHit(
            name="Viparita Raja Yoga",
            description_zh="6、8、12宮主互換或相合 → 逆境中翻身，危機後大成",
            is_present=conj_any,
            reason_zh="6/8/12宮主有同宮現象" if conj_any else "6/8/12宮主未同宮",
        ))

    # 6. Neecha Bhanga Raja Yoga: debilitated planet rescued
    for pk, info in planet_map.items():
        ucca_data = BPHS_UCCA_NEECHA.get(pk, {})
        neecha_sign_name = ucca_data.get("neecha", "")
        if not neecha_sign_name:
            continue
        neecha_idx = _RASHI_IDX.get(neecha_sign_name, -1)
        if info["sign"] != neecha_idx:
            continue
        # Planet is debilitated — check if lord of debilitation sign
        # is in a kendra or conjunct a benefic
        deb_lord = _SIGN_LORD[neecha_idx]
        if deb_lord in planet_map:
            deb_lord_sign = _sign(deb_lord)
            in_kendra = ((deb_lord_sign - asc_sign) % 12) in (0, 3, 6, 9)
            if in_kendra:
                results.append(RajaYogaHit(
                    name="Neecha Bhanga Raja Yoga",
                    description_zh=f"落陷行星{_KEY_CN.get(pk, pk)}被{_KEY_CN.get(deb_lord, deb_lord)}救起 → 逆轉大富大貴",
                    is_present=True,
                    reason_zh=f"{_KEY_CN.get(pk, pk)}落陷在{neecha_sign_name}，而{neecha_sign_name}主{_KEY_CN.get(deb_lord, deb_lord)}在角宮",
                ))

    # 7. Mahabhagya Yoga: all of Sun, Moon, Asc in same gender signs
    if "sun" in planet_map and "moon" in planet_map:
        sun_sign = _sign("sun")
        moon_sign = _sign("moon")
        # Sign indices 0,2,4,6,8,10 (Aries,Gemini,Leo,Libra,Sagittarius,Aquarius) = masculine
        # Sign indices 1,3,5,7,9,11 (Taurus,Cancer,Virgo,Scorpio,Capricorn,Pisces) = feminine
        sun_masc = sun_sign % 2 == 0
        moon_masc = moon_sign % 2 == 0
        asc_masc = asc_sign % 2 == 0
        all_masc = sun_masc and moon_masc and asc_masc
        all_fem = (not sun_masc) and (not moon_masc) and (not asc_masc)
        present = all_masc or all_fem
        results.append(RajaYogaHit(
            name="Mahabhagya Yoga",
            description_zh="日/月/上升皆在陽性星座(或皆在陰性) → 大富大貴、名聲遠播",
            is_present=present,
            reason_zh="太陽、月亮、上升皆在同性星座" if present
            else "太陽、月亮、上升不全在同性星座",
        ))

    return results
