import { Component } from 'react';
import { Checkbox } from 'antd';
import {convertLatToStr, convertLonToStr} from '../astro/AstroHelper';
import { dstAwareZoneAt } from '../../utils/timezone';
import * as ZWCont from '../../constants/ZWConst';
import DateTime from '../comp/DateTime';
import SpaceTimePanel from '../comp/SpaceTimePanel';
import { XQSelect as Select } from '../xq-ui';
import XQIcon from '../xq-icons';

const {Option} = Select;

class ZiWeiInput extends Component{
	
	constructor(props) {
		super(props);

		let showTips = true;
		let tips = localStorage.getItem('ziweiTips');
		if(tips !== undefined && tips !== null){
			if(tips+'' === '1'){
				showTips = true;
			}else{
				showTips = false;
			}
		}

		this.state = {
			showTips: showTips,
		}

        this.tmHook = {
            getValue: null,
        }

		this.onTimeChanged = this.onTimeChanged.bind(this);
		this.changeGeo = this.changeGeo.bind(this);

		this.onGenderChange = this.onGenderChange.bind(this);
		this.onTimeAlgChange = this.onTimeAlgChange.bind(this);
		this.onChartTypeChange = this.onChartTypeChange.bind(this);
		this.onTipsChange = this.onTipsChange.bind(this);

		let type = localStorage.getItem('ziweiChartType');
		if(type !== undefined && type !== null){
			ZWCont.ZWChart.chart = parseInt(type+'');
		}

	}

	onChartTypeChange(val){
		ZWCont.ZWChart.chart = val;
		localStorage.setItem('ziweiChartType', val);
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
				zwchart: {
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
	
	onTimeAlgChange(val){
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
				timeAlg: {
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



	onTipsChange(e){
		let val = e.target.checked;
		localStorage.setItem('ziweiTips', val ? 1 : 0);
		this.setState({
			showTips: val,
		});
	}


	changeGeo(rec){
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			// 选新地点时按新坐标自动校正时区(未在 atlas 内手改时区时)。
			// setZone 仅改时区标签、保留出生钟面时刻(见 DateTime.setZone),不移位时间。
			if(dt && dt.setZone){
				try{
					if(rec.zone){
						dt.setZone(rec.zone);
					}else{
						const ds = dt.format ? dt.format('YYYY-MM-DD') : null;
						const z = dstAwareZoneAt(rec.gpsLat, rec.gpsLng, ds);
						if(z && z.offset){ dt.setZone(z.offset); }
					}
				}catch(e){ /* 推断失败保留原时区 */ }
			}
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
						fields.time.value.format('HH:mm');
			datetm = datetm.parse(str, 'YYYY-MM-DD HH:mm');
			if(fields.zone){
				datetm.setZone(fields.zone.value);
			}
		}

		let zwchart = ZWCont.ZWChart.chart;
		if(fields.zwchart !== undefined && fields.zwchart !== null &&
			fields.zwchart.value !== undefined && fields.zwchart.value !== null){
			zwchart = fields.zwchart.value;
		}
		let timeAlg = fields.timeAlg && fields.timeAlg.value !== undefined && fields.timeAlg.value !== null
			? fields.timeAlg.value
			: 0;

		return (
			<div className="horosa-ziwei-input-stack">
				<div className="horosa-side-panel-heading">
					<div>
						<div className="horosa-side-panel-title">紫微设置</div>
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

				<div className="horosa-ziwei-input-section">
					<div className="horosa-ziwei-field-title">
						<XQIcon name="sliders" />
						<span>选项</span>
					</div>
					<div className="horosa-ziwei-select-grid">
						<label className="horosa-ziwei-select-field">
							<span>性别</span>
							<Select value={fields.gender.value} onChange={this.onGenderChange} size='small'>
								<Option value={-1}>未知</Option>
								<Option value={0}>女</Option>
								<Option value={1}>男</Option>
							</Select>
						</label>
						<label className="horosa-ziwei-select-field">
							<span>时间算法</span>
							<Select value={timeAlg} onChange={this.onTimeAlgChange} size='small'>
								<Option value={0}>真太阳时</Option>
								<Option value={1}>直接时间</Option>
							</Select>
						</label>
						<label className="horosa-ziwei-select-field horosa-ziwei-select-field-wide">
							<span>盘式</span>
							<Select value={zwchart} onChange={this.onChartTypeChange} size='small'>
								<Option value={ZWCont.ZWChart_SiHua}>四化盘</Option>
								<Option value={ZWCont.ZWChart_SangHe}>三合盘</Option>
							</Select>
						</label>
					</div>
					<div className="horosa-ziwei-option-card">
						<Checkbox checked={this.state.showTips} onChange={this.onTipsChange}>允许提示</Checkbox>
					</div>
				</div>
			</div>
		);
	}

}

export default ZiWeiInput;
