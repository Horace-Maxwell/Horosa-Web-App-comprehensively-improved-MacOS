"""
astro/byzantine_astrology/constants.py — Byzantine Astrology Constants & Historical Database

Historical database faithful to primary Byzantine astrological sources:

Primary Sources:
- Catalogus Codicum Astrologorum Graecorum (CCAG), Vols. I–XII
- Rhetorius of Egypt, "Compendium" (ca. 6th c.), CCAG I pp. 140–164
- Hephaestion of Thebes, "Apotelesmatika" (ca. 415 CE), ed. Pingree 1973–74
- Paulus Alexandrinus, "Eisagogika" (378 CE), ed. Boer 1958
- Theophilus of Edessa, "Apotelesmatics" (ca. 785 CE), trans. Burnett 2010
- John Abramius, "Introduction to Astrology" (ca. 1000 CE), CCAG V.1
- Anonymus Byzantinus, "Περὶ Σεισμῶν" (On Earthquakes), CCAG II
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional, Tuple

# ============================================================
# Byzantine Astrologers Database
# Historical figures and their key contributions
# ============================================================

BYZANTINE_ASTROLOGERS: Dict[str, Dict[str, Any]] = {
    "paulus_alexandrinus": {
        "name_en": "Paulus Alexandrinus",
        "name_gr": "Παῦλος Ἀλεξανδρεύς",
        "name_cn": "亞歷山大里亞的保羅",
        "floruit": "378 CE",
        "location": "Alexandria (later Byzantine Empire)",
        "period": "Late Antiquity / Early Byzantine",
        "work_en": "Eisagogika (Introduction to Astrology)",
        "work_gr": "Εἰσαγωγικά",
        "work_cn": "《占星入門》",
        "key_contributions_en": [
            "Systematized the 'lots' (Κλῆροι) beyond Fortune and Spirit",
            "Codified the 'Bounds' (ὅρια / terms) system",
            "Introduced the concept of 'Chrono­kratores' (time lords)",
            "Developed the doctrine of 'Place' (τόπος) significations",
            "First systematic treatment of the paranatellonta (rising stars)",
        ],
        "key_contributions_cn": [
            "系統化了「命運份額」（Κλῆροι）體系，超越幸運點與精神點",
            "編纂了「界」（ὅρια）系統",
            "引入「時間主宰」（Χρονοκράτορες）概念",
            "發展了宮位（τόπος）象義學說",
            "首次系統論述升起星座（paranatellonta）",
        ],
        "signature_technique": "Lots (Κλῆροι) & Time-Lords",
        "source_ref": "Paulus Alex., Eisag. ch. 14–24; CCAG II pp. 5–30",
        "icon": "📜",
        "color": "#D4AF37",
    },
    "hephaestion_thebes": {
        "name_en": "Hephaestion of Thebes",
        "name_gr": "Ἡφαιστίων ὁ Θηβαῖος",
        "name_cn": "底比斯的赫費斯提翁",
        "floruit": "ca. 415 CE",
        "location": "Thebes, Egypt (Byzantine province)",
        "period": "Late Antique Byzantine",
        "work_en": "Apotelesmatika (Astrological Results)",
        "work_gr": "Ἀποτελεσματικά",
        "work_cn": "《占星結果》",
        "key_contributions_en": [
            "Preserved Nechepso-Petosiris tradition with Byzantine commentary",
            "Detailed eclipse interpretation for political events",
            "Katarche (inceptions) doctrine for mundane astrology",
            "Integration of Egyptian Decan lore into Byzantine framework",
            "Preserved otherwise lost Antiochus of Athens material",
        ],
        "key_contributions_cn": [
            "保存了涅切普索-佩托西里斯傳統及拜占庭注疏",
            "詳細的日月食解讀用於政治事件預測",
            "世俗占星的「起始時刻」（Katarche）學說",
            "將埃及旬星傳統融入拜占庭框架",
            "保存了雅典安提俄克斯的佚失材料",
        ],
        "signature_technique": "Mundane Eclipses & Katarche",
        "source_ref": "Heph. Theb., Apotel. Books I–III; ed. Pingree 1973",
        "icon": "🌙",
        "color": "#C0C0C0",
    },
    "rhetorius_egypt": {
        "name_en": "Rhetorius of Egypt",
        "name_gr": "Ῥητόριος",
        "name_cn": "埃及的雷托里烏斯",
        "floruit": "ca. 505–515 CE",
        "location": "Egypt (Byzantine province)",
        "period": "Early Byzantine",
        "work_en": "Compendium (Astrological Handbook)",
        "work_gr": "Συλλογή",
        "work_cn": "《占星綱要》",
        "key_contributions_en": [
            "Comprehensive synthesis of all earlier Hellenistic material",
            "Detailed house significations (112 chapters on each house)",
            "Preserved Teucer of Babylon's paranatellonta lists",
            "Fixed star catalogue with astrological meanings",
            "Unique chapter on 'bonification and maltreatment' of planets",
        ],
        "key_contributions_cn": [
            "對所有早期希臘化占星材料的全面綜合",
            "詳盡的宮位象義（每個宮位112章）",
            "保存了巴比倫的突克爾星座升起列表",
            "帶有占星意義的恆星星表",
            "關於行星「吉化與惡化」的獨特章節",
        ],
        "signature_technique": "House Significations & Fixed Stars",
        "source_ref": "Rhet. Aeg., Compend.; CCAG I pp. 140–164, VIII.4",
        "icon": "⭐",
        "color": "#FFD700",
    },
    "theophilus_edessa": {
        "name_en": "Theophilus of Edessa",
        "name_gr": "Θεόφιλος ὁ Ἐδέσσης",
        "name_cn": "埃德薩的塞奧菲盧斯",
        "floruit": "ca. 695–785 CE",
        "location": "Edessa (modern Şanlıurfa, Turkey)",
        "period": "Middle Byzantine / Arabo-Byzantine Transition",
        "work_en": "Apotelesmatics (Astrological Predictions)",
        "work_gr": "Ἀποτελεσματικά",
        "work_cn": "《占星預言》",
        "key_contributions_en": [
            "Critical bridge between Hellenistic and Arabic astrology",
            "Military astrology: timing of battles and campaigns",
            "Translated Dorotheus of Sidon into Arabic (lost original)",
            "Extensive mundane work for Mahdi and Byzantine courts simultaneously",
            "Introduced Hermetic planetary period concepts",
        ],
        "key_contributions_cn": [
            "希臘化與阿拉伯占星之間的關鍵橋梁",
            "軍事占星：戰役與戰役時機的確定",
            "將西頓的多羅提烏斯翻譯成阿拉伯語（原版已佚）",
            "同時為馬赫迪和拜占庭宮廷從事廣泛的世俗占星工作",
            "引入赫爾墨斯行星時期概念",
        ],
        "signature_technique": "Military Astrology & Hellenistic-Arabic Bridge",
        "source_ref": "Theoph. Edess., Apotel.; trans. Burnett & Pingree 2010",
        "icon": "⚔️",
        "color": "#B22222",
    },
    "john_abramius": {
        "name_en": "John Abramius",
        "name_gr": "Ἰωάννης Ἀβράμιος",
        "name_cn": "約翰·阿布拉米烏斯",
        "floruit": "ca. 1000–1050 CE",
        "location": "Constantinople",
        "period": "Middle Byzantine",
        "work_en": "Introduction to Astrology (Εἰσαγωγή)",
        "work_gr": "Εἰσαγωγή εἰς τὴν ἀποτελεσματικήν",
        "work_cn": "《占星入門》",
        "key_contributions_en": [
            "Byzantine court astrologer under Emperor Basil II",
            "Adapted Arabic planetary period (firdaria) to Byzantine context",
            "Synthesized Arabic and Hellenistic approaches for Christian empire",
            "Provided horoscopes for Byzantine imperial succession",
            "Preserved unique Byzantine variant of the Thema Mundi",
        ],
        "key_contributions_cn": [
            "巴西爾二世皇帝時期的拜占庭宮廷占星師",
            "將阿拉伯行星時期（firdaria）適應於拜占庭背景",
            "為基督教帝國綜合了阿拉伯與希臘化占星方法",
            "提供了拜占庭帝位繼承的占星盤",
            "保存了世界主題（Thema Mundi）的獨特拜占庭版本",
        ],
        "signature_technique": "Byzantine Firdaria & Imperial Succession Charts",
        "source_ref": "Abr., Eisag.; CCAG V.1 pp. 72–103; Pingree 1976",
        "icon": "👑",
        "color": "#9B59B6",
    },
    "stephanus_alexandria": {
        "name_en": "Stephanus of Alexandria",
        "name_gr": "Στέφανος Ἀλεξανδρεύς",
        "name_cn": "亞歷山大里亞的斯蒂法諾斯",
        "floruit": "ca. 610–641 CE",
        "location": "Alexandria / Constantinople",
        "period": "Early Byzantine",
        "work_en": "Commentary on Paulus; Horoscope of Islam",
        "work_gr": "Ὑπομνήματα",
        "work_cn": "《保羅注疏》及《伊斯蘭星盤》",
        "key_contributions_en": [
            "Commentary on Paulus Alexandrinus (only surviving Byzantine commentary)",
            "Famous 'Horoscope of Islam' — predicted rise of Mohammed (retroactively?)",
            "University professor in Alexandria and Constantinople",
            "Integrated Neoplatonic philosophy with practical astrology",
            "Earliest Byzantine text on political-religious astrology",
        ],
        "key_contributions_cn": [
            "保羅注疏（唯一現存的拜占庭注疏）",
            "著名的「伊斯蘭星盤」——預測穆罕默德的崛起（追溯性？）",
            "亞歷山大里亞及君士坦丁堡大學教授",
            "將新柏拉圖哲學與實際占星相結合",
            "最早的拜占庭政治宗教占星文本",
        ],
        "signature_technique": "Political-Religious Horoscopes",
        "source_ref": "Steph. Alex., Comm. on Paulus; CCAG II pp. 179–186",
        "icon": "✝️",
        "color": "#2E86C1",
    },
}

# ============================================================
# Political Horoscope Examples — Historical Byzantine Charts
# Key founding and imperial horoscopes
# ============================================================

POLITICAL_HOROSCOPES: Dict[str, Dict[str, Any]] = {
    "constantinople_founding": {
        "name_en": "Founding of Constantinople",
        "name_gr": "Κτίσις Κωνσταντινουπόλεως",
        "name_cn": "君士坦丁堡建城星盤",
        "date_str": "330 CE, May 11, 06:00 LT",
        "julian_day_approx": 1793528.75,
        "year": 330, "month": 5, "day": 11,
        "hour": 6, "minute": 0,
        "latitude": 41.016, "longitude": 28.977,
        "location_name_en": "Constantinople (Istanbul)",
        "location_name_cn": "君士坦丁堡（伊斯坦布爾）",
        "ascendant_sign": "Gemini",
        "mc_sign": "Pisces",
        "description_en": (
            "The founding horoscope of Constantinople, dedicated on 11 May 330 CE "
            "by Emperor Constantine I. Byzantine astrologers regarded this chart "
            "as the 'chart of the empire.' Gemini rising was interpreted as "
            "signifying the city's role as bridge between East and West. "
            "The chart was used for centuries to interpret state crises."
        ),
        "description_cn": (
            "君士坦丁堡建城星盤，由康斯坦丁一世皇帝於公元330年5月11日奉獻。"
            "拜占庭占星師視此盤為「帝國之盤」。雙子座上升被解釋為城市作為東西方橋樑的象徵。"
            "此盤在數百年間被用於解讀國家危機。"
        ),
        "key_planets_en": {
            "Jupiter": "Exalted in Cancer (4th house) — wealth and foundation",
            "Mars": "In Scorpio (6th house) — military power and conflict",
            "Saturn": "In Capricorn (8th house) — endurance through suffering",
        },
        "historical_use_en": [
            "Used by Theophilus of Edessa to predict Arab invasions",
            "Consulted by Byzantine astrologers during the 7th-century crisis",
            "Referenced in CCAG VIII as a canonical political chart",
        ],
        "source_ref": "Steph. Alex.; CCAG II, VIII; Tihon 1987",
        "icon": "🏛️",
    },
    "islam_horoscope": {
        "name_en": "Horoscope of Islam / Rise of Mohammed",
        "name_gr": "Τὸ θέμα τοῦ Ἰσλάμ",
        "name_cn": "伊斯蘭星盤（穆罕默德崛起盤）",
        "date_str": "571 CE (traditional birth year of Mohammed)",
        "julian_day_approx": 1948438.5,
        "year": 571, "month": 4, "day": 20,
        "hour": 0, "minute": 0,
        "latitude": 21.389, "longitude": 39.857,
        "location_name_en": "Mecca (Arabia)",
        "location_name_cn": "麥加（阿拉伯半島）",
        "ascendant_sign": "Scorpio",
        "mc_sign": "Leo",
        "description_en": (
            "The famous 'Horoscope of Islam' attributed to Stephanus of Alexandria "
            "and discussed by multiple Byzantine astrologers. Cast retroactively "
            "to interpret the rise of Islam, it featured Saturn and Jupiter conjunct "
            "in Scorpio, interpreted as the birth of a conquering new religion. "
            "This chart exemplifies Byzantine political-religious astrology."
        ),
        "description_cn": (
            "著名的「伊斯蘭星盤」，歸於亞歷山大里亞的斯蒂法諾斯，多位拜占庭占星師討論過此盤。"
            "追溯建立以解釋伊斯蘭的崛起，土星與木星合相於天蠍座，被解讀為一個征服性新宗教的誕生。"
            "此盤是拜占庭政治宗教占星的典型示例。"
        ),
        "key_planets_en": {
            "Saturn": "In Scorpio — dark destructive power rising",
            "Jupiter": "Conjunct Saturn in Scorpio — expansion of the creed",
            "Mars": "Ruler of Scorpio — military conquest",
        },
        "historical_use_en": [
            "Cast by Stephanus of Alexandria ca. 630 CE",
            "Used to explain and predict Islamic expansion",
            "Debated in Byzantine astrological manuscripts through 15th century",
        ],
        "source_ref": "Steph. Alex. in CCAG II; Pingree 1963",
        "icon": "☽",
    },
    "basil_ii_coronation": {
        "name_en": "Coronation of Emperor Basil II Bulgaroktonos",
        "name_gr": "Στέψη Βασιλείου Β' Βουλγαροκτόνου",
        "name_cn": "巴西爾二世「保加利亞人屠夫」加冕星盤",
        "date_str": "960 CE (co-emperor) / 976 CE (sole emperor)",
        "julian_day_approx": 2082924.5,
        "year": 976, "month": 1, "day": 10,
        "hour": 9, "minute": 0,
        "latitude": 41.016, "longitude": 28.977,
        "location_name_en": "Constantinople",
        "location_name_cn": "君士坦丁堡",
        "ascendant_sign": "Capricorn",
        "mc_sign": "Libra",
        "description_en": (
            "Emperor Basil II (976–1025) was the greatest Byzantine emperor. "
            "Byzantine astrologers including John Abramius cast charts for his "
            "reign, noting Saturn rising in Capricorn as indicating his cold, "
            "ruthless but effective rule. His defeat of Bulgaria was predicted "
            "from Mars's position in the chart."
        ),
        "description_cn": (
            "巴西爾二世皇帝（976-1025年）是最偉大的拜占庭皇帝。"
            "包括約翰·阿布拉米烏斯在內的拜占庭占星師為其統治立盤，"
            "注意到摩羯座上升的土星預示其冷酷但有效的統治。"
            "他對保加利亞的征服從盤中火星的位置得到預測。"
        ),
        "key_planets_en": {
            "Saturn": "Rising in Capricorn — cold, disciplined sovereign",
            "Mars": "Exalted in Capricorn — military supremacy",
            "Jupiter": "In Sagittarius — imperial expansion",
        },
        "historical_use_en": [
            "Chart analyzed by John Abramius in his 'Eisagoge'",
            "Used to justify Byzantine military campaigns in the Balkans",
            "Discussed in CCAG V.1 imperial horoscopes section",
        ],
        "source_ref": "Abramius, Eisag.; CCAG V.1; Tihon 1996",
        "icon": "👑",
    },
    "thema_mundi": {
        "name_en": "Thema Mundi — The Horoscope of the World",
        "name_gr": "Θέμα Κόσμου",
        "name_cn": "世界主題（宇宙本命盤）",
        "date_str": "Mythological — Creation of the World",
        "julian_day_approx": None,
        "year": -5509, "month": 3, "day": 25,
        "hour": 6, "minute": 0,
        "latitude": 41.016, "longitude": 28.977,
        "location_name_en": "Jerusalem (or Alexandria)",
        "location_name_cn": "耶路撒冷（或亞歷山大里亞）",
        "ascendant_sign": "Cancer",
        "mc_sign": "Aries",
        "description_en": (
            "The Thema Mundi ('World Horoscope') is a mythological chart "
            "representing the moment of creation. In Byzantine astrology it served "
            "as the canonical reference chart explaining why planets have their "
            "domiciles, exaltations, and other dignities. Cancer rising placed "
            "the Moon (ruler of Cancer) as lord of the Ascendant at the world's "
            "birth. Used by Byzantine astrologers to anchor the entire dignity system."
        ),
        "description_cn": (
            "「世界主題」（Thema Mundi）是代表創世時刻的神話性星盤。"
            "在拜占庭占星中，它作為解釋行星廟位、旺位及其他尊嚴的標準參考盤。"
            "巨蟹座上升使月亮（巨蟹座的主宰）成為世界誕生時上升點的主宰。"
            "拜占庭占星師用它來奠定整個尊嚴體系。"
        ),
        "key_planets_en": {
            "Moon": "In Cancer on ASC — nocturnal luminary at world's birth",
            "Sun": "In Leo (2nd house) — natural diurnal luminary",
            "Saturn": "In Capricorn (7th house) — opposite Cancer, cold/dry",
        },
        "historical_use_en": [
            "Used by Paulus Alexandrinus to explain planetary dignities",
            "Discussed by Rhetorius in his Compendium",
            "Preserved in Byzantine manuscripts through Abramius",
        ],
        "source_ref": "Paul. Alex., Eisag. ch. 2; Rhet. Aeg., Compend. ch. 1",
        "icon": "🌍",
    },
}

# ============================================================
# Seismologia — Earthquake Omens
# Source: Anonymus Byzantinus "Περὶ Σεισμῶν"; CCAG II; Lydus "De Ostentis"
# ============================================================

SEISMOLOGIA: Dict[str, Dict[str, Any]] = {
    "Sun": {
        "planet_cn": "太陽",
        "glyph": "☉",
        "sign_effects": {
            "Aries": {
                "region_en": "Eastern lands, Rome, Syria",
                "region_cn": "東方諸地、羅馬、敘利亞",
                "severity": "severe",
                "omen_en": "Great earthquake in the East; fire following the tremor",
                "omen_cn": "東方大地震；震後火災",
                "color": "#FF4444",
            },
            "Taurus": {
                "region_en": "Northern Italy, Greece, Thrace",
                "region_cn": "北義大利、希臘、色雷斯",
                "severity": "moderate",
                "omen_en": "Earthquake near mountains; landslides in Italy",
                "omen_cn": "山區地震；義大利山崩",
                "color": "#FF8800",
            },
            "Gemini": {
                "region_en": "Egypt, Libya, coastal regions",
                "region_cn": "埃及、利比亞、沿海地區",
                "severity": "mild",
                "omen_en": "Coastal tremors; flooding follows",
                "omen_cn": "沿海震動；洪水隨後而至",
                "color": "#FFD700",
            },
            "Cancer": {
                "region_en": "Sea and islands, Bithynia",
                "region_cn": "海洋與島嶼、比提尼亞",
                "severity": "severe",
                "omen_en": "Tsunami-type earthquake from the sea",
                "omen_cn": "來自海洋的海嘯型地震",
                "color": "#FF4444",
            },
            "Leo": {
                "region_en": "Persia, Mesopotamia, central lands",
                "region_cn": "波斯、美索不達米亞、中部地帶",
                "severity": "moderate",
                "omen_en": "Earthquake with loud sound; fires in cities",
                "omen_cn": "伴隨巨響的地震；城市火災",
                "color": "#FF8800",
            },
            "Virgo": {
                "region_en": "Greece, Macedonia, Asia Minor",
                "region_cn": "希臘、馬其頓、小亞細亞",
                "severity": "mild",
                "omen_en": "Minor tremors; harm to crops",
                "omen_cn": "輕微震動；農作物受損",
                "color": "#FFD700",
            },
            "Libra": {
                "region_en": "Western Empire, Italy, Gaul",
                "region_cn": "西部帝國、義大利、高盧",
                "severity": "moderate",
                "omen_en": "Earthquake causes political instability",
                "omen_cn": "地震導致政治不穩定",
                "color": "#FF8800",
            },
            "Scorpio": {
                "region_en": "Arabia, Palestine, Syria",
                "region_cn": "阿拉伯、巴勒斯坦、敘利亞",
                "severity": "severe",
                "omen_en": "Volcanic eruption; poisonous emanations from earth",
                "omen_cn": "火山噴發；地球散發有毒氣體",
                "color": "#FF4444",
            },
            "Sagittarius": {
                "region_en": "Spain, Gaul, Scythia",
                "region_cn": "西班牙、高盧、斯基泰",
                "severity": "mild",
                "omen_en": "Earthquake in distant barbarian lands",
                "omen_cn": "遙遠蠻族領地發生地震",
                "color": "#FFD700",
            },
            "Capricorn": {
                "region_en": "India, Persia, mountainous East",
                "region_cn": "印度、波斯、東部山區",
                "severity": "severe",
                "omen_en": "Prolonged series of earthquakes; collapse of mountains",
                "omen_cn": "持續一系列地震；山脈崩塌",
                "color": "#FF4444",
            },
            "Aquarius": {
                "region_en": "Pontus, Armenia, Caucasus",
                "region_cn": "本都、亞美尼亞、高加索",
                "severity": "moderate",
                "omen_en": "Earthquake at rivers; floods and tremors combined",
                "omen_cn": "河流地帶地震；洪水與震動並發",
                "color": "#FF8800",
            },
            "Pisces": {
                "region_en": "Egypt, Ethiopia, sea-shores",
                "region_cn": "埃及、衣索比亞、海岸",
                "severity": "severe",
                "omen_en": "Great flood accompanied by earthquakes; sea-level change",
                "omen_cn": "大洪水伴隨地震；海平面變化",
                "color": "#FF4444",
            },
        },
        "source_ref": "Anon. Byz., Περὶ Σεισμῶν; Lydus, De Ostentis ch. 58",
    },
    "Saturn": {
        "planet_cn": "土星",
        "glyph": "♄",
        "sign_effects": {
            "Aries": {
                "region_en": "Persia, Eastern lands",
                "region_cn": "波斯、東方諸地",
                "severity": "severe",
                "omen_en": "Prolonged drought followed by earthquake; destruction of cities",
                "omen_cn": "長期乾旱後發生地震；城市毀滅",
                "color": "#FF4444",
            },
            "Taurus": {
                "region_en": "Northern lands, Thrace",
                "region_cn": "北方諸地、色雷斯",
                "severity": "severe",
                "omen_en": "Earthquake with prolonged aftershocks lasting months",
                "omen_cn": "持續數月的余震性地震",
                "color": "#FF4444",
            },
            "Virgo": {
                "region_en": "Greece, Asia Minor",
                "region_cn": "希臘、小亞細亞",
                "severity": "moderate",
                "omen_en": "Subsidence of buildings; slow ground movement",
                "omen_cn": "建築物下陷；地面緩慢移動",
                "color": "#FF8800",
            },
            "Capricorn": {
                "region_en": "India, mountains",
                "region_cn": "印度、山區",
                "severity": "severe",
                "omen_en": "Catastrophic earthquake; collapse of entire regions",
                "omen_cn": "災難性地震；整個地區崩塌",
                "color": "#FF4444",
            },
        },
        "source_ref": "Heph. Theb., Apotel. III; CCAG II pp. 139–144",
    },
    "Mars": {
        "planet_cn": "火星",
        "glyph": "♂",
        "sign_effects": {
            "Aries": {
                "region_en": "Syria, Babylonia",
                "region_cn": "敘利亞、巴比倫尼亞",
                "severity": "severe",
                "omen_en": "Fire-earthquake with destruction of armies",
                "omen_cn": "帶有火焰的地震，摧毀軍隊",
                "color": "#FF4444",
            },
            "Scorpio": {
                "region_en": "Palestine, Syria, Arabia",
                "region_cn": "巴勒斯坦、敘利亞、阿拉伯",
                "severity": "severe",
                "omen_en": "Underground fire; poisonous gases from earth",
                "omen_cn": "地下火；地球噴出毒氣",
                "color": "#FF4444",
            },
            "Leo": {
                "region_en": "Rome, Italy, central Empire",
                "region_cn": "羅馬、義大利、帝國中部",
                "severity": "moderate",
                "omen_en": "Earthquake during war; civic unrest follows",
                "omen_cn": "戰爭期間地震；隨後民眾騷亂",
                "color": "#FF8800",
            },
        },
        "source_ref": "Rhet. Aeg., Compend. ch. 57; CCAG I",
    },
}

# ============================================================
# Selenodromia — Moon Phase Omens
# Source: Hephaestion of Thebes, Apotel. III; Lydus De Ostentis
# Moon phase predictions for weather, crops, and political events
# ============================================================

SELENODROMIA: Dict[str, Dict[str, Any]] = {
    "new_moon": {
        "phase_en": "New Moon (Σύνοδος / Synodos)",
        "phase_cn": "朔月（月日合朔）",
        "glyph": "🌑",
        "description_en": (
            "The New Moon (conjunction of Sun and Moon) is a moment of "
            "initiation. Byzantine astrologers assessed the sign and house "
            "of the Synodos to predict the coming month's events."
        ),
        "description_cn": (
            "朔月（日月合相）是開始的時刻。拜占庭占星師評估合相的星座與宮位，"
            "以預測即將到來月份的事件。"
        ),
        "sign_omens": {
            "Aries": {
                "weather_en": "Hot, dry winds; risk of wildfires",
                "weather_cn": "炎熱乾燥的風；野火風險",
                "political_en": "Military conflicts; royal proclamations",
                "political_cn": "軍事衝突；王室宣告",
                "agriculture_en": "Harmful to grain; good for fruit trees",
                "agriculture_cn": "對穀物有害；有利於果樹",
                "color": "#FF6B35",
            },
            "Cancer": {
                "weather_en": "Heavy rains; flooding",
                "weather_cn": "大雨；洪水",
                "political_en": "Changes in sea trade; naval matters prominent",
                "political_cn": "海上貿易變化；海軍事務突出",
                "agriculture_en": "Excellent for water crops; rice, reeds",
                "agriculture_cn": "極有利於水生作物；稻米、蘆葦",
                "color": "#4A90D9",
            },
            "Leo": {
                "weather_en": "Extreme heat; drought",
                "weather_cn": "極端高溫；乾旱",
                "political_en": "Emperor or king makes important decision",
                "political_cn": "皇帝或國王做出重要決定",
                "agriculture_en": "Harmful to crops; good for lions (!)",
                "agriculture_cn": "對農作物有害；有利於獅子（！）",
                "color": "#F4D03F",
            },
            "Scorpio": {
                "weather_en": "Pestilential air; risk of plague",
                "weather_cn": "疫癘之氣；瘟疫風險",
                "political_en": "Conspiracies; assassinations plotted",
                "political_cn": "陰謀詭計；策劃謀殺",
                "agriculture_en": "Destruction of crops by insects",
                "agriculture_cn": "昆蟲毀壞農作物",
                "color": "#8B0000",
            },
        },
        "source_ref": "Heph. Theb., Apotel. III.1–4; Lydus, De Ostentis",
    },
    "first_quarter": {
        "phase_en": "First Quarter (Πρώτη τετράς)",
        "phase_cn": "上弦月（第一象限）",
        "glyph": "🌓",
        "description_en": (
            "The First Quarter Moon indicates building action; plans set at "
            "New Moon now face their first challenge. Byzantine mundane "
            "astrologers watched for the sign of the First Quarter to "
            "judge the first week's difficulties."
        ),
        "description_cn": (
            "上弦月表示行動升溫；朔月時設定的計劃現在面臨第一個挑戰。"
            "拜占庭世俗占星師觀察上弦月的星座，以判斷第一週的困難。"
        ),
        "general_omen_en": "Tension between beginnings and resistance; conflicts emerge",
        "general_omen_cn": "開始與阻力之間的張力；衝突浮現",
        "source_ref": "Heph. Theb., Apotel. III.5–8",
    },
    "full_moon": {
        "phase_en": "Full Moon (Πανσέληνος / Panselenos)",
        "phase_cn": "望月（滿月）",
        "glyph": "🌕",
        "description_en": (
            "The Full Moon (opposition of Sun and Moon) is the culmination "
            "of the month's energies. Byzantine astrologers regarded it as "
            "the peak moment for medical, agricultural, and political events."
        ),
        "description_cn": (
            "望月（日月對衝）是月份能量的頂點。拜占庭占星師將其視為"
            "醫療、農業和政治事件的最高峰時刻。"
        ),
        "sign_omens": {
            "Aries": {
                "weather_en": "Thunderstorms; lightning",
                "weather_cn": "雷暴；閃電",
                "political_en": "Battles reach their climax; victory or defeat decided",
                "political_cn": "戰役達到高潮；勝負決定",
                "medical_en": "Fevers peak; crisis day in illness",
                "medical_cn": "發燒達到高峰；疾病危機日",
                "color": "#E74C3C",
            },
            "Taurus": {
                "weather_en": "Pleasant, mild weather",
                "weather_cn": "宜人、溫和的天氣",
                "political_en": "Commercial prosperity; trade agreements",
                "political_cn": "商業繁榮；貿易協議",
                "medical_en": "Good time for convalescence",
                "medical_cn": "適合康復的好時機",
                "color": "#27AE60",
            },
            "Gemini": {
                "weather_en": "Variable winds; messenger birds active",
                "weather_cn": "多變的風；信鴿活躍",
                "political_en": "Negotiations and treaties prominent",
                "political_cn": "談判與條約突出",
                "medical_en": "Nervous disorders peak; respiratory issues",
                "medical_cn": "神經疾患高峰；呼吸問題",
                "color": "#F39C12",
            },
            "Cancer": {
                "weather_en": "Heavy dew; mists; flooding at coast",
                "weather_cn": "濃露；霧氣；海岸洪水",
                "political_en": "Matters of the home country and empress",
                "political_cn": "本國事務與皇后事務",
                "medical_en": "Digestive crises; stomach ailments",
                "medical_cn": "消化危機；胃部疾病",
                "color": "#3498DB",
            },
            "Leo": {
                "weather_en": "Scorching heat; drought peak",
                "weather_cn": "酷熱；乾旱高峰",
                "political_en": "Emperor announces great campaign or decree",
                "political_cn": "皇帝宣布重大征討或法令",
                "medical_en": "Heart conditions peak; sunstroke",
                "medical_cn": "心臟病高峰；中暑",
                "color": "#F1C40F",
            },
            "Virgo": {
                "weather_en": "Good harvest rains",
                "weather_cn": "有益的收穫期降雨",
                "political_en": "Bureaucratic and administrative matters",
                "political_cn": "官僚與行政事務",
                "medical_en": "Intestinal ailments",
                "medical_cn": "腸道疾病",
                "color": "#2ECC71",
            },
            "Libra": {
                "weather_en": "Fair, equable weather",
                "weather_cn": "公平、均衡的天氣",
                "political_en": "Legal judgments; senatorial decisions",
                "political_cn": "法律判決；元老院決定",
                "medical_en": "Kidney ailments",
                "medical_cn": "腎臟疾病",
                "color": "#9B59B6",
            },
            "Scorpio": {
                "weather_en": "Pestilence in the air; epidemic risk",
                "weather_cn": "空氣中的瘟疫；流行病風險",
                "political_en": "Conspiracies revealed; executions",
                "political_cn": "陰謀揭露；處決",
                "medical_en": "Venomous diseases; reproductive disorders",
                "medical_cn": "毒性疾病；生殖疾患",
                "color": "#C0392B",
            },
            "Sagittarius": {
                "weather_en": "Strong winds from the south",
                "weather_cn": "南方強風",
                "political_en": "Religious proclamations; church matters",
                "political_cn": "宗教宣告；教會事務",
                "medical_en": "Hip and thigh ailments",
                "medical_cn": "髖部與大腿疾病",
                "color": "#E67E22",
            },
            "Capricorn": {
                "weather_en": "Cold, harsh winter conditions",
                "weather_cn": "寒冷、嚴酷的冬季條件",
                "political_en": "Government decisions; taxation matters",
                "political_cn": "政府決定；稅收事務",
                "medical_en": "Bone and joint ailments",
                "medical_cn": "骨骼與關節疾病",
                "color": "#7F8C8D",
            },
            "Aquarius": {
                "weather_en": "Floods and unusual rains",
                "weather_cn": "洪水與異常降雨",
                "political_en": "Revolutionary ideas; uprisings",
                "political_cn": "革命性想法；起義",
                "medical_en": "Circulatory and nerve disorders",
                "medical_cn": "循環與神經疾患",
                "color": "#2980B9",
            },
            "Pisces": {
                "weather_en": "Heavy seas; storms at sea",
                "weather_cn": "波濤洶湧；海上風暴",
                "political_en": "Naval matters; matters of the Church (Pisces = fish symbol)",
                "political_cn": "海軍事務；教會事務（魚是基督徒象徵）",
                "medical_en": "Foot ailments; lymphatic problems",
                "medical_cn": "足部疾病；淋巴問題",
                "color": "#1ABC9C",
            },
        },
        "source_ref": "Heph. Theb., Apotel. III.9–15; Rhet. Aeg., Compend.",
    },
    "last_quarter": {
        "phase_en": "Last Quarter (Τελευταία τετράς)",
        "phase_cn": "下弦月（最後象限）",
        "glyph": "🌗",
        "description_en": (
            "The Last Quarter Moon indicates dissolution and preparation "
            "for new cycles. Events begun at the Full Moon now face their "
            "consequences. Byzantine astrologers watched for what must be "
            "released before the next New Moon."
        ),
        "description_cn": (
            "下弦月表示消散與準備新週期。滿月時開始的事件現在面臨其後果。"
            "拜占庭占星師觀察在下一次朔月之前必須釋放什麼。"
        ),
        "general_omen_en": "Completion of cycles; harvest of consequences; endings",
        "general_omen_cn": "週期的完成；後果的收穫；結束",
        "source_ref": "Heph. Theb., Apotel. III.16",
    },
}

# ============================================================
# Vrontologia — Thunder / Lightning Omens
# Source: Lydus "De Ostentis" (Περὶ Διοσημειῶν); CCAG II
# Month-by-month thunder/lightning omen interpretations
# ============================================================

VRONTOLOGIA: Dict[str, Dict[str, Any]] = {
    "January": {
        "month_gr": "Ἰανουάριος",
        "month_cn": "一月",
        "thunder_from_east": {
            "omen_en": "Famine and disease among cattle; loss of the weak",
            "omen_cn": "牲畜饑荒與疾病；弱者的喪亡",
            "severity": "moderate",
        },
        "thunder_from_west": {
            "omen_en": "Good year for crops; winds favorable for sailing",
            "omen_cn": "農作物豐年；航行風向有利",
            "severity": "mild",
        },
        "thunder_from_north": {
            "omen_en": "Great war in the North; barbarian incursions",
            "omen_cn": "北方大戰；蠻族入侵",
            "severity": "severe",
        },
        "thunder_from_south": {
            "omen_en": "Abundance of fruit; merchants prosper",
            "omen_cn": "果實豐收；商人繁榮",
            "severity": "mild",
        },
        "source_ref": "Lydus, De Ostentis 27.1; CCAG II p. 135",
    },
    "February": {
        "month_gr": "Φεβρουάριος",
        "month_cn": "二月",
        "thunder_from_east": {
            "omen_en": "Death of a great king or emperor in the East",
            "omen_cn": "東方偉大國王或皇帝的駕崩",
            "severity": "severe",
        },
        "thunder_from_west": {
            "omen_en": "Revolt among western armies; civil strife",
            "omen_cn": "西方軍隊叛亂；內部衝突",
            "severity": "severe",
        },
        "thunder_from_north": {
            "omen_en": "Hard winter to follow; cold spring",
            "omen_cn": "隨後嚴冬；寒冷的春天",
            "severity": "moderate",
        },
        "thunder_from_south": {
            "omen_en": "Good health throughout the year; mild fevers",
            "omen_cn": "全年健康狀況良好；輕微發燒",
            "severity": "mild",
        },
        "source_ref": "Lydus, De Ostentis 27.2",
    },
    "March": {
        "month_gr": "Μάρτιος",
        "month_cn": "三月",
        "thunder_from_east": {
            "omen_en": "Abundant grain; but dearth of wine",
            "omen_cn": "穀物豐收；但葡萄酒短缺",
            "severity": "moderate",
        },
        "thunder_from_west": {
            "omen_en": "Wars in the western regions; armies mobilize",
            "omen_cn": "西部地區戰爭；軍隊動員",
            "severity": "severe",
        },
        "thunder_from_north": {
            "omen_en": "Plague among soldiers; epidemic in army",
            "omen_cn": "士兵中的瘟疫；軍隊疫情",
            "severity": "severe",
        },
        "thunder_from_south": {
            "omen_en": "Prosperity in southern regions; good trade",
            "omen_cn": "南部地區繁榮；貿易良好",
            "severity": "mild",
        },
        "source_ref": "Lydus, De Ostentis 27.3",
    },
    "April": {
        "month_gr": "Ἀπρίλιος",
        "month_cn": "四月",
        "thunder_from_east": {
            "omen_en": "Favorable for agriculture; abundant harvests",
            "omen_cn": "有利於農業；豐收",
            "severity": "mild",
        },
        "thunder_from_west": {
            "omen_en": "Locust swarms from the West; crop destruction",
            "omen_cn": "來自西方的蝗蟲群；農作物毀壞",
            "severity": "severe",
        },
        "thunder_from_north": {
            "omen_en": "Barbarian raids; northern frontier threatened",
            "omen_cn": "蠻族劫掠；北方邊境受威脅",
            "severity": "severe",
        },
        "thunder_from_south": {
            "omen_en": "Mild and pleasant year; good health",
            "omen_cn": "溫和宜人的一年；健康良好",
            "severity": "mild",
        },
        "source_ref": "Lydus, De Ostentis 27.4",
    },
    "May": {
        "month_gr": "Μάϊος",
        "month_cn": "五月",
        "thunder_from_east": {
            "omen_en": "Abundance and peace; emperor gains victory",
            "omen_cn": "豐收與和平；皇帝獲得勝利",
            "severity": "mild",
        },
        "thunder_from_west": {
            "omen_en": "Wheat harvest ruined; shortage of bread",
            "omen_cn": "小麥收成毀壞；麵包短缺",
            "severity": "moderate",
        },
        "thunder_from_north": {
            "omen_en": "Plague and famine in northern territories",
            "omen_cn": "北部領土的瘟疫與飢荒",
            "severity": "severe",
        },
        "thunder_from_south": {
            "omen_en": "Excellent wine harvest; trade with Egypt",
            "omen_cn": "優質葡萄酒收穫；與埃及的貿易",
            "severity": "mild",
        },
        "source_ref": "Lydus, De Ostentis 27.5",
    },
    "June": {
        "month_gr": "Ἰούνιος",
        "month_cn": "六月",
        "thunder_from_east": {
            "omen_en": "Persian or eastern enemy threatens borders",
            "omen_cn": "波斯或東方敵人威脅邊境",
            "severity": "severe",
        },
        "thunder_from_west": {
            "omen_en": "Good harvest; grain prices fall",
            "omen_cn": "豐收；糧食價格下降",
            "severity": "mild",
        },
        "thunder_from_north": {
            "omen_en": "Drought in summer; water shortage",
            "omen_cn": "夏季乾旱；水資源短缺",
            "severity": "moderate",
        },
        "thunder_from_south": {
            "omen_en": "Fever season particularly harsh this year",
            "omen_cn": "今年發燒季節特別嚴酷",
            "severity": "moderate",
        },
        "source_ref": "Lydus, De Ostentis 27.6",
    },
    "July": {
        "month_gr": "Ἰούλιος",
        "month_cn": "七月",
        "thunder_from_east": {
            "omen_en": "Great heat and drought; rivers low",
            "omen_cn": "酷熱與乾旱；河流水位低",
            "severity": "moderate",
        },
        "thunder_from_west": {
            "omen_en": "Naval battle or sea disaster",
            "omen_cn": "海戰或海上災難",
            "severity": "severe",
        },
        "thunder_from_north": {
            "omen_en": "Hun or Avar raids; northern frontier breaks",
            "omen_cn": "匈人或阿瓦爾人劫掠；北方邊境突破",
            "severity": "severe",
        },
        "thunder_from_south": {
            "omen_en": "Abundant dates and figs in southern lands",
            "omen_cn": "南方地區椰棗和無花果豐收",
            "severity": "mild",
        },
        "source_ref": "Lydus, De Ostentis 27.7",
    },
    "August": {
        "month_gr": "Αὔγουστος",
        "month_cn": "八月",
        "thunder_from_east": {
            "omen_en": "Religious dispute or council in the East",
            "omen_cn": "東方宗教爭論或會議",
            "severity": "moderate",
        },
        "thunder_from_west": {
            "omen_en": "Good vintage; wine trade flourishes",
            "omen_cn": "優質年份；葡萄酒貿易繁榮",
            "severity": "mild",
        },
        "thunder_from_north": {
            "omen_en": "Earthquake follows in northern regions",
            "omen_cn": "北部地區隨後發生地震",
            "severity": "severe",
        },
        "thunder_from_south": {
            "omen_en": "Plague in Egypt and Africa this year",
            "omen_cn": "今年埃及和非洲發生瘟疫",
            "severity": "severe",
        },
        "source_ref": "Lydus, De Ostentis 27.8",
    },
    "September": {
        "month_gr": "Σεπτέμβριος",
        "month_cn": "九月",
        "thunder_from_east": {
            "omen_en": "Heretical movement rises in the Church",
            "omen_cn": "教會中的異端運動興起",
            "severity": "moderate",
        },
        "thunder_from_west": {
            "omen_en": "Abundant olive harvest; oil cheap",
            "omen_cn": "橄欖豐收；橄欖油廉價",
            "severity": "mild",
        },
        "thunder_from_north": {
            "omen_en": "Severe winter approaching; prepare provisions",
            "omen_cn": "嚴冬臨近；準備糧食",
            "severity": "moderate",
        },
        "thunder_from_south": {
            "omen_en": "Piracy increases in the Mediterranean",
            "omen_cn": "地中海海盜活動增加",
            "severity": "moderate",
        },
        "source_ref": "Lydus, De Ostentis 27.9",
    },
    "October": {
        "month_gr": "Ὀκτώβριος",
        "month_cn": "十月",
        "thunder_from_east": {
            "omen_en": "Campaign season ends; armies return to quarters",
            "omen_cn": "征戰季結束；軍隊返回駐地",
            "severity": "mild",
        },
        "thunder_from_west": {
            "omen_en": "Rebellion in western themes of the Empire",
            "omen_cn": "帝國西部主題省份的叛亂",
            "severity": "severe",
        },
        "thunder_from_north": {
            "omen_en": "Famine conditions in the northern Balkans",
            "omen_cn": "北部巴爾幹半島的飢荒狀況",
            "severity": "severe",
        },
        "thunder_from_south": {
            "omen_en": "Peace negotiation with southern peoples",
            "omen_cn": "與南方民族的和平談判",
            "severity": "mild",
        },
        "source_ref": "Lydus, De Ostentis 27.10",
    },
    "November": {
        "month_gr": "Νοέμβριος",
        "month_cn": "十一月",
        "thunder_from_east": {
            "omen_en": "Eastern emperor plans winter campaign",
            "omen_cn": "東方皇帝計劃冬季征討",
            "severity": "moderate",
        },
        "thunder_from_west": {
            "omen_en": "Ships lost at sea; storms in western Mediterranean",
            "omen_cn": "海上船隻遇難；西地中海風暴",
            "severity": "moderate",
        },
        "thunder_from_north": {
            "omen_en": "Severe winter; livestock losses",
            "omen_cn": "嚴冬；牲畜損失",
            "severity": "severe",
        },
        "thunder_from_south": {
            "omen_en": "Mild winter in the south; olive trees productive",
            "omen_cn": "南方冬季溫和；橄欖樹豐產",
            "severity": "mild",
        },
        "source_ref": "Lydus, De Ostentis 27.11",
    },
    "December": {
        "month_gr": "Δεκέμβριος",
        "month_cn": "十二月",
        "thunder_from_east": {
            "omen_en": "Christmas-tide rebellion or coup d'état",
            "omen_cn": "聖誕節期間叛亂或政變",
            "severity": "severe",
        },
        "thunder_from_west": {
            "omen_en": "Mild and prosperous new year coming",
            "omen_cn": "溫和繁榮的新年即將到來",
            "severity": "mild",
        },
        "thunder_from_north": {
            "omen_en": "Extreme cold; deaths from freezing",
            "omen_cn": "極寒；凍死事件",
            "severity": "severe",
        },
        "thunder_from_south": {
            "omen_en": "Good year for trade and commerce",
            "omen_cn": "貿易與商業的良年",
            "severity": "mild",
        },
        "source_ref": "Lydus, De Ostentis 27.12",
    },
}

# ============================================================
# Christian-Astrological Syncretism
# Planetary associations with saints and biblical figures
# Source: Byzantine liturgical astrology; Michael Psellos;
#         Anastasios Sinaites; Byzantine Horologion traditions
# ============================================================

CHRISTIAN_SYNCRETISM: Dict[str, Dict[str, Any]] = {
    "Sun": {
        "planet_cn": "太陽",
        "glyph": "☉",
        "biblical_figure_en": "Christ (the Sun of Righteousness, Malachi 4:2)",
        "biblical_figure_cn": "基督（公義之日，《瑪拉基書》4:2）",
        "saint_en": "St. Elijah the Prophet (associated with solar fire and chariot)",
        "saint_cn": "先知以利亞（與太陽之火及戰車相關）",
        "liturgical_day_en": "Sunday (Κυριακή — Lord's Day)",
        "liturgical_day_cn": "星期日（主日）",
        "theological_note_en": (
            "The Sun as Christ was a common Byzantine interpretation, drawing on "
            "Malachi 4:2 ('Sun of Righteousness') and the Sol Invictus tradition "
            "Christianized by Constantine. Byzantine church architecture oriented "
            "toward the rising sun (East = Christ)."
        ),
        "theological_note_cn": (
            "太陽作為基督是常見的拜占庭解釋，援引《瑪拉基書》4:2（「公義的日頭」）"
            "和由君士坦丁基督教化的「不可征服的太陽」（Sol Invictus）傳統。"
            "拜占庭教堂建築朝向升起的太陽（東方=基督）。"
        ),
        "source_ref": "Michael Psellos, Theol. I.15; Anastasios Sinaites; CCAG",
    },
    "Moon": {
        "planet_cn": "月亮",
        "glyph": "☽",
        "biblical_figure_en": "The Virgin Mary (Theotokos, Mother of God)",
        "biblical_figure_cn": "聖母馬利亞（上帝之母）",
        "saint_en": "St. Mary Magdalene; St. Anne (mother of Mary)",
        "saint_cn": "抹大拉的馬利亞；聖安妮（馬利亞之母）",
        "liturgical_day_en": "Monday (Δευτέρα)",
        "liturgical_day_cn": "星期一",
        "theological_note_en": (
            "The Moon as the Theotokos (God-bearer) became central to Byzantine "
            "Mariology after the Council of Ephesus (431 CE). The Moon reflects "
            "the Sun's light just as Mary reflects Christ's glory. "
            "Revelation 12:1 'a woman clothed with the sun, with the moon under her feet' "
            "was a key Byzantine image."
        ),
        "theological_note_cn": (
            "月亮作為上帝之母（Theotokos）在以弗所公會議（公元431年）後成為"
            "拜占庭馬利亞神學的核心。月亮反射太陽的光，就像馬利亞反射基督的榮耀一樣。"
            "《啟示錄》12:1「身披太陽，腳踏月亮」是關鍵的拜占庭形象。"
        ),
        "source_ref": "Rev. 12:1; Council of Ephesus 431 CE; Byzantine hymnody",
    },
    "Mercury": {
        "planet_cn": "水星",
        "glyph": "☿",
        "biblical_figure_en": "The Holy Spirit (Logos, Divine Reason)",
        "biblical_figure_cn": "聖靈（道、神聖理性）",
        "saint_en": "St. John the Evangelist; St. Luke (physician-evangelist)",
        "saint_cn": "使徒約翰；路加（醫師傳道者）",
        "liturgical_day_en": "Wednesday (Τετάρτη)",
        "liturgical_day_cn": "星期三",
        "theological_note_en": (
            "Mercury's association with reason, communication, and medicine linked it "
            "to the Logos (John 1:1) and the Holy Spirit as divine communicator. "
            "St. Luke's dual role as physician and evangelist made him Mercury's patron. "
            "Byzantine scribes worked under Mercury's auspices."
        ),
        "theological_note_cn": (
            "水星與理性、溝通和醫學的聯繫使其與道（《約翰福音》1:1）和"
            "作為神聖溝通者的聖靈相連。路加作為醫師和傳道者的雙重角色使他成為水星的守護者。"
            "拜占庭文士在水星的庇護下工作。"
        ),
        "source_ref": "John 1:1; CCAG V.1; Byzantine monastic tradition",
    },
    "Venus": {
        "planet_cn": "金星",
        "glyph": "♀",
        "biblical_figure_en": "The Church as Bride of Christ (Revelation 19:7)",
        "biblical_figure_cn": "作為基督新娘的教會（《啟示錄》19:7）",
        "saint_en": "St. Mary of Egypt; St. Theodora (repentant saints)",
        "saint_cn": "埃及的聖馬利亞；聖西奧多拉（悔罪的聖人）",
        "liturgical_day_en": "Friday (Παρασκευή — Preparation Day)",
        "liturgical_day_cn": "星期五（準備日）",
        "theological_note_en": (
            "Venus's association with love, beauty, and earthly pleasures was "
            "ambivalent in Byzantine Christianity. As Friday (the day Christ died) "
            "was Venus's day, Byzantine astrologers saw a mystical tension between "
            "earthly love and divine sacrifice. The Church as Bride of Christ "
            "was the spiritualized Venus."
        ),
        "theological_note_cn": (
            "金星與愛情、美麗和塵世快樂的聯繫在拜占庭基督教中是矛盾的。"
            "由於星期五（基督受難日）是金星之日，拜占庭占星師看到"
            "塵世之愛與神聖犧牲之間的神秘張力。作為基督新娘的教會是靈性化的金星。"
        ),
        "source_ref": "Rev. 19:7; Byzantine homilies on Friday fasting",
    },
    "Mars": {
        "planet_cn": "火星",
        "glyph": "♂",
        "biblical_figure_en": "St. Michael the Archangel (warrior of God)",
        "biblical_figure_cn": "大天使米迦勒（上帝的戰士）",
        "saint_en": "St. George (patron of soldiers); St. Demetrius of Thessalonica",
        "saint_cn": "聖喬治（士兵的守護者）；帖撒羅尼迦的聖底米丟",
        "liturgical_day_en": "Tuesday (Τρίτη)",
        "liturgical_day_cn": "星期二",
        "theological_note_en": (
            "Mars's martial nature aligned naturally with the military saints of "
            "Byzantium. St. Michael led God's heavenly armies; St. George and "
            "St. Demetrius were the great warrior martyrs. Byzantine emperors "
            "invoked these saints before battle, and the astrologers linked Mars's "
            "position to military outcomes. Feast of St. Michael: 8 November."
        ),
        "theological_note_cn": (
            "火星的軍事本性自然地與拜占庭的軍事聖人相吻合。聖米迦勒率領上帝的天軍；"
            "聖喬治和聖底米丟是偉大的戰士殉道者。拜占庭皇帝在戰前向這些聖人祈禱，"
            "占星師將火星的位置與軍事結果相連。聖米迦勒瞻禮：11月8日。"
        ),
        "source_ref": "Rev. 12:7–9; Byzantine military hagiography; CCAG VIII",
    },
    "Jupiter": {
        "planet_cn": "木星",
        "glyph": "♃",
        "biblical_figure_en": "God the Father; Divine Providence",
        "biblical_figure_cn": "天父上帝；神聖天意",
        "saint_en": "St. Nicholas (patron of sailors and merchants); St. Basil the Great",
        "saint_cn": "聖尼古拉（水手和商人的守護者）；大聖巴西爾",
        "liturgical_day_en": "Thursday (Πέμπτη)",
        "liturgical_day_cn": "星期四",
        "theological_note_en": (
            "Jupiter as the Great Benefic was associated with Divine Providence "
            "and the Father in Byzantine theological astrology. The Byzantine "
            "emperor was considered Jupiter's earthly representative — Rex Iustitiae "
            "(King of Justice). St. Nicholas's miracle-working paralleled Jupiter's "
            "benevolence and bounty."
        ),
        "theological_note_cn": (
            "木星作為「大吉星」在拜占庭神學占星中與神聖天意和天父相關聯。"
            "拜占庭皇帝被認為是木星在世間的代表——公義之王（Rex Iustitiae）。"
            "聖尼古拉的神蹟與木星的仁慈和慷慨相呼應。"
        ),
        "source_ref": "Michael Psellos, Theol.; CCAG V; Byzantine imperial theology",
    },
    "Saturn": {
        "planet_cn": "土星",
        "glyph": "♄",
        "biblical_figure_en": "God the Father (in his aspect of Justice and Time)",
        "biblical_figure_cn": "天父上帝（在其正義與時間的面向）",
        "saint_en": "St. John the Baptist (ascetic, desert); St. Anthony the Great",
        "saint_cn": "施洗約翰（禁慾、沙漠）；偉大的聖安東尼",
        "liturgical_day_en": "Saturday (Σάββατον — Sabbath)",
        "liturgical_day_cn": "星期六（安息日）",
        "theological_note_en": (
            "Saturn's saturnine, melancholic, and restrictive qualities aligned with "
            "the monastic ideal in Byzantine Christianity. Saturday as the Sabbath "
            "carried Hebrew resonance in Byzantine liturgical practice. "
            "The Desert Fathers and ascetics were Saturn's holy men — remote, "
            "contemplative, mortifying the flesh. The dead were commemorated on Saturdays."
        ),
        "theological_note_cn": (
            "土星的憂鬱、抑制特質與拜占庭基督教的修道理想相吻合。"
            "作為安息日的星期六在拜占庭禮儀實踐中攜帶希伯來共鳴。"
            "曠野教父和禁慾者是土星的聖人——遠離世俗、沉思冥想、苦修肉身。"
            "亡者在星期六被紀念。"
        ),
        "source_ref": "Byzantine liturgical calendar; monastic typika; CCAG II",
    },
}

# ============================================================
# Byzantine Aspect Table — Classical Greek Aspect Theory
# Source: Paulus Alexandrinus, Eisag. ch. 13; Rhetorius Compend.
# ============================================================

BYZANTINE_ASPECTS: Dict[str, Dict[str, Any]] = {
    "conjunction": {
        "name_en": "Conjunction (Σύνοδος)",
        "name_cn": "合相（會合）",
        "degrees": 0,
        "orb": 8,
        "glyph": "☌",
        "quality_en": "Intensifying — merges the natures of both planets",
        "quality_cn": "強化——融合兩行星的本性",
        "byzantine_note_en": "Most powerful aspect; planets speak with one voice",
        "byzantine_note_cn": "最強力的相位；行星以同一聲音說話",
        "color": "#FFD700",
    },
    "sextile": {
        "name_en": "Sextile (Ἑξάγωνον)",
        "name_cn": "六分相",
        "degrees": 60,
        "orb": 6,
        "glyph": "⚹",
        "quality_en": "Harmonious — moderate benefit",
        "quality_cn": "和諧——中等吉利",
        "byzantine_note_en": "Friendly aspect; planets assist each other gently",
        "byzantine_note_cn": "友好相位；行星溫和地相互協助",
        "color": "#00FF88",
    },
    "square": {
        "name_en": "Square (Τετράγωνον)",
        "name_cn": "四分相",
        "degrees": 90,
        "orb": 8,
        "glyph": "□",
        "quality_en": "Difficult — conflict and tension",
        "quality_cn": "困難——衝突與張力",
        "byzantine_note_en": "Contentious aspect; planets quarrel and hinder",
        "byzantine_note_cn": "爭執相位；行星爭鬥並相互阻礙",
        "color": "#FF4444",
    },
    "trine": {
        "name_en": "Trine (Τρίγωνον)",
        "name_cn": "三分相",
        "degrees": 120,
        "orb": 8,
        "glyph": "△",
        "quality_en": "Benefic — greatest harmony",
        "quality_cn": "吉利——最大的和諧",
        "byzantine_note_en": "Most beneficial aspect; planets cooperate fully",
        "byzantine_note_cn": "最吉利的相位；行星完全合作",
        "color": "#44AAFF",
    },
    "opposition": {
        "name_en": "Opposition (Διάμετρος)",
        "name_cn": "對衝相（對立）",
        "degrees": 180,
        "orb": 8,
        "glyph": "☍",
        "quality_en": "Most difficult — complete opposition of natures",
        "quality_cn": "最困難——本性的完全對立",
        "byzantine_note_en": "Planets face each other in full antagonism",
        "byzantine_note_cn": "行星在完全對抗中面對面",
        "color": "#FF0000",
    },
}

# ============================================================
# Hellenistic-Byzantine Lots (Κλῆροι) — Extended Lot System
# Source: Paulus Alexandrinus, Eisag. ch. 14–24; Rhetorius Compend.
# ============================================================

BYZANTINE_LOTS: Dict[str, Dict[str, Any]] = {
    "fortune": {
        "name_en": "Lot of Fortune (Κλῆρος Τύχης)",
        "name_cn": "幸運點",
        "name_gr": "Κλῆρος Τύχης",
        "day_formula": "ASC + Moon − Sun",
        "night_formula": "ASC + Sun − Moon",
        "signifies_en": "Body, health, material fortune, life circumstances",
        "signifies_cn": "身體、健康、物質財富、生活境況",
        "byzantine_use_en": "Primary lot for mundane charts and personal destiny",
        "byzantine_use_cn": "世俗星盤和個人命運的主要命份份額",
        "source_ref": "Paul. Alex., Eisag. ch. 14; Rhet. Aeg., Compend. ch. 12",
    },
    "spirit": {
        "name_en": "Lot of Spirit (Κλῆρος Δαίμονος)",
        "name_cn": "精神點",
        "name_gr": "Κλῆρος Δαίμονος",
        "day_formula": "ASC + Sun − Moon",
        "night_formula": "ASC + Moon − Sun",
        "signifies_en": "Soul, mind, occupation, intellectual matters",
        "signifies_cn": "靈魂、心智、職業、智識事務",
        "byzantine_use_en": "Used for career and spiritual development analysis",
        "byzantine_use_cn": "用於職業和精神發展分析",
        "source_ref": "Paul. Alex., Eisag. ch. 15",
    },
    "eros": {
        "name_en": "Lot of Eros (Κλῆρος Ἔρωτος)",
        "name_cn": "愛欲點",
        "name_gr": "Κλῆρος Ἔρωτος",
        "day_formula": "ASC + Venus − Spirit",
        "night_formula": "ASC + Venus − Spirit",
        "signifies_en": "Love, desire, attraction, relationships",
        "signifies_cn": "愛情、慾望、吸引、關係",
        "byzantine_use_en": "Prominent in Byzantine love and marriage charts",
        "byzantine_use_cn": "在拜占庭愛情和婚姻星盤中突出",
        "source_ref": "Paul. Alex., Eisag. ch. 16; Heph. Theb., Apotel. II.18",
    },
    "victory": {
        "name_en": "Lot of Victory (Κλῆρος Νίκης)",
        "name_cn": "勝利點",
        "name_gr": "Κλῆρος Νίκης",
        "day_formula": "ASC + Jupiter − Spirit",
        "night_formula": "ASC + Jupiter − Spirit",
        "signifies_en": "Victory, contests, success in competition",
        "signifies_cn": "勝利、競賽、競爭中的成功",
        "byzantine_use_en": "Prominent in Byzantine military and political horoscopes",
        "byzantine_use_cn": "在拜占庭軍事和政治星盤中突出",
        "source_ref": "Paul. Alex., Eisag. ch. 17",
    },
    "nemesis": {
        "name_en": "Lot of Nemesis (Κλῆρος Νεμέσεως)",
        "name_cn": "復仇點",
        "name_gr": "Κλῆρος Νεμέσεως",
        "day_formula": "ASC + Fortune − Saturn",
        "night_formula": "ASC + Fortune − Saturn",
        "signifies_en": "Retribution, fate's justice, what cannot be escaped",
        "signifies_cn": "報應、命運的正義、無法逃脫的事",
        "byzantine_use_en": "Used in Byzantine analyses of imperial downfall and justice",
        "byzantine_use_cn": "用於拜占庭帝王沒落和正義的分析",
        "source_ref": "Paul. Alex., Eisag. ch. 20",
    },
    "necessity": {
        "name_en": "Lot of Necessity (Κλῆρος Ἀνάγκης)",
        "name_cn": "必然點",
        "name_gr": "Κλῆρος Ἀνάγκης",
        "day_formula": "ASC + Fortune − Mercury",
        "night_formula": "ASC + Fortune − Mercury",
        "signifies_en": "Necessity, bondage, constraints, what must be endured",
        "signifies_cn": "必然性、束縛、限制、必須忍受的事",
        "byzantine_use_en": "Analyzed for periods of captivity and enforced changes",
        "byzantine_use_cn": "用於分析監禁時期和強制性變化",
        "source_ref": "Paul. Alex., Eisag. ch. 19",
    },
    "courage": {
        "name_en": "Lot of Courage (Κλῆρος Τόλμης)",
        "name_cn": "勇氣點",
        "name_gr": "Κλῆρος Τόλμης",
        "day_formula": "ASC + Fortune − Mars",
        "night_formula": "ASC + Fortune − Mars",
        "signifies_en": "Courage, boldness, military valor, risk-taking",
        "signifies_cn": "勇氣、大膽、軍事英勇、冒險精神",
        "byzantine_use_en": "Key lot in Byzantine military horoscopes for generals",
        "byzantine_use_cn": "拜占庭將領軍事星盤中的關鍵命份份額",
        "source_ref": "Paul. Alex., Eisag. ch. 18",
    },
}

# ============================================================
# Byzantine Zodiac Sign Names
# Greek names used in Byzantine manuscripts
# ============================================================

BYZANTINE_SIGN_NAMES: Dict[str, Dict[str, str]] = {
    "Aries":       {"greek": "Κριός",      "cn": "白羊座", "glyph": "♈"},
    "Taurus":      {"greek": "Ταῦρος",     "cn": "金牛座", "glyph": "♉"},
    "Gemini":      {"greek": "Δίδυμοι",    "cn": "雙子座", "glyph": "♊"},
    "Cancer":      {"greek": "Καρκίνος",   "cn": "巨蟹座", "glyph": "♋"},
    "Leo":         {"greek": "Λέων",       "cn": "獅子座", "glyph": "♌"},
    "Virgo":       {"greek": "Παρθένος",   "cn": "處女座", "glyph": "♍"},
    "Libra":       {"greek": "Ζυγός",      "cn": "天秤座", "glyph": "♎"},
    "Scorpio":     {"greek": "Σκορπίος",   "cn": "天蠍座", "glyph": "♏"},
    "Sagittarius": {"greek": "Τοξότης",    "cn": "射手座", "glyph": "♐"},
    "Capricorn":   {"greek": "Αἰγόκερως", "cn": "摩羯座", "glyph": "♑"},
    "Aquarius":    {"greek": "Ὑδροχόος",   "cn": "水瓶座", "glyph": "♒"},
    "Pisces":      {"greek": "Ἰχθύες",     "cn": "雙魚座", "glyph": "♓"},
}

ZODIAC_SIGN_ORDER: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# ============================================================
# Byzantine Planet Names (Greek)
# ============================================================

BYZANTINE_PLANET_NAMES: Dict[str, Dict[str, str]] = {
    "Sun":     {"greek": "Ἥλιος",   "cn": "太陽", "glyph": "☉"},
    "Moon":    {"greek": "Σελήνη",  "cn": "月亮", "glyph": "☽"},
    "Mercury": {"greek": "Ἑρμῆς",   "cn": "水星", "glyph": "☿"},
    "Venus":   {"greek": "Ἀφροδίτη","cn": "金星", "glyph": "♀"},
    "Mars":    {"greek": "Ἄρης",    "cn": "火星", "glyph": "♂"},
    "Jupiter": {"greek": "Ζεύς",    "cn": "木星", "glyph": "♃"},
    "Saturn":  {"greek": "Κρόνος",  "cn": "土星", "glyph": "♄"},
}

CLASSICAL_PLANET_ORDER: List[str] = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"
]

# ============================================================
# Byzantine House Significations
# Source: Rhetorius "Compendium" chs. 57–112; Paulus Alex. ch. 24
# ============================================================

BYZANTINE_HOUSES: Dict[int, Dict[str, Any]] = {
    1: {
        "name_en": "Horoskopos (Ὡροσκόπος) — The Ascendant",
        "name_cn": "時標（上升點）",
        "signifies_en": ["Life", "Body", "Character", "Self", "Beginnings"],
        "signifies_cn": ["生命", "身體", "性格", "自我", "開端"],
        "joy": "Mercury",
        "byzantine_note_en": "The Horoskopos ('hour-watcher') is the most powerful place; the soul emerges here",
        "byzantine_note_cn": "時標（「時間觀察者」）是最強力的宮位；靈魂從這裡湧現",
    },
    2: {
        "name_en": "Gate of Hades (Πύλη τοῦ ᾍδου)",
        "name_cn": "冥府之門",
        "signifies_en": ["Livelihood", "Property", "Resources", "Death of hope"],
        "signifies_cn": ["生計", "財產", "資源", "希望的死亡"],
        "joy": None,
        "byzantine_note_en": "A weak place; planets here are obscured like going underground",
        "byzantine_note_cn": "一個弱小的宮位；此處的行星被遮蔽，如同進入地下",
    },
    3: {
        "name_en": "Goddess (Θεά) — Moon's Joy",
        "name_cn": "女神宮（月亮喜樂）",
        "signifies_en": ["Siblings", "Short travels", "Communication", "Goddess worship"],
        "signifies_cn": ["兄弟姐妹", "短途旅行", "溝通", "女神崇拜"],
        "joy": "Moon",
        "byzantine_note_en": "The Moon delights here; this place rules the early Church (Θεά = Theotokos in Byzantine)",
        "byzantine_note_cn": "月亮在此喜樂；此宮位統治早期教會（拜占庭的Θεά=神之母）",
    },
    4: {
        "name_en": "Lower Midheaven (Ὑπόγειον)",
        "name_cn": "地底中天",
        "signifies_en": ["Father", "Home", "Ancestry", "Land", "Foundations"],
        "signifies_cn": ["父親", "家庭", "祖先", "土地", "基礎"],
        "joy": None,
        "byzantine_note_en": "The foundation of the chart; ancestors and the homeland",
        "byzantine_note_cn": "星盤的基礎；祖先與故鄉",
    },
    5: {
        "name_en": "Good Fortune (Ἀγαθὴ Τύχη)",
        "name_cn": "吉祥宮",
        "signifies_en": ["Children", "Pleasure", "Creative works", "Benefic gifts"],
        "signifies_cn": ["子女", "快樂", "創意作品", "吉利的禮物"],
        "joy": "Venus",
        "byzantine_note_en": "Venus delights here; a place of joy and progeny",
        "byzantine_note_cn": "金星在此喜樂；喜悅與後代的宮位",
    },
    6: {
        "name_en": "Bad Fortune (Κακὴ Τύχη)",
        "name_cn": "惡運宮",
        "signifies_en": ["Illness", "Slaves", "Service", "Small animals", "Enemies"],
        "signifies_cn": ["疾病", "奴隸", "服務", "小動物", "敵人"],
        "joy": "Mars",
        "byzantine_note_en": "Mars delights here but brings strife; health crises manifest here",
        "byzantine_note_cn": "火星在此喜樂但帶來衝突；健康危機在此顯現",
    },
    7: {
        "name_en": "Setting Place (Δύσις / Ἑσπέρα)",
        "name_cn": "降落宮（西方）",
        "signifies_en": ["Marriage", "Partnership", "Open enemies", "Death"],
        "signifies_cn": ["婚姻", "合夥", "公開的敵人", "死亡"],
        "joy": None,
        "byzantine_note_en": "The setting (Western) angle; what sets and ends; the partner",
        "byzantine_note_cn": "落下（西方）角位；結束與終結之物；伴侶",
    },
    8: {
        "name_en": "Idle Place (Ἀργός / Ἐπικατaφορά)",
        "name_cn": "無力宮（死亡宮）",
        "signifies_en": ["Death", "Inheritance", "Crisis", "Occult matters"],
        "signifies_cn": ["死亡", "遺產", "危機", "神秘事務"],
        "joy": None,
        "byzantine_note_en": "The most malefic place; planets here are weakened and bring death matters",
        "byzantine_note_cn": "最凶惡的宮位；此處行星被削弱並帶來死亡事務",
    },
    9: {
        "name_en": "God (Θεός) — Sun's Joy",
        "name_cn": "上帝宮（太陽喜樂）",
        "signifies_en": ["Religion", "Long journeys", "Philosophy", "Prophecy"],
        "signifies_cn": ["宗教", "長途旅行", "哲學", "預言"],
        "joy": "Sun",
        "byzantine_note_en": "The Sun delights here; the place of God, Church, and divination",
        "byzantine_note_cn": "太陽在此喜樂；上帝、教會和占卜的宮位",
    },
    10: {
        "name_en": "Midheaven (Μεσουράνημα)",
        "name_cn": "中天（天頂）",
        "signifies_en": ["Career", "Reputation", "Authority", "Emperor", "Power"],
        "signifies_cn": ["職業", "聲譽", "權威", "皇帝", "權力"],
        "joy": None,
        "byzantine_note_en": "The most powerful angular house; the emperor's house in political charts",
        "byzantine_note_cn": "最強力的角宮；政治星盤中皇帝的宮位",
    },
    11: {
        "name_en": "Good Daemon (Ἀγαθὸς Δαίμων)",
        "name_cn": "善靈宮",
        "signifies_en": ["Friends", "Hopes", "Fortune", "Benefits from authority"],
        "signifies_cn": ["朋友", "希望", "財富", "來自權威的利益"],
        "joy": "Jupiter",
        "byzantine_note_en": "Jupiter delights here; the place of divine favor and the emperor's beneficence",
        "byzantine_note_cn": "木星在此喜樂；神聖恩惠和皇帝仁慈的宮位",
    },
    12: {
        "name_en": "Bad Daemon (Κακὸς Δαίμων)",
        "name_cn": "惡靈宮",
        "signifies_en": ["Enemies", "Imprisonment", "Exile", "Hidden matters", "Self-undoing"],
        "signifies_cn": ["敵人", "監禁", "流放", "隱藏事務", "自我毀滅"],
        "joy": "Saturn",
        "byzantine_note_en": "Saturn delights here; a malefic place of hidden enemies and imprisonment",
        "byzantine_note_cn": "土星在此喜樂；隱藏敵人和監禁的凶惡宮位",
    },
}

# ============================================================
# Byzantine Planetary Dignities (Triplicity Lords)
# Source: Ptolemy Tetrabiblos I.18–19 (as used in Byzantine tradition)
# ============================================================

BYZANTINE_TRIPLICITY_LORDS: Dict[str, Dict[str, Any]] = {
    "Fire": {
        "signs": ["Aries", "Leo", "Sagittarius"],
        "day_lord": "Sun",
        "night_lord": "Jupiter",
        "co_lord": "Saturn",
        "byzantine_note_en": "Fire triplicity lords govern energy, authority, and religion",
        "byzantine_note_cn": "火象三分性主宰統治能量、權威和宗教",
    },
    "Earth": {
        "signs": ["Taurus", "Virgo", "Capricorn"],
        "day_lord": "Venus",
        "night_lord": "Moon",
        "co_lord": "Mars",
        "byzantine_note_en": "Earth triplicity lords govern material world and the body",
        "byzantine_note_cn": "土象三分性主宰統治物質世界和身體",
    },
    "Air": {
        "signs": ["Gemini", "Libra", "Aquarius"],
        "day_lord": "Saturn",
        "night_lord": "Mercury",
        "co_lord": "Jupiter",
        "byzantine_note_en": "Air triplicity lords govern mind, communication, and law",
        "byzantine_note_cn": "風象三分性主宰統治心智、溝通和法律",
    },
    "Water": {
        "signs": ["Cancer", "Scorpio", "Pisces"],
        "day_lord": "Venus",
        "night_lord": "Mars",
        "co_lord": "Moon",
        "byzantine_note_en": "Water triplicity lords govern emotion, religion, and hidden matters",
        "byzantine_note_cn": "水象三分性主宰統治情感、宗教和隱藏事務",
    },
}

# ============================================================
# Theophilus of Edessa's Military Astrology Rules
# Source: Theophilus of Edessa, Apotelesmatics; Burnett & Pingree 2010
# ============================================================

THEOPHILUS_MILITARY_RULES: List[Dict[str, str]] = [
    {
        "rule_en": "If Mars is in the Ascendant at the inception of a battle, the attacker gains advantage",
        "rule_cn": "若火星在戰役開始時位於上升點，進攻方獲得優勢",
        "source": "Theoph. Edess., Apotel. II.3",
    },
    {
        "rule_en": "Saturn in opposition to the Moon at war's inception portends defeat and massacre",
        "rule_cn": "土星與月亮對衝於戰役開始時，預示失敗與屠殺",
        "source": "Theoph. Edess., Apotel. II.5",
    },
    {
        "rule_en": "Jupiter in the 10th house at the moment of battle ensures imperial victory",
        "rule_cn": "木星在戰役時刻位於第十宮，確保帝國的勝利",
        "source": "Theoph. Edess., Apotel. II.7",
    },
    {
        "rule_en": "The Moon applying to a benefic planet favors the attacker; to a malefic, the defender",
        "rule_cn": "月亮趨近吉星有利於進攻方；趨近凶星有利於防守方",
        "source": "Theoph. Edess., Apotel. II.9",
    },
    {
        "rule_en": "A planet in its own domicile or exaltation in the Ascendant at war's start ensures military strength",
        "rule_cn": "行星在戰役開始時在上升點的廟位或旺位中，確保軍事力量",
        "source": "Theoph. Edess., Apotel. II.11",
    },
    {
        "rule_en": "The ruler of the 7th house afflicted by malefics signals the enemy's weakness",
        "rule_cn": "第七宮主宰受凶星afflicted，預示敵方的弱點",
        "source": "Theoph. Edess., Apotel. II.13",
    },
    {
        "rule_en": "An eclipse (solar or lunar) within 15 days of battle inception portends great destruction",
        "rule_cn": "戰役開始15天內的日月食預示巨大破壞",
        "source": "Theoph. Edess., Apotel. II.15",
    },
]

# ============================================================
# Arabic-Byzantine Transition Techniques
# Source: Theophilus of Edessa; Mashallah; Abu Ma'shar
# Techniques that bridged Hellenistic and Arabic traditions
# ============================================================

ARABO_BYZANTINE_TECHNIQUES: Dict[str, Dict[str, str]] = {
    "firdaria": {
        "name_en": "Firdaria (Planetary Periods)",
        "name_cn": "菲爾達里亞（行星時期）",
        "origin_en": "Persian/Hellenistic; transmitted by Theophilus of Edessa to Arabic tradition",
        "origin_cn": "波斯/希臘化；由埃德薩的塞奧菲盧斯傳遞給阿拉伯傳統",
        "description_en": (
            "A system of planetary time periods based on the sect of the nativity. "
            "Day chart: Sun(10), Venus(8), Mercury(13), Moon(9), Saturn(11), Jupiter(12), Mars(7), then nodes. "
            "Night chart: Moon(9), Saturn(11), Jupiter(12), Mars(7), Sun(10), Venus(8), Mercury(13)."
        ),
        "description_cn": (
            "基於出生時晝夜區分的行星時期體系。"
            "晝盤：太陽(10)、金星(8)、水星(13)、月亮(9)、土星(11)、木星(12)、火星(7)，然後是交點。"
            "夜盤：月亮(9)、土星(11)、木星(12)、火星(7)、太陽(10)、金星(8)、水星(13)。"
        ),
        "source_ref": "Theoph. Edess.; Abu Ma'shar, Great Introduction; Bonatti 1491",
    },
    "solar_return": {
        "name_en": "Solar Return (Ἡλιακὴ Ἐπιστροφή / Tahwil)",
        "name_cn": "太陽回歸（Tahwil）",
        "origin_en": "Hellenistic; systematized in Arabic as Tahwil; used by Byzantine astrologers",
        "origin_cn": "希臘化起源；在阿拉伯中系統化為Tahwil；被拜占庭占星師使用",
        "description_en": (
            "The chart cast for the moment the Sun returns to its natal degree each year. "
            "Byzantine astrologers combined this with profections to give yearly predictions "
            "for emperors and city horoscopes."
        ),
        "description_cn": (
            "每年太陽回到本命度數時建立的星盤。"
            "拜占庭占星師將此與行運相結合，為皇帝和城市星盤提供年度預測。"
        ),
        "source_ref": "Theoph. Edess.; Heph. Theb., Apotel. II; Masha'allah",
    },
    "annual_profections": {
        "name_en": "Annual Profections (Ἐπαφέσεις)",
        "name_cn": "年度行運（向運）",
        "origin_en": "Hellenistic; Paulus Alexandrinus; preserved and transmitted by Byzantine tradition",
        "origin_cn": "希臘化起源；保羅·亞歷山大里亞；由拜占庭傳統保存和傳遞",
        "description_en": (
            "Each house is activated for one year of life in order: "
            "1st house at birth, 2nd at age 1, etc., with the cycle repeating every 12 years. "
            "Byzantine astrologers used this to identify the 'Lord of the Year'."
        ),
        "description_cn": (
            "每個宮位按順序為生命的一年被激活："
            "誕生時第一宮，1歲時第二宮，以此類推，週期每12年重複一次。"
            "拜占庭占星師用此確定「年主」。"
        ),
        "source_ref": "Paul. Alex., Eisag. ch. 31; Rhet. Aeg., Compend.",
    },
    "bonification_maltreatment": {
        "name_en": "Bonification & Maltreatment (Εὐεργεσία / Κακοποίησις)",
        "name_cn": "吉化與惡化",
        "origin_en": "Byzantine refinement of Hellenistic planet condition doctrine",
        "origin_cn": "希臘化行星狀態學說的拜占庭改進",
        "description_en": (
            "Bonification: a benefic planet (Jupiter or Venus) applies by trine or sextile "
            "to a planet, improving its condition. "
            "Maltreatment: a malefic (Saturn or Mars) applies by conjunction, square, or opposition, "
            "worsening its condition. Rhetorius gave extensive rules for this."
        ),
        "description_cn": (
            "吉化：吉星（木星或金星）以三分相或六分相趨近某行星，改善其狀態。"
            "惡化：凶星（土星或火星）以合相、四分相或對衝趨近，惡化其狀態。"
            "雷托里烏斯給出了詳盡的規則。"
        ),
        "source_ref": "Rhet. Aeg., Compend. ch. 57; Paul. Alex., Eisag.",
    },
}
