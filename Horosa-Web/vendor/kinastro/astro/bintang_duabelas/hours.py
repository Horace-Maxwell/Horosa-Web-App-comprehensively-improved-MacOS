"""
astro/bintang_duabelas/hours.py
===============================

Bintang Duabelas 行星時辰模組。

保留原典的日間 / 夜間 12 時辰吉凶序列，
並額外提供日期時間排程，方便 KinAstro 後續 UI 直接繪圖。
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

_DAY_ORDER: tuple[str, ...] = ("isnin", "selasa", "rabu", "khamis", "jumaat", "sabtu", "ahad")
_DEFAULT_SUNRISE = time(6, 0)
_DEFAULT_SUNSET = time(18, 0)


class PlanetaryHours:
    """每日 / 夜間十二時辰資料與排程。"""

    BAIK = "baik"
    NAHS = "nahs"
    CAMPUR = "bercampur"

    PLANET_NAMES: dict[str, dict[str, str]] = {
        "al-shams": {"ar": "الشمس", "en": "Sun", "zh": "太陽"},
        "al-zuhrah": {"ar": "الزهرة", "en": "Venus", "zh": "金星"},
        "al-utarid": {"ar": "عطارد", "en": "Mercury", "zh": "水星"},
        "al-qamar": {"ar": "القمر", "en": "Moon", "zh": "月亮"},
        "zuhal": {"ar": "زحل", "en": "Saturn", "zh": "土星"},
        "al-mushtari": {"ar": "المشتري", "en": "Jupiter", "zh": "木星"},
        "al-mirrikh": {"ar": "المريخ", "en": "Mars", "zh": "火星"},
    }

    PLANET_FORTUNE: dict[str, str] = {
        "al-shams": BAIK,
        "al-zuhrah": BAIK,
        "al-utarid": CAMPUR,
        "al-qamar": BAIK,
        "zuhal": NAHS,
        "al-mushtari": BAIK,
        "al-mirrikh": NAHS,
    }

    DAYTIME_HOURS: dict[str, list[tuple[str, str]]] = {
        "ahad": [("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS)],
        "isnin": [("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK)],
        "selasa": [("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK)],
        "rabu": [("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS)],
        "khamis": [("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR)],
        "jumaat": [("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK)],
        "sabtu": [("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-utarid", CAMPUR)],
    }

    # 夜間表保留原始專案與 1957 手冊轉錄內容；
    # 即使個別序列看似不符合一般七曜輪轉，也不主動「修正」，
    # 以確保 KinAstro 版本忠於來源文本。
    NIGHTTIME_HOURS: dict[str, list[tuple[str, str]]] = {
        "malam_ahad": [("al-utarid", CAMPUR), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK)],
        "malam_isnin": [("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR)],
        "malam_selasa": [("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK)],
        "malam_rabu": [("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK)],
        "malam_khamis": [("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mirrikh", NAHS), ("al-mushtari", BAIK), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS)],
        "malam_jumaat": [("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK), ("zuhal", NAHS), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK)],
        "malam_sabtu": [("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("zuhal", NAHS), ("al-qamar", BAIK), ("al-mushtari", BAIK), ("al-mirrikh", NAHS), ("al-shams", BAIK), ("al-zuhrah", BAIK), ("al-utarid", CAMPUR), ("al-qamar", BAIK)],
    }

    @staticmethod
    def weekday_to_day_key(value: int) -> str:
        """Python weekday (Mon=0) 轉 Malay day key。"""
        return _DAY_ORDER[value % 7]

    def _format_hour(self, hour_num: int, planet_key: str, fortune: str) -> dict[str, int | str]:
        """格式化單一時辰資料。"""
        names = self.PLANET_NAMES.get(planet_key, {})
        labels = {
            self.BAIK: {"en": "Auspicious", "zh": "吉", "malay": "Baik"},
            self.NAHS: {"en": "Inauspicious", "zh": "凶", "malay": "Nahs"},
            self.CAMPUR: {"en": "Mixed", "zh": "混合", "malay": "Bercampur"},
        }
        label = labels.get(fortune, labels[self.CAMPUR])
        return {
            "hour": hour_num,
            "planet_key": planet_key,
            "planet_ar": names.get("ar", ""),
            "planet_en": names.get("en", ""),
            "planet_zh": names.get("zh", ""),
            "fortune": fortune,
            "fortune_en": label["en"],
            "fortune_zh": label["zh"],
            "fortune_malay": label["malay"],
        }

    def get_daytime_hours(self, day_name: str) -> list[dict[str, int | str]]:
        """取得某日白天十二時辰。"""
        hours = self.DAYTIME_HOURS.get(day_name.lower(), self.DAYTIME_HOURS["ahad"])
        return [self._format_hour(index + 1, planet, fortune) for index, (planet, fortune) in enumerate(hours)]

    def get_nighttime_hours(self, night_name: str) -> list[dict[str, int | str]]:
        """取得某夜十二時辰。"""
        hours = self.NIGHTTIME_HOURS.get(night_name.lower(), self.NIGHTTIME_HOURS["malam_ahad"])
        return [self._format_hour(index + 1, planet, fortune) for index, (planet, fortune) in enumerate(hours)]

    def get_current_hour_fortune(
        self,
        day_name: str,
        hour_number: int,
        is_night: bool = False,
    ) -> dict[str, int | str]:
        """取得指定時辰結果。"""
        if hour_number < 1 or hour_number > 12:
            return {"error": "Hour must be between 1 and 12."}
        if is_night:
            hours = self.get_nighttime_hours(f"malam_{day_name.lower()}")
        else:
            hours = self.get_daytime_hours(day_name)
        return hours[hour_number - 1]

    def find_auspicious_hours(self, day_name: str, is_night: bool = False) -> list[dict[str, int | str]]:
        """篩出吉時。"""
        hours = self.get_nighttime_hours(f"malam_{day_name.lower()}") if is_night else self.get_daytime_hours(day_name)
        return [entry for entry in hours if entry["fortune"] == self.BAIK]

    def get_hours_for_date(
        self,
        day_input: str | date | datetime,
        *,
        is_night: bool = False,
        sunrise: time | None = None,
        sunset: time | None = None,
    ) -> list[dict[str, object]]:
        """依日期建立帶起訖時間的十二時辰排程。"""
        sunrise = sunrise or _DEFAULT_SUNRISE
        sunset = sunset or _DEFAULT_SUNSET

        if isinstance(day_input, datetime):
            base_date = day_input.date()
            day_key = self.weekday_to_day_key(day_input.weekday())
        elif isinstance(day_input, date):
            base_date = day_input
            day_key = self.weekday_to_day_key(day_input.weekday())
        else:
            base_date = date.today()
            day_key = day_input.lower()

        if is_night:
            night_key = f"malam_{self.weekday_to_day_key((base_date.weekday() + 1) % 7)}"
            start_dt = datetime.combine(base_date, sunset)
            end_dt = datetime.combine(base_date + timedelta(days=1), sunrise)
            template = self.get_nighttime_hours(night_key)
            sequence_name = night_key
        else:
            start_dt = datetime.combine(base_date, sunrise)
            end_dt = datetime.combine(base_date, sunset)
            template = self.get_daytime_hours(day_key)
            sequence_name = day_key

        step = (end_dt - start_dt) / 12
        schedule: list[dict[str, object]] = []
        for index, item in enumerate(template):
            slot_start = start_dt + step * index
            slot_end = start_dt + step * (index + 1)
            schedule.append(
                {
                    **item,
                    "sequence": sequence_name,
                    "is_night": is_night,
                    "start": slot_start,
                    "end": slot_end,
                }
            )
        return schedule

    def get_hours_for_datetime(
        self,
        moment: datetime,
        *,
        sunrise: time | None = None,
        sunset: time | None = None,
    ) -> dict[str, object]:
        """依實際時間判定白天 / 夜間序列與當前時辰。"""
        sunrise = sunrise or _DEFAULT_SUNRISE
        sunset = sunset or _DEFAULT_SUNSET
        sunrise_today = datetime.combine(moment.date(), sunrise)
        sunset_today = datetime.combine(moment.date(), sunset)

        if sunrise_today <= moment < sunset_today:
            schedule = self.get_hours_for_date(moment.date(), is_night=False, sunrise=sunrise, sunset=sunset)
            phase = "day"
        elif moment >= sunset_today:
            schedule = self.get_hours_for_date(moment.date(), is_night=True, sunrise=sunrise, sunset=sunset)
            phase = "night"
        else:
            previous_date = moment.date() - timedelta(days=1)
            schedule = self.get_hours_for_date(previous_date, is_night=True, sunrise=sunrise, sunset=sunset)
            phase = "night"

        current = next((entry for entry in schedule if entry["start"] <= moment < entry["end"]), schedule[-1])
        return {
            "phase": phase,
            "moment": moment,
            "current_hour": current,
            "hours": schedule,
        }


__all__ = ["PlanetaryHours"]
