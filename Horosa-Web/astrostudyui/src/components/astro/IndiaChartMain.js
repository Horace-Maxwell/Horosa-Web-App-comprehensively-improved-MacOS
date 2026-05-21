import { Component } from 'react';
import { createPortal } from 'react-dom';
import moment from 'moment';
import IndiaChart, { fieldsToParams, requestIndiaChartData } from './IndiaChart';
import DateTime from '../comp/DateTime';
import SpaceTimePanel from '../comp/SpaceTimePanel';
import {convertLatToStr, convertLonToStr} from './AstroHelper';
import * as AstroConst from '../../constants/AstroConst';
import { XQSegmented as Segmented, XQSelect as Select, XQTabs as Tabs } from '../xq-ui';
import XQIcon from '../xq-icons';

const TabPane = Tabs.TabPane;
const {Option} = Select;
const DASHA_YEAR_DAYS = 365.25;
const NAKSHATRA_SIZE = 360 / 27;
const INDIA_DEGREE_DISPLAY_DEGREE = 'degree';
const INDIA_DEGREE_DISPLAY_FULL = 'full';
const INDIA_DEGREE_DISPLAY_OPTIONS = [
	{ value: INDIA_DEGREE_DISPLAY_DEGREE, label: '只度数' },
	{ value: INDIA_DEGREE_DISPLAY_FULL, label: '度数+分数' },
];
const INDIA_QUICK_ACTIONS = [
	{ key: 'd1', label: '命盘', icon: 'sidePlanets', action: 'tab', tab: 'Natal' },
	{ key: 'd9', label: '合伴', icon: 'sideHouses', action: 'tab', tab: 'Navamsa' },
	{ key: 'd10', label: '事业', icon: 'quickPrimary', action: 'tab', tab: 'Dasamsa' },
	{ key: 'd12', label: '父辈', icon: 'quickFirdaria', action: 'tab', tab: 'Dwadasamsa' },
	{ key: 'north', label: '北印', icon: 'sideStyle', action: 'style', style: AstroConst.INDIA_CHART_STYLE_NORTH },
	{ key: 'south', label: '南印', icon: 'quickReturn', action: 'style', style: AstroConst.INDIA_CHART_STYLE_SOUTH },
	{ key: 'east', label: '东印', icon: 'quickTransit', action: 'style', style: AstroConst.INDIA_CHART_STYLE_EAST },
	{ key: 'dasha', label: '大运', icon: 'quickNote', action: 'infoTab', infoTab: '3' },
];
const DASHA_SEQUENCE = [
	{ key: 'Ketu', label: '计都', en: 'Ketu', years: 7 },
	{ key: 'Venus', label: '金星', en: 'Venus', years: 20 },
	{ key: 'Sun', label: '太阳', en: 'Sun', years: 6 },
	{ key: 'Moon', label: '月亮', en: 'Moon', years: 10 },
	{ key: 'Mars', label: '火星', en: 'Mars', years: 7 },
	{ key: 'Rahu', label: '罗睺', en: 'Rahu', years: 18 },
	{ key: 'Jupiter', label: '木星', en: 'Jupiter', years: 16 },
	{ key: 'Saturn', label: '土星', en: 'Saturn', years: 19 },
	{ key: 'Mercury', label: '水星', en: 'Mercury', years: 17 },
];
const DASHA_BY_KEY = DASHA_SEQUENCE.reduce((map, item, idx)=>{
	map[item.key] = {
		...item,
		idx,
	};
	return map;
}, {});

const NAKSHATRAS = [
	['Ashwini', 'Ketu'], ['Bharani', 'Venus'], ['Krittika', 'Sun'],
	['Rohini', 'Moon'], ['Mrigashira', 'Mars'], ['Ardra', 'Rahu'],
	['Punarvasu', 'Jupiter'], ['Pushya', 'Saturn'], ['Ashlesha', 'Mercury'],
	['Magha', 'Ketu'], ['Purva Phalguni', 'Venus'], ['Uttara Phalguni', 'Sun'],
	['Hasta', 'Moon'], ['Chitra', 'Mars'], ['Swati', 'Rahu'],
	['Vishakha', 'Jupiter'], ['Anuradha', 'Saturn'], ['Jyeshtha', 'Mercury'],
	['Mula', 'Ketu'], ['Purva Ashadha', 'Venus'], ['Uttara Ashadha', 'Sun'],
	['Shravana', 'Moon'], ['Dhanishta', 'Mars'], ['Shatabhisha', 'Rahu'],
	['Purva Bhadrapada', 'Jupiter'], ['Uttara Bhadrapada', 'Saturn'], ['Revati', 'Mercury'],
];

function normalizeDegree(value){
	let num = Number(value);
	if(!Number.isFinite(num)){
		return null;
	}
	num = num % 360;
	if(num < 0){
		num += 360;
	}
	return num;
}

function getChartObjects(chartObj){
	const chart = chartObj && chartObj.chart ? chartObj.chart : chartObj;
	if(chart && chart.objects && Array.isArray(chart.objects)){
		return chart.objects;
	}
	return [];
}

function getMoonObject(chartObj){
	const objects = getChartObjects(chartObj);
	for(let i=0; i<objects.length; i++){
		if(objects[i] && objects[i].id === AstroConst.MOON){
			return objects[i];
		}
	}
	return null;
}

function momentFromFieldValue(value, fallbackFormat){
	if(!value){
		return null;
	}
	if(value.format){
		const formatted = fallbackFormat ? value.format(fallbackFormat) : value.format('YYYY-MM-DD HH:mm:ss');
		const parsedFormatted = fallbackFormat ? moment(formatted, fallbackFormat) : moment(formatted, 'YYYY-MM-DD HH:mm:ss');
		return parsedFormatted.isValid() ? parsedFormatted : null;
	}
	if(value.year && value.month && value.date && value.hour !== undefined){
		return moment({
			year: value.ad < 0 ? -Math.abs(value.year) + 1 : Math.abs(value.year),
			month: Math.max(0, value.month - 1),
			date: value.date,
			hour: value.hour,
			minute: value.minute || 0,
			second: value.second || 0,
			millisecond: 0,
		});
	}
	const parsed = fallbackFormat ? moment(value, fallbackFormat) : moment(value);
	return parsed.isValid() ? parsed : null;
}

function buildBirthMoment(fields){
	if(!fields || !fields.date || !fields.time || !fields.date.value || !fields.time.value){
		return null;
	}
	const birth = momentFromFieldValue(fields.date.value, 'YYYY-MM-DD');
	const time = momentFromFieldValue(fields.time.value, 'HH:mm:ss');
	if(!birth || !time){
		return null;
	}
	if(birth.hour && time.hour){
		birth.hour(time.hour());
		birth.minute(time.minute());
		birth.second(time.second ? time.second() : 0);
		birth.millisecond(0);
	}
	return birth;
}

function addDashaYears(momentValue, years){
	if(!momentValue || !momentValue.clone){
		return null;
	}
	return momentValue.clone().add(years * DASHA_YEAR_DAYS * 24 * 60 * 60 * 1000, 'milliseconds');
}

function subtractDashaYears(momentValue, years){
	if(!momentValue || !momentValue.clone){
		return null;
	}
	return momentValue.clone().subtract(years * DASHA_YEAR_DAYS * 24 * 60 * 60 * 1000, 'milliseconds');
}

function formatDuration(years){
	const totalMonths = Math.max(0, Math.round(years * 12));
	const y = Math.floor(totalMonths / 12);
	const m = totalMonths % 12;
	if(y && m){
		return `${y}年${m}月`;
	}
	if(y){
		return `${y}年`;
	}
	return `${m}月`;
}

function formatAge(years){
	if(years < 0){
		return `出生前${Math.abs(years).toFixed(1)}年`;
	}
	return `${years.toFixed(1)}岁`;
}

function buildDashaSubPeriods(item){
	if(item && Array.isArray(item.antardashas)){
		return item.antardashas.map((subItem)=>({
			...subItem,
			lord: normalizeDashaLord(subItem.lord),
			start: moment(subItem.start),
			end: moment(subItem.end),
		}));
	}
	if(!item || !item.start || !item.lord){
		return [];
	}
	const subItems = [];
	let start = item.start.clone();
	let lordIndex = Number.isFinite(item.lord.idx)
		? item.lord.idx
		: DASHA_SEQUENCE.findIndex((lord)=>lord.key === item.lord.key);
	if(lordIndex < 0){
		return [];
	}
	for(let i=0; i<DASHA_SEQUENCE.length; i++){
		const currentLordIndex = lordIndex % DASHA_SEQUENCE.length;
		const lord = {
			...DASHA_SEQUENCE[currentLordIndex],
			idx: currentLordIndex,
		};
		const years = item.years * lord.years / 120;
		const end = i === DASHA_SEQUENCE.length - 1 ? item.end.clone() : addDashaYears(start, years);
		if(!end || !end.clone){
			break;
		}
		subItems.push({
			lord,
			years,
			start: start.clone(),
			end: end.clone(),
		});
		start = end;
		lordIndex += 1;
	}
	return subItems;
}

function normalizeDashaLord(lord){
	if(!lord){
		return {
			key: '',
			label: '—',
			en: '',
			years: 0,
		};
	}
	const local = DASHA_BY_KEY[lord.key] || DASHA_SEQUENCE.find((item)=>item.en === lord.key || item.key === lord.key);
	return {
		...(local || {}),
		...lord,
		en: lord.en || lord.key || (local ? local.en : ''),
		label: lord.label || (local ? local.label : lord.key),
	};
}

function buildVimshottariDasha(chartObj, fields){
	const backend = chartObj && chartObj.jyotish && chartObj.jyotish.dasha && chartObj.jyotish.dasha.vimshottari;
	if(backend && backend.available && Array.isArray(backend.mahadashas)){
		return {
			backend: true,
			moon: null,
			moonLon: backend.moonLongitude,
			nakshatra: {
				...(backend.moonNakshatra || {}),
				lord: normalizeDashaLord(backend.firstLord || (backend.moonNakshatra ? {key: backend.moonNakshatra.lord} : null)),
			},
			firstBalance: backend.firstBalanceYears,
			firstElapsed: backend.firstElapsedYears,
			items: backend.mahadashas.map((item)=>({
				...item,
				lord: normalizeDashaLord(item.lord),
				start: moment(item.start),
				end: moment(item.end),
				active: !!item.active,
				isBirthBalance: !!item.birthBalance,
			})),
		};
	}
	const moon = getMoonObject(chartObj);
	const moonLon = normalizeDegree(moon ? moon.lon : null);
	const birth = buildBirthMoment(fields);
	if(moonLon === null || !birth){
		return null;
	}
	const nakIndex = Math.min(26, Math.floor(moonLon / NAKSHATRA_SIZE));
	const nakStart = nakIndex * NAKSHATRA_SIZE;
	const progress = (moonLon - nakStart) / NAKSHATRA_SIZE;
	const remainingRatio = Math.max(0, Math.min(1, 1 - progress));
	const nak = NAKSHATRAS[nakIndex];
	const firstLord = DASHA_BY_KEY[nak[1]];
	if(!firstLord){
		return null;
	}
	const firstBalance = firstLord.years * remainingRatio;
	const firstElapsed = firstLord.years - firstBalance;
	const items = [];
	if(!birth.clone){
		return null;
	}
	let start = subtractDashaYears(birth, firstElapsed);
	if(!start || !start.clone){
		return null;
	}
	let lordIndex = firstLord.idx;
	for(let i=0; i<10; i++){
		const currentLordIndex = lordIndex % DASHA_SEQUENCE.length;
		const lord = {
			...DASHA_SEQUENCE[currentLordIndex],
			idx: currentLordIndex,
		};
		const years = lord.years;
		const end = addDashaYears(start, years);
		if(!end || !end.clone){
			break;
		}
		items.push({
			lord,
			years,
			start: start.clone(),
			end: end.clone(),
			startAge: start.diff(birth, 'days', true) / DASHA_YEAR_DAYS,
			endAge: end.diff(birth, 'days', true) / DASHA_YEAR_DAYS,
			isBirthBalance: i === 0,
			active: Date.now() >= start.valueOf() && Date.now() < end.valueOf(),
		});
		start = end;
		lordIndex += 1;
	}
	return {
		moon,
		moonLon,
		nakshatra: {
			name: nak[0],
			index: nakIndex + 1,
			progress,
			remainingRatio,
			lord: firstLord,
		},
		firstBalance,
		firstElapsed,
		items,
	};
}

function getJyotish(chartObj){
	return chartObj && chartObj.jyotish ? chartObj.jyotish : null;
}

function formatJyotishDate(value){
	if(!value){
		return '—';
	}
	if(value.format){
		return value.format('YYYY-MM-DD');
	}
	const parsed = moment(value);
	return parsed.isValid() ? parsed.format('YYYY-MM-DD') : `${value}`;
}

function formatDegree(value){
	const num = Number(value);
	if(!Number.isFinite(num)){
		return '—';
	}
	const deg = Math.floor(num);
	const min = Math.floor((num - deg) * 60);
	return `${deg}°${`${min}`.padStart(2, '0')}′`;
}

function getJyotishPlanetStates(jyotish){
	return jyotish && jyotish.strengths && Array.isArray(jyotish.strengths.planetaryStates)
		? jyotish.strengths.planetaryStates
		: [];
}

function getJyotishDasha(chartObj){
	return chartObj && chartObj.jyotish && chartObj.jyotish.dasha ? chartObj.jyotish.dasha.vimshottari : null;
}

function normalizeChartDateKey(value){
	return `${value || ''}`.replace(/\//g, '-');
}

function buildJyotishParamsKey(params){
	if(!params){
		return '';
	}
	return [
		normalizeChartDateKey(params.date),
		params.time || '',
		params.ad,
		params.zone || '',
		params.lon || '',
		params.lat || '',
		params.gpsLon,
		params.gpsLat,
		params.hsys,
		params.indiaAyanamsa || AstroConst.INDIA_AYANAMSA_DEFAULT,
	].join('|');
}

function cloneIndiaFieldValue(value){
	if(value && value.clone){
		try{
			return value.clone();
		}catch(e){}
	}
	if(value && typeof value === 'object'){
		return {
			...value,
		};
	}
	return value;
}

function cloneIndiaFieldsForJyotish(fields){
	if(!fields){
		return null;
	}
	const cloned = {
		...fields,
	};
	Object.keys(cloned).forEach((key)=>{
		const item = cloned[key];
		if(item && typeof item === 'object' && Object.prototype.hasOwnProperty.call(item, 'value')){
			cloned[key] = {
				...item,
				value: cloneIndiaFieldValue(item.value),
			};
		}
	});
	return cloned;
}

function resolveJyotishChartObj(state, fields){
	const activeKey = buildDashaFieldsKey(fields);
	if(!state || !activeKey){
		return null;
	}
	if(state.mainChartObj && state.mainChartObj.jyotish && state.mainChartKey === activeKey){
		return state.mainChartObj;
	}
	return (state.dashaChartObj && state.dashaChartKey === activeKey)
		? state.dashaChartObj
		: null;
}

function hasUsableJyotishChart(state, fieldsKey){
	if(!state || !fieldsKey){
		return false;
	}
	if(state.mainChartObj && state.mainChartObj.jyotish && state.mainChartKey === fieldsKey){
		return true;
	}
	if(state.dashaChartObj && state.dashaChartObj.jyotish && state.dashaChartKey === fieldsKey){
		return true;
	}
	return false;
}

function buildDashaFieldsKey(fields){
	if(!fields || !fields.date || !fields.time){
		return '';
	}
	const dateMoment = momentFromFieldValue(fields.date.value, 'YYYY-MM-DD');
	const timeMoment = momentFromFieldValue(fields.time.value, 'HH:mm:ss');
	return [
		dateMoment ? dateMoment.format('YYYY-MM-DD') : '',
		timeMoment ? timeMoment.format('HH:mm:ss') : '',
		fields.ad ? fields.ad.value : '',
		fields.zone ? fields.zone.value : '',
		fields.lon ? fields.lon.value : '',
		fields.lat ? fields.lat.value : '',
		fields.gpsLon ? fields.gpsLon.value : '',
		fields.gpsLat ? fields.gpsLat.value : '',
		fields.indiaHsys ? fields.indiaHsys.value : AstroConst.INDIA_HOUSE_SYSTEM_DEFAULT,
		fields.indiaAyanamsa ? fields.indiaAyanamsa.value : AstroConst.INDIA_AYANAMSA_DEFAULT,
	].join('|');
}

function canBuildIndiaChartParams(fields){
	const nullableKeys = ['name', 'pos'];
	const requiredKeys = [
		'date', 'time', 'ad', 'zone', 'lat', 'lon', 'gpsLat', 'gpsLon',
		'tradition', 'strongRecption', 'simpleAsp', 'virtualPointReceiveAsp',
		'name', 'pos',
	];
	return requiredKeys.every((key)=>fields && fields[key] && fields[key].value !== undefined
		&& (nullableKeys.indexOf(key) >= 0 || fields[key].value !== null));
}

class IndiaChartMain extends Component{

	constructor(props) {
		super(props);
		this.state = {
			currentTab: "Natal",
			currentFractal: 1,
			dashaChartObj: null,
			dashaLoading: false,
			dashaFieldsKey: '',
			dashaChartKey: '',
			dashaPopoverItem: null,
			dashaPopoverStyle: null,
			mainChartObj: null,
			mainChartKey: '',
			activeJyotishFields: null,
			activeJyotishKey: '',
			jyotishTab: '3',
			indiaHsysValue: null,
			indiaAyanamsaValue: null,
			degreeDisplayMode: INDIA_DEGREE_DISPLAY_DEGREE,
			hook: {
				Natal:{
					txt:'命盘',
					fractal: 1,
					fun: null
				},
				Hora:{
					txt:'财产',
					fractal: 2,
					fun: null
				},
				Drekkana:{
					txt:'兄妹',
					fractal: 3,
					fun: null
				},
				Chaturthamsa:{
					txt:'资质',
					fractal: 4,
					fun: null
				},
				Panchamsa:{
					txt:'世俗',
					fractal: 5,
					fun: null
				},
				Shashthamsa:{
					txt:'疾病',
					fractal: 6,
					fun: null
				},
				Saptamsa:{
					txt:'子嗣',
					fractal: 7,
					fun: null
				},
				Ashthamsa:{
					txt:'困难',
					fractal: 8,
					fun: null
				},
				Navamsa:{
					txt:'合作',
					fractal: 9,
					fun: null
				},
				Dasamsa:{
					txt:'事业',
					fractal: 10,
					fun: null
				},
				Rudramsa:{
					txt:'增长',
					fractal: 11,
					fun: null
				},
				Dwadasamsa:{
					txt:'父辈',
					fractal: 12,
					fun: null
				},
				Shodasamsa:{
					txt:'座驾',
					fractal: 16,
					fun: null
				},
				Vimsamsa:{
					txt:'灵魂',
					fractal: 20,
					fun: null
				},
				Chaturvimsamsa:{
					txt:'教育',
					fractal: 24,
					fun: null
				},
				Nakshatramsa:{
					txt:'生命',
					fractal: 27,
					fun: null
				},
				Trimsamsa:{
					txt: null,
					fractal: 30,
					fun: null
				},
				Khavedamsa:{
					txt:'母系',
					fractal: 40,
					fun: null
				},
				Akshavedamsa:{
					txt:'父系',
					fractal: 45,
					fun: null
				},
				Shashtyamsa:{
					txt: null,
					fractal: 60,
					fun: null
				},
	
			},
		};

		this.changeTab = this.changeTab.bind(this);
		this.onFieldsChange = this.onFieldsChange.bind(this);
		this.changeTime = this.changeTime.bind(this);
			this.changeGeo = this.changeGeo.bind(this);
			this.changeHsys = this.changeHsys.bind(this);
			this.changeIndiaAyanamsa = this.changeIndiaAyanamsa.bind(this);
			this.changeDegreeDisplayMode = this.changeDegreeDisplayMode.bind(this);
			this.changeIndiaChartStyle = this.changeIndiaChartStyle.bind(this);
		this.requestDashaChart = this.requestDashaChart.bind(this);
		this.showDashaSubPopover = this.showDashaSubPopover.bind(this);
		this.hideDashaSubPopover = this.hideDashaSubPopover.bind(this);
		this.handleQuickAction = this.handleQuickAction.bind(this);
		this.changeJyotishTab = this.changeJyotishTab.bind(this);
		this.handleMainChartLoad = this.handleMainChartLoad.bind(this);
			this.lastDashaRequestKey = '';
			this.lastObservedFieldsKey = '';
			this.mainIndiaChartRef = null;

		this.tmHook = {
			getValue: null,
		};

		if(this.props.hook){
			this.props.hook.fun = (fields)=>{
				let hook = this.state.hook;
				if(hook[this.state.currentTab].fun){
					let fld = {
						...fields,
						chartnum: {
							value: this.state.currentFractal
						}
					}
					hook[this.state.currentTab].fun(fld)
				}
				this.requestDashaChart(this.withIndiaOptionFields(fields));
			};
		}

	}


	changeTab(key){		
		let hook = this.state.hook;
		this.setState({
			currentTab: key,
			currentFractal: hook[key].fractal
		}, ()=>{
			if(this.state.hook[key] && this.state.hook[key].fun){
				this.state.hook[key].fun();
			}
			if(this.props.dispatch){
				this.props.dispatch({
					type: 'astro/save',
					payload: {
						currentSubTab: key,
					}
				});
			}	
		});
	}

	onFieldsChange(values){
		let flds = this.withIndiaOptionFields(this.props.fields);
		if(this.props.onChange){
			try{
				const changedFields = this.props.onChange(values);
				if(changedFields){
					flds = this.withIndiaOptionFields(changedFields);
				}
			}catch(e){
				if(typeof window !== 'undefined' && window.console){
					window.console.error(e);
				}
			}
		}
		if(!flds){
			return;
		}
		flds.chartnum = {};
		flds.chartnum.value = this.state.currentFractal;
		let hook = this.state.hook[this.state.currentTab];
		if(hook.fun){
			hook.fun(flds);
		}
		this.requestDashaChart(flds);
	}

	changeTime(value){
		let dt = value.time;
		this.onFieldsChange({
			__confirmed: !!value.confirmed,
			date: {
				value: dt.clone(),
			},
			time:{
				value: dt.clone(),
			},
			ad:{
				value: dt.ad,
			},
			zone:{
				value: dt.zone,
			}
		});
	}

	changeGeo(rec){
		let dt = this.tmHook.getValue ? this.tmHook.getValue().value : null;
		const patch = {
			lon: {
				value: convertLonToStr(rec.lng),
			},
			lat: {
				value: convertLatToStr(rec.lat),
			},
			gpsLon: {
				value: rec.gpsLng
			},
			gpsLat: {
				value: rec.gpsLat
			},
		};
		if(dt){
			patch.date = {
				value: dt.clone(),
			};
			patch.time = {
				value: dt.clone(),
			};
			patch.ad = {
				value: dt.ad,
			};
			patch.zone = {
				value: dt.zone,
			};
		}
		this.onFieldsChange(patch);
	}

	changeHsys(value){
		const indiaHsys = AstroConst.normalizeIndiaHouseSystem(value);
		const indiaAyanamsa = this.state.indiaAyanamsaValue !== null && this.state.indiaAyanamsaValue !== undefined
			? this.state.indiaAyanamsaValue
			: (this.props.fields && this.props.fields.indiaAyanamsa ? AstroConst.normalizeIndiaAyanamsa(this.props.fields.indiaAyanamsa.value) : AstroConst.INDIA_AYANAMSA_DEFAULT);
		this.setState({
			indiaHsysValue: indiaHsys,
			mainChartObj: null,
			mainChartKey: '',
		}, ()=>{
			this.requestDashaChart(this.withIndiaOptionFields(this.props.fields, {
				indiaHsys,
				indiaAyanamsa,
			}));
		});
	}

	changeIndiaAyanamsa(value){
		const indiaAyanamsa = AstroConst.normalizeIndiaAyanamsa(value);
		const indiaHsys = this.state.indiaHsysValue !== null && this.state.indiaHsysValue !== undefined
			? this.state.indiaHsysValue
			: (this.props.fields && this.props.fields.indiaHsys ? AstroConst.normalizeIndiaHouseSystem(this.props.fields.indiaHsys.value) : AstroConst.INDIA_HOUSE_SYSTEM_DEFAULT);
		this.setState({
			indiaAyanamsaValue: indiaAyanamsa,
			mainChartObj: null,
			mainChartKey: '',
		}, ()=>{
			this.requestDashaChart(this.withIndiaOptionFields(this.props.fields, {
				indiaHsys,
				indiaAyanamsa,
			}));
		});
	}

	changeDegreeDisplayMode(value){
		const degreeDisplayMode = value === INDIA_DEGREE_DISPLAY_FULL
			? INDIA_DEGREE_DISPLAY_FULL
			: INDIA_DEGREE_DISPLAY_DEGREE;
		this.setState({
			degreeDisplayMode,
		});
	}

	withIndiaOptionFields(fields, optionOverrides = {}){
		if(!fields){
			return fields;
		}
		const indiaHsys = optionOverrides.indiaHsys !== undefined && optionOverrides.indiaHsys !== null
			? AstroConst.normalizeIndiaHouseSystem(optionOverrides.indiaHsys)
			: (this.state.indiaHsysValue !== null && this.state.indiaHsysValue !== undefined
			? this.state.indiaHsysValue
			: (fields.indiaHsys ? AstroConst.normalizeIndiaHouseSystem(fields.indiaHsys.value) : AstroConst.INDIA_HOUSE_SYSTEM_DEFAULT));
		const indiaAyanamsa = optionOverrides.indiaAyanamsa !== undefined && optionOverrides.indiaAyanamsa !== null
			? AstroConst.normalizeIndiaAyanamsa(optionOverrides.indiaAyanamsa)
			: (this.state.indiaAyanamsaValue !== null && this.state.indiaAyanamsaValue !== undefined
			? this.state.indiaAyanamsaValue
			: (fields.indiaAyanamsa ? AstroConst.normalizeIndiaAyanamsa(fields.indiaAyanamsa.value) : AstroConst.INDIA_AYANAMSA_DEFAULT));
		return {
			...fields,
			indiaHsys: {
				...(fields.indiaHsys || { name: ['indiaHsys'] }),
				value: indiaHsys,
			},
			indiaAyanamsa: {
				...(fields.indiaAyanamsa || { name: ['indiaAyanamsa'] }),
				value: indiaAyanamsa,
			},
		};
	}

	changeIndiaChartStyle(value){
		const indiaChartStyle = AstroConst.normalizeIndiaChartStyle(value && value.target ? value.target.value : value);
		if(this.props.dispatch){
			this.props.dispatch({
				type: 'app/save',
				payload: {
					indiaChartStyle,
				},
			});
		}
	}

	handleQuickAction(item){
		if(!item){
			return;
		}
		if(item.action === 'tab' && item.tab){
			this.changeTab(item.tab);
			this.changeJyotishTab('1');
			return;
		}
		if(item.action === 'style' && item.style){
			this.changeIndiaChartStyle(item.style);
			return;
		}
		if(item.action === 'infoTab' && item.infoTab){
			this.changeJyotishTab(item.infoTab);
		}
	}

	async requestDashaChart(fields){
		const sourceFields = fields || this.props.fields;
		if(!canBuildIndiaChartParams(sourceFields)){
			return;
		}
		const jyotishFields = cloneIndiaFieldsForJyotish(sourceFields);
		const dashaFieldsKey = buildDashaFieldsKey(jyotishFields);
		const alreadyHasData = hasUsableJyotishChart(this.state, dashaFieldsKey);
		if(!dashaFieldsKey || (dashaFieldsKey === this.lastDashaRequestKey && (this.state.dashaLoading || alreadyHasData))){
			if(dashaFieldsKey && dashaFieldsKey !== this.state.activeJyotishKey){
				this.setState({
					activeJyotishFields: jyotishFields,
					activeJyotishKey: dashaFieldsKey,
				});
			}
			return;
		}
		this.lastDashaRequestKey = dashaFieldsKey;
		let params = null;
		try{
			params = fieldsToParams(jyotishFields);
			params.chartnum = 1;
		}catch(e){
			this.lastDashaRequestKey = '';
			return;
		}
		this.setState({
			dashaChartObj: null,
			dashaChartKey: '',
			dashaLoading: true,
			dashaFieldsKey,
			mainChartObj: this.state.mainChartKey === dashaFieldsKey ? this.state.mainChartObj : null,
			mainChartKey: this.state.mainChartKey === dashaFieldsKey ? this.state.mainChartKey : '',
			activeJyotishFields: jyotishFields,
			activeJyotishKey: dashaFieldsKey,
		});
		try{
			const dashaChartObj = await requestIndiaChartData(params);
			if(this.state.dashaFieldsKey === dashaFieldsKey){
				this.setState({
					dashaChartObj,
					dashaChartKey: dashaFieldsKey,
					mainChartObj: dashaChartObj || null,
					mainChartKey: dashaFieldsKey,
					dashaLoading: false,
				});
			}
		}catch(e){
			if(this.state.dashaFieldsKey === dashaFieldsKey){
				this.setState({
					dashaChartObj: null,
					dashaChartKey: '',
					dashaLoading: false,
				});
			}
		}
	}

	componentDidMount(){
		let hook = this.state.hook;
		if(hook[this.state.currentTab].fun){
			hook[this.state.currentTab].fun()
		}
		const fields = this.withIndiaOptionFields(this.props.fields);
		this.lastObservedFieldsKey = buildDashaFieldsKey(fields);
		this.requestDashaChart(fields);
	}

	componentDidUpdate(prevProps, prevState){
		const fields = this.withIndiaOptionFields(this.props.fields);
		const currentFieldsKey = buildDashaFieldsKey(fields);
		if(currentFieldsKey && currentFieldsKey !== this.lastObservedFieldsKey){
			this.lastObservedFieldsKey = currentFieldsKey;
			this.requestDashaChart(fields);
			return;
		}
		if(currentFieldsKey && currentFieldsKey !== this.lastDashaRequestKey && !hasUsableJyotishChart(this.state, currentFieldsKey) && !this.state.dashaLoading){
			this.requestDashaChart(fields);
		}
	}

	showDashaSubPopover(item, e){
		if(typeof window === 'undefined' || !e || !e.currentTarget || !e.currentTarget.getBoundingClientRect){
			return;
		}
		const rect = e.currentTarget.getBoundingClientRect();
		const margin = 12;
		const panelWidth = Math.min(380, Math.max(300, window.innerWidth - margin * 2));
		let left = rect.left - panelWidth - margin;
		if(left < margin){
			left = rect.right + margin;
		}
		if(left + panelWidth > window.innerWidth - margin){
			left = Math.max(margin, window.innerWidth - panelWidth - margin);
		}
		const top = Math.max(88, Math.min(window.innerHeight - 88, rect.top + rect.height / 2));
		this.setState({
			dashaPopoverItem: item,
			dashaPopoverStyle: {
				left,
				top,
				width: panelWidth,
			},
		});
	}

	hideDashaSubPopover(){
		this.setState({
			dashaPopoverItem: null,
			dashaPopoverStyle: null,
		});
	}

	changeJyotishTab(key){
		this.setState({
			jyotishTab: key,
		});
	}

	handleMainChartLoad(chartObj, params){
		const mainChartKey = buildJyotishParamsKey(params);
		const activeKey = this.state.activeJyotishKey || buildDashaFieldsKey(this.withIndiaOptionFields(this.props.fields));
		if(activeKey && mainChartKey && mainChartKey !== activeKey){
			return;
		}
		this.setState({
			mainChartObj: chartObj || null,
			mainChartKey,
			dashaLoading: mainChartKey && mainChartKey === activeKey && chartObj && chartObj.jyotish ? false : this.state.dashaLoading,
		});
	}

	renderJyotishNav(){
		const items = [
			{ key: '2', icon: 'note', title: '五支', sub: '起盘' },
			{ key: '3', icon: 'clock', title: '大运', sub: 'Dasha' },
			{ key: '4', icon: 'sidePlanets', title: '星曜', sub: '状态' },
			{ key: '5', icon: 'target', title: '八分', sub: 'AV' },
			{ key: '6', icon: 'quickTransit', title: 'KP', sub: '择时' },
		];
		return (
			<div className="horosa-india-input-section horosa-india-jyotish-nav">
				<div className="horosa-india-field-title">
					<XQIcon name="target" />
					<span>高级印占</span>
				</div>
				<div className="horosa-india-jyotish-buttons">
					{items.map((item)=>(
						<button
							type="button"
							key={item.key}
							className={`horosa-india-jyotish-button${this.state.jyotishTab === item.key ? ' is-active' : ''}`}
							onClick={()=>this.changeJyotishTab(item.key)}
						>
							<XQIcon name={item.icon} />
							<span>{item.title}</span>
							<em>{item.sub}</em>
						</button>
					))}
				</div>
			</div>
		);
	}

	renderDashaPanel(fields){
		const dasha = buildVimshottariDasha(resolveJyotishChartObj(this.state, fields), fields);
		if(this.state.dashaLoading && !dasha){
			return (
				<div className="horosa-india-dasha-panel">
					<div className="horosa-india-dasha-empty">大运计算中...</div>
				</div>
			);
		}
		if(!dasha){
			return (
				<div className="horosa-india-dasha-panel">
					<div className="horosa-india-dasha-empty">暂无 Vimshottari Dasha 数据</div>
				</div>
			);
		}
		const activeItem = dasha.items.find((item)=>item.active);
		return (
			<div className="horosa-india-dasha-panel">
				<div className="horosa-info-card horosa-india-dasha-overview">
					<div className="horosa-info-card-title">Vimshottari Dasha</div>
					<div className="horosa-info-row"><span>月宿</span><strong>{dasha.nakshatra.index}. {dasha.nakshatra.name}</strong></div>
					<div className="horosa-info-row"><span>起运</span><strong>{dasha.nakshatra.lord.label} · {dasha.nakshatra.lord.en}</strong></div>
					<div className="horosa-info-row"><span>出生余额</span><strong>{formatDuration(dasha.firstBalance)}</strong></div>
					<div className="horosa-info-row"><span>当前</span><strong>{activeItem ? `${activeItem.lord.label} · ${activeItem.lord.en}` : '—'}</strong></div>
				</div>
				<div className="horosa-india-dasha-list">
					{dasha.items.map((item, idx)=>this.renderDashaItem(item, idx))}
				</div>
				{this.renderDashaFloatingPopover()}
			</div>
		);
	}

	renderPanchangaPanel(fields){
		const chartObj = resolveJyotishChartObj(this.state, fields);
		const jyotish = getJyotish(chartObj);
		const panchanga = jyotish ? jyotish.panchanga : null;
		const dasha = getJyotishDasha(chartObj);
		return (
			<div className="horosa-india-summary horosa-india-jyotish-panel">
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">基本参数</div>
					<div className="horosa-info-row"><span>时间</span><strong>{fields.date.value.format('YYYY-MM-DD')} {fields.time.value.format('HH:mm:ss')}</strong></div>
					<div className="horosa-info-row"><span>地点</span><strong>{fields.lon.value} {fields.lat.value}</strong></div>
					<div className="horosa-info-row"><span>时区</span><strong>{fields.zone.value}</strong></div>
					<div className="horosa-info-row"><span>星历</span><strong>{jyotish && jyotish.engine ? 'Swiss / flatlib' : '—'}</strong></div>
					<div className="horosa-info-row"><span>黄道</span><strong>Sidereal 恒星黄道</strong></div>
					<div className="horosa-info-row"><span>岁差</span><strong>{(chartObj && chartObj.params && chartObj.params.ayanamsaLabel) || 'Lahiri / Chitrapaksha'}</strong></div>
				</div>
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">Panchanga 五支</div>
					{panchanga ? (
						<>
							<div className="horosa-info-row"><span>Vara</span><strong>{panchanga.vara.label} · {panchanga.vara.name}</strong></div>
							<div className="horosa-info-row"><span>Tithi</span><strong>{panchanga.tithi.index}. {panchanga.tithi.name} · {panchanga.tithi.paksha}</strong></div>
							<div className="horosa-info-row"><span>Nakshatra</span><strong>{panchanga.nakshatra.index}. {panchanga.nakshatra.name} P{panchanga.nakshatra.pada}</strong></div>
							<div className="horosa-info-row"><span>Yoga</span><strong>{panchanga.yoga.index}. {panchanga.yoga.name}</strong></div>
							<div className="horosa-info-row"><span>Karana</span><strong>{panchanga.karana.name}</strong></div>
							<div className="horosa-info-row"><span>日出</span><strong>{panchanga.sunrise || '—'}</strong></div>
						</>
					) : (
						<div className="horosa-india-dasha-empty">暂无五支数据</div>
					)}
				</div>
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">Dasha 摘要</div>
					{dasha && dasha.available ? (
						<>
							<div className="horosa-info-row"><span>月宿</span><strong>{dasha.moonNakshatra.index}. {dasha.moonNakshatra.name}</strong></div>
							<div className="horosa-info-row"><span>起运</span><strong>{dasha.firstLord.label} · {dasha.firstLord.key}</strong></div>
							<div className="horosa-info-row"><span>出生余额</span><strong>{formatDuration(dasha.firstBalanceYears)}</strong></div>
							<div className="horosa-info-row"><span>当前大运</span><strong>{dasha.current ? `${dasha.current.lord.label} · ${dasha.current.lord.key}` : '—'}</strong></div>
						</>
					) : (
						<div className="horosa-india-dasha-empty">暂无大运摘要</div>
					)}
				</div>
			</div>
		);
	}

	renderPlanetStatePanel(fields){
		const jyotish = getJyotish(resolveJyotishChartObj(this.state, fields));
		const states = getJyotishPlanetStates(jyotish);
		const shadbala = jyotish && jyotish.shadbala && Array.isArray(jyotish.shadbala.planets) ? jyotish.shadbala.planets : [];
		const karakas = jyotish && jyotish.jaimini ? jyotish.jaimini.charaKarakas || [] : [];
		const drishti = jyotish && Array.isArray(jyotish.grahaDrishti) ? jyotish.grahaDrishti : [];
		return (
			<div className="horosa-india-jyotish-panel">
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">Graha 状态</div>
					<div className="horosa-india-data-list">
						{states.map((item)=>(
							<div className="horosa-india-data-row" key={item.id}>
								<strong>{item.label}</strong>
								<span>{item.signLabel} {formatDegree(item.signlon)} · 宫{item.house || '—'}</span>
								<em>{item.dignity} · {item.nakshatra ? `${item.nakshatra.name} P${item.nakshatra.pada}` : '—'}</em>
							</div>
						))}
					</div>
				</div>
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">Shadbala</div>
					<div className="horosa-india-data-list">
						{shadbala.map((item)=>(
							<div className="horosa-india-data-row" key={item.id}>
								<strong>{item.label}</strong>
								<span>{item.totalRupa} Rupa · {item.totalVirupa} Virupa</span>
								<em>Sthana {item.sthana} · Dig {item.dig} · Chesta {item.chesta}</em>
							</div>
						))}
					</div>
				</div>
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">Jaimini Chara Karaka</div>
					<div className="horosa-india-data-list">
						{karakas.map((item)=>(
							<div className="horosa-india-data-row" key={item.karaka}>
								<strong>{item.karaka}</strong>
								<span>{item.label}</span>
								<em>{item.signLabel} {formatDegree(item.signlon)}</em>
							</div>
						))}
					</div>
				</div>
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">Graha Drishti</div>
					<div className="horosa-india-data-list">
						{drishti.slice(0, 14).map((item, idx)=>(
							<div className="horosa-india-data-row" key={`${item.giver}_${item.aspectHouse}_${idx}`}>
								<strong>{item.giverLabel}</strong>
								<span>{item.aspectHouse}视 · {item.targetSignLabel}</span>
								<em>{item.receives && item.receives.length ? item.receives.join('、') : '无星体承接'}</em>
							</div>
						))}
					</div>
				</div>
			</div>
		);
	}

	renderAshtakavargaPanel(fields){
		const jyotish = getJyotish(resolveJyotishChartObj(this.state, fields));
		const ashtakavarga = jyotish ? jyotish.ashtakavarga : null;
		if(!ashtakavarga || !ashtakavarga.available){
			return <div className="horosa-india-dasha-empty">暂无 Ashtakavarga 数据</div>;
		}
		const rows = ashtakavarga.sarvaBySign || [];
		return (
			<div className="horosa-india-jyotish-panel">
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">Sarvashtakavarga</div>
					<div className="horosa-india-av-grid">
						{rows.map((item)=>(
							<div className="horosa-india-av-cell" key={item.sign}>
								<span>{item.label}</span>
								<strong>{item.bindu}</strong>
							</div>
						))}
					</div>
				</div>
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">Bhinna Ashtakavarga</div>
					<div className="horosa-india-data-list">
						{Object.keys(ashtakavarga.bhinna || {}).map((planet)=>(
							<div className="horosa-india-data-row" key={planet}>
								<strong>{planet}</strong>
								<span>{Object.values(ashtakavarga.bhinna[planet]).reduce((sum, value)=>sum + value, 0)} bindu</span>
								<em>按 BPHS 表计算</em>
							</div>
						))}
					</div>
				</div>
			</div>
		);
	}

	renderKpMuhurtaPanel(fields){
		const jyotish = getJyotish(resolveJyotishChartObj(this.state, fields));
		const kp = jyotish ? jyotish.kp : null;
		const muhurta = jyotish ? jyotish.muhurta : null;
		const sublords = kp && kp.sublords ? kp.sublords : {};
		return (
			<div className="horosa-india-jyotish-panel">
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">KP Sublord</div>
					<div className="horosa-india-data-list">
						{Object.keys(sublords).map((key)=>(
							<div className="horosa-india-data-row" key={key}>
								<strong>{key}</strong>
								<span>{sublords[key].starLord ? sublords[key].starLord.label : '—'} / {sublords[key].subLord ? sublords[key].subLord.label : '—'}</span>
								<em>{sublords[key].nakshatra ? `${sublords[key].nakshatra.name} P${sublords[key].nakshatra.pada}` : '—'}</em>
							</div>
						))}
					</div>
				</div>
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">Muhurta</div>
					{muhurta && muhurta.available !== false ? (
						<>
							<div className="horosa-info-row"><span>日出</span><strong>{muhurta.sunrise || '—'}</strong></div>
							<div className="horosa-info-row"><span>日落</span><strong>{muhurta.sunset || '—'}</strong></div>
							<div className="horosa-info-row"><span>Rahu Kalam</span><strong>{muhurta.rahuKalam ? `${muhurta.rahuKalam.start} - ${muhurta.rahuKalam.end}` : '—'}</strong></div>
							<div className="horosa-info-row"><span>Yamaganda</span><strong>{muhurta.yamaganda ? `${muhurta.yamaganda.start} - ${muhurta.yamaganda.end}` : '—'}</strong></div>
							<div className="horosa-info-row"><span>Gulika</span><strong>{muhurta.gulika ? `${muhurta.gulika.start} - ${muhurta.gulika.end}` : '—'}</strong></div>
						</>
					) : (
						<div className="horosa-india-dasha-empty">暂无择时数据</div>
					)}
				</div>
			</div>
		);
	}

	renderQuickDock(indiaChartStyle){
		return (
			<div className="horosa-bottom-quick-dock horosa-india-quick-dock">
				<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
				<div className="horosa-bottom-quick-actions horosa-india-quick-actions">
					{INDIA_QUICK_ACTIONS.map((item)=>{
						const isActive = (item.action === 'tab' && this.state.currentTab === item.tab)
							|| (item.action === 'style' && indiaChartStyle === item.style)
							|| (item.action === 'infoTab' && this.state.jyotishTab === item.infoTab);
						return (
							<button
								type="button"
								key={item.key}
								className={`horosa-bottom-quick-button horosa-india-quick-button${isActive ? ' is-active' : ''}`}
								onClick={()=>this.handleQuickAction(item)}
							>
								<span className="horosa-bottom-quick-icon"><XQIcon name={item.icon} /></span>
								<span>{item.label}</span>
							</button>
						);
					})}
				</div>
			</div>
		);
	}

	renderDashaSubPopover(item, extraClassName = '', style = null){
		const subItems = buildDashaSubPeriods(item);
		return (
			<div className={`horosa-india-dasha-subpanel${extraClassName}`} style={style || undefined}>
				<div className="horosa-india-dasha-subtitle">
					<strong>{item.lord.label}</strong>
					<span>{item.lord.en} Antardasha</span>
				</div>
				<div className="horosa-india-dasha-sublist">
					{subItems.map((subItem, idx)=>(
						<div className="horosa-india-dasha-subitem" key={`${item.lord.key}_${subItem.lord.key}_${idx}`}>
							<div className="horosa-india-dasha-subname">
								<strong>{subItem.lord.label}</strong>
								<span>{subItem.lord.en}</span>
							</div>
							<div className="horosa-india-dasha-submeta">
								<span>{formatJyotishDate(subItem.start)} - {formatJyotishDate(subItem.end)}</span>
								<em>{formatDuration(subItem.years)}</em>
							</div>
						</div>
					))}
				</div>
			</div>
		);
	}

	renderDashaFloatingPopover(){
		if(!this.state.dashaPopoverItem || !this.state.dashaPopoverStyle || typeof document === 'undefined' || !document.body){
			return null;
		}
		return createPortal(
			this.renderDashaSubPopover(this.state.dashaPopoverItem, ' is-floating', this.state.dashaPopoverStyle),
			document.body
		);
	}

	renderDashaItem(item, idx){
		return (
			<div
				className="horosa-india-dasha-hover"
				key={`${item.lord.key}_${idx}`}
				onMouseEnter={(e)=>this.showDashaSubPopover(item, e)}
				onMouseLeave={this.hideDashaSubPopover}
				onFocus={(e)=>this.showDashaSubPopover(item, e)}
				onBlur={this.hideDashaSubPopover}
			>
				<button
					aria-label={`${item.lord.label} ${item.lord.en} 小运`}
					className={`horosa-india-dasha-item${item.active ? ' is-active' : ''}`}
					onClick={(e)=>this.showDashaSubPopover(item, e)}
					type="button"
				>
					<div className="horosa-india-dasha-item-main">
						<strong>{item.lord.label}</strong>
						<span>{item.lord.en}</span>
					</div>
					<div className="horosa-india-dasha-item-meta">
						<span>{formatJyotishDate(item.start)} - {formatJyotishDate(item.end)}</span>
						<em>{formatAge(item.startAge)} - {formatAge(item.endAge)} · {formatDuration(item.years)}</em>
					</div>
				</button>
			</div>
		);
	}

	render(){
		let fields = this.withIndiaOptionFields(this.props.fields);
		const indiaHsys = fields.indiaHsys
			? AstroConst.normalizeIndiaHouseSystem(fields.indiaHsys.value)
			: AstroConst.INDIA_HOUSE_SYSTEM_DEFAULT;
		const indiaAyanamsa = fields.indiaAyanamsa
			? AstroConst.normalizeIndiaAyanamsa(fields.indiaAyanamsa.value)
			: AstroConst.INDIA_AYANAMSA_DEFAULT;
		let jyotishFields = this.state.activeJyotishFields || fields;
		let chartHeight = '100%';
		let datetm = new DateTime();
		if(fields.date && fields.time){
			let str = fields.date.value.format('YYYY-MM-DD') + ' ' +
						fields.time.value.format('HH:mm:ss');
			datetm = datetm.parse(str, 'YYYY-MM-DD HH:mm:ss');
			if(fields.zone){
				datetm.setZone(fields.zone.value);
			}
		}
			const currentHook = this.state.hook[this.state.currentTab] || this.state.hook.Natal;
			const indiaChartStyle = AstroConst.normalizeIndiaChartStyle(this.props.indiaChartStyle);
			const degreeDisplayMode = this.state.degreeDisplayMode || INDIA_DEGREE_DISPLAY_DEGREE;
			let splitItems = [];
		for(let key in this.state.hook){
			let hook = this.state.hook[key];
			if(hook.fractal === 1 || hook.fractal === 5 ||
				hook.fractal === 6 || hook.fractal === 8 ||
				hook.fractal === 11 || hook.fractal === 30 || hook.fractal === 60){
				continue;
			}
			splitItems.push({
				key,
				...hook,
				});
			}
			const splitOptions = [
				{ value: 'Natal', label: '命盘 D1' },
				...splitItems.map((item)=>({
					value: item.key,
					label: `${item.fractal}分盘${item.txt ? ` · ${item.txt}` : ''}`,
				})),
			];

			return (
			<div className="horosa-india-chart-main horosa-astro-redesign horosa-india-redesign">
				<div className="horosa-astro-layout horosa-astro-redesign-layout horosa-india-redesign-layout">
					<div className="horosa-astro-redesign-grid horosa-india-redesign-grid">
						<div className="horosa-astro-context-panel horosa-astro-input-panel horosa-india-input-panel">
							<div className="horosa-india-input-stack">
								<div className="horosa-side-panel-heading">
									<div>
										<div className="horosa-side-panel-title">印占设置</div>
										<div className="horosa-side-panel-subtitle">时间、地点与分盘选项</div>
									</div>
								</div>
								<SpaceTimePanel
									fields={fields}
									value={datetm}
									onTimeChange={this.changeTime}
									timeHook={this.tmHook}
									onGeoChange={this.changeGeo}
								/>
								<div className="horosa-india-input-section">
									<div className="horosa-india-field-title">
										<XQIcon name="sliders" />
										<span>选项</span>
									</div>
										<div className="horosa-india-select-grid">
											<div className="horosa-india-select-field">
												<span>岁差制</span>
												<Select
													size="small"
													style={{width: '100%'}}
													value={indiaAyanamsa}
													onChange={this.changeIndiaAyanamsa}
												>
													{AstroConst.INDIA_AYANAMSA_OPTIONS.map((item)=>(
														<Option value={item.value} key={item.value}>{item.label}</Option>
													))}
												</Select>
											</div>
											<div className="horosa-india-select-field">
												<span>分宫制</span>
												<Select
													size="small"
													style={{width: '100%'}}
													value={indiaHsys}
													onChange={this.changeHsys}
												>
													{AstroConst.INDIA_HOUSE_SYSTEM_OPTIONS.map((item)=>(
														<Option value={item.value} key={item.value}>{item.label}</Option>
													))}
												</Select>
											</div>
												<div className="horosa-india-select-field">
													<span>当前分盘</span>
													<Select
													size="small"
													style={{width: '100%'}}
													value={this.state.currentTab}
													onChange={this.changeTab}
												>
													{splitOptions.map((item)=>(
														<Option value={item.value} key={item.value}>{item.label}</Option>
													))}
													</Select>
												</div>
												<div className="horosa-india-select-field">
													<span>完整度数</span>
													<Select
														size="small"
														style={{width: '100%'}}
														value={degreeDisplayMode}
														onChange={this.changeDegreeDisplayMode}
													>
														{INDIA_DEGREE_DISPLAY_OPTIONS.map((item)=>(
															<Option value={item.value} key={item.value}>{item.label}</Option>
														))}
													</Select>
												</div>
											</div>
									<div className="horosa-india-style-block">
										<div className="horosa-side-section-title">盘式</div>
										<Segmented
											value={indiaChartStyle}
											onChange={this.changeIndiaChartStyle}
											options={AstroConst.INDIA_CHART_STYLE_OPTIONS}
										/>
									</div>
								</div>
								{this.renderJyotishNav()}
							</div>
						</div>
						<div className="horosa-chart-stage horosa-chart-stage-redesign horosa-india-chart-panel">
								<IndiaChart
									key={`${this.state.currentTab}_${indiaChartStyle}_${indiaAyanamsa}_${indiaHsys}`}
									chartOnly
									ref={(node)=>{ this.mainIndiaChartRef = node; }}
									chartnum={currentHook.fractal}
							onChange={this.onFieldsChange}
								fields={fields}
								height={chartHeight}
									chartDisplay={this.props.chartDisplay}
										indiaChartStyle={indiaChartStyle}
										indiaAyanamsa={indiaAyanamsa}
										indiaHsys={indiaHsys}
										degreeDisplayMode={degreeDisplayMode}
										planetDisplay={this.props.planetDisplay}
								lotsDisplay={this.props.lotsDisplay}
								showPlanetHouseInfo={this.props.showPlanetHouseInfo}
								showAstroMeaning={this.props.showAstroMeaning}
								hook={currentHook}
								dispatch={this.props.dispatch}
								onChartLoad={this.handleMainChartLoad}
							/>
						</div>
						<div className="horosa-inspector-panel horosa-astro-content-panel horosa-india-info-panel">
							<Tabs activeKey={this.state.jyotishTab} onChange={this.changeJyotishTab} tabPosition="top" className="horosa-content-tabs horosa-india-tabs">
								<TabPane tab="分盘" key="1">
									<div className="horosa-india-split-list">
										<button
											type="button"
											className={`horosa-india-split-button${this.state.currentTab === 'Natal' ? ' is-active' : ''}`}
											onClick={()=>this.changeTab('Natal')}
										>
											<strong>D1</strong>
											<span>命盘</span>
										</button>
										{splitItems.map((item)=>(
											<button
												type="button"
												key={item.key}
												className={`horosa-india-split-button${this.state.currentTab === item.key ? ' is-active' : ''}`}
												onClick={()=>this.changeTab(item.key)}
											>
												<strong>D{item.fractal}</strong>
												<span>{item.txt || `${item.fractal}分盘`}</span>
											</button>
										))}
									</div>
								</TabPane>
								<TabPane tab="五支" key="2">
									{this.renderPanchangaPanel(jyotishFields)}
								</TabPane>
								<TabPane tab="大运" key="3">
									{this.renderDashaPanel(jyotishFields)}
								</TabPane>
								<TabPane tab="星曜" key="4">
									{this.renderPlanetStatePanel(jyotishFields)}
								</TabPane>
								<TabPane tab="八分" key="5">
									{this.renderAshtakavargaPanel(jyotishFields)}
								</TabPane>
								<TabPane tab="KP/择时" key="6">
									{this.renderKpMuhurtaPanel(jyotishFields)}
								</TabPane>
							</Tabs>
						</div>
					</div>
					{this.renderQuickDock(indiaChartStyle)}
				</div>
			</div>
		);
	}
}

export default IndiaChartMain;
