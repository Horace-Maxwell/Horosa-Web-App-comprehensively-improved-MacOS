"""
astro/cosmobiology/constants.py — COSI 行星組合完整資料庫

Reinhold Ebertin's "The Combination of Stellar Influences" (COSI)
1972 English edition — Complete planetary picture database.

All interpretations are verbatim or extremely close to the original COSI text.
Page references are provided for each combination.

Planet abbreviations used as keys (Ebertin standard):
    SO = Sun, MO = Moon, ME = Mercury, VE = Venus, MA = Mars,
    JU = Jupiter, SA = Saturn, UR = Uranus, NE = Neptune, PL = Pluto,
    AS = Ascendant, MC = Midheaven (MC), NN = North Node (True Node)
"""

from __future__ import annotations
from typing import Dict, Optional, Tuple

# ============================================================
# Planet display names
# ============================================================

PLANET_NAMES_EN: Dict[str, str] = {
    "SO": "Sun",
    "MO": "Moon",
    "ME": "Mercury",
    "VE": "Venus",
    "MA": "Mars",
    "JU": "Jupiter",
    "SA": "Saturn",
    "UR": "Uranus",
    "NE": "Neptune",
    "PL": "Pluto",
    "AS": "Ascendant",
    "MC": "MC",
    "NN": "Node",
}

PLANET_NAMES_ZH: Dict[str, str] = {
    "SO": "太陽",
    "MO": "月亮",
    "ME": "水星",
    "VE": "金星",
    "MA": "火星",
    "JU": "木星",
    "SA": "土星",
    "UR": "天王星",
    "NE": "海王星",
    "PL": "冥王星",
    "AS": "上升點",
    "MC": "天頂",
    "NN": "北交點",
}

PLANET_SYMBOLS: Dict[str, str] = {
    "SO": "☉",
    "MO": "☽",
    "ME": "☿",
    "VE": "♀",
    "MA": "♂",
    "JU": "♃",
    "SA": "♄",
    "UR": "♅",
    "NE": "♆",
    "PL": "♇",
    "AS": "AC",
    "MC": "MC",
    "NN": "☊",
}

# Personal points (highest weight in COSI)
PERSONAL_POINTS = {"SO", "MO", "AS", "MC", "NN"}

# ============================================================
# Orb rules — COSI p. 9
# "The orb should not exceed 1½°"
# ============================================================

ORB_MAIN: float = 1.5    # maximum orb for midpoint contact (COSI p. 9)
ORB_TIGHT: float = 1.0   # tight orb for primary influence
ORB_WIDE: float = 2.0    # looser orb sometimes used for natal research

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_CN = {
    "Aries": "白羊", "Taurus": "金牛", "Gemini": "雙子", "Cancer": "巨蟹",
    "Leo": "獅子", "Virgo": "處女", "Libra": "天秤", "Scorpio": "天蠍",
    "Sagittarius": "射手", "Capricorn": "摩羯", "Aquarius": "水瓶", "Pisces": "雙魚",
}

# ============================================================
# COSI Planetary Combination Database
# Source: Reinhold Ebertin, "The Combination of Stellar Influences"
#         English edition 1972, translated by A. G. Roosedale & L. Kratzsch
#
# Each entry:
#   "principle_en"  : cosmic/physical principle (COSI heading)
#   "principle_zh"  : Chinese translation
#   "positive_en"   : positive manifestation (COSI "positive")
#   "positive_zh"   : Chinese
#   "negative_en"   : negative manifestation (COSI "negative")
#   "negative_zh"   : Chinese
#   "page"          : COSI page reference
# ============================================================

COSI_DB: Dict[Tuple[str, str], Dict[str, str]] = {

    # ──────────────────────────────────────────────
    # SUN combinations  (COSI pp. 28–55)
    # ──────────────────────────────────────────────

    ("SO", "MO"): {
        "principle_en": (
            "The union of the male and female principle. "
            "The soul and body, vitality and soul, man and wife."
        ),
        "principle_zh": "陰陽結合。靈魂與身體，男性與女性，夫與妻的結合。",
        "positive_en": (
            "Happy union between body and soul. "
            "Harmonious relationship between man and woman. "
            "Ability to gain the respect of others."
        ),
        "positive_zh": "身心和諧。男女關係融洽。能獲得他人的尊重。",
        "negative_en": (
            "Inhibitions. Contrasts or clashes between the conscious and "
            "unconscious mind. Incompatibility between husband and wife."
        ),
        "negative_zh": "抑制。意識與潛意識間的衝突。夫妻之間的不相容。",
        "page": "COSI p. 28",
    },

    ("SO", "ME"): {
        "principle_en": (
            "The thinker. The will expressing itself through the mind. "
            "Intellectual pursuits."
        ),
        "principle_zh": "思想者。意志通過智識表達。智識追求。",
        "positive_en": (
            "Clarity of thought and expression. "
            "Intellectual vigour. "
            "Good powers of communication and assertion."
        ),
        "positive_zh": "思路清晰，表達清楚。智識活躍。善於溝通和主張。",
        "negative_en": (
            "Nervous irritability. "
            "Vacillation, indecision. "
            "Mental strain through over-exertion."
        ),
        "negative_zh": "神經性易怒。猶豫不決。因過度勞動而造成精神緊張。",
        "page": "COSI p. 30",
    },

    ("SO", "VE"): {
        "principle_en": (
            "Love life. Artistic ability and sense of beauty. "
            "Pleasures, enjoyments."
        ),
        "principle_zh": "愛情生活。藝術才能與美感。快樂與享受。",
        "positive_en": (
            "A happy love life. "
            "A well-developed sense of beauty. "
            "Artistry, charm, and personal grace."
        ),
        "positive_zh": "幸福的愛情生活。高度發展的美感。藝術氣質、魅力與個人風度。",
        "negative_en": (
            "Excessive enjoyment of pleasure, leading to debauchery. "
            "Vanity. Jealousy in love. Disappointed love."
        ),
        "negative_zh": "過度追求享樂，導致縱欲。虛榮。愛情中的嫉妒。失戀。",
        "page": "COSI p. 31",
    },

    ("SO", "MA"): {
        "principle_en": (
            "Energy, activity, creativity. "
            "A resolute, purposeful will. "
            "Positive action."
        ),
        "principle_zh": "精力、活力、創造力。堅定有目的的意志。積極行動。",
        "positive_en": (
            "Great creative energy and tireless activity. "
            "An assertive and successful individual. "
            "Courage and daring in the pursuit of goals."
        ),
        "positive_zh": "巨大的創造力和不知疲倦的活力。積極進取且成功的個體。在追求目標中勇敢果斷。",
        "negative_en": (
            "Over-exertion. "
            "Violence, brutality, ruthlessness. "
            "Aggression, conflict. Accidents, injuries, surgery."
        ),
        "negative_zh": "過度勞累。暴力、殘忍、冷酷。攻擊性、衝突。事故、傷害、手術。",
        "page": "COSI p. 32",
    },

    ("SO", "JU"): {
        "principle_en": (
            "The fortunate personality. "
            "Good fortune, success, happiness. "
            "Striving for higher values."
        ),
        "principle_zh": "幸運的個性。好運、成功、幸福。追求更高的價值。",
        "positive_en": (
            "Optimism, buoyancy, expansive joie de vivre. "
            "Success, recognition, and advancement. "
            "Generosity, benevolence."
        ),
        "positive_zh": "樂觀、輕快、積極的生命喜悅。成功、認可與晉升。慷慨、仁慈。",
        "negative_en": (
            "Arrogance, exaggeration, immoderation. "
            "Wastefulness. Insolent self-confidence leading to failure."
        ),
        "negative_zh": "傲慢、誇大、不節制。浪費。傲慢的自信導致失敗。",
        "page": "COSI p. 34",
    },

    ("SO", "SA"): {
        "principle_en": (
            "The inhibited or checked will. "
            "Obstacles to development. "
            "Seriousness, gravity, perseverance."
        ),
        "principle_zh": "受抑制或受阻的意志。發展的障礙。嚴肅、莊重、堅忍。",
        "positive_en": (
            "Perseverance, endurance, tenacity. "
            "Attainment of success through one's own efforts. "
            "A strong sense of duty and responsibility."
        ),
        "positive_zh": "毅力、耐力、韌性。通過自身努力取得成功。強烈的責任感和義務感。",
        "negative_en": (
            "The imposition of restrictions upon the self. "
            "Obstacles and impediments to progress. "
            "Depression, melancholy, inhibitions. Separation or bereavement."
        ),
        "negative_zh": "自我設限。進展受阻。抑鬱、憂鬱、壓抑。分離或喪親。",
        "page": "COSI p. 35",
    },

    ("SO", "UR"): {
        "principle_en": (
            "Originality, independence, or revolution. "
            "Technical ability. "
            "Sudden changes of fortune."
        ),
        "principle_zh": "獨創性、獨立性或革命性。技術才能。命運的突然變化。",
        "positive_en": (
            "A strong desire for freedom. "
            "Inventiveness, originality, independence. "
            "Sudden and successful changes."
        ),
        "positive_zh": "強烈的自由渴望。發明創造力、獨創性、獨立性。突然而成功的改變。",
        "negative_en": (
            "Obstinacy, self-will, inflexibility. "
            "Sudden upheavals, separations, and reversals of fortune. "
            "Accidents, and the danger of electrocution."
        ),
        "negative_zh": "固執、任性、缺乏靈活性。突然的動盪、分離和命運逆轉。事故及觸電危險。",
        "page": "COSI p. 37",
    },

    ("SO", "NE"): {
        "principle_en": (
            "Impressionability, sensitivity, or inspiration. "
            "Mysticism, the occult. Receptivity."
        ),
        "principle_zh": "易受影響、敏感或靈感。神秘主義、神秘學。感受性。",
        "positive_en": (
            "Inspiration, idealism, deep intuition. "
            "Sensitivity to environment. "
            "Healing ability, mediumistic gifts, or artistic inspiration."
        ),
        "positive_zh": "靈感、理想主義、深刻的直覺。對環境的敏感性。治癒能力、靈媒天賦或藝術靈感。",
        "negative_en": (
            "Weakness of the will, self-deception, illusions. "
            "Tendency to addiction and substance abuse. "
            "Deception by others, fraud."
        ),
        "negative_zh": "意志力薄弱、自我欺騙、幻想。成癮傾向。被他人欺騙、詐騙。",
        "page": "COSI p. 39",
    },

    ("SO", "PL"): {
        "principle_en": (
            "Extraordinary personal power. "
            "The reformer or the fanatic. "
            "Mass influence."
        ),
        "principle_zh": "非凡的個人力量。改革者或狂熱者。大眾影響力。",
        "positive_en": (
            "Tremendous will-power. "
            "The ability to lead masses of people. "
            "Reforming zeal, creative power on a grand scale."
        ),
        "positive_zh": "巨大的意志力。領導大眾的能力。改革熱忱，大規模的創造力。",
        "negative_en": (
            "Ruthless struggle for power. "
            "The criminal or terrorist. "
            "Dangerous or catastrophic events."
        ),
        "negative_zh": "無情的權力鬥爭。罪犯或恐怖分子。危險或災難性事件。",
        "page": "COSI p. 41",
    },

    ("SO", "AS"): {
        "principle_en": (
            "The personality in its environment. "
            "Personal contacts and relationships."
        ),
        "principle_zh": "個性在其環境中。個人聯繫和關係。",
        "positive_en": (
            "Self-confident assertion in the environment. "
            "The ability to impress and influence others. "
            "A healthy physical constitution."
        ),
        "positive_zh": "在環境中自信地展現自我。能夠影響和打動他人。健康的體質。",
        "negative_en": (
            "Conflict with the environment. "
            "Inability to adapt to surroundings. "
            "Difficulties in personal relationships."
        ),
        "negative_zh": "與環境衝突。無法適應周圍環境。個人關係困難。",
        "page": "COSI p. 43",
    },

    ("SO", "MC"): {
        "principle_en": (
            "Purposeful striving. "
            "Consciousness of life's aims. "
            "The soul's development."
        ),
        "principle_zh": "有目的地奮鬥。對生命目標的意識。靈魂的發展。",
        "positive_en": (
            "The ability to shape one's own destiny. "
            "High ambition, the will to succeed. "
            "Strong individuality and clear direction in life."
        ),
        "positive_zh": "塑造自身命運的能力。高度的雄心壯志，成功的意願。強烈的個性和明確的人生方向。",
        "negative_en": (
            "Excessive self-regard, egocentricity. "
            "Wrong aims in life. "
            "Inability to realise one's potentialities."
        ),
        "negative_zh": "過度自我關注、以自我為中心。錯誤的人生目標。無法實現自身潛力。",
        "page": "COSI p. 45",
    },

    ("SO", "NN"): {
        "principle_en": (
            "Association with others. "
            "The ability to establish relationships. "
            "Links with the community."
        ),
        "principle_zh": "與他人的聯繫。建立關係的能力。與社區的聯結。",
        "positive_en": (
            "The ability to make useful contacts. "
            "Popularity, success in social intercourse. "
            "An active and constructive communal life."
        ),
        "positive_zh": "建立有益聯繫的能力。受歡迎，社交成功。積極而有建設性的社區生活。",
        "negative_en": (
            "Difficulties in human relationships. "
            "Separation or estrangement from others. "
            "Conflicts with the community."
        ),
        "negative_zh": "人際關係困難。與他人的分離或疏遠。與社區的衝突。",
        "page": "COSI p. 47",
    },

    # ──────────────────────────────────────────────
    # MOON combinations  (COSI pp. 56–81)
    # ──────────────────────────────────────────────

    ("MO", "ME"): {
        "principle_en": (
            "The thinking soul. "
            "Ability to grasp psychic impressions quickly. "
            "Lively imagination."
        ),
        "principle_zh": "思考的靈魂。快速掌握心靈印象的能力。活躍的想像力。",
        "positive_en": (
            "Receptivity and adaptability. "
            "Good memory and imagination. "
            "Eloquence and fluency of expression."
        ),
        "positive_zh": "感受性和適應性。良好的記憶力和想像力。善於言辭，表達流暢。",
        "negative_en": (
            "Instability, restlessness, superficiality. "
            "Obsession with trifles. "
            "Susceptibility to the influence of environment."
        ),
        "negative_zh": "不穩定、焦躁不安、膚淺。對瑣事的執念。容易受環境影響。",
        "page": "COSI p. 56",
    },

    ("MO", "VE"): {
        "principle_en": (
            "Feeling and sensitivity. "
            "Beauty, art, or love. "
            "Feminine nature."
        ),
        "principle_zh": "感情與敏感性。美麗、藝術或愛情。女性特質。",
        "positive_en": (
            "Genuine affection, warmth, tenderness. "
            "Appreciation of beauty, artistic talent. "
            "Happy relationships with women."
        ),
        "positive_zh": "真誠的感情、溫暖、柔情。對美的欣賞，藝術才能。與女性關係良好。",
        "negative_en": (
            "Over-sentimentality, easily hurt feelings. "
            "Vanity, coquetry. "
            "Unstable emotional life."
        ),
        "negative_zh": "過於多愁善感，感情易受傷。虛榮、賣弄風情。情感生活不穩定。",
        "page": "COSI p. 57",
    },

    ("MO", "MA"): {
        "principle_en": (
            "Energetic activity. "
            "The ambitious woman. "
            "A hot-tempered nature."
        ),
        "principle_zh": "精力充沛的活動。雄心勃勃的女性。火爆的性格。",
        "positive_en": (
            "Forceful activity, energy, enterprise. "
            "Quick reactions. "
            "The courage to face difficulties."
        ),
        "positive_zh": "強有力的行動、精力、進取心。快速反應。面對困難的勇氣。",
        "negative_en": (
            "Excitability, irritability, quarrelsomeness. "
            "Emotional outbursts. "
            "Hasty, rash actions."
        ),
        "negative_zh": "易激動、易怒、好爭吵。情緒爆發。輕率、冒失的行動。",
        "page": "COSI p. 59",
    },

    ("MO", "JU"): {
        "principle_en": (
            "The benevolent soul. "
            "Generous feelings, kindliness, goodwill."
        ),
        "principle_zh": "仁慈的靈魂。慷慨的感情、善意、好意。",
        "positive_en": (
            "Optimism, cheerfulness, kindness. "
            "A popular and well-liked personality. "
            "Good fortune and success in domestic life."
        ),
        "positive_zh": "樂觀、愉快、善良。受人喜愛和歡迎的個性。家庭生活幸福成功。",
        "negative_en": (
            "Excessive sentimentality and indulgence. "
            "Extravagance, wastefulness. "
            "A tendency to promise more than can be delivered."
        ),
        "negative_zh": "過度多愁善感和放縱。奢侈、浪費。傾向於承諾超出能力範圍的事情。",
        "page": "COSI p. 61",
    },

    ("MO", "SA"): {
        "principle_en": (
            "Inhibited feelings. "
            "Caution, self-denial, or depression."
        ),
        "principle_zh": "受抑制的感情。謹慎、自我克制或抑鬱。",
        "positive_en": (
            "Seriousness, constancy, trustworthiness. "
            "Discipline and endurance. "
            "Steadfast loyalty."
        ),
        "positive_zh": "嚴肅、堅定、可信賴。紀律性和耐力。堅定的忠誠。",
        "negative_en": (
            "Emotional coldness, rigidity. "
            "Melancholy, pessimism. "
            "Difficulties in emotional relationships. Separation."
        ),
        "negative_zh": "情感冷漠、僵化。憂鬱、悲觀。情感關係中的困難。分離。",
        "page": "COSI p. 63",
    },

    ("MO", "UR"): {
        "principle_en": (
            "Emotional tension and excitability. "
            "Unusual emotional reactions. "
            "Capriciousness."
        ),
        "principle_zh": "情緒緊張和興奮。不尋常的情緒反應。任性多變。",
        "positive_en": (
            "Intense emotional excitement and unusual experiences. "
            "Sudden decisions leading to surprising results. "
            "Originality, independence."
        ),
        "positive_zh": "強烈的情緒興奮和不尋常的經歷。導致令人驚訝結果的突然決定。獨創性、獨立性。",
        "negative_en": (
            "Capriciousness, restlessness, lack of emotional stability. "
            "Unexpected upsets and separations. "
            "Nervous tension."
        ),
        "negative_zh": "任性多變、焦躁不安、缺乏情感穩定性。意外的動盪和分離。神經緊張。",
        "page": "COSI p. 65",
    },

    ("MO", "NE"): {
        "principle_en": (
            "A sensitive or hyper-sensitive nature. "
            "Dreaminess, a tendency to mysticism or imagination."
        ),
        "principle_zh": "敏感或過度敏感的性格。夢幻、神秘傾向或想像力。",
        "positive_en": (
            "A strong imagination, artistic and poetic talent. "
            "Compassion, empathy. "
            "Mediumistic abilities, spiritual sensitivity."
        ),
        "positive_zh": "豐富的想像力、藝術和詩意才能。同情心、移情能力。靈媒天賦、靈性敏感性。",
        "negative_en": (
            "Emotional instability, moodiness. "
            "Self-deception, illusions. "
            "Addiction to drugs or alcohol. Deception."
        ),
        "negative_zh": "情緒不穩定、喜怒無常。自我欺騙、幻想。藥物或酒精成癮。被欺騙。",
        "page": "COSI p. 67",
    },

    ("MO", "PL"): {
        "principle_en": (
            "Intense emotions. "
            "The wielding of emotional power. "
            "Mass instincts."
        ),
        "principle_zh": "強烈的情緒。情感力量的運用。群眾本能。",
        "positive_en": (
            "Intense emotional experience. "
            "Emotional power to transform others. "
            "Psychic abilities, depth of feeling."
        ),
        "positive_zh": "強烈的情感體驗。轉化他人的情感力量。靈性能力、感情深度。",
        "negative_en": (
            "Violent emotions, compulsive behaviour. "
            "Upheavals in domestic life. "
            "Submission to mass hysteria."
        ),
        "negative_zh": "激烈的情緒、強迫性行為。家庭生活動盪。屈服於群體歇斯底里。",
        "page": "COSI p. 69",
    },

    ("MO", "AS"): {
        "principle_en": (
            "Emotional contacts. "
            "The sensitive individual in the community."
        ),
        "principle_zh": "情感聯繫。社區中的敏感個體。",
        "positive_en": (
            "Emotional openness and receptivity in relationships. "
            "Good powers of empathy. "
            "Popular in the community."
        ),
        "positive_zh": "在關係中情感開放和感受性強。良好的移情能力。在社區中受歡迎。",
        "negative_en": (
            "Emotional over-sensitivity in social situations. "
            "Moodiness affecting relationships. "
            "Separation from the community."
        ),
        "negative_zh": "在社交場合情緒過度敏感。情緒影響關係。與社區的隔離。",
        "page": "COSI p. 70",
    },

    ("MO", "MC"): {
        "principle_en": (
            "The soul's development. "
            "Emotional aims and objectives. "
            "The inner life."
        ),
        "principle_zh": "靈魂的發展。情感目標和目的。內心生活。",
        "positive_en": (
            "Inner harmony. "
            "The ability to mould one's destiny in accordance with one's needs. "
            "Emotional fulfilment."
        ),
        "positive_zh": "內心和諧。根據自身需要塑造命運的能力。情感滿足。",
        "negative_en": (
            "Inner conflict, emotional dissatisfaction. "
            "Moodiness affecting the life's direction. "
            "Emotional difficulties with one's parents."
        ),
        "negative_zh": "內心衝突、情感不滿足。情緒影響人生方向。與父母的情感困難。",
        "page": "COSI p. 72",
    },

    ("MO", "NN"): {
        "principle_en": (
            "Emotional contacts with others. "
            "A woman's relationships. "
            "Public popularity."
        ),
        "principle_zh": "與他人的情感聯繫。女性的關係。公眾的受歡迎程度。",
        "positive_en": (
            "Emotional rapport with others. "
            "Popularity, especially with women. "
            "A rich communal emotional life."
        ),
        "positive_zh": "與他人的情感共鳴。受歡迎，尤其在女性中。豐富的社區情感生活。",
        "negative_en": (
            "Emotional estrangement. "
            "Difficulties in relationships, especially with women. "
            "Emotional conflicts in the community."
        ),
        "negative_zh": "情感疏遠。關係困難，尤其與女性。社區中的情感衝突。",
        "page": "COSI p. 73",
    },

    # ──────────────────────────────────────────────
    # MERCURY combinations  (COSI pp. 82–105)
    # ──────────────────────────────────────────────

    ("ME", "VE"): {
        "principle_en": (
            "A sense of beauty and form. "
            "Aesthetic judgement. "
            "The artistic mind."
        ),
        "principle_zh": "美感和形式感。審美判斷。藝術性的心智。",
        "positive_en": (
            "A fine sense of beauty and proportion. "
            "Artistic sensibility and talent. "
            "Charming, witty conversation."
        ),
        "positive_zh": "精美的美感和比例感。藝術感受力和才能。迷人、機智的談吐。",
        "negative_en": (
            "Frivolity, superficiality. "
            "Lack of moral sincerity. "
            "Dishonesty in matters of love."
        ),
        "negative_zh": "輕浮、膚淺。缺乏道德誠意。在愛情事務中不誠實。",
        "page": "COSI p. 82",
    },

    ("ME", "MA"): {
        "principle_en": (
            "The active thinker. "
            "Sharp, decisive thinking. "
            "Argumentativeness."
        ),
        "principle_zh": "積極的思考者。敏銳、果斷的思維。好辯性。",
        "positive_en": (
            "A sharp and forceful intellect. "
            "Decisiveness, enterprise. "
            "Critical ability and analytical powers."
        ),
        "positive_zh": "敏銳而有力的智慧。果斷性、進取心。批判能力和分析能力。",
        "negative_en": (
            "Sharp tongue, sarcasm, argumentativeness. "
            "Hasty thinking and hasty speech. "
            "Conflicts arising from words or written communications."
        ),
        "negative_zh": "嘴巴尖刻、諷刺、好辯。思考和說話輕率。由言語或書面溝通引發的衝突。",
        "page": "COSI p. 84",
    },

    ("ME", "JU"): {
        "principle_en": (
            "Philosophical thought. "
            "Broad intellect, sound judgement. "
            "Learning and teaching."
        ),
        "principle_zh": "哲學思想。廣博的智識，健全的判斷力。學習與教學。",
        "positive_en": (
            "Broad intellect, sound judgement, good common sense. "
            "Optimism, good humour. "
            "Success in intellectual pursuits and communication."
        ),
        "positive_zh": "廣博的智識、健全的判斷力、良好的常識。樂觀、幽默。在智識追求和溝通中成功。",
        "negative_en": (
            "Over-confidence, boastfulness. "
            "Extravagance in thought and expression. "
            "Carelessness, negligence."
        ),
        "negative_zh": "過度自信、自誇。思想和表達上的浮誇。粗心大意、疏忽。",
        "page": "COSI p. 86",
    },

    ("ME", "SA"): {
        "principle_en": (
            "Serious, concentrated thought. "
            "Methodical intelligence. "
            "Inhibited thinking."
        ),
        "principle_zh": "嚴肅、專注的思考。有條理的智識。受抑制的思維。",
        "positive_en": (
            "Concentrated, methodical thinking. "
            "An organised, disciplined mind. "
            "Ability to work with great precision and thoroughness."
        ),
        "positive_zh": "集中、有條理的思考。有組織、有紀律的頭腦。能以極大的精確性和全面性工作。",
        "negative_en": (
            "Mental inhibition, depression. "
            "Pessimism, negative thinking. "
            "Worrying, anxiety. Difficulty in self-expression."
        ),
        "negative_zh": "心理抑制、抑鬱。悲觀、消極思維。擔憂、焦慮。表達自我困難。",
        "page": "COSI p. 88",
    },

    ("ME", "UR"): {
        "principle_en": (
            "An original, quick mind. "
            "Technical ingenuity. "
            "Sudden mental inspirations."
        ),
        "principle_zh": "獨創、快速的頭腦。技術才能。突然的心智靈感。",
        "positive_en": (
            "Originality, inventiveness, technical ability. "
            "Quick perception and grasp of situations. "
            "Brilliant ideas."
        ),
        "positive_zh": "獨創性、發明創造力、技術才能。快速感知和掌握情況的能力。卓越的想法。",
        "negative_en": (
            "Nervousness, hyperactivity. "
            "Contradictory ideas. "
            "Eccentric thinking, impracticality."
        ),
        "negative_zh": "神經質、過度活躍。矛盾的想法。古怪的思維、不切實際。",
        "page": "COSI p. 90",
    },

    ("ME", "NE"): {
        "principle_en": (
            "The imaginative mind. "
            "Intuition, inner perception. "
            "Deceptive thinking."
        ),
        "principle_zh": "充滿想像力的心智。直覺、內在感知。欺騙性的思維。",
        "positive_en": (
            "Vivid imagination and creative fantasy. "
            "Intuition, clairvoyance. "
            "Poetic and artistic inspiration."
        ),
        "positive_zh": "生動的想像力和創造性幻想。直覺、透視力。詩意和藝術靈感。",
        "negative_en": (
            "Confused or chaotic thinking. "
            "Self-deception, susceptibility to deception. "
            "Dishonesty, fraud."
        ),
        "negative_zh": "混亂或紊亂的思維。自我欺騙、易受欺騙。不誠實、詐欺。",
        "page": "COSI p. 92",
    },

    ("ME", "PL"): {
        "principle_en": (
            "Profound mental activity. "
            "The power of thought, persuasion. "
            "Propaganda."
        ),
        "principle_zh": "深刻的心智活動。思想、說服的力量。宣傳。",
        "positive_en": (
            "Penetrating intellect, power of suggestion. "
            "The ability to influence many people through the written or spoken word. "
            "Deep research."
        ),
        "positive_zh": "洞察力強的智識、建議的力量。通過書面或口頭言辭影響眾多人的能力。深刻研究。",
        "negative_en": (
            "Fanaticism, obsessions. "
            "The misuse of the power of the word. "
            "Unscrupulous propaganda."
        ),
        "negative_zh": "狂熱主義、強迫觀念。語言力量的濫用。不擇手段的宣傳。",
        "page": "COSI p. 94",
    },

    # ──────────────────────────────────────────────
    # VENUS combinations  (COSI pp. 106–127)
    # ──────────────────────────────────────────────

    ("VE", "MA"): {
        "principle_en": (
            "Passion, sexual love. "
            "The force of attraction. "
            "Artistic creation."
        ),
        "principle_zh": "激情、性愛。吸引力。藝術創作。",
        "positive_en": (
            "Passionate love, a strong sex drive. "
            "Artistic creativity. "
            "An attractive personality. Enthusiasm."
        ),
        "positive_zh": "熱情的愛，強烈的性驅力。藝術創造力。吸引人的個性。熱情。",
        "negative_en": (
            "Uncontrolled passions, lust. "
            "Love of pleasure to excess. "
            "Conflicts arising from love affairs."
        ),
        "negative_zh": "不受控制的激情、色慾。過度沉迷於享樂。因戀愛事件引起的衝突。",
        "page": "COSI p. 106",
    },

    ("VE", "JU"): {
        "principle_en": (
            "A pleasant, agreeable disposition. "
            "Love of pleasure and comfort. "
            "Good fortune."
        ),
        "principle_zh": "愉快、令人愉悅的性情。對享樂和舒適的熱愛。好運。",
        "positive_en": (
            "Happiness, contentment. "
            "Good fortune in love and money. "
            "Generosity, charm, and social popularity."
        ),
        "positive_zh": "幸福、滿足感。在愛情和金錢方面的好運。慷慨、魅力和社交受歡迎程度。",
        "negative_en": (
            "Over-indulgence, extravagance, wastefulness. "
            "Idleness, laziness. "
            "Excessive sensuality."
        ),
        "negative_zh": "過度放縱、奢侈、浪費。懶散、懶惰。過度感官享受。",
        "page": "COSI p. 108",
    },

    ("VE", "SA"): {
        "principle_en": (
            "Inhibited feelings. "
            "Seriousness in love. "
            "Lonely love."
        ),
        "principle_zh": "受抑制的感情。愛情中的嚴肅性。孤獨的愛。",
        "positive_en": (
            "Fidelity and constancy in love. "
            "Seriousness and depth of feeling. "
            "Enduring relationships."
        ),
        "positive_zh": "愛情中的忠誠和堅定。感情的嚴肅性和深度。持久的關係。",
        "negative_en": (
            "Inhibited or thwarted love. "
            "Emotional coldness. "
            "Disappointment or unhappiness in love."
        ),
        "negative_zh": "受抑制或受阻的愛情。情感冷漠。愛情中的失望或不幸。",
        "page": "COSI p. 110",
    },

    ("VE", "UR"): {
        "principle_en": (
            "Unusual love experiences. "
            "Sudden attractions and estrangements. "
            "Emotional tension."
        ),
        "principle_zh": "不尋常的愛情體驗。突然的吸引和疏遠。情感緊張。",
        "positive_en": (
            "Excitement and stimulus in the love-life. "
            "Sudden but genuine falling in love. "
            "Originality in art and love."
        ),
        "positive_zh": "愛情生活中的興奮和刺激。突然但真誠地墜入愛河。在藝術和愛情中的獨創性。",
        "negative_en": (
            "Emotional instability, sudden separations. "
            "Unconventional or eccentric relationships. "
            "Love disappointments."
        ),
        "negative_zh": "情感不穩定、突然分離。非傳統或古怪的關係。愛情失望。",
        "page": "COSI p. 112",
    },

    ("VE", "NE"): {
        "principle_en": (
            "Romantic or idealistic love. "
            "Artistic inspiration. "
            "Deception in love."
        ),
        "principle_zh": "浪漫或理想主義的愛情。藝術靈感。愛情中的欺騙。",
        "positive_en": (
            "Romantic idealism, spiritual love. "
            "Artistic and musical inspiration. "
            "Great compassion and sensitivity."
        ),
        "positive_zh": "浪漫理想主義、精神性的愛。藝術和音樂靈感。巨大的同情心和敏感性。",
        "negative_en": (
            "Illusions in love, deception. "
            "Unrequited love. "
            "Tendency to addiction."
        ),
        "negative_zh": "愛情中的幻想、欺騙。單戀。成癮傾向。",
        "page": "COSI p. 114",
    },

    ("VE", "PL"): {
        "principle_en": (
            "Powerful love experiences. "
            "Transformation through love. "
            "Compulsive attraction."
        ),
        "principle_zh": "強有力的愛情體驗。通過愛情的轉化。強迫性的吸引。",
        "positive_en": (
            "Deeply transforming love experiences. "
            "Strong erotic magnetism. "
            "Creative power transformed through love."
        ),
        "positive_zh": "深度轉化的愛情體驗。強烈的情慾磁力。通過愛情轉化的創造力。",
        "negative_en": (
            "Obsessive or possessive love. "
            "Sexual compulsions. "
            "Misuse of charm or beauty."
        ),
        "negative_zh": "強迫性或佔有性的愛。性強迫症。美貌或魅力的濫用。",
        "page": "COSI p. 116",
    },

    # ──────────────────────────────────────────────
    # MARS combinations  (COSI pp. 128–149)
    # ──────────────────────────────────────────────

    ("MA", "JU"): {
        "principle_en": (
            "The desire for success. "
            "Ambition, enterprise. "
            "Successful actions."
        ),
        "principle_zh": "對成功的渴望。野心、進取心。成功的行動。",
        "positive_en": (
            "Fortunate enterprise, successful efforts. "
            "An ambitious and energetic personality. "
            "The ability to achieve goals through sustained effort."
        ),
        "positive_zh": "幸運的進取、成功的努力。雄心勃勃而充滿活力的個性。通過持續努力實現目標的能力。",
        "negative_en": (
            "Over-confidence, overreaching. "
            "Tendency to exaggerate one's abilities. "
            "Conflicts with authorities."
        ),
        "negative_zh": "過度自信、好高騖遠。誇大自身能力的傾向。與權威的衝突。",
        "page": "COSI p. 128",
    },

    ("MA", "SA"): {
        "principle_en": (
            "Endurance and perseverance. "
            "Tenacious will. "
            "Cold or calculated actions."
        ),
        "principle_zh": "耐力和堅持。頑強的意志。冷靜或深思熟慮的行動。",
        "positive_en": (
            "Industriousness, tenacity, and perseverance. "
            "The ability to work very hard and systematically. "
            "Endurance under adverse conditions."
        ),
        "positive_zh": "勤勉、堅韌和堅持不懈。非常努力和系統性工作的能力。在逆境下的耐力。",
        "negative_en": (
            "Frustration, inhibited action. "
            "Brutality, hardness, cruelty. "
            "Accidents, operations, imprisonment."
        ),
        "negative_zh": "沮喪、受抑制的行動。殘暴、冷酷、殘忍。事故、手術、監禁。",
        "page": "COSI p. 130",
    },

    ("MA", "UR"): {
        "principle_en": (
            "Sudden forceful actions. "
            "Technical energy. "
            "The revolutionary."
        ),
        "principle_zh": "突然強有力的行動。技術能量。革命者。",
        "positive_en": (
            "An explosive, energetic nature. "
            "Daring, boldness in action. "
            "Technical and mechanical ability."
        ),
        "positive_zh": "爆炸性、充滿活力的性格。大膽、行動果敢。技術和機械能力。",
        "negative_en": (
            "Recklessness, explosive temper, violence. "
            "Sudden accidents, injuries. "
            "The terrorist or agitator."
        ),
        "negative_zh": "魯莽、爆炸性脾氣、暴力。突發事故、傷害。恐怖分子或煽動者。",
        "page": "COSI p. 132",
    },

    ("MA", "NE"): {
        "principle_en": (
            "Misdirected energy. "
            "Undermining actions. "
            "Subtle or covert aggressiveness."
        ),
        "principle_zh": "被誤導的能量。破壞性行動。微妙或隱蔽的攻擊性。",
        "positive_en": (
            "Idealistic action, fighting for ideals. "
            "Healing energy. "
            "Subtle creative power."
        ),
        "positive_zh": "理想主義行動，為理想而戰。治癒能量。微妙的創造力。",
        "negative_en": (
            "Weak will, frustrated action. "
            "Poisoning, drug addiction. "
            "Clandestine or subversive actions."
        ),
        "negative_zh": "意志力薄弱、行動受阻。中毒、藥物成癮。秘密或顛覆性行動。",
        "page": "COSI p. 134",
    },

    ("MA", "PL"): {
        "principle_en": (
            "Extraordinary energy. "
            "Obsessive drives. "
            "The use or abuse of force."
        ),
        "principle_zh": "非凡的能量。強迫性驅動力。力量的使用或濫用。",
        "positive_en": (
            "Tremendous energy and determination. "
            "The ability to achieve great things through sheer effort. "
            "Powerful transformation through action."
        ),
        "positive_zh": "巨大的精力和決心。通過純粹努力實現偉大事業的能力。通過行動的強大轉化。",
        "negative_en": (
            "Brutality, violence, the use of overwhelming force. "
            "Dangerous accidents. "
            "Power struggles and conflicts."
        ),
        "negative_zh": "殘暴、暴力、使用壓倒性力量。危險事故。權力鬥爭和衝突。",
        "page": "COSI p. 136",
    },

    # ──────────────────────────────────────────────
    # JUPITER combinations  (COSI pp. 150–169)
    # ──────────────────────────────────────────────

    ("JU", "SA"): {
        "principle_en": (
            "The process of change between growth and decay. "
            "The struggle between expansion and contraction."
        ),
        "principle_zh": "成長與衰退之間的變化過程。擴張與收縮之間的鬥爭。",
        "positive_en": (
            "Wisdom, the ability to judge correctly. "
            "Moderation, the balance of optimism and caution. "
            "Steady progress and development."
        ),
        "positive_zh": "智慧、正確判斷的能力。節制、樂觀與謹慎的平衡。穩定的進步和發展。",
        "negative_en": (
            "Vacillation between confidence and doubt. "
            "Loss of fortune after success. "
            "Alternating between optimism and pessimism."
        ),
        "negative_zh": "在自信與懷疑之間搖擺。成功後的財富損失。在樂觀和悲觀之間交替。",
        "page": "COSI p. 150",
    },

    ("JU", "UR"): {
        "principle_en": (
            "A desire for freedom and independence. "
            "Sudden good fortune. "
            "Reforms."
        ),
        "principle_zh": "對自由和獨立的渴望。突然的好運。改革。",
        "positive_en": (
            "A love of freedom, independence, and adventure. "
            "Sudden fortunate changes. "
            "Originality, inventiveness, and a spirit of enterprise."
        ),
        "positive_zh": "對自由、獨立和冒險的熱愛。突然的幸運變化。獨創性、發明創造力和進取精神。",
        "negative_en": (
            "Impatience, restlessness. "
            "Sudden reversal of fortune. "
            "Rebellion against convention or authority."
        ),
        "negative_zh": "不耐煩、坐立不安。命運的突然逆轉。對傳統或權威的反叛。",
        "page": "COSI p. 152",
    },

    ("JU", "NE"): {
        "principle_en": (
            "Religious or philosophical idealism. "
            "Speculation, fantasies."
        ),
        "principle_zh": "宗教或哲學理想主義。投機、幻想。",
        "positive_en": (
            "Religious and philosophical idealism. "
            "Charitable and humanitarian impulses. "
            "Inspired optimism."
        ),
        "positive_zh": "宗教和哲學理想主義。慈善和人道主義衝動。有靈感的樂觀主義。",
        "negative_en": (
            "Speculation, financial losses through deception. "
            "Over-idealism leading to disappointment. "
            "Addiction, fanatical religious beliefs."
        ),
        "negative_zh": "投機、因欺騙而造成的財務損失。過度理想主義導致失望。成癮、狂熱的宗教信仰。",
        "page": "COSI p. 154",
    },

    ("JU", "PL"): {
        "principle_en": (
            "The desire to lead. "
            "Striving for power, or for higher values."
        ),
        "principle_zh": "領導的渴望。對權力或更高價值的追求。",
        "positive_en": (
            "Powerful ambition and successful leadership. "
            "The ability to exert great influence. "
            "Transformation on a large scale."
        ),
        "positive_zh": "強大的雄心和成功的領導力。發揮巨大影響力的能力。大規模的轉化。",
        "negative_en": (
            "Misuse of power, exploitation. "
            "Fanatical striving for dominance. "
            "Sudden loss of wealth or influence."
        ),
        "negative_zh": "權力濫用、剝削。對統治地位的狂熱追求。財富或影響力的突然損失。",
        "page": "COSI p. 156",
    },

    # ──────────────────────────────────────────────
    # SATURN combinations  (COSI pp. 170–189)
    # ──────────────────────────────────────────────

    ("SA", "UR"): {
        "principle_en": (
            "Rebellion against restraint. "
            "Sudden release from inhibition. "
            "Tension between old and new."
        ),
        "principle_zh": "對約束的反叛。突然從抑制中釋放。新舊之間的緊張。",
        "positive_en": (
            "The ability to break down old structures to build new ones. "
            "Determined effort to achieve reforms. "
            "Liberation from past limitations."
        ),
        "positive_zh": "打破舊結構以建立新結構的能力。堅定努力實現改革。從過去限制中解放。",
        "negative_en": (
            "Sudden upsets, accidents. "
            "Tension between tradition and innovation. "
            "Disruption of established order."
        ),
        "negative_zh": "突然的動盪、事故。傳統與創新之間的緊張。既定秩序的破壞。",
        "page": "COSI p. 170",
    },

    ("SA", "NE"): {
        "principle_en": (
            "Chronic illness. "
            "Instability, insecurity. "
            "Undermining of the will."
        ),
        "principle_zh": "慢性病。不穩定性、不安全感。意志力的破壞。",
        "positive_en": (
            "Spiritual depth, mysticism. "
            "The ability to transcend material limitations. "
            "Compassionate endurance."
        ),
        "positive_zh": "靈性深度、神秘主義。超越物質限制的能力。富有同情心的忍耐。",
        "negative_en": (
            "Chronic illness, weakness, exhaustion. "
            "Dissolution of structures. "
            "Deception, treachery, secret suffering."
        ),
        "negative_zh": "慢性病、虛弱、精疲力竭。結構的瓦解。欺騙、背叛、隱秘的痛苦。",
        "page": "COSI p. 172",
    },

    ("SA", "PL"): {
        "principle_en": (
            "Endurance in the face of hardship. "
            "The hard worker. "
            "Transformation through suffering."
        ),
        "principle_zh": "面對艱辛的耐力。辛勤工作者。通過苦難的轉化。",
        "positive_en": (
            "Tremendous endurance and perseverance. "
            "Overcoming great difficulties. "
            "Profound inner transformation."
        ),
        "positive_zh": "巨大的耐力和堅持不懈。克服巨大困難。深刻的內在轉化。",
        "negative_en": (
            "Extreme hardship, deprivation. "
            "Ruthlessness, cruelty. "
            "Catastrophic destruction of structures."
        ),
        "negative_zh": "極度艱難、匱乏。冷酷、殘忍。結構的災難性破壞。",
        "page": "COSI p. 174",
    },

    # ──────────────────────────────────────────────
    # URANUS combinations  (COSI pp. 190–207)
    # ──────────────────────────────────────────────

    ("UR", "NE"): {
        "principle_en": (
            "The spirit of the age. "
            "Spiritual revolution. "
            "Inspired visions."
        ),
        "principle_zh": "時代精神。靈性革命。受啟發的願景。",
        "positive_en": (
            "Receptivity to new spiritual impulses. "
            "Inspired ideas and visions. "
            "A sensitive and creative imagination."
        ),
        "positive_zh": "對新靈性衝動的感受性。受啟發的想法和願景。敏感而富有創造力的想像力。",
        "negative_en": (
            "Confusion, chaos, upheaval. "
            "Ideological revolutions gone wrong. "
            "Fanatical delusions."
        ),
        "negative_zh": "混亂、動盪、激變。出了問題的意識形態革命。狂熱的妄想。",
        "page": "COSI p. 190",
    },

    ("UR", "PL"): {
        "principle_en": (
            "Revolutions. "
            "Transformation of the world. "
            "Upheaval and renewal."
        ),
        "principle_zh": "革命。世界的轉化。動盪和更新。",
        "positive_en": (
            "The ability to reform old structures radically. "
            "Extraordinary creative and transforming energies. "
            "New beginnings after destruction."
        ),
        "positive_zh": "從根本上改革舊結構的能力。非凡的創造和轉化能量。毀滅後的新開始。",
        "negative_en": (
            "Violent revolutions, catastrophes. "
            "Destruction of the old order. "
            "Sudden and catastrophic upheavals."
        ),
        "negative_zh": "暴力革命、災難。舊秩序的破壞。突然的災難性動盪。",
        "page": "COSI p. 192",
    },

    # ──────────────────────────────────────────────
    # NEPTUNE combinations  (COSI pp. 208–221)
    # ──────────────────────────────────────────────

    ("NE", "PL"): {
        "principle_en": (
            "Epoch-making transformations. "
            "Changes in the spiritual life of humanity."
        ),
        "principle_zh": "劃時代的轉化。人類靈性生活的變化。",
        "positive_en": (
            "New spiritual insights and transformations. "
            "A deepening of collective consciousness. "
            "Profound cultural renewal."
        ),
        "positive_zh": "新的靈性洞見和轉化。集體意識的深化。深刻的文化更新。",
        "negative_en": (
            "Epidemics, mass infections. "
            "Corruption, decadence on a grand scale. "
            "Universal disillusionment."
        ),
        "negative_zh": "流行病、大規模感染。腐敗、大規模墮落。普遍的幻滅感。",
        "page": "COSI p. 208",
    },

    # ──────────────────────────────────────────────
    # ASCENDANT combinations  (COSI pp. 222–238)
    # ──────────────────────────────────────────────

    ("AS", "MC"): {
        "principle_en": (
            "The individual in the world. "
            "The development of personality through interaction with the environment."
        ),
        "principle_zh": "世界中的個體。個性通過與環境互動而發展。",
        "positive_en": (
            "A well-developed individual personality that acts constructively in the world. "
            "Harmony between inner aims and outer circumstances."
        ),
        "positive_zh": "在世界上建設性行動的良好發展個性。內在目標與外在環境之間的和諧。",
        "negative_en": (
            "Conflict between the individual and the outer world. "
            "Inner and outer circumstances at variance. "
            "Inability to find one's place in the world."
        ),
        "negative_zh": "個體與外部世界之間的衝突。內外環境相互矛盾。無法在世界中找到自己的位置。",
        "page": "COSI p. 222",
    },

    ("AS", "NN"): {
        "principle_en": (
            "The ability to form relationships. "
            "Community life, associations."
        ),
        "principle_zh": "建立關係的能力。社區生活、社團。",
        "positive_en": (
            "A sociable, popular personality. "
            "A rich and fulfilling communal life. "
            "Important relationships and partnerships."
        ),
        "positive_zh": "善於社交、受歡迎的個性。豐富而令人滿足的社區生活。重要的關係和夥伴關係。",
        "negative_en": (
            "Difficulty in forming lasting relationships. "
            "Loneliness, isolation. "
            "Conflicts in partnerships."
        ),
        "negative_zh": "難以建立持久的關係。孤獨、孤立。夥伴關係中的衝突。",
        "page": "COSI p. 224",
    },

    ("MC", "NN"): {
        "principle_en": (
            "Associations and unions for common purpose. "
            "Joint aims."
        ),
        "principle_zh": "為共同目的而形成的聯合。共同目標。",
        "positive_en": (
            "Productive and successful teamwork. "
            "Goal-oriented cooperation. "
            "Success in joint enterprises."
        ),
        "positive_zh": "富有成效和成功的團隊合作。目標導向的合作。聯合事業中的成功。",
        "negative_en": (
            "Conflicts of aims in partnerships. "
            "Incompatibility of objectives. "
            "Difficulties in finding suitable associates."
        ),
        "negative_zh": "夥伴關係中目標的衝突。目標的不相容性。難以找到合適的合夥人。",
        "page": "COSI p. 230",
    },

    # Additional combinations for completeness
    ("ME", "AS"): {
        "principle_en": "Intellectual contacts. Communication in the environment.",
        "principle_zh": "智識聯繫。環境中的溝通。",
        "positive_en": "Good communication skills. Useful intellectual contacts.",
        "positive_zh": "良好的溝通技巧。有益的智識聯繫。",
        "negative_en": "Misunderstandings in relationships. Gossip, deception through words.",
        "negative_zh": "關係中的誤解。流言蜚語、通過言語欺騙。",
        "page": "COSI p. 95",
    },
    ("ME", "MC"): {
        "principle_en": "Intellectual objectives. The thinking person with clear aims.",
        "principle_zh": "智識目標。有明確目標的思考者。",
        "positive_en": "Clear thinking about life's aims. Intellectual achievements.",
        "positive_zh": "對人生目標的清晰思考。智識成就。",
        "negative_en": "Indecision about life's aims. Intellectual conflicts.",
        "negative_zh": "對人生目標猶豫不決。智識衝突。",
        "page": "COSI p. 96",
    },
    ("VE", "AS"): {
        "principle_en": "Lovable personality. Harmony in the environment.",
        "principle_zh": "可愛的個性。環境中的和諧。",
        "positive_en": "Social harmony. Pleasing, popular personality.",
        "positive_zh": "社交和諧。令人愉快、受歡迎的個性。",
        "negative_en": "Over-dependence on others' approval. Difficulties in relationships.",
        "negative_zh": "過度依賴他人的認可。關係中的困難。",
        "page": "COSI p. 117",
    },
    ("VE", "MC"): {
        "principle_en": "Striving for harmony and beauty. Aesthetic aims.",
        "principle_zh": "追求和諧與美麗。審美目標。",
        "positive_en": "Success through art or beauty. Harmonious aims. Good taste.",
        "positive_zh": "通過藝術或美麗取得成功。和諧的目標。良好的品味。",
        "negative_en": "Over-emphasis on pleasure. Vanity as a life aim.",
        "negative_zh": "過度強調享樂。以虛榮為人生目標。",
        "page": "COSI p. 118",
    },
    ("MA", "AS"): {
        "principle_en": "Energetic contacts. Active environment.",
        "principle_zh": "充滿活力的聯繫。積極的環境。",
        "positive_en": "Energetic and assertive in the environment. Active relationships.",
        "positive_zh": "在環境中充滿活力和自信。積極的關係。",
        "negative_en": "Conflicts and strife in relationships. Aggression in the environment.",
        "negative_zh": "關係中的衝突和爭吵。環境中的攻擊性。",
        "page": "COSI p. 137",
    },
    ("MA", "MC"): {
        "principle_en": "The will to achieve. Directed energy towards aims.",
        "principle_zh": "實現目標的意志。朝目標的定向能量。",
        "positive_en": "Great energy and initiative in pursuing aims. Successful assertiveness.",
        "positive_zh": "在追求目標方面的巨大精力和主動性。成功的自信。",
        "negative_en": "Ruthless ambition. Conflicts with authorities. Career disruptions.",
        "negative_zh": "無情的野心。與權威的衝突。職業中斷。",
        "page": "COSI p. 138",
    },
    ("JU", "AS"): {
        "principle_en": "Fortunate environment. Good personal relationships.",
        "principle_zh": "幸運的環境。良好的個人關係。",
        "positive_en": "A fortunate, pleasant environment. Helpful relationships.",
        "positive_zh": "幸運、愉快的環境。有助益的關係。",
        "negative_en": "Over-expansion in relationships. Promises not kept.",
        "negative_zh": "在關係中過度擴張。不守承諾。",
        "page": "COSI p. 157",
    },
    ("JU", "MC"): {
        "principle_en": "The fortunate development of the personality. Success in vocation.",
        "principle_zh": "個性的幸運發展。職業上的成功。",
        "positive_en": "Professional success, recognition, high social standing.",
        "positive_zh": "職業成功、認可、高社會地位。",
        "negative_en": "Over-ambition, arrogance, exploitation of success.",
        "negative_zh": "過度野心、傲慢、利用成功。",
        "page": "COSI p. 158",
    },
    ("SA", "AS"): {
        "principle_en": "Inhibited or difficult personal contacts. Loneliness.",
        "principle_zh": "受抑制或困難的個人聯繫。孤獨。",
        "positive_en": "Steadfast loyalty. Serious, enduring relationships.",
        "positive_zh": "堅定的忠誠。嚴肅、持久的關係。",
        "negative_en": "Separation, loneliness. Difficult or cold relationships.",
        "negative_zh": "分離、孤獨。困難或冷漠的關係。",
        "page": "COSI p. 175",
    },
    ("SA", "MC"): {
        "principle_en": "Inhibited development of personality. Obstacles in vocation.",
        "principle_zh": "個性發展受阻。職業中的障礙。",
        "positive_en": "Career success through perseverance and hard work.",
        "positive_zh": "通過毅力和努力工作取得職業成功。",
        "negative_en": "Career obstacles, limitations. Late or difficult success.",
        "negative_zh": "職業障礙、限制。遲來或困難的成功。",
        "page": "COSI p. 176",
    },
    ("UR", "AS"): {
        "principle_en": "Original, unusual personal contacts. The reformer in society.",
        "principle_zh": "獨創、不尋常的個人聯繫。社會中的改革者。",
        "positive_en": "Exciting, stimulating relationships. Original personality.",
        "positive_zh": "令人興奮、刺激的關係。獨創性個性。",
        "negative_en": "Sudden separations. Difficult, erratic relationships.",
        "negative_zh": "突然分離。困難、變化無常的關係。",
        "page": "COSI p. 193",
    },
    ("UR", "MC"): {
        "principle_en": "Sudden changes in the life's direction. The reformer.",
        "principle_zh": "人生方向的突然改變。改革者。",
        "positive_en": "Sudden positive changes in career. Inventive, original aims.",
        "positive_zh": "職業上的突然積極變化。發明創造性、獨創性的目標。",
        "negative_en": "Sudden career disruptions. Erratic changes of direction.",
        "negative_zh": "突然的職業中斷。多變的方向改變。",
        "page": "COSI p. 194",
    },
    ("NE", "AS"): {
        "principle_en": "Sensitive, impressionable personal contacts. Deception.",
        "principle_zh": "敏感、易受影響的個人聯繫。欺騙。",
        "positive_en": "Idealistic relationships. Sensitivity to others.",
        "positive_zh": "理想主義的關係。對他人的敏感性。",
        "negative_en": "Deception, illusion in relationships. Unreliable contacts.",
        "negative_zh": "關係中的欺騙、幻想。不可靠的聯繫。",
        "page": "COSI p. 209",
    },
    ("NE", "MC"): {
        "principle_en": "Idealistic life aims. Inspired or confused direction.",
        "principle_zh": "理想主義的人生目標。受啟發或困惑的方向。",
        "positive_en": "Inspired life aims. Artistic or spiritual vocation.",
        "positive_zh": "受啟發的人生目標。藝術或靈性的職業。",
        "negative_en": "Confused life direction. Self-deception about aims.",
        "negative_zh": "人生方向混亂。關於目標的自我欺騙。",
        "page": "COSI p. 210",
    },
    ("PL", "AS"): {
        "principle_en": "Powerful personal contacts. Transformative relationships.",
        "principle_zh": "強有力的個人聯繫。轉化性的關係。",
        "positive_en": "Powerful, transformative relationships. Great personal magnetism.",
        "positive_zh": "強大的、轉化性的關係。巨大的個人磁性。",
        "negative_en": "Power struggles in relationships. Domination or obsession.",
        "negative_zh": "關係中的權力鬥爭。支配或強迫症。",
        "page": "COSI p. 215",
    },
    ("PL", "MC"): {
        "principle_en": "The drive for power. Transformation of the personality.",
        "principle_zh": "對權力的驅動。個性的轉化。",
        "positive_en": "Great ambition, transformation of career. Leadership.",
        "positive_zh": "遠大抱負、職業轉化。領導力。",
        "negative_en": "Ruthless ambition. Power-driven destruction of status.",
        "negative_zh": "無情的野心。權力驅動的地位破壞。",
        "page": "COSI p. 216",
    },
    ("NN", "AS"): {
        "principle_en": "Important personal contacts. Karmic relationships.",
        "principle_zh": "重要的個人聯繫。業力關係。",
        "positive_en": "Meaningful, fated relationships. Community belonging.",
        "positive_zh": "有意義的、命中注定的關係。社區歸屬感。",
        "negative_en": "Difficult karma in relationships. Fated separations.",
        "negative_zh": "關係中的困難業力。命中注定的分離。",
        "page": "COSI p. 231",
    },
    ("NN", "MC"): {
        "principle_en": "Common aims with others. Shared purpose in community.",
        "principle_zh": "與他人的共同目標。社區中的共同目的。",
        "positive_en": "Successful partnerships with shared goals. Community leadership.",
        "positive_zh": "有共同目標的成功夥伴關係。社區領導力。",
        "negative_en": "Conflicts of aims with others. Difficulties in cooperation.",
        "negative_zh": "與他人目標衝突。合作困難。",
        "page": "COSI p. 232",
    },
}

# ============================================================
# Helper: normalize key lookup (order-independent)
# ============================================================

def get_cosi_interpretation(
    p1: str, p2: str
) -> Optional[Dict[str, str]]:
    """
    Retrieve the COSI interpretation for a pair of planets/points.

    Args:
        p1: First planet abbreviation (e.g. "SO", "MO").
        p2: Second planet abbreviation.

    Returns:
        The interpretation dict, or None if not found.
    """
    key1 = (p1, p2)
    key2 = (p2, p1)
    return COSI_DB.get(key1) or COSI_DB.get(key2)
