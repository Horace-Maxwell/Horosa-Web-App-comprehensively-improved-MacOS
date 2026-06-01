"""
astro/astronomical_geomancy/geomancy_figures.py
══════════════════════════════════════════════════════════════
Canonical 16-figure data module for Astronomical Geomancy.

Provides:
  - FIGURE_SVG_ROWS  : per-figure SVG dot geometry (derived from FIGURES constants)
  - FIGURE_CATALOG   : bilingual labels, wiki anchors, astrological correspondences,
                       and omen texts for all 16 geomantic figures

No streamlit imports at module level (per CONTRIBUTING.md convention).
"""

from __future__ import annotations

from typing import Dict, List

from .constants import FIGURES

# ─────────────────────────────────────────────────────────────────────────────
# SVG geometry — dot positions within a CELL_W × CELL_H bounding box
# ─────────────────────────────────────────────────────────────────────────────

CELL_W: int = 72    # logical width of the figure bounding cell
CELL_H: int = 72    # logical height of the figure bounding cell

# Y-centres of the 4 dot rows (top = row 0)
ROW_Y: List[int] = [12, 26, 44, 58]

# X positions for single (odd) and double (even) rows
X_SINGLE: List[int] = [36]        # one dot, centred
X_DOUBLE: List[int] = [24, 48]    # two dots, symmetric


# ─────────────────────────────────────────────────────────────────────────────
# Build FIGURE_SVG_ROWS from FIGURES constants (single source of truth)
# ─────────────────────────────────────────────────────────────────────────────

def _build_figure_svg_rows() -> Dict[str, Dict]:
    """Return {name_en: {rows_y, rows_x}} for all 16 geomantic figures."""
    out: Dict[str, Dict] = {}
    for _key, data in FIGURES.items():
        name = data["name_en"]
        rows_x: List[List[int]] = []
        for single in data["dots"]:
            rows_x.append(list(X_SINGLE) if single else list(X_DOUBLE))
        out[name] = {
            "rows_y": list(ROW_Y),
            "rows_x": rows_x,
        }
    return out


FIGURE_SVG_ROWS: Dict[str, Dict] = _build_figure_svg_rows()

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE_CATALOG — bilingual labels, omen texts, wiki anchors
# ─────────────────────────────────────────────────────────────────────────────

_WIKI_BASE = "/wiki/systems/astronomical_geomancy"

FIGURE_CATALOG: Dict[str, Dict] = {
    "Acquisitio": {
        "zh": "得益（聚財）",
        "latin": "Acquisitio",
        "en_short": "Gain",
        "wiki": f"{_WIKI_BASE}#acquisitio",
        "astrology_zh": "白羊座 ♈ · 木星 ♃",
        "astrology_en": "Aries ♈ · Jupiter ♃",
        "omen_zh": "大吉。一切求之皆得，財富滋長，事業有成。如木星高照，萬物豐收。",
        "omen_en": "Very fortunate. All that is sought shall be gained; wealth grows and career succeeds, as Jupiter bestows abundance.",
    },
    "Laetitia": {
        "zh": "喜悅",
        "latin": "Laetitia",
        "en_short": "Joy",
        "wiki": f"{_WIKI_BASE}#laetitia",
        "astrology_zh": "金牛座 ♉ · 木星 ♃",
        "astrology_en": "Taurus ♉ · Jupiter ♃",
        "omen_zh": "吉。喜事連連，心情愉快，福祉充裕。春花盛放，吉人天相。",
        "omen_en": "Fortunate. Joyful events, uplifted spirits, abundant wellbeing — spring blossoms under Jupiter's grace.",
    },
    "Puer": {
        "zh": "男孩（陽剛）",
        "latin": "Puer",
        "en_short": "Boy",
        "wiki": f"{_WIKI_BASE}#puer",
        "astrology_zh": "雙子座 ♊ · 火星 ♂",
        "astrology_en": "Gemini ♊ · Mars ♂",
        "omen_zh": "中。衝動行事，宜謀定後動；利戰不利和。如烈火方起，勇則傷身。",
        "omen_en": "Mixed. Impulsive action — plan before striking. Favors conflict over peace; like a young warrior, courage without wisdom brings wounds.",
    },
    "Rubeus": {
        "zh": "赤紅",
        "latin": "Rubeus",
        "en_short": "Red",
        "wiki": f"{_WIKI_BASE}#rubeus",
        "astrology_zh": "雙子座 ♊ · 火星 ♂",
        "astrology_en": "Gemini ♊ · Mars ♂",
        "omen_zh": "凶。危險、憤怒與衝突；血光之兆，萬事宜緩。",
        "omen_en": "Unfortunate. Danger, anger, conflict — omen of bloodshed; all matters counsel delay.",
    },
    "Albus": {
        "zh": "白色（純淨）",
        "latin": "Albus",
        "en_short": "White",
        "wiki": f"{_WIKI_BASE}#albus",
        "astrology_zh": "巨蟹座 ♋ · 水星 ☿",
        "astrology_en": "Cancer ♋ · Mercury ☿",
        "omen_zh": "吉。智慧清明，商業有利，思考透徹。如皓月當空，萬象清晰。",
        "omen_en": "Fortunate. Clear wisdom, favourable for commerce, keen and lucid thought — like the full moon revealing all.",
    },
    "Via": {
        "zh": "道路",
        "latin": "Via",
        "en_short": "Road",
        "wiki": f"{_WIKI_BASE}#via",
        "astrology_zh": "獅子座 ♌ · 月亮 ☽",
        "astrology_en": "Leo ♌ · Moon ☽",
        "omen_zh": "中。流動變化，旅行吉，定局凶。如大道通衢，行者不滯。",
        "omen_en": "Neutral. Fluid change — good for journeys, ill for fixed matters; the wanderer finds no walls on the open road.",
    },
    "Conjunctio": {
        "zh": "合相（連接）",
        "latin": "Conjunctio",
        "en_short": "Conjunction",
        "wiki": f"{_WIKI_BASE}#conjunctio",
        "astrology_zh": "處女座 ♍ · 水星 ☿",
        "astrology_en": "Virgo ♍ · Mercury ☿",
        "omen_zh": "中。聯合與相遇；結果視伴侶性質而定，善者增善，惡者增惡。",
        "omen_en": "Mixed. Union and meeting — outcome mirrors the companion's nature; good amplifies good, ill amplifies ill.",
    },
    "Caput Draconis": {
        "zh": "龍頭（北交點）",
        "latin": "Caput Draconis",
        "en_short": "Dragon's Head",
        "wiki": f"{_WIKI_BASE}#caput-draconis",
        "astrology_zh": "處女座 ♍ · 龍頭 ☊",
        "astrology_en": "Virgo ♍ · North Node ☊",
        "omen_zh": "吉。上升力量，良好開端，入世有利。如龍首昂揚，諸事肇始。",
        "omen_en": "Fortunate. Rising power, auspicious beginnings, worldly gain — the Dragon's Head ascends, initiating all things.",
    },
    "Puella": {
        "zh": "女孩（陰柔）",
        "latin": "Puella",
        "en_short": "Girl",
        "wiki": f"{_WIKI_BASE}#puella",
        "astrology_zh": "天秤座 ♎ · 金星 ♀",
        "astrology_en": "Libra ♎ · Venus ♀",
        "omen_zh": "吉。美麗、愛情與和諧；適於感情婚姻，金星垂愛。",
        "omen_en": "Fortunate. Beauty, love, harmony — excellent for romance and marriage, blessed by Venus.",
    },
    "Amissio": {
        "zh": "失去",
        "latin": "Amissio",
        "en_short": "Loss",
        "wiki": f"{_WIKI_BASE}#amissio",
        "astrology_zh": "天蠍座 ♏ · 金星 ♀",
        "astrology_en": "Scorpio ♏ · Venus ♀",
        "omen_zh": "凶。財物散失，感情受損；保留現有勝於追求新得。",
        "omen_en": "Unfortunate. Loss of wealth and affection — hold fast to what you have rather than grasping after more.",
    },
    "Tristitia": {
        "zh": "悲傷",
        "latin": "Tristitia",
        "en_short": "Sorrow",
        "wiki": f"{_WIKI_BASE}#tristitia",
        "astrology_zh": "天蠍座 ♏ · 土星 ♄",
        "astrology_en": "Scorpio ♏ · Saturn ♄",
        "omen_zh": "凶。悲傷、困頓與延遲；土星重壓，萬事不順。",
        "omen_en": "Unfortunate. Sorrow, hardship, delay — Saturn presses down; matters go awry.",
    },
    "Cauda Draconis": {
        "zh": "龍尾（南交點）",
        "latin": "Cauda Draconis",
        "en_short": "Dragon's Tail",
        "wiki": f"{_WIKI_BASE}#cauda-draconis",
        "astrology_zh": "射手座 ♐ · 龍尾 ☋",
        "astrology_en": "Sagittarius ♐ · South Node ☋",
        "omen_zh": "凶。下降消散，業力清算；適於結束，不宜開始。",
        "omen_en": "Unfortunate. Descending dissipation, karmic reckoning — suited for endings, not new ventures.",
    },
    "Populus": {
        "zh": "民眾（群體）",
        "latin": "Populus",
        "en_short": "People",
        "wiki": f"{_WIKI_BASE}#populus",
        "astrology_zh": "摩羯座 ♑ · 月亮 ☽",
        "astrology_en": "Capricorn ♑ · Moon ☽",
        "omen_zh": "中。群眾力量，隨波逐流；因環境而異，善地則善，惡地則惡。",
        "omen_en": "Neutral. Collective force, going with the flow — outcome shifts with context; good ground bears good fruit.",
    },
    "Fortuna Major": {
        "zh": "大吉（大福運）",
        "latin": "Fortuna Major",
        "en_short": "Greater Fortune",
        "wiki": f"{_WIKI_BASE}#fortuna-major",
        "astrology_zh": "水瓶座 ♒ · 太陽 ☉",
        "astrology_en": "Aquarius ♒ · Sun ☉",
        "omen_zh": "大吉。內在力量強大，榮耀加冕，萬事如意。如君王登基，四方臣服。",
        "omen_en": "Very fortunate. Inner strength crowned with honour — all things favour; like a king ascending the throne, all bow before.",
    },
    "Fortuna Minor": {
        "zh": "小吉（小福運）",
        "latin": "Fortuna Minor",
        "en_short": "Lesser Fortune",
        "wiki": f"{_WIKI_BASE}#fortuna-minor",
        "astrology_zh": "獅子座 ♌ · 太陽 ☉",
        "astrology_en": "Leo ♌ · Sun ☉",
        "omen_zh": "小吉。短暫好運，外部援助；謹防好景不常，須自立自強。",
        "omen_en": "Minor fortune. Brief luck, aid from without — guard against impermanence; self-reliance endures longer than borrowed fortune.",
    },
    "Carcer": {
        "zh": "監獄（囚困）",
        "latin": "Carcer",
        "en_short": "Prison",
        "wiki": f"{_WIKI_BASE}#carcer",
        "astrology_zh": "雙魚座 ♓ · 土星 ♄",
        "astrology_en": "Pisces ♓ · Saturn ♄",
        "omen_zh": "凶。囚困阻礙，動彈不得；宜靜待時機，強行則碰壁。",
        "omen_en": "Unfortunate. Imprisonment, obstruction, inability to move — wait patiently for the opportune moment; forcing the matter brings only harder walls.",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Public accessor functions
# ─────────────────────────────────────────────────────────────────────────────

def get_figure_svg_rows() -> Dict[str, Dict]:
    """Return the pre-built SVG row specs for all 16 geomantic figures."""
    return FIGURE_SVG_ROWS


def get_figure_catalog() -> Dict[str, Dict]:
    """Return the full bilingual figure catalog."""
    return FIGURE_CATALOG
