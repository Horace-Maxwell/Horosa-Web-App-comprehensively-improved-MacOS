#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《家傳秘法手稿 · 南極神數》 Python 實現
按照手稿邏輯完整建構

本代碼嚴格遵循手稿章節與公式：
- 第一章：天干地支、陰陽五行
- 第二章：四柱排法（年月日時、大運）
- 第三章：二十八星宿、五星、建除十二辰、神數測算點竅
- 第四章：十八星圖秘解、密碼、條文查詢

注意：
1. 完整十八幅星盤秘圖與全部條文需對照原書圖像（手稿僅公開部分密碼與示例）。
2. 日柱精確計算需萬年曆或天文曆法（本代碼提供公式框架，可擴展 astropy 計算太陽黃經求節氣）。
3. 五星精確宮位需天文計算（手稿強調右行72日一宮，結合28宿）。
4. 手稿核心精神：「圖為體，條文為用」「重在自悟」「研讀《果老星宗》」。

作者依手稿公開內容整理，供易學同仁參研。
"""

from typing import Dict, List, Tuple, Optional
import math

# ============================================================
# 第一章 數術基本知識
# ============================================================

TIANGAN: List[str] = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DIZHI: List[str] = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 天干陰陽五行（手稿明確：甲丙戊庚壬屬陽，乙丁己辛癸屬陰）
YINYANG_GAN: Dict[str, str] = {g: '阳' if i % 2 == 0 else '阴' for i, g in enumerate(TIANGAN)}
WUXING_GAN: Dict[str, str] = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土',
    '庚': '金', '辛': '金', '壬': '水', '癸': '水'
}

# 地支陰陽五行
YINYANG_ZHI: Dict[str, str] = {z: '阳' if i % 2 == 0 else '阴' for i, z in enumerate(DIZHI)}
WUXING_ZHI: Dict[str, str] = {
    '寅': '木', '卯': '木', '巳': '火', '午': '火',
    '申': '金', '酉': '金', '亥': '水', '子': '水',
    '辰': '土', '戌': '土', '丑': '土', '未': '土'
}

# 方位（手稿）
DIRECTION_GAN: Dict[str, str] = {'甲': '东', '乙': '东', '丙': '南', '丁': '南',
                                 '戊': '中', '己': '中', '庚': '西', '辛': '西',
                                 '壬': '北', '癸': '北'}
DIRECTION_ZHI: Dict[str, str] = {
    '寅': '东', '卯': '东', '辰': '中',
    '巳': '南', '午': '南', '未': '中',
    '申': '西', '酉': '西', '戌': '中',
    '亥': '北', '子': '北', '丑': '中'
}

# 五行生克（手稿根本）
SHENG_CYCLE = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
KE_CYCLE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}

def get_wuxing_relation(w1: str, w2: str) -> str:
    """五行生克制化"""
    if SHENG_CYCLE.get(w1) == w2:
        return f"{w1}生{w2}"
    if KE_CYCLE.get(w1) == w2:
        return f"{w1}克{w2}"
    if SHENG_CYCLE.get(w2) == w1:
        return f"{w2}被{w1}生"
    if KE_CYCLE.get(w2) == w1:
        return f"{w2}被{w1}克"
    return "同類"

# ============================================================
# 二十八星宿（手稿第三章）
# ============================================================
XIU28: Dict[str, List[str]] = {
    '東方蒼龍': ['角', '亢', '氏', '房', '心', '尾', '箕'],
    '北方玄武': ['斗', '牛', '女', '虚', '危', '室', '壁'],
    '西方白虎': ['奎', '娄', '胃', '昴', '毕', '觜', '参'],
    '南方朱雀': ['井', '鬼', '柳', '星', '张', '翼', '轸']
}

def get_xiu_group(xiu: str) -> str:
    for group, xius in XIU28.items():
        if xiu in xius:
            return group
    return "未知"

# ============================================================
# 建除十二辰（手稿第三章，兩種用法皆存）
# ============================================================
JIANCHU: List[str] = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']

def get_jianchu_huainan(zhi: str) -> str:
    """《淮南子》法：寅建、卯除、辰满、巳平、午定、未执、申破、酉危、戌成、亥收、子开、丑闭"""
    start = DIZHI.index('寅')
    idx = DIZHI.index(zhi)
    offset = (idx - start) % 12
    return JIANCHU[offset]

def get_jianchu_from_month_build(month_zhi: str, day_offset: int = 0) -> str:
    """協紀法：月建為建，順行十二辰（手稿註「每月交節則叠兩值日」）"""
    start = DIZHI.index(month_zhi)
    return JIANCHU[(start + day_offset) % 12]

# ============================================================
# 第二章 四柱篇
# ============================================================

def calculate_year_pillar(lunar_year: int, after_lichun: bool = True) -> str:
    """
    手稿年柱排法：
    - 立春後出生用本年干支
    - 立春前出生用上一年干支
    參考系：1984年為甲子（常用）
    """
    if not after_lichun:
        lunar_year -= 1
    idx = (lunar_year - 1984) % 60
    return TIANGAN[idx % 10] + DIZHI[idx % 12]

def calculate_month_pillar(year_gan: str, solar_month: int) -> str:
    """
    手稿月柱排法：
    1. 五虎遁起月訣（完全照錄）
    2. 月支固定對應節氣月：正月寅、二月卯...十二月丑
    注意：南極數「以節為月份界限，不用十二氣」
    """
    starters = {
        '甲': '丙', '己': '丙',
        '乙': '戊', '庚': '戊',
        '丙': '庚', '辛': '庚',
        '丁': '壬', '壬': '壬',
        '戊': '甲', '癸': '甲'
    }
    start_gan = starters.get(year_gan, '丙')
    gan_idx = (TIANGAN.index(start_gan) + solar_month - 1) % 10
    month_gan = TIANGAN[gan_idx]

    # 節氣月支對應（手稿列表）
    zhi_map = {1: '寅', 2: '卯', 3: '辰', 4: '巳', 5: '午', 6: '未',
               7: '申', 8: '酉', 9: '戌', 10: '亥', 11: '子', 12: '丑'}
    month_zhi = zhi_map.get(solar_month, '寅')
    return month_gan + month_zhi

def calculate_hour_pillar(day_gan: str, hour_zhi: str) -> str:
    """
    手稿時柱排法（完全照錄訣）：
    甲己還加甲，乙庚丙作初，丙年從戊起，丁壬庚子居，戊癸何方發，壬子是真途。
    """
    starters = {
        '甲': '甲', '己': '甲',
        '乙': '丙', '庚': '丙',
        '丙': '戊', '辛': '戊',
        '丁': '庚', '壬': '庚',
        '戊': '壬', '癸': '壬'
    }
    start_gan = starters.get(day_gan, '甲')
    zhi_idx = DIZHI.index(hour_zhi)
    gan_idx = (TIANGAN.index(start_gan) + zhi_idx) % 10
    return TIANGAN[gan_idx] + hour_zhi

def calculate_da_yun(month_pillar: str, gender: str, year_yinyang: str, steps: int = 8) -> List[str]:
    """
    手稿大運排法：
    陽年生男、陰年生女 → 順排（從月柱後一干支起）
    陰年生男、陽年生女 → 逆排
    每運十年，干管前五年，支管後五年
    """
    forward = (year_yinyang == '阳' and gender == '男') or (year_yinyang == '阴' and gender == '女')
    gan, zhi = month_pillar[0], month_pillar[1]
    gan_idx = TIANGAN.index(gan)
    zhi_idx = DIZHI.index(zhi)
    step = 1 if forward else -1
    dayun = []
    for i in range(1, steps + 1):
        g = TIANGAN[(gan_idx + i * step) % 10]
        z = DIZHI[(zhi_idx + i * step) % 12]
        dayun.append(g + z)
    return dayun

# ============================================================
# 第三章 神數門徑
# ============================================================

# 五星出沒規律（手稿）
FIVE_STAR_DAYS: Dict[str, List[int]] = {
    '水': [1, 6, 11, 16, 21, 26],
    '木': [3, 8],
    '火': [2, 7],
    '土': [5, 10],
    '金': [4, 9]
}

def five_star_appear(star: str, day: int) -> bool:
    return day in FIVE_STAR_DAYS.get(star, [])

# ============================================================
# 第四章 星圖秘解 + 密碼 + 條文
# ============================================================

# 手稿公開密碼（完全照錄）
PASSWORDS: Dict[str, str] = {
    '海异山同': '同父异母，东方南方为大运',
    '山异海同': '同母异父，上捶下贯为恶运，址支运为地支运',
    '将脫這際': '大運不吉，還有幾年可脫災',
    '除柳': '破相過遷',
    '蕉局': '流年月限不吉',
    '財勝局': '流年財運',
    '原比': '夫妻屬相相同',
    '花牌同乾': '坤造之兄弟人數並且同父異母',
    '跳重': '克夫',
    '重肘': '克妻',
    '則要荊茨': '出生時刻，妻子及其五行',
    '天地局': '出生時辰及父母之年命五行',
    '陰盛': '妻比夫大',
}

# 手稿示例條文（完全照錄）
SAMPLE_VERSES: Dict[str, str] = {
    '子部滿斗一度': '傷官架煞不貞。命中注定有刑伤，结发夫主属兔象，定然先死梦黄粱。',
    '寅部成斗一度': '五行八字命生成，姐妹行中是七人，同父不同母亲生。',
    '戌宫分成斗子一度七分': '子部第一个成斗 → 兄弟七人，同父异母。',
    '子宫分除壁寅二度小': '寅部第二个除壁 → 兄弟二人，本人居小。（天干数乙为2，丙为1，辛为3）',
    '亥宫分正月十八亥二度': '亥部第二个闭轸 → 命主亡于正月十八，并生于亥时。',
}

def lookup_password(code: str) -> str:
    return PASSWORDS.get(code, '此密碼手稿未公開，需自行參悟十八星圖。')

def lookup_verse(key: str) -> str:
    return SAMPLE_VERSES.get(key, '此條文手稿未公開，需查對應星圖原圖。')

# 星圖解讀函數（依手稿描述實現邏輯）
def interpret_chart_1(palace: str, xiu: str, degree: float) -> str:
    """
    圖一秘解（手稿）：
    從午至亥為建張全日表，定命主出生月日。
    午宫分辰一度一分 → 辰部第一輪第一個建張 = 正月初一
    午宫分辰二度二分 → 辰部第二輪第一個 = 正月初二
    """
    round_num = math.floor(degree)
    return (f"圖一：{palace}宫分{xiu}{degree}度 → "
            f"{xiu}部第{round_num}輪建張（建張全日表定位出生日期）。"
            " 宫分亦可查大運支運。")

def interpret_chart_6(palace: str, degree: float) -> str:
    """
    圖六秘解（手稿）：
    午至亥為閉軫（命主死亡月份）
    了至巳為成牛（兄弟人數、中途夭折幾人）
    """
    if palace in ['午', '未', '申', '酉', '戌', '亥']:
        return f"圖六：{palace}宫分{degree}度 → 閉軫局，查命主亡月條文。"
    else:
        return f"圖六：{palace}宫分{degree}度 → 成牛局，兄弟人數及夭折數查條文。"

def interpret_general(chart_num: int, palace: str, jianchu: str, xiu: str, degree: float,
                      extra_code: str = "") -> str:
    """
    綜合星圖解讀（手稿第四章總論）
    結合密碼與條文，圖不破則數難起。
    """
    key = f"{palace}宫分{jianchu}{xiu}{degree}"
    verse = lookup_verse(key)
    if verse != '此條文手稿未公開，需查對應星圖原圖。':
        return verse

    pwd = ""
    if extra_code:
        pwd = lookup_password(extra_code)
    return (f"星圖{chart_num} {palace}宫 {jianchu}{xiu}{degree}度。\n"
            f"密碼解：{pwd or '請對照手稿圖中密碼位置自行破譯。'}\n"
            "手稿提示：圖為體，條文為用。研讀《果老星宗》可深入。")

# ============================================================
# 南極神數核心類
# ============================================================

class NanJiShenShu:
    """南極神數命理推演主類"""

    def __init__(self, lunar_year: int, solar_month: int, day: int,
                 hour_zhi: str, gender: str = '男', after_lichun: bool = True):
        self.lunar_year = lunar_year
        self.solar_month = solar_month
        self.day = day
        self.hour_zhi = hour_zhi
        self.gender = gender
        self.after_lichun = after_lichun

        # 計算四柱
        self.year_pillar = calculate_year_pillar(lunar_year, after_lichun)
        self.year_gan = self.year_pillar[0]
        self.year_zhi = self.year_pillar[1]
        self.year_yinyang = YINYANG_GAN[self.year_gan]

        self.month_pillar = calculate_month_pillar(self.year_gan, solar_month)
        self.month_gan = self.month_pillar[0]
        self.month_zhi = self.month_pillar[1]

        self.day_gan: Optional[str] = None
        self.hour_pillar: Optional[str] = None
        self.da_yun: List[str] = calculate_da_yun(
            self.month_pillar, gender, self.year_yinyang
        )

    def set_day_pillar(self, day_gan: str):
        """日柱需萬年曆精確查詢，此處手動設定"""
        self.day_gan = day_gan

    def set_hour_pillar(self, hour_zhi: Optional[str] = None):
        if hour_zhi:
            self.hour_zhi = hour_zhi
        if self.day_gan:
            self.hour_pillar = calculate_hour_pillar(self.day_gan, self.hour_zhi)

    def get_four_pillars(self) -> str:
        day_str = self.day_gan + '日' if self.day_gan else '日柱(待查萬年曆)'
        hour_str = self.hour_pillar if self.hour_pillar else '時柱(待設定)'
        return f"{self.year_pillar} {self.month_pillar} {day_str} {hour_str}"

    def get_da_yun(self) -> str:
        return ' '.join(self.da_yun)

    def divine(self, chart: int = 1, palace: str = '子', jianchu: str = '建',
               xiu: str = '角', degree: float = 1.0, extra_code: str = "") -> str:
        """依手稿星圖邏輯綜合推演"""
        if chart == 1:
            return interpret_chart_1(palace, xiu, degree)
        elif chart == 6:
            return interpret_chart_6(palace, degree)
        else:
            return interpret_general(chart, palace, jianchu, xiu, degree, extra_code)

    def print_full_report(self):
        print("=" * 60)
        print("南極神數 命理報告（依手稿邏輯）")
        print("=" * 60)
        print(f"四柱八字：{self.get_four_pillars()}")
        print(f"性別：{self.gender}　　年干陰陽：{self.year_yinyang}")
        print(f"大運序列：{self.get_da_yun()}")
        print("-" * 40)
        print("【手稿命例演示】乾造丙午 庚寅 丙申 辛卯")
        print("大運：辛卯 壬辰 癸巳 甲午 乙未（陽年男順排）")
        print("① 查圖一酉宮分一度七 → 西部第一輪建張定位於西")
        print(self.divine(chart=1, palace='酉', xiu='觜', degree=1.7))
        print("② 火星定於子，開觜於子宮分三度一 → 弟兄無靠是一人")
        print(lookup_verse('子部滿斗一度'))
        print("③ 火星移位戌宮分卯三度二，查條文（手稿略）")
        print("④ 幼運水星移位丑局寅酉二度，查條文（手稿略）")
        print("⑤ 時辰過午宮得危氏")
        print("-" * 40)
        print("手稿核心：圖為體，條文為用。十八星圖為钥卷，破圖則數起。")
        print("密碼示例：跳重 →", lookup_password('跳重'))
        print("陰盛 →", lookup_password('陰盛'))
        print("=" * 60)
        print("提示：完整功能需補充原書十八星圖數據與全部條文。")
        print("建議結合 astropy 計算五星黃經與28宿宮位，以實現精確演數。")

# ============================================================
# 主程式演示
# ============================================================

if __name__ == "__main__":
    print("《南極神數》Python實現 v1.0")
    print("嚴格按照家傳秘法手稿邏輯編寫")
    print()

    # 手稿示例命造：一九九〇年四月初二辰時 → 庚午 庚辰 辛酉 壬辰
    # 注意：月柱手稿為庚辰，此處 solar_month=4 計算結果為演示，實際以手稿為準
    njs = NanJiShenShu(lunar_year=1990, solar_month=4, day=2,
                       hour_zhi='辰', gender='男', after_lichun=True)
    njs.set_day_pillar('辛')      # 手稿日柱辛酉
    njs.set_hour_pillar('辰')     # 手稿時柱壬辰（此處簡化示範，實際小時干計算正確）

    njs.print_full_report()

    print("\n自訂命造示例（2026年3月15日午時 女命）：")
    njs2 = NanJiShenShu(2026, 3, 15, '午', '女')
    njs2.set_day_pillar('甲')
    njs2.set_hour_pillar()
    print(njs2.get_four_pillars())
    print("大運：", njs2.get_da_yun())
    print("星圖1查詢示例：", njs2.divine(1, '午', '建', '角', 2.5))

    print("\n【手稿精神】")
    print("「圖不破則數難起」")
    print("「給人以黃金不如給人點金之術」")
    print("「神數為天機，不能輕泄」")
    print("請研讀原書圖像與《果老星宗》，結合實踐自悟。")
    print("本代碼僅為入門引路，完整神數仍需手稿原圖與長期實證。")