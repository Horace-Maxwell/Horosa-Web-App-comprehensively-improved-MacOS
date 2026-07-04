# -*- coding: utf-8 -*-
"""敌友 Pañcadhā Maitrī 单元测试（古籍第 6 章）。

钉定（古籍 §6.1/§6.2/§6.3 + 示例盘 2000-03-01）：
- 自然敌友表 §6.1 逐曜友/敌/中；
- 复合五分 §6.3：Su→Mo=大友(adhimitra) / Sa→Mo=大敌(adhisatru)；
- 非对称：Su→Me=敌(satru) 而 Me→Su=中立(sama)；
- 临时 §6.2：对方在本星 2/3/4/10/11/12 宫=临友，其余=临敌。
真值来自古籍数表（法律），失败=重核古籍勿改测试将就。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flatlib import const  # noqa: E402
from astrostudy.india import primitives as P  # noqa: E402


def test_natural_relation_matches_manual_table7():
    # §6.1 太阳行：友={月火木}、敌={金土}、中={水}
    assert P.natural_relation(const.SUN, const.MOON) == 'friend'
    assert P.natural_relation(const.SUN, const.MARS) == 'friend'
    assert P.natural_relation(const.SUN, const.JUPITER) == 'friend'
    assert P.natural_relation(const.SUN, const.VENUS) == 'enemy'
    assert P.natural_relation(const.SUN, const.SATURN) == 'enemy'
    assert P.natural_relation(const.SUN, const.MERCURY) == 'neutral'
    # §6.1 土星行：友={水金}、敌={日月火}、中={木}
    assert P.natural_relation(const.SATURN, const.MERCURY) == 'friend'
    assert P.natural_relation(const.SATURN, const.MOON) == 'enemy'
    assert P.natural_relation(const.SATURN, const.MARS) == 'enemy'
    assert P.natural_relation(const.SATURN, const.JUPITER) == 'neutral'
    # 月亮无自然敌（§6.1 月行全友/中）
    assert P.natural_relation(const.MOON, const.MARS) == 'neutral'


# 示例盘 2000-03-01 星座：Su/Me 水瓶、Mo 射手、Sa 白羊（古籍卷首速查表）。
_SIGNS = {
    const.SUN: const.AQUARIUS,
    const.MOON: const.SAGITTARIUS,
    const.MERCURY: const.AQUARIUS,
    const.SATURN: const.ARIES,
}


def test_compound_manual_examples_6_3():
    # §6.3 示例 1：Su→Mo = 大友（自然友 + 临时友[Mo 在 Su 第11宫]）
    assert P.compound_relation(const.SUN, const.MOON, _SIGNS) == 'adhimitra'
    # §6.3 示例 2：Sa→Mo = 大敌（自然敌 + 临时敌[Mo 在 Sa 第9宫]）
    assert P.compound_relation(const.SATURN, const.MOON, _SIGNS) == 'adhisatru'
    # §6.3 示例 3（非对称）：Su→Me=敌，Me→Su=中立
    assert P.compound_relation(const.SUN, const.MERCURY, _SIGNS) == 'satru'
    assert P.compound_relation(const.MERCURY, const.SUN, _SIGNS) == 'sama'


def test_non_symmetric():
    assert (P.compound_relation(const.SUN, const.MERCURY, _SIGNS)
            != P.compound_relation(const.MERCURY, const.SUN, _SIGNS))


def test_tatkalika_2_3_4_10_11_12_is_friend():
    # §6.2：对方在本星 2/3/4/10/11/12 宫 = 临友，其余 = 临敌。
    # Su 水瓶(11)，Mo 射手(9)：从水瓶数到射手 = 第 11 位 → 临友。
    assert P.tatkalika_relation(const.SUN, const.MOON, _SIGNS) == 'friend'
    # Sa 白羊(1)，Mo 射手(9)：从白羊数到射手 = 第 9 位 → 临敌。
    assert P.tatkalika_relation(const.SATURN, const.MOON, _SIGNS) == 'enemy'
    # 同座 = 第 1 位 → 临敌。
    assert P.tatkalika_relation(const.SUN, const.MERCURY, _SIGNS) == 'enemy'


def test_compound_values_in_five_levels():
    levels = {'adhimitra', 'mitra', 'sama', 'satru', 'adhisatru'}
    for a in (const.SUN, const.MOON, const.MARS, const.MERCURY, const.JUPITER, const.VENUS, const.SATURN):
        for b in (const.SUN, const.MOON, const.MARS, const.MERCURY, const.JUPITER, const.VENUS, const.SATURN):
            if a == b:
                continue
            r = P.compound_relation(a, b, _SIGNS)
            assert r in levels or r is None
