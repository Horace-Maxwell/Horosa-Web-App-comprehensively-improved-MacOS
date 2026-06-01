"""
astro/vastu/engine.py — VastuEngine 核心引擎

結合 KinAstro 的 VedicChart 命盤與居所朝向方位，
計算個人化 Vastu Purusha Mandala 影響分析。

主要類別與函數：
    VastuResult           — 計算結果資料模型
    VastuEngine           — 主引擎，接受 VedicChart + house_facing
    generate_vastu_disk   — 便利函數

演算法：
    1. 從 VedicChart 取得 Lagna (asc_rashi) 與各行星星座
    2. 根據 LAGNA_RULER 確定上升主宰行星
    3. 根據 PLANET_ZONE 映射各行星到 Vastu 方位區域
    4. 根據房屋朝向計算旋轉偏移，調整方位重要性
    5. 計算 Vastu Compliance Score（0–100）
    6. 生成高亮方位字典與房間配置建議

參考典籍：Mayamata（6–13 世紀）、Manasara、Bṛhat Saṃhitā（Varāhamihira, 5 世紀）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any

from astro.vastu.constants import (
    FACING_OPTIONS_8,
    INNER_ZONES,
    LAGNA_FACING,
    LAGNA_RULER,
    MOON_ELEMENT_TIPS,
    OUTER_PADAS,
    PLANET_DIRECTION,
    PLANET_SYMBOL,
    PLANET_ZH,
    PLANET_ZH_SHORT,
    PLANET_ZONE,
    SIGN_ELEMENT,
    ZODIAC_ZH,
    ZONE_BASE_SCORE,
    ZONE_COLORS_INNER,
    ZONE_COLORS_OUTER,
    ZONE_NAMES_ZH,
)
from astro.vastu.interpretations import (
    LAGNA_VASTU_DETAILS,
    ROOM_PLACEMENT,
    get_direction_detail,
)


# ─────────────────────────────────────────────────────────────────────────────
# 資料模型
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PlanetVastuInfluence:
    """單顆行星在 Vastu 盤上的影響記錄。

    Attributes:
        planet_en:   行星英文名（如 ``"Mars"``）。
        planet_zh:   行星中文名（如 ``"火星 (Maṅgala)"``）。
        symbol:      Unicode 符號（如 ``"♂"``）。
        sign_en:     所在星座英文名。
        sign_zh:     所在星座中文名。
        vastu_zone:  Vastu 方位代碼（如 ``"S"``）。
        zone_name_zh: 方位中文名（如 ``"南方"``）。
        is_lagna_ruler: 是否為上升主宰行星。
        influence_type: 影響類型（"benefic" / "malefic" / "neutral"）。
    """

    planet_en: str
    planet_zh: str
    symbol: str
    sign_en: str
    sign_zh: str
    vastu_zone: str
    zone_name_zh: str
    is_lagna_ruler: bool = False
    influence_type: str = "neutral"


@dataclass
class VastuResult:
    """個人化 Astro-Vastu 計算結果。

    Attributes:
        lagna_sign:         上升星座英文名。
        lagna_sign_zh:      上升星座中文名。
        lagna_ruler:        上升主宰行星英文名。
        lagna_ruler_zh:     上升主宰行星中文名。
        lagna_ruler_zone:   上升主宰行星對應 Vastu 方位代碼。
        moon_sign:          月亮星座英文名。
        moon_element:       月亮星座元素（火/土/風/水）。
        house_facing:       房屋朝向方位代碼（如 ``"N"``）。
        house_facing_angle: 房屋朝向中心角度（0–360°）。
        planet_influences:  各行星 Vastu 影響列表。
        highlight_zones:    需要高亮的方位字典 {zone_code: reason_zh}。
        compliance_score:   Vastu 符合度分數（0–100）。
        recommended_facing: 建議房屋朝向文字。
        room_suggestions:   房間配置建議列表。
        moon_element_tip:   月亮元素相關 Vastu 建議。
        lagna_details:      上升星座詳細 Vastu 建議字典。
    """

    lagna_sign: str = ""
    lagna_sign_zh: str = ""
    lagna_ruler: str = ""
    lagna_ruler_zh: str = ""
    lagna_ruler_zone: str = ""
    moon_sign: str = ""
    moon_element: str = ""
    house_facing: str = "N"
    house_facing_angle: float = 0.0
    planet_influences: list[PlanetVastuInfluence] = field(default_factory=list)
    highlight_zones: dict[str, str] = field(default_factory=dict)
    compliance_score: float = 0.0
    recommended_facing: str = ""
    room_suggestions: list[dict[str, str]] = field(default_factory=list)
    moon_element_tip: str = ""
    lagna_details: dict[str, tuple[str, str]] = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# 輔助函數
# ─────────────────────────────────────────────────────────────────────────────

# 吉星（benefic）與凶星（malefic）分類
# 注意：此為簡化分類，傳統吠陀占星中水星（Mercury）為中性行星（與吉星同宮時為吉，
# 與凶星同宮時為凶）。此處將水星歸為吉星，以取其最通用的 Vastu 分類慣例，
# 即水星代表智慧、財務能力，對北方（財神方位）有正面影響。
_BENEFIC_PLANETS = {"Jupiter", "Venus", "Moon", "Mercury"}
_MALEFIC_PLANETS = {"Mars", "Saturn", "Rahu", "Ketu", "Sun"}


def _classify_influence(planet_en: str) -> str:
    """分類行星影響類型（吉/凶/中性）。

    Args:
        planet_en: 行星英文名。

    Returns:
        ``"benefic"``、``"malefic"`` 或 ``"neutral"``。
    """
    if planet_en in _BENEFIC_PLANETS:
        return "benefic"
    if planet_en in _MALEFIC_PLANETS:
        return "malefic"
    return "neutral"


def _facing_angle(facing_code: str) -> float:
    """將方位代碼轉換為中心角度（正北=0°，順時針）。

    Args:
        facing_code: 方位代碼（如 ``"N"``、``"NE"``）。

    Returns:
        角度（float），找不到時回傳 0.0。
    """
    for code, _name, angle in FACING_OPTIONS_8:
        if code == facing_code:
            return angle
    return 0.0


def _compute_compliance_score(
    highlight_zones: dict[str, str],
    planet_influences: list[PlanetVastuInfluence],
    house_facing: str,
    lagna_ruler_zone: str,
) -> float:
    """計算 Vastu Compliance Score（0–100）。

    評分邏輯：
    - 基礎分：以命盤主宰行星方位的基準分為起點
    - 加分：吉星在吉祥方位（NE、N、E）
    - 減分：凶星在關鍵吉祥方位
    - 加分：房屋朝向與上升主宰方位一致

    Args:
        highlight_zones:     高亮方位字典。
        planet_influences:   各行星影響列表。
        house_facing:        房屋朝向代碼。
        lagna_ruler_zone:    上升主宰行星 Vastu 方位代碼。

    Returns:
        Vastu 符合度分數（0.0–100.0）。
    """
    score = ZONE_BASE_SCORE.get(lagna_ruler_zone, 65.0)

    for inf in planet_influences:
        z = inf.vastu_zone
        base = ZONE_BASE_SCORE.get(z, 65.0)
        if inf.influence_type == "benefic":
            # 吉星在高基準方位 → 加分
            score += (base - 65.0) * 0.1
        elif inf.influence_type == "malefic":
            # 凶星在高基準方位 → 輕微減分
            if base >= 80.0:
                score -= 5.0

    # 房屋朝向與主宰行星方位一致加分
    if house_facing == lagna_ruler_zone:
        score += 10.0

    return max(0.0, min(100.0, score))


# ─────────────────────────────────────────────────────────────────────────────
# 主引擎
# ─────────────────────────────────────────────────────────────────────────────

class VastuEngine:
    """個人化 Astro-Vastu 計算引擎。

    結合 KinAstro VedicChart 命盤與居所朝向，
    計算個人化 Vastu Purusha Mandala 影響分析。

    Example::

        from astro.vastu.engine import VastuEngine

        engine = VastuEngine()
        result = engine.compute(
            lagna_sign="Aries",
            planet_positions={"Mars": "Scorpio", "Moon": "Cancer", ...},
            house_facing="N",
        )
    """

    def compute(
        self,
        lagna_sign: str,
        planet_positions: dict[str, str],
        house_facing: str = "N",
    ) -> VastuResult:
        """計算個人化 Vastu 影響分析。

        Args:
            lagna_sign:       上升星座英文名（如 ``"Aries"``）。
            planet_positions: 行星 → 星座映射字典
                              （如 ``{"Mars": "Scorpio", "Moon": "Cancer"}``）。
            house_facing:     房屋朝向方位代碼（預設 ``"N"``）。

        Returns:
            :class:`VastuResult` 完整計算結果。
        """
        result = VastuResult()

        # ── Lagna 基本資訊 ──
        result.lagna_sign = lagna_sign
        result.lagna_sign_zh = ZODIAC_ZH.get(lagna_sign, lagna_sign)
        result.lagna_ruler = LAGNA_RULER.get(lagna_sign, "Jupiter")
        result.lagna_ruler_zh = PLANET_ZH.get(result.lagna_ruler, result.lagna_ruler)
        result.lagna_ruler_zone = PLANET_ZONE.get(result.lagna_ruler, "NE")

        # ── 月亮資訊 ──
        moon_sign = planet_positions.get("Moon", "")
        result.moon_sign = moon_sign
        result.moon_element = SIGN_ELEMENT.get(moon_sign, "")

        # ── 房屋朝向 ──
        result.house_facing = house_facing
        result.house_facing_angle = _facing_angle(house_facing)

        # ── 行星影響分析 ──
        planet_order = [
            "Sun", "Moon", "Mars", "Mercury",
            "Jupiter", "Venus", "Saturn", "Rahu", "Ketu",
        ]
        highlight_zones: dict[str, str] = {}

        for p_en in planet_order:
            sign_en = planet_positions.get(p_en, "")
            if not sign_en:
                continue

            zone = PLANET_ZONE.get(p_en, "")
            if not zone:
                continue

            inf = PlanetVastuInfluence(
                planet_en=p_en,
                planet_zh=PLANET_ZH.get(p_en, p_en),
                symbol=PLANET_SYMBOL.get(p_en, ""),
                sign_en=sign_en,
                sign_zh=ZODIAC_ZH.get(sign_en, sign_en),
                vastu_zone=zone,
                zone_name_zh=ZONE_NAMES_ZH.get(zone, zone),
                is_lagna_ruler=(p_en == result.lagna_ruler),
                influence_type=_classify_influence(p_en),
            )
            result.planet_influences.append(inf)

            # 高亮邏輯：主宰行星方位 + 凶星在關鍵方位
            if inf.is_lagna_ruler:
                highlight_zones[zone] = (
                    f"⭐ 上升主宰 {PLANET_ZH_SHORT.get(p_en, p_en)} 方位"
                )
            elif inf.influence_type == "malefic" and zone in ("NE", "N", "E"):
                highlight_zones[zone] = (
                    f"⚠️ 凶星 {PLANET_ZH_SHORT.get(p_en, p_en)} 在吉祥方位，需補救"
                )
            elif inf.influence_type == "benefic" and zone in ("NE", "N"):
                highlight_zones.setdefault(
                    zone,
                    f"✨ 吉星 {PLANET_ZH_SHORT.get(p_en, p_en)} 加持財富靈性"
                )

        result.highlight_zones = highlight_zones

        # ── Vastu Compliance Score ──
        result.compliance_score = _compute_compliance_score(
            highlight_zones=highlight_zones,
            planet_influences=result.planet_influences,
            house_facing=house_facing,
            lagna_ruler_zone=result.lagna_ruler_zone,
        )

        # ── 建議朝向 ──
        result.recommended_facing = LAGNA_FACING.get(lagna_sign, "東方 — 通用推薦")

        # ── 房間配置建議 ──
        result.room_suggestions = list(
            ROOM_PLACEMENT.get(lagna_sign, ROOM_PLACEMENT.get("Aries", []))
        )

        # ── 月亮元素建議 ──
        result.moon_element_tip = MOON_ELEMENT_TIPS.get(
            result.moon_element, "請參考一般 Vastu 建議。"
        )

        # ── 上升星座詳細建議 ──
        result.lagna_details = dict(
            LAGNA_VASTU_DETAILS.get(lagna_sign, LAGNA_VASTU_DETAILS.get("Aries", {}))
        )

        return result

    @staticmethod
    def from_vedic_chart(vedic_chart: Any, house_facing: str = "N") -> VastuResult:
        """從 VedicChart 物件直接建立 VastuResult。

        接受 KinAstro ``VedicChart`` 資料類別，自動擷取：
        - ``asc_rashi`` 作為 Lagna 星座
        - ``planets`` 列表中各行星的星座資訊

        Args:
            vedic_chart:  KinAstro ``VedicChart`` 物件（含 ``asc_rashi``、``planets``）。
            house_facing: 房屋朝向方位代碼（預設 ``"N"``）。

        Returns:
            :class:`VastuResult` 完整計算結果。
        """
        # ── 解析 Lagna ──
        # asc_rashi 格式如 "Aries (Mesha)" 或 "Aries"
        raw_lagna = getattr(vedic_chart, "asc_rashi", "")
        lagna_sign = raw_lagna.split("(")[0].strip().split()[0]

        # ── 解析行星星座 ──
        # VedicChart.planets 是 PlanetData dataclass 列表
        # 每個 PlanetData 有 name（如 "Surya (太陽)"）和 sign（如 "Aries"）
        _NAME_MAP = {
            "Surya":   "Sun",
            "Chandra": "Moon",
            "Mangal":  "Mars",
            "Budha":   "Mercury",
            "Guru":    "Jupiter",
            "Shukra":  "Venus",
            "Shani":   "Saturn",
            "Rahu":    "Rahu",
            "Ketu":    "Ketu",
        }

        planet_positions: dict[str, str] = {}
        for p in getattr(vedic_chart, "planets", []):
            raw_name = getattr(p, "name", "")
            # 取括號前的第一個詞
            first_word = raw_name.split("(")[0].strip().split()[0]
            canonical = _NAME_MAP.get(first_word, first_word)
            sign = getattr(p, "sign", "")
            if canonical and sign:
                planet_positions[canonical] = sign

        engine = VastuEngine()
        return engine.compute(
            lagna_sign=lagna_sign,
            planet_positions=planet_positions,
            house_facing=house_facing,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 便利函數
# ─────────────────────────────────────────────────────────────────────────────

def generate_vastu_disk(
    birth_data_or_chart: Any,
    house_facing: str = "N",
    *,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    hour: Optional[int] = None,
    minute: Optional[int] = None,
    timezone: Optional[float] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    location_name: str = "",
) -> VastuResult:
    """根據命盤資料與房屋朝向生成個人化 Vastu 盤。

    支援兩種呼叫模式：

    **模式 A — 直接傳入 VedicChart**::

        from astro.vedic.indian import compute_vedic_chart
        from astro.vastu import generate_vastu_disk

        v_chart = compute_vedic_chart(...)
        result = generate_vastu_disk(v_chart, house_facing="NE")

    **模式 B — 傳入出生資料字典**::

        result = generate_vastu_disk(
            birth_data_or_chart={},  # 傳入 None 或空 dict 時使用關鍵字參數
            year=1990, month=5, day=15,
            hour=8, minute=30,
            timezone=8.0, latitude=25.033, longitude=121.565,
            house_facing="NE",
        )

    Args:
        birth_data_or_chart: ``VedicChart`` 物件，或 ``None``（配合關鍵字參數使用）。
        house_facing:        房屋朝向方位代碼（N/NE/E/SE/S/SW/W/NW）。
        year, month, day:    出生年月日（模式 B 時使用）。
        hour, minute:        出生時刻（模式 B 時使用）。
        timezone:            UTC 時區偏移（模式 B 時使用）。
        latitude, longitude: 出生地座標（模式 B 時使用）。
        location_name:       出生地名稱（可選）。

    Returns:
        :class:`VastuResult` 完整計算結果。
    """
    # 若傳入的是 VedicChart（有 asc_rashi 屬性），直接使用
    if hasattr(birth_data_or_chart, "asc_rashi"):
        return VastuEngine.from_vedic_chart(birth_data_or_chart, house_facing)

    # 否則嘗試以關鍵字參數計算 VedicChart
    if all(v is not None for v in [year, month, day, hour, minute, timezone, latitude, longitude]):
        try:
            from astro.vedic.indian import compute_vedic_chart  # 延遲匯入避免循環
            v_chart = compute_vedic_chart(
                year=year, month=month, day=day,
                hour=hour, minute=minute, timezone=timezone,
                latitude=latitude, longitude=longitude,
                location_name=location_name,
            )
            return VastuEngine.from_vedic_chart(v_chart, house_facing)
        except Exception:
            pass

    # Fallback：建立空白結果
    return VastuResult(house_facing=house_facing)
