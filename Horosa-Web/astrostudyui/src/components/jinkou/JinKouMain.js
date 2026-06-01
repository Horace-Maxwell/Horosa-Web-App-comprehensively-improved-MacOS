import { Component } from 'react';
import { message, Modal } from 'antd';
import * as Constants from '../../utils/constants';
import request from '../../utils/request';
import * as LRConst from '../liureng/LRConst';
import { ZSList, ZhangSheng, } from '../liureng/LRZhangSheng';
import LiuRengInput from '../lrzhan/LiuRengInput';
import LiuRengBirthInput from '../lrzhan/LiuRengBirthInput';
import DateTime from '../comp/DateTime';
import JinKouChart from './JinKouChart';
import JinKouRelationMini from './JinKouRelationMini';
import { buildJinKouData, fetchJinKouPan, normalizeKinjinkouData } from './JinKouCalc';
import { resolveJinKouDiFen } from './JinKouState';
import { saveModuleAISnapshot, loadModuleAISnapshot } from '../../utils/moduleAiSnapshot';
import {
	XQButton as Button,
	XQSelect as Select,
	XQTabs as Tabs,
} from '../xq-ui';
import {
	getBirthGanzhiLocalCache,
	getLiurengRunyearLocalCache,
	setBirthGanzhiLocalCache,
	setLiurengRunyearLocalCache,
} from '../../utils/localCalcCache';
import XQIcon from '../xq-icons';
import { defaultAfter23NewDay, defaultLateZiHourUseNextDay } from '../../utils/dayBoundary';

const { Option } = Select;
const TabPane = Tabs.TabPane;

function cloneDateTimeSafe(val, fallback){
	if(val && val instanceof DateTime){
		return val.clone();
	}
	if(fallback && fallback instanceof DateTime){
		return fallback.clone();
	}
	return new DateTime();
}

function buildBirthFields(source, fallbackNow){
	const now = fallbackNow && fallbackNow instanceof DateTime ? fallbackNow : new DateTime();
	const src = source || {};
	const dateVal = src.date && src.date.value ? cloneDateTimeSafe(src.date.value, now.startOf('date')) : now.startOf('date');
	const timeVal = src.time && src.time.value ? cloneDateTimeSafe(src.time.value, now) : now.clone();
	return {
		date: { value: dateVal },
		time: { value: timeVal },
		ad: { value: src.ad && src.ad.value !== undefined ? src.ad.value : now.ad },
		zone: { value: src.zone && src.zone.value ? src.zone.value : now.zone },
		lat: { value: src.lat && src.lat.value ? src.lat.value : Constants.DefLat },
		lon: { value: src.lon && src.lon.value ? src.lon.value : Constants.DefLon },
		gpsLat: { value: src.gpsLat && src.gpsLat.value !== undefined ? src.gpsLat.value : Constants.DefGpsLat },
		gpsLon: { value: src.gpsLon && src.gpsLon.value !== undefined ? src.gpsLon.value : Constants.DefGpsLon },
		gender: { value: src.gender && src.gender.value !== undefined ? src.gender.value : 1 },
		after23NewDay: { value: src.after23NewDay && src.after23NewDay.value !== undefined ? src.after23NewDay.value : defaultAfter23NewDay() },
		lateZiHourUseNextDay: { value: src.lateZiHourUseNextDay && src.lateZiHourUseNextDay.value !== undefined ? src.lateZiHourUseNextDay.value : defaultLateZiHourUseNextDay() },
	};
}

function fmtValue(value){
	if(value === undefined || value === null || value === ''){
		return '无';
	}
	if(value instanceof Array){
		return value.join('、') || '无';
	}
	return `${value}`;
}

function cleanKey(key){
	const txt = `${key || ''}`;
	const idx = txt.indexOf('(');
	if(idx >= 0){
		return txt.substring(0, idx);
	}
	return txt;
}

function appendMapSection(lines, title, obj){
	lines.push(`[${title}]`);
	if(!obj || typeof obj !== 'object'){
		lines.push('无');
		lines.push('');
		return;
	}
	const keys = Object.keys(obj);
	if(keys.length === 0){
		lines.push('无');
		lines.push('');
		return;
	}
	for(let i=0; i<keys.length; i++){
		const key = keys[i];
		lines.push(`${cleanKey(key)}：${fmtValue(obj[key])}`);
	}
	lines.push('');
}

function extractGanZi(text){
	const raw = `${text || ''}`.trim();
	if(raw.length < 2){
		return '';
	}
	if(LRConst.GanList.indexOf(raw.substr(0, 1)) >= 0 && LRConst.ZiList.indexOf(raw.substr(1, 1)) >= 0){
		return raw.substr(0, 2);
	}
	for(let i=0; i<raw.length - 1; i++){
		const gan = raw.substr(i, 1);
		const zi = raw.substr(i + 1, 1);
		if(LRConst.GanList.indexOf(gan) >= 0 && LRConst.ZiList.indexOf(zi) >= 0){
			return gan + zi;
		}
	}
	return '';
}

function resolveGuaYearGanZi(liureng){
	if(!liureng){
		return '';
	}
	const fourYear = liureng.fourColumns ? liureng.fourColumns.year : null;
	if(fourYear){
		if(typeof fourYear === 'string'){
			const got = extractGanZi(fourYear);
			if(got){
				return got;
			}
		}else if(fourYear.ganzi){
			const got = extractGanZi(fourYear.ganzi);
			if(got){
				return got;
			}
		}
	}
	const nongli = liureng.nongli ? liureng.nongli : {};
	const fallback = [
		nongli.yearGanZi,
		nongli.yearJieqi,
		nongli.year,
	];
	for(let i=0; i<fallback.length; i++){
		const got = extractGanZi(fallback[i]);
		if(got){
			return got;
		}
	}
	return '';
}

const JiaZiList = (()=>{
	const list = [];
	for(let i=0; i<60; i++){
		list.push(`${LRConst.GanList[i % 10]}${LRConst.ZiList[i % 12]}`);
	}
	return list;
})();

function buildRunYearList(startGanZi, delta){
	const list = [];
	let idx = JiaZiList.indexOf(startGanZi);
	if(idx < 0){
		return list;
	}
	for(let i=0; i<60; i++){
		list.push(JiaZiList[idx]);
		idx = (idx + delta + 60) % 60;
	}
	return list;
}

const MaleRunYearList = buildRunYearList('丙寅', 1);
const FemaleRunYearList = buildRunYearList('壬申', -1);

function resolveCycleYear(ganzi, approxYear){
	const idx = JiaZiList.indexOf(ganzi);
	if(idx < 0){
		return approxYear;
	}
	const base = 1984 + idx; // 1984 = 甲子
	const k = Math.floor((approxYear - base) / 60);
	const c1 = base + k * 60;
	const c2 = c1 + 60;
	return Math.abs(c2 - approxYear) < Math.abs(c1 - approxYear) ? c2 : c1;
}

function calcRunYearLocal(birthGanZi, guaGanZi, gender, birthYear, guaYear){
	const bIdx = JiaZiList.indexOf(extractGanZi(birthGanZi));
	const gIdx = JiaZiList.indexOf(extractGanZi(guaGanZi));
	if(bIdx < 0 || gIdx < 0){
		return null;
	}
	const ageCycle = (gIdx - bIdx + 60) % 60;
	let age = ageCycle;
	if(Number.isFinite(birthYear) && Number.isFinite(guaYear)){
		const bSolar = resolveCycleYear(JiaZiList[bIdx], birthYear);
		const gSolar = resolveCycleYear(JiaZiList[gIdx], guaYear);
		const diff = gSolar - bSolar;
		if(diff >= 0){
			age = diff;
		}
	}
	const male = `${gender}` !== '0';
	const yearList = male ? MaleRunYearList : FemaleRunYearList;
	return {
		age,
		ageCycle,
		year: yearList[ageCycle] || '',
	};
}

function getSolarYearFromField(field){
	if(!field || !field.value){
		return NaN;
	}
	const dt = field.value;
	const y = Number(dt.year);
	if(!Number.isFinite(y)){
		return NaN;
	}
	const ad = Number(dt.ad || 1);
	return ad >= 0 ? y : -y;
}

function buildFallbackRunYearByYearDiff(birth, guaFields){
	const birthYear = getSolarYearFromField(birth && birth.date ? birth.date : null);
	const guaYear = getSolarYearFromField(guaFields && guaFields.date ? guaFields.date : null);
	if(!Number.isFinite(birthYear) || !Number.isFinite(guaYear) || guaYear < birthYear){
		return null;
	}
	const genderVal = birth && birth.gender ? birth.gender.value : 1;
	const age = guaYear - birthYear;
	const ageCycle = ((age % 60) + 60) % 60;
	const yearList = `${genderVal}` === '0' ? FemaleRunYearList : MaleRunYearList;
	return {
		age: age,
		ageCycle: ageCycle,
		year: yearList[ageCycle] || '',
	};
}

function resolveDisplayRunYear(runyear, birth, guaFields){
	const fallback = buildFallbackRunYearByYearDiff(birth, guaFields);
	if(!fallback){
		return runyear;
	}
	const currAge = runyear && runyear.age !== undefined && runyear.age !== null ? Number(runyear.age) : NaN;
	const currAgeCycle = runyear && runyear.ageCycle !== undefined && runyear.ageCycle !== null ? Number(runyear.ageCycle) : NaN;
	const currYear = runyear && runyear.year ? `${runyear.year}` : '';
	const ageDelta = Number.isFinite(currAge) ? Math.abs(currAge - fallback.age) : NaN;
	const cycleDelta = Number.isFinite(currAgeCycle)
		? Math.min(Math.abs(currAgeCycle - fallback.ageCycle), 60 - Math.abs(currAgeCycle - fallback.ageCycle))
		: NaN;
	const hardMismatch = (Number.isFinite(ageDelta) && ageDelta >= 2)
		|| (Number.isFinite(cycleDelta) && cycleDelta >= 2);
	const sameAgeYearMismatch = Number.isFinite(currAge)
		&& currAge === fallback.age
		&& currYear !== ''
		&& fallback.year !== ''
		&& currYear !== fallback.year;
	const useFallback = !runyear
		|| !Number.isFinite(currAge)
		|| (currAge === 0 && fallback.age > 0)
		|| currYear === ''
		|| (currYear === '丙寅' && fallback.age > 0)
		|| hardMismatch
		|| sameAgeYearMismatch;
	if(!useFallback){
		return runyear;
	}
	return {
		...(runyear || {}),
		...fallback,
	};
}

export function buildJinKouSnapshotText(params, liureng, runyear, jinkouData, wuxing, guirengType, gender){
	const lines = [];
	const nongli = liureng && liureng.nongli ? liureng.nongli : {};
	const xingbie = `${gender}` === '1' ? '男' : '女';
	const guirenType = jinkouData && jinkouData.source === 'kinjinkou' ? 'kinjinkou 贵人歌诀' : (guirengType === 0 ? '六壬法贵人' : (guirengType === 1 ? '遁甲法贵人' : '星占法贵人'));
	const briefKong = (txt)=>{
		const val = `${txt || ''}`;
		const hasEmpty = val.indexOf('空亡') >= 0;
		const hasSiKong = val.indexOf('四大空亡') >= 0;
		if(hasEmpty && hasSiKong){
			return '空&四空';
		}
		if(hasEmpty){
			return '空';
		}
		if(hasSiKong){
			return '四空';
		}
		return '';
	};
	const findRow = (name)=>{
		if(!jinkouData || !jinkouData.rows){
			return null;
		}
		for(let i=0; i<jinkouData.rows.length; i++){
			const row = jinkouData.rows[i];
			if(row && row.label === name){
				return row;
			}
		}
		return null;
	};
	const appendBriefRow = (name, withShenjiang)=>{
		const row = findRow(name);
		if(!row){
			lines.push(`${name}：无`);
			return;
		}
		const main = fmtValue(row.content);
		const shenjiang = withShenjiang && row.shenjiang && row.shenjiang !== '-' ? `（${row.shenjiang}）` : '';
		const power = row.power && row.power !== '—' ? row.power : '无';
		const kong = briefKong(row.kong);
		let line = `${name}：${main}${shenjiang}；（${power}）`;
		if(kong){
			line = `${line}；${kong}`;
		}
		lines.push(line);
	};

	lines.push('[起盘信息]');
	if(params){
		lines.push(`日期：${params.date} ${params.time}`);
		lines.push(`时区：${params.zone}`);
		lines.push(`经纬度：${params.lon} ${params.lat}`);
	}
	if(nongli && nongli.birth){
		lines.push(`真太阳时：${nongli.birth}`);
	}
	if(liureng && liureng.fourColumns){
		const cols = liureng.fourColumns;
		lines.push(`四柱：${fmtValue(cols.year && cols.year.ganzi)}年 ${fmtValue(cols.month && cols.month.ganzi)}月 ${fmtValue(cols.day && cols.day.ganzi)}日 ${fmtValue(cols.time && cols.time.ganzi)}时`);
	}
	lines.push(`贵人体系：${guirenType}`);
	lines.push(`十二长生五行：${fmtValue(wuxing)}`);
	lines.push(`问测人性别：${xingbie}`);
	lines.push('');

	lines.push('[金口诀速览]');
	if(jinkouData && jinkouData.ready){
		lines.push(`地分：${fmtValue(jinkouData.topInfo.diFen)}`);
		lines.push(`空亡：${fmtValue(jinkouData.topInfo.xunKong)}`);
		lines.push(`四大空亡：${fmtValue(jinkouData.topInfo.siDaKong)}`);
		if(jinkouData.yongYao && jinkouData.yongYao.label){
			lines.push(`用爻：${jinkouData.yongYao.label}${jinkouData.yongYao.sign ? `(${jinkouData.yongYao.sign})` : ''}`);
		}
		appendBriefRow('人元', false);
		appendBriefRow('贵神', true);
		appendBriefRow('将神', true);
		appendBriefRow('地分', false);
	}else{
		lines.push('无');
	}
	lines.push('');

	lines.push('[金口诀四位]');
	if(jinkouData && jinkouData.ready){
		lines.push(`地分：${fmtValue(jinkouData.topInfo.diFen)}`);
		lines.push(`空亡：${fmtValue(jinkouData.topInfo.xunKong)}`);
		lines.push(`四大空亡：${fmtValue(jinkouData.topInfo.siDaKong)}`);
		if(jinkouData.yongYao && jinkouData.yongYao.label){
			lines.push(`用爻判定：${jinkouData.yongYao.reason || ''}；取${jinkouData.yongYao.label}${jinkouData.yongYao.sign ? `(${jinkouData.yongYao.sign})` : ''}`);
		}
		for(let i=0; i<jinkouData.rows.length; i++){
			const row = jinkouData.rows[i];
			const nayin = row.nayin ? `；纳音=${fmtValue(row.nayin)}` : '';
			lines.push(`${row.label}：天干=${fmtValue(row.gan)}；内容=${fmtValue(row.content)}；神将=${fmtValue(row.shenjiang)}；状态=${fmtValue(row.power)}；空亡=${fmtValue(row.kong)}${nayin}`);
		}
	}else{
		lines.push('无');
	}
	lines.push('');

	lines.push('[金口诀三盘]');
	if(jinkouData && jinkouData.ready && jinkouData.plates && jinkouData.plates.length){
		for(let i=0; i<jinkouData.plates.length; i++){
			const row = jinkouData.plates[i];
			lines.push(`${fmtValue(row.di)}：天盘=${fmtValue(row.tian)}；将神=${fmtValue(row.jiang)}；神盘=${fmtValue(row.shen)}；贵神=${fmtValue(row.gui)}`);
		}
	}else{
		lines.push('无');
	}
	lines.push('');

	lines.push('[四位神煞]');
	if(jinkouData && jinkouData.shenshaRows && jinkouData.shenshaRows.length){
		for(let i=0; i<jinkouData.shenshaRows.length; i++){
			const row = jinkouData.shenshaRows[i];
			lines.push(`${row.label}：${fmtValue(row.value)}`);
		}
	}else{
		lines.push('无');
	}
	lines.push('');

	lines.push('[用神强弱]');
	lines.push(jinkouData && jinkouData.yongStrength ? jinkouData.yongStrength.text : '无');
	lines.push('');

	lines.push('[四位生克]');
	if(jinkouData && jinkouData.relations && jinkouData.relations.length){
		for(let i=0; i<jinkouData.relations.length; i++){
			const r = jinkouData.relations[i];
			lines.push(`${r.from}${r.rel}${r.to}：${r.text || ''}`);
		}
	}else{
		lines.push('无');
	}
	lines.push('');

	lines.push('[应期]');
	if(jinkouData && jinkouData.yingQi){
		lines.push(`${jinkouData.yingQi.scope}：${jinkouData.yingQi.text}`);
	}else{
		lines.push('无');
	}
	lines.push('');

	lines.push('[地支关系]');
	if(jinkouData && jinkouData.branchRelations && jinkouData.branchRelations.length){
		for(let i=0; i<jinkouData.branchRelations.length; i++){
			const b = jinkouData.branchRelations[i];
			lines.push(`${b.aLabel}${b.a} ${b.type} ${b.bLabel}${b.b}`);
		}
	}else{
		lines.push('无');
	}
	lines.push('');

	lines.push('[相关神煞]');
	if(jinkouData && jinkouData.relevantShensha && jinkouData.relevantShensha.length){
		for(let i=0; i<jinkouData.relevantShensha.length; i++){
			const it = jinkouData.relevantShensha[i];
			lines.push(`${it.position}·${it.name}：${it.desc || ''}`);
		}
	}else{
		lines.push('无');
	}
	lines.push('');

	lines.push('[分类用神·求财]');
	if(jinkouData && jinkouData.categoryRules){
		const qc = jinkouData.categoryRules.filter((c)=>c.texts && c.texts.length);
		if(qc.length){
			for(let i=0; i<qc.length; i++){
				lines.push(`${qc[i].name}（用神：${qc[i].yongHint || ''}）`);
				for(let j=0; j<qc[i].texts.length; j++){
					lines.push(`- ${qc[i].texts[j]}`);
				}
			}
		}else{
			lines.push('细则完善中');
		}
	}else{
		lines.push('无');
	}
	lines.push('');

	lines.push('[行年]');
	if(runyear){
		lines.push(`行年干支：${fmtValue(runyear.year)}`);
		lines.push(`年龄：${fmtValue(runyear.age)}岁`);
		lines.push(`性别：${xingbie}`);
	}else{
		lines.push('无');
	}
	lines.push('');

	appendMapSection(lines, '旬日', liureng ? liureng.xun : null);
	appendMapSection(lines, '旺衰', liureng ? liureng.season : null);
	appendMapSection(lines, '基础神煞', liureng ? liureng.gods : null);
	appendMapSection(lines, '干煞', liureng ? liureng.godsGan : null);
	appendMapSection(lines, '月煞', liureng ? liureng.godsMonth : null);
	appendMapSection(lines, '支煞', liureng ? liureng.godsZi : null);
	appendMapSection(lines, '岁煞', liureng && liureng.godsYear ? liureng.godsYear.taisui1 : null);

	lines.push('[十二长生]');
	if(wuxing){
		for(let i=0; i<ZSList.length; i++){
			const item = ZSList[i];
			const key = `${wuxing}_${item}`;
			lines.push(`${item}：${fmtValue(ZhangSheng.wxphase[key])}`);
		}
	}else{
		lines.push('无');
	}
	return lines.join('\n').trim();
}

function mapObjToRows(obj){
	if(!obj || typeof obj !== 'object'){
		return [];
	}
	const keys = Object.keys(obj);
	const rows = [];
	for(let i=0; i<keys.length; i++){
		const key = keys[i];
		let value = obj[key];
		if(value instanceof Array){
			value = value.join('、');
		}
		rows.push({
			key: cleanKey(key),
			value: value === undefined || value === null || value === '' ? '—' : `${value}`,
		});
	}
	return rows;
}

function normalizeZiFromText(text){
	const txt = `${text || ''}`;
	for(let i=0; i<txt.length; i++){
		const one = txt.substr(i, 1);
		if(LRConst.ZiList.indexOf(one) >= 0){
			return one;
		}
	}
	return '';
}

function resolveChartIsDiurnal(chartObj){
	if(chartObj === undefined || chartObj === null){
		return null;
	}
	const chart = chartObj.chart ? chartObj.chart : chartObj;
	if(chart && typeof chart.isDiurnal === 'boolean'){
		return chart.isDiurnal;
	}
	return null;
}

function getAppliedBirth(state){
	if(state && state.calcBirth){
		return state.calcBirth;
	}
	return state ? state.birth : null;
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

function buildCacheKey(obj){
	try{
		return JSON.stringify(obj || {});
	}catch(e){
		return '';
	}
}

function pushCache(map, key, val, max = 96){
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

class JinKouMain extends Component{
	constructor(props) {
		super(props);
		const now = new DateTime();
		const birth = buildBirthFields(this.props.fields, now);

		this.state = {
			birth: birth,
			calcBirth: birth,
			liureng: null,
			runyear: null,
			wuxing: '土',
			guireng: 0,
			diFen: '子',
			diFenAuto: true,
			yueJiang: 'auto',
			zhanShi: 'auto',
			timeBasis: 'direct',
			jinkouPan: null,
			jinkouError: '',
			rightPanelTab: 'overview',
			rightTab: 'godsZi',
			analysisTab: 'basic',
			auxTab: 'category',
			calcFields: null,
			calcIsDiurnal: null,
		};

		this.unmounted = false;
		this.birthYearGanZiCache = {};
		this.godsCache = new Map();
		this.godsInflight = new Map();
		this.runYearServerCache = new Map();
		this.runYearServerInflight = new Map();

		this.onFieldsChange = this.onFieldsChange.bind(this);
		this.onBirthChange = this.onBirthChange.bind(this);
		this.onWuXingChange = this.onWuXingChange.bind(this);
		this.onGuiRengChange = this.onGuiRengChange.bind(this);
		this.onDiFenChange = this.onDiFenChange.bind(this);
		this.onYueJiangChange = this.onYueJiangChange.bind(this);
		this.onZhanShiChange = this.onZhanShiChange.bind(this);
		this.onTimeBasisChange = this.onTimeBasisChange.bind(this);
		this.setRightPanelTab = this.setRightPanelTab.bind(this);
		this.setRightTab = this.setRightTab.bind(this);
		this.setAnalysisTab = this.setAnalysisTab.bind(this);
		this.setAuxTab = this.setAuxTab.bind(this);
		this.navigateFeature = this.navigateFeature.bind(this);
		this.genWuXingDoms = this.genWuXingDoms.bind(this);
		this.genGodsParams = this.genGodsParams.bind(this);
		this.genRunYearParams = this.genRunYearParams.bind(this);
		this.requestGods = this.requestGods.bind(this);
		this.requestRunYear = this.requestRunYear.bind(this);
		this.requestBirthYearGanZi = this.requestBirthYearGanZi.bind(this);
		this.saveJinKouSnapshot = this.saveJinKouSnapshot.bind(this);
		this.clickSaveCase = this.clickSaveCase.bind(this);
		this.renderInfoTable = this.renderInfoTable.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (fields, chartObj)=>{
				if(this.unmounted){
					return;
				}
				this.requestGods(fields || this.props.fields, chartObj || this.props.value);
			};
		}
	}

	onFieldsChange(field){
		const patch = {
			...(field || {}),
		};
		const hasConfirmedFlag = Object.prototype.hasOwnProperty.call(patch, '__confirmed');
		const confirmed = hasConfirmedFlag ? !!patch.__confirmed : true;
		if(hasConfirmedFlag && !confirmed){
			return;
		}
		if(hasConfirmedFlag){
			delete patch.__confirmed;
		}
		// 用户拍板: 左栏改过 after23NewDay 后,全局事件不再覆盖。
		if(field && Object.prototype.hasOwnProperty.call(field, 'after23NewDay')){
			this._after23BoundaryUserOverrode = true;
			if(this.props.dispatch){
				this.props.dispatch({ type: 'astro/setAfter23BoundaryUserOverrode', payload: { value: true } });
			}
		}
		// v2.2.1: 时柱开关同款局部覆盖 — 同时设本地 flag 和 dva 中央 flag
		if(field && Object.prototype.hasOwnProperty.call(field, 'lateZiHourUseNextDay')){
			this._lateZiHourUserOverrode = true;
			if(this.props.dispatch){
				this.props.dispatch({ type: 'astro/setLateZiHourUserOverrode', payload: { value: true } });
			}
		}
		if(this.props.dispatch && this.props.fields){
			const flds = {
				...this.props.fields,
				...patch,
			};
			this.props.dispatch({
				type: 'astro/fetchByFields',
				payload: {
					...flds,
					__requestOptions: {
						silent: true,
					},
					nohook: !confirmed,
				},
			});
		}
	}

	onBirthChange(field){
		const patch = {
			...(field || {}),
		};
		if(Object.prototype.hasOwnProperty.call(patch, '__confirmed')){
			delete patch.__confirmed;
		}
		const flds = {
			...this.state.birth,
			...patch,
		};
		this.setState({
			birth: flds,
		});
	}

	onWuXingChange(val){
		this.setState({
			wuxing: val,
		}, ()=>{
			this.saveJinKouSnapshot(null, this.state.liureng, this.state.runyear, val, this.state.guireng, this.state.diFen);
		});
	}

	onGuiRengChange(val){
		this.setState({
			guireng: val,
		}, ()=>{
			this.saveJinKouSnapshot(null, this.state.liureng, this.state.runyear, this.state.wuxing, val, this.state.diFen);
		});
	}

	onDiFenChange(val){
		this.setState({
			diFen: val,
			diFenAuto: false,
		}, ()=>{
			if(this.state.liureng){
				this.requestGods(this.state.calcFields || this.props.fields, this.props.value);
			}else{
				this.saveJinKouSnapshot(null, this.state.liureng, this.state.runyear, this.state.wuxing, this.state.guireng, val);
			}
		});
	}

	onYueJiangChange(val){
		this.setState({
			yueJiang: val,
		}, ()=>{
			if(this.state.liureng){
				this.requestGods(this.state.calcFields || this.props.fields, this.props.value);
			}
		});
	}

	onZhanShiChange(val){
		this.setState({
			zhanShi: val,
		}, ()=>{
			if(this.state.liureng){
				this.requestGods(this.state.calcFields || this.props.fields, this.props.value);
			}
		});
	}

	onTimeBasisChange(val){
		this.setState({
			timeBasis: val,
		}, ()=>{
			if(this.state.liureng){
				this.requestGods(this.state.calcFields || this.props.fields, this.props.value);
			}
		});
	}

	setRightTab(key){
		this.setState({
			rightTab: key,
		});
	}

	setRightPanelTab(key){
		this.setState({
			rightPanelTab: key,
		});
	}

	setAnalysisTab(key){
		this.setState({ analysisTab: key });
	}

	setAuxTab(key){
		this.setState({ auxTab: key });
	}

	navigateFeature(tabKey, subTab){
		if(this.props.dispatch){
			const payload = {
				currentTab: tabKey,
			};
			if(subTab){
				payload.currentSubTab = subTab;
			}
			this.props.dispatch({
				type: 'astro/save',
				payload,
			});
		}
	}

	genRunYearParams(){
		const flds = getAppliedBirth(this.state);
		const calcFields = this.state.calcFields ? this.state.calcFields : this.props.fields;
		const guaDate = calcFields && calcFields.date && calcFields.date.value ? calcFields.date.value.format('YYYY-MM-DD') : '';
		const guaTime = calcFields && calcFields.time && calcFields.time.value ? calcFields.time.value.format('HH:mm') : '';
		const guaAd = calcFields && calcFields.ad && calcFields.ad.value !== undefined
			? calcFields.ad.value
			: (calcFields && calcFields.date && calcFields.date.value ? calcFields.date.value.ad : 1);
		const guaZone = calcFields && calcFields.zone && calcFields.zone.value
			? calcFields.zone.value
			: (calcFields && calcFields.date && calcFields.date.value ? calcFields.date.value.zone : '');
		const guaLon = calcFields && calcFields.lon ? calcFields.lon.value : '';
		const guaLat = calcFields && calcFields.lat ? calcFields.lat.value : '';
		const guaAfter23 = calcFields && calcFields.after23NewDay && calcFields.after23NewDay.value !== undefined
			? calcFields.after23NewDay.value
			: 0;
		const lateZiVal = flds.lateZiHourUseNextDay && flds.lateZiHourUseNextDay.value !== undefined
			? flds.lateZiHourUseNextDay.value
			: defaultLateZiHourUseNextDay();
		return {
			ad: flds.date.value.ad,
			date: flds.date.value.format('YYYY-MM-DD'),
			time: flds.time.value.format('HH:mm'),
			zone: flds.date.value.zone,
			lon: flds.lon.value,
			lat: flds.lat.value,
			gender: flds.gender.value,
			after23NewDay: flds.after23NewDay.value,
			lateZiHourUseNextDay: lateZiVal,
			guaYearGanZi: resolveGuaYearGanZi(this.state.liureng),
			guaDate: guaDate,
			guaTime: guaTime,
			guaAd: guaAd,
			guaZone: guaZone,
			guaLon: guaLon,
			guaLat: guaLat,
			guaAfter23NewDay: guaAfter23,
		};
	}

	genGodsParams(fields){
		let params = null;
		const flds = fields ? fields : this.props.fields;
		const after23 = flds.after23NewDay && flds.after23NewDay.value !== undefined ? flds.after23NewDay.value : defaultAfter23NewDay();
		const lateZi = flds.lateZiHourUseNextDay && flds.lateZiHourUseNextDay.value !== undefined ? flds.lateZiHourUseNextDay.value : defaultLateZiHourUseNextDay();
		if(flds.params){
			const dtparts = flds.params.birth.split(' ');
			params = {
				...flds.params,
				date: dtparts[0],
				time: dtparts[1],
				after23NewDay: flds.params.after23NewDay !== undefined ? flds.params.after23NewDay : after23,
				lateZiHourUseNextDay: flds.params.lateZiHourUseNextDay !== undefined ? flds.params.lateZiHourUseNextDay : lateZi,
			};
		}else{
			params = {
				date: flds.date.value.format('YYYY-MM-DD'),
				time: flds.time.value.format('HH:mm'),
				zone: flds.date.value.zone,
				ad: flds.date.value.ad,
				lon: flds.lon.value,
				lat: flds.lat.value,
				after23NewDay: after23,
				lateZiHourUseNextDay: lateZi,
			};
		}
		return params;
	}

	async requestBirthYearGanZi(){
		const flds = getAppliedBirth(this.state);
		if(!flds || !flds.date || !flds.time){
			return '';
		}
		const key = [
			flds.date.value.format('YYYY-MM-DD'),
			flds.time.value.format('HH:mm'),
			flds.date.value.ad,
			flds.date.value.zone,
			flds.lon.value,
			flds.lat.value,
			flds.after23NewDay.value,
		].join('|');
		if(this.birthYearGanZiCache[key]){
			return this.birthYearGanZiCache[key];
		}
		const localHit = getBirthGanzhiLocalCache(key);
		if(localHit){
			this.birthYearGanZiCache[key] = localHit;
			return localHit;
		}
		const params = {
			ad: flds.date.value.ad,
			date: flds.date.value.format('YYYY-MM-DD'),
			time: flds.time.value.format('HH:mm'),
			zone: flds.date.value.zone,
			lon: flds.lon.value,
			lat: flds.lat.value,
			after23NewDay: flds.after23NewDay.value,
			lateZiHourUseNextDay: flds.lateZiHourUseNextDay && flds.lateZiHourUseNextDay.value !== undefined ? flds.lateZiHourUseNextDay.value : defaultLateZiHourUseNextDay(),
		};
		try{
			const data = await request(`${Constants.ServerRoot}/liureng/gods`, {
				body: JSON.stringify(params),
				silent: true,
			});
			const lr = data && data[Constants.ResultKey] ? data[Constants.ResultKey].liureng : null;
			const ganzi = extractGanZi(
				lr && lr.fourColumns && lr.fourColumns.year ? lr.fourColumns.year.ganzi : ''
			) || extractGanZi(lr && lr.nongli ? (lr.nongli.yearGanZi || lr.nongli.yearJieqi || lr.nongli.year) : '');
			if(ganzi){
				this.birthYearGanZiCache[key] = ganzi;
				setBirthGanzhiLocalCache(key, ganzi);
			}
			return ganzi;
		}catch(e){
			return '';
		}
	}

	saveJinKouSnapshot(params, liureng, runyear, wuxing, guirengType, diFen, jinkouPan){
		if(!liureng){
			return;
		}
		const flds = this.state.calcFields ? this.state.calcFields : this.props.fields;
		const baseParams = params ? params : (flds ? this.genGodsParams(flds) : null);
		if(!baseParams){
			return;
		}
		const finalZone = baseParams.zone !== undefined ? baseParams.zone : (flds && flds.zone ? flds.zone.value : '');
		const finalLon = baseParams.lon !== undefined ? baseParams.lon : (flds && flds.lon ? flds.lon.value : '');
		const finalLat = baseParams.lat !== undefined ? baseParams.lat : (flds && flds.lat ? flds.lat.value : '');
		const saveParams = {
			...baseParams,
			zone: finalZone,
			lon: finalLon,
			lat: finalLat,
		};
		const localJinKouData = buildJinKouData(liureng, {
			diFen: diFen,
			guirengType: guirengType,
			isDiurnal: this.state.calcIsDiurnal,
		});
		const jinkouData = normalizeKinjinkouData(jinkouPan || this.state.jinkouPan, localJinKouData);
		const appliedBirth = getAppliedBirth(this.state);
		saveModuleAISnapshot('jinkou', buildJinKouSnapshotText(
			saveParams,
			liureng,
			runyear,
			jinkouData,
			wuxing,
			guirengType,
			appliedBirth && appliedBirth.gender ? appliedBirth.gender.value : 1
		), {
			date: saveParams.date,
			time: saveParams.time,
			zone: saveParams.zone,
			lon: saveParams.lon,
			lat: saveParams.lat,
			diFen: jinkouData && jinkouData.topInfo ? jinkouData.topInfo.diFen : '',
		});
	}

	async requestGods(fields, chartObj){
		if(fields === undefined || fields === null){
			return;
		}
		const params = this.genGodsParams(fields);
		const godsKey = buildCacheKey(params);
		let result = null;
		if(godsKey && this.godsCache.has(godsKey)){
			result = clonePlain(this.godsCache.get(godsKey));
		}else if(godsKey && this.godsInflight.has(godsKey)){
			result = clonePlain(await this.godsInflight.get(godsKey));
		}else{
			const req = request(`${Constants.ServerRoot}/liureng/gods`, {
				body: JSON.stringify(params),
				silent: true,
			}).then((data)=>{
				return data && data[Constants.ResultKey] ? data[Constants.ResultKey] : null;
			}).finally(()=>{
				if(godsKey){
					this.godsInflight.delete(godsKey);
				}
			});
			if(godsKey){
				this.godsInflight.set(godsKey, req);
			}
			result = await req;
			if(godsKey && result){
				pushCache(this.godsCache, godsKey, clonePlain(result), 72);
			}
		}
		if(!result || !result.liureng){
			return;
		}

		const dayGanZi = result.liureng.nongli.dayGanZi;
		const dayGan = dayGanZi.substr(0, 1);
		const wx = LRConst.GanZiWuXing[dayGan];
		const timeZi = normalizeZiFromText(result.liureng.nongli.time);
		const diFen = resolveJinKouDiFen(
			this.state.diFen,
			this.state.diFenAuto === true,
			timeZi,
			!!this.state.liureng
		);
		const calcIsDiurnal = resolveChartIsDiurnal(chartObj === undefined ? this.props.value : chartObj);
		const appliedBirth = buildBirthFields(this.state.birth, new DateTime());
		let jinkouPan = null;
		let jinkouError = '';
		try{
			jinkouPan = await fetchJinKouPan(fields, result.liureng.nongli, {
				diFen: diFen,
				yueJiang: this.state.yueJiang,
				zhanShi: this.state.zhanShi,
				timeBasis: this.state.timeBasis,
			});
		}catch(e){
			jinkouError = e && e.message ? e.message : '金口诀本地排盘服务尚未就绪';
			console.warn('kinjinkou backend failed, falling back to local JinKouCalc', e);
		}
		const st = {
			liureng: result.liureng,
			calcBirth: appliedBirth,
			wuxing: wx,
			diFen: diFen,
			jinkouPan: jinkouPan,
			jinkouError: jinkouError,
			calcFields: fields,
			calcIsDiurnal: calcIsDiurnal,
		};

		this.setState(st, ()=>{
			this.requestRunYear();
			this.saveJinKouSnapshot(params, result.liureng, this.state.runyear, wx, this.state.guireng, diFen, jinkouPan);
		});
	}

	async requestRunYear(){
		if(this.state.liureng === null){
			return;
		}
		const fields = this.state.calcFields ? this.state.calcFields : this.props.fields;
		if(!fields || !fields.date || !fields.date.value){
			return;
		}
		const birthFields = getAppliedBirth(this.state);
		if(!birthFields || !birthFields.date || !birthFields.date.value){
			return;
		}
		const params = this.genRunYearParams();
		if(birthFields.date.value.year > fields.date.value.year){
			Modal.error({
				title: '出生年份必须小于卜卦年份',
			});
			return;
		}
		const birthSolarYear = getSolarYearFromField(birthFields.date);
		const guaSolarYear = getSolarYearFromField(fields.date);
		const genderVal = birthFields && birthFields.gender ? birthFields.gender.value : 1;
		let fallbackRunYear = null;
		if(Number.isFinite(birthSolarYear) && Number.isFinite(guaSolarYear) && guaSolarYear >= birthSolarYear){
			const age = guaSolarYear - birthSolarYear;
			const ageCycle = ((age % 60) + 60) % 60;
			const yearList = `${genderVal}` === '0' ? FemaleRunYearList : MaleRunYearList;
			fallbackRunYear = {
				age: age,
				ageCycle: ageCycle,
				year: yearList[ageCycle] || '',
			};
		}
		if(!params.guaYearGanZi && !fallbackRunYear){
			Modal.error({
				title: '无法识别卜卦年份干支，请先排盘后再试',
			});
			return;
		}

		let result = fallbackRunYear ? { ...fallbackRunYear } : {};
		const runyearKey = buildCacheKey(params);
		try{
			let serverRes = {};
			const localRunyearHit = runyearKey ? getLiurengRunyearLocalCache(runyearKey) : null;
			if(runyearKey && this.runYearServerCache.has(runyearKey)){
				serverRes = clonePlain(this.runYearServerCache.get(runyearKey)) || {};
			}else if(runyearKey && this.runYearServerInflight.has(runyearKey)){
				serverRes = clonePlain(await this.runYearServerInflight.get(runyearKey)) || {};
			}else if(localRunyearHit){
				serverRes = clonePlain(localRunyearHit) || {};
				pushCache(this.runYearServerCache, runyearKey, clonePlain(serverRes), 96);
			}else{
				const req = request(`${Constants.ServerRoot}/liureng/runyear`, {
					body: JSON.stringify(params),
					silent: true,
				}).then((data)=>{
					return data && data[Constants.ResultKey] ? { ...data[Constants.ResultKey] } : {};
				}).finally(()=>{
					if(runyearKey){
						this.runYearServerInflight.delete(runyearKey);
					}
				});
				if(runyearKey){
					this.runYearServerInflight.set(runyearKey, req);
				}
				serverRes = await req;
				if(runyearKey){
					pushCache(this.runYearServerCache, runyearKey, clonePlain(serverRes), 96);
					setLiurengRunyearLocalCache(runyearKey, clonePlain(serverRes));
				}
			}
			result = {
				...serverRes,
				...result,
			};
			const guaGanZi = extractGanZi(params.guaYearGanZi) || resolveGuaYearGanZi(this.state.liureng);
			const birthGanZi = await this.requestBirthYearGanZi();
			let localRunYear = calcRunYearLocal(
				birthGanZi,
				guaGanZi,
				genderVal,
				birthSolarYear,
				guaSolarYear
			);
			if(!localRunYear && fallbackRunYear){
				localRunYear = fallbackRunYear;
			}
			if(!localRunYear && serverRes.age !== undefined && serverRes.age !== null){
				const age = Number(serverRes.age);
				if(Number.isFinite(age)){
					const ageCycle = ((age % 60) + 60) % 60;
					const yearList = `${genderVal}` === '0' ? FemaleRunYearList : MaleRunYearList;
					localRunYear = {
						age: age,
						ageCycle: ageCycle,
						year: yearList[ageCycle] || serverRes.year || '',
					};
				}
			}
			if(localRunYear){
				result.year = localRunYear.year;
				result.age = localRunYear.age;
				result.ageCycle = localRunYear.ageCycle;
			}
		}catch(e){
			if(fallbackRunYear){
				result = {
					...result,
					...fallbackRunYear,
				};
			}
		}
		if(fallbackRunYear){
			if(result.year === undefined || result.year === null || result.year === ''){
				result.year = fallbackRunYear.year;
			}
			if(result.age === undefined || result.age === null || Number.isNaN(Number(result.age))){
				result.age = fallbackRunYear.age;
			}
			if(result.ageCycle === undefined || result.ageCycle === null || Number.isNaN(Number(result.ageCycle))){
				result.ageCycle = fallbackRunYear.ageCycle;
			}
		}
		this.setState({
			runyear: result,
		}, ()=>{
			this.saveJinKouSnapshot(null, this.state.liureng, result, this.state.wuxing, this.state.guireng, this.state.diFen, this.state.jinkouPan);
		});
	}

	clickSaveCase(){
		if(!this.state.liureng){
			message.warning('请先完成起课后再保存');
			return;
		}
		const flds = this.state.calcFields ? this.state.calcFields : this.props.fields;
		if(!flds){
			return;
		}
		const displayRunYear = resolveDisplayRunYear(this.state.runyear, getAppliedBirth(this.state), flds);
		const divTime = `${flds.date.value.format('YYYY-MM-DD')} ${flds.time.value.format('HH:mm:ss')}`;
		const snapshot = loadModuleAISnapshot('jinkou');
		const payload = {
			module: 'jinkou',
			snapshot: snapshot,
			liureng: this.state.liureng,
			runyear: displayRunYear,
			wuxing: this.state.wuxing,
			guireng: this.state.guireng,
			diFen: this.state.diFen,
			jinkouPan: this.state.jinkouPan,
		};
		if(this.props.dispatch){
			this.props.dispatch({
				type: 'astro/openDrawer',
				payload: {
					key: 'caseadd',
					record: {
						event: `金口诀占断 ${divTime}`,
						caseType: 'jinkou',
						divTime: divTime,
						zone: flds.zone.value,
						lat: flds.lat.value,
						lon: flds.lon.value,
						gpsLat: flds.gpsLat.value,
						gpsLon: flds.gpsLon.value,
						pos: flds.pos ? flds.pos.value : '',
						payload: payload,
						sourceModule: 'jinkou',
					},
				},
			});
		}
	}

	genWuXingDoms(){
		return LRConst.WuXing.map((item, idx)=>{
			return (
				<Option key={idx} value={item.elem}>十二长生：{item.elem}--{item.ganzi}</Option>
			);
		});
	}

	componentDidMount(){
		this.unmounted = false;
		this._after23BoundaryUserOverrode = false; // 用户拍板:左栏改过 after23NewDay 后,全局事件不再触发重新起课
		this._lateZiHourUserOverrode = false; // v2.2.1: 同款时柱开关局部覆盖语义
		if(typeof window !== 'undefined'){
			// v2.2.1: setTimeout 0 延迟到下一 macrotask,让 dva 的 syncFromGlobal subscription 先把
			// fields.{after23NewDay,lateZiHourUseNextDay}.value 更新到 store + React 把新 props 透给本组件,再 fetch。
			// 否则 this.props.fields 在 listener 同步触发时仍是旧 snapshot,fetch 用的还是旧值,全局开关切了不生效。
			this._dayBoundaryListener = (ev) => {
				if(this._after23BoundaryUserOverrode) return;
				const v = ev && ev.detail ? ev.detail.after23NewDay : null;
				if((v === 0 || v === 1) && this.props.fields){
					setTimeout(() => {
						if(this.unmounted) return;
						this.requestGods(this.props.fields, this.props.value);
					}, 0);
				}
			};
			window.addEventListener('horosa:day-boundary-changed', this._dayBoundaryListener);
			this._lateZiHourListener = (ev) => {
				if(this._lateZiHourUserOverrode) return;
				const v = ev && ev.detail ? ev.detail.lateZiHourUseNextDay : null;
				if((v === 0 || v === 1) && this.props.fields){
					setTimeout(() => {
						if(this.unmounted) return;
						this.requestGods(this.props.fields, this.props.value);
					}, 0);
				}
			};
			window.addEventListener('horosa:late-zi-hour-mode-changed', this._lateZiHourListener);
		}
		if(this.props.fields){
			this.requestGods(this.props.fields, this.props.value);
		}
	}

	componentWillUnmount(){
		this.unmounted = true;
		if(typeof window !== 'undefined' && this._dayBoundaryListener){
			window.removeEventListener('horosa:day-boundary-changed', this._dayBoundaryListener);
		}
		if(typeof window !== 'undefined' && this._lateZiHourListener){
			window.removeEventListener('horosa:late-zi-hour-mode-changed', this._lateZiHourListener);
		}
	}

	renderInfoTable(title, rows){
		if(!rows || rows.length === 0){
			return (
				<div style={{ border: '1px solid var(--horosa-border, #d9d9d9)', marginBottom: 8 }}>
					<div style={{ backgroundColor: 'var(--horosa-gold-soft, #f7f3dc)', padding: '2px 8px', fontWeight: 600 }}>{title}</div>
					<div style={{ padding: '6px 8px', color: 'var(--horosa-muted, #8c8c8c)' }}>无</div>
				</div>
			);
		}
		return (
			<div style={{ border: '1px solid var(--horosa-border, #d9d9d9)', marginBottom: 8 }}>
				<div style={{ backgroundColor: 'var(--horosa-gold-soft, #f7f3dc)', padding: '2px 8px', fontWeight: 600 }}>{title}</div>
				<div style={{ padding: 0 }}>
					<table style={{ width: '100%', borderCollapse: 'collapse' }}>
						<tbody>
							{
								rows.map((row, idx)=>(
									<tr key={`${title}_${idx}`}>
										<td style={{ width: '42%', borderTop: '1px solid var(--horosa-border, #f0f0f0)', padding: '2px 6px', color: 'var(--horosa-text-soft, #595959)' }}>{row.key}</td>
										<td style={{ borderTop: '1px solid var(--horosa-border, #f0f0f0)', padding: '2px 6px', color: row.color && row.color !== '#262626' ? row.color : 'var(--horosa-text, #262626)', wordBreak: 'break-all' }}>{row.value}</td>
									</tr>
								))
							}
						</tbody>
					</table>
				</div>
			</div>
		);
	}

	renderInputPanel(wxdoms){
		return (
			<div className="horosa-jinkou-input-stack">
				<div>
					<div className="horosa-side-panel-title">金口诀设置</div>
					<div className="horosa-side-panel-subtitle">起课时间、地分与问测人</div>
				</div>

				<div className="horosa-jinkou-input-section">
					<div className="horosa-jinkou-field-title"><XQIcon name="clock" />起课时间与地点</div>
					<div className="horosa-jinkou-input-embed">
						<LiuRengInput
							fields={this.props.fields}
							onFieldsChange={this.onFieldsChange}
						/>
					</div>
				</div>

				<div className="horosa-jinkou-input-section">
					<div className="horosa-jinkou-field-title"><XQIcon name="target" />地分与课式</div>
					<label className="horosa-jinkou-select-field">
						<span>地分</span>
						<Select value={this.state.diFen} onChange={this.onDiFenChange}>
							{
								LRConst.ZiList.map((zi)=>(
									<Option key={`difen_${zi}`} value={zi}>地分：{zi}</Option>
								))
							}
						</Select>
					</label>
					<label className="horosa-jinkou-select-field">
						<span>十二长生五行</span>
						<Select value={this.state.wuxing} onChange={this.onWuXingChange}>
							{wxdoms}
						</Select>
					</label>
					<label className="horosa-jinkou-select-field">
						<span>月将</span>
						<Select value={this.state.yueJiang} onChange={this.onYueJiangChange}>
							<Option value="auto">自动取月将</Option>
							{
								LRConst.ZiList.map((zi)=>(
									<Option key={`yuejiang_${zi}`} value={zi}>月将：{zi}</Option>
								))
							}
						</Select>
					</label>
					<label className="horosa-jinkou-select-field">
						<span>占时</span>
						<Select value={this.state.zhanShi} onChange={this.onZhanShiChange}>
							<Option value="auto">自动取时支</Option>
							{
								LRConst.ZiList.map((zi)=>(
									<Option key={`zhanshi_${zi}`} value={zi}>占时：{zi}</Option>
								))
							}
						</Select>
					</label>
					<label className="horosa-jinkou-select-field">
						<span>时间基准</span>
						<Select value={this.state.timeBasis} onChange={this.onTimeBasisChange}>
							<Option value="direct">直接时间</Option>
							<Option value="trueSolar">真太阳时</Option>
						</Select>
					</label>
				</div>

				<div className="horosa-jinkou-input-section">
					<div className="horosa-jinkou-field-title"><XQIcon name="user" />问测人出生时间</div>
					<div className="horosa-jinkou-input-embed">
						<LiuRengBirthInput
							fields={this.state.birth}
							onFieldsChange={this.onBirthChange}
							requireConfirm={true}
						/>
					</div>
				</div>

				<div className="horosa-jinkou-action-row">
					<Button type="primary" onClick={()=>this.requestGods(this.props.fields, this.props.value)}>起课</Button>
					<Button onClick={this.clickSaveCase}>保存</Button>
				</div>
			</div>
		);
	}

	renderOverviewRows(jinkouData, displayRunYear, appliedBirth, chartFields){
		const params = chartFields ? this.genGodsParams(chartFields) : null;
		const gender = appliedBirth && appliedBirth.gender ? appliedBirth.gender.value : -1;
		const rows = [
			['起课时间', params ? `${params.date} ${params.time}` : '—'],
			['地点', params ? `${params.lon || '—'} ${params.lat || '—'}` : '—'],
			['时间基准', this.state.timeBasis === 'trueSolar' ? '真太阳时' : '直接时间'],
			['地分', jinkouData && jinkouData.ready ? jinkouData.topInfo.diFen : this.state.diFen],
			['月将', jinkouData && jinkouData.topInfo ? (jinkouData.topInfo.yuejiang || '—') : '—'],
			['占时', jinkouData && jinkouData.topInfo ? (jinkouData.topInfo.zhanshi || '—') : '—'],
			['空亡', jinkouData && jinkouData.ready ? jinkouData.topInfo.xunKong : '—'],
			['四大空亡', jinkouData && jinkouData.ready ? jinkouData.topInfo.siDaKong : '—'],
			['用爻', jinkouData && jinkouData.yongYao ? `${jinkouData.yongYao.label || '—'}${jinkouData.yongYao.sign ? `(${jinkouData.yongYao.sign})` : ''}` : '—'],
			['十二长生', this.state.wuxing],
			['行年', displayRunYear ? `${displayRunYear.year || '—'} / ${displayRunYear.age || '—'}岁` : '—'],
			['性别', `${gender}` === '0' ? '女' : (`${gender}` === '1' ? '男' : '未知')],
		];
		return rows.map(([label, value])=>(
			<div className="horosa-jinkou-info-row" key={label}>
				<span>{label}</span>
				<strong>{fmtValue(value)}</strong>
			</div>
		));
	}

	renderStartRows(jinkouData, chartFields){
		if(!jinkouData || !jinkouData.ready){
			return <div className="horosa-jinkou-empty">暂无起课数据</div>;
		}
		const params = chartFields ? this.genGodsParams(chartFields) : null;
		const backend = jinkouData.backend || {};
		const ganzhi = backend.ganzhi || {};
		const rows = [
			['日期', backend.dateStr || (params ? params.date : '')],
			['时间', backend.timeStr || (params ? params.time : '')],
			['真太阳时', backend.realSunTime || (this.state.liureng && this.state.liureng.nongli ? this.state.liureng.nongli.birth : '')],
			['节气', backend.jiedelta || (this.state.liureng && this.state.liureng.nongli ? this.state.liureng.nongli.jiedelta : '')],
			['年柱', ganzhi.year],
			['月柱', ganzhi.month],
			['日柱', ganzhi.day],
			['时柱', ganzhi.time],
			['地分', backend.difen],
			['月将', backend.yuejiang],
			['占时', backend.zhanshi],
			['四大空亡', backend.siDaKong],
		];
		return (
			<div className="horosa-jinkou-info-card">
				{rows.map(([label, value])=>(
					<div className="horosa-jinkou-info-row" key={`start_${label}`}>
						<span>{label}</span>
						<strong>{fmtValue(value || '—')}</strong>
					</div>
				))}
			</div>
		);
	}

	renderJinKouRows(jinkouData){
		if(!jinkouData || !jinkouData.ready || !jinkouData.rows){
			return <div className="horosa-jinkou-empty">暂无金口诀数据</div>;
		}
		return jinkouData.rows.map((row)=>(
			<div className="horosa-jinkou-four-row" key={row.label}>
				<div className="horosa-jinkou-four-label">{row.label}</div>
				<div>
					<strong>{fmtValue(row.content)}</strong>
					<span>天干 {fmtValue(row.gan)} · 神将 {fmtValue(row.shenjiang)} · {fmtValue(row.power)} · {fmtValue(row.kong)}{row.nayin ? ` · 纳音 ${row.nayin}` : ''}</span>
				</div>
			</div>
		));
	}

	renderShenshaRows(jinkouData){
		const docRows = jinkouData && jinkouData.shenshaDocRows ? jinkouData.shenshaDocRows : [];
		if(!docRows.length){
			return <div className="horosa-jinkou-empty">暂无四位神煞</div>;
		}
		return docRows.map((row)=>(
			<div key={row.label} style={{ marginBottom: 10 }}>
				<div style={{ fontWeight: 600, color: 'var(--horosa-text, #262626)', marginBottom: 4 }}>{row.position}</div>
				{row.items && row.items.length ? row.items.map((it, idx)=>(
					<div key={`${row.label}_${idx}`} style={{ borderLeft: `3px solid ${this.jxColor(it.jx)}`, padding: '2px 8px', marginBottom: 4, lineHeight: 1.6 }}>
						<strong style={{ color: this.jxColor(it.jx) }}>{it.name}</strong>
						{it.desc ? <span style={{ color: 'var(--horosa-text-soft, #595959)' }}>　{it.desc}</span> : null}
					</div>
				)) : <div className="horosa-jinkou-empty">无</div>}
			</div>
		));
	}

	jxColor(jx){
		if(jx === 'ji'){ return 'var(--horosa-jx-ji, #1f8a4c)'; }
		if(jx === 'xiong'){ return 'var(--horosa-jx-xiong, #c0392b)'; }
		return 'var(--horosa-muted, #8c8c8c)';
	}

	renderTextBlock(title, text){
		if(!text){ return null; }
		return (
			<div style={{ border: '1px solid var(--horosa-border, #d9d9d9)', borderRadius: 6, marginBottom: 8 }}>
				<div style={{ backgroundColor: 'var(--horosa-gold-soft, #f7f3dc)', padding: '2px 8px', fontWeight: 600 }}>{title}</div>
				<div style={{ padding: '6px 8px', lineHeight: 1.6, color: 'var(--horosa-text, #262626)' }}>{text}</div>
			</div>
		);
	}

	renderAnalysisBasic(jinkouData){
		if(!jinkouData || !jinkouData.ready){
			return <div className="horosa-jinkou-empty">暂无分析</div>;
		}
		const yin = (jinkouData.lineSigns || []).map((s)=>`${s.label}${s.sign}`).join(' · ');
		const shortRows = [
			['阴阳', yin || '—'],
			['旬空', jinkouData.xunKongBranches && jinkouData.xunKongBranches.length ? jinkouData.xunKongBranches.join('') : '无'],
			['四大空亡', jinkouData.topInfo ? jinkouData.topInfo.siDaKong : '—'],
		];
		return (
			<div>
				<div className="horosa-jinkou-info-card">
					{shortRows.map((item)=>(
						<div className="horosa-jinkou-info-row" key={item[0]}>
							<span>{item[0]}</span>
							<strong>{fmtValue(item[1])}</strong>
						</div>
					))}
				</div>
				{this.renderTextBlock('用神强弱', jinkouData.yongStrength ? jinkouData.yongStrength.text : '')}
				{this.renderTextBlock('应期', jinkouData.yingQi ? jinkouData.yingQi.text : '')}
			</div>
		);
	}

	renderRelations(jinkouData){
		const rels = jinkouData && jinkouData.relations ? jinkouData.relations : [];
		if(!rels.length){
			return <div className="horosa-jinkou-empty">四位无显著生克</div>;
		}
		const relColor = (rel)=>{
			if(rel === '生' || rel === '被生'){ return '#2f9f68'; }
			if(rel === '克' || rel === '被克'){ return '#d64a35'; }
			return 'var(--horosa-muted, #8c8c8c)';
		};
		return (
			<div style={{ padding: '4px 0' }}>
				{rels.map((r, idx)=>(
					<div key={`rel_${idx}`} style={{ borderLeft: `3px solid ${relColor(r.rel)}`, padding: '4px 8px', marginBottom: 6, lineHeight: 1.6 }}>
						<span style={{ display: 'inline-block', padding: '0 8px', borderRadius: 10, background: 'var(--horosa-gold-soft, #f7f3dc)', color: relColor(r.rel), fontWeight: 600, marginRight: 6 }}>
							{r.from}{r.rel}{r.to}
						</span>
						{r.text ? <span style={{ color: 'var(--horosa-text-soft, #595959)' }}>{r.text}</span> : null}
					</div>
				))}
			</div>
		);
	}

	renderHezhan(){
		return <div className="horosa-jinkou-empty">六壬合占（分类占断）细则完善中。</div>;
	}

	renderCategory(jinkouData){
		const cats = jinkouData && jinkouData.categoryRules ? jinkouData.categoryRules : [];
		const ready = cats.filter((c)=>c.texts && c.texts.length);
		if(!ready.length){
			return <div className="horosa-jinkou-empty">分类用神细则完善中</div>;
		}
		return (
			<div>
				{ready.map((c)=>(
					<div key={c.key} style={{ border: '1px solid var(--horosa-border, #d9d9d9)', borderRadius: 6, marginBottom: 8 }}>
						<div style={{ backgroundColor: 'var(--horosa-gold-soft, #f7f3dc)', padding: '4px 8px', fontWeight: 600 }}>
							{c.name}
							{c.yongHint ? <span style={{ fontWeight: 400, color: 'var(--horosa-text-soft, #595959)', marginLeft: 8 }}>用神：{c.yongHint}</span> : null}
						</div>
						<div style={{ padding: '6px 8px' }}>
							{c.texts.map((t, idx)=>(
								<div key={`cat_${idx}`} style={{ borderLeft: '3px solid var(--horosa-border, #e8e8e8)', padding: '2px 8px', marginBottom: 6, lineHeight: 1.6, color: 'var(--horosa-text, #262626)' }}>{t}</div>
							))}
							{c.src ? <div style={{ color: 'var(--horosa-muted, #8c8c8c)', fontSize: 12, marginTop: 2 }}>源：{c.src}</div> : null}
						</div>
					</div>
				))}
			</div>
		);
	}

	renderBranchRelation(jinkouData){
		const brs = jinkouData && jinkouData.branchRelations ? jinkouData.branchRelations : [];
		const typeColor = (t)=>{
			if(t === '合' || t === '三合'){ return '#2f9f68'; }
			if(t === '冲'){ return '#d64a35'; }
			return '#c98a2f';
		};
		return (
			<div>
				<JinKouRelationMini relations={brs} rows={jinkouData ? jinkouData.rows : []} />
				{brs.length ? (
					<div style={{ marginTop: 6 }}>
						{brs.map((b, idx)=>(
							<div key={`br_${idx}`} style={{ borderLeft: `3px solid ${typeColor(b.type)}`, padding: '2px 8px', marginBottom: 6, lineHeight: 1.6 }}>
								<span style={{ color: typeColor(b.type), fontWeight: 600 }}>{b.aLabel}{b.a} {b.type} {b.bLabel}{b.b}</span>
								{b.desc ? <div style={{ color: 'var(--horosa-text-soft, #595959)', fontSize: 13 }}>{b.desc}</div> : null}
							</div>
						))}
					</div>
				) : <div className="horosa-jinkou-empty">四位与日辰无刑冲合害破</div>}
			</div>
		);
	}

	renderTaixuan(jinkouData){
		const tx = jinkouData && jinkouData.taixuan ? jinkouData.taixuan : [];
		if(!tx.length){
			return <div className="horosa-jinkou-empty">暂无数理</div>;
		}
		const rows = tx.map((t)=>({ key: t.label, value: `${t.tokens || '—'}　太玄数 ${t.num}` }));
		return this.renderInfoTable('太玄数', rows);
	}

	renderRelevantShensha(jinkouData){
		const list = jinkouData && jinkouData.relevantShensha ? jinkouData.relevantShensha : [];
		if(!list.length){
			return <div className="horosa-jinkou-empty">暂无相关神煞</div>;
		}
		return (
			<div style={{ padding: '2px 0' }}>
				{list.map((it, idx)=>(
					<div key={`rs_${idx}`} style={{ borderLeft: `3px solid ${this.jxColor(it.jx)}`, padding: '2px 8px', marginBottom: 4, lineHeight: 1.6 }}>
						<span style={{ color: 'var(--horosa-muted, #8c8c8c)', fontSize: 12, marginRight: 6 }}>{it.position}</span>
						<strong style={{ color: this.jxColor(it.jx) }}>{it.name}</strong>
						{it.desc ? <span style={{ color: 'var(--horosa-text-soft, #595959)' }}>　{it.desc}</span> : null}
					</div>
				))}
			</div>
		);
	}

	renderPlateRows(jinkouData){
		if(!jinkouData || !jinkouData.plates || !jinkouData.plates.length){
			return <div className="horosa-jinkou-empty">暂无三盘数据</div>;
		}
		return jinkouData.plates.map((row)=>(
			<div className="horosa-jinkou-info-row" key={`plate_${row.index || row.di}`}>
					<span>{row.di}</span>
				<strong>{`天${fmtValue(row.tian)} · 将${fmtValue(row.jiang)} · 神${fmtValue(row.shen)} · 贵${fmtValue(row.gui)}`}</strong>
			</div>
		));
	}

	renderRawText(jinkouData){
		const rawText = jinkouData && jinkouData.backend ? jinkouData.backend.rawText : '';
		if(!rawText){
			return <div className="horosa-jinkou-empty">暂无原文</div>;
		}
		return <pre className="horosa-jinkou-snapshot">{rawText}</pre>;
	}

	renderSectionTitle(title){
		return (
			<div style={{ margin: '14px 0 6px', paddingLeft: 8, borderLeft: '3px solid var(--horosa-gold, #c9a84c)', fontWeight: 600, fontSize: 14, color: 'var(--horosa-text, #262626)' }}>{title}</div>
		);
	}

	renderOverviewAll(jinkouData, displayRunYear, appliedBirth, chartFields, roleRefRows){
		return (
			<div>
				<div className="horosa-jinkou-info-card">
					{this.renderOverviewRows(jinkouData, displayRunYear, appliedBirth, chartFields)}
				</div>
				{this.renderSectionTitle('课情')}
				{this.renderStartRows(jinkouData, chartFields)}
				{this.renderSectionTitle('四位')}
				<div className="horosa-jinkou-info-card">
					{this.renderJinKouRows(jinkouData)}
				</div>
				{this.renderSectionTitle('三盘')}
				<div className="horosa-jinkou-info-card">
					{this.renderPlateRows(jinkouData)}
				</div>
				{this.renderSectionTitle('四位类象')}
				{this.renderInfoTable('四位类象', roleRefRows)}
			</div>
		);
	}

	renderRightPanel(jinkouData, displayRunYear, appliedBirth, chartFields, godsZiRows, godsYearRows, zsRows, roleRefRows){
		const validPanelTabs = ['overview', 'gods', 'analysis', 'aux'];
		const activeKey = validPanelTabs.indexOf(this.state.rightPanelTab) >= 0 ? this.state.rightPanelTab : 'overview';
		const validGodsTabs = ['godsZi', 'godsYear', 'zs', 'jkshensha'];
		const godsKey = validGodsTabs.indexOf(this.state.rightTab) >= 0 ? this.state.rightTab : 'godsZi';
		return (
			<Tabs activeKey={activeKey} onChange={this.setRightPanelTab} defaultActiveKey="overview" tabPosition="top" className="horosa-jinkou-tabs">
				<TabPane tab="概览" key="overview">
					{this.renderOverviewAll(jinkouData, displayRunYear, appliedBirth, chartFields, roleRefRows)}
				</TabPane>
				<TabPane tab="神煞" key="gods">
					<Tabs
						activeKey={godsKey}
						onChange={this.setRightTab}
						defaultActiveKey='godsZi'
						tabPosition='top'
						size='small'
						className="horosa-jinkou-nested-tabs"
					>
						<TabPane tab='支煞' key='godsZi'>
							{this.renderInfoTable('支煞', godsZiRows)}
						</TabPane>
						<TabPane tab='年煞' key='godsYear'>
							{this.renderInfoTable('年煞', godsYearRows)}
						</TabPane>
						<TabPane tab='长生' key='zs'>
							{this.renderInfoTable(`${this.state.wuxing}十二长生`, zsRows)}
						</TabPane>
						<TabPane tab='四煞' key='jkshensha'>
							<div className="horosa-jinkou-info-card">
								{this.renderShenshaRows(jinkouData)}
							</div>
						</TabPane>
					</Tabs>
				</TabPane>
				<TabPane tab="分析" key="analysis">
					<Tabs activeKey={this.state.analysisTab} onChange={this.setAnalysisTab} defaultActiveKey="basic" tabPosition="top" size="small" className="horosa-jinkou-nested-tabs">
						<TabPane tab="基本" key="basic">{this.renderAnalysisBasic(jinkouData)}</TabPane>
						<TabPane tab="四位关系" key="relation">{this.renderRelations(jinkouData)}</TabPane>
						<TabPane tab="合占" key="hezhan">{this.renderHezhan(jinkouData)}</TabPane>
					</Tabs>
				</TabPane>
				<TabPane tab="辅助" key="aux">
					<Tabs activeKey={this.state.auxTab} onChange={this.setAuxTab} defaultActiveKey="category" tabPosition="top" size="small" className="horosa-jinkou-nested-tabs">
						<TabPane tab="分类用神" key="category">{this.renderCategory(jinkouData)}</TabPane>
						<TabPane tab="关系图" key="branch">{this.renderBranchRelation(jinkouData)}</TabPane>
						<TabPane tab="数理" key="num">{this.renderTaixuan(jinkouData)}</TabPane>
					</Tabs>
				</TabPane>
			</Tabs>
		);
	}

	renderBottomQuickDock(){
		const actions = [
			{ label: '起课', icon: 'quickPrimary', onClick: ()=>this.requestGods(this.props.fields, this.props.value) },
			{ label: '概览', icon: 'quickComposite', active: this.state.rightPanelTab === 'overview', onClick: ()=>this.setRightPanelTab('overview') },
			{ label: '神煞', icon: 'quickFirdaria', active: this.state.rightPanelTab === 'gods', onClick: ()=>this.setRightPanelTab('gods') },
			{ label: '分析', icon: 'quickProfection', active: this.state.rightPanelTab === 'analysis', onClick: ()=>this.setRightPanelTab('analysis') },
			{ label: '辅助', icon: 'quickComposite', active: this.state.rightPanelTab === 'aux', onClick: ()=>this.setRightPanelTab('aux') },
			{ label: '保存', icon: 'quickNote', onClick: this.clickSaveCase },
			{ label: '宿盘', icon: 'quickReturn', onClick: ()=>this.navigateFeature('cnyibu', 'suzhan') },
			{ label: '统摄法', icon: 'quickProfection', onClick: ()=>this.navigateFeature('cnyibu', 'tongshefa') },
			{ label: 'AI助手', icon: 'quickAi', onClick: ()=>this.navigateFeature('aianalysis') },
		];
		return (
			<div className="horosa-bottom-quick-dock horosa-jinkou-quick-dock">
				<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
				<div className="horosa-bottom-quick-actions horosa-jinkou-quick-actions">
					{actions.map((item)=>(
						<button
							type="button"
							key={item.label}
							className={`horosa-bottom-quick-button horosa-jinkou-quick-button${item.active ? ' is-active' : ''}`}
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

	render(){
		let height = this.props.height ? this.props.height : 760;
		if(height === '100%'){
			height = 760;
		}else{
			height = height - 20;
		}

		let chartHeight = height;
		if(typeof chartHeight !== 'number'){
			chartHeight = 760;
		}

		const chartObj = this.props.value;
		const chart = chartObj ? chartObj.chart : {};
		const chartFields = this.state.calcFields ? this.state.calcFields : this.props.fields;
		const appliedBirth = getAppliedBirth(this.state);
		const displayRunYear = resolveDisplayRunYear(this.state.runyear, appliedBirth, chartFields);
		const localJinKouData = buildJinKouData(this.state.liureng, {
			diFen: this.state.diFen,
			guirengType: this.state.guireng,
			isDiurnal: this.state.calcIsDiurnal,
		});
		const jinkouData = normalizeKinjinkouData(this.state.jinkouPan, localJinKouData);
		const wxdoms = this.genWuXingDoms();

		const godsZiRows = this.state.liureng ? mapObjToRows(this.state.liureng.godsZi) : [];
		const godsYearRows = this.state.liureng && this.state.liureng.godsYear ? mapObjToRows(this.state.liureng.godsYear.taisui1) : [];
		const zsRows = ZSList.map((name)=>{
			const key = `${this.state.wuxing}_${name}`;
			return {
				key: name,
				value: ZhangSheng.wxphase[key] ? ZhangSheng.wxphase[key] : '—',
			};
		});
		const roleRefRows = [{
			key: '四、人元',
			value: '尊、客、天、君、祖、外',
		}, {
			key: '三、贵神',
			value: '上、主、宰相、臣、父、官禄',
		}, {
			key: '二、月将',
			value: '中、己身、妻财、亲戚、内',
		}, {
			key: '一、地分',
			value: '下、田宅、子孙、奴仆、鞍马、六畜',
		}];

		return (
				<div className={`horosa-jinkou-page horosa-astro-redesign horosa-jinkou-redesign${this.props.hideQuickDock ? ' horosa-jinkou-embedded' : ''}`} style={{ height: height, minHeight: height, overflow: 'hidden' }}>
				<div className="horosa-astro-layout horosa-astro-redesign-layout horosa-jinkou-redesign-layout">
					<div className="horosa-astro-redesign-grid horosa-jinkou-redesign-grid">
						<div className="horosa-astro-context-panel horosa-astro-input-panel horosa-jinkou-input-panel">
							{this.renderInputPanel(wxdoms)}
						</div>
						<div className="horosa-chart-stage horosa-chart-stage-redesign horosa-jinkou-chart-panel xq-chart-renderer xq-chart-renderer-jinkou">
							<div className="horosa-jinkou-board-host">
								<JinKouChart
									value={chart}
									liureng={this.state.liureng}
									runyear={displayRunYear}
									gender={appliedBirth && appliedBirth.gender ? appliedBirth.gender.value : -1}
									zhangshengElem={this.state.wuxing}
									guireng={this.state.guireng}
									jinkouData={jinkouData}
									height={Math.max(560, chartHeight - 22)}
									fields={this.props.fields}
									chartDisplay={this.props.chartDisplay}
									planetDisplay={this.props.planetDisplay}
								/>
							</div>
						</div>
						<div className="horosa-inspector-panel horosa-astro-content-panel horosa-jinkou-info-panel">
							<div className="horosa-side-panel-heading horosa-jinkou-info-heading">
								<div>
									<div className="horosa-side-panel-title">金口诀信息</div>
									<div className="horosa-side-panel-subtitle">概览、四位与神煞</div>
								</div>
							</div>
							{this.renderRightPanel(jinkouData, displayRunYear, appliedBirth, chartFields, godsZiRows, godsYearRows, zsRows, roleRefRows)}
						</div>
					</div>
					{!this.props.hideQuickDock && this.renderBottomQuickDock()}
				</div>
			</div>
		);
	}
}

export default JinKouMain;
