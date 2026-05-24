"""interpretations/arabic_lots.py

Arabic Lots 解讀資料（中英雙語）基礎庫。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LotInterpretation:
    lot_id: str
    title_zh: str
    title_en: str
    interpretation_zh: str
    interpretation_en: str
    source: str
    mythological_reference: str


BASE_INTERPRETATIONS: dict[str, LotInterpretation] = {
    "lot_fortune": LotInterpretation(
        lot_id="lot_fortune",
        title_zh="幸運點",
        title_en="Lot of Fortune",
        interpretation_zh="主身體福祉、物質際遇與生活可得資源。與吉星合、受吉相時，常見財務與機運提升。",
        interpretation_en="Represents bodily fortune, material conditions, and accessible resources. Benefic aspects often increase prosperity and opportunity.",
        source="Al-Biruni, Book of Instruction in the Elements of the Art of Astrology",
        mythological_reference="Tyche / Fortuna",
    ),
    "lot_spirit": LotInterpretation(
        lot_id="lot_spirit",
        title_zh="精神點",
        title_en="Lot of Spirit",
        interpretation_zh="主意志、使命感與主動選擇。與太陽、火星互動佳時，行動力與決策力更強。",
        interpretation_en="Signifies will, vocation, and intentional action. Supportive ties to Sun/Mars increase agency and determination.",
        source="Al-Biruni, Book of Instruction in the Elements of the Art of Astrology",
        mythological_reference="Nous / Daimon",
    ),
    "lot_marriage": LotInterpretation(
        lot_id="lot_marriage",
        title_zh="婚姻點",
        title_en="Lot of Marriage",
        interpretation_zh="主伴侶關係、婚配契約與結盟品質。與第七宮與金星狀態需合併判讀。",
        interpretation_en="Indicates partnership contracts, marriage quality, and alliance dynamics. Read together with 7th-house and Venus condition.",
        source="Al-Biruni and later medieval Arabic tradition",
        mythological_reference="Venus–Saturn relational covenant symbolism",
    ),
}


def get_lot_interpretation(lot_id: str) -> LotInterpretation | None:
    """依 lot_id 取得基礎解讀。"""

    return BASE_INTERPRETATIONS.get(lot_id)
