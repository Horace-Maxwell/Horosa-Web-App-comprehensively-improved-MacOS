"""
巴厘傳統 Wariga 計算模組 (Balinese Wariga Calendar Calculator)

使用傳統 Wuku (210天週期) + Wewaran (Eka~Dasa Wara) 的 Neptu/Urip 數值系統
進行巴厘傳統曆法計算。核心算法完全依照古典 Lontar Wariga / Dasar Wariga 規則，
不使用現代天文簡化公式或近似值。

Wewaran 計算階層規則：Wewaran alah dening Wuku
→ 總 Neptu 相加後再對各 Wara 週期取模

pyswisseph 僅用於：
- Gregorian → Julian Day 轉換
- 太陽/月亮黃經（用於 Sasih 月份近似驗證和季節參考）
- Orion (Waluku) 升落參考（用於季節校驗）

古法依據：Lontar Wariga / Dasar Wariga
"""

import math
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional

import streamlit as _st
import swisseph as swe

from .constants import (
    EPOCH_YEAR, EPOCH_MONTH, EPOCH_DAY,
    WUKU_TABLE,
    EKA_WARA, DWI_WARA, TRI_WARA, CATUR_WARA,
    PANCA_WARA, SAD_WARA, SAPTA_WARA,
    ASTA_WARA, SANGA_WARA, DASA_WARA,
    INGKEL, WATEK_ALIT, WATEK_MADYA, PAWATEKAN,
    LINTANG,
    SASIH_NAMES,
    SEASON_LAHRU_RANGE, SEASON_RENGRENG_RANGE,
    PANCASUDA,
    PAWUKON_CYCLE,
    PANCA_DAUH, ASTA_DAUH,
    PENANGGAL_NAMES, PANGLONG_NAMES,
    WUKU_ATTRIBUTES, ALA_AYUNING_DEWASA,
    WUKU_DETAILS, ACTIVITY_RULES,
    GOOD_WEWARAN_COMBOS,
    UTTAMA_WUKU, ALA_WUKU,
    OTONAN_RITUALS,
)


# ============================================================
# 資料類定義 (Data Classes)
# ============================================================

@dataclass
class DauhInfo:
    """時辰（Dauh）資訊"""
    dauh_type: str       # 時辰系統名稱 (Panca Dauh / Asta Dauh)
    name: str            # 時辰名稱
    deity: str           # 主宰神明
    direction: str       # 方位
    quality: str         # 吉凶


@dataclass
class PenanggalInfo:
    """月相日（Penanggal/Panglong）資訊"""
    is_penanggal: bool   # True=月盈期(Penanggal), False=月虧期(Panglong)
    day_number: int      # 月相日數 (1-15)
    name: str            # 傳統名稱
    neptu: int           # Neptu/Urip 值
    moon_phase_deg: float  # 月相角度 (0-360)
    special: str = ""    # 特殊聖日標記 (Purnama / Tilem / 空白)


@dataclass
class WaraInfo:
    """單一 Wara（星期類別）的資訊"""
    wara_type: str       # Wara 類型名稱 (如 "Sapta Wara")
    name: str            # 該日的 Wara 名稱 (如 "Redite")
    neptu: int           # 該 Wara 的 Neptu/Urip 值


@dataclass
class WukuInfo:
    """Wuku（週）的資訊"""
    index: int           # Wuku 索引 (0-29)
    name: str            # Wuku 名稱
    neptu: int           # Wuku 的 Neptu 值


@dataclass
class DewasaInfo:
    """吉凶判斷資訊"""
    is_auspicious: bool              # 總體是否為吉日
    auspicious_labels: list          # 吉日標籤列表
    inauspicious_labels: list        # 凶日標籤列表
    neptu_sum: int                   # Panca Wara + Sapta Wara Neptu 總和
    pancasuda: str                   # Pancasuda 名稱
    pancasuda_meaning: str           # Pancasuda 含義
    notes: list = field(default_factory=list)  # 額外說明


@dataclass
class SasihInfo:
    """Sasih（月）與季節資訊"""
    sasih_index: int     # Sasih 索引 (0-11)
    sasih_name: str      # Sasih 名稱
    season: str          # 季節名稱 (Lahru / Rengreng)
    season_cn: str       # 季節中文 (乾季 / 雨季)
    ayana: str           # Uttarayana / Dakshinayana


@dataclass
class AlaAyuningDetail:
    """
    增強版 Ala Ayuning Dewasa — 5 因素分析結果
    依 Lontar Wariga Dewasa 古典五因素規則計算

    五因素：Wuku + Wewaran + Sasih + Penanggal/Panglong + Dawuh
    """
    level: str                        # "Uttama" / "Madya" / "Ala"
    level_cn: str                     # "上吉" / "中吉" / "凶" / "大凶"
    color: str                        # 顏色代碼（綠/黃/紅）
    uttama_factors: List[str]         # 大吉因素列表
    madya_factors: List[str]          # 中性/小吉因素列表
    ala_factors: List[str]            # 凶因素列表
    explanation: str                  # 中文說明（因...→...）
    factor_summary: List[str]         # 完整因素清單（帶符號）
    special_holy_day: str = ""        # 特殊聖日名稱（如 Galungan）
    activity_advice: dict = field(default_factory=dict)  # 各活動的建議


@dataclass
class OtonanResult:
    """
    Otonan（210天命主生日）計算結果
    古法依據：Lontar Tattwa Krama — Otonan 章節
    """
    birth_wuku: str               # 出生 Wuku 名稱
    birth_wuku_index: int         # 出生 Wuku 索引 (0-29)
    birth_day_in_pawukon: int     # 出生日在 Pawukon 中的位置 (0-209)
    birth_panca_wara: str         # 出生 Panca Wara
    birth_sapta_wara: str         # 出生 Sapta Wara
    next_otonan_dates: List[date] # 接下來 3 個 Otonan 日期
    wuku_profile: dict            # Wuku 性格檔案
    ritual_note: str              # 推薦 Otonan 儀式說明


@dataclass
class CompatibilityResult:
    """
    Wuku 緣分配對結果
    古法依據：Lontar Wariga — Pawatekan 相合章節
    """
    wuku1: str          # 甲方 Wuku
    wuku2: str          # 乙方 Wuku
    panca1: str         # 甲方 Panca Wara
    panca2: str         # 乙方 Panca Wara
    sapta1: str         # 甲方 Sapta Wara
    sapta2: str         # 乙方 Sapta Wara
    ingkel1: str        # 甲方 Ingkel
    ingkel2: str        # 乙方 Ingkel
    score: int          # 緣分分數 (0-100)
    level: str          # 緣分等級（中文）
    level_en: str       # 緣分等級（英文）
    description: str    # 緣分說明
    suggestions: str    # 建議事項


@dataclass
class WarigaResult:
    """Wariga 計算完整結果"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    latitude: float
    longitude: float
    # Pawukon 資訊
    day_in_pawukon: int         # 在 210 天週期中的第幾天 (0-209)
    wuku: WukuInfo              # Wuku 資訊
    # 所有 Wara
    eka_wara: WaraInfo
    dwi_wara: WaraInfo
    tri_wara: WaraInfo
    catur_wara: WaraInfo
    panca_wara: WaraInfo
    sad_wara: WaraInfo
    sapta_wara: WaraInfo
    asta_wara: WaraInfo
    sanga_wara: WaraInfo
    dasa_wara: WaraInfo
    # 分類
    ingkel: str                 # Ingkel 動物分類
    watek_alit: str             # Watek Alit 分類
    watek_madya: str            # Watek Madya 分類
    lintang: str                # Lintang 星宿
    # 吉凶
    dewasa: DewasaInfo          # 吉凶判斷
    # 增強版 Ala Ayuning（5因素）
    ala_ayuning_detail: Optional[AlaAyuningDetail]  # 增強版吉凶分析
    # 月份與季節
    sasih: SasihInfo            # Sasih 月份與季節
    # 時辰資訊（Panca Dauh / Asta Dauh）
    panca_dauh: DauhInfo        # Panca Dauh 時辰
    asta_dauh: DauhInfo         # Asta Dauh 時辰
    # 月相日（Penanggal / Panglong）
    penanggal: PenanggalInfo    # 月相日資訊
    # 天文參考（使用 pyswisseph 計算，僅供參考）
    sun_longitude: float        # 太陽黃經
    moon_longitude: float       # 月亮黃經
    julian_day: float           # 儒略日


# ============================================================
# 核心計算類 (Core Calculator)
# ============================================================

class WarigaCalculator:
    """
    巴厘傳統 Wariga 計算器

    根據傳統 Lontar Wariga / Dasar Wariga 的古法規則，
    從格里高利日期計算完整的 Wariga 資訊。

    核心算法：
    1. 計算目標日期與基準日 (epoch) 的天數差
    2. 天數差 mod 210 → 得到 Pawukon 日序
    3. Pawukon 日序 → Wuku 名稱 (日序 // 7)
    4. Pawukon 日序 → 各 Wara (各自的取模規則)
    5. Neptu 累加 → 吉凶判斷

    古法依據：Lontar Wariga / Dasar Wariga
    """

    def __init__(self, year, month, day, hour=0, minute=0, lat=None, lon=None):
        """
        初始化 Wariga 計算器

        參數：
            year   (int): 格里高利年份
            month  (int): 月份 (1-12)
            day    (int): 日 (1-31)
            hour   (int): 時 (0-23)，預設為 0
            minute (int): 分 (0-59)，預設為 0
            lat  (float): 緯度（可選，用於天文參考計算）
            lon  (float): 經度（可選，用於天文參考計算）
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        # 巴厘島預設座標 (Ubud, Bali)
        self.lat = lat if lat is not None else -8.5069
        self.lon = lon if lon is not None else 115.2625

    # --------------------------------------------------------
    # 公開介面
    # --------------------------------------------------------

    def compute(self) -> dict:
        """
        執行完整的 Wariga 計算，回傳完整資訊字典

        回傳：
            dict: 包含所有 Wariga 資訊的字典，
                  等同於 WarigaResult 的所有欄位
        """
        result = self._compute_all()
        return self._result_to_dict(result)

    def compute_result(self) -> WarigaResult:
        """
        執行完整的 Wariga 計算，回傳 WarigaResult 資料類

        回傳：
            WarigaResult: 完整 Wariga 計算結果
        """
        return self._compute_all()

    # --------------------------------------------------------
    # 內部計算方法
    # --------------------------------------------------------

    def _compute_all(self) -> WarigaResult:
        """執行所有計算，回傳 WarigaResult"""
        # 1) 計算 Julian Day 與天文參考數據
        jd, sun_lon, moon_lon = self._compute_astro_reference()

        # 2) 計算 Pawukon 日序 (0-209)
        day_in_pawukon = self._compute_pawukon_day()

        # 3) 計算 Wuku
        wuku = self._compute_wuku(day_in_pawukon)

        # 4) 計算所有 Wara
        eka = self._compute_eka_wara(day_in_pawukon)
        dwi = self._compute_dwi_wara(day_in_pawukon)
        tri = self._compute_tri_wara(day_in_pawukon)
        catur = self._compute_catur_wara(day_in_pawukon)
        panca = self._compute_panca_wara(day_in_pawukon)
        sad = self._compute_sad_wara(day_in_pawukon)
        sapta = self._compute_sapta_wara(day_in_pawukon)
        asta = self._compute_asta_wara(day_in_pawukon)
        sanga = self._compute_sanga_wara(day_in_pawukon)
        dasa = self._compute_dasa_wara(panca, sapta)

        # 5) 計算分類
        ingkel = self._compute_ingkel(wuku.index)
        watek_alit, watek_madya = self._compute_watek(wuku.index)
        lintang = self._compute_lintang(day_in_pawukon)

        # 6) 計算吉凶 (Dewasa)
        dewasa = self._compute_dewasa(
            panca, sapta, tri, wuku, day_in_pawukon
        )

        # 7) 計算 Sasih 與季節
        sasih = self._compute_sasih(sun_lon, moon_lon)

        # 8) 計算時辰 (Panca Dauh / Asta Dauh)
        panca_dauh = self._compute_panca_dauh(self.hour)
        asta_dauh = self._compute_asta_dauh(self.hour)

        # 9) 計算月相日 (Penanggal / Panglong)
        penanggal = self._compute_penanggal(sun_lon, moon_lon)

        # 10) 計算增強版 Ala Ayuning（5 因素）
        # 建立臨時結果以傳遞給增強計算方法
        partial = WarigaResult(
            year=self.year, month=self.month, day=self.day,
            hour=self.hour, minute=self.minute,
            latitude=self.lat, longitude=self.lon,
            day_in_pawukon=day_in_pawukon,
            wuku=wuku,
            eka_wara=eka, dwi_wara=dwi, tri_wara=tri,
            catur_wara=catur, panca_wara=panca, sad_wara=sad,
            sapta_wara=sapta, asta_wara=asta, sanga_wara=sanga,
            dasa_wara=dasa,
            ingkel=ingkel, watek_alit=watek_alit,
            watek_madya=watek_madya, lintang=lintang,
            dewasa=dewasa, ala_ayuning_detail=None,
            sasih=sasih, panca_dauh=panca_dauh, asta_dauh=asta_dauh,
            penanggal=penanggal,
            sun_longitude=sun_lon, moon_longitude=moon_lon, julian_day=jd,
        )
        ala_ayuning_detail = self._compute_ala_ayuning_detail(partial)

        return WarigaResult(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            latitude=self.lat,
            longitude=self.lon,
            day_in_pawukon=day_in_pawukon,
            wuku=wuku,
            eka_wara=eka,
            dwi_wara=dwi,
            tri_wara=tri,
            catur_wara=catur,
            panca_wara=panca,
            sad_wara=sad,
            sapta_wara=sapta,
            asta_wara=asta,
            sanga_wara=sanga,
            dasa_wara=dasa,
            ingkel=ingkel,
            watek_alit=watek_alit,
            watek_madya=watek_madya,
            lintang=lintang,
            dewasa=dewasa,
            ala_ayuning_detail=ala_ayuning_detail,
            sasih=sasih,
            panca_dauh=panca_dauh,
            asta_dauh=asta_dauh,
            penanggal=penanggal,
            sun_longitude=sun_lon,
            moon_longitude=moon_lon,
            julian_day=jd,
        )

    def _compute_astro_reference(self):
        """
        使用 pyswisseph 計算天文參考數據

        回傳：
            tuple: (julian_day, sun_longitude, moon_longitude)
        """
        # 計算儒略日（使用 UTC 近似，巴厘時區 WITA = UTC+8）
        decimal_hour = self.hour + self.minute / 60.0 - 8.0
        jd = swe.julday(self.year, self.month, self.day, decimal_hour)

        # 太陽黃經、月亮黃經
        sun_lon = self._extract_longitude(jd, swe.SUN)
        moon_lon = self._extract_longitude(jd, swe.MOON)

        return jd, sun_lon, moon_lon

    @staticmethod
    def _extract_longitude(jd: float, planet_id: int) -> float:
        """
        從 pyswisseph 計算結果中提取天體黃經

        參數：
            jd        (float): 儒略日
            planet_id (int):   pyswisseph 天體 ID

        回傳：
            float: 黃經度數 (0-360)
        """
        result = swe.calc_ut(jd, planet_id)
        return result[0][0] if isinstance(result[0], (list, tuple)) else result[0]

    def _compute_pawukon_day(self) -> int:
        """
        計算目標日期在 Pawukon 210 天週期中的位置

        算法：
        1. 計算目標日期與基準日 (epoch: 1969-12-31) 的天數差
        2. 天數差 mod 210 = Pawukon 日序 (0-209)

        古法依據：Lontar Wariga — Pawukon 日序計算法

        回傳：
            int: Pawukon 日序 (0-209)
        """
        target = date(self.year, self.month, self.day)
        epoch = date(EPOCH_YEAR, EPOCH_MONTH, EPOCH_DAY)
        delta_days = (target - epoch).days
        return delta_days % PAWUKON_CYCLE

    def _compute_wuku(self, day_in_pawukon: int) -> WukuInfo:
        """
        計算 Wuku（週）名稱與 Neptu

        算法：Wuku 索引 = Pawukon 日序 // 7

        古法依據：Lontar Wariga — 30 Wuku 表

        回傳：
            WukuInfo: 包含 Wuku 索引、名稱、Neptu
        """
        wuku_idx = day_in_pawukon // 7
        name, neptu = WUKU_TABLE[wuku_idx]
        return WukuInfo(index=wuku_idx, name=name, neptu=neptu)

    def _compute_eka_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Eka Wara (1天週期)

        古法規則：Eka Wara 由 Panca Wara Urip + Sapta Wara Urip 總和的奇偶決定
        但傳統上 Eka Wara 只有 "Luang" 一值，所有日皆為 Luang。

        古法依據：Lontar Wariga — Eka Wara

        回傳：
            WaraInfo: Eka Wara 資訊
        """
        name, neptu = EKA_WARA[0]
        return WaraInfo(wara_type="Eka Wara", name=name, neptu=neptu)

    def _compute_dwi_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Dwi Wara (2天週期)

        古法規則：由 Panca Wara Urip + Sapta Wara Urip 總和奇偶決定
        偶數 → Menga(0)，奇數 → Pepet(5)

        古法依據：Lontar Wariga — Dwi Wara

        回傳：
            WaraInfo: Dwi Wara 資訊
        """
        # 先取得 Panca Wara 和 Sapta Wara 的 Urip
        panca_idx = day_in_pawukon % 5
        sapta_idx = day_in_pawukon % 7
        panca_neptu = PANCA_WARA[panca_idx][1]
        sapta_neptu = SAPTA_WARA[sapta_idx][1]
        total = panca_neptu + sapta_neptu
        # 偶數 → Menga，奇數 → Pepet
        dwi_idx = total % 2
        name, neptu = DWI_WARA[dwi_idx]
        return WaraInfo(wara_type="Dwi Wara", name=name, neptu=neptu)

    def _compute_tri_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Tri Wara (3天週期)

        算法：day_in_pawukon mod 3

        古法依據：Lontar Wariga — Tri Wara

        回傳：
            WaraInfo: Tri Wara 資訊
        """
        idx = day_in_pawukon % 3
        name, neptu = TRI_WARA[idx]
        return WaraInfo(wara_type="Tri Wara", name=name, neptu=neptu)

    def _compute_catur_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Catur Wara (4天週期)

        古法規則：非簡單 day % 4。
        在 Pawukon 週期中，Catur Wara 在特定日（第71、72天）
        會使用 Jaya 和 Menala 的特殊重複規則。

        修正算法：
        - 如果 day_in_pawukon < 71: idx = day_in_pawukon % 4
        - 如果 day_in_pawukon == 71 或 72: 使用固定值
        - 如果 day_in_pawukon > 72: idx = (day_in_pawukon - 2) % 4

        古法依據：Lontar Wariga — Catur Wara 排序法

        回傳：
            WaraInfo: Catur Wara 資訊
        """
        if day_in_pawukon < 71:
            idx = day_in_pawukon % 4
        elif day_in_pawukon == 71:
            idx = 2  # Jaya（重複）
        elif day_in_pawukon == 72:
            idx = 3  # Menala（重複）
        else:
            idx = (day_in_pawukon - 2) % 4
        name, neptu = CATUR_WARA[idx]
        return WaraInfo(wara_type="Catur Wara", name=name, neptu=neptu)

    def _compute_panca_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Panca Wara (5天週期)

        算法：day_in_pawukon mod 5

        古法依據：Lontar Wariga — Panca Wara

        回傳：
            WaraInfo: Panca Wara 資訊
        """
        idx = day_in_pawukon % 5
        name, neptu = PANCA_WARA[idx]
        return WaraInfo(wara_type="Panca Wara", name=name, neptu=neptu)

    def _compute_sad_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Sad Wara (6天週期)

        算法：day_in_pawukon mod 6

        古法依據：Lontar Wariga — Sad Wara

        回傳：
            WaraInfo: Sad Wara 資訊
        """
        idx = day_in_pawukon % 6
        name, neptu = SAD_WARA[idx]
        return WaraInfo(wara_type="Sad Wara", name=name, neptu=neptu)

    def _compute_sapta_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Sapta Wara (7天週期) — 星期

        算法：day_in_pawukon mod 7

        古法依據：Lontar Wariga — Sapta Wara

        回傳：
            WaraInfo: Sapta Wara 資訊
        """
        idx = day_in_pawukon % 7
        name, neptu = SAPTA_WARA[idx]
        return WaraInfo(wara_type="Sapta Wara", name=name, neptu=neptu)

    def _compute_asta_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Asta Wara (8天週期)

        古法規則：非簡單 day % 8。
        Asta Wara 在 Pawukon 週期中有特殊跳過規則：
        - 如果 day_in_pawukon < 71: idx = day_in_pawukon % 8
        - 如果 day_in_pawukon == 71 或 72: 使用固定值 (Kala, Uma)
        - 如果 day_in_pawukon > 72: idx = (day_in_pawukon - 2) % 8

        古法依據：Lontar Wariga — Asta Wara 排序法

        回傳：
            WaraInfo: Asta Wara 資訊
        """
        if day_in_pawukon < 71:
            idx = day_in_pawukon % 8
        elif day_in_pawukon == 71:
            idx = 6  # Kala
        elif day_in_pawukon == 72:
            idx = 7  # Uma
        else:
            idx = (day_in_pawukon - 2) % 8
        name, neptu = ASTA_WARA[idx]
        return WaraInfo(wara_type="Asta Wara", name=name, neptu=neptu)

    def _compute_sanga_wara(self, day_in_pawukon: int) -> WaraInfo:
        """
        計算 Sanga Wara (9天週期)

        古法規則：非簡單 day % 9。
        Sanga Wara 在 Pawukon 週期中有跳過規則：
        - 如果 day_in_pawukon < 4: idx = Dangu (索引0)
        - 否則: idx = (day_in_pawukon - 3) % 9
        （前4天 [索引0-3] 固定為 Dangu，從第5天 [索引4] 開始正常循環）

        古法依據：Lontar Wariga — Sanga Wara 排序法

        回傳：
            WaraInfo: Sanga Wara 資訊
        """
        if day_in_pawukon < 4:
            idx = 0  # Dangu（前四天固定）
        else:
            idx = (day_in_pawukon - 3) % 9
        name, neptu = SANGA_WARA[idx]
        return WaraInfo(wara_type="Sanga Wara", name=name, neptu=neptu)

    def _compute_dasa_wara(self, panca: WaraInfo, sapta: WaraInfo) -> WaraInfo:
        """
        計算 Dasa Wara (10天週期)

        古法規則：Dasa Wara 索引 = (Panca Wara Urip + Sapta Wara Urip) mod 10
        這是 Wewaran 階層規則「Wewaran alah dening Wuku」的體現。

        古法依據：Lontar Wariga — Dasa Wara 表

        回傳：
            WaraInfo: Dasa Wara 資訊
        """
        total = panca.neptu + sapta.neptu
        idx = total % 10
        name, neptu = DASA_WARA[idx]
        return WaraInfo(wara_type="Dasa Wara", name=name, neptu=neptu)

    def _compute_ingkel(self, wuku_index: int) -> str:
        """
        計算 Ingkel 動物分類

        算法：Wuku 索引 // 6 → Ingkel 索引 (0-4)

        古法依據：Lontar Wariga — Ingkel 分類

        回傳：
            str: Ingkel 名稱
        """
        return INGKEL[wuku_index // 6]

    def _compute_watek(self, wuku_index: int):
        """
        計算 Watek Alit 與 Watek Madya

        算法：查 PAWATEKAN 表，取對應的索引

        古法依據：Lontar Wariga — Pawatekan 對照表

        回傳：
            tuple: (Watek Alit 名稱, Watek Madya 名稱)
        """
        alit_idx, madya_idx = PAWATEKAN[wuku_index]
        return WATEK_ALIT[alit_idx], WATEK_MADYA[madya_idx]

    def _compute_lintang(self, day_in_pawukon: int) -> str:
        """
        計算 Lintang 星宿

        算法：day_in_pawukon mod 35 → Lintang 索引

        古法依據：Lontar Wariga — Lintang 表

        回傳：
            str: Lintang 名稱
        """
        idx = day_in_pawukon % 35
        return LINTANG[idx]

    def _compute_dewasa(self, panca, sapta, tri, wuku, day_in_pawukon):
        """
        計算 Ala Ayuning Dewasa（吉凶日判斷）

        核心規則：
        1. Neptu 總和 = Panca Wara Urip + Sapta Wara Urip
        2. Neptu 總和 ≤ 9 → 初步判為吉
        3. 檢查特定凶日組合（Kajeng Kliwon, Anggara Kasih 等）
        4. 計算 Pancasuda = Neptu 總和 mod 7

        古法依據：Lontar Wariga — Dewasa Ayu / Ala 章節 / Dasar Wariga

        回傳：
            DewasaInfo: 吉凶判斷結果
        """
        neptu_sum = panca.neptu + sapta.neptu
        auspicious_labels = []
        inauspicious_labels = []
        notes = []

        # (1) Pancasuda 計算
        pancasuda_idx = neptu_sum % 7
        ps_name, ps_meaning = PANCASUDA[pancasuda_idx]

        # (2) 基本吉凶判斷：Neptu ≤ 9 初步為吉
        if neptu_sum <= 9:
            auspicious_labels.append("Dewasa Ayu（Neptu 總和 ≤ 9）")

        # (3) 特殊吉日檢查
        # Beteng（平衡日）= Tri Wara Beteng
        if tri.name == "Beteng":
            auspicious_labels.append("Beteng（均衡日）")

        # (4) 特殊凶日檢查
        # Kajeng Kliwon = Tri Wara Kajeng + Panca Wara Kliwon
        if tri.name == "Kajeng" and panca.name == "Kliwon":
            inauspicious_labels.append("Kajeng Kliwon（大忌日）")
            notes.append("Kajeng Kliwon 為傳統大忌日，忌一切重要活動")

        # Anggara Kasih = Sapta Wara Anggara + Panca Wara Kliwon
        if sapta.name == "Anggara" and panca.name == "Kliwon":
            inauspicious_labels.append("Anggara Kasih（火曜凶日）")
            notes.append("Anggara Kasih 為火曜凶日，忌重大決定")

        # Buda Cemeng = Sapta Wara Buda + Panca Wara Kliwon
        if sapta.name == "Buda" and panca.name == "Kliwon":
            inauspicious_labels.append("Buda Cemeng（水曜凶日）")
            notes.append("Buda Cemeng 為水曜凶日，宜謹慎行事")

        # Tumpek = Sapta Wara Saniscara + Panca Wara Kliwon
        if sapta.name == "Saniscara" and panca.name == "Kliwon":
            # Tumpek 有多種類型，某些視為吉
            inauspicious_labels.append("Tumpek（土曜特殊日）")
            tumpek_type = self._get_tumpek_type(wuku.index)
            notes.append(f"Tumpek 類型：{tumpek_type}")

        # Buda Kliwon Pahang（大凶）
        if (sapta.name == "Buda" and panca.name == "Kliwon"
                and wuku.name == "Pahang"):
            inauspicious_labels.append("Buda Kliwon Pahang（大凶日）")

        # (5) Neptu 總和 ≥ 10 且無特殊吉日標記 → 偏凶
        if neptu_sum >= 10 and not auspicious_labels:
            inauspicious_labels.append("Neptu 總和偏高（≥ 10）")

        # (6) Pancasuda 吉凶判斷
        if pancasuda_idx in (0, 1, 2):
            auspicious_labels.append(f"Pancasuda 吉：{ps_name}")
        elif pancasuda_idx in (3, 4, 5, 6):
            inauspicious_labels.append(f"Pancasuda 凶：{ps_name}")

        # 總體判斷
        is_auspicious = (
            len(auspicious_labels) > 0
            and len(inauspicious_labels) == 0
        )

        return DewasaInfo(
            is_auspicious=is_auspicious,
            auspicious_labels=auspicious_labels,
            inauspicious_labels=inauspicious_labels,
            neptu_sum=neptu_sum,
            pancasuda=ps_name,
            pancasuda_meaning=ps_meaning,
            notes=notes,
        )

    def _get_tumpek_type(self, wuku_index: int) -> str:
        """
        根據 Wuku 判斷 Tumpek 類型

        每 35 天出現一次 Tumpek（Saniscara + Kliwon），
        在 210 天週期中共有 6 個 Tumpek，各有不同意義。

        古法依據：Lontar Wariga — Tumpek 分類

        回傳：
            str: Tumpek 類型名稱
        """
        # 6 種 Tumpek 類型，按 Wuku 範圍劃分
        tumpek_types = {
            (0, 4):   "Tumpek Landep（器具日）",
            (5, 9):   "Tumpek Uduh / Pengatag（植物日）",
            (10, 14): "Tumpek Kuningan（祖靈日）",
            (15, 19): "Tumpek Krulut（音樂/藝術日）",
            (20, 24): "Tumpek Kandang（動物日）",
            (25, 29): "Tumpek Wayang（皮影戲日）",
        }
        for (low, high), name in tumpek_types.items():
            if low <= wuku_index <= high:
                return name
        return "Tumpek（未分類）"

    def _compute_ala_ayuning_detail(self, r: "WarigaResult") -> AlaAyuningDetail:
        """
        計算增強版 Ala Ayuning Dewasa（5 因素分析）

        依 Lontar Wariga Dewasa 的古典五因素規則：
        1. Wuku（Pawukon 週）
        2. Wewaran（尤其 Tri+Panca+Sapta Wara 組合）
        3. Sasih（Saka 農曆月）
        4. Penanggal/Panglong（月相日）
        5. Dawuh（時辰）

        回傳：
            AlaAyuningDetail: 含 Uttama/Madya/Ala 等級的完整分析
        """
        panca  = r.panca_wara
        sapta  = r.sapta_wara
        tri    = r.tri_wara
        wuku   = r.wuku
        sasih  = r.sasih
        penan  = r.penanggal
        ad     = r.asta_dauh

        uttama_factors: List[str] = []
        madya_factors:  List[str] = []
        ala_factors:    List[str] = []
        special_holy_day = ""

        # ── 因素 1：Wuku ───────────────────────────────────────
        if wuku.index in UTTAMA_WUKU:
            uttama_factors.append(f"Wuku {wuku.name}（天生大吉週）")
        elif wuku.index in ALA_WUKU:
            ala_factors.append(f"Wuku {wuku.name}（謹慎週）")
        else:
            wuku_qual = WUKU_ATTRIBUTES[wuku.index][4] if wuku.index < len(WUKU_ATTRIBUTES) else ""
            if wuku_qual in ("吉", "大吉"):
                madya_factors.append(f"Wuku {wuku.name}（吉週）")

        # ── 因素 2：Wewaran 特殊組合 ──────────────────────────
        # 大凶特殊日（最優先）
        if sapta.name == "Buda" and panca.name == "Kliwon" and wuku.name == "Pahang":
            ala_factors.append("Buda Kliwon Pahang（Lontar 記載最大凶日）")
            special_holy_day = "Buda Kliwon Pahang"
        # Kajeng Kliwon（大忌）
        if tri.name == "Kajeng" and panca.name == "Kliwon":
            ala_factors.append("Kajeng Kliwon（三日週期忌日，惡靈出沒）")
            special_holy_day = special_holy_day or "Kajeng Kliwon"
        # Anggara Kasih（火曜凶）
        if sapta.name == "Anggara" and panca.name == "Kliwon":
            ala_factors.append("Anggara Kasih（火曜Kliwon 凶日）")
            special_holy_day = special_holy_day or "Anggara Kasih"
        # Buda Cemeng（水曜凶，Klawu 週除外）
        if sapta.name == "Buda" and panca.name == "Kliwon" and wuku.name != "Klawu":
            ala_factors.append("Buda Cemeng（水曜Kliwon 凶日）")
            special_holy_day = special_holy_day or "Buda Cemeng"

        # Galungan（大吉聖日）
        if wuku.name == "Dungulan" and sapta.name == "Buda" and panca.name == "Kliwon":
            uttama_factors.append("🎊 Hari Raya Galungan（天神降臨大吉日）")
            # 移除 Buda Cemeng 凶項（Galungan 優先）
            ala_factors = [f for f in ala_factors if "Buda Cemeng" not in f]
            special_holy_day = "Galungan"
        # Kuningan（大吉聖日）
        if wuku.name == "Kuningan" and sapta.name == "Saniscara" and panca.name == "Kliwon":
            uttama_factors.append("🎊 Hari Raya Kuningan（天神護佑祖靈日）")
            special_holy_day = "Kuningan"
        # Tumpek（聖日，6 種）
        if sapta.name == "Saniscara" and panca.name == "Kliwon":
            tumpek = self._get_tumpek_type(wuku.index)
            uttama_factors.append(f"🙏 {tumpek}（Tumpek 聖日）")
            if not special_holy_day:
                special_holy_day = tumpek.split("（")[0]
        # Sugihan（淨化日）
        if wuku.name == "Sungsang":
            if sapta.name == "Saniscara":
                madya_factors.append("Sugihan Bali（大地淨化日）")
            elif sapta.name == "Wraspati":
                madya_factors.append("Sugihan Jawa（自身靈魂淨化日）")
        # Buda Kliwon Klawu（特殊小吉，非凶）
        if wuku.name == "Klawu" and sapta.name == "Buda" and panca.name == "Kliwon":
            madya_factors.append("Buda Kliwon Klawu（自然女神聖日，宜靜修）")
            ala_factors = [f for f in ala_factors if "Buda Cemeng" not in f]

        # 良好 Wewaran 組合
        combo_key = (sapta.name, panca.name)
        if combo_key in GOOD_WEWARAN_COMBOS:
            combo_desc, _ = GOOD_WEWARAN_COMBOS[combo_key]
            # 避免 Tumpek 重複計入
            if "Tumpek" not in combo_desc:
                madya_factors.append(combo_desc)

        # ── 因素 3：Sasih（月份）────────────────────────────
        # Sasih Kasa~Kapat（1-4）通常為宜辦喜事之月
        _ayu_sasih = {0: "Kasa", 1: "Karo", 2: "Katiga", 3: "Kapat", 9: "Kadasa", 11: "Sada"}
        # Kasanga（3月，3之倍數多禁忌）等部分月份有特殊限制
        _ala_sasih = {8: "Kasanga（傳統忌大事）"}
        if sasih.sasih_index in _ayu_sasih:
            madya_factors.append(f"Sasih {sasih.sasih_name}（吉月，宜辦喜事）")
        elif sasih.sasih_index in _ala_sasih:
            madya_factors.append(f"Sasih {sasih.sasih_name}（謹慎月）")

        # ── 因素 4：Penanggal / Panglong（月相日）───────────
        if penan.special == "Purnama（滿月聖日）":
            uttama_factors.append("🌕 Purnama 滿月（大吉聖日，宜祈福）")
            special_holy_day = special_holy_day or "Purnama"
        elif penan.special == "Tilem（新月聖日）":
            # Tilem 對靈修大吉，但對俗事為凶
            ala_factors.append("🌑 Tilem 新月（靈界活躍，俗事需謹慎）")
            special_holy_day = special_holy_day or "Tilem"
        else:
            # 部分特殊 Tithi
            if penan.is_penanggal:
                if penan.day_number in (1, 2, 4, 6, 7, 11, 12):
                    madya_factors.append(f"Penanggal {penan.day_number}（吉 Tithi）")
                elif penan.day_number in (9, 13):
                    ala_factors.append(f"Penanggal {penan.day_number}（謹慎 Tithi）")

        # ── 因素 5：Dawuh（時辰）────────────────────────────
        if ad.quality == "吉":
            madya_factors.append(f"Asta Dauh {ad.name}（吉時）")
        elif ad.quality == "凶":
            ala_factors.append(f"Asta Dauh {ad.name}（凶時）")

        # ── 判斷等級 ─────────────────────────────────────────
        has_super_ala  = any("Buda Kliwon Pahang" in f for f in ala_factors)
        has_major_ala  = any(kw in " ".join(ala_factors)
                             for kw in ("Kajeng Kliwon", "Anggara Kasih", "Buda Cemeng", "Tilem"))
        has_galungan   = any("Galungan" in f or "Kuningan" in f for f in uttama_factors)

        if has_super_ala:
            level, level_cn, color = "Ala", "大凶", "#7B0000"
        elif has_galungan or (uttama_factors and not ala_factors):
            level, level_cn, color = "Uttama", "上吉", "#1B5E20"
        elif uttama_factors and ala_factors:
            level, level_cn, color = "Madya", "中吉", "#E65100"
        elif has_major_ala:
            level, level_cn, color = "Ala", "凶", "#B71C1C"
        elif ala_factors:
            level, level_cn, color = "Madya", "中平", "#BF360C"
        elif len(madya_factors) >= 3:
            level, level_cn, color = "Uttama", "上吉", "#2E7D32"
        elif madya_factors:
            level, level_cn, color = "Madya", "中吉", "#F57F17"
        else:
            level, level_cn, color = "Madya", "平", "#795548"

        # ── 說明文字 ─────────────────────────────────────────
        purnama_label = "Purnama" if penan.special == "Purnama（滿月聖日）" else ""
        tilem_label   = "Tilem" if penan.special == "Tilem（新月聖日）" else ""
        tithi_label   = (purnama_label or tilem_label
                         or f"{'Penanggal' if penan.is_penanggal else 'Panglong'} {penan.day_number}")
        explanation = (
            f"因 Wuku {wuku.name}（{WUKU_ATTRIBUTES[wuku.index][4] if wuku.index < len(WUKU_ATTRIBUTES) else ''}）"
            f" + {sapta.name} {panca.name}"
            f" + Sasih {sasih.sasih_name}"
            f" + {tithi_label}"
            f" → {level_cn}（{level}）"
        )

        # ── 因素彙總（帶符號） ───────────────────────────────
        factor_summary: List[str] = []
        for f in uttama_factors:
            factor_summary.append(f"✨ {f}")
        for f in madya_factors:
            factor_summary.append(f"⚪ {f}")
        for f in ala_factors:
            factor_summary.append(f"⚠️ {f}")

        # ── 各活動建議 ───────────────────────────────────────
        activity_advice: dict = {}
        for act_key, rule in ACTIVITY_RULES.items():
            # 計算這個活動的適配分數
            act_score = 0
            act_notes = []
            if panca.name in rule.get("best_panca", []):
                act_score += 2
            if sapta.name in rule.get("best_sapta", []):
                act_score += 2
            if sasih.sasih_index in rule.get("best_sasih", []):
                act_score += 1
            if combo_key in [(s, p) for (s, p) in rule.get("best_combo", [])]:
                act_score += 3
                act_notes.append(f"最佳 {sapta.name} {panca.name} 組合")
            if panca.name in rule.get("avoid_panca", []) or sapta.name in rule.get("avoid_sapta", []):
                act_score -= 3
                act_notes.append("Wewaran 不宜")
            if wuku.name in rule.get("avoid_wuku", []):
                act_score -= 2
                act_notes.append(f"Wuku {wuku.name} 忌此活動")
            if tri.name in rule.get("avoid_tri", []) and panca.name == "Kliwon":
                act_score -= 4
                act_notes.append("Kajeng Kliwon 忌此活動")
            if has_super_ala:
                act_score = -10
                act_notes = ["Buda Kliwon Pahang 萬事皆忌"]
            if purnama_label:
                act_score += 2
                act_notes.append("Purnama 加持")

            if act_score >= 4:
                act_level = "✅ 大吉"
            elif act_score >= 2:
                act_level = "🟡 吉"
            elif act_score >= 0:
                act_level = "⚪ 普通"
            else:
                act_level = "🔴 不宜"

            activity_advice[act_key] = {
                "name_cn": rule["name_cn"],
                "icon": rule.get("icon", ""),
                "level": act_level,
                "score": act_score,
                "notes": act_notes or [rule.get("notes", "")],
            }

        return AlaAyuningDetail(
            level=level,
            level_cn=level_cn,
            color=color,
            uttama_factors=uttama_factors,
            madya_factors=madya_factors,
            ala_factors=ala_factors,
            explanation=explanation,
            factor_summary=factor_summary,
            special_holy_day=special_holy_day,
            activity_advice=activity_advice,
        )

    def _compute_panca_dauh(self, hour: int) -> DauhInfo:
        """
        計算 Panca Dauh 時辰（5 時辰劃分）

        依照傳統 Lontar Wariga，一日分為 5 個 Dauh，
        每個 Dauh 約 4.8 小時，各歸屬特定神明掌管。

        古法依據：Lontar Wariga — Panca Dauh 時辰表

        回傳：
            DauhInfo: Panca Dauh 時辰資訊
        """
        selected = PANCA_DAUH[0]  # 預設
        for entry in PANCA_DAUH:
            name, start, end, deity, quality, desc = entry
            if start <= hour < end:
                selected = entry
                break
        name, start, end, deity, quality, desc = selected
        return DauhInfo(
            dauh_type="Panca Dauh",
            name=name,
            deity=deity,
            direction=desc,
            quality=quality,
        )

    def _compute_asta_dauh(self, hour: int) -> DauhInfo:
        """
        計算 Asta Dauh 時辰（8 時辰劃分，每 3 小時）

        Asta Dauh 為更精細的時辰系統，嚴格依照
        Lontar Wariga Gemet 的 8 方位神明體系。

        古法依據：Lontar Wariga Gemet — Asta Dauh

        回傳：
            DauhInfo: Asta Dauh 時辰資訊
        """
        selected = ASTA_DAUH[0]  # 預設
        for entry in ASTA_DAUH:
            name, start, end, direction, quality, desc = entry
            if start <= hour < end:
                selected = entry
                break
        name, start, end, direction, quality, desc = selected
        return DauhInfo(
            dauh_type="Asta Dauh",
            name=name,
            deity=desc,
            direction=direction,
            quality=quality,
        )

    def _compute_penanggal(self, sun_lon: float, moon_lon: float) -> PenanggalInfo:
        """
        計算 Penanggal / Panglong（月相日）

        月相角度 = (月亮黃經 - 太陽黃經) mod 360
        - 0°~180°  → Penanggal（月盈期）1-15
        - 180°~360° → Panglong（月虧期）1-15

        Sasih 的階層規則：
        「Penanggal/Panglong alah dening Śaśih」
        月相日的計算服從於 Sasih 月份體系。

        古法依據：Lontar Wariga — Penanggal/Panglong 計算法

        回傳：
            PenanggalInfo: 月相日資訊
        """
        # 月相角度 (0-360)
        phase_deg = (moon_lon - sun_lon) % 360.0

        if phase_deg < 180.0:
            # 月盈期 (Penanggal)：0° ~ 180°，共 15 天
            day_num = max(1, min(15, int(phase_deg / 12.0) + 1))
            table = PENANGGAL_NAMES
            is_penanggal = True
        else:
            # 月虧期 (Panglong)：180° ~ 360°，共 15 天
            day_num = max(1, min(15, int((phase_deg - 180.0) / 12.0) + 1))
            table = PANGLONG_NAMES
            is_penanggal = False

        # 查找對應的表格條目
        entry = table[day_num - 1]
        seq, name, sanskrit, neptu = entry

        # 特殊聖日標記
        special = ""
        if is_penanggal and day_num == 15:
            special = "Purnama（滿月聖日）"
        elif not is_penanggal and day_num == 15:
            special = "Tilem（新月聖日）"

        return PenanggalInfo(
            is_penanggal=is_penanggal,
            day_number=day_num,
            name=name,
            neptu=neptu,
            moon_phase_deg=phase_deg,
            special=special,
        )

    def _compute_sasih(self, sun_lon, moon_lon) -> SasihInfo:
        """
        計算 Sasih（月份）與季節

        巴厘傳統 Sasih 為陰陽合曆，以太陽位置決定月份歸屬：
        - 太陽黃經每 30° 劃分一個 Sasih
        - 起始點約為 Sasih Kasa（太陽在巨蟹座附近，約黃經 90°-120°）

        季節判斷：
        - Sasih 1-6 (Kasa ~ Kanem): Lahru (乾季) / Dakshinayana（太陽南行）
        - Sasih 7-12 (Kapitu ~ Sada): Rengreng (雨季) / Uttarayana（太陽北行）

        古法依據：Lontar Wariga — Sasih 與季節劃分

        回傳：
            SasihInfo: 月份與季節資訊
        """
        # 太陽黃經 → Sasih 索引
        # Sasih Kasa 起始約太陽黃經 90°（夏至附近）
        # 每個 Sasih 約 30° 太陽行程
        sasih_idx = int(((sun_lon - 90.0) % 360.0) / 30.0)
        if sasih_idx < 0:
            sasih_idx += 12
        sasih_idx = sasih_idx % 12

        sasih_name = SASIH_NAMES[sasih_idx]
        sasih_number = sasih_idx + 1  # 1-based

        # 季節判斷
        if SEASON_LAHRU_RANGE[0] <= sasih_number <= SEASON_LAHRU_RANGE[1]:
            season = "Lahru (Kemarau)"
            season_cn = "乾季"
            ayana = "Dakshinayana（太陽南行）"
        else:
            season = "Rengreng (Penghujan)"
            season_cn = "雨季"
            ayana = "Uttarayana（太陽北行）"

        return SasihInfo(
            sasih_index=sasih_idx,
            sasih_name=sasih_name,
            season=season,
            season_cn=season_cn,
            ayana=ayana,
        )

    # --------------------------------------------------------
    # 結果轉換
    # --------------------------------------------------------

    @staticmethod
    def _wara_to_dict(w: WaraInfo) -> dict:
        """將 WaraInfo 轉為字典"""
        return {
            "wara_type": w.wara_type,
            "name": w.name,
            "neptu": w.neptu,
        }

    def _result_to_dict(self, r: WarigaResult) -> dict:
        """將 WarigaResult 轉為字典"""
        aad = r.ala_ayuning_detail
        return {
            "year": r.year,
            "month": r.month,
            "day": r.day,
            "hour": r.hour,
            "minute": r.minute,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "day_in_pawukon": r.day_in_pawukon,
            "wuku": {
                "index": r.wuku.index,
                "name": r.wuku.name,
                "neptu": r.wuku.neptu,
            },
            "eka_wara": self._wara_to_dict(r.eka_wara),
            "dwi_wara": self._wara_to_dict(r.dwi_wara),
            "tri_wara": self._wara_to_dict(r.tri_wara),
            "catur_wara": self._wara_to_dict(r.catur_wara),
            "panca_wara": self._wara_to_dict(r.panca_wara),
            "sad_wara": self._wara_to_dict(r.sad_wara),
            "sapta_wara": self._wara_to_dict(r.sapta_wara),
            "asta_wara": self._wara_to_dict(r.asta_wara),
            "sanga_wara": self._wara_to_dict(r.sanga_wara),
            "dasa_wara": self._wara_to_dict(r.dasa_wara),
            "ingkel": r.ingkel,
            "watek_alit": r.watek_alit,
            "watek_madya": r.watek_madya,
            "lintang": r.lintang,
            "dewasa": {
                "is_auspicious": r.dewasa.is_auspicious,
                "auspicious_labels": r.dewasa.auspicious_labels,
                "inauspicious_labels": r.dewasa.inauspicious_labels,
                "neptu_sum": r.dewasa.neptu_sum,
                "pancasuda": r.dewasa.pancasuda,
                "pancasuda_meaning": r.dewasa.pancasuda_meaning,
                "notes": r.dewasa.notes,
            },
            "ala_ayuning_detail": {
                "level": aad.level,
                "level_cn": aad.level_cn,
                "color": aad.color,
                "uttama_factors": aad.uttama_factors,
                "madya_factors": aad.madya_factors,
                "ala_factors": aad.ala_factors,
                "explanation": aad.explanation,
                "special_holy_day": aad.special_holy_day,
            } if aad else None,
            "sasih": {
                "sasih_index": r.sasih.sasih_index,
                "sasih_name": r.sasih.sasih_name,
                "season": r.sasih.season,
                "season_cn": r.sasih.season_cn,
                "ayana": r.sasih.ayana,
            },
            "panca_dauh": {
                "name": r.panca_dauh.name,
                "deity": r.panca_dauh.deity,
                "direction": r.panca_dauh.direction,
                "quality": r.panca_dauh.quality,
            },
            "asta_dauh": {
                "name": r.asta_dauh.name,
                "deity": r.asta_dauh.deity,
                "direction": r.asta_dauh.direction,
                "quality": r.asta_dauh.quality,
            },
            "penanggal": {
                "is_penanggal": r.penanggal.is_penanggal,
                "day_number": r.penanggal.day_number,
                "name": r.penanggal.name,
                "neptu": r.penanggal.neptu,
                "moon_phase_deg": r.penanggal.moon_phase_deg,
                "special": r.penanggal.special,
            },
            "sun_longitude": r.sun_longitude,
            "moon_longitude": r.moon_longitude,
            "julian_day": r.julian_day,
        }


# ============================================================
# 快取便利函式 (Cached convenience function)
# ============================================================


@_st.cache_data(ttl=3600, show_spinner=False)
def compute_wariga(
    year: int, month: int, day: int,
    hour: int, minute: int,
    lat: float = -8.5069, lon: float = 115.2625,
) -> "WarigaResult":
    """Cached wrapper around :class:`WarigaCalculator`.compute_result().

    Default coordinates (-8.5069, 115.2625) are the centre of Bali, Indonesia,
    the home of the Wariga calendar tradition.
    """
    return WarigaCalculator(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        lat=lat, lon=lon,
    ).compute_result()


# ============================================================
# 新增獨立工具函式 (New Standalone Utility Functions)
# ============================================================

def calculate_otonan(
    birth_year: int, birth_month: int, birth_day: int,
) -> OtonanResult:
    """
    計算 Otonan（210天命主生日）

    Otonan 是巴厘傳統每隔 210 天的個人聖日，
    在出生時相同的 Wuku 週、Wewaran 組合再次出現。

    參數：
        birth_year  (int): 出生年份
        birth_month (int): 出生月份
        birth_day   (int): 出生日

    回傳：
        OtonanResult: 含出生 Wuku、下次 3 個 Otonan 日期、性格報告

    古法依據：Lontar Tattwa Krama — Otonan 章節
    """
    birth_calc = WarigaCalculator(birth_year, birth_month, birth_day)
    birth_result = birth_calc.compute_result()

    birth_pos = birth_result.day_in_pawukon
    birth_wuku = birth_result.wuku.name
    birth_wuku_idx = birth_result.wuku.index

    epoch = date(EPOCH_YEAR, EPOCH_MONTH, EPOCH_DAY)
    today = date.today()
    today_delta = (today - epoch).days
    today_pos   = today_delta % PAWUKON_CYCLE

    # 計算下次 Otonan 的天數差
    # (birth_pos - today_pos) % PAWUKON_CYCLE 給出今日之後最近的相同位置；
    # 若結果為 0 則今日恰好也是相同 Pawukon 位置，下次在 210 天後。
    diff = (birth_pos - today_pos) % PAWUKON_CYCLE
    if diff == 0:
        diff = PAWUKON_CYCLE

    next_otonan_dates: List[date] = []
    for i in range(3):
        delta = today_delta + diff + i * PAWUKON_CYCLE
        next_otonan_dates.append(epoch + timedelta(days=delta))

    wuku_profile = WUKU_DETAILS[birth_wuku_idx] if birth_wuku_idx < len(WUKU_DETAILS) else {}
    ritual_note  = OTONAN_RITUALS[birth_wuku_idx] if birth_wuku_idx < len(OTONAN_RITUALS) else ""

    return OtonanResult(
        birth_wuku=birth_wuku,
        birth_wuku_index=birth_wuku_idx,
        birth_day_in_pawukon=birth_pos,
        birth_panca_wara=birth_result.panca_wara.name,
        birth_sapta_wara=birth_result.sapta_wara.name,
        next_otonan_dates=next_otonan_dates,
        wuku_profile=wuku_profile,
        ritual_note=ritual_note,
    )


def find_dewasa_ayu(
    start_date: date,
    end_date: date,
    activity_type: Optional[str] = None,
    max_results: int = 5,
) -> List[dict]:
    """
    在指定日期範圍內搜尋最佳 Dewasa Ayu 吉日

    掃描每一天並按吉祥程度評分，回傳最佳的若干天。

    參數：
        start_date    (date): 搜尋起始日（含）
        end_date      (date): 搜尋結束日（含）
        activity_type (str):  活動類型（見 ACTIVITY_RULES 的鍵）
        max_results   (int):  最多回傳幾天（預設 5）

    回傳：
        list[dict]: 每個元素含 date, score, wuku, panca_wara, sapta_wara, reasons

    古法依據：Lontar Wariga Dewasa — Dewasa Ayu 擇日法
    """
    epoch = date(EPOCH_YEAR, EPOCH_MONTH, EPOCH_DAY)
    rule = ACTIVITY_RULES.get(activity_type, {}) if activity_type else {}
    candidates = []

    current = start_date
    while current <= end_date:
        delta        = (current - epoch).days
        day_p        = delta % PAWUKON_CYCLE
        wuku_idx     = day_p // 7
        panca_idx    = day_p % 5
        sapta_idx    = day_p % 7
        tri_idx      = day_p % 3

        wuku_name  = WUKU_TABLE[wuku_idx][0]
        panca_name = PANCA_WARA[panca_idx][0]
        sapta_name = SAPTA_WARA[sapta_idx][0]
        tri_name   = TRI_WARA[tri_idx][0]

        # 凶日直接跳過
        is_ala = (
            (tri_name   == "Kajeng" and panca_name == "Kliwon") or
            (sapta_name == "Anggara" and panca_name == "Kliwon") or
            (sapta_name == "Buda"   and panca_name == "Kliwon" and wuku_name != "Klawu") or
            wuku_idx in ALA_WUKU
        )
        # 允許靈性活動在 Kajeng Kliwon 等日
        if activity_type == "spiritual":
            is_ala = (sapta_name == "Buda" and panca_name == "Kliwon"
                      and wuku_name == "Pahang")  # 只有最大凶日才跳過

        if not is_ala:
            score   = 0
            reasons = []

            # 大吉聖日加分
            if wuku_idx in UTTAMA_WUKU:
                score += 3; reasons.append(f"Wuku {wuku_name}（大吉週）")
            if sapta_name == "Saniscara" and panca_name == "Kliwon":
                score += 4
                tumpek_types = {(0,4):"Tumpek Landep",(5,9):"Tumpek Uduh",(10,14):"Tumpek Kuningan",
                                (15,19):"Tumpek Krulut",(20,24):"Tumpek Kandang",(25,29):"Tumpek Wayang"}
                for (lo, hi), tn in tumpek_types.items():
                    if lo <= wuku_idx <= hi:
                        reasons.append(tn); break

            # 良好 Wewaran 組合
            combo = (sapta_name, panca_name)
            if combo in GOOD_WEWARAN_COMBOS:
                score += 2; reasons.append(GOOD_WEWARAN_COMBOS[combo][0])

            # 活動特定加分
            if rule:
                if panca_name in rule.get("best_panca", []):
                    score += 1
                if sapta_name in rule.get("best_sapta", []):
                    score += 1
                if combo in [(s, p) for (s, p) in rule.get("best_combo", [])]:
                    score += 2; reasons.append(f"最佳 {rule['name_cn']} 日")
                if panca_name in rule.get("avoid_panca", []) or sapta_name in rule.get("avoid_sapta", []):
                    score -= 2
                if wuku_name in rule.get("avoid_wuku", []):
                    score -= 2

            if score > 0:
                candidates.append({
                    "date": current,
                    "score": score,
                    "wuku": wuku_name,
                    "wuku_index": wuku_idx,
                    "panca_wara": panca_name,
                    "sapta_wara": sapta_name,
                    "reasons": reasons or [f"{sapta_name} {panca_name}"],
                })

        current += timedelta(days=1)

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:max_results]


def calculate_compatibility(
    year1: int, month1: int, day1: int,
    year2: int, month2: int, day2: int,
) -> CompatibilityResult:
    """
    計算兩人的 Wuku 緣分配對

    依照巴厘傳統 Pawatekan 相合理論，結合 Ingkel、Watek、
    Panca Wara 與 Sapta Wara 的 Neptu 差值計算緣分分數。

    參數：
        year1, month1, day1: 甲方出生日期
        year2, month2, day2: 乙方出生日期

    回傳：
        CompatibilityResult: 含緣分分數、等級與建議

    古法依據：Lontar Wariga — Pawatekan 相合章節
    """
    r1 = WarigaCalculator(year1, month1, day1).compute_result()
    r2 = WarigaCalculator(year2, month2, day2).compute_result()

    w1, w2   = r1.wuku.index, r2.wuku.index
    p1, p2   = r1.panca_wara, r2.panca_wara
    s1, s2   = r1.sapta_wara, r2.sapta_wara
    ingkel1  = INGKEL[w1 // 6]
    ingkel2  = INGKEL[w2 // 6]

    score = 50  # 基礎分

    # Ingkel 相合
    complement_pairs = {("Wong","Sato"),("Sato","Wong"),("Mina","Manuk"),("Manuk","Mina"),
                        ("Taru","Wong"),("Wong","Taru")}
    if ingkel1 == ingkel2:
        score += 5
    elif (ingkel1, ingkel2) in complement_pairs:
        score += 15

    # Watek Alit 相合
    wa1, _ = PAWATEKAN[w1]
    wa2, _ = PAWATEKAN[w2]
    alit_compat = {(0,2):15,(2,0):15,(1,3):15,(3,1):15,
                   (0,1):8,(1,0):8,(2,3):8,(3,2):8}
    score += alit_compat.get((wa1, wa2), 3)

    # Panca Wara Neptu 差值
    panca_diff = abs(p1.neptu - p2.neptu)
    if panca_diff <= 1:
        score += 12
    elif panca_diff <= 3:
        score += 6

    # Sapta Wara Neptu 差值
    sapta_diff = abs(s1.neptu - s2.neptu)
    if sapta_diff <= 1:
        score += 10
    elif sapta_diff <= 3:
        score += 5

    # Wuku 特殊搭配獎勵（使用整數索引與 UTTAMA_WUKU 比較）
    if {w1, w2} <= UTTAMA_WUKU or w1 == w2:
        score += 8

    score = max(0, min(100, score))

    if score >= 82:
        level, level_en = "天作之合 ✨", "Excellent"
        desc = "Wuku 組合極為吉祥，性格互補、緣分天定，共築美好家園"
        suggestions = "宜選 Purnama 或 Sukra Umanis 辦婚禮，請 Pedanda 主持儀式"
    elif score >= 68:
        level, level_en = "緣分不淺 🌸", "Good"
        desc = "Wuku 組合良好，相互理解後能建立深厚感情"
        suggestions = "宜共同參與靈性活動，定期辦 Otonan 感恩儀式"
    elif score >= 52:
        level, level_en = "平淡相守 🌿", "Moderate"
        desc = "Wuku 組合一般，需多溝通、相互包容"
        suggestions = "建議共同學習傳統 Wariga 智慧，請 Pemangku 指引生活方向"
    else:
        level, level_en = "緣分薄弱 🌧️", "Challenging"
        desc = "Wuku 組合有挑戰，需靈性修行化解業障差異"
        suggestions = "建議各自辦個人 Otonan 儀式，再辦合同 Pecaruan（業障清除）儀式"

    return CompatibilityResult(
        wuku1=r1.wuku.name, wuku2=r2.wuku.name,
        panca1=p1.name, panca2=p2.name,
        sapta1=s1.name, sapta2=s2.name,
        ingkel1=ingkel1, ingkel2=ingkel2,
        score=score,
        level=level, level_en=level_en,
        description=desc,
        suggestions=suggestions,
    )


@_st.cache_data(ttl=3600, show_spinner=False)
def cached_calculate_otonan(
    birth_year: int, birth_month: int, birth_day: int,
) -> OtonanResult:
    """快取版 calculate_otonan()"""
    return calculate_otonan(birth_year, birth_month, birth_day)


@_st.cache_data(ttl=600, show_spinner=False)
def cached_find_dewasa_ayu(
    start_year: int, start_month: int, start_day: int,
    end_year: int, end_month: int, end_day: int,
    activity_type: Optional[str] = None,
    max_results: int = 5,
) -> List[dict]:
    """快取版 find_dewasa_ayu()（日期拆分為整數以支援快取）"""
    return find_dewasa_ayu(
        start_date=date(start_year, start_month, start_day),
        end_date=date(end_year, end_month, end_day),
        activity_type=activity_type,
        max_results=max_results,
    )


@_st.cache_data(ttl=3600, show_spinner=False)
def cached_calculate_compatibility(
    year1: int, month1: int, day1: int,
    year2: int, month2: int, day2: int,
) -> CompatibilityResult:
    """快取版 calculate_compatibility()"""
    return calculate_compatibility(year1, month1, day1, year2, month2, day2)

