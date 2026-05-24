import { Component } from 'react';
import { Input, InputNumber, Modal, Spin } from 'antd';
import DateTime from '../comp/DateTime';
import SpaceTimePanel, { buildDateTimeFromFields, formatSpaceTime } from '../comp/SpaceTimePanel';
import XQIcon from '../xq-icons';
import { XQButton as Button, XQSelect as Select, XQTabs as Tabs } from '../xq-ui';
import ZiWeiChart from '../ziwei/ZiWeiChart';
import { saveModuleAISnapshot } from '../../utils/moduleAiSnapshot';
import { ServerRoot, ResultKey } from '../../utils/constants';
import { buildKentangEndpoint } from '../../integrations/kentang/serviceRoot';
import { formatHumanValue } from '../../utils/humanReadableFields';

const { TabPane } = Tabs;
const { Option } = Select;

const TECHNIQUE_CONFIG = {
	shaozi: {
		pageTitle: '数算',
		infoTitle: '数算信息',
		infoSubTitle: '邵子、铁板、鬼谷与条文',
		serviceKey: 'shaozi',
		moduleKey: 'shusuan',
		techniqueLabel: '邵子神数',
		showRail: true,
		tabs: [
			{ key: 'overview', label: '概览' },
			{ key: 'pillars', label: '四柱' },
			{ key: 'digits', label: '起数' },
			{ key: 'text', label: '条文' },
		],
	},
	tieban: {
		pageTitle: '数算',
		infoTitle: '数算信息',
		infoSubTitle: '铁板神数、扣入法与算盘打数',
		serviceKey: 'tieban',
		moduleKey: 'shusuan',
		techniqueLabel: '铁板神数',
		showRail: true,
		tabs: [
			{ key: 'overview', label: '概览' },
			{ key: 'pillars', label: '四柱' },
			{ key: 'core', label: '核心' },
			{ key: 'palaces', label: '宫位' },
			{ key: 'verses', label: '条文' },
			{ key: 'dayun', label: '大运' },
		],
	},
	fendjing: {
		pageTitle: '数算',
		infoTitle: '数算信息',
		infoSubTitle: '鬼谷分定经、两头钳与古文断语',
		serviceKey: 'fendjing',
		moduleKey: 'shusuan',
		techniqueLabel: '鬼谷分定经',
		showRail: true,
		tabs: [
			{ key: 'overview', label: '概览' },
			{ key: 'pillars', label: '四柱' },
			{ key: 'twoGan', label: '两头钳' },
			{ key: 'fate', label: '命格' },
			{ key: 'verses', label: '断语' },
		],
	},
	beiji: {
		pageTitle: '数算',
		infoTitle: '数算信息',
		infoSubTitle: '北极神数、刻分与条文',
		serviceKey: 'beiji',
		moduleKey: 'shusuan',
		techniqueLabel: '北极神数',
		showRail: true,
		tabs: [
			{ key: 'overview', label: '概览' },
			{ key: 'yearHour', label: '年时' },
			{ key: 'queries', label: '条文' },
			{ key: 'search', label: '检索' },
			{ key: 'family', label: '家亲' },
			{ key: 'fortune', label: '财官' },
			{ key: 'dayun', label: '大运' },
		],
	},
	nanji: {
		pageTitle: '数算',
		infoTitle: '数算信息',
		infoSubTitle: '南极神数、宫部与条文',
		serviceKey: 'nanji',
		moduleKey: 'shusuan',
		techniqueLabel: '南极神数',
		showRail: true,
		tabs: [
			{ key: 'overview', label: '概览' },
			{ key: 'pillars', label: '四柱' },
			{ key: 'palaceText', label: '宫部' },
			{ key: 'queryText', label: '查询' },
			{ key: 'dayun', label: '大运' },
			{ key: 'password', label: '密码' },
			{ key: 'divine', label: '星图' },
		],
	},
	chunzi: {
		pageTitle: '数算',
		infoTitle: '数算信息',
		infoSubTitle: '蠢子数、宿度与诗词候选',
		serviceKey: 'chunzi',
		moduleKey: 'shusuan',
		techniqueLabel: '蠢子数',
		showRail: true,
		tabs: [
			{ key: 'overview', label: '概览' },
			{ key: 'pillars', label: '四柱' },
			{ key: 'codes', label: '代码' },
			{ key: 'analysis', label: '解析' },
			{ key: 'candidates', label: '候选' },
			{ key: 'lookup', label: '查询' },
			{ key: 'search', label: '检索' },
		],
	},
	xianqin: {
		pageTitle: '演禽',
		infoTitle: '演禽信息',
		infoSubTitle: '三宫、星禽与吞啖',
		serviceKey: 'xianqin',
		moduleKey: 'yanqin',
		techniqueLabel: '万化仙禽',
		showRail: false,
		tabs: [
			{ key: 'overview', label: '概览' },
			{ key: 'palaces', label: '宫位' },
			{ key: 'stars', label: '星禽' },
			{ key: 'swallow', label: '吞啖' },
		],
	},
	cetian: {
		pageTitle: '其他',
		infoTitle: '其他信息',
		infoSubTitle: '策天飞星、四化与格局',
		serviceKey: 'cetian',
		moduleKey: 'mingother',
		techniqueLabel: '策天飞星',
		showRail: true,
		tabs: [
			{ key: 'overview', label: '概览' },
			{ key: 'palaces', label: '宫位' },
			{ key: 'flying', label: '飞星' },
			{ key: 'patterns', label: '格局' },
		],
	},
};

function parseFieldsDateTime(fields){
	if(!fields || !fields.date || !fields.time || !fields.date.value || !fields.time.value){
		return null;
	}
	const dateStr = fields.date.value.format('YYYY-MM-DD');
	const timeStr = fields.time.value.format('HH:mm:ss');
	const d = dateStr.split('-').map((item)=>parseInt(item, 10));
	const t = timeStr.split(':').map((item)=>parseInt(item, 10));
	if(d.length < 3 || t.length < 2){
		return null;
	}
	return {
		year: d[0],
		month: d[1],
		day: d[2],
		hour: t[0],
		minute: t[1],
		second: t[2] || 0,
		date: dateStr,
		time: timeStr,
		zone: fields.zone && fields.zone.value ? fields.zone.value : '',
		lat: fields.lat && fields.lat.value ? fields.lat.value : '',
		lon: fields.lon && fields.lon.value ? fields.lon.value : '',
		gender: fields.gender && fields.gender.value !== undefined ? fields.gender.value : 1,
	};
}

async function postKinAstro(serviceKey, payload){
	let rsp = null;
	try{
		const rawResponse = await fetch(buildKentangEndpoint(serviceKey, 'pan'), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json; charset=UTF-8' },
			body: JSON.stringify(payload),
		});
		const rawText = await rawResponse.text();
		rsp = rawText ? JSON.parse(rawText) : null;
		if(!rsp || (rsp.ResultCode !== undefined && rsp.ResultCode !== 0)){
			throw new Error(rsp && rsp[ResultKey] ? `${rsp[ResultKey]}` : 'kinastro.local.fetch.failed');
		}
	}catch(e){
		const rawResponse = await fetch(`${ServerRoot}/${serviceKey}/pan`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json; charset=UTF-8' },
			body: JSON.stringify(payload),
		});
		const rawText = await rawResponse.text();
		rsp = rawText ? JSON.parse(rawText) : null;
	}
	if(!rsp || (rsp.ResultCode !== undefined && rsp.ResultCode !== 0)){
		throw new Error(rsp && rsp[ResultKey] ? `${rsp[ResultKey]}` : 'kinastro.fetch.failed');
	}
	return rsp && rsp[ResultKey] ? rsp[ResultKey] : rsp;
}

function fmtValue(value){
	return formatHumanValue(value);
}

function textValue(value){
	if(value === undefined || value === null || value === ''){
		return '—';
	}
	if(typeof value === 'object'){
		return fmtValue(value.text || value.verse || value.content || value.raw_key || value);
	}
	return fmtValue(value);
}

function buildSnapshotText(pan){
	if(!pan){
		return '暂无 kinastro 数据';
	}
	if(pan.snapshot){
		return pan.snapshot;
	}
	const lines = [];
	(pan.sections || []).forEach((section)=>{
		lines.push(`[${section.title}]`);
		(section.rows || []).forEach((row)=>{
			lines.push(`${row.label}：${fmtValue(row.value)}`);
		});
		lines.push('');
	});
	return lines.join('\n').trim();
}

function kinAstroSnapshotKey(serviceKey){
	return `kinastro-${serviceKey || 'unknown'}`;
}

function setRuntimeKinAstroTechnique(moduleKey, serviceKey){
	try{
		if(typeof window === 'undefined'){
			return;
		}
		if(!window.__horosaKinAstroCurrent || typeof window.__horosaKinAstroCurrent !== 'object'){
			window.__horosaKinAstroCurrent = {};
		}
		if(moduleKey){
			window.__horosaKinAstroCurrent[moduleKey] = serviceKey;
		}
		window.__horosaKinAstroCurrent.technique = serviceKey;
		window.__horosaKinAstroTechnique = serviceKey;
	}catch(e){
		// runtime hint only
	}
}

function saveKinAstroAISnapshots(config, pan){
	if(!config || !pan){
		return;
	}
	const content = buildSnapshotText(pan);
	const meta = {
		source: 'kentang2017/kinastro',
		serviceKey: config.serviceKey,
		technique: config.techniqueLabel,
		moduleKey: config.moduleKey,
		sections: (pan.sections || []).map((section)=>section.title).filter(Boolean),
	};
	saveModuleAISnapshot(kinAstroSnapshotKey(config.serviceKey), content, meta);
	saveModuleAISnapshot(config.moduleKey, content, meta);
}

function sectionByTitle(sections, names){
	const wanted = new Set(names);
	return (sections || []).filter((section)=>wanted.has(section.title));
}

const BRANCH_INDEX = {
	子: 0, 丑: 1, 寅: 2, 卯: 3, 辰: 4, 巳: 5,
	午: 6, 未: 7, 申: 8, 酉: 9, 戌: 10, 亥: 11,
};

const TWELVE_PALACE_LAYOUT = [
	{ row: 1, col: 1, branch: 5 }, { row: 1, col: 2, branch: 6 }, { row: 1, col: 3, branch: 7 }, { row: 1, col: 4, branch: 8 },
	{ row: 2, col: 1, branch: 4 }, { row: 2, col: 4, branch: 9 },
	{ row: 3, col: 1, branch: 3 }, { row: 3, col: 4, branch: 10 },
	{ row: 4, col: 1, branch: 2 }, { row: 4, col: 2, branch: 1 }, { row: 4, col: 3, branch: 0 }, { row: 4, col: 4, branch: 11 },
];

const BRANCH_NAMES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
const STEM_NAMES = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
const SIHUA_KEYS = ['禄', '权', '科', '忌'];
const BEIJI_KE_OPTIONS = [
	{ value: '1', label: '初一刻' },
	{ value: '2', label: '初二刻' },
	{ value: '3', label: '初三刻' },
	{ value: '4', label: '初四刻' },
	{ value: '5', label: '正一刻' },
	{ value: '6', label: '正二刻' },
	{ value: '7', label: '正三刻' },
	{ value: '8', label: '正四刻' },
];
const NANJI_SECTION_OPTIONS = BRANCH_NAMES.map((item)=>({ value: `${item}部`, label: `${item}部` }));
const NANJI_JIANCHU_OPTIONS = [
	{ value: '建', label: '建' },
	{ value: '除', label: '除' },
	{ value: '滿', label: '满' },
	{ value: '平', label: '平' },
	{ value: '定', label: '定' },
	{ value: '執', label: '执' },
	{ value: '破', label: '破' },
	{ value: '危', label: '危' },
	{ value: '成', label: '成' },
	{ value: '收', label: '收' },
	{ value: '開', label: '开' },
	{ value: '閉', label: '闭' },
];
const NANJI_XIU_OPTIONS = [
	'角', '亢', '氏', '房', '心', '尾', '箕',
	'斗', '牛', '女', '虛', '危', '室', '壁',
	'奎', '婁', '胃', '昴', '畢', '觜', '參',
	'井', '鬼', '柳', '星', '張', '翼', '軫',
].map((item)=>({
	value: item,
	label: item.replace('虛', '虚').replace('婁', '娄').replace('畢', '毕').replace('參', '参').replace('張', '张').replace('軫', '轸'),
}));
const NANJI_PASSWORD_OPTIONS = [
	'海異山同', '山異海同', '將脫這際', '除柳', '蕉局', '財勝局',
	'原比', '花牌同乾', '跳重', '重肘', '則要荊茨', '天地局', '陰盛',
].map((item)=>({
	value: item,
	label: item
		.replace('異', '异')
		.replace('將脫這際', '将脱这际')
		.replace('財勝局', '财胜局')
		.replace('則要荊茨', '则要荆茨')
		.replace('陰盛', '阴盛'),
}));
const NANJI_CHART_OPTIONS = Array.from({ length: 18 }).map((_, index)=>({
	value: index + 1,
	label: `第${index + 1}图`,
}));
const CHUNZI_KE_OPTIONS = Array.from({ length: 10 }).map((_, index)=>({
	value: `${index + 1}`,
	label: `${index + 1}刻`,
}));
const CHUNZI_RESULT_LIMIT_OPTIONS = [10, 20, 30, 50].map((item)=>({
	value: `${item}`,
	label: `${item}条`,
}));
const CHUNZI_MANSION_OPTIONS = [
	'角', '亢', '氐', '房', '心', '尾', '箕',
	'斗', '牛', '女', '虛', '危', '室', '壁',
	'奎', '婁', '胃', '昴', '畢', '觜', '參',
	'井', '鬼', '柳', '星', '張', '翼', '軫',
].map((item)=>({
	value: item,
	label: item.replace('虛', '虚').replace('婁', '娄').replace('畢', '毕').replace('參', '参').replace('張', '张').replace('軫', '轸'),
}));
const HUA_NORMALIZE = {
	祿: '禄',
	權: '权',
	科: '科',
	忌: '忌',
};
const GANZHI_PATTERN = /^[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]$/;
const INTERNAL_SECTION_TITLES = new Set([
	'十二宫顺序',
	'三元起宿',
	'合宿表',
	'科名月宿',
	'四季得时',
	'情性赋全表',
	'二十八宿正像',
	'吞啖合战规则',
	'贵贱赋摘要',
	'星曜属性',
	'正曜副曜',
	'宫干四化表',
	'飞化规则',
	'古法格局规则',
	'三合组',
]);

function normalizeGanzhiInput(value){
	const text = `${value || ''}`.trim();
	return GANZHI_PATTERN.test(text) ? text : '';
}

function toStarList(value){
	if(!value){
		return [];
	}
	const list = value instanceof Array ? value : [value];
	return list.map((item)=>{
		const name = typeof item === 'object' ? (item.name || item.label || item.title || '') : item;
		return `${name || ''}`.trim();
	}).filter(Boolean).map((name)=>({ name }));
}

function normalizeHuaLabel(value){
	const text = `${value || ''}`.trim();
	return HUA_NORMALIZE[text] || text;
}

function getCetianStarFlightTarget(starName, palace, cetian){
	const formatTarget = (target)=>{
		if(target === undefined || target === null || target === ''){
			return '';
		}
		let branchValue = target;
		if(typeof target === 'object'){
			branchValue = target.to_branch !== undefined && target.to_branch !== null ? target.to_branch
				: (target.branch !== undefined && target.branch !== null ? target.branch
					: (target.to_palace || target.palace || ''));
		}
		return BRANCH_NAMES[branchValue] || `${branchValue || ''}`.replace(/[宫宮]$/, '').slice(-1);
	};
	if(palace && palace.flying_stars && palace.flying_stars[starName]){
		return formatTarget(palace.flying_stars[starName]);
	}
	const flight = cetian && cetian.star_flight ? cetian.star_flight[starName] : null;
	if(!flight || flight.to_branch === undefined || flight.to_branch === null){
		return '';
	}
	return formatTarget(flight);
}

function toCetianStarList(value, sihua, palace = {}, cetian = {}){
	return toStarList(value).map((star)=>({
		...star,
		hua: normalizeHuaLabel((palace.sihua && palace.sihua[star.name]) || (sihua && sihua[star.name])),
		starlight: palace.brightness && palace.brightness[star.name] ? `${palace.brightness[star.name]}` : '',
		flyTo: getCetianStarFlightTarget(star.name, palace, cetian),
	}));
}

function toXianqinStarList(value){
	if(!value){
		return [];
	}
	const list = value instanceof Array ? value : [value];
	return list.map((item)=>{
		if(typeof item === 'object'){
			return {
				name: `${item.name || item.label || item.title || ''}`.trim(),
			};
		}
		const text = `${item || ''}`.trim();
		const parts = text.split(/[：:]/);
		if(parts.length >= 2){
			return {
				name: parts.slice(1).join('：').trim(),
			};
		}
		return { name: text };
	}).filter((item)=>item.name);
}

const XIANQIN_PALACE_STAR_MAP = [
	{ match: ['命'], label: '命星', source: 'ming_xing' },
	{ match: ['财帛', '財帛'], label: '财帛星', key: '財帛星' },
	{ match: ['兄弟'], label: '兄弟星', key: '兄弟星' },
	{ match: ['田宅'], label: '田宅星', key: '田宅星' },
	{ match: ['子女', '子息'], label: '子息星', key: '子息星' },
	{ match: ['奴仆', '奴僕'], label: '奴仆星', key: '奴僕星' },
	{ match: ['夫妻', '妻妾'], label: '妻妾星', key: '妻妾星' },
	{ match: ['疾厄'], label: '疾厄星', key: '疾厄星' },
	{ match: ['迁移', '遷移'], label: '迁移星', key: '遷移星' },
	{ match: ['官禄', '官祿'], label: '官禄星', key: '官祿星' },
	{ match: ['福德'], label: '福德星', key: '福德星' },
	{ match: ['相貌'], label: '相貌星', key: '相貌星' },
];

function normalizeXianqinPalaceName(value){
	return `${value || ''}`
		.replace(/[宫宮]/g, '')
		.replace(/財/g, '财')
		.replace(/僕/g, '仆')
		.replace(/遷/g, '迁')
		.replace(/祿/g, '禄')
		.replace(/妾/g, '妻');
}

function getXianqinPalaceStarEntry(chartData, palaceName){
	const stars = (chartData && chartData.stars) || {};
	const derived = stars.derived || {};
	const normalizedName = normalizeXianqinPalaceName(palaceName);
	const found = XIANQIN_PALACE_STAR_MAP.find((item)=>item.match.some((name)=>normalizedName.indexOf(normalizeXianqinPalaceName(name)) >= 0));
	if(!found){
		return '';
	}
	const qin = found.source ? stars[found.source] : (derived[found.key] || derived[normalizeXianqinPalaceName(found.key)]);
	return qin ? `${found.label}：${qin}` : '';
}

function getXianqinPalaceNameByBranch(chartData, branch){
	const twelve = ((chartData && chartData.palaces) || {}).twelve || {};
	const entry = Object.keys(twelve).find((key)=>twelve[key] === branch);
	return entry || '';
}

function emptyZiWeiHouse(branchIdx){
	const branch = BRANCH_NAMES[branchIdx] || '';
	return {
		name: branch,
		ganzi: `　${branch}`,
		starsMain: [],
		starsAssist: [],
		starsEvil: [],
		starsSmall: [],
		starsOthersGood: [],
		starsOthersBad: [],
		direction: [branchIdx * 10 + 1, branchIdx * 10 + 10],
		phase: '',
	};
}

function buildZiWeiRulesForChart(chart){
	const ruleHouses = {};
	const huaInHouse = {};
	SIHUA_KEYS.forEach((key)=>{
		huaInHouse[key] = {};
	});
	(chart.houses || []).forEach((house)=>{
		const name = house && house.name ? house.name : '';
		if(name){
			ruleHouses[name] = [];
			SIHUA_KEYS.forEach((key)=>{
				huaInHouse[key][name] = [];
			});
		}
	});
	return {
		ZWRules: {
			RuleHouses: ruleHouses,
			RuleStars: {},
			RuleSihua: { 禄: [], 权: [], 科: [], 忌: [] },
		},
		ZWRuleSihua: {
			HuaInHouse: huaInHouse,
		},
	};
}

function addPalaceMarker(house, marker){
	if(!house || !marker){
		return;
	}
	const exists = (house.starsAssist || []).some((star)=>star.name === marker);
	if(!exists){
		house.starsAssist = [{ name: marker }].concat(house.starsAssist || []);
	}
}

function buildKinAstroZiWeiChart(pan, serviceKey){
	const dateStr = pan && pan.dateStr ? pan.dateStr : '2026-01-01';
	const timeStr = pan && pan.timeStr ? pan.timeStr : '00:00:00';
	const chart = {
		kinastroBorrowed: true,
		birth: dateStr,
		zone: fmtValue(pan && pan.timezone),
		lon: fmtValue(pan && pan.longitude),
		lat: fmtValue(pan && pan.latitude),
		yearZi: '子',
		yearGan: '',
		yearPolar: 'Positive',
		gender: 'Male',
		wuxingJuText: serviceKey === 'cetian' ? fmtValue(pan && pan.wuXingJu) : '演禽盘',
		lifeMaster: serviceKey === 'cetian' ? fmtValue(pan && pan.mingGong) : '命星',
		bodyMaster: serviceKey === 'cetian' ? fmtValue(pan && pan.shenGong) : '身星',
		zidou: serviceKey === 'cetian' ? fmtValue(pan && pan.ziwei) : '—',
		doujun: serviceKey === 'cetian' ? fmtValue(pan && pan.hourBranch) : '—',
		nongli: {
			year: pan && pan.lunar && pan.lunar.text ? pan.lunar.text : dateStr,
			month: '',
			day: '',
			time: ` ${timeStr}`,
			birth: `${dateStr} ${timeStr}`,
			leap: false,
		},
		bazi: {
			bazi: {
				year: { ganzi: '—' },
				month: { ganzi: '—' },
				day: { ganzi: '—' },
				time: { ganzi: '—' },
			},
			direct: { direction: [] },
		},
		houses: BRANCH_NAMES.map((_, idx)=>emptyZiWeiHouse(idx)),
	};

	if(serviceKey === 'cetian'){
		const palaces = (pan.cetian && pan.cetian.palaces) || [];
		const cetian = pan.cetian || {};
		palaces.forEach((palace, idx)=>{
			const branchIdx = palace.branch;
			if(branchIdx === undefined || branchIdx === null || !chart.houses[branchIdx]){
				return;
			}
			const branch = palace.branch_name || BRANCH_NAMES[branchIdx] || '';
			const mainStars = toCetianStarList(palace.stars, cetian.sihua, palace, cetian);
			const assistStars = toCetianStarList(palace.aux_stars, cetian.sihua, palace, cetian);
			const stemBranch = `${palace.stem_name || ''}${branch}`;
			chart.houses[branchIdx] = {
				...emptyZiWeiHouse(branchIdx),
				name: `${palace.name || branch || ''}`.replace(/[宫宮]$/, '') || branch,
				ganzi: stemBranch || branch,
				starsMain: mainStars,
				starsAssist: assistStars,
				starsEvil: toStarList(palace.patterns),
				direction: [idx * 10 + 1, idx * 10 + 10],
			};
		});
		if(chart.houses[cetian.shen_gong_branch]){
			chart.houses[cetian.shen_gong_branch].kinastroCornerMark = '身';
			chart.houses[cetian.shen_gong_branch].isBody = true;
		}
		return chart;
	}

	if(serviceKey === 'xianqin'){
		const palaces = {};
		(pan.palaceCards || []).forEach((card)=>{
			const branchIdx = BRANCH_INDEX[card.branch];
			if(branchIdx !== undefined){
				palaces[branchIdx] = card;
			}
		});
		const chartData = pan.xianqin || {};
		BRANCH_NAMES.forEach((branch, idx)=>{
			const palace = palaces[idx] || {};
			const palaceName = palace.name || getXianqinPalaceNameByBranch(chartData, branch) || branch;
			const stars = (palace.stars && palace.stars.length)
				? palace.stars
				: [getXianqinPalaceStarEntry(chartData, palaceName)].filter(Boolean);
			chart.houses[idx] = {
				...emptyZiWeiHouse(idx),
				name: `${palaceName || branch || ''}`.replace(/[宫宮]$/, '') || branch,
				ganzi: `　${branch}`,
				starsMain: toXianqinStarList(stars.slice ? stars.slice(0, 1) : stars),
				starsAssist: toXianqinStarList(stars.slice ? stars.slice(1) : []),
				starsEvil: [],
				direction: [idx * 10 + 1, idx * 10 + 10],
			};
		});
		const stars = chartData.stars || {};
		const xianqinPalaces = chartData.palaces || {};
		[
			{ palace: xianqinPalaces.tai_gong, marker: '胎' },
			{ palace: xianqinPalaces.shen_gong, marker: '身' },
		].forEach((item)=>{
			const branchIdx = BRANCH_INDEX[item.palace && item.palace.branch];
			if(chart.houses[branchIdx]){
				chart.houses[branchIdx].kinastroCornerMark = item.marker;
			}
		});
		chart.lifeMaster = fmtValue(stars.ming_xing);
		chart.bodyMaster = fmtValue(stars.shen_xing);
		chart.zidou = fmtValue(stars.tai_xing);
		chart.doujun = fmtValue((chartData.basic_info || {}).san_yuan);
		return chart;
	}

	return chart;
}

class KinAstroMain extends Component{
	constructor(props){
		super(props);
		const technique = props.technique || 'shaozi';
		this.config = TECHNIQUE_CONFIG[technique] || TECHNIQUE_CONFIG.shaozi;
		this.state = {
			loading: false,
			pan: null,
			rightPanelTab: 'overview',
			centerInfoVisible: false,
			gender: '1',
			ke: '初刻',
			useKey: '1',
			pillarOverride: '0',
			yearGz: '',
			monthGz: '',
			dayGz: '',
			hourGz: '',
			calendarMode: 'autoLunar',
			lunarYear: 2026,
			lunarMonth: 1,
			lunarDay: 1,
			tiebanMethod: 'kunji',
			tiebanStartAge: 0,
			tiebanDayunSteps: 8,
			fatherBirthYear: null,
			fatherDeathYear: null,
			motherBirthYear: null,
			motherDeathYear: null,
			siblingsInfo: '',
			maritalStatus: '',
			childrenInfo: '',
				fendjingStemOverride: '0',
				fendjingYearStem: '甲',
				fendjingHourStem: '甲',
				beijiKeMode: 'auto',
				beijiKe: '1',
				beijiLookupCode: '',
				beijiKeyword: '',
				nanjiMode: 'solar',
				nanjiAfterLichun: '1',
				nanjiLunarYear: 2026,
				nanjiSolarMonth: 1,
				nanjiDay: 1,
				nanjiHourZhi: '子',
				nanjiDayGan: '',
				nanjiDayZhi: '',
				nanjiSection: '子部',
				nanjiJianchu: '建',
				nanjiXiu: '張',
				nanjiPasswordCode: '海異山同',
				nanjiChart: 1,
				nanjiPalace: '子',
				nanjiDegree: 1,
				chunziKeMode: 'auto',
				chunziKe: '3',
				chunziLunarMode: 'auto',
				chunziLunarMonth: 1,
				chunziLunarDay: 1,
				chunziLookupCode: '',
				chunziKeyword: '',
				chunziTags: '',
				chunziMansion: '室',
				chunziHourBranch: '子',
				chunziResultLimit: '20',
			};
		this.unmounted = false;
		this.timeHook = {};
		this.requestSeq = 0;
		this.onTimeChanged = this.onTimeChanged.bind(this);
		this.clickPlot = this.clickPlot.bind(this);
		this.fetchPan = this.fetchPan.bind(this);
		this.setRightPanelTab = this.setRightPanelTab.bind(this);
		this.openCenterInfo = this.openCenterInfo.bind(this);
		this.closeCenterInfo = this.closeCenterInfo.bind(this);
		if(this.props.hook){
			this.props.hook.fun = (fields)=>{
				if(this.unmounted){
					return;
				}
				this.fetchPan(fields || this.props.fields);
			};
		}
	}

	componentDidMount(){
		this.unmounted = false;
		setRuntimeKinAstroTechnique(this.config.moduleKey, this.config.serviceKey);
		const dt = parseFieldsDateTime(this.props.fields);
		const nextState = {};
		if(dt){
			nextState.gender = `${dt.gender}`;
			nextState.lunarYear = dt.year;
			nextState.lunarMonth = dt.month;
			nextState.lunarDay = Math.min(30, dt.day);
			nextState.nanjiLunarYear = dt.year;
			nextState.nanjiSolarMonth = dt.month;
			nextState.nanjiDay = Math.min(31, dt.day);
			nextState.chunziLunarMonth = dt.month;
			nextState.chunziLunarDay = Math.min(30, dt.day);
		}
		this.setState(nextState, ()=>this.fetchPan(this.props.fields));
	}

	componentDidUpdate(prevProps, prevState){
		if(prevProps.technique !== this.props.technique){
			this.config = TECHNIQUE_CONFIG[this.props.technique || 'shaozi'] || TECHNIQUE_CONFIG.shaozi;
			setRuntimeKinAstroTechnique(this.config.moduleKey, this.config.serviceKey);
			this.requestSeq += 1;
			this.setState({
				pan: null,
				rightPanelTab: 'overview',
				centerInfoVisible: false,
				loading: false,
			}, ()=>this.fetchPan(this.props.fields));
			return;
		}
		setRuntimeKinAstroTechnique(this.config.moduleKey, this.config.serviceKey);
		if(prevProps.fields !== this.props.fields && this.props.fields){
			this.fetchPan(this.props.fields);
		}
		const optionKeys = [
			'gender', 'ke', 'useKey', 'pillarOverride', 'yearGz', 'monthGz', 'dayGz', 'hourGz',
			'calendarMode', 'lunarYear', 'lunarMonth', 'lunarDay',
			'tiebanMethod', 'tiebanStartAge', 'tiebanDayunSteps',
			'fatherBirthYear', 'fatherDeathYear', 'motherBirthYear', 'motherDeathYear',
				'siblingsInfo', 'maritalStatus', 'childrenInfo',
				'fendjingStemOverride', 'fendjingYearStem', 'fendjingHourStem',
				'beijiKeMode', 'beijiKe', 'beijiLookupCode', 'beijiKeyword',
				'nanjiMode', 'nanjiAfterLichun', 'nanjiLunarYear', 'nanjiSolarMonth', 'nanjiDay',
				'nanjiHourZhi', 'nanjiDayGan', 'nanjiDayZhi', 'nanjiSection', 'nanjiJianchu',
				'nanjiXiu', 'nanjiPasswordCode', 'nanjiChart', 'nanjiPalace', 'nanjiDegree',
				'chunziKeMode', 'chunziKe', 'chunziLunarMode', 'chunziLunarMonth', 'chunziLunarDay',
				'chunziLookupCode', 'chunziKeyword', 'chunziTags', 'chunziMansion', 'chunziHourBranch',
				'chunziResultLimit',
			];
		if(optionKeys.some((key)=>prevState[key] !== this.state[key])){
			this.fetchPan(this.props.fields);
		}
	}

	componentWillUnmount(){
		this.unmounted = true;
	}

	onFieldsChange(field){
		if(this.props.dispatch){
			const flds = { ...(this.props.fields || {}), ...field };
			this.props.dispatch({ type: 'astro/fetchByFields', payload: flds });
		}
	}

	onTimeChanged(value){
		const dt = value.time;
		this.onFieldsChange({
			date: { value: dt.clone() },
			time: { value: dt.clone() },
			ad: { value: dt.ad },
			zone: { value: dt.zone },
		});
	}

	getTimeFieldsFromSelector(baseFields){
		if(!this.timeHook || !this.timeHook.getValue){
			return null;
		}
		const raw = this.timeHook.getValue();
		const dt = raw && raw.value && raw.value instanceof DateTime
			? raw.value
			: (raw && raw.time && raw.time instanceof DateTime ? raw.time : null);
		if(!dt){
			return null;
		}
		const patch = {
			date: { value: dt.clone() },
			time: { value: dt.clone() },
			ad: { value: dt.ad },
			zone: { value: dt.zone },
		};
		return { ...(baseFields || {}), ...patch };
	}

	clickPlot(){
		const nextFields = this.getTimeFieldsFromSelector(this.props.fields) || this.props.fields;
		if(nextFields && nextFields.date && nextFields.time && nextFields.zone){
			this.onFieldsChange({
				date: nextFields.date,
				time: nextFields.time,
				ad: nextFields.ad,
				zone: nextFields.zone,
			});
		}
		this.fetchPan(nextFields);
	}

	buildPayload(fields){
		const dt = parseFieldsDateTime(fields);
		if(!dt){
			return null;
		}
		const payload = {
			...dt,
			gender: this.state.gender,
			ke: this.state.ke,
			useKey: this.state.useKey === '1',
			method: this.state.tiebanMethod,
			startAge: this.state.tiebanStartAge,
			dayunSteps: this.state.tiebanDayunSteps,
			fatherBirthYear: this.state.fatherBirthYear,
			fatherDeathYear: this.state.fatherDeathYear,
			motherBirthYear: this.state.motherBirthYear,
			motherDeathYear: this.state.motherDeathYear,
			siblingsInfo: this.state.siblingsInfo,
			maritalStatus: this.state.maritalStatus,
			childrenInfo: this.state.childrenInfo,
			calendarMode: this.state.calendarMode,
			lunarYear: this.state.lunarYear,
			lunarMonth: this.state.lunarMonth,
			lunarDay: this.state.lunarDay,
				stemOverride: this.state.fendjingStemOverride === '1',
				yearStem: this.state.fendjingYearStem,
				hourStem: this.state.fendjingHourStem,
				keMode: this.state.beijiKeMode,
				beijiKeMode: this.state.beijiKeMode,
				beijiKe: this.state.beijiKe,
				beijiLookupCode: this.state.beijiLookupCode,
				beijiKeyword: this.state.beijiKeyword,
				useKe: this.state.beijiKeMode === 'manual',
				nanjiMode: this.state.nanjiMode,
				nanjiAfterLichun: this.state.nanjiAfterLichun,
				nanjiLunarYear: this.state.nanjiLunarYear,
				nanjiSolarMonth: this.state.nanjiSolarMonth,
				nanjiDay: this.state.nanjiDay,
				nanjiHourZhi: this.state.nanjiHourZhi,
				nanjiDayGan: this.state.nanjiDayGan,
				nanjiDayZhi: this.state.nanjiDayZhi,
				nanjiSection: this.state.nanjiSection,
				nanjiJianchu: this.state.nanjiJianchu,
				nanjiXiu: this.state.nanjiXiu,
				nanjiPasswordCode: this.state.nanjiPasswordCode,
				nanjiChart: this.state.nanjiChart,
				nanjiPalace: this.state.nanjiPalace,
				nanjiDegree: this.state.nanjiDegree,
				chunziKeMode: this.state.chunziKeMode,
				chunziKe: this.state.chunziKe,
				chunziLunarMode: this.state.chunziLunarMode,
				chunziLunarMonth: this.state.chunziLunarMonth,
				chunziLunarDay: this.state.chunziLunarDay,
				chunziLookupCode: this.state.chunziLookupCode,
				chunziKeyword: this.state.chunziKeyword,
				chunziTags: this.state.chunziTags,
				chunziMansion: this.state.chunziMansion,
				chunziHourBranch: this.state.chunziHourBranch,
				chunziResultLimit: this.state.chunziResultLimit,
			};
		if(this.state.pillarOverride === '1'){
			const yearGz = normalizeGanzhiInput(this.state.yearGz);
			const monthGz = normalizeGanzhiInput(this.state.monthGz);
			const dayGz = normalizeGanzhiInput(this.state.dayGz);
			const hourGz = normalizeGanzhiInput(this.state.hourGz);
			if(yearGz){
				payload.yearGz = yearGz;
			}
			if(monthGz){
				payload.monthGz = monthGz;
			}
			if(dayGz){
				payload.dayGz = dayGz;
			}
			if(hourGz){
				payload.hourGz = hourGz;
			}
		}
		return payload;
	}

	async fetchPan(fields){
		const payload = this.buildPayload(fields);
		if(!payload){
			return;
		}
		const reqSeq = ++this.requestSeq;
		this.setState({ loading: true });
		try{
			const pan = await postKinAstro(this.config.serviceKey, payload);
			if(this.unmounted || reqSeq !== this.requestSeq){
				return;
			}
			this.setState({ pan, loading: false }, ()=>{
				saveKinAstroAISnapshots(this.config, pan);
			});
		}catch(e){
			console.warn('kinastro backend failed', this.config.serviceKey, e);
			if(!this.unmounted && reqSeq === this.requestSeq){
				this.setState({ loading: false });
			}
		}
	}

	setRightPanelTab(key){
		this.setState({ rightPanelTab: key });
	}

	openCenterInfo(){
		this.setState({ centerInfoVisible: true });
	}

	closeCenterInfo(){
		this.setState({ centerInfoVisible: false });
	}

	renderPillarOverrideFields(){
		if(!['shaozi', 'tieban'].includes(this.config.serviceKey) || this.state.pillarOverride !== '1'){
			return null;
		}
		const fields = [
			{ key: 'yearGz', label: '年柱', placeholder: '甲子' },
			{ key: 'monthGz', label: '月柱', placeholder: '丙寅' },
			{ key: 'dayGz', label: '日柱', placeholder: '戊辰' },
			{ key: 'hourGz', label: '时柱', placeholder: '庚午' },
		];
		return fields.map((item)=>(
			<label className="horosa-huangji-select-field" key={item.key}>
				<span>{item.label}</span>
				<Input
					value={this.state[item.key]}
					placeholder={item.placeholder}
					maxLength={2}
					onChange={(event)=>this.setState({ [item.key]: event.target.value })}
				/>
			</label>
		));
	}

	renderInputPanel(){
		const fields = this.props.fields || {};
		const datetm = buildDateTimeFromFields(fields);
		return (
			<div className="horosa-huangji-input-stack horosa-kinastro-input-stack">
				<div>
					<div className="horosa-side-panel-title">{this.config.pageTitle}设置</div>
					<div className="horosa-side-panel-subtitle">时间、命盘与技法选项</div>
				</div>
				<SpaceTimePanel
					fields={fields}
					value={datetm}
					timeText={formatSpaceTime(fields, '---- -- -- --:--:--')}
					onTimeChange={this.onTimeChanged}
					timeHook={this.timeHook}
					showLocation={this.config.serviceKey === 'cetian'}
				/>
				<div className="horosa-huangji-input-section">
					<div className="horosa-huangji-field-title"><XQIcon name="quickPrimary" />{this.config.techniqueLabel}</div>
					<div className={`horosa-huangji-select-grid horosa-kinastro-select-grid horosa-kinastro-select-grid-${this.config.serviceKey}`}>
						{this.config.serviceKey !== 'xianqin' ? (
							<label className="horosa-huangji-select-field">
								<span>性别</span>
								<Select value={this.state.gender} onChange={(value)=>this.setState({ gender: value })}>
									<Option value="1">男</Option>
									<Option value="0">女</Option>
								</Select>
							</label>
						) : null}
						{this.config.serviceKey === 'shaozi' ? (
							<>
								<label className="horosa-huangji-select-field">
									<span>刻数</span>
									<Select value={this.state.ke} onChange={(value)=>this.setState({ ke: value })}>
										{['初刻', '二刻', '三刻', '四刻', '五刻', '六刻', '七刻', '八刻'].map((item)=><Option value={item} key={item}>{item}</Option>)}
									</Select>
								</label>
								<label className="horosa-huangji-select-field is-wide">
									<span>64钥匙细调</span>
									<Select value={this.state.useKey} onChange={(value)=>this.setState({ useKey: value })}>
										<Option value="1">启用</Option>
										<Option value="0">关闭</Option>
									</Select>
								</label>
								<label className="horosa-huangji-select-field is-wide">
									<span>四柱覆写</span>
									<Select value={this.state.pillarOverride} onChange={(value)=>this.setState({ pillarOverride: value })}>
										<Option value="0">自动换算</Option>
										<Option value="1">手动覆写</Option>
									</Select>
								</label>
								{this.renderPillarOverrideFields()}
							</>
						) : null}
						{this.config.serviceKey === 'tieban' ? (
							<>
								<label className="horosa-huangji-select-field">
									<span>算法</span>
									<Select value={this.state.tiebanMethod} onChange={(value)=>this.setState({ tiebanMethod: value })}>
										<Option value="kunji">扣入法</Option>
										<Option value="suanpan">算盘打数</Option>
									</Select>
								</label>
								<label className="horosa-huangji-select-field">
									<span>起运年龄</span>
									<InputNumber min={0} max={120} value={this.state.tiebanStartAge} onChange={(value)=>this.setState({ tiebanStartAge: value || 0 })} />
								</label>
								<label className="horosa-huangji-select-field">
									<span>大运步数</span>
									<InputNumber min={1} max={12} value={this.state.tiebanDayunSteps} onChange={(value)=>this.setState({ tiebanDayunSteps: value || 8 })} />
								</label>
								<label className="horosa-huangji-select-field is-wide">
									<span>四柱覆写</span>
									<Select value={this.state.pillarOverride} onChange={(value)=>this.setState({ pillarOverride: value })}>
										<Option value="0">自动换算</Option>
										<Option value="1">手动覆写</Option>
									</Select>
								</label>
								{this.renderPillarOverrideFields()}
								<label className="horosa-huangji-select-field">
									<span>父亲生年</span>
									<InputNumber min={1} max={9999} value={this.state.fatherBirthYear} onChange={(value)=>this.setState({ fatherBirthYear: value })} />
								</label>
								<label className="horosa-huangji-select-field">
									<span>父亲卒年</span>
									<InputNumber min={1} max={9999} value={this.state.fatherDeathYear} onChange={(value)=>this.setState({ fatherDeathYear: value })} />
								</label>
								<label className="horosa-huangji-select-field">
									<span>母亲生年</span>
									<InputNumber min={1} max={9999} value={this.state.motherBirthYear} onChange={(value)=>this.setState({ motherBirthYear: value })} />
								</label>
								<label className="horosa-huangji-select-field">
									<span>母亲卒年</span>
									<InputNumber min={1} max={9999} value={this.state.motherDeathYear} onChange={(value)=>this.setState({ motherDeathYear: value })} />
								</label>
								<label className="horosa-huangji-select-field is-wide">
									<span>兄弟信息</span>
									<Input value={this.state.siblingsInfo} placeholder="如：兄弟二人" onChange={(event)=>this.setState({ siblingsInfo: event.target.value })} />
								</label>
								<label className="horosa-huangji-select-field is-wide">
									<span>婚姻状况</span>
									<Input value={this.state.maritalStatus} placeholder="如：已婚" onChange={(event)=>this.setState({ maritalStatus: event.target.value })} />
								</label>
								<label className="horosa-huangji-select-field is-wide">
									<span>子女信息</span>
									<Input value={this.state.childrenInfo} placeholder="如：二子一女" onChange={(event)=>this.setState({ childrenInfo: event.target.value })} />
								</label>
							</>
						) : null}
							{this.config.serviceKey === 'fendjing' ? (
								<>
									<label className="horosa-huangji-select-field">
										<span>两头钳</span>
									<Select value={this.state.fendjingStemOverride} onChange={(value)=>this.setState({ fendjingStemOverride: value })}>
										<Option value="0">自动换算</Option>
										<Option value="1">手动指定</Option>
									</Select>
								</label>
								{this.state.fendjingStemOverride === '1' ? (
									<>
										<label className="horosa-huangji-select-field">
											<span>年干</span>
											<Select value={this.state.fendjingYearStem} onChange={(value)=>this.setState({ fendjingYearStem: value })}>
												{STEM_NAMES.map((item)=><Option value={item} key={item}>{item}</Option>)}
											</Select>
										</label>
										<label className="horosa-huangji-select-field">
											<span>时干</span>
											<Select value={this.state.fendjingHourStem} onChange={(value)=>this.setState({ fendjingHourStem: value })}>
												{STEM_NAMES.map((item)=><Option value={item} key={item}>{item}</Option>)}
											</Select>
										</label>
									</>
									) : null}
								</>
							) : null}
							{this.config.serviceKey === 'beiji' ? (
								<>
									<label className="horosa-huangji-select-field">
										<span>刻法</span>
										<Select value={this.state.beijiKeMode} onChange={(value)=>this.setState({ beijiKeMode: value })}>
											<Option value="auto">自动换算</Option>
											<Option value="manual">手动指定</Option>
										</Select>
									</label>
									{this.state.beijiKeMode === 'manual' ? (
										<label className="horosa-huangji-select-field">
											<span>刻</span>
											<Select value={this.state.beijiKe} onChange={(value)=>this.setState({ beijiKe: value })}>
												{BEIJI_KE_OPTIONS.map((item)=><Option value={item.value} key={item.value}>{item.label}</Option>)}
											</Select>
										</label>
									) : null}
									<label className="horosa-huangji-select-field is-wide">
										<span>条文码</span>
										<Input
											value={this.state.beijiLookupCode}
											maxLength={4}
											placeholder="如：1111"
											onChange={(event)=>this.setState({ beijiLookupCode: event.target.value.replace(/\D/g, '').slice(0, 4) })}
										/>
									</label>
									<label className="horosa-huangji-select-field is-wide">
										<span>关键词</span>
										<Input
											value={this.state.beijiKeyword}
											placeholder="如：属鼠、再婚"
											onChange={(event)=>this.setState({ beijiKeyword: event.target.value })}
										/>
									</label>
								</>
							) : null}
							{this.config.serviceKey === 'nanji' ? (
								<>
									<label className="horosa-huangji-select-field">
										<span>起盘方式</span>
										<Select value={this.state.nanjiMode} onChange={(value)=>this.setState({ nanjiMode: value })}>
											<Option value="solar">公历精算</Option>
											<Option value="manual">手动古法</Option>
										</Select>
									</label>
									<label className="horosa-huangji-select-field">
										<span>宫部</span>
										<Select value={this.state.nanjiSection} onChange={(value)=>this.setState({ nanjiSection: value })}>
											{NANJI_SECTION_OPTIONS.map((item)=><Option value={item.value} key={item.value}>{item.label}</Option>)}
										</Select>
									</label>
									<label className="horosa-huangji-select-field">
										<span>建除</span>
										<Select value={this.state.nanjiJianchu} onChange={(value)=>this.setState({ nanjiJianchu: value })}>
											{NANJI_JIANCHU_OPTIONS.map((item)=><Option value={item.value} key={item.value}>{item.label}</Option>)}
										</Select>
									</label>
									<label className="horosa-huangji-select-field">
										<span>二十八宿</span>
										<Select value={this.state.nanjiXiu} onChange={(value)=>this.setState({ nanjiXiu: value })}>
											{NANJI_XIU_OPTIONS.map((item)=><Option value={item.value} key={item.value}>{item.label}</Option>)}
										</Select>
									</label>
									<label className="horosa-huangji-select-field is-wide">
										<span>密码</span>
										<Select value={this.state.nanjiPasswordCode} onChange={(value)=>this.setState({ nanjiPasswordCode: value })}>
											{NANJI_PASSWORD_OPTIONS.map((item)=><Option value={item.value} key={item.value}>{item.label}</Option>)}
										</Select>
									</label>
									<label className="horosa-huangji-select-field">
										<span>星图</span>
										<Select value={this.state.nanjiChart} onChange={(value)=>this.setState({ nanjiChart: value })}>
											{NANJI_CHART_OPTIONS.map((item)=><Option value={item.value} key={item.value}>{item.label}</Option>)}
										</Select>
									</label>
									<label className="horosa-huangji-select-field">
										<span>推演宫</span>
										<Select value={this.state.nanjiPalace} onChange={(value)=>this.setState({ nanjiPalace: value })}>
											{BRANCH_NAMES.map((item)=><Option value={item} key={item}>{item}</Option>)}
										</Select>
									</label>
									<label className="horosa-huangji-select-field">
										<span>宿度</span>
										<InputNumber min={0} max={30} step={0.5} value={this.state.nanjiDegree} onChange={(value)=>this.setState({ nanjiDegree: value || 1 })} />
									</label>
									{this.state.nanjiMode === 'manual' ? (
										<>
											<label className="horosa-huangji-select-field">
												<span>历年</span>
												<InputNumber min={1} max={9999} value={this.state.nanjiLunarYear} onChange={(value)=>this.setState({ nanjiLunarYear: value || 2026 })} />
											</label>
											<label className="horosa-huangji-select-field">
												<span>节月</span>
												<InputNumber min={1} max={12} value={this.state.nanjiSolarMonth} onChange={(value)=>this.setState({ nanjiSolarMonth: value || 1 })} />
											</label>
											<label className="horosa-huangji-select-field">
												<span>日</span>
												<InputNumber min={1} max={31} value={this.state.nanjiDay} onChange={(value)=>this.setState({ nanjiDay: value || 1 })} />
											</label>
											<label className="horosa-huangji-select-field">
												<span>时支</span>
												<Select value={this.state.nanjiHourZhi} onChange={(value)=>this.setState({ nanjiHourZhi: value })}>
													{BRANCH_NAMES.map((item)=><Option value={item} key={item}>{item}</Option>)}
												</Select>
											</label>
											<label className="horosa-huangji-select-field">
												<span>立春</span>
												<Select value={this.state.nanjiAfterLichun} onChange={(value)=>this.setState({ nanjiAfterLichun: value })}>
													<Option value="1">立春后</Option>
													<Option value="0">立春前</Option>
												</Select>
											</label>
											<label className="horosa-huangji-select-field">
												<span>日干</span>
												<Select value={this.state.nanjiDayGan} onChange={(value)=>this.setState({ nanjiDayGan: value })}>
													<Option value="">自动</Option>
													{STEM_NAMES.map((item)=><Option value={item} key={item}>{item}</Option>)}
												</Select>
											</label>
											<label className="horosa-huangji-select-field">
												<span>日支</span>
												<Select value={this.state.nanjiDayZhi} onChange={(value)=>this.setState({ nanjiDayZhi: value })}>
													<Option value="">自动</Option>
													{BRANCH_NAMES.map((item)=><Option value={item} key={item}>{item}</Option>)}
												</Select>
											</label>
										</>
									) : null}
								</>
							) : null}
							{this.config.serviceKey === 'chunzi' ? (
								<>
									<label className="horosa-huangji-select-field">
										<span>刻法</span>
										<Select value={this.state.chunziKeMode} onChange={(value)=>this.setState({ chunziKeMode: value })}>
											<Option value="auto">自动换算</Option>
											<Option value="manual">手动指定</Option>
											<Option value="none">不取刻数</Option>
										</Select>
									</label>
									{this.state.chunziKeMode === 'manual' ? (
										<label className="horosa-huangji-select-field">
											<span>刻数</span>
											<Select value={this.state.chunziKe} onChange={(value)=>this.setState({ chunziKe: value })}>
												{CHUNZI_KE_OPTIONS.map((item)=><Option value={item.value} key={item.value}>{item.label}</Option>)}
											</Select>
										</label>
									) : null}
									<label className="horosa-huangji-select-field">
										<span>月日匹配</span>
										<Select value={this.state.chunziLunarMode} onChange={(value)=>this.setState({ chunziLunarMode: value })}>
											<Option value="auto">随当前日期</Option>
											<Option value="manual">手动月日</Option>
											<Option value="none">关闭</Option>
										</Select>
									</label>
									{this.state.chunziLunarMode === 'manual' ? (
										<>
											<label className="horosa-huangji-select-field">
												<span>农历月</span>
												<InputNumber min={1} max={12} value={this.state.chunziLunarMonth} onChange={(value)=>this.setState({ chunziLunarMonth: value || 1 })} />
											</label>
											<label className="horosa-huangji-select-field">
												<span>农历日</span>
												<InputNumber min={1} max={30} value={this.state.chunziLunarDay} onChange={(value)=>this.setState({ chunziLunarDay: value || 1 })} />
											</label>
										</>
									) : null}
									<label className="horosa-huangji-select-field">
										<span>宿名</span>
										<Select value={this.state.chunziMansion} onChange={(value)=>this.setState({ chunziMansion: value })}>
											{CHUNZI_MANSION_OPTIONS.map((item)=><Option value={item.value} key={item.value}>{item.label}</Option>)}
										</Select>
									</label>
									<label className="horosa-huangji-select-field">
										<span>时辰</span>
										<Select value={this.state.chunziHourBranch} onChange={(value)=>this.setState({ chunziHourBranch: value })}>
											{BRANCH_NAMES.map((item)=><Option value={item} key={item}>{item}</Option>)}
										</Select>
									</label>
									<label className="horosa-huangji-select-field">
										<span>显示数量</span>
										<Select value={this.state.chunziResultLimit} onChange={(value)=>this.setState({ chunziResultLimit: value })}>
											{CHUNZI_RESULT_LIMIT_OPTIONS.map((item)=><Option value={item.value} key={item.value}>{item.label}</Option>)}
										</Select>
									</label>
									<label className="horosa-huangji-select-field is-wide">
										<span>条文代码</span>
										<Input value={this.state.chunziLookupCode} placeholder="可批量：毕龙6巳、室巨9未" onChange={(event)=>this.setState({ chunziLookupCode: event.target.value })} />
									</label>
									<label className="horosa-huangji-select-field is-wide">
										<span>关键词</span>
										<Input value={this.state.chunziKeyword} placeholder="如：先去父、妻宫" onChange={(event)=>this.setState({ chunziKeyword: event.target.value })} />
									</label>
									<label className="horosa-huangji-select-field is-wide">
										<span>多标签</span>
										<Input value={this.state.chunziTags} placeholder="逗号分隔，如：先去父,石皮" onChange={(event)=>this.setState({ chunziTags: event.target.value })} />
									</label>
								</>
							) : null}
							{this.config.serviceKey === 'xianqin' ? (
								<div className="horosa-kinastro-xianqin-options">
								<div className="horosa-kinastro-xianqin-option-row is-method">
									<label className="horosa-huangji-select-field">
										<span>性别</span>
										<Select value={this.state.gender} dropdownMatchSelectWidth={false} onChange={(value)=>this.setState({ gender: value })}>
											<Option value="1">男</Option>
											<Option value="0">女</Option>
										</Select>
									</label>
									<label className="horosa-huangji-select-field">
										<span>入式历法</span>
										<Select value={this.state.calendarMode} onChange={(value)=>this.setState({ calendarMode: value })}>
											<Option value="autoLunar">自动换算农历</Option>
											<Option value="manualLunar">手动农历</Option>
											<Option value="solarAsLunar">公历数值入式</Option>
										</Select>
									</label>
								</div>
								<div className="horosa-kinastro-xianqin-option-row is-lunar">
									<label className="horosa-huangji-select-field">
										<span>农历年</span>
										<InputNumber min={1} max={9999} value={this.state.lunarYear} disabled={this.state.calendarMode !== 'manualLunar'} onChange={(value)=>this.setState({ lunarYear: value || 2026 })} />
									</label>
									<label className="horosa-huangji-select-field">
										<span>农历月</span>
										<InputNumber min={1} max={12} value={this.state.lunarMonth} disabled={this.state.calendarMode !== 'manualLunar'} onChange={(value)=>this.setState({ lunarMonth: value || 1 })} />
									</label>
									<label className="horosa-huangji-select-field">
										<span>农历日</span>
										<InputNumber min={1} max={30} value={this.state.lunarDay} disabled={this.state.calendarMode !== 'manualLunar'} onChange={(value)=>this.setState({ lunarDay: value || 1 })} />
									</label>
								</div>
							</div>
						) : null}
					</div>
				</div>
				<div className="horosa-huangji-action-row">
					<Button type="primary" onClick={this.clickPlot}>起盘</Button>
				</div>
			</div>
		);
	}

	renderMetaGrid(items){
		return (
			<div className="horosa-huangji-meta-grid horosa-kinastro-meta-grid">
				{items.map((item)=>(
					<div key={item.label}>
						<span>{item.label}</span>
						<strong>{fmtValue(item.value)}</strong>
					</div>
				))}
			</div>
		);
	}

	renderShaoziCenter(pan){
		const sz = pan.shaozi || {};
		const full = pan.full || {};
		const key = full.key || {};
		const pillars = pan.pillars || [];
		return (
			<div className="horosa-taixuan-board horosa-kinastro-board horosa-kinastro-shaozi-board">
				<div className="horosa-huangji-board-header">
					<div><h2 className="horosa-taixuan-title">邵子神数</h2></div>
					<div className="horosa-huangji-board-time">{fmtValue(pan.dateStr)} {fmtValue(pan.timeStr)}</div>
				</div>
				{this.renderMetaGrid([
					{ label: '条文号', value: sz.tiaowenId },
					{ label: '集', value: sz.collection },
					{ label: '卦名', value: sz.guaName || full.gua },
					{ label: '基础数', value: full.base_number },
					{ label: '钥匙', value: key['名稱'] },
					{ label: '刻数', value: pan.ke },
				])}
				<div className="horosa-kinastro-pillar-grid">
					{pillars.map((item)=>(
						<div className="horosa-shenyishu-pillar-card" key={item.key}>
							<span>{item.label}</span>
							<strong>{fmtValue(item.ganzhi)}</strong>
						</div>
					))}
				</div>
				<div className="horosa-kinastro-feature-grid">
					<div className="horosa-taixuan-text-card horosa-kinastro-text-card">
						<span>四位起数</span>
						<strong>{fmtValue(sz.yearDigit)} / {fmtValue(sz.monthDigit)} / {fmtValue(sz.dayDigit)} / {fmtValue(sz.hourDigit)}</strong>
						<p>{fmtValue(sz.note)}</p>
					</div>
					<div className="horosa-taixuan-text-card horosa-kinastro-text-card">
						<span>条文</span>
						<strong>{fmtValue(sz.tiaowenText)}</strong>
					</div>
					<div className="horosa-taixuan-text-card horosa-kinastro-text-card">
						<span>64钥匙</span>
						<strong>{fmtValue(key['說明'])}</strong>
						<p>{fmtValue(key['特殊事項'])}</p>
					</div>
				</div>
			</div>
		);
	}

	renderTiebanCenter(pan){
		const tieban = pan.tieban || {};
		const kunji = tieban.kunji || {};
		const suanpan = tieban.suanpan || {};
		const isSuanpan = tieban.method === 'suanpan';
		const pillars = pan.pillars || [];
		const primaryText = isSuanpan ? textValue(suanpan.tiaowen) : textValue(kunji.tiaowen_data || kunji.verse);
		const palaceRows = Object.keys(kunji.palace_verses || {}).slice(0, 6).map((name)=>{
			const item = kunji.palace_verses[name] || {};
			return {
				name: name.replace(/[宮宫]$/, ''),
				branch: item.branch,
				number: item.number,
				verse: item.verse,
			};
		});
		const dayun = tieban.dayun || [];
		return (
			<div className="horosa-taixuan-board horosa-kinastro-board horosa-kinastro-tieban-board">
				<div className="horosa-huangji-board-header">
					<div><h2 className="horosa-taixuan-title">铁板神数</h2></div>
					<div className="horosa-huangji-board-time">{fmtValue(pan.dateStr)} {fmtValue(pan.timeStr)}</div>
				</div>
				{this.renderMetaGrid([
					{ label: '算法', value: tieban.methodLabel },
					{ label: isSuanpan ? '算盘总数' : '铁板号码', value: isSuanpan ? suanpan.total_number : kunji.tieban_number },
					{ label: isSuanpan ? '条文编号' : '坤集条文号', value: isSuanpan ? suanpan.tiaowen_key : kunji.tiaowen_number },
					{ label: isSuanpan ? '五部' : '命宫', value: isSuanpan ? suanpan.department : kunji.ming_palace },
					{ label: isSuanpan ? '纳音' : '身宫', value: isSuanpan ? suanpan.nayin : kunji.shen_palace },
					{ label: isSuanpan ? '岁君加数' : '刻分', value: isSuanpan ? suanpan.suijun_add : `${fmtValue(kunji.ke_label)} / ${fmtValue(kunji.fen)}` },
				])}
				<div className="horosa-kinastro-pillar-grid">
					{pillars.map((item)=>(
						<div className="horosa-shenyishu-pillar-card" key={item.key}>
							<span>{item.label}</span>
							<strong>{fmtValue(item.ganzhi)}</strong>
						</div>
					))}
				</div>
				<div className="horosa-kinastro-feature-grid horosa-kinastro-tieban-feature-grid">
					<div className="horosa-taixuan-text-card horosa-kinastro-text-card">
						<span>{isSuanpan ? '算盘结构' : '命身刻分'}</span>
						<strong>{isSuanpan ? `${fmtValue(suanpan.stem_sum)} + ${fmtValue(suanpan.branch_sum)} + ${fmtValue(suanpan.suijun_add)}` : `${fmtValue(kunji.ming_palace)} / ${fmtValue(kunji.shen_palace)} / ${fmtValue(kunji.wuxing_ju)}`}</strong>
						<p>{isSuanpan ? fmtValue(suanpan.note) : `河洛数 ${fmtValue(kunji.he_luo_number)}，扣入 ${fmtValue(kunji.kunji_tiangan)}`}</p>
					</div>
					<div className="horosa-taixuan-text-card horosa-kinastro-text-card is-large">
						<span>条文</span>
						<strong>{primaryText}</strong>
					</div>
					<div className="horosa-taixuan-text-card horosa-kinastro-text-card">
						<span>大运</span>
						<strong>{dayun.slice(0, 3).map((item)=>fmtValue(item.age || item.dayun_number)).filter((item)=>item !== '—').join(' / ') || '—'}</strong>
						<p>{dayun.length ? textValue(dayun[0].tiaowen) : '—'}</p>
					</div>
				</div>
				{palaceRows.length ? (
					<div className="horosa-kinastro-tieban-palace-strip">
						{palaceRows.map((item)=>(
							<div key={`${item.name}_${item.branch}`}>
								<span>{item.name} {fmtValue(item.branch)}</span>
								<strong>{fmtValue(item.number)}</strong>
								<p>{fmtValue(item.verse)}</p>
							</div>
						))}
					</div>
				) : null}
			</div>
		);
	}

	renderFendjingCenter(pan){
		const fendjing = pan.fendjing || {};
		const pillars = pan.pillars || [];
		const sections = fendjing.sections || {};
		const sectionCards = [
			{ key: 'foundation', title: '基业', value: sections.foundation },
			{ key: 'siblings', title: '兄弟', value: sections.siblings },
			{ key: 'conduct', title: '行藏', value: sections.conduct },
			{ key: 'marriage', title: '婚姻', value: sections.marriage },
			{ key: 'children', title: '子息', value: sections.children },
			{ key: 'harvest', title: '收成', value: sections.harvest },
		];
		return (
			<div className="horosa-taixuan-board horosa-kinastro-board horosa-kinastro-fendjing-board">
				<div className="horosa-huangji-board-header">
					<div><h2 className="horosa-taixuan-title">鬼谷分定经</h2></div>
					<div className="horosa-huangji-board-time">{fmtValue(pan.dateStr)} {fmtValue(pan.timeStr)}</div>
				</div>
				{this.renderMetaGrid([
					{ label: '两头钳', value: fendjing.twoGanKey },
					{ label: '年干', value: fendjing.yearStem },
					{ label: '时干', value: fendjing.hourStem },
					{ label: '命格', value: fendjing.minggeName },
					{ label: '来源', value: fendjing.stemOverride ? '手动指定' : '自动换算' },
					{ label: '组合库', value: fendjing.dataSize },
				])}
				<div className="horosa-kinastro-pillar-grid">
					{pillars.map((item)=>(
						<div className="horosa-shenyishu-pillar-card" key={item.key}>
							<span>{item.label}</span>
							<strong>{fmtValue(item.ganzhi)}</strong>
						</div>
					))}
				</div>
				<div className="horosa-kinastro-feature-grid horosa-kinastro-fendjing-feature-grid">
					<div className="horosa-taixuan-text-card horosa-kinastro-text-card">
						<span>判断</span>
						<strong>{fmtValue(fendjing.judgment)}</strong>
					</div>
					<div className="horosa-taixuan-text-card horosa-kinastro-text-card is-large">
						<span>命格</span>
						<strong>{fmtValue(fendjing.minggeName)}</strong>
						<p>{fmtValue(fendjing.minggeText)}</p>
					</div>
					<div className="horosa-taixuan-text-card horosa-kinastro-text-card">
						<span>两头取象</span>
						<strong>{fmtValue(fendjing.twoGanKey)}</strong>
						<p>{fmtValue(fendjing.yearStem)}年干 · {fmtValue(fendjing.hourStem)}时干</p>
					</div>
				</div>
				<div className="horosa-kinastro-fendjing-verse-grid">
					{sectionCards.map((item)=>(
						<div key={item.key}>
							<span>{item.title}</span>
							<p>{fmtValue(item.value)}</p>
						</div>
					))}
				</div>
			</div>
		);
	}

	renderBeijiCenter(pan){
		const beiji = pan.beiji || {};
		const queries = beiji.queries || [];
		const dayun = beiji.dayun || [];
		const family = (beiji.queryGroups && beiji.queryGroups.family) || queries.filter((item)=>['parents', 'siblings', 'first_wife_surname', 'remarriage_wife_surname', 'children'].includes(item.type));
		const fortune = (beiji.queryGroups && beiji.queryGroups.fortune) || queries.filter((item)=>['character', 'wealth', 'career', 'health'].includes(item.type));
		const queryCard = (item)=>(
			<div key={`${item.type}_${item.code}`}>
				<span>{fmtValue(item.label)}</span>
				<strong>{fmtValue(item.code)} · {fmtValue(item.palaceName)}宫{item.surname ? ` · 姓${fmtValue(item.surname)}` : ''}</strong>
				<p>{fmtValue(item.verse)}</p>
			</div>
		);
		return (
			<div className="horosa-taixuan-board horosa-kinastro-board horosa-kinastro-beiji-board">
				<div className="horosa-huangji-board-header">
					<div><h2 className="horosa-taixuan-title">北极神数</h2></div>
					<div className="horosa-huangji-board-time">{fmtValue(pan.dateStr)} {fmtValue(pan.timeStr)}</div>
				</div>
				{this.renderMetaGrid([
					{ label: '年干支', value: `${fmtValue(beiji.yearStem)}${fmtValue(beiji.yearBranch)}` },
					{ label: '生肖', value: beiji.yearShengxiao },
					{ label: '时辰', value: `${fmtValue(beiji.hourBranch)}时` },
					{ label: '刻', value: `${fmtValue(beiji.keValue)} · ${fmtValue(beiji.keLabel)}` },
					{ label: '刻法', value: beiji.keModeLabel },
					{ label: '条文库', value: beiji.verseCount },
					...(beiji.keMode === 'manual' ? [{ label: '自动刻', value: `${fmtValue(beiji.autoKeValue)} · ${fmtValue(beiji.autoKeLabel)}` }] : []),
				])}
				<div className="horosa-kinastro-beiji-core">
					<div className="horosa-shenyishu-pillar-card">
						<span>年干</span>
						<strong>{fmtValue(beiji.yearStem)}</strong>
					</div>
					<div className="horosa-shenyishu-pillar-card">
						<span>年支</span>
						<strong>{fmtValue(beiji.yearBranch)}</strong>
					</div>
					<div className="horosa-shenyishu-pillar-card">
						<span>时辰</span>
						<strong>{fmtValue(beiji.hourBranch)}时</strong>
					</div>
					<div className="horosa-shenyishu-pillar-card">
						<span>刻分</span>
						<strong>{fmtValue(beiji.keLabel)}</strong>
					</div>
				</div>
				<div className="horosa-kinastro-beiji-query-grid">
					{family.slice(0, 4).map(queryCard)}
					{fortune.slice(0, 4).map(queryCard)}
				</div>
				<div className="horosa-kinastro-beiji-dayun-grid">
					{dayun.map((item)=>(
						<div key={`${item.index}_${item.code}`}>
							<span>{fmtValue(item.startAge)}-{fmtValue(item.endAge)}岁</span>
							<strong>{fmtValue(item.stemBranch)}</strong>
							<p>{fmtValue(item.code)} · {fmtValue(item.direction)}行</p>
						</div>
					))}
				</div>
			</div>
		);
	}

	renderNanjiCenter(pan){
		const nanji = pan.nanji || {};
		const fp = nanji.fourPillars || {};
		const query = nanji.query || {};
		const palaceEntries = nanji.palaceEntries || [];
		const queryEntries = query.entries || [];
		const dayun = nanji.daYun || [];
		const primaryEntries = queryEntries.length ? queryEntries : palaceEntries.slice(0, 6);
		return (
			<div className="horosa-taixuan-board horosa-kinastro-board horosa-kinastro-nanji-board">
				<div className="horosa-huangji-board-header">
					<div><h2 className="horosa-taixuan-title">南极神数</h2></div>
					<div className="horosa-huangji-board-time">{fmtValue(pan.dateStr)} {fmtValue(pan.timeStr)}</div>
				</div>
				{this.renderMetaGrid([
					{ label: '宫部', value: nanji.palaceSection },
					{ label: '起盘方式', value: nanji.modeLabel },
					{ label: '年干阴阳', value: fp.yearYinyang },
					{ label: '条文库', value: nanji.verseCount },
					{ label: '查询密码', value: query.code },
					{ label: '命中数', value: query.count },
					{ label: '星图', value: nanji.divine && nanji.divine.chart },
					{ label: '推演宫', value: nanji.divine && nanji.divine.palace },
					{ label: '宿度', value: nanji.divine && nanji.divine.degree },
				])}
				<div className="horosa-kinastro-pillar-grid">
					{[
						{ label: '年柱', value: fp.year },
						{ label: '月柱', value: fp.month },
						{ label: '日柱', value: fp.day },
						{ label: '时柱', value: fp.hour },
					].map((item)=>(
						<div className="horosa-shenyishu-pillar-card" key={item.label}>
							<span>{item.label}</span>
							<strong>{fmtValue(item.value)}</strong>
						</div>
					))}
				</div>
				<div className="horosa-kinastro-nanji-entry-grid">
					{primaryEntries.slice(0, 6).map((item, idx)=>(
						<div key={`${item.rawSection || item.section}_${item.rawCode || item.code}_${idx}`}>
							<span>{fmtValue(item.section)} · {fmtValue(item.code)}</span>
							<strong>{fmtValue(item.verse)}</strong>
							<p>{fmtValue(item.comment)}</p>
						</div>
					))}
				</div>
				<div className="horosa-kinastro-beiji-dayun-grid horosa-kinastro-nanji-dayun-grid">
					{dayun.map((item)=>(
						<div key={`${item.index}_${item.ganzhi}`}>
							<span>{fmtValue(item.startAge)}-{fmtValue(item.endAge)}岁</span>
							<strong>{fmtValue(item.ganzhi)}</strong>
							<p>第{fmtValue(item.index)}运</p>
						</div>
					))}
				</div>
			</div>
		);
	}

	renderChunziCenter(pan){
		const chunzi = pan.chunzi || {};
		const analysis = chunzi.analysis || {};
		const parents = analysis.parents || {};
		const spouse = analysis.spouse || {};
		const children = analysis.children || {};
		const verses = chunzi.verses || [];
		const renderVerse = (item, idx)=>(
			<div key={`${item.rawCode || item.code}_${idx}`}>
				<span>{fmtValue(item.code)} · {fmtValue(item.category)}宿</span>
				<strong>{[item.star, item.degree ? `${item.degree}度` : '', item.branch].map(fmtValue).filter((text)=>text && text !== '—').join(' · ') || '—'}</strong>
				<p>{fmtValue(item.verse)}</p>
			</div>
		);
		return (
			<div className="horosa-taixuan-board horosa-kinastro-board horosa-kinastro-chunzi-board">
				<div className="horosa-huangji-board-header">
					<div><h2 className="horosa-taixuan-title">蠢子数</h2></div>
					<div className="horosa-huangji-board-time">{fmtValue(pan.dateStr)} {fmtValue(pan.timeStr)}</div>
				</div>
				{this.renderMetaGrid([
					{ label: '命造', value: chunzi.genderLabel },
					{ label: '刻法', value: chunzi.keModeLabel },
					{ label: '刻数', value: chunzi.keValueLabel },
					{ label: '月日匹配', value: chunzi.lunarModeLabel },
					{ label: '农历月日', value: chunzi.lunarText },
					{ label: '候选代码', value: (chunzi.codes || []).length },
					{ label: '显示数量', value: chunzi.resultLimit ? `${chunzi.resultLimit}条` : '' },
					{ label: '条文库', value: chunzi.verseCount },
				])}
				<div className="horosa-kinastro-pillar-grid">
					{(chunzi.pillars || []).map((item)=>(
						<div className="horosa-shenyishu-pillar-card" key={item.key || item.label}>
							<span>{item.label}</span>
							<strong>{fmtValue(item.ganzhi)}</strong>
						</div>
					))}
				</div>
				<div className="horosa-kinastro-chunzi-analysis-grid">
					<div>
						<span>父母</span>
						<strong>{fmtValue({
							父属: parents.father,
							母属: parents.mother,
							父先亡: parents.father_first,
							母先亡: parents.mother_first,
						})}</strong>
					</div>
					<div>
						<span>妻宫</span>
						<strong>{fmtValue({
							属相: spouse.zodiac,
							侧室: spouse.concubine,
							再娶: spouse.remarriage,
						})}</strong>
					</div>
					<div>
						<span>子息</span>
						<strong>{fmtValue({
							数量: children.count,
							带石皮: children.stone_skin,
						})}</strong>
					</div>
					<div>
						<span>事业 / 特记</span>
						<strong>{fmtValue([analysis.career, analysis.conflicts, analysis.flags, analysis.longevity ? `寿元${analysis.longevity}岁` : ''])}</strong>
					</div>
				</div>
				<div className="horosa-kinastro-nanji-entry-grid horosa-kinastro-chunzi-verse-grid">
					{verses.length ? verses.slice(0, 6).map(renderVerse) : (
						<div>
							<span>候选条文</span>
							<strong>未命中</strong>
							<p>可改用手动代码、宿名或关键词检索补查。</p>
						</div>
					)}
				</div>
			</div>
		);
	}

	renderXianqinCenter(pan){
		const chart = pan.xianqin || {};
		const basic = chart.basic_info || {};
		const stars = chart.stars || {};
		const pattern = chart.pattern || {};
		const palaces = chart.palaces || {};
		const branchToPalace = {};
		(pan.palaceCards || []).forEach((card)=>{
			const branchIdx = BRANCH_INDEX[card.branch];
			if(branchIdx !== undefined){
				branchToPalace[branchIdx] = card;
			}
		});
		const renderCell = (item)=>{
			const palace = branchToPalace[item.branch] || {};
			const branch = palace.branch || Object.keys(BRANCH_INDEX).find((key)=>BRANCH_INDEX[key] === item.branch) || '—';
			const palaceName = palace.name || getXianqinPalaceNameByBranch(chart, branch) || branch;
			const palaceStars = (palace.stars && palace.stars.length)
				? palace.stars
				: [getXianqinPalaceStarEntry(chart, palaceName)].filter(Boolean);
			const isTai = (palaces.tai_gong || {}).branch === branch;
			const isMing = (palaces.ming_gong || {}).branch === branch;
			const isShen = (palaces.shen_gong || {}).branch === branch;
			const marks = [
				isTai ? '胎' : '',
				isMing ? '命' : '',
				isShen ? '身' : '',
			].filter(Boolean);
			return (
				<div
					className={`horosa-kinastro-cetian-cell horosa-kinastro-xianqin-cell${isTai ? ' is-tai' : ''}${isMing ? ' is-ming' : ''}${isShen ? ' is-shen' : ''}`}
					key={`${palace.name || branch}_${item.branch}`}
					style={{ gridRow: item.row, gridColumn: item.col }}
				>
					<div className="horosa-kinastro-cetian-cell-top">
						<span>{branch}</span>
						<em>{marks.join(' / ')}</em>
					</div>
					<strong>{fmtValue(palaceName || '—')}</strong>
					<div className="horosa-kinastro-cetian-starline is-main">{fmtValue(palaceStars[0])}</div>
					<div className="horosa-kinastro-cetian-starline is-aux">{fmtValue(palaceStars.slice(1))}</div>
				</div>
			);
		};
		return (
			<div className="horosa-taixuan-board horosa-kinastro-board horosa-kinastro-xianqin-board">
				<div className="horosa-huangji-board-header">
					<div><h2 className="horosa-taixuan-title">万化仙禽</h2></div>
					<div className="horosa-huangji-board-time">{fmtValue(pan.dateStr)} {fmtValue(pan.timeStr)}</div>
				</div>
				<div className="horosa-kinastro-cetian-grid horosa-kinastro-xianqin-grid">
					{TWELVE_PALACE_LAYOUT.map(renderCell)}
					<div className="horosa-kinastro-cetian-center horosa-kinastro-xianqin-center">
						<h3>万化仙禽</h3>
						<p>{fmtValue(pan.calendarModeLabel)} · {fmtValue(basic.year)}年{fmtValue(basic.month)}月{fmtValue(basic.day)}日</p>
						<div className="horosa-kinastro-cetian-center-grid">
							<span>三元<strong>{fmtValue(basic.san_yuan)}</strong></span>
							<span>昼夜<strong>{fmtValue(basic.day_night)}</strong></span>
							<span>胎星<strong>{fmtValue(stars.tai_xing)}</strong></span>
							<span>命星<strong>{fmtValue(stars.ming_xing)}</strong></span>
						</div>
						<div className="horosa-kinastro-cetian-sihua">
							<span>身星 {fmtValue(stars.shen_xing)}</span>
							<span>{fmtValue(pattern.grade)}</span>
						</div>
						<small>{fmtValue(pattern.reason)}</small>
					</div>
				</div>
			</div>
		);
	}

	renderCetianCenter(pan){
		const chart = pan.cetian || {};
		const branchToPalace = {};
		(chart.palaces || []).forEach((palace)=>{
			branchToPalace[palace.branch] = palace;
		});
		const renderCell = (item)=>{
			const palace = branchToPalace[item.branch] || {};
			const isMing = palace.branch === chart.ming_gong_branch;
			const isShen = palace.branch === chart.shen_gong_branch;
			return (
				<div
					className={`horosa-kinastro-cetian-cell${isMing ? ' is-ming' : ''}${isShen ? ' is-shen' : ''}`}
					key={`${palace.name}_${item.branch}`}
					style={{ gridRow: item.row, gridColumn: item.col }}
				>
					<div className="horosa-kinastro-cetian-cell-top">
						<span>{fmtValue(palace.stem_name)}{fmtValue(palace.branch_name)}</span>
						<em>{fmtValue(palace.da_xian)}</em>
					</div>
					<strong>{fmtValue(palace.name)}</strong>
					<div className="horosa-kinastro-cetian-starline is-main">{fmtValue(palace.stars)}</div>
					<div className="horosa-kinastro-cetian-starline is-aux">{fmtValue(palace.aux_stars)}</div>
					<small>{fmtValue(palace.sihua || palace.flying_stars || palace.patterns)}</small>
				</div>
			);
		};
		return (
			<div className="horosa-taixuan-board horosa-kinastro-board horosa-kinastro-cetian-board">
				<div className="horosa-huangji-board-header">
					<div><h2 className="horosa-taixuan-title">策天飞星</h2></div>
					<div className="horosa-huangji-board-time">{fmtValue(pan.dateStr)} {fmtValue(pan.timeStr)}</div>
				</div>
				<div className="horosa-kinastro-cetian-grid">
					{TWELVE_PALACE_LAYOUT.map(renderCell)}
					<div className="horosa-kinastro-cetian-center">
						<h3>策天十八飞星</h3>
						<p>{fmtValue(pan.lunar && pan.lunar.text)}</p>
						<div className="horosa-kinastro-cetian-center-grid">
							<span>命宫<strong>{fmtValue(pan.mingGong)}</strong></span>
							<span>身宫<strong>{fmtValue(pan.shenGong)}</strong></span>
							<span>五行局<strong>{fmtValue(pan.wuXingJu)}</strong></span>
							<span>紫微<strong>{fmtValue(pan.ziwei)}</strong></span>
						</div>
						<div className="horosa-kinastro-cetian-sihua">
							{Object.keys(chart.sihua || {}).map((star)=>(
								<span key={star}>{star}化{chart.sihua[star]}</span>
							))}
						</div>
						<small>{fmtValue(chart.solar_term_influence)}</small>
					</div>
				</div>
			</div>
		);
	}

	renderZiWeiCopiedCenter(pan){
		const chart = buildKinAstroZiWeiChart(pan, this.config.serviceKey);
		const rules = buildZiWeiRulesForChart(chart);
		return (
			<div className="horosa-kinastro-ziwei-copy-board">
				<div className="horosa-ziwei-chart-viewport horosa-kinastro-ziwei-viewport">
					<ZiWeiChart
						value={chart}
						height="100%"
						fields={this.props.fields}
						rules={rules}
						onCenterInfoClick={this.openCenterInfo}
					/>
				</div>
				<button
					type="button"
					className="horosa-kinastro-center-info-overlay"
					onClick={this.openCenterInfo}
					aria-label="打开命盘信息"
				>
					命盘信息
				</button>
			</div>
		);
	}

	renderCenterInfoModal(){
		if(this.config.serviceKey !== 'xianqin' && this.config.serviceKey !== 'cetian'){
			return null;
		}
		const sections = this.getCenterInfoSections();
		return (
			<Modal
				open={this.state.centerInfoVisible}
				title="命盘信息"
				footer={null}
				onCancel={this.closeCenterInfo}
				width={640}
				className="horosa-ziwei-center-info-modal horosa-kinastro-center-info-modal"
			>
				{this.renderCenterInfoPanel(sections)}
			</Modal>
		);
	}

	getCenterInfoSections(){
		const sections = this.state.pan ? (this.state.pan.sections || []).filter((section)=>!INTERNAL_SECTION_TITLES.has(section.title)) : [];
		const titles = this.config.serviceKey === 'cetian'
			? ['起盘', '农历与命身', '三宫', '四化']
			: ['起盘', '农历与命身', '三宫', '三星', '二十八宿禽'];
		const matched = titles
			.map((title)=>sections.find((section)=>section.title === title))
			.filter((section)=>section && section.rows && section.rows.length);
		return matched.length ? matched : sections.slice(0, 4).filter((section)=>section.rows && section.rows.length);
	}

	renderCenterInfoPanel(sections){
		const list = sections || [];
		if(!list.length){
			return <div className="horosa-empty-hint">起盘后显示命盘信息</div>;
		}
		return (
			<div className="horosa-ziwei-meta-scroll horosa-astro-content-scroll horosa-kinastro-center-info-scroll">
				{list.map((section)=>{
					const rows = section.rows || [];
					const isPillar = section.title === '四柱' || rows.every((row)=>/[年月日時时]柱$/.test(row.label || ''));
					return (
						<div className="horosa-info-card" key={section.title}>
							<div className="horosa-info-card-title">{section.title}</div>
							{isPillar ? (
								<div className="horosa-ziwei-bazi-grid">
									{rows.map((row, idx)=>(
										<div className="horosa-ziwei-bazi-cell" key={`${section.title}_${row.label}_${idx}`}>
											<span>{row.label}</span>
											<strong>{fmtValue(row.value)}</strong>
										</div>
									))}
								</div>
							) : rows.map((row, idx)=>(
								<div className="horosa-info-row" key={`${section.title}_${row.label}_${idx}`}>
									<span>{row.label}</span>
									<strong>{fmtValue(row.value)}</strong>
								</div>
							))}
						</div>
					);
				})}
			</div>
		);
	}

	renderCenter(){
		const pan = this.state.pan;
		if(!pan){
			return <div className="horosa-huangji-empty">暂无{this.config.techniqueLabel}数据</div>;
		}
		if(this.config.serviceKey === 'xianqin'){
			return this.renderZiWeiCopiedCenter(pan);
		}
		if(this.config.serviceKey === 'cetian'){
			return this.renderZiWeiCopiedCenter(pan);
		}
		if(this.config.serviceKey === 'tieban'){
			return this.renderTiebanCenter(pan);
		}
		if(this.config.serviceKey === 'fendjing'){
			return this.renderFendjingCenter(pan);
		}
		if(this.config.serviceKey === 'beiji'){
			return this.renderBeijiCenter(pan);
		}
		if(this.config.serviceKey === 'nanji'){
			return this.renderNanjiCenter(pan);
		}
		if(this.config.serviceKey === 'chunzi'){
			return this.renderChunziCenter(pan);
		}
		return this.renderShaoziCenter(pan);
	}

	renderRows(sections){
		const list = sections || [];
		if(!list.length){
			return <div className="horosa-huangji-empty">暂无数据</div>;
		}
		return list.map((section)=>(
			<div className="horosa-huangji-info-card" key={section.title}>
				<div className="horosa-huangji-info-heading">{section.title}</div>
				{(section.rows || []).map((item, idx)=>(
					<div className="horosa-huangji-info-row" key={`${section.title}_${item.label}_${idx}`}>
						<span>{item.label}</span>
						<strong>{fmtValue(item.value)}</strong>
					</div>
				))}
			</div>
		));
	}

	renderClassics(){
		const classics = this.state.pan && this.state.pan.classics ? this.state.pan.classics : null;
		if(!classics || !classics.sections || !classics.sections.length){
			return <div className="horosa-huangji-empty">暂无来源说明</div>;
		}
		return (
			<div className="horosa-huangji-classics">
				{(classics.meta || []).map((item)=>(
					<div className="horosa-huangji-info-card" key={item.key}>
						<div className="horosa-huangji-info-heading">{item.title}</div>
						<div className="horosa-huangji-info-row"><span>作者</span><strong>{item.author}</strong></div>
						<div className="horosa-huangji-info-row"><span>说明</span><strong>{item.description}</strong></div>
					</div>
				))}
				<div className="horosa-huangji-classic-list">
					{classics.sections.map((section)=>(
						<div className="horosa-huangji-classic-section" key={section.title}>
							<strong>{section.title}</strong>
							<p>{section.content}</p>
						</div>
					))}
				</div>
			</div>
		);
	}

	getTabSections(tabKey){
		const sections = this.state.pan ? (this.state.pan.sections || []).filter((section)=>!INTERNAL_SECTION_TITLES.has(section.title)) : [];
		if(tabKey === 'overview'){
			return sections.slice(0, 4);
		}
		if(tabKey === 'pillars'){
			return sectionByTitle(sections, ['四柱']);
		}
		if(tabKey === 'digits'){
			return sectionByTitle(sections, ['四位起数', '河洛纳音', '完整结构', '64钥匙']);
		}
		if(tabKey === 'core'){
			return sectionByTitle(sections, ['命身刻分', '神数号码', '算盘定部', '计算摘要']);
		}
		if(tabKey === 'twoGan'){
			return sectionByTitle(sections, ['两头钳']);
		}
		if(tabKey === 'fate'){
			return sectionByTitle(sections, ['命格']);
		}
		if(tabKey === 'yearHour'){
			return sectionByTitle(sections, ['起盘', '年时', '条文索引']);
		}
		if(tabKey === 'queries'){
			return sectionByTitle(sections, ['完整条文']);
		}
		if(tabKey === 'search'){
			return sectionByTitle(sections, ['条文检索', '代码查询', '批量代码查询', '关键词检索', '多标签检索', '宿名检索', '时辰检索']);
		}
		if(tabKey === 'palaceText'){
			return sectionByTitle(sections, ['宫部条文']);
		}
		if(tabKey === 'queryText'){
			return sectionByTitle(sections, ['条文查询']);
		}
		if(tabKey === 'family'){
			return sectionByTitle(sections, ['家亲']);
		}
		if(tabKey === 'fortune'){
			return sectionByTitle(sections, ['财官性情']);
		}
		if(tabKey === 'text'){
			return sectionByTitle(sections, ['条文', '64钥匙', '元会运世']);
		}
		if(tabKey === 'palaces'){
			return sectionByTitle(sections, ['三宫', '十二宫', '十二宫条文'].concat((sections || []).map((s)=>s.title).filter((title)=>/[宫宮]$/.test(title))));
		}
		if(tabKey === 'verses'){
			return sectionByTitle(sections, ['条文', '十二宫条文', '条文库', '判断', '六段断语']);
		}
		if(tabKey === 'dayun'){
			return sectionByTitle(sections, ['大运']);
		}
		if(tabKey === 'password'){
			return sectionByTitle(sections, ['密码']);
		}
		if(tabKey === 'divine'){
			return sectionByTitle(sections, ['星图推演']);
		}
		if(tabKey === 'codes'){
			return sectionByTitle(sections, ['代码来源']);
		}
		if(tabKey === 'analysis'){
			return sectionByTitle(sections, ['结构解析']);
		}
		if(tabKey === 'candidates'){
			return sectionByTitle(sections, ['候选条文']);
		}
		if(tabKey === 'lookup'){
			return sectionByTitle(sections, ['代码查询', '批量代码查询']);
		}
		if(tabKey === 'stars'){
			return sectionByTitle(sections, ['三星', '衍生星', '二十八宿禽']);
		}
		if(tabKey === 'swallow'){
			return sectionByTitle(sections, ['吞啖合战', '情性与格局']);
		}
		if(tabKey === 'flying'){
			return sectionByTitle(sections, ['飞星']);
		}
		if(tabKey === 'patterns'){
			return sectionByTitle(sections, ['格局']);
		}
		if(tabKey === 'full'){
			return sections;
		}
		return sections.slice(0, 4);
	}

	renderRightPanel(){
		const snapshot = buildSnapshotText(this.state.pan);
		const visibleTabs = this.config.tabs.filter((item)=>{
			if(!this.state.pan){
				return item.key === 'overview' || item.key === 'snapshot';
			}
			if(item.key === 'snapshot'){
				return !!snapshot;
			}
			if(item.key === 'classics'){
				const classics = this.state.pan && this.state.pan.classics;
				return !!(classics && classics.sections && classics.sections.length);
			}
			return this.getTabSections(item.key).length > 0;
		});
		const activeKey = visibleTabs.some((item)=>item.key === this.state.rightPanelTab)
			? this.state.rightPanelTab
			: (visibleTabs[0] ? visibleTabs[0].key : 'overview');
		return (
			<Tabs activeKey={activeKey} onChange={this.setRightPanelTab} defaultActiveKey="overview" tabPosition="top" className="horosa-huangji-tabs horosa-kinastro-tabs">
				{visibleTabs.map((item)=>(
					<TabPane tab={item.label} key={item.key}>
						{item.key === 'snapshot' ? (
							<pre className="horosa-huangji-snapshot">{snapshot}</pre>
						) : item.key === 'classics' ? (
							<div className="horosa-huangji-section-list">{this.renderClassics()}</div>
						) : (
							<div className="horosa-huangji-section-list">{this.renderRows(this.getTabSections(item.key))}</div>
						)}
					</TabPane>
				))}
			</Tabs>
		);
	}

	renderBottomQuickDock(){
		const snapshot = buildSnapshotText(this.state.pan);
		const visibleTabs = this.config.tabs.filter((item)=>{
			if(!this.state.pan){
				return item.key === 'overview' || item.key === 'snapshot';
			}
			if(item.key === 'snapshot'){
				return !!snapshot;
			}
			if(item.key === 'classics'){
				const classics = this.state.pan && this.state.pan.classics;
				return !!(classics && classics.sections && classics.sections.length);
			}
			return this.getTabSections(item.key).length > 0;
		});
		const actions = [
			{ label: '起盘', icon: 'quickPrimary', onClick: this.clickPlot },
			...visibleTabs.map((item)=>({
				label: item.label,
				icon: item.key === 'snapshot' ? 'quickAi' : (item.key === 'classics' ? 'book' : 'quickNote'),
				active: this.state.rightPanelTab === item.key,
				onClick: ()=>this.setRightPanelTab(item.key),
			})),
		];
		return (
			<div className="horosa-bottom-quick-dock horosa-huangji-quick-dock horosa-kinastro-quick-dock">
				<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
				<div className="horosa-bottom-quick-actions horosa-huangji-quick-actions horosa-kinastro-quick-actions">
					{actions.map((item)=>(
						<button
							type="button"
							key={`${item.label}_${item.icon}`}
							className={`horosa-bottom-quick-button horosa-huangji-quick-button${item.active ? ' is-active' : ''}`}
							onClick={item.onClick}
						>
							<span className="horosa-bottom-quick-icon"><XQIcon name={item.icon} /></span>
							<span>{item.label}</span>
						</button>
					))}
				</div>
			</div>
		);
	}

	renderTechniqueRail(){
		const propTechniqueTabs = Array.isArray(this.props.techniqueTabs) ? this.props.techniqueTabs : [];
		if(propTechniqueTabs.length > 1){
			const activeTechnique = this.props.activeTechnique || this.props.technique || this.config.serviceKey;
			return (
				<div className="horosa-kinastro-technique-rail">
					{propTechniqueTabs.map((item)=>(
						<button
							type="button"
							key={item.key}
							className={activeTechnique === item.key ? 'is-active' : ''}
							onClick={()=>this.props.onTechniqueChange && this.props.onTechniqueChange(item.key)}
						>
							{item.label}
						</button>
					))}
				</div>
			);
		}
		if(!this.config.showRail){
			return null;
		}
		const techniques = this.config.moduleKey === 'shusuan'
			? [
					{ key: 'shaozi', label: '邵子神数' },
					{ key: 'tieban', label: '铁板神数' },
					{ key: 'fendjing', label: '鬼谷分定经' },
					{ key: 'beiji', label: '北极神数' },
					{ key: 'nanji', label: '南极神数' },
					{ key: 'chunzi', label: '蠢子数' },
				]
			: [{ key: this.props.technique || this.config.serviceKey, label: this.config.techniqueLabel }];
		return (
			<div className="horosa-kinastro-technique-rail">
				{techniques.map((item)=>(
					<button
						type="button"
						key={item.key}
						className={(this.props.technique || this.config.serviceKey) === item.key ? 'is-active' : ''}
						onClick={()=>this.props.onTechniqueChange && this.props.onTechniqueChange(item.key)}
					>
						{item.label}
					</button>
				))}
			</div>
		);
	}

	render(){
		const embedded = !!this.props.hideQuickDock;
		const chartRendererClass = this.config.serviceKey === 'xianqin' || this.config.serviceKey === 'cetian' ? ' xq-chart-renderer-ziwei' : '';
		const showTechniqueRail = this.config.showRail || (Array.isArray(this.props.techniqueTabs) && this.props.techniqueTabs.length > 1);
		let height = this.props.height ? this.props.height : 760;
		let pageStyle = { height: '100%', minHeight: 0, overflow: 'hidden' };
		if(embedded){
			pageStyle = { height: '100%', minHeight: 0, overflow: 'hidden' };
		}
		return (
			<div className={`horosa-huangji-page horosa-astro-redesign horosa-huangji-redesign horosa-kinastro-redesign horosa-kinastro-module-${this.config.moduleKey} horosa-kinastro-${this.config.serviceKey}-redesign${embedded ? ' horosa-huangji-embedded' : ''}`} style={pageStyle}>
				<div className="horosa-astro-layout horosa-astro-redesign-layout horosa-huangji-redesign-layout">
					<Spin spinning={this.state.loading}>
						<div className={`horosa-astro-redesign-grid horosa-huangji-redesign-grid horosa-kinastro-grid${showTechniqueRail ? ' has-technique-rail' : ''}`}>
							<div className="horosa-astro-context-panel horosa-astro-input-panel horosa-huangji-input-panel">
								{this.renderInputPanel()}
							</div>
							<div className={`horosa-chart-stage horosa-chart-stage-redesign horosa-huangji-chart-panel xq-chart-renderer${chartRendererClass}`}>
								<div className="horosa-huangji-board-host horosa-kinastro-board-host">{this.renderCenter()}</div>
							</div>
							<div className="horosa-inspector-panel horosa-astro-content-panel horosa-huangji-info-panel">
								<div className="horosa-side-panel-heading horosa-huangji-info-heading-main">
									<div>
										<div className="horosa-side-panel-title">{this.config.infoTitle}</div>
										<div className="horosa-side-panel-subtitle">{this.config.infoSubTitle}</div>
									</div>
								</div>
								{this.renderRightPanel()}
							</div>
							{this.renderTechniqueRail()}
						</div>
					</Spin>
					{!this.props.hideQuickDock && this.renderBottomQuickDock()}
					{this.renderCenterInfoModal()}
				</div>
			</div>
		);
	}
}

export default KinAstroMain;
