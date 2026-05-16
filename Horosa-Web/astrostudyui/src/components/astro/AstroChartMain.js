import { Component } from 'react';
import { Row, Col, Tabs, Select, Button, Tooltip } from 'antd';
import AstroChart from './AstroChart';
import AstroInfo from './AstroInfo';
import AstroAspect from './AstroAspect';
import AstroPlanet from './AstroPlanet';
import AstroLots from './AstroLots';
import AstroPredictPlanetSign from './AstroPredictPlanetSign';
import PlusMinusTime from './PlusMinusTime';
import DateTime from '../comp/DateTime';
import GeoCoordModal from '../amap/GeoCoordModal';
import { convertLatToStr, convertLonToStr} from './AstroHelper';
import { getHousesOption } from '../comp/CompHelper'
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import { XQButton, XQSegmented, XQToggle } from '../xq-ui';
import XQIcon from '../xq-icons';

const TabPane = Tabs.TabPane;
const Option = Select.Option;

function fieldValue(fields, key, fallback = ''){
	if(!fields || !fields[key]){
		return fallback;
	}
	return fields[key].value !== undefined && fields[key].value !== null ? fields[key].value : fallback;
}

function formatFieldTime(fields){
	const date = fieldValue(fields, 'date', null);
	const time = fieldValue(fields, 'time', null);
	const dateText = date && date.format ? date.format('YYYY-MM-DD') : '';
	const timeText = time && time.format ? time.format('HH:mm:ss') : '';
	return `${dateText}${timeText ? ` ${timeText}` : ''}`.trim();
}

function formatTrueSolarTime(value){
	if(!value){
		return '';
	}
	return `${value}`.replace(' ', '，');
}

class AstroChartMain extends Component{

	constructor(props) {
		super(props);
		this.state = {

		}

        this.tmHook = {
            getValue: null,
        }

		this.changeTime = this.changeTime.bind(this);
		this.changeZodiacal = this.changeZodiacal.bind(this);
		this.changeHsys = this.changeHsys.bind(this);
		this.changeGeo = this.changeGeo.bind(this);
		this.changeSouthChart = this.changeSouthChart.bind(this);
		this.openDrawer = this.openDrawer.bind(this);
		this.newChart = this.newChart.bind(this);
		this.changeChartStyle = this.changeChartStyle.bind(this);
		this.changeIndiaChartStyle = this.changeIndiaChartStyle.bind(this);
		this.toggleChartDisplayOption = this.toggleChartDisplayOption.bind(this);
		this.navigateFeature = this.navigateFeature.bind(this);
		this.navigateDirectionTool = this.navigateDirectionTool.bind(this);

		if(this.props.hook){
			this.props.hook.fun = ()=>{
				return;
			};
		}

	}

	changeTime(tm){
		if(this.props.onChange){
			this.props.onChange({
				tm: tm.time,
				ad: tm.ad,
				zone: tm.time.zone,
				confirmed: tm.confirmed,
			});
		}
	}

	changeZodiacal(val){
		if(this.props.onChange){
			if(this.tmHook.getValue){
				let tm = this.tmHook.getValue().value;
				this.props.onChange({
					zodiacal: val,
					tm: tm,
					ad: tm.ad,
					zone: tm.zone,
				});	
			}else{
				this.props.onChange({
					zodiacal: val,
				});	
			}
	
		}
	}

	changeHsys(val){
		if(this.props.onChange){
			if(this.tmHook.getValue){
				let tm = this.tmHook.getValue().value;
				this.props.onChange({
					hsys: val,
					tm: tm,
					ad: tm.ad,
					zone: tm.zone,
				});	
			}else{
				this.props.onChange({
					hsys: val,
				});	
			}
		}
	}

	changeSouthChart(val){
		if(this.props.fields.lat === undefined || this.props.fields.lat === null){
			return;
		}
		let lat = this.props.fields.lat.value;
		if(lat.toLowerCase().indexOf('n') >= 0){
			return;
		}

		if(this.props.onChange){
			if(this.tmHook.getValue){
				let tm = this.tmHook.getValue().value;
				this.props.onChange({
					southchart: val,
					tm: tm,
					ad: tm.ad,
					zone: tm.zone,
				});		
			}else{
				this.props.onChange({
					southchart: val,
				});	
			}
		}
	}

	changeGeo(rec){
		if(this.props.onChange){
			if(this.tmHook.getValue){
				let tm = this.tmHook.getValue().value;
				this.props.onChange({
					lon: convertLonToStr(rec.lng),
					lat: convertLatToStr(rec.lat),
					gpsLon: rec.gpsLng,
					gpsLat: rec.gpsLat,
					tm: tm,
					ad: tm.ad,
					zone: tm.zone,
				});	
			}else{
				this.props.onChange({
					lon: convertLonToStr(rec.lng),
					lat: convertLatToStr(rec.lat),
					gpsLon: rec.gpsLng,
					gpsLat: rec.gpsLat
				});	
			}
		}
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

	newChart(){
		if(this.props.dispatch){
			this.props.dispatch({
				type: 'astro/nowChart',
				payload: {},
			});
		}
	}

	changeChartStyle(e){
		const chartStyle = e && e.target ? e.target.value : e;
		if(this.props.dispatch){
			this.props.dispatch({
				type: 'app/save',
				payload: {
					chartStyle,
				},
			});
		}
	}

	changeIndiaChartStyle(e){
		const indiaChartStyle = e && e.target ? e.target.value : e;
		if(this.props.dispatch){
			this.props.dispatch({
				type: 'app/save',
				payload: {
					indiaChartStyle,
				},
			});
		}
	}

	toggleChartDisplayOption(opt){
		if(!this.props.dispatch){
			return;
		}
		const current = Array.isArray(this.props.chartDisplay) ? this.props.chartDisplay.slice(0) : [];
		const idx = current.indexOf(opt);
		if(idx >= 0){
			current.splice(idx, 1);
		}else{
			current.push(opt);
		}
		this.props.dispatch({
			type: 'app/save',
			payload: {
				chartDisplay: current,
			},
		});
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

	getChartMeta(chartObj, fields){
		const chart = chartObj && chartObj.chart ? chartObj.chart : {};
		const params = chartObj && chartObj.params ? chartObj.params : {};
		const zodiacalRaw = chart.zodiacal || AstroConst.ZODIACAL[`${fieldValue(fields, 'zodiacal', 0)}`];
		const hsysRaw = chart.hsys || AstroConst.HouseSys[`${fieldValue(fields, 'hsys', '')}`];
		const birth = params.birth || formatFieldTime(fields) || '未排盘';
		const location = fieldValue(fields, 'pos', '') || params.pos || '未命名地点';
		const lon = fieldValue(fields, 'lon', params.lon || '--');
		const lat = fieldValue(fields, 'lat', params.lat || '--');
		const zone = params.zone || fieldValue(fields, 'zone', '--');
		const zodiacal = AstroText.AstroMsg[zodiacalRaw] || AstroText.AstroTxtMsg[zodiacalRaw] || zodiacalRaw || '--';
		const hsys = AstroText.AstroMsg[hsysRaw] || hsysRaw || '--';
		const sect = chart.isDiurnal === undefined || chart.isDiurnal === null ? '昼夜未定' : (chart.isDiurnal ? '日生盘' : '夜生盘');
		const dayofweek = chart.dayofweek || '';
		const trueSolarTime = chart.nongli && chart.nongli.birth ? chart.nongli.birth : '';
		const dayerStar = chart.dayerStar ? (AstroText.AstroMsgCN[chart.dayerStar] || chart.dayerStar) : '';
		const timerStar = chart.timerStar ? (AstroText.AstroMsgCN[chart.timerStar] || chart.timerStar) : '';
		return {
			title: params.name || '本命盘',
			birth: `${birth}${dayofweek ? ` ${dayofweek}` : ''}`,
			location,
			lon,
			lat,
			zone,
			zodiacal,
			hsys,
			sect,
			trueSolarTime,
			dayerStar,
			timerStar,
		};
	}

	renderFeatureLinks(){
		const links = this.props.featureLinks || [];
		if(!links.length){
			return null;
		}
		const iconMap = {
			direction: <XQIcon name="direction" />,
			auxchart: <XQIcon name="aux" />,
			relativechart: <XQIcon name="composite" />,
			jieqichart: <XQIcon name="solstice" />,
		};
		return (
			<div className="horosa-astro-feature-links">
				<div className="horosa-side-section-title">相关功能</div>
				<div className="horosa-feature-link-stack">
					{links.map((item)=>(
						<XQButton
							key={item.key}
							size="small"
							className="horosa-feature-link-button"
							icon={iconMap[item.key] || <XQIcon name="other" />}
							onClick={()=>this.navigateFeature(item.key)}
						>
							<span className="horosa-feature-link-copy">
								<span className="horosa-feature-link-label">{item.label}</span>
								{item.desc ? <span className="horosa-feature-link-desc">{item.desc}</span> : null}
							</span>
						</XQButton>
					))}
				</div>
			</div>
		);
	}

	renderContextPanel(meta){
		const isIndiaChart = !!this.props.indiahsys;
		const chartStyle = AstroConst.normalizeChartStyle(this.props.chartStyle);
		const indiaChartStyle = AstroConst.normalizeIndiaChartStyle(this.props.indiaChartStyle);
		const currentDisplay = Array.isArray(this.props.chartDisplay) ? this.props.chartDisplay : [];
		const chartTools = [
			{ label: '组件', key: 'selectchartdisplay' },
			{ label: '行星', key: 'selectplanet' },
			{ label: '相位', key: 'selectasp' },
		];
		const quickToggles = [
			{ label: '相位线', opt: AstroConst.CHART_ASP_LINES },
			{ label: '四角连线', opt: AstroConst.CHART_ANGLELINE },
			{ label: '行星度数', opt: AstroConst.CHART_TXTPLANET },
			{ label: '埃及界', opt: AstroConst.CHART_TERM },
		];
		return (
			<div className="horosa-astro-context-panel">
				<div className="horosa-context-heading">
					<div className="horosa-context-title">
						<span>{meta.title}</span>
						<span className="horosa-context-sect">{meta.sect}</span>
					</div>
					<div className="horosa-context-mode">{meta.hsys} | {meta.zodiacal}</div>
				</div>
				<div className="horosa-context-lines">
					<div>{meta.birth}</div>
					<div className="horosa-context-line-pair">
						<span>时区 {meta.zone}</span>
						<span>{meta.location}</span>
					</div>
					<div className="horosa-context-line-pair">
						<span>经度 {meta.lon}</span>
						<span>纬度 {meta.lat}</span>
					</div>
					{meta.trueSolarTime ? (
						<div>
							<Tooltip title={`真太阳时：${formatTrueSolarTime(meta.trueSolarTime)}`} placement="right">
								<Button className="horosa-true-solar-button" size="small">真太阳时</Button>
							</Tooltip>
						</div>
					) : null}
				</div>
				<div className={`horosa-chart-style-block${isIndiaChart ? ' horosa-india-style-block' : ''}`}>
					<div className="horosa-side-section-title">星盘样式</div>
					{isIndiaChart ? (
						<XQSegmented
							value={indiaChartStyle}
							onChange={this.changeIndiaChartStyle}
							options={AstroConst.INDIA_CHART_STYLE_OPTIONS}
						/>
					) : (
						<XQSegmented
							value={chartStyle}
							onChange={this.changeChartStyle}
							options={AstroConst.CHART_STYLE_OPTIONS}
						/>
					)}
				</div>
				<div className="horosa-context-actions">
					<XQButton size="small" iconName="aiExport" onClick={()=>this.openDrawer('chartadd')}>存为命盘</XQButton>
					<XQButton size="small" iconName="newChart" onClick={this.newChart}>此刻</XQButton>
					<XQButton size="small" iconName="note" onClick={()=>this.openDrawer('memo')}>笔记</XQButton>
				</div>
				<div className="horosa-context-tool-stack">
					{chartTools.map((item)=>(
						<XQButton key={item.key} size="small" autoInsertSpace={false} onClick={()=>this.openDrawer(item.key)}>
							<span className="horosa-context-tool-text">{item.label}</span>
						</XQButton>
					))}
				</div>
				<div className="horosa-chart-quick-toggles">
					<div className="horosa-side-section-title">快捷显示</div>
					<div className="horosa-chart-toggle-grid">
						{quickToggles.map((item)=>{
							const active = currentDisplay.includes(item.opt);
							return (
								<XQToggle
									key={item.opt}
									size="small"
									active={active}
									onClick={()=>this.toggleChartDisplayOption(item.opt)}
								>
									{item.label}
								</XQToggle>
							);
						})}
					</div>
				</div>
				{this.renderFeatureLinks()}
			</div>
		);
	}

	renderInterpretationPanel(meta){
		const memo = this.props.memo ? this.props.memo : '';
		const summary = [
			`${meta.zodiacal}，${meta.hsys}，${meta.sect}`,
			`${meta.birth}，${meta.location}`,
			`经度 ${meta.lon}，纬度 ${meta.lat}，时区 ${meta.zone}`,
		];
		return (
			<div className="horosa-interpretation-panel">
				<Tabs defaultActiveKey="interpret" tabPosition="top" className="horosa-interpretation-tabs">
					<TabPane tab="解读" key="interpret">
						<div className="horosa-reading-lines">
							{summary.map((line)=><p key={line}>{line}</p>)}
						</div>
					</TabPane>
					<TabPane tab="笔记" key="note">
						<div className="horosa-reading-lines">
							<p>{memo || '暂无笔记'}</p>
						</div>
					</TabPane>
					<TabPane tab="批注" key="memo">
						<div className="horosa-reading-lines">
							<p>{memo || '暂无批注'}</p>
						</div>
					</TabPane>
				</Tabs>
			</div>
		);
	}

	renderQuickActions(){
		if(this.props.showQuickActions !== true){
			return null;
		}
		const actions = [
			{ label: '主/界限法', icon: <XQIcon name="qimen" />, key: 'primarydirect' },
			{ label: '法达星限', icon: <XQIcon name="solstice" />, key: 'firdaria' },
			{ label: '黄道星释', icon: <XQIcon name="astro" />, key: 'zodialrelease' },
			{ label: '小限法', icon: <XQIcon name="newChart" />, key: 'profection' },
			{ label: '太阳返照', icon: <XQIcon name="direction" />, key: 'solarreturn' },
		];
		return (
			<div className="horosa-side-quick-actions">
				<div className="horosa-side-section-title">高频功能</div>
				<div className="horosa-quick-action-grid">
					{actions.map((item)=>(
						<XQButton key={item.key} size="small" onClick={()=>this.navigateDirectionTool(item.key)}>
							<span className="horosa-quick-action-icon">{item.icon}</span>
							<span className="horosa-quick-action-label">{item.label}</span>
						</XQButton>
					))}
				</div>
			</div>
		);
	}

	render(){
		let chartObj = this.props.value;
		let fields = this.props.fields;
		let dt = new DateTime();
		if(chartObj){
			dt.setZone(chartObj.params.zone);
		}else{
			dt.setZone(fields.zone.value);
		}
		let dtstr = chartObj ? chartObj.params.birth : null;
		if(dtstr){
			if(dtstr.length > 11){
				dt.parse(dtstr, 'YYYY-MM-DD HH:mm:ss');
			}else{
				dt.parse(dtstr, 'YYYY-MM-DD');
			}
		}	

		let height = this.props.height ? this.props.height : 760;
		let tabHeight = height - 100;
		const showQuickActions = this.props.showQuickActions === true;
		const viewportHeight = typeof window !== 'undefined' ? window.innerHeight : height;
		let chartHeight = Math.max(560, Math.min(height - 150, viewportHeight - 204));

		let showzodical = true;
		let showhsys = true;
		let showdateselector = true;
		let showlots = true;
		let indiahsys = false;
		if(this.props.hidezodiacal){
			showzodical = false
		}
		if(this.props.hidehsys){
			showhsys = false;
		}
		if(this.props.hidedateselector){
			showdateselector = false;
			tabHeight = tabHeight + 100;
		}
		if(this.props.hidelots){
			showlots = false;
		}
		if(this.props.indiahsys){
			indiahsys = true;
			showhsys = false;
		}
		if(showQuickActions){
			tabHeight = tabHeight - 108;
		}
		const meta = this.getChartMeta(chartObj, fields);

		return (
			<div className="horosa-astro-page">
				<div className="horosa-astro-layout">
					<div className="horosa-astro-workbench">
						<div className="horosa-chart-body">
							{this.renderContextPanel(meta)}
							<div className="horosa-chart-stage">
								{
									this.props.chartRenderer ? (
										this.props.chartRenderer({
											chartObj,
											height: chartHeight,
											chartStyle: this.props.chartStyle,
										})
									) : (
										<AstroChart value={chartObj}
											chartDisplay={this.props.chartDisplay}
											chartStyle={this.props.chartStyle}
										planetDisplay={this.props.planetDisplay}
										lotsDisplay={this.props.lotsDisplay}
										showAstroMeaning={this.props.showAstroMeaning}
										height="100%"
									/>
									)
								}
							</div>
						</div>
						{this.renderInterpretationPanel(meta)}
					</div>
					<div className="horosa-inspector-panel">
						<Row gutter={0} className="horosa-inspector-controls">
							{
								showdateselector && (
									<Col span={24}>
										<PlusMinusTime value={dt} onChange={this.changeTime} hook={this.tmHook} />
									</Col>	
								)
							}
							{
								showzodical && (
									<Col span={7}>
										<Select 
											style={{width: '100%'}}
											onChange={this.changeZodiacal}
											value={this.props.fields.zodiacal.value} size='small'>
											<Option value={0}>回归黄道</Option>
											<Option value={1}>恒星黄道</Option>
										</Select>
									</Col>
	
								)
							}
							{
								showhsys && (
									<Col span={10}>
										<Select style={{width: '100%'}}
											onChange={this.changeHsys}
											value={this.props.fields.hsys.value} 
											size='small'>
											{ getHousesOption() }
										</Select>
									</Col>	
								)
							}
							{
								showhsys && (
									<Col span={7}>
										<Select style={{width: '100%'}}
											onChange={this.changeSouthChart}
											value={this.props.fields.southchart.value} 
											size='small'>
											<Option value={0}>天文星座</Option>
											<Option value={1}>涵义星座</Option>
										</Select>
									</Col>	
								)
							}
							{
								indiahsys && (
									<Col span={24}>
										<Select style={{width:196}}
											onChange={this.changeHsys}
											value={this.props.fields.hsys.value} 
											size='small'>
											<Option value={0}>整宫制</Option>
											<Option value={5}>Vehlow Equal</Option>
										</Select>
									</Col>	
								)
							}
							{
								showdateselector && (
									<Col span={24}>
										<Row>
										<Col span={8}>
											<GeoCoordModal 
												onOk={this.changeGeo}
												lat={this.props.fields.gpsLat.value} lng={this.props.fields.gpsLon.value}
											>
												<Button size='small' style={{width:'100%'}}>经纬度选择</Button>
											</GeoCoordModal>
										</Col>
										<Col span={16} className="horosa-geo-value">
											<span>{this.props.fields.lon.value + ' ' + this.props.fields.lat.value}</span>
										</Col>
										</Row>
									</Col>
								)
							}
						</Row>
						<Tabs defaultActiveKey="1" tabPosition='top' className="horosa-inspector-tabs">
								<TabPane tab="信息" key="1">
									<AstroInfo height={tabHeight}
										value={chartObj} fields={fields}
										planetDisplay={this.props.planetDisplay}
										showPlanetHouseInfo={this.props.showPlanetHouseInfo}
										showAstroMeaning={this.props.showAstroMeaning}
									/>
								</TabPane>
								<TabPane tab="相位" key="2">
									<AstroAspect 
										value={chartObj} height={tabHeight}
										lotsDisplay={this.props.lotsDisplay}
										planetDisplay={this.props.planetDisplay}
										showPlanetHouseInfo={this.props.showPlanetHouseInfo}
										showAstroMeaning={this.props.showAstroMeaning}
									/>
								</TabPane>
								<TabPane tab="行星" key="3">
									<AstroPlanet
										value={chartObj}
										height={tabHeight}
										showPlanetHouseInfo={this.props.showPlanetHouseInfo}
										showAstroMeaning={this.props.showAstroMeaning}
									/>
								</TabPane>
								{
									showlots && (
										<TabPane tab="希腊点" key="4">
											<AstroLots value={chartObj} height={tabHeight} showAstroMeaning={this.props.showAstroMeaning}/>
										</TabPane>	
									)
								}
							<TabPane tab="可能性" key="5">
								<AstroPredictPlanetSign height={tabHeight}
									value={chartObj} fields={fields}
									planetDisplay={this.props.planetDisplay}
									showPlanetHouseInfo={this.props.showPlanetHouseInfo}
								/>
							</TabPane>
						</Tabs>
						{this.renderQuickActions()}
					</div>
				</div>

			</div>
		);
	}

}

export default AstroChartMain;
