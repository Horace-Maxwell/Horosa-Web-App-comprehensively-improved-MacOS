"""
緬甸／撣族 Mahabote 深度占星常量定義
Burmese / Shan Mahabote Astrology — Constants

完整 8 守護星座資料庫，含性格、事業、健康、幸運資訊、化解之道及撣族文化注解。
所有數值依照古典緬甸占星傳承硬編碼，不使用近似公式。

古法依據：
  - Barbara Cameron, *The Little Key* (traditional Mahabote handbook)
  - Traditional Pali texts on Myanmar planetary astrology
  - Shan (Tai) cultural oral traditions
"""

from __future__ import annotations
from typing import Dict, List, Tuple

# ============================================================
# 行星週期（Atar / Dasa）— 七曜大運合計 96 年
# 依照古典 Mahabote 傳承順序
# ============================================================
PLANET_PERIOD_YEARS: Dict[str, int] = {
    "Sun":     6,
    "Moon":    15,
    "Mars":    8,
    "Mercury": 17,
    "Jupiter": 19,
    "Venus":   21,
    "Saturn":  10,
    "Rahu":    0,   # Rahu 者採其底層行星（Mercury）的大運
}

# 7 曜順序（用於大運推排：從出生星起順序 7 週期 = 96 年）
PLANET_SEQUENCE: List[str] = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
]

# ============================================================
# 行星顏色（UI 顯示用）
# ============================================================
PLANET_COLORS: Dict[str, str] = {
    "Sun":     "#FFD700",
    "Moon":    "#C0C0C0",
    "Mars":    "#DC143C",
    "Mercury": "#228B22",
    "Jupiter": "#4169E1",
    "Venus":   "#FF69B4",
    "Saturn":  "#000080",
    "Rahu":    "#556B2F",
}

# ============================================================
# 八宮位定義（Mahabote 8 Houses）
# 格式：(英文名, 緬甸文, 中文名, 英文含義, 詳細描述)
# 順序：Bhin(0) → Kamma(7)
# ============================================================
MAHABOTE_HOUSES: List[Tuple] = [
    (
        "Bhin", "ဘင်", "本命宮", "State of Being",
        "出生狀態，代表此生的起點與本質。此宮主性格基調、天賦潛力。"
    ),
    (
        "Ayu", "အာယု", "壽命宮", "Longevity",
        "壽命與健康。此宮主體能、壽限、生命活力。"
    ),
    (
        "Winya", "ဝိညာဉ်", "意識宮", "Consciousness",
        "精神與意識。此宮主智力、學習能力、精神狀態。"
    ),
    (
        "Kiya", "ကိယာ", "身體宮", "Physical Body",
        "肉體與物質。此宮主身體健康、外貌特徵、物質享受。"
    ),
    (
        "Hein", "ဟိန်း", "權勢宮", "Power / Prosperity",
        "力量與繁榮。此宮主事業成就、社會地位、財富。"
    ),
    (
        "Marana", "မရဏ", "死亡宮", "Death / Decline",
        "衰退與終結。此宮主危機、挑戰、人生低谷。"
    ),
    (
        "Thila", "သီလ", "道德宮", "Virtue / Morality",
        "品德與修為。此宮主道德標準、宗教修行、行善積德。"
    ),
    (
        "Kamma", "ကမ္မ", "業力宮", "Karma / Void",
        "業力與未知。此宮為第八隱藏宮，主前世業報、未解之緣、神秘力量。"
    ),
]

# ============================================================
# 星期名稱
# ============================================================
WEEKDAY_NAMES_EN: List[str] = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday",
]
WEEKDAY_NAMES_CN: List[str] = [
    "星期日", "星期一", "星期二", "星期三",
    "星期四", "星期五", "星期六",
]
WEEKDAY_NAMES_MYANMAR: List[str] = [
    "တနင်္ဂနွေ", "တနင်္လာ", "အင်္ဂါ", "ဗုဒ္ဓဟူး",
    "ကြာသပတေး", "သောကြာ", "စနေ",
]

# ============================================================
# 完整 8 守護星座資料庫 (BIRTH_SIGN_DATA)
#
# 索引：Sunday=0, Monday=1, Tuesday=2, Wednesday AM=3,
#       Wednesday PM / Rahu=4, Thursday=5, Friday=6, Saturday=7
#
# 每條記錄包含：
#   planet_en / planet_cn / planet_myanmar / planet_symbol
#   animal_en / animal_cn / animal_myanmar / animal_emoji
#   direction_en / direction_cn
#   element_en / element_cn
#   lucky_colors / lucky_numbers / lucky_days
#   personality (性格描述)
#   career (事業建議)
#   health (健康提示)
#   love (感情婚姻)
#   remedies (化解之道 / 傳統補救)
#   strengths / weaknesses
#   shan_note (撣族文化注解)
#   fortune (吉凶評級)
# ============================================================
BIRTH_SIGN_DATA: Dict[str, Dict] = {

    # ── 星期日 (Sunday) ── 太陽 / 迦樓羅 ──────────────────────
    "Sunday": {
        "planet_en":       "Sun",
        "planet_cn":       "太陽",
        "planet_myanmar":  "နေ",
        "planet_symbol":   "☉",
        "weekday_idx":     0,
        "weekday_en":      "Sunday",
        "weekday_cn":      "星期日",
        "weekday_myanmar": "တနင်္ဂနွေ",

        "animal_en":       "Garuda",
        "animal_cn":       "迦樓羅",
        "animal_myanmar":  "ဂဠုန်",
        "animal_emoji":    "🦅",

        "direction_en":    "NE",
        "direction_cn":    "東北",
        "element_en":      "Fire",
        "element_cn":      "火",

        "lucky_colors":    ["紅色", "橙色", "金黃色"],
        "lucky_numbers":   [1, 9],
        "lucky_days":      ["星期日", "星期四"],

        "personality": (
            "太陽守護者天生具有王者氣質，自信、慷慨、充滿活力。"
            "他們崇尚榮譽、渴望被認可，且具備強烈的領導欲望。"
            "個性直率、熱情、充滿創造力，但偶爾會顯得傲慢或自我中心。"
            "他們有強烈的道德感，重視公平正義，是天生的保護者。"
        ),
        "strengths": ["領導力強", "自信果斷", "慷慨大方", "創造力佳", "道德感強"],
        "weaknesses": ["易驕傲自大", "固執己見", "需要認可", "較難接受批評"],

        "career": (
            "適合政府官員、企業主管、醫生、法官、演藝人員或任何需要展現權威與領導力的職業。"
            "在創業方面有天分，做事有魄力，能在公眾場合發光發熱。"
            "太陽人在 30 歲後事業運最旺，宜從事管理或決策層工作。"
        ),
        "health": (
            "太陽掌管心臟、眼睛與脊椎。需特別注意高血壓、心臟疾病及視力問題。"
            "炎熱天氣對太陽人影響較大，夏季宜避免過度曝曬。"
            "建議定期做心血管檢查，並保持規律作息。"
        ),
        "love": (
            "感情熱烈、忠誠專一，重視伴侶的尊重與欣賞。"
            "喜歡主導關係，偶爾需要學習傾聽對方。"
            "與月亮（虎）和木星（鼠）守護者最為相配，"
            "與土星（那伽）守護者需較多磨合。"
        ),
        "remedies": (
            "供奉黃金花或向日葵於東北方佛像前；"
            "每週日布施，尤其是食物給老人或兒童；"
            "佩戴紅寶石（Ruby）以增強太陽能量；"
            "誦念太陽咒語（Namo Suryaya）有助消業。"
        ),
        "shan_note": (
            "在撣族（Tai）文化中，迦樓羅（Garuda / 嘎魯達）象徵太陽神鳥，"
            "是王權的守護者。撣族新年（Lern Seign）的東北方旗幡以金紅色為主，"
            "代表太陽能量。撣族命名傳統中，帶有「Sai（男）/ Nang（女）+ 日」的名字，"
            "象徵光明與尊貴。"
        ),
        "fortune":         "吉 (Auspicious)",
    },

    # ── 星期一 (Monday) ── 月亮 / 虎 ──────────────────────────
    "Monday": {
        "planet_en":       "Moon",
        "planet_cn":       "月亮",
        "planet_myanmar":  "လ",
        "planet_symbol":   "☽",
        "weekday_idx":     1,
        "weekday_en":      "Monday",
        "weekday_cn":      "星期一",
        "weekday_myanmar": "တနင်္လာ",

        "animal_en":       "Tiger",
        "animal_cn":       "虎",
        "animal_myanmar":  "ကျား",
        "animal_emoji":    "🐅",

        "direction_en":    "E",
        "direction_cn":    "東",
        "element_en":      "Water",
        "element_cn":      "水",

        "lucky_colors":    ["白色", "銀色", "淡藍色"],
        "lucky_numbers":   [2, 7],
        "lucky_days":      ["星期一", "星期五"],

        "personality": (
            "月亮守護者情感豐富、直覺敏銳、富有同理心。"
            "他們天生具有藝術細胞，對美感有獨特的品味。"
            "個性溫柔、善解人意，是天生的照顧者與和平締造者。"
            "情緒容易受外界影響，需要建立穩定的內心環境。"
            "記憶力強，對過去的情感與事件有深刻印記。"
        ),
        "strengths": ["直覺準確", "情感豐富", "藝術天分", "同理心強", "記憶力佳"],
        "weaknesses": ["情緒起伏大", "易多愁善感", "優柔寡斷", "依賴性較強"],

        "career": (
            "適合藝術、文學、音樂、教育、護理、社會工作或任何需要溝通與關懷的職業。"
            "在創意產業中特別出色，如攝影、設計或詩歌。"
            "月亮人在穩定的環境中工作表現最佳，宜建立長期的職業關係。"
        ),
        "health": (
            "月亮掌管胃部、消化系統與淋巴系統。需注意胃炎、腸胃不適及水腫。"
            "情緒狀態直接影響身體健康，焦慮和壓力容易引發消化問題。"
            "建議養成規律的飲食習慣，避免情緒性暴飲暴食。"
        ),
        "love": (
            "感情細膩、忠誠體貼，非常重視家庭與伴侶關係。"
            "需要安全感與穩定的情感環境。"
            "與太陽（迦樓羅）和金星（天竺鼠）守護者最為和諧，"
            "與火星（獅）守護者需要相互包容。"
        ),
        "remedies": (
            "在月圓之夜向月亮獻上白花或牛奶；"
            "佩戴珍珠或月長石以穩定情緒；"
            "每週一向寺廟供奉白色食物；"
            "修持慈悲觀想（Metta Meditation）以提升月亮能量。"
        ),
        "shan_note": (
            "撣族文化中，虎（Sua / ซือ）是東方守護神獸，象徵勇氣與母性守護。"
            "撣族月亮節（Poi Awk Phansa）對月亮守護者尤為重要，"
            "在此節日放水燈可化解流年阻滯。"
            "撣族占卜傳統中，月亮人宜在東方建屋，臥房床頭朝東。"
        ),
        "fortune":         "吉 (Auspicious)",
    },

    # ── 星期二 (Tuesday) ── 火星 / 獅 ────────────────────────
    "Tuesday": {
        "planet_en":       "Mars",
        "planet_cn":       "火星",
        "planet_myanmar":  "အင်္ဂါ",
        "planet_symbol":   "♂",
        "weekday_idx":     2,
        "weekday_en":      "Tuesday",
        "weekday_cn":      "星期二",
        "weekday_myanmar": "အင်္ဂါ",

        "animal_en":       "Lion",
        "animal_cn":       "獅",
        "animal_myanmar":  "ခြင်္သေ့",
        "animal_emoji":    "🦁",

        "direction_en":    "SE",
        "direction_cn":    "東南",
        "element_en":      "Fire",
        "element_cn":      "火",

        "lucky_colors":    ["紅色", "深橙色", "磚紅色"],
        "lucky_numbers":   [9, 3],
        "lucky_days":      ["星期二", "星期日"],

        "personality": (
            "火星守護者勇猛果敢、充滿行動力。"
            "他們天生是戰士，面對挑戰毫不退縮，具有強烈的競爭意識與求勝欲。"
            "個性直接、坦率，不喜歡迂迴或虛偽。"
            "精力充沛，做事講求效率，是出色的執行者。"
            "需要學習控制怒氣，避免衝動行事。"
        ),
        "strengths": ["勇氣過人", "行動力強", "執行力佳", "坦率直接", "精力充沛"],
        "weaknesses": ["易衝動暴躁", "缺乏耐心", "固執倔強", "易樹敵"],

        "career": (
            "適合軍警、運動員、外科醫生、工程師、消防員或任何需要體力與勇氣的職業。"
            "在競爭激烈的環境中表現出色，如商業談判或法律辯護。"
            "創業潛力強，尤其適合需要開拓新市場的行業。"
        ),
        "health": (
            "火星掌管血液、肌肉與腎上腺。需注意發炎、外傷、血壓問題及燙傷。"
            "過旺的火元素易導致憤怒與焦躁，需透過體育運動釋放能量。"
            "建議定期血液檢查，並學習冥想以平衡火性。"
        ),
        "love": (
            "感情熱烈、激情四射，但也容易因個性強烈產生摩擦。"
            "需要一個能接受直率風格、給予空間的伴侶。"
            "與木星（鼠）和太陽（迦樓羅）守護者較為和諧，"
            "與月亮（虎）守護者需要更多包容與溝通。"
        ),
        "remedies": (
            "每週二向寺廟供奉紅色花卉（如雞冠花）；"
            "佩戴紅珊瑚或紅瑪瑙以緩和火星衝動；"
            "修持特定的慈悲心冥想，以化解火星帶來的憤怒業障；"
            "東南方種植紅花植物可增強正面火星能量。"
        ),
        "shan_note": (
            "在撣族文化中，獅（Singa）象徵南方守護力量，是東南亞皇室的傳統符號。"
            "撣族火星守護者傳統上在男孩出生後第三天行儀式（Poi Sang Long）；"
            "撣族傳統醫療中，火星守護者宜用薑黃系草藥來調和火性，"
            "並避免在南方或東南方動土。"
        ),
        "fortune":         "凶中帶吉 (Mixed)",
    },

    # ── 星期三上午 (Wednesday AM) ── 水星 / 象(有牙) ─────────
    "Wednesday": {
        "planet_en":       "Mercury",
        "planet_cn":       "水星",
        "planet_myanmar":  "ဗုဒ္ဓဟူး",
        "planet_symbol":   "☿",
        "weekday_idx":     3,
        "weekday_en":      "Wednesday",
        "weekday_cn":      "星期三",
        "weekday_myanmar": "ဗုဒ္ဓဟူး",

        "animal_en":       "Tusked Elephant",
        "animal_cn":       "象（有牙）",
        "animal_myanmar":  "ဆင်စွယ်",
        "animal_emoji":    "🐘",

        "direction_en":    "S",
        "direction_cn":    "南",
        "element_en":      "Earth",
        "element_cn":      "土",

        "lucky_colors":    ["綠色", "黃綠色", "青色"],
        "lucky_numbers":   [5, 14],
        "lucky_days":      ["星期三", "星期一"],

        "personality": (
            "水星守護者（有牙象）智識超群、溝通能力出色，天生是學者與溝通者。"
            "思維敏捷、反應快速，善於分析複雜的問題。"
            "多才多藝，對語言、數字和邏輯有特殊天賦。"
            "好奇心旺盛，學習新事物樂此不疲，但有時缺乏持續性。"
            "有牙象象徵智慧與威嚴，象徵受過完整教育的智者。"
        ),
        "strengths": ["智識超群", "溝通能力強", "多才多藝", "分析力佳", "適應力強"],
        "weaknesses": ["優柔寡斷", "過度分析", "容易分心", "可能口無遮攔"],

        "career": (
            "適合教師、作家、記者、律師、翻譯、IT 專業人士或任何需要智識與溝通的職業。"
            "在商業、貿易和仲介行業有突出表現。"
            "水星人在中年（35-45 歲）的事業運最為強旺。"
        ),
        "health": (
            "水星掌管神經系統、呼吸道與手部。需注意神經緊張、焦慮、呼吸道疾病。"
            "過度思考和工作壓力容易導致神經衰弱。"
            "建議練習正念冥想和呼吸練習，有助平衡神經系統。"
        ),
        "love": (
            "感情上重視溝通與心靈契合，需要能夠理解其思維的伴侶。"
            "戀愛期較長，喜歡在充分了解對方後再做決定。"
            "與金星（天竺鼠）和土星（那伽）守護者較為和諧，"
            "與羅睺（無牙象）守護者形成特殊的「自我對話」關係。"
        ),
        "remedies": (
            "每週三向象神（Ganesh）供奉綠葡萄或草藥；"
            "佩戴祖母綠（Emerald）以增強水星智慧；"
            "南方書桌或書房可提升水星學術能量；"
            "誦念智慧咒語（Prajna Paramita）有助提升判斷力。"
        ),
        "shan_note": (
            "撣族文化中，象徵知識與力量的白象是撣族皇族的神聖象徵。"
            "星期三出生的撣族人傳統上被認為適合擔任僧侶、教師或占星師。"
            "撣族新年儀式中，有牙象旗幡象徵佛法傳承，"
            "水星守護者宜在水獺節（Poi Kham）期間許願。"
        ),
        "fortune":         "中性 (Neutral)",
    },

    # ── 星期三下午 (Wednesday PM / Rahu) ── 羅睺 / 象(無牙) ──
    "Rahu": {
        "planet_en":       "Rahu",
        "planet_cn":       "羅睺",
        "planet_myanmar":  "ရာဟု",
        "planet_symbol":   "☊",
        "weekday_idx":     -1,   # 特殊標記
        "weekday_en":      "Wednesday (PM)",
        "weekday_cn":      "星期三（傍晚）",
        "weekday_myanmar": "ဗုဒ္ဓဟူးညနေ",

        "animal_en":       "Tuskless Elephant",
        "animal_cn":       "象（無牙）",
        "animal_myanmar":  "ဆင်",
        "animal_emoji":    "🐘",

        "direction_en":    "SW",
        "direction_cn":    "西南",
        "element_en":      "—",
        "element_cn":      "影 / 暗",

        "lucky_colors":    ["深灰色", "黑色", "深藍色"],
        "lucky_numbers":   [4, 8],
        "lucky_days":      ["星期三", "星期六"],

        "personality": (
            "羅睺守護者（無牙象）生而具有神秘氣質，與命運有著複雜的連結。"
            "他們是深刻的思考者，對靈性、哲學和神秘學有天然的親和力。"
            "無牙象象徵沉默的智慧——雖不如有牙象威猛，卻有其獨特的深邃與韌性。"
            "命運多舛，但每次逆境都能讓他們脫胎換骨。"
            "具有強大的直覺和療癒能力，是天生的治療師和靈性導師。"
        ),
        "strengths": ["靈性敏感", "深邃直覺", "療癒能力", "韌性極強", "神秘洞察力"],
        "weaknesses": ["命途多磨", "易疑神疑鬼", "孤立傾向", "情緒深沉"],

        "career": (
            "適合宗教修行者、占星師、心理治療師、研究員、玄學工作者或醫療行業。"
            "在非主流或邊緣領域往往有意想不到的成就。"
            "羅睺人宜選擇能發揮直覺與靈性洞察力的職業，避免過於規律的辦公室工作。"
        ),
        "health": (
            "羅睺掌管不明疾病、心理健康與過敏反應。需特別注意心理健康、睡眠障礙。"
            "易受到環境毒素或不明原因的健康問題困擾。"
            "建議定期進行靈性淨化（如佛教懺悔儀式），並避免熬夜。"
        ),
        "love": (
            "感情深邃而複雜，往往經歷多次波折才能找到真愛。"
            "需要一個能理解其靈性追求並給予足夠包容的伴侶。"
            "與土星（那伽）和木星（鼠）守護者有特殊的業力連結，"
            "需要透過共同的靈性實踐來加深感情。"
        ),
        "remedies": (
            "每週三下午在寺廟前供奉香蕉或椰子；"
            "佩戴貓眼石（Chrysoberyl Cat's Eye）以化解羅睺業障；"
            "西南方設置佛壇並定期供燈；"
            "持誦《解冤咒》或《羅睺迴向文》以化解業障糾纏。"
        ),
        "shan_note": (
            "在撣族傳統中，羅睺守護者被視為具有特殊業力的人，"
            "撣族薩滿（Mo）常為羅睺守護者進行特別的「解繩儀式」（Khe Sai）。"
            "撣族曆法以日出後 18 小時為一天的星期三界限，"
            "無牙象在撣族文化中象徵沉默的智慧與佛法的守護。"
        ),
        "fortune":         "凶 (Inauspicious)",
    },

    # ── 星期四 (Thursday) ── 木星 / 鼠 ────────────────────────
    "Thursday": {
        "planet_en":       "Jupiter",
        "planet_cn":       "木星",
        "planet_myanmar":  "ကြာသပတေး",
        "planet_symbol":   "♃",
        "weekday_idx":     4,
        "weekday_en":      "Thursday",
        "weekday_cn":      "星期四",
        "weekday_myanmar": "ကြာသပတေး",

        "animal_en":       "Rat",
        "animal_cn":       "鼠",
        "animal_myanmar":  "ကြွက်",
        "animal_emoji":    "🐀",

        "direction_en":    "W",
        "direction_cn":    "西",
        "element_en":      "Air / Wind",
        "element_cn":      "風",

        "lucky_colors":    ["黃色", "金色", "橙黃色"],
        "lucky_numbers":   [3, 12],
        "lucky_days":      ["星期四", "星期二"],

        "personality": (
            "木星守護者是八個星座中最受福澤眷顧的一群。"
            "他們慷慨仁愛、樂觀向上，具有強大的道德感和宗教情懷。"
            "智慧深廣，是天生的導師與智者。"
            "個性寬容、包容力強，能在各種環境中找到和諧之道。"
            "鼠在緬甸文化中象徵機智與生存能力，代表在逆境中找到出路的智慧。"
        ),
        "strengths": ["智慧廣博", "慷慨仁愛", "道德標準高", "樂觀進取", "教學才能"],
        "weaknesses": ["過度樂觀", "奢靡浪費傾向", "缺乏實際", "說教性格"],

        "career": (
            "適合教育、哲學、法律、宗教、醫學或任何服務社會的崇高職業。"
            "在政府、非政府組織或國際機構中表現傑出。"
            "木星人的事業在 40 歲以後往往達到頂峰，晚年更受人尊敬。"
        ),
        "health": (
            "木星掌管肝臟、脂肪代謝與循環系統。需注意肝臟問題、膽固醇及體重管理。"
            "過度飲食和缺乏運動是木星人的主要健康風險。"
            "建議保持均衡飲食，定期進行肝功能檢查，適度運動。"
        ),
        "love": (
            "感情穩定、忠誠度高，重視心靈層面的連結。"
            "是體貼的伴侶和盡責的父母，家庭幸福感強。"
            "與太陽（迦樓羅）和月亮（虎）守護者最為相配，"
            "與水星（有牙象）守護者形成「師生」般的互補關係。"
        ),
        "remedies": (
            "每週四向寺廟供奉黃花和水果；"
            "佩戴黃色藍寶石（Yellow Sapphire）以增強木星福澤；"
            "西方或西北方種植黃色或橙色花卉；"
            "誦念《大吉祥經》（Mahā Maṅgala Sutta）可增強木星加持。"
        ),
        "shan_note": (
            "在撣族文化中，木星（Guru / 大師）是最受尊崇的導師星。"
            "鼠在撣族民間故事中是智慧與機智的象徵，傳說能找到任何問題的解答。"
            "撣族在木星守護者孩子出生時，傳統上為其取帶有「吉祥」（Mangala）含義的名字。"
            "撣曆中的「木星日」（Wan Saoa）是最適合占卜和決策的日子。"
        ),
        "fortune":         "大吉 (Highly Auspicious)",
    },

    # ── 星期五 (Friday) ── 金星 / 天竺鼠 / 豪豬 ───────────────
    "Friday": {
        "planet_en":       "Venus",
        "planet_cn":       "金星",
        "planet_myanmar":  "သောကြာ",
        "planet_symbol":   "♀",
        "weekday_idx":     5,
        "weekday_en":      "Friday",
        "weekday_cn":      "星期五",
        "weekday_myanmar": "သောကြာ",

        "animal_en":       "Guinea Pig / Porcupine",
        "animal_cn":       "天竺鼠 / 豪豬",
        "animal_myanmar":  "ပူးရွှေ",
        "animal_emoji":    "🐹",

        "direction_en":    "NW",
        "direction_cn":    "西北",
        "element_en":      "Water",
        "element_cn":      "水",

        "lucky_colors":    ["粉紅色", "白色", "淡紫色"],
        "lucky_numbers":   [6, 15],
        "lucky_days":      ["星期五", "星期一"],

        "personality": (
            "金星守護者天生具有藝術家的靈魂，對美麗與和諧有敏銳的感知。"
            "他們迷人、親切、善於社交，具有出色的外交手腕。"
            "重視感官享受與生活品質，喜愛藝術、音樂、美食和大自然。"
            "豪豬的刺象徵金星人的雙重性格：表面溫柔，骨子裡有原則和自我保護機制。"
        ),
        "strengths": ["藝術天賦", "外交手腕", "社交能力", "審美品位", "情感細膩"],
        "weaknesses": ["易縱情享樂", "虛榮心強", "優柔寡斷", "過度理想化"],

        "career": (
            "適合藝術家、設計師、音樂家、時尚工作者、外交官、教師或美容行業。"
            "在任何需要審美判斷和人際關係的領域都能發揮所長。"
            "金星人在創意工作上有天生優勢，尤其是 25-35 歲之間的創作最為豐盛。"
        ),
        "health": (
            "金星掌管腎臟、泌尿系統與皮膚。需注意腎臟疾病、皮膚問題及婦科問題（女性）。"
            "過度縱情享樂（美食、酒精）是金星人的主要健康風險。"
            "建議定期做腎功能和皮膚保養，保持適度的運動習慣。"
        ),
        "love": (
            "多情浪漫，重視感情中的儀式感和美感。"
            "是溫柔貼心的伴侶，但也需要伴侶的欣賞與讚美。"
            "與月亮（虎）和水星（有牙象）守護者最為相配，"
            "與火星（獅）守護者的激情組合充滿火花但也有衝突。"
        ),
        "remedies": (
            "每週五向寺廟供奉白色花卉（如茉莉花）；"
            "佩戴鑽石或白色藍寶石以增強金星魅力；"
            "西北方的居室裝飾粉色或白色調有助提升金星運；"
            "修持觀世音菩薩（Quan Yin）法門有助金星守護者開啟慈悲心。"
        ),
        "shan_note": (
            "在撣族文化中，豪豬（Moo Kham）象徵溫柔而有原則的女性力量。"
            "金星守護者在撣族傳統上被視為天生的藝術家和工藝師，"
            "尤其擅長撣族絲織（Sin）和銀器工藝。"
            "撣族慶典中，金星守護者傳統上負責準備儀式用的花卉裝飾。"
        ),
        "fortune":         "吉 (Auspicious)",
    },

    # ── 星期六 (Saturday) ── 土星 / 那伽 / 龍 ─────────────────
    "Saturday": {
        "planet_en":       "Saturn",
        "planet_cn":       "土星",
        "planet_myanmar":  "စနေ",
        "planet_symbol":   "♄",
        "weekday_idx":     6,
        "weekday_en":      "Saturday",
        "weekday_cn":      "星期六",
        "weekday_myanmar": "စနေ",

        "animal_en":       "Naga / Dragon",
        "animal_cn":       "那伽 / 龍",
        "animal_myanmar":  "နဂါး",
        "animal_emoji":    "🐉",

        "direction_en":    "N",
        "direction_cn":    "北",
        "element_en":      "Fire",
        "element_cn":      "火",

        "lucky_colors":    ["深藍色", "黑色", "深紫色"],
        "lucky_numbers":   [8, 17],
        "lucky_days":      ["星期六", "星期三"],

        "personality": (
            "土星守護者是八個星座中最有耐力和毅力的一群。"
            "他們嚴謹、負責、具有強烈的紀律感，對自己和他人都有很高的要求。"
            "那伽（神龍）象徵古老的智慧、水域的神秘力量和業力的守護者。"
            "土星人大器晚成，生命前半段可能充滿挑戰，但後半生往往功成名就。"
            "他們是天生的建設者，能夠將長期願景化為現實。"
        ),
        "strengths": ["毅力卓絕", "責任感強", "深謀遠慮", "自律嚴格", "大器晚成"],
        "weaknesses": ["過於嚴肅", "悲觀傾向", "固執守舊", "對自己要求過高"],

        "career": (
            "適合建築、農業、礦業、考古、政府行政、法律或任何需要長期耐心的職業。"
            "在學術研究、歷史和古典學問方面有深厚造詣。"
            "土星人宜選擇能讓他們發揮長期規劃能力的職業，避免快速致富的冒險行業。"
        ),
        "health": (
            "土星掌管骨骼、關節、牙齒與皮膚老化。需注意關節炎、骨質疏鬆及慢性疾病。"
            "土星人容易因工作過度而忽視身體信號，需注意慢性疲勞。"
            "建議定期補充鈣質和維生素 D，保持適度的戶外活動。"
        ),
        "love": (
            "感情謹慎保守，需要較長的時間建立信任。"
            "一旦承諾，便是極為忠誠和穩定的伴侶。"
            "與木星（鼠）守護者形成「師生」般的互補，"
            "與太陽（迦樓羅）守護者有傳統的「對立而互補」關係。"
        ),
        "remedies": (
            "每週六向寺廟供奉深色花卉或黑豆；"
            "佩戴藍色藍寶石（Blue Sapphire）以與土星達成和諧；"
            "北方設置靜坐角落或佛壇有助提升土星能量；"
            "修持地藏王菩薩（Ksitigarbha）法門有助化解土星業障。"
        ),
        "shan_note": (
            "在撣族文化中，那伽（Naga / ナーガ）是守護水源和大地的聖龍，"
            "是撣族神話中最受尊崇的神獸之一。"
            "土星守護者在撣族傳統上被視為業力重大的智者，"
            "撣族長老（Pho Luang）多出身土星守護者。"
            "撣族曆中，土星日是傳統上最適合獻祭祖先的日子。"
        ),
        "fortune":         "凶中帶吉 (Mixed)",
    },
}

# 便捷映射：weekday_idx → sign key
WEEKDAY_TO_SIGN: Dict[int, str] = {
    0: "Sunday",
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
}

# 行星英文名 → sign key
PLANET_TO_SIGN: Dict[str, str] = {
    "Sun":     "Sunday",
    "Moon":    "Monday",
    "Mars":    "Tuesday",
    "Mercury": "Wednesday",
    "Jupiter": "Thursday",
    "Venus":   "Friday",
    "Saturn":  "Saturday",
    "Rahu":    "Rahu",
}

# ============================================================
# 方位行星對照表（8 方位固定對應）
# 順序：NE → E → SE → S → SW → W → NW → N（順時針）
# ============================================================
DIRECTIONS_8 = [
    {
        "dir_en": "NE", "dir_cn": "東北", "dir_myanmar": "အရှေ့မြောက်",
        "planet": "Sun", "symbol": "☉", "planet_cn": "太陽",
        "weekday_idx": 0, "sign_key": "Sunday",
        "animal": "Garuda", "animal_emoji": "🦅", "animal_cn": "迦樓羅",
        "fortune": "吉",
        "omen_career": "領導力強，適合開創事業，有貴人扶持。",
        "omen_marriage": "婚姻光明，伴侶忠誠，但需避免過於強勢。",
        "omen_health": "精力充沛，心臟與視力需注意保養。",
    },
    {
        "dir_en": "E", "dir_cn": "東", "dir_myanmar": "အရှေ့",
        "planet": "Moon", "symbol": "☽", "planet_cn": "月亮",
        "weekday_idx": 1, "sign_key": "Monday",
        "animal": "Tiger", "animal_emoji": "🐅", "animal_cn": "虎",
        "fortune": "吉",
        "omen_career": "才華橫溢，適合文學、藝術、教育領域。",
        "omen_marriage": "感情豐富，婚姻和諧，但情緒波動需控制。",
        "omen_health": "消化系統與水分代謝需留意，情緒影響健康。",
    },
    {
        "dir_en": "SE", "dir_cn": "東南", "dir_myanmar": "အရှေ့တောင်",
        "planet": "Mars", "symbol": "♂", "planet_cn": "火星",
        "weekday_idx": 2, "sign_key": "Tuesday",
        "animal": "Lion", "animal_emoji": "🦁", "animal_cn": "獅",
        "fortune": "凶中帶吉",
        "omen_career": "勇猛果敢，軍警、運動、競爭型事業有利。",
        "omen_marriage": "性格剛烈，婚姻需忍讓，易有口角衝突。",
        "omen_health": "血液循環與外傷需防範，火氣旺盛。",
    },
    {
        "dir_en": "S", "dir_cn": "南", "dir_myanmar": "တောင်",
        "planet": "Mercury", "symbol": "☿", "planet_cn": "水星",
        "weekday_idx": 3, "sign_key": "Wednesday",
        "animal": "Tusked Elephant", "animal_emoji": "🐘", "animal_cn": "象（有牙）",
        "fortune": "中性",
        "omen_career": "智商高，適合商業、通訊、寫作、學術。",
        "omen_marriage": "善於溝通，但需避免口舌是非影響感情。",
        "omen_health": "神經系統與呼吸道較弱，需防過勞。",
    },
    {
        "dir_en": "SW", "dir_cn": "西南", "dir_myanmar": "အနောက်တောင်",
        "planet": "Rahu", "symbol": "☊", "planet_cn": "羅睺",
        "weekday_idx": -1, "sign_key": "Rahu",
        "animal": "Tuskless Elephant", "animal_emoji": "🐘", "animal_cn": "象（無牙）",
        "fortune": "凶",
        "omen_career": "命運多舛但深具靈性，適合宗教、玄學、醫療。",
        "omen_marriage": "婚姻考驗多，需培養信任與耐心。",
        "omen_health": "體質較弱，需防不明疾病與精神壓力。",
    },
    {
        "dir_en": "W", "dir_cn": "西", "dir_myanmar": "အနောက်",
        "planet": "Jupiter", "symbol": "♃", "planet_cn": "木星",
        "weekday_idx": 4, "sign_key": "Thursday",
        "animal": "Rat", "animal_emoji": "🐀", "animal_cn": "鼠",
        "fortune": "大吉",
        "omen_career": "智慧與福報兼具，適合教育、法律、宗教。",
        "omen_marriage": "婚姻美滿，伴侶賢德，子女孝順。",
        "omen_health": "肝膽系統需注意，整體福壽綿長。",
    },
    {
        "dir_en": "NW", "dir_cn": "西北", "dir_myanmar": "အနောက်မြောက်",
        "planet": "Venus", "symbol": "♀", "planet_cn": "金星",
        "weekday_idx": 5, "sign_key": "Friday",
        "animal": "Guinea Pig", "animal_emoji": "🐹", "animal_cn": "天竺鼠",
        "fortune": "吉",
        "omen_career": "藝術才華出眾，適合設計、音樂、時尚、外交。",
        "omen_marriage": "桃花旺盛，婚姻甜蜜，但需防爛桃花。",
        "omen_health": "腎臟與泌尿系統需注意，享樂過度損健康。",
    },
    {
        "dir_en": "N", "dir_cn": "北", "dir_myanmar": "မြောက်",
        "planet": "Saturn", "symbol": "♄", "planet_cn": "土星",
        "weekday_idx": 6, "sign_key": "Saturday",
        "animal": "Naga", "animal_emoji": "🐉", "animal_cn": "龍/那伽",
        "fortune": "凶中帶吉",
        "omen_career": "刻苦耐勞，大器晚成，適合建築、農業、礦業。",
        "omen_marriage": "婚姻來遲但穩固，需耐心等待良緣。",
        "omen_health": "骨骼與關節需注意，晚年養生重要。",
    },
]

# planet name → direction index in DIRECTIONS_8
PLANET_TO_DIR_IDX: Dict[str, int] = {
    "Sun":     0,
    "Moon":    1,
    "Mars":    2,
    "Mercury": 3,
    "Rahu":    4,
    "Jupiter": 5,
    "Venus":   6,
    "Saturn":  7,
}

# ============================================================
# 合婚相容性表 (Compatibility Matrix)
#
# 8 個星座（Sun/Moon/Mars/Mercury/Rahu/Jupiter/Venus/Saturn）
# 相容性評分：5=非常相配, 4=相配, 3=中性, 2=需努力, 1=困難
#
# 依據古典緬甸 Mahabote 和諧/敵對關係：
#   - 友好 (Maitri): 太陽↔木星, 月亮↔金星, 火星↔太陽, 水星↔金星, 木星↔月亮
#   - 中性 (Sama): 大多數組合
#   - 敵對 (Shatru): 太陽↔土星, 火星↔月亮, 羅睺↔火星
# ============================================================
COMPAT_PLANETS: List[str] = [
    "Sun", "Moon", "Mars", "Mercury", "Rahu", "Jupiter", "Venus", "Saturn"
]

# 0-indexed matrix [row=person1_planet][col=person2_planet]
COMPAT_MATRIX: List[List[int]] = [
    # Sun  Moon Mars Merc Rahu Jupi Venu Satu
    [  5,   4,   4,   3,   2,   5,   3,   1 ],  # Sun
    [  4,   5,   2,   3,   3,   5,   5,   3 ],  # Moon
    [  4,   2,   5,   3,   1,   4,   3,   3 ],  # Mars
    [  3,   3,   3,   5,   3,   4,   5,   4 ],  # Mercury
    [  2,   3,   1,   3,   5,   3,   3,   4 ],  # Rahu
    [  5,   5,   4,   4,   3,   5,   4,   3 ],  # Jupiter
    [  3,   5,   3,   5,   3,   4,   5,   3 ],  # Venus
    [  1,   3,   3,   4,   4,   3,   3,   5 ],  # Saturn
]

COMPAT_LABELS: Dict[int, Tuple[str, str, str]] = {
    5: ("非常相配", "Pesthi", "💑"),
    4: ("相配",   "Maitri",  "💕"),
    3: ("中性",   "Sama",    "🤝"),
    2: ("需努力", "Shatru-M","⚠️"),
    1: ("困難",   "Shatru",  "⛔"),
}

# 相容性評分 → 百分比
COMPAT_PERCENT: Dict[int, int] = {
    5: 90, 4: 72, 3: 55, 2: 38, 1: 20
}

# ============================================================
# 敵對宮位組合 (Hostile House Combinations)
# 當出生行星與流年行星形成這些組合時，視為壓力期
# ============================================================
HOSTILE_PAIRS: List[Tuple[str, str, str]] = [
    ("Sun",     "Saturn",  "太陽與土星相對，代表命運挑戰與孤立感，需加強積德布施"),
    ("Mars",    "Moon",    "火星與月亮相沖，代表情緒爆發與感情風波，需修持忍辱"),
    ("Rahu",    "Mars",    "羅睺與火星相合，代表突發事故風險，需迴向功德"),
    ("Saturn",  "Moon",    "土星與月亮相剋，代表情緒壓抑與家庭阻礙，需供養月亮"),
    ("Jupiter", "Rahu",    "木星與羅睺相會，代表信仰困惑與法律糾紛，需親近正法"),
]

# ============================================================
# 撣族曆法資訊 (Shan Calendar)
# ============================================================
SHAN_CALENDAR_INFO = {
    "year_offset":       -450,  # 撣族年 = 緬甸年 (BE) - 450
    "new_year_month":    4,     # 撣族新年 (Lern Seign) 約在農曆 4 月
    "new_year_day_approx": 13,  # 約 4 月 13-16 日（與緬甸 Thingyan 同期）
    "shan_year_note":    "撣曆年 ≈ 緬甸歷 (BE) − 450（近似）",
    "festivals": [
        {
            "name_shan": "Lern Seign",
            "name_cn":   "撣族新年（水節）",
            "month":     4,
            "note":      "撣族新年水節，與緬甸 Thingyan 同期，互潑水祈福。",
        },
        {
            "name_shan": "Poi Kham",
            "name_cn":   "傣曆新年",
            "month":     4,
            "note":      "傣/撣族文化圈共通節日，有舞獅、水燈及佛塔繞行儀式。",
        },
        {
            "name_shan": "Poi Awk Phansa",
            "name_cn":   "出安居節",
            "month":     10,
            "note":      "佛教出安居節，撣族放水燈（Khomloy）慶祝。",
        },
        {
            "name_shan": "Poi Sang Long",
            "name_cn":   "男孩剃度節",
            "month":     3,
            "note":      "撣族男孩出家儀式，全村盛大慶典，被視為孝順父母的最高功德。",
        },
    ],
    "name_giving": (
        "撣族命名傳統：男孩以『Sai（賽）』開頭，女孩以『Nang（囡）』開頭，"
        "後接帶有守護星吉意的文字。木星守護者宜取『吉祥』或『繁盛』之意的名字；"
        "太陽守護者宜取帶有『光明』、『尊貴』之意的名字；"
        "月亮守護者宜取帶有『柔美』、『藝術』之意的名字。"
    ),
    "shan_direction_beliefs": (
        "撣族建屋傳統中，大門朝向應與主人的守護星方位一致：\n"
        "  太陽守護者 → 朝東北\n"
        "  月亮守護者 → 朝東\n"
        "  火星守護者 → 朝東南\n"
        "  水星守護者 → 朝南\n"
        "  木星守護者 → 朝西\n"
        "  金星守護者 → 朝西北\n"
        "  土星守護者 → 朝北\n"
        "  羅睺守護者 → 朝西南"
    ),
}
