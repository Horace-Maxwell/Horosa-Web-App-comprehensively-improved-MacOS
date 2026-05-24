"""
astro/andean/models.py — Andean Dark Constellation data table
=============================================================

Data model and catalogue for the Yana Phuyu (暗星宿 / Dark Cloud Constellations)
of the Andean sky.  Each constellation is defined by:

  • Quechua / Spanish / Chinese / English names
  • Approximate galactic-coordinate polygon (l, b in degrees)
  • J2000 equatorial anchor point (RA, Dec in degrees)
  • Peak-visibility months (Southern-Hemisphere austral year)
  • Cultural meaning, myth, and agricultural omen

Source data:
  Gary Urton (1981) *At the Crossroads of the Earth and Sky*
  Urton & Bauer (2004) *Calendar Keeping in a Native Andean Community*
  Schechner & Aveni (eds., 1997) *Inca Astrophysics*
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Core data model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class DarkConstellation:
    """One Andean dark cloud constellation (Yana Phuyu).

    Attributes:
        key:                  Internal string identifier.
        names:                Multi-language names: qu / es / zh / en.
        galactic_bbox:        Approximate polygon of the dark-cloud region as a list
                              of (galactic_longitude_deg, galactic_latitude_deg) tuples.
        anchor_ra_dec_j2000:  Reference centroid in equatorial coords (RA, Dec, degrees J2000).
        season_window_months: Calendar months (1–12) when this constellation is most
                              visible after local sunset from the Andean altiplano
                              (roughly lat −13° to −16°, Cusco region).
        meaning:              zh / en cultural meaning.
        myth:                 zh / en short mythological narrative.
        agro_omen:            zh / en agricultural / weather omen.
        cross_refs:           Optional cross-references to other traditions (e.g. Chinese
                              lunar mansions, Vedic Nakshatra, Western fixed stars).
    """

    key: str
    names: Dict[str, str]
    galactic_bbox: List[Tuple[float, float]]
    anchor_ra_dec_j2000: Tuple[float, float]
    season_window_months: List[int]
    meaning: Dict[str, str]
    myth: Dict[str, str]
    agro_omen: Dict[str, str]
    cross_refs: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class BrightMarker:
    """A bright Andean stellar marker (not a dark cloud).

    Attributes:
        key:                  Identifier.
        names:                Multi-language names.
        anchor_ra_dec_j2000:  Equatorial coords of the primary star (RA, Dec, degrees).
        swe_name:             Swiss Ephemeris fixed-star name (empty string if a cluster).
        meaning:              zh / en.
        heliacal_month_approx: Month of approximate heliacal rising (Southern Hemisphere).
    """

    key: str
    names: Dict[str, str]
    anchor_ra_dec_j2000: Tuple[float, float]
    swe_name: str
    meaning: Dict[str, str]
    heliacal_month_approx: int


# ─────────────────────────────────────────────────────────────────────────────
# Dark Constellation catalogue
# ─────────────────────────────────────────────────────────────────────────────

ANDEAN_DARK_CONSTELLATIONS: List[DarkConstellation] = [
    DarkConstellation(
        key="qatachillay",
        names={
            "qu": "Qatachillay",
            "es": "Llama Madre y Cría",
            "zh": "母駱馬與幼駱馬",
            "en": "Llama & Baby Llama",
        },
        # Approximate dark-cloud region around the Coalsack nebula and adjacent rift
        # covering roughly l=295°–340°, b=−20° to 0°
        galactic_bbox=[
            (295, -5), (305, -18), (320, -22), (338, -14),
            (340, -6), (332, -2), (318, 0), (302, -2),
        ],
        anchor_ra_dec_j2000=(248.0, -38.0),   # near alpha/beta Centauri
        season_window_months=[5, 6, 7, 8, 9],
        meaning={
            "zh": "母性、馱運、群體保護、繁殖力",
            "en": "Nurture, endurance, herd protection, fertility",
        },
        myth={
            "zh": (
                "天河中的神聖駱馬（Yakana）守護人間所有駱馬的生命與水源。"
                "母駱馬引領小駱馬同行，象徵 Pachamama 的無盡慈悲。"
                "每年農曆八月前後，母駱馬在天頂升起，預示雨季即將到來。"
            ),
            "en": (
                "The celestial llama Yakana guards all llamas on Earth and the water "
                "sources that sustain them.  The mother and her cria travel together, "
                "symbolising Pachamama's boundless compassion.  Around August the llama "
                "climbs to the zenith, heralding the approaching rainy season."
            ),
        },
        agro_omen={
            "zh": "輪廓清晰明亮：雨季豐沛，牧場肥美；輪廓昏暗模糊：旱象，需加強水利祭儀。",
            "en": (
                "Clear bright outline: abundant rains and lush pastures; "
                "faint or diffuse shape: drought risk — intensify water-rite ceremonies."
            ),
        },
        cross_refs={
            "zh_lunar_mansion": "尾宿（第18宿）區域",
            "vedic_nakshatra": "Jyeshtha / Mula",
            "western_fixed_star": "Near Antares (alpha Scorpii) region",
        },
    ),

    DarkConstellation(
        key="hampatu",
        names={
            "qu": "Hamp'atu",
            "es": "Sapo",
            "zh": "蟾蜍",
            "en": "Toad",
        },
        galactic_bbox=[
            (336, -8), (346, -11), (354, -9),
            (352, -3), (344, -2), (337, -3),
        ],
        anchor_ra_dec_j2000=(266.0, -29.0),   # region around Sagittarius dark lanes
        season_window_months=[10, 11, 12, 1],
        meaning={
            "zh": "雨訊、播種時機、地底世界（Uku Pacha）的使者",
            "en": "Rain harbinger, sowing timing, messenger from Uku Pacha (underworld)",
        },
        myth={
            "zh": (
                "蟾蜍是地底世界（Uku Pacha）的守護者與信使。"
                "牠的歌聲呼喚雲雨，每當蟾蜍在天河中升起，農人便知播種時機已近。"
            ),
            "en": (
                "The toad is guardian and messenger of Uku Pacha (the inner/lower world). "
                "Its croaking calls the rains; when the toad rises in Mayu the farmers "
                "know that the sowing season approaches."
            ),
        },
        agro_omen={
            "zh": "提早可見：降雨提早，豐收可期；延遲出現：播種延後，謹慎備糧。",
            "en": (
                "Early visibility: earlier rains and good harvest prospects; "
                "late appearance: delay sowing and prepare food reserves."
            ),
        },
        cross_refs={
            "zh_lunar_mansion": "斗宿（第21宿）附近",
            "vedic_nakshatra": "Purva Ashadha",
            "western_fixed_star": "Sagittarius dark rift region",
        },
    ),

    DarkConstellation(
        key="machaqway",
        names={
            "qu": "Mach'aqway",
            "es": "Serpiente",
            "zh": "蛇",
            "en": "Serpent",
        },
        galactic_bbox=[
            (350, -4), (2, 2), (14, 4), (22, 2),
            (18, -2), (8, -4), (356, -5),
        ],
        anchor_ra_dec_j2000=(280.0, -23.0),   # northern Sagittarius / Scutum rift
        season_window_months=[8, 9, 10],
        meaning={
            "zh": "地氣、轉化、警醒、三界通道",
            "en": "Earth-force, transformation, vigilance, gateway between worlds",
        },
        myth={
            "zh": (
                "蛇在天河中巡行，象徵連通 Hanan Pacha（上界）、Kay Pacha（現世）"
                "與 Uku Pacha（下界）的神聖通道。"
                "目睹蛇形於天河，意味宇宙正在更新，人應覺醒與轉化。"
            ),
            "en": (
                "The serpent courses through Mayu as a living conduit linking the three "
                "worlds: Hanan Pacha (the upper realm), Kay Pacha (this world), and "
                "Uku Pacha (the underworld).  Seeing the serpent in the Milky Way "
                "signals cosmic renewal and calls for personal transformation."
            ),
        },
        agro_omen={
            "zh": "蛇形清晰：大地更新、作物換代吉兆；邊界模糊：病蟲害風險上升，宜祭儀防護。",
            "en": (
                "Clear serpent shape: earth renewal, good for crop rotation; "
                "blurred edges: elevated pest and disease pressure — "
                "perform protective rituals."
            ),
        },
        cross_refs={
            "zh_lunar_mansion": "牛宿（第22宿）南側",
            "vedic_nakshatra": "Uttara Ashadha / Abhijit",
            "western_fixed_star": "Scutum / Serpens region",
        },
    ),

    DarkConstellation(
        key="atoq",
        names={
            "qu": "Atoq",
            "es": "Zorro",
            "zh": "狐狸",
            "en": "Fox",
        },
        galactic_bbox=[
            (14, -7), (24, -9), (32, -7),
            (28, -1), (20, 0), (15, -2),
        ],
        anchor_ra_dec_j2000=(296.0, -21.0),   # Aquila / Scutum region
        season_window_months=[12, 1, 2],
        meaning={
            "zh": "試煉、機智、邊境生存、盜賊與守護的雙重性",
            "en": "Trial, cunning, edge survival; the dual nature of thief and guardian",
        },
        myth={
            "zh": (
                "狐狸緊跟在幼駱馬（Uña Llama）之後，測試人們是否警覺。"
                "祂象徵狡黠的試煉，提醒人在豐年中不可鬆懈。"
                "同時，能夠識別狐狸之人，具備在邊境與荒野中生存的智慧。"
            ),
            "en": (
                "The fox follows close behind the young llama, testing human vigilance. "
                "It symbolises the cunning trial that warns against complacency in good "
                "times.  At the same time, one who recognises the fox possesses the "
                "wisdom needed to survive on the frontier and in wild places."
            ),
        },
        agro_omen={
            "zh": "狐狸輪廓突顯：防農作物被偷食，警惕突發災害；星形模糊：試煉期稍緩。",
            "en": (
                "Prominent fox shape: guard crops against predation, beware sudden losses; "
                "faint shape: the season of trial is less intense."
            ),
        },
        cross_refs={
            "zh_lunar_mansion": "女宿（第23宿）附近",
            "vedic_nakshatra": "Sravana / Dhanishtha",
            "western_fixed_star": "Aquila / Altair region",
        },
    ),

    DarkConstellation(
        key="lluthu",
        names={
            "qu": "Lluthu",
            "es": "Perdiz / Tinamú",
            "zh": "山鶉",
            "en": "Partridge / Tinamou",
        },
        galactic_bbox=[
            (290, 0), (298, -4), (308, -5), (314, -2),
            (310, 3), (298, 4),
        ],
        anchor_ra_dec_j2000=(232.0, -42.0),   # Crux / Centaurus vicinity
        season_window_months=[3, 4, 5, 6],
        meaning={
            "zh": "謙遜、勤勉、低調的富足",
            "en": "Humility, diligence, quiet abundance",
        },
        myth={
            "zh": (
                "山鶉在地面悄悄移動，象徵謙遜而勤勉的日常工作。"
                "牠的出現提醒人：豐收並非來自炫耀，而是來自每日的腳踏實地。"
            ),
            "en": (
                "The tinamou moves quietly on the ground, embodying humble daily labour. "
                "Its appearance reminds us that abundance comes not from display "
                "but from grounded, persistent effort."
            ),
        },
        agro_omen={
            "zh": "明顯可見：農事順遂，腳踏實地可得豐收；難以辨認：提醒謙遜行事。",
            "en": (
                "Clearly visible: farming proceeds smoothly, diligent labour is rewarded; "
                "hard to discern: a reminder to act with humility."
            ),
        },
        cross_refs={
            "zh_lunar_mansion": "角宿（第1宿）南方",
            "vedic_nakshatra": "Chitra",
            "western_fixed_star": "Crux / Centaurus region",
        },
    ),

    DarkConstellation(
        key="kuntur",
        names={
            "qu": "Kuntur",
            "es": "Cóndor",
            "zh": "兀鷹",
            "en": "Condor",
        },
        galactic_bbox=[
            (300, 2), (312, 7), (324, 6),
            (320, 1), (310, -1), (302, 0),
        ],
        anchor_ra_dec_j2000=(240.0, -50.0),   # Southern Cross vicinity
        season_window_months=[4, 5, 6],
        meaning={
            "zh": "高瞻、祖靈傳訊、神聖使者",
            "en": "Far sight, ancestral transmission, sacred messenger",
        },
        myth={
            "zh": (
                "兀鷹是天界（Hanan Pacha）的神聖使者，承載人類的祈禱與死者的靈魂往返。"
                "兀鷹在天頂翱翔，意味祖先正在聆聽；祭儀期間若天河清晰，"
                "表示祈禱已被接受。"
            ),
            "en": (
                "The condor is the sacred messenger of Hanan Pacha (the upper world), "
                "carrying human prayers and the souls of the deceased between worlds. "
                "When the condor soars at the zenith of Mayu, the ancestors are "
                "listening; a clear Milky Way during ceremonies confirms prayers received."
            ),
        },
        agro_omen={
            "zh": "高位清晰：祭儀吉、長途旅行吉；低沉模糊：謹慎行事，避免遠行。",
            "en": (
                "Clear high form: auspicious for ceremonies and long journeys; "
                "low or diffuse: proceed cautiously, avoid distant travel."
            ),
        },
        cross_refs={
            "zh_lunar_mansion": "角宿（第1宿）南側",
            "vedic_nakshatra": "Spica region",
            "western_fixed_star": "Crux (Southern Cross) / Centaurus",
        },
    ),

    DarkConstellation(
        key="michiq",
        names={
            "qu": "Michiq",
            "es": "Pastor",
            "zh": "牧羊人",
            "en": "Shepherd",
        },
        galactic_bbox=[
            (322, -3), (332, -5), (340, -4),
            (337, 1), (328, 2), (323, 0),
        ],
        anchor_ra_dec_j2000=(258.0, -35.0),   # Scorpius dark lane
        season_window_months=[6, 7, 8],
        meaning={
            "zh": "秩序、守護、責任、群體領袖",
            "en": "Order, guardianship, duty, community leadership",
        },
        myth={
            "zh": (
                "牧羊人（Michiq）在天河中守望整個星群，維繫宇宙與社群的秩序。"
                "祂代表 Inca 最高領袖（Sapa Inca）守護人民的責任，"
                "也象徵每一位部落長老的神聖職責。"
            ),
            "en": (
                "The shepherd watches over the whole constellation family in Mayu, "
                "sustaining the order of both cosmos and community.  Michiq represents "
                "the Sapa Inca's duty to guard his people and the sacred responsibility "
                "of every community elder."
            ),
        },
        agro_omen={
            "zh": "牧者明亮：畜牧與家族運勢穩定，領袖決策有效；昏暗：群體需加強凝聚。",
            "en": (
                "Visible shepherd: stable herding and family fortune, "
                "leadership decisions prove effective; "
                "faint: the community needs stronger cohesion."
            ),
        },
        cross_refs={
            "zh_lunar_mansion": "心宿（第17宿）附近",
            "vedic_nakshatra": "Anuradha / Jyeshtha",
            "western_fixed_star": "Antares / Scorpius region",
        },
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Bright-marker catalogue
# ─────────────────────────────────────────────────────────────────────────────

ANDEAN_BRIGHT_MARKERS: List[BrightMarker] = [
    BrightMarker(
        key="collca",
        names={
            "qu": "Collca",
            "es": "Pléyades",
            "zh": "昴宿星團（穀倉）",
            "en": "Pleiades (Granary)",
        },
        anchor_ra_dec_j2000=(56.75, 24.1),
        swe_name="Pleiades",
        meaning={
            "zh": "穀倉、儲糧、豐收預兆、新年起點",
            "en": "Granary, food storage, harvest omen, new-year marker",
        },
        heliacal_month_approx=5,
    ),
    BrightMarker(
        key="chakana",
        names={
            "qu": "Chakana",
            "es": "Cruz del Sur",
            "zh": "南十字座",
            "en": "Southern Cross",
        },
        anchor_ra_dec_j2000=(187.8, -63.1),   # alpha Crucis
        swe_name="Acrux",
        meaning={
            "zh": "宇宙階梯、四方秩序、天地橋樑",
            "en": "Cosmic staircase, four-directional order, bridge between worlds",
        },
        heliacal_month_approx=3,
    ),
    BrightMarker(
        key="orion_belt",
        names={
            "qu": "Chakra qullqa",
            "es": "Cinturón de Orión",
            "zh": "參宿三星（獵人腰帶）",
            "en": "Orion's Belt",
        },
        anchor_ra_dec_j2000=(83.82, -1.94),   # Alnilam
        swe_name="Alnilam",
        meaning={
            "zh": "播種時機、宇宙中軸",
            "en": "Sowing timing, cosmic axis",
        },
        heliacal_month_approx=6,
    ),
    BrightMarker(
        key="venus_chaska",
        names={
            "qu": "Chaska (Venus)",
            "es": "Venus",
            "zh": "金星（晨昏之星）",
            "en": "Venus (Morning / Evening Star)",
        },
        anchor_ra_dec_j2000=(0.0, 0.0),       # computed dynamically
        swe_name="",
        meaning={
            "zh": "英雄使者、戰爭與愛的信使、農業曆法守護",
            "en": "Heroic messenger, herald of war and love, guardian of agro-calendar",
        },
        heliacal_month_approx=0,
    ),
]
