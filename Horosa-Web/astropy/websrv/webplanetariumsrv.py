import os
import math
import json
import re
import time
import traceback

import cherrypy
import swisseph

try:
    import jsonpickle
except ImportError:
    class _JsonpickleCompat:
        @staticmethod
        def encode(obj, unpicklable=False):
            return json.dumps(obj, ensure_ascii=False, default=str)

    jsonpickle = _JsonpickleCompat()

from flatlib import const
from flatlib import utils
from flatlib.ephem import swe
from astrostudy.perchart import PerChart, getHSys
from websrv.helper import enable_crossdomain


_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
_FIXSTARS_PATH = os.path.join(_ROOT, "flatlib-ctrad2", "flatlib", "resources", "swefiles", "fixstars.cat")
_BSC5_PATH = os.path.join(_ROOT, "astropy", "resources", "bsc5-horosa.json")
_STAR_CACHE = None
_BSC5_CACHE = None


ZODIAC_LABELS = [
    "白羊", "金牛", "双子", "巨蟹", "狮子", "处女",
    "天秤", "天蝎", "射手", "摩羯", "水瓶", "双鱼",
]

ZODIAC_IDS = [
    const.ARIES, const.TAURUS, const.GEMINI, const.CANCER, const.LEO, const.VIRGO,
    const.LIBRA, const.SCORPIO, const.SAGITTARIUS, const.CAPRICORN, const.AQUARIUS, const.PISCES,
]

PLANETARIUM_OBJECTS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE,
    const.PLUTO, const.NORTH_NODE, const.SOUTH_NODE,
]
PLANETARIUM_OBJECT_IDS = set(PLANETARIUM_OBJECTS)

QIZHENG_SIYU = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.NORTH_NODE, const.SOUTH_NODE,
]


def _norm_degree(value):
    res = float(value) % 360.0
    return res + 360.0 if res < 0 else res


def _zodiac_info(lon):
    lon = _norm_degree(lon)
    idx = int(lon // 30) % 12
    return {
        "zodiacSign": ZODIAC_LABELS[idx],
        "zodiacSignId": ZODIAC_IDS[idx],
        "zodiacDegree": lon - idx * 30,
    }


def _visibility_info(item, sun_altitude=None):
    alt = _num(item.get("altitudeAppa", item.get("altitudeTrue", 0)))
    mag = item.get("mag", None)
    is_above = alt > 0
    twilight = None
    if sun_altitude is not None:
        if sun_altitude > -0.833:
            twilight = "day"
        elif sun_altitude > -6:
            twilight = "civil"
        elif sun_altitude > -12:
            twilight = "nautical"
        elif sun_altitude > -18:
            twilight = "astronomical"
        else:
            twilight = "night"
    visible = is_above
    if mag is not None and sun_altitude is not None and sun_altitude > -6 and _num(mag, 99) > 1.5:
        visible = False
    if alt > 60:
        horizon_state = "高空"
    elif alt > 15:
        horizon_state = "可见"
    elif alt > 0:
        horizon_state = "近地平"
    elif alt > -6:
        horizon_state = "地平线下"
    else:
        horizon_state = "不可见"
    return {
        "visible": visible,
        "aboveHorizon": is_above,
        "horizonState": horizon_state,
        "twilight": twilight,
    }


def _moon_phase_info(bodies):
    sun = next((item for item in bodies if item.get("id") == const.SUN), None)
    moon = next((item for item in bodies if item.get("id") == const.MOON), None)
    if not sun or not moon:
        return None
    elongation = _norm_degree(_num(moon.get("lon")) - _num(sun.get("lon")))
    illumination = (1 - math.cos(math.radians(elongation))) / 2
    age = elongation / 360.0 * 29.530588853
    if elongation < 22.5 or elongation >= 337.5:
        name = "朔"
    elif elongation < 67.5:
        name = "蛾眉月"
    elif elongation < 112.5:
        name = "上弦"
    elif elongation < 157.5:
        name = "盈凸月"
    elif elongation < 202.5:
        name = "望"
    elif elongation < 247.5:
        name = "亏凸月"
    elif elongation < 292.5:
        name = "下弦"
    else:
        name = "残月"
    return {
        "phaseAngle": elongation,
        "illumination": illumination,
        "ageDays": age,
        "phaseName": name,
        "waxing": elongation < 180,
    }


def _num(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def _ra_hours_to_deg(parts):
    h = _num(parts[0])
    m = _num(parts[1])
    s = _num(parts[2])
    return (h + m / 60.0 + s / 3600.0) * 15.0


def _decl_to_deg(parts):
    deg_txt = str(parts[0]).strip()
    sign = -1.0 if deg_txt.startswith("-") else 1.0
    d = abs(_num(deg_txt))
    m = abs(_num(parts[1] if len(parts) > 1 else 0))
    s = abs(_num(parts[2] if len(parts) > 2 else 0))
    return sign * (d + m / 60.0 + s / 3600.0)


def _ra_text_to_deg(value):
    vals = re.findall(r"[-+]?\d+(?:\.\d+)?", value or "")
    if len(vals) < 3:
        return None
    return (_num(vals[0]) + _num(vals[1]) / 60.0 + _num(vals[2]) / 3600.0) * 15.0


def _dec_text_to_deg(value):
    txt = value or ""
    vals = re.findall(r"[-+]?\d+(?:\.\d+)?", txt)
    if len(vals) < 3:
        return None
    sign = -1.0 if txt.strip().startswith("-") else 1.0
    return sign * (abs(_num(vals[0])) + abs(_num(vals[1])) / 60.0 + abs(_num(vals[2])) / 3600.0)


def _altaz_from_equatorial(jd, pos, ra, decl, height=150.0, press=1000.0, temp=20.0):
    za = swisseph.azalt(
        jd,
        swisseph.EQU2HOR,
        [pos.lon, pos.lat, height],
        press,
        temp,
        [ra, decl, 1],
    )
    return {
        "azimuth": za[0],
        "altitudeTrue": za[1],
        "altitudeAppa": za[2],
    }


def _altaz_from_ecliptic(jd, pos, lon, lat=0.0, height=150.0, press=1000.0, temp=20.0):
    za = swisseph.azalt(
        jd,
        swisseph.ECL2HOR,
        [pos.lon, pos.lat, height],
        press,
        temp,
        [lon, lat, 1],
    )
    return {
        "azimuth": za[0],
        "altitudeTrue": za[1],
        "altitudeAppa": za[2],
    }


def _read_star_catalog():
    global _STAR_CACHE
    if _STAR_CACHE is not None:
        return _STAR_CACHE

    stars = []
    if not os.path.exists(_FIXSTARS_PATH):
        _STAR_CACHE = stars
        return stars

    with open(_FIXSTARS_PATH, "r", encoding="utf-8", errors="ignore") as fh:
        seen = set()
        for idx, line in enumerate(fh):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [item.strip() for item in line.split(",")]
            if len(parts) < 14:
                continue
            try:
                mag = float(parts[13])
            except Exception:
                continue
            if mag > 6.5 or mag >= 99:
                continue
            label = parts[0] or parts[1] or "Star"
            label_lower = label.lower()
            bayer_lower = (parts[1] or "").lower()
            if "cluster" in label_lower or "galaxy" in label_lower or label_lower.startswith("gal.") or label_lower == "great attractor" or bayer_lower in ("m31", "m44"):
                continue
            ra = _ra_hours_to_deg(parts[3:6])
            decl = _decl_to_deg(parts[6:9])
            dedupe_key = (parts[1] or label or "", round(ra, 5), round(decl, 5))
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            stars.append({
                "id": f"catalog-{idx}",
                "name": label,
                "bayer": parts[1],
                "ra": _norm_degree(ra),
                "decl": decl,
                "mag": mag,
                "kind": "catalogStar",
            })
    _STAR_CACHE = stars
    return stars


def _read_bsc5_catalog():
    global _BSC5_CACHE
    if _BSC5_CACHE is not None:
        return _BSC5_CACHE

    stars = []
    if not os.path.exists(_BSC5_PATH):
        _BSC5_CACHE = stars
        return stars

    try:
        with open(_BSC5_PATH, "r", encoding="utf-8") as fh:
            rows = json.load(fh)
    except Exception:
        traceback.print_exc()
        _BSC5_CACHE = stars
        return stars

    for row in rows:
        ra = _ra_text_to_deg(row.get("RA"))
        decl = _dec_text_to_deg(row.get("Dec"))
        if ra is None or decl is None:
            continue
        mag = _num(row.get("Vmag"), 99)
        if mag > 6.5:
            continue
        bayer = row.get("B") or ""
        flamsteed = row.get("F") or ""
        constell = row.get("C") or ""
        name = row.get("N") or (f"{bayer} {constell}".strip()) or (f"{flamsteed} {constell}".strip()) or f"HR {row.get('HR', '')}".strip()
        stars.append({
            "id": f"bsc5-{row.get('HR', len(stars))}",
            "name": name,
            "bayer": bayer,
            "flamsteed": flamsteed,
            "constellation": constell,
            "ra": _norm_degree(ra),
            "decl": decl,
            "mag": mag,
            "colorIndex": row.get("B-V"),
            "colorTemperature": _num(row.get("K"), None),
            "spectralClass": row.get("SpectralCls"),
            "kind": "catalogStar",
        })
    stars.sort(key=lambda rec: rec.get("mag", 99))
    _BSC5_CACHE = stars
    return stars


def _plain_obj(obj):
    res = {
        "id": getattr(obj, "id", ""),
        "name": getattr(obj, "name", None) or getattr(obj, "id", ""),
        "type": getattr(obj, "type", ""),
        "lon": _num(getattr(obj, "lon", 0)),
        "lat": _num(getattr(obj, "lat", 0)),
        "ra": _num(getattr(obj, "ra", 0)),
        "decl": _num(getattr(obj, "decl", 0)),
        "azimuth": _num(getattr(obj, "azimuth", 0)),
        "altitudeTrue": _num(getattr(obj, "altitudeTrue", 0)),
        "altitudeAppa": _num(getattr(obj, "altitudeAppa", 0)),
        "mag": getattr(obj, "mag", None),
        "sign": getattr(obj, "sign", None),
        "signlon": getattr(obj, "signlon", None),
        "house": getattr(obj, "house", None),
        "su28": getattr(obj, "su28", None),
    }
    res.update(_zodiac_info(res["lon"]))
    if getattr(obj, "lonspeed", None) is not None:
        res["lonspeed"] = obj.lonspeed
    res.update(_visibility_info(res))
    return res


def _build_catalog_stars(perchart, limit):
    stars = []
    catalog = _read_bsc5_catalog() or _read_star_catalog()
    for star in catalog:
        item = dict(star)
        item.update(_altaz_from_equatorial(perchart.dateTime.jd, perchart.pos, item["ra"], item["decl"]))
        item.update(_visibility_info(item))
        stars.append(item)
    stars.sort(key=lambda rec: rec.get("mag", 99))
    if limit and len(stars) > limit:
        return stars[:limit]
    return stars


def _chart_objects(perchart):
    objects = []
    for key in perchart.chart.objects.content.keys():
        obj = perchart.chart.objects.content[key]
        if getattr(obj, "id", None) in PLANETARIUM_OBJECT_IDS:
            objects.append(obj)
    objects.sort(key=lambda item: _num(getattr(item, "lon", 0)))
    return objects


def _safe_perchart_list(perchart, method_name):
    try:
        method = getattr(perchart, method_name)
        return method()
    except Exception:
        traceback.print_exc()
        return []


def _build_line_from_equatorial(perchart, points, key, label):
    res = []
    for item in points:
        row = {
            "ra": _norm_degree(item["ra"]),
            "decl": _num(item["decl"]),
        }
        row.update(_altaz_from_equatorial(perchart.dateTime.jd, perchart.pos, row["ra"], row["decl"]))
        res.append(row)
    return {
        "key": key,
        "label": label,
        "points": res,
    }


def _build_line_from_ecliptic(perchart, start, end, step, key, label):
    points = []
    lon = start
    while lon <= end:
        eq = utils.eqCoords(_norm_degree(lon), 0)
        row = {
            "lon": _norm_degree(lon),
            "lat": 0,
            "ra": _norm_degree(eq[0]),
            "decl": eq[1],
        }
        row.update(_altaz_from_ecliptic(perchart.dateTime.jd, perchart.pos, row["lon"], 0))
        points.append(row)
        lon += step
    return {
        "key": key,
        "label": label,
        "points": points,
    }


def _build_overlays(perchart):
    horizon = []
    for az in range(0, 361, 5):
        horizon.append({
            "azimuth": az,
            "altitudeTrue": 0,
            "altitudeAppa": 0,
        })

    meridian_points = []
    for alt in range(-80, 91, 5):
        meridian_points.append({
            "azimuth": 180,
            "altitudeTrue": alt,
            "altitudeAppa": alt,
        })

    equator_points = []
    for ra in range(0, 361, 5):
        row = {
            "ra": ra,
            "decl": 0,
        }
        row.update(_altaz_from_equatorial(perchart.dateTime.jd, perchart.pos, ra, 0))
        equator_points.append(row)

    zodiac = []
    for idx, name in enumerate(ZODIAC_LABELS):
        start = idx * 30
        line = _build_line_from_ecliptic(perchart, start, start + 30, 2, f"zodiac-{idx}", name)
        line["startLon"] = start
        line["endLon"] = start + 30
        zodiac.append(line)

    houses = []
    try:
        chart = perchart.chart
        for house in chart.houses:
            row = _plain_obj(house)
            row.update(_altaz_from_ecliptic(perchart.dateTime.jd, perchart.pos, row["lon"], 0))
            houses.append(row)
    except Exception:
        traceback.print_exc()

    return {
        "horizon": {
            "key": "horizon",
            "label": "地平线",
            "points": horizon,
        },
        "meridian": {
            "key": "meridian",
            "label": "子午线",
            "points": meridian_points,
        },
        "equator": {
            "key": "equator",
            "label": "天赤道",
            "points": equator_points,
        },
        "ecliptic": _build_line_from_ecliptic(perchart, 0, 360, 2, "ecliptic", "黄道"),
        "zodiac": zodiac,
        "houses": houses,
    }


class PlanetariumSrv:
    exposed = True

    @cherrypy.expose
    @cherrypy.config(**{"tools.cors.on": True})
    @cherrypy.tools.json_in()
    def index(self):
        return self.state()

    @cherrypy.expose
    @cherrypy.config(**{"tools.cors.on": True})
    @cherrypy.tools.json_in()
    def state(self):
        enable_crossdomain()
        started = time.perf_counter()
        try:
            data = cherrypy.request.json if cherrypy.request.method == "POST" else {}
            data = data or {}
            data.setdefault("hsys", 1)
            data.setdefault("zodiacal", 0)
            data.setdefault("predictive", False)
            data.setdefault("needpars", False)
            requested_objects = data.get("objlists") or PLANETARIUM_OBJECTS
            data["objlists"] = [item for item in requested_objects if item in PLANETARIUM_OBJECT_IDS]
            perchart = PerChart(data)
            catalog_limit = int(data.get("starLimit", 9000))
            include_catalog = catalog_limit != 0
            include_overlays = data.get("includeOverlays", True) is not False
            include_traditions = data.get("includeTraditions", True) is not False

            bodies = [_plain_obj(item) for item in _chart_objects(perchart)]
            sun_body = next((item for item in bodies if item.get("id") == const.SUN), None)
            sun_altitude = sun_body.get("altitudeAppa") if sun_body else None
            for item in bodies:
                item.update(_visibility_info(item, sun_altitude))
            su28 = [_plain_obj(item) for item in _safe_perchart_list(perchart, "getFixedStarSu28")] if include_traditions else []
            beidou = [_plain_obj(item) for item in _safe_perchart_list(perchart, "getBeiDou")] if include_traditions else []
            fixed_stars = [_plain_obj(item) for item in _safe_perchart_list(perchart, "getFixedStars")] if include_traditions else []
            for group in (su28, beidou, fixed_stars):
                for item in group:
                    item.update(_visibility_info(item, sun_altitude))
            catalog_stars = _build_catalog_stars(perchart, catalog_limit) if include_catalog else []
            for item in catalog_stars:
                item.update(_visibility_info(item, sun_altitude))
            moon_phase = _moon_phase_info(bodies)
            sky_mode = "night"
            if sun_altitude is not None:
                if sun_altitude > -0.833:
                    sky_mode = "day"
                elif sun_altitude > -6:
                    sky_mode = "civilTwilight"
                elif sun_altitude > -12:
                    sky_mode = "nauticalTwilight"
                elif sun_altitude > -18:
                    sky_mode = "astronomicalTwilight"

            res = {
                "version": "planetarium-v1",
                "schema": {
                    "id": "horosa.planetarium.state",
                    "version": 1,
                    "sections": ["observer", "bodies", "stars", "overlays", "traditions", "sky", "meta"],
                },
                "observer": {
                    "date": data.get("date"),
                    "time": data.get("time"),
                    "zone": data.get("zone"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "gpsLat": data.get("gpsLat"),
                    "gpsLon": data.get("gpsLon"),
                    "jd": perchart.dateTime.jd,
                    "locationName": data.get("pos") or data.get("name") or "未命名地点",
                },
                "bodies": bodies,
                "stars": {
                    "catalog": catalog_stars,
                    "fixed": fixed_stars,
                    "source": "Yale Bright Star Catalog v5, with Swiss Ephemeris Alt-Az projection",
                    "magLimit": 6.5,
                    "catalogFields": ["id", "name", "ra", "decl", "azimuth", "altitudeAppa", "mag", "colorIndex", "colorTemperature", "constellation", "visible"],
                },
                "overlays": _build_overlays(perchart) if include_overlays else {},
                "traditions": {
                    "su28": su28,
                    "beidou": beidou,
                    "qizhengSiyu": [item for item in bodies if item["id"] in QIZHENG_SIYU],
                },
                "sky": {
                    "mode": sky_mode,
                    "sunAltitude": sun_altitude,
                    "moonPhase": moon_phase,
                },
                "meta": {
                    "catalogCount": len(_read_bsc5_catalog() or _read_star_catalog()),
                    "bsc5CatalogCount": len(_read_bsc5_catalog()),
                    "swissFixedStarCount": len(_read_star_catalog()),
                    "renderedCatalogCount": len(catalog_stars),
                    "lightweight": not include_catalog or not include_overlays or not include_traditions,
                    "hsys": getHSys(data.get("hsys", 1)),
                    "zodiacal": perchart.zodiacal,
                    "timingMs": {
                        "total": round((time.perf_counter() - started) * 1000, 2),
                    },
                },
            }
            return jsonpickle.encode(res, unpicklable=False)
        except Exception:
            traceback.print_exc()
            return jsonpickle.encode({"err": "planetarium param error"}, unpicklable=False)
