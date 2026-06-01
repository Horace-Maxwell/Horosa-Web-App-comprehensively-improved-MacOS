"""
Constants for the Polynesian / Hawaiian Star Lore module.

Includes the Hawaiian star database, 32-house compass, star lines,
Makahiki seasons, and cultural introduction text.
"""

# ============================================================
# Hawaiian Star Database
# ============================================================

HAWAIIAN_STARS: dict[str, dict] = {
    "Arcturus": {
        "hawaiian_name": "Hōkūleʻa",
        "pronunciation": "HO-koo-LEH-ah",
        "meaning": "Star of Gladness / Joy",
        "meaning_cn": "喜悅之星",
        "star_line": "Ka Iwikuamoʻo",
        "star_line_cn": "脊椎星線",
        "key_use": "Zenith star for Hawaiʻi",
        "key_use_cn": "夏威夷天頂星",
        "mythology": (
            "Hōkūleʻa is the zenith star of Hawaiʻi, passing directly overhead at "
            "21.3° N latitude. Master navigator Nainoa Thompson used it as the "
            "primary guide to sail the traditional double-hulled canoe Hōkūleʻa "
            "from Hawaiʻi to Tahiti without instruments. Its rising in the northeast "
            "signals the approach of spring planting season."
        ),
        "mythology_cn": (
            "Hōkūleʻa 是夏威夷的天頂星，直接經過北緯21.3度的頭頂正上方。"
            "航海大師 Nainoa Thompson 以此星為主要導航，無儀器地駕駛傳統雙體獨木舟"
            "Hōkūleʻa 從夏威夷航行至大溪地。它在東北方升起，預示著春季播種季節的來臨。"
        ),
        "swe_name": "Arcturus",
        "magnitude": -0.05,
        "compass_house": "Hikina",
        "ra_approx": 213.9,
        "dec_approx": 19.18,
    },
    "Sirius": {
        "hawaiian_name": "Āʻā",
        "pronunciation": "AH-ah",
        "meaning": "Glowing / Burning Bright",
        "meaning_cn": "閃耀燃燒之星",
        "star_line": "Ke Ka o Makaliʻi",
        "star_line_cn": "馬卡利伊的弦",
        "key_use": "Brightest star; winter navigator",
        "key_use_cn": "最亮星；冬季導航",
        "mythology": (
            "Āʻā, the brightest star in the sky, was used by Polynesian navigators "
            "as a brilliant winter guide. It rises in the ESE and is part of the "
            "Ke Ka o Makaliʻi star line — the Canoe Bailer — which stretches across "
            "the winter sky from Orion through Sirius."
        ),
        "mythology_cn": (
            "Āʻā 是天空中最亮的星星，玻里尼西亞航海者以它作為冬季的燦爛嚮導。"
            "它從東南偏東方向升起，是馬卡利伊的弦（Ke Ka o Makaliʻi）星線的一部分，"
            "從獵戶座橫跨冬季天空延伸至天狼星。"
        ),
        "swe_name": "Sirius",
        "magnitude": -1.46,
        "compass_house": "Nā Leo Malanai",
        "ra_approx": 101.3,
        "dec_approx": -16.72,
    },
    "Pleiades": {
        "hawaiian_name": "Makaliʻi",
        "pronunciation": "mah-kah-LEE-ee",
        "meaning": "Little Eyes / Eyes of the Chief",
        "meaning_cn": "小眼睛／酋長之眼",
        "star_line": "Ke Ka o Makaliʻi",
        "star_line_cn": "馬卡利伊的弦",
        "key_use": "Marks Makahiki (New Year) season",
        "key_use_cn": "標誌馬卡希基新年季節",
        "mythology": (
            "Makaliʻi (the Pleiades) is the most sacred star cluster in Hawaiian "
            "tradition. When it rises at sunset on the eastern horizon, it marks the "
            "beginning of Makahiki — the Hawaiian New Year and harvest festival "
            "dedicated to the god Lono. Navigation uses its rising point in the ENE."
        ),
        "mythology_cn": (
            "Makaliʻi（昴星團）是夏威夷傳統中最神聖的星群。"
            "當它在日落時從東方地平線升起，標誌著馬卡希基的開始——"
            "夏威夷新年及獻給神靈羅諾的豐收節。"
            "航海導航使用其在東北偏東方向的升起點。"
        ),
        "swe_name": "Alcyone",
        "magnitude": 2.87,
        "compass_house": "Nālani Koʻolau",
        "ra_approx": 56.87,
        "dec_approx": 24.11,
    },
    "Polaris": {
        "hawaiian_name": "Hōkūpaʻa",
        "pronunciation": "HO-koo-PAH-ah",
        "meaning": "Fixed Star / Immovable Star",
        "meaning_cn": "不動之星",
        "star_line": "Ka Iwikuamoʻo",
        "star_line_cn": "脊椎星線",
        "key_use": "North celestial pole; true north reference",
        "key_use_cn": "北天極；正北參考",
        "mythology": (
            "Hōkūpaʻa, the North Star, is the anchor of the celestial canoe. "
            "It never moves, always marking true north. Hawaiian navigators used "
            "its altitude above the horizon to determine their latitude — crucial "
            "for knowing how far north or south they had traveled."
        ),
        "mythology_cn": (
            "Hōkūpaʻa，北極星，是天上獨木舟的錨。"
            "它永不移動，始終指向正北。"
            "夏威夷航海者利用它在地平線上的高度來確定緯度——"
            "這對於了解已向北或向南航行多遠至關重要。"
        ),
        "swe_name": "Polaris",
        "magnitude": 2.02,
        "compass_house": "Hema Ko Luna",
        "ra_approx": 37.95,
        "dec_approx": 89.26,
    },
    "Spica": {
        "hawaiian_name": "Hikianalia",
        "pronunciation": "hee-kee-ah-NAH-lee-ah",
        "meaning": "Southern Companion / Escort",
        "meaning_cn": "南方伴星",
        "star_line": "Ka Iwikuamoʻo",
        "star_line_cn": "脊椎星線",
        "key_use": "Southern pair to Hōkūleʻa; guides to Tahiti",
        "key_use_cn": "Hōkūleʻa 的南方伴星；指向大溪地",
        "mythology": (
            "Hikianalia (Spica) is the sailing companion of Hōkūleʻa, traveling "
            "together across the sky. When navigating southward to Tahiti, "
            "Hikianalia becomes the zenith star and confirms the canoe has reached "
            "the Southern Hemisphere. Its name refers to the escort that accompanies "
            "the great chief Hōkūleʻa on voyages."
        ),
        "mythology_cn": (
            "Hikianalia（角宿一）是 Hōkūleʻa 的航行伴侶，共同橫越天空。"
            "向南航行至大溪地時，Hikianalia 成為天頂星，"
            "確認獨木舟已到達南半球。"
            "其名字指陪伴偉大酋長 Hōkūleʻa 出航的護送者。"
        ),
        "swe_name": "Spica",
        "magnitude": 0.97,
        "compass_house": "Komohana",
        "ra_approx": 201.3,
        "dec_approx": -11.16,
    },
    "Canopus": {
        "hawaiian_name": "Ke Aliʻi o Kona i ka lewa",
        "pronunciation": "keh ah-LEE-ee oh KOH-nah ee kah LEH-wah",
        "meaning": "The Chief of the Southern Skies",
        "meaning_cn": "南天之王",
        "star_line": "Ke Ka o Makaliʻi",
        "star_line_cn": "馬卡利伊的弦",
        "key_use": "Southern sky chief; guides SW voyages",
        "key_use_cn": "南天之主；引導西南航行",
        "mythology": (
            "Ke Aliʻi o Kona i ka lewa, the brilliant Canopus, is the chief of "
            "the southern skies — the second brightest star visible from Hawaiʻi "
            "during winter. It rises in the SSE and was used as a southward guide "
            "when navigating toward the Marquesas Islands."
        ),
        "mythology_cn": (
            "Ke Aliʻi o Kona i ka lewa，燦爛的老人星，是南天之王——"
            "冬季從夏威夷可見的第二亮星。"
            "它從南偏南方向升起，在向馬克薩斯群島航行時用作向南的指引。"
        ),
        "swe_name": "Canopus",
        "magnitude": -0.72,
        "compass_house": "Noio Malanai",
        "ra_approx": 95.99,
        "dec_approx": -52.70,
    },
    "Scorpius": {
        "hawaiian_name": "Ka Makau Nui o Maui",
        "pronunciation": "kah mah-KAU noo-ee oh MAU-ee",
        "meaning": "The Great Fishhook of Maui",
        "meaning_cn": "茂伊的大魚鉤",
        "star_line": "Mānaiakalani",
        "star_line_cn": "馬烏伊的魚鉤",
        "key_use": "Summer navigation; southern sky anchor",
        "key_use_cn": "夏季導航；南天錨點",
        "mythology": (
            "Ka Makau Nui o Maui — the Great Fishhook of Maui — is the constellation "
            "Scorpius, which the demigod Maui used to fish up the Hawaiian Islands "
            "from the bottom of the ocean. It rises in the SSE during summer and "
            "curves like a great hook across the southern sky."
        ),
        "mythology_cn": (
            "Ka Makau Nui o Maui——茂伊的大魚鉤——是天蠍座，"
            "半神茂伊用它從海底釣起了夏威夷群島。"
            "它在夏季從南偏南方向升起，"
            "像一個巨大的魚鉤橫跨南方天空。"
        ),
        "swe_name": "Antares",
        "magnitude": 1.06,
        "compass_house": "ʻĀina Malanai",
        "ra_approx": 247.35,
        "dec_approx": -26.43,
    },
    "Southern Cross": {
        "hawaiian_name": "Hānaiakamalama",
        "pronunciation": "hah-nah-ee-ah-kah-mah-LAH-mah",
        "meaning": "Foster Child of the Moon",
        "meaning_cn": "月亮的養子",
        "star_line": "Ka Iwikuamoʻo",
        "star_line_cn": "脊椎星線",
        "key_use": "Southern celestial pole indicator",
        "key_use_cn": "南天極指示星",
        "mythology": (
            "Hānaiakamalama, the Southern Cross, is the foster child of the moon. "
            "Its long axis points toward the south celestial pole, making it "
            "essential for navigation in the Southern Hemisphere. Hawaiian navigators "
            "used it to confirm they had crossed the equator heading south."
        ),
        "mythology_cn": (
            "Hānaiakamalama，南十字座，是月亮的養子。"
            "其長軸指向南天極，使其在南半球航行中不可或缺。"
            "夏威夷航海者用它來確認自己已向南越過赤道。"
        ),
        "swe_name": "Acrux",
        "magnitude": 0.77,
        "compass_house": "Hema Ko Lalo",
        "ra_approx": 186.65,
        "dec_approx": -63.10,
    },
    "Rigel": {
        "hawaiian_name": "Puanakau",
        "pronunciation": "poo-ah-NAH-kau",
        "meaning": "Flower of the Heavens",
        "meaning_cn": "天堂之花",
        "star_line": "Ke Ka o Makaliʻi",
        "star_line_cn": "馬卡利伊的弦",
        "key_use": "Winter rising star; eastern guide",
        "key_use_cn": "冬季升起之星；東方嚮導",
        "mythology": (
            "Puanakau (Rigel), the bright foot of Orion, was known as the Flower "
            "of the Heavens. It rises nearly due east and was used to set the "
            "course toward the east. Part of the great winter star line that "
            "stretches from the Pleiades through Orion."
        ),
        "mythology_cn": (
            "Puanakau（參宿七），獵戶座的明亮腳部，被稱為天堂之花。"
            "它幾乎從正東方升起，用於確定向東的航線。"
            "是從昴星團穿越獵戶座的偉大冬季星線的一部分。"
        ),
        "swe_name": "Rigel",
        "magnitude": 0.13,
        "compass_house": "Hikina",
        "ra_approx": 78.63,
        "dec_approx": -8.20,
    },
    "Betelgeuse": {
        "hawaiian_name": "Kauluakoko",
        "pronunciation": "kau-loo-ah-KOH-koh",
        "meaning": "The Cluster of Blood / Red Shoulder Star",
        "meaning_cn": "血紅星團／紅肩星",
        "star_line": "Ke Ka o Makaliʻi",
        "star_line_cn": "馬卡利伊的弦",
        "key_use": "Red winter star; storm warning",
        "key_use_cn": "紅色冬季星；風暴警示",
        "mythology": (
            "Kauluakoko (Betelgeuse), the red giant shoulder of Orion, was associated "
            "with blood-red warnings. When it appears unusually bright or reddish, "
            "sailors interpreted this as a sign of approaching storms or rough seas. "
            "It marked the shoulder of the great winter giant."
        ),
        "mythology_cn": (
            "Kauluakoko（參宿四），獵戶座的紅色巨星肩部，與血紅色警告相關聯。"
            "當它顯得異常明亮或紅色時，水手將此解讀為風暴或惡海即將來臨的徵兆。"
            "它標誌著偉大冬季巨人的肩膀。"
        ),
        "swe_name": "Betelgeuse",
        "magnitude": 0.42,
        "compass_house": "Nālani Koʻolau",
        "ra_approx": 88.79,
        "dec_approx": 7.41,
    },
    "Aldebaran": {
        "hawaiian_name": "Hōkūnui",
        "pronunciation": "HO-koo-NOO-ee",
        "meaning": "Great Star / The Big Star",
        "meaning_cn": "大星",
        "star_line": "Ke Ka o Makaliʻi",
        "star_line_cn": "馬卡利伊的弦",
        "key_use": "Red eye of Taurus; winter compass point",
        "key_use_cn": "金牛座的紅眼；冬季羅盤點",
        "mythology": (
            "Hōkūnui (Aldebaran), the Great Star, is the fiery red eye of the Bull "
            "in Taurus. Hawaiian navigators used it to gauge the Pleiades' direction "
            "and as a companion waypoint in the winter sky. Its reddish glow was "
            "noticed by fishermen as a guide for nighttime ocean crossings."
        ),
        "mythology_cn": (
            "Hōkūnui（畢宿五），大星，是金牛座熾熱的紅眼。"
            "夏威夷航海者用它來衡量昴星團的方向，"
            "並作為冬季天空的伴隨途徑點。"
            "它的紅色光芒被漁民注意到，作為夜間海洋穿越的指引。"
        ),
        "swe_name": "Aldebaran",
        "magnitude": 0.85,
        "compass_house": "Nālani Koʻolau",
        "ra_approx": 68.98,
        "dec_approx": 16.51,
    },
    "Antares": {
        "hawaiian_name": "Lehua",
        "pronunciation": "leh-HOO-ah",
        "meaning": "Red Star of Scorpius / Lehua Blossom",
        "meaning_cn": "天蠍座紅星／勒瓦花",
        "star_line": "Mānaiakalani",
        "star_line_cn": "馬烏伊的魚鉤",
        "key_use": "Red summer star; heart of the fishhook",
        "key_use_cn": "紅色夏季星；魚鉤之心",
        "mythology": (
            "Lehua (Antares), the red heart of Scorpius, shares the same name as "
            "the sacred red lehua blossom of the ʻōhiʻa tree. In Hawaiian tradition, "
            "the lehua flower holds the spirit of lovers — picking one brings rain "
            "as the separated lovers cry. This red star was the anchor of Maui's "
            "great fishhook constellation."
        ),
        "mythology_cn": (
            "Lehua（心宿二），天蠍座的紅心，與ʻōhiʻa 樹神聖的紅色勒瓦花同名。"
            "在夏威夷傳統中，勒瓦花承載著戀人的靈魂——"
            "摘下一朵會帶來雨水，因為分離的戀人在哭泣。"
            "這顆紅星是茂伊大魚鉤星座的錨點。"
        ),
        "swe_name": "Antares",
        "magnitude": 1.06,
        "compass_house": "ʻĀina Malanai",
        "ra_approx": 247.35,
        "dec_approx": -26.43,
    },
    "Vega": {
        "hawaiian_name": "Keoeoe",
        "pronunciation": "keh-oh-EH-oh-eh",
        "meaning": "The Whistler / Wind Star",
        "meaning_cn": "吹哨者／風之星",
        "star_line": "Ka Iwikuamoʻo",
        "star_line_cn": "脊椎星線",
        "key_use": "Summer zenith region; wind direction indicator",
        "key_use_cn": "夏季天頂區域；風向指示",
        "mythology": (
            "Keoeoe (Vega), the Whistler, is a bright summer star associated with "
            "the winds of the Hawaiian summer season. It passes nearly overhead "
            "at Hawaiian latitudes during summer nights, and its brightness was "
            "used to gauge atmospheric clarity — relevant for predicting weather "
            "and sailing conditions."
        ),
        "mythology_cn": (
            "Keoeoe（織女星），吹哨者，是與夏威夷夏季風相關的明亮夏季星星。"
            "夏季夜晚幾乎從夏威夷緯度的頭頂直過，"
            "其亮度用於衡量大氣清晰度——這與預測天氣和航行條件有關。"
        ),
        "swe_name": "Vega",
        "magnitude": 0.03,
        "compass_house": "Manu Koʻolau",
        "ra_approx": 279.23,
        "dec_approx": 38.78,
    },
    "Altair": {
        "hawaiian_name": "Humu",
        "pronunciation": "HOO-moo",
        "meaning": "Triggerfish / Sewing Star",
        "meaning_cn": "砲彈魚星",
        "star_line": "Ka Iwikuamoʻo",
        "star_line_cn": "脊椎星線",
        "key_use": "Summer triangle; equatorial guide",
        "key_use_cn": "夏季三角形；赤道嚮導",
        "mythology": (
            "Humu (Altair) is named for the triggerfish — the humuhumunukunukuāpuaʻa — "
            "Hawaiʻi's state fish. It rises nearly due east, making it an excellent "
            "equatorial guide star. Part of the Summer Triangle, it helped navigators "
            "confirm they were sailing along the equatorial latitudes."
        ),
        "mythology_cn": (
            "Humu（牛郎星）以礁砲彈魚命名——humuhumunukunukuāpuaʻa——夏威夷的州魚。"
            "它幾乎從正東方升起，使其成為一顆出色的赤道嚮導星。"
            "作為夏季三角形的一部分，它幫助航海者確認他們沿赤道緯度航行。"
        ),
        "swe_name": "Altair",
        "magnitude": 0.76,
        "compass_house": "Hikina",
        "ra_approx": 297.70,
        "dec_approx": 8.87,
    },
    "Fomalhaut": {
        "hawaiian_name": "Ā",
        "pronunciation": "AH",
        "meaning": "The Traditional One / Solitary Star",
        "meaning_cn": "傳統之星／孤獨之星",
        "star_line": "Mānaiakalani",
        "star_line_cn": "馬烏伊的魚鉤",
        "key_use": "Autumn southern guide star",
        "key_use_cn": "秋季南方嚮導星",
        "mythology": (
            "Ā (Fomalhaut), the solitary bright star of the southern autumn sky, "
            "was the traditional autumn south-pointing guide. Known as the loneliest "
            "bright star — it has no bright neighbors — it was used by navigators "
            "as a landmark in the southern sky during the season of Hoʻoilo "
            "(the rainy season beginning)."
        ),
        "mythology_cn": (
            "Ā（北落師門），南方秋季天空中孤獨的明亮星星，"
            "是傳統的秋季南方指向嚮導。"
            "被稱為最孤獨的明亮星——它沒有明亮的鄰星——"
            "航海者在 Hoʻoilo（雨季開始）季節用它作為南方天空的地標。"
        ),
        "swe_name": "Fomalhaut",
        "magnitude": 1.16,
        "compass_house": "Noio Malanai",
        "ra_approx": 344.41,
        "dec_approx": -29.62,
    },
    "Alpha Centauri": {
        "hawaiian_name": "Nānā-moa",
        "pronunciation": "NAH-nah MOH-ah",
        "meaning": "Look for the Chicken / Pointer to the Cross",
        "meaning_cn": "尋找雞星／南十字座指標",
        "star_line": "Ka Iwikuamoʻo",
        "star_line_cn": "脊椎星線",
        "key_use": "Points to Southern Cross; deep south guide",
        "key_use_cn": "指向南十字座；深南指引",
        "mythology": (
            "Nānā-moa (Alpha Centauri) literally means 'look for the chicken' — "
            "a reference to following this star's direction toward the Southern Cross. "
            "As one of the closest stars to our solar system, its movement across "
            "the southern sky guided navigators deep into the Southern Hemisphere "
            "on voyages toward New Zealand and beyond."
        ),
        "mythology_cn": (
            "Nānā-moa（南門二）字面意思是「尋找雞」——"
            "指沿著這顆星的方向走向南十字座。"
            "作為距離我們太陽系最近的星星之一，"
            "它在南方天空的運動引導航海者深入南半球，"
            "踏上通往新西蘭及更遠地方的航程。"
        ),
        "swe_name": "Rigil Kentaurus",
        "magnitude": -0.27,
        "compass_house": "Hema Ko Lalo",
        "ra_approx": 219.90,
        "dec_approx": -60.84,
    },
    "Achernar": {
        "hawaiian_name": "Kaelo",
        "pronunciation": "kah-EH-loh",
        "meaning": "The Water Carrier / River's End",
        "meaning_cn": "水的攜帶者／河流盡頭",
        "star_line": "Ka Iwikuamoʻo",
        "star_line_cn": "脊椎星線",
        "key_use": "End of the celestial river; south polar guide",
        "key_use_cn": "天河盡頭；南極嚮導",
        "mythology": (
            "Kaelo (Achernar) sits at the end of the celestial river Eridanus. "
            "For Hawaiian navigators, the 'water carrier' star indicated the southern "
            "horizon limit for voyages. Only visible from Hawaiʻi when it just grazes "
            "the southern horizon, it confirmed when a canoe had ventured far to the "
            "south, approaching the tropics of Capricorn."
        ),
        "mythology_cn": (
            "Kaelo（水委一）位於天上波江座的盡頭。"
            "對於夏威夷航海者來說，這顆「水的攜帶者」星標誌著航行的南方地平線極限。"
            "只有在夏威夷才能看到它剛好掠過南方地平線時，"
            "確認獨木舟已遠征至南方，接近摩羯座回歸線。"
        ),
        "swe_name": "Achernar",
        "magnitude": 0.46,
        "compass_house": "Hema Ko Lalo",
        "ra_approx": 24.43,
        "dec_approx": -57.24,
    },
    "Capella": {
        "hawaiian_name": "Hōkūlei",
        "pronunciation": "HO-koo-LAY",
        "meaning": "Star Garland / Wreath Star",
        "meaning_cn": "星花環",
        "star_line": "Ke Ka o Makaliʻi",
        "star_line_cn": "馬卡利伊的弦",
        "key_use": "Winter northern guide; overhead path",
        "key_use_cn": "冬季北方嚮導；頭頂路徑",
        "mythology": (
            "Hōkūlei (Capella) is the Star Garland — a bright yellowish star that "
            "passes nearly overhead at Hawaiian latitudes in winter. Like a lei "
            "adorning the head of the sky, it was used in winter navigation to "
            "confirm northward progress. Part of the Canoe Bailer star line."
        ),
        "mythology_cn": (
            "Hōkūlei（五車二）是星花環——一顆在冬季幾乎從夏威夷緯度頭頂直過的明亮黃色星星。"
            "像裝飾天空頭部的花環，冬季航行時用它來確認向北的進度。"
            "是馬卡利伊的弦星線的一部分。"
        ),
        "swe_name": "Capella",
        "magnitude": 0.08,
        "compass_house": "Manu Koʻolau",
        "ra_approx": 79.17,
        "dec_approx": 45.99,
    },
    "Deneb": {
        "hawaiian_name": "Kehoʻomoana",
        "pronunciation": "keh-hoh-oh-MOH-ah-nah",
        "meaning": "The Ocean Crosser",
        "meaning_cn": "橫越大洋者",
        "star_line": "Ka Iwikuamoʻo",
        "star_line_cn": "脊椎星線",
        "key_use": "Summer northern sky; long voyage marker",
        "key_use_cn": "夏季北方天空；長途航行標誌",
        "mythology": (
            "Kehoʻomoana (Deneb), the Ocean Crosser, marks the tail of the Celestial "
            "Swan and the top of the Summer Triangle. Its position high in the "
            "northern summer sky was used to gauge how far north a canoe had "
            "traveled during summer voyages to the north Pacific."
        ),
        "mythology_cn": (
            "Kehoʻomoana（天津四），橫越大洋者，標誌著天鵝座的尾部和夏季三角形的頂部。"
            "其在北方夏季天空中的高位置用於衡量獨木舟在夏季北太平洋航行中向北走了多遠。"
        ),
        "swe_name": "Deneb",
        "magnitude": 1.25,
        "compass_house": "Manu Hoʻolua",
        "ra_approx": 310.36,
        "dec_approx": 45.28,
    },
}

# ============================================================
# 32-House Star Compass (Nainoa Thompson system)
# ============================================================
# 32 houses at 11.25° spacing starting from North (0°)
# Listed clockwise from North

_HOUSE_NAMES_CW = [
    # N — index 0
    ("Hema Ko Luna",      "North Star / True North",   "正北；北天極"),
    # NNE
    ("ʻĀina Koʻolau",    "Land of the Northeast",     "東北偏北之地"),
    # NNE (2)
    ("Noio Koʻolau",     "Tern of the Northeast",     "東北偏北燕鷗"),
    # NE
    ("Manu Koʻolau",     "Bird of the Northeast",     "東北之鳥"),
    # ENE
    ("Nālani Koʻolau",   "Heavens of the Northeast",  "東北天空"),
    # ENE (2)
    ("Nā Leo Koʻolau",   "Voices of the Northeast",   "東北之聲"),
    # E — index 6
    ("Hikina",           "East / Rising Sun",         "正東；日出"),
    # ESE
    ("Nā Leo Malanai",   "Voices of the Southeast",   "東南之聲"),
    # ESE (2)
    ("Nālani Malanai",   "Heavens of the Southeast",  "東南天空"),
    # SE
    ("Manu Malanai",     "Bird of the Southeast",     "東南之鳥"),
    # SSE
    ("Noio Malanai",     "Tern of the Southeast",     "東南偏南燕鷗"),
    # SSE (2)
    ("ʻĀina Malanai",    "Land of the Southeast",     "東南偏南之地"),
    # S — index 12
    ("Hema Ko Lalo",     "South / Below South Star",  "正南；南天極方向"),
    # SSW
    ("ʻĀina Kona",       "Land of the Southwest",     "西南偏南之地"),
    # SSW (2)
    ("Noio Kona",        "Tern of the Southwest",     "西南偏南燕鷗"),
    # SW
    ("Manu Kona",        "Bird of the Southwest",     "西南之鳥"),
    # WSW
    ("Nālani Kona",      "Heavens of the Southwest",  "西南天空"),
    # WSW (2)
    ("Nā Leo Kona",      "Voices of the Southwest",   "西南之聲"),
    # W — index 18
    ("Komohana",         "West / Setting Sun",        "正西；日落"),
    # WNW
    ("Nā Leo Hoʻolua",   "Voices of the Northwest",   "西北之聲"),
    # WNW (2)
    ("Nālani Hoʻolua",   "Heavens of the Northwest",  "西北天空"),
    # NW
    ("Manu Hoʻolua",     "Bird of the Northwest",     "西北之鳥"),
    # NNW
    ("Noio Hoʻolua",     "Tern of the Northwest",     "西北偏北燕鷗"),
    # NNW (2)
    ("ʻĀina Hoʻolua",    "Land of the Northwest",     "西北偏北之地"),
    # Back toward N — index 24 would be second half
    # The full 32 houses repeat the pattern with finer subdivisions
    # Houses 24-31 fill NNE to N with extra detail
    ("ʻĀina Koʻolau Luna", "Upper Land of the Northeast", "東北上方之地"),
    ("Noio Koʻolau Luna",  "Upper Tern of the Northeast", "東北上方燕鷗"),
    ("Manu Koʻolau Luna",  "Upper Bird of the Northeast",  "東北上方之鳥"),
    ("Nālani Koʻolau Luna","Upper Heavens of the Northeast","東北上方天空"),
    ("Nā Leo Koʻolau Luna","Upper Voices of the Northeast","東北上方之聲"),
    ("Hikina Luna",        "Upper East",                  "上方正東"),
    ("Nā Leo Malanai Luna","Upper Voices of the Southeast","東南上方之聲"),
    ("Nālani Malanai Luna","Upper Heavens of the Southeast","東南上方天空"),
]

def _quadrant_for(idx: int) -> str:
    """Return the wind quadrant name for a 0-based house index (0-31).

    The 32 houses are ordered clockwise from North at 11.25° spacing:
      0– 5 → Koʻolau  (N through NE, indices  0– 5)
      6–11 → Malanai  (E through SE, indices  6–11)
     12–17 → Kona     (S through SW, indices 12–17)
     18–31 → Hoʻolua  (W through NW, indices 18–31)
    """
    if idx <= 5:
        return "Koʻolau"
    if idx <= 11:
        return "Malanai"
    if idx <= 17:
        return "Kona"
    return "Hoʻolua"


COMPASS_HOUSES: list[dict] = []
for _i, (_haw, _eng, _cn) in enumerate(_HOUSE_NAMES_CW):
    _deg = (_i * 11.25) % 360.0
    COMPASS_HOUSES.append(
        {
            "index": _i,
            "hawaiian": _haw,
            "english": _eng,
            "cn": _cn,
            "direction_deg": _deg,
            "quadrant": _quadrant_for(_i),
            "description": f"House {_i + 1} of 32: {_eng} ({_deg:.2f}°)",
            "description_cn": f"第{_i + 1}屋（共32屋）：{_cn}（{_deg:.2f}°）",
        }
    )

# ============================================================
# Star Lines
# ============================================================

STAR_LINES: dict[str, dict] = {
    "Ka Iwikuamoʻo": {
        "cn": "脊椎星線",
        "description": "The Backbone — runs N-S through the zenith of Hawaiʻi",
        "description_cn": "脊椎星線，南北方向貫穿夏威夷天頂",
        "stars": ["Hōkūpaʻa", "Hōkūleʻa", "Hikianalia", "Hānaiakamalama"],
        "stars_western": ["Polaris", "Arcturus", "Spica", "Southern Cross"],
        "significance": (
            "The Backbone of Heaven runs from Polaris (Hōkūpaʻa) in the north "
            "through the zenith star Hōkūleʻa (Arcturus) and down to the Southern "
            "Cross (Hānaiakamalama). This N-S line divides the sky into east and "
            "west halves and served as the primary orientation reference."
        ),
        "significance_cn": (
            "天空的脊椎從北方的北極星（Hōkūpaʻa）穿越天頂星 Hōkūleʻa（大角星），"
            "向下延伸至南十字座（Hānaiakamalama）。"
            "這條南北線將天空分為東西兩半，是主要的方向參考線。"
        ),
    },
    "Ke Ka o Makaliʻi": {
        "cn": "馬卡利伊的弦",
        "description": "The Canoe Bailer — Orion/Taurus/Sirius region",
        "description_cn": "獨木舟的水桶，獵戶座/金牛座/天狼星區域",
        "stars": ["Makaliʻi", "Āʻā", "Puanakau", "Kauluakoko", "Hōkūnui", "Hōkūlei"],
        "stars_western": ["Pleiades", "Sirius", "Rigel", "Betelgeuse", "Aldebaran", "Capella"],
        "significance": (
            "The Canoe Bailer arc stretches from the Pleiades (Makaliʻi) through "
            "Orion and down to Sirius (Āʻā). This prominent winter arc was used to "
            "bail water from the sky — metaphorically keeping the celestial canoe "
            "afloat. Its rising and setting points provided multiple compass bearings."
        ),
        "significance_cn": (
            "馬卡利伊的弦弧從昴星團（Makaliʻi）延伸穿越獵戶座，向下至天狼星（Āʻā）。"
            "這個顯眼的冬季弧被用來從天空中汲水——"
            "象徵性地保持天上獨木舟的漂浮。"
            "它的升起和落下點提供了多個羅盤方位。"
        ),
    },
    "Mānaiakalani": {
        "cn": "馬烏伊的魚鉤",
        "description": "Maui's Fishhook — Scorpius constellation",
        "description_cn": "茂伊的魚鉤，天蠍座",
        "stars": ["Ka Makau Nui o Maui", "Lehua"],
        "stars_western": ["Scorpius", "Antares"],
        "significance": (
            "Mānaiakalani is the magical fishhook of the demigod Maui, used to "
            "fish the Hawaiian Islands up from the ocean floor. The curve of Scorpius "
            "perfectly represents this fishhook shape. The heart star Antares (Lehua) "
            "glows red like the sacred lehua blossom, marking the summer south."
        ),
        "significance_cn": (
            "Mānaiakalani 是半神茂伊的神奇魚鉤，用來從海底釣起夏威夷群島。"
            "天蠍座的弧度完美地呈現了這個魚鉤形狀。"
            "心星心宿二（Lehua）像神聖的勒瓦花朵般紅色發光，標誌著夏季的南方。"
        ),
    },
    "Ka Lupe o Kawelo": {
        "cn": "卡韋洛的風箏",
        "description": "Kawelo's Kite — the Great Square of Pegasus",
        "description_cn": "卡韋洛的風箏，飛馬座大四方形",
        "stars": ["Ka Lupe o Kawelo"],
        "stars_western": ["Pegasus"],
        "significance": (
            "Ka Lupe o Kawelo, Kawelo's Kite, is the Great Square of Pegasus — "
            "a large, nearly empty square of stars visible in autumn. Named after "
            "the famous warrior Kawelo, this kite-shaped star pattern was used in "
            "autumn/winter navigation when the summer triangle had set."
        ),
        "significance_cn": (
            "Ka Lupe o Kawelo，卡韋洛的風箏，是飛馬座的大四方形——"
            "秋季可見的一個大型、幾乎空曠的星星四方形。"
            "以著名戰士卡韋洛命名，這個風箏形狀的星群在夏季三角形落下後用於秋冬航行。"
        ),
    },
}

# ============================================================
# Makahiki & Seasons
# ============================================================

SEASONS: dict[str, dict] = {
    "Makahiki": {
        "cn": "馬卡希基節",
        "description": (
            "Hawaiian New Year when Makaliʻi (Pleiades) rises at sunset (~Nov). "
            "A 4-month festival of peace, sports, and tribute to the god Lono."
        ),
        "description_cn": (
            "夏威夷新年，當 Makaliʻi（昴星團）於日落時升起（約11月）。"
            "四個月的和平、體育和向神靈羅諾致敬的節日。"
        ),
        "start_month": 11,
        "end_month": 2,
        "color": "#D4A017",
    },
    "Hoʻoilo": {
        "cn": "雨季",
        "description": "Wet season, Nov–Apr. Dominated by Ke Ka o Makaliʻi winter stars.",
        "description_cn": "雨季，11月至4月。以冬季星線馬卡利伊的弦為主。",
        "start_month": 11,
        "end_month": 4,
        "color": "#0B8FA8",
    },
    "Kau": {
        "cn": "旱季",
        "description": "Dry season, May–Oct. Mānaiakalani (Scorpius fishhook) dominates.",
        "description_cn": "旱季，5月至10月。馬烏伊的魚鉤（天蠍座）當道。",
        "start_month": 5,
        "end_month": 10,
        "color": "#D97B27",
    },
}

# ============================================================
# Cultural Introduction
# ============================================================

CULTURAL_INTRO: str = """
Polynesian / Hawaiian Star Lore — Wayfinding by the Stars

For over 2,000 years, Polynesian navigators voyaged across the vast Pacific Ocean
using nothing but the stars, ocean swells, wind, and birds. The Hawaiian tradition
of non-instrument navigation was nearly lost, but was revived in the 1970s by
Hokule'a Foundation and master navigator Nainoa Thompson.

The 32-House Star Compass divides the horizon into 32 equal houses (11.25° each),
named after the rising and setting points of stars. Rather than magnetic north,
the compass is oriented to Hema Ko Luna (the North Star) and Hema Ko Lalo (the
South celestial pole direction).

Key Concepts:
• Hōkūleʻa (Arcturus) — The zenith star of Hawaiʻi, rising directly overhead
• Ka Iwikuamoʻo — The Backbone star line, running N-S through zenith
• Makaliʻi (Pleiades) — Marks the Makahiki New Year when rising at sunset
• Ka Makau Nui o Maui — Scorpius, the Great Fishhook that raised the islands
"""

CULTURAL_INTRO_CN: str = """
玻里尼西亞／夏威夷星辰知識 — 星辰導航

兩千多年來，玻里尼西亞航海者僅憑星辰、海浪、風和鳥類橫越廣闊的太平洋。
夏威夷非儀器導航傳統幾近失傳，但在1970年代由 Hokule'a 基金會和
航海大師 Nainoa Thompson 重振。

32星屋羅盤將地平線分成32等份（每份11.25度），以星辰升起和落下的點命名。
羅盤不以磁北方向為準，而是朝向 Hema Ko Luna（北極星）和
Hema Ko Lalo（南天極方向）。

核心概念：
• Hōkūleʻa（大角星）— 夏威夷天頂星，直接從頭頂升起
• Ka Iwikuamoʻo — 脊椎星線，南北方向貫穿天頂
• Makaliʻi（昴星團）— 日落時升起，標誌馬卡希基新年
• Ka Makau Nui o Maui — 天蠍座，舉起群島的大魚鉤
"""
