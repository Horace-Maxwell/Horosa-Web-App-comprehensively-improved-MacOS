"""
astro/bintang_duabelas/core.py
==============================

KinAstro 的 Bintang Duabelas 核心引擎。

此引擎將原始規則模組封裝為單一入口，
供後續 Streamlit / API / AI 解讀層直接呼叫。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, time
from typing import Literal

from .abjad import AbjadCalculator
from .azimat import AzimatGenerator
from .hisab import HisabNama
from .hours import PlanetaryHours
from .houses import TwelveHouses
from .normalization import NameNormalization, normalize_name
from .yearly import YearlyFortune

QuestionType = Literal[
    "abjad",
    "hisab",
    "disease",
    "fetal_gender",
    "marriage",
    "star_sign",
    "missing_person",
    "houses",
    "planetary_hours",
    "yearly_fortune",
    "azimat",
    "full_reading",
]


@dataclass(frozen=True)
class BintangDuabelasRequest:
    """Bintang Duabelas 問題請求。"""

    question_type: QuestionType
    primary_name: str = ""
    secondary_name: str = ""
    mother_name: str = ""
    father_name: str = ""
    target_name: str = ""
    birth_datetime: datetime | None = None
    day_name: str | None = None
    is_night: bool | None = None
    sunrise: time | None = None
    sunset: time | None = None
    hour_number: int | None = None
    azimat_purpose: str = "protection"
    script_hint: str = "auto"
    secondary_script_hint: str = "auto"
    mother_script_hint: str = "auto"
    father_script_hint: str = "auto"


class BintangDuabelasEngine:
    """Bintang Duabelas 主引擎。"""

    def __init__(self) -> None:
        self.abjad = AbjadCalculator()
        self.hisab = HisabNama()
        self.yearly = YearlyFortune()
        self.hours = PlanetaryHours()
        self.houses = TwelveHouses()
        self.azimat = AzimatGenerator()

    def normalize_name(self, name: str, script_hint: str = "auto") -> NameNormalization:
        """公開姓名正規化接口。"""
        return normalize_name(name, script_hint=script_hint)

    def _resolve_day_name(self, day_name: str | None, birth_datetime: datetime | None) -> str:
        """優先使用明確 day_name，否則由出生時間推算。"""
        if day_name:
            return day_name.lower()
        if birth_datetime is not None:
            return self.hours.weekday_to_day_key(birth_datetime.weekday())
        return "ahad"

    def name_to_abjad(self, name: str, script_hint: str = "auto") -> int:
        return self.abjad.name_to_abjad(name, script_hint=script_hint)

    def get_letter_breakdown(self, name: str, script_hint: str = "auto") -> list[tuple[str, int]]:
        return self.abjad.get_letter_breakdown(name, script_hint=script_hint)

    def hisab_nama(self, name: str, mod: int = 9, script_hint: str = "auto") -> tuple[int, int]:
        return self.hisab.hisab_nama(name, mod=mod, script_hint=script_hint)

    def diagnose_disease(
        self,
        patient_name: str,
        day_name: str | None = None,
        birth_datetime: datetime | None = None,
        script_hint: str = "auto",
    ) -> dict[str, int | str]:
        return self.hisab.diagnose_disease(
            patient_name,
            day_name=self._resolve_day_name(day_name, birth_datetime),
            script_hint=script_hint,
        )

    def predict_fetal_gender(
        self,
        mother_name: str,
        father_name: str,
        day_name: str | None = None,
        birth_datetime: datetime | None = None,
        mother_script_hint: str = "auto",
        father_script_hint: str = "auto",
    ) -> dict[str, int | str]:
        return self.hisab.predict_fetal_gender(
            mother_name,
            father_name,
            day_name=self._resolve_day_name(day_name, birth_datetime),
            mother_script_hint=mother_script_hint,
            father_script_hint=father_script_hint,
        )

    def check_marriage_compatibility(
        self,
        name1: str,
        name2: str,
        script_hint1: str = "auto",
        script_hint2: str = "auto",
    ) -> dict[str, int | str]:
        return self.hisab.check_marriage_compatibility(
            name1,
            name2,
            script_hint1=script_hint1,
            script_hint2=script_hint2,
        )

    def determine_star_sign(
        self,
        person_name: str,
        mother_name: str,
        person_script_hint: str = "auto",
        mother_script_hint: str = "auto",
    ) -> dict[str, int | str]:
        return self.hisab.determine_star_sign(
            person_name,
            mother_name,
            person_script_hint=person_script_hint,
            mother_script_hint=mother_script_hint,
        )

    def check_missing_person(
        self,
        person_name: str,
        day_name: str | None = None,
        birth_datetime: datetime | None = None,
        script_hint: str = "auto",
    ) -> dict[str, int | str]:
        return self.hisab.check_missing_person(
            person_name,
            day_name=self._resolve_day_name(day_name, birth_datetime),
            script_hint=script_hint,
        )

    def get_yearly_fortune(
        self,
        day_name: str | None = None,
        birth_datetime: datetime | None = None,
    ) -> dict[str, object]:
        return self.yearly.get_yearly_fortune(self._resolve_day_name(day_name, birth_datetime))

    def get_planetary_hours(
        self,
        birth_datetime: datetime | None = None,
        *,
        day_name: str | None = None,
        is_night: bool | None = None,
        sunrise: time | None = None,
        sunset: time | None = None,
    ) -> dict[str, object]:
        """取得行星時辰；若給定 datetime 則自動判定白天 / 夜間。"""
        if birth_datetime is not None:
            return self.hours.get_hours_for_datetime(birth_datetime, sunrise=sunrise, sunset=sunset)
        resolved_day = self._resolve_day_name(day_name, None)
        schedule = self.hours.get_hours_for_date(
            resolved_day,
            is_night=bool(is_night),
            sunrise=sunrise,
            sunset=sunset,
        )
        return {
            "phase": "night" if is_night else "day",
            "hours": schedule,
            "current_hour": schedule[0] if schedule else None,
        }

    def get_house(self, house_number: int) -> dict[str, int | str]:
        return self.houses.get_house(house_number)

    def get_all_houses(self) -> list[dict[str, int | str]]:
        return self.houses.get_all_houses()

    def get_full_reading(
        self,
        person_name: str,
        mother_name: str,
        person_script_hint: str = "auto",
        mother_script_hint: str = "auto",
    ) -> dict[str, object]:
        sign = self.determine_star_sign(
            person_name,
            mother_name,
            person_script_hint=person_script_hint,
            mother_script_hint=mother_script_hint,
        )
        house = self.houses.get_house_for_person(int(sign["sign_number"]))
        return {"star_sign": sign, "house": house}

    def generate_azimat(
        self,
        purpose: str,
        person_name: str = "",
        target_name: str = "",
    ) -> dict[str, object]:
        return self.azimat.generate_azimat(purpose, person_name=person_name, target_name=target_name)

    def list_azimat_types(self) -> list[dict[str, str]]:
        return self.azimat.list_available_types()

    def get_azimat_for_day(
        self,
        day_name: str | None = None,
        birth_datetime: datetime | None = None,
    ) -> list[dict[str, object]]:
        return self.azimat.get_azimat_for_day(self._resolve_day_name(day_name, birth_datetime))

    def run_question(self, request: BintangDuabelasRequest) -> dict[str, object]:
        """統一問題入口。"""
        normalized_inputs = {
            "primary_name": asdict(self.normalize_name(request.primary_name, request.script_hint)),
            "secondary_name": asdict(self.normalize_name(request.secondary_name, request.secondary_script_hint)),
            "mother_name": asdict(self.normalize_name(request.mother_name, request.mother_script_hint)),
            "father_name": asdict(self.normalize_name(request.father_name, request.father_script_hint)),
        }
        day_name = self._resolve_day_name(request.day_name, request.birth_datetime)

        if request.question_type == "abjad":
            result: object = {
                "total": self.name_to_abjad(request.primary_name, script_hint=request.script_hint),
                "breakdown": self.get_letter_breakdown(request.primary_name, script_hint=request.script_hint),
            }
        elif request.question_type == "hisab":
            total, remainder = self.hisab_nama(request.primary_name, script_hint=request.script_hint)
            result = {"total": total, "remainder": remainder}
        elif request.question_type == "disease":
            result = self.diagnose_disease(request.primary_name, day_name=day_name, script_hint=request.script_hint)
        elif request.question_type == "fetal_gender":
            result = self.predict_fetal_gender(
                request.primary_name,
                request.father_name,
                day_name=day_name,
                mother_script_hint=request.script_hint,
                father_script_hint=request.father_script_hint,
            )
        elif request.question_type == "marriage":
            result = self.check_marriage_compatibility(
                request.primary_name,
                request.secondary_name,
                script_hint1=request.script_hint,
                script_hint2=request.secondary_script_hint,
            )
        elif request.question_type == "star_sign":
            result = self.determine_star_sign(
                request.primary_name,
                request.mother_name,
                person_script_hint=request.script_hint,
                mother_script_hint=request.mother_script_hint,
            )
        elif request.question_type == "missing_person":
            result = self.check_missing_person(request.primary_name, day_name=day_name, script_hint=request.script_hint)
        elif request.question_type == "houses":
            result = self.get_all_houses() if request.hour_number is None else self.get_house(request.hour_number)
        elif request.question_type == "planetary_hours":
            result = self.get_planetary_hours(
                request.birth_datetime,
                day_name=day_name,
                is_night=request.is_night,
                sunrise=request.sunrise,
                sunset=request.sunset,
            )
        elif request.question_type == "yearly_fortune":
            result = self.get_yearly_fortune(day_name=day_name)
        elif request.question_type == "azimat":
            result = self.generate_azimat(
                request.azimat_purpose,
                person_name=request.primary_name,
                target_name=request.target_name,
            )
        else:
            result = self.get_full_reading(
                request.primary_name,
                request.mother_name,
                person_script_hint=request.script_hint,
                mother_script_hint=request.mother_script_hint,
            )

        return {
            "question_type": request.question_type,
            "day_name": day_name,
            "birth_datetime": request.birth_datetime,
            "normalized_inputs": normalized_inputs,
            "result": result,
        }


BintangDuabelas = BintangDuabelasEngine

__all__ = [
    "BintangDuabelas",
    "BintangDuabelasEngine",
    "BintangDuabelasRequest",
    "QuestionType",
]
