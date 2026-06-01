"""馬來群島時間占卜資料集（Ketika Lima / Bintang Tujuh）。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


# 吉凶標籤（固定三類）
FORTUNE_LABELS: Dict[str, Dict[str, str]] = {
    "baik": {"en": "Auspicious ✨", "zh": "吉 ✨"},
    "nahas": {"en": "Inauspicious ⚠️", "zh": "凶 ⚠️"},
    "sederhana": {"en": "Moderate / Neutral 🔸", "zh": "中平 🔸"},
}

# 活動類型（活動規劃器用）
ACTIVITY_CATALOGUE: Dict[str, Dict[str, str]] = {
    "sailing": {"en": "Sailing / Travel", "zh": "航海／出行"},
    "marriage": {"en": "Marriage / Engagement", "zh": "婚姻／訂婚"},
    "building": {"en": "Building / Groundbreaking", "zh": "建屋／動土"},
    "healing": {"en": "Healing / Medicine", "zh": "療癒／醫藥"},
    "business": {"en": "Business / Trade", "zh": "生意／貿易"},
    "study": {"en": "Study / Learning", "zh": "學習／進修"},
    "prayer": {"en": "Prayer / Spiritual", "zh": "祈禱／靈修"},
    "agriculture": {"en": "Agriculture / Planting", "zh": "農耕／種植"},
    "meeting": {"en": "Meeting / Negotiation", "zh": "會面／談判"},
    "ceremony": {"en": "Ceremony / Celebration", "zh": "慶典／儀式"},
    "war": {"en": "Warfare / Competition", "zh": "戰事／競爭"},
    "rest": {"en": "Rest / Retreat", "zh": "休息／靜養"},
}


@dataclass(frozen=True)
class KetikaPeriod:
    """單一時段資料。"""

    index: int
    name_malay: str  # 保留原始傳統命名，必要時可附帶祈禱時段註記（如 Subuh）
    name_en: str
    name_zh: str
    time_start: str
    time_end: str
    fortune: str
    colour: str
    emoji: str
    planet_or_star: str
    good_activities: List[str] = field(default_factory=list)
    bad_activities: List[str] = field(default_factory=list)
    note_en: str = ""
    note_zh: str = ""


KETIKA_LIMA: List[KetikaPeriod] = [
    KetikaPeriod(
        index=1,
        name_malay="Maswara (Subuh)",
        name_en="Dawn — Maswara",
        name_zh="黎明 — 瑪斯瓦拉（晨禮）",
        time_start="05:00",
        time_end="08:00",
        fortune="baik",
        colour="#D4AF37",
        emoji="🌅",
        planet_or_star="Zuhrah (Venus)",
        good_activities=["prayer", "healing", "study", "agriculture"],
        bad_activities=["war", "business"],
        note_en=(
            "The dawn period is ruled by Maswara, a gentle and sacred energy. "
            "Traditional Malay healers (bomoh) consider this the best time for "
            "spiritual cleansing, reciting doa, and beginning new learning."
        ),
        note_zh=(
            "黎明時段由瑪斯瓦拉主宰，能量溫和而神聖。"
            "傳統馬來療癒師（Bomoh）認為此時最適合靈性淨化、"
            "誦念祈禱詞（Doa）及展開新的學習。"
        ),
    ),
    KetikaPeriod(
        index=2,
        name_malay="Kala (Zohor)",
        name_en="Midday — Kala",
        name_zh="正午 — 卡拉（午禮）",
        time_start="08:00",
        time_end="12:00",
        fortune="nahas",
        colour="#8B0000",
        emoji="☀️",
        planet_or_star="Marikh (Mars)",
        good_activities=["war", "meeting"],
        bad_activities=["marriage", "sailing", "building", "healing"],
        note_en=(
            "Kala is associated with fierce and aggressive energy (Mars). "
            "Manuscripts warn against starting marriages, voyages, or "
            "construction during this period."
        ),
        note_zh=(
            "卡拉與火星的猛烈攻擊性能量相關。"
            "手稿警告此時段不宜展開婚事、航行或建造工程。"
        ),
    ),
    KetikaPeriod(
        index=3,
        name_malay="Sri (Asar)",
        name_en="Afternoon — Sri",
        name_zh="下午 — 斯里（晡禮）",
        time_start="12:00",
        time_end="16:00",
        fortune="baik",
        colour="#228B22",
        emoji="🌿",
        planet_or_star="Musytari (Jupiter)",
        good_activities=["business", "marriage", "ceremony", "meeting", "building"],
        bad_activities=["rest"],
        note_en=(
            "Sri carries the benevolent influence of Jupiter — prosperity and success. "
            "This is a favoured period for trade, weddings, and important negotiations."
        ),
        note_zh=(
            "斯里承載木星的慈愛影響——繁榮與成功。"
            "此時段最受傳統推崇，適合貿易、婚禮及重要談判。"
        ),
    ),
    KetikaPeriod(
        index=4,
        name_malay="Laba (Maghrib)",
        name_en="Dusk — Laba",
        name_zh="黃昏 — 拉巴（昏禮）",
        time_start="16:00",
        time_end="20:00",
        fortune="sederhana",
        colour="#DAA520",
        emoji="🌇",
        planet_or_star="Utarid (Mercury)",
        good_activities=["prayer", "healing", "rest", "study"],
        bad_activities=["sailing", "building", "war"],
        note_en=(
            "Laba is a transitional time governed by Mercury — quick-witted but unpredictable. "
            "Suitable for intellectual and spiritual pursuits."
        ),
        note_zh=(
            "拉巴是由水星主宰的過渡時段——敏銳但難以預測。"
            "適合知識性與靈修活動。"
        ),
    ),
    KetikaPeriod(
        index=5,
        name_malay="Dana (Isyak)",
        name_en="Night — Dana",
        name_zh="夜晚 — 達那（宵禮）",
        time_start="20:00",
        time_end="05:00",
        fortune="sederhana",
        colour="#191970",
        emoji="🌙",
        planet_or_star="Zuhal (Saturn)",
        good_activities=["prayer", "rest", "study", "healing"],
        bad_activities=["sailing", "business", "building", "agriculture"],
        note_en=(
            "Dana falls under Saturn's deep, contemplative energy. "
            "The night is reserved for rest, devotion, and inner work."
        ),
        note_zh=(
            "達那處於土星深沉、沉思的能量之下。"
            "夜晚宜用於休息、祈禱和內省。"
        ),
    ),
]


BINTANG_TUJUH: List[KetikaPeriod] = [
    KetikaPeriod(
        index=1,
        name_malay="Bintang Syams (Matahari)",
        name_en="Star of the Sun",
        name_zh="太陽星",
        time_start="05:00",
        time_end="08:25",
        fortune="baik",
        colour="#FFD700",
        emoji="☀️",
        planet_or_star="Syams (Sun / 太陽)",
        good_activities=["prayer", "ceremony", "business", "meeting"],
        bad_activities=["rest"],
        note_en=(
            "Ruled by the Sun — authority, clarity, and new beginnings. "
            "Ideal for opening ceremonies and enterprise launches."
        ),
        note_zh=(
            "由太陽主宰——代表權威、明晰與新的開端。"
            "最適合開幕儀式與展開事業。"
        ),
    ),
    KetikaPeriod(
        index=2,
        name_malay="Bintang Qamar (Bulan)",
        name_en="Star of the Moon",
        name_zh="月亮星",
        time_start="08:25",
        time_end="11:50",
        fortune="baik",
        colour="#C0C0C0",
        emoji="🌙",
        planet_or_star="Qamar (Moon / 月亮)",
        good_activities=["healing", "agriculture", "marriage", "study"],
        bad_activities=["war", "sailing"],
        note_en="The Moon bestows gentle, nurturing energy, favoured for healing and unions.",
        note_zh="月亮賦予溫和滋養的能量，適合療癒與婚戀。",
    ),
    KetikaPeriod(
        index=3,
        name_malay="Bintang Marikh (Merah)",
        name_en="Star of Mars",
        name_zh="火星",
        time_start="11:50",
        time_end="15:15",
        fortune="nahas",
        colour="#DC143C",
        emoji="🔴",
        planet_or_star="Marikh (Mars / 火星)",
        good_activities=["war"],
        bad_activities=["marriage", "building", "sailing", "business", "healing"],
        note_en="Mars brings aggressive, disruptive energy and is generally a nahas period.",
        note_zh="火星帶來攻擊性與破壞性能量，通常被視為凶時。",
    ),
    KetikaPeriod(
        index=4,
        name_malay="Bintang Utarid (Kelabu)",
        name_en="Star of Mercury",
        name_zh="水星",
        time_start="15:15",
        time_end="18:40",
        fortune="sederhana",
        colour="#708090",
        emoji="⚡",
        planet_or_star="Utarid (Mercury / 水星)",
        good_activities=["study", "meeting", "business"],
        bad_activities=["building", "agriculture"],
        note_en="Mercury favours communication and study; physical projects are less stable.",
        note_zh="水星有利溝通與學習；實體工程較不穩定。",
    ),
    KetikaPeriod(
        index=5,
        name_malay="Bintang Musytari (Hijau)",
        name_en="Star of Jupiter",
        name_zh="木星",
        time_start="18:40",
        time_end="22:05",
        fortune="baik",
        colour="#006400",
        emoji="🍀",
        planet_or_star="Musytari (Jupiter / 木星)",
        good_activities=["marriage", "business", "ceremony", "building", "meeting"],
        bad_activities=["war"],
        note_en="Jupiter radiates abundance and honour; one of the most auspicious periods.",
        note_zh="木星象徵豐饒與榮譽，是最吉利的時段之一。",
    ),
    KetikaPeriod(
        index=6,
        name_malay="Bintang Zuhrah (Putih)",
        name_en="Star of Venus",
        name_zh="金星",
        time_start="22:05",
        time_end="01:30",
        fortune="baik",
        colour="#FF69B4",
        emoji="💖",
        planet_or_star="Zuhrah (Venus / 金星)",
        good_activities=["marriage", "healing", "prayer", "rest", "ceremony"],
        bad_activities=["war", "agriculture"],
        note_en="Venus brings love, beauty, and ritual harmony.",
        note_zh="金星帶來愛、美與和諧，適合浪漫與靈修。",
    ),
    KetikaPeriod(
        index=7,
        name_malay="Bintang Zuhal (Hitam)",
        name_en="Star of Saturn",
        name_zh="土星",
        time_start="01:30",
        time_end="05:00",
        fortune="nahas",
        colour="#2F2F2F",
        emoji="🪐",
        planet_or_star="Zuhal (Saturn / 土星)",
        good_activities=["rest", "prayer"],
        bad_activities=["sailing", "marriage", "building", "business", "agriculture", "meeting"],
        note_en="Saturn's heavy night energy is inauspicious for worldly ventures.",
        note_zh="土星深夜能量沉重，多數世俗活動被視為不宜。",
    ),
]


def time_to_minutes(time_value: str) -> int:
    """將 HH:MM 轉為分鐘。"""
    hour, minute = map(int, time_value.split(":"))
    return hour * 60 + minute
