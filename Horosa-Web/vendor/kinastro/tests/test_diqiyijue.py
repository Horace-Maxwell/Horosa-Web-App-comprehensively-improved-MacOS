"""Tests for the Di Qi Yi Jue integration."""

from astro.diqiyijue import DiqiyijueChart, compute_diqiyijue_chart
from astro.diqiyijue.calculator import DiQiYiJue


def test_public_compute_returns_chart_dataclass():
    chart = compute_diqiyijue_chart(
        year=1985,
        month=2,
        day=4,
        hour=10,
        minute=0,
        timezone=8.0,
        latitude=39.9042,
        longitude=116.4074,
        location_name='Beijing',
        gender='male',
    )
    assert isinstance(chart, DiqiyijueChart)
    assert chart.four_pillars == {'年': '乙丑', '月': '戊寅', '日': '甲戌', '時': '己巳'}


def test_li_yi_legacy_example_core_values_match():
    engine = DiQiYiJue({'年': '己丑', '月': '乙亥', '日': '庚寅', '時': '丁丑'}, '男')
    assert engine.tai_gz == '丙寅'
    assert engine.yuan_shu == [4, 1, 5, 2]
    assert engine.ying_shu == [2, 1, 1, 2]
    assert engine.ba_gong_raw == [8, 7, 6, 9, 0, 2, 4, 0]
    assert engine.ben_gong_siwei == [7, 5, 2, 4]


def test_li_yi_legacy_example_divination_states_match():
    engine = DiQiYiJue({'年': '己丑', '月': '乙亥', '日': '庚寅', '時': '丁丑'}, '男')
    assert engine.guankong['卦名'] == '乾'
    assert engine.bagua_tibian_result['卦名'] == '巽'
    assert engine.bagua_tibian_result['本變'] == '變'
    assert engine.shu_wei['零數'] == 8
    assert engine.ming_gong_idx == 3
    assert engine.ming_gong_wx == '金'


def test_li_yi_flow_year_biefa_matches_documented_example():
    engine = DiQiYiJue({'年': '己丑', '月': '乙亥', '日': '庚寅', '時': '丁丑'}, '男')
    result = engine.flow_year_biefa(age=44)
    assert result['流籌四位'] == [9, 2, 4, 3]


def test_chart_to_dict_contains_full_chart_snapshot():
    chart = compute_diqiyijue_chart(
        year=1985,
        month=2,
        day=4,
        hour=10,
        minute=0,
        timezone=8.0,
        latitude=39.9042,
        longitude=116.4074,
        location_name='Beijing',
        gender='female',
    )
    payload = chart.to_dict()
    assert payload['gender'] == '女'
    assert payload['full_chart']['胎月'] == chart.tai_month
    assert payload['full_chart']['四柱'] == chart.four_pillars
