#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import datetime

"""
    datetime说明：
        模块内容：
        1.datetime.date：表示日期的类
        2.datetime.datetime：表示日期时间的类
        3.datetime.time：表示时间的类
        4.datetime.timedelta：表示时间间隔，即两个时间点的间隔
        5.datetime.tzinfo：时区的相关信息

        建立对象：
        now = datetime.datetime.today()/datetime.datetime.now()
            ——取当前日期时间；today()包含全部日期时间信息，now()只包含时间信息
        dt = datetime.datetime(year, month, day, hour, minute, second)
            ——建立基于输入的日期时间的对象

        取日期时间：
        dt.year/now.month/now.day/now.hour/now.minute/now.second
            ——取年月日时分秒
        dt.weekday()
            ——返回星期几，星期一起0

        日期时间格式化：
        dt.strftime('%Y-%m-%d %H:%M:%S')
            ——日期时间转格式化字符串
        dt.strptime(str, '%Y-%m-%d %H:%M:%S')
            ——格式化字符串转日期时间
        %y 两位数的年份表示（00-99）
        %Y 四位数的年份表示（000-9999）
        %m 月份（01-12）
        %d 月内中的一天（0-31）
        %H 24小时制小时数（0-23）
        %M 分钟数（00=59）
        %S 秒（00-59）
        %j 年内的一天（001-366）
        %U 一年中的星期数（00-53）星期天为星期的开始
        %w 星期（0-6），星期天为星期的开始

        日期时间的计算：
        dt1 = datetime.datetime(2016, 10, 20)
        dt2 = datetime.datetime(2015, 11, 2)
        dt1 - dt2
            ——计算两个时间的差值
        dt3 = dt2 + datetime.timedelta(days=intDays)
            ——加上时间的差值
        timedelta.days/timedelta.hours
            ——查看时间的差值
"""


class RealSolar:
    # 输入：日期时间（北京时间），经度
    # 输出：1.当前北京时间、当前河洛时间；2.输入时间对应的河洛时间、输入时间输入经度对应的真太阳时
    def __init__(self):
        self.now_obj = datetime.datetime.today()

    def beijingshijian_now(self, zhidinggeshi):
        # 当前北京时间。东经120度
        if zhidinggeshi is None:
            return self.now_obj
        else:
            return self.now_obj.strftime(zhidinggeshi)

    def heluoshijian(self, zhidingshijian, zhidinggeshi):
        # 河洛时间。东经110度，比北京时间晚40分钟
        return self.zhentaiyangshi(zhidingshijian=zhidingshijian, jingdu=110, zhidinggeshi=zhidinggeshi)

    def zhentaiyangshi(self, zhidingshijian, jingdu, zhidinggeshi):
        # 返回各经度对应输入时间的真太阳时
        # 对精度要求不高，纬度暂时不用，经度每15度相差1个小时即60分钟，每1度相差4分钟（取整数度），交日柱暂时按照时辰算
        # 如果没有输入时间则按当前北京时间，否则按输入时间，自动判断输入格式
        # 若没有指定时间则使用当前时间对象
        if zhidingshijian is None:
            datetime_obj = self.now_obj
        else:
            # 若指定的时间是字符串参数，则要转化为datetime对象
            if type(zhidingshijian) is str:
                #datetime_obj = datetime.datetime.strptime(dt, '%Y/%m/%d %H:%M')  # strptime()函数出现BUG
                datetime_obj = self._datetimeStr2Obj(zhidingshijian)  # 用自己写的解析函数替代
            # 若指定的时间是datetime对象，则直接使用
            else:
                datetime_obj = zhidingshijian
        # 根据输入经度确定时间差值
        minute_delta = (jingdu - 120) * 4
        time_delta = datetime.timedelta(minutes=minute_delta)
        # 判断输入日期时间是否正确
        if 0 <= datetime_obj.year <= 9999 and 1 <= datetime_obj.month <= 12 \
            and 1 <= datetime_obj.day <= self._solarMonthDayMax(datetime_obj.year, datetime_obj.month) \
            and 0 <= datetime_obj.hour <= 23 and 0 <= datetime_obj.minute <= 59:
            datetime_obj += time_delta
        else:
            print('输入的日期时间有错误！')
            raise IOError
        # 返回。根据输入确定输出，若给定格式化字符串，则返回字符串，否则默认返回日期时间对象。例：zhidinggeshi='%Y/%m/%d %H:%M'
        if zhidinggeshi is None:
            return {'时间': datetime_obj, '经度': jingdu}
        else:
            return {'时间': datetime_obj.strftime(zhidinggeshi), '经度': jingdu}

    @staticmethod
    def _solarYearDayMax(solar_year):
        # 判断阳历年的最大天数
        if ((solar_year % 4 == 0) and (solar_year % 100 != 0)) or (solar_year % 400 == 0):
            solar_year_day_max = 366
        else:
            solar_year_day_max = 365
        return solar_year_day_max

    @staticmethod
    def _solarMonthDayMax(solar_year, solar_month):
        # 判断阳历月的最大天数
        if solar_month in [1, 3, 5, 7, 8, 10, 12]:
            solar_month_day_max = 31
        elif solar_month in [4, 6, 9, 11]:
            solar_month_day_max = 30
        elif solar_month == 2:
            if ((solar_year % 4 == 0) and (solar_year % 100 != 0)) or (solar_year % 400 == 0):
                solar_month_day_max = 29
            else:
                solar_month_day_max = 28
        else:
            solar_month_day_max = None
        return solar_month_day_max

    @staticmethod
    def _datetimeStr2Obj(datetime_str):
        try:
            datetime_obj = datetime.datetime(
                # 此处能够转换的日期时间必须足位（不够位数的必须补0）
                # 编程语言问题：字符串切片截取——从0开始，从左界开始，顺数几个就截取几位
                # 例：2017-08-09 15:30
                int(datetime_str[0:4]),   # year=2017
                int(datetime_str[5:7]),   # month=08
                int(datetime_str[8:10]),   # day=09
                int(datetime_str[11:13]),  # hour=15
                int(datetime_str[14:16])  # minute=30
            )
        except ValueError:
            datetime_obj = datetime.datetime(
                # 此处能够转换的日期时间必须足位（不够位数的必须补0）
                # 编程语言问题：字符串切片截取——从0开始，从左界开始，顺数几个就截取几位
                # 例：2017-08-09
                int(datetime_str[0:4]),  # year=2017
                int(datetime_str[5:7]),  # month=08
                int(datetime_str[8:10])  # day=09
            )
        return datetime_obj

    @staticmethod
    def _datetimeObj2Str(datetime_obj):
        # 转化为字符串形式：YYYY-mm-dd HH:MM
        datetime_str = str(datetime_obj.year).zfill(4) + '-' + \
                       str(datetime_obj.month).zfill(2) + '-' + \
                       str(datetime_obj.day).zfill(2) + ' ' + \
                       str(datetime_obj.hour).zfill(2) + ':' + \
                       str(datetime_obj.minute).zfill(2)
        return datetime_str
