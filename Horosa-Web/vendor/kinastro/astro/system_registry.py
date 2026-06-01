"""
astro/system_registry.py
═══════════════════════════════════════════════════════════════════════════════
KinAstro 占星體系統一 Registry（Unified System Registry）

所有占星體系的中央目錄。每個 System 實例完整描述一個占星系統，包含：
  • 多語言名稱（via i18n keys）
  • 分類 / 圖示 / 主題色
  • 子功能分頁設定（sub_tabs）
  • AI 解讀人格
  • 計算技術參數（house system、ayanamsa 等）
  • 標籤、成熟度、特性旗標

Central catalogue for all 84 astrology systems in KinAstro.
Each System instance fully describes one astrology system, including:
  • Multi-language names (via i18n keys)
  • Category / icon / accent colour
  • Sub-tab configuration
  • AI reading persona
  • Technical parameters (house system, ayanamsa etc.)
  • Tags, maturity, feature flags

Usage::

    from astro.system_registry import REGISTRY, get_system, get_systems_by_category

    system = get_system("tab_western")           # → System
    western = get_systems_by_category("cat_western")
    hits   = search_systems("印度")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

# ─────────────────────────────────────────────────────────────────────────────
# Dataclass definitions / 資料類別定義
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SubTab:
    """Configuration for one sub-tab within a system's render panel.

    一個體系子分頁的設定描述。

    Attributes:
        i18n_key:   i18n key used to look up the tab label via ``t()``.
        render_key: Internal identifier passed to the render dispatcher.
    """

    i18n_key: str    # e.g. "ch_subtab_natal"
    render_key: str  # e.g. "natal"


@dataclass
class System:
    """Complete descriptor for one astrology system registered in KinAstro.

    一個占星體系的完整描述。所有 ``*_key`` 欄位均透過 ``astro.i18n.t()`` 查詢。

    Attributes:
        id:                      Unique system ID matching the ``tab_*`` key used in
                                 ``app.py``'s ``_selected_system``.
        name_zh:                 Short Chinese name without emoji (for search / display).
        name_en:                 Short English name without emoji.
        category:                Category key (``cat_*``), matching the grouping in
                                 ``_SYSTEM_CATEGORIES`` in ``app.py``.
        icon:                    Emoji or very short SVG string for visual identity.
        tab_key:                 i18n key for the full tab label (with emoji prefix).
        desc_key:                i18n key for the system description paragraph.
        spinner_key:             i18n key for the computing-spinner text.
        hint_key:                i18n key for the short tooltip / sys_hint.
        sub_tabs:                Ordered list of sub-tab configs shown when this system
                                 is active.
        tags:                    Free-form searchable tags (bilingual encouraged).
        maturity:                ``"core"`` | ``"beta"`` | ``"experimental"``.
        accent_color:            Per-system or per-category hex accent colour used for
                                 UI theming.
        recommended_house_system: Preferred house division (Western systems).
        default_ayanamsa:        Default ayanamsa (Vedic / sidereal systems).
        supports_transit:        Whether a transit sub-feature is available.
        supports_synastry:       Whether a synastry / compatibility sub-feature exists.
        supports_dasha:          Whether a dasha / period sub-feature exists.
        supports_return:         Whether a solar/lunar return sub-feature exists.
        supports_rectification:  Whether this system has rectification support.
        ai_persona_key:          Optional i18n key for the AI expert persona system
                                 prompt used in ``ai_analysis.py``.
        origin_culture:          Cultural origin string (for filtering / display).
        tradition_period:        Historical period / dynasty string.
        extra:                   Extensible dict for future metadata.
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    id: str                    # e.g. "tab_western"
    name_zh: str               # e.g. "西洋占星"
    name_en: str               # e.g. "Western Astrology"
    category: str              # e.g. "cat_western"
    icon: str                  # e.g. "🌍"

    # ── i18n keys ─────────────────────────────────────────────────────────────
    tab_key: str               # i18n key for the tab label
    desc_key: str              # i18n key for description
    spinner_key: str           # i18n key for spinner text
    hint_key: str              # i18n key for sys_hint tooltip

    # ── Sub-tabs ──────────────────────────────────────────────────────────────
    sub_tabs: List[SubTab] = field(default_factory=list)

    # ── Taxonomy ──────────────────────────────────────────────────────────────
    tags: List[str] = field(default_factory=list)
    maturity: str = "core"     # "core" | "beta" | "experimental"

    # ── Visual identity ───────────────────────────────────────────────────────
    accent_color: str = "#7C3AED"  # Violet default; override per system/category

    # ── Astro technical config ────────────────────────────────────────────────
    recommended_house_system: Optional[str] = None   # e.g. "Placidus", "Whole Sign"
    default_ayanamsa: Optional[str] = None           # e.g. "Lahiri", "Krishnamurti"

    # ── Feature flags ─────────────────────────────────────────────────────────
    supports_transit: bool = False
    supports_synastry: bool = False
    supports_dasha: bool = False
    supports_return: bool = False
    supports_rectification: bool = False

    # ── AI persona ────────────────────────────────────────────────────────────
    ai_persona_key: Optional[str] = None  # i18n key for AI system-prompt persona

    # ── Metadata ──────────────────────────────────────────────────────────────
    origin_culture: str = ""   # e.g. "Chinese", "Western", "Indian"
    tradition_period: str = "" # e.g. "Han Dynasty", "Medieval", "Ancient Greek"
    extra: Dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Accent colour palette / 各分類主題色
# ─────────────────────────────────────────────────────────────────────────────

_ACCENT = {
    "cat_sanshi":     "#8B3A3A",  # 深磚紅——三式秘術
    "cat_chinese":    "#C8102E",  # 中國紅——中華傳統
    "cat_western":    "#2C5FBF",  # 皇家藍——西方占星
    "cat_indian":     "#E87416",  # 番紅花橙——印度吠陀
    "cat_asian":      "#2E7D32",  # 翠綠——亞洲體系
    "cat_middle_east":"#B8860B",  # 古金——中東體系
    "cat_africa":     "#8B4513",  # 赭紅——非洲體系
    "cat_ancient":    "#6B4226",  # 古銅——古文明
    "cat_obscure":    "#5A3B2E",  # 深赭——隱祕與原民傳統
    "cat_yi_zhan":    "#1B5E20",  # 醫綠——醫占
    "cat_horary":     "#6A0DAD",  # 深紫——卜卦
}

# ─────────────────────────────────────────────────────────────────────────────
# Category display order (matches _SYSTEM_CATEGORIES in app.py)
# ─────────────────────────────────────────────────────────────────────────────

CATEGORY_ORDER: List[str] = [
    "cat_sanshi",
    "cat_chinese",
    "cat_western",
    "cat_indian",
    "cat_asian",
    "cat_middle_east",
    "cat_africa",
    "cat_ancient",
    "cat_obscure",
    "cat_yi_zhan",
    "cat_horary",
]

# ─────────────────────────────────────────────────────────────────────────────
# Category icon mapping / 分類圖示
# ─────────────────────────────────────────────────────────────────────────────

CATEGORY_ICONS: Dict[str, str] = {
    "cat_sanshi":     "☯️",
    "cat_chinese":    "🏮",
    "cat_western":    "🏛️",
    "cat_indian":     "🪷",
    "cat_asian":      "🌏",
    "cat_middle_east":"🕌",
    "cat_africa":     "🌍",
    "cat_ancient":    "🏺",
    "cat_obscure":    "🜁",
    "cat_yi_zhan":    "⚕️",
    "cat_horary":     "📜",
}

# ─────────────────────────────────────────────────────────────────────────────
# Helper: build accent for a system given its category
# ─────────────────────────────────────────────────────────────────────────────

def _a(category: str) -> str:
    """Return accent colour for a category. / 傳回分類主題色。"""
    return _ACCENT.get(category, "#7C3AED")


# ─────────────────────────────────────────────────────────────────────────────
# REGISTRY: dict[system_id → System]
# Sorted in the same order as _SYSTEM_CATEGORIES in app.py for predictability.
# ─────────────────────────────────────────────────────────────────────────────

REGISTRY: Dict[str, System] = {}

# ── Helper to register and return ────────────────────────────────────────────

def _reg(system: System) -> System:
    """Register a system and return it (fluent helper)."""
    REGISTRY[system.id] = system
    return system


# ═════════════════════════════════════════════════════════════════════════════
# cat_sanshi — 三式（Three Formulae）☯️
# ═════════════════════════════════════════════════════════════════════════════

_reg(System(
    id="tab_liuren",
    name_zh="大六壬",
    name_en="Da Liu Ren",
    category="cat_sanshi",
    icon="🔮",
    tab_key="tab_liuren",
    desc_key="desc_liuren",
    spinner_key="spinner_liuren",
    hint_key="sys_hint_liuren",
    tags=["六壬", "三式", "liuren", "divination", "chinese", "timekeeping"],
    maturity="core",
    accent_color=_a("cat_sanshi"),
    origin_culture="Chinese",
    tradition_period="Han Dynasty",
    ai_persona_key="info_liuren_prompt",
))

_reg(System(
    id="tab_taiyi",
    name_zh="太乙命法",
    name_en="Taiyi Life Method",
    category="cat_sanshi",
    icon="🌟",
    tab_key="tab_taiyi",
    desc_key="desc_taiyi",
    spinner_key="spinner_taiyi",
    hint_key="sys_hint_taiyi",
    tags=["太乙", "三式", "taiyi", "chinese", "imperial"],
    maturity="core",
    accent_color=_a("cat_sanshi"),
    origin_culture="Chinese",
    tradition_period="Tang–Song Dynasty",
    ai_persona_key="info_taiyi_prompt",
))

_reg(System(
    id="tab_qimen_luming",
    name_zh="奇門祿命",
    name_en="Qimen Destiny",
    category="cat_sanshi",
    icon="🔮",
    tab_key="tab_qimen_luming",
    desc_key="desc_qimen_luming",
    spinner_key="spinner_qimen_luming",
    hint_key="sys_hint_qimen_luming",
    tags=["奇門", "三式", "qimen", "destiny", "chinese"],
    maturity="core",
    accent_color=_a("cat_sanshi"),
    origin_culture="Chinese",
    tradition_period="Tang–Song Dynasty",
    ai_persona_key="info_qimen_luming_prompt",
))


# ═════════════════════════════════════════════════════════════════════════════
# cat_chinese — 中華傳統 🏮
# ═════════════════════════════════════════════════════════════════════════════

_reg(System(
    id="tab_ziwei",
    name_zh="紫微斗數",
    name_en="Zi Wei Dou Shu",
    category="cat_chinese",
    icon="🌟",
    tab_key="tab_ziwei",
    desc_key="desc_ziwei",
    spinner_key="spinner_ziwei",
    hint_key="sys_hint_ziwei",
    sub_tabs=[
        SubTab("ziwei_subtab_natal",   "natal"),
        SubTab("ziwei_subtab_daxian",  "daxian"),
    ],
    tags=["紫微", "命盤", "ziwei", "chinese", "popular"],
    maturity="core",
    accent_color="#6A0DAD",   # 紫金色——紫微專屬
    supports_dasha=True,
    origin_culture="Chinese",
    tradition_period="Song Dynasty",
    ai_persona_key="info_ziwei_prompt",
))

_reg(System(
    id="tab_chinese",
    name_zh="七政四餘",
    name_en="Qi Zheng Si Yu",
    category="cat_chinese",
    icon="🀄",
    tab_key="tab_chinese",
    desc_key="desc_chinese",
    spinner_key="spinner_chinese",
    hint_key="sys_hint_chinese",
    sub_tabs=[
        SubTab("ch_subtab_natal",       "natal"),
        SubTab("ch_subtab_shensha",     "shensha"),
        SubTab("ch_subtab_dasha",       "dasha"),
        SubTab("ch_subtab_transit",     "transit"),
        SubTab("ch_subtab_zhangguo",    "zhangguo"),
        SubTab("ch_subtab_electional",  "electional"),
    ],
    tags=["七政", "四餘", "qizheng", "chinese", "astrology", "planets"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    supports_transit=True,
    supports_dasha=True,
    origin_culture="Chinese",
    tradition_period="Tang–Ming Dynasty",
    ai_persona_key="info_chinese_prompt",
))

_reg(System(
    id="tab_chinstar",
    name_zh="萬化仙禽",
    name_en="WanHua XianQin",
    category="cat_chinese",
    icon="🐦",
    tab_key="tab_chinstar",
    desc_key="desc_chinstar",
    spinner_key="spinner_chinstar",
    hint_key="sys_hint_chinstar",
    sub_tabs=[
        SubTab("chinstar_subtab_chart",     "chart"),
        SubTab("chinstar_subtab_xiangtai",  "xiangtai"),
        SubTab("chinstar_subtab_gui_jian",  "gui_jian"),
    ],
    tags=["仙禽", "演禽", "chinstar", "birds", "chinese", "ming"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Ming Dynasty",
    ai_persona_key="info_chinstar_prompt",
))

_reg(System(
    id="tab_twelve_ci",
    name_zh="十二星次",
    name_en="Twelve Ci",
    category="cat_chinese",
    icon="🌌",
    tab_key="tab_twelve_ci",
    desc_key="desc_twelve_ci",
    spinner_key="spinner_twelve_ci",
    hint_key="sys_hint_twelve_ci",
    sub_tabs=[
        SubTab("twelve_ci_subtab_chart",  "chart"),
        SubTab("twelve_ci_subtab_detail", "detail"),
    ],
    tags=["十二星次", "木星", "twelve_ci", "jupiter", "chinese", "ancient"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Zhou–Han Dynasty",
    ai_persona_key="info_twelve_ci_prompt",
))

_reg(System(
    id="tab_cetian_ziwei",
    name_zh="策天飛星",
    name_en="Ce Tian Flying Stars",
    category="cat_chinese",
    icon="🌠",
    tab_key="tab_cetian_ziwei",
    desc_key="desc_cetian_ziwei",
    spinner_key="spinner_cetian_ziwei",
    hint_key="sys_hint_cetian_ziwei",
    tags=["策天", "飛星", "cetian_ziwei", "chinese", "ancient"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Ancient",
    ai_persona_key="info_cetian_ziwei_prompt",
))

_reg(System(
    id="tab_damo",
    name_zh="達摩一掌經",
    name_en="Damo One Palm",
    category="cat_chinese",
    icon="🤚",
    tab_key="tab_damo",
    desc_key="desc_damo",
    spinner_key="spinner_damo",
    hint_key="sys_hint_damo",
    sub_tabs=[
        SubTab("damo_subtab_chart",   "chart"),
        SubTab("damo_subtab_detail",  "detail"),
        SubTab("damo_subtab_advice",  "advice"),
        SubTab("damo_subtab_classic", "classic"),
    ],
    tags=["達摩", "一掌經", "damo", "palm", "chinese"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Tang Dynasty",
    ai_persona_key="info_damo_prompt",
))

_reg(System(
    id="tab_tieban",
    name_zh="鐵板神數",
    name_en="Tie Ban Shen Shu",
    category="cat_chinese",
    icon="🔮",
    tab_key="tab_tieban",
    desc_key="desc_tieban",
    spinner_key="spinner_tieban",
    hint_key="sys_hint_tieban",
    sub_tabs=[
        SubTab("tieban_subtab_main",    "main"),
        SubTab("tieban_subtab_tiaowen", "tiaowen"),
        SubTab("tieban_subtab_kunji",   "kunji"),
    ],
    tags=["鐵板", "神數", "tieban", "shenshu", "chinese", "numerology"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Song Dynasty",
    ai_persona_key="info_tieban_prompt",
    extra={"has_kunji_mode": True, "has_suanpan_mode": True},
))

_reg(System(
    id="tab_shaozi",
    name_zh="邵子神數",
    name_en="Shao Zi Shen Shu",
    category="cat_chinese",
    icon="🔯",
    tab_key="tab_shaozi",
    desc_key="desc_shaozi",
    spinner_key="spinner_shaozi",
    hint_key="sys_hint_shaozi",
    sub_tabs=[
        SubTab("shaozi_subtab_main",    "main"),
        SubTab("shaozi_subtab_64keys",  "64keys"),
        SubTab("shaozi_subtab_tiaowen", "tiaowen"),
    ],
    tags=["邵子", "神數", "shaozi", "shenshu", "chinese", "numerology"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Song Dynasty (Shao Yong)",
    ai_persona_key="info_shaozi_prompt",
))

_reg(System(
    id="tab_huangji",
    name_zh="皇極經世",
    name_en="Huangji Jingshi",
    category="cat_chinese",
    icon="🏮",
    tab_key="tab_huangji",
    desc_key="desc_huangji",
    spinner_key="spinner_huangji",
    hint_key="sys_hint_huangji",
    sub_tabs=[
        SubTab("huangji_tab_basic", "basic"),
        SubTab("huangji_tab_cycles", "cycles"),
        SubTab("huangji_tab_cross", "cross"),
        SubTab("huangji_tab_history", "history"),
    ],
    tags=[
        "皇極經世", "邵雍", "先天易數", "元會運世", "huangji", "wangji",
        "kinwangji", "四卦", "歷史周期", "cross-system",
    ],
    maturity="beta",
    accent_color="#8E6B3D",
    origin_culture="Chinese",
    tradition_period="Song Dynasty (Shao Yong)",
    ai_persona_key="info_huangji_prompt",
))


_reg(System(
    id="tab_diqiyijue",
    name_zh="滌器遺訣",
    name_en="Di Qi Yi Jue",
    category="cat_chinese",
    icon="🌀",
    tab_key="tab_diqiyijue",
    desc_key="desc_diqiyijue",
    spinner_key="spinner_diqiyijue",
    hint_key="sys_hint_diqiyijue",
    sub_tabs=[
        SubTab("diqiyijue_subtab_chart", "chart"),
        SubTab("diqiyijue_subtab_analysis", "analysis"),
        SubTab("diqiyijue_subtab_flow", "flow"),
        SubTab("diqiyijue_subtab_classic", "classic"),
    ],
    tags=["滌器遺訣", "邵子氣數", "diqiyijue", "qi_shu", "chinese", "numerology"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Song Dynasty (Shao Yong tradition)",
    ai_persona_key="info_diqiyijue_prompt",
))

_reg(System(
    id="tab_fendjing",
    name_zh="鬼谷分定經",
    name_en="Ghost Valley Fen Ding Jing",
    category="cat_chinese",
    icon="🔮",
    tab_key="tab_fendjing",
    desc_key="desc_fendjing",
    spinner_key="spinner_fendjing",
    hint_key="sys_hint_fendjing",
    tags=["鬼谷", "分定", "fendjing", "chinese", "fate"],
    maturity="beta",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Warring States",
    ai_persona_key="info_fendjing_prompt",
))

_reg(System(
    id="tab_taixuan",
    name_zh="太玄數",
    name_en="Tai Xuan Shu",
    category="cat_chinese",
    icon="☰",
    tab_key="tab_taixuan",
    desc_key="desc_taixuan",
    spinner_key="spinner_taixuan",
    hint_key="sys_hint_taixuan",
    sub_tabs=[
        SubTab("taixuan_subtab_natal", "natal"),
        SubTab("taixuan_subtab_qigua", "qigua"),
    ],
    tags=["太玄", "taixuan", "chinese", "yang_xiong", "hexagram"],
    maturity="beta",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Han Dynasty (Yang Xiong)",
    ai_persona_key="info_taixuan_prompt",
))

_reg(System(
    id="tab_wuyunliuqi",
    name_zh="五運六氣",
    name_en="Wu Yun Liu Qi",
    category="cat_chinese",
    icon="☯",
    tab_key="tab_wuyunliuqi",
    desc_key="desc_wuyunliuqi",
    spinner_key="spinner_wuyunliuqi",
    hint_key="sys_hint_wuyunliuqi",
    tags=["五運", "六氣", "wuyunliuqi", "tcm", "chinese", "medical"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Han Dynasty",
    ai_persona_key="info_wuyunliuqi_prompt",
))

_reg(System(
    id="tab_liuyao_lifetime",
    name_zh="六爻終身卦",
    name_en="Lifetime Liu Yao",
    category="cat_chinese",
    icon="🔯",
    tab_key="tab_liuyao_lifetime",
    desc_key="desc_liuyao_lifetime",
    spinner_key="spinner_liuyao_lifetime",
    hint_key="sys_hint_liuyao_lifetime",
    tags=["六爻", "終身卦", "liuyao", "iching", "chinese"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Song Dynasty",
    ai_persona_key="info_liuyao_lifetime_prompt",
))

_reg(System(
    id="tab_beiji",
    name_zh="北極神數",
    name_en="Beiji Shenshu",
    category="cat_chinese",
    icon="⭐",
    tab_key="tab_beiji",
    desc_key="desc_beiji",
    spinner_key="spinner_beiji",
    hint_key="sys_hint_beiji",
    tags=["北極", "神數", "beiji", "shenshu", "chinese"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Classical",
    ai_persona_key="info_beiji_prompt",
))

_reg(System(
    id="tab_nanji",
    name_zh="南極神數",
    name_en="Nanji Shenshu",
    category="cat_chinese",
    icon="☰",
    tab_key="tab_nanji",
    desc_key="desc_nanji",
    spinner_key="spinner_nanji",
    hint_key="sys_hint_nanji",
    tags=["南極", "神數", "nanji", "shenshu", "chinese"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Classical",
    ai_persona_key="info_nanji_prompt",
))

_reg(System(
    id="tab_bazi",
    name_zh="子平八字",
    name_en="Ziping Bazi",
    category="cat_chinese",
    icon="🀄",
    tab_key="tab_bazi",
    desc_key="desc_bazi",
    spinner_key="spinner_bazi",
    hint_key="sys_hint_bazi",
    tags=["八字", "子平", "bazi", "four pillars", "chinese", "popular"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Song Dynasty (Xu Zi Ping)",
    supports_dasha=True,
    ai_persona_key="info_bazi_prompt",
))

_reg(System(
    id="tab_chunzi",
    name_zh="蠢子數",
    name_en="ChunZiShu",
    category="cat_chinese",
    icon="☵",
    tab_key="tab_chunzi",
    desc_key="desc_chunzi",
    spinner_key="spinner_chunzi",
    hint_key="sys_hint_chunzi",
    tags=["蠢子數", "二十八宿", "七政四餘", "詩詞命理", "chunzi", "lunar mansions", "chinese"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Traditional Chinese",
    ai_persona_key="info_chunzi_prompt",
))

_reg(System(
    id="tab_kaiyuan",
    name_zh="開元占經",
    name_en="Kaiyuan Zhanjing",
    category="cat_chinese",
    icon="📜",
    tab_key="tab_kaiyuan",
    desc_key="desc_kaiyuan",
    spinner_key="spinner_kaiyuan",
    hint_key="sys_hint_kaiyuan",
    tags=["開元占經", "五星", "二十八宿", "月占", "日食", "五音", "kaiyuan", "tang dynasty", "chinese", "omen"],
    maturity="core",
    accent_color=_a("cat_chinese"),
    origin_culture="Chinese",
    tradition_period="Tang Dynasty (開元年間)",
    ai_persona_key="info_kaiyuan_prompt",
))


# ═════════════════════════════════════════════════════════════════════════════
# cat_western — 西方體系 🏛️
# ═════════════════════════════════════════════════════════════════════════════

_reg(System(
    id="tab_western",
    name_zh="西洋占星",
    name_en="Western Astrology",
    category="cat_western",
    icon="🌍",
    tab_key="tab_western",
    desc_key="desc_western",
    spinner_key="spinner_western",
    hint_key="sys_hint_western",
    sub_tabs=[
        SubTab("western_subtab_natal",    "natal"),
        SubTab("western_subtab_transit",  "transit"),
        SubTab("western_subtab_return",   "return"),
        SubTab("western_subtab_synastry", "synastry"),
        SubTab("western_subtab_dignity",  "dignity"),
        SubTab("western_subtab_harmonic", "harmonic"),
        SubTab("western_subtab_draconic", "draconic"),
        SubTab("western_subtab_asteroids","asteroids"),
        SubTab("western_subtab_stars",    "fixed_stars"),
        SubTab("western_subtab_parans",   "parans"),
        SubTab("western_subtab_heliacal", "heliacal"),
        SubTab("western_subtab_predictive","predictive"),
    ],
    tags=["western", "natal", "transit", "synastry", "modern", "popular"],
    maturity="core",
    accent_color="#1565C0",
    recommended_house_system="Placidus",
    supports_transit=True,
    supports_synastry=True,
    supports_return=True,
    supports_rectification=True,
    origin_culture="Western",
    tradition_period="Modern (20th century)",
    ai_persona_key="info_western_prompt",
))

_reg(System(
    id="tab_sabian",
    name_zh="薩比恩符號",
    name_en="Sabian Symbols",
    category="cat_western",
    icon="🔯",
    tab_key="sabian_system_label",  # app.py uses "sabian_system_label" (not "tab_sabian")
    desc_key="desc_sabian",
    spinner_key="spinner_western",   # Sabian uses the western spinner
    hint_key="sys_hint_sabian",
    tags=["sabian", "symbols", "western", "degrees", "marc jones"],
    maturity="core",
    accent_color=_a("cat_western"),
    recommended_house_system="Placidus",
    origin_culture="Western",
    tradition_period="20th century (Marc Edmund Jones)",
    ai_persona_key="info_sabian_prompt",
))

_reg(System(
    id="tab_hellenistic",
    name_zh="希臘占星",
    name_en="Hellenistic Astrology",
    category="cat_western",
    icon="🏛️",
    tab_key="tab_hellenistic",
    desc_key="desc_hellenistic",
    spinner_key="spinner_hellenistic",
    hint_key="sys_hint_hellenistic",
    sub_tabs=[
        SubTab("hellen_subtab_chart",       "chart"),
        SubTab("hellen_subtab_natal",       "natal"),
        SubTab("hellen_subtab_profections", "profections"),
        SubTab("hellen_subtab_zr",          "zodiacal_releasing"),
        SubTab("hellen_subtab_lots",        "lots"),
        SubTab("hellen_subtab_synkrasis",   "synkrasis"),
        SubTab("hellen_subtab_centiloquy",  "centiloquy"),
    ],
    tags=["hellenistic", "greek", "ptolemy", "ancient", "lots", "profections"],
    maturity="core",
    accent_color="#795548",    # Antique brown for antiquity
    recommended_house_system="Whole Sign",
    origin_culture="Greco-Roman",
    tradition_period="Hellenistic (3rd c. BCE – 7th c. CE)",
    ai_persona_key="info_hellenistic_prompt",
))

_reg(System(
    id="tab_acg",
    name_zh="地點占星 ACG",
    name_en="Astrocartography",
    category="cat_western",
    icon="🌍",
    tab_key="tab_acg",
    desc_key="desc_acg",
    spinner_key="spinner_acg",
    hint_key="sys_hint_acg",
    sub_tabs=[
        SubTab("acg_subtab_map",     "map"),
        SubTab("acg_subtab_table",   "table"),
        SubTab("acg_subtab_transit", "transit"),
    ],
    tags=["acg", "astrocartography", "location", "relocation", "western"],
    maturity="core",
    accent_color=_a("cat_western"),
    supports_transit=True,
    origin_culture="Western",
    tradition_period="20th century (Jim Lewis)",
    ai_persona_key="info_acg_prompt",
))

_reg(System(
    id="tab_uranian",
    name_zh="天王星占星",
    name_en="Uranian Astrology",
    category="cat_western",
    icon="♅",
    tab_key="tab_uranian",
    desc_key="desc_uranian",
    spinner_key="spinner_uranian",
    hint_key="sys_hint_uranian",
    tags=["uranian", "hamburger school", "transneptunian", "western"],
    maturity="core",
    accent_color=_a("cat_western"),
    recommended_house_system="Aries",
    origin_culture="Western",
    tradition_period="Early 20th century (Hamburg School)",
    ai_persona_key="info_uranian_prompt",
))

_reg(System(
    id="tab_cosmobiology",
    name_zh="宇宙生物學",
    name_en="Cosmobiology",
    category="cat_western",
    icon="🔬",
    tab_key="tab_cosmobiology",
    desc_key="desc_cosmobiology",
    spinner_key="spinner_cosmobiology",
    hint_key="sys_hint_cosmobiology",
    tags=["cosmobiology", "ebertin", "midpoints", "western"],
    maturity="core",
    accent_color=_a("cat_western"),
    origin_culture="Western",
    tradition_period="20th century (Ebertin)",
    ai_persona_key="info_cosmobiology_prompt",
))

_reg(System(
    id="tab_harmonic",
    name_zh="和諧占星",
    name_en="Harmonic Astrology",
    category="cat_western",
    icon="🎵",
    tab_key="tab_harmonic",
    desc_key="desc_harmonic",
    spinner_key="spinner_harmonic",
    hint_key="sys_hint_harmonic",
    tags=["harmonic", "harmonics", "john addey", "western"],
    maturity="core",
    accent_color=_a("cat_western"),
    origin_culture="Western",
    tradition_period="20th century (John Addey)",
    ai_persona_key="info_harmonic_prompt",
))

_reg(System(
    id="tab_primary_directions",
    name_zh="古典主限推運",
    name_en="Primary Directions",
    category="cat_western",
    icon="⚷",
    tab_key="tab_primary_directions",
    desc_key="desc_primary_directions",
    spinner_key="spinner_primary_directions",
    hint_key="sys_hint_primary_directions",
    tags=["primary directions", "ptolemy", "classical", "predictive", "western"],
    maturity="core",
    accent_color=_a("cat_western"),
    recommended_house_system="Placidus",
    origin_culture="Western",
    tradition_period="Classical to Medieval",
    ai_persona_key="info_primary_directions_prompt",
))

_reg(System(
    id="tab_celtic_tree",
    name_zh="凱爾特樹木曆",
    name_en="Celtic Tree Calendar",
    category="cat_western",
    icon="🌳",
    tab_key="tab_celtic_tree",
    desc_key="desc_celtic_tree",
    spinner_key="spinner_celtic_tree",
    hint_key="sys_hint_celtic_tree",
    tags=["celtic", "tree calendar", "druid", "celtic tree", "western"],
    maturity="core",
    accent_color="#2E7D32",   # Forest green for Celtic
    origin_culture="Celtic",
    tradition_period="Iron Age Celtic",
    ai_persona_key="info_celtic_tree_prompt",
))

_reg(System(
    id="tab_rectification",
    name_zh="出生時間校正",
    name_en="Birth Time Rectification",
    category="cat_western",
    icon="🔮",
    tab_key="tab_rectification",
    desc_key="desc_rectification",
    spinner_key="spinner_rectification",
    hint_key="sys_hint_rectification",
    tags=["rectification", "birth time", "western", "accuracy"],
    maturity="core",
    accent_color=_a("cat_western"),
    supports_rectification=True,
    origin_culture="Western",
    ai_persona_key="info_rectification_prompt",
))

_reg(System(
    id="tab_trutine_of_hermes",
    name_zh="赫密士前世盤",
    name_en="Trutine of Hermes",
    category="cat_western",
    icon="☿",
    tab_key="tab_trutine_of_hermes",
    desc_key="desc_trutine_of_hermes",
    spinner_key="spinner_trutine_of_hermes",
    hint_key="sys_hint_trutine_of_hermes",
    tags=["trutine", "hermes", "pre-natal", "conception", "western", "hellenistic"],
    maturity="core",
    accent_color=_a("cat_western"),
    origin_culture="Western",
    tradition_period="Hellenistic",
    ai_persona_key="info_trutine_of_hermes_prompt",
))

_reg(System(
    id="tab_esoteric",
    name_zh="靈性占星（七道光線）",
    name_en="Esoteric Astrology (Seven Rays)",
    category="cat_western",
    icon="✨",
    tab_key="tab_esoteric",
    desc_key="desc_esoteric",
    spinner_key="spinner_esoteric",
    hint_key="sys_hint_esoteric",
    tags=["esoteric", "seven rays", "alice bailey", "spiritual", "western"],
    maturity="core",
    accent_color="#9C27B0",   # Mystical violet
    origin_culture="Western",
    tradition_period="20th century (Alice Bailey / Djwhal Khul)",
    ai_persona_key="info_esoteric_prompt",
))

_reg(System(
    id="tab_byzantine_astrology",
    name_zh="拜占庭占星",
    name_en="Byzantine Astrology",
    category="cat_western",
    icon="✚",
    tab_key="tab_byzantine_astrology",
    desc_key="desc_byzantine_astrology",
    spinner_key="spinner_byzantine_astrology",
    hint_key="sys_hint_byzantine_astrology",
    tags=["byzantine", "medieval", "eastern roman", "western", "classical"],
    maturity="core",
    accent_color="#B71C1C",   # Byzantine crimson
    recommended_house_system="Whole Sign",
    origin_culture="Byzantine",
    tradition_period="Byzantine Empire (4th–15th c.)",
    ai_persona_key="info_byzantine_astrology_prompt",
))

_reg(System(
    id="tab_human_design",
    name_zh="人間圖",
    name_en="Human Design",
    category="cat_western",
    icon="☯",
    tab_key="tab_human_design",
    desc_key="desc_human_design",
    spinner_key="spinner_human_design",
    hint_key="sys_hint_human_design",
    tags=["human design", "bodygraph", "channels", "gates", "modern", "western"],
    maturity="core",
    accent_color="#FF7043",   # Modern warm orange
    origin_culture="Western",
    tradition_period="20th century (Ra Uru Hu)",
    ai_persona_key="info_human_design_prompt",
))


# ═════════════════════════════════════════════════════════════════════════════
# cat_indian — 印度體系 🪷
# ═════════════════════════════════════════════════════════════════════════════

_reg(System(
    id="tab_indian",
    name_zh="印度占星",
    name_en="Indian / Vedic Astrology",
    category="cat_indian",
    icon="🙏",
    tab_key="tab_indian",
    desc_key="desc_indian",
    spinner_key="spinner_indian",
    hint_key="sys_hint_indian",
    sub_tabs=[
        SubTab("vedic_subtab_rashi",   "rashi"),
        SubTab("vedic_subtab_dasha",   "dasha"),
        SubTab("vedic_subtab_ashtaka", "ashtaka"),
        SubTab("vedic_subtab_yogas",   "yogas"),
        SubTab("vedic_subtab_bphs",    "bphs"),
        SubTab("vedic_subtab_varga",   "varga"),
    ],
    tags=["vedic", "jyotish", "indian", "rashi", "dasha", "popular"],
    maturity="core",
    accent_color=_a("cat_indian"),
    recommended_house_system="Whole Sign",
    default_ayanamsa="Lahiri",
    supports_transit=True,
    supports_dasha=True,
    origin_culture="Indian",
    tradition_period="Vedic (1500 BCE – present)",
    ai_persona_key="info_indian_prompt",
))

_reg(System(
    id="tab_lal_kitab",
    name_zh="紅皮書占星",
    name_en="Lal Kitab",
    category="cat_indian",
    icon="📕",
    tab_key="tab_lal_kitab",
    desc_key="desc_lal_kitab",
    spinner_key="spinner_lal_kitab",
    hint_key="sys_hint_lal_kitab",
    tags=["lal kitab", "red book", "indian", "remedies", "urdu"],
    maturity="core",
    accent_color="#C62828",   # Red for Lal Kitab
    default_ayanamsa="Lahiri",
    origin_culture="Indian",
    tradition_period="19th century (Pandit Roop Chand Joshi)",
    ai_persona_key="info_lal_kitab_prompt",
))

_reg(System(
    id="tab_nadi",
    name_zh="印度納迪占星",
    name_en="Nadi Jyotish",
    category="cat_indian",
    icon="🔱",
    tab_key="tab_nadi",
    desc_key="desc_nadi",
    spinner_key="spinner_nadi",
    hint_key="sys_hint_nadi",
    tags=["nadi", "palm leaf", "agastya", "tamil", "indian"],
    maturity="core",
    accent_color=_a("cat_indian"),
    default_ayanamsa="Lahiri",
    origin_culture="South Indian",
    tradition_period="Ancient Tamil (Agastya Muni)",
    ai_persona_key="info_nadi_prompt",
))

_reg(System(
    id="tab_jaimini",
    name_zh="闍彌尼占星",
    name_en="Jaimini Astrology",
    category="cat_indian",
    icon="🕉️",
    tab_key="tab_jaimini",
    desc_key="desc_jaimini",
    spinner_key="spinner_jaimini",
    hint_key="sys_hint_jaimini",
    sub_tabs=[
        SubTab("jaimini_subtab_chart", "chart"),
        SubTab("jaimini_subtab_dasha", "dasha"),
    ],
    tags=["jaimini", "vedic", "chara dasha", "rashi drishti", "indian"],
    maturity="core",
    accent_color=_a("cat_indian"),
    default_ayanamsa="Lahiri",
    supports_dasha=True,
    origin_culture="Indian",
    tradition_period="Sutras period (Jaimini Muni)",
    ai_persona_key="info_jaimini_prompt",
))

_reg(System(
    id="tab_kp",
    name_zh="KP 占星",
    name_en="KP Astrology",
    category="cat_indian",
    icon="🔮",
    tab_key="tab_kp",
    desc_key="desc_kp",
    spinner_key="spinner_kp",
    hint_key="sys_hint_kp",
    tags=["kp", "krishnamurti", "sub lord", "ruling planets", "indian"],
    maturity="core",
    accent_color=_a("cat_indian"),
    recommended_house_system="Placidus",
    default_ayanamsa="Krishnamurti",
    origin_culture="Indian",
    tradition_period="20th century (K.S. Krishnamurti)",
    ai_persona_key="info_kp_prompt",
))

_reg(System(
    id="tab_vastu",
    name_zh="吠陀風水",
    name_en="Vastu Shastra",
    category="cat_indian",
    icon="🪔",
    tab_key="tab_vastu",
    desc_key="desc_vastu",
    spinner_key="spinner_vastu",
    hint_key="sys_hint_vastu",
    tags=["vastu", "vedic", "indian", "architecture", "directional", "mandala", "popular"],
    maturity="core",
    accent_color="#FF9F1C",  # 橘金——Vastu 曼荼羅主題色
    default_ayanamsa="Lahiri",
    origin_culture="Indian",
    tradition_period="Vedic (Mayamata, Manasara, Bṛhat Saṃhitā)",
    ai_persona_key="info_vastu_prompt",
))


# ═════════════════════════════════════════════════════════════════════════════
# cat_asian — 亞洲體系 🌏
# ═════════════════════════════════════════════════════════════════════════════

_reg(System(
    id="tab_tojeong",
    name_zh="土亭數",
    name_en="Tojeong Shu",
    category="cat_asian",
    icon="🔮",
    tab_key="tab_tojeong",
    desc_key="desc_tojeong",
    spinner_key="spinner_tojeong",
    hint_key="sys_hint_tojeong",
    tags=["tojeong", "korean", "joseon", "numerology", "asian"],
    maturity="core",
    accent_color=_a("cat_asian"),
    origin_culture="Korean",
    tradition_period="Joseon Dynasty (Yi Ji-ham)",
    ai_persona_key="info_tojeong_prompt",
))

_reg(System(
    id="tab_sukkayodo",
    name_zh="日本宿曜道",
    name_en="Sukkayodo",
    category="cat_asian",
    icon="🈳",
    tab_key="tab_sukkayodo",
    desc_key="desc_sukkayodo",
    spinner_key="spinner_sukkayodo",
    hint_key="sys_hint_sukkayodo",
    tags=["sukkayodo", "japanese", "nakshatra", "lunar mansion", "asian"],
    maturity="core",
    accent_color=_a("cat_asian"),
    origin_culture="Japanese",
    tradition_period="Heian Period",
    ai_persona_key="info_sukkayodo_prompt",
))

_reg(System(
    id="tab_thai",
    name_zh="泰國占星",
    name_en="Thai Astrology",
    category="cat_asian",
    icon="🐘",
    tab_key="tab_thai",
    desc_key="desc_thai",
    spinner_key="spinner_thai",
    hint_key="sys_hint_thai",
    tags=["thai", "thailand", "animal", "asian"],
    maturity="core",
    accent_color=_a("cat_asian"),
    origin_culture="Thai",
    tradition_period="Traditional Thai",
    ai_persona_key="info_thai_prompt",
))

_reg(System(
    id="tab_laos",
    name_zh="老撾占星",
    name_en="Laos Horasat",
    category="cat_asian",
    icon="🇱🇦",
    tab_key="tab_laos",
    desc_key="desc_laos",
    spinner_key="spinner_laos",
    hint_key="sys_hint_laos",
    tags=["laos", "lao", "horasat", "sangkhom", "sikarat", "asian"],
    maturity="beta",
    accent_color=_a("cat_asian"),
    origin_culture="Lao",
    tradition_period="Traditional Lao Horasat",
    ai_persona_key="info_lao_prompt",
))

_reg(System(
    id="tab_mahabote",
    name_zh="緬甸 Mahabote",
    name_en="Burmese Mahabote",
    category="cat_asian",
    icon="🇲🇲",
    tab_key="tab_mahabote",
    desc_key="desc_mahabote",
    spinner_key="spinner_mahabote",
    hint_key="sys_hint_mahabote",
    tags=["mahabote", "burmese", "myanmar", "shan", "asian"],
    maturity="core",
    accent_color=_a("cat_asian"),
    origin_culture="Burmese",
    tradition_period="Traditional Burmese",
    ai_persona_key="info_mahabote_prompt",
    extra={
        "phase1_core_module_example": "astro.burmese.mahabote",
        "phase1_renderer_module_example": "astro.burmese.renderer",
        "phase1_features": [
            "myanmar_year_with_thingyan_cutoff",
            "eight_symbol_weekday_split_wednesday_am_pm",
            "fixed_eight_house_mapping",
            "basic_svg_wheel_renderer",
        ],
    },
))

_reg(System(
    id="tab_wariga",
    name_zh="巴厘 Wariga",
    name_en="Balinese Wariga",
    category="cat_asian",
    icon="🏝️",
    tab_key="tab_wariga",
    desc_key="desc_wariga",
    spinner_key="spinner_wariga",
    hint_key="sys_hint_wariga",
    tags=["wariga", "balinese", "bali", "wuku", "calendar", "asian"],
    maturity="core",
    accent_color=_a("cat_asian"),
    origin_culture="Balinese",
    tradition_period="Traditional Balinese Hinduism",
    ai_persona_key="info_wariga_prompt",
))

_reg(System(
    id="tab_jawa_weton",
    name_zh="爪哇 Weton",
    name_en="Javanese Weton / Primbon",
    category="cat_asian",
    icon="🏺",
    tab_key="tab_jawa_weton",
    desc_key="desc_jawa_weton",
    spinner_key="spinner_jawa_weton",
    hint_key="sys_hint_jawa_weton",
    tags=["weton", "javanese", "java", "primbon", "asian"],
    maturity="core",
    accent_color=_a("cat_asian"),
    origin_culture="Javanese",
    tradition_period="Traditional Javanese",
    ai_persona_key="info_jawa_weton_prompt",
))

_reg(System(
    id="tab_bintang_duabelas",
    name_zh="馬來伊斯蘭占星（十二星）",
    name_en="Bintang Duabelas (Twelve Stars)",
    category="cat_asian",
    icon="⭐",
    tab_key="tab_bintang_duabelas",
    desc_key="desc_bintang_duabelas",
    spinner_key="spinner_bintang_duabelas",
    hint_key="sys_hint_bintang_duabelas",
    tags=[
        "bintang duabelas",
        "twelve stars",
        "十二星",
        "十二星宮",
        "馬來伊斯蘭占星",
        "malay",
        "jawi",
        "abjad",
        "hisab nama",
        "planetary hours",
        "asian",
    ],
    maturity="beta",
    accent_color=_a("cat_asian"),
    origin_culture="Malay / Nusantara",
    tradition_period="Islamic Malay manuscripts",
    ai_persona_key="info_bintang_duabelas_prompt",
))

_reg(System(
    id="tab_kinketika",
    name_zh="馬來七星五刻占卜",
    name_en="Kinketika (Malay Time Divination)",
    category="cat_asian",
    icon="🌙",
    tab_key="tab_kinketika",
    desc_key="desc_kinketika",
    spinner_key="spinner_kinketika",
    hint_key="sys_hint_kinketika",
    tags=[
        "kinketika",
        "ketika lima",
        "bintang tujuh",
        "malay time divination",
        "nusantara",
        "bugis",
        "makassar",
        "electional",
        "asian",
    ],
    maturity="beta",
    accent_color=_a("cat_asian"),
    origin_culture="Malay / Nusantara / Bugis-Makassar",
    tradition_period="Malay Islamic manuscripts & Bugis-Makassar practice",
    ai_persona_key="info_kinketika_prompt",
))

_reg(System(
    id="tab_zurkhai",
    name_zh="蒙古祖爾海",
    name_en="Mongolian Zurkhai",
    category="cat_asian",
    icon="🇲🇳",
    tab_key="tab_zurkhai",
    desc_key="desc_zurkhai",
    spinner_key="spinner_zurkhai",
    hint_key="sys_hint_zurkhai",
    tags=["zurkhai", "mongolian", "tibetan", "buddhist", "asian"],
    maturity="core",
    accent_color=_a("cat_asian"),
    origin_culture="Mongolian",
    tradition_period="Traditional Mongolian Buddhist",
    ai_persona_key="info_zurkhai_prompt",
))

_reg(System(
    id="tab_tibetan",
    name_zh="藏傳時輪金剛占星",
    name_en="Tibetan Kalachakra",
    category="cat_asian",
    icon="🏔️",
    tab_key="tab_tibetan",
    desc_key="desc_tibetan",
    spinner_key="spinner_tibetan",
    hint_key="sys_hint_tibetan",
    sub_tabs=[
        SubTab("tibetan_subtab_mandala", "mandala"),
        SubTab("tibetan_subtab_natal",   "natal"),
        SubTab("tibetan_subtab_mewa",    "mewa"),
        SubTab("tibetan_subtab_forces",  "forces"),
        SubTab("tibetan_subtab_planets", "planets"),
    ],
    tags=["tibetan", "kalachakra", "vajrayana", "buddhist", "asian"],
    maturity="core",
    accent_color="#FF6F00",   # Tibetan saffron
    origin_culture="Tibetan",
    tradition_period="Vajrayana Buddhism",
    ai_persona_key="info_tibetan_prompt",
))

_reg(System(
    id="tab_nine_star_ki",
    name_zh="九星氣學",
    name_en="Nine Star Ki",
    category="cat_asian",
    icon="🌟",
    tab_key="tab_nine_star_ki",
    desc_key="desc_nine_star_ki",
    spinner_key="spinner_nine_star_ki",
    hint_key="sys_hint_nine_star_ki",
    tags=["nine star ki", "ki", "japanese", "chinese", "feng shui", "asian"],
    maturity="core",
    accent_color=_a("cat_asian"),
    origin_culture="Japanese / Chinese",
    tradition_period="Traditional East Asian",
    ai_persona_key="info_nine_star_ki_prompt",
))

_reg(System(
    id="tab_khmer",
    name_zh="高棉占星",
    name_en="Khmer Astrology",
    category="cat_asian",
    icon="🇰🇭",
    tab_key="tab_khmer",
    desc_key="desc_khmer",
    spinner_key="spinner_khmer",
    hint_key="sys_hint_khmer",
    tags=["khmer", "cambodian", "cambodia", "asian"],
    maturity="beta",
    accent_color=_a("cat_asian"),
    origin_culture="Khmer",
    tradition_period="Traditional Khmer",
    ai_persona_key="info_khmer_prompt",
))

_reg(System(
    id="tab_polynesian",
    name_zh="波利尼西亞星辰",
    name_en="Polynesian / Hawaiian Star Lore",
    category="cat_asian",
    icon="🌺",
    tab_key="tab_polynesian",
    desc_key="desc_polynesian",
    spinner_key="spinner_polynesian",
    hint_key="sys_hint_polynesian",
    tags=["polynesian", "hawaiian", "star lore", "navigation", "pacific"],
    maturity="beta",
    accent_color=_a("cat_asian"),
    origin_culture="Polynesian",
    tradition_period="Traditional Polynesian",
    ai_persona_key="info_polynesian_prompt",
))


# ═════════════════════════════════════════════════════════════════════════════
# cat_middle_east — 中東體系 🕌
# ═════════════════════════════════════════════════════════════════════════════

_reg(System(
    id="tab_kabbalistic",
    name_zh="卡巴拉占星",
    name_en="Kabbalistic Astrology",
    category="cat_middle_east",
    icon="✡",
    tab_key="tab_kabbalistic",
    desc_key="desc_kabbalistic",
    spinner_key="spinner_kabbalistic",
    hint_key="sys_hint_kabbalistic",
    tags=["kabbalistic", "kabbalah", "jewish", "tree of life", "sephiroth"],
    maturity="core",
    accent_color=_a("cat_middle_east"),
    origin_culture="Jewish",
    tradition_period="Medieval Kabbalah",
    ai_persona_key="info_kabbalistic_prompt",
))

_reg(System(
    id="tab_mazzalot",
    name_zh="猶太占星",
    name_en="Jewish Mazzalot",
    category="cat_middle_east",
    icon="✡",
    tab_key="tab_mazzalot",
    desc_key="desc_mazzalot",
    spinner_key="spinner_mazzalot",
    hint_key="sys_hint_mazzalot",
    sub_tabs=[
        SubTab("mazzalot_subtab_star",  "star"),
        SubTab("mazzalot_subtab_natal", "natal"),
        SubTab("mazzalot_subtab_omens", "omens"),
    ],
    tags=["mazzalot", "jewish", "talmud", "sefer yetzirah", "zodiac"],
    maturity="core",
    accent_color=_a("cat_middle_east"),
    origin_culture="Jewish",
    tradition_period="Talmudic period",
    ai_persona_key="info_mazzalot_prompt",
))

_reg(System(
    id="tab_persian",
    name_zh="波斯傳統占星",
    name_en="Persian / Sassanian Astrology",
    category="cat_middle_east",
    icon="🔯",
    tab_key="tab_persian",
    desc_key="desc_persian",
    spinner_key="spinner_persian",
    hint_key="sys_hint_persian",
    sub_tabs=[
        # app.py reuses "western_subtab_natal" for the Persian intro/natal tab
        SubTab("western_subtab_natal",       "natal"),
        SubTab("persian_firdar_title",       "firdar"),
        SubTab("persian_hyleg_title",        "hyleg"),
        SubTab("persian_profections_title",  "profections"),
        SubTab("persian_almuten_title",      "almuten"),
        SubTab("persian_royal_stars_title",  "royal_stars"),
        SubTab("persian_lots_title",         "lots"),
    ],
    tags=["persian", "sassanian", "firdar", "hyleg", "middle east"],
    maturity="core",
    accent_color=_a("cat_middle_east"),
    origin_culture="Persian",
    tradition_period="Sassanian Empire (224–651 CE)",
    ai_persona_key="info_persian_prompt",
))

_reg(System(
    id="tab_persian_deep",
    name_zh="薩珊波斯進階版",
    name_en="Sassanian Persia (Advanced)",
    category="cat_middle_east",
    icon="🏛️",
    tab_key="tab_persian_deep",
    desc_key="desc_persian_deep",
    spinner_key="spinner_persian_deep",
    hint_key="sys_hint_persian_deep",
    tags=["persian deep", "sassanian", "firdar", "almuten", "bounds", "middle east"],
    maturity="core",
    accent_color=_a("cat_middle_east"),
    origin_culture="Persian",
    tradition_period="Sassanian Empire (Advanced)",
    ai_persona_key="info_persian_deep_prompt",
))

_reg(System(
    id="tab_arabic",
    name_zh="阿拉伯占星",
    name_en="Arabic Astrology",
    category="cat_middle_east",
    icon="☪",
    tab_key="tab_arabic",
    desc_key="desc_arabic",
    spinner_key="spinner_arabic",
    hint_key="sys_hint_arabic",
    sub_tabs=[
        SubTab("arabic_subtab_chart",     "chart"),
        SubTab("arabic_subtab_lots",      "lots"),
        SubTab("arabic_subtab_picatrix",  "picatrix"),
        SubTab("arabic_subtab_shams",     "shams"),
        SubTab("arabic_subtab_reference", "reference"),
        SubTab("arabic_subtab_ms164",     "ms164"),
    ],
    tags=["arabic", "islamic", "golden age", "lunar mansion", "picatrix", "middle east"],
    maturity="core",
    accent_color=_a("cat_middle_east"),
    origin_culture="Arabic / Islamic",
    tradition_period="Islamic Golden Age (8th–13th c.)",
    ai_persona_key="info_arabic_prompt",
))

_reg(System(
    id="tab_yemeni",
    name_zh="也門占星",
    name_en="Yemeni Astrology",
    category="cat_middle_east",
    icon="🕌",
    tab_key="tab_yemeni",
    desc_key="desc_yemeni",
    spinner_key="spinner_yemeni",
    hint_key="sys_hint_yemeni",
    sub_tabs=[
        SubTab("yemeni_subtab_mandala", "mandala"),
        SubTab("yemeni_subtab_natal",   "natal"),
        SubTab("yemeni_subtab_manazil", "manazil"),
        SubTab("yemeni_subtab_omens",   "omens"),
    ],
    tags=["yemeni", "rasulid", "lunar mansion", "manazil", "middle east"],
    maturity="core",
    accent_color=_a("cat_middle_east"),
    origin_culture="Yemeni / Arab",
    tradition_period="Rasulid Dynasty (13th–15th c.)",
    ai_persona_key="info_yemeni_prompt",
))

_reg(System(
    id="tab_amazigh",
    name_zh="柏柏爾占星",
    name_en="Amazigh (Berber) Astrology",
    category="cat_africa",
    icon="ⵣ",
    tab_key="tab_amazigh",
    desc_key="desc_amazigh",
    spinner_key="spinner_amazigh",
    hint_key="sys_hint_amazigh",
    tags=["amazigh", "berber", "north africa", "fixed stars", "lots"],
    maturity="beta",
    accent_color=_a("cat_africa"),
    origin_culture="Amazigh / Berber (North Africa)",
    tradition_period="Traditional to Contemporary",
    ai_persona_key="info_amazigh_prompt",
))

_reg(System(
    id="tab_bahre_hasab",
    name_zh="衣索比亞 Bahre Hasab",
    name_en="Ethiopian Bahre Hasab",
    category="cat_africa",
    icon="⛪",
    tab_key="tab_bahre_hasab",
    desc_key="desc_bahre_hasab",
    spinner_key="spinner_bahre_hasab",
    hint_key="sys_hint_bahre_hasab",
    tags=["ethiopian", "bahre hasab", "fasika", "orthodox", "calendar", "geez", "africa"],
    maturity="beta",
    accent_color=_a("cat_africa"),
    origin_culture="Ethiopian Orthodox",
    tradition_period="Medieval to Contemporary Church Computus",
    ai_persona_key="info_bahre_hasab_prompt",
))

_reg(System(
    id="tab_picatrix_behenian",
    name_zh="Picatrix 占星魔法",
    name_en="Picatrix Star Magic",
    category="cat_middle_east",
    icon="✦",
    tab_key="tab_picatrix_behenian",
    desc_key="desc_picatrix_behenian",
    spinner_key="spinner_picatrix_behenian",
    hint_key="sys_hint_picatrix_behenian",
    tags=["picatrix", "behenian", "stellar magic", "talismans", "medieval", "middle east"],
    maturity="core",
    accent_color=_a("cat_middle_east"),
    origin_culture="Arabic / Medieval European",
    tradition_period="Medieval (Picatrix, 10th–11th c.)",
    ai_persona_key="info_picatrix_behenian_prompt",
))


_reg(System(
    id="tab_armenian",
    name_zh="亞美尼亞占星",
    name_en="Armenian Astrology",
    category="cat_obscure",
    icon="✶",
    tab_key="tab_armenian",
    desc_key="desc_armenian",
    spinner_key="spinner_armenian",
    hint_key="sys_hint_armenian",
    tags=["armenian", "haykian", "arevakhach", "obscure", "indigenous", "zodiac"],
    maturity="beta",
    accent_color=_a("cat_obscure"),
    origin_culture="Armenian Highlands",
    tradition_period="Ancient to Medieval Armenian Traditions",
    ai_persona_key="info_armenian_prompt",
))


# ═════════════════════════════════════════════════════════════════════════════
# cat_ancient — 古文明 🏺
# ═════════════════════════════════════════════════════════════════════════════

_reg(System(
    id="tab_maya",
    name_zh="瑪雅占星",
    name_en="Maya Astrology",
    category="cat_ancient",
    icon="🏺",
    tab_key="tab_maya",
    desc_key="desc_maya",
    spinner_key="spinner_maya",
    hint_key="sys_hint_maya",
    tags=["maya", "tzolkin", "haab", "mesoamerican", "ancient"],
    maturity="core",
    accent_color=_a("cat_ancient"),
    origin_culture="Maya",
    tradition_period="Classic Maya (250–900 CE)",
    ai_persona_key="info_maya_prompt",
))

_reg(System(
    id="tab_andean",
    name_zh="印加／安地斯占星",
    name_en="Inca / Andean Astrology",
    category="cat_ancient",
    icon="⛰️",
    tab_key="tab_andean",
    desc_key="desc_andean",
    spinner_key="spinner_andean",
    hint_key="sys_hint_andean",
    tags=[
        "andean", "inca", "mayu", "dark constellations", "yana phuyu",
        "qatachillay", "chakana", "southern cross", "agro-omens", "ancient",
    ],
    maturity="beta",
    accent_color=_a("cat_ancient"),
    origin_culture="Andean / Inca (Quechua)",
    tradition_period="Pre-Columbian Andes to living traditions",
    ai_persona_key="info_andean_prompt",
))

_reg(System(
    id="tab_dogon_sirius",
    name_zh="多貢天狼星宇宙學",
    name_en="Dogon Sirius Cosmology",
    category="cat_ancient",
    icon="🜂",
    tab_key="tab_dogon_sirius",
    desc_key="desc_dogon_sirius",
    spinner_key="spinner_dogon_sirius",
    hint_key="sys_hint_dogon_sirius",
    tags=["dogon", "sirius", "po tolo", "nommo", "sigui", "mali", "ancient"],
    maturity="beta",
    accent_color=_a("cat_ancient"),
    origin_culture="Dogon (Mali)",
    tradition_period="Oral tradition (recorded mainly in 20th c.)",
    ai_persona_key="info_dogon_sirius_prompt",
))

_reg(System(
    id="tab_aztec",
    name_zh="阿茲特克占星",
    name_en="Aztec Astrology",
    category="cat_ancient",
    icon="🦅",
    tab_key="tab_aztec",
    desc_key="desc_aztec",
    spinner_key="spinner_aztec",
    hint_key="sys_hint_aztec",
    tags=["aztec", "tonalpohualli", "xiuhpohualli", "mesoamerican", "ancient"],
    maturity="core",
    accent_color=_a("cat_ancient"),
    origin_culture="Aztec",
    tradition_period="Aztec Empire (14th–16th c.)",
    ai_persona_key="info_aztec_prompt",
))

_reg(System(
    id="tab_decans",
    name_zh="古埃及十度區間",
    name_en="Egyptian Decans",
    category="cat_ancient",
    icon="🏛️",
    tab_key="tab_decans",
    desc_key="desc_decans",
    spinner_key="spinner_decans",
    hint_key="sys_hint_decans",
    tags=["decans", "egyptian", "decanates", "ancient", "stars"],
    maturity="core",
    accent_color="#D4AF37",   # Egyptian gold
    origin_culture="Egyptian",
    tradition_period="Ancient Egyptian (2400 BCE +)",
    ai_persona_key="info_decans_prompt",
))

_reg(System(
    id="tab_babylonian",
    name_zh="古巴比倫占星",
    name_en="Babylonian Astrology",
    category="cat_ancient",
    icon="🏺",
    tab_key="tab_babylonian",
    desc_key="desc_babylonian",
    spinner_key="spinner_babylonian",
    hint_key="sys_hint_babylonian",
    sub_tabs=[
        SubTab("babylonian_subtab_chart", "chart"),
        SubTab("babylonian_subtab_natal", "natal"),
        SubTab("babylonian_subtab_omens", "omens"),
    ],
    tags=["babylonian", "mesopotamian", "enuma anu enlil", "omens", "ancient"],
    maturity="core",
    accent_color=_a("cat_ancient"),
    origin_culture="Babylonian",
    tradition_period="Babylonian (1800–539 BCE)",
    ai_persona_key="info_babylonian_prompt",
))

_reg(System(
    id="tab_sumerian",
    name_zh="蘇美 / 美索不達米亞占星",
    name_en="Sumerian / Mesopotamian",
    category="cat_ancient",
    icon="𒀭",
    tab_key="tab_sumerian",
    desc_key="desc_sumerian",
    spinner_key="spinner_sumerian",
    hint_key="sys_hint_sumerian",
    tags=["sumerian", "mesopotamian", "akkadian", "ancient", "cuneiform"],
    maturity="beta",
    accent_color=_a("cat_ancient"),
    origin_culture="Sumerian",
    tradition_period="Sumerian (3000–2000 BCE)",
    ai_persona_key="info_sumerian_prompt",
))

_reg(System(
    id="tab_etruscan",
    name_zh="伊特魯里亞占星",
    name_en="Etruscan Astrology",
    category="cat_ancient",
    icon="🏺",
    tab_key="tab_etruscan",
    desc_key="desc_etruscan",
    spinner_key="spinner_etruscan",
    hint_key="sys_hint_etruscan",
    tags=[
        "etruscan", "piacenza", "liver", "haruspicy", "templum",
        "fulgural divination", "tinia", "ancient", "italy",
        "bronze liver", "omens", "thunderbolt",
    ],
    maturity="beta",
    accent_color="#8C6F4E",   # Etruscan bronze
    origin_culture="Etruscan",
    tradition_period="Etruscan (7th–1st century BCE)",
    ai_persona_key="info_etruscan_prompt",
))

_reg(System(
    id="tab_astro_geomancy",
    name_zh="地占占星",
    name_en="Astronomical Geomancy",
    category="cat_middle_east",
    icon="🔮",
    tab_key="tab_astro_geomancy",
    desc_key="desc_astro_geomancy",
    spinner_key="spinner_astro_geomancy",
    hint_key="sys_hint_astro_geomancy",
    tags=[
        "geomancy", "geomantia", "gerard cremonensis", "arabic", "medieval",
        "divination", "12 houses", "figures", "middle east", "latin",
        "horary", "geomantic astrology",
    ],
    maturity="beta",
    accent_color=_a("cat_middle_east"),
    origin_culture="Arabic / Medieval Latin",
    tradition_period="Medieval Islamic-Latin (12th c., Gerard of Cremona)",
    ai_persona_key="info_astro_geomancy_prompt",
))


# ═════════════════════════════════════════════════════════════════════════════
# cat_yi_zhan — 醫占 ⚕️
# ═════════════════════════════════════════════════════════════════════════════

_reg(System(
    id="tab_medical_astrology",
    name_zh="醫學占星",
    name_en="Medical Astrology",
    category="cat_yi_zhan",
    icon="⚕️",
    tab_key="tab_medical_astrology",
    desc_key="desc_medical_astrology",
    spinner_key="spinner_medical_astrology",
    hint_key="sys_hint_medical_astrology",
    tags=["medical", "health", "body", "western", "ancient"],
    maturity="core",
    accent_color=_a("cat_yi_zhan"),
    recommended_house_system="Whole Sign",
    origin_culture="Western / Hellenistic",
    tradition_period="Ancient to Medieval",
    ai_persona_key="info_medical_astrology_prompt",
))

_reg(System(
    id="tab_shanghan_qianfa",
    name_zh="傷寒鈐法",
    name_en="Shanghan Qianfa",
    category="cat_yi_zhan",
    icon="🌿",
    tab_key="tab_shanghan_qianfa",
    desc_key="desc_shanghan_qianfa",
    spinner_key="spinner_shanghan_qianfa",
    hint_key="sys_hint_shanghan_qianfa",
    tags=["shanghan", "tcm", "zhang zhongjing", "chinese medicine", "yi_zhan"],
    maturity="core",
    accent_color=_a("cat_yi_zhan"),
    origin_culture="Chinese",
    tradition_period="Han Dynasty (Zhang Zhong-jing)",
    ai_persona_key="info_shanghan_qianfa_prompt",
))


# ═════════════════════════════════════════════════════════════════════════════
# cat_horary — 傳統卜卦占星 📜
# ═════════════════════════════════════════════════════════════════════════════

_reg(System(
    id="tab_horary",
    name_zh="傳統卜卦占星",
    name_en="Traditional Horary",
    category="cat_horary",
    icon="📜",
    tab_key="tab_horary",
    desc_key="desc_horary",
    spinner_key="spinner_horary",
    hint_key="sys_hint_horary",
    tags=["horary", "lilly", "traditional", "question", "western"],
    maturity="core",
    accent_color=_a("cat_horary"),
    recommended_house_system="Regiomontanus",
    origin_culture="Western",
    tradition_period="Medieval (William Lilly, 17th c.)",
    ai_persona_key="info_horary_prompt",
))

_reg(System(
    id="tab_sports_astrology",
    name_zh="運動占星",
    name_en="Sports Astrology",
    category="cat_horary",
    icon="🏟️",
    tab_key="tab_sports_astrology",
    desc_key="desc_sports_astrology",
    spinner_key="spinner_sports_astrology",
    hint_key="sys_hint_sports_astrology",
    tags=["sports", "horary", "frawley", "event_chart", "prediction"],
    maturity="beta",
    accent_color=_a("cat_horary"),
    recommended_house_system="Regiomontanus",
    origin_culture="Western (Traditional Horary)",
    tradition_period="Contemporary Traditional (Frawley lineage)",
    ai_persona_key="info_sports_astrology_prompt",
))

_reg(System(
    id="tab_european_geomancy",
    name_zh="歐洲地占",
    name_en="European Geomancy",
    category="cat_horary",
    icon="🜃",
    tab_key="tab_european_geomancy",
    desc_key="desc_european_geomancy",
    spinner_key="spinner_european_geomancy",
    hint_key="sys_hint_european_geomancy",
    tags=[
        "geomancy", "european geomancy", "renaissance", "shield chart",
        "house chart", "agrippa", "divination", "horary",
    ],
    maturity="beta",
    accent_color="#8A6A3A",
    origin_culture="European (Medieval/Renaissance)",
    tradition_period="Medieval to Renaissance",
    ai_persona_key="info_european_geomancy_prompt",
))

_reg(System(
    id="tab_electional",
    name_zh="擇日占星",
    name_en="Electional Astrology / Muhurta",
    category="cat_horary",
    icon="⏳",
    tab_key="tab_electional",
    desc_key="desc_electional",
    spinner_key="spinner_electional",
    hint_key="sys_hint_electional",
    tags=["electional", "muhurta", "timing", "election", "western", "vedic"],
    maturity="core",
    accent_color=_a("cat_horary"),
    origin_culture="Western / Indian",
    tradition_period="Medieval",
    ai_persona_key="info_electional_prompt",
))

# ── 弗拉德命運輪盤（Fludd Rota Simulator）────────────────────────────────────
# 靈感來自 Robert Fludd《Utriusque Cosmi Historia》(1617)
# 四層同心圓輪盤，由出生星盤行星度數驅動旋轉
_reg(System(
    id="tab_fludd_rota",
    name_zh="弗拉德命運輪盤",
    name_en="Fludd Rota Simulator",
    category="cat_western",
    icon="⚙",
    tab_key="tab_fludd_rota",
    desc_key="desc_fludd_rota",
    spinner_key="spinner_fludd_rota",
    hint_key="sys_hint_fludd_rota",
    tags=[
        "fludd", "rota", "divination wheel", "robert fludd", "renaissance",
        "rosicrucian", "hermetic", "utriusque cosmi", "occult", "mystery",
        "弗拉德", "命運輪盤", "神秘學", "文藝復興占卜", "宇宙輪",
    ],
    maturity="beta",
    accent_color="#8C6E2A",   # 古金色——弗拉德銅版雕刻風格
    origin_culture="European (Renaissance)",
    tradition_period="Renaissance (Robert Fludd, 1617)",
    ai_persona_key="info_fludd_rota_prompt",
))


# ── 煉金占星（Alchemical Astrology / Paracelsus 傳統）────────────────────────
# 嚴格以 Paracelsus《Coelum Philosophorum》《Astronomia Magna》等著作為基礎
# 行星–金屬–草藥–礦物–人體對應，Signatures 符號論，四大煉金階段
_reg(System(
    id="tab_alchemical_astrology",
    name_zh="煉金占星",
    name_en="Alchemical Astrology",
    category="cat_western",
    icon="⚗️",
    tab_key="tab_alchemical_astrology",
    desc_key="desc_alchemical_astrology",
    spinner_key="spinner_alchemical_astrology",
    hint_key="sys_hint_alchemical_astrology",
    tags=[
        "alchemy", "alchemical astrology", "paracelsus", "signatures", "doctrine of signatures",
        "signatura rerum", "coelum philosophorum", "astronomia magna", "agrippa",
        "seven metals", "seven planets", "herbs", "minerals", "nigredo", "albedo",
        "rubedo", "citrinitas", "opus magnum", "renaissance", "hermetic",
        "煉金術", "煉金占星", "帕拉塞爾蘇斯", "符號論", "七大行星", "草藥對應",
        "礦物對應", "金屬對應", "文藝復興", "鍊金術", "赫密士",
    ],
    maturity="beta",
    accent_color="#8B5C10",   # 古銅金色——煉金術文藝復興風格
    origin_culture="European (Renaissance)",
    tradition_period="Renaissance (Paracelsus, 1493–1541)",
    ai_persona_key="info_alchemical_astrology_prompt",
))

# ═════════════════════════════════════════════════════════════════════════════
# cat_western — Mundane Astrology 世俗占星 🌍
# ═════════════════════════════════════════════════════════════════════════════

_reg(System(
    id="tab_mundane",
    name_zh="世俗占星",
    name_en="Mundane Astrology",
    category="cat_western",
    icon="🌍",
    tab_key="tab_mundane",
    desc_key="desc_mundane",
    spinner_key="spinner_mundane",
    hint_key="sys_hint_mundane",
    sub_tabs=[
        SubTab("mundane_ingress",      "ingress"),
        SubTab("mundane_eclipse",      "eclipse"),
        SubTab("mundane_conjunction",  "conjunction"),
        SubTab("mundane_national",     "national"),
    ],
    tags=[
        "mundane", "world astrology", "national astrology",
        "ingress", "eclipse", "great conjunction", "jupiter saturn",
        "世俗占星", "國家占星", "入宮圖", "日月食", "木土合相", "時代",
    ],
    maturity="beta",
    accent_color="#1B4F8A",   # Deep navy for world/macro theme
    recommended_house_system="Whole Sign",
    supports_transit=True,
    origin_culture="Western / Chinese",
    tradition_period="Classical to Modern",
    ai_persona_key="info_mundane_prompt",
))


# ─────────────────────────────────────────────────────────────────────────────
# Derived helper data structures
# ─────────────────────────────────────────────────────────────────────────────

# Systems grouped by category, preserving CATEGORY_ORDER.
# 依分類分組，保留 CATEGORY_ORDER 順序。
_SYSTEMS_BY_CATEGORY: Dict[str, List[System]] = {cat: [] for cat in CATEGORY_ORDER}
for _sys in REGISTRY.values():
    _SYSTEMS_BY_CATEGORY.setdefault(_sys.category, []).append(_sys)


# ─────────────────────────────────────────────────────────────────────────────
# Public helper functions / 公開輔助函式
# ─────────────────────────────────────────────────────────────────────────────

def get_system(system_id: str) -> Optional[System]:
    """Return the System for *system_id*, or None if not found.

    依 ID 查詢占星體系。找不到則傳回 None。

    Example::

        sys = get_system("tab_western")
        if sys:
            print(sys.name_en)
    """
    return REGISTRY.get(system_id)


def get_systems_by_category(category: str) -> List[System]:
    """Return all systems in *category* in registration order.

    傳回指定分類的所有體系（保持註冊順序）。

    Example::

        western_systems = get_systems_by_category("cat_western")
    """
    return _SYSTEMS_BY_CATEGORY.get(category, [])


def search_systems(query: str, *, lang: str = "both") -> List[System]:
    """Full-text search across name, tags, and i18n keys.

    在名稱、標籤、id 等欄位執行全文搜索，不區分大小寫。

    Args:
        query: Search string. Searches name_zh, name_en, tags, and system id.
        lang:  ``"zh"`` | ``"en"`` | ``"both"`` (default).

    Returns:
        List of matching System instances.

    Example::

        hits = search_systems("印度")
        hits = search_systems("vedic", lang="en")
    """
    q = query.lower()
    results: List[System] = []
    for sys in REGISTRY.values():
        fields = [sys.id, sys.origin_culture.lower(), sys.tradition_period.lower()]
        fields.extend(t.lower() for t in sys.tags)
        if lang in ("zh", "both"):
            fields.append(sys.name_zh.lower())
        if lang in ("en", "both"):
            fields.append(sys.name_en.lower())
        if any(q in f for f in fields):
            results.append(sys)
    return results


def get_systems_by_tags(tags: List[str], *, require_all: bool = False) -> List[System]:
    """Return systems matching *tags*.

    依標籤篩選體系。

    Args:
        tags:        List of tag strings to match against.
        require_all: If True, all tags must match; otherwise any tag suffices.

    Example::

        vedic_dasha = get_systems_by_tags(["vedic", "dasha"], require_all=True)
        chinese_any = get_systems_by_tags(["chinese"])
    """
    tags_lower = [t.lower() for t in tags]
    results: List[System] = []
    for sys in REGISTRY.values():
        sys_tags = [t.lower() for t in sys.tags]
        if require_all:
            if all(tg in sys_tags for tg in tags_lower):
                results.append(sys)
        else:
            if any(tg in sys_tags for tg in tags_lower):
                results.append(sys)
    return results


def get_systems_by_maturity(maturity: str) -> List[System]:
    """Return all systems with the given maturity level.

    按成熟度篩選體系（``"core"`` / ``"beta"`` / ``"experimental"``）。
    """
    return [s for s in REGISTRY.values() if s.maturity == maturity]


def list_categories() -> List[str]:
    """Return category keys in display order.

    以顯示順序傳回所有分類鍵值。
    """
    return [c for c in CATEGORY_ORDER if c in _SYSTEMS_BY_CATEGORY]


def get_flat_system_list() -> List[System]:
    """Return all systems in category-order, then registration order.

    傳回所有體系，按 CATEGORY_ORDER 排序，再按各類別內部的註冊順序。
    """
    result: List[System] = []
    for cat in CATEGORY_ORDER:
        result.extend(_SYSTEMS_BY_CATEGORY.get(cat, []))
    return result
