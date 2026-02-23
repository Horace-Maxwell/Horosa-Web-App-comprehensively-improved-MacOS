import { Component } from 'react';
import { Row, Card, } from 'antd';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import { appendPlanetHouseInfoById, splitPlanetHouseInfoText, } from '../../utils/planetHouseInfo';
import styles from '../../css/styles.less';

class AstroPredictPlanetSign extends Component{

	constructor(props) {
		super(props);
		this.state = {

		}
		this.genDom = this.genDom.bind(this);
		this.renderTitle = this.renderTitle.bind(this);
	}

	renderTitle(id, chartObj){
		const text = appendPlanetHouseInfoById(
			AstroText.AstroMsg[id],
			chartObj,
			id,
			this.props.showPlanetHouseInfo
		);
		const one = splitPlanetHouseInfoText(text);
		return (
			<span>
				<span style={{fontFamily: AstroConst.AstroFont}}>{one.label}</span>
				{one.info ? <span style={{fontFamily: AstroConst.NormalFont}}>{`(${one.info})`}</span> : null}
				<span style={{fontFamily: AstroConst.NormalFont}}>{`(${AstroText.AstroTxtMsg[id] || id})`}</span>
			</span>
		);
	}


	genDom(chartObj){
		const doms = [];
		const planetsig = chartObj && chartObj.predict && chartObj.predict.PlanetSign
			? chartObj.predict.PlanetSign
			: {};
		const keys = Object.keys(planetsig);
		if(keys.length === 0){
			return (
				<div style={{padding: 12}}>
					暂无可能性数据
				</div>
			);
		}
		for(let i=0; i<keys.length; i++){
			const key = keys[i];
			let list = planetsig[key];
			if(!Array.isArray(list)){
				list = [];
			}
			let desc = list.map((item, idx)=>{
				return (
					<li key={`${key}_${idx}`}>{item}</li>
				)
			});
			let dom = (
				<Row key={key}>
					<Card title={this.renderTitle(key, chartObj)} 
						bordered={true} 
						style={{
							fontFamily: AstroConst.AstroFont,
							background: AstroConst.AstroColor.Backgroud
						}}>
							<ul style={{fontFamily: AstroConst.NormalFont}}>
								{desc}
							</ul>
					</Card>
				</Row>
			);
			doms.push(dom);
		}
		return doms;
	}


	render(){
		const chart = this.props.value || {};
		const dom = this.genDom(chart);

		let height = this.props.height ? this.props.height : '100%';
		let style = {
			height: (height-130) + 'px',
			overflowY:'auto', 
			overflowX:'hidden',
		};

		return (
			<div className={styles.scrollbar} style={style}>
				{dom}
			</div>
		);
	}
}

export default AstroPredictPlanetSign;
