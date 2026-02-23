import { Component } from 'react';
import { Row, Col, Divider, Popover, } from 'antd';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import * as AstroHelper from '../astro/AstroHelper';
import { randomStr} from '../../utils/helper'
import { appendPlanetHouseInfoById, splitPlanetHouseInfoText, } from '../../utils/planetHouseInfo';
import styles from '../../css/styles.less';

const LIST_POINTS = [
    AstroConst.ASC, AstroConst.MC, AstroConst.DESC, AstroConst.IC,
	AstroConst.SUN, AstroConst.MOON, AstroConst.MERCURY, AstroConst.VENUS, 
	AstroConst.MARS, AstroConst.JUPITER, AstroConst.SATURN, 
	AstroConst.URANUS, AstroConst.NEPTUNE, AstroConst.PLUTO, 
	AstroConst.CHIRON, AstroConst.NORTH_NODE, AstroConst.SOUTH_NODE, 
	AstroConst.DARKMOON, AstroConst.PURPLE_CLOUDS, AstroConst.SYZYGY, AstroConst.PARS_FORTUNA
]

let pars = new Set()
let planets = new Set()

class AntisciaInfo extends Component{

	constructor(props) {
		super(props);
		this.state = {
			 
		}

		this.genAntisciasDom = this.genAntisciasDom.bind(this);
		this.renderLabel = this.renderLabel.bind(this);
	}

	renderLabel(text){
		const one = splitPlanetHouseInfoText(text);
		return (
			<span>
				<span style={{fontFamily: AstroConst.AstroFont}}>{one.label}</span>
				{one.info ? <span style={{fontFamily: AstroConst.NormalFont}}>{`(${one.info})`}</span> : null}
			</span>
		);
	}


	genAntisciasDom(chart, title, innerTitle){
		if(chart === undefined || chart.antiscias === undefined || chart.antiscias === null){
			return null;
		}
		let anti = chart.antiscias;

		let divs = [];
		let divider = (<Divider key={randomStr(8)} orientation="left">映点</Divider>);
		divs.push(divider);
		for(let idx=0; idx<anti.length; idx++){
			let obj = anti[idx];
			const labelA = appendPlanetHouseInfoById(
				AstroText.AstroMsg[obj.idA],
				this.props.dirChart,
				obj.idA,
				this.props.showPlanetHouseInfo
			);
			const labelB = appendPlanetHouseInfoById(
				AstroText.AstroMsg[obj.idB],
				this.props.natualChart,
				obj.idB,
				this.props.showPlanetHouseInfo
			);
			let dom = (
				<div key={randomStr(8)} style={{fontFamily: AstroConst.AstroFont}}>
					<span style={{fontFamily: AstroConst.NormalFont}}>{title}&nbsp;</span>
					{this.renderLabel(labelA)}&nbsp;与&nbsp;
					<span style={{fontFamily: AstroConst.NormalFont}}>{innerTitle}&nbsp;</span>
					{this.renderLabel(labelB)}&nbsp;成映点&nbsp;
					<span style={{fontFamily: AstroConst.NormalFont}}>误差{Math.round(obj.delta * 1000) / 1000}</span>
				</div>
			);
			divs.push(dom);
		}

		divider = (<Divider key={randomStr(8)} orientation="left">反映点</Divider>);
		divs.push(divider);
		let canti = chart.cantiscias;
		for(let idx=0; idx<canti.length; idx++){
			let obj = canti[idx];
			const labelA = appendPlanetHouseInfoById(
				AstroText.AstroMsg[obj.idA],
				this.props.dirChart,
				obj.idA,
				this.props.showPlanetHouseInfo
			);
			const labelB = appendPlanetHouseInfoById(
				AstroText.AstroMsg[obj.idB],
				this.props.natualChart,
				obj.idB,
				this.props.showPlanetHouseInfo
			);
			let dom = (
				<div key={randomStr(8)} style={{fontFamily: AstroConst.AstroFont}}>
					<span style={{fontFamily: AstroConst.NormalFont}}>{title}&nbsp;</span>
					{this.renderLabel(labelA)}&nbsp;与&nbsp;
					<span style={{fontFamily: AstroConst.NormalFont}}>{innerTitle}&nbsp;</span>
					{this.renderLabel(labelB)}&nbsp;成反映点&nbsp;
					<span style={{fontFamily: AstroConst.NormalFont}}>误差{Math.round(obj.delta * 1000) / 1000}</span>
				</div>
			);
			divs.push(dom);
		}

		let dom = (
			<div>
				<Row>
					<Col span={24}>{divs}</Col>
				</Row>
			</div>
		);

		return dom;
	}


	render(){
		if(this.props.lotsDisplay){
			pars = new Set();
			for(let i=0; i<this.props.lotsDisplay.length; i++){
				pars.add(this.props.lotsDisplay[i]);
			}
		}
		if(this.props.planetDisplay){
			planets = new Set();
			for(let i=0; i<this.props.planetDisplay.length; i++){
				planets.add(this.props.planetDisplay[i]);
			}
		}

		let normalAsp = this.genAntisciasDom(this.props.value, this.props.title, this.props.innerTitle);

		let height = this.props.height ? this.props.height : '100%';
		let style = {
			height: (height-130) + 'px',
			overflowY:'auto', 
			overflowX:'hidden',
		};

		return (
			<div className={styles.scrollbar} style={style}>
				{normalAsp}
			</div>
		);
	}
}

export default AntisciaInfo;
