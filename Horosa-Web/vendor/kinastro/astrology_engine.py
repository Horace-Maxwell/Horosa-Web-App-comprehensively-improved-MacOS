"""Core calculation and interpretation engine for KaiYuan Five Planets Divination."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from data_loader import KaiyuanDataLoader, PlanetOmenDict


TWENTY_EIGHT_MANSIONS = [
    "角", "亢", "氐", "房", "心", "尾", "箕",
    "斗", "牛", "女", "虛", "危", "室", "壁",
    "奎", "婁", "胃", "昴", "畢", "觜", "參",
    "井", "鬼", "柳", "星", "張", "翼", "軫",
]

TWELVE_PALACES = [
    "命宮", "兄弟", "夫妻", "子女", "財帛", "疾厄",
    "遷移", "奴僕", "官祿", "田宅", "福德", "父母",
]

TRACKED_BODIES = ["日", "月", "填星", "歲星", "熒惑", "太白", "辰星"]

HOUSE_MEANINGS: Dict[str, str] = {
    "命宮": "核心性格、生命主軸與自我定位。",
    "兄弟": "手足、同儕、合作與競爭關係。",
    "夫妻": "伴侶關係、婚姻品質與情感承諾。",
    "子女": "創造力、子女緣、作品與後續發展。",
    "財帛": "收入、資源管理、風險偏好與財務習慣。",
    "疾厄": "壓力、健康弱點與日常保養議題。",
    "遷移": "外出、轉換、跨域與環境適應。",
    "奴僕": "團隊、同事、下屬與協作效率。",
    "官祿": "職涯、責任、名望與社會角色。",
    "田宅": "居住、資產、家族基礎與安全感。",
    "福德": "精神狀態、內在安定與福分累積。",
    "父母": "長輩、師承、規範與支持系統。",
}

GOOD_HINTS = ("吉", "福", "喜", "安", "平", "熟", "赦", "慶", "利", "和")
CAUTION_HINTS = ("凶", "兵", "死", "喪", "憂", "亂", "疾", "旱", "水", "災", "饑")


@dataclass
class PlanetPosition:
    planet: str
    mansion: str
    house: str
    source: str = "simulated"


class ChineseAstrologyEngine:
    """Compute mansion/house placements and produce KaiYuan omen interpretations."""

    def __init__(self, omen_data: Optional[PlanetOmenDict] = None, loader: Optional[KaiyuanDataLoader] = None):
        self.loader = loader or KaiyuanDataLoader()
        self.omen_data: PlanetOmenDict = omen_data or self.loader.load_all()

    @staticmethod
    def parse_datetime(dt_input: str | datetime) -> datetime:
        if isinstance(dt_input, datetime):
            return dt_input
        try:
            return datetime.strptime(dt_input, "%Y-%m-%d %H:%M")
        except ValueError as exc:
            raise ValueError("日期時間格式錯誤，請使用 'YYYY-MM-DD HH:MM'。") from exc

    def compute_positions(
        self,
        dt_input: str | datetime,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        manual_mode: bool = False,
        manual_mansions: Optional[Dict[str, str]] = None,
        manual_houses: Optional[Dict[str, str]] = None,
    ) -> Dict[str, PlanetPosition]:
        """
        Return body placements in 28 mansions + 12 palaces.

        Note: current automatic mode uses deterministic simulation fallback
        when ephemeris is unavailable.
        """
        dt_obj = self.parse_datetime(dt_input)
        manual_mansions = manual_mansions or {}
        manual_houses = manual_houses or {}

        if manual_mode:
            return self._manual_positions(manual_mansions, manual_houses)

        return self._simulated_positions(dt_obj, latitude=latitude, longitude=longitude)

    def get_omen_text(self, planet: str, mansion: str) -> Optional[str]:
        canonical_planet = self.loader.normalize_planet_name(planet)
        mansion_key = self.loader.normalize_mansion_name(mansion)

        if canonical_planet not in self.omen_data:
            self.omen_data = self.loader.load_all()
        return self.omen_data.get(canonical_planet, {}).get(mansion_key)

    def interpret_house(self, planet: str, house: str, mansion: str) -> str:
        domain = HOUSE_MEANINGS.get(house, "此宮位象徵該主題的現況與變化。")
        omen = self.get_omen_text(planet, mansion)

        if not omen:
            return (
                f"【{planet}在{house}】{domain}"
                "目前無《開元占經》對應宿文，建議以整體盤勢與現實情境綜合判讀。"
            )

        level = self._estimate_tone(omen)
        return (
            f"【{planet}在{house}】{domain}"
            f" 綜合落宿（{mansion}宿）訊號，傾向「{level}」。"
            " 建議把占象當作風險提示，配合可驗證的行動規劃。"
        )

    def detect_special_patterns(self, positions: Dict[str, PlanetPosition]) -> List[Dict[str, str]]:
        patterns: List[Dict[str, str]] = []

        five_planets = ["填星", "歲星", "熒惑", "太白", "辰星"]
        present_five_planets = [p for p in five_planets if p in positions]
        five_mansions = {positions[p].mansion for p in present_five_planets}
        if len(five_mansions) == 1 and len(present_five_planets) == 5:
            same_mansion = next(iter(five_mansions))
            patterns.append(
                {
                    "name": "五星聚一宿",
                    "detail": f"五行五星同聚 {same_mansion} 宿，象徵事件集中、短期主題強化。",
                }
            )

        if "日" in positions and "月" in positions and positions["日"].house == positions["月"].house:
            patterns.append(
                {
                    "name": "日月同宮",
                    "detail": f"日月同在{positions['日'].house}，主內外議題同步放大，需平衡情緒與決策。",
                }
            )

        if positions.get("填星") and positions["填星"].mansion == "角":
            patterns.append(
                {
                    "name": "填星守角",
                    "detail": "填星守角，多見制度、秩序與權責重整議題。",
                }
            )

        if positions.get("歲星") and positions["歲星"].mansion == "心":
            patterns.append(
                {
                    "name": "歲星守心",
                    "detail": "歲星守心，重視政令正當性與核心決策品質。",
                }
            )

        return patterns

    def generate_integrated_report(self, positions: Dict[str, PlanetPosition]) -> Dict[str, object]:
        per_planet: List[Dict[str, str]] = []

        for planet in TRACKED_BODIES:
            if planet not in positions:
                continue

            pos = positions[planet]
            omen = self.get_omen_text(planet, pos.mansion)
            house_reading = self.interpret_house(planet, pos.house, pos.mansion)

            per_planet.append(
                {
                    "planet": planet,
                    "mansion": pos.mansion,
                    "house": pos.house,
                    "source": pos.source,
                    "raw_omen": omen or "（此星體目前無對應宿文）",
                    "house_interpretation": house_reading,
                    "tone": self._estimate_tone((omen or "") + house_reading),
                }
            )

        patterns = self.detect_special_patterns(positions)
        summary = self._build_summary(per_planet, patterns)

        return {
            "positions": {k: vars(v) for k, v in positions.items()},
            "per_planet": per_planet,
            "patterns": patterns,
            "summary": summary,
            "notice": "本工具為歷史文本占例整理與研究用途，請以理性參考，不作唯一決策依據。",
        }

    def _manual_positions(
        self,
        manual_mansions: Dict[str, str],
        manual_houses: Dict[str, str],
    ) -> Dict[str, PlanetPosition]:
        positions: Dict[str, PlanetPosition] = {}

        for body in TRACKED_BODIES:
            mansion = self.loader.normalize_mansion_name(manual_mansions.get(body, "角"))
            house = manual_houses.get(body, "命宮").strip()

            if mansion not in TWENTY_EIGHT_MANSIONS:
                mansion = "角"
            if house not in TWELVE_PALACES:
                house = "命宮"

            positions[body] = PlanetPosition(
                planet=body,
                mansion=mansion,
                house=house,
                source="manual",
            )

        return positions

    def _simulated_positions(
        self,
        dt_obj: datetime,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, PlanetPosition]:
        """Deterministic fallback placement (placeholder when ephemeris is not configured)."""
        seed = (
            dt_obj.year * 10000
            + dt_obj.month * 100
            + dt_obj.day
            + dt_obj.hour
            + dt_obj.minute
        )

        # Keep deterministic but spread out bodies.
        offsets = {
            "日": 0,
            "月": 4,
            "填星": 8,
            "歲星": 12,
            "熒惑": 16,
            "太白": 20,
            "辰星": 24,
        }

        geo_bias = 0
        if latitude is not None and longitude is not None:
            geo_bias = int((abs(latitude) + abs(longitude)) * 10) % 28

        positions: Dict[str, PlanetPosition] = {}
        for body in TRACKED_BODIES:
            mansion_idx = (seed + offsets[body] + geo_bias) % len(TWENTY_EIGHT_MANSIONS)
            house_idx = (seed // 7 + offsets[body]) % len(TWELVE_PALACES)
            positions[body] = PlanetPosition(
                planet=body,
                mansion=TWENTY_EIGHT_MANSIONS[mansion_idx],
                house=TWELVE_PALACES[house_idx],
                source="simulated",
            )

        return positions

    def _estimate_tone(self, text: str) -> str:
        good_score = sum(text.count(k) for k in GOOD_HINTS)
        caution_score = sum(text.count(k) for k in CAUTION_HINTS)

        if good_score > caution_score:
            return "偏吉"
        if caution_score > good_score:
            return "偏凶"
        return "中性"

    def _build_summary(self, per_planet: List[Dict[str, str]], patterns: List[Dict[str, str]]) -> str:
        if not per_planet:
            return "暫無可用盤勢資料。"

        tone_count = {"偏吉": 0, "偏凶": 0, "中性": 0}
        for item in per_planet:
            tone_count[item["tone"]] += 1

        if tone_count["偏凶"] > tone_count["偏吉"]:
            trend = "整體訊號偏向風險管理，宜保守決策、分散壓力。"
        elif tone_count["偏吉"] > tone_count["偏凶"]:
            trend = "整體訊號偏向可把握機會，但仍需設定停損與檢核點。"
        else:
            trend = "整體訊號吉凶參半，建議以現實數據與資源條件為主。"

        if patterns:
            pattern_names = "、".join(p["name"] for p in patterns)
            return f"{trend} 偵測到特殊格局：{pattern_names}。"
        return trend
