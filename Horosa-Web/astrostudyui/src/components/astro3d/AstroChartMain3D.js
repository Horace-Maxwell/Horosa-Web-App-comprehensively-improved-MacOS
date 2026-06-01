import { Component } from 'react';
import AstroChart3D from './AstroChart3D';
import AstroInfo from '../astro/AstroInfo';
import AstroAspect from '../astro/AstroAspect';
import AstroPlanet from '../astro/AstroPlanet';
import AstroLots from '../astro/AstroLots';
import PlusMinusTime from '../astro/PlusMinusTime';
import DateTime from '../comp/DateTime';
import GeoCoordModal from '../amap/GeoCoordModal';
import { convertLatToStr, convertLonToStr} from '../astro/AstroHelper';
import { resolveGeoZone } from '../../utils/timezone';
import { getHousesOption } from '../comp/CompHelper'
import {
	XQButton,
	XQPanel,
	XQSectionTitle,
	XQSelect,
	XQTabs,
	XQToolbar,
} from '../xq-ui';

const TabPane = XQTabs.TabPane;
const Option = XQSelect.Option;

class AstroChartMain3D extends Component{

	constructor(props) {
		super(props);
		this.state = {

		}

		this.changeTime = this.changeTime.bind(this);
		this.changeZodiacal = this.changeZodiacal.bind(this);
		this.changeHsys = this.changeHsys.bind(this);
		this.changeGeo = this.changeGeo.bind(this);
		this.changeSouthChart = this.changeSouthChart.bind(this);

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
			this.props.onChange({
				zodiacal: val,
			});
		}
	}

	changeHsys(val){
		if(this.props.onChange){
			this.props.onChange({
				hsys: val,
			});
		}
	}

	changeSouthChart(val){
		if(this.props.fields.gpsLat === undefined || this.props.fields.gpsLat === null || this.props.fields.gpsLat.value >= 0){
			return;
		}
		if(this.props.onChange){
			this.props.onChange({
				southchart: val,
			});
		}
	}

	changeGeo(rec){
		if(this.props.onChange){
			const payload = {
				lon: convertLonToStr(rec.lng),
				lat: convertLatToStr(rec.lat),
				gpsLon: rec.gpsLng,
				gpsLat: rec.gpsLat
			};
			// 选地点 → 时区自动校正(与 2D 占星一致:重锚出生时刻到新偏移、保留钟面时刻;手动改过则用 rec.zone)
			const chartObj = this.props.value;
			const f = this.props.fields || {};
			const curZone = (chartObj && chartObj.params) ? chartObj.params.zone : (f.zone ? f.zone.value : null);
			const birth = (chartObj && chartObj.params) ? chartObj.params.birth : null;
			if(birth){
				const dt = new DateTime();
				if(curZone){ dt.setZone(curZone); }
				if(birth.length > 11){ dt.parse(birth, 'YYYY-MM-DD HH:mm:ss'); }else{ dt.parse(birth, 'YYYY-MM-DD'); }
				const z = resolveGeoZone(rec, dt.format ? dt.format('YYYY-MM-DD') : null);
				if(z && dt.setZone){ dt.setZone(z); }
				payload.tm = dt;
				payload.ad = dt.ad;
				payload.zone = dt.zone;
			}else{
				const z = resolveGeoZone(rec, null);
				if(z){ payload.zone = z; }
			}
			this.props.onChange(payload);
		}
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
		let chartHeight = Math.max(360, height - 28);
		let tabHeight = height - 252;

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
			tabHeight = tabHeight + 112;
		}
		if(this.props.hidelots){
			showlots = false;
		}
		if(this.props.indiahsys){
			indiahsys = true;
			showhsys = false;
		}

		let needChart3D = false;
		if((this.props.currentTab && this.props.currentTab === 'astrochart3D') || this.props.needChart3D){
			needChart3D = true;
		}

		return (
			<div className="horosa-3d-page xq-chart-renderer xq-chart-renderer-3d">
				<XQPanel className="horosa-3d-stage">
					<div className="horosa-3d-stage-title">
						<div>
							<div className="horosa-3d-eyebrow">三维天球</div>
							<div className="horosa-3d-title">3D 星盘</div>
						</div>
						<div className="horosa-3d-hint">双击画布进入或退出全屏</div>
					</div>
					<div className="horosa-3d-canvas-wrap">
						<AstroChart3D 
							value={chartObj} 
							fields={this.props.fields}
							chartDisplay={this.props.chartDisplay}
							planetDisplay={this.props.planetDisplay}
							lotsDisplay={this.props.lotsDisplay}
							height={chartHeight}
							needChart3D={needChart3D}
						/>
					</div>
				</XQPanel>
				<XQPanel className="horosa-3d-side">
					{showdateselector ? (
						<div className="horosa-3d-time">
							<XQSectionTitle>时间</XQSectionTitle>
							<PlusMinusTime value={dt} onChange={this.changeTime} />
						</div>
					) : null}
					<XQSectionTitle>盘面参数</XQSectionTitle>
					<div className="horosa-3d-control-grid">
						{showzodical ? (
							<XQSelect
								onChange={this.changeZodiacal}
								value={this.props.fields.zodiacal.value}
								size='small'
							>
								<Option value={0}>回归黄道</Option>
								<Option value={1}>恒星黄道</Option>
							</XQSelect>
						) : null}
						{showhsys ? (
							<XQSelect
								onChange={this.changeHsys}
								value={this.props.fields.hsys.value}
								size='small'
							>
								{ getHousesOption() }
							</XQSelect>
						) : null}
						{showhsys ? (
							<XQSelect
								onChange={this.changeSouthChart}
								value={this.props.fields.southchart.value}
								size='small'
							>
								<Option value={0}>天文星座</Option>
								<Option value={1}>涵义星座</Option>
							</XQSelect>
						) : null}
						{indiahsys ? (
							<XQSelect
								onChange={this.changeHsys}
								value={this.props.fields.hsys.value}
								size='small'
							>
								<Option value={0}>整宫制</Option>
								<Option value={5}>Vehlow Equal</Option>
							</XQSelect>
						) : null}
					</div>
					{showdateselector ? (
						<XQToolbar className="horosa-3d-geo">
							<GeoCoordModal
								onOk={this.changeGeo}
								lat={this.props.fields.gpsLat.value}
								lng={this.props.fields.gpsLon.value}
							>
								<XQButton size='small' iconName="locastro">经纬度选择</XQButton>
							</GeoCoordModal>
							<span>{this.props.fields.lon.value + ' ' + this.props.fields.lat.value}</span>
						</XQToolbar>
					) : null}
					<XQTabs defaultActiveKey="1" tabPosition='top' className="horosa-3d-tabs">
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
						{showlots ? (
							<TabPane tab="希腊点" key="4">
								<AstroLots value={chartObj} height={tabHeight} showAstroMeaning={this.props.showAstroMeaning}/>
							</TabPane>
						) : null}
					</XQTabs>
				</XQPanel>
			</div>
		);
	}

}

export default AstroChartMain3D;
