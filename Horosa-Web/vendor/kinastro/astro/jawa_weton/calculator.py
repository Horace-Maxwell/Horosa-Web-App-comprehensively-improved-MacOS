"""
爪哇 Weton / Primbon 計算核心模組 (Javanese Weton Calculator)

從格里高利日期計算 Saptawara（七曜）× Pancawara（五曜）= Weton，
並提供本命 Neptu、合婚計算（兩人 Neptu 相加）、
擇日判斷、以及 35 天 Weton 循環位置。

算法依據：
  - Saptawara：直接使用 Python datetime 星期值映射
  - Pancawara：使用已知基準日 2000-01-01 = Legi（index 0）的取模算法
    已與 maziyank/javaneseDate 及 beaudu/weton 交叉驗證

古法依據：Primbon Betaljemur Adammakna
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional, Tuple

from .constants import (
    SAPTAWARA, PANCAWARA,
    SAPTAWARA_NEPTU, PANCAWARA_NEPTU,
    WETON_PROFILES, MARRIAGE_COMPAT,
    SPECIAL_WETONS, DAILY_ACTIVITY_ADVICE,
    PASARAN_EPOCH_DATE, PASARAN_EPOCH_INDEX,
    WETON_CYCLE_ORDER,
)


# ============================================================
# 資料類定義 (Data Classes)
# ============================================================

@dataclass
class SaptawaraInfo:
    """Saptawara（七曜 / 星期）資訊"""
    index: int         # 索引 0=Minggu … 6=Sabtu
    name: str          # 爪哇名稱
    neptu: int         # Neptu 值
    cn: str            # 中文星期
    deity: str         # 主宰神明
    color: str         # 顏色象徵


@dataclass
class PancawaraInfo:
    """Pancawara（五曜 / Pasaran）資訊"""
    index: int         # 索引 0=Legi … 4=Kliwon
    name: str          # 爪哇名稱
    neptu: int         # Neptu 值
    cn: str            # 中文含義
    direction: str     # 方位
    deity: str         # 主宰神明
    color: str         # 顏色象徵


@dataclass
class WetonInfo:
    """完整 Weton 資訊"""
    saptawara: SaptawaraInfo
    pancawara: PancawaraInfo
    weton_name: str         # 組合名稱，如 "Jumat Kliwon"
    neptu_total: int        # Neptu 總值
    cycle_day: int          # 在35天週期中的位置 (0-34)
    is_special: bool        # 是否為特殊聖日
    special_name: str       # 特殊聖日名稱（若有）
    special_cn: str         # 特殊聖日中文名（若有）
    profile: dict           # Primbon 本命詳解
    daily_advice: dict      # 今日活動建議


@dataclass
class MarriageCompatResult:
    """合婚計算結果"""
    person1_weton: str       # 甲方 Weton 名
    person2_weton: str       # 乙方 Weton 名
    neptu1: int              # 甲方 Neptu
    neptu2: int              # 乙方 Neptu
    neptu_sum: int           # Neptu 總和
    remainder: int           # 總和 mod 9 (0-8, 0=9)
    compat_name: str         # 相容性名稱（爪哇）
    compat_cn: str           # 相容性中文名
    level: str               # 等級標記（含表情符號）
    color: str               # 顏色代碼
    description: str         # 詳細說明
    percentage: int          # 相容百分比 (0-100)


@dataclass
class WetonCalendarDay:
    """Weton 曆法中的單日資訊（用於多日視圖）"""
    date: date
    saptawara: str
    pancawara: str
    weton_name: str
    neptu: int
    is_special: bool
    special_name: str = ""


@dataclass
class WetonResult:
    """WetonCalculator 完整計算結果"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    # 核心 Weton
    weton: WetonInfo
    # 元資訊
    location_name: str = ""
    timezone: float = 7.0   # 爪哇標準時區 UTC+7


# ============================================================
# 核心計算類 (Core Calculator)
# ============================================================

class WetonCalculator:
    """
    爪哇傳統 Weton / Primbon 計算器

    從格里高利日期計算：
    1. Saptawara（七曜 / 爪哇星期）
    2. Pancawara（五曜 / Pasaran）
    3. Weton 組合名稱與 Neptu 值
    4. 本命 Primbon 解讀
    5. 合婚 Neptu 相容性

    算法核心：
    - Saptawara：date.isoweekday() % 7
      （Sun=0, Mon=1, ..., Sat=6 → 映射到 Minggu..Sabtu）
    - Pancawara：(delta_days + EPOCH_INDEX) % 5
      （基準日 2000-01-01 = Legi = index 0）

    古法依據：Primbon Betaljemur Adammakna
    """

    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        location_name: str = "",
        timezone: float = 7.0,
    ):
        """
        初始化計算器

        參數：
            year        (int): 格里高利年份
            month       (int): 月份 (1-12)
            day         (int): 日 (1-31)
            hour        (int): 時 (0-23)，預設 0
            minute      (int): 分 (0-59)，預設 0
            location_name (str): 地點名稱（顯示用）
            timezone  (float): 時區偏移（爪哇為 UTC+7）
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.location_name = location_name
        self.timezone = timezone

    # ── 公開介面 ──────────────────────────────────────────────

    def compute(self) -> WetonResult:
        """
        執行完整 Weton 計算，回傳 WetonResult

        回傳：
            WetonResult: 完整計算結果
        """
        target = date(self.year, self.month, self.day)
        weton = WetonCalculator._compute_weton_static(target)
        return WetonResult(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            weton=weton,
            location_name=self.location_name,
            timezone=self.timezone,
        )

    @staticmethod
    def compute_compatibility(
        weton1: WetonInfo,
        weton2: WetonInfo,
    ) -> MarriageCompatResult:
        """
        計算兩人合婚相容性

        算法：(neptu1 + neptu2) % 9，0 視為 9（Pesthi）

        參數：
            weton1 (WetonInfo): 甲方 Weton
            weton2 (WetonInfo): 乙方 Weton

        回傳：
            MarriageCompatResult: 合婚結果
        """
        neptu_sum = weton1.neptu_total + weton2.neptu_total
        remainder = neptu_sum % 9  # 0 → Pesthi (最吉)

        compat = MARRIAGE_COMPAT[remainder]
        compat_name, compat_cn, level, color, desc, pct = compat

        return MarriageCompatResult(
            person1_weton=weton1.weton_name,
            person2_weton=weton2.weton_name,
            neptu1=weton1.neptu_total,
            neptu2=weton2.neptu_total,
            neptu_sum=neptu_sum,
            remainder=remainder,
            compat_name=compat_name,
            compat_cn=compat_cn,
            level=level,
            color=color,
            description=desc,
            percentage=pct,
        )

    @staticmethod
    def compute_weton_for_date(target: date) -> WetonInfo:
        """
        計算指定日期的 Weton（靜態便捷方法）

        參數：
            target (date): 目標日期

        回傳：
            WetonInfo: 該日期的 Weton 資訊
        """
        return WetonCalculator._compute_weton_static(target)

    @staticmethod
    def get_weton_calendar(
        start_date: date,
        days: int = 35,
    ) -> List[WetonCalendarDay]:
        """
        生成指定起始日期後 N 天的 Weton 曆法

        參數：
            start_date (date): 起始日期
            days       (int) : 天數（預設35，完整一個 Weton 週期）

        回傳：
            List[WetonCalendarDay]: 每日 Weton 資訊列表
        """
        result = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            w = WetonCalculator._compute_weton_static(d)
            special_name = ""
            if w.is_special:
                special_name = w.special_name
            result.append(WetonCalendarDay(
                date=d,
                saptawara=w.saptawara.name,
                pancawara=w.pancawara.name,
                weton_name=w.weton_name,
                neptu=w.neptu_total,
                is_special=w.is_special,
                special_name=special_name,
            ))
        return result

    # ── 內部方法 ──────────────────────────────────────────────

    @staticmethod
    def _compute_weton_static(target: date) -> WetonInfo:
        """
        計算指定日期的完整 Weton 資訊

        參數：
            target (date): 目標日期

        回傳：
            WetonInfo: 完整 Weton 資訊
        """
        # 1) Saptawara：利用 Python 內建星期
        #    isoweekday(): Mon=1 … Sun=7
        #    mapping: 7%7=0=Minggu(Sun), 1%7=1=Senin(Mon), ..., 6%7=6=Sabtu(Sat)
        sapta_idx = target.isoweekday() % 7
        sw = SAPTAWARA[sapta_idx]
        saptawara = SaptawaraInfo(
            index=sapta_idx,
            name=sw[0],
            neptu=sw[1],
            cn=sw[2],
            deity=sw[4],
            color=sw[5],
        )

        # 2) Pancawara：基準日 2000-01-01 = index 0 (Legi)
        delta = (target - PASARAN_EPOCH_DATE).days
        panca_idx = (delta + PASARAN_EPOCH_INDEX) % 5
        pw = PANCAWARA[panca_idx]
        pancawara = PancawaraInfo(
            index=panca_idx,
            name=pw[0],
            neptu=pw[1],
            cn=pw[2],
            direction=pw[3],
            deity=pw[4],
            color=pw[5],
        )

        # 3) Weton 組合
        weton_name = f"{saptawara.name} {pancawara.name}"
        neptu_total = saptawara.neptu + pancawara.neptu

        # 4) 35 天循環位置
        cycle_day = sapta_idx * 5 + panca_idx

        # 5) 特殊聖日
        key = (saptawara.name, pancawara.name)
        special_info = SPECIAL_WETONS.get(key, {})
        is_special = bool(special_info)
        special_name = special_info.get("name", "")
        special_cn = special_info.get("cn", "")

        # 6) 本命 Primbon 解讀
        profile = WETON_PROFILES.get(key, {
            "neptu": neptu_total,
            "personality": "性格特質詳解暫未收錄。",
            "career": "事業傾向詳解暫未收錄。",
            "health": "健康提示詳解暫未收錄。",
            "lucky_direction": "東方",
            "lucky_color": "白色",
            "lucky_professions": [],
            "symbol": "⭐",
            "weton_nature": "一般",
        })

        # 7) 今日活動建議
        if neptu_total >= 15:
            daily_advice = DAILY_ACTIVITY_ADVICE["high_neptu"]
        elif neptu_total >= 10:
            daily_advice = DAILY_ACTIVITY_ADVICE["mid_neptu"]
        else:
            daily_advice = DAILY_ACTIVITY_ADVICE["low_neptu"]

        return WetonInfo(
            saptawara=saptawara,
            pancawara=pancawara,
            weton_name=weton_name,
            neptu_total=neptu_total,
            cycle_day=cycle_day,
            is_special=is_special,
            special_name=special_name,
            special_cn=special_cn,
            profile=profile,
            daily_advice=daily_advice,
        )


# ============================================================
# 模組級別便捷函數 (Module-level convenience functions)
# ============================================================

def compute_weton(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    location_name: str = "",
    timezone: float = 7.0,
) -> WetonResult:
    """
    便捷函數：計算指定日期的完整 Weton 結果

    參數：
        year  (int): 格里高利年份
        month (int): 月份
        day   (int): 日
        hour  (int): 時（可選）
        minute(int): 分（可選）
        location_name (str): 地點名稱
        timezone(float): 時區

    回傳：
        WetonResult: 完整計算結果

    範例：
        >>> result = compute_weton(1990, 1, 1)
        >>> print(result.weton.weton_name)
        'Senin Pon'
    """
    calc = WetonCalculator(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        location_name=location_name,
        timezone=timezone,
    )
    return calc.compute()
