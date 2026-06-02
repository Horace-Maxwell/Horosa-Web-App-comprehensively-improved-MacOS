import traceback
import jsonpickle
import cherrypy
from astrostudy.perchart import PerChart
from websrv.helper import enable_crossdomain
from astrostudy.germany.midpoint import MidPoint
from flatlib import const
from flatlib.ephem import ephem as flatlib_ephem


def _build_uranian_tnp(perchart):
    """8 颗汉堡虚星(TNP)，用 perchart 现成 dateTime/pos 纯读计算——
    不进 objlists、不动 MidPoint.aspects(逐字节不变)。"""
    out = []
    for oid in const.LIST_URANIAN:
        try:
            o = flatlib_ephem.getObject(oid, perchart.dateTime, perchart.pos)
            out.append({
                'id': o.id,
                'lon': o.lon,
                'lat': o.lat,
                'lonspeed': o.lonspeed,
                'sign': o.sign,
                'signlon': o.signlon,
            })
        except Exception:
            traceback.print_exc()
    return out


class GermanyAstroSrv:
    exposed = True

    def OPTIONS(*args, **kwargs):
        enable_crossdomain()


    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    def midpoint(self):
        enable_crossdomain()
        try:
            data = cherrypy.request.json

            data['tradition'] = False
            data['predictive'] = False

            # 必要参数校验：缺 date/time/zone/lat/lon 时直接回结构化错误，不进 PerChart（避免 GeoPos/Datetime
            # 抛栈被裸 except 笼统兜成 'param error'）。前端已先校验、正常不会到这里，仅作后端兜底。
            missing = [k for k in ('date', 'time', 'zone', 'lat', 'lon')
                       if data.get(k) is None or '{0}'.format(data.get(k)).strip() == '']
            if missing:
                return jsonpickle.encode({'err': 'missing_param', 'missing': missing}, unpicklable=False)

            perchart = PerChart(data)
            midpoint = MidPoint(perchart)
            mids = midpoint.calculate()
            mids['tnp'] = _build_uranian_tnp(perchart)  # 增量字段；midpoints/aspects 不变

            res = jsonpickle.encode(mids, unpicklable=False)
            return res
        except Exception as e:
            traceback.print_exc()
            obj = {
                'err': 'compute_error',
                'detail': '{0}'.format(e),
            }
            return jsonpickle.encode(obj, unpicklable=False)
