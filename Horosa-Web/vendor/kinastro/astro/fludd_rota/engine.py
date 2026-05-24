"""
astro/fludd_rota/engine.py
═══════════════════════════════════════════════════════════════════════════════
Fludd Rota 占卜輪盤 — 計算引擎

將行星黃道度數映射至四層輪盤的旋轉偏移角，
並根據對齊結果生成占卜解讀文本。

層級與行星對應：
  Ring 1 (outermost) — 字母 + 符號  ← 太陽 (☉) + 上升點 (ASC)
  Ring 2             — 羅馬數字     ← 月亮 (☽)
  Ring 3             — 行星符號     ← 水星 (☿) + 金星 (♀)
  Ring 4 (innermost) — 命運區域     ← 火星 (♂) × 0.4 + 木星 (♃) × 0.35 + 土星 (♄) × 0.25

南北交點（☊☋）作為解讀調節因子（modifier），
不控制旋轉，但影響吉凶解讀的傾向。

偏移公式（以 360° 模運算）：
  ring1_offset = (sun * 0.6 + asc * 0.4) % 360
  ring2_offset = moon % 360
  ring3_offset = (mercury * 0.55 + venus * 0.45) % 360
  ring4_offset = (mars * 0.40 + jupiter * 0.35 + saturn * 0.25) % 360

偏移角代表各層輪盤從初始位置逆時針旋轉的角度，
最終決定哪個符號出現在頂部指針（north pointer）位置。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from .constants import (
    NODE_MODIFIER,
    RING1_MEANINGS,
    RING1_SYMBOLS,
    RING2_MEANINGS,
    RING2_NUMBERS,
    RING3_MEANINGS,
    RING3_PLANETS,
    RING4_ZONE_MEANINGS,
    RING4_ZONE_NAMES,
    RING4_ZONES,
)

# Ecliptic arc (in degrees) within which a lunar node is considered
# conjunct the Sun and thus actively modifies the reading direction.
_NODE_INFLUENCE_THRESHOLD_DEG: float = 30.0
_LIFESPAN_NODE_BONUS: dict[str, int] = {
    "north_node": 5,
    "south_node": -5,
    "neutral": 0,
}


# ─────────────────────────────────────────────────────────────────────────────
# 資料結構
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RotaConfig:
    """出生星盤行星度數輸入（黃道經度 0–360°）。

    所有欄位均為黃道度數，預設值 0.0。
    north_node / south_node 為月交點，用於調節解讀方向。
    """

    # ── 主控行星 ─────────────────────────────────────────────
    sun: float = 0.0          # ☉ 太陽  → Ring 1 主控
    moon: float = 0.0         # ☽ 月亮  → Ring 2 主控
    mercury: float = 0.0      # ☿ 水星  → Ring 3 共控
    venus: float = 0.0        # ♀ 金星  → Ring 3 共控
    mars: float = 0.0         # ♂ 火星  → Ring 4 共控
    jupiter: float = 0.0      # ♃ 木星  → Ring 4 共控
    saturn: float = 0.0       # ♄ 土星  → Ring 4 共控

    # ── 上升點 ───────────────────────────────────────────────
    ascendant: float = 0.0    # ASC 上升點 → Ring 1 次控

    # ── 月交點（調節因子）────────────────────────────────────
    north_node: float = 0.0   # ☊ 北交點 → 解讀方向調節
    south_node: float = 180.0 # ☋ 南交點 → 解讀方向調節（通常與北交點相差 180°）

    # ── 擴充保留欄位（未來：命運點 Lot of Fortune、凱龍星等）
    extra: dict = field(default_factory=dict)


@dataclass
class RotaReading:
    """輪盤解讀結果。"""

    # 各層對應符號（頂部指針所指）
    ring1_symbol: str = ""    # 字母 / 符號
    ring2_number: str = ""    # 羅馬數字
    ring3_planet: str = ""    # 行星符號
    ring4_zone: str = ""      # 命運區域星座符號
    ring4_zone_name: str = "" # 命運區域中文名稱

    # 各層旋轉偏移角（度）
    ring1_offset: float = 0.0
    ring2_offset: float = 0.0
    ring3_offset: float = 0.0
    ring4_offset: float = 0.0

    # 月交點調節方向
    node_modifier_key: str = "neutral"  # "north_node" | "south_node" | "neutral"

    # 各層解讀文本
    ring1_text: str = ""
    ring2_text: str = ""
    ring3_text: str = ""
    ring4_text: str = ""
    node_text: str = ""

    # 綜合解讀
    summary: str = ""

    # 壽命趨勢（靈性參考）
    lifespan_score: int = 0
    lifespan_level: str = ""
    lifespan_text: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# 核心計算
# ─────────────────────────────────────────────────────────────────────────────

def compute_ring_offsets(config: RotaConfig) -> dict[str, float]:
    """計算四層輪盤的旋轉偏移角（0–360°）。

    Returns:
        dict with keys "ring1", "ring2", "ring3", "ring4"
    """
    ring1 = (config.sun * 0.6 + config.ascendant * 0.4) % 360
    ring2 = config.moon % 360
    ring3 = (config.mercury * 0.55 + config.venus * 0.45) % 360
    ring4 = (
        config.mars * 0.40
        + config.jupiter * 0.35
        + config.saturn * 0.25
    ) % 360
    return {
        "ring1": ring1,
        "ring2": ring2,
        "ring3": ring3,
        "ring4": ring4,
    }


def _symbol_at_pointer(
    symbols: list[str],
    offset_deg: float,
) -> tuple[str, int]:
    """根據偏移角計算頂部指針指向的符號。

    輪盤從 12 點鐘位置開始，順時針排列符號。
    偏移角代表輪盤旋轉量（正數 = 逆時針）。
    指針固定在頂部（0° / 12 o'clock）。

    Returns:
        (symbol, index)
    """
    n = len(symbols)
    segment_deg = 360.0 / n
    # 輪盤旋轉 offset_deg 後，指針指向哪個索引
    # 指針在 0°，符號 i 在角度 (i * segment_deg - offset_deg) % 360
    # 最近 0° 的符號即為當前符號
    idx = int(offset_deg / segment_deg) % n
    return symbols[idx], idx


def _node_modifier_key(config: RotaConfig) -> str:
    """判斷月交點對解讀的影響方向。

    規則：
    - 若北交點與太陽的黃道距離 < 30°，北交點加持吉運
    - 若南交點與太陽的黃道距離 < 30°，南交點帶來淨化課題
    - 否則中性
    """
    def arc(a: float, b: float) -> float:
        diff = abs(a - b) % 360
        return min(diff, 360 - diff)

    north_arc = arc(config.north_node, config.sun)
    south_arc = arc(config.south_node, config.sun)

    if north_arc < _NODE_INFLUENCE_THRESHOLD_DEG:
        return "north_node"
    if south_arc < _NODE_INFLUENCE_THRESHOLD_DEG:
        return "south_node"
    return "neutral"


def compute_reading(config: RotaConfig) -> RotaReading:
    """根據行星配置計算完整的輪盤解讀。

    Args:
        config: RotaConfig — 行星黃道度數輸入

    Returns:
        RotaReading — 完整解讀結果（含各層符號、偏移、文本、綜合結論）
    """
    offsets = compute_ring_offsets(config)

    # ── 各層指向符號 ─────────────────────────────────────────
    ring1_sym, _r1i = _symbol_at_pointer(RING1_SYMBOLS, offsets["ring1"])
    ring2_num, _r2i = _symbol_at_pointer(RING2_NUMBERS, offsets["ring2"])
    ring3_plt, _r3i = _symbol_at_pointer(RING3_PLANETS, offsets["ring3"])
    ring4_zn,  _r4i = _symbol_at_pointer(RING4_ZONES,   offsets["ring4"])

    # ── 月交點調節 ───────────────────────────────────────────
    node_key = _node_modifier_key(config)

    # ── 各層解讀文本 ─────────────────────────────────────────
    r1_text = RING1_MEANINGS.get(ring1_sym, ring1_sym)
    r2_text = RING2_MEANINGS.get(ring2_num, ring2_num)
    r3_text = RING3_MEANINGS.get(ring3_plt, ring3_plt)
    r4_text = RING4_ZONE_MEANINGS.get(ring4_zn, ring4_zn)
    node_text = NODE_MODIFIER.get(node_key, "")
    zone_name = RING4_ZONE_NAMES.get(ring4_zn, ring4_zn)
    lifespan_score, lifespan_level, lifespan_text = _estimate_lifespan(
        ring4_zn=ring4_zn,
        ring3_plt=ring3_plt,
        node_key=node_key,
    )

    # ── 綜合解讀 ─────────────────────────────────────────────
    summary = _build_summary(
        ring1_sym=ring1_sym,
        ring2_num=ring2_num,
        ring3_plt=ring3_plt,
        ring4_zn=ring4_zn,
        zone_name=zone_name,
        r1_text=r1_text,
        r2_text=r2_text,
        r3_text=r3_text,
        r4_text=r4_text,
        node_key=node_key,
        node_text=node_text,
        lifespan_level=lifespan_level,
        lifespan_score=lifespan_score,
        lifespan_text=lifespan_text,
        config=config,
    )

    return RotaReading(
        ring1_symbol=ring1_sym,
        ring2_number=ring2_num,
        ring3_planet=ring3_plt,
        ring4_zone=ring4_zn,
        ring4_zone_name=zone_name,
        ring1_offset=offsets["ring1"],
        ring2_offset=offsets["ring2"],
        ring3_offset=offsets["ring3"],
        ring4_offset=offsets["ring4"],
        node_modifier_key=node_key,
        ring1_text=r1_text,
        ring2_text=r2_text,
        ring3_text=r3_text,
        ring4_text=r4_text,
        node_text=node_text,
        lifespan_score=lifespan_score,
        lifespan_level=lifespan_level,
        lifespan_text=lifespan_text,
        summary=summary,
    )


def _estimate_lifespan(
    ring4_zn: str,
    ring3_plt: str,
    node_key: str,
) -> tuple[int, str, str]:
    """根據輪盤結果估計壽命趨勢（僅供靈性參考）。"""
    zone_base: dict[str, int] = {
        "♈": 52,
        "♉": 68,
        "♊": 56,
        "♋": 62,
        "♌": 60,
        "♍": 65,
        "♎": 58,
        "♏": 54,
        "♐": 57,
        "♑": 66,
        "♒": 59,
        "♓": 61,
    }
    planet_bonus: dict[str, int] = {
        "☽": 2,
        "☿": 1,
        "♀": 3,
        "☉": 2,
        "♂": -2,
        "♃": 4,
        "♄": 0,
    }
    node_bonus = _LIFESPAN_NODE_BONUS.get(node_key, 0)
    raw_score = zone_base.get(ring4_zn, 58) + planet_bonus.get(ring3_plt, 0) + node_bonus
    score = max(35, min(90, raw_score))

    if score >= 75:
        level = "偏長壽"
        detail = "命盤顯示生命韌性較高，宜持續規律作息與長期養生。"
    elif score >= 65:
        level = "中上壽"
        detail = "整體壽元趨勢平穩偏佳，重點在節律與壓力管理。"
    elif score >= 55:
        level = "中壽"
        detail = "壽命走勢屬中段，保持運動、飲食與情緒平衡可穩步提升。"
    else:
        level = "需重視養生"
        detail = "此期顯示耗損偏高，建議更積極地調整生活習慣與休養節奏。"

    text = f"{level}（壽命趨勢分數：{score}/100）。{detail}（僅供靈性探索參考）"
    return score, level, text


def _build_summary(
    ring1_sym: str,
    ring2_num: str,
    ring3_plt: str,
    ring4_zn: str,
    zone_name: str,
    r1_text: str,
    r2_text: str,
    r3_text: str,
    r4_text: str,
    node_key: str,
    node_text: str,
    lifespan_score: int,
    lifespan_level: str,
    lifespan_text: str,
    config: RotaConfig,
) -> str:
    """組合四層解讀成綜合占卜文本（弗拉德古典風格）。"""

    from astro.fludd_rota.constants import RING3_PLANET_NAMES

    planet_name = RING3_PLANET_NAMES.get(ring3_plt, ring3_plt)

    node_line = ""
    if node_key == "north_node":
        node_line = "\n\n✦ **業力加持**：" + node_text
    elif node_key == "south_node":
        node_line = "\n\n✦ **業力課題**：" + node_text

    summary = (
        f"### ✦ 弗拉德命運輪盤解讀\n\n"
        f"**宇宙之輪旋轉，指針停於四重奧秘之上——**\n\n"
        f"**第一層（字母 {ring1_sym}）**：{r1_text}\n\n"
        f"**第二層（{ring2_num} 宮）**：{r2_text}\n\n"
        f"**第三層（{planet_name} {ring3_plt}）**：{r3_text}\n\n"
        f"**第四層（{zone_name} {ring4_zn}）**：{r4_text}"
        f"{node_line}\n\n"
        f"✦ **壽命趨勢**：{lifespan_level}（{lifespan_score}/100）\n\n"
        f"{lifespan_text}\n\n"
        f"---\n"
        f"**綜合天機**：字母「{ring1_sym}」象徵的宇宙原力，"
        f"與月亮第 {ring2_num} 宮的命運潮汐相遇，"
        f"在{planet_name}的引導之下，"
        f"最終流向{zone_name}命運區域所示之路。"
        f"此刻宇宙的訊息是——"
        f"{'在業力加持下勇於把握，吉運相隨。' if node_key == 'north_node' else '以清醒之心面對課題，業力自此淨化。' if node_key == 'south_node' else '保持中道，順應天時，命運之輪自有安排。'}"
    )
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# 便捷函數：從 dict 創建 RotaConfig
# ─────────────────────────────────────────────────────────────────────────────

def config_from_dict(data: dict) -> RotaConfig:
    """從字典創建 RotaConfig。

    Args:
        data: 包含行星度數的字典，鍵名為行星英文名（小寫）。

    Returns:
        RotaConfig 實例
    """
    return RotaConfig(
        sun=float(data.get("sun", 0.0)),
        moon=float(data.get("moon", 0.0)),
        mercury=float(data.get("mercury", 0.0)),
        venus=float(data.get("venus", 0.0)),
        mars=float(data.get("mars", 0.0)),
        jupiter=float(data.get("jupiter", 0.0)),
        saturn=float(data.get("saturn", 0.0)),
        ascendant=float(data.get("ascendant", 0.0)),
        north_node=float(data.get("north_node", 0.0)),
        south_node=float(data.get("south_node", 180.0)),
    )
