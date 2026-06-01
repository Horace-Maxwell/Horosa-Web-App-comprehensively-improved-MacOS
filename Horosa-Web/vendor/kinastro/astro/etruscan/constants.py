"""
astro/etruscan/constants.py — Constants for the Etruscan Astrology module
=========================================================================

Includes:
  • BRONZE_THEME       — UI colour palette (ancient bronze / parchment aesthetic)
  • TEMPLUM_16         — The 16 Templum regions of the Etruscan celestial division,
                         mapped clockwise from North (0°) in 22.5° sectors.
                         Based on the Piacenza Liver model and Martianus Capella's
                         description of the Etruscan sky-temple.
  • ETRUSCAN_PLANETS   — pyswisseph planet IDs mapped to Etruscan deity names
  • LIGHTNING_INTERPRETATIONS — Tinia's 9 thunderbolt types for fulguratores practice

References:
  van der Meer (1987) *The Bronze Liver of Piacenza*
  Turfa (2012) *Divining the Etruscan World*
  Martianus Capella, *De Nuptiis Philologiae et Mercurii* II.150–168
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# UI Theme — ancient bronze / dark parchment palette
# ─────────────────────────────────────────────────────────────────────────────

BRONZE_THEME: dict[str, str] = {
    "bg":           "#1A0F06",   # 深褐背景 / deep dark earth
    "bg_card":      "#2A1810",   # 卡片背景 / card background
    "gold":         "#D4AF37",   # 金青銅高光 / burnished gold highlight
    "bronze":       "#8C6F4E",   # 青銅本色 / raw bronze
    "dark_red":     "#9C2F2F",   # 凶兆暗紅 / inauspicious dark red
    "black_gold":   "#3A2A10",   # 深金底色 / dark gold undertone
    "border":       "#8C6F4E",   # 邊框 / border colour
    "header":       "#D4AF37",   # 標題色 / header colour
    "text":         "#E8DCC8",   # 正文色 / body text colour
    "favorable":    "#D4AF37",   # 吉祥色 / auspicious highlight
    "unfavorable":  "#9C2F2F",   # 凶兆色 / inauspicious highlight
    "neutral":      "#8C6F4E",   # 中性色 / neutral colour
}


# ─────────────────────────────────────────────────────────────────────────────
# Templum 16 Regions
# ─────────────────────────────────────────────────────────────────────────────
# 伊特魯里亞天宮16區，從正北(0°)順時針每22.5°一區
# The 16 Templum sectors follow the horizon from N→NNE→NE→… clockwise.
# Region 1 = 0°–22.5° (NNE), region 16 = 337.5°–360° (NNW).
#
# Sources: Martianus Capella's enumeration of Etruscan deities in 16 sky regions;
# van der Meer's reconstruction of the Piacenza Liver outer rim inscriptions.
# ─────────────────────────────────────────────────────────────────────────────

TEMPLUM_16: list[dict] = [
    {
        "region": 1,
        "name_etruscan": "Tin Cilens",
        "name_en": "Tinia of the Curses",
        "name_zh": "詛咒之廷尼亞",
        "deity_zh": "掌管詛咒雷霆的廷尼亞，天神最凶之相，降下毀滅性閃電",
        "deity_en": "Tinia in his cursing aspect, wielding the most destructive thunderbolts",
        "nature": "unfavorable",
        "nature_zh": "大凶",
        "thunder_type": "Mala fulmina — 惡雷",
        "azimuth_start": 0.0,
        "azimuth_end": 22.5,
        "color": "#7A1A1A",
        "interpretation_zh": "最凶之域，詛咒與毀滅。行星入此區，示重大災禍或不可逆轉之變局，慎之。",
        "interpretation_en": "Most inauspicious region of curses and destruction. Planets here warn of catastrophe or irreversible change.",
    },
    {
        "region": 2,
        "name_etruscan": "Tin Thvflthas",
        "name_en": "Tinia of the Counsellors",
        "name_zh": "議政之廷尼亞",
        "deity_zh": "廷尼亞之諮詢相，眾神議事，調解天意",
        "deity_en": "Tinia in council with the gods, mediating divine will through deliberation",
        "nature": "neutral",
        "nature_zh": "中性",
        "thunder_type": "Communia fulmina — 共議雷",
        "azimuth_start": 22.5,
        "azimuth_end": 45.0,
        "color": "#8C6F4E",
        "interpretation_zh": "議事中性之域，需謀而後動。此區行星示需廣納建言、集思廣益方可成事。",
        "interpretation_en": "Neutral deliberative region. Planets here counsel seeking advice and collective wisdom before action.",
    },
    {
        "region": 3,
        "name_etruscan": "Tins θ Neθuns",
        "name_en": "Tinia and Neptune",
        "name_zh": "廷尼亞與涅普頓",
        "deity_zh": "天神與海神聯合，賜福雷霆，天地相通，吉祥之兆",
        "deity_en": "Jupiter and Neptune in union, blessing thunderbolts linking sky and sea",
        "nature": "favorable",
        "nature_zh": "吉",
        "thunder_type": "Bona fulmina — 祝福雷",
        "azimuth_start": 45.0,
        "azimuth_end": 67.5,
        "color": "#8B7355",
        "interpretation_zh": "吉祥之域，天地聯通。行星入此，示宏圖大展，旅途順遂，貿易興隆。",
        "interpretation_en": "Auspicious region of sky-sea unity. Planets here favour grand plans, journeys, and prosperous trade.",
    },
    {
        "region": 4,
        "name_etruscan": "Uni / Mae Uni",
        "name_en": "Uni / Great Uni",
        "name_zh": "烏尼 / 大天后烏尼",
        "deity_zh": "天后朱諾，護佑女性、婚姻與生育，王室守護女神",
        "deity_en": "Queen of Heaven, guardian of women, marriage, and royalty — Etruscan Juno",
        "nature": "favorable",
        "nature_zh": "吉",
        "thunder_type": None,
        "azimuth_start": 67.5,
        "azimuth_end": 90.0,
        "color": "#9B8B6A",
        "interpretation_zh": "天后護佑之域，婚姻、女性與王權皆得庇蔭。行星入此，家族興旺，女性事業大吉。",
        "interpretation_en": "Protected by the Queen of Heaven. Auspicious for marriage, women's affairs, and royal matters.",
    },
    {
        "region": 5,
        "name_etruscan": "Tec / Vm / Cels",
        "name_en": "Tec / Vm / Cels (Earth Powers)",
        "name_zh": "大地諸神",
        "deity_zh": "大地女神群，掌農耕、土地豐饒與建築根基",
        "deity_en": "Earth deity cluster governing agriculture, land fertility, and foundations",
        "nature": "neutral",
        "nature_zh": "中性",
        "thunder_type": None,
        "azimuth_start": 90.0,
        "azimuth_end": 112.5,
        "color": "#6B7355",
        "interpretation_zh": "大地中性之域，農耕與建設之基。行星入此，宜耕作、置業、穩固根基，不利冒進。",
        "interpretation_en": "Neutral earth domain. Favourable for agriculture, construction, and consolidating foundations — not for bold ventures.",
    },
    {
        "region": 6,
        "name_etruscan": "Lvsl / Usil",
        "name_en": "Losna / Usil (Sun-Moon Pair)",
        "name_zh": "月亮女神洛斯納與太陽神烏西爾",
        "deity_zh": "太陽神烏西爾與月亮女神，光明、時間循環、預言之眼",
        "deity_en": "Usil the Sun and Losna the Moon — light, time cycles, prophetic vision",
        "nature": "favorable",
        "nature_zh": "吉",
        "thunder_type": None,
        "azimuth_start": 112.5,
        "azimuth_end": 135.0,
        "color": "#B8860B",
        "interpretation_zh": "日月輝耀之域，光明昌盛。行星入此，名聲顯赫、占卜靈驗、事業如日中天。",
        "interpretation_en": "Domain of solar-lunar radiance. Planets here bring fame, prophetic clarity, and career success.",
    },
    {
        "region": 7,
        "name_etruscan": "Neθuns",
        "name_en": "Nethuns (Neptune / Water)",
        "name_zh": "涅普頓水神",
        "deity_zh": "水神尼普頓，掌航海、河流與水利，中性守護",
        "deity_en": "Nethuns, lord of waters — shipping, rivers, irrigation, and the sea",
        "nature": "neutral",
        "nature_zh": "中性",
        "thunder_type": None,
        "azimuth_start": 135.0,
        "azimuth_end": 157.5,
        "color": "#2A6B8C",
        "interpretation_zh": "水神中性之域，流動與變化。行星入此，示遷移、航海、感情流動，忌固執。",
        "interpretation_en": "Neutral water domain of flow and change. Planets here favour travel, maritime affairs, and emotional fluidity.",
    },
    {
        "region": 8,
        "name_etruscan": "Caθa",
        "name_en": "Catha (Chthonic Sun)",
        "name_zh": "卡塔地下太陽",
        "deity_zh": "地下太陽女神卡塔，掌秘術、隱藏知識與冥界光輝",
        "deity_en": "Catha, goddess of the underworld sun — occult knowledge, hidden light, mysteries",
        "nature": "neutral",
        "nature_zh": "中性",
        "thunder_type": None,
        "azimuth_start": 157.5,
        "azimuth_end": 180.0,
        "color": "#7A5A3A",
        "interpretation_zh": "秘術中性之域，隱藏的力量與知識。行星入此，宜深研秘法，知曉隱情，可轉危為機。",
        "interpretation_en": "Neutral occult domain of hidden power. Planets here favour esoteric study, uncovering secrets, turning danger to opportunity.",
    },
    {
        "region": 9,
        "name_etruscan": "Fufluns",
        "name_en": "Fufluns (Bacchus)",
        "name_zh": "福弗倫斯酒神",
        "deity_zh": "酒神巴克斯，掌歡宴、葡萄豐收、生命喜悅與創造力",
        "deity_en": "Fufluns / Bacchus — festivity, vine harvest, life-joy, and creative force",
        "nature": "favorable",
        "nature_zh": "吉",
        "thunder_type": None,
        "azimuth_start": 180.0,
        "azimuth_end": 202.5,
        "color": "#6B3A7A",
        "interpretation_zh": "酒神喜慶之域，歡宴與豐收。行星入此，藝術創作、慶典宴飲、人際歡洽皆大吉。",
        "interpretation_en": "Domain of Bacchic joy. Planets here bless artistic creation, celebrations, social gatherings, and abundant harvests.",
    },
    {
        "region": 10,
        "name_etruscan": "Selva / Selvans",
        "name_en": "Selvans (Sylvanus)",
        "name_zh": "席爾瓦努斯林神",
        "deity_zh": "林神席爾瓦努斯，掌荒野、邊界之地與未開化自然",
        "deity_en": "Selvans / Silvanus — woodlands, boundary-marking, the wild untamed earth",
        "nature": "neutral",
        "nature_zh": "中性",
        "thunder_type": None,
        "azimuth_start": 202.5,
        "azimuth_end": 225.0,
        "color": "#2A5A3A",
        "interpretation_zh": "林神中性之域，荒野與邊界。行星入此，示需確立界限，享受自然，遠離塵囂以求清醒。",
        "interpretation_en": "Neutral domain of wilderness and boundaries. Planets here call for setting limits, seeking nature, gaining clarity away from crowds.",
    },
    {
        "region": 11,
        "name_etruscan": "Leθns",
        "name_en": "Lethns (Fate / Destiny)",
        "name_zh": "萊斯命運神",
        "deity_zh": "命運神萊斯，不可抗拒的宿命，終結與不歸之路",
        "deity_en": "Lethns, deity of irresistible fate — the inescapable thread of destiny",
        "nature": "unfavorable",
        "nature_zh": "凶",
        "thunder_type": None,
        "azimuth_start": 225.0,
        "azimuth_end": 247.5,
        "color": "#6B3A2A",
        "interpretation_zh": "命運凶兆之域，不可抗拒之力。行星入此，示命運關口，強求無益，宜順勢而為，接受改變。",
        "interpretation_en": "Domain of irresistible fate. Planets here signal a karmic turning point — resistance is futile; acceptance and adaptation are essential.",
    },
    {
        "region": 12,
        "name_etruscan": "Tluscv",
        "name_en": "Tluschva (Dark Deities)",
        "name_zh": "圖盧斯卡黑暗群神",
        "deity_zh": "黑暗群神圖盧斯卡，掌深淵、幽冥與不可名狀之黑暗",
        "deity_en": "Tluschva — the dark chthonic deities of abyss and nameless shadows",
        "nature": "unfavorable",
        "nature_zh": "大凶",
        "thunder_type": None,
        "azimuth_start": 247.5,
        "azimuth_end": 270.0,
        "color": "#3A2A1A",
        "interpretation_zh": "黑暗深淵大凶之域。行星入此，示潛藏危機、陰謀算計或心理陰影，需強化自我防護。",
        "interpretation_en": "Most dark and dangerous abyss region. Planets here warn of hidden dangers, conspiracies, and psychological shadows requiring strong protective measures.",
    },
    {
        "region": 13,
        "name_etruscan": "Cels / Uelsl",
        "name_en": "Cels / Velsl (Underworld Earth)",
        "name_zh": "賽爾斯冥土之神",
        "deity_zh": "大地神賽爾斯之冥土相，掌死亡、腐朽與冥界大地",
        "deity_en": "Cels / Velsl in underworld aspect — death, decay, and the chthonic earth",
        "nature": "unfavorable",
        "nature_zh": "凶",
        "thunder_type": None,
        "azimuth_start": 270.0,
        "azimuth_end": 292.5,
        "color": "#5A3A2A",
        "interpretation_zh": "冥土凶兆之域，死亡與腐朽。行星入此，示健康受損、事業衰頹，宜靜養守舊、避免大動作。",
        "interpretation_en": "Inauspicious underworld domain. Planets here warn of health issues, career decline — conserve energy and avoid major initiatives.",
    },
    {
        "region": 14,
        "name_etruscan": "Cvl / Alpanu",
        "name_en": "Culsu / Alpanu (Love-Erotic)",
        "name_zh": "愛神阿爾帕努",
        "deity_zh": "愛慾女神阿爾帕努，掌慾望、魅力與情感糾葛",
        "deity_en": "Alpanu, goddess of love-eros — desire, allure, and entangled passions",
        "nature": "neutral",
        "nature_zh": "中性",
        "thunder_type": None,
        "azimuth_start": 292.5,
        "azimuth_end": 315.0,
        "color": "#7A4A6A",
        "interpretation_zh": "愛慾中性之域，情感與魅力交織。行星入此，示感情複雜多變，魅力增強但需辨別真偽情感。",
        "interpretation_en": "Neutral erotic domain of desire and allure. Planets here intensify magnetism but warn of complex, ambivalent emotional entanglements.",
    },
    {
        "region": 15,
        "name_etruscan": "Maris",
        "name_en": "Maris (War / Mars)",
        "name_zh": "馬里斯戰神",
        "deity_zh": "戰神馬里斯，掌衝突、勇武與競爭，凶中含勇",
        "deity_en": "Maris the war-god — conflict, martial courage, and fierce competition",
        "nature": "unfavorable",
        "nature_zh": "凶",
        "thunder_type": None,
        "azimuth_start": 315.0,
        "azimuth_end": 337.5,
        "color": "#8A3A2A",
        "interpretation_zh": "戰神凶兆之域，衝突與競爭。行星入此，示爭端紛起，宜以柔克剛，避免正面衝突，靜待時機。",
        "interpretation_en": "Inauspicious war domain. Planets here signal disputes and conflicts — use diplomacy, avoid direct confrontation, await the right moment.",
    },
    {
        "region": 16,
        "name_etruscan": "Cautha",
        "name_en": "Cautha (Dawn Goddess)",
        "name_zh": "考塔黎明女神",
        "deity_zh": "黎明女神考塔，新生、希望、日出時分的神聖啟示",
        "deity_en": "Cautha, dawn goddess — rebirth, hope, and sacred revelation at sunrise",
        "nature": "favorable",
        "nature_zh": "吉",
        "thunder_type": None,
        "azimuth_start": 337.5,
        "azimuth_end": 360.0,
        "color": "#8A7A3A",
        "interpretation_zh": "黎明吉祥之域，新生與希望。行星入此，示新的開始，舊事已過，曙光乍現，大膽前行。",
        "interpretation_en": "Auspicious dawn domain of new beginnings. Planets here bless fresh starts — the past is gone, the light returns; move forward boldly.",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Etruscan Planet Identifiers
# ─────────────────────────────────────────────────────────────────────────────
# 對應 pyswisseph 行星 ID 到伊特魯里亞神名

ETRUSCAN_PLANETS: dict[int, dict[str, str]] = {
    0: {"zh": "太陽/Usil",      "en": "Sun (Usil)",       "glyph": "☀️"},
    1: {"zh": "月亮",           "en": "Moon",             "glyph": "🌙"},
    2: {"zh": "水星/Turms",     "en": "Mercury (Turms)",  "glyph": "☿"},
    3: {"zh": "金星/Turan",     "en": "Venus (Turan)",    "glyph": "♀"},
    4: {"zh": "火星/Laran",     "en": "Mars (Laran)",     "glyph": "♂"},
    5: {"zh": "木星/Tinia",     "en": "Jupiter (Tinia)",  "glyph": "♃"},
    6: {"zh": "土星/Satre",     "en": "Saturn (Satre)",   "glyph": "♄"},
}


# ─────────────────────────────────────────────────────────────────────────────
# Lightning Interpretations (Tinia's 9 Thunderbolts)
# ─────────────────────────────────────────────────────────────────────────────
# 廷尼亞九雷：依據伊特魯里亞閃電占卜傳統，廷尼亞擁有九種雷霆。
# 前三種由廷尼亞獨用，後三種需諸神同意，最後三種由命運女神協助。
# Source: Seneca, *Naturales Quaestiones* II.41; Pliny, *NH* II.138

LIGHTNING_INTERPRETATIONS: list[dict] = [
    {
        "type_num": 1,
        "description_zh": "警示雷——廷尼亞的第一雷，善意警告，提醒凡人注意即將到來的試煉",
        "description_en": "Warning bolt — Tinia's first thunderbolt; a benevolent caution heralding approaching trials",
        "severity": 1,
    },
    {
        "type_num": 2,
        "description_zh": "確認雷——廷尼亞確認諾言，神意允許，計畫得到天界認可",
        "description_en": "Confirming bolt — divine ratification; plans and promises receive celestial approval",
        "severity": 1,
    },
    {
        "type_num": 3,
        "description_zh": "命令雷——廷尼亞下達神聖命令，凡人必須立即行動或改變方向",
        "description_en": "Commanding bolt — Tinia issues a divine mandate; immediate action or course change required",
        "severity": 2,
    },
    {
        "type_num": 4,
        "description_zh": "眾神議決雷——十二主神共議而降，重大命運轉折，不可違逆",
        "description_en": "Council bolt — struck after deliberation of the twelve gods; major fate turning point, irresistible",
        "severity": 3,
    },
    {
        "type_num": 5,
        "description_zh": "淨化雷——燒毀舊有，清除污染，痛苦中帶來更新與淨化",
        "description_en": "Purifying bolt — burns away the old and polluted; painful but ultimately renewing",
        "severity": 3,
    },
    {
        "type_num": 6,
        "description_zh": "毀壞雷——諸神同意毀滅，建築、計畫或關係遭到破壞，需重建",
        "description_en": "Destructive bolt — the gods consent to ruin; structures, plans, or relationships must be rebuilt",
        "severity": 4,
    },
    {
        "type_num": 7,
        "description_zh": "命運定局雷——命運女神加入廷尼亞，宿命已定，人力無法改變",
        "description_en": "Fate-sealing bolt — the Fates join Tinia; destiny is sealed beyond human power to alter",
        "severity": 4,
    },
    {
        "type_num": 8,
        "description_zh": "滅亡雷——諸神與命運共同降下，國家或文明面臨崩潰，極大凶兆",
        "description_en": "Annihilating bolt — gods and Fates together; nations or civilisations face collapse",
        "severity": 5,
    },
    {
        "type_num": 9,
        "description_zh": "天譴終極雷——最高秘密雷霆，只由命運神降下，代表絕對終結，萬劫不復",
        "description_en": "Ultimate divine wrath — the supreme secret bolt wielded only by the Fates; absolute finality",
        "severity": 5,
    },
]
