"""Kinketika 傳統詮釋文字工具。"""

from __future__ import annotations

from .engine import SystemKey


def get_cultural_disclaimer(lang: str = "zh") -> str:
    """文化聲明：強調工具用途與尊重在地知識傳承。"""
    if lang == "en":
        return (
            "This module is for cultural learning and reference. Please respect local "
            "Bomoh and Panrita traditions, and combine divinatory guidance with rational judgement."
        )
    return (
        "本模組為文化學習與參考用途，請尊重在地 Bomoh 與 Panrita 傳承，"
        "並將占卜建議與理性判斷並行。"
    )


def get_system_background(system: SystemKey, lang: str = "zh") -> str:
    """回傳體系背景文字。"""
    if system == "ketika_lima":
        if lang == "en":
            return (
                "Ketika Lima divides the day into five prayer-related periods "
                "(Subuh, Zohor, Asar, Maghrib, Isyak), with Baik / Nahas / Sederhana judgments."
            )
        return "Ketika Lima 依五時禮拜（Subuh、Zohor、Asar、Maghrib、Isyak）劃分吉凶時段。"

    if lang == "en":
        return (
            "Bintang Tujuh maps seven periods to the seven classical celestial bodies "
            "(Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn), widely used in Bugis-Makassar traditions."
        )
    return "Bintang Tujuh 以七曜（太陽、月亮、火星、水星、木星、金星、土星）分段，於 Bugis-Makassar 傳統尤為重要。"
