"""
astro/interpretations.py — 解讀文字資料庫 (Interpretation Text Database)

Contains transit, synastry, dasha, and natal interpretation texts
for Western, Vedic, and Chinese astrology systems.
"""

# ============================================================
# Planet name canonicalization helpers
# ============================================================

_CANONICAL_MAP = {
    "Sun ☉": "Sun", "Moon ☽": "Moon", "Mercury ☿": "Mercury",
    "Venus ♀": "Venus", "Mars ♂": "Mars", "Jupiter ♃": "Jupiter",
    "Saturn ♄": "Saturn", "Uranus ♅": "Uranus", "Neptune ♆": "Neptune",
    "Pluto ♇": "Pluto",
    "太陽": "Sun", "太陰": "Moon", "水星": "Mercury",
    "金星": "Venus", "火星": "Mars", "木星": "Jupiter", "土星": "Saturn",
    "Surya": "Sun", "Chandra": "Moon", "Mangal": "Mars",
    "Budha": "Mercury", "Guru": "Jupiter", "Shukra": "Venus", "Shani": "Saturn",
    "Rahu": "Rahu", "Ketu": "Ketu",
}

_ASPECT_KEY_MAP = {
    "Conjunction (合)": "Conjunction", "Opposition (沖)": "Opposition",
    "Trine (三合)": "Trine", "Square (刑)": "Square",
    "Sextile (六合)": "Sextile",
}


def _canonical(name: str) -> str:
    """Resolve planet name to canonical English key."""
    if name in _CANONICAL_MAP:
        return _CANONICAL_MAP[name]
    for alias, canon in _CANONICAL_MAP.items():
        if alias in name:
            return canon
    # strip glyph suffix
    base = name.split()[0] if name else name
    return _CANONICAL_MAP.get(base, base)


def _aspect_key(name: str) -> str:
    """Resolve aspect name to canonical key."""
    return _ASPECT_KEY_MAP.get(name, name)


# ============================================================
# Transit Interpretations (流年解讀)
# ============================================================

TRANSIT_INTERPRETATIONS: dict[tuple[str, str, str], tuple[str, str]] = {
    # Jupiter transits
    ("Jupiter", "Sun", "Conjunction"): (
        "A period of growth, optimism, and new opportunities in self-expression and career.",
        "木星合太陽：自信心增強，事業發展機會增多，適合展開新計畫與拓展視野。",
    ),
    ("Jupiter", "Sun", "Trine"): (
        "Smooth period of personal expansion. Good fortune and confidence flow naturally.",
        "木星三合太陽：順遂的個人擴展期，好運和自信自然流動，適合推進長期目標。",
    ),
    ("Jupiter", "Sun", "Opposition"): (
        "Over-expansion risk. Ambitions may exceed capacity. Practice moderation.",
        "木星沖太陽：過度擴張的風險期，野心可能超出能力，需適度節制。",
    ),
    ("Jupiter", "Sun", "Square"): (
        "Tension between growth desires and current reality. Avoid overcommitting.",
        "木星刑太陽：成長渴望與現實之間的張力，避免過度承諾或鋪張。",
    ),
    ("Jupiter", "Moon", "Conjunction"): (
        "Emotional expansion and generosity. Good for family matters and home improvements.",
        "木星合月亮：情感豐沛慷慨的時期，適合處理家庭事務與居住環境改善。",
    ),
    ("Jupiter", "Moon", "Trine"): (
        "Emotional well-being and contentment. Nurturing relationships flourish.",
        "木星三合月亮：情緒安康滿足，親密關係蓬勃發展。",
    ),
    ("Jupiter", "Venus", "Conjunction"): (
        "Excellent for romance, social life, and financial gain. Artistic inspiration peaks.",
        "木星合金星：戀愛、社交與財務收益的絕佳時期，藝術靈感達到高峰。",
    ),
    ("Jupiter", "Venus", "Trine"): (
        "Harmonious period for love, beauty, and pleasure. Financial luck improves.",
        "木星三合金星：愛情、美感與享樂和諧的時期，財運改善。",
    ),
    ("Jupiter", "Mars", "Conjunction"): (
        "Surge of energy and initiative. Great for starting new ventures.",
        "木星合火星：能量與主動性暴增，適合開創新事業。",
    ),
    ("Jupiter", "Saturn", "Conjunction"): (
        "Major life restructuring. Balancing expansion with discipline yields lasting results.",
        "木星合土星：人生重大重整期，在擴展與紀律之間取得平衡可帶來持久成果。",
    ),
    # Saturn transits
    ("Saturn", "Sun", "Conjunction"): (
        "Major reality check. Time to commit seriously to long-term goals. Health needs attention.",
        "土星合太陽：重大的現實考驗，必須認真投入長期目標，健康需注意。",
    ),
    ("Saturn", "Sun", "Opposition"): (
        "Relationship and career challenges test your foundations. Patience required.",
        "土星沖太陽：關係與事業的挑戰考驗你的根基，需要耐心。",
    ),
    ("Saturn", "Sun", "Square"): (
        "Frustration and obstacles. Hard work now builds character and future success.",
        "土星刑太陽：挫折與阻礙期，此時的努力能磨練品格並奠定未來的成功。",
    ),
    ("Saturn", "Moon", "Conjunction"): (
        "Emotional maturation. Loneliness may surface. Time to build inner resilience.",
        "土星合月亮：情感成熟期，可能出現孤獨感，是建立內在韌性的時候。",
    ),
    ("Saturn", "Moon", "Square"): (
        "Emotional restrictions and responsibilities. Past issues may surface for resolution.",
        "土星刑月亮：情緒壓力增加，家庭責任加重，過去的問題浮現需要處理。",
    ),
    ("Saturn", "Moon", "Opposition"): (
        "Relationships may feel burdened. Emotional boundaries need reassessment.",
        "土星沖月亮：關係感覺沉重，情感界限需要重新評估。",
    ),
    ("Saturn", "Venus", "Conjunction"): (
        "Serious relationships form. Financial discipline required. Love matures.",
        "土星合金星：認真的關係形成期，財務需紀律，愛情走向成熟。",
    ),
    ("Saturn", "Venus", "Square"): (
        "Love life feels restricted. Financial pressures. Reassess values.",
        "土星刑金星：感情生活受限，財務壓力，需重新審視價值觀。",
    ),
    ("Saturn", "Mars", "Conjunction"): (
        "Energy feels blocked. Frustration with slow progress. Controlled effort succeeds.",
        "土星合火星：能量受阻的感覺，對進展緩慢感到挫折，有控制的努力終將成功。",
    ),
    ("Saturn", "Jupiter", "Conjunction"): (
        "Reality meets aspiration. Build lasting structures for your dreams.",
        "土星合木星：現實與理想交匯，為夢想建立持久的架構。",
    ),
    # Mars transits
    ("Mars", "Sun", "Conjunction"): (
        "Energy and drive peak. Initiative and courage boost. Watch for impulsiveness.",
        "火星合太陽：能量與動力達到頂峰，主動性和勇氣增強，注意衝動。",
    ),
    ("Mars", "Moon", "Conjunction"): (
        "Emotional intensity rises. Possible irritability. Channel energy into action.",
        "火星合月亮：情緒強度上升，可能出現易怒，將能量引導至行動中。",
    ),
    ("Mars", "Venus", "Conjunction"): (
        "Passion and desire intensify. Romance or creative projects energized.",
        "火星合金星：熱情與慾望增強，戀愛或創意項目充滿活力。",
    ),
    ("Mars", "Mars", "Conjunction"): (
        "Mars return — new two-year energy cycle begins. Assert your goals.",
        "火星回歸——新的兩年能量週期開始，堅定你的目標。",
    ),
    ("Mars", "Saturn", "Conjunction"): (
        "Tension between action and restriction. Careful, disciplined effort required.",
        "火星合土星：行動與限制之間的張力，需要小心且有紀律的努力。",
    ),
    ("Mars", "Saturn", "Square"): (
        "Blocked energy and frustration. Avoid confrontations. Strategic patience wins.",
        "火星刑土星：能量受阻與挫折感，避免對抗，策略性耐心勝出。",
    ),
    # Venus transits
    ("Venus", "Sun", "Conjunction"): (
        "Charm and attractiveness increase. Good for social events and romance.",
        "金星合太陽：魅力與吸引力增加，適合社交活動與戀愛。",
    ),
    ("Venus", "Moon", "Conjunction"): (
        "Emotional warmth and comfort. Good for family gatherings and self-care.",
        "金星合月亮：情感溫暖舒適期，適合家庭聚會和自我照顧。",
    ),
    ("Venus", "Venus", "Conjunction"): (
        "Venus return — new cycle of relationships and values. Reflect on what you love.",
        "金星回歸——關係與價值觀的新週期，反思你所珍愛之事。",
    ),
    ("Venus", "Mars", "Conjunction"): (
        "Romantic and creative energy surge. Attraction and passion heightened.",
        "金星合火星：浪漫與創造能量湧現，吸引力和激情高漲。",
    ),
    # Mercury transits
    ("Mercury", "Sun", "Conjunction"): (
        "Mental clarity and communication skills peak. Good for negotiations and writing.",
        "水星合太陽：思維清晰度與溝通能力達到頂峰，適合談判和寫作。",
    ),
    ("Mercury", "Moon", "Conjunction"): (
        "Emotional and intellectual connection. Good for expressing feelings verbally.",
        "水星合月亮：情感與智性的連結，適合用言語表達感受。",
    ),
    ("Mercury", "Mercury", "Conjunction"): (
        "Mercury return — new communication cycle. Ideas and contacts refresh.",
        "水星回歸——新的溝通週期，想法和人脈更新。",
    ),
    # Sun transits
    ("Sun", "Sun", "Conjunction"): (
        "Solar return — birthday period. New yearly cycle of self-expression begins.",
        "太陽回歸——生日期間，自我表達的新年度週期開始。",
    ),
    ("Sun", "Sun", "Opposition"): (
        "Half-birthday. Review progress and adjust goals for the year's second half.",
        "太陽沖太陽：半年檢視點，回顧進展並調整下半年目標。",
    ),
    ("Sun", "Moon", "Conjunction"): (
        "Alignment of will and emotions. Confidence to act on feelings.",
        "太陽合月亮：意志與情感的對齊，有信心依據感受行動。",
    ),
    ("Sun", "Moon", "Opposition"): (
        "Tension between public self and private needs. Balance inner/outer life.",
        "太陽沖月亮：公眾自我與私人需求之間的張力，平衡內外生活。",
    ),
    # Outer planet transits
    ("Uranus", "Sun", "Conjunction"): (
        "Life-changing awakening. Sudden shifts in identity and direction. Embrace change.",
        "天王星合太陽：改變人生的覺醒，身份和方向突然轉變，擁抱變化。",
    ),
    ("Uranus", "Moon", "Conjunction"): (
        "Emotional liberation. Unexpected changes in home and family. Freedom needed.",
        "天王星合月亮：情感解放，家庭和居所的意外變化，需要自由空間。",
    ),
    ("Neptune", "Sun", "Conjunction"): (
        "Spiritual awakening but ego boundaries dissolve. Watch for confusion and deception.",
        "海王星合太陽：靈性覺醒但自我界限溶解，注意困惑和欺騙。",
    ),
    ("Neptune", "Moon", "Conjunction"): (
        "Heightened intuition and sensitivity. Creative inspiration. Avoid escapism.",
        "海王星合月亮：直覺和敏感度增強，創意靈感豐富，避免逃避現實。",
    ),
    ("Pluto", "Sun", "Conjunction"): (
        "Profound transformation of self. Power struggles and rebirth. Life-altering period.",
        "冥王星合太陽：自我的深刻轉化，權力鬥爭與重生，人生改變的時期。",
    ),
    ("Pluto", "Moon", "Conjunction"): (
        "Intense emotional transformation. Deep psychological healing. Release old patterns.",
        "冥王星合月亮：強烈的情感轉化，深層心理療癒，釋放舊模式。",
    ),
    # Moon transits (brief)
    ("Moon", "Sun", "Conjunction"): (
        "Short burst of emotional alignment with your core self. Act on instinct today.",
        "月亮合太陽：短暫的情感與核心自我對齊，今天依直覺行動。",
    ),
    ("Moon", "Moon", "Conjunction"): (
        "Lunar return — emotional reset every 28 days. Tune into your deepest needs.",
        "月亮回歸——每28天的情感重置，傾聽最深層的需求。",
    ),
}


# ============================================================
# Synastry Interpretations (合盤解讀)
# ============================================================

SYNASTRY_INTERPRETATIONS: dict[tuple[str, str, str], tuple[str, str, float]] = {
    # Sun aspects
    ("Sun", "Sun", "Conjunction"): (
        "Powerful identity bond. You energize each other but may also compete for attention.",
        "太陽合太陽：強大的身份認同連結，彼此激勵但也可能競爭焦點。",
        0.7,
    ),
    ("Sun", "Moon", "Conjunction"): (
        "Classic soulmate aspect. The Sun person vitalizes, the Moon person nurtures.",
        "太陽合月亮：經典靈魂伴侶相位，太陽方給予活力，月亮方提供滋養。",
        1.0,
    ),
    ("Sun", "Moon", "Opposition"): (
        "Magnetic attraction with awareness of differences. Growth through complementarity.",
        "太陽沖月亮：意識到差異的磁性吸引，通過互補而成長。",
        0.4,
    ),
    ("Sun", "Venus", "Conjunction"): (
        "Natural affection and admiration. The Venus person adores the Sun person's vitality.",
        "太陽合金星：自然的愛慕和欣賞，金星方崇拜太陽方的活力。",
        0.9,
    ),
    ("Sun", "Mars", "Conjunction"): (
        "Dynamic and passionate. Shared drive and initiative, but watch for ego clashes.",
        "太陽合火星：動態且充滿熱情，共同的驅動力與主動性，注意自我衝突。",
        0.5,
    ),
    ("Sun", "Jupiter", "Conjunction"): (
        "Uplifting and optimistic bond. Mutual encouragement and shared adventures.",
        "太陽合木星：令人振奮的樂觀連結，互相鼓勵與共同冒險。",
        0.8,
    ),
    ("Sun", "Saturn", "Conjunction"): (
        "Serious, committed bond. The Saturn person stabilizes but may restrict the Sun.",
        "太陽合土星：認真且有承諾的連結，土星方穩定但可能限制太陽方。",
        0.2,
    ),
    # Moon aspects
    ("Moon", "Moon", "Conjunction"): (
        "Deep emotional understanding. You feel at home with each other instantly.",
        "月亮合月亮：深層的情感理解，彼此立刻感到像回到家一樣。",
        0.9,
    ),
    ("Moon", "Venus", "Conjunction"): (
        "Gentle and loving connection. Emotional comfort and shared aesthetic sense.",
        "月亮合金星：溫柔且充滿愛意的連結，情感慰藉與共同的美感。",
        0.9,
    ),
    ("Moon", "Mars", "Conjunction"): (
        "Emotionally exciting but volatile. Passion mixed with sensitivity.",
        "月亮合火星：情感上令人興奮但也不穩定，熱情與敏感交織。",
        0.3,
    ),
    # Venus-Mars
    ("Venus", "Mars", "Conjunction"): (
        "Strong physical and romantic attraction. Classic chemistry between two people.",
        "金星合火星：強烈的身體和浪漫吸引力，雙方之間的經典化學反應。",
        0.8,
    ),
    ("Venus", "Mars", "Opposition"): (
        "Irresistible attraction with push-pull dynamics. Exciting but requires balance.",
        "金星沖火星：不可抗拒的吸引力與推拉動態，令人興奮但需要平衡。",
        0.5,
    ),
    ("Venus", "Mars", "Square"): (
        "Sexual tension and frustration. Desire is strong but timing may be off.",
        "金星刑火星：性張力和挫折感，慾望強烈但時機可能不對。",
        0.2,
    ),
    ("Venus", "Jupiter", "Conjunction"): (
        "Joyful, generous, and indulgent. Great for shared pleasures and travel.",
        "金星合木星：歡樂、慷慨且享受的關係，適合共同享樂與旅行。",
        0.8,
    ),
    ("Venus", "Saturn", "Conjunction"): (
        "Loyal and enduring but may lack spontaneity. Love tested by time.",
        "金星合土星：忠誠且持久但可能缺乏自發性，愛情經受時間考驗。",
        0.3,
    ),
    ("Venus", "Venus", "Conjunction"): (
        "Shared values and tastes. You appreciate the same things in life.",
        "金星合金星：共同的價值觀和品味，你們欣賞生活中相同的事物。",
        0.7,
    ),
    # Mars aspects
    ("Mars", "Mars", "Conjunction"): (
        "Similar energy levels and drive. Can be highly productive or competitive.",
        "火星合火星：相似的能量水平和驅動力，可以高度有效率或彼此競爭。",
        0.4,
    ),
    ("Mars", "Jupiter", "Conjunction"): (
        "Energizing and adventurous. Mutual encouragement to take bold action.",
        "火星合木星：充滿活力和冒險精神，互相鼓勵採取大膽行動。",
        0.7,
    ),
    ("Mars", "Saturn", "Conjunction"): (
        "Frustrating dynamics. One pushes, the other restricts. Requires patience.",
        "火星合土星：令人挫折的動態，一方推動另一方限制，需要耐心。",
        -0.3,
    ),
    # Jupiter-Saturn
    ("Jupiter", "Saturn", "Conjunction"): (
        "Growth meets structure. A mature bond that can achieve great things together.",
        "木星合土星：成長與結構的相遇，成熟的連結能共同成就大事。",
        0.5,
    ),
}


# ============================================================
# Dasha Lord Meanings (大限主星解讀 — Vedic)
# ============================================================

DASHA_LORD_MEANINGS: dict[str, dict[str, str]] = {
    "Sun": {
        "en": "Focus on authority, leadership, health, and father-related matters. Government dealings may be prominent. Self-confidence and vitality are highlighted.",
        "cn": "太陽大限：重點在權威、領導能力、健康與父親相關事務。可能涉及與政府的往來。自信心和活力被突顯。",
    },
    "Moon": {
        "en": "Emotional growth, mother, public life, and travel. Mental peace and domestic happiness are key themes. Water-related activities may increase.",
        "cn": "月亮大限：情緒發展、母親、公眾生活與旅行。心靈平靜和家庭幸福是關鍵主題。與水相關的活動可能增加。",
    },
    "Mars": {
        "en": "Period of courage, action, siblings, and property matters. Physical energy increases. Conflicts and surgical interventions possible.",
        "cn": "火星大限：勇氣、行動力、兄弟姊妹與不動產事務的時期。體能增加。可能出現衝突和手術。",
    },
    "Mercury": {
        "en": "Intellectual pursuits, communication, business, and education. Good for studies, writing, and commerce. Nervous energy may increase.",
        "cn": "水星大限：智性追求、溝通、商業與教育的時期。適合讀書、寫作和商業活動。神經能量可能增加。",
    },
    "Jupiter": {
        "en": "Expansion, wisdom, children, and spiritual growth. Financial prosperity likely. Teaching and advisory roles may develop.",
        "cn": "木星大限：擴展、智慧、子女與靈性成長的時期。財務繁榮的可能性高。可能發展教學和諮詢角色。",
    },
    "Venus": {
        "en": "Love, marriage, arts, luxury, and vehicles. Social life flourishes. Creative talents shine. Romance and partnerships are emphasized.",
        "cn": "金星大限：愛情、婚姻、藝術、奢侈品與車輛的時期。社交生活蓬勃發展。創意才華閃耀。戀愛和夥伴關係被強調。",
    },
    "Saturn": {
        "en": "Hard work, discipline, delays, and karmic lessons. Chronic health issues may surface. Land and labor matters prominent. Patience required.",
        "cn": "土星大限：努力工作、紀律、延遲與業力功課的時期。慢性健康問題可能浮現。土地和勞動事務突出。需要耐心。",
    },
    "Rahu": {
        "en": "Unconventional experiences, foreign connections, technology, and sudden changes. Desires intensify. Material gains possible but through unusual means.",
        "cn": "羅睺大限：非傳統的經歷、外國連結、科技與突然變化的時期。慾望增強。可能通過不尋常的方式獲得物質收益。",
    },
    "Ketu": {
        "en": "Spiritual detachment, past-life karma, sudden losses, and mystical experiences. Letting go of attachments. Introspection deepens.",
        "cn": "計都大限：靈性超脫、前世業力、突然失去與神秘體驗的時期。放下執著。內省加深。",
    },
}


# ============================================================
# Qizheng Dasha Meanings (七政四餘大運解讀)
# ============================================================

QIZHENG_DASHA_MEANINGS: dict[str, dict[str, str]] = {
    "太陽": {
        "en": "Solar period (19 yrs): Authority, reputation, health vitality. Career advancement through leadership.",
        "cn": "太陽限（19年）：權威、名聲、健康活力。通過領導能力推進事業。",
    },
    "太陰": {
        "en": "Lunar period (25 yrs): Emotions, family, travel, public affairs. Nurturing relationships matter.",
        "cn": "太陰限（25年）：情感、家庭、旅行、公眾事務。滋養型關係重要。",
    },
    "火星": {
        "en": "Mars period (7 yrs): Courage, conflicts, surgery, property. High energy but short-tempered.",
        "cn": "火星限（7年）：勇氣、衝突、手術、不動產。精力充沛但容易急躁。",
    },
    "水星": {
        "en": "Mercury period (20 yrs): Intelligence, commerce, writing, education. Communication skills highlighted.",
        "cn": "水星限（20年）：智慧、商業、寫作、教育。溝通能力被突顯。",
    },
    "木星": {
        "en": "Jupiter period (12 yrs): Expansion, fortune, children, wisdom. Benevolent period overall.",
        "cn": "木星限（12年）：擴展、福運、子女、智慧。整體而言是吉利的時期。",
    },
    "金星": {
        "en": "Venus period (15 yrs): Love, art, luxury, partnerships. Social and romantic life flourishes.",
        "cn": "金星限（15年）：愛情、藝術、奢侈、合作關係。社交和感情生活蓬勃發展。",
    },
    "土星": {
        "en": "Saturn period (22 yrs): Discipline, hard work, delays, karmic duty. Patience builds lasting success.",
        "cn": "土星限（22年）：紀律、努力、延遲、因果責任。耐心能建立持久的成功。",
    },
}


# ============================================================
# Yogini Dasha Meanings (瑜伽尼大限解讀)
# ============================================================

YOGINI_DASHA_MEANINGS: dict[str, dict[str, str]] = {
    "Mangala": {
        "en": "Mangala (1 yr): Auspicious beginnings. Quick positive results. Good health.",
        "cn": "吉祥期（1年）：吉利的開端，快速正面結果，健康良好。",
    },
    "Pingala": {
        "en": "Pingala (2 yrs): Mixed results. Solar energy. Government relations important.",
        "cn": "紅光期（2年）：結果混合。太陽能量。與政府的關係重要。",
    },
    "Dhanya": {
        "en": "Dhanya (3 yrs): Prosperity and abundance. Good for wealth accumulation.",
        "cn": "豐收期（3年）：繁榮與豐盛。適合累積財富。",
    },
    "Bhramari": {
        "en": "Bhramari (4 yrs): Mixed period. Travel and restlessness. Creative endeavors.",
        "cn": "蜜蜂期（4年）：混合時期。旅行與不安定。創意活動。",
    },
    "Bhadrika": {
        "en": "Bhadrika (5 yrs): Very auspicious. Success in all endeavors. Happy family life.",
        "cn": "吉祥母期（5年）：非常吉利。所有努力都能成功。家庭生活幸福。",
    },
    "Ulka": {
        "en": "Ulka (6 yrs): Difficult period. Sudden changes. Health requires attention.",
        "cn": "流星期（6年）：困難的時期。突然的變化。健康需要注意。",
    },
    "Siddha": {
        "en": "Siddha (7 yrs): Spiritual attainment and accomplishment. Wisdom deepens.",
        "cn": "成就期（7年）：靈性成就與達成目標。智慧加深。",
    },
    "Sankata": {
        "en": "Sankata (8 yrs): Obstacles and difficulties. Karmic lessons. Inner growth through struggle.",
        "cn": "障礙期（8年）：障礙與困難。業力功課。通過掙扎而內在成長。",
    },
}


# ============================================================
# Sign Readings (星座解讀)
# ============================================================

ASC_READINGS: dict[str, dict[str, str]] = {
    "Aries": {
        "en": "Aries rising: Bold, energetic, and pioneering spirit. Natural leader with strong initiative.",
        "cn": "白羊座上升：大膽、充滿活力的開拓精神。天生的領導者，主動性強。",
    },
    "Taurus": {
        "en": "Taurus rising: Grounded, patient, and sensual. Values stability and material comfort.",
        "cn": "金牛座上升：踏實、有耐心且注重感官。重視穩定和物質舒適。",
    },
    "Gemini": {
        "en": "Gemini rising: Curious, communicative, and adaptable. Quick mind with diverse interests.",
        "cn": "雙子座上升：好奇、善溝通且適應力強。思維敏捷，興趣多元。",
    },
    "Cancer": {
        "en": "Cancer rising: Sensitive, nurturing, and protective. Strong emotional intuition.",
        "cn": "巨蟹座上升：敏感、有養育之心且具保護性。強烈的情感直覺。",
    },
    "Leo": {
        "en": "Leo rising: Confident, dramatic, and warm-hearted. Natural magnetism and creative flair.",
        "cn": "獅子座上升：自信、戲劇性且熱心。天生的魅力和創意天分。",
    },
    "Virgo": {
        "en": "Virgo rising: Analytical, practical, and health-conscious. Detail-oriented perfectionist.",
        "cn": "處女座上升：分析型、務實且注重健康。注重細節的完美主義者。",
    },
    "Libra": {
        "en": "Libra rising: Charming, diplomatic, and aesthetically inclined. Seeks harmony in relationships.",
        "cn": "天秤座上升：迷人、善外交且有美感。在關係中追求和諧。",
    },
    "Scorpio": {
        "en": "Scorpio rising: Intense, magnetic, and deeply perceptive. Powerful emotional depth.",
        "cn": "天蠍座上升：強烈、有磁性且深具洞察力。強大的情感深度。",
    },
    "Sagittarius": {
        "en": "Sagittarius rising: Optimistic, adventurous, and philosophical. Love of freedom and exploration.",
        "cn": "射手座上升：樂觀、愛冒險且具哲學思維。熱愛自由和探索。",
    },
    "Capricorn": {
        "en": "Capricorn rising: Ambitious, disciplined, and responsible. Long-term planner and achiever.",
        "cn": "摩羯座上升：有野心、自律且負責。長期規劃者和成就者。",
    },
    "Aquarius": {
        "en": "Aquarius rising: Independent, innovative, and humanitarian. Original thinker and reformer.",
        "cn": "水瓶座上升：獨立、創新且具人道主義精神。原創思想家和改革者。",
    },
    "Pisces": {
        "en": "Pisces rising: Empathetic, intuitive, and dreamy. Strong spiritual and artistic sensitivity.",
        "cn": "雙魚座上升：富同理心、直覺強且夢幻。強烈的靈性和藝術敏感度。",
    },
}

SUN_SIGN_READINGS: dict[str, dict[str, str]] = {
    "Aries": {
        "en": "Sun in Aries: Core identity centers on courage, initiative, and leadership. Thrives on challenges and new beginnings.",
        "cn": "太陽在白羊座：核心身份以勇氣、主動性和領導力為中心。在挑戰和新開始中蓬勃發展。",
    },
    "Taurus": {
        "en": "Sun in Taurus: Core identity values stability, sensuality, and material security. Patient and determined nature.",
        "cn": "太陽在金牛座：核心身份重視穩定、感官享受和物質安全。耐心且堅定的性格。",
    },
    "Gemini": {
        "en": "Sun in Gemini: Core identity expresses through communication, curiosity, and intellectual versatility.",
        "cn": "太陽在雙子座：核心身份通過溝通、好奇心和智性多才多藝來表達。",
    },
    "Cancer": {
        "en": "Sun in Cancer: Core identity is rooted in emotional security, family, and nurturing. Deep instinctual wisdom.",
        "cn": "太陽在巨蟹座：核心身份根植於情感安全、家庭和養育。深層的本能智慧。",
    },
    "Leo": {
        "en": "Sun in Leo: Core identity shines through creativity, self-expression, and generous warmth.",
        "cn": "太陽在獅子座：核心身份通過創造力、自我表達和慷慨的溫暖閃耀。",
    },
    "Virgo": {
        "en": "Sun in Virgo: Core identity driven by service, analysis, and pursuit of practical perfection.",
        "cn": "太陽在處女座：核心身份由服務、分析和追求實際完美所驅動。",
    },
    "Libra": {
        "en": "Sun in Libra: Core identity seeks balance, partnership, and aesthetic harmony in all things.",
        "cn": "太陽在天秤座：核心身份在所有事物中追求平衡、夥伴關係和美學和諧。",
    },
    "Scorpio": {
        "en": "Sun in Scorpio: Core identity forged through transformation, depth, and emotional power.",
        "cn": "太陽在天蠍座：核心身份通過轉化、深度和情感力量鍛造。",
    },
    "Sagittarius": {
        "en": "Sun in Sagittarius: Core identity animated by adventure, philosophy, and the search for meaning.",
        "cn": "太陽在射手座：核心身份由冒險、哲學和尋找意義所激發。",
    },
    "Capricorn": {
        "en": "Sun in Capricorn: Core identity built on ambition, discipline, and achieving tangible results.",
        "cn": "太陽在摩羯座：核心身份建立在野心、紀律和實現具體成果之上。",
    },
    "Aquarius": {
        "en": "Sun in Aquarius: Core identity expressed through innovation, independence, and humanitarian vision.",
        "cn": "太陽在水瓶座：核心身份通過創新、獨立和人道主義願景來表達。",
    },
    "Pisces": {
        "en": "Sun in Pisces: Core identity flows through compassion, imagination, and spiritual receptivity.",
        "cn": "太陽在雙魚座：核心身份通過慈悲、想像力和靈性接受性流動。",
    },
}

MOON_SIGN_READINGS: dict[str, dict[str, str]] = {
    "Aries": {
        "en": "Moon in Aries: Emotional nature is fiery and impulsive. Needs independence and action to feel secure.",
        "cn": "月亮在白羊座：情感本質火熱且衝動，需要獨立和行動來感到安全。",
    },
    "Taurus": {
        "en": "Moon in Taurus: Emotional nature is steady and comfort-seeking. Deep need for material and emotional stability.",
        "cn": "月亮在金牛座：情感本質穩定且追求舒適，深層需要物質和情感的穩定。",
    },
    "Gemini": {
        "en": "Moon in Gemini: Emotional nature is curious and changeable. Needs mental stimulation and variety.",
        "cn": "月亮在雙子座：情感本質好奇且多變，需要智性刺激和多樣性。",
    },
    "Cancer": {
        "en": "Moon in Cancer: Emotional nature is deeply nurturing and sensitive. Home and family provide emotional anchor.",
        "cn": "月亮在巨蟹座：情感本質深具養育性和敏感，家和家庭提供情感錨點。",
    },
    "Leo": {
        "en": "Moon in Leo: Emotional nature is warm and dramatic. Needs recognition and creative expression.",
        "cn": "月亮在獅子座：情感本質溫暖且戲劇性，需要被認可和創意表達。",
    },
    "Virgo": {
        "en": "Moon in Virgo: Emotional nature is analytical and service-oriented. Needs order and usefulness.",
        "cn": "月亮在處女座：情感本質是分析型且以服務為導向，需要秩序和實用性。",
    },
    "Libra": {
        "en": "Moon in Libra: Emotional nature seeks harmony and partnership. Needs beauty and balanced relationships.",
        "cn": "月亮在天秤座：情感本質追求和諧與夥伴關係，需要美感和平衡的關係。",
    },
    "Scorpio": {
        "en": "Moon in Scorpio: Emotional nature is intense and private. Needs depth, trust, and emotional honesty.",
        "cn": "月亮在天蠍座：情感本質強烈且私密，需要深度、信任和情感誠實。",
    },
    "Sagittarius": {
        "en": "Moon in Sagittarius: Emotional nature is optimistic and freedom-loving. Needs adventure and meaning.",
        "cn": "月亮在射手座：情感本質樂觀且熱愛自由，需要冒險和意義。",
    },
    "Capricorn": {
        "en": "Moon in Capricorn: Emotional nature is reserved and responsible. Needs achievement and structure.",
        "cn": "月亮在摩羯座：情感本質含蓄且負責，需要成就和結構。",
    },
    "Aquarius": {
        "en": "Moon in Aquarius: Emotional nature is detached and progressive. Needs intellectual freedom and community.",
        "cn": "月亮在水瓶座：情感本質超然且進步，需要智性自由和社群。",
    },
    "Pisces": {
        "en": "Moon in Pisces: Emotional nature is deeply empathetic and dreamy. Needs creative and spiritual outlets.",
        "cn": "月亮在雙魚座：情感本質深具同理心且夢幻，需要創意和靈性出口。",
    },
}


# ============================================================
# Public API
# ============================================================

def get_transit_reading(transit_planet: str, natal_planet: str,
                        aspect: str, lang: str = "zh") -> str:
    """Look up transit interpretation text."""
    t_key = _canonical(transit_planet)
    n_key = _canonical(natal_planet)
    a_key = _aspect_key(aspect)
    entry = TRANSIT_INTERPRETATIONS.get((t_key, n_key, a_key))
    if not entry:
        return _generic_transit_text(transit_planet, natal_planet, aspect, lang)
    return entry[1] if lang == "zh" else entry[0]


def get_synastry_reading(planet_a: str, planet_b: str,
                         aspect: str, lang: str = "zh") -> str:
    """Look up synastry interpretation text."""
    a_key = _canonical(planet_a)
    b_key = _canonical(planet_b)
    asp = _aspect_key(aspect)
    entry = SYNASTRY_INTERPRETATIONS.get((a_key, b_key, asp))
    if not entry:
        # Try reversed order
        entry = SYNASTRY_INTERPRETATIONS.get((b_key, a_key, asp))
    if not entry:
        return _generic_synastry_text(planet_a, planet_b, aspect, lang)
    return entry[1] if lang == "zh" else entry[0]


def get_dasha_reading(lord: str, lang: str = "zh") -> str:
    """Look up Vedic dasha lord interpretation."""
    key = _canonical(lord)
    entry = DASHA_LORD_MEANINGS.get(key)
    if not entry:
        return ""
    return entry.get("cn" if lang == "zh" else "en", "")


def get_yogini_reading(yogini_name: str, lang: str = "zh") -> str:
    """Look up Yogini dasha interpretation."""
    entry = YOGINI_DASHA_MEANINGS.get(yogini_name)
    if not entry:
        return ""
    return entry.get("cn" if lang == "zh" else "en", "")


def get_qizheng_dasha_reading(lord: str, lang: str = "zh") -> str:
    """Look up Qizheng dasha lord interpretation."""
    entry = QIZHENG_DASHA_MEANINGS.get(lord)
    if not entry:
        return ""
    return entry.get("cn" if lang == "zh" else "en", "")


def _generic_transit_text(transit_planet: str, natal_planet: str,
                          aspect: str, lang: str) -> str:
    """Generate generic transit interpretation."""
    if lang == "zh":
        return f"過運 {transit_planet} {aspect} 本命 {natal_planet}：留意此相位帶來的能量變化。"
    return f"Transit {transit_planet} {aspect} natal {natal_planet}: Pay attention to the energy shift this aspect brings."


def _generic_synastry_text(planet_a: str, planet_b: str,
                           aspect: str, lang: str) -> str:
    """Generate generic synastry interpretation."""
    if lang == "zh":
        return f"A的 {planet_a} {aspect} B的 {planet_b}：此相位影響兩人之間的互動方式。"
    return f"A's {planet_a} {aspect} B's {planet_b}: This aspect influences how the two people interact."
