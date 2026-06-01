import DateTime from '../components/comp/DateTime';
import request from './request';
import * as Constants from './constants';
import { defaultAfter23NewDay, defaultLateZiHourUseNextDay } from './dayBoundary';

// 用户拍板·v2.2.1: 给 AI 看的"排盘规则"语义说明,作为 first-class metadata 显式标注。
// 让 GPT/Claude/Ollama 看到 snapshot 时知道四柱按哪种规则计算,不会按错语义解读。
function buildDayBoundaryMeta(after23NewDay, lateZiHourUseNextDay){
	const a23 = after23NewDay === 0 || after23NewDay === '0' || after23NewDay === false ? 0 : 1;
	const lzh = lateZiHourUseNextDay === 0 || lateZiHourUseNextDay === '0' || lateZiHourUseNextDay === false ? 0 : 1;
	const dayLabel = a23 === 1 ? '23点算第二天(日柱进位次日)' : '24点算第二天(日柱守今、24点才换日柱)';
	const hourLabel = lzh === 1 ? '晚子时按次日日柱计算(时干用次日日干起子时)' : '晚子时按当日柱计算(时干用今日日干起子时)';
	return {
		after23NewDay: a23,
		lateZiHourUseNextDay: lzh,
		dayBoundaryLabel: dayLabel,
		lateZiHourLabel: hourLabel,
		note: `本盘排盘规则：日柱开关【${dayLabel}】+ 时柱开关【${hourLabel}】。23:00–23:59 范围内,日柱与时柱按上述规则计算;其他时辰两个开关均不影响。`,
	};
}
import { buildAstroSnapshotContent, loadAstroAISnapshot } from './astroAiSnapshot';
import { getCaseTypeLabel, getCaseTypeMeta, listLocalCases } from './localcases';
import { listLocalCharts } from './localcharts';
import { loadModuleAISnapshot, saveModuleAISnapshot } from './moduleAiSnapshot';
import { fetchChart } from '../services/astro';
import { AI_ANALYSIS_STORES, getStoreRecord, putStoreRecord } from './aiAnalysisStore';
import { buildRetrievedContextText } from './aiAnalysisRag';
import { fetchPreciseNongli } from './preciseCalcBridge';
import { calcDunJia, buildDunJiaSnapshotText } from '../components/dunjia/DunJiaCalc';
import { fetchTaiyiPan, buildTaiyiSnapshotText } from '../components/taiyi/TaiYiCalc';
import { buildTongSheFaModel, buildTongSheFaSnapshot } from '../components/tongshefa/TongSheFaMain';
import { buildJinKouData } from '../components/jinkou/JinKouCalc';
import { resolveJinKouDiFen } from '../components/jinkou/JinKouState';
import { buildLiuRengSnapshotText } from '../components/lrzhan/LiuRengMain';
import { buildJinKouSnapshotText } from '../components/jinkou/JinKouMain';
import { buildGuaSnapshotText } from '../components/guazhan/GuaZhanMain';
import { buildBaziSnapshotForParams } from '../components/cntradition/BaZi';
import { buildZiweiSnapshotForParams } from '../components/ziwei/ZiWeiMain';
import { buildIndiaSnapshotForFields } from '../components/astro/IndiaChart';
import { buildFirdariaSnapshotText, buildPrimaryDirectSnapshotText } from '../components/direction/AstroDirectMain';
import { buildDistributionsSnapshotText } from '../components/astro/AstroDistributions';
import { buildAgePointSnapshotText } from '../components/astro/AstroAgePoint';
import { buildPlanetaryAgesSnapshotText } from './planetaryAges';
import { buildVedicProgSnapshotText } from '../components/astro/AstroVedicProgressions';
import { buildBalbillusSnapshotText } from './balbillus';
import { buildYearSystem129SnapshotText } from '../components/astro/AstroYearSystem129';
import { buildPlanetaryArcSnapshotText } from '../components/astro/AstroPlanetaryArc';
import { buildPersianDirectedSnapshotText } from '../components/astro/AstroPersianDirected';
import { buildJaynesProgSnapshotText } from '../components/astro/AstroJaynesProgressions';
import { buildZodialReleaseSnapshotText } from '../components/astro/AstroZR';
import { buildDecennialsSnapshotText } from '../components/astro/AstroDecennials';
import { buildKinAstroSnapshotForFields } from '../components/kinastro/KinAstroMain';
import { buildHuangJiSnapshotForFields } from '../components/huangji/HuangJiMain';
import { buildGuolaoSnapshotForFields } from '../components/guolao/GuoLaoChartMain';
import { buildSuzhanSnapshotText } from '../components/suzhan/SuZhanMain';
import { buildGermanySnapshotForFields } from '../components/germany/AstroMidpoint';
import { buildPredictiveSnapshotText } from './predictiveAiSnapshot';
import { runHorary } from '../divination/horary/horaryEngine';
import { buildHorarySnapshot } from '../divination/horary/horarySnapshot';
import { runElection } from '../divination/election/electionEngine';
import { buildElectionSnapshot } from '../divination/election/electionSnapshot';
import { buildLocalBaziResult } from './baziLunarLocal';
import { calculate as canpingCalculate, buildSnapshotText as buildCanpingSnapshotText, liunianSeries as canpingLiunianSeries } from './canpingLocal';
import { calculate as heluoCalc, daYun as heluoDaYun, judge as heluoJudge, buildSnapshotText as buildHeluoSnapshotText } from './heluoLocal';

const DEFAULT_PD_ASPECTS = [0, 60, 90, 120, 180];
const DEFAULT_CONTEXT_CHAR_LIMIT = 18000;
const MODULE_SNAPSHOT_PREFIX = 'horosa.ai.snapshot.module.v1.';
const DEFAULT_QIMEN_OPTIONS = {
	jieQiType: 1,
	yearGanZhiType: 2,
	monthGanZhiType: 1,
	dayGanZhiType: 0,
	qijuMethod: 'zhirun',
	kongMode: 'day',
	yimaMode: 'day',
	timeAlg: 0,
	shiftPalace: 0,
	after23NewDay: defaultAfter23NewDay(),
	lateZiHourUseNextDay: defaultLateZiHourUseNextDay(),
	fengJu: false,
	paiPanType: 3,
	zhiShiType: 0,
	yueJiaQiJuType: 1,
};
const DEFAULT_TAIYI_OPTIONS = {
	style: 3,
	tn: 0,
	tenching: 0,
	sex: '男',
	rotation: '固定',
};

const ANALYSIS_TECHNIQUE_LABELS = {
	astrochart: '星盘',
	astrochart_like: '十三分盘 / 占星地图',
	indiachart: '印度占星',
	relative: '合盘',
	guolao: '七政四余',
	germany: '量化盘',
	jieqi: '节气盘',
	jieqi_meta: '节气盘-通用参数',
	jieqi_chunfen: '节气盘-春分',
	jieqi_xiazhi: '节气盘-夏至',
	jieqi_qiufen: '节气盘-秋分',
	jieqi_dongzhi: '节气盘-冬至',
	primarydirect: '星运-主/界限法',
	primarydirchart: '星运-主限法盘',
	zodialrelease: '星运-黄道星释',
	firdaria: '星运-法达星限',
	distributions: '星运-界推运',
	agepoint: '星运-年龄推进点',
	profection: '星运-小限法',
	solararc: '星运-太阳弧',
	solarreturn: '星运-太阳返照',
	lunarreturn: '星运-月亮返照',
	givenyear: '星运-流年法',
	decennials: '星运-十年大运',
	planetaryages: '星运-行星年龄',
	vedicprog: '星运-恒星推运',
	balbillus: '星运-Balbillus',
	yearsystem129: '星运-129年系统',
	planetaryarc: '星运-行星弧',
	persiandirected: '星运-波斯向运',
	jaynesprog: '星运-赤纬推运',
	cntradition: '辅助',
	bazi: '八字',
	ziwei: '紫微斗数',
	suzhan: '宿占',
	otherbu: '骰子',
	fengshui: '风水',
	sixyao: '六爻',
	tongshefa: '统摄法',
	liureng: '大六壬',
	jinkou: '金口诀',
	qimen: '奇门遁甲',
	sanshiunited: '三式合一',
	taiyi: '太乙',
	horary: '卜卦盘',
	election: '择日盘',
	canping: '邵子参评数',
	heluo: '河洛理数',
	xianqin: '演禽',
	cetian: '策天飞星',
	huangji: '皇极经世',
};

// AI 分析「使用技法」命盘类下拉。仅收录能按本盘数据返回结构化快照的技法。
// 已移除的空壳（选了挂不出内容，徒增干扰）：
//   relative(合盘,需两张盘)、jieqi 系列×6(节气盘,需多次取数+列表参数,非单盘技法)、
//   cntradition(辅助,无可复用 builder)、otherbu(骰子,随机不可复算)、fengshui(风水,iframe/DOM)。
// 标签仍保留在 ANALYSIS_TECHNIQUE_LABELS（导出/他处可能引用）。
export const ANALYSIS_CHART_TECHNIQUES = [
	'astrochart',
	'astrochart_like',
	'indiachart',
	'guolao',
	'germany',
	'primarydirect',
	'primarydirchart',
	'zodialrelease',
	'firdaria',
	'distributions',
	'agepoint',
	'profection',
	'solararc',
	'solarreturn',
	'lunarreturn',
	'givenyear',
	'decennials',
	'planetaryages',
	'vedicprog',
	'balbillus',
	'yearsystem129',
	'planetaryarc',
	'persiandirected',
	'jaynesprog',
	'bazi',
	'ziwei',
	'suzhan',
	'canping',
	'heluo',
	'xianqin',
	'cetian',
	'huangji',
];

export const ANALYSIS_CASE_TECHNIQUES = [
	'sixyao',
	'tongshefa',
	'liureng',
	'jinkou',
	'qimen',
	'sanshiunited',
	'taiyi',
	'suzhan',
	'horary',
	'election',
];

// 「时间确定式法」：盘面完全由起课时间 + 默认设置(含地点)决定，可即时起盘。
// 用途：① 新的「起课时间」入口对它们即时起盘；② 已存事盘若 payload 缺该技法，按其起课时间自动补算。
// 含西洋卜卦盘 horary / 择日盘 election——二者仅凭时间+地点即可起西洋盘、引擎默认类别(general/marriage)即出结构化裁决/评分。
// 六爻/统摄法/宿占等【不在此列】——六爻是摇钱/报数起卦，按时间重算 = 伪造一个不同的卦，永远只认存盘。
export const TIME_CASTABLE_DIVINATION = ['liureng', 'jinkou', 'qimen', 'taiyi', 'sanshiunited', 'horary', 'election'];
const TIME_CASTABLE_SET = new Set(TIME_CASTABLE_DIVINATION);

function safeParseJson(txt, defVal = null){
	if(!txt){
		return defVal;
	}
	try{
		return JSON.parse(txt);
	}catch(e){
		return defVal;
	}
}

function parseBirthString(text, zone = '+08:00'){
	const raw = `${text || ''}`.trim();
	const matched = raw.match(/^(-?\d+)-(\d{2})-(\d{2})(?:\s+(\d{2}):(\d{2})(?::(\d{2}))?)?$/);
	if(!matched){
		return new DateTime({ zone });
	}
	const yearVal = parseInt(matched[1], 10);
	return new DateTime({
		ad: yearVal < 0 ? -1 : 1,
		year: Math.abs(yearVal),
		month: parseInt(matched[2], 10),
		date: parseInt(matched[3], 10),
		hour: parseInt(matched[4] || '0', 10),
		minute: parseInt(matched[5] || '0', 10),
		second: parseInt(matched[6] || '0', 10),
		zone: zone || '+08:00',
	});
}

function normalizeTags(group){
	const parsed = safeParseJson(group, null);
	if(Array.isArray(parsed)){
		return parsed;
	}
	if(Array.isArray(group)){
		return group;
	}
	if(typeof group === 'string' && group.trim() !== ''){
		return group.split(/[,，\n]/g).map((item)=>`${item || ''}`.trim()).filter(Boolean);
	}
	return [];
}

function buildFieldObject(record){
	const birth = parseBirthString(record.birth, record.zone);
	return {
		cid: { value: record.cid || null },
		ad: { value: birth.ad },
		date: { value: birth.clone().startOf('date') },
		time: { value: birth.clone() },
		zone: { value: record.zone || birth.zone || '+08:00' },
		lat: { value: record.lat || '' },
		lon: { value: record.lon || '' },
		gpsLat: { value: record.gpsLat || 0 },
		gpsLon: { value: record.gpsLon || 0 },
		name: { value: record.name || '' },
		pos: { value: record.pos || '' },
		hsys: { value: record.hsys !== undefined ? record.hsys : 0 },
		zodiacal: { value: record.zodiacal !== undefined ? record.zodiacal : 0 },
		tradition: { value: 0 },
		strongRecption: { value: 0 },
		simpleAsp: { value: 0 },
		virtualPointReceiveAsp: { value: 0 },
		doubingSu28: { value: record.doubingSu28 ? 1 : 0 },
		houseStartMode: { value: 0 },
		predictive: { value: 1 },
		showPdBounds: { value: 1 },
		pdtype: { value: 0 },
		pdMethod: { value: 'core_alchabitius' },
		pdTimeKey: { value: 'Ptolemy' },
		pdaspects: { value: DEFAULT_PD_ASPECTS.slice(0) },
		timeAlg: { value: 0 },
		phaseType: { value: 0 },
		godKeyPos: { value: '年' },
		after23NewDay: { value: defaultAfter23NewDay() },
		lateZiHourUseNextDay: { value: defaultLateZiHourUseNextDay() },
		adjustJieqi: { value: 0 },
		gender: { value: record.gender !== undefined && record.gender !== null ? record.gender : 1 },
		southchart: { value: 0 },
		group: { value: normalizeTags(record.group) },
	};
}

function fieldParams(fields){
	return {
		cid: null,
		ad: fields.date.value.ad,
		date: fields.date.value.format('YYYY/MM/DD'),
		time: fields.time.value.format('HH:MM:SS'),
		zone: fields.date.value.zone,
		lat: fields.lat.value,
		lon: fields.lon.value,
		gpsLat: fields.gpsLat.value,
		gpsLon: fields.gpsLon.value,
		hsys: fields.hsys.value,
		southchart: fields.southchart.value,
		zodiacal: fields.zodiacal.value,
		tradition: fields.tradition.value,
		doubingSu28: fields.doubingSu28.value,
		strongRecption: fields.strongRecption.value,
		simpleAsp: fields.simpleAsp.value,
		virtualPointReceiveAsp: fields.virtualPointReceiveAsp.value,
		predictive: fields.predictive.value,
		showPdBounds: fields.showPdBounds.value,
		pdtype: fields.pdtype.value,
		pdMethod: fields.pdMethod.value,
		pdTimeKey: fields.pdTimeKey.value,
		pdaspects: fields.pdaspects.value,
		name: fields.name.value,
		pos: fields.pos.value,
		group: fields.group.value,
	};
}

function buildSnapshotMetaFromRecord(record, extraMeta = {}){
	const parts = buildSourceSignature({
		sourceType: record && record.birth ? 'chart' : 'case',
		record,
	});
	return {
		date: parts.date || '',
		time: parts.time || '',
		zone: parts.zone || '',
		lon: parts.lon || '',
		lat: parts.lat || '',
		...extraMeta,
	};
}

function buildCaseSnapshotFields(record){
	const dt = parseBirthString(record && (record.divTime || record.updateTime || ''), record && record.zone ? record.zone : '+08:00');
	return {
		ad: { value: dt.ad },
		date: { value: dt.clone() },
		time: { value: dt.clone() },
		zone: { value: record && record.zone ? record.zone : dt.zone || '+08:00' },
		lon: { value: record && record.lon ? record.lon : '' },
		lat: { value: record && record.lat ? record.lat : '' },
		gpsLon: { value: record && record.gpsLon !== undefined ? record.gpsLon : 0 },
		gpsLat: { value: record && record.gpsLat !== undefined ? record.gpsLat : 0 },
		gender: { value: record && record.gender !== undefined && record.gender !== null ? record.gender : 1 },
		after23NewDay: { value: record && record.after23NewDay !== undefined ? record.after23NewDay : defaultAfter23NewDay() },
		lateZiHourUseNextDay: { value: record && record.lateZiHourUseNextDay !== undefined ? record.lateZiHourUseNextDay : defaultLateZiHourUseNextDay() },
		timeAlg: { value: record && record.timeAlg !== undefined ? record.timeAlg : 0 },
	};
}

function buildCaseSnapshotParams(record){
	const fields = buildCaseSnapshotFields(record || {});
	return {
		date: fields.date.value.format('YYYY-MM-DD'),
		time: fields.time.value.format('HH:mm:ss'),
		zone: fields.zone.value,
		lon: fields.lon.value,
		lat: fields.lat.value,
		gpsLat: fields.gpsLat.value,
		gpsLon: fields.gpsLon.value,
		after23NewDay: (fields.after23NewDay && fields.after23NewDay.value !== undefined) ? fields.after23NewDay.value : defaultAfter23NewDay(),
		lateZiHourUseNextDay: (fields.lateZiHourUseNextDay && fields.lateZiHourUseNextDay.value !== undefined) ? fields.lateZiHourUseNextDay.value : defaultLateZiHourUseNextDay(),
	};
}

function getSnapshotSaveModuleName(key){
	if(key === 'sixyao'){
		return 'guazhan';
	}
	return key;
}

function getCaseGenderLabel(record){
	return `${record && record.gender !== undefined && record.gender !== null ? record.gender : ''}` === '0' ? '女' : '男';
}

function saveGeneratedTechniqueSnapshot(key, content, record, extraMeta = {}){
	const text = `${content || ''}`.trim();
	if(!text){
		return null;
	}
	return saveModuleAISnapshot(
		getSnapshotSaveModuleName(normalizeTechniqueKey(key)),
		text,
		buildSnapshotMetaFromRecord(record, extraMeta)
	);
}

function buildSanshiUnifiedFallbackSnapshot(record, payload){
	const result = payload && payload.result ? payload.result : {};
	const sections = [];
	if(result.liureng){
		const liurengText = buildLiuRengSnapshotText(
			buildCaseSnapshotParams(record),
			result.liureng,
			null,
			null,
			2,
			'土',
			record && record.gender !== undefined && record.gender !== null ? record.gender : 1
		);
		if(liurengText){
			sections.push(`[大六壬]\n${liurengText}`);
		}
	}
	if(result.dunjia){
		const qimenText = buildDunJiaSnapshotText(result.dunjia);
		if(qimenText){
			sections.push(`[奇门遁甲]\n${qimenText}`);
		}
	}
	if(result.taiyi){
		const taiyiText = buildTaiyiSnapshotText(result.taiyi);
		if(taiyiText){
			sections.push(`[太乙]\n${taiyiText}`);
		}
	}
	if(result.keData || result.sanChuan){
		sections.push('[三式合一结构化数据]\n' + JSON.stringify({
			options: payload && payload.options ? payload.options : {},
			result: payload && payload.result ? payload.result : {},
		}, null, 2));
	}
	return sections.join('\n\n').trim();
}

async function requestLiurengGods(record){
	const fields = buildCaseSnapshotFields(record);
	const params = {
		ad: fields.ad.value,
		date: fields.date.value.format('YYYY-MM-DD'),
		time: fields.time.value.format('HH:mm'),
		zone: fields.zone.value,
		lon: fields.lon.value,
		lat: fields.lat.value,
		gpsLat: fields.gpsLat.value,
		gpsLon: fields.gpsLon.value,
		after23NewDay: fields.after23NewDay.value,
		lateZiHourUseNextDay: fields.lateZiHourUseNextDay && fields.lateZiHourUseNextDay.value !== undefined ? fields.lateZiHourUseNextDay.value : defaultLateZiHourUseNextDay(),
	};
	const data = await request(`${Constants.ServerRoot}/liureng/gods`, {
		body: JSON.stringify(params),
		silent: true,
		timeoutMs: 45000,
	});
	const result = data && data[Constants.ResultKey] ? data[Constants.ResultKey] : null;
	if(!result || !result.liureng){
		return null;
	}
	return {
		params,
		liureng: result.liureng,
	};
}

async function regenerateLiurengSnapshot(record){
	const result = await requestLiurengGods(record);
	if(!result || !result.liureng){
		return '';
	}
	return buildLiuRengSnapshotText(
		result.params,
		result.liureng,
		null,
		null,
		2,
		'土',
		record && record.gender !== undefined && record.gender !== null ? record.gender : 1
	);
}

async function regenerateJinkouSnapshot(record, payload){
	const result = await requestLiurengGods(record);
	if(!result || !result.liureng){
		return '';
	}
	const timeText = result.liureng && result.liureng.nongli ? result.liureng.nongli.time : '';
	const diFen = resolveJinKouDiFen(
		payload && payload.diFen,
		false,
		timeText,
		!!(payload && payload.diFen)
	);
	const jinkouData = buildJinKouData(result.liureng, {
		diFen,
		guirengType: payload && payload.guireng !== undefined && payload.guireng !== null ? payload.guireng : 2,
		isDiurnal: null,
	});
	return buildJinKouSnapshotText(
		result.params,
		result.liureng,
		null,
		jinkouData,
		payload && payload.wuxing ? payload.wuxing : '土',
		payload && payload.guireng !== undefined && payload.guireng !== null ? payload.guireng : 2,
		record && record.gender !== undefined && record.gender !== null ? record.gender : 1
	);
}

async function regenerateQimenSnapshot(record, payload){
	const fields = buildCaseSnapshotFields(record);
	const params = buildCaseSnapshotParams(record);
	const nongli = await fetchPreciseNongli(params);
	if(!nongli){
		return '';
	}
	const options = {
		...DEFAULT_QIMEN_OPTIONS,
		...(payload && payload.options ? payload.options : {}),
	};
	const pan = calcDunJia(fields, nongli, options, {});
	return buildDunJiaSnapshotText(pan);
}

async function regenerateTaiyiSnapshot(record, payload){
	const fields = buildCaseSnapshotFields(record);
	const params = buildCaseSnapshotParams(record);
	const nongli = await fetchPreciseNongli(params);
	if(!nongli){
		return '';
	}
	const options = {
		...DEFAULT_TAIYI_OPTIONS,
		...(payload && payload.options ? payload.options : {}),
	};
	if(!options.sex){
		options.sex = getCaseGenderLabel(record);
	}
	const pan = await fetchTaiyiPan(fields, nongli, options);
	return buildTaiyiSnapshotText(pan);
}

async function regenerateSanshiUnifiedSnapshot(record, payload){
	const [liurengText, qimenText, taiyiText] = await Promise.all([
		regenerateLiurengSnapshot(record),
		regenerateQimenSnapshot(record, payload),
		regenerateTaiyiSnapshot(record, payload),
	]);
	const sections = [];
	if(liurengText){
		sections.push(`[大六壬]\n${liurengText}`);
	}
	if(qimenText){
		sections.push(`[奇门遁甲]\n${qimenText}`);
	}
	if(taiyiText){
		sections.push(`[太乙]\n${taiyiText}`);
	}
	if(sections.length){
		return sections.join('\n\n').trim();
	}
	return buildSanshiUnifiedFallbackSnapshot(record, payload || {});
}

function generateCaseTechniqueSnapshot(record, moduleName, payload){
	const key = normalizeTechniqueKey(moduleName || (payload && payload.module) || (record && record.sourceModule) || '');
	if(!record || !key){
		return '';
	}
	const params = buildCaseSnapshotParams(record);
	switch(key){
	case 'liureng':
		if(!payload || !payload.liureng){
			return '';
		}
		return buildLiuRengSnapshotText(
			params,
			payload.liureng,
			payload.runyear || null,
			null,
			payload.guireng !== undefined && payload.guireng !== null ? payload.guireng : 2,
			payload.wuxing || '土',
			record.gender !== undefined && record.gender !== null ? record.gender : 1,
			{
				castMethod: payload.castMethod,
				xuanShiZhi: payload.xuanShiZhi,
				yanShuNum: payload.yanShuNum,
				yueJiangMethod: payload.yueJiangMethod,
				fenZhouYe: payload.fenZhouYe,
			}
		);
	case 'jinkou': {
		if(!payload || !payload.liureng){
			return '';
		}
		const timeText = payload.liureng && payload.liureng.nongli ? payload.liureng.nongli.time : '';
		const diFen = resolveJinKouDiFen(
			payload.diFen,
			false,
			timeText,
			!!payload.diFen
		);
		const jinkouData = buildJinKouData(payload.liureng, {
			diFen,
			guirengType: payload.guireng !== undefined && payload.guireng !== null ? payload.guireng : 2,
			isDiurnal: null,
		});
		return buildJinKouSnapshotText(
			params,
			payload.liureng,
			payload.runyear || null,
			jinkouData,
			payload.wuxing || '',
			payload.guireng !== undefined && payload.guireng !== null ? payload.guireng : 2,
			record.gender !== undefined && record.gender !== null ? record.gender : 1
		);
	}
	case 'qimen':
		if(!payload || !(payload.pan || (payload.result && payload.result.dunjia) || payload.dunjia)){
			return '';
		}
		return buildDunJiaSnapshotText(payload.pan || (payload.result && payload.result.dunjia) || payload.dunjia);
	case 'tongshefa': {
		const selection = payload && (payload.selection || (payload.tongshefa && payload.tongshefa.selection));
		if(!selection){
			return '';
		}
		return buildTongSheFaSnapshot(buildTongSheFaModel(selection));
	}
	case 'sixyao':
		if(!payload || !payload.gua){
			return '';
		}
		return buildGuaSnapshotText(buildCaseSnapshotFields(record), payload && payload.gua ? payload.gua : {});
	case 'taiyi':
		if(!payload || !(payload.pan || (payload.result && payload.result.taiyi) || payload.taiyi)){
			return '';
		}
		return buildTaiyiSnapshotText(payload.pan || (payload.result && payload.result.taiyi) || payload.taiyi);
	case 'sanshiunited':
		if(!payload || (!payload.moduleSnapshots && !payload.modules && !payload.snapshot && !payload.result)){
			return '';
		}
		return buildSanshiUnifiedFallbackSnapshot(record, payload || {});
	default:
		return '';
	}
}

async function regenerateCaseTechniqueSnapshot(record, moduleName, payload){
	const key = normalizeTechniqueKey(moduleName || (payload && payload.module) || (record && record.sourceModule) || '');
	if(!record || !key){
		return '';
	}
	switch(key){
	case 'liureng':
		return regenerateLiurengSnapshot(record);
	case 'jinkou':
		return regenerateJinkouSnapshot(record, payload);
	case 'qimen':
		return regenerateQimenSnapshot(record, payload);
	case 'taiyi':
		return regenerateTaiyiSnapshot(record, payload);
	case 'sanshiunited':
		return regenerateSanshiUnifiedSnapshot(record, payload);
	case 'horary':
		return regenerateHorarySnapshot(record);
	case 'election':
		return regenerateElectionSnapshot(record);
	default:
		return '';
	}
}

// 命盘技法的出生参数（形状对齐各组件 genParams：date 'YYYY-MM-DD' / time 'HH:mm:ss'）。
function buildChartBaziParams(record){
	const fields = buildFieldObject(record);
	return {
		date: fields.date.value.format('YYYY-MM-DD'),
		time: fields.time.value.format('HH:mm:ss'),
		zone: fields.zone.value,
		lon: fields.lon.value,
		lat: fields.lat.value,
		gpsLat: fields.gpsLat.value,
		gpsLon: fields.gpsLon.value,
		gender: fields.gender.value,
		timeAlg: fields.timeAlg.value,
		phaseType: fields.phaseType.value,
		godKeyPos: fields.godKeyPos.value,
		after23NewDay: fields.after23NewDay.value,
		lateZiHourUseNextDay: fields.lateZiHourUseNextDay && fields.lateZiHourUseNextDay.value !== undefined ? fields.lateZiHourUseNextDay.value : defaultLateZiHourUseNextDay(),
		adjustJieqi: fields.adjustJieqi.value,
	};
}

function buildChartZiweiParams(record){
	const fields = buildFieldObject(record);
	return {
		date: fields.date.value.format('YYYY-MM-DD'),
		time: fields.time.value.format('HH:mm:ss'),
		zone: fields.zone.value,
		lon: fields.lon.value,
		lat: fields.lat.value,
		gpsLat: fields.gpsLat.value,
		gpsLon: fields.gpsLon.value,
		gender: fields.gender.value,
		timeAlg: fields.timeAlg.value === 1 ? 1 : 0,
		after23NewDay: fields.after23NewDay.value,
		lateZiHourUseNextDay: fields.lateZiHourUseNextDay && fields.lateZiHourUseNextDay.value !== undefined ? fields.lateZiHourUseNextDay.value : defaultLateZiHourUseNextDay(),
	};
}

// 数算（参评数 / 河洛理数）：纯前端。先用本盘出生数据排四柱（buildLocalBaziResult），再喂各自引擎。
// 镜像 HeLuoMain.getModel 的取数口径；缺四柱即返 null → 上层显示「缺失」（不挂空表头）。
function buildChartShusuanBazi(record){
	try{
		const params = buildChartBaziParams(record);
		const bazi = buildLocalBaziResult(params).bazi;
		const fc = (bazi && bazi.fourColumns) || {};
		const gz = (p)=>(p && (p.ganzi || p.ganZhi)) || '';
		const fourPillars = { year: gz(fc.year), month: gz(fc.month), day: gz(fc.day), hour: gz(fc.time) };
		if(!fourPillars.year || !fourPillars.month || !fourPillars.day || !fourPillars.hour){
			return null;
		}
		return {
			fourPillars,
			yearGz: fourPillars.year,
			monthZhi: fourPillars.month.charAt(1),
			dayZhi: fourPillars.day.charAt(1),
			hourZhi: fourPillars.hour.charAt(1),
			birthYear: parseInt(`${params.date}`.slice(0, 4), 10) || 0,
			gender: bazi.gender === 'Female' ? '女' : '男',
		};
	}catch(e){
		return null;
	}
}

async function buildCanpingSnapshotForRecord(record){
	const b = buildChartShusuanBazi(record);
	if(!b){ return ''; }
	try{
		const result = canpingCalculate({
			yearGz: b.yearGz,
			monthBranch: b.monthZhi,
			dayBranch: b.dayZhi,
			hourBranch: b.hourZhi,
			gender: b.gender,
			method: 'ming',
			qiyunAge: 1,
		});
		// 补全生涯流年表:此前不传 liunianRows → result.liunian 恒 null、快照缺整层流年(用户反馈数算缺流年)。
		let liunianRows = null;
		try{
			const series = canpingLiunianSeries({
				yearGz: b.yearGz,
				monthBranch: b.monthZhi,
				dayBranch: b.dayZhi,
				hourBranch: b.hourZhi,
				gender: b.gender,
				method: 'ming',
				qiyunAge: 1,
				birthYear: b.birthYear,
				startAge: 1,
				endAge: 120,
			});
			liunianRows = (series && series.rows) || null;
		}catch(e){ liunianRows = null; }
		return buildCanpingSnapshotText(result, { liunianRows }) || '';
	}catch(e){
		return '';
	}
}

async function buildHeluoSnapshotForRecord(record){
	const b = buildChartShusuanBazi(record);
	if(!b){ return ''; }
	try{
		const chart = heluoCalc({
			fourPillars: b.fourPillars,
			gender: b.gender,
			hourZhi: b.hourZhi,
			birthYear: b.birthYear,
			monthZhi: b.monthZhi,
		});
		if(!chart || !chart.xian || !chart.xian.name || !chart.hou || !chart.hou.name){
			return '';
		}
		const dy = heluoDaYun(chart.xian, chart.hou, b.birthYear);
		const jg = heluoJudge(chart, b.fourPillars, b.monthZhi, null);
		return buildHeluoSnapshotText(chart, jg, dy) || '';
	}catch(e){
		return '';
	}
}

// 取该盘的西洋星盘原始结果（含 predictive 衍生数据，如 firdaria；可选含主限法）。
async function fetchChartResultForRecord(record, options = {}){
	const fields = buildFieldObject(record);
	const rsp = await fetchChart({
		...fieldParams(fields),
		includePrimaryDirection: !!options.includePrimaryDirection,
	}, {
		silent: true,
		timeoutMs: 20000,
	});
	return rsp && rsp.Result ? rsp.Result : null;
}

// 卜卦盘 horary：仅凭起课时间+地点起西洋盘(无需人工摇卦),用引擎默认类别 general 出结构化裁决快照。
// 与 DivinationChartShell 同源(fetchChart→Result→runHorary);后端不可达 → 无盘返 '' → 显「缺失」(西洋盘必后端)。
async function regenerateHorarySnapshot(record){
	// 起课/事盘记录用 divTime,但西洋盘 fetch 走 buildFieldObject(读 record.birth)→ 须把起课时刻映射为 birth 才能起盘。
	const chartRecord = (record && record.birth) ? record : { ...record, birth: (record && (record.divTime || record.updateTime)) || '' };
	const chart = await fetchChartResultForRecord(chartRecord);
	if(!chart){
		return '';
	}
	try{
		const j = runHorary(chart, 'general');
		return j ? (buildHorarySnapshot(j) || '') : '';
	}catch(e){
		return '';
	}
}

// 择日盘 election：同理,引擎默认 topicId=marriage(runElection 自带兜底)出总评/红线/分项/应期/建议快照。
async function regenerateElectionSnapshot(record){
	// 同 horary:起课/事盘记录用 divTime,映射为 birth 后才能起西洋盘。
	const chartRecord = (record && record.birth) ? record : { ...record, birth: (record && (record.divTime || record.updateTime)) || '' };
	const chart = await fetchChartResultForRecord(chartRecord);
	if(!chart){
		return '';
	}
	try{
		const j = runElection(chart, 'marriage');
		return j ? (buildElectionSnapshot(j) || '') : '';
	}catch(e){
		return '';
	}
}

// 5 个「目标时刻型」推运（小限 profection / 太阳弧 solararc / 太阳返照 solarreturn /
// 月亮返照 lunarreturn / 流年 givenyear）：POST /predict/<key>，目标时刻默认「此刻」
// （与各组件 datetime 默认一致 = 当前流年/期），用共享 buildPredictiveSnapshotText 出 [星盘信息]/[起盘信息]/[相位] 快照。
// 无相位数据即返 '' → 挂载显示「缺失」而非空段头。
async function buildPredictivePeriodSnapshot(chartObj, key){
	if(!chartObj){
		return '';
	}
	const np = chartObj.params || {};
	let datetimeStr = '';
	try{
		datetimeStr = new DateTime().format('YYYY-MM-DD HH:mm');
	}catch(e){
		datetimeStr = '';
	}
	const params = {
		date: np.date,
		time: np.time,
		ad: np.ad !== undefined ? np.ad : 1,
		zone: np.zone,
		dirZone: np.zone,
		lon: np.lon,
		lat: np.lat,
		gpsLat: np.gpsLat,
		gpsLon: np.gpsLon,
		hsys: np.hsys,
		zodiacal: np.zodiacal,
		tradition: np.tradition,
		datetime: datetimeStr,
		tmType: 'y',
		nodeRetrograde: false,
		asporb: 1,
	};
	if(!params.date && np.birth){
		const parts = `${np.birth}`.split(' ');
		params.date = parts[0];
		params.time = params.time || parts[1] || '';
	}
	try{
		const data = await request(`${Constants.ServerRoot}/predict/${key}`, {
			body: JSON.stringify(params),
			timeoutMs: 60000,
		});
		const result = data && data[Constants.ResultKey];
		if(!result){
			return '';
		}
		return buildPredictiveSnapshotText(chartObj, params, result) || '';
	}catch(e){
		return '';
	}
}

// 命盘侧：按该盘的出生数据无头复算指定技法的快照文本。占卜/事盘走 Part F，不在此列。
async function regenerateChartTechniqueSnapshot(record, key){
	if(!record){
		return '';
	}
	try{
		switch(normalizeTechniqueKey(key)){
		case 'bazi':
			return await buildBaziSnapshotForParams(buildChartBaziParams(record));
		case 'ziwei':
			return await buildZiweiSnapshotForParams(buildChartZiweiParams(record));
		case 'indiachart':
			return await buildIndiaSnapshotForFields(buildFieldObject(record), 1);
		case 'firdaria': {
			// 法达星限随西洋盘 predictive 一并返回，直接读取即可。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (buildFirdariaSnapshotText(chartObj) || '') : '';
		}
		case 'distributions': {
			// 界推运：上升点经主限运动穿越埃及界，分配星(界主)+参与星。内部 fetch /predict/dist。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (await buildDistributionsSnapshotText(chartObj) || '') : '';
		}
		case 'agepoint': {
			// 年龄推进点（Huber）：年龄点自上升点起沿 Koch 宫顺行。内部 fetch /predict/agepoint。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (await buildAgePointSnapshotText(chartObj) || '') : '';
		}
		case 'planetaryages': {
			// 行星年龄（托勒密人生七阶）：纯前端固定七阶表，读本命盘。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (buildPlanetaryAgesSnapshotText(chartObj) || '') : '';
		}
		case 'vedicprog': {
			// 恒星推运（Vedic）：二/三/小限推运在恒星黄道下计算。内部 fetch /astroextra/progressions + zodiacal:1。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (await buildVedicProgSnapshotText(chartObj) || '') : '';
		}
		case 'balbillus': {
			// Balbillus：十年大运月制族变体（旺距削减），纯前端独立引擎，读本命盘。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (buildBalbillusSnapshotText(chartObj) || '') : '';
		}
		case 'yearsystem129': {
			// 129 年系统：七政小年序列（仿 firdaria），随盘 predictive 返回。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (buildYearSystem129SnapshotText(chartObj) || '') : '';
		}
		case 'planetaryarc': {
			// 行星弧：solararc 引擎换弧源（默认月亮弧）。内部 fetch /predict/planetaryarc。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (await buildPlanetaryArcSnapshotText(chartObj) || '') : '';
		}
		case 'persiandirected': {
			// 波斯向运：黄经象征向运(1°/年,宫头不动)，应期 hit-list 纯前端算术，读本命盘。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (buildPersianDirectedSnapshotText(chartObj) || '') : '';
		}
		case 'jaynesprog': {
			// Jayne 赤纬推运：推运后看赤纬平行/反平行。内部 fetch /astroextra/jaynesprog。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (await buildJaynesProgSnapshotText(chartObj) || '') : '';
		}
		case 'primarydirchart':
		case 'primarydirect': {
			// 主限法 / 主限法盘（同一主限方向数据）：取含主限法的西洋盘（默认 Alchabitius 弧 / Ptolemy 时钥 / 显示界限）。
			const chartObj = await fetchChartResultForRecord(record, { includePrimaryDirection: true });
			if(!chartObj){
				return '';
			}
			const snapshotChartObj = {
				...chartObj,
				params: {
					...(chartObj.params || {}),
					showPdBounds: 1,
					pdMethod: 'core_alchabitius',
					pdTimeKey: 'Ptolemy',
				},
			};
			return buildPrimaryDirectSnapshotText(snapshotChartObj) || '';
		}
		case 'profection':
		case 'solararc':
		case 'solarreturn':
		case 'lunarreturn':
		case 'givenyear': {
			// 目标时刻型推运：取本命西洋盘后按「此刻」起该期推运（POST /predict/<key>）。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (await buildPredictivePeriodSnapshot(chartObj, normalizeTechniqueKey(key)) || '') : '';
		}
		case 'zodialrelease': {
			// 黄道星释：取本命盘后 fetch /predict/zr，福点基点 + L1 全列概览。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (await buildZodialReleaseSnapshotText(chartObj) || '') : '';
		}
		case 'decennials': {
			// 十年大运：纯前端 buildDecennialTimeline（默认设置）+ L1 全列概览。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (buildDecennialsSnapshotText(chartObj) || '') : '';
		}
		case 'guolao':
			// 七政四余：命度/罗计沿用已保存设置，显示全部传统星曜。
			return await buildGuolaoSnapshotForFields(buildFieldObject(record));
		case 'suzhan': {
			// 宿占：宿盘随标准西洋盘的二十八宿数据生成，显示全部传统星曜。
			const chartObj = await fetchChartResultForRecord(record);
			return chartObj ? (buildSuzhanSnapshotText(chartObj, buildFieldObject(record), null) || '') : '';
		}
		case 'germany':
			// 量化盘（中点盘）。
			return await buildGermanySnapshotForFields(buildFieldObject(record));
		case 'canping':
			// 邵子参评数（数算）：纯前端，按本盘出生四柱起本命 + 大运。
			return await buildCanpingSnapshotForRecord(record);
		case 'heluo':
			// 河洛理数（数算）：纯前端，按本盘出生四柱起先后天卦 + 大限 + 命运篇判断。
			return await buildHeluoSnapshotForRecord(record);
		case 'xianqin':
			// 演禽（禽星）：经 ken 后端按出生数据起盘。
			return await buildKinAstroSnapshotForFields(buildFieldObject(record), 'xianqin');
		case 'cetian':
			// 策天飞星：经 ken 后端按出生数据起盘。
			return await buildKinAstroSnapshotForFields(buildFieldObject(record), 'cetian');
		case 'huangji':
			// 皇极经世：经 ken 后端起元会运世盘。
			return await buildHuangJiSnapshotForFields(buildFieldObject(record));
		default:
			return '';
		}
	}catch(e){
		return '';
	}
}

function summarizeCasePayload(record, payload){
	const lines = [];
	const meta = getCaseTypeMeta(record.caseType);
	lines.push(`案例名称：${record.event || '未命名案例'}`);
	lines.push(`案例类型：${getCaseTypeLabel(record.caseType)}`);
	lines.push(`所属模块：${record.sourceModule || meta.module || meta.value || ''}`);
	if(record.divTime){
		lines.push(`占断时间：${record.divTime}`);
	}
	if(record.zone){
		lines.push(`时区：${record.zone}`);
	}
	if(record.pos){
		lines.push(`地点：${record.pos}`);
	}
	const tags = normalizeTags(record.group);
	if(tags.length){
		lines.push(`标签：${tags.join('、')}`);
	}
	lines.push('');
	lines.push('结构化案例数据：');
	lines.push(JSON.stringify(payload || {}, null, 2));
	return lines.join('\n').trim();
}

function summarizeCaseMeta(record){
	const lines = [];
	const meta = getCaseTypeMeta(record.caseType);
	lines.push(`案例名称：${record.event || '未命名案例'}`);
	lines.push(`案例类型：${getCaseTypeLabel(record.caseType)}`);
	lines.push(`所属模块：${record.sourceModule || meta.module || meta.value || ''}`);
	if(record.divTime){
		lines.push(`占断时间：${record.divTime}`);
	}
	if(record.zone){
		lines.push(`时区：${record.zone}`);
	}
	if(record.pos){
		lines.push(`地点：${record.pos}`);
	}
	const tags = normalizeTags(record.group);
	if(tags.length){
		lines.push(`标签：${tags.join('、')}`);
	}
	return lines.join('\n').trim();
}

function extractCaseSnapshotText(record){
	const payload = safeParseJson(record.payload, null);
	if(!payload){
		return {
			content: summarizeCasePayload(record, null),
			payload: null,
			moduleName: record.sourceModule || getCaseTypeMeta(record.caseType).module,
			snapshotStatus: 'generated',
		};
	}
	const snapshot =
		(payload.snapshot && payload.snapshot.content) ||
		(payload.snapshot && payload.snapshot.text) ||
		payload.aiExport ||
		payload.aiSnapshot ||
		(payload.result && payload.result.aiSnapshot) ||
		(payload.result && payload.result.snapshotText) ||
		'';
	if(`${snapshot || ''}`.trim()){
		return {
			content: `${snapshot}`.trim(),
			payload,
			moduleName: payload.module || record.sourceModule || getCaseTypeMeta(record.caseType).module,
			snapshotStatus: 'ready',
		};
	}
	return {
		content: summarizeCasePayload(record, payload),
		payload,
		moduleName: payload.module || record.sourceModule || getCaseTypeMeta(record.caseType).module,
		snapshotStatus: 'generated',
	};
}

export function listAnalysisSources(){
	const charts = listLocalCharts({}).map((item)=>({
		id: item.cid,
		sourceType: 'chart',
		title: item.name || '未命名命盘',
		module: 'astrochart',
		time: item.birth || item.updateTime || '',
		zone: item.zone || '+08:00',
		tags: normalizeTags(item.group),
		snapshotStatus: 'lazy',
		updatedAt: item.updateTime || '',
		record: item,
	}));
	const cases = listLocalCases({}).map((item)=>{
		const meta = getCaseTypeMeta(item.caseType);
		const extracted = extractCaseSnapshotText(item);
		return {
			id: item.cid,
			sourceType: 'case',
			title: item.event || '未命名事盘',
			module: item.sourceModule || extracted.moduleName || meta.module,
			time: item.divTime || item.updateTime || '',
			zone: item.zone || '+08:00',
			tags: normalizeTags(item.group),
			snapshotStatus: extracted.snapshotStatus,
			updatedAt: item.updateTime || '',
			record: item,
		};
	});
	return charts.concat(cases).sort((a, b)=>{
		const ta = Date.parse(a.updatedAt || a.time || '') || 0;
		const tb = Date.parse(b.updatedAt || b.time || '') || 0;
		return tb - ta;
	});
}

function parseAstroSnapshotSignature(signature){
	const raw = `${signature || ''}`.trim();
	if(!raw){
		return null;
	}
	const parts = raw.split('|');
	return {
		chartId: `${parts[0] || ''}`.trim(),
		birth: `${parts[1] || ''}`.trim(),
		zone: `${parts[2] || ''}`.trim(),
		lon: `${parts[3] || ''}`.trim(),
		lat: `${parts[4] || ''}`.trim(),
		zodiacal: `${parts[5] || ''}`.trim(),
		hsys: `${parts[6] || ''}`.trim(),
	};
}

function normalizeSnapshotMatchText(value){
	return `${value || ''}`.trim();
}

function hasMatchingSavedAstroSnapshot(record){
	if(!record){
		return null;
	}
	const snapshot = loadAstroAISnapshot();
	if(!snapshot || !snapshot.content){
		return null;
	}
	const parsed = parseAstroSnapshotSignature(snapshot.signature);
	if(!parsed){
		return null;
	}
	const birth = normalizeSnapshotMatchText(record.birth);
	const zone = normalizeSnapshotMatchText(record.zone || '+08:00');
	const lon = normalizeSnapshotMatchText(record.lon);
	const lat = normalizeSnapshotMatchText(record.lat);
	if(parsed.birth && birth && parsed.birth !== birth){
		return null;
	}
	if(parsed.zone && zone && parsed.zone !== zone){
		return null;
	}
	if(parsed.lon && lon && parsed.lon !== lon){
		return null;
	}
	if(parsed.lat && lat && parsed.lat !== lat){
		return null;
	}
	if(!(parsed.birth || parsed.zone || parsed.lon || parsed.lat)){
		return null;
	}
	return snapshot;
}

async function buildChartContext(source){
	const record = source && source.record ? source.record : null;
	if(!record){
		throw new Error('chart.source.required');
	}
	const saved = hasMatchingSavedAstroSnapshot(record);
	if(saved){
		return {
			content: `${saved.content || ''}`.trim(),
			title: source.title,
			module: 'astrochart',
			meta: {
				sourceType: 'chart',
				sourceId: source.id,
				birth: record.birth || '',
				zone: record.zone || '',
				reusedStoredSnapshot: true,
			},
		};
	}
	const fields = buildFieldObject(record);
	const rsp = await fetchChart({
		...fieldParams(fields),
		includePrimaryDirection: false,
	}, {
		silent: true,
		timeoutMs: 20000,
	});
	if(!rsp || !rsp.Result){
		throw new Error('chart.context.failed');
	}
	const content = buildAstroSnapshotContent(rsp.Result, fields) || '';
	return {
		content: `${content}`.trim(),
		title: source.title,
		module: 'astrochart',
		meta: {
			sourceType: 'chart',
			sourceId: source.id,
			birth: record.birth || '',
			zone: record.zone || '',
		},
	};
}

function buildChartMetaContext(source){
	const record = source && source.record ? source.record : null;
	if(!record){
		throw new Error('chart.source.required');
	}
	const lines = [];
	lines.push(`命盘名称：${source.title || record.name || '未命名命盘'}`);
	lines.push('案例类型：命盘');
	if(record.birth){
		lines.push(`出生时间：${record.birth}`);
	}
	if(record.zone){
		lines.push(`时区：${record.zone}`);
	}
	if(record.lon || record.lat){
		lines.push(`经纬度：${record.lon || ''} ${record.lat || ''}`.trim());
	}
	if(record.pos){
		lines.push(`地点：${record.pos}`);
	}
	const tags = normalizeTags(record.group);
	if(tags.length){
		lines.push(`标签：${tags.join('、')}`);
	}
	return {
		content: lines.join('\n').trim(),
		title: source.title,
		module: 'chart_meta',
		meta: {
			sourceType: 'chart',
			sourceId: source.id,
			birth: record.birth || '',
			zone: record.zone || '',
			metaOnly: true,
		},
	};
}

async function buildCaseContext(source){
	const record = source && source.record ? source.record : null;
	if(!record){
		throw new Error('case.source.required');
	}
	const extracted = extractCaseSnapshotText(record);
	if(extracted.content && extracted.snapshotStatus === 'ready'){
		return {
			content: extracted.content,
			title: source.title,
			module: extracted.moduleName,
			meta: {
				sourceType: 'case',
				sourceId: source.id,
				caseType: record.caseType,
				divTime: record.divTime,
			},
		};
	}
	// Part F：事盘只从自身 payload 重建文本（用起盘结果，不碰时间），不读全局模块缓存
	// （那是「上次看过的某一卦」，会挂出与所选事盘对不上的内容），也不按时间重新起盘。
	const generated = generateCaseTechniqueSnapshot(record, extracted.moduleName, extracted.payload);
	if(generated){
		saveGeneratedTechniqueSnapshot(extracted.moduleName, generated, record);
		return {
			content: generated,
			title: source.title,
			module: extracted.moduleName,
			meta: {
				sourceType: 'case',
				sourceId: source.id,
				caseType: record.caseType,
				divTime: record.divTime,
				generatedFromStoredCase: true,
			},
		};
	}
	return {
		content: extracted.content,
		title: source.title,
		module: extracted.moduleName,
		meta: {
			sourceType: 'case',
			sourceId: source.id,
			caseType: record.caseType,
			divTime: record.divTime,
		},
	};
}

function buildCaseMetaContext(source){
	const record = source && source.record ? source.record : null;
	if(!record){
		throw new Error('case.source.required');
	}
	return {
		content: summarizeCaseMeta(record),
		title: source.title,
		module: source.module || record.sourceModule || getCaseTypeMeta(record.caseType).module,
		meta: {
			sourceType: 'case',
			sourceId: source.id,
			caseType: record.caseType,
			divTime: record.divTime,
			metaOnly: true,
		},
	};
}

function normalizeTechniqueKey(key){
	const text = `${key || ''}`.trim();
	if(!text){
		return '';
	}
	if(text === 'liuyao' || text === 'guazhan'){
		return 'sixyao';
	}
	if(text === 'dunjia'){
		return 'qimen';
	}
	if(text === 'germanytech'){
		return 'germany';
	}
	if(text === 'hellenastro' || text === 'locastro'){
		return 'astrochart_like';
	}
	if(text === 'relativechart'){
		return 'relative';
	}
	if(text === 'jieqichart'){
		return 'jieqi';
	}
	if(text === 'chart13'){
		return 'astrochart_like';
	}
	return text;
}

function getTechniqueLabel(key){
	return ANALYSIS_TECHNIQUE_LABELS[normalizeTechniqueKey(key)] || `${key || ''}`.trim();
}

function getTechniqueAliasList(moduleName){
	const name = normalizeTechniqueKey(moduleName);
	if(!name){
		return [];
	}
	const set = new Set([name]);
	if(name === 'sixyao'){
		set.add('guazhan');
		set.add('liuyao');
	}
	if(name === 'qimen'){
		set.add('dunjia');
	}
	if(name === 'primarydirect' || name === 'primarydirchart'){
		set.add('direction');
		set.add('primarydirect');
		set.add('primarydirchart');
	}
	if(name === 'zodialrelease'){
		set.add('zodiacrelease');
	}
	if(name === 'decennials'){
		set.add('decennial');
	}
	if(name === 'germany'){
		set.add('germanytech');
	}
	if(name === 'relative'){
		set.add('relativechart');
	}
	if(name === 'astrochart_like'){
		set.add('hellenastro');
		set.add('locastro');
		set.add('chart13');
	}
	if(name === 'indiachart'){
		set.add('indiachart_current');
	}
	if(name === 'jieqi'){
		set.add('jieqi_current');
		set.add('jieqi_meta');
		set.add('jieqi_chunfen');
		set.add('jieqi_xiazhi');
		set.add('jieqi_qiufen');
		set.add('jieqi_dongzhi');
	}
	return Array.from(set);
}

function normalizeDateText(value){
	const raw = `${value || ''}`.trim();
	if(!raw){
		return '';
	}
	const matched = raw.match(/^(-?\d+)[-/](\d{1,2})[-/](\d{1,2})/);
	if(!matched){
		return raw.replace(/-/g, '/');
	}
	return `${matched[1]}/${matched[2].padStart(2, '0')}/${matched[3].padStart(2, '0')}`;
}

function normalizeMinuteTime(value){
	const raw = `${value || ''}`.trim();
	if(!raw){
		return '';
	}
	const matched = raw.match(/^(\d{1,2}):(\d{2})/);
	if(!matched){
		return raw;
	}
	return `${matched[1].padStart(2, '0')}:${matched[2]}`;
}

function buildSourceSignature(source){
	const record = source && source.record ? source.record : null;
	if(!record){
		return {
			date: '',
			time: '',
			zone: '',
			lon: '',
			lat: '',
		};
	}
	const rawTime = source.sourceType === 'chart' ? record.birth : (record.divTime || record.updateTime || '');
	const matched = `${rawTime || ''}`.trim().match(/^(-?\d+)-(\d{2})-(\d{2})(?:\s+(\d{2}):(\d{2})(?::(\d{2}))?)?$/);
	if(!matched){
		return {
			date: normalizeDateText(rawTime),
			time: normalizeMinuteTime(rawTime),
			zone: `${record.zone || ''}`.trim(),
			lon: `${record.lon || ''}`.trim(),
			lat: `${record.lat || ''}`.trim(),
		};
	}
	return {
		date: `${matched[1]}/${matched[2]}/${matched[3]}`,
		time: normalizeMinuteTime(`${matched[4] || '00'}:${matched[5] || '00'}:${matched[6] || '00'}`),
		zone: `${record.zone || ''}`.trim(),
		lon: `${record.lon || ''}`.trim(),
		lat: `${record.lat || ''}`.trim(),
	};
}

function isSnapshotMetaCompatible(snapshotMeta, source){
	if(!snapshotMeta || typeof snapshotMeta !== 'object'){
		return true;
	}
	const current = buildSourceSignature(source);
	const snapDate = normalizeDateText(snapshotMeta.date || snapshotMeta.birth || '');
	if(current.date && snapDate && current.date !== snapDate){
		return false;
	}
	const snapTime = normalizeMinuteTime(snapshotMeta.time || '');
	if(current.time && snapTime && current.time !== snapTime){
		return false;
	}
	const snapZone = `${snapshotMeta.zone || ''}`.trim();
	if(current.zone && snapZone && current.zone !== snapZone){
		return false;
	}
	const snapLon = `${snapshotMeta.lon || ''}`.trim();
	if(current.lon && snapLon && current.lon !== snapLon){
		return false;
	}
	const snapLat = `${snapshotMeta.lat || ''}`.trim();
	if(current.lat && snapLat && current.lat !== snapLat){
		return false;
	}
	return true;
}

function extractSnapshotText(raw){
	if(raw === undefined || raw === null){
		return '';
	}
	if(typeof raw === 'string'){
		const txt = raw.trim();
		if(!txt){
			return '';
		}
		const parsed = safeParseJson(txt, null);
		return parsed !== null ? extractSnapshotText(parsed) : txt;
	}
	if(Array.isArray(raw)){
		for(let i = 0; i < raw.length; i += 1){
			const txt = extractSnapshotText(raw[i]);
			if(txt){
				return txt;
			}
		}
		return '';
	}
	if(typeof raw !== 'object'){
		return '';
	}
	if(typeof raw.content === 'string' && raw.content.trim()){
		return raw.content.trim();
	}
	if(typeof raw.text === 'string' && raw.text.trim()){
		return raw.text.trim();
	}
	const likelyKeys = ['value', 'snapshot', 'payload', 'data', 'result', 'snapshotText', 'moduleSnapshots', 'snapshots', 'modules'];
	for(let i = 0; i < likelyKeys.length; i += 1){
		const key = likelyKeys[i];
		if(raw[key] === undefined){
			continue;
		}
		const txt = extractSnapshotText(raw[key]);
		if(txt){
			return txt;
		}
	}
	return '';
}

function pickSnapshotCandidate(candidates){
	// 拒绝与当前案例出生/起盘签名明确不匹配的候选，避免挂载到「上次看过的那张盘」。
	// generated 候选恒为 compatible:true；payload/cache 候选由 isSnapshotMetaCompatible 判定（源签名为空时为 true，不误伤）。
	const valid = (candidates || []).filter((item)=>item && item.content && item.compatible !== false);
	if(!valid.length){
		return null;
	}
	valid.sort((a, b)=>{
		const sa = a.specificity || 0;
		const sb = b.specificity || 0;
		if(sa !== sb){
			return sb - sa;
		}
		if(Boolean(a.compatible) !== Boolean(b.compatible)){
			return a.compatible ? -1 : 1;
		}
		if(Boolean(a.fromPayload) !== Boolean(b.fromPayload)){
			return a.fromPayload ? -1 : 1;
		}
		const ta = Date.parse(a.createdAt || '') || 0;
		const tb = Date.parse(b.createdAt || '') || 0;
		if(ta !== tb){
			return tb - ta;
		}
		return `${b.content || ''}`.length - `${a.content || ''}`.length;
	});
	return valid[0];
}

function getTechniqueSnapshotFromPayload(payload, moduleName, source){
	if(!payload || typeof payload !== 'object'){
		return null;
	}
	const aliases = getTechniqueAliasList(moduleName);
	const aliasSet = new Set(aliases);
	const record = source && source.record ? source.record : null;
	const primaryPayloadKey = normalizeTechniqueKey(
		payload.module
		|| payload.moduleName
		|| payload.sourceModule
		|| (record && (record.sourceModule || record.caseType || record.chartType))
		|| ''
	);
	const genericSnapshotMatchesRequest = !primaryPayloadKey || aliasSet.has(primaryPayloadKey);
	const candidates = [];
	const pushCandidate = (raw, extra = {})=>{
		const content = extractSnapshotText(raw);
		if(!content){
			return;
		}
		candidates.push({
			content,
			createdAt: extra.createdAt || '',
			meta: extra.meta || {},
			compatible: isSnapshotMetaCompatible(extra.meta, source),
			fromPayload: true,
			specificity: extra.specificity || 0,
		});
	};
	if(genericSnapshotMatchesRequest){
		pushCandidate(payload.snapshot, {
			meta: payload.meta || {},
			createdAt: payload.createdAt || '',
			specificity: 0,
		});
	}
	if(payload.module && aliasSet.has(normalizeTechniqueKey(payload.module))){
		pushCandidate(payload.snapshot, {
			meta: payload.meta || {},
			createdAt: payload.createdAt || '',
			specificity: 1,
		});
	}
	aliases.forEach((alias, idx)=>{
		const aliasSpecificity = Math.max(2, 40 - idx);
		const moduleSpecificity = Math.max(3, 60 - idx);
		if(payload[alias] !== undefined){
			pushCandidate(payload[alias], {
				meta: payload.meta || {},
				createdAt: payload.createdAt || '',
				specificity: aliasSpecificity,
			});
		}
		const moduleSnapshots = payload.moduleSnapshots && typeof payload.moduleSnapshots === 'object' ? payload.moduleSnapshots : null;
		if(moduleSnapshots && moduleSnapshots[alias] !== undefined){
			pushCandidate(moduleSnapshots[alias], {
				meta: moduleSnapshots[alias] && moduleSnapshots[alias].meta ? moduleSnapshots[alias].meta : payload.meta || {},
				createdAt: moduleSnapshots[alias] && moduleSnapshots[alias].createdAt ? moduleSnapshots[alias].createdAt : payload.createdAt || '',
				specificity: moduleSpecificity,
			});
		}
		const modules = payload.modules && typeof payload.modules === 'object' ? payload.modules : null;
		if(modules && modules[alias] !== undefined){
			pushCandidate(modules[alias], {
				meta: modules[alias] && modules[alias].meta ? modules[alias].meta : payload.meta || {},
				createdAt: modules[alias] && modules[alias].createdAt ? modules[alias].createdAt : payload.createdAt || '',
				specificity: moduleSpecificity,
			});
		}
	});
	const snapshots = payload.snapshots && typeof payload.snapshots === 'object' ? payload.snapshots : null;
	if(snapshots){
		Object.keys(snapshots).forEach((rawKey)=>{
			const key = `${rawKey || ''}`.trim();
			if(!key){
				return;
			}
			const suffix = key.indexOf(MODULE_SNAPSHOT_PREFIX) === 0 ? key.substring(MODULE_SNAPSHOT_PREFIX.length) : key;
			if(!aliasSet.has(normalizeTechniqueKey(suffix))){
				return;
			}
			pushCandidate(snapshots[rawKey], {
				meta: snapshots[rawKey] && snapshots[rawKey].meta ? snapshots[rawKey].meta : payload.meta || {},
				createdAt: snapshots[rawKey] && snapshots[rawKey].createdAt ? snapshots[rawKey].createdAt : payload.createdAt || '',
				specificity: 3,
			});
		});
	}
	return pickSnapshotCandidate(candidates);
}

// 全局模块缓存 `horosa.ai.snapshot.module.v1.<module>` 本质是「上次算过的某一张盘/卦」（key 不含出生时间）。
// 复用它【只能在签名确凿匹配当前源时】，否则宁可回退按本盘出生数据重算，也绝不挂错盘。
// 与宽松的 isSnapshotMetaCompatible 不同：这里要求 date 双方都有且相等（date 是最强身份位）；
// 缺签名 / 单边为空一律判不确凿（false），交由 buildTechniqueContext 走重算分支。
function isCacheSnapshotConfidentMatch(snapshotMeta, source){
	if(!snapshotMeta || typeof snapshotMeta !== 'object'){
		return false;
	}
	const current = buildSourceSignature(source);
	const snapDate = normalizeDateText(snapshotMeta.date || snapshotMeta.birth || '');
	if(!current.date || !snapDate || current.date !== snapDate){
		return false;
	}
	const snapTime = normalizeMinuteTime(snapshotMeta.time || '');
	if(current.time && snapTime && current.time !== snapTime){
		return false;
	}
	const snapZone = `${snapshotMeta.zone || ''}`.trim();
	if(current.zone && snapZone && current.zone !== snapZone){
		return false;
	}
	const snapLon = `${snapshotMeta.lon || ''}`.trim();
	if(current.lon && snapLon && current.lon !== snapLon){
		return false;
	}
	const snapLat = `${snapshotMeta.lat || ''}`.trim();
	if(current.lat && snapLat && current.lat !== snapLat){
		return false;
	}
	return true;
}

function getTechniqueSnapshotFromCache(moduleName, source){
	const aliases = getTechniqueAliasList(moduleName);
	const candidates = aliases.map((alias, idx)=>{
		const snapshot = loadModuleAISnapshot(alias);
		if(!snapshot || !snapshot.content){
			return null;
		}
		return {
			content: snapshot.content,
			createdAt: snapshot.createdAt || '',
			meta: snapshot.meta || {},
			compatible: isCacheSnapshotConfidentMatch(snapshot.meta, source),
			fromPayload: false,
			specificity: Math.max(2, 40 - idx),
		};
	}).filter(Boolean);
	return pickSnapshotCandidate(candidates);
}

async function buildTechniqueContext(source, techniqueKey, baseSourceContext){
	const key = normalizeTechniqueKey(techniqueKey);
	if(!source || !key){
		return null;
	}
	const label = getTechniqueLabel(key);
	const canReuseBaseSourceContext = baseSourceContext
		&& baseSourceContext.content
		&& !(baseSourceContext.meta && baseSourceContext.meta.metaOnly);
	if(source.sourceType === 'chart' && (key === 'astrochart' || key === 'astrochart_like')){
		const ctx = canReuseBaseSourceContext ? baseSourceContext : await buildChartContext(source);
		return {
			key,
			title: label,
			module: key,
			content: ctx && ctx.content ? ctx.content : '',
			available: !!(ctx && ctx.content),
			status: ctx && ctx.content ? 'ready' : 'missing',
			meta: ctx && ctx.meta ? ctx.meta : {},
		};
	}
	const record = source.record || null;
	const payload = record && record.payload ? safeParseJson(record.payload, null) : null;
	const fromPayload = getTechniqueSnapshotFromPayload(payload, key, source);
	let generated = null;
	if(source.sourceType === 'timepoint'){
		// 「起课时间」入口：纯时间 + 地点，没有「已存的卦」→ 时间确定式法按默认设置即时起盘；
		// 非纯时间可推的（六爻/统摄法）不在白名单（界面也只提供白名单技法，正常走不到这里）。
		let timeText = '';
		if(TIME_CASTABLE_SET.has(key)){
			timeText = await regenerateCaseTechniqueSnapshot(record, key, payload);
			if(timeText){
				saveGeneratedTechniqueSnapshot(key, timeText, record, { generatedFromTimepoint: true });
			}
		}
		return {
			key,
			title: label,
			module: key,
			content: timeText || '',
			available: !!timeText,
			status: timeText ? 'ready' : 'missing',
			meta: timeText ? buildSnapshotMetaFromRecord(record, { generatedFromTimepoint: true }) : {},
		};
	}
	if(source.sourceType === 'case'){
		// 事盘：优先用本案例 payload 重建文本（不读全局模块缓存——那是「上次看过的某一卦」）。
		// 若 payload 未存该技法：时间确定式法（六壬/金口诀/奇门/太乙/三式）按本案例起课时间 + 默认【即时补算】，
		// 像命盘一样而非显示「未挂载」；六爻等不在白名单 → 保持 Part F：绝不按时间重算（不伪造卦象）。
		if(!(fromPayload && fromPayload.content)){
			let generatedText = generateCaseTechniqueSnapshot(record, key, payload);
			let genFlag = { generatedFromStoredCase: true };
			if(!generatedText && TIME_CASTABLE_SET.has(key)){
				generatedText = await regenerateCaseTechniqueSnapshot(record, key, payload);
				genFlag = { regeneratedFromCaseTime: true };
			}
			if(generatedText){
				saveGeneratedTechniqueSnapshot(key, generatedText, record, genFlag);
				generated = {
					content: generatedText,
					createdAt: new Date().toISOString(),
					meta: buildSnapshotMetaFromRecord(record, genFlag),
					compatible: true,
					fromPayload: false,
					specificity: 4,
				};
			}
		}
		const pickedCase = pickSnapshotCandidate([fromPayload, generated]);
		return {
			key,
			title: label,
			module: key,
			content: pickedCase && pickedCase.content ? pickedCase.content : '',
			available: !!(pickedCase && pickedCase.content),
			status: pickedCase && pickedCase.content ? 'ready' : 'missing',
			meta: pickedCase && pickedCase.meta ? pickedCase.meta : {},
		};
	}
	// 命盘（chart）：payload 命中优先；否则查兼容缓存（A1 已过滤掉不匹配的盘）；
	// 仍无则按本盘出生数据无头复算（Part A）。
	const fromCache = getTechniqueSnapshotFromCache(key, source);
	if(!(fromPayload && fromPayload.content) && !(fromCache && fromCache.content)){
		const generatedText = await regenerateChartTechniqueSnapshot(record, key);
		if(generatedText){
			saveGeneratedTechniqueSnapshot(key, generatedText, record, {
				generatedFromChart: true,
			});
			generated = {
				content: generatedText,
				createdAt: new Date().toISOString(),
				meta: buildSnapshotMetaFromRecord(record, {
					generatedFromChart: true,
				}),
				compatible: true,
				fromPayload: false,
				specificity: 5,
			};
		}
	}
	const picked = pickSnapshotCandidate([fromPayload, fromCache, generated]);
	return {
		key,
		title: label,
		module: key,
		content: picked && picked.content ? picked.content : '',
		available: !!(picked && picked.content),
		status: picked && picked.content ? 'ready' : 'missing',
		meta: picked && picked.meta ? picked.meta : {},
	};
}

export function listAnalysisTechniqueOptions(source){
	let keys;
	if(source && source.sourceType === 'timepoint'){
		keys = TIME_CASTABLE_DIVINATION;
	}else if(source && source.sourceType === 'case'){
		keys = ANALYSIS_CASE_TECHNIQUES;
	}else{
		keys = ANALYSIS_CHART_TECHNIQUES;
	}
	return keys.map((key)=>({
		value: key,
		label: getTechniqueLabel(key),
	}));
}

export async function getAnalysisTechniqueContexts(source, techniqueKeys, options = {}){
	if(!source){
		return [];
	}
	const keys = Array.from(new Set((techniqueKeys || []).map((item)=>normalizeTechniqueKey(item)).filter(Boolean)));
	if(!keys.length){
		return [];
	}
	const baseSourceContext = options.sourceContext || null;
	const results = [];
	for(let i = 0; i < keys.length; i += 1){
		// eslint-disable-next-line no-await-in-loop
		const context = await buildTechniqueContext(source, keys[i], baseSourceContext);
		if(context){
			results.push(context);
		}
	}
	return results;
}

// 「起课时间」源的前提上下文：纯时间 + 地点的简短说明（技法快照各自携带正文）。
function buildTimepointContext(source){
	const record = source && source.record ? source.record : {};
	const lines = ['起课时间盘（按所选时间 + 默认设置即时起盘）'];
	if(record.divTime){ lines.push(`起课时间：${record.divTime}`); }
	if(record.zone){ lines.push(`时区：${record.zone}`); }
	if(record.lon || record.lat){ lines.push(`地点：经 ${record.lon || '—'} / 纬 ${record.lat || '—'}`); }
	return {
		content: lines.join('\n').trim(),
		title: source.title,
		module: 'timepoint',
		meta: buildSnapshotMetaFromRecord(record, { sourceType: 'timepoint', sourceId: source.id }),
	};
}

export async function getAnalysisSourceContext(source, options = {}){
	if(!source){
		return null;
	}
	const mode = options.mode === 'meta' ? 'meta' : 'full';
	const cacheId = `${source.sourceType}:${source.id}:${mode}`;
	const preferCache = options.preferCache !== false;
	const shouldPreferCache = preferCache
		&& source.sourceType !== 'timepoint'
		&& !(source.sourceType === 'case' && source.snapshotStatus !== 'ready');
	if(shouldPreferCache){
		const cached = await getStoreRecord(AI_ANALYSIS_STORES.contextCache, cacheId);
		if(cached && cached.sourceUpdatedAt === source.updatedAt && cached.content){
			return cached;
		}
	}
	let built;
	if(source.sourceType === 'timepoint'){
		built = buildTimepointContext(source);
	}else if(mode === 'meta'){
		built = source.sourceType === 'chart' ? buildChartMetaContext(source) : buildCaseMetaContext(source);
	}else{
		built = source.sourceType === 'chart' ? await buildChartContext(source) : await buildCaseContext(source);
	}
	const next = {
		id: cacheId,
		sourceId: source.id,
		sourceType: source.sourceType,
		title: source.title,
		module: built.module,
		content: built.content,
		meta: built.meta || {},
		sourceUpdatedAt: source.updatedAt || '',
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	};
	await putStoreRecord(AI_ANALYSIS_STORES.contextCache, next, 'ctx');
	return next;
}

export function estimateTextTokens(text){
	const raw = `${text || ''}`.trim();
	return Math.ceil(raw.length / 4);
}

export function buildContextLayers({
	sourceContext,
	techniqueContexts,
	materials,
	bundles,
	templates,
	retrievedChunks,
	conversationMessages,
	systemPrompt,
}) {
	const layers = [];
	layers.push({
		key: 'system',
		title: '系统提示',
		priority: 100,
		content: systemPrompt || '你是星阙的 AI 分析助手。请严格依据当前案例上下文、参考资料与回复模版作答。',
	});
	if(sourceContext && sourceContext.content){
		layers.push({
			key: 'source',
			title: `案例前提：${sourceContext.title || ''}`,
			priority: 95,
			content: sourceContext.content,
		});
	}
	// v2.2.1:把「日界点·晚子时」排盘规则作为 first-class 上下文稳定挂载,
	// 让 AI 知道四柱按哪种换日/起时干规则计算,不会误读 23:00–23:59 的日柱/时柱。
	// 优先用案例自带的开关值(命盘 fields / 事盘 payload),否则回退全局设置。
	{
		const a23 = sourceContext && sourceContext.after23NewDay !== undefined
			? sourceContext.after23NewDay : defaultAfter23NewDay();
		const lzh = sourceContext && sourceContext.lateZiHourUseNextDay !== undefined
			? sourceContext.lateZiHourUseNextDay : defaultLateZiHourUseNextDay();
		const meta = buildDayBoundaryMeta(a23, lzh);
		layers.push({
			key: 'dayBoundaryRule',
			title: '排盘规则（日界点·晚子时）',
			priority: 94,
			content: meta.note,
		});
	}
	(techniqueContexts || []).forEach((item, idx)=>{
		if(!item || !item.content){
			return;
		}
		if(sourceContext && sourceContext.content && item.content === sourceContext.content){
			return;
		}
		layers.push({
			key: `technique:${item.key || idx}`,
			title: `使用技法：${item.title || item.key || `技法 ${idx + 1}`}`,
			priority: 93 - idx,
			content: item.content,
		});
	});
	(bundles || []).forEach((bundle)=>{
		if(bundle.defaultSystemPrompt){
			layers.push({
				key: `bundle-system:${bundle.id}`,
				title: `组合系统提示：${bundle.name || ''}`,
				priority: 92,
				content: bundle.defaultSystemPrompt,
			});
		}
	});
	(templates || []).forEach((template)=>{
		const text = template && template.format === 'json'
			? [template.instructionText, template.jsonSchema && `JSON Schema：\n${template.jsonSchema}`].filter(Boolean).join('\n\n')
			: (template && (template.instructionText || template.content));
		if(text){
			layers.push({
				key: `template:${template.id}`,
				title: `模版约束：${template.name || ''}`,
				priority: 90,
				content: text,
			});
		}
	});
	const directMaterials = (materials || []).filter((item)=>!item.retrievedOnly);
	directMaterials.forEach((item, idx)=>{
		if(item.extractedText){
			layers.push({
				key: `material:${item.id}`,
				title: `参考资料 ${idx + 1}：${item.name || '未命名资料'}`,
				priority: 70,
				content: item.extractedText,
			});
		}
	});
	if(Array.isArray(retrievedChunks) && retrievedChunks.length){
		const retrievedText = buildRetrievedContextText(retrievedChunks);
		if(retrievedText){
			layers.push({
				key: 'retrieved-context',
				title: '检索资料片段',
				priority: 80,
				content: retrievedText,
			});
		}
	}
	const visibleHistory = (conversationMessages || []).filter((item)=>item && item.role !== 'system_hidden').slice(-10);
	if(visibleHistory.length){
		layers.push({
			key: 'recent-history',
			title: '最近对话',
			priority: 60,
			content: visibleHistory.map((item)=>`[${item.role}] ${item.content || ''}`).join('\n\n'),
		});
	}
	return layers.map((item)=>({
		...item,
		tokenEstimate: estimateTextTokens(item.content),
	}));
}

export function clipContextLayers(layers, options = {}){
	const maxChars = options.maxChars || DEFAULT_CONTEXT_CHAR_LIMIT;
	const sorted = (layers || []).slice(0).sort((a, b)=>b.priority - a.priority);
	const kept = [];
	let totalChars = 0;
	sorted.forEach((item)=>{
		const content = `${item.content || ''}`.trim();
		if(!content){
			return;
		}
		const nextChars = totalChars + content.length;
		if(nextChars <= maxChars){
			kept.push({
				...item,
				content,
				clipped: false,
			});
			totalChars = nextChars;
			return;
		}
		if(kept.length === 0 || item.priority >= 90){
			const remain = Math.max(0, maxChars - totalChars);
			if(remain > 120){
				kept.push({
					...item,
					content: `${content.slice(0, remain)}\n...[已裁剪]`,
					clipped: true,
				});
				totalChars = maxChars;
			}
		}
	});
	return kept;
}

export function buildPromptContext({
	sourceContext,
	techniqueContexts,
	materials,
	bundles,
	templates,
	retrievedChunks,
	conversationMessages,
	systemPrompt,
	maxChars,
}) {
	const layers = buildContextLayers({
		sourceContext,
		techniqueContexts,
		materials,
		bundles,
		templates,
		retrievedChunks,
		conversationMessages,
		systemPrompt,
	});
	const clippedLayers = clipContextLayers(layers, { maxChars });
	return clippedLayers.map((item)=>`${item.title}\n${item.content}`).join('\n\n').trim();
}
