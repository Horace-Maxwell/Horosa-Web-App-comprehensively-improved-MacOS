# -*- coding: utf-8 -*-
"""坐标格式全兼容 · 永久哨兵（param error 根因回归锁）。

历史事故：前端字段在表单/储存往返中会把数值坐标字符串化（'31.2'/'121.5'/'39.9'），
flatlib geopos.toFloat 对无方向字符的十进制串落进 DMS 分段解析 int('31.2') 抛 ValueError
→ PerChart 崩 → Java 泛化「param error」→ 用户看到误导性的「本地服务未就绪」弹窗。

钉死四件事：
① 十进制串按浮点直读（修复本体）；
② 既有 DMS/数值路径 byte-identical（'26n04'/'121e30'/'12W30:00'/floats 分毫不动）；
③ 🔴 '121e30' 绝不被科学计数误读成 1.21e+32（这是修复实现里最危险的暗雷）；
④ 入口守卫 validate_geo 对真垃圾返回结构化错误、对一切合法格式放行。
任何人改动 geopos/守卫导致回归 → 本套必红。
"""
import pytest

from flatlib.geopos import GeoPos, toFloat
from websrv._guards import validate_geo


# ── ① 十进制串直读（历史崩溃点，修后必须等值于浮点）────────────────────────────
@pytest.mark.parametrize('raw,expected', [
    ('31.2', 31.2), ('121.5', 121.5), ('39.9', 39.9), ('116.4', 116.4),
    ('-121.5', -121.5), ('+26.07', 26.07), ('0', 0.0), ('90', 90.0), (' 31.2 ', 31.2),
])
def test_decimal_string_reads_as_float(raw, expected):
    assert toFloat(raw) == pytest.approx(expected)


# ── ② 既有 DMS / 数值路径 byte-identical（回归锚）────────────────────────────
@pytest.mark.parametrize('raw,expected', [
    ('26n04', 26 + 4 / 60.0), ('31n12', 31.2), ('119e19', 119 + 19 / 60.0),
    ('121e30', 121.5), ('12W30:00', -12.5), ('45N32', 45 + 32 / 60.0), ('128w45', -(128 + 45 / 60.0)),
])
def test_dms_paths_unchanged(raw, expected):
    assert toFloat(raw) == pytest.approx(expected)


@pytest.mark.parametrize('raw', [31.2, -121.5, 0, 90, -90.0])
def test_numeric_passthrough(raw):
    assert toFloat(raw) == pytest.approx(float(raw))


# ── ③ 科学计数暗雷：'121e30' 是东经 121°30'，绝不是 1.21e+32 ────────────────────
def test_e_direction_never_parsed_as_scientific_notation():
    assert toFloat('121e30') == pytest.approx(121.5)
    assert toFloat('121e30') < 180.0
    assert toFloat('119e19') < 180.0


# ── 十进制+尾随方向字符（旧路径同样崩，一并救活）─────────────────────────────
@pytest.mark.parametrize('raw,expected', [
    ('26.07N', 26.07), ('26N', 26.0), ('121.5w', -121.5), ('31.2s', -31.2),
])
def test_decimal_with_trailing_direction(raw, expected):
    assert toFloat(raw) == pytest.approx(expected)


# ── GeoPos 端到端：串/数值同坐标同结果 ─────────────────────────────────────
def test_geopos_string_equals_numeric():
    a = GeoPos('31.2', '121.5')
    b = GeoPos(31.2, 121.5)
    assert a.lat == pytest.approx(b.lat)
    assert a.lon == pytest.approx(b.lon)
    c = GeoPos('31n12', '121e30')
    assert c.lat == pytest.approx(b.lat)
    assert c.lon == pytest.approx(b.lon)


# ── ④ 入口守卫：合法全放行、垃圾结构化拦截（不再抛原始堆栈）───────────────────
@pytest.mark.parametrize('data', [
    {'lat': '31.2', 'lon': '121.5'},
    {'lat': 31.2, 'lon': 121.5},
    {'lat': '26n04', 'lon': '119e19'},
    {'lat': '31n12', 'lon': '121e30', 'gpsLat': 31.2, 'gpsLon': 121.5},
    {},                       # 字段缺失兼容旧请求
    {'lat': '', 'lon': ''},   # 空串放行(下游默认)
])
def test_validate_geo_accepts_all_legal_formats(data):
    assert validate_geo(data) is None


@pytest.mark.parametrize('data,frag', [
    ({'lat': 'abc', 'lon': '121.5'}, 'lat'),          # 真垃圾 → 结构化错误
    ({'lat': '31.2', 'lon': 'garbage'}, 'lon'),
    ({'lat': '200', 'lon': '121.5'}, 'lat'),           # 越界十进制串
    ({'lat': '31.2', 'lon': '181'}, 'lon'),
    ({'gpsLat': 200, 'lat': '31.2', 'lon': '121.5'}, 'gpsLat'),
])
def test_validate_geo_rejects_garbage_structured(data, frag):
    err = validate_geo(data)
    assert err is not None and err.get('err') == 'invalid_coordinates'
    assert frag in err.get('detail', '')


# ── webchartsrv finally 早退漏洞回归锁：_trip_orig 必须与 _terms_orig 同预初始化 ──
# 历史 bug：守卫早退(invalid_date/invalid_coordinates)时 finally 引用未赋值的 _trip_orig
# → UnboundLocalError → CherryPy HTML 500(结构化错误被吞)。源扫锁死配对。
def test_webchartsrv_trip_orig_preinitialized_with_terms_orig():
    import io
    import os
    src = io.open(os.path.join(os.path.dirname(__file__), '..', 'websrv', 'webchartsrv.py'), encoding='utf-8').read()
    terms_inits = src.count('_terms_orig = None')
    trip_inits = src.count('_trip_orig = None')
    assert terms_inits >= 3, '端点结构变动:请同步本哨兵'
    assert trip_inits >= terms_inits, '_trip_orig 预初始化缺失:守卫早退将 UnboundLocalError→500'


# ── PerChart 冒烟：十进制串坐标出盘 == 数值坐标出盘（历史上前者直接崩）──────────
def test_perchart_decimal_string_coords_smoke():
    from astrostudy.perchart import PerChart
    from flatlib import const
    base = {'date': '1991/08/21', 'time': '14:30:00', 'zone': '+08:00'}
    a = PerChart({**base, 'lat': '31.2', 'lon': '121.5'})
    b = PerChart({**base, 'lat': 31.2, 'lon': 121.5})
    sa = a.chart.getObject(const.SUN).lon
    sb = b.chart.getObject(const.SUN).lon
    assert sa == pytest.approx(sb)
    assert a.chart.getAngle(const.ASC).lon == pytest.approx(b.chart.getAngle(const.ASC).lon)
