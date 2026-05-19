package spacex.astrostudycn.service;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class QizhengMoiraRuleService {

	private static final String[] SIGN_IDS = new String[] {
		"Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
		"Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
	};

	private static final String[] SIGN_NAMES = new String[] {
		"白羊", "金牛", "双子", "巨蟹", "狮子", "处女",
		"天秤", "天蝎", "射手", "摩羯", "水瓶", "双鱼"
	};

	private static final String[] SIGN_ZI = new String[] {
		"戌", "酉", "申", "未", "午", "巳", "辰", "卯", "寅", "丑", "子", "亥"
	};

	private static final String[] SIGN_AREAS = new String[] {
		"降娄", "大梁", "实沉", "鹑首", "鹑火", "鹑尾",
		"寿星", "大火", "析木", "星纪", "玄枵", "娵訾"
	};

	private static final String[] MOIRA_HOUSE_NAMES = new String[] {
		"命宫", "财帛", "兄弟", "田宅", "男女", "奴仆",
		"夫妻", "疾厄", "迁移", "官禄", "福德", "相貌"
	};

	private static final String[] MOIRA_STAR_HOUSES = new String[] {
		"命宫", "相貌", "福德", "官禄", "迁移", "疾厄",
		"夫妻", "奴仆", "男女", "田宅", "兄弟", "财帛"
	};

	private static final String[] PLANET_ORDER = new String[] {
		"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
		"North Node", "South Node", "Purple Clouds", "Dark Moon"
	};

	private static final Map<String, String> PLANET_NAMES = new HashMap<String, String>();
	private static final Map<String, String> RULERS = new HashMap<String, String>();
	private static final Map<String, String> EXALTS = new HashMap<String, String>();
	private static final Map<String, String> EXILES = new HashMap<String, String>();
	private static final Map<String, String> FALLS = new HashMap<String, String>();
	private static final Set<String> QIZHENG = new HashSet<String>();
	private static final Set<String> SIYU = new HashSet<String>();
	private static final Set<String> GOOD_GODS = new HashSet<String>();
	private static final Set<String> BAD_GODS = new HashSet<String>();
	private static final Map<String, String> PLANET_IDS_BY_CN = new HashMap<String, String>();
	private static final Map<String, String> OVERCOMING = new HashMap<String, String>();
	private static final String LIFE_MODE_ASC = "asc";
	private static final String LIFE_MODE_YUMAO = "yumao";
	private static final String LIFE_MODE_COTRANS = "cotrans";

	static {
		PLANET_NAMES.put("Sun", "日");
		PLANET_NAMES.put("Moon", "月");
		PLANET_NAMES.put("Mercury", "水");
		PLANET_NAMES.put("Venus", "金");
		PLANET_NAMES.put("Mars", "火");
		PLANET_NAMES.put("Jupiter", "木");
		PLANET_NAMES.put("Saturn", "土");
		PLANET_NAMES.put("North Node", "罗");
		PLANET_NAMES.put("South Node", "计");
		PLANET_NAMES.put("Purple Clouds", "炁");
		PLANET_NAMES.put("Dark Moon", "孛");
		PLANET_NAMES.put("Pars Fortuna", "福");
		PLANET_NAMES.put("Asc", "升");
		PLANET_NAMES.put("MC", "顶");
		PLANET_NAMES.put("LifeMasterDeg74", "命度");
		for(Map.Entry<String, String> entry : PLANET_NAMES.entrySet()) {
			PLANET_IDS_BY_CN.put(entry.getValue(), entry.getKey());
		}

		QIZHENG.addAll(Arrays.asList("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"));
		SIYU.addAll(Arrays.asList("North Node", "South Node", "Purple Clouds", "Dark Moon"));

		RULERS.put("Aries", "Mars");
		RULERS.put("Taurus", "Venus");
		RULERS.put("Gemini", "Mercury");
		RULERS.put("Cancer", "Moon");
		RULERS.put("Leo", "Sun");
		RULERS.put("Virgo", "Mercury");
		RULERS.put("Libra", "Venus");
		RULERS.put("Scorpio", "Mars");
		RULERS.put("Sagittarius", "Jupiter");
		RULERS.put("Capricorn", "Saturn");
		RULERS.put("Aquarius", "Saturn");
		RULERS.put("Pisces", "Jupiter");

		EXALTS.put("Aries", "Sun");
		EXALTS.put("Taurus", "Moon");
		EXALTS.put("Cancer", "Jupiter");
		EXALTS.put("Virgo", "Mercury");
		EXALTS.put("Libra", "Saturn");
		EXALTS.put("Capricorn", "Mars");
		EXALTS.put("Pisces", "Venus");

		EXILES.put("Aries", "Venus");
		EXILES.put("Taurus", "Mars");
		EXILES.put("Gemini", "Jupiter");
		EXILES.put("Cancer", "Saturn");
		EXILES.put("Leo", "Saturn");
		EXILES.put("Virgo", "Jupiter");
		EXILES.put("Libra", "Mars");
		EXILES.put("Scorpio", "Venus");
		EXILES.put("Sagittarius", "Mercury");
		EXILES.put("Capricorn", "Moon");
		EXILES.put("Aquarius", "Sun");
		EXILES.put("Pisces", "Mercury");

		FALLS.put("Aries", "Saturn");
		FALLS.put("Virgo", "Venus");
		FALLS.put("Libra", "Sun");
		FALLS.put("Scorpio", "Moon");
		FALLS.put("Capricorn", "Jupiter");
		FALLS.put("Pisces", "Mercury");

		GOOD_GODS.addAll(Arrays.asList("禄勋", "文昌", "天喜", "国印", "天德", "天贵", "岁驾", "斗杓", "驿马", "红鸾", "解神", "玉贵", "紫微", "华盖", "卦气", "唐符", "天厨"));
		BAD_GODS.addAll(Arrays.asList("大耗", "剑锋", "飞廉", "病符", "死符", "天雄", "天哭", "天狗", "地耗", "天耗", "阳刃", "劫杀", "的杀", "空亡", "天空", "孤辰", "寡宿", "咸池", "亡神", "六害", "血刃"));

		OVERCOMING.put("日", "月");
		OVERCOMING.put("月", "日");
		OVERCOMING.put("金", "火");
		OVERCOMING.put("木", "金");
		OVERCOMING.put("水", "土");
		OVERCOMING.put("火", "水");
		OVERCOMING.put("土", "木");
		OVERCOMING.put("炁", "金");
		OVERCOMING.put("孛", "土");
		OVERCOMING.put("罗", "水");
		OVERCOMING.put("计", "木");
	}

	public Map<String, Object> analyze(Map<String, Object> chartObj, Map<String, Object> params) {
		Map<String, Object> result = new LinkedHashMap<String, Object>();
		Map<String, Object> chart = asMap(chartObj.get("chart"));
		List<Object> objects = asList(chart.get("objects"));
		List<Object> houses = asList(chart.get("houses"));
		Map<String, Map<String, Object>> byId = indexObjects(objects);
		Map<String, Map<String, Object>> houseById = indexHouses(houses);

		String lifeMode = lifeMode(params);
		Map<String, Object> lifeObj = (LIFE_MODE_YUMAO.equals(lifeMode) || LIFE_MODE_COTRANS.equals(lifeMode))
			? firstPresent(byId, "LifeMasterDeg74", "Asc", "Sun")
			: firstPresent(byId, "Asc", "LifeMasterDeg74", "Sun");
		Map<String, Object> selfObj = firstPresent(byId, "Moon", "LifeMasterDeg74", "Asc");
		double lifeLon = normalizeDegree(position(lifeObj));
		double selfLon = normalizeDegree(position(selfObj));
		int lifeSignIndex = signIndex(lifeLon);
		int selfSignIndex = signIndex(selfLon);

		List<Map<String, Object>> moiraHouses = buildMoiraHouses(lifeSignIndex);
		List<Map<String, Object>> planets = buildPlanetRows(byId, houseById, lifeSignIndex);
		List<Map<String, Object>> godHits = buildGodHits(chartObj, chart, lifeSignIndex);
		List<Map<String, Object>> patternHints = buildPatternHints(planets, godHits, lifeSignIndex);
		List<Map<String, Object>> patterns = evaluateMoiraStylePatterns(chart, byId, params, lifeSignIndex, selfSignIndex, godHits);

		Map<String, Object> anchors = new LinkedHashMap<String, Object>();
		anchors.put("life", point("命度", lifeObj, lifeLon, lifeSignIndex, moiraHouseName(lifeSignIndex, lifeSignIndex)));
		anchors.put("self", point("身度", selfObj, selfLon, selfSignIndex, moiraHouseName(selfSignIndex, lifeSignIndex)));
		anchors.put("lifeSignIndex", lifeSignIndex);
		anchors.put("lifeSignName", signLabel(lifeSignIndex));
		anchors.put("lifeZi", signZi(lifeSignIndex));
		anchors.put("lifeMode", lifeMode);
		anchors.put("lifeModeName", lifeModeName(lifeMode));

		result.put("engine", "horosa-ephemeris-moira-layout");
		result.put("engineLabel", "Moira版式层");
		result.put("version", "qizheng-moira-layout-v3");
		result.put("isFallback", false);
		result.put("lifeMode", lifeMode);
		result.put("lifeModeName", lifeModeName(lifeMode));
		result.put("styleSource", "moira-dsl-evaluated");
		result.put("styleWarning", "");
		result.put("params", params == null ? Collections.emptyMap() : params);
		result.put("anchors", anchors);
		result.put("houses", moiraHouses);
		result.put("planets", planets);
		result.put("godHits", godHits);
		result.put("patterns", patterns);
		result.put("patternHints", patternHints);
		result.put("summary", buildSummary(anchors, patterns, planets, godHits));
		result.put("snapshot", buildSnapshot(anchors, patterns, planets, godHits));
		return result;
	}

	private List<Map<String, Object>> buildMoiraHouses(int lifeSignIndex) {
		List<Map<String, Object>> rows = new ArrayList<Map<String, Object>>();
		for(int i=0; i<12; i++) {
			int idx = wrap(lifeSignIndex + i, 12);
			Map<String, Object> row = new LinkedHashMap<String, Object>();
			row.put("index", i + 1);
			row.put("name", MOIRA_HOUSE_NAMES[i]);
			row.put("moiraStarHouse", MOIRA_STAR_HOUSES[wrap(idx + 2, 12)]);
			row.put("sign", SIGN_IDS[idx]);
			row.put("signName", signLabel(idx));
			row.put("zi", signZi(idx));
			row.put("area", SIGN_AREAS[idx]);
			rows.add(row);
		}
		return rows;
	}

	private List<Map<String, Object>> buildPlanetRows(Map<String, Map<String, Object>> byId, Map<String, Map<String, Object>> houseById, int lifeSignIndex) {
		List<Map<String, Object>> rows = new ArrayList<Map<String, Object>>();
		for(String id : PLANET_ORDER) {
			Map<String, Object> obj = byId.get(id);
			if(obj == null) {
				continue;
			}
			double lon = normalizeDegree(position(obj));
			int idx = signIndex(lon);
			Map<String, Object> row = new LinkedHashMap<String, Object>();
			row.put("id", id);
			row.put("name", planetName(id));
			row.put("longitude", round(lon, 4));
			row.put("degreeText", degreeText(lon));
			row.put("sign", str(obj.get("sign"), SIGN_IDS[idx]));
			row.put("signName", signLabel(idx));
			row.put("zi", signZi(idx));
			row.put("su28", str(obj.get("su28"), ""));
			row.put("speed", round(num(obj.get("lonspeed"), 0), 6));
			row.put("retrograde", num(obj.get("lonspeed"), 0) < 0);
			row.put("moiraHouse", moiraHouseName(idx, lifeSignIndex));
			row.put("moiraHouseIndex", moiraHouseIndex(idx, lifeSignIndex));
			row.put("dignity", dignity(id, str(obj.get("sign"), SIGN_IDS[idx])));
			Object houseId = obj.get("house");
			row.put("horosaHouse", houseLabel(houseId, houseById));
			row.put("kind", QIZHENG.contains(id) ? "七政" : "四余");
			rows.add(row);
		}
		return rows;
	}

	private List<Map<String, Object>> buildGodHits(Map<String, Object> chartObj, Map<String, Object> chart, int lifeSignIndex) {
		List<Map<String, Object>> rows = new ArrayList<Map<String, Object>>();
		Map<String, Object> ziGods = resolveZiGods(chartObj, chart);
		if(ziGods.isEmpty()) {
			return rows;
		}
		for(int i=0; i<12; i++) {
			int signIdx = wrap(lifeSignIndex + i, 12);
			String zi = signZi(signIdx);
			Map<String, Object> one = asMap(ziGods.get(zi));
			List<String> good = stringList(one.get("goodGods"));
			List<String> neutral = stringList(one.get("neutralGods"));
			List<String> bad = stringList(one.get("badGods"));
			List<String> tai = stringList(one.get("taisuiGods"));
			List<String> importantGood = intersect(good, GOOD_GODS);
			List<String> importantBad = intersect(bad, BAD_GODS);
			if(good.isEmpty() && neutral.isEmpty() && bad.isEmpty() && tai.isEmpty()) {
				continue;
			}
			Map<String, Object> row = new LinkedHashMap<String, Object>();
			row.put("house", MOIRA_HOUSE_NAMES[i]);
			row.put("houseIndex", i + 1);
			row.put("signName", signLabel(signIdx));
			row.put("zi", zi);
			row.put("goodGods", good);
			row.put("neutralGods", neutral);
			row.put("badGods", bad);
			row.put("taisuiGods", tai);
			row.put("importantGood", importantGood);
			row.put("importantBad", importantBad);
			rows.add(row);
		}
		return rows;
	}

	private List<Map<String, Object>> buildPatternHints(List<Map<String, Object>> planets, List<Map<String, Object>> godHits, int lifeSignIndex) {
		List<Map<String, Object>> patterns = new ArrayList<Map<String, Object>>();
		Map<String, Integer> pHouse = new HashMap<String, Integer>();
		Map<Integer, List<String>> byHouse = new HashMap<Integer, List<String>>();
		for(Map<String, Object> p : planets) {
			String id = str(p.get("id"), "");
			int h = (int) num(p.get("moiraHouseIndex"), 0);
			pHouse.put(id, h);
			if(!byHouse.containsKey(h)) {
				byHouse.put(h, new ArrayList<String>());
			}
			byHouse.get(h).add(str(p.get("name"), id));
		}

		addSunMoonPattern(patterns, pHouse);
		addFourRemaindersPattern(patterns, pHouse);
		addClusterPatterns(patterns, byHouse);
		addPairPattern(patterns, pHouse, "Mercury", "Venus", "金水相涵", "金水同宫，按 Horosa 近似规则作提示。");
		addPairPattern(patterns, pHouse, "Mars", "Saturn", "火土高强", "火土同宫，按 Horosa 近似规则作提示。");
		addPairPattern(patterns, pHouse, "Jupiter", "Purple Clouds", "木炁连枝", "木炁同宫，按 Horosa 近似规则作提示。");
		addGodPattern(patterns, godHits);

		if(patterns.isEmpty()) {
			Map<String, Object> p = new LinkedHashMap<String, Object>();
			p.put("name", "未触发收录格局");
			p.put("level", "neutral");
			p.put("detail", "当前仅按 Horosa 近似提示规则检查，没有命中强提示项。");
			patterns.add(p);
		}
		return patterns;
	}

	private List<Map<String, Object>> evaluateMoiraStylePatterns(Map<String, Object> chart, Map<String, Map<String, Object>> byId, Map<String, Object> params, int lifeSignIndex, int selfSignIndex, List<Map<String, Object>> godHits) {
		MoiraStyleContext ctx = new MoiraStyleContext(chart, byId, params, lifeSignIndex, selfSignIndex, godHits);
		List<MoiraStyleRule> rules = new ArrayList<MoiraStyleRule>();
		rules.add(new MoiraStyleRule("八杀朝天", "good", "3.2.0", "@{@{疾厄}[1]}=@命 & (@命[0]=戌 | @命[0]=亥)"));
		rules.add(new MoiraStyleRule("孤月独明", "good", "2.3.0", "?{孤月} & ?夜"));
		rules.add(new MoiraStyleRule("日月拱官", "good", "2.3.0", "@日=@官禄+4 & @月=@官禄-4 | @日=@官禄-4 & @月=@官禄+4"));
		rules.add(new MoiraStyleRule("金水相涵", "good", "2.3.0", "?{金水会} & !?冬"));
		rules.add(new MoiraStyleRule("日月拱贵人", "good", "2.2.0", "?昼 & (@日=@{天贵}+4 & @月=@{天贵}-4 | @日=@{天贵}-4 & @月=@{天贵}+4) | ?夜 & (@日=@{玉贵}+4 & @月=@{玉贵}-4 | @日=@{玉贵}-4 & @月=@{玉贵}+4)"));
		rules.add(new MoiraStyleRule("命登岁驾", "good", "2.0.3", "@命=@{岁驾}"));
		rules.add(new MoiraStyleRule("日月失所", "bad", "2.3.0", "(?{日西} | ?{日北}) & (?{月东} | ?{月南})"));
		rules.add(new MoiraStyleRule("官福失垣", "bad", "2.2.0", "?{官失垣} & ?{福失垣}"));
		rules.add(new MoiraStyleRule("孛犯太阳", "bad", "2.2.0", "?{日孛遇}"));
		rules.add(new MoiraStyleRule("罗犯太阳", "bad", "2.2.0", "?{日罗遇}"));
		rules.add(new MoiraStyleRule("孛罗交战", "bad", "2.2.0", "?{罗孛遇}"));
		rules.add(new MoiraStyleRule("命坐两歧", "bad", "2.0.4", "?{命宫歧} | ?{命宿歧}"));

		List<Map<String, Object>> patterns = new ArrayList<Map<String, Object>>();
		for(MoiraStyleRule rule : rules) {
			if(ctx.eval(rule.expr)) {
				Map<String, Object> item = new LinkedHashMap<String, Object>();
				item.put("name", rule.name);
				item.put("level", rule.level);
				item.put("score", rule.score);
				item.put("source", "moira_s.prop");
				item.put("dsl", rule.expr);
				item.put("detail", ("good".equals(rule.level) ? "政余喜格" : "政余忌格") + "：" + rule.name + "。");
				patterns.add(item);
			}
		}
		Collections.sort(patterns, new Comparator<Map<String, Object>>() {
			@Override
			public int compare(Map<String, Object> a, Map<String, Object> b) {
				int la = "good".equals(str(a.get("level"), "")) ? 0 : 1;
				int lb = "good".equals(str(b.get("level"), "")) ? 0 : 1;
				if(la != lb) {
					return la - lb;
				}
				return 0;
			}
		});
		return patterns;
	}

	private void addSunMoonPattern(List<Map<String, Object>> patterns, Map<String, Integer> pHouse) {
		Integer sun = pHouse.get("Sun");
		Integer moon = pHouse.get("Moon");
		if(sun == null || moon == null) {
			return;
		}
		if((sun == 2 && moon == 12) || (sun == 12 && moon == 2)) {
			addPattern(patterns, "日月夹命", "good", "日月分居命宫前后，按 Horosa 近似规则作提示。");
		}
		if((sun == 5 && moon == 9) || (sun == 9 && moon == 5)) {
			addPattern(patterns, "日月拱命", "good", "日月在三方拱照命宫，按 Horosa 近似规则作提示。");
		}
	}

	private void addFourRemaindersPattern(List<Map<String, Object>> patterns, Map<String, Integer> pHouse) {
		List<Integer> houses = new ArrayList<Integer>();
		for(String id : Arrays.asList("North Node", "South Node", "Purple Clouds", "Dark Moon")) {
			Integer h = pHouse.get(id);
			if(h != null) {
				houses.add(h);
			}
		}
		if(houses.size() < 4) {
			return;
		}
		Set<Integer> unique = new HashSet<Integer>(houses);
		if(unique.size() == 4) {
			addPattern(patterns, "四余独步", "good", "炁、孛、罗、计分居四宫，按 Horosa 近似规则作提示。");
		}
	}

	private void addClusterPatterns(List<Map<String, Object>> patterns, Map<Integer, List<String>> byHouse) {
		for(Map.Entry<Integer, List<String>> entry : byHouse.entrySet()) {
			List<String> names = entry.getValue();
			if(names.size() >= 3) {
				addPattern(patterns, "政余聚宫", "notice", MOIRA_HOUSE_NAMES[entry.getKey() - 1] + "见" + join(names, "、") + "，宜细看同宫生克与神煞。");
			}
		}
	}

	private void addPairPattern(List<Map<String, Object>> patterns, Map<String, Integer> pHouse, String a, String b, String name, String detail) {
		Integer ha = pHouse.get(a);
		Integer hb = pHouse.get(b);
		if(ha != null && hb != null && ha.intValue() == hb.intValue()) {
			addPattern(patterns, name, "good", detail);
		}
	}

	private void addGodPattern(List<Map<String, Object>> patterns, List<Map<String, Object>> godHits) {
		for(Map<String, Object> row : godHits) {
			if(((int) num(row.get("houseIndex"), 0)) != 1) {
				continue;
			}
			List<String> good = stringList(row.get("importantGood"));
			List<String> bad = stringList(row.get("importantBad"));
			if(!good.isEmpty()) {
				addPattern(patterns, "命临吉曜", "good", "命宫见" + join(good, "、") + "。");
			}
			if(!bad.isEmpty()) {
				addPattern(patterns, "命临忌曜", "bad", "命宫见" + join(bad, "、") + "，按 Horosa 近似规则提示需谨慎解读。");
			}
		}
	}

	private void addPattern(List<Map<String, Object>> patterns, String name, String level, String detail) {
		Map<String, Object> p = new LinkedHashMap<String, Object>();
		p.put("name", name);
		p.put("level", level);
		p.put("detail", detail);
		patterns.add(p);
	}

	private String buildSummary(Map<String, Object> anchors, List<Map<String, Object>> patterns, List<Map<String, Object>> planets, List<Map<String, Object>> godHits) {
		Map<String, Object> life = asMap(anchors.get("life"));
		int good = 0;
		int bad = 0;
		for(Map<String, Object> p : patterns) {
			String level = str(p.get("level"), "");
			if("good".equals(level)) {
				good++;
			}else if("bad".equals(level)) {
				bad++;
			}
		}
		return "命度采用" + str(anchors.get("lifeModeName"), "占星上升") + "，落" + str(life.get("signName"), "") + "（" + str(life.get("zi"), "") + "），"
			+ "Moira 政余格局 DSL 已接入当前七政盘：命中喜格 " + good + " 条、忌格 " + bad + " 条。";
	}

	private String buildSnapshot(Map<String, Object> anchors, List<Map<String, Object>> patterns, List<Map<String, Object>> planets, List<Map<String, Object>> godHits) {
		StringBuilder sb = new StringBuilder();
		sb.append("[Moira版式层]\n");
		sb.append(buildSummary(anchors, patterns, planets, godHits)).append("\n\n");
		sb.append("[格局]\n");
		if(patterns.isEmpty()) {
			sb.append("当前盘未命中已接入的 Moira 政余喜格/忌格。\n");
		}else {
			for(Map<String, Object> p : patterns) {
				sb.append(str(p.get("name"), "")).append("：").append(str(p.get("detail"), "")).append("\n");
			}
		}
		sb.append("\n[星曜]\n");
		for(Map<String, Object> p : planets) {
			sb.append(str(p.get("name"), "")).append("：")
				.append(str(p.get("moiraHouse"), "")).append(" ")
				.append(str(p.get("signName"), "")).append(" ")
				.append(str(p.get("degreeText"), "")).append(" ")
				.append(str(p.get("su28"), "")).append("\n");
		}
		return sb.toString();
	}

	private Map<String, Object> point(String label, Map<String, Object> obj, double lon, int signIdx, String houseName) {
		Map<String, Object> point = new LinkedHashMap<String, Object>();
		point.put("label", label);
		point.put("sourceId", obj == null ? "" : str(obj.get("id"), ""));
		point.put("longitude", round(lon, 4));
		point.put("degreeText", degreeText(lon));
		point.put("sign", SIGN_IDS[signIdx]);
		point.put("signName", signLabel(signIdx));
		point.put("zi", signZi(signIdx));
		point.put("area", SIGN_AREAS[signIdx]);
		point.put("moiraHouse", houseName);
		return point;
	}

	private Map<String, Object> resolveZiGods(Map<String, Object> chartObj, Map<String, Object> chart) {
		Map<String, Object> nongli = asMap(chart.get("nongli"));
		Map<String, Object> bazi = asMap(nongli.get("bazi"));
		Map<String, Object> gl = asMap(bazi.get("guolaoGods"));
		Map<String, Object> ziGods = asMap(gl.get("ziGods"));
		if(!ziGods.isEmpty()) {
			return ziGods;
		}
		nongli = asMap(chartObj.get("nongli"));
		bazi = asMap(nongli.get("bazi"));
		gl = asMap(bazi.get("guolaoGods"));
		return asMap(gl.get("ziGods"));
	}

	private String dignity(String id, String sign) {
		if(id.equals(RULERS.get(sign))) {
			return "入垣";
		}
		if(id.equals(EXALTS.get(sign))) {
			return "升殿";
		}
		if(id.equals(EXILES.get(sign))) {
			return "失垣";
		}
		if(id.equals(FALLS.get(sign))) {
			return "落陷";
		}
		return "平";
	}

	private Map<String, Map<String, Object>> indexObjects(List<Object> objects) {
		Map<String, Map<String, Object>> map = new HashMap<String, Map<String, Object>>();
		for(Object item : objects) {
			Map<String, Object> obj = asMap(item);
			String id = str(obj.get("id"), "");
			if(!id.isEmpty()) {
				map.put(id, obj);
			}
		}
		return map;
	}

	private Map<String, Map<String, Object>> indexHouses(List<Object> houses) {
		Map<String, Map<String, Object>> map = new HashMap<String, Map<String, Object>>();
		for(Object item : houses) {
			Map<String, Object> obj = asMap(item);
			String id = str(obj.get("id"), "");
			if(!id.isEmpty()) {
				map.put(id, obj);
			}
		}
		return map;
	}

	private Map<String, Object> firstPresent(Map<String, Map<String, Object>> byId, String... ids) {
		for(String id : ids) {
			if(byId.containsKey(id)) {
				return byId.get(id);
			}
		}
		return null;
	}

	private String lifeMode(Map<String, Object> params) {
		String raw = str(params == null ? null : params.get("guolaoLifeMode"), LIFE_MODE_ASC);
		if(LIFE_MODE_YUMAO.equals(raw)) {
			return LIFE_MODE_YUMAO;
		}
		if(LIFE_MODE_COTRANS.equals(raw)) {
			return LIFE_MODE_COTRANS;
		}
		return LIFE_MODE_ASC;
	}

	private String lifeModeName(String mode) {
		if(LIFE_MODE_YUMAO.equals(mode)) {
			return "遇卯安命";
		}
		if(LIFE_MODE_COTRANS.equals(mode)) {
			return "赤黄转换";
		}
		return "占星上升";
	}

	private double position(Map<String, Object> obj) {
		if(obj == null) {
			return 0;
		}
		if(obj.containsKey("ra")) {
			return num(obj.get("ra"), 0);
		}
		if(obj.containsKey("lon")) {
			return num(obj.get("lon"), 0);
		}
		String sign = str(obj.get("sign"), "");
		double signLon = num(obj.get("signlon"), 0);
		for(int i=0; i<SIGN_IDS.length; i++) {
			if(SIGN_IDS[i].equals(sign)) {
				return i * 30 + signLon;
			}
		}
		return signLon;
	}

	private int moiraHouseIndex(int signIdx, int lifeSignIndex) {
		return wrap(signIdx - lifeSignIndex, 12) + 1;
	}

	private String moiraHouseName(int signIdx, int lifeSignIndex) {
		return MOIRA_HOUSE_NAMES[moiraHouseIndex(signIdx, lifeSignIndex) - 1];
	}

	private String houseLabel(Object houseId, Map<String, Map<String, Object>> houseById) {
		String id = str(houseId, "");
		if(id.isEmpty()) {
			return "";
		}
		Map<String, Object> house = houseById.get(id);
		if(house != null && house.containsKey("id")) {
			return str(house.get("id"), id);
		}
		return id;
	}

	private String degreeText(double lon) {
		double val = normalizeDegree(lon);
		int signIdx = signIndex(val);
		double inSign = val - signIdx * 30;
		int deg = (int) Math.floor(inSign);
		int min = (int) Math.floor((inSign - deg) * 60);
		return deg + "度" + min + "分";
	}

	private int signIndex(double lon) {
		return wrap((int) Math.floor(normalizeDegree(lon) / 30.0), 12);
	}

	private String signLabel(int idx) {
		return SIGN_NAMES[wrap(idx, 12)];
	}

	private String signZi(int idx) {
		return SIGN_ZI[wrap(idx, 12)];
	}

	private String planetName(String id) {
		String name = PLANET_NAMES.get(id);
		return name == null ? id : name;
	}

	private double normalizeDegree(double val) {
		double d = val % 360.0;
		if(d < 0) {
			d += 360.0;
		}
		return d;
	}

	private int wrap(int val, int size) {
		int v = val % size;
		return v < 0 ? v + size : v;
	}

	private double round(double val, int scale) {
		double m = Math.pow(10, scale);
		return Math.round(val * m) / m;
	}

	private double num(Object obj, double defVal) {
		if(obj instanceof Number) {
			return ((Number)obj).doubleValue();
		}
		if(obj != null) {
			try {
				return Double.parseDouble(String.valueOf(obj));
			}catch(Exception e) {
				return defVal;
			}
		}
		return defVal;
	}

	private String str(Object obj, String defVal) {
		if(obj == null) {
			return defVal;
		}
		String s = String.valueOf(obj);
		return s == null ? defVal : s;
	}

	@SuppressWarnings("unchecked")
	private Map<String, Object> asMap(Object obj) {
		if(obj instanceof Map) {
			return (Map<String, Object>) obj;
		}
		return Collections.emptyMap();
	}

	@SuppressWarnings("unchecked")
	private List<Object> asList(Object obj) {
		if(obj instanceof List) {
			return (List<Object>) obj;
		}
		return Collections.emptyList();
	}

	private List<String> stringList(Object obj) {
		List<String> list = new ArrayList<String>();
		Set<String> seen = new HashSet<String>();
		if(obj instanceof List) {
			for(Object item : (List<?>) obj) {
				if(item != null) {
					String name = formatGodName(String.valueOf(item));
					if(!name.isEmpty() && !seen.contains(name)) {
						seen.add(name);
						list.add(name);
					}
				}
			}
		}
		return list;
	}

	private String formatGodName(String name) {
		if(name == null) {
			return "";
		}
		String val = name.replaceAll("\\s+", "");
		if(val.isEmpty()) {
			return "";
		}
		int slash = val.indexOf("/");
		int fullSlash = val.indexOf("／");
		int cut = -1;
		if(slash >= 0 && fullSlash >= 0) {
			cut = Math.min(slash, fullSlash);
		}else if(slash >= 0) {
			cut = slash;
		}else if(fullSlash >= 0) {
			cut = fullSlash;
		}
		if(cut >= 0) {
			val = val.substring(0, cut);
		}
		if("天乙贵人".equals(val)) {
			return "天贵";
		}
		if("玉堂贵人".equals(val)) {
			return "玉贵";
		}
		return val;
	}

	private List<String> intersect(List<String> list, Set<String> filter) {
		List<String> res = new ArrayList<String>();
		for(String item : list) {
			if(filter.contains(item)) {
				res.add(item);
			}
		}
		return res;
	}

	private String join(List<String> list, String sep) {
		StringBuilder sb = new StringBuilder();
		for(int i=0; i<list.size(); i++) {
			if(i > 0) {
				sb.append(sep);
			}
			sb.append(list.get(i));
		}
		return sb.toString();
	}

	private static class MoiraStyleRule {
		private final String name;
		private final String level;
		private final String score;
		private final String expr;

		private MoiraStyleRule(String name, String level, String score, String expr) {
			this.name = name;
			this.level = level;
			this.score = score;
			this.expr = expr;
		}
	}

	private class MoiraStyleContext {
		private final Map<String, Object> chart;
		private final Map<String, Map<String, Object>> byId;
		private final Map<String, Object> params;
		private final int lifeSignIndex;
		private final int selfSignIndex;
		private final Map<String, Integer> godSigns = new HashMap<String, Integer>();
		private final Map<String, Integer> houseSigns = new HashMap<String, Integer>();

		private MoiraStyleContext(Map<String, Object> chart, Map<String, Map<String, Object>> byId, Map<String, Object> params, int lifeSignIndex, int selfSignIndex, List<Map<String, Object>> godHits) {
			this.chart = chart == null ? Collections.<String, Object>emptyMap() : chart;
			this.byId = byId == null ? Collections.<String, Map<String, Object>>emptyMap() : byId;
			this.params = params == null ? Collections.<String, Object>emptyMap() : params;
			this.lifeSignIndex = lifeSignIndex;
			this.selfSignIndex = selfSignIndex;
			for(int i=0; i<MOIRA_HOUSE_NAMES.length; i++) {
				houseSigns.put(MOIRA_HOUSE_NAMES[i], wrap(lifeSignIndex + i, 12));
			}
			houseSigns.put("命", houseSigns.get("命宫"));
			houseSigns.put("身", selfSignIndex);
			houseSigns.put("官", houseSigns.get("官禄"));
			houseSigns.put("福", houseSigns.get("福德"));
			houseSigns.put("财", houseSigns.get("财帛"));
			houseSigns.put("田", houseSigns.get("田宅"));
			houseSigns.put("妻", houseSigns.get("夫妻"));
			houseSigns.put("嗣", houseSigns.get("男女"));
			houseSigns.put("奴", houseSigns.get("奴仆"));
			houseSigns.put("疾", houseSigns.get("疾厄"));
			houseSigns.put("迁", houseSigns.get("迁移"));
			houseSigns.put("相", houseSigns.get("相貌"));

			for(Map<String, Object> row : godHits) {
				int signIdx = ziToSign(str(row.get("zi"), ""));
				if(signIdx < 0) {
					continue;
				}
				for(String key : Arrays.asList("goodGods", "neutralGods", "badGods", "taisuiGods")) {
					for(String name : stringList(row.get(key))) {
						if(!godSigns.containsKey(name)) {
							godSigns.put(name, signIdx);
						}
					}
				}
			}
		}

		private boolean eval(String expr) {
			return evalExpr(cleanOuter(expr == null ? "" : expr.trim()));
		}

		private boolean evalExpr(String expr) {
			expr = cleanOuter(expr.trim());
			List<String> ors = splitTop(expr, '|');
			if(ors.size() > 1) {
				for(String item : ors) {
					if(evalExpr(item)) {
						return true;
					}
				}
				return false;
			}
			List<String> ands = splitTop(expr, '&');
			if(ands.size() > 1) {
				for(String item : ands) {
					if(!evalExpr(item)) {
						return false;
					}
				}
				return true;
			}
			if(expr.startsWith("!")) {
				return !evalExpr(expr.substring(1));
			}
			if(expr.startsWith("?")) {
				return predicate(readPredicateName(expr.substring(1)));
			}
			int eq = indexTop(expr, '=');
			if(eq >= 0) {
				Object left = term(expr.substring(0, eq));
				Object right = term(expr.substring(eq + 1));
				return same(left, right);
			}
			return predicate(expr);
		}

		private String readPredicateName(String raw) {
			raw = raw.trim();
			if(raw.startsWith("{") && raw.endsWith("}")) {
				return raw.substring(1, raw.length() - 1).trim();
			}
			return raw;
		}

		private boolean predicate(String name) {
			name = name == null ? "" : name.trim();
			if("昼".equals(name)) {
				return isDay();
			}
			if("夜".equals(name)) {
				return !isDay();
			}
			if("冬".equals(name)) {
				int month = datePart(1, 1);
				return month == 11 || month == 12 || month == 1;
			}
			if(name.endsWith("会") || name.endsWith("遇")) {
				String core = name.substring(0, name.length() - 1);
				if(core.length() >= 2) {
					String a = core.substring(0, 1);
					String b = core.substring(1, 2);
					return same(signOfName(a), signOfName(b));
				}
			}
			if(name.startsWith("孤") && name.length() >= 2) {
				Integer sign = signOfName(name.substring(1, 2));
				if(sign == null) {
					return false;
				}
				int count = 0;
				for(String id : PLANET_ORDER) {
					Integer other = signOfName(planetName(id));
					if(other != null && other.intValue() == sign.intValue()) {
						count++;
					}
				}
				return count == 1;
			}
			if(name.endsWith("东") || name.endsWith("南") || name.endsWith("西") || name.endsWith("北")) {
				String star = name.substring(0, 1);
				Integer sign = signOfName(star);
				if(sign == null) {
					return false;
				}
				String zi = signZi(sign);
				if(name.endsWith("东")) {
					return "寅卯辰".indexOf(zi) >= 0;
				}
				if(name.endsWith("南")) {
					return "巳午未".indexOf(zi) >= 0;
				}
				if(name.endsWith("西")) {
					return "申酉戌".indexOf(zi) >= 0;
				}
				return "亥子丑".indexOf(zi) >= 0;
			}
			if(name.endsWith("失垣")) {
				return lostRulership(name.substring(0, name.length() - 2));
			}
			if("命宫歧".equals(name)) {
				return nearSignBoundary(position(firstPresent(byId, "LifeMasterDeg74", "Asc", "Sun")));
			}
			if("命宿歧".equals(name)) {
				return nearSuBoundary(position(firstPresent(byId, "LifeMasterDeg74", "Asc", "Sun")));
			}
			if("命坐两歧".equals(name)) {
				return predicate("命宫歧") || predicate("命宿歧");
			}
			return false;
		}

		private Object term(String raw) {
			String s = cleanOuter(raw == null ? "" : raw.trim());
			if(s.startsWith("${克") && s.endsWith("}")) {
				String inner = s.substring(3, s.length() - 1);
				if(inner.startsWith("{") && inner.endsWith("}")) {
					inner = inner.substring(1, inner.length() - 1);
				}
				Object val = term(inner);
				return OVERCOMING.get(String.valueOf(val));
			}
			if(s.startsWith("@") || s.startsWith("%")) {
				return atLikeTerm(s);
			}
			return s;
		}

		private Object atLikeTerm(String s) {
			char op = s.charAt(0);
			String body = s.substring(1).trim();
			String name;
			String suffix;
			if(body.startsWith("{")) {
				int end = matchBrace(body, 0);
				if(end < 0) {
					return "";
				}
				String innerText = body.substring(1, end).trim();
				if(innerText.startsWith("@") || innerText.startsWith("%") || innerText.startsWith("${")) {
					name = String.valueOf(term(innerText));
				}else {
					name = innerText;
				}
				suffix = body.substring(end + 1).trim();
			}else {
				int cut = 0;
				while(cut < body.length()) {
					char ch = body.charAt(cut);
					if(ch == '[' || ch == '+' || ch == '-' || Character.isWhitespace(ch)) {
						break;
					}
					cut++;
				}
				name = body.substring(0, cut);
				suffix = body.substring(cut).trim();
			}

			Object value;
			if(op == '%') {
				value = suValue(name, suffix);
				suffix = stripLeadingIndex(suffix);
			}else {
				value = signOfName(name);
				if(value == null) {
					value = name;
				}
			}

			while(suffix.startsWith("[")) {
				int end = suffix.indexOf(']');
				if(end < 0) {
					break;
				}
				String idx = suffix.substring(1, end);
				if("0".equals(idx) && value instanceof Integer) {
					value = signZi((Integer) value);
				}else if("1".equals(idx) && value instanceof Integer) {
					value = signRulerCn((Integer) value);
				}
				suffix = suffix.substring(end + 1).trim();
			}
			if(value instanceof Integer && (suffix.startsWith("+") || suffix.startsWith("-"))) {
				int offset = parseIntSafe(suffix, 0);
				value = wrap(((Integer)value) + offset, 12);
			}
			return value;
		}

		private Object suValue(String name, String suffix) {
			Map<String, Object> obj = objectByCnName(name);
			if(obj == null) {
				return "";
			}
			String su = str(obj.get("su28"), "");
			if(suffix.startsWith("[1]")) {
				return suRuler(su);
			}
			return su;
		}

		private String stripLeadingIndex(String suffix) {
			if(suffix.startsWith("[")) {
				int end = suffix.indexOf(']');
				if(end >= 0) {
					return suffix.substring(end + 1).trim();
				}
			}
			return suffix;
		}

		private Integer signOfName(String name) {
			if(name == null || name.isEmpty()) {
				return null;
			}
			if(houseSigns.containsKey(name)) {
				return houseSigns.get(name);
			}
			if(godSigns.containsKey(name)) {
				return godSigns.get(name);
			}
			String id = PLANET_IDS_BY_CN.get(name);
			if(id != null) {
				Map<String, Object> obj = byId.get(id);
				if(obj != null) {
					return signIndex(position(obj));
				}
			}
			return ziToSign(name);
		}

		private Map<String, Object> objectByCnName(String name) {
			String id = PLANET_IDS_BY_CN.get(name);
			return id == null ? null : byId.get(id);
		}

		private boolean lostRulership(String subject) {
			String ruler = null;
			if("官".equals(subject)) {
				ruler = signRulerCn(houseSigns.get("官禄"));
			}else if("福".equals(subject)) {
				ruler = signRulerCn(houseSigns.get("福德"));
			}else if(subject.length() == 1) {
				ruler = subject;
			}
			if(ruler == null) {
				return false;
			}
			Integer rulerSign = signOfName(ruler);
			if(rulerSign == null) {
				return false;
			}
			String rulerOfRulerSign = signRulerCn(rulerSign);
			return same(rulerOfRulerSign, OVERCOMING.get(ruler));
		}

		private boolean isDay() {
			String time = str(params.get("time"), "");
			int hour = 12;
			try {
				hour = Integer.parseInt(time.split(":")[0]);
			}catch(Exception e) {
				hour = 12;
			}
			return hour >= 6 && hour < 18;
		}

		private int datePart(int idx, int defVal) {
			String date = str(params.get("date"), "");
			date = date.replace('/', '-');
			String[] parts = date.split("-");
			if(parts.length > idx) {
				return parseIntSafe(parts[idx], defVal);
			}
			return defVal;
		}

		private boolean nearSignBoundary(double lon) {
			double inSign = normalizeDegree(lon) % 30.0;
			return inSign <= 1.0 || inSign >= 29.0;
		}

		private boolean nearSuBoundary(double lon) {
			List<Object> raw = asList(chart.get("fixedStarSu28"));
			if(raw.isEmpty()) {
				return false;
			}
			double pos = normalizeDegree(lon);
			for(Object item : raw) {
				Map<String, Object> row = asMap(item);
				double rawRa = num(row.get("ra"), -999);
				if(rawRa < -900) {
					continue;
				}
				double ra = normalizeDegree(rawRa);
				double diff = Math.abs(pos - ra);
				diff = Math.min(diff, 360.0 - diff);
				if(diff <= 1.0) {
					return true;
				}
			}
			return false;
		}

		private boolean same(Object a, Object b) {
			if(a == null || b == null) {
				return false;
			}
			if(a instanceof Integer && b instanceof Integer) {
				return ((Integer)a).intValue() == ((Integer)b).intValue();
			}
			return String.valueOf(a).equals(String.valueOf(b));
		}

		private String signRulerCn(int signIdx) {
			String rulerId = RULERS.get(SIGN_IDS[wrap(signIdx, 12)]);
			return planetName(rulerId);
		}

		private String suRuler(String su) {
			if(su == null || su.isEmpty()) {
				return "";
			}
			if("星房虚昴".indexOf(su) >= 0) {
				return "日";
			}
			if("张心危毕".indexOf(su) >= 0) {
				return "月";
			}
			if("亢牛娄鬼".indexOf(su) >= 0) {
				return "金";
			}
			if("角斗奎井".indexOf(su) >= 0) {
				return "木";
			}
			if("轸壁参箕".indexOf(su) >= 0) {
				return "水";
			}
			if("尾室觜翼".indexOf(su) >= 0) {
				return "火";
			}
			if("氐女胃柳".indexOf(su) >= 0) {
				return "土";
			}
			return "";
		}
	}

	private int ziToSign(String zi) {
		for(int i=0; i<SIGN_ZI.length; i++) {
			if(SIGN_ZI[i].equals(zi)) {
				return i;
			}
		}
		return -1;
	}

	private int parseIntSafe(String raw, int defVal) {
		try {
			return Integer.parseInt(raw.trim());
		}catch(Exception e) {
			return defVal;
		}
	}

	private String cleanOuter(String expr) {
		String s = expr == null ? "" : expr.trim();
		while(s.startsWith("(") && s.endsWith(")") && matchBrace(s, 0, '(', ')') == s.length() - 1) {
			s = s.substring(1, s.length() - 1).trim();
		}
		return s;
	}

	private int indexTop(String s, char needle) {
		int paren = 0;
		int brace = 0;
		int bracket = 0;
		for(int i=0; i<s.length(); i++) {
			char ch = s.charAt(i);
			if(ch == '(') paren++;
			else if(ch == ')') paren--;
			else if(ch == '{') brace++;
			else if(ch == '}') brace--;
			else if(ch == '[') bracket++;
			else if(ch == ']') bracket--;
			else if(ch == needle && paren == 0 && brace == 0 && bracket == 0) return i;
		}
		return -1;
	}

	private List<String> splitTop(String s, char sep) {
		List<String> list = new ArrayList<String>();
		int paren = 0;
		int brace = 0;
		int bracket = 0;
		int start = 0;
		for(int i=0; i<s.length(); i++) {
			char ch = s.charAt(i);
			if(ch == '(') paren++;
			else if(ch == ')') paren--;
			else if(ch == '{') brace++;
			else if(ch == '}') brace--;
			else if(ch == '[') bracket++;
			else if(ch == ']') bracket--;
			else if(ch == sep && paren == 0 && brace == 0 && bracket == 0) {
				list.add(s.substring(start, i).trim());
				start = i + 1;
			}
		}
		list.add(s.substring(start).trim());
		return list;
	}

	private int matchBrace(String s, int start) {
		return matchBrace(s, start, '{', '}');
	}

	private int matchBrace(String s, int start, char open, char close) {
		int depth = 0;
		for(int i=start; i<s.length(); i++) {
			char ch = s.charAt(i);
			if(ch == open) {
				depth++;
			}else if(ch == close) {
				depth--;
				if(depth == 0) {
					return i;
				}
			}
		}
		return -1;
	}
}
