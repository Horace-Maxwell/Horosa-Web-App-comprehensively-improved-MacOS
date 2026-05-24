"""
astro/esoteric/constants.py — Alice Bailey 七道光線體系常數

資料來源：
  - Alice A. Bailey, *Esoteric Astrology* (A Treatise on the Seven Rays, Vol. III)
    (Lucis Publishing, 1951)
  - Alice A. Bailey, *A Treatise on the Seven Rays* Vol. I–V
  - Alice A. Bailey, *Esoteric Psychology* Vol. I–II

本模組所有資料嚴格依照 Alice Bailey 教導，所有靈性詮釋均帶有解釋性質，
非機械推算公式。靈魂光線的判斷需要靈性洞察，不能以單純計算取代。

All data strictly follows Alice Bailey's teachings. All spiritual
interpretations are indicative, not mechanically deterministic.
Soul Ray determination requires spiritual discernment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ============================================================
#  Seven Rays — Core Data
#  Bailey, *Esoteric Psychology* Vol. I, Chapters 1–3
# ============================================================

@dataclass(frozen=True)
class RayData:
    """
    Immutable data for one of the Seven Rays.

    Ref: Bailey, *Esoteric Astrology*, pp. 605–627 (Ray-Sign correspondences);
         *Esoteric Psychology* Vol. I, pp. 49–200 (Ray qualities).
    """
    number: int                    # 1–7
    name_en: str                   # English name
    name_zh: str                   # Chinese name
    color: str                     # Traditional Ray colour
    svg_color: str                 # SVG hex for rendering
    svg_glow: str                  # SVG glow/highlight colour
    quality_en: str                # Primary quality (EN)
    quality_zh: str                # Primary quality (ZH)
    qualities_en: List[str]        # Secondary qualities (EN)
    qualities_zh: List[str]        # Secondary qualities (ZH)
    glamour_en: str                # Chief glamour / illusion
    glamour_zh: str                # Chief glamour (ZH)
    exoteric_planets: List[str]    # Exoteric (personality-level) rulers
    esoteric_planets: List[str]    # Esoteric (soul-level) rulers
    signs: List[str]               # Signs transmitting this Ray
    soul_purpose_en: str           # Soul purpose
    soul_purpose_zh: str
    service_en: str                # Service direction
    service_zh: str


SEVEN_RAYS: Dict[int, RayData] = {
    1: RayData(
        number=1,
        name_en="Will / Power",
        name_zh="意志／力量",
        color="Red / Crimson",
        svg_color="#DC143C",
        svg_glow="#FF4466",
        quality_en="Will, Power, Strength, Courage, Detachment",
        quality_zh="意志、力量、勇氣、超然、統治力",
        qualities_en=["Leadership", "Courage", "Detachment", "Independence", "One-pointedness"],
        qualities_zh=["領導力", "勇氣", "超然", "獨立性", "專一性"],
        glamour_en="The glamour of power, isolation, and pride of separateness",
        glamour_zh="力量的幻相、孤立、分離的傲慢",
        exoteric_planets=["Pluto"],
        esoteric_planets=["Vulcan"],
        signs=["Aries", "Leo", "Capricorn"],
        soul_purpose_en="To embody Divine Will, lead through spiritual authority, and serve as a channel for the First Ray purpose in the world",
        soul_purpose_zh="體現神聖意志、以靈性權威引領，作為第一光線目的在世界中的管道",
        service_en="Leadership, governance, executive work, pioneering new directions",
        service_zh="領導、治理、行政工作、開拓新方向",
    ),
    2: RayData(
        number=2,
        name_en="Love-Wisdom",
        name_zh="愛-智慧",
        color="Blue / Indigo",
        svg_color="#1E3A8A",
        svg_glow="#3B82F6",
        quality_en="Love, Wisdom, Inclusivity, Magnetism, Intuition",
        quality_zh="愛、智慧、包容性、磁性、直覺",
        qualities_en=["Love", "Wisdom", "Intuition", "Magnetism", "Inclusiveness", "Patience"],
        qualities_zh=["愛", "智慧", "直覺", "磁性", "包容", "耐心"],
        glamour_en="The glamour of attachment, over-sensitivity, and love of being loved",
        glamour_zh="依附的幻相、過度敏感、渴望被愛",
        exoteric_planets=["Jupiter", "Sun"],
        esoteric_planets=["Jupiter"],
        signs=["Gemini", "Virgo", "Pisces"],
        soul_purpose_en="To express universal love-wisdom, teach truth, build bridges of understanding",
        soul_purpose_zh="表達宇宙愛-智慧，傳授真理，建立理解的橋梁",
        service_en="Teaching, healing, counselling, building inclusive communities",
        service_zh="教學、療癒、諮詢、建立包容性社群",
    ),
    3: RayData(
        number=3,
        name_en="Active Intelligence",
        name_zh="主動智性",
        color="Yellow / Green",
        svg_color="#92400E",
        svg_glow="#F59E0B",
        quality_en="Intelligence, Adaptability, Abstract Thought, Economy",
        quality_zh="智性、適應性、抽象思維、節約",
        qualities_en=["Intelligence", "Adaptability", "Strategy", "Economy", "Versatility"],
        qualities_zh=["智性", "適應性", "策略", "節儉", "多才多藝"],
        glamour_en="The glamour of over-activity, manipulation, and over-emphasis on material forms",
        glamour_zh="過度活躍的幻相、操弄、對物質形式的過度強調",
        exoteric_planets=["Saturn", "Earth"],
        esoteric_planets=["Saturn"],
        signs=["Cancer", "Libra", "Capricorn"],
        soul_purpose_en="To manifest divine intelligence through creative activity and wise use of matter",
        soul_purpose_zh="通過創造性活動和對物質的明智使用來顯化神聖智性",
        service_en="Philosophy, finance, strategy, science of manifestation, creative intelligence",
        service_zh="哲學、金融、策略、顯化科學、創造性智性",
    ),
    4: RayData(
        number=4,
        name_en="Harmony through Conflict",
        name_zh="透過衝突達成和諧",
        color="Yellow / Green",
        svg_color="#166534",
        svg_glow="#4ADE80",
        quality_en="Harmony, Beauty, Art, Unity through struggle",
        quality_zh="和諧、美、藝術、透過掙扎達成統一",
        qualities_en=["Harmony", "Beauty", "Art", "Intuition", "Mediation", "Struggle→Synthesis"],
        qualities_zh=["和諧", "美", "藝術", "直覺", "調解", "掙扎→綜合"],
        glamour_en="The glamour of conflict for its own sake, drama, and excessive emotionalism",
        glamour_zh="為衝突而衝突的幻相、戲劇性、過度情緒化",
        exoteric_planets=["Moon", "Mercury"],
        esoteric_planets=["Mercury"],
        signs=["Taurus", "Scorpio", "Sagittarius"],
        soul_purpose_en="To achieve synthesis through the resolution of opposites, bringing beauty and harmony into manifestation",
        soul_purpose_zh="透過解決對立面達成綜合，將美麗與和諧帶入顯化",
        service_en="Art, music, mediation, conflict resolution, creative reconciliation of opposites",
        service_zh="藝術、音樂、調解、衝突解決、對立面的創造性和解",
    ),
    5: RayData(
        number=5,
        name_en="Concrete Science / Knowledge",
        name_zh="具體科學／知識",
        color="Orange / Yellow",
        svg_color="#9A3412",
        svg_glow="#FB923C",
        quality_en="Concrete Knowledge, Science, Research, Analysis",
        quality_zh="具體知識、科學、研究、分析",
        qualities_en=["Accuracy", "Analysis", "Research", "Separation of truth from illusion", "Scientific mind"],
        qualities_zh=["精確性", "分析", "研究", "從幻相中辨析真相", "科學思維"],
        glamour_en="The glamour of materialistic intellectualism and of living in the lower concrete mind",
        glamour_zh="唯物主義智識主義的幻相，囿於低層具體心智",
        exoteric_planets=["Venus"],
        esoteric_planets=["Venus"],
        signs=["Leo", "Sagittarius", "Aquarius"],
        soul_purpose_en="To reveal the light of knowledge and to prove the existence of the soul through scientific investigation",
        soul_purpose_zh="透過科學研究揭示知識之光，證明靈魂的存在",
        service_en="Science, research, technology, education, revelation of esoteric truths through outer forms",
        service_zh="科學、研究、技術、教育、透過外在形式揭示秘傳真理",
    ),
    6: RayData(
        number=6,
        name_en="Devotion / Idealism",
        name_zh="奉獻／理想主義",
        color="Indigo / Rose",
        svg_color="#581C87",
        svg_glow="#A855F7",
        quality_en="Devotion, Idealism, Dedication, One-pointedness",
        quality_zh="奉獻、理想主義、獻身、專一",
        qualities_en=["Devotion", "Idealism", "Loyalty", "Fervour", "Spirituality"],
        qualities_zh=["奉獻", "理想主義", "忠誠", "熱忱", "靈性"],
        glamour_en="The glamour of devotion to a person, cause, or ideal rather than to universal truth",
        glamour_zh="對某人、某事業或某理想的奉獻幻相，而非對宇宙真理的奉獻",
        exoteric_planets=["Mars", "Neptune"],
        esoteric_planets=["Neptune"],
        signs=["Virgo", "Sagittarius", "Pisces"],
        soul_purpose_en="To become a channel for divine devotion, idealism, and one-pointed aspiration toward the Divine",
        soul_purpose_zh="成為神聖奉獻、理想主義和對神聖的專一渴望的管道",
        service_en="Religion, devotion, healing through prayer, inspired idealism, mystical service",
        service_zh="宗教、奉獻、透過祈禱療癒、受啟發的理想主義、神秘服務",
    ),
    7: RayData(
        number=7,
        name_en="Ceremonial Order / Magic",
        name_zh="典禮秩序／魔法",
        color="Violet / Purple",
        svg_color="#4C1D95",
        svg_glow="#8B5CF6",
        quality_en="Order, Ceremony, Magic, Ritual, Organization",
        quality_zh="秩序、典禮、魔法、儀式、組織",
        qualities_en=["Order", "Ceremony", "White Magic", "Organization", "Grace", "Precision"],
        qualities_zh=["秩序", "典禮", "白魔法", "組織", "優雅", "精確"],
        glamour_en="The glamour of magical work for self-glorification and the manipulation of matter",
        glamour_zh="為自我榮耀而施展魔法的幻相，以及對物質的操弄",
        exoteric_planets=["Uranus"],
        esoteric_planets=["Uranus"],
        signs=["Aries", "Cancer", "Capricorn"],
        soul_purpose_en="To bring spirit and matter into alignment through ceremony, ritual and the science of invocation",
        soul_purpose_zh="透過典禮、儀式和召喚科學，將靈性與物質帶入一致",
        service_en="Ceremonial work, organization, ritual, bringing divine pattern into manifestation",
        service_zh="典禮工作、組織、儀式、將神聖模式帶入顯化",
    ),
}


# ============================================================
#  Esoteric Rulers — Complete Table
#  Bailey, *Esoteric Astrology*, Chapter III
#  "The Rays, Constellations and Planets"
# ============================================================

@dataclass(frozen=True)
class SignRulers:
    """
    Rulers for one zodiac sign at three levels:
      exoteric  — Personality level (traditional Western ruler)
      esoteric  — Soul level (Bailey's esoteric ruler)
      hierarchical — Monad/Spirit level (Bailey's hierarchical ruler)

    Ref: Bailey, *Esoteric Astrology*, p. 50 (Table of Rulers),
         and Chapter III throughout.
    """
    sign: str
    exoteric: str
    esoteric: str
    hierarchical: str
    rays_transmitted: List[int]       # Ray numbers transmitted by this sign
    quality_zh: str
    quality_en: str


SIGN_RULERS: Dict[str, SignRulers] = {
    "Aries": SignRulers(
        sign="Aries", exoteric="Mars", esoteric="Mercury", hierarchical="Uranus",
        rays_transmitted=[1, 7],
        quality_zh="先驅、新起點、意志表達",
        quality_en="Pioneering, new beginnings, will expression",
    ),
    "Taurus": SignRulers(
        sign="Taurus", exoteric="Venus", esoteric="Vulcan", hierarchical="Vulcan",
        rays_transmitted=[4],
        quality_zh="物質顯化、慾望轉化、覺悟",
        quality_en="Manifestation, desire transmutation, illumination",
    ),
    "Gemini": SignRulers(
        sign="Gemini", exoteric="Mercury", esoteric="Venus", hierarchical="Earth",
        rays_transmitted=[2],
        quality_zh="二元性、橋梁、愛-智慧之道",
        quality_en="Duality, bridging, the Path of Love-Wisdom",
    ),
    "Cancer": SignRulers(
        sign="Cancer", exoteric="Moon", esoteric="Neptune", hierarchical="Neptune",
        rays_transmitted=[3, 7],
        quality_zh="孕育、形式建構、群體意識",
        quality_en="Gestation, form-building, mass consciousness",
    ),
    "Leo": SignRulers(
        sign="Leo", exoteric="Sun", esoteric="Sun", hierarchical="Sun",
        rays_transmitted=[1, 5],
        quality_zh="個體化、自我表達、靈魂意志",
        quality_en="Individualization, self-expression, soul will",
    ),
    "Virgo": SignRulers(
        sign="Virgo", exoteric="Mercury", esoteric="Moon (veiling Vulcan)", hierarchical="Jupiter",
        rays_transmitted=[2, 6],
        quality_zh="孕育基督意識、服務、純化",
        quality_en="Gestation of the Christ principle, service, purification",
    ),
    "Libra": SignRulers(
        sign="Libra", exoteric="Venus", esoteric="Uranus", hierarchical="Saturn",
        rays_transmitted=[3],
        quality_zh="均衡、選擇、因果平衡",
        quality_en="Balance, choice, karmic equilibrium",
    ),
    "Scorpio": SignRulers(
        sign="Scorpio", exoteric="Mars (Pluto)", esoteric="Mars", hierarchical="Mercury",
        rays_transmitted=[4],
        quality_zh="考驗、轉化、死亡與重生",
        quality_en="Trial, transformation, death and rebirth",
    ),
    "Sagittarius": SignRulers(
        sign="Sagittarius", exoteric="Jupiter", esoteric="Earth", hierarchical="Mars",
        rays_transmitted=[4, 5, 6],
        quality_zh="方向、目的、靈性探索",
        quality_en="Direction, purpose, spiritual quest",
    ),
    "Capricorn": SignRulers(
        sign="Capricorn", exoteric="Saturn", esoteric="Saturn", hierarchical="Venus",
        rays_transmitted=[1, 3, 7],
        quality_zh="啟蒙、高峰體驗、靈性進化頂點",
        quality_en="Initiation, peak experience, apex of spiritual evolution",
    ),
    "Aquarius": SignRulers(
        sign="Aquarius", exoteric="Uranus (Saturn)", esoteric="Jupiter", hierarchical="Moon (veiling Uranus)",
        rays_transmitted=[5],
        quality_zh="群體意識、新紀元服務、兄弟情誼",
        quality_en="Group consciousness, New Age service, brotherhood",
    ),
    "Pisces": SignRulers(
        sign="Pisces", exoteric="Jupiter (Neptune)", esoteric="Pluto", hierarchical="Pluto",
        rays_transmitted=[2, 6],
        quality_zh="救贖、溶解、世界救主",
        quality_en="Redemption, dissolution, World Saviour",
    ),
}


# ============================================================
#  Planet → Ray Mapping
#  Bailey, *Esoteric Astrology*, pp. 13–14, 605–627
# ============================================================

#: Each planet transmits one or more Rays
PLANET_RAY_MAP: Dict[str, List[int]] = {
    "Sun":     [2],        # Veils Vulcan (Ray 1) or Neptune (Ray 6) or Uranus (Ray 7)
    "Moon":    [4],        # Veils Vulcan, Neptune, Uranus at soul level
    "Mercury": [4],        # Ray 4 — Harmony through Conflict (major); also Ray 1
    "Venus":   [5],        # Ray 5 — Concrete Science
    "Mars":    [6],        # Ray 6 — Devotion/Idealism
    "Jupiter": [2],        # Ray 2 — Love-Wisdom
    "Saturn":  [3],        # Ray 3 — Active Intelligence
    "Uranus":  [7],        # Ray 7 — Ceremonial Order
    "Neptune": [6],        # Ray 6 — Devotion/Idealism (also Ray 2 esoteric)
    "Pluto":   [1],        # Ray 1 — Will/Power
    "Vulcan":  [1],        # Ray 1 — Will/Power (esoteric planet)
    "Earth":   [3],        # Ray 3 (also Ray 2 esoteric)
    "ASC":     [],         # Ascendant — depends on sign
    "MC":      [],         # Midheaven — depends on sign
}

# Esoteric planet names & symbols
ESOTERIC_PLANET_NAMES: Dict[str, str] = {
    "Sun":     "Sun ☉",
    "Moon":    "Moon ☽",
    "Mercury": "Mercury ☿",
    "Venus":   "Venus ♀",
    "Mars":    "Mars ♂",
    "Jupiter": "Jupiter ♃",
    "Saturn":  "Saturn ♄",
    "Uranus":  "Uranus ♅",
    "Neptune": "Neptune ♆",
    "Pluto":   "Pluto ♇",
    "Vulcan":  "Vulcan ⚡",
    "Earth":   "Earth ⊕",
}

# Signs in order (Western tropical)
ZODIAC_SIGNS: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_ZH: Dict[str, str] = {
    "Aries":       "牡羊座",
    "Taurus":      "金牛座",
    "Gemini":      "雙子座",
    "Cancer":      "巨蟹座",
    "Leo":         "獅子座",
    "Virgo":       "處女座",
    "Libra":       "天秤座",
    "Scorpio":     "天蠍座",
    "Sagittarius": "射手座",
    "Capricorn":   "摩羯座",
    "Aquarius":    "水瓶座",
    "Pisces":      "雙魚座",
}

SIGN_EN_ABBR: Dict[str, str] = {
    "Aries": "Ari", "Taurus": "Tau", "Gemini": "Gem", "Cancer": "Can",
    "Leo": "Leo", "Virgo": "Vir", "Libra": "Lib", "Scorpio": "Sco",
    "Sagittarius": "Sag", "Capricorn": "Cap", "Aquarius": "Aqu", "Pisces": "Pis",
}

# ============================================================
#  Ray Quality Keywords — for scoring
# ============================================================

#: Keywords associated with each Ray number in chart factors
RAY_KEYWORDS: Dict[int, List[str]] = {
    1: ["will", "power", "authority", "leadership", "courage", "detachment", "isolation"],
    2: ["love", "wisdom", "teaching", "intuition", "magnetism", "inclusiveness"],
    3: ["intelligence", "adaptability", "strategy", "economy", "versatility", "creativity"],
    4: ["harmony", "beauty", "art", "conflict", "intuition", "mediation"],
    5: ["science", "analysis", "research", "knowledge", "accuracy"],
    6: ["devotion", "idealism", "loyalty", "fervour", "aspiration"],
    7: ["order", "ceremony", "magic", "organisation", "ritual", "precision"],
}

# ============================================================
#  Interaction descriptions
# ============================================================

RAY_INTERACTION: Dict[Tuple[int, int], Dict[str, str]] = {
    (1, 2): {
        "zh": "意志力量與愛-智慧的相遇——第一光線的推動力因第二光線的愛與包容而得到深化，靈魂以智慧的愛引導意志的表達。",
        "en": "Meeting of Will-Power and Love-Wisdom — Ray 1 drive is deepened by Ray 2 love and inclusiveness, the soul guides will through wise love.",
        "type": "complementary",
    },
    (1, 3): {
        "zh": "意志與主動智性的結合——強大的執行力與策略性智慧的整合，需防止過度操控或純粹功利主義。",
        "en": "Will meets Active Intelligence — powerful executive force united with strategic thinking; beware excessive manipulation or pure pragmatism.",
        "type": "complementary",
    },
    (1, 4): {
        "zh": "意志與和諧的張力——此生存在深刻衝突：征服與和解的掙扎。靈魂課題是透過衝突達成真正的和諧。",
        "en": "Tension between Will and Harmony — deep conflict between conquest and reconciliation; the soul lesson is achieving true harmony through conflict.",
        "type": "tension",
    },
    (1, 5): {
        "zh": "意志與知識的結合——強大的智識探索能力，以意志力推動科學研究；注意不要以知識作為控制他人的工具。",
        "en": "Will united with Knowledge — powerful intellectual exploration driven by will; beware using knowledge as a tool of control.",
        "type": "complementary",
    },
    (1, 6): {
        "zh": "意志與奉獻的對峙——最具挑戰性的組合之一：個人意志與理想主義奉獻之間的衝突。整合之道在於將意志奉獻於崇高理想。",
        "en": "Will versus Devotion — one of the most challenging combinations: conflict between personal will and idealistic dedication. Integration: consecrate will to higher ideals.",
        "type": "tension",
    },
    (1, 7): {
        "zh": "意志與秩序的整合——組織魔法與靈性意志的強大結合，適合帶領儀式性或行政性服務工作。",
        "en": "Will and Order in integration — powerful combination of organizational magic with spiritual will, suited for ceremonial or executive service.",
        "type": "complementary",
    },
    (2, 3): {
        "zh": "愛-智慧與主動智性——智識服務的理想組合：以愛表達的智慧，以及在服務中靈活運用智性。",
        "en": "Love-Wisdom with Active Intelligence — ideal for intellectual service: wisdom expressed through love, intelligence applied in service.",
        "type": "complementary",
    },
    (2, 4): {
        "zh": "愛-智慧與和諧——深刻的美感與慈悲的愛的結合，天生的療癒者與藝術家；需防過度情緒化。",
        "en": "Love-Wisdom with Harmony — deep aesthetic sense combined with compassionate love; natural healers and artists; beware excessive emotionalism.",
        "type": "complementary",
    },
    (2, 5): {
        "zh": "愛-智慧與知識——靈性科學家或哲學型教師的典型組合，以愛的動機推動知識探索。",
        "en": "Love-Wisdom with Knowledge — typical of spiritual scientists or philosophical teachers, knowledge exploration motivated by love.",
        "type": "complementary",
    },
    (2, 6): {
        "zh": "愛-智慧與奉獻——神秘主義者或靈性教師的組合：以理想化的愛服務神聖；需防偏執的奉獻或依附。",
        "en": "Love-Wisdom with Devotion — the mystic or spiritual teacher: serving the Divine through idealized love; beware fanatical devotion or attachment.",
        "type": "complementary",
    },
    (2, 7): {
        "zh": "愛-智慧與秩序——以愛引導儀式與組織，適合建立療癒社群或靈性組織。",
        "en": "Love-Wisdom with Order — love guiding ritual and organization; suited for building healing communities or spiritual organizations.",
        "type": "complementary",
    },
    (3, 4): {
        "zh": "主動智性與和諧的衝突——理性頭腦與藝術直覺的緊張，靈魂課題是在具體活動中創造美麗形式。",
        "en": "Active Intelligence in tension with Harmony — conflict between rational mind and artistic intuition; soul lesson: creating beautiful forms through concrete activity.",
        "type": "tension",
    },
    (3, 5): {
        "zh": "主動智性與具體科學——理性智識的最強組合，天生的科學家、哲學家或策略家。",
        "en": "Active Intelligence with Concrete Science — strongest rational-intellectual combination; natural scientists, philosophers, or strategists.",
        "type": "complementary",
    },
    (3, 6): {
        "zh": "智性與奉獻的矛盾——此生在理性分析與情感奉獻之間存在緊張，整合之道是以理想奉獻激勵智性活動。",
        "en": "Intellect versus Devotion — tension between rational analysis and emotional dedication; integration: inspired idealism motivating intellectual activity.",
        "type": "tension",
    },
    (3, 7): {
        "zh": "主動智性與秩序魔法——在具體世界中顯化神聖秩序的能力，組織與管理的天賦。",
        "en": "Active Intelligence with Ceremonial Order — ability to manifest divine order in the concrete world; gifts in organization and management.",
        "type": "complementary",
    },
    (4, 5): {
        "zh": "和諧與知識——藝術科學的結合，通過分析和研究創造美麗；天生的美學家或藝術批評家。",
        "en": "Harmony with Knowledge — artistic science combined; creating beauty through analysis and research; natural aesthetes or art critics.",
        "type": "complementary",
    },
    (4, 6): {
        "zh": "和諧與奉獻——最富感情色彩的組合：熱情的藝術家或宗教奉獻者；需防戲劇化與情緒波動。",
        "en": "Harmony with Devotion — most emotionally intense combination: passionate artists or devoted mystics; beware drama and emotional volatility.",
        "type": "tension",
    },
    (4, 7): {
        "zh": "和諧與秩序——美麗儀式的創造者，在典禮藝術中表達靈性；天生的舞台設計師或典禮主持。",
        "en": "Harmony with Order — creators of beautiful ritual; expressing spirit through ceremonial art; natural stage designers or ceremony officiants.",
        "type": "complementary",
    },
    (5, 6): {
        "zh": "知識與奉獻的極端——理性科學與神秘信仰的對立，整合之道是以靈性理想激勵科學探索。",
        "en": "Knowledge versus Devotion — opposition of rational science and mystical faith; integration: spiritual idealism inspiring scientific exploration.",
        "type": "tension",
    },
    (5, 7): {
        "zh": "具體科學與秩序——精密科學與組織管理的結合，精確而有條理的研究者。",
        "en": "Concrete Science with Order — precise science combined with organized management; methodical and precise researchers.",
        "type": "complementary",
    },
    (6, 7): {
        "zh": "奉獻與秩序——透過儀式表達靈性奉獻，宗教禮儀的實踐者或靈性組織的創建者。",
        "en": "Devotion with Order — expressing spiritual devotion through ritual; practitioners of religious liturgy or founders of spiritual organizations.",
        "type": "complementary",
    },
}


def get_ray_interaction(ray_a: int, ray_b: int) -> Optional[Dict[str, str]]:
    """Return interaction description for a pair of Rays."""
    key = (min(ray_a, ray_b), max(ray_a, ray_b))
    return RAY_INTERACTION.get(key)


# ============================================================
#  Sign → Ray mapping
# ============================================================

def get_sign_rays(sign: str) -> List[int]:
    """Return the Rays transmitted by a zodiac sign."""
    rulers = SIGN_RULERS.get(sign)
    if rulers:
        return list(rulers.rays_transmitted)
    return []


def get_sign_from_longitude(lon: float) -> str:
    """Return the zodiac sign name for an absolute longitude."""
    idx = int(lon / 30.0) % 12
    return ZODIAC_SIGNS[idx]


def get_degree_in_sign(lon: float) -> float:
    """Return the degree within a sign (0–30°)."""
    return lon % 30.0


# ============================================================
#  Example birth data for testing
#  (Representative spiritual/historical figures)
# ============================================================

EXAMPLE_CHARTS = [
    {
        "name": "Alice A. Bailey",
        "name_zh": "愛麗絲·貝利",
        "year": 1880, "month": 6, "day": 16,
        "hour": 7, "minute": 32,
        "timezone": 0.0,
        "latitude": 53.4808, "longitude": -2.2426,
        "location_name": "Manchester, UK",
        "notes_zh": (
            "《秘傳占星》作者，新紀元靈性教師。"
            "太陽雙子座（第二光線之星座），上升水瓶座，月亮射手座。"
        ),
        "notes_en": (
            "Author of Esoteric Astrology, New Age spiritual teacher. "
            "Sun in Gemini (Ray 2 sign), Asc Aquarius, Moon Sagittarius."
        ),
    },
    {
        "name": "Helena P. Blavatsky",
        "name_zh": "海倫娜·布拉瓦茨基",
        "year": 1831, "month": 8, "day": 12,
        "hour": 2, "minute": 17,
        "timezone": 2.0,
        "latitude": 48.7450, "longitude": 37.5673,
        "location_name": "Yekaterinoslav, Ukraine",
        "notes_zh": (
            "神智學協會創始人，《神智學密義》作者。"
            "太陽獅子座（第一與第五光線），上升金牛座。"
        ),
        "notes_en": (
            "Founder of Theosophical Society, author of The Secret Doctrine. "
            "Sun in Leo (Rays 1 & 5), Asc Taurus."
        ),
    },
    {
        "name": "Mahatma Gandhi",
        "name_zh": "聖雄甘地",
        "year": 1869, "month": 10, "day": 2,
        "hour": 7, "minute": 11,
        "timezone": 5.5,
        "latitude": 21.6340, "longitude": 69.6090,
        "location_name": "Porbandar, India",
        "notes_zh": (
            "印度獨立運動精神領袖，非暴力（Ahimsa）踐行者。"
            "太陽天秤座（第三光線），上升天蠍座，月亮巨蟹座。"
        ),
        "notes_en": (
            "Spiritual leader of India's independence movement, practitioner of Ahimsa. "
            "Sun in Libra (Ray 3), Asc Scorpio, Moon Cancer."
        ),
    },
]
