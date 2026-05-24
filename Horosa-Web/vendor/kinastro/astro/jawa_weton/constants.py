"""
爪哇 Weton / Primbon 常量定義 (Constants for Javanese Weton/Primbon System)

嚴格依照古典 Primbon Betaljemur Adammakna 的規則硬編碼所有數值，
包含 Saptawara、Pancawara Neptu 表、35 種 Weton 詳解、
合婚計算表，以及擇日活動建議。

古法依據：
  - Primbon Betaljemur Adammakna (詳盡版)
  - Primbon Kanjeng Sunan Kalijaga
  - Serat Centhini
"""

from datetime import date

# ============================================================
# 計算基準日 (Epoch)
# 已知：2000 年 1 月 1 日（星期六，Sabtu）= Pasaran: Legi（index 0）
# 此基準日已透過多個爪哇曆法工具交叉驗證
# ============================================================
PASARAN_EPOCH_DATE = date(2000, 1, 1)
PASARAN_EPOCH_INDEX = 0   # Legi = index 0


# ============================================================
# Saptawara（七曜 / 七日週期）— 爪哇語星期名稱與 Neptu
# 順序：週日(Minggu)→週六(Sabtu)，對應 Python isoweekday() % 7
# 古法依據：Primbon — Saptawara Neptu 表
# ============================================================
SAPTAWARA = [
    # (名稱, Neptu, 中文, 梵語根源, 主宰神明, 顏色象徵)
    ("Minggu",  5,  "週日", "Aditya（太陽神）", "Bathara Surya",  "紅色"),
    ("Senin",   4,  "週一", "Soma（月神）",     "Bathara Candra", "黃色"),
    ("Selasa",  3,  "週二", "Anggara（火神）",  "Bathara Anggara","Merah Muda（粉紅）"),
    ("Rabu",    7,  "週三", "Budha（水神）",    "Bathara Wisnu",  "Hitam（黑色）"),
    ("Kamis",   8,  "週四", "Wrespati（木神）", "Bathara Guru",   "Kuning（黃色）"),
    ("Jumat",   6,  "週五", "Sukra（金神）",    "Bathara Indra",  "Biru（藍色）"),
    ("Sabtu",   9,  "週六", "Tumpak（土神）",   "Bathara Yama",   "Ungu（紫色）"),
]

# 快速查詢字典
SAPTAWARA_NEPTU = {row[0]: row[1] for row in SAPTAWARA}


# ============================================================
# Pancawara / Pasaran（五曜 / 五日市集週期）— 名稱與 Neptu
# 順序：Legi(0) → Kliwon(4)
# 古法依據：Primbon — Pancawara Urip / Neptu 表
# ============================================================
PANCAWARA = [
    # (名稱, Neptu, 中文含義, 方位, 主宰神明, 顏色象徵)
    ("Legi",   5, "甜美 / 清晨", "Timur（東）",    "Bathara Wisnu",  "Putih（白色）"),
    ("Pahing", 9, "苦澀 / 南方", "Selatan（南）",   "Bathara Brahma", "Merah（紅色）"),
    ("Pon",    7, "圓滿 / 西方", "Barat（西）",     "Bathara Mahadewa","Kuning（黃色）"),
    ("Wage",   4, "安靜 / 北方", "Utara（北）",     "Bathara Wisnu",  "Hitam（黑色）"),
    ("Kliwon", 8, "中央/神聖",   "Tengah（中央）",  "Bathara Siwa",   "Merah Putih（紅白）"),
]

# 快速查詢字典
PANCAWARA_NEPTU = {row[0]: row[1] for row in PANCAWARA}


# ============================================================
# 合婚 Neptu 相加結果對照表（Primbon 合婚法）
# 以兩人 Weton Neptu 總和 mod 9 (0→9) 取餘數對應
# 古法依據：Primbon Betaljemur Adammakna — 合婚章
# ============================================================
MARRIAGE_COMPAT = {
    # remainder: (名稱, 中文名, 等級, 顏色標記, 描述, 百分比)
    1: (
        "Sri",
        "財富吉祥",
        "🟢 大吉",
        "#2E7D32",
        "Sri 是豐收女神，象徵財富與豐足。此組合帶來財運亨通、家庭和樂。"
        "兩人互補，生活優渥，後代昌盛。",
        88,
    ),
    2: (
        "Lungguh",
        "安定尊榮",
        "🟢 吉",
        "#388E3C",
        "Lungguh 意為「坐穩」，象徵地位穩固、受人尊重。"
        "此組合社會地位較高，婚姻穩定，雖偶有摩擦但不傷大局。",
        78,
    ),
    3: (
        "Gedhong",
        "財倉豐盈",
        "🟢 吉",
        "#43A047",
        "Gedhong 意為「倉庫」，象徵財富積累。"
        "此組合物質生活充裕，善於理財，家業日漸興旺。",
        80,
    ),
    4: (
        "Lara",
        "病痛困擾",
        "🔴 凶",
        "#C62828",
        "Lara 意為「疾病」，象徵健康困擾與痛苦。"
        "此組合需特別注意健康，雙方易有病痛，生活中挑戰較多。建議加強靈性修持。",
        32,
    ),
    5: (
        "Pati",
        "生死離別",
        "🔴 大凶",
        "#B71C1C",
        "Pati 意為「死亡」，是最凶的組合之一。"
        "此組合易有分離、喪偶或大的人生波折。傳統上建議避免此組合或進行特殊儀式化解。",
        15,
    ),
    6: (
        "Satriya",
        "武士之道",
        "🟡 中吉",
        "#F57F17",
        "Satriya 意為「武士」，象徵奮鬥精神。"
        "此組合雙方個性強烈，需要磨合，但最終能相輔相成，共同克服困難。",
        65,
    ),
    7: (
        "Perdana",
        "領袖風範",
        "🟢 吉",
        "#1565C0",
        "Perdana 意為「首相/領袖」，象徵社會地位與聲望。"
        "此組合雙方能在社會上有所成就，婚後生活品質不斷提升。",
        75,
    ),
    8: (
        "Ratu",
        "帝王之尊",
        "🟢 大吉",
        "#4527A0",
        "Ratu 意為「王/女王」，是最高吉祥的組合之一。"
        "此組合威嚴尊貴，生活富裕，社會地位高，受人敬重。婚姻幸福美滿。",
        92,
    ),
    0: (
        "Pesthi",
        "天定良緣",
        "🟢 最吉",
        "#1B5E20",
        "Pesthi 意為「命定/永恆」，是天作之合的象徵。"
        "此組合緣分天定，相濡以沫，白頭偕老。傳統上視為最理想的婚配。",
        95,
    ),
}


# ============================================================
# 35 種 Weton 詳解（Primbon 本命分析）
# 格式：(Weton名, Neptu, 性格特質, 事業傾向, 健康提示, 幸運方位, 幸運色, 適合職業)
# 古法依據：Primbon Betaljemur Adammakna — Watak Weton 章節
# ============================================================
WETON_PROFILES = {
    # ── Minggu (週日, Neptu=5) ──────────────────────────────
    ("Minggu", "Legi"): {
        "neptu": 10,
        "personality": "個性開朗、慷慨大方，天生具有領導魅力。善於社交，樂觀進取，容易贏得他人信任。有時過於自信，需學習傾聽他人意見。",
        "career": "適合從事服務業、公關、政治、藝術創作。具備天生的表演才能，在眾人面前表現出色。",
        "health": "注意心臟與血壓問題。需保持規律作息，避免過度勞累。多進行戶外活動有益健康。",
        "lucky_direction": "東方 (Timur)",
        "lucky_color": "白色、金色",
        "lucky_professions": ["教師", "政治家", "藝術家", "公關顧問", "宗教領袖"],
        "symbol": "☀️",
        "weton_nature": "吉祥",
    },
    ("Minggu", "Pahing"): {
        "neptu": 14,
        "personality": "意志堅定、性格剛強，做事有魄力。雖然個性有些強勢，但內心充滿熱情。善於面對挑戰，不輕易妥協。",
        "career": "適合商業、軍事、競爭性行業。具有企業家精神，適合獨立創業。",
        "health": "注意消化系統與胃部健康。飲食需節制，避免辛辣食物。",
        "lucky_direction": "南方 (Selatan)",
        "lucky_color": "紅色、橙色",
        "lucky_professions": ["企業家", "軍警", "運動員", "廚師", "外科醫生"],
        "symbol": "🔥",
        "weton_nature": "剛強",
    },
    ("Minggu", "Pon"): {
        "neptu": 12,
        "personality": "溫和圓融、善解人意，具有調解爭端的能力。重視家庭，忠誠可靠，朋友緣好。偶爾猶豫不決。",
        "career": "適合外交、調解、諮詢、心理輔導等需要溝通技巧的工作。",
        "health": "注意腎臟與泌尿系統。多喝水，保持心情平靜。",
        "lucky_direction": "西方 (Barat)",
        "lucky_color": "黃色、米白色",
        "lucky_professions": ["外交官", "心理師", "律師", "調解員", "社工"],
        "symbol": "🌕",
        "weton_nature": "和諧",
    },
    ("Minggu", "Wage"): {
        "neptu": 9,
        "personality": "獨立自主、思想獨特，不喜歡受到約束。富有創造力，善於獨立思考。有時顯得孤僻，但內心世界豐富。",
        "career": "適合研究、發明、藝術創作、獨立工作。思維前衛，適合科技創新領域。",
        "health": "注意神經系統與睡眠品質。需要充足休息，避免過度思慮。",
        "lucky_direction": "北方 (Utara)",
        "lucky_color": "黑色、深藍色",
        "lucky_professions": ["研究員", "作家", "程式設計師", "發明家", "哲學家"],
        "symbol": "🌑",
        "weton_nature": "獨立",
    },
    ("Minggu", "Kliwon"): {
        "neptu": 13,
        "personality": "靈性敏感、直覺強烈，具有預感能力。善於與神靈溝通，心靈豐富。對藝術與宗教有深厚興趣。",
        "career": "適合宗教、靈性工作、藝術、療癒師。具有薩滿般的靈性天賦。",
        "health": "注意精神與情緒健康。需要冥想與靜心，避免能量消耗過大。",
        "lucky_direction": "中央 (Tengah)",
        "lucky_color": "紅白相間、紫色",
        "lucky_professions": ["宗教師", "靈性療癒師", "藝術家", "占卜師", "醫師"],
        "symbol": "✨",
        "weton_nature": "靈性",
    },

    # ── Senin (週一, Neptu=4) ──────────────────────────────
    ("Senin", "Legi"): {
        "neptu": 9,
        "personality": "溫柔體貼、感情豐富，對家人充滿愛心。富有同情心，樂於助人。容易受到他人情緒影響。",
        "career": "適合護理、教育、社會工作、藝術創作。善於照顧他人，在服務業中表現出色。",
        "health": "注意情緒波動對身體的影響。需保持心情平靜，避免過度敏感。",
        "lucky_direction": "東方 (Timur)",
        "lucky_color": "白色、銀色",
        "lucky_professions": ["護士", "教師", "社工", "畫家", "音樂家"],
        "symbol": "🌙",
        "weton_nature": "溫柔",
    },
    ("Senin", "Pahing"): {
        "neptu": 13,
        "personality": "熱情活躍、勇於冒險，充滿行動力。具有強烈的求勝慾，不甘示弱。性格直率，有時失於衝動。",
        "career": "適合商業競爭、體育運動、冒險探索。具有開拓精神，適合創業或銷售工作。",
        "health": "注意肌肉與骨骼問題。需適當運動，避免運動傷害。",
        "lucky_direction": "南方 (Selatan)",
        "lucky_color": "紅色、橙色",
        "lucky_professions": ["銷售員", "運動員", "軍人", "消防員", "冒險家"],
        "symbol": "⚡",
        "weton_nature": "活躍",
    },
    ("Senin", "Pon"): {
        "neptu": 11,
        "personality": "聰明機智、善於分析，邏輯思維強。重視學習，知識廣博。有時過於理性，缺乏感性。",
        "career": "適合科學研究、分析、工程、法律。具有嚴謹的邏輯思維，在學術界表現出色。",
        "health": "注意大腦與神經系統。需要充足睡眠，避免思慮過重。",
        "lucky_direction": "西方 (Barat)",
        "lucky_color": "黃色、綠色",
        "lucky_professions": ["科學家", "工程師", "律師", "分析師", "會計師"],
        "symbol": "💡",
        "weton_nature": "智慧",
    },
    ("Senin", "Wage"): {
        "neptu": 8,
        "personality": "安靜內斂、深思熟慮，有自己的節奏。不喜歡喧囂，喜愛平靜的生活。雖然表面冷漠，內心卻充滿熱情。",
        "career": "適合研究、寫作、藝術、靈性工作。在安靜的環境中工作效率最高。",
        "health": "注意腎臟與內分泌系統。需要規律生活，避免熬夜。",
        "lucky_direction": "北方 (Utara)",
        "lucky_color": "黑色、深綠色",
        "lucky_professions": ["研究員", "作家", "僧侶", "哲學家", "圖書館員"],
        "symbol": "🌿",
        "weton_nature": "沉穩",
    },
    ("Senin", "Kliwon"): {
        "neptu": 12,
        "personality": "神秘深邃、靈性敏感，具有超自然直覺。人緣好，容易吸引他人注意。善於感知他人的情感狀態。",
        "career": "適合靈療、諮詢、藝術、宗教工作。具有治癒他人的天賦。",
        "health": "注意睡眠品質與夢境影響。需要靈性淨化，保持能量平衡。",
        "lucky_direction": "中央 (Tengah)",
        "lucky_color": "紫色、白色",
        "lucky_professions": ["靈療師", "心理師", "藝術家", "音樂家", "宗教師"],
        "symbol": "🌊",
        "weton_nature": "神秘",
    },

    # ── Selasa (週二, Neptu=3) ──────────────────────────────
    ("Selasa", "Legi"): {
        "neptu": 8,
        "personality": "勇敢果斷、行動力強，具有戰士精神。不怕困難，敢於冒險。有時衝動，需要學習耐心。",
        "career": "適合武術、競技運動、軍事、緊急救援。在壓力下表現更為出色。",
        "health": "注意頭部與血液循環。避免過激運動，防止受傷。",
        "lucky_direction": "東方 (Timur)",
        "lucky_color": "紅色、白色",
        "lucky_professions": ["軍人", "警察", "消防員", "運動員", "救援人員"],
        "symbol": "⚔️",
        "weton_nature": "勇武",
    },
    ("Selasa", "Pahing"): {
        "neptu": 12,
        "personality": "性格強烈、個人主義，有強烈的自尊心。富有創造力，不循常規。雖然固執，但一旦下定決心，必然貫徹到底。",
        "career": "適合獨立創業、藝術創作、設計。具有獨特的創新思維。",
        "health": "注意消化系統與肝臟健康。飲食需均衡，少食辛辣。",
        "lucky_direction": "南方 (Selatan)",
        "lucky_color": "紅色、金色",
        "lucky_professions": ["設計師", "藝術家", "企業家", "建築師", "廚師長"],
        "symbol": "🌋",
        "weton_nature": "創新",
    },
    ("Selasa", "Pon"): {
        "neptu": 10,
        "personality": "靈活善變、適應力強，能夠在不同環境中生存。具有多方面才能，善於溝通。有時缺乏持久力。",
        "career": "適合外交、銷售、公關、翻譯。善於與各種人打交道。",
        "health": "注意肺部與呼吸系統。多做深呼吸運動，保持良好通風環境。",
        "lucky_direction": "西方 (Barat)",
        "lucky_color": "橙色、黃色",
        "lucky_professions": ["外交官", "銷售員", "翻譯", "記者", "旅行家"],
        "symbol": "🦅",
        "weton_nature": "靈活",
    },
    ("Selasa", "Wage"): {
        "neptu": 7,
        "personality": "謙遜低調、內斂沉穩，不喜歡炫耀。做事踏實，重視細節。雖不善言辭，但行動力強。",
        "career": "適合技術性工作、手工藝、農業、科研。做事認真負責，是優秀的執行者。",
        "health": "注意關節與骨骼健康。需要適當運動，防止過勞。",
        "lucky_direction": "北方 (Utara)",
        "lucky_color": "黑色、棕色",
        "lucky_professions": ["工匠", "農夫", "技術員", "研究員", "建築工人"],
        "symbol": "🔨",
        "weton_nature": "踏實",
    },
    ("Selasa", "Kliwon"): {
        "neptu": 11,
        "personality": "神秘睿智、洞察力強，善於看穿人心。具有強大的意志力和精神力量。在人際關係中影響力大。",
        "career": "適合領導、占卜、靈性指導、戰略規劃。在幕後決策中往往發揮關鍵作用。",
        "health": "注意精神壓力與心理健康。需要定期靜心與冥想。",
        "lucky_direction": "中央 (Tengah)",
        "lucky_color": "黑色、紫色",
        "lucky_professions": ["策略師", "占卜師", "心理諮詢師", "軍師", "靈性導師"],
        "symbol": "🔮",
        "weton_nature": "深邃",
    },

    # ── Rabu (週三, Neptu=7) ──────────────────────────────
    ("Rabu", "Legi"): {
        "neptu": 12,
        "personality": "聰明博學、思維敏捷，具有出色的溝通能力。善於學習新知，知識廣博。有時缺乏決斷力。",
        "career": "適合教育、媒體、寫作、外交。是天生的溝通者和知識傳播者。",
        "health": "注意神經系統與手臂健康。避免資訊過載，需要定期放鬆。",
        "lucky_direction": "東方 (Timur)",
        "lucky_color": "綠色、白色",
        "lucky_professions": ["教授", "作家", "記者", "翻譯家", "外交官"],
        "symbol": "📚",
        "weton_nature": "博學",
    },
    ("Rabu", "Pahing"): {
        "neptu": 16,
        "personality": "威嚴強勢、具有領導魄力，天生的指揮者。在困難情況下仍能保持冷靜。有時過於強勢，需學習包容。",
        "career": "適合政治、管理、軍事、大型企業。在高位上能發揮最大才能。",
        "health": "注意血壓與心臟健康。需要規律運動，控制壓力。",
        "lucky_direction": "南方 (Selatan)",
        "lucky_color": "黑色、紅色",
        "lucky_professions": ["政治家", "高管", "將軍", "法官", "企業總裁"],
        "symbol": "👑",
        "weton_nature": "權威",
    },
    ("Rabu", "Pon"): {
        "neptu": 14,
        "personality": "穩重成熟、責任感強，值得信賴。做事有計劃，重視原則。雖然有時過於嚴肅，但是可靠的夥伴。",
        "career": "適合法律、財務、行政管理。在需要嚴謹邏輯的崗位上表現優秀。",
        "health": "注意脊椎與消化系統。保持良好姿勢，飲食規律。",
        "lucky_direction": "西方 (Barat)",
        "lucky_color": "黑色、灰色",
        "lucky_professions": ["法官", "會計師", "行政主管", "財務顧問", "稽查員"],
        "symbol": "⚖️",
        "weton_nature": "嚴謹",
    },
    ("Rabu", "Wage"): {
        "neptu": 11,
        "personality": "思想深邃、哲學性強，喜歡探討生命意義。具有獨特的世界觀，不隨波逐流。",
        "career": "適合哲學、神學、研究、寫作。善於思考深層問題。",
        "health": "注意眼睛與肝臟健康。減少螢幕時間，多接觸自然。",
        "lucky_direction": "北方 (Utara)",
        "lucky_color": "黑色、深藍色",
        "lucky_professions": ["哲學家", "神學家", "研究員", "作家", "佛法師"],
        "symbol": "🌌",
        "weton_nature": "哲思",
    },
    ("Rabu", "Kliwon"): {
        "neptu": 15,
        "personality": "智慧與靈性兼備，是天生的智者。具有預見未來的能力，洞察力超群。",
        "career": "適合占卜、靈性指導、哲學研究、高等教育。",
        "health": "注意心理與靈性健康的平衡。避免精神過載。",
        "lucky_direction": "中央 (Tengah)",
        "lucky_color": "黑色、金色",
        "lucky_professions": ["哲學家", "占星師", "靈性導師", "大學教授", "傳道者"],
        "symbol": "🌟",
        "weton_nature": "智者",
    },

    # ── Kamis (週四, Neptu=8) ──────────────────────────────
    ("Kamis", "Legi"): {
        "neptu": 13,
        "personality": "仁慈寬厚、具有宗教情懷，善於接受不同文化。天生具有親和力，讓人感到溫暖。",
        "career": "適合宗教、教育、慈善、外交。是天生的和平使者。",
        "health": "注意肝臟與大腿健康。保持樂觀心態，多從事有益身心的活動。",
        "lucky_direction": "東方 (Timur)",
        "lucky_color": "黃色、白色",
        "lucky_professions": ["宗教師", "教育家", "慈善家", "外交官", "法官"],
        "symbol": "🙏",
        "weton_nature": "仁慈",
    },
    ("Kamis", "Pahing"): {
        "neptu": 17,
        "personality": "強大雄偉、天生的領袖，擁有豐富的人生閱歷。具有不可思議的毅力和耐力。",
        "career": "適合高級管理、政治、宗教領袖。在各行各業均可達到頂峰。",
        "health": "注意體重與新陳代謝。需要均衡飲食，適量運動。",
        "lucky_direction": "南方 (Selatan)",
        "lucky_color": "黃色、紅色",
        "lucky_professions": ["政治家", "企業家", "宗教領袖", "教育家", "法官"],
        "symbol": "⛩️",
        "weton_nature": "偉大",
    },
    ("Kamis", "Pon"): {
        "neptu": 15,
        "personality": "成熟穩重、具有智慧，善於在複雜情況中找到解決方案。平衡理性與感性，是出色的協調者。",
        "career": "適合管理、法律、財務、諮詢。能夠在各種環境中發揮才能。",
        "health": "注意腰部與腎臟健康。保持良好的生活習慣。",
        "lucky_direction": "西方 (Barat)",
        "lucky_color": "黃色、綠色",
        "lucky_professions": ["管理顧問", "律師", "財務規劃師", "教育主管", "人力資源"],
        "symbol": "🏛️",
        "weton_nature": "均衡",
    },
    ("Kamis", "Wage"): {
        "neptu": 12,
        "personality": "獨立思考、不受拘束，具有強烈的正義感。雖然行事低調，但在關鍵時刻能挺身而出。",
        "career": "適合社會正義、法律、改革工作。具有改革社會的理想主義。",
        "health": "注意腸胃與消化系統。飲食規律，保持良好排毒習慣。",
        "lucky_direction": "北方 (Utara)",
        "lucky_color": "黃色、黑色",
        "lucky_professions": ["社會活動家", "法律工作者", "記者", "改革家", "教師"],
        "symbol": "⚡",
        "weton_nature": "正義",
    },
    ("Kamis", "Kliwon"): {
        "neptu": 16,
        "personality": "靈性與智慧的最高結合，具有神秘的吸引力。是傳統上最受尊崇的 Weton 之一，被視為具有神聖天賦。",
        "career": "適合靈性導師、高級宗教師、哲學家、治療師。",
        "health": "注意維持靈性與物質生活的平衡。避免過度消耗靈性能量。",
        "lucky_direction": "中央 (Tengah)",
        "lucky_color": "黃色、紫色",
        "lucky_professions": ["高僧", "靈性大師", "哲學家", "宮廷顧問", "神職人員"],
        "symbol": "☸️",
        "weton_nature": "神聖",
    },

    # ── Jumat (週五, Neptu=6) ──────────────────────────────
    ("Jumat", "Legi"): {
        "neptu": 11,
        "personality": "優雅迷人、具有藝術天賦，對美有獨特品味。善於創造和諧的氛圍，人際關係圓融。",
        "career": "適合藝術、時尚、設計、美容。是天生的美學家。",
        "health": "注意腎臟與生殖系統健康。保持情緒穩定，多欣賞美好事物。",
        "lucky_direction": "東方 (Timur)",
        "lucky_color": "藍色、白色",
        "lucky_professions": ["藝術家", "設計師", "時裝設計師", "美容師", "室內設計師"],
        "symbol": "🌸",
        "weton_nature": "優雅",
    },
    ("Jumat", "Pahing"): {
        "neptu": 15,
        "personality": "熱情奔放、感情豐富，具有強烈的感染力。在人際關係中能夠深深打動他人。",
        "career": "適合表演、娛樂、藝術創作、公關。在舞台上或公眾眼前能發光發熱。",
        "health": "注意心臟與血液循環。保持情緒穩定，避免激動。",
        "lucky_direction": "南方 (Selatan)",
        "lucky_color": "藍色、紅色",
        "lucky_professions": ["演員", "歌手", "舞蹈家", "公關", "主持人"],
        "symbol": "💃",
        "weton_nature": "熱情",
    },
    ("Jumat", "Pon"): {
        "neptu": 13,
        "personality": "溫和有禮、善於平衡，具有天生的外交才能。懂得如何讓所有人都感到舒適。",
        "career": "適合外交、人力資源、服務業、藝術。是出色的協調者和和平締造者。",
        "health": "注意荷爾蒙與內分泌平衡。保持規律作息，情緒穩定。",
        "lucky_direction": "西方 (Barat)",
        "lucky_color": "藍色、粉色",
        "lucky_professions": ["外交官", "人力資源", "服務業主管", "婚禮策劃師", "諮詢師"],
        "symbol": "🕊️",
        "weton_nature": "和諧",
    },
    ("Jumat", "Wage"): {
        "neptu": 10,
        "personality": "安靜神秘、具有深刻的內心世界，對藝術與美有獨到見解。雖然低調，但有強大的內在力量。",
        "career": "適合藝術創作、靈性工作、研究。在幕後默默發揮影響力。",
        "health": "注意腎臟與膀胱健康。多喝水，保持內在平靜。",
        "lucky_direction": "北方 (Utara)",
        "lucky_color": "藍色、黑色",
        "lucky_professions": ["詩人", "音樂家", "靈性療癒師", "研究員", "冥想師"],
        "symbol": "🎵",
        "weton_nature": "深邃",
    },
    ("Jumat", "Kliwon"): {
        "neptu": 14,
        "personality": "Jumat Kliwon 是爪哇傳統中最神聖的日子之一！具有超凡的靈性敏感度和神秘力量。對超自然現象特別敏感。",
        "career": "適合靈性工作、藝術、療癒。在爪哇傳統中，此 Weton 者常被視為具有特殊天賦。",
        "health": "注意靈性能量的保護。需要定期進行靈性淨化儀式（Selametan）。",
        "lucky_direction": "中央 (Tengah)",
        "lucky_color": "藍色、紫色",
        "lucky_professions": ["靈性大師", "藝術家", "巫師", "治療師", "宗教師"],
        "symbol": "🔯",
        "weton_nature": "神秘聖日",
    },

    # ── Sabtu (週六, Neptu=9) ──────────────────────────────
    ("Sabtu", "Legi"): {
        "neptu": 14,
        "personality": "勤奮刻苦、有毅力，對目標執著追求。具有強烈的責任感，可靠踏實。雖然嚴肅，但內心溫暖。",
        "career": "適合建築、農業、傳統手工藝、長期規劃工作。善於耕耘，必有收穫。",
        "health": "注意骨骼與牙齒健康。需要充足休息，避免過勞。",
        "lucky_direction": "東方 (Timur)",
        "lucky_color": "紫色、白色",
        "lucky_professions": ["建築師", "農業專家", "傳統工藝師", "醫生", "教師"],
        "symbol": "🏗️",
        "weton_nature": "勤奮",
    },
    ("Sabtu", "Pahing"): {
        "neptu": 18,
        "personality": "Sabtu Pahing 擁有最高的 Neptu 值（18）！威嚴如王，具有強大的個人魅力和領導力。天生的征服者，但也需要學習謙遜。",
        "career": "適合最高級別的領導職位、政治、大型企業。具有帝王般的氣質。",
        "health": "注意高血壓與心臟問題。需要學會放鬆，避免過度緊繃。",
        "lucky_direction": "南方 (Selatan)",
        "lucky_color": "紫色、金色",
        "lucky_professions": ["國家領袖", "大企業家", "軍事將領", "高級法官", "宗教最高領袖"],
        "symbol": "👑",
        "weton_nature": "王者",
    },
    ("Sabtu", "Pon"): {
        "neptu": 16,
        "personality": "沉穩有力、具有深厚的耐力，能夠承受巨大的壓力。重視傳統與規則，是社會的守護者。",
        "career": "適合政府機關、法律、軍事、傳統行業。在穩定的環境中發揮最大效能。",
        "health": "注意關節與骨骼健康。保持規律運動，特別是強化腿部力量。",
        "lucky_direction": "西方 (Barat)",
        "lucky_color": "紫色、黑色",
        "lucky_professions": ["政府官員", "法律人員", "軍官", "傳統文化保護者", "博物館館長"],
        "symbol": "🗿",
        "weton_nature": "穩固",
    },
    ("Sabtu", "Wage"): {
        "neptu": 13,
        "personality": "謹慎低調、深思熟慮，不輕易相信他人。具有強大的自我保護意識，是出色的戰略家。",
        "career": "適合情報、安全、戰略規劃、秘密工作。善於在幕後運籌帷幄。",
        "health": "注意皮膚與排毒系統。保持體內清潔，定期排毒。",
        "lucky_direction": "北方 (Utara)",
        "lucky_color": "紫色、深綠色",
        "lucky_professions": ["情報員", "安全顧問", "戰略家", "偵探", "研究員"],
        "symbol": "🕵️",
        "weton_nature": "謹慎",
    },
    ("Sabtu", "Kliwon"): {
        "neptu": 17,
        "personality": "神聖威嚴、靈性與世俗力量兼備。在爪哇傳統中，此 Weton 被視為具有神靈護佑的特殊人物。",
        "career": "適合靈性領袖、高級宗教師、國家顧問。具有結合世俗與靈性兩界的獨特能力。",
        "health": "注意靈性保護，定期進行淨化儀式（Penanaman）。避免在靈性不穩定時進行重要決定。",
        "lucky_direction": "中央 (Tengah)",
        "lucky_color": "紫色、金色",
        "lucky_professions": ["靈性領袖", "高僧", "宮廷占星師", "國師", "宗教大師"],
        "symbol": "🌠",
        "weton_nature": "神王",
    },
}


# ============================================================
# 今日 Weton 活動建議（依 Neptu 總值判斷吉凶活動）
# 古法依據：Primbon Betaljemur Adammakna — 活動宜忌表
# ============================================================
DAILY_ACTIVITY_ADVICE = {
    # neptu_range (min, max inclusive): {活動: 吉/凶}
    "high_neptu": {  # Neptu >= 15
        "結婚": "🟢 大吉",
        "開業": "🟢 大吉",
        "重要決策": "🟢 吉",
        "出行": "🟢 吉",
        "修房建築": "🟡 可行",
        "治病": "🟡 可行",
        "搬家": "🟡 需擇吉時",
    },
    "mid_neptu": {  # Neptu 10-14
        "結婚": "🟡 可行，宜擇吉時",
        "開業": "🟡 可行",
        "重要決策": "🟢 吉",
        "出行": "🟢 吉",
        "修房建築": "🟢 吉",
        "治病": "🟢 吉",
        "搬家": "🟢 吉",
    },
    "low_neptu": {  # Neptu 7-9
        "結婚": "🔴 需謹慎，宜先進行淨化儀式",
        "開業": "🟡 可行，但需謹慎",
        "重要決策": "🔴 不宜輕舉妄動",
        "出行": "🟡 短途可行",
        "修房建築": "🟡 可行",
        "治病": "🟢 吉（治病求醫）",
        "搬家": "🔴 不宜",
    },
}


# ============================================================
# 特殊 Weton 日（爪哇傳統聖日）
# 古法依據：Primbon Betaljemur Adammakna
# ============================================================
SPECIAL_WETONS = {
    ("Jumat", "Kliwon"): {
        "name": "Jumat Kliwon 聖日",
        "cn": "週五克立旺聖日",
        "description": "爪哇傳統中最神聖的日子，充滿靈性能量。傳統上適合進行靈性修持、冥想、祭祀儀式。",
        "symbol": "🔯",
    },
    ("Selasa", "Kliwon"): {
        "name": "Selasa Kliwon",
        "cn": "週二克立旺",
        "description": "具有強大能量的特殊日子，傳統上適合傳授知識、學習武術或神秘技藝。",
        "symbol": "✨",
    },
    ("Kamis", "Kliwon"): {
        "name": "Kamis Kliwon",
        "cn": "週四克立旺",
        "description": "智慧與靈性的神聖結合日，適合向師長請教、學習、靈修。",
        "symbol": "☸️",
    },
    ("Sabtu", "Kliwon"): {
        "name": "Sabtu Kliwon",
        "cn": "週六克立旺",
        "description": "結合土星力量與靈性中心的強大日子，傳統上用於重要的靈性儀式。",
        "symbol": "🌠",
    },
}


# ============================================================
# 35 天 Weton 循環順序（用於循環圖表顯示）
# 7×5 完整組合，每行一個 Saptawara
# ============================================================
WETON_CYCLE_ORDER = []
for _sw in [row[0] for row in SAPTAWARA]:
    for _pw in [row[0] for row in PANCAWARA]:
        WETON_CYCLE_ORDER.append((_sw, _pw))


# ============================================================
# 文化簡介（用於 UI 顯示）
# ============================================================
CULTURAL_INTRO = {
    "zh": """
### 什麼是 Weton？

**Weton**（wéton / 韋東）是爪哇語，字面意思為「誕生時刻」。
它是爪哇傳統占星系統 **Primbon**（普里姆本）的核心概念，
源自數千年的爪哇宇宙觀與印度占星的融合。

**Weton = Saptawara（七曜）× Pancawara（五曜）**

- **Saptawara**（七日週期）：與梵語星期週期相同，
  對應太陽（日）、月亮（月）、火星（火）、水星（水）、
  木星（木）、金星（金）、土星（土）七個天體。

- **Pancawara / Pasaran**（五日市集週期）：純粹爪哇本土的五日市集循環，
  Legi、Pahing、Pon、Wage、Kliwon 各代表一種能量與市集性格。

七天 × 五天 = **35 天完整 Weton 循環**，每 35 天重複一次。

### Weton 與 Wariga（巴厘 Pawukon）的關係

巴厘島的 **Wariga** 體系與爪哇的 **Weton** 體系同根同源，
均來自古代印度占星與東南亞本土信仰的融合。

主要差異：
- **Weton（爪哇）**：強調個人命運分析（Primbon 性格解讀）與合婚計算
- **Wariga（巴厘）**：更注重儀式曆法，使用 Wuku 210 天大週期

Pancawara（五曜）在兩個體系中完全相同，
只是名稱略有差異（巴厘稱 Panca Wara）。

### Neptu — 爪哇命理數值

每個 Saptawara 與 Pancawara 均有對應的 **Neptu（納圖）**數值，
兩者相加即為個人的 **Weton Neptu**（命理數）。

Neptu 是合婚計算的核心：兩人 Neptu 相加，
對照古典 Primbon 結果，即可得知婚配吉凶。
""",
    "en": """
### What is Weton?

**Weton** (from Javanese "wéton" = moment of birth) is the core concept
of the **Primbon** (Javanese astrological almanac) tradition.
It represents the intersection of two concurrent cycles:

**Weton = Saptawara (7-day week) × Pancawara (5-day market week)**

- **Saptawara**: The 7-day planetary week (Sun, Mon, Tue... Sat)
- **Pancawara / Pasaran**: A native Javanese 5-day market cycle
  (Legi, Pahing, Pon, Wage, Kliwon)

7 × 5 = **35-day Weton cycle**, repeating every 35 days.

### Weton vs Wariga (Balinese Pawukon)

Both systems share common Indo-Javanese roots.
The **Pancawara** cycle is identical in both traditions.
The key difference is scope: Weton emphasizes personal destiny
and marriage compatibility (Primbon), while Wariga focuses on
the full 210-day Pawukon ritual calendar.

### Neptu — The Javanese Numerological Value

Each Saptawara and Pancawara has an assigned **Neptu** value.
Their sum forms your personal **Weton Neptu**, used for
marriage compatibility and auspicious day selection.
""",
}
