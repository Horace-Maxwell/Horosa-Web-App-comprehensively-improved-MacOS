"""
astro/bintang_duabelas/hisab.py
===============================

Bintang Duabelas 姓名數理占卜（Hisab Nama）。

規則完整承襲原始專案：
- mod 9：姓名數理 / 婚姻相合
- mod 7：疾病來源
- mod 4：胎兒性別 / 失蹤者
- mod 12：十二星宮
"""

from __future__ import annotations

from .abjad import AbjadCalculator


class HisabNama:
    """Hisab Nama 規則引擎。"""

    DAY_VALUES: dict[str, int] = {
        "ahad": 1,
        "isnin": 2,
        "selasa": 3,
        "rabu": 4,
        "khamis": 5,
        "jumaat": 6,
        "sabtu": 7,
    }

    DISEASE_ORIGINS: dict[int, dict[str, str]] = {
        1: {
            "source": "Jin (精靈)",
            "source_malay": "Penyakit daripada jin",
            "description": "The illness originates from supernatural beings (jin/jinn).",
            "description_zh": "疾病源自精靈（金）的影響。",
        },
        2: {
            "source": "Air/Wind (風邪)",
            "source_malay": "Penyakit daripada hawa",
            "description": "The illness originates from bad air or wind element.",
            "description_zh": "疾病源自風邪（不良氣流）。",
        },
        3: {
            "source": "Bewilderment (迷惑)",
            "source_malay": "Penyakit daripada hair",
            "description": "The illness originates from confusion or bewilderment.",
            "description_zh": "疾病源自迷惑或精神困擾。",
        },
        4: {
            "source": "Evil Eye (邪眼)",
            "source_malay": "Penyakit daripada kena mata orang",
            "description": "The illness originates from the evil eye of another person.",
            "description_zh": "疾病源自他人的邪眼（嫉妒之眼）。",
        },
        5: {
            "source": "Blood (血症)",
            "source_malay": "Penyakit daripada darah",
            "description": "The illness originates from blood-related issues.",
            "description_zh": "疾病源自血液相關問題。",
        },
        6: {
            "source": "Yellow Bile (黃膽)",
            "source_malay": "Penyakit sakit kuning (safra)",
            "description": "The illness is jaundice or related to yellow bile.",
            "description_zh": "疾病為黃疸或與膽汁相關。",
        },
        0: {
            "source": "Cold Blood (寒血)",
            "source_malay": "Penyakit daripada darah sejuk",
            "description": "The illness originates from cold blood.",
            "description_zh": "疾病源自寒血（血液過冷）。",
        },
    }

    FETAL_GENDER: dict[int, dict[str, str]] = {
        1: {
            "result": "Male (男)",
            "result_malay": "Anak lelaki",
            "description": "The child will be male.",
            "description_zh": "胎兒為男孩。",
        },
        2: {
            "result": "Female (女)",
            "result_malay": "Anak perempuan",
            "description": "The child will be female.",
            "description_zh": "胎兒為女孩。",
        },
        3: {
            "result": "Miscarriage (流產)",
            "result_malay": "Keguguran",
            "description": "Risk of miscarriage.",
            "description_zh": "有流產風險。",
        },
        0: {
            "result": "Twins (雙胞胎)",
            "result_malay": "Kembar",
            "description": "The pregnancy may result in twins.",
            "description_zh": "可能為雙胞胎。",
        },
    }

    MARRIAGE_COMPATIBILITY: dict[int, dict[str, str]] = {
        1: {
            "result": "Not good (不佳)",
            "result_malay": "Tidak baik, terpandang rendah",
            "description": "Not favorable; looked down upon.",
            "description_zh": "不佳，被人看低。",
        },
        2: {
            "result": "Good, moderate (良好)",
            "result_malay": "Baik, sedang",
            "description": "Good and moderate relationship.",
            "description_zh": "良好，關係穩定。",
        },
        3: {
            "result": "Starts low, ends bad (先低後差)",
            "result_malay": "Mulanya rendah, akhirnya buruk",
            "description": "Starts poorly and ends worse.",
            "description_zh": "開始低落，結尾更差。",
        },
        4: {
            "result": "Good, husband strong (良好，夫強)",
            "result_malay": "Baik, laki kuat",
            "description": "Good marriage; the husband is strong.",
            "description_zh": "良好的婚姻，丈夫強壯。",
        },
        5: {
            "result": "Wealthy but divorced (富裕但離婚)",
            "result_malay": "Rumah kemewahan atau talak",
            "description": "Wealthy household but risk of divorce.",
            "description_zh": "家庭富裕但有離婚風險。",
        },
        6: {
            "result": "Starts good, ends sad (先好後悲)",
            "result_malay": "Mulanya baik, akhirnya dukacita",
            "description": "Starts well but ends in sorrow.",
            "description_zh": "開始美好，結尾悲傷。",
        },
        7: {
            "result": "Grand household (大宅之家)",
            "result_malay": "Rumah besar, hampir terbentam dan sebahagia",
            "description": "Grand household, blessed and fortunate.",
            "description_zh": "大宅之家，有福有運。",
        },
        8: {
            "result": "Household reversed (家運反覆)",
            "result_malay": "Rumah terbalik",
            "description": "The household is unstable and reversed.",
            "description_zh": "家運反覆不定。",
        },
        0: {
            "result": "Separation and conflict (分離爭執)",
            "result_malay": "Berpindah dan berbantah dan berperang",
            "description": "Characterized by moving, quarreling, and fighting.",
            "description_zh": "以搬遷、爭吵和衝突為特徵。",
        },
    }

    STAR_SIGNS: dict[int, dict[str, str]] = {
        1: {"name_ar": "الحمل", "name_en": "Aries (Al-Hamal)", "name_zh": "白羊宮", "planet": "Mars (المريخ)", "element": "Fire (火)", "nature": "Hot and Dry (熱燥)"},
        2: {"name_ar": "الثور", "name_en": "Taurus (Al-Thawr)", "name_zh": "金牛宮", "planet": "Venus (الزهرة)", "element": "Earth (土)", "nature": "Cold and Dry (冷燥)"},
        3: {"name_ar": "الجوزاء", "name_en": "Gemini (Al-Jawza)", "name_zh": "雙子宮", "planet": "Mercury (عطارد)", "element": "Air (風)", "nature": "Hot and Moist (熱濕)"},
        4: {"name_ar": "السرطان", "name_en": "Cancer (Al-Saratan)", "name_zh": "巨蟹宮", "planet": "Moon (القمر)", "element": "Water (水)", "nature": "Cold and Moist (冷濕)"},
        5: {"name_ar": "الأسد", "name_en": "Leo (Al-Asad)", "name_zh": "獅子宮", "planet": "Sun (الشمس)", "element": "Fire (火)", "nature": "Hot and Dry (熱燥)"},
        6: {"name_ar": "السنبلة", "name_en": "Virgo (Al-Sunbulah)", "name_zh": "室女宮", "planet": "Mercury (عطارد)", "element": "Earth (土)", "nature": "Cold and Dry (冷燥)"},
        7: {"name_ar": "الميزان", "name_en": "Libra (Al-Mizan)", "name_zh": "天秤宮", "planet": "Venus (الزهرة)", "element": "Air (風)", "nature": "Hot and Moist (熱濕)"},
        8: {"name_ar": "العقرب", "name_en": "Scorpio (Al-Aqrab)", "name_zh": "天蠍宮", "planet": "Mars (المريخ)", "element": "Water (水)", "nature": "Cold and Moist (冷濕)"},
        9: {"name_ar": "القوس", "name_en": "Sagittarius (Al-Qaws)", "name_zh": "人馬宮", "planet": "Jupiter (المشتري)", "element": "Fire (火)", "nature": "Hot and Dry (熱燥)"},
        10: {"name_ar": "الجدي", "name_en": "Capricorn (Al-Jady)", "name_zh": "摩羯宮", "planet": "Saturn (زحل)", "element": "Earth (土)", "nature": "Cold and Dry (冷燥)"},
        11: {"name_ar": "الدلو", "name_en": "Aquarius (Al-Dalw)", "name_zh": "寶瓶宮", "planet": "Saturn (زحل)", "element": "Air (風)", "nature": "Hot and Moist (熱濕)"},
        12: {"name_ar": "الحوت", "name_en": "Pisces (Al-Hut)", "name_zh": "雙魚宮", "planet": "Jupiter (المشتري)", "element": "Water (水)", "nature": "Cold and Moist (冷濕)"},
    }

    def __init__(self) -> None:
        self.abjad = AbjadCalculator()

    def hisab_nama(self, name: str, mod: int = 9, script_hint: str = "auto") -> tuple[int, int]:
        """回傳（總值, 餘數）。"""
        total = self.abjad.name_to_abjad(name, script_hint=script_hint)
        return total, total % mod

    def diagnose_disease(
        self,
        patient_name: str,
        day_name: str = "ahad",
        script_hint: str = "auto",
    ) -> dict[str, int | str]:
        """依姓名與星期推算疾病來源。"""
        name_value = self.abjad.name_to_abjad(patient_name, script_hint=script_hint)
        day_value = self.DAY_VALUES.get(day_name.lower(), 1)
        total = name_value + day_value + 10
        remainder = total % 7
        return {
            "name_value": name_value,
            "day": day_name,
            "day_value": day_value,
            "total": total,
            "remainder": remainder,
            **self.DISEASE_ORIGINS.get(remainder, self.DISEASE_ORIGINS[1]),
        }

    def predict_fetal_gender(
        self,
        mother_name: str,
        father_name: str,
        day_name: str = "ahad",
        mother_script_hint: str = "auto",
        father_script_hint: str = "auto",
    ) -> dict[str, int | str]:
        """依父母姓名與星期推算胎兒性別。"""
        mother_value = self.abjad.name_to_abjad(mother_name, script_hint=mother_script_hint)
        father_value = self.abjad.name_to_abjad(father_name, script_hint=father_script_hint)
        day_value = self.DAY_VALUES.get(day_name.lower(), 1)
        total = mother_value + father_value + day_value
        remainder = total % 4
        return {
            "mother_name_value": mother_value,
            "father_name_value": father_value,
            "day": day_name,
            "day_value": day_value,
            "total": total,
            "remainder": remainder,
            **self.FETAL_GENDER.get(remainder, self.FETAL_GENDER[1]),
        }

    def check_marriage_compatibility(
        self,
        name1: str,
        name2: str,
        script_hint1: str = "auto",
        script_hint2: str = "auto",
    ) -> dict[str, int | str]:
        """婚姻相合計算。"""
        value1 = self.abjad.name_to_abjad(name1, script_hint=script_hint1)
        value2 = self.abjad.name_to_abjad(name2, script_hint=script_hint2)
        combined = value1 + value2
        remainder = (combined - 7) % 9
        return {
            "name1_value": value1,
            "name2_value": value2,
            "combined": combined,
            "remainder": remainder,
            **self.MARRIAGE_COMPATIBILITY.get(remainder, self.MARRIAGE_COMPATIBILITY[1]),
        }

    def determine_star_sign(
        self,
        person_name: str,
        mother_name: str,
        person_script_hint: str = "auto",
        mother_script_hint: str = "auto",
    ) -> dict[str, int | str]:
        """依本人與母名計算十二星宮。"""
        person_value = self.abjad.name_to_abjad(person_name, script_hint=person_script_hint)
        mother_value = self.abjad.name_to_abjad(mother_name, script_hint=mother_script_hint)
        combined = person_value + mother_value
        remainder = combined % 12 or 12
        return {
            "person_name_value": person_value,
            "mother_name_value": mother_value,
            "combined": combined,
            "sign_number": remainder,
            **self.STAR_SIGNS.get(remainder, self.STAR_SIGNS[1]),
        }

    def check_missing_person(
        self,
        person_name: str,
        day_name: str = "ahad",
        script_hint: str = "auto",
    ) -> dict[str, int | str]:
        """失蹤 / 遠行者占斷。"""
        name_value = self.abjad.name_to_abjad(person_name, script_hint=script_hint)
        day_value = self.DAY_VALUES.get(day_name.lower(), 1)
        total = name_value + day_value
        remainder = total % 4
        results: dict[int, dict[str, str]] = {
            1: {"status": "Alive, worried (在世，憂心)", "status_malay": "Menunggu, bersusah hati", "description": "The person is alive but anxious and troubled.", "description_zh": "此人在世但心中憂慮不安。"},
            2: {"status": "Detained or sick (被拘或患病)", "status_malay": "Tertutup atau sakit", "description": "The person is detained or ill.", "description_zh": "此人被拘禁或正在患病。"},
            3: {"status": "In good company (結伴同行)", "status_malay": "Dalam kepulan, berkasih sayang", "description": "The person is in good company and cared for.", "description_zh": "此人與他人結伴，受到關愛。"},
            0: {"status": "Returning soon (即將歸來)", "status_malay": "Hampir pulang, mendapat laba", "description": "The person is about to return with profit.", "description_zh": "此人即將帶著收穫歸來。"},
        }
        return {
            "name_value": name_value,
            "day": day_name,
            "day_value": day_value,
            "total": total,
            "remainder": remainder,
            **results.get(remainder, results[1]),
        }


__all__ = ["HisabNama"]
