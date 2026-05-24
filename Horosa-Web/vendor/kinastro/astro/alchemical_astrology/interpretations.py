"""
astro/alchemical_astrology/interpretations.py
═══════════════════════════════════════════════════════════════════════════════
煉金占星學 — 解讀文本庫

提供每顆行星與每個煉金階段的深度解讀，
以及個人化星盤解讀的模板文本。

所有解讀均以帕拉塞爾蘇斯古典文獻為基礎，
並以文藝復興煉金術風格撰寫（雙語：英文 + 中文）。
"""

from __future__ import annotations


# ─────────────────────────────────────────────────────────────────────────────
# 行星解讀（個人星盤）
# ─────────────────────────────────────────────────────────────────────────────

PLANET_READING: dict[str, dict[str, str]] = {
    "sun": {
        "en": (
            "The Sun (Sol) holds dominion over your vital spirit. "
            "Gold is your metal — pure, incorruptible, and perfected. "
            "Your constitution tends toward the choleric and vital: warm, dry, creative. "
            "The heart is your central organ; tend to it with solar herbs — "
            "St John's Wort for the solar plexus, saffron to warm the blood. "
            "In the Great Work, you stand at the Citrinitas threshold, "
            "the dawn of gold from silver, the first light of perfection."
        ),
        "zh": (
            "太陽（Sol）主宰您的生命精氣。黃金是您的金屬——純粹、不可腐蝕且完美。"
            "您的體質趨向膽汁質和活力型：溫暖、乾燥、富有創造力。"
            "心臟是您的核心器官；用太陽草本滋養它——聖約翰草調理太陽神經叢，"
            "番紅花溫暖血液。在煉金大功中，您處於黃化的門檻，"
            "黃金從白銀中破曉，完美的第一縷光芒。"
        ),
    },
    "moon": {
        "en": (
            "The Moon (Luna) governs your inner tides, the rhythms of your body, "
            "and the flow of your bodily humours. Silver is your metal. "
            "Your constitution is phlegmatic — responsive, receptive, and fluid. "
            "The brain and bodily fluids are your domain. "
            "Lunar herbs — mugwort and moonwort — assist in regulating your sleep, "
            "dreams, and the subtle rhythms of your vital moisture. "
            "In the Opus Magnum, you carry the Albedo within you: "
            "the purification that comes after the dark night of Nigredo."
        ),
        "zh": (
            "月亮（Luna）主宰您的內在潮汐、身體節律和體液流動。白銀是您的金屬。"
            "您的體質是黏液質——敏感、接納且流動。大腦和體液是您的領域。"
            "月亮草本——艾草與月牙草——幫助調節您的睡眠、夢境"
            "以及生命濕氣的微妙節律。在煉金大功中，您在內心承載著白化："
            "黑化黑暗之夜後的淨化。"
        ),
    },
    "mars": {
        "en": (
            "Mars (Ares) rules your bile and martial force. "
            "Iron is your metal — strong, magnetic, and warlike. "
            "You carry a choleric fire: active, driven, cutting through stagnation. "
            "The gallbladder and bile are your domain; excess bile may manifest "
            "as inflammation or aggression. Martial herbs — wormwood, garlic, nettles — "
            "purge corrupt phlegm and drive out what has overstayed its welcome. "
            "In the Great Work, you initiate the Nigredo: the necessary dissolution "
            "that precedes all transformation."
        ),
        "zh": (
            "火星（Ares）主宰您的膽汁與火星力量。鐵是您的金屬——強壯、磁性且好戰。"
            "您攜帶著膽汁質的火焰：積極、有驅動力，切穿停滯。膽囊與膽汁是您的領域；"
            "過多膽汁可能表現為炎症或攻擊性。火星草本——苦艾草、大蒜、蕁麻——"
            "清除腐敗的痰液，驅逐已滯留過久的事物。在煉金大功中，"
            "您啟動黑化：所有轉化之前必要的溶解。"
        ),
    },
    "mercury": {
        "en": (
            "Mercury (Hermes-Thoth) rules the spiritus animalis — "
            "the animating intelligence flowing through your nervous system. "
            "Quicksilver is your metal: volatile, mercurial, and the great mediator. "
            "Your constitution is sanguine: warm, moist, and quickening. "
            "The lungs and nervous system are your domain. "
            "Mercurial herbs — fennel, lavender — clear the channels of speech and thought. "
            "In the Great Work, Mercury is the alchemical solvent and mediator, "
            "present at every stage of the Opus."
        ),
        "zh": (
            "水星（赫爾墨斯-托特）主宰動物精氣（spiritus animalis）——"
            "流通於您神經系統的活化智識。水銀是您的金屬：揮發性、善變且是偉大的調解者。"
            "您的體質是多血質：溫暖、濕潤且充滿活力。肺部和神經系統是您的領域。"
            "水星草本——茴香、薰衣草——清理語言與思維的通道。在煉金大功中，"
            "水星是煉金溶劑與調解者，存在於大功的每個階段。"
        ),
    },
    "jupiter": {
        "en": (
            "Jupiter (Zeus) presides over the sanguine and expansive principle within you. "
            "Tin is your metal — generous, resonant, and expansive. "
            "The liver is your central organ: the seat of sanguine blood production, "
            "vitality, and abundance. Jovial herbs — agrimony, sage, betony — "
            "strengthen the liver, enrich the blood, and restore natural confidence. "
            "You are aligned with the Rubedo — the final expansion into wholeness, "
            "the gold of the completed Great Work."
        ),
        "zh": (
            "木星（宙斯）主持您內在的多血質與擴展原則。錫是您的金屬——慷慨、共鳴且富有擴展性。"
            "肝臟是您的核心器官：多血質血液生產的所在，活力與豐盛之源。"
            "木星草本——龍芽草、鼠尾草、林間水蘇——強化肝臟，滋富血液，恢復自然的自信。"
            "您與赤化對齊——走向圓滿的最終擴展，完成煉金大功的黃金。"
        ),
    },
    "venus": {
        "en": (
            "Venus (Aphrodite) governs beauty, harmony, and the generative force within you. "
            "Copper is your metal — warm, ductile, and nurturing. "
            "The kidneys and generative organs are your domain; "
            "your constitution mixes phlegmatic and sanguine. "
            "Venereal herbs — maidenhair fern, vervain, rose — "
            "restore beauty to the skin, ease kidney complaints, "
            "and attune the soul to the harmonious Venereal principle. "
            "In the Great Work, Venus participates in the Albedo: "
            "the beautification and purification of the soul."
        ),
        "zh": (
            "金星（阿芙羅狄忒）主宰您內在的美麗、和諧與生殖力量。銅是您的金屬——溫暖、延展且有養育性。"
            "腎臟和生殖器官是您的領域；您的體質混合黏液質和多血質。"
            "金星草本——鐵線蕨、馬鞭草、玫瑰——恢復皮膚的美麗，緩解腎臟不適，"
            "並使靈魂與和諧的金星原則相調。在煉金大功中，金星參與白化："
            "靈魂的美化與淨化。"
        ),
    },
    "saturn": {
        "en": (
            "Saturn (Kronos) rules the deep, the bounded, and the bones of existence. "
            "Lead is your metal — heavy, cold, and the prima materia of the Great Work. "
            "The spleen and melancholic humour are your domain. "
            "Saturn asks for patience, endurance, and the willingness to descend "
            "into the Nigredo before ascending. Saturnine herbs — comfrey, horsetail — "
            "consolidate, bind, and build the solid foundations of body and spirit. "
            "You are the necessary beginning: the dark, rich soil from which gold may grow."
        ),
        "zh": (
            "土星（克洛諾斯）主宰深淵、界限和存在的骨架。鉛是您的金屬——沉重、寒冷，"
            "且是煉金大功的原初物質。脾臟和憂鬱質體液是您的領域。"
            "土星要求耐心、忍耐，以及在升華之前下降入黑化的意願。"
            "土星草本——聚合草、問荊——鞏固、束縛並建造身心的堅實基礎。"
            "您是必要的開始：黑暗、豐富的土壤，黃金可以從中生長。"
        ),
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# 煉金階段深度解讀
# ─────────────────────────────────────────────────────────────────────────────

STAGE_READING: dict[str, dict[str, str]] = {
    "nigredo": {
        "en": (
            "You are at the Nigredo — the blackening, the putrefaction of prima materia. "
            "This is the necessary darkness before any transformation can begin. "
            "Saturn and Mars preside here; lead and iron are active. "
            "Do not resist the dissolution. Paracelsus taught that all impurities "
            "must be brought to the surface before they can be purged. "
            "This is the soil from which the gold of the Rubedo will eventually grow."
        ),
        "zh": (
            "您處於黑化——原初物質的腐化與分解。這是任何轉化開始之前必要的黑暗。"
            "土星和火星在此主持；鉛和鐵活躍運作。不要抗拒溶解。"
            "帕拉塞爾蘇斯教導說，所有雜質在被清除之前必須浮現到表面。"
            "這是最終將生長出赤化黃金的土壤。"
        ),
    },
    "albedo": {
        "en": (
            "You are at the Albedo — the whitening, the purification. "
            "After the darkness of Nigredo comes the pure white of the lunar wash. "
            "The Moon, Mercury, and Venus preside here; silver and quicksilver are active. "
            "The soul has been cleansed; the unconscious illuminated. "
            "Paracelsus described this as the 'washing of the black' — "
            "the appearance of the White Stone before the Red."
        ),
        "zh": (
            "您處於白化——淨化與清潔。黑化的黑暗之後是月亮洗滌的純白。"
            "月亮、水星和金星在此主持；銀和水銀活躍運作。"
            "靈魂已被清洗；潛意識已被照亮。帕拉塞爾蘇斯將此描述為「洗黑」——"
            "白石在紅石之前的顯現。"
        ),
    },
    "citrinitas": {
        "en": (
            "You are at the Citrinitas — the yellowing, the dawn of gold. "
            "This is the stage Paracelsus particularly emphasised: "
            "the transition from the silver of Albedo to the gold of Rubedo. "
            "The Sun enters the Work; the solar principle begins to illuminate. "
            "You are the alchemist at the threshold of perfection."
        ),
        "zh": (
            "您處於黃化——黃金的黎明。這是帕拉塞爾蘇斯特別強調的階段："
            "從白化的銀向赤化的金過渡。太陽進入煉金大功；太陽原則開始照亮。"
            "您是站在完美門檻上的煉金術士。"
        ),
    },
    "rubedo": {
        "en": (
            "You are at the Rubedo — the reddening, the perfection, the completion. "
            "The Great Work approaches its culmination. "
            "The Philosopher's Stone is within reach; perfect gold is attained. "
            "The Sun and Jupiter preside here in their fullness. "
            "Paracelsus taught that Rubedo represents not merely chemical perfection "
            "but the healing and perfection of the soul itself."
        ),
        "zh": (
            "您處於赤化——紅化、完美與完成。煉金大功趨近其頂峰。"
            "賢者之石觸手可及；完美黃金已被達成。太陽和木星在此以完整形式主持。"
            "帕拉塞爾蘇斯教導說，赤化不僅代表化學上的完美，"
            "也代表靈魂本身的療癒與完善。"
        ),
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# 綜合解讀生成
# ─────────────────────────────────────────────────────────────────────────────

def get_planet_reading(planet_key: str, lang: str = "zh") -> str:
    """獲取行星個人解讀文本。

    Args:
        planet_key: 行星英文鍵名
        lang: "zh"（中文）或 "en"（英文）

    Returns:
        解讀文本字串
    """
    reading = PLANET_READING.get(planet_key, {})
    return reading.get(lang, reading.get("en", ""))


def get_stage_reading(stage_key: str, lang: str = "zh") -> str:
    """獲取煉金階段解讀文本。

    Args:
        stage_key: 階段鍵名（"nigredo", "albedo", "citrinitas", "rubedo"）
        lang: "zh" 或 "en"

    Returns:
        解讀文本字串
    """
    reading = STAGE_READING.get(stage_key, {})
    return reading.get(lang, reading.get("en", ""))
