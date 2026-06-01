"""
Lal Kitab (लाल किताब / 紅皮書) Astrology Module
Pt. Roop Chand Joshi's system — Kal Purush Kundli

Uses Vedic/Lahiri ayanamsa planetary positions.
House = Sign index + 1 (fixed, never Lagna-based).
"""

import swisseph as swe
import streamlit as st
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

from astro.lal_kitab_1952_expanded import (
    PLANET_IN_HOUSE_FULL,
    HOUSE_COLOR_RULES,
    WEEKDAY_DIRECTIONS,
    TIME_DIRECTIONS,
    FARMAN_RULES,
    GENERAL_REMEDIES,
    HOUSE_COLOR_REMEDIES,
    PalmistryLongevityCalculator,
    FarmanRuleEngine,
    get_auspicious_direction,
    get_complete_remedies,
    get_full_lal_kitab_analysis,
    get_palmistry_and_farman_analysis,
    calculate_35_year_cycle,
    is_blind_planet,
)

# ============================================================
# Constants
# ============================================================

RASHI_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
RASHI_ZH = [
    "白羊", "金牛", "雙子", "巨蟹", "獅子", "處女",
    "天秤", "天蠍", "射手", "摩羯", "水瓶", "雙魚",
]
RASHI_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
RASHI_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
]

PLANET_ZH = {
    "Sun": "太陽 (Surya)",
    "Moon": "月亮 (Chandra)",
    "Mars": "火星 (Mangal)",
    "Mercury": "水星 (Budh)",
    "Jupiter": "木星 (Guru)",
    "Venus": "金星 (Shukra)",
    "Saturn": "土星 (Shani)",
    "Rahu": "羅睺 (Rahu)",
    "Ketu": "計都 (Ketu)",
}
PLANET_ZH_SHORT = {
    "Sun": "日", "Moon": "月", "Mars": "火",
    "Mercury": "水", "Jupiter": "木", "Venus": "金",
    "Saturn": "土", "Rahu": "羅", "Ketu": "計",
}

# Pakka Ghar (Permanent Houses) for each planet in Lal Kitab
PAKKA_GHAR: Dict[str, List[int]] = {
    "Sun": [5],
    "Moon": [4],
    "Mars": [1, 8],
    "Mercury": [3, 6],
    "Jupiter": [9, 12],
    "Venus": [2, 7],
    "Saturn": [10, 11],
    "Rahu": [6, 11],
    "Ketu": [3, 12],
}

PLANET_COLORS = {
    "Sun":     "#FFD700",
    "Moon":    "#C8C8FF",
    "Mars":    "#FF4444",
    "Mercury": "#44CC88",
    "Jupiter": "#FFA500",
    "Venus":   "#FF69B4",
    "Saturn":  "#7B68EE",
    "Rahu":    "#9B59B6",
    "Ketu":    "#7D3C98",
}
PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mars": "♂", "Mercury": "☿",
    "Jupiter": "♃", "Venus": "♀", "Saturn": "♄",
    "Rahu": "☊", "Ketu": "☋",
}

PLANET_DAYS = {
    "Sun": "Sunday / 週日",
    "Moon": "Monday / 週一",
    "Mars": "Tuesday / 週二",
    "Mercury": "Wednesday / 週三",
    "Jupiter": "Thursday / 週四",
    "Venus": "Friday / 週五",
    "Saturn": "Saturday / 週六",
    "Rahu": "Saturday / 週六",
    "Ketu": "Tuesday / 週二",
}

PLANET_ASSOC_COLORS = {
    "Sun": "red / orange (紅/橙)",
    "Moon": "white / silver (白/銀)",
    "Mars": "red / coral (紅/珊瑚)",
    "Mercury": "green / emerald (綠/翠)",
    "Jupiter": "yellow / gold (黃/金)",
    "Venus": "white / pink / cream (白/粉/奶)",
    "Saturn": "black / dark blue (黑/深藍)",
    "Rahu": "smoky / multi-colour (煙灰/雜色)",
    "Ketu": "grey / smoke (灰/煙)",
}

PLANET_DONATIONS = {
    "Sun":     "wheat, jaggery, copper, red cloth (小麥、紅糖、銅器、紅布)",
    "Moon":    "rice, milk, white cloth, silver (大米、牛奶、白布、銀器)",
    "Mars":    "red lentils, jaggery, red cloth, copper (紅扁豆、紅糖、紅布、銅器)",
    "Mercury": "green moong dal, green cloth, emerald (綠豆、綠布、祖母綠)",
    "Jupiter": "yellow lentils, turmeric, yellow cloth, gold (黃扁豆、薑黃、黃布、黃金)",
    "Venus":   "white rice, cow ghee, white cloth, silver (白米、牛油、白布、銀器)",
    "Saturn":  "sesame seeds, black urad dal, iron, black cloth (芝麻、黑扁豆、鐵器、黑布)",
    "Rahu":    "black sesame, blue/black cloth, iron, coconut (黑芝麻、深藍/黑布、鐵、椰子)",
    "Ketu":    "sesame seeds, grey/multi-coloured cloth, iron (芝麻、灰/雜色布、鐵器)",
}

PLANET_FEED_ANIMALS = {
    "Sun":     "cow (牛)",
    "Moon":    "fish or cow (魚或牛)",
    "Mars":    "red ants / stray dogs (紅螞蟻/流浪狗)",
    "Mercury": "cows, young girls (牛、少女)",
    "Jupiter": "fish, yellow birds (魚、黃色鳥類)",
    "Venus":   "cows, white birds (牛、白色鳥類)",
    "Saturn":  "crows, black dogs (烏鴉、黑狗)",
    "Rahu":    "black crows, stray dogs (黑烏鴉、流浪狗)",
    "Ketu":    "stray dogs, crows (流浪狗、烏鴉)",
}


# ============================================================
# Planet-in-House Interpretations
# ============================================================

PLANET_IN_HOUSE_ZH: Dict[str, Dict[int, str]] = {
    "Sun": {
        1: "日在第一宮（白羊）：精力充沛，有領導魄力，自尊心強，父親緣薄，宜從政或軍旅，容易有頭部病症。",
        2: "日在第二宮（金牛）：財運靠自己努力，家族財富可期，眼睛或喉嚨需注意，表達能力強。",
        3: "日在第三宮（雙子）：膽量非凡，兄弟情深，文字能力出眾，兄弟可能為官，政府關係有利。",
        4: "日在第四宮（巨蟹）：家庭生活有波折，母親緣分複雜，心靈需要安定，不宜破壞老房子，祖業需保護。",
        5: "日在第五宮（獅子）：日居本位，威嚴卓著，孩子出眾，投機有利，創意豐富，領導才能天賦異稟。",
        6: "日在第六宮（處女）：政府或官方衝突，敵人難纏，健康需注意，但事業在官場仍有機遇，不宜行賄。",
        7: "日在第七宮（天秤）：婚姻受考驗，配偶強勢，可能遭遇衝突，合作關係需謹慎，宜善待配偶父親。",
        8: "日在第八宮（天蠍）：財富有起伏，遺產問題，壽命中等，神秘事物有緣，宜遠離貪腐行為。",
        9: "日在第九宮（射手）：宗教熱誠，得父蔭，哲學思維，長途旅行有利，宜尊重父親，善行豐盛。",
        10: "日在第十宮（摩羯）：事業有成，政府職位，聲望顯赫，父親影響大，但感情生活需注意，宜保持誠信。",
        11: "日在第十一宮（水瓶）：收入豐厚，朋友圈廣，社會地位上升，長子運佳，但需提防小人。",
        12: "日在第十二宮（雙魚）：秘密支出，外國緣分，靈性傾向，睡眠問題，宜謙遜行善，捐獻光明物（燈油等）。",
    },
    "Moon": {
        1: "月在第一宮（白羊）：性格善感，外貌出眾，母親緣深，情緒起伏，直覺敏銳，宜在水邊生活。",
        2: "月在第二宮（金牛）：財富由家庭積累，飲食豐盛，母親財運佳，口才好，家庭幸福，乳製品事業吉祥。",
        3: "月在第三宮（雙子）：兄弟姐妹情深，旅行頻繁，溝通能力佳，思想活躍，母親健康需注意。",
        4: "月在第四宮（巨蟹）：月居本位，家庭幸福，房地產有利，母親健在，感情豐富，心靈安定。",
        5: "月在第五宮（獅子）：孩子緣佳，創作力旺，情感豐富，投機需謹慎，教育事業有利。",
        6: "月在第六宮（處女）：健康問題，母親健康受影響，工作辛苦，宜服務他人，避免水邊危險。",
        7: "月在第七宮（天秤）：配偶美麗溫柔，婚姻幸福，伴侶事業有成，商業合作有利，感情表達流暢。",
        8: "月在第八宮（天蠍）：情緒起伏，秘密事務，神秘緣分，壽命與遺產事項複雜，宜冥想修行。",
        9: "月在第九宮（射手）：母親虔誠，宗教緣深，哲學思維，長途旅行吉祥，祖先加護。",
        10: "月在第十宮（摩羯）：事業有成，聲望來自大眾，情感事業兩全，媒體傳播有利，但需管理情緒。",
        11: "月在第十一宮（水瓶）：收入穩定，友誼珍貴，母親長壽，社交活躍，但夢想需踏實追求。",
        12: "月在第十二宮（雙魚）：靈性傾向，秘密生活，睡眠品質差，宜外出旅行或靜修，眼睛需注意。",
    },
    "Mars": {
        1: "火在第一宮（白羊）：火居本位，精力充沛，勇敢堅毅，事業有成，但衝動易怒，需控制脾氣，手足需注意。",
        2: "火在第二宮（金牛）：財運波動，家庭衝突，金融需謹慎，說話直接，宜種植樹木以求財運平穩。",
        3: "火在第三宮（雙子）：勇氣十足，兄弟情深但有摩擦，書寫有力，競爭心強，事業在中年後有成。",
        4: "火在第四宮（巨蟹）：家庭不寧，房產事務複雜，母親健康需注意，宜在家中種植植物，遠離衝突。",
        5: "火在第五宮（獅子）：創意旺盛，孩子英勇，投機有利有弊，教育事業有利，但需控制衝動決策。",
        6: "火在第六宮（處女）：勝過敵人，疾病抵抗力強，工作努力，但脾氣暴躁，宜從事軍警工作。",
        7: "火在第七宮（天秤）：婚姻衝突，配偶強勢，合作關係緊張，宜修煉耐性，尊重伴侶。",
        8: "火在第八宮（天蠍）：火居本位，無形力量強大，神秘事物緣深，但意外受傷需防，宜從事探索研究。",
        9: "火在第九宮（射手）：宗教熱情，父親嚴厲，哲學辯論，長途旅行，宜以信仰指導行動。",
        10: "火在第十宮（摩羯）：事業有成，政府職位，聲望顯赫，行動力強，宜鐵器或金屬相關事業。",
        11: "火在第十一宮（水瓶）：收入豐厚，朋友忠誠，夢想成真，但需防小人，兄弟助力關鍵。",
        12: "火在第十二宮（雙魚）：秘密行動，海外機遇，靈性修行，但需防足部傷害，宜捐獻紅色物品。",
    },
    "Mercury": {
        1: "水在第一宮（白羊）：口才絕佳，機智靈活，商業頭腦，學習能力強，但需警惕欺騙，皮膚問題需注意。",
        2: "水在第二宮（金牛）：財富通過智慧積累，家族溝通順暢，商業財運佳，寫作或教學有成。",
        3: "水在第三宮（雙子）：水居本位，口才一流，兄弟情深，寫作出版有成，旅行愉快，學習速度快。",
        4: "水在第四宮（巨蟹）：家庭教育重視，房地產智慧，母親受益，家中書籍豐富，商業從家出發。",
        5: "水在第五宮（獅子）：聰明孩子，教育事業有成，投機靠智慧，創意文字工作有利。",
        6: "水在第六宮（處女）：水居本位，工作效率高，健康知識豐富，服務行業，但需警惕神經緊張。",
        7: "水在第七宮（天秤）：配偶聰明，婚姻靠溝通，商業合作有利，但配偶可能健康欠佳。",
        8: "水在第八宮（天蠍）：神秘知識，研究有利，秘密財富，但需防止欺騙，靈性研究有成。",
        9: "水在第九宮（射手）：智慧父親，學問淵博，寫作出版宗教書籍，長途旅行學習。",
        10: "水在第十宮（摩羯）：事業靠智慧，媒體或商業有成，名聲來自溝通能力，政府關係良好。",
        11: "水在第十一宮（水瓶）：智慧帶來收入，社交網絡廣泛，朋友聰明，夢想靠計劃實現。",
        12: "水在第十二宮（雙魚）：靈性知識，秘密研究，外國語言有成，但需防止過度思慮，睡眠受影響。",
    },
    "Jupiter": {
        1: "木在第一宮（白羊）：仁慈寬容，知識豐富，受人尊重，長壽健康，孩子優秀，但需防止過度樂觀。",
        2: "木在第二宮（金牛）：財富積累，家族幸福，飲食豐盛，演講有力，黃金或珠寶事業有利。",
        3: "木在第三宮（雙子）：兄弟情深，知識傳播，寫作出版，旅行帶來智慧，溝通帶來財富。",
        4: "木在第四宮（巨蟹）：家庭幸福美滿，房地產豐盛，母親健康長壽，心靈安定，教育環境優良。",
        5: "木在第五宮（獅子）：孩子出眾，創意豐富，教育事業有成，投機小利，宗教靈性修行有成。",
        6: "木在第六宮（處女）：克服疾病，慈善工作，服務他人，但需防止懶散，宜醫療或社工事業。",
        7: "木在第七宮（天秤）：配偶仁慈賢德，婚姻美滿，商業合作有利，外交才能出眾，伴侶帶來財富。",
        8: "木在第八宮（天蠍）：長壽，神秘知識，遺產豐厚，靈性修行，但需防止秘密事務的危機。",
        9: "木在第九宮（射手）：木居本位，宗教虔誠，父親慈祥，哲學智慧，長途旅行吉祥，大師之命。",
        10: "木在第十宮（摩羯）：事業有成，政府高位，聲望崇高，慈善事業，但需防止驕傲自大。",
        11: "木在第十一宮（水瓶）：收入豐厚，朋友忠誠，夢想成真，孩子繁榮，社會貢獻有目共睹。",
        12: "木在第十二宮（雙魚）：木居本位，靈性極高，解脫之命，外國緣分，秘密善行，慈悲心強。",
    },
    "Venus": {
        1: "金在第一宮（白羊）：外貌出眾，魅力十足，藝術才能，感情豐富，但需防止放縱，宜藝術或娛樂事業。",
        2: "金在第二宮（金牛）：金居本位，財富豐盛，家庭美滿，飲食精緻，珠寶或藝術品事業有利，歌聲動人。",
        3: "金在第三宮（雙子）：溝通有魅力，藝術寫作，兄弟姐妹美麗，旅行享受，但需防止懶散。",
        4: "金在第四宮（巨蟹）：家庭豪華舒適，母親美麗溫柔，家居裝飾出眾，房地產有利，心靈平和。",
        5: "金在第五宮（獅子）：孩子美麗，藝術天賦，感情戀愛豐富，投機謹慎，娛樂創意事業有成。",
        6: "金在第六宮（處女）：感情遭遇困難，工作場合衝突，健康需注意，宜服務行業，避免奢侈。",
        7: "金在第七宮（天秤）：金居本位，婚姻美滿，配偶美麗富裕，商業合作有利，外交才能出眾。",
        8: "金在第八宮（天蠍）：神秘感情，遺產豐厚，靈性修行，但感情複雜，宜修煉冥想。",
        9: "金在第九宮（射手）：宗教藝術，父親富裕，哲學美學，長途旅行享受，外國藝術緣分。",
        10: "金在第十宮（摩羯）：事業靠魅力，娛樂傳媒有成，聲望從藝術而來，但需防止感情影響事業。",
        11: "金在第十一宮（水瓶）：收入豐厚，朋友美麗，夢想成真，社交生活精彩，藝術收藏有利。",
        12: "金在第十二宮（雙魚）：秘密感情，靈性享受，外國感情緣分，宜冥想，內在美比外在更重要。",
    },
    "Saturn": {
        1: "土在第一宮（白羊）：性格堅韌，生命有考驗，責任心重，中晚年有成，但青年時期艱辛，需培養耐心。",
        2: "土在第二宮（金牛）：財富積累緩慢但穩定，家庭需要耐心，說話謹慎，宜鐵器或煤炭相關事業。",
        3: "土在第三宮（雙子）：兄弟需幫助，書寫事業有成，努力旅行，溝通謹慎，年長後成就顯著。",
        4: "土在第四宮（巨蟹）：家庭有苦楚，房地產事務艱辛，母親健康受影響，宜在家中放置土星相關物品。",
        5: "土在第五宮（獅子）：孩子少但優秀，投機需謹慎，教育事業辛苦但有成，中年後孩子運改善。",
        6: "土在第六宮（處女）：勝過敵人，健康問題緩慢改善，工作紀律嚴格，服務事業有利。",
        7: "土在第七宮（天秤）：婚姻晚或有波折，配偶年長或性格嚴肅，商業合作需謹慎，婚後責任重大。",
        8: "土在第八宮（天蠍）：壽命長，神秘事物理解深，遺產問題，中晚年靈性覺悟，宜冥想修行。",
        9: "土在第九宮（射手）：父親嚴厲或缺乏，宗教義務繁重，哲學沉思，晚年精神有所寄托。",
        10: "土在第十宮（摩羯）：土居本位，事業有大成，政府高位，聲望來自努力，中晚年功成名就。",
        11: "土在第十一宮（水瓶）：土居本位，收入晚年豐厚，朋友老成持重，夢想靠努力實現，社會貢獻深遠。",
        12: "土在第十二宮（雙魚）：秘密苦惱，外國緣分複雜，靈性考驗，宜捐獻給窮人，慈悲心化解業力。",
    },
    "Rahu": {
        1: "羅在第一宮（白羊）：性格獨特，野心勃勃，外表有異域氣質，容易有頭痛或身份迷失，宜放銀椰子入水。",
        2: "羅在第二宮（金牛）：財運起伏，家庭有秘密，飲食習慣獨特，宜謹慎言語，敬重祖先。",
        3: "羅在第三宮（雙子）：溝通有利有弊，兄弟關係複雜，旅行多，思維超前，宜敬重手足。",
        4: "羅在第四宮（巨蟹）：家庭不安，母親緣分複雜，房地產問題，宜在家中保持清潔，敬奉蛇神。",
        5: "羅在第五宮（獅子）：孩子緣分複雜，投機需謹慎，創意獨特，宜捐獻給孤兒，靈性修行。",
        6: "羅在第六宮（處女）：羅在本位，勝過敵人，事業有利，但健康問題特殊，宜捐獻給祖先靈魂。",
        7: "羅在第七宮（天秤）：婚姻複雜，配偶有外族緣分，商業有利有弊，宜尊重配偶，謹慎合作。",
        8: "羅在第八宮（天蠍）：神秘力量，秘密財富，壽命中等，事故需防，宜冥想和靈性淨化。",
        9: "羅在第九宮（射手）：宗教觀念異常，父親緣分複雜，長途旅行有利有弊，宜敬重神靈祖先。",
        10: "羅在第十宮（摩羯）：事業波動，政府關係複雜，聲望有起伏，宜誠信經營，敬重上司。",
        11: "羅在第十一宮（水瓶）：羅在本位，收入有利，朋友圈廣泛，夢想靠努力，但需防財來財去。",
        12: "羅在第十二宮（雙魚）：秘密事務，外國緣分，靈性迷失，宜冥想靜修，放流椰子或鐵物入河。",
    },
    "Ketu": {
        1: "計在第一宮（白羊）：靈性本質，外表特殊，脫世傾向，神秘感強，需防意外，宜靜修冥想。",
        2: "計在第二宮（金牛）：財運不穩，家庭有隱秘，飲食需節制，宜捐獻食物給窮人，敬神儀式重要。",
        3: "計在第三宮（雙子）：計居本位，溝通有靈感，兄弟緣分複雜，旅行多，寫作有靈性色彩。",
        4: "計在第四宮（巨蟹）：家庭有隱秘苦楚，房地產複雜，母親健康受影響，宜敬奉家中神靈。",
        5: "計在第五宮（獅子）：孩子緣分複雜，靈性孩子，投機謹慎，教育有靈性方向，修行有成。",
        6: "計在第六宮（處女）：業力疾病，服務療愈，敵人特殊，宜靈性療愈工作，捐獻醫療品。",
        7: "計在第七宮（天秤）：婚姻有靈性考驗，配偶有靈性背景，商業有複雜因素，宜修行共渡。",
        8: "計在第八宮（天蠍）：神秘力量極強，靈性深度，祖先業力，壽命有考驗，宜靈性修行解業。",
        9: "計在第九宮（射手）：宗教修行，靈性父親，哲學深度，朝聖旅行，祖先加護豐厚。",
        10: "計在第十宮（摩羯）：事業有靈性方向，聲望與靈性相關，宜宗教或慈善事業，避免純物質追求。",
        11: "計在第十一宮（水瓶）：收入有靈性來源，夢想靈性豐盈，朋友有靈性追求，社群服務有成。",
        12: "計在第十二宮（雙魚）：計居本位，解脫之命，靈性最高境界，外國靈修，業力圓滿，超脫輪迴之相。",
    },
}

PLANET_IN_HOUSE_EN: Dict[str, Dict[int, str]] = {
    "Sun": {
        1: "Sun in House 1 (Aries): Energetic leader, strong ego, strained father relationship, prone to head ailments. Good for politics or military.",
        2: "Sun in House 2 (Taurus): Wealth through personal effort, strong vocal expression. Watch eyes and throat.",
        3: "Sun in House 3 (Gemini): Exceptional courage, sibling support, powerful writing, government connections beneficial.",
        4: "Sun in House 4 (Cancer): Turbulent home life, complex mother relationship, protect ancestral property.",
        5: "Sun in House 5 (Leo): Sun in Pakka Ghar — majestic authority, distinguished children, creative brilliance, natural leader.",
        6: "Sun in House 6 (Virgo): Government conflicts, persistent enemies. Career through official channels if honest.",
        7: "Sun in House 7 (Libra): Marital tensions, dominant spouse. Respect father-in-law to improve relations.",
        8: "Sun in House 8 (Scorpio): Fluctuating wealth, inheritance issues. Avoid corrupt practices.",
        9: "Sun in House 9 (Sagittarius): Religious devotion, paternal blessings, philosophical mind.",
        10: "Sun in House 10 (Capricorn): Career success, government positions, high reputation. Maintain integrity.",
        11: "Sun in House 11 (Aquarius): Good income, wide social circle. Beware of sycophants.",
        12: "Sun in House 12 (Pisces): Hidden expenses, spiritual inclinations. Donate oil lamps to temples.",
    },
    "Moon": {
        1: "Moon in House 1 (Aries): Sensitive and beautiful, deep bond with mother, intuitive. Water nearby is auspicious.",
        2: "Moon in House 2 (Taurus): Family wealth, good fortune through mother, happiness through dairy.",
        3: "Moon in House 3 (Gemini): Close sibling bonds, frequent travel, sharp communicator.",
        4: "Moon in House 4 (Cancer): Moon in Pakka Ghar — blissful home, healthy mother, real estate gains.",
        5: "Moon in House 5 (Leo): Blessed with children, creative nature. Cautious in speculation.",
        6: "Moon in House 6 (Virgo): Health concerns, mother's health affected. Serve others to improve karma.",
        7: "Moon in House 7 (Libra): Beautiful gentle spouse, happy marriage, business partnerships favoured.",
        8: "Moon in House 8 (Scorpio): Emotional turbulence, occult attraction. Meditation helps.",
        9: "Moon in House 9 (Sagittarius): Devout mother, religious fortune, long journeys blessed.",
        10: "Moon in House 10 (Capricorn): Public recognition, career linked to emotions or public service.",
        11: "Moon in House 11 (Aquarius): Steady income, long-lived mother. Keep dreams practical.",
        12: "Moon in House 12 (Pisces): Spiritual tendencies, hidden life, poor sleep. Protect eyesight.",
    },
    "Mars": {
        1: "Mars in House 1 (Aries): Mars in Pakka Ghar — fierce energy, bold action, success through courage. Control anger.",
        2: "Mars in House 2 (Taurus): Fluctuating finances, family arguments. Plant trees to stabilize wealth.",
        3: "Mars in House 3 (Gemini): Exceptional bravery, sibling rivalry possible. Career success in middle age.",
        4: "Mars in House 4 (Cancer): Domestic conflicts, property challenges. Grow plants at home.",
        5: "Mars in House 5 (Leo): Brave children, creative fire. Control impulsive decisions.",
        6: "Mars in House 6 (Virgo): Defeats enemies, strong immunity. Suited for military or police career.",
        7: "Mars in House 7 (Libra): Marital conflicts, dominant partner. Cultivate patience and mutual respect.",
        8: "Mars in House 8 (Scorpio): Mars in Pakka Ghar — occult power, longevity, mysterious strength. Guard against accidents.",
        9: "Mars in House 9 (Sagittarius): Religious fervour, strict father. Long journeys guided by faith.",
        10: "Mars in House 10 (Capricorn): Career success, government recognition. Good for metal industries.",
        11: "Mars in House 11 (Aquarius): Prosperous income, loyal friends. Guard against enemies.",
        12: "Mars in House 12 (Pisces): Secret plans, overseas opportunities. Protect feet; donate red items.",
    },
    "Mercury": {
        1: "Mercury in House 1 (Aries): Brilliant communicator, agile mind, business acumen. Watch for deception.",
        2: "Mercury in House 2 (Taurus): Wealth through intellect, harmonious family communication.",
        3: "Mercury in House 3 (Gemini): Mercury in Pakka Ghar — eloquent, scholarly, publishing success.",
        4: "Mercury in House 4 (Cancer): Educated household, real estate through wisdom.",
        5: "Mercury in House 5 (Leo): Bright children, educational career, creative writing success.",
        6: "Mercury in House 6 (Virgo): Mercury in Pakka Ghar — highly efficient, excellent in service professions.",
        7: "Mercury in House 7 (Libra): Intelligent spouse, communication-based marriage, business partnerships.",
        8: "Mercury in House 8 (Scorpio): Occult research, hidden wealth. Spiritual study beneficial.",
        9: "Mercury in House 9 (Sagittarius): Scholarly father, writing religious texts, educational travel.",
        10: "Mercury in House 10 (Capricorn): Career through intellect, media or commerce success.",
        11: "Mercury in House 11 (Aquarius): Income through ideas, smart friends, plans lead to success.",
        12: "Mercury in House 12 (Pisces): Spiritual knowledge, foreign languages. Avoid overthinking.",
    },
    "Jupiter": {
        1: "Jupiter in House 1 (Aries): Magnanimous, knowledgeable, respected, long-lived. Guard against overconfidence.",
        2: "Jupiter in House 2 (Taurus): Family wealth and happiness, eloquent speech. Gold or jewellery trade favoured.",
        3: "Jupiter in House 3 (Gemini): Close siblings, wisdom through travel, publishing success.",
        4: "Jupiter in House 4 (Cancer): Blessed home, healthy long-lived mother, excellent education.",
        5: "Jupiter in House 5 (Leo): Brilliant children, creative abundance, spiritual education.",
        6: "Jupiter in House 6 (Virgo): Overcomes illness, charitable work, service industries beneficial.",
        7: "Jupiter in House 7 (Libra): Wise and virtuous spouse, happy marriage. Business and diplomacy thrive.",
        8: "Jupiter in House 8 (Scorpio): Long life, occult wisdom, rich inheritance, late-life spiritual awakening.",
        9: "Jupiter in House 9 (Sagittarius): Jupiter in Pakka Ghar — highest fortune, devout father, blessed pilgrimages.",
        10: "Jupiter in House 10 (Capricorn): Exceptional career, high government position, charitable renown.",
        11: "Jupiter in House 11 (Aquarius): Abundant income, loyal friends, children prosperous.",
        12: "Jupiter in House 12 (Pisces): Jupiter in Pakka Ghar — supreme spiritual heights, liberation path, compassionate.",
    },
    "Venus": {
        1: "Venus in House 1 (Aries): Attractive, artistic, romantic. Arts or entertainment career blessed.",
        2: "Venus in House 2 (Taurus): Venus in Pakka Ghar — abundant wealth, loving family, jewellery business prospers.",
        3: "Venus in House 3 (Gemini): Charming communication, artistic writing. Avoid laziness.",
        4: "Venus in House 4 (Cancer): Luxurious home, beautiful mother, real estate profitable.",
        5: "Venus in House 5 (Leo): Beautiful children, artistic talents. Entertainment career successful.",
        6: "Venus in House 6 (Virgo): Relationship challenges, workplace conflicts. Service with care.",
        7: "Venus in House 7 (Libra): Venus in Pakka Ghar — beautiful wealthy spouse, blissful marriage.",
        8: "Venus in House 8 (Scorpio): Mysterious romance, rich inheritance. Complex emotional life.",
        9: "Venus in House 9 (Sagittarius): Religious arts, wealthy father, journeys of pleasure.",
        10: "Venus in House 10 (Capricorn): Career through charm, performing arts, fame through beauty.",
        11: "Venus in House 11 (Aquarius): Rich social life, artistic collections, dreams of luxury realised.",
        12: "Venus in House 12 (Pisces): Hidden romance, spiritual pleasure. Inner beauty most important.",
    },
    "Saturn": {
        1: "Saturn in House 1 (Aries): Resilient character, strong duty. Success comes with age and patience.",
        2: "Saturn in House 2 (Taurus): Slow but steady wealth accumulation. Iron or coal industries favoured.",
        3: "Saturn in House 3 (Gemini): Support siblings, cautious communication, great achievements late in life.",
        4: "Saturn in House 4 (Cancer): Family hardship, property challenges. Keep home clean and orderly.",
        5: "Saturn in House 5 (Leo): Few but outstanding children. Education through discipline.",
        6: "Saturn in House 6 (Virgo): Defeats enemies through persistence, disciplined service career.",
        7: "Saturn in House 7 (Libra): Late or difficult marriage, older or serious spouse.",
        8: "Saturn in House 8 (Scorpio): Long life, deep karmic understanding. Meditation beneficial.",
        9: "Saturn in House 9 (Sagittarius): Strict or absent father, heavy religious duties. Spiritual peace in later years.",
        10: "Saturn in House 10 (Capricorn): Saturn in Pakka Ghar — great career, high government position, earned through hard work.",
        11: "Saturn in House 11 (Aquarius): Saturn in Pakka Ghar — wealth in later years, steadfast friends, dreams through perseverance.",
        12: "Saturn in House 12 (Pisces): Hidden sorrows, complex foreign ties. Charitable giving to the poor dissolves karma.",
    },
    "Rahu": {
        1: "Rahu in House 1 (Aries): Unique personality, ambitious. Throw silver coconut into flowing water.",
        2: "Rahu in House 2 (Taurus): Fluctuating wealth, family secrets. Respect ancestors, speak carefully.",
        3: "Rahu in House 3 (Gemini): Communication double-edged, forward-thinking mind.",
        4: "Rahu in House 4 (Cancer): Domestic instability, property issues. Honour serpent deity.",
        5: "Rahu in House 5 (Leo): Complex children's karma, unique creativity. Donate to orphans.",
        6: "Rahu in House 6 (Virgo): Rahu in strong position — defeats enemies, career gains. Honour ancestors.",
        7: "Rahu in House 7 (Libra): Unusual marriage, complex business ties. Respect spouse.",
        8: "Rahu in House 8 (Scorpio): Occult power, accidents possible. Spiritual purification essential.",
        9: "Rahu in House 9 (Sagittarius): Unconventional religion, complex father. Foreign journeys mixed.",
        10: "Rahu in House 10 (Capricorn): Career fluctuations. Build reputation through honesty.",
        11: "Rahu in House 11 (Aquarius): Rahu in strong position — good income, wide network. Guard against money slipping.",
        12: "Rahu in House 12 (Pisces): Hidden affairs, spiritual confusion. Float coconut or iron in river.",
    },
    "Ketu": {
        1: "Ketu in House 1 (Aries): Spiritual nature, unique appearance, strong intuition. Guard against accidents; meditate.",
        2: "Ketu in House 2 (Taurus): Unstable finances, dietary discipline needed. Donate food to the poor.",
        3: "Ketu in House 3 (Gemini): Ketu in Pakka Ghar — inspired communication, spiritually-coloured writing.",
        4: "Ketu in House 4 (Cancer): Hidden domestic sorrows, complex mother bond. Honour household deities.",
        5: "Ketu in House 5 (Leo): Karmic children, spiritual creativity. Spiritual education path advised.",
        6: "Ketu in House 6 (Virgo): Karmic illness, healing service. Spiritual healing work recommended.",
        7: "Ketu in House 7 (Libra): Spiritual marriage, complex partnership karma.",
        8: "Ketu in House 8 (Scorpio): Deep occult power, ancestral karma. Longevity through spiritual practice.",
        9: "Ketu in House 9 (Sagittarius): Spiritual father, deep religious practice, pilgrimages blessed.",
        10: "Ketu in House 10 (Capricorn): Spiritually-oriented career. Avoid purely material ambitions.",
        11: "Ketu in House 11 (Aquarius): Income from spiritual sources, community service fulfilling.",
        12: "Ketu in House 12 (Pisces): Ketu in Pakka Ghar — liberation path, supreme detachment, karma fully resolved.",
    },
}


# ============================================================
# Upay (Remedies) Generator
# ============================================================

def _get_upay(planet: str, house: int, lang: str = "zh") -> List[str]:
    """Generate 3-5 authentic Lal Kitab remedies for a planet in a house."""

    base_zh = {
        "Sun": [
            "週日清晨向太陽供水（水中加紅花），同時誦讀 Aditya Hridayam",
            "佩戴紅寶石（Ruby），或在週日穿紅色/橙色衣服",
            "尊重父親及長輩，不要說謊或背叛",
            "向神廟捐獻小麥、紅糖和銅器",
        ],
        "Moon": [
            "週一早晨向月亮供牛奶，飲食中多攝取乳製品",
            "佩戴珍珠或月光石，或在週一穿白色衣服",
            "尊重母親，對女性保持尊重",
            "向河流放魚，或餵食牛奶給流浪動物",
        ],
        "Mars": [
            "週二向漢努曼廟供奉紅色花朵和椰子",
            "佩戴紅珊瑚（Red Coral），或穿紅色衣服",
            "避免爭吵和暴力行為，修煉耐心",
            "向廟宇捐獻紅扁豆（Masoor Dal）和紅糖",
        ],
        "Mercury": [
            "週三清晨餵食綠色蔬菜給乳牛",
            "佩戴祖母綠（Emerald）或穿綠色衣服",
            "定期閱讀和學習，尊重知識",
            "向神廟捐獻綠豆、黃油或綠布",
        ],
        "Jupiter": [
            "週四向毘濕奴廟供奉黃色花朵和薑黃",
            "佩戴黃色藍寶石（Yellow Sapphire）或穿黃色衣服",
            "餵食魚類（在河流/池塘中放魚），尊重老師和智者",
            "向神廟捐獻黃扁豆（Chana Dal）和薑黃",
        ],
        "Venus": [
            "週五向拉克希米女神供奉白花和牛奶",
            "佩戴鑽石或白色藍寶石，或穿白色/粉色衣服",
            "尊重女性，特別是妻子/母親/姐妹",
            "向神廟捐獻白米和牛油（Ghee）",
        ],
        "Saturn": [
            "週六向土星廟供奉芝麻油和黑芝麻",
            "佩戴藍色藍寶石（Blue Sapphire）或穿黑色/深藍色衣服",
            "餵食烏鴉和流浪狗（特別是黑色動物）",
            "向窮人捐獻黑扁豆（Urad Dal）、鐵器或黑芝麻",
        ],
        "Rahu": [
            "週六向羅睺廟供奉椰子和黑芝麻",
            "佩戴赫松尼特（Hessonite / Gomed）或穿深藍色衣服",
            "在週六流水中放入一個銀製椰子或鐵器",
            "向蛇神（Nag Devata）廟供奉牛奶",
        ],
        "Ketu": [
            "週二向象神（Ganesha）廟供奉紅花和椰子",
            "佩戴貓眼石（Cat's Eye）或穿灰色衣服",
            "餵食流浪狗，特別是斑點狗或雜色狗",
            "向神廟捐獻芝麻、黑毯或灰色布",
        ],
    }

    base_en = {
        "Sun": [
            "On Sunday at sunrise, offer water mixed with red flowers to the Sun while reciting Aditya Hridayam",
            "Wear a Ruby or wear red/orange clothes on Sundays",
            "Respect your father and elders; never lie or betray",
            "Donate wheat, jaggery and copper vessels to a temple",
        ],
        "Moon": [
            "On Monday morning, offer milk to the Moon; include dairy in your daily diet",
            "Wear a Pearl or moonstone, or wear white clothes on Mondays",
            "Respect your mother and all women in your life",
            "Release fish into a river or feed milk to stray animals",
        ],
        "Mars": [
            "On Tuesday, offer red flowers and coconut at a Hanuman temple",
            "Wear Red Coral or wear red clothes on Tuesdays",
            "Avoid arguments and violent behaviour; practise patience daily",
            "Donate red lentils (Masoor Dal) and jaggery to a temple",
        ],
        "Mercury": [
            "On Wednesday morning, feed green vegetables to a cow",
            "Wear an Emerald or wear green clothes on Wednesdays",
            "Read and study regularly; honour teachers and knowledge",
            "Donate green gram (moong dal), butter or green cloth to a temple",
        ],
        "Jupiter": [
            "On Thursday, offer yellow flowers and turmeric at a Vishnu temple",
            "Wear a Yellow Sapphire or wear yellow clothes on Thursdays",
            "Release fish into a river; respect Gurus and wise elders",
            "Donate yellow lentils (Chana Dal) and turmeric to a temple",
        ],
        "Venus": [
            "On Friday, offer white flowers and milk at a Lakshmi temple",
            "Wear a Diamond or white sapphire, or wear white/pink clothes on Fridays",
            "Honour all women in your life, especially wife, mother or sister",
            "Donate white rice and pure ghee (clarified butter) to a temple",
        ],
        "Saturn": [
            "On Saturday, offer sesame oil and black sesame seeds at a Shani temple",
            "Wear a Blue Sapphire or wear black/dark blue clothes on Saturdays",
            "Feed crows and stray dogs, especially black-coloured animals",
            "Donate black lentils (Urad Dal), iron items or black sesame to the poor",
        ],
        "Rahu": [
            "On Saturday, offer coconut and black sesame at a Rahu temple",
            "Wear Hessonite (Gomed) or wear dark blue clothes on Saturdays",
            "Float a silver coconut or iron object into flowing water on Saturdays",
            "Offer milk to a Nag Devata (serpent deity) temple",
        ],
        "Ketu": [
            "On Tuesday, offer red flowers and coconut at a Ganesha temple",
            "Wear Cat's Eye or wear grey clothes on Tuesdays",
            "Feed stray dogs, especially spotted or multi-coloured ones",
            "Donate sesame seeds, a black blanket or grey cloth to a temple",
        ],
    }

    house_upay_zh = {
        1:  "每日清晨洗臉後向太陽行禮，保持良好的個人形象和誠信",
        2:  "家中常備清潔，尊重長輩，避免說謊話，錢財勿藏於不潔之處",
        3:  "定期幫助兄弟姐妹，多寫作或學習，保持積極的溝通",
        4:  "在家中種植尼姆樹（Neem）或植物，敬奉家中神靈，敬愛母親",
        5:  "教育孩子宗教知識，對孤兒行善，避免過度賭博投機",
        6:  "保持良好衛生習慣，服務病人或窮人，克服懶惰",
        7:  "尊重配偶家人，婚姻儀式要完整莊重，避免婚前不潔行為",
        8:  "定期冥想，尊重祖先，不貪圖不義之財",
        9:  "尊重父親和上師，定期朝聖或前往廟宇，行善積德",
        10: "誠信經營，不貪腐，對下屬公平，樹立良好榜樣",
        11: "幫助老年朋友，履行承諾，不做空想，腳踏實地",
        12: "定期佈施，幫助囚犯或被遺棄者，靜修冥想",
    }

    house_upay_en = {
        1:  "Bow to the rising Sun each morning after washing; maintain personal integrity",
        2:  "Keep your home clean; respect elders; never lie; do not hide money in impure places",
        3:  "Regularly support your siblings; write, study, and maintain positive communication",
        4:  "Plant a Neem tree at home; honour household deities; love and care for your mother",
        5:  "Teach children religious knowledge; do good deeds for orphans; avoid excessive speculation",
        6:  "Maintain good hygiene; serve the sick or poor; overcome laziness",
        7:  "Respect your in-laws; perform marriage rites reverently; avoid pre-marital impurity",
        8:  "Meditate regularly; honour your ancestors; do not covet ill-gotten wealth",
        9:  "Respect your father and Guru; make regular temple visits or pilgrimages",
        10: "Conduct business with integrity; avoid corruption; treat subordinates fairly",
        11: "Help elderly friends; fulfil your promises; stay grounded",
        12: "Give to the poor regularly; help the abandoned; practise meditation",
    }

    base = base_zh if lang in ("zh", "zh_cn") else base_en
    house_extra = house_upay_zh if lang in ("zh", "zh_cn") else house_upay_en

    remedies = list(base.get(planet, []))
    if house in house_extra:
        remedies.append(house_extra[house])

    # Special combo rules
    if lang in ("zh", "zh_cn"):
        if planet == "Saturn" and house in [1, 4, 7, 10]:
            remedies.append("土星在角宮：每週六給七個流浪人/窮人分發麵包，可大幅改善業力影響")
        if planet == "Rahu" and house in [1, 4, 7, 10]:
            remedies.append("羅睺在角宮：在家門口埋入一塊銀板（不可見光），可穩定家宅運勢")
        if planet in ["Sun", "Moon"] and house == 7:
            remedies.append("日月在七宮：每日尊重配偶，避免自我中心，家和萬事興")
        if planet == "Mars" and house in [1, 2, 4, 7, 8]:
            remedies.append("火星在此宮（Mangal Dosha）：婚前需進行甘尼許普賈（Ganesh Puja），或先嫁給神（Kumbh Vivah）")
    else:
        if planet == "Saturn" and house in [1, 4, 7, 10]:
            remedies.append("Saturn in angular house: Distribute bread to 7 poor people every Saturday to mitigate karmic impact")
        if planet == "Rahu" and house in [1, 4, 7, 10]:
            remedies.append("Rahu in angular house: Bury a small silver plate at the threshold of your home to stabilise the household")
        if planet in ["Sun", "Moon"] and house == 7:
            remedies.append("Sun/Moon in 7th house: Respect your spouse daily; avoid ego-centrism — family harmony heals all")
        if planet == "Mars" and house in [1, 2, 4, 7, 8]:
            remedies.append("Mars in this house (Mangal Dosha): Perform Ganesh Puja before marriage, or perform Kumbh Vivah ritual")

    return remedies[:5]


# ============================================================
# Data Classes
# ============================================================

@dataclass
class LalKitabPlanet:
    name: str
    name_zh: str
    longitude: float
    house: int
    sign: str
    sign_zh: str
    sign_glyph: str
    sign_degree: float
    retrograde: bool
    pakka_ghar: List[int]
    in_pakka_ghar: bool
    is_benefic: bool
    glyph: str
    color: str


@dataclass
class LalKitabHouse:
    number: int
    sign: str
    sign_zh: str
    sign_glyph: str
    lord: str
    planets: List[str] = field(default_factory=list)


@dataclass
class LalKitabChart:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    location_name: str
    ayanamsa: float
    planets: List[LalKitabPlanet]
    houses: List[LalKitabHouse]
    lagna_sign: str
    lagna_house: int


# ============================================================
# Chart Computation
# ============================================================

def _normalize(deg: float) -> float:
    return deg % 360.0


@st.cache_data(ttl=3600, show_spinner=False)
def compute_lal_kitab_chart(
    year: int, month: int, day: int,
    hour: int, minute: int, timezone: float,
    latitude: float, longitude: float,
    location_name: str = "",
) -> LalKitabChart:
    """Compute Lal Kitab Kal Purush Kundli.
    House = sign index + 1 (Aries=1 ... Pisces=12).
    """
    swe.set_ephe_path("")
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    decimal_hour = hour + minute / 60.0 - timezone
    jd = swe.julday(year, month, day, decimal_hour)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Lagna (Ascendant) — for reference only
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b"P", swe.FLG_SIDEREAL)
    lagna_lon = _normalize(ascmc[0])
    lagna_sign_idx = int(lagna_lon / 30.0)
    lagna_sign = RASHI_NAMES[lagna_sign_idx]
    lagna_house = lagna_sign_idx + 1

    _PLANET_SWE = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
    }

    planets: List[LalKitabPlanet] = []

    for pname, pid in _PLANET_SWE.items():
        result, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        lon = _normalize(result[0])
        speed = result[3]
        retrograde = speed < 0
        sign_idx = int(lon / 30.0)
        house_num = sign_idx + 1
        sign_deg = lon % 30.0
        pg = PAKKA_GHAR.get(pname, [])
        planets.append(LalKitabPlanet(
            name=pname,
            name_zh=PLANET_ZH.get(pname, pname),
            longitude=lon,
            house=house_num,
            sign=RASHI_NAMES[sign_idx],
            sign_zh=RASHI_ZH[sign_idx],
            sign_glyph=RASHI_GLYPHS[sign_idx],
            sign_degree=sign_deg,
            retrograde=retrograde,
            pakka_ghar=pg,
            in_pakka_ghar=(house_num in pg),
            is_benefic=(pname in ["Jupiter", "Venus", "Moon", "Mercury"]),
            glyph=PLANET_GLYPHS.get(pname, pname[0]),
            color=PLANET_COLORS.get(pname, "#FFFFFF"),
        ))

    # Rahu (Mean North Node)
    rahu_res, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    rahu_lon = _normalize(rahu_res[0])
    sign_idx = int(rahu_lon / 30.0)
    pg_r = PAKKA_GHAR.get("Rahu", [])
    planets.append(LalKitabPlanet(
        name="Rahu", name_zh=PLANET_ZH["Rahu"],
        longitude=rahu_lon, house=sign_idx + 1,
        sign=RASHI_NAMES[sign_idx], sign_zh=RASHI_ZH[sign_idx],
        sign_glyph=RASHI_GLYPHS[sign_idx],
        sign_degree=rahu_lon % 30.0,
        retrograde=True,
        pakka_ghar=pg_r, in_pakka_ghar=((sign_idx + 1) in pg_r),
        is_benefic=False,
        glyph=PLANET_GLYPHS["Rahu"], color=PLANET_COLORS["Rahu"],
    ))

    # Ketu = Rahu + 180°
    ketu_lon = _normalize(rahu_lon + 180.0)
    sign_idx_k = int(ketu_lon / 30.0)
    pg_k = PAKKA_GHAR.get("Ketu", [])
    planets.append(LalKitabPlanet(
        name="Ketu", name_zh=PLANET_ZH["Ketu"],
        longitude=ketu_lon, house=sign_idx_k + 1,
        sign=RASHI_NAMES[sign_idx_k], sign_zh=RASHI_ZH[sign_idx_k],
        sign_glyph=RASHI_GLYPHS[sign_idx_k],
        sign_degree=ketu_lon % 30.0,
        retrograde=True,
        pakka_ghar=pg_k, in_pakka_ghar=((sign_idx_k + 1) in pg_k),
        is_benefic=False,
        glyph=PLANET_GLYPHS["Ketu"], color=PLANET_COLORS["Ketu"],
    ))

    # Build 12 fixed houses
    houses: List[LalKitabHouse] = []
    for h in range(1, 13):
        sign_i = h - 1
        h_planets = [p.name for p in planets if p.house == h]
        houses.append(LalKitabHouse(
            number=h,
            sign=RASHI_NAMES[sign_i],
            sign_zh=RASHI_ZH[sign_i],
            sign_glyph=RASHI_GLYPHS[sign_i],
            lord=RASHI_LORDS[sign_i],
            planets=h_planets,
        ))

    return LalKitabChart(
        year=year, month=month, day=day,
        hour=hour, minute=minute, timezone=timezone,
        location_name=location_name,
        ayanamsa=ayanamsa,
        planets=planets,
        houses=houses,
        lagna_sign=lagna_sign,
        lagna_house=lagna_house,
    )


# ============================================================
# SVG Chart — North Indian Style (4×4 grid)
# ============================================================

def _build_lal_kitab_svg(chart: LalKitabChart, width: int = 480) -> str:
    """Build a North Indian Kundli SVG for the Lal Kitab chart."""
    H = width
    c = width // 4
    half = c // 2
    pad = 6

    # House → abbreviated planet labels
    house_planets: Dict[int, List[Tuple[str, str]]] = {h: [] for h in range(1, 13)}
    for p in chart.planets:
        abbr = PLANET_ZH_SHORT.get(p.name, p.name[0])
        retro = "\u211e" if p.retrograde and p.name not in ("Rahu", "Ketu") else ""
        pk = "\u2605" if p.in_pakka_ghar else ""
        house_planets[p.house].append((f"{abbr}{retro}{pk}", p.color))

    # North Indian grid: (row, col) → house number
    GRID = {
        (0, 0): 12, (0, 1): 1,  (0, 2): 2,  (0, 3): 3,
        (1, 0): 11,                            (1, 3): 4,
        (2, 0): 10,                            (2, 3): 5,
        (3, 0): 9,  (3, 1): 8,  (3, 2): 7,  (3, 3): 6,
    }

    BG = "#0C0A1A"
    BORDER_COL = "#8B1A1A"
    GRID_LINE = "#3A0808"
    CENTER_BG = "rgba(139,26,26,0.12)"
    HOUSE_BG = "rgba(12,10,26,0.9)"
    ACTIVE_BG = "rgba(50,8,8,0.55)"
    TEXT_SIGN = "#C8A04A"
    TEXT_HOUSE = "#7A4A4A"
    CENTER_TEXT = "#C41E3A"

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{H}" height="{H}" '
        f'viewBox="0 0 {H} {H}" style="font-family:\'Noto Sans TC\',sans-serif;'
        f'background:{BG};">',
        f'<rect x="1" y="1" width="{H-2}" height="{H-2}" fill="{BG}" '
        f'stroke="{BORDER_COL}" stroke-width="2.5" rx="4"/>',
        # Center diagonal marks
        f'<line x1="{c}" y1="{c}" x2="{3*c}" y2="{3*c}" stroke="{GRID_LINE}" '
        f'stroke-width="1" opacity="0.6"/>',
        f'<line x1="{3*c}" y1="{c}" x2="{c}" y2="{3*c}" stroke="{GRID_LINE}" '
        f'stroke-width="1" opacity="0.6"/>',
        # Center block
        f'<rect x="{c}" y="{c}" width="{2*c}" height="{2*c}" fill="{CENTER_BG}" '
        f'stroke="{BORDER_COL}" stroke-width="1.5" rx="2"/>',
    ]

    # Center text
    cx = 2 * c
    cy_c = int(1.5 * c)
    lines += [
        f'<text x="{cx}" y="{cy_c - 26}" text-anchor="middle" '
        f'font-size="13" font-weight="bold" fill="{CENTER_TEXT}" '
        f'font-family="Cinzel,serif" letter-spacing="1">\u0932\u093e\u0932 \u0915\u093f\u0924\u093e\u092c</text>',
        f'<text x="{cx}" y="{cy_c - 8}" text-anchor="middle" '
        f'font-size="11" fill="{CENTER_TEXT}">Lal Kitab</text>',
        f'<text x="{cx}" y="{cy_c + 8}" text-anchor="middle" '
        f'font-size="9.5" fill="#AA8888">\u7d05\u76ae\u66f8\u547d\u76e4</text>',
        f'<text x="{cx}" y="{cy_c + 30}" text-anchor="middle" '
        f'font-size="8.5" fill="#666688">\u4e0a\u5347\uff1a{chart.lagna_sign}</text>',
        f'<text x="{cx}" y="{cy_c + 44}" text-anchor="middle" '
        f'font-size="8" fill="#555566">(\u7b2c{chart.lagna_house}\u5c45)</text>',
    ]

    # House cells
    for (row, col), house_num in GRID.items():
        x, y = col * c, row * c
        sign_i = house_num - 1
        plist = house_planets.get(house_num, [])
        has_planets = bool(plist)
        bg = ACTIVE_BG if has_planets else HOUSE_BG

        lines.append(
            f'<rect x="{x+1}" y="{y+1}" width="{c-2}" height="{c-2}" '
            f'fill="{bg}" stroke="{GRID_LINE}" stroke-width="0.8" rx="1"/>'
        )
        # House number
        lines.append(
            f'<text x="{x+pad}" y="{y+pad+9}" font-size="8" fill="{TEXT_HOUSE}" '
            f'font-weight="bold">{house_num}</text>'
        )
        # Sign glyph
        lines.append(
            f'<text x="{x+c-pad-2}" y="{y+pad+10}" font-size="11" fill="{TEXT_SIGN}" '
            f'text-anchor="end">{RASHI_GLYPHS[sign_i]}</text>'
        )
        # Sign name (bottom)
        lines.append(
            f'<text x="{x+half}" y="{y+c-pad}" font-size="7" fill="{TEXT_SIGN}" '
            f'text-anchor="middle" opacity="0.65">{RASHI_ZH[sign_i]}</text>'
        )
        # Planet abbreviations
        if plist:
            py_start = y + 26
            for i, (pabbr, pcol) in enumerate(plist[:4]):
                lines.append(
                    f'<text x="{x+half}" y="{py_start + i*12}" '
                    f'font-size="9.5" fill="{pcol}" text-anchor="middle" '
                    f'font-weight="bold">{pabbr}</text>'
                )

    # Grid lines
    for i in range(5):
        lines.append(
            f'<line x1="{i*c}" y1="0" x2="{i*c}" y2="{H}" '
            f'stroke="{GRID_LINE}" stroke-width="0.4" opacity="0.5"/>'
        )
        lines.append(
            f'<line x1="0" y1="{i*c}" x2="{H}" y2="{i*c}" '
            f'stroke="{GRID_LINE}" stroke-width="0.4" opacity="0.5"/>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


# ============================================================
# Life Summary
# ============================================================

def _compute_summary(chart: LalKitabChart, lang: str = "zh") -> Dict[str, str]:
    """Generate a brief life-themes summary."""
    strengths = []
    weaknesses = []
    themes = []

    for p in chart.planets:
        if p.in_pakka_ghar:
            if lang in ("zh", "zh_cn"):
                strengths.append(
                    f"{p.glyph} {p.name_zh} 在第{p.house}宮（本位 Pakka Ghar）：力量強盛，此宮領域大吉"
                )
            else:
                strengths.append(
                    f"{p.glyph} {p.name_zh} in House {p.house} (Pakka Ghar): Great strength in this life area"
                )
        elif not p.is_benefic and p.retrograde and p.name not in ("Rahu", "Ketu"):
            if lang in ("zh", "zh_cn"):
                weaknesses.append(
                    f"{p.glyph} {p.name_zh} 逆行於第{p.house}宮：此宮領域需留意、加強化解修煉"
                )
            else:
                weaknesses.append(
                    f"{p.glyph} {p.name_zh} retrograde in House {p.house}: This life area needs extra attention"
                )

    occupied = [h for h in chart.houses if h.planets]
    if lang in ("zh", "zh_cn"):
        if any(h.number in [1, 5, 9] for h in occupied):
            themes.append("命主具有強烈的領導力、創意與哲學思想（三方宮有星）")
        if any(h.number in [2, 6, 10] for h in occupied):
            themes.append("財富與事業是人生重要課題（成長宮有星）")
        if any(h.number in [4, 8, 12] for h in occupied):
            themes.append("靈性修行、家庭和隱秘事務是生命核心主題（解脫宮有星）")
    else:
        if any(h.number in [1, 5, 9] for h in occupied):
            themes.append("Strong leadership, creativity and philosophy (trine houses occupied)")
        if any(h.number in [2, 6, 10] for h in occupied):
            themes.append("Wealth and career are major life themes (upachaya houses occupied)")
        if any(h.number in [4, 8, 12] for h in occupied):
            themes.append("Spirituality, family and hidden matters are core life themes (moksha houses occupied)")

    no_str = "無特別突出之處" if lang in ("zh", "zh_cn") else "No outstanding strengths detected"
    no_wk = "無明顯弱點" if lang in ("zh", "zh_cn") else "No obvious weaknesses detected"
    balanced = "均衡命盤，各領域平衡發展" if lang in ("zh", "zh_cn") else "Balanced chart — well-rounded life"

    return {
        "strengths": "\n".join(strengths) or no_str,
        "weaknesses": "\n".join(weaknesses) or no_wk,
        "themes": "\n".join(themes) or balanced,
    }


# ============================================================
# CSS
# ============================================================

_LK_CSS = """
<style>
.lk-title-banner {
    background: linear-gradient(135deg, #1a0505 0%, #2d0808 50%, #1a0505 100%);
    border: 1px solid #8B1A1A;
    border-radius: 8px;
    padding: 18px 24px;
    margin-bottom: 16px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.lk-title-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(196,30,58,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.lk-title {
    font-family: 'Cinzel', serif;
    font-size: 1.55rem;
    font-weight: 700;
    color: #C41E3A;
    letter-spacing: 3px;
    text-shadow: 0 0 22px rgba(196,30,58,0.45);
    margin: 0;
    position: relative;
}
.lk-subtitle {
    font-size: 0.82rem;
    color: #C8A04A;
    margin-top: 5px;
    letter-spacing: 1px;
    position: relative;
}
.lk-section-title {
    font-family: 'Cinzel', serif;
    font-size: 0.95rem;
    color: #C41E3A;
    letter-spacing: 2px;
    border-bottom: 1px solid rgba(139,26,26,0.4);
    padding-bottom: 6px;
    margin: 16px 0 10px 0;
}
.lk-upay-item {
    padding: 8px 12px;
    border-left: 3px solid #8B1A1A;
    background: rgba(139,26,26,0.08);
    border-radius: 0 6px 6px 0;
    margin-bottom: 6px;
    font-size: 0.87rem;
    color: #D4C0B0;
    line-height: 1.5;
}
.lk-strength-item {
    padding: 6px 10px;
    border-left: 3px solid #F0C040;
    background: rgba(240,192,64,0.06);
    border-radius: 0 4px 4px 0;
    margin-bottom: 5px;
    font-size: 0.85rem;
    color: #D4C0B0;
}
.lk-weakness-item {
    padding: 6px 10px;
    border-left: 3px solid #9B59B6;
    background: rgba(155,89,182,0.06);
    border-radius: 0 4px 4px 0;
    margin-bottom: 5px;
    font-size: 0.85rem;
    color: #D4C0B0;
}
</style>
"""


# ============================================================
# Main Streamlit Renderer
# ============================================================

def render_lal_kitab_chart(
    chart: LalKitabChart,
    lang: str = "zh",
    after_chart_hook=None,
):
    """Render the complete Lal Kitab chart in Streamlit."""
    st.markdown(_LK_CSS, unsafe_allow_html=True)

    # Title banner
    if lang in ("zh", "zh_cn"):
        title_text = "\u0932\u093e\u0932 \u0915\u093f\u0924\u093e\u092c \u00b7 \u7d05\u76ae\u66f8\u547d\u76e4"
        subtitle_text = "Lal Kitab \u00b7 \u5361\u723e\u666e\u62c9\u4ec0\u5764\u5e73\u91cc\uff08\u56fa\u5b9a\u5bae\u4f4d\u7cfb\u7d71\uff09"
    else:
        title_text = "\u0932\u093e\u0932 \u0915\u093f\u0924\u093e\u092c \u00b7 Lal Kitab Chart"
        subtitle_text = "Kal Purush Kundli \u2014 Fixed House System (Lahiri Ayanamsa)"

    st.markdown(
        f'<div class="lk-title-banner">'
        f'<div class="lk-title">{title_text}</div>'
        f'<div class="lk-subtitle">{subtitle_text}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Tabs
    if lang in ("zh", "zh_cn"):
        tab_labels = [
            "\U0001f4dc \u547d\u76e4\u5716",
            "\U0001fa90 \u884c\u661f\u8a73\u89e3",
            "\U0001f534 \u6d88\u7a3d\u5316\u89e3\uff08Upay\uff09",
            "\u2728 \u547d\u5c40\u7e3d\u7d50",
            "\U0001f4d6 1952\u5e74\u7248",
        ]
    else:
        tab_labels = [
            "\U0001f4dc Chart",
            "\U0001fa90 Planet Details",
            "\U0001f534 Remedies (Upay)",
            "\u2728 Life Summary",
            "\U0001f4d6 1952 Edition",
        ]

    tab_chart, tab_planets, tab_upay, tab_summary, tab_1952 = st.tabs(tab_labels)

    # ── Tab 1: Kundli Chart ───────────────────────────────────
    with tab_chart:
        col_svg, col_info = st.columns([1, 1])

        with col_svg:
            svg = _build_lal_kitab_svg(chart, width=480)
            st.markdown(
                f'<div style="display:flex;justify-content:center;margin:8px 0;">'
                f'{svg}</div>',
                unsafe_allow_html=True,
            )

        with col_info:
            if lang in ("zh", "zh_cn"):
                st.markdown("**\U0001f4d0 \u57fa\u672c\u8cc7\u8a0a**")
                st.markdown(
                    f"- **\u6b72\u5dee (Ayanamsa)**\uff1a{chart.ayanamsa:.4f}\u00b0\n"
                    f"- **\u51fa\u751f\u4e0a\u5347**\uff1a{chart.lagna_sign}\uff08\u7b2c{chart.lagna_house}\u5c45\uff09\n"
                    f"- **\u65e5\u671f**\uff1a{chart.year}/{chart.month:02d}/{chart.day:02d}\n"
                    f"- **\u6642\u9593**\uff1a{chart.hour:02d}:{chart.minute:02d} UTC{chart.timezone:+.1f}\n"
                    f"- **\u5730\u9ede**\uff1a{chart.location_name or 'N/A'}"
                )
                st.divider()
                st.markdown("**\U0001f4d6 \u547d\u76e4\u8aaa\u660e**")
                st.markdown(
                    "\u7d05\u76ae\u66f8\uff08Lal Kitab\uff09\u4f7f\u7528**\u5361\u723e\u666e\u62c9\u4ec0\u5764\u5e73\u91cc**\u2014\u2014"
                    "\u767d\u7f8a\u5ea7\u6c38\u9060\u662f\u7b2c\u4e00\u5c45\uff0c\u4e0d\u8ad6\u4e0a\u5347\u661f\u5ea7\u3002"
                    "\u6bcf\u984f\u884c\u661f\u6240\u5728\u7684**\u661f\u5ea7**\u5373\u6c7a\u5b9a\u5176\u6240\u5728**\u5bae\u4f4d**\u3002\n\n"
                    "\u2b50 **Pakka Ghar\uff08\u672c\u4f4d\uff09**\uff1a\u884c\u661f\u5728\u5176\u6c38\u4e45\u672c\u5c45\uff0c\u529b\u91cf\u6700\u5f37\u3002"
                )
            else:
                st.markdown("**\U0001f4d0 Chart Information**")
                st.markdown(
                    f"- **Ayanamsa**\uff1a{chart.ayanamsa:.4f}\u00b0\n"
                    f"- **Natal Lagna**\uff1a{chart.lagna_sign} (House {chart.lagna_house})\n"
                    f"- **Date**\uff1a{chart.year}/{chart.month:02d}/{chart.day:02d}\n"
                    f"- **Time**\uff1a{chart.hour:02d}:{chart.minute:02d} UTC{chart.timezone:+.1f}\n"
                    f"- **Location**\uff1a{chart.location_name or 'N/A'}"
                )
                st.divider()
                st.markdown("**\U0001f4d6 About Lal Kitab**")
                st.markdown(
                    "Lal Kitab uses the **Kal Purush Kundli** \u2014 Aries is always House 1, "
                    "regardless of Lagna. Each planet's **sign** determines its house number.\n\n"
                    "\u2b50 **Pakka Ghar** (Permanent House): A planet in its Pakka Ghar is at maximum strength."
                )

        # Planet table
        if lang in ("zh", "zh_cn"):
            st.markdown("#### \U0001fa90 \u884c\u661f\u4f4d\u7f6e\u4e00\u89bd")
        else:
            st.markdown("#### \U0001fa90 Planetary Positions")

        rows = []
        for p in chart.planets:
            deg = int(p.sign_degree)
            arc_minute = int((p.sign_degree - deg) * 60)
            retro_str = "\u211e" if p.retrograde and p.name not in ("Rahu", "Ketu") else ""
            pakka_str = "\u2605 Pakka Ghar" if p.in_pakka_ghar else ""
            if lang in ("zh", "zh_cn"):
                rows.append({
                    "\u884c\u661f": f"{p.glyph} {p.name_zh}",
                    "\u5bae\u4f4d": p.house,
                    "\u661f\u5ea7": f"{p.sign_glyph} {p.sign_zh}",
                    "\u5bae\u5167\u5ea6\u6578": f"{deg}\u00b0{arc_minute:02d}'",
                    "\u9006\u884c": retro_str,
                    "\u672c\u4f4d": pakka_str,
                })
            else:
                rows.append({
                    "Planet": f"{p.glyph} {p.name_zh}",
                    "House": p.house,
                    "Sign": f"{p.sign_glyph} {p.sign}",
                    "Degree": f"{deg}\u00b0{arc_minute:02d}'",
                    "Retro": retro_str,
                    "Status": pakka_str,
                })
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    # ── Tab 2: Planet Details ─────────────────────────────────
    with tab_planets:
        if lang in ("zh", "zh_cn"):
            st.markdown("#### \u884c\u661f\u5bae\u4f4d\u8a73\u89e3\uff08\u7d05\u76ae\u66f8\u89e3\u8b80\uff09")
            st.caption("\u6bcf\u984f\u884c\u661f\u5728\u6240\u5728\u5bae\u4f4d\u7684\u7d05\u76ae\u66f8\u539f\u5178\u610f\u7fa9\u3002")
        else:
            st.markdown("#### Planet-in-House Interpretations (Lal Kitab)")
            st.caption("Authentic Lal Kitab meanings for each planet in its Kal Purush Kundli house.")

        for p in chart.planets:
            if lang in ("zh", "zh_cn"):
                interp_db = PLANET_IN_HOUSE_ZH
                pakka_note = "\uff08\u2605 \u672c\u4f4d\u52a0\u6210\uff09" if p.in_pakka_ghar else ""
                retro_note = "\uff08\u211e \u9006\u884c\uff09" if p.retrograde and p.name not in ("Rahu", "Ketu") else ""
                label = f"{p.glyph} {p.name_zh} \u2014 \u7b2c{p.house}\u5c45 {p.sign_glyph}{p.sign_zh} {pakka_note}{retro_note}"
            else:
                interp_db = PLANET_IN_HOUSE_EN
                pakka_note = " (\u2605 Pakka Ghar)" if p.in_pakka_ghar else ""
                retro_note = " (\u211e Retrograde)" if p.retrograde and p.name not in ("Rahu", "Ketu") else ""
                label = f"{p.glyph} {p.name_zh} \u2014 House {p.house} {p.sign_glyph}{p.sign}{pakka_note}{retro_note}"

            interp = interp_db.get(p.name, {}).get(p.house, "")
            with st.expander(label, expanded=False):
                if interp:
                    st.markdown(f"\U0001f4d6 {interp}")
                if p.in_pakka_ghar:
                    if lang in ("zh", "zh_cn"):
                        st.success(f"\u2728 \u6b64\u884c\u661f\u4f4d\u65bc\u5176\u6c38\u4e45\u672c\u5c45\uff08Pakka Ghar: {p.pakka_ghar}\uff09\uff0c\u529b\u91cf\u6700\u5f37\uff01")
                    else:
                        st.success(f"\u2728 This planet is in its Pakka Ghar (Permanent House {p.pakka_ghar}) \u2014 maximum strength!")
                if p.retrograde and p.name not in ("Rahu", "Ketu"):
                    if lang in ("zh", "zh_cn"):
                        st.warning("\u26a0\ufe0f \u6b64\u884c\u661f\u9006\u884c\uff0c\u76f8\u95dc\u4e8b\u52a1\u9700\u8981\u52a0\u500d\u52aa\u529b\u6216\u9032\u884c\u7279\u6b8a\u6d88\u89e3\u5100\u5f0f\u3002")
                    else:
                        st.warning("\u26a0\ufe0f This planet is retrograde \u2014 related matters need extra effort or specific remedial rituals.")

    # ── Tab 3: Upay (Remedies) ────────────────────────────────
    with tab_upay:
        if lang in ("zh", "zh_cn"):
            st.markdown("#### \U0001f534 \u7d05\u76ae\u66f8\u6d88\u7a3d\u5316\u89e3\uff08Upay\uff09")
            st.caption(
                "\u6839\u64da\u6bcf\u984f\u884c\u661f\u7684\u5bae\u4f4d\uff0c\u63d0\u4f9b 3\u20135 \u500b\u5373\u6642\u53ef\u884c\u3001\u771f\u5be6\u6709\u6548\u7684\u7d05\u76ae\u66f8\u5316\u89e3\u65b9\u6cd5\u3002"
                "Upay \u662f\u7d05\u76ae\u66f8\u6700\u91cd\u8981\u7684\u7279\u8272\uff0c\u4ee5\u7c21\u55ae\u7684\u65e5\u5e38\u884c\u70ba\u5316\u89e3\u696d\u529b\u3002"
            )
        else:
            st.markdown("#### \U0001f534 Lal Kitab Remedies (Upay)")
            st.caption(
                "For each planet in its house, 3\u20135 practical, affordable Lal Kitab remedies. "
                "Upay dissolves karma through simple daily actions."
            )

        for p in chart.planets:
            remedies = _get_upay(p.name, p.house, lang)
            day_str = PLANET_DAYS.get(p.name, "")
            if lang in ("zh", "zh_cn"):
                label = f"{p.glyph} {p.name_zh} \u2014 \u7b2c{p.house}\u5c45 \u00b7 \u5316\u89e3\u65e5\uff1a{day_str}"
            else:
                label = f"{p.glyph} {p.name_zh} \u2014 House {p.house} \u00b7 Remedy Day: {day_str}"

            with st.expander(label, expanded=False):
                if lang in ("zh", "zh_cn"):
                    st.markdown(f"**\u6350\u737b\u7269\u54c1**\uff1a{PLANET_DONATIONS.get(p.name, '')}")
                    st.markdown(f"**\u9905\u98df\u52d5\u7269**\uff1a{PLANET_FEED_ANIMALS.get(p.name, '')}")
                    st.markdown(f"**\u5409\u7965\u984f\u8272**\uff1a{PLANET_ASSOC_COLORS.get(p.name, '')}")
                    st.divider()
                    st.markdown("**\u5177\u9ad4\u5316\u89e3\u6cd5\uff1a**")
                else:
                    st.markdown(f"**Donation Items**\uff1a{PLANET_DONATIONS.get(p.name, '')}")
                    st.markdown(f"**Feed Animals**\uff1a{PLANET_FEED_ANIMALS.get(p.name, '')}")
                    st.markdown(f"**Auspicious Colour**\uff1a{PLANET_ASSOC_COLORS.get(p.name, '')}")
                    st.divider()
                    st.markdown("**Specific Remedies:**")
                for i, remedy in enumerate(remedies, 1):
                    st.markdown(
                        f'<div class="lk-upay-item">\U0001f538 {i}. {remedy}</div>',
                        unsafe_allow_html=True,
                    )

    # ── Tab 4: Life Summary ────────────────────────────────────
    with tab_summary:
        if lang in ("zh", "zh_cn"):
            st.markdown("#### \u2728 \u547d\u5c40\u7e3d\u7d50")
        else:
            st.markdown("#### \u2728 Life Summary")

        summary = _compute_summary(chart, lang)

        if lang in ("zh", "zh_cn"):
            st.markdown('<div class="lk-section-title">\u2605 \u5f37\u52e2\u884c\u661f\u8207\u5409\u7965\u5bae\u4f4d</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="lk-section-title">\u2605 Strengths &amp; Auspicious Placements</div>', unsafe_allow_html=True)

        for line in summary["strengths"].split("\n"):
            if line.strip():
                st.markdown(f'<div class="lk-strength-item">{line}</div>', unsafe_allow_html=True)

        if lang in ("zh", "zh_cn"):
            st.markdown('<div class="lk-section-title">\u26a0 \u9700\u8981\u95dc\u6ce8\u7684\u884c\u661f</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="lk-section-title">\u26a0 Areas Needing Attention</div>', unsafe_allow_html=True)

        for line in summary["weaknesses"].split("\n"):
            if line.strip():
                st.markdown(f'<div class="lk-weakness-item">{line}</div>', unsafe_allow_html=True)

        if lang in ("zh", "zh_cn"):
            st.markdown('<div class="lk-section-title">\U0001f31f \u4eba\u751f\u4e3b\u984c</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="lk-section-title">\U0001f31f Life Themes</div>', unsafe_allow_html=True)

        for line in summary["themes"].split("\n"):
            if line.strip():
                st.info(line)

        # Dharmi planets
        trines = [p for p in chart.planets if p.house in [1, 5, 9]]
        if trines:
            pnames = ", ".join(f"{p.glyph}{p.name}" for p in trines)
            if lang in ("zh", "zh_cn"):
                st.markdown(f"**\U0001f549\ufe0f \u4e09\u65b9\u5bae\uff081/5/9\uff09\u884c\u661f**\uff1a{pnames}")
                st.caption("\u4e09\u65b9\u5bea\u884c\u661f\u88ab\u8996\u70ba\u300c\u6cd5\u6027\u884c\u661f\uff08Dharmi Grahas\uff09\u300d\uff0c\u5e36\u4f86\u7cbe\u795e\u529b\u91cf\u8207\u5584\u696d\u5eb87\u8b77\u3002")
            else:
                st.markdown(f"**\U0001f549\ufe0f Trine Houses (1/5/9) Planets**: {pnames}")
                st.caption("Planets in trines are 'Dharmi Grahas' \u2014 they bring spiritual strength and meritorious protection.")

        upachaya = [p for p in chart.planets if p.house in [2, 6, 10]]
        if upachaya:
            pnames2 = ", ".join(f"{p.glyph}{p.name}" for p in upachaya)
            if lang in ("zh", "zh_cn"):
                st.markdown(f"**\U0001f4bc \u6210\u9577\u5bea\uff082/6/10\uff09\u884c\u661f**\uff1a{pnames2}")
                st.caption("\u6210\u9577\u5bea\u884c\u661f\u5f37\u5316\u7269\u8cea\u6210\u5c31\u3001\u8077\u696d\u8207\u5065\u5eb7\u3002")
            else:
                st.markdown(f"**\U0001f4bc Upachaya Houses (2/6/10) Planets**: {pnames2}")
                st.caption("Planets in Upachaya houses strengthen material achievements, career and health.")

    # ── Tab 5: 1952 Edition ───────────────────────────────────
    with tab_1952:
        _render_1952_tab(chart, lang)

    if after_chart_hook:
        after_chart_hook()


def _render_1952_tab(chart: "LalKitabChart", lang: str = "zh") -> None:
    """Render the Lal Kitab 1952 expanded edition tab."""
    import datetime as _dt

    planets_in_house = {p.name: p.house for p in chart.planets}
    birth_date = _dt.date(chart.year, chart.month, chart.day)

    # derive weekday string
    _weekday_map = {
        0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
        4: "Friday", 5: "Saturday", 6: "Sunday",
    }
    birth_weekday = _weekday_map[birth_date.weekday()]

    if lang in ("zh", "zh_cn"):
        st.markdown("#### \U0001f4d6 Lal Kitab 1952 年版完整分析")
        st.caption(
            "基於 Lal Kitab 1952 年最終版（Pt. Roop Chand Joshi）提煉，"
            "涵蓋完整宮位解釋、盲星判定、吉方位、三十五年週期、"
            "房屋顏色補救、手相壽命及 Farman 規則引擎。"
        )
    else:
        st.markdown("#### \U0001f4d6 Lal Kitab 1952 Edition — Complete Analysis")
        st.caption(
            "Extracted from the Lal Kitab 1952 Final Edition (Pt. Roop Chand Joshi). "
            "Includes full house interpretations, blind-planet status, auspicious directions, "
            "35-year cycle, house colour remedies, palmistry longevity and Farman engine."
        )

    # ── Section A: Full house interpretations + blind status ──
    if lang in ("zh", "zh_cn"):
        st.markdown("##### \U0001fa90 完整宮位解釋（1952年版）與盲星狀態")
    else:
        st.markdown("##### \U0001fa90 Full House Interpretations (1952) & Blind-Planet Status")

    for p in chart.planets:
        interp = PLANET_IN_HOUSE_FULL.get(p.name, {}).get(p.house, "")
        blind = is_blind_planet(p.name, p.house)
        if lang in ("zh", "zh_cn"):
            label = f"{p.glyph} {p.name_zh} — 第{p.house}宮 | {blind}"
        else:
            label = f"{p.glyph} {p.name_zh} — House {p.house} | {blind}"
        with st.expander(label, expanded=False):
            if interp:
                st.markdown(f"\U0001f4d6 {interp}")
            color_info = HOUSE_COLOR_RULES.get(p.house, {})
            if color_info:
                if lang in ("zh", "zh_cn"):
                    st.markdown(
                        f"**房屋顏色**：推薦 {color_info.get('recommended','')} "
                        f"| 避免 {color_info.get('avoid','')} "
                        f"| 備注：{color_info.get('note','')}"
                    )
                else:
                    st.markdown(
                        f"**House Colour**: Recommended {color_info.get('recommended','')} "
                        f"| Avoid {color_info.get('avoid','')} "
                        f"| Note: {color_info.get('note','')}"
                    )

    # ── Section B: Auspicious directions ──────────────────────
    st.divider()
    day_dir, hour_dir = get_auspicious_direction(birth_weekday, chart.hour)
    if lang in ("zh", "zh_cn"):
        st.markdown(f"##### \U0001f9ed 出生日時吉利方位")
        st.markdown(
            f"- **出生星期**：{birth_weekday} → 吉方位：**{day_dir}**\n"
            f"- **出生時辰**：{chart.hour:02d}:00 → 吉方位：**{hour_dir}**"
        )
    else:
        st.markdown("##### \U0001f9ed Auspicious Birth Directions")
        st.markdown(
            f"- **Birth Weekday**: {birth_weekday} → Direction: **{day_dir}**\n"
            f"- **Birth Hour**: {chart.hour:02d}:00 → Direction: **{hour_dir}**"
        )

    # ── Section C: 35-year cycle ───────────────────────────────
    st.divider()
    if lang in ("zh", "zh_cn"):
        st.markdown("##### \U0001f501 三十五年週期（35-Year Cycle）")
        st.caption("每個行星主運的吉凶狀態及建議補救，基於宮位判定。")
    else:
        st.markdown("##### \U0001f501 35-Year Planetary Cycle")
        st.caption("Auspicious/inauspicious status and remedies for each planetary period.")

    cycle_data = calculate_35_year_cycle(birth_date, planets_in_house)
    # Show only the first 35-year cycle (keys starting with "週期1")
    rows_35 = []
    for period_key, info in cycle_data.items():
        if not period_key.startswith("週期1"):
            continue
        if lang in ("zh", "zh_cn"):
            rows_35.append({
                "週期/年齡": period_key,
                "行星": info["planet_zh"],
                "年數": info["years"],
                "宮位": info["house"],
                "狀態": info["status"],
                "補救": info["remedy"],
            })
        else:
            rows_35.append({
                "Period/Age": period_key,
                "Planet": info["planet_zh"],
                "Years": info["years"],
                "House": info["house"],
                "Status": info["status"],
                "Remedy": info["remedy"],
            })
    if rows_35:
        st.dataframe(pd.DataFrame(rows_35), hide_index=True, width="stretch")

    # ── Section D: House colour remedies ──────────────────────
    st.divider()
    if lang in ("zh", "zh_cn"):
        st.markdown("##### \U0001f3e0 房屋顏色補救一覽")
    else:
        st.markdown("##### \U0001f3e0 House Colour Remedies")

    color_rows = []
    for house_num, remedies_list in HOUSE_COLOR_REMEDIES.items():
        if lang in ("zh", "zh_cn"):
            color_rows.append({"宮位": house_num, "補救建議": "；".join(remedies_list)})
        else:
            color_rows.append({"House": house_num, "Remedies": "; ".join(remedies_list)})
    st.dataframe(pd.DataFrame(color_rows), hide_index=True, width="stretch")

    # ── Section E: Farman Engine ───────────────────────────────
    st.divider()
    if lang in ("zh", "zh_cn"):
        st.markdown("##### \U0001f4dc Farman 規則引擎")
        st.caption("根據行星宮位自動匹配1952年版Farman規則。")
    else:
        st.markdown("##### \U0001f4dc Farman Rule Engine")
        st.caption("Auto-matches 1952 Farman rules based on planetary house placements.")

    farman_results = FarmanRuleEngine.get_all_house_farmans(planets_in_house)
    for planet_name, fdata in farman_results.items():
        pobj = next((p for p in chart.planets if p.name == planet_name), None)
        glyph = pobj.glyph if pobj else ""
        zh_name = pobj.name_zh if pobj else planet_name
        house_n = planets_in_house.get(planet_name, "?")
        if lang in ("zh", "zh_cn"):
            flabel = f"{glyph} {zh_name} — 第{house_n}宮"
        else:
            flabel = f"{glyph} {zh_name} — House {house_n}"
        with st.expander(flabel, expanded=False):
            for fm in fdata.get("matched_farmans", []):
                if lang in ("zh", "zh_cn"):
                    st.markdown(f"**Farman {fm['farman_number']}**：{fm['rule']}")
                    st.markdown(f"補救：{', '.join(fm['remedy']) if isinstance(fm['remedy'], list) else fm['remedy']}")
                    st.caption(f"備注：{fm.get('note', '')}")
                else:
                    st.markdown(f"**Farman {fm['farman_number']}**: {fm['rule']}")
                    st.markdown(f"Remedy: {', '.join(fm['remedy']) if isinstance(fm['remedy'], list) else fm['remedy']}")
                    st.caption(f"Note: {fm.get('note', '')}")

    # ── Section F: General remedies ───────────────────────────
    st.divider()
    if lang in ("zh", "zh_cn"):
        st.markdown("##### \U0001f538 通用補救建議")
        for r in GENERAL_REMEDIES:
            st.markdown(f'<div class="lk-upay-item">\U0001f538 {r}</div>', unsafe_allow_html=True)
    else:
        st.markdown("##### \U0001f538 General Remedies")
        for r in GENERAL_REMEDIES:
            st.markdown(f'<div class="lk-upay-item">\U0001f538 {r}</div>', unsafe_allow_html=True)


# ============================================================
# Lal Kitab 1952 Full Page Renderer (7 tabs)
# ============================================================

def _generate_pdf_text(chart: "LalKitabChart", lang: str = "zh") -> str:
    """Generate a plain-text report suitable for download as a PDF stand-in."""
    import datetime as _dt

    planets_in_house = {p.name: p.house for p in chart.planets}
    birth_date = _dt.date(chart.year, chart.month, chart.day)
    weekday_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
                   4: "Friday", 5: "Saturday", 6: "Sunday"}
    weekday = weekday_map[birth_date.weekday()]
    day_dir, hour_dir = get_auspicious_direction(weekday, chart.hour)

    lines = [
        "=" * 60,
        "  लाल किताब · Lal Kitab 1952 · 紅皮書命盤報告",
        "=" * 60,
        f"出生日期：{chart.year}/{chart.month:02d}/{chart.day:02d}",
        f"出生時間：{chart.hour:02d}:{chart.minute:02d} UTC{chart.timezone:+.1f}",
        f"地點：{chart.location_name or 'N/A'}",
        f"歲差（Ayanamsa）：{chart.ayanamsa:.4f}°",
        f"出生上升：{chart.lagna_sign}（第{chart.lagna_house}宮）",
        "",
        "── 行星宮位 ──",
    ]
    for p in chart.planets:
        pk = " ★本位" if p.in_pakka_ghar else ""
        rt = " ℞逆行" if p.retrograde and p.name not in ("Rahu", "Ketu") else ""
        lines.append(f"  {p.name_zh}：第{p.house}宮 {p.sign_zh}{pk}{rt}")

    lines += ["", "── 行星宮位完整解釋（1952年版）──"]
    for p in chart.planets:
        interp = PLANET_IN_HOUSE_FULL.get(p.name, {}).get(p.house, "")
        if interp:
            lines.append(f"\n{p.name_zh}（第{p.house}宮）：{interp}")

    lines += ["", "── 吉利方位 ──",
              f"  出生星期 {weekday} → {day_dir}",
              f"  出生時辰 {chart.hour:02d}:00 → {hour_dir}"]

    cycle = calculate_35_year_cycle(birth_date, planets_in_house)
    lines += ["", "── 三十五年週期（第一循環）──"]
    for k, v in cycle.items():
        if k.startswith("週期1"):
            lines.append(f"  {k}：{v['planet_zh']} {v['years']}年 第{v['house']}宮 {v['status']}")

    lines += ["", "── 房屋顏色建議 ──"]
    for h, rule in HOUSE_COLOR_RULES.items():
        lines.append(f"  第{h}宮：推薦 {rule['recommended']} | 避免 {rule['avoid']}")

    lines += ["", "=" * 60, "  報告由 KinAstro (kinastro.streamlit.app) 自動生成", "=" * 60]
    return "\n".join(lines)


def render_lal_kitab_1952_page(
    chart: "LalKitabChart",
    lang: str = "zh",
    after_chart_hook=None,
) -> None:
    """Render the comprehensive Lal Kitab 1952 7-tab page.

    Tabs:
        1. 【星盤總覽】 — SVG chart + planet table + birth info
        2. 【宮位解釋】 — PLANET_IN_HOUSE_FULL interpretations + blind status
        3. 【補救措施】 — get_complete_remedies() Upay display
        4. 【35年大運】 — calculate_35_year_cycle() with metrics
        5. 【手相壽命】 — interactive PalmistryLongevityCalculator form
        6. 【Farman 法則】 — FarmanRuleEngine matched rules
        7. 【房屋顏色與方位】 — HOUSE_COLOR_RULES + get_auspicious_direction()
    """
    import datetime as _dt

    st.markdown(_LK_CSS, unsafe_allow_html=True)

    planets_in_house: Dict[str, int] = {p.name: p.house for p in chart.planets}
    try:
        birth_date = _dt.date(chart.year, chart.month, chart.day)
    except ValueError:
        birth_date = _dt.date.today()
    weekday_map = {
        0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
        4: "Friday", 5: "Saturday", 6: "Sunday",
    }
    birth_weekday = weekday_map[birth_date.weekday()]

    # ── Title banner ──────────────────────────────────────────
    if lang in ("zh", "zh_cn"):
        title = "लाल किताब · 拉爾基塔布 1952 · 紅皮書完整命盤"
        subtitle = "Lal Kitab 1952 Final Edition · Pt. Roop Chand Joshi · 卡爾普拉什固定宮位系統"
    else:
        title = "लाल किताब · Lal Kitab 1952 Complete Chart"
        subtitle = "Lal Kitab 1952 Final Edition · Pt. Roop Chand Joshi · Kal Purush Fixed House System"

    st.markdown(
        f'<div class="lk-title-banner">'
        f'<div class="lk-title">{title}</div>'
        f'<div class="lk-subtitle">{subtitle}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── PDF download button ───────────────────────────────────
    pdf_text = _generate_pdf_text(chart, lang)
    col_dl, col_sp = st.columns([1, 3])
    with col_dl:
        st.download_button(
            label="📄 一鍵下載報告 (TXT)" if lang in ("zh", "zh_cn") else "📄 Download Report (TXT)",
            data=pdf_text.encode("utf-8"),
            file_name=f"lal_kitab_1952_{chart.year}{chart.month:02d}{chart.day:02d}.txt",
            mime="text/plain",
        )

    # ── 7 Tabs ────────────────────────────────────────────────
    if lang in ("zh", "zh_cn"):
        tab_labels = [
            "🌟 星盤總覽",
            "🔮 宮位解釋",
            "🔴 補救措施",
            "🔄 35年大運",
            "✋ 手相壽命",
            "📜 Farman 法則",
            "🏠 房屋顏色與方位",
        ]
    else:
        tab_labels = [
            "🌟 Chart Overview",
            "🔮 House Interpretations",
            "🔴 Remedies (Upay)",
            "🔄 35-Year Cycle",
            "✋ Palmistry Longevity",
            "📜 Farman Rules",
            "🏠 House Colours & Directions",
        ]

    (
        tab_overview,
        tab_interp,
        tab_remedies,
        tab_cycle,
        tab_palm,
        tab_farman,
        tab_house,
    ) = st.tabs(tab_labels)

    # ──────────────────────────────────────────────────────────
    # Tab 1: 星盤總覽
    # ──────────────────────────────────────────────────────────
    with tab_overview:
        col_svg, col_info = st.columns([1, 1])

        with col_svg:
            svg = _build_lal_kitab_svg(chart, width=480)
            st.markdown(
                f'<div style="display:flex;justify-content:center;margin:8px 0;">{svg}</div>',
                unsafe_allow_html=True,
            )
            if lang in ("zh", "zh_cn"):
                st.caption("★ = Pakka Ghar 本位　℞ = 逆行　顏色對應各行星能量")
            else:
                st.caption("★ = Pakka Ghar (permanent house)　℞ = Retrograde")

        with col_info:
            if lang in ("zh", "zh_cn"):
                st.markdown("**📐 基本資訊**")
                st.markdown(
                    f"- **歲差（Ayanamsa）**：{chart.ayanamsa:.4f}°\n"
                    f"- **出生上升**：{chart.lagna_sign}（第{chart.lagna_house}宮）\n"
                    f"- **出生日期**：{chart.year}/{chart.month:02d}/{chart.day:02d}\n"
                    f"- **出生時間**：{chart.hour:02d}:{chart.minute:02d} UTC{chart.timezone:+.1f}\n"
                    f"- **地點**：{chart.location_name or 'N/A'}"
                )
                st.divider()
                st.markdown("**📖 拉爾基塔布系統說明**")
                st.info(
                    "拉爾基塔布使用**卡爾普拉什固定宮位**：白羊座永遠是第一宮，"
                    "無論上升星座。每顆行星所在**星座**即決定其**宮位**。\n\n"
                    "⭐ **Pakka Ghar（本位）**：行星在其永久本宮時，力量最強，影響最大。\n\n"
                    "🔵 **盲星**：羅睺/計都永遠是盲星。土星/火星在角宮為半盲星。"
                )
            else:
                st.markdown("**📐 Chart Information**")
                st.markdown(
                    f"- **Ayanamsa**：{chart.ayanamsa:.4f}°\n"
                    f"- **Natal Lagna**：{chart.lagna_sign} (House {chart.lagna_house})\n"
                    f"- **Date**：{chart.year}/{chart.month:02d}/{chart.day:02d}\n"
                    f"- **Time**：{chart.hour:02d}:{chart.minute:02d} UTC{chart.timezone:+.1f}\n"
                    f"- **Location**：{chart.location_name or 'N/A'}"
                )
                st.divider()
                st.markdown("**📖 About Lal Kitab**")
                st.info(
                    "Lal Kitab uses the **Kal Purush fixed house** system: Aries is always House 1, "
                    "regardless of Lagna. Each planet's **sign** determines its house number.\n\n"
                    "⭐ **Pakka Ghar**: Planet in its permanent house has maximum strength.\n\n"
                    "🔵 **Blind planets**: Rahu/Ketu are always blind. Saturn/Mars in angular houses are semi-blind."
                )

        # Planet metrics row
        st.divider()
        if lang in ("zh", "zh_cn"):
            st.markdown("#### 🪐 行星位置一覽")
        else:
            st.markdown("#### 🪐 Planetary Positions")

        metric_cols = st.columns(len(chart.planets))
        for col, p in zip(metric_cols, chart.planets):
            with col:
                deg = int(p.sign_degree)
                arc_minutes = int((p.sign_degree - deg) * 60)
                retro = " ℞" if p.retrograde and p.name not in ("Rahu", "Ketu") else ""
                pk = " ★" if p.in_pakka_ghar else ""
                st.metric(
                    label=f"{p.glyph} {PLANET_ZH_SHORT.get(p.name, p.name[0])}",
                    value=f"第{p.house}宮" if lang in ("zh", "zh_cn") else f"H{p.house}",
                    delta=f"{p.sign_zh}{retro}{pk}" if lang in ("zh", "zh_cn") else f"{p.sign}{retro}{pk}",
                )

        # Detailed table
        rows = []
        for p in chart.planets:
            deg = int(p.sign_degree)
            arc_minutes = int((p.sign_degree - deg) * 60)
            retro_str = "℞" if p.retrograde and p.name not in ("Rahu", "Ketu") else ""
            pakka_str = "★ 本位" if p.in_pakka_ghar else ""
            blind = is_blind_planet(p.name, p.house)
            if lang in ("zh", "zh_cn"):
                rows.append({
                    "行星": f"{p.glyph} {p.name_zh}",
                    "宮位": p.house,
                    "星座": f"{p.sign_glyph} {p.sign_zh}",
                    "宮內度數": f"{deg}°{arc_minutes:02d}'",
                    "逆行": retro_str,
                    "本位": pakka_str,
                    "盲星狀態": blind,
                })
            else:
                rows.append({
                    "Planet": f"{p.glyph} {p.name_zh}",
                    "House": p.house,
                    "Sign": f"{p.sign_glyph} {p.sign}",
                    "Degree": f"{deg}°{arc_minutes:02d}'",
                    "Retro": retro_str,
                    "Pakka": pakka_str,
                    "Blind Status": blind,
                })
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

        if after_chart_hook:
            after_chart_hook()

    # ──────────────────────────────────────────────────────────
    # Tab 2: 宮位解釋
    # ──────────────────────────────────────────────────────────
    with tab_interp:
        if lang in ("zh", "zh_cn"):
            st.markdown("#### 🔮 行星宮位完整解釋（1952年版）")
            st.caption("使用 PLANET_IN_HOUSE_FULL 字典，1952年版原典詳細果報（吉凶、財富、婚姻、健康）。")
        else:
            st.markdown("#### 🔮 Planet-in-House Full Interpretations (1952 Edition)")
            st.caption("From PLANET_IN_HOUSE_FULL — detailed karmic outcomes per planet/house (1952 Final Edition).")

        for p in chart.planets:
            interp = PLANET_IN_HOUSE_FULL.get(p.name, {}).get(p.house, "")
            blind = is_blind_planet(p.name, p.house)
            if lang in ("zh", "zh_cn"):
                pk_note = "（★ 本位加成）" if p.in_pakka_ghar else ""
                rt_note = "（℞ 逆行）" if p.retrograde and p.name not in ("Rahu", "Ketu") else ""
                label = f"{p.glyph} {p.name_zh} — 第{p.house}宮 {p.sign_glyph}{p.sign_zh} {pk_note}{rt_note} | {blind}"
            else:
                pk_note = " (★ Pakka Ghar)" if p.in_pakka_ghar else ""
                rt_note = " (℞ Retrograde)" if p.retrograde and p.name not in ("Rahu", "Ketu") else ""
                label = f"{p.glyph} {p.name_zh} — House {p.house} {p.sign_glyph}{p.sign} {pk_note}{rt_note} | {blind}"

            with st.expander(label, expanded=False):
                if interp:
                    st.markdown(f"📖 {interp}")
                else:
                    st.info("此宮位解釋待補充。" if lang in ("zh", "zh_cn") else "Interpretation not available.")

                if p.in_pakka_ghar:
                    if lang in ("zh", "zh_cn"):
                        st.success(f"✨ 此行星位於其永久本宮（Pakka Ghar：{p.pakka_ghar}），力量最強！")
                    else:
                        st.success(f"✨ Planet is in Pakka Ghar (Permanent House {p.pakka_ghar}) — maximum strength!")

                if p.retrograde and p.name not in ("Rahu", "Ketu"):
                    if lang in ("zh", "zh_cn"):
                        st.warning("⚠️ 此行星逆行，相關事務需加倍努力或進行特殊消解儀式。")
                    else:
                        st.warning("⚠️ This planet is retrograde — related matters need extra effort or specific rituals.")

                color_info = HOUSE_COLOR_RULES.get(p.house, {})
                if color_info and lang in ("zh", "zh_cn"):
                    st.markdown(
                        f"**🏠 房屋顏色提示**：推薦 {color_info.get('recommended','')} "
                        f"| 避免 {color_info.get('avoid','')} "
                        f"| {color_info.get('note','')}"
                    )
                elif color_info:
                    st.markdown(
                        f"**🏠 House Colour Tip**: Recommended {color_info.get('recommended','')} "
                        f"| Avoid {color_info.get('avoid','')} "
                        f"| {color_info.get('note','')}"
                    )

    # ──────────────────────────────────────────────────────────
    # Tab 3: 補救措施
    # ──────────────────────────────────────────────────────────
    with tab_remedies:
        if lang in ("zh", "zh_cn"):
            st.markdown("#### 🔴 專屬 Upay 補救措施（完整版）")
            st.caption(
                "使用 get_complete_remedies() 函式，顯示每顆行星在其宮位的具體 Upay，"
                "含行星特定補救、房屋顏色、捐贈物品、餵食動物等。"
            )
        else:
            st.markdown("#### 🔴 Complete Upay Remedies")
            st.caption(
                "From get_complete_remedies() — planet+house specific Upay, house colour remedies, "
                "donations, and animal offerings."
            )

        all_remedies = get_complete_remedies(planets_in_house)

        # General remedies
        if lang in ("zh", "zh_cn"):
            with st.expander("🌐 通用補救建議（適用所有人）", expanded=True):
                for r in all_remedies.get("general", []):
                    st.markdown(f'<div class="lk-upay-item">🔸 {r}</div>', unsafe_allow_html=True)
        else:
            with st.expander("🌐 General Remedies (For Everyone)", expanded=True):
                for r in all_remedies.get("general", []):
                    st.markdown(f'<div class="lk-upay-item">🔸 {r}</div>', unsafe_allow_html=True)

        st.divider()

        # Per-planet remedies
        for p in chart.planets:
            planet_data = all_remedies.get(p.name, {})
            specific = planet_data.get("specific_remedies", [])
            house_col = planet_data.get("house_color", [])
            day_str = PLANET_DAYS.get(p.name, "")
            if lang in ("zh", "zh_cn"):
                label = f"{p.glyph} {p.name_zh} — 第{p.house}宮 · 化解日：{day_str}"
            else:
                label = f"{p.glyph} {p.name_zh} — House {p.house} · Remedy Day: {day_str}"

            with st.expander(label, expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    if lang in ("zh", "zh_cn"):
                        st.markdown(f"**捐贈物品**：{PLANET_DONATIONS.get(p.name, '')}")
                        st.markdown(f"**餵食動物**：{PLANET_FEED_ANIMALS.get(p.name, '')}")
                        st.markdown(f"**吉祥顏色**：{PLANET_ASSOC_COLORS.get(p.name, '')}")
                    else:
                        st.markdown(f"**Donation Items**：{PLANET_DONATIONS.get(p.name, '')}")
                        st.markdown(f"**Feed Animals**：{PLANET_FEED_ANIMALS.get(p.name, '')}")
                        st.markdown(f"**Auspicious Colour**：{PLANET_ASSOC_COLORS.get(p.name, '')}")

                with c2:
                    if lang in ("zh", "zh_cn"):
                        st.markdown(f"**房屋顏色補救**：{'；'.join(house_col)}")
                    else:
                        st.markdown(f"**House Colour Remedy**：{'; '.join(house_col)}")

                st.divider()
                if lang in ("zh", "zh_cn"):
                    st.markdown("**具體化解法（1952年版）：**")
                else:
                    st.markdown("**Specific Remedies (1952 Edition):**")

                for i, remedy in enumerate(specific, 1):
                    st.markdown(
                        f'<div class="lk-upay-item">🔸 {i}. {remedy}</div>',
                        unsafe_allow_html=True,
                    )

    # ──────────────────────────────────────────────────────────
    # Tab 4: 35年大運
    # ──────────────────────────────────────────────────────────
    with tab_cycle:
        if lang in ("zh", "zh_cn"):
            st.markdown("#### 🔄 三十五年週期大運（35-Year Planetary Cycle）")
            st.caption(
                "拉爾基塔布1952年版獨有的三十五年週期，以9顆行星循環計算，"
                "每個行星主運的吉凶狀態取決於其所在宮位。"
            )
        else:
            st.markdown("#### 🔄 35-Year Planetary Cycle (Lal Kitab 1952)")
            st.caption(
                "Unique to the 1952 Final Edition — nine planets in a 35-year repeating cycle. "
                "Auspiciousness depends on each planet's house placement."
            )

        cycle_data = calculate_35_year_cycle(birth_date, planets_in_house)

        # Current age to highlight active period
        today = _dt.date.today()
        current_age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

        if lang in ("zh", "zh_cn"):
            st.metric("🎂 目前年齡", f"{current_age} 歲")
        else:
            st.metric("🎂 Current Age", f"{current_age} years")

        st.divider()

        for cycle_num in range(1, 4):
            cycle_prefix = f"週期{cycle_num}"
            if lang in ("zh", "zh_cn"):
                st.markdown(f"##### 第 {cycle_num} 輪 35 年週期")
            else:
                st.markdown(f"##### Cycle {cycle_num} of 35 Years")

            rows_35: List[Dict] = []
            is_active_cycle = False
            cumulative_age = 0
            for period_key, info in cycle_data.items():
                if not period_key.startswith(cycle_prefix):
                    continue
                # Derive age range from cumulative tracking (robust, not string-parsing)
                age_start = cumulative_age
                age_end = cumulative_age + info["years"]
                cumulative_age = age_end
                is_active = age_start <= current_age < age_end
                if is_active:
                    is_active_cycle = True

                auspicious = "🟢 吉" if info["house"] in {1, 4, 5, 9, 10, 11} else "🔴 需補救"
                if lang in ("zh", "zh_cn"):
                    rows_35.append({
                        "週期/年齡": f"{'▶ ' if is_active else ''}{period_key}",
                        "行星": info["planet_zh"],
                        "年數": info["years"],
                        "宮位": info["house"],
                        "狀態": auspicious + " " + info["status"],
                        "補救": info["remedy"],
                    })
                else:
                    status_en = "🟢 Prosperous" if info["house"] in {1, 4, 5, 9, 10, 11} else "🔴 Needs Remedy"
                    rows_35.append({
                        "Period/Age": f"{'▶ ' if is_active else ''}{period_key}",
                        "Planet": info["planet_zh"],
                        "Years": info["years"],
                        "House": info["house"],
                        "Status": status_en,
                        "Remedy": info["remedy"],
                    })

            if rows_35:
                if is_active_cycle:
                    st.info("▶ 目前正在此週期中！" if lang in ("zh", "zh_cn") else "▶ Currently in this cycle!")
                st.dataframe(pd.DataFrame(rows_35), hide_index=True, width="stretch")

    # ──────────────────────────────────────────────────────────
    # Tab 5: 手相壽命
    # ──────────────────────────────────────────────────────────
    with tab_palm:
        if lang in ("zh", "zh_cn"):
            st.markdown("#### ✋ 手相壽命計算器（1952年版第1161-1167頁）")
            st.caption(
                "根據拉爾基塔布1952年版手相篇，輸入生命線長度描述、心臟線交叉年齡、"
                "主要掌紋數量，即時計算預估壽命與死亡徵兆警告。"
            )
        else:
            st.markdown("#### ✋ Palmistry Longevity Calculator (1952 Edition, pp.1161-1167)")
            st.caption(
                "Based on the palmistry chapter of Lal Kitab 1952. Enter life line description, "
                "heart line crossing age and major lines count to estimate longevity."
            )

        with st.container():
            col_a, col_b, col_c = st.columns(3)

            life_line_options = list(PalmistryLongevityCalculator.LIFE_LINE_AGES.keys())
            with col_a:
                if lang in ("zh", "zh_cn"):
                    life_line_sel = st.selectbox(
                        "🖐 生命線長度描述",
                        options=life_line_options,
                        index=life_line_options.index("生命線末端"),
                        help="根據手掌上的生命線終止位置選擇",
                    )
                    total_lines = st.number_input(
                        "📊 主要掌紋數量（1-4）",
                        min_value=1, max_value=4, value=3, step=1,
                        help="手掌上的主要掌紋總數（生命線、感情線、智慧線、事業線）",
                    )
                else:
                    life_line_sel = st.selectbox(
                        "🖐 Life Line Description",
                        options=life_line_options,
                        index=life_line_options.index("生命線末端"),
                        help="Select based on where the life line ends on the palm",
                    )
                    total_lines = st.number_input(
                        "📊 Major Lines Count (1-4)",
                        min_value=1, max_value=4, value=3, step=1,
                        help="Total major palm lines (life, heart, head, fate)",
                    )

            heart_crossing_options = [None, 35, 45, 56]
            heart_label_map = {
                None: "無交叉" if lang in ("zh", "zh_cn") else "No crossing",
                35: "35歲（農業線×心臟線）" if lang in ("zh", "zh_cn") else "Age 35 (field × heart)",
                45: "45歲（生命線×心臟線）" if lang in ("zh", "zh_cn") else "Age 45 (life × heart)",
                56: "56歲（農業線×心臟線）" if lang in ("zh", "zh_cn") else "Age 56 (field × heart)",
            }
            with col_b:
                if lang in ("zh", "zh_cn"):
                    heart_sel_label = st.selectbox(
                        "💓 心臟線交叉年齡",
                        options=list(heart_label_map.values()),
                        index=0,
                        help="心臟線與其他掌紋的交叉年齡（第1166頁）",
                    )
                else:
                    heart_sel_label = st.selectbox(
                        "💓 Heart Line Crossing Age",
                        options=list(heart_label_map.values()),
                        index=0,
                        help="Age at which heart line crosses another line (p.1166)",
                    )
                heart_sel = next(
                    (k for k, v in heart_label_map.items() if v == heart_sel_label), None
                )

            warning_options = list(PalmistryLongevityCalculator.DEATH_WARNINGS.keys())
            with col_c:
                if lang in ("zh", "zh_cn"):
                    selected_warnings = st.multiselect(
                        "⚠️ 特殊死亡徵兆（可多選）",
                        options=warning_options,
                        default=[],
                        help="選擇手掌上出現的特殊徵兆（第1166-1167頁）",
                    )
                else:
                    selected_warnings = st.multiselect(
                        "⚠️ Special Death Omens (optional)",
                        options=warning_options,
                        default=[],
                        help="Select special signs on the palm (pp.1166-1167)",
                    )

        result = PalmistryLongevityCalculator.calculate_longevity(
            life_line_desc=life_line_sel,
            heart_line_cross_year=heart_sel,
            total_major_lines=total_lines,
            special_warnings=selected_warnings if selected_warnings else None,
        )

        st.divider()

        res_c1, res_c2, res_c3 = st.columns(3)
        with res_c1:
            if lang in ("zh", "zh_cn"):
                st.metric("🕯️ 預估壽命", result["estimated_longevity"], delta=f"信心：{result['confidence']}")
            else:
                est = result["estimated_longevity"]
                st.metric("🕯️ Estimated Longevity", est, delta=f"Confidence: {result['confidence']}")
        with res_c2:
            if lang in ("zh", "zh_cn"):
                st.metric("🖐 生命線", result["base_life_line"])
            else:
                st.metric("🖐 Life Line", result["base_life_line"])
        with res_c3:
            if lang in ("zh", "zh_cn"):
                st.metric("📊 掌紋數量加成", f"{total_lines} 條")
            else:
                st.metric("📊 Lines Bonus", f"{total_lines} lines")

        warnings = result.get("heart_line_warning", [])
        if warnings:
            for w in warnings:
                st.warning(f"⚠️ {w}")

        if lang in ("zh", "zh_cn"):
            st.info(f"💊 補救建議：{result.get('remedy_suggestion', '')}")
            with st.expander("📋 完整死亡徵兆對照表（1952年版）", expanded=False):
                for sign, meaning in PalmistryLongevityCalculator.DEATH_WARNINGS.items():
                    st.markdown(f"- **{sign}**：{meaning}")
            with st.expander("📋 心臟線交叉年齡說明（1952年版）", expanded=False):
                for age, desc in PalmistryLongevityCalculator.HEART_LINE_CROSSINGS.items():
                    st.markdown(f"- **{age}歲**：{desc}")
        else:
            st.info(f"💊 Remedy: {result.get('remedy_suggestion', '')}")
            with st.expander("📋 Full Death Omen Reference (1952 Edition)", expanded=False):
                for sign, meaning in PalmistryLongevityCalculator.DEATH_WARNINGS.items():
                    st.markdown(f"- **{sign}**: {meaning}")
            with st.expander("📋 Heart Line Crossing Ages (1952 Edition)", expanded=False):
                for age, desc in PalmistryLongevityCalculator.HEART_LINE_CROSSINGS.items():
                    st.markdown(f"- **Age {age}**: {desc}")

    # ──────────────────────────────────────────────────────────
    # Tab 6: Farman 法則
    # ──────────────────────────────────────────────────────────
    with tab_farman:
        if lang in ("zh", "zh_cn"):
            st.markdown("#### 📜 Farman 規則引擎（1952年版第7-12號法則）")
            st.caption(
                "使用 FarmanRuleEngine 自動匹配此命盤觸發的 Farman 法則（第7至12號），"
                "顯示每顆行星對應的具體 Farman 建議與補救。"
            )
        else:
            st.markdown("#### 📜 Farman Rule Engine (1952 Edition, Rules 7-12)")
            st.caption(
                "FarmanRuleEngine auto-matches Farman rules 7-12 triggered by this chart's "
                "planetary placements, showing specific advice and remedies."
            )

        # Show Farman rules reference table
        with st.expander(
            "📋 Farman 規則一覽表（7-12）" if lang in ("zh", "zh_cn") else "📋 Farman Rules Reference (7-12)",
            expanded=False,
        ):
            farman_rows = []
            for fnum, frule in FARMAN_RULES.items():
                if lang in ("zh", "zh_cn"):
                    farman_rows.append({
                        "法則編號": fnum,
                        "適用條件": frule["condition"],
                        "法則內容": frule["rule"],
                        "補救方法": "、".join(frule["remedy"]) if isinstance(frule["remedy"], list) else frule["remedy"],
                        "備注": frule.get("note", ""),
                    })
                else:
                    farman_rows.append({
                        "Farman #": fnum,
                        "Condition": frule["condition"],
                        "Rule": frule["rule"],
                        "Remedy": ", ".join(frule["remedy"]) if isinstance(frule["remedy"], list) else frule["remedy"],
                        "Note": frule.get("note", ""),
                    })
            if farman_rows:
                st.dataframe(pd.DataFrame(farman_rows), hide_index=True, width="stretch")

        st.divider()

        farman_results = FarmanRuleEngine.get_all_house_farmans(planets_in_house)
        for planet_name, fdata in farman_results.items():
            pobj = next((p for p in chart.planets if p.name == planet_name), None)
            glyph = pobj.glyph if pobj else ""
            zh_name = pobj.name_zh if pobj else planet_name
            house_n = planets_in_house.get(planet_name, "?")

            if lang in ("zh", "zh_cn"):
                flabel = f"{glyph} {zh_name} — 第{house_n}宮 · 匹配 {fdata.get('total_matches', 0)} 條 Farman"
            else:
                flabel = f"{glyph} {zh_name} — House {house_n} · {fdata.get('total_matches', 0)} Farman match(es)"

            with st.expander(flabel, expanded=False):
                for fm in fdata.get("matched_farmans", []):
                    if lang in ("zh", "zh_cn"):
                        st.markdown(f"**Farman {fm['farman_number']}**：{fm['rule']}")
                        remedy_text = (
                            "、".join(fm["remedy"])
                            if isinstance(fm["remedy"], list)
                            else fm["remedy"]
                        )
                        st.markdown(f"補救：{remedy_text}")
                        if fm.get("note"):
                            st.caption(f"備注：{fm['note']}")
                    else:
                        st.markdown(f"**Farman {fm['farman_number']}**: {fm['rule']}")
                        remedy_text = (
                            ", ".join(fm["remedy"])
                            if isinstance(fm["remedy"], list)
                            else fm["remedy"]
                        )
                        st.markdown(f"Remedy: {remedy_text}")
                        if fm.get("note"):
                            st.caption(f"Note: {fm['note']}")

        # Full integrated analysis summary
        st.divider()
        if lang in ("zh", "zh_cn"):
            with st.expander("🌟 一鍵完整報告（Farman + 手相整合分析）", expanded=False):
                full_report = get_palmistry_and_farman_analysis(planets_in_house)
                palm_data = full_report.get("palmistry_longevity", {})
                st.markdown(f"**手相預估壽命**：{palm_data.get('estimated_longevity', 'N/A')}")
                st.markdown(f"**信心程度**：{palm_data.get('confidence', 'N/A')}")
                st.markdown(f"**整合補救建議**：{full_report.get('combined_remedy', '')}")
        else:
            with st.expander("🌟 Integrated Report (Farman + Palmistry)", expanded=False):
                full_report = get_palmistry_and_farman_analysis(planets_in_house)
                palm_data = full_report.get("palmistry_longevity", {})
                st.markdown(f"**Estimated Longevity**: {palm_data.get('estimated_longevity', 'N/A')}")
                st.markdown(f"**Confidence**: {palm_data.get('confidence', 'N/A')}")
                st.markdown(f"**Combined Remedy**: {full_report.get('combined_remedy', '')}")

    # ──────────────────────────────────────────────────────────
    # Tab 7: 房屋顏色與方位
    # ──────────────────────────────────────────────────────────
    with tab_house:
        if lang in ("zh", "zh_cn"):
            st.markdown("#### 🏠 房屋顏色規則與出生吉利方位")
            st.caption("來自1952年版第11章，房屋顏色吉凶建議與出生日時吉利方位。")
        else:
            st.markdown("#### 🏠 House Colour Rules & Auspicious Directions")
            st.caption("From Chapter 11 of the 1952 Final Edition — house colour advice and birth direction guidance.")

        # Auspicious direction
        day_dir, hour_dir = get_auspicious_direction(birth_weekday, chart.hour)
        dir_c1, dir_c2, dir_c3 = st.columns(3)
        with dir_c1:
            if lang in ("zh", "zh_cn"):
                st.metric("📅 出生星期", birth_weekday)
            else:
                st.metric("📅 Birth Weekday", birth_weekday)
        with dir_c2:
            if lang in ("zh", "zh_cn"):
                st.metric("🧭 星期吉方位", day_dir)
            else:
                st.metric("🧭 Weekday Direction", day_dir)
        with dir_c3:
            if lang in ("zh", "zh_cn"):
                st.metric("🕐 時辰吉方位", hour_dir)
            else:
                st.metric("🕐 Birth Hour Direction", hour_dir)

        st.divider()

        # Full weekday/time direction tables
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if lang in ("zh", "zh_cn"):
                st.markdown("**📅 出生星期吉方位一覽**")
                wd_rows = [{"星期": k, "吉利方位": " / ".join(v)} for k, v in WEEKDAY_DIRECTIONS.items()]
            else:
                st.markdown("**📅 Weekday Auspicious Directions**")
                wd_rows = [{"Weekday": k, "Auspicious Directions": " / ".join(v)} for k, v in WEEKDAY_DIRECTIONS.items()]
            st.dataframe(pd.DataFrame(wd_rows), hide_index=True, width="stretch")

        with col_t2:
            if lang in ("zh", "zh_cn"):
                st.markdown("**🕐 時辰吉方位一覽**")
                td_rows = [{"時辰": k, "吉利方位": " / ".join(v)} for k, v in TIME_DIRECTIONS.items()]
            else:
                st.markdown("**🕐 Birth Hour Auspicious Directions**")
                td_rows = [{"Time Slot": k, "Auspicious Directions": " / ".join(v)} for k, v in TIME_DIRECTIONS.items()]
            st.dataframe(pd.DataFrame(td_rows), hide_index=True, width="stretch")

        st.divider()

        # House colour rules
        if lang in ("zh", "zh_cn"):
            st.markdown("**🎨 十二宮房屋顏色吉凶規則**")
        else:
            st.markdown("**🎨 12-House Colour Rules**")

        color_cols = st.columns(3)
        for i, (house_num, rule) in enumerate(HOUSE_COLOR_RULES.items()):
            col = color_cols[i % 3]
            with col:
                planets_here = [p.name_zh for p in chart.planets if p.house == house_num]
                planet_note = f"（{', '.join(planets_here)}）" if planets_here else ""
                if lang in ("zh", "zh_cn"):
                    with st.container():
                        st.markdown(
                            f"**第{house_num}宮** {planet_note}\n\n"
                            f"✅ 推薦：{rule['recommended']}\n\n"
                            f"❌ 避免：{rule['avoid']}\n\n"
                            f"📝 {rule['note']}"
                        )
                else:
                    with st.container():
                        st.markdown(
                            f"**House {house_num}** {planet_note}\n\n"
                            f"✅ Recommended: {rule['recommended']}\n\n"
                            f"❌ Avoid: {rule['avoid']}\n\n"
                            f"📝 {rule['note']}"
                        )

        st.divider()

        # House colour remedies from expanded module
        if lang in ("zh", "zh_cn"):
            st.markdown("**🔨 十二宮補救色彩措施一覽**")
        else:
            st.markdown("**🔨 House Colour Remedy Actions**")

        hcr_rows = []
        for hnum, rem_list in HOUSE_COLOR_REMEDIES.items():
            planets_in_h = [p.name_zh for p in chart.planets if p.house == hnum]
            if lang in ("zh", "zh_cn"):
                hcr_rows.append({
                    "宮位": hnum,
                    "居住行星": "、".join(planets_in_h) if planets_in_h else "空宮",
                    "補救建議": "；".join(rem_list),
                })
            else:
                hcr_rows.append({
                    "House": hnum,
                    "Planets": ", ".join(planets_in_h) if planets_in_h else "Empty",
                    "Remedy": "; ".join(rem_list),
                })
        st.dataframe(pd.DataFrame(hcr_rows), hide_index=True, width="stretch")
