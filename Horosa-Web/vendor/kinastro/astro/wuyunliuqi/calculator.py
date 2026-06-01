"""
五運六氣核心計算模組 (Wu Yun Liu Qi Core Calculator)

依據《黃帝內經·素問》運氣七篇，實作完整五運六氣推演：
1. 大運（Annual Movement）
2. 主運（Host Movements，五步）
3. 客運（Guest Movements，五步）
4. 司天之氣（Heavenly Domination Qi）
5. 在泉之氣（Earth's Spring Qi）
6. 主氣（Host Qi，六步）
7. 客氣（Guest Qi，六步）
8. 客主加臨（Guest-Host Interaction）
9. 運氣同化（Yun-Qi Assimilation）
10. 勝復鬱發（Victory-Revenge-Depression-Outbreak）

支援以節氣為單位的傳統推演與每分鐘精細計算。

古法依據：
- 《素問·天元紀大論》
- 《素問·五運行大論》
- 《素問·六微旨大論》
- 《素問·氣交變大論》
- 《素問·五常政大論》
- 《素問·六元正紀大論》
- 《素問·至真要大論》
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple, Dict, Any

from .constants import (
    TIANGAN, DIZHI, WUXING, WUYIN,
    TIANGAN_HUA_YUN, DAYUN_TABLE,
    ZHUYUN_ORDER,
    LIUQI_NAMES, LIUQI_SHORT, LIUQI_QI, LIUQI_WUXING,
    ZHUQI_ORDER,
    DIZHI_SITIAN, DIZHI_ZAIQUAN, SITIAN_ZAIQUAN,
    LIUQI_ORDER_INDEX, LIUQI_STEP_ORDER,
    get_keqi_steps, _get_keyun_order,
    DIZHI_WUXING, SITIAN_WUXING,
    SHENGFU, YUFA,
    QI_JIEQI_START,
    YUN_STEP_DAYS,
    ZHUYUN_BOUNDARIES_DAYS, ZHUQI_BOUNDARIES_DAYS,
    QI_ATTRIBUTES, YUN_ATTRIBUTES,
    HEALTH_ADVICE, TONG_HUA_DESC,
    get_ganzhi, JIAZI_CYCLE,
    TIANGAN_YINYANG,
)


# ============================================================
# 資料類定義 (Data Classes)
# ============================================================

@dataclass
class DaYunInfo:
    """大運（Annual Movement）資訊"""
    wuxing: str         # 五行：木火土金水
    tone: str           # 五音：角徵宮商羽
    taishao: str        # 太少（如太宮、少商）
    yinyang: str        # 陰陽（陽年太運，陰年少運）
    is_tai: bool        # 是否太過（True=太過，False=不及）
    attributes: dict    # 詳細屬性


@dataclass
class ZhuYunStep:
    """主運單步資訊"""
    step_name: str      # 步名：初運/二運/三運/四運/終運
    wuxing: str         # 五行
    tone: str           # 五音
    taishao: str        # 太少
    start_day: float    # 距年起（大寒）天數
    end_day: float      # 距年起（大寒）天數


@dataclass
class KeYunStep:
    """客運單步資訊"""
    step_name: str      # 步名
    wuxing: str         # 五行
    tone: str           # 五音
    taishao: str        # 太少


@dataclass
class ZhuQiStep:
    """主氣單步資訊"""
    step_name: str      # 步名：初之氣/.../終之氣
    qi_name: str        # 氣名：厥陰風木等
    nature: str         # 氣性：風熱火濕燥寒
    start_day: float    # 距年起（大寒）天數
    end_day: float      # 距年起（大寒）天數
    attributes: dict    # 詳細屬性


@dataclass
class KeQiStep:
    """客氣單步資訊"""
    step_name: str      # 步名
    qi_name: str        # 氣名
    nature: str         # 氣性
    attributes: dict    # 詳細屬性


@dataclass
class KeZhuJiaLin:
    """客主加臨資訊（某一步的客主互動）"""
    step_name: str      # 步名
    zhuqi: str          # 主氣
    keqi: str           # 客氣
    relation: str       # 關係：順化/相得/不相得/相克
    effect: str         # 影響說明


@dataclass
class TongHuaResult:
    """運氣同化結果"""
    is_tianfu: bool         # 天符
    is_suihui: bool         # 歲會
    is_taiyi_tianfu: bool   # 太乙天符
    is_tong_tianfu: bool    # 同天符
    is_tong_suihui: bool    # 同歲會
    categories: List[str]   # 所屬類型列表
    description: str        # 說明


@dataclass
class ShengFuResult:
    """勝復結果"""
    has_sheng: bool         # 是否有勝氣
    sheng_qi: str           # 勝氣（五行）
    fu_qi: str              # 復氣（五行）
    sheng_desc: str         # 勝氣說明
    fu_desc: str            # 復氣說明


@dataclass
class CurrentQiPosition:
    """當前時刻的運氣位置（精細計算結果）"""
    # 時間資訊
    year: int
    month: int
    day: int
    hour: int
    minute: int
    # 大運
    dayun: DaYunInfo
    # 當前主運步
    current_zhuyun: ZhuYunStep
    current_zhuyun_index: int       # 0-4
    zhuyun_progress_pct: float      # 當前步進度百分比 0-100
    days_in_zhuyun: float           # 已進入本步天數
    # 當前客運步
    current_keyun: KeYunStep
    current_keyun_index: int        # 0-4
    # 當前主氣步
    current_zhuqi: ZhuQiStep
    current_zhuqi_index: int        # 0-5
    zhuqi_progress_pct: float       # 當前步進度百分比 0-100
    days_in_zhuqi: float            # 已進入本步天數
    # 當前客氣步
    current_keqi: KeQiStep
    current_keqi_index: int         # 0-5
    # 司天在泉
    sitian: str
    zaiquan: str
    # 客主加臨
    jialin: KeZhuJiaLin
    # 同化
    tonghua: TongHuaResult
    # 勝復
    shengfu: ShengFuResult


@dataclass
class WuYunLiuQiResult:
    """五運六氣完整年度計算結果"""
    # 干支年
    year: int
    tiangan: str
    dizhi: str
    ganzhi: str
    yinyang: str        # 陰年/陽年
    # 大運
    dayun: DaYunInfo
    # 主運五步
    zhuyun_steps: List[ZhuYunStep]
    # 客運五步
    keyun_steps: List[KeYunStep]
    # 司天在泉
    sitian: str
    zaiquan: str
    # 主氣六步
    zhuqi_steps: List[ZhuQiStep]
    # 客氣六步
    keqi_steps: List[KeQiStep]
    # 客主加臨（六步）
    jialin_steps: List[KeZhuJiaLin]
    # 運氣同化
    tonghua: TongHuaResult
    # 勝復
    shengfu: ShengFuResult
    # 鬱發建議
    yufa: dict
    # 當前時刻精細位置（可選）
    current_position: Optional[CurrentQiPosition] = None


# ============================================================
# 核心計算類
# ============================================================

class WuYunLiuQiCalculator:
    """
    五運六氣計算器

    完整實作《黃帝內經》運氣七篇的推演體系，
    支援年度完整計算與任意時刻（年月日時分）精細計算。

    古法依據：
    - 天干紀運：甲己化土、乙庚化金、丙辛化水、丁壬化木、戊癸化火
    - 地支紀氣：子午少陰君火、丑未太陰濕土、寅申少陽相火
               卯酉陽明燥金、辰戌太陽寒水、巳亥厥陰風木
    - 陽年太運（太過），陰年少運（不及）
    - 五運六氣年起大寒日，以六十甲子為週期
    """

    def __init__(
        self,
        year: int,
        month: int = 1,
        day: int = 20,
        hour: int = 0,
        minute: int = 0,
    ):
        """
        初始化計算器

        參數：
            year   (int): 西曆年份（如2024）
            month  (int): 月份（精細計算用，預設1）
            day    (int): 日（精細計算用，預設20）
            hour   (int): 時（精細計算用，預設0）
            minute (int): 分（精細計算用，預設0）
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self._dt = datetime(year, month, day, hour, minute)

    # ── 公開介面 ──────────────────────────────────────────────

    def compute(self) -> WuYunLiuQiResult:
        """
        執行完整五運六氣年度計算

        回傳：
            WuYunLiuQiResult: 完整計算結果
        """
        # 確定運氣年所屬干支
        # 注意：五運六氣年從大寒開始，約1月20日
        # 若輸入時間在大寒前，則屬於上一個運氣年
        yun_year = self._get_yun_year()
        tg, dz, gz = get_ganzhi(yun_year)
        yinyang = TIANGAN_YINYANG[tg]

        # 1. 大運
        dayun = self._compute_dayun(tg, yinyang)

        # 2. 主運五步
        zhuyun_steps = self._compute_zhuyun()

        # 3. 客運五步
        keyun_steps = self._compute_keyun(dayun)

        # 4. 司天在泉
        sitian = DIZHI_SITIAN[dz]
        zaiquan = DIZHI_ZAIQUAN[dz]

        # 5. 主氣六步
        zhuqi_steps = self._compute_zhuqi()

        # 6. 客氣六步
        keqi_steps = self._compute_keqi(sitian)

        # 7. 客主加臨
        jialin_steps = self._compute_jialin(zhuqi_steps, keqi_steps)

        # 8. 運氣同化
        tonghua = self._compute_tonghua(tg, dz, dayun, sitian, yinyang)

        # 9. 勝復
        shengfu = self._compute_shengfu(dayun)

        # 10. 鬱發（各運之鬱發建議）
        yufa_result = {wx: YUFA[wx] for wx in WUXING}

        # 11. 當前時刻精細位置
        current_pos = self._compute_current_position(
            yun_year, tg, dz, dayun, zhuyun_steps, keyun_steps,
            zhuqi_steps, keqi_steps, sitian, zaiquan, jialin_steps,
            tonghua, shengfu,
        )

        return WuYunLiuQiResult(
            year=yun_year,
            tiangan=tg,
            dizhi=dz,
            ganzhi=gz,
            yinyang=yinyang,
            dayun=dayun,
            zhuyun_steps=zhuyun_steps,
            keyun_steps=keyun_steps,
            sitian=sitian,
            zaiquan=zaiquan,
            zhuqi_steps=zhuqi_steps,
            keqi_steps=keqi_steps,
            jialin_steps=jialin_steps,
            tonghua=tonghua,
            shengfu=shengfu,
            yufa=yufa_result,
            current_position=current_pos,
        )

    def compute_minute_series(
        self,
        start_dt: datetime,
        end_dt: datetime,
        step_minutes: int = 60,
    ) -> List[Dict[str, Any]]:
        """
        計算時間範圍內每N分鐘的運氣狀態，用於運氣變化曲線

        參數：
            start_dt     (datetime): 起始時間
            end_dt       (datetime): 結束時間
            step_minutes (int): 步長（分鐘），預設60

        回傳：
            List[Dict]: 每個時間點的運氣簡要狀態
        """
        results = []
        current = start_dt
        delta = timedelta(minutes=step_minutes)
        while current <= end_dt:
            calc = WuYunLiuQiCalculator(
                current.year, current.month, current.day,
                current.hour, current.minute,
            )
            result = calc.compute()
            pos = result.current_position
            if pos:
                results.append({
                    "datetime": current,
                    "ganzhi": result.ganzhi,
                    "dayun": f"{result.dayun.taishao}（{result.dayun.wuxing}）",
                    "zhuyun": f"{pos.current_zhuyun.step_name}·{pos.current_zhuyun.taishao}",
                    "keyun": f"{pos.current_keyun.step_name}·{pos.current_keyun.taishao}",
                    "zhuqi": f"{pos.current_zhuqi.step_name}·{pos.current_zhuqi.qi_name}",
                    "keqi": f"{pos.current_keqi.step_name}·{pos.current_keqi.qi_name}",
                    "sitian": result.sitian,
                    "zaiquan": result.zaiquan,
                    "jialin_relation": pos.jialin.relation,
                    "zhuyun_progress": pos.zhuyun_progress_pct,
                    "zhuqi_progress": pos.zhuqi_progress_pct,
                    "tonghua": result.tonghua.categories,
                })
            current += delta
        return results

    # ── 私有計算方法 ──────────────────────────────────────────

    def _get_yun_year(self) -> int:
        """
        確定運氣年份

        五運六氣年從大寒起算（約1月20日）。
        若當前日期在大寒前，則屬於上一個運氣年。

        回傳：
            int: 運氣年份
        """
        # 近似：以1月20日為大寒基準
        dahan_approx = date(self.year, 1, 20)
        input_date = date(self.year, self.month, self.day)
        if input_date < dahan_approx:
            return self.year - 1
        return self.year

    def _get_year_start_date(self, yun_year: int) -> date:
        """取得運氣年起始日（大寒，近似1月20日）"""
        return date(yun_year, 1, 20)

    def _days_from_year_start(self, yun_year: int) -> float:
        """計算當前時刻距離本運氣年起始（大寒）的天數（含小時分鐘）"""
        year_start = self._get_year_start_date(yun_year)
        start_dt = datetime(year_start.year, year_start.month, year_start.day)
        delta = self._dt - start_dt
        return delta.total_seconds() / 86400.0

    def _compute_dayun(self, tg: str, yinyang: str) -> DaYunInfo:
        """計算大運"""
        wuxing, tone, taishao = DAYUN_TABLE[tg]
        is_tai = yinyang == "陽"  # 陽年太運，陰年少運
        attrs = YUN_ATTRIBUTES.get(wuxing, {})
        return DaYunInfo(
            wuxing=wuxing,
            tone=tone,
            taishao=taishao,
            yinyang=yinyang,
            is_tai=is_tai,
            attributes=attrs,
        )

    def _compute_zhuyun(self) -> List[ZhuYunStep]:
        """計算主運五步"""
        steps = []
        for i, (name, wx, tone, taishao) in enumerate(ZHUYUN_ORDER):
            start_d = ZHUYUN_BOUNDARIES_DAYS[i]
            end_d = ZHUYUN_BOUNDARIES_DAYS[i + 1]
            steps.append(ZhuYunStep(
                step_name=name,
                wuxing=wx,
                tone=tone,
                taishao=taishao,
                start_day=start_d,
                end_day=end_d,
            ))
        return steps

    def _compute_keyun(self, dayun: DaYunInfo) -> List[KeYunStep]:
        """計算客運五步（以大運為初運，按五行相生推五步）"""
        keyun_order = _get_keyun_order(dayun.wuxing, dayun.taishao)
        steps = []
        for name, wx, tone, taishao in keyun_order:
            steps.append(KeYunStep(
                step_name=name,
                wuxing=wx,
                tone=tone,
                taishao=taishao,
            ))
        return steps

    def _compute_zhuqi(self) -> List[ZhuQiStep]:
        """計算主氣六步"""
        steps = []
        for i, (name, qi_name, nature) in enumerate(ZHUQI_ORDER):
            start_d = ZHUQI_BOUNDARIES_DAYS[i]
            end_d = ZHUQI_BOUNDARIES_DAYS[i + 1]
            attrs = QI_ATTRIBUTES.get(qi_name, {})
            steps.append(ZhuQiStep(
                step_name=name,
                qi_name=qi_name,
                nature=nature,
                start_day=start_d,
                end_day=end_d,
                attributes=attrs,
            ))
        return steps

    def _compute_keqi(self, sitian: str) -> List[KeQiStep]:
        """計算客氣六步（以司天為三之氣）"""
        keqi_order = get_keqi_steps(sitian)
        step_names = ["初之氣", "二之氣", "三之氣", "四之氣", "五之氣", "終之氣"]
        nature_map = {
            "厥陰風木": "風", "少陰君火": "熱", "少陽相火": "火",
            "太陰濕土": "濕", "陽明燥金": "燥", "太陽寒水": "寒",
        }
        steps = []
        for i, qi_name in enumerate(keqi_order):
            nature = nature_map.get(qi_name, "")
            attrs = QI_ATTRIBUTES.get(qi_name, {})
            steps.append(KeQiStep(
                step_name=step_names[i],
                qi_name=qi_name,
                nature=nature,
                attributes=attrs,
            ))
        return steps

    def _compute_jialin(
        self,
        zhuqi_steps: List[ZhuQiStep],
        keqi_steps: List[KeQiStep],
    ) -> List[KeZhuJiaLin]:
        """
        計算客主加臨（六步）

        加臨規則（《素問·六微旨大論》）：
        - 客生主：小逆（客氣五行生主氣五行）
        - 客克主：不和（客氣五行克主氣五行）
        - 主生客：順（主氣五行生客氣五行）
        - 主克客：逆（主氣五行克客氣五行）
        - 同氣相遇：和（客主同一五行或同類氣）
        """
        results = []
        for i in range(6):
            zhuqi = zhuqi_steps[i]
            keqi = keqi_steps[i]
            relation, effect = self._get_jialin_relation(
                zhuqi.qi_name, keqi.qi_name
            )
            results.append(KeZhuJiaLin(
                step_name=zhuqi.step_name,
                zhuqi=zhuqi.qi_name,
                keqi=keqi.qi_name,
                relation=relation,
                effect=effect,
            ))
        return results

    def _get_jialin_relation(self, zhuqi_name: str, keqi_name: str) -> Tuple[str, str]:
        """
        判斷客主加臨關係

        回傳：
            (str, str): (關係名稱, 影響說明)
        """
        zhu_wx = LIUQI_WUXING[LIUQI_NAMES.index(zhuqi_name)] if zhuqi_name in LIUQI_NAMES else ""
        ke_wx = LIUQI_WUXING[LIUQI_NAMES.index(keqi_name)] if keqi_name in LIUQI_NAMES else ""

        # 五行相生克關係
        SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        KE = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}

        if zhu_wx == ke_wx:
            return "同化", "客主同氣，化氣和平，氣候正常，少有疾病。"
        elif SHENG.get(zhu_wx) == ke_wx:
            return "順化", "主生客，順化平和，氣候溫和，疾病較少，預後佳。"
        elif SHENG.get(ke_wx) == zhu_wx:
            return "小逆", "客生主，小逆之氣，氣候略有偏差，稍有病邪，不甚嚴重。"
        elif KE.get(ke_wx) == zhu_wx:
            return "不和", "客克主，不和之氣，氣候偏差，病邪較多，需注意調護。"
        elif KE.get(zhu_wx) == ke_wx:
            return "逆", "主克客，逆氣偏盛，氣候異常，疾病多發，治療較難。"
        else:
            return "一般", "客主加臨關係複雜，氣候變化不定，注意順應自然。"

    def _compute_tonghua(
        self, tg: str, dz: str, dayun: DaYunInfo,
        sitian: str, yinyang: str,
    ) -> TongHuaResult:
        """
        計算運氣同化（天符、歲會、太乙天符、同天符、同歲會）

        規則（《素問·六微旨大論》）：
        - 天符：大運五行 = 司天之氣五行
        - 歲會：大運五行 = 歲支五行
        - 太乙天符：天符 AND 歲會
        - 同天符：陽年，大運五行 = 司天五行（排除已算天符的）
        - 同歲會：陰年，大運五行 = 歲支五行
        """
        dayun_wx = dayun.wuxing
        sitian_wx = SITIAN_WUXING.get(sitian, "")
        dizhi_wx = DIZHI_WUXING.get(dz, "")

        is_tianfu = dayun_wx == sitian_wx
        is_suihui = dayun_wx == dizhi_wx
        is_taiyi = is_tianfu and is_suihui

        # 同天符：陽年且大運與司天同五行（同天符通常指非天符的陽年）
        is_tong_tianfu = (yinyang == "陽") and is_tianfu and not is_taiyi
        # 同歲會：陰年且大運與歲支同五行（同歲會通常指非歲會的陰年）
        is_tong_suihui = (yinyang == "陰") and is_suihui and not is_taiyi

        categories = []
        descs = []
        if is_taiyi:
            categories.append("太乙天符")
            descs.append(TONG_HUA_DESC["太乙天符"])
        elif is_tianfu:
            categories.append("天符")
            descs.append(TONG_HUA_DESC["天符"])
        elif is_suihui:
            categories.append("歲會")
            descs.append(TONG_HUA_DESC["歲會"])
        elif is_tong_tianfu:
            categories.append("同天符")
            descs.append(TONG_HUA_DESC["同天符"])
        elif is_tong_suihui:
            categories.append("同歲會")
            descs.append(TONG_HUA_DESC["同歲會"])
        else:
            categories.append("平氣之年")
            descs.append(TONG_HUA_DESC["平氣之年"])

        return TongHuaResult(
            is_tianfu=is_tianfu,
            is_suihui=is_suihui,
            is_taiyi_tianfu=is_taiyi,
            is_tong_tianfu=is_tong_tianfu,
            is_tong_suihui=is_tong_suihui,
            categories=categories,
            description="\n".join(descs),
        )

    def _compute_shengfu(self, dayun: DaYunInfo) -> ShengFuResult:
        """
        計算勝復（五行勝復規律）

        規則（《素問·氣交變大論》）：
        - 太過之年：本運太過，克我之氣受虧，我克之氣承乃制之，可發生勝氣
        - 不及之年：本運不及，克我之氣來勝，我生之氣起而復之
        """
        wx = dayun.wuxing
        shengfu = SHENGFU.get(wx, {})
        sheng_qi = shengfu.get("勝", "")
        fu_qi = shengfu.get("復", "")

        if dayun.is_tai:
            sheng_desc = f"{wx}運太過，氣有餘，則{sheng_qi}受克偏虧，{sheng_qi}之復氣應之。"
            fu_desc = f"若{sheng_qi}氣衰，則{fu_qi}起而復之，以制{wx}之太過。"
            has_sheng = True
        else:
            sheng_desc = f"{wx}運不及，{sheng_qi}氣來勝（克{wx}之氣偏盛），{wx}受邪。"
            fu_desc = f"勝氣偏盛，{fu_qi}起而復之，以制{sheng_qi}之勝。"
            has_sheng = True

        return ShengFuResult(
            has_sheng=has_sheng,
            sheng_qi=sheng_qi,
            fu_qi=fu_qi,
            sheng_desc=sheng_desc,
            fu_desc=fu_desc,
        )

    def _compute_current_position(
        self,
        yun_year: int,
        tg: str, dz: str,
        dayun: DaYunInfo,
        zhuyun_steps: List[ZhuYunStep],
        keyun_steps: List[KeYunStep],
        zhuqi_steps: List[ZhuQiStep],
        keqi_steps: List[KeQiStep],
        sitian: str, zaiquan: str,
        jialin_steps: List[KeZhuJiaLin],
        tonghua: TongHuaResult,
        shengfu: ShengFuResult,
    ) -> Optional[CurrentQiPosition]:
        """計算當前時刻的精細運氣位置"""
        days_elapsed = self._days_from_year_start(yun_year)

        # 若日期在運氣年起始之前，天數為負
        if days_elapsed < 0:
            return None

        # 找當前主運步
        zhuyun_idx = 4
        for i in range(5):
            if days_elapsed < ZHUYUN_BOUNDARIES_DAYS[i + 1]:
                zhuyun_idx = i
                break
        cur_zhuyun = zhuyun_steps[zhuyun_idx]
        days_in_zhuyun = days_elapsed - cur_zhuyun.start_day
        zhuyun_span = cur_zhuyun.end_day - cur_zhuyun.start_day
        zhuyun_pct = min(100.0, (days_in_zhuyun / zhuyun_span) * 100.0)

        # 當前客運步（與主運同步索引）
        cur_keyun = keyun_steps[zhuyun_idx]

        # 找當前主氣步
        zhuqi_idx = 5
        for i in range(6):
            if days_elapsed < ZHUQI_BOUNDARIES_DAYS[i + 1]:
                zhuqi_idx = i
                break
        cur_zhuqi = zhuqi_steps[zhuqi_idx]
        days_in_zhuqi = days_elapsed - cur_zhuqi.start_day
        zhuqi_span = cur_zhuqi.end_day - cur_zhuqi.start_day
        zhuqi_pct = min(100.0, (days_in_zhuqi / zhuqi_span) * 100.0)

        # 當前客氣步
        cur_keqi = keqi_steps[zhuqi_idx]

        # 當前客主加臨
        cur_jialin = jialin_steps[zhuqi_idx]

        return CurrentQiPosition(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            dayun=dayun,
            current_zhuyun=cur_zhuyun,
            current_zhuyun_index=zhuyun_idx,
            zhuyun_progress_pct=zhuyun_pct,
            days_in_zhuyun=days_in_zhuyun,
            current_keyun=cur_keyun,
            current_keyun_index=zhuyun_idx,
            current_zhuqi=cur_zhuqi,
            current_zhuqi_index=zhuqi_idx,
            zhuqi_progress_pct=zhuqi_pct,
            days_in_zhuqi=days_in_zhuqi,
            current_keqi=cur_keqi,
            current_keqi_index=zhuqi_idx,
            sitian=sitian,
            zaiquan=zaiquan,
            jialin=cur_jialin,
            tonghua=tonghua,
            shengfu=shengfu,
        )


# ============================================================
# 模組級便捷函數
# ============================================================

def compute_wuyunliuqi(
    year: int,
    month: int = 1,
    day: int = 20,
    hour: int = 0,
    minute: int = 0,
) -> WuYunLiuQiResult:
    """
    便捷函數：計算指定時刻的五運六氣

    參數：
        year   (int): 西曆年份
        month  (int): 月份（預設1）
        day    (int): 日（預設20，大寒近似）
        hour   (int): 時（預設0）
        minute (int): 分（預設0）

    回傳：
        WuYunLiuQiResult: 完整五運六氣計算結果

    範例：
        >>> result = compute_wuyunliuqi(2024, 6, 15, 10, 30)
        >>> print(result.ganzhi)
        '甲辰'
        >>> print(result.sitian)
        '太陽寒水'
    """
    calc = WuYunLiuQiCalculator(year, month, day, hour, minute)
    return calc.compute()


def compute_minute_series(
    start_year: int, start_month: int, start_day: int,
    end_year: int, end_month: int, end_day: int,
    step_minutes: int = 60,
) -> List[Dict[str, Any]]:
    """
    計算時間範圍內每N分鐘的運氣變化序列

    參數：
        start_year/month/day: 起始日期
        end_year/month/day: 結束日期
        step_minutes: 步長（分鐘）

    回傳：
        List[Dict]: 每個時間點的運氣簡要狀態
    """
    start_dt = datetime(start_year, start_month, start_day)
    end_dt = datetime(end_year, end_month, end_day)
    calc = WuYunLiuQiCalculator(start_year, start_month, start_day)
    return calc.compute_minute_series(start_dt, end_dt, step_minutes)
