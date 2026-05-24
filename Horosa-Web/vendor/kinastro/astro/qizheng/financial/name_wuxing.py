"""
名學五行分析模組 (Name Wuxing Analysis)

依「姓名學」五行理論，分析：
  1. 中文公司名稱各字筆劃 → 五行屬性比重
  2. 股票代碼數字 → 五行比重
  3. 使用者八字五行比重（從出生日期計算）
  4. 兩者比較：相生、相和、相剋解讀

筆劃五行規則（傳統姓名學）：
  末位數 1, 2 → 木
  末位數 3, 4 → 火
  末位數 5, 6 → 土
  末位數 7, 8 → 金
  末位數 9, 0 → 水

股票代碼數字規則（金融實盤優化）：
  9, 3, 5 → 火（強）
  4, 8    → 木（強）
  7, 0, 6 → 金（弱）
  1, 2    → 水（弱）
"""

from __future__ import annotations

from collections import Counter
from typing import Optional

# ──────────────────────────────────────────────────────────────────
# 五行常數
# ──────────────────────────────────────────────────────────────────

WUXING_ELEMENTS = ("木", "火", "土", "金", "水")

WUXING_COLORS = {
    "木": "#86efac",   # green
    "火": "#f87171",   # red
    "土": "#fbbf24",   # amber/yellow
    "金": "#e5e7eb",   # white/silver
    "水": "#60a5fa",   # blue
}

# 相生：木→火→土→金→水→木
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
# 相剋：木→土→水→火→金→木
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
# 被生（生我）
WUXING_SHENGME = {v: k for k, v in WUXING_SHENG.items()}
# 被剋（剋我）
WUXING_KEME = {v: k for k, v in WUXING_KE.items()}

# 數字五行（0-9）
# 依金融占星實盤優化：強化火（9/3/5）與木（4/8），弱化金（7/0/6）與水（1/2）
DIGIT_WUXING: dict[str, str] = {
    "0": "金",
    "1": "水",
    "2": "水",
    "3": "火",
    "4": "木",
    "5": "火",
    "6": "金",
    "7": "金",
    "8": "木",
    "9": "火",
}

_FAVOURABLE_NAME_KEYWORDS_ZH = {
    "光": "火", "麗": "火", "能": "火", "源": "火", "陽": "火", "昇": "火", "耀": "火",
    "聖": "火", "彩": "火", "帝": "火", "天": "火",
    "協": "木", "信": "木", "義": "木", "宜": "木", "愛": "木", "都": "木", "市": "木",
    "南": "火", "方": "火",
}
_UNFAVOURABLE_NAME_KEYWORDS_ZH = {
    "銀": "金", "鋼": "金", "鐵": "金", "晶": "金", "控": "金", "電": "水",
    "集": "土", "團": "土", "國": "土", "際": "土", "白": "金", "重": "土", "慶": "土",
}

_FAVOURABLE_KEYWORDS_EN = {
    "energy": "火", "solar": "火", "light": "火", "bright": "火",
    "green": "木", "tech": "木", "inno": "木", "innovation": "木",
}
_UNFAVOURABLE_KEYWORDS_EN = {
    "bank": "金", "securities": "金", "telecom": "水", "steel": "金",
    "metal": "金", "property": "土", "estate": "土", "semiconductor": "金",
}

_INDUSTRY_KEYWORDS = {
    "新能源": "火",
    "太陽能": "火",
    "光伏": "火",
    "環保": "木",
    "科技": "木",
    "電子": "木",
    "創新": "木",
    "汽車": "火",
    "消費": "木",
    "鋼": "金",
    "鐵": "金",
    "金屬": "金",
    "半導體": "金",
    "金融": "金",
    "券商": "金",
    "電訊": "水",
    "地產": "土",
    "房地產": "土",
}

# 英文字母五行（按字母序分五組，每組五至六個字母）
# A-E → 木, F-J → 火, K-O → 土, P-T → 金, U-Z → 水
LETTER_WUXING: dict[str, str] = {
    "A": "木", "B": "木", "C": "木", "D": "木", "E": "木",
    "F": "火", "G": "火", "H": "火", "I": "火", "J": "火",
    "K": "土", "L": "土", "M": "土", "N": "土", "O": "土",
    "P": "金", "Q": "金", "R": "金", "S": "金", "T": "金",
    "U": "水", "V": "水", "W": "水", "X": "水", "Y": "水", "Z": "水",
}

# ──────────────────────────────────────────────────────────────────
# 常見漢字筆劃表（傳統中文筆劃）
# 覆蓋大量常見公司名稱字符
# ──────────────────────────────────────────────────────────────────

_STROKE_COUNT: dict[str, int] = {
    # 1 畫
    "一": 1, "乙": 1,
    # 2 畫
    "二": 2, "十": 2, "丁": 2, "七": 2, "八": 2, "人": 2, "入": 2, "力": 2,
    "又": 2, "卜": 2, "刀": 2, "了": 2, "九": 2,
    # 3 畫
    "三": 3, "上": 3, "下": 3, "大": 3, "小": 3, "山": 3, "川": 3, "工": 3,
    "土": 3, "干": 3, "才": 3, "子": 3, "女": 3, "口": 3, "已": 3,
    "弓": 3, "士": 3, "也": 3, "千": 3, "凡": 3, "久": 3, "丈": 3, "丸": 3,
    "夕": 3, "之": 3, "亡": 3, "刃": 3,
    # 4 畫
    "中": 4, "王": 4, "天": 4, "元": 4, "公": 4, "火": 4, "水": 4, "木": 4,
    "文": 4, "心": 4, "手": 4, "月": 4, "日": 4, "牛": 4, "父": 4, "方": 4,
    "六": 4, "今": 4, "內": 4, "化": 4, "比": 4, "太": 4, "少": 4, "牙": 4,
    "升": 4, "反": 4, "仁": 4, "介": 4, "井": 4, "云": 4, "丹": 4,
    "互": 4, "五": 4, "允": 4, "友": 4, "分": 4, "切": 4, "及": 4,
    "夫": 4, "孔": 4, "引": 4, "毛": 4, "片": 4, "巴": 4, "止": 4, "不": 4,
    "予": 4, "幻": 4,
    # 5 畫
    "生": 5, "用": 5, "本": 5, "司": 5, "四": 5, "石": 5, "平": 5, "立": 5,
    "北": 5, "外": 5, "主": 5, "白": 5, "目": 5, "示": 5, "禾": 5, "田": 5,
    "由": 5, "甲": 5, "令": 5, "古": 5, "句": 5, "可": 5, "台": 5,
    "右": 5, "史": 5, "失": 5, "尼": 5, "市": 5, "央": 5, "布": 5, "代": 5,
    "以": 5, "付": 5, "仙": 5, "冊": 5, "功": 5, "包": 5, "半": 5, "幼": 5,
    "加": 5, "正": 5, "世": 5, "丘": 5, "且": 5, "仕": 5, "另": 5, "只": 5,
    "冬": 5, "出": 5, "卡": 5, "充": 5, "去": 5, "占": 5, "孕": 5,
    "召": 5, "民": 5, "玉": 5, "末": 5, "未": 5, "巨": 5, "永": 5,
    # 6 畫
    "行": 6, "有": 6, "地": 6, "年": 6, "份": 6, "合": 6, "名": 6, "安": 6,
    "先": 6, "字": 6, "在": 6, "百": 6, "此": 6, "肉": 6, "血": 6, "羊": 6,
    "米": 6, "色": 6, "西": 6, "成": 6, "江": 6, "光": 6, "因": 6, "同": 6,
    "全": 6, "向": 6, "吉": 6, "多": 6, "好": 6, "如": 6, "早": 6, "曲": 6,
    "次": 6, "竹": 6, "老": 6, "至": 6, "各": 6, "任": 6, "件": 6, "企": 6,
    "伊": 6, "伍": 6, "休": 6, "伏": 6, "价": 6, "仲": 6, "兆": 6,
    "共": 6, "再": 6, "匠": 6, "卯": 6, "危": 6, "旭": 6, "汗": 6,
    "牟": 6, "羽": 6, "耳": 6, "臣": 6, "自": 6, "舌": 6, "衣": 6,
    "亦": 6, "仿": 6, "伐": 6, "仰": 6, "帆": 6, "芒": 6, "后": 6,
    "囚": 6, "宇": 6, "宅": 6, "寺": 6, "朽": 6, "朴": 6, "机": 6,
    "州": 6, "式": 6, "印": 6, "存": 6, "交": 6,
    # 7 畫
    "投": 7, "技": 7, "志": 7, "利": 7, "材": 7, "村": 7, "快": 7,
    "宏": 7, "佐": 7, "但": 7, "克": 7, "兵": 7, "別": 7, "初": 7, "助": 7,
    "努": 7, "均": 7, "完": 7, "忍": 7, "扶": 7, "改": 7, "更": 7, "李": 7,
    "杉": 7, "步": 7, "系": 7, "谷": 7, "言": 7, "身": 7, "邑": 7, "角": 7,
    "車": 7, "見": 7, "走": 7, "足": 7, "豆": 7, "貝": 7, "赤": 7, "辰": 7,
    "里": 7, "吾": 7, "告": 7, "呆": 7, "君": 7, "吹": 7, "吶": 7, "否": 7,
    "局": 7, "役": 7, "床": 7, "廷": 7, "弟": 7, "形": 7, "我": 7,
    "抗": 7, "批": 7, "扭": 7, "扮": 7, "扼": 7, "抓": 7,
    "把": 7, "攻": 7, "每": 7, "汾": 7, "沙": 7, "沃": 7, "沐": 7, "沛": 7,
    "汽": 7, "男": 7, "皂": 7, "私": 7, "秀": 7, "究": 7,
    "芷": 7, "串": 7, "亨": 7, "享": 7, "佑": 7, "佔": 7, "伽": 7,
    "坐": 7, "尾": 7, "坊": 7, "序": 7, "弄": 7, "折": 7, "杏": 7, "杜": 7,
    "杖": 7, "杠": 7, "狂": 7, "芽": 7, "貢": 7, "芯": 7,
    # 8 畫
    "股": 8, "金": 8, "明": 8, "東": 8, "法": 8, "來": 8, "青": 8,
    "空": 8, "和": 8, "長": 8, "直": 8, "英": 8, "物": 8, "版": 8, "供": 8,
    "依": 8, "使": 8, "典": 8, "其": 8, "協": 8, "受": 8, "取": 8, "命": 8,
    "奇": 8, "奉": 8, "始": 8, "宗": 8, "官": 8, "定": 8, "岡": 8, "岸": 8,
    "店": 8, "府": 8, "征": 8, "忠": 8, "念": 8, "服": 8, "析": 8,
    "枝": 8, "果": 8, "武": 8, "泥": 8, "沸": 8, "波": 8, "泡": 8,
    "炎": 8, "知": 8, "社": 8, "芳": 8, "表": 8, "采": 8, "近": 8, "邦": 8,
    "阿": 8, "附": 8, "承": 8, "旺": 8, "昌": 8, "昆": 8, "昇": 8, "昏": 8,
    "杰": 8, "松": 8, "林": 8, "治": 8, "油": 8, "泳": 8, "沿": 8, "泊": 8,
    "炒": 8, "炊": 8, "玩": 8, "佳": 8, "侃": 8,
    "例": 8, "侍": 8, "坤": 8, "固": 8, "垂": 8, "季": 8, "孟": 8, "宙": 8,
    "宛": 8, "岳": 8, "忿": 8, "放": 8, "昀": 8, "昂": 8, "朋": 8,
    "杭": 8, "枉": 8, "欣": 8, "汪": 8, "況": 8,
    "沼": 8, "炕": 8, "矽": 8, "矸": 8, "肩": 8,
    "育": 8, "臥": 8, "芙": 8, "芬": 8, "虎": 8, "迎": 8, "門": 8,
    "昊": 8, "泱": 8, "怡": 8, "押": 8, "抵": 8, "板": 8, "事": 8, "牧": 8,
    "亞": 8, "所": 8, "坡": 8,
    # 9 畫
    "信": 9, "科": 9, "限": 9, "品": 9, "政": 9, "南": 9, "後": 9, "室": 9,
    "春": 9, "城": 9, "查": 9, "活": 9, "洋": 9, "持": 9, "星": 9, "面": 9,
    "保": 9, "幽": 9, "俗": 9, "前": 9, "度": 9, "盾": 9, "秋": 9,
    "約": 9, "重": 9, "風": 9, "亮": 9, "界": 9, "研": 9, "省": 9,
    "看": 9, "砂": 9, "砍": 9, "神": 9, "祈": 9, "祉": 9, "禺": 9,
    "紅": 9, "紀": 9, "美": 9, "耐": 9, "胃": 9, "背": 9,
    "胎": 9, "胡": 9, "致": 9, "般": 9, "茂": 9, "茄": 9,
    "茅": 9, "茶": 9, "計": 9, "訂": 9, "軍": 9, "述": 9, "退": 9,
    "迷": 9, "郊": 9, "郁": 9, "郡": 9, "革": 9, "頁": 9,
    "食": 9, "首": 9, "侯": 9, "俊": 9, "俏": 9, "俐": 9, "俠": 9,
    "冠": 9, "帥": 9, "帝": 9, "恆": 9,
    "恐": 9, "恭": 9, "恰": 9, "洽": 9,
    "洗": 9, "洛": 9, "洞": 9, "洪": 9, "洲": 9, "炸": 9,
    "為": 9, "皇": 9, "相": 9, "眉": 9, "胞": 9,
    "茉": 9, "迫": 9, "音": 9,
    "恨": 9, "急": 9, "怒": 9, "泓": 9, "洵": 9, "盈": 9, "恒": 9,
    "氦": 9, "泉": 9,
    # 10 畫
    "能": 10, "高": 10, "記": 10, "海": 10, "特": 10,
    "個": 10, "原": 10, "效": 10, "旅": 10, "時": 10, "財": 10, "益": 10,
    "紙": 10, "素": 10, "索": 10, "航": 10, "班": 10, "真": 10, "純": 10,
    "框": 10, "桃": 10, "桌": 10, "格": 10, "案": 10, "消": 10,
    "浦": 10, "流": 10, "浩": 10, "烈": 10, "珠": 10,
    "疾": 10, "盆": 10, "眠": 10, "迅": 10,
    "家": 10, "庭": 10, "容": 10, "師": 10, "席": 10, "庫": 10, "弱": 10,
    "徑": 10, "晃": 10, "晉": 10, "浙": 10, "涉": 10, "粉": 10,
    "粒": 10, "脂": 10, "討": 10, "起": 10, "骨": 10, "鬼": 10,
    "唐": 10, "員": 10, "哲": 10, "訊": 10, "氣": 10, "核": 10,
    "紡": 10, "站": 10, "倉": 10, "院": 10, "校": 10,
    "倫": 10, "哥": 10, "悉": 10, "值": 10, "料": 10,
    "酒": 10, "馬": 10, "秦": 10, "泰": 10, "迪": 10,
    "書": 10, "診": 10,
    # 11 畫
    "商": 11, "國": 11, "通": 11, "健": 11, "理": 11, "產": 11, "設": 11,
    "康": 11, "基": 11, "售": 11, "率": 11, "控": 11, "達": 11, "深": 11,
    "球": 11, "域": 11, "票": 11, "處": 11, "習": 11,
    "都": 11, "動": 11, "務": 11, "問": 11, "帶": 11, "強": 11, "張": 11,
    "視": 11, "袋": 11, "規": 11, "訪": 11, "貨": 11, "軟": 11, "連": 11,
    "部": 11, "雪": 11, "頂": 11, "麻": 11, "彩": 11, "情": 11, "盛": 11,
    "清": 11, "涵": 11, "乾": 11, "假": 11, "偏": 11, "偵": 11, "偶": 11,
    "停": 11, "側": 11, "偽": 11, "剪": 11, "副": 11,
    "參": 11, "唱": 11, "啟": 11, "培": 11,
    "執": 11, "堂": 11, "堅": 11, "婚": 11, "媒": 11,
    "專": 11, "密": 11, "崗": 11, "得": 11, "從": 11, "敘": 11,
    "晚": 11, "眼": 11, "移": 11, "符": 11, "第": 11, "組": 11, "細": 11, "終": 11,
    "脫": 11, "術": 11, "頃": 11, "産": 11, "訓": 11,
    "教": 11, "排": 11, "皖": 11, "現": 11,
    # 12 畫
    "港": 12, "萬": 12, "創": 12, "發": 12, "博": 12, "富": 12, "景": 12,
    "棟": 12, "植": 12, "森": 12, "湖": 12, "華": 12, "貿": 12, "超": 12,
    "量": 12, "黃": 12, "雅": 12, "集": 12, "欽": 12, "無": 12, "善": 12,
    "結": 12, "等": 12, "策": 12, "統": 12, "菊": 12, "萊": 12, "菠": 12,
    "衆": 12, "評": 12, "詞": 12, "貸": 12, "費": 12, "越": 12,
    "閒": 12, "陽": 12, "雁": 12, "順": 12, "須": 12, "飯": 12, "馮": 12,
    "媽": 12, "堡": 12, "塊": 12, "備": 12, "傅": 12, "傑": 12,
    "傢": 12, "凱": 12, "勞": 12, "勝": 12, "喜": 12, "喝": 12, "報": 12,
    "奧": 12, "寒": 12, "寬": 12, "就": 12, "散": 12, "敦": 12, "普": 12,
    "替": 12, "晴": 12, "期": 12, "欺": 12, "款": 12, "渠": 12, "減": 12,
    "渡": 12, "湯": 12, "游": 12, "然": 12, "焦": 12, "番": 12, "短": 12,
    "登": 12, "稀": 12, "程": 12, "稅": 12, "窗": 12, "絡": 12, "紫": 12,
    "給": 12, "翁": 12, "聖": 12, "脹": 12, "舒": 12,
    "著": 12, "裂": 12, "距": 12, "開": 12, "隊": 12, "雲": 12,
    "頌": 12, "馳": 12, "黑": 12, "粵": 12, "陝": 12, "渝": 12, "湘": 12,
    "智": 12, "惠": 12, "廈": 12,
    "棉": 12, "絲": 12, "晶": 12, "硬": 12,
    "隼": 12,
    # 13 畫
    "業": 13, "資": 13, "置": 13, "解": 13, "源": 13,
    "慈": 13, "意": 13, "感": 13, "想": 13, "損": 13,
    "搖": 13, "搜": 13, "新": 13, "暖": 13, "楊": 13, "楷": 13, "經": 13,
    "瑞": 13, "當": 13, "稱": 13, "節": 13, "裝": 13,
    "運": 13, "道": 13, "遊": 13, "酬": 13, "頑": 13, "幹": 13,
    "勢": 13, "勤": 13, "填": 13, "夢": 13, "嫁": 13,
    "嫌": 13, "幕": 13, "愉": 13,
    "暗": 13, "楓": 13, "楠": 13, "楫": 13, "極": 13, "歇": 13,
    "準": 13, "滄": 13, "滾": 13, "煤": 13, "煩": 13,
    "爺": 13, "裙": 13, "裕": 13,
    "試": 13, "誇": 13, "話": 13, "路": 13,
    "違": 13, "遙": 13, "靖": 13, "飾": 13, "預": 13,
    "滬": 13, "蓉": 13, "溫": 13, "滇": 13, "楚": 13, "廉": 13,
    "誠": 13, "鉛": 13, "蓄": 13, "傳": 13, "飲": 13, "匯": 13,
    "廣": 13, "廟": 13, "播": 13, "電": 13,
    # 14 畫
    "際": 14, "團": 14, "管": 14, "銀": 14, "精": 14, "演": 14, "算": 14,
    "綜": 14, "網": 14, "製": 14, "認": 14, "增": 14, "種": 14,
    "碗": 14, "碰": 14, "碳": 14, "碼": 14, "維": 14, "綠": 14, "聚": 14,
    "說": 14, "調": 14, "圖": 14, "幣": 14, "察": 14, "廢": 14, "彰": 14,
    "慢": 14, "態": 14, "截": 14, "摩": 14, "暢": 14,
    "榮": 14, "構": 14, "漢": 14, "漸": 14, "緒": 14, "遠": 14,
    "需": 14, "靜": 14, "領": 14, "颱": 14,
    "鳴": 14, "齊": 14, "實": 14, "槓": 14, "漲": 14,
    "閩": 14, "寧": 14, "漁": 14, "嘉": 14, "鳳": 14,
    "爾": 14, "臺": 14, "趙": 14, "魏": 14,
    "塾": 14, "壽": 14, "銅": 14, "誌": 14, "娛": 14,
    "模": 14,
    # 15 畫
    "數": 15, "廠": 15, "盤": 15, "確": 15, "線": 15, "養": 15,
    "課": 15, "諸": 15, "賤": 15, "賦": 15,
    "質": 15, "輝": 15, "適": 15, "樓": 15,
    "賞": 15, "廬": 15, "影": 15, "摯": 15, "操": 15,
    "標": 15, "熟": 15, "熱": 15, "獎": 15, "璃": 15,
    "窮": 15, "練": 15, "緣": 15, "蓬": 15, "蓮": 15,
    "誰": 15, "諒": 15, "遷": 15, "選": 15, "鋒": 15,
    "駐": 15, "駕": 15, "澳": 15, "德": 15, "潔": 15, "樂": 15,
    "魯": 15,
    # 16 畫
    "融": 16, "機": 16, "積": 16, "頻": 16, "儲": 16, "諮": 16,
    "翰": 16, "衡": 16, "親": 16, "謀": 16, "輸": 16, "遵": 16,
    "錦": 16, "錢": 16, "錯": 16, "錄": 16, "辦": 16, "陳": 16, "險": 16,
    "霖": 16, "駱": 16, "鮮": 16, "優": 16, "據": 16, "築": 16,
    "燃": 16, "獨": 16, "穎": 16, "糖": 16, "縱": 16, "聲": 16,
    "興": 16, "薦": 16, "薪": 16, "謙": 16, "諾": 16,
    "辨": 16, "遺": 16, "霓": 16, "隨": 16, "頭": 16, "頸": 16, "歷": 16,
    "澤": 16, "豫": 16, "黔": 16, "燕": 16, "鋼": 16, "橋": 16,
    "鴻": 16, "龍": 16, "館": 16,
    # 17 畫
    "環": 17, "購": 17, "總": 17, "鍵": 17, "應": 17, "聯": 17, "講": 17,
    "謝": 17, "臨": 17, "雜": 17, "點": 17,
    "檢": 17, "牆": 17, "謹": 17, "輿": 17,
    "鎳": 17, "隧": 17, "穗": 17, "嶺": 17, "韓": 17,
    "彙": 17, "磯": 17, "鋁": 17, "氫": 17, "賽": 17,
    # 18 畫
    "藥": 18, "醫": 18, "職": 18, "叢": 18, "覆": 18, "轉": 18, "豐": 18,
    "顏": 18, "擴": 18, "織": 18, "績": 18, "藏": 18,
    "贊": 18, "騁": 18, "鎮": 18, "鎖": 18, "鎊": 18, "鎗": 18,
    "騎": 18, "髮": 18, "濃": 18, "濟": 18, "礎": 18, "黎": 18,
    # 19 畫 +
    "羅": 19, "疆": 19, "類": 19, "識": 19, "麗": 19, "瀚": 19,
    "贏": 19, "證": 19, "護": 20, "騰": 20, "議": 20, "礦": 20, "贛": 20,
    "瓊": 20, "蘇": 22, "鐵": 21, "鶴": 21, "體": 23, "麟": 23, "灣": 25,
    "廳": 25, "觀": 25, "鑽": 27,
    # Heavenly Stems (some already defined above)
    "丙": 5, "戊": 5, "己": 3, "庚": 8, "辛": 7, "壬": 4, "癸": 9,
    # Earthly Branches (丑, 午, 酉, 戌, 亥 not elsewhere defined)
    "丑": 4, "寅": 11, "午": 4, "酉": 7, "戌": 6, "亥": 6,
}


def _stroke_to_wuxing(strokes: int) -> str:
    """筆劃數末位 → 五行"""
    unit = strokes % 10
    if unit in (1, 2):
        return "木"
    if unit in (3, 4):
        return "火"
    if unit in (5, 6):
        return "土"
    if unit in (7, 8):
        return "金"
    return "水"  # 0, 9


def _get_stroke_count(char: str) -> Optional[int]:
    """取得單一漢字的筆劃數，若無資料則回傳 None"""
    return _STROKE_COUNT.get(char)


def _zero_distribution() -> dict[str, float]:
    return {el: 0.0 for el in WUXING_ELEMENTS}


def _digit_weighted_element_score(digit: str) -> dict[str, float]:
    score = _zero_distribution()
    if digit in {"3", "5", "9"}:
        score["火"] += 1.9
        score["木"] += 0.4
    elif digit in {"4", "8"}:
        score["木"] += 1.5
        score["火"] += 0.3
    elif digit in {"1", "2"}:
        score["水"] += 0.45
    else:  # 0, 6, 7
        score["金"] += 0.45
    return score


def _match_keyword_distribution(
    text: str,
    favourable: dict[str, str],
    unfavourable: dict[str, str],
    *,
    favourable_weight: float,
    unfavourable_element_weight: float,
) -> tuple[dict[str, float], list[dict[str, str]]]:
    dist = _zero_distribution()
    hits: list[dict[str, str]] = []
    normalized_text = (text or "").lower()

    for key, element in favourable.items():
        if key.lower() in normalized_text:
            dist[element] += favourable_weight
            hits.append({"keyword": key, "element": element, "effect": "favourable"})

    for key, element in unfavourable.items():
        if key.lower() in normalized_text:
            dist[element] += unfavourable_element_weight
            hits.append({"keyword": key, "element": element, "effect": "unfavourable"})

    return dist, hits


def analyze_name_wuxing(name: str) -> dict:
    """
    分析中文公司名稱各字的五行屬性。

    Parameters:
        name: 中文公司名稱（只分析 CJK 字符）

    Returns:
        {
          "chars": [{"char": str, "strokes": int|None, "wuxing": str}],
          "distribution": {"木":int, "火":int, "土":int, "金":int, "水":int},
          "dominant": str,  # 最多的五行
          "unknown_chars": [str],  # 找不到筆劃的字
        }
    """
    cjk_chars = [
        c for c in name
        if "\u3400" <= c <= "\u4dbf" or "\u4e00" <= c <= "\u9fff"
    ]

    chars_data = []
    dist: Counter = Counter()
    unknown: list[str] = []

    for char in cjk_chars:
        strokes = _get_stroke_count(char)
        if strokes is not None:
            wx = _stroke_to_wuxing(strokes)
        else:
            unknown.append(char)
            wx = "土"  # 未知字預設為土（中性）
            strokes = None
        dist[wx] += 1
        chars_data.append({"char": char, "strokes": strokes, "wuxing": wx})

    # 確保所有五行都有計數
    for el in WUXING_ELEMENTS:
        dist.setdefault(el, 0)

    dominant = dist.most_common(1)[0][0] if chars_data else "土"

    keyword_distribution, keyword_hits = _match_keyword_distribution(
        name,
        _FAVOURABLE_NAME_KEYWORDS_ZH,
        _UNFAVOURABLE_NAME_KEYWORDS_ZH,
        favourable_weight=1.0,
        unfavourable_element_weight=1.2,
    )

    return {
        "chars": chars_data,
        "distribution": dict(dist),
        "weighted_distribution": {
            element: float(dist.get(element, 0)) + keyword_distribution.get(element, 0.0)
            for element in WUXING_ELEMENTS
        },
        "keyword_distribution": keyword_distribution,
        "keyword_hits": keyword_hits,
        "dominant": dominant,
        "unknown_chars": unknown,
        "total": len(chars_data),
    }


def analyze_english_name_wuxing(name: str) -> dict:
    """
    分析英文公司名稱各字母的五行屬性。
    字母按字母序分為五組：A-E→木, F-J→火, K-O→土, P-T→金, U-Z→水
    （前四組各含5個字母，最後一組含6個字母 U-Z）。

    只計算字母（A-Z, a-z），忽略數字、空格及符號。

    Parameters:
        name: 英文公司名稱

    Returns:
        {
          "letters": [{"letter": str, "wuxing": str}],
          "distribution": {"木":int, "火":int, "土":int, "金":int, "水":int},
          "dominant": str,
          "total": int,
        }
    """
    letters_data = []
    dist: Counter = Counter()

    for ch in name:
        upper = ch.upper()
        if upper in LETTER_WUXING:
            wx = LETTER_WUXING[upper]
            dist[wx] += 1
            letters_data.append({"letter": ch, "wuxing": wx})

    for el in WUXING_ELEMENTS:
        dist.setdefault(el, 0)

    dominant = dist.most_common(1)[0][0] if letters_data else "土"

    keyword_distribution, keyword_hits = _match_keyword_distribution(
        name,
        _FAVOURABLE_KEYWORDS_EN,
        _UNFAVOURABLE_KEYWORDS_EN,
        favourable_weight=1.2,
        unfavourable_element_weight=1.2,
    )

    return {
        "letters": letters_data,
        "distribution": dict(dist),
        "weighted_distribution": {
            element: float(dist.get(element, 0)) + keyword_distribution.get(element, 0.0)
            for element in WUXING_ELEMENTS
        },
        "keyword_distribution": keyword_distribution,
        "keyword_hits": keyword_hits,
        "dominant": dominant,
        "total": len(letters_data),
    }


def analyze_ticker_wuxing(ticker: str) -> dict:
    """
    分析股票代碼中數字的五行屬性。

    Parameters:
        ticker: 股票代碼（如 0550.HK, AAPL, 600519.SS）

    Returns:
        {
          "digits": [{"digit": str, "wuxing": str}],
          "distribution": {"木":int, "火":int, "土":int, "金":int, "水":int},
          "weighted_distribution": {"木":float, ...},
          "dominant": str,
          "ticker_clean": str,  # 僅數字部分
          "numerology_score": float,
        }
    """
    import re
    # 只取數字
    digits = re.findall(r"\d", ticker)

    digits_data = []
    dist: Counter = Counter()

    weighted_dist = _zero_distribution()

    for d in digits:
        wx = DIGIT_WUXING[d]
        dist[wx] += 1
        digits_data.append({"digit": d, "wuxing": wx})
        weighted_by_digit = _digit_weighted_element_score(d)
        for element, value in weighted_by_digit.items():
            weighted_dist[element] += value

    for el in WUXING_ELEMENTS:
        dist.setdefault(el, 0)

    dominant = dist.most_common(1)[0][0] if digits_data else "土"
    lucky_digit_count = sum(1 for d in digits if d in {"3", "5", "8", "9"})
    suppressive_digit_count = sum(1 for d in digits if d in {"0", "1", "2", "6", "7"})
    numerology_score = lucky_digit_count * 1.8 - suppressive_digit_count * 1.4

    return {
        "digits": digits_data,
        "distribution": dict(dist),
        "weighted_distribution": weighted_dist,
        "dominant": dominant,
        "ticker_clean": "".join(digits),
        "lucky_digit_count": lucky_digit_count,
        "suppressive_digit_count": suppressive_digit_count,
        "numerology_score": numerology_score,
        "total": len(digits),
    }


def analyze_industry_wuxing(industry: str) -> dict:
    """分析公司主要業務行業對應五行。"""
    normalized_industry = industry or ""
    dist = Counter()
    matched_keywords: list[dict[str, str]] = []

    for keyword, element in _INDUSTRY_KEYWORDS.items():
        if keyword in normalized_industry:
            dist[element] += 1
            matched_keywords.append({"keyword": keyword, "element": element})

    for el in WUXING_ELEMENTS:
        dist.setdefault(el, 0)

    if sum(dist.values()) == 0:
        dist["土"] += 1

    weighted_distribution = {el: float(dist.get(el, 0)) for el in WUXING_ELEMENTS}
    for item in matched_keywords:
        if item["element"] in {"木", "火"}:
            weighted_distribution[item["element"]] += 1.0
        elif item["element"] in {"金", "水"}:
            weighted_distribution[item["element"]] += 1.1
        else:
            weighted_distribution[item["element"]] += 0.8

    dominant = max(dist, key=lambda k: dist.get(k, 0)) if dist else "土"

    return {
        "industry": normalized_industry,
        "matched_keywords": matched_keywords,
        "distribution": dict(dist),
        "weighted_distribution": weighted_distribution,
        "dominant": dominant,
        "total": sum(dist.values()),
    }


def get_bazi_wuxing(
    year: int,
    month: int,
    day: int,
    hour: int = 12,
    include_hour: bool = True,
) -> dict:
    """
    從出生日期取得八字五行分佈（可選擇是否包含時柱）。

    Args:
        year: 出生年
        month: 出生月
        day: 出生日
        hour: 出生時（0-23），僅在 include_hour=True 時使用
        include_hour: 是否納入時柱（預設 True）

    Returns:
        {
          "pillars": [{"label":"年柱","stem":"甲","branch":"子","wuxing_stem":"木","wuxing_branch":"水"}, ...],
          "distribution": {"木":int, ...},
          "dominant": str,
          "available": bool,  # 是否成功計算
          "error": str,
        }
    """
    try:
        from sxtwl import fromSolar
        from astro.bazi.constants import TIANGAN, DIZHI, WUXING_TG, WUXING_DZ
    except ImportError as exc:
        return {
            "pillars": [],
            "distribution": {el: 0 for el in WUXING_ELEMENTS},
            "dominant": "土",
            "available": False,
            "error": str(exc),
        }

    try:
        cdate = fromSolar(year, month, day)
        ygz = cdate.getYearGZ(False)
        mgz = cdate.getMonthGZ()
        dgz = cdate.getDayGZ()

        pillar_data = [
            ("年柱", TIANGAN[ygz.tg], DIZHI[ygz.dz]),
            ("月柱", TIANGAN[mgz.tg], DIZHI[mgz.dz]),
            ("日柱", TIANGAN[dgz.tg], DIZHI[dgz.dz]),
        ]
        if include_hour:
            hgz = cdate.getHourGZ(hour)
            pillar_data.append(("時柱", TIANGAN[hgz.tg], DIZHI[hgz.dz]))

        dist: Counter = Counter()
        pillars = []
        for label, stem, branch in pillar_data:
            ws = WUXING_TG[stem]
            wb = WUXING_DZ[branch]
            dist[ws] += 1
            dist[wb] += 1
            pillars.append({
                "label": label,
                "stem": stem,
                "branch": branch,
                "wuxing_stem": ws,
                "wuxing_branch": wb,
            })

        for el in WUXING_ELEMENTS:
            dist.setdefault(el, 0)

        dominant = dist.most_common(1)[0][0]

        return {
            "pillars": pillars,
            "distribution": dict(dist),
            "dominant": dominant,
            "available": True,
            "error": "",
        }

    except Exception as exc:
        return {
            "pillars": [],
            "distribution": {el: 0 for el in WUXING_ELEMENTS},
            "dominant": "土",
            "available": False,
            "error": str(exc),
        }


def compare_wuxing(dist_a: dict[str, int], label_a: str,
                   dist_b: dict[str, int], label_b: str) -> dict:
    """
    比較兩個五行分佈，判斷相生、相和或相剋。

    Parameters:
        dist_a, label_a: 第一方的五行分佈及名稱（如「命主八字」）
        dist_b, label_b: 第二方的五行分佈及名稱（如「公司名稱」）

    Returns:
        {
          "dominant_a": str,
          "dominant_b": str,
          "relationship_code": str,
          "relationship": str,  # 相生|相剋|比和|中性
          "relationship_en": str,
          "color": str,
          "summary_zh": str,
          "summary_en": str,
          "score": int,  # +2=大吉, +1=吉, 0=中性, -1=凶, -2=大凶
        }
    """
    def _safe_float(value: object) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    normalized_a = {element: _safe_float(dist_a.get(element, 0)) for element in WUXING_ELEMENTS}
    normalized_b = {element: _safe_float(dist_b.get(element, 0)) for element in WUXING_ELEMENTS}

    total_a = sum(normalized_a.values()) or 1.0
    total_b = sum(normalized_b.values()) or 1.0

    # 主要五行：佔比最高
    dom_a = max(WUXING_ELEMENTS, key=lambda k: normalized_a.get(k, 0.0))
    dom_b = max(WUXING_ELEMENTS, key=lambda k: normalized_b.get(k, 0.0))

    # 關係判斷：以 A（命主）視角
    if dom_a == dom_b:
        relationship_code = "same_element"
        relationship = "比和"
        rel_en = "Harmonious (Same Element)"
        color = "#60a5fa"
        score = 1
        summary_zh = (
            f"命主{label_a}（{dom_a}）與{label_b}（{dom_b}）**同氣相通、比和格**。"
            f"五行相同，氣場共振，有天然親和力，相互理解，投資互利。"
        )
        summary_en = (
            f"{label_a} ({dom_a}) and {label_b} ({dom_b}) share the same element — **Harmonious**. "
            f"Natural resonance and mutual affinity; investment tends to be compatible."
        )
    elif WUXING_SHENG.get(dom_a) == dom_b:
        relationship_code = "you_feed_stock"
        relationship = "相生（命主生股）"
        rel_en = "Productive (You Feed Stock)"
        color = "#86efac"
        score = 2
        summary_zh = (
            f"命主{label_a}（{dom_a}）**生助**{label_b}（{dom_b}），屬相生格。"
            f"命主能量灌注股票，有助推動股票向好，長期持有有利。"
        )
        summary_en = (
            f"Your {dom_a} energy nurtures {label_b}'s {dom_b} — **Productive cycle**. "
            f"You energise the stock; long-term holding tends to be favourable."
        )
    elif WUXING_SHENG.get(dom_b) == dom_a:
        relationship_code = "stock_feeds_you"
        relationship = "相生（股生命主）"
        rel_en = "Productive (Stock Feeds You)"
        color = "#86efac"
        score = 2
        summary_zh = (
            f"{label_b}（{dom_b}）**生助**命主{label_a}（{dom_a}），屬相生格。"
            f"股票的五行能量滋養命主，持有此股能提升個人財運與運氣。"
        )
        summary_en = (
            f"{label_b}'s {dom_b} nurtures your {dom_a} — **Productive cycle**. "
            f"The stock's energy nourishes you; holding it may enhance your fortune."
        )
    elif WUXING_KE.get(dom_a) == dom_b:
        relationship_code = "you_overcome_stock"
        relationship = "相剋（命主剋股）"
        rel_en = "Conflicting (You Overcome Stock)"
        color = "#fb923c"
        score = -1
        summary_zh = (
            f"命主{label_a}（{dom_a}）**剋制**{label_b}（{dom_b}），屬相剋格。"
            f"命主能量壓制股票，持有期間或對股票走勢帶來壓力，宜謹慎操作。"
        )
        summary_en = (
            f"Your {dom_a} controls {label_b}'s {dom_b} — **Controlling cycle**. "
            f"Your energy may suppress the stock; proceed cautiously."
        )
    elif WUXING_KE.get(dom_b) == dom_a:
        relationship_code = "stock_overcomes_you"
        relationship = "相剋（股剋命主）"
        rel_en = "Conflicting (Stock Overcomes You)"
        color = "#f87171"
        score = -2
        summary_zh = (
            f"{label_b}（{dom_b}）**剋制**命主{label_a}（{dom_a}），屬相剋格。"
            f"股票能量壓制命主，持有此股財運受損、易生波折，不宜重倉。"
        )
        summary_en = (
            f"{label_b}'s {dom_b} controls your {dom_a} — **Conflicting cycle**. "
            f"The stock's energy suppresses yours; avoid heavy positions."
        )
    else:
        relationship_code = "neutral"
        relationship = "中性"
        rel_en = "Neutral"
        color = "#9090b8"
        score = 0
        summary_zh = (
            f"命主{label_a}（{dom_a}）與{label_b}（{dom_b}）五行**中性**，無明顯相生相剋。"
            f"需結合其他星盤因素綜合判斷。"
        )
        summary_en = (
            f"{label_a} ({dom_a}) and {label_b} ({dom_b}) have a **neutral** relationship. "
            f"No strong synergy or conflict; evaluate other chart factors."
        )

    return {
        "dominant_a": dom_a,
        "dominant_b": dom_b,
        "relationship_code": relationship_code,
        "relationship": relationship,
        "relationship_en": rel_en,
        "color": color,
        "summary_zh": summary_zh,
        "summary_en": summary_en,
        "score": score,
    }
