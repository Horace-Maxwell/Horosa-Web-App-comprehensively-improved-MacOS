"""
Picatrix Invocations Module
《賢者之目標》（Ghayat al-Hakim / Picatrix）第三卷靈體召喚資料與工具
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
import json


class Planet(str, Enum):
    SATURN = "Saturn"
    JUPITER = "Jupiter"
    MARS = "Mars"
    SUN = "Sun"
    VENUS = "Venus"
    MERCURY = "Mercury"
    MOON = "Moon"


_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_json(filename: str) -> dict[str, Any]:
    with open(_DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


_SPIRITS_DATA = _load_json("picatrix_spirits.json")
_PRAYERS_DATA = _load_json("picatrix_planetary_prayers.json")

PLANET_NAME_ZH = {
    "Saturn": "土星",
    "Jupiter": "木星",
    "Mars": "火星",
    "Sun": "太陽",
    "Venus": "金星",
    "Mercury": "水星",
    "Moon": "月亮",
}

CORE_PRINCIPLES = [
    {
        "title_zh": "幾何要求",
        "title_en": "Geometric Requirement",
        "content_zh": "影像表面需平滑、平直，才能完整承接行星射線。",
        "content_en": "The image surface must be smooth and leveled to receive full planetary rays.",
    },
    {
        "title_zh": "天時要求",
        "title_en": "Timing Requirement",
        "content_zh": "需在行星強勢時刻（廟旺、面相、月相與角宮配合）施作。",
        "content_en": "Operation must occur in strong planetary timing (dignity, face, phase, and angular support).",
    },
    {
        "title_zh": "相似性原則",
        "title_en": "Principle of Similarity",
        "content_zh": "影像、金屬、顏色、香料需與行星本質相似對應。",
        "content_en": "Image, metal, color, and incense must match the essential planetary nature.",
    },
]

PRACTICAL_TALISMAN_EXAMPLES = [
    {
        "name_zh": "驅逐貓頭鷹／鴞鳥",
        "name_en": "Expel Owls",
        "timing": "木星上升面相",
        "materials": "石頭",
        "procedure": "刻圖後放置於目標位置，持續驅離。",
    },
    {
        "name_zh": "驅逐蒼蠅",
        "name_en": "Drive Away Flies",
        "timing": "上升天蠍座面相",
        "materials": "鐵板 + 三符號",
        "procedure": "刻符後放置於目標位置。",
    },
    {
        "name_zh": "吸引朋友前來",
        "name_en": "Call Friends",
        "timing": "金星 + 木星第二面相上升",
        "materials": "金屬板 + 戴勝鳥頭 + 亞麻布",
        "procedure": "書寫姓名並配合焚燒與包裹儀式。",
    },
    {
        "name_zh": "在兩人間製造敵意",
        "name_en": "Create Enmity",
        "timing": "土星日 + 上升摩羯座面相",
        "materials": "黑狗牙",
        "procedure": "刻圖後放於兩人常聚之處。",
    },
    {
        "name_zh": "對某地帶來不幸",
        "name_en": "Bring Misfortune to a Place",
        "timing": "土星日 + 上升摩羯座第二面相",
        "materials": "鉛板 + 戴勝鳥腦",
        "procedure": "刻圖後埋於目標地點。",
    },
]


PERFECT_NATURE_DATA = _SPIRITS_DATA.get("perfect_nature", {})
PERFECT_NATURE_NAMES = {
    "arabic": PERFECT_NATURE_DATA.get("arabic_names", []),
    "latin": PERFECT_NATURE_DATA.get("latin_names", []),
    "chinese": PERFECT_NATURE_DATA.get("chinese_names", []),
}
PERFECT_NATURE_TIMING = PERFECT_NATURE_DATA.get("timing", "月亮位於白羊座 1°（無論晝夜）")
PERFECT_NATURE_LONG_PRAYER = {
    "zh": "呼喚守護靈降臨，賜予智慧、辨識與正確理解，移除無知與迷霧。",
    "en": "Call the guardian spirit to descend and grant wisdom, discernment, and right understanding.",
}

PLANETARY_SPIRIT_NAMES: dict[str, list[str]] = {
    item["planet"]: item.get("spirit_names", [])
    for item in _PRAYERS_DATA.get("prayers", [])
}


@dataclass
class PlanetarySpirit:
    planet: Planet
    arabic_name: str
    latin_name: str
    chinese_name: str
    metal: str
    stones: list[str]
    colors: list[str]
    suffumigation: str
    direction: str
    invocation_text: dict[str, str]
    figures: list[dict[str, str]]
    talisman_examples: list[dict[str, str]] = field(default_factory=list)


def _planet_from_key(key: str) -> Planet:
    return Planet(key)


def _build_spirit(planet_key: str, raw: dict[str, Any]) -> PlanetarySpirit:
    planet_name = raw.get("planet", planet_key)
    chinese_name = raw.get("chinese_name")
    if not chinese_name:
        chinese_name = PLANET_NAME_ZH.get(planet_name, planet_key)

    return PlanetarySpirit(
        planet=_planet_from_key(planet_name),
        arabic_name=raw.get("arabic_name", ""),
        latin_name=raw.get("latin_name", ""),
        chinese_name=chinese_name,
        metal=raw.get("metal", ""),
        stones=raw.get("stones", []),
        colors=raw.get("colors", []),
        suffumigation=raw.get("suffumigation", ""),
        direction=raw.get("direction", ""),
        invocation_text=raw.get("invocation_text", {}),
        figures=raw.get("figures", []),
        talisman_examples=raw.get("talisman_examples", []),
    )


PICATRIX_SPIRITS: dict[Planet, PlanetarySpirit] = {
    _planet_from_key(v.get("planet", k)): _build_spirit(k, v)
    for k, v in _SPIRITS_DATA.get("spirits", {}).items()
}


def get_spirit(planet: Planet | str) -> PlanetarySpirit:
    _planet = planet if isinstance(planet, Planet) else Planet(str(planet))
    return PICATRIX_SPIRITS[_planet]


def perfect_nature_invocation() -> dict[str, Any]:
    return {
        "name": PERFECT_NATURE_DATA.get("name", "完美本性（Perfect Nature）"),
        "timing": PERFECT_NATURE_TIMING,
        "repetitions": 7,
        "step": PERFECT_NATURE_DATA.get("steps", []),
        "long_prayer": PERFECT_NATURE_LONG_PRAYER,
        "names": PERFECT_NATURE_NAMES,
        "warning": PERFECT_NATURE_DATA.get("warning", ""),
    }


def build_spirit_invocation_steps(
    planet: Planet | str,
    language: str = "zh",
) -> list[str]:
    spirit = get_spirit(planet)
    lang = "en" if language == "en" else "zh"
    invocation = spirit.invocation_text.get(lang, spirit.invocation_text.get("zh", ""))
    spirit_names = PLANETARY_SPIRIT_NAMES.get(spirit.planet.value, [])

    if lang == "en":
        steps = [
            f"Face {spirit.direction}; prepare {spirit.metal} with {', '.join(spirit.stones[:3])}.",
            f"Burn suffumigation: {spirit.suffumigation}.",
            f"Recite spirit names: {', '.join(spirit_names)}.",
            f"Recite invocation: {invocation}",
        ]
    else:
        steps = [
            f"面向{spirit.direction}，準備材質：{spirit.metal}（可配 {', '.join(spirit.stones[:3])}）。",
            f"焚香：{spirit.suffumigation}。",
            f"朗誦靈名：{', '.join(spirit_names)}。",
            f"誦念祈請文：{invocation}",
        ]
    return steps


def generate_talisman_invocation(
    planet: Planet | str,
    purpose: str = "general",
    language: str = "zh",
) -> str:
    spirit = get_spirit(planet)
    lang = "en" if language == "en" else "zh"
    invocation = spirit.invocation_text.get(lang, spirit.invocation_text.get("zh", ""))
    lines = [
        f"【{spirit.chinese_name}靈體召喚】" if lang == "zh" else f"[{spirit.planet.value} Spirit Invocation]",
        f"目的：{purpose}" if lang == "zh" else f"Purpose: {purpose}",
        f"方位：{spirit.direction}" if lang == "zh" else f"Direction: {spirit.direction}",
        f"金屬：{spirit.metal}" if lang == "zh" else f"Metal: {spirit.metal}",
        f"香料：{spirit.suffumigation}" if lang == "zh" else f"Suffumigation: {spirit.suffumigation}",
        "",
        "祈請文：" if lang == "zh" else "Invocation:",
        invocation,
    ]
    return "\n".join(lines)


def render_picatrix_invocations() -> None:
    import streamlit as st

    st.subheader("🕯️ 靈體召喚（Picatrix）")
    st.caption("資料來源：Picatrix Book III, Ch.6–7")

    st.markdown("### 核心原理（Chapter Seven）")
    for rule in CORE_PRINCIPLES:
        st.markdown(f"- **{rule['title_zh']} / {rule['title_en']}**：{rule['content_zh']}")

    pn = perfect_nature_invocation()
    st.markdown("### 完美本性（Perfect Nature）召喚")
    st.write(f"**天時：** {pn['timing']}")
    st.write(f"**四靈名（阿拉伯音）：** {'、'.join(pn['names']['arabic'])}")
    st.write(f"**拉丁音譯：** {'、'.join(pn['names']['latin'])}")
    for i, step in enumerate(pn["step"], start=1):
        st.write(f"{i}. {step}")
    st.info(pn["warning"])

    st.markdown("### 七大行星靈")
    for spirit in PICATRIX_SPIRITS.values():
        with st.expander(f"{spirit.chinese_name} / {spirit.planet.value}"):
            st.write(f"**阿拉伯名：** {spirit.arabic_name}")
            st.write(f"**拉丁音譯：** {spirit.latin_name}")
            st.write(f"**金屬：** {spirit.metal}")
            st.write(f"**石頭：** {'、'.join(spirit.stones)}")
            st.write(f"**香料：** {spirit.suffumigation}")
            st.write(f"**方位：** {spirit.direction}")
            st.write(f"**祈請文（中）：** {spirit.invocation_text.get('zh', '')}")
            st.write(f"**Invocation (EN):** {spirit.invocation_text.get('en', '')}")
            if spirit.figures:
                st.write("**影像形式：**")
                for fig in spirit.figures:
                    st.markdown(f"- {fig.get('tradition', '傳統')}: {fig.get('desc', '')}")

    st.markdown("### 實用塔利斯曼範例")
    for example in PRACTICAL_TALISMAN_EXAMPLES:
        with st.expander(f"{example['name_zh']} / {example['name_en']}"):
            st.write(f"**天時：** {example['timing']}")
            st.write(f"**材質：** {example['materials']}")
            st.write(f"**步驟：** {example['procedure']}")
