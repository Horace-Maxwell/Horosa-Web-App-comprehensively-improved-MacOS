import { Solar, LunarUtil } from 'lunar-javascript';
import { NaYin, SixtyJiaZi } from '../constants/ZWConst';
import { calcFourPillarShenSha } from './baziShenShaLocal';

const GANS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
const ZHIS = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];

const GAN_ELEMENT = {
	甲: 'Wood', 乙: 'Wood',
	丙: 'Fire', 丁: 'Fire',
	戊: 'Earth', 己: 'Earth',
	庚: 'Metal', 辛: 'Metal',
	壬: 'Water', 癸: 'Water',
};

const ZHI_ELEMENT = {
	寅: 'Wood', 卯: 'Wood',
	巳: 'Fire', 午: 'Fire',
	辰: 'Earth', 戌: 'Earth', 丑: 'Earth', 未: 'Earth',
	申: 'Metal', 酉: 'Metal',
	亥: 'Water', 子: 'Water',
};

const SHI_SHEN_SHORT = {
	比肩: '比',
	劫财: '劫',
	食神: '食',
	伤官: '伤',
	偏财: '才',
	正财: '财',
	七杀: '杀',
	正官: '官',
	偏印: '枭',
	正印: '印',
	日主: '日元',
};

const TRIGRAMS = {
	乾: { name: '乾', yao: [1, 1, 1] },
	兑: { name: '兑', yao: [1, 1, 0] },
	离: { name: '离', yao: [1, 0, 1] },
	震: { name: '震', yao: [1, 0, 0] },
	巽: { name: '巽', yao: [0, 1, 1] },
	坎: { name: '坎', yao: [0, 1, 0] },
	艮: { name: '艮', yao: [0, 0, 1] },
	坤: { name: '坤', yao: [0, 0, 0] },
};

const GAN_GUA = {
	甲: TRIGRAMS.乾, 乙: TRIGRAMS.坤, 丙: TRIGRAMS.离, 丁: TRIGRAMS.兑, 戊: TRIGRAMS.坎,
	己: TRIGRAMS.艮, 庚: TRIGRAMS.震, 辛: TRIGRAMS.巽, 壬: TRIGRAMS.乾, 癸: TRIGRAMS.坤,
};

const ZHI_GUA = {
	子: TRIGRAMS.坎, 丑: TRIGRAMS.艮, 寅: TRIGRAMS.震, 卯: TRIGRAMS.震, 辰: TRIGRAMS.巽, 巳: TRIGRAMS.离,
	午: TRIGRAMS.离, 未: TRIGRAMS.坤, 申: TRIGRAMS.兑, 酉: TRIGRAMS.兑, 戌: TRIGRAMS.乾, 亥: TRIGRAMS.坎,
};

function mod(num, base){
	return ((num % base) + base) % base;
}

function parseZoneHours(zone){
	if(zone === undefined || zone === null || zone === ''){
		return 8;
	}
	if(typeof zone === 'number'){
		return zone;
	}
	const text = `${zone}`;
	const match = text.match(/^([+-]?)(\d{1,2})(?::?(\d{2}))?/);
	if(match){
		const sign = match[1] === '-' ? -1 : 1;
		const hour = Number(match[2]);
		const minute = Number(match[3] || 0);
		return sign * (hour + minute / 60);
	}
	const n = Number(text);
	return Number.isFinite(n) ? n : 8;
}

function parseGeoDegrees(value, limit){
	if(value === undefined || value === null || value === ''){
		return null;
	}
	if(typeof value === 'number'){
		return Math.abs(value) <= limit ? value : null;
	}
	const text = `${value}`.trim().toLowerCase();
	const compass = text.match(/^(\d+(?:\.\d+)?)([ewns])(?:(\d+(?:\.\d+)?))?$/);
	if(compass){
		const deg = Number(compass[1]);
		const min = Number(compass[3] || 0);
		if(!Number.isFinite(deg) || !Number.isFinite(min)){
			return null;
		}
		const sign = compass[2] === 'w' || compass[2] === 's' ? -1 : 1;
		const result = sign * (deg + min / 60);
		return Math.abs(result) <= limit ? result : null;
	}
	const n = Number(text);
	return Number.isFinite(n) && Math.abs(n) <= limit ? n : null;
}

function parseDateTime(params){
	const [year, month, day] = `${params.date || ''}`.split('-').map((item)=>Number(item));
	const [hour, minute, second] = `${params.time || '00:00:00'}`.split(':').map((item)=>Number(item));
	return {
		year,
		month,
		day,
		hour: Number.isFinite(hour) ? hour : 0,
		minute: Number.isFinite(minute) ? minute : 0,
		second: Number.isFinite(second) ? second : 0,
	};
}

function dayOfYearUTC(date){
	const start = Date.UTC(date.getUTCFullYear(), 0, 1);
	return Math.floor((date.getTime() - start) / 86400000) + 1;
}

function equationOfTime(dayOfYear){
	const b = (360 / 365) * (dayOfYear - 81) * Math.PI / 180;
	return 9.87 * Math.sin(2 * b) - 7.53 * Math.cos(b) - 1.5 * Math.sin(b);
}

function applyApparentSolarTime(parts, params){
	if(Number(params.timeAlg) !== 0){
		return parts;
	}
	const lon = parseGeoDegrees(params.lon, 180);
	if(!Number.isFinite(lon)){
		return parts;
	}
	const zoneHours = parseZoneHours(params.zone);
	const wall = new Date(Date.UTC(parts.year, parts.month - 1, parts.day, parts.hour, parts.minute, parts.second));
	const utcForEot = new Date(wall.getTime() - zoneHours * 3600000);
	const ltcSeconds = (lon - zoneHours * 15) * 4 * 60;
	const eotSeconds = equationOfTime(dayOfYearUTC(utcForEot)) * 60;
	const adjusted = new Date(wall.getTime() + Math.round(ltcSeconds + eotSeconds) * 1000);
	return {
		year: adjusted.getUTCFullYear(),
		month: adjusted.getUTCMonth() + 1,
		day: adjusted.getUTCDate(),
		hour: adjusted.getUTCHours(),
		minute: adjusted.getUTCMinutes(),
		second: adjusted.getUTCSeconds(),
	};
}

function solarFromParts(parts){
	return Solar.fromYmdHms(parts.year, parts.month, parts.day, parts.hour, parts.minute, parts.second);
}

function shortShiShen(label){
	return SHI_SHEN_SHORT[label] || label || '';
}

function polarFromGan(gan){
	const idx = GANS.indexOf(gan);
	return idx >= 0 && idx % 2 === 0 ? 'Positive' : 'Negative';
}

function polarFromZhi(zhi){
	const idx = ZHIS.indexOf(zhi);
	return idx >= 0 && idx % 2 === 0 ? 'Positive' : 'Negative';
}

function emptyGods(){
	return {
		goodGods: [],
		neutralGods: [],
		badGods: [],
		taisuiGods: [],
	};
}

function makeStem(gan, relative){
	return {
		...emptyGods(),
		cell: gan || '',
		element: GAN_ELEMENT[gan] || '',
		polar: polarFromGan(gan),
		relative: shortShiShen(relative),
		gua: GAN_GUA[gan] || TRIGRAMS.乾,
	};
}

function makeBranch(zhi, relative){
	return {
		...emptyGods(),
		cell: zhi || '',
		element: ZHI_ELEMENT[zhi] || '',
		polar: polarFromZhi(zhi),
		relative: shortShiShen(relative),
		gua: ZHI_GUA[zhi] || TRIGRAMS.坤,
	};
}

function makeGua(gan, zhi){
	const up = GAN_GUA[gan] || TRIGRAMS.乾;
	const down = ZHI_GUA[zhi] || TRIGRAMS.坤;
	const yao = [...down.yao, ...up.yao];
	const name = `${up.name}${down.name}`;
	return {
		name,
		abrname: name,
		desc: '本地排盘',
		url: '#',
		yao,
	};
}

function makePillar(label, ganzi, data){
	const gan = `${ganzi || ''}`.charAt(0);
	const zhi = `${ganzi || ''}`.charAt(1);
	const hidden = data.hideGan || [];
	const hiddenRel = data.hideRel || [];
	const gua64 = makeGua(gan, zhi);
	const huGua = makeGua(gan, zhi);
	return {
		...emptyGods(),
		zhu: label,
		ganzi,
		ganZhi: ganzi,
		stem: makeStem(gan, data.stemRel),
		branch: makeBranch(zhi, hiddenRel[0] || data.branchRel),
		stemInBranch: hidden.map((item, idx)=>makeStem(item, hiddenRel[idx])),
		naying: data.nayin || NaYin[ganzi] || '',
		nayingPhase: '',
		ganziPhase: data.diShi || '',
		xunEmpty: data.xunKong || '',
		zhiStarGod: { gua: '' },
		gua64,
		huGua,
		tongGua: makeGua(gan, zhi),
		huGuaUp: GAN_GUA[gan] || TRIGRAMS.乾,
		huGuaDown: ZHI_GUA[zhi] || TRIGRAMS.坤,
	};
}

function ganziAt(ganzi, delta){
	const idx = SixtyJiaZi.indexOf(ganzi);
	return SixtyJiaZi[mod((idx >= 0 ? idx : 0) + delta, 60)];
}

function pillarFromGanzi(label, ganzi, dayGan){
	const gan = `${ganzi || ''}`.charAt(0);
	const zhi = `${ganzi || ''}`.charAt(1);
	const hideGan = (LunarUtil.ZHI_HIDE_GAN && LunarUtil.ZHI_HIDE_GAN[zhi]) || [];
	const hideRel = hideGan.map((item)=>shortShiShen(LunarUtil.SHI_SHEN[`${dayGan}${item}`]));
	return makePillar(label, ganzi, {
		stemRel: shortShiShen(LunarUtil.SHI_SHEN[`${dayGan}${gan}`]),
		hideGan,
		hideRel,
		nayin: LunarUtil.NAYIN && LunarUtil.NAYIN[ganzi] ? LunarUtil.NAYIN[ganzi] : NaYin[ganzi],
		xunKong: LunarUtil.getXunKong ? LunarUtil.getXunKong(ganzi) : '',
	});
}

function buildFourColumns(eightChar){
	const dayGan = eightChar.getDayGan();
	const four = {
		year: makePillar('年', eightChar.getYear(), {
			stemRel: eightChar.getYearShiShenGan(),
			hideGan: eightChar.getYearHideGan(),
			hideRel: eightChar.getYearShiShenZhi(),
			nayin: eightChar.getYearNaYin(),
			diShi: eightChar.getYearDiShi(),
			xunKong: eightChar.getYearXunKong(),
		}),
		month: makePillar('月', eightChar.getMonth(), {
			stemRel: eightChar.getMonthShiShenGan(),
			hideGan: eightChar.getMonthHideGan(),
			hideRel: eightChar.getMonthShiShenZhi(),
			nayin: eightChar.getMonthNaYin(),
			diShi: eightChar.getMonthDiShi(),
			xunKong: eightChar.getMonthXunKong(),
		}),
		day: makePillar('日', eightChar.getDay(), {
			stemRel: '日主',
			hideGan: eightChar.getDayHideGan(),
			hideRel: eightChar.getDayShiShenZhi(),
			nayin: eightChar.getDayNaYin(),
			diShi: eightChar.getDayDiShi(),
			xunKong: eightChar.getDayXunKong(),
		}),
		time: makePillar('时', eightChar.getTime(), {
			stemRel: eightChar.getTimeShiShenGan(),
			hideGan: eightChar.getTimeHideGan(),
			hideRel: eightChar.getTimeShiShenZhi(),
			nayin: eightChar.getTimeNaYin(),
			diShi: eightChar.getTimeDiShi(),
			xunKong: eightChar.getTimeXunKong(),
		}),
		tai: pillarFromGanzi('胎', eightChar.getTaiYuan(), dayGan),
		ming: pillarFromGanzi('命', eightChar.getMingGong(), dayGan),
		shen: pillarFromGanzi('身', eightChar.getShenGong(), dayGan),
		ganHe: {},
		ganCong: {},
		ziHe6: {},
		ziHe3: {},
		ziHui: {},
		ziXing: {},
		ziCong: {},
		ziCuan: {},
		ziPo: {},
	};
	four.ming12 = {
		zhi: four.ming.branch.cell,
	};
	const shenSha = calcFourPillarShenSha(four);
	['year', 'month', 'day', 'time'].forEach((key)=>{
		if(four[key]){
			four[key].shenSha = shenSha[key] || [];
			four[key].neutralGods = four[key].shenSha;
		}
	});
	return four;
}

function flowMonthFromSolar(year, term, solar, dayGan){
	const lunar = solar.getLunar();
	const ganzi = lunar.getMonthInGanZhi();
	return {
		year,
		month: solar.getMonth(),
		day: solar.getDay(),
		term,
		date: solar.toYmd(),
		ganzi,
		ganzhi: ganzi,
		...pillarFromGanzi('月', ganzi, dayGan),
	};
}

function buildFlowMonths(liuNian, birthSolar, dayGan){
	const year = liuNian.getYear();
	let months = liuNian.getLiuYue();
	if(birthSolar && year === birthSolar.getYear()){
		months = months.filter((item)=>item.getIndex() + 1 >= birthSolar.getMonth());
	}
	const seen = {};
	const result = [];
	months.forEach((month, idx)=>{
		const seed = Solar.fromYmd(year, month.getIndex() + 1, 1);
		const jie = seed.getLunar().getNextJie(true);
		const term = jie.getName();
		if(month.getIndex() === 0 && term === '小寒'){
			return;
		}
		if(!seen[term]){
			seen[term] = true;
			result.push(flowMonthFromSolar(year, term, jie.getSolar(), dayGan));
		}
		if(idx === months.length - 1 && term === '大雪'){
			const nextSeed = Solar.fromYmd(year + 1, 1, 1);
			const nextJie = nextSeed.getLunar().getNextJie(true);
			result.push(flowMonthFromSolar(year + 1, nextJie.getName(), nextJie.getSolar(), dayGan));
		}
	});
	return result;
}

function buildDirection(yun, dayGan, birthSolar){
	return yun.getDaYun(10).slice(1).map((item)=>{
		const mainDirect = pillarFromGanzi('运', item.getGanZhi(), dayGan);
		return {
			age: item.getStartAge(),
			startYear: item.getStartYear(),
			endYear: item.getEndYear(),
			mainDirect,
			subDirect: item.getLiuNian().map((year)=>({
				year: year.getYear(),
				age: year.getAge(),
				index: year.getIndex(),
				flowMonths: buildFlowMonths(year, birthSolar, dayGan),
				...pillarFromGanzi('年', year.getGanZhi(), dayGan),
			})),
		};
	});
}

function buildMainDirection(yun, dayGan){
	return yun.getDaYun(10).map((item, idx)=>{
		const ganzi = item.getGanZhi();
		return {
			age: item.getStartAge(),
			startYear: item.getStartYear(),
			year: item.getStartYear(),
			ganzi,
			ganzhi: ganzi,
			index: idx,
			...(ganzi ? pillarFromGanzi('运', ganzi, dayGan) : {}),
		};
	});
}

function buildSmallDirection(yun, dayGan){
	const first = yun.getDaYun(1)[0];
	return first.getXiaoYun().map((item)=>({
		year: item.getYear(),
		age: item.getAge(),
		ganzi: item.getGanZhi(),
		...pillarFromGanzi('小', item.getGanZhi(), dayGan),
	}));
}

function formatStartLuck(yun){
	return `出生后${yun.getStartYear()}年${yun.getStartMonth()}个月${yun.getStartDay()}天${yun.getStartHour ? yun.getStartHour() : 0}小时起运`;
}

function buildNongli(lunar, solar, apparentSolar){
	const prev = lunar.getPrevJie(true);
	const prevSolar = prev && prev.getSolar ? prev.getSolar() : null;
	let dayDiff = '';
	if(prevSolar && solar.subtract){
		dayDiff = `${prev.getName()}后第${Math.max(1, solar.subtract(prevSolar) + 1)}天`;
	}
	return {
		year: lunar.getYearInChinese(),
		month: `${lunar.getMonthInChinese()}月`,
		day: lunar.getDayInChinese(),
		leap: lunar.getMonth ? lunar.getMonth() < 0 : false,
		birth: apparentSolar.toYmdHms(),
		jiedelta: dayDiff,
		chef: '',
	};
}

export function buildLocalBaziResult(params){
	const rawParts = parseDateTime(params);
	if(!Number.isFinite(rawParts.year) || !Number.isFinite(rawParts.month) || !Number.isFinite(rawParts.day)){
		throw new Error('invalid bazi date');
	}
	const apparentParts = applyApparentSolarTime(rawParts, params || {});
	const solar = solarFromParts(apparentParts);
	const lunar = solar.getLunar();
	const eightChar = lunar.getEightChar();
	eightChar.setSect(1);
	const gender = Number(params.gender) === 0 ? 0 : 1;
	const yun = eightChar.getYun(gender);
	const dayGan = eightChar.getDayGan();
	const fourColumns = buildFourColumns(eightChar);
	const bazi = {
		gender: gender === 1 ? 'Male' : 'Female',
		nongli: buildNongli(lunar, solar, solar),
		fourColumns,
		gong12God: {},
		direction: buildDirection(yun, dayGan, solar),
		mainDirection: buildMainDirection(yun, dayGan),
		smallDirection: buildSmallDirection(yun, dayGan),
		directTime: yun.getStartSolar().toYmdHms(),
		directInfo: formatStartLuck(yun),
		tiaohou: [],
		source: 'lunar-local',
	};
	return {
		bazi,
		gender: bazi.gender,
		local: true,
	};
}

export default buildLocalBaziResult;
