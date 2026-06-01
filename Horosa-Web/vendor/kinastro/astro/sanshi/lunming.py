# -*- coding: utf-8 -*-
"""
astro/sanshi/lunming.py — 大六壬論命分析模組

依據《六壬論命秘要》原文，實作身命、女命、五節總決、十二宮、
二十四格、十六局、流年月令、壽夭等完整論命邏輯。

用法::

    from astro.sanshi.lunming import LunMingAnalyzer
    analyzer = LunMingAnalyzer(chart, benming_zhi="子")
    report = analyzer.analyze_all()
"""

from __future__ import annotations

from typing import Any

# ============================================================
# 常量表
# ============================================================

DIZHI: tuple[str, ...] = tuple("子丑寅卯辰巳午未申酉戌亥")
TIANGAN: tuple[str, ...] = tuple("甲乙丙丁戊己庚辛壬癸")

# 地支五行
ZHI_WUXING: dict[str, str] = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

# 天干五行
GAN_WUXING: dict[str, str] = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

# 干支統一五行
GANZHI_WUXING: dict[str, str] = {**GAN_WUXING, **ZHI_WUXING}

# 五行生剋表：(主, 客) -> 關係
WUXING_SHENGKE: dict[tuple[str, str], str] = {
    ("木", "火"): "生", ("火", "土"): "生", ("土", "金"): "生",
    ("金", "水"): "生", ("水", "木"): "生",
    ("木", "土"): "剋", ("土", "水"): "剋", ("水", "火"): "剋",
    ("火", "金"): "剋", ("金", "木"): "剋",
    ("木", "木"): "比和", ("火", "火"): "比和", ("土", "土"): "比和",
    ("金", "金"): "比和", ("水", "水"): "比和",
    ("火", "木"): "被生", ("土", "火"): "被生", ("金", "土"): "被生",
    ("水", "金"): "被生", ("木", "水"): "被生",
    ("土", "木"): "被剋", ("水", "土"): "被剋", ("火", "水"): "被剋",
    ("金", "火"): "被剋", ("木", "金"): "被剋",
}

# 六親對應（以日干五行為主）
LIUQIN_MAP: dict[str, str] = {
    "生": "子孫", "被生": "父母", "剋": "妻財",
    "被剋": "官鬼", "比和": "兄弟",
}

# 十二長生（五行 -> 起始支）
CHANGSHENG_ORDER: list[str] = [
    "長生", "沐浴", "冠帶", "臨官", "帝旺", "衰",
    "病", "死", "墓", "絕", "胎", "養",
]

# 各五行長生起始地支索引
CHANGSHENG_START: dict[str, int] = {
    "木": 10,  # 亥
    "火": 2,   # 寅
    "金": 5,   # 巳
    "水": 8,   # 申
    "土": 8,   # 申（土寄水長生）
}

# 地支六衝
CHONG: dict[str, str] = {
    "子": "午", "午": "子", "丑": "未", "未": "丑",
    "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳",
}

# 地支六合
HE: dict[str, str] = {
    "子": "丑", "丑": "子", "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯", "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳", "午": "未", "未": "午",
}

# 地支三刑
XING: dict[str, str] = {
    "寅": "巳", "巳": "申", "申": "寅",  # 無恩之刑
    "丑": "戌", "戌": "未", "未": "丑",  # 恃勢之刑
    "子": "卯", "卯": "子",              # 無禮之刑
    "辰": "辰", "午": "午", "酉": "酉", "亥": "亥",  # 自刑
}

# 地支六害
HAI: dict[str, str] = {
    "子": "未", "未": "子", "丑": "午", "午": "丑",
    "寅": "巳", "巳": "寅", "卯": "辰", "辰": "卯",
    "申": "亥", "亥": "申", "酉": "戌", "戌": "酉",
}

# 地支破
PO: dict[str, str] = {
    "子": "酉", "酉": "子", "丑": "辰", "辰": "丑",
    "寅": "亥", "亥": "寅", "卯": "午", "午": "卯",
    "巳": "申", "申": "巳", "未": "戌", "戌": "未",
}

# 地支墓庫
MU: dict[str, str] = {
    "木": "未", "火": "戌", "金": "丑", "水": "辰", "土": "辰",
}

# 天將吉凶屬性
JIANG_JIXI: dict[str, str] = {
    "貴": "吉", "龍": "吉", "合": "吉", "后": "吉",
    "陰": "吉", "常": "吉",
    "蛇": "凶", "雀": "凶", "勾": "凶", "空": "凶",
    "虎": "凶", "玄": "凶",
}

# 天將全名
JIANG_FULLNAME: dict[str, str] = {
    "貴": "天乙貴人", "蛇": "騰蛇", "雀": "朱雀", "合": "六合",
    "勾": "勾陳", "龍": "青龍", "空": "天空", "虎": "白虎",
    "常": "太常", "玄": "玄武", "陰": "太陰", "后": "天后",
}

# 天將五行
JIANG_WUXING: dict[str, str] = {
    "貴": "土", "蛇": "火", "雀": "火", "合": "木",
    "勾": "土", "龍": "木", "空": "土", "虎": "金",
    "常": "土", "玄": "水", "陰": "金", "后": "水",
}

# 月將名
YUEJIANG_NAME: dict[str, str] = {
    "亥": "登明", "戌": "河魁", "酉": "從魁", "申": "傳送",
    "未": "小吉", "午": "勝光", "巳": "太乙", "辰": "天罡",
    "卯": "太沖", "寅": "功曹", "丑": "大吉", "子": "神後",
}

# 十二宮名稱（固定序）
TWELVE_PALACES: list[str] = [
    "命宮", "兄弟宮", "夫妻宮", "子女宮",
    "財帛宮", "疾厄宮", "遷移宮", "奴僕宮",
    "官祿宮", "田宅宮", "福德宮", "相貌宮",
]

# 旺相休囚死：季節 -> {五行: 狀態}
WANGXIANG: dict[str, dict[str, str]] = {
    "春": {"木": "旺", "火": "相", "水": "休", "金": "囚", "土": "死"},
    "夏": {"火": "旺", "土": "相", "木": "休", "水": "囚", "金": "死"},
    "秋": {"金": "旺", "水": "相", "土": "休", "火": "囚", "木": "死"},
    "冬": {"水": "旺", "木": "相", "金": "休", "土": "囚", "火": "死"},
    # 四季月（辰戌丑未月）土旺
    "四季": {"土": "旺", "金": "相", "火": "休", "木": "囚", "水": "死"},
}

# 節氣 -> 季節
JIEQI_SEASON: dict[str, str] = {
    "立春": "春", "雨水": "春", "驚蟄": "春", "春分": "春", "清明": "春", "穀雨": "春",
    "立夏": "夏", "小滿": "夏", "芒種": "夏", "夏至": "夏", "小暑": "夏", "大暑": "夏",
    "立秋": "秋", "處暑": "秋", "白露": "秋", "秋分": "秋", "寒露": "秋", "霜降": "秋",
    "立冬": "冬", "小雪": "冬", "大雪": "冬", "冬至": "冬", "小寒": "冬", "大寒": "冬",
}


# ============================================================
# 工具函數
# ============================================================

def _wx(gz: str) -> str:
    """取干或支的五行。"""
    return GANZHI_WUXING.get(gz, "")


def _shengke(a: str, b: str) -> str:
    """回傳 a 對 b 的五行關係（生/剋/比和/被生/被剋）。"""
    wa, wb = _wx(a), _wx(b)
    if not wa or not wb:
        return ""
    return WUXING_SHENGKE.get((wa, wb), "")


def _liuqin(ri_gan: str, target: str) -> str:
    """以日干為主，求 target 的六親。"""
    rel = _shengke(ri_gan, target)
    return LIUQIN_MAP.get(rel, "")


def _changsheng_state(wx: str, zhi: str) -> str:
    """求五行在某地支的十二長生狀態。"""
    start = CHANGSHENG_START.get(wx)
    if start is None:
        return ""
    idx = (DIZHI.index(zhi) - start) % 12
    return CHANGSHENG_ORDER[idx]


def _is_kongwang(day_gz: str, zhi: str) -> bool:
    """判斷地支是否為日干支的旬空。"""
    jz = [TIANGAN[x % 10] + DIZHI[x % 12] for x in range(60)]
    # 找所在旬首
    pos = -1
    for i, g in enumerate(jz):
        if g == day_gz:
            pos = i
            break
    if pos < 0:
        return False
    xun_start = (pos // 10) * 10
    xun_zhis = [DIZHI[(xun_start + j) % 12] for j in range(10)]
    # 空亡是該旬未出現的兩個地支
    kong = [z for z in DIZHI if z not in xun_zhis]
    return zhi in kong


def _is_mu(wx: str, zhi: str) -> bool:
    """判斷地支是否為該五行的墓。"""
    return MU.get(wx) == zhi


def _season_from_jieqi(jieqi: str) -> str:
    """由節氣取季節。"""
    return JIEQI_SEASON.get(jieqi, "春")


def _wangxiang_state(wx: str, season: str) -> str:
    """取五行在指定季節的旺相休囚死狀態。"""
    mapping = WANGXIANG.get(season, {})
    return mapping.get(wx, "")


def _is_wangxiang(state: str) -> bool:
    """旺或相為有氣。"""
    return state in ("旺", "相")


def _is_xiuqiu(state: str) -> bool:
    """休囚死為無氣。"""
    return state in ("休", "囚", "死")


def _jiang_jixi(jiang: str) -> str:
    """天將吉凶（取首字匹配）。"""
    if not jiang:
        return ""
    return JIANG_JIXI.get(jiang[0], "")


def _has_relation(zhi_a: str, zhi_b: str, rel_dict: dict[str, str]) -> bool:
    """判斷兩支是否有某種關係（衝/合/刑/害/破）。"""
    return rel_dict.get(zhi_a) == zhi_b


# ============================================================
# 核心分析類
# ============================================================

class LunMingAnalyzer:
    """大六壬論命分析器。

    依據《六壬論命秘要》實作身命、女命、五節總決、十二宮、
    二十四格、十六局、流年月令、壽夭等完整論命邏輯。

    Parameters
    ----------
    chart : dict
        ``Liuren.result(0)`` 的回傳值。
    benming_zhi : str
        本命地支（如 ``'子'``）。
    """

    def __init__(self, chart: dict, benming_zhi: str) -> None:
        self.chart = chart
        self.benming = benming_zhi

        # 解析基礎資訊
        riqi: str = chart.get("日期", "")
        self.ri_gan: str = riqi[0] if len(riqi) >= 1 else ""
        self.ri_zhi: str = riqi[1] if len(riqi) >= 2 else ""
        self.day_gz: str = riqi[:2] if len(riqi) >= 2 else ""

        # 節氣 & 季節
        self.jieqi: str = chart.get("節氣", "")
        self.season: str = _season_from_jieqi(self.jieqi)

        # 三傳
        self.san_chuan: dict[str, list] = chart.get("三傳", {})
        # 四課
        self.si_ke: dict[str, list] = chart.get("四課", {})
        # 天地盤
        self.tiandi_pan: dict[str, list] = chart.get("天地盤", {})
        # 地轉天將（地支 -> 天將首字）
        self.di_to_jiang: dict[str, str] = chart.get("地轉天將", {})
        # 地轉天盤（地支 -> 天盤地支）
        self.di_to_tian: dict[str, str] = chart.get("地轉天盤", {})
        # 格局
        self.geju: list[str] = chart.get("格局", [])

        # 日干五行
        self.ri_wx: str = _wx(self.ri_gan)
        # 本命五行
        self.benming_wx: str = _wx(self.benming)
        # 本命上神（天盤上對應地支）
        self.benming_shang: str = self.di_to_tian.get(self.benming, "")
        # 日上神
        ri_gong = self._ri_gong()
        self.ri_shang: str = self.di_to_tian.get(ri_gong, "")
        # 辰上神（日支上神）
        self.chen_shang: str = self.di_to_tian.get(self.ri_zhi, "")

        # 日上天將
        self.ri_jiang: str = self.di_to_jiang.get(ri_gong, "")
        # 辰上天將
        self.chen_jiang: str = self.di_to_jiang.get(self.ri_zhi, "")
        # 本命天將
        self.benming_jiang: str = self.di_to_jiang.get(self.benming, "")

        # 三傳地支列表
        self._chuan_zhis: list[str] = []
        self._chuan_jiangs: list[str] = []
        self._chuan_liuqin: list[str] = []
        self._chuan_kong: list[bool] = []
        for k in ("初傳", "中傳", "末傳"):
            vals = self.san_chuan.get(k, [])
            self._chuan_zhis.append(vals[0] if len(vals) > 0 else "")
            self._chuan_jiangs.append(vals[1] if len(vals) > 1 else "")
            self._chuan_liuqin.append(vals[2] if len(vals) > 2 else "")
            kong_val = vals[3] if len(vals) > 3 else ""
            self._chuan_kong.append(kong_val == "空")

    # ----------------------------------------------------------
    # 內部輔助
    # ----------------------------------------------------------

    def _ri_gong(self) -> str:
        """日干寄宮（干 -> 地支）。"""
        mapping = {
            "甲": "寅", "乙": "辰", "丙": "巳", "丁": "未",
            "戊": "巳", "己": "未", "庚": "申", "辛": "戌",
            "壬": "亥", "癸": "丑",
        }
        return mapping.get(self.ri_gan, "")

    def _wangxiang(self, gz: str) -> str:
        """取干/支在當前季節的旺相休囚死。"""
        wx = _wx(gz)
        return _wangxiang_state(wx, self.season)

    def _changsheng(self, gz: str) -> str:
        """取干/支的十二長生狀態（以本命支為宮位）。"""
        wx = _wx(gz)
        return _changsheng_state(wx, self.benming)

    def _is_kong(self, zhi: str) -> bool:
        """判斷地支是否旬空。"""
        return _is_kongwang(self.day_gz, zhi)

    def _is_mu_ku(self, zhi: str) -> bool:
        """判斷地支是否入墓（以日干五行算）。"""
        return _is_mu(self.ri_wx, zhi)

    def _check_xiong_jiang(self, jiang: str) -> bool:
        """判斷天將是否為凶將（蛇虎雀勾空玄）。"""
        return _jiang_jixi(jiang) == "凶"

    def _check_ji_jiang(self, jiang: str) -> bool:
        """判斷天將是否為吉將（貴龍合后陰常）。"""
        return _jiang_jixi(jiang) == "吉"

    def _chuan_zhi(self, idx: int) -> str:
        """取三傳地支（0=初, 1=中, 2=末）。"""
        return self._chuan_zhis[idx] if idx < len(self._chuan_zhis) else ""

    def _chuan_jiang(self, idx: int) -> str:
        """取三傳天將。"""
        return self._chuan_jiangs[idx] if idx < len(self._chuan_jiangs) else ""

    def _chuan_lq(self, idx: int) -> str:
        """取三傳六親。"""
        return self._chuan_liuqin[idx] if idx < len(self._chuan_liuqin) else ""

    def _has_chong(self, zhi_a: str, zhi_b: str) -> bool:
        return _has_relation(zhi_a, zhi_b, CHONG)

    def _has_he(self, zhi_a: str, zhi_b: str) -> bool:
        return _has_relation(zhi_a, zhi_b, HE)

    def _has_xing(self, zhi_a: str, zhi_b: str) -> bool:
        return _has_relation(zhi_a, zhi_b, XING)

    def _has_hai(self, zhi_a: str, zhi_b: str) -> bool:
        return _has_relation(zhi_a, zhi_b, HAI)

    def _has_po(self, zhi_a: str, zhi_b: str) -> bool:
        return _has_relation(zhi_a, zhi_b, PO)

    def _sanchuan_has_ji(self) -> bool:
        """三傳中是否有吉將。"""
        return any(self._check_ji_jiang(j) for j in self._chuan_jiangs)

    def _sanchuan_has_xiong(self) -> bool:
        """三傳中是否有凶將。"""
        return any(self._check_xiong_jiang(j) for j in self._chuan_jiangs)

    def _count_chuan_shengke(self, target: str) -> dict[str, int]:
        """統計三傳地支對 target 的生剋數量。"""
        counts: dict[str, int] = {"生": 0, "剋": 0, "被生": 0, "被剋": 0, "比和": 0}
        for z in self._chuan_zhis:
            rel = _shengke(z, target)
            if rel in counts:
                counts[rel] += 1
        return counts

    # ── 十二宮排列 ──
    def _twelve_palace_zhis(self) -> list[str]:
        """以本命支為命宮，逆時針排十二宮地支。"""
        start = DIZHI.index(self.benming)
        return [DIZHI[(start + i) % 12] for i in range(12)]

    # ==========================================================
    # 1. 身命總則（原文第 1 節）
    # ==========================================================

    def analyze_shenming(self) -> dict[str, Any]:
        """凡論人富貴貧賤壽夭，只看身命。

        包含日上神、辰上神、三傳早中晚限分析。
        """
        results: dict[str, Any] = {}

        # --- 日上神分析（身） ---
        ri_state = self._wangxiang(self.ri_shang)
        ri_jiang_ji = self._check_ji_jiang(self.ri_jiang)
        ri_kong = self._is_kong(self.ri_shang)
        ri_mu = self._is_mu_ku(self.ri_shang)

        body_comments: list[str] = []

        # 身命旺相遇吉神良將生扶合助 → 富貴福壽
        if _is_wangxiang(ri_state) and ri_jiang_ji:
            body_comments.append("身命旺相遇吉神良將，主富貴福壽")
        # 休囚無氣更遇凶神惡將剋制 → 非夭即貧
        elif _is_xiuqiu(ri_state) and self._check_xiong_jiang(self.ri_jiang):
            body_comments.append("身命休囚無氣，更遇凶神惡將剋制，主非夭即貧")
        elif _is_wangxiang(ri_state) and self._check_xiong_jiang(self.ri_jiang):
            body_comments.append("日上有氣卻臨凶煞，乃修偉榮顯而帶殘疾之人；若凶煞有制反主假煞為權")
        elif _is_xiuqiu(ri_state) and ri_jiang_ji:
            body_comments.append("身命無氣雖遇吉神，亦足小可規模，主虛花不實之象")

        # 空亡
        if ri_kong:
            body_comments.append("大忌身命空亡：一身作事無成，多謀少遂，難立家計")
        # 入墓
        if ri_mu:
            body_comments.append("身命入墓：一世昏晦不明，行藏動靜必不亨快")

        # 身命瘦弱無助
        ri_sheng_counts = self._count_chuan_shengke(self.ri_gan)
        if _is_xiuqiu(ri_state) and ri_sheng_counts["被生"] == 0 and ri_sheng_counts["比和"] == 0:
            # 無氣無助
            if self._sanchuan_has_xiong():
                body_comments.append("無氣無助更遇刑衝剋害，官府欺凌、小人謗毀")
            else:
                body_comments.append("無氣遇扶必因人並立")
        elif _is_wangxiang(ri_state) and ri_sheng_counts["被生"] == 0 and ri_sheng_counts["比和"] == 0:
            if self._sanchuan_has_ji():
                body_comments.append("有氣無助但遇生扶合助，貴人提攜")
            else:
                body_comments.append("有氣無助必獨立撐持")

        results["身（日上）"] = {
            "日上神": self.ri_shang,
            "天將": JIANG_FULLNAME.get(self.ri_jiang, self.ri_jiang),
            "旺衰": ri_state,
            "空亡": ri_kong,
            "入墓": ri_mu,
            "論斷": body_comments,
        }

        # --- 辰上神分析（妻子） ---
        chen_state = self._wangxiang(self.chen_shang)
        chen_ji = self._check_ji_jiang(self.chen_jiang)
        chen_comments: list[str] = []

        rel_day_chen = _shengke(self.ri_gan, self.chen_shang)
        if rel_day_chen in ("生", "比和") or self._has_he(self.ri_zhi, self.chen_shang):
            chen_comments.append("日辰相生相合，夫妻和翕偕老百年")
        elif rel_day_chen in ("剋", "被剋") or self._has_chong(self.ri_zhi, self.chen_shang):
            chen_comments.append("日辰相剋相衝，夫妻反目朝夕不睦")

        if chen_ji:
            chen_comments.append("辰上吉神臨之主好妻")
        elif self._check_xiong_jiang(self.chen_jiang):
            chen_comments.append("辰上凶神惡煞臨之，其妻必惡")

        if self._is_kong(self.chen_shang):
            chen_comments.append("辰上值空，主妻刑傷")

        results["宅（辰上）"] = {
            "辰上神": self.chen_shang,
            "天將": JIANG_FULLNAME.get(self.chen_jiang, self.chen_jiang),
            "旺衰": chen_state,
            "論斷": chen_comments,
        }

        # --- 三傳限運分析（初=早年, 中=中年, 末=晚年） ---
        limit_names = ["初限（早年）", "中限（中年）", "末限（晚年）"]
        limit_comments_all: list[dict[str, Any]] = []

        for i, lname in enumerate(limit_names):
            cz = self._chuan_zhi(i)
            cj = self._chuan_jiang(i)
            clq = self._chuan_lq(i)
            c_state = self._wangxiang(cz)
            c_kong = self._is_kong(cz)
            c_ji = self._check_ji_jiang(cj)
            c_comments: list[str] = []

            if i == 0:  # 初傳
                if clq == "財" and _is_wangxiang(c_state) and cj in ("龍",):
                    c_comments.append("財旺乘龍臨吉地，早年身必富貴")
                elif clq == "子" and _is_wangxiang(c_state):
                    c_comments.append("子旺興隆，初年子定軒昂")
                if cj in ("合", "常") and clq == "財":
                    c_comments.append("六合太常臨財，作經商買賣興家")
                if cj in ("陰", "后") and clq == "財":
                    c_comments.append("太陰天后見妻財，婚姻早娶")
                if cj == "虎" and clq == "官":
                    c_comments.append("白虎乘鬼發用，初歲多災")
                if c_ji and _is_wangxiang(c_state):
                    c_comments.append("初得吉神臨於生旺，初景清高富貴")
                elif self._check_xiong_jiang(cj):
                    c_comments.append("初年遇凶煞惡將，積害多災疾")
            elif i == 1:  # 中傳
                if clq == "財" and _is_wangxiang(c_state):
                    c_comments.append("中傳財馬，中年立業興家")
                if clq == "子" and cj == "龍":
                    c_comments.append("子乘青龍並立，金玉滿堂餘慶")
                if cj in ("雀", "蛇") and _is_wangxiang(c_state) and clq == "官":
                    c_comments.append("雀蛇乘旺臨鬼，中年多遭非禍")
                if cj in ("勾", "空") and c_kong:
                    c_comments.append("勾空帶空亡，詞訟有傷")
            else:  # 末傳
                if c_ji:
                    c_comments.append("末見吉神，一路春風")
                elif self._check_xiong_jiang(cj) and not self._sanchuan_has_ji():
                    c_comments.append("末遇凶煞無制，老來孤困極窮")

            if not c_comments:
                if c_ji and _is_wangxiang(c_state):
                    c_comments.append("此限吉神旺相，順利發達")
                elif self._check_xiong_jiang(cj) and _is_xiuqiu(c_state):
                    c_comments.append("此限凶將休囚，恐有災厄")
                else:
                    c_comments.append("此限平常")

            limit_comments_all.append({
                "傳名": lname,
                "地支": cz,
                "天將": JIANG_FULLNAME.get(cj, cj),
                "六親": clq,
                "旺衰": c_state,
                "空亡": c_kong,
                "論斷": c_comments,
            })

        # 初末對比
        cross_comments: list[str] = []
        cj0 = self._chuan_jiang(0)
        cj2 = self._chuan_jiang(2)
        if self._check_ji_jiang(cj0) and self._check_xiong_jiang(cj2):
            cross_comments.append("初傳德合末傳剋害，即幼年發福末年貧寒")
        elif self._check_xiong_jiang(cj0) and self._check_ji_jiang(cj2):
            cross_comments.append("初傳刑傷末傳生比，即幼年貧困老境亨通")

        results["三傳限運"] = limit_comments_all
        if cross_comments:
            results["初末對比"] = cross_comments

        # 課命旺不如爻象旺
        results["課爻總論"] = (
            "課命旺不如爻象旺，得課象旺可許根基壯實；"
            "更得爻乘吉臨得力之地扶助身命，乃為十全造化"
        )

        return results

    # ==========================================================
    # 2. 女命專論（原文第 2 節）
    # ==========================================================

    def analyze_female(self) -> dict[str, Any]:
        """推婦人之命與男命不同，惟取柔順情正為吉。"""
        results: dict[str, Any] = {}
        comments: list[str] = []

        # 支上神分析
        zhi_shang = self.chen_shang
        zhi_jiang = self.chen_jiang

        if self._check_ji_jiang(zhi_jiang):
            comments.append("支上神吉，其女良")
        elif self._check_xiong_jiang(zhi_jiang):
            comments.append("支上神惡，其女悍")

        # 坐宮分析
        benming_rel = _shengke(self.benming, self.ri_zhi)
        if benming_rel == "被剋":
            comments.append("女命喜坐剋宮，主慎重而有禮")
        elif benming_rel == "生":
            comments.append("坐小宮恐太過而嬌恣")

        # 衝宮
        if self._has_chong(self.benming, self.ri_zhi):
            comments.append("最不宜衝宮動搖，更有陰合乘之恐別宮無制")
        # 害宮
        if self._has_hai(self.benming, self.ri_zhi):
            comments.append("坐害宮主不睦而嫉妒")
        # 刑宮
        if self._has_xing(self.benming, self.ri_zhi):
            comments.append("坐刑害多刑傷暴戾")

        # 德祿宮
        benming_state = self._wangxiang(self.benming)
        if _is_wangxiang(benming_state) and self._check_ji_jiang(self.benming_jiang):
            comments.append("坐德祿宮作命婦推之，歷重有福")

        # 空亡
        if self._is_kong(self.benming):
            comments.append("入空鄉無救作寡婦斷之，孀居無依")

        # 丁馬
        ri_ma = self.chart.get("日馬", "")
        if self.benming == ri_ma:
            if self._check_ji_jiang(self.benming_jiang):
                comments.append("坐丁馬乘貴常等吉將，他宮遙制，又當以貴論")
            elif self._check_xiong_jiang(self.benming_jiang):
                comments.append("坐丁馬帶凶將，恐棄禮義而忻私奔")

        if not comments:
            comments.append("女命平穩，無特殊格局")

        results["女命論斷"] = comments
        results["支上神"] = zhi_shang
        results["支上天將"] = JIANG_FULLNAME.get(zhi_jiang, zhi_jiang)

        return results

    # ==========================================================
    # 3. 五節總決（原文第 5-10 節）
    # ==========================================================

    def analyze_five_sections(self) -> dict[str, Any]:
        """推身命總決五節。"""
        results: dict[str, Any] = {}

        # ── 第一節：日上為主 ──
        sec1: list[str] = []
        ri_state = self._wangxiang(self.ri_shang)
        ri_ji = self._check_ji_jiang(self.ri_jiang)

        if ri_ji and _is_wangxiang(ri_state):
            sec1.append("日上見貴人青龍等吉神生旺，身命有氣，為可貴可富之人")
        elif _is_xiuqiu(ri_state) and ri_ji:
            sec1.append("日上見墓絕身命無氣，雖遇龍常吉神亦足小可規模，主虛花不實之象")
        elif _is_xiuqiu(ri_state) and self._check_xiong_jiang(self.ri_jiang):
            sec1.append("日干無氣又臨凶煞，乃下等疾困之輩")
        elif _is_wangxiang(ri_state) and self._check_xiong_jiang(self.ri_jiang):
            sec1.append("日上有氣卻臨凶煞，乃修偉榮顯而帶殘疾之人")
        else:
            sec1.append("日上平常，無特別吉凶")

        results["第一節（日上為主）"] = sec1

        # ── 第二節：辰上神（妻室子孫） ──
        sec2: list[str] = []
        rel_day_chen = _shengke(self.ri_gan, self.chen_shang)

        if rel_day_chen in ("生", "比和") or self._has_he(self.ri_zhi, self.chen_shang):
            sec2.append("福德日辰相生相合，夫妻和翕偕老百年")
        elif rel_day_chen in ("剋", "被剋") or self._has_chong(self.ri_zhi, self.chen_shang):
            sec2.append("相剋相衝，夫妻反目即朝夕不睦")

        chen_ji = self._check_ji_jiang(self.chen_jiang)
        if chen_ji:
            sec2.append("辰上吉神臨之主好妻")
        elif self._check_xiong_jiang(self.chen_jiang):
            sec2.append("凶神惡煞臨之，其妻必惡")

        # 妻財檢查
        has_wife_wealth = any(lq == "財" for lq in self._chuan_liuqin)
        if not has_wife_wealth:
            sec2.append("課無妻財，主無妻室")

        # 子孫檢查
        has_child = any(lq == "子" for lq in self._chuan_liuqin)
        if has_child:
            sec2.append("課中有子，必有子孫")
            # 子孫空亡
            for i, lq in enumerate(self._chuan_liuqin):
                if lq == "子" and self._chuan_kong[i]:
                    sec2.append("子孫空亡，多養少成")
                    break
        else:
            sec2.append("無子爻，後無子息")

        if self._is_kong(self.chen_shang):
            sec2.append("辰上值空，主妻刑傷")

        results["第二節（辰上妻子）"] = sec2

        # ── 第三節：財官 ──
        sec3: list[str] = []
        ri_state_wx = self._wangxiang(self.ri_gan)

        # 官星：子孫爻制鬼 → 有官
        has_guan = any(lq == "官" for lq in self._chuan_liuqin)
        has_zi = any(lq == "子" for lq in self._chuan_liuqin)
        has_cai = any(lq == "財" for lq in self._chuan_liuqin)
        has_xiong = any(lq == "兄" for lq in self._chuan_liuqin)

        if has_guan and has_zi:
            sec3.append("子爻制鬼則有官")
        elif has_guan and not has_zi:
            sec3.append("子爻見而無制則有官災")
        if has_cai and not has_xiong:
            sec3.append("有財無兄弟剋，財運亨通")
        elif has_xiong and not has_cai:
            sec3.append("兄爻見無制則財薄")

        if _is_wangxiang(ri_state_wx):
            if has_guan and self._sanchuan_has_ji():
                sec3.append("日月有氣，官祿貴馬龍常諸吉生合日干，乃官貴之命")
            if has_cai and self._sanchuan_has_ji():
                sec3.append("子孫妻財青龍常諸吉神臨日合日，乃富貴之命")

        if not sec3:
            sec3.append("財官平常")

        results["第三節（財官）"] = sec3

        # ── 第四節：運限 ──
        sec4: list[str] = []
        if _is_wangxiang(ri_state_wx):
            if has_cai or has_guan:
                sec4.append("日上旺相遇財官，發福增產")
            if has_guan and self._sanchuan_has_xiong():
                sec4.append("遇鬼煞須防險")
            if has_xiong:
                sec4.append("遇兄弟必主破財")
        else:
            if has_guan:
                sec4.append("日衰遇官鬼則變官為鬼賊")
            if any(lq == "父" for lq in self._chuan_liuqin):
                sec4.append("遇父母則變為艱辛")
            if has_cai:
                sec4.append("遇財福稍可發")
            if has_xiong:
                sec4.append("遇兄弟則必遭禍患")

        if not sec4:
            sec4.append("運限平穩")

        results["第四節（運限）"] = sec4

        # ── 第五節：壽數 ──
        sec5: list[str] = []
        ri_cs = _changsheng_state(_wx(self.ri_gan), self.benming)

        if ri_cs in ("長生", "冠帶", "臨官", "帝旺"):
            sec5.append(f"本命長生狀態為「{ri_cs}」，壯健可望壽")
        elif ri_cs == "沐浴":
            sec5.append("沐浴好色多病，備氣不足")
        elif ri_cs in ("死", "墓", "絕"):
            sec5.append(f"本命長生狀態為「{ri_cs}」，主夭")
        elif ri_cs in ("胎", "養"):
            sec5.append(f"本命長生狀態為「{ri_cs}」，主弱")
        else:
            sec5.append(f"本命長生狀態為「{ri_cs}」，壽數中等")

        # 日上神生日主壽
        rel_ri_shang = _shengke(self.ri_shang, self.ri_gan)
        if rel_ri_shang == "生":
            sec5.append("日上神生日，主壽")
        elif rel_ri_shang == "剋":
            sec5.append("日上神剋日，須防壽損")

        # 白虎喪門
        has_tiger_ke = False
        for i, cj in enumerate(self._chuan_jiangs):
            if cj == "虎":
                cz = self._chuan_zhi(i)
                if _shengke(cz, self.ri_gan) == "剋":
                    has_tiger_ke = True
                    sec5.append("白虎乘鬼剋日，須防壽厄")
                    break

        if self._is_kong(self.benming) and has_tiger_ke:
            sec5.append("本命空亡又見白虎剋日，為黃泉鬼")

        # 四孟/四仲/四季三傳
        si_meng = {"寅", "巳", "申", "亥"}
        si_zhong = {"子", "午", "卯", "酉"}
        si_ji = {"辰", "戌", "丑", "未"}
        chuan_set = set(self._chuan_zhis)
        if chuan_set and chuan_set <= si_meng:
            sec5.append("四孟作三傳，遞生日干本命主長壽")
        elif chuan_set and chuan_set <= si_zhong:
            sec5.append("四仲作傳，不夭不壽")
        elif chuan_set and chuan_set <= si_ji:
            sec5.append("四季作三傳，命無壽也")

        if not sec5:
            sec5.append("壽數中等")

        results["第五節（壽數）"] = sec5

        return results

    # ==========================================================
    # 4. 十二宮論（動態判斷每個宮的吉凶）
    # ==========================================================

    def analyze_twelve_palaces(self) -> dict[str, Any]:
        """十二宮論命。

        以本命支為命宮起點，逆推十二宮，逐一分析吉凶。
        """
        palace_zhis = self._twelve_palace_zhis()
        results: dict[str, Any] = {}

        for i, pname in enumerate(TWELVE_PALACES):
            pz = palace_zhis[i]
            # 該宮天盤上神
            p_shang = self.di_to_tian.get(pz, "")
            # 該宮天將
            p_jiang = self.di_to_jiang.get(pz, "")
            p_state = self._wangxiang(p_shang)
            p_ji = self._check_ji_jiang(p_jiang)
            p_kong = self._is_kong(pz)
            p_comments: list[str] = []

            # 與命宮/日干關係
            rel_to_ri = _shengke(p_shang, self.ri_gan)
            rel_to_ming = _shengke(p_shang, self.benming)

            has_chong_ming = self._has_chong(pz, self.benming)
            has_xing_ming = self._has_xing(pz, self.benming)
            has_hai_ming = self._has_hai(pz, self.benming)
            has_he_ming = self._has_he(pz, self.benming)
            has_po_ming = self._has_po(pz, self.benming)

            # 通用吉凶判斷
            if p_ji and _is_wangxiang(p_state):
                p_comments.append(f"{pname}旺相吉神，主順利發達")
            elif self._check_xiong_jiang(p_jiang) and _is_xiuqiu(p_state):
                p_comments.append(f"{pname}凶神休囚，主不利")

            if has_chong_ming:
                p_comments.append(f"{pname}衝命宮，動搖不安")
            if has_xing_ming:
                p_comments.append(f"{pname}刑命宮，多刑傷")
            if has_hai_ming:
                p_comments.append(f"{pname}害命宮，主不睦")
            if has_he_ming and p_ji:
                p_comments.append(f"{pname}合命宮帶吉，主和順有益")

            if p_kong:
                p_comments.append(f"{pname}入空亡，遇吉不吉凶不凶")

            # 各宮專論
            if pname == "命宮":
                if p_ji and _is_wangxiang(p_state) and not has_chong_ming:
                    p_comments.append("命到吉位，身更入吉何求")
                elif self._check_xiong_jiang(p_jiang):
                    p_comments.append("命宮凶，根基薄弱")

            elif pname == "財帛宮":
                if self._check_xiong_jiang(p_jiang):
                    p_comments.append("財帛宮見凶煞，不是寒士即浮誇")
                elif p_ji and _is_wangxiang(p_state):
                    p_comments.append("財帛宮吉神旺相，主財帛厚產業興隆")
                    if rel_to_ri in ("生", "比和") and not has_chong_ming and not has_hai_ming:
                        p_comments.append("與日干相生合無刑衝破害，財帛厚產業興隆")

            elif pname == "兄弟宮":
                if has_xing_ming or self._check_xiong_jiang(p_jiang):
                    p_comments.append("兄弟之宮刑煞遇，若非只身是仇家")
                elif p_ji and not has_chong_ming and not has_hai_ming:
                    p_comments.append("兄弟富貴和睦")

            elif pname == "田宅宮":
                if self._check_xiong_jiang(p_jiang):
                    p_comments.append("田宅宮中見凶，漸蕭條")
                elif p_ji and _is_wangxiang(p_state):
                    p_comments.append("旺相吉神，田宅日增盛利益")

            elif pname == "子女宮":
                cs_state = _changsheng_state(_wx(p_shang), pz)
                if cs_state == "長生" and p_ji:
                    p_comments.append("男女宮中見吉神長生，多兒女")
                elif _is_xiuqiu(p_state) and self._check_xiong_jiang(p_jiang):
                    p_comments.append("反此子息無處尋")

            elif pname == "奴僕宮":
                if _shengke(pz, self.benming) == "被剋":
                    p_comments.append("奴僕宮受剋為順")
                elif _shengke(pz, self.benming) == "生":
                    p_comments.append("奴僕宮生命不遜")
                if p_jiang in ("虎", "勾"):
                    p_comments.append("遇虎勾並厭煞，將來惹禍累主人")

            elif pname == "夫妻宮":
                if not has_xing_ming and not has_chong_ming:
                    p_comments.append("無刑無劫便為佳")
                    if p_ji:
                        p_comments.append("有善逢吉為良德，益夫益子善持家")
                else:
                    p_comments.append("妻妾之宮怕刑衝")

            elif pname == "疾厄宮":
                if p_kong:
                    p_comments.append("疾厄之宮卻喜空")
                if self._is_mu_ku(pz):
                    p_comments.append("支忌丘墓莫相逢")
                if p_ji:
                    p_comments.append("遇德神為有救")
                elif self._check_xiong_jiang(p_jiang):
                    p_comments.append("遭惡將定主凶")

            elif pname == "遷移宮":
                if p_kong:
                    p_comments.append("遷移宮內逢空，空空如也")
                opp_idx = (i + 6) % 12
                opp_pz = palace_zhis[opp_idx]
                opp_jiang = self.di_to_jiang.get(opp_pz, "")
                if self._check_ji_jiang(opp_jiang):
                    p_comments.append("對宮有德祿馬，遷到處人欽敬")

            elif pname == "官祿宮":
                ri_ma = self.chart.get("日馬", "")
                if pz == ri_ma or p_shang == ri_ma:
                    p_comments.append("官祿之鄉有驛馬，動人應")
                elif not ri_ma:
                    p_comments.append("無馬官不顯")
                if p_ji and _is_wangxiang(p_state):
                    p_comments.append("官祿宮吉旺，主得美官")
                elif _is_xiuqiu(p_state):
                    p_comments.append("官祿宮休囚，主得微官或缺俸")

            elif pname == "福德宮":
                if p_ji and _is_wangxiang(p_state):
                    p_comments.append("福德之宮遇吉為榮")
                elif self._check_xiong_jiang(p_jiang):
                    p_comments.append("凶則寒")
                if p_kong:
                    p_comments.append("此處逢空遇劫煞，一生坎坷無足言")
                elif p_ji:
                    p_comments.append("有吉神良將會，便得優游子孫綿")

            elif pname == "相貌宮":
                if p_jiang in ("勾", "玄", "蛇", "虎"):
                    p_comments.append("帶勾玄蛇虎，五官有破")
                elif p_jiang in ("貴", "常", "龍", "合") and _is_wangxiang(p_state):
                    p_comments.append("貴常龍合旺相吉，相貌魁偉人敬親")

            if not p_comments:
                p_comments.append("此宮平常")

            results[pname] = {
                "宮位地支": pz,
                "天盤上神": p_shang,
                "天將": JIANG_FULLNAME.get(p_jiang, p_jiang),
                "旺衰": p_state,
                "空亡": p_kong,
                "論斷": p_comments,
            }

        return results

    # ==========================================================
    # 5. 二十四格
    # ==========================================================

    def detect_24_ge(self) -> list[str]:
        """逐一判斷二十四格，回傳符合的格局名稱及說明。"""
        matched: list[str] = []
        bm = self.benming
        bm_shang = self.benming_shang
        bm_jiang = self.benming_jiang
        bm_state = self._wangxiang(bm)

        # 1. 正跨青龍：本命加於寅，寅乃青龍
        if bm_shang == "寅" or (bm == "寅" and bm_jiang == "龍"):
            if self._check_ji_jiang(bm_jiang) and not self._sanchuan_has_xiong():
                matched.append("正跨青龍：命帶吉將，主極貴台閣之命")
            else:
                matched.append("正跨青龍（跨龍不住）：有蛇虎來衝剋壞其貴氣")

        # 2. 倒跨青龍：寅乘青龍加於本命上
        tian_on_bm = self.di_to_tian.get(bm, "")
        jiang_on_bm = self.di_to_jiang.get(bm, "")
        if tian_on_bm == "寅" and jiang_on_bm == "龍":
            if self._sanchuan_has_ji():
                matched.append("倒跨青龍：龍反來就我，喜課傳扶助，主大貴富之命")
            else:
                matched.append("倒跨青龍：來衝剋更兼空亡則不美")

        # 3. 雙騎龍背：本命辰加寅，或寅加辰
        if (bm == "辰" and bm_shang == "寅") or (bm == "寅" and bm_shang == "辰"):
            has_chong_shen_xu = self._has_chong("申", bm) or self._has_chong("戌", bm)
            if not has_chong_shen_xu and self._check_ji_jiang(bm_jiang):
                matched.append("雙騎龍背：吉神拱護，主富貴奇局")
            else:
                matched.append("雙騎龍背：怕申戌來衝")

        # 4. 二龍禦命：本命子，寅加其上，又得辰為上龍加寅
        if bm == "子" and tian_on_bm == "寅":
            tian_on_yin = self.di_to_tian.get("寅", "")
            if tian_on_yin == "辰":
                if _is_wangxiang(bm_state):
                    matched.append("二龍禦命：最怕無氣衝剋")
                else:
                    matched.append("二龍禦命反為二龍傷命：窮困至賤")

        # 5. 龍化土蛇：本命寅加於巳，更有騰蛇乘之
        if bm == "寅" and bm_shang == "巳" and bm_jiang == "蛇":
            matched.append("龍化土蛇：為賤命，反喜來衝，多生富貴之家")

        # 6. 土蛇化龍：本命巳帶蛇臨於寅上
        if bm == "巳" and bm_shang == "寅":
            if self._sanchuan_has_ji() and _is_wangxiang(bm_state):
                matched.append("土蛇化龍：前後吉神良將拱護，化之易且更顯")
            else:
                matched.append("土蛇化龍：化而不化，反主賤，多生貧賤之家")

        # 7. 乘虎登天：本命午帶白虎臨於亥上，或本命申加於亥上亦是
        if (bm == "午" and bm_shang == "亥" and bm_jiang == "虎") or \
           (bm == "申" and bm_shang == "亥" and bm_jiang == "虎"):
            if _is_wangxiang(bm_state):
                matched.append("乘虎登天：主威鎮邊夷，公侯之命")
            else:
                matched.append("乘虎登天：無氣便為無賴惡徒")

        # 8. 履虎尾格：本命未或本命臨未
        if bm == "未" or bm_shang == "未":
            if self._sanchuan_has_ji():
                matched.append("履虎尾格：逢吉辰良將扶助亦稍可")
            else:
                matched.append("履虎尾格：不見吉神良將便為術士吏卒之流")

        # 9. 立虎首格：本命酉或本命臨酉
        if bm == "酉" or bm_shang == "酉":
            if _is_wangxiang(bm_state) and self._check_ji_jiang(bm_jiang):
                matched.append("立虎首格：主人折衝萬里功名蓋世")
            else:
                matched.append("立虎首格：無氣則立虎首而抱驚懼之心")

        # 10. 雙騎虎背：本命申又乘白虎
        if bm == "申" and bm_jiang == "虎":
            if _is_wangxiang(bm_state):
                matched.append("雙騎虎背：猛烈剛傲之性，武則好殺文則輕刑，乃英豪")
            else:
                matched.append("雙騎虎背：喜有氣")

        # 11. 虎化狸格：本命申加戌，或帶白虎臨戌
        if (bm == "申" and bm_shang == "戌") or (bm_jiang == "虎" and bm_shang == "戌"):
            if _is_xiuqiu(bm_state) and self._is_kong(bm):
                matched.append("虎化狸格：無氣並空，乃為朱門餓莩")
            else:
                matched.append("虎化狸格：軍座吏役或凶惡悍徒，有半福之象")

        # 12. 狸化虎格：本命戌加於申，或帶白虎
        if bm == "戌" and (bm_shang == "申" or bm_jiang == "虎"):
            if _is_wangxiang(bm_state) and self._sanchuan_has_ji():
                matched.append("狸化虎格：化則貴，應白屋出公卿之喻")
            else:
                matched.append("狸化虎格：不能化，不化則賤")

        # 13. 司命天門：本命之神加於亥上
        if bm_shang == "亥":
            if self._check_ji_jiang(bm_jiang) and not self._is_kong(bm):
                matched.append("司命天門：帶貴常龍后，總書記人樞秘之職")
            else:
                matched.append("司命天門：凶將並空亡或衝剋，皆不得司")

        # 14. 天門不開：本命作閉口臨亥或亥作閉口
        # 簡化判斷：本命臨亥但帶凶無氣
        if bm_shang == "亥" and self._check_xiong_jiang(bm_jiang):
            matched.append("天門不開：主有大志而不得伸，乃寒儒之命")

        # 15. 明入天門：本命作太陽臨亥
        if bm_shang == "亥" and _is_wangxiang(bm_state):
            matched.append("明入天門：主富貴不怕衝合空亡")

        # 16. 暗入天門：本命上乘玄武臨於亥
        if bm_shang == "亥" and bm_jiang == "玄":
            matched.append("暗入天門：乘玄武喜夜不喜晝，逢旺氣為綠林豪傑")

        # 17. 坐守地戶：本命加於巳上
        if bm_shang == "巳":
            if self._check_ji_jiang(bm_jiang) and _is_wangxiang(bm_state):
                matched.append("坐守地戶：帶貴常勾空，主為看財虜，最喜有氣")
            elif _is_xiuqiu(bm_state):
                matched.append("坐守地戶：無氣帶凶將，主至貧薄之命")
            else:
                matched.append("坐守地戶：中人產業")

        # 18. 來拱地戶：本命辰加午
        if bm == "辰" and bm_shang == "午":
            if _is_wangxiang(bm_state) and self._check_ji_jiang(bm_jiang):
                matched.append("來拱地戶：中格之極富，以財得官")
            else:
                matched.append("來拱地戶：有衝剋帶凶則不以富貴取之")

        # 19. 朱雀束翅：本命上乘朱雀臨亥子丑
        if bm_jiang == "雀" and bm_shang in ("亥", "子", "丑"):
            matched.append("朱雀束翅：雀落水束翅，主有七步之才而不得展")

        # 20. 朱雀騰輝：本命帶朱雀臨寅卯辰巳午
        if bm_jiang == "雀" and bm_shang in ("寅", "卯", "辰", "巳", "午"):
            if _is_wangxiang(bm_state):
                matched.append("朱雀騰輝：主文章蓋世官由翰苑")
            else:
                matched.append("朱雀騰輝：無氣帶凶則為寒儒")

        # 21. 四墓交錯：本命屬土加於四土之上
        if _wx(bm) == "土" and _wx(bm_shang) == "土":
            matched.append("四墓交錯：主人豐厚有財產")

        # 22. 河魁貫甲：本命戌加於寅
        if bm == "戌" and bm_shang == "寅":
            if _is_wangxiang(bm_state):
                matched.append("河魁貫甲：宜修武業，有氣則文武全備之貴命")
            else:
                matched.append("河魁貫甲：無氣又被衝破不以此推")

        # 23. 甲貫河魁：本命寅加於戌
        if bm == "寅" and bm_shang == "戌":
            if _is_wangxiang(bm_state) and self._sanchuan_has_ji():
                matched.append("甲貫河魁：有氣得吉神將扶助即為貴命")
            else:
                matched.append("甲貫河魁：取用與河魁貫甲相近")

        # 24. 朱勾拱拜：本命午加辰，或本命乘火臨辰
        if (bm == "午" and bm_shang == "辰") or (_wx(bm) == "火" and bm_shang == "辰"):
            if _is_wangxiang(bm_state):
                matched.append("朱勾拱拜：有氣主人性剛好辯有傳貴")
            else:
                matched.append("朱勾拱拜：無氣徒抱不平之氣，逐日訟斗之人")

        return matched

    # ==========================================================
    # 6. 十六局
    # ==========================================================

    def detect_16_ju(self) -> list[str]:
        """判斷十六局，回傳符合的局名及說明。"""
        matched: list[str] = []
        czs = set(self._chuan_zhis)
        bm = self.benming
        bm_shang = self.benming_shang
        bm_state = self._wangxiang(bm)

        # 三合局判斷
        jin_ju = {"巳", "酉", "丑"}
        mu_ju = {"亥", "卯", "未"}
        shui_ju = {"申", "子", "辰"}
        huo_ju = {"寅", "午", "戌"}
        tu_ju = {"辰", "戌", "丑", "未"}

        # 1. 庚星呈瑞（三合金局從革）
        if czs & jin_ju == jin_ju:
            matched.append("庚星呈瑞（三合金局從革）")
        # 2. 祥光搖拱（三合火局炎上）
        if czs & huo_ju == huo_ju:
            matched.append("祥光搖拱（三合火局炎上）")
        # 3. 帝座淵穆（三合水局潤下）
        if czs & shui_ju == shui_ju:
            matched.append("帝座淵穆（三合水局潤下）")
        # 4. 青帝施恩（三合木局曲直）
        if czs & mu_ju == mu_ju:
            matched.append("青帝施恩（三合木局曲直）")
        # 5. 穩坐中宮（四季土局稼穡）
        tu_overlap = czs & tu_ju
        if tu_overlap and len(tu_overlap) >= 2 and all(_wx(z) == "土" for z in czs):
            matched.append("穩坐中宮（四季土局稼穡）")

        # 方位秀氣三傳
        bei = {"亥", "子", "丑"}
        nan = {"巳", "午", "未"}
        xi = {"申", "酉", "戌"}
        dong = {"寅", "卯", "辰"}

        # 6. 北斗司權
        if czs == bei:
            matched.append("北斗司權（三傳亥子丑）")
        # 7. 南極獻圖
        if czs == nan:
            matched.append("南極獻圖（三傳巳午未）")
        # 8. 西方專美
        if czs == xi:
            matched.append("西方專美（三傳申酉戌）")
        # 9. 東海探珠
        if czs == dong:
            matched.append("東海探珠（三傳寅卯辰）")

        # 10. 坎離交泰：本命亥子丑臨巳午未，或反之（反吟）
        bei_set = {"亥", "子", "丑"}
        nan_set = {"巳", "午", "未"}
        if (bm in bei_set and bm_shang in nan_set) or (bm in nan_set and bm_shang in bei_set):
            if _is_wangxiang(bm_state) and self._sanchuan_has_ji():
                matched.append("坎離交泰：有氣吉神將俱集，主發福")
            else:
                matched.append("坎離交泰：無氣帶凶，始終貧困")

        # 11. 兌震投合：本命寅卯辰加申酉戌，或反之
        dong_set = {"寅", "卯", "辰"}
        xi_set = {"申", "酉", "戌"}
        if (bm in dong_set and bm_shang in xi_set) or (bm in xi_set and bm_shang in dong_set):
            if _is_wangxiang(bm_state) and self._sanchuan_has_ji():
                matched.append("兌震投合：有氣吉將，主發福")
            else:
                matched.append("兌震投合：無氣帶凶，貧困")

        # 12. 周天守躔：本命坐本宮不動
        if bm_shang == bm:
            ri_ma = self.chart.get("日馬", "")
            if ri_ma and self._sanchuan_has_ji():
                matched.append("周天守躔：丁馬有氣入傳帶吉，主發富發貴")
            else:
                matched.append("周天守躔：本命坐本宮不動")

        # 13. 紅雲雋秀：本命寅卯辰加亥子丑，或反之（連茹）
        if (bm in dong_set and bm_shang in bei_set) or (bm in bei_set and bm_shang in dong_set):
            if self._sanchuan_has_ji():
                matched.append("紅雲雋秀：喜吉神不忌衝合")
            else:
                matched.append("紅雲雋秀：帶罪煞則秀而不秀反不貴")

        # 14. 林火揚光：本命寅卯辰加巳午未，或反之
        if (bm in dong_set and bm_shang in nan_set) or (bm in nan_set and bm_shang in dong_set):
            if self._sanchuan_has_ji():
                matched.append("林火揚光：喜吉神將")
            else:
                matched.append("林火揚光：凶將亦損其光明")

        # 15. 天合北極：本命申酉戌加亥子丑，或反之
        if (bm in xi_set and bm_shang in bei_set) or (bm in bei_set and bm_shang in xi_set):
            if _is_wangxiang(bm_state) and self._sanchuan_has_ji():
                matched.append("天合北極：旺相遇德祿馬等大好達")
            else:
                matched.append("天合北極：休囚無氣則不為合")

        # 16. 火明西嶽：本命巳午未加申酉戌，或反之
        if (bm in nan_set and bm_shang in xi_set) or (bm in xi_set and bm_shang in nan_set):
            if _is_wangxiang(bm_state) and not self._sanchuan_has_xiong():
                matched.append("火明西嶽：旺相有氣無凶將惡煞，必崢嶸")
            else:
                matched.append("火明西嶽：否則不以此論")

        # 五局加通用評語
        # 遍歷已匹配的格局，為五局加通用評語（複製列表避免迭代時修改）
        for m in matched[:]:
            if any(k in m for k in ("庚星", "祥光", "帝座", "青帝", "穩坐")):
                if _shengke(self._chuan_zhi(0), self.benming) == "生" and self._sanchuan_has_ji():
                    matched.append("以上五局喜生命生身，更有吉神將扶助，旺氣則富貴奇局")
                break

        return matched

    # ==========================================================
    # 7. 流年月令、壽夭
    # ==========================================================

    def analyze_flow_year_month(self, liunian_zhi: str | None = None) -> dict[str, Any]:
        """流年月令吉凶及壽夭分析。

        Parameters
        ----------
        liunian_zhi : str, optional
            流年地支（如 ``'寅'``）。若不提供則僅做靜態分析。
        """
        results: dict[str, Any] = {}

        # ── 占貴賤（靈轄經） ──
        gui_jian: list[str] = []
        si_zheng = {"子", "午", "丑", "未", "寅", "申"}
        si_yu = {"卯", "酉", "辰", "戌", "巳", "亥"}
        fu_gui_shen = {"功曹", "傳送", "神後", "勝光", "大吉", "小吉"}

        benming_jiang_name = YUEJIANG_NAME.get(self.benming_shang, "")
        if self.benming in si_zheng:
            gui_jian.append("子午丑未寅申生人以天罡加本命")
            if benming_jiang_name in fu_gui_shen:
                gui_jian.append(f"生月上見{benming_jiang_name}，主大富貴")
            elif benming_jiang_name in ("天罡", "河魁"):
                gui_jian.append(f"見{benming_jiang_name}，主貧窮無神")
        elif self.benming in si_yu:
            gui_jian.append("卯酉辰戌巳亥生人以天魁加本命")
            if benming_jiang_name in fu_gui_shen:
                gui_jian.append(f"生月上見{benming_jiang_name}，主大富貴")
            elif benming_jiang_name in ("天罡", "河魁"):
                gui_jian.append(f"見{benming_jiang_name}，主貧窮")

        results["占貴賤"] = gui_jian if gui_jian else ["無特殊貴賤格局"]

        # ── 流年禍福 ──
        flow_comments: list[str] = []
        if liunian_zhi:
            # 太歲加本命看持年上神
            liunian_shang = self.di_to_tian.get(liunian_zhi, "")
            ln_jiang_name = YUEJIANG_NAME.get(liunian_shang, "")
            ln_jiang = self.di_to_jiang.get(liunian_zhi, "")

            if ln_jiang_name in ("功曹", "傳送"):
                flow_comments.append(f"流年{liunian_zhi}上見{ln_jiang_name}，其利加增官祿倍獲財利")
            elif ln_jiang_name in ("天罡", "河魁"):
                flow_comments.append(f"流年{liunian_zhi}上見{ln_jiang_name}，其年災害疾病")

            # 與日干生旺比和德合
            rel_ln = _shengke(liunian_zhi, self.ri_gan)
            if rel_ln in ("生", "比和"):
                if self._check_ji_jiang(ln_jiang):
                    flow_comments.append("流年與日干生旺比和，更有吉神良將，主有進益之喜凡事吉利通達")
                else:
                    flow_comments.append("流年與日干生旺比和，但缺吉將")
            elif rel_ln in ("剋", "被剋"):
                if self._check_xiong_jiang(ln_jiang):
                    flow_comments.append("流年與日干刑衝破害，見凶神惡煞，此年不利")
                else:
                    flow_comments.append("流年與日干相剋，須謹慎")

            # 衝合
            if self._has_chong(liunian_zhi, self.benming):
                flow_comments.append("流年衝本命，此年動盪不安")
            if self._has_he(liunian_zhi, self.benming):
                flow_comments.append("流年合本命，此年和順有助")

        if not flow_comments:
            flow_comments.append("未指定流年或無特殊吉凶")
        results["流年禍福"] = flow_comments

        # ── 壽夭專論 ──
        shou: list[str] = []
        # 本命上神長生狀態
        bm_cs = _changsheng_state(_wx(self.benming), self.benming)
        if bm_cs in ("長生",):
            shou.append("本命長生，主延年上壽")
        elif bm_cs in ("冠帶", "臨官", "帝旺"):
            shou.append(f"本命{bm_cs}，壯健可望壽")
        elif bm_cs == "沐浴":
            shou.append("沐浴好色多病，備氣不足")
        elif bm_cs in ("死", "墓", "絕"):
            shou.append(f"本命{bm_cs}，俱主夭")
        elif bm_cs in ("胎", "養"):
            shou.append(f"本命{bm_cs}，亦主夭")

        # 本命上神生剋
        rel_bm_shang = _shengke(self.benming_shang, self.benming)
        if rel_bm_shang == "生":
            shou.append("本命上神生本命，主壽")
        elif rel_bm_shang == "剋":
            shou.append("本命上神剋本命，須防壽損")

        # 德合則延年
        if self._has_he(self.benming_shang, self.benming):
            shou.append("本命上神與本命合，德合則主延年")
        if self._has_chong(self.benming_shang, self.benming):
            shou.append("本命上神與本命衝，剋害刑衝反此")

        # 白虎帶鬼剋日
        for i, cj in enumerate(self._chuan_jiangs):
            if cj == "虎":
                cz = self._chuan_zhi(i)
                if _shengke(cz, self.ri_gan) == "剋":
                    if liunian_zhi and self._has_chong(liunian_zhi, self.benming):
                        shou.append("白虎有氣乘鬼剋日，行年衝本命，此年須防大厄")
                    else:
                        shou.append("白虎乘鬼剋日，須防壽厄在某運中")

        # 命上得何神便知何年命終
        bm_jiang_name = YUEJIANG_NAME.get(self.benming_shang, "")
        if bm_jiang_name:
            shou.append(f"命上得{bm_jiang_name}（{self.benming_shang}），便知壽盡之年與此支相關")

        if not shou:
            shou.append("壽數中等，無特殊凶兆")
        results["壽夭"] = shou

        return results

    # ==========================================================
    # 總入口
    # ==========================================================

    def analyze_all(self) -> dict[str, Any]:
        """一次性回傳完整結構化論命報告。"""
        return {
            "身命總則": self.analyze_shenming(),
            "女命專論": self.analyze_female(),
            "五節總決": self.analyze_five_sections(),
            "十二宮論": self.analyze_twelve_palaces(),
            "二十四格": self.detect_24_ge(),
            "十六局": self.detect_16_ju(),
            "流年壽夭": self.analyze_flow_year_month(),
        }
