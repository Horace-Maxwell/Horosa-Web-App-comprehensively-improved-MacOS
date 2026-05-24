"""
astro/maya/constants.py — 瑪雅占星常量 (Maya Astrology Constants)

包含 Tzolk'in、Haab、Long Count 的完整常量與詮釋資料。
Contains complete constants and interpretive data for Tzolk'in, Haab, and Long Count.

GMT Correlation (Goodman-Martinez-Thompson): JD 584283 = 0.0.0.0.0 = 4 Ajaw 8 Kumku

Note: swisseph is imported solely to resolve planet ID constants (swe.SUN, swe.VENUS, …)
used in MAYAN_PLANETS. Actual ephemeris calculations happen in calculator.py.
"""

import swisseph as swe

# ============================================================
# 基準常量 (Base Constants)
# ============================================================

# GMT correlation constant (Goodman-Martinez-Thompson)
# Julian Day of the Mayan Long Count epoch (0.0.0.0.0 = 4 Ajaw 8 Kumku)
MAYAN_EPOCH_JD = 584283.0

# Tzolk'in offsets from epoch (GMT correlation)
# At epoch (day 0): Tzolk'in = 4 Ajaw
#   number offset: (0 + 3) % 13 + 1 = 4  → TZOLKIN_NUMBER_OFFSET = 3
#   sign offset:   (0 + 19) % 20 = 19 (Ajaw) → TZOLKIN_SIGN_OFFSET = 19
TZOLKIN_NUMBER_OFFSET = 3   # Added before mod-13
TZOLKIN_SIGN_OFFSET = 19    # Added before mod-20

# Haab offset from epoch (GMT correlation)
# At epoch (day 0): Haab = 8 Kumku (month index 17, day 8)
# Position = 17*20 + 8 = 348
HAAB_EPOCH_OFFSET = 348     # Added before mod-365

# Long Count unit sizes (in K'in / days)
KINS_PER_WINAL  = 20
KINS_PER_TUN    = 360        # 18 Winals
KINS_PER_KATUN  = 7_200      # 20 Tuns
KINS_PER_BAKTUN = 144_000    # 20 Katuns
KINS_PER_PIKTUN = 2_880_000  # 20 Baktuns

# Degrees of ecliptic longitude per Tzolk'in sign (360° / 20 signs = 18°/sign)
# Used to map planetary longitudes to a Tzolk'in day sign.
DEGREES_PER_TZOLKIN_SIGN: float = 18.0

# ============================================================
# Tzolk'in 二十日符號 (20 Day Signs)
# ============================================================
# 格式：完整詮釋字典列表
# Format: list of full interpretation dicts

TZOLKIN_DAY_DATA = [
    {
        "index": 0,
        "name": "Imix",
        "name_cn": "伊米希",
        "name_en": "Water Lily / Crocodile",
        "glyph_emoji": "🌊",
        "element": "water", "element_cn": "水",
        "direction": "east", "direction_cn": "東",
        "color": "#1a6b8a",
        "deity": "Itzamna", "deity_cn": "伊茲瑪那（創世之神）",
        "animal": "Crocodile / Water Lily", "animal_cn": "鱷魚 / 水蓮",
        "personality_cn": "直覺敏銳、具創造原力、喜探索未知。靈性豐富，有保護他人的天性。",
        "personality_en": "Deeply intuitive, primal creative force, loves exploring the unknown. Spiritually rich with a protective nature.",
        "destiny_cn": "帶著宇宙初始的能量降生，是新時代的開創者。你的使命是滋養他人的靈魂。",
        "destiny_en": "Born with primordial cosmic energy, you are a pioneer of new eras. Your mission is to nourish others' souls.",
        "mythology_cn": "伊米希代表宇宙大洋的初始表面——創世之前的原始水域。瑪雅神話中，世界從伊茲瑪那神的水蓮中誕生。",
        "mythology_en": "Imix represents the primordial surface of the cosmic ocean before creation. In Maya myth, the world was born from Itzamna's water lily.",
    },
    {
        "index": 1,
        "name": "Ik'",
        "name_cn": "伊克",
        "name_en": "Wind / Breath",
        "glyph_emoji": "🌀",
        "element": "air", "element_cn": "風",
        "direction": "north", "direction_cn": "北",
        "color": "#5c8db8",
        "deity": "Kukulkan (Wind)", "deity_cn": "庫庫爾坎（風之羽蛇神）",
        "animal": "Hummingbird", "animal_cn": "蜂鳥",
        "personality_cn": "善溝通、思維靈活、充滿靈性氣息。能感知他人心意，是天生的傳訊者。",
        "personality_en": "Excellent communicator, flexible thinker, spiritually gifted. Can sense others' thoughts; a natural messenger.",
        "destiny_cn": "你是神聖訊息的傳遞者。風吹過的地方，你帶來轉變與呼吸新鮮生命的機會。",
        "destiny_en": "You are a carrier of divine messages. Wherever the wind blows, you bring transformation and fresh life.",
        "mythology_cn": "伊克是神聖的呼吸與生命之氣。在瑪雅創世故事中，神明將呼吸（伊克）吹入泥塑人形，帶來生命。",
        "mythology_en": "Ik' is sacred breath and the life force. In Maya creation myths, gods blew Ik' into clay figures to bring them to life.",
    },
    {
        "index": 2,
        "name": "Ak'bal",
        "name_cn": "阿克巴",
        "name_en": "Night / Darkness",
        "glyph_emoji": "🌙",
        "element": "earth", "element_cn": "地",
        "direction": "west", "direction_cn": "西",
        "color": "#2d1b4e",
        "deity": "Jaguar Sun God", "deity_cn": "美洲豹太陽神",
        "animal": "Jaguar", "animal_cn": "美洲豹",
        "personality_cn": "深沉內斂、直覺力強、與夢境世界連結深厚。在黑暗中尋找光明的智者。",
        "personality_en": "Deep and introspective, powerful intuition, deeply connected to the dream world. A wise seeker of light in darkness.",
        "destiny_cn": "你是夜的守護者，在黑暗中點燃內在之光。你的洞察力能穿透表象，揭示隱藏的真相。",
        "destiny_en": "You are guardian of the night, kindling inner light in darkness. Your insight penetrates surfaces to reveal hidden truths.",
        "mythology_cn": "阿克巴代表夜晚的宮殿，是美洲豹太陽神在夜間穿越地下世界的旅程。黑暗中蘊含著神聖的轉化力量。",
        "mythology_en": "Ak'bal represents the House of Darkness, the Jaguar Sun God's nocturnal journey through the underworld. Sacred transformation resides in the dark.",
    },
    {
        "index": 3,
        "name": "K'an",
        "name_cn": "坎",
        "name_en": "Maize / Seed",
        "glyph_emoji": "🌽",
        "element": "fire", "element_cn": "火",
        "direction": "south", "direction_cn": "南",
        "color": "#d4a017",
        "deity": "Corn God (Hun Hunahpu)", "deity_cn": "玉米神（匈胡納浦）",
        "animal": "Lizard / Corn", "animal_cn": "蜥蜴 / 玉米穗",
        "personality_cn": "豐盛、慷慨、充滿生命力。如種子般蘊含無盡潛能，在適當時機爆發成長。",
        "personality_en": "Abundant, generous, full of vitality. Like a seed containing infinite potential, bursting forth at the right moment.",
        "destiny_cn": "你是豐盛的種子，被宇宙埋在大地中。你的成長滋養了所有人，你的給予是真正的神聖祭品。",
        "destiny_en": "You are a seed of abundance planted by the cosmos. Your growth nourishes everyone; your giving is a sacred offering.",
        "mythology_cn": "K'an 是玉米神的化身，代表生命、豐收與文明的基礎。瑪雅人相信第三代人類是玉米麵糰所造。",
        "mythology_en": "K'an embodies the Corn God, representing life, harvest, and civilization's foundation. Maya believed the third generation of humanity was made of maize dough.",
    },
    {
        "index": 4,
        "name": "Chikchan",
        "name_cn": "契查恩",
        "name_en": "Serpent / Sky Serpent",
        "glyph_emoji": "🐍",
        "element": "water", "element_cn": "水",
        "direction": "east", "direction_cn": "東",
        "color": "#2d6b2d",
        "deity": "Kukulkan (Feathered Serpent)", "deity_cn": "庫庫爾坎（羽蛇神）",
        "animal": "Feathered Serpent", "animal_cn": "羽蛇",
        "personality_cn": "強大的生命力與魅力，天生的領導者。能感知宇宙的脈動，具強烈的使命感。",
        "personality_en": "Powerful life force and charisma, natural leader. Can sense cosmic rhythms, with a strong sense of mission.",
        "destiny_cn": "你是宇宙生命之蛇，連結天地兩界。你的靈魂沿著生命螺旋上升，每個循環都帶來更深的智慧。",
        "destiny_en": "You are the cosmic life serpent, connecting heaven and earth. Your soul spirals upward, each cycle bringing deeper wisdom.",
        "mythology_cn": "契查恩是天空中的羽蛇，代表宇宙生命力的流動。瑪雅人以羽蛇神儀式喚醒昆達里尼能量，完成靈魂的蛻變。",
        "mythology_en": "Chikchan is the celestial feathered serpent, representing the flow of cosmic life force. Maya rituals to the feathered serpent awakened kundalini energy for soul transformation.",
    },
    {
        "index": 5,
        "name": "Kimi",
        "name_cn": "基米",
        "name_en": "Death / Transformation",
        "glyph_emoji": "💀",
        "element": "air", "element_cn": "風",
        "direction": "north", "direction_cn": "北",
        "color": "#5a5a5a",
        "deity": "Ah Puch / Kisin", "deity_cn": "阿普奇（死亡之神）",
        "animal": "Owl", "animal_cn": "貓頭鷹（死亡使者）",
        "personality_cn": "深刻理解無常，能從逝去中看見重生。不懼死亡，能以超然視角審視生命本質。",
        "personality_en": "Deep understanding of impermanence, seeing rebirth in endings. Fearless before death, with a transcendent view of life's essence.",
        "destiny_cn": "你是轉化的大師。每一次結束都是你的重生時刻，祖先的智慧流淌在你的血脈中，引導你穿越生死之門。",
        "destiny_en": "You are a master of transformation. Every ending is your rebirth, ancestral wisdom flowing in your veins, guiding you through the gates of life and death.",
        "mythology_cn": "基米代表希巴巴（冥界）的死亡之神。在瑪雅神話中，死亡不是終結，而是進入地下世界的旅程，是靈魂轉化的必要階段。",
        "mythology_en": "Kimi represents the death god of Xibalba (the underworld). In Maya myth, death is not an end but a journey into the underworld — a necessary stage of soul transformation.",
    },
    {
        "index": 6,
        "name": "Manik'",
        "name_cn": "瑪尼克",
        "name_en": "Deer / Hand",
        "glyph_emoji": "🦌",
        "element": "earth", "element_cn": "地",
        "direction": "west", "direction_cn": "西",
        "color": "#8b6914",
        "deity": "Deer God", "deity_cn": "鹿神",
        "animal": "Deer", "animal_cn": "鹿",
        "personality_cn": "優雅、善良、具天然的治癒能力。尊重生命中的一切神聖，是靈魂的引導者。",
        "personality_en": "Graceful, kind, with natural healing abilities. Respects the sacred in all life; a guide of souls.",
        "destiny_cn": "你的手握有神聖的治癒力量。如鹿般優雅穿行於世間，你帶來和平、豐收與神明的祝福。",
        "destiny_en": "Your hands hold sacred healing power. Moving through the world with deer-like grace, you bring peace, abundance, and divine blessing.",
        "mythology_cn": "瑪尼克的手符號代表神的賜予。鹿是瑪雅神話中的聖物，象徵太陽的光芒投射在大地上，是狩獵之神的化身。",
        "mythology_en": "Manik's hand symbol represents divine giving. The deer is sacred in Maya myth, symbolizing sunlight cast upon the earth — an incarnation of the hunt god.",
    },
    {
        "index": 7,
        "name": "Lamat",
        "name_cn": "拉瑪特",
        "name_en": "Rabbit / Venus Star",
        "glyph_emoji": "⭐",
        "element": "fire", "element_cn": "火",
        "direction": "south", "direction_cn": "南",
        "color": "#c8a800",
        "deity": "Venus God (Lahun Chan)", "deity_cn": "金星神（拉洪查恩）",
        "animal": "Rabbit / Venus", "animal_cn": "兔子 / 金星",
        "personality_cn": "和諧、歡樂、充滿創意。天生對美與藝術有強烈感知，善於製造和諧氛圍。",
        "personality_en": "Harmonious, joyful, full of creativity. Naturally gifted for beauty and art, skilled at creating harmony.",
        "destiny_cn": "你是金星的孩子，帶著宇宙的和諧頻率而生。你的使命是在衝突中建立美麗的橋梁。",
        "destiny_en": "You are a child of Venus, born with the harmonic frequency of the cosmos. Your mission is to build beautiful bridges amid conflict.",
        "mythology_cn": "拉瑪特是金星的象徵，亦代表兔子月神。瑪雅人精確追蹤金星週期（584天），將其與戰爭和命運緊密相連。",
        "mythology_en": "Lamat symbolizes Venus and also the Rabbit Moon God. Maya astronomers precisely tracked Venus cycles (584 days), linking them to war and destiny.",
    },
    {
        "index": 8,
        "name": "Muluk",
        "name_cn": "穆魯克",
        "name_en": "Water / Rain",
        "glyph_emoji": "💧",
        "element": "water", "element_cn": "水",
        "direction": "east", "direction_cn": "東",
        "color": "#1a5276",
        "deity": "Chaak (Rain God)", "deity_cn": "查克（雨神）",
        "animal": "Shark / Rain", "animal_cn": "鯊魚 / 雨",
        "personality_cn": "情感豐富、富有同情心、具強大的靈性感知。如水一般能適應一切，滋養生命。",
        "personality_en": "Emotionally rich, compassionate, with powerful spiritual perception. Adaptable like water, nourishing life.",
        "destiny_cn": "你承載著神聖的雨水——情感、淨化與奉獻的象徵。透過你的犧牲，宇宙循環得以延續。",
        "destiny_en": "You carry sacred rainwater — symbol of emotion, purification, and offering. Through your sacrifice, the cosmic cycle continues.",
        "mythology_cn": "穆魯克代表查克雨神，其儀式性供品確保雨水豐沛。水在瑪雅文明中是最珍貴的聖物，象徵靈魂流動的能力。",
        "mythology_en": "Muluk represents Chaak the Rain God, whose ritual offerings ensure rainfall. Water was the most sacred element in Maya civilization, symbolizing the soul's capacity to flow.",
    },
    {
        "index": 9,
        "name": "Ok",
        "name_cn": "歐克",
        "name_en": "Dog / Guide",
        "glyph_emoji": "🐕",
        "element": "air", "element_cn": "風",
        "direction": "north", "direction_cn": "北",
        "color": "#7d6b4a",
        "deity": "Dog Guide God", "deity_cn": "引路狗神",
        "animal": "Dog", "animal_cn": "狗",
        "personality_cn": "忠誠、正直、具強烈的正義感。天生的引導者，能在混沌中找到正確方向。",
        "personality_en": "Loyal, upright, with a strong sense of justice. A natural guide who finds the right path in chaos.",
        "destiny_cn": "你是死者靈魂通往來世的引路人。你的忠誠是宇宙的法則，你的愛是超越時空的守護。",
        "destiny_en": "You are a guide leading souls to the afterlife. Your loyalty is cosmic law; your love is protection beyond space and time.",
        "mythology_cn": "在瑪雅神話中，狗是靈魂穿越地下世界的嚮導。它引導死者越過九層地下世界，是最忠實的宇宙守護者。",
        "mythology_en": "In Maya myth, the dog guides souls through the underworld. It leads the dead through nine levels of Xibalba — the most faithful of cosmic guardians.",
    },
    {
        "index": 10,
        "name": "Chuwen",
        "name_cn": "丘文",
        "name_en": "Monkey / Thread of Time",
        "glyph_emoji": "🐒",
        "element": "earth", "element_cn": "地",
        "direction": "west", "direction_cn": "西",
        "color": "#8b4513",
        "deity": "Howler Monkey Scribes", "deity_cn": "吼猴書寫神",
        "animal": "Spider Monkey", "animal_cn": "蜘蛛猴",
        "personality_cn": "創意無限、喜歡遊戲、天生的藝術家與說故事者。以幽默與創造力編織生命的故事。",
        "personality_en": "Boundlessly creative, playful, natural artist and storyteller. Weaving life's story with humor and creativity.",
        "destiny_cn": "你是時間的編織者，以創意之線將過去、現在與未來串連。你的使命是透過藝術讓靈魂自由。",
        "destiny_en": "You are a weaver of time, threading past, present, and future with creative filaments. Your mission is to free souls through art.",
        "mythology_cn": "丘文代表吼猴雙神——瑪雅的藝術與書寫之神。他們是《波波爾烏》史詩中赫那普（Hunahpu）的同父異母兄弟，代表藝術創作的神聖起源。",
        "mythology_en": "Chuwen represents the Howler Monkey Twins — Maya gods of arts and writing. In the Popol Vuh epic, they are Hunahpu's half-brothers, embodying the divine origin of artistic creation.",
    },
    {
        "index": 11,
        "name": "Eb",
        "name_cn": "埃布",
        "name_en": "Road / Offering",
        "glyph_emoji": "🛤️",
        "element": "fire", "element_cn": "火",
        "direction": "south", "direction_cn": "南",
        "color": "#4a7c4e",
        "deity": "Road Deity", "deity_cn": "道路女神",
        "animal": "Human / Grass", "animal_cn": "人 / 草",
        "personality_cn": "服務導向、謙遜、具強烈的社群意識。願意為他人付出，在平凡中找到神聖。",
        "personality_en": "Service-oriented, humble, with strong community spirit. Willing to give for others, finding the sacred in the ordinary.",
        "destiny_cn": "你走在神聖的白色道路（Sacbe）上，連結各個神廟。你的服務是對宇宙最崇高的奉獻。",
        "destiny_en": "You walk the sacred white road (Sacbe) connecting temples. Your service is the most sublime offering to the cosmos.",
        "mythology_cn": "埃布代表瑪雅白色道路（薩克貝）——連結城市與神廟的神聖通道。這條路也象徵靈魂返回天界的旅途。",
        "mythology_en": "Eb represents the Maya white road (Sacbe) — the sacred causeway connecting cities and temples. This road also symbolizes the soul's journey back to the heavens.",
    },
    {
        "index": 12,
        "name": "Ben",
        "name_cn": "本",
        "name_en": "Reed / Corn Stalk",
        "glyph_emoji": "🌾",
        "element": "water", "element_cn": "水",
        "direction": "east", "direction_cn": "東",
        "color": "#2e8b57",
        "deity": "Corn Stalk God", "deity_cn": "玉米稈神",
        "animal": "Reed / Corn Stalk", "animal_cn": "蘆葦 / 玉米稈",
        "personality_cn": "具領導才能、原則性強、能建立持久的秩序。如蘆葦般強韌，風中搖曳卻不折斷。",
        "personality_en": "Leadership talent, strong principles, able to establish lasting order. Resilient as a reed — swaying in the wind but never breaking.",
        "destiny_cn": "你是宇宙的脊梁，連結大地與天空。你的使命是建立真正的秩序，以正義為基礎創造神聖的結構。",
        "destiny_en": "You are the cosmic spine connecting earth and sky. Your mission is to establish true order, creating sacred structures founded on justice.",
        "mythology_cn": "本代表的蘆葦是瑪雅神廟建築的基本材料，亦象徵人體的脊椎——連結大地與星空的宇宙軸心。",
        "mythology_en": "Ben's reed is a foundational building material in Maya temples, also symbolizing the human spine — the cosmic axis connecting earth and sky.",
    },
    {
        "index": 13,
        "name": "Ix",
        "name_cn": "伊克斯",
        "name_en": "Jaguar / Earth Magic",
        "glyph_emoji": "🐆",
        "element": "air", "element_cn": "風",
        "direction": "north", "direction_cn": "北",
        "color": "#6b3a8b",
        "deity": "Jaguar God of the Underworld", "deity_cn": "地下世界美洲豹神",
        "animal": "Jaguar", "animal_cn": "美洲豹",
        "personality_cn": "神秘、強大、具薩滿能力。能在不同意識層次之間自由穿行，是靈界與現實的橋梁。",
        "personality_en": "Mysterious, powerful, with shamanic abilities. Freely moves between different consciousness levels — a bridge between spirit and reality.",
        "destiny_cn": "你是大地魔法的守護者。美洲豹的斑點是宇宙星辰的印記，你的靈魂攜帶著宇宙最古老的知識。",
        "destiny_en": "You are guardian of earth magic. The jaguar's spots are the marks of cosmic stars — your soul carries the oldest cosmic knowledge.",
        "mythology_cn": "伊克斯代表在地下世界奔馳的美洲豹太陽神，其斑點象徵夜空中的星星。薩滿祭司以美洲豹皮為法袍，代表對地球神秘力量的掌控。",
        "mythology_en": "Ix represents the Jaguar Sun God racing through the underworld, whose spots symbolize night stars. Shamans wore jaguar skins as vestments, representing mastery of earth's mysterious forces.",
    },
    {
        "index": 14,
        "name": "Men",
        "name_cn": "門",
        "name_en": "Eagle / Higher Mind",
        "glyph_emoji": "🦅",
        "element": "earth", "element_cn": "地",
        "direction": "west", "direction_cn": "西",
        "color": "#b8860b",
        "deity": "Moon Goddess (Ix Chel)", "deity_cn": "月神（伊克斯切爾）",
        "animal": "Eagle", "animal_cn": "老鷹",
        "personality_cn": "視野開闊、追求完美、具強烈的個人目標。能從高處俯瞰全局，以智慧指引方向。",
        "personality_en": "Broad vision, pursues perfection, with strong personal goals. Can view the whole from above, guiding with wisdom.",
        "destiny_cn": "你有老鷹的眼睛，能看見他人無法看見的未來。你的使命是翱翔於更高的智慧境界，將天界的知識帶回人間。",
        "destiny_en": "You have eagle's eyes, seeing futures others cannot. Your mission is to soar to higher wisdom realms, bringing celestial knowledge back to humanity.",
        "mythology_cn": "門代表老鷹，是瑪雅月神伊克斯切爾的聖鳥。月神主宰醫藥、生育與編織，老鷹則是連結月亮與地球的神聖使者。",
        "mythology_en": "Men represents the eagle, sacred bird of Maya Moon Goddess Ix Chel. The Moon Goddess governs medicine, fertility, and weaving; the eagle is the divine messenger connecting moon and earth.",
    },
    {
        "index": 15,
        "name": "Kib",
        "name_cn": "基布",
        "name_en": "Warrior / Wax / Owl",
        "glyph_emoji": "🦉",
        "element": "fire", "element_cn": "火",
        "direction": "south", "direction_cn": "南",
        "color": "#8b7355",
        "deity": "Earth Lord / Earthly Fire", "deity_cn": "地主神 / 大地之火",
        "animal": "Owl / Vulture", "animal_cn": "貓頭鷹 / 禿鷲",
        "personality_cn": "古老智慧的承載者，具豐富的閱歷與深刻的洞見。能從業力中學習，以智慧化解困境。",
        "personality_en": "Carrier of ancient wisdom, rich in experience and deep insight. Learns from karma, resolving difficulties with wisdom.",
        "destiny_cn": "你的靈魂積累了無數世的智慧與業力。你的使命是以深刻的理解超越因果，為後代照亮道路。",
        "destiny_en": "Your soul has accumulated wisdom and karma from countless lifetimes. Your mission is to transcend cause and effect with deep understanding, illuminating the path for future generations.",
        "mythology_cn": "基布代表靈魂從業力中解脫的能力，亦與蠟燭（蜂蠟）儀式相關——在黑暗中以小小的光守護神聖空間。",
        "mythology_en": "Kib represents the soul's ability to liberate itself from karma, and is linked to beeswax candle rituals — guarding sacred space with a small light in the darkness.",
    },
    {
        "index": 16,
        "name": "Kaban",
        "name_cn": "卡班",
        "name_en": "Earth / Movement / Thought",
        "glyph_emoji": "🌍",
        "element": "water", "element_cn": "水",
        "direction": "east", "direction_cn": "東",
        "color": "#228b22",
        "deity": "Earth Goddess (Ix Chel)", "deity_cn": "大地女神",
        "animal": "Earth / Brain", "animal_cn": "大地 / 腦波",
        "personality_cn": "思維敏銳、充滿創意、擁有強大的分析能力。與地球的脈動同步，能感知集體意識的動向。",
        "personality_en": "Sharp-minded, creative, powerful analytical ability. Synchronized with Earth's pulse, able to sense collective consciousness movements.",
        "destiny_cn": "你是地球智慧的接收器，宇宙的思維透過你流動。你的洞察力能改變世界的走向。",
        "destiny_en": "You are a receiver of Earth's wisdom; cosmic thought flows through you. Your insight can change the direction of the world.",
        "mythology_cn": "卡班代表大地的意識與震動，亦象徵人類大腦的思考能力。瑪雅人相信地球是有意識的生命體，與人類大腦以神聖頻率共振。",
        "mythology_en": "Kaban represents Earth's consciousness and vibration, also symbolizing the human brain's thinking capacity. Maya believed Earth was a conscious being resonating with the human brain at sacred frequencies.",
    },
    {
        "index": 17,
        "name": "Etz'nab",
        "name_cn": "埃茲納布",
        "name_en": "Flint / Obsidian Mirror",
        "glyph_emoji": "🗡️",
        "element": "air", "element_cn": "風",
        "direction": "north", "direction_cn": "北",
        "color": "#c0c0c0",
        "deity": "Lightning God / Flint God", "deity_cn": "閃電神 / 燧石神",
        "animal": "Flint / Mirror", "animal_cn": "燧石刀 / 黑曜石鏡",
        "personality_cn": "銳利、誠實、能看透謊言。如黑曜石鏡般反映真相，有時犀利得令人不舒服。",
        "personality_en": "Sharp, honest, able to see through lies. Like an obsidian mirror reflecting truth — sometimes uncomfortably so.",
        "destiny_cn": "你是宇宙的手術刀，切除不再需要的一切。你的犧牲帶來純淨，你的誠實是最高形式的慈悲。",
        "destiny_en": "You are the cosmic scalpel, cutting away what is no longer needed. Your sacrifice brings purification; your honesty is the highest form of compassion.",
        "mythology_cn": "埃茲納布是黑曜石刀，用於神聖儀式的獻祭。黑曜石鏡是薩滿預言的工具，是通往神界的窗口。",
        "mythology_en": "Etz'nab is the obsidian blade used in sacred sacrificial rituals. The obsidian mirror is a shamanic divination tool — a window to the divine realm.",
    },
    {
        "index": 18,
        "name": "Kawak",
        "name_cn": "卡瓦克",
        "name_en": "Storm / Thunder",
        "glyph_emoji": "⛈️",
        "element": "earth", "element_cn": "地",
        "direction": "west", "direction_cn": "西",
        "color": "#4a6fa5",
        "deity": "Storm God / Tlaloc", "deity_cn": "風暴神 / 查克",
        "animal": "Storm Cloud / Turtle", "animal_cn": "風暴雲 / 烏龜",
        "personality_cn": "充滿能量、喜歡團隊合作、具強大的轉化能力。如暴風雨般清潔舊有模式，迎接新的開始。",
        "personality_en": "Full of energy, enjoys teamwork, powerful transformative ability. Like a storm clearing old patterns to welcome new beginnings.",
        "destiny_cn": "你是宇宙的淨化之雨，洗去陳舊的傷痛與局限。透過你的轉化力，集體靈魂得以更新。",
        "destiny_en": "You are the cosmos's purifying rain, washing away old wounds and limitations. Through your transformative power, the collective soul is renewed.",
        "mythology_cn": "卡瓦克代表神聖的風暴，是查克雨神顯現力量的時刻。烏龜背上的雨水象徵豐收的祝福從天而降。",
        "mythology_en": "Kawak represents the sacred storm, the moment when Chaak the Rain God manifests his power. Rain on the turtle's back symbolizes harvest blessings descending from heaven.",
    },
    {
        "index": 19,
        "name": "Ajaw",
        "name_cn": "阿哈瓦",
        "name_en": "Sun Lord / Flower",
        "glyph_emoji": "☀️",
        "element": "fire", "element_cn": "火",
        "direction": "south", "direction_cn": "南",
        "color": "#ff8c00",
        "deity": "Kinich Ahau (Sun God)", "deity_cn": "基尼奇阿豪（太陽神）",
        "animal": "Sun / Flower", "animal_cn": "太陽 / 花朵",
        "personality_cn": "光明、慷慨、具王者氣質。天生的領袖，以愛與智慧照耀他人，是周遭所有人的中心。",
        "personality_en": "Radiant, generous, with regal bearing. A natural leader illuminating others with love and wisdom — the center of all around them.",
        "destiny_cn": "你是太陽的孩子，承載著宇宙最高的光輝。你的生命是一首讚美詩，呼喚所有靈魂覺醒到自身的神聖。",
        "destiny_en": "You are a child of the Sun, carrying the cosmos's highest radiance. Your life is a hymn of praise, calling all souls to awaken to their own divinity.",
        "mythology_cn": "阿哈瓦是瑪雅曆法中最尊貴的日符號，代表太陽神基尼奇阿豪。在 Tzolk'in 輪迴中，Ajaw 是結束與完成的象徵，也是新循環開始前的神聖頂點。",
        "mythology_en": "Ajaw is the most honored day sign in the Maya calendar, representing Sun God Kinich Ahau. In the Tzolk'in cycle, Ajaw symbolizes endings and completion — the sacred apex before a new cycle begins.",
    },
]

# ============================================================
# Tzolk'in 十三神聖數字 (13 Sacred Numbers)
# ============================================================

TZOLKIN_NUMBERS = [
    {
        "number": 1, "name_cn": "統一", "name_en": "Unity",
        "tone_cn": "磁性調", "tone_en": "Magnetic Tone",
        "meaning_cn": "新的開始，吸引力，目標設定。一切可能性的種子。",
        "meaning_en": "New beginnings, magnetic attraction, setting purpose. The seed of all possibilities.",
    },
    {
        "number": 2, "name_cn": "雙元", "name_en": "Duality",
        "tone_cn": "月亮調", "tone_en": "Lunar Tone",
        "meaning_cn": "極性，挑戰，選擇。在光與暗之間找到平衡的智慧。",
        "meaning_en": "Polarity, challenge, choice. Wisdom of finding balance between light and dark.",
    },
    {
        "number": 3, "name_cn": "節奏", "name_en": "Rhythm",
        "tone_cn": "電能調", "tone_en": "Electric Tone",
        "meaning_cn": "激活，連結服務。三位一體的力量，將想法化為行動。",
        "meaning_en": "Activation, bonding in service. Trinitarian power transforming ideas into action.",
    },
    {
        "number": 4, "name_cn": "穩定", "name_en": "Stability",
        "tone_cn": "自存調", "tone_en": "Self-Existing Tone",
        "meaning_cn": "形式，度量，定義。為夢想建立具體基礎的力量。",
        "meaning_en": "Form, measure, definition. Power to build concrete foundations for dreams.",
    },
    {
        "number": 5, "name_cn": "輝耀", "name_en": "Radiance",
        "tone_cn": "超音調", "tone_en": "Overtone Tone",
        "meaning_cn": "掌控，光芒，中心。全然展現自身力量的命令式能量。",
        "meaning_en": "Command, radiance, center. Commanding energy that fully manifests one's power.",
    },
    {
        "number": 6, "name_cn": "均衡", "name_en": "Balance",
        "tone_cn": "節奏調", "tone_en": "Rhythmic Tone",
        "meaning_cn": "組織，平衡，和諧。以優雅的節奏協調一切矛盾。",
        "meaning_en": "Organization, balance, equality. Coordinating all contradictions with elegant rhythm.",
    },
    {
        "number": 7, "name_cn": "共鳴", "name_en": "Resonance",
        "tone_cn": "共鳴調", "tone_en": "Resonant Tone",
        "meaning_cn": "靈感，神秘校準，管道。Tzolk'in 中最具靈性力量的神聖數字。",
        "meaning_en": "Inspiration, mystical attunement, channeling. The most spiritually powerful sacred number in Tzolk'in.",
    },
    {
        "number": 8, "name_cn": "和諧", "name_en": "Harmony",
        "tone_cn": "銀河調", "tone_en": "Galactic Tone",
        "meaning_cn": "整合，誠信，示範。銀河系頻率的入口，誠信是最高法則。",
        "meaning_en": "Integration, integrity, modeling. Gateway to galactic frequencies; integrity is the highest law.",
    },
    {
        "number": 9, "name_cn": "完成", "name_en": "Completion",
        "tone_cn": "太陽調", "tone_en": "Solar Tone",
        "meaning_cn": "意圖，脈動，實現。九是循環完成的數字，意圖化為現實的時刻。",
        "meaning_en": "Intention, pulsing, realization. Nine completes the cycle; the moment intention becomes reality.",
    },
    {
        "number": 10, "name_cn": "顯化", "name_en": "Manifestation",
        "tone_cn": "行星調", "tone_en": "Planetary Tone",
        "meaning_cn": "完美展現，製造，生產。在物質世界中完美體現靈性意圖。",
        "meaning_en": "Perfect manifestation, production, production. Perfectly embodying spiritual intention in the material world.",
    },
    {
        "number": 11, "name_cn": "解脫", "name_en": "Liberation",
        "tone_cn": "光譜調", "tone_en": "Spectral Tone",
        "meaning_cn": "釋放，溶解，解放。從舊有束縛中解放的必要蛻變。",
        "meaning_en": "Release, dissolve, liberation. Necessary transformation liberating from old constraints.",
    },
    {
        "number": 12, "name_cn": "合作", "name_en": "Cooperation",
        "tone_cn": "水晶調", "tone_en": "Crystal Tone",
        "meaning_cn": "普世化，合作，分享。在社群中找到個人使命的最高形式。",
        "meaning_en": "Universalizing, cooperation, sharing. The highest form of finding personal mission within community.",
    },
    {
        "number": 13, "name_cn": "超越", "name_en": "Transcendence",
        "tone_cn": "宇宙調", "tone_en": "Cosmic Tone",
        "meaning_cn": "超越，宇宙意識，無限存在。Tzolk'in 循環的最後一個數字，代表無限擴展的宇宙意識。",
        "meaning_en": "Transcendence, cosmic consciousness, infinite presence. The final number of the Tzolk'in cycle, representing infinitely expanding cosmic consciousness.",
    },
]

# ============================================================
# Long Count 週期詮釋 (Long Count Period Interpretations)
# ============================================================

LONG_COUNT_PERIOD_MEANINGS = {
    "kin": {
        "name_cn": "K'in（一日）", "name_en": "K'in (1 Day)",
        "days": 1,
        "meaning_cn": "最基本的時間單位，象徵太陽的單次旅程。每一天都是一個完整的宇宙循環。",
        "meaning_en": "The most basic unit of time, symbolizing the Sun's single journey. Each day is a complete cosmic cycle.",
    },
    "winal": {
        "name_cn": "Winal（二十日）", "name_en": "Winal (20 Days)",
        "days": 20,
        "meaning_cn": "二十天週期，對應人體的二十根手指腳趾，是瑪雅計數系統的基礎。",
        "meaning_en": "A 20-day period corresponding to the human body's twenty fingers and toes — the basis of the Maya vigesimal counting system.",
    },
    "tun": {
        "name_cn": "Tun（360日）", "name_en": "Tun (360 Days ≈ 1 Year)",
        "days": 360,
        "meaning_cn": "近似一個太陽年。是個人與集體命運的基本週期，代表一個完整的生命季節。",
        "meaning_en": "Approximating one solar year. The basic cycle for personal and collective destiny, representing a complete life season.",
    },
    "katun": {
        "name_cn": "K'atun（7,200日 ≈ 20年）", "name_en": "K'atun (7,200 Days ≈ 20 Years)",
        "days": 7200,
        "meaning_cn": "約二十年的命運週期。瑪雅預言書《奇蘭巴蘭》以K'atun為單位記錄王朝命運，每個K'atun都有特定的時代主題。",
        "meaning_en": "A ~20-year destiny cycle. The Maya prophetic book Chilam Balam records dynastic fates by K'atun; each K'atun has a specific era theme.",
    },
    "baktun": {
        "name_cn": "B'ak'tun（144,000日 ≈ 394年）", "name_en": "B'ak'tun (144,000 Days ≈ 394 Years)",
        "days": 144000,
        "meaning_cn": "約四百年的文明時代週期。2012年12月21日（13.0.0.0.0）是第13個B'ak'tun的結束，標誌著一個偉大世界時代的轉換。",
        "meaning_en": "A ~400-year cycle of civilizational eras. Dec 21, 2012 (13.0.0.0.0) marked the end of the 13th B'ak'tun — a transition of a great world age.",
    },
    "piktun": {
        "name_cn": "Piktun（2,880,000日 ≈ 7,885年）", "name_en": "Piktun (2,880,000 Days ≈ 7,885 Years)",
        "days": 2880000,
        "meaning_cn": "超越單一文明的宇宙時代。代表人類在這個星球上演化的巨大週期。",
        "meaning_en": "A cosmic era transcending individual civilizations. Represents the grand cycle of human evolution on this planet.",
    },
}

# 當前 Baktun 13 的 Katun 主題 (Current Baktun 13 Katun Themes)
KATUN_THEMES = {
    0:  {"cn": "K'atun 0 — 重建時代：文明秩序的重新建立，舊規則消亡，新秩序誕生。",
         "en": "K'atun 0 — Era of Rebuilding: Re-establishment of civilizational order; old rules die, new order is born."},
    1:  {"cn": "K'atun 1 — 轉化時代：深刻的個人與集體轉化，靈魂在危機中覺醒。",
         "en": "K'atun 1 — Era of Transformation: Profound personal and collective transformation; souls awaken in crisis."},
    2:  {"cn": "K'atun 2 — 統一時代：對立面尋求融合，和解與整合的時代。",
         "en": "K'atun 2 — Era of Unity: Opposites seek merger; an age of reconciliation and integration."},
    3:  {"cn": "K'atun 3 — 創造時代：藝術、科技與靈性的爆炸性創新時代。",
         "en": "K'atun 3 — Era of Creation: Explosive innovation in arts, technology, and spirituality."},
    4:  {"cn": "K'atun 4 — 奠基時代：社會基礎設施的重建，長遠規劃的時代。",
         "en": "K'atun 4 — Era of Foundation: Rebuilding societal infrastructure; an age of long-term planning."},
    5:  {"cn": "K'atun 5 — 擴張時代：邊界被打破，探索與發現的黃金時代。",
         "en": "K'atun 5 — Era of Expansion: Boundaries broken; golden age of exploration and discovery."},
    6:  {"cn": "K'atun 6 — 和諧時代：自然與人類的關係走向平衡與共生。",
         "en": "K'atun 6 — Era of Harmony: Nature and humanity move toward balance and symbiosis."},
    7:  {"cn": "K'atun 7 — 神秘時代：靈性覺醒加速，古老智慧重新浮現。",
         "en": "K'atun 7 — Era of Mystery: Spiritual awakening accelerates; ancient wisdom resurfaces."},
    8:  {"cn": "K'atun 8 — 覺知時代：集體意識提升，全球性問題浮上檯面。",
         "en": "K'atun 8 — Era of Awareness: Collective consciousness rises; global issues come to the forefront."},
    9:  {"cn": "K'atun 9 — 審判時代：業力清算，舊有不公平結構面臨瓦解。",
         "en": "K'atun 9 — Era of Judgment: Karmic reckoning; unjust old structures face dissolution."},
    10: {"cn": "K'atun 10 — 解放時代：從古老枷鎖中解放，新的自由意識誕生。",
         "en": "K'atun 10 — Era of Liberation: Liberation from ancient shackles; new freedom consciousness is born."},
    11: {"cn": "K'atun 11 — 智慧時代：古老知識與現代科技的融合，宇宙智慧開花結果。",
         "en": "K'atun 11 — Era of Wisdom: Ancient knowledge merges with modern technology; cosmic wisdom blooms."},
    12: {"cn": "K'atun 12 — 完成時代：一個大週期走向完結，為下一個新世界做準備。",
         "en": "K'atun 12 — Era of Completion: A great cycle approaches its end; preparing for the next new world."},
    13: {"cn": "K'atun 13 — 誕生時代：嶄新世界時代的黎明，宇宙的重新創造。",
         "en": "K'atun 13 — Era of Birth: Dawn of a brand new world age; cosmic re-creation."},
    14: {"cn": "K'atun 14 — 開拓時代：新疆域的探索，先驅精神引領時代。",
         "en": "K'atun 14 — Era of Pioneering: Exploration of new frontiers; pioneer spirit leads the age."},
    15: {"cn": "K'atun 15 — 整合時代：不同系統與文化的大融合時代。",
         "en": "K'atun 15 — Era of Integration: Grand fusion of diverse systems and cultures."},
    16: {"cn": "K'atun 16 — 記憶時代：集體記憶被喚醒，祖先智慧重現。",
         "en": "K'atun 16 — Era of Memory: Collective memory awakened; ancestral wisdom reappears."},
    17: {"cn": "K'atun 17 — 淨化時代：大規模的清理與更新，為新時代奠定清潔的基礎。",
         "en": "K'atun 17 — Era of Purification: Large-scale cleansing and renewal; laying a clean foundation for the new age."},
    18: {"cn": "K'atun 18 — 先知時代：靈視能力大幅提升，人類重新連結宇宙意識。",
         "en": "K'atun 18 — Era of Prophecy: Visionary capacity greatly enhanced; humanity reconnects with cosmic consciousness."},
    19: {"cn": "K'atun 19 — 黃金時代：文明達到頂峰，靈性與物質的完美和諧。",
         "en": "K'atun 19 — Era of Gold: Civilization reaches its peak; perfect harmony of spirit and matter."},
}

# ============================================================
# 重要歷史 Long Count 日期 (Important Historical Long Count Dates)
# ============================================================

HISTORICAL_LONG_COUNT_EVENTS = [
    {
        "long_count": "0.0.0.0.0",
        "gregorian": "Aug 11, 3114 BCE",
        "event_cn": "瑪雅創世紀元開始——第四太陽的誕生",
        "event_en": "Maya Creation Era begins — Birth of the Fourth Sun",
        "category": "creation",
    },
    {
        "long_count": "8.17.0.0.0",
        "gregorian": "Sep 8, 159 BCE",
        "event_cn": "佩騰地區早期瑪雅文明崛起",
        "event_en": "Early Maya civilization rises in the Petén region",
        "category": "civilization",
    },
    {
        "long_count": "9.0.0.0.0",
        "gregorian": "Dec 9, 435 CE",
        "event_cn": "瑪雅古典期開始，偉大城邦興盛",
        "event_en": "Maya Classic Period begins; great city-states flourish",
        "category": "civilization",
    },
    {
        "long_count": "9.8.9.13.0",
        "gregorian": "Apr 17, 603 CE",
        "event_cn": "帕倫克王朝帕卡爾一世登基",
        "event_en": "King Pakal I ascends the throne of Palenque",
        "category": "royalty",
    },
    {
        "long_count": "9.12.11.5.18",
        "gregorian": "Aug 28, 683 CE",
        "event_cn": "帕倫克偉大國王帕卡爾升天，墓碑銘文記錄Long Count",
        "event_en": "Great King Pakal of Palenque ascends; sarcophagus lid records Long Count",
        "category": "royalty",
    },
    {
        "long_count": "9.13.0.0.0",
        "gregorian": "Mar 18, 692 CE",
        "event_cn": "科潘（Copán）天文觀測鼎盛期",
        "event_en": "Zenith of astronomical observation at Copán",
        "category": "astronomy",
    },
    {
        "long_count": "9.16.0.0.0",
        "gregorian": "May 9, 751 CE",
        "event_cn": "瑪雅城邦聯盟最盛期，奇琴伊察崛起",
        "event_en": "Peak of Maya city-state alliances; Chichén Itzá rises",
        "category": "civilization",
    },
    {
        "long_count": "10.0.0.0.0",
        "gregorian": "Oct 15, 830 CE",
        "event_cn": "瑪雅古典期衰落開始，南部低地城邦逐漸廢棄",
        "event_en": "Maya Classic Period begins declining; southern lowland cities gradually abandoned",
        "category": "decline",
    },
    {
        "long_count": "11.16.0.0.0",
        "gregorian": "Nov 3, 1539 CE",
        "event_cn": "西班牙征服尤卡坦半島完成，瑪雅文明遭到毀滅性衝擊",
        "event_en": "Spanish conquest of Yucatán complete; Maya civilization suffers devastating impact",
        "category": "conquest",
    },
    {
        "long_count": "12.19.19.17.19",
        "gregorian": "Dec 20, 2012 CE",
        "event_cn": "第13個B'ak'tun的最後一天",
        "event_en": "Last day of the 13th B'ak'tun",
        "category": "transition",
    },
    {
        "long_count": "13.0.0.0.0",
        "gregorian": "Dec 21, 2012 CE",
        "event_cn": "新的B'ak'tun週期開始——第五太陽新紀元",
        "event_en": "New B'ak'tun cycle begins — New Era of the Fifth Sun",
        "category": "transition",
    },
    {
        "long_count": "13.0.11.4.1",
        "gregorian": "Jan 1, 2020 CE",
        "event_cn": "新的十年開始，全球性轉化加速",
        "event_en": "New decade begins; global transformation accelerates",
        "category": "modern",
    },
    {
        "long_count": "13.0.13.0.3",
        "gregorian": "Jan 1, 2025 CE",
        "event_cn": "新的K'atun 13時代，全球意識重塑期",
        "event_en": "New K'atun 13 era; global consciousness reshaping",
        "category": "modern",
    },
]

# ============================================================
# 金星週期 (Venus Cycle — 584 Days)
# ============================================================

VENUS_CYCLE_DAYS = 584  # Venus synodic period

VENUS_PHASES = [
    {"phase": "morning_star", "duration_days": 263,
     "name_cn": "晨星（明星）", "name_en": "Morning Star (Great Star)",
     "meaning_cn": "金星作為晨星升起——勇士的出現，力量與征服的時刻。瑪雅戰爭往往在晨星升起時發動。",
     "meaning_en": "Venus rises as morning star — warrior's emergence, moment of power and conquest. Maya wars were often launched at morning star rise."},
    {"phase": "superior_conjunction", "duration_days": 50,
     "name_cn": "上合（隱沒於日後）", "name_en": "Superior Conjunction (Hidden after Sun)",
     "meaning_cn": "金星消失於太陽後方——神祇降入天堂深處，蛻變與重生的神秘時期。",
     "meaning_en": "Venus disappears behind the Sun — the deity descends into heaven's depths; a mysterious period of metamorphosis and rebirth."},
    {"phase": "evening_star", "duration_days": 263,
     "name_cn": "昏星（暮星）", "name_en": "Evening Star",
     "meaning_cn": "金星作為昏星出現——愛與美的女神顯現，創造力與靈感的時期。",
     "meaning_en": "Venus appears as evening star — goddess of love and beauty manifests; period of creativity and inspiration."},
    {"phase": "inferior_conjunction", "duration_days": 8,
     "name_cn": "下合（地下世界）", "name_en": "Inferior Conjunction (Underworld)",
     "meaning_cn": "金星最接近地球且短暫消失——神祇穿越地下世界的最深處，死亡與重生的關鍵時刻。",
     "meaning_en": "Venus closest to Earth and briefly vanishes — the deity passes through the underworld's deepest realm; critical moment of death and rebirth."},
]

# ============================================================
# 瑪雅行星 (Mayan Planets for Chart Calculation)
# ============================================================

MAYAN_PLANETS = {
    "Sun ☉ (太陽)":       swe.SUN,
    "Moon ☽ (月亮)":      swe.MOON,
    "Venus ♀ (金星)":     swe.VENUS,
    "Mars ♂ (火星)":      swe.MARS,
    "Jupiter ♃ (木星)":   swe.JUPITER,
    "Saturn ♄ (土星)":    swe.SATURN,
}

PLANET_COLORS = {
    "Sun ☉ (太陽)":       "#FFD700",
    "Moon ☽ (月亮)":      "#C0C0C0",
    "Venus ♀ (金星)":     "#228B22",
    "Mars ♂ (火星)":      "#DC143C",
    "Jupiter ♃ (木星)":   "#4169E1",
    "Saturn ♄ (土星)":    "#000080",
}

# 12 Western zodiac signs (tropical)
ZODIAC_SIGNS = [
    ("Aries",        "♈", "白羊座"),
    ("Taurus",       "♉", "金牛座"),
    ("Gemini",       "♊", "雙子座"),
    ("Cancer",       "♋", "巨蟹座"),
    ("Leo",          "♌", "獅子座"),
    ("Virgo",        "♍", "處女座"),
    ("Libra",        "♎", "天秤座"),
    ("Scorpio",      "♏", "天蠍座"),
    ("Sagittarius",  "♐", "射手座"),
    ("Capricorn",    "♑", "摩羯座"),
    ("Aquarius",     "♒", "水瓶座"),
    ("Pisces",       "♓", "雙魚座"),
]

# Legacy aliases (backward compatibility with old maya.py constants)
TZOLKIN_NAMES = [
    (d["index"], d["name"], d["name_cn"], d["glyph_emoji"])
    for d in TZOLKIN_DAY_DATA
]
HAAB_MONTHS = [
    ("Pop",    "POP",    "波普 (墊)",       "🟤"),
    ("Wo",     "WO",     "沃 (黑豹)",        "⚫"),
    ("Sip",    "SIP",    "西普 (鹿)",        "🦌"),
    ("Sotz",   "SOTZ",   "索茲 (蝙蝠)",      "🦇"),
    ("Sek",    "SEK",    "塞克 (骨)",        "🦴"),
    ("Xul",    "XUL",    "舒爾 (狗)",        "🐕"),
    ("Yaxkin", "YAXKIN", "亞克斯金 (新生)",  "🌱"),
    ("Mol",    "MOL",    "莫爾 (水)",        "💧"),
    ("Chen",   "CHEN",   "陳 (黑曜石)",      "⬛"),
    ("Yax",    "YAX",    "亞克斯 (新生)",    "🌿"),
    ("Sak",    "SAK",    "薩克 (白玉米)",    "⚪"),
    ("Keh",    "KEH",    "凱 (紅玉米)",      "🔴"),
    ("Mak",    "MAK",    "瑪克 (覆蓋)",      "🟫"),
    ("Kankin", "KANKIN", "坎金 (太陽)",      "☀️"),
    ("Muwan",  "MUWAN",  "穆萬 (貓頭鷹)",    "🦉"),
    ("Pax",    "PAX",    "帕克斯 (鼓)",      "🥁"),
    ("Kayab",  "KAYAB",  "卡亞布 (龜)",      "🐢"),
    ("Kumku",  "KUMKU",  "庫姆庫 (玉米)",    "🌽"),
    ("Wayeb",  "WAYEB",  "瓦耶布 (五無日)",  "🔥"),
]
TZOLKIN_ENERGIES = {d["index"]: d["name_cn"] for d in TZOLKIN_DAY_DATA}
