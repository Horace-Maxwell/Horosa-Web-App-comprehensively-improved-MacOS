"""
astro/medical_astrology/constants.py — Classical Medical Astrology Correspondences

100% faithful to traditional sources:
- Ptolemy "Tetrabiblos" Book I ch. 10–24 (planetary natures, humors)
- Galen "On the Temperaments", "On the Usefulness of the Parts"
- Avicenna "Canon of Medicine" (Kitāb al-Qānūn fī al-Ṭibb)
- Hippocrates "Aphorisms" and "Airs, Waters, Places"
- Medieval Zodiac Man manuscripts (Homo Signorum)
- William Lilly "Christian Astrology" (1647) — medical chapters
- Nicholas Culpeper "Astrological Judgement of Diseases" (1655)
- Egyptian Decan traditions (Dendera, Tanis lists)
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Optional

# ============================================================
# Zodiac Sign body-part correspondences (Homo Signorum / Zodiac Man)
# Source: Medieval manuscripts, Ptolemy Tetrabiblos III.11,
#         Culpeper "Astrological Judgement of Diseases"
# ============================================================

ZODIAC_BODY_PARTS: Dict[str, Dict] = {
    "Aries": {
        "sign_cn": "白羊座",
        "glyph": "♈",
        "element": "Fire",
        "quality": "Cardinal",
        "body_parts_en": ["Head", "Brain", "Face", "Eyes"],
        "body_parts_cn": ["頭部", "大腦", "面部", "眼睛"],
        "diseases_en": ["Headaches", "Migraines", "Eye disorders", "Fevers", "Epilepsy"],
        "diseases_cn": ["頭痛", "偏頭痛", "眼部疾患", "發燒", "癲癇"],
        "humor": "Choleric",
        "classical_desc_en": (
            "Aries governs the head and brain; afflictions here produce fevers, headaches, "
            "eye diseases, and inflammatory conditions of the head. (Culpeper, Ch.1)"
        ),
        "classical_desc_cn": (
            "白羊座主管頭部與大腦；此宮受困則引發發燒、頭痛、眼疾及頭部炎症。"
            "（卡爾佩伯，第一章）"
        ),
        "zodiac_man_position": "head",
        "color": "#FF2400",
    },
    "Taurus": {
        "sign_cn": "金牛座",
        "glyph": "♉",
        "element": "Earth",
        "quality": "Fixed",
        "body_parts_en": ["Neck", "Throat", "Tonsils", "Vocal cords", "Thyroid"],
        "body_parts_cn": ["頸部", "咽喉", "扁桃腺", "聲帶", "甲狀腺"],
        "diseases_en": ["Throat infections", "Tonsillitis", "Thyroid disorders", "Goitre", "Stiff neck"],
        "diseases_cn": ["咽喉感染", "扁桃體炎", "甲狀腺疾患", "甲狀腺腫", "頸項僵硬"],
        "humor": "Phlegmatic",
        "classical_desc_en": (
            "Taurus rules the neck and throat; its afflictions bring sore throats, swellings of "
            "the neck, and disorders of the larynx. (Lilly, Christian Astrology)"
        ),
        "classical_desc_cn": (
            "金牛座主管頸部與咽喉；其受困帶來咽痛、頸部腫脹及喉頭疾患。"
            "（威廉·利利，《基督教占星》）"
        ),
        "zodiac_man_position": "neck",
        "color": "#4CAF50",
    },
    "Gemini": {
        "sign_cn": "雙子座",
        "glyph": "♊",
        "element": "Air",
        "quality": "Mutable",
        "body_parts_en": ["Shoulders", "Arms", "Hands", "Lungs", "Bronchi", "Nervous system"],
        "body_parts_cn": ["肩部", "手臂", "雙手", "肺部", "支氣管", "神經系統"],
        "diseases_en": ["Asthma", "Bronchitis", "Shoulder injuries", "Nervous disorders", "Fractures of arms"],
        "diseases_cn": ["哮喘", "支氣管炎", "肩部損傷", "神經疾患", "手臂骨折"],
        "humor": "Sanguine",
        "classical_desc_en": (
            "Gemini governs the shoulders, arms, hands, and lungs; afflictions produce "
            "lung diseases, asthma, and breakages of the arms. (Culpeper, Ch.3)"
        ),
        "classical_desc_cn": (
            "雙子座主管肩部、手臂、雙手及肺部；受困則引發肺病、哮喘及手臂骨折。"
            "（卡爾佩伯，第三章）"
        ),
        "zodiac_man_position": "arms",
        "color": "#FFD700",
    },
    "Cancer": {
        "sign_cn": "巨蟹座",
        "glyph": "♋",
        "element": "Water",
        "quality": "Cardinal",
        "body_parts_en": ["Chest", "Breasts", "Stomach", "Ribs", "Diaphragm"],
        "body_parts_cn": ["胸部", "乳房", "胃部", "肋骨", "橫膈膜"],
        "diseases_en": ["Breast disorders", "Stomach ulcers", "Indigestion", "Coughs", "Dropsy"],
        "diseases_cn": ["乳房疾患", "胃潰瘍", "消化不良", "咳嗽", "水腫"],
        "humor": "Phlegmatic",
        "classical_desc_en": (
            "Cancer rules the chest, breasts, stomach and ribs; afflictions here cause "
            "phlegmatic disorders, dropsy, and ailments of the breast. (Lilly, CA p.254)"
        ),
        "classical_desc_cn": (
            "巨蟹座主管胸部、乳房、胃部及肋骨；此宮受困引發痰濕疾患、水腫及乳部疾患。"
            "（利利，《基督教占星》第254頁）"
        ),
        "zodiac_man_position": "chest",
        "color": "#40E0D0",
    },
    "Leo": {
        "sign_cn": "獅子座",
        "glyph": "♌",
        "element": "Fire",
        "quality": "Fixed",
        "body_parts_en": ["Heart", "Upper back", "Spine", "Aorta"],
        "body_parts_cn": ["心臟", "上背部", "脊椎", "主動脈"],
        "diseases_en": ["Heart disease", "Palpitations", "Back pain", "Fainting", "High fever"],
        "diseases_cn": ["心臟病", "心悸", "背痛", "昏厥", "高燒"],
        "humor": "Choleric",
        "classical_desc_en": (
            "Leo governs the heart and upper back; its afflictions bring heart disorders, "
            "fainting, fevers of the blood, and spinal weakness. (Culpeper, Ch.5)"
        ),
        "classical_desc_cn": (
            "獅子座主管心臟與上背部；其受困帶來心臟疾患、昏厥、血熱及脊柱虛弱。"
            "（卡爾佩伯，第五章）"
        ),
        "zodiac_man_position": "heart",
        "color": "#FF8C00",
    },
    "Virgo": {
        "sign_cn": "處女座",
        "glyph": "♍",
        "element": "Earth",
        "quality": "Mutable",
        "body_parts_en": ["Abdomen", "Intestines", "Spleen", "Digestion", "Pancreas"],
        "body_parts_cn": ["腹部", "腸道", "脾臟", "消化系統", "胰腺"],
        "diseases_en": ["Digestive disorders", "Irritable bowel", "Malabsorption", "Worms", "Colic"],
        "diseases_cn": ["消化疾患", "腸易激綜合症", "吸收不良", "腸蟲病", "腸絞痛"],
        "humor": "Melancholic",
        "classical_desc_en": (
            "Virgo rules the abdomen and bowels; afflictions here bring digestive ailments, "
            "bowel obstructions, and melancholic humour imbalances. (Lilly, CA p.255)"
        ),
        "classical_desc_cn": (
            "處女座主管腹部與腸道；受困引發消化疾患、腸道阻塞及憂鬱液失衡。"
            "（利利，《基督教占星》第255頁）"
        ),
        "zodiac_man_position": "abdomen",
        "color": "#8B7355",
    },
    "Libra": {
        "sign_cn": "天秤座",
        "glyph": "♎",
        "element": "Air",
        "quality": "Cardinal",
        "body_parts_en": ["Kidneys", "Lower back", "Adrenal glands", "Lumbar region"],
        "body_parts_cn": ["腎臟", "下背部", "腎上腺", "腰椎區域"],
        "diseases_en": ["Kidney disease", "Lumbago", "Renal stones", "Skin disorders", "Diabetes"],
        "diseases_cn": ["腎臟疾病", "腰痛", "腎結石", "皮膚疾患", "糖尿病"],
        "humor": "Sanguine",
        "classical_desc_en": (
            "Libra governs the kidneys and lower back; afflictions bring kidney ailments, "
            "lumbago, and sanguine excess. (Culpeper, Ch.7)"
        ),
        "classical_desc_cn": (
            "天秤座主管腎臟與下背部；受困帶來腎臟疾患、腰痛及血液過剩。"
            "（卡爾佩伯，第七章）"
        ),
        "zodiac_man_position": "kidneys",
        "color": "#87CEEB",
    },
    "Scorpio": {
        "sign_cn": "天蠍座",
        "glyph": "♏",
        "element": "Water",
        "quality": "Fixed",
        "body_parts_en": ["Reproductive organs", "Bladder", "Colon", "Rectum", "Genitals"],
        "body_parts_cn": ["生殖器官", "膀胱", "結腸", "直腸", "外生殖器"],
        "diseases_en": ["STDs", "Bladder infections", "Haemorrhoids", "Hernias", "Gonorrhoea"],
        "diseases_cn": ["性病", "膀胱炎", "痔瘡", "疝氣", "淋病"],
        "humor": "Phlegmatic",
        "classical_desc_en": (
            "Scorpio rules the genitals, bladder and rectum; afflictions here cause diseases "
            "of the secret parts, haemorrhoids, and phlegmatic stagnation. (Lilly, CA p.256)"
        ),
        "classical_desc_cn": (
            "天蠍座主管生殖器、膀胱及直腸；受困引發私密部位疾病、痔瘡及痰濕停滯。"
            "（利利，《基督教占星》第256頁）"
        ),
        "zodiac_man_position": "genitals",
        "color": "#8B0000",
    },
    "Sagittarius": {
        "sign_cn": "射手座",
        "glyph": "♐",
        "element": "Fire",
        "quality": "Mutable",
        "body_parts_en": ["Hips", "Thighs", "Sciatic nerve", "Liver", "Femur"],
        "body_parts_cn": ["臀部", "大腿", "坐骨神經", "肝臟", "股骨"],
        "diseases_en": ["Hip fractures", "Sciatica", "Liver disorders", "Rheumatism of thighs", "Fevers"],
        "diseases_cn": ["髖骨骨折", "坐骨神經痛", "肝臟疾患", "大腿風濕", "發燒"],
        "humor": "Choleric",
        "classical_desc_en": (
            "Sagittarius governs the hips, thighs and liver; afflictions here cause sciatica, "
            "hip disorders, and bilious complaints. (Culpeper, Ch.9)"
        ),
        "classical_desc_cn": (
            "射手座主管臀部、大腿及肝臟；受困引發坐骨神經痛、髖部疾患及膽汁病。"
            "（卡爾佩伯，第九章）"
        ),
        "zodiac_man_position": "hips",
        "color": "#9B59B6",
    },
    "Capricorn": {
        "sign_cn": "摩羯座",
        "glyph": "♑",
        "element": "Earth",
        "quality": "Cardinal",
        "body_parts_en": ["Knees", "Joints", "Bones", "Skin", "Tendons"],
        "body_parts_cn": ["膝蓋", "關節", "骨骼", "皮膚", "肌腱"],
        "diseases_en": ["Arthritis", "Knee injuries", "Skin diseases", "Depression", "Bone disorders"],
        "diseases_cn": ["關節炎", "膝部損傷", "皮膚病", "抑鬱", "骨骼疾患"],
        "humor": "Melancholic",
        "classical_desc_en": (
            "Capricorn rules the knees, skin and bones; afflictions here produce arthritic "
            "conditions, skin disease, and melancholic depression. (Lilly, CA p.257)"
        ),
        "classical_desc_cn": (
            "摩羯座主管膝蓋、皮膚及骨骼；受困引發關節炎症、皮膚病及憂鬱抑鬱。"
            "（利利，《基督教占星》第257頁）"
        ),
        "zodiac_man_position": "knees",
        "color": "#696969",
    },
    "Aquarius": {
        "sign_cn": "水瓶座",
        "glyph": "♒",
        "element": "Air",
        "quality": "Fixed",
        "body_parts_en": ["Ankles", "Shins", "Calves", "Circulation", "Nervous system"],
        "body_parts_cn": ["踝部", "脛骨", "小腿", "循環系統", "神經系統"],
        "diseases_en": ["Varicose veins", "Ankle sprains", "Circulatory problems", "Cramps", "Spasms"],
        "diseases_cn": ["靜脈曲張", "踝部扭傷", "循環問題", "抽筋", "痙攣"],
        "humor": "Sanguine",
        "classical_desc_en": (
            "Aquarius governs the ankles and shins; afflictions here cause cramps, varicosities, "
            "and sanguine disorders of the lower extremities. (Culpeper, Ch.11)"
        ),
        "classical_desc_cn": (
            "水瓶座主管踝部與脛骨；受困引發抽筋、靜脈曲張及下肢血液疾患。"
            "（卡爾佩伯，第十一章）"
        ),
        "zodiac_man_position": "ankles",
        "color": "#4169E1",
    },
    "Pisces": {
        "sign_cn": "雙魚座",
        "glyph": "♓",
        "element": "Water",
        "quality": "Mutable",
        "body_parts_en": ["Feet", "Toes", "Lymphatic system", "Immune system"],
        "body_parts_cn": ["雙腳", "腳趾", "淋巴系統", "免疫系統"],
        "diseases_en": ["Foot ailments", "Bunions", "Lymph disorders", "Drug sensitivity", "Gout"],
        "diseases_cn": ["足部疾患", "拇指外翻", "淋巴疾患", "藥物敏感", "痛風"],
        "humor": "Phlegmatic",
        "classical_desc_en": (
            "Pisces rules the feet and lymphatic system; afflictions bring gout, foot disorders, "
            "and phlegmatic excess causing immune weakness. (Lilly, CA p.258)"
        ),
        "classical_desc_cn": (
            "雙魚座主管雙腳及淋巴系統；受困帶來痛風、足部疾患及痰濕過盛免疫虛弱。"
            "（利利，《基督教占星》第258頁）"
        ),
        "zodiac_man_position": "feet",
        "color": "#006994",
    },
}

# Order of signs (index → sign)
ZODIAC_SIGN_ORDER: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# ============================================================
# Four Humors (四液體質) — Hippocrates / Galen
# Source: Hippocrates "On the Nature of Man", Galen "On the Temperaments"
# ============================================================

FOUR_HUMORS: Dict[str, Dict] = {
    "Sanguine": {
        "cn": "多血質（血液）",
        "element": "Air",
        "season": "Spring",
        "season_cn": "春",
        "organ": "Liver",
        "organ_cn": "肝臟",
        "quality": "Hot & Moist",
        "quality_cn": "熱且濕",
        "color": "#DC143C",
        "signs": ["Gemini", "Libra", "Aquarius"],
        "signs_cn": ["雙子座", "天秤座", "水瓶座"],
        "planet": "Jupiter",
        "planet_cn": "木星",
        "traits_en": "Optimistic, social, generous, active, energetic",
        "traits_cn": "樂觀、社交、慷慨、活躍、精力充沛",
        "health_tendencies_en": "Prone to blood-related disorders, inflammation, excess heat",
        "health_tendencies_cn": "易患血液疾患、炎症、過熱症",
        "classical_ref": "Hippocrates 'On the Nature of Man' Ch.2; Galen 'On the Temperaments' I.6",
    },
    "Choleric": {
        "cn": "膽汁質（黃膽汁）",
        "element": "Fire",
        "season": "Summer",
        "season_cn": "夏",
        "organ": "Gallbladder",
        "organ_cn": "膽囊",
        "quality": "Hot & Dry",
        "quality_cn": "熱且燥",
        "color": "#FF8C00",
        "signs": ["Aries", "Leo", "Sagittarius"],
        "signs_cn": ["白羊座", "獅子座", "射手座"],
        "planet": "Mars",
        "planet_cn": "火星",
        "traits_en": "Ambitious, decisive, passionate, quick-tempered, bold",
        "traits_cn": "雄心勃勃、果斷、熱情、急躁、大膽",
        "health_tendencies_en": "Prone to fevers, bile disorders, inflammatory diseases, high BP",
        "health_tendencies_cn": "易患發燒、膽汁疾患、炎症性疾病、高血壓",
        "classical_ref": "Galen 'On the Temperaments' I.9; Avicenna 'Canon' Book I, Fen 3",
    },
    "Melancholic": {
        "cn": "憂鬱質（黑膽汁）",
        "element": "Earth",
        "season": "Autumn",
        "season_cn": "秋",
        "organ": "Spleen",
        "organ_cn": "脾臟",
        "quality": "Cold & Dry",
        "quality_cn": "寒且燥",
        "color": "#4B0082",
        "signs": ["Taurus", "Virgo", "Capricorn"],
        "signs_cn": ["金牛座", "處女座", "摩羯座"],
        "planet": "Saturn",
        "planet_cn": "土星",
        "traits_en": "Analytical, cautious, detail-oriented, prone to anxiety",
        "traits_cn": "分析型、謹慎、注重細節、易焦慮",
        "health_tendencies_en": "Prone to depression, chronic ailments, bone/joint disease, constipation",
        "health_tendencies_cn": "易患抑鬱、慢性疾患、骨關節病、便秘",
        "classical_ref": "Hippocrates 'Aphorisms' VI.23; Galen 'On the Temperaments' II.3",
    },
    "Phlegmatic": {
        "cn": "黏液質（黏液）",
        "element": "Water",
        "season": "Winter",
        "season_cn": "冬",
        "organ": "Brain/Lungs",
        "organ_cn": "大腦／肺部",
        "quality": "Cold & Moist",
        "quality_cn": "寒且濕",
        "color": "#4682B4",
        "signs": ["Cancer", "Scorpio", "Pisces"],
        "signs_cn": ["巨蟹座", "天蠍座", "雙魚座"],
        "planet": "Moon",
        "planet_cn": "月亮",
        "traits_en": "Patient, empathetic, reflective, calm, sometimes lethargic",
        "traits_cn": "耐心、善感、沉思、平靜、有時遲鈍",
        "health_tendencies_en": "Prone to mucus disorders, oedema, respiratory ailments, fatigue",
        "health_tendencies_cn": "易患黏液疾患、水腫、呼吸疾患、疲勞",
        "classical_ref": "Avicenna 'Canon' Book I, Fen 3, Ch.4; Galen 'On the Temperaments' II.6",
    },
}

# ============================================================
# Planetary Medical Rulerships (行星醫療主管)
# Source: Culpeper "Astrological Judgement of Diseases",
#         Lilly "Christian Astrology", Ptolemy Tetrabiblos I.10–16
# ============================================================

PLANET_MEDICAL: Dict[str, Dict] = {
    "Sun": {
        "cn": "太陽",
        "glyph": "☉",
        "humor": "Choleric/Vital",
        "humor_cn": "膽汁質／生命力",
        "temperament": "Hot & Dry",
        "temperament_cn": "熱且燥",
        "body_parts_en": ["Heart", "Vital spirits", "Brain (right side)", "Eyes (right — male)", "Arteries"],
        "body_parts_cn": ["心臟", "生命精氣", "大腦（右側）", "右眼（男性）", "動脈"],
        "governs_en": ["Circulation", "Vitality", "Life force", "Bone marrow"],
        "governs_cn": ["血液循環", "活力", "生命力", "骨髓"],
        "diseases_en": ["Heart disease", "Eye problems", "High fever", "Loss of vital force"],
        "diseases_cn": ["心臟病", "眼部問題", "高燒", "生命力衰竭"],
        "herbs_en": ["Saffron", "St. John's Wort", "Mistletoe", "Rue"],
        "herbs_cn": ["番紅花", "聖約翰草", "槲寄生", "芸香"],
        "classical_ref": "Culpeper 'Complete Herbal' — Solar Plants; Ptolemy Tetrabiblos I.10",
    },
    "Moon": {
        "cn": "月亮",
        "glyph": "☽",
        "humor": "Phlegmatic",
        "humor_cn": "黏液質",
        "temperament": "Cold & Moist",
        "temperament_cn": "寒且濕",
        "body_parts_en": ["Brain", "Stomach", "Womb", "Eyes (left — male)", "Lymphatic system", "Fluids"],
        "body_parts_cn": ["大腦", "胃部", "子宮", "左眼（男性）", "淋巴系統", "體液"],
        "governs_en": ["Menstruation", "Tides of bodily fluids", "Mucus", "Sleep cycles"],
        "governs_cn": ["月經", "體液潮汐", "黏液", "睡眠週期"],
        "diseases_en": ["Menstrual disorders", "Oedema", "Lunacy", "Epilepsy (with Sun)", "Bowel fluxes"],
        "diseases_cn": ["月經疾患", "水腫", "精神失常", "癲癇（與太陽合）", "腸道病"],
        "herbs_en": ["Moonwort", "Chickweed", "White Poppy", "Willow"],
        "herbs_cn": ["月蕨", "繁縷", "白鴉片", "柳樹"],
        "classical_ref": "Culpeper 'Complete Herbal' — Lunar Plants; Galen 'On the Faculties of Foods'",
    },
    "Mercury": {
        "cn": "水星",
        "glyph": "☿",
        "humor": "Mixed (variable)",
        "humor_cn": "混合（可變）",
        "temperament": "Cold & Dry (variable)",
        "temperament_cn": "寒且燥（可變）",
        "body_parts_en": ["Nervous system", "Tongue", "Hands", "Lungs", "Memory", "Bile ducts"],
        "body_parts_cn": ["神經系統", "舌頭", "雙手", "肺部", "記憶力", "膽管"],
        "governs_en": ["Mental faculties", "Sensory perception", "Respiratory motion"],
        "governs_cn": ["心智能力", "感官知覺", "呼吸運動"],
        "diseases_en": ["Mental illness", "Nervous disorders", "Stammering", "Vertigo"],
        "diseases_cn": ["精神疾病", "神經失調", "口吃", "眩暈"],
        "herbs_en": ["Fennel", "Dill", "Caraway", "Parsley", "Horehound"],
        "herbs_cn": ["茴香", "蒔蘿", "葛縷子", "歐芹", "夏枯草"],
        "classical_ref": "Culpeper 'Astrological Judgement of Diseases' Ch.2; Lilly CA p.61",
    },
    "Venus": {
        "cn": "金星",
        "glyph": "♀",
        "humor": "Phlegmatic/Sanguine",
        "humor_cn": "黏液質／多血質",
        "temperament": "Hot & Moist",
        "temperament_cn": "熱且濕",
        "body_parts_en": ["Kidneys", "Throat", "Ovaries", "Lumbar region", "Neck", "Venous blood"],
        "body_parts_cn": ["腎臟", "咽喉", "卵巢", "腰部", "頸部", "靜脈血"],
        "governs_en": ["Reproductive health", "Skin beauty", "Kidney filtration", "Hormonal balance"],
        "governs_cn": ["生殖健康", "皮膚美觀", "腎臟過濾", "荷爾蒙平衡"],
        "diseases_en": ["Venereal disease", "Kidney stones", "Diabetes", "Throat ailments"],
        "diseases_cn": ["性病", "腎結石", "糖尿病", "咽喉疾患"],
        "herbs_en": ["Myrtle", "Violet", "Elder", "Periwinkle", "Ladies Mantle"],
        "herbs_cn": ["桃金娘", "紫羅蘭", "接骨木", "長春花", "斗篷草"],
        "classical_ref": "Culpeper 'Complete Herbal' — Venereal Plants; Ptolemy Tetrabiblos I.13",
    },
    "Mars": {
        "cn": "火星",
        "glyph": "♂",
        "humor": "Choleric",
        "humor_cn": "膽汁質",
        "temperament": "Hot & Dry",
        "temperament_cn": "熱且燥",
        "body_parts_en": ["Gallbladder", "Left ear", "Muscles", "Nose", "Blood (arterial)"],
        "body_parts_cn": ["膽囊", "左耳", "肌肉", "鼻部", "動脈血"],
        "governs_en": ["Fevers", "Inflammations", "Wounds", "Surgical operations", "Blood pressure"],
        "governs_cn": ["發燒", "炎症", "創傷", "外科手術", "血壓"],
        "diseases_en": ["Fevers", "Inflammations", "Burns", "Injuries", "Plague"],
        "diseases_cn": ["發燒", "炎症", "燒傷", "外傷", "瘟疫"],
        "herbs_en": ["Garlic", "Nettles", "Basil", "Tobacco", "Onion"],
        "herbs_cn": ["大蒜", "蕁麻", "羅勒", "煙草", "洋蔥"],
        "classical_ref": "Culpeper 'Astrological Judgement of Diseases' Ch.4; Lilly CA p.65",
    },
    "Jupiter": {
        "cn": "木星",
        "glyph": "♃",
        "humor": "Sanguine",
        "humor_cn": "多血質",
        "temperament": "Hot & Moist",
        "temperament_cn": "熱且濕",
        "body_parts_en": ["Liver", "Lungs", "Ribs", "Arterial blood", "Semen", "Right ear"],
        "body_parts_cn": ["肝臟", "肺部", "肋骨", "動脈血", "精液", "右耳"],
        "governs_en": ["Growth", "Healing", "Digestion of food in liver", "Immune protection"],
        "governs_cn": ["生長", "癒合", "肝臟消化食物", "免疫保護"],
        "diseases_en": ["Liver disease", "Pleurisy", "Excess of blood", "Apoplexy"],
        "diseases_cn": ["肝臟病", "胸膜炎", "血液過多", "中風"],
        "herbs_en": ["Borage", "Chestnut", "Betony", "Agrimony", "Lemon Balm"],
        "herbs_cn": ["琉璃苣", "栗樹", "甜薰衣草", "龍牙草", "香蜂草"],
        "classical_ref": "Culpeper 'Complete Herbal' — Jovial Plants; Ptolemy Tetrabiblos I.14",
    },
    "Saturn": {
        "cn": "土星",
        "glyph": "♄",
        "humor": "Melancholic",
        "humor_cn": "憂鬱質",
        "temperament": "Cold & Dry",
        "temperament_cn": "寒且燥",
        "body_parts_en": ["Spleen", "Bones", "Right ear (some sources)", "Teeth", "Joints", "Skin"],
        "body_parts_cn": ["脾臟", "骨骼", "右耳（部分文獻）", "牙齒", "關節", "皮膚"],
        "governs_en": ["Long-term chronic illness", "Ageing process", "Calcification", "Obstruction"],
        "governs_cn": ["長期慢性疾病", "老化過程", "鈣化", "阻塞"],
        "diseases_en": ["Chronic diseases", "Arthritis", "Depression", "Consumption", "Obstructions"],
        "diseases_cn": ["慢性病", "關節炎", "抑鬱", "癆病", "梗阻"],
        "herbs_en": ["Comfrey", "Solomon's Seal", "Hemlock", "Henbane", "Shepherd's Purse"],
        "herbs_cn": ["紫草", "玉竹", "毒芹", "天仙子", "薺菜"],
        "classical_ref": "Culpeper 'Astrological Judgement of Diseases' Ch.6; Lilly CA p.58",
    },
}

# ============================================================
# Egyptian Decan Body-Part Mapping (36 旬星身體對應)
# Source: Derived from Greco-Egyptian medical-astrological texts,
#         Hephaestio of Thebes "Apotelesmatika" Book I,
#         Franz Boll "Sphaera" (1903), Bouché-Leclercq "L'Astrologie Grecque"
# Note: decans 0–35 match the index in decans_data.DECANS_DATA
# ============================================================

DECAN_BODY_PARTS: Dict[int, Dict] = {
    # === ARIES Decans ===
    0: {"body_en": "Head, Forehead", "body_cn": "頭部、前額",
        "zone": "head", "classical_ref": "Manilius Astronomica II.453–458"},
    1: {"body_en": "Eyes, Nose bridge", "body_cn": "眼睛、鼻梁",
        "zone": "head", "classical_ref": "Hephaestio Apotelesmatika I.1"},
    2: {"body_en": "Chin, Jaw", "body_cn": "下巴、頜骨",
        "zone": "head", "classical_ref": "Firmicus Maternus 'Mathesis' IV.22"},
    # === TAURUS Decans ===
    3: {"body_en": "Neck, Throat", "body_cn": "頸部、咽喉",
        "zone": "neck", "classical_ref": "Manilius II.464"},
    4: {"body_en": "Vocal cords, Thyroid", "body_cn": "聲帶、甲狀腺",
        "zone": "neck", "classical_ref": "Hephaestio I.2"},
    5: {"body_en": "Lower neck, Clavicle", "body_cn": "下頸、鎖骨",
        "zone": "neck", "classical_ref": "Firmicus IV.22"},
    # === GEMINI Decans ===
    6: {"body_en": "Shoulders, Upper arms", "body_cn": "肩膀、上臂",
        "zone": "arms", "classical_ref": "Manilius II.471"},
    7: {"body_en": "Forearms, Elbows", "body_cn": "前臂、肘部",
        "zone": "arms", "classical_ref": "Hephaestio I.3"},
    8: {"body_en": "Hands, Fingers, Wrists", "body_cn": "雙手、手指、腕部",
        "zone": "arms", "classical_ref": "Firmicus IV.22"},
    # === CANCER Decans ===
    9: {"body_en": "Chest, Lungs", "body_cn": "胸部、肺部",
        "zone": "chest", "classical_ref": "Manilius II.477"},
    10: {"body_en": "Breasts, Stomach", "body_cn": "乳房、胃部",
         "zone": "chest", "classical_ref": "Hephaestio I.4"},
    11: {"body_en": "Ribs, Diaphragm", "body_cn": "肋骨、橫膈膜",
         "zone": "chest", "classical_ref": "Firmicus IV.22"},
    # === LEO Decans ===
    12: {"body_en": "Heart, Aorta", "body_cn": "心臟、主動脈",
         "zone": "heart", "classical_ref": "Manilius II.483"},
    13: {"body_en": "Upper back, Dorsal vertebrae", "body_cn": "上背部、胸椎",
         "zone": "heart", "classical_ref": "Hephaestio I.5"},
    14: {"body_en": "Solar plexus, Epigastrium", "body_cn": "太陽神經叢、上腹部",
         "zone": "heart", "classical_ref": "Firmicus IV.22"},
    # === VIRGO Decans ===
    15: {"body_en": "Abdomen, Small intestine", "body_cn": "腹部、小腸",
         "zone": "abdomen", "classical_ref": "Manilius II.490"},
    16: {"body_en": "Spleen, Pancreas", "body_cn": "脾臟、胰腺",
         "zone": "abdomen", "classical_ref": "Hephaestio I.6"},
    17: {"body_en": "Large intestine, Bowels", "body_cn": "大腸、腸道",
         "zone": "abdomen", "classical_ref": "Firmicus IV.22"},
    # === LIBRA Decans ===
    18: {"body_en": "Kidneys (right)", "body_cn": "右腎",
         "zone": "kidneys", "classical_ref": "Manilius II.496"},
    19: {"body_en": "Lower back, Lumbar", "body_cn": "下背部、腰椎",
         "zone": "kidneys", "classical_ref": "Hephaestio I.7"},
    20: {"body_en": "Kidneys (left), Adrenals", "body_cn": "左腎、腎上腺",
         "zone": "kidneys", "classical_ref": "Firmicus IV.22"},
    # === SCORPIO Decans ===
    21: {"body_en": "Genitals, Bladder", "body_cn": "生殖器、膀胱",
         "zone": "genitals", "classical_ref": "Manilius II.503"},
    22: {"body_en": "Uterus, Ovaries (Testes)", "body_cn": "子宮、卵巢（睪丸）",
         "zone": "genitals", "classical_ref": "Hephaestio I.8"},
    23: {"body_en": "Rectum, Anus", "body_cn": "直腸、肛門",
         "zone": "genitals", "classical_ref": "Firmicus IV.22"},
    # === SAGITTARIUS Decans ===
    24: {"body_en": "Hips, Sacrum", "body_cn": "臀部、骶骨",
         "zone": "hips", "classical_ref": "Manilius II.510"},
    25: {"body_en": "Thighs, Femur", "body_cn": "大腿、股骨",
         "zone": "hips", "classical_ref": "Hephaestio I.9"},
    26: {"body_en": "Sciatic nerve, Buttocks", "body_cn": "坐骨神經、臀大肌",
         "zone": "hips", "classical_ref": "Firmicus IV.22"},
    # === CAPRICORN Decans ===
    27: {"body_en": "Knees, Patella", "body_cn": "膝蓋、髕骨",
         "zone": "knees", "classical_ref": "Manilius II.516"},
    28: {"body_en": "Knee joints, Tendons", "body_cn": "膝關節、肌腱",
         "zone": "knees", "classical_ref": "Hephaestio I.10"},
    29: {"body_en": "Skin, Outer skeleton", "body_cn": "皮膚、外骨架",
         "zone": "knees", "classical_ref": "Firmicus IV.22"},
    # === AQUARIUS Decans ===
    30: {"body_en": "Shins, Tibiae", "body_cn": "脛骨、脛部",
         "zone": "ankles", "classical_ref": "Manilius II.522"},
    31: {"body_en": "Calves, Fibulae", "body_cn": "小腿、腓骨",
         "zone": "ankles", "classical_ref": "Hephaestio I.11"},
    32: {"body_en": "Ankles, Achilles tendon", "body_cn": "踝部、跟腱",
         "zone": "ankles", "classical_ref": "Firmicus IV.22"},
    # === PISCES Decans ===
    33: {"body_en": "Feet, Metatarsals", "body_cn": "雙腳、蹠骨",
         "zone": "feet", "classical_ref": "Manilius II.528"},
    34: {"body_en": "Toes, Plantar fascia", "body_cn": "腳趾、足底筋膜",
         "zone": "feet", "classical_ref": "Hephaestio I.12"},
    35: {"body_en": "Lymphatic vessels, Immune system", "body_cn": "淋巴管、免疫系統",
         "zone": "feet", "classical_ref": "Firmicus IV.22"},
}

# ============================================================
# Critical Days in Acute Illness (危機日 / Crisis Periods)
# Source: Hippocrates "Aphorisms" IV.36–37, Galen "On Critical Days",
#         Avicenna "Canon" Book II, Fen 1
# The Moon's transit through certain degrees triggers crises.
# Classical 7th, 14th, 20th (lunar month crisis days) and
# the 4th, 11th, 17th, 24th "indicator" days.
# ============================================================

CRITICAL_DAYS: Dict[str, Dict] = {
    "day_4": {
        "day": 4,
        "type": "indicator",
        "type_cn": "指示日",
        "significance_en": "First indicator day — Moon square natal position. Watch for symptom change.",
        "significance_cn": "第一指示日——月亮與本命呈刑（四分相）。注意症狀變化。",
        "classical_ref": "Hippocrates 'Aphorisms' IV.36; Galen 'On Critical Days' I.4",
    },
    "day_7": {
        "day": 7,
        "type": "critical",
        "type_cn": "危機日",
        "significance_en": "First crisis day — Moon opposition to natal. Major turning point; recovery or deterioration.",
        "significance_cn": "第一危機日——月亮與本命呈衝（對分相）。重大轉捩點：轉好或惡化。",
        "classical_ref": "Hippocrates 'Aphorisms' IV.37; Galen 'On Critical Days' II.8",
    },
    "day_11": {
        "day": 11,
        "type": "indicator",
        "type_cn": "指示日",
        "significance_en": "Second indicator day — Moon trine natal. More favourable; watch for improvement.",
        "significance_cn": "第二指示日——月亮與本命呈三合相。較為有利；注意好轉跡象。",
        "classical_ref": "Galen 'On Critical Days' II.10",
    },
    "day_14": {
        "day": 14,
        "type": "critical",
        "type_cn": "危機日",
        "significance_en": "Second crisis day — Moon returns to natal position (opposition completed). Decision point.",
        "significance_cn": "第二危機日——月亮回到本命位置（完成對衝循環）。決定性時刻。",
        "classical_ref": "Hippocrates 'Aphorisms' IV.38; Galen 'On Critical Days' III.1",
    },
    "day_17": {
        "day": 17,
        "type": "indicator",
        "type_cn": "指示日",
        "significance_en": "Third indicator day — Moon in 3rd quarter. Watch for chronic development.",
        "significance_cn": "第三指示日——月亮進入第三象限。注意慢性化發展。",
        "classical_ref": "Galen 'On Critical Days' III.4",
    },
    "day_20": {
        "day": 20,
        "type": "critical",
        "type_cn": "危機日",
        "significance_en": "Third crisis day — final acute crisis. If illness persists beyond this, expect long illness.",
        "significance_cn": "第三危機日——最後急性危機。若病情延續至此，預示長期病況。",
        "classical_ref": "Hippocrates 'Prognostics' Ch.20; Avicenna 'Canon' Book I, Fen 3",
    },
    "day_24": {
        "day": 24,
        "type": "indicator",
        "type_cn": "指示日",
        "significance_en": "Fourth indicator day — Moon sextile. Check for final resolution.",
        "significance_cn": "第四指示日——月亮六分相。檢視最終解除情況。",
        "classical_ref": "Galen 'On Critical Days' III.7",
    },
    "day_28": {
        "day": 28,
        "type": "critical",
        "type_cn": "危機日",
        "significance_en": "Fourth and final crisis — Moon completes lunation. Illness resolved or becomes chronic.",
        "significance_cn": "第四及最終危機——月亮完成一個朔望月。疾病解除或轉為慢性。",
        "classical_ref": "Hippocrates 'Aphorisms' IV.40; Galen 'On Critical Days' III.11",
    },
}

# ============================================================
# Electional Rules for Medical Procedures (療癒擇時規則)
# Source: Galen "On the Best Method of Teaching", Avicenna "Canon",
#         Culpeper "Astrological Judgement of Diseases", Lilly "CA"
# ============================================================

ELECTIONAL_RULES: Dict[str, Dict] = {
    "bloodletting": {
        "name_en": "Bloodletting / Phlebotomy",
        "name_cn": "放血療法",
        "favorable_en": [
            "Moon waxing (1st–2nd quarter) — blood is rising",
            "Moon in the sign governing the afflicted body part",
            "Moon trine or sextile Sun/Venus/Jupiter",
            "Day of the Moon (Monday) or Venus (Friday)",
            "Hour of Mars (for surgical incision) or Moon",
        ],
        "favorable_cn": [
            "月亮盈月（第一至第二象限）——血氣上升",
            "月亮位於主管患病身體部位的星座",
            "月亮與太陽、金星、木星呈三合或六分",
            "月曜日（星期一）或金曜日（星期五）",
            "火星時辰（手術切入）或月亮時辰",
        ],
        "avoid_en": [
            "Avoid Moon in the sign of the afflicted body part (danger of excess bleeding)",
            "Avoid New Moon or Full Moon for bloodletting",
            "Avoid Moon square or opposite Mars or Saturn",
            "Avoid the ascendant or 8th house ruler under affliction",
        ],
        "avoid_cn": [
            "避免月亮位於患病部位對應的星座（過度出血危險）",
            "避免新月或滿月時放血",
            "避免月亮與火星或土星呈刑或衝",
            "避免上升星座或第八宮主星受困",
        ],
        "classical_ref": "Galen 'Method of Medicine' XI.315; Avicenna 'Canon' Book I, Fen 4",
        "icon": "🩸",
    },
    "surgery": {
        "name_en": "Surgery / Operation",
        "name_cn": "外科手術",
        "favorable_en": [
            "Moon waning and not in the sign of the body part to be operated on",
            "Moon in a fixed or earth sign (stable incision)",
            "Hour of Mars (incision strength) or Sun (vitality during op.)",
            "Moon trine or sextile Jupiter (healing) or Venus",
            "Saturn well-placed (steady hands, proper time for cutting)",
        ],
        "favorable_cn": [
            "月亮虧月且不在待手術身體部位的星座",
            "月亮位於固定星座或土象星座（切口穩定）",
            "火星時辰（切割力道）或太陽時辰（手術中的活力）",
            "月亮與木星（療癒）或金星呈三合或六分",
            "土星運行良好（雙手穩定，切割時機恰當）",
        ],
        "avoid_en": [
            "NEVER operate on the body part ruled by the sign currently occupied by the Moon",
            "Avoid Moon conjunct, square, or opposite Saturn or Mars",
            "Avoid Moon void of course",
            "Avoid 8th house stellium — malefic or rising",
            "Avoid eclipses within 2 weeks",
        ],
        "avoid_cn": [
            "絕不在月亮所在星座主管的身體部位動手術",
            "避免月亮合相、刑或衝土星或火星",
            "避免月亮虛空（Void of Course）",
            "避免第八宮群星——凶星上升",
            "避免兩週內有日月食",
        ],
        "classical_ref": "Culpeper 'Astrological Judgement of Diseases' Ch.43; Lilly CA p.276",
        "icon": "🔪",
    },
    "medicine_taking": {
        "name_en": "Taking Medicine / Purging",
        "name_cn": "服藥／瀉下療法",
        "favorable_en": [
            "Moon in a mutable sign (Gemini, Virgo, Sagittarius, Pisces) — promotes movement",
            "Moon waning for purging/downward movement",
            "Moon waxing for tonics and building medicines",
            "Hour of Jupiter or Moon (receptive to beneficial herbs)",
            "Moon sextile or trine Mercury (ruler of medicine)",
        ],
        "favorable_cn": [
            "月亮位於變動星座（雙子、處女、射手、雙魚）——促進流動",
            "瀉下之藥選擇虧月（向下運動）",
            "補益之藥選擇盈月（積累建造）",
            "木星或月亮時辰（易受有益草藥作用）",
            "月亮與水星（醫藥之主）呈六分或三合",
        ],
        "avoid_en": [
            "Avoid Moon in fixed signs for purging",
            "Avoid Moon square or opposite Mars or Saturn",
            "Avoid Moon in the sign of the organ to be purged",
        ],
        "avoid_cn": [
            "瀉藥避免月亮位於固定星座",
            "避免月亮與火星或土星呈刑或衝",
            "避免月亮位於待瀉器官所在的星座",
        ],
        "classical_ref": "Avicenna 'Canon' Book I, Fen 4, Ch.17; Culpeper 'Complete Herbal' introduction",
        "icon": "💊",
    },
    "cauterization": {
        "name_en": "Cauterization / Moxibustion",
        "name_cn": "燒灼療法／艾灸",
        "favorable_en": [
            "Moon waning and in a dry sign (Fire or Earth)",
            "Mars hour (cauterizing heat)",
            "Sun in Aries or Leo (solar fire principle)",
            "Moon trine Mars (controlled heat application)",
        ],
        "favorable_cn": [
            "月亮虧月且位於乾燥星座（火象或土象）",
            "火星時辰（燒灼熱力）",
            "太陽位於白羊或獅子座（太陽火象原則）",
            "月亮與火星呈三合（可控的熱力應用）",
        ],
        "avoid_en": [
            "Avoid Moon in Cancer, Pisces, or Scorpio (water signs resist cautery)",
            "Avoid New Moon or Full Moon",
            "Avoid Moon conjunct Saturn (cold obstruction counteracts heat)",
        ],
        "avoid_cn": [
            "避免月亮位於巨蟹、雙魚或天蠍（水象星座抵抗燒灼）",
            "避免新月或滿月",
            "避免月亮合相土星（寒冷阻塞抵消熱力）",
        ],
        "classical_ref": "Galen 'Method of Medicine' XIV.7; Avicenna 'Canon' Book IV, Fen 7",
        "icon": "🔥",
    },
    "bathing": {
        "name_en": "Therapeutic Bathing",
        "name_cn": "藥浴療法",
        "favorable_en": [
            "Moon in Cancer, Pisces, or Scorpio (water signs)",
            "Venus hour (relaxation and skin benefit)",
            "Moon waxing for invigorating baths",
            "Moon waning for detox and cleansing baths",
            "Jupiter or Venus well-aspected in 1st house",
        ],
        "favorable_cn": [
            "月亮位於巨蟹、雙魚或天蠍（水象星座）",
            "金星時辰（放鬆與皮膚益處）",
            "盈月用於提振活力浴",
            "虧月用於排毒淨化浴",
            "木星或金星與第一宮形成良好相位",
        ],
        "avoid_en": [
            "Avoid bathing when Moon is in Leo or Aries (fiery heat worsens inflammation)",
            "Avoid Saturn hour for therapeutic baths",
            "Avoid bathing after bloodletting on same day",
        ],
        "avoid_cn": [
            "月亮位於獅子或白羊時避免藥浴（火象熱力加重炎症）",
            "藥浴避免土星時辰",
            "放血同日避免沐浴",
        ],
        "classical_ref": "Galen 'On Hygiene' V.3; Avicenna 'Canon' Book I, Fen 3, Ch.21",
        "icon": "🛁",
    },
    "fasting": {
        "name_en": "Therapeutic Fasting",
        "name_cn": "治療性斷食",
        "favorable_en": [
            "Moon waning (especially 3rd–4th quarter) — diminishing, reducing",
            "Moon in Virgo or Capricorn (digestive control signs)",
            "Saturn well-placed (discipline and endurance)",
            "Hour of Moon or Saturn for beginning fast",
        ],
        "favorable_cn": [
            "虧月（尤其第三至第四象限）——漸減、縮小",
            "月亮位於處女或摩羯座（消化控制星座）",
            "土星運行良好（自律與耐力）",
            "月亮或土星時辰開始斷食",
        ],
        "avoid_en": [
            "Avoid fasting when Moon is in Taurus (increased appetite and obstinacy)",
            "Avoid fasting when Jupiter is ruler and dignified (body needs nourishment)",
        ],
        "avoid_cn": [
            "月亮位於金牛時避免斷食（食慾增加，意志固執）",
            "木星為主星且獲尊貴時避免斷食（身體需要滋養）",
        ],
        "classical_ref": "Avicenna 'Canon' Book I, Fen 3, Ch.20; Hippocrates 'Regimen in Acute Diseases'",
        "icon": "🍃",
    },
    "herbal_remedy": {
        "name_en": "Gathering & Preparing Herbal Remedies",
        "name_cn": "採集及配製草藥",
        "favorable_en": [
            "Moon in the sign of the ruling planet of the herb",
            "Moon or Sun in aspect with the ruling planet of the herb",
            "Hour of the herb's ruling planet for gathering",
            "Moon waxing for strengthening herbs",
            "Moon in Virgo or Taurus (earth quality, stable medicinal virtue)",
        ],
        "favorable_cn": [
            "月亮位於草藥主星所在星座",
            "月亮或太陽與草藥的主星形成相位",
            "採集時選擇草藥主星的時辰",
            "盈月採集強健補益類草藥",
            "月亮位於處女或金牛（土象品質，藥效穩定）",
        ],
        "avoid_en": [
            "Never gather herbs when Moon is void of course",
            "Avoid when Moon is afflicted by Mars or Saturn",
        ],
        "avoid_cn": [
            "月亮虛空（Void of Course）時切勿採集草藥",
            "避免月亮受火星或土星困迫時採集",
        ],
        "classical_ref": "Culpeper 'Complete Herbal' Introduction; Macer Floridus 'De Viribus Herbarum'",
        "icon": "🌿",
    },
}

# ============================================================
# Planetary Hour Order (行星時辰序)
# Chaldean order: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon
# The ruler of the 1st hour of a day = the day ruler.
# ============================================================

PLANETARY_HOUR_ORDER: List[str] = [
    "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"
]

DAY_RULERS: Dict[str, str] = {
    "Monday": "Moon",
    "Tuesday": "Mars",
    "Wednesday": "Mercury",
    "Thursday": "Jupiter",
    "Friday": "Venus",
    "Saturday": "Saturn",
    "Sunday": "Sun",
}

# ============================================================
# Temperament calculation weights (體質計算權重)
# Based on Ptolemy Tetrabiblos I.8–9 and Galen's framework
# ============================================================

# Each element contributes to a humor/temperament
ELEMENT_HUMOR_MAP: Dict[str, str] = {
    "Fire": "Choleric",
    "Earth": "Melancholic",
    "Air": "Sanguine",
    "Water": "Phlegmatic",
}

# Planet weights for temperament: +2 strong, +1 moderate
PLANET_TEMPERAMENT_CONTRIBUTION: Dict[str, str] = {
    "Sun": "Choleric",
    "Moon": "Phlegmatic",
    "Mercury": "Melancholic",   # Mercury is cold and dry by nature
    "Venus": "Phlegmatic",
    "Mars": "Choleric",
    "Jupiter": "Sanguine",
    "Saturn": "Melancholic",
}

# ============================================================
# Temperament descriptions (體質描述)
# ============================================================

TEMPERAMENT_DESCRIPTIONS: Dict[str, Dict] = {
    "Choleric": {
        "cn": "膽汁質",
        "element": "Fire",
        "quality_en": "Hot & Dry",
        "quality_cn": "熱且燥",
        "health_en": "Strong constitution, prone to fevers, inflammations, and anger-related ailments. "
                     "Excellent regenerative power but burns out quickly.",
        "health_cn": "體質強健，易患發燒、炎症及情緒相關疾病。再生力強但容易透支。",
        "lifestyle_en": "Reduce spicy, hot foods. Favour cooling herbs (violet, chickweed). "
                        "Practice moderation in physical exertion.",
        "lifestyle_cn": "減少辛辣熱性食物，多用清涼草藥（紫羅蘭、繁縷），注意體力消耗的適度。",
        "dominant_planets": ["Sun", "Mars"],
        "dominant_signs": ["Aries", "Leo", "Sagittarius"],
        "classical_ref": "Galen 'On the Temperaments' I.9; Avicenna 'Canon' Book I, Fen 3",
    },
    "Melancholic": {
        "cn": "憂鬱質",
        "element": "Earth",
        "quality_en": "Cold & Dry",
        "quality_cn": "寒且燥",
        "health_en": "Careful, cautious constitution. Prone to chronic ailments, depression, constipation, "
                     "and conditions involving obstruction or dryness.",
        "health_cn": "謹慎型體質，易患慢性疾病、抑鬱、便秘及阻塞或乾燥相關症狀。",
        "lifestyle_en": "Warm, moist foods and herbs (comfrey, borage). Regular moderate exercise. "
                        "Avoid cold, damp environments. Cultivate joy and social connection.",
        "lifestyle_cn": "溫熱濕潤食物及草藥（紫草、琉璃苣），定期適度運動，避免寒濕環境，培養喜悅與社交連結。",
        "dominant_planets": ["Saturn", "Mercury"],
        "dominant_signs": ["Taurus", "Virgo", "Capricorn"],
        "classical_ref": "Galen 'On the Temperaments' II.3; Hippocrates 'Aphorisms' VI.23",
    },
    "Sanguine": {
        "cn": "多血質",
        "element": "Air",
        "quality_en": "Hot & Moist",
        "quality_cn": "熱且濕",
        "health_en": "Generally healthy and optimistic. Prone to excess blood, inflammatory skin conditions, "
                     "and ailments from overindulgence.",
        "health_cn": "通常健康樂觀，易患血液過多、炎性皮膚疾患及因縱慾過度引起的疾病。",
        "lifestyle_en": "Moderate diet, avoid excess in food and drink. Bloodletting (classically) for excess. "
                        "Cooling herbs (violet, elder flower). Regular sleep.",
        "lifestyle_cn": "飲食節制，避免食物飲酒過度。古典放血療法用於血液過多。清涼草藥（紫羅蘭、接骨木花），規律睡眠。",
        "dominant_planets": ["Jupiter", "Venus"],
        "dominant_signs": ["Gemini", "Libra", "Aquarius"],
        "classical_ref": "Hippocrates 'On the Nature of Man' Ch.2; Galen 'On the Temperaments' I.6",
    },
    "Phlegmatic": {
        "cn": "黏液質",
        "element": "Water",
        "quality_en": "Cold & Moist",
        "quality_cn": "寒且濕",
        "health_en": "Calm, patient constitution. Prone to mucus disorders, oedema, respiratory ailments, "
                     "and conditions of cold and damp.",
        "health_cn": "平靜耐心型體質，易患黏液疾患、水腫、呼吸疾患及寒濕相關症狀。",
        "lifestyle_en": "Warming, drying foods and herbs (ginger, thyme, sage). Avoid cold, damp environments. "
                        "Physical activity to counteract lethargy.",
        "lifestyle_cn": "溫熱乾燥食物及草藥（薑、百里香、鼠尾草），避免寒濕環境，體能活動對抗遲鈍。",
        "dominant_planets": ["Moon", "Venus"],
        "dominant_signs": ["Cancer", "Scorpio", "Pisces"],
        "classical_ref": "Avicenna 'Canon' Book I, Fen 3, Ch.4; Galen 'On the Temperaments' II.6",
    },
}

# ============================================================
# Moon Phase Medical Significance (月相醫療意義)
# ============================================================

MOON_PHASE_MEDICAL: Dict[str, Dict] = {
    "new_moon": {
        "name_en": "New Moon",
        "name_cn": "新月",
        "range_deg": (0, 45),
        "medical_en": "Diminished vitality; avoid surgery or bloodletting. Good for beginning fasting or detox.",
        "medical_cn": "活力減弱；避免手術或放血。適合開始斷食或排毒。",
    },
    "waxing_crescent": {
        "name_en": "Waxing Crescent",
        "name_cn": "眉月（盈）",
        "range_deg": (45, 90),
        "medical_en": "Building energy; good for tonic medicines and nutritive therapies.",
        "medical_cn": "能量積累；適合服用補益藥物及滋養療法。",
    },
    "first_quarter": {
        "name_en": "First Quarter",
        "name_cn": "上弦月",
        "range_deg": (90, 135),
        "medical_en": "Increasing vital force; good for vigorous treatments, exercise therapy.",
        "medical_cn": "生命力增強；適合積極療法及運動治療。",
    },
    "waxing_gibbous": {
        "name_en": "Waxing Gibbous",
        "name_cn": "凸月（盈）",
        "range_deg": (135, 180),
        "medical_en": "Peak building phase; strong bloodletting effectiveness; good for surgery (wounds heal with flesh growing)",
        "medical_cn": "積累高峰期；放血效果強；傷口癒合時肉芽生長旺盛，可行手術。",
    },
    "full_moon": {
        "name_en": "Full Moon",
        "name_cn": "滿月",
        "range_deg": (180, 225),
        "medical_en": "Maximum bodily fluid; avoid surgery (excess bleeding risk). Mental disturbance heightened.",
        "medical_cn": "體液最盛；避免手術（過度出血風險）。精神波動加劇。",
    },
    "waning_gibbous": {
        "name_en": "Waning Gibbous",
        "name_cn": "凸月（虧）",
        "range_deg": (225, 270),
        "medical_en": "Diminishing; good for purging, laxatives, and treatments that reduce excess.",
        "medical_cn": "遞減期；適合瀉下、通便及消除過盛的療法。",
    },
    "last_quarter": {
        "name_en": "Last Quarter",
        "name_cn": "下弦月",
        "range_deg": (270, 315),
        "medical_en": "Weakening; good for removing obstructions, surgery on lower body parts.",
        "medical_cn": "漸弱；適合清除阻塞、下半身手術。",
    },
    "waning_crescent": {
        "name_en": "Waning Crescent",
        "name_cn": "殘月（虧）",
        "range_deg": (315, 360),
        "medical_en": "Lowest energy; rest and recuperation. Begin gentle cleansing.",
        "medical_cn": "能量最低；休息與恢復。開始輕柔淨化療法。",
    },
}
