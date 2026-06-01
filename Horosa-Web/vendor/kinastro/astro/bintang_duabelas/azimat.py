"""
astro/bintang_duabelas/azimat.py
================================

Bintang Duabelas Azimat 產生器。
"""

from __future__ import annotations


class AzimatGenerator:
    """Azimat / talisman 資料產生器。"""

    AZIMAT_CATALOG: dict[str, dict[str, object]] = {
        "protection": {"name_en": "General Protection", "name_zh": "一般保護", "name_malay": "Perlindungan Am", "verse_ar": "بسم الله الرحمن الرحيم\nاللهم إنى أستودعك نفسي وأهلي ومالي\nبحق كهيعص حم عسق\nوبحق بسم الله الذي لا يضر مع اسمه شيء\nفي الأرض ولا في السماء وهو السميع العليم", "instructions_en": "Write on white paper with saffron ink. Fold and wrap in clean white cloth. Carry on your person at all times.", "instructions_zh": "用藏紅花墨水寫在白紙上。折疊後用白布包裹。隨身攜帶。", "timing": {"day": "Monday (Isnin)", "planet_hour": "Moon (القمر)", "best_time": "After Subuh prayer"}},
        "love": {"name_en": "Love & Affection", "name_zh": "愛情與感情", "name_malay": "Kasih Sayang", "verse_ar": "بسم الله الرحمن الرحيم\nوألقيت عليك محبة مني ولتصنع على عيني\nاللهم اجعل قلب فلان يحب فلان\nبحق يس والقرآن الحكيم", "instructions_en": "Write with rose water and saffron ink on paper. Prepare during Venus hour on Friday. Fumigate with oud/agarwood incense.", "instructions_zh": "用玫瑰水和藏紅花墨水寫在紙上。在星期五金星時辰製作。以沉香薰香。", "timing": {"day": "Friday (Jumaat)", "planet_hour": "Venus (الزهرة)", "best_time": "First Venus hour after sunrise"}},
        "healing": {"name_en": "Healing & Recovery", "name_zh": "治療與康復", "name_malay": "Penyembuhan", "verse_ar": "بسم الله الرحمن الرحيم\nوننزل من القرآن ما هو شفاء ورحمة للمؤمنين\nاللهم رب الناس أذهب البأس\nاشف أنت الشافي لا شفاء إلا شفاؤك\nشفاء لا يغادر سقماً", "instructions_en": "Write with saffron ink on clean paper. Dissolve in clean water (zamzam if available). The patient drinks the water. Best prepared on Wednesday during Mercury hour.", "instructions_zh": "用藏紅花墨水寫在乾淨的紙上。溶解在乾淨的水中（如有滲滲泉水更佳）。患者飲用此水。最佳在星期三水星時辰製作。", "timing": {"day": "Wednesday (Rabu)", "planet_hour": "Mercury (عطارد)", "best_time": "Mercury hour, Cancer moon if possible"}},
        "pregnancy": {"name_en": "Pregnancy Protection", "name_zh": "孕期保護", "name_malay": "Perlindungan Kehamilan", "verse_ar": "بسم الله الرحمن الرحيم\nإن الله يمسك السماوات والأرض أن تزولا\nولئن زالتا إن أمسكهما من أحد من بعده\nإنه كان حليماً غفوراً\nاللهم احفظ ما في بطن فلانة", "instructions_en": "Write on deerskin or clean paper with musk and saffron ink. Tie around the pregnant woman's waist. Prepare during Moon hour on Monday.", "instructions_zh": "用麝香和藏紅花墨水寫在鹿皮或乾淨紙上。繫在孕婦腰間。在星期一月亮時辰製作。", "timing": {"day": "Monday (Isnin)", "planet_hour": "Moon (القمر)", "best_time": "Moon hour on Monday, waxing moon phase"}},
        "business": {"name_en": "Business Success", "name_zh": "事業成功", "name_malay": "Kejayaan Perniagaan", "verse_ar": "بسم الله الرحمن الرحيم\nوقل رب أدخلني مدخل صدق\nوأخرجني مخرج صدق\nواجعل لي من لدنك سلطاناً نصيراً\nاللهم ارزقني رزقاً واسعاً حلالاً طيباً", "instructions_en": "Write with saffron and musk ink on paper. Place in the cash register or main entrance of business. Prepare during Jupiter hour on Thursday.", "instructions_zh": "用藏紅花和麝香墨水寫在紙上。放在收銀機或店鋪主入口。在星期四木星時辰製作。", "timing": {"day": "Thursday (Khamis)", "planet_hour": "Jupiter (المشتري)", "best_time": "First Jupiter hour on Thursday"}},
        "enemy_protection": {"name_en": "Enemy Protection (避小人/避邪術)", "name_zh": "避小人／避邪術", "name_malay": "Perlindungan dari Musuh", "verse_ar": "بسم الله الرحمن الرحيم\nأقبل ولا تخف نجوت من القوم الظالمين\nلا تخافا إنني معكما أسمع وأرى\nوعلى الله فليتوكل المؤمنون\nاللهم إنى أستودعك من شر كل ذي شر", "instructions_en": "Based on p.23 & p.34: Write on paper with musk, saffron, and rose water. Fumigate with agarwood incense. If possible, engrave on an emerald or turquoise ring. Wear the ring on the little finger. Prepare on Friday during Venus hour.", "instructions_zh": "根據第23、34頁：用麝香、藏紅花和玫瑰水寫在紙上。以沉香薰香。如可能，刻在翡翠或綠松石戒指上。戒指戴在小指上。在星期五金星時辰製作。", "timing": {"day": "Friday (Jumaat)", "planet_hour": "Venus (الزهرة)", "best_time": "Friday, Venus hour, full moon night if possible"}},
        "travel_safety": {"name_en": "Travel Safety (旅行平安)", "name_zh": "旅行平安", "name_malay": "Keselamatan Perjalanan", "verse_ar": "بسم الله الرحمن الرحيم\nسبحان الذي سخر لنا هذا وما كنا له مقرنين\nوإنا إلى ربنا لمنقلبون\nاللهم إنا نسألك في سفرنا هذا البر والتقوى\nومن العمل ما ترضى", "instructions_en": "Write on paper with saffron ink. Fold and carry in a pouch during travel. Read the verse before departing. Prepare during Jupiter hour on Thursday.", "instructions_zh": "用藏紅花墨水寫在紙上。折疊放入旅行袋中攜帶。出發前誦讀此經文。在星期四木星時辰製作。", "timing": {"day": "Thursday (Khamis)", "planet_hour": "Jupiter (المشتري)", "best_time": "Thursday, Jupiter hour, before departure"}},
        "family_harmony": {"name_en": "Family Harmony (家庭和睦)", "name_zh": "家庭和睦", "name_malay": "Keharmonian Keluarga", "verse_ar": "بسم الله الرحمن الرحيم\nومن آياته أن خلق لكم من أنفسكم أزواجاً\nلتسكنوا إليها وجعل بينكم مودة ورحمة\nإن في ذلك لآيات لقوم يتفكرون\nاللهم ألف بين قلوبنا", "instructions_en": "Write with saffron and rose water on paper. Place above the main entrance of the home. Prepare on Monday during Moon hour for emotional harmony.", "instructions_zh": "用藏紅花和玫瑰水寫在紙上。放在家中主入口上方。在星期一月亮時辰製作，以促進情感和諧。", "timing": {"day": "Monday (Isnin)", "planet_hour": "Moon (القمر)", "best_time": "Monday, Moon hour, waxing moon"}},
        "exam_success": {"name_en": "Exam & Career Success (考試/事業成功)", "name_zh": "考試／事業成功", "name_malay": "Kejayaan Peperiksaan dan Kerjaya", "verse_ar": "بسم الله الرحمن الرحيم\nرب اشرح لي صدري ويسر لي أمري\nواحلل عقدة من لساني يفقهوا قولي\nرب زدني علماً\nاللهم انفعني بما علمتني وعلمني ما ينفعني", "instructions_en": "Write with saffron ink on clean paper. Carry in pocket during examinations or interviews. Prepare during Mercury hour on Wednesday for intellect.", "instructions_zh": "用藏紅花墨水寫在乾淨的紙上。考試或面試時放在口袋中。在星期三水星時辰製作，以增強智力。", "timing": {"day": "Wednesday (Rabu)", "planet_hour": "Mercury (عطارد)", "best_time": "Wednesday, Mercury hour"}},
        "wealth": {"name_en": "Wealth & Sustenance (招財/Rezeki)", "name_zh": "招財／財運", "name_malay": "Rezeki dan Kekayaan", "verse_ar": "بسم الله الرحمن الرحيم\nوفي السماء رزقكم وما توعدون\nفورب السماء والأرض إنه لحق\nمثل ما أنكم تنطقون\nاللهم ارزقني رزقاً حلالاً طيباً واسعاً\nبغير حساب", "instructions_en": "Write with saffron and musk ink on paper. Place in wallet, safe, or main entrance of business. Prepare during Jupiter hour on Thursday. Fumigate with frankincense (luban).", "instructions_zh": "用藏紅花和麝香墨水寫在紙上。放在錢包、保險箱或店鋪主入口。在星期四木星時辰製作。以乳香薰香。", "timing": {"day": "Thursday (Khamis)", "planet_hour": "Jupiter (المشتري)", "best_time": "Thursday, Jupiter hour, waxing moon"}},
        "child_protection": {"name_en": "Child Protection", "name_zh": "兒童保護", "name_malay": "Perlindungan Kanak-Kanak", "verse_ar": "بسم الله الرحمن الرحيم\nأعوذ بكلمات الله التامة من كل شيطان وهامة\nومن كل عين لامة\nاللهم احفظ أولادنا من كل سوء", "instructions_en": "Write on paper and place in the child's pillow or hang above the crib. Prepare during Sun hour on Sunday.", "instructions_zh": "寫在紙上放入兒童枕頭中或掛在搖籃上方。在星期日太陽時辰製作。", "timing": {"day": "Sunday (Ahad)", "planet_hour": "Sun (الشمس)", "best_time": "Sunday, Sun hour"}},
        "debt_relief": {"name_en": "Debt Relief", "name_zh": "還債解困", "name_malay": "Pelepasan Hutang", "verse_ar": "بسم الله الرحمن الرحيم\nاللهم اكفني بحلالك عن حرامك\nوأغنني بفضلك عمن سواك\nاللهم إني أعوذ بك من الهم والحزن\nوالعجز والكسل والبخل والجبن\nوضلع الدين وغلبة الرجال", "instructions_en": "Write with saffron ink and carry on person. Read the prayer after every obligatory prayer. Prepare during Jupiter hour.", "instructions_zh": "用藏紅花墨水書寫並隨身攜帶。每次禮拜後誦讀此祈禱文。在木星時辰製作。", "timing": {"day": "Thursday (Khamis)", "planet_hour": "Jupiter (المشتري)", "best_time": "Thursday, after Asr prayer"}},
    }

    def generate_azimat(
        self,
        purpose: str,
        person_name: str = "",
        target_name: str = "",
    ) -> dict[str, object]:
        """依目的產生 azimat。"""
        if purpose not in self.AZIMAT_CATALOG:
            return {
                "error": f"Unknown azimat type: '{purpose}'",
                "available_types": ", ".join(sorted(self.AZIMAT_CATALOG.keys())),
            }

        azimat = dict(self.AZIMAT_CATALOG[purpose])
        azimat["purpose"] = purpose
        azimat["person_name"] = person_name
        azimat["target_name"] = target_name
        if person_name:
            verse = str(azimat["verse_ar"])
            verse = verse.replace("فلان", person_name)
            verse = verse.replace("فلانة", person_name)
            azimat["verse_ar"] = verse
        return azimat

    def list_available_types(self) -> list[dict[str, str]]:
        """列出可用 azimat 類型。"""
        return [
            {
                "type": key,
                "name_en": str(info["name_en"]),
                "name_zh": str(info["name_zh"]),
                "name_malay": str(info["name_malay"]),
            }
            for key, info in self.AZIMAT_CATALOG.items()
        ]

    def get_azimat_for_day(self, day_name: str) -> list[dict[str, object]]:
        """找出建議在某天製作的 azimat。"""
        day_map = {
            "ahad": "Sunday",
            "isnin": "Monday",
            "selasa": "Tuesday",
            "rabu": "Wednesday",
            "khamis": "Thursday",
            "jumaat": "Friday",
            "sabtu": "Saturday",
        }
        day_en = day_map.get(day_name.lower(), "")
        results: list[dict[str, object]] = []
        for key, info in self.AZIMAT_CATALOG.items():
            timing = info["timing"]
            if day_en.lower() in str(timing["day"]).lower():
                results.append(
                    {
                        "type": key,
                        "name_en": str(info["name_en"]),
                        "name_zh": str(info["name_zh"]),
                        "timing": timing,
                    }
                )
        return results


__all__ = ["AzimatGenerator"]
