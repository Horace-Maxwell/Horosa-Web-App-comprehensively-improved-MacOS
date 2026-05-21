import { Component } from 'react';
import { XQModal, XQTabs as Tabs } from '../xq-ui';
import XQIcon from '../xq-icons';
import * as Constants from '../../utils/constants';
import request from '../../utils/request';
import {randomStr,} from '../../utils/helper';
import * as AstroConst from '../../constants/AstroConst';
import DateTime from '../comp/DateTime';
import GuoLaoInput from './GuoLaoInput';
import GuoLaoChart from './GuoLaoChart';
import GuoLaoMoiraPanel from './GuoLaoMoiraPanel';
import GuoLaoMoiraWheel from './GuoLaoMoiraWheel';
import GuoLaoMoiraPickWheel from './GuoLaoMoiraPickWheel';
import { GUOLAO_CHART_STYLE_MOIRA, GUOLAO_CHART_STYLE_PICK, GUOLAO_LIFE_MODE_COTRANS, GUOLAO_LIFE_MODE_YUMAO, GUOLAO_NODE_MODE_NORTH_RAHU, getStoredGuolaoChartStyle, getStoredGuolaoLifeMode, getStoredGuolaoNodeMode, getStoredGuolaoSu28Mode, getStoredMoiraTransitGodsVisible, normalizeGuolaoLifeMode, normalizeGuolaoNodeMode, setStoredGuolaoChartStyle, setStoredGuolaoLifeMode, setStoredGuolaoNodeMode, setStoredGuolaoSu28Mode, setStoredMoiraTransitGodsVisible, } from './GuoLaoChartStyle';
import { fetchMoiraQizhengRules, } from '../../services/qizheng';
import { saveModuleAISnapshot, } from '../../utils/moduleAiSnapshot';
import * as AstroText from '../../constants/AstroText';
import * as SZConst from '../suzhan/SZConst';
import * as Su28Helper from '../su28/Su28Helper';

const TabPane = Tabs.TabPane;

const SIMPLE_TOKEN_MAP = {
	A: '日',
	B: '月',
	C: '水',
	D: '金',
	E: '火',
	F: '木',
	G: '土',
	H: '天王',
	I: '海王',
	J: '冥王',
	K: '北交',
	L: '南交',
	p: '福点',
	v: '暗月',
	w: '紫气',
	y: '凯龙',
	z: '月亮朔望点',
	Y: '月亮平均远地点',
	$: '月亮平均近地点',
	a: '白羊',
	b: '金牛',
	c: '双子',
	d: '巨蟹',
	e: '狮子',
	f: '处女',
	g: '天秤',
	h: '天蝎',
	i: '射手',
	j: '摩羯',
	k: '水瓶',
	l: '双鱼',
	0: '上升',
	1: '天顶',
	2: '天底',
	3: '下降',
	4: '谷神星',
	5: '智神星',
	6: '婚神星',
	7: '灶神星',
	8: '人龙星',
};

const MOIRA_QUICK_ACTIONS = [
	{key: 'patterns', label: '格局', icon: 'sideStyle'},
	{key: 'yearStars', label: '化曜', icon: 'quickPrimary'},
	{key: 'weakSolid', label: '虚实', icon: 'sideHouses'},
	{key: 'natalStars', label: '命曜', icon: 'sidePlanets'},
	{key: 'transitStars', label: '流曜', icon: 'quickTransit'},
	{key: 'aspects', label: '相位', icon: 'sideSwitch'},
	{key: 'gods', label: '神煞', icon: 'quickNote'},
];

const MOIRA_PLANET_ORDER = [
	{id: AstroConst.SUN, name: '日'},
	{id: AstroConst.MOON, name: '月'},
	{id: AstroConst.VENUS, name: '金'},
	{id: AstroConst.JUPITER, name: '木'},
	{id: AstroConst.MERCURY, name: '水'},
	{id: AstroConst.MARS, name: '火'},
	{id: AstroConst.SATURN, name: '土'},
	{id: AstroConst.SOUTH_NODE, name: '计'},
	{id: AstroConst.NORTH_NODE, name: '罗'},
	{id: AstroConst.PURPLE_CLOUDS, name: '炁'},
	{id: AstroConst.DARKMOON, name: '孛'},
];

const STEM_BRANCHES = ['甲子', '乙丑', '丙寅', '丁卯', '戊辰', '己巳', '庚午', '辛未', '壬申', '癸酉', '甲戌', '乙亥', '丙子', '丁丑', '戊寅', '己卯', '庚辰', '辛巳', '壬午', '癸未', '甲申', '乙酉', '丙戌', '丁亥', '戊子', '己丑', '庚寅', '辛卯', '壬辰', '癸巳', '甲午', '乙未', '丙申', '丁酉', '戊戌', '己亥', '庚子', '辛丑', '壬寅', '癸卯', '甲辰', '乙巳', '丙午', '丁未', '戊申', '己酉', '庚戌', '辛亥', '壬子', '癸丑', '甲寅', '乙卯', '丙辰', '丁巳', '戊午', '己未', '庚申', '辛酉', '壬戌', '癸亥'];
const MOIRA_YEAR_STAR_BY_STEM = {
	甲: '火',
	乙: '孛',
	丙: '木',
	丁: '金',
	戊: '土',
	己: '月',
	庚: '水',
	辛: '炁',
	壬: '计',
	癸: '罗',
};
const MOIRA_YEAR_STAR_SEQ = ['火', '孛', '木', '金', '土', '月', '水', '炁', '计', '罗'];
const MOIRA_YEAR_STAR_MAP = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
const MOIRA_TEN_GOD_ORG = ['天禄', '天暗', '天福', '天耗', '天荫', '天贵', '天嗣', '天刑', '天印', '天囚', '天权'];
const MOIRA_TEN_GOD_ALT = ['比肩', '劫财', '食神', '伤官', '偏财', '正财', '七杀', '正官', '偏印', '正印'];
const MOIRA_YEAR_INFO_GROUPS = [
	['天禄', '科名', '天马', '生官'],
	['天暗', '科甲', '地驿'],
	['天福', '文星', '禄元'],
	['天耗', '魁星', '马元', '值难'],
	['天荫', '官星', '天元', '职元'],
	['天贵', '印星', '地元', '局主'],
	['天嗣', '寿元', '人元', '天经'],
	['天刑', '催官', '仁元', '地纬'],
	['天印', '禄神', '血支'],
	['天囚', '喜神', '血忌'],
	['天权', '爵星', '产星', '伤官'],
];
const MOIRA_BIRTH_GOD_ORDER = ['劫杀', '文昌', '禄勋', '大耗', '月杀', '咸池', '唐符', '天厨', '伏尸', '三刑', '勾神', '蓦越', '黄幡', '的杀', '孤辰', '天喜', '注受', '剑锋', '飞廉', '病符', '紫微', '华盖', '天贵', '六害', '孤虚', '游奕', '年符', '死符', '地雌', '卷舌', '绞杀', '天德', '贯索', '亡神', '国印', '岁殿', '卦气', '空亡', '豹尾', '擎天', '天空', '大杀', '天厄', '月廉', '天雄', '天哭', '天狗', '地耗', '月符', '披头', '红鸾', '岁驾', '小耗', '寡宿', '飞刃', '天耗', '斗杓', '驿马', '阳刃', '阑干', '玉贵', '血刃', '浮沉', '解神'];
const MOIRA_TRANSIT_GOD_ORDER = ['岁驾', '天空', '地雌', '贯索', '五鬼', '死符', '大耗', '天厄', '天雄', '大杀', '卷舌', '天德', '天狗', '蓦越', '亡神', '天喜', '披头', '血刃', '解神', '天哭', '地解', '劫杀', '的杀', '红鸾', '驿马', '游奕', '擎天', '黄幡', '豹尾', '天厨', '三刑', '六害', '咸池', '阳刃', '禄勋', '天贵'];
const MOIRA_SPEED_LIMITS = {
	Venus: {slow: 0.71, fast: 1.245},
	Jupiter: {slow: 0.05, fast: 0.23},
	Mercury: {slow: 0.88, fast: 1.50},
	Mars: {slow: 0.4, fast: 0.70},
	Saturn: {slow: 0.02, fast: 0.13},
};
const MOIRA_PLANET_CN_TO_ID = {
	日: AstroConst.SUN,
	月: AstroConst.MOON,
	水: AstroConst.MERCURY,
	金: AstroConst.VENUS,
	火: AstroConst.MARS,
	木: AstroConst.JUPITER,
	土: AstroConst.SATURN,
	罗: AstroConst.NORTH_NODE,
	计: AstroConst.SOUTH_NODE,
	炁: AstroConst.PURPLE_CLOUDS,
	孛: AstroConst.DARKMOON,
};
const MOIRA_RULER_BY_SIGN = {
	Aries: AstroConst.MARS,
	Taurus: AstroConst.VENUS,
	Gemini: AstroConst.MERCURY,
	Cancer: AstroConst.MOON,
	Leo: AstroConst.SUN,
	Virgo: AstroConst.MERCURY,
	Libra: AstroConst.VENUS,
	Scorpio: AstroConst.MARS,
	Sagittarius: AstroConst.JUPITER,
	Capricorn: AstroConst.SATURN,
	Aquarius: AstroConst.SATURN,
	Pisces: AstroConst.JUPITER,
};
const MOIRA_EXILE_BY_SIGN = {
	Aries: AstroConst.VENUS,
	Taurus: AstroConst.MARS,
	Gemini: AstroConst.JUPITER,
	Cancer: AstroConst.SATURN,
	Leo: AstroConst.SATURN,
	Virgo: AstroConst.JUPITER,
	Libra: AstroConst.MARS,
	Scorpio: AstroConst.VENUS,
	Sagittarius: AstroConst.MERCURY,
	Capricorn: AstroConst.MOON,
	Aquarius: AstroConst.SUN,
	Pisces: AstroConst.MERCURY,
};
const MOIRA_OVERCOMING = {
	日: '月',
	月: '日',
	金: '火',
	木: '金',
	水: '土',
	火: '水',
	土: '木',
	炁: '金',
	孛: '土',
	罗: '水',
	计: '木',
};

const GUOLAO_CACHE_MAX = 96;
const GUOLAO_SU28_CACHE_REV = 'guolao_moira_su28_v7_zheng_yumao_rise_set';
const GUOLAO_SU28_MODE_ZHENG_SIDEREAL = 4;
const guolaoMem = new Map();
const guolaoInflight = new Map();

function splitDegree(degree){
	let d = Number(degree);
	if(Number.isNaN(d)){
		return [0, 0];
	}
	if(d < 0){
		d += 360;
	}
	const deg = Math.floor(d % 30);
	const min = Math.floor(((d % 30) - deg) * 60);
	return [deg, min];
}

function isEncodedToken(text){
	return /^[A-Za-z0-9${}]$/.test((text || '').trim());
}

function msg(id){
	if(id === undefined || id === null){
		return '';
	}
	if(AstroText.AstroTxtMsg[id]){
		return AstroText.AstroTxtMsg[id];
	}
	if(AstroText.AstroMsg[id]){
		const val = AstroText.AstroMsg[id];
		if(!isEncodedToken(val)){
			return `${val}`;
		}
	}
	const one = `${id}`.trim();
	if(one.length === 1 && SIMPLE_TOKEN_MAP[one]){
		return SIMPLE_TOKEN_MAP[one];
	}
	return `${id}`;
}

function safeList(val){
	return Array.isArray(val) ? val : [];
}

function safeMap(val){
	return val && typeof val === 'object' ? val : {};
}

function hasUnverifiedMoiraPatternSource(value){
	return value && (
		value.styleSource === 'moira-dsl-not-evaluated'
		|| value.engine === 'moira-rules-on-horosa-ephemeris'
		|| value.version === 'qizheng-moira-rules-v1'
	);
}

function isIncompleteMoiraRules(value){
	if(!value){
		return true;
	}
	if(hasUnverifiedMoiraPatternSource(value)){
		return true;
	}
	const text = `${value.styleWarning || ''} ${value.summary || ''} ${value.message || ''}`;
	return (
		text.indexOf('仍在接入') >= 0
		|| text.indexOf('暂不输出') >= 0
		|| text.indexOf('暂不生成') >= 0
		|| text.indexOf('未返回完整') >= 0
		|| !Array.isArray(value.patterns)
	);
}

function moiraStyleLevelMeta(rules, currentLevel){
	const min = Number(rules && rules.styleLevelMin) || 1;
	const max = Number(rules && rules.styleLevelMax) || 5;
	const def = Number(rules && rules.styleLevel) || 3;
	let level = currentLevel === undefined || currentLevel === null ? def : Number(currentLevel);
	if(!Number.isFinite(level)){
		level = def;
	}
	level = Math.max(min, Math.min(max, Math.round(level)));
	return {
		min,
		max,
		level,
		displayLevel: max - level,
		fillMax: Number(rules && rules.styleFillMax) || 6,
	};
}

function applyMoiraStyleLevel(list, meta){
	const displayLevel = Number(meta && meta.displayLevel) || 0;
	const fillMax = Number(meta && meta.fillMax) || 6;
	const result = [];
	safeList(list).forEach((item)=>{
		const level = Number(item && item.moiraLevel);
		const rank = Number(item && item.moiraRank);
		const moiraLevel = Number.isFinite(level) ? level : 0;
		const moiraRank = Number.isFinite(rank) ? rank : 65536;
		if(moiraLevel < displayLevel){
			return;
		}
		if(moiraLevel === displayLevel && moiraRank < 65536 && result.length >= fillMax){
			return;
		}
		result.push(item);
	});
	return result;
}

function joinNames(list){
	const arr = safeList(list).map(formatGodName).filter(Boolean);
	return arr.length ? arr.join('、') : '无';
}

function joinMoiraYearItems(items){
	return safeList(items).map((item)=>{
		if(item && typeof item === 'object'){
			return [item.name, item.star ? `化${item.star}` : ''].filter(Boolean).join(' ');
		}
		return `${item || ''}`;
	}).filter(Boolean).join('、');
}

function formatGodName(name){
	let val = `${name || ''}`.replace(/\s+/g, '');
	if(!val){
		return '';
	}
	val = val.split(/[\/／]/)[0];
	const aliases = {
		天乙贵人: '天贵',
		玉堂贵人: '玉贵',
	};
	return aliases[val] || val;
}

function normDegree(val){
	let deg = Number(val);
	if(!Number.isFinite(deg)){
		return null;
	}
	deg %= 360;
	if(deg < 0){
		deg += 360;
	}
	return deg;
}

function objectLon(obj){
	const raw = obj && (obj.ra !== undefined ? obj.ra : obj.lon);
	const lon = normDegree(raw);
	if(lon !== null){
		return lon;
	}
	const sign = obj && obj.sign ? AstroConst.LIST_SIGNS.indexOf(obj.sign) : -1;
	const signlon = Number(obj && obj.signlon);
	if(sign >= 0 && Number.isFinite(signlon)){
		return normDegree(sign * 30 + signlon);
	}
	return null;
}

function formatSignDegree(lon){
	const deg = normDegree(lon);
	if(deg === null){
		return '';
	}
	const sign = AstroConst.LIST_SIGNS[Math.floor(deg / 30) % 12];
	const parts = splitDegree(deg);
	return `${msg(sign)} ${parts[0]}度${parts[1]}分`;
}

function compactDegree(lon){
	const deg = normDegree(lon);
	if(deg === null){
		return '';
	}
	const one = Math.floor(deg % 30);
	const min = Math.floor(((deg % 30) - one) * 60);
	return `${`${one}`.padStart(2, '0')}.${`${min}`.padStart(2, '0')}`;
}

function speedText(speed){
	const num = Number(speed);
	if(!Number.isFinite(num)){
		return '';
	}
	return `${num > 0 ? '+' : ''}${num.toFixed(4)}`;
}

function planetStatus(obj){
	const speed = Number(obj && obj.lonspeed);
	if(!Number.isFinite(speed)){
		return '顺';
	}
	if(speed < -0.000001){
		return '逆';
	}
	if(Math.abs(speed) < 0.002){
		return '留';
	}
	const limit = MOIRA_SPEED_LIMITS[obj.id];
	if(limit){
		const abs = Math.abs(speed);
		if(abs < limit.slow){
			return '迟';
		}
		if(abs > limit.fast){
			return '速';
		}
	}
	return '顺';
}

function stemBranchForYear(year){
	const num = Number(year);
	if(!Number.isFinite(num)){
		return '';
	}
	const idx = ((num - 1984) % 60 + 60) % 60;
	return STEM_BRANCHES[idx] || '';
}

function yearFromParams(params){
	const raw = params && params.date ? `${params.date}` : '';
	const match = raw.match(/-?\d{3,4}/);
	return match ? Number(match[0]) : new Date().getFullYear();
}

function getChartRoot(result){
	return result || {};
}

function getChart(result){
	const root = getChartRoot(result);
	return root.chart || {};
}

function getBazi(result){
	const root = getChartRoot(result);
	const chart = getChart(root);
	return (chart.nongli && chart.nongli.bazi) || (root.nongli && root.nongli.bazi) || {};
}

function baziStemBranch(result, key, fallbackYear){
	const bazi = getBazi(result);
	const one = bazi[key] || {};
	if(one.text){
		return one.text;
	}
	if(one.stem && one.branch){
		const stem = one.stem.cell || one.stem.name || one.stem.text || one.stem;
		const branch = one.branch.cell || one.branch.name || one.branch.text || one.branch;
		return `${stem || ''}${branch || ''}`;
	}
	return key === 'year' ? stemBranchForYear(fallbackYear) : '';
}

function baziText(result){
	return ['year', 'month', 'day', 'time'].map((key)=>baziStemBranch(result, key, '')).filter(Boolean).join(' ');
}

function lunarText(result){
	const root = getChartRoot(result);
	const chart = getChart(root);
	const nongli = chart.nongli || root.nongli || {};
	return nongli.text || nongli.nongli || nongli.lunar || nongli.lunarText || '';
}

function getZiGods(result){
	const root = getChartRoot(result);
	const chart = getChart(root);
	const rootGods = root.nongli && root.nongli.bazi && root.nongli.bazi.guolaoGods
		? root.nongli.bazi.guolaoGods.ziGods : null;
	const chartGods = chart.nongli && chart.nongli.bazi && chart.nongli.bazi.guolaoGods
		? chart.nongli.bazi.guolaoGods.ziGods : null;
	return chartGods || rootGods || {};
}

function orderGods(list, order){
	const priority = new Map(order.map((name, idx)=>[name, idx]));
	const seen = new Set();
	return safeList(list).map(formatGodName).filter((item)=>{
		if(!item || seen.has(item)){
			return false;
		}
		seen.add(item);
		return true;
	}).sort((a, b)=>{
		const ia = priority.has(a) ? priority.get(a) : 999;
		const ib = priority.has(b) ? priority.get(b) : 999;
		if(ia !== ib){
			return ia - ib;
		}
		return `${a}`.localeCompare(`${b}`, 'zh-Hans-CN');
	});
}

function findChartObject(chart, id){
	return safeList(chart.objects).find((obj)=>obj && obj.id === id);
}

function buildQuickPlanetRows(result, rulePlanets){
	const chart = getChart(result);
	const ruleMap = new Map(safeList(rulePlanets).map((item)=>[item.id, item]));
	return MOIRA_PLANET_ORDER.map((def)=>{
		const obj = findChartObject(chart, def.id);
		const lon = objectLon(obj);
		if(!obj || lon === null){
			return null;
		}
		const rule = ruleMap.get(def.id) || {};
		return {
			id: def.id,
			name: def.name,
			signName: rule.signName || msg(obj.sign) || msg(signFromLon(lon)),
			degree: rule.degreeText || formatSignDegree(lon),
			compactDegree: compactDegree(lon),
			su28: obj.su28 || rule.su28 || '',
			house: rule.moiraHouse || msg(obj.house) || '',
			dignity: rule.dignity || '',
			status: planetStatus(obj),
			speed: speedText(obj.lonspeed),
		};
	}).filter(Boolean);
}

function buildGodRowsFromChart(result, fields){
	const chart = getChart(result);
	const houses = safeList(chart.houses);
	const ziGods = getZiGods(result);
	const ascSignIndex = computeAscSignIndex(result, chart, fields);
	return houses.map((house, idx)=>{
		const sign = signFromLon(house && house.lon);
		const zi = sign ? SZConst.SignZi[sign] : '';
		const one = zi && ziGods ? safeMap(ziGods[zi]) : {};
		return {
			house: houseFullLabel(house, idx, ascSignIndex),
			zi,
			signName: sign ? msg(sign) : '',
			goodGods: orderGods(one.goodGods, MOIRA_BIRTH_GOD_ORDER),
			neutralGods: orderGods(one.neutralGods, MOIRA_BIRTH_GOD_ORDER),
			badGods: orderGods(one.badGods, MOIRA_BIRTH_GOD_ORDER),
			taisuiGods: orderGods(one.taisuiGods, MOIRA_TRANSIT_GOD_ORDER),
		};
	});
}

function buildHouseRowsFromChart(result, fields){
	const chart = getChart(result);
	const ascSignIndex = computeAscSignIndex(result, chart, fields);
	return safeList(chart.houses).map((house, idx)=>{
		const sign = signFromLon(house && house.lon);
		const signIdx = sign ? AstroConst.LIST_SIGNS.indexOf(sign) : -1;
		const area = signIdx >= 0 && SZConst.SZSigns[signIdx] && SZConst.SZSigns[signIdx].length >= 2
			? `${SZConst.SZSigns[signIdx][0]}${SZConst.SZSigns[signIdx][1]}`
			: '';
		return {
			index: idx,
			name: houseFullLabel(house, idx, ascSignIndex),
			zi: sign ? (SZConst.SignZi[sign] || '') : '',
			area,
			signName: sign ? msg(sign) : '',
			moiraStarHouse: msg(house && house.id ? house.id : null) || '',
		};
	});
}

function signIndexFromLon(lon){
	const sign = signFromLon(lon);
	return sign ? AstroConst.LIST_SIGNS.indexOf(sign) : -1;
}

function objectSignIndex(chart, id){
	const obj = findChartObject(chart, id);
	const lon = objectLon(obj);
	return lon === null ? -1 : signIndexFromLon(lon);
}

function localLifeObject(chart, fields){
	const mode = guolaoLifeModeFromFields(fields);
	const life = findChartObject(chart, AstroConst.LIFEMASTERDEG74);
	const asc = findChartObject(chart, AstroConst.ASC);
	const sun = findChartObject(chart, AstroConst.SUN);
	if(mode === GUOLAO_LIFE_MODE_YUMAO || mode === GUOLAO_LIFE_MODE_COTRANS){
		return life || asc || sun || null;
	}
	return asc || life || sun || null;
}

function localLifeSignIndex(chart, fields){
	const life = localLifeObject(chart, fields);
	const lon = objectLon(life);
	return lon === null ? -1 : signIndexFromLon(lon);
}

function localMoiraHouseSign(lifeSignIndex, houseOffset){
	return lifeSignIndex < 0 ? -1 : (lifeSignIndex + houseOffset + 12) % 12;
}

function localSignZi(signIdx){
	const sign = AstroConst.LIST_SIGNS[(signIdx + 12) % 12];
	return sign ? (SZConst.SignZi[sign] || '') : '';
}

function localPlanetCnById(id){
	const row = MOIRA_PLANET_ORDER.find((item)=>item.id === id);
	return row ? row.name : msg(id);
}

function localSignOfCn(chart, name, lifeSignIndex, selfSignIndex, godSigns){
	const houseMap = {
		命: localMoiraHouseSign(lifeSignIndex, 0),
		命宫: localMoiraHouseSign(lifeSignIndex, 0),
		财: localMoiraHouseSign(lifeSignIndex, 1),
		财帛: localMoiraHouseSign(lifeSignIndex, 1),
		兄弟: localMoiraHouseSign(lifeSignIndex, 2),
		田: localMoiraHouseSign(lifeSignIndex, 3),
		田宅: localMoiraHouseSign(lifeSignIndex, 3),
		嗣: localMoiraHouseSign(lifeSignIndex, 4),
		男女: localMoiraHouseSign(lifeSignIndex, 4),
		奴: localMoiraHouseSign(lifeSignIndex, 5),
		奴仆: localMoiraHouseSign(lifeSignIndex, 5),
		妻: localMoiraHouseSign(lifeSignIndex, 6),
		夫妻: localMoiraHouseSign(lifeSignIndex, 6),
		疾: localMoiraHouseSign(lifeSignIndex, 7),
		疾厄: localMoiraHouseSign(lifeSignIndex, 7),
		迁: localMoiraHouseSign(lifeSignIndex, 8),
		迁移: localMoiraHouseSign(lifeSignIndex, 8),
		官: localMoiraHouseSign(lifeSignIndex, 9),
		官禄: localMoiraHouseSign(lifeSignIndex, 9),
		福: localMoiraHouseSign(lifeSignIndex, 10),
		福德: localMoiraHouseSign(lifeSignIndex, 10),
		相: localMoiraHouseSign(lifeSignIndex, 11),
		相貌: localMoiraHouseSign(lifeSignIndex, 11),
		身: selfSignIndex,
	};
	if(Object.prototype.hasOwnProperty.call(houseMap, name)){
		return houseMap[name];
	}
	if(godSigns && godSigns[name] !== undefined){
		return godSigns[name];
	}
	if(MOIRA_PLANET_CN_TO_ID[name]){
		return objectSignIndex(chart, MOIRA_PLANET_CN_TO_ID[name]);
	}
	const signs = ['戌', '酉', '申', '未', '午', '巳', '辰', '卯', '寅', '丑', '子', '亥'];
	const idx = signs.indexOf(name);
	return idx >= 0 ? idx : -1;
}

function localMoiraGodSigns(godRows){
	const res = {};
	safeList(godRows).forEach((row)=>{
		const signIdx = ['戌', '酉', '申', '未', '午', '巳', '辰', '卯', '寅', '丑', '子', '亥'].indexOf(row.zi);
		if(signIdx < 0){
			return;
		}
		['goodGods', 'neutralGods', 'badGods', 'taisuiGods'].forEach((key)=>{
			safeList(row[key]).forEach((name)=>{
				const val = formatGodName(name);
				if(val && res[val] === undefined){
					res[val] = signIdx;
				}
			});
		});
	});
	return res;
}

function localMoiraSuRuler(su){
	if(!su){
		return '';
	}
	if('星房虚昴'.indexOf(su) >= 0){
		return '日';
	}
	if('张心危毕'.indexOf(su) >= 0){
		return '月';
	}
	if('亢牛娄鬼'.indexOf(su) >= 0){
		return '金';
	}
	if('角斗奎井'.indexOf(su) >= 0){
		return '木';
	}
	if('轸壁参箕'.indexOf(su) >= 0){
		return '水';
	}
	if('尾室觜翼'.indexOf(su) >= 0){
		return '火';
	}
	if('氐女胃柳'.indexOf(su) >= 0){
		return '土';
	}
	return '';
}

function localMoiraIsWinter(params){
	const raw = `${params && params.date ? params.date : ''}`.replace(/\//g, '-');
	const month = Number((raw.split('-')[1] || '').replace(/^0+/, ''));
	return month === 11 || month === 12 || month === 1;
}

function localMoiraIsDay(params){
	const hour = Number(`${params && params.time ? params.time : '12:00:00'}`.split(':')[0]);
	return Number.isFinite(hour) ? hour >= 6 && hour < 18 : true;
}

function localMoiraNearSignBoundary(lon){
	if(lon === null){
		return false;
	}
	const val = ((lon % 30) + 30) % 30;
	return val <= 1 || val >= 29;
}

function localMoiraNearSuBoundary(chart, lon){
	if(lon === null){
		return false;
	}
	return safeList(chart && chart.fixedStarSu28).some((item)=>{
		const ra = normDegree(item && item.ra);
		if(ra === null){
			return false;
		}
		const diff = Math.abs(normDegree(lon) - ra);
		return Math.min(diff, 360 - diff) <= 1;
	});
}

function localMoiraLostRulership(chart, subject, lifeSignIndex, selfSignIndex, godSigns){
	const signIdx = localSignOfCn(chart, subject, lifeSignIndex, selfSignIndex, godSigns);
	if(signIdx < 0){
		return false;
	}
	const sign = AstroConst.LIST_SIGNS[signIdx];
	const rulerId = MOIRA_RULER_BY_SIGN[sign];
	const rulerCn = localPlanetCnById(rulerId);
	const rulerSign = objectSignIndex(chart, rulerId);
	if(rulerSign < 0){
		return false;
	}
	const rulerOfRulerSign = localPlanetCnById(MOIRA_RULER_BY_SIGN[AstroConst.LIST_SIGNS[rulerSign]]);
	return rulerOfRulerSign === MOIRA_OVERCOMING[rulerCn];
}

function addLocalMoiraPattern(list, name, level, score, detail, dsl){
	list.push({
		name,
		level,
		score,
		source: 'moira_s.prop-local',
		dsl,
		detail,
	});
}

function buildLocalMoiraPatterns(chartObj, fields, params, godRows){
	const chart = getChart(chartObj);
	const lifeObj = localLifeObject(chart, fields);
	const lifeLon = objectLon(lifeObj);
	const lifeSignIndex = localLifeSignIndex(chart, fields);
	const selfSignIndex = objectSignIndex(chart, AstroConst.MOON);
	const godSigns = localMoiraGodSigns(godRows);
	const signOf = (name)=>localSignOfCn(chart, name, lifeSignIndex, selfSignIndex, godSigns);
	const same = (a, b)=>a >= 0 && b >= 0 && a === b;
	const rel = (base, offset)=>(base + offset + 12) % 12;
	const sun = signOf('日');
	const moon = signOf('月');
	const venus = signOf('金');
	const mercury = signOf('水');
	const darkMoon = signOf('孛');
	const northNode = signOf('罗');
	const guan = signOf('官');
	const fu = signOf('福');
	const patterns = [];
	const isDay = localMoiraIsDay(params);
	const lifeZi = lifeSignIndex >= 0 ? localSignZi(lifeSignIndex) : '';

	if(lifeSignIndex >= 0 && lifeZi && ('戌亥'.indexOf(lifeZi) >= 0)){
		const diseaseRulerCn = localPlanetCnById(MOIRA_RULER_BY_SIGN[AstroConst.LIST_SIGNS[signOf('疾')]]);
		if(same(signOf(diseaseRulerCn), lifeSignIndex)){
			addLocalMoiraPattern(patterns, '八杀朝天', 'good', '3.2.0', '政余喜格：疾厄宫主入命，且命临戌亥。', '@{@{疾厄}[1]}=@命');
		}
	}
	const moonSign = moon;
	if(moonSign >= 0){
		const sameMoonSignCount = MOIRA_PLANET_ORDER
			.map((item)=>objectSignIndex(chart, item.id))
			.filter((idx)=>idx === moonSign).length;
		if(!isDay && sameMoonSignCount === 1){
			addLocalMoiraPattern(patterns, '孤月独明', 'good', '2.3.0', '政余喜格：夜生月曜独居一方。', '?{孤月} & ?夜');
		}
	}
	if(same(sun, rel(guan, 4)) && same(moon, rel(guan, -4)) || same(sun, rel(guan, -4)) && same(moon, rel(guan, 4))){
		addLocalMoiraPattern(patterns, '日月拱官', 'good', '2.3.0', '政余喜格：日月分拱官禄。', '@日=@官禄+4 & @月=@官禄-4');
	}
	if(same(venus, mercury) && !localMoiraIsWinter(params)){
		addLocalMoiraPattern(patterns, '金水相涵', 'good', '2.3.0', '政余喜格：金水同宫，且不以冬令破格。', '?{金水会} & !?冬');
	}
	const noble = signOf(isDay ? '天贵' : '玉贵');
	if(same(sun, rel(noble, 4)) && same(moon, rel(noble, -4)) || same(sun, rel(noble, -4)) && same(moon, rel(noble, 4))){
		addLocalMoiraPattern(patterns, '日月拱贵人', 'good', '2.2.0', `政余喜格：${isDay ? '昼取天贵' : '夜取玉贵'}，日月分拱。`, '?昼/夜 & 日月拱贵人');
	}
	if(same(lifeSignIndex, signOf('岁驾'))){
		addLocalMoiraPattern(patterns, '命登岁驾', 'good', '2.0.3', '政余喜格：命度临岁驾。', '@命=@{岁驾}');
	}
	if(sun >= 0 && moon >= 0){
		const sunZi = localSignZi(sun);
		const moonZi = localSignZi(moon);
		if(('申酉戌亥子丑'.indexOf(sunZi) >= 0) && ('寅卯辰巳午未'.indexOf(moonZi) >= 0)){
			addLocalMoiraPattern(patterns, '日月失所', 'bad', '2.3.0', '政余忌格：日居西北、月居东南。', '(?{日西}|?{日北}) & (?{月东}|?{月南})');
		}
	}
	if(localMoiraLostRulership(chart, '官', lifeSignIndex, selfSignIndex, godSigns) && localMoiraLostRulership(chart, '福', lifeSignIndex, selfSignIndex, godSigns)){
		addLocalMoiraPattern(patterns, '官福失垣', 'bad', '2.2.0', '政余忌格：官禄、福德主失垣。', '?{官失垣} & ?{福失垣}');
	}
	if(same(darkMoon, sun)){
		addLocalMoiraPattern(patterns, '孛犯太阳', 'bad', '2.2.0', '政余忌格：孛与太阳同宫。', '?{日孛遇}');
	}
	if(same(northNode, sun)){
		addLocalMoiraPattern(patterns, '罗犯太阳', 'bad', '2.2.0', '政余忌格：罗与太阳同宫。', '?{日罗遇}');
	}
	if(same(northNode, darkMoon)){
		addLocalMoiraPattern(patterns, '孛罗交战', 'bad', '2.2.0', '政余忌格：罗孛同宫。', '?{罗孛遇}');
	}
	if(localMoiraNearSignBoundary(lifeLon) || localMoiraNearSuBoundary(chart, lifeLon)){
		addLocalMoiraPattern(patterns, '命坐两歧', 'bad', '2.0.4', '政余忌格：命度近宫界或宿界。', '?{命宫歧} | ?{命宿歧}');
	}
	return patterns.sort((a, b)=>{
		const la = a.level === 'good' ? 0 : (a.level === 'bad' ? 1 : 2);
		const lb = b.level === 'good' ? 0 : (b.level === 'bad' ? 1 : 2);
		return la - lb;
	});
}

function buildLocalMoiraRules(params, chartObj, fields, reason){
	const godHits = buildGodRowsFromChart(chartObj, fields);
	const patterns = buildLocalMoiraPatterns(chartObj, fields, params, godHits);
	return {
		engine: 'horosa-local-moira-panel-fallback',
		engineLabel: 'Moira政余格局（本地规则）',
		summary: `本地已接入 Moira 政余格局规则：命中喜格 ${patterns.filter((item)=>item.level === 'good').length} 条、忌格 ${patterns.filter((item)=>item.level === 'bad').length} 条。`,
		styleSource: 'moira-dsl-local-evaluated',
		styleWarning: '',
		params: {
			...(params || {}),
		},
		anchors: {},
		houses: buildHouseRowsFromChart(chartObj, fields),
		planets: [],
		patterns,
		godHits,
		fallbackReason: reason ? `${reason}` : '',
	};
}

function normalizeGodRows(rows, order){
	return safeList(rows).filter(Boolean).map((row)=>({
		...row,
		goodGods: orderGods(row.goodGods, order),
		neutralGods: orderGods(row.neutralGods, order),
		badGods: orderGods(row.badGods, order),
		taisuiGods: orderGods(row.taisuiGods, MOIRA_TRANSIT_GOD_ORDER),
	}));
}

function aspectName(deg){
	const val = AstroText.AstroMsg[`Asp${deg}`] || AstroText.AstroTxtMsg[`Asp${deg}`] || '';
	return val || `${deg}度`;
}

function buildAspectRows(aspects){
	const normal = aspects && aspects.normalAsp ? aspects.normalAsp : aspects;
	const rows = [];
	if(!normal || typeof normal !== 'object'){
		return rows;
	}
	Object.keys(normal).forEach((key)=>{
		const bucket = normal[key] || {};
		[
			['Applicative', '入相'],
			['Exact', '精确'],
			['Separative', '离相'],
			['None', '容许'],
		].forEach(([field, state])=>{
			safeList(bucket[field]).forEach((asp, idx)=>{
				if(!asp || !asp.id){
					return;
				}
				rows.push({
					key: `${key}-${asp.id}-${field}-${idx}`,
					from: msg(key),
					to: msg(asp.id),
					aspect: aspectName(asp.asp),
					state,
					orb: Number.isFinite(Number(asp.orb)) ? `${Math.round(Number(asp.orb) * 1000) / 1000}` : '',
				});
			});
		});
	});
	return rows;
}

function clonePlain(obj){
	if(obj === undefined || obj === null){
		return obj;
	}
	try{
		return JSON.parse(JSON.stringify(obj));
	}catch(e){
		return obj;
	}
}

function swapGuolaoNodeId(id){
	if(id === AstroConst.NORTH_NODE){
		return AstroConst.SOUTH_NODE;
	}
	if(id === AstroConst.SOUTH_NODE){
		return AstroConst.NORTH_NODE;
	}
	return id;
}

function swapGuolaoNodeIdsDeep(value, seen){
	if(value === undefined || value === null){
		return value;
	}
	if(typeof value === 'string'){
		return swapGuolaoNodeId(value);
	}
	if(typeof value !== 'object'){
		return value;
	}
	const visited = seen || new Set();
	if(visited.has(value)){
		return value;
	}
	visited.add(value);
	if(Array.isArray(value)){
		for(let i = 0; i < value.length; i++){
			value[i] = swapGuolaoNodeIdsDeep(value[i], visited);
		}
		return value;
	}
	const keys = Object.keys(value);
	const entries = keys.map((key)=>[swapGuolaoNodeId(key), swapGuolaoNodeIdsDeep(value[key], visited)]);
	keys.forEach((key)=>delete value[key]);
	entries.forEach(([key, val])=>{
		value[key] = val;
	});
	return value;
}

function guolaoNodeModeFromFields(fields){
	if(fields && fields.guolaoNodeMode && fields.guolaoNodeMode.value !== undefined && fields.guolaoNodeMode.value !== null){
		return normalizeGuolaoNodeMode(fields.guolaoNodeMode.value);
	}
	return getStoredGuolaoNodeMode();
}

function guolaoNodeModeName(mode){
	const normalized = normalizeGuolaoNodeMode(mode);
	return normalized === GUOLAO_NODE_MODE_NORTH_RAHU ? '北罗南计' : '北计南罗';
}

function applyGuolaoNodeMode(chartObj, fields){
	const next = clonePlain(chartObj);
	if(!next){
		return next;
	}
	if(guolaoNodeModeFromFields(fields) === GUOLAO_NODE_MODE_NORTH_RAHU){
		swapGuolaoNodeIdsDeep(next);
	}
	return next;
}

const GUOLAO_RISE_SET_KEYS = {
	sunrise: true,
	sunRise: true,
	sunriseTime: true,
	sunRiseTime: true,
	sun_rise: true,
	guolaoSunRiseTime: true,
	sunset: true,
	sunSet: true,
	sunsetTime: true,
	sunSetTime: true,
	sun_set: true,
	moonrise: true,
	moonRise: true,
	moonriseTime: true,
	moonRiseTime: true,
	moon_rise: true,
	moonset: true,
	moonSet: true,
	moonsetTime: true,
	moonSetTime: true,
	moon_set: true,
};

function hasGuolaoRiseSetFields(value, seen){
	if(value === undefined || value === null){
		return false;
	}
	if(typeof value !== 'object'){
		return false;
	}
	const visited = seen || new Set();
	if(visited.has(value)){
		return false;
	}
	visited.add(value);
	const keys = Object.keys(value);
	for(let i = 0; i < keys.length; i++){
		const key = keys[i];
		const item = value[key];
		if(GUOLAO_RISE_SET_KEYS[key] && item !== undefined && item !== null && `${item}`.trim()){
			return true;
		}
		if(item && typeof item === 'object' && hasGuolaoRiseSetFields(item, visited)){
			return true;
		}
	}
	return false;
}

function pushCache(map, key, val, max = GUOLAO_CACHE_MAX){
	if(!map || !key || val === undefined || val === null){
		return;
	}
	if(map.has(key)){
		map.delete(key);
	}
	map.set(key, val);
	if(map.size > max){
		const first = map.keys().next().value;
		if(first){
			map.delete(first);
		}
	}
}

function normalizeDateText(val){
	const raw = `${val || ''}`.trim();
	if(!raw){
		return '';
	}
	const one = raw.indexOf(' ') >= 0 ? raw.split(' ')[0] : raw;
	return one.replace(/-/g, '/');
}

function normalizeTimeText(val){
	const raw = `${val || ''}`.trim();
	if(!raw){
		return '';
	}
	const one = raw.indexOf(' ') >= 0 ? raw.split(' ')[1] : raw;
	if(/^\d{2}:\d{2}$/.test(one)){
		return `${one}:00`;
	}
	return one;
}

function normalizeNumText(val, defVal = 0){
	const num = Number(val);
	if(!Number.isFinite(num)){
		return `${defVal}`;
	}
	return `${num}`;
}

function normalizeGpsText(val){
	const num = Number(val);
	if(!Number.isFinite(num)){
		return '';
	}
	return `${Math.round(num * 1000000) / 1000000}`;
}

function normalizeChartParams(input){
	const src = input || {};
	const birth = `${src.birth || ''}`.trim();
	const birthParts = birth ? birth.split(' ') : [];
	const birthDate = birthParts[0] || '';
	const birthTime = birthParts[1] || '';
	return {
		date: normalizeDateText(src.date || birthDate),
		time: normalizeTimeText(src.time || birthTime || '00:00:00'),
		ad: normalizeNumText(src.ad, 1),
		zone: `${src.zone || ''}`,
		lon: `${src.lon || ''}`,
		lat: `${src.lat || ''}`,
		gpsLon: normalizeGpsText(src.gpsLon),
		gpsLat: normalizeGpsText(src.gpsLat),
		hsys: normalizeNumText(src.hsys, 0),
		zodiacal: normalizeNumText(src.zodiacal, 0),
		tradition: normalizeNumText(src.tradition, 0),
		doubingSu28: normalizeNumText(src.doubingSu28, 0),
		guolaoZhengSidereal: normalizeNumText(src.guolaoZhengSidereal, 0),
		guolaoLifeMode: normalizeGuolaoLifeMode(src.guolaoLifeMode),
		strongRecption: normalizeNumText(src.strongRecption, 0),
		simpleAsp: normalizeNumText(src.simpleAsp, 0),
		virtualPointReceiveAsp: normalizeNumText(src.virtualPointReceiveAsp, 0),
		predictive: normalizeNumText(src.predictive, 0),
		_su28Rev: src._su28Rev || GUOLAO_SU28_CACHE_REV,
	};
}

function buildGuolaoKey(input){
	try{
		return JSON.stringify(normalizeChartParams(input));
	}catch(e){
		return '';
	}
}

function isChartObjMatchParams(chartObj, params){
	if(!chartObj || !chartObj.params || !params){
		return false;
	}
	const chartKey = buildGuolaoKey(chartObj.params);
	const paramKey = buildGuolaoKey(params);
	return !!chartKey && chartKey === paramKey;
}

async function fetchGuolaoChartCached(params, options){
	const opt = options || {};
	const key = buildGuolaoKey(params);
	const disableCache = opt.cache === false;
	if(!disableCache && key && guolaoMem.has(key)){
		const cached = guolaoMem.get(key);
		if(hasGuolaoRiseSetFields(cached)){
			return clonePlain(cached);
		}
		guolaoMem.delete(key);
	}
	if(!disableCache && key && guolaoInflight.has(key)){
		const inflight = await guolaoInflight.get(key);
		return clonePlain(inflight);
	}
	const req = request(`${Constants.ServerRoot}/chart`, {
		body: JSON.stringify(params),
		silent: opt.silent !== false,
	}).then((data)=>{
		const result = data && data[Constants.ResultKey] ? data[Constants.ResultKey] : null;
		if(!disableCache && key && result){
			pushCache(guolaoMem, key, clonePlain(result));
		}
		return result;
	}).finally(()=>{
		if(!disableCache && key){
			guolaoInflight.delete(key);
		}
	});
	if(!disableCache && key){
		guolaoInflight.set(key, req);
	}
	const result = await req;
	return clonePlain(result);
}

function buildGuolaoSnapshotText(params, result){
	const lines = [];
	const chart = result && result.chart ? result.chart : {};
	const houses = chart.houses || [];
	const objects = chart.objects || [];
	const signsRA = result && result.signsRA ? result.signsRA : [];
	const ziGods = result && result.nongli && result.nongli.bazi && result.nongli.bazi.guolaoGods
		? result.nongli.bazi.guolaoGods.ziGods : null;

	lines.push('[起盘信息]');
	lines.push(`日期：${params.date} ${params.time}`);
	lines.push(`时区：${params.zone}`);
	lines.push(`经纬度：${params.lon} ${params.lat}`);

	lines.push('');
	lines.push('[宫位与星体]');
	houses.forEach((house, idx)=>{
		lines.push(`宫位：${msg(house.id) || `第${idx + 1}宫`}`);
		const inHouse = objects.filter((obj)=>obj.house === house.id);
		if(inHouse.length === 0){
			lines.push('星体：无');
			lines.push('');
			return;
		}
		inHouse.forEach((obj)=>{
			const sd = splitDegree(obj.signlon);
			const su28 = obj.su28 ? `，宿:${obj.su28}` : '';
			lines.push(`星体：${msg(obj.id)} ${sd[0]}˚${msg(obj.sign)}${sd[1]}分${su28}`);
		});
		lines.push('');
	});

	if(signsRA.length){
		lines.push('');
		lines.push('[宫位二十八宿]');
		signsRA.forEach((sig)=>{
			lines.push(`${msg(sig.id)}：赤经${Math.round(sig.ra * 1000) / 1000}`);
		});
	}

	if(ziGods){
		lines.push('');
		lines.push('[神煞]');
		Object.keys(ziGods).forEach((zi)=>{
			const one = ziGods[zi] || {};
			const all = orderGods(one.allGods || [], MOIRA_BIRTH_GOD_ORDER);
			const tai = orderGods(one.taisuiGods || [], MOIRA_TRANSIT_GOD_ORDER);
			lines.push(`${zi}：神煞=${all.join('、') || '无'}；太岁神=${tai.join('、') || '无'}`);
		});
	}
	return lines.join('\n');
}

function buildGuolaoSuSection(result, planetDisplay){
	const chart = result && result.chart ? result.chart : {};
	const suHouses = chart && chart.fixedStarSu28 ? chart.fixedStarSu28 : [];
	const objects = chart && chart.objects ? chart.objects : [];
	const lines = [];
	let visibleSet = null;
	if(planetDisplay && planetDisplay.length){
		visibleSet = new Set(planetDisplay);
	}

	suHouses.forEach((su)=>{
		lines.push(`${su.name}`);
		let inSu = objects.filter((obj)=>{
			if(obj.su28 !== su.name){
				return false;
			}
			if(visibleSet){
				return visibleSet.has(obj.id);
			}
			return AstroConst.isTraditionPlanet(obj.id);
		});
		inSu = inSu.sort((a, b)=>{
			if(a.ra > 300 && b.ra < 30){
				return -1;
			}
			return a.ra - b.ra;
		});
		if(inSu.length === 0){
			lines.push('星体：无');
			lines.push('');
			return;
		}
		inSu.forEach((obj)=>{
			let radeg = Number(obj.ra) - Number(su.ra);
			if(Number.isNaN(radeg)){
				radeg = Number(obj.signlon);
			}
			if(radeg < 0){
				radeg += 360;
			}
			const sd = splitDegree(radeg);
			lines.push(`星体：${msg(obj.id)} ${sd[0]}˚${obj.su28}${sd[1]}分`);
		});
		lines.push('');
	});

	return lines.join('\n').trim();
}

function signFromLon(lon){
	if(lon === undefined || lon === null || Number.isNaN(Number(lon))){
		return null;
	}
	let val = Number(lon) % 360;
	if(val < 0){
		val += 360;
	}
	const idx = Math.floor(val / 30) % 12;
	return AstroConst.LIST_SIGNS[idx];
}

function guolaoLifeModeFromFields(fields){
	if(fields && fields.guolaoLifeMode && fields.guolaoLifeMode.value !== undefined && fields.guolaoLifeMode.value !== null){
		return normalizeGuolaoLifeMode(fields.guolaoLifeMode.value);
	}
	return getStoredGuolaoLifeMode();
}

function guolaoLifeModeName(mode){
	const normalized = normalizeGuolaoLifeMode(mode);
	if(normalized === GUOLAO_LIFE_MODE_YUMAO){
		return '遇卯安命';
	}
	if(normalized === GUOLAO_LIFE_MODE_COTRANS){
		return '赤黄转换';
	}
	return '占星上升';
}

function resolveHouseStartMode(fields){
	if(fields && fields.houseStartMode && fields.houseStartMode.value !== undefined && fields.houseStartMode.value !== null){
		return parseInt(fields.houseStartMode.value, 10) === SZConst.SZHouseStart_ASC
			? SZConst.SZHouseStart_ASC : SZConst.SZHouseStart_Bazi;
	}
	return SZConst.SZHouseStart_Bazi;
}

function computeAscSignIndex(result, chart, fields){
	const objects = chart && chart.objects ? chart.objects : [];
	const asc = objects.find((obj)=>obj.id === AstroConst.ASC);
	const sun = objects.find((obj)=>obj.id === AstroConst.SUN);
	if(!asc){
		return -1;
	}
	const ascIdx = Math.floor(Number(asc.ra) / 30);
	const mode = resolveHouseStartMode(fields);
	if(mode === SZConst.SZHouseStart_ASC){
		return ascIdx;
	}
	const bazi = (chart && chart.nongli && chart.nongli.bazi)
		|| (result && result.nongli && result.nongli.bazi);
	if(!bazi || !sun){
		return ascIdx;
	}
	const timezi = bazi.time && bazi.time.branch ? bazi.time.branch.cell : null;
	const timesig = timezi ? SZConst.ZiSign[timezi] : null;
	const tmsigidx = timesig ? AstroConst.LIST_SIGNS.indexOf(timesig) : -1;
	if(tmsigidx < 0){
		return ascIdx;
	}
	const sunidx = Math.floor(Number(sun.ra) / 30);
	return (sunidx - tmsigidx - 5 + 24) % 12;
}

function houseFullLabel(house, idx, ascSignIndex){
	let houseName = msg(house && house.id ? house.id : null) || `第${idx + 1}宫`;
	const sign = signFromLon(house ? house.lon : null);
	if(!sign){
		return houseName;
	}
	const signIdx = AstroConst.LIST_SIGNS.indexOf(sign);
	if(signIdx >= 0 && ascSignIndex >= 0){
		const hnum = (signIdx - ascSignIndex + 12) % 12 + 1;
		houseName = `第${hnum}宫`;
	}
	const zi = SZConst.SignZi[sign] || '';
	const area = (SZConst.SZSigns[signIdx] && SZConst.SZSigns[signIdx].length >= 2)
		? `${SZConst.SZSigns[signIdx][0]}${SZConst.SZSigns[signIdx][1]}`
		: '';
	const signName = AstroText.AstroMsgCN[sign] || msg(sign);
	return `${zi}—${area}—${signName}座—${houseName}`;
}

function buildHouseSuAndGodsSection(result, planetDisplay, fields){
	const chart = result && result.chart ? result.chart : {};
	const houses = chart && chart.houses ? chart.houses : [];
	const objects = chart && chart.objects ? chart.objects : [];
	const ascSignIndex = computeAscSignIndex(result, chart, fields);
	let visibleSet = null;
	if(planetDisplay && planetDisplay.length){
		visibleSet = new Set(planetDisplay);
	}
	const lines = [];

	houses.forEach((house, idx)=>{
		lines.push(`宫位：${houseFullLabel(house, idx, ascSignIndex)}`);
		let inHouse = objects.filter((obj)=>{
			if(obj.house !== house.id){
				return false;
			}
			if(visibleSet){
				return visibleSet.has(obj.id);
			}
			return AstroConst.isTraditionPlanet(obj.id);
		});
		inHouse = inHouse.sort((a, b)=>{
			if(a.ra > 300 && b.ra < 30){
				return -1;
			}
			return a.ra - b.ra;
		});

		const sign = signFromLon(house.lon);

		if(inHouse.length === 0){
			lines.push('二十八宿：无');
			lines.push('星曜：无');
			lines.push('');
			return;
		}
		const suMap = new Map();
		inHouse.forEach((obj)=>{
			const su = obj.su28 || '未知宿';
			if(!suMap.has(su)){
				suMap.set(su, []);
			}
			suMap.get(su).push(obj);
		});

		const suKeys = Array.from(suMap.keys()).sort((a, b)=>{
			const ia = Su28Helper.Su28.indexOf(a);
			const ib = Su28Helper.Su28.indexOf(b);
			if(ia < 0 && ib < 0){
				return `${a}`.localeCompare(`${b}`);
			}
			if(ia < 0){
				return 1;
			}
			if(ib < 0){
				return -1;
			}
			return ia - ib;
		});

		suKeys.forEach((su)=>{
			const list = suMap.get(su) || [];
			lines.push(`二十八宿：${su}`);
			list.forEach((obj)=>{
				let radeg = Number(obj.ra);
				if(!Number.isNaN(radeg)){
					const suRef = (chart.fixedStarSu28 || []).find((it)=>it.name === su);
					if(suRef && suRef.ra !== undefined && suRef.ra !== null){
						radeg = Number(obj.ra) - Number(suRef.ra);
						if(radeg < 0){
							radeg += 360;
						}
					}else{
						radeg = Number(obj.signlon);
					}
				}else{
					radeg = Number(obj.signlon);
				}
				const sd = splitDegree(radeg);
				lines.push(`星曜：${msg(obj.id)} ${sd[0]}˚${su}${sd[1]}分`);
			});
		});
		lines.push('');
	});
	return lines.join('\n').trim();
}

function buildHouseGodsSection(result, fields){
	const chart = result && result.chart ? result.chart : {};
	const houses = chart && chart.houses ? chart.houses : [];
	const ascSignIndex = computeAscSignIndex(result, chart, fields);
	const rootZiGods = result && result.nongli && result.nongli.bazi && result.nongli.bazi.guolaoGods
		? result.nongli.bazi.guolaoGods.ziGods : null;
	const chartZiGods = chart && chart.nongli && chart.nongli.bazi && chart.nongli.bazi.guolaoGods
		? chart.nongli.bazi.guolaoGods.ziGods : null;
	const ziGods = chartZiGods || rootZiGods || null;
	const lines = [];

	houses.forEach((house, idx)=>{
		lines.push(`宫位：${houseFullLabel(house, idx, ascSignIndex)}`);
		const sign = signFromLon(house.lon);
		const zi = sign ? SZConst.SignZi[sign] : null;
		const gz = ziGods && zi ? ziGods[zi] : null;
		const allGods = orderGods(gz ? []
			.concat(gz.goodGods || [])
			.concat(gz.neutralGods || [])
			.concat(gz.badGods || []) : [], MOIRA_BIRTH_GOD_ORDER);
		const taiGods = orderGods(gz ? (gz.taisuiGods || []) : [], MOIRA_TRANSIT_GOD_ORDER);
		lines.push(`神煞：${allGods.join('、') || '无'}`);
		lines.push(`太岁神：${taiGods.join('、') || '无'}`);
		lines.push('');
	});

	return lines.join('\n').trim();
}

function buildGuolaoSnapshotTextV2(params, result, planetDisplay, fields){
	const lines = [];
	const chart = result && result.chart ? result.chart : {};
	const rootZiGods = result && result.nongli && result.nongli.bazi && result.nongli.bazi.guolaoGods
		? result.nongli.bazi.guolaoGods.ziGods : null;
	const chartZiGods = chart && chart.nongli && chart.nongli.bazi && chart.nongli.bazi.guolaoGods
		? chart.nongli.bazi.guolaoGods.ziGods : null;
	const ziGods = chartZiGods || rootZiGods || null;

	lines.push('[起盘信息]');
	lines.push(`日期：${params.date} ${params.time}`);
	lines.push(`时区：${params.zone}`);
	lines.push(`经纬度：${params.lon} ${params.lat}`);
	lines.push(`七政命度：${guolaoLifeModeName(guolaoLifeModeFromFields(fields))}`);
	lines.push(`罗计：${guolaoNodeModeName(guolaoNodeModeFromFields(fields))}`);
	lines.push('');

	lines.push('[七政四余宫位与二十八宿星曜]');
	lines.push(buildHouseSuAndGodsSection(result, planetDisplay, fields) || '无');
	lines.push('');
	lines.push('[神煞]');
	lines.push(buildHouseGodsSection(result, fields) || '无');
	return lines.join('\n').trim();
}

function fieldsToParams(fields){
	const su28Mode = Number(fields.doubingSu28.value);
	const params = {
		date: fields.date.value.format('YYYY/MM/DD'),
		time: fields.time.value.format('HH:mm:ss'),
		zone: fields.zone.value,
		lat: fields.lat.value,
		lon: fields.lon.value,
		gpsLat: fields.gpsLat.value,
		gpsLon: fields.gpsLon.value,
		hsys: 0,
		zodiacal: su28Mode === GUOLAO_SU28_MODE_ZHENG_SIDEREAL ? 1 : 0,
		tradition: fields.tradition.value,
		doubingSu28: fields.doubingSu28.value,
		guolaoZhengSidereal: su28Mode === GUOLAO_SU28_MODE_ZHENG_SIDEREAL ? 1 : 0,
		guolaoLifeMode: guolaoLifeModeFromFields(fields),
		strongRecption: fields.strongRecption.value,
		simpleAsp: fields.simpleAsp.value,
		virtualPointReceiveAsp: fields.virtualPointReceiveAsp.value,
		predictive: 0,
		name: fields.name.value,
		pos: fields.pos.value,
		_su28Rev: GUOLAO_SU28_CACHE_REV,
	};

	return params;
}

function makeDefaultMoiraTransitTime(fields){
	const tm = new DateTime();
	if(fields && fields.zone && fields.zone.value){
		tm.setZone(fields.zone.value);
	}
	return tm;
}

function paramsWithMoiraTransit(fields, transitTime){
	const params = fieldsToParams(fields);
	const tm = transitTime || makeDefaultMoiraTransitTime(fields);
	if(tm){
		params.date = tm.format('YYYY/MM/DD');
		params.time = tm.format('HH:mm:ss');
		params.ad = tm.ad;
		params.zone = tm.zone || params.zone;
		params.predictive = 1;
	}
	return params;
}


class GuoLaoChartMain extends Component{
	constructor(props) {
		super(props);
		this.state = {
			chartObj: null,
			moiraTransitTime: makeDefaultMoiraTransitTime(props.fields),
			moiraTransitChartObj: null,
			moiraTransitLoading: false,
			tips: null,
			moiraRules: null,
			moiraPanelChartObj: null,
			moiraPanelTransitChartObj: null,
			moiraPanelTransitParams: null,
			moiraLoading: false,
			chartStyle: getStoredGuolaoChartStyle(),
			showMoiraTransitGods: getStoredMoiraTransitGodsVisible(),
			moiraQuickDialog: null,
			moiraStyleLevel: 3,
		};

		this.unmounted = false;
		this.chartReqSeq = 0;
		this.moiraReqSeq = 0;
		this.prefetchTimer = null;
		this.moiraTransitReqSeq = 0;
		this.guolaoDefaultsEnsured = false;

		this.onFieldsChange = this.onFieldsChange.bind(this);
		this.requestChart = this.requestChart.bind(this);
		this.requestChartObj = this.requestChartObj.bind(this);
		this.requestMoiraTransitChart = this.requestMoiraTransitChart.bind(this);
		this.genParams = this.genParams.bind(this);
		this.onTipClick = this.onTipClick.bind(this);
		this.saveGuolaoAISnapshot = this.saveGuolaoAISnapshot.bind(this);
		this.applyChartObj = this.applyChartObj.bind(this);
		this.prefetchChart = this.prefetchChart.bind(this);
		this.requestMoiraRules = this.requestMoiraRules.bind(this);
		this.commitMoiraPanel = this.commitMoiraPanel.bind(this);
		this.ensureGuolaoDefaults = this.ensureGuolaoDefaults.bind(this);
		this.onChartStyleChange = this.onChartStyleChange.bind(this);
		this.onMoiraTransitTimeChange = this.onMoiraTransitTimeChange.bind(this);
		this.onMoiraTransitGodsVisibleChange = this.onMoiraTransitGodsVisibleChange.bind(this);
		this.openMoiraQuickDialog = this.openMoiraQuickDialog.bind(this);
		this.closeMoiraQuickDialog = this.closeMoiraQuickDialog.bind(this);
		this.onMoiraStyleLevelChange = this.onMoiraStyleLevelChange.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (fields, chartObj)=>{
				if(this.unmounted){
					return;
				}
				this.requestChartObj(fields, chartObj);
			};
		}
	}

	onChartStyleChange(val){
		this.setState({
			chartStyle: setStoredGuolaoChartStyle(val),
		}, ()=>{
			if(val === GUOLAO_CHART_STYLE_MOIRA || val === GUOLAO_CHART_STYLE_PICK){
				this.requestMoiraTransitChart();
			}
		});
	}

	onMoiraTransitTimeChange(value){
		const time = value && value.time ? value.time : (value && value.value ? value.value : null);
		if(!time){
			return;
		}
		this.setState({
			moiraTransitTime: time.clone ? time.clone() : time,
		}, ()=>{
			if(!value || value.confirmed !== false){
				this.requestMoiraTransitChart();
			}
		});
	}

	onMoiraTransitGodsVisibleChange(visible){
		this.setState({
			showMoiraTransitGods: setStoredMoiraTransitGodsVisible(visible),
		});
	}

	openMoiraQuickDialog(key){
		this.setState({
			moiraQuickDialog: key,
		});
	}

	closeMoiraQuickDialog(){
		this.setState({
			moiraQuickDialog: null,
		});
	}

	onMoiraStyleLevelChange(event){
		const level = Number(event && event.currentTarget ? event.currentTarget.value : null);
		if(!Number.isFinite(level)){
			return;
		}
		this.setState({
			moiraStyleLevel: level,
		});
	}

	ensureGuolaoDefaults(){
		if(this.guolaoDefaultsEnsured){
			return false;
		}
		if(!this.props.fields || !this.props.dispatch){
			return false;
		}
		this.guolaoDefaultsEnsured = true;
		const su28Mode = getStoredGuolaoSu28Mode();
		const lifeMode = getStoredGuolaoLifeMode();
		const nodeMode = getStoredGuolaoNodeMode();
		const currentSu28 = this.props.fields.doubingSu28 ? Number(this.props.fields.doubingSu28.value) : null;
		const currentLifeMode = guolaoLifeModeFromFields(this.props.fields);
		const currentNodeMode = guolaoNodeModeFromFields(this.props.fields);
		if(currentSu28 === su28Mode && currentLifeMode === lifeMode && currentNodeMode === nodeMode){
			return false;
		}
		const patch = {};
		if(currentSu28 !== su28Mode){
			patch.doubingSu28 = {
				value: su28Mode,
			};
		}
		if(currentLifeMode !== lifeMode){
			patch.guolaoLifeMode = {
				value: lifeMode,
			};
		}
		if(currentNodeMode !== nodeMode){
			patch.guolaoNodeMode = {
				value: nodeMode,
			};
		}
		this.onFieldsChange(patch);
		return true;
	}

	applyChartObj(params, chartObj){
		if(!params || !chartObj || this.unmounted){
			return;
		}
		const key = buildGuolaoKey(params);
		if(key){
			pushCache(guolaoMem, key, clonePlain(chartObj));
		}
		const displayChartObj = applyGuolaoNodeMode(chartObj, this.props.fields);
		this.setState({
			chartObj: displayChartObj,
		});
		this.saveGuolaoAISnapshot(params, displayChartObj);
		this.requestMoiraTransitChart(params, displayChartObj);
	}

	commitMoiraPanel(rules, params, chartObj, transitParams, transitChartObj){
		const nextTransitParams = transitParams || paramsWithMoiraTransit(this.props.fields, this.state.moiraTransitTime);
		this.setState({
			moiraRules: rules,
			moiraPanelChartObj: clonePlain(chartObj),
			moiraPanelTransitChartObj: clonePlain(transitChartObj || this.state.moiraTransitChartObj),
			moiraPanelTransitParams: clonePlain(nextTransitParams),
			moiraLoading: false,
		});
	}

	async requestMoiraRules(params, chartObj, transitParams, transitChartObj){
		if(!params || !chartObj || this.unmounted){
			return;
		}
		const seq = ++this.moiraReqSeq;
		this.setState({
			moiraLoading: true,
		});
		let rsp = null;
		let fallbackReason = 'empty-response';
		try{
			rsp = await fetchMoiraQizhengRules({
				params: params,
				chartObj: chartObj,
				transitParams: transitParams || paramsWithMoiraTransit(this.props.fields, this.state.moiraTransitTime),
				transitChartObj: transitChartObj || this.state.moiraTransitChartObj || null,
			}, {
				silent: true,
				timeoutMs: 12000,
			});
		}catch(e){
			fallbackReason = e && e.message ? e.message : 'request-error';
		}
		if(this.unmounted || seq !== this.moiraReqSeq){
			return;
		}
		const remoteRules = rsp && rsp[Constants.ResultKey] ? rsp[Constants.ResultKey] : null;
		const rules = isIncompleteMoiraRules(remoteRules)
			? buildLocalMoiraRules(params, chartObj, this.props.fields, fallbackReason)
			: remoteRules;
		this.commitMoiraPanel(rules, params, chartObj, transitParams, transitChartObj);
	}

	async prefetchChart(params){
		if(!params){
			return null;
		}
		return fetchGuolaoChartCached(params, {
			silent: true,
		});
	}

	async requestMoiraTransitChart(baseParams, baseChartObj){
		if(!this.props.fields || this.unmounted){
			return null;
		}
		const params = paramsWithMoiraTransit(this.props.fields, this.state.moiraTransitTime);
		if(baseParams){
			params.lon = baseParams.lon;
			params.lat = baseParams.lat;
			params.gpsLon = baseParams.gpsLon;
			params.gpsLat = baseParams.gpsLat;
			params.doubingSu28 = baseParams.doubingSu28;
			params.guolaoZhengSidereal = baseParams.guolaoZhengSidereal;
			params.zodiacal = baseParams.zodiacal;
			params.guolaoLifeMode = baseParams.guolaoLifeMode;
			params.tradition = baseParams.tradition;
			params.strongRecption = baseParams.strongRecption;
			params.simpleAsp = baseParams.simpleAsp;
			params.virtualPointReceiveAsp = baseParams.virtualPointReceiveAsp;
			params._su28Rev = baseParams._su28Rev || GUOLAO_SU28_CACHE_REV;
		}
		const seq = ++this.moiraTransitReqSeq;
		this.setState({
			moiraTransitLoading: true,
			moiraLoading: true,
		});
		try{
			const result = await fetchGuolaoChartCached(params, {
				silent: true,
			});
			if(this.unmounted || seq !== this.moiraTransitReqSeq){
				return result;
			}
			const displayResult = applyGuolaoNodeMode(result, this.props.fields);
			const rootParams = baseParams || this.genParams();
			const rootChartObj = baseChartObj || this.state.chartObj || applyGuolaoNodeMode(this.props.value, this.props.fields);
			if(!rootParams || !rootChartObj){
				this.setState({
					moiraTransitChartObj: displayResult,
					moiraTransitLoading: false,
					moiraLoading: false,
				});
				return result;
			}
			this.setState({
				moiraTransitChartObj: displayResult,
				moiraTransitLoading: false,
			});
			this.requestMoiraRules(rootParams, rootChartObj, params, displayResult);
			return result;
		}catch(e){
			if(!this.unmounted && seq === this.moiraTransitReqSeq){
				const rootParams = baseParams || this.genParams();
				const rootChartObj = baseChartObj || this.state.chartObj || applyGuolaoNodeMode(this.props.value, this.props.fields);
				this.setState({
					moiraTransitLoading: false,
				});
				if(rootParams && rootChartObj){
					this.requestMoiraRules(rootParams, rootChartObj, params, null);
				}else {
					this.setState({
						moiraLoading: false,
					});
				}
			}
			return null;
		}
	}

	async requestChart(params, options){
		if(!params){
			return null;
		}
		const opt = options || {};
		const applyResult = opt.applyResult !== false;
		if(!applyResult){
			return this.prefetchChart(params);
		}
		const seq = ++this.chartReqSeq;
		const result = await fetchGuolaoChartCached(params, {
			silent: opt.silent !== false,
		});
		if(!result || this.unmounted || seq !== this.chartReqSeq){
			return result;
		}
		this.applyChartObj(params, result);
		return result;
	}

	saveGuolaoAISnapshot(params, result){
		const p = params || this.genParams();
		const r = result || this.state.chartObj;
		if(!p || !r){
			return;
		}
		saveModuleAISnapshot('guolao', buildGuolaoSnapshotTextV2(p, r, this.props.planetDisplay, this.props.fields), {
			date: p.date,
			time: p.time,
			zone: p.zone,
			lon: p.lon,
			lat: p.lat,
		});
	}

	requestChartObj(fields, chartObj){
		let params = null;
		if(fields){
			params = fieldsToParams(fields);
		}else{
			params = this.genParams();
		}
		if(!params){
			return;
		}
		const srcChart = chartObj || this.props.value;
		if(srcChart && isChartObjMatchParams(srcChart, params)){
			if(hasGuolaoRiseSetFields(srcChart)){
				this.applyChartObj(params, srcChart);
				return;
			}
		}
		if(srcChart && !this.state.chartObj){
			this.setState({
				chartObj: clonePlain(srcChart),
			});
		}
		this.requestChart(params, {
			silent: true,
		});
	}

	genParams(){
		let fields = this.props.fields;
		let params = fieldsToParams(fields);
		return params;
	}

	onFieldsChange(field){
		if(this.props.dispatch && this.props.fields){
			const patch = {
				...(field || {}),
			};
			const hasConfirmedFlag = Object.prototype.hasOwnProperty.call(patch, '__confirmed');
			const confirmed = hasConfirmedFlag ? !!patch.__confirmed : true;
			if(hasConfirmedFlag){
				delete patch.__confirmed;
			}
			if(patch.doubingSu28 && Object.prototype.hasOwnProperty.call(patch.doubingSu28, 'value')){
				patch.doubingSu28 = {
					...patch.doubingSu28,
					value: setStoredGuolaoSu28Mode(patch.doubingSu28.value),
				};
			}
			if(patch.guolaoLifeMode && Object.prototype.hasOwnProperty.call(patch.guolaoLifeMode, 'value')){
				patch.guolaoLifeMode = {
					...patch.guolaoLifeMode,
					value: setStoredGuolaoLifeMode(patch.guolaoLifeMode.value),
				};
			}
			if(patch.guolaoNodeMode && Object.prototype.hasOwnProperty.call(patch.guolaoNodeMode, 'value')){
				patch.guolaoNodeMode = {
					...patch.guolaoNodeMode,
					value: setStoredGuolaoNodeMode(patch.guolaoNodeMode.value),
				};
			}
			let flds = {
				fields: {
					...this.props.fields,
					...patch,
					nohook: false,
				}
			};
			if(!confirmed){
				this.props.dispatch({
					type: 'astro/fetchByFields',
					payload: {
						...flds.fields,
						nohook: true,
						__requestOptions: {
							silent: true,
						},
					},
				});
				if(this.prefetchTimer){
					clearTimeout(this.prefetchTimer);
				}
				this.prefetchTimer = setTimeout(()=>{
					this.prefetchTimer = null;
					if(this.unmounted){
						return;
					}
					this.prefetchChart(fieldsToParams(flds.fields)).catch(()=>{
						return null;
					});
				}, 220);
				return;
			}
			if(this.prefetchTimer){
				clearTimeout(this.prefetchTimer);
				this.prefetchTimer = null;
			}
			this.props.dispatch({
				type: 'astro/fetchByFields',
				payload: {
					...flds.fields,
					__requestOptions: {
						silent: true,
					},
				},
			});
		}
	}

	onTipClick(tipobj){
		this.setState({
			tips: tipobj,
		});
	}

	componentDidMount(){
		this.unmounted = false;
		if(this.ensureGuolaoDefaults()){
			return;
		}
		if(this.props.fields){
			this.requestChartObj();
		}
	}

	componentDidUpdate(prevProps){
		if(prevProps.fields !== this.props.fields && this.ensureGuolaoDefaults()){
			return;
		}
		if(prevProps.planetDisplay !== this.props.planetDisplay){
			this.saveGuolaoAISnapshot(null, this.state.chartObj);
		}
		if(prevProps.value !== this.props.value && this.props.value){
			const params = this.genParams();
			if(isChartObjMatchParams(this.props.value, params)){
				if(hasGuolaoRiseSetFields(this.props.value)){
					this.applyChartObj(params, this.props.value);
				}else {
					this.requestChart(params, {
						silent: true,
					});
				}
			}
		}
	}

	componentWillUnmount(){
		this.unmounted = true;
		this.moiraReqSeq++;
		this.moiraTransitReqSeq++;
		if(this.prefetchTimer){
			clearTimeout(this.prefetchTimer);
			this.prefetchTimer = null;
		}
	}

	renderMoiraSection(title, children, extraClass = ''){
		return (
			<div className={`horosa-guolao-quick-section ${extraClass}`.trim()}>
				<div className="horosa-guolao-quick-section-title">{title}</div>
				{children}
			</div>
		);
	}

	renderMoiraEmpty(text){
		return (
			<div className="horosa-guolao-quick-empty">{text}</div>
		);
	}

	renderQuickMeta(items){
		return (
			<div className="horosa-guolao-quick-meta-grid">
				{items.filter((item)=>item && item.value !== undefined && item.value !== null && item.value !== '').map((item)=>(
					<div className="horosa-guolao-quick-meta" key={item.label}>
						<span>{item.label}</span>
						<strong>{item.value}</strong>
					</div>
				))}
			</div>
		);
	}

	renderQuickPlanetRows(rows){
		if(!rows.length){
			return this.renderMoiraEmpty('当前星历响应里没有可输出的星曜数据。');
		}
		return (
			<div className="horosa-guolao-quick-table horosa-guolao-quick-planet-table">
				<div className="horosa-guolao-quick-table-row horosa-guolao-quick-table-head">
					<span>星曜</span><span>宫位</span><span>黄道</span><span>宿度</span><span>势态</span><span>速度</span>
				</div>
				{rows.map((row)=>(
					<div className="horosa-guolao-quick-table-row" key={row.id}>
						<strong>{row.name}</strong>
						<span>{row.house || '-'}</span>
						<span>{row.degree || row.signName || '-'}</span>
						<span>{row.su28 ? `${row.su28} ${row.compactDegree}` : row.compactDegree}</span>
						<span>{[row.dignity, row.status].filter(Boolean).join(' / ') || '-'}</span>
						<span>{row.speed || '-'}</span>
					</div>
				))}
			</div>
		);
	}

	renderQuickYearPlanetRows(rows){
		const list = safeList(rows);
		if(!list.length){
			return this.renderMoiraEmpty('当前 Moira 规则层未返回化曜数据。');
		}
		return (
			<div className="horosa-guolao-quick-table horosa-guolao-quick-planet-table">
				<div className="horosa-guolao-quick-table-row horosa-guolao-quick-table-head">
					<span>曜</span><span>化曜</span><span>同归项</span><span></span><span></span><span></span>
				</div>
				{list.map((row)=>(
					<div className="horosa-guolao-quick-table-row" key={row.star}>
						<strong>{row.star}</strong>
						<span>{row.changeTo || '-'}</span>
						<span>{joinNames(row.items)}</span>
						<span></span><span></span><span></span>
					</div>
				))}
			</div>
		);
	}

	renderQuickYearGroups(groups){
		const list = safeList(groups);
		if(!list.length){
			return this.renderMoiraEmpty('当前 Moira 规则层未返回天禄至天权数据。');
		}
		return (
			<div className="horosa-guolao-quick-card-grid horosa-guolao-quick-year-grid">
				{list.map((group, idx)=>(
					<div className="horosa-guolao-quick-card" key={`${group.main || 'group'}-${idx}`}>
						<div className="horosa-guolao-quick-card-title">{group.main || '-'}</div>
						<div className="horosa-guolao-quick-card-text">{joinMoiraYearItems(group.items)}</div>
					</div>
				))}
			</div>
		);
	}

	renderQuickYearSignRows(rows){
		const list = safeList(rows);
		if(!list.length){
			return this.renderMoiraEmpty('当前 Moira 规则层未返回命曜数据。');
		}
		return (
			<div className="horosa-guolao-quick-table horosa-guolao-quick-weak-table">
				<div className="horosa-guolao-quick-table-row horosa-guolao-quick-table-head">
					<span>宫名</span><span>化曜</span><span>曜名</span><span>宫性</span>
				</div>
				{list.map((row)=>(
					<div className="horosa-guolao-quick-table-row" key={`${row.mode || 'year'}-${row.name}`}>
						<strong>{row.name}</strong>
						<span>{row.star || '-'}</span>
						<span>{row.shortName || '-'}</span>
						<span>{[row.quality, row.zi, row.signName].filter(Boolean).join(' · ')}</span>
					</div>
				))}
			</div>
		);
	}

		renderQuickPatterns(){
			const rules = this.state.moiraRules || {};
			const unverifiedSource = hasUnverifiedMoiraPatternSource(rules);
			const meta = moiraStyleLevelMeta(rules, this.state.moiraStyleLevel);
			const allPatterns = unverifiedSource ? [] : safeList(rules.patterns);
			const byLevel = applyMoiraStyleLevel(allPatterns, meta);
			const patterns = byLevel;
			const warning = rules.styleWarning || (unverifiedSource ? '当前接口返回的是旧版 Horosa 近似格局，不是 Moira 本体的政余喜格/忌格；已在前端屏蔽，避免误读。' : '');
			const good = patterns.filter((item)=>item.level === 'good');
			const bad = patterns.filter((item)=>item.level === 'bad');
			const other = patterns.filter((item)=>item.level !== 'good' && item.level !== 'bad');
			const renderPatternGroup = (type, label, list, emptyText)=>(
				<div className={`horosa-guolao-quick-pattern-group horosa-guolao-quick-pattern-group-${type}`}>
					<div className="horosa-guolao-quick-pattern-group-head">
						<span>{type === 'good' ? '喜' : '忌'}</span>
						<strong>{label}</strong>
						<em>{list.length} 条</em>
					</div>
					<div className="horosa-guolao-quick-pattern-chip-list">
						{list.length ? list.map((item, idx)=>(
							<span key={`${type}-${item.name}-${idx}`} title={item.detail || item.dsl || item.name}>{item.name}</span>
						)) : <i>{emptyText}</i>}
					</div>
				</div>
			);
			return (
				<div className="horosa-guolao-quick-dialog">
					{warning ? this.renderMoiraSection('格局数据源', (
						<div className="horosa-guolao-quick-warning">{warning}</div>
					)) : null}
					{this.renderMoiraSection('显示程度', (
						<div className="horosa-guolao-quick-meta horosa-guolao-quick-style-level">
							<label>
								<span>最低</span>
								<input
									type="range"
									min={meta.min}
									max={meta.max}
									step="1"
									value={meta.level}
									onInput={this.onMoiraStyleLevelChange}
									onChange={this.onMoiraStyleLevelChange}
									onClick={this.onMoiraStyleLevelChange}
									onMouseUp={this.onMoiraStyleLevelChange}
									onKeyUp={this.onMoiraStyleLevelChange}
								/>
								<span>最高</span>
							</label>
							<div className="horosa-guolao-quick-card-text">
								当前 {meta.level} 档，Moira 阈值 level ≥ {meta.displayLevel}；显示 {patterns.length}/{allPatterns.length} 条命中格局。
							</div>
						</div>
					))}
					<div className="horosa-guolao-quick-pattern-output">
						{renderPatternGroup('good', '政余喜格', good, warning ? 'Moira 真实喜格 DSL 尚未接入，暂不输出正式喜格。' : '当前盘未命中 Moira 喜格。')}
						{renderPatternGroup('bad', '政余忌格', bad, warning ? 'Moira 真实忌格 DSL 尚未接入，暂不输出正式忌格。' : '当前盘未命中 Moira 忌格。')}
					</div>
				{other.length ? this.renderMoiraSection('察看项', (
					<div className="horosa-guolao-quick-card-grid">
						{other.map((item, idx)=>(
							<div className={`horosa-guolao-quick-card horosa-guolao-quick-pattern-${item.level || 'neutral'}`} key={`${item.name}-${idx}`}>
								<div className="horosa-guolao-quick-card-title">{item.name}</div>
								<div className="horosa-guolao-quick-card-text">{item.detail || 'Moira 规则命中，但后端未返回细节。'}</div>
							</div>
						))}
					</div>
				)) : null}
			</div>
		);
	}

	renderQuickYearStars(){
		const birthParams = this.genParams();
		const transitParams = paramsWithMoiraTransit(this.props.fields, this.state.moiraTransitTime);
		const birthYear = yearFromParams(birthParams);
		const transitYear = yearFromParams(transitParams);
		const birthGz = baziStemBranch(this.state.chartObj, 'year', birthYear);
		const transitGz = stemBranchForYear(transitYear);
		const rules = this.state.moiraRules || {};
		const nativeYearStars = safeMap(rules.yearStars);
		const birthYearStars = safeMap(nativeYearStars.birth);
		const transitYearStars = safeMap(nativeYearStars.transit);
		if(safeList(transitYearStars.groups).length || safeList(birthYearStars.groups).length){
			return (
				<div className="horosa-guolao-quick-dialog">
					{this.renderMoiraSection('年曜化星', this.renderQuickMeta([
						{label: '本命年柱', value: birthYearStars.yearPole || birthGz},
						{label: '流年年柱', value: transitYearStars.yearPole || transitGz},
						{label: '流年时间', value: `${transitParams.date} ${transitParams.time}`},
						{label: '本命首曜', value: birthYearStars.yearStar},
						{label: '流年首曜', value: transitYearStars.yearStar},
						{label: '规则源', value: rules.styleSource || 'moira_s.prop'},
					]))}
					{this.renderMoiraSection('流年化曜', this.renderQuickYearPlanetRows(transitYearStars.planetRows))}
					{this.renderMoiraSection('本命化曜', this.renderQuickYearPlanetRows(birthYearStars.planetRows))}
					{this.renderMoiraSection('流年天禄至天权', this.renderQuickYearGroups(transitYearStars.groups))}
				</div>
			);
		}
		const stem = transitGz.slice(0, 1);
		const currentStar = MOIRA_YEAR_STAR_BY_STEM[stem] || '';
		return (
			<div className="horosa-guolao-quick-dialog">
				{this.renderMoiraSection('年曜化星', this.renderQuickMeta([
					{label: '本命年柱', value: birthGz},
					{label: '流年年柱', value: transitGz},
					{label: '流年时间', value: `${transitParams.date} ${transitParams.time}`},
					{label: 'Moira化曜', value: currentStar ? `${stem}年化${currentStar}` : '未取得流年干'},
					{label: '年曜序', value: MOIRA_YEAR_STAR_SEQ.join('、')},
					{label: '年干序', value: MOIRA_YEAR_STAR_MAP.join('、')},
				]))}
				{this.renderMoiraSection('天禄至天权', (
					<div className="horosa-guolao-quick-card-grid horosa-guolao-quick-year-grid">
						{MOIRA_YEAR_INFO_GROUPS.map((items, idx)=>(
							<div className="horosa-guolao-quick-card" key={items[0]}>
								<div className="horosa-guolao-quick-card-title">{items[0]}</div>
								<div className="horosa-guolao-quick-card-text">{items.slice(1).join('、') || '主项'}</div>
								{idx === 0 && currentStar ? <em>本流年化星：{currentStar}</em> : null}
							</div>
						))}
					</div>
				))}
				{this.renderMoiraSection('十神序', this.renderQuickMeta([
					{label: '原十神序', value: MOIRA_TEN_GOD_ORG.join('、')},
					{label: '替代十神序', value: MOIRA_TEN_GOD_ALT.join('、')},
				]))}
			</div>
		);
	}

	renderQuickWeakSolid(){
		const rules = this.state.moiraRules || {};
		const nativeWeakSolid = safeMap(rules.weakSolid);
		const nativeHouseRows = safeList(nativeWeakSolid.houses);
		if(nativeHouseRows.length){
			return (
				<div className="horosa-guolao-quick-dialog">
					{this.renderMoiraSection('虚实宫位', (
						<div className="horosa-guolao-quick-table horosa-guolao-quick-weak-table">
							<div className="horosa-guolao-quick-table-row horosa-guolao-quick-table-head">
								<span>宫位</span><span>虚实</span><span>虚柱</span><span>实柱</span>
							</div>
							{nativeHouseRows.map((house, idx)=>(
								<div className="horosa-guolao-quick-table-row" key={`${house.house}-${idx}`}>
									<strong>{house.house}</strong>
									<span className={house.solid ? 'horosa-guolao-quick-solid' : (house.weak ? 'horosa-guolao-quick-weak' : '')}>{house.label || '-'}</span>
									<span>{joinNames(house.weakPillars)}</span>
									<span>{joinNames(house.solidPillars)}</span>
								</div>
							))}
						</div>
					))}
					{this.renderMoiraSection('Moira口径', this.renderQuickMeta([
						{label: '虚宫', value: '按四柱旬空推虚：Moira computeWeakHouse。'},
						{label: '实宫', value: '按年、月、日、时四柱地支定实。'},
					]))}
				</div>
			);
		}
		const houses = safeList(rules.houses);
		const rows = buildQuickPlanetRows(this.state.chartObj, rules.planets);
		const byHouse = new Map();
		rows.forEach((row)=>{
			const key = row.house || '未定';
			if(!byHouse.has(key)){
				byHouse.set(key, []);
			}
			byHouse.get(key).push(row.name);
		});
		const houseRows = houses.length ? houses : Array.from(byHouse.keys()).map((name)=>({name}));
		return (
			<div className="horosa-guolao-quick-dialog">
				{this.renderMoiraSection('虚实宫位', (
					<div className="horosa-guolao-quick-table horosa-guolao-quick-weak-table">
						<div className="horosa-guolao-quick-table-row horosa-guolao-quick-table-head">
							<span>宫位</span><span>虚实</span><span>星曜</span><span>位置</span>
						</div>
						{houseRows.map((house, idx)=>{
							const stars = byHouse.get(house.name) || [];
							return (
								<div className="horosa-guolao-quick-table-row" key={`${house.name}-${idx}`}>
									<strong>{house.name}</strong>
									<span className={stars.length ? 'horosa-guolao-quick-solid' : 'horosa-guolao-quick-weak'}>{stars.length ? '实' : '虚'}</span>
									<span>{stars.length ? stars.join('、') : '无星曜驻守'}</span>
									<span>{[house.zi, house.area, house.signName].filter(Boolean).join(' · ') || '-'}</span>
								</div>
							);
						})}
						{houseRows.length === 0 ? this.renderMoiraEmpty('当前 Moira 规则层未返回宫位虚实数据。') : null}
					</div>
				))}
				{this.renderMoiraSection('Moira口径', this.renderQuickMeta([
					{label: '虚宫', value: '无七政四余驻守的宫位，按 Moira 虚宫线口径展示。'},
					{label: '实宫', value: '有七政四余驻守的宫位，按 Moira 实宫线口径展示。'},
				]))}
			</div>
		);
	}

	renderQuickNatalStars(){
		const rules = this.state.moiraRules || {};
		const nativeRows = safeList(rules.natalYearStars);
		if(nativeRows.length){
			const anchors = safeMap(rules.anchors);
			return (
				<div className="horosa-guolao-quick-dialog">
					{this.renderMoiraSection('命曜', this.renderQuickYearSignRows(nativeRows))}
					{this.renderMoiraSection('命身锚点', this.renderQuickMeta([
						{label: '命度', value: anchors.life ? [anchors.life.signName, anchors.life.degreeText, anchors.life.zi, anchors.life.moiraHouse, anchors.lifeModeName || rules.lifeModeName].filter(Boolean).join(' · ') : ''},
						{label: '身度', value: anchors.self ? [anchors.self.signName, anchors.self.degreeText, anchors.self.zi, anchors.self.moiraHouse].filter(Boolean).join(' · ') : ''},
						{label: '四柱', value: baziText(this.state.chartObj)},
						{label: '规则源', value: rules.styleSource || 'moira_s.prop'},
					]))}
				</div>
			);
		}
		const rows = buildQuickPlanetRows(this.state.chartObj, rules.planets);
		const anchors = safeMap(rules.anchors);
		return (
			<div className="horosa-guolao-quick-dialog">
				{this.renderMoiraSection('命盘星曜', this.renderQuickPlanetRows(rows))}
				{this.renderMoiraSection('命身锚点', this.renderQuickMeta([
					{label: '命度', value: anchors.life ? [anchors.life.signName, anchors.life.degreeText, anchors.life.zi, anchors.life.moiraHouse, anchors.lifeModeName || rules.lifeModeName].filter(Boolean).join(' · ') : ''},
					{label: '身度', value: anchors.self ? [anchors.self.signName, anchors.self.degreeText, anchors.self.zi, anchors.self.moiraHouse].filter(Boolean).join(' · ') : ''},
					{label: '四柱', value: baziText(this.state.chartObj)},
					{label: '农历', value: lunarText(this.state.chartObj)},
				]))}
			</div>
		);
	}

	renderQuickTransitStars(){
		const rows = buildQuickPlanetRows(this.state.moiraTransitChartObj, []);
		const transitParams = paramsWithMoiraTransit(this.props.fields, this.state.moiraTransitTime);
		const transitYear = yearFromParams(transitParams);
		const rules = this.state.moiraRules || {};
		const nativeRows = safeList(rules.transitYearStars);
		const currentYearStars = safeMap(safeMap(rules.yearStars).transit);
		if(nativeRows.length || safeList(currentYearStars.planetRows).length){
			return (
				<div className="horosa-guolao-quick-dialog">
					{this.renderMoiraSection('流曜', this.state.moiraTransitLoading
						? this.renderMoiraEmpty('流年盘正在计算。')
						: this.renderQuickYearSignRows(nativeRows))}
					{this.renderMoiraSection('流年化曜', this.renderQuickYearPlanetRows(currentYearStars.planetRows))}
					{this.renderMoiraSection('流年参数', this.renderQuickMeta([
						{label: '流年时间', value: `${transitParams.date} ${transitParams.time}`},
						{label: '流年干支', value: currentYearStars.yearPole || stemBranchForYear(transitYear)},
						{label: '规则源', value: rules.styleSource || 'moira_s.prop'},
					]))}
				</div>
			);
		}
		return (
			<div className="horosa-guolao-quick-dialog">
				{this.renderMoiraSection('流曜星体', this.state.moiraTransitLoading
					? this.renderMoiraEmpty('流年盘正在计算。')
					: this.renderQuickPlanetRows(rows))}
				{this.renderMoiraSection('流年参数', this.renderQuickMeta([
					{label: '流年时间', value: `${transitParams.date} ${transitParams.time}`},
					{label: '流年干支', value: stemBranchForYear(transitYear)},
					{label: '流年化曜', value: `${stemBranchForYear(transitYear).slice(0, 1)} → ${MOIRA_YEAR_STAR_BY_STEM[stemBranchForYear(transitYear).slice(0, 1)] || '-'}`},
				]))}
			</div>
		);
	}

	renderQuickAspects(){
		const rows = buildAspectRows(this.state.chartObj && this.state.chartObj.aspects);
		return (
			<div className="horosa-guolao-quick-dialog">
				{this.renderMoiraSection('相位列表', rows.length ? (
					<div className="horosa-guolao-quick-table horosa-guolao-quick-aspect-table">
						<div className="horosa-guolao-quick-table-row horosa-guolao-quick-table-head">
							<span>主星</span><span>相位</span><span>客星</span><span>状态</span><span>误差</span>
						</div>
						{rows.map((row)=>(
							<div className="horosa-guolao-quick-table-row" key={row.key}>
								<strong>{row.from}</strong>
								<span>{row.aspect}</span>
								<span>{row.to}</span>
								<span>{row.state}</span>
								<span>{row.orb || '-'}</span>
							</div>
						))}
					</div>
				) : this.renderMoiraEmpty('当前七政盘没有返回可列出的相位数据。'))}
			</div>
		);
	}

	renderQuickGodRows(rows){
		if(!rows.length){
			return this.renderMoiraEmpty('当前盘没有返回可列出的神煞数据。');
		}
		return (
			<div className="horosa-guolao-quick-god-grid">
				{rows.map((row, idx)=>(
					<div className="horosa-guolao-quick-god-card" key={`${row.house}-${row.zi}-${idx}`}>
							<div className="horosa-guolao-quick-card-title">{row.house || row.zi || `宫位${idx + 1}`}</div>
							<div className="horosa-guolao-quick-card-subtitle">{[row.zi, row.signName].filter(Boolean).join(' · ')}</div>
							{safeList(row.gods).length ? <div><span>曜</span>{joinNames(row.gods)}</div> : (
								<>
									<div><span>吉</span>{joinNames(row.goodGods)}</div>
									<div><span>平</span>{joinNames(row.neutralGods)}</div>
									<div><span>忌</span>{joinNames(row.badGods)}</div>
									<div><span>岁</span>{joinNames(row.taisuiGods)}</div>
								</>
							)}
						</div>
					))}
			</div>
		);
	}

	renderQuickGods(){
		const rules = this.state.moiraRules || {};
		const birthRows = normalizeGodRows(safeList(rules.godHits).length ? rules.godHits : buildGodRowsFromChart(this.state.chartObj, this.props.fields), MOIRA_BIRTH_GOD_ORDER);
		const transitRows = normalizeGodRows(safeList(rules.transitGodHits).length ? rules.transitGodHits : buildGodRowsFromChart(this.state.moiraTransitChartObj, this.props.fields), MOIRA_TRANSIT_GOD_ORDER);
		return (
			<div className="horosa-guolao-quick-dialog">
				{this.renderMoiraSection('本命神煞', this.renderQuickGodRows(birthRows))}
				{this.renderMoiraSection('流年神煞', this.state.moiraTransitLoading ? this.renderMoiraEmpty('流年神煞正在计算。') : this.renderQuickGodRows(transitRows))}
				{this.renderMoiraSection('Moira显示序', this.renderQuickMeta([
					{label: '本命显示序', value: MOIRA_BIRTH_GOD_ORDER.join('、')},
					{label: '流年显示序', value: MOIRA_TRANSIT_GOD_ORDER.join('、')},
				]))}
			</div>
		);
	}

	renderMoiraQuickContent(key){
		if(this.state.moiraLoading && key !== 'transitStars'){
			return this.renderMoiraEmpty('Moira 规则层正在推演，稍后会自动填入。');
		}
		if(key === 'patterns'){
			return this.renderQuickPatterns();
		}
		if(key === 'yearStars'){
			return this.renderQuickYearStars();
		}
		if(key === 'weakSolid'){
			return this.renderQuickWeakSolid();
		}
		if(key === 'natalStars'){
			return this.renderQuickNatalStars();
		}
		if(key === 'transitStars'){
			return this.renderQuickTransitStars();
		}
		if(key === 'aspects'){
			return this.renderQuickAspects();
		}
		if(key === 'gods'){
			return this.renderQuickGods();
		}
		return this.renderMoiraEmpty('请选择一个快捷功能。');
	}

	renderMoiraQuickModal(){
		const key = this.state.moiraQuickDialog;
		const meta = MOIRA_QUICK_ACTIONS.find((item)=>item.key === key);
		return (
			<XQModal
				className="horosa-guolao-quick-modal"
				visible={!!key}
				title={meta ? `Moira ${meta.label}` : 'Moira'}
				width={980}
				footer={null}
				destroyOnClose
				onCancel={this.closeMoiraQuickDialog}
			>
				{this.renderMoiraQuickContent(key)}
			</XQModal>
		);
	}

	renderQuickDock(){
		return (
			<div className="horosa-bottom-quick-dock horosa-guolao-quick-dock">
				<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
				<div className="horosa-bottom-quick-actions horosa-guolao-quick-actions">
					{MOIRA_QUICK_ACTIONS.map((item)=>(
						<button
							type="button"
							className="horosa-bottom-quick-button horosa-guolao-quick-button"
							key={item.key}
							onClick={()=>this.openMoiraQuickDialog(item.key)}
						>
							<span className="horosa-bottom-quick-icon"><XQIcon name={item.icon} /></span>
							<span>{item.label}</span>
						</button>
					))}
				</div>
			</div>
		);
	}

	render(){
		let height = this.props.height ? this.props.height : 760;
		if(height === '100%'){
			height = 'calc(100% - 70px)'
		}else{
			height = height - 20
		}

		let chartObj = this.state.chartObj;
		let chart = chartObj ? chartObj.chart : {};
		chart.aspects = chartObj ? chartObj.aspects : {};
		chart.lots = chartObj ? chartObj.lots : [];
		const useMoiraWheel = this.state.chartStyle === GUOLAO_CHART_STYLE_MOIRA;
		const usePickWheel = this.state.chartStyle === GUOLAO_CHART_STYLE_PICK;
		const useMoiraLikeWheel = useMoiraWheel || usePickWheel;
		const moiraPanelChartObj = this.state.moiraPanelChartObj || chartObj;
		const moiraPanelTransitChartObj = this.state.moiraPanelTransitChartObj || this.state.moiraTransitChartObj;
		const moiraPanelTransitParams = this.state.moiraPanelTransitParams || paramsWithMoiraTransit(this.props.fields, this.state.moiraTransitTime);

		return (
			<div className="horosa-guolao-page horosa-astro-redesign horosa-guolao-redesign">
				<div className="horosa-astro-layout horosa-astro-redesign-layout horosa-guolao-redesign-layout">
					<div className="horosa-astro-redesign-grid horosa-guolao-redesign-grid">
						<div className="horosa-astro-context-panel horosa-astro-input-panel horosa-guolao-input-panel">
							<GuoLaoInput
								fields={this.props.fields}
								onFieldsChange={this.onFieldsChange}
								chartStyle={this.state.chartStyle}
								onChartStyleChange={this.onChartStyleChange}
								moiraTransitTime={this.state.moiraTransitTime}
								onMoiraTransitTimeChange={this.onMoiraTransitTimeChange}
								showMoiraTransitGods={this.state.showMoiraTransitGods}
								onMoiraTransitGodsVisibleChange={this.onMoiraTransitGodsVisibleChange}
							/>
						</div>
						<div className={`horosa-chart-stage horosa-chart-stage-redesign horosa-guolao-chart-panel xq-chart-renderer xq-chart-renderer-guolao${useMoiraLikeWheel ? ' horosa-guolao-chart-panel-moira' : ''}`}>
							{usePickWheel ? (
								<GuoLaoMoiraPickWheel
									rootValue={chartObj}
									value={chart}
									transitValue={this.state.moiraTransitChartObj}
									transitParams={paramsWithMoiraTransit(this.props.fields, this.state.moiraTransitTime)}
									transitLoading={this.state.moiraTransitLoading}
									moiraRules={this.state.moiraRules}
									height={height}
									fields={this.props.fields}
									chartDisplay={this.props.chartDisplay}
									planetDisplay={this.props.planetDisplay}
									onTipClick={this.onTipClick}
								/>
							) : useMoiraWheel ? (
								<GuoLaoMoiraWheel
									rootValue={chartObj}
									value={chart}
									transitValue={this.state.moiraTransitChartObj}
									transitParams={paramsWithMoiraTransit(this.props.fields, this.state.moiraTransitTime)}
									transitLoading={this.state.moiraTransitLoading}
									showMoiraTransitGods={this.state.showMoiraTransitGods}
									moiraRules={this.state.moiraRules}
									height={height}
									fields={this.props.fields}
									chartDisplay={this.props.chartDisplay}
									planetDisplay={this.props.planetDisplay}
									onTipClick={this.onTipClick}
								/>
							) : (
								<GuoLaoChart
									value={chart}
									height={height}
									fields={this.props.fields}
									chartDisplay={this.props.chartDisplay}
									planetDisplay={this.props.planetDisplay}
									onTipClick={this.onTipClick}
								/>
							)}
						</div>
						<div className="horosa-inspector-panel horosa-astro-content-panel horosa-guolao-info-panel">
							<Tabs
								activeKey="moira"
								tabPosition="top"
								className="horosa-content-tabs horosa-guolao-tabs"
							>
								<TabPane tab="Moira" key="moira">
									<GuoLaoMoiraPanel
										value={this.state.moiraRules}
										loading={this.state.moiraLoading}
										rootValue={moiraPanelChartObj}
										transitValue={moiraPanelTransitChartObj}
										transitParams={moiraPanelTransitParams}
										fields={this.props.fields}
										chartMode={usePickWheel ? 'pick' : 'moira'}
									/>
								</TabPane>
							</Tabs>
						</div>
					</div>
					{this.renderQuickDock()}
				</div>
				{this.renderMoiraQuickModal()}
			</div>
		);
	}
}

export default GuoLaoChartMain;
