import { Component } from 'react';
import { Row, Col, Button, Divider, Select, InputNumber, Input, Checkbox, Modal, message } from 'antd';
import * as Constants from '../../utils/constants';
import request from '../../utils/request';
import * as AstroConst from '../../constants/AstroConst';
import {randomStr, randomNum, littleEndian,} from '../../utils/helper';
import * as LRConst from '../liureng/LRConst';
import { ZSList, ZhangSheng, } from '../liureng/LRZhangSheng';
import ChuangChart from '../liureng/ChuangChart';
import LiuRengChart from './LiuRengChart';
import LiuRengInput from './LiuRengInput';
import LiuRengBirthInput from './LiuRengBirthInput';
import DateTime from '../comp/DateTime';
import { saveModuleAISnapshot, loadModuleAISnapshot } from '../../utils/moduleAiSnapshot';


const InputGroup = Input.Group;
const {Option} = Select;

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
		after23NewDay: { value: src.after23NewDay && src.after23NewDay.value !== undefined ? src.after23NewDay.value : 0 },
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
	keys.forEach((key)=>{
		lines.push(`${cleanKey(key)}：${fmtValue(obj[key])}`);
	});
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
	const base = 1984 + idx;
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

function getChartYue(chartObj){
	if(!chartObj || !chartObj.objects){
		return '';
	}
	for(let i=0; i<chartObj.objects.length; i++){
		const obj = chartObj.objects[i];
		if(obj.id === AstroConst.SUN){
			return LRConst.getSignZi(obj.sign);
		}
	}
	return '';
}

function buildLiuRengLayout(chartObj, guirengType){
	if(!chartObj || !chartObj.nongli || !chartObj.nongli.time){
		return null;
	}
	const yue = getChartYue(chartObj);
	if(!yue){
		return null;
	}
	const downZi = LRConst.ZiList.slice(0);
	const upZi = LRConst.ZiList.slice(0);
	const yueIndexs = [];
	const timezi = chartObj.nongli.time.substr(1);
	const yueIdx = LRConst.ZiList.indexOf(yue);
	const tmIdx = LRConst.ZiList.indexOf(timezi);
	if(yueIdx < 0 || tmIdx < 0){
		return null;
	}
	const delta = yueIdx - tmIdx;
	for(let i=0; i<12; i++){
		const idx = (i + delta + 12) % 12;
		yueIndexs[i] = idx;
		upZi[i] = LRConst.ZiList[idx];
	}

	const houseTianJiang = LRConst.TianJiang.slice(0);
	const guizi = LRConst.getGuiZi(chartObj, guirengType);
	let houseidx = 0;
	for(let i=0; i<12; i++){
		const zi = LRConst.ZiList[yueIndexs[i]];
		if(zi === guizi){
			houseidx = i;
			break;
		}
	}
	const housezi = LRConst.ZiList[houseidx];
	if(LRConst.SummerZiList.indexOf(housezi) >= 0){
		for(let i=0; i<12; i++){
			const idx = (houseidx - i + 12) % 12;
			houseTianJiang[i] = LRConst.TianJiang[idx];
		}
	}else{
		for(let i=0; i<12; i++){
			const idx = (i - houseidx + 12) % 12;
			houseTianJiang[i] = LRConst.TianJiang[idx];
		}
	}

	return {
		yue,
		timezi,
		guizi,
		downZi,
		upZi,
		houseTianJiang,
	};
}

function getAppliedBirth(state){
	if(state && state.calcBirth){
		return state.calcBirth;
	}
	return state ? state.birth : null;
}

function buildKeData(layout, chartObj){
	const result = {
		raw: [],
		lines: [],
	};
	if(!layout || !chartObj || !chartObj.nongli || !chartObj.nongli.dayGanZi){
		return result;
	}
	const dayGanZi = chartObj.nongli.dayGanZi;
	const daygan = dayGanZi.substr(0, 1);
	const dayzi = dayGanZi.substr(1, 1);

	const idx1 = layout.downZi.indexOf(LRConst.GanJiZi[daygan]);
	if(idx1 < 0){
		return result;
	}
	const ke1zi = layout.upZi[idx1];
	const ke1 = [layout.houseTianJiang[idx1], ke1zi, daygan];

	const idx2 = layout.downZi.indexOf(ke1zi);
	const ke2zi = idx2 >= 0 ? layout.upZi[idx2] : '';
	const ke2 = [idx2 >= 0 ? layout.houseTianJiang[idx2] : '', ke2zi, ke1zi];

	const idx3 = layout.downZi.indexOf(dayzi);
	const ke3zi = idx3 >= 0 ? layout.upZi[idx3] : '';
	const ke3 = [idx3 >= 0 ? layout.houseTianJiang[idx3] : '', ke3zi, dayzi];

	const idx4 = layout.downZi.indexOf(ke3zi);
	const ke4zi = idx4 >= 0 ? layout.upZi[idx4] : '';
	const ke4 = [idx4 >= 0 ? layout.houseTianJiang[idx4] : '', ke4zi, ke3zi];

	const all = [ke1, ke2, ke3, ke4];
	const names = ['一课', '二课', '三课', '四课'];
	all.forEach((item, idx)=>{
		result.lines.push(`${names[idx]}：地盘=${item[2]}，天盘=${item[1]}，贵神=${item[0]}`);
	});
	result.raw = all;
	return result;
}

function buildSanChuanData(layout, keRaw, chartObj){
	if(!layout || !keRaw || keRaw.length !== 4 || !chartObj || !chartObj.nongli){
		return null;
	}
	try{
		const helper = new ChuangChart({
			owner: null,
			chartObj: chartObj,
			nongli: chartObj.nongli,
			ke: keRaw,
			liuRengChart: {
				upZi: layout.upZi,
				downZi: layout.downZi,
				houseTianJiang: layout.houseTianJiang,
			},
			x: 0,
			y: 0,
			width: 0,
			height: 0,
		});
		helper.genCuangs();
		return helper.cuangs || null;
	}catch(e){
		return null;
	}
}

function buildLiuRengSnapshotText(params, liureng, runyear, chartObj, guirengType, zhangshengElem, gender){
	const lines = [];
	const nongli = liureng && liureng.nongli ? liureng.nongli : (chartObj && chartObj.nongli ? chartObj.nongli : {});
	const layout = buildLiuRengLayout(chartObj, guirengType);
	const keData = buildKeData(layout, chartObj);
	const sanChuan = buildSanChuanData(layout, keData.raw, chartObj);
	const xingbie = `${gender}` === '1' ? '男' : '女';

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
	lines.push(`贵人体系：${guirengType === 0 ? '六壬法贵人' : (guirengType === 1 ? '遁甲法贵人' : '星占法贵人')}`);
	lines.push(`十二长生五行：${fmtValue(zhangshengElem)}`);
	lines.push(`问测人性别：${xingbie}`);
	lines.push('');

	lines.push('[十二地盘/十二天盘/十二贵神对应]');
	if(layout){
		for(let i=0; i<12; i++){
			lines.push(`${i + 1}. 地盘${layout.downZi[i]} -> 天盘${layout.upZi[i]} -> 贵神${layout.houseTianJiang[i]}`);
		}
	}else{
		lines.push('无');
	}
	lines.push('');

	lines.push('[四课]');
	if(keData.lines.length){
		keData.lines.forEach((line)=>lines.push(line));
	}else{
		lines.push('无');
	}
	lines.push('');

	lines.push('[三传]');
	if(sanChuan){
		lines.push(`课式：${fmtValue(sanChuan.name)}`);
		const names = ['初传', '中传', '末传'];
		for(let i=0; i<3; i++){
			const gz = sanChuan.cuang && sanChuan.cuang[i] ? sanChuan.cuang[i] : '无';
			const lq = sanChuan.liuQin && sanChuan.liuQin[i] ? sanChuan.liuQin[i] : '无';
			const gs = sanChuan.tianJiang && sanChuan.tianJiang[i] ? sanChuan.tianJiang[i] : '无';
			lines.push(`${names[i]}：干支=${gz}；六亲=${lq}；贵神=${gs}`);
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

	lines.push('[岁煞]');
	const yearGods = liureng && liureng.godsYear ? liureng.godsYear.taisui1 : null;
	if(yearGods){
		LRConst.TaiSui.forEach((name)=>{
			lines.push(`${name}：${fmtValue(yearGods[name])}`);
		});
	}else{
		lines.push('无');
	}
	lines.push('');

	lines.push('[十二长生]');
	if(zhangshengElem){
		ZSList.forEach((item)=>{
			const key = `${zhangshengElem}_${item}`;
			lines.push(`${item}：${fmtValue(ZhangSheng.wxphase[key])}`);
		});
	}else{
		lines.push('无');
	}
	return lines.join('\n').trim();
}

class LiuRengMain extends Component{
	constructor(props) {
		super(props);
		let now = new DateTime();
		let birth = buildBirthFields(this.props.fields, now);

		this.state = {
			birth: birth,
			calcBirth: birth,
			liureng: null,
			runyear: null,
			wuxing: '土',
			guireng: 2,
			calcFields: null,
			calcChart: null,
		};

		this.unmounted = false;
		this.birthYearGanZiCache = {};

		this.onFieldsChange = this.onFieldsChange.bind(this);
		this.onBirthChange = this.onBirthChange.bind(this);
		this.onWuXingChange = this.onWuXingChange.bind(this);
		this.onGuiRengChange = this.onGuiRengChange.bind(this);
		this.genWuXingDoms = this.genWuXingDoms.bind(this);
		this.genGodsParams = this.genGodsParams.bind(this);
		this.genRunYearParams = this.genRunYearParams.bind(this);
		this.requestGods = this.requestGods.bind(this);
		this.requestRunYear = this.requestRunYear.bind(this);
		this.requestBirthYearGanZi = this.requestBirthYearGanZi.bind(this);
		this.startPaiPanByFields = this.startPaiPanByFields.bind(this);
		this.clickStartPaiPan = this.clickStartPaiPan.bind(this);
		this.saveLiuRengAISnapshot = this.saveLiuRengAISnapshot.bind(this);
		this.clickSaveCase = this.clickSaveCase.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (fields, chartObj)=>{
				if(this.unmounted){
					return;
				}
				this.startPaiPanByFields(fields || this.props.fields, chartObj || this.props.value);
			};
		}
	}

	onFieldsChange(field){
		const patch = {
			...(field || {}),
		};
		const confirmed = !!patch.__confirmed;
		if(Object.prototype.hasOwnProperty.call(patch, '__confirmed')){
			delete patch.__confirmed;
		}
		if(this.props.dispatch && this.props.fields){
			let flds = {
				fields: {
					...this.props.fields,
					...patch,
				}
			};
			this.props.dispatch({
				type: 'astro/fetchByFields',
				payload: {
					...flds.fields,
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

	startPaiPanByFields(fields, chartObj){
		const calcFields = fields || this.props.fields;
		const chartWrap = chartObj === undefined || chartObj === null ? this.props.value : chartObj;
		const calcChart = chartWrap && chartWrap.chart ? chartWrap.chart : null;
		if(!calcFields || !calcChart){
			return;
		}
		this.setState({
			calcFields: calcFields,
			calcChart: calcChart,
		}, ()=>{
			this.requestGods(calcFields);
		});
	}

	clickStartPaiPan(){
		this.startPaiPanByFields(this.props.fields, this.props.value);
	}

	onWuXingChange(val){
		this.setState({
			wuxing: val,
		}, ()=>{
			this.saveLiuRengAISnapshot(null, this.state.liureng, this.state.runyear, val, this.state.guireng);
		});
	}

	onGuiRengChange(val){
		this.setState({
			guireng: val,
		}, ()=>{
			this.saveLiuRengAISnapshot(null, this.state.liureng, this.state.runyear, this.state.wuxing, val);
		});
	}

	saveLiuRengAISnapshot(params, liureng, runyear, wuxing, guirengType){
		if(!liureng){
			return;
		}
		const flds = this.state.calcFields ? this.state.calcFields : this.props.fields;
		const baseParams = params ? params : (flds ? this.genGodsParams(flds) : null);
		if(!baseParams){
			return;
		}
		const chartObj = this.state.calcChart ? this.state.calcChart : (this.props.value && this.props.value.chart ? this.props.value.chart : null);
		const finalZone = baseParams.zone !== undefined ? baseParams.zone : (flds && flds.zone ? flds.zone.value : '');
		const finalLon = baseParams.lon !== undefined ? baseParams.lon : (flds && flds.lon ? flds.lon.value : '');
		const finalLat = baseParams.lat !== undefined ? baseParams.lat : (flds && flds.lat ? flds.lat.value : '');
		const saveParams = {
			...baseParams,
			zone: finalZone,
			lon: finalLon,
			lat: finalLat,
		};
		const appliedBirth = getAppliedBirth(this.state);
		saveModuleAISnapshot('liureng', buildLiuRengSnapshotText(
			saveParams,
			liureng,
			runyear,
			chartObj,
			guirengType,
			wuxing,
			appliedBirth && appliedBirth.gender ? appliedBirth.gender.value : 1
		), {
			date: saveParams.date,
			time: saveParams.time,
			zone: saveParams.zone,
			lon: saveParams.lon,
			lat: saveParams.lat,
		});
	}

	genRunYearParams(){
		let flds = getAppliedBirth(this.state);
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
		const params = {
			ad: flds.date.value.ad,
			date: flds.date.value.format('YYYY-MM-DD'),
			time: flds.time.value.format('HH:mm'),
			zone: flds.date.value.zone,
			lon: flds.lon.value,
			lat: flds.lat.value,
			gender: flds.gender.value,
			after23NewDay: flds.after23NewDay.value,
			guaYearGanZi: resolveGuaYearGanZi(this.state.liureng),
			guaDate: guaDate,
			guaTime: guaTime,
			guaAd: guaAd,
			guaZone: guaZone,
			guaLon: guaLon,
			guaLat: guaLat,
			guaAfter23NewDay: guaAfter23,
		}
		return params;
	}

	genGodsParams(fields){
		let params = null;
		let flds = fields ? fields : this.props.fields;
		if(flds.params){
			let dtparts = flds.params.birth.split(' ');
			params = {
				...flds.params,
				date: dtparts[0],
				time: dtparts[1],
			};
	
		}else{
			params = {
				date: flds.date.value.format('YYYY-MM-DD'),
				time: flds.time.value.format('HH:mm'),
				zone: flds.date.value.zone,
				ad: flds.date.value.ad,
				lon: flds.lon.value,
				lat: flds.lat.value,
			};	
		}

		if(this.props.value){
			let chartObj = this.props.value.chart;
			if(chartObj){
				let yue = null;
				for(let i=0; i<chartObj.objects.length; i++){
					let obj = chartObj.objects[i];
					if(obj.id === AstroConst.SUN){
						yue = LRConst.getSignZi(obj.sign);
						break;
					}
				}	
				// params.yue = yue;	
				// params.isDiurnal = chartObj.isDiurnal;
			}
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
		const params = {
			ad: flds.date.value.ad,
			date: flds.date.value.format('YYYY-MM-DD'),
			time: flds.time.value.format('HH:mm'),
			zone: flds.date.value.zone,
			lon: flds.lon.value,
			lat: flds.lat.value,
			after23NewDay: flds.after23NewDay.value,
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
			}
			return ganzi;
		}catch(e){
			return '';
		}
	}

	async requestGods(fields){
		if(fields === undefined || fields === null){
			return;
		}
		const params = this.genGodsParams(fields);

		const data = await request(`${Constants.ServerRoot}/liureng/gods`, {
			body: JSON.stringify(params),
		});
		const result = data[Constants.ResultKey]
		
		let dayGanZi = result.liureng.nongli.dayGanZi;
		let dayGan = dayGanZi.substr(0, 1);
		let wx = LRConst.GanZiWuXing[dayGan];
		const appliedBirth = buildBirthFields(this.state.birth, new DateTime());
		const st = {
			liureng: result.liureng,
			calcBirth: appliedBirth,
			wuxing: wx,
		};

		this.setState(st, ()=>{
			this.requestRunYear();
			this.saveLiuRengAISnapshot(params, result.liureng, this.state.runyear, wx, this.state.guireng);
		});
	}

	async requestRunYear(){
		if(this.state.liureng === null){
			return;
		}
		
		const params = this.genRunYearParams();
		const fields = this.state.calcFields ? this.state.calcFields : this.props.fields;
		if(!fields || !fields.date || !fields.date.value){
			return;
		}
		const birthFields = getAppliedBirth(this.state);
		if(!birthFields || !birthFields.date || !birthFields.date.value){
			return;
		}
		if(birthFields.date.value.year > fields.date.value.year){
			Modal.error({
				title: '出生年份必须小于卜卦年份'
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
				title: '无法识别卜卦年份干支，请先起课后再试',
			});
			return;
		}

		let result = fallbackRunYear ? { ...fallbackRunYear } : {};
		try{
			const data = await request(`${Constants.ServerRoot}/liureng/runyear`, {
				body: JSON.stringify(params),
			});
			const serverRes = data[Constants.ResultKey] ? { ...data[Constants.ResultKey] } : {};
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
		
		const st = {
			runyear: result,
		};

		this.setState(st, ()=>{
			this.saveLiuRengAISnapshot(null, this.state.liureng, result, this.state.wuxing, this.state.guireng);
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
		const snapshot = loadModuleAISnapshot('liureng');
		const payload = {
			module: 'liureng',
			snapshot: snapshot,
			liureng: this.state.liureng,
			runyear: displayRunYear,
			wuxing: this.state.wuxing,
			guireng: this.state.guireng,
		};
		if(this.props.dispatch){
			this.props.dispatch({
				type: 'astro/openDrawer',
				payload: {
					key: 'caseadd',
					record: {
						event: `六壬占断 ${divTime}`,
						caseType: 'liureng',
						divTime: divTime,
						zone: flds.zone.value,
						lat: flds.lat.value,
						lon: flds.lon.value,
						gpsLat: flds.gpsLat.value,
						gpsLon: flds.gpsLon.value,
						pos: flds.pos ? flds.pos.value : '',
						payload: payload,
						sourceModule: 'liureng',
					},
				},
			});
		}
	}

	genWuXingDoms(){
		let res = LRConst.WuXing.map((item, idx)=>{
			return (
				<Option key={idx} value={item.elem}>十二长生：{item.elem}--{item.ganzi}</Option>
			);
		});
		return res;

	}

	componentDidMount(){
		this.unmounted = false;
	}

	componentWillUnmount(){
		this.unmounted = true;
	}

	render(){
		let height = this.props.height ? this.props.height : 760;
		if(height === '100%'){
			height = 'calc(100% - 70px)'
		}else{
			height = height - 20
		}

		let chart = this.state.calcChart ? this.state.calcChart : null;
		let chartFields = this.state.calcFields ? this.state.calcFields : this.props.fields;
		const appliedBirth = getAppliedBirth(this.state);
		const displayRunYear = resolveDisplayRunYear(this.state.runyear, appliedBirth, chartFields);

		let wxdoms = this.genWuXingDoms();
		return (
			<div>
				<Row gutter={6}>
					<Col span={16}>
						<LiuRengChart 
							value={chart} 
							liureng={this.state.liureng}
							runyear={displayRunYear}
							gender={appliedBirth && appliedBirth.gender ? appliedBirth.gender.value : -1}
							zhangshengElem={this.state.wuxing}
							guireng={this.state.guireng}
							height={height} 
							fields={chartFields}  
							chartDisplay={this.props.chartDisplay}
							planetDisplay={this.props.planetDisplay}
						/>
					</Col>
					<Col span={8}>
						<Row>
							<Col span={24}>
								<LiuRengInput 
									fields={this.props.fields} 
									onFieldsChange={this.onFieldsChange}
								/>
							</Col>
						</Row>
						<Row style={{ marginTop: 8 }}>
							<Col span={24}>
								<Button type='primary' style={{ width: '100%' }} onClick={this.clickStartPaiPan}>起课</Button>
							</Col>
						</Row>
						<Row style={{ marginTop: 8 }}>
							<Col span={24}>
								<Button style={{ width: '100%' }} onClick={this.clickSaveCase}>保存</Button>
							</Col>
						</Row>
						<Divider orientation='left'>卜卦人出生时间</Divider>
						<Row>
							<Col span={24}>
								<LiuRengBirthInput 
									fields={this.state.birth} 
									onFieldsChange={this.onBirthChange}
									requireConfirm={true}
								/>
							</Col>
						</Row>
						<Divider />
						<Row>
							<Col span={24}>
								<Select value={this.state.wuxing} onChange={this.onWuXingChange} style={{width: '100%'}}>
									{wxdoms}
								</Select>
							</Col>
							<Col span={24}>
								<Select value={this.state.guireng} onChange={this.onGuiRengChange} style={{width: '100%'}}>
									<Option value={0}>六壬法贵人</Option>
									<Option value={1}>遁甲法贵人</Option>
									<Option value={2}>星占法贵人</Option>
								</Select>
							</Col>
						</Row>

					</Col>
				</Row>
			</div>

		);
	}
}

export default LiuRengMain;
