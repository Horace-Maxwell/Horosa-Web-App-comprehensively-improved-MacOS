
"""
astro/diqiyijue/calculator.py — Di Qi Yi Jue core computation module.

Integrates the legacy 滌器遺訣 implementation into KinAstro with a pure
`compute_diqiyijue_chart()` API and a dataclass result structure.
"""

from __future__ import annotations

# ============================================================
# 基礎常量與工具函數
# ============================================================

# 十天干
TIANGAN = ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")

# 十二地支
DIZHI = ("子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥")

# 六十甲子納音表（按甲子起算，每兩柱一納音，共30組）
# 甲子乙丑金, 丙寅丁卯火, 戊辰己巳木, 庚午辛未土, 壬申癸酉金,
# 甲戌乙亥火, 丙子丁丑水, 戊寅己卯土, 庚辰辛巳金, 壬午癸未木,
# 甲申乙酉水, 丙戌丁亥土, 戊子己丑火, 庚寅辛卯木, 壬辰癸巳水,
# 甲午乙未金, 丙申丁酉火, 戊戌己亥木, 庚子辛丑土, 壬寅癸卯金,
# 甲辰乙巳火, 丙午丁未水, 戊申己酉土, 庚戌辛亥金, 壬子癸丑木,
# 甲寅乙卯水, 丙辰丁巳土, 戊午己未火, 庚申辛酉木, 壬戌癸亥水
_NAYIN_TABLE = [
    "金", "火", "木", "土", "金", "火", "水", "土", "金", "木",
    "水", "土", "火", "木", "水", "金", "火", "木", "土", "金",
    "火", "水", "土", "金", "木", "水", "土", "火", "木", "水",
]

# 六十甲子納音詳表（含具體名稱，30組）
_NAYIN_DETAIL = [
    "海中金", "爐中火", "大林木", "路旁土", "劍鋒金", "山頭火",
    "澗下水", "城頭土", "白蠟金", "楊柳木", "井泉水", "屋上土",
    "霹靂火", "松柏木", "長流水", "砂石金", "山下火", "平地木",
    "壁上土", "金箔金", "覆燈火", "天河水", "大驛土", "釵釧金",
    "桑拓木", "大溪水", "沙中土", "天上火", "石榴木", "大海水",
]

# 河圖五行：1,6→水  2,7→火  3,8→木  4,9→金  5,10(0)→土
HETU_WUXING = {
    1: "水", 6: "水",
    2: "火", 7: "火",
    3: "木", 8: "木",
    4: "金", 9: "金",
    5: "土", 0: "土", 10: "土",
}

# 五行相生：木生火、火生土、土生金、金生水、水生木
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

# 五行相克：木克土、土克水、水克火、火克金、金克木
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 後天八卦對應（先天卦序用於部分貴格）
BAGUA_NAMES = ("坎", "坤", "震", "巽", "乾", "兌", "艮", "離")

# 後天八卦九宮順時針排列（用於屬齒卦）
# 兌→乾→坎→艮→震→巽→離→坤
BAGUA_HOUTIAN_ORDER = ("兌", "乾", "坎", "艮", "震", "巽", "離", "坤")

# 八宮名稱（固定順序）
BAGONG_NAMES = ("倫", "己", "雁", "翡", "乳", "養", "鬼", "基")
BAGONG_FULLNAMES = (
    "倫（父母）", "己（己身）", "雁（兄弟）", "翡（夫妻）",
    "乳（子女）", "養（官祿）", "鬼（疾厄）", "基（家宅）",
)

# 八星八卦分屬八宮
BAGONG_XING = ("貪狼", "巨門", "祿存", "文曲", "廉貞", "武曲", "破軍", "伏吟")
BAGONG_GUA = ("坎", "坤", "震", "巽", "離", "乾", "兌", "艮")

# 十二長生順序（起胞法中「胞」即「絕」位）
SHIER_CHANGSHENG = (
    "胞", "胎", "養", "生", "敗", "冠", "官", "旺", "衰", "病", "死", "墓"
)

# 起胞法起始地支：金寅、水土巳、木申、火亥（皆順數）
QIPAO_START = {"金": "寅", "水": "巳", "土": "巳", "木": "申", "火": "亥"}

# 八觀法——以八卦變爻對應八觀
# 口訣：上二天宜 下二福德 中動絕命 對延年(絕體)
#        上動生氣 下祸害 上下俱動游魂 不動歸魂
BAGUAN_NAMES = ("生氣", "天宜", "絕體", "遊魂", "禍害", "福德", "絕命", "歸魂")

# 八卦方位地支歸屬
# 兌酉  乾戌亥  坎子  艮丑寅  震卯  巽辰巳  離午  坤未申
GUA_DIZHI_MAP = {
    "兌": ["酉"],
    "乾": ["戌", "亥"],
    "坎": ["子"],
    "艮": ["丑", "寅"],
    "震": ["卯"],
    "巽": ["辰", "巳"],
    "離": ["午"],
    "坤": ["未", "申"],
}

# 反向：地支→卦
DIZHI_TO_GUA = {}
for _g, _dzs in GUA_DIZHI_MAP.items():
    for _dz in _dzs:
        DIZHI_TO_GUA[_dz] = _g

# 八觀矩陣（主卦 vs 客卦 → 八觀結果）
# 使用後天八卦的爻變來推導
# 爻編碼（自上而下）: 乾111 兌011 離101 震001 巽110 坎010 艮100 坤000
_GUA_YAO = {
    "乾": (1, 1, 1), "兌": (0, 1, 1), "離": (1, 0, 1), "震": (0, 0, 1),
    "巽": (1, 1, 0), "坎": (0, 1, 0), "艮": (1, 0, 0), "坤": (0, 0, 0),
}


def _baguan_relation(zhu_gua: str, ke_gua: str) -> str:
    """
    根據兩卦爻變位置，判定八觀關係。
    對應《涤器遗诀》八觀法。
    口訣：
      上二天宜(五鬼) 下二福德(延年)
      中動絕命 對延年→絕體
      上動生氣 下禍害
      上下俱動遊魂(六煞)
      不動歸魂(伏位)
    """
    y1 = _GUA_YAO[zhu_gua]
    y2 = _GUA_YAO[ke_gua]
    diff = [i for i in range(3) if y1[i] != y2[i]]
    n = len(diff)
    if n == 0:
        return "歸魂"  # 伏位
    if n == 1:
        if diff[0] == 0:
            return "生氣"  # 上動
        elif diff[0] == 1:
            return "絕命"  # 中動
        else:
            return "禍害"  # 下動
    if n == 2:
        if diff == [0, 1]:
            return "天宜"  # 上二
        elif diff == [1, 2]:
            return "福德"  # 下二
        else:  # [0, 2]
            return "遊魂"  # 上下俱動
    # n == 3
    return "絕體"  # 全動（對延年）


# 建立完整的八觀查找表
BAGUAN_TABLE = {}
for _g1 in _GUA_YAO:
    BAGUAN_TABLE[_g1] = {}
    for _g2 in _GUA_YAO:
        BAGUAN_TABLE[_g1][_g2] = _baguan_relation(_g1, _g2)


# ============================================================
# 工具函數
# ============================================================

def tiangan_index(gan: str) -> int:
    """天干序號，甲=0, 乙=1, ..., 癸=9"""
    return TIANGAN.index(gan)


def dizhi_index(zhi: str) -> int:
    """地支序號，子=0, 丑=1, ..., 亥=11"""
    return DIZHI.index(zhi)


def ganzhi_to_index(gz: str) -> int:
    """干支組合轉為六十甲子序號（0~59），如甲子=0, 乙丑=1, ..."""
    g = tiangan_index(gz[0])
    z = dizhi_index(gz[1])
    # 六十甲子：天干地支同步推進
    for i in range(60):
        if i % 10 == g and i % 12 == z:
            return i
    raise ValueError(f"無效干支組合: {gz}")


def nayin_wuxing(gz: str) -> str:
    """
    取干支之納音五行。
    對應《涤器遗诀》五條納音相關用法。
    """
    idx = ganzhi_to_index(gz)
    return _NAYIN_TABLE[idx // 2]


def nayin_detail(gz: str) -> str:
    """取干支之納音詳名（如「海中金」）。"""
    idx = ganzhi_to_index(gz)
    return _NAYIN_DETAIL[idx // 2]


def hetu_wuxing(num: int) -> str:
    """
    河圖五行：以數字定五行。
    對應《涤器遗诀》河圖五行章：一六水 二七火 三八木 四九金 五十土。
    """
    return HETU_WUXING.get(num % 10, "土")


def wuxing_relation(zhu: str, ke: str) -> str:
    """
    五行生克關係判斷。
    返回：「比和」「生」「被生」「克」「被克」
    主(zhu)為主體，客(ke)為客體。
    """
    if zhu == ke:
        return "比和"
    if WUXING_SHENG.get(zhu) == ke:
        return "生"   # 主生客（泄氣）
    if WUXING_SHENG.get(ke) == zhu:
        return "被生"  # 客生主（吉）
    if WUXING_KE.get(zhu) == ke:
        return "克"   # 主克客
    if WUXING_KE.get(ke) == zhu:
        return "被克"  # 客克主
    return "無"


def count_forward_gan(from_gan: str, to_gan: str) -> int:
    """
    從 from_gan 順數到 to_gan，含 from_gan 計為第 1 位。
    對應《涤器遗诀》元數計算：「自胎干之丙，順數至年干己，得四數」。
    """
    f = tiangan_index(from_gan)
    t = tiangan_index(to_gan)
    diff = (t - f) % 10
    return diff + 1  # 從 from 計 1


def count_forward_zhi(from_zhi: str, to_zhi: str) -> int:
    """
    從 from_zhi 順數到 to_zhi，含 from_zhi 計為第 1 位。
    對應《涤器遗诀》影數計算：「自胎月之寅支，順數至生年丑支，得十二數」。
    """
    f = dizhi_index(from_zhi)
    t = dizhi_index(to_zhi)
    diff = (t - f) % 12
    return diff + 1  # 從 from 計 1


def reduce_number(n: int) -> int:
    """
    滿十去零（去十用零）：
    10 → 1（去0留十位1），11 → 1（去十留個位1），12 → 2。
    對應《涤器遗诀》「數至十一、十二者，棄其十位而只書一、二」。
    """
    if n <= 0:
        return 0
    if n == 10:
        return 1  # 「滿十數計之以一」—— 10去十位留零數0，但0視同空位故書1
    if n > 10:
        return n % 10 if n % 10 != 0 else 1
    return n


def qipao_position(wuxing: str, zhi: str) -> str:
    """
    起胞法：根據五行和地支，返回十二長生位置名。
    對應《涤器遗诀》起胞法章：「金寅、水土巳、木申、火亥當。皆順數。」
    """
    start_zhi = QIPAO_START.get(wuxing)
    if start_zhi is None:
        return "未知"
    start_idx = dizhi_index(start_zhi)
    target_idx = dizhi_index(zhi)
    pos = (target_idx - start_idx) % 12
    return SHIER_CHANGSHENG[pos]


def is_qipao_ji(position: str) -> bool:
    """
    起胞法吉凶判斷。
    吉：胎、養、生、帶(冠)、官、旺、墓。
    凶：敗、絕(胞)、衰、病、死。
    """
    return position in ("胎", "養", "生", "冠", "官", "旺", "墓")


# ============================================================
# 八卦體變相關
# ============================================================

def _yinyang_of(n: int) -> int:
    """奇為陽(1)，偶為陰(0)。0視為偶/陰。"""
    return 1 if n % 2 == 1 else 0


def bagua_tibian(four_pos: list) -> dict:
    """
    八卦體變例——根據四位的奇偶（陽陰）定本卦/變卦及先後上下五行。
    對應《涤器遗诀》八卦體變例章。

    參數：four_pos = [一位, 二位, 三位, 四位]
    返回字典包含：卦名、本/變、先卦、後卦、上五行、下五行。
    """
    yy = [_yinyang_of(p) for p in four_pos]

    # 本卦/變卦對照表（〇陽 ●陰）
    # 乾本 1111  乾變 1011
    # 巽本 1110  巽變 1100
    # 坎本 0110  坎變 0010
    # 離本 1001  離變 1101
    # 艮本 1000  艮變 1010
    # 坤本 0000  坤變 0100
    # 震本 0001  震變 0011
    # 兌本 0111  兌變 0101
    _map = {
        (1, 1, 1, 1): ("乾", "本"),
        (1, 0, 1, 1): ("乾", "變"),
        (1, 1, 1, 0): ("巽", "本"),
        (1, 1, 0, 0): ("巽", "變"),
        (0, 1, 1, 0): ("坎", "本"),
        (0, 0, 1, 0): ("坎", "變"),
        (1, 0, 0, 1): ("離", "本"),
        (1, 1, 0, 1): ("離", "變"),
        (1, 0, 0, 0): ("艮", "本"),
        (1, 0, 1, 0): ("艮", "變"),
        (0, 0, 0, 0): ("坤", "本"),
        (0, 1, 0, 0): ("坤", "變"),
        (0, 0, 0, 1): ("震", "本"),
        (0, 0, 1, 1): ("震", "變"),
        (0, 1, 1, 1): ("兌", "本"),
        (0, 1, 0, 1): ("兌", "變"),
    }

    key = tuple(yy)
    gua_name, ben_bian = _map.get(key, ("未知", "未知"))

    # 先後卦：先=1,2,3位構成三爻卦；後=2,3,4位構成三爻卦
    _three_yao_map = {
        (1, 1, 1): "乾", (0, 1, 1): "兌", (1, 0, 1): "離", (0, 0, 1): "震",
        (1, 1, 0): "巽", (0, 1, 0): "坎", (1, 0, 0): "艮", (0, 0, 0): "坤",
    }
    xian_gua = _three_yao_map.get(tuple(yy[:3]), "未知")
    hou_gua = _three_yao_map.get(tuple(yy[1:]), "未知")

    # 上下五行：上=1位+2位合數取零數；下=3位+4位合數取零數
    shang_sum = four_pos[0] + four_pos[1]
    xia_sum = four_pos[2] + four_pos[3]
    shang_wx = hetu_wuxing(shang_sum % 10)
    xia_wx = hetu_wuxing(xia_sum % 10)

    # 卦的五行
    gua_wuxing_map = {
        "乾": "金", "兌": "金", "離": "火", "震": "木",
        "巽": "木", "坎": "水", "艮": "土", "坤": "土",
    }

    return {
        "四位": four_pos,
        "陰陽": yy,
        "卦名": gua_name,
        "本變": ben_bian,
        "卦五行": gua_wuxing_map.get(gua_name, "未知"),
        "先卦": xian_gua,
        "後卦": hou_gua,
        "先卦五行": gua_wuxing_map.get(xian_gua, "未知"),
        "後卦五行": gua_wuxing_map.get(hou_gua, "未知"),
        "上數": shang_sum % 10,
        "上五行": shang_wx,
        "下數": xia_sum % 10,
        "下五行": xia_wx,
    }


# ============================================================
# 觀空定卦法
# ============================================================

def guankong_dinggua(four_pos: list) -> dict:
    """
    觀空定卦法——通過觀察本宮四位中是否含「〇」及互相組合滿十為空來定卦。
    對應《涤器遗诀》觀空定卦法章。

    全位空→坤  全不空→乾
    上三空→震  下三空→艮
    中位空→離  隔間空→坎
    上位空→兌  下位空→巽
    """
    a, b, c, d = four_pos

    total = a + b + c + d
    s234 = b + c + d  # 除一位
    s123 = a + b + c  # 除四位
    s14 = a + d       # 隔間
    s23 = b + c       # 中位
    s34 = c + d       # 下位
    s12 = a + b       # 上位

    # 檢查自身為0的情況（「不待滿十而本位自己皆空」）
    all_zero = (a == 0 and b == 0 and c == 0 and d == 0)

    # 全位空：四位合數滿十 (total % 10 == 0)
    quan_kong = (total % 10 == 0)
    # 各種空的情況
    xia_san_kong = (s234 % 10 == 0) and not quan_kong
    shang_san_kong = (s123 % 10 == 0) and not quan_kong
    ge_jian_kong = (s14 % 10 == 0) and (s23 % 10 != 0) and not quan_kong
    zhong_wei_kong = (s23 % 10 == 0) and (s14 % 10 != 0) and not quan_kong
    xia_wei_kong = (s34 % 10 == 0) and (s12 % 10 != 0) and not quan_kong
    shang_wei_kong = (s12 % 10 == 0) and (s34 % 10 != 0) and not quan_kong

    # 優先級：全空→全不空→其他
    if all_zero or quan_kong:
        gua = "坤"
        kong_type = "全位空"
    elif shang_san_kong:
        gua = "震"
        kong_type = "上三空"
    elif xia_san_kong:
        gua = "艮"
        kong_type = "下三空"
    elif zhong_wei_kong:
        gua = "離"
        kong_type = "中位空"
    elif ge_jian_kong:
        gua = "坎"
        kong_type = "隔間空"
    elif shang_wei_kong:
        gua = "兌"
        kong_type = "上位空"
    elif xia_wei_kong:
        gua = "巽"
        kong_type = "下位空"
    else:
        # 全不空
        gua = "乾"
        kong_type = "全不空"

    # 開閉數
    zong_ling = total % 10
    if zong_ling == 0:
        kai_bi = "閉數"
    else:
        kai_bi = "開數"

    gua_wuxing_map = {
        "乾": "金", "兌": "金", "離": "火", "震": "木",
        "巽": "木", "坎": "水", "艮": "土", "坤": "土",
    }

    return {
        "卦名": gua,
        "空類型": kong_type,
        "卦五行": gua_wuxing_map.get(gua, "未知"),
        "總數": total,
        "總零": zong_ling,
        "總零五行": hetu_wuxing(zong_ling),
        "開閉": kai_bi,
    }


# ============================================================
# 主要類別 DiQiYiJue
# ============================================================

class DiQiYiJue:
    """
    涤器遗诀（康節氣數 / 氣孕數 / 皇極數）完整排盤系統。

    嚴格依據《涤器遗诀》原文記載之全部古法實現。
    """

    def __init__(self, birth_ganzhi: dict, gender: str = "男"):
        """
        初始化排盤。

        參數：
            birth_ganzhi: dict，包含四柱干支，鍵為 "年", "月", "日", "時"。
                例如 {"年": "己丑", "月": "乙亥", "日": "庚寅", "時": "丁丑"}
            gender: str，「男」或「女」，用於屬齒卦等。
        """
        self.birth = birth_ganzhi
        self.gender = gender

        # 解析四柱
        self.year_gz = birth_ganzhi["年"]
        self.month_gz = birth_ganzhi["月"]
        self.day_gz = birth_ganzhi["日"]
        self.hour_gz = birth_ganzhi["時"]

        # 提取天干地支
        self.year_gan, self.year_zhi = self.year_gz[0], self.year_gz[1]
        self.month_gan, self.month_zhi = self.month_gz[0], self.month_gz[1]
        self.day_gan, self.day_zhi = self.day_gz[0], self.day_gz[1]
        self.hour_gan, self.hour_zhi = self.hour_gz[0], self.hour_gz[1]

        # 五條納音
        self.year_nayin = nayin_wuxing(self.year_gz)
        self.month_nayin = nayin_wuxing(self.month_gz)
        self.day_nayin = nayin_wuxing(self.day_gz)
        self.hour_nayin = nayin_wuxing(self.hour_gz)

        # 第一步：求胎月
        self.tai_gz = self._calc_tai_month()
        self.tai_gan, self.tai_zhi = self.tai_gz[0], self.tai_gz[1]
        self.tai_nayin = nayin_wuxing(self.tai_gz)

        # 五條（胎、年、月、日、時）
        self.wu_tiao = [self.tai_gz, self.year_gz, self.month_gz,
                        self.day_gz, self.hour_gz]
        self.wu_tiao_nayin = [self.tai_nayin, self.year_nayin,
                              self.month_nayin, self.day_nayin, self.hour_nayin]

        # 第二步：計算元數和影數
        self.yuan_shu, self.ying_shu = self._calc_yuan_ying()

        # 第三步：八宮起例（鋪地錦乘法）
        self.ba_gong_raw = self._calc_bagong()  # 8位數列表
        self.ba_gong_wuxing = []  # 八宮五行（含填空）
        self._fill_bagong_wuxing()

        # 第四步：先定本宮四位
        self.ben_gong_siwei = self._calc_bengong_siwei()

        # 第五步：觀空定卦
        self.guankong = guankong_dinggua(self.ben_gong_siwei)

        # 第六步：八卦體變
        self.bagua_tibian_result = bagua_tibian(self.ben_gong_siwei)

        # 第七步：先定命例（命宮、大運、小運）
        self.du_shu = sum(self.ba_gong_raw)  # 都數
        self.ming_gong_idx, self.ming_gong_wx = self._calc_ming_gong()
        self.dayun = self._calc_dayun()
        self.xiaoyun = self._calc_xiaoyun()

        # 第八步：求數尾、五條
        self.shu_wei = self._calc_shuwei()

        # 第九步：合孕數
        self.he_yun = self._calc_heyun()

        # 第十步：起胞法（八宮及本宮之吉凶）
        self.qipao_bagong = self._calc_qipao_bagong()
        self.qipao_bengong = self._calc_qipao_bengong()

        # 本宮別法（倫乳合、己養合、雁鬼合、翡基合）
        self.ben_gong_biefa = self._calc_bengong_biefa()

    # --------------------------------------------------------
    # 1. 胎月求法
    # --------------------------------------------------------
    def _calc_tai_month(self) -> str:
        """
        胎月求法——以月建「進干一位、進支四位」求之。
        對應《涤器遗诀》求胎月例章。

        如乙亥月建生人，進乙干一位則為丙，進亥支四位
        （亥上數1、子上數2、丑上數3、寅上數4）則為寅，胎月即為丙寅。
        """
        # 月干進一位
        gan_idx = (tiangan_index(self.month_gan) + 1) % 10
        # 月支進四位（從月支起數1,2,3,4——月支自身是第0位，後面第3位）
        # 「亥上數1、子上數2、丑上數3、寅上數4」→ 即月支 +3
        zhi_idx = (dizhi_index(self.month_zhi) + 3) % 12
        tai_gan = TIANGAN[gan_idx]
        tai_zhi = DIZHI[zhi_idx]
        return tai_gan + tai_zhi

    # --------------------------------------------------------
    # 2. 元數、影數計算
    # --------------------------------------------------------
    def _calc_yuan_ying(self) -> tuple:
        """
        計算元數（胎干→年月日時干）和影數（胎支→年月日時支）。
        對應《涤器遗诀》八宮起例章。

        元數：胎干分別順數到年、月、日、時干，滿十去零。
        影數：胎支分別順數到年、月、日、時支，滿十去零。
        """
        # 元數（胎干→年月日時干）
        y_gan = reduce_number(count_forward_gan(self.tai_gan, self.year_gan))
        m_gan = reduce_number(count_forward_gan(self.tai_gan, self.month_gan))
        d_gan = reduce_number(count_forward_gan(self.tai_gan, self.day_gan))
        h_gan = reduce_number(count_forward_gan(self.tai_gan, self.hour_gan))
        yuan = [y_gan, m_gan, d_gan, h_gan]

        # 影數（胎支→年月日時支）
        y_zhi = reduce_number(count_forward_zhi(self.tai_zhi, self.year_zhi))
        m_zhi = reduce_number(count_forward_zhi(self.tai_zhi, self.month_zhi))
        d_zhi = reduce_number(count_forward_zhi(self.tai_zhi, self.day_zhi))
        h_zhi = reduce_number(count_forward_zhi(self.tai_zhi, self.hour_zhi))
        ying = [y_zhi, m_zhi, d_zhi, h_zhi]

        return yuan, ying

    # --------------------------------------------------------
    # 3. 八宮起例（鋪地錦算法）
    # --------------------------------------------------------
    def _calc_bagong(self) -> list:
        """
        八宮起例——以鋪地錦算法（元影數乘法）求八宮數。
        對應《涤器遗诀》八宮起例章。

        簡法：元數四位組成數字 × 影數四位組成數字，
        結果不足八位在末尾補零。
        """
        # 元數組成四位數
        yuan_num = (self.yuan_shu[0] * 1000 + self.yuan_shu[1] * 100 +
                    self.yuan_shu[2] * 10 + self.yuan_shu[3])
        # 影數組成四位數
        ying_num = (self.ying_shu[0] * 1000 + self.ying_shu[1] * 100 +
                    self.ying_shu[2] * 10 + self.ying_shu[3])

        product = yuan_num * ying_num

        # 轉為字符串，不足八位在末尾補零
        prod_str = str(product)
        if len(prod_str) < 8:
            prod_str = prod_str + "0" * (8 - len(prod_str))

        # 取前八位
        result = [int(c) for c in prod_str[:8]]
        return result

    def _fill_bagong_wuxing(self):
        """
        填空法——為八宮各數字定河圖五行，空則按古法填入。
        對應《涤器遗诀》填空法章。

        己宮空→生年納音；雁宮空→生月納音；
        翡宮空→生日納音；乳宮空→生時納音。
        養、鬼、基三宮空→己宮五行。
        """
        raw = list(self.ba_gong_raw)

        # 尋找第一個非零數起排伦宫
        # 「左側斜格第一間無數，則自第二間安倫宮」
        start_offset = 0
        for i, v in enumerate(raw):
            if v != 0:
                start_offset = i
                break

        # 重新排列八宮：從第一個非零位開始
        rearranged = raw[start_offset:] + raw[:start_offset]

        # 如果不足8位，需要補充（正常情況下都是8位）
        while len(rearranged) < 8:
            rearranged.append(0)

        self.ba_gong_raw = rearranged[:8]

        # 為每宮定五行
        wuxing_list = []
        for i, val in enumerate(self.ba_gong_raw):
            if val == 0:
                # 填空法
                gong_name = BAGONG_NAMES[i]
                if gong_name == "己":
                    # 己宮空→生年納音
                    wuxing_list.append(self.year_nayin)
                elif gong_name == "雁":
                    # 雁宮空→生月納音
                    wuxing_list.append(self.month_nayin)
                elif gong_name == "翡":
                    # 翡宮空→生日納音
                    wuxing_list.append(self.day_nayin)
                elif gong_name == "乳":
                    # 乳宮空→生時納音
                    wuxing_list.append(self.hour_nayin)
                elif gong_name in ("養", "鬼", "基"):
                    # 養鬼基空→己宮五行
                    # 己宮始終在index 1（第二宮），必已處理
                    wuxing_list.append(wuxing_list[1])  # 己宮五行
                else:
                    # 倫宮不會空（從非空起排）
                    wuxing_list.append(hetu_wuxing(val))
            else:
                wuxing_list.append(hetu_wuxing(val))

        self.ba_gong_wuxing = wuxing_list

    # --------------------------------------------------------
    # 4. 先定本宮四位
    # --------------------------------------------------------
    def _calc_bengong_siwei(self) -> list:
        """
        先定本宮例——倫己合、雁翡合、乳養合、鬼基合，滿十升一。
        對應《涤器遗诀》先定本宮例章。

        從右往左計算：
        四位數 = 鬼 + 基
        三位數 = 乳 + 養（+ 進位）
        二位數 = 雁 + 翡（+ 進位）
        一位數 = 倫 + 己（+ 進位），若滿十自身再加一
        """
        bg = self.ba_gong_raw
        # 倫=bg[0], 己=bg[1], 雁=bg[2], 翡=bg[3]
        # 乳=bg[4], 養=bg[5], 鬼=bg[6], 基=bg[7]

        carry = 0

        # 四位數：鬼 + 基
        s4 = bg[6] + bg[7] + carry
        d4 = s4 % 10
        carry = s4 // 10

        # 三位數：乳 + 養
        s3 = bg[4] + bg[5] + carry
        d3 = s3 % 10
        carry = s3 // 10

        # 二位數：雁 + 翡
        s2 = bg[2] + bg[3] + carry
        d2 = s2 % 10
        carry = s2 // 10

        # 一位數：倫 + 己
        s1 = bg[0] + bg[1] + carry
        d1 = s1 % 10
        carry1 = s1 // 10
        # 「滿十則無可升處，故本位加計一數」
        d1 = (d1 + carry1) % 10

        return [d1, d2, d3, d4]

    # --------------------------------------------------------
    # 本宮別法（倫乳合、己養合、雁鬼合、翡基合）
    # --------------------------------------------------------
    def _calc_bengong_biefa(self) -> list:
        """
        本宮別法——倫乳合、己養合、雁鬼合、翡基合。
        對應《涤器遗诀》本宮別法章。

        此法不用滿十升一，滿十去零用一。
        """
        bg = self.ba_gong_raw

        def _reduce(n):
            if n == 10:
                return 1
            if n > 10:
                return n % 10 if n % 10 != 0 else 1
            return n

        d1 = _reduce(bg[0] + bg[4])  # 倫 + 乳
        d2 = _reduce(bg[1] + bg[5])  # 己 + 養
        d3 = _reduce(bg[2] + bg[6])  # 雁 + 鬼
        d4 = _reduce(bg[3] + bg[7])  # 翡 + 基
        return [d1, d2, d3, d4]

    # --------------------------------------------------------
    # 5. 觀空定卦 — 已在外部函數實現
    # 6. 八卦體變 — 已在外部函數實現
    # --------------------------------------------------------

    # --------------------------------------------------------
    # 7. 起胞法
    # --------------------------------------------------------
    def _calc_qipao_bagong(self) -> list:
        """
        起胞法——八宮各宮五行在生月之支的十二長生位。
        對應《涤器遗诀》起胞法章：「八位元命皆以本法起胞。觀生月之支值何位。」
        """
        results = []
        for i, wx in enumerate(self.ba_gong_wuxing):
            pos = qipao_position(wx, self.month_zhi)
            ji = is_qipao_ji(pos)
            results.append({
                "宮": BAGONG_NAMES[i],
                "數": self.ba_gong_raw[i],
                "五行": wx,
                "胞胎位": pos,
                "吉凶": "吉" if ji else "凶",
            })
        return results

    def _calc_qipao_bengong(self) -> list:
        """
        起胞法——本宮四位各位五行在生月之支的十二長生位。
        """
        results = []
        for i, val in enumerate(self.ben_gong_siwei):
            wx = hetu_wuxing(val)
            pos = qipao_position(wx, self.month_zhi)
            ji = is_qipao_ji(pos)
            results.append({
                "位": i + 1,
                "數": val,
                "五行": wx,
                "胞胎位": pos,
                "吉凶": "吉" if ji else "凶",
            })
        return results

    # --------------------------------------------------------
    # 8. 先定命例
    # --------------------------------------------------------
    def _calc_ming_gong(self) -> tuple:
        """
        先定命宮——都數定命宮。
        對應《涤器遗诀》先定命例章。

        總合八宮零數計之，自倫宮起一，順數八位，終到處為命。
        """
        du = self.du_shu
        if du == 0:
            return 0, self.ba_gong_wuxing[0]
        # 從倫宮起1，循環八宮
        idx = (du - 1) % 8
        return idx, self.ba_gong_wuxing[idx]

    def _calc_dayun(self) -> list:
        """
        大運——總數去十用零起算，從命宮起推，每運十年。
        對應《涤器遗诀》先定命例章大運部分。
        """
        ling = self.du_shu % 10
        if ling == 0:
            ling = 10  # 若零數為0，意為10

        dayun_list = []
        start_idx = self.ming_gong_idx
        # 命主大運：初一到初ling
        current_age = 1

        # 生成足夠多的大運（至少到100歲）
        i = 0
        while current_age <= 100:
            gong_idx = (start_idx + i) % 8
            age_start = current_age
            if i == 0:
                age_end = ling
            else:
                age_end = age_start + 9
            if age_start > 100:
                break
            dayun_list.append({
                "起始歲": age_start,
                "終止歲": min(age_end, 100),
                "宮": BAGONG_NAMES[gong_idx],
                "宮五行": self.ba_gong_wuxing[gong_idx],
            })
            current_age = age_end + 1
            i += 1

        return dayun_list

    def _calc_xiaoyun(self) -> list:
        """
        小運——從命宮起，一年行一位。
        對應《涤器遗诀》先定命例章小運部分。
        """
        xiaoyun_list = []
        for age in range(1, 101):
            gong_idx = (self.ming_gong_idx + age - 1) % 8
            xiaoyun_list.append({
                "歲": age,
                "宮": BAGONG_NAMES[gong_idx],
                "宮五行": self.ba_gong_wuxing[gong_idx],
            })
        return xiaoyun_list

    # --------------------------------------------------------
    # 9. 求數尾
    # --------------------------------------------------------
    def _calc_shuwei(self) -> dict:
        """
        求數尾例——本宮四位總計去十用零。
        對應《涤器遗诀》求數尾例章。

        尾數為四位合數之零數（個位數），尾數置於五條之末為子孫位。
        """
        total = sum(self.ben_gong_siwei)
        ling = total % 10
        wx = hetu_wuxing(ling)
        return {
            "總計": total,
            "零數": ling,
            "五行": wx,
            "與本卦關係": wuxing_relation(
                self.bagua_tibian_result["卦五行"], wx
            ),
        }

    # --------------------------------------------------------
    # 10. 合孕數
    # --------------------------------------------------------
    def _calc_heyun(self) -> dict:
        """
        求合孕數例——四位中上下為夫婦，中二位為孕數。
        對應《涤器遗诀》求合孕數例章。

        七為夫，四為婦。中五二為孕數。
        夫數宜得陽，婦數宜得陰。
        """
        sp = self.ben_gong_siwei
        fu = sp[0]   # 夫（一位）
        fu2 = sp[3]  # 婦（四位）
        yun1 = sp[1]  # 孕數一（二位）
        yun2 = sp[2]  # 孕數二（三位）

        fu_wx = hetu_wuxing(fu)
        fu2_wx = hetu_wuxing(fu2)
        yun_sum = yun1 + yun2
        yun_ling = yun_sum % 10
        fufu_sum = fu + fu2
        fufu_ling = fufu_sum % 10

        # 夫婦陰陽
        fu_yy = "陽" if fu % 2 == 1 else "陰"
        fu2_yy = "陽" if fu2 % 2 == 1 else "陰"

        # 得位判斷
        if fu_yy == "陽" and fu2_yy == "陰":
            dewei = "得位（吉）"
        elif fu_yy == "陰" and fu2_yy == "陽":
            dewei = "失位（凶）"
        elif fu_yy == fu2_yy:
            dewei = "純陰純陽（不佳）"
        else:
            dewei = "其他"

        # 夫婦生克
        fufu_rel = wuxing_relation(fu_wx, fu2_wx)

        # 孕數空否
        yun_kong = (yun1 == 0 and yun2 == 0)
        yun_po = (yun_sum % 10 == 0 and yun_sum > 0)  # 破孕

        # 男女判斷（以孕數零數奇偶）
        if yun_kong:
            nan_nv = "無子（孕空）"
        elif yun_po:
            nan_nv = "落胎（破孕）"
        elif yun1 == 0 or yun2 == 0:
            # 一位空
            eff = yun1 if yun1 != 0 else yun2
            nan_nv = "陽（男多）" if eff % 2 == 1 else "陰（女多）"
        else:
            nan_nv = "陽（男多）" if yun_ling % 2 == 1 else "陰（女多）"

        return {
            "夫": {"數": fu, "五行": fu_wx, "陰陽": fu_yy},
            "婦": {"數": fu2, "五行": fu2_wx, "陰陽": fu2_yy},
            "得位": dewei,
            "夫婦關係": fufu_rel,
            "夫婦合數": fufu_sum,
            "夫婦合零": fufu_ling,
            "孕一": yun1,
            "孕二": yun2,
            "孕合數": yun_sum,
            "孕零數": yun_ling,
            "孕空": yun_kong,
            "破孕": yun_po,
            "男女": nan_nv,
        }

    # --------------------------------------------------------
    # 流籌別法（本宮別法四位 × 行年）
    # --------------------------------------------------------
    def flow_year_biefa(self, year_ganzhi: str = None, age: int = None) -> dict:
        """
        流籌別法——以本宮別法四位×行年，取中間四位。
        對應《涤器遗诀》本宮別法章。

        「金始振以此法為是。流籌亦以此求之。」
        別法四位 × 行年 → 取中間四位為流籌。
        """
        if age is None:
            raise ValueError("必須提供行年歲數 age")

        bp = self.ben_gong_biefa
        yuan_num = bp[0] * 1000 + bp[1] * 100 + bp[2] * 10 + bp[3]
        product = yuan_num * age
        prod_str = str(product)
        digits = [int(c) for c in prod_str]

        tui_shu = None
        ruan_shu = None

        if len(digits) >= 6:
            tui_shu = digits[0]
            ruan_shu = digits[-1]
            liu_chou = digits[1:5]
        elif len(digits) == 5:
            tui_shu = digits[0]
            liu_chou = digits[1:5]
        elif len(digits) == 4:
            liu_chou = digits[:]
        else:
            while len(digits) < 4:
                digits.insert(0, 0)
            liu_chou = digits[:4]

        lc_tibian = bagua_tibian(liu_chou)

        return {
            "方法": "本宮別法",
            "本宮別法四位": bp,
            "行年": age,
            "乘積": product,
            "退數": tui_shu,
            "軟數": ruan_shu,
            "流籌四位": liu_chou,
            "八卦體變": lc_tibian,
            "觀空定卦": guankong_dinggua(liu_chou),
        }

    # --------------------------------------------------------
    # 11. 屬齒卦（年齡行卦）
    # --------------------------------------------------------
    def shu_chi_gua(self, age: int) -> str:
        """
        屬齒卦——男十歲起兌順行，女十歲起兌逆行。
        對應《涤器遗诀》求屬齒卦章。

        後天卦順序：兌→乾→坎→艮→震→巽→離→坤
        """
        if age < 10:
            # 十歲以下無齒卦
            return "未及齒卦（未滿十歲）"

        offset = age - 10
        if self.gender == "男":
            idx = offset % 8
        else:
            idx = (-offset) % 8  # 逆行
        return BAGUA_HOUTIAN_ORDER[idx]

    # --------------------------------------------------------
    # 12. 八觀法
    # --------------------------------------------------------
    def baguan(self, zhu_gua: str, ke_zhi: str) -> str:
        """
        八觀法——以主卦觀客方地支之八觀。
        對應《涤器遗诀》八觀法章。

        先將地支轉為所屬卦，再查八觀關係。
        """
        ke_gua = DIZHI_TO_GUA.get(ke_zhi, None)
        if ke_gua is None:
            return "未知"
        return BAGUAN_TABLE.get(zhu_gua, {}).get(ke_gua, "未知")

    # --------------------------------------------------------
    # 13. 流籌卦算法
    # --------------------------------------------------------
    def flow_year(self, year_ganzhi: str = None, age: int = None) -> dict:
        """
        流籌卦算法——以本宮四位×行年，折外補中法。
        對應《涤器遗诀》求流籌卦算法章。

        參數：
            year_ganzhi: 流年干支（如「壬申」），用於八觀等判斷
            age: 行年歲數（從出生年當年算起為1）

        「以本宮四位置元數，以行年置影數，畫作格圖。」
        """
        if age is None:
            raise ValueError("必須提供行年歲數 age")

        # 本宮四位
        bp = self.ben_gong_siwei
        # 元數：四位組成的數
        yuan_num = bp[0] * 1000 + bp[1] * 100 + bp[2] * 10 + bp[3]

        # 影數：行年
        ying_num = age

        product = yuan_num * ying_num
        prod_str = str(product)
        digits = [int(c) for c in prod_str]

        # 提取流籌四位：
        # 《涤器遗诀》：「乘得中間四位畫之格中，其前後零數則為棄數，
        # 前數為退數，後數為軟數。」
        # 6位數：退(1位) + 流籌四位(中間4位) + 軟(1位)
        # 5位數：退(1位) + 流籌四位(後4位)
        # 4位數：全部即為流籌四位
        # 7+位數：先折外補中（頭兩位合、尾兩位合）再提取
        tui_shu = None  # 退數
        ruan_shu = None  # 軟數

        while len(digits) > 6:
            # 折外補中：頭兩位相加，尾兩位相加
            head = digits[0] + digits[1]
            tail = digits[-2] + digits[-1]
            mid = digits[2:-2]
            new_digits = []
            # 頭部（可能>=10，需進位到自身）
            new_digits.append(head)
            new_digits.extend(mid)
            new_digits.append(tail)
            # 從右向左處理進位
            carry = 0
            for i in range(len(new_digits) - 1, -1, -1):
                new_digits[i] += carry
                carry = new_digits[i] // 10
                new_digits[i] %= 10
            if carry > 0:
                new_digits.insert(0, carry)
            digits = new_digits

        if len(digits) >= 6:
            tui_shu = digits[0]
            ruan_shu = digits[-1]
            liu_chou = digits[1:5]
        elif len(digits) == 5:
            tui_shu = digits[0]
            liu_chou = digits[1:5]
        elif len(digits) == 4:
            liu_chou = digits[:]
        else:
            # 不足4位，左邊補零
            while len(digits) < 4:
                digits.insert(0, 0)
            liu_chou = digits[:4]

        # 流籌卦分析
        lc_guankong = guankong_dinggua(liu_chou)
        lc_tibian = bagua_tibian(liu_chou)

        # 齒卦
        chi_gua = self.shu_chi_gua(age) if age >= 10 else "未及"

        # 齒卦與流籌卦八觀
        chi_liuchou_baguan = ""
        if chi_gua not in ("未及齒卦（未滿十歲）", "未及"):
            lc_gua = lc_tibian["卦名"]
            chi_liuchou_baguan = BAGUAN_TABLE.get(chi_gua, {}).get(lc_gua, "未知")

        # 流籌卦與年支八觀
        lc_year_baguan = ""
        if year_ganzhi and len(year_ganzhi) >= 2:
            year_zhi = year_ganzhi[1]
            lc_year_baguan = self.baguan(lc_tibian["卦名"], year_zhi)

        # 觀數五章
        guan_wu = self._guanshu_wuzhang(liu_chou)

        # 貼星
        zei_xing = self._calc_zeixing(liu_chou)

        # 客運卦
        lc_total = sum(liu_chou)
        lc_ling = lc_total % 10
        ke_yun_gua_num = liu_chou[0] + liu_chou[1]  # 簡化：六三式
        # 不足時用總數

        # 大運所在
        dayun_info = None
        for dy in self.dayun:
            if dy["起始歲"] <= age <= dy["終止歲"]:
                dayun_info = dy
                break

        # 小運所在
        xiaoyun_info = None
        if 1 <= age <= len(self.xiaoyun):
            xiaoyun_info = self.xiaoyun[age - 1]

        return {
            "行年": age,
            "流年干支": year_ganzhi or "",
            "乘積": product,
            "流籌四位": liu_chou,
            "觀空定卦": lc_guankong,
            "八卦體變": lc_tibian,
            "齒卦": chi_gua,
            "齒卦與流籌八觀": chi_liuchou_baguan,
            "流籌與年支八觀": lc_year_baguan,
            "觀數五章": guan_wu,
            "賊星": zei_xing,
            "總數": lc_total,
            "總零": lc_ling,
            "總零五行": hetu_wuxing(lc_ling),
            "大運": dayun_info,
            "小運": xiaoyun_info,
        }

    # --------------------------------------------------------
    # 14. 觀數五章
    # --------------------------------------------------------
    def _guanshu_wuzhang(self, four_pos: list) -> dict:
        """
        觀數五章——陰陽眾寡、數位順逆、五行連疊、賊星、總數奇偶。
        對應《涤器遗诀》觀數五章及《推算錄》相關章節。
        """
        # 一、陰陽眾寡
        yang_count = sum(1 for x in four_pos if x % 2 == 1)
        yin_count = 4 - yang_count

        if yang_count == yin_count:
            yinyang = "陰陽平分（吉）"
        elif yang_count > yin_count:
            yinyang = f"陽眾陰寡（陽{yang_count}陰{yin_count}）"
        else:
            yinyang = f"陰眾陽寡（陰{yin_count}陽{yang_count}）"

        # 二、數位順逆
        shunni = self._check_shunni(four_pos)

        # 三、五行連疊
        wx_list = [hetu_wuxing(x) for x in four_pos]
        liandie = self._check_liandie(wx_list)

        # 四、賊星
        zei = self._calc_zeixing(four_pos)

        # 五、總數奇偶
        total = sum(four_pos)
        ling = total % 10
        ji_ou = "奇" if ling % 2 == 1 else "偶"

        return {
            "陰陽眾寡": yinyang,
            "數位順逆": shunni,
            "五行連疊": liandie,
            "賊星": zei,
            "總餘": ling,
            "總餘奇偶": ji_ou,
        }

    def _check_shunni(self, fp: list) -> str:
        """檢查四位的順逆情況。"""
        shun_count = 0
        ni_count = 0
        for i in range(len(fp) - 1):
            if fp[i + 1] > fp[i]:
                shun_count += 1
            elif fp[i + 1] < fp[i]:
                ni_count += 1
        if shun_count == 3:
            return "四位俱順（登科第一）"
        if ni_count == 3:
            return "四位俱逆（成事歸虛）"
        if shun_count == 2 and ni_count == 1:
            return "三順一逆（運數平常）"
        if shun_count == 1 and ni_count == 2:
            return "一順三逆（觸事見害）"
        if shun_count == ni_count:
            return "二順二逆（吉凶散錯）"
        return "平"

    def _check_liandie(self, wx_list: list) -> str:
        """檢查五行連疊（相鄰同五行）。"""
        max_run = 1
        cur_run = 1
        run_wx = wx_list[0]
        for i in range(1, len(wx_list)):
            if wx_list[i] == wx_list[i - 1]:
                cur_run += 1
                if cur_run > max_run:
                    max_run = cur_run
                    run_wx = wx_list[i]
            else:
                cur_run = 1

        liandie_desc = {
            "金": "金之比疊者，遭刑殺損財貨",
            "木": "木之比疊者，陰密之事或風散之嘆",
            "水": "水之比疊者，淫事之謗或死別生離",
            "火": "火之比疊者，口舌爭訟之辨",
            "土": "土之比疊者，萬事遲鈍",
        }

        if max_run >= 4:
            return f"四位連疊（{run_wx}）——一年動靜莫非辛苦憂患。{liandie_desc.get(run_wx, '')}"
        if max_run >= 3:
            return f"三位連疊（{run_wx}）——尋者遠失，存者遠亡。{liandie_desc.get(run_wx, '')}"
        if max_run >= 2:
            return f"二位連疊（{run_wx}）——所謀阻滯，成敗無常。{liandie_desc.get(run_wx, '')}"
        return "無連疊"

    def _calc_zeixing(self, liu_chou: list) -> list:
        """
        賊星——行年四位中有而八宮中無之數。
        對應《涤器遗诀》觀數五章賊星章。
        """
        bagong_set = set(self.ba_gong_raw)
        zei = []
        for val in liu_chou:
            if val not in bagong_set and val != 0:
                zei.append(val)
        return list(set(zei))

    # --------------------------------------------------------
    # 15. 四位觀八觀法
    # --------------------------------------------------------
    def siwei_baguan(self, four_pos: list, start_year_gz: str = None) -> list:
        """
        四位觀八觀法——本宮卦自生年起數，流籌卦自當年起數。
        對應《涤器遗诀》四位觀八觀法章。

        分別從起始年起1，數至四位中的其中一位，
        將所數得之地支與四位所成之卦進行八觀。
        """
        if start_year_gz is None:
            start_year_gz = self.year_gz

        start_zhi_idx = dizhi_index(start_year_gz[1])
        tibian = bagua_tibian(four_pos)
        gua_name = tibian["卦名"]

        results = []
        for i, val in enumerate(four_pos):
            if val == 0:
                results.append({
                    "位": i + 1,
                    "數": val,
                    "地支": "空",
                    "八觀": "空位",
                })
                continue
            # 從起始年支起1，數到val
            target_zhi_idx = (start_zhi_idx + val - 1) % 12
            target_zhi = DIZHI[target_zhi_idx]
            # 找到對應的六十甲子（這裡只用地支做八觀）
            bg = self.baguan(gua_name, target_zhi)
            results.append({
                "位": i + 1,
                "數": val,
                "地支": target_zhi,
                "干支": TIANGAN[(tiangan_index(start_year_gz[0]) + val - 1) % 10] + target_zhi,
                "八觀": bg,
            })
        return results

    # --------------------------------------------------------
    # 16. 盈卦（四位換六爻卦 + 動爻）
    # --------------------------------------------------------
    def ying_gua(self, four_pos: list = None) -> dict:
        """
        盈卦——以四位合數換六爻卦及動爻。
        對應《涤器遗诀》盈卦相關章節。

        上卦 = (一位 + 四位) 除八取餘，
        下卦 = (二位 + 三位) 除八取餘，
        動爻 = 四位總和 除六取餘。
        先天卦序：1乾 2兌 3離 4震 5巽 6坎 7艮 8坤
        """
        if four_pos is None:
            four_pos = self.ben_gong_siwei

        xiantian_gua = {1: "乾", 2: "兌", 3: "離", 4: "震",
                        5: "巽", 6: "坎", 7: "艮", 0: "坤"}

        shang_sum = four_pos[0] + four_pos[3]
        xia_sum = four_pos[1] + four_pos[2]
        total = sum(four_pos)

        shang_gua_num = shang_sum % 8
        xia_gua_num = xia_sum % 8
        dong_yao = total % 6
        if dong_yao == 0:
            dong_yao = 6

        shang_gua = xiantian_gua.get(shang_gua_num, "坤")
        xia_gua = xiantian_gua.get(xia_gua_num, "坤")

        return {
            "上卦": shang_gua,
            "下卦": xia_gua,
            "上卦數": shang_sum,
            "下卦數": xia_sum,
            "動爻": dong_yao,
            "總數": total,
        }

    # --------------------------------------------------------
    # 17. 二十四山高平低起數
    # --------------------------------------------------------
    @staticmethod
    def ershisi_shan_qishu(shan_data: dict) -> dict:
        """
        二十四山高平低三等起數——葬山造宅用。
        對應《涤器遗诀》二十四位高平低三等起數章。

        參數：shan_data: dict，鍵為山名（乾、戌、亥等），值為「高」「平」「低」。

        高、平、低三等數值需查表（原書數據）。
        返回八宮數及四位數。
        """
        # 二十四山三等起數表（根據原文，括號內為成師遺錄數據）
        # 此處採用涤器遗诀之數
        _shan_table = {
            "乾": {"高": 40, "平": 30, "低": 20},
            "戌": {"高": 36, "平": 27, "低": 18},
            "亥": {"高": 44, "平": 33, "低": 22},
            "壬": {"高": 28, "平": 21, "低": 14},
            "子": {"高": 36, "平": 27, "低": 18},
            "癸": {"高": 52, "平": 39, "低": 26},
            "丑": {"高": 24, "平": 18, "低": 12},
            "艮": {"高": 32, "平": 24, "低": 16},
            "寅": {"高": 28, "平": 21, "低": 14},
            "甲": {"高": 16, "平": 12, "低": 8},
            "卯": {"高": 8, "平": 6, "低": 4},
            "乙": {"高": 8, "平": 6, "低": 4},
            "辰": {"高": 20, "平": 15, "低": 10},
            "巽": {"高": 32, "平": 24, "低": 16},
            "巳": {"高": 38, "平": 28, "低": 19},
            "丙": {"高": 36, "平": 27, "低": 18},
            "午": {"高": 36, "平": 27, "低": 18},
            "丁": {"高": 42, "平": 32, "低": 21},
            "未": {"高": 44, "平": 33, "低": 22},
            "坤": {"高": 56, "平": 42, "低": 28},
            "申": {"高": 50, "平": 38, "低": 25},
            "庚": {"高": 44, "平": 33, "低": 22},
            "酉": {"高": 28, "平": 21, "低": 14},
            "辛": {"高": 32, "平": 24, "低": 16},
        }

        # 八宮分組（每三山一組）
        groups = [
            ("乾", "戌", "亥"),   # 1-伦
            ("壬", "子", "癸"),   # 2-己
            ("丑", "艮", "寅"),   # 3-雁
            ("甲", "卯", "乙"),   # 4-翡
            ("辰", "巽", "巳"),   # 5-乳
            ("丙", "午", "丁"),   # 6-養
            ("未", "坤", "申"),   # 7-鬼
            ("庚", "酉", "辛"),   # 8-基
        ]

        bagong_nums = []
        for group in groups:
            total = 0
            for shan in group:
                level = shan_data.get(shan, "平")
                total += _shan_table.get(shan, {}).get(level, 0)
            bagong_nums.append(total)

        # 取零數為八宮
        bagong_ling = [n % 10 for n in bagong_nums]

        # 兩兩合成四位（同先定本宫之法）
        carry = 0
        s4 = bagong_ling[6] + bagong_ling[7] + carry
        d4 = s4 % 10
        carry = s4 // 10

        s3 = bagong_ling[4] + bagong_ling[5] + carry
        d3 = s3 % 10
        carry = s3 // 10

        s2 = bagong_ling[2] + bagong_ling[3] + carry
        d2 = s2 % 10
        carry = s2 // 10

        s1 = bagong_ling[0] + bagong_ling[1] + carry
        d1 = s1 % 10
        carry1 = s1 // 10
        d1 = (d1 + carry1) % 10

        siwei = [d1, d2, d3, d4]

        # 數尾
        sw_total = sum(siwei)
        sw_ling = sw_total % 10

        return {
            "八宮原數": bagong_nums,
            "八宮零數": bagong_ling,
            "八宮五行": [hetu_wuxing(x) for x in bagong_ling],
            "四位": siwei,
            "數尾": sw_ling,
            "數尾五行": hetu_wuxing(sw_ling),
        }

    # --------------------------------------------------------
    # 18. 離合推算、到任推算、造屋推算
    # --------------------------------------------------------
    @staticmethod
    def lihe_calc(year_zhi: str, month_num: int, day_num: int,
                  hour_zhi: str, person_age: int) -> dict:
        """
        離合推算——以某年月日時分為元影數求四位。
        對應《涤器遗诀》離合推算章。

        年、時用地支序數；月、日用數字本身（滿十去零）。
        元數 = 年×日，影數 = 月×時。
        本宮 = 元×影，流籌 = 本宮×年數。
        """
        year_num = reduce_number(dizhi_index(year_zhi) + 1)
        hour_num = reduce_number(dizhi_index(hour_zhi) + 1)
        day_reduced = reduce_number(day_num)
        month_reduced = reduce_number(month_num)

        yuan = year_num * 10 + day_reduced  # 年、日為元
        ying = month_reduced * 10 + hour_num  # 月、時為影

        bengong_product = yuan * ying

        # 本宮 × 年數
        liuchou_product = bengong_product * person_age
        prod_str = str(liuchou_product)

        # 提取中間四位（同流籌法）
        digits = [int(c) for c in prod_str]
        if len(digits) >= 6:
            siwei = digits[1:5]
        elif len(digits) == 5:
            siwei = digits[1:5]
        elif len(digits) == 4:
            siwei = digits[:]
        else:
            while len(digits) < 4:
                digits.insert(0, 0)
            siwei = digits[:4]

        return {
            "元數": yuan,
            "影數": ying,
            "本宮乘積": bengong_product,
            "流籌乘積": liuchou_product,
            "四位": siwei,
            "觀空定卦": guankong_dinggua(siwei),
            "八卦體變": bagua_tibian(siwei),
        }

    # --------------------------------------------------------
    # 19. 三奇吉門
    # --------------------------------------------------------
    def san_qi_ji_men(self) -> dict:
        """
        三奇吉門——生氣、天宜、福德為三奇。
        對應《涤器遗诀》三奇吉門章。

        以本宮卦象數考之年月日時之支，
        得卦或數若符合則為三奇吉門。
        """
        # 先確定命卦（觀空定卦或八卦體變所得卦）
        ming_gua = self.bagua_tibian_result["卦名"]

        # 四管地支
        four_zhi = [self.year_zhi, self.month_zhi, self.day_zhi, self.hour_zhi]

        # 各地支與命卦的八觀
        results = []
        san_qi_count = 0
        for i, zhi in enumerate(four_zhi):
            bg = self.baguan(ming_gua, zhi)
            is_san_qi = bg in ("生氣", "天宜", "福德")
            if is_san_qi:
                san_qi_count += 1
            results.append({
                "柱": ["年", "月", "日", "時"][i],
                "地支": zhi,
                "八觀": bg,
                "三奇": is_san_qi,
            })

        return {
            "命卦": ming_gua,
            "四管八觀": results,
            "三奇數": san_qi_count,
            "有三奇": san_qi_count > 0,
        }

    # --------------------------------------------------------
    # 20. 貴格判定
    # --------------------------------------------------------
    def gui_ge(self) -> list:
        """
        消殺貴格——判定各種貴格。
        對應《涤器遗诀》消殺貴格章（三十六貴格部分）。
        """
        guis = []

        # 五條納音
        tai_ny = self.tai_nayin
        nians = [self.year_nayin, self.month_nayin, self.day_nayin, self.hour_nayin]

        # 1. 仙宮貴人：年月日時納音俱生胎月納音
        all_sheng_tai = all(
            WUXING_SHENG.get(ny) == tai_ny or ny == tai_ny
            for ny in nians
        )
        if all_sheng_tai:
            guis.append("仙宮貴人")

        # 2. 學堂貴人：生月、生日之納音並與胎月比和
        if self.month_nayin == tai_ny and self.day_nayin == tai_ny:
            guis.append("學堂貴人")

        # 3. 養閒貴人：四水一火、四火一金等
        wx_counts = {}
        for ny in self.wu_tiao_nayin:
            wx_counts[ny] = wx_counts.get(ny, 0) + 1
        yangxian_patterns = [
            ({"水": 4, "火": 1}), ({"火": 4, "金": 1}),
            ({"金": 4, "木": 1}), ({"木": 4, "土": 1}),
            ({"土": 4, "水": 1}),
        ]
        for pat in yangxian_patterns:
            if all(wx_counts.get(k, 0) >= v for k, v in pat.items()):
                guis.append("養閒貴人")
                break

        # 4. 龍虎貴人：四木一火、四火一土等
        longhu_patterns = [
            ({"木": 4, "火": 1}), ({"火": 4, "土": 1}),
            ({"土": 4, "金": 1}), ({"金": 4, "水": 1}),
            ({"水": 4, "木": 1}),
        ]
        for pat in longhu_patterns:
            if all(wx_counts.get(k, 0) >= v for k, v in pat.items()):
                guis.append("龍虎貴人")
                break

        # 5. 文星貴人：三丙一甲等（看天干）
        gans = [self.year_gan, self.month_gan, self.day_gan, self.hour_gan]
        gan_counts = {}
        for g in gans:
            gan_counts[g] = gan_counts.get(g, 0) + 1
        wenxing_patterns = [
            ("丙", 3, "甲"), ("丁", 3, "乙"), ("戊", 3, "丙"),
            ("己", 3, "丁"), ("庚", 3, "戊"), ("辛", 3, "己"),
            ("壬", 3, "庚"), ("癸", 3, "辛"), ("甲", 3, "壬"),
            ("乙", 3, "癸"),
        ]
        for g3, cnt, g1 in wenxing_patterns:
            if gan_counts.get(g3, 0) >= cnt and gan_counts.get(g1, 0) >= 1:
                guis.append("文星貴人")
                break

        # 6. 天乙貴人：兩甲兩乙胎逢水等
        all_gans = gans + [self.tai_gan]
        tiangan_pair_counts = {}
        for g in all_gans:
            tiangan_pair_counts[g] = tiangan_pair_counts.get(g, 0) + 1
        tianyi_checks = [
            (["甲", "乙"], "水"), (["丙", "丁"], "木"),
            (["戊", "己"], "火"), (["庚", "辛"], "土"),
            (["壬", "癸"], "金"),
        ]
        for pair, tai_wx in tianyi_checks:
            c1 = tiangan_pair_counts.get(pair[0], 0)
            c2 = tiangan_pair_counts.get(pair[1], 0)
            if c1 >= 2 and c2 >= 2 and self.tai_nayin == tai_wx:
                guis.append("天乙貴人")
                break

        # 7. 鄉井貴人：五干相生
        all_5gans = [self.tai_gan, self.year_gan, self.month_gan,
                     self.day_gan, self.hour_gan]
        # 檢查連續相生（簡化判斷）
        gan_wuxing = []
        _gan_wx_map = {
            "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
            "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
        }
        for g in all_5gans:
            gan_wuxing.append(_gan_wx_map[g])
        # 相鄰皆生
        all_sheng = True
        for i in range(len(gan_wuxing) - 1):
            if WUXING_SHENG.get(gan_wuxing[i]) != gan_wuxing[i + 1]:
                all_sheng = False
                break
        if all_sheng and self.hour_nayin == self.tai_nayin:
            guis.append("鄉井貴人")

        # 12. 壽星貴人：胎干與日時干相對，胎支與日時支相對
        def _xiangdui_gan(g1, g2):
            return abs(tiangan_index(g1) - tiangan_index(g2)) == 5

        def _xiangdui_zhi(z1, z2):
            return abs(dizhi_index(z1) - dizhi_index(z2)) == 6

        if (_xiangdui_gan(self.tai_gan, self.day_gan) and
                _xiangdui_zhi(self.tai_zhi, self.day_zhi)):
            guis.append("壽星貴人（日）")
        if (_xiangdui_gan(self.tai_gan, self.hour_gan) and
                _xiangdui_zhi(self.tai_zhi, self.hour_zhi)):
            guis.append("壽星貴人（時）")

        return guis

    # --------------------------------------------------------
    # 21. 凶星判定
    # --------------------------------------------------------
    def xiong_xing(self) -> list:
        """
        凶星——根據生日及四干判定各種凶格。
        對應《涤器遗诀》凶星章。
        """
        xiongs = []
        gans = [self.year_gan, self.month_gan, self.day_gan, self.hour_gan]
        gan_counts = {}
        for g in gans:
            gan_counts[g] = gan_counts.get(g, 0) + 1

        # 簡化判斷示例（完整版需根據生日分類）
        # 四丙者斬
        if gan_counts.get("丙", 0) >= 4:
            xiongs.append("四丙凶星")
        if gan_counts.get("丁", 0) >= 4:
            xiongs.append("四丁凶星")
        if gan_counts.get("庚", 0) >= 4:
            xiongs.append("四庚凶星")
        if gan_counts.get("戊", 0) >= 4 or gan_counts.get("己", 0) >= 4:
            xiongs.append("四戊/四己凶星")

        return xiongs

    # --------------------------------------------------------
    # 22. 關殺
    # --------------------------------------------------------
    def guan_sha(self) -> list:
        """
        關殺——五宮三位與五條納音相克等各種關殺。
        對應《涤器遗诀》關殺章。
        """
        guan_list = []

        # 五宮與五條納音相克
        wugong_nayin_pairs = [
            (0, self.tai_nayin, "倫"),   # 伦宮與胎納音
            (1, self.year_nayin, "己"),   # 己宮與年納音
            (2, self.month_nayin, "雁"),  # 雁宮與月納音
            (3, self.day_nayin, "翡"),    # 翡宮與日納音
            (4, self.hour_nayin, "乳"),   # 乳宮與時納音
        ]

        for gong_idx, ny, gong_name in wugong_nayin_pairs:
            gong_wx = self.ba_gong_wuxing[gong_idx]
            rel = wuxing_relation(gong_wx, ny)
            if "克" in rel:
                guan_list.append(f"{gong_name}宮{gong_wx}與{ny}納音相克——關殺")

        # 伦宮與胎干
        lun_wx = self.ba_gong_wuxing[0]
        tai_gan_wx = {"甲": "木", "乙": "木", "丙": "火", "丁": "火",
                      "戊": "土", "己": "土", "庚": "金", "辛": "金",
                      "壬": "水", "癸": "水"}.get(self.tai_gan, "")
        if tai_gan_wx:
            rel = wuxing_relation(lun_wx, tai_gan_wx)
            if "克" in rel:
                guan_list.append(f"倫宮{lun_wx}與胎干{self.tai_gan}{tai_gan_wx}相克——關殺")

        # 翡宮與日支
        fei_wx = self.ba_gong_wuxing[3]
        day_zhi_wx = {"子": "水", "丑": "土", "寅": "木", "卯": "木",
                      "辰": "土", "巳": "火", "午": "火", "未": "土",
                      "申": "金", "酉": "金", "戌": "土", "亥": "水"}.get(self.day_zhi, "")
        if day_zhi_wx:
            rel = wuxing_relation(fei_wx, day_zhi_wx)
            if "克" in rel:
                guan_list.append(f"翡宮{fei_wx}與日支{self.day_zhi}{day_zhi_wx}相克——關殺")

        # 對沖關殺
        chong_pairs = [("子", "午"), ("丑", "未"), ("寅", "申"),
                       ("卯", "酉"), ("辰", "戌"), ("巳", "亥")]
        zhis = [self.year_zhi, self.month_zhi, self.day_zhi, self.hour_zhi]
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                for p in chong_pairs:
                    if (zhis[i] == p[0] and zhis[j] == p[1]) or \
                       (zhis[i] == p[1] and zhis[j] == p[0]):
                        guan_list.append(
                            f"對沖關殺：{['年','月','日','時'][i]}支{zhis[i]}"
                            f"沖{['年','月','日','時'][j]}支{zhis[j]}"
                        )

        # 疊關殺（四條納音與本宮命數比疊）
        bengong = self.ben_gong_siwei
        nayin_pairs = [
            (self.year_nayin, bengong[0], "年"),
            (self.month_nayin, bengong[1], "月"),
            (self.day_nayin, bengong[2], "日"),
            (self.hour_nayin, bengong[3], "時"),
        ]
        for ny, num, name in nayin_pairs:
            if ny == hetu_wuxing(num):
                guan_list.append(f"疊關殺：{name}納音{ny}與本宮{name}位{num}{hetu_wuxing(num)}比疊")

        return guan_list

    # --------------------------------------------------------
    # 23. 命主（內外盤）
    # --------------------------------------------------------
    def ming_zhu(self) -> dict:
        """
        命主——合天干數定外盤命主，合地支數定內盤命主。
        對應《涤器遗诀》命主章。

        合「未去十、去零前」的元數以其零餘定五行為外盤命主；
        合「未去十、去零前」的影數以其零餘定五行為內盤命主。
        """
        # 原始元數（未去十）
        raw_yuan = [
            count_forward_gan(self.tai_gan, self.year_gan),
            count_forward_gan(self.tai_gan, self.month_gan),
            count_forward_gan(self.tai_gan, self.day_gan),
            count_forward_gan(self.tai_gan, self.hour_gan),
        ]
        # 原始影數（未去十）
        raw_ying = [
            count_forward_zhi(self.tai_zhi, self.year_zhi),
            count_forward_zhi(self.tai_zhi, self.month_zhi),
            count_forward_zhi(self.tai_zhi, self.day_zhi),
            count_forward_zhi(self.tai_zhi, self.hour_zhi),
        ]

        yuan_total = sum(raw_yuan)
        ying_total = sum(raw_ying)

        wai_ling = yuan_total % 10
        nei_ling = ying_total % 10

        return {
            "外盤命主": {
                "原始元數": raw_yuan,
                "合數": yuan_total,
                "零數": wai_ling,
                "五行": hetu_wuxing(wai_ling),
            },
            "內盤命主": {
                "原始影數": raw_ying,
                "合數": ying_total,
                "零數": nei_ling,
                "五行": hetu_wuxing(nei_ling),
            },
        }

    # --------------------------------------------------------
    # 24. 行運別法
    # --------------------------------------------------------
    def xingyun_biefa(self, age: int) -> dict:
        """
        行運別法——以年齡數五行定大運星。
        對應《涤器遗诀》行運別法章。

        初一、十一、廿一為水；初五、十五、廿五為土。
        一十為水空；二十為火空；三十為木空；四十為金空；五十為土空。
        """
        ling = age % 10
        wx = hetu_wuxing(ling)
        is_kong = (ling == 0)

        kong_map = {10: "水空", 20: "火空", 30: "木空", 40: "金空", 50: "土空"}
        kong_desc = ""
        if is_kong:
            base = (age // 10) * 10
            kong_desc = kong_map.get(base % 60, f"{wx}空")

        return {
            "歲": age,
            "零數": ling,
            "五行": wx,
            "空": is_kong,
            "空描述": kong_desc,
        }

    # --------------------------------------------------------
    # 25. 八宮各宮吉凶論斷
    # --------------------------------------------------------
    def bagong_jixiong(self) -> list:
        """
        八宮各宮吉凶論斷——綜合五宮三位、夾星等。
        對應《涤器遗诀》伦宮至基宮各章吉凶論斷。
        """
        results = []
        ji_wx = self.ba_gong_wuxing[1]  # 己宮五行

        for i in range(8):
            gong = BAGONG_NAMES[i]
            gong_wx = self.ba_gong_wuxing[i]
            gong_num = self.ba_gong_raw[i]

            # 夾星（循環取相鄰宮）
            jia_left = self.ba_gong_wuxing[(i - 1) % 8]
            jia_right = self.ba_gong_wuxing[(i + 1) % 8]

            # 己宮與該宮的關係
            ji_rel = wuxing_relation(ji_wx, gong_wx) if i != 1 else "自身"

            # 胞胎
            pos = qipao_position(gong_wx, self.month_zhi)

            entry = {
                "宮": gong,
                "全名": BAGONG_FULLNAMES[i],
                "數": gong_num,
                "五行": gong_wx,
                "胞胎位": pos,
                "胞胎吉凶": "吉" if is_qipao_ji(pos) else "凶",
                "與己宮關係": ji_rel,
                "左夾": jia_left,
                "右夾": jia_right,
                "星": BAGONG_XING[i],
                "所屬卦": BAGONG_GUA[i],
            }

            # 特殊宮位關係
            if gong == "倫":
                entry["與胎納音"] = wuxing_relation(gong_wx, self.tai_nayin)
            elif gong == "己":
                entry["與年納音"] = wuxing_relation(gong_wx, self.year_nayin)
            elif gong == "雁":
                entry["與月納音"] = wuxing_relation(gong_wx, self.month_nayin)
            elif gong == "翡":
                entry["與日納音"] = wuxing_relation(gong_wx, self.day_nayin)
            elif gong == "乳":
                entry["與時納音"] = wuxing_relation(gong_wx, self.hour_nayin)
            elif gong in ("養", "鬼", "基"):
                entry["與己宮"] = wuxing_relation(ji_wx, gong_wx)

            results.append(entry)

        return results

    # --------------------------------------------------------
    # 26. 科數得失
    # --------------------------------------------------------
    def ke_shu(self) -> dict:
        """
        科數得失——文曲(翡)與武曲(養)之分析。
        對應《涤器遗诀》科數得失章。
        """
        ji_wx = self.ba_gong_wuxing[1]
        fei_wx = self.ba_gong_wuxing[3]  # 文曲
        yang_wx = self.ba_gong_wuxing[5]  # 武曲

        return {
            "文曲（翡宮）": fei_wx,
            "武曲（養宮）": yang_wx,
            "文曲與己宮": wuxing_relation(fei_wx, ji_wx),
            "武曲與己宮": wuxing_relation(yang_wx, ji_wx),
            "文武互觀": wuxing_relation(fei_wx, yang_wx),
        }

    # --------------------------------------------------------
    # 27. 壽限長短
    # --------------------------------------------------------
    def shou_xian(self) -> dict:
        """
        壽限長短——綜合多種因素判斷壽數。
        對應《涤器遗诀》壽限長短章。
        """
        # 數尾五行觀胞胎於月支
        sw = self.shu_wei
        sw_pos = qipao_position(sw["五行"], self.month_zhi)

        # 先定命宮五行觀胞胎於月支
        ming_pos = qipao_position(self.ming_gong_wx, self.month_zhi)

        # 本宮卦與先定命生克
        bengong_gua_wx = self.bagua_tibian_result["卦五行"]
        ming_rel = wuxing_relation(self.ming_gong_wx, bengong_gua_wx)

        return {
            "數尾五行": sw["五行"],
            "數尾胞胎（月支）": sw_pos,
            "數尾壽判": "壽" if is_qipao_ji(sw_pos) else "夭",
            "命宮五行": self.ming_gong_wx,
            "命宮胞胎（月支）": ming_pos,
            "命宮壽判": "壽" if is_qipao_ji(ming_pos) else "夭",
            "本宮卦與命宮": ming_rel,
        }

    # ============================================================
    # 主方法 calculate_chart
    # ============================================================
    def calculate_chart(self) -> dict:
        """
        主方法——返回完整排盤字典。
        對應《涤器遗诀》全書排盤流程。

        返回包含：五條、八宮、本宮四位、觀空定卦、八卦體變、
        命宮、大小運、數尾、孕數、貴格、凶格、關殺等完整信息。
        """
        return {
            # 基礎信息
            "四柱": {
                "年": self.year_gz,
                "月": self.month_gz,
                "日": self.day_gz,
                "時": self.hour_gz,
            },
            "胎月": self.tai_gz,
            "五條": {
                "胎": {"干支": self.tai_gz, "納音": self.tai_nayin},
                "年": {"干支": self.year_gz, "納音": self.year_nayin},
                "月": {"干支": self.month_gz, "納音": self.month_nayin},
                "日": {"干支": self.day_gz, "納音": self.day_nayin},
                "時": {"干支": self.hour_gz, "納音": self.hour_nayin},
            },
            "性別": self.gender,

            # 元影數
            "元數": self.yuan_shu,
            "影數": self.ying_shu,

            # 八宮
            "八宮": {
                "數列": self.ba_gong_raw,
                "五行": self.ba_gong_wuxing,
                "詳情": self.bagong_jixiong(),
            },

            # 本宮四位
            "本宮四位": self.ben_gong_siwei,
            "本宮別法": self.ben_gong_biefa,

            # 觀空定卦
            "觀空定卦": self.guankong,

            # 八卦體變
            "八卦體變": self.bagua_tibian_result,

            # 命宮
            "都數": self.du_shu,
            "命宮": {
                "宮序": self.ming_gong_idx,
                "宮名": BAGONG_NAMES[self.ming_gong_idx],
                "五行": self.ming_gong_wx,
            },

            # 起胞
            "起胞（八宮）": self.qipao_bagong,
            "起胞（本宮）": self.qipao_bengong,

            # 大小運
            "大運": self.dayun,
            "小運前十年": self.xiaoyun[:10],

            # 數尾
            "數尾": self.shu_wei,

            # 合孕數
            "合孕數": self.he_yun,

            # 盈卦
            "盈卦": self.ying_gua(),

            # 四位觀八觀
            "四位觀八觀": self.siwei_baguan(self.ben_gong_siwei),

            # 命主
            "命主": self.ming_zhu(),

            # 三奇吉門
            "三奇吉門": self.san_qi_ji_men(),

            # 貴格
            "貴格": self.gui_ge(),

            # 凶星
            "凶星": self.xiong_xing(),

            # 關殺
            "關殺": self.guan_sha(),

            # 科數
            "科數得失": self.ke_shu(),

            # 壽限
            "壽限": self.shou_xian(),
        }


# ============================================================
# 便捷入口函數
# ============================================================

def calculate_chart(birth_ganzhi: dict, gender: str = "男") -> dict:
    """
    便捷函數——直接計算完整排盤。

    參數：
        birth_ganzhi: dict，{"年": "己丑", "月": "乙亥", "日": "庚寅", "時": "丁丑"}
        gender: str，「男」或「女」

    返回：完整排盤字典。
    """
    chart = DiQiYiJue(birth_ganzhi, gender)
    return chart.calculate_chart()


def flow_year(birth_ganzhi: dict, year_ganzhi: str, age: int,
              gender: str = "男") -> dict:
    """
    便捷函數——計算特定流年流籌。

    參數：
        birth_ganzhi: 出生四柱
        year_ganzhi: 流年干支
        age: 行年歲數
        gender: 性別
    """
    chart = DiQiYiJue(birth_ganzhi, gender)
    return chart.flow_year(year_ganzhi=year_ganzhi, age=age)




# ============================================================
# KinAstro integration wrappers
# ============================================================

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from sxtwl import fromSolar


_GENDER_MAP = {
    "male": "男",
    "female": "女",
    "男": "男",
    "女": "女",
}


def _normalize_gender(gender: str) -> str:
    """Normalize gender labels for Di Qi Yi Jue computations."""
    return _GENDER_MAP.get((gender or "男").strip().lower(), _GENDER_MAP.get(gender, "男"))


_WUSHU_DUN = {
    "甲": "甲", "己": "甲",
    "乙": "丙", "庚": "丙",
    "丙": "戊", "辛": "戊",
    "丁": "庚", "壬": "庚",
    "戊": "壬", "癸": "壬",
}


def _hour_to_branch_idx(hour: int) -> int:
    """Convert 24-hour time to the Earthly Branch hour index."""
    if hour == 23:
        return 0
    return (hour + 1) // 2 % 12


def _compute_four_pillars_for_diqiyijue(
    year: int,
    month: int,
    day: int,
    hour: int,
) -> tuple[tuple[str, str], tuple[str, str], tuple[str, str], tuple[str, str]]:
    """Compute Four Pillars using sxtwl without importing Streamlit-heavy modules."""
    calc_year, calc_month, calc_day, calc_hour = year, month, day, hour
    if hour == 23:
        from datetime import date as _date, timedelta as _timedelta

        dt = _date(year, month, day) + _timedelta(days=1)
        calc_year, calc_month, calc_day = dt.year, dt.month, dt.day
        calc_hour = 0

    cdate = fromSolar(calc_year, calc_month, calc_day)

    ygz_raw = cdate.getYearGZ(False)
    y_stem = TIANGAN[ygz_raw.tg]
    y_branch = DIZHI[ygz_raw.dz]

    mgz_raw = cdate.getMonthGZ()
    m_stem = TIANGAN[mgz_raw.tg]
    m_branch = DIZHI[mgz_raw.dz]

    dgz_raw = cdate.getDayGZ()
    d_stem = TIANGAN[dgz_raw.tg]
    d_branch = DIZHI[dgz_raw.dz]

    h_branch = DIZHI[_hour_to_branch_idx(calc_hour)]
    h_stem_base = _WUSHU_DUN[d_stem]
    h_stem_idx = (tiangan_index(h_stem_base) + dizhi_index(h_branch)) % 10
    h_stem = TIANGAN[h_stem_idx]

    return (y_stem, y_branch), (m_stem, m_branch), (d_stem, d_branch), (h_stem, h_branch)


def _compute_birth_ganzhi(year: int, month: int, day: int, hour: int, minute: int) -> dict[str, str]:
    """Convert Gregorian birth data to Four Pillars ganzhi strings.

    Minute is accepted for API symmetry with the public chart function, but the
    classical Four Pillars conversion only changes at the hour boundary.
    """
    _ = minute
    year_pillar, month_pillar, day_pillar, hour_pillar = _compute_four_pillars_for_diqiyijue(
        year, month, day, hour
    )
    return {
        "年": "".join(year_pillar),
        "月": "".join(month_pillar),
        "日": "".join(day_pillar),
        "時": "".join(hour_pillar),
    }


@dataclass(frozen=True)
class DiqiyijueChart:
    """Structured Di Qi Yi Jue chart data returned by the public compute API."""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str = ""
    gender: str = "男"
    four_pillars: Dict[str, str] = field(default_factory=dict)
    tai_month: str = ""
    five_lines: Dict[str, Dict[str, str]] = field(default_factory=dict)
    yuan_numbers: List[int] = field(default_factory=list)
    ying_numbers: List[int] = field(default_factory=list)
    eight_palaces_numbers: List[int] = field(default_factory=list)
    eight_palaces_wuxing: List[str] = field(default_factory=list)
    eight_palaces_details: List[Dict[str, Any]] = field(default_factory=list)
    core_four_positions: List[int] = field(default_factory=list)
    alternate_four_positions: List[int] = field(default_factory=list)
    guankong: Dict[str, Any] = field(default_factory=dict)
    bagua_tibian: Dict[str, Any] = field(default_factory=dict)
    destiny_palace: Dict[str, Any] = field(default_factory=dict)
    qipao_bagong: List[Dict[str, Any]] = field(default_factory=list)
    qipao_bengong: List[Dict[str, Any]] = field(default_factory=list)
    shu_wei: Dict[str, Any] = field(default_factory=dict)
    he_yun: Dict[str, Any] = field(default_factory=dict)
    ying_gua: Dict[str, Any] = field(default_factory=dict)
    ming_zhu: Dict[str, Any] = field(default_factory=dict)
    san_qi_ji_men: Dict[str, Any] = field(default_factory=dict)
    gui_ge: List[str] = field(default_factory=list)
    xiong_xing: List[str] = field(default_factory=list)
    guan_sha: List[str] = field(default_factory=list)
    ke_shu: Dict[str, Any] = field(default_factory=dict)
    shou_xian: Dict[str, Any] = field(default_factory=dict)
    dayun: List[Dict[str, Any]] = field(default_factory=list)
    xiaoyun_preview: List[Dict[str, Any]] = field(default_factory=list)
    full_chart: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable dictionary view of the chart."""
        return asdict(self)


class DiqiyijueEngine(DiQiYiJue):
    """Backward-compatible engine alias for the legacy DiQiYiJue implementation."""



def compute_diqiyijue_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    gender: str = "male",
) -> DiqiyijueChart:
    """Compute a Di Qi Yi Jue chart from Gregorian birth data."""
    birth_ganzhi = _compute_birth_ganzhi(year, month, day, hour, minute)
    gender_zh = _normalize_gender(gender)
    engine = DiQiYiJue(birth_ganzhi=birth_ganzhi, gender=gender_zh)
    full_chart = engine.calculate_chart()

    return DiqiyijueChart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        gender=gender_zh,
        four_pillars=dict(birth_ganzhi),
        tai_month=engine.tai_gz,
        five_lines={
            key: {"干支": gz, "納音": ny}
            for key, gz, ny in (
                ("胎", engine.tai_gz, engine.tai_nayin),
                ("年", engine.year_gz, engine.year_nayin),
                ("月", engine.month_gz, engine.month_nayin),
                ("日", engine.day_gz, engine.day_nayin),
                ("時", engine.hour_gz, engine.hour_nayin),
            )
        },
        yuan_numbers=list(engine.yuan_shu),
        ying_numbers=list(engine.ying_shu),
        eight_palaces_numbers=list(engine.ba_gong_raw),
        eight_palaces_wuxing=list(engine.ba_gong_wuxing),
        eight_palaces_details=list(full_chart["八宮"]["詳情"]),
        core_four_positions=list(engine.ben_gong_siwei),
        alternate_four_positions=list(engine.ben_gong_biefa),
        guankong=dict(engine.guankong),
        bagua_tibian=dict(engine.bagua_tibian_result),
        destiny_palace=dict(full_chart["命宮"]),
        qipao_bagong=list(engine.qipao_bagong),
        qipao_bengong=list(engine.qipao_bengong),
        shu_wei=dict(engine.shu_wei),
        he_yun=dict(engine.he_yun),
        ying_gua=dict(engine.ying_gua()),
        ming_zhu=dict(engine.ming_zhu()),
        san_qi_ji_men=dict(engine.san_qi_ji_men()),
        gui_ge=list(engine.gui_ge()),
        xiong_xing=list(engine.xiong_xing()),
        guan_sha=list(engine.guan_sha()),
        ke_shu=dict(engine.ke_shu()),
        shou_xian=dict(engine.shou_xian()),
        dayun=list(engine.dayun),
        xiaoyun_preview=list(engine.xiaoyun[:12]),
        full_chart=full_chart,
    )


__all__ = [
    "BAGONG_FULLNAMES",
    "BAGONG_NAMES",
    "BAGONG_XING",
    "DiQiYiJue",
    "DiqiyijueChart",
    "DiqiyijueEngine",
    "calculate_chart",
    "compute_diqiyijue_chart",
    "flow_year",
    "guankong_dinggua",
    "bagua_tibian",
]
