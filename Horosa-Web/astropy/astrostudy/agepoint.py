# astrostudy/agepoint.py
# Huber 年龄推进点（Age Point）：年龄点自上升点起，沿 12 个 Koch 宫顺行，每宫 6 年、72 年一周，
# 宫内按黄道跨度线性插值。报每岁 AP 落座/落宫 + 与本命星合相(orb 1°)。
import swisseph
from flatlib import const

PLANET_POINTS = [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN]


def _norm360(x):
    return (x % 360 + 360) % 360


def _koch_cusps(jd, lat, lon):
    """ 返回 (asc, [12 个 Koch 宫头黄经 house1..house12])。 """
    res = swisseph.houses_ex2(jd, float(lat), float(lon), b'K', 0)
    cusps = list(res[0])
    ascmc = list(res[1])
    if len(cusps) >= 13:
        kc = [float(cusps[i]) for i in range(1, 13)]   # 1-indexed [1..12]
    else:
        kc = [float(cusps[i]) for i in range(0, 12)]   # 0-indexed [0..11]
    asc = float(ascmc[0]) if ascmc else kc[0]
    return asc, kc


def compute(perchart, max_age=72):
    chart = perchart.getChart()
    jd = chart.date.jd
    asc, kc = _koch_cusps(jd, perchart.pos.lat, perchart.pos.lon)

    natal = {}
    for pid in PLANET_POINTS:
        try:
            o = chart.getObject(pid)
            if o is not None:
                natal[pid] = o.lon
        except Exception:
            pass

    points = []
    for age in range(0, max_age + 1):
        houseIdx = int(age // 6) % 12          # 0-based house index the AP is in
        frac = (age % 6) / 6.0                 # progress through that house
        startCusp = kc[houseIdx]
        endCusp = kc[(houseIdx + 1) % 12]
        span = _norm360(endCusp - startCusp)
        apLon = _norm360(startCusp + frac * span)
        aspectTo = None
        for pid, plon in natal.items():
            d = abs(_norm360(apLon - plon))
            d = min(d, 360 - d)
            if d <= 1.0:
                aspectTo = pid
                break
        points.append({
            'age': age,
            'apLon': round(apLon, 2),
            'sign': const.LIST_SIGNS[int(apLon / 30) % 12],
            'signlon': round(apLon % 30, 2),
            'house': houseIdx + 1,
            'aspectTo': aspectTo,
            'aspect': '合' if aspectTo else None,
            'cuspCrossing': frac == 0.0,        # 进入新宫的整岁
        })
    return {
        'asc': round(asc, 2),
        'kochCusps': [round(c, 2) for c in kc],
        'maxAge': max_age,
        'points': points,
    }
