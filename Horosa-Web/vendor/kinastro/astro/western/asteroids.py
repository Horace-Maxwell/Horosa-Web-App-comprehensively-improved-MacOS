"""
astro/asteroids.py — 小行星與半人馬天體位置計算
(Asteroid & Centaur Positions)

Supports: Chiron, Black Moon Lilith (mean & true), main-belt asteroids
(Ceres, Pallas, Juno, Vesta), romance asteroids (Eros, Psyche),
health/healing asteroid (Hygiea), dwarf planets (Eris),
and popular centaurs/TNOs (Pholus, Nessus, Chariklo, Ixion, Varuna,
Quaoar, Sedna).

Design principles:
- Config-driven: add new bodies by appending to ASTEROID_CONFIG.
- Heliocentric option via swe.FLG_HELCTR flag.
- Returns rich AsteroidPosition dataclass compatible with the
  existing planet-table rendering.
"""
import swisseph as swe
from dataclasses import dataclass

ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# ── Body ID helpers ─────────────────────────────────────────────────────────
# Built-in Swiss Ephemeris pseudo-planet IDs
_CHIRON_ID  = swe.CHIRON  if hasattr(swe, "CHIRON")   else 15
_PHOLUS_ID  = swe.PHOLUS  if hasattr(swe, "PHOLUS")   else 16
_MEAN_LILITH_ID = swe.MEAN_APOG if hasattr(swe, "MEAN_APOG") else 12
_TRUE_LILITH_ID = swe.OSCU_APOG if hasattr(swe, "OSCU_APOG") else 13

# Minor-planet asteroid numbers (MPC catalogue)
_AST = swe.AST_OFFSET  # 10000

# ── Master body catalogue ────────────────────────────────────────────────────
# Each entry: (display_name, swe_id, symbol, cn_name, group, meaning_en, meaning_cn)
ASTEROID_CONFIG = [
    # — Chiron & Pholus (built-in SE ids) ——————————————————————————————
    ("Chiron",       _CHIRON_ID,           "⚷", "凱龍星",  "centaur",
     "Healing, wound, teaching",       "療癒、傷口、教導"),
    ("Pholus",       _PHOLUS_ID,           "🜲", "福魯斯",  "centaur",
     "Sudden release, transformation", "突發釋放、轉化"),

    # — Black Moon Lilith ——————————————————————————————————————————————
    ("Lilith (Mean)",  _MEAN_LILITH_ID,    "⚸", "黑月麗莉絲（平均）", "lilith",
     "Shadow self, raw instinct (mean apogee)",      "暗影自我、原始本能（平均遠地點）"),
    ("Lilith (True)",  _TRUE_LILITH_ID,    "⚸", "黑月麗莉絲（振盪）", "lilith",
     "Shadow self, raw instinct (osculating apogee)", "暗影自我、原始本能（振盪遠地點）"),

    # — Main-belt asteroids (MPC numbers) ——————————————————————————————
    ("Ceres",        _AST + 1,            "⚳", "穀神星", "main_belt",
     "Nurturing, harvest, loss",       "養育、收穫、失去"),
    ("Pallas",       _AST + 2,            "⚴", "智神星", "main_belt",
     "Wisdom, strategy, craft",        "智慧、策略、技藝"),
    ("Juno",         _AST + 3,            "⚵", "婚神星", "main_belt",
     "Partnership, commitment",        "合夥、承諾"),
    ("Vesta",        _AST + 4,            "⚶", "灶神星", "main_belt",
     "Devotion, sacred flame, focus",  "奉獻、聖火、專注"),
    ("Hygiea",       _AST + 10,           "⚕", "健康神星", "main_belt",
     "Health, healing, hygiene, prevention", "健康、療癒、預防"),

    # — Romance asteroids ——————————————————————————————————————————————
    ("Eros",         _AST + 433,          "♡", "愛神星",  "romance",
     "Erotic desire, passionate attraction, obsession", "愛慾、熱情吸引、癡迷"),
    ("Psyche",       _AST + 16,           "🦋", "賽姬星",  "romance",
     "Soul, psyche, unconditional love, spiritual bond", "靈魂、無條件的愛、靈性連結"),

    # — Dwarf planets ——————————————————————————————————————————————————
    ("Eris",         _AST + 136199,       "⊗", "鬩神星",  "dwarf_planets",
     "Discord, revelation, equality, radical disruption", "不和、揭示、平等、顛覆"),

    # — Centaurs & Trans-Neptunian Objects ————————————————————————————
    ("Nessus",       _AST + 7066,         "⛎", "涅索斯",  "centaur",
     "Abuse of power, karma, cycles",  "權力濫用、業力、循環"),
    ("Chariklo",     _AST + 10199,        "⟡", "卡莉克蘿", "centaur",
     "Boundaries, grace, devotion",    "界限、優雅、奉獻"),
    ("Ixion",        _AST + 28978,        "✦", "伊克西翁", "tno",
     "Lawlessness, betrayal",          "無法無天、背叛"),
    ("Varuna",       _AST + 20000,        "♆", "伐樓拿",  "tno",
     "Natural law, cosmic order",      "自然法則、宇宙秩序"),
    ("Quaoar",       _AST + 50000,        "✧", "夸奧阿",  "tno",
     "Creative force, new patterns",   "創造力、新模式"),
    ("Sedna",        _AST + 90377,        "❄", "賽德娜",  "tno",
     "Isolation, sacrifice, evolution","孤立、犧牲、進化"),
]

# Convenience mapping: name → config tuple
ASTEROIDS = {row[0]: row for row in ASTEROID_CONFIG}

# Groups users can toggle
ASTEROID_GROUPS = {
    "chiron_pholus": ["Chiron", "Pholus"],
    "lilith":        ["Lilith (Mean)", "Lilith (True)"],
    "main_belt":     ["Ceres", "Pallas", "Juno", "Vesta", "Hygiea"],
    "romance":       ["Eros", "Psyche"],
    "centaurs":      ["Nessus", "Chariklo"],
    "tnos":          ["Ixion", "Varuna", "Quaoar", "Sedna"],
    "dwarf_planets": ["Eris"],
}


@dataclass
class AsteroidPosition:
    """Position record for one asteroid / centaur / Lilith point."""
    name: str
    name_cn: str
    symbol: str
    group: str
    longitude: float
    latitude: float
    speed: float
    sign: str
    sign_degree: float
    retrograde: bool
    heliocentric: bool
    meaning_en: str
    meaning_cn: str


def compute_asteroids(
    jd: float,
    heliocentric: bool = False,
    include_groups: list | None = None,
) -> list[AsteroidPosition]:
    """Compute positions of asteroids, centaurs, and Lilith points.

    Parameters
    ----------
    jd:
        Julian Day (UT).
    heliocentric:
        If True, compute heliocentric positions (not applicable to
        Lilith which is Earth-centric by definition; those are always
        geocentric).
    include_groups:
        List of group keys from ASTEROID_GROUPS to include.  Pass
        None (default) to include *all* bodies.

    Returns
    -------
    List of AsteroidPosition objects sorted by ecliptic longitude.
    """
    # Determine which body names to compute
    if include_groups is None:
        names_to_compute = list(ASTEROIDS.keys())
    else:
        names_to_compute = []
        for g in include_groups:
            names_to_compute.extend(ASTEROID_GROUPS.get(g, []))

    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    helio_flags = flags | swe.FLG_HELCTR

    results: list[AsteroidPosition] = []
    for name in names_to_compute:
        if name not in ASTEROIDS:
            continue
        _, swe_id, symbol, cn, group, meaning_en, meaning_cn = ASTEROIDS[name]

        # Lilith points are geocentric by definition — skip heliocentric flag
        use_helio = heliocentric and group not in ("lilith",)
        calc_flags = helio_flags if use_helio else flags

        try:
            xx, _ = swe.calc_ut(jd, swe_id, calc_flags)
            lon   = float(xx[0])
            lat   = float(xx[1])
            speed = float(xx[3]) if len(xx) > 3 else 0.0
            sign_idx = int(lon / 30) % 12
            results.append(AsteroidPosition(
                name=name, name_cn=cn, symbol=symbol, group=group,
                longitude=lon, latitude=lat, speed=speed,
                sign=ZODIAC_SIGNS[sign_idx], sign_degree=round(lon % 30, 4),
                retrograde=speed < 0,
                heliocentric=use_helio,
                meaning_en=meaning_en, meaning_cn=meaning_cn,
            ))
        except Exception:
            # Body ephemeris file may be missing for some TNOs — skip silently
            pass

    results.sort(key=lambda a: a.longitude)
    return results
