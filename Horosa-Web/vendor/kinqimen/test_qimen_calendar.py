# -*- coding: utf-8 -*-
"""
奇門曆法回歸測試 (v2.1.6)：月柱交節邊界 + 三元超神接氣置閏。

對應修復：
  - Windows #4 示例一 / 上游 #53,#9：月柱以精確交節時刻判定(非日級)。
  - Windows #4 示例二 / 上游 #62：置閏定局採超神接氣後之節氣(節氣標籤與局數一致)。
  - 上游 #43：置閏法與拆補法在超神日應給出不同局。

執行：python3 test_qimen_calendar.py
"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import jieqi
import kinqimen


class MonthPillarBoundary(unittest.TestCase):
    """月柱應依精確交節時刻換月(交節當日、交節前仍屬前一節)。"""

    def mtg(self, y, mo, d, h, mi):
        return config.gangzhi(y, mo, d, h, mi)[1]

    def ytg(self, y, mo, d, h, mi):
        return config.gangzhi(y, mo, d, h, mi)[0]

    def test_lixia_2005_before_crossing(self):
        # 立夏 2005-05-05 17:52；16:30 在交節前 → 庚辰(非辛巳)。Windows #4 示例一 / 上游 #53
        self.assertEqual(self.mtg(2005, 5, 5, 16, 30), '庚辰')

    def test_lixia_2005_after_crossing(self):
        # 交節後 → 辛巳(不可回歸)
        self.assertEqual(self.mtg(2005, 5, 5, 18, 0), '辛巳')

    def test_lixia_2021_before_crossing(self):
        # 立夏 2021-05-05 ~14:47；14:00 在交節前 → 壬辰。上游 #9
        self.assertEqual(self.mtg(2021, 5, 5, 14, 0), '壬辰')

    def test_non_jieqi_day_unchanged(self):
        self.assertEqual(self.mtg(2005, 5, 6, 10, 0), '辛巳')   # 巳月內
        self.assertEqual(self.mtg(2005, 4, 20, 10, 0), '庚辰')  # 辰月內

    def test_lichun_rolls_year_and_month(self):
        # 立春 2005-02-04 01:43：之前屬甲申年丁丑月,之後乙酉年戊寅月
        self.assertEqual((self.ytg(2005, 2, 4, 0, 0), self.mtg(2005, 2, 4, 0, 0)), ('甲申', '丁丑'))
        self.assertEqual((self.ytg(2005, 2, 4, 23, 0), self.mtg(2005, 2, 4, 23, 0)), ('乙酉', '戊寅'))


class ThreeYuanZhirun(unittest.TestCase):
    """三元超神接氣置閏：置閏定局採超神後之節氣;拆補採曆法節氣。"""

    def test_issue62_zhirun_lidong(self):
        # 2027-10-31 20:49：置閏應為立冬上元六局(超神),非霜降。上游 #62 / Windows #4 示例二
        self.assertEqual(config.qimen_ju_name_zhirun(2027, 10, 31, 20, 49), '陰遁六局上元')
        self.assertEqual(config.dingju_jieqi(2027, 10, 31, 20, 49, 2), '立冬')

    def test_issue62_chaibu_shuangjiang(self):
        # 拆補採曆法節氣 → 霜降上元五局(不變)
        self.assertEqual(config.qimen_ju_name_chaibu(2027, 10, 31, 20, 49), '陰遁五局上')
        self.assertEqual(config.dingju_jieqi(2027, 10, 31, 20, 49, 1), '霜降')

    def test_issue43_methods_differ(self):
        # 2004-09-01 12:00：拆補=處暑上元一局；置閏=白露上元九局(超神)。上游 #43
        self.assertEqual(config.qimen_ju_name_chaibu(2004, 9, 1, 12, 0), '陰遁一局上')
        self.assertEqual(config.qimen_ju_name_zhirun(2004, 9, 1, 12, 0), '陰遁九局上元')
        self.assertEqual(config.dingju_jieqi(2004, 9, 1, 12, 0, 2), '白露')

    def test_zhirun_leap_repeats_daxue(self):
        # 2027 冬至超神≥9天 → 置閏重複大雪;2027-12-15 落於閏大雪上元(四局)
        self.assertEqual(config.qimen_ju_name_zhirun(2027, 12, 15, 10, 0), '陰遁四局上元')
        self.assertEqual(config.dingju_jieqi(2027, 12, 15, 10, 0, 2), '大雪')


class FullPanSmoke(unittest.TestCase):
    """整盤端到端：長區間內不崩、節氣有效、天盤/地盤等齊全。"""

    VALID_JIEQI = set('冬至 小寒 大寒 立春 雨水 驚蟄 春分 清明 穀雨 立夏 小滿 芒種 '
                      '夏至 小暑 大暑 立秋 處暑 白露 秋分 寒露 霜降 立冬 小雪 大雪'.split())

    def test_zhirun_jieqi_valid_over_range(self):
        import datetime
        cur, end = datetime.date(2018, 1, 1), datetime.date(2030, 12, 31)
        while cur <= end:
            j = jieqi.zhirun_jieqi(cur.year, cur.month, cur.day, 12, 0)
            self.assertIn(j, self.VALID_JIEQI, msg=f"{cur} 置閏節氣無效: {j}")
            cur += datetime.timedelta(days=3)

    def test_pan_no_crash_both_methods(self):
        for (y, mo, d, h, mi) in [(2027, 10, 31, 20, 49), (2005, 5, 5, 16, 30),
                                  (2004, 9, 1, 12, 0), (2024, 11, 11, 21, 54),
                                  (2021, 2, 16, 2, 33), (2027, 12, 15, 10, 0)]:
            for opt in (1, 2):
                r = kinqimen.Qimen(y, mo, d, h, mi).pan(opt)
                for k in ('干支', '排局', '節氣', '天盤', '地盤', '門', '星', '神'):
                    self.assertIn(k, r)
                self.assertIn(r['節氣'], self.VALID_JIEQI)


if __name__ == '__main__':
    unittest.main(verbosity=2)
