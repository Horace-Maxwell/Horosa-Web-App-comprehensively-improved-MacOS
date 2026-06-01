package spacex.astrostudy.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import boundless.exception.ErrorCodeException;
import boundless.spring.help.interceptor.TransData;
import spacex.astrostudy.helper.AstroHelper;

@Controller
@RequestMapping("/astroextra")
public class AstroExtraController {
	private static final String[] OPTIONAL_KEYS = new String[] {
		"ad", "gpsLat", "gpsLon", "southchart", "strongRecption", "virtualPointReceiveAsp",
		"simpleAsp", "predictive", "tradition", "zodiacal", "fixedStarOrb", "startDate",
		"endDate", "startTime", "endTime", "includeTransits", "planets", "natalPoints",
		"aspects", "targetDate", "targetTime", "datetime", "orb", "startYear", "count",
		"harmonic", "inner", "outer", "relative", "altitude"
	};

	private Map<String, Object> getBaseParams(){
		Map<String, Object> params = new HashMap<String, Object>();
		if(!TransData.containsParam("date")) {
			throw new ErrorCodeException(390001, "miss.date");
		}
		if(!TransData.containsParam("time")) {
			throw new ErrorCodeException(390002, "miss.time");
		}
		if(!TransData.containsParam("zone")) {
			throw new ErrorCodeException(390003, "miss.zone");
		}
		if(!TransData.containsParam("lat")) {
			throw new ErrorCodeException(390004, "miss.lat");
		}
		if(!TransData.containsParam("lon")) {
			throw new ErrorCodeException(390005, "miss.lon");
		}
		params.put("date", TransData.get("date"));
		params.put("time", TransData.get("time"));
		params.put("zone", TransData.get("zone"));
		params.put("lat", TransData.get("lat"));
		params.put("lon", TransData.get("lon"));
		params.put("hsys", TransData.getValueAsInt("hsys", 0));
		for(String key: OPTIONAL_KEYS) {
			if(TransData.containsParam(key)) {
				params.put(key, TransData.get(key));
			}
		}
		return params;
	}

	private Map<String, Object> getGreatConjParams(){
		Map<String, Object> params = new HashMap<String, Object>();
		params.put("startYear", TransData.getValueAsInt("startYear", 1900));
		params.put("endYear", TransData.getValueAsInt("endYear", 2100));
		return params;
	}

	private Map<String, Object> getRelativeParams(){
		Map<String, Object> params = new HashMap<String, Object>();
		if(!TransData.containsParam("inner")) {
			throw new ErrorCodeException(391001, "miss.inner");
		}
		if(!TransData.containsParam("outer")) {
			throw new ErrorCodeException(391002, "miss.outer");
		}
		params.put("inner", TransData.get("inner"));
		params.put("outer", TransData.get("outer"));
		params.put("hsys", TransData.getValueAsInt("hsys", 0));
		params.put("zodiacal", TransData.getValueAsInt("zodiacal", 0));
		if(TransData.containsParam("relative")) {
			params.put("relative", TransData.get("relative"));
		}
		return params;
	}

	@ResponseBody
	@RequestMapping("/analysis")
	public void analysis(){
		TransData.set(AstroHelper.getAstroExtraAnalysis(getBaseParams()));
	}

	@ResponseBody
	@RequestMapping("/ephemeris")
	public void ephemeris(){
		TransData.set(AstroHelper.getAstroExtraEphemeris(getBaseParams()));
	}

	@ResponseBody
	@RequestMapping("/progressions")
	public void progressions(){
		TransData.set(AstroHelper.getAstroExtraProgressions(getBaseParams()));
	}

	@ResponseBody
	@RequestMapping("/jaynesprog")
	public void jaynesprog(){
		TransData.set(AstroHelper.getAstroExtraJaynesProg(getBaseParams()));
	}

	@ResponseBody
	@RequestMapping("/returns")
	public void returns(){
		TransData.set(AstroHelper.getAstroExtraReturns(getBaseParams()));
	}

	@ResponseBody
	@RequestMapping("/harmonic")
	public void harmonic(){
		TransData.set(AstroHelper.getAstroExtraHarmonic(getBaseParams()));
	}

	@ResponseBody
	@RequestMapping("/draconic")
	public void draconic(){
		TransData.set(AstroHelper.getAstroExtraDraconic(getBaseParams()));
	}

	@ResponseBody
	@RequestMapping("/greatconj")
	public void greatconj(){
		TransData.set(AstroHelper.getAstroExtraGreatConj(getGreatConjParams()));
	}

	@ResponseBody
	@RequestMapping("/relative")
	public void relative(){
		TransData.set(AstroHelper.getAstroExtraRelative(getRelativeParams()));
	}
}
