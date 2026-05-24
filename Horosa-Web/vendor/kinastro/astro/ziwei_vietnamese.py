"""
越南 Tử Vi 模式模組 (Vietnamese Tử Vi Đẩu Số Mode)
=====================================================

越南紫微斗數（Tử Vi Đẩu Số）是從中國紫微斗數傳入越南後，
融合越南文化、佛教信仰與農耕智慧而形成的獨特命理體系。

主要區別：
  - 生肖以貓（Mèo）代替兔（Thỏ/兔），源於越南農曆傳說
  - 星曜解釋融入越南農耕文化與佛教觀念
  - 宮位詮釋更強調家族、農田與社會和諧
  - 大限解讀結合越南節氣與民俗習慣

References:
  - 《紫微斗數全書》越南流傳版本
  - Tử Vi Đẩu Số - Nguyễn Mạnh Bảo
  - Tử Vi Toàn Thư - traditional Vietnamese manuscript
"""

# ============================================================
# 生肖覆寫 (Zodiac Animal Overrides)
# ============================================================

# 越南農曆以貓（Mèo）代替兔（Thỏ），這是越南與中國曆法最著名的差異。
# 地支索引 3 = 卯 → 越南稱「貓年」（Năm Mèo）
# 地支索引 1 = 丑 → 越南稱「水牛年」（Năm Trâu，部分傳統文本）
VIETNAMESE_ZODIAC_OVERRIDE: dict[int, dict[str, str]] = {
    3: {
        "zh": "貓",       # 卯宮 → 貓（代替兔）
        "vi": "Mèo",
        "zh_full": "貓年",
        "vi_full": "Năm Mèo",
        "note": "越南曆法以貓代兔，象徵靈敏機警與家庭守護",
    },
    1: {
        "zh": "水牛",     # 丑宮 → 水牛（部分傳統文本）
        "vi": "Trâu",
        "zh_full": "水牛年",
        "vi_full": "Năm Trâu",
        "note": "越南農耕文化中，水牛是重要勞動夥伴，象徵勤勞與豐收",
    },
}

# 標準十二生肖越南名稱（子=鼠...亥=豬）
VIETNAMESE_ZODIAC_NAMES: dict[int, tuple[str, str]] = {
    0:  ("鼠", "Tý / Chuột"),
    1:  ("水牛", "Sửu / Trâu"),
    2:  ("虎", "Dần / Hổ"),
    3:  ("貓", "Mão / Mèo"),    # 越南：貓！非兔
    4:  ("龍", "Thìn / Rồng"),
    5:  ("蛇", "Tỵ / Rắn"),
    6:  ("馬", "Ngọ / Ngựa"),
    7:  ("羊", "Mùi / Dê"),
    8:  ("猴", "Thân / Khỉ"),
    9:  ("雞", "Dậu / Gà"),
    10: ("狗", "Tuất / Chó"),
    11: ("豬", "Hợi / Lợn"),
}

# ============================================================
# 越南星曜名稱與解釋 (Vietnamese Star Names & Interpretations)
# ============================================================

# 格式: 星名 → (越南名, 拼音/讀音, 越南文化詮釋)
VIETNAMESE_STAR_MEANINGS: dict[str, dict[str, str]] = {
    # ── 紫微系 (Nhóm Tử Vi) ──
    "紫微": {
        "vi_name": "Tử Vi",
        "vi_reading": "Từ Vi",
        "zh_interp": "帝王之星，主貴、主權威。越南傳統視為守護祖廟、保佑家族興旺的主宰星。",
        "vi_interp": "Sao chủ quyền lực, phúc thọ và sự bảo hộ của tổ tiên. "
                     "Người có Tử Vi tọa mệnh thường có chí hướng lớn.",
    },
    "天機": {
        "vi_name": "Thiên Cơ",
        "vi_reading": "Thiên Cơ",
        "zh_interp": "智謀之星，主機變、聰明。越南文化中象徵農耕智慧與因地制宜的應變能力。",
        "vi_interp": "Sao trí tuệ và mưu lược. Người mang sao này khéo léo, "
                     "thích nghi tốt với hoàn cảnh.",
    },
    "太陽": {
        "vi_name": "Thái Dương",
        "vi_reading": "Thái Dương",
        "zh_interp": "官祿之星，主光明、名望。越南傳統視為護佑村社、引領社區的父性力量。",
        "vi_interp": "Sao danh vọng và quan lộc. Biểu trưng cho ánh sáng, "
                     "sự công nhận trong cộng đồng.",
    },
    "武曲": {
        "vi_name": "Vũ Khúc",
        "vi_reading": "Vũ Khúc",
        "zh_interp": "財星兼將星，主財富與果斷。越南文化中代表精明商賈與武將精神。",
        "vi_interp": "Sao tài lộc và quyết đoán. Người có Vũ Khúc thường "
                     "giỏi kinh doanh hoặc có chí tiến thủ.",
    },
    "天同": {
        "vi_name": "Thiên Đồng",
        "vi_reading": "Thiên Đồng",
        "zh_interp": "福星，主享樂、溫柔。越南傳統中象徵農村安樂、家庭和睦與佛緣深厚。",
        "vi_interp": "Sao phúc đức và an nhàn. Người có Thiên Đồng thường "
                     "hiền lành, hưởng thụ cuộc sống.",
    },
    "廉貞": {
        "vi_name": "Liêm Trinh",
        "vi_reading": "Liêm Trinh",
        "zh_interp": "囚星兼桃花，主是非、才藝。越南文化強調其正直品格的一面，戒其口舌之爭。",
        "vi_interp": "Sao cầm tù và nghệ thuật. Có thể mang đến tài năng "
                     "hoặc thị phi, cần giữ phẩm hạnh.",
    },
    # ── 天府系 (Nhóm Thiên Phủ) ──
    "天府": {
        "vi_name": "Thiên Phủ",
        "vi_reading": "Thiên Phủ",
        "zh_interp": "財帛星，主富貴、穩定。越南視之為守護糧倉與家業的吉星，象徵豐衣足食。",
        "vi_interp": "Sao tài phú và ổn định. Biểu trưng cho sự no đủ, "
                     "bảo vệ gia sản và lương thực.",
    },
    "太陰": {
        "vi_name": "Thái Âm",
        "vi_reading": "Thái Âm",
        "zh_interp": "田宅星兼陰柔之星，主家產、母性。越南文化中象徵月亮女神的庇護，主田園豐收。",
        "vi_interp": "Sao điền trạch và âm nhu. Liên quan đến bất động sản, "
                     "mẹ và sự che chở của trăng.",
    },
    "貪狼": {
        "vi_name": "Tham Lang",
        "vi_reading": "Tham Lang",
        "zh_interp": "桃花星兼欲望之星，主多才多藝。越南傳統重其才藝面，警惕貪慾帶來的業障。",
        "vi_interp": "Sao đào hoa và đa tài. Người có Tham Lang thường "
                     "hấp dẫn, đa năng nhưng cần kiểm soát ham muốn.",
    },
    "巨門": {
        "vi_name": "Cự Môn",
        "vi_reading": "Cự Môn",
        "zh_interp": "是非星，主口才、競爭。越南文化中提醒慎言惜福，以口德積累功德。",
        "vi_interp": "Sao thị phi và khẩu tài. Cần thận trọng trong lời nói, "
                     "tránh tranh cãi không cần thiết.",
    },
    "天相": {
        "vi_name": "Thiên Tướng",
        "vi_reading": "Thiên Tướng",
        "zh_interp": "印星，主輔佐、正直。越南傳統視為忠臣良將的護身符，主公務順遂。",
        "vi_interp": "Sao ấn tín và hỗ trợ. Người có Thiên Tướng thường "
                     "trung thực, phù hợp công việc nhà nước.",
    },
    "天梁": {
        "vi_name": "Thiên Lương",
        "vi_reading": "Thiên Lương",
        "zh_interp": "蔭星，主長壽、清高。越南佛教文化中視為菩薩庇蔭之星，主化厄解難。",
        "vi_interp": "Sao âm đức và trường thọ. Có sức mạnh hóa giải tai nạn, "
                     "liên quan đến Phật pháp.",
    },
    "七殺": {
        "vi_name": "Thất Sát",
        "vi_reading": "Thất Sát",
        "zh_interp": "將星，主威嚴、衝勁。越南武將文化視之為英勇護國之星，需以禮法駕馭其剛強。",
        "vi_interp": "Sao tướng tinh và uy quyền. Người có Thất Sát thường "
                     "quyết đoán, dũng cảm nhưng cần kiên nhẫn.",
    },
    "破軍": {
        "vi_name": "Phá Quân",
        "vi_reading": "Phá Quân",
        "zh_interp": "耗星，主變動、開創。越南傳統重其開疆闢土的精神，適合改革與冒險。",
        "vi_interp": "Sao phá cách và đổi thay. Người có Phá Quân thích "
                     "thay đổi, phù hợp sáng tạo và kinh doanh mới.",
    },
    # ── 輔助星 (Sao Phụ) ──
    "文昌": {
        "vi_name": "Văn Xương",
        "vi_reading": "Văn Xương",
        "zh_interp": "文曜吉星，主學業、科甲。越南科舉文化中極受重視，主文才出眾。",
        "vi_interp": "Sao văn học và học vấn. Người có Văn Xương thường "
                     "thông minh, đỗ đạt trong học tập.",
    },
    "文曲": {
        "vi_name": "Văn Khúc",
        "vi_reading": "Văn Khúc",
        "zh_interp": "文曜吉星，主才藝、口才。越南民間藝術中象徵音樂與詩詞的靈感泉源。",
        "vi_interp": "Sao nghệ thuật và khẩu tài. Liên quan đến âm nhạc, "
                     "thơ ca và sự lưu loát trong diễn đạt.",
    },
    "左輔": {
        "vi_name": "Tả Phụ",
        "vi_reading": "Tả Phụ",
        "zh_interp": "輔佐吉星，主貴人助力。越南重視人際和諧，此星象徵得到長輩與貴人扶持。",
        "vi_interp": "Sao quý nhân hỗ trợ. Người có Tả Phụ thường được "
                     "người trên giúp đỡ trong sự nghiệp.",
    },
    "右弼": {
        "vi_name": "Hữu Bật",
        "vi_reading": "Hữu Bật",
        "zh_interp": "輔佐吉星，主人緣、協調。與左輔相輔相成，象徵朋友與同伴的支持。",
        "vi_interp": "Sao nhân duyên và hỗ trợ. Người có Hữu Bật thường "
                     "có nhiều bạn bè tốt và được hợp tác thuận lợi.",
    },
    "天魁": {
        "vi_name": "Thiên Khôi",
        "vi_reading": "Thiên Khôi",
        "zh_interp": "貴人星，主天賦貴人緣。越南傳統視為上天賜予的守護神，助人逢凶化吉。",
        "vi_interp": "Sao thiên khôi quý nhân. Người có sao này thường "
                     "gặp may mắn và được người tốt giúp đỡ.",
    },
    "天鉞": {
        "vi_name": "Thiên Việt",
        "vi_reading": "Thiên Việt",
        "zh_interp": "貴人星，主陰性貴人。越南文化中與女性長輩或菩薩庇護有關。",
        "vi_interp": "Sao âm quý nhân. Liên quan đến sự bảo hộ của phụ nữ "
                     "lớn tuổi, Bồ Tát hoặc thần linh.",
    },
    "祿存": {
        "vi_name": "Lộc Tồn",
        "vi_reading": "Lộc Tồn",
        "zh_interp": "財祿吉星，主穩定收入與保守財富。越南農村文化中象徵糧食儲備豐足。",
        "vi_interp": "Sao tài lộc bảo thủ. Người có Lộc Tồn thường ổn định "
                     "tài chính nhưng cần tránh quá tiết kiệm.",
    },
    "火星": {
        "vi_name": "Hỏa Tinh",
        "vi_reading": "Hỏa Tinh",
        "zh_interp": "煞星，主衝動、意外。越南民俗中需以水克火、以佛法化煞。",
        "vi_interp": "Sao sát khí và bốc đồng. Cần kiểm soát tính nóng nảy, "
                     "tránh tai nạn và xung đột.",
    },
    "鈴星": {
        "vi_name": "Linh Tinh",
        "vi_reading": "Linh Tinh",
        "zh_interp": "煞星，主陰謀、暗算。越南傳統用符咒化解，需防小人暗害。",
        "vi_interp": "Sao âm mưu và tai họa tiềm ẩn. Cần cẩn thận với "
                     "tiểu nhân và những mối nguy không rõ ràng.",
    },
    "天馬": {
        "vi_name": "Thiên Mã",
        "vi_reading": "Thiên Mã",
        "zh_interp": "驛馬星，主奔波、遠行。越南遷移文化中象徵出外打拼、南遷北上的遷徙精神。",
        "vi_interp": "Sao dịch chuyển và bôn ba. Người có Thiên Mã thường "
                     "hay di chuyển, thích hợp làm việc xa nhà.",
    },
    "地空": {
        "vi_name": "Địa Không",
        "vi_reading": "Địa Không",
        "zh_interp": "空耗之星，主耗財、落空。越南傳統需供奉土地神以化解地空之煞。",
        "vi_interp": "Sao không đắc và hao tổn. Liên quan đến sự thất bại "
                     "bất ngờ, cần cúng bái thổ địa để hóa giải.",
    },
    "地劫": {
        "vi_name": "Địa Kiếp",
        "vi_reading": "Địa Kiếp",
        "zh_interp": "劫耗之星，主橫禍、失財。與地空同為越南命理師最重視的煞星。",
        "vi_interp": "Sao kiếp nạn và tai họa bất ngờ. Cùng với Địa Không "
                     "tạo thành cặp sao nguy hiểm nhất.",
    },
}

# ============================================================
# 越南十二宮位詮釋 (Vietnamese Palace Interpretations)
# ============================================================

VIETNAMESE_PALACE_DESC: dict[str, dict[str, str]] = {
    "命宮": {
        "vi_name": "Cung Mệnh",
        "zh_interp": "決定人生格局、個性與命運走向。越南傳統尤重命宮與祖德的關聯。",
        "vi_interp": "Cung chủ về tính cách, số phận và hướng đi cuộc đời. "
                     "Phản ánh phúc đức tổ tiên để lại.",
    },
    "兄弟宮": {
        "vi_name": "Cung Huynh Đệ",
        "zh_interp": "兄弟姐妹關係，以及朋友、同儕互動。越南重視家族倫理，此宮尤為重要。",
        "vi_interp": "Cung về anh chị em và bạn bè thân thiết. "
                     "Trong văn hóa Việt, tình cốt nhục được coi trọng hàng đầu.",
    },
    "夫妻宮": {
        "vi_name": "Cung Phu Thê",
        "zh_interp": "婚姻與感情，越南傳統中此宮還影響家族延續與祖先香火。",
        "vi_interp": "Cung hôn nhân và tình duyên. Ảnh hưởng đến sự hòa thuận "
                     "gia đình và việc nối dõi tông đường.",
    },
    "子女宮": {
        "vi_name": "Cung Tử Tức",
        "zh_interp": "子女、學生與創造力。越南農村文化中子女是勞動力的來源，此宮象徵家族昌盛。",
        "vi_interp": "Cung con cái và sự sáng tạo. Trong văn hóa nông nghiệp, "
                     "con cái là nguồn lao động và sự nối tiếp gia tộc.",
    },
    "財帛宮": {
        "vi_name": "Cung Tài Bạch",
        "zh_interp": "金錢、財富與求財方式。越南商業文化重視此宮，與田地收成、貿易皆相關。",
        "vi_interp": "Cung tài chính và cách kiếm tiền. Liên quan đến mùa màng, "
                     "buôn bán và tích lũy tài sản.",
    },
    "疾厄宮": {
        "vi_name": "Cung Tật Ách",
        "zh_interp": "健康、疾病與意外。越南傳統用草藥與佛法調養此宮所顯示的健康問題。",
        "vi_interp": "Cung sức khỏe và tai nạn. Người Việt thường dùng "
                     "thảo dược và lễ cúng để hóa giải.",
    },
    "遷移宮": {
        "vi_name": "Cung Thiên Di",
        "zh_interp": "旅行、遷徙與出外運勢。越南歷史上多次遷徙，此宮象徵開疆闢土的移民精神。",
        "vi_interp": "Cung di chuyển và vận mệnh khi ra ngoài. Phản ánh "
                     "tinh thần khai phá của người Việt qua lịch sử.",
    },
    "交友宮": {
        "vi_name": "Cung Giao Hữu",
        "zh_interp": "朋友、同事與下屬關係。越南重視「bạn tốt」（良友），此宮影響社交網絡。",
        "vi_interp": "Cung bạn bè, đồng nghiệp và cấp dưới. "
                     "Phản ánh chất lượng các mối quan hệ xã hội.",
    },
    "官祿宮": {
        "vi_name": "Cung Quan Lộc",
        "zh_interp": "事業、工作與官運。越南科舉傳統中此宮決定仕途成敗，現代則擴展至各類職業。",
        "vi_interp": "Cung sự nghiệp và thăng tiến. Từ truyền thống khoa cử "
                     "đến hiện đại, cung này quyết định con đường công danh.",
    },
    "田宅宮": {
        "vi_name": "Cung Điền Trạch",
        "zh_interp": "房產、家庭環境與祖業。越南農業社會中田地是命根子，此宮尤受重視。",
        "vi_interp": "Cung bất động sản và gia đình. Trong xã hội nông nghiệp "
                     "Việt Nam, ruộng đất là nền tảng cuộc sống.",
    },
    "福德宮": {
        "vi_name": "Cung Phúc Đức",
        "zh_interp": "福份、精神享受與前世積德。越南佛教文化極重此宮，視為業力與因果的體現。",
        "vi_interp": "Cung phúc báu và tinh thần. Trong Phật giáo Việt Nam, "
                     "cung này phản ánh nghiệp lực từ kiếp trước.",
    },
    "父母宮": {
        "vi_name": "Cung Phụ Mẫu",
        "zh_interp": "父母、長輩關係與文書運。越南孝道文化中此宮極為重要，影響祖先庇護。",
        "vi_interp": "Cung cha mẹ và người trên. Đạo hiếu của người Việt "
                     "coi trọng cung này như nền tảng của mọi may mắn.",
    },
}

# ============================================================
# 越南大限詮釋 (Vietnamese Đại Vận / Major Luck Period)
# ============================================================

VIETNAMESE_DA_XIAN_TIPS: dict[str, str] = {
    "命宮大限": (
        "命宮大限（Đại Vận Cung Mệnh）：此大限為人生最重要的十年，"
        "個人潛能全面發揮，越南命理師建議積極行動、廣結善緣。"
    ),
    "兄弟宮大限": (
        "兄弟宮大限（Đại Vận Cung Huynh Đệ）：此期與手足、朋友互動頻繁，"
        "越南傳統強調此時應回饋家族，多行孝順之事。"
    ),
    "夫妻宮大限": (
        "夫妻宮大限（Đại Vận Cung Phu Thê）：感情婚姻的關鍵十年，"
        "越南習俗建議此期內擇吉成婚或鞏固感情。"
    ),
    "子女宮大限": (
        "子女宮大限（Đại Vận Cung Tử Tức）：子女與創造力旺盛之期，"
        "越南傳統認為此時生子最為吉利，子嗣聰明孝順。"
    ),
    "財帛宮大限": (
        "財帛宮大限（Đại Vận Cung Tài Bạch）：財運旺盛之十年，"
        "越南商人視此大限為黃金創業期，宜投資田產。"
    ),
    "疾厄宮大限": (
        "疾厄宮大限（Đại Vận Cung Tật Ách）：健康需特別注意，"
        "越南民俗建議多禮佛、少勞累，定期健康檢查。"
    ),
    "遷移宮大限": (
        "遷移宮大限（Đại Vận Cung Thiên Di）：適合遠行、移居或出外發展，"
        "越南歷史上許多成功故事都在此大限中開展。"
    ),
    "交友宮大限": (
        "交友宮大限（Đại Vận Cung Giao Hữu）：人際關係決定成敗，"
        "越南俗語「bạn tốt hơn vàng」（良友勝黃金）在此期最為應驗。"
    ),
    "官祿宮大限": (
        "官祿宮大限（Đại Vận Cung Quan Lộc）：事業最旺之十年，"
        "越南傳統視此為「thi đỗ進仕」的黃金機遇期。"
    ),
    "田宅宮大限": (
        "田宅宮大限（Đại Vận Cung Điền Trạch）：置業安家的好時機，"
        "越南農業社會傳統認為此時購地建屋最為吉利。"
    ),
    "福德宮大限": (
        "福德宮大限（Đại Vận Cung Phúc Đức）：精神修養與享福之期，"
        "越南佛教徒常在此大限中皈依修行或廣結佛緣。"
    ),
    "父母宮大限": (
        "父母宮大限（Đại Vận Cung Phụ Mẫu）：與父母長輩關係密切，"
        "越南孝道傳統強調此期應盡力奉養雙親、回報養育之恩。"
    ),
}

# ============================================================
# 越南婚姻合婚 (Vietnamese Marriage Compatibility)
# ============================================================

# 越南傳統合婚以生肖相配為核心，同時參考紫微斗數夫妻宮
VIETNAMESE_MARRIAGE_COMPAT: dict[tuple[int, int], dict[str, str]] = {
    # 三合：子辰申 (鼠龍猴)
    (0, 4):  {"level": "大吉", "vi": "Đại Cát", "note": "鼠龍相配，天作之合"},
    (0, 8):  {"level": "大吉", "vi": "Đại Cát", "note": "鼠猴同屬水局，情投意合"},
    (4, 8):  {"level": "大吉", "vi": "Đại Cát", "note": "龍猴三合，富貴雙全"},
    # 三合：丑巳酉 (水牛蛇雞)
    (1, 5):  {"level": "大吉", "vi": "Đại Cát", "note": "水牛蛇相配，勤勞持家"},
    (1, 9):  {"level": "大吉", "vi": "Đại Cát", "note": "水牛雞同屬金局，財運亨通"},
    (5, 9):  {"level": "大吉", "vi": "Đại Cát", "note": "蛇雞三合，智慧與美麗兼備"},
    # 三合：寅午戌 (虎馬狗)
    (2, 6):  {"level": "大吉", "vi": "Đại Cát", "note": "虎馬相配，英雄美人"},
    (2, 10): {"level": "大吉", "vi": "Đại Cát", "note": "虎狗同屬火局，忠義相守"},
    (6, 10): {"level": "大吉", "vi": "Đại Cát", "note": "馬狗三合，義氣深重"},
    # 三合：卯未亥 (貓羊豬) ← 越南：貓取代兔！
    (3, 7):  {"level": "大吉", "vi": "Đại Cát", "note": "貓羊相配（越南特色），溫柔甜蜜"},
    (3, 11): {"level": "大吉", "vi": "Đại Cát", "note": "貓豬同屬木局，富有詩意"},
    (7, 11): {"level": "大吉", "vi": "Đại Cát", "note": "羊豬三合，安康富足"},
    # 六合
    (0, 1):  {"level": "吉", "vi": "Cát", "note": "鼠水牛六合，穩中求進"},
    (2, 3):  {"level": "吉", "vi": "Cát", "note": "虎貓六合（越南），活潑相映"},
    (4, 5):  {"level": "吉", "vi": "Cát", "note": "龍蛇六合，神秘相吸"},
    (6, 7):  {"level": "吉", "vi": "Cát", "note": "馬羊六合，自由浪漫"},
    (8, 9):  {"level": "吉", "vi": "Cát", "note": "猴雞六合，才智相稱"},
    (10, 11): {"level": "吉", "vi": "Cát", "note": "狗豬六合，忠誠溫暖"},
    # 相沖（不利）
    (0, 6):  {"level": "不利", "vi": "Bất Lợi", "note": "鼠馬相沖，個性相左，需包容"},
    (1, 7):  {"level": "不利", "vi": "Bất Lợi", "note": "水牛羊相沖，越南命理師建議慎重"},
    (2, 8):  {"level": "不利", "vi": "Bất Lợi", "note": "虎猴相沖，性格衝突"},
    (3, 9):  {"level": "不利", "vi": "Bất Lợi", "note": "貓雞相沖（越南特色），需磨合"},
    (4, 10): {"level": "不利", "vi": "Bất Lợi", "note": "龍狗相沖，主見相左"},
    (5, 11): {"level": "不利", "vi": "Bất Lợi", "note": "蛇豬相沖，生活方式差異大"},
}

# ============================================================
# 越南文化特色說明 (Vietnamese Cultural Notes)
# ============================================================

VIETNAMESE_CULTURAL_NOTE = (
    "🇻🇳 **越南 Tử Vi 特色**\n\n"
    "• **以貓代兔**：越南農曆以「貓」（Mèo）代替中國曆法中的「兔」（Thỏ），"
    "這是越南與中國命理體系最顯著的差異，源於越南文化中貓是家庭守護神的傳統。\n\n"
    "• **融合佛教智慧**：越南 Tử Vi 深受南傳佛教影響，"
    "星曜解釋中融入了因果業力（Nghiệp lực）與慈悲（Từ bi）的觀念。\n\n"
    "• **農耕文化底蘊**：宮位詮釋與大限分析中，"
    "保留了對田地、糧食與家族農業的深切關注，體現越南稻作文明的特色。\n\n"
    "• **孝道倫理**：父母宮與兄弟宮在越南命理中尤為重要，"
    "體現「百善孝為先」（Trăm điều thiện, hiếu vi đầu）的傳統美德。"
)

# 越南旗幟 emoji 與主題色
VI_FLAG = "🇻🇳"
VI_ACCENT_COLOR = "#DA251D"   # 越南國旗紅色
VI_STAR_COLOR = "#FFCD00"     # 越南國旗黃色


def get_vietnamese_zodiac_name(branch_idx: int) -> tuple[str, str]:
    """
    取得越南生肖名稱。

    Parameters:
        branch_idx: 地支索引（0=子, 1=丑, ..., 11=亥）

    Returns:
        (中文名, 越南文名) tuple

    Notes:
        地支 3（卯）在越南為貓（Mèo）而非兔（Thỏ）。
        地支 1（丑）在越南為水牛（Trâu）。
    """
    if branch_idx < 0 or branch_idx > 11:
        raise ValueError(f"branch_idx must be 0-11, got {branch_idx}")
    zh, vi = VIETNAMESE_ZODIAC_NAMES[branch_idx]
    return zh, vi


def get_star_vietnamese_info(star_name: str) -> dict[str, str] | None:
    """
    取得星曜的越南文化詮釋。

    Parameters:
        star_name: 星曜中文名稱

    Returns:
        包含 vi_name, vi_reading, zh_interp, vi_interp 的字典，
        若無資料則回傳 None。
    """
    return VIETNAMESE_STAR_MEANINGS.get(star_name)


def get_palace_vietnamese_info(palace_name: str) -> dict[str, str] | None:
    """
    取得宮位的越南文化詮釋。

    Parameters:
        palace_name: 宮位中文名稱

    Returns:
        包含 vi_name, zh_interp, vi_interp 的字典，
        若無資料則回傳 None。
    """
    return VIETNAMESE_PALACE_DESC.get(palace_name)


def get_zodiac_year_label(branch_idx: int, vietnam_mode: bool = False) -> str:
    """
    取得生肖年標籤（中文），越南模式時卯宮顯示「貓」。

    Parameters:
        branch_idx: 地支索引
        vietnam_mode: 是否啟用越南模式

    Returns:
        生肖年中文標籤字串
    """
    if vietnam_mode and branch_idx in VIETNAMESE_ZODIAC_OVERRIDE:
        return VIETNAMESE_ZODIAC_OVERRIDE[branch_idx]["zh"]
    standard = ["鼠", "牛", "虎", "兔", "龍", "蛇", "馬", "羊", "猴", "雞", "狗", "豬"]
    return standard[branch_idx]


def get_marriage_compatibility(branch1: int, branch2: int) -> dict[str, str]:
    """
    取得越南傳統合婚相容性資訊。

    Parameters:
        branch1: 第一人地支索引（年支）
        branch2: 第二人地支索引（年支）

    Returns:
        包含 level, vi, note 的字典；若無特殊記錄則回傳普通相容。
    """
    _DEFAULT_COMPAT: dict[str, str] = {
        "level": "一般", "vi": "Bình Thường", "note": "需進一步查看夫妻宮星曜",
    }
    key = (min(branch1, branch2), max(branch1, branch2))
    return VIETNAMESE_MARRIAGE_COMPAT.get(key, _DEFAULT_COMPAT)


def build_vietnam_mode_header_html() -> str:
    """
    生成越南模式的頂部說明 HTML 橫幅。

    Returns:
        HTML 字串，用於 st.markdown(..., unsafe_allow_html=True)
    """
    return (
        f'<div style="background:linear-gradient(135deg,{VI_ACCENT_COLOR},{VI_ACCENT_COLOR}cc);'
        f'border-radius:10px;padding:12px 16px;margin-bottom:12px;'
        f'border-left:5px solid {VI_STAR_COLOR};">'
        f'<span style="font-size:18px;font-weight:bold;color:{VI_STAR_COLOR}">'
        f'{VI_FLAG} 越南 Tử Vi Đẩu Số 模式</span>'
        f'<span style="font-size:12px;color:#ffe0e0;margin-left:12px">'
        f'以貓代兔 · 融合越南佛教與農耕智慧</span>'
        f'</div>'
    )
