#!/usr/bin/python3
# -*- coding: utf-8 -*-
from ._db import Db


class Db2Cdata:
    def __init__(self):
        self.db = Db()
        self.Wuxing = self.db.get_tabledict_dict("[基础表-五行]")

    def get_wuxing_shengke(self, input_x, input_y=None, return_type='耗'):
        # 输入五行，返回对输入五行起对应作用的五行（返回类型通过return_type指定）；或者输入两个五行，返回后一个对前一个的作用关系
        # 生：生我、印枭、父母；助：同我、比劫、兄弟；克：克我、官杀、官鬼；泄：我生、食伤、子女；耗：我克、财星、妻财
        Wuxing = self.Wuxing.copy()
        # 获取输入五行的序号（1-5）
        wuxingIdx = int(Wuxing[input_x]['序号'])
        # 根据输入五行序号计算生助克泄耗的五行序号
        haoIdx = wuxingIdx + 2
        if haoIdx > 5:
            haoIdx -= 5
        keIdx = wuxingIdx - 2
        if keIdx < 1:
            keIdx += 5
        shengIdx = wuxingIdx - 1
        if shengIdx < 1:
            shengIdx += 5
        zhuIdx = wuxingIdx
        xieIdx = wuxingIdx + 1
        if xieIdx > 5:
            xieIdx -= 5
        # 五行生克
        for i in Wuxing.values():
            if int(i['序号']) == haoIdx:
                i['生克'] = '耗'
            if int(i['序号']) == keIdx:
                i['生克'] = '克'
            if int(i['序号']) == shengIdx:
                i['生克'] = '生'
            if int(i['序号']) == zhuIdx:
                i['生克'] = '助'
            if int(i['序号']) == xieIdx:
                i['生克'] = '泄'
        if input_y == None:
            for i in Wuxing.values():
                if i['生克'] == return_type:
                    return i['五行']
        else:
            return Wuxing[input_y]['生克']
