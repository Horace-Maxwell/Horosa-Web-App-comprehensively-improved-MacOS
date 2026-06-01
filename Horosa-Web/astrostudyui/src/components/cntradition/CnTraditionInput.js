import { Component } from 'react';
import { Checkbox } from 'antd';
import { XQSelect as Select } from '../xq-ui';
import SpaceTimePanel from '../comp/SpaceTimePanel';
import {convertLatToStr, convertLonToStr} from '../astro/AstroHelper';
import { dstAwareZoneAt } from '../../utils/timezone';
import DateTime from '../comp/DateTime';

const {Option} = Select

class CnTraditionInput extends Component{
	
	constructor(props) {
		super(props);

        this.tmHook = {
            getValue: null,
        }

		this.onTimeChanged = this.onTimeChanged.bind(this);
		this.onZoneChanged = this.onZoneChanged.bind(this);
		this.changeGeo = this.changeGeo.bind(this);

		this.onTimeAlgChange = this.onTimeAlgChange.bind(this);
		this.onPhaseTypeChange = this.onPhaseTypeChange.bind(this);
		this.onGodKeyPosChange = this.onGodKeyPosChange.bind(this);
		this.onGenderChange = this.onGenderChange.bind(this);
		this.onAfter23NewDayChange = this.onAfter23NewDayChange.bind(this);
		this.onChangeAdjustJieqi = this.onChangeAdjustJieqi.bind(this);

		this.onOnlyZiganChange = this.onOnlyZiganChange.bind(this);
		this.onUiModeChange = this.onUiModeChange.bind(this);

	}

	onOnlyZiganChange(e){
		let val = e.target.checked;
		let opt = {
			...this.props.baziOpt,
		};
		opt.onlyZiGanShen = val;
		if(this.props.onBaziOptChange){
			this.props.onBaziOptChange(opt);
		}
	}

	onUiModeChange(val){
		let opt = {
			...this.props.baziOpt,
			uiMode: val,
		};
		if(this.props.onBaziOptChange){
			this.props.onBaziOptChange(opt);
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

	onPhaseTypeChange(val){
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
				phaseType: {
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

	onGodKeyPosChange(val){
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
				godKeyPos: {
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
				},
			});
		}
	}

	onZoneChanged(val){
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
				zone: {
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

	onAfter23NewDayChange(val){
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
				after23NewDay: {
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

	onChangeAdjustJieqi(val){
		if(this.props.onFieldsChange){
			let dt = this.tmHook.getValue().value;
			this.props.onFieldsChange({
				adjustJieqi: {
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
							fields.time.value.format('HH:mm:ss');
				datetm.parse(str, 'YYYY-MM-DD HH:mm:ss');
				if(fields.zone){
					datetm.setZone(fields.zone.value);
				}
			}

			return (
				<div className="horosa-bazi-input-stack">
					<div className="horosa-panel-head">
						<div>
							<div className="horosa-panel-kicker">八字设置</div>
							<div className="horosa-panel-title">时间、地点与排盘选项</div>
						</div>
					</div>
					<SpaceTimePanel
						className="horosa-bazi-time-control"
						fields={fields}
						value={datetm}
						onTimeChange={this.onTimeChanged}
						timeHook={this.tmHook}
						onGeoChange={this.changeGeo}
					/>
					<div className="horosa-field-grid">
						<div className="horosa-field-block">
							<div className="horosa-field-label">性别</div>
							<Select value={fields.gender.value} onChange={this.onGenderChange} size='small' style={{width:'100%'}}>
								<Option value={-1}>未知</Option>
								<Option value={0}>女</Option>
								<Option value={1}>男</Option>
							</Select>
						</div>
						<div className="horosa-field-block">
							<div className="horosa-field-label">时间算法</div>
							<Select value={fields.timeAlg.value} onChange={this.onTimeAlgChange} size='small' style={{width:'100%'}}>
								<Option value={0}>真太阳时</Option>
								<Option value={1}>直接时间</Option>
								<Option value={2}>春分定卯时</Option>
							</Select>
						</div>
					</div>
					<div className="horosa-field-block">
						<div className="horosa-field-label">计算选项</div>
						<Select value={fields.phaseType.value} onChange={this.onPhaseTypeChange} size='small' style={{width:'100%'}}>
							<Option value={0}>长生火土同</Option>
							<Option value={1}>长生水土同</Option>
							<Option value={2}>长生阳顺阴逆</Option>
						</Select>
					</div>
					<div className="horosa-field-block">
						<Select value={fields.godKeyPos.value} onChange={this.onGodKeyPosChange} size='small' style={{width:'100%'}} >
							<Option value='年'>按年柱查神煞</Option>
							<Option value='日'>按日柱查神煞</Option>
							<Option value='年日'>年柱日柱都查</Option>
						</Select>
					</div>
					<div className="horosa-field-block">
						<Select value={fields.after23NewDay.value} onChange={this.onAfter23NewDayChange} size='small' style={{width:'100%'}}>
							{/* 用户拍板(见 baziLunarLocal:637): after23NewDay=1「23点算第二天」=日柱守今、时柱跨日; =0「24点算第二天」=日柱与时柱整体进位次日。 */}
							<Option value={1}>23点算第二天</Option>
							<Option value={0}>24点算第二天</Option>
						</Select>
					</div>
					<div className="horosa-field-block">
						<Select size='small' style={{width: '100%'}} value={fields.adjustJieqi.value} onChange={this.onChangeAdjustJieqi}>
							<Option value={0}>不调整节气</Option>
							<Option value={1}>节气按纬度调整</Option>
						</Select>
					</div>
					<div className="horosa-bazi-option-card">
						<Checkbox checked={this.props.baziOpt.onlyZiGanShen} onChange={this.onOnlyZiganChange}>只显示地支藏干十神</Checkbox>
					</div>
					<div className="horosa-field-block">
						<div className="horosa-field-label">界面样式</div>
						<Select value={this.props.baziOpt.uiMode || 'modern'} onChange={this.onUiModeChange} size='small' style={{width:'100%'}}>
							<Option value="modern">新星阙UI</Option>
							<Option value="legacy">旧星阙UI</Option>
						</Select>
					</div>
				</div>

			);
		}

}

export default CnTraditionInput;
