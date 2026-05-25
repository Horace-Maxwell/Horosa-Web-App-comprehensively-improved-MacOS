import DateTime from '../components/comp/DateTime';
import request from './request';
import * as Constants from './constants';
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
import { buildGuolaoSnapshotForFields } from '../components/guolao/GuoLaoChartMain';
import { buildSuzhanSnapshotText } from '../components/suzhan/SuZhanMain';
import { buildGermanySnapshotForFields } from '../components/germany/AstroMidpoint';

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
	after23NewDay: 0,
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
	profection: '星运-小限法',
	solararc: '星运-太阳弧',
	solarreturn: '星运-太阳返照',
	lunarreturn: '星运-月亮返照',
	givenyear: '星运-流年法',
	decennials: '星运-十年大运',
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
};

export const ANALYSIS_CHART_TECHNIQUES = [
	'astrochart',
	'astrochart_like',
	'indiachart',
	'relative',
	'guolao',
	'germany',
	'jieqi',
	'jieqi_meta',
	'jieqi_chunfen',
	'jieqi_xiazhi',
	'jieqi_qiufen',
	'jieqi_dongzhi',
	'primarydirect',
	'primarydirchart',
	'zodialrelease',
	'firdaria',
	'profection',
	'solararc',
	'solarreturn',
	'lunarreturn',
	'givenyear',
	'decennials',
	'cntradition',
	'bazi',
	'ziwei',
	'suzhan',
	'otherbu',
	'fengshui',
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
];

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
		after23NewDay: { value: 0 },
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
		after23NewDay: { value: record && record.after23NewDay !== undefined ? record.after23NewDay : 0 },
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
			record.gender !== undefined && record.gender !== null ? record.gender : 1
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
	};
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
		case 'primarydirect': {
			// 主限法：取含主限法的西洋盘（默认 Alchabitius 弧 / Ptolemy 时钥 / 显示界限）。
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
	const fromCache = getTechniqueSnapshotFromCache(extracted.moduleName, source);
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
	if(fromCache && fromCache.content){
		return {
			content: fromCache.content,
			title: source.title,
			module: extracted.moduleName,
			meta: {
				sourceType: 'case',
				sourceId: source.id,
				caseType: record.caseType,
				divTime: record.divTime,
				...(fromCache.meta || {}),
			},
		};
	}
	// Part F：事盘只从自身 payload 重建文本（用起盘结果，不碰时间），不按时间重新起盘。
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
			compatible: isSnapshotMetaCompatible(snapshot.meta, source),
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
	if(source.sourceType === 'case'){
		// Part F：事盘只认自身起盘那一刻保存的卦/课，绝不按时间重算，也不读全局模块缓存
		// （那是「上次看过的某一卦」）。勾选的技法若不在本案例 payload 中则显示缺失。
		if(!(fromPayload && fromPayload.content)){
			const generatedText = generateCaseTechniqueSnapshot(record, key, payload);
			if(generatedText){
				saveGeneratedTechniqueSnapshot(key, generatedText, record, {
					generatedFromStoredCase: true,
				});
				generated = {
					content: generatedText,
					createdAt: new Date().toISOString(),
					meta: buildSnapshotMetaFromRecord(record, {
						generatedFromStoredCase: true,
					}),
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
	const keys = source && source.sourceType === 'case'
		? ANALYSIS_CASE_TECHNIQUES
		: ANALYSIS_CHART_TECHNIQUES;
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

export async function getAnalysisSourceContext(source, options = {}){
	if(!source){
		return null;
	}
	const mode = options.mode === 'meta' ? 'meta' : 'full';
	const cacheId = `${source.sourceType}:${source.id}:${mode}`;
	const preferCache = options.preferCache !== false;
	const shouldPreferCache = preferCache && !(source.sourceType === 'case' && source.snapshotStatus !== 'ready');
	if(shouldPreferCache){
		const cached = await getStoreRecord(AI_ANALYSIS_STORES.contextCache, cacheId);
		if(cached && cached.sourceUpdatedAt === source.updatedAt && cached.content){
			return cached;
		}
	}
	const built = mode === 'meta'
		? (source.sourceType === 'chart' ? buildChartMetaContext(source) : buildCaseMetaContext(source))
		: (source.sourceType === 'chart' ? await buildChartContext(source) : await buildCaseContext(source));
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
