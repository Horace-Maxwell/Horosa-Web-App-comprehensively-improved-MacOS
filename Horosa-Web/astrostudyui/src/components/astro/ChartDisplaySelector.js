import { Component } from 'react';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import { XQCheckItem, XQCheckList, XQSectionTitle } from '../xq-ui';

class ChartDisplaySelector extends Component{

	constructor(props) {
		super(props);

		this.changeChartOption = this.changeChartOption.bind(this);
		this.changeShowPdBounds = this.changeShowPdBounds.bind(this);
		this.changeShowPlanetHouseInfo = this.changeShowPlanetHouseInfo.bind(this);
		this.changeShowAstroMeaning = this.changeShowAstroMeaning.bind(this);
		this.changeOnlyRulerExaltReception = this.changeOnlyRulerExaltReception.bind(this);
	}

	changeChartOption(opt, e){
		if(!this.props.dispatch){
			return;
		}
		const checked = !!(e && e.target && e.target.checked);
		const current = Array.isArray(this.props.value) ? [...this.props.value] : [];
		const idx = current.indexOf(opt);
		if(checked && idx < 0){
			current.push(opt);
		}
		if(!checked && idx >= 0){
			current.splice(idx, 1);
		}
		this.props.dispatch({
			type: 'app/save',
			payload:{
				chartDisplay: current,
			},
		});
	}

	changeShowPdBounds(e){
		if(!this.props.dispatch){
			return;
		}
		const val = e && e.target && e.target.checked ? 1 : 0;
		this.props.dispatch({
			type: 'app/save',
			payload:{
				showPdBounds: val,
			},
		});

		let flds = {
			...(this.props.fields || {}),
		};
		if(!flds.showPdBounds){
			flds.showPdBounds = {
				value: val,
				name: ['showPdBounds'],
			};
		}else{
			flds.showPdBounds.value = val;
		}
		this.props.dispatch({
			type: 'astro/save',
			payload:{
				fields: flds,
			},
		});
	}

	changeShowPlanetHouseInfo(e){
		if(!this.props.dispatch){
			return;
		}
		const checked = e && e.target && e.target.checked ? 1 : 0;
		this.props.dispatch({
			type: 'app/save',
			payload: {
				showPlanetHouseInfo: checked,
			},
		});
	}

	changeShowAstroMeaning(e){
		if(!this.props.dispatch){
			return;
		}
		const checked = e && e.target && e.target.checked ? 1 : 0;
		this.props.dispatch({
			type: 'app/save',
			payload: {
				showAstroMeaning: checked,
			},
		});
	}

	changeOnlyRulerExaltReception(e){
		if(!this.props.dispatch){
			return;
		}
		const checked = e && e.target && e.target.checked ? 1 : 0;
		this.props.dispatch({
			type: 'app/save',
			payload: {
				showOnlyRulExaltReception: checked,
			},
		});
	}

	render(){
		const labelStyle = {
			fontFamily: AstroConst.AstroFont,
		};
		const currentDisplay = Array.isArray(this.props.value) ? this.props.value : [];

		// 三维盘已淘汰（改用天文馆），从星盘组件设置中清掉其 6 个选项；常量保留供旧 astro3d 组件引用。
		const chart3dBits = [AstroConst.CHART_3D_SKYBALL_LATLINE, AstroConst.CHART_3D_EARTH_LATLINE, AstroConst.CHART_3D_EARTH_LONLINE, AstroConst.CHART_3D_EARTH_RADIUS_SAMESKY, AstroConst.CHART_3D_EARTH, AstroConst.CHART_3D_PLANET_SYM];
		let allobjs = AstroConst.CHART_OPTIONS.filter((opt)=>opt !== AstroConst.CHART_INFOINCIRCLE && !chart3dBits.includes(opt)).map((opt)=>{
			const checked = currentDisplay.includes(opt);
			return (
				<XQCheckItem
					key={opt}
					checked={checked}
					onClick={()=>this.changeChartOption(opt, {target: {checked: !checked}})}
				>
					<span style={labelStyle}>
						{AstroText.ChartOptionText[opt+'']}
					</span>
				</XQCheckItem>
			);
		});

		return (
			<div className="horosa-selector-drawer">
				<XQSectionTitle>星盘层级</XQSectionTitle>
				<XQCheckList>
					{allobjs}
				</XQCheckList>
				<XQSectionTitle>解释与计算</XQSectionTitle>
				<XQCheckList>
					<XQCheckItem
						checked={this.props.showPdBounds !== 0}
						onClick={()=>this.changeShowPdBounds({target: {checked: !(this.props.showPdBounds !== 0)}})}
					>
						<span style={labelStyle}>
							主/界限法显示界限法
						</span>
					</XQCheckItem>
					<XQCheckItem
						checked={this.props.showPlanetHouseInfo === 1 || this.props.showPlanetHouseInfo === true}
						onClick={()=>this.changeShowPlanetHouseInfo({target: {checked: !(this.props.showPlanetHouseInfo === 1 || this.props.showPlanetHouseInfo === true)}})}
					>
						<span style={labelStyle}>
							星曜附带后天宫信息
						</span>
					</XQCheckItem>
					<XQCheckItem
						checked={this.props.showAstroMeaning === 1 || this.props.showAstroMeaning === true}
						onClick={()=>this.changeShowAstroMeaning({target: {checked: !(this.props.showAstroMeaning === 1 || this.props.showAstroMeaning === true)}})}
					>
						<span style={labelStyle}>
							是否显示星/宫/座/相释义
						</span>
					</XQCheckItem>
					<XQCheckItem
						checked={this.props.showOnlyRulExaltReception === 1 || this.props.showOnlyRulExaltReception === true}
						onClick={()=>this.changeOnlyRulerExaltReception({target: {checked: !(this.props.showOnlyRulExaltReception === 1 || this.props.showOnlyRulExaltReception === true)}})}
					>
						<span style={labelStyle}>
							仅按照本垣擢升计算互容接纳
						</span>
					</XQCheckItem>
				</XQCheckList>
			</div>
		);
	}
}

export default ChartDisplaySelector;
