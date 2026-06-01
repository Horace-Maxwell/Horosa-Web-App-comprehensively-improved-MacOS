"""Traditional interpretation strings for Bahre Hasab outputs."""

from __future__ import annotations


TRADITION_NOTE_ZH = (
    "本模組依據衣索比亞正教會 Bahre Hasab（ባሕረ ሐሳብ）傳統計算邏輯實作，"
    "含 Amete Alem、Wenber、Abekte、Metqi 與可移動節日推算。"
)

TRADITION_NOTE_EN = (
    "This module follows Ethiopian Orthodox Bahre Hasab traditional computation principles, "
    "including Amete Alem, Wenber, Abekte, Metqi, and movable-feast computation."
)

TERM_GLOSSARY = {
    "amete_alem": {"geez": "ዓመተ ዓለም", "en": "Amete Alem", "zh": "世界紀元"},
    "wenber": {"geez": "ወንበር", "en": "Wenber", "zh": "十九年循環位次"},
    "abekte": {"geez": "አበቅቴ", "en": "Abekte", "zh": "月差日數"},
    "metqi": {"geez": "መጥቅዕ", "en": "Metqi", "zh": "補正日數"},
    "fasika": {"geez": "ፋሲካ", "en": "Fasika", "zh": "復活節"},
    "hasabe_kewakibit": {"geez": "ሐሳበ ከዋክብት", "en": "Hasabe Kewakibit", "zh": "星象推算"},
}
