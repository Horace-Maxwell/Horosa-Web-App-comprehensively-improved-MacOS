"""
astro/bintang_duabelas/abjad.py
===============================

Bintang Duabelas 的 Abjad 數值系統。

此版本保留原始字母-數值規則，並額外透過姓名正規化工具支援：
- 阿拉伯文
- Jawi
- 馬來 / 阿拉伯羅馬拼音
"""

from __future__ import annotations

from .normalization import NameNormalization, normalize_name


class AbjadCalculator:
    """Abjad 數值計算器。"""

    ABJAD_VALUES: dict[str, int] = {
        "ا": 1,
        "ب": 2,
        "ج": 3,
        "د": 4,
        "ه": 5,
        "و": 6,
        "ز": 7,
        "ح": 8,
        "ط": 9,
        "ي": 10,
        "ك": 20,
        "ل": 30,
        "م": 40,
        "ن": 50,
        "س": 60,
        "ع": 70,
        "ف": 80,
        "ص": 90,
        "ق": 100,
        "ر": 200,
        "ش": 300,
        "ت": 400,
        "ث": 500,
        "خ": 600,
        "ذ": 700,
        "ض": 800,
        "ظ": 900,
        "غ": 1000,
    }

    MALAY_LETTER_MAP: dict[str, str] = {
        "چ": "ج",
        "ڠ": "غ",
        "ݠ": "غ",
        "ݢ": "ق",
        "ڽ": "ي",
        "ڤ": "ف",
    }

    IGNORED_CHARS: set[str] = {
        "َ",
        "ُ",
        "ِ",
        "ّ",
        "ْ",
        "ً",
        "ٌ",
        "ٍ",
        "ٰ",
        " ",
    }

    def __init__(self) -> None:
        """建立含 Jawi 對照的查表。"""
        self._lookup = dict(self.ABJAD_VALUES)
        for malay_char, arabic_equiv in self.MALAY_LETTER_MAP.items():
            self._lookup[malay_char] = self.ABJAD_VALUES[arabic_equiv]

    def normalize(self, name: str, script_hint: str = "auto") -> NameNormalization:
        """回傳姓名正規化結果。"""
        return normalize_name(name, script_hint=script_hint)

    def letter_value(self, char: str) -> int:
        """取得單一字母 Abjad 值。"""
        return self._lookup.get(char, 0)

    def name_to_abjad_full(self, name: str, script_hint: str = "auto") -> int:
        """計算完整字母總值，不套用第二個 Alif 略去規則。"""
        normalized = self.normalize(name, script_hint=script_hint).normalized
        total = 0
        for char in normalized:
            if char in self.IGNORED_CHARS:
                continue
            total += self.letter_value(char)
        return total

    def name_to_abjad(self, name: str, script_hint: str = "auto") -> int:
        """計算姓名 Abjad 值，保留原典第二個 Alif 不計規則。"""
        normalized = self.normalize(name, script_hint=script_hint).normalized
        total = 0
        alif_count = 0
        for char in normalized:
            if char in self.IGNORED_CHARS:
                continue
            if char == "ا":
                alif_count += 1
                if alif_count > 1:
                    continue
            total += self.letter_value(char)
        return total

    def get_letter_breakdown(
        self,
        name: str,
        script_hint: str = "auto",
    ) -> list[tuple[str, int]]:
        """回傳逐字分解結果。"""
        normalized = self.normalize(name, script_hint=script_hint).normalized
        breakdown: list[tuple[str, int]] = []
        for char in normalized:
            if char in self.IGNORED_CHARS:
                continue
            value = self.letter_value(char)
            if value > 0:
                breakdown.append((char, value))
        return breakdown


__all__ = ["AbjadCalculator"]
