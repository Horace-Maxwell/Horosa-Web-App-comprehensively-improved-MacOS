"""
astro/swe_init.py — 集中初始化 pyswisseph (Centralized Swiss Ephemeris Init)

使用 @st.cache_resource 確保整個 Streamlit 進程只初始化一次。
"""
import os

import streamlit as st
import swisseph as swe


@st.cache_resource
def init_swisseph():
    """初始化 pyswisseph，只在進程啟動時執行一次。

    Returns the ``swisseph`` module after setting the ephemeris path
    (if a local ``data/ephe`` directory exists).
    """
    ephe_path = os.path.join(os.path.dirname(__file__), "data", "ephe")
    if os.path.isdir(ephe_path):
        swe.set_ephe_path(ephe_path)
    return swe
