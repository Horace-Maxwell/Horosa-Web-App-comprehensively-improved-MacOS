#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sqlite3

"""
使用sqlite3数据库保存易学通用数据
"""


class Db:
    def __init__(self, dbname='utils.db'):
        self.conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), dbname))
        self.cursor = self.conn.cursor()

    # 获取字典格式的列表，把每一行数据从值序列转化为键值对，并且用键索引（可节省大量搜索代码及执行时间）
    def get_tabledict_dict(self, tablename, key_col=1):  # 可指定索引键列
        self.cursor.execute("PRAGMA table_info({0});".format(tablename))
        rows1 = self.cursor.fetchall()  # 每一行的内容是列信息
        colname = []  # 存储列名的列表
        for row in rows1:
            colname.append(row[1])  # 系统输出信息的第二个元素是列名
        self.cursor.execute("SELECT * from {0};".format(tablename))
        rows2 = self.cursor.fetchall()
        tabledict_list = []  # 存储每行字典数据的列表
        for row in rows2:
            dict_tmp = {}
            for i,col in enumerate(row):
                dict_tmp[colname[i]] = col
                tabledict_list.append(dict_tmp)
        tabledict_dict = {}  # 给结果列表添加索引键（指定的索引键列的值必须唯一）
        keyname = colname[key_col]
        for i in tabledict_list:
            tabledict_dict.update({i[keyname]: i})
        return tabledict_dict
