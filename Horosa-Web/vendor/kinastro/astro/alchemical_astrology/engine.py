"""
astro/alchemical_astrology/engine.py
═══════════════════════════════════════════════════════════════════════════════
煉金占星學 — 計算引擎

接受西方星盤行星黃道度數，計算：
  1. 每顆行星的煉金對應關係（金屬、草本、礦石、人體部位）
  2. 主導行星（依尊貴狀態計算）
  3. 當前煉金階段（Nigredo / Albedo / Citrinitas / Rubedo）
  4. 草本與礦石建議（前三名）
  5. 物質印記說文本

計算邏輯：
  - 行星尊貴評分：統治宮 +5，擢升宮 +4，其他 +1
  - 主導行星 = 尊貴評分最高的行星
  - 若同分，依 Chaldean 順序（土星→木星→火星→太陽→金星→水星→月亮）選取
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .correspondences import (
    ALCHEMICAL_STAGES,
    DIGNITY_SCORES,
    PLANET_CORRESPONDENCES,
    PLANET_KEYS,
    AlchemicalStageInfo,
    PlanetCorrespondence,
    longitude_to_sign_index,
)
from .interpretations import get_planet_reading, get_stage_reading
from .signatures import PLANET_SIGNATURES, PlanetSignature, get_signature_text_zh


# ─────────────────────────────────────────────────────────────────────────────
# 資料結構
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PlanetProfile:
    """單顆行星的完整煉金星盤輪廓。"""

    planet_key: str                # 行星鍵名
    symbol: str                    # 天文符號
    name_zh: str                   # 中文名
    longitude: float               # 黃道度數（輸入值）
    sign_index: int                # 星座索引（0-11）
    dignity_score: int             # 尊貴評分

    # 對應關係（來自 correspondences.py）
    metal_en: str
    metal_zh: str
    metal_latin: str
    metal_symbol: str
    herbs: list[str]
    herbs_zh: list[str]
    minerals: list[str]
    minerals_zh: list[str]
    body_part_zh: str
    temperament_zh: str
    alchemical_stage: str          # 對應的煉金階段鍵名
    stage_zh: str
    color: str

    # 物質印記說
    signature_text_zh: str

    # 個人解讀
    reading_zh: str

    # 文獻來源
    source: str


@dataclass
class AlchemicalReading:
    """完整的煉金占星解讀結果。"""

    # 輸入行星度數（原始輸入）
    planet_longitudes: dict[str, float]

    # 所有行星的輪廓
    planetary_profiles: list[PlanetProfile]

    # 主導行星
    dominant_planet: str           # planet_key
    dominant_profile: Optional[PlanetProfile]

    # 當前煉金階段（基於主導行星）
    alchemical_stage_key: str      # "nigredo" / "albedo" / "citrinitas" / "rubedo"
    alchemical_stage_info: Optional[AlchemicalStageInfo]

    # 建議（主導行星）
    herb_recommendations: list[str]       # 英文草本名（前3）
    herb_recommendations_zh: list[str]    # 中文草本名（前3）
    mineral_recommendations: list[str]    # 英文礦石名（前3）
    mineral_recommendations_zh: list[str] # 中文礦石名（前3）

    # 物質印記說文本（所有行星）
    signature_descriptions: dict[str, str]    # planet_key → 中文印記說明

    # 個人解讀摘要
    summary_zh: str
    stage_reading_zh: str

    # 尊貴評分表（供前端顯示）
    dignity_scores: dict[str, int]         # planet_key → 評分


# ─────────────────────────────────────────────────────────────────────────────
# 計算函數
# ─────────────────────────────────────────────────────────────────────────────

# Chaldean 行星順序（用於同分時的優先級：序號越大，優先級越高）
_CHALDEAN_PRIORITY: dict[str, int] = {
    "saturn": 7,
    "jupiter": 6,
    "mars": 5,
    "sun": 4,
    "venus": 3,
    "mercury": 2,
    "moon": 1,
}


def _compute_dignity_score(planet_key: str, longitude: float) -> int:
    """計算行星在指定黃道度數的尊貴評分。

    評分規則：
      - 統治宮（Domicile）：+5
      - 擢升宮（Exaltation）：+4
      - 其他（中性）：+1

    Args:
        planet_key: 行星鍵名
        longitude: 黃道度數（0–360°）

    Returns:
        尊貴評分（整數）
    """
    sign_idx = longitude_to_sign_index(longitude)
    scores = DIGNITY_SCORES.get(planet_key, {})
    return scores.get(sign_idx, 1)


def _find_dominant_planet(scores: dict[str, int]) -> str:
    """從尊貴評分字典中選出主導行星。

    同分時依 Chaldean 行星順序（土星最高）決定優先級。

    Args:
        scores: {planet_key: dignity_score}，必須非空（由 compute_reading 保證）

    Returns:
        主導行星的 planet_key

    Raises:
        ValueError: 若 scores 為空字典
    """
    if not scores:
        raise ValueError("scores 字典不可為空；compute_reading 應傳入至少一顆行星的評分。")
    # 先按評分降序，再按 Chaldean 優先級降序
    return max(
        scores.keys(),
        key=lambda k: (scores[k], _CHALDEAN_PRIORITY.get(k, 0)),
    )


def _build_planet_profile(
    planet_key: str,
    longitude: float,
    dignity_score: int,
) -> PlanetProfile:
    """構建單顆行星的完整輪廓。

    Args:
        planet_key: 行星鍵名
        longitude: 黃道度數
        dignity_score: 已計算的尊貴評分

    Returns:
        PlanetProfile 資料類別實例
    """
    corr: PlanetCorrespondence = PLANET_CORRESPONDENCES[planet_key]
    sig: Optional[PlanetSignature] = PLANET_SIGNATURES.get(planet_key)

    return PlanetProfile(
        planet_key=planet_key,
        symbol=corr.symbol,
        name_zh=corr.name_zh,
        longitude=longitude,
        sign_index=longitude_to_sign_index(longitude),
        dignity_score=dignity_score,
        metal_en=corr.metal_en,
        metal_zh=corr.metal_zh,
        metal_latin=corr.metal_latin,
        metal_symbol=corr.metal_symbol,
        herbs=list(corr.herbs),
        herbs_zh=list(corr.herbs_zh),
        minerals=list(corr.minerals),
        minerals_zh=list(corr.minerals_zh),
        body_part_zh=corr.body_part_zh,
        temperament_zh=corr.temperament_zh,
        alchemical_stage=corr.alchemical_stage.lower(),
        stage_zh=corr.stage_zh,
        color=corr.color,
        signature_text_zh=sig.signature_text_zh if sig else "",
        reading_zh=get_planet_reading(planet_key, "zh"),
        source=corr.source,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 主引擎
# ─────────────────────────────────────────────────────────────────────────────

class AlchemicalEngine:
    """煉金占星計算引擎。

    接受西方星盤的行星黃道度數字典，計算完整的煉金占星解讀。

    用法::

        engine = AlchemicalEngine()
        reading = engine.compute_reading({
            "sun": 45.0,
            "moon": 120.0,
            "mars": 270.0,
            ...
        })
    """

    def compute_reading(
        self,
        planet_longitudes: dict[str, float],
    ) -> AlchemicalReading:
        """根據行星度數計算完整煉金占星解讀。

        Args:
            planet_longitudes: 行星黃道度數字典，
                鍵名為小寫行星英文名（"sun", "moon", "mars",
                "mercury", "jupiter", "venus", "saturn"）。
                缺失行星使用預設值 0.0°。

        Returns:
            AlchemicalReading — 完整解讀結果
        """
        # 填充缺失行星（預設 0.0°）
        filled: dict[str, float] = {
            key: float(planet_longitudes.get(key, 0.0))
            for key in PLANET_KEYS
        }

        # 計算每顆行星的尊貴評分
        dignity_scores: dict[str, int] = {
            key: _compute_dignity_score(key, lon)
            for key, lon in filled.items()
        }

        # 主導行星
        dominant_key = _find_dominant_planet(dignity_scores)

        # 構建所有行星輪廓
        profiles: list[PlanetProfile] = [
            _build_planet_profile(key, filled[key], dignity_scores[key])
            for key in PLANET_KEYS
        ]

        # 找到主導行星輪廓
        dominant_profile: Optional[PlanetProfile] = next(
            (p for p in profiles if p.planet_key == dominant_key), None
        )

        # 煉金階段（基於主導行星的對應）
        stage_key = dominant_profile.alchemical_stage if dominant_profile else "nigredo"
        stage_info = ALCHEMICAL_STAGES.get(stage_key)

        # 草本與礦石建議（主導行星，前3名）
        herb_recs = dominant_profile.herbs[:3] if dominant_profile else []
        herb_recs_zh = dominant_profile.herbs_zh[:3] if dominant_profile else []
        mineral_recs = dominant_profile.minerals[:3] if dominant_profile else []
        mineral_recs_zh = dominant_profile.minerals_zh[:3] if dominant_profile else []

        # 物質印記說（所有行星）
        signatures: dict[str, str] = {
            key: get_signature_text_zh(key) for key in PLANET_KEYS
        }

        # 解讀摘要
        summary = self._build_summary(dominant_profile, stage_key, dominant_key, dignity_scores)
        stage_reading = get_stage_reading(stage_key, "zh")

        return AlchemicalReading(
            planet_longitudes=dict(filled),
            planetary_profiles=profiles,
            dominant_planet=dominant_key,
            dominant_profile=dominant_profile,
            alchemical_stage_key=stage_key,
            alchemical_stage_info=stage_info,
            herb_recommendations=herb_recs,
            herb_recommendations_zh=herb_recs_zh,
            mineral_recommendations=mineral_recs,
            mineral_recommendations_zh=mineral_recs_zh,
            signature_descriptions=signatures,
            summary_zh=summary,
            stage_reading_zh=stage_reading,
            dignity_scores=dignity_scores,
        )

    def _build_summary(
        self,
        dominant_profile: Optional[PlanetProfile],
        stage_key: str,
        dominant_key: str,
        dignity_scores: dict[str, int],
    ) -> str:
        """構建個人化煉金占星解讀摘要。"""
        if dominant_profile is None:
            return "無法生成解讀。"

        stage_info = ALCHEMICAL_STAGES.get(stage_key)
        stage_name = stage_info.name_zh if stage_info else stage_key

        # 尊貴評分最高的前三行星
        top3 = sorted(
            PLANET_KEYS,
            key=lambda k: (dignity_scores.get(k, 0), _CHALDEAN_PRIORITY.get(k, 0)),
            reverse=True,
        )[:3]
        top3_corrs = [PLANET_CORRESPONDENCES[k] for k in top3]
        top3_names = "、".join(c.name_zh for c in top3_corrs)

        return (
            f"### ✦ 煉金占星解讀（帕拉塞爾蘇斯傳統）\n\n"
            f"**主導行星**：{dominant_profile.symbol} {dominant_profile.name_zh}"
            f"（尊貴評分：{dominant_profile.dignity_score}）\n\n"
            f"**金屬對應**：{dominant_profile.metal_zh}（{dominant_profile.metal_latin}）"
            f"— {dominant_profile.metal_symbol}\n\n"
            f"**人體對應**：{dominant_profile.body_part_zh}\n\n"
            f"**氣質類型**：{dominant_profile.temperament_zh}\n\n"
            f"**煉金階段**：{stage_name}\n\n"
            f"**草本建議**：{'、'.join(dominant_profile.herbs_zh[:3])}\n\n"
            f"**礦石建議**：{'、'.join(dominant_profile.minerals_zh[:3])}\n\n"
            f"---\n\n"
            f"{dominant_profile.reading_zh}\n\n"
            f"---\n\n"
            f"*依帕拉塞爾蘇斯《偉大天文學》（1537-38）傳統，"
            f"您命盤中能量最顯著的行星群為：{top3_names}。*\n\n"
            f"*文獻來源：{dominant_profile.source}*"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 便捷函數
# ─────────────────────────────────────────────────────────────────────────────

def compute_reading(planet_longitudes: dict[str, float]) -> AlchemicalReading:
    """計算煉金占星解讀的模組級便捷函數。

    Args:
        planet_longitudes: 行星黃道度數字典

    Returns:
        AlchemicalReading — 完整解讀結果
    """
    engine = AlchemicalEngine()
    return engine.compute_reading(planet_longitudes)
