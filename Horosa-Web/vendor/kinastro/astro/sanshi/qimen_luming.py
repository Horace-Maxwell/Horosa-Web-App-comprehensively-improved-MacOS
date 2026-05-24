# -*- coding: utf-8 -*-
"""
astro/sanshi/qimen_luming.py — 奇門祿命模組 (Qi Men Destiny Analysis)

依據奇門遁甲推命法，以本人出生時辰之奇門局為主，
搜尋本命年干所在宮位，分析六親（父母、兄弟、子孫、官祿、妻財、疾厄），
結合八門、八神（八將）、九星、格局等，推斷一生窮通壽夭吉凶禍福。

用法::

    from astro.sanshi.qimen_luming import compute_qimen_luming, render_qimen_luming
    result = compute_qimen_luming(year, month, day, hour, minute, method=1)
    render_qimen_luming(result)
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from astro.i18n import auto_cn

# ============================================================
# 常量表
# ============================================================

TIANGAN: tuple[str, ...] = tuple("甲乙丙丁戊己庚辛壬癸")
DIZHI: tuple[str, ...] = tuple("子丑寅卯辰巳午未申酉戌亥")

# 九宮名
GONG_ORDER: list[str] = ["巽", "離", "坤", "震", "中", "兌", "艮", "坎", "乾"]
GONG_GRID: list[list[str]] = [
    ["巽", "離", "坤"],
    ["震", "中", "兌"],
    ["艮", "坎", "乾"],
]

# 四正宮（子午卯酉對應宮位）
SI_ZHENG_GONG: set[str] = {"坎", "離", "震", "兌"}

# 凶格關鍵字（用於判斷格局吉凶）
XIONG_KEYWORDS: tuple[str, ...] = ("不利", "凶", "貧窮", "嗽咳", "昏迷", "刑傷", "憂愁")

# 天干五行
GAN_WUXING: dict[str, str] = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

# 宮位五行
GONG_WUXING: dict[str, str] = {
    "坎": "水", "坤": "土", "震": "木", "巽": "木",
    "中": "土", "乾": "金", "兌": "金", "艮": "土", "離": "火",
}

# 天干陰陽
GAN_YINYANG: dict[str, str] = {
    "甲": "陽", "乙": "陰", "丙": "陽", "丁": "陰",
    "戊": "陽", "己": "陰", "庚": "陽", "辛": "陰",
    "壬": "陽", "癸": "陰",
}

# 五行生剋
WUXING_SHENGKE: dict[tuple[str, str], str] = {
    ("木", "火"): "我生", ("火", "土"): "我生", ("土", "金"): "我生",
    ("金", "水"): "我生", ("水", "木"): "我生",
    ("木", "土"): "我剋", ("土", "水"): "我剋", ("水", "火"): "我剋",
    ("火", "金"): "我剋", ("金", "木"): "我剋",
    ("木", "木"): "比肩", ("火", "火"): "比肩", ("土", "土"): "比肩",
    ("金", "金"): "比肩", ("水", "水"): "比肩",
    ("火", "木"): "生我", ("土", "火"): "生我", ("金", "土"): "生我",
    ("水", "金"): "生我", ("木", "水"): "生我",
    ("土", "木"): "剋我", ("水", "土"): "剋我", ("火", "水"): "剋我",
    ("金", "火"): "剋我", ("木", "金"): "剋我",
}

# 六親對應
LIUQIN_MAP: dict[str, str] = {
    "生我": "父母",
    "我生": "子孫",
    "比肩": "兄弟",
    "剋我": "官祿（疾厄）",
    "我剋": "妻財（奴僕）",
}

# 八門五行
MEN_WUXING: dict[str, str] = {
    "休": "水", "生": "土", "傷": "木", "杜": "木",
    "景": "火", "死": "土", "驚": "金", "開": "金",
}

# 六親 emoji 映射
LIUQIN_EMOJI: dict[str, str] = {
    "父母": "🟢",
    "兄弟": "🔵",
    "子孫": "🟡",
    "官祿": "🟠",
    "疾厄": "🟠",
    "妻財": "🔴",
    "奴僕": "🔴",
    "比肩": "🔵",
}

# 九星五行
XING_WUXING: dict[str, str] = {
    "蓬": "水", "任": "土", "沖": "木", "輔": "木",
    "英": "火", "禽": "土", "柱": "金", "心": "金",
}

# ── 八神（八將）全名映射 ──
SHEN_FULLNAME: dict[str, str] = {
    "符": "值符（青龍）",
    "蛇": "螣蛇",
    "陰": "太陰",
    "合": "六合",
    "勾": "勾陳（白虎）",
    "雀": "朱雀（玄武）",
    "虎": "白虎",
    "玄": "玄武",
    "地": "九地",
    "天": "九天",
}

# ── 八門論命詳斷 ──
# 每門對六親的斷語
MEN_LIUQIN_DUAN: dict[str, dict[str, str]] = {
    "休": {
        "summary": "休門主休養安和",
        "父母": "父慈子孝，和氣藹人",
        "兄弟": "真心愛敬，無分彼我",
        "子孫": "少有和合，各守家園",
        "官祿": "功名妥手，職位安穩",
        "疾厄": "隱虛暗疾，延拖難愈",
        "妻妾": "幽閑貞靜，和偕得助",
        "財帛": "錢財進益，滔滔不絕",
    },
    "生": {
        "summary": "生門主發生安閑",
        "父母": "財祿旺相，安福尊榮",
        "兄弟": "和順愛敬，情誼深切",
        "子孫": "家道興隆，義高得厚",
        "官祿": "官職高升，榮華赫奕",
        "疾厄": "身軀強壯，無災無病",
        "妻妾": "和順貞潔",
        "財帛": "積聚富厚",
    },
    "傷": {
        "summary": "傷門主振動傷殘",
        "父母": "殘忍寡愛，性若浮萍",
        "兄弟": "一生不和，無情無義",
        "子孫": "後嗣美麗，振作英發",
        "官祿": "顯赫威權，亦多掣時",
        "疾厄": "手足拘攣，骨節疼痛",
        "妻妾": "才德俱全，內治有力",
        "財帛": "謀遠奔走，辛勤成家",
    },
    "杜": {
        "summary": "杜門主閉塞無為",
        "父母": "一生蹇滯，牢守家園",
        "兄弟": "彼此睽違，情同陌路",
        "子孫": "難生少育，須藉陰功",
        "官祿": "仕途閉塞，難得職位",
        "疾厄": "少病少災，風病宜防",
        "妻妾": "心性閉澀，難以調和",
        "財帛": "少年貧窘，晚來方裕",
    },
    "景": {
        "summary": "景門主張大虛華之事，事無實濟",
        "父母": "浮躁虛假，狂風疾雨",
        "兄弟": "無情少義，面上虛文",
        "子孫": "生產難有，從養螟蛉",
        "官祿": "少年早發，忽升忽降",
        "疾厄": "風火暴疾，易作易止",
        "妻妾": "聰明智慧，心性乖舛",
        "財帛": "以無為有，虛張實少",
    },
    "死": {
        "summary": "死門主死亡敗絕，凡百無成",
        "父母": "病不離床，死亡相繼",
        "兄弟": "無情少義，刑克傷亡",
        "子孫": "刑傷忤逆，雖有若無",
        "官祿": "功名不遂，南畝終身",
        "疾厄": "有病難療，終致殘生",
        "妻妾": "必有死亡，繼室方安",
        "財帛": "虛耗傷敗，聚散不常",
    },
    "驚": {
        "summary": "驚門主驚惶不安",
        "父母": "生平多怨，父子不和",
        "兄弟": "乖戾欺妒，各使神通",
        "子孫": "恃財矜夸，刻薄少情",
        "官祿": "凶險地面，散職閑員",
        "疾厄": "卒暴驚險，危篤傍惶",
        "妻妾": "詭詐口舌，夫婦不和",
        "財帛": "寡少難聚，入不償出",
    },
    "開": {
        "summary": "開門主豁達開暢",
        "父母": "性不真切，浮泛相待",
        "兄弟": "意不相聯，似親非親",
        "子孫": "聰明俊秀，科甲貴顯",
        "官祿": "功名顯達，職位高遷",
        "疾厄": "一生少病，強健安和",
        "妻妾": "正直果決，內助賢能",
        "財帛": "資材難聚，聚亦易散",
    },
}

# ── 八神（八將）論性情 ──
SHEN_PERSONALITY: dict[str, str] = {
    "符": "六甲值符屬青龍，其人仁厚溫和，若得美格更妙，做事有始有終",
    "蛇": "螣蛇之性虛花不實，無有誠信，多疑猜善呻吟，有成有敗",
    "陰": "太陰多謀多為，能剛能柔，性則廉潔",
    "合": "六合面上有情，心無專主，不生慳吝，女命逢之淫亂污穢",
    "勾": "白虎性剛激烈，逼迫無情，有殺伐之心，遭刀兵之慘，在女人則有傷損",
    "雀": "玄武性多詭詐，不是穿窬便是盜賊，暗地謀人，人難防避",
    "虎": "白虎性剛激烈，逼迫無情，有殺伐之心，遭刀兵之慘，在女人則有傷損",
    "玄": "玄武性多詭詐，不是穿窬便是盜賊，暗地謀人，人難防避",
    "地": "九地心性昏濛，稟質重厚，能陰謀善籌畫，做事能下毒手",
    "天": "九天性氣發揚，浮躁剛暴，英氣逼人，令人難當，然心無私曲，掣日月而行，不為暗昧事",
}

# ── 八神論命（加於各宮之吉凶）──
SHEN_LUMING: dict[str, str] = {
    "符": "值符為貴神，加本命非貴即富，正直端方，人皆尊敬，生平有吉無凶",
    "蛇": "螣蛇加本命，做人必古怪難交，言語欺誑，作事虛花，有名無實",
    "陰": "太陰加本命，一生善於計算，陰謀詭詐，終無良策",
    "合": "六合加本命，心性和同，恩仇一類，善惡無分，同流合污",
    "勾": "白虎加年命，做人殘刻無情，所遇傷損，一生破敗",
    "雀": "玄武加本命，不是穿窬就是劫盜，立心陰險，做事惡毒",
    "虎": "白虎加年命，做人殘刻無情，所遇傷損，一生破敗",
    "玄": "玄武加本命，不是穿窬就是劫盜，立心陰險，做事惡毒",
    "地": "九地加本命，陰晦暗滯，昏迷度日，毫無光彩之色",
    "天": "九天加本命，虛張聲勢，假裝門面，實少情義，不可依仗",
}

# ── 八神特定宮位喜忌 ──
SHEN_GONG_YIJI: dict[str, dict[str, str]] = {
    "符": {
        "_default": "吉",
        "_desc": "八將之中最喜值符貴神，命宮及父母、兄弟、子孫宮遇之，必主富貴榮華",
    },
    "蛇": {
        "_default": "凶",
        "_desc": "螣蛇白虎加之，必主有疾病",
    },
    "陰": {
        "_default": "吉",
        "_desc": "太陰吉神不拘何宮，加之皆吉",
    },
    "合": {
        "_default": "吉",
        "妻妾": "凶：六合之宮百事和諧，惟妻妾宮忌之，有此必主淫佚無恥、醜聲遠播",
        "_desc": "六合之宮百事和諧，惟妻妾宮忌之",
    },
    "虎": {
        "_default": "凶",
        "_desc": "白虎加之，必主有疾病",
    },
    "勾": {
        "_default": "凶",
        "_desc": "白虎加之，必主有疾病",
    },
    "玄": {
        "_default": "凶",
        "疾厄": "吉：玄武疾厄宮加之則終身必少病",
        "財帛": "吉：玄武財帛宮加之則喜聚金錢，必成富翁",
        "_desc": "玄武各宮俱不宜，惟疾厄宮、財帛宮逢之則吉",
    },
    "雀": {
        "_default": "凶",
        "疾厄": "吉：玄武疾厄宮加之則終身必少病",
        "財帛": "吉：玄武財帛宮加之則喜聚金錢，必成富翁",
        "_desc": "玄武各宮俱不宜，惟疾厄宮、財帛宮逢之則吉",
    },
    "地": {
        "_default": "凶",
        "財帛": "吉：九地財帛宮逢之則吉，金銀滿室，盜賊不能偷劫",
        "疾厄": "大凶：九地疾厄宮遇之尤不喜，必至死亡",
        "_desc": "九地幽暗閉藏，諸宮俱不喜，惟財帛宮逢之則吉",
    },
    "天": {
        "_default": "平",
        "官祿": "大吉：九天官祿宮逢之則主功高顯達，職位超遷",
        "本命": "大吉：九天本命宮遇之尤為喜慶",
        "_desc": "九天性烈，他宮不宜，惟官祿宮逢之主功高顯達，本命宮遇之尤喜",
    },
}

# ── 十干迫制 ──
GANZHI_POZHI: dict[str, dict[str, str]] = {
    "木": {
        "乾": "木被金克：金旺木衰則主折傷之禍",
        "兌": "木被金克：金旺木衰則主折傷之禍",
    },
    "火": {
        "坎": "火被水克：水旺火衰則主有滅亡之禍",
    },
    "土": {
        "震": "土被木克：木旺土衰則主有癰疽瘡毒之症",
        "巽": "土被木克：木旺土衰則主有癰疽瘡毒之症",
    },
    "金": {
        "離": "金被火克：火旺金衰則主有痰火嗽癆之症",
    },
    "水": {
        "坤": "水被土克：土旺水衰則主有下元虛耗之災",
        "艮": "水被土克：土旺水衰則主有下元虛耗之災",
    },
}


# ============================================================
# 輔助函數
# ============================================================

def _get_wuxing(char: str) -> str | None:
    """取得天干或宮位的五行。"""
    return GAN_WUXING.get(char) or GONG_WUXING.get(char)


def _get_shengke(my_wx: str, other_wx: str) -> str:
    """取得五行生剋關係（以 my_wx 為主）。"""
    return WUXING_SHENGKE.get((my_wx, other_wx), "")


def _get_liuqin(relation: str) -> str:
    """將生剋關係轉換為六親。"""
    return LIUQIN_MAP.get(relation, relation)


def _find_stem_palace(chart: dict, stem: str) -> str | None:
    """在天盤和地盤中找到指定天干所在的宮位。優先用天盤。"""
    sky = chart.get("天盤", {})
    earth = chart.get("地盤", {})
    # 先搜天盤
    for gong, gan in sky.items():
        if gan == stem:
            return gong
    # 再搜地盤
    for gong, gan in earth.items():
        if gan == stem:
            return gong
    return None


def _find_year_stem_substitute(year_gan: str) -> str:
    """甲用戊代，甲所遁之六儀。年干若為甲，按甲所遁取代干。"""
    # 六甲遁干：甲子遁戊、甲戌遁己、甲申遁庚、甲午遁辛、甲辰遁壬、甲寅遁癸
    # 但年干為甲時，一般以「戊」代甲入盤
    if year_gan == "甲":
        return "戊"
    return year_gan


def _get_palace_info(chart: dict, gong: str) -> dict:
    """取得某宮的天盤、地盤、門、星、神資訊。"""
    return {
        "天干": chart.get("天盤", {}).get(gong, ""),
        "地干": chart.get("地盤", {}).get(gong, ""),
        "門": chart.get("門", {}).get(gong, ""),
        "星": chart.get("星", {}).get(gong, ""),
        "神": chart.get("神", {}).get(gong, ""),
    }


def _analyze_six_relations(
    benming_gan: str,
    chart: dict,
) -> list[dict[str, Any]]:
    """分析六親：遍歷九宮，找出每個天盤奇儀與本命干的五行關係。

    Returns
    -------
    list of dict
        每項包含：宮位、天干、六親、門、門斷語、星、神、神論等。
    """
    my_wx = _get_wuxing(benming_gan)
    if not my_wx:
        return []

    sky = chart.get("天盤", {})
    men = chart.get("門", {})
    xing = chart.get("星", {})
    shen = chart.get("神", {})

    results: list[dict[str, Any]] = []
    for gong in GONG_ORDER:
        if gong == "中":
            # 中宮無門無星無神，不參與六親分析
            continue
        tian_gan = sky.get(gong)
        if not tian_gan:
            continue

        other_wx = _get_wuxing(tian_gan)
        if not other_wx:
            continue

        relation = _get_shengke(my_wx, other_wx)
        liuqin = _get_liuqin(relation)

        # 細分官祿/疾厄、妻財/奴僕
        liuqin_simple = liuqin.split("（")[0]

        # 門的斷語
        door = men.get(gong, "")
        door_duan = {}
        if door and door in MEN_LIUQIN_DUAN:
            dd = MEN_LIUQIN_DUAN[door]
            door_duan = {
                "summary": dd.get("summary", ""),
            }
            # 匹配六親
            for key in ("父母", "兄弟", "子孫", "官祿", "疾厄", "妻妾", "財帛"):
                if key in liuqin or key in liuqin_simple:
                    door_duan["斷語"] = dd.get(key, "")
                    door_duan["六親類別"] = key
                    break
            # 如果是「官祿（疾厄）」，同時取官祿和疾厄
            if "官祿" in liuqin:
                door_duan["官祿"] = dd.get("官祿", "")
                door_duan["疾厄"] = dd.get("疾厄", "")
            if "妻財" in liuqin:
                door_duan["妻妾"] = dd.get("妻妾", "")
                door_duan["財帛"] = dd.get("財帛", "")

        # 神的斷語
        god = shen.get(gong, "")
        god_personality = SHEN_PERSONALITY.get(god, "")
        god_luming = SHEN_LUMING.get(god, "")
        god_fullname = SHEN_FULLNAME.get(god, god)

        star = xing.get(gong, "")
        yinyang = GAN_YINYANG.get(tian_gan, "")

        results.append({
            "宮位": gong,
            "天干": tian_gan,
            "天干五行": other_wx,
            "天干陰陽": yinyang,
            "五行關係": relation,
            "六親": liuqin,
            "門": door,
            "門斷語": door_duan,
            "星": star,
            "神": god,
            "神全名": god_fullname,
            "神性情": god_personality,
            "神論命": god_luming,
        })

    return results


def _analyze_suppression(benming_gan: str, benming_gong: str | None) -> str:
    """分析十干迫制（年命天干落在被克宮位）。"""
    if not benming_gong:
        return ""
    wx = _get_wuxing(benming_gan)
    if not wx:
        return ""
    suppression = GANZHI_POZHI.get(wx, {})
    return suppression.get(benming_gong, "")


def _analyze_shen_special(
    shen: str,
    liuqin_category: str,
) -> str:
    """分析八神在特定宮位（六親宮）的特殊喜忌。"""
    yiji = SHEN_GONG_YIJI.get(shen, {})
    if not yiji:
        return ""
    specific = yiji.get(liuqin_category, "")
    if specific:
        return specific
    return yiji.get("_default", "")


def _analyze_patterns(chart: dict, benming_gong: str | None) -> list[str]:
    """分析格局（凶格吉格），返回分析結果列表。"""
    patterns: list[str] = []
    if not benming_gong or benming_gong == "中":
        return patterns

    sky = chart.get("天盤", {})
    earth = chart.get("地盤", {})
    men = chart.get("門", {})

    tian_gan = sky.get(benming_gong, "")
    di_gan = earth.get(benming_gong, "")
    door = men.get(benming_gong, "")

    # ── 天地二遁、人遁 ──
    if tian_gan == "乙" and di_gan == "丙":
        patterns.append("天遁（乙加丙）：吉格，可安守家園")
    if tian_gan == "丙" and di_gan == "丁":
        patterns.append("地遁（丙加丁）：吉格，可安守家園")
    if tian_gan == "丁" and di_gan == "乙":
        patterns.append("人遁（丁加乙）：吉格，可安守家園")

    # ── 甲加丙、丙加甲 ──
    if (tian_gan == "戊" and di_gan == "丙") or (tian_gan == "丙" and di_gan == "戊"):
        patterns.append("甲（戊）加丙或丙加甲（戊）：各宮皆利，惟疾厄宮主一生疾病纏綿")

    # ── 太白入熒惑（庚加丙）──
    if tian_gan == "庚" and di_gan == "丙":
        patterns.append("太白入熒惑（庚加丙）：作事受虧，一世貧窮")
    # ── 熒惑入太白（丙加庚）──
    if tian_gan == "丙" and di_gan == "庚":
        patterns.append("熒惑入太白（丙加庚）：火旺克金，嗽咳喘急")

    # ── 六癸加丁 ──
    if tian_gan == "癸" and di_gan == "丁":
        patterns.append("六癸加丁：昏迷惑亂，事事傷嗟")
    # ── 六丁加癸 ──
    if tian_gan == "丁" and di_gan == "癸":
        patterns.append("六丁加癸：憂愁恐驚，自投刑獄")

    # ── 大格（庚加癸）──
    if tian_gan == "庚" and di_gan == "癸":
        patterns.append("大格（庚加癸）：有刑傷阻格")
    # ── 小格（庚加壬）──
    if tian_gan == "庚" and di_gan == "壬":
        patterns.append("小格（庚加壬）：有刑傷阻格")
    # ── 刑格（庚加己）──
    if tian_gan == "庚" and di_gan == "己":
        patterns.append("刑格（庚加己）：有刑傷阻格")

    # ── 宮門生克 ──
    if door:
        door_wx = MEN_WUXING.get(door, "")
        gong_wx = GONG_WUXING.get(benming_gong, "")
        if door_wx and gong_wx:
            gm_rel = _get_shengke(gong_wx, door_wx)
            if gm_rel == "我生":
                patterns.append(f"宮生門（{benming_gong}宮{gong_wx}生{door}門{door_wx}）：宮門相生，吉")
            elif gm_rel == "生我":
                patterns.append(f"門生宮（{door}門{door_wx}生{benming_gong}宮{gong_wx}）：宮門相生，吉")
            elif gm_rel == "剋我":
                patterns.append(f"門克宮（{door}門{door_wx}克{benming_gong}宮{gong_wx}）：宮門相剋，不利")
            elif gm_rel == "我剋":
                patterns.append(f"宮克門（{benming_gong}宮{gong_wx}克{door}門{door_wx}）：宮門相剋，耗氣")

    # ── 四正宮判定 ──
    if benming_gong in SI_ZHENG_GONG:
        patterns.append(f"本命落四正宮（{benming_gong}）：格局較高，主貴")

    return patterns


def _overall_assessment(
    benming_gong: str | None,
    benming_shen: str,
    benming_door: str,
    suppression: str,
    patterns: list[str],
    chart: dict,
) -> str:
    """綜合評斷本命格局高低。"""
    parts: list[str] = []

    # 四正宮
    if benming_gong and benming_gong in SI_ZHENG_GONG:
        parts.append("本命落四正宮，格局較高")

    # 值符加本命
    if benming_shen == "符":
        parts.append("值符貴神臨本命，非貴即富")
    elif benming_shen == "陰":
        parts.append("太陰臨本命，一生善計")
    elif benming_shen in ("蛇",):
        parts.append("螣蛇臨本命，虛花不實")
    elif benming_shen in ("虎", "勾"):
        parts.append("白虎臨本命，殘克無情")
    elif benming_shen in ("玄", "雀"):
        parts.append("玄武臨本命，詭詐陰險")
    elif benming_shen == "地":
        parts.append("九地臨本命，陰晦暗滯")
    elif benming_shen == "天":
        parts.append("九天臨本命，英氣發揚，惟虛張聲勢")
    elif benming_shen == "合":
        parts.append("六合臨本命，和同心性")

    # 門
    if benming_door in ("開", "休", "生"):
        parts.append(f"本命逢{benming_door}門，三吉門，主吉")
    elif benming_door in ("傷", "杜"):
        parts.append(f"本命逢{benming_door}門，有振動閉塞之象")
    elif benming_door in ("景",):
        parts.append(f"本命逢{benming_door}門，虛華不實")
    elif benming_door in ("死",):
        parts.append(f"本命逢{benming_door}門，死氣沉沉")
    elif benming_door in ("驚",):
        parts.append(f"本命逢{benming_door}門，驚惶不安")

    # 迫制
    if suppression:
        parts.append(f"十干迫制：{suppression}")

    # 凶格
    xiong_patterns = [p for p in patterns if any(w in p for w in XIONG_KEYWORDS)]
    if xiong_patterns:
        parts.append("命局有凶格：" + "；".join(xiong_patterns))

    if not parts:
        parts.append("命局平穩，無特別凶吉")

    return "。".join(parts) + "。"


# ============================================================
# 主計算函數
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def compute_qimen_luming(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    method: int = 1,
    **_kwargs,
) -> dict[str, Any]:
    """計算奇門祿命。

    以出生時辰排奇門局，找出年干所在宮位為本命宮，
    分析六親、八門、八神、格局、迫制等。

    Parameters
    ----------
    year, month, day, hour, minute : int
        出生日期時間。
    method : int
        1 = 拆補法, 2 = 置閏法（默認拆補）。

    Returns
    -------
    dict
        包含排盤結果及祿命分析。
    """
    import sys
    # kinqimen 的 config 模組需要特殊處理
    if "config" not in sys.modules or not hasattr(sys.modules.get("config", None), "gangzhi"):
        try:
            import kinqimen.config  # noqa: F811
            sys.modules["config"] = kinqimen.config
        except ImportError:
            pass

    from kinqimen.kinqimen import Qimen

    q = Qimen(year, month, day, hour, minute)
    chart = q.pan(method)

    # 取得四柱干支
    from kinqimen import config as _qm_config
    gz = _qm_config.gangzhi(year, month, day, hour, minute)
    year_gz = gz[0]  # e.g. "庚午"
    month_gz = gz[1]
    day_gz = gz[2]
    hour_gz = gz[3]

    year_gan = year_gz[0]
    hour_gan = hour_gz[0]

    # 年干替代（甲遁戊）
    benming_gan = _find_year_stem_substitute(year_gan)

    # 找本命宮（年干在天盤/地盤的位置）
    benming_gong = _find_stem_palace(chart, benming_gan)

    # 本命宮資訊
    benming_info = _get_palace_info(chart, benming_gong) if benming_gong else {}

    # ── 值符值使分析 ──
    zhifu_zhishi = chart.get("值符值使", {})

    # 值符宮（本身/住宅/子孫）
    zhifu_xing_gong = zhifu_zhishi.get("值符星宮", [])
    zhifu_gong = zhifu_xing_gong[1] if len(zhifu_xing_gong) > 1 else ""
    zhifu_info = _get_palace_info(chart, zhifu_gong) if zhifu_gong else {}

    # 值使宮（立業/妻妾/官職/客旅）
    zhishi_men_gong = zhifu_zhishi.get("值使門宮", [])
    zhishi_gong = zhishi_men_gong[1] if len(zhishi_men_gong) > 1 else ""
    zhishi_info = _get_palace_info(chart, zhishi_gong) if zhishi_gong else {}

    # ── 六親分析 ──
    six_relations = _analyze_six_relations(benming_gan, chart)

    # ── 十干迫制 ──
    suppression = _analyze_suppression(benming_gan, benming_gong)

    # ── 格局分析 ──
    pattern_analysis = _analyze_patterns(chart, benming_gong)

    # ── 八神特殊喜忌 ──
    shen_special: list[dict[str, str]] = []
    for rel in six_relations:
        lq = rel["六親"]
        # 簡化六親名
        for cat in ("父母", "兄弟", "子孫", "官祿", "疾厄", "妻妾", "財帛"):
            if cat in lq:
                special = _analyze_shen_special(rel["神"], cat)
                if special:
                    shen_special.append({
                        "宮位": rel["宮位"],
                        "六親": cat,
                        "神": rel["神全名"],
                        "喜忌": special,
                    })
                break

    # ── 本命宮的神 ──
    benming_shen = benming_info.get("神", "")
    benming_door = benming_info.get("門", "")
    benming_star = benming_info.get("星", "")

    # ── 綜合評斷 ──
    overall = _overall_assessment(
        benming_gong, benming_shen, benming_door,
        suppression, pattern_analysis, chart,
    )

    return {
        "排盤": chart,
        "四柱": {
            "年柱": year_gz,
            "月柱": month_gz,
            "日柱": day_gz,
            "時柱": hour_gz,
        },
        "本命干": benming_gan,
        "本命宮": benming_gong,
        "本命宮資訊": benming_info,
        "值符宮": {
            "宮位": zhifu_gong,
            "資訊": zhifu_info,
            "意義": "天上值符宮之星儀門將為本身；值符下地盤之星儀門將為住宅、為子孫",
        },
        "值使宮": {
            "宮位": zhishi_gong,
            "資訊": zhishi_info,
            "意義": "值使之門為立業、為妻妾、為官職、為客旅；值使下地盤之星儀八門為地頭、為任所、為子女",
        },
        "六親分析": six_relations,
        "十干迫制": suppression,
        "格局分析": pattern_analysis,
        "八神喜忌": shen_special,
        "綜合評斷": overall,
    }


# ============================================================
# Streamlit 渲染
# ============================================================

def render_qimen_luming(result: dict, after_chart_hook=None):
    """在 Streamlit 中渲染奇門祿命分析結果。"""
    st.markdown(f"### 🔮 {auto_cn('奇門祿命')}")

    chart = result.get("排盤", {})
    sizhu = result.get("四柱", {})
    benming_gan = result.get("本命干", "")
    benming_gong = result.get("本命宮", "")
    benming_info = result.get("本命宮資訊", {})

    # ── 九宮盤（3×3 格局）── 移到最前面，手機版優先
    st.markdown(f"#### {auto_cn('九宮盤')}")
    
    # 手機版響應式 CSS
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .qimen-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; margin: 8px 0; }
        .qimen-cell { border: 1px solid #555; border-radius: 6px; padding: 4px; text-align: center; font-size: 9px; min-height: 50px; }
        .qimen-cell.benming { border: 2px solid #EF4444; background: rgba(239,68,68,0.08); }
        .qimen-cell.zhong { border: 2px solid #EAB308; background: rgba(234,179,8,0.1); }
        .qimen-shen { color: #EAB308; }
        .qimen-xing { color: #A78BFA; }
        .qimen-men { color: #60A5FA; }
    }
    @media (min-width: 769px) {
        .qimen-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 12px 0; }
        .qimen-cell { border: 1px solid #555; border-radius: 8px; padding: 8px; text-align: center; min-height: 100px; }
        .qimen-cell.benming { border: 3px solid #EF4444; background: rgba(239,68,68,0.08); }
        .qimen-cell.zhong { border: 2px solid #EAB308; background: rgba(234,179,8,0.1); }
        .qimen-shen { color: #EAB308; font-size: 1rem; }
        .qimen-xing { color: #A78BFA; font-size: 1rem; }
        .qimen-men { color: #60A5FA; font-size: 1rem; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 構建九宮盤 HTML
    tian_pan = chart.get("天盤", {})
    di_pan = chart.get("地盤", {})
    men_map = chart.get("門", {})
    xing_map = chart.get("星", {})
    shen_map = chart.get("神", {})
    
    grid_html = '<div class="qimen-grid">'
    for row in GONG_GRID:
        for gong in row:
            tp = tian_pan.get(gong, "")
            dp = di_pan.get(gong, "")
            m = men_map.get(gong, "")
            x = xing_map.get(gong, "")
            s = shen_map.get(gong, "")
            
            is_benming = (gong == benming_gong)
            cell_class = "qimen-cell benming" if is_benming else "qimen-cell"
            if gong == "中":
                cell_class += " zhong"
            
            label = f"<b>{gong}</b>"
            if is_benming:
                label += f" <span style='color:#EF4444;'>★{auto_cn('本命')}</span>"
            
            if gong == "中":
                content = f"{label}<br>{auto_cn('天乙')}：{chart.get('天乙', '')}<br>{auto_cn('地')}：{dp}"
            else:
                content = f"{label}<br><span class='qimen-shen'>{auto_cn('神')}：{SHEN_FULLNAME.get(s, s)}</span><br><span class='qimen-xing'>{auto_cn('星')}：{x}</span><br><span class='qimen-men'>{auto_cn('門')}：{m}</span><br>{auto_cn('天')}：{tp} / {auto_cn('地')}：{dp}"
            
            grid_html += f'<div class="{cell_class}">{content}</div>'
    
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # ── 基本資訊 + 本命宮 + 值符值使（緊湊佈局，手機版一頁可見）──
    # 構建完整 HTML
    info_cards_html = []
    
    # 基本資訊（四柱 + 排局）
    info_cards_html.append(f'''
    <div class="qimen-info-card">
        <h4>四柱</h4>
        <div class="qimen-sizhu">
            <span>年：{sizhu.get("年柱", "")}</span>
            <span>月：{sizhu.get("月柱", "")}</span>
            <span>日：{sizhu.get("日柱", "")}</span>
            <span>時：{sizhu.get("時柱", "")}</span>
        </div>
        <div style="margin-top:6px;font-size:12px;">
            排局：<b>{chart.get("排局", "")}</b> | 
            節氣：<b>{chart.get("節氣", "")}</b>
        </div>
    </div>
    ''')
    
    # 本命宮
    if benming_info:
        info_cards_html.append(f'''
        <div class="qimen-info-card qimen-benming">
            <h4>★ 本命宮</h4>
            <div style="font-size:13px;margin-bottom:4px;">
                <b>{benming_gong}</b> ({benming_gan} {GAN_WUXING.get(benming_gan, "")})
            </div>
            <div style="font-size:11px;line-height:1.6;">
                <div>天：{benming_info.get("天干", "")}</div>
                <div>地：{benming_info.get("地干", "")}</div>
                <div>門：{benming_info.get("門", "")}</div>
                <div>星：{benming_info.get("星", "")}</div>
                <div>神：{SHEN_FULLNAME.get(benming_info.get("神", ""), benming_info.get("神", ""))}</div>
            </div>
        </div>
        ''')
    
    # 值符宮
    zhifu = result.get("值符宮", {})
    if zhifu and zhifu.get("宮位"):
        zf_info = zhifu.get("資訊", {})
        info_cards_html.append(f'''
        <div class="qimen-info-card qimen-zhifu">
            <h4>值符</h4>
            <div style="font-size:13px;margin-bottom:4px;">
                <b>{zhifu.get("宮位", "")}</b>
            </div>
            <div style="font-size:11px;line-height:1.6;">
                <div>天：{zf_info.get("天干", "")}</div>
                <div>地：{zf_info.get("地干", "")}</div>
                <div>門：{zf_info.get("門", "")}</div>
                <div>星：{zf_info.get("星", "")}</div>
                <div>神：{SHEN_FULLNAME.get(zf_info.get("神", ""), zf_info.get("神", ""))}</div>
            </div>
            <div style="margin-top:6px;font-size:10px;color:#888;">
                {zhifu.get("意義", "")}
            </div>
        </div>
        ''')
    
    # 值使宮
    zhishi = result.get("值使宮", {})
    if zhishi and zhishi.get("宮位"):
        zs_info = zhishi.get("資訊", {})
        info_cards_html.append(f'''
        <div class="qimen-info-card qimen-zhifu">
            <h4>值使</h4>
            <div style="font-size:13px;margin-bottom:4px;">
                <b>{zhishi.get("宮位", "")}</b>
            </div>
            <div style="font-size:11px;line-height:1.6;">
                <div>天：{zs_info.get("天干", "")}</div>
                <div>地：{zs_info.get("地干", "")}</div>
                <div>門：{zs_info.get("門", "")}</div>
                <div>星：{zs_info.get("星", "")}</div>
                <div>神：{SHEN_FULLNAME.get(zs_info.get("神", ""), zs_info.get("神", ""))}</div>
            </div>
            <div style="margin-top:6px;font-size:10px;color:#888;">
                {zhishi.get("意義", "")}
            </div>
        </div>
        ''')
    
    # 組合完整 HTML
    full_html = f'''
    <style>
    @media (max-width: 768px) {{
        .qimen-info-grid {{ 
            display: grid; 
            grid-template-columns: repeat(2, 1fr); 
            gap: 8px; 
            margin: 12px 0;
            font-size: 11px;
        }}
        .qimen-info-card {{
            background: #1a1a2e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            color: #ffffff;
            min-height: 140px;
        }}
        .qimen-info-card h4 {{
            margin: 0 0 8px 0;
            color: #EAB308;
            font-size: 13px;
            font-weight: bold;
        }}
        .qimen-info-card .info-row {{
            line-height: 1.8;
            font-size: 12px;
        }}
        .qimen-sizhu {{ display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; }}
        .qimen-sizhu span {{ background: #333; padding: 3px 8px; border-radius: 4px; font-size: 11px; color: #ffffff; }}
        .qimen-benming {{ background: rgba(239,68,68,0.15); border-color: #EF4444; }}
        .qimen-zhifu {{ background: rgba(234,179,8,0.15); border-color: #EAB308; }}
    }}
    @media (min-width: 769px) {{
        .qimen-info-grid {{ 
            display: grid; 
            grid-template-columns: repeat(4, 1fr); 
            gap: 12px; 
            margin: 16px 0;
        }}
        .qimen-info-card {{
            background: #1a1a2e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            color: #ffffff;
            min-height: 150px;
        }}
        .qimen-info-card h4 {{
            margin: 0 0 10px 0;
            color: #EAB308;
            font-size: 14px;
            font-weight: bold;
        }}
        .qimen-info-card .info-row {{
            line-height: 1.8;
            font-size: 13px;
        }}
    }}
    </style>
    <div class="qimen-info-grid">{''.join(info_cards_html)}</div>
    '''
    
    import streamlit.components.v1 as components
    components.html(full_html, height=380)
    st.divider()

    # ── 六親分析 ──

    # ── 六親分析 ──
    st.markdown(f"#### {auto_cn('六親分析')}")
    st.caption(auto_cn("以本命年干五行為主，查看各宮奇儀之生克關係"))

    six_rels = result.get("六親分析", [])
    # 按六親分組
    liuqin_groups: dict[str, list] = {}
    for rel in six_rels:
        lq = rel["六親"]
        liuqin_groups.setdefault(lq, []).append(rel)

    for lq_name, rels in liuqin_groups.items():
        emoji = next((v for k, v in LIUQIN_EMOJI.items() if k in lq_name), "⚪")
        with st.expander(auto_cn(f"{emoji} {lq_name}"), expanded=False):
            for rel in rels:
                gong = rel["宮位"]
                st.markdown(
                    f"**{gong}宮** — "
                    f"天干：{rel['天干']}（{rel['天干五行']}{rel['天干陰陽']}）　"
                    f"門：{rel['門']}　星：{rel['星']}　"
                    f"神：{rel['神全名']}"
                )
                dd = rel.get("門斷語", {})
                if dd:
                    if dd.get("summary"):
                        st.caption(auto_cn(dd["summary"]))
                    if dd.get("斷語"):
                        st.info(auto_cn(dd["斷語"]))
                    # 顯示多重斷語（官祿/疾厄 或 妻妾/財帛）
                    for sub_key in ("官祿", "疾厄", "妻妾", "財帛"):
                        if sub_key in dd and dd[sub_key]:
                            st.markdown(f"　— {auto_cn(sub_key)}：{auto_cn(dd[sub_key])}")

                if rel.get("神性情"):
                    st.caption(auto_cn(f"八將性情：{rel['神性情']}"))

    st.divider()

    # ── 八神喜忌 ──
    shen_special = result.get("八神喜忌", [])
    if shen_special:
        st.markdown(f"#### {auto_cn('八神（八將）特殊喜忌')}")
        for sp in shen_special:
            st.markdown(
                f"**{sp['宮位']}宮**（{auto_cn(sp['六親'])}）— {auto_cn(sp['神'])}：{auto_cn(sp['喜忌'])}"
            )
        st.divider()

    # ── 十干迫制 ──
    suppression = result.get("十干迫制", "")
    if suppression:
        st.markdown(f"#### {auto_cn('十干迫制')}")
        st.warning(auto_cn(suppression))
        st.divider()

    # ── 格局分析 ──
    patterns = result.get("格局分析", [])
    if patterns:
        st.markdown(f"#### {auto_cn('格局分析')}")
        for p in patterns:
            if any(w in p for w in XIONG_KEYWORDS):
                st.error(auto_cn(p))
            elif any(w in p for w in ("吉", "貴")):
                st.success(auto_cn(p))
            else:
                st.info(auto_cn(p))
        st.divider()

    # ── 綜合評斷 ──
    overall = result.get("綜合評斷", "")
    if overall:
        st.markdown(f"#### {auto_cn('綜合評斷')}")
        st.markdown(f"> {auto_cn(overall)}")

    if after_chart_hook:
        after_chart_hook()
