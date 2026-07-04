// 紫白飞星 · 年/月/日/时入中九宫 + 紫白吉凶 + 紫白诀（8.1 / 8.9）。日时用 lunar-javascript 取干支与节气。
import { Solar } from 'lunar-javascript';
import { zibaiYearCenter } from './liqiCore';
import { ZIBAI_STAR, ZIBAI_JX, GONG_NAME, GONG_GUA, NINE_STAR_MEANING, GANZHI_60, DIZHI } from './fengshuiData';

const idxF = (n)=>(n - 5 + 9) % 9;
function flyFromCenter(center) {
	const pan = {};
	for (let g = 1; g <= 9; g++) { pan[g] = (center - 1 + idxF(g)) % 9 + 1; }
	return pan;
}

// 月入中（8.1.2）：年支三组定正月入中星，逐月逆退。
const MONTH_START = { 子: 8, 午: 8, 卯: 8, 酉: 8, 辰: 5, 戌: 5, 丑: 5, 未: 5, 寅: 2, 申: 2, 巳: 2, 亥: 2 };
const YEAR_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];   // 1900=庚子(支子)起
function yearZhi(year) { return YEAR_ZHI[((year - 1900) % 12 + 12) % 12]; }
export function monthCenter(year, month) {
	const start = MONTH_START[yearZhi(year)];
	let c = start - (month - 1);
	c = ((c - 1) % 9 + 9) % 9 + 1;
	return c;
}

// ── 日紫白（8.1.3）：冬至后阳遁甲子起一白顺、夏至后阴遁甲子起九紫逆；三元(上/中/下)符头。──
function gzIndex(gz) { return GANZHI_60.indexOf(gz); }
function solarOf(y, m, d) { return Solar.fromYmd(y, m, d); }
// 取某年冬至/夏至 Solar，归一到当日 0 时（节气原 Solar 含时刻，会令日差非整）。
function jieqiSolar(year, name) {
	const t = solarOf(year, 6, 1).getLunar().getJieQiTable();
	const s = t[name];
	return s ? Solar.fromYmd(s.getYear(), s.getMonth(), s.getDay()) : null;
}
export function dayCenter(y, m, d) {
	const target = solarOf(y, m, d);
	const tJD = target.getJulianDay();
	// 汇集邻年冬至/夏至候选（jieqiSolar 相对 solarOf(yr,6,1) 返 冬至=yr-1腊月/夏至=yr本年，故跨年取）。
	const cands = [];
	[y - 1, y, y + 1, y + 2].forEach((yr)=>{
		['冬至', '夏至'].forEach((nm)=>{ const s = jieqiSolar(yr, nm); if (s) { cands.push({ type: nm, jd: s.getJulianDay(), solar: s }); } });
	});
	// 取「≤ 目标日」中最近的一个至：冬至→阳遁、夏至→阴遁。
	const past = cands.filter((c)=>c.jd <= tJD).sort((a, b)=>b.jd - a.jd);
	if (!past.length) { return null; }
	const anchorC = past[0];
	const yang = anchorC.type === '冬至';
	const anchor = anchorC.solar;
	if (!anchor) { return null; }
	// 符头甲子 = 节气日所在日干支回退至甲子。
	const anchorGZ = anchor.getLunar().getDayInGanZhi();
	const fuTouJD = anchor.getJulianDay() - gzIndex(anchorGZ);
	const offset = Math.round(tJD - fuTouJD);
	const yuan = ((Math.floor(offset / 60) % 3) + 3) % 3;      // 0上/1中/2下元
	const within = ((offset % 60) + 60) % 60;
	const startStar = yang ? [1, 4, 7][yuan] : [9, 6, 3][yuan];
	let c = yang ? (startStar - 1 + within) : (startStar - 1 - within);
	c = ((c % 9) + 9) % 9 + 1;
	return { center: c, yang, yuan, dayGanZhi: target.getLunar().getDayInGanZhi() };
}

// ── 时紫白（8.1.4）：日支三元 + 冬夏至顺逆，子时起入中，逐时推。──
const HOUR_YANG_START = { 0: 1, 1: 4, 2: 7 };   // 子午卯酉/辰戌丑未/寅申巳亥 日 阳遁子时起一白/四绿/七赤
const HOUR_YIN_START = { 0: 9, 1: 6, 2: 3 };
function dayZhiGroup(dayZhi) {
	if ('子午卯酉'.indexOf(dayZhi) >= 0) { return 0; }
	if ('辰戌丑未'.indexOf(dayZhi) >= 0) { return 1; }
	return 2;
}
export function hourCenter(y, m, d, hour) {
	const dc = dayCenter(y, m, d);
	if (!dc) { return null; }
	const dayZhi = dc.dayGanZhi.slice(-1);
	const grp = dayZhiGroup(dayZhi);
	const shiZhiIdx = Math.floor(((Number(hour) || 0) + 1) / 2) % 12;   // 子=0
	const start = dc.yang ? HOUR_YANG_START[grp] : HOUR_YIN_START[grp];
	let c = dc.yang ? (start - 1 + shiZhiIdx) : (start - 1 - shiZhiIdx);
	c = ((c % 9) + 9) % 9 + 1;
	return { center: c, yang: dc.yang, shiZhi: DIZHI[shiZhiIdx] };
}

// ── 紫白诀名句（8.9，断验字典）：两星相会引动。──
export const ZIBAI_JUE = [
	{ when: [1, 2], text: '一白二黑交临，损主重病' },
	{ when: [3, 7], text: '三碧七赤叠至，被劫盗，更见官灾' },
	{ when: [4, 8], text: '八会四而小口殒生（四绿文昌，然八四会主伤小口）' },
	{ when: [7, 9], text: '七九合辙，常招回禄之灾' },
	{ when: [2, 5], text: '二五交加，罹死亡并生疾病' },
	{ when: [6, 7], text: '六七交剑，争斗官非' },
	{ when: [9, 5], text: '五九相逢，火照五黄，暴病' },
];

function palacesOf(pan) {
	const out = [];
	for (let g = 1; g <= 9; g++) {
		const star = pan[g];
		out.push({ gong: g, name: GONG_NAME[g], gua: GONG_GUA[g], star, starName: ZIBAI_STAR[star], jx: ZIBAI_JX[star], meaning: NINE_STAR_MEANING[star] });
	}
	return out;
}

// 紫白排盘：年/月(/日/时)入中九宫。date {y,m,d,hour} 供日时。
export function zibai({ year, month, date } = {}) {
	const y = year || new Date().getFullYear();
	const yc = zibaiYearCenter(y);
	const yearPan = flyFromCenter(yc);
	let monthPan = null; let mc = null;
	if (month) { mc = monthCenter(y, month); monthPan = flyFromCenter(mc); }
	// 日/时紫白（给完整年月日）。
	let dayInfo = null; let dayPan = null; let hourInfo = null; let hourPan = null;
	if (date && date.m && date.d) {
		try {
			dayInfo = dayCenter(date.y || y, date.m, date.d);
			if (dayInfo) { dayPan = flyFromCenter(dayInfo.center); }
			if (dayInfo && date.hour != null) { hourInfo = hourCenter(date.y || y, date.m, date.d, date.hour); if (hourInfo) { hourPan = flyFromCenter(hourInfo.center); } }
		} catch (e) { dayInfo = null; }
	}
	return {
		available: true, year: y, month: month || null,
		yearCenter: yc, yearCenterStar: ZIBAI_STAR[yc],
		monthCenter: mc, monthCenterStar: mc ? ZIBAI_STAR[mc] : null,
		yearPalaces: palacesOf(yearPan),
		monthPalaces: monthPan ? palacesOf(monthPan) : null,
		dayInfo, dayPalaces: dayPan ? palacesOf(dayPan) : null,
		hourInfo, hourPalaces: hourPan ? palacesOf(hourPan) : null,
		jue: ZIBAI_JUE,
		note: '一六八九吉、二三五七凶、四绿文昌、五黄大凶;日/时紫白依节气顺逆(近似,精确查日家紫白)',
	};
}
