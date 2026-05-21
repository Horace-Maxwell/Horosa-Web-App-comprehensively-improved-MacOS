import math
import traceback

import swisseph
from flatlib import const
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import angle
from flatlib.dignities import essential
from flatlib.protocols.temperament import Temperament

from astrostudy.perchart import PerChart
from astrostudy.perpredict import dateSolarReturn, dateLunarReturn


PLANET_SWISS_IDS = {
    const.SUN: swisseph.SUN,
    const.MOON: swisseph.MOON,
    const.MERCURY: swisseph.MERCURY,
    const.VENUS: swisseph.VENUS,
    const.MARS: swisseph.MARS,
    const.JUPITER: swisseph.JUPITER,
    const.SATURN: swisseph.SATURN,
    const.URANUS: swisseph.URANUS,
    const.NEPTUNE: swisseph.NEPTUNE,
    const.PLUTO: swisseph.PLUTO,
}

DEFAULT_EVENT_PLANETS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
]

DEFAULT_NATAL_POINTS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.ASC, const.MC
]

MAJOR_ASPECTS = [
    {'name': 'Conjunction', 'angle': 0, 'orb': 8},
    {'name': 'Sextile', 'angle': 60, 'orb': 4},
    {'name': 'Square', 'angle': 90, 'orb': 6},
    {'name': 'Trine', 'angle': 120, 'orb': 6},
    {'name': 'Quincunx', 'angle': 150, 'orb': 3},
    {'name': 'Opposition', 'angle': 180, 'orb': 8},
]

SIGN_ELEMENTS = {
    const.ARIES: 'Fire', const.LEO: 'Fire', const.SAGITTARIUS: 'Fire',
    const.TAURUS: 'Earth', const.VIRGO: 'Earth', const.CAPRICORN: 'Earth',
    const.GEMINI: 'Air', const.LIBRA: 'Air', const.AQUARIUS: 'Air',
    const.CANCER: 'Water', const.SCORPIO: 'Water', const.PISCES: 'Water',
}

SIGN_MODES = {
    const.ARIES: 'Cardinal', const.CANCER: 'Cardinal', const.LIBRA: 'Cardinal', const.CAPRICORN: 'Cardinal',
    const.TAURUS: 'Fixed', const.LEO: 'Fixed', const.SCORPIO: 'Fixed', const.AQUARIUS: 'Fixed',
    const.GEMINI: 'Mutable', const.VIRGO: 'Mutable', const.SAGITTARIUS: 'Mutable', const.PISCES: 'Mutable',
}

HOUSE_SCORES = {
    const.HOUSE1: 12, const.HOUSE2: 6, const.HOUSE3: 3, const.HOUSE4: 9,
    const.HOUSE5: 7, const.HOUSE6: 1, const.HOUSE7: 10, const.HOUSE8: 4,
    const.HOUSE9: 5, const.HOUSE10: 11, const.HOUSE11: 8, const.HOUSE12: 2,
}

DIGNITY_SCORES = {
    'ruler': 5,
    'exalt': 4,
    'dayTrip': 3,
    'nightTrip': 3,
    'partTrip': 3,
    'term': 2,
    'face': 1,
}

PARS_SPIRIT = 'Pars Spirit'

LOT_FORMULAS = [
    ('pars_eros_extra', 'Lot of Eros', const.VENUS),
    ('pars_necessity_extra', 'Lot of Necessity', const.MERCURY),
    ('pars_courage_extra', 'Lot of Courage', const.MARS),
    ('pars_victory_extra', 'Lot of Victory', const.JUPITER),
    ('pars_nemesis_extra', 'Lot of Nemesis', const.SATURN),
]


def norm360(value):
    return value % 360.0


def norm180(value):
    return (value + 180.0) % 360.0 - 180.0


def angle_distance(a, b):
    return abs(norm180(a - b))


def signed_aspect_delta(lon_a, lon_b, aspect):
    diff = abs(norm180(lon_a - lon_b))
    return diff - float(aspect)


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def to_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ('1', 'true', 'yes', 'on')
    return bool(value)


def zone_value(zone):
    txt = str(zone or '+00:00')
    sign = -1 if txt.startswith('-') else 1
    txt = txt[1:] if txt[:1] in ('+', '-') else txt
    parts = txt.split(':')
    hours = int(parts[0]) if parts and parts[0] else 0
    minutes = int(parts[1]) if len(parts) > 1 else 0
    return sign * (hours + minutes / 60.0)


def geo_to_degree(value, positive_marker, negative_marker):
    if isinstance(value, (int, float)):
        return float(value)
    txt = str(value or '0').strip().lower()
    sign = -1 if negative_marker in txt else 1
    txt = txt.replace(positive_marker, ' ').replace(negative_marker, ' ')
    parts = [p for p in txt.replace(':', ' ').split() if p]
    deg = safe_float(parts[0], 0.0) if parts else 0.0
    minute = safe_float(parts[1], 0.0) if len(parts) > 1 else 0.0
    sec = safe_float(parts[2], 0.0) if len(parts) > 2 else 0.0
    return sign * (abs(deg) + minute / 60.0 + sec / 3600.0)


def base_params(data):
    params = dict(data or {})
    params.setdefault('time', '12:00:00')
    params.setdefault('zone', '+00:00')
    params.setdefault('lat', '0n00')
    params.setdefault('lon', '0e00')
    params.setdefault('hsys', 0)
    params.setdefault('zodiacal', 0)
    params.setdefault('tradition', False)
    params.setdefault('predictive', False)
    return params


def dt_from_data(data, date_key='date', time_key='time'):
    return Datetime(data[date_key], data.get(time_key, '00:00:00'), data.get('zone', '+00:00'))


def date_time_from_jd(jd, zone):
    local_jd = jd + zone_value(zone) / 24.0
    year, month, day, hour_float = swisseph.revjul(local_jd, swisseph.GREG_CAL)
    hour = int(hour_float)
    minute_float = (hour_float - hour) * 60.0
    minute = int(minute_float)
    second = int(round((minute_float - minute) * 60.0))
    if second >= 60:
        second -= 60
        minute += 1
    if minute >= 60:
        minute -= 60
        hour += 1
    date_text = '{0:04d}-{1:02d}-{2:02d}'.format(year, month, day)
    time_text = '{0:02d}:{1:02d}:{2:02d}'.format(hour, minute, second)
    return {
        'jd': jd,
        'datetime': '{0} {1}'.format(date_text, time_text),
        'date': date_text,
        'time': time_text,
    }


def chart_params_from_jd(base, jd, pos=None):
    local = date_time_from_jd(jd, base.get('zone', '+00:00'))
    params = dict(base)
    params['date'] = local['date']
    params['time'] = local['time']
    if pos is not None:
        params['lat'] = pos.lat
        params['lon'] = pos.lon
    params['tradition'] = False
    params['predictive'] = False
    return params


def swe_lon(body, jd):
    xx, _ = swisseph.calc_ut(jd, PLANET_SWISS_IDS[body], swisseph.FLG_SWIEPH | swisseph.FLG_SPEED)
    return norm360(xx[0]), xx[3], xx


def sign_index(lon):
    return int(norm360(lon) / 30.0) % 12


def sign_name_from_lon(lon):
    return const.LIST_SIGNS[sign_index(lon)]


def object_to_dict(obj):
    return {
        'id': obj.id,
        'lon': safe_float(getattr(obj, 'lon', 0)),
        'lat': safe_float(getattr(obj, 'lat', 0)),
        'sign': getattr(obj, 'sign', sign_name_from_lon(safe_float(getattr(obj, 'lon', 0)))),
        'signlon': safe_float(getattr(obj, 'signlon', safe_float(getattr(obj, 'lon', 0)) % 30)),
        'lonspeed': safe_float(getattr(obj, 'lonspeed', 0)),
    }


def chart_points(perchart, include_angles=True):
    points = []
    for obj in perchart.chart.objects:
        if getattr(obj, 'id', None) in const.LIST_MIDDLE_POINTS:
            continue
        points.append(object_to_dict(obj))
    if include_angles:
        for obj in perchart.chart.angles:
            points.append(object_to_dict(obj))
    return points


def find_aspect(points, a, b, target, orb):
    pa = next((item for item in points if item['id'] == a), None)
    pb = next((item for item in points if item['id'] == b), None)
    if not pa or not pb:
        return None
    delta = abs(angle_distance(pa['lon'], pb['lon']) - target)
    if delta <= orb:
        return {'a': a, 'b': b, 'aspect': target, 'orb': delta}
    return None


def detect_patterns(points):
    ids = [p['id'] for p in points if p['id'] in DEFAULT_EVENT_PLANETS or p['id'] in (const.ASC, const.MC)]
    patterns = []
    aspects = {}
    for i, ida in enumerate(ids):
        for idb in ids[i + 1:]:
            for asp in MAJOR_ASPECTS:
                hit = find_aspect(points, ida, idb, asp['angle'], asp['orb'])
                if hit:
                    aspects[(ida, idb, asp['angle'])] = hit
                    aspects[(idb, ida, asp['angle'])] = hit

    def has(a, b, deg):
        return aspects.get((a, b, deg))

    for i, a in enumerate(ids):
        for j, b in enumerate(ids[i + 1:], i + 1):
            for c in ids[j + 1:]:
                if has(a, b, 120) and has(a, c, 120) and has(b, c, 120):
                    patterns.append({'type': 'grand_trine', 'label': 'Grand Trine', 'points': [a, b, c]})
                if has(a, b, 60) and has(a, c, 150) and has(b, c, 150):
                    patterns.append({'type': 'yod', 'label': 'Yod', 'points': [a, b, c], 'apex': c})
                if has(a, c, 60) and has(a, b, 150) and has(c, b, 150):
                    patterns.append({'type': 'yod', 'label': 'Yod', 'points': [a, c, b], 'apex': b})
                if has(b, c, 60) and has(b, a, 150) and has(c, a, 150):
                    patterns.append({'type': 'yod', 'label': 'Yod', 'points': [b, c, a], 'apex': a})
                for apex, left, right in ((a, b, c), (b, a, c), (c, a, b)):
                    if has(left, right, 180) and has(apex, left, 90) and has(apex, right, 90):
                        patterns.append({'type': 't_square', 'label': 'T-Square', 'points': [apex, left, right], 'apex': apex})

    n = len(ids)
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                for d in range(c + 1, n):
                    quad = [ids[a], ids[b], ids[c], ids[d]]
                    opps = 0
                    squares = 0
                    sextiles = 0
                    trines = 0
                    for i in range(4):
                        for j in range(i + 1, 4):
                            opps += 1 if has(quad[i], quad[j], 180) else 0
                            squares += 1 if has(quad[i], quad[j], 90) else 0
                            sextiles += 1 if has(quad[i], quad[j], 60) else 0
                            trines += 1 if has(quad[i], quad[j], 120) else 0
                    if opps >= 2 and squares >= 4:
                        patterns.append({'type': 'grand_cross', 'label': 'Grand Cross', 'points': quad})
                    if opps >= 2 and sextiles >= 2 and trines >= 2:
                        patterns.append({'type': 'mystic_rectangle', 'label': 'Mystic Rectangle', 'points': quad})
                    for tri in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)):
                        rest = next(idx for idx in range(4) if idx not in tri)
                        tri_ids = [quad[idx] for idx in tri]
                        rest_id = quad[rest]
                        if has(tri_ids[0], tri_ids[1], 120) and has(tri_ids[0], tri_ids[2], 120) and has(tri_ids[1], tri_ids[2], 120):
                            if any(has(rest_id, t, 180) for t in tri_ids) and sum(1 for t in tri_ids if has(rest_id, t, 60)) >= 2:
                                patterns.append({'type': 'kite', 'label': 'Kite', 'points': quad, 'tail': rest_id})

    by_sign = {}
    for p in points:
        if p['id'] in ids:
            by_sign.setdefault(p['sign'], []).append(p['id'])
    for sign, members in by_sign.items():
        if len(members) >= 3:
            patterns.append({'type': 'stellium_sign', 'label': 'Sign Stellium', 'sign': sign, 'points': members})

    sorted_points = sorted([p for p in points if p['id'] in ids], key=lambda item: item['lon'])
    doubled = sorted_points + [{**p, 'lon': p['lon'] + 360} for p in sorted_points]
    seen = set()
    for i in range(len(sorted_points)):
        cluster = [doubled[i]]
        j = i + 1
        while j < i + len(sorted_points) and doubled[j]['lon'] - doubled[i]['lon'] <= 10:
            cluster.append(doubled[j])
            j += 1
        if len(cluster) >= 3:
            key = tuple(sorted(p['id'] for p in cluster))
            if key not in seen:
                seen.add(key)
                patterns.append({'type': 'stellium_orb', 'label': 'Tight Stellium', 'span': cluster[-1]['lon'] - cluster[0]['lon'], 'points': list(key)})

    unique = []
    keys = set()
    for item in patterns:
        key = (item['type'], tuple(sorted(item.get('points', []))), item.get('sign'))
        if key not in keys:
            unique.append(item)
            keys.add(key)
    return unique


def distribution(points):
    res = {
        'elements': {'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0},
        'modes': {'Cardinal': 0, 'Fixed': 0, 'Mutable': 0},
        'hemispheres': {'east': 0, 'west': 0, 'above': 0, 'below': 0},
    }
    for p in points:
        if p['id'] not in DEFAULT_EVENT_PLANETS:
            continue
        sign = p['sign']
        if sign in SIGN_ELEMENTS:
            res['elements'][SIGN_ELEMENTS[sign]] += 1
        if sign in SIGN_MODES:
            res['modes'][SIGN_MODES[sign]] += 1
        lon = p['lon']
        if 0 <= lon < 180:
            res['hemispheres']['below'] += 1
        else:
            res['hemispheres']['above'] += 1
        if 90 <= lon < 270:
            res['hemispheres']['west'] += 1
        else:
            res['hemispheres']['east'] += 1
    return res


def almuten_table(perchart):
    rows = []
    totals = {obj: 0 for obj in const.LIST_SEVEN_PLANETS}
    hylegic = [
        perchart.chart.getObject(const.SUN),
        perchart.chart.getObject(const.MOON),
        perchart.chart.getAngle(const.ASC),
        perchart.chart.getObject(const.PARS_FORTUNA),
        perchart.chart.getObject(const.SYZYGY),
    ]
    for point in hylegic:
        row = {'point': point.id, 'scores': {obj: 0 for obj in const.LIST_SEVEN_PLANETS}}
        dig = essential.getInfo(point.sign, point.signlon)
        for key, score in DIGNITY_SCORES.items():
            obj_id = dig.get(key)
            if obj_id in row['scores']:
                row['scores'][obj_id] += score
                totals[obj_id] += score
        rows.append(row)

    house_row = {'point': 'Houses', 'scores': {obj: 0 for obj in const.LIST_SEVEN_PLANETS}}
    for obj_id in const.LIST_SEVEN_PLANETS:
        obj = perchart.chart.getObject(obj_id)
        try:
            house = perchart.chart.houses.getObjectHouse(obj)
            score = HOUSE_SCORES.get(house.id, 0)
        except Exception:
            score = 0
        house_row['scores'][obj_id] += score
        totals[obj_id] += score
    rows.append(house_row)
    return {
        'rows': rows,
        'totals': totals,
        'winner': max(totals.items(), key=lambda item: item[1])[0] if totals else None,
    }


def extra_lots(perchart):
    points = {p['id']: p for p in chart_points(perchart, include_angles=True)}
    for lot in perchart.getPars(perchart.chart):
        points[lot.id] = object_to_dict(lot)
    res = []
    asc = points.get(const.ASC)
    fortuna = points.get(const.PARS_FORTUNA)
    spirit = points.get(PARS_SPIRIT)
    for lot in perchart.getPars(perchart.chart):
        obj = object_to_dict(lot)
        res.append({
            'id': obj['id'],
            'label': obj['id'],
            'lon': obj['lon'],
            'sign': obj['sign'],
            'signlon': obj['signlon'],
            'formula': 'flatlib arabicparts registry',
            'source': 'built_in',
        })
    for lot_id, label, planet_id in LOT_FORMULAS:
        planet = points.get(planet_id)
        if not asc or not planet:
            continue
        base = spirit if spirit else fortuna
        if not base:
            continue
        lon = norm360(asc['lon'] + planet['lon'] - base['lon'])
        res.append({
            'id': lot_id,
            'label': label,
            'lon': lon,
            'sign': sign_name_from_lon(lon),
            'signlon': lon % 30,
            'formula': 'ASC + planet - reference lot',
            'planet': planet_id,
            'reference': base['id'],
        })
    return res


def fixed_star_hits(perchart, orb=1.0):
    stars = perchart.getFixedStars()
    points = [p for p in chart_points(perchart, include_angles=True) if p['id'] in DEFAULT_EVENT_PLANETS or p['id'] in (const.ASC, const.MC, const.DESC, const.IC)]
    hits = []
    for star in stars:
        slon = safe_float(getattr(star, 'lon', 0))
        for p in points:
            delta = angle_distance(slon, p['lon'])
            if delta <= orb:
                hits.append({
                    'star': getattr(star, 'id', ''),
                    'point': p['id'],
                    'orb': delta,
                    'starLon': slon,
                    'pointLon': p['lon'],
                    'sign': sign_name_from_lon(slon),
                    'signlon': slon % 30,
                })
    return sorted(hits, key=lambda item: item['orb'])


def analyze_chart(data):
    params = base_params(data)
    perchart = PerChart(params)
    points = chart_points(perchart, include_angles=True)
    try:
        temperament = Temperament(perchart.chart).getScore()
    except Exception:
        traceback.print_exc()
        temperament = None
    return {
        'patterns': detect_patterns(points),
        'distribution': distribution(points),
        'almutem': almuten_table(perchart),
        'temperament': temperament,
        'extraLots': extra_lots(perchart),
        'fixedStarHits': fixed_star_hits(perchart, safe_float(data.get('fixedStarOrb', 1.0), 1.0)),
    }


def refine_crossing(func, a, b, iterations=24):
    fa = func(a)
    fb = func(b)
    if fa == 0:
        return a
    if fb == 0:
        return b
    for _ in range(iterations):
        mid = (a + b) / 2.0
        fm = func(mid)
        if (fa <= 0 <= fm) or (fa >= 0 >= fm):
            b = mid
            fb = fm
        else:
            a = mid
            fa = fm
    return (a + b) / 2.0


def calc_ingresses(start_jd, end_jd, zone, planets):
    events = []
    for body in planets:
        if body not in PLANET_SWISS_IDS:
            continue
        step = 0.25 if body == const.MOON else 1.0
        jd = start_jd
        prev_lon, _, _ = swe_lon(body, jd)
        prev_sign = sign_index(prev_lon)
        while jd < end_jd:
            nxt = min(jd + step, end_jd)
            lon, speed, _ = swe_lon(body, nxt)
            cur_sign = sign_index(lon)
            if cur_sign != prev_sign:
                def f(x):
                    l, _, _ = swe_lon(body, x)
                    return norm180(l - cur_sign * 30.0)
                hit_jd = refine_crossing(f, jd, nxt)
                hit_lon, hit_speed, _ = swe_lon(body, hit_jd)
                events.append({
                    **date_time_from_jd(hit_jd, zone),
                    'type': 'ingress',
                    'body': body,
                    'toSign': sign_name_from_lon(hit_lon),
                    'lon': hit_lon,
                    'speed': hit_speed,
                })
                prev_sign = cur_sign
            jd = nxt
    return sorted(events, key=lambda item: item['jd'])


def calc_stations(start_jd, end_jd, zone, planets):
    events = []
    for body in planets:
        if body not in PLANET_SWISS_IDS or body in (const.SUN, const.MOON):
            continue
        jd = start_jd
        _, prev_speed, _ = swe_lon(body, jd)
        while jd < end_jd:
            nxt = min(jd + 1.0, end_jd)
            lon, speed, _ = swe_lon(body, nxt)
            if (prev_speed <= 0 <= speed) or (prev_speed >= 0 >= speed):
                def f(x):
                    _, s, _ = swe_lon(body, x)
                    return s
                hit_jd = refine_crossing(f, jd, nxt)
                hit_lon, hit_speed, _ = swe_lon(body, hit_jd)
                events.append({
                    **date_time_from_jd(hit_jd, zone),
                    'type': 'station',
                    'body': body,
                    'direction': 'Direct' if hit_speed >= 0 else 'Retrograde',
                    'lon': hit_lon,
                    'speed': hit_speed,
                    'sign': sign_name_from_lon(hit_lon),
                    'signlon': hit_lon % 30,
                })
            prev_speed = speed
            jd = nxt
    return sorted(events, key=lambda item: item['jd'])


def moon_sun_elongation(jd):
    moon, _, _ = swe_lon(const.MOON, jd)
    sun, _, _ = swe_lon(const.SUN, jd)
    return norm360(moon - sun)


def calc_lunar_phases(start_jd, end_jd, zone):
    targets = [
        (0, 'New Moon'), (90, 'First Quarter'),
        (180, 'Full Moon'), (270, 'Last Quarter')
    ]
    events = []
    for target, label in targets:
        jd = start_jd
        prev = norm180(moon_sun_elongation(jd) - target)
        while jd < end_jd:
            nxt = min(jd + 0.5, end_jd)
            cur = norm180(moon_sun_elongation(nxt) - target)
            if (prev <= 0 <= cur) or (prev >= 0 >= cur):
                def f(x):
                    return norm180(moon_sun_elongation(x) - target)
                hit_jd = refine_crossing(f, jd, nxt)
                moon_lon, _, _ = swe_lon(const.MOON, hit_jd)
                sun_lon, _, _ = swe_lon(const.SUN, hit_jd)
                events.append({
                    **date_time_from_jd(hit_jd, zone),
                    'type': 'lunar_phase',
                    'phase': label,
                    'moonLon': moon_lon,
                    'sunLon': sun_lon,
                    'sign': sign_name_from_lon(moon_lon),
                    'signlon': moon_lon % 30,
                })
            prev = cur
            jd = nxt
    return sorted(events, key=lambda item: item['jd'])


def eclipse_type(retflag, lunar=False):
    types = []
    if retflag & swisseph.ECL_TOTAL:
        types.append('total')
    if retflag & swisseph.ECL_ANNULAR:
        types.append('annular')
    if retflag & getattr(swisseph, 'ECL_ANNULAR_TOTAL', 0):
        types.append('hybrid')
    if retflag & swisseph.ECL_PARTIAL:
        types.append('partial')
    if lunar and retflag & swisseph.ECL_PENUMBRAL:
        types.append('penumbral')
    return '/'.join(types) if types else 'eclipse'


def calc_eclipses(start_jd, end_jd, zone):
    events = []
    jd = start_jd - 1
    while True:
        ret, tret = swisseph.sol_eclipse_when_glob(jd, swisseph.FLG_SWIEPH, 0, False)
        e_jd = tret[0]
        if e_jd > end_jd:
            break
        if e_jd >= start_jd:
            sun_lon, _, _ = swe_lon(const.SUN, e_jd)
            events.append({
                **date_time_from_jd(e_jd, zone),
                'type': 'solar_eclipse',
                'eclipseType': eclipse_type(ret),
                'body': const.SUN,
                'lon': sun_lon,
                'sign': sign_name_from_lon(sun_lon),
                'signlon': sun_lon % 30,
            })
        jd = e_jd + 1
    jd = start_jd - 1
    while True:
        ret, tret = swisseph.lun_eclipse_when(jd, swisseph.FLG_SWIEPH, 0, False)
        e_jd = tret[0]
        if e_jd > end_jd:
            break
        if e_jd >= start_jd:
            moon_lon, _, _ = swe_lon(const.MOON, e_jd)
            events.append({
                **date_time_from_jd(e_jd, zone),
                'type': 'lunar_eclipse',
                'eclipseType': eclipse_type(ret, lunar=True),
                'body': const.MOON,
                'lon': moon_lon,
                'sign': sign_name_from_lon(moon_lon),
                'signlon': moon_lon % 30,
            })
        jd = e_jd + 1
    return sorted(events, key=lambda item: item['jd'])


def calc_daily_positions(start_jd, end_jd, zone, planets, max_days=370):
    rows = []
    days = int(math.floor(end_jd - start_jd)) + 1
    if days > max_days:
        days = max_days
    for idx in range(days):
        jd = start_jd + idx
        row = date_time_from_jd(jd, zone)
        row['positions'] = {}
        for body in planets:
            if body not in PLANET_SWISS_IDS:
                continue
            lon, speed, xx = swe_lon(body, jd)
            row['positions'][body] = {
                'lon': lon,
                'sign': sign_name_from_lon(lon),
                'signlon': lon % 30,
                'speed': speed,
                'retrograde': speed < 0,
                'lat': xx[1],
                'distance': xx[2],
            }
        rows.append(row)
    return rows


def calc_transit_aspects(base, start_jd, end_jd, zone, planets, natal_points, aspects, max_hits=600):
    try:
        perchart = PerChart(base)
    except Exception:
        return []
    natal = {p['id']: p for p in chart_points(perchart, include_angles=True) if p['id'] in natal_points}
    events = []
    for t_body in planets:
        if t_body not in PLANET_SWISS_IDS:
            continue
        for n_id, n_point in natal.items():
            for aspect in aspects:
                target = float(aspect)
                jd = start_jd
                lon, _, _ = swe_lon(t_body, jd)
                prev = signed_aspect_delta(lon, n_point['lon'], target)
                while jd < end_jd and len(events) < max_hits:
                    nxt = min(jd + (0.25 if t_body == const.MOON else 1.0), end_jd)
                    cur_lon, _, _ = swe_lon(t_body, nxt)
                    cur = signed_aspect_delta(cur_lon, n_point['lon'], target)
                    if (prev <= 0 <= cur) or (prev >= 0 >= cur):
                        def f(x):
                            l, _, _ = swe_lon(t_body, x)
                            return signed_aspect_delta(l, n_point['lon'], target)
                        hit_jd = refine_crossing(f, jd, nxt)
                        hit_lon, hit_speed, _ = swe_lon(t_body, hit_jd)
                        events.append({
                            **date_time_from_jd(hit_jd, zone),
                            'type': 'transit_aspect',
                            'transitBody': t_body,
                            'natalPoint': n_id,
                            'aspect': target,
                            'orb': abs(signed_aspect_delta(hit_lon, n_point['lon'], target)),
                            'lon': hit_lon,
                            'speed': hit_speed,
                            'sign': sign_name_from_lon(hit_lon),
                            'signlon': hit_lon % 30,
                        })
                    prev = cur
                    jd = nxt
    return sorted(events, key=lambda item: item['jd'])


def calc_rise_set(start_jd, data, planets):
    geopos = [
        geo_to_degree(data.get('lon', '0e00'), 'e', 'w'),
        geo_to_degree(data.get('lat', '0n00'), 'n', 's'),
        safe_float(data.get('altitude', 0.0), 0.0),
    ]
    rows = []
    zero = math.floor(start_jd - 0.5) + 0.5
    for body in planets:
        if body not in PLANET_SWISS_IDS:
            continue
        item = {'body': body}
        for key, flag in (
            ('rise', swisseph.CALC_RISE),
            ('set', swisseph.CALC_SET),
            ('upperTransit', swisseph.CALC_MTRANSIT),
            ('lowerTransit', swisseph.CALC_ITRANSIT),
        ):
            try:
                ret, tret = swisseph.rise_trans(zero, PLANET_SWISS_IDS[body], flag, geopos, 0.0, 0.0, swisseph.FLG_SWIEPH)
                item[key] = date_time_from_jd(tret[0], data.get('zone', '+00:00'))
                item[key]['retflag'] = ret
            except Exception as exc:
                item[key] = {'err': str(exc)}
        rows.append(item)
    return rows


def calc_phenomena(start_jd, planets):
    rows = []
    for body in planets:
        if body not in PLANET_SWISS_IDS:
            continue
        try:
            attr = swisseph.pheno_ut(start_jd, PLANET_SWISS_IDS[body], swisseph.FLG_SWIEPH)
            rows.append({
                'body': body,
                'phaseAngle': attr[0],
                'phase': attr[1],
                'elongation': attr[2],
                'apparentDiameter': attr[3],
                'magnitude': attr[4],
            })
        except Exception as exc:
            rows.append({'body': body, 'err': str(exc)})
    return rows


def calc_heliacal(start_jd, data, planets):
    geopos = [
        geo_to_degree(data.get('lon', '0e00'), 'e', 'w'),
        geo_to_degree(data.get('lat', '0n00'), 'n', 's'),
        safe_float(data.get('altitude', 0.0), 0.0),
    ]
    atmo = [1013.25, 15.0, 40.0, 0.25]
    observer = [36.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    rows = []
    for body in planets:
        if body not in (const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN):
            continue
        item = {'body': body}
        for key, event in (('rising', swisseph.HELIACAL_RISING), ('setting', swisseph.HELIACAL_SETTING)):
            try:
                tret = swisseph.heliacal_ut(start_jd, geopos, atmo, observer, body, event, swisseph.FLG_SWIEPH | swisseph.HELFLAG_HIGH_PRECISION)
                jd = tret[0] if isinstance(tret, (list, tuple)) else tret
                item[key] = date_time_from_jd(jd, data.get('zone', '+00:00'))
            except Exception as exc:
                item[key] = {'err': str(exc)}
        rows.append(item)
    return rows


def build_ephemeris(data):
    params = base_params(data)
    start_date = data.get('startDate') or data.get('date')
    end_date = data.get('endDate') or start_date
    start_time = data.get('startTime', '00:00:00')
    end_time = data.get('endTime', '23:59:59')
    start_dt = Datetime(start_date, start_time, params.get('zone', '+00:00'))
    end_dt = Datetime(end_date, end_time, params.get('zone', '+00:00'))
    start_jd = start_dt.jd
    end_jd = max(end_dt.jd, start_jd + 1)
    if end_jd - start_jd > 732:
        end_jd = start_jd + 732
    planets = data.get('planets') or DEFAULT_EVENT_PLANETS
    natal_points = data.get('natalPoints') or DEFAULT_NATAL_POINTS
    aspects = data.get('aspects') or [0, 60, 90, 120, 180]
    include_transits = to_bool(data.get('includeTransits'), True)
    return {
        'params': {
            'startDate': date_time_from_jd(start_jd, params.get('zone', '+00:00')),
            'endDate': date_time_from_jd(end_jd, params.get('zone', '+00:00')),
            'planets': planets,
            'natalPoints': natal_points,
            'aspects': aspects,
        },
        'dailyPositions': calc_daily_positions(start_jd, end_jd, params.get('zone', '+00:00'), planets),
        'ingresses': calc_ingresses(start_jd, end_jd, params.get('zone', '+00:00'), planets),
        'stations': calc_stations(start_jd, end_jd, params.get('zone', '+00:00'), planets),
        'lunarPhases': calc_lunar_phases(start_jd, end_jd, params.get('zone', '+00:00')),
        'eclipses': calc_eclipses(start_jd, end_jd, params.get('zone', '+00:00')),
        'transitAspects': calc_transit_aspects(params, start_jd, end_jd, params.get('zone', '+00:00'), planets, natal_points, aspects) if include_transits else [],
        'riseSet': calc_rise_set(start_jd, params, planets),
        'phenomena': calc_phenomena(start_jd, planets),
        'heliacal': calc_heliacal(start_jd, params, planets),
    }


def progression_date(base_dt, target_dt, method):
    age_days = target_dt.jd - base_dt.jd
    if method == 'secondary':
        delta_days = age_days / 365.2425
    elif method == 'tertiary':
        delta_days = age_days / 27.321661
    elif method == 'minor':
        delta_days = age_days / 12.3685 / 365.2425
    else:
        delta_days = age_days / 365.2425
    return base_dt.jd + delta_days


def aspects_between(points_a, points_b, asp_list=None, orb=1.5):
    asp_list = asp_list or [0, 60, 90, 120, 180]
    rows = []
    for pa in points_a:
        if pa['id'] not in DEFAULT_EVENT_PLANETS and pa['id'] not in (const.ASC, const.MC):
            continue
        for pb in points_b:
            if pb['id'] not in DEFAULT_EVENT_PLANETS and pb['id'] not in (const.ASC, const.MC):
                continue
            for asp in asp_list:
                delta = abs(angle_distance(pa['lon'], pb['lon']) - float(asp))
                if delta <= orb:
                    rows.append({'a': pa['id'], 'b': pb['id'], 'aspect': asp, 'orb': delta})
    return sorted(rows, key=lambda item: item['orb'])


def build_progressions(data):
    params = base_params(data)
    target_date = data.get('targetDate') or data.get('datetime') or data.get('date')
    target_time = data.get('targetTime') or '12:00:00'
    if ' ' in target_date:
        date_part, time_part = target_date.split(' ', 1)
        target_date = date_part
        target_time = time_part
    natal_dt = dt_from_data(params)
    target_dt = Datetime(target_date, target_time, params.get('zone', '+00:00'))
    natal_chart = PerChart(params)
    natal_points = chart_points(natal_chart, include_angles=True)
    methods = []
    for method, label in (
        ('secondary', 'Secondary Progression'),
        ('tertiary', 'Tertiary Progression'),
        ('minor', 'Minor Progression'),
    ):
        jd = progression_date(natal_dt, target_dt, method)
        p_params = chart_params_from_jd(params, jd)
        p_chart = PerChart(p_params)
        p_points = chart_points(p_chart, include_angles=True)
        methods.append({
            'method': method,
            'label': label,
            'progressedDate': date_time_from_jd(jd, params.get('zone', '+00:00')),
            'positions': p_points,
            'aspectsToNatal': aspects_between(p_points, natal_points, data.get('aspects') or [0, 60, 90, 120, 180], safe_float(data.get('orb', 1.5), 1.5)),
        })
    return {
        'target': date_time_from_jd(target_dt.jd, params.get('zone', '+00:00')),
        'ageDays': target_dt.jd - natal_dt.jd,
        'methods': methods,
    }


def build_return_timeline(data):
    params = base_params(data)
    count = max(1, min(int(data.get('count', 10)), 40))
    start_year = int(data.get('startYear') or str(data.get('date', '2000/01/01')).replace('-', '/').split('/')[0])
    perchart = PerChart(params)
    sun = perchart.chart.getObject(const.SUN)
    moon = perchart.chart.getObject(const.MOON)
    rows = []
    for year in range(start_year, start_year + count):
        solar_seed = Datetime('{0}/01/01'.format(year), params.get('time', '12:00:00'), params.get('zone', '+00:00'))
        solar_dt = dateSolarReturn(solar_seed, sun.lon, perchart.zodiacal)
        lunar_seed = Datetime('{0}/01/01'.format(year), params.get('time', '12:00:00'), params.get('zone', '+00:00'))
        lunar_dt = dateLunarReturn(lunar_seed, moon.lon, perchart.zodiacal)
        solar_params = chart_params_from_jd(params, solar_dt.jd)
        lunar_params = chart_params_from_jd(params, lunar_dt.jd)
        try:
            solar_perchart = PerChart(solar_params)
            solar_asc = object_to_dict(solar_perchart.chart.getAngle(const.ASC))
        except Exception:
            solar_asc = None
        try:
            lunar_perchart = PerChart(lunar_params)
            lunar_asc = object_to_dict(lunar_perchart.chart.getAngle(const.ASC))
        except Exception:
            lunar_asc = None
        rows.append({
            'year': year,
            'solarReturn': date_time_from_jd(solar_dt.jd, params.get('zone', '+00:00')),
            'lunarReturn': date_time_from_jd(lunar_dt.jd, params.get('zone', '+00:00')),
            'solarAsc': solar_asc,
            'lunarAsc': lunar_asc,
        })
    return {'rows': rows}


def build_harmonic(data):
    params = base_params(data)
    harmonic = max(1, min(int(data.get('harmonic', 9)), 360))
    perchart = PerChart(params)
    positions = []
    for p in chart_points(perchart, include_angles=True):
        if p['id'] not in DEFAULT_EVENT_PLANETS and p['id'] not in (const.ASC, const.MC, const.PARS_FORTUNA):
            continue
        lon = norm360(p['lon'] * harmonic)
        positions.append({
            'id': p['id'],
            'natalLon': p['lon'],
            'lon': lon,
            'sign': sign_name_from_lon(lon),
            'signlon': lon % 30,
            'harmonic': harmonic,
        })
    aspects = aspects_between(positions, positions, [0], safe_float(data.get('orb', 2.0), 2.0))
    aspects = [a for a in aspects if a['a'] != a['b']]
    return {'harmonic': harmonic, 'positions': positions, 'conjunctions': aspects[:120]}


def build_relative_score(data):
    from astrostudy.modern.chartcomp import ChartComp
    params = dict(data or {})
    params['relative'] = 0
    inner = dict(params.get('inner') or {})
    outer = dict(params.get('outer') or {})
    hsys = params.get('hsys', 0)
    zodiacal = params.get('zodiacal', 0)
    for item in (inner, outer):
        item['tradition'] = False
        item['predictive'] = False
        item['hsys'] = hsys
        item['zodiacal'] = zodiacal
    comp = ChartComp(inner, outer).compute()
    weights = {0: 6, 60: 3, 90: -4, 120: 4, 180: -5}
    score = 50
    highlights = []
    challenges = []
    flat = []
    for group_key in ('outToInAsp', 'inToOutAsp'):
        for row in comp.get(group_key, []):
            key = row.get('id')
            for asp in row.get('objects', []):
                deg = int(asp.get('aspect', -999))
                weight = weights.get(deg, 0)
                orb = safe_float(asp.get('orb', asp.get('delta', 0)), 0)
                impact = weight * max(0.2, 1.0 - min(orb, 8) / 8.0)
                score += impact
                item = {
                    'a': key,
                    'b': asp.get('id') or asp.get('idB') or asp.get('obj') or '',
                    'aspect': deg,
                    'orb': orb,
                    'impact': impact,
                    'direction': group_key,
                }
                flat.append(item)
                if impact > 0:
                    highlights.append(item)
                elif impact < 0:
                    challenges.append(item)
    return {
        'score': max(0, min(100, round(score, 1))),
        'aspects': sorted(flat, key=lambda item: abs(item['impact']), reverse=True)[:80],
        'highlights': sorted(highlights, key=lambda item: item['impact'], reverse=True)[:20],
        'challenges': sorted(challenges, key=lambda item: item['impact'])[:20],
        'raw': comp,
    }
