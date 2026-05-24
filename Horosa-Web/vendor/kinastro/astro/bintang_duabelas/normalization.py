"""
astro/bintang_duabelas/normalization.py
======================================

Bintang Duabelas 姓名正規化工具。

此模組負責：
1. 偵測輸入是阿拉伯文 / Jawi / 羅馬拼音。
2. 將常見阿拉伯字形統一為 Abjad 可計算形式。
3. 以保守的馬來羅馬拼音規則轉寫為 Jawi/Arabic 字母。

注意：羅馬拼音轉寫僅作為進入傳統規則系統的橋接層，
不會改動任何原始 Abjad / Hisab 規則本身。
"""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

_SCRIPT_ARABIC = "arabic"
_SCRIPT_ROMAN = "roman"
_SCRIPT_EMPTY = "empty"
_SCRIPT_MIXED = "mixed"

_ARABIC_LETTER_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")
_LATIN_LETTER_RE = re.compile(r"[A-Za-z]")

_COMMON_ROMAN_OVERRIDES: dict[str, str] = {
    "ahmad": "احمد",
    "ahmed": "احمد",
    "ali": "علي",
    "aminah": "امينه",
    "aishah": "عايشه",
    "fatimah": "فاطمه",
    "fatimahh": "فاطمه",
    "hasan": "حسن",
    "husain": "حسين",
    "hussein": "حسين",
    "ismail": "اسماعيل",
    "khadijah": "خديجه",
    "muhammad": "محمد",
    "mohamed": "محمد",
    "mustafa": "مصطفى",
    "othman": "عثمان",
    "othmann": "عثمان",
    "umar": "عمر",
    "uthman": "عثمان",
    "yusuf": "يوسف",
}

# 先處理長字母群，避免較短規則提前截斷。
_ROMAN_MULTI_MAP: tuple[tuple[str, str], ...] = (
    ("sch", "ش"),
    ("sy", "ش"),
    ("sh", "ش"),
    ("kh", "خ"),
    ("gh", "غ"),
    ("ng", "ڠ"),
    ("ny", "ڽ"),
    ("ch", "چ"),
    ("ph", "ف"),
    ("th", "ث"),
    ("dh", "ذ"),
    ("dz", "ذ"),
    ("zh", "ظ"),
    ("aa", "ا"),
    ("ii", "ي"),
    ("uu", "و"),
    ("oo", "و"),
)

_ROMAN_SINGLE_MAP: dict[str, str] = {
    "a": "ا",
    "b": "ب",
    "c": "ك",
    "d": "د",
    "e": "",
    "f": "ف",
    "g": "ݢ",
    "h": "ه",
    "i": "ي",
    "j": "ج",
    "k": "ك",
    "l": "ل",
    "m": "م",
    "n": "ن",
    "o": "و",
    "p": "ڤ",
    "q": "ق",
    "r": "ر",
    "s": "س",
    "t": "ت",
    "u": "و",
    "v": "ف",
    "w": "و",
    "x": "كس",
    "y": "ي",
    "z": "ز",
}

# 將多種字形收斂至 Abjad 計算需要的基本形。
_ARABIC_NORMALIZATION_MAP: dict[str, str] = {
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",
    "ٱ": "ا",
    "ؤ": "و",
    "ئ": "ي",
    "ى": "ي",
    "ة": "ه",
    "ک": "ك",
    "ی": "ي",
    "ھ": "ه",
    "ﻻ": "لا",
    "ﻷ": "لا",
    "ﻹ": "لا",
    "ﻵ": "لا",
}

_IGNORED_CHARACTERS: set[str] = {
    "'",
    '"',
    "`",
    "’",
    "-",
    "_",
    ".",
    ",",
    ";",
    ":",
    "!",
    "?",
    "/",
    "\\",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    "|",
}


@dataclass(frozen=True)
class NameNormalization:
    """姓名正規化結果。"""

    original: str
    normalized: str
    detected_script: str
    method: str
    used_override: bool = False

def detect_name_script(name: str) -> str:
    """偵測姓名腳本類型。"""
    if not name or not name.strip():
        return _SCRIPT_EMPTY

    has_arabic = bool(_ARABIC_LETTER_RE.search(name))
    has_latin = bool(_LATIN_LETTER_RE.search(name))

    if has_arabic and has_latin:
        return _SCRIPT_MIXED
    if has_arabic:
        return _SCRIPT_ARABIC
    if has_latin:
        return _SCRIPT_ROMAN
    return _SCRIPT_EMPTY

def _strip_combining_marks(text: str) -> str:
    """移除 Unicode 組合附標。"""
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))

def normalize_arabic_jawi_name(name: str) -> str:
    """將阿拉伯 / Jawi 姓名收斂至 Abjad 可計算形式。"""
    cleaned = unicodedata.normalize("NFC", name or "")
    pieces: list[str] = []
    for char in cleaned:
        if char.isspace():
            continue
        mapped = _ARABIC_NORMALIZATION_MAP.get(char, char)
        pieces.append(mapped)
    return "".join(pieces)

def roman_to_jawi(name: str) -> NameNormalization:
    """將常見馬來 / 阿拉伯羅馬拼音保守轉寫為 Jawi。"""
    collapsed = _strip_combining_marks(name or "").lower().strip()
    collapsed = collapsed.replace(" ", "")
    for ignored in _IGNORED_CHARACTERS:
        collapsed = collapsed.replace(ignored, "")

    if not collapsed:
        return NameNormalization(
            original=name,
            normalized="",
            detected_script=_SCRIPT_EMPTY,
            method="roman-empty",
            used_override=False,
        )

    if collapsed in _COMMON_ROMAN_OVERRIDES:
        return NameNormalization(
            original=name,
            normalized=_COMMON_ROMAN_OVERRIDES[collapsed],
            detected_script=_SCRIPT_ROMAN,
            method="roman-override",
            used_override=True,
        )

    output: list[str] = []
    index = 0
    while index < len(collapsed):
        matched = False
        for roman, jawi in _ROMAN_MULTI_MAP:
            if collapsed.startswith(roman, index):
                output.append(jawi)
                index += len(roman)
                matched = True
                break
        if matched:
            continue

        char = collapsed[index]
        output.append(_ROMAN_SINGLE_MAP.get(char, ""))
        index += 1

    normalized = normalize_arabic_jawi_name("".join(output))
    return NameNormalization(
        original=name,
        normalized=normalized,
        detected_script=_SCRIPT_ROMAN,
        method="roman-transliteration",
        used_override=False,
    )

def normalize_name(name: str, script_hint: str = "auto") -> NameNormalization:
    """依腳本提示或自動偵測結果正規化姓名。"""
    raw = name or ""
    hint = (script_hint or "auto").lower()

    if hint == _SCRIPT_ROMAN:
        return roman_to_jawi(raw)
    if hint == _SCRIPT_ARABIC:
        return NameNormalization(
            original=raw,
            normalized=normalize_arabic_jawi_name(raw),
            detected_script=_SCRIPT_ARABIC,
            method="arabic-normalization",
        )

    detected = detect_name_script(raw)
    if detected == _SCRIPT_ROMAN:
        return roman_to_jawi(raw)
    if detected in {_SCRIPT_ARABIC, _SCRIPT_MIXED}:
        return NameNormalization(
            original=raw,
            normalized=normalize_arabic_jawi_name(raw),
            detected_script=detected,
            method="arabic-normalization",
        )
    return NameNormalization(
        original=raw,
        normalized="",
        detected_script=detected,
        method="empty",
    )


__all__ = [
    "NameNormalization",
    "detect_name_script",
    "normalize_arabic_jawi_name",
    "normalize_name",
    "roman_to_jawi",
]
