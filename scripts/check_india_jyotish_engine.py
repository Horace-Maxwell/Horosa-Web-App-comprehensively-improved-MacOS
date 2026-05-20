#!/usr/bin/env python3
import copy
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for rel in [
    os.path.join('Horosa-Web', 'astropy'),
    os.path.join('Horosa-Web', 'flatlib-ctrad2'),
]:
    path = os.path.join(ROOT, rel)
    if path not in sys.path:
        sys.path.insert(0, path)

from astrostudy.perchart import PerChart  # noqa: E402
from astrostudy.helper import getChartObj  # noqa: E402
from astrostudy.india.chart9 import Chart9  # noqa: E402
from astrostudy.india.jyotish_engine import build_jyotish  # noqa: E402


BASE_CASES = [
    {
        'name': 'Shanghai modern',
        'date': '1990/01/01',
        'time': '12:00:00',
        'zone': '+08:00',
        'lat': '31n14',
        'lon': '121e28',
    },
    {
        'name': 'Delhi modern',
        'date': '1984/10/31',
        'time': '09:20:00',
        'zone': '+05:30',
        'lat': '28n36',
        'lon': '77e12',
    },
]


def build_params(case):
    data = dict(case)
    data.update({
        'tradition': False,
        'predictive': False,
        'zodiacal': 1,
        'hsys': 0,
        'strongRecption': True,
        'virtualPointReceiveAsp': False,
        'simpleAsp': False,
        'southchart': False,
    })
    return data


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def validate_case(case):
    data = build_params(case)
    perchart = PerChart(data)
    chart_before = getChartObj(data, perchart)
    jyotish = build_jyotish(perchart)
    chart_after = getChartObj(data, perchart)

    assert_true(chart_before['chart']['objects'][0].lon == chart_after['chart']['objects'][0].lon,
                'JyotishEngine must not mutate Horosa chart objects')
    assert_true(jyotish['engine']['source'] == 'chart_json_only', 'engine source should be chart_json_only')
    assert_true(jyotish['panchanga']['tithi']['index'] >= 1, 'missing tithi')
    assert_true(jyotish['panchanga']['nakshatra']['index'] >= 1, 'missing nakshatra')
    assert_true(jyotish['dasha']['vimshottari']['available'], 'missing vimshottari')
    assert_true(len(jyotish['dasha']['vimshottari']['mahadashas']) == 10, 'unexpected mahadasha count')
    assert_true(jyotish['ashtakavarga']['available'], 'missing ashtakavarga')
    assert_true(sum(row['bindu'] for row in jyotish['ashtakavarga']['sarvaBySign']) > 300, 'SAV total too low')
    assert_true(jyotish['shadbala']['available'], 'missing shadbala')
    assert_true(len(jyotish['shadbala']['planets']) == 7, 'unexpected shadbala planet count')
    assert_true(len(jyotish['jaimini']['charaKarakas']) == 7, 'missing chara karakas')
    assert_true('Moon' in jyotish['kp']['sublords'], 'missing KP Moon sublord')

    d1_moon_nak = jyotish['panchanga']['nakshatra']['name']
    navamsa_data = copy.deepcopy(data)
    navamsa = PerChart(navamsa_data)
    jyotish_before_fractal = build_jyotish(navamsa)
    Chart9(navamsa).fractal()
    assert_true(jyotish_before_fractal['panchanga']['nakshatra']['name'] == d1_moon_nak,
                'jyotish data should be captured from D1 before fractal mutation')

    return {
        'name': case['name'],
        'tithi': jyotish['panchanga']['tithi']['index'],
        'nakshatra': d1_moon_nak,
        'firstDasha': jyotish['dasha']['vimshottari']['firstLord']['key'],
        'savTotal': sum(row['bindu'] for row in jyotish['ashtakavarga']['sarvaBySign']),
        'topShadbala': jyotish['shadbala']['planets'][0]['id'],
    }


def main():
    rows = [validate_case(case) for case in BASE_CASES]
    print(json.dumps({
        'ok': True,
        'cases': rows,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
