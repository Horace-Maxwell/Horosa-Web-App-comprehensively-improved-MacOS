# -*- coding: utf-8 -*-
"""
六爻終身卦 — 核心計算模組
Lifetime Liu Yao Hexagram — Core Calculator

本模組直接讀取 ichingshifa 數據庫，並重新實現 gangzhi / datetime_bookgua 邏輯，
避免對 ephem 庫的依賴（ephem 在 Python 3.12 上不相容）。

算法依據：
  - 農曆年干支地支數 + 農曆月 + 農曆日 + 時辰地支數 = 上卦、下卦、動爻
  - 與 ichingshifa.Iching.datetime_bookgua() 等效
  - 納甲排盤參考 ichingshifa.Iching.decode_gua()

古法依據：
  - 《卜筮正宗》（王洪緒）
  - 《增刪卜易》（野鶴老人）
  - 《六爻預測學》（邵偉華）
"""

from __future__ import annotations

import itertools
import os
import pickle
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sxtwl import fromSolar

from .constants import (
    DONG_YAO_LIFE_PERIODS,
    HEXAGRAM_LIFETIME,
    LIUQIN_LIFETIME,
    LIUSHEN_LIFETIME,
    MARRIAGE_COMPAT_DESC,
    WUXING_KE,
    WUXING_SHENG,
    YAO_NAMES,
    YAO_SYMBOLS,
)


# ──────────────────────────────────────────────────────────────────────────────
# 載入 ichingshifa 數據庫
# ──────────────────────────────────────────────────────────────────────────────

def _load_iching_data() -> Dict[str, Any]:
    """從 ichingshifa 套件載入 data.pkl。

    回傳：
        dict: ichingshifa 完整數據庫。

    異常：
        FileNotFoundError: 若找不到 data.pkl 文件。
    """
    import ichingshifa as _pkg
    base = os.path.dirname(_pkg.__file__)
    path = os.path.join(base, "data.pkl")
    with open(path, "rb") as fh:
        return pickle.load(fh)


_DATA: Dict[str, Any] = _load_iching_data()

# 常用查找表
_TIANGAN: List[str] = _DATA["干"]        # 甲乙丙丁戊己庚辛壬癸
_DIZHI: List[str] = _DATA["支"]          # 子丑寅卯辰巳午未申酉戌亥
_WUXIN: List[str] = _DATA["五行"]        # 金木水火土
_LIUQIN: List[str] = _DATA["六親"]       # 父母兄弟官鬼妻財子孫
_LIUQIN_W: Dict = _DATA["六親五行"]      # (五行+宮五行) → 六親
_MONS: List[str] = _DATA["六獸"]         # 青龍朱雀勾陳騰蛇白虎玄武
_SIXTYFOURGUA: Dict = _DATA["數字排六十四卦"]  # (碼) → 卦名
_EIGHT_GUA_STR: Dict = _DATA["數字排八卦"]   # (碼) → 八卦名
_EIGHTGUA_ELEMENT: Dict = _DATA["八卦卦象"]  # 宮號 → 天澤火震巽坎艮坤
_GUA_NAMES: List[str] = _DATA["八卦"]        # 乾坎坤離震...
_DOWN_CODES: List = _DATA["下卦數"]
_UP_CODES: List = _DATA["上卦數"]
_GUA_DOWN: Dict[str, Any] = dict(zip(_GUA_NAMES, _DOWN_CODES))
_GUA_UP: Dict[str, Any] = dict(zip(_GUA_NAMES, _UP_CODES))
_BAGUA_WUXING: Dict = _DATA["八宮卦五行"]
_BAGUA_PALACE: Dict = _DATA["八宮卦"]
_BAGUA_PURE: Dict = _DATA["八宮卦純卦"]
_SHIYING2: List = _DATA["世應排法"]
_SIXTYFOUR_INDEX: List[str] = _DATA["六十四卦"]
_CHIN_LIST: List[str] = _DATA["二十八宿"]
_SU_YAO: List = _DATA["二十八宿配干支"]
_FIVE_STARS: List = _DATA["五星"]
_SHEN: Dict = _DATA["世身"]
_GUA_DESCR: Dict = _DATA["易經卦爻詳解"]
_YUE_JIAN: List = _DATA["月建"]
_JISUAN: List = _DATA["積算"]

_FINDSHIYING: Dict = dict(
    zip(list(_BAGUA_PALACE.values()), _SHIYING2)
)
_ZHI_CODE: Dict[str, int] = dict(zip(_DIZHI, range(1, 13)))  # 子=1 … 亥=12


# ──────────────────────────────────────────────────────────────────────────────
# 輔助函數
# ──────────────────────────────────────────────────────────────────────────────

def _multi_key_get(d: Dict, key: Any) -> Any:
    """從以 tuple 為 key 的字典中查找 key。

    ichingshifa 的字典常以 tuple(多個碼) 作為鍵，
    本函數遍歷所有 key，找到包含 ``key`` 的 tuple 後回傳對應值。

    參數：
        d   (dict): 以 tuple 作為鍵的字典。
        key       : 目標查找值。

    回傳：
        對應值，找不到則回傳 None。
    """
    for keys, v in d.items():
        if key in keys:
            return v
    return None


def _new_list(olist: List, start: Any) -> List:
    """將列表從 start 元素開始循環排列。

    參數：
        olist (list): 原始列表。
        start       : 起始元素（必須存在於 olist 中）。

    回傳：
        list: 重新排列後的列表。
    """
    idx = olist.index(start)
    return [olist[(idx + i) % len(olist)] for i in range(len(olist))]


def _jiazi() -> List[str]:
    """生成六十甲子序列。

    回傳：
        List[str]: 60 個天干地支組合，由甲子起。
    """
    return [
        _TIANGAN[x % len(_TIANGAN)] + _DIZHI[x % len(_DIZHI)]
        for x in range(60)
    ]


def _find_lunar_month(year_gz: str) -> Dict[int, str]:
    """五虎遁年求月干支（正月起）。

    以年干確定正月天干，回傳農曆月份 → 月柱干支字典。

    參數：
        year_gz (str): 年干支，如「甲子」。

    回傳：
        Dict[int, str]: {月份: 干支}，月份 1-12。
    """
    five_tigers: Dict[Tuple[str, ...], str] = {
        tuple("甲己"): "丙寅",
        tuple("乙庚"): "戊寅",
        tuple("丙辛"): "庚寅",
        tuple("丁壬"): "壬寅",
        tuple("戊癸"): "甲寅",
    }
    result = _multi_key_get(five_tigers, year_gz[0])
    if result is None:
        result = _multi_key_get(five_tigers, year_gz[1])
    jz = _jiazi()
    return dict(zip(range(1, 13), _new_list(jz, result)[:12]))


def _find_lunar_hour(day_gz: str) -> Dict[str, str]:
    """五鼠遁日求時干支（子時起）。

    以日干確定子時天干，回傳時辰地支 → 時柱干支字典。

    參數：
        day_gz (str): 日干支，如「甲子」。

    回傳：
        Dict[str, str]: {地支: 干支}。
    """
    five_rats: Dict[Tuple[str, ...], str] = {
        tuple("甲己"): "甲子",
        tuple("乙庚"): "丙子",
        tuple("丙辛"): "戊子",
        tuple("丁壬"): "庚子",
        tuple("戊癸"): "壬子",
    }
    result = _multi_key_get(five_rats, day_gz[0])
    if result is None:
        result = _multi_key_get(five_rats, day_gz[1])
    jz = _jiazi()
    return dict(zip(list(_DIZHI), _new_list(jz, result)[:12]))


def _gangzhi(year: int, month: int, day: int, hour: int) -> List[str]:
    """計算年月日時四柱干支（不依賴 ephem）。

    使用 sxtwl 直接計算：
    - 23:00 起視為翌日子時 (依六爻傳統，23點後進入新的一天)
    - 1900 年前使用五虎遁推算月柱

    參數：
        year  (int): 公曆年。
        month (int): 公曆月。
        day   (int): 公曆日。
        hour  (int): 時辰（24小時制，0–23）。

    回傳：
        List[str]: [年柱, 月柱, 日柱, 時柱]，每個元素為兩字干支。
    """
    if year == 0:
        return ["無效"] * 4

    # 時辰 23 點後進入翌日子時
    calc_year, calc_month, calc_day, calc_hour = year, month, day, hour
    if hour == 23:
        dt = date(year, month, day) + timedelta(days=1)
        calc_year, calc_month, calc_day, calc_hour = (
            dt.year, dt.month, dt.day, 0
        )

    cdate = fromSolar(calc_year, calc_month, calc_day)
    y_gz = _TIANGAN[cdate.getYearGZ().tg] + _DIZHI[cdate.getYearGZ().dz]
    m_gz = _TIANGAN[cdate.getMonthGZ().tg] + _DIZHI[cdate.getMonthGZ().dz]
    d_gz = _TIANGAN[cdate.getDayGZ().tg] + _DIZHI[cdate.getDayGZ().dz]
    h_gz_raw = cdate.getHourGZ(calc_hour)
    h_gz = _TIANGAN[h_gz_raw.tg] + _DIZHI[h_gz_raw.dz]

    # 1900 年前用五虎遁推算月柱
    if calc_year < 1900:
        lunar = fromSolar(year, month, day)
        lunar_month = lunar.getLunarMonth()
        m_gz = _find_lunar_month(y_gz).get(lunar_month, m_gz)

    # 五鼠遁求時干（精確時柱）
    h_gz = _find_lunar_hour(d_gz).get(h_gz[1], h_gz)

    return [y_gz, m_gz, d_gz, h_gz]


def _lunar_date(year: int, month: int, day: int) -> Dict[str, int]:
    """取得農曆年月日。

    參數：
        year  (int): 公曆年。
        month (int): 公曆月。
        day   (int): 公曆日。

    回傳：
        Dict: {"年": 農曆年干支年, "月": 農曆月, "日": 農曆日}。
    """
    cdate = fromSolar(year, month, day)
    return {
        "年": cdate.getLunarYear(),
        "月": cdate.getLunarMonth(),
        "日": cdate.getLunarDay(),
    }


def _find_six_mons(day_gz: str) -> List[str]:
    """根據日干求六神順序（青龍起）。

    按「甲乙日青龍起、丙丁日朱雀起...」規則排列。

    參數：
        day_gz (str): 日干支。

    回傳：
        List[str]: 六神列表，長度 6，由初爻起。
    """
    mapping: Dict[Tuple[str, ...], str] = {
        tuple("甲乙"):  "青龍",
        tuple("丙丁"):  "朱雀",
        tuple("戊"):    "勾陳",
        tuple("己"):    "騰蛇",
        tuple("庚辛"):  "白虎",
        tuple("壬癸"):  "玄武",
    }
    start = _multi_key_get(mapping, day_gz[0])
    return _new_list(_MONS, start)[:6]


def _chin_iter(start: str) -> itertools.cycle:
    """從指定二十八宿位置開始的循環迭代器。"""
    return itertools.cycle(_new_list(_CHIN_LIST, start))


# ──────────────────────────────────────────────────────────────────────────────
# 十二長生查找表
# ──────────────────────────────────────────────────────────────────────────────

_CS_STARTS: Dict[str, str] = {
    "甲": "亥", "乙": "亥",
    "丙": "寅", "丁": "寅",
    "戊": "寅", "己": "寅",
    "庚": "巳", "辛": "巳",
    "壬": "申", "癸": "申",
}

_YANG_CS_STATES: List[str] = ["長生", "沐浴", "冠帶", "臨官", "帝旺", "衰", "病", "死", "墓", "絕", "胎", "養"]
_YIN_CS_STATES: List[str]  = ["死",   "病",   "衰",   "帝旺", "臨官", "冠帶", "沐浴", "長生", "養", "胎", "絕", "墓"]

_YIN_STEMS: set = {"乙", "丁", "己", "辛", "癸"}


def _get_changsheng(tiangan: str, dizhi: str) -> str:
    """計算天干在某地支的十二長生狀態。

    參數：
        tiangan (str): 天干，如「辛」。
        dizhi   (str): 地支，如「卯」。

    回傳：
        str: 長生狀態，如「帝旺」；若無法計算則回傳空字串。
    """
    start = _CS_STARTS.get(tiangan)
    if start is None or dizhi not in _DIZHI:
        return ""
    states = _YIN_CS_STATES if tiangan in _YIN_STEMS else _YANG_CS_STATES
    rotated = _new_list(_DIZHI, start)
    try:
        pos = rotated.index(dizhi)
    except ValueError:
        return ""
    return states[pos] if pos < len(states) else ""


def _get_shiying(gua_code: str) -> List[str]:
    """取得本卦世應爻位置列表。

    參數：
        gua_code (str): 6 位數字卦碼。

    回傳：
        List[str]: 六個爻的標記，"世" 或 "應" 或 ""。
    """
    gua_name = _multi_key_get(_SIXTYFOURGUA, gua_code)
    shiying_key = _multi_key_get(_BAGUA_PALACE, gua_name)
    return list(_FINDSHIYING.get(shiying_key, [""] * 6))


def _decode_single_gua(gua_code: str, day_gz: str) -> Dict[str, Any]:
    """對單一卦進行完整納甲排盤。

    依照 ichingshifa.Iching.decode_gua() 的算法實現，
    包含：天干、地支、五行、六親、六神、世應、伏神、納甲、二十八宿。

    參數：
        gua_code (str): 6 位數字卦碼，如 "777787"。
        day_gz   (str): 日干支，用於定六神起點，如 "甲子"。

    回傳：
        dict: 包含完整納甲排盤資料的字典。
    """
    gua_name = _multi_key_get(_SIXTYFOURGUA, gua_code)
    if gua_name is None:
        return {}

    # 世應爻位
    shiying = _get_shiying(gua_code)

    # 取下卦、上卦名稱
    down_gua_name = _multi_key_get(_EIGHT_GUA_STR, gua_code[:3])
    up_gua_name = _multi_key_get(_EIGHT_GUA_STR, gua_code[3:6])
    down_code = _GUA_DOWN.get(down_gua_name, [])
    up_code = _GUA_UP.get(up_gua_name, [])

    # 解析天干、地支、五行
    def _parse(codes: List, count: int) -> Tuple[List, List, List]:
        tg_lst, dz_lst, wx_lst = [], [], []
        for i in range(count):
            parts = codes[i].split(",")
            tg_lst.append(_TIANGAN[int(parts[0])])
            dz_lst.append(_DIZHI[int(parts[1])])
            wx_lst.append(_WUXIN[int(parts[2])])
        return tg_lst, dz_lst, wx_lst

    dt, dd, dw = _parse(down_code, 3)
    ut, ud, uw = _parse(up_code, 3)

    t_all = dt + ut   # 天干 (初爻→上爻)
    d_all = dd + ud   # 地支
    w_all = dw + uw   # 五行

    # 宮五行
    palace_wx = _multi_key_get(_BAGUA_WUXING, gua_name)

    # 六親
    lq = [_multi_key_get(_LIUQIN_W, wx + palace_wx) for wx in w_all]

    # 納甲（天干+地支）
    najia = [t_all[i] + d_all[i] for i in range(6)]

    # 二十八宿
    su_ref = dict(zip(_SIXTYFOUR_INDEX, _chin_iter("參"))).get(gua_name)
    su_yao_ref = dict(zip(_SIXTYFOUR_INDEX, _SU_YAO)).get(gua_name)
    ng = najia
    su_match = [c == su_yao_ref for c in ng]
    su_labels = [su_ref if m else "" for m in su_match]
    pos = su_match.index(True) if True in su_match else 0
    revlist = list(reversed(_new_list(_CHIN_LIST, su_ref)))
    if pos == 0:
        xiu = _new_list(_CHIN_LIST, su_ref)[:6]
    elif pos == 5:
        xiu = revlist[-6:]
    elif pos == 4:
        xiu = revlist[-6:][1:] + [revlist[0]]
    elif pos == 3:
        xiu = revlist[-6:][2:] + revlist[:2]
    elif pos == 2:
        xiu = revlist[-6:][3:] + revlist[:3]
    else:
        xiu = revlist[-6:][4:] + revlist[:4]

    # 五星
    five_star = dict(zip(_SIXTYFOUR_INDEX, itertools.cycle(_FIVE_STARS))).get(gua_name, "")

    # 六神
    liu_shen = _find_six_mons(day_gz)

    # 世爻身爻
    try:
        shi_idx = shiying.index("世")
        shen_idx_raw = _multi_key_get(_SHEN, d_all[shi_idx])
        shen_str = lq[shen_idx_raw] + t_all[shen_idx_raw] + d_all[shen_idx_raw] + w_all[shen_idx_raw]
    except (ValueError, TypeError, IndexError):
        shi_idx = 0
        shen_str = ""

    # 月建 / 積算
    jian_code = dict(zip(_SIXTYFOUR_INDEX, _YUE_JIAN)).get(gua_name, "甲子")
    jian = _new_list(_jiazi(), jian_code)[:6]
    ji_code = dict(zip(_SIXTYFOUR_INDEX, _JISUAN)).get(gua_name, "甲子")
    jisuan_all = _new_list(_jiazi(), ji_code)

    # 伏神（找在宮純卦中出現、而本卦中缺失的六親）
    all_lq_set = set(lq)
    missing_lq = [ln for ln in _LIUQIN if ln not in all_lq_set]
    fu_yao: Any = ""
    if missing_lq:
        fu_name = missing_lq[0]
        pure_code = _multi_key_get(_BAGUA_PURE, gua_name)
        if pure_code:
            fu_gua = _decode_single_gua_light(pure_code)
            fu_lq = fu_gua.get("六親用神", [])
            fu_t = fu_gua.get("天干", [])
            fu_d = fu_gua.get("地支", [])
            fu_w = fu_gua.get("五行", [])
            try:
                fu_num = fu_lq.index(fu_name)
                fuyao1 = fu_lq[fu_num] + fu_t[fu_num] + fu_d[fu_num] + fu_w[fu_num]
                fu_yao = {
                    "伏神所在爻": lq[fu_num],
                    "伏神六親": fu_name,
                    "伏神爻": fuyao1,
                    "伏神天干地支五行": fu_t[fu_num] + fu_d[fu_num] + fu_w[fu_num],
                    "伏神爻位": fu_num,  # 0-5，對應初爻到上爻
                }
            except (ValueError, IndexError):
                fu_yao = ""

    return {
        "卦": gua_name,
        "五星": five_star,
        "世應卦": _multi_key_get(_BAGUA_PALACE, gua_name) + "卦",
        "星宿": xiu,
        "天干": t_all,
        "地支": d_all,
        "五行": w_all,
        "世應爻": shiying,
        "身爻": shen_str,
        "六親用神": lq,
        "伏神": fu_yao,
        "六神": liu_shen,
        "納甲": najia,
        "建月": jian,
        "積算": jisuan_all,
        "下卦": down_gua_name,
        "上卦": up_gua_name,
        "宮五行": palace_wx,
    }


def _decode_single_gua_light(gua_code: str) -> Dict[str, Any]:
    """輕量版 decode（不含六神/伏神），用於伏神計算。"""
    gua_name = _multi_key_get(_SIXTYFOURGUA, gua_code)
    if gua_name is None:
        return {}
    down_gua_name = _multi_key_get(_EIGHT_GUA_STR, gua_code[:3])
    up_gua_name = _multi_key_get(_EIGHT_GUA_STR, gua_code[3:6])
    down_code = _GUA_DOWN.get(down_gua_name, [])
    up_code = _GUA_UP.get(up_gua_name, [])

    def _parse(codes: List, count: int) -> Tuple[List, List, List]:
        tg_lst, dz_lst, wx_lst = [], [], []
        for i in range(count):
            parts = codes[i].split(",")
            tg_lst.append(_TIANGAN[int(parts[0])])
            dz_lst.append(_DIZHI[int(parts[1])])
            wx_lst.append(_WUXIN[int(parts[2])])
        return tg_lst, dz_lst, wx_lst

    dt, dd, dw = _parse(down_code, 3)
    ut, ud, uw = _parse(up_code, 3)
    t_all, d_all, w_all = dt + ut, dd + ud, dw + uw
    palace_wx = _multi_key_get(_BAGUA_WUXING, gua_name)
    lq = [_multi_key_get(_LIUQIN_W, wx + palace_wx) for wx in w_all]
    return {
        "六親用神": lq,
        "天干": t_all,
        "地支": d_all,
        "五行": w_all,
    }


# ──────────────────────────────────────────────────────────────────────────────
# 資料類
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class YaoInfo:
    """單一爻的完整資訊。"""
    position: int        # 爻位 1-6（初爻=1，上爻=6）
    code: str            # "7"/"8"/"9"/"6"
    tiangan: str         # 天干
    dizhi: str           # 地支
    wuxing: str          # 五行
    liuqin: str          # 六親
    liushen: str         # 六神
    najia: str           # 納甲（天干+地支）
    xiu: str             # 二十八宿
    changsheng: str      # 十二長生狀態（帝旺/病/墓…）
    shiying: str         # 世/應/""
    is_dong: bool        # 是否為動爻
    symbol: str          # 爻象符號
    yao_name: str        # 爻名（初爻…上爻）
    yao_text: str        # 爻辭


@dataclass
class HexagramLayout:
    """完整六爻排盤結果。"""
    gua_code: str           # 6 位數卦碼
    gua_name: str           # 本卦名
    biangua_code: str       # 之卦碼
    biangua_name: str       # 之卦名
    dong_yao: int           # 動爻爻位 (1-6)
    yao_list: List[YaoInfo] # 六爻列表（初爻→上爻）
    palace_wx: str          # 宮五行
    five_star: str          # 五星
    shiying_palace: str     # 世應宮卦
    guaci: str              # 卦辭
    tuanci: str             # 彖辭
    dong_yao_text: str      # 動爻爻辭
    shen_str: str = ""      # 身爻干支描述
    fuyao: Any = None       # 伏神資料（dict 或 None）
    biangua_layout: Optional["HexagramLayout"] = None  # 之卦排盤


@dataclass
class LifetimeResult:
    """六爻終身卦完整計算結果。"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location_name: str

    # 四柱干支
    year_gz: str
    month_gz: str
    day_gz: str
    hour_gz: str

    # 農曆
    lunar_year: int
    lunar_month: int
    lunar_day: int

    # 起卦關鍵數值
    year_zhi_code: int
    hour_zhi_code: int

    # 本卦 / 之卦
    hexagram: HexagramLayout

    # 終身解讀
    lifetime_interp: Dict[str, str] = field(default_factory=dict)

    # 動爻對應人生大限
    life_period: Dict[str, str] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────────
# 主計算類
# ──────────────────────────────────────────────────────────────────────────────

class LifetimeHexagramCalculator:
    """六爻終身卦計算器。

    根據出生時間計算固定終身本命卦，完整納甲排盤，
    並提供終身性格、事業、婚姻、財運、健康等解讀。

    算法：
        上卦 = (年支數 + 農曆月 + 農曆日 + 時支數) % 8
        下卦 = (年支數 + 農曆月 + 農曆日) % 8
        動爻 = (年支數 + 農曆月 + 農曆日 + 時支數) % 6

    與 ichingshifa.Iching.datetime_bookgua() 完全等效。

    參數：
        year           (int): 公曆年。
        month          (int): 公曆月。
        day            (int): 公曆日。
        hour           (int): 時辰（0–23）。
        minute         (int): 分鐘（0–59，預設 0）。
        location_name  (str): 地點名稱（顯示用）。
    """

    # 八宮卦碼對照 (1-8 → 三爻卦碼)
    _EIGHT_GUA_CODES: Dict[int, str] = {
        1: "777",
        2: "778",
        3: "787",
        4: "788",
        5: "877",
        6: "878",
        7: "887",
        8: "888",
    }

    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        location_name: str = "",
    ) -> None:
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.location_name = location_name

    # ── 公開介面 ──────────────────────────────────────────────

    def compute(self) -> LifetimeResult:
        """執行完整終身卦計算。

        回傳：
            LifetimeResult: 完整計算結果，包含本卦、之卦、納甲排盤、終身解讀。
        """
        gz = _gangzhi(self.year, self.month, self.day, self.hour)
        ld = _lunar_date(self.year, self.month, self.day)

        y_gz, m_gz, d_gz, h_gz = gz
        yz_code = _ZHI_CODE.get(y_gz[1], 1)   # 年支數
        hz_code = _ZHI_CODE.get(h_gz[1], 1)   # 時支數
        cm = ld["月"]                           # 農曆月
        cd = ld["日"]                           # 農曆日

        # 起卦
        gua_code, biangua_code, dong_yao = self._calc_gua(
            yz_code, cm, cd, hz_code
        )

        # 建立本卦排盤
        hexagram = self._build_layout(gua_code, biangua_code, dong_yao, d_gz)

        # 終身解讀
        gua_name = hexagram.gua_name
        lifetime_interp = HEXAGRAM_LIFETIME.get(gua_name, {})
        life_period = DONG_YAO_LIFE_PERIODS.get(dong_yao, {})

        return LifetimeResult(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            location_name=self.location_name,
            year_gz=y_gz,
            month_gz=m_gz,
            day_gz=d_gz,
            hour_gz=h_gz,
            lunar_year=ld["年"],
            lunar_month=cm,
            lunar_day=cd,
            year_zhi_code=yz_code,
            hour_zhi_code=hz_code,
            hexagram=hexagram,
            lifetime_interp=lifetime_interp,
            life_period=life_period,
        )

    @staticmethod
    def compute_compatibility(
        result1: LifetimeResult,
        result2: LifetimeResult,
    ) -> Dict[str, Any]:
        """計算兩人終身卦合婚相性。

        根據兩人終身卦宮五行生剋關係判斷相性。

        參數：
            result1 (LifetimeResult): 甲方計算結果。
            result2 (LifetimeResult): 乙方計算結果。

        回傳：
            dict: 含相性等級、描述、建議的字典。
        """
        wx1 = result1.hexagram.palace_wx
        wx2 = result2.hexagram.palace_wx

        if wx1 == wx2:
            compat_key = "比和"
        elif WUXING_SHENG.get(wx1) == wx2 or WUXING_SHENG.get(wx2) == wx1:
            compat_key = "相生"
        else:
            compat_key = "相克"

        compat = MARRIAGE_COMPAT_DESC.get(compat_key, {})
        return {
            "person1_gua": result1.hexagram.gua_name,
            "person2_gua": result2.hexagram.gua_name,
            "person1_wx": wx1,
            "person2_wx": wx2,
            "compat_type": compat_key,
            "level": compat.get("level", ""),
            "desc": compat.get("desc", ""),
            "advice": compat.get("advice", ""),
            "color": compat.get("color", "#888888"),
        }

    # ── 內部方法 ──────────────────────────────────────────────

    def _calc_gua(
        self,
        yz_code: int,
        cm: int,
        cd: int,
        hz_code: int,
    ) -> Tuple[str, str, int]:
        """核心起卦算法。

        依據 ichingshifa.datetime_bookgua 等效算法：
            上卦 = (yz + cm + cd + hz) % 8  (0→8)
            下卦 = (yz + cm + cd) % 8       (0→8)
            動爻 = (yz + cm + cd + hz) % 6  (0→6)

        參數：
            yz_code (int): 年支數 (1–12)。
            cm      (int): 農曆月 (1–12)。
            cd      (int): 農曆日 (1–30)。
            hz_code (int): 時支數 (1–12)。

        回傳：
            Tuple[str, str, int]: (本卦碼, 之卦碼, 動爻位 1-6)。
        """
        upper_r = (yz_code + cm + cd + hz_code) % 8
        if upper_r == 0:
            upper_r = 8
        lower_r = (yz_code + cm + cd) % 8
        if lower_r == 0:
            lower_r = 8

        upper_code = self._EIGHT_GUA_CODES[upper_r]
        lower_code = self._EIGHT_GUA_CODES[lower_r]
        combine = list(lower_code + upper_code)

        dong_yao = (yz_code + cm + cd + hz_code) % 6
        if dong_yao == 0:
            dong_yao = 6

        # 標記動爻（9=老陽，6=老陰）
        idx = dong_yao - 1
        combine[idx] = combine[idx].replace("7", "9").replace("8", "6")
        gua_code = "".join(combine)

        # 之卦（動爻翻轉）
        bian_code = gua_code.replace("6", "7").replace("9", "8")

        return gua_code, bian_code, dong_yao

    def _build_layout(
        self,
        gua_code: str,
        biangua_code: str,
        dong_yao: int,
        day_gz: str,
    ) -> HexagramLayout:
        """建立完整六爻排盤。

        參數：
            gua_code     (str): 本卦 6 位數字碼。
            biangua_code (str): 之卦 6 位數字碼。
            dong_yao     (int): 動爻爻位 (1–6)。
            day_gz       (str): 日柱干支。

        回傳：
            HexagramLayout: 完整排盤資料。
        """
        decoded = _decode_single_gua(gua_code, day_gz)
        gua_name = decoded.get("卦", "")

        # 取爻辭
        descr = _GUA_DESCR.get(gua_name, {})
        guaci = descr.get(0, "")
        tuanci = descr.get(7, "")
        dong_text = descr.get(dong_yao, "")

        t_all = decoded.get("天干", [""] * 6)
        d_all = decoded.get("地支", [""] * 6)
        w_all = decoded.get("五行", [""] * 6)
        lq_all = decoded.get("六親用神", [""] * 6)
        ls_all = decoded.get("六神", [""] * 6)
        nj_all = decoded.get("納甲", [""] * 6)
        xiu_all = decoded.get("星宿", [""] * 6)
        sy_all = decoded.get("世應爻", [""] * 6)

        yao_list: List[YaoInfo] = []
        for i in range(6):
            pos = i + 1
            code_ch = gua_code[i]
            is_dong = (pos == dong_yao)
            yao_text = descr.get(pos, "")
            tg = t_all[i] if i < len(t_all) else ""
            dz = d_all[i] if i < len(d_all) else ""
            yao_list.append(YaoInfo(
                position=pos,
                code=code_ch,
                tiangan=tg,
                dizhi=dz,
                wuxing=w_all[i] if i < len(w_all) else "",
                liuqin=lq_all[i] if i < len(lq_all) else "",
                liushen=ls_all[i] if i < len(ls_all) else "",
                najia=nj_all[i] if i < len(nj_all) else "",
                xiu=xiu_all[i] if i < len(xiu_all) else "",
                changsheng=_get_changsheng(tg, dz),
                shiying=sy_all[i] if i < len(sy_all) else "",
                is_dong=is_dong,
                symbol=YAO_SYMBOLS.get(code_ch, "—"),
                yao_name=YAO_NAMES.get(pos, f"{pos}爻"),
                yao_text=yao_text,
            ))

        # 之卦排盤（淺解，不再遞迴）
        bian_decoded = _decode_single_gua_light(biangua_code)
        biangua_name = _multi_key_get(_SIXTYFOURGUA, biangua_code) or ""
        bian_t = bian_decoded.get("天干", [""] * 6)
        bian_d = bian_decoded.get("地支", [""] * 6)
        bian_w = bian_decoded.get("五行", [""] * 6)
        bian_lq = bian_decoded.get("六親用神", [""] * 6)
        bian_nj = [bian_t[i] + bian_d[i] for i in range(6)]
        bian_yao_list: List[YaoInfo] = []
        for i in range(6):
            pos = i + 1
            code_ch = biangua_code[i]
            bian_yao_list.append(YaoInfo(
                position=pos,
                code=code_ch,
                tiangan=bian_t[i] if i < len(bian_t) else "",
                dizhi=bian_d[i] if i < len(bian_d) else "",
                wuxing=bian_w[i] if i < len(bian_w) else "",
                liuqin=bian_lq[i] if i < len(bian_lq) else "",
                liushen="",
                najia=bian_nj[i] if i < len(bian_nj) else "",
                xiu="",
                changsheng="",
                shiying="",
                is_dong=(pos == dong_yao),
                symbol=YAO_SYMBOLS.get(code_ch, "—"),
                yao_name=YAO_NAMES.get(pos, f"{pos}爻"),
                yao_text="",
            ))

        biangua_layout = HexagramLayout(
            gua_code=biangua_code,
            gua_name=biangua_name,
            biangua_code=gua_code,
            biangua_name=gua_name,
            dong_yao=dong_yao,
            yao_list=bian_yao_list,
            palace_wx=_multi_key_get(_BAGUA_WUXING, biangua_name) or "",
            five_star="",
            shiying_palace="",
            guaci=_GUA_DESCR.get(biangua_name, {}).get(0, ""),
            tuanci=_GUA_DESCR.get(biangua_name, {}).get(7, ""),
            dong_yao_text="",
        )

        return HexagramLayout(
            gua_code=gua_code,
            gua_name=gua_name,
            biangua_code=biangua_code,
            biangua_name=biangua_name,
            dong_yao=dong_yao,
            yao_list=yao_list,
            palace_wx=decoded.get("宮五行", ""),
            five_star=decoded.get("五星", ""),
            shiying_palace=decoded.get("世應卦", ""),
            guaci=guaci,
            tuanci=tuanci,
            dong_yao_text=dong_text,
            shen_str=decoded.get("身爻", ""),
            fuyao=decoded.get("伏神") or None,
            biangua_layout=biangua_layout,
        )


# ──────────────────────────────────────────────────────────────────────────────
# 模組級別便捷函數
# ──────────────────────────────────────────────────────────────────────────────

def compute_lifetime_hexagram(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    location_name: str = "",
) -> LifetimeResult:
    """計算六爻終身卦的便捷函數。

    參數：
        year          (int): 公曆年。
        month         (int): 公曆月 (1–12)。
        day           (int): 公曆日 (1–31)。
        hour          (int): 出生時辰（24小時制，0–23）。
        minute        (int): 出生分鐘（0–59）。
        location_name (str): 地點名稱。

    回傳：
        LifetimeResult: 完整計算結果。

    範例：
        >>> result = compute_lifetime_hexagram(1990, 5, 15, 8)
        >>> print(result.hexagram.gua_name)
    """
    calc = LifetimeHexagramCalculator(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        location_name=location_name,
    )
    return calc.compute()
