"""
邵子神數模組 (Shao Zi Shen Shu / Shaozi Divine Numbers)

邵康節神數 · 洛陽派神數

基於北宋邵雍（邵康節）易學體系，以洛書九宮配天干起集，
天干配卦取位，組成四位條文號查詢命運條文。

核心特點：
- 四位數條文系統（1111–9888）
- 洛書九宮起集（年天干 → 1–9 集）
- 後天八卦配卦取位（月日時天干 → 1–8）
- 河洛數輔助配卦
- 4000+ 條文資料庫（CSV 格式，延遲載入）
- 64個鑰匙表格進階整合（全64數完整版）
- 元會運世時間哲學系統

使用方式::

    from astro.shaozi import ShaoziShenShu, ShaoziBirthData
    from datetime import datetime

    engine = ShaoziShenShu()
    birth = ShaoziBirthData(birth_dt=datetime(1990, 5, 15, 8, 30))
    result = engine.calculate(birth)
    print(result.tiaowen_id, result.tiaowen_text)

進階使用（含64鑰匙 + 元會運世）::

    from astro.shaozi import ShaoziFullShenShu

    shaozi = ShaoziFullShenShu()
    result = shaozi.cast_plate(
        year_gz="甲子", month_gz="丙寅",
        day_gz="戊辰", hour_gz="庚午",
        ke="初刻"
    )
    # result 包含 base_number, tiaowen_id, key（64鑰匙）, yuanhui（元會運世）
"""

from astro.shaozi.calculator import (
    ShaoziShenShu,
    ShaoziBirthData,
    ShaoziResult,
    ShaoziTiaowenDatabase,
    calculate_ganzhi_from_datetime,
)
from astro.shaozi.constants import (
    HEAVENLY_STEMS,
    EARTHLY_BRANCHES,
    TIANGAN_COLLECTION,
    TIANGAN_PEIGUA,
    TIANGAN_GUA_INDEX,
    DIZHI_PEIGUA,
    HELUO_TIANGAN,
    HELUO_DIZHI,
    COLLECTIONS,
    GUA_INDEX,
    EIGHT_TRIGRAMS,
)
from astro.shaozi.shaozi_yuanhui import YuanHuiYunShi
from astro.shaozi.shaozi_64_keys import (
    SHAOZI_64_KEYS,
    get_key_info,
    get_special_notes,
    get_key_name,
    get_detailed_key,
)
from astro.shaozi.shaozi_full_structure import ShaoziFullShenShu

__all__ = [
    # Core calculator
    "ShaoziShenShu",
    "ShaoziBirthData",
    "ShaoziResult",
    "ShaoziTiaowenDatabase",
    "calculate_ganzhi_from_datetime",
    # Constants
    "HEAVENLY_STEMS",
    "EARTHLY_BRANCHES",
    "TIANGAN_COLLECTION",
    "TIANGAN_PEIGUA",
    "TIANGAN_GUA_INDEX",
    "DIZHI_PEIGUA",
    "HELUO_TIANGAN",
    "HELUO_DIZHI",
    "COLLECTIONS",
    "GUA_INDEX",
    "EIGHT_TRIGRAMS",
    # Yuan Hui Yun Shi
    "YuanHuiYunShi",
    # 64 Keys
    "SHAOZI_64_KEYS",
    "get_key_info",
    "get_special_notes",
    "get_key_name",
    "get_detailed_key",
    # Full advanced engine
    "ShaoziFullShenShu",
]
