import math

from flatlib import const
from flatlib import utils


VARGA_ENGINE_VERSION = 'india_kernel_varga_v2'


VARGA_DEFINITIONS = {
    1: {'key': 'd1', 'name': 'Rashi', 'label': 'D1 Rashi'},
    2: {'key': 'd2', 'name': 'Hora', 'label': 'D2 Hora'},
    3: {'key': 'd3', 'name': 'Drekkana', 'label': 'D3 Drekkana'},
    4: {'key': 'd4', 'name': 'Chaturthamsa', 'label': 'D4 Chaturthamsa'},
    5: {'key': 'd5', 'name': 'Panchamsa', 'label': 'D5 Panchamsa'},
    6: {'key': 'd6', 'name': 'Shashthamsa', 'label': 'D6 Shashthamsa'},
    7: {'key': 'd7', 'name': 'Saptamsa', 'label': 'D7 Saptamsa'},
    8: {'key': 'd8', 'name': 'Ashtamsa', 'label': 'D8 Ashtamsa'},
    9: {'key': 'd9', 'name': 'Navamsa', 'label': 'D9 Navamsa'},
    10: {'key': 'd10', 'name': 'Dasamsa', 'label': 'D10 Dasamsa'},
    11: {'key': 'd11', 'name': 'Rudramsa', 'label': 'D11 Rudramsa'},
    12: {'key': 'd12', 'name': 'Dwadasamsa', 'label': 'D12 Dwadasamsa'},
    16: {'key': 'd16', 'name': 'Shodasamsa', 'label': 'D16 Shodasamsa'},
    20: {'key': 'd20', 'name': 'Vimsamsa', 'label': 'D20 Vimsamsa'},
    24: {'key': 'd24', 'name': 'Chaturvimsamsa', 'label': 'D24 Chaturvimsamsa'},
    27: {'key': 'd27', 'name': 'Nakshatramsa', 'label': 'D27 Nakshatramsa'},
    30: {'key': 'd30', 'name': 'Trimsamsa', 'label': 'D30 Trimsamsa'},
    40: {'key': 'd40', 'name': 'Khavedamsa', 'label': 'D40 Khavedamsa'},
    45: {'key': 'd45', 'name': 'Akshavedamsa', 'label': 'D45 Akshavedamsa'},
    60: {'key': 'd60', 'name': 'Shashtiamsa', 'label': 'D60 Shashtiamsa'},
}


ODD_SIGNS = {0, 2, 4, 6, 8, 10}
MOVABLE_SIGNS = {0, 3, 6, 9}
FIXED_SIGNS = {1, 4, 7, 10}
FIRE_SIGNS = {0, 4, 8}
EARTH_SIGNS = {1, 5, 9}
AIR_SIGNS = {2, 6, 10}


def normalize_chartnum(chartnum):
    try:
        value = int(chartnum)
    except Exception:
        value = 1
    return value if value in VARGA_DEFINITIONS else 1


def get_supported_vargas():
    return [dict({'chartnum': chartnum}, **VARGA_DEFINITIONS[chartnum])
            for chartnum in sorted(VARGA_DEFINITIONS.keys())]


def _part(degree_in_sign, chartnum):
    interval = 30.0 / chartnum
    value = int(math.floor(degree_in_sign / interval))
    return min(max(value, 0), chartnum - 1)


def _scaled_degree(degree_in_sign, chartnum):
    interval = 30.0 / chartnum
    part = _part(degree_in_sign, chartnum)
    return ((degree_in_sign - part * interval) / interval) * 30.0


def _modality_start(sign_index, movable=0, fixed=4, dual=8):
    if sign_index in MOVABLE_SIGNS:
        return movable
    if sign_index in FIXED_SIGNS:
        return fixed
    return dual


def _element_start_for_d9(sign_index):
    if sign_index in FIRE_SIGNS:
        return 0
    if sign_index in EARTH_SIGNS:
        return 9
    if sign_index in AIR_SIGNS:
        return 6
    return 3


def _element_start_for_d27(sign_index):
    if sign_index in FIRE_SIGNS:
        return 0
    if sign_index in EARTH_SIGNS:
        return 3
    if sign_index in AIR_SIGNS:
        return 6
    return 9


def _d30_position(sign_index, degree_in_sign):
    is_odd = sign_index in ODD_SIGNS
    if is_odd:
        ranges = [
            (0.0, 5.0, 0),
            (5.0, 10.0, 10),
            (10.0, 18.0, 8),
            (18.0, 25.0, 2),
            (25.0, 30.0, 6),
        ]
    else:
        ranges = [
            (0.0, 5.0, 1),
            (5.0, 12.0, 5),
            (12.0, 20.0, 11),
            (20.0, 25.0, 9),
            (25.0, 30.0, 7),
        ]
    for start, end, target_sign in ranges:
        if degree_in_sign < end or end == 30.0:
            span = end - start
            degree = ((degree_in_sign - start) / span) * 30.0 if span else 0.0
            return target_sign, max(0.0, min(degree, 29.999999999))
    return ranges[-1][2], 0.0


def varga_position(longitude, chartnum):
    chartnum = normalize_chartnum(chartnum)
    lon = float(longitude) % 360.0
    if chartnum == 1:
        return lon

    sign_index = int(math.floor(lon / 30.0)) % 12
    degree_in_sign = lon % 30.0
    part = _part(degree_in_sign, chartnum)
    degree = _scaled_degree(degree_in_sign, chartnum)
    is_odd = sign_index in ODD_SIGNS

    if chartnum == 2:
        if is_odd:
            target_sign = 4 if degree_in_sign < 15.0 else 3
        else:
            target_sign = 3 if degree_in_sign < 15.0 else 4
    elif chartnum == 3:
        target_sign = (sign_index + part * 4) % 12
    elif chartnum == 4:
        target_sign = (sign_index + part * 3) % 12
    elif chartnum in (5, 6):
        target_sign = ((0 if is_odd else 6) + part) % 12
    elif chartnum == 7:
        target_sign = (sign_index + (0 if is_odd else 6) + part) % 12
    elif chartnum in (8, 11, 16, 45):
        target_sign = (_modality_start(sign_index) + part) % 12
    elif chartnum == 9:
        target_sign = (_element_start_for_d9(sign_index) + part) % 12
    elif chartnum == 10:
        target_sign = (sign_index + (0 if is_odd else 8) + part) % 12
    elif chartnum == 12:
        target_sign = (sign_index + part) % 12
    elif chartnum == 20:
        target_sign = (_modality_start(sign_index, movable=0, fixed=8, dual=4) + part) % 12
    elif chartnum == 24:
        target_sign = ((4 if is_odd else 3) + part) % 12
    elif chartnum == 27:
        target_sign = (_element_start_for_d27(sign_index) + part) % 12
    elif chartnum == 30:
        target_sign, degree = _d30_position(sign_index, degree_in_sign)
    elif chartnum == 40:
        target_sign = ((0 if is_odd else 6) + part) % 12
    elif chartnum == 60:
        target_sign = (sign_index + part) % 12
    else:
        target_sign = sign_index

    return (target_sign * 30.0 + degree) % 360.0


def _relocate(point, longitude):
    point.relocate(longitude % 360.0)


def _relocate_house(house, longitude, hsys):
    house.hsys = hsys
    house.size = 30.0
    house.relocate(longitude % 360.0)
    ra, decl = utils.eqCoords(house.lon, 0)
    house.ra = ra
    house.decl = decl


def apply_varga_chart(perchart, chartnum):
    chartnum = normalize_chartnum(chartnum)
    definition = VARGA_DEFINITIONS[chartnum]
    perchart.vargaChart = dict({'chartnum': chartnum}, **definition)
    perchart.vargaEngineVersion = VARGA_ENGINE_VERSION
    if chartnum == 1:
        perchart.reinit()
        return perchart

    chart = perchart.chart
    asc = chart.getAngle(const.ASC)
    mc = chart.getAngle(const.MC)
    desc = chart.getAngle(const.DESC)
    ic = chart.getAngle(const.IC)

    asclon = varga_position(asc.lon, chartnum)
    mclon = varga_position(mc.lon, chartnum)
    _relocate(asc, asclon)
    _relocate(mc, mclon)
    _relocate(desc, asclon + 180.0)
    _relocate(ic, mclon + 180.0)

    if getattr(perchart, 'houseCode', None) == 5:
        house1lon = asclon
    else:
        house1lon = math.floor(asclon / 30.0) * 30.0
    for house in chart.houses:
        house_num = int(house.id[5:])
        _relocate_house(house, house1lon + (house_num - 1) * 30.0, perchart.house)

    for obj in chart.objects:
        _relocate(obj, varga_position(obj.lon, chartnum))
    for obj in chart.pars:
        _relocate(obj, varga_position(obj.lon, chartnum))

    perchart.reinit()
    return perchart
