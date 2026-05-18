import { Component } from 'react';
import moment from 'moment';
import IndiaChart, { fieldsToParams, requestIndiaChartData } from './IndiaChart';
import DateTime from '../comp/DateTime';
import SpaceTimePanel from '../comp/SpaceTimePanel';
import {convertLatToStr, convertLonToStr} from './AstroHelper';
import * as AstroConst from '../../constants/AstroConst';
import { XQSelect as Select, XQSegmented as Segmented, XQTabs as Tabs } from '../xq-ui';
import XQIcon from '../xq-icons';

const {Option} = Select;
const TabPane = Tabs.TabPane;
const DASHA_YEAR_DAYS = 365.25;
const NAKSHATRA_SIZE = 360 / 27;
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
	return `${Math.max(0, years).toFixed(1)}岁`;
}

function buildVimshottariDasha(chartObj, fields){
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
	const items = [];
	if(!birth.clone){
		return null;
	}
	let start = birth.clone();
	let lordIndex = firstLord.idx;
	for(let i=0; i<10; i++){
		const lord = DASHA_SEQUENCE[lordIndex % DASHA_SEQUENCE.length];
		const years = i === 0 ? firstBalance : lord.years;
		const end = addDashaYears(start, years);
		if(!end || !end.clone){
			break;
		}
		items.push({
			lord,
			years,
			start: start.clone(),
			end: end.clone(),
			startAge: i === 0 ? 0 : items.length ? items[items.length - 1].endAge : 0,
			endAge: items.length ? items[items.length - 1].endAge + years : years,
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
		items,
	};
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
		fields.hsys ? fields.hsys.value : '',
	].join('|');
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
		this.changeIndiaChartStyle = this.changeIndiaChartStyle.bind(this);
		this.requestDashaChart = this.requestDashaChart.bind(this);

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
		if(this.props.onChange){
			let flds = this.props.onChange(values);
			flds.chartnum = {};
			flds.chartnum.value = this.state.currentFractal;
			let hook = this.state.hook[this.state.currentTab];
			if(hook.fun){
				hook.fun(flds);
			}
			this.requestDashaChart(flds);
		}		
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
		this.onFieldsChange({
			hsys: {
				value,
			},
		});
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

	async requestDashaChart(fields){
		const sourceFields = fields || this.props.fields;
		const dashaFieldsKey = buildDashaFieldsKey(sourceFields);
		if(!dashaFieldsKey || dashaFieldsKey === this.state.dashaFieldsKey){
			return;
		}
		let params = fieldsToParams(sourceFields);
		params.chartnum = 1;
		this.setState({
			dashaLoading: true,
			dashaFieldsKey,
		});
		try{
			const dashaChartObj = await requestIndiaChartData(params);
			if(this.state.dashaFieldsKey === dashaFieldsKey){
				this.setState({
					dashaChartObj,
					dashaLoading: false,
				});
			}
		}catch(e){
			if(this.state.dashaFieldsKey === dashaFieldsKey){
				this.setState({
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
		this.requestDashaChart();
	}

	componentDidUpdate(prevProps){
		const oldKey = buildDashaFieldsKey(prevProps.fields);
		const newKey = buildDashaFieldsKey(this.props.fields);
		if(oldKey !== newKey){
			this.requestDashaChart();
		}
	}

	renderDashaPanel(fields){
		const dasha = buildVimshottariDasha(this.state.dashaChartObj, fields);
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
					{dasha.items.map((item, idx)=>(
						<div className={`horosa-india-dasha-item${item.active ? ' is-active' : ''}`} key={`${item.lord.key}_${idx}`}>
							<div className="horosa-india-dasha-item-main">
								<strong>{item.lord.label}</strong>
								<span>{item.lord.en}</span>
							</div>
							<div className="horosa-india-dasha-item-meta">
								<span>{item.start.format('YYYY-MM-DD')} - {item.end.format('YYYY-MM-DD')}</span>
								<em>{formatAge(item.startAge)} - {formatAge(item.endAge)} · {formatDuration(item.years)}</em>
							</div>
						</div>
					))}
				</div>
			</div>
		);
	}

	render(){
		let fields = this.props.fields;
		let height = this.props.height ? this.props.height : 760;
		let chartHeight = height === '100%' ? '100%' : Math.max(520, height - 118);
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
										<label className="horosa-india-select-field">
											<span>印度宫制</span>
											<Select value={fields.hsys.value} onChange={this.changeHsys} size="small">
												{Object.keys(AstroConst.HouseSys).map((key)=>(
													<Option value={parseInt(key, 10)} key={key}>{AstroConst.HouseSys[key]}</Option>
												))}
											</Select>
										</label>
										<label className="horosa-india-select-field">
											<span>当前分盘</span>
											<Select value={this.state.currentTab} onChange={this.changeTab} size="small">
												<Option value="Natal">命盘 D1</Option>
												{splitItems.map((item)=>(
													<Option value={item.key} key={item.key}>{item.fractal}分盘{item.txt ? ` · ${item.txt}` : ''}</Option>
												))}
											</Select>
										</label>
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
							</div>
						</div>
						<div className="horosa-chart-stage horosa-chart-stage-redesign horosa-india-chart-panel">
							<IndiaChart
								key={`${this.state.currentTab}_${indiaChartStyle}`}
								chartOnly
								chartnum={currentHook.fractal}
							onChange={this.onFieldsChange}
								fields={fields}
								height={chartHeight}
								chartDisplay={this.props.chartDisplay}
								indiaChartStyle={indiaChartStyle}
								planetDisplay={this.props.planetDisplay}
								lotsDisplay={this.props.lotsDisplay}
								showPlanetHouseInfo={this.props.showPlanetHouseInfo}
								showAstroMeaning={this.props.showAstroMeaning}
								hook={currentHook}
								dispatch={this.props.dispatch}
							/>
						</div>
						<div className="horosa-inspector-panel horosa-astro-content-panel horosa-india-info-panel">
							<Tabs defaultActiveKey="1" tabPosition="top" className="horosa-content-tabs horosa-india-tabs">
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
								<TabPane tab="起盘信息" key="2">
									<div className="horosa-india-summary">
										<div className="horosa-info-card">
											<div className="horosa-info-card-title">基本参数</div>
											<div className="horosa-info-row"><span>时间</span><strong>{fields.date.value.format('YYYY-MM-DD')} {fields.time.value.format('HH:mm:ss')}</strong></div>
											<div className="horosa-info-row"><span>地点</span><strong>{fields.lon.value} {fields.lat.value}</strong></div>
											<div className="horosa-info-row"><span>时区</span><strong>{fields.zone.value}</strong></div>
											<div className="horosa-info-row"><span>当前分盘</span><strong>D{currentHook.fractal} {currentHook.txt || ''}</strong></div>
										</div>
									</div>
								</TabPane>
								<TabPane tab="大运" key="3">
									{this.renderDashaPanel(fields)}
								</TabPane>
							</Tabs>
						</div>
					</div>
					<div className="horosa-bottom-quick-dock horosa-india-quick-dock">
						<div className="horosa-bottom-quick-title">快捷功能 <XQIcon name="ai" /></div>
						<div className="horosa-bottom-quick-actions horosa-india-quick-placeholders">
							{Array.from({length: 8}).map((_, idx)=>(
								<div className="horosa-bottom-quick-placeholder" key={idx} />
							))}
						</div>
					</div>
				</div>
			</div>
		);
	}
}

export default IndiaChartMain;
