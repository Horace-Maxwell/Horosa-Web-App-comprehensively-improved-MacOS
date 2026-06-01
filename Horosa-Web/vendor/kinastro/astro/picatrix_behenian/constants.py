"""
astro/picatrix_behenian/constants.py — Behenian 15 Fixed Stars Database

Classical Agrippa / Hermes Trismegistus correspondences for the fifteen
Behenian (root / foundation) stars, as transmitted through:

  • Heinrich Cornelius Agrippa, *De Occulta Philosophia* Bk I ch. 32 (1531)
  • *Ghayat al-Hakim* (Picatrix), Arabic c. 10th c. CE; Castilian c. 1256 CE
  • Hermes Trismegistus (attributed), *Liber Hermetis de XV Stellis*

The table includes:
  - tropical longitude (J2000 / ~2025 approximate value)
  - planetary rulers (primary + secondary)
  - gemstone, herb / plant, color, incense
  - traditional use / talisman power
  - classical invocation text (Latin + English + Chinese)
  - Unicode sigil placeholder (☽★ etc.) for each star

This module is intentionally extensible: add more stars by appending
``BehenianStar`` instances to ``BEHENIAN_STARS``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


# ============================================================
# Data Class
# ============================================================

@dataclass
class BehenianStar:
    """
    One of the fifteen Behenian fixed stars with full magical correspondences.

    Attributes
    ----------
    name : str
        Classical Latin/Arabic name (Agrippa spelling).
    modern_name : str
        Modern Bayer designation.
    cn_name : str
        Traditional Chinese transliteration / name.
    swe_name : str
        Swiss Ephemeris ``fixstar`` lookup name (empty string → use ``name``).
    longitude : float
        Approximate tropical ecliptic longitude for epoch ~J2025.0 (degrees).
    sign : str
        Zodiac sign (derived from longitude).
    sign_degree : float
        Degree within the sign.
    primary_ruler : str
        Primary planetary ruler (Agrippa attribution).
    secondary_ruler : str
        Secondary planetary ruler.
    gemstone : str
        Agrippa / Hermes gemstone for talisman.
    gemstone_cn : str
        Chinese name for the gemstone.
    herb : str
        Plant / herb used in talisman making.
    herb_cn : str
        Chinese name for the herb.
    color : str
        Ritual / talisman color.
    color_cn : str
        Chinese name for the color.
    incense : str
        Recommended incense.
    incense_cn : str
        Chinese name for the incense.
    magic_uses : list[str]
        List of English magical purposes.
    magic_uses_cn : list[str]
        List of Chinese magical purposes.
    talisman_power : str
        Short English summary of talisman power.
    talisman_power_cn : str
        Chinese talisman power summary.
    invocation_latin : str
        Classical Latin invocation (Agrippa / Hermes).
    invocation_en : str
        English translation of invocation.
    invocation_cn : str
        Chinese translation of invocation.
    sigil : str
        Unicode sigil placeholder (SVG path or special character).
    image_description : str
        Classical image to engrave on talisman (Agrippa description).
    image_description_cn : str
        Chinese description of the engraved image.
    magnitude : float
        Apparent magnitude (for display purposes).
    nature : str
        Benefic / malefic nature (classical, abbreviated).
    """

    name: str
    modern_name: str
    cn_name: str
    swe_name: str
    longitude: float
    sign: str
    sign_degree: float
    primary_ruler: str
    secondary_ruler: str
    gemstone: str
    gemstone_cn: str
    herb: str
    herb_cn: str
    color: str
    color_cn: str
    incense: str
    incense_cn: str
    magic_uses: List[str] = field(default_factory=list)
    magic_uses_cn: List[str] = field(default_factory=list)
    talisman_power: str = ""
    talisman_power_cn: str = ""
    invocation_latin: str = ""
    invocation_en: str = ""
    invocation_cn: str = ""
    sigil: str = "✦"
    image_description: str = ""
    image_description_cn: str = ""
    magnitude: float = 2.0
    nature: str = ""


# ============================================================
# Zodiac Sign Helper
# ============================================================

_ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

_ZODIAC_SIGNS_CN = [
    "牡羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座",
    "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座",
]


def _sign_from_lon(lon: float) -> str:
    return _ZODIAC_SIGNS[int(lon / 30) % 12]


def _sign_degree_from_lon(lon: float) -> float:
    return round(lon % 30, 2)


# ============================================================
# Behenian 15 Fixed Stars — Complete Table
# ============================================================

BEHENIAN_STARS: List[BehenianStar] = [

    BehenianStar(
        name="Algol",
        modern_name="β Persei",
        cn_name="大陵五（惡魔之星）",
        swe_name="Algol",
        longitude=56.10,
        sign=_sign_from_lon(56.10),
        sign_degree=_sign_degree_from_lon(56.10),
        primary_ruler="Saturn",
        secondary_ruler="Jupiter",
        gemstone="Diamond",
        gemstone_cn="鑽石",
        herb="Black Hellebore",
        herb_cn="黑藜蘆",
        color="Black",
        color_cn="黑色",
        incense="Myrrh",
        incense_cn="沒藥",
        magic_uses=["Protection", "Victory over enemies", "Courage", "Defense"],
        magic_uses_cn=["保護", "戰勝敵人", "勇氣", "防禦"],
        talisman_power="Protection, victory over enemies, courage",
        talisman_power_cn="保護、戰勝敵人、賦予勇氣",
        invocation_latin="O Algol, stella Saturni et Jovis, da mihi victoriam contra inimicos meos!",
        invocation_en="O Algol, star of Saturn and Jupiter, grant me victory over my enemies!",
        invocation_cn="哦，大陵五，土星與木星之星，賜予我戰勝敵人之力！",
        sigil="⊕",
        image_description="A man's head with a serpent wound around the neck.",
        image_description_cn="一個男人的頭部，頸部纏繞蛇形。",
        magnitude=2.12,
        nature="Malefic",
    ),

    BehenianStar(
        name="Pleiades",
        modern_name="η Tauri (Alcyone)",
        cn_name="昴宿（七姊妹星團）",
        swe_name="Alcyone",
        longitude=60.05,
        sign=_sign_from_lon(60.05),
        sign_degree=_sign_degree_from_lon(60.05),
        primary_ruler="Moon",
        secondary_ruler="Mars",
        gemstone="Rock Crystal",
        gemstone_cn="水晶",
        herb="Fennel",
        herb_cn="茴香",
        color="Silver",
        color_cn="銀色",
        incense="Frankincense",
        incense_cn="乳香",
        magic_uses=["Improve eyesight", "Love spells", "Increase wealth", "Acquire hidden knowledge"],
        magic_uses_cn=["增強視力", "愛情魔法", "增加財富", "獲取隱秘知識"],
        talisman_power="Increase eyesight, love, wealth",
        talisman_power_cn="增強視力、促進愛情、增加財富",
        invocation_latin="O Pleiades, stellae Lunae et Martis, da mihi amorem et divitias!",
        invocation_en="O Pleiades, stars of the Moon and Mars, grant me love and riches!",
        invocation_cn="哦，昴宿，月亮與火星之星，賜予我愛情與財富！",
        sigil="✦",
        image_description="A small lamp or the figure of a grieving woman.",
        image_description_cn="一盞小燈，或一位悲傷女性的形象。",
        magnitude=2.87,
        nature="Moderately Malefic",
    ),

    BehenianStar(
        name="Aldebaran",
        modern_name="α Tauri",
        cn_name="畢宿五（公牛之眼）",
        swe_name="Aldebaran",
        longitude=70.03,
        sign=_sign_from_lon(70.03),
        sign_degree=_sign_degree_from_lon(70.03),
        primary_ruler="Mars",
        secondary_ruler="Venus",
        gemstone="Ruby",
        gemstone_cn="紅寶石",
        herb="Milk Thistle",
        herb_cn="奶薊草",
        color="Red",
        color_cn="紅色",
        incense="Dragon's Blood",
        incense_cn="龍血",
        magic_uses=["Honor", "Riches", "Eloquence", "Leadership", "Military success"],
        magic_uses_cn=["榮耀", "財富", "口才", "領導力", "軍事成功"],
        talisman_power="Honor, riches, eloquence",
        talisman_power_cn="名譽、財富、口才",
        invocation_latin="O Aldebaran, stella Martis et Veneris, da mihi honorem et eloquentiam!",
        invocation_en="O Aldebaran, star of Mars and Venus, grant me honor and eloquence!",
        invocation_cn="哦，畢宿五，火星與金星之星，賜予我榮耀與口才！",
        sigil="♈",
        image_description="A key, or a flying figure brandishing a sword.",
        image_description_cn="一把鑰匙，或持劍飛翔的形象。",
        magnitude=0.87,
        nature="Benefic",
    ),

    BehenianStar(
        name="Capella",
        modern_name="α Aurigae",
        cn_name="五車二（御夫座α）",
        swe_name="Capella",
        longitude=82.19,
        sign=_sign_from_lon(82.19),
        sign_degree=_sign_degree_from_lon(82.19),
        primary_ruler="Jupiter",
        secondary_ruler="Saturn",
        gemstone="Sapphire",
        gemstone_cn="藍寶石",
        herb="Horehound",
        herb_cn="苦薄荷",
        color="Blue",
        color_cn="藍色",
        incense="Storax",
        incense_cn="蘇合香",
        magic_uses=["Honor", "Wealth", "Favor of kings", "Nobility", "Good fortune"],
        magic_uses_cn=["榮耀", "財富", "獲得王侯青睞", "高貴", "好運"],
        talisman_power="Honor, wealth, favor of kings",
        talisman_power_cn="名譽、財富、獲得王侯之恩寵",
        invocation_latin="O Capella, stella Iovis et Saturni, da mihi favorem regum et divitias!",
        invocation_en="O Capella, star of Jupiter and Saturn, grant me the favor of kings and wealth!",
        invocation_cn="哦，五車二，木星與土星之星，賜予我王者的恩寵與財富！",
        sigil="♃",
        image_description="A man in armor, or a crowned figure seated on a throne.",
        image_description_cn="一個武裝男人，或坐在王座上的加冕人物。",
        magnitude=0.08,
        nature="Benefic",
    ),

    BehenianStar(
        name="Sirius",
        modern_name="α Canis Majoris",
        cn_name="天狼星（大犬座α）",
        swe_name="Sirius",
        longitude=104.08,
        sign=_sign_from_lon(104.08),
        sign_degree=_sign_degree_from_lon(104.08),
        primary_ruler="Jupiter",
        secondary_ruler="Mars",
        gemstone="Beryl",
        gemstone_cn="綠柱石",
        herb="Juniper",
        herb_cn="杜松",
        color="Gold",
        color_cn="金色",
        incense="Mastic",
        incense_cn="乳香脂",
        magic_uses=["Honor", "Fame", "Good fortune", "Preservation of health", "Favor of spirits"],
        magic_uses_cn=["榮耀", "聲望", "好運", "保持健康", "獲得靈性眷顧"],
        talisman_power="Honor, fame, good fortune",
        talisman_power_cn="名譽、聲望、帶來好運",
        invocation_latin="O Syrius, stella Iovis et Martis, da mihi gloriam et bonam fortunam!",
        invocation_en="O Sirius, star of Jupiter and Mars, grant me glory and good fortune!",
        invocation_cn="哦，天狼星，木星與火星之星，賜予我榮耀與好運！",
        sigil="★",
        image_description="A hound, or a little maiden wearing a crown.",
        image_description_cn="一隻獵犬，或一個戴著皇冠的少女。",
        magnitude=-1.46,
        nature="Benefic",
    ),

    BehenianStar(
        name="Procyon",
        modern_name="α Canis Minoris",
        cn_name="南河三（小犬座α）",
        swe_name="Procyon",
        longitude=116.33,
        sign=_sign_from_lon(116.33),
        sign_degree=_sign_degree_from_lon(116.33),
        primary_ruler="Mercury",
        secondary_ruler="Mars",
        gemstone="Agate",
        gemstone_cn="瑪瑙",
        herb="Pennyroyal",
        herb_cn="薄荷草",
        color="Yellow",
        color_cn="黃色",
        incense="Benzoin",
        incense_cn="安息香",
        magic_uses=["Protection from evil", "Health", "Speed", "Hidden wisdom", "Travel safety"],
        magic_uses_cn=["驅除邪惡", "健康", "迅速", "隱秘智慧", "旅行平安"],
        talisman_power="Protection from evil, health",
        talisman_power_cn="驅除邪惡、保持健康",
        invocation_latin="O Procyon, stella Mercurii et Martis, protege me ab omni malo!",
        invocation_en="O Procyon, star of Mercury and Mars, protect me from all evil!",
        invocation_cn="哦，南河三，水星與火星之星，保護我免受一切邪惡！",
        sigil="☿",
        image_description="A cock, or three maidens standing.",
        image_description_cn="一隻公雞，或三個站立的少女。",
        magnitude=0.40,
        nature="Moderately Benefic",
    ),

    BehenianStar(
        name="Regulus",
        modern_name="α Leonis",
        cn_name="軒轅十四（獅子座α）",
        swe_name="Regulus",
        longitude=150.06,
        sign=_sign_from_lon(150.06),
        sign_degree=_sign_degree_from_lon(150.06),
        primary_ruler="Jupiter",
        secondary_ruler="Mars",
        gemstone="Garnet",
        gemstone_cn="石榴石",
        herb="Celandine",
        herb_cn="白屈菜",
        color="Purple",
        color_cn="紫色",
        incense="Saffron",
        incense_cn="番紅花",
        magic_uses=["Power", "Victory", "Nobility", "Honor", "Courage", "Banish melancholy"],
        magic_uses_cn=["權力", "勝利", "高貴", "榮耀", "勇氣", "驅除憂鬱"],
        talisman_power="Power, victory, nobility",
        talisman_power_cn="賦予權力、帶來勝利、彰顯高貴",
        invocation_latin="O Regulus, stella Iovis et Martis, da mihi victoriam et nobilitatem!",
        invocation_en="O Regulus, star of Jupiter and Mars, grant me victory and nobility!",
        invocation_cn="哦，軒轅十四，木星與火星之星，賜予我勝利與高貴！",
        sigil="♌",
        image_description="A lion, or a king sitting on a throne, crowned.",
        image_description_cn="一頭獅子，或坐在王座上的加冕國王。",
        magnitude=1.35,
        nature="Benefic",
    ),

    BehenianStar(
        name="Algorab",
        modern_name="δ Corvi",
        cn_name="軫宿一（烏鴉座δ）",
        swe_name="Algorab",
        longitude=193.46,
        sign=_sign_from_lon(193.46),
        sign_degree=_sign_degree_from_lon(193.46),
        primary_ruler="Saturn",
        secondary_ruler="Mars",
        gemstone="Black Onyx",
        gemstone_cn="黑瑪瑙",
        herb="Comfrey",
        herb_cn="聚合草",
        color="Black",
        color_cn="黑色",
        incense="Black Pepper",
        incense_cn="黑胡椒",
        magic_uses=["Protection", "Dispel evil", "Destroy enemies", "Obstruction magic"],
        magic_uses_cn=["保護", "驅除邪惡", "消滅敵人", "阻礙魔法"],
        talisman_power="Protection, dispel evil",
        talisman_power_cn="保護、驅除邪惡",
        invocation_latin="O Algorab, stella Saturni et Martis, expelle malum a me!",
        invocation_en="O Algorab, star of Saturn and Mars, expel evil from me!",
        invocation_cn="哦，軫宿一，土星與火星之星，從我身邊驅除邪惡！",
        sigil="⚫",
        image_description="A raven on a serpent, or a black-robed man holding a sword.",
        image_description_cn="站在蛇上的烏鴉，或身著黑袍持劍的男人。",
        magnitude=2.94,
        nature="Malefic",
    ),

    BehenianStar(
        name="Spica",
        modern_name="α Virginis",
        cn_name="角宿一（處女座α）",
        swe_name="Spica",
        longitude=204.20,
        sign=_sign_from_lon(204.20),
        sign_degree=_sign_degree_from_lon(204.20),
        primary_ruler="Venus",
        secondary_ruler="Mercury",
        gemstone="Emerald",
        gemstone_cn="祖母綠",
        herb="Sage",
        herb_cn="鼠尾草",
        color="Green",
        color_cn="綠色",
        incense="Sage",
        incense_cn="鼠尾草",
        magic_uses=["Wealth", "Success", "Love", "Artistic talent", "Agriculture"],
        magic_uses_cn=["財富", "成功", "愛情", "藝術才能", "農業豐收"],
        talisman_power="Wealth, success, love",
        talisman_power_cn="招財、帶來成功與愛情",
        invocation_latin="O Spica, stella Veneris et Mercurii, da mihi divitias et amorem!",
        invocation_en="O Spica, star of Venus and Mercury, grant me wealth and love!",
        invocation_cn="哦，角宿一，金星與水星之星，賜予我財富與愛情！",
        sigil="♀",
        image_description="A bird, or a man in fine clothes with a precious stone.",
        image_description_cn="一隻鳥，或穿著華麗、持寶石的男子。",
        magnitude=0.97,
        nature="Benefic",
    ),

    BehenianStar(
        name="Arcturus",
        modern_name="α Boötis",
        cn_name="大角星（牧夫座α）",
        swe_name="Arcturus",
        longitude=204.39,
        sign=_sign_from_lon(204.39),
        sign_degree=_sign_degree_from_lon(204.39),
        primary_ruler="Jupiter",
        secondary_ruler="Mars",
        gemstone="Jasper",
        gemstone_cn="碧玉",
        herb="Plantain",
        herb_cn="車前草",
        color="Orange",
        color_cn="橙色",
        incense="Frankincense",
        incense_cn="乳香",
        magic_uses=["Protection", "Healing", "Success in travel", "Preservation of body", "Good fortune"],
        magic_uses_cn=["保護", "治癒", "旅行順利", "保持身體健康", "好運"],
        talisman_power="Protection, healing, success in travel",
        talisman_power_cn="保護、治癒、旅行順利",
        invocation_latin="O Arcturus, stella Iovis et Martis, da mihi sanitatem et in via salutem!",
        invocation_en="O Arcturus, star of Jupiter and Mars, grant me health and safety in travel!",
        invocation_cn="哦，大角星，木星與火星之星，賜予我健康與旅途平安！",
        sigil="✴",
        image_description="A horse, or a man riding a horse holding a staff.",
        image_description_cn="一匹馬，或騎馬持杖的男子。",
        magnitude=-0.05,
        nature="Benefic",
    ),

    BehenianStar(
        name="Alphecca",
        modern_name="α Coronae Borealis",
        cn_name="貫索四（北冕座α）",
        swe_name="Alphecca",
        longitude=222.37,
        sign=_sign_from_lon(222.37),
        sign_degree=_sign_degree_from_lon(222.37),
        primary_ruler="Venus",
        secondary_ruler="Mercury",
        gemstone="Topaz",
        gemstone_cn="黃玉",
        herb="Rosemary",
        herb_cn="迷迭香",
        color="White",
        color_cn="白色",
        incense="Roses",
        incense_cn="玫瑰",
        magic_uses=["Love", "Joy", "Protection from poison", "Artistic skill", "Eloquence"],
        magic_uses_cn=["愛情", "喜悅", "防止中毒", "藝術技能", "口才"],
        talisman_power="Love, joy, protection from poison",
        talisman_power_cn="愛情、喜悅、防止中毒",
        invocation_latin="O Alphecca, stella Veneris et Mercurii, da mihi amorem et gaudium!",
        invocation_en="O Alphecca, star of Venus and Mercury, grant me love and joy!",
        invocation_cn="哦，貫索四，金星與水星之星，賜予我愛情與喜悅！",
        sigil="♡",
        image_description="A woman crowned with flowers, or a man crowned with a laurel.",
        image_description_cn="頭戴花冠的女子，或頭戴月桂的男子。",
        magnitude=2.23,
        nature="Benefic",
    ),

    BehenianStar(
        name="Antares",
        modern_name="α Scorpii",
        cn_name="心宿二（天蠍座α）",
        swe_name="Antares",
        longitude=249.93,
        sign=_sign_from_lon(249.93),
        sign_degree=_sign_degree_from_lon(249.93),
        primary_ruler="Mars",
        secondary_ruler="Jupiter",
        gemstone="Sardonyx",
        gemstone_cn="紅縞瑪瑙",
        herb="Coriander",
        herb_cn="芫荽（香菜）",
        color="Red",
        color_cn="紅色",
        incense="Dragon's Blood",
        incense_cn="龍血",
        magic_uses=["Courage", "Protection", "Military success", "Dispel evil spirits", "Victory"],
        magic_uses_cn=["勇氣", "保護", "軍事成功", "驅除惡靈", "勝利"],
        talisman_power="Courage, protection, military success",
        talisman_power_cn="賦予勇氣、保護、軍事勝利",
        invocation_latin="O Antares, stella Martis et Iovis, da mihi fortitudinem et victoriam!",
        invocation_en="O Antares, star of Mars and Jupiter, grant me strength and victory!",
        invocation_cn="哦，心宿二，火星與木星之星，賜予我力量與勝利！",
        sigil="♂",
        image_description="A man armed with a sword, or a scorpion.",
        image_description_cn="手持劍的武士，或天蠍形象。",
        magnitude=1.06,
        nature="Malefic",
    ),

    BehenianStar(
        name="Vega",
        modern_name="α Lyrae",
        cn_name="織女星（天琴座α）",
        swe_name="Vega",
        longitude=285.04,
        sign=_sign_from_lon(285.04),
        sign_degree=_sign_degree_from_lon(285.04),
        primary_ruler="Mercury",
        secondary_ruler="Venus",
        gemstone="Chrysolite",
        gemstone_cn="貴橄欖石",
        herb="Savory",
        herb_cn="香薄荷",
        color="Pale Green",
        color_cn="淡綠色",
        incense="Mastic",
        incense_cn="乳香脂",
        magic_uses=["Favor of princes", "Protection from evil", "Beauty", "Music", "Arts"],
        magic_uses_cn=["獲王侯青睞", "驅除邪惡", "美麗", "音樂", "藝術"],
        talisman_power="Favor of princes, protection from evil",
        talisman_power_cn="獲得王侯青睞、驅除邪惡",
        invocation_latin="O Vega, stella Mercurii et Veneris, da mihi gratiam principum!",
        invocation_en="O Vega, star of Mercury and Venus, grant me the favor of princes!",
        invocation_cn="哦，織女星，水星與金星之星，賜予我王侯的恩寵！",
        sigil="♪",
        image_description="A vulture, or a man playing a lute.",
        image_description_cn="一隻禿鷹，或彈奏琵琶的男子。",
        magnitude=0.03,
        nature="Benefic",
    ),

    BehenianStar(
        name="Alkaid",
        modern_name="η Ursae Majoris",
        cn_name="搖光（北斗七星之末）",
        swe_name="Alkaid",
        longitude=177.68,
        sign=_sign_from_lon(177.68),
        sign_degree=_sign_degree_from_lon(177.68),
        primary_ruler="Moon",
        secondary_ruler="Venus",
        gemstone="Topaz",
        gemstone_cn="黃玉",
        herb="Mugwort",
        herb_cn="艾草",
        color="Silver",
        color_cn="銀色",
        incense="Camphor",
        incense_cn="樟腦",
        magic_uses=["Protection", "Vengeance on enemies", "Safe travels", "Banish evil spirits"],
        magic_uses_cn=["保護", "報復敵人（Picatrix）", "旅行平安", "驅除惡靈"],
        talisman_power="Protection, vengeance on enemies (Picatrix)",
        talisman_power_cn="保護、向敵人復仇（Picatrix）",
        invocation_latin="O Alkaid, stella Lunae et Veneris, protege me et da mihi victoriam super hostes!",
        invocation_en="O Alkaid, star of the Moon and Venus, protect me and grant victory over enemies!",
        invocation_cn="哦，搖光，月亮與金星之星，保護我並賜予我戰勝敵人之力！",
        sigil="☽",
        image_description="A man on a horse holding a lance, or a figure holding a book.",
        image_description_cn="騎馬持矛的男子，或手持書本的人物。",
        magnitude=1.86,
        nature="Moderately Malefic",
    ),

    BehenianStar(
        name="Deneb Algedi",
        modern_name="δ Capricorni",
        cn_name="壘壁陣四（摩羯座δ）",
        swe_name="DenebAlgedi",
        longitude=323.47,
        sign=_sign_from_lon(323.47),
        sign_degree=_sign_degree_from_lon(323.47),
        primary_ruler="Saturn",
        secondary_ruler="Venus",
        gemstone="Chalcedony",
        gemstone_cn="玉髓",
        herb="Marjoram",
        herb_cn="馬鬱蘭",
        color="Dark Brown",
        color_cn="深棕色",
        incense="Civet",
        incense_cn="靈貓香",
        magic_uses=["Increase wealth", "Safety in travel", "Favorable legal outcomes", "Stability"],
        magic_uses_cn=["增加財富", "旅行平安", "法律訴訟順利", "穩定"],
        talisman_power="Increase wealth, safety in travel",
        talisman_power_cn="增加財富、旅行平安",
        invocation_latin="O Deneb Algedi, stella Saturni et Veneris, da mihi divitias et in viis salutem!",
        invocation_en="O Deneb Algedi, star of Saturn and Venus, grant me wealth and safety in journeys!",
        invocation_cn="哦，壘壁陣四，土星與金星之星，賜予我財富與旅途平安！",
        sigil="♑",
        image_description="A fish's tail, or a man in a goat-skin garment.",
        image_description_cn="魚尾形，或穿著山羊皮衣的男子。",
        magnitude=2.85,
        nature="Benefic",
    ),
]


# ============================================================
# Quick Lookup Map
# ============================================================

BEHENIAN_BY_NAME: dict[str, BehenianStar] = {s.name: s for s in BEHENIAN_STARS}

# Planetary ruler index for quick look-ups
RULER_COLORS: dict[str, str] = {
    "Sun":     "#FFC300",
    "Moon":    "#C0C0C0",
    "Mercury": "#B0E0E6",
    "Venus":   "#90EE90",
    "Mars":    "#FF4500",
    "Jupiter": "#6495ED",
    "Saturn":  "#A0A0A0",
}

RULER_CN: dict[str, str] = {
    "Sun":     "太陽",
    "Moon":    "月亮",
    "Mercury": "水星",
    "Venus":   "金星",
    "Mars":    "火星",
    "Jupiter": "木星",
    "Saturn":  "土星",
}

# Magic use categories for filtering
MAGIC_CATEGORIES: dict[str, list[str]] = {
    "Protection":  ["Algol", "Procyon", "Algorab", "Antares", "Alkaid", "Vega"],
    "Love":        ["Pleiades", "Spica", "Alphecca"],
    "Wealth":      ["Pleiades", "Aldebaran", "Capella", "Sirius", "Spica", "Deneb Algedi"],
    "Victory":     ["Algol", "Aldebaran", "Regulus", "Antares"],
    "Healing":     ["Procyon", "Arcturus"],
    "Honor":       ["Aldebaran", "Capella", "Sirius", "Regulus"],
    "Travel":      ["Procyon", "Arcturus", "Alkaid", "Deneb Algedi"],
    "Eloquence":   ["Aldebaran", "Procyon", "Alphecca"],
    "Arts":        ["Spica", "Alphecca", "Vega"],
}

MAGIC_CATEGORIES_CN: dict[str, list[str]] = {
    "保護防禦":   ["Algol", "Procyon", "Algorab", "Antares", "Alkaid", "Vega"],
    "愛情婚姻":   ["Pleiades", "Spica", "Alphecca"],
    "財富招財":   ["Pleiades", "Aldebaran", "Capella", "Sirius", "Spica", "Deneb Algedi"],
    "勝利成功":   ["Algol", "Aldebaran", "Regulus", "Antares"],
    "治癒健康":   ["Procyon", "Arcturus"],
    "名譽榮耀":   ["Aldebaran", "Capella", "Sirius", "Regulus"],
    "旅行平安":   ["Procyon", "Arcturus", "Alkaid", "Deneb Algedi"],
    "口才智慧":   ["Aldebaran", "Procyon", "Alphecca"],
    "藝術才能":   ["Spica", "Alphecca", "Vega"],
}

# Standard Behenian orb (6° as per classical sources)
BEHENIAN_ORB: float = 6.0

# Tighter conjunction orb for "strong activation"
BEHENIAN_STRONG_ORB: float = 1.0
