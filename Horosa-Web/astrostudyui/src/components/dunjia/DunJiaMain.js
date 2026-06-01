import { Component } from 'react';
import { Spin, Tag, message, Popover } from 'antd';
import { XQButton as Button, XQCard as Card, XQSelect as Select, XQTabs as Tabs } from '../xq-ui';
import XQIcon from '../xq-icons';
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
import SpaceTimePanel from '../comp/SpaceTimePanel';
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
	fetchQimenPan,
	isKinqimenMode,
	normalizeKinqimenData,
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
import { defaultAfter23NewDay, defaultLateZiHourUseNextDay } from '../../utils/dayBoundary';

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
	after23NewDay: defaultAfter23NewDay(),
	lateZiHourUseNextDay: defaultLateZiHourUseNextDay(),
	fengJu: false,
};

const DUNJIA_BOARD_BASE_WIDTH = 662;
const DUNJIA_BOARD_BASE_HEIGHT = 870;
const DUNJIA_SCALE_MIN = 0.58;
const DUNJIA_SCALE_MAX = 1.18;
const QIMEN_PATTERN_INTERPRETATION_STORAGE_KEY = 'qimenShowPatternInterpretation';
let lastDunJiaLiveState = null;
function normalizeKenQimenOptions(options){
	const next = {
		...DEFAULT_OPTIONS,
		...(options || {}),
	};
	if(next.paiPanType === 1){
		next.paiPanType = 3;
	}
	return next;
}
const DUNJIA_LEGEND_ITEMS = [
	{ key: 'jixing', label: '击刑', color: '#cf1322', bg: 'rgba(207, 19, 34, 0.10)' },
	{ key: 'rumu', label: '入墓', color: '#8b5e3c', bg: 'rgba(139, 94, 60, 0.12)' },
	{ key: 'both', label: '击刑+入墓', color: '#722ed1', bg: 'rgba(114, 46, 209, 0.10)' },
	{ key: 'menpo', label: '门迫', color: '#fa8c16', bg: 'rgba(250, 140, 22, 0.12)' },
	{ key: 'kongwang', label: '空亡', color: '#2f54eb', bg: 'rgba(47, 84, 235, 0.10)' },
	{ key: 'yima', label: '🐎 驿马', color: 'var(--horosa-text, #262626)', bg: 'rgba(140, 140, 140, 0.10)' },
];

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
	return GAN_COLOR_MAP[safe(stem, '')] || 'var(--horosa-text, #333333)';
}

function getBaZiBranchColor(branch){
	return ZhiColor[safe(branch, '')] || 'var(--horosa-text, #333333)';
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
	return options && options.after23NewDay === 1 ? 1 : 0;
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
		safe(options.lateZiHourUseNextDay),
		getTimeAlgValue(options),
		options.fengJu ? 1 : 0,
	].join('|');
}

function needJieqiYearSeed(options){
	const opt = options || {};
	if(isKinqimenMode(opt.paiPanType)){
		return false;
	}
	return opt.paiPanType === 3 && opt.qijuMethod === 'zhirun';
}

function rememberDunJiaLiveState(payload){
	if(!payload || !payload.pan){
		return;
	}
	lastDunJiaLiveState = {
		fieldKey: payload.fieldKey || '',
		lastNongliKey: payload.lastNongliKey || '',
		lastPanSignature: payload.lastPanSignature || '',
		nongli: payload.nongli || null,
		displaySolarTime: payload.displaySolarTime || '',
		pan: payload.pan,
		options: payload.options ? { ...payload.options } : null,
	};
}

function getRestorableDunJiaLiveState(fields){
	if(!lastDunJiaLiveState || !lastDunJiaLiveState.pan){
		return null;
	}
	const fieldKey = getFieldKey(fields);
	if(lastDunJiaLiveState.fieldKey && fieldKey && lastDunJiaLiveState.fieldKey !== fieldKey){
		return null;
	}
	return lastDunJiaLiveState;
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
		const restoredLiveState = getRestorableDunJiaLiveState(props.fields);
		const initialOptions = restoredLiveState && restoredLiveState.options
			? normalizeKenQimenOptions(restoredLiveState.options)
			: normalizeKenQimenOptions();

		this.state = {
			loading: false,
			nongli: restoredLiveState ? restoredLiveState.nongli : null,
			displaySolarTime: restoredLiveState ? restoredLiveState.displaySolarTime : '',
			pan: restoredLiveState ? restoredLiveState.pan : null,
			localFields: null,
			hasPlotted: !!(restoredLiveState && restoredLiveState.pan),
			rightPanelTab: 'overview',
			bagongPalace: BAGONG_PALACE_ORDER[0],
			showPatternInterpretation: loadPatternInterpretationPreference(),
			leftBoardWidth: 0,
			leftBoardHeight: 0,
			viewportHeight: getViewportHeight(),
			options: initialOptions,
		};

		this.unmounted = false;
		this.jieqiSeedPromises = {};
		this.jieqiYearSeeds = {};
		this.lastRestoredCaseId = null;
		this.timeHook = {};
		this.lastNongliKey = restoredLiveState ? restoredLiveState.lastNongliKey : '';
		this.lastPanSignature = restoredLiveState ? restoredLiveState.lastPanSignature : '';
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

	async getResolvedPan(fields, nongli, options, displaySolarTime){
		const ctx = this.getContext(fields, displaySolarTime);
		const fallbackPan = this.getCachedPan(fields, nongli, options, displaySolarTime);
		if(!fallbackPan || !isKinqimenMode(options && options.paiPanType)){
			return fallbackPan;
		}
		const backendPan = await fetchQimenPan(fields, nongli, options, ctx);
		return normalizeKinqimenData(backendPan, fallbackPan, options, nongli);
	}

	componentDidMount(){
		this.unmounted = false;
		this._after23BoundaryUserOverrode = false; // 用户改过左栏下拉后,全局事件不再覆盖(用户拍板:左栏最高权限)
		this._lateZiHourUserOverrode = false; // v2.2.1: 同上 — 时柱开关也尊重左栏覆盖
		if(typeof window !== 'undefined'){
			window.addEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
			this._dayBoundaryListener = (ev) => {
				if(this._after23BoundaryUserOverrode) return;
				const v = ev && ev.detail ? ev.detail.after23NewDay : null;
				if((v === 0 || v === 1) && typeof this.onOptionChange === 'function'){
					this.onOptionChange('after23NewDay', v, { fromGlobal: true });
				}
			};
			window.addEventListener('horosa:day-boundary-changed', this._dayBoundaryListener);
			this._lateZiHourListener = (ev) => {
				if(this._lateZiHourUserOverrode) return;
				const v = ev && ev.detail ? ev.detail.lateZiHourUseNextDay : null;
				if((v === 0 || v === 1) && typeof this.onOptionChange === 'function'){
					this.onOptionChange('lateZiHourUseNextDay', v, { fromGlobal: true });
				}
			};
			window.addEventListener('horosa:late-zi-hour-mode-changed', this._lateZiHourListener);
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
			if(this._dayBoundaryListener){
				window.removeEventListener('horosa:day-boundary-changed', this._dayBoundaryListener);
			}
			if(this._lateZiHourListener){
				window.removeEventListener('horosa:late-zi-hour-mode-changed', this._lateZiHourListener);
			}
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
		const leftBoardHeight = this.leftBoardHost ? this.leftBoardHost.clientHeight : 0;
		const changed = Math.abs((this.state.leftBoardWidth || 0) - leftBoardWidth) >= 2
			|| Math.abs((this.state.leftBoardHeight || 0) - leftBoardHeight) >= 2
			|| Math.abs((this.state.viewportHeight || 0) - viewportHeight) >= 2;
		if(changed){
			this.setState({
				leftBoardWidth,
				leftBoardHeight,
				viewportHeight,
			});
		}
	}

	calcBoardScale(){
		const viewH = this.state.viewportHeight || 900;
		const availW = this.state.leftBoardWidth > 0 ? (this.state.leftBoardWidth - 22) : DUNJIA_BOARD_BASE_WIDTH;
		const availH = this.state.leftBoardHeight > 0 ? (this.state.leftBoardHeight - 12) : (viewH - 96);
		const widthScale = availW / DUNJIA_BOARD_BASE_WIDTH;
		const heightScale = availH / DUNJIA_BOARD_BASE_HEIGHT;
		// 遁甲盘直接铺在中心栏里，缩放以实际容器高宽为准，不再预留旧卡片外框空间。
		let rawScale = Math.min(widthScale, heightScale);
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
		if(nextOptions.paiPanType === 1){
			nextOptions.paiPanType = 3;
			changed = true;
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
			// v2.2.1: 透传时柱开关给后端 /nongli/time;后端 NongliController 已读入并传给 OnlyFourColumns。
			lateZiHourUseNextDay: options && options.lateZiHourUseNextDay !== undefined ? options.lateZiHourUseNextDay : 1,
		};
	}

	async recalc(fields, nongli, options, displaySolarTime){
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
		const remoteMode = isKinqimenMode(fixedOptions.paiPanType);
		if(remoteMode && !this.state.loading){
			this.setState({ loading: true });
		}
		try{
			const pan = await this.getResolvedPan(flds, nongli || this.state.nongli, fixedOptions, displaySolar);
			this.lastPanSignature = panSignature;
			this.setState({ pan, displaySolarTime: displaySolar, loading: false }, ()=>{
				if(pan){
					rememberDunJiaLiveState({
						fieldKey: getFieldKey(flds),
						lastNongliKey: this.lastNongliKey,
						lastPanSignature: this.lastPanSignature,
						nongli: nongli || this.state.nongli,
						displaySolarTime: displaySolar,
						pan,
						options: fixedOptions,
					});
					const snapshotText = saveQimenLiveSnapshot(pan);
					if(snapshotText){
						saveModuleAISnapshot('qimen', snapshotText);
					}
				}
			});
		}catch(e){
			if(!this.unmounted){
				this.setState({ loading: false });
				message.error('遁甲计算失败：本地奇门服务不可用');
			}
		}
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
					const pan = await this.getResolvedPan(flds, result, fixedOptions, displaySolarTime);
					this.lastNongliKey = requestKey;
					this.lastPanSignature = panSignature;
						this.setState({
							nongli: result,
							displaySolarTime,
							pan,
							hasPlotted: true,
							loading: false,
						}, ()=>{
						if(pan){
							rememberDunJiaLiveState({
								fieldKey: getFieldKey(flds),
								lastNongliKey: this.lastNongliKey,
								lastPanSignature: this.lastPanSignature,
								nongli: result,
								displaySolarTime,
								pan,
								options: fixedOptions,
							});
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

	onOptionChange(key, value, opts){
		if(key === 'paiPanType' && value === 1){
			message.warning('月家奇门暂未由 Ken 后端支持，已从排盘选项移除');
			return;
		}
		// 用户拍板: 左栏改过 after23NewDay 后,全局事件不再覆盖(最高权限)。fromGlobal 时不打用户改过的标记。
		if(key === 'after23NewDay' && !(opts && opts.fromGlobal)){
			this._after23BoundaryUserOverrode = true;
		}
		// v2.2.1: 时柱开关同款局部覆盖语义
		if(key === 'lateZiHourUseNextDay' && !(opts && opts.fromGlobal)){
			this._lateZiHourUserOverrode = true;
		}
		const nextVal = key === 'timeAlg' ? normalizeTimeAlg(value) : value;
		const options = normalizeKenQimenOptions({
			...this.state.options,
			[key]: nextVal,
		});
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
				<div style={{ fontSize: 17, lineHeight: '24px', fontWeight: 700, color: 'var(--horosa-text, #1f1f1f)' }}>
					{tipObj.title}
				</div>
				<div style={{ borderTop: '1px solid var(--horosa-border, #d9d9d9)', margin: '6px 0 8px' }} />
				{blocks.map((block, idx)=>{
					if(!block){
						return null;
					}
					if(block.type === 'blank'){
						return <div key={`qimen_doc_blank_${idx}`} style={{ height: 6 }} />;
					}
					if(block.type === 'divider'){
						return <div key={`qimen_doc_divider_${idx}`} style={{ borderTop: '1px solid var(--horosa-border, #e8e8e8)', margin: '6px 0' }} />;
					}
					if(block.type === 'subTitle'){
						return (
							<div key={`qimen_doc_subtitle_${idx}`} style={{ margin: '4px 0 6px' }}>
								<div style={{ fontSize: 14, lineHeight: '20px', fontWeight: 700, color: 'var(--horosa-text, #262626)' }}>{block.text}</div>
								<div style={{ borderTop: '1px solid var(--horosa-border, #efefef)', marginTop: 4 }} />
							</div>
						);
					}
					const html = formatQimenDocLineToHtml(block.text || '');
					return (
						<div
							key={`qimen_doc_text_${idx}`}
							style={{ fontSize: 13, lineHeight: '21px', color: 'var(--horosa-text, #262626)', whiteSpace: 'pre-wrap' }}
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
		const titleColor = cell.hasKongWang
			? 'var(--horosa-accent, #2f54eb)'
			: (cell.isCenter ? 'var(--horosa-muted, #c7c7c7)' : 'var(--horosa-text-soft, #5f5f5f)');
		let tianGanColor = 'var(--horosa-text, #262626)';
		if(cell.hasJiXing && cell.hasRuMu){
			tianGanColor = '#722ed1';
		}else if(cell.hasJiXing){
			tianGanColor = '#cf1322';
		}else if(cell.hasRuMu){
			tianGanColor = '#8b5e3c';
		}
		// 八神不跟随值符或天盘干状态染色，保持独立显示。
		const godColor = 'var(--horosa-text, #262626)';
		const line2Color = cell.hasMenPo ? '#fa8c16' : 'var(--horosa-text, #262626)';
		const line3Color = 'var(--horosa-text, #262626)';
		const diGanColor = 'var(--horosa-text, #262626)';
		const centerMinorColor = 'var(--horosa-muted, #8c8c8c)';
		const unifiedFont = 34;
		const insetX = 52;
		const insetY = 40;
		const isGenPalace = cell.palaceNum === 7 || cell.palaceName === '艮';
		const yiMaStyle = isGenPalace
			? { position: 'absolute', left: 10, bottom: 8, fontSize: 20, lineHeight: '20px', color: 'var(--horosa-text, #111)' }
			: { position: 'absolute', top: 8, right: 10, fontSize: 20, lineHeight: '20px', color: 'var(--horosa-text, #111)' };

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
						background: 'var(--horosa-panel-soft, #f6f6f6)',
						borderRadius: 14,
						border: '1px solid var(--horosa-border, #ececec)',
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
					background: 'var(--horosa-panel-soft, #f6f6f6)',
					borderRadius: 14,
					border: '1px solid var(--horosa-border, #ececec)',
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
			return <Card bordered={false}>点击左侧“起盘”后显示遁甲盘</Card>;
		}
		if(!pan){
			return <Card bordered={false}>暂无遁甲盘数据</Card>;
		}
		const cellSize = 214;
		const boardGap = 10;
		const boardWidth = (cellSize * 3) + (boardGap * 2);
		const boardScale = this.calcBoardScale();
		const scaledWidth = Math.round(boardWidth * boardScale);
		const scaledHeight = Math.round(DUNJIA_BOARD_BASE_HEIGHT * boardScale);
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
			<div
				className="horosa-dunjia-board-shell xq-chart-renderer xq-chart-renderer-qimen"
				style={{ width: scaledWidth, height: scaledHeight, maxWidth: '100%', margin: '0 auto' }}
			>
					<div style={{ width: boardWidth, transform: `scale(${boardScale})`, transformOrigin: 'top left' }}>
						<div
							className="horosa-dunjia-board-summary"
							style={{
								padding: 12,
								borderRadius: 14,
								background: 'var(--horosa-surface-solid, #fbfbfb)',
								border: '1px solid var(--horosa-border, #efefef)',
								marginBottom: 8,
								width: boardWidth,
								maxWidth: '100%',
							}}
						>
							<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
									<div style={{ display: 'flex', alignItems: 'baseline', minWidth: 0 }}>
										<span style={{ fontSize: 18, lineHeight: '22px', fontWeight: 700, color: 'var(--horosa-text, #222)' }}>
											{dateTitle}
										</span>
										<span
											style={{
												marginLeft: '1.2em',
												fontSize: 18,
												lineHeight: '22px',
												fontWeight: 700,
												color: 'var(--horosa-text, #222)',
												whiteSpace: 'nowrap',
											}}
										>
										{timeLine}
									</span>
								</div>
								{shiftTitle ? (
									<div style={{ fontSize: 16, lineHeight: '20px', fontWeight: 700, color: 'var(--horosa-text-soft, #595959)' }}>
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
												color: 'var(--horosa-muted, #8c8c8c)',
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
							<div style={{ marginTop: 6, fontSize: 16, lineHeight: '20px', fontWeight: 700, color: 'var(--horosa-text, #202020)' }}>
								{pan.juText} 值符:{pan.zhiFu} 值使:{pan.zhiShi}
							</div>
							<div style={{ marginTop: 4, fontSize: 14, lineHeight: '18px', color: 'var(--horosa-text-soft, #595959)' }}>
								{pan.options.kongModeLabel}-{pan.kongWang} 旬首-{pan.xunShou}
							</div>
						</div>
						<div className="horosa-dunjia-grid-wrap" style={{ position: 'relative', width: boardWidth, maxWidth: '100%' }}>
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
						<div className="horosa-dunjia-board-tags" style={{ marginTop: 12 }}>
							{DUNJIA_LEGEND_ITEMS.map((item)=>(
								<span
									key={item.key}
									className="horosa-dunjia-legend-tag"
									style={{
										'--qimen-legend-color': item.color,
										'--qimen-legend-bg': item.bg,
									}}
								>
									{item.label}
								</span>
							))}
						</div>
					</div>
			</div>
		);
	}

	renderInputPanel(){
		const opt = this.state.options;
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
			<div className="horosa-dunjia-input-stack">
				<div className="horosa-side-panel-heading">
					<div>
						<div className="horosa-side-panel-title">遁甲设置</div>
						<div className="horosa-side-panel-subtitle">时间、地点与起盘选项</div>
					</div>
				</div>
				<SpaceTimePanel
					fields={fields}
					value={datetm}
					onTimeChange={this.onTimeChanged}
					timeHook={this.timeHook}
					onGeoChange={this.changeGeo}
				/>
				<div className="horosa-dunjia-input-section">
					<div className="horosa-dunjia-field-title">
						<XQIcon name="sliders" />
						<span>选项</span>
					</div>
					<div className="horosa-dunjia-select-grid">
						<label className="horosa-dunjia-select-field">
							<span>排盘</span>
							<Select size="small" value={opt.paiPanType} onChange={(v)=>this.onOptionChange('paiPanType', v)}>
								{PAIPAN_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-dunjia-select-field">
							<span>值使</span>
							<Select size="small" value={opt.zhiShiType} onChange={(v)=>this.onOptionChange('zhiShiType', v)}>
								{ZHISHI_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-dunjia-select-field">
							<span>起局</span>
							<Select size="small" value={opt.qijuMethod} disabled={[3, 4, 5].indexOf(opt.paiPanType) < 0} onChange={(v)=>this.onOptionChange('qijuMethod', v)}>
								{QIJU_METHOD_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-dunjia-select-field is-wide">
							<span>月家</span>
							<Select size="small" value={opt.yueJiaQiJuType} disabled={opt.paiPanType !== 1} onChange={(v)=>this.onOptionChange('yueJiaQiJuType', v)}>
								{YUEJIA_QIJU_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-dunjia-select-field">
							<span>空亡</span>
							<Select size="small" value={opt.kongMode} onChange={(v)=>this.onOptionChange('kongMode', v)}>
								{KONG_MODE_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-dunjia-select-field">
							<span>驿马</span>
							<Select size="small" value={opt.yimaMode} onChange={(v)=>this.onOptionChange('yimaMode', v)}>
								{MA_MODE_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-dunjia-select-field">
							<span>性别</span>
							<Select size="small" value={opt.sex} onChange={this.onGenderChange}>
								{SEX_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-dunjia-select-field">
							<span>移星</span>
							<Select size="small" value={opt.shiftPalace} onChange={(v)=>this.onOptionChange('shiftPalace', v)}>
								{YIXING_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-dunjia-select-field">
							<span>日界</span>
							<Select size="small" value={opt.after23NewDay} onChange={(v)=>this.onOptionChange('after23NewDay', v)}>
								{DAY_SWITCH_OPTIONS.map((item)=><Option key={`day_switch_${item.value}`} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-dunjia-select-field">
							<span>时间算法</span>
							<Select size="small" value={normalizeTimeAlg(opt.timeAlg)} onChange={(v)=>this.onOptionChange('timeAlg', v)}>
								{TIME_ALG_OPTIONS.map((item)=><Option key={`time_alg_${item.value}`} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<label className="horosa-dunjia-select-field">
							<span>封局</span>
							<Select size="small" value={opt.fengJu ? 1 : 0} onChange={(v)=>this.onOptionChange('fengJu', v === 1)}>
								{FENGJU_OPTIONS.map((item)=><Option key={item.value} value={item.value}>{item.label}</Option>)}
							</Select>
						</label>
						<div className="horosa-dunjia-toggle-field">
							<span>格局释义</span>
							<Button
								type={showPatternInterpretation ? 'primary' : 'default'}
								onClick={()=>{
									const next = !showPatternInterpretation;
									this.setState({ showPatternInterpretation: next });
									savePatternInterpretationPreference(next);
								}}
							>
								{showPatternInterpretation ? '显示' : '隐藏'}
							</Button>
						</div>
					</div>
					<div className="horosa-dunjia-action-row">
						<Button type="primary" onClick={this.clickPlot} loading={this.state.loading} disabled={this.state.loading}>起盘</Button>
						<Button onClick={this.clickSaveCase}>保存</Button>
					</div>
				</div>
			</div>
		);
	}

	renderRight(){
		const pan = this.state.pan;
		const opt = this.state.options;
		const validPanelTabs = ['overview', 'shensha', 'bagong'];
		const panelTab = validPanelTabs.indexOf(this.state.rightPanelTab) >= 0 ? this.state.rightPanelTab : 'overview';
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
				<div style={{ display: 'none', paddingBottom: 6, borderBottom: '1px solid var(--horosa-border, #f0f0f0)' }}>
					<div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
						<div>
							<PlusMinusTime value={datetm} onChange={this.onTimeChanged} hook={this.timeHook} confirmOnAdjust />
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
								<Select size="small" value={opt.qijuMethod} disabled={[3, 4, 5].indexOf(opt.paiPanType) < 0} onChange={(v)=>this.onOptionChange('qijuMethod', v)} style={{ width: '100%' }}>
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
							<div style={{ flex: 1.45 }}>
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
					className="horosa-dunjia-tabs"
					activeKey={panelTab}
					onChange={(key)=>this.setState({ rightPanelTab: key })}
					style={{ marginTop: 8 }}
				>
					<TabPane tab="概览" key="overview">
						<Card bordered={false} bodyStyle={{ padding: '10px 12px' }}>
							<div style={{ lineHeight: '26px' }}>
								<div>命式：{pan ? pan.options.sexLabel : '—'}</div>
								<div>起盘方式：{pan ? (pan.qimenModeLabel || pan.options.paiPanLabel || '—') : '—'}</div>
								<div>符头：{pan ? pan.fuTou : '—'}</div>
								<div>节气：{pan ? pan.jieqiText : '—'}</div>
								<div>局数：{pan ? pan.juText : '—'}</div>
								<div>旬首：{pan ? pan.xunShou : '—'}</div>
								<div>{pan ? pan.options.kongModeLabel : '空亡'}：{pan ? pan.kongWang : '—'}</div>
								<div>值符：{pan ? pan.zhiFu : '—'}</div>
								<div>值使：{pan ? pan.zhiShi : '—'}</div>
								<div>奇门演卦：{pan ? (fushiYiGua.text || '无') : '—'}</div>
								<div>移星：{pan ? (pan.options.shiftLabel || '原宫') : '原宫'}</div>
								<div>换日：{pan ? (pan.options.daySwitchLabel || '23点算第二天') : (opt.after23NewDay === 1 ? '23点算第二天' : '24点算第二天')}</div>
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
						<Card bordered={false} bodyStyle={{ padding: '10px 12px' }}>
							<div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', columnGap: 14, rowGap: 6, lineHeight: '24px' }}>
								{pan && pan.shenSha && pan.shenSha.allItems && pan.shenSha.allItems.length
									? pan.shenSha.allItems.map((item)=>(<div key={`ss_item_${item.name}`}><span style={{ color: 'var(--horosa-text, #262626)' }}>{item.name}-</span><span style={{ color: 'var(--horosa-muted, #8c8c8c)' }}>{item.value}</span></div>))
									: <div>暂无神煞</div>}
							</div>
						</Card>
					</TabPane>
					<TabPane tab="八宫" key="bagong">
						<Card bordered={false} bodyStyle={{ padding: '10px 12px' }}>
							<div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 10 }}>
								{BAGONG_PALACE_ORDER.map((num)=>(
									<Button
										key={`bagong_btn_${num}`}
										size="small"
										shape="round"
										type={bagongPalace === num ? 'primary' : 'default'}
										style={bagongPalace === num ? { minWidth: 42 } : { minWidth: 42, background: 'var(--horosa-panel-soft, #fafafa)' }}
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
										<div style={{ color: 'var(--horosa-text-soft, #595959)', lineHeight: '22px', whiteSpace: 'pre-wrap' }}>
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
										<div style={{ color: 'var(--horosa-text-soft, #595959)', lineHeight: '22px', whiteSpace: 'pre-wrap' }}>
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
										<div style={{ color: 'var(--horosa-text-soft, #595959)', lineHeight: '22px', whiteSpace: 'pre-wrap' }}>
											天{bagongData.tianGan || '—'}加地{bagongData.diGan || '—'}：{bagongData.tenGanText}
										</div>
									</Card>
									<Card size='small' style={{ marginBottom: 8 }}>
										<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
											<span style={{ fontWeight: 600 }}>八门克应和奇仪主应</span>
											<Tag color='purple'>人{bagongData.renDoor || '—'}</Tag>
										</div>
										<div style={{ color: 'var(--horosa-text-soft, #595959)', lineHeight: '22px', whiteSpace: 'pre-wrap' }}>
											<div>人{bagongData.renDoor || '—'}加地{bagongData.baseDoor || '—'}：{bagongData.doorBaseText}</div>
											<div style={{ marginTop: 4 }}>人{bagongData.renDoor || '—'}加天{bagongData.tianGan || '—'}：{bagongData.doorTianText}</div>
										</div>
									</Card>
									<Card size='small'>
										<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
											<span style={{ fontWeight: 600 }}>八神加八门</span>
											<Tag color='geekblue'>{bagongData.godFull || '—'}</Tag>
										</div>
										<div style={{ color: 'var(--horosa-text-soft, #595959)', lineHeight: '22px', whiteSpace: 'pre-wrap' }}>
											{bagongData.godFull || '—'}加{bagongData.renDoor || '—'}门：{bagongData.godDoorText}
										</div>
									</Card>
									<Card size='small' style={{ marginTop: 8 }}>
										<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
											<span style={{ fontWeight: 600 }}>奇门演卦</span>
											<Tag color='cyan'>{bagongData.menFangYiGua || '无'}</Tag>
										</div>
										<div style={{ color: 'var(--horosa-text-soft, #595959)', lineHeight: '22px', whiteSpace: 'pre-wrap' }}>
											{bagongData.menFangYiGuaText || '无'}
										</div>
									</Card>
								</div>
							) : (
								<Card size='small'>
									<div style={{ color: 'var(--horosa-muted, #8c8c8c)' }}>请先起盘后查看八宫信息。</div>
								</Card>
							)}
						</Card>
					</TabPane>
				</Tabs>
			</div>
		);
	}

	renderQuickDock(){
		const validPanelTabs = ['overview', 'shensha', 'bagong'];
		const panelTab = validPanelTabs.indexOf(this.state.rightPanelTab) >= 0 ? this.state.rightPanelTab : 'overview';
		const showPatternInterpretation = this.state.showPatternInterpretation !== false;
		const items = [
			{
				key: 'overview',
				label: '概览',
				icon: 'target',
				active: panelTab === 'overview',
				onClick: ()=>this.setState({ rightPanelTab: 'overview' }),
			},
			{
				key: 'shensha',
				label: '神煞',
				icon: 'sidePlanets',
				active: panelTab === 'shensha',
				onClick: ()=>this.setState({ rightPanelTab: 'shensha' }),
			},
			{
				key: 'bagong',
				label: '八宫',
				icon: 'sideHouses',
				active: panelTab === 'bagong',
				onClick: ()=>this.setState({ rightPanelTab: 'bagong' }),
			},
			{
				key: 'interpretation',
				label: showPatternInterpretation ? '释义显示' : '释义隐藏',
				icon: 'quickNote',
				active: showPatternInterpretation,
				onClick: ()=>{
					const next = !showPatternInterpretation;
					this.setState({ showPatternInterpretation: next });
					savePatternInterpretationPreference(next);
				},
			},
			{
				key: 'plot',
				label: '重新起盘',
				icon: 'qimen',
				active: false,
				disabled: this.state.loading,
				onClick: this.clickPlot,
			},
			{
				key: 'save',
				label: '保存案例',
				icon: 'bookmark',
				active: false,
				disabled: !this.state.pan,
				onClick: this.clickSaveCase,
			},
		];
		return (
			<div className="horosa-bottom-quick-dock horosa-dunjia-quick-dock">
				<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
				<div className="horosa-bottom-quick-actions horosa-dunjia-quick-actions">
					{items.map((item)=>(
						<button
							type="button"
							key={item.key}
							className={`horosa-bottom-quick-button horosa-dunjia-quick-button${item.active ? ' is-active' : ''}`}
							onClick={item.onClick}
							disabled={item.disabled}
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
			height = '100%';
		}else{
			height = Number(height);
			height = Number.isFinite(height) && height > 0 ? height : 760;
		}
		const pageHeight = this.props.height ? '100%' : height;
		return (
			<div className="horosa-dunjia-page horosa-astro-redesign horosa-dunjia-redesign" style={{ height: pageHeight, minHeight: 0, overflow: 'hidden' }}>
				<div className="horosa-astro-layout horosa-astro-redesign-layout horosa-dunjia-redesign-layout">
					<Spin spinning={this.state.loading}>
						<div className="horosa-astro-redesign-grid horosa-dunjia-redesign-grid">
							<div className="horosa-astro-context-panel horosa-astro-input-panel horosa-dunjia-input-panel">
								{this.renderInputPanel()}
							</div>
							<div className="horosa-chart-stage horosa-chart-stage-redesign horosa-dunjia-chart-panel xq-chart-renderer xq-chart-renderer-qimen">
								<div ref={this.captureLeftBoardHost} className="horosa-dunjia-board-host">
									{this.renderBoard()}
								</div>
							</div>
							<div className="horosa-inspector-panel horosa-astro-content-panel horosa-dunjia-info-panel">
								<div className="horosa-side-panel-heading horosa-dunjia-info-heading">
									<div>
										<div className="horosa-side-panel-title">遁甲信息</div>
										<div className="horosa-side-panel-subtitle">概览、神煞与八宫详解</div>
									</div>
								</div>
								{this.renderRight()}
							</div>
						</div>
					</Spin>
					{this.renderQuickDock()}
				</div>
			</div>
		);
	}
}

export default DunJiaMain;
