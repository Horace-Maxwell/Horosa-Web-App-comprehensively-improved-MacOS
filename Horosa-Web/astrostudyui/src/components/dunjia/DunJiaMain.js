import { Component } from 'react';
import { Row, Col, Card, Select, Button, Divider, Spin, Tag, Tabs, message, Popover } from 'antd';
import { saveModuleAISnapshot, loadModuleAISnapshot } from '../../utils/moduleAiSnapshot';
import {
	getNongliLocalCache,
	setNongliLocalCache,
} from '../../utils/localCalcCache';
import {
} from '../../utils/localNongliAdapter';
import {
	fetchPreciseNongli,
	fetchPreciseJieqiSeed,
} from '../../utils/preciseCalcBridge';
import sealedImage from '../../assets/sealed.png';
import GeoCoordModal from '../amap/GeoCoordModal';
import PlusMinusTime from '../astro/PlusMinusTime';
import DateTime from '../comp/DateTime';
import { convertLatToStr, convertLonToStr } from '../astro/AstroHelper';
import { getStore } from '../../utils/storageutil';
import {
	SEX_OPTIONS,
	PAIPAN_OPTIONS,
	ZHISHI_OPTIONS,
	YUEJIA_QIJU_OPTIONS,
	QIJU_METHOD_OPTIONS,
	KONG_MODE_OPTIONS,
	MA_MODE_OPTIONS,
	TIME_ALG_OPTIONS,
	YIXING_OPTIONS,
	DAY_SWITCH_OPTIONS,
	calcDunJia,
	buildDunJiaSnapshotText,
} from './DunJiaCalc';
import {
	BAGONG_PALACE_ORDER,
	BAGONG_PALACE_NAME,
	buildQimenBaGongPanelData,
	buildQimenFuShiYiGua,
} from './DunJiaBaGongRules';
import {
	buildQimenXiangTipObj,
	formatQimenDocLineToHtml,
} from './QimenXiangDoc';
import { BaZiColor, ZhiColor } from '../../msg/bazimsg';

const { Option } = Select;
const TabPane = Tabs.TabPane;
const FENGJU_OPTIONS = [
	{ value: 0, label: '未封局' },
	{ value: 1, label: '已封局' },
];
const DEFAULT_OPTIONS = {
	sex: 1,
	dateType: 0,
	leapMonthType: 0,
	xuShiSuiType: 0,
	jieQiType: 1,
	paiPanType: 3,
	zhiShiType: 0,
	yueJiaQiJuType: 1,
	yearGanZhiType: 2,
	monthGanZhiType: 1,
	dayGanZhiType: 0,
	qijuMethod: 'zhirun',
	kongMode: 'day',
	yimaMode: 'day',
	timeAlg: 0,
	shiftPalace: 0,
	after23NewDay: 1,
	fengJu: false,
};

const DUNJIA_BOARD_BASE_WIDTH = 662;
const DUNJIA_BOARD_BASE_HEIGHT = 870;
const DUNJIA_SCALE_MIN = 0.64;
const DUNJIA_SCALE_MAX = 1.22;
const QIMEN_PATTERN_INTERPRETATION_STORAGE_KEY = 'qimenShowPatternInterpretation';

function clamp(val, min, max){
	return Math.max(min, Math.min(max, val));
}

function getViewportHeight(){
	if(typeof window !== 'undefined' && Number.isFinite(window.innerHeight) && window.innerHeight > 0){
		return window.innerHeight;
	}
	if(typeof document !== 'undefined' && document.documentElement){
		return document.documentElement.clientHeight || 900;
	}
	return 900;
}

function safe(v, d = ''){
	return v === undefined || v === null ? d : v;
}

const GAN_COLOR_MAP = {
	甲: BaZiColor.PositiveWood,
	乙: BaZiColor.NegativeWood,
	丙: BaZiColor.PositiveFire,
	丁: BaZiColor.NegativeFire,
	戊: BaZiColor.PositiveEarth,
	己: BaZiColor.NegativeEarth,
	庚: BaZiColor.PositiveMetal,
	辛: BaZiColor.NegativeMetal,
	壬: BaZiColor.PositiveWater,
	癸: BaZiColor.NegativeWater,
};

function getBaZiStemColor(stem){
	return GAN_COLOR_MAP[safe(stem, '')] || '#333333';
}

function getBaZiBranchColor(branch){
	return ZhiColor[safe(branch, '')] || '#333333';
}

function normalizeTimeAlg(value){
	return value === 1 ? 1 : 0;
}

function getTimeAlgLabel(value){
	return normalizeTimeAlg(value) === 1 ? '直接时间' : '真太阳时';
}

function parseZoneOffsetHour(zone){
	if(zone === undefined || zone === null || zone === ''){
		return null;
	}
	const raw = `${zone}`.trim();
	if(!raw){
		return null;
	}
	const numeric = Number(raw);
	if(Number.isFinite(numeric)){
		return numeric;
	}
	const m = raw.match(/^([+-])(\d{1,2})(?::?(\d{2}))?$/);
	if(!m){
		return null;
	}
	const sign = m[1] === '-' ? -1 : 1;
	const hh = parseInt(m[2], 10);
	const mm = parseInt(m[3] || '0', 10);
	if(Number.isNaN(hh) || Number.isNaN(mm)){
		return null;
	}
	return sign * (hh + mm / 60);
}

function resolveCalcGeo(fields, options){
	const lon = safe(fields && fields.lon && fields.lon.value, '');
	const lat = safe(fields && fields.lat && fields.lat.value, '');
	const gpsLon = safe(fields && fields.gpsLon && fields.gpsLon.value, '');
	const gpsLat = safe(fields && fields.gpsLat && fields.gpsLat.value, '');
	// timeAlg 仅用于“计算基准”切换，不应改写显示真太阳时所依赖的地理位置。
	return { lon, lat, gpsLon, gpsLat };
}

function buildDisplaySolarParams(params){
	if(!params){
		return null;
	}
	return {
		...params,
		timeAlg: 0,
	};
}

function loadPatternInterpretationPreference(){
	try{
		if(typeof window === 'undefined' || !window.localStorage){
			return true;
		}
		const val = window.localStorage.getItem(QIMEN_PATTERN_INTERPRETATION_STORAGE_KEY);
		if(val === null || val === undefined || val === ''){
			return true;
		}
		return val !== '0' && val !== 'false';
	}catch(e){
		return true;
	}
}

function savePatternInterpretationPreference(value){
	try{
		if(typeof window !== 'undefined' && window.localStorage){
			window.localStorage.setItem(QIMEN_PATTERN_INTERPRETATION_STORAGE_KEY, value ? '1' : '0');
		}
	}catch(e){
	}
}

function saveQimenLiveSnapshot(pan){
	if(!pan || typeof window === 'undefined'){
		return '';
	}
	let snapshotText = '';
	try{
		snapshotText = buildDunJiaSnapshotText(pan);
	}catch(e){
		snapshotText = '';
	}
	if(snapshotText){
		window.__horosa_qimen_snapshot_text = snapshotText;
		window.__horosa_qimen_snapshot_at = Date.now();
	}
	return snapshotText;
}

function parseDisplayDateHm(rawText){
	const text = `${safe(rawText, '')}`.trim();
	if(!text){
		return null;
	}
	const normalized = text.replace('T', ' ').replace('Z', ' ').trim();
	const dateMatch = normalized.match(/([-+]?\d{1,6})[/-](\d{1,2})[/-](\d{1,2})/);
	const timeMatch = normalized.match(/(\d{1,2}):(\d{2})/);
	if(!dateMatch && !timeMatch){
		return null;
	}
	const yyyy = dateMatch ? `${dateMatch[1]}` : '';
	const mm = dateMatch ? `${dateMatch[2]}`.padStart(2, '0') : '';
	const dd = dateMatch ? `${dateMatch[3]}`.padStart(2, '0') : '';
	const hh = timeMatch ? `${timeMatch[1]}`.padStart(2, '0') : '';
	return {
		date: yyyy ? `${yyyy}年${mm}月${dd}日` : '',
		hm: timeMatch ? `${hh}:${timeMatch[2]}` : '',
	};
}

function getBoardTimeInfo(pan){
	const solar = parseDisplayDateHm(pan && pan.realSunTime);
	const direct = parseDisplayDateHm(`${safe(pan && pan.dateStr, '')} ${safe(pan && pan.timeStr, '')}`);
	const clockDate = safe(direct && direct.date, '');
	const clockHm = safe(direct && direct.hm, '') || (safe(pan && pan.timeStr, '').length >= 5 ? safe(pan && pan.timeStr, '').substr(0, 5) : '--:--');
	if(solar && (solar.date || solar.hm)){
		return {
			dateText: solar.date || clockDate || '日期--',
			clockHm,
			solarHm: solar.hm || '--:--',
		};
	}
	if(clockDate || clockHm){
		return {
			dateText: clockDate || '日期--',
			clockHm,
			solarHm: clockHm,
		};
	}
	return {
		dateText: '时间--',
		clockHm: '--:--',
		solarHm: '--:--',
	};
}

function getFieldKey(fields){
	if(!fields || !fields.date || !fields.time){
		return '';
	}
	return [
		fields.date.value.format('YYYY-MM-DD'),
		fields.time.value.format('HH:mm:ss'),
		safe(fields.zone && fields.zone.value),
		safe(fields.lon && fields.lon.value),
		safe(fields.lat && fields.lat.value),
		safe(fields.ad && fields.ad.value),
		safe(fields.gender && fields.gender.value),
	].join('|');
}

function getAfter23NewDayValue(options){
	return options && options.after23NewDay === 0 ? 0 : 1;
}

function getTimeAlgValue(options){
	return normalizeTimeAlg(options && options.timeAlg);
}

function getNongliRequestKey(fields, options){
	return `${getFieldKey(fields)}|after23NewDay=${getAfter23NewDayValue(options)}|timeAlg=${getTimeAlgValue(options)}`;
}

function getNongliKey(nongli){
	if(!nongli){
		return '';
	}
	return [
		safe(nongli.yearGanZi),
		safe(nongli.monthGanZi),
		safe(nongli.dayGanZi),
		safe(nongli.time),
		safe(nongli.jieqi),
		safe(nongli.runyear),
	].join('|');
}

function getQimenOptionsKey(options){
	if(!options){
		return '';
	}
	return [
		safe(options.sex),
		safe(options.dateType),
		safe(options.leapMonthType),
		safe(options.xuShiSuiType),
		safe(options.jieQiType),
		safe(options.paiPanType),
		safe(options.zhiShiType),
		safe(options.yueJiaQiJuType),
		safe(options.yearGanZhiType),
		safe(options.monthGanZhiType),
		safe(options.dayGanZhiType),
		safe(options.qijuMethod),
		safe(options.kongMode),
		safe(options.yimaMode),
		safe(options.shiftPalace),
		getAfter23NewDayValue(options),
		getTimeAlgValue(options),
		options.fengJu ? 1 : 0,
	].join('|');
}

function needJieqiYearSeed(options){
	const opt = options || {};
	return opt.paiPanType === 3 && opt.qijuMethod === 'zhirun';
}

function extractIsDiurnalFromChartProp(val){
	if(!val){
		return null;
	}
	const chart = val.chart ? val.chart : val;
	if(chart && chart.isDiurnal !== undefined && chart.isDiurnal !== null){
		return !!chart.isDiurnal;
	}
	return null;
}

class DunJiaMain extends Component {
	constructor(props){
		super(props);

		this.state = {
			loading: false,
			nongli: null,
			displaySolarTime: '',
			pan: null,
			localFields: null,
			hasPlotted: false,
			rightPanelTab: 'overview',
			bagongPalace: BAGONG_PALACE_ORDER[0],
			showPatternInterpretation: loadPatternInterpretationPreference(),
			leftBoardWidth: 0,
			viewportHeight: getViewportHeight(),
			options: {
				...DEFAULT_OPTIONS,
			},
		};

		this.unmounted = false;
		this.jieqiSeedPromises = {};
		this.jieqiYearSeeds = {};
		this.lastRestoredCaseId = null;
		this.timeHook = {};
		this.lastNongliKey = '';
		this.lastPanSignature = '';
		this.pendingNongli = null;
		this.requestSeq = 0;
		this.panCache = new Map();
		this.resizeObserver = null;
		this.prefetchSeedTimer = null;
		this.onOptionChange = this.onOptionChange.bind(this);
		this.onFieldsChange = this.onFieldsChange.bind(this);
		this.onTimeChanged = this.onTimeChanged.bind(this);
		this.onGenderChange = this.onGenderChange.bind(this);
		this.changeGeo = this.changeGeo.bind(this);
		this.genJieqiParams = this.genJieqiParams.bind(this);
		this.ensureJieqiSeed = this.ensureJieqiSeed.bind(this);
		this.prefetchJieqiSeedForFields = this.prefetchJieqiSeedForFields.bind(this);
		this.prefetchNongliForFields = this.prefetchNongliForFields.bind(this);
		this.resolveDisplaySolarTime = this.resolveDisplaySolarTime.bind(this);
		this.getContext = this.getContext.bind(this);
		this.requestNongli = this.requestNongli.bind(this);
		this.genParams = this.genParams.bind(this);
		this.recalc = this.recalc.bind(this);
		this.clickSaveCase = this.clickSaveCase.bind(this);
		this.clickPlot = this.clickPlot.bind(this);
		this.getTimeFieldsFromSelector = this.getTimeFieldsFromSelector.bind(this);
		this.restoreOptionsFromCurrentCase = this.restoreOptionsFromCurrentCase.bind(this);
		this.parseCasePayload = this.parseCasePayload.bind(this);
		this.captureLeftBoardHost = this.captureLeftBoardHost.bind(this);
		this.handleWindowResize = this.handleWindowResize.bind(this);
		this.handleSnapshotRefreshRequest = this.handleSnapshotRefreshRequest.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (fields)=>{
				if(this.unmounted){
					return;
				}
				this.restoreOptionsFromCurrentCase();
				if(fields){
					this.setState({
						localFields: fields,
					});
					this.prefetchJieqiSeedForFields(fields);
					this.prefetchNongliForFields(fields);
				}
			};
		}
	}

	getCachedPan(fields, nongli, options, displaySolarTime){
		const ctx = this.getContext(fields, displaySolarTime);
		const key = [
			getFieldKey(fields),
			getNongliKey(nongli),
			getQimenOptionsKey(options),
			safe(ctx && ctx.isDiurnal, ''),
			safe(ctx && ctx.displaySolarTime, ''),
		].join('|');
		if(this.panCache.has(key)){
			return this.panCache.get(key);
		}
		const pan = calcDunJia(fields, nongli, options, ctx);
		this.panCache.set(key, pan);
		if(this.panCache.size > 64){
			const firstKey = this.panCache.keys().next().value;
			if(firstKey){
				this.panCache.delete(firstKey);
			}
		}
		return pan;
	}

	componentDidMount(){
		this.unmounted = false;
		if(typeof window !== 'undefined'){
			window.addEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
		this.restoreOptionsFromCurrentCase(true);
		window.addEventListener('resize', this.handleWindowResize);
		this.handleWindowResize();
		this.prefetchJieqiSeedForFields(this.state.localFields || this.props.fields);
		this.prefetchNongliForFields(this.state.localFields || this.props.fields);
	}

	componentDidUpdate(){
		this.restoreOptionsFromCurrentCase();
	}

	componentWillUnmount(){
		this.unmounted = true;
		if(typeof window !== 'undefined'){
			window.removeEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
		window.removeEventListener('resize', this.handleWindowResize);
		if(this.prefetchSeedTimer){
			clearTimeout(this.prefetchSeedTimer);
			this.prefetchSeedTimer = null;
		}
		if(this.resizeObserver){
			this.resizeObserver.disconnect();
			this.resizeObserver = null;
		}
	}

	handleSnapshotRefreshRequest(evt){
		const moduleName = evt && evt.detail ? evt.detail.module : '';
		if(moduleName !== 'qimen'){
			return;
		}
		if(this.state.pan){
			const snapshotText = saveQimenLiveSnapshot(this.state.pan);
			if(snapshotText){
				saveModuleAISnapshot('qimen', snapshotText);
				if(evt && evt.detail && typeof evt.detail === 'object'){
					evt.detail.snapshotText = snapshotText;
				}
			}
		}
	}

	captureLeftBoardHost(node){
		if(this.resizeObserver){
			this.resizeObserver.disconnect();
			this.resizeObserver = null;
		}
		this.leftBoardHost = node || null;
		if(this.leftBoardHost && typeof ResizeObserver !== 'undefined'){
			this.resizeObserver = new ResizeObserver(()=>{
				this.handleWindowResize();
			});
			this.resizeObserver.observe(this.leftBoardHost);
		}
		this.handleWindowResize();
	}

	handleWindowResize(){
		const viewportHeight = getViewportHeight();
		const leftBoardWidth = this.leftBoardHost ? this.leftBoardHost.clientWidth : 0;
		const changed = Math.abs((this.state.leftBoardWidth || 0) - leftBoardWidth) >= 2
			|| Math.abs((this.state.viewportHeight || 0) - viewportHeight) >= 2;
		if(changed){
			this.setState({
				leftBoardWidth,
				viewportHeight,
			});
		}
	}

	calcBoardScale(){
		const viewH = this.state.viewportHeight || 900;
		const availW = this.state.leftBoardWidth > 0 ? (this.state.leftBoardWidth - 22) : DUNJIA_BOARD_BASE_WIDTH;
		const widthScale = availW / DUNJIA_BOARD_BASE_WIDTH;
		// 高度优先：先按可视高度给出主缩放，再用宽度做上限约束。
		let rawScale = (viewH - 230) / DUNJIA_BOARD_BASE_HEIGHT;
		if(Number.isFinite(widthScale) && widthScale > 0){
			rawScale = Math.min(rawScale, widthScale);
		}
		if(!Number.isFinite(rawScale) || rawScale <= 0){
			return 1;
		}
		return clamp(rawScale, DUNJIA_SCALE_MIN, DUNJIA_SCALE_MAX);
	}

	parseCasePayload(raw){
		if(!raw){
			return null;
		}
		if(typeof raw === 'string'){
			try{
				return JSON.parse(raw);
			}catch(e){
				return null;
			}
		}
		if(typeof raw === 'object'){
			return raw;
		}
		return null;
	}

	restoreOptionsFromCurrentCase(force){
		const store = getStore();
		const userState = store && store.user ? store.user : null;
		const currentCase = userState && userState.currentCase ? userState.currentCase : null;
		if(!currentCase || !currentCase.cid || !currentCase.cid.value){
			return;
		}
		const cid = `${currentCase.cid.value}`;
		const updateTime = currentCase.updateTime && currentCase.updateTime.value ? `${currentCase.updateTime.value}` : '';
		const caseVersion = `${cid}|${updateTime}`;
		if(!force && this.lastRestoredCaseId === caseVersion){
			return;
		}
		const sourceModule = currentCase.sourceModule ? currentCase.sourceModule.value : null;
		const caseType = currentCase.caseType ? currentCase.caseType.value : null;
		if(sourceModule !== 'qimen' && caseType !== 'qimen'){
			return;
		}
		const payload = this.parseCasePayload(currentCase.payload ? currentCase.payload.value : null);
		if(!payload){
			return;
		}
		const nextOptions = {
			...this.state.options,
		};
		let changed = false;
		const savedOptions = payload.options && typeof payload.options === 'object' ? payload.options : null;
		if(savedOptions){
			Object.keys(DEFAULT_OPTIONS).forEach((key)=>{
				if(savedOptions[key] !== undefined){
					nextOptions[key] = savedOptions[key];
					changed = true;
				}
			});
		}
		const pan = payload.pan && typeof payload.pan === 'object' ? payload.pan : null;
		if(pan){
			if(pan.shiftPalace !== undefined){
				nextOptions.shiftPalace = pan.shiftPalace;
				changed = true;
			}
			if(pan.fengJu !== undefined){
				nextOptions.fengJu = !!pan.fengJu;
				changed = true;
			}
		}
		this.lastRestoredCaseId = caseVersion;
		if(!changed){
			return;
		}
		this.setState({
			options: nextOptions,
		}, ()=>{
			const calcFields = this.state.localFields || this.props.fields;
			const calcFieldKey = getFieldKey(calcFields);
			const nongliKey = getNongliRequestKey(calcFields, nextOptions);
			const canRecalc = this.state.nongli
				&& calcFieldKey
				&& nongliKey
				&& nongliKey === this.lastNongliKey;
			if(this.state.hasPlotted){
				if(canRecalc){
					this.recalc(this.state.localFields || this.props.fields, this.state.nongli, nextOptions, this.state.displaySolarTime);
				}else{
					this.requestNongli(calcFields, true);
				}
			}
		});
	}

	onFieldsChange(field, syncOnly){
		if(this.props.dispatch){
			const flds = {
				...(this.props.fields || {}),
				...field,
			};
			if(syncOnly){
				this.props.dispatch({
					type: 'astro/save',
					payload: {
						fields: flds,
					},
				});
				return;
			}
			this.props.dispatch({
				type: 'astro/fetchByFields',
				payload: flds,
			});
		}
	}

	onTimeChanged(value){
		const dt = value.time;
		const base = this.props.fields || {};
		const localFields = {
			...base,
			date: { value: dt.clone() },
			time: { value: dt.clone() },
			ad: { value: dt.ad },
			zone: { value: dt.zone },
		};
		this.setState({ localFields });
		if(this.prefetchSeedTimer){
			clearTimeout(this.prefetchSeedTimer);
		}
		this.prefetchSeedTimer = setTimeout(()=>{
			this.prefetchSeedTimer = null;
			if(this.unmounted){
				return;
			}
			this.prefetchJieqiSeedForFields(localFields);
			this.prefetchNongliForFields(localFields);
		}, 120);
	}

	onGenderChange(val){
		this.onOptionChange('sex', val);
		this.onFieldsChange({
			gender: { value: val },
		}, true);
	}

	getTimeFieldsFromSelector(baseFields){
		if(!this.timeHook || typeof this.timeHook.getValue !== 'function'){
			return null;
		}
		const draft = this.timeHook.getValue();
		if(!draft || !draft.value || !(draft.value instanceof DateTime)){
			return null;
		}
		const dt = draft.value;
		return {
			...(baseFields || this.state.localFields || this.props.fields || {}),
			date: { value: dt.clone() },
			time: { value: dt.clone() },
			ad: { value: dt.ad },
			zone: { value: dt.zone },
		};
	}

	clickPlot(){
		if(this.state.loading){
			return;
		}
		const timeFields = this.getTimeFieldsFromSelector(this.state.localFields || this.props.fields);
		const nextFields = timeFields || this.state.localFields || this.props.fields;
		if(!nextFields){
			return;
		}
		const nextKey = getFieldKey(nextFields);
		const curKey = getFieldKey(this.props.fields);
		if(nextKey && nextKey !== curKey){
			this.onFieldsChange({
				date: { value: nextFields.date.value.clone() },
				time: { value: nextFields.time.value.clone() },
				ad: { value: nextFields.ad.value },
				zone: { value: nextFields.zone.value },
			}, true);
		}
		this.setState({
			hasPlotted: true,
			localFields: nextFields,
		}, ()=>{
			const shouldForce = !this.state.nongli
				|| getNongliRequestKey(nextFields, this.state.options) !== this.lastNongliKey;
			this.requestNongli(nextFields, shouldForce);
		});
	}

	changeGeo(rec){
		this.onFieldsChange({
			lon: { value: convertLonToStr(rec.lng) },
			lat: { value: convertLatToStr(rec.lat) },
			gpsLon: { value: rec.gpsLng },
			gpsLat: { value: rec.gpsLat },
		}, true);
	}

	genParams(fields){
		const flds = fields || this.state.localFields || this.props.fields;
		if(!flds){
			return null;
		}
		const options = this.state.options || DEFAULT_OPTIONS;
		const genderValue = (flds.gender && flds.gender.value !== undefined && flds.gender.value !== null)
			? flds.gender.value
			: options.sex;
		const zoneValue = flds.zone && flds.zone.value !== undefined && flds.zone.value !== null
			? flds.zone.value
			: 8;
		const adValue = flds.ad && flds.ad.value !== undefined && flds.ad.value !== null
			? flds.ad.value
			: 1;
		const calcGeo = resolveCalcGeo(flds, options);
		return {
			date: flds.date.value.format('YYYY-MM-DD'),
			time: flds.time.value.format('HH:mm:ss'),
			zone: zoneValue,
			lon: calcGeo.lon,
			lat: calcGeo.lat,
			gpsLat: calcGeo.gpsLat,
			gpsLon: calcGeo.gpsLon,
			ad: adValue,
			gender: genderValue,
			timeAlg: normalizeTimeAlg(options.timeAlg),
			after23NewDay: getAfter23NewDayValue(options),
		};
	}

	recalc(fields, nongli, options, displaySolarTime){
		const flds = fields || this.state.localFields || this.props.fields;
		if(!flds || !nongli){
			return;
		}
		const displaySolar = safe(displaySolarTime, this.state.displaySolarTime);
		const fixedOptions = {
			...(options || this.state.options),
			jieQiType: 1,
			yearGanZhiType: 2,
			monthGanZhiType: 1,
			dayGanZhiType: 1,
		};
			const panSignature = [
				getFieldKey(flds),
				getNongliKey(nongli || this.state.nongli),
				getQimenOptionsKey(fixedOptions),
				safe(this.getContext(flds, displaySolar).isDiurnal, ''),
				displaySolar,
			].join('|');
		if(this.state.pan && panSignature === this.lastPanSignature){
			return;
		}
		const pan = this.getCachedPan(flds, nongli || this.state.nongli, fixedOptions, displaySolar);
		this.lastPanSignature = panSignature;
		this.setState({ pan, displaySolarTime: displaySolar }, ()=>{
			if(pan){
				const snapshotText = saveQimenLiveSnapshot(pan);
				if(snapshotText){
					saveModuleAISnapshot('qimen', snapshotText);
				}
			}
		});
	}

	genJieqiParams(fields, year){
		const flds = fields || this.state.localFields || this.props.fields;
		if(!flds){
			return null;
		}
		const options = this.state.options || DEFAULT_OPTIONS;
		const calcGeo = resolveCalcGeo(flds, options);
		return {
			year: `${year}`,
			ad: flds.ad ? flds.ad.value : 1,
			zone: flds.zone.value,
			lon: calcGeo.lon,
			lat: calcGeo.lat,
			gpsLat: calcGeo.gpsLat,
			gpsLon: calcGeo.gpsLon,
			timeAlg: normalizeTimeAlg(options.timeAlg),
			hsys: 0,
			zodiacal: 0,
			doubingSu28: false,
		};
	}

	async resolveDisplaySolarTime(params, primaryResult){
		if(!params){
			return safe(primaryResult && primaryResult.birth, '');
		}
		const current = safe(primaryResult && primaryResult.birth, '');
		if(normalizeTimeAlg(params.timeAlg) === 0){
			return current;
		}
		const solarParams = buildDisplaySolarParams(params);
		const cachedSolar = getNongliLocalCache(solarParams);
		if(cachedSolar && cachedSolar.birth){
			return safe(cachedSolar.birth, current);
		}
		try{
			const solarResult = await fetchPreciseNongli(solarParams);
			if(solarResult){
				setNongliLocalCache(solarParams, solarResult);
			}
			return safe(solarResult && solarResult.birth, current);
		}catch(e){
			// 显示用真太阳时请求失败时，回退主请求时间，不中断排盘。
			return current;
		}
	}

	getContext(fields, displaySolarTime){
		const flds = fields || this.state.localFields || this.props.fields;
		let year = null;
		if(flds && flds.date && flds.date.value){
			year = parseInt(flds.date.value.format('YYYY'), 10);
		}
		return {
			year,
			jieqiYearSeeds: this.jieqiYearSeeds,
			isDiurnal: extractIsDiurnalFromChartProp(this.props.value),
			displaySolarTime: safe(displaySolarTime, this.state.displaySolarTime),
		};
	}

	async ensureJieqiSeed(fields, year){
		if(!year || Number.isNaN(year)){
			return null;
		}
		if(this.jieqiYearSeeds[year]){
			return this.jieqiYearSeeds[year];
		}
		if(this.jieqiSeedPromises[year]){
			return this.jieqiSeedPromises[year];
		}
		const params = this.genJieqiParams(fields, year);
		if(!params){
			return null;
		}
		this.jieqiSeedPromises[year] = Promise.resolve().then(async()=>{
			let seed = await fetchPreciseJieqiSeed(params);
			if(seed){
				this.jieqiYearSeeds[year] = seed;
			}
			return seed;
		}).finally(()=>{
			delete this.jieqiSeedPromises[year];
		});
		return this.jieqiSeedPromises[year];
	}

	prefetchJieqiSeedForFields(fields){
		const flds = fields || this.state.localFields || this.props.fields;
		if(!flds || !flds.date || !flds.date.value){
			return;
		}
		const fixedOptions = {
			...this.state.options,
			jieQiType: 1,
			yearGanZhiType: 2,
			monthGanZhiType: 1,
			dayGanZhiType: 1,
		};
		if(!needJieqiYearSeed(fixedOptions)){
			return;
		}
		const year = parseInt(flds.date.value.format('YYYY'), 10);
		if(!year || Number.isNaN(year)){
			return;
		}
		Promise.all([
			this.ensureJieqiSeed(flds, year - 1),
			this.ensureJieqiSeed(flds, year),
		]).catch(()=>null);
	}

	prefetchNongliForFields(fields){
		const flds = fields || this.state.localFields || this.props.fields;
		if(!flds){
			return;
		}
		let params = null;
		try{
			params = this.genParams(flds);
		}catch(e){
			return;
		}
		if(!params){
			return;
		}
		fetchPreciseNongli(params).then((result)=>{
			if(result){
				setNongliLocalCache(params, result);
			}
		}).catch(()=>null);
	}

	async requestNongli(fields, force){
		const fldsToUse = fields || this.state.localFields || this.props.fields;
		let params = null;
		try{
			params = this.genParams(fldsToUse);
		}catch(e){
			message.error('遁甲起盘参数无效，请确认时间与经纬度后重试');
			return;
		}
		if(!params){
			return;
		}
		const requestKey = getNongliRequestKey(fldsToUse, this.state.options);
		if(!force && this.state.nongli && requestKey && requestKey === this.lastNongliKey){
			this.recalc(fldsToUse, this.state.nongli, this.state.options, this.state.displaySolarTime);
			return;
		}
		if(this.pendingNongli && this.pendingNongli.key === requestKey){
			return this.pendingNongli.promise;
		}
		const seq = ++this.requestSeq;
		if(force && !this.state.loading){
			this.setState({ loading: true });
		}

		const reqPromise = (async ()=>{
			const fixedOptions = {
				...this.state.options,
				jieQiType: 1,
				yearGanZhiType: 2,
				monthGanZhiType: 1,
				dayGanZhiType: 1,
			};
			const shouldWaitSeed = needJieqiYearSeed(fixedOptions);
			const flds = fldsToUse;
			let year = null;
			if(flds && flds.date && flds.date.value){
				year = parseInt(flds.date.value.format('YYYY'), 10);
			}
			const waitSeed = !!(year && shouldWaitSeed);
			const seedPromise = waitSeed ? Promise.all([
				this.ensureJieqiSeed(flds, year - 1),
				this.ensureJieqiSeed(flds, year),
			]) : null;
			const missingSeed = waitSeed && (!this.jieqiYearSeeds[year - 1] || !this.jieqiYearSeeds[year]);
			if(missingSeed && !this.state.loading){
				this.setState({ loading: true });
			}
				try{
					const result = await fetchPreciseNongli(params);
					if(!result){
						throw new Error('precise.nongli.unavailable');
					}
					setNongliLocalCache(params, result);
					const displaySolarTime = await this.resolveDisplaySolarTime(params, result);
					if(this.unmounted || seq !== this.requestSeq){
						return;
					}
				if(waitSeed){
					const seeds = await seedPromise;
					if(!seeds[0] || !seeds[1]){
						throw new Error('precise.jieqi.unavailable');
					}
				}
				if(this.unmounted || seq !== this.requestSeq){
					return;
				}
					const panSignature = [
						getFieldKey(flds),
						getNongliKey(result),
						getQimenOptionsKey(fixedOptions),
						safe(this.getContext(flds, displaySolarTime).isDiurnal, ''),
						displaySolarTime,
					].join('|');
					const pan = this.getCachedPan(flds, result, fixedOptions, displaySolarTime);
					this.lastNongliKey = requestKey;
					this.lastPanSignature = panSignature;
						this.setState({
							nongli: result,
							displaySolarTime,
							pan,
							loading: false,
						}, ()=>{
						if(pan){
							const snapshotText = saveQimenLiveSnapshot(pan);
							if(snapshotText){
								saveModuleAISnapshot('qimen', snapshotText);
							}
						}
					});
			}catch(e){
				if(!this.unmounted && seq === this.requestSeq){
					this.setState({ loading: false });
					message.error('遁甲计算失败：精确历法服务不可用');
				}
			}finally{
				if(this.pendingNongli && this.pendingNongli.key === requestKey && seq === this.requestSeq){
					this.pendingNongli = null;
				}
			}
		})();
		this.pendingNongli = {
			key: requestKey,
			promise: reqPromise,
		};
		return reqPromise;
	}

	onOptionChange(key, value){
		const nextVal = key === 'timeAlg' ? normalizeTimeAlg(value) : value;
		const options = {
			...this.state.options,
			[key]: nextVal,
		};
		const nextState = { options };
		if(key === 'timeAlg'){
			nextState.localFields = {
				...(this.state.localFields || this.props.fields || {}),
				timeAlg: { value: nextVal },
			};
		}
		this.setState(nextState, ()=>{
			if(key === 'timeAlg'){
				this.jieqiSeedPromises = {};
				this.jieqiYearSeeds = {};
				this.panCache.clear();
				this.lastPanSignature = '';
				this.lastNongliKey = '';
				this.onFieldsChange({
					timeAlg: { value: nextVal },
				}, true);
			}
			const calcFields = this.state.localFields || this.props.fields;
			const calcFieldKey = getFieldKey(calcFields);
			this.prefetchJieqiSeedForFields(calcFields);
			const canRecalc = this.state.nongli
				&& calcFieldKey
				&& getNongliRequestKey(calcFields, options) === this.lastNongliKey;
			if(key === 'after23NewDay' || key === 'timeAlg'){
				this.prefetchNongliForFields(calcFields);
				if(this.state.hasPlotted){
					this.requestNongli(calcFields, true);
				}
				return;
			}
			if(this.state.hasPlotted && canRecalc){
				this.recalc(this.state.localFields || this.props.fields, this.state.nongli, options, this.state.displaySolarTime);
			}
		});
	}

	clickSaveCase(){
		const pan = this.state.pan;
		if(!pan){
			message.warning('请先起盘后再保存');
			return;
		}
		const flds = this.state.localFields || this.props.fields;
		if(!flds){
			return;
		}
		const divTime = `${flds.date.value.format('YYYY-MM-DD')} ${flds.time.value.format('HH:mm:ss')}`;
		const snapshot = loadModuleAISnapshot('qimen');
		const payload = {
			module: 'qimen',
			snapshot: snapshot,
			pan: pan,
			options: {
				...this.state.options,
				fengJu: !!this.state.options.fengJu,
			},
		};
		if(this.props.dispatch){
			this.props.dispatch({
				type: 'astro/openDrawer',
				payload: {
					key: 'caseadd',
					record: {
						event: `奇门占断 ${divTime}`,
						caseType: 'qimen',
						divTime: divTime,
						zone: flds.zone.value,
						lat: flds.lat.value,
						lon: flds.lon.value,
						gpsLat: flds.gpsLat.value,
						gpsLon: flds.gpsLon.value,
						pos: flds.pos ? flds.pos.value : '',
						payload: payload,
						sourceModule: 'qimen',
					},
				},
			});
		}
	}

	renderQimenDocPopover(tipObj){
		if(!tipObj){
			return null;
		}
		const blocks = Array.isArray(tipObj.blocks) ? tipObj.blocks : [];
		return (
			<div style={{ maxWidth: 560, maxHeight: 460, overflowY: 'auto', paddingRight: 4 }}>
				<div style={{ fontSize: 17, lineHeight: '24px', fontWeight: 700, color: '#1f1f1f' }}>
					{tipObj.title}
				</div>
				<div style={{ borderTop: '1px solid #d9d9d9', margin: '6px 0 8px' }} />
				{blocks.map((block, idx)=>{
					if(!block){
						return null;
					}
					if(block.type === 'blank'){
						return <div key={`qimen_doc_blank_${idx}`} style={{ height: 6 }} />;
					}
					if(block.type === 'divider'){
						return <div key={`qimen_doc_divider_${idx}`} style={{ borderTop: '1px solid #e8e8e8', margin: '6px 0' }} />;
					}
					if(block.type === 'subTitle'){
						return (
							<div key={`qimen_doc_subtitle_${idx}`} style={{ margin: '4px 0 6px' }}>
								<div style={{ fontSize: 14, lineHeight: '20px', fontWeight: 700, color: '#262626' }}>{block.text}</div>
								<div style={{ borderTop: '1px solid #efefef', marginTop: 4 }} />
							</div>
						);
					}
					const html = formatQimenDocLineToHtml(block.text || '');
					return (
						<div
							key={`qimen_doc_text_${idx}`}
							style={{ fontSize: 13, lineHeight: '21px', color: '#262626', whiteSpace: 'pre-wrap' }}
							dangerouslySetInnerHTML={{ __html: html }}
						/>
					);
				})}
			</div>
		);
	}

	renderQimenHoverNode(type, text, style, key){
		const raw = `${text || ''}`.trim();
		const tipObj = buildQimenXiangTipObj(type, raw);
		const node = (
			<div key={key} style={{ ...style, cursor: tipObj ? 'help' : 'default' }}>
				{text || ' '}
			</div>
		);
		if(!tipObj){
			return node;
		}
		return (
			<Popover
				key={`${key}_popover`}
				trigger="hover"
				placement="bottomLeft"
				content={this.renderQimenDocPopover(tipObj)}
				overlayStyle={{ maxWidth: 600 }}
			>
				{node}
			</Popover>
		);
	}

	renderCell(cell){
		const titleColor = cell.hasKongWang ? '#2f54eb' : (cell.isCenter ? '#c7c7c7' : '#5f5f5f');
		let tianGanColor = '#262626';
		if(cell.hasJiXing && cell.hasRuMu){
			tianGanColor = '#722ed1';
		}else if(cell.hasJiXing){
			tianGanColor = '#cf1322';
		}else if(cell.hasRuMu){
			tianGanColor = '#8b5e3c';
		}
		// 八神不跟随值符或天盘干状态染色，保持独立显示。
		const godColor = '#262626';
		const line2Color = cell.hasMenPo ? '#fa8c16' : '#262626';
		const line3Color = '#262626';
		const diGanColor = '#262626';
		const centerMinorColor = '#8c8c8c';
		const unifiedFont = 34;
		const insetX = 52;
		const insetY = 40;
		const isGenPalace = cell.palaceNum === 7 || cell.palaceName === '艮';
		const yiMaStyle = isGenPalace
			? { position: 'absolute', left: 10, bottom: 8, fontSize: 20, lineHeight: '20px', color: '#111' }
			: { position: 'absolute', top: 8, right: 10, fontSize: 20, lineHeight: '20px', color: '#111' };

		const palacePosMap = {
			1: { right: 12, bottom: 8 }, // 巽：靠中宫（右下）
			2: { left: '50%', bottom: 8, transform: 'translateX(-50%)' }, // 离：靠中宫（下中）
			3: { left: 12, bottom: 8 }, // 坤：靠中宫（左下）
			4: { right: 12, top: '50%', transform: 'translateY(-50%)' }, // 震：靠中宫（右中）
			6: { left: 12, top: '50%', transform: 'translateY(-50%)' }, // 兑：靠中宫（左中）
			7: { right: 12, top: 8 }, // 艮：靠中宫（右上）
			8: { left: '50%', top: 8, transform: 'translateX(-50%)' }, // 坎：靠中宫（上中）
			9: { left: 12, top: 8 }, // 乾：靠中宫（左上）
		};
		const palaceStyle = palacePosMap[cell.palaceNum] || null;
		const wuHeMap = {
			甲: '己',
			乙: '庚',
			丙: '辛',
			丁: '壬',
			戊: '癸',
			己: '甲',
			庚: '乙',
			辛: '丙',
			壬: '丁',
			癸: '戊',
		};
		const centerGan = cell.tianGan || cell.diGan || '';
		const centerHeGan = centerGan ? (wuHeMap[centerGan] || '') : '';
		const centerItems = [];
		if(centerGan){
			centerItems.push({ text: centerGan, color: centerMinorColor });
		}
		if(centerHeGan){
			centerItems.push({ text: `五合${centerHeGan}`, color: centerMinorColor });
		}

		if(cell.isCenter){
			return (
				<div
					key={`cell_${cell.palaceNum}`}
					style={{
						background: '#f6f6f6',
						borderRadius: 14,
						border: '1px solid #ececec',
						height: 214,
						padding: 0,
						position: 'relative',
					}}
				>
					<div
						style={{
							position: 'absolute',
							left: '50%',
							top: '50%',
							transform: 'translate(-50%, -50%)',
							display: 'flex',
							flexDirection: 'column',
							alignItems: 'center',
							justifyContent: 'center',
							gap: 4,
						}}
					>
						{centerItems.map((item, idx)=>(
							<div
								key={`center_item_${idx}`}
								style={{
									fontSize: 32,
									lineHeight: '32px',
									fontWeight: 700,
									color: item.color,
								}}
							>
								{item.text}
							</div>
						))}
					</div>
				</div>
			);
		}

		return (
			<div
				key={`cell_${cell.palaceNum}`}
				style={{
					background: '#f6f6f6',
					borderRadius: 14,
					border: '1px solid #ececec',
					height: 214,
					padding: 0,
					position: 'relative',
				}}
			>
					{cell.isYiMa && (
						<div style={yiMaStyle}>🐎</div>
					)}

				{this.renderQimenHoverNode(
					'stem',
					cell.tianGan || ' ',
					{
						position: 'absolute',
						left: insetX,
						top: insetY,
						fontSize: unifiedFont,
						lineHeight: `${unifiedFont}px`,
						color: tianGanColor,
						fontWeight: 700,
					},
					`qimen_tiangan_${cell.palaceNum}`
				)}
				{this.renderQimenHoverNode(
					'stem',
					cell.diGan || ' ',
					{
						position: 'absolute',
						left: insetX,
						bottom: insetY,
						fontSize: unifiedFont,
						lineHeight: `${unifiedFont}px`,
						color: diGanColor,
						fontWeight: 700,
					},
					`qimen_digan_${cell.palaceNum}`
				)}
				{this.renderQimenHoverNode(
					'god',
					cell.god || ' ',
					{
						position: 'absolute',
						right: insetX,
						top: insetY,
						fontSize: unifiedFont,
						lineHeight: `${unifiedFont}px`,
						color: godColor,
						fontWeight: 700,
					},
					`qimen_god_${cell.palaceNum}`
				)}
				{this.renderQimenHoverNode(
					'star',
					cell.tianXing || ' ',
					{
						position: 'absolute',
						right: insetX,
						bottom: insetY,
						fontSize: unifiedFont,
						lineHeight: `${unifiedFont}px`,
						color: line3Color,
						fontWeight: 700,
					},
					`qimen_star_${cell.palaceNum}`
				)}
				{this.renderQimenHoverNode(
					'door',
					cell.door || ' ',
					{
						position: 'absolute',
						left: '50%',
						top: '50%',
						transform: 'translate(-50%, -50%)',
						fontSize: unifiedFont,
						lineHeight: `${unifiedFont}px`,
						color: line2Color,
						fontWeight: 700,
					},
					`qimen_door_${cell.palaceNum}`
				)}

				{!!palaceStyle && (
					<div
						style={{
							position: 'absolute',
							color: titleColor,
							fontSize: 15,
							lineHeight: '15px',
							fontWeight: 700,
							...palaceStyle,
						}}
					>
						{cell.palaceName}
					</div>
				)}
			</div>
		);
	}

	renderBoard(){
		const pan = this.state.pan;
		if(!this.state.hasPlotted){
			return <Card bordered={false}>点击右侧“起盘”后显示遁甲盘</Card>;
		}
		if(!pan){
			return <Card bordered={false}>暂无遁甲盘数据</Card>;
		}
		const cellSize = 214;
		const boardGap = 10;
		const boardWidth = (cellSize * 3) + (boardGap * 2);
		const boardScale = this.calcBoardScale();
		const scaledWidth = Math.round(boardWidth * boardScale);
		const timeInfo = getBoardTimeInfo(pan);
		const dateTitle = timeInfo.dateText;
		const shiftTitle = pan && pan.shiftPalace > 0 ? `（顺转${pan.shiftPalace}宫）` : '';
		const timeLine = `直接时间：${timeInfo.clockHm}  真太阳时：${timeInfo.solarHm}`;
		const pillars = [
			{
				key: 'year',
				label: '年',
				gan: (pan.ganzhi.year || '').substr(0, 1),
				zhi: (pan.ganzhi.year || '').substr(1, 1),
			},
			{
				key: 'month',
				label: '月',
				gan: (pan.ganzhi.month || '').substr(0, 1),
				zhi: (pan.ganzhi.month || '').substr(1, 1),
			},
			{
				key: 'day',
				label: '日',
				gan: (pan.ganzhi.day || '').substr(0, 1),
				zhi: (pan.ganzhi.day || '').substr(1, 1),
			},
			{
				key: 'time',
				label: '时',
				gan: (pan.ganzhi.time || '').substr(0, 1),
				zhi: (pan.ganzhi.time || '').substr(1, 1),
			},
		].map((item)=>({
			...item,
			ganColor: getBaZiStemColor(item.gan),
			zhiColor: getBaZiBranchColor(item.zhi),
		}));
		return (
			<Card bordered={false}>
				<div style={{ width: scaledWidth, maxWidth: '100%' }}>
					<div style={{ width: boardWidth, transform: `scale(${boardScale})`, transformOrigin: 'top left' }}>
						<div
							style={{
								padding: 12,
								borderRadius: 14,
								background: '#fbfbfb',
								border: '1px solid #efefef',
								marginBottom: 8,
								width: boardWidth,
								maxWidth: '100%',
							}}
						>
							<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
									<div style={{ display: 'flex', alignItems: 'baseline', minWidth: 0 }}>
										<span style={{ fontSize: 18, lineHeight: '22px', fontWeight: 700, color: '#222' }}>
											{dateTitle}
										</span>
										<span
											style={{
												marginLeft: '1.2em',
												fontSize: 18,
												lineHeight: '22px',
												fontWeight: 700,
												color: '#222',
												whiteSpace: 'nowrap',
											}}
										>
										{timeLine}
									</span>
								</div>
								{shiftTitle ? (
									<div style={{ fontSize: 16, lineHeight: '20px', fontWeight: 700, color: '#595959' }}>
										{shiftTitle}
									</div>
								) : null}
							</div>
							<div
								style={{
									marginTop: 6,
									display: 'flex',
									alignItems: 'flex-end',
									gap: 14,
								}}
							>
								{pillars.map((p)=>(
									<div key={`pillar_${p.key}`} style={{ display: 'flex', alignItems: 'center' }}>
										<div
											style={{
												display: 'flex',
												flexDirection: 'column',
												alignItems: 'center',
												lineHeight: 1,
												fontWeight: 700,
												fontSize: 32,
											}}
										>
											<span style={{ color: p.ganColor }}>{p.gan || ' '}</span>
											<span style={{ color: p.zhiColor, marginTop: 4 }}>{p.zhi || ' '}</span>
										</div>
										<span
											style={{
												marginLeft: 6,
												color: '#8c8c8c',
												fontSize: 24,
												lineHeight: 1,
												fontWeight: 700,
											}}
										>
											{p.label}
										</span>
									</div>
								))}
							</div>
							<div style={{ marginTop: 6, fontSize: 16, lineHeight: '20px', fontWeight: 700, color: '#202020' }}>
								{pan.juText} 值符:{pan.zhiFu} 值使:{pan.zhiShi}
							</div>
							<div style={{ marginTop: 4, fontSize: 14, lineHeight: '18px', color: '#595959' }}>
								{pan.options.kongModeLabel}-{pan.kongWang} 旬首-{pan.xunShou}
							</div>
						</div>
						<div style={{ position: 'relative', width: boardWidth, maxWidth: '100%' }}>
							<div style={{ display: 'grid', gridTemplateColumns: `repeat(3, ${cellSize}px)`, gap: boardGap }}>
								{pan.cells.map((cell)=>this.renderCell(cell))}
							</div>
							{pan.fengJu ? (
								<div
									style={{
										position: 'absolute',
										left: '50%',
										top: '50%',
										transform: 'translate(-50%, -50%)',
										width: '62%',
										maxWidth: 430,
										opacity: 0.22,
										pointerEvents: 'none',
										zIndex: 9,
									}}
								>
									<img src={sealedImage} alt="雷霆都司印章" style={{ width: '100%', height: 'auto', display: 'block' }} />
								</div>
							) : null}
						</div>
						<div style={{ marginTop: 12 }}>
							<Tag color="red">击刑</Tag>
							<Tag color="#8b5e3c">入墓</Tag>
							<Tag color="#722ed1">击刑+入墓</Tag>
							<Tag color="orange">门迫</Tag>
							<Tag color="blue">空亡</Tag>
							<Tag color="default">🐎 驿马</Tag>
						</div>
					</div>
				</div>
			</Card>
		);
	}

	renderRight(){
		const pan = this.state.pan;
		const opt = this.state.options;
		const panelTab = this.state.rightPanelTab;
		const bagongPalace = BAGONG_PALACE_NAME[this.state.bagongPalace] ? this.state.bagongPalace : BAGONG_PALACE_ORDER[0];
		const bagongData = buildQimenBaGongPanelData(pan, bagongPalace);
		const fushiYiGua = buildQimenFuShiYiGua(pan);
		const timeInfo = getBoardTimeInfo(pan);
		const showPatternInterpretation = this.state.showPatternInterpretation !== false;
		const fields = this.state.localFields || this.props.fields || {};
		let datetm = new DateTime();
		if(fields.date && fields.time){
			const str = `${fields.date.value.format('YYYY-MM-DD')} ${fields.time.value.format('HH:mm:ss')}`;
			datetm = datetm.parse(str, 'YYYY-MM-DD HH:mm:ss');
			if(fields.zone){
				datetm.setZone(fields.zone.value);
			}
		}
		return (
			<div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
				<div style={{ paddingBottom: 6, borderBottom: '1px solid #f0f0f0' }}>
					<div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
						<div>
							<PlusMinusTime value={datetm} onChange={this.onTimeChanged} hook={this.timeHook} />
						</div>

						<div style={{ display: 'flex', gap: 4 }}>
							<div style={{ flex: 1 }}>
								<Select size="small" value={opt.kongMode} onChange={(v)=>this.onOptionChange('kongMode', v)} style={{ width: '100%' }}>
									{KONG_MODE_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
								</Select>
							</div>
							<div style={{ flex: 1 }}>
								<Select size="small" value={opt.yimaMode} onChange={(v)=>this.onOptionChange('yimaMode', v)} style={{ width: '100%' }}>
									{MA_MODE_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
								</Select>
							</div>
							<div style={{ flex: 1 }}>
								<Select size="small" value={opt.qijuMethod} disabled={opt.paiPanType !== 3} onChange={(v)=>this.onOptionChange('qijuMethod', v)} style={{ width: '100%' }}>
									{QIJU_METHOD_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
								</Select>
							</div>
							<div style={{ flex: 1 }}>
								<Select size="small" value={opt.sex} onChange={this.onGenderChange} style={{ width: '100%' }}>
									{SEX_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
								</Select>
							</div>
							<div style={{ flex: 1 }}>
								<Select size="small" value={opt.shiftPalace} onChange={(v)=>this.onOptionChange('shiftPalace', v)} style={{ width: '100%' }}>
									{YIXING_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
								</Select>
							</div>
						</div>

						<div style={{ display: 'flex', gap: 4 }}>
							<div style={{ flex: 1 }}>
								<Select size="small" value={opt.paiPanType} onChange={(v)=>this.onOptionChange('paiPanType', v)} style={{ width: '100%' }}>
									{PAIPAN_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
								</Select>
							</div>
							<div style={{ flex: 1 }}>
								<Select size="small" value={opt.zhiShiType} onChange={(v)=>this.onOptionChange('zhiShiType', v)} style={{ width: '100%' }}>
									{ZHISHI_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
								</Select>
							</div>
							<div style={{ flex: 1 }}>
								<Select size="small" value={opt.yueJiaQiJuType} disabled={opt.paiPanType !== 1} onChange={(v)=>this.onOptionChange('yueJiaQiJuType', v)} style={{ width: '100%' }}>
									{YUEJIA_QIJU_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
								</Select>
							</div>
						</div>

						<div style={{ display: 'flex', gap: 4 }}>
							<div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 4 }}>
								<Select size="small" value={opt.after23NewDay} onChange={(v)=>this.onOptionChange('after23NewDay', v)} style={{ width: '100%' }}>
									{DAY_SWITCH_OPTIONS.map((item)=><Option key={`day_switch_${item.value}`} value={item.value}>{item.label}</Option>)}
								</Select>
								<div style={{ display: 'flex', gap: 4 }}>
									<Button
										size="small"
										type={showPatternInterpretation ? 'primary' : 'default'}
										style={{ flex: 1 }}
										onClick={()=>{
											const next = !showPatternInterpretation;
											this.setState({ showPatternInterpretation: next });
											savePatternInterpretationPreference(next);
										}}
									>
										释义：{showPatternInterpretation ? '是' : '否'}
									</Button>
									<div style={{ flex: 1 }}>
										<Select size="small" value={normalizeTimeAlg(opt.timeAlg)} onChange={(v)=>this.onOptionChange('timeAlg', v)} style={{ width: '100%' }}>
											{TIME_ALG_OPTIONS.map((item)=><Option key={`time_alg_${item.value}`} value={item.value}>{item.label}</Option>)}
										</Select>
									</div>
									<div style={{ flex: 1 }}>
										<GeoCoordModal onOk={this.changeGeo} lat={fields.gpsLat && fields.gpsLat.value} lng={fields.gpsLon && fields.gpsLon.value}>
											<Button size="small" style={{ width: '100%' }}>经纬度选择</Button>
										</GeoCoordModal>
									</div>
								</div>
							</div>
							<div style={{ flex: 1 }}>
								<Select size="small" value={opt.fengJu ? 1 : 0} onChange={(v)=>this.onOptionChange('fengJu', v === 1)} style={{ width: '100%' }}>
									{FENGJU_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
								</Select>
							</div>
							<div style={{ flex: 1 }}>
								<Button
									size="small"
									type="primary"
									style={{ width: '100%' }}
									onClick={this.clickPlot}
									loading={this.state.loading}
									disabled={this.state.loading}
								>
									起盘
								</Button>
							</div>
							<div style={{ flex: 1 }}>
								<Button size="small" style={{ width: '100%' }} onClick={this.clickSaveCase}>保存</Button>
							</div>
						</div>
						<div style={{ textAlign: 'right' }}>
							<span>{fields.lon ? fields.lon.value : ''} {fields.lat ? fields.lat.value : ''}</span>
						</div>
					</div>
				</div>

				<Tabs
					activeKey={panelTab}
					onChange={(key)=>this.setState({ rightPanelTab: key })}
					style={{ marginTop: 8 }}
				>
					<TabPane tab="概览" key="overview">
						<Card bordered={false} bodyStyle={{ padding: '10px 12px', maxHeight: 'calc(100vh - 420px)', overflowY: 'auto' }}>
							<div style={{ lineHeight: '26px' }}>
								<div>命式：{pan ? pan.options.sexLabel : '—'}</div>
								<div>符头：{pan ? pan.fuTou : '—'}</div>
								<div>节气：{pan ? pan.jieqiText : '—'}</div>
								<div>局数：{pan ? pan.juText : '—'}</div>
								<div>旬首：{pan ? pan.xunShou : '—'}</div>
								<div>{pan ? pan.options.kongModeLabel : '空亡'}：{pan ? pan.kongWang : '—'}</div>
								<div>值符：{pan ? pan.zhiFu : '—'}</div>
								<div>值使：{pan ? pan.zhiShi : '—'}</div>
								<div>奇门演卦：{pan ? (fushiYiGua.text || '无') : '—'}</div>
								<div>移星：{pan ? (pan.options.shiftLabel || '原宫') : '原宫'}</div>
								<div>换日：{pan ? (pan.options.daySwitchLabel || '子初换日') : (opt.after23NewDay === 1 ? '子初换日' : '子正换日')}</div>
								<div>时间算法：{pan ? (pan.options.timeAlgLabel || getTimeAlgLabel(opt.timeAlg)) : getTimeAlgLabel(opt.timeAlg)}</div>
								<div>奇门封局：{pan ? (pan.options.fengJuLabel || '未封局') : (opt.fengJu ? '已封局' : '未封局')}</div>
								<div>六仪击刑：{pan && pan.liuYiJiXing.length ? pan.liuYiJiXing.join('；') : '无'}</div>
								<div>奇仪入墓：{pan && pan.qiYiRuMu.length ? pan.qiYiRuMu.join('；') : '无'}</div>
								<div>门迫：{pan && pan.menPo && pan.menPo.list.length ? pan.menPo.list.join('；') : '无'}</div>
								<div>空亡宫：{pan && pan.kongWangDesc && pan.kongWangDesc.length ? pan.kongWangDesc.join('；') : '无'}</div>
								<div>{pan && pan.yiMa ? pan.yiMa.text : '日马：无'}</div>
								<div>农历：{pan ? pan.lunarText : '—'}</div>
								<div>直接时间：{timeInfo.clockHm}</div>
								<div>真太阳时：{timeInfo.solarHm}</div>
								<div>干支：{pan ? `年${pan.ganzhi.year} 月${pan.ganzhi.month} 日${pan.ganzhi.day} 时${pan.ganzhi.time}` : '—'}</div>
								<div>节气段：{pan ? (pan.jiedelta || '—') : '—'}</div>
							</div>
						</Card>
					</TabPane>
					<TabPane tab="神煞" key="shensha">
						<Card bordered={false} bodyStyle={{ padding: '10px 12px', maxHeight: 'calc(100vh - 420px)', overflowY: 'auto' }}>
							<div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', columnGap: 14, rowGap: 6, lineHeight: '24px' }}>
								{pan && pan.shenSha && pan.shenSha.allItems && pan.shenSha.allItems.length
									? pan.shenSha.allItems.map((item)=>(<div key={`ss_item_${item.name}`}><span style={{ color: '#262626' }}>{item.name}-</span><span style={{ color: '#8c8c8c' }}>{item.value}</span></div>))
									: <div>暂无神煞</div>}
							</div>
						</Card>
					</TabPane>
					<TabPane tab="八宫" key="bagong">
						<Card bordered={false} bodyStyle={{ padding: '10px 12px', maxHeight: 'calc(100vh - 420px)', overflowY: 'auto' }}>
							<div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 10 }}>
								{BAGONG_PALACE_ORDER.map((num)=>(
									<Button
										key={`bagong_btn_${num}`}
										size="small"
										shape="round"
										type={bagongPalace === num ? 'primary' : 'default'}
										style={bagongPalace === num ? { minWidth: 42 } : { minWidth: 42, background: '#fafafa' }}
										onClick={()=>this.setState({ bagongPalace: num })}
									>
										{BAGONG_PALACE_NAME[num]}
									</Button>
								))}
							</div>
							{pan ? (
								<div>
									<Card size='small' style={{ marginBottom: 8 }}>
										<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
											<span style={{ fontWeight: 600 }}>奇门吉格</span>
											<Tag color='green'>{bagongData.jiPatterns.length}项</Tag>
										</div>
										<div style={{ color: '#595959', lineHeight: '22px', whiteSpace: 'pre-wrap' }}>
											{showPatternInterpretation
												? (bagongData.jiPatternDetails && bagongData.jiPatternDetails.length
													? bagongData.jiPatternDetails.map((text)=>`• ${text}`).join('\n')
													: '未命中')
												: (bagongData.jiPatterns.length ? bagongData.jiPatterns.join('、') : '未命中')}
										</div>
									</Card>
									<Card size='small' style={{ marginBottom: 8 }}>
										<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
											<span style={{ fontWeight: 600 }}>奇门凶格</span>
											<Tag color='volcano'>{bagongData.xiongPatterns.length}项</Tag>
										</div>
										<div style={{ color: '#595959', lineHeight: '22px', whiteSpace: 'pre-wrap' }}>
											{showPatternInterpretation
												? (bagongData.xiongPatternDetails && bagongData.xiongPatternDetails.length
													? bagongData.xiongPatternDetails.map((text)=>`• ${text}`).join('\n')
													: '未命中')
												: (bagongData.xiongPatterns.length ? bagongData.xiongPatterns.join('、') : '未命中')}
										</div>
									</Card>
									<Card size='small' style={{ marginBottom: 8 }}>
										<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
											<span style={{ fontWeight: 600 }}>十干克应</span>
											<Tag color='blue'>天{bagongData.tianGan || '—'} / 地{bagongData.diGan || '—'}</Tag>
										</div>
										<div style={{ color: '#595959', lineHeight: '22px', whiteSpace: 'pre-wrap' }}>
											天{bagongData.tianGan || '—'}加地{bagongData.diGan || '—'}：{bagongData.tenGanText}
										</div>
									</Card>
									<Card size='small' style={{ marginBottom: 8 }}>
										<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
											<span style={{ fontWeight: 600 }}>八门克应和奇仪主应</span>
											<Tag color='purple'>人{bagongData.renDoor || '—'}</Tag>
										</div>
										<div style={{ color: '#595959', lineHeight: '22px', whiteSpace: 'pre-wrap' }}>
											<div>人{bagongData.renDoor || '—'}加地{bagongData.baseDoor || '—'}：{bagongData.doorBaseText}</div>
											<div style={{ marginTop: 4 }}>人{bagongData.renDoor || '—'}加天{bagongData.tianGan || '—'}：{bagongData.doorTianText}</div>
										</div>
									</Card>
									<Card size='small'>
										<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
											<span style={{ fontWeight: 600 }}>八神加八门</span>
											<Tag color='geekblue'>{bagongData.godFull || '—'}</Tag>
										</div>
										<div style={{ color: '#595959', lineHeight: '22px', whiteSpace: 'pre-wrap' }}>
											{bagongData.godFull || '—'}加{bagongData.renDoor || '—'}门：{bagongData.godDoorText}
										</div>
									</Card>
									<Card size='small' style={{ marginTop: 8 }}>
										<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
											<span style={{ fontWeight: 600 }}>奇门演卦</span>
											<Tag color='cyan'>{bagongData.menFangYiGua || '无'}</Tag>
										</div>
										<div style={{ color: '#595959', lineHeight: '22px', whiteSpace: 'pre-wrap' }}>
											{bagongData.menFangYiGuaText || '无'}
										</div>
									</Card>
								</div>
							) : (
								<Card size='small'>
									<div style={{ color: '#8c8c8c' }}>请先起盘后查看八宫信息。</div>
								</Card>
							)}
						</Card>
					</TabPane>
				</Tabs>
			</div>
		);
	}

	render(){
		let height = this.props.height ? this.props.height : 760;
		if(height === '100%'){
			height = 'calc(100% - 70px)';
		}else{
			height = height - 20;
		}
		return (
			<div style={{ minHeight: height }}>
				<Spin spinning={this.state.loading}>
					<Row gutter={6}>
						<Col span={16}>
							<div ref={this.captureLeftBoardHost}>
								{this.renderBoard()}
							</div>
						</Col>
						<Col span={8}>
							{this.renderRight()}
						</Col>
					</Row>
				</Spin>
			</div>
		);
	}
}

export default DunJiaMain;
