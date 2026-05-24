"""
astro/alchemical_astrology/signatures.py
═══════════════════════════════════════════════════════════════════════════════
煉金占星學 — 物質印記說（Doctrine of Signatures / Signatura Rerum）

帕拉塞爾蘇斯的物質印記說（Signatura Rerum）核心主張：
  宇宙中每個行星在自然界留下可辨識的「印記」（Signatura）。
  草藥的形狀、顏色、氣味、生長環境，乃至礦石的晶體結構，
  皆映射著對應行星的宇宙振動（virtus）。
  醫者應藉此辨識藥物歸屬，以同性相療（similia similibus）原則
  運用草本治療對應行星失衡所引發的疾病。

來源：
  Paracelsus, Opus Paramirum (1531); De Natura Rerum (1537);
  Astronomia Magna (1537-38); Archidoxes of Magic
  Jakob Boehme, Signatura Rerum (1621) [發展帕拉塞爾蘇斯概念]
"""

from __future__ import annotations

from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────────────────────
# 資料結構
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PlanetSignature:
    """單顆行星的物質印記說描述。"""
    planet_key: str
    symbol: str
    visual_signs: list[str]       # 植物視覺印記特徵（英文）
    visual_signs_zh: list[str]    # 對應中文描述
    healing_principle: str        # 治療原則（英文）
    healing_principle_zh: str     # 中文
    signature_text: str           # 完整印記說明（英文）
    signature_text_zh: str        # 中文說明
    source: str                   # 文獻來源


# ─────────────────────────────────────────────────────────────────────────────
# 七大行星物質印記（帕拉塞爾蘇斯 Signatura Rerum）
# ─────────────────────────────────────────────────────────────────────────────

PLANET_SIGNATURES: dict[str, PlanetSignature] = {

    "sun": PlanetSignature(
        planet_key="sun",
        symbol="☉",
        visual_signs=[
            "Round, radiate flower heads resembling the solar disc",
            "Yellow or golden flowers and fruits",
            "Heliotropic movement (turns toward sunlight)",
            "Warm, stimulating fragrance",
            "Shiny, reflective leaf surfaces",
        ],
        visual_signs_zh=[
            "圓形放射狀花冠，形似太陽圓盤",
            "黃色或金色的花朵與果實",
            "趨光性（向陽性）生長習性",
            "溫暖、振奮精神的氣味",
            "光亮、反光的葉面",
        ],
        healing_principle=(
            "Solar herbs strengthen the vital spirit (spiritus vitalis), "
            "fortify the heart, elevate the spirits, and combat excessive cold and moisture. "
            "They are warm and dry in the first to third degrees."
        ),
        healing_principle_zh=(
            "太陽草本強化生命精氣（spiritus vitalis），鞏固心臟，振奮精神，"
            "對抗過度的寒冷與濕氣。性質溫熱乾燥，屬第一至第三度。"
        ),
        signature_text=(
            "Paracelsus taught that plants bearing the Sun's signature are recognisable "
            "by their golden or yellow colouration, circular form, and heliotropic nature. "
            "Heliotrope (Heliotropium) turns its face ever toward the Sun — a perfect solar "
            "signature. St John's Wort (Hypericum perforatum), flowering at midsummer (St John's "
            "Day, 24 June), when the Sun reaches its zenith, manifests tiny perforations in its "
            "leaves — the Sun's rays piercing the green veil. Saffron's golden threads distil "
            "the Sun's warmth. These herbs govern the heart, strengthen vital heat, and counter "
            "melancholic coldness."
        ),
        signature_text_zh=(
            "帕拉塞爾蘇斯教導說，帶有太陽印記的植物可從其金黃色澤、圓形外觀"
            "和向光性中辨認。旋覆花（Heliotropium）永遠將臉龐轉向太陽——這是完美的"
            "太陽印記。聖約翰草（金絲桃）在仲夏（聖約翰節，6月24日，太陽至頂之時）盛開，"
            "葉片上有細小穿孔，象徵太陽光芒穿透綠色面紗。番紅花的金色花絲蒸餾了太陽的暖意。"
            "這些草本主宰心臟，強化生命熱力，對抗憂鬱的寒冷。"
        ),
        source="Paracelsus, Astronomia Magna (1537-38); De Natura Rerum; Archidoxes of Magic",
    ),

    "moon": PlanetSignature(
        planet_key="moon",
        symbol="☽",
        visual_signs=[
            "White or pale silver flowers blooming at night or in shade",
            "Juicy, water-retaining leaves (succulent quality)",
            "Crescent or cup-shaped leaves",
            "Plants growing near water or in moist environments",
            "Rapid, rhythmic growth following lunar cycles",
        ],
        visual_signs_zh=[
            "白色或淡銀色花朵，夜間或陰處開放",
            "多汁、保水的葉片（多肉質感）",
            "新月形或杯狀葉片",
            "生長在水邊或潮濕環境的植物",
            "隨月亮週期快速、週期性生長",
        ],
        healing_principle=(
            "Lunar herbs govern the brain, bodily fluids, and the phlegmatic humour. "
            "They cool fevers, regulate moisture in the body, calm agitated spirits, "
            "and assist in matters of fertility and sleep."
        ),
        healing_principle_zh=(
            "月亮草本主宰大腦、體液與黏液質。它們退燒、調節體內水分、平靜激動的情緒，"
            "並有助於生育與睡眠。"
        ),
        signature_text=(
            "The Moon's signature is found in white, nocturnal plants and those closely "
            "associated with water. Mugwort (Artemisia vulgaris), sacred to Diana-Luna, "
            "grows along riverbanks and was used by Paracelsus to govern the 'moist brain.' "
            "Moonwort (Botrychium lunaria) bears crescent-shaped pinnules — the very symbol "
            "of Luna pressed into leaf form. White Poppy induces sleep and governs dreams, "
            "the Moon's dominion. Paracelsus held that lunar plants regulate the tides of "
            "bodily fluid just as the Moon moves the ocean tides."
        ),
        signature_text_zh=(
            "月亮的印記見於白色、夜行性植物以及與水密切相關的植物。"
            "艾草（Artemisia vulgaris）被月神黛安娜所聖化，生長在河岸邊，"
            "帕拉塞爾蘇斯用它來調理「濕潤的大腦」。月牙草（Botrychium lunaria）"
            "的羽狀小葉呈新月形——月亮符號直接印刻在葉片形態中。白罌粟引發睡眠並"
            "主宰夢境，這是月亮的領域。帕拉塞爾蘇斯認為，月亮草本調節體液潮汐，"
            "一如月亮驅動海洋潮汐。"
        ),
        source="Paracelsus, Astronomia Magna (1537-38); De Natura Rerum, Book VII",
    ),

    "mars": PlanetSignature(
        planet_key="mars",
        symbol="♂",
        visual_signs=[
            "Thorny, spiny, or prickly plants",
            "Red or blood-red flowers and berries",
            "Sharp, acrid, or burning taste",
            "Plants growing in dry, barren, or iron-rich soils",
            "Stinging or caustic properties (contact irritation)",
        ],
        visual_signs_zh=[
            "有刺、多刺或針刺狀植物",
            "紅色或血紅色的花朵與漿果",
            "辛辣、刺激或灼燒的味道",
            "生長在乾燥、貧瘠或富含鐵的土壤",
            "刺痛或腐蝕性（接觸刺激）",
        ],
        healing_principle=(
            "Martial herbs stimulate bile production, dispel phlegm and damp stagnation, "
            "reduce inflammation through driving out corrupt matter, and fortify martial "
            "courage. They govern the gallbladder and bile duct, and treat Saturnine coldness."
        ),
        healing_principle_zh=(
            "火星草本刺激膽汁分泌，驅散痰濕停滯，通過驅逐腐敗物質來消炎，"
            "並強化火星之勇氣。它們主宰膽囊與膽管，治療土星的寒冷症狀。"
        ),
        signature_text=(
            "Mars stamps its signature upon plants with thorns and stinging power — "
            "weapons in vegetable form. Nettles (Urtica dioica) sting on contact, "
            "their iron-rich leaves carrying the martial metal within. Wormwood "
            "(Artemisia absinthium) is intensely bitter — Mars's choler in taste — "
            "driving away worms and corrupt phlegm from the gallbladder. Garlic's "
            "pungent, penetrating odour mirrors the fiery, cutting nature of Mars. "
            "Paracelsus prescribed martial herbs in conditions of excess moisture "
            "and phlegmatic stagnation."
        ),
        signature_text_zh=(
            "火星將其印記烙印在帶刺和蟄人力量的植物上——植物形態的武器。"
            "蕁麻（Urtica dioica）接觸即蟄，其富含鐵質的葉片攜帶著火星金屬。"
            "苦艾草（Artemisia absinthium）極度苦澀——火星的膽汁質體現在味道中——"
            "驅除寄生蟲和膽囊的腐爛痰液。大蒜辛辣穿透的氣味映照火星的火熱切割本質。"
            "帕拉塞爾蘇斯在水分過多和痰濕停滯的病症中開具火星草本。"
        ),
        source="Paracelsus, De Natura Rerum (1537); Archidoxes of Magic; Agrippa Book I",
    ),

    "mercury": PlanetSignature(
        planet_key="mercury",
        symbol="☿",
        visual_signs=[
            "Feathery, finely divided leaves (pinnate or bipinnate)",
            "Delicate, intricate branching patterns",
            "Pale blue, lavender, or multi-coloured flowers",
            "Aromatic yet light, subtle fragrance",
            "Plants with mixed or ambiguous characteristics (mercurial duality)",
        ],
        visual_signs_zh=[
            "羽狀、細密分裂的葉片（羽狀複葉或二回羽狀）",
            "精緻、複雜的分枝模式",
            "淡藍色、薰衣草色或多色花朵",
            "芳香而清淡的氣味",
            "具有混合或模糊特徵的植物（水星雙重性）",
        ],
        healing_principle=(
            "Mercurial herbs refine and carry the vital spirits through the nervous system, "
            "clear the lungs of phlegm, sharpen the intellect, and govern all communicative "
            "and respiratory functions. They are the messengers among plant medicines."
        ),
        healing_principle_zh=(
            "水星草本精煉並傳遞神經系統中的生命精氣，清除肺部痰液，"
            "鋒利智識，並主宰所有溝通和呼吸功能。它們是植物藥物中的信使。"
        ),
        signature_text=(
            "Mercury's signature is subtlety and duality. Fennel (Foeniculum vulgare) "
            "bears feathery, finely divided leaves — the very image of nervous, "
            "quicksilver energy. Its seeds carry both stimulating and calming virtues, "
            "reflecting Mercury's dual nature. Lavender's narrow leaves and pale violet "
            "flower spikes mirror the refined, elevated vibration of Mercury. Parsley's "
            "curled, intricate leaves show Mercury's love of complexity. Paracelsus "
            "taught that Mercurial plants purify the 'spiritus animalis' flowing through "
            "the nervous system."
        ),
        signature_text_zh=(
            "水星的印記是精微與雙重性。茴香（Foeniculum vulgare）具有羽毛狀、"
            "細密分裂的葉片——正是神經質、水銀能量的意象。其種子兼具刺激與鎮靜功效，"
            "反映水星的雙重本質。薰衣草狹窄的葉片和淡紫色穗狀花序映照水星精煉、"
            "高頻的振動。歐芹捲曲複雜的葉片顯示水星對複雜性的喜愛。帕拉塞爾蘇斯"
            "教導說，水星植物淨化流通於神經系統的「動物精氣」（spiritus animalis）。"
        ),
        source="Paracelsus, Concerning the Spirits of the Planets; Opus Paramirum, Book I",
    ),

    "jupiter": PlanetSignature(
        planet_key="jupiter",
        symbol="♃",
        visual_signs=[
            "Large, broad, expansive leaves with generous form",
            "Sweet or mildly bitter, nourishing taste",
            "Blue, indigo, or purple flowers",
            "Abundant fruiting and generous growth habit",
            "Plants associated with oak trees and high, airy places",
        ],
        visual_signs_zh=[
            "大型、寬闊、舒展的葉片",
            "甜味或微苦、滋養性的味道",
            "藍色、靛藍色或紫色的花朵",
            "豐碩結果且生長茂盛",
            "與橡樹及高聳通風場所相關的植物",
        ],
        healing_principle=(
            "Jovial herbs strengthen the liver (Jupiter's organ), enrich the blood, "
            "restore sanguine humour, and promote general expansion and well-being. "
            "They counter the excess of cold, melancholic Saturn."
        ),
        healing_principle_zh=(
            "木星草本強化肝臟（木星主宰之器官），滋富血液，恢復多血質體液，"
            "促進整體擴展與幸福感。它們對抗過度寒冷的憂鬱土星。"
        ),
        signature_text=(
            "Jupiter's magnanimous nature is reflected in large-leafed, generously "
            "growing plants. Agrimony (Agrimonia eupatoria) with its tall, yellow-spiked "
            "flower stalk reaching toward Jupiter's domain — the heavens — was the premier "
            "Jovial liver herb. Sage (Salvia officinalis), whose name derives from 'salvo' "
            "(to save), embodies Jupiter's preserving, life-giving force. Wood Betony, "
            "broad-leafed and growing in high woodland, was prized as a universal Jovial "
            "tonic. Agrippa confirms Jupiter's plants are 'sweet and aromatic, temperate "
            "in heat and moisture' (Book I, Ch. XXIV)."
        ),
        signature_text_zh=(
            "木星的慷慨本質反映在大葉、茂盛生長的植物上。龍芽草（Agrimonia eupatoria）"
            "高聳的黃色穗狀花序伸向木星的領域——天空——是首屈一指的木星肝臟草本。"
            "鼠尾草（Salvia officinalis）的名稱源自「salvo」（拯救），體現了木星"
            "保存、賦予生命的力量。林間水蘇葉片寬大，生長在高處林地，被珍視為"
            "通用的木星補品。阿格里帕確認木星植物「甘甜芳香，寒熱均衡」（第一卷第24章）。"
        ),
        source="Agrippa, Three Books of Occult Philosophy, Book I, Ch. XXIV (1531); Paracelsus, Astronomia Magna",
    ),

    "venus": PlanetSignature(
        planet_key="venus",
        symbol="♀",
        visual_signs=[
            "Delicate, beautiful, symmetrical flowers",
            "Sweet, pleasing fragrance",
            "Soft, smooth, or silky textures",
            "Green or pink colouration",
            "Plants associated with beauty, love, and fertile gardens",
        ],
        visual_signs_zh=[
            "精緻、美麗、對稱的花朵",
            "甜蜜、令人愉悅的芬芳",
            "柔軟、光滑或絲綢般的質地",
            "綠色或粉紅色的色調",
            "與美麗、愛情和肥沃庭園相關的植物",
        ],
        healing_principle=(
            "Venereal herbs govern the kidneys and generative organs, beautify and soften "
            "the skin, ease female complaints, promote the flow of the venous blood, "
            "and restore harmony between the humours."
        ),
        healing_principle_zh=(
            "金星草本主宰腎臟和生殖器官，美化並柔化皮膚，緩解女性病症，"
            "促進靜脈血液流通，並恢復體液之間的和諧。"
        ),
        signature_text=(
            "Venus imprints her beauty upon the most graceful plants. Maidenhair Fern "
            "(Adiantum capillus-veneris) — 'Venus's hair' — with its delicate, hair-like "
            "fronds was dedicated to Venus and used to treat hair loss and beautify complexion. "
            "Vervain (Verbena officinalis), the ancient altar plant of Venus, embodies "
            "harmonious, peaceful Venereal virtue; it purifies and soothes. The Rose, "
            "supreme flower of Venus, with its perfect symmetry, sweet scent, and beauty "
            "beside its thorns, carries the full complexity of the Venereal principle. "
            "Paracelsus assigned these plants to kidney ailments and imbalanced generative fluids."
        ),
        signature_text_zh=(
            "金星將她的美麗烙印在最優雅的植物上。鐵線蕨（Adiantum capillus-veneris）——"
            "「維納斯之髮」——其精緻的髮絲狀葉片被獻給金星，用於治療脫髮和美化膚色。"
            "馬鞭草（Verbena officinalis），金星的古代祭壇植物，體現了和諧、平靜的"
            "金星美德；它淨化並撫慰。玫瑰，金星的至尊花朵，以其完美的對稱、甜蜜的香氣"
            "以及美麗與荊棘並存，承載了金星原則的全部複雜性。帕拉塞爾蘇斯將這些植物"
            "分配給腎臟疾病和失衡的生殖體液。"
        ),
        source="Paracelsus, Astronomia Magna (1537-38); Concerning the Spirits of the Planets; Agrippa Book I",
    ),

    "saturn": PlanetSignature(
        planet_key="saturn",
        symbol="♄",
        visual_signs=[
            "Dark, sombre, or blackish colouration",
            "Hairy, rough, or coarse texture",
            "Bitter, astringent, or cold taste",
            "Slow-growing, long-lived, or deep-rooted plants",
            "Plants associated with decay, boundaries, and cold, damp places",
        ],
        visual_signs_zh=[
            "深色、陰暗或近黑色的色調",
            "毛髮狀、粗糙或粗糙的質地",
            "苦澀、收斂或寒冷的味道",
            "生長緩慢、長壽或根系深長的植物",
            "與腐爛、邊界以及寒冷潮濕之地相關的植物",
        ],
        healing_principle=(
            "Saturnine herbs are cold and dry; they consolidate, contract, and bind. "
            "They knit broken bones, heal wounds through astringency, govern the spleen "
            "and melancholic humour, and — at the highest level — provide the prima materia "
            "for the alchemical Great Work."
        ),
        healing_principle_zh=(
            "土星草本寒冷乾燥；它們鞏固、收縮並束縛。它們接合斷骨，通過收斂性"
            "治癒傷口，主宰脾臟與憂鬱質體液，並且在最高層面上，為煉金大功提供原初物質。"
        ),
        signature_text=(
            "Saturn's dark, contracting signature is unmistakable. Comfrey (Symphytum "
            "officinale) — 'knitbone' — its rough, hairy leaves and deep taproot consolidating "
            "and binding, perfectly mirrors Saturn's bone-governing, binding nature. "
            "Horsetail (Equisetum) is ancient — a survivor from primordial ages, "
            "deep-rooted and silica-rich (bones), a true Saturnine plant. Hemlock, "
            "deadly and cold to the point of death, embodies Saturn's extreme principle. "
            "Paracelsus taught that Saturnine plants purify the spleen and transform "
            "the heavy lead-humour (melancholia) into prima materia for spiritual work."
        ),
        signature_text_zh=(
            "土星黑暗、收縮的印記不可誤認。聚合草（Symphytum officinale）——「接骨草」——"
            "其粗糙毛茸的葉片和深入地下的主根，具有鞏固和束縛的作用，完美映照土星"
            "主宰骨骼、束縛的本質。問荊（Equisetum）是古老植物——遠古時代的幸存者，"
            "根系深長且富含硅質（骨骼），是真正的土星植物。毒芹致命且寒冷至死，"
            "體現了土星的極端原則。帕拉塞爾蘇斯教導說，土星植物淨化脾臟，"
            "並將沉重的鉛質體液（憂鬱）轉化為靈性工作的原初物質。"
        ),
        source="Paracelsus, De Mineralibus; Coelum Philosophorum; De Natura Rerum, Book I",
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# 便捷函數
# ─────────────────────────────────────────────────────────────────────────────

def get_planet_signature(planet_key: str) -> PlanetSignature | None:
    """根據行星鍵名獲取物質印記說資料。

    Args:
        planet_key: 行星英文鍵名（"sun", "moon", "mars", …）

    Returns:
        PlanetSignature 或 None（若行星不存在）
    """
    return PLANET_SIGNATURES.get(planet_key)


def get_signature_text_zh(planet_key: str) -> str:
    """獲取指定行星的物質印記說中文說明。

    Args:
        planet_key: 行星英文鍵名

    Returns:
        中文說明字串，若不存在則返回空字串
    """
    sig = PLANET_SIGNATURES.get(planet_key)
    if sig is None:
        return ""
    return sig.signature_text_zh
