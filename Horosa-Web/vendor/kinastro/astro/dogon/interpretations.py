"""Interpretation helpers for Dogon Sirius Cosmology."""

from __future__ import annotations

from .calculator import DogonZoneResult, SiguiCycleInfo


# ---------------------------------------------------------------------------
# Elder phrase bank — poetic Nommo/Hogon voice
# ---------------------------------------------------------------------------

_ZONE_ELDER_ZH: dict[str, str] = {
    "nommo_corridor": (
        "以 Nommo 之名，你誕生於傳承之廊——祖靈之水在此流動，你天生攜帶部落記憶的紋路。"
        "你的使命：成為行走的祖先，讓古老之聲透過你的生命再度發聲。"
    ),
    "seed_axis": (
        "Amma 的宇宙蛋在你降生時初破其殼。你是一粒 fonio 種子，被宇宙之手播入大地。"
        "你的生命是播種，每一個選擇都在種下明日的宇宙形狀。"
    ),
    "mask_horizon": (
        "你誕生於面具之境——儀式的彼岸與此岸交界。你的命運是成為顯化者："
        "將隱藏的宇宙法則，以行動、藝術與群聚之力，顯現於人間舞台。"
    ),
}

_ZONE_ELDER_EN: dict[str, str] = {
    "nommo_corridor": (
        "In the name of Nommo, you were born within the Ancestral Corridor — "
        "the waters of spirit flow here, and you carry within you the woven memory of the tribe. "
        "Your calling: become a living ancestor, giving ancient voices new utterance through your life."
    ),
    "seed_axis": (
        "Amma's cosmic egg cracked open at your birth. You are a fonio seed "
        "planted by the hand of the universe into the earth of time. "
        "Your life is the planting; every choice seeds tomorrow's cosmic shape."
    ),
    "mask_horizon": (
        "You were born at the Mask Horizon — the threshold between ritual and reality. "
        "Your destiny is to become the Manifestor: "
        "bringing hidden cosmic law into visible form through action, art, and communal fire."
    ),
}

_PHASE_ELDER_ZH: dict[int, str] = {
    1: "你正處於種子醞釀期（Amma 之息）：根系紮入大地，未見之力正在聚集。此刻靜聽比行動更重要。",
    2: "你正在 Nommo 覺醒中：雙生性甦醒，渴望建立真實連結與社群認同。追隨你心中的水聲。",
    3: "儀式承擔期已至：你是部落傳統的守護者，走在祖先的足跡上。你的存在本身即是儀式。",
    4: "長老醞釀之際：智慧如 Po Tolo 的種子，在壓力中濃縮成光。準備傳遞，不保留。",
    5: "你進入 Sigui 回歸之境：宇宙週期閉合，長老智慧在大儀式中顯化。你是這個時代的計時者。",
}

_PHASE_ELDER_EN: dict[int, str] = {
    1: "You are in the Seed Incubation (Breath of Amma): roots push into earth, unseen forces gather. Listening matters more than acting now.",
    2: "You are in the Nommo Awakening: duality stirs, you yearn for authentic connection and communal identity. Follow the water-voice within.",
    3: "Ritual Stewardship has arrived: you are the guardian of ancestral tradition, walking in ancestral footprints. Your very existence is ceremony.",
    4: "Elder Ripening is upon you: wisdom condenses like Po Tolo under pressure — a seed of light. Prepare to transmit, holding nothing back.",
    5: "You have entered the Sigui Return: the cosmic cycle closes, elder wisdom manifests in the Great Ceremony. You are the timekeeper of this age.",
}


def build_dogon_personal_influence(
    sirius_declination: float,
    zone_result: DogonZoneResult,
    sigui: SiguiCycleInfo,
    latitude: float,
    longitude: float,
) -> tuple[str, str]:
    nearing_en = "approaching" if sigui.years_until_next <= 8 else "between"

    zone_zh = zone_result.meaning_zh
    zone_en = zone_result.meaning_en

    lat_msg_zh = (
        "高緯度地區可見性變化較大，建議重視節律而非單點判讀。"
        if abs(latitude) > 66
        else "可見性條件穩定，可結合年度觀測節點。"
    )
    lat_msg_en = (
        "At polar/high latitudes, visibility varies strongly; prioritize ritual rhythm over single-point readings."
        if abs(latitude) > 66
        else "Visibility is relatively stable; combine with yearly observation markers."
    )

    # Elder poetic voice — zone layer
    elder_zone_zh = _ZONE_ELDER_ZH.get(zone_result.zone_id or "", zone_zh)
    elder_zone_en = _ZONE_ELDER_EN.get(zone_result.zone_id or "", zone_en)

    # Life phase voice
    phase_voice_zh = _PHASE_ELDER_ZH.get(sigui.life_phase, sigui.life_phase_desc_zh)
    phase_voice_en = _PHASE_ELDER_EN.get(sigui.life_phase, sigui.life_phase_desc_en)

    influence_zh = (
        f"Hogon 的星空長老之語：\n\n"
        f"{elder_zone_zh}\n\n"
        f"你的 Sirius 赤緯為 {sirius_declination:.2f}°，落於「{zone_result.label}」：{zone_zh}。\n"
        f"目前位於 Sigui {sigui.cycle_years} 年週期的 {nearing_year_phrase(sigui, zh=True)}，"
        f"與下一次 Sigui 尚有 {sigui.years_until_next:.2f} 年。\n\n"
        f"【Sigui 生命階段 {sigui.life_phase}：{sigui.life_phase_label_zh}】\n"
        f"{phase_voice_zh}\n\n"
        f"{lat_msg_zh}\n\n"
        f"（基於人類學與天文重建；文化象徵僅供探索用途。）"
    )

    influence_en = (
        "Words from the Hogon, Elder of the Star-Sky:\n\n"
        f"{elder_zone_en}\n\n"
        f"Your Sirius declination is {sirius_declination:.2f}°, mapped to '{zone_result.label}': {zone_en}. "
        f"You are {nearing_en} the {sigui.cycle_years}-year Sigui pulse "
        f"({sigui.years_until_next:.2f} years to next Sigui).\n\n"
        f"[Sigui Life Phase {sigui.life_phase}: {sigui.life_phase_label_en}]\n"
        f"{phase_voice_en}\n\n"
        f"{lat_msg_en}\n\n"
        "(Based on anthropological and astronomical reconstruction; cultural symbolism for exploratory use only.)"
    )

    return influence_zh, influence_en


def nearing_year_phrase(sigui: SiguiCycleInfo, zh: bool = True) -> str:
    if zh:
        return f"第 {sigui.years_since_previous:.2f} 年（上一輪 {sigui.previous_year}）"
    return f"year {sigui.years_since_previous:.2f} since {sigui.previous_year}"


def build_cross_system_comparison(chart_data: dict, lang: str = "zh") -> str:
    """Generate a poetic cross-system comparison for AI analysis.

    Args:
        chart_data: dict with keys 'dogon', and optionally 'vedic', 'ziwei', 'andean'.
        lang: 'zh' or 'en'.
    Returns:
        Formatted comparison text for prompting.
    """
    is_zh = lang in ("zh", "zh_cn")
    lines = [
        ("多體系 Sirius 共鳴對話（Hogon 長老視角）" if is_zh else "Multi-System Sirius Resonance (Hogon Elder Perspective)"),
        "",
    ]

    dogon_info = chart_data.get("dogon", {})
    if dogon_info:
        sirius_dec = dogon_info.get("sirius_dec")
        years_until = dogon_info.get("years_until_sigui")
        zone = dogon_info.get("zone", "未知星域" if is_zh else "unknown zone")
        dec_str = f"{sirius_dec:.2f}°" if isinstance(sirius_dec, (int, float)) else "?"
        yrs_str = f"{years_until:.1f}" if isinstance(years_until, (int, float)) else "?"
        if is_zh:
            lines.append(f"🌟 Dogon：Sirius 赤緯 {dec_str}，{zone}，距下次 Sigui {yrs_str} 年。")
        else:
            lines.append(f"🌟 Dogon: Sirius dec {dec_str}, {zone}, {yrs_str} yr to Sigui.")

    vedic_info = chart_data.get("vedic", {})
    if vedic_info:
        if is_zh:
            lines.append(f"🕉 Vedic：Sirius 近 {vedic_info.get('nakshatra', '?')} 月宿，宇宙秩序（Ṛta）在你的命宮激活古老記憶。")
        else:
            lines.append(f"🕉 Vedic: Sirius near {vedic_info.get('nakshatra', '?')} nakshatra — Ṛta activates ancestral memory in your ascendant.")

    ziwei_info = chart_data.get("ziwei", {})
    if ziwei_info:
        if is_zh:
            lines.append(f"☯ 紫微：Sirius 與 60 年甲子週期共振，命宮 {ziwei_info.get('ming_gong', '?')} 映照多貢星性。")
        else:
            lines.append(f"☯ Ziwei: Sirius resonates with the 60-yr Jiazi cycle; Ming Gong at {ziwei_info.get('ming_gong', '?')} reflects Dogon stellar nature.")

    andean_info = chart_data.get("andean", {})
    if andean_info:
        if is_zh:
            lines.append(f"🦙 Andean：Urcuchillay 神域與 Sirius 能量對話，{andean_info.get('ceque', '?')} 聖線印證農牧週期節律。")
        else:
            lines.append(f"🦙 Andean: Urcuchillay domain dialogues with Sirius energy; {andean_info.get('ceque', '?')} ceque line affirms agropastoral cycle rhythm.")

    lines += [
        "",
        ("（基於人類學與天文重建，供跨文化探索。）" if is_zh else "(Based on anthropological and astronomical reconstruction, for cross-cultural exploration.)")
    ]
    return "\n".join(lines)
