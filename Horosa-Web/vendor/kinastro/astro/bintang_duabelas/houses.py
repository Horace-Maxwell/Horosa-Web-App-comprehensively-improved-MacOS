"""
astro/bintang_duabelas/houses.py
================================

Bintang Duabelas 十二宮（12 Rumah）資料。
"""

from __future__ import annotations


class TwelveHouses:
    """十二宮資料查詢。"""

    HOUSES: dict[int, dict[str, str]] = {
        1: {"name_ar": "بيت الحياة", "name_en": "House of Life (Bayt al-Hayah)", "name_zh": "生命宮", "name_malay": "Rumah Kehidupan", "sign": "Aries (الحمل)", "planet": "Mars (المريخ)", "element": "Fire (火)", "domain_en": "Life, personality, physical appearance, character.", "domain_zh": "生命、性格、外貌、品性。", "interpretation_en": "This house represents one's life force, personality, and physical constitution. The native is brave and energetic, with a strong will. Mars bestows courage and determination. The wise say: one born under this sign is a leader by nature.", "interpretation_zh": "此宮代表一個人的生命力、性格與體質。命主勇敢而精力充沛，意志堅強。火星賦予勇氣與決心。智者曰：此星下所生之人，天生為領袖。"},
        2: {"name_ar": "بيت المال", "name_en": "House of Wealth (Bayt al-Mal)", "name_zh": "財帛宮", "name_malay": "Rumah Harta", "sign": "Taurus (الثور)", "planet": "Venus (الزهرة)", "element": "Earth (土)", "domain_en": "Wealth, property, livelihood, material possessions.", "domain_zh": "財富、產業、生計、物質財產。", "interpretation_en": "This house governs wealth and material possessions. Venus brings fortune in commerce and art. The native may experience fluctuations in wealth—early struggles followed by later prosperity. Business and trade are favored.", "interpretation_zh": "此宮管轄財富與物質財產。金星帶來商業與藝術方面的好運。命主可能經歷財富起伏——早期困難後期繁榮。有利於商業與貿易。"},
        3: {"name_ar": "بيت الإخوة", "name_en": "House of Siblings (Bayt al-Ikhwah)", "name_zh": "兄弟宮", "name_malay": "Rumah Saudara", "sign": "Gemini (الجوزاء)", "planet": "Mercury (عطارد)", "element": "Air (風)", "domain_en": "Brothers, sisters, short journeys, communication.", "domain_zh": "兄弟姐妹、短途旅行、溝通。", "interpretation_en": "This house governs siblings and close relatives. Mercury brings eloquence and intelligence. The native is skilled in communication and has both helpful and challenging relationships with siblings.", "interpretation_zh": "此宮管轄兄弟姐妹與近親。水星帶來口才與智慧。命主善於溝通，與兄弟姐妹的關係有好有壞。"},
        4: {"name_ar": "بيت الآباء", "name_en": "House of Parents (Bayt al-Aba)", "name_zh": "父母宮", "name_malay": "Rumah Ibu Bapa", "sign": "Cancer (السرطان)", "planet": "Moon (القمر)", "element": "Water (水)", "domain_en": "Parents, home, ancestry, roots, foundations.", "domain_zh": "父母、家庭、祖先、根基。", "interpretation_en": "This house represents parents and ancestral roots. The Moon brings emotional depth and family bonds. The native is filial and deeply loved by parents. May inherit property and gardens from parents.", "interpretation_zh": "此宮代表父母與祖先根基。月亮帶來情感深度與家庭紐帶。命主孝順父母，深受父母喜愛。可能繼承父母的財產與田園。"},
        5: {"name_ar": "بيت الأولاد", "name_en": "House of Children (Bayt al-Awlad)", "name_zh": "子女宮", "name_malay": "Rumah Anak", "sign": "Leo (الأسد)", "planet": "Sun (الشمس)", "element": "Fire (火)", "domain_en": "Children, joy, creativity, pleasure.", "domain_zh": "子女、喜樂、創造力、享樂。", "interpretation_en": "This house governs children and life's joys. The Sun brings vitality and creative energy. The native receives blessings from children, both sons and daughters. Reading the Quran brings mercy in this life and the next.", "interpretation_zh": "此宮管轄子女與人生喜樂。太陽帶來活力與創造能量。命主因子女而得福，男女皆有。誦讀古蘭經可得今世與來世的恩慈。"},
        6: {"name_ar": "بيت الأمراض", "name_en": "House of Illness (Bayt al-Amrad)", "name_zh": "疾厄宮", "name_malay": "Rumah Penyakit", "sign": "Virgo (السنبلة)", "planet": "Mercury (عطارد)", "element": "Earth (土)", "domain_en": "Health, illness, servants, daily work.", "domain_zh": "健康、疾病、僕役、日常工作。", "interpretation_en": "This house relates to health and illness. Mercury indicates illnesses of the mind and head. The wise recommend writing protective azimat (talismans) and reciting specific prayers for healing.", "interpretation_zh": "此宮與健康和疾病有關。水星指示頭部與心智方面的疾病。智者建議書寫護身符（阿茲默）並誦讀特定祈禱文以治療。"},
        7: {"name_ar": "بيت الزواج", "name_en": "House of Marriage (Bayt al-Zawaj)", "name_zh": "婚姻宮", "name_malay": "Rumah Perkahwinan", "sign": "Libra (الميزان)", "planet": "Venus (الزهرة)", "element": "Air (風)", "domain_en": "Marriage, partnerships, open enemies, contracts.", "domain_zh": "婚姻、合夥、公開敵人、契約。", "interpretation_en": "This house governs marriage and partnerships. Venus brings love and harmony but also potential conflict. The native may marry multiple times; sometimes in harmony, sometimes in disagreement.", "interpretation_zh": "此宮管轄婚姻與合作關係。金星帶來愛情與和諧，但也可能有衝突。命主可能多次結婚；時而和諧，時而不合。"},
        8: {"name_ar": "بيت الموت", "name_en": "House of Death (Bayt al-Mawt)", "name_zh": "死亡宮", "name_malay": "Rumah Ketakutan dan Mati", "sign": "Scorpio (العقرب)", "planet": "Mars (المريخ)", "element": "Water (水)", "domain_en": "Death, fear, inheritance, transformation.", "domain_zh": "死亡、恐懼、遺產、轉化。", "interpretation_en": "This house relates to death and fear. Mars brings danger and transformation. The native should be cautious during the first year, as there is danger of falling from high places. However, they will be saved from destruction by divine mercy.", "interpretation_zh": "此宮與死亡和恐懼有關。火星帶來危險與轉化。命主在第一年應謹慎，有從高處墜落的危險。然而，將因神的恩慈而免於毀滅。"},
        9: {"name_ar": "بيت السفر", "name_en": "House of Travel (Bayt al-Safar)", "name_zh": "遷移宮", "name_malay": "Rumah Perjalanan", "sign": "Sagittarius (القوس)", "planet": "Jupiter (المشتري)", "element": "Fire (火)", "domain_en": "Long journeys, pilgrimage, religion, higher learning.", "domain_zh": "遠行、朝聖、宗教、高等學識。", "interpretation_en": "This house governs long journeys and pilgrimage. Jupiter brings blessings in travel. The native will undertake journeys toward the east (sunrise direction) and may perform Hajj to the Sacred House of God and visit the Prophet's tomb.", "interpretation_zh": "此宮管轄遠行與朝聖。木星帶來旅途祝福。命主將向東（日出方向）旅行，可能前往麥加朝覲並拜訪先知的陵墓。"},
        10: {"name_ar": "بيت العز", "name_en": "House of Honor (Bayt al-Izz)", "name_zh": "官祿宮", "name_malay": "Rumah Kemuliaan dan Kekuasaan", "sign": "Capricorn (الجدي)", "planet": "Saturn (زحل)", "element": "Earth (土)", "domain_en": "Honor, authority, career, public standing.", "domain_zh": "榮譽、權威、事業、社會地位。", "interpretation_en": "This house represents honor and authority. Saturn brings discipline and perseverance. The native is respected and honored, associates with nobility and leaders. Good ending in life, receiving love and honor from all.", "interpretation_zh": "此宮代表榮譽與權威。土星帶來紀律與毅力。命主受人尊敬，與貴族和領袖交往。人生結局美好，受到眾人的愛戴與尊崇。"},
        11: {"name_ar": "بيت الأصدقاء", "name_en": "House of Friends (Bayt al-Asdiqa)", "name_zh": "福德宮", "name_malay": "Rumah Sahabat", "sign": "Aquarius (الدلو)", "planet": "Saturn (زحل)", "element": "Air (風)", "domain_en": "Friends, hopes, wishes, social groups.", "domain_zh": "朋友、希望、願望、社交團體。", "interpretation_en": "This house governs friendships and hopes. The native has loyal friends and achieves their wishes. Promises are fulfilled and good deeds are rewarded. The journey of life ends in repentance toward God.", "interpretation_zh": "此宮管轄友誼與希望。命主擁有忠誠的朋友，願望可以實現。承諾會被履行，善行會得到回報。人生旅途以向真主懺悔而結束。"},
        12: {"name_ar": "بيت الأعداء", "name_en": "House of Enemies (Bayt al-A'da)", "name_zh": "玄秘宮", "name_malay": "Rumah Musuh", "sign": "Pisces (الحوت)", "planet": "Jupiter (المشتري)", "element": "Water (水)", "domain_en": "Hidden enemies, sorrow, imprisonment, secrets.", "domain_zh": "隱藏的敵人、悲傷、監禁、秘密。", "interpretation_en": "This house relates to hidden enemies and secrets. Jupiter may protect from the worst, but the native faces enemies from family and acquaintances who become foes. A yellow-skinned woman may work sorcery. Protection through azimat and proper planetary timing is recommended.", "interpretation_zh": "此宮與隱藏的敵人和秘密有關。木星可能保護免受最壞情況，但命主面對來自家族和熟人轉變的敵人。建議通過護身符和適當的行星時辰來保護自己。"},
    }

    def get_house(self, house_number: int) -> dict[str, int | str]:
        """取得指定宮位資料。"""
        if house_number < 1 or house_number > 12:
            return {"error": "House number must be between 1 and 12."}
        return {"house_number": house_number, **self.HOUSES[house_number]}

    def get_all_houses(self) -> list[dict[str, int | str]]:
        """取得全部十二宮資料。"""
        return [{"house_number": num, **info} for num, info in self.HOUSES.items()]

    def get_house_by_sign(self, sign_name: str) -> dict[str, int | str] | None:
        """依星座名稱反查宮位。"""
        lookup = sign_name.lower()
        for number, info in self.HOUSES.items():
            if lookup in info["sign"].lower():
                return {"house_number": number, **info}
        return None

    def get_house_for_person(self, sign_number: int) -> dict[str, int | str]:
        """依 Hisab Nama 的十二星宮編號取得宮位。"""
        return self.get_house(sign_number)


__all__ = ["TwelveHouses"]
