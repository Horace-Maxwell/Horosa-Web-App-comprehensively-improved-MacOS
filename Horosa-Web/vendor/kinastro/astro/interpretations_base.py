"""
astro/interpretations_base.py — 解讀引擎基類 (Interpretation Engine Base)

統一所有占星體系的解讀文字介面，提供 JSON 資料載入的通用引擎。
各體系（西洋、印度、中國等）的解讀模組可繼承此基類以保持一致性。

Usage::

    from astro.interpretations_base import JsonInterpretationEngine

    engine = JsonInterpretationEngine("path/to/readings.json")
    text = engine.get_reading("Sun_in_Aries", lang="zh")
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import List

import streamlit as st


class InterpretationEngine(ABC):
    """所有解讀引擎的抽象基類。

    每個占星體系可以有自己的引擎實作，
    只需實作 ``get_reading`` 和 ``get_all_keys`` 兩個方法。
    """

    @abstractmethod
    def get_reading(self, key: str, lang: str = "zh") -> str:
        """根據 key 返回對應語言的解讀文字。

        Parameters
        ----------
        key : str
            解讀條目的唯一識別碼（如 ``"Sun_in_Aries"``）。
        lang : str
            語言代碼，``"zh"`` 或 ``"en"``。

        Returns
        -------
        str
            解讀文字。找不到時回傳空字串。
        """
        ...

    @abstractmethod
    def get_all_keys(self) -> List[str]:
        """返回所有可用的解讀 key 列表。"""
        ...

    def has_reading(self, key: str) -> bool:
        """檢查是否有指定 key 的解讀。"""
        return key in self.get_all_keys()


class JsonInterpretationEngine(InterpretationEngine):
    """從 JSON 檔案載入解讀文字的通用引擎。

    JSON 格式::

        {
            "Sun_in_Aries": {
                "zh": "太陽在白羊座代表…",
                "en": "Sun in Aries represents…"
            },
            ...
        }

    Parameters
    ----------
    json_path : str
        JSON 檔案的絕對路徑或相對路徑。
    """

    def __init__(self, json_path: str):
        self._data = _load_interpretation_json(json_path)

    def get_reading(self, key: str, lang: str = "zh") -> str:
        entry = self._data.get(key, {})
        if isinstance(entry, str):
            return entry
        return entry.get(lang, entry.get("zh", ""))

    def get_all_keys(self) -> List[str]:
        return list(self._data.keys())


@st.cache_data(show_spinner=False)
def _load_interpretation_json(json_path: str) -> dict:
    """Load and cache a JSON interpretation file."""
    abs_path = os.path.abspath(json_path)
    if not os.path.exists(abs_path):
        return {}
    with open(abs_path, "r", encoding="utf-8") as f:
        return json.load(f)
