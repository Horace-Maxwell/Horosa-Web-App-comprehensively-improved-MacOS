package spacex.astrostudycn.model;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import boundless.utility.ConvertUtility;
import spacex.astrostudy.constants.StemBranch;
import spacex.astrostudy.helper.BaZiHelper;
import spacex.astrostudy.helper.NongliHelper;
import spacex.astrostudy.model.NongLi;
import spacex.astrostudycn.constants.BaZiGender;
import spacex.astrostudycn.constants.TimeZiAlg;
import spacex.astrostudycn.helper.ZiWeiHelper;

/**
 * 紫微运限引擎：流年 / 流月 / 流日 / 流时 / 小限 各层的命宫定位、干支、四化与流曜。
 * 算法皆紫微通法（斗君法起流月、男顺女逆起小限等），不涉任何第三方实现。
 *
 * 命宫索引 = 地支索引（houses[i] 之地支为 Branches[i]，i 与地支索引一一对应）。
 * relabel（流命/流兄…顺布）与盘面渲染由前端负责；本引擎只产结构化数据。
 */
public class ZiWeiLuck {

	private static final String[] HUA = { "禄", "权", "科", "忌" };

	public static Map<String, Object> build(ZiWeiChart c, Map<String, Object> target,
			boolean after23NewDay, boolean lateZiHourUseNextDay) {
		Map<String, Object> layers = new HashMap<String, Object>();
		if (target == null) {
			return layers;
		}

		if (target.get("daxianIndex") != null) {
			int di = ConvertUtility.getValueAsInt(target.get("daxianIndex"), -1);
			if (di >= 0 && di < 12) {
				layers.put("daxian", daxian(c, di));
			}
		}
		if (target.get("year") != null) {
			int year = ConvertUtility.getValueAsInt(target.get("year"), 0);
			if (year != 0) {
				layers.put("liunian", liunian(c, year));
				if (target.get("lunarMonth") != null) {
					int m = ConvertUtility.getValueAsInt(target.get("lunarMonth"), 0);
					if (m >= 1 && m <= 12) {
						layers.put("liuyue", liuyue(c, year, m));
					}
				}
			}
		}
		if (target.get("gregDate") != null) {
			String gd = String.valueOf(target.get("gregDate"));
			String hourBranch = target.get("hourBranch") == null ? null : String.valueOf(target.get("hourBranch"));
			Map<String, Object>[] rishi = riShi(c, gd, hourBranch, after23NewDay, lateZiHourUseNextDay);
			if (rishi[0] != null) {
				layers.put("liuri", rishi[0]);
			}
			if (rishi[1] != null) {
				layers.put("liushi", rishi[1]);
			}
		}
		if (target.get("xiaoxianAge") != null) {
			int age = ConvertUtility.getValueAsInt(target.get("xiaoxianAge"), 0);
			if (age >= 1) {
				layers.put("xiaoxian", xiaoxian(c, age));
			}
		}
		return layers;
	}

	// ---- 各层 ----

	private static Map<String, Object> daxian(ZiWeiChart c, int idx) {
		String ganzi = c.houses[idx].ganzi;
		String gan = ganzi.substring(0, 1);
		Map<String, Object> m = layer(ganzi, gan, idx, c);
		m.put("ageRange", new int[] { c.houses[idx].direction[0], c.houses[idx].direction[1] });
		return m;
	}

	private static Map<String, Object> liunian(ZiWeiChart c, int year) {
		String ganzi = BaZiHelper.getYearGanzi(year);
		String gan = ganzi.substring(0, 1);
		String zhi = ganzi.substring(1);
		int ming = branchIdx(zhi);
		Map<String, Object> m = layer(ganzi, gan, ming, c);
		m.put("year", year);
		m.put("flowStars", flowStars(gan, zhi));
		m.put("doujunIndex", doujunIdx(c, zhi));
		return m;
	}

	private static Map<String, Object> liuyue(ZiWeiChart c, int year, int month) {
		String yearGanzi = BaZiHelper.getYearGanzi(year);
		String ganzi = BaZiHelper.getMonthGanziStr(yearGanzi, month);
		String gan = ganzi.substring(0, 1);
		int ming = (doujunIdx(c, yearGanzi.substring(1)) + (month - 1)) % 12;
		Map<String, Object> m = layer(ganzi, gan, ming, c);
		m.put("lunarMonth", month);
		return m;
	}

	/** 流日 + 流时：用公历日期求 NongLi（含日柱），命宫走斗君法。返回 [流日, 流时]。 */
	@SuppressWarnings("unchecked")
	private static Map<String, Object>[] riShi(ZiWeiChart c, String gregDate, String hourBranch,
			boolean after23NewDay, boolean lateZiHourUseNextDay) {
		Map<String, Object>[] out = new Map[2];
		String dt = gregDate.length() <= 10 ? gregDate + " 12:00:00" : gregDate;
		int ad = dt.startsWith("-") ? -1 : 1;
		boolean directTime = c.timeAlg == TimeZiAlg.DirectTime.getCode();
		NongLi nl = NongliHelper.getNongLi(ad, dt, c.zone, c.lon, after23NewDay, directTime, lateZiHourUseNextDay);

		String yearGanzi = nl.year;
		int yueMing = (doujunIdx(c, yearGanzi.substring(1)) + (nl.monthInt - 1)) % 12;
		int riMing = (yueMing + (nl.dayInt - 1)) % 12;

		String dayGanzi = nl.dayGanZi;
		Map<String, Object> liuri = layer(dayGanzi, dayGanzi.substring(0, 1), riMing, c);
		liuri.put("lunarMonth", nl.monthInt);
		liuri.put("lunarDay", nl.dayInt);
		out[0] = liuri;

		if (hourBranch != null && StemBranch.BranchIndex.containsKey(hourBranch)) {
			String shiGanzi = BaZiHelper.getTimeGanZi(dayGanzi.substring(0, 1), hourBranch, after23NewDay,
					lateZiHourUseNextDay);
			int shiMing = (riMing + branchIdx(hourBranch)) % 12;
			Map<String, Object> liushi = layer(shiGanzi, shiGanzi.substring(0, 1), shiMing, c);
			liushi.put("hourBranch", hourBranch);
			out[1] = liushi;
		}
		return out;
	}

	private static Map<String, Object> xiaoxian(ZiWeiChart c, int age) {
		int idx = ZiWeiHelper.getSmallDirectioinHouse(age - 1, c.yearZi, c.gender);
		String ganzi = c.houses[idx].ganzi; // K4：小限干支复用本命宫位
		Map<String, Object> m = layer(ganzi, ganzi.substring(0, 1), idx, c);
		m.put("age", age);
		return m;
	}

	// ---- 公共组装 ----

	/** 一层的通用结构：干支 + 命宫支index + 该层四化（按层干）。 */
	private static Map<String, Object> layer(String ganzi, String gan, int mingZhiIndex, ZiWeiChart c) {
		Map<String, Object> m = new HashMap<String, Object>();
		m.put("ganzi", ganzi);
		m.put("gan", gan);
		m.put("mingZhiIndex", mingZhiIndex);
		m.put("sihua", sihuaOf(c, gan));
		return m;
	}

	/** 任意天干的四化：禄权科忌四星 + 各星本命所落地支index。 */
	private static List<Map<String, Object>> sihuaOf(ZiWeiChart c, String gan) {
		List<Map<String, Object>> list = new ArrayList<Map<String, Object>>();
		String[] stars = ZiWeiHelper.GanSihuaStars.get(gan);
		if (stars == null) {
			return list;
		}
		for (int i = 0; i < 4 && i < stars.length; i++) {
			Map<String, Object> h = new HashMap<String, Object>();
			h.put("star", stars[i]);
			h.put("hua", HUA[i]);
			Integer pos = c.starsHouseIndex.get(stars[i]);
			h.put("zhiIndex", pos == null ? -1 : pos.intValue());
			list.add(h);
		}
		return list;
	}

	/** 流曜（流年）：流禄/羊/陀/魁/钺 取年干表，流马取年支表，流昌/曲取干系新表。 */
	private static List<Map<String, Object>> flowStars(String gan, String zhi) {
		List<Map<String, Object>> list = new ArrayList<Map<String, Object>>();
		addGanStar(list, "流禄", "禄存", gan);
		addGanStar(list, "流羊", "擎羊", gan);
		addGanStar(list, "流陀", "陀罗", gan);
		addGanStar(list, "流魁", "天魁", gan);
		addGanStar(list, "流钺", "天钺", gan);
		// 流马（年支系）
		Object yearMa = ZiWeiHelper.StarsYearZi.get("年马");
		if (yearMa instanceof Map) {
			addStarZhi(list, "流马", posOf((Map<String, Object>) yearMa, zhi));
		}
		// 流昌 / 流曲（干系新表）
		Map<String, String> liuChang = ZiWeiHelper.LiuChangQu.get("流昌");
		Map<String, String> liuQu = ZiWeiHelper.LiuChangQu.get("流曲");
		if (liuChang != null) {
			addStarZhi(list, "流昌", liuChang.get(gan));
		}
		if (liuQu != null) {
			addStarZhi(list, "流曲", liuQu.get(gan));
		}
		return list;
	}

	@SuppressWarnings("unchecked")
	private static void addGanStar(List<Map<String, Object>> list, String flowName, String baseStar, String gan) {
		Object star = ZiWeiHelper.StarsYearGan.get(baseStar);
		if (star instanceof Map) {
			addStarZhi(list, flowName, posOf((Map<String, Object>) star, gan));
		}
	}

	@SuppressWarnings("unchecked")
	private static String posOf(Map<String, Object> starDef, String key) {
		Object pos = starDef.get("pos");
		if (pos instanceof Map) {
			Object v = ((Map<String, Object>) pos).get(key);
			return v == null ? null : String.valueOf(v);
		}
		return null;
	}

	private static void addStarZhi(List<Map<String, Object>> list, String name, String zhi) {
		if (zhi == null || zhi.length() == 0) {
			return;
		}
		Map<String, Object> m = new HashMap<String, Object>();
		m.put("name", name);
		m.put("zhiIndex", branchIdx(zhi));
		list.add(m);
	}

	private static int branchIdx(String zhi) {
		Integer i = StemBranch.BranchIndex.get(zhi);
		return i == null ? -1 : i.intValue();
	}

	/** 流年斗君宫index = (子斗支index + 流年支index) % 12（与 ZiWeiChart 构造时同法，非 ZiWeiHelper.getDouJun 月名查表）。 */
	private static int doujunIdx(ZiWeiChart c, String yearZhi) {
		return (branchIdx(c.zidou) + branchIdx(yearZhi)) % 12;
	}
}
