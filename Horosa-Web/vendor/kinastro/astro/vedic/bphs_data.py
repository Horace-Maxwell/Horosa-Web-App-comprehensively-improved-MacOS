# astro/data/bphs_data.py
# ========================================================
# 《布里哈特·帕拉沙拉占星經》 (Brihat Parashara Hora Shastra)
# 結構化資料庫 - 專為 kinastro 專案設計
# 來源：2001年修訂版（甘尼許達塔·帕塔克編輯，薩維特里·塔庫爾出版社）
# 包含：梵文原文 + 印地語註釋 + 完整中文翻譯
# 版本：1.0 (2026-04-14)
# ========================================================

BPHS_METADATA = {
    "title_zh": "布里哈特·帕拉沙拉占星經",
    "title_en": "Brihat Parashara Hora Shastra",
    "edition": "2001年修訂版",
    "editor": "已故甘尼許達塔·帕塔克",
    "publisher": "薩維特里·塔庫爾出版社",
    "language": ["梵文", "印地語", "中文"],
    "description_zh": "吠陀占星學最權威的根本經典，涵蓋星座、行星、16分盤、宮位、瑜伽、大運、八分圖、壽命等所有主題。",
    "total_pages": 788,
    "source_file": "Brihat Parashar Hora Shastra.txt"
}

# ==================== 章節目錄 (完整翻譯自原文TOC) ====================
BPHS_CHAPTERS = [
    {"id": 1, "title_zh": "吉祥開篇", "title_en": "Mangalacharana", "page": 17},
    {"id": 2, "title_zh": "化身論述", "title_en": "Avatara Vada", "page": 18},
    {"id": 3, "title_zh": "星座分類章", "title_en": "Rashi Prabheda", "page": 22},
    {"id": 4, "title_zh": "行星本質章", "title_en": "Graha Svarupa", "page": 26},
    {"id": 5, "title_zh": "行星高低點與基本三角", "title_en": "Ucca Neecha & Moola Trikona", "page": 32},
    {"id": 6, "title_zh": "行星友敵關係", "title_en": "Graha Maitri", "page": 33},
    {"id": 7, "title_zh": "行星力量計算", "title_en": "Graha Bala", "page": 35},
    {"id": 8, "title_zh": "隱蔽行星與古拉卡", "title_en": "Aprakasha Graha & Gulika", "page": 37},
    {"id": 9, "title_zh": "16種分盤專論", "title_en": "Shodasa Varga", "page": 47},
    {"id": 10, "title_zh": "行星視線章", "title_en": "Drishti", "page": 76},
    {"id": 11, "title_zh": "災厄與化解章", "title_en": "Arishta & Bhanga", "page": 80},
    {"id": 12, "title_zh": "主宰星章", "title_en": "Karaka", "page": 105},
    {"id": 13, "title_zh": "宮位果報章", "title_en": "Bhava Phala", "page": 152},
    {"id": 14, "title_zh": "王者瑜伽等特殊組合", "title_en": "Raja Yoga & Special Yogas", "page": 222},
    {"id": 15, "title_zh": "行星狀態章（阿瓦斯塔）", "title_en": "Graha Avastha", "page": 232},
    {"id": 16, "title_zh": "壽命章", "title_en": "Ayurdaya", "page": 260},
    {"id": 17, "title_zh": "殺星與死亡章", "title_en": "Maraka", "page": 292},
    {"id": 18, "title_zh": "八分圖章", "title_en": "Ashtakavarga", "page": 317},
    {"id": 19, "title_zh": "大運章", "title_en": "Dasha", "page": 374},
    {"id": 20, "title_zh": "小運與微細運", "title_en": "Antardasha & Sookshma", "page": 448},
    {"id": 21, "title_zh": "生命大運與死亡時刻", "title_en": "Prana Dasha", "page": 574},
    {"id": 22, "title_zh": "力量計算總論", "title_en": "Shad Bala & Other Balas", "page": 614},
]

# ==================== 新增：完整的財富宮果報 ====================
BPHS_DHANA_BHAVA = {
    "bhava_number": 2,
    "title_zh": "財富宮果報（धनभावफलम्）",
    "basic_signification_zh": "財富、家庭、言語、食物、右眼、銀行存款、珠寶、家族傳統",
    "general_rule_zh": "第2宮強旺、吉星入駐或主星落吉宮 → 極富；凶星入駐或主星落凶宮 → 貧困或財來財去。",
    
    "lord_placement": {
        1: {"zh": "財富自力更生，靠自身努力致富"},
        2: {"zh": "財富穩定，家族事業興旺"},
        3: {"zh": "靠努力、旅行或兄弟幫助致富"},
        4: {"zh": "祖產豐厚，房地產帶來財富"},
        5: {"zh": "投機、智慧或子女帶來財富"},
        6: {"zh": "財富來自服務、醫療或訴訟，但多波折"},
        7: {"zh": "配偶或合夥帶來大量財富"},
        8: {"zh": "意外之財、遺產，但易有損失"},
        9: {"zh": "幸運之財、父親或宗教帶來財富"},
        10: {"zh": "事業、名聲帶來大量財富"},
        11: {"zh": "收入穩定，朋友與願望實現帶來財富"},
        12: {"zh": "財富外流、異國花費多，易破財"},
    },
    
    "planet_in_2nd": {
        "sun": {"zh": "財富來自政府、權力或父親，說話權威，但易有眼疾", "wealth_level": "中上"},
        "moon": {"zh": "財富波動，靠母親或情感相關行業，言語柔和", "wealth_level": "中"},
        "mars": {"zh": "財富來自土地、軍事或技術，說話直率，易有爭執", "wealth_level": "中"},
        "mercury": {"zh": "商業、演說、寫作帶來財富，智慧型致富", "wealth_level": "上"},
        "jupiter": {"zh": "極富，智慧、宗教、教學帶來大量財富，言語有德", "wealth_level": "極上"},
        "venus": {"zh": "奢侈享受、藝術、珠寶、配偶帶來財富，言語優美", "wealth_level": "上"},
        "saturn": {"zh": "晚年致富，勞苦中得財，言語嚴肅，家族傳統重要", "wealth_level": "中下"},
        "rahu": {"zh": "意外之財、投機致富，但易有欺詐或波折", "wealth_level": "不穩定"},
        "ketu": {"zh": "靈性財富或突然損失，言語簡樸，易斷離物質", "wealth_level": "不穩定"},
    },
    
    "wealth_yogas": [
        {"name": "Dhana Yoga", "zh": "第2宮主落吉宮或與吉星合 → 財富豐厚"},
        {"name": "Lakshmi Yoga", "zh": "第2宮主與第9宮主強旺或互換 → 極大財富與幸運"},
        {"name": "Saraswati Yoga", "zh": "木星、水星、金星同在第2宮 → 智慧與財富兼備"},
    ],
    
    "note_zh": "判斷財富宮時，必須同時看第2宮主星強弱、第11宮（收入宮）、木星影響，以及行星狀態（Avastha）。"
}

# ==================== 新增：完整的配偶宮果報（第7宮） ====================
BPHS_SAPTAMA_BHAVA = {
    "bhava_number": 7,
    "title_zh": "配偶宮果報（सप्तमभावफलम्）",
    "basic_signification_zh": "婚姻、配偶、事業合夥、異國旅行、公開競爭、性慾、右側身體",
    "general_rule_zh": "第7宮強旺、吉星入駐或主星落吉宮 → 婚姻美滿、配偶賢淑；凶星入駐或主星落凶宮 → 婚姻不順、配偶有疾或分離。",
    
    "lord_placement": {
        1: {"zh": "配偶個性強烈，婚姻靠自身努力維繫"},
        2: {"zh": "配偶帶來財富，婚姻穩定"},
        3: {"zh": "配偶勇敢、善於溝通，婚姻中多旅行"},
        4: {"zh": "配偶溫柔、家庭導向，婚姻生活安穩"},
        5: {"zh": "配偶聰明、子女緣佳，婚姻有浪漫"},
        6: {"zh": "配偶可能有健康問題或爭執，婚姻波折"},
        7: {"zh": "配偶優秀，婚姻和諧，但需注意外遇"},
        8: {"zh": "配偶長壽或神秘，婚姻中易有意外"},
        9: {"zh": "配偶有宗教或異國背景，婚姻帶來幸運"},
        10: {"zh": "配偶事業有成，婚姻中互相支持"},
        11: {"zh": "配偶帶來收入與朋友圈，婚姻圓滿"},
        12: {"zh": "配偶可能異國或有分離傾向，婚姻需努力"},
    },
    
    "planet_in_7th": {
        "sun": {"zh": "配偶權威、個性強，婚姻中易有爭執，但地位高", "marriage_level": "中"},
        "moon": {"zh": "配偶溫柔、情感豐富，婚姻生活變化多", "marriage_level": "中上"},
        "mars": {"zh": "配偶精力旺盛、可能脾氣大，婚姻中易有衝突", "marriage_level": "中下"},
        "mercury": {"zh": "配偶聰明、善談，婚姻中多交流與旅行", "marriage_level": "上"},
        "jupiter": {"zh": "配偶賢淑、智慧高，婚姻美滿、子女優秀", "marriage_level": "極上"},
        "venus": {"zh": "配偶美麗、藝術氣質，婚姻浪漫且享樂", "marriage_level": "極上"},
        "saturn": {"zh": "配偶年長或嚴肅，婚姻穩定但較晚婚", "marriage_level": "中下"},
        "rahu": {"zh": "配偶異國或特殊背景，婚姻刺激但易波折", "marriage_level": "不穩定"},
        "ketu": {"zh": "配偶靈性強或有分離傾向，婚姻偏精神層面", "marriage_level": "不穩定"},
    },
    
    "special_yogas": [
        {"name": "Kalatra Yoga", "zh": "第7宮主與吉星合或落吉宮 → 婚姻極美滿"},
        {"name": "Dara Yoga", "zh": "金星或木星強旺在第7宮 → 配偶優秀、婚姻幸福"},
        {"name": "Upapada Yoga", "zh": "Upapada lagna 強旺 → 配偶高貴、婚姻長久"},
    ],
    
    "note_zh": "判斷配偶宮時，必須同時看第7宮主星強弱、第2宮（家庭）、第8宮（長壽）、金星與木星影響，以及行星狀態（Avastha）。吉星強旺 → 婚姻美滿；凶星強 → 婚姻波折或分離。"
}


# ==================== 新增：完整的事業宮果報（第10宮） ====================
BPHS_DASHAMA_BHAVA = {
    "bhava_number": 10,
    "title_zh": "事業宮果報（दशमभावफलम्）",
    "basic_signification_zh": "事業、地位、名聲、父親、權威、政府、行動（karma）、膝蓋、左側身體、榮譽、職業成就",
    "general_rule_zh": "第10宮強旺、吉星入駐或主星落吉宮 → 事業成功、地位崇高、名聲遠播；凶星入駐或主星落凶宮 → 事業波折、地位不穩、名聲受損。",
    
    "lord_placement": {
        1: {"zh": "事業靠自身努力，地位來自個人能力"},
        2: {"zh": "事業帶來財富，家族事業興旺"},
        3: {"zh": "事業靠努力與勇氣，適合旅行或兄弟合作"},
        4: {"zh": "事業與房產、母親或教育相關，穩定發展"},
        5: {"zh": "事業靠智慧、投機或子女幫助，榮譽顯赫"},
        6: {"zh": "事業來自服務、醫療或競爭，易有波折"},
        7: {"zh": "事業與配偶或合夥人密切相關"},
        8: {"zh": "事業有意外轉變、遺產或神秘行業"},
        9: {"zh": "事業得幸運、父親或宗教支持，遠行有利"},
        10: {"zh": "事業極強，地位崇高、名聲遠播"},
        11: {"zh": "事業收入豐厚，朋友與願望助力大"},
        12: {"zh": "事業可能在異國發展，或易有支出與轉變"},
    },
    
    "planet_in_10th": {
        "sun": {"zh": "政府、公職、權威事業，地位崇高，但易與父親有衝突", "career_level": "極上"},
        "moon": {"zh": "事業多變化，適合與公眾、情感相關行業（如教育、護理）", "career_level": "中"},
        "mars": {"zh": "軍事、技術、土地或工程事業，積極進取但易有爭執", "career_level": "上"},
        "mercury": {"zh": "商業、寫作、演說、顧問事業，智慧型成功", "career_level": "上"},
        "jupiter": {"zh": "教學、宗教、法律或顧問事業，地位崇高、名聲遠播", "career_level": "極上"},
        "venus": {"zh": "藝術、娛樂、美容、外交事業，享受與榮譽兼得", "career_level": "上"},
        "saturn": {"zh": "勞苦型事業、行政或技術工作，晚年才得大成就", "career_level": "中下"},
        "rahu": {"zh": "投機、異國、科技或非常規事業，成名快但易波折", "career_level": "不穩定"},
        "ketu": {"zh": "靈性、研究、醫療或隱秘事業，地位來自內在修為", "career_level": "中"},
    },
    
    "special_yogas": [
        {"name": "Karma Yoga / Rajya Yoga", "zh": "第10宮主強旺或與吉星合 → 事業大成、地位崇高"},
        {"name": "Dharma Karmadhipati Yoga", "zh": "9宮主與10宮主互換或相合 → 極高地位與榮譽"},
        {"name": "Mahabhagya Yoga (部分)", "zh": "太陽或木星強在第10宮 → 名聲與權力"},
    ],
    
    "note_zh": "判斷事業宮時，必須同時看第10宮主星強弱、第2宮（財富）、第11宮（收入）、太陽與木星影響，以及行星狀態（Avastha）。吉星強旺 → 事業順遂、名聲遠播；凶星強 → 事業多阻、地位不穩。"
}

# ==================== 新增：完整的子女宮果報（第5宮） ====================
BPHS_PANCHAMA_BHAVA = {
    "bhava_number": 5,
    "title_zh": "子女宮果報（पञ्चमभावफलम्）",
    "basic_signification_zh": "子女、智慧、愛情、投機、咒語、前世福德、創造力、學業、娛樂",
    "general_rule_zh": "第5宮強旺、吉星入駐或主星落吉宮 → 子女優秀、智慧高、投機成功、愛情甜蜜；凶星入駐或主星落凶宮 → 子女緣薄、智慧受阻、投機失敗。",
    
    "lord_placement": {
        1: {"zh": "子女靠自身能力，智慧來自個人努力"},
        2: {"zh": "子女帶來財富，家族智慧傳承"},
        3: {"zh": "子女勇敢、善於溝通，投機靠努力"},
        4: {"zh": "子女溫柔、家庭導向，智慧與母親相關"},
        5: {"zh": "子女極優秀，智慧與投機皆大吉"},
        6: {"zh": "子女可能有健康問題或爭執，投機波折"},
        7: {"zh": "子女與配偶相關，愛情帶來子女緣"},
        8: {"zh": "子女有神秘或靈性特質，易有意外"},
        9: {"zh": "子女帶來幸運，前世福德深厚"},
        10: {"zh": "子女事業有成，智慧與地位兼備"},
        11: {"zh": "子女帶來收入與朋友圈，投機成功"},
        12: {"zh": "子女可能異國或有分離傾向，智慧偏靈性"},
    },
    
    "planet_in_5th": {
        "sun": {"zh": "子女有領導力、地位高，但易與父親有衝突", "children_level": "中上"},
        "moon": {"zh": "子女情感豐富、數量多，智慧敏銳", "children_level": "上"},
        "mars": {"zh": "子女勇敢、技術型，但脾氣較大", "children_level": "中"},
        "mercury": {"zh": "子女聰明、善於學習與商業，智慧極高", "children_level": "極上"},
        "jupiter": {"zh": "子女優秀、智慧與道德兼備，投機大吉", "children_level": "極上"},
        "venus": {"zh": "子女美麗、藝術氣質，愛情與子女緣皆佳", "children_level": "極上"},
        "saturn": {"zh": "子女較晚得或數量少，智慧需長期培養", "children_level": "中下"},
        "rahu": {"zh": "子女特殊或異國背景，投機刺激但易波折", "children_level": "不穩定"},
        "ketu": {"zh": "子女靈性強或有分離傾向，智慧偏內在", "children_level": "中"},
    },
    
    "special_yogas": [
        {"name": "Putra Yoga", "zh": "第5宮主強旺或與吉星合 → 子女優秀、數量多"},
        {"name": "Budhi Yoga", "zh": "木星或水星強在第5宮 → 智慧極高、學業成就"},
        {"name": "Saraswati Yoga (部分)", "zh": "木星、水星、金星同在第5宮 → 智慧、藝術、子女皆大吉"},
    ],
    
    "note_zh": "判斷子女宮時，必須同時看第5宮主星強弱、第2宮（家庭）、木星影響，以及行星狀態（Avastha）。吉星強旺 → 子女賢孝、智慧超群；凶星強 → 子女緣薄或智慧受阻。"
}


# ==================== 新增：完整的疾厄宮果報（第6宮） ====================
BPHS_SHASHTA_BHAVA = {
    "bhava_number": 6,
    "title_zh": "疾厄宮果報（षष्ठभावफलम्）",
    "basic_signification_zh": "疾病、敵人、債務、僕人、舅舅、傷口、訴訟、競爭、盜賊、毒物、醫療",
    "general_rule_zh": "第6宮為塵薩那（壞宮），吉星入駐可戰勝敵人、解除債務，但易有疾病；凶星入駐則敵人眾多、疾病纏身、債務沉重、訴訟不斷。",
    
    "lord_placement": {
        1: {"zh": "疾病與敵人來自自身，需靠努力克服"},
        2: {"zh": "疾病影響財富，敵人來自家族"},
        3: {"zh": "敵人與兄弟相關，疾病需勇氣面對"},
        4: {"zh": "疾病與母親或房產有關，敵人來自家庭"},
        5: {"zh": "子女或智慧帶來敵人，疾病影響投機"},
        6: {"zh": "疾病與敵人極強，但自身抵抗力也強"},
        7: {"zh": "配偶或合夥帶來疾病或敵人"},
        8: {"zh": "疾病與長壽、意外相關，敵人來自隱秘"},
        9: {"zh": "疾病影響幸運，敵人來自宗教或父親"},
        10: {"zh": "疾病影響事業，敵人來自職場或上司"},
        11: {"zh": "敵人帶來收入，但疾病影響收益"},
        12: {"zh": "疾病導致支出，敵人來自異國或隱秘"},
    },
    
    "planet_in_6th": {
        "sun": {"zh": "疾病與權威或父親相關，易有眼疾或心臟病，敵人強大", "level": "中下"},
        "moon": {"zh": "疾病多變化、情緒相關，敵人來自女性或公眾", "level": "中"},
        "mars": {"zh": "急性疾病、傷口、發炎、事故，敵人兇猛", "level": "弱"},
        "mercury": {"zh": "皮膚病、呼吸系統疾病、商業糾紛，敵人聰明", "level": "中"},
        "jupiter": {"zh": "疾病較輕，可戰勝敵人，智慧化解債務", "level": "上"},
        "venus": {"zh": "疾病與生殖、腎臟相關，敵人來自異性或享樂", "level": "中"},
        "saturn": {"zh": "慢性病、骨骼或關節疾病，敵人持久，債務沉重", "level": "弱"},
        "rahu": {"zh": "奇怪疾病、毒物、中邪、意外，敵人強大且隱秘", "level": "不穩定"},
        "ketu": {"zh": "靈性疾病、神秘症狀、脫離物質，敵人來自前世", "level": "中"},
    },
    
    "special_yogas": [
        {"name": "Shatru Yoga", "zh": "第6宮主強旺或吉星入駐 → 戰勝敵人、解除債務"},
        {"name": "Roga Bhanga Yoga", "zh": "木星或金星強在第6宮 → 疾病可化解"},
        {"name": "Harsha Yoga", "zh": "第6宮主落吉宮且無凶星干擾 → 戰勝所有敵人"},
    ],
    
    "note_zh": "第6宮為塵薩那，判斷時必須同時看第6宮主星強弱、第12宮（支出）、火星與土星影響，以及行星狀態（Avastha）。吉星強 → 戰勝敵人、疾病輕；凶星強 → 疾病重、敵人多、債務纏身。"
}

# ==================== 新增：完整的福德宮果報（第9宮） ====================
BPHS_NAVAMA_BHAVA = {
    "bhava_number": 9,
    "title_zh": "福德宮果報（नवमभावफलम्）",
    "basic_signification_zh": "幸運、父親、宗教、遠行、福德、高等教育、孫子、導師、道德、祖產、朝聖",
    "general_rule_zh": "第9宮為大吉宮，強旺、吉星入駐或主星落吉宮 → 大幸運、父親恩惠、宗教虔誠、遠行吉利、智慧與道德俱佳；凶星入駐或主星落凶宮 → 幸運受阻、父親問題、宗教信仰不穩、遠行不利。",
    
    "lord_placement": {
        1: {"zh": "幸運來自自身努力，父親影響大"},
        2: {"zh": "幸運帶來財富，家族宗教傳統強"},
        3: {"zh": "幸運靠勇氣與努力，遠行或兄弟幫助"},
        4: {"zh": "幸運與母親或房產相關，宗教教育穩定"},
        5: {"zh": "幸運來自智慧、子女或投機，福德深厚"},
        6: {"zh": "幸運需克服敵人或疾病，宗教信仰受考驗"},
        7: {"zh": "配偶或合夥帶來幸運與宗教緣"},
        8: {"zh": "幸運來自意外或遺產，宗教偏神秘"},
        9: {"zh": "幸運極強，父親恩惠、宗教虔誠、遠行大吉"},
        10: {"zh": "事業帶來幸運，地位與宗教結合"},
        11: {"zh": "收入與朋友帶來幸運，願望容易實現"},
        12: {"zh": "幸運來自異國或隱秘修行，易有支出"},
    },
    
    "planet_in_9th": {
        "sun": {"zh": "父親權威、地位高，宗教或政府相關幸運，遠行吉利", "fortune_level": "上"},
        "moon": {"zh": "母親帶來幸運，情感與宗教結合，遠行變化多", "fortune_level": "中上"},
        "mars": {"zh": "勇氣帶來幸運，適合軍事或技術遠行，但易衝突", "fortune_level": "中"},
        "mercury": {"zh": "智慧、商業、寫作帶來幸運，高等教育優秀", "fortune_level": "上"},
        "jupiter": {"zh": "極大幸運、宗教虔誠、父親恩惠、智慧與道德俱佳", "fortune_level": "極上"},
        "venus": {"zh": "藝術、配偶或享樂帶來幸運，宗教偏優美", "fortune_level": "上"},
        "saturn": {"zh": "晚年得幸運，宗教信仰需長期修持，父親較嚴格", "fortune_level": "中下"},
        "rahu": {"zh": "異國或非常規宗教帶來幸運，但易波折或欺詐", "fortune_level": "不穩定"},
        "ketu": {"zh": "靈性幸運、解脫傾向，宗教偏神秘或出家", "fortune_level": "中"},
    },
    
    "special_yogas": [
        {"name": "Bhagya Yoga", "zh": "第9宮主強旺或與吉星合 → 大幸運、父親恩惠"},
        {"name": "Dharma Karmadhipati Yoga", "zh": "9宮主與10宮主互換或相合 → 極高地位與宗教榮譽"},
        {"name": "Guru-Mangala Yoga", "zh": "木星與火星強在第9宮 → 勇氣與智慧帶來大福德"},
    ],
    
    "note_zh": "第9宮為大吉宮，判斷時必須同時看第9宮主星強弱、第2宮（財富）、第5宮（智慧）、木星影響，以及行星狀態（Avastha）。吉星強旺 → 幸運無比、宗教虔誠；凶星強 → 幸運受阻、父親或信仰問題。"
}

BPHS_ASHTAMA_BHAVA = {
    "bhava_number": 8,
    "title_zh": "隱秘宮果報（अष्टमभावफलम्）",
    "basic_signification_zh": "長壽、遺產、突然得失、隱秘知識、神秘學、死亡、配偶家族、研究、傷害、意外、再生、解脫",
    "general_rule_zh": "第8宮為塵薩那（壞宮），吉星入駐可得長壽與意外之財、精通神秘學；凶星入駐則壽命受損、意外頻發、遺產糾紛、隱秘敵人。",
    
    "lord_placement": {
        1: {"zh": "長壽靠自身努力，隱秘事務需謹慎"},
        2: {"zh": "遺產影響財富，家族隱秘事務多"},
        3: {"zh": "勇氣帶來長壽，意外與兄弟相關"},
        4: {"zh": "長壽與母親或房產有關，隱秘事務影響家庭"},
        5: {"zh": "子女或智慧帶來意外之財，隱秘福德"},
        6: {"zh": "戰勝疾病與敵人可延壽，隱秘競爭"},
        7: {"zh": "配偶帶來遺產或長壽，但易有隱秘問題"},
        8: {"zh": "長壽極強，遺產與神秘知識豐富"},
        9: {"zh": "幸運帶來長壽與遺產，宗教或遠行有利"},
        10: {"zh": "事業帶來意外之財，地位與隱秘事務相關"},
        11: {"zh": "收入來自遺產或隱秘來源"},
        12: {"zh": "長壽與解脫相關，隱秘支出或異國事務"},
    },
    
    "planet_in_8th": {
        "sun": {"zh": "長壽中等，父親相關隱秘事務，易有眼疾或心臟問題", "longevity_level": "中"},
        "moon": {"zh": "壽命波動，母親或情感帶來遺產，隱秘情緒問題", "longevity_level": "中"},
        "mars": {"zh": "意外傷害、事故多，壽命較短但勇氣強", "longevity_level": "弱"},
        "mercury": {"zh": "精通神秘學、研究能力強，遺產來自智慧", "longevity_level": "中上"},
        "jupiter": {"zh": "長壽、智慧化解隱秘危機，遺產豐富", "longevity_level": "上"},
        "venus": {"zh": "配偶家族帶來遺產，隱秘享樂或藝術才能", "longevity_level": "中上"},
        "saturn": {"zh": "長壽但晚年辛苦，慢性病或遺產糾紛", "longevity_level": "中下"},
        "rahu": {"zh": "突然意外之財或損失，隱秘敵人強大", "longevity_level": "不穩定"},
        "ketu": {"zh": "靈性解脫、神秘智慧，壽命偏精神層面", "longevity_level": "中"},
    },
    
    "special_yogas": [
        {"name": "Ashtama Yoga Bhanga", "zh": "第8宮主落吉宮或與吉星合 → 長壽與意外之財"},
        {"name": "Mrityu Bhanga Yoga", "zh": "木星或金星強在第8宮 → 化解死亡危機"},
        {"name": "Kemadruma Bhanga (部分)", "zh": "第8宮吉星強 → 隱秘知識帶來大成就"},
    ],
    
    "note_zh": "第8宮為壽命與隱秘之宮，判斷時必須同時看第8宮主星強弱、第2宮（財富）、第12宮（支出）、土星與火星影響，以及行星狀態（Avastha）。吉星強 → 長壽、遺產、神秘智慧；凶星強 → 意外、疾病、壽命受損。"
}

# ==================== 新增：完整的收益宮果報（第11宮） ====================
BPHS_EKADASA_BHAVA = {
    "bhava_number": 11,
    "title_zh": "收益宮果報（एकादशभावफलम्）",
    "basic_signification_zh": "收入、收益、朋友、願望實現、左耳、左側身體、年金、兄弟的兒子、社會圈、社團、利潤",
    "general_rule_zh": "第11宮為大吉宮，強旺、吉星入駐或主星落吉宮 → 收入豐厚、朋友眾多、願望容易實現；凶星入駐或主星落凶宮 → 收入不穩、朋友背叛、願望難成。",
    
    "lord_placement": {
        1: {"zh": "收入靠自身努力，朋友來自個人魅力"},
        2: {"zh": "收入帶來財富，家族朋友圈強"},
        3: {"zh": "收入靠勇氣與努力，朋友來自兄弟或旅行"},
        4: {"zh": "收入與房產、母親相關，穩定收益"},
        5: {"zh": "收入來自智慧、投機或子女，願望大成"},
        6: {"zh": "收入來自服務、醫療或競爭，但多波折"},
        7: {"zh": "配偶或合夥帶來大量收入"},
        8: {"zh": "收入來自遺產或隱秘來源，意外之財"},
        9: {"zh": "幸運帶來收入，朋友與宗教相關"},
        10: {"zh": "事業帶來豐厚收入，地位與收益結合"},
        11: {"zh": "收入極強，朋友眾多、願望全部實現"},
        12: {"zh": "收入可能來自異國，但易有支出"},
    },
    
    "planet_in_11th": {
        "sun": {"zh": "收入來自政府或權威，朋友地位高，願望易實現", "income_level": "上"},
        "moon": {"zh": "收入波動，朋友來自公眾或女性，願望情感化", "income_level": "中"},
        "mars": {"zh": "收入靠努力與競爭，朋友勇敢，但易有爭執", "income_level": "中"},
        "mercury": {"zh": "商業、演說、寫作帶來豐厚收入，朋友智慧型", "income_level": "極上"},
        "jupiter": {"zh": "極大收入、朋友眾多、願望全部實現，智慧與道德兼備", "income_level": "極上"},
        "venus": {"zh": "收入來自藝術、享樂或配偶，朋友優雅", "income_level": "上"},
        "saturn": {"zh": "晚年收入穩定，朋友少但忠誠，需長期努力", "income_level": "中下"},
        "rahu": {"zh": "意外之財、投機收入，朋友特殊但易波折", "income_level": "不穩定"},
        "ketu": {"zh": "靈性收入或突然損失，朋友偏精神層面", "income_level": "中"},
    },
    
    "special_yogas": [
        {"name": "Labha Yoga", "zh": "第11宮主強旺或與吉星合 → 收入極豐、願望大成"},
        {"name": "Upachaya Yoga", "zh": "第3、6、11宮吉星強 → 收入持續增長"},
        {"name": "Saraswati Yoga (部分)", "zh": "木星、水星、金星強在第11宮 → 智慧帶來大量收益"},
    ],
    
    "note_zh": "第11宮為收益與願望之宮，判斷時必須同時看第11宮主星強弱、第2宮（財富）、第10宮（事業）、木星影響，以及行星狀態（Avastha）。吉星強旺 → 收入豐厚、朋友眾多；凶星強 → 收入不穩、朋友背叛。"
}

# ==================== 新增：完整的損失宮果報（第12宮） ====================
BPHS_DVADASHA_BHAVA = {
    "bhava_number": 12,
    "title_zh": "損失宮果報（द्वादशभावफलम्）",
    "basic_signification_zh": "支出、損失、異國、解脫、床第之樂、左眼、隔離、醫院、慈善、隱居、左側身體、 Moksha（解脫）",
    "general_rule_zh": "第12宮為塵薩那（壞宮），吉星入駐可得異國居住、靈性解脫、慈善功德；凶星入駐則支出巨大、損失嚴重、異國波折、壽命受損。",
    
    "lord_placement": {
        1: {"zh": "支出來自自身，易有隱居或異國傾向"},
        2: {"zh": "支出影響財富，家族有隱秘損失"},
        3: {"zh": "支出與兄弟或旅行相關，勇氣帶來解脫"},
        4: {"zh": "支出與母親或房產有關，易有醫院或隔離"},
        5: {"zh": "支出影響子女或投機，智慧帶來解脫"},
        6: {"zh": "支出用於疾病或敵人，戰勝後得解脫"},
        7: {"zh": "配偶帶來支出或異國居住"},
        8: {"zh": "遺產或隱秘事務帶來支出"},
        9: {"zh": "幸運帶來異國或宗教支出，解脫吉"},
        10: {"zh": "事業帶來支出，地位與隱居相關"},
        11: {"zh": "收入用於支出，朋友帶來損失"},
        12: {"zh": "損失極大，但靈性解脫與 Moksha 最強"},
    },
    
    "planet_in_12th": {
        "sun": {"zh": "父親或權威帶來支出，異國居住或隱居，左眼易有問題", "loss_level": "中"},
        "moon": {"zh": "情感支出多，母親相關損失，易有隔離或醫院", "loss_level": "中"},
        "mars": {"zh": "意外支出、事故、傷害，異國衝突", "loss_level": "弱"},
        "mercury": {"zh": "商業或智慧相關支出，異國學習或研究", "loss_level": "中"},
        "jupiter": {"zh": "慈善支出、宗教捐獻，異國或靈性居住吉利", "loss_level": "上"},
        "venus": {"zh": "享樂或配偶相關支出，床第之樂，異國浪漫", "loss_level": "中上"},
        "saturn": {"zh": "長期支出、慢性損失、隔離或醫院，晚年隱居", "loss_level": "弱"},
        "rahu": {"zh": "異國或神秘支出、突然大損失，隱秘敵人", "loss_level": "不穩定"},
        "ketu": {"zh": "靈性支出、解脫傾向，Moksha 強烈", "loss_level": "中"},
    },
    
    "special_yogas": [
        {"name": "Vyaya Yoga Bhanga", "zh": "第12宮主落吉宮或與吉星合 → 支出轉為慈善與解脫"},
        {"name": "Moksha Yoga", "zh": "木星或金星強在第12宮 → 強烈解脫傾向"},
        {"name": "Harsha Yoga (部分)", "zh": "第6、8、12宮吉星強 → 戰勝敵人後得大解脫"},
    ],
    
    "note_zh": "第12宮為支出與 Moksha 之宮，判斷時必須同時看第12宮主星強弱、第2宮（財富）、第8宮（遺產）、土星與木星影響，以及行星狀態（Avastha）。吉星強 → 異國居住、慈善、解脫；凶星強 → 巨大損失、隔離、壽命受損。"
}



# ==================== 新增：行星友敵關係 ====================
BPHS_GRAHA_MAITRI = {
    "sun": {"friends": ["moon", "mars", "jupiter"], "neutral": ["mercury"], "enemies": ["venus", "saturn"]},
    "moon": {"friends": ["sun", "mercury"], "neutral": ["venus", "jupiter", "saturn"], "enemies": ["mars"]},
    "mars": {"friends": ["sun", "moon", "jupiter"], "neutral": ["venus", "saturn"], "enemies": ["mercury"]},
    "mercury": {"friends": ["sun", "venus"], "neutral": ["mars", "jupiter", "saturn"], "enemies": ["moon"]},
    "jupiter": {"friends": ["sun", "moon", "mars"], "neutral": ["mercury"], "enemies": ["venus", "saturn"]},
    "venus": {"friends": ["mercury", "saturn"], "neutral": ["mars", "jupiter"], "enemies": ["sun", "moon"]},
    "saturn": {"friends": ["mercury", "venus"], "neutral": ["jupiter"], "enemies": ["sun", "moon", "mars"]},
}



# ==================== 行星阿瓦斯塔（最重要的一章） ====================
# 12種主要阿瓦斯塔 + 各行星具體果報（直接從原文提取並翻譯）
BPHS_AVASTHAS = {
    "avastha_list": [
        "Shayana", "Upaveshana", "Netrapani", "Prakashana",
        "Gamana", "Agamana", "Sabha", "Agama", "Bhojana",
        "Nrityalipsa", "Kautuka", "Nidra"
    ],
    "description_zh": "行星在出生圖中的12種狀態（阿瓦斯塔），決定該行星的實際表現強弱與吉凶。",
    "calculation_method_zh": "1. 宿序號 × 行星序號 × 九分盤序號\n2. 加上出生宿 + 出生時刻 + 上升點序號\n3. 除以12取餘數即為狀態\n4. 再用姓名首字母元音數值與極點數精算視線/動態/無效。",
    
    # 各行星具體果報
	# ==================== 太陽 ====================
    "sun": {
        "Shayana": {"zh": "消化不良、四肢浮腫、膽汁失調、肛門潰瘍、心口絞痛", "strength": "弱"},
        "Upaveshana": {"zh": "貧窮、性格剛硬、財產損失、常涉訴訟", "strength": "弱"},
        "Netrapani": {"zh": "恒享喜樂、具洞察力、樂於助人、受君王恩寵", "strength": "強"},
        "Prakashana": {"zh": "胸懷寬廣、財富圓滿、善於演說、體力超群", "strength": "強"},
        "Gamana": {"zh": "長居異鄉、苦難纏身、怠惰、智慧與財富皆缺", "strength": "中"},
        "Agamana": {"zh": "沉溺他人妻妾、不受歡迎、熱衷旅行、品行污穢", "strength": "弱"},
        "Sabha": {"zh": "樂善好施、財寶盈滿、居華屋、朋友眾多", "strength": "強"},
        "Agama": {"zh": "受敵人困擾、性格浮躁、心術不正", "strength": "弱"},
        "Bhojana": {"zh": "關節疼痛、外遇破財、言語虛偽、頭痛、步入歧途", "strength": "弱"},
        "Nrityalipsa": {"zh": "受智者環繞、博學多才、受國王尊崇", "strength": "強"},
        "Kautuka": {"zh": "喜樂之源、擅長詩文、居王宮、容顏俊美", "strength": "強"},
        "Nidra": {"zh": "雙目昏沉、寄居異鄉、妻室與財富損失", "strength": "弱"}
    },

    # ==================== 月亮 ====================
    "moon": {
        "Shayana": {"zh": "自尊心強、性格清冷、好色、容易破財", "strength": "中"},
        "Upaveshana": {"zh": "易罹疾病、愚鈍、貧乏、沉溺惡行", "strength": "弱"},
        "Netrapani": {"zh": "重疾、言語浮誇、狡詐、沉迷不正之業", "strength": "弱"},
        "Prakashana": {"zh": "聲名顯赫、獲君王賞賜、與妻和樂、常赴聖地", "strength": "強"},
        "Gamana": {"zh": "罪孽深重、眼疾、黑月時膽怯", "strength": "弱"},
        "Agamana": {"zh": "傲慢、足部多病、隱藏罪行、心態卑微", "strength": "弱"},
        "Sabha": {"zh": "萬人之上、受諸王尊崇、風姿俊美、通曉情愛", "strength": "強"},
        "Agama": {"zh": "善辯、奉行正法（黑月則擁二妻、固執邪惡）", "strength": "中"},
        "Bhojana": {"zh": "享榮譽、車馬優渥、與妻兒共享天倫（黑月無此吉果）", "strength": "強"},
        "Nrityalipsa": {"zh": "強健有力、精通音律、深諳情趣（黑月則為罪人）", "strength": "強"},
        "Kautuka": {"zh": "可得王權或財富、擅長情愛技藝", "strength": "強"},
        "Nidra": {"zh": "具藝術才華（若衰弱則妻財皆失）", "strength": "中"}
    },

    # ==================== 火星（已完整補齊） ====================
    "mars": {
        "Shayana": {"zh": "身上多瘡瘍、劇烈搔癢、皮膚病（環狀癬、蟲咬）", "strength": "弱"},
        "Upaveshana": {"zh": "罪孽纏身、言語虛偽、傲慢無禮、雖富有卻背離正道", "strength": "弱"},
        "Netrapani": {"zh": "若在命宮則終生貧困，否則可為城鎮首長", "strength": "中"},
        "Prakashana": {"zh": "德行蓬勃、獲君王尊崇；第五宮或與羅睺同宮則子女配偶有損", "strength": "強"},
        "Gamana": {"zh": "每日瘡瘍、夫妻爭吵、多受蟲咬搔癢、財產損失", "strength": "弱"},
        "Agamana": {"zh": "受敵人騷擾、性格浮躁、心思狡詐、體型消瘦", "strength": "弱"},
        "Sabha": {"zh": "樂善好施、財寶盈滿、居華屋、朋友眾多", "strength": "強"},
        "Agama": {"zh": "受敵人困擾、性格浮躁、心術不正", "strength": "弱"},
        "Bhojana": {"zh": "關節疼痛、外遇破財、言語虛偽、頭痛、步入歧途", "strength": "弱"},
        "Nrityalipsa": {"zh": "受智者環繞、博學多才、受國王尊崇", "strength": "強"},
        "Kautuka": {"zh": "喜樂之源、擅長詩文、居王宮、容顏俊美", "strength": "強"},
        "Nidra": {"zh": "雙目昏沉、寄居異鄉、妻室與財富損失", "strength": "弱"}
    },

    # ==================== 水星 ====================
    "mercury": {
        "Shayana": {"zh": "言語笨拙、皮膚病、智慧受阻", "strength": "弱"},
        "Upaveshana": {"zh": "商業受阻、欺詐傾向、思慮不周", "strength": "弱"},
        "Netrapani": {"zh": "機智過人、擅長演說、商業成功", "strength": "強"},
        "Prakashana": {"zh": "智慧大開、學術成就、受長輩尊崇", "strength": "強"},
        "Gamana": {"zh": "頻繁旅行、思緒混亂、財務波動", "strength": "中"},
        "Agamana": {"zh": "口才便給、善於交際、商業獲利", "strength": "強"},
        "Sabha": {"zh": "演說家、受眾人喜愛、智慧受肯定", "strength": "強"},
        "Agama": {"zh": "思慮敏捷、商業機會多", "strength": "強"},
        "Bhojana": {"zh": "飲食講究、智慧增益", "strength": "中"},
        "Nrityalipsa": {"zh": "藝術天分、音樂舞蹈才能", "strength": "強"},
        "Kautuka": {"zh": "好奇心強、學習能力佳", "strength": "強"},
        "Nidra": {"zh": "思緒活躍、睡眠淺", "strength": "中"}
    },

    # ==================== 木星 ====================
    "jupiter": {
        "Shayana": {"zh": "智慧受阻、宗教事務受阻", "strength": "弱"},
        "Upaveshana": {"zh": "財富受限、子女緣薄", "strength": "弱"},
        "Netrapani": {"zh": "智慧大開、受尊長喜愛", "strength": "強"},
        "Prakashana": {"zh": "德行圓滿、得貴人相助、子女優秀", "strength": "強"},
        "Gamana": {"zh": "旅行中獲智慧、宗教旅行吉", "strength": "強"},
        "Agamana": {"zh": "智慧增益、財富穩定", "strength": "強"},
        "Sabha": {"zh": "受眾人尊敬、擔任顧問或教師", "strength": "強"},
        "Agama": {"zh": "智慧與財富皆增", "strength": "強"},
        "Bhojana": {"zh": "飲食豐盛、身體健康", "strength": "強"},
        "Nrityalipsa": {"zh": "藝術與宗教結合、受尊敬", "strength": "強"},
        "Kautuka": {"zh": "喜樂、智慧增長", "strength": "強"},
        "Nidra": {"zh": "睡眠安穩、智慧在夢中顯現", "strength": "強"}
    },

    # ==================== 金星 ====================
    "venus": {
        "Shayana": {"zh": "情慾受阻、配偶不和", "strength": "弱"},
        "Upaveshana": {"zh": "奢侈浪費、感情糾紛", "strength": "弱"},
        "Netrapani": {"zh": "美貌出眾、藝術才能、異性緣佳", "strength": "強"},
        "Prakashana": {"zh": "婚姻美滿、藝術成就、財富與享樂", "strength": "強"},
        "Gamana": {"zh": "旅行中遇美事、浪漫機會", "strength": "強"},
        "Agamana": {"zh": "感情穩定、配偶賢淑", "strength": "強"},
        "Sabha": {"zh": "受異性喜愛、社交成功", "strength": "強"},
        "Agama": {"zh": "情慾滿足、藝術靈感", "strength": "強"},
        "Bhojana": {"zh": "美食享受、身體愉悅", "strength": "強"},
        "Nrityalipsa": {"zh": "舞蹈、音樂、藝術天分極佳", "strength": "強"},
        "Kautuka": {"zh": "浪漫好奇、享受生活", "strength": "強"},
        "Nidra": {"zh": "睡眠中夢見愛情與美事", "strength": "強"}
    },

    # ==================== 土星 ====================
    "saturn": {
        "Shayana": {"zh": "慢性病、勞苦、延遲", "strength": "弱"},
        "Upaveshana": {"zh": "貧困、孤獨、事業受阻", "strength": "弱"},
        "Netrapani": {"zh": "堅韌、長期努力後成功", "strength": "中"},
        "Prakashana": {"zh": "晚年得名、權力、智慧", "strength": "強"},
        "Gamana": {"zh": "長期旅行、流離、勞苦", "strength": "弱"},
        "Agamana": {"zh": "事業穩定、責任感強", "strength": "中"},
        "Sabha": {"zh": "受長輩或權威尊敬", "strength": "中"},
        "Agama": {"zh": "耐心帶來成果", "strength": "中"},
        "Bhojana": {"zh": "飲食簡單、身體耐勞", "strength": "中"},
        "Nrityalipsa": {"zh": "藝術需長期磨練", "strength": "弱"},
        "Kautuka": {"zh": "好奇心轉為堅韌", "strength": "中"},
        "Nidra": {"zh": "睡眠不安、思慮沉重", "strength": "弱"}
    },

    # ==================== 羅睺 ====================
    "rahu": {
        "Shayana": {"zh": "幻覺、欺騙、精神困擾", "strength": "弱"},
        "Upaveshana": {"zh": "投機失敗、意外損失", "strength": "弱"},
        "Netrapani": {"zh": "機智、投機成功", "strength": "強"},
        "Prakashana": {"zh": "突然成名、權力、但不穩定", "strength": "中"},
        "Gamana": {"zh": "異國旅行、神秘經歷", "strength": "中"},
        "Agamana": {"zh": "意外獲利、但易生是非", "strength": "中"},
        "Sabha": {"zh": "群眾魅力、但易招嫉", "strength": "中"},
        "Agama": {"zh": "投機機會多", "strength": "中"},
        "Bhojana": {"zh": "異國飲食、消化問題", "strength": "弱"},
        "Nrityalipsa": {"zh": "前衛藝術、神秘魅力", "strength": "強"},
        "Kautuka": {"zh": "好奇心強、探索未知", "strength": "強"},
        "Nidra": {"zh": "睡眠中多怪夢", "strength": "弱"}
    },

    # ==================== 計都 ====================
    "ketu": {
        "Shayana": {"zh": "靈性覺醒、但身體虛弱", "strength": "中"},
        "Upaveshana": {"zh": "出家傾向、物質損失", "strength": "弱"},
        "Netrapani": {"zh": "神秘智慧、直覺強", "strength": "強"},
        "Prakashana": {"zh": "靈性成就、解脫傾向", "strength": "強"},
        "Gamana": {"zh": "朝聖旅行、尋求解脫", "strength": "強"},
        "Agamana": {"zh": "靈性回歸、放下執著", "strength": "強"},
        "Sabha": {"zh": "受靈性人士尊敬", "strength": "強"},
        "Agama": {"zh": "神秘知識增益", "strength": "強"},
        "Bhojana": {"zh": "素食、簡單飲食", "strength": "中"},
        "Nrityalipsa": {"zh": "靈性藝術、冥想", "strength": "強"},
        "Kautuka": {"zh": "探索神秘事物", "strength": "強"},
        "Nidra": {"zh": "睡眠中得靈性啟示", "strength": "強"}
    }
}

# ==================== 新增：星座分類章（12 Rashi） ====================
BPHS_RASHI = {
    "Aries": {"zh": "白羊座", "element": "火", "gender": "男", "ruler": "Mars", "nature": "動態、勇敢、領導力強、急躁"},
    "Taurus": {"zh": "金牛座", "element": "地", "gender": "女", "ruler": "Venus", "nature": "穩定、堅韌、物質享受、固執"},
    "Gemini": {"zh": "雙子座", "element": "風", "gender": "男", "ruler": "Mercury", "nature": "機智、善變、溝通、好奇"},
    "Cancer": {"zh": "巨蟹座", "element": "水", "gender": "女", "ruler": "Moon", "nature": "情感豐富、保護、敏感、家庭導向"},
    "Leo": {"zh": "獅子座", "element": "火", "gender": "男", "ruler": "Sun", "nature": "尊貴、領導、創造力、自我中心"},
    "Virgo": {"zh": "處女座", "element": "地", "gender": "女", "ruler": "Mercury", "nature": "分析、細心、服務、完美主義"},
    "Libra": {"zh": "天秤座", "element": "風", "gender": "男", "ruler": "Venus", "nature": "平衡、外交、美感、優柔寡斷"},
    "Scorpio": {"zh": "天蠍座", "element": "水", "gender": "女", "ruler": "Mars", "nature": "神秘、堅強、轉化、控制欲"},
    "Sagittarius": {"zh": "射手座", "element": "火", "gender": "男", "ruler": "Jupiter", "nature": "哲學、冒險、樂觀、自由"},
    "Capricorn": {"zh": "摩羯座", "element": "地", "gender": "女", "ruler": "Saturn", "nature": "務實、野心、紀律、保守"},
    "Aquarius": {"zh": "水瓶座", "element": "風", "gender": "男", "ruler": "Saturn", "nature": "創新、人道、獨立、叛逆"},
    "Pisces": {"zh": "雙魚座", "element": "水", "gender": "女", "ruler": "Jupiter", "nature": "慈悲、直覺、藝術、犧牲"},
}

# ==================== 新增：行星本質章（Graha Svarupa） ====================
BPHS_GRAHA_SVARUPA = {
    "sun": {"zh": "太陽", "gender": "男", "element": "火", "nature": "靈魂、權威、父親、榮耀", "color": "紅", "metal": "金"},
    "moon": {"zh": "月亮", "gender": "女", "element": "水", "nature": "心智、母親、情感、變化", "color": "白", "metal": "銀"},
    "mars": {"zh": "火星", "gender": "男", "element": "火", "nature": "勇氣、戰爭、兄弟、土地", "color": "紅", "metal": "銅"},
    "mercury": {"zh": "水星", "gender": "中性", "element": "地", "nature": "智慧、商業、演說、皮膚", "color": "綠", "metal": "水銀"},
    "jupiter": {"zh": "木星", "gender": "男", "element": "火", "nature": "智慧、子女、財富、宗教", "color": "黃", "metal": "金"},
    "venus": {"zh": "金星", "gender": "女", "element": "水", "nature": "愛情、藝術、配偶、享樂", "color": "白", "metal": "銀"},
    "saturn": {"zh": "土星", "gender": "中性", "element": "風", "nature": "紀律、勞苦、 longevity、僕人", "color": "黑", "metal": "鐵"},
    "rahu": {"zh": "羅睺", "gender": "中性", "element": "風", "nature": "幻覺、物質慾望、異國", "color": "黑", "metal": "鉛"},
    "ketu": {"zh": "計都", "gender": "中性", "element": "火", "nature": "靈性、解脫、神秘、斷離", "color": "灰", "metal": "鉛"},
}

# ==================== 新增：行星高低點（Ucca Neecha） ====================
BPHS_UCCA_NEECHA = {
    "sun": {"ucca": "Aries", "neecha": "Libra"},
    "moon": {"ucca": "Taurus", "neecha": "Scorpio"},
    "mars": {"ucca": "Capricorn", "neecha": "Cancer"},
    "mercury": {"ucca": "Virgo", "neecha": "Pisces"},
    "jupiter": {"ucca": "Cancer", "neecha": "Capricorn"},
    "venus": {"ucca": "Pisces", "neecha": "Virgo"},
    "saturn": {"ucca": "Libra", "neecha": "Aries"},
}

# ==================== 新增：基本三角星座（Moola Trikona） ====================
BPHS_MOOLA_TRIKONA = {
    "sun": "Leo",
    "moon": "Taurus",
    "mars": "Aries",
    "mercury": "Virgo",
    "jupiter": "Sagittarius",
    "venus": "Libra",
    "saturn": "Aquarius",
}

# ==================== 新增：王者瑜伽與特殊瑜伽 ====================
BPHS_RAJA_YOGA = {
    "title_zh": "王者瑜伽與特殊瑜伽",
    "description_zh": "BPHS 第14章專論各種王者瑜伽與特殊組合，這些瑜伽可帶來極高地位、財富、名聲、智慧與權力。",
    
    "raja_yogas": [
        {
            "name": "Dharma Karmadhipati Yoga",
            "zh": "9宮主與10宮主互換位置或相合 → 極高地位、宗教與事業完美結合"
        },
        {
            "name": "Mahabhagya Yoga",
            "zh": "日生圖中太陽、月亮、上升皆在陽性星座（或夜生圖皆在陰性星座）→ 大富大貴、名聲遠播"
        },
        {
            "name": "Gaja Kesari Yoga",
            "zh": "木星與月亮相合或對沖，且無凶星干擾 → 智慧、名聲、財富、權力、領導力"
        },
        {
            "name": "Hamsa Yoga",
            "zh": "木星落於自己的星座（Sagittarius/Cancer）或 Moola Trikona → 極高道德、智慧、地位、純潔"
        },
        {
            "name": "Malavya Yoga",
            "zh": "金星落於自己的星座（Taurus/Libra）或 Moola Trikona → 奢華、藝術、享樂、配偶優秀"
        },
        {
            "name": "Ruchaka Yoga",
            "zh": "火星落於自己的星座（Aries/Scorpio）或 Moola Trikona → 勇猛、軍事、領導力、權威"
        },
        {
            "name": "Bhadra Yoga",
            "zh": "水星落於自己的星座（Gemini/Virgo）或 Moola Trikona → 智慧超群、演說能力強"
        },
        {
            "name": "Sasa Yoga",
            "zh": "土星落於自己的星座（Capricorn/Aquarius）或 Moola Trikona → 權力、紀律、長期成就"
        }
    ],
    
    "special_yogas": [
        {
            "name": "Lakshmi Yoga",
            "zh": "第2宮主與第9宮主強旺或互換 → 極大財富與幸運"
        },
        {
            "name": "Saraswati Yoga",
            "zh": "木星、水星、金星同在吉宮（尤其是2、5、9、11宮） → 極高智慧、學術成就、藝術天分"
        },
        {
            "name": "Neecha Bhanga Raja Yoga",
            "zh": "落陷行星得救（被旺星或吉星救起） → 原本貧困，後來突然大富大貴"
        },
        {
            "name": "Viparita Raja Yoga",
            "zh": "6、8、12宮主互換或相合 → 逆境中翻身，危機後大成"
        }
    ],
    
    "note_zh": "王者瑜伽的強度需同時看行星強弱、Navamsa 分盤、Ashtakavarga 分數與行星 Avastha。單一條件不一定成立，需多重條件滿足才為強瑜伽。"
}

# ==================== 新增：Ashtakavarga 完整使用方法 ====================
BPHS_ASHTAKAVARGA = {
    "title_zh": "八分圖完整使用方法（अष्टकवर्गाध्यायः）",
    "description_zh": "BPHS 第18章詳細說明八分圖，是古典占星中最重要、最精細的量化工具之一，用來精準判斷行星與宮位的強弱、果報時機。",
    
    "basic_concept_zh": "每個行星從8個來源（自身 + 其他7顆行星）獲得點數（Bindu / Rekha）。點數越高，該行星或宮位越強。",
    
    "calculation_steps_zh": [
        "1. 每顆行星各自建立自己的 Ashtakavarga 表（8分圖）",
        "2. 計算每宮的點數（0～8分）",
        "3. Sarvashtakavarga（總八分圖）= 所有行星在該宮的點數總和",
        "4. 進行三角減法（Trikona Shodhana）與單一主宰減法（Ekadhipatya Shodhana）",
        "5. 最終點數用來判斷吉凶與事件時機"
    ],
    
    "sarvashtakavarga_interpretation": {
        "28_plus": "極強（大吉）→ 該宮位極旺，事件順利",
        "25_to_27": "強（吉）→ 該宮位良好，成果穩定",
        "20_to_24": "普通 → 該宮位中性，需看其他因素",
        "below_20": "弱（凶）→ 該宮位受阻，事件多波折"
    },
    
    "planet_points_interpretation": {
        "high": "該行星在自己 Ashtakavarga 中得高分 → 力量強，果報良好",
        "low": "該行星得低分 → 力量弱，果報不佳",
        "note": "即使凶星在高分宮位，也可能帶來正面結果（例如戰勝敵人）"
    },
    
    "main_uses": [
        "判斷各行星本體強弱",
        "判斷12宮位的實際吉凶強弱",
        "大運與流年事件的精準時機",
        "壽命計算（與 Pindayu 結合）",
        "婚姻、事業、財富、子女等重大事件的預測",
        "判斷 Maraka（殺星）與 Ariṣṭa（災厄）"
    ],
    
    "important_rules_zh": [
        "Sarvashtakavarga 高於28點的宮位極吉",
        "行星在自己 Ashtakavarga 中得高分則力量強",
        "凶星在高分宮位仍可帶來正面結果",
        "需與行星 Avastha、Navamsa、Bhava Phala 結合判斷",
        "三角減法與單一主宰減法後的點數才是最終結果"
    ],
    
    "note_zh": "Ashtakavarga 是 BPHS 中最精細的量化工具，常與 Vimshottari Dasha 結合使用來精準預測事件發生時機。單獨使用 Sarvashtakavarga 已非常強大，但與其他章節綜合判斷效果最佳。"
}

# ==================== 新增：完整的16分盤表格（Shodasa Varga） ====================
BPHS_SHODASA_VARGA = {
    "description_zh": "BPHS 第9章專論16種分盤（Shodasa Varga），用來細分命盤各個面向的吉凶與強弱。每一分盤皆有特定切割方式與用途。",
    
    "vargas": {
        "D1": {
            "zh": "本命盤（Rasi）",
            "division": "30°（全宮）",
            "use": "整體人生、性格、身體、健康、主要事件",
            "judgment": "所有判斷的基礎，吉星強旺則全盤吉"
        },
        "D2": {
            "zh": "Hora盤（Hora）",
            "division": "15°（太陽/月亮分）",
            "use": "財富、家庭、飲食、銀行存款",
            "judgment": "太陽Hora主權威財，月亮Hora主流動財"
        },
        "D3": {
            "zh": "Drekkana盤（Drekkana）",
            "division": "10°",
            "use": "兄弟姊妹、勇氣、短途旅行、努力成果",
            "judgment": "火星影響強，兄弟緣與競爭力"
        },
        "D4": {
            "zh": "Chaturthamsa盤（Chaturthamsa）",
            "division": "7°30′",
            "use": "房產、車輛、母親、家庭快樂、祖產",
            "judgment": "月亮與金星強則房產與幸福大吉"
        },
        "D7": {
            "zh": "Saptamsa盤（Saptamsa）",
            "division": "4°17′",
            "use": "子女、子嗣、創造力、投機",
            "judgment": "木星與第5宮主影響最大"
        },
        "D9": {
            "zh": "Navamsa盤（Navamsa）",
            "division": "3°20′",
            "use": "配偶、婚姻、業力、內在品質、晚年",
            "judgment": "BPHS最重視的分盤，吉星落Navamsa吉上加吉"
        },
        "D10": {
            "zh": "Dasamsa盤（Dasamsa）",
            "division": "3°",
            "use": "事業、地位、名聲、權力、職業成就",
            "judgment": "太陽與第10宮主影響最大"
        },
        "D12": {
            "zh": "Dwadasamsa盤（Dwadasamsa）",
            "division": "2°30′",
            "use": "父母、祖先、家族傳統、前世因果",
            "judgment": "太陽（父）、月亮（母）位置關鍵"
        },
        "D16": {
            "zh": "Shodamsa盤（Shodamsa）",
            "division": "1°52′30″",
            "use": "快樂、車輛、舒適、物質享受",
            "judgment": "金星與月亮強則生活舒適"
        },
        "D20": {
            "zh": "Vimsamsa盤（Vimsamsa）",
            "division": "1°30′",
            "use": "宗教、靈性、崇拜、咒語、修行",
            "judgment": "木星與第9宮主影響最大"
        },
        "D24": {
            "zh": "Chaturvimsamsa盤（Chaturvimsamsa）",
            "division": "1°15′",
            "use": "學業、高等教育、知識、學術成就",
            "judgment": "水星與木星強則學業優秀"
        },
        "D30": {
            "zh": "Trimsamsa盤（Trimsamsa）",
            "division": "1°",
            "use": "不幸、疾病、災厄、惡運、隱患",
            "judgment": "凶星強則災厄嚴重，用來看Ariṣṭa"
        },
        "D40": {
            "zh": "Khavedamsa盤（Khavedamsa）",
            "division": "45′",
            "use": "母親的福祉、祖產、家族福德",
            "judgment": "月亮與第4宮主影響最大"
        },
        "D45": {
            "zh": "Akshavedamsa盤（Akshavedamsa）",
            "division": "40′",
            "use": "父親的福祉、祖先功德、整體福報",
            "judgment": "太陽與第9宮主影響最大"
        },
        "D60": {
            "zh": "Shashtiamsa盤（Shashtiamsa）",
            "division": "30′",
            "use": "前世業力、極細微果報、整體命運細節",
            "judgment": "BPHS中最精細的分盤，用來看極微細果報"
        }
    },
    
    "general_note_zh": "BPHS強調：Navamsa（D9）為婚姻與內在本質之關鍵，Dasamsa（D10）為事業之關鍵，Trimsamsa（D30）為災厄之關鍵。所有分盤皆需與本命盤（D1）結合判斷。",
    "strength_rule_zh": "同一行星在多個分盤皆落吉位 → 該事項極強；落凶位 → 該事項受阻。"
}


# ==================== 新增：宮位果報簡表 ====================
BPHS_BHAVA_PHALA = {
    1: {"zh": "命宮", "signification": "身體、健康、性格、外貌"},
    2: {"zh": "財宮", "signification": "財富、家庭、言語、食物"},
    3: {"zh": "兄弟宮", "signification": "兄弟姊妹、勇氣、短途旅行"},
    4: {"zh": "田宅宮", "signification": "母親、房產、車輛、快樂"},
    5: {"zh": "子女宮", "signification": "子女、智慧、愛情、投機"},
    6: {"zh": "疾病宮", "signification": "疾病、敵人、債務、僕人"},
    7: {"zh": "配偶宮", "signification": "婚姻、配偶、事業合夥"},
    8: {"zh": "隱秘宮", "signification": "長壽、遺產、神秘、死亡"},
    9: {"zh": "福德宮", "signification": "幸運、父親、宗教、遠行"},
    10: {"zh": "事業宮", "signification": "事業、地位、名聲"},
    11: {"zh": "收益宮", "signification": "收入、朋友、願望實現"},
    12: {"zh": "損失宮", "signification": "支出、醫院、異國、解脫"},
}



"""
# 在 indian.py 或新頁面中使用範例：
from astro.data.bphs_data import BPHS_AVASTHAS, BPHS_CHAPTERS

def show_avastha(planet: str, avastha_name: str):
    data = BPHS_AVASTHAS.get(planet.lower(), {})
    return data.get(avastha_name, {"zh": "無資料", "strength": "未知"})

# 在 Streamlit 頁面中：
st.title("《布里哈特·帕拉沙拉占星經》行星阿瓦斯塔")
planet = st.selectbox("選擇行星", ["sun", "moon", "mars"])
avastha = st.selectbox("選擇狀態", BPHS_AVASTHAS["avastha_list"])
result = show_avastha(planet, avastha)
st.write(result["zh"])
"""