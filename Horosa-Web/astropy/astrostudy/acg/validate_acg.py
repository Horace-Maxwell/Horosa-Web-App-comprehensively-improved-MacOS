"""
占星地图（ACG）算法对齐 / 回归自检 —— 金标准。

思路：ACG 四轴线是天文学定义——MC/IC 线 = 行星正在上/下中天（位于本地子午线）；
ASC/DESC 线 = 行星正在升/落（真高度=0）。用 Swiss Ephemeris **权威的地平坐标函数
`swisseph.azalt()`** 反验 ACGraph 算出的线是否满足这些定义。`azalt` 内部用它自己的
恒星时，与 ACGraph 的 GMST/公式**完全独立**，因此这是对算法的独立精度校验；又因
本项目与同类专业软件都用同一套 Swiss Ephemeris，本检验即"与业界标准对齐"。

运行（用内嵌运行时 python，PYTHONPATH 由本脚本自行补好）：
    runtime/mac/python/bin/python3 Horosa-Web/astropy/astrostudy/acg/validate_acg.py
期望：所有行星 ASC/DESC 真高度≈0、MC/IC 方位角≈子午线，worst < 1e-3°（实测 0.00000°）。
退出码 0=通过，1=失败（可用于 CI / 发布前 gate）。
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))          # .../Horosa-Web/astropy/astrostudy/acg
_WEB = os.path.abspath(os.path.join(_HERE, '..', '..', '..'))  # .../Horosa-Web
for _p in (os.path.join(_WEB, 'flatlib-ctrad2'), os.path.join(_WEB, 'astropy'), os.path.join(_WEB, 'vendor')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import swisseph
from astrostudy.acg.ACGraph import ACGraph
from flatlib import const

MAIN = [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
        const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO]

TOL = 1e-3  # degrees

CASES = [
    ({'date': '1990/01/15', 'time': '12:00:00', 'zone': '+08:00', 'lat': '39n54', 'lon': '116e23', 'ad': 1},
     '1990-01-15 12:00 +08 Beijing'),
    ({'date': '1985/07/13', 'time': '06:45:00', 'zone': '-03:00', 'lat': '23s33', 'lon': '46w38', 'ad': 1},
     '1985-07-13 06:45 -03 Sao Paulo (S.hemi)'),
    ({'date': '2001/09/11', 'time': '08:46:00', 'zone': '-04:00', 'lat': '40n43', 'lon': '74w00', 'ad': 1},
     '2001-09-11 08:46 -04 New York'),
]


def _merid_dev(az):
    a = az % 180.0
    return min(a, 180.0 - a)


def _alt_err(jd, xin, pts):
    errs = []
    n = len(pts)
    for idx in (1, n // 4, n // 2, 3 * n // 4, n - 2):
        q = pts[idx]
        _, talt, _ = swisseph.azalt(jd, swisseph.ECL2HOR, [q['lon'], q['lat'], 0], 0, 0, xin)
        errs.append(abs(talt))
    return max(errs)


def check(data, label):
    acg = ACGraph(data)
    res = acg.compute()
    jd = acg.jd
    worst = 0.0
    rows = []
    for pid in MAIN:
        p = res['planets'][pid]
        xin = [p['lon'], p['lat'], 1.0]
        asc_e = _alt_err(jd, xin, p['lines']['asc'])
        dsc_e = _alt_err(jd, xin, p['lines']['desc'])
        azmc, _, _ = swisseph.azalt(jd, swisseph.ECL2HOR, [p['lines']['mc']['lon'], 20.0, 0], 0, 0, xin)
        azic, _, _ = swisseph.azalt(jd, swisseph.ECL2HOR, [p['lines']['ic']['lon'], 20.0, 0], 0, 0, xin)
        mc_d, ic_d = _merid_dev(azmc), _merid_dev(azic)
        worst = max(worst, asc_e, dsc_e, mc_d, ic_d)
        rows.append('  %-12s ASC|alt|=%.5f DESC|alt|=%.5f  MC dev=%.5f IC dev=%.5f'
                    % (pid, asc_e, dsc_e, mc_d, ic_d))
    print('\n[%s] jd=%.5f' % (label, jd))
    print('\n'.join(rows))
    print('  worst = %.6f deg' % worst)
    return worst


def main():
    overall = 0.0
    for data, label in CASES:
        overall = max(overall, check(data, label))
    ok = overall < TOL
    print('\n==== ACG alignment %s (worst %.6f deg, tol %g) ====' % ('PASS' if ok else 'FAIL', overall, TOL))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
