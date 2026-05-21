import traceback
import jsonpickle
import cherrypy
from websrv.helper import enable_crossdomain
from astrostudy.india.india_chart_kernel import IndiaChartKernel
from astrostudy.india.jyotish_engine import build_jyotish
from astrostudy.india.varga import apply_varga_chart, normalize_chartnum


def getIndiaChartJson(data, indiachart, jyotish=None):
    obj = indiachart.to_response(data, jyotish)
    if jyotish is not None:
        obj['jyotish'] = jyotish
    return jsonpickle.encode(obj, unpicklable=False)


class IndiaAstroSrv:
    exposed = True

    def OPTIONS(*args, **kwargs):
        enable_crossdomain()


    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    def chart(self):
        enable_crossdomain()
        try:
            data = cherrypy.request.json

            data['tradition'] = False
            data['predictive'] = False
            data['zodiacal'] = 1
            data['hsys'] = data.get('indiaHsys', data.get('hsys', 0))
            data['siderealMode'] = data.get('indiaAyanamsa', data.get('ayanamsa', data.get('siderealMode', 'lahiri')))
            chartnum = 1
            if 'chartnum' in data.keys():
                try:
                    chartnum = int(data['chartnum'])
                except:
                    chartnum = 1
            chartnum = normalize_chartnum(chartnum)

            perchart = IndiaChartKernel(data)
            try:
                jyotish = build_jyotish(perchart)
            except:
                traceback.print_exc()
                jyotish = {
                    'engine': {
                        'name': 'Horosa JyotishEngine',
                        'version': '0.1.0',
                        'ephemeris': 'Horosa Swiss Ephemeris / IndiaChartKernel',
                        'source': 'chart_json_only',
                        'chartnum': 1,
                    },
                    'error': 'jyotish calculation error'
                }
            apply_varga_chart(perchart, chartnum)

            res = getIndiaChartJson(data, perchart, jyotish)
            return res
        except:
            traceback.print_exc()
            obj = {
                'err': 'param error'
            }
            return jsonpickle.encode(obj, unpicklable=False)
