"""
Picatrix (Ghayat al-Hakim) Data Module
資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
Greer & Warnock 2011 translation / Attrell & Porreca 2019

28 Lunar Mansions (Manazil al-Qamar / 阿拉伯月宿) complete attributes.
Planetary Hours (行星時) Chaldean order data.
Talisman intent mappings (護符意圖對應).

All data sourced directly from Picatrix classical text.
Do NOT modify without consulting primary sources.
"""

from __future__ import annotations
import json
import streamlit as st
from pathlib import Path
from typing import Any
from html import escape


# ====================== 資料載入函式 ======================
@st.cache_data(show_spinner=False)
def _load_json(filename: str) -> dict[str, Any]:
    """從 data/ 資料夾載入 JSON (cached)"""
    json_path = Path(__file__).parent.parent / "data" / filename
    if not json_path.exists():
        raise FileNotFoundError(f"找不到 Picatrix 資料檔：{json_path}")
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)
# ============================================================
# 28 Lunar Mansions — Picatrix Complete Data
# (Manazil al-Qamar / 阿拉伯月宿)
# ============================================================
# Each mansion spans 360/28 ≈ 12.857° of ecliptic longitude.
# start_degree = index * (360 / 28)
# fortunate / unfortunate per Picatrix Book I, Ch. 4
# ============================================================

PICATRIX_MANSIONS: list[dict] = [
    {
        "index": 0,
        "arabic_name": "Al-Sharatain",
        "arabic_script": "الشرطين",
        "english_name": "The Two Signs / The Horns",
        "chinese_name": "婁宿",
        "ruling_planet": "Saturn",
        "fortunate": True,
        "magic_image": (
            "A black man, tall and large, wearing a cloak and standing in the air"
        ),
        "magic_image_cn": "一個高大的黑人，身披斗篷，立於空中",
        "purposes": ["journeys", "journeys by sea", "good beginnings"],
        "purposes_cn": ["旅行", "海上旅行", "吉祥開端"],
        "incense": "pepper",
        "color": "black",
        "metal": "iron",
        "invocation_summary": "For journeys and beginnings; invoke Saturn",
        "start_degree": 0.0,
    },
    {
        "index": 1,
        "arabic_name": "Al-Butain",
        "arabic_script": "البطين",
        "english_name": "The Belly (of Aries)",
        "chinese_name": "胃宿",
        "ruling_planet": "Saturn",
        "fortunate": True,
        "magic_image": "A crowned king on a throne",
        "magic_image_cn": "一個戴冠的國王坐在王座上",
        "purposes": [
            "finding hidden treasures",
            "helping those in captivity",
            "harm of enemies",
        ],
        "purposes_cn": ["尋找寶藏", "幫助囚犯", "克敵"],
        "incense": "camphor",
        "color": "white",
        "metal": "silver",
        "invocation_summary": "For finding treasures and helping captives; invoke the Moon",
        "start_degree": 360 / 28 * 1,
    },
    {
        "index": 2,
        "arabic_name": "Al-Thurayya",
        "arabic_script": "الثريا",
        "english_name": "The Many Little Ones / Pleiades",
        "chinese_name": "昴宿",
        "ruling_planet": "Jupiter",
        "fortunate": True,
        "magic_image": (
            "A woman dressed in new clothes, with her hands on her head"
        ),
        "magic_image_cn": "一個穿著新衣服的女人，雙手置於頭上",
        "purposes": ["gain and merchandise", "safe navigation", "alchemy"],
        "purposes_cn": ["獲利與貿易", "安全航行", "煉金術"],
        "incense": "frankincense",
        "color": "golden yellow",
        "metal": "gold",
        "invocation_summary": "For commerce and navigation; invoke Jupiter",
        "start_degree": 360 / 28 * 2,
    },
    {
        "index": 3,
        "arabic_name": "Al-Dabaran",
        "arabic_script": "الدبران",
        "english_name": "The Follower / Aldebaran",
        "chinese_name": "畢宿",
        "ruling_planet": "Mars",
        "fortunate": False,
        "magic_image": "A rider on a horse bearing a serpent in his right hand",
        "magic_image_cn": "一個騎馬的人，右手持蛇",
        "purposes": [
            "destroying towns",
            "harming buildings and travelers",
            "causing discord",
        ],
        "purposes_cn": ["破壞城鎮", "危害建築與旅者", "製造紛爭"],
        "incense": "red myrrh",
        "color": "red",
        "metal": "iron",
        "invocation_summary": "For conflict and destruction; invoke Mars",
        "start_degree": 360 / 28 * 3,
    },
    {
        "index": 4,
        "arabic_name": "Al-Haqa",
        "arabic_script": "الهقعة",
        "english_name": "The White Spot / Orion's Head",
        "chinese_name": "觜宿",
        "ruling_planet": "Sun",
        "fortunate": True,
        "magic_image": "A head of a man with no body but with a crown",
        "magic_image_cn": "一個無軀幹的人頭，頭戴王冠",
        "purposes": ["reconciling a husband and wife", "sieges and prisons"],
        "purposes_cn": ["夫妻和好", "圍困與監獄"],
        "incense": "saffron",
        "color": "yellow",
        "metal": "gold",
        "invocation_summary": "For reconciliation and binding; invoke the Sun",
        "start_degree": 360 / 28 * 4,
    },
    {
        "index": 5,
        "arabic_name": "Al-Hana",
        "arabic_script": "الهنعة",
        "english_name": "The Brand Mark",
        "chinese_name": "參宿",
        "ruling_planet": "Mercury",
        "fortunate": True,
        "magic_image": "Two dark images embracing one another",
        "magic_image_cn": "兩個深色人像相互擁抱",
        "purposes": ["love and friendship", "good travel", "freedom from shackles"],
        "purposes_cn": ["愛情與友誼", "順利旅行", "解除束縛"],
        "incense": "mastic",
        "color": "red",
        "metal": "copper",
        "invocation_summary": "For love, friendship, and freedom; invoke Mercury",
        "start_degree": 360 / 28 * 5,
    },
    {
        "index": 6,
        "arabic_name": "Al-Dhira",
        "arabic_script": "الذراع",
        "english_name": "The Forearm (of Gemini)",
        "chinese_name": "井宿",
        "ruling_planet": "Moon",
        "fortunate": True,
        "magic_image": (
            "A man dressed in fine clothes, with his hands raised to the sky, rejoicing"
        ),
        "magic_image_cn": "一個穿著華麗衣服的男人，雙手舉向天空，面露喜色",
        "purposes": ["gain profits and acquire riches", "love and friendship", "safe journeys"],
        "purposes_cn": ["獲利致富", "愛情與友誼", "安全旅行"],
        "incense": "wood aloe",
        "color": "green",
        "metal": "silver",
        "invocation_summary": "For wealth, love, and journey safety; invoke the Moon",
        "start_degree": 360 / 28 * 6,
    },
    {
        "index": 7,
        "arabic_name": "Al-Nathra",
        "arabic_script": "النثرة",
        "english_name": "The Gap / Praesepe",
        "chinese_name": "鬼宿",
        "ruling_planet": "Saturn",
        "fortunate": False,
        "magic_image": "A lion with the head of a man, holding a sword",
        "magic_image_cn": "一隻長有人頭的獅子，手持寶劍",
        "purposes": [
            "driving away hatred",
            "expelling captives",
            "destruction of enemies",
        ],
        "purposes_cn": ["消除仇恨", "驅逐囚犯", "消滅敵人"],
        "incense": "sulfur",
        "color": "black",
        "metal": "lead",
        "invocation_summary": "For driving away enemies and captives; invoke Saturn",
        "start_degree": 360 / 28 * 7,
    },
    {
        "index": 8,
        "arabic_name": "Al-Tarf",
        "arabic_script": "الطرف",
        "english_name": "The Gaze / Eye",
        "chinese_name": "柳宿",
        "ruling_planet": "Mars",
        "fortunate": False,
        "magic_image": "A dark man with frightening features riding a serpent",
        "magic_image_cn": "一個面目可憎的黑人騎著一條蛇",
        "purposes": [
            "harming harvests and plantings",
            "discord between married couples",
            "destruction",
        ],
        "purposes_cn": ["破壞農作物", "破壞婚姻", "毀滅"],
        "incense": "red myrrh",
        "color": "red",
        "metal": "iron",
        "invocation_summary": "For harm and destruction; invoke Mars",
        "start_degree": 360 / 28 * 8,
    },
    {
        "index": 9,
        "arabic_name": "Al-Jabha",
        "arabic_script": "الجبهة",
        "english_name": "The Forehead (of Leo)",
        "chinese_name": "星宿",
        "ruling_planet": "Sun",
        "fortunate": True,
        "magic_image": "A crowned lion holding a sword in its right hand",
        "magic_image_cn": "一隻戴冠的獅子，右手持劍",
        "purposes": [
            "obtaining goodwill and benevolence",
            "curing illnesses",
            "hunting",
        ],
        "purposes_cn": ["獲得善意與慈悲", "治癒疾病", "狩獵"],
        "incense": "saffron",
        "color": "golden",
        "metal": "gold",
        "invocation_summary": "For goodwill, healing, and hunting; invoke the Sun",
        "start_degree": 360 / 28 * 9,
    },
    {
        "index": 10,
        "arabic_name": "Al-Zubra",
        "arabic_script": "الزبرة",
        "english_name": "The Mane (of Leo)",
        "chinese_name": "張宿",
        "ruling_planet": "Mercury",
        "fortunate": True,
        "magic_image": "A man with a long beard, sitting and writing",
        "magic_image_cn": "一個留著長鬍鬚的男人，坐著書寫",
        "purposes": [
            "concord and good will",
            "friendship between allies",
            "freeing captives",
        ],
        "purposes_cn": ["和諧與善意", "盟友之間的友誼", "釋放囚犯"],
        "incense": "mastic",
        "color": "white",
        "metal": "silver",
        "invocation_summary": "For friendship and freeing captives; invoke Mercury",
        "start_degree": 360 / 28 * 10,
    },
    {
        "index": 11,
        "arabic_name": "Al-Sarfa",
        "arabic_script": "الصرفة",
        "english_name": "The Changer (of Weather)",
        "chinese_name": "翼宿",
        "ruling_planet": "Jupiter",
        "fortunate": True,
        "magic_image": "A dog standing upright with its tail raised",
        "magic_image_cn": "一隻直立站立的狗，尾巴高舉",
        "purposes": ["planting and agriculture", "profit and gain"],
        "purposes_cn": ["種植與農業", "獲利致富"],
        "incense": "frankincense",
        "color": "yellow",
        "metal": "tin",
        "invocation_summary": "For agriculture and profit; invoke Jupiter",
        "start_degree": 360 / 28 * 11,
    },
    {
        "index": 12,
        "arabic_name": "Al-Awwa",
        "arabic_script": "العواء",
        "english_name": "The Barking Dog / The Howler",
        "chinese_name": "軫宿",
        "ruling_planet": "Venus",
        "fortunate": True,
        "magic_image": "A woman holding two men by their hair",
        "magic_image_cn": "一個女人用雙手各抓住一個男人的頭髮",
        "purposes": ["benevolence and love", "voyages and travel", "gaining wealth"],
        "purposes_cn": ["善意與愛情", "航行與旅行", "獲得財富"],
        "incense": "mastic",
        "color": "green",
        "metal": "copper",
        "invocation_summary": "For love, travel, and wealth; invoke Venus",
        "start_degree": 360 / 28 * 12,
    },
    {
        "index": 13,
        "arabic_name": "Al-Simak",
        "arabic_script": "السماك",
        "english_name": "The Unarmed / Spica Virginis",
        "chinese_name": "角宿",
        "ruling_planet": "Mercury",
        "fortunate": True,
        "magic_image": "A sitting man holding a lance in his right hand",
        "magic_image_cn": "一個坐著的男人，右手持長矛",
        "purposes": ["amity and love between married couples", "healing"],
        "purposes_cn": ["夫妻情愛", "療癒"],
        "incense": "frankincense",
        "color": "white",
        "metal": "gold",
        "invocation_summary": "For love and healing; invoke Mercury",
        "start_degree": 360 / 28 * 13,
    },
    {
        "index": 14,
        "arabic_name": "Al-Ghafr",
        "arabic_script": "الغفر",
        "english_name": "The Cover / The Veil",
        "chinese_name": "亢宿",
        "ruling_planet": "Moon",
        "fortunate": True,
        "magic_image": "A man with his hands clasped above his head",
        "magic_image_cn": "一個雙手合十舉過頭頂的男人",
        "purposes": [
            "discovering hidden things",
            "freeing captives",
            "digging wells",
        ],
        "purposes_cn": ["發現隱藏之物", "釋放囚犯", "挖掘水井"],
        "incense": "camphor",
        "color": "white",
        "metal": "silver",
        "invocation_summary": "For uncovering secrets and captives; invoke the Moon",
        "start_degree": 360 / 28 * 14,
    },
    {
        "index": 15,
        "arabic_name": "Al-Zubana",
        "arabic_script": "الزبانى",
        "english_name": "The Claws (of Scorpio) / The Scales",
        "chinese_name": "氐宿",
        "ruling_planet": "Saturn",
        "fortunate": False,
        "magic_image": "A seated man whose face is inclined toward the earth",
        "magic_image_cn": "一個坐著的男人，臉朝向大地",
        "purposes": [
            "separating lovers",
            "destroying buildings",
            "causing sickness",
        ],
        "purposes_cn": ["分離戀人", "破壞建築", "致病"],
        "incense": "sulfur",
        "color": "black",
        "metal": "lead",
        "invocation_summary": "For separation and destruction; invoke Saturn",
        "start_degree": 360 / 28 * 15,
    },
    {
        "index": 16,
        "arabic_name": "Al-Iklil",
        "arabic_script": "الإكليل",
        "english_name": "The Crown (of Scorpio)",
        "chinese_name": "房宿",
        "ruling_planet": "Jupiter",
        "fortunate": True,
        "magic_image": "A king seated on a throne with his hands over his chest",
        "magic_image_cn": "一個坐在王座上的國王，雙手交疊於胸前",
        "purposes": ["goodness and union", "journeys and travel", "hunting and fishing"],
        "purposes_cn": ["善意與結合", "旅途", "狩獵與捕魚"],
        "incense": "frankincense",
        "color": "golden",
        "metal": "tin",
        "invocation_summary": "For goodness, travel, and hunting; invoke Jupiter",
        "start_degree": 360 / 28 * 16,
    },
    {
        "index": 17,
        "arabic_name": "Al-Qalb",
        "arabic_script": "القلب",
        "english_name": "The Heart (of Scorpio) / Antares",
        "chinese_name": "心宿",
        "ruling_planet": "Mars",
        "fortunate": False,
        "magic_image": "A scorpion being trampled by a man",
        "magic_image_cn": "一個男人踩踏一隻蠍子",
        "purposes": [
            "causing division",
            "evil works against enemies",
            "discord",
        ],
        "purposes_cn": ["製造分裂", "對敵人的惡意行為", "不和"],
        "incense": "red myrrh",
        "color": "red",
        "metal": "iron",
        "invocation_summary": "For conflict and division; invoke Mars",
        "start_degree": 360 / 28 * 17,
    },
    {
        "index": 18,
        "arabic_name": "Al-Shaula",
        "arabic_script": "الشولة",
        "english_name": "The Sting (of Scorpio)",
        "chinese_name": "尾宿",
        "ruling_planet": "Venus",
        "fortunate": False,
        "magic_image": "A figure holding a serpent in each hand",
        "magic_image_cn": "一個手持雙蛇的人",
        "purposes": ["casting spells", "binding enemies", "destructive magic"],
        "purposes_cn": ["施咒", "束縛敵人", "破壞性魔法"],
        "incense": "sulfur",
        "color": "dark red",
        "metal": "iron",
        "invocation_summary": "For binding and destructive spells; invoke Venus",
        "start_degree": 360 / 28 * 18,
    },
    {
        "index": 19,
        "arabic_name": "Al-Na'am",
        "arabic_script": "النعائم",
        "english_name": "The Ostriches",
        "chinese_name": "箕宿",
        "ruling_planet": "Mercury",
        "fortunate": True,
        "magic_image": "A man holding a bow and arrow",
        "magic_image_cn": "一個持弓箭的男人",
        "purposes": [
            "taming wild beasts",
            "strengthening prisons and captives",
            "gain",
        ],
        "purposes_cn": ["馴服野獸", "加強囚禁", "獲利"],
        "incense": "mastic",
        "color": "green",
        "metal": "quicksilver",
        "invocation_summary": "For taming and strengthening prisons; invoke Mercury",
        "start_degree": 360 / 28 * 19,
    },
    {
        "index": 20,
        "arabic_name": "Al-Balda",
        "arabic_script": "البلدة",
        "english_name": "The City / The Empty Area",
        "chinese_name": "斗宿",
        "ruling_planet": "Moon",
        "fortunate": True,
        "magic_image": "A woman with her hands placed over her head",
        "magic_image_cn": "一個雙手置於頭頂的女人",
        "purposes": [
            "taming beasts",
            "strengthening buildings",
            "freeing captives",
        ],
        "purposes_cn": ["馴服野獸", "加固建築", "釋放囚犯"],
        "incense": "camphor",
        "color": "white",
        "metal": "silver",
        "invocation_summary": "For taming, building, and captives; invoke the Moon",
        "start_degree": 360 / 28 * 20,
    },
    {
        "index": 21,
        "arabic_name": "Sa'd al-Dhabih",
        "arabic_script": "سعد الذابح",
        "english_name": "The Lucky Star of the Slaughterer",
        "chinese_name": "牛宿",
        "ruling_planet": "Saturn",
        "fortunate": False,
        "magic_image": "A man with a large sword in his hand, lying face down",
        "magic_image_cn": "一個手持大劍俯臥的男人",
        "purposes": [
            "escape from slavery",
            "bringing kindness",
            "healing diseases",
        ],
        "purposes_cn": ["逃脫奴役", "帶來善意", "治療疾病"],
        "incense": "camphor",
        "color": "black",
        "metal": "lead",
        "invocation_summary": "For freedom, kindness, and healing; invoke Saturn",
        "start_degree": 360 / 28 * 21,
    },
    {
        "index": 22,
        "arabic_name": "Sa'd al-Bula",
        "arabic_script": "سعد بلع",
        "english_name": "The Lucky Star of the Swallower",
        "chinese_name": "女宿",
        "ruling_planet": "Jupiter",
        "fortunate": True,
        "magic_image": "A man holding a woman by her hair while she looks at him",
        "magic_image_cn": "一個男人抓住女人的頭髮，而她注視著他",
        "purposes": [
            "healing diseases of the body",
            "purging evil spirits",
            "gain",
        ],
        "purposes_cn": ["治療身體疾病", "驅逐惡靈", "獲利"],
        "incense": "frankincense",
        "color": "yellow",
        "metal": "tin",
        "invocation_summary": "For healing and purging evil; invoke Jupiter",
        "start_degree": 360 / 28 * 22,
    },
    {
        "index": 23,
        "arabic_name": "Sa'd al-Su'ud",
        "arabic_script": "سعد السعود",
        "english_name": "The Luckiest of the Lucky",
        "chinese_name": "虛宿",
        "ruling_planet": "Saturn",
        "fortunate": True,
        "magic_image": "A man standing with his hands raised to the sky",
        "magic_image_cn": "一個雙手舉向天空的男人",
        "purposes": [
            "achieving all good things",
            "marriages and partnerships",
            "planting",
        ],
        "purposes_cn": ["達成一切好事", "婚姻與合夥", "種植"],
        "incense": "camphor",
        "color": "white",
        "metal": "silver",
        "invocation_summary": "For all goodness and marriages; invoke Saturn",
        "start_degree": 360 / 28 * 23,
    },
    {
        "index": 24,
        "arabic_name": "Sa'd al-Akhbiya",
        "arabic_script": "سعد الأخبية",
        "english_name": "The Lucky Stars of the Tents",
        "chinese_name": "危宿",
        "ruling_planet": "Mercury",
        "fortunate": True,
        "magic_image": "A man holding a key in his hand",
        "magic_image_cn": "一個手持鑰匙的男人",
        "purposes": [
            "building houses",
            "beneficial rain and plantings",
            "good luck",
        ],
        "purposes_cn": ["建造房屋", "有益的雨水與種植", "好運"],
        "incense": "mastic",
        "color": "green",
        "metal": "copper",
        "invocation_summary": "For building and planting; invoke Mercury",
        "start_degree": 360 / 28 * 24,
    },
    {
        "index": 25,
        "arabic_name": "Al-Fargh al-Awwal",
        "arabic_script": "الفرغ الأول",
        "english_name": "The First Spout (of the Water-Pourer)",
        "chinese_name": "室宿",
        "ruling_planet": "Jupiter",
        "fortunate": True,
        "magic_image": "A woman with her hair spread, clothed in a garment",
        "magic_image_cn": "一個髮絲散開的女人，身穿衣袍",
        "purposes": [
            "building houses",
            "constructing wells",
            "strengthening friendships",
        ],
        "purposes_cn": ["建造房屋", "挖掘水井", "加強友誼"],
        "incense": "frankincense",
        "color": "yellow",
        "metal": "tin",
        "invocation_summary": "For building and friendship; invoke Jupiter",
        "start_degree": 360 / 28 * 25,
    },
    {
        "index": 26,
        "arabic_name": "Al-Fargh al-Thani",
        "arabic_script": "الفرغ الثاني",
        "english_name": "The Second Spout (of the Water-Pourer)",
        "chinese_name": "壁宿",
        "ruling_planet": "Mars",
        "fortunate": True,
        "magic_image": "A woman raising her hand to her forehead",
        "magic_image_cn": "一個舉手置於前額的女人",
        "purposes": [
            "good will among allies",
            "completing buildings",
            "beneficial travel",
        ],
        "purposes_cn": ["盟友之間的善意", "完成建築", "有益旅行"],
        "incense": "red myrrh",
        "color": "red",
        "metal": "iron",
        "invocation_summary": "For goodwill and building completion; invoke Mars",
        "start_degree": 360 / 28 * 26,
    },
    {
        "index": 27,
        "arabic_name": "Batn al-Hut",
        "arabic_script": "بطن الحوت",
        "english_name": "The Belly of the Fish",
        "chinese_name": "奎宿",
        "ruling_planet": "Moon",
        "fortunate": True,
        "magic_image": "A fish swimming with its head raised upward",
        "magic_image_cn": "一條頭部朝上游動的魚",
        "purposes": [
            "increase in merchandise and gain",
            "good navigation",
            "all fortunate works",
        ],
        "purposes_cn": ["增加商品與收益", "良好航行", "一切吉祥之事"],
        "incense": "camphor",
        "color": "white",
        "metal": "silver",
        "invocation_summary": "For all fortunate works; invoke the Moon",
        "start_degree": 360 / 28 * 27,
    },
]

# ====================== 載入各 JSON ======================
GREER_MANSIONS = _load_json("picatrix_mansions_greer.json")["mansions"]
TALISMANS = _load_json("picatrix_talismans.json")["talismans"]
CORRESPONDENCES = _load_json("picatrix_planetary_correspondences.json")["planets"]
NATURAL_RECIPES = _load_json("picatrix_natural_recipes.json")["recipes"]
SPIRITS_LIBRARY = _load_json("picatrix_spirits.json")
INCENSES = _load_json("picatrix_incenses.json")
PICATRIX_INCENSES = {
    "planets": INCENSES["planets"],
    "special_ointments": INCENSES["special_ointments"],
    "general_rules": INCENSES["general_rules"]
}


def _figure_svg_template(planet_zh: str, tradition: str) -> str:
    safe_planet = escape(planet_zh)
    safe_tradition = escape(tradition)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180">'
        '<rect width="320" height="180" fill="#111"/>'
        f'<text x="160" y="72" text-anchor="middle" fill="#f4d06f" font-size="20">{safe_planet}</text>'
        f'<text x="160" y="108" text-anchor="middle" fill="#d0d0d0" font-size="14">{safe_tradition}</text>'
        '</svg>'
    )


def _build_spirits_map() -> dict[str, dict[str, str]]:
    mapped: dict[str, dict[str, str]] = {}
    for planet_key, spirit in SPIRITS_LIBRARY.get("spirits", {}).items():
        mapped[planet_key] = {
            "name": spirit.get("chinese_name", planet_key),
            "arabic": spirit.get("arabic_name", ""),
            "latin": spirit.get("latin_name", ""),
        }
    return mapped


def _build_figures() -> list[dict[str, str]]:
    data: list[dict[str, str]] = []
    for planet_key, spirit in SPIRITS_LIBRARY.get("spirits", {}).items():
        for fig in spirit.get("figures", []):
            tradition = fig.get("tradition", "傳統")
            data.append(
                {
                    "planet": planet_key,
                    "tradition": tradition,
                    "description": fig.get("desc", ""),
                    "svg_template": _figure_svg_template(planet_key, tradition),
                }
            )
    return data


def _expand_correspondences() -> list[dict[str, Any]]:
    spirit_by_en = {
        spirit.get("planet", ""): spirit
        for spirit in SPIRITS_LIBRARY.get("spirits", {}).values()
    }
    expanded: list[dict[str, Any]] = []
    for item in CORRESPONDENCES:
        spirit = spirit_by_en.get(item.get("planet", ""), {})
        merged = dict(item)
        merged["direction"] = spirit.get("direction", "")
        merged["stones"] = spirit.get("stones", [])
        merged["colors"] = spirit.get("colors", [])
        merged["suffumigation"] = spirit.get("suffumigation", item.get("incense", ""))
        if not merged.get("stone") and merged["stones"]:
            merged["stone"] = "、".join(merged["stones"])
        expanded.append(merged)
    return expanded


spirits = _build_spirits_map()
figures = _build_figures()
correspondences = _expand_correspondences()

# ====================== 自動合併 Greer 詳細資料 ======================
def enrich_mansions():
    """把 Greer 版的詳細用途、圖像、注意事項合併到原有 Mansions"""
    greer_dict = {m["number"]: m for m in GREER_MANSIONS}
    for mansion in PICATRIX_MANSIONS:
        num = mansion.get("index", 0) + 1
        if num in greer_dict:
            g = greer_dict[num]
            mansion.update({
                "greer_name_en": g["name_en"],
                "greer_name_zh": g["name_zh"],
                "good_uses": g.get("good_uses", []),
                "bad_uses": g.get("bad_uses", []),
                "detailed_image": g.get("image", ""),
                "notes": g.get("notes", ""),
                "start_degree": g["start_deg"],
                "end_degree": g["end_deg"],
            })
    return PICATRIX_MANSIONS

# 執行合併
PICATRIX_MANSIONS = enrich_mansions()

# ====================== 公開變數（直接 import 使用）======================
PICATRIX_TALISMANS = TALISMANS
PICATRIX_SPIRITS = spirits
PICATRIX_FIGURES = figures
PICATRIX_CORRESPONDENCES = correspondences
PICATRIX_NATURAL_RECIPES = NATURAL_RECIPES

# ====================== 輔助函式 ======================
def get_mansion_by_degree(longitude: float) -> dict | None:
    """根據月亮黃道經度回傳目前月宮"""
    lon = longitude % 360
    for m in PICATRIX_MANSIONS:
        if m.get("start_degree") <= lon < m.get("end_degree", 360):
            return m
    return None

def get_talismans_by_purpose(keyword: str) -> list[dict]:
    """依用途關鍵字搜尋圖像配方"""
    keyword = keyword.lower()
    return [t for t in PICATRIX_TALISMANS if keyword in t["purpose"].lower()]



# ============================================================
# Planetary Hours — Chaldean Order
# 行星時序 (Chaldean Order: Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon)
# ============================================================
# Source: Picatrix Book III, Ch. 9; also standard classical tradition.
# Day 0 = Sunday, Day 1 = Monday, ..., Day 6 = Saturday
# The first hour of each day is ruled by the day planet.
# Chaldean order (slowest to fastest): Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon
# ============================================================

CHALDEAN_ORDER: list[str] = [
    "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"
]

# Glyph and Chinese name for each planet
PLANET_GLYPHS: dict[str, str] = {
    "Saturn": "♄",
    "Jupiter": "♃",
    "Mars": "♂",
    "Sun": "☉",
    "Venus": "♀",
    "Mercury": "☿",
    "Moon": "☽",
}

PLANET_NAMES_CN: dict[str, str] = {
    "Saturn": "土星",
    "Jupiter": "木星",
    "Mars": "火星",
    "Sun": "太陽",
    "Venus": "金星",
    "Mercury": "水星",
    "Moon": "月亮",
}

# Day planet: which Chaldean planet rules each weekday
# Sunday=0 → Sun (index 3), Monday=1 → Moon (index 6), ...
DAY_PLANETS: dict[int, str] = {
    0: "Sun",      # Sunday
    1: "Moon",     # Monday
    2: "Mars",     # Tuesday
    3: "Mercury",  # Wednesday
    4: "Jupiter",  # Thursday
    5: "Venus",    # Friday
    6: "Saturn",   # Saturday
}

DAY_NAMES_EN: dict[int, str] = {
    0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
    4: "Thursday", 5: "Friday", 6: "Saturday",
}

DAY_NAMES_CN: dict[int, str] = {
    0: "星期日", 1: "星期一", 2: "星期二", 3: "星期三",
    4: "星期四", 5: "星期五", 6: "星期六",
}

# ============================================================
# Talisman Intent Mapping — Picatrix Book II
# 護符意圖對應 (Talisman intent → recommended planet, mansion range, material)
# Source: Picatrix Book II, Ch. 10-12
# ============================================================

TALISMAN_INTENTS: list[dict] = [
    {
        "intent_key": "love",
        "intent_cn": "愛情",
        "intent_en": "Love & Romance",
        "planet": "Venus",
        "mansion_indices": [5, 6, 12, 13],
        "metal": "copper",
        "incense": "mastic",
        "color": "green",
        "hour_planet": "Venus",
        "description_cn": "在金星時辰，月亮行經第 6、7、13 或 14 宿，以銅鑄刻金星圖像",
        "description_en": (
            "In the Venus hour, with Moon in mansions 6, 7, 13 or 14; "
            "engrave Venus image in copper"
        ),
    },
    {
        "intent_key": "wealth",
        "intent_cn": "財富",
        "intent_en": "Wealth & Prosperity",
        "planet": "Jupiter",
        "mansion_indices": [2, 11, 16, 22, 25],
        "metal": "tin",
        "incense": "frankincense",
        "color": "yellow",
        "hour_planet": "Jupiter",
        "description_cn": "在木星時辰，月亮行經第 3、12、17、23 或 26 宿，以錫鑄刻木星圖像",
        "description_en": (
            "In the Jupiter hour, with Moon in mansions 3, 12, 17, 23 or 26; "
            "engrave Jupiter image in tin"
        ),
    },
    {
        "intent_key": "health",
        "intent_cn": "治病",
        "intent_en": "Health & Healing",
        "planet": "Sun",
        "mansion_indices": [4, 9, 21, 22],
        "metal": "gold",
        "incense": "saffron",
        "color": "golden",
        "hour_planet": "Sun",
        "description_cn": "在太陽時辰，月亮行經第 5、10、22 或 23 宿，以金鑄刻太陽圖像",
        "description_en": (
            "In the Sun hour, with Moon in mansions 5, 10, 22 or 23; "
            "engrave Sun image in gold"
        ),
    },
    {
        "intent_key": "travel",
        "intent_cn": "旅行",
        "intent_en": "Safe Travel",
        "planet": "Mercury",
        "mansion_indices": [0, 6, 16, 19, 24],
        "metal": "quicksilver",
        "incense": "mastic",
        "color": "green",
        "hour_planet": "Mercury",
        "description_cn": "在水星時辰，月亮行經第 1、7、17、20 或 25 宿，以水銀為引",
        "description_en": (
            "In the Mercury hour, with Moon in mansions 1, 7, 17, 20 or 25; "
            "use quicksilver as medium"
        ),
    },
    {
        "intent_key": "protection",
        "intent_cn": "保護",
        "intent_en": "Protection & Warding",
        "planet": "Mars",
        "mansion_indices": [3, 7, 8, 17, 18],
        "metal": "iron",
        "incense": "red myrrh",
        "color": "red",
        "hour_planet": "Mars",
        "description_cn": "在火星時辰，月亮行經第 4、8、9、18 或 19 宿，以鐵鑄刻火星圖像",
        "description_en": (
            "In the Mars hour, with Moon in mansions 4, 8, 9, 18 or 19; "
            "engrave Mars image in iron"
        ),
    },
    {
        "intent_key": "knowledge",
        "intent_cn": "知識",
        "intent_en": "Knowledge & Wisdom",
        "planet": "Mercury",
        "mansion_indices": [5, 10, 13, 19, 24],
        "metal": "quicksilver",
        "incense": "mastic",
        "color": "white",
        "hour_planet": "Mercury",
        "description_cn": "在水星時辰，月亮行經第 6、11、14、20 或 25 宿，以水銀為媒",
        "description_en": (
            "In the Mercury hour, with Moon in mansions 6, 11, 14, 20 or 25; "
            "use quicksilver as medium"
        ),
    },
    {
        "intent_key": "power",
        "intent_cn": "權力",
        "intent_en": "Power & Authority",
        "planet": "Sun",
        "mansion_indices": [4, 9, 16, 23],
        "metal": "gold",
        "incense": "saffron",
        "color": "golden",
        "hour_planet": "Sun",
        "description_cn": "在太陽時辰，月亮行經第 5、10、17 或 24 宿，以金鑄刻太陽圖像",
        "description_en": (
            "In the Sun hour, with Moon in mansions 5, 10, 17 or 24; "
            "engrave Sun image in gold"
        ),
    },
    {
        "intent_key": "agriculture",
        "intent_cn": "農業",
        "intent_en": "Agriculture & Planting",
        "planet": "Moon",
        "mansion_indices": [6, 11, 20, 23, 25],
        "metal": "silver",
        "incense": "camphor",
        "color": "white",
        "hour_planet": "Moon",
        "description_cn": "在月亮時辰，月亮行經第 7、12、21、24 或 26 宿，以銀為媒",
        "description_en": (
            "In the Moon hour, with Moon in mansions 7, 12, 21, 24 or 26; "
            "use silver as medium"
        ),
    },
]
