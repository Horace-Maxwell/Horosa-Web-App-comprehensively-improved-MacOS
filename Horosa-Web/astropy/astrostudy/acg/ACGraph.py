import math
import swisseph

from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from flatlib import utils
from flatlib import angle
from astrostudy.helper import distance
from astrostudy.helper import convertLonToStr
from astrostudy.helper import convertLatToStr

ACG_LIST_OBJECTS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN,
    const.URANUS, const.NEPTUNE, const.PLUTO, const.NORTH_NODE, const.CHIRON,
    const.SOUTH_NODE, const.DARKMOON, const.PURPLE_CLOUDS
]

ACG_LIST_OBJECTS_NOCHIRON = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS, const.JUPITER, const.SATURN,
    const.URANUS, const.NEPTUNE, const.PLUTO, const.NORTH_NODE,
    const.SOUTH_NODE, const.DARKMOON, const.PURPLE_CLOUDS
]

# Astrocartography line geometry, analytic (Jim Lewis in-mundo) method.
# Conventions: longitude east-positive, normalised to (-180, 180]; degrees.

# Latitude sampling step (degrees) for the rising/setting great-circle curves.
ACG_LAT_STEP = 0.5

# Fallback obliquity if swisseph nutation lookup is unavailable.
DEFAULT_OBLIQUITY = 23.4392911

# Local-space great circle sampling step (degrees of arc).
LS_STEP = 3

# Parans are computed only for the main planets to keep the latitude-line set readable.
PARAN_OBJECTS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO,
]
PARAN_EVENTS = ['rise', 'set', 'mc', 'ic']
PARAN_LAT_LIMIT = 66.0
# Default to luminary parans (a pair involving the Sun or Moon) — the classic, readable set.
PARAN_LUMINARIES = [const.SUN, const.MOON]


def norm360(x):
    return x % 360.0


def norm180(x):
    return (x + 180.0) % 360.0 - 180.0


class ACGraph:
    def __init__(self, data):
        date = data['date']
        self.time = data['time']
        self.zone = data['zone']
        self.lat = data['lat']
        self.lon = data['lon']

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
        if 'ad' in data.keys():
            if int(data['ad']) == 1:
                pass
            else:
                if self.date[0:1] != '-':
                    self.date = '-{0}'.format(self.date)
                    self.year = '-{0}'.format(self.year)

        self.zodiacal = const.TROPICAL
        self.house = const.HOUSES_WHOLE_SIGN

        self.dateTime = Datetime(self.date, self.time, self.zone)
        self.pos = GeoPos(self.lat, self.lon)

        self.objlists = ACG_LIST_OBJECTS
        jd = self.dateTime.jd
        if jd > 3419437.5 or jd < 1967601.5:
            self.objlists = ACG_LIST_OBJECTS_NOCHIRON
        self.jd = jd

        self.chart = Chart(self.dateTime, self.pos, self.zodiacal, hsys=self.house,
                           IDs=self.objlists, needpars=False)

        self.eps = self._obliquity(jd)
        self.theta0 = self._gmst(jd)

    # ----- astronomical primitives -------------------------------------------------

    def _obliquity(self, jd):
        """ True obliquity of the ecliptic (degrees). """
        try:
            nut = swisseph.calc_ut(jd, swisseph.ECL_NUT, swisseph.FLG_SWIEPH)[0]
            return nut[0]
        except Exception:
            return DEFAULT_OBLIQUITY

    def _gmst(self, jd):
        """ Greenwich (apparent) sidereal time in degrees. """
        try:
            return norm360(swisseph.sidtime(jd) * 15.0)
        except Exception:
            # ARMC (apparent RA of MC) at birth == apparent LST == gmst + birthLon
            _, ascmc = swisseph.houses(jd, self.pos.lat, self.pos.lon, b'P')
            return norm360(ascmc[2] - self.pos.lon)

    def _radec(self, obj):
        """ Apparent right ascension / declination of a chart object (degrees).

        Uses the object's true ecliptic latitude (in-mundo), converted with the
        true obliquity. Works for every object including computed points (月孛/紫炁).
        """
        eq = swisseph.cotrans([obj.lon, obj.lat, 1.0], -self.eps)
        return norm360(eq[0]), eq[1]

    def createChart(self, lat, lon, planetid):
        """ Relocated chart at (lat, lon) for a single object. Kept for point reports. """
        pos = GeoPos(lat, lon)
        ids = [planetid]
        return Chart(self.dateTime, pos, self.zodiacal, hsys=self.house, IDs=ids, needpars=False)

    # ----- planet/angle lines ------------------------------------------------------

    def _mcLon(self, ra):
        """ Longitude of the MC (upper culmination) meridian for right ascension ra. """
        return norm180(ra - self.theta0)

    def _icLon(self, ra):
        return norm180(ra - self.theta0 + 180.0)

    def _ascDescLines(self, ra, dec):
        """ Rising (Asc) and setting (Dsc) great-circle curves.

        For each geographic latitude phi the body is on the horizon at hour angle
        +/-H where cos H = -tan(phi) tan(dec). LST = ra -/+ H, longitude = LST - gmst.
        Where |cos H| > 1 the body is circumpolar / never rises at that latitude, so
        the curve simply terminates (the characteristic polar "hook").
        """
        asc = []
        desc = []
        tanDec = math.tan(math.radians(dec))
        # Body rises/sets where |tan(phi)*tan(dec)| <= 1, i.e. |phi| <= 90 - |dec|.
        band = 89.5 if abs(tanDec) < 1e-6 else min(89.5, 90.0 - abs(dec))
        if band <= 0:
            return asc, desc
        # Fine sampling + EXACT band endpoints so the curve is smooth and closes onto
        # the MC/IC meridians (at |phi|=band, H=0 or 180 -> asc/desc reach MC/IC longitude).
        lats = []
        la = -band
        while la < band:
            lats.append(la)
            la += ACG_LAT_STEP
        lats.append(band)
        for la in lats:
            c = -math.tan(math.radians(la)) * tanDec
            if c < -1.0:
                c = -1.0
            elif c > 1.0:
                c = 1.0
            H = math.degrees(math.acos(c))
            asc.append({'lat': la, 'lon': norm180(ra - H - self.theta0)})
            desc.append({'lat': la, 'lon': norm180(ra + H - self.theta0)})
        return asc, desc

    # ----- geographic reference lines ----------------------------------------------

    def _hLine(self, lat):
        # Multi-point parallel of latitude. A 2-point [-180..180] line is degenerate on
        # the antimeridian (d3.geoPath clips it to nothing) — sample across the span.
        pts = [{'lat': lat, 'lon': float(l)} for l in range(-179, 180, 20)]
        pts.append({'lat': lat, 'lon': 179.0})
        return pts

    def _geoLines(self):
        equator = self._hLine(0.0)
        tropicN = self._hLine(self.eps)
        tropicS = self._hLine(-self.eps)
        # Ecliptic-overhead curve: zenith lies on the ecliptic <=> tan(phi)=tan(eps) sin(LST)
        tanEps = math.tan(math.radians(self.eps))
        ecliptic = []
        ilon = -180
        while ilon <= 180:
            lst = math.radians(self.theta0 + ilon)
            phi = math.degrees(math.atan(tanEps * math.sin(lst)))
            ecliptic.append({'lat': phi, 'lon': float(ilon)})
            ilon += 3
        return {
            'equator': equator,
            'tropicN': tropicN,
            'tropicS': tropicS,
            'ecliptic': ecliptic,
        }

    # ----- local space lines -------------------------------------------------------

    def _localSpace(self, ra, dec):
        """ Great circle from the birthplace along the body's compass azimuth. """
        phi0 = math.radians(self.pos.lat)
        lon0 = self.pos.lon
        H0 = math.radians(norm360(self.theta0 + lon0 - ra))
        decr = math.radians(dec)
        az = math.atan2(-math.cos(decr) * math.sin(H0),
                        math.cos(phi0) * math.sin(decr) - math.sin(phi0) * math.cos(decr) * math.cos(H0))
        pts = []
        d = 0
        while d <= 360:
            dr = math.radians(d)
            latr = math.asin(math.sin(phi0) * math.cos(dr) + math.cos(phi0) * math.sin(dr) * math.cos(az))
            lonr = math.atan2(math.sin(az) * math.sin(dr) * math.cos(phi0),
                              math.cos(dr) - math.sin(phi0) * math.sin(latr))
            pts.append({'lat': math.degrees(latr), 'lon': norm180(lon0 + math.degrees(lonr))})
            d += LS_STEP
        return pts

    # ----- parans (latitude crossing lines) ----------------------------------------

    def _eventLST(self, event, ra, dec, phi):
        if event == 'mc':
            return ra
        if event == 'ic':
            return norm360(ra + 180.0)
        c = -math.tan(math.radians(phi)) * math.tan(math.radians(dec))
        if c < -1.0 or c > 1.0:
            return None
        H = math.degrees(math.acos(c))
        return norm360(ra - H) if event == 'rise' else norm360(ra + H)

    def _fixedVarLats(self, c, event, ra, dec):
        """ One body fixed on the meridian (LST=c); solve the rising/setting latitude of the other. """
        H = norm360(ra - c) if event == 'rise' else norm360(c - ra)
        if H > 180.0:
            return []
        tand = math.tan(math.radians(dec))
        if abs(tand) < 1e-9:
            return []
        return [math.degrees(math.atan(-math.cos(math.radians(H)) / tand))]

    def _varVarLats(self, ea, ara, adec, eb, bra, bdec):
        """ Both bodies rising/setting; root-find the latitude where their event times coincide. """
        def f(phi):
            la = self._eventLST(ea, ara, adec, phi)
            lb = self._eventLST(eb, bra, bdec, phi)
            if la is None or lb is None:
                return None
            return norm180(la - lb)
        res = []
        phi = -PARAN_LAT_LIMIT
        prev = None
        prevphi = None
        while phi <= PARAN_LAT_LIMIT:
            v = f(phi)
            if v is not None and prev is not None and abs(prev) < 90.0 and abs(v) < 90.0:
                if (prev <= 0 <= v) or (prev >= 0 >= v):
                    lo, hi, flo = prevphi, phi, prev
                    for _ in range(40):
                        mid = (lo + hi) / 2.0
                        fm = f(mid)
                        if fm is None:
                            break
                        if (flo <= 0 <= fm) or (flo >= 0 >= fm):
                            hi = mid
                        else:
                            lo, flo = mid, fm
                    res.append((lo + hi) / 2.0)
            prev, prevphi = v, phi
            phi += 1.0
        return res

    def _parans(self, bodies):
        main = [b for b in bodies if b[0] in PARAN_OBJECTS]
        res = []
        for i in range(len(main)):
            for j in range(i + 1, len(main)):
                ai, ara, adec = main[i]
                bi, bra, bdec = main[j]
                for ea in PARAN_EVENTS:
                    for eb in PARAN_EVENTS:
                        fa = ea in ('mc', 'ic')
                        fb = eb in ('mc', 'ic')
                        if fa and fb:
                            continue
                        if fa:
                            lats = self._fixedVarLats(ara if ea == 'mc' else norm360(ara + 180.0), eb, bra, bdec)
                        elif fb:
                            lats = self._fixedVarLats(bra if eb == 'mc' else norm360(bra + 180.0), ea, ara, adec)
                        else:
                            lats = self._varVarLats(ea, ara, adec, eb, bra, bdec)
                        ptype = 'RSRS' if (not fa and not fb) else 'RSCA'
                        for lat in lats:
                            if abs(lat) > PARAN_LAT_LIMIT:
                                continue
                            res.append({'lat': round(lat, 3), 'a': ai, 'aEvent': ea,
                                        'b': bi, 'bEvent': eb, 'type': ptype})
        return res

    # ----- relocation point report -------------------------------------------------

    def pointReport(self, lat, lon, orb=2.0):
        """ Planets within orb of a local angle at (lat, lon) — Astro Gold's 'planets on angles'. """
        chart = Chart(self.dateTime, GeoPos(lat, lon), self.zodiacal, hsys=self.house,
                      IDs=self.objlists, needpars=False)
        angids = [const.ASC, const.DESC, const.MC, const.IC]
        angs = {a: chart.get(a).lon for a in angids}
        hits = []
        for id in self.objlists:
            plon = chart.getObject(id).lon
            best = None
            for a in angids:
                d = abs(norm180(plon - angs[a]))
                if d <= orb and (best is None or d < best['orb']):
                    best = {'planet': id, 'angle': a, 'orb': round(d, 3)}
            if best is not None:
                hits.append(best)
        hits.sort(key=lambda h: h['orb'])
        return {
            'lat': lat,
            'lon': lon,
            'orb': orb,
            'hits': hits,
            'relocAngles': {a: round(angs[a], 3) for a in angids},
        }

    # ----- entry point -------------------------------------------------------------

    def compute(self):
        planets = {}
        bodies = []
        for id in self.objlists:
            obj = self.chart.getObject(id)
            ra, dec = self._radec(obj)
            bodies.append((obj.id, ra, dec))
            asc, desc = self._ascDescLines(ra, dec)
            planets[obj.id] = {
                'ra': ra,
                'decl': dec,
                'lon': obj.lon,
                'lat': obj.lat,
                'lines': {
                    'mc': {'lon': self._mcLon(ra)},
                    'ic': {'lon': self._icLon(ra)},
                    'asc': asc,
                    'desc': desc,
                    'ls': self._localSpace(ra, dec),
                },
            }

        return {
            'meta': {
                'gmst': self.theta0,
                'obliquity': self.eps,
                'jd': self.jd,
                'birth': {'lat': self.pos.lat, 'lon': self.pos.lon},
            },
            'planets': planets,
            'geo': self._geoLines(),
            'parans': self._parans(bodies),
        }
