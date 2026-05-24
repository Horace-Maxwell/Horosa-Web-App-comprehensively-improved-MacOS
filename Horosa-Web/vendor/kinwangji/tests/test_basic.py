"""Basic tests for the kinwangji package."""

import pytest
from kinwangji import wanji_four_gua, jq, gangzhi, jiazi
from kinwangji.wanji import wangji_gua, wangji_gua2


def test_jiazi_length():
    """The sexagenary cycle should contain exactly 60 entries."""
    assert len(jiazi()) == 60


def test_jiazi_first_last():
    """First entry is 甲子, last is 癸亥."""
    cycle = jiazi()
    assert cycle[0] == "甲子"
    assert cycle[-1] == "癸亥"


def test_gangzhi_returns_five_elements():
    """gangzhi should return a list of 5 elements (year, month, day, hour, minute)."""
    result = gangzhi(2025, 6, 15, 10, 30)
    assert isinstance(result, list)
    assert len(result) == 5


def test_jq_returns_string():
    """jq should return the name of a solar term as a string."""
    result = jq(2025, 6, 15, 10, 30)
    assert isinstance(result, str)
    assert len(result) == 2  # Chinese solar term names are 2 characters


def test_wanji_four_gua_keys():
    """wanji_four_gua should return a dict with expected keys."""
    result = wanji_four_gua(2025, 6, 15, 10, 30)
    assert isinstance(result, dict)
    expected_keys = {"日期", "干支", "會", "運", "世", "運卦動爻", "世卦動爻", "旬卦動爻",
                     "正卦", "運卦", "世卦", "旬卦", "年卦", "月卦", "日卦", "時卦", "分卦"}
    assert set(result.keys()) == expected_keys


# ---------------------------------------------------------------------------
# Tests for the I Ching Unicode hexagram mapping used in app.py
# ---------------------------------------------------------------------------

# King Wen sequence: maps hexagram name → Unicode symbol (U+4DC0–U+4DFF)
_GUA_UNICODE = {
    "乾": "䷀", "坤": "䷁", "屯": "䷂", "蒙": "䷃", "需": "䷄",
    "訟": "䷅", "師": "䷆", "比": "䷇", "小畜": "䷈", "履": "䷉",
    "泰": "䷊", "否": "䷋", "同人": "䷌", "大有": "䷍", "謙": "䷎",
    "豫": "䷏", "隨": "䷐", "蠱": "䷑", "臨": "䷒", "觀": "䷓",
    "噬嗑": "䷔", "賁": "䷕", "剝": "䷖", "復": "䷗", "無妄": "䷘",
    "大畜": "䷙", "頤": "䷚", "大過": "䷛", "坎": "䷜", "離": "䷝",
    "咸": "䷞", "恆": "䷟", "遯": "䷠", "大壯": "䷡", "晉": "䷢",
    "明夷": "䷣", "家人": "䷤", "睽": "䷥", "蹇": "䷦", "解": "䷧",
    "損": "䷨", "益": "䷩", "夬": "䷪", "姤": "䷫", "萃": "䷬",
    "升": "䷭", "困": "䷮", "井": "䷯", "革": "䷰", "鼎": "䷱",
    "震": "䷲", "艮": "䷳", "漸": "䷴", "歸妹": "䷵", "豐": "䷶",
    "旅": "䷷", "巽": "䷸", "兌": "䷹", "渙": "䷺", "節": "䷻",
    "中孚": "䷼", "小過": "䷽", "既濟": "䷾", "未濟": "䷿",
}


def test_gua_unicode_covers_all_64():
    """The Unicode hexagram mapping should contain exactly 64 entries."""
    assert len(_GUA_UNICODE) == 64


def test_gua_unicode_symbols_in_correct_range():
    """All Unicode symbols should be in the I Ching Hexagram block U+4DC0–U+4DFF."""
    for name, symbol in _GUA_UNICODE.items():
        code = ord(symbol)
        assert 0x4DC0 <= code <= 0x4DFF, (
            f"Symbol for {name} (U+{code:04X}) is outside the hexagram block"
        )


def test_gua_unicode_covers_wangji_gua2():
    """Every hexagram name in the 64-gua cycle should have a Unicode symbol."""
    for idx, name in wangji_gua2.items():
        assert name in _GUA_UNICODE, f"Missing Unicode symbol for {name} (index {idx})"


def test_gua_unicode_covers_wangji_gua():
    """Every hexagram name in the 60-gua cycle should have a Unicode symbol."""
    for idx, name in wangji_gua.items():
        assert name in _GUA_UNICODE, f"Missing Unicode symbol for {name} (index {idx})"


def test_gua_unicode_unique_symbols():
    """Each hexagram name should map to a unique Unicode symbol."""
    symbols = list(_GUA_UNICODE.values())
    assert len(symbols) == len(set(symbols)), "Duplicate Unicode symbols found"


def test_gua_unicode_spot_check():
    """Spot-check well-known hexagram-to-symbol mappings."""
    assert _GUA_UNICODE["乾"] == "\u4DC0"  # ䷀ Qian (Heaven)
    assert _GUA_UNICODE["坤"] == "\u4DC1"  # ䷁ Kun (Earth)
    assert _GUA_UNICODE["屯"] == "\u4DC2"  # ䷂ Zhun (Difficulty at the Beginning)
    assert _GUA_UNICODE["既濟"] == "\u4DFE"  # ䷾ Ji Ji (After Completion)
    assert _GUA_UNICODE["未濟"] == "\u4DFF"  # ䷿ Wei Ji (Before Completion)


def test_wanji_four_gua_hexagrams_in_unicode_map():
    """All hexagram values returned by wanji_four_gua should be in the mapping."""
    result = wanji_four_gua(2025, 6, 15, 10, 30)
    gua_keys = ["正卦", "運卦", "世卦", "旬卦", "年卦", "月卦", "日卦", "時卦", "分卦"]
    for key in gua_keys:
        name = result[key]
        assert name in _GUA_UNICODE, f"Hexagram '{name}' ({key}) not in Unicode map"
