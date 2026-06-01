"""
astro/alchemical_astrology/correspondences.py
═══════════════════════════════════════════════════════════════════════════════
煉金占星學 — 七大行星對應關係常數

所有對應關係均源自帕拉塞爾蘇斯（Paracelsus）的一手文獻：
  • Coelum Philosophorum（天哲學，1520s）
  • Astronomia Magna（偉大天文學，1537-38）
  • De Natura Rerum（自然之物論，1537）
  • Concerning the Spirits of the Planets（論行星靈，1530s）
  • De Mineralibus（礦物論）

二手文獻：
  • Cornelius Agrippa: Three Books of Occult Philosophy（神秘哲學三書，1531）
  • Marsilio Ficino: De Vita Libri Tres（三生命書，1489）

歷史原則：Signatura Rerum（物質印記說）— 帕拉塞爾蘇斯認為
宇宙中每個行星在地上王國（金屬、植物、礦石、人體）皆留有印記，
治療師可循此印記辨識藥材與病症的行星歸屬。
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ─────────────────────────────────────────────────────────────────────────────
# 資料結構
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PlanetCorrespondence:
    """單顆行星的全部煉金占星對應關係（帕拉塞爾蘇斯傳統）。"""

    # 識別
    planet_key: str          # 英文鍵名（"sun", "moon", …）
    symbol: str              # 天文符號（☉ ☽ ♂ …）
    name_en: str             # 英文名
    name_zh: str             # 中文名

    # 金屬對應（帕拉塞爾蘇斯 Coelum Philosophorum）
    metal_en: str            # 英文金屬名
    metal_zh: str            # 中文金屬名
    metal_latin: str         # 拉丁名稱
    metal_symbol: str        # 煉金術金屬符號

    # 藥草對應（帕拉塞爾蘇斯 Signatura Rerum）
    herbs: list[str]         # 藥草列表（英文學名/俗名）
    herbs_zh: list[str]      # 對應中文名

    # 礦石/寶石對應（帕拉塞爾蘇斯/阿格里帕）
    minerals: list[str]      # 礦石列表（英文）
    minerals_zh: list[str]   # 對應中文名

    # 人體對應（帕拉塞爾蘇斯醫學占星）
    body_part_en: str        # 支配的人體部位（英文）
    body_part_zh: str        # 中文

    # 氣質/體液（四體液理論）
    temperament_en: str      # 氣質（Choleric / Phlegmatic / Sanguine / Melancholic）
    temperament_zh: str      # 中文

    # 煉金階段（Opus Magnum）
    alchemical_stage: str    # 對應的煉金階段（Nigredo / Albedo / Citrinitas / Rubedo / —）
    stage_zh: str            # 中文

    # 文獻來源（每筆資料均需可追溯）
    source: str              # 原始文獻引用字串

    # 統治星座（黃道）
    ruling_signs: list[int]  # 統治星座起始度數（0-based，每30°一個星座）
    exaltation_sign: int     # 擢升星座起始度數（-1 = 無）

    # 視覺色彩（用於 SVG 渲染）
    color: str               # 代表色十六進位碼


# ─────────────────────────────────────────────────────────────────────────────
# 七大行星完整對應資料（帕拉塞爾蘇斯傳統，附文獻來源）
# ─────────────────────────────────────────────────────────────────────────────

PLANET_CORRESPONDENCES: dict[str, PlanetCorrespondence] = {

    "sun": PlanetCorrespondence(
        planet_key="sun",
        symbol="☉",
        name_en="Sol (Sun)",
        name_zh="太陽（Sol）",
        # 金：帕拉塞爾蘇斯明確指出黃金是太陽在金屬王國的印記
        metal_en="Gold",
        metal_zh="黃金",
        metal_latin="Aurum",
        metal_symbol="🜚",
        # 日光草本：向日性植物、黃色圓形花朵即太陽印記
        herbs=["Heliotrope (Heliotropium europaeum)", "St John's Wort (Hypericum perforatum)", "Saffron (Crocus sativus)"],
        herbs_zh=["旋覆花（天芥菜屬）", "聖約翰草（金絲桃）", "番紅花"],
        # 黃金色、溫暖光澤之石
        minerals=["Topaz", "Chrysolite", "Heliodor (Golden Beryl)"],
        minerals_zh=["黃玉", "橄欖石", "金綠柱石"],
        body_part_en="Heart, Vital Spirit (spiritus vitalis)",
        body_part_zh="心臟、生命精氣",
        temperament_en="Choleric",
        temperament_zh="膽汁質（火熱乾燥）",
        alchemical_stage="Citrinitas",
        stage_zh="黃化（過渡階段）",
        # 帕拉塞爾蘇斯在 Coelum Philosophorum 中將黃金/太陽置於煉金過程的核心
        source="Paracelsus, Coelum Philosophorum (c.1525); Astronomia Magna (1537-38), Part I",
        ruling_signs=[120],   # 獅子座 Leo (120–150°)
        exaltation_sign=0,    # 白羊座 Aries (0–30°)
        color="#D4AF37",
    ),

    "moon": PlanetCorrespondence(
        planet_key="moon",
        symbol="☽",
        name_en="Luna (Moon)",
        name_zh="月亮（Luna）",
        metal_en="Silver",
        metal_zh="白銀",
        metal_latin="Argentum",
        metal_symbol="🜛",
        # 月光植物：夜間開放、白色花朵、多水分的植物
        herbs=["Mugwort (Artemisia vulgaris)", "Moonwort (Botrychium lunaria)", "White Poppy (Papaver somniferum)"],
        herbs_zh=["艾草（歐洲艾）", "月牙草（扇蕨屬）", "白罌粟"],
        minerals=["Selenite", "Pearl", "Moonstone"],
        minerals_zh=["月光石膏（透石膏）", "珍珠", "月長石"],
        body_part_en="Brain, Phlegm, Reproductive fluids",
        body_part_zh="大腦、痰液、生殖體液",
        temperament_en="Phlegmatic",
        temperament_zh="黏液質（寒冷濕潤）",
        alchemical_stage="Albedo",
        stage_zh="白化（純化階段）",
        source="Paracelsus, Astronomia Magna (1537-38); De Natura Rerum, Book VII",
        ruling_signs=[90],    # 巨蟹座 Cancer (90–120°)
        exaltation_sign=30,   # 金牛座 Taurus (30–60°)
        color="#C0C8D0",
    ),

    "mars": PlanetCorrespondence(
        planet_key="mars",
        symbol="♂",
        name_en="Mars",
        name_zh="火星（Mars）",
        metal_en="Iron",
        metal_zh="鐵",
        metal_latin="Ferrum",
        metal_symbol="🜜",
        # 火星植物：有刺、紅色、灼熱性質，帕拉塞爾蘇斯詳述
        herbs=["Wormwood (Artemisia absinthium)", "Garlic (Allium sativum)", "Nettles (Urtica dioica)"],
        herbs_zh=["苦艾草", "大蒜", "蕁麻"],
        minerals=["Bloodstone (Heliotrope)", "Red Jasper", "Magnetite"],
        minerals_zh=["血石（日光石）", "紅碧玉", "磁鐵礦"],
        body_part_en="Gallbladder, Bile (chole), Muscles",
        body_part_zh="膽囊、膽汁、肌肉",
        temperament_en="Choleric",
        temperament_zh="膽汁質（火熱乾燥）",
        alchemical_stage="Nigredo",
        stage_zh="黑化（腐化分解）",
        source="Paracelsus, De Natura Rerum (1537); De Mineralibus; Archidoxes of Magic",
        ruling_signs=[0, 210],   # 白羊座 Aries + 天蠍座 Scorpio
        exaltation_sign=270,     # 摩羯座 Capricorn (270–300°)
        color="#8B0000",
    ),

    "mercury": PlanetCorrespondence(
        planet_key="mercury",
        symbol="☿",
        name_en="Mercury",
        name_zh="水星（Mercury）",
        # 水銀（汞）：帕拉塞爾蘇斯三原質之首
        metal_en="Mercury (Quicksilver)",
        metal_zh="水銀（汞）",
        metal_latin="Hydrargyrum / Mercurius",
        metal_symbol="☿",
        # 羽狀、精細、善於溝通的植物
        herbs=["Fennel (Foeniculum vulgare)", "Lavender (Lavandula angustifolia)", "Parsley (Petroselinum crispum)"],
        herbs_zh=["茴香", "薰衣草", "歐芹（巴西利）"],
        minerals=["Agate", "Cinnabar (Quicksilver ore)", "Opal"],
        minerals_zh=["瑪瑙", "辰砂（朱砂/汞礦）", "蛋白石"],
        body_part_en="Lungs, Nervous system, Speech organs",
        body_part_zh="肺部、神經系統、言語器官",
        temperament_en="Sanguine",
        temperament_zh="多血質（溫暖濕潤）",
        alchemical_stage="Albedo",
        stage_zh="白化（昇華分離）",
        source="Paracelsus, Concerning the Spirits of the Planets (c.1530); Opus Paramirum, Book I",
        ruling_signs=[60, 150],  # 雙子座 Gemini + 處女座 Virgo
        exaltation_sign=150,     # 處女座 Virgo (150–180°)
        color="#7EB8C9",
    ),

    "jupiter": PlanetCorrespondence(
        planet_key="jupiter",
        symbol="♃",
        name_en="Jupiter",
        name_zh="木星（Jupiter）",
        metal_en="Tin",
        metal_zh="錫",
        metal_latin="Stannum",
        metal_symbol="🜩",
        # 木星植物：苦中帶甘、大葉、滋養性植物
        herbs=["Agrimony (Agrimonia eupatoria)", "Sage (Salvia officinalis)", "Wood Betony (Betonica officinalis)"],
        herbs_zh=["龍芽草", "鼠尾草", "林間水蘇"],
        minerals=["Amethyst", "Sapphire", "Lapis Lazuli"],
        minerals_zh=["紫水晶", "藍寶石", "青金石"],
        body_part_en="Liver, Blood, Right ear",
        body_part_zh="肝臟、血液、右耳",
        temperament_en="Sanguine",
        temperament_zh="多血質（溫暖濕潤）",
        alchemical_stage="Rubedo",
        stage_zh="赤化（擴展完成）",
        # 阿格里帕在《神秘哲學三書》第一卷明確列出木星對應的草本與金屬
        source="Agrippa, Three Books of Occult Philosophy, Book I, Ch. XXIV (1531); Paracelsus, Astronomia Magna",
        ruling_signs=[240, 330],  # 射手座 Sagittarius + 雙魚座 Pisces
        exaltation_sign=90,       # 巨蟹座 Cancer (90–120°)
        color="#4169E1",
    ),

    "venus": PlanetCorrespondence(
        planet_key="venus",
        symbol="♀",
        name_en="Venus",
        name_zh="金星（Venus）",
        metal_en="Copper",
        metal_zh="銅",
        metal_latin="Cuprum",
        metal_symbol="🜙",
        # 金星植物：芬芳、柔美、與愛和美有關
        herbs=["Maidenhair Fern (Adiantum capillus-veneris)", "Vervain (Verbena officinalis)", "Rose (Rosa canina)"],
        herbs_zh=["鐵線蕨（維納斯之髮）", "馬鞭草", "玫瑰（犬薔薇）"],
        minerals=["Malachite", "Emerald", "Copper ore (Chalcopyrite)"],
        minerals_zh=["孔雀石", "祖母綠", "黃銅礦"],
        body_part_en="Kidneys, Generative organs, Throat",
        body_part_zh="腎臟、生殖器官、喉嚨",
        temperament_en="Phlegmatic/Sanguine",
        temperament_zh="黏液質兼多血質（溫潤平衡）",
        alchemical_stage="Albedo",
        stage_zh="白化（美化淨化）",
        source="Paracelsus, Astronomia Magna (1537-38); Concerning the Spirits of the Planets",
        ruling_signs=[30, 180],  # 金牛座 Taurus + 天秤座 Libra
        exaltation_sign=330,     # 雙魚座 Pisces (330–360°)
        color="#228B22",
    ),

    "saturn": PlanetCorrespondence(
        planet_key="saturn",
        symbol="♄",
        name_en="Saturn",
        name_zh="土星（Saturn）",
        metal_en="Lead",
        metal_zh="鉛",
        metal_latin="Plumbum",
        metal_symbol="🜪",
        # 土星植物：苦澀、黑暗生長環境、與死亡和腐化相關
        herbs=["Comfrey (Symphytum officinale)", "Horsetail (Equisetum arvense)", "Hemlock (Conium maculatum)"],
        herbs_zh=["聚合草（康弗利）", "問荊（木賊草）", "毒芹"],
        minerals=["Galena (Lead ore)", "Jet (Lignite)", "Obsidian"],
        minerals_zh=["方鉛礦", "黑玉（煤精）", "黑曜石"],
        body_part_en="Spleen, Bones, Teeth, Right ear (cold)",
        body_part_zh="脾臟、骨骼、牙齒",
        temperament_en="Melancholic",
        temperament_zh="憂鬱質（寒冷乾燥）",
        alchemical_stage="Nigredo",
        stage_zh="黑化（原初物質/腐化）",
        # 帕拉塞爾蘇斯在 De Mineralibus 中詳述鉛/土星的對應
        source="Paracelsus, De Mineralibus; Coelum Philosophorum (c.1525); Agrippa Book I Ch. XXIII",
        ruling_signs=[270, 300],  # 摩羯座 Capricorn + 水瓶座 Aquarius
        exaltation_sign=180,      # 天秤座 Libra (180–210°)
        color="#6B5B45",
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# 煉金四階段（Opus Magnum）— 帕拉塞爾蘇斯傳統
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AlchemicalStageInfo:
    """煉金大功（Opus Magnum）各階段描述。"""
    key: str             # 英文鍵名
    name_la: str         # 拉丁名
    name_zh: str         # 中文名
    color: str           # 代表色
    planets: list[str]   # 關聯行星（planet_key）
    metal: str           # 關聯金屬
    description_en: str  # 英文說明
    description_zh: str  # 中文說明
    source: str          # 文獻來源


ALCHEMICAL_STAGES: dict[str, AlchemicalStageInfo] = {
    "nigredo": AlchemicalStageInfo(
        key="nigredo",
        name_la="Nigredo",
        name_zh="黑化（Nigredo）",
        color="#1A1A1A",
        planets=["saturn", "mars"],
        metal="Lead / Iron（鉛／鐵）",
        description_en="The blackening; putrefaction of prima materia. Saturn presides over the dissolution of form into raw chaos. The first stage of the Great Work.",
        description_zh="黑化，原初物質的腐爛分解。土星主宰形體消融於混沌之中。煉金大功的第一階段，對應死亡與再生前的黑暗。",
        source="Paracelsus, Coelum Philosophorum; De Natura Rerum, Book I; Agrippa, Occult Philosophy",
    ),
    "albedo": AlchemicalStageInfo(
        key="albedo",
        name_la="Albedo",
        name_zh="白化（Albedo）",
        color="#E8E8F0",
        planets=["moon", "mercury", "venus"],
        metal="Silver / Quicksilver（銀／汞）",
        description_en="The whitening; purification after putrefaction. The Moon presides over the washing (ablutio) of the blackened matter into pristine white. Second stage.",
        description_zh="白化，腐化後的淨化階段。月亮主宰洗滌黑化物質使其純白。第二階段，象徵靈魂的淨化與潛意識的浮現。",
        source="Paracelsus, Astronomia Magna (1537-38); Concerning the Spirits of the Planets",
    ),
    "citrinitas": AlchemicalStageInfo(
        key="citrinitas",
        name_la="Citrinitas",
        name_zh="黃化（Citrinitas）",
        color="#DAA520",
        planets=["sun"],
        metal="Gold transition（黃金過渡）",
        description_en="The yellowing; transition from silver to gold. A stage particularly emphasised by Paracelsus as the dawn of the solar principle entering the work.",
        description_zh="黃化，由銀向金過渡。帕拉塞爾蘇斯特別強調此中間階段，太陽原則開始進入煉金大功，象徵智慧的黎明。",
        source="Paracelsus, Coelum Philosophorum; Archidoxes of Magic",
    ),
    "rubedo": AlchemicalStageInfo(
        key="rubedo",
        name_la="Rubedo",
        name_zh="赤化（Rubedo）",
        color="#8B1A1A",
        planets=["sun", "jupiter"],
        metal="Gold（黃金）",
        description_en="The reddening; final perfection and completion. The Sun brings the Great Work to its culmination — the Philosopher's Stone, perfect gold, the healed soul.",
        description_zh="赤化，最終完成與圓滿。太陽引領煉金大功達到頂峰——賢者之石、完美黃金、靈魂的全癒。",
        source="Paracelsus, Coelum Philosophorum; Agrippa, Three Books of Occult Philosophy, Book III",
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# 行星統治星座映射（完整查找表）
# ─────────────────────────────────────────────────────────────────────────────

# 黃道度數 → 星座索引（0-11），每30°一個星座
def longitude_to_sign_index(longitude: float) -> int:
    """將黃道度數（0–360°）轉換為星座索引（0–11）。"""
    return int(longitude % 360 / 30)


# 行星尊貴點數：統治宮 +5，擢升宮 +4，互涉 +1
DIGNITY_SCORES: dict[str, dict[int, int]] = {
    "sun":     {4: 5, 0: 4},               # 統治獅子座(4)，擢升白羊座(0)
    "moon":    {3: 5, 1: 4},               # 統治巨蟹座(3)，擢升金牛座(1)
    "mars":    {0: 5, 7: 5, 9: 4},         # 統治白羊(0)+天蠍(7)，擢升摩羯(9)
    "mercury": {2: 5, 5: 5},                # 統治雙子(2)，統治/擢升處女(5)；Paracelsus 傳統統治宮優先，同宮取 5
    "jupiter": {8: 5, 11: 5, 3: 4},        # 統治射手(8)+雙魚(11)，擢升巨蟹(3)
    "venus":   {1: 5, 6: 5, 11: 4},        # 統治金牛(1)+天秤(6)，擢升雙魚(11)
    "saturn":  {9: 5, 10: 5, 6: 4},        # 統治摩羯(9)+水瓶(10)，擢升天秤(6)
}


# 便捷列表（有序，供前端迭代）
PLANET_KEYS: list[str] = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]
