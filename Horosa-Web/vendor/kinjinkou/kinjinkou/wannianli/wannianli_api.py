#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import datetime
from ._realsolar import RealSolar
from ._calendar import Calendar

"""
1.时间换算类
2.历法类（公历、农历、数术流运、四柱）
3.对外接口、可变输出API类
"""


class WannianliApi:
    def __init__(self):
        pass

    # 获取指定时间指定经度的真太阳时
    def get_Realsolar(self, zhidingshijian=None, jingdu=120, zhidinggeshi=None):
        r = RealSolar()
        zhentaiyangshi_obj = r.zhentaiyangshi(zhidingshijian=zhidingshijian, jingdu=jingdu, zhidinggeshi=zhidinggeshi)
        return zhentaiyangshi_obj

    # 获取指定时间的河洛时间
    def get_Heluoshijian(self, zhidingshijian=None, zhidinggeshi=None):
        r = RealSolar()
        heluoshijian_obj = r.heluoshijian(zhidingshijian=zhidingshijian, zhidinggeshi=zhidinggeshi)
        return heluoshijian_obj

    # 获取当前北京时间
    def get_BeijingshijianNow(self, zhidinggeshi=None):
        r = RealSolar()
        beijingshijian_now_obj = r.beijingshijian_now(zhidinggeshi=zhidinggeshi)
        return beijingshijian_now_obj

    # 获取完整时间历法信息，阳历、阴历、节气、干支必选，其余可选
    def get_Calendar(self, datetime_obj, return_fengshui=False, return_zhongyi=False, return_huangji=False, return_type='origin'):
        w = Calendar()
        solar_obj = w.Solar().solar(datetime_obj)
        lunar_obj = w.Lunar().lunar(datetime_obj)
        solarTerm_obj = w.SolarTerm().solarTerm(datetime_obj)
        ganzhi_obj = w.Ganzhilifa().ganzhi(datetime_obj, solarTerm_obj, wuzhu='')
        if return_fengshui:
            fengshui_obj = w.Fengshuilifa().fengshui(datetime_obj,lunar_obj,solarTerm_obj,ganzhi_obj)
        else:
            fengshui_obj = {'类别': '风水', '文本': ''}
        if return_zhongyi:
            zhongyi_obj = w.Zhongyilifa().zhongyi(solarTerm_obj,ganzhi_obj)
        else:
            zhongyi_obj = {'类别': '中医', '文本': ''}
        if return_huangji:
            huangji_obj = w.Huangjilifa().huangjijingshi(datetime_obj,solarTerm_obj)
        else:
            huangji_obj = {'类别': '皇极', '文本': ''}
        if return_type == 'str':
            return solar_obj['文本']+'\n'+lunar_obj['文本']+'\n'+solarTerm_obj['文本']+'\n'+ganzhi_obj['文本']+'\n'+fengshui_obj['文本']+'\n'+zhongyi_obj['文本']+'\n'+huangji_obj['文本']
        elif return_type == 'json':
            solarTerm_obj['交节气日'] = solarTerm_obj['交节气日'].strftime('%Y/%m/%d')
            return [solar_obj, lunar_obj, solarTerm_obj, ganzhi_obj, fengshui_obj, zhongyi_obj, huangji_obj]
        elif return_type == 'origin':
            return [solar_obj,lunar_obj,solarTerm_obj,ganzhi_obj,fengshui_obj,zhongyi_obj,huangji_obj]

    # 获取当前节与下一节信息，八字用到
    def get_SolarTermJie(self, datetime_obj):
        w = Calendar()
        solarTermJie_obj = w.SolarTerm().solarTermJie(datetime_obj)
        return solarTermJie_obj

    # 获取本年所有的交节气日
    def get_SolarTermDays(self, datetime_obj):
        w = Calendar()
        solarTermDays_obj = w.SolarTerm().solarTermDays(datetime_obj)
        return solarTermDays_obj

    # 由农历反推得到阳历
    def get_OneDay_lunar2Solar(self, lunar_obj):
        pass

    # 获取所有阳历年份的年干支
    def get_GanzhiYears(self, start_year=1900, end_year=2100):
        if start_year<1900 or end_year>2100:
            print('错误的输入')
            return None
        # 输入：起止年份
        # 输出：对应年份和年干支
        res = []
        ganzhi = Calendar.Ganzhilifa()
        solarterm = Calendar.SolarTerm()
        for y in range(start_year, end_year + 1):
            dt = datetime.datetime(y,5,1)  # 以每年的5月1日定年干支
            solarterm_obj = solarterm.solarTerm(dt)
            ganzhi_year = ganzhi.ganzhi(dt,solarterm_obj,wuzhu='')['年柱']
            res.append([y,ganzhi_year])
        return res

    # 获取指定阳历年的月干支
    def get_GanzhiOneYear(self, year=2018):
        if year<1900 or year>2100:
            print('错误的输入')
            return None
        res = []
        ganzhi = Calendar.Ganzhilifa()
        solarterm = Calendar.SolarTerm()
        solartermdays = solarterm.solarTermDays(datetime.datetime(year,5,1))['交节气日']  # 先获取本年的所有交节气日
        for m in range(0, 12):
            dt = datetime.datetime(year, m+1, int(solartermdays[2*m]))  # 交节换月，取上半月的交节气日
            solarterm_obj = solarterm.solarTerm(dt)
            ganzhi_obj = ganzhi.ganzhi(dt, solarterm_obj, wuzhu='')
            res.append([m+1, ganzhi_obj['月柱']])
        return res

    # 获取指定阳历月的日干支
    def get_GanzhiOneMonth(self, year=2018, month=1):
        if year<1900 or year>2100 or month<1 or month>12:
            print('错误的输入')
            return None
        res = []
        ganzhi = Calendar.Ganzhilifa()
        solarterm = Calendar.SolarTerm()
        if month == 12:
            end_day = datetime.datetime(year=year+1, month=1, day=1) - datetime.timedelta(days=1)
        else:
            end_day = datetime.datetime(year=year,month=month+1,day=1)-datetime.timedelta(days=1)
        dt = datetime.datetime(year=year,month=month,day=1)
        dayIdx = 1
        while dt <= end_day:
            solarterm_obj = solarterm.solarTerm(dt)
            ganzhi_obj = ganzhi.ganzhi(dt, solarterm_obj, wuzhu='')
            res.append([dayIdx, ganzhi_obj['日柱']])
            dayIdx += 1
            dt += datetime.timedelta(days=1)
        return res

    # 获取指定阳历日的时干支
    def get_GanzhiOneDay(self, datetime_obj):
        res = []
        ganzhi = Calendar.Ganzhilifa()
        solarterm = Calendar.SolarTerm()
        year = datetime_obj.year
        month = datetime_obj.month
        day = datetime_obj.day
        for h in range(0, 12):
            dt = datetime.datetime(year,month,day,2*h)
            solarterm_obj = solarterm.solarTerm(dt)
            ganzhi_obj = ganzhi.ganzhi(dt, solarterm_obj, wuzhu='')
            res.append([2*h, ganzhi_obj['时柱']])
        return res
