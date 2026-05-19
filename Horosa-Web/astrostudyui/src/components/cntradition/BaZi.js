import { Component } from 'react';
import { XQTabs as Tabs } from '../xq-ui';
import CnTraditionInput from './CnTraditionInput';
import * as Constants from '../../utils/constants';
import request from '../../utils/request';
import PaiBaZi, { BAZI_CHART_STYLE_KEY } from './PaiBaZi';
import Gods from './Gods';
import GanHeCong from './GanHeCong';
import ZiHeCong from './ZiHeCong';
import BaZiZhangSheng from './BaZiZhangSheng';
import FourZhuGuaDesc from './FourZhuGuaDesc';
import BaZiLuckFlowPanel from './BaZiLuckFlowPanel';
import BaZiAppInfoPanel from './BaZiAppInfoPanel';
import { saveModuleAISnapshot, } from '../../utils/moduleAiSnapshot';
import { buildLocalBaziResult } from '../../utils/baziLunarLocal';

const TabPane = Tabs.TabPane;

const BaZiOptKey = 'baziopt';
const BAZI_CORE_ENDPOINT = '/bazi/birth';
const BAZI_DIRECT_ENDPOINT = '/bazi/direct';

function gzText(zhu){
	if(!zhu){
		return '';
	}
	const gan = zhu.stem && zhu.stem.cell ? zhu.stem.cell : '';
	const zhi = zhu.branch && zhu.branch.cell ? zhu.branch.cell : '';
	const relGan = zhu.stem && zhu.stem.relative ? `，干十神:${zhu.stem.relative}` : '';
	const relZhi = zhu.branch && zhu.branch.relative ? `，支十神:${zhu.branch.relative}` : '';
	return `${gan}${zhi}${relGan}${relZhi}`;
}

function buildBaziSnapshotText(params, result){
	const bazi = result && result.bazi ? result.bazi : {};
	const four = bazi.fourColumns || {};
	const lines = [];
	const labelMap = {
		gender: {
			'-1': '未知',
			'0': '女',
			'1': '男',
		},
		timeAlg: {
			'0': '真太阳时',
			'1': '直接时间',
			'2': '春分定卯时',
		},
		adjustJieqi: {
			'0': '不调整节气',
			'1': '节气按纬度调整',
		},
	};
	const getGz = (item)=>{
		if(!item){
			return '';
		}
		return item.ganzhi || item.ganzi || item.ganZhi || '';
	};
	const formatLabel = (dictName, value)=>{
		const dict = labelMap[dictName] || {};
		const key = `${value}`;
		if(dict[key] !== undefined){
			return dict[key];
		}
		return value;
	};
	const getNongliLine = (nongli)=>{
		if(!nongli){
			return '';
		}
		const leap = nongli.leap ? '闰' : '';
		return `${nongli.year || ''}年${leap}${nongli.month || ''}${nongli.day || ''}`;
	};
	const appendIf = (label, value)=>{
		if(value === undefined || value === null || value === ''){
			return;
		}
		lines.push(`${label}：${value}`);
	};
	const collectGodNames = (node)=>{
		if(!node){
			return [];
		}
		const all = [];
		if(Array.isArray(node.goodGods)){
			all.push(...node.goodGods);
		}
		if(Array.isArray(node.neutralGods)){
			all.push(...node.neutralGods);
		}
		if(Array.isArray(node.badGods)){
			all.push(...node.badGods);
		}
		return all.filter(Boolean);
	};
	const gzGodText = (zhu)=>{
		if(!zhu){
			return '无';
		}
		const whole = collectGodNames(zhu);
		const stem = collectGodNames(zhu.stem);
		const branch = collectGodNames(zhu.branch);
		const taiSui = zhu.branch && Array.isArray(zhu.branch.taisuiGods) ? zhu.branch.taisuiGods.filter(Boolean) : [];
		const wholeTxt = whole.length ? whole.join('、') : '无';
		const stemTxt = stem.length ? stem.join('、') : '无';
		const branchTxt = branch.length ? branch.join('、') : '无';
		const taiSuiTxt = taiSui.length ? taiSui.join('、') : '无';
		return `整柱=${wholeTxt}；天干=${stemTxt}；地支=${branchTxt}；太岁=${taiSuiTxt}`;
	};
	let baziGender = bazi && bazi.gender === 'Female' ? '坤造' : (bazi && bazi.gender === 'Male' ? '乾造' : '');
	if(!baziGender){
		if(Number(params.gender) === 0){
			baziGender = '坤造';
		}else if(Number(params.gender) === 1){
			baziGender = '乾造';
		}
	}

	lines.push('[起盘信息]');
	appendIf('日期', `${params.date} ${params.time}`);
	appendIf('时区', params.zone);
	appendIf('经纬度', `${params.lon} ${params.lat}`);
	appendIf('性别', formatLabel('gender', params.gender));
	appendIf('时间算法', formatLabel('timeAlg', params.timeAlg));
	appendIf('节气修正', formatLabel('adjustJieqi', params.adjustJieqi));
	appendIf('命造', baziGender);
	const nongli = bazi && bazi.nongli ? bazi.nongli : {};
	const nltxt = getNongliLine(nongli);
	const realtm = nongli.birth || `${params.date} ${params.time}`;
	lines.push(`农历：${nltxt || '未知'} 真太阳时：${realtm || '未知'}`);
	const jiedelta = nongli.jiedelta || '';
	const chef = nongli.chef || '';
	const tiaohou = Array.isArray(bazi.tiaohou) ? bazi.tiaohou.join('，') : '';
	const fixedLine = [jiedelta, chef].filter(Boolean).join('，');
	const fixedBase = (fixedLine || '立春后信息：无').replace(/[；，\s]+$/g, '');
	lines.push(`${fixedBase}； 调候：${tiaohou || '无'}`);

	lines.push('');
	lines.push('[四柱与三元]');
	lines.push(`年柱：${gzText(four.year)}`);
	lines.push(`月柱：${gzText(four.month)}`);
	lines.push(`日柱：${gzText(four.day)}`);
	lines.push(`时柱：${gzText(four.time)}`);
	lines.push(`胎元：${gzText(four.tai)}`);
	lines.push(`命宫：${gzText(four.ming)}`);
	lines.push(`身宫：${gzText(four.shen)}`);

	lines.push('');
	lines.push('[神煞（四柱与三元）]');
	lines.push(`年柱：${gzGodText(four.year)}`);
	lines.push(`月柱：${gzGodText(four.month)}`);
	lines.push(`日柱：${gzGodText(four.day)}`);
	lines.push(`时柱：${gzGodText(four.time)}`);
	lines.push(`胎元：${gzGodText(four.tai)}`);
	lines.push(`命宫：${gzGodText(four.ming)}`);
	lines.push(`身宫：${gzGodText(four.shen)}`);

	if(bazi.mainDirection && bazi.mainDirection.length){
		lines.push('');
		lines.push('[大运]');
		bazi.mainDirection.forEach((item, idx)=>{
			const y = item.year !== undefined ? `${item.year}` : '';
			const gz = getGz(item);
			lines.push(`第${idx + 1}步：${y} ${gz}`);
		});
	}

	if(bazi.direction && bazi.direction.length){
		lines.push('');
		lines.push('[流年行运概略]');
		bazi.direction.forEach((block, idx)=>{
			const startYear = block && block.startYear !== undefined ? `${block.startYear}` : '';
			const startAge = block && block.age !== undefined ? `${block.age}` : '';
			const dayunGz = getGz(block ? block.mainDirect : null);
			const startYearNum = block && block.startYear !== undefined ? Number(block.startYear) : null;
			const yearGzs = (block && block.subDirect && block.subDirect.length ? block.subDirect : [])
				.map((sub, subIdx)=>{
					const gz = getGz(sub);
					if(!gz){
						return '';
					}
					const yearNum = Number.isFinite(startYearNum) ? startYearNum + subIdx : null;
					if(Number.isFinite(yearNum)){
						return `${yearNum}-${gz}`;
					}
					return gz;
				})
				.filter(Boolean);
			lines.push(`板块${idx + 1}：起始年${startYear}，起始年龄${startAge}岁，大运${dayunGz}`);
			if(yearGzs.length){
				lines.push(`流年：${yearGzs.join(' ')}`);
			}
		});
	}
	return lines.join('\n');
}

const BAZI_CACHE_MAX = 96;
const baziMem = new Map();
const baziInflight = new Map();
const baziDirectMem = new Map();
const baziDirectInflight = new Map();

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

function pushCache(map, key, val, max = BAZI_CACHE_MAX){
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

function normalizeBaziGender(gender){
	if(gender === 'Male' || gender === 'Female'){
		return gender;
	}
	if(gender === false || `${gender}` === '0'){
		return 'Female';
	}
	if(gender === true || `${gender}` === '1'){
		return 'Male';
	}
	return '';
}

function normalizeBaziResult(result, params){
	if(!result){
		return result;
	}
	const next = {
		...result,
	};
	const bazi = {
		...(next.bazi || {}),
	};
	if(!bazi.gender){
		bazi.gender = next.gender || normalizeBaziGender(params ? params.gender : null);
	}
	next.bazi = bazi;
	next.coreOnly = !Array.isArray(bazi.direction) || bazi.direction.length === 0;
	return next;
}

function buildBaziKey(params){
	try{
		return JSON.stringify(params || {});
	}catch(e){
		return '';
	}
}

async function fetchBaziCached(params, options){
	const opt = options || {};
	const disableCache = opt.cache === false;
	const key = disableCache ? '' : buildBaziKey(params);
	if(key && baziMem.has(key)){
		return clonePlain(baziMem.get(key));
	}
	if(key && baziInflight.has(key)){
		const inflight = await baziInflight.get(key);
		return clonePlain(inflight);
	}
	try{
		const localResult = buildLocalBaziResult(params);
		if(key && localResult){
			pushCache(baziMem, key, clonePlain(localResult));
		}
		return clonePlain(localResult);
	}catch(e){
		// Fall through to the legacy service when the local Lunar calculator cannot parse old edge cases.
	}
	const req = request(`${Constants.ServerRoot}${BAZI_CORE_ENDPOINT}`, {
		body: JSON.stringify(params),
		silent: opt.silent !== false,
	}).then((data)=>{
		const result = data && data[Constants.ResultKey] ? data[Constants.ResultKey] : null;
		if(key && result){
			pushCache(baziMem, key, clonePlain(result));
		}
		return result;
	}).finally(()=>{
		if(key){
			baziInflight.delete(key);
		}
	});
	if(key){
		baziInflight.set(key, req);
	}
	const result = await req;
	return clonePlain(result);
}

async function fetchBaziDirectCached(params, options){
	const opt = options || {};
	const disableCache = opt.cache === false;
	const key = disableCache ? '' : buildBaziKey(params);
	if(key && baziDirectMem.has(key)){
		return clonePlain(baziDirectMem.get(key));
	}
	if(key && baziDirectInflight.has(key)){
		const inflight = await baziDirectInflight.get(key);
		return clonePlain(inflight);
	}
	try{
		const localResult = buildLocalBaziResult(params);
		if(key && localResult){
			pushCache(baziDirectMem, key, clonePlain(localResult));
		}
		return clonePlain(localResult);
	}catch(e){
		// Fall through to the legacy service when the local Lunar calculator cannot parse old edge cases.
	}
	const req = request(`${Constants.ServerRoot}${BAZI_DIRECT_ENDPOINT}`, {
		body: JSON.stringify(params),
		silent: opt.silent !== false,
	}).then((data)=>{
		const result = data && data[Constants.ResultKey] ? data[Constants.ResultKey] : null;
		if(key && result){
			pushCache(baziDirectMem, key, clonePlain(result));
		}
		return result;
	}).finally(()=>{
		if(key){
			baziDirectInflight.delete(key);
		}
	});
	if(key){
		baziDirectInflight.set(key, req);
	}
	const result = await req;
	return clonePlain(result);
}

class BaZi extends Component{
	constructor(props) {
		super(props);

		let bzopt = localStorage.getItem(BaZiOptKey);
		if(bzopt){
			bzopt = JSON.parse(bzopt);
		}else{
			bzopt = {
				onlyZiGanShen: true,
			};
		}	

		this.state = {
			result: null,
			baziOpt: bzopt,
			chartStyle: localStorage.getItem(BAZI_CHART_STYLE_KEY) === 'fine' ? 'fine' : 'simple',
			currentBaziKey: '',
			directResult: null,
			directKey: '',
			directLoading: false,
			directError: null,
		};

		this.unmounted = false;
		this.baziReqSeq = 0;
		this.prefetchTimer = null;

		this.requestBazi = this.requestBazi.bind(this);
		this.requestBaziDirect = this.requestBaziDirect.bind(this);
		this.prefetchBazi = this.prefetchBazi.bind(this);
		this.genParams = this.genParams.bind(this);
		this.onFieldsChange = this.onFieldsChange.bind(this);
		this.onBaziOptChange = this.onBaziOptChange.bind(this);
		this.onInfoTabChange = this.onInfoTabChange.bind(this);
		this.changeBaziChartStyle = this.changeBaziChartStyle.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (fields)=>{
				if(this.unmounted){
					return;
				}
				this.requestBazi(fields);
			};
		}

	}

	onFieldsChange(field){
		if(this.props.dispatch && this.props.fields){
			const patch = {
				...field,
			};
			const hasConfirmedFlag = Object.prototype.hasOwnProperty.call(patch, '__confirmed');
			const confirmed = hasConfirmedFlag ? !!patch.__confirmed : true;
			if(hasConfirmedFlag){
				delete patch.__confirmed;
			}
			let flds = {
				fields: {
					...this.props.fields,
					...patch,
				}
			};
			this.props.dispatch({
				type: 'astro/save',
				payload: flds
			});
			if(!confirmed){
				if(this.prefetchTimer){
					clearTimeout(this.prefetchTimer);
				}
				this.prefetchTimer = setTimeout(()=>{
					this.prefetchTimer = null;
					if(this.unmounted){
						return;
					}
					this.prefetchBazi(flds.fields).catch(()=>{
						return null;
					});
				}, 240);
				return;
			}
			if(this.prefetchTimer){
				clearTimeout(this.prefetchTimer);
				this.prefetchTimer = null;
			}
			this.requestBazi(flds.fields, {
				silent: true,
			});
		}
	}
	
	onBaziOptChange(opt){
		this.setState({
			baziOpt: opt,
		}, ()=>{
			localStorage.setItem(BaZiOptKey, JSON.stringify(opt));
		});
	}

	changeBaziChartStyle(chartStyle){
		this.setState({
			chartStyle,
		}, ()=>{
			localStorage.setItem(BAZI_CHART_STYLE_KEY, chartStyle);
		});
	}

	genParams(fields){
		let flds = fields ? fields : this.props.fields;
		const params = {
			date: flds.date.value.format('YYYY-MM-DD'),
			time: flds.time.value.format('HH:mm:ss'),
			zone: flds.zone.value,
			lon: flds.lon.value,
			lat: flds.lat.value,
			gpsLat: flds.gpsLat.value,
			gpsLon: flds.gpsLon.value,
			gender: flds.gender.value,
			timeAlg: flds.timeAlg.value,
			phaseType: flds.phaseType.value,
			godKeyPos: flds.godKeyPos.value,
			after23NewDay: flds.after23NewDay.value,
			adjustJieqi: flds.adjustJieqi.value,
		}
		return params;
	}

	async prefetchBazi(fields){
		if(fields === undefined || fields === null){
			return;
		}
		const params = this.genParams(fields);
		await fetchBaziCached(params, {
			silent: true,
		});
	}

	async requestBazi(fields, options){
		if(fields === undefined || fields === null){
			return;
		}
		const params = this.genParams(fields);
		const currentBaziKey = buildBaziKey(params);
		const opt = options || {};
		const seq = ++this.baziReqSeq;
		const rawResult = await fetchBaziCached(params, {
			silent: opt.silent !== false,
		});
		const result = normalizeBaziResult(rawResult, params);
		if(!result || this.unmounted || seq !== this.baziReqSeq){
			return;
		}

		const st = {
			result: result,
			currentBaziKey,
			directResult: result && result.local ? result : (this.state.currentBaziKey === currentBaziKey ? this.state.directResult : null),
			directKey: result && result.local ? currentBaziKey : (this.state.currentBaziKey === currentBaziKey ? this.state.directKey : ''),
			directLoading: this.state.currentBaziKey === currentBaziKey ? this.state.directLoading : false,
			directError: this.state.currentBaziKey === currentBaziKey ? this.state.directError : null,
		};

		this.setState(st);
		saveModuleAISnapshot('bazi', buildBaziSnapshotText(params, result), {
			date: params.date,
			time: params.time,
			zone: params.zone,
			lon: params.lon,
			lat: params.lat,
		});
	}

	async requestBaziDirect(){
		if(!this.props.fields){
			return;
		}
		const params = this.genParams(this.props.fields);
		const key = buildBaziKey(params);
		if(this.state.directResult && this.state.directKey === key){
			return;
		}
		if(this.state.directLoading && this.state.directKey === key){
			return;
		}
		this.setState({
			directLoading: true,
			directError: null,
			directKey: key,
		});
		try{
			const rawResult = await fetchBaziDirectCached(params, {
				silent: true,
			});
			const result = normalizeBaziResult(rawResult, params);
			if(this.unmounted || buildBaziKey(this.genParams(this.props.fields)) !== key){
				return;
			}
			this.setState({
				directResult: result,
				directKey: key,
				directLoading: false,
				directError: null,
			});
		}catch(e){
			if(this.unmounted){
				return;
			}
			this.setState({
				directLoading: false,
				directError: '行运数据加载失败',
			});
		}
	}

	onInfoTabChange(key){
		if(`${key}` === '0'){
			this.requestBaziDirect();
		}
	}


	componentDidMount(){
		this.unmounted = false;
		if(this.props.fields){
			this.requestBazi(this.props.fields, {
				silent: true,
			});
		}
	}

	componentWillUnmount(){
		this.unmounted = true;
		if(this.prefetchTimer){
			clearTimeout(this.prefetchTimer);
			this.prefetchTimer = null;
		}
	}

	render(){
		let height = this.props.height ? this.props.height : 760;
		if(height === '100%'){
			height = '100%'
		}else{
			height = Math.max(320, height - 8);
		}
		let tabHeight = height - 20;

		let bazi = this.state.result ? this.state.result.bazi : {};
		const directBazi = this.state.directResult && this.state.directResult.bazi ? this.state.directResult.bazi : null;
		const baziParams = this.props.fields ? this.genParams(this.props.fields) : {};
		const isFineChart = this.state.chartStyle === 'fine';
		const chartHeight = typeof height === 'number' ? Math.max(360, Math.round(height * 0.62)) : height;
		const flowHeight = typeof height === 'number' ? Math.max(220, height - chartHeight - 18) : 240;

		return (
			<div className="horosa-bazi-page horosa-astro-redesign horosa-bazi-redesign">
				<div className="horosa-astro-layout horosa-astro-redesign-layout horosa-bazi-redesign-layout">
					<div className="horosa-astro-redesign-grid horosa-bazi-redesign-grid">
						<div className="horosa-astro-context-panel horosa-astro-input-panel horosa-bazi-input-panel">
							<CnTraditionInput
								fields={this.props.fields}
								baziOpt={this.state.baziOpt}
								onFieldsChange={this.onFieldsChange}
								onBaziOptChange={this.onBaziOptChange}
							/>
						</div>
						<div className="horosa-chart-stage horosa-chart-stage-redesign horosa-bazi-chart-panel xq-chart-renderer xq-chart-renderer-bazi">
							<div className={`horosa-bazi-main-stack ${isFineChart ? 'horosa-bazi-main-stack-fine' : ''}`}>
								<div className="horosa-bazi-main-chart-slot">
									<PaiBaZi
										value={bazi}
										height={isFineChart ? 'auto' : chartHeight}
										fields={this.props.fields}
										baziOpt={this.state.baziOpt}
										chartStyle={this.state.chartStyle}
										onChartStyleChange={this.changeBaziChartStyle}
										showStyleSwitch={false}
									/>
								</div>
								<div className="horosa-bazi-main-flow-slot">
									<BaZiLuckFlowPanel
										coreValue={bazi}
										fullValue={directBazi}
										height={flowHeight}
										loading={this.state.directLoading}
										error={this.state.directError}
										jieqiParams={baziParams}
										onLoad={this.requestBaziDirect}
										compact
									/>
								</div>
							</div>
						</div>
						<div className="horosa-inspector-panel horosa-astro-content-panel horosa-bazi-info-panel">
							<BaZiAppInfoPanel value={bazi} fields={this.props.fields} height={tabHeight} />
						</div>
					</div>
				</div>
			</div>
		);
	}

}

export default BaZi;
