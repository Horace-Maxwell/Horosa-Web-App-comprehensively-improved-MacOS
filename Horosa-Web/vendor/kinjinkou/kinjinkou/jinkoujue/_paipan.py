#!/usr/bin/python3
# -*- coding: utf-8 -*-
from kinjinkou.utils import Db, Db2Cdata


class Paipan:
    def __init__(self):
        # 初始数据
        self.wuxingName = '木 火 土 金 水'.split(' ')
        self.tianganName = '甲 乙 丙 丁 戊 己 庚 辛 壬 癸'.split(' ')
        self.dizhiName = '子 丑 寅 卯 辰 巳 午 未 申 酉 戌 亥'.split(' ')
        self.jiangshenName = '神后 大吉 功曹 太冲 天罡 太乙 胜光 小吉 传送 从魁 河魁 登明'.split(' ')
        self.guishenName = '贵人 腾蛇 朱雀 六合 勾陈 青龙 天空 白虎 太常 玄武 太阴 天后'.split(' ')
        self.guishendizhiName = '丑 巳 午 卯 辰 寅 戌 申 未 子 酉 亥'.split(' ')
        # 导入数据
        self.db = Db()
        self.db2cdata = Db2Cdata()
        self.Wuxing = self.db.get_tabledict_dict("[基础表-五行]")
        self.Tiangan = self.db.get_tabledict_dict("[基础表-十天干]")
        self.Dizhi = self.db.get_tabledict_dict("[基础表-十二地支]")
        self.Bagua = self.db.get_tabledict_dict("[基础表-八卦]")
        self.Liushisigua = self.db.get_tabledict_dict("[基础表-六十四卦]")
        self.Liushijiazi = self.db.get_tabledict_dict("[基础表-六十甲子]")

    def paipan(self, ganzhi, difen, yuejiang, zhanshi):
        # 时间信息
        self.Zhanshi = {'占时': {}, '月将': {}}
        # 盘
        self.Pan = {'1': {'地盘': '子'},
                    '2': {'地盘': '丑'},
                    '3': {'地盘': '寅'},
                    '4': {'地盘': '卯'},
                    '5': {'地盘': '辰'},
                    '6': {'地盘': '巳'},
                    '7': {'地盘': '午'},
                    '8': {'地盘': '未'},
                    '9': {'地盘': '申'},
                    '10': {'地盘': '酉'},
                    '11': {'地盘': '戌'},
                    '12': {'地盘': '亥'}}
        # 课
        self.Ke = {'人元': {'用神': '  '},
                   '贵神': {'用神': '  '},
                   '将神': {'用神': '  '},
                   '地分': {'用神': '  '}}
        # 如果没有输入月将，则使用干支的月支
        if yuejiang is None:
            yuejian = ganzhi['月柱'][1:2]
            yuejianIdx = self.dizhiName.index(yuejian)
            if 13 - yuejianIdx >= 12:
                yuejianIdx += 12
            yuejiang = self.dizhiName[13 - yuejianIdx]
        # 如果没有输入占时，则使用干支的时支
        if zhanshi is None:
            zhanshi = ganzhi['时柱'][1:2]
        # 起课
        Difen, Jiangshen, JiangshenName = self._qike_jiangshen(yuejiang, zhanshi, difen)
        Guishen, GuishenName = self._qike_guishen(ganzhi, zhanshi, Difen)
        Renyuan, Jianggan, Shengan = self._qike_renyuandungan(ganzhi, Difen, Jiangshen, Guishen)
        self.Zhanshi['占时']['干支'] = ganzhi['文本']
        self.Zhanshi['月将']['干支'] = yuejiang
        self.Zhanshi['四大空亡'] = self._qike_sidakongwang(ganzhi)
        self.Ke['人元']['干支'] = Renyuan
        self.Ke['贵神']['干支'] = Shengan + Guishen + '（' + GuishenName + '）'
        self.Ke['将神']['干支'] = Jianggan + Jiangshen + '（' + JiangshenName + '）'
        self.Ke['地分']['干支'] = Difen
        # 判断阴阳、五行、旺衰、用神
        self._qike_wuxing()
        self._qike_yinyang()
        self._qike_wangshuai()
        self._qike_yongshen()
        # 加入纳音
        self._qike_nayin()
        self.Res = {'占时': self.Zhanshi, '盘': self.Pan, '课': self.Ke}
        return self.Res, ganzhi

    def _qike_sidakongwang(self, ganzhi):
        rizhu = ganzhi['日柱']
        jiazi_idx = int(self.Liushijiazi[rizhu]['序号'])
        if 1 <= jiazi_idx <= 10 or 31 <= jiazi_idx <= 40:  # 甲子、甲午旬，纳音水空亡
            return '水'
        elif 21 <= jiazi_idx <= 30 or 51 <= jiazi_idx <= 60:  # 甲申、甲寅旬，纳音金空亡
            return '金'
        else:  # 甲戌、甲辰旬，纳音五行具足
            return '无'

    def _qike_jiangshen(self, yuejiang, zhanshi, difen):
        # 月将加时起天盘
        idx = self.dizhiName.index(yuejiang) - self.dizhiName.index(zhanshi)
        if idx < 0:
            idx += 12
        for i in self.Pan.keys():
            if int(i) - 1 + idx >= 12:
                idx -= 12
            self.Pan[i]['天盘'] = self.dizhiName[int(i) - 1 + idx]
            self.Pan[i]['将神'] = self.jiangshenName[int(i) - 1 + idx]
        # 数到地分求将神
        Difen = difen
        Jiangshen = self.Pan[str(self.dizhiName.index(Difen) + 1)]['天盘']
        JiangshenName = self.Pan[str(self.dizhiName.index(Difen) + 1)]['将神']
        return Difen, Jiangshen, JiangshenName

    def _qike_guishen(self, ganzhi, zhanshi, Difen):
        # 依照贵人歌诀取天盘贵人，即首位
        rigan = ganzhi['日柱'][0:1]
        guiren = None
        if rigan in ['甲', '戊', '庚']:
            if zhanshi in ['卯', '辰', '巳', '午', '未', '申']:  # 昼贵
                guiren = '丑'
            else:
                guiren = '未'
        if rigan in ['乙', '己']:
            if zhanshi in ['卯', '辰', '巳', '午', '未', '申']:
                guiren = '子'
            else:
                guiren = '申'
        if rigan in ['丙', '丁']:
            if zhanshi in ['卯', '辰', '巳', '午', '未', '申']:
                guiren = '亥'
            else:
                guiren = '酉'
        if rigan in ['壬', '癸']:
            if zhanshi in ['卯', '辰', '巳', '午', '未', '申']:
                guiren = '巳'
            else:
                guiren = '卯'
        if rigan in ['辛']:
            if zhanshi in ['卯', '辰', '巳', '午', '未', '申']:
                guiren = '午'
            else:
                guiren = '寅'
        idx = 0
        for i in self.Pan.keys():
            if self.Pan[i]['地盘'] == guiren:
                idx = int(i) - 1
        for i in self.Pan.keys():
            if (zhanshi in ['卯', '辰', '巳', '午', '未', '申'] and rigan not in ['壬', '癸', '辛']) \
                    or (zhanshi not in ['卯', '辰', '巳', '午', '未', '申'] and rigan in ['壬', '癸', '辛']):
                if idx + int(i) >= 13:
                    idx -= 12
                self.Pan[str(idx + int(i))]['神盘'] = self.guishendizhiName[int(i) - 1]  # 顺行
                self.Pan[str(idx + int(i))]['贵神'] = self.guishenName[int(i) - 1]
            else:
                if idx - int(i) + 2 <= 0:
                    idx += 12
                self.Pan[str(idx - int(i) + 2)]['神盘'] = self.guishendizhiName[int(i) - 1]  # 逆行
                self.Pan[str(idx - int(i) + 2)]['贵神'] = self.guishenName[int(i) - 1]
        Guishen = self.Pan[str(self.dizhiName.index(Difen) + 1)]['神盘']
        GuishenName = self.Pan[str(self.dizhiName.index(Difen) + 1)]['贵神']
        return Guishen, GuishenName

    def _qike_renyuandungan(self, ganzhi, Difen, Jiangshen, Guishen):
        rigan = ganzhi['日柱'][0:1]
        # 五子元遁
        if rigan in ['甲', '己']:
            shigan_index = 1  # 甲子
        elif rigan in ['乙', '庚']:
            shigan_index = 3  # 丙子
        elif rigan in ['丙', '辛']:
            shigan_index = 5  # 戊子
        elif rigan in ['丁', '壬']:
            shigan_index = 7  # 庚子
        elif rigan in ['戊', '癸']:
            shigan_index = 9  # 壬子
        else:
            shigan_index = 1
        idx1 = self.dizhiName.index(Difen) + shigan_index - 1
        if idx1 >= 10:
            idx1 -= 10
        idx2 = self.dizhiName.index(Jiangshen) + shigan_index - 1
        if idx2 >= 10:
            idx2 -= 10
        idx3 = self.dizhiName.index(Guishen) + shigan_index - 1
        if idx3 >= 10:
            idx3 -= 10
        Renyuan = self.tianganName[idx1]
        Jianggan = self.tianganName[idx2]
        Shengan = self.tianganName[idx3]
        return Renyuan, Jianggan, Shengan

    def _qike_wuxing(self):
        self.Ke['人元']['五行'] = self.Tiangan[self.Ke['人元']['干支']]['五行']
        self.Ke['贵神']['五行'] = self.Dizhi[self.Ke['贵神']['干支'][1:2]]['五行']
        self.Ke['将神']['五行'] = self.Dizhi[self.Ke['将神']['干支'][1:2]]['五行']
        self.Ke['地分']['五行'] = self.Dizhi[self.Ke['地分']['干支']]['五行']

    def _qike_yinyang(self):
        self.Ke['人元']['阴阳'] = self.Tiangan[self.Ke['人元']['干支']]['阴阳']
        self.Ke['贵神']['阴阳'] = self.Dizhi[self.Ke['贵神']['干支'][1:2]]['阴阳']
        self.Ke['将神']['阴阳'] = self.Dizhi[self.Ke['将神']['干支'][1:2]]['阴阳']
        self.Ke['地分']['阴阳'] = self.Dizhi[self.Ke['地分']['干支']]['阴阳']

    def _qike_wangshuai(self):
        # 生克情况：
        # 1.4种五行，必然有3克，必然有1个不受克，取不受克者为旺
        # 2.3种五行，则有某个五行出现2次（无影响），有1或2克，有1或2个不受克，若有2个不受克，则其中必有1个克他爻，取克他爻者为旺
        # 3.2种五行，有相生或相克两种情况，相克取克他爻者为旺，相生取受生者为旺；出现次数有1:3、2:2两种情况，若某一五行出现3次则取多者为旺
        # 4.1种五行，比和，无所谓旺衰
        #
        # 首先确定旺者，其余可依旺者推出。统计出现次数
        for i in self.Wuxing.keys():
            self.Wuxing[i]['次数'] = 0
        for i in self.Ke.keys():
            self.Wuxing[self.Ke[i]['五行']]['次数'] += 1
        wuxing = []
        for i in self.Wuxing.keys():
            if self.Wuxing[i]['次数'] > 0:
                wuxing.append(i)
        wang = None
        if len(wuxing) == 4:
            wuxing1 = wuxing.copy()
            # 不受克者为旺
            for i in wuxing1:
                if self.db2cdata.get_wuxing_shengke(i, return_type='克') in wuxing1:
                    wuxing1.remove(i)
            wang = wuxing1[0]
        if len(wuxing) == 3:
            wuxing1 = wuxing.copy()
            for i in wuxing1:
                if self.db2cdata.get_wuxing_shengke(i, return_type='克') in wuxing1:
                    wuxing1.remove(i)
            # 2个不受克者，克他爻者为旺
            if len(wuxing1) > 1:
                for i in wuxing1:
                    if self.db2cdata.get_wuxing_shengke(i, return_type='耗') in wuxing:
                        wang = i
            # 1个不受克者，不受克者为旺
            else:
                wang = wuxing1[0]
        if len(wuxing) == 2:
            wuxing1 = wuxing.copy()
            cishu_flag = 0
            shengke_flag = 0
            # 多者为旺
            for i in self.Wuxing.keys():
                if self.Wuxing[i]['次数'] >= 3:
                    cishu_flag += 1
                    shengke_flag += 1
                    wang = i
            if cishu_flag == 0:
                # 克他爻者为旺
                for i in wuxing1:
                    if self.db2cdata.get_wuxing_shengke(i, return_type='克') in wuxing1:
                        wuxing1.remove(i)
                        shengke_flag += 1
                wang = wuxing1[0]
            if shengke_flag == 0:
                # 受生者为旺
                for i in wuxing1:
                    if self.db2cdata.get_wuxing_shengke(i, return_type='生') in wuxing1:
                        wang = i
        if len(wuxing) == 1:
            wang = wuxing[0]
        # 求出旺相休囚死，并输出到课式
        xiang = self.db2cdata.get_wuxing_shengke(wang, return_type='泄')
        xiu = self.db2cdata.get_wuxing_shengke(wang, return_type='生')
        qiu = self.db2cdata.get_wuxing_shengke(wang, return_type='克')
        si = self.db2cdata.get_wuxing_shengke(wang, return_type='耗')
        for i in self.Ke.keys():
            if self.Ke[i]['五行'] == wang:
                self.Ke[i]['旺衰'] = '旺'
            if self.Ke[i]['五行'] == xiang:
                self.Ke[i]['旺衰'] = '相'
            if self.Ke[i]['五行'] == xiu:
                self.Ke[i]['旺衰'] = '休'
            if self.Ke[i]['五行'] == qiu:
                self.Ke[i]['旺衰'] = '囚'
            if self.Ke[i]['五行'] == si:
                self.Ke[i]['旺衰'] = '死'

    def _qike_yongshen(self):
        tongji = 0
        for i in self.Ke.keys():
            if self.Ke[i]['阴阳'] == '阳':
                tongji += 1
        if tongji == 0:  # 纯阴，以将为用
            self.Ke['将神']['用神'] = '用'
        if tongji == 1:  # 一阳，以阳为用
            for i in self.Ke.keys():
                if self.Ke[i]['阴阳'] == '阳':
                    self.Ke[i]['用神'] = '用'
        if tongji == 2:  # 二阳二阴，以将为用
            self.Ke['将神']['用神'] = '用'
        if tongji == 3:  # 一阴，以阴为用
            for i in self.Ke.keys():
                if self.Ke[i]['阴阳'] == '阴':
                    self.Ke[i]['用神'] = '用'
        if tongji == 4:  # 纯阳，以神为用
            self.Ke['贵神']['用神'] = '用'

    def _qike_nayin(self):
        self.Ke['贵神']['纳音'] = '纳音' + self.Liushijiazi[self.Ke['贵神']['干支'].split('（')[0]]['纳音五行']
        self.Ke['将神']['纳音'] = '纳音' + self.Liushijiazi[self.Ke['将神']['干支'].split('（')[0]]['纳音五行']

    def output(self):
        map_str = ''
        # 盘
        map_str += '地盘：'
        for i in self.Pan.keys():
            map_str += self.Pan[i]['地盘']
        map_str += '\n'
        map_str += '天盘：'
        for i in self.Pan.keys():
            map_str += self.Pan[i]['天盘']
        map_str += '\n'
        map_str += '神盘：'
        for i in self.Pan.keys():
            map_str += self.Pan[i]['神盘']
        map_str += '\n'
        # 课
        map_str += '月将：'
        map_str += str(self.Zhanshi['月将']['干支'])+'\n'
        map_str += str(self.Zhanshi['占时']['干支'])+' '
        map_str += '四大空亡：'
        map_str += str(self.Zhanshi['四大空亡'])+'\n'
        map_str += '人元：'
        map_str += str(self.Ke['人元']['干支'])
        map_str += str(self.Ke['人元']['用神'])+'\t\t'
        map_str += str(self.Ke['人元']['五行'])
        map_str += ('+' if self.Ke['人元']['阴阳'] == '阳' else '-')
        map_str += str(self.Ke['人元']['旺衰'])+'\n'
        map_str += '贵神：'
        map_str += str(self.Ke['贵神']['干支'])
        map_str += str(self.Ke['贵神']['用神'])+'\t'
        map_str += str(self.Ke['贵神']['五行'])
        map_str += ('+' if self.Ke['贵神']['阴阳'] == '阳' else '-')
        map_str += str(self.Ke['贵神']['旺衰'])
        map_str += ' '
        map_str += str(self.Ke['贵神']['纳音'])+'\n'
        map_str += '将神：'
        map_str += str(self.Ke['将神']['干支'])
        map_str += str(self.Ke['将神']['用神'])+'\t'
        map_str += str(self.Ke['将神']['五行'])
        map_str += ('+' if self.Ke['将神']['阴阳'] == '阳' else '-')
        map_str += str(self.Ke['将神']['旺衰'])
        map_str += ' '
        map_str += str(self.Ke['将神']['纳音'])+'\n'
        map_str += '地分：'
        map_str += str(self.Ke['地分']['干支'])
        map_str += str(self.Ke['地分']['用神'])+'\t\t'
        map_str += str(self.Ke['地分']['五行'])
        map_str += ('+' if self.Ke['地分']['阴阳'] == '阳' else '-')
        map_str += str(self.Ke['地分']['旺衰'])+'\n'
        return map_str

#print(gangzhi1(2024, 12, 31, 18, 20))