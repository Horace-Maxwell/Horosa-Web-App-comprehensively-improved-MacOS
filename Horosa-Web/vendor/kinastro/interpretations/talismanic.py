"""
interpretations/talismanic.py — Picatrix 占星魔法護符詮釋資料庫

收錄 Picatrix（Ghayat al-Hakim）、Agrippa（De Occulta Philosophia）
及 Hermes Trismegistus（Liber Hermetis）三大傳統對護符的完整記載。

資料結構：
  • PlanetaryTalisman  — 7 顆傳統行星護符（各含目的、時機、材質、圖像、祈請文）
  • DecanTalisman      — 36 Decan 護符（Picatrix 明確記載的 36 個圖像）
  • FixedStarTalisman  — 15 Behenian 恆星護符（Agrippa / Hermes 傳統）

資料來源（Sources）：
  - *Ghayat al-Hakim* (Picatrix), Arabic c. 10th c. CE; Castilian c. 1256 CE
  - Heinrich Cornelius Agrippa, *De Occulta Philosophia* Bk I & II (1531)
  - Hermes Trismegistus (attributed), *Liber Hermetis de XV Stellis*
  - Marsilio Ficino, *De Vita Coelitus Comparanda* (1489)
  - Ibn Arfa' Ra's, *Shudhur al-Dhahab* (12th c.)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ============================================================
# Planetary Talisman
# ============================================================

@dataclass
class PlanetaryTalisman:
    """
    完整行星護符記錄（Planetary Talisman Record）。

    Attributes
    ----------
    planet : str
        行星英文名稱
    planet_cn : str
        行星中文名稱
    planet_glyph : str
        行星符號
    day_of_week : str
        最佳製作日（星期）
    day_of_week_cn : str
        最佳製作日（中文）
    planetary_hour_ruler : str
        行星時主星（需與護符行星一致）
    metal : str
        對應金屬（材質）
    metal_cn : str
        對應金屬（中文）
    gemstone : str
        對應寶石
    gemstone_cn : str
        對應寶石（中文）
    color : str
        對應顏色
    color_cn : str
        對應顏色（中文）
    incense : str
        薰香
    incense_cn : str
        薰香（中文）
    purposes_en : list[str]
        護符用途（英文）
    purposes_cn : list[str]
        護符用途（中文）
    electional_rules_en : list[str]
        擇時規則（英文，嚴格 Picatrix 傳統）
    electional_rules_cn : list[str]
        擇時規則（中文）
    image_description_en : str
        護符刻印圖像描述（英文，Picatrix 原文）
    image_description_cn : str
        護符刻印圖像描述（中文）
    invocation_en : str
        祈請文（英文）
    invocation_cn : str
        祈請文（中文）
    effects_en : str
        護符效力描述（英文）
    effects_cn : str
        護符效力描述（中文）
    picatrix_source : str
        Picatrix 原典出處
    dignity_requirement : str
        行星尊貴要求（Domicile / Exaltation / Triplicity）
    sigil_description : str
        符印描述
    """

    planet: str
    planet_cn: str
    planet_glyph: str
    day_of_week: str
    day_of_week_cn: str
    planetary_hour_ruler: str
    metal: str
    metal_cn: str
    gemstone: str
    gemstone_cn: str
    color: str
    color_cn: str
    incense: str
    incense_cn: str
    purposes_en: List[str] = field(default_factory=list)
    purposes_cn: List[str] = field(default_factory=list)
    electional_rules_en: List[str] = field(default_factory=list)
    electional_rules_cn: List[str] = field(default_factory=list)
    image_description_en: str = ""
    image_description_cn: str = ""
    invocation_en: str = ""
    invocation_cn: str = ""
    effects_en: str = ""
    effects_cn: str = ""
    picatrix_source: str = ""
    dignity_requirement: str = "Domicile or Exaltation"
    sigil_description: str = ""


# ============================================================
# Decan Talisman
# ============================================================

@dataclass
class DecanTalisman:
    """
    Decan（10° 度數帶）護符記錄（36 Decans）。

    Attributes
    ----------
    decan_number : int
        Decan 序號（1–36）
    sign : str
        所在星座（英文）
    sign_cn : str
        所在星座（中文）
    decan_in_sign : int
        星座內第幾 Decan（1, 2, 3）
    degrees_start : int
        起始度數（0, 10, 20）
    degrees_end : int
        結束度數（10, 20, 30）
    ruler : str
        Chaldean 順序主星
    ruler_cn : str
        主星（中文）
    image_description_en : str
        Picatrix 描述的雕刻圖像（英文）
    image_description_cn : str
        Picatrix 描述的雕刻圖像（中文）
    powers_en : list[str]
        護符力量（英文）
    powers_cn : list[str]
        護符力量（中文）
    incense : str
        薰香
    incense_cn : str
        薰香（中文）
    picatrix_source : str
        原典出處
    """

    decan_number: int
    sign: str
    sign_cn: str
    decan_in_sign: int
    degrees_start: int
    degrees_end: int
    ruler: str
    ruler_cn: str
    image_description_en: str = ""
    image_description_cn: str = ""
    powers_en: List[str] = field(default_factory=list)
    powers_cn: List[str] = field(default_factory=list)
    incense: str = ""
    incense_cn: str = ""
    picatrix_source: str = "Picatrix Bk II, Ch. 11"


# ============================================================
# Fixed Star Talisman (cross-reference to picatrix_behenian)
# ============================================================

@dataclass
class FixedStarTalisman:
    """
    Behenian 固定星護符記錄（Agrippa / Hermes 傳統）。
    本記錄為詮釋擴充版，完整護符資料見 astro.picatrix_behenian.constants。
    """

    star_name: str
    star_name_cn: str
    modern_name: str
    longitude_approx: float
    sign: str
    sign_cn: str
    primary_ruler: str
    primary_ruler_cn: str
    gemstone: str
    gemstone_cn: str
    herb: str
    herb_cn: str
    color: str
    color_cn: str
    incense: str
    incense_cn: str
    purposes_cn: List[str] = field(default_factory=list)
    purposes_en: List[str] = field(default_factory=list)
    image_description_en: str = ""
    image_description_cn: str = ""
    invocation_en: str = ""
    invocation_cn: str = ""
    picatrix_source: str = ""
    agrippa_source: str = ""
    extended_effects_cn: str = ""


# ============================================================
# 七大行星護符資料庫（7 Planetary Talismans）
# ============================================================

PLANETARY_TALISMANS: List[PlanetaryTalisman] = [

    # ── 土星 Saturn ──────────────────────────────────────────
    PlanetaryTalisman(
        planet="Saturn",
        planet_cn="土星",
        planet_glyph="♄",
        day_of_week="Saturday",
        day_of_week_cn="星期六",
        planetary_hour_ruler="Saturn",
        metal="Lead",
        metal_cn="鉛",
        gemstone="Onyx",
        gemstone_cn="縞瑪瑙",
        color="Black",
        color_cn="黑色",
        incense="Asafoetida / Myrrh",
        incense_cn="阿魏 / 沒藥",
        purposes_en=[
            "Protection against enemies", "Longevity", "Access to hidden knowledge",
            "Binding", "Curses (with caution)", "Real estate & property",
            "Agricultural matters", "Detention & imprisonment",
        ],
        purposes_cn=[
            "防護敵人", "長壽", "獲取隱秘知識",
            "束縛", "詛咒（謹慎）", "土地與財產",
            "農業事務", "拘押羈束",
        ],
        electional_rules_en=[
            "Saturn in Capricorn (domicile) or Libra (exaltation)",
            "Saturn rising or on the Midheaven",
            "Saturn in a dignified state (not retrograde if possible)",
            "Moon applying to Saturn in a good aspect (trine or sextile)",
            "Moon not in Via Combusta (Libra 15° – Scorpio 15°)",
            "Avoid Moon-Mars square or opposition",
        ],
        electional_rules_cn=[
            "土星位於摩羯座（本位）或天秤座（擢升）",
            "土星上升或位於中天",
            "土星品質良好（盡量非逆行）",
            "月亮以吉相接近土星（三合或六合）",
            "月亮不在焦灼帶（天秤 15° – 天蠍 15°）",
            "避免月亮與火星形成四分或對分",
        ],
        image_description_en=(
            "Picatrix Bk III: A man seated upon a throne, with the face of a raven "
            "or crow, holding a sickle in the right hand and a staff in the left; "
            "clad in black garments, aged and bearded."
        ),
        image_description_cn=(
            "Picatrix 卷三：一男子端坐王座，面貌如烏鴉，右手握鐮刀，左手持杖；"
            "身著黑袍，年邁鬚長，象徵時間與邊界之主。"
        ),
        invocation_en=(
            "O Saturn, high and exalted, supreme among the planets, "
            "lord of time and necessity — descend into this talisman, "
            "grant it the power of protection, endurance, and hidden wisdom. "
            "By thy seal I bind this intention; by thy ring I seal this power."
        ),
        invocation_cn=(
            "哦，土星，崇高之主，眾星之上，時間與宿命之王——"
            "降臨至此護符，賦予其防護、持久與隱秘智慧之力。"
            "以汝之封印，吾束縛此意念；以汝之環，吾封存此力量。"
        ),
        effects_en=(
            "Protects against slander, poison, and enemy plots. "
            "Grants access to chthonic and secret knowledge. Binds enemies. "
            "Aids in legal matters concerning land and inheritance."
        ),
        effects_cn=(
            "防護誹謗、毒藥與敵人陰謀。賦予獲取冥界與隱秘知識之能力。"
            "束縛敵人。有助於土地、遺產相關法律事務。"
        ),
        picatrix_source="Picatrix Bk II Ch. 10; Bk III Ch. 7",
        dignity_requirement="Domicile (Capricorn/Aquarius) or Exaltation (Libra)",
        sigil_description="Square seal with Saturn's Kamea (3×3 magic square) inscribed",
    ),

    # ── 木星 Jupiter ─────────────────────────────────────────
    PlanetaryTalisman(
        planet="Jupiter",
        planet_cn="木星",
        planet_glyph="♃",
        day_of_week="Thursday",
        day_of_week_cn="星期四",
        planetary_hour_ruler="Jupiter",
        metal="Tin",
        metal_cn="錫",
        gemstone="Sapphire / Lapis Lazuli",
        gemstone_cn="藍寶石 / 青金石",
        color="Blue / Purple",
        color_cn="藍色 / 紫色",
        incense="Cedar / Lignum Aloes / Saffron",
        incense_cn="雪松 / 沉香木 / 番紅花",
        purposes_en=[
            "Wealth and fortune", "Legal success and justice",
            "Political power and authority", "Health and well-being",
            "Spiritual growth and wisdom", "Friendship and goodwill",
            "Fertility and abundance", "Protection of rulers",
        ],
        purposes_cn=[
            "財富與好運", "法律勝訴與正義",
            "政治權力與權威", "健康與福祉",
            "靈性成長與智慧", "友誼與善意",
            "生育與豐盛", "統治者的庇護",
        ],
        electional_rules_en=[
            "Jupiter in Sagittarius or Pisces (domicile) or Cancer (exaltation)",
            "Jupiter in the 1st, 10th, or 11th house",
            "Moon applying to Jupiter by trine or conjunction",
            "Jupiter not retrograde, not under the Sun's beams",
            "Avoid Saturn-Jupiter opposition",
            "Moon waxing (first or second quarter preferred)",
        ],
        electional_rules_cn=[
            "木星位於射手座或雙魚座（本位）或巨蟹座（擢升）",
            "木星在第一、十、或十一宮",
            "月亮以三合或合相接近木星",
            "木星非逆行，不在太陽光束下",
            "避免土星與木星對分",
            "月亮漸盈（上弦至望月為佳）",
        ],
        image_description_en=(
            "Picatrix Bk III: A man seated on an eagle, crowned, bearing a bow; "
            "wearing royal garments of sky blue and purple; the eagle's wings spread "
            "wide. Alternatively: a robed judge holding scales of justice."
        ),
        image_description_cn=(
            "Picatrix 卷三：一男子騎乘老鷹，頭戴王冠，手持弓箭；"
            "身著天藍與紫色王室袍服，老鷹雙翼展開。"
            "另一版本：身著長袍的法官，手持正義天秤。"
        ),
        invocation_en=(
            "O Jupiter, beneficent king of the gods, distributor of all good things — "
            "pour your virtues into this talisman. Grant fortune, justice, and the "
            "favour of all who behold it. Let your power endure within this seal."
        ),
        invocation_cn=(
            "哦，木星，眾神仁慈之王，萬善之賜予者——"
            "將汝之美德注入此護符。賜予財富、正義，"
            "並讓所有見之者都給予青睞。讓汝之力量在此印記中長存。"
        ),
        effects_en=(
            "Brings wealth, fame, and the favor of powerful people. "
            "Protects in legal disputes. Grants health and longevity. "
            "Enhances spiritual authority and wisdom."
        ),
        effects_cn=(
            "帶來財富、名聲與有權勢者的庇護。在法律糾紛中給予保護。"
            "賜予健康與長壽。增強靈性權威與智慧。"
        ),
        picatrix_source="Picatrix Bk II Ch. 10; Bk III Ch. 7",
        dignity_requirement="Domicile (Sagittarius/Pisces) or Exaltation (Cancer)",
        sigil_description="4×4 Jupiter Kamea (magic square of 34) inscribed on tin",
    ),

    # ── 火星 Mars ────────────────────────────────────────────
    PlanetaryTalisman(
        planet="Mars",
        planet_cn="火星",
        planet_glyph="♂",
        day_of_week="Tuesday",
        day_of_week_cn="星期二",
        planetary_hour_ruler="Mars",
        metal="Iron / Steel",
        metal_cn="鐵 / 鋼",
        gemstone="Ruby / Bloodstone",
        gemstone_cn="紅寶石 / 血石",
        color="Red",
        color_cn="紅色",
        incense="Sulfur / Pepper / Galbanum",
        incense_cn="硫磺 / 胡椒 / 白松香",
        purposes_en=[
            "Victory in battle and conflict", "Courage and strength",
            "Breaking harmful magic", "Protection from violence",
            "Surgical success", "Driving away enemies",
            "Fevers and acute diseases (to cure)", "Hunting and athletics",
        ],
        purposes_cn=[
            "戰場與衝突中的勝利", "勇氣與力量",
            "破除有害魔法", "免受暴力傷害",
            "手術成功", "驅逐敵人",
            "治療發燒與急性疾病", "狩獵與競技",
        ],
        electional_rules_en=[
            "Mars in Aries or Scorpio (domicile) or Capricorn (exaltation)",
            "Mars angular (1st, 4th, 7th, or 10th house)",
            "Moon in a fire sign (Aries, Leo, Sagittarius)",
            "Avoid Moon-Saturn aspect for protection talismans",
            "Mars direct (not retrograde)",
        ],
        electional_rules_cn=[
            "火星位於牡羊座或天蠍座（本位）或摩羯座（擢升）",
            "火星位於角宮（第一、四、七、十宮）",
            "月亮在火象星座（牡羊、獅子、射手）",
            "防護護符應避免月亮與土星相位",
            "火星順行（非逆行）",
        ],
        image_description_en=(
            "Picatrix Bk III: An armed warrior standing upon a chariot drawn by "
            "two lions; wearing red armor, helmet with plumes; right hand holds a "
            "drawn sword, left holds a severed head. Alternatively: a man armed "
            "with sword and shield, face turned to the right."
        ),
        image_description_cn=(
            "Picatrix 卷三：一名全副武裝的戰士站在兩獅牽引的戰車上；"
            "身著紅色盔甲，頭盔飾有羽毛；右手握出鞘之劍，左手提一個斷頭。"
            "另一版本：手持劍與盾的武裝男子，臉朝右方。"
        ),
        invocation_en=(
            "O Mars, unconquered warrior, lord of iron and conflict — "
            "descend into this talisman and fill it with your strength. "
            "Grant victory to its bearer, repel all enemies, and protect "
            "against violence and malice."
        ),
        invocation_cn=(
            "哦，火星，無敵戰士，鐵與衝突之主——"
            "降臨至此護符，以汝之力量充滿它。"
            "賜予持有者勝利，驅退所有敵人，"
            "並抵禦暴力與惡意。"
        ),
        effects_en=(
            "Grants victory in conflicts and legal battles. Protects against "
            "violence, theft, and harmful magic. Grants courage and fearlessness."
        ),
        effects_cn=(
            "在衝突與法律訴訟中賜予勝利。防護暴力、盜竊與有害魔法。"
            "賜予勇氣與無畏之心。"
        ),
        picatrix_source="Picatrix Bk II Ch. 10; Bk III Ch. 7",
        dignity_requirement="Domicile (Aries/Scorpio) or Exaltation (Capricorn)",
        sigil_description="5×5 Mars Kamea (magic square of 65) on iron or red jasper",
    ),

    # ── 太陽 Sun ─────────────────────────────────────────────
    PlanetaryTalisman(
        planet="Sun",
        planet_cn="太陽",
        planet_glyph="☉",
        day_of_week="Sunday",
        day_of_week_cn="星期日",
        planetary_hour_ruler="Sun",
        metal="Gold",
        metal_cn="黃金",
        gemstone="Chrysolite / Diamond / Sunstone",
        gemstone_cn="橄欖石 / 鑽石 / 太陽石",
        color="Gold / Yellow",
        color_cn="金色 / 黃色",
        incense="Frankincense / Cinnamon / Saffron",
        incense_cn="乳香 / 肉桂 / 番紅花",
        purposes_en=[
            "Royal favor and recognition", "Leadership and authority",
            "Fame and reputation", "Health and vitality",
            "Overcoming depression", "Success in all undertakings",
            "Reconciliation with superiors", "Clear vision and prophecy",
        ],
        purposes_cn=[
            "王室恩寵與認可", "領導力與權威",
            "聲名與名譽", "健康與活力",
            "克服憂鬱", "所有事業的成功",
            "與上位者和解", "清晰視野與預言",
        ],
        electional_rules_en=[
            "Sun in Leo (domicile) or Aries (exaltation)",
            "Sun in the 1st, 10th, or 11th house",
            "Moon applying to Sun by favorable aspect (sextile or trine)",
            "Avoid lunar eclipse within 2 weeks",
            "Sunday during the hour of the Sun",
            "Moon not in Scorpio or Capricorn",
        ],
        electional_rules_cn=[
            "太陽位於獅子座（本位）或牡羊座（擢升）",
            "太陽在第一、十、或十一宮",
            "月亮以吉相接近太陽（六合或三合）",
            "避免兩週內有月食",
            "星期日太陽時",
            "月亮不在天蠍座或摩羯座",
        ],
        image_description_en=(
            "Picatrix Bk III: A crowned king seated on a lion throne, holding a "
            "golden scepter; the Sun blazing above his head; wearing golden robes "
            "adorned with rubies. The lion at his feet looks up adoringly."
        ),
        image_description_cn=(
            "Picatrix 卷三：一位頭戴王冠的國王端坐在獅子王座上，手持黃金權杖；"
            "頭頂烈日高照；身著嵌有紅寶石的金色袍服。腳邊的獅子仰頭崇敬。"
        ),
        invocation_en=(
            "O Sun, life-giver, king of all lights, from whom all vitality flows — "
            "pour your golden rays into this talisman. Grant fame, authority, "
            "health, and the favour of kings and nobles to its bearer."
        ),
        invocation_cn=(
            "哦，太陽，生命賦予者，萬光之王，一切活力之源——"
            "將汝之金色光芒注入此護符。賜予持有者聲名、權威、"
            "健康，以及王者與貴族的青睞。"
        ),
        effects_en=(
            "Grants recognition from powerful people, rulers, and employers. "
            "Restores health and vitality. Brings fame and lasting reputation. "
            "Protects against depression and failure."
        ),
        effects_cn=(
            "獲得有權勢者、統治者與雇主的認可。恢復健康與活力。"
            "帶來聲名與持久名譽。防護憂鬱與失敗。"
        ),
        picatrix_source="Picatrix Bk II Ch. 10; Bk III Ch. 7; Ficino De Vita III",
        dignity_requirement="Domicile (Leo) or Exaltation (Aries)",
        sigil_description="6×6 Sun Kamea (magic square of 111) on gold leaf",
    ),

    # ── 金星 Venus ───────────────────────────────────────────
    PlanetaryTalisman(
        planet="Venus",
        planet_cn="金星",
        planet_glyph="♀",
        day_of_week="Friday",
        day_of_week_cn="星期五",
        planetary_hour_ruler="Venus",
        metal="Copper / Bronze",
        metal_cn="銅 / 青銅",
        gemstone="Emerald / Malachite",
        gemstone_cn="翡翠 / 孔雀石",
        color="Green / Pink",
        color_cn="綠色 / 粉紅色",
        incense="Rose / Myrtle / Amber",
        incense_cn="玫瑰 / 桃金娘 / 琥珀",
        purposes_en=[
            "Love and attraction", "Harmony in relationships",
            "Beauty and charm", "Musical and artistic talent",
            "Fertility and pregnancy", "Reconciliation between lovers",
            "Pleasure and enjoyment", "Good fortune in trade",
        ],
        purposes_cn=[
            "愛情與吸引力", "關係中的和諧",
            "美麗與魅力", "音樂與藝術才能",
            "生育與懷孕", "戀人之間的和解",
            "享樂與歡愉", "貿易好運",
        ],
        electional_rules_en=[
            "Venus in Taurus or Libra (domicile) or Pisces (exaltation)",
            "Venus in the 1st, 5th, or 7th house",
            "Moon in Taurus or Libra, applying to Venus",
            "Avoid Mars-Venus square or opposition",
            "Venus direct, not under Sun's beams",
            "Friday at the hour of Venus, Moon waxing",
        ],
        electional_rules_cn=[
            "金星位於金牛座或天秤座（本位）或雙魚座（擢升）",
            "金星在第一、五、或七宮",
            "月亮在金牛或天秤，接近金星",
            "避免火星與金星形成四分或對分",
            "金星順行，不在太陽光束下",
            "星期五金星時，月亮漸盈",
        ],
        image_description_en=(
            "Picatrix Bk III: A young woman of great beauty, dressed in white and "
            "green; in her right hand an apple, in her left a comb; surrounded by "
            "doves, wearing a diadem of flowers. Alternatively: a naked goddess "
            "rising from the sea-foam, with long golden hair."
        ),
        image_description_cn=(
            "Picatrix 卷三：一位容貌絕美的年輕女子，身著白色與綠色服裝；"
            "右手持蘋果，左手拿梳子；四周環繞鴿子，頭戴花冠。"
            "另一版本：長髮如金的裸體女神從海泡中升起。"
        ),
        invocation_en=(
            "O Venus, sweet and gentle queen of beauty and love, "
            "who brings all hearts together in harmony — infuse this talisman "
            "with your grace. Grant love, beauty, pleasure, and the power "
            "to attract all whom the bearer desires."
        ),
        invocation_cn=(
            "哦，金星，美麗與愛情的甜美溫柔女王，"
            "以和諧凝聚一切心靈者——將汝之恩典注入此護符。"
            "賜予愛情、美麗、歡愉，以及吸引持有者所渴望之人的力量。"
        ),
        effects_en=(
            "Makes the bearer beloved and attractive to all. Restores broken "
            "relationships and brings harmony. Enhances beauty, creativity, "
            "and musical talent. Aids fertility."
        ),
        effects_cn=(
            "使持有者為所有人所愛慕吸引。修復破碎的關係並帶來和諧。"
            "增強美麗、創造力與音樂才能。助益生育。"
        ),
        picatrix_source="Picatrix Bk II Ch. 10; Bk III Ch. 7; Agrippa Op. III",
        dignity_requirement="Domicile (Taurus/Libra) or Exaltation (Pisces)",
        sigil_description="7×7 Venus Kamea (magic square of 175) on copper plate",
    ),

    # ── 水星 Mercury ─────────────────────────────────────────
    PlanetaryTalisman(
        planet="Mercury",
        planet_cn="水星",
        planet_glyph="☿",
        day_of_week="Wednesday",
        day_of_week_cn="星期三",
        planetary_hour_ruler="Mercury",
        metal="Quicksilver / Alloy",
        metal_cn="水銀 / 合金",
        gemstone="Agate / Carnelian / Emerald",
        gemstone_cn="瑪瑙 / 紅玉髓 / 翡翠",
        color="Multi-color / Purple",
        color_cn="多色 / 紫色",
        incense="Mastic / Storax / Lavender",
        incense_cn="乳香脂 / 安息香 / 薰衣草",
        purposes_en=[
            "Intelligence and memory", "Eloquence and persuasion",
            "Commercial success and trade", "Learning and study",
            "Communication and writing", "Divination and prophecy",
            "Cunning and cleverness", "Safe travel",
        ],
        purposes_cn=[
            "智力與記憶力", "口才與說服力",
            "商業成功與貿易", "學習與研究",
            "溝通與寫作", "占卜與預言",
            "機智與聰慧", "旅途平安",
        ],
        electional_rules_en=[
            "Mercury in Gemini (domicile) or Virgo (domicile and exaltation)",
            "Mercury in the 1st, 3rd, or 9th house",
            "Moon applying to Mercury by favorable aspect",
            "Mercury direct and not under Sun's beams",
            "Wednesday at the hour of Mercury",
            "Avoid Mercury retrograde for communication talismans",
        ],
        electional_rules_cn=[
            "水星位於雙子座或處女座（本位）或處女座（擢升）",
            "水星在第一、三、或九宮",
            "月亮以吉相接近水星",
            "水星順行且不在太陽光束下",
            "星期三水星時",
            "溝通護符應避免水星逆行期間",
        ],
        image_description_en=(
            "Picatrix Bk III: A young man with a youthful beard, holding a writing "
            "tablet and stylus in the right hand, a serpent in the left; wearing a "
            "multi-colored robe; winged sandals on his feet. Sometimes depicted "
            "carrying the caduceus (winged staff with two serpents)."
        ),
        image_description_cn=(
            "Picatrix 卷三：一位留有年輕鬍鬚的男子，右手持書寫板與鐵筆，"
            "左手執一條蛇；身著多色袍服；腳穿翼狀涼鞋。"
            "有時描繪為手持雙蛇纏繞的信使杖（Caduceus）。"
        ),
        invocation_en=(
            "O Mercury, swift messenger, lord of reason and cunning eloquence, "
            "who governs all commerce and learning — descend into this talisman. "
            "Grant intelligence, eloquence, and success in all endeavors "
            "requiring mind and skill."
        ),
        invocation_cn=(
            "哦，水星，敏捷信使，理智與機智口才之主，"
            "掌管一切貿易與學問者——降臨至此護符。"
            "賜予智識、口才，以及在所有需要心智與技巧的事業中的成功。"
        ),
        effects_en=(
            "Sharpens the mind and improves memory. Grants eloquence and "
            "persuasive power. Brings success in commerce and negotiations. "
            "Aids learning, writing, and all intellectual pursuits."
        ),
        effects_cn=(
            "使思維敏銳並改善記憶。賜予口才與說服力。"
            "帶來商業與談判的成功。助益學習、寫作與所有智識追求。"
        ),
        picatrix_source="Picatrix Bk II Ch. 10; Bk III Ch. 7",
        dignity_requirement="Domicile (Gemini/Virgo) or Exaltation (Virgo)",
        sigil_description="8×8 Mercury Kamea (magic square of 260) on silver alloy",
    ),

    # ── 月亮 Moon ────────────────────────────────────────────
    PlanetaryTalisman(
        planet="Moon",
        planet_cn="月亮",
        planet_glyph="☽",
        day_of_week="Monday",
        day_of_week_cn="星期一",
        planetary_hour_ruler="Moon",
        metal="Silver",
        metal_cn="銀",
        gemstone="Pearl / Moonstone / Crystal",
        gemstone_cn="珍珠 / 月光石 / 水晶",
        color="White / Silver",
        color_cn="白色 / 銀色",
        incense="Camphor / Jasmine / White Sandalwood",
        incense_cn="樟腦 / 茉莉 / 白檀香",
        purposes_en=[
            "Emotional healing and peace", "Dreams and visions",
            "Safe sea and water travel", "Fertility and childbirth",
            "Recovery from illness", "Good memory",
            "Protection of the home", "Matters involving women and children",
        ],
        purposes_cn=[
            "情感療癒與平靜", "夢境與靈視",
            "海上與水上旅行平安", "生育與分娩",
            "疾病康復", "良好記憶力",
            "家宅防護", "涉及女性與兒童之事",
        ],
        electional_rules_en=[
            "Moon in Cancer (domicile) or Taurus (exaltation)",
            "Moon waxing and in a good phase (crescent to full)",
            "Moon in a favorable sign (Cancer, Taurus, Pisces)",
            "Avoid Moon in Scorpio, Capricorn, or Gemini for emotional matters",
            "Monday at the hour of the Moon",
            "Moon not afflicted by Saturn or Mars",
        ],
        electional_rules_cn=[
            "月亮位於巨蟹座（本位）或金牛座（擢升）",
            "月亮漸盈並處於吉相（新月至望月）",
            "月亮在吉利星座（巨蟹、金牛、雙魚）",
            "情感事務應避免月亮在天蠍、摩羯或雙子",
            "星期一月亮時",
            "月亮不受土星或火星凶害",
        ],
        image_description_en=(
            "Picatrix Bk III: A woman of luminous beauty, seated upon a bull; "
            "wearing silver garments; her head surrounded by a crescent moon; "
            "in her right hand a mirror, in her left a serpent. "
            "Some versions show her crowned with stars, feet on the sea."
        ),
        image_description_cn=(
            "Picatrix 卷三：一位容貌光輝的女子，端坐於公牛背上；"
            "身著銀色衣裳；頭部環繞著新月；右手持鏡，左手執蛇。"
            "部分版本描繪她頭戴星冠，腳踏海浪。"
        ),
        invocation_en=(
            "O Moon, queen of the night, ruler of the tides and dreams, "
            "silver light that governs growth and rest — pour your gentle "
            "radiance into this talisman. Grant emotional peace, healing, "
            "and safe passage through all changing waters."
        ),
        invocation_cn=(
            "哦，月亮，夜之女王，潮汐與夢境的統治者，"
            "掌管生長與休息的銀色之光——將汝柔和的光輝注入此護符。"
            "賜予情感平靜、療癒，以及安全穿越所有流變之水的力量。"
        ),
        effects_en=(
            "Brings emotional healing, peace of mind, and restful sleep. "
            "Enhances intuition and psychic ability. Protects at sea. "
            "Aids fertility and safe childbirth."
        ),
        effects_cn=(
            "帶來情感療癒、心靈平靜與安眠。增強直覺與通靈能力。"
            "在海上給予保護。助益生育與平安分娩。"
        ),
        picatrix_source="Picatrix Bk II Ch. 10; Bk III Ch. 7",
        dignity_requirement="Domicile (Cancer) or Exaltation (Taurus)",
        sigil_description="9×9 Moon Kamea (magic square of 369) on silver",
    ),
]

# 建立行星快速查詢字典
PLANETARY_TALISMAN_BY_PLANET: Dict[str, PlanetaryTalisman] = {
    t.planet: t for t in PLANETARY_TALISMANS
}


# ============================================================
# 36 Decan 護符資料庫（Picatrix 卷二第十一章）
# ============================================================

DECAN_TALISMANS: List[DecanTalisman] = [

    # ── 牡羊座 Aries Decans ───────────────────────────────────
    DecanTalisman(
        decan_number=1, sign="Aries", sign_cn="牡羊座",
        decan_in_sign=1, degrees_start=0, degrees_end=10, ruler="Mars", ruler_cn="火星",
        image_description_en=(
            "A dark man with a large and white body, having red eyes, "
            "holding a sword, girded with white cloth — fierce and wrathful."
        ),
        image_description_cn="一個身材高大膚色黝黑的男子，紅眼睛，手持劍，腰圍白布——凶猛憤怒的形象。",
        powers_en=["Strength and courage", "Victory in conflict", "Physical vitality"],
        powers_cn=["力量與勇氣", "衝突中的勝利", "肢體活力"],
        incense="Pepper and galbanum", incense_cn="胡椒與白松香",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=2, sign="Aries", sign_cn="牡羊座",
        decan_in_sign=2, degrees_start=10, degrees_end=20, ruler="Sun", ruler_cn="太陽",
        image_description_en=(
            "A woman dressed in green, who lacks one leg; she is clothed "
            "and veiled. In her hand she holds a pomegranate."
        ),
        image_description_cn="一位身著綠衣的女子，缺一條腿；她蒙著面紗。手持石榴。",
        powers_en=["Fertility", "Growth of plants", "Women's health"],
        powers_cn=["生育", "植物生長", "女性健康"],
        incense="Saffron and myrtle", incense_cn="番紅花與桃金娘",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=3, sign="Aries", sign_cn="牡羊座",
        decan_in_sign=3, degrees_start=20, degrees_end=30, ruler="Jupiter", ruler_cn="木星",
        image_description_en=(
            "A man of restless spirit, with a serpent in his hand; he has "
            "red hair and is wearing a coat of mail."
        ),
        image_description_cn="一個心神不寧的男子，手持蛇；紅髮，身穿鎖子甲。",
        powers_en=["Protection from poison", "Serpent magic", "Military protection"],
        powers_cn=["防毒保護", "蛇魔法", "軍事防護"],
        incense="Opoponax and henbane", incense_cn="歐白芷與天仙子",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),

    # ── 金牛座 Taurus Decans ──────────────────────────────────
    DecanTalisman(
        decan_number=4, sign="Taurus", sign_cn="金牛座",
        decan_in_sign=1, degrees_start=0, degrees_end=10, ruler="Venus", ruler_cn="金星",
        image_description_en=(
            "A woman with the face of a stag, who wears red clothing; she "
            "holds a serpent and a spear; she is called 'the keeper of cultivated lands.'"
        ),
        image_description_cn="一位鹿頭人身的女子，穿著紅衣；手持蛇與長矛；被稱為「農田守護者」。",
        powers_en=["Agricultural abundance", "Land fertility", "Protection of crops"],
        powers_cn=["農業豐收", "土地肥沃", "保護農作物"],
        incense="Cinnamon and myrrh", incense_cn="肉桂與沒藥",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=5, sign="Taurus", sign_cn="金牛座",
        decan_in_sign=2, degrees_start=10, degrees_end=20, ruler="Mercury", ruler_cn="水星",
        image_description_en=(
            "A man plowing, with a key in his hand. He is a keeper and "
            "guardian of the seeds that are sown."
        ),
        image_description_cn="一個耕地的男子，手持鑰匙。他是播種種子的守護者。",
        powers_en=["Success in farming", "Opening doors to opportunity", "Secrets and keys"],
        powers_cn=["農業成功", "開啟機遇之門", "秘密與鑰匙"],
        incense="Storax and camphor", incense_cn="安息香與樟腦",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=6, sign="Taurus", sign_cn="金牛座",
        decan_in_sign=3, degrees_start=20, degrees_end=30, ruler="Saturn", ruler_cn="土星",
        image_description_en=(
            "A man with the form of a camel, holding a scorpion in his hand; "
            "an emblem of stubbornness and endurance."
        ),
        image_description_cn="一個駱駝形態的男子，手持蠍子；頑強與耐力的象徵。",
        powers_en=["Endurance and perseverance", "Overcoming obstacles", "Patience"],
        powers_cn=["忍耐與堅持", "克服障礙", "耐性"],
        incense="Asafoetida and myrrh", incense_cn="阿魏與沒藥",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),

    # ── 雙子座 Gemini Decans ──────────────────────────────────
    DecanTalisman(
        decan_number=7, sign="Gemini", sign_cn="雙子座",
        decan_in_sign=1, degrees_start=0, degrees_end=10, ruler="Mercury", ruler_cn="水星",
        image_description_en=(
            "A man of beautiful form, holding a staff; he writes letters "
            "and moves quickly like the wind."
        ),
        image_description_cn="一個形貌俊美的男子，手持杖；他書寫文字，移動如風般迅速。",
        powers_en=["Communication excellence", "Speed of mind", "Writing and oratory"],
        powers_cn=["卓越溝通", "思維敏捷", "寫作與演說"],
        incense="Mastic and lavender", incense_cn="乳香脂與薰衣草",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=8, sign="Gemini", sign_cn="雙子座",
        decan_in_sign=2, degrees_start=10, degrees_end=20, ruler="Venus", ruler_cn="金星",
        image_description_en=(
            "A man clothed in a coat of mail, holding a bow and arrows; "
            "he shoots and misses not."
        ),
        image_description_cn="一個穿著鎖子甲的男子，手持弓與箭；他射箭從不失手。",
        powers_en=["Accuracy and precision", "Martial skill", "Hunting"],
        powers_cn=["準確性與精密", "武術技巧", "狩獵"],
        incense="Rose and amber", incense_cn="玫瑰與琥珀",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=9, sign="Gemini", sign_cn="雙子座",
        decan_in_sign=3, degrees_start=20, degrees_end=30, ruler="Saturn", ruler_cn="土星",
        image_description_en=(
            "A man holding a key and a book; an elder seated in a chair "
            "of learning, wearing dark robes."
        ),
        image_description_cn="一個手持鑰匙與書籍的男子；一位坐在學習椅上的長者，身著深色袍服。",
        powers_en=["Secret knowledge", "Access to locked wisdom", "Academic success"],
        powers_cn=["隱秘知識", "獲取封存智慧", "學術成功"],
        incense="Asafoetida and mastic", incense_cn="阿魏與乳香脂",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),

    # ── 巨蟹座 Cancer Decans ──────────────────────────────────
    DecanTalisman(
        decan_number=10, sign="Cancer", sign_cn="巨蟹座",
        decan_in_sign=1, degrees_start=0, degrees_end=10, ruler="Moon", ruler_cn="月亮",
        image_description_en=(
            "A man with the form of a horse's head, clothed in a coat of mail; "
            "he runs with great speed over the sea."
        ),
        image_description_cn="一個馬頭人身的男子，穿著鎖子甲；他在海面上奔馳如飛。",
        powers_en=["Safe sea travel", "Speed", "Overcoming water dangers"],
        powers_cn=["海上安全旅行", "速度", "克服水上危險"],
        incense="Camphor and jasmine", incense_cn="樟腦與茉莉",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=11, sign="Cancer", sign_cn="巨蟹座",
        decan_in_sign=2, degrees_start=10, degrees_end=20, ruler="Mars", ruler_cn="火星",
        image_description_en=(
            "A man of great size, with the neck of a bull, holding a "
            "sharp weapon in his hand; he is very powerful."
        ),
        image_description_cn="一個身材高大的男子，擁有公牛般的頸部，手持鋒利兵器；他非常強大。",
        powers_en=["Physical strength", "Protection", "Domination over enemies"],
        powers_cn=["肢體力量", "保護", "壓制敵人"],
        incense="Galbanum and pepper", incense_cn="白松香與胡椒",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=12, sign="Cancer", sign_cn="巨蟹座",
        decan_in_sign=3, degrees_start=20, degrees_end=30, ruler="Jupiter", ruler_cn="木星",
        image_description_en=(
            "A woman with a beautiful face, wearing fine garments and a crown; "
            "she presides over all works of abundance."
        ),
        image_description_cn="一位面容美麗、身著華服頭戴王冠的女子；她主持一切豐盛之事。",
        powers_en=["Abundance", "Beauty and grace", "Social success"],
        powers_cn=["豐盛", "美麗與優雅", "社交成功"],
        incense="Cedar and saffron", incense_cn="雪松與番紅花",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),

    # ── 獅子座 Leo Decans ────────────────────────────────────
    DecanTalisman(
        decan_number=13, sign="Leo", sign_cn="獅子座",
        decan_in_sign=1, degrees_start=0, degrees_end=10, ruler="Sun", ruler_cn="太陽",
        image_description_en=(
            "A man with a horse's face and the form of a great lord; "
            "he wears a crown and holds a whip."
        ),
        image_description_cn="一個馬臉人身的男子，有著偉大領主的形態；頭戴王冠，手持鞭子。",
        powers_en=["Authority and command", "Control of animals", "Noble bearing"],
        powers_cn=["權威與指揮", "控制動物", "貴族氣度"],
        incense="Frankincense and cinnamon", incense_cn="乳香與肉桂",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=14, sign="Leo", sign_cn="獅子座",
        decan_in_sign=2, degrees_start=10, degrees_end=20, ruler="Jupiter", ruler_cn="木星",
        image_description_en=(
            "A man clothed in lion's skin, with the face of a lion; "
            "he carries a sword and a shield, and is very warlike."
        ),
        image_description_cn="一個身著獅皮的男子，獅子面孔；手持劍與盾，非常好戰。",
        powers_en=["Courage", "Victory", "Defeat of enemies"],
        powers_cn=["勇氣", "勝利", "擊敗敵人"],
        incense="Cedar and lignum aloes", incense_cn="雪松與沉香",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=15, sign="Leo", sign_cn="獅子座",
        decan_in_sign=3, degrees_start=20, degrees_end=30, ruler="Mars", ruler_cn="火星",
        image_description_en=(
            "A man on a horse, holding a snake in his hand; he is skilled "
            "in the science of poisons and their antidotes."
        ),
        image_description_cn="一個騎馬的男子，手持蛇；他精通毒物及其解藥之學。",
        powers_en=["Protection from poison", "Knowledge of remedies", "Cunning"],
        powers_cn=["防毒保護", "藥物知識", "機智"],
        incense="Sulfur and opoponax", incense_cn="硫磺與歐白芷",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),

    # ── 處女座 Virgo Decans ──────────────────────────────────
    DecanTalisman(
        decan_number=16, sign="Virgo", sign_cn="處女座",
        decan_in_sign=1, degrees_start=0, degrees_end=10, ruler="Mercury", ruler_cn="水星",
        image_description_en=(
            "A young virgin, beautiful and clothed in white; she holds "
            "a sheaf of grain; she is the keeper of all that grows."
        ),
        image_description_cn="一個美麗的年輕處女，身著白衣；手持一束穀物；她是一切生長之物的守護者。",
        powers_en=["Purity", "Harvest abundance", "Healing herbs"],
        powers_cn=["純潔", "豐收", "療癒草藥"],
        incense="Mastic and storax", incense_cn="乳香脂與安息香",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=17, sign="Virgo", sign_cn="處女座",
        decan_in_sign=2, degrees_start=10, degrees_end=20, ruler="Saturn", ruler_cn="土星",
        image_description_en=(
            "A black man with a white staff; he is the guardian of "
            "boundaries and the keeper of secret places."
        ),
        image_description_cn="一個持白杖的黑衣男子；他是邊界守護者，隱秘場所的守衛。",
        powers_en=["Protection of property", "Boundary magic", "Secret keeping"],
        powers_cn=["財產保護", "邊界魔法", "保守秘密"],
        incense="Myrrh and asafoetida", incense_cn="沒藥與阿魏",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=18, sign="Virgo", sign_cn="處女座",
        decan_in_sign=3, degrees_start=20, degrees_end=30, ruler="Venus", ruler_cn="金星",
        image_description_en=(
            "A man with the form of a scribe, holding a book and a pen; "
            "he is learned in all the arts and sciences."
        ),
        image_description_cn="一個以書記形態呈現的男子，手持書本與筆；他精通所有藝術與科學。",
        powers_en=["Learning", "Writing mastery", "Scientific knowledge"],
        powers_cn=["學習", "寫作精通", "科學知識"],
        incense="Rose and amber", incense_cn="玫瑰與琥珀",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),

    # ── 天秤座 Libra Decans ──────────────────────────────────
    DecanTalisman(
        decan_number=19, sign="Libra", sign_cn="天秤座",
        decan_in_sign=1, degrees_start=0, degrees_end=10, ruler="Moon", ruler_cn="月亮",
        image_description_en=(
            "A man holding a balance scale in his right hand; he is "
            "dressed in fine clothes and seeks justice in all things."
        ),
        image_description_cn="一個右手持天秤的男子；身著華服，在一切事物中尋求正義。",
        powers_en=["Justice and fairness", "Legal success", "Balance in relationships"],
        powers_cn=["正義與公平", "法律勝訴", "關係平衡"],
        incense="Camphor and sandalwood", incense_cn="樟腦與檀香",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=20, sign="Libra", sign_cn="天秤座",
        decan_in_sign=2, degrees_start=10, degrees_end=20, ruler="Saturn", ruler_cn="土星",
        image_description_en=(
            "A man in a hunting outfit, with a dog by his side; he is "
            "skilled in tracking and discovery."
        ),
        image_description_cn="一個穿著狩獵裝的男子，身旁有一條狗；他擅長追蹤與發現。",
        powers_en=["Hunting success", "Finding lost things", "Investigation"],
        powers_cn=["狩獵成功", "尋回失物", "調查"],
        incense="Asafoetida and myrrh", incense_cn="阿魏與沒藥",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=21, sign="Libra", sign_cn="天秤座",
        decan_in_sign=3, degrees_start=20, degrees_end=30, ruler="Jupiter", ruler_cn="木星",
        image_description_en=(
            "A man of generous bearing, with a noble face; he distributes "
            "gifts and wealth with both hands."
        ),
        image_description_cn="一個氣度慷慨、面容高貴的男子；他雙手分發禮物與財富。",
        powers_en=["Generosity", "Wealth distribution", "Noble friendships"],
        powers_cn=["慷慨", "財富分配", "貴族友誼"],
        incense="Cedar and saffron", incense_cn="雪松與番紅花",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),

    # ── 天蠍座 Scorpio Decans ─────────────────────────────────
    DecanTalisman(
        decan_number=22, sign="Scorpio", sign_cn="天蠍座",
        decan_in_sign=1, degrees_start=0, degrees_end=10, ruler="Mars", ruler_cn="火星",
        image_description_en=(
            "A man with a dark face and red eyes; in his right hand a serpent, "
            "in his left a spear. He is the keeper of hidden venoms."
        ),
        image_description_cn="一個面容陰暗、紅眼的男子；右手持蛇，左手持長矛。他是隱秘毒物的守護者。",
        powers_en=["Protection from poison", "Occult power", "Transformation"],
        powers_cn=["防毒保護", "神秘力量", "轉化"],
        incense="Sulfur and opoponax", incense_cn="硫磺與歐白芷",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=23, sign="Scorpio", sign_cn="天蠍座",
        decan_in_sign=2, degrees_start=10, degrees_end=20, ruler="Sun", ruler_cn="太陽",
        image_description_en=(
            "A man with a cat's face, wearing armour; he has great power "
            "over hidden things and unseen forces."
        ),
        image_description_cn="一個貓臉、身穿盔甲的男子；他對隱秘事物與無形力量有強大掌控力。",
        powers_en=["Control of hidden forces", "Uncovering secrets", "Night protection"],
        powers_cn=["掌控隱秘力量", "揭露秘密", "夜間保護"],
        incense="Frankincense and henbane", incense_cn="乳香與天仙子",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=24, sign="Scorpio", sign_cn="天蠍座",
        decan_in_sign=3, degrees_start=20, degrees_end=30, ruler="Venus", ruler_cn="金星",
        image_description_en=(
            "A man with the face of a dog, wearing a long coat; "
            "he governs over the boundaries between life and death."
        ),
        image_description_cn="一個狗臉、穿著長袍的男子；他掌管生死之間的界線。",
        powers_en=["Crossing boundaries", "Necromantic protection", "Death and rebirth"],
        powers_cn=["跨越邊界", "靈媒保護", "死亡與重生"],
        incense="Myrrh and rose", incense_cn="沒藥與玫瑰",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),

    # ── 射手座 Sagittarius Decans ──────────────────────────────
    DecanTalisman(
        decan_number=25, sign="Sagittarius", sign_cn="射手座",
        decan_in_sign=1, degrees_start=0, degrees_end=10, ruler="Jupiter", ruler_cn="木星",
        image_description_en=(
            "A man on horseback, wearing a coat of mail and a helmet "
            "adorned with a crown; he holds a javelin."
        ),
        image_description_cn="一個騎馬的男子，身穿鎖子甲與飾有王冠的頭盔；手持標槍。",
        powers_en=["Long journeys", "Higher education", "Philosophy and religion"],
        powers_cn=["長途旅行", "高等教育", "哲學與宗教"],
        incense="Cedar and lignum aloes", incense_cn="雪松與沉香",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=26, sign="Sagittarius", sign_cn="射手座",
        decan_in_sign=2, degrees_start=10, degrees_end=20, ruler="Mars", ruler_cn="火星",
        image_description_en=(
            "A woman with her hair unbound, holding a bow and arrows; "
            "she is swift as the wind and never misses her target."
        ),
        image_description_cn="一個頭髮散開的女子，手持弓與箭；她如風般迅速，從不失手。",
        powers_en=["Precision", "Freedom", "Athletic excellence"],
        powers_cn=["精準", "自由", "運動卓越"],
        incense="Pepper and galbanum", incense_cn="胡椒與白松香",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=27, sign="Sagittarius", sign_cn="射手座",
        decan_in_sign=3, degrees_start=20, degrees_end=30, ruler="Sun", ruler_cn="太陽",
        image_description_en=(
            "A man with the face of a monkey, holding a staff; "
            "he is laughing and reveals the secrets of wisdom through jest."
        ),
        image_description_cn="一個猴臉的男子，手持杖；他在笑，透過玩笑揭示智慧的秘密。",
        powers_en=["Wit and cleverness", "Humor as power", "Revealing hidden wisdom"],
        powers_cn=["機智與聰慧", "幽默作為力量", "揭示隱藏智慧"],
        incense="Frankincense and cinnamon", incense_cn="乳香與肉桂",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),

    # ── 摩羯座 Capricorn Decans ────────────────────────────────
    DecanTalisman(
        decan_number=28, sign="Capricorn", sign_cn="摩羯座",
        decan_in_sign=1, degrees_start=0, degrees_end=10, ruler="Saturn", ruler_cn="土星",
        image_description_en=(
            "A woman with a goat's face, of great age; she carries "
            "a serpent and rules over barren lands."
        ),
        image_description_cn="一個山羊面孔的年邁女子；她攜帶一條蛇，統治荒地。",
        powers_en=["Endurance in hardship", "Control over barren lands", "Old age wisdom"],
        powers_cn=["在苦難中堅忍", "掌控荒地", "老年智慧"],
        incense="Asafoetida and myrrh", incense_cn="阿魏與沒藥",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=29, sign="Capricorn", sign_cn="摩羯座",
        decan_in_sign=2, degrees_start=10, degrees_end=20, ruler="Venus", ruler_cn="金星",
        image_description_en=(
            "A woman with a beautiful but severe face; she holds "
            "a golden cup from which she pours wine."
        ),
        image_description_cn="一個面容美麗但嚴峻的女子；她手持金杯，從中倒出葡萄酒。",
        powers_en=["Hospitality", "Refined pleasure", "Control through grace"],
        powers_cn=["好客", "精緻享樂", "以優雅掌控"],
        incense="Rose and myrrh", incense_cn="玫瑰與沒藥",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=30, sign="Capricorn", sign_cn="摩羯座",
        decan_in_sign=3, degrees_start=20, degrees_end=30, ruler="Mercury", ruler_cn="水星",
        image_description_en=(
            "A man of old age, leaning on a staff; he is a collector "
            "of herbs and knows their secret virtues."
        ),
        image_description_cn="一個倚杖的老人；他是草藥採集者，知曉其隱秘功效。",
        powers_en=["Herbal wisdom", "Medical knowledge", "Patience and age"],
        powers_cn=["草藥智慧", "醫學知識", "耐性與老年智慧"],
        incense="Mastic and storax", incense_cn="乳香脂與安息香",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),

    # ── 水瓶座 Aquarius Decans ─────────────────────────────────
    DecanTalisman(
        decan_number=31, sign="Aquarius", sign_cn="水瓶座",
        decan_in_sign=1, degrees_start=0, degrees_end=10, ruler="Saturn", ruler_cn="土星",
        image_description_en=(
            "A man with a great crown upon his head, pouring water from "
            "a vessel; he is the lord of springs and streams."
        ),
        image_description_cn="一個頭戴大王冠的男子，從容器中倒出水；他是泉水與溪流之主。",
        powers_en=["Command of water", "Generosity", "Innovation"],
        powers_cn=["掌控水源", "慷慨大方", "創新"],
        incense="Asafoetida and camphor", incense_cn="阿魏與樟腦",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=32, sign="Aquarius", sign_cn="水瓶座",
        decan_in_sign=2, degrees_start=10, degrees_end=20, ruler="Mercury", ruler_cn="水星",
        image_description_en=(
            "A man with a monkey's face, clothed in silk; "
            "he speaks in riddles and knows many languages."
        ),
        image_description_cn="一個猴臉男子，身著絲衣；他說謎語，懂得多種語言。",
        powers_en=["Language mastery", "Riddles and codes", "Cross-cultural communication"],
        powers_cn=["語言精通", "謎語與密碼", "跨文化溝通"],
        incense="Lavender and mastic", incense_cn="薰衣草與乳香脂",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=33, sign="Aquarius", sign_cn="水瓶座",
        decan_in_sign=3, degrees_start=20, degrees_end=30, ruler="Venus", ruler_cn="金星",
        image_description_en=(
            "A woman with long dark hair, sitting by a stream; "
            "she is absorbed in deep contemplation of hidden truths."
        ),
        image_description_cn="一個長著烏黑長髮的女子，坐在溪流旁；她沉浸在對隱藏真相的深沉冥思中。",
        powers_en=["Deep contemplation", "Hidden knowledge", "Mystical understanding"],
        powers_cn=["深沉冥想", "隱秘知識", "神秘理解"],
        incense="Amber and rose", incense_cn="琥珀與玫瑰",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),

    # ── 雙魚座 Pisces Decans ──────────────────────────────────
    DecanTalisman(
        decan_number=34, sign="Pisces", sign_cn="雙魚座",
        decan_in_sign=1, degrees_start=0, degrees_end=10, ruler="Jupiter", ruler_cn="木星",
        image_description_en=(
            "A man with the form of a fish, holding a vessel of water; "
            "he is the guardian of the sea's hidden treasures."
        ),
        image_description_cn="一個魚形的男子，手持水容器；他是海洋隱藏寶藏的守護者。",
        powers_en=["Sea treasure", "Spiritual gifts", "Compassion and mercy"],
        powers_cn=["海洋寶藏", "靈性恩賜", "慈悲與仁慈"],
        incense="Cedar and jasmine", incense_cn="雪松與茉莉",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=35, sign="Pisces", sign_cn="雙魚座",
        decan_in_sign=2, degrees_start=10, degrees_end=20, ruler="Moon", ruler_cn="月亮",
        image_description_en=(
            "A woman of pale complexion, wearing white; she sings "
            "and leads souls through the waters of the underworld."
        ),
        image_description_cn="一個面色蒼白、身著白衣的女子；她歌唱，引導靈魂穿越地下世界的水域。",
        powers_en=["Spiritual guidance", "Dream work", "Soul healing"],
        powers_cn=["靈性指引", "夢境工作", "靈魂療癒"],
        incense="Camphor and white sandalwood", incense_cn="樟腦與白檀香",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
    DecanTalisman(
        decan_number=36, sign="Pisces", sign_cn="雙魚座",
        decan_in_sign=3, degrees_start=20, degrees_end=30, ruler="Saturn", ruler_cn="土星",
        image_description_en=(
            "An old man with a long beard, sitting on a throne of clouds; "
            "he is the final keeper, the one who dissolves all forms into eternity."
        ),
        image_description_cn="一個長鬚老人，坐在雲霧之座上；他是最終守護者，將一切形式溶解入永恆者。",
        powers_en=["Liberation", "Dissolution of obstacles", "Spiritual completion"],
        powers_cn=["解脫", "化解障礙", "靈性圓滿"],
        incense="Myrrh and asafoetida", incense_cn="沒藥與阿魏",
        picatrix_source="Picatrix Bk II Ch. 11",
    ),
]

# 建立 Decan 快速查詢字典
DECAN_TALISMAN_BY_NUMBER: Dict[int, DecanTalisman] = {
    d.decan_number: d for d in DECAN_TALISMANS
}

DECAN_TALISMAN_BY_SIGN: Dict[str, List[DecanTalisman]] = {}
for _d in DECAN_TALISMANS:
    DECAN_TALISMAN_BY_SIGN.setdefault(_d.sign, []).append(_d)


# ============================================================
# 目的 → 行星 / Decan / Fixed Star 推薦映射
# ============================================================

PURPOSE_TO_PLANETS: Dict[str, List[str]] = {
    # 愛情與吸引力
    "love":          ["Venus", "Moon"],
    "attraction":    ["Venus", "Sun"],
    "reconciliation":["Venus", "Moon"],
    # 財富與繁榮
    "wealth":        ["Jupiter", "Venus", "Sun"],
    "fortune":       ["Jupiter", "Sun"],
    "commerce":      ["Mercury", "Venus", "Jupiter"],
    # 保護與防禦
    "protection":    ["Saturn", "Mars", "Sun"],
    "banishing":     ["Saturn", "Mars"],
    "binding":       ["Saturn"],
    # 健康與療癒
    "health":        ["Sun", "Moon", "Jupiter"],
    "healing":       ["Moon", "Sun"],
    "fertility":     ["Moon", "Venus", "Jupiter"],
    # 智慧與知識
    "wisdom":        ["Mercury", "Saturn", "Sun"],
    "learning":      ["Mercury", "Jupiter"],
    "divination":    ["Moon", "Mercury", "Saturn"],
    # 權力與地位
    "power":         ["Sun", "Jupiter", "Mars"],
    "authority":     ["Sun", "Jupiter"],
    "victory":       ["Mars", "Sun", "Jupiter"],
    # 旅行與溝通
    "travel":        ["Mercury", "Moon"],
    "communication": ["Mercury"],
    # 運動與競技
    "sports":        ["Mars", "Sun"],
    # 農業與自然
    "agriculture":   ["Moon", "Saturn", "Jupiter"],
}

PURPOSE_LABELS_CN: Dict[str, str] = {
    "love":          "愛情",
    "attraction":    "吸引力",
    "reconciliation":"和解",
    "wealth":        "財富",
    "fortune":       "好運",
    "commerce":      "商業",
    "protection":    "保護",
    "banishing":     "驅逐",
    "binding":       "束縛",
    "health":        "健康",
    "healing":       "療癒",
    "fertility":     "生育",
    "wisdom":        "智慧",
    "learning":      "學習",
    "divination":    "占卜",
    "power":         "權力",
    "authority":     "權威",
    "victory":       "勝利",
    "travel":        "旅行",
    "communication": "溝通",
    "sports":        "競技",
    "agriculture":   "農業",
}

# 所有目的的中英文標籤
ALL_PURPOSES: List[Dict[str, str]] = [
    {"key": k, "en": k.title(), "cn": v}
    for k, v in PURPOSE_LABELS_CN.items()
]


# ============================================================
# 便利查詢函式
# ============================================================

def get_planetary_talisman(planet: str) -> Optional[PlanetaryTalisman]:
    """根據行星名稱取得護符資料。"""
    return PLANETARY_TALISMAN_BY_PLANET.get(planet)


def get_decan_by_longitude(longitude: float) -> Optional[DecanTalisman]:
    """根據黃道經度取得對應的 Decan 護符。"""
    lon_norm = longitude % 360.0
    decan_index = int(lon_norm / 10.0) + 1  # 1–36
    return DECAN_TALISMAN_BY_NUMBER.get(decan_index)


def get_recommended_planets(purpose: str) -> List[str]:
    """根據目的關鍵字取得推薦行星列表。"""
    # 直接匹配
    if purpose in PURPOSE_TO_PLANETS:
        return PURPOSE_TO_PLANETS[purpose]
    # 模糊匹配（找包含 purpose 關鍵字的第一個）
    for key, planets in PURPOSE_TO_PLANETS.items():
        if purpose.lower() in key.lower() or key.lower() in purpose.lower():
            return planets
    return ["Jupiter", "Sun"]  # 預設返回木星、太陽


def get_decan_by_number(n: int) -> Optional[DecanTalisman]:
    """根據 Decan 序號（1-36）取得護符資料。"""
    return DECAN_TALISMAN_BY_NUMBER.get(n)
