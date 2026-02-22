from flatlib import angle
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from astrostudy.helper import getChartObj

from astrostudy.helper import distance
from . import jieqiconst

def takeTime(obj):
    return obj['jdn']

class YearJieQi:

    def __init__(self, data):
        self.year = data['year']
        self.zone = data['zone']
        self.lat = data['lat']
        self.lon = data['lon']
        self.pos = GeoPos(self.lat, self.lon)
        self.ad = -1 if int(self.year) < 0 else 1

        if 'jieqis' in data.keys():
            jieqis = data['jieqis']
            if isinstance(jieqis, (list, tuple, set)):
                self.jieqis = set(jieqis)
            elif isinstance(jieqis, str):
                self.jieqis = set([jieqis]) if jieqis != '' else set()
            else:
                self.jieqis = set()
        else:
            self.jieqis = set()

        if 'seedOnly' in data.keys():
            raw = data['seedOnly']
            if isinstance(raw, str):
                self.seedOnly = raw.lower() in ('1', 'true', 'yes', 'on')
            else:
                self.seedOnly = bool(raw)
        else:
            self.seedOnly = False

        if 'hsys' in data.keys():
            self.hsys = data['hsys']
        else:
            self.hsys = 0

        if 'zodiacal' in data.keys():
            self.zodiacal = data['zodiacal']
        else:
            self.zodiacal = 0

        if 'doubingSu28' in data.keys():
            self.doubingSu28 = data['doubingSu28']
        else:
            self.doubingSu28 = 0

        self.params = {}
        self.params['zone'] = self.zone
        self.params['lat'] = self.lat
        self.params['lon'] = self.lon
        self.params['hsys'] = self.hsys
        self.params['zodiacal'] = self.zodiacal
        self.params['doubingSu28'] = self.doubingSu28
        self.params['predictive'] = False

    def compute(self):
        if self.seedOnly:
            return {
                'jieqi24': self.computeJieQi(False),
                'charts': {}
            }
        return self.computeJieQi(True)

    def filterJieqi24(self, jieqi24):
        if jieqi24 is None or len(jieqi24) < 24:
            return jieqi24
        res = []
        if jieqi24[23]['jieqi'] == '小寒':
            res.append(jieqi24[23])
            for i in range(0, 23):
                res.append(jieqi24[i])
        else:
            return jieqi24
        return res

    def approach(self, dt, jieqiLon):
        chart = Chart(dt, self.pos, const.TROPICAL, hsys=const.HOUSES_WHOLE_SIGN)
        sun = chart.getObject(const.SUN)
        delta = distance(jieqiLon, sun.lon) + 1/7200
        deltatm = delta / sun.lonspeed
        newjd = dt.jd + deltatm
        newtm = Datetime.fromJD(newjd, self.zone)
        while abs(delta) > 0.0003:
            chart = Chart(newtm, self.pos, const.TROPICAL, hsys=const.HOUSES_WHOLE_SIGN)
            sun = chart.getObject(const.SUN)
            delta = distance(jieqiLon, sun.lon) + 1/7200
            deltatm = delta / sun.lonspeed
            newjd = newtm.jd + deltatm
            newtm = Datetime.fromJD(newjd, self.zone)
        return newtm

    def computeJieQi(self, needChart):
        jieqicharts = {}
        jieqi24 = []
        tmpjieqi24 = {} if needChart and len(self.jieqis) > 0 else None
        res = {}

        terms = list(jieqiconst.JieQiLon.keys())
        if len(self.jieqis) > 0:
            terms = [key for key in terms if key in self.jieqis]

        for key in terms:
            jieqi = jieqiconst.JieQiLon[key]
            date = '{0}/{1}'.format(self.year, jieqi['start'])
            dateTime = Datetime(date, '00:00', self.zone)
            newtm = self.approach(dateTime, jieqi['lon'])

            dtstr = newtm.toCNString()
            obj = {
                'ord': jieqi['ord'],
                'jieqi': key,
                'jie': jieqi['jie'],
                'time': dtstr,
                'tm': newtm,
                'jdn': newtm.jd,
                'ad': newtm.ad()
            }
            jieqi24.append(obj)

            if tmpjieqi24 is not None:
                parts = dtstr.split(' ')
                tmpjieqi24[key] = {
                    'date': parts[0],
                    'time': parts[1]
                }

        jieqi24.sort(key=takeTime)
        jieqi24 = self.filterJieqi24(jieqi24)
        if self.pos.lat < 0:
            for jq in jieqi24:
                jqname = jq['jieqi']
                jq['jieqi'] = jieqiconst.SouthEarthJieQi[jqname]

        if needChart == True:
            res['jieqi24'] = jieqi24

            if tmpjieqi24 is not None:
                for key in self.jieqis:
                    if key in tmpjieqi24.keys():
                        self.params['date'] = tmpjieqi24[key]['date']
                        self.params['time'] = tmpjieqi24[key]['time']
                        self.params['name'] = key
                        from astrostudy.perchart import PerChart
                        perchart = PerChart(self.params)
                        jieqicharts[key] = getChartObj(self.params, perchart)

            res['charts'] = jieqicharts
            return res
        else:
            return jieqi24

    def computeOneJieQi(self, jieqi):
        date = '{0}/{1}'.format(self.year, jieqi['start'])
        dateTime = Datetime(date, '00:00', self.zone)
        newtm = self.approach(dateTime, jieqi['lon'])

        dtstr = newtm.toCNString()
        parts = dtstr.split(' ')

        obj = {
            'ord': jieqi['ord'],
            'time': dtstr,
            'date': parts[0],
            'tm': newtm,
            'jdn': newtm.jd,
            'jie': jieqi['jie'],
            'ad': newtm.ad()
        }

        return obj

    def computeOneJieQiByName(self, jieqi):
        jq = jieqiconst.JieQiLon[jieqi]
        return self.computeOneJieQi(jq)
