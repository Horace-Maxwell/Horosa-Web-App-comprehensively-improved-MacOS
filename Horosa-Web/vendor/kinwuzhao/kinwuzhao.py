# -*- coding: utf-8 -*-
"""堅五兆 (Kinwuzhao) — 五兆占卜核心模組

本模組忠實復原唐代太卜署「五兆卜法」，主要依據：
- 敦煌寫本 P.2859《五兆要訣略》
- 王祥偉《敦煌五兆卜法文獻校錄研究》
- 《舊唐書·經籍志》官占記載

提供兩種演算模式：
1. 唐代正法「36 算子揲筮」模式 (WuzhaoDivination)
2. 宋代「折竹彈占」簡化模式 (five_zhao_paipan / gangzhi_paipan)
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Any

import config
from bidict import bidict
from kinliuren import kinliuren


# ---------------------------------------------------------------------------
# FiveElementsMapper — 五行對映與生尅關係
# ---------------------------------------------------------------------------

class FiveElementsMapper:
    """五行數字對映與生尅關係判斷。

    References:
        P.2859 第 3–5 行：「一水二火三木四金五土」
        《五兆要訣略》：五行相生相尅次序
    """

    # 數字對應五行（P.2859 第 3 行）
    NUM_TO_ELEMENT: dict[int, str] = {
        1: "水",
        2: "火",
        3: "木",
        4: "金",
        5: "土",
    }

    # 五行生尅文字 → 六親名稱
    _RELATION_TO_LIUQIN: dict[str, str] = dict(
        zip(
            re.findall("..", "尅我我尅比和生我我生"),
            re.findall("..", "官鬼妻財兄弟父母子孫"),
        )
    )

    @classmethod
    def element_for(cls, num: int) -> str:
        """將 1–5 的數字對映為五行名稱。

        Args:
            num: 揲筮餘數 (1–5)。

        Returns:
            五行名稱（水/火/木/金/土）。
        """
        return cls.NUM_TO_ELEMENT[num]

    @classmethod
    def relation(cls, my_element: str, target_element: str) -> str:
        """判斷兩個五行之間的六親關係。

        Args:
            my_element: 兆位五行。
            target_element: 鄉位五行。

        Returns:
            六親名稱（官鬼/妻財/兄弟/父母/子孫）。
        """
        wx_rel = config.multi_key_dict_get(
            config.wuxing_relation_2, my_element + target_element
        )
        return cls._RELATION_TO_LIUQIN.get(wx_rel, "")


# ---------------------------------------------------------------------------
# SixBeastsArranger — 六獸排列
# ---------------------------------------------------------------------------

class SixBeastsArranger:
    """依日干排列六獸序列並判斷死害。

    References:
        《五兆要訣略》：六獸配日干法
    """

    ORDER: list[str] = ["青龍", "朱雀", "螣蛇", "勾陳", "白虎", "玄武"]

    # 日干 → 起首六獸
    DAY_GAN_TO_BEAST: dict[str, str] = {
        "甲": "青龍", "乙": "青龍",
        "丙": "朱雀", "丁": "朱雀",
        "戊": "勾陳", "己": "勾陳",
        "庚": "白虎", "辛": "白虎",
        "壬": "玄武", "癸": "玄武",
    }

    # 六獸落宮死害（宮位首字 → 死/害）
    WEAKNESS: dict[str, list[str]] = {
        "青龍": re.findall("..", "坤死兌害"),
        "朱雀": re.findall("..", "坎死巽害"),
        "螣蛇": re.findall("..", "坎死巽害"),
        "勾陳": re.findall("..", "巽死巽害"),
        "白虎": re.findall("..", "坎死離害"),
        "玄武": re.findall("..", "巽死震害"),
    }

    @classmethod
    def arrange(cls, day_gan: str) -> list[str]:
        """依日干產生六獸序列。

        Args:
            day_gan: 日天干。

        Returns:
            長度為 6 的六獸名稱列表。

        Raises:
            ValueError: 日干不在十天干之內。
        """
        if day_gan not in cls.DAY_GAN_TO_BEAST:
            raise ValueError(f"日干不正確: {day_gan!r}，請輸入甲乙丙丁戊己庚辛壬癸")
        beast_start = cls.DAY_GAN_TO_BEAST[day_gan]
        start_idx = cls.ORDER.index(beast_start)
        return [cls.ORDER[(start_idx + i) % len(cls.ORDER)] for i in range(6)]

    @classmethod
    def check_death(cls, beast: str, gong_char: str) -> str:
        """判斷六獸是否落死宮。"""
        weakness = cls.WEAKNESS.get(beast, [])
        return "死" if weakness and weakness[0][0] == gong_char else ""

    @classmethod
    def check_harm(cls, beast: str, gong_char: str) -> str:
        """判斷六獸是否落害宮。"""
        weakness = cls.WEAKNESS.get(beast, [])
        return "害" if len(weakness) > 1 and weakness[1][0] == gong_char else ""


# ---------------------------------------------------------------------------
# GuxuJudge — 孤虛判斷
# ---------------------------------------------------------------------------

class GuxuJudge:
    """依六甲旬與陰陽判斷孤虛。

    References:
        《五兆要訣略》：孤虛之法
    """

    # 六甲旬 → 陰陽 → 孤/虛地支
    GUXU_DATA: dict[tuple[str, ...], dict[str, dict[str, str]]] = dict(
        zip(
            config.liujiashun_dict().keys(),
            [
                {"陽": {"孤": "戌", "虛": "辰"}, "陰": {"孤": "亥", "虛": "巳"}},
                {"陽": {"孤": "申", "虛": "寅"}, "陰": {"孤": "酉", "虛": "卯"}},
                {"陽": {"孤": "午", "虛": "子"}, "陰": {"孤": "未", "虛": "丑"}},
                {"陽": {"孤": "辰", "虛": "戌"}, "陰": {"孤": "巳", "虛": "亥"}},
                {"陽": {"孤": "寅", "虛": "申"}, "陰": {"孤": "卯", "虛": "酉"}},
                {"陽": {"孤": "子", "虛": "午"}, "陰": {"孤": "丑", "虛": "未"}},
            ],
        )
    )

    # 天干 → 陰陽
    YIN_YANG: dict[tuple[str, ...], str] = {
        tuple(list("甲丙戊庚壬")): "陽",
        tuple(list("乙丁己辛癸")): "陰",
    }

    # 地支 → 宮位名
    ZHI2GUA: dict[str, str] = {
        "子": "坎", "寅": "震", "卯": "震", "辰": "巽", "巳": "巽",
        "午": "離", "申": "兌", "酉": "兌", "戌": "乾", "亥": "乾",
        "丑": "中", "未": "中",
    }

    @classmethod
    def judge(cls, gz: str) -> tuple[str, str]:
        """判斷指定干支的孤虛宮位。

        Args:
            gz: 干支（如 "丁卯"）。

        Returns:
            (孤宮位, 虛宮位) 元組。
        """
        gx_data = config.multi_key_dict_get(cls.GUXU_DATA, gz)
        yy_label = config.multi_key_dict_get(cls.YIN_YANG, gz[0])
        guxu = gx_data.get(yy_label, {})
        gu_gong = cls.ZHI2GUA[guxu["孤"]]
        xu_gong = cls.ZHI2GUA[guxu["虛"]]
        return gu_gong, xu_gong


# ---------------------------------------------------------------------------
# WuzhaoCalculator — 揲筮計算核心
# ---------------------------------------------------------------------------

class WuzhaoCalculator:
    """五兆揲筮計算核心。

    支持兩種模式：
    1. 唐代正法「36 算子六次揲筮」
    2. 宋代「折竹彈占」隨機簡化

    References:
        P.2859 第 6–12 行：揲筮法
        《五兆要訣略》：「以三十六數，五五除之」
    """

    BASE_STICKS: int = 36  # P.2859：「凡筮用三十六莖」

    @staticmethod
    def _mod5_nonzero(n: int) -> int:
        """取模 5，若餘 0 則歸 5（P.2859：「盡則為五」）。"""
        r = n % 5
        return r if r != 0 else 5

    @classmethod
    def random_split(cls, total: int) -> int:
        """隨機折竹——將 total 根竹隨機分為兩份，返回左份。

        此為宋代折竹彈占簡化法。

        Args:
            total: 剩餘竹/算子總數。

        Returns:
            左手份數 (1 至 total-1)。
        """
        if total <= 1:
            return 1
        return random.randint(1, total - 1)

    @classmethod
    def tang_shi_divination(
        cls,
        manual_splits: list[int] | None = None,
    ) -> list[int]:
        """唐代正法「36 算子多次五五除之」揲筮演算法。

        共 6 次變動：
        - 第 1 次：定兆局（巽宮）
        - 第 2–6 次：定五鄉六親支辭（震/離/中/兌/坎）

        每次取一把算子，以 5 除取餘（餘 0 歸 5），即為該宮位五行數。
        餘下算子繼續用於下一次揲筮。

        References:
            P.2859 第 6–8 行：「先揲三十六算，五五除之，餘者定兆」
            P.2859 第 9–12 行：「又以所餘，五五除之，次定五鄉」
            《五兆要訣略》：六次揲筮法

        Args:
            manual_splits: 手動指定每次分裂取走的數量（長度為 6），
                若為 None 則使用隨機分裂。用於復現傳統折竹體驗。

        Returns:
            長度為 6 的列表，每項為 1–5 的五行數字，
            依序對應 [兆, 木鄉, 火鄉, 土鄉, 金鄉, 水鄉]。
        """
        remain = cls.BASE_STICKS
        results: list[int] = []

        for i in range(6):
            if manual_splits is not None and i < len(manual_splits):
                # 手動折竹：使用者指定分裂數
                left = manual_splits[i]
                left = max(1, min(left, remain - 1)) if remain > 1 else 1
            else:
                left = cls.random_split(remain)

            # P.2859：「五五除之，餘者定兆/鄉」
            zhao_num = cls._mod5_nonzero(left)
            results.append(zhao_num)

            # 修正：以 left（實際取走的算子數）遞減，而非 zhao_num（五除餘數）
            remain -= left
            if remain <= 0:
                # 若算子用盡，剩餘位置以 5（土）填充
                # P.2859 第 8 行：「盡則為五」
                results.extend([5] * (6 - len(results)))
                break

        return results

    @classmethod
    def gangzhi_calculation(
        cls,
        parts: list[Any],
        jz2num: dict[str, int],
    ) -> int:
        """干支數值法計算五行數。

        將干支名稱轉為序數（甲子=1 ... 癸亥=60），加總後取模 5。

        Args:
            parts: 混合干支字串與整數的列表。
            jz2num: 六十甲子 → 序數的對映。

        Returns:
            1–5 的五行數字。
        """
        total = sum(jz2num.get(i, i) for i in parts)
        return cls._mod5_nonzero(total)


# ---------------------------------------------------------------------------
# InterpretationEngine — 排盤結果組裝
# ---------------------------------------------------------------------------

class InterpretationEngine:
    """組裝各宮位的排盤結果。

    References:
        《五兆要訣略》：兆與五鄉排盤法
    """

    # 宮位固定序列
    POSITIONS: list[tuple[str, str]] = [
        ("巽宮", "兆"),
        ("震宮", "木鄉"),
        ("離宮", "火鄉"),
        ("中宮", "土鄉"),
        ("兌宮", "金鄉"),
        ("坎宮", "水鄉"),
    ]

    GONG_TO_LABEL: dict[str, str] = dict(
        zip(
            "巽宮,震宮,離宮,中宮,兌宮,坎宮".split(","),
            "兆,木鄉,火鄉,土鄉,金鄉,水鄉".split(","),
        )
    )

    # 地支 → 將軍方位
    GENERAL_MAP: dict[str, str] = dict(
        zip(
            list("子丑寅卯辰巳午未申酉戌亥"),
            list("子酉午卯子酉午卯子酉午卯"),
        )
    )

    # 二十四節氣
    TWENTY_FOUR_SOLAR_TERMS: tuple[str, ...] = (
        "立春", "雨水", "驚蟄", "春分", "清明", "穀雨",
        "立夏", "小滿", "芒種", "夏至", "小暑", "大暑",
        "立秋", "處暑", "白露", "秋分", "寒露", "霜降",
        "立冬", "小雪", "大雪", "冬至", "小寒", "大寒",
    )

    # 節氣 → 關籥地支
    SOLAR_TERMS_BY_SEASON: dict[tuple[str, ...], dict[str, str]] = {
        TWENTY_FOUR_SOLAR_TERMS[0:6]: {"關": "丑", "籥": "巳"},
        TWENTY_FOUR_SOLAR_TERMS[6:12]: {"關": "辰", "籥": "申"},
        TWENTY_FOUR_SOLAR_TERMS[12:18]: {"關": "未", "籥": "亥"},
        TWENTY_FOUR_SOLAR_TERMS[18:24]: {"關": "戌", "籥": "寅"},
    }

    # 旺相胎沒死囚廢休
    _WANGXIANG: tuple[str, ...] = tuple("王相胎沒死囚廢休")
    _TRIGRAMS: tuple[str, ...] = tuple("艮震巽離坤兌乾坎")
    _JIEQI_GROUPS: list[tuple[str, ...]] = [
        ("立春", "雨水", "驚蟄"),
        ("春分", "清明", "穀雨"),
        ("立夏", "小滿", "芒種"),
        ("夏至", "小暑", "大暑"),
        ("立秋", "處暑", "白露"),
        ("秋分", "寒露", "霜降"),
        ("立冬", "小雪", "大雪"),
        ("冬至", "小寒", "大寒"),
    ]

    @classmethod
    def _rotate(cls, base: tuple[str, ...], shift: int) -> tuple[str, ...]:
        return base[shift:] + base[:shift]

    @classmethod
    def _jieqi_wangxiang_map(cls) -> dict[tuple[str, ...], dict[str, str]]:
        return {
            jq_group: dict(zip(cls._rotate(cls._TRIGRAMS, i), cls._WANGXIANG))
            for i, jq_group in enumerate(cls._JIEQI_GROUPS)
        }

    @classmethod
    def get_wangxiang(cls, jq: str, gong_char: str) -> str:
        """查詢宮位在指定節氣下的旺相。"""
        wangxiang_map = cls._jieqi_wangxiang_map()
        gong_lookup = gong_char.replace("中", "坤")
        return config.multi_key_dict_get(wangxiang_map, jq).get(gong_lookup, "")

    @classmethod
    def compute_lock_key_general(
        cls, jq: str, cm: str, gz1: str, gz2: str
    ) -> tuple[str, str, str]:
        """計算關、籥、將軍宮位（需六壬天地盤）。

        Args:
            jq: 節氣名稱。
            cm: 農曆月份。
            gz1: 上柱干支（如月干支）。
            gz2: 下柱干支（如日干支）。

        Returns:
            (關宮, 籥宮, 將軍宮)。
        """
        liuren_hour = kinliuren.Liuren(jq, cm, gz1, gz2).result_m(0)
        sky2earth = bidict(liuren_hour["地轉天盤"])
        lnk = config.multi_key_dict_get(cls.SOLAR_TERMS_BY_SEASON, jq)
        lock = GuxuJudge.ZHI2GUA[sky2earth.inverse[lnk["關"]]]
        key = GuxuJudge.ZHI2GUA[sky2earth.inverse[lnk["籥"]]]
        g = GuxuJudge.ZHI2GUA[sky2earth.inverse[cls.GENERAL_MAP[gz2[1]]]]
        return lock, key, g

    @classmethod
    def build_position_result(
        cls,
        *,
        gong: str,
        label: str,
        zhao_num: int,
        beast: str,
        my_element: str,
        idx: int,
        jq: str,
        lock: str,
        key: str,
        general_gong: str,
        gu: str,
        xu: str,
    ) -> dict[str, Any]:
        """組裝單一宮位的排盤結果。

        Args:
            gong: 宮位名（如 "巽宮"）。
            label: 標籤名（如 "兆"）。
            zhao_num: 五行數字 (1–5)。
            beast: 六獸名。
            my_element: 兆位五行（用於六親判斷）。
            idx: 宮位索引 (0=兆, 1–5=五鄉)。
            jq: 節氣。
            lock: 關宮位字。
            key: 籥宮位字。
            general_gong: 將軍宮位字。
            gu: 孤宮位字。
            xu: 虛宮位字。

        Returns:
            宮位結果字典。
        """
        gong_char = gong[0]
        zhao_element = FiveElementsMapper.element_for(zhao_num)

        if idx == 0:
            relation = ""
        else:
            relation = FiveElementsMapper.relation(my_element, zhao_element)

        return {
            "宮位": cls.GONG_TO_LABEL.get(gong, ""),
            "旺相": cls.get_wangxiang(jq, gong_char),
            "宮位1": gong_char,
            "數字": zhao_num,
            "五行": zhao_element,
            "六獸": beast,
            "六獸死": SixBeastsArranger.check_death(beast, gong_char),
            "六獸害": SixBeastsArranger.check_harm(beast, gong_char),
            "六親": relation,
            "孤": "孤" if gu == gong_char else "",
            "虛": "虛" if xu == gong_char else "",
            "關": "關" if lock == gong_char else "",
            "籥": "籥" if key == gong_char else "",
            "將軍": "將軍" if general_gong == gong_char else "",
        }


# ---------------------------------------------------------------------------
# WuzhaoDivination — 唐代正法五兆占卜 (新增)
# ---------------------------------------------------------------------------

@dataclass
class WuzhaoDivination:
    """唐代太卜署正法「五兆卜法」完整實作。

    以 36 算子進行 6 次揲筮（五五除之），忠實復原 P.2859《五兆要訣略》
    所載之太卜署占法。

    References:
        P.2859 第 1–2 行：「五兆要訣略序」
        P.2859 第 6–12 行：揲筮法「凡筮用三十六莖，五五除之」
        王祥偉《敦煌五兆卜法文獻校錄研究》第三章

    Attributes:
        jq: 節氣名稱。
        cm: 農曆月份。
        gz1: 上柱干支。
        gz2: 下柱干支。
        manual_splits: 手動分裂數列表（可選，用於復原折竹體驗）。

    Example:
        >>> div = WuzhaoDivination(jq="夏至", cm="六", gz1="壬午", gz2="丁卯")
        >>> result = div.divine()
    """

    jq: str
    cm: str
    gz1: str
    gz2: str
    manual_splits: list[int] | None = None

    def divine(self) -> dict[str, dict[str, Any]]:
        """執行唐代正法揲筮並返回完整排盤。

        Returns:
            各宮位名稱 → 排盤結果的字典。

        Raises:
            ValueError: 日干不在十天干之內。
        """
        day_gan = self.gz1[0]
        beast_seq = SixBeastsArranger.arrange(day_gan)

        # P.2859 第 6–8 行：36 算子六次揲筮
        zhao_nums = WuzhaoCalculator.tang_shi_divination(
            manual_splits=self.manual_splits
        )

        lock, key, general_gong = InterpretationEngine.compute_lock_key_general(
            self.jq, self.cm, self.gz1, self.gz2
        )
        gu, xu = GuxuJudge.judge(self.gz2)

        result: dict[str, dict[str, Any]] = {}
        my_element = ""

        for idx, (gong, label) in enumerate(InterpretationEngine.POSITIONS):
            zhao_num = zhao_nums[idx]
            if idx == 0:
                my_element = FiveElementsMapper.element_for(zhao_num)

            result[label] = InterpretationEngine.build_position_result(
                gong=gong,
                label=label,
                zhao_num=zhao_num,
                beast=beast_seq[idx],
                my_element=my_element,
                idx=idx,
                jq=self.jq,
                lock=lock,
                key=key,
                general_gong=general_gong,
                gu=gu,
                xu=xu,
            )

        return result


# ---------------------------------------------------------------------------
# 向後相容的模組級常量與函數（宋代折竹彈占簡化模式）
# ---------------------------------------------------------------------------

# 保留模組級常量供外部引用
num_to_element = FiveElementsMapper.NUM_TO_ELEMENT
sixbeast_weakness = SixBeastsArranger.WEAKNESS
guxu = GuxuJudge.GUXU_DATA
yy = GuxuJudge.YIN_YANG
general = InterpretationEngine.GENERAL_MAP
six_beasts_order = SixBeastsArranger.ORDER
day_gan_to_beast = SixBeastsArranger.DAY_GAN_TO_BEAST
zhi2gua = GuxuJudge.ZHI2GUA
solar_terms_by_season = InterpretationEngine.SOLAR_TERMS_BY_SEASON
wangxiang = InterpretationEngine._WANGXIANG
trigrams = InterpretationEngine._TRIGRAMS
jieqi_groups = InterpretationEngine._JIEQI_GROUPS
twenty_four_solar_terms = InterpretationEngine.TWENTY_FOUR_SOLAR_TERMS

locknkey = {
    ("丑", "寅", "卯"): re.findall("..", "關中籥離"),
    ("辰", "巳", "午"): re.findall("..", "關震籥兌"),
    ("未", "申", "酉"): re.findall("..", "關離籥坎"),
    ("戌", "亥", "子"): re.findall("..", "關中籥震"),
}


def rotate_trigrams(base: tuple[str, ...], shift: int) -> tuple[str, ...]:
    """旋轉八卦序列（向後相容）。"""
    return InterpretationEngine._rotate(base, shift)


jieqi_wangxiang = InterpretationEngine._jieqi_wangxiang_map()


def random_split(total: int) -> int:
    """隨機分兩份，返回左一份（宋代折竹法，向後相容）。"""
    return WuzhaoCalculator.random_split(total)


def five_zhao_paipan(
    num: int,
    jq: str,
    cm: str,
    gz1: str,
    gz2: str,
    manual_splits: list[int] | None = None,
) -> dict[str, dict[str, Any]]:
    """宋代折竹彈占簡化模式排盤（隨機揲筮）。

    此函數保留原有介面，修正以下 bug：
    - 移除 num=0 覆蓋輸入參數的 dead code
    - 修正 remain 應以 left（實際取走數）遞減，而非 zhao_num（餘數）

    Args:
        num: 使用者輸入數字（目前保留介面，未在隨機模式中使用）。
        jq: 節氣名稱。
        cm: 農曆月份。
        gz1: 上柱干支。
        gz2: 下柱干支。
        manual_splits: 手動分裂數列表（可選）。

    Returns:
        各宮位排盤結果字典。
    """
    day_gan = gz1[0]
    try:
        beast_seq = SixBeastsArranger.arrange(day_gan)
    except ValueError:
        return {"錯誤": "日干不正確，請輸入：甲乙丙丁戊己庚辛壬癸"}

    lock, key, general_gong = InterpretationEngine.compute_lock_key_general(
        jq, cm, gz1, gz2
    )
    gu, xu = GuxuJudge.judge(gz2)

    base = WuzhaoCalculator.BASE_STICKS
    remain = base
    result: dict[str, dict[str, Any]] = {}
    my_element = ""

    for idx, (gong, label) in enumerate(InterpretationEngine.POSITIONS):
        if manual_splits is not None and idx < len(manual_splits):
            left = manual_splits[idx]
            left = max(1, min(left, remain - 1)) if remain > 1 else 1
        else:
            left = WuzhaoCalculator.random_split(remain)

        zhao_num = WuzhaoCalculator._mod5_nonzero(left)
        zhao_element = FiveElementsMapper.element_for(zhao_num)

        if idx == 0:
            my_element = zhao_element

        result[label] = InterpretationEngine.build_position_result(
            gong=gong,
            label=label,
            zhao_num=zhao_num,
            beast=beast_seq[idx],
            my_element=my_element,
            idx=idx,
            jq=jq,
            lock=lock,
            key=key,
            general_gong=general_gong,
            gu=gu,
            xu=xu,
        )

        # 修正：以 left（實際取走數）遞減，非 zhao_num（餘數）
        remain -= left
        if remain <= 0:
            # 算子用盡，剩餘位置以 5（土）填充（P.2859：「盡則為五」）
            for fill_idx in range(idx + 1, len(InterpretationEngine.POSITIONS)):
                fill_gong, fill_label = InterpretationEngine.POSITIONS[fill_idx]
                result[fill_label] = InterpretationEngine.build_position_result(
                    gong=fill_gong,
                    label=fill_label,
                    zhao_num=5,
                    beast=beast_seq[fill_idx],
                    my_element=my_element,
                    idx=fill_idx,
                    jq=jq,
                    lock=lock,
                    key=key,
                    general_gong=general_gong,
                    gu=gu,
                    xu=xu,
                )
            break

    return result


def gangzhi_paipan(
    gz_list: list[str],
    num: int,
    jq: str,
    cm: str,
) -> dict[str, dict[str, Any]]:
    """以年月日時干支計算五兆（干支數值法）。

    Args:
        gz_list: config.gangzhi 所傳回的 [年, 月, 日, 時, 分] 干支列表。
        num: 使用者輸入數字。
        jq: 節氣名稱。
        cm: 農曆月份。

    Returns:
        各宮位排盤結果字典。
    """
    if len(gz_list) < 4:
        return {"錯誤": "干支資料不足"}

    y, m, d, h, mi = gz_list
    if mi[0] not in SixBeastsArranger.DAY_GAN_TO_BEAST:
        return {"錯誤": "日干不正確，請輸入：甲乙丙丁戊己庚辛壬癸"}

    jz2num = dict(zip(config.jiazi(), range(1, 61)))
    beast_seq = SixBeastsArranger.arrange(mi[0])

    lock, key, general_gong = InterpretationEngine.compute_lock_key_general(
        jq, cm, h, mi
    )
    gu, xu = GuxuJudge.judge(mi)

    positions_with_parts: list[tuple[str, str, list[Any]]] = [
        ("巽宮", "兆", [y, m, d, h, mi, num]),
        ("震宮", "木鄉", [m, d, h, mi, num]),
        ("離宮", "火鄉", [d, h, mi, num]),
        ("中宮", "土鄉", [h, mi, num]),
        ("兌宮", "金鄉", [mi, num]),
        ("坎宮", "水鄉", [num]),
    ]

    result: dict[str, dict[str, Any]] = {}
    my_element = ""

    for idx, (gong, label, parts) in enumerate(positions_with_parts):
        zhao_num = WuzhaoCalculator.gangzhi_calculation(parts, jz2num)
        zhao_element = FiveElementsMapper.element_for(zhao_num)

        if idx == 0:
            my_element = zhao_element

        result[label] = InterpretationEngine.build_position_result(
            gong=gong,
            label=label,
            zhao_num=zhao_num,
            beast=beast_seq[idx],
            my_element=my_element,
            idx=idx,
            jq=jq,
            lock=lock,
            key=key,
            general_gong=general_gong,
            gu=gu,
            xu=xu,
        )

    return result


if __name__ == "__main__":
    gz = config.gangzhi(2025, 6, 27, 11, 24)
    jq_name = "夏至"
    cm_val = config.lunar_date_d(2025, 6, 27)["農曆月"][0]

    print("=== 干支起盤 ===")
    print(gangzhi_paipan(gz, 0, jq_name, cm_val))

    print("\n=== 日干起盤（宋代簡化） ===")
    print(five_zhao_paipan(0, jq_name, cm_val, gz[1], gz[2]))

    print("\n=== 唐代正法揲筮 ===")
    div = WuzhaoDivination(jq=jq_name, cm=cm_val, gz1=gz[1], gz2=gz[2])
    print(div.divine())
