
# 129 年系统（129 Year System）：七政各管其「小年」，一轮共 129 年。
# 真正的「129 年」体系（非十年大运的 129 月递归）。镜像 firdaria.py 的主限 + 等分子限结构。
# succession 序为实验性，待进一步核验。
from flatlib import const
from flatlib.datetime import Datetime

# 各行星小年（年）。Σ = 19+25+30+12+15+8+20 = 129。
MINOR_YEARS = {
    const.SUN: 19,
    const.MOON: 25,
    const.SATURN: 30,
    const.JUPITER: 12,
    const.MARS: 15,
    const.VENUS: 8,
    const.MERCURY: 20,
}

# 主限/子限行进序列（实验性，待校准）。
SEQUENCE = [
    const.SUN,
    const.MOON,
    const.SATURN,
    const.JUPITER,
    const.MARS,
    const.VENUS,
    const.MERCURY,
]
SEQ_LEN = len(SEQUENCE)
SEQ_INDEX = {p: i for i, p in enumerate(SEQUENCE)}


def _rotate(start):
    i = SEQ_INDEX.get(start, 0)
    return SEQUENCE[i:] + SEQUENCE[:i]


def compute(chart):
    res = []
    zone = chart.date.utcoffset
    # 起始星 = sect 光体（日昼 ☉ / 夜 ☽）。
    start = const.SUN if chart.isDiurnal() else const.MOON
    maindirect = _rotate(start)
    date = Datetime.fromJD(chart.date.jd, zone)
    for dir in maindirect:
        dirobj = {
            'mainDirect': dir,
            'subDirect': []
        }
        # 子限：把该主限期(minor years)等分为 7 段，从该星索引起循环。
        j = SEQ_INDEX[dir]
        avg = MINOR_YEARS[dir] / SEQ_LEN
        deltaday = avg * 365.2421904
        k = 0
        while k < SEQ_LEN:
            parts = date.toCNString().split(' ')
            subobj = {
                'subDirect': SEQUENCE[j],
                'date': parts[0]
            }
            dirobj['subDirect'].append(subobj)
            jd = date.jd + deltaday
            date = Datetime.fromJD(jd, zone)
            j = (j + 1) % SEQ_LEN
            k = k + 1
        res.append(dirobj)
    return res
