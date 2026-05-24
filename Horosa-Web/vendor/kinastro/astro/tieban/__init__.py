"""
鐵板神數模組 (Tie Ban Shen Shu / Iron Plate Divine Numbers)

基於《鐵板神數清刻足本》（心一堂術數珍本古籍叢刊·星命類·神數類，2013）
底本為虛白廬藏清中葉「貞元書屋」刻本，含秘鈔密碼表

支援兩種計算版本：
1. 扣入法（kunji）  — 江靜川版：坤集密碼表 + 扣入法
2. 算盤打數（suanpan）— 曹展碩實務版：金鎖銀匙歌 + 五部條文

統一介面（推薦）：
    from astro.tieban import TieBanDiviner, TieBanBirthData

    # 算盤數模式
    diviner = TieBanDiviner(method="suanpan")
    result  = diviner.calculate(birth_data)   # -> SuanpanResult
    dayun   = diviner.get_dayun(birth_data)   # -> List[SuanpanResult]

    # 扣入法模式
    diviner = TieBanDiviner(method="kunji")
    result  = diviner.calculate(birth_data)   # -> TieBanResult
    tiaowen = diviner.get_tiaowen(tiaowen_number=1001)

    # 隨時切換
    suanpan_diviner = diviner.switch_method("suanpan")

個別引擎（進階）：
    from astro.tieban import TieBanShenShu, TieBanBirthData

    tbss = TieBanShenShu()
    result = tbss.calculate(birth_data)
    info   = tbss.get_tiaowen(1001)
    seq    = tbss.kou_ru_fa(1001)
    bake   = tbss.lookup_bake_96ke('子', '父母兄弟', 0)
"""

# ── 統一介面 ─────────────────────────────────────────────────────────────────
from astro.tieban.tieban_diviner import TieBanDiviner, DivinerMethod

# ── 扣入法（kunji）引擎 ───────────────────────────────────────────────────────
from astro.tieban.tieban_calculator import (
    TieBanShenShu,
    TieBanBirthData,
    TieBanResult,
    TiaowenDatabase,
)
from astro.tieban.tieban_renderer import render_tieban_chart_svg
from astro.tieban.kunji_full_structure import (
    kou_ru_fa,
    advanced_kou_ru_fa,
    BAKE_96_KE,
    SIX_QIN_KE_FEN,
    KUNJI_TIANGAN_CODE,
)

# ── 算盤打數（suanpan）引擎 ───────────────────────────────────────────────────
from astro.tieban.suanpan_full_structure import (
    SuanpanTiaowenDatabase,
    SuanpanResult,
    SuanpanDepartment,
    SuanpanGender,
    suanpan_calculate,
    get_dayun as suanpan_get_dayun,
    get_nayin,
    get_nayin_element,
    BASE_NUMBER as SUANPAN_BASE_NUMBER,
    SUIJUN_ADD,
    NAYIN_ADD,
    NAYIN_TO_ELEMENT,
)

__all__ = [
    # 統一介面
    "TieBanDiviner",
    "DivinerMethod",
    # 扣入法引擎
    "TieBanShenShu",
    "TieBanBirthData",
    "TieBanResult",
    "TiaowenDatabase",
    "render_tieban_chart_svg",
    "kou_ru_fa",
    "advanced_kou_ru_fa",
    "BAKE_96_KE",
    "SIX_QIN_KE_FEN",
    "KUNJI_TIANGAN_CODE",
    # 算盤打數引擎
    "SuanpanTiaowenDatabase",
    "SuanpanResult",
    "SuanpanDepartment",
    "SuanpanGender",
    "suanpan_calculate",
    "suanpan_get_dayun",
    "get_nayin",
    "get_nayin_element",
    "SUANPAN_BASE_NUMBER",
    "SUIJUN_ADD",
    "NAYIN_ADD",
    "NAYIN_TO_ELEMENT",
]
