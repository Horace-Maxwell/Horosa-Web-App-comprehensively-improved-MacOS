"""
克里希納穆提占星術 (Krishnamurti Paddhati / KP Astrology) sub-package

KP 占星術由印度占星家 K.S. Krishnamurti (1908-1972) 創立，
結合了西洋占星的宮位系統與印度占星的 Nakshatra（27 宿）系統，
以精確預測事件發生時機而聞名。

核心特點：
- 使用 KP New Ayanamsa（與 Lahiri 略有不同）
- 採用 Placidus 宮位系統計算宮頭（Cusps）
- 每顆行星/宮頭都有 Rasi Lord（星座主）、Star Lord（宿度主）、Sub Lord（分主）
- 27 宿 × 9 Sub = 249 個 Sub 區間，嚴格按照 Vimshottari Dasha 比例分割
- 強調 Sub Lord 決定事件「是否成立」
- Ruling Planets 用於時辰占卜（Horary）與擇時

References
----------
- Krishnamurti, K.S. (1974). "KP Reader Vol. I: Fundamentals of KP Astrology"
- Krishnamurti, K.S. (1980). "KP Reader Vol. II: Horary Astrology"
- Krishnamurti, K.S. (1990). "KP Reader Vol. III: Astrological Insights"
- Krishnamurti, K.S. (1991). "KP Reader Vol. IV: Predictive Techniques"
"""

from astro.kp.kp_calculator import compute_kp_chart, KPChart
from astro.kp.kp_renderer import render_kp_chart
from astro.kp.kp_utils import (
    get_nakshatra_lord,
    get_sub_lord,
    get_rasi_lord,
    calculate_ruling_planets,
    get_significators,
)
from astro.kp.constants import (
    KP_AYANAMSA,
    NAKSHATRAS,
    SUB_LORDS,
    PLANETS,
    HOUSES,
)

__all__ = [
    # Main computation
    "compute_kp_chart",
    "KPChart",
    # Rendering
    "render_kp_chart",
    # Utils
    "get_nakshatra_lord",
    "get_sub_lord",
    "get_rasi_lord",
    "calculate_ruling_planets",
    "get_significators",
    # Constants
    "KP_AYANAMSA",
    "NAKSHATRAS",
    "SUB_LORDS",
    "PLANETS",
    "HOUSES",
]
