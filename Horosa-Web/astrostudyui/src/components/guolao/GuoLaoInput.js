import { Component } from 'react';
import {convertLatToStr, convertLonToStr} from '../astro/AstroHelper';
import DateTime from '../comp/DateTime';
import SpaceTimePanel from '../comp/SpaceTimePanel';
import * as SZConst from '../suzhan/SZConst';
import { XQSelect as Select, XQToggle } from '../xq-ui';
import XQIcon from '../xq-icons';
import { GUOLAO_CHART_STYLE_CLASSIC, GUOLAO_CHART_STYLE_MOIRA, GUOLAO_CHART_STYLE_PICK, GUOLAO_LIFE_MODE_ASC, GUOLAO_LIFE_MODE_COTRANS, GUOLAO_LIFE_MODE_YUMAO, GUOLAO_NODE_MODE_NORTH_KETU, GUOLAO_NODE_MODE_NORTH_RAHU, getStoredGuolaoLifeMode, getStoredGuolaoNodeMode, normalizeGuolaoLifeMode, normalizeGuolaoNodeMode, } from './GuoLaoChartStyle';

const {Option} = Select;

class GuoLaoInput extends Component{
	
	constructor(props) {
		super(props);

        this.tmHook = {
            getValue: null,
        }

		this.onTimeChanged = this.onTimeChanged.bind(this);
		this.changeGeo = this.changeGeo.bind(this);
		this.onGenderChange = this.onGenderChange.bind(this);
		this.onDoubingSu28Change = this.onDoubingSu28Change.bind(this);
		this.onChartShapeChange = this.onChartShapeChange.bind(this);
		this.onChartStyleChange = this.onChartStyleChange.bind(this);
		this.onLifeModeChange = this.onLifeModeChange.bind(this);
		this.onNodeModeChange = this.onNodeModeChange.bind(this);
		this.onMoiraTransitTimeChanged = this.onMoiraTransitTimeChanged.bind(this);
		this.onMoiraTransitGodsToggle = this.onMoiraTransitGodsToggle.bind(this);
	}

	onGenderChange(val){
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
				gender: {
					value: val,
				},
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
				},

			});
		}
	}

	onDoubingSu28Change(val){
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
				doubingSu28: {
					value: val,
				},
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
				},

			});
		}
	}

	onTimeChanged(value){
		if(this.props.onFieldsChange){
			let dt = value.time;

			this.props.onFieldsChange({
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
	}

	onChartShapeChange(val){
		SZConst.SZChart.shape = val;
		localStorage.setItem('suzhanChartShape', val);
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
				szshape: {
					value: val,
				},
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
				},

			});
		}
	}

	onChartStyleChange(val){
		if(this.props.onChartStyleChange){
			this.props.onChartStyleChange(val);
		}
	}

	onLifeModeChange(val){
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
				guolaoLifeMode: {
					value: normalizeGuolaoLifeMode(val),
				},
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
				},

			});
		}
	}

	onNodeModeChange(val){
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
				guolaoNodeMode: {
					value: normalizeGuolaoNodeMode(val),
				},
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
				},
			});
		}
	}

	onMoiraTransitTimeChanged(value){
		if(this.props.onMoiraTransitTimeChange){
			this.props.onMoiraTransitTimeChange(value);
		}
	}

	onMoiraTransitGodsToggle(){
		if(this.props.onMoiraTransitGodsVisibleChange){
			this.props.onMoiraTransitGodsVisibleChange(!this.props.showMoiraTransitGods);
		}
	}

	changeGeo(rec){
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
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
				},

			});
		}
	}

	render(){
		let fields = this.props.fields ? this.props.fields : {};
		let datetm = new DateTime();
		if(fields.date && fields.time){
			let str = fields.date.value.format('YYYY-MM-DD') + ' ' + 
						fields.time.value.format('HH:mm:ss');
			datetm = datetm.parse(str, 'YYYY-MM-DD HH:mm:ss');
			if(fields.zone){
				datetm.setZone(fields.zone.value);
			}
		}

		let szshape = SZConst.SZChart.shape;
		if(fields.szshape !== undefined && fields.szshape !== null &&
			fields.szshape.value !== undefined && fields.szshape.value !== null){
			szshape = fields.szshape.value;
		}
		const chartStyle = this.props.chartStyle === GUOLAO_CHART_STYLE_PICK
			? GUOLAO_CHART_STYLE_PICK
			: (this.props.chartStyle === GUOLAO_CHART_STYLE_MOIRA ? GUOLAO_CHART_STYLE_MOIRA : GUOLAO_CHART_STYLE_CLASSIC);
		const lifeMode = fields.guolaoLifeMode && fields.guolaoLifeMode.value !== undefined && fields.guolaoLifeMode.value !== null
			? normalizeGuolaoLifeMode(fields.guolaoLifeMode.value)
			: getStoredGuolaoLifeMode();
		const nodeMode = fields.guolaoNodeMode && fields.guolaoNodeMode.value !== undefined && fields.guolaoNodeMode.value !== null
			? normalizeGuolaoNodeMode(fields.guolaoNodeMode.value)
			: getStoredGuolaoNodeMode();

		return (
			<div className="horosa-guolao-input-stack">
				<div className="horosa-side-panel-heading">
					<div>
						<div className="horosa-side-panel-title">七政设置</div>
						<div className="horosa-side-panel-subtitle">时间、地点与排盘选项</div>
					</div>
				</div>

				<SpaceTimePanel
					fields={fields}
					value={datetm}
					onTimeChange={this.onTimeChanged}
					timeHook={this.tmHook}
					onGeoChange={this.changeGeo}
				/>

				<div className="horosa-guolao-input-section">
					<div className="horosa-guolao-field-title">
						<XQIcon name="sliders" />
						<span>选项</span>
					</div>
					<div className="horosa-guolao-select-grid">
						<label className="horosa-guolao-select-field">
							<span>性别</span>
							<Select value={fields.gender.value} onChange={this.onGenderChange} size='small'>
								<Option value={-1}>未知</Option>
								<Option value={0}>女</Option>
								<Option value={1}>男</Option>
							</Select>
						</label>
						<label className="horosa-guolao-select-field">
							<span>宿度制</span>
							<Select value={fields.doubingSu28.value} onChange={this.onDoubingSu28Change} size='small'>
								<Option value={2}>回归今制</Option>
								<Option value={3}>回归古制（开禧）</Option>
								<Option value={4}>恒星制（郑式）</Option>
								<Option value={0}>荀爽19年测量</Option>
								<Option value={1}>斗柄定房法</Option>
							</Select>
						</label>
						<label className="horosa-guolao-select-field">
							<span>命度</span>
							<Select value={lifeMode} onChange={this.onLifeModeChange} size='small'>
								<Option value={GUOLAO_LIFE_MODE_ASC}>占星上升</Option>
								<Option value={GUOLAO_LIFE_MODE_YUMAO}>遇卯安命</Option>
								<Option value={GUOLAO_LIFE_MODE_COTRANS}>赤黄转换</Option>
							</Select>
						</label>
						<label className="horosa-guolao-select-field">
							<span>盘式</span>
							<Select value={szshape} onChange={this.onChartShapeChange} size='small'>
								<Option value={SZConst.SZChart_Circle}>圆形盘</Option>
								<Option value={SZConst.SZChart_Square}>方形盘</Option>
							</Select>
						</label>
						<label className="horosa-guolao-select-field">
							<span>星盘样式</span>
							<Select value={chartStyle} onChange={this.onChartStyleChange} size='small'>
								<Option value={GUOLAO_CHART_STYLE_CLASSIC}>Horosa原盘</Option>
								<Option value={GUOLAO_CHART_STYLE_MOIRA}>Moira圆盘</Option>
								<Option value={GUOLAO_CHART_STYLE_PICK}>天星择日</Option>
							</Select>
						</label>
						<label className="horosa-guolao-select-field">
							<span>罗计</span>
							<Select value={nodeMode} onChange={this.onNodeModeChange} size='small'>
								<Option value={GUOLAO_NODE_MODE_NORTH_RAHU}>北罗南计</Option>
								<Option value={GUOLAO_NODE_MODE_NORTH_KETU}>北计南罗</Option>
							</Select>
						</label>
					</div>
				</div>

				{chartStyle === GUOLAO_CHART_STYLE_MOIRA || chartStyle === GUOLAO_CHART_STYLE_PICK ? (
					<div className="horosa-guolao-input-section horosa-guolao-moira-transit-section">
						<div className="horosa-guolao-field-title">
							<XQIcon name="clock" />
							<span>{chartStyle === GUOLAO_CHART_STYLE_PICK ? '天星择日动盘' : 'Moira流年'}</span>
						</div>
						<SpaceTimePanel
							className="horosa-guolao-moira-transit-time"
							value={this.props.moiraTransitTime}
							timeText={this.props.moiraTransitTime ? this.props.moiraTransitTime.format('YYYY-MM-DD HH:mm:ss') : ''}
							onTimeChange={this.onMoiraTransitTimeChanged}
							showLocation={false}
							needZone={false}
						/>
						{chartStyle === GUOLAO_CHART_STYLE_MOIRA ? <div className="horosa-guolao-toggle-grid">
							<XQToggle
								size="small"
								iconName="sideSwitch"
								active={this.props.showMoiraTransitGods !== false}
								onClick={this.onMoiraTransitGodsToggle}
							>
								流年神煞圈
							</XQToggle>
						</div> : null}
					</div>
				) : null}
			</div>
		);
	}

}

export default GuoLaoInput;
