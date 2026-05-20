import { Component } from 'react';
import { Row, Col } from 'antd';
import { XQButton as Button, XQModal as Modal, XQTabs as Tabs } from '../xq-ui';
import XQIcon from '../xq-icons';
import * as Constants from '../../utils/constants';
import request from '../../utils/request';
import {randomStr,} from '../../utils/helper';
import ZiWeiInput from './ZiWeiInput';
import ZiWeiChart from './ZiWeiChart';
import ZWRuleMain from '../ruleziwei/ZWRuleMain';
import TipsBoard from '../comp/TipsBoard';
import * as ZiWeiHelper from './ZiWeiHelper';
import * as ZWText from '../../constants/ZWText';
import DateTime from '../comp/DateTime';
import { saveModuleAISnapshot, } from '../../utils/moduleAiSnapshot';

const TabPane = Tabs.TabPane;

function normalizeGan(value){
	if(!value){
		return '';
	}
	return `${value}`.trim().charAt(0);
}

function pickYearGan(chart){
	if(!chart){
		return '';
	}
	if(chart.yearGan){
		return normalizeGan(chart.yearGan);
	}
	if(chart.nongli && chart.nongli.yearGanZi){
		return normalizeGan(chart.nongli.yearGanZi);
	}
	if(chart.nongli && chart.nongli.year){
		return normalizeGan(chart.nongli.year);
	}
	return '';
}

function collectHouseStars(house){
	const groups = [
		'starsMain',
		'starsAssist',
		'starsEvil',
		'starsOthersGood',
		'starsOthersBad',
		'starsSmall',
		'stars',
	];
	const out = [];
	const seen = new Set();
	groups.forEach((key)=>{
		const arr = house && house[key] ? house[key] : [];
		arr.forEach((item)=>{
			let name = '';
			if(typeof item === 'string'){
				name = item;
			}else{
				name = item && (item.name || item.id) ? (item.name || item.id) : '';
			}
			name = `${name || ''}`.trim();
			if(!name || seen.has(name)){
				return;
			}
			seen.add(name);
			out.push(name);
		});
	});
	return out;
}

function formatStarSiHua(starName, yearGan, lifeGan){
	const tags = [];
	if(yearGan){
		const yearHua = ZiWeiHelper.getSiHua(starName, yearGan);
		if(yearHua){
			tags.push(`生年${yearHua}`);
		}
	}
	if(lifeGan){
		const lifeHua = ZiWeiHelper.getSiHua(starName, lifeGan);
		if(lifeHua){
			tags.push(`命宫${lifeHua}`);
		}
	}
	if(tags.length === 0){
		return starName;
	}
	return `${starName}（${tags.join('，')}）`;
}

function getLifeHouse(chart, houses){
	if(!chart || !houses || houses.length === 0){
		return null;
	}
	if(chart.lifeHouseIndex !== undefined && chart.lifeHouseIndex !== null){
		const idx = Number(chart.lifeHouseIndex);
		if(!Number.isNaN(idx) && houses[idx]){
			return houses[idx];
		}
	}
	return houses.find((house)=>`${house.name || ''}`.includes('命')) || null;
}

function buildZiWeiSnapshotText(params, result){
	const chart = result && result.chart ? result.chart : {};
	const houses = chart.houses || [];
	const yearGan = pickYearGan(chart);
	const lifeHouse = getLifeHouse(chart, houses);
	const lifeGan = lifeHouse && lifeHouse.ganzi ? normalizeGan(lifeHouse.ganzi) : '';
	const lines = [];

	lines.push('[起盘信息]');
	lines.push(`日期：${params.date} ${params.time}`);
	lines.push(`时区：${params.zone}`);
	lines.push(`经纬度：${params.lon} ${params.lat}`);
	lines.push(`性别：${params.gender}`);
	lines.push(`时间算法：${params.timeAlg === 1 ? '直接时间' : '真太阳时'}`);
	if(yearGan){
		lines.push(`生年天干：${yearGan}`);
	}
	if(lifeHouse && lifeHouse.name){
		lines.push(`命宫：${lifeHouse.name}${lifeHouse.ganzi ? `（${lifeHouse.ganzi}）` : ''}`);
	}
	if(lifeGan){
		lines.push(`命宫天干：${lifeGan}`);
	}

	lines.push('');
	lines.push('[宫位总览]');
	houses.forEach((house, idx)=>{
		const name = house.name || house.id || `宫位${idx + 1}`;
		const ganzi = house.ganzi || '';
		const direction = house.direction && house.direction.length === 2 ? `${house.direction[0]}~${house.direction[1]}` : '';
		const stars = collectHouseStars(house);
		lines.push(`${name}：大限=${direction || '无'}，干支=${ganzi || '无'}`);
		if(stars.length > 0){
			lines.push(`星曜：${stars.map((starName)=>formatStarSiHua(starName, yearGan, lifeGan)).join('、')}`);
		}else{
			lines.push('星曜：无');
		}
		lines.push('');
	});
	return lines.join('\n');
}

function getFieldValue(fields, key, fallback = ''){
	const field = fields && fields[key] ? fields[key] : null;
	if(!field || field.value === undefined || field.value === null || field.value === ''){
		return fallback;
	}
	return field.value;
}

function buildZiWeiInfoData(chart, fields){
	if(!chart || !chart.nongli){
		return { rows: [], bazi: [], directions: [] };
	}
	const nongli = chart.nongli || {};
	const timeAlg = chart.timeAlg !== undefined && chart.timeAlg !== null ? chart.timeAlg : getFieldValue(fields, 'timeAlg', 0);
	const birthPrefix = timeAlg === 1 ? '直接时间' : '真太阳时';
	const leap = nongli.leap ? '闰' : '';
	const ju = `${ZWText.ZWMsg[chart.yearPolar] || ''}${ZWText.ZWMsg[chart.gender] || ''} ${chart.wuxingJuText || ''}`.trim();
	const rows = [
		['姓名', getFieldValue(fields, 'name', '匿名')],
		['命主', chart.lifeMaster || '—'],
		['身主', chart.bodyMaster || '—'],
		['子斗', chart.zidou || '—'],
		['斗君', chart.doujun || '—'],
		['命局', ju || '—'],
		[birthPrefix, nongli.birth || '—'],
		['农历', `${nongli.year || ''}年 ${leap}${nongli.month || ''}${nongli.day || ''} ${nongli.time ? nongli.time.charAt(1) : ''}时`.trim()],
		['时区', chart.zone || getFieldValue(fields, 'zone', '—')],
		['经纬度', `${chart.lon || getFieldValue(fields, 'lon', '—')}，${chart.lat || getFieldValue(fields, 'lat', '—')}`],
	];
	const bz = chart.bazi && chart.bazi.bazi ? chart.bazi.bazi : {};
	const bazi = [
		{ label: '年', value: bz.year && bz.year.ganzi ? bz.year.ganzi : '—' },
		{ label: '月', value: bz.month && bz.month.ganzi ? bz.month.ganzi : '—' },
		{ label: '日', value: bz.day && bz.day.ganzi ? bz.day.ganzi : '—' },
		{ label: '时', value: bz.time && bz.time.ganzi ? bz.time.ganzi : '—' },
	];
	const directions = chart.bazi && chart.bazi.direct && chart.bazi.direct.direction
		? chart.bazi.direct.direction.map((item, idx)=>{
			const age = item.age + 1;
			return {
				age: age < 10 ? `0${age}` : `${age}`,
				gz: item.mainDirect && item.mainDirect.ganzi ? item.mainDirect.ganzi : '—',
				startYear: item.startYear,
				key: `${idx}-${item.startYear || ''}`,
			};
		})
		: [];
	return { rows, bazi, directions };
}

class ZiWeiMain extends Component{
	constructor(props) {
		super(props);
		this.state = {
			result: null,
			rules: null,
			currentDirectionIndex: null,
			indicator: null,
			cnt: 0,
			tips: null,
			centerInfoVisible: false,
		};

		this.unmounted = false;

		this.requestZiWei = this.requestZiWei.bind(this);
		this.genParams = this.genParams.bind(this);
		this.onFieldsChange = this.onFieldsChange.bind(this);
		this.onChangeDirection = this.onChangeDirection.bind(this);
		this.getNowDirectionIdx = this.getNowDirectionIdx.bind(this);
		this.genDirectionDom = this.genDirectionDom.bind(this);
		this.indicate = this.indicate.bind(this);
		this.onTipClick = this.onTipClick.bind(this);
		this.openCenterInfo = this.openCenterInfo.bind(this);
		this.closeCenterInfo = this.closeCenterInfo.bind(this);
		this.openDrawer = this.openDrawer.bind(this);
		this.navigateFeature = this.navigateFeature.bind(this);
		this.navigateDirectionTool = this.navigateDirectionTool.bind(this);
		this.renderBottomQuickDock = this.renderBottomQuickDock.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (fields)=>{
				if(this.unmounted){
					return;
				}
				this.requestZiWei(fields);
			};
		}
	}

	onFieldsChange(field){
		if(this.props.dispatch && this.props.fields){
			const patch = {
				...field,
			};
			const confirmed = !!patch.__confirmed;
			if(Object.prototype.hasOwnProperty.call(patch, '__confirmed')){
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
			if(confirmed || !Object.prototype.hasOwnProperty.call(field || {}, '__confirmed')){
				this.requestZiWei(flds.fields);
			}
		}
	}

	onChangeDirection(value){
		let ind = this.state.indicator;
		let cnt = this.state.cnt;
		this.setState({
			currentDirectionIndex: value,
			indicator: ind,
			cnt: cnt+1,
		});
	}

	genParams(fields){
		let flds = fields ? fields : this.props.fields;
		const timeAlg = (flds.timeAlg && flds.timeAlg.value !== undefined && flds.timeAlg.value !== null)
			? flds.timeAlg.value
			: 0;
		const params = {
			date: flds.date.value.format('YYYY-MM-DD'),
			time: flds.time.value.format('HH:mm:ss'),
			zone: flds.zone.value,
			lon: flds.lon.value,
			lat: flds.lat.value,
			gpsLat: flds.gpsLat.value,
			gpsLon: flds.gpsLon.value,
			gender: flds.gender.value,
			timeAlg: timeAlg === 1 ? 1 : 0,
			after23NewDay: 0,
		}
		return params;
	}

	async requestZiWei(fields){
		if(fields === undefined || fields === null){
			return;
		}
		const params = this.genParams(fields);

		const data = await request(`${Constants.ServerRoot}/ziwei/birth`, {
			body: JSON.stringify(params),
		});
		const result = data[Constants.ResultKey]

		const rules = await request(`${Constants.ServerRoot}/ziwei/rules`, {
			body: JSON.stringify({}),
		});

		let currentIdx = this.getNowDirectionIdx(result.chart);

		const st = {
			result: result,
			rules: rules[Constants.ResultKey],
			currentDirectionIndex: currentIdx,
		};


		this.setState(st);
		saveModuleAISnapshot('ziwei', buildZiWeiSnapshotText(params, result), {
			date: params.date,
			time: params.time,
			zone: params.zone,
			lon: params.lon,
			lat: params.lat,
		});
	}

	getNowDirectionIdx(chartobj){
		if(chartobj.birth === undefined || chartobj.birth === null){
			return null;
		}
		let now = new DateTime();
		let y = now.format('YYYY');
		let year = parseInt(y);
		let birth = parseInt(chartobj.birth.substr(0,4));
		let age = year - birth + 1;
		for(let i = 0; i<12; i++){
			let house = chartobj.houses[i];
			if(house.direction[0]<= age && age<=house.direction[1]){
				return i;
			}
		}
		return null;
	}

	genDirectionDom(chart){
		if(chart.houses === undefined || chart.houses === null){
			return null;
		}
		let startidx = chart.lifeHouseIndex;

		let dom = [];
		for(let i=0; i<12; i++){
			let idx = 0;
			if(ZiWeiHelper.isDirCloseWise(chart)){
				idx = (startidx + i) % 12;
			}else{
				idx = (startidx - i + 12) % 12;
			}
			let house = chart.houses[idx];
			let txt1 = house.direction[0] + '~' + house.direction[1];
			let txt2 = house.ganzi + '限';
			let lbl = (
				<Row>
					<Col span={24} style={{textAlign: 'center'}}>{txt1}</Col>
					<Col span={24} style={{textAlign: 'center'}}>{txt2}</Col>
				</Row>
			);
			let btntype = null;
			if(this.state.currentDirectionIndex !== null && this.state.currentDirectionIndex === idx){
				btntype = 'primary';
			}
			let rad = (
				<Col span={8} key={randomStr(8)}>
					<Button 
						className="horosa-ziwei-direction-button"
						type={btntype}
						onClick={()=>{this.onChangeDirection(idx);}} 
						style={{width: '100%', height: 50}}
					>
						{lbl}
					</Button>
				</Col>
			);
			dom.push(rad);
		}
		return dom;
	}

	indicate(zwIndicator){
		this.setState({
			indicator: zwIndicator,
		});
	}

	onTipClick(tipobj){
		this.setState({
			tips: tipobj,
		});
	}

	openCenterInfo(){
		this.setState({
			centerInfoVisible: true,
		});
	}

	closeCenterInfo(){
		this.setState({
			centerInfoVisible: false,
		});
	}

	openDrawer(key){
		if(this.props.dispatch){
			this.props.dispatch({
				type: 'astro/openDrawer',
				payload: {
					key,
				},
			});
		}
	}

	navigateFeature(key){
		if(this.props.onNavigate){
			this.props.onNavigate(key);
			return;
		}
		if(this.props.dispatch){
			this.props.dispatch({
				type: 'astro/save',
				payload: {
					currentTab: key,
				},
			});
		}
	}

	navigateDirectionTool(subTab){
		if(this.props.dispatch){
			this.props.dispatch({
				type: 'astro/save',
				payload: {
					currentTab: 'direction',
					currentSubTab: subTab,
				},
			});
			return;
		}
		this.navigateFeature('direction');
	}

	renderBottomQuickDock(){
		const actions = [
			{ label: '主限', icon: 'quickPrimary', onClick: ()=>this.navigateDirectionTool('primarydirect') },
			{ label: '法达', icon: 'quickFirdaria', onClick: ()=>this.navigateDirectionTool('firdaria') },
			{ label: '小限', icon: 'quickProfection', onClick: ()=>this.navigateDirectionTool('profection') },
			{ label: '返照', icon: 'quickReturn', onClick: ()=>this.navigateDirectionTool('solarreturn') },
			{ label: '合盘', icon: 'quickComposite', onClick: ()=>this.navigateFeature('relativechart') },
			{ label: '星运', icon: 'quickTransit', onClick: ()=>this.navigateFeature('direction') },
			{ label: '笔记', icon: 'quickNote', onClick: ()=>this.openDrawer('memo') },
			{ label: 'AI助手', icon: 'quickAi', onClick: ()=>this.navigateFeature('aianalysis') },
		];
		return (
			<div className="horosa-bottom-quick-dock horosa-ziwei-quick-dock">
				<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
				<div className="horosa-bottom-quick-actions horosa-ziwei-quick-actions">
					{actions.map((item)=>(
						<button type="button" key={item.label} className="horosa-bottom-quick-button" onClick={item.onClick}>
							<span className="horosa-bottom-quick-icon"><XQIcon name={item.icon} /></span>
							<span>{item.label}</span>
						</button>
					))}
				</div>
			</div>
		);
	}

	renderZiWeiInfoPanel(infoData){
		if(!infoData || infoData.rows.length === 0){
			return <div className="horosa-empty-hint">起盘后显示命盘信息</div>;
		}
		return (
			<div className="horosa-ziwei-meta-scroll horosa-astro-content-scroll">
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">基本信息</div>
					{infoData.rows.map((row)=>(
						<div className="horosa-info-row" key={row[0]}>
							<span>{row[0]}</span>
							<strong>{row[1]}</strong>
						</div>
					))}
				</div>
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">四柱</div>
					<div className="horosa-ziwei-bazi-grid">
						{infoData.bazi.map((item)=>(
							<div className="horosa-ziwei-bazi-cell" key={item.label}>
								<span>{item.label}</span>
								<strong>{item.value}</strong>
							</div>
						))}
					</div>
				</div>
				<div className="horosa-info-card">
					<div className="horosa-info-card-title">大限</div>
					<div className="horosa-ziwei-direction-mini-grid">
						{infoData.directions.map((item)=>(
							<div className="horosa-ziwei-direction-mini" key={item.key}>
								<span>{item.age}</span>
								<strong>{item.gz}</strong>
								<em>{item.startYear || '—'}</em>
							</div>
						))}
					</div>
				</div>
			</div>
		);
	}

	componentDidMount(){
		this.unmounted = false;
		if(this.props.fields){
			this.requestZiWei(this.props.fields);
		}
	}

	componentWillUnmount(){
		this.unmounted = true;
	}

	render(){
		let height = this.props.height ? this.props.height : 760;
		if(height === '100%'){
			height = 'calc(100% - 70px)'
		}else{
			height = height - 40
		}

		let chart = this.state.result ? this.state.result.chart : {};
		let dirIndex = this.state.currentDirectionIndex;
		let doms = this.genDirectionDom(chart);
		let infoData = buildZiWeiInfoData(chart, this.props.fields);

		let tipheight = 270;
		let docwid = document.documentElement.clientWidth;
		if(docwid <= 1440){
			tipheight = 120;
		}

		return (
			<div className="horosa-ziwei-page horosa-astro-redesign horosa-ziwei-redesign">
				<div className="horosa-astro-layout horosa-astro-redesign-layout horosa-ziwei-redesign-layout">
					<div className="horosa-astro-redesign-grid horosa-ziwei-redesign-grid">
						<div className="horosa-astro-context-panel horosa-astro-input-panel horosa-ziwei-input-panel">
							<ZiWeiInput
								fields={this.props.fields}
								onFieldsChange={this.onFieldsChange}
							/>
						</div>
						<div className="horosa-chart-stage horosa-chart-stage-redesign horosa-ziwei-chart-panel xq-chart-renderer xq-chart-renderer-ziwei">
							<div className="horosa-ziwei-chart-viewport">
								<ZiWeiChart
									value={chart}
									height="100%"
									fields={this.props.fields}
									dirIndex={dirIndex}
									indicate={this.indicate}
									rules={this.state.rules}
									onTipClick={this.onTipClick}
									onCenterInfoClick={this.openCenterInfo}
								/>
							</div>
						</div>
						<div className="horosa-inspector-panel horosa-astro-content-panel horosa-ziwei-info-panel">
							<Tabs defaultActiveKey="info" tabPosition='top' className="horosa-content-tabs horosa-ziwei-tabs">
								<TabPane tab="命盘" key="info">
									{this.renderZiWeiInfoPanel(infoData)}
								</TabPane>
								<TabPane tab="行运" key="1">
									<div className="horosa-ziwei-direction-list">
										<Row>
											{doms}
										</Row>
									</div>
								</TabPane>
								<TabPane tab="资料参考" key="2">
									<ZWRuleMain height={height} rules={this.state.rules} />
								</TabPane>
								<TabPane tab="提示" key="3">
									<TipsBoard
										height={tipheight}
										value={this.state.tips}
										/>
									</TabPane>
								</Tabs>
							</div>
						</div>
						{this.renderBottomQuickDock()}
						<Modal
							open={this.state.centerInfoVisible}
							title="命盘信息"
							footer={null}
							onCancel={this.closeCenterInfo}
							width={640}
							className="horosa-ziwei-center-info-modal"
						>
							{this.renderZiWeiInfoPanel(infoData)}
						</Modal>
					</div>
				</div>
		);
	}
}

export default ZiWeiMain;
