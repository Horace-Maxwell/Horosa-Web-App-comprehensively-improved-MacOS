# 赤道回归·实时(mode8)golden:宿宽=盘历元距星真赤经差(与 mode5 同一活体距星源),
# 锚=回归点(牛前冬至 270° 默认 / 春分壁2.3,与 mode7 同款)。
# 判定性关系:与 mode7 之别在宿宽(实时 vs 元明立成·跨历元会变),与 mode5 之别仅在锚(纯旋转)。
import pytest
from astrostudy.perchart import PerChart
from flatlib import const

BASE = {'date': '1992/06/12', 'time': '18:00:00', 'zone': '8', 'lat': '30n54', 'lon': '119e24',
        'gpsLat': '30n54', 'gpsLon': '119e24', 'hsys': 0, 'zodiacal': 0, 'tradition': 0, 'guolaoLifeMode': 'asc'}
SEVEN = (const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN)


def _ring(data):
    pc = PerChart(dict(data))
    return {s.name: s.ra for s in pc.getEquatorialTropicalLiveSu28()}


def _ring5(data):
    pc = PerChart(dict(data))
    return {getattr(s, 'name', None) or s.id: s.ra for s in pc.getEquatorialSu28()}


def _su(data):
    pc = PerChart(dict(data))
    pc.getFixedStarSu28()
    return {o.id: getattr(o, 'su28', '') for o in pc.chart.objects if o.id in SEVEN}


def test_mode8_anchor_dongzhi_default():
    # 默认锚=牛前冬至:牛宿前缘 = 冬至 RA 270°(精确钉死)。
    assert abs(_ring(dict(BASE, doubingSu28=8))['牛'] - 270.0) < 0.001


def test_mode8_anchor_chunfen_option():
    # 春分锚:壁宿2.3(古度)= 春分 RA 0°。
    bi = _ring(dict(BASE, doubingSu28=8, guolaoEqTropicalAnchor='chunfen'))['壁']
    wrapped = (bi + 2.3 * 360.0 / 365.2575) % 360.0
    assert wrapped < 0.001 or (360.0 - wrapped) < 0.001


def test_mode8_widths_equal_mode5_pure_rotation():
    # 宿宽与 mode5 逐宿一致(同一活体距星源)——mode8 只是整体旋转到回归锚。
    r8 = _ring(dict(BASE, doubingSu28=8))
    pc5 = PerChart(dict(BASE, doubingSu28=5))
    stars5 = pc5.getEquatorialSu28()
    name_by_id = dict(zip(const.LIST_FIXED_SU28, const.LIST_FIXED_SU28_NAME))
    r5 = {name_by_id[s.id]: s.ra for s in stars5}

    def widths(ring):
        ras = sorted(ring.values())
        return sorted(round((ras[(i + 1) % 28] - ras[i]) % 360.0, 6) for i in range(28))

    w8 = widths(r8)
    w5 = widths(r5)
    assert all(abs(a - b) < 1e-6 for a, b in zip(w8, w5)), (w8[:4], w5[:4])
    # 且两者相差恒定旋转量(逐宿 offset 一致)。
    offsets = {name: round((r8[name] - r5[name]) % 360.0, 6) for name in r8}
    assert len(set(offsets.values())) == 1, offsets


def test_mode8_live_varies_across_epochs():
    # 活体判定:1992 与 2092 两盘宿界不同(与 mode7 立成跨历元恒定正相反)。
    assert _ring(dict(BASE, doubingSu28=8)) != _ring(dict(BASE, date='2092/06/12', doubingSu28=8))
    # 但两历元的牛前缘都精确钉在 270(锚不动、宿形变)。
    assert abs(_ring(dict(BASE, date='2092/06/12', doubingSu28=8))['牛'] - 270.0) < 0.001


def test_mode8_places_all_seven_and_siyu():
    pc = PerChart(dict(BASE, doubingSu28=8))
    pc.getFixedStarSu28()
    su7 = {o.id: getattr(o, 'su28', '') for o in pc.chart.objects if o.id in SEVEN}
    assert su7 and all(su7.values()), su7
    siyu = [o.id for o in pc.chart.objects if o.id in (const.NORTH_NODE, const.SOUTH_NODE) and getattr(o, 'su28', '')]
    assert len(siyu) >= 2, siyu


def test_mode8_ring_differs_from_mode7_and_mode5():
    # 宿界层面判定(行星落宿可能恰好同宿,不作强断言):
    # vs mode7:宿宽不同(实时距星 vs 元明立成,觜宽 1.7° vs 0.05°);vs mode5:整体旋转(锚不同)。
    r8 = _ring(dict(BASE, doubingSu28=8))
    pc7 = PerChart(dict(BASE, doubingSu28=7))
    r7 = {s.name: s.ra for s in pc7.getEquatorialTropicalSu28()}
    assert any(abs(r8[n] - r7[n]) > 0.1 for n in r8)
    pc5 = PerChart(dict(BASE, doubingSu28=5))
    name_by_id = dict(zip(const.LIST_FIXED_SU28, const.LIST_FIXED_SU28_NAME))
    r5 = {name_by_id[s.id]: s.ra for s in pc5.getEquatorialSu28()}
    assert any(abs(r8[n] - r5[n]) > 0.1 for n in r8)


def test_mode0_to_7_zero_regression():
    # mode8 仅加 ==8 分支 → mode 0–7 输出不变(抽查 mode2 默认 + mode5 + mode7 锚)。
    su2 = _su(dict(BASE, doubingSu28=2))
    su5 = _su(dict(BASE, doubingSu28=5))
    assert su2[const.SUN] == '毕' and su2[const.MARS] == '奎'
    assert su5[const.SUN] == '毕' and su5[const.JUPITER] == '星'
    pc7 = PerChart(dict(BASE, doubingSu28=7))
    assert abs({s.name: s.ra for s in pc7.getEquatorialTropicalSu28()}['牛'] - 270.0) < 0.01
