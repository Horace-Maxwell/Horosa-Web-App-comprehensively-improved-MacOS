"""Laos Horasat calculator.

此模組提供老撾占星（ໄທຣາສາດລາວ）的純計算能力：
- 出生盤（七曜 + 羅睺 / 計都）
- 老撾曆日期資訊與特殊年份分析
- ສັງຄົມ 擇日吉凶
- ສີກາດ 時段建議

雙語設計：所有回傳 dict 的關鍵欄位均有對應 ``_zh`` 中文欄位。
透過 ``data_loader`` 統一載入資料；``reload_all_data()`` 可在開發中重置快取。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from functools import lru_cache
from threading import Lock
from typing import Any, Dict, List, Literal

import swisseph as swe

from .data.calendar_rules import get_lao_date_info
from .data.data_loader import reload_all_data  # noqa: F401  (re-exported for convenience)
from .data.sangkhom_tables import SUPPORTED_SANGKHOM_ACTIVITIES, get_sangkhom_for_date
from .data.sikarat import get_best_sikarat_hours, get_sikarat_for_datetime, get_sikarat_summary
from .data.special_years import analyze_special_year

HouseSystem = Literal["whole_sign"]
AyanamsaType = Literal["LAHIRI", "RAMAN", "KRISHNAMURTI", "TRUE_CITRA", "CUSTOM"]

# 主要行星映射（依專案 Thai 模組風格，採用簡潔 key）
_LAO_GRAHA_IDS: Dict[str, int] = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mars": swe.MARS,
    "mercury": swe.MERCURY,
    "jupiter": swe.JUPITER,
    "venus": swe.VENUS,
    "saturn": swe.SATURN,
}

# 行星符號（含羅睺 / 計都）
_PLANET_SYMBOLS: Dict[str, str] = {
    "sun": "☉",
    "moon": "☾",
    "mars": "♂",
    "mercury": "☿",
    "jupiter": "♃",
    "venus": "♀",
    "saturn": "♄",
    "rahu": "☊",
    "ketu": "☋",
}

# 行星中文名稱（供 chart_to_dict _zh 欄位使用）
_PLANET_ZH: Dict[str, str] = {
    "sun": "太陽",
    "moon": "月亮",
    "mars": "火星",
    "mercury": "水星",
    "jupiter": "木星",
    "venus": "金星",
    "saturn": "土星",
    "rahu": "羅睺",
    "ketu": "計都",
}

# 老撾傳統在不同師承下會用不同 sidereal 基準，故需支援可配置 ayanamsa。
_AYANAMSA_MODE_MAP: Dict[str, int] = {
    "LAHIRI": swe.SIDM_LAHIRI,
    "RAMAN": swe.SIDM_RAMAN,
    "KRISHNAMURTI": swe.SIDM_KRISHNAMURTI,
    "CUSTOM": swe.SIDM_USER,
}
_TRUE_CITRA_SUPPORTED = hasattr(swe, "SIDM_TRUE_CITRA")
if _TRUE_CITRA_SUPPORTED:
    _AYANAMSA_MODE_MAP["TRUE_CITRA"] = swe.SIDM_TRUE_CITRA

# 自訂偏移只允許小範圍微調，避免偏離常見老撾/印度 sidereal 傳統過大。
_CUSTOM_AYANAMSA_MIN = -5.0
_CUSTOM_AYANAMSA_MAX = 5.0


@dataclass
class LaoPlanet:
    """單一星曜資料。"""

    key: str
    symbol: str
    longitude: float
    latitude: float
    speed: float
    sign_index: int
    sign_degree: float
    house: int
    retrograde: bool


@dataclass
class LaoChart:
    """老撾出生盤資料模型。"""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float
    latitude: float
    longitude: float
    location_name: str
    house_system: HouseSystem
    julian_day_ut: float
    ayanamsa: str
    ayanamsa_offset: float
    ayanamsa_value: float
    ascendant: float
    lao_date: Dict[str, Any]
    special_year: Dict[str, Any]
    sangkhom: Dict[str, Any]
    sikarat: Dict[str, Any]
    planets: List[LaoPlanet] = field(default_factory=list)


_SWE_READY = False
_SWE_INIT_LOCK = Lock()
_SWE_CALC_LOCK = Lock()


def _ensure_swe_ready() -> None:
    """Lazy singleton 初始化 Swiss Ephemeris。"""

    global _SWE_READY
    if _SWE_READY:
        return

    with _SWE_INIT_LOCK:
        if _SWE_READY:
            return

        try:
            from astro.swe_init import init_swisseph

            init_swisseph()
        except Exception:
            swe.set_ephe_path("")

        _SWE_READY = True


def get_ayanamsa_mode(ayanamsa: str) -> int:
    """回傳 ayanamsa 字串對應的 Swiss Ephemeris SIDM 常數。"""

    key = ayanamsa.strip().upper()
    if key == "TRUE_CITRA" and not _TRUE_CITRA_SUPPORTED:
        raise ValueError("目前 swisseph 版本不支援 TRUE_CITRA（SIDM_TRUE_CITRA）")
    if key in _AYANAMSA_MODE_MAP:
        return _AYANAMSA_MODE_MAP[key]
    supported = ", ".join(sorted(_AYANAMSA_MODE_MAP.keys()))
    raise ValueError(f"ayanamsa 不支援：{ayanamsa}。可用值：{supported}")


def validate_ayanamsa(ayanamsa: str, offset: float = 0.0) -> bool:
    """驗證 ayanamsa 與自訂偏移是否合法。"""

    key = ayanamsa.strip().upper()
    if key == "TRUE_CITRA" and not _TRUE_CITRA_SUPPORTED:
        return False
    if key not in _AYANAMSA_MODE_MAP:
        return False
    if key == "CUSTOM":
        return _CUSTOM_AYANAMSA_MIN <= offset <= _CUSTOM_AYANAMSA_MAX
    return True


def init_laos_ayanamsa(ayanamsa: str, offset: float = 0.0) -> tuple[str, float]:
    """初始化 Swiss Ephemeris 與 ayanamsa 設定，回傳標準化名稱與實際 offset。"""

    key = ayanamsa.strip().upper()
    if not validate_ayanamsa(key, offset):
        supported = ", ".join(sorted(_AYANAMSA_MODE_MAP.keys()))
        if key == "CUSTOM":
            raise ValueError(
                f"custom_ayanamsa_offset 必須介於 {_CUSTOM_AYANAMSA_MIN} 到 {_CUSTOM_AYANAMSA_MAX} 度"
            )
        raise ValueError(f"ayanamsa 不支援：{ayanamsa}。可用值：{supported}")

    _ensure_swe_ready()
    mode = get_ayanamsa_mode(key)
    if key == "CUSTOM":
        # t0=0 代表以 Swiss Ephemeris 既定基準 epoch（J2000.0）套用 ayan_t0 偏移。
        swe.set_sid_mode(mode, t0=0, ayan_t0=float(offset))
        return key, float(offset)

    swe.set_sid_mode(mode)
    return key, 0.0


def _norm(deg: float) -> float:
    """角度正規化到 0~360。"""

    return deg % 360.0


def _sign_index(longitude: float) -> int:
    """回傳黃道宮位索引（0~11）。"""

    return int(_norm(longitude) // 30.0)


def _sign_degree(longitude: float) -> float:
    """回傳宮內度數（0~30）。"""

    return _norm(longitude) % 30.0


def _resolve_activity(activity: str | None) -> str:
    """標準化活動名稱，避免傳入未知活動造成表格查詢失敗。"""

    if activity and activity in SUPPORTED_SANGKHOM_ACTIVITIES:
        return activity
    return SUPPORTED_SANGKHOM_ACTIVITIES[0] if SUPPORTED_SANGKHOM_ACTIVITIES else "ການແຕ່ງງານ"


def _planet_house_whole_sign(lon: float, ascendant: float) -> int:
    """Whole-sign 宮位計算。"""

    return ((_sign_index(lon) - _sign_index(ascendant)) % 12) + 1


def _validate_datetime(
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
) -> None:
    """輸入驗證，統一在入口處檢查，避免下游錯誤難以追查。"""

    try:
        datetime(year, month, day, hour, minute)
    except ValueError as exc:
        raise ValueError(f"出生日期時間不合法：{exc}") from exc

    if not -12.0 <= timezone <= 14.0:
        raise ValueError("timezone 必須介於 -12 到 +14")


@lru_cache(maxsize=1024)
def compute_lao_chart(
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone: float,
    latitude: float,
    longitude: float,
    location_name: str = "",
    house_system: HouseSystem = "whole_sign",
    sangkhom_activity: str = "ການແຕ່ງງານ",
    sikarat_type: str = "ສີກາດລາວ",
    ayanamsa: AyanamsaType = "LAHIRI",
    custom_ayanamsa_offset: float = 0.0,
) -> LaoChart:
    """計算老撾占星出生盤。

    與 Thai 模組相同：
    - 純計算函式（不依賴 Streamlit）
    - 回傳結構化 dataclass，方便 UI 與 API 重用

    Ayanamsa 設定：
    - `ayanamsa` 支援 `LAHIRI`、`RAMAN`、`KRISHNAMURTI`、`TRUE_CITRA`、`CUSTOM`
    - 預設 `LAHIRI`，與舊行為完全一致
    - 當 `ayanamsa="CUSTOM"` 時，會使用 `custom_ayanamsa_offset`（度）
      並透過 `swe.set_sid_mode(swe.SIDM_USER, t0=0, ayan_t0=offset)` 套用，
      其中 `t0=0` 代表以 J2000.0 基準 epoch 設定偏移
    - 自訂 offset 合理範圍為 -5.0 ~ +5.0 度（供傳統流派小幅校準）
    """

    _validate_datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
    )

    if house_system != "whole_sign":
        raise ValueError(f"目前僅支援 whole_sign，收到：{house_system}")

    with _SWE_CALC_LOCK:
        resolved_ayanamsa, resolved_offset = init_laos_ayanamsa(
            ayanamsa=ayanamsa,
            offset=custom_ayanamsa_offset,
        )

        # UTC 小時：與專案既有星盤計算邏輯一致
        decimal_hour_ut = hour + minute / 60.0 - timezone
        jd_ut = swe.julday(year, month, day, decimal_hour_ut)
        ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)

        # 先取 Asc（sidereal）
        _, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b"W", swe.FLG_SIDEREAL)
        ascendant = _norm(ascmc[0])

        planets: List[LaoPlanet] = []
        for key, pid in _LAO_GRAHA_IDS.items():
            result, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
            lon = _norm(result[0])
            speed = result[3]
            planets.append(
                LaoPlanet(
                    key=key,
                    symbol=_PLANET_SYMBOLS[key],
                    longitude=lon,
                    latitude=result[1],
                    speed=speed,
                    sign_index=_sign_index(lon),
                    sign_degree=_sign_degree(lon),
                    house=_planet_house_whole_sign(lon, ascendant),
                    retrograde=speed < 0,
                )
            )

        # 羅睺 / 計都
        rahu_raw, _ = swe.calc_ut(jd_ut, swe.MEAN_NODE, swe.FLG_SIDEREAL)
        rahu_lon = _norm(rahu_raw[0])
        ketu_lon = _norm(rahu_lon + 180.0)

        planets.extend(
            [
                LaoPlanet(
                    key="rahu",
                    symbol=_PLANET_SYMBOLS["rahu"],
                    longitude=rahu_lon,
                    latitude=rahu_raw[1],
                    speed=rahu_raw[3],
                    sign_index=_sign_index(rahu_lon),
                    sign_degree=_sign_degree(rahu_lon),
                    house=_planet_house_whole_sign(rahu_lon, ascendant),
                    retrograde=True,
                ),
                LaoPlanet(
                    key="ketu",
                    symbol=_PLANET_SYMBOLS["ketu"],
                    longitude=ketu_lon,
                    latitude=-rahu_raw[1],
                    speed=rahu_raw[3],
                    sign_index=_sign_index(ketu_lon),
                    sign_degree=_sign_degree(ketu_lon),
                    house=_planet_house_whole_sign(ketu_lon, ascendant),
                    retrograde=True,
                ),
            ]
        )

    local_dt = datetime(year, month, day, hour, minute)
    local_day = local_dt.date()

    lao_date = get_lao_date_info(local_day)
    special_year = analyze_special_year(year, era="gregorian")
    activity = _resolve_activity(sangkhom_activity)
    sangkhom = get_sangkhom_for_date(activity, local_day)

    # ສີກາດ：保留當下時段 + 推薦吉時列表
    sikarat = get_sikarat_for_datetime(local_dt, sikarat_type=sikarat_type)
    sikarat["best_hours"] = get_best_sikarat_hours(activity)

    return LaoChart(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        house_system=house_system,
        julian_day_ut=jd_ut,
        ayanamsa=resolved_ayanamsa,
        ayanamsa_offset=resolved_offset,
        ayanamsa_value=ayanamsa_value,
        ascendant=ascendant,
        lao_date=lao_date,
        special_year=special_year,
        sangkhom=sangkhom,
        sikarat=sikarat,
        planets=planets,
    )


def chart_to_dict(chart: LaoChart) -> Dict[str, Any]:
    """序列化 LaoChart，供 API / AI / 前端存取。

    所有關鍵欄位均包含 ``_zh`` 中文版本，方便直接渲染。
    """

    data = asdict(chart)
    data["system"] = "lao_horasat"
    data["system_name"] = "ໄທຣາສາດລາວ"
    data["system_name_zh"] = "老撾占星"

    # 為每顆星曜補充中文名稱
    for planet in data.get("planets", []):
        key = planet.get("key", "")
        planet["name_zh"] = _PLANET_ZH.get(key, key.upper())
        planet["symbol"] = _PLANET_SYMBOLS.get(key, "✶")

    return data


def get_lao_auspicious_time(
    target_dt: datetime,
    *,
    activity: str = "ການແຕ່ງງານ",
    sikarat_type: str = "ສີກາດລາວ",
) -> Dict[str, Any]:
    """查詢單一時間點的 ສັງຄົມ + ສີກາດ 建議，並給出綜合評分。

    回傳 dict 包含：
    - ``sangkhom``：星期宜忌評估（ສັງຄົມ）
    - ``sikarat``：時辰色嘎評估（ສີກາດ）
    - ``sikarat_all``：四種體系比較摘要
    - ``combined_score``：0–10 綜合吉凶分數
    - ``combined_recommendation`` / ``combined_recommendation_zh``：綜合建議
    """

    resolved = _resolve_activity(activity)
    sangkhom = get_sangkhom_for_date(resolved, target_dt.date())
    sikarat = get_sikarat_for_datetime(target_dt, sikarat_type=sikarat_type)
    sikarat["best_hours"] = get_best_sikarat_hours(resolved)
    sikarat_all = get_sikarat_summary(target_dt)

    # ---- 綜合評分（簡單規則）----
    san_status = sangkhom.get("status", "")
    sik_status = sikarat.get("status", "")

    def _score(status: str) -> float:
        if "✅ ດີຫຼາຍ" in status:
            return 10.0
        if "✅ ດີ" in status:
            return 7.5
        if "⚠️" in status:
            return 4.5
        if "❌" in status:
            return 1.5
        return 5.0

    combined_score = round((_score(san_status) + _score(sik_status)) / 2, 1)

    if combined_score >= 8.0:
        combined_rec = "✅ ດີຫຼາຍ - ເໝາະສົມທີ່ສຸດ"
        combined_rec_zh = "✅ 非常吉利，最為適合"
    elif combined_score >= 6.0:
        combined_rec = "✅ ດີ - ເໝາະສົມ"
        combined_rec_zh = "✅ 吉利，適合進行"
    elif combined_score >= 4.0:
        combined_rec = "⚠️ ປານກາງ - ຕ້ອງລະມັດລະວັງ"
        combined_rec_zh = "⚠️ 一般，需謹慎"
    else:
        combined_rec = "❌ ບໍ່ແນະນຳ - ອາດເກີດບັນຫາ"
        combined_rec_zh = "❌ 不宜，可能有阻礙"

    return {
        "activity": resolved,
        "activity_zh": _ACTIVITY_ZH_MAP.get(resolved, resolved),
        "lao_date": sangkhom.get("lao_date"),
        "sangkhom": sangkhom,
        "sikarat": sikarat,
        "sikarat_all": sikarat_all,
        "combined_score": combined_score,
        "combined_recommendation": combined_rec,
        "combined_recommendation_zh": combined_rec_zh,
    }


# 活動中文對照（calculator 內部使用）
_ACTIVITY_ZH_MAP: Dict[str, str] = {
    "ການແຕ່ງງານ": "婚禮",
    "ການສ້າງເຮືອນ": "建房／動土",
    "ການເດີນທາງ": "出行",
    "ການເປີດກິຈະການ": "開業",
    "ການບູຊາບູຊາ": "祭祀／做功德",
}


@lru_cache(maxsize=1024)
def find_best_dates(
    start_dt: datetime,
    *,
    days: int = 30,
    activity: str = "ການແຕ່ງງານ",
) -> List[Dict[str, Any]]:
    """尋找未來 N 天較吉利的日期（基於 ສັງຄົມ 表格）。"""

    if days <= 0:
        raise ValueError("days 必須大於 0")

    resolved = _resolve_activity(activity)
    result: List[Dict[str, Any]] = []

    for i in range(days):
        current_day = (start_dt + timedelta(days=i)).date()
        daily = get_sangkhom_for_date(resolved, current_day)
        status = str(daily.get("status", ""))
        if "✅" in status:
            result.append(
                {
                    "date": current_day.isoformat(),
                    "status": daily.get("status", ""),
                    "recommendation": daily.get("recommendation", ""),
                    "lao_date": daily.get("lao_date", ""),
                }
            )

    return result


@lru_cache(maxsize=1024)
def get_monthly_fortune(
    year: int,
    month: int,
    *,
    activity: str = "ການແຕ່ງງານ",
) -> List[Dict[str, Any]]:
    """回傳指定月份的每日 ສັງຄົມ 吉凶摘要。"""

    first_day = date(year, month, 1)
    next_month = date(year + (month // 12), ((month % 12) + 1), 1)
    total_days = (next_month - first_day).days
    resolved = _resolve_activity(activity)

    rows: List[Dict[str, Any]] = []
    for d in range(1, total_days + 1):
        g_date = date(year, month, d)
        daily = get_sangkhom_for_date(resolved, g_date)
        rows.append(
            {
                "day": d,
                "date": g_date.isoformat(),
                "status": daily.get("status", ""),
                "recommendation": daily.get("recommendation", ""),
            }
        )

    return rows
