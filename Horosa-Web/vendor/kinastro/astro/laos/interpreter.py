"""老撾占星傳統解讀引擎（ໄທຣາສາດລາວ）。

依照《ໂຫຣາສາດລາວ》傳統規則，提供七曜在十二宮的基礎詮釋、
逆行影響、行星星座涵義及整體盤面評讀。

所有回傳 dict 均同時提供寮國文（Lao script）與中文（``_zh``）欄位。
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List, Tuple

# ──────────────────────────────────────────────────────────
# 1. 行星雙語名稱
# ──────────────────────────────────────────────────────────
_PLANET_NAMES: Dict[str, Dict[str, str]] = {
    "sun":     {"lao": "ພຣະອາທິດ（ສຸຣິຍະ）", "zh": "太陽（ສຸຣິຍະ）"},
    "moon":    {"lao": "ພຣະຈັນ（ຈັນ）",     "zh": "月亮（ຈັນ）"},
    "mars":    {"lao": "ພຣະອັງຄານ",         "zh": "火星（ອັງຄານ）"},
    "mercury": {"lao": "ພຣະພຸດ",            "zh": "水星（ພຸດ）"},
    "jupiter": {"lao": "ພຣະພະຫັດ",          "zh": "木星（ພະຫັດ）"},
    "venus":   {"lao": "ພຣະສຸກ",            "zh": "金星（ສຸກ）"},
    "saturn":  {"lao": "ພຣະເສົາ",           "zh": "土星（ເສົາ）"},
    "rahu":    {"lao": "ຣາຫູ",              "zh": "羅睺（ຣາຫູ）"},
    "ketu":    {"lao": "ເກດຸ",              "zh": "計都（ເກດຸ）"},
}

# ──────────────────────────────────────────────────────────
# 2. 行星宮位傳統義理（書中第3–5章）
# ──────────────────────────────────────────────────────────
# 格式：(lao, zh)  — 其中 {planet_lao}/{planet_zh} 為行星名佔位符
_HOUSE_MEANINGS: Dict[str, Dict[int, Tuple[str, str]]] = {
    "sun": {
        1:  ("ພຣະອາທິດຢູ່ຮືອນ 1: ລາສີ / ບຸກຄະລິກ — ມີຄວາມເປັນຜູ້ນຳ, ແສງສີທອງ",
             "太陽在第1宮：強烈的領導力與自信，外表氣宇不凡"),
        2:  ("ພຣະອາທິດຢູ່ຮືອນ 2: ຊັບສິນ — ໂຊກດ້ານທຸລະກິດ, ຄອບຄົວໃຫ້ການຮັກສາ",
             "太陽在第2宮：財運穩固，家庭給予物質保障"),
        3:  ("ພຣະອາທິດຢູ່ຮືອນ 3: ພີ່ນ້ອງ / ການສື່ສານ — ໂຊກໃນການຮ່ວມມື",
             "太陽在第3宮：溝通能力強，兄弟緣佳"),
        4:  ("ພຣະອາທິດຢູ່ຮືອນ 4: ເຮືອນ / ຄອບຄົວ — ຕ້ອງລະມັດລະວັງກ່ຽວກັບຊັບສົມບັດ",
             "太陽在第4宮：家庭根基重要，需注意財產紛爭"),
        5:  ("ພຣະອາທິດຢູ່ຮືອນ 5: ສ້າງສັນ / ລູກ — ສ້າງສັນ, ສຸກ",
             "太陽在第5宮：創意豐沛，子女緣佳"),
        6:  ("ພຣະອາທິດຢູ່ຮືອນ 6: ສຸຂະພາບ / ສັດ — ສຸຂະພາບດີ, ຕ້ອງດູແລ",
             "太陽在第6宮：體力充沛，但需注意健康管理"),
        7:  ("ພຣະອາທິດຢູ່ຮືອນ 7: ຄູ່ຮ່ວມ / ສັນຍາ — ຄູ່ຊີວິດສ້ອງໄສ, ດີ",
             "太陽在第7宮：伴侶強勢，婚姻關係明朗"),
        8:  ("ພຣະອາທິດຢູ່ຮືອນ 8: ການລ້ຽວໃໝ່ / ມໍລະດົກ — ຕ້ອງລະມັດລະວັງ",
             "太陽在第8宮：需謹慎面對轉變與遺產問題"),
        9:  ("ພຣະອາທິດຢູ່ຮືອນ 9: ສາສະໜາ / ການໄກ — ຍ່ຽວໄກ, ໂຊກ",
             "太陽在第9宮：遠行吉利，宗教信仰帶來福德"),
        10: ("ພຣະອາທິດຢູ່ຮືອນ 10: ອາຊີບ / ກຽດ — ສ້ຳເສີມ, ສ່ອງສ້ວ່າງ",
             "太陽在第10宮：事業輝煌，地位崇高"),
        11: ("ພຣະອາທິດຢູ່ຮືອນ 11: ໝູ່ / ຄວາມຫວັງ — ມີຜູ້ຊ່ວຍ, ໄດ້ຜົນ",
             "太陽在第11宮：人際廣，夢想易實現"),
        12: ("ພຣະອາທິດຢູ່ຮືອນ 12: ຄວາມລັບ / ການສູນເສຍ — ຕ້ອງລະວັງ",
             "太陽在第12宮：隱性影響，需防損失與秘密"),
    },
    "moon": {
        1:  ("ພຣະຈັນຢູ່ຮືອນ 1: ລາສີ — ຈິດໃຈອ່ອນໄຫວ, ດຶງດູດຜູ້ຄົນ",
             "月亮在第1宮：情感豐富，天生具有親和力"),
        2:  ("ພຣະຈັນຢູ່ຮືອນ 2: ຊັບສິນ — ຂຶ້ນລົງກັນ ຊັບ, ຕ້ອງຄົ້ນຄ້ວາ",
             "月亮在第2宮：財運起伏，情緒影響財務決策"),
        3:  ("ພຣະຈັນຢູ່ຮືອນ 3: ສື່ສານ — ປາກທ່ຽງ, ຈິດໃຈໄວ",
             "月亮在第3宮：口才流暢，思維敏捷"),
        4:  ("ພຣະຈັນຢູ່ຮືອນ 4: ເຮືອນ — ຄອບຄົວ, ຄວາມສຸກ",
             "月亮在第4宮：家庭溫暖，根基穩固"),
        5:  ("ພຣະຈັນຢູ່ຮືອນ 5: ສ້າງສັນ / ລູກ — ໂຊກດ້ານລູກ, ຮັກ",
             "月亮在第5宮：子女緣深，情感創意豐富"),
        6:  ("ພຣະຈັນຢູ່ຮືອນ 6: ສຸຂະພາບ — ຕ້ອງດູແລ, ຈິດໃຈ",
             "月亮在第6宮：需注意情緒與健康連動"),
        7:  ("ພຣະຈັນຢູ່ຮືອນ 7: ຄູ່ຮ່ວມ — ຄູ່ຊີວິດດີ, ໄດ້ຮັບການດູແລ",
             "月亮在第7宮：婚姻溫柔體貼，伴侶關懷"),
        8:  ("ພຣະຈັນຢູ່ຮືອນ 8: ການລ້ຽວ — ຕ້ອງລະວັງ ຈິດໃຈ",
             "月亮在第8宮：情緒波動影響人生轉變"),
        9:  ("ພຣະຈັນຢູ່ຮືອນ 9: ສາສະໜາ — ຄວາມເຊື່ອ, ໂຊກ",
             "月亮在第9宮：虔誠帶來福運，適合修行"),
        10: ("ພຣະຈັນຢູ່ຮືອນ 10: ອາຊີບ — ມີຊື່ສຽງ, ໂຊກ",
             "月亮在第10宮：事業有名，受公眾喜愛"),
        11: ("ພຣະຈັນຢູ່ຮືອນ 11: ໝູ່ — ມິດ, ຄວາມຮ່ວມ",
             "月亮在第11宮：朋友助力大，群體受歡迎"),
        12: ("ພຣະຈັນຢູ່ຮືອນ 12: ຄວາມລັບ — ຕ້ອງລະວັງ ຈິດ",
             "月亮在第12宮：直覺強，但需防情緒隱患"),
    },
    "mars": {
        1:  ("ພຣະອັງຄານຢູ່ຮືອນ 1: ກຳລັງ / ແຂ່ງຂັນ — ກ້ຽວ, ກ້ຽວ",
             "火星在第1宮：精力充沛，個性強烈果斷"),
        4:  ("ພຣະອັງຄານຢູ່ຮືອນ 4: ເຮືອນ — ຕ້ອງລະມັດລະວັງ ອຸປະຕິເຫດ",
             "火星在第4宮：家庭易有衝突，需防意外"),
        7:  ("ພຣະອັງຄານຢູ່ຮືອນ 7: ຄູ່ — ຕ້ອງລະວັງ ຄວາມຂັດແຍ້ງ",
             "火星在第7宮：伴侶關係易有爭執，需磨合"),
        10: ("ພຣະອັງຄານຢູ່ຮືອນ 10: ອາຊີບ — ສ້ຳເສີມ, ແຂ່ງ",
             "火星在第10宮：事業競爭力強，但需防衝動"),
    },
    "jupiter": {
        1:  ("ພຣະພະຫັດຢູ່ຮືອນ 1: ລາສີ — ໂຊກດີ, ສ່ວງສວຍ",
             "木星在第1宮：天生福德，外表儒雅祥和"),
        4:  ("ພຣະພະຫັດຢູ່ຮືອນ 4: ເຮືອນ / ຄອບຄົວ — ຄອບຄົວໂຊກ",
             "木星在第4宮：家庭富足，傳統根基強"),
        9:  ("ພຣະພະຫັດຢູ່ຮືອນ 9: ສາສະໜາ — ສ້ຳເສີມ ທາງລຶ້ງ",
             "木星在第9宮：宗教智慧深厚，遠行有福"),
        10: ("ພຣະພະຫັດຢູ່ຮືອນ 10: ອາຊີບ — ຍ່ຽວ, ໂຊກ",
             "木星在第10宮：事業發展順利，得貴人提攜"),
    },
    "venus": {
        1:  ("ພຣະສຸກຢູ່ຮືອນ 1: ລາສີ — ຮ່ວງສວຍ, ດຶງດູດ",
             "金星在第1宮：外表迷人，人際關係和諧"),
        2:  ("ພຣະສຸກຢູ່ຮືອນ 2: ຊັບ — ໂຊກ ຊັບ, ຄ້າ",
             "金星在第2宮：財運佳，善理財"),
        7:  ("ພຣະສຸກຢູ່ຮືອນ 7: ຄູ່ — ຄວາມຮັກ, ໂຊກ",
             "金星在第7宮：婚姻美滿，感情順遂"),
    },
    "saturn": {
        1:  ("ພຣະເສົາຢູ່ຮືອນ 1: ລາສີ — ຕ້ອງໄດ້ທົດທານ, ຊ້າ",
             "土星在第1宮：人生考驗多，但堅忍成就大"),
        7:  ("ພຣະເສົາຢູ່ຮືອນ 7: ຄູ່ — ຄົວຊ້າ, ໄດ້ຄົນໃຫຍ່",
             "土星在第7宮：晚婚或伴侶成熟，婚姻重責任"),
        10: ("ພຣະເສົາຢູ່ຮືອນ 10: ອາຊີບ — ຮາກຖານ, ຊ້ານຊ້ານ",
             "土星在第10宮：事業穩健，需耐心積累"),
    },
    "mercury": {
        3:  ("ພຣະພຸດຢູ່ຮືອນ 3: ສື່ສານ — ຄຳ, ປາກ",
             "水星在第3宮：口才出眾，學習能力強"),
        6:  ("ພຣະພຸດຢູ່ຮືອນ 6: ສຸຂະພາບ — ສ້ຳເສີມ ວິຊາ",
             "水星在第6宮：分析能力強，適合醫療/服務業"),
        10: ("ພຣະພຸດຢູ່ຮືອນ 10: ອາຊີບ — ໂຊກ ຄຳ ການ",
             "水星在第10宮：商業溝通佳，事業多元"),
    },
    "rahu": {
        1:  ("ຣາຫູຢູ່ຮືອນ 1: ອ້ຽ, ລຸ້ນ ສ່ວນຕົວ",
             "羅睺在第1宮：人生充滿變數，個性強烈執著"),
        7:  ("ຣາຫູຢູ່ຮືອນ 7: ຄູ່ ສ່ວນ — ຕ້ອງລະວັງ",
             "羅睺在第7宮：婚姻帶來業力考驗，需磨合"),
    },
    "ketu": {
        4:  ("ເກດຸຢູ່ຮືອນ 4: ເຮືອນ — ຕ້ອງລະວັງ ຄອບຄົວ",
             "計都在第4宮：家庭帶來出離感，需守根"),
        12: ("ເກດຸຢູ່ຮືອນ 12: ຄວາມລັບ — ຢາກລ້ຶ່ງ, ທາງ",
             "計都在第12宮：前世業力深，靈性修行佳"),
    },
}

# ──────────────────────────────────────────────────────────
# 3. 星座傳統義理（書中第2章 ຣາສີ）
# ──────────────────────────────────────────────────────────
_SIGN_NAMES_LAO = [
    "ເມສ", "ພຶດສະພາ", "ມິຖຸນ", "ກະກົດ", "ສິງ", "ກັນຍາ",
    "ຕຸລາ", "ພະຈິກ", "ທະນູ", "ມັງກອນ", "ກຸມພາ", "ມີນ",
]
_SIGN_NAMES_ZH = [
    "白羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座",
    "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座",
]
_SIGN_TRAITS_ZH = [
    "勇敢開創、衝動急進",   # 白羊
    "穩定務實、享受物質",   # 金牛
    "靈活多變、溝通能力強", # 雙子
    "情感深厚、重家庭",     # 巨蟹
    "自信領導、愛受關注",   # 獅子
    "細心分析、追求完美",   # 處女
    "追求平衡、善於合作",   # 天秤
    "深沉神秘、意志堅定",   # 天蠍
    "樂觀豁達、崇尚自由",   # 射手
    "謹慎務實、目標明確",   # 摩羯
    "獨立創新、人道關懷",   # 水瓶
    "感性浪漫、靈性敏感",   # 雙魚
]

# ──────────────────────────────────────────────────────────
# 4. 行星傳統義理（書中第3章 ດາວ）
# ──────────────────────────────────────────────────────────
_PLANET_TRAD_ZH: Dict[str, str] = {
    "sun":     "代表生命力、權威與父親；宮主星尊貴，能量強",
    "moon":    "代表情感、心性與母親；盈虧影響吉凶",
    "mars":    "代表行動力、競爭與勇氣；逆行需謹慎衝動",
    "mercury": "代表學習、溝通與商業；邏輯思維之星",
    "jupiter": "代表福德、智慧與擴展；稱為「吉星之主」",
    "venus":   "代表愛情、美麗與財富；人際和諧之星",
    "saturn":  "代表責任、考驗與業力；慢而穩是其特色",
    "rahu":    "代表突變、執著與外界誘惑；影射業力入世",
    "ketu":    "代表出離、直覺與前世業；靈性解脫之象",
}

# ──────────────────────────────────────────────────────────
# 5. 逆行傳統說明
# ──────────────────────────────────────────────────────────
_RETROGRADE_NOTE_ZH: Dict[str, str] = {
    "mercury": "水星逆行：溝通與契約易出差錯，需反思計畫",
    "venus":   "金星逆行：感情易有波折，重新審視關係",
    "mars":    "火星逆行：行動力內化，宜靜不宜動",
    "jupiter": "木星逆行：福德轉向內在，適合修行反省",
    "saturn":  "土星逆行：業力加重，需面對過去未完之事",
    "rahu":    "羅睺恆逆行：業力執著為常態",
    "ketu":    "計都恆逆行：出離業力為常態",
}


# ──────────────────────────────────────────────────────────
# 6. 核心解讀函數
# ──────────────────────────────────────────────────────────

def interpret_planet(
    planet_key: str,
    house: int,
    sign_index: int,
    retrograde: bool,
    longitude: float,
) -> Dict[str, Any]:
    """解讀單一行星的傳統涵義（雙語）。

    Args:
        planet_key:  行星鍵值（``"sun"``、``"moon"`` 等）。
        house:       所在宮位（1–12）。
        sign_index:  所在星座索引（0–11）。
        retrograde:  是否逆行。
        longitude:   黃道經度（0–360°）。

    Returns:
        包含 ``house_note``、``sign_note``、``planet_note``、
        ``retrograde_note``（若逆行）及對應 ``_zh`` 欄位的 dict。
    """
    key = planet_key.lower()
    names = _PLANET_NAMES.get(key, {"lao": key.upper(), "zh": key.upper()})
    sign_lao = _SIGN_NAMES_LAO[sign_index] if 0 <= sign_index < 12 else "—"
    sign_zh = _SIGN_NAMES_ZH[sign_index] if 0 <= sign_index < 12 else "—"
    sign_trait_zh = _SIGN_TRAITS_ZH[sign_index] if 0 <= sign_index < 12 else ""

    # 宮位義理
    house_meanings = _HOUSE_MEANINGS.get(key, {})
    house_note_lao, house_note_zh = house_meanings.get(
        house,
        (
            f"{names['lao']}ຢູ່ຮືອນ {house}",
            f"{names['zh']}在第 {house} 宮",
        ),
    )

    result: Dict[str, Any] = {
        "planet_key": key,
        "planet_lao": names["lao"],
        "planet_zh": names["zh"],
        "house": house,
        "sign_lao": sign_lao,
        "sign_zh": sign_zh,
        "sign_trait_zh": sign_trait_zh,
        "longitude": round(longitude, 2),
        "retrograde": retrograde,
        "house_note_lao": house_note_lao,
        "house_note_zh": house_note_zh,
        "planet_note_zh": _PLANET_TRAD_ZH.get(key, ""),
    }

    if retrograde and key in _RETROGRADE_NOTE_ZH:
        result["retrograde_note_zh"] = _RETROGRADE_NOTE_ZH[key]

    return result


def interpret_chart(chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """對整個出生盤進行傳統解讀，回傳雙語詮釋 dict。

    Args:
        chart_data: ``compute_lao_chart()`` 或 ``chart_to_dict()`` 的回傳值。

    Returns:
        包含逐行星解讀（``planet_readings``）、整體摘要（``summary``）
        與吉凶星數量統計（``auspicious_count``）的 dict。
    """
    planets = chart_data.get("planets", [])
    ascendant = float(chart_data.get("ascendant", 0.0))
    special_year = chart_data.get("special_year", {})
    sangkhom = chart_data.get("sangkhom", {})

    planet_readings: List[Dict[str, Any]] = []
    auspicious_keys = {"sun", "moon", "jupiter", "venus"}
    auspicious_count = 0

    for p in planets:
        key = str(p.get("key", "")).lower()
        house = int(p.get("house", 0))
        sign_index = int(p.get("sign_index", 0))
        retrograde = bool(p.get("retrograde"))
        longitude = float(p.get("longitude", 0.0))

        reading = interpret_planet(key, house, sign_index, retrograde, longitude)
        planet_readings.append(reading)

        if key in auspicious_keys and not retrograde:
            auspicious_count += 1

    # 整體摘要
    asc_sign_idx = int(ascendant // 30) % 12
    asc_sign_lao = _SIGN_NAMES_LAO[asc_sign_idx]
    asc_sign_zh = _SIGN_NAMES_ZH[asc_sign_idx]
    asc_trait_zh = _SIGN_TRAITS_ZH[asc_sign_idx]

    special_note_zh = (
        f"⚠️ 特殊年份（{special_year.get('description_zh', '')}），"
        "建議加強 ສີກາດ 與 ສັງຄົມ 擇日"
        if special_year.get("is_special")
        else "✅ 普通年份，整體穩定"
    )

    sangkhom_rec = sangkhom.get("recommendation_zh", "")

    summary_zh = (
        f"命主上升星座為【{asc_sign_zh}】，特質：{asc_trait_zh}。"
        f"盤中吉星共 {auspicious_count} 顆直行，能量積極。"
        f"{special_note_zh}。"
        f"擇日建議：{sangkhom_rec}"
    )

    return {
        "ascendant_sign_lao": asc_sign_lao,
        "ascendant_sign_zh": asc_sign_zh,
        "ascendant_sign_trait_zh": asc_trait_zh,
        "planet_readings": planet_readings,
        "auspicious_count": auspicious_count,
        "special_year_note_zh": special_note_zh,
        "sangkhom_summary_zh": sangkhom_rec,
        "summary_zh": summary_zh,
    }


def get_planet_sign_reading(planet_key: str, sign_index: int) -> Dict[str, str]:
    """快速取得行星在某星座的雙語說明（供 UI tooltip 使用）。

    Args:
        planet_key: 行星鍵值。
        sign_index: 0–11。

    Returns:
        ``{"sign_lao": ..., "sign_zh": ..., "trait_zh": ..., "planet_zh": ...}``
    """
    sign_lao = _SIGN_NAMES_LAO[sign_index] if 0 <= sign_index < 12 else "—"
    sign_zh = _SIGN_NAMES_ZH[sign_index] if 0 <= sign_index < 12 else "—"
    trait_zh = _SIGN_TRAITS_ZH[sign_index] if 0 <= sign_index < 12 else ""
    planet_zh = _PLANET_NAMES.get(planet_key, {}).get("zh", planet_key.upper())
    planet_trad = _PLANET_TRAD_ZH.get(planet_key.lower(), "")

    return {
        "sign_lao": sign_lao,
        "sign_zh": sign_zh,
        "trait_zh": trait_zh,
        "planet_zh": planet_zh,
        "planet_traditional_zh": planet_trad,
    }


# ──────────────────────────────────────────────────────────
# 公開介面
# ──────────────────────────────────────────────────────────
__all__ = [
    "interpret_chart",
    "interpret_planet",
    "get_planet_sign_reading",
]
