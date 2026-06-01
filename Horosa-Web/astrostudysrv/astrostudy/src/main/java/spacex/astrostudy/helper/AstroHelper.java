package spacex.astrostudy.helper;

import java.util.HashMap;
import java.util.Map;

import boundless.exception.ErrorCodeException;
import boundless.net.http.HttpClientUtility;
import boundless.spring.help.PropertyPlaceholder;
import boundless.utility.JsonUtility;

public class AstroHelper {
	private static final boolean Debug = PropertyPlaceholder.getPropertyAsBool("devmode", false);
	private static final boolean DisableRequestCache = PropertyPlaceholder.getPropertyAsBool("astrohelper.disable.request.cache", false);
	private static final int RequestCacheExpInSec = PropertyPlaceholder.getPropertyAsInt("astrohelper.request.cache.expireinsecond", 86400);

	public static final String AstroSrvUrl = PropertyPlaceholder.getProperty("astrosrv", "http://127.0.0.1:8899");
	public static final String SolarReturn = PropertyPlaceholder.getProperty("solarreturn", "/predict/solarreturn");
	public static final String LunarReturn = PropertyPlaceholder.getProperty("lunarreturn", "/predict/lunarreturn");
	public static final String GivenYear = PropertyPlaceholder.getProperty("givenyear", "/predict/givenyear");
	public static final String SolarArc = PropertyPlaceholder.getProperty("solararc", "/predict/solararc");
	public static final String PlanetaryArc = PropertyPlaceholder.getProperty("planetaryarc", "/predict/planetaryarc");
	public static final String PersianChart = PropertyPlaceholder.getProperty("persianchart", "/predict/persianchart");
	public static final String Distribution = PropertyPlaceholder.getProperty("dist", "/predict/dist");
	public static final String AgePoint = PropertyPlaceholder.getProperty("agepoint", "/predict/agepoint");
	public static final String Profection = PropertyPlaceholder.getProperty("profection", "/predict/profection");
	public static final String PrimaryDirection = PropertyPlaceholder.getProperty("pd", "/predict/pd");
	public static final String PrimaryDirectionChart = PropertyPlaceholder.getProperty("pdchart", "/predict/pdchart");
	public static final String ZodiacalRelease = PropertyPlaceholder.getProperty("zr", "/predict/zr");
	public static final String Dice = PropertyPlaceholder.getProperty("dice", "/predict/dice");
	public static final String Chart13 = PropertyPlaceholder.getProperty("chart13", "/chart13");
	public static final String IndiaChart = PropertyPlaceholder.getProperty("indiachart", "/india/chart");
	public static final String RelativeChart = PropertyPlaceholder.getProperty("relativechart", "/modern/relative");
	public static final String MidPoint = PropertyPlaceholder.getProperty("midpoint", "/germany/midpoint");
	public static final String JieQiYear = PropertyPlaceholder.getProperty("jieqiyear", "/jieqi/year");
	public static final String JieQiBirth = PropertyPlaceholder.getProperty("jieqibirth", "/jieqi/birth");
	public static final String Nongli = PropertyPlaceholder.getProperty("nongli", "/jieqi/nongli");
	public static final String JdnDate = PropertyPlaceholder.getProperty("jdndate", "/jdn/date");
	public static final String Acg = PropertyPlaceholder.getProperty("acg", "/location/acg");
	public static final String AcgPoint = PropertyPlaceholder.getProperty("acgpoint", "/location/acgpoint");
	public static final String Azimuth = PropertyPlaceholder.getProperty("azimuth", "/calc/azimuth");
	public static final String Cotrans = PropertyPlaceholder.getProperty("cotrans", "/calc/cotrans");
	public static final String AstroExtraAnalysis = PropertyPlaceholder.getProperty("astroextra.analysis", "/astroextra/analysis");
	public static final String AstroExtraEphemeris = PropertyPlaceholder.getProperty("astroextra.ephemeris", "/astroextra/ephemeris");
	public static final String AstroExtraProgressions = PropertyPlaceholder.getProperty("astroextra.progressions", "/astroextra/progressions");
	public static final String AstroExtraJaynesProg = PropertyPlaceholder.getProperty("astroextra.jaynesprog", "/astroextra/jaynesprog");
	public static final String AstroExtraReturns = PropertyPlaceholder.getProperty("astroextra.returns", "/astroextra/returns");
	public static final String AstroExtraHarmonic = PropertyPlaceholder.getProperty("astroextra.harmonic", "/astroextra/harmonic");
	public static final String AstroExtraDraconic = PropertyPlaceholder.getProperty("astroextra.draconic", "/astroextra/draconic");
	public static final String AstroExtraGreatConj = PropertyPlaceholder.getProperty("astroextra.greatconj", "/astroextra/greatconj");
	public static final String AstroExtraRelative = PropertyPlaceholder.getProperty("astroextra.relative", "/astroextra/relative");
	public static final String PlanetariumState = PropertyPlaceholder.getProperty("planetarium.state", "/planetarium/state");
	
	private static Map<String, Object> request(String path, Map<String, Object> params){
		if(Debug || DisableRequestCache) {
			return requestNoCache(path, params);
		}
		Object obj = ParamHashCacheHelper.get(path, params, (args)->{
			return requestNoCache(path, args);
		}, RequestCacheExpInSec);
		return (Map<String, Object>)obj;
	}
	
	public static Map<String, Object> requestNoCache(String path, Map<String, Object> params){
		String url = String.format("%s%s", AstroSrvUrl, path);
		String jsonData = JsonUtility.encode(params);
		Map<String, String> headers = new HashMap<String, String>();
		Map<String, String> respHeadMap = new HashMap<String, String>();
		String str = HttpClientUtility.uploadString(url, headers, "application/json; charset=UTF-8", jsonData, respHeadMap);
		Map<String, Object> jsonres = JsonUtility.toDictionary(str);
		if(jsonres.containsKey("err")) {
			throw new ErrorCodeException(200001, jsonres.get("err").toString());
		}
		
		return jsonres;		
	}
	
	
	public static Map<String, Object> getChart(Map<String, Object> params) {
		return request("/", params);
	}
	
	public static Map<String, Object> getSolarReturn(Map<String, Object> params){
		return request(SolarReturn, params);
	}
	
	public static Map<String, Object> getLunarReturn(Map<String, Object> params){
		return request(LunarReturn, params);
	}
	
	public static Map<String, Object> getGivenYear(Map<String, Object> params){
		return request(GivenYear, params);
	}
	
	public static Map<String, Object> getSolarArc(Map<String, Object> params){
		return request(SolarArc, params);
	}

	public static Map<String, Object> getPlanetaryArc(Map<String, Object> params){
		return request(PlanetaryArc, params);
	}

	public static Map<String, Object> getPersianChart(Map<String, Object> params){
		return requestNoCache(PersianChart, params);
	}
	
	public static Map<String, Object> getProfection(Map<String, Object> params){
		return request(Profection, params);
	}

	public static Map<String, Object> getDistribution(Map<String, Object> params){
		return request(Distribution, params);
	}

	public static Map<String, Object> getAgePoint(Map<String, Object> params){
		return request(AgePoint, params);
	}
	
	public static Map<String, Object> getPrimaryDirection(Map<String, Object> params){
		return request(PrimaryDirection, params);
	}

	public static Map<String, Object> getPrimaryDirectionChart(Map<String, Object> params){
		return request(PrimaryDirectionChart, params);
	}
	
	public static Map<String, Object> getZodiacalRelease(Map<String, Object> params){
		return request(ZodiacalRelease, params);
	}
	
	public static Map<String, Object> getChart13(Map<String, Object> params){
		return request(Chart13, params);
	}
	
	public static Map<String, Object> getIndiaChart(Map<String, Object> params){
		return request(IndiaChart, params);
	}
	
	public static Map<String, Object> getRelativeChart(Map<String, Object> params){
		return request(RelativeChart, params);
	}
	
	public static Map<String, Object> getGermanyTech(Map<String, Object> params){
		return request(MidPoint, params);
	}
	
	public static Map<String, Object> getJieQiYear(Map<String, Object> params){
		return request(JieQiYear, params);
	}
	
	public static Map<String, Object> getJieQiBirth(Map<String, Object> params){
		return request(JieQiBirth, params);
	}
	
	public static Map<String, Object> getNongliMonth(Map<String, Object> params){
		return request(Nongli, params);
	}
	
	public static String getJdnDate(Map<String, Object> params){
		Map<String, Object> res = requestNoCache(JdnDate, params);
		return (String) res.get("date");
	}
	
	public static Map<String, Object> getAcg(Map<String, Object> params){
		return requestNoCache(Acg, params);
	}

	public static Map<String, Object> getAcgPoint(Map<String, Object> params){
		return requestNoCache(AcgPoint, params);
	}
	
	public static Map<String, Object> getDice(Map<String, Object> params){
		return requestNoCache(Dice, params);
	}
	
	public static Map<String, Object> getAzimuth(Map<String, Object> params){
		return requestNoCache(Azimuth, params);
	}
	
	public static Map<String, Object> getCotrans(Map<String, Object> params){
		return requestNoCache(Cotrans, params);
	}

	public static Map<String, Object> getAstroExtraAnalysis(Map<String, Object> params){
		return requestNoCache(AstroExtraAnalysis, params);
	}

	public static Map<String, Object> getAstroExtraEphemeris(Map<String, Object> params){
		return requestNoCache(AstroExtraEphemeris, params);
	}

	public static Map<String, Object> getAstroExtraProgressions(Map<String, Object> params){
		return requestNoCache(AstroExtraProgressions, params);
	}

	public static Map<String, Object> getAstroExtraJaynesProg(Map<String, Object> params){
		return requestNoCache(AstroExtraJaynesProg, params);
	}

	public static Map<String, Object> getAstroExtraReturns(Map<String, Object> params){
		return requestNoCache(AstroExtraReturns, params);
	}

	public static Map<String, Object> getAstroExtraHarmonic(Map<String, Object> params){
		return requestNoCache(AstroExtraHarmonic, params);
	}

	public static Map<String, Object> getAstroExtraDraconic(Map<String, Object> params){
		return requestNoCache(AstroExtraDraconic, params);
	}

	public static Map<String, Object> getAstroExtraGreatConj(Map<String, Object> params){
		return requestNoCache(AstroExtraGreatConj, params);
	}

	public static Map<String, Object> getAstroExtraRelative(Map<String, Object> params){
		return requestNoCache(AstroExtraRelative, params);
	}

	public static Map<String, Object> getPlanetariumState(Map<String, Object> params){
		return requestNoCache(PlanetariumState, params);
	}
		
	}
