import math
from datetime import datetime, timedelta

from flatlib import const
from flatlib.datetime import Datetime
from flatlib.ephem import eph


SIGN_CN = {
    const.ARIES: '白羊',
    const.TAURUS: '金牛',
    const.GEMINI: '双子',
    const.CANCER: '巨蟹',
    const.LEO: '狮子',
    const.VIRGO: '处女',
    const.LIBRA: '天秤',
    const.SCORPIO: '天蝎',
    const.SAGITTARIUS: '射手',
    const.CAPRICORN: '摩羯',
    const.AQUARIUS: '水瓶',
    const.PISCES: '双鱼',
}

PLANET_CN = {
    const.SUN: '太阳',
    const.MOON: '月亮',
    const.MARS: '火星',
    const.MERCURY: '水星',
    const.JUPITER: '木星',
    const.VENUS: '金星',
    const.SATURN: '土星',
    const.NORTH_NODE: '罗睺',
    const.SOUTH_NODE: '计都',
}

JYOTISH_PLANETS = [
    const.SUN, const.MOON, const.MARS, const.MERCURY, const.JUPITER,
    const.VENUS, const.SATURN, const.NORTH_NODE, const.SOUTH_NODE
]

DASHA_SEQUENCE = [
    {'key': 'Ketu', 'id': const.SOUTH_NODE, 'label': '计都', 'years': 7},
    {'key': 'Venus', 'id': const.VENUS, 'label': '金星', 'years': 20},
    {'key': 'Sun', 'id': const.SUN, 'label': '太阳', 'years': 6},
    {'key': 'Moon', 'id': const.MOON, 'label': '月亮', 'years': 10},
    {'key': 'Mars', 'id': const.MARS, 'label': '火星', 'years': 7},
    {'key': 'Rahu', 'id': const.NORTH_NODE, 'label': '罗睺', 'years': 18},
    {'key': 'Jupiter', 'id': const.JUPITER, 'label': '木星', 'years': 16},
    {'key': 'Saturn', 'id': const.SATURN, 'label': '土星', 'years': 19},
    {'key': 'Mercury', 'id': const.MERCURY, 'label': '水星', 'years': 17},
]

NAKSHATRAS = [
    ('Ashwini', '马', 'Ketu'), ('Bharani', '胃', 'Venus'), ('Krittika', '昴', 'Sun'),
    ('Rohini', '毕', 'Moon'), ('Mrigashira', '参', 'Mars'), ('Ardra', '井', 'Rahu'),
    ('Punarvasu', '鬼', 'Jupiter'), ('Pushya', '柳', 'Saturn'), ('Ashlesha', '星', 'Mercury'),
    ('Magha', '张', 'Ketu'), ('Purva Phalguni', '翼', 'Venus'), ('Uttara Phalguni', '轸', 'Sun'),
    ('Hasta', '角', 'Moon'), ('Chitra', '亢', 'Mars'), ('Swati', '氐', 'Rahu'),
    ('Vishakha', '房', 'Jupiter'), ('Anuradha', '心', 'Saturn'), ('Jyeshtha', '尾', 'Mercury'),
    ('Mula', '箕', 'Ketu'), ('Purva Ashadha', '斗', 'Venus'), ('Uttara Ashadha', '牛', 'Sun'),
    ('Shravana', '女', 'Moon'), ('Dhanishta', '虚', 'Mars'), ('Shatabhisha', '危', 'Rahu'),
    ('Purva Bhadrapada', '室', 'Jupiter'), ('Uttara Bhadrapada', '壁', 'Saturn'), ('Revati', '奎', 'Mercury'),
]

TITHI_NAMES = [
    'Pratipada', 'Dvitiya', 'Tritiya', 'Chaturthi', 'Panchami', 'Shashthi',
    'Saptami', 'Ashtami', 'Navami', 'Dashami', 'Ekadashi', 'Dwadashi',
    'Trayodashi', 'Chaturdashi', 'Purnima/Amavasya'
]

YOGA_NAMES = [
    'Vishkambha', 'Priti', 'Ayushman', 'Saubhagya', 'Shobhana', 'Atiganda',
    'Sukarman', 'Dhriti', 'Shula', 'Ganda', 'Vriddhi', 'Dhruva', 'Vyaghata',
    'Harshana', 'Vajra', 'Siddhi', 'Vyatipata', 'Variyan', 'Parigha', 'Shiva',
    'Siddha', 'Sadhya', 'Shubha', 'Shukla', 'Brahma', 'Indra', 'Vaidhriti'
]

KARANA_SEQUENCE = [
    'Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti'
]

VARA_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
VARA_CN = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']

OWN_SIGNS = {
    const.SUN: [const.LEO],
    const.MOON: [const.CANCER],
    const.MARS: [const.ARIES, const.SCORPIO],
    const.MERCURY: [const.GEMINI, const.VIRGO],
    const.JUPITER: [const.SAGITTARIUS, const.PISCES],
    const.VENUS: [const.TAURUS, const.LIBRA],
    const.SATURN: [const.CAPRICORN, const.AQUARIUS],
    const.NORTH_NODE: [],
    const.SOUTH_NODE: [],
}

EXALTATION = {
    const.SUN: (const.ARIES, 10),
    const.MOON: (const.TAURUS, 3),
    const.MARS: (const.CAPRICORN, 28),
    const.MERCURY: (const.VIRGO, 15),
    const.JUPITER: (const.CANCER, 5),
    const.VENUS: (const.PISCES, 27),
    const.SATURN: (const.LIBRA, 20),
    const.NORTH_NODE: (const.TAURUS, 20),
    const.SOUTH_NODE: (const.SCORPIO, 20),
}

MOOLATRIKONA = {
    const.SUN: (const.LEO, 0, 20),
    const.MOON: (const.TAURUS, 4, 30),
    const.MARS: (const.ARIES, 0, 12),
    const.MERCURY: (const.VIRGO, 16, 20),
    const.JUPITER: (const.SAGITTARIUS, 0, 10),
    const.VENUS: (const.LIBRA, 0, 15),
    const.SATURN: (const.AQUARIUS, 0, 20),
}

BENEFIC_HOUSES = {
    'Sun': {
        'Sun': [1, 2, 4, 7, 8, 9, 10, 11],
        'Moon': [3, 6, 10, 11],
        'Mars': [1, 2, 4, 7, 8, 9, 10, 11],
        'Mercury': [3, 5, 6, 9, 10, 11, 12],
        'Jupiter': [5, 6, 9, 11],
        'Venus': [6, 7, 12],
        'Saturn': [1, 2, 4, 7, 8, 9, 10, 11],
        'Lagna': [3, 4, 6, 10, 11, 12],
    },
    'Moon': {
        'Sun': [3, 6, 7, 8, 10, 11],
        'Moon': [1, 3, 6, 7, 10, 11],
        'Mars': [2, 3, 5, 6, 9, 10, 11],
        'Mercury': [1, 3, 4, 5, 7, 8, 10, 11],
        'Jupiter': [1, 4, 7, 8, 10, 11, 12],
        'Venus': [3, 4, 5, 7, 9, 10, 11],
        'Saturn': [3, 5, 6, 11],
        'Lagna': [3, 6, 10, 11],
    },
    'Mars': {
        'Sun': [3, 5, 6, 10, 11],
        'Moon': [3, 6, 11],
        'Mars': [1, 2, 4, 7, 8, 10, 11],
        'Mercury': [3, 5, 6, 11],
        'Jupiter': [6, 10, 11, 12],
        'Venus': [6, 8, 11, 12],
        'Saturn': [1, 4, 7, 8, 9, 10, 11],
        'Lagna': [1, 3, 6, 10, 11],
    },
    'Mercury': {
        'Sun': [5, 6, 9, 11, 12],
        'Moon': [2, 4, 6, 8, 10, 11],
        'Mars': [1, 2, 4, 7, 8, 9, 10, 11],
        'Mercury': [1, 3, 5, 6, 9, 10, 11, 12],
        'Jupiter': [6, 8, 11, 12],
        'Venus': [1, 2, 3, 4, 5, 8, 9, 11],
        'Saturn': [1, 2, 4, 7, 8, 9, 10, 11],
        'Lagna': [1, 2, 4, 6, 8, 10, 11],
    },
    'Jupiter': {
        'Sun': [1, 2, 3, 4, 7, 8, 9, 10, 11],
        'Moon': [2, 5, 7, 9, 11],
        'Mars': [1, 2, 4, 7, 8, 10, 11],
        'Mercury': [1, 2, 4, 5, 6, 9, 10, 11],
        'Jupiter': [1, 2, 3, 4, 7, 8, 10, 11],
        'Venus': [2, 5, 6, 9, 10, 11],
        'Saturn': [3, 5, 6, 12],
        'Lagna': [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    'Venus': {
        'Sun': [8, 11, 12],
        'Moon': [1, 2, 3, 4, 5, 8, 9, 11, 12],
        'Mars': [3, 5, 6, 9, 11, 12],
        'Mercury': [3, 5, 6, 9, 11],
        'Jupiter': [5, 8, 9, 10, 11],
        'Venus': [1, 2, 3, 4, 5, 8, 9, 10, 11],
        'Saturn': [3, 4, 5, 8, 9, 10, 11],
        'Lagna': [1, 2, 3, 4, 5, 8, 9, 11],
    },
    'Saturn': {
        'Sun': [1, 2, 4, 7, 8, 10, 11],
        'Moon': [3, 6, 11],
        'Mars': [3, 5, 6, 10, 11, 12],
        'Mercury': [6, 8, 9, 10, 11, 12],
        'Jupiter': [5, 6, 11, 12],
        'Venus': [6, 11, 12],
        'Saturn': [3, 5, 6, 11],
        'Lagna': [1, 3, 4, 6, 10, 11],
    },
}


def norm(deg):
    return deg % 360


def sign_index_from_lon(lon):
    return int(norm(lon) / 30) % 12


def sign_from_lon(lon):
    return const.LIST_SIGNS[sign_index_from_lon(lon)]


def nakshatra_from_lon(lon):
    span = 360.0 / 27.0
    value = norm(lon)
    idx = min(26, int(value / span))
    progress = (value - idx * span) / span
    pada = min(4, int(progress * 4) + 1)
    name, label, lord = NAKSHATRAS[idx]
    return {
        'index': idx + 1,
        'name': name,
        'label': label,
        'lord': lord,
        'pada': pada,
        'progress': progress,
        'remainingRatio': 1 - progress,
    }


def house_number(obj):
    house = getattr(obj, 'house', None)
    if isinstance(house, str) and house.startswith('House'):
        try:
            return int(house[5:])
        except Exception:
            return None
    return None


def safe_get(chart, obj_id):
    try:
        return chart.get(obj_id)
    except Exception:
        return None


def get_local_birth_datetime(perchart):
    try:
        year = int(perchart.year)
        if year <= 0:
            return None
        parts = [int(x) for x in perchart.time.split(':')]
        while len(parts) < 3:
            parts.append(0)
        return datetime(year, int(perchart.month), int(perchart.day), parts[0], parts[1], parts[2])
    except Exception:
        return None


def format_dt(value):
    if value is None:
        return None
    return value.strftime('%Y-%m-%d')


def dasha_lord(key):
    for item in DASHA_SEQUENCE:
        if item['key'] == key:
            return item
    return DASHA_SEQUENCE[0]


class JyotishEngine:
    def __init__(self, perchart):
        self.perchart = perchart
        self.chart = perchart.chart
        self.asc = safe_get(self.chart, const.ASC)
        self.sun = safe_get(self.chart, const.SUN)
        self.moon = safe_get(self.chart, const.MOON)

    def compute(self):
        return {
            'engine': {
                'name': 'Horosa JyotishEngine',
                'version': '0.1.0',
                'ephemeris': 'Horosa Swiss Ephemeris / IndiaChartKernel',
                'source': 'chart_json_only',
                'chartnum': 1,
            },
            'panchanga': self.panchanga(),
            'nakshatras': self.nakshatras(),
            'dasha': {
                'vimshottari': self.vimshottari(),
            },
            'grahaDrishti': self.graha_drishti(),
            'ashtakavarga': self.ashtakavarga(),
            'shadbala': self.shadbala(),
            'strengths': self.strengths(),
            'jaimini': self.jaimini(),
            'kp': self.kp(),
            'muhurta': self.muhurta(),
            'transit': self.transit_notes(),
            'compatibility': self.compatibility_shell(),
        }

    def panchanga(self):
        sun_lon = getattr(self.sun, 'lon', 0)
        moon_lon = getattr(self.moon, 'lon', 0)
        lunar_angle = norm(moon_lon - sun_lon)
        tithi_index = min(29, int(lunar_angle / 12))
        tithi_day = tithi_index + 1
        paksha = 'Shukla' if tithi_day <= 15 else 'Krishna'
        tithi_name_idx = (tithi_day - 1) % 15
        yoga_index = min(26, int(norm(sun_lon + moon_lon) / (360.0 / 27.0)))
        karana_index = min(59, int(lunar_angle / 6))
        vara_index = self.perchart.dateTime.date.dayofweek()
        return {
            'vara': {
                'index': vara_index,
                'name': VARA_NAMES[vara_index],
                'label': VARA_CN[vara_index],
                'lord': dasha_lord(['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'][vara_index]),
            },
            'tithi': {
                'index': tithi_day,
                'name': TITHI_NAMES[tithi_name_idx],
                'paksha': paksha,
                'angle': lunar_angle,
                'progress': (lunar_angle % 12) / 12.0,
            },
            'nakshatra': nakshatra_from_lon(moon_lon),
            'yoga': {
                'index': yoga_index + 1,
                'name': YOGA_NAMES[yoga_index],
                'progress': (norm(sun_lon + moon_lon) % (360.0 / 27.0)) / (360.0 / 27.0),
            },
            'karana': self.karana(karana_index),
            'sunrise': self.safe_sunrise(),
        }

    def karana(self, karana_index):
        if karana_index == 0:
            name = 'Kimstughna'
        elif karana_index == 57:
            name = 'Shakuni'
        elif karana_index == 58:
            name = 'Chatushpada'
        elif karana_index == 59:
            name = 'Naga'
        else:
            name = KARANA_SEQUENCE[(karana_index - 1) % len(KARANA_SEQUENCE)]
        return {
            'index': karana_index + 1,
            'name': name,
        }

    def safe_sunrise(self):
        try:
            return self.perchart.getSunRiseTime()['timeStr']
        except Exception:
            return None

    def nakshatras(self):
        result = {}
        for obj_id in JYOTISH_PLANETS:
            obj = safe_get(self.chart, obj_id)
            if obj:
                result[obj_id] = nakshatra_from_lon(obj.lon)
        if self.asc:
            result[const.ASC] = nakshatra_from_lon(self.asc.lon)
        return result

    def vimshottari(self):
        birth = get_local_birth_datetime(self.perchart)
        moon_lon = getattr(self.moon, 'lon', None)
        if birth is None or moon_lon is None:
            return {
                'available': False,
                'reason': 'birth_date_outside_python_datetime_range',
            }

        moon_nak = nakshatra_from_lon(moon_lon)
        lord = dasha_lord(moon_nak['lord'])
        first_balance_years = lord['years'] * moon_nak['remainingRatio']
        first_elapsed_years = lord['years'] - first_balance_years
        cycle_start = birth - timedelta(days=first_elapsed_years * 365.25)
        lord_index = [x['key'] for x in DASHA_SEQUENCE].index(lord['key'])
        current_start = cycle_start
        now = datetime.now()
        items = []
        current = None
        for i in range(10):
            item_lord = DASHA_SEQUENCE[(lord_index + i) % len(DASHA_SEQUENCE)]
            duration_days = item_lord['years'] * 365.25
            current_end = current_start + timedelta(days=duration_days)
            sub_periods = self.dasha_sub_periods(item_lord, current_start, duration_days, 2)
            item = {
                'lord': item_lord,
                'years': item_lord['years'],
                'start': format_dt(current_start),
                'end': format_dt(current_end),
                'startIso': current_start.isoformat(),
                'endIso': current_end.isoformat(),
                'startAge': (current_start - birth).days / 365.25,
                'endAge': (current_end - birth).days / 365.25,
                'birthBalance': i == 0,
                'active': current_start <= now < current_end,
                'antardashas': sub_periods,
            }
            if item['active']:
                current = item
            items.append(item)
            current_start = current_end
        return {
            'available': True,
            'system': 'Vimshottari',
            'yearLengthDays': 365.25,
            'moonLongitude': moon_lon,
            'moonNakshatra': moon_nak,
            'firstLord': lord,
            'firstBalanceYears': first_balance_years,
            'firstElapsedYears': first_elapsed_years,
            'cycleStart': format_dt(cycle_start),
            'current': current,
            'mahadashas': items,
        }

    def dasha_sub_periods(self, parent_lord, start, parent_days, max_depth):
        result = []
        lord_index = [x['key'] for x in DASHA_SEQUENCE].index(parent_lord['key'])
        current_start = start
        for i in range(len(DASHA_SEQUENCE)):
            sub_lord = DASHA_SEQUENCE[(lord_index + i) % len(DASHA_SEQUENCE)]
            sub_days = parent_days * sub_lord['years'] / 120.0
            end = current_start + timedelta(days=sub_days)
            item = {
                'lord': sub_lord,
                'start': format_dt(current_start),
                'end': format_dt(end),
                'years': sub_days / 365.25,
            }
            if max_depth > 2:
                item['pratyantardashas'] = self.dasha_sub_periods(sub_lord, current_start, sub_days, max_depth - 1)
            result.append(item)
            current_start = end
        return result

    def graha_drishti(self):
        aspects = {
            const.SUN: [7],
            const.MOON: [7],
            const.MARS: [4, 7, 8],
            const.MERCURY: [7],
            const.JUPITER: [5, 7, 9],
            const.VENUS: [7],
            const.SATURN: [3, 7, 10],
            const.NORTH_NODE: [5, 7, 9],
            const.SOUTH_NODE: [5, 7, 9],
        }
        sign_map = self.planet_sign_map()
        result = []
        for giver, houses in aspects.items():
            if giver not in sign_map:
                continue
            giver_sign = sign_map[giver]
            for offset in houses:
                target_sign = (giver_sign + offset - 1) % 12
                receives = [
                    obj_id for obj_id, obj_sign in sign_map.items()
                    if obj_id != giver and obj_sign == target_sign
                ]
                result.append({
                    'giver': giver,
                    'giverLabel': PLANET_CN.get(giver, giver),
                    'aspectHouse': offset,
                    'targetSign': const.LIST_SIGNS[target_sign],
                    'targetSignLabel': SIGN_CN.get(const.LIST_SIGNS[target_sign], const.LIST_SIGNS[target_sign]),
                    'receives': receives,
                })
        return result

    def planet_sign_map(self):
        result = {}
        for obj_id in JYOTISH_PLANETS:
            obj = safe_get(self.chart, obj_id)
            if obj:
                result[obj_id] = sign_index_from_lon(obj.lon)
        return result

    def ashtakavarga(self):
        sign_names = const.LIST_SIGNS
        natal = {}
        for obj_id in [const.SUN, const.MOON, const.MARS, const.MERCURY, const.JUPITER, const.VENUS, const.SATURN]:
            obj = safe_get(self.chart, obj_id)
            if obj:
                natal[obj_id] = sign_index_from_lon(obj.lon)
        if self.asc:
            natal['Lagna'] = sign_index_from_lon(self.asc.lon)
        if len(natal) < 8:
            return {'available': False, 'reason': 'missing_planets'}

        bhinna = {}
        for target, table in BENEFIC_HOUSES.items():
            values = {sign: 0 for sign in sign_names}
            for contributor, houses in table.items():
                source_key = contributor if contributor == 'Lagna' else contributor
                if source_key not in natal:
                    continue
                source_sign = natal[source_key]
                for house in houses:
                    sign = sign_names[(source_sign + house - 1) % 12]
                    values[sign] += 1
            bhinna[target] = values

        sarva = {sign: 0 for sign in sign_names}
        for values in bhinna.values():
            for sign, count in values.items():
                sarva[sign] += count
        return {
            'available': True,
            'bhinna': bhinna,
            'sarva': sarva,
            'sarvaBySign': [
                {
                    'sign': sign,
                    'label': SIGN_CN.get(sign, sign),
                    'bindu': sarva[sign],
                }
                for sign in sign_names
            ],
        }

    def strengths(self):
        planets = []
        for obj_id in JYOTISH_PLANETS:
            obj = safe_get(self.chart, obj_id)
            if not obj:
                continue
            dignity = self.dignity(obj_id, obj.sign, obj.signlon)
            planets.append({
                'id': obj_id,
                'label': PLANET_CN.get(obj_id, obj_id),
                'lon': obj.lon,
                'sign': obj.sign,
                'signLabel': SIGN_CN.get(obj.sign, obj.sign),
                'signlon': obj.signlon,
                'house': house_number(obj),
                'motion': getattr(obj, 'movedir', None),
                'dignity': dignity,
                'nakshatra': nakshatra_from_lon(obj.lon),
            })
        return {
            'planetaryStates': planets,
            'vargaDignity': self.varga_dignity(planets),
        }

    def shadbala(self):
        dignity_scores = {
            'deep_exaltation': 60,
            'exaltation': 55,
            'moolatrikona': 50,
            'own_sign': 45,
            'neutral': 30,
            'debilitation': 15,
        }
        natural_scores = {
            const.SUN: 60,
            const.MOON: 51,
            const.VENUS: 43,
            const.JUPITER: 34,
            const.MERCURY: 26,
            const.MARS: 17,
            const.SATURN: 9,
        }
        digbala_houses = {
            const.SUN: 10,
            const.MARS: 10,
            const.JUPITER: 1,
            const.MERCURY: 1,
            const.MOON: 4,
            const.VENUS: 4,
            const.SATURN: 7,
        }
        rows = []
        for obj_id in [const.SUN, const.MOON, const.MARS, const.MERCURY, const.JUPITER, const.VENUS, const.SATURN]:
            obj = safe_get(self.chart, obj_id)
            if not obj:
                continue
            dignity = self.dignity(obj_id, obj.sign, obj.signlon)
            house = house_number(obj)
            target_house = digbala_houses.get(obj_id)
            if house and target_house:
                house_distance = min((house - target_house) % 12, (target_house - house) % 12)
                digbala = max(0, 60 - house_distance * 10)
            else:
                digbala = 0
            chestabala = 45 if getattr(obj, 'movedir', None) == 'Retrograde' else 30
            sthanabala = dignity_scores.get(dignity, 30)
            naisargika = natural_scores.get(obj_id, 0)
            total = sthanabala + digbala + chestabala + naisargika
            rows.append({
                'id': obj_id,
                'label': PLANET_CN.get(obj_id, obj_id),
                'sthana': sthanabala,
                'dig': digbala,
                'chesta': chestabala,
                'naisargika': naisargika,
                'totalVirupa': total,
                'totalRupa': round(total / 60.0, 2),
                'dignity': dignity,
                'house': house,
            })
        rows.sort(key=lambda item: item['totalVirupa'], reverse=True)
        return {
            'available': bool(rows),
            'method': 'structured_rule_estimate_from_Horosa_D1',
            'note': 'Uses Horosa chart JSON positions only; replaceable with full BPHS component formulas in the same isolated layer.',
            'planets': rows,
        }

    def dignity(self, obj_id, sign, signlon):
        if obj_id in EXALTATION:
            exalt_sign, exalt_deg = EXALTATION[obj_id]
            deb_sign = const.LIST_SIGNS[(const.LIST_SIGNS.index(exalt_sign) + 6) % 12]
            if sign == exalt_sign:
                return 'deep_exaltation' if abs(signlon - exalt_deg) < 1 else 'exaltation'
            if sign == deb_sign:
                return 'debilitation'
        if obj_id in MOOLATRIKONA:
            mt_sign, mt_start, mt_end = MOOLATRIKONA[obj_id]
            if sign == mt_sign and mt_start <= signlon <= mt_end:
                return 'moolatrikona'
        if sign in OWN_SIGNS.get(obj_id, []):
            return 'own_sign'
        return 'neutral'

    def varga_dignity(self, planets):
        return [
            {
                'id': item['id'],
                'label': item['label'],
                'd1': item['dignity'],
                'note': 'computed_from_Horosa_D1_positions',
            }
            for item in planets
        ]

    def jaimini(self):
        candidates = []
        for obj_id in [const.SUN, const.MOON, const.MARS, const.MERCURY, const.JUPITER, const.VENUS, const.SATURN]:
            obj = safe_get(self.chart, obj_id)
            if obj:
                candidates.append((obj.signlon, obj_id, obj))
        candidates.sort(reverse=True, key=lambda row: row[0])
        names = ['Atmakaraka', 'Amatyakaraka', 'Bhratrikaraka', 'Matrikaraka', 'Putrakaraka', 'Gnatikaraka', 'Darakaraka']
        return {
            'charaKarakas': [
                {
                    'karaka': names[idx],
                    'planet': obj_id,
                    'label': PLANET_CN.get(obj_id, obj_id),
                    'sign': obj.sign,
                    'signLabel': SIGN_CN.get(obj.sign, obj.sign),
                    'signlon': obj.signlon,
                }
                for idx, (_, obj_id, obj) in enumerate(candidates[:len(names)])
            ],
        }

    def kp(self):
        sublords = {}
        for obj_id in JYOTISH_PLANETS:
            obj = safe_get(self.chart, obj_id)
            if not obj:
                continue
            sublords[obj_id] = self.kp_sublord(obj.lon)
        if self.asc:
            sublords[const.ASC] = self.kp_sublord(self.asc.lon)
        return {
            'ayanamsa': getattr(self.perchart, 'siderealModeLabel', 'Lahiri / Horosa sidereal context'),
            'ayanamsaKey': getattr(self.perchart, 'siderealModeKey', 'lahiri'),
            'sublords': sublords,
        }

    def kp_sublord(self, lon):
        nak = nakshatra_from_lon(lon)
        lord_index = [x['key'] for x in DASHA_SEQUENCE].index(nak['lord'])
        span = 360.0 / 27.0
        progress_deg = (norm(lon) % span)
        cursor = 0
        sublord = DASHA_SEQUENCE[lord_index]
        for i in range(len(DASHA_SEQUENCE)):
            candidate = DASHA_SEQUENCE[(lord_index + i) % len(DASHA_SEQUENCE)]
            part = span * candidate['years'] / 120.0
            if progress_deg <= cursor + part:
                sublord = candidate
                break
            cursor += part
        return {
            'nakshatra': nak,
            'starLord': dasha_lord(nak['lord']),
            'subLord': sublord,
        }

    def muhurta(self):
        try:
            sunrise_jd = eph.lastSunrise(self.perchart.dateTime.jd + 0.5, self.perchart.pos.lat, self.perchart.pos.lon)
            sunset_jd = eph.nextSunset(sunrise_jd, self.perchart.pos.lat, self.perchart.pos.lon)
            sunrise = Datetime.fromJD(sunrise_jd, self.perchart.zone)
            sunset = Datetime.fromJD(sunset_jd, self.perchart.zone)
            day_length_hours = (sunset_jd - sunrise_jd) * 24
            weekday = self.perchart.dateTime.date.dayofweek()
            rahu_slots = [8, 2, 7, 5, 6, 4, 3]
            yama_slots = [5, 4, 3, 2, 1, 7, 6]
            gulika_slots = [7, 6, 5, 4, 3, 2, 1]
            slot_hours = day_length_hours / 8.0
            return {
                'sunrise': sunrise.toCNString(),
                'sunset': sunset.toCNString(),
                'rahuKalam': self.muhurta_interval(sunrise, slot_hours, rahu_slots[weekday]),
                'yamaganda': self.muhurta_interval(sunrise, slot_hours, yama_slots[weekday]),
                'gulika': self.muhurta_interval(sunrise, slot_hours, gulika_slots[weekday]),
            }
        except Exception as exc:
            return {'available': False, 'reason': str(exc)}

    def muhurta_interval(self, sunrise, slot_hours, slot):
        start_jd = sunrise.jd + (slot - 1) * slot_hours / 24.0
        end_jd = start_jd + slot_hours / 24.0
        return {
            'start': Datetime.fromJD(start_jd, self.perchart.zone).toCNString(),
            'end': Datetime.fromJD(end_jd, self.perchart.zone).toCNString(),
        }

    def transit_notes(self):
        moon_house = house_number(self.moon) if self.moon else None
        saturn = safe_get(self.chart, const.SATURN)
        return {
            'sadeSatiNatalBasis': {
                'moonSign': getattr(self.moon, 'sign', None),
                'saturnSign': getattr(saturn, 'sign', None),
                'moonHouse': moon_house,
                'note': 'natal_basis_only_current_transit_requires_transit_chart',
            }
        }

    def compatibility_shell(self):
        return {
            'available': False,
            'reason': 'requires_second_chart',
            'supportedFutureMethods': ['kuta_matching', 'tara_bala', 'yoni', 'graha_maitri'],
        }


def build_jyotish(perchart):
    return JyotishEngine(perchart).compute()
