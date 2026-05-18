import { Component } from 'react';
import {convertLatToStr, convertLonToStr} from '../astro/AstroHelper';
import DateTime from '../comp/DateTime';
import SpaceTimePanel from '../comp/SpaceTimePanel';
import * as SZConst from '../suzhan/SZConst';
import { XQSelect as Select } from '../xq-ui';
import XQIcon from '../xq-icons';

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
		this.onHouseStartModeChange = this.onHouseStartModeChange.bind(this);

		let houseStartMode = localStorage.getItem('suzhanHouseStartMode');
		if(houseStartMode !== undefined && houseStartMode !== null){
			try{
				houseStartMode = parseInt(houseStartMode, 10);
				if(houseStartMode === SZConst.SZHouseStart_ASC){
					SZConst.SZChart.houseStartMode = SZConst.SZHouseStart_ASC;
				}
			}catch(e){
				SZConst.SZChart.houseStartMode = SZConst.SZHouseStart_Bazi;
			}
		}
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

	onHouseStartModeChange(val){
		SZConst.SZChart.houseStartMode = val;
		localStorage.setItem('suzhanHouseStartMode', val);
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
				houseStartMode: {
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
		let houseStartMode = SZConst.SZChart.houseStartMode;
		if(fields.houseStartMode !== undefined && fields.houseStartMode !== null &&
			fields.houseStartMode.value !== undefined && fields.houseStartMode.value !== null){
			houseStartMode = parseInt(fields.houseStartMode.value, 10);
		}
		if(houseStartMode !== SZConst.SZHouseStart_ASC){
			houseStartMode = SZConst.SZHouseStart_Bazi;
		}

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
							<span>二十八宿</span>
							<Select value={fields.doubingSu28.value} onChange={this.onDoubingSu28Change} size='small'>
								<Option value={0}>现实距星法</Option>
								<Option value={1}>斗柄定房法</Option>
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
							<span>人事十二宫</span>
							<Select value={houseStartMode} onChange={this.onHouseStartModeChange} size='small'>
								<Option value={SZConst.SZHouseStart_Bazi}>八字公式起盘</Option>
								<Option value={SZConst.SZHouseStart_ASC}>ASC起盘</Option>
							</Select>
						</label>
					</div>
				</div>
			</div>
		);
	}

}

export default GuoLaoInput;
