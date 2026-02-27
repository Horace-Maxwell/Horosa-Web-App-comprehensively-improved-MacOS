import { Component } from 'react';
import { Checkbox, Row, Col } from 'antd';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';

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

		let allobjs = AstroConst.CHART_OPTIONS.map((opt)=>{
			return (
				<Col span={24} key={opt}>
					<Checkbox
						style={labelStyle}
						checked={currentDisplay.includes(opt)}
						onChange={(e)=>this.changeChartOption(opt, e)}
					>
						{AstroText.ChartOptionText[opt+'']}
					</Checkbox>
				</Col>
			);
		});

		return (
			<div>
				<Row gutter={12}>
					{allobjs}
					<Col span={24}>
						<Checkbox
							style={labelStyle}
							checked={this.props.showPdBounds !== 0}
							onChange={this.changeShowPdBounds}
						>
							主/界限法显示界限法
						</Checkbox>
					</Col>
					<Col span={24}>
						<Checkbox
							style={labelStyle}
							checked={this.props.showPlanetHouseInfo === 1 || this.props.showPlanetHouseInfo === true}
							onChange={this.changeShowPlanetHouseInfo}
						>
							星曜附带后天宫信息
						</Checkbox>
					</Col>
					<Col span={24}>
						<Checkbox
							style={labelStyle}
							checked={this.props.showAstroMeaning === 1 || this.props.showAstroMeaning === true}
							onChange={this.changeShowAstroMeaning}
						>
							是否显示星/宫/座/相释义
						</Checkbox>
					</Col>
					<Col span={24}>
						<Checkbox
							style={labelStyle}
							checked={this.props.showOnlyRulExaltReception === 1 || this.props.showOnlyRulExaltReception === true}
							onChange={this.changeOnlyRulerExaltReception}
						>
							仅按照本垣擢升计算互容接纳
						</Checkbox>
					</Col>
				</Row>
			</div>
		);
	}
}

export default ChartDisplaySelector;
