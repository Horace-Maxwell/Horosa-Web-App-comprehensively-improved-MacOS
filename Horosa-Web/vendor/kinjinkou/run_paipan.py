#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
金口诀排盘 (Jin Kou Jue Paipan) Runner
用于运行 _paipan.py 中的 Paipan 类进行六壬排盘

使用方法：
    python run_paipan.py
"""

from kinjinkou import Paipan


def main():
    # 创建排盘实例
    pp = Paipan()

    # 设置干支信息（示例：甲子年 丙寅月 丙午日 甲午时）
    ganzhi = {
        '年柱': '甲子',
        '月柱': '丙寅',
        '日柱': '丙午',
        '时柱': '甲午',
        '文本': '甲子年 丙寅月 丙午日 甲午时'
    }

    # 设置地分（十二地支之一）
    difen = '子'

    # 月将和占时可设为 None，自动从干支中获取
    yuejiang = None
    zhanshi = None

    # 执行排盘
    pp.paipan(ganzhi, difen, yuejiang, zhanshi)

    # 输出结果
    print(pp.output())


if __name__ == '__main__':
    main()
