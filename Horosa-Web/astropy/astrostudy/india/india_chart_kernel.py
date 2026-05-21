import math
import traceback

from flatlib import angle
from flatlib import const
from flatlib import utils
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.dignities import essential
from flatlib.dignities import tables
from flatlib.ephem import eph
from flatlib.ephem import swe


INDIA_AYANAMSA_MODES = {
    'lahiri': {
        'key': 'lahiri',
        'label': 'Lahiri / Chitrapaksha',
        'mode': swe.SE_SIDM_LAHIRI,
    },
    'raman': {
        'key': 'raman',
        'label': 'Raman',
        'mode': swe.SE_SIDM_RAMAN,
    },
    'krishnamurti': {
        'key': 'krishnamurti',
        'label': 'Krishnamurti / KP',
        'mode': swe.SE_SIDM_KRISHNAMURTI,
    },
    'krishnamurti_vp291': {
        'key': 'krishnamurti_vp291',
        'label': 'Krishnamurti VP291',
        'mode': swe.SE_SIDM_KRISHNAMURTI_VP291,
    },
    'yukteshwar': {
        'key': 'yukteshwar',
        'label': 'Yukteshwar',
        'mode': swe.SE_SIDM_YUKTESHWAR,
    },
    'true_citra': {
        'key': 'true_citra',
        'label': 'True Citra',
        'mode': swe.SE_SIDM_TRUE_CITRA,
    },
    'true_revati': {
        'key': 'true_revati',
        'label': 'True Revati',
        'mode': swe.SE_SIDM_TRUE_REVATI,
    },
    'fagan_bradley': {
        'key': 'fagan_bradley',
        'label': 'Fagan/Bradley',
        'mode': swe.SE_SIDM_FAGAN_BRADLEY,
    },
}

INDIA_AYANAMSA_ALIASES = {
    'chitrapaksha': 'lahiri',
    'lahiri_1940': 'lahiri',
    'kp': 'krishnamurti',
    'krishnamurti-vp291': 'krishnamurti_vp291',
    'truecitra': 'true_citra',
    'true-citra': 'true_citra',
    'truerevati': 'true_revati',
    'true-revati': 'true_revati',
    'fagan': 'fagan_bradley',
    'fagan-bradley': 'fagan_bradley',
}

INDIA_HOUSE_SYSTEMS = {
    0: {
        'key': 'whole_sign',
        'label': 'Whole Sign / Rashi',
        'flatlib': const.HOUSES_WHOLE_SIGN,
        'base': const.HOUSES_PLACIDUS,
    },
    5: {
        'key': 'equal_lagna',
        'label': 'Equal / Lagna Bhava',
        'flatlib': const.HOUSES_EQUAL,
        'base': const.HOUSES_PLACIDUS,
    },
    7: {
        'key': 'sripati',
        'label': 'Sripati',
        'flatlib': const.HOUSES_SRIPATI,
        'base': const.HOUSES_SRIPATI,
    },
    3: {
        'key': 'kp_placidus',
        'label': 'KP / Placidus',
        'flatlib': const.HOUSES_PLACIDUS,
        'base': const.HOUSES_PLACIDUS,
    },
}

INDIA_HOUSE_ALIASES = {
    'whole': 0,
    'whole_sign': 0,
    'rashi': 0,
    'bhava_chalit': 5,
    'equal': 5,
    'equal_lagna': 5,
    'lagna_equal': 5,
    'sripati': 7,
    'placidus': 3,
    'kp': 3,
    'kp_placidus': 3,
}

INDIA_OBJECTS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO,
    const.CHIRON, const.NORTH_NODE, const.SOUTH_NODE, const.SYZYGY, const.PARS_FORTUNA,
    const.DARKMOON, const.PURPLE_CLOUDS,
]


def normalize_ayanamsa(value):
    if value is None or value == '':
        value = 'lahiri'
    key = str(value).strip().lower()
    key = INDIA_AYANAMSA_ALIASES.get(key, key)
    return INDIA_AYANAMSA_MODES.get(key, INDIA_AYANAMSA_MODES['lahiri'])


def normalize_house_system(value):
    if value is None or value == '':
        return 0, INDIA_HOUSE_SYSTEMS[0]
    if isinstance(value, str):
        key = value.strip().lower()
        if key in INDIA_HOUSE_ALIASES:
            code = INDIA_HOUSE_ALIASES[key]
            return code, INDIA_HOUSE_SYSTEMS[code]
        try:
            value = int(key)
        except Exception:
            return 0, INDIA_HOUSE_SYSTEMS[0]
    try:
        code = int(value)
    except Exception:
        code = 0
    if code not in INDIA_HOUSE_SYSTEMS:
        code = 0
    return code, INDIA_HOUSE_SYSTEMS[code]


def positive_distance(start, end):
    return (end - start + 360.0) % 360.0


def sorted_objects(values):
    return sorted(list(values), key=lambda item: getattr(item, 'lon', 0))


class IndiaChartKernel:
    def __init__(self, data):
        self.data = data
        self.time = data['time']
        self.zone = data['zone']
        self.lat = data['lat']
        self.lon = data['lon']
        self.tradition = False
        self.zodiacal = const.SIDEREAL
        self.southchart = False
        self.su28Mode = 0
        self.pdtype = data.get('pdtype', 0)
        self.pdMethod = data.get('pdMethod', 'india_kernel')
        self.pdTimeKey = data.get('pdTimeKey', 'Birth')
        self.isBC = False

        date = data['date']
        parts = date.split('/')
        if len(parts) == 1:
            parts = date.split('-')
        if len(parts) == 4:
            self.year = '-{0}'.format(parts[1])
            self.month = parts[2]
            self.day = parts[3]
        else:
            self.year = parts[0]
            self.month = parts[1]
            self.day = parts[2]
        self.date = '{0}/{1}/{2}'.format(self.year, self.month, self.day)

        if 'ad' in data:
            self.isBC = int(data.get('ad', 1)) != 1
            if self.isBC and self.date[0:1] != '-':
                self.date = '-{0}'.format(self.date)
                self.year = '-{0}'.format(self.year)
        if self.year[0:1] == '-':
            self.isBC = True

        self.dateTime = Datetime(self.date, self.time, self.zone)
        self.pos = GeoPos(self.lat, self.lon)

        self.siderealMode = normalize_ayanamsa(data.get('indiaAyanamsa', data.get('ayanamsa', data.get('siderealMode', 'lahiri'))))
        self.siderealModeKey = self.siderealMode['key']
        self.siderealModeLabel = self.siderealMode['label']
        self.ayanamsaValue = self._compute_ayanamsa_value()

        self.houseCode, self.houseSystem = normalize_house_system(data.get('indiaHsys', data.get('hsys', 0)))
        self.house = self.houseSystem['flatlib']
        self.houseLabel = self.houseSystem['label']

        self.objlists = [obj for obj in INDIA_OBJECTS if obj in swe.SWE_OBJECTS or obj in [const.SOUTH_NODE, const.SYZYGY, const.PARS_FORTUNA]]
        self.hasSun = const.SUN in self.objlists
        self.hasMoon = const.MOON in self.objlists

        self.chart = Chart(
            self.dateTime,
            self.pos,
            const.SIDEREAL,
            hsys=self.houseSystem['base'],
            IDs=self.objlists,
            needpars=True,
            sidereal_mode=self.siderealMode,
        )
        self.chart.hsys = self.house
        self._apply_india_houses()
        self.reinit()

    def _compute_ayanamsa_value(self):
        try:
            swe.setSiderealContext(self.siderealMode['mode'])
            swe.applySiderealMode()
            return swe.swisseph.get_ayanamsa_ut(self.dateTime.jd)
        except Exception:
            return None
        finally:
            swe.clearSiderealContext()

    def _apply_india_houses(self):
        if self.houseCode not in (0, 5):
            for house in self.chart.houses:
                house.hsys = self.house
            return

        asc = self.chart.getAngle(const.ASC)
        start_lon = math.floor(asc.lon / 30.0) * 30.0 if self.houseCode == 0 else asc.lon
        for house in self.chart.houses:
            house_num = int(house.id[5:])
            house.hsys = self.house
            house.size = 30.0
            house.relocate((start_lon + (house_num - 1) * 30.0) % 360.0)
            ra, decl = utils.eqCoords(house.lon, 0)
            house.ra = ra
            house.decl = decl
        self.chart.hsys = self.house

    def _house_for_lon(self, lon):
        houses = sorted(list(self.chart.houses), key=lambda item: int(item.id[5:]))
        for idx, house in enumerate(houses):
            next_house = houses[(idx + 1) % len(houses)]
            size = positive_distance(house.lon, next_house.lon)
            house.size = size if size > 0 else 30.0
            if positive_distance(house.lon, lon) < house.size:
                return house
        return houses[0] if houses else None

    def _assign_house(self, obj):
        house = self._house_for_lon(obj.lon)
        obj.house = house.id if house else None

    def reinit(self):
        self.isDiurnal = self.chart.isDiurnal()
        self.chart.hsys = self.house
        for house in self.chart.houses:
            house.planets = []
            house.ruler = None
            house.exalt = None

        asc = self.chart.getAngle(const.ASC)
        asc_sign_index = const.LIST_SIGNS.index(asc.sign)
        for index in range(12):
            sign = const.LIST_SIGNS[(asc_sign_index + index) % 12]
            house = self.chart.getHouse(const.LIST_HOUSES[index])
            try:
                ruler = tables.ESSENTIAL_DIGNITIES[sign]['ruler']
                exalt = tables.ESSENTIAL_DIGNITIES[sign]['exalt'][0]
                house.ruler = ruler
                house.exalt = exalt
            except Exception:
                pass

        for obj in list(self.chart.angles) + list(self.chart.objects) + list(self.chart.pars):
            self._assign_house(obj)
            try:
                obj.movedir = obj.movement()
            except Exception:
                obj.movedir = None
            try:
                obj.dignities = essential.getInfo(obj.sign, obj.signlon)
                obj.selfDignity = []
            except Exception:
                obj.dignities = {}
                obj.selfDignity = []

        for obj in self.chart.objects:
            if not getattr(obj, 'id', '').startswith('House') and getattr(obj, 'house', None):
                try:
                    self.chart.getHouse(obj.house).planets.append(obj.id)
                except Exception:
                    pass

    def getBirthStr(self):
        return '{0}-{1}-{2} {3}'.format(self.year, self.month, self.day, self.time)

    def getSunRiseTime(self):
        try:
            sunrise_jd = eph.lastSunrise(self.dateTime.jd + 0.5, self.pos.lat, self.pos.lon)
            dt = Datetime.fromJD(sunrise_jd, self.zone)
            text = dt.toCNString()
            parts = text.split(' ')
            return {
                'datetime': dt,
                'timeStr': parts[1] if len(parts) > 1 else text,
            }
        except Exception:
            return {
                'datetime': self.dateTime,
                'timeStr': '',
            }

    def getRiseSetTimes(self):
        def fmt(jd):
            dt = Datetime.fromJD(jd, self.zone)
            parts = dt.toCNString().split(' ')
            return parts[1] if len(parts) > 1 else dt.toCNString()

        try:
            sunrise = eph.lastSunrise(self.dateTime.jd + 0.5, self.pos.lat, self.pos.lon)
            sunset = eph.nextSunset(sunrise, self.pos.lat, self.pos.lon)
            return {
                'sunrise': fmt(sunrise),
                'sunset': fmt(sunset),
                'moonrise': '',
                'moonset': '',
                'source': 'swisseph.rise_trans',
            }
        except Exception:
            return {
                'sunrise': '',
                'sunset': '',
                'moonrise': '',
                'moonset': '',
                'source': 'swisseph.rise_trans',
            }

    def getChartObj(self):
        houses = sorted_objects(self.chart.houses)
        objs = sorted_objects(list(self.chart.objects) + list(self.chart.angles))
        rise_set = self.getRiseSetTimes()
        return {
            'zodiacal': self.zodiacal,
            'date': self.chart.orgdate,
            'geo': self.chart.pos,
            'hsys': self.houseLabel,
            'houses': houses,
            'objects': objs,
            'isDiurnal': self.isDiurnal,
            'antiscias': {},
            'stars': [],
            'orientOccident': {},
            'fixedStarSu28': [],
            'fixedStars': [],
            'signsRA': [],
            'signsRaDoubingSu28': [],
            'su28Adjust': {},
            'su28Virtual': [],
            'beidou': [],
            'beiji': [],
            'timerStar': '',
            'dayerStar': '',
            'dayofweek': '',
            'sunRiseTime': rise_set.get('sunrise', ''),
            'sunSetTime': rise_set.get('sunset', ''),
            'moonRiseTime': rise_set.get('moonrise', ''),
            'moonSetTime': rise_set.get('moonset', ''),
            'riseSet': rise_set,
            'sunrise': rise_set.get('sunrise', ''),
            'sunset': rise_set.get('sunset', ''),
            'moonrise': rise_set.get('moonrise', ''),
            'moonset': rise_set.get('moonset', ''),
        }

    def getLots(self):
        return sorted_objects(self.chart.pars)

    def empty_parallel(self):
        return {
            'parallel': [],
            'contraParallel': {},
        }

    def to_response(self, data, jyotish=None):
        varga = getattr(self, 'vargaChart', {
            'chartnum': 1,
            'key': 'd1',
            'name': 'Rashi',
            'label': 'D1 Rashi',
        })
        varga_engine_version = getattr(self, 'vargaEngineVersion', 'india_kernel_varga_v2')
        params = {
            'birth': self.getBirthStr(),
            'ad': -1 if self.isBC else 1,
            'lat': data['lat'],
            'lon': data['lon'],
            'chartnum': varga.get('chartnum', 1),
            'varga': varga,
            'hsys': self.houseCode,
            'hsysLabel': self.houseLabel,
            'ayanamsa': self.siderealModeKey,
            'ayanamsaLabel': self.siderealModeLabel,
            'ayanamsaValue': self.ayanamsaValue,
            'zone': data['zone'],
            'tradition': False,
            'zodiacal': const.SIDEREAL,
            'doubingSu28': 0,
            'showPdBounds': data.get('showPdBounds', 1),
            'pdtype': self.pdtype,
            'pdMethod': self.pdMethod,
            'pdTimeKey': self.pdTimeKey,
            'pdSyncRev': varga_engine_version,
            'engine': 'IndiaChartKernel',
        }
        if 'name' in data:
            params['name'] = data['name']

        obj = {
            'params': params,
            'chart': self.getChartObj(),
            'receptions': {
                'normal': [],
                'abnormal': [],
            },
            'mutuals': {},
            'declParallel': self.empty_parallel(),
            'aspects': {
                'normalAsp': [],
                'immediateAsp': [],
                'signAsp': [],
            },
            'lots': self.getLots(),
            'surround': {
                'planets': {},
                'attacks': {},
                'houses': {},
            },
            'guoStarSect': {
                'houses': [],
            },
        }
        if jyotish is not None:
            obj['jyotish'] = jyotish
        return obj


def build_india_chart(data, chartnum=1):
    kernel = IndiaChartKernel(data)
    return kernel
