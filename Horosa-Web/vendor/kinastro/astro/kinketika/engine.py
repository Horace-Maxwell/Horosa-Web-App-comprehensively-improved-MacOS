"""Kinketika 核心計算引擎。"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Dict, List, Literal, TypedDict

from .ketika_data import (
    ACTIVITY_CATALOGUE,
    BINTANG_TUJUH,
    FORTUNE_LABELS,
    KETIKA_LIMA,
    KetikaPeriod,
    time_to_minutes,
)

SystemKey = Literal["ketika_lima", "bintang_tujuh"]


class DailyStats(TypedDict):
    total: int
    baik: int
    nahas: int
    sederhana: int


class KinketikaEngine:
    """封裝五時刻與七星時刻查詢、活動推薦與摘要。"""

    def get_periods(self, system: SystemKey) -> List[KetikaPeriod]:
        return KETIKA_LIMA if system == "ketika_lima" else BINTANG_TUJUH

    def get_current_period(self, system: SystemKey, moment: datetime) -> KetikaPeriod:
        """依輸入時間取得當前時段。"""
        now_min = moment.hour * 60 + moment.minute
        periods = self.get_periods(system)
        for period in periods:
            start_min = time_to_minutes(period.time_start)
            end_min = time_to_minutes(period.time_end)
            if start_min < end_min and start_min <= now_min < end_min:
                return period
            if start_min >= end_min and (now_min >= start_min or now_min < end_min):
                return period
        raise ValueError(f"No matching period for system={system}, minute={now_min}, periods={len(periods)}")

    def get_activity_plan(self, system: SystemKey, activity_key: str) -> Dict[str, List[KetikaPeriod]]:
        """回傳指定活動的推薦與禁忌時段。"""
        periods = self.get_periods(system)
        return {
            "good": [p for p in periods if activity_key in p.good_activities],
            "bad": [p for p in periods if activity_key in p.bad_activities],
        }

    def get_daily_stats(self, system: SystemKey) -> DailyStats:
        periods = self.get_periods(system)
        return {
            "total": len(periods),
            "baik": sum(1 for p in periods if p.fortune == "baik"),
            "nahas": sum(1 for p in periods if p.fortune == "nahas"),
            "sederhana": sum(1 for p in periods if p.fortune == "sederhana"),
        }

    def get_daily_summary_text(self, system: SystemKey, lang: str = "zh") -> str:
        """每日總覽敘述（含吉凶統計與方向建議）。"""
        stats = self.get_daily_stats(system)
        if lang == "en":
            recommendation = (
                "Auspicious periods dominate; suitable for important undertakings."
                if stats["baik"] > stats["nahas"]
                else "Inauspicious periods dominate; proceed conservatively."
                if stats["nahas"] > stats["baik"]
                else "Mixed day; choose timing carefully."
            )
            return (
                f"Total periods: {stats['total']} | Auspicious: {stats['baik']} | "
                f"Inauspicious: {stats['nahas']} | Neutral: {stats['sederhana']}. {recommendation}"
            )

        recommendation_zh = (
            "今日吉時較多，適合推進重要事務。"
            if stats["baik"] > stats["nahas"]
            else "今日凶時偏多，宜保守行事。"
            if stats["nahas"] > stats["baik"]
            else "今日吉凶參半，宜精準擇時。"
        )
        return (
            f"今日共 {stats['total']} 段：吉 {stats['baik']}、凶 {stats['nahas']}、中平 {stats['sederhana']}。"
            f"{recommendation_zh}"
        )

    def build_structured_report(self, system: SystemKey, moment: datetime, activity_key: str) -> Dict[str, object]:
        """提供 AI 報告用的結構化資料。"""
        periods = self.get_periods(system)
        current = self.get_current_period(system, moment)
        activity_plan = self.get_activity_plan(system, activity_key)
        stats = self.get_daily_stats(system)

        return {
            "system": system,
            "system_name": "Ketika Lima" if system == "ketika_lima" else "Bintang Tujuh",
            "query_datetime": moment.isoformat(),
            "fortune_labels": FORTUNE_LABELS,
            "activity_catalogue": ACTIVITY_CATALOGUE,
            "current_period": asdict(current),
            "daily_stats": stats,
            "daily_summary": {
                "zh": self.get_daily_summary_text(system, "zh"),
                "en": self.get_daily_summary_text(system, "en"),
            },
            "activity_plan": {
                "activity_key": activity_key,
                "good": [asdict(p) for p in activity_plan["good"]],
                "bad": [asdict(p) for p in activity_plan["bad"]],
            },
            "periods": [asdict(p) for p in periods],
        }
