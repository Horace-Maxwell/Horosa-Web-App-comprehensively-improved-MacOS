import traceback

import cherrypy
import jsonpickle

from astrostudy import astroextra
from websrv.helper import enable_crossdomain


class AstroExtraSrv:
    exposed = True

    def OPTIONS(*args, **kwargs):
        enable_crossdomain()

    def _json(self, obj):
        return jsonpickle.encode(obj, unpicklable=False)

    def _payload(self, params):
        data = getattr(cherrypy.request, 'json', None)
        if isinstance(data, dict):
            payload = dict(data)
        else:
            payload = {}
        payload.update(params)
        return payload

    def _error(self):
        traceback.print_exc()
        return self._json({'err': 'param error'})

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    def analysis(self, **params):
        enable_crossdomain()
        try:
            return self._json(astroextra.analyze_chart(self._payload(params)))
        except Exception:
            return self._error()

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    def ephemeris(self, **params):
        enable_crossdomain()
        try:
            return self._json(astroextra.build_ephemeris(self._payload(params)))
        except Exception:
            return self._error()

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    def progressions(self, **params):
        enable_crossdomain()
        try:
            return self._json(astroextra.build_progressions(self._payload(params)))
        except Exception:
            return self._error()

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    def returns(self, **params):
        enable_crossdomain()
        try:
            return self._json(astroextra.build_return_timeline(self._payload(params)))
        except Exception:
            return self._error()

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    def harmonic(self, **params):
        enable_crossdomain()
        try:
            return self._json(astroextra.build_harmonic(self._payload(params)))
        except Exception:
            return self._error()

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    def relative(self, **params):
        enable_crossdomain()
        try:
            return self._json(astroextra.build_relative_score(self._payload(params)))
        except Exception:
            return self._error()
