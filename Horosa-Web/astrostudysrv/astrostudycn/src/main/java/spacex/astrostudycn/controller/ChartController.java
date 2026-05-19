package spacex.astrostudycn.controller;


import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import boundless.exception.ErrorCodeException;
import boundless.spring.help.interceptor.TransData;
import boundless.utility.ConvertUtility;
import boundless.utility.JsonUtility;
import spacex.astrostudy.helper.AstroHelper;
import spacex.astrostudy.helper.NongliHelper;
import spacex.astrostudy.helper.ParamHashCacheHelper;
import spacex.astrostudy.helper.predict.PlanetSignPredictHelper;
import spacex.astrostudycn.model.OnlyFourColumns;

@Controller
public class ChartController {

	private static final int SU28_MODE_ZHENG_SIDEREAL = 4;
	private static final double ZHENG_AYANAMSHA_BASE_DEGREE = 4.0;
	private static final double ZHENG_AYANAMSHA_BASE_YEAR = 1300.0;
	private static final double PRECESSION_DEGREE_PER_YEAR = 50.290966 / 3600.0;
	private static final String[] ZHENG_SU28_NAMES = new String[] {
		"娄", "胃", "昴", "毕", "觜", "参", "井", "鬼", "柳", "星", "张", "翼", "轸", "角",
		"亢", "氐", "房", "心", "尾", "箕", "斗", "牛", "女", "虚", "危", "室", "壁", "奎"
	};
	private static final double[] ZHENG_SIDEREAL_STELLAR_RA = new double[] {
		15.9, 26.3, 41.1, 53.2, 69.0, 70.0, 81.8, 112.3, 115.2, 130.5, 136.4, 151.4, 170.1, 187.2,
		200.0, 208.9, 225.2, 230.6, 237.0, 255.6, 266.3, 290.1, 298.0, 308.9, 318.3, 333.6, 349.4, 358.3
	};

	@ResponseBody
	@RequestMapping("/chart")
	public void chart(){
		Map<String, Object> params = getParams();
		Map<String, Object> keyparams = new HashMap<String, Object>();
		keyparams.putAll(params);
		keyparams.remove("gpsLat");
		keyparams.remove("gpsLon");
		Object obj = ParamHashCacheHelper.get("/chart", keyparams, (args)->{
			Map<String, Object> astroArgs = args;
			if(ConvertUtility.getValueAsInt(args.get("doubingSu28"), 0) == SU28_MODE_ZHENG_SIDEREAL) {
				astroArgs = new HashMap<String, Object>();
				astroArgs.putAll(args);
				astroArgs.put("zodiacal", 1);
				astroArgs.put("guolaoZhengSidereal", 1);
			}
			Map<String, Object> res = AstroHelper.getChart(astroArgs);
			Map<String, Object> reqparams = (Map<String, Object>) res.get("params");
			if(reqparams != null) {
				reqparams.put("doubingSu28", args.get("doubingSu28"));
				if(args.containsKey("guolaoLifeMode")) {
					reqparams.put("guolaoLifeMode", args.get("guolaoLifeMode"));
					reqparams.put("_guolaoLifeRev", "life_cotrans_v4");
				}
				if(ConvertUtility.getValueAsInt(args.get("doubingSu28"), 0) == SU28_MODE_ZHENG_SIDEREAL) {
					reqparams.put("zodiacal", 1);
					reqparams.put("guolaoZhengSidereal", 1);
				}
			}
			int ad = ConvertUtility.getValueAsInt(args.get("ad"), 1);
			String zone = ConvertUtility.getValueAsString(args.get("zone"));
			String lon = ConvertUtility.getValueAsString(args.get("lon"));
			String lat = ConvertUtility.getValueAsString(args.get("lat"));
			String dtstr = String.format("%s %s", args.get("date"), args.get("time"));
			boolean after23NewDay = false;
			OnlyFourColumns bz = new OnlyFourColumns(ad, dtstr, zone, lon, lat, after23NewDay);
			Map<String, Object> map = bz.getNongli();
			if(res.containsKey("chart")) {
				Map<String, Object> chart = (Map<String, Object>) res.get("chart");
				String guolaoLifeMode = ConvertUtility.getValueAsString(args.get("guolaoLifeMode"));
				String guolaoSunRiseTime = reqparams == null ? null : ConvertUtility.getValueAsString(reqparams.get("guolaoSunRiseTime"));
				boolean zhengSidereal = ConvertUtility.getValueAsInt(args.get("doubingSu28"), 0) == SU28_MODE_ZHENG_SIDEREAL
					|| ConvertUtility.getValueAsInt(args.get("guolaoZhengSidereal"), 0) == 1;
				bz.genLifeMasterDeg(chart, guolaoLifeMode, guolaoSunRiseTime, zhengSidereal);
				applyZhengSiderealSu28(chart, args);
				chart.put("nongli", map);
			}else {
				res.put("nongli", map);					
			}
			
			PlanetSignPredictHelper.predictPlanetSign(res);
			syncPredictiveMetaAndRows(res, args);
			return res;
		});
		
		Map<String, Object> res = (Map<String, Object>)obj;
		setupGps(res);
		TransData.set(res);
	}
	
	@ResponseBody
	@RequestMapping("/chart13")
	public void chart13(){
		Map<String, Object> params = getParams();
		Map<String, Object> keyparams = new HashMap<String, Object>();
		keyparams.putAll(params);
		keyparams.remove("gpsLat");
		keyparams.remove("gpsLon");
		Object obj = ParamHashCacheHelper.get("/chart13", keyparams, (args)->{
			Map<String, Object> res = AstroHelper.getChart13(args);
			int ad = ConvertUtility.getValueAsInt(args.get("ad"), 1);
			NongliHelper.fillNongli(res, args, ad);
			syncPredictiveMetaAndRows(res, args);
			return res;
		});
		
		Map<String, Object> res = (Map<String, Object>)obj;
		setupGps(res);
		TransData.set(res);
	}

	private void setupGps(Map<String, Object> res) {
		Map<String, Object> reqparams = (Map<String, Object>) res.get("params");
		if(reqparams != null) {
			reqparams.put("gpsLat", TransData.get("gpsLat"));
			reqparams.put("gpsLon", TransData.get("gpsLon"));
		}
	}

	private void applyZhengSiderealSu28(Map<String, Object> chart, Map<String, Object> args) {
		if(chart == null || args == null || ConvertUtility.getValueAsInt(args.get("doubingSu28"), 0) != SU28_MODE_ZHENG_SIDEREAL) {
			return;
		}
		double ayanamsha = zhengAyanamsha(args);
		List<Map<String, Object>> stars = new ArrayList<Map<String, Object>>();
		for(int i=0; i<ZHENG_SU28_NAMES.length; i++) {
			Map<String, Object> row = new HashMap<String, Object>();
			row.put("name", ZHENG_SU28_NAMES[i]);
			row.put("ra", normalizeDegree(ZHENG_SIDEREAL_STELLAR_RA[i]));
			row.put("siderealRa", ZHENG_SIDEREAL_STELLAR_RA[i]);
			row.put("source", "zheng-sidereal");
			stars.add(row);
		}
		Collections.sort(stars, new Comparator<Map<String, Object>>() {
			@Override
			public int compare(Map<String, Object> a, Map<String, Object> b) {
				return Double.compare(number(a.get("ra"), 0), number(b.get("ra"), 0));
			}
		});
		chart.put("fixedStarSu28", stars);
		chart.put("su28Mode", SU28_MODE_ZHENG_SIDEREAL);
		chart.put("su28ModeName", "郑式恒星制");
		chart.put("su28Ayanamsha", ayanamsha);

		Object rawObjects = chart.get("objects");
		if(!(rawObjects instanceof List)) {
			return;
		}
		List<Map<String, Object>> objects = (List<Map<String, Object>>) rawObjects;
		for(Map<String, Object> obj : objects) {
			double ra = normalizeDegree(number(obj.get("ra"), number(obj.get("lon"), 0)));
			Map<String, Object> star = su28ForDegree(stars, ra);
			if(star != null) {
				obj.put("su28", star.get("name"));
				obj.put("su28Mode", "zheng-sidereal");
			}
		}
	}

	private Map<String, Object> su28ForDegree(List<Map<String, Object>> stars, double ra) {
		if(stars == null || stars.isEmpty()) {
			return null;
		}
		Map<String, Object> star = stars.get(stars.size() - 1);
		for(Map<String, Object> item : stars) {
			if(number(item.get("ra"), 0) <= ra) {
				star = item;
			}else {
				break;
			}
		}
		return star;
	}

	private double zhengAyanamsha(Map<String, Object> args) {
		return normalizeDegree(ZHENG_AYANAMSHA_BASE_DEGREE
			+ (decimalYear(args) - ZHENG_AYANAMSHA_BASE_YEAR) * PRECESSION_DEGREE_PER_YEAR);
	}

	private double decimalYear(Map<String, Object> args) {
		String date = ConvertUtility.getValueAsString(args.get("date"));
		int ad = ConvertUtility.getValueAsInt(args.get("ad"), 1);
		date = date == null ? "" : date.trim().replace('/', '-');
		boolean negative = date.startsWith("-");
		if(negative) {
			date = date.substring(1);
		}
		String[] parts = date.split("-");
		int year = parts.length > 0 ? ConvertUtility.getValueAsInt(parts[0], 2000) : 2000;
		int month = parts.length > 1 ? ConvertUtility.getValueAsInt(parts[1], 1) : 1;
		int day = parts.length > 2 ? ConvertUtility.getValueAsInt(parts[2], 1) : 1;
		if(negative || ad < 0) {
			year = -Math.abs(year);
		}
		month = Math.max(1, Math.min(12, month));
		day = Math.max(1, Math.min(31, day));
		return year + ((month - 1) * 30.4375 + (day - 1)) / 365.25;
	}

	private double normalizeDegree(double val) {
		double res = val % 360.0;
		return res < 0 ? res + 360.0 : res;
	}

	private double number(Object obj, double def) {
		if(obj instanceof Number) {
			return ((Number) obj).doubleValue();
		}
		try{
			return Double.parseDouble(ConvertUtility.getValueAsString(obj));
		}catch(Exception ex) {
			return def;
		}
	}

	private void syncPredictiveMetaAndRows(Map<String, Object> res, Map<String, Object> args) {
		if(res == null || args == null) {
			return;
		}
		Map<String, Object> reqparams = (Map<String, Object>) res.get("params");
		if(reqparams != null) {
			reqparams.put("pdSyncRev", "pd_method_sync_v8");
			reqparams.put("showPdBounds", ConvertUtility.getValueAsInt(args.get("showPdBounds"), 1));
			if(args.containsKey("pdtype")) {
				reqparams.put("pdtype", args.get("pdtype"));
			}
			if(args.containsKey("pdMethod")) {
				reqparams.put("pdMethod", args.get("pdMethod"));
			}
			if(args.containsKey("pdTimeKey")) {
				reqparams.put("pdTimeKey", args.get("pdTimeKey"));
			}
		}

		if(!ConvertUtility.getValueAsBool(args.get("predictive"), false)) {
			return;
		}
		if(!ConvertUtility.getValueAsBool(args.get("includePrimaryDirection"), false)) {
			return;
		}
		Map<String, Object> pdres = AstroHelper.getPrimaryDirection(args);
		if(pdres == null || !pdres.containsKey("pd")) {
			return;
		}
		Map<String, Object> predictives = (Map<String, Object>) res.get("predictives");
		if(predictives == null) {
			predictives = new HashMap<String, Object>();
			res.put("predictives", predictives);
		}
		predictives.put("primaryDirection", pdres.get("pd"));
	}
	
	private Map<String, Object> getParams(){
		Map<String, Object> params = new HashMap<String, Object>();
		if(!TransData.containsParam("date")) {
			throw new ErrorCodeException(100001, "miss.date");
		}
		if(!TransData.containsParam("time")) {
			throw new ErrorCodeException(100002, "miss.time");
		}
		if(!TransData.containsParam("zone")) {
			throw new ErrorCodeException(100003, "miss.zone");
		}
		if(!TransData.containsParam("lat")) {
			throw new ErrorCodeException(100004, "miss.lat");
		}
		if(!TransData.containsParam("lon")) {
			throw new ErrorCodeException(100005, "miss.lon");
		}
		params.put("date", TransData.get("date"));
		params.put("time", TransData.get("time"));
		if(TransData.containsParam("ad")) {
			int ad = TransData.getValueAsInt("ad", 1);
			params.put("ad", ad);
			if(ad != 1) {
				String dt = TransData.getValueAsString("date");
				if(dt.indexOf('-') != 0) {
					params.put("date", "-" + dt);
				}
			}			
		}else {
			String dt = TransData.getValueAsString("date");
			if(dt.indexOf('-') == 0) {
				params.put("ad", -1);
			}
		}
		params.put("zone", TransData.get("zone"));
		params.put("lat", TransData.get("lat"));
		params.put("lon", TransData.get("lon"));
		// Bust legacy local/runtime cache entries after PD method/time-key response wiring changes.
		params.put("_wireRev", "pd_method_sync_v8");
		if(TransData.containsParam("_su28Rev")) {
			params.put("_su28Rev", TransData.get("_su28Rev"));
		}
		params.put("hsys", TransData.getValueAsInt("hsys", 0));
		params.put("tradition", TransData.getValueAsBool("tradition", false));
		params.put("doubingSu28", getSu28Mode());
		if(TransData.containsParam("guolaoLifeMode")) {
			params.put("guolaoLifeMode", TransData.get("guolaoLifeMode"));
			params.put("_guolaoLifeRev", "life_cotrans_v4");
		}
		params.put("strongRecption", TransData.getValueAsBool("strongRecption", false));
		params.put("virtualPointReceiveAsp", TransData.getValueAsBool("virtualPointReceiveAsp", false));
		params.put("simpleAsp", TransData.getValueAsBool("simpleAsp", false));
		params.put("predictive", TransData.getValueAsBool("predictive", true));
		params.put("includePrimaryDirection", TransData.getValueAsBool("includePrimaryDirection", false));
		params.put("southchart", TransData.getValueAsBool("southchart", false));
		if(TransData.containsParam("pdaspects")) {
			Object aspobj = TransData.get("pdaspects");
			if(aspobj instanceof String) {
				aspobj = JsonUtility.decodeList((String)aspobj, String.class);
			}
			params.put("pdaspects", aspobj);
		}
		if(TransData.containsParam("pdtype")) {
			params.put("pdtype", TransData.get("pdtype"));
		}
		if(TransData.containsParam("pdMethod")) {
			params.put("pdMethod", TransData.get("pdMethod"));
		}
		if(TransData.containsParam("pdTimeKey")) {
			params.put("pdTimeKey", TransData.get("pdTimeKey"));
		}
		if(TransData.containsParam("zodiacal")) {
			params.put("zodiacal", TransData.get("zodiacal"));
		}else {
			params.put("zodiacal", 0);
		}
		if(TransData.containsParam("gpsLat")) {
			params.put("gpsLat", TransData.get("gpsLat"));
			params.put("gpsLon", TransData.get("gpsLon"));
		}
		
		return params;
	}

	private int getSu28Mode() {
		if(!TransData.containsParam("doubingSu28")) {
			return 0;
		}
		Object raw = TransData.get("doubingSu28");
		if(raw instanceof Number) {
			return ((Number) raw).intValue();
		}
		if(raw instanceof Boolean) {
			return ((Boolean) raw) ? 1 : 0;
		}
		String val = ConvertUtility.getValueAsString(raw);
		if("true".equalsIgnoreCase(val)) {
			return 1;
		}
		if("false".equalsIgnoreCase(val)) {
			return 0;
		}
		return ConvertUtility.getValueAsInt(raw, 0);
	}
}
