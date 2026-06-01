# -*- coding: utf-8 -*-
"""
心易發微 (Xinyi Fawei) divination methods.

Implements the practical hexagram-raising (起卦) methods described in the
*Huangji Jingshi Xinyi Fawei* (皇極經世心易發微) by Yang Xiangjun (楊向春).

These methods form the basis of what later became known as Meihua Yishu
(梅花易數) — the Plum Blossom Numerology system.  Each method derives a
hexagram (卦) from a stimulus and returns the original hexagram (本卦),
changed hexagram (變卦), moving line position (動爻), and body/use
analysis (體用).

Supported methods
-----------------
- :func:`number_qigua` — 先天數起卦: two arbitrary numbers → hexagram
- :func:`datetime_qigua` — 年月日時起卦: date-time → hexagram
- :func:`direction_qigua` — 後天方位起卦: object + direction + hour
- :func:`character_qigua` — 字數起卦: character stroke counts → hexagram

References
----------
- ``examples/皇极经世心易发微.txt``, lines 179–235 (先天/後天體用起例,
  為人占例, 自己占例, 動物占例, 靜物占例)
- Shao Yong 邵雍, *Huangji Jingshi* 皇極經世

@author: kinwangji
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .jieqi import di_zhi, lunar_date_d, multi_key_dict_get
from .wanji import change, sixtyfourgua

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Trigram line codes (bottom-to-top, 7 = yang, 8 = yin).
TRIGRAM_CODE: Dict[str, str] = {
    "乾": "777",
    "兌": "778",
    "離": "787",
    "震": "788",
    "巽": "877",
    "坎": "878",
    "艮": "887",
    "坤": "888",
}

#: Inverse lookup: trigram code → name.
_CODE_TO_TRIGRAM: Dict[str, str] = {v: k for k, v in TRIGRAM_CODE.items()}

#: Pre-Heaven trigram numbers (先天八卦數): 乾1 兌2 離3 震4 巽5 坎6 艮7 坤8.
XIANTIAN_NUM: Dict[int, str] = {
    1: "乾", 2: "兌", 3: "離", 4: "震",
    5: "巽", 6: "坎", 7: "艮", 8: "坤",
}

#: Post-Heaven trigram numbers (後天八卦數):
#: 坎1 坤2 震3 巽4 中5寄坤 乾6 兌7 艮8 離9 十寄艮.
HOUTIAN_NUM: Dict[int, str] = {
    1: "坎", 2: "坤", 3: "震", 4: "巽", 5: "坤",
    6: "乾", 7: "兌", 8: "艮", 9: "離", 10: "艮",
}

#: Post-Heaven direction → trigram mapping (後天方位).
DIRECTION_GUA: Dict[str, str] = {
    "北": "坎", "西南": "坤", "東": "震", "東南": "巽",
    "南": "離", "中": "坤", "西北": "乾", "西": "兌", "東北": "艮",
}

#: Trigram → Five-Element mapping (五行).
GUA_WUXING: Dict[str, str] = {
    "乾": "金", "兌": "金",
    "離": "火",
    "震": "木", "巽": "木",
    "坎": "水",
    "艮": "土", "坤": "土",
}

#: Five-Element producing/overcoming relationships.
_WUXING_SHENG: Dict[str, str] = {
    "金": "水", "水": "木", "木": "火", "火": "土", "土": "金",
}
_WUXING_KE: Dict[str, str] = {
    "金": "木", "木": "土", "土": "水", "水": "火", "火": "金",
}

#: Map modern hour (0–23) to 時辰 number (子=1 … 亥=12).
_HOUR_TO_SHICHEN: Dict[int, int] = {
    23: 1, 0: 1,
    1: 2, 2: 2,
    3: 3, 4: 3,
    5: 4, 6: 4,
    7: 5, 8: 5,
    9: 6, 10: 6,
    11: 7, 12: 7,
    13: 8, 14: 8,
    15: 9, 16: 9,
    17: 10, 18: 10,
    19: 11, 20: 11,
    21: 12, 22: 12,
}

#: Earthly-branch index (used for year/month/day → number conversion).
_DIZHI_NUM: Dict[str, int] = {ch: i + 1 for i, ch in enumerate(di_zhi)}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _num_to_trigram(n: int, system: str = "xiantian") -> str:
    """Convert a number to a trigram name.

    For Pre-Heaven (先天): divide by 8, remainder maps to trigram.
    For Post-Heaven (後天): divide by 8 (or 10 if raw), remainder maps to trigram.

    The text says: "如數過八者，以八除之，用零作卦也" — if number exceeds 8,
    divide by 8, use remainder as trigram.  Remainder 0 maps to 8 (坤 in
    Pre-Heaven, 艮 in Post-Heaven).

    Args:
        n: Positive integer.
        system: ``"xiantian"`` (Pre-Heaven) or ``"houtian"`` (Post-Heaven).

    Returns:
        Trigram name, e.g. ``"乾"``

    Raises:
        ValueError: If *n* < 1 or *system* is invalid.
    """
    if n < 1:
        raise ValueError(f"Number must be ≥ 1, got {n}")
    if system == "xiantian":
        r = n % 8
        if r == 0:
            r = 8
        return XIANTIAN_NUM[r]
    elif system == "houtian":
        r = n % 8
        if r == 0:
            r = 8
        return HOUTIAN_NUM[r]
    else:
        raise ValueError(f"Unknown system: {system!r}")


def _moving_line(total: int) -> int:
    """Determine the moving line position (動爻, 1–6) from a total number.

    The text says: "如數不滿六，即零為動爻；如數過六，以六除之，用零作動爻"
    — divide by 6, use remainder; remainder 0 maps to 6.

    Args:
        total: Positive integer.

    Returns:
        Moving line position (1–6).
    """
    r = total % 6
    return r if r != 0 else 6


def _trigram_at(hexagram_code: str, position: str) -> str:
    """Extract a trigram name from a 6-line hexagram code.

    Args:
        hexagram_code: Six-character code (``'7'``/``'8'`` only).
        position: ``"lower"`` (lines 1–3) or ``"upper"`` (lines 4–6).

    Returns:
        Trigram name, e.g. ``"乾"``.
    """
    norm = hexagram_code.replace("9", "7").replace("6", "8")
    if position == "lower":
        return _CODE_TO_TRIGRAM[norm[:3]]
    return _CODE_TO_TRIGRAM[norm[3:]]


def _hu_gua(hexagram_code: str) -> str:
    """Derive the interlocking hexagram (互卦) from a hexagram code.

    The 互卦 is formed by taking lines 2-3-4 as the lower trigram and
    lines 3-4-5 as the upper trigram.

    Args:
        hexagram_code: Six-character normalized code.

    Returns:
        Hexagram name of the 互卦.
    """
    norm = hexagram_code.replace("9", "7").replace("6", "8")
    # Lines are indexed 0–5 (bottom to top)
    lower_hu = norm[1] + norm[2] + norm[3]  # lines 2, 3, 4
    upper_hu = norm[2] + norm[3] + norm[4]  # lines 3, 4, 5
    hu_code = lower_hu + upper_hu
    return multi_key_dict_get(sixtyfourgua, hu_code)


def _build_result(
    upper_trigram: str,
    lower_trigram: str,
    moving_line: int,
) -> Dict[str, Any]:
    """Build the full divination result from upper/lower trigrams and moving line.

    Args:
        upper_trigram: Name of the upper (outer) trigram.
        lower_trigram: Name of the lower (inner) trigram.
        moving_line: Moving line position (1–6).

    Returns:
        Dict with keys:
        - ``本卦``: original hexagram name
        - ``變卦``: changed hexagram name (after moving line toggles)
        - ``動爻``: moving line position (1–6)
        - ``上卦``: upper trigram name
        - ``下卦``: lower trigram name
        - ``體卦``: body trigram name (the *static* trigram)
        - ``用卦``: use trigram name (the trigram with the moving line)
        - ``互卦``: interlocking hexagram name
        - ``體用五行``: five-element relationship analysis
    """
    lower_code = TRIGRAM_CODE[lower_trigram]
    upper_code = TRIGRAM_CODE[upper_trigram]
    hex_code = lower_code + upper_code

    ben_gua = multi_key_dict_get(sixtyfourgua, hex_code)
    bian_code = change(hex_code, moving_line)
    bian_gua = multi_key_dict_get(sixtyfourgua, bian_code)
    hu_gua = _hu_gua(hex_code)

    # Body (體) is the *static* trigram; Use (用) is the one with the moving line.
    # Lines 1–3 = lower, lines 4–6 = upper.
    if moving_line <= 3:
        ti_gua = upper_trigram
        yong_gua = lower_trigram
    else:
        ti_gua = lower_trigram
        yong_gua = upper_trigram

    ti_wx = GUA_WUXING[ti_gua]
    yong_wx = GUA_WUXING[yong_gua]

    if ti_wx == yong_wx:
        wx_relation = "比和"
    elif _WUXING_SHENG.get(yong_wx) == ti_wx:
        wx_relation = "用生體"
    elif _WUXING_SHENG.get(ti_wx) == yong_wx:
        wx_relation = "體生用"
    elif _WUXING_KE.get(yong_wx) == ti_wx:
        wx_relation = "用克體"
    elif _WUXING_KE.get(ti_wx) == yong_wx:
        wx_relation = "體克用"
    else:
        wx_relation = ""

    return {
        "本卦": ben_gua,
        "變卦": bian_gua,
        "動爻": moving_line,
        "上卦": upper_trigram,
        "下卦": lower_trigram,
        "體卦": ti_gua,
        "用卦": yong_gua,
        "互卦": hu_gua,
        "體用五行": f"體{ti_gua}({ti_wx}) {wx_relation} 用{yong_gua}({yong_wx})",
    }


# ---------------------------------------------------------------------------
# Public API: divination methods (起卦法)
# ---------------------------------------------------------------------------


def number_qigua(upper_num: int, lower_num: int) -> Dict[str, Any]:
    """先天數起卦 — Pre-Heaven number method.

    Derives a hexagram from two numbers using the Pre-Heaven (先天) trigram
    sequence.  This is the fundamental method described in the *Xinyi Fawei*
    (先天體用起例).

    The text says: "先天者，伏羲所畫之卦也。其數乾一、兌二、離三、震四、
    巽五、坎六、艮七、坤八。故起例只依此作卦，如數過八者，以八除之，
    用零作卦也。動爻者，合總數而算之。"

    Rules:
    - Upper trigram: ``upper_num mod 8`` → Pre-Heaven trigram
    - Lower trigram: ``lower_num mod 8`` → Pre-Heaven trigram
    - Moving line: ``(upper_num + lower_num) mod 6``

    Args:
        upper_num: Positive integer for the upper (outer) trigram.
        lower_num: Positive integer for the lower (inner) trigram.

    Returns:
        Divination result dict (see :func:`_build_result`).

    Raises:
        ValueError: If either number is < 1.

    Examples:
        >>> r = number_qigua(5, 10)
        >>> r["本卦"]
        '中孚'
    """
    if upper_num < 1 or lower_num < 1:
        raise ValueError(
            f"Numbers must be ≥ 1, got upper={upper_num}, lower={lower_num}"
        )
    upper = _num_to_trigram(upper_num, "xiantian")
    lower = _num_to_trigram(lower_num, "xiantian")
    yao = _moving_line(upper_num + lower_num)
    return _build_result(upper, lower, yao)


def datetime_qigua(
    year: int,
    month: int,
    day: int,
    hour: int,
) -> Dict[str, Any]:
    """年月日時起卦 — Date-time method.

    Derives a hexagram from a date and time, using the Pre-Heaven trigram
    number system.  This is described in the *Xinyi Fawei* under 為人占例:

    "年月日時者，當著力共算為上卦，加時總算為下卦，合上下也；
    除六取零，即知動爻也。"

    The year is represented by its Earthly Branch number (子=1 … 亥=12),
    month and day are the *lunar* month and day numbers, and hour is
    converted to the traditional 時辰 number (子時=1 … 亥時=12).

    Rules:
    - Upper trigram: ``(year_branch + lunar_month + lunar_day) mod 8``
    - Lower trigram: ``(year_branch + lunar_month + lunar_day + shichen) mod 8``
    - Moving line: ``(year_branch + lunar_month + lunar_day + shichen) mod 6``

    Args:
        year: Solar (Gregorian) calendar year.
        month: Solar month (1–12).
        day: Solar day of month.
        hour: Hour of day (0–23).

    Returns:
        Divination result dict (see :func:`_build_result`).

    Examples:
        >>> r = datetime_qigua(2025, 6, 15, 10)
        >>> r["本卦"]  # doctest: +SKIP
        '...'
    """
    # Convert to lunar date
    lunar = lunar_date_d(year, month, day)
    lunar_month = lunar.get("月")
    lunar_day = lunar.get("日")

    # Year branch number: use the Earthly Branch of the lunar year
    # The branch is the second character of the year's stems-branches.
    # For simplicity, compute from (lunar_year - 4) % 12 to get branch index.
    lunar_year = lunar.get("年")
    # Earthly branch index: 子=0, 丑=1, ..., 亥=11 in the cycle
    # Branch number for divination: 子=1, 丑=2, ..., 亥=12
    year_branch = (lunar_year - 4) % 12 + 1  # +1 for 1-based

    # Convert modern hour to 時辰 number
    shichen = _HOUR_TO_SHICHEN[hour]

    upper_sum = year_branch + lunar_month + lunar_day
    lower_sum = upper_sum + shichen

    upper = _num_to_trigram(upper_sum, "xiantian")
    lower = _num_to_trigram(lower_sum, "xiantian")
    yao = _moving_line(lower_sum)
    return _build_result(upper, lower, yao)


def direction_qigua(
    object_gua: str,
    direction: str,
    hour: int,
) -> Dict[str, Any]:
    """後天方位起卦 — Post-Heaven direction method.

    Derives a hexagram from an observed object's trigram type and its
    compass direction, combined with the current hour.  Described in the
    *Xinyi Fawei* under 後天體用起例:

    "後天者，文王所定之方位也。以物來為上卦，方位為下卦，
    加時合總，除六數而取動爻。"

    Rules:
    - Upper trigram: object's trigram (from the 8 trigrams)
    - Lower trigram: direction's trigram (from Post-Heaven 方位)
    - Moving line: ``(object_number + direction_number + shichen) mod 6``

    For the object, use one of the 8 trigram names directly:
    乾 (heaven/metal/horse), 兌 (lake/damage), 離 (fire/pheasant),
    震 (thunder/dragon), 巽 (wind/chicken), 坎 (water/pig),
    艮 (mountain/dog), 坤 (earth/ox).

    For direction, use: 北/東北/東/東南/南/西南/西/西北/中.

    Args:
        object_gua: Trigram name for the object (one of 8 trigram names).
        direction: Compass direction in Chinese.
        hour: Hour of day (0–23).

    Returns:
        Divination result dict (see :func:`_build_result`).

    Raises:
        ValueError: If *object_gua* is not a valid trigram or *direction* is
            not recognized.

    Examples:
        >>> r = direction_qigua("離", "南", 14)
        >>> r["本卦"]
        '離'
    """
    if object_gua not in TRIGRAM_CODE:
        raise ValueError(
            f"Invalid trigram name: {object_gua!r}. "
            f"Must be one of {list(TRIGRAM_CODE.keys())}"
        )
    if direction not in DIRECTION_GUA:
        raise ValueError(
            f"Invalid direction: {direction!r}. "
            f"Must be one of {list(DIRECTION_GUA.keys())}"
        )

    upper = object_gua
    lower_name = DIRECTION_GUA[direction]

    # Post-Heaven primary numbers (excluding 5寄坤 and 10寄艮 aliases)
    _houtian_primary = {
        "坎": 1, "坤": 2, "震": 3, "巽": 4,
        "乾": 6, "兌": 7, "艮": 8, "離": 9,
    }
    obj_num = _houtian_primary.get(upper, 1)
    dir_num = _houtian_primary.get(lower_name, 1)
    shichen = _HOUR_TO_SHICHEN[hour]

    yao = _moving_line(obj_num + dir_num + shichen)
    return _build_result(upper, lower_name, yao)


def character_qigua(
    upper_strokes: int,
    lower_strokes: int,
) -> Dict[str, Any]:
    """字數起卦 — Character stroke-count method.

    Derives a hexagram from the stroke counts of Chinese characters.
    Described in the *Xinyi Fawei* under 為人占例 (書字):

    "如字有間斷者，以上截為上卦，下截為下卦；如字有偏旁者，
    以左旁為上卦，右旁為下卦。"

    And for two characters: "以上字筆數為上卦，下字筆數為下卦。"

    Rules:
    - Upper trigram: ``upper_strokes mod 8`` → Pre-Heaven trigram
    - Lower trigram: ``lower_strokes mod 8`` → Pre-Heaven trigram
    - Moving line: ``(upper_strokes + lower_strokes) mod 6``

    The caller is responsible for computing the stroke counts. For a
    single character, split its strokes between upper/lower or left/right
    structural components.

    Args:
        upper_strokes: Stroke count for the upper/left component.
        lower_strokes: Stroke count for the lower/right component.

    Returns:
        Divination result dict (see :func:`_build_result`).

    Raises:
        ValueError: If either stroke count is < 1.

    Examples:
        >>> r = character_qigua(5, 8)
        >>> r["上卦"]
        '巽'
        >>> r["下卦"]
        '坤'
    """
    return number_qigua(upper_strokes, lower_strokes)
