import { Component } from 'react';
import * as AstroText from '../../constants/AstroText';
import {
	ROMAN_HOUSES,
	SIGN_NAMES,
	getAscSignNumber,
	getHouseCuspDegree,
	getObjectColor,
	getObjectDegree,
	getObjectLabel,
	getObjectsBySign,
} from './IndiaSouthChart';
import '../../css/styles.less';

const NORTH_HOUSE_LABEL_POSITIONS = {
	1: [50, 8],
	2: [38, 8],
	3: [7, 17],
	4: [36, 34],
	5: [7, 53],
	6: [24, 83],
	7: [50, 85],
	8: [84, 83],
	9: [94, 58],
	10: [74, 34],
	11: [94, 17],
	12: [84, 8],
};

const NORTH_SIGN_BADGE_POSITIONS = {
	1: [50, 42],
	2: [25, 25],
	3: [19, 31],
	4: [41, 53],
	5: [19, 77],
	6: [25, 82],
	7: [50, 58],
	8: [75, 82],
	9: [81, 77],
	10: [59, 62],
	11: [81, 31],
	12: [75, 25],
};

const NORTH_OBJECT_ANCHOR_POSITIONS = {
	1: [50, 36],
	2: [36, 20],
	3: [17, 29],
	4: [36, 43],
	5: [16, 55],
	6: [22, 73],
	7: [50, 70],
	8: [82, 73],
	9: [86, 55],
	10: [66, 60],
	11: [84, 29],
	12: [64, 38],
};

function signNumberForHouse(houseNumber, ascSignNumber){
	return ((ascSignNumber + houseNumber - 2) % 12) + 1;
}

class IndiaNorthChart extends Component{
	renderObjects(objects, houseNumber){
		return (
			<div className="horosa-india-diagram-objects">
				{objects.map((obj, idx)=>(
					<span
						className="horosa-india-square-object"
						key={`${houseNumber}_${obj.id}_${idx}_${obj.lon}`}
						title={`${AstroText.AstroMsgCN[obj.id] || obj.name || obj.id} ${getObjectDegree(obj)}`}
						style={{ '--india-object-color': getObjectColor(obj) }}
					>
						<span className="horosa-india-square-object-name">{getObjectLabel(obj)}</span>
						<span className="horosa-india-square-object-degree">{getObjectDegree(obj)}</span>
						{Number(obj.lonspeed) < 0 ? <span className="horosa-india-square-retro">R</span> : null}
					</span>
				))}
			</div>
		);
	}

	renderHouse(houseNumber, ascSignNumber, objectsBySign, chartObj){
		const signNumber = signNumberForHouse(houseNumber, ascSignNumber);
		const objects = objectsBySign[signNumber] || [];
		const labelPos = NORTH_HOUSE_LABEL_POSITIONS[houseNumber];
		const signPos = NORTH_SIGN_BADGE_POSITIONS[houseNumber];
		const objectsPos = NORTH_OBJECT_ANCHOR_POSITIONS[houseNumber];
		const sign = SIGN_NAMES[signNumber];
		const signName = AstroText.AstroMsgCN[sign] || sign;
		const cuspDegree = getHouseCuspDegree(chartObj, houseNumber, signNumber);
		return (
			<div
				key={`north_house_${houseNumber}`}
				className="horosa-india-diagram-layer"
				title={`${ROMAN_HOUSES[houseNumber - 1]}宫 · ${signNumber} ${signName}`}
			>
				<div className="horosa-india-diagram-house" style={{ left: `${labelPos[0]}%`, top: `${labelPos[1]}%` }}>
					<div className="horosa-india-square-roman">{ROMAN_HOUSES[houseNumber - 1]}</div>
					{cuspDegree ? <div className="horosa-india-square-cusp">{cuspDegree}</div> : null}
				</div>
				<div className="horosa-india-diagram-sign" style={{ left: `${signPos[0]}%`, top: `${signPos[1]}%` }}>
					{signNumber}
				</div>
				<div className="horosa-india-diagram-object-anchor" style={{ left: `${objectsPos[0]}%`, top: `${objectsPos[1]}%` }}>
					{this.renderObjects(objects, houseNumber)}
				</div>
			</div>
		);
	}

	render(){
		const chartObj = this.props.value;
		const chartnum = this.props.chartnum || 1;
		const label = this.props.label || (chartnum === 1 ? '命盘' : `${chartnum}分盘`);
		const height = this.props.height || 720;
		if(!chartObj || !chartObj.chart || chartObj.err){
			return (
				<div className="horosa-india-square-shell" style={{ '--india-chart-height': `${height}px` }}>
					<div className="horosa-india-square-placeholder">等待排盘数据</div>
				</div>
			);
		}
		const ascSignNumber = getAscSignNumber(chartObj);
		const objectsBySign = getObjectsBySign(chartObj, this.props.planetDisplay, this.props.lotsDisplay);
		return (
			<div className="horosa-india-square-shell" style={{ '--india-chart-height': `${height}px` }}>
				<div className="horosa-india-square-board horosa-india-diagram-board horosa-india-north-board">
					<svg className="horosa-india-diagram-lines" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
						<rect x="0" y="0" width="100" height="100" />
						<polygon points="50,0 100,50 50,100 0,50" />
						<line x1="0" y1="0" x2="50" y2="50" />
						<line x1="100" y1="0" x2="50" y2="50" />
						<line x1="0" y1="100" x2="50" y2="50" />
						<line x1="100" y1="100" x2="50" y2="50" />
					</svg>
					{ROMAN_HOUSES.map((_, idx)=>this.renderHouse(idx + 1, ascSignNumber, objectsBySign, chartObj))}
					<div className="horosa-india-diagram-center">
						<div className="horosa-india-square-center-d">D{chartnum}</div>
						<div className="horosa-india-square-center-label">{label}</div>
						<div className="horosa-india-square-center-note">固定宫位 · 星座随升</div>
					</div>
				</div>
			</div>
		);
	}
}

export default IndiaNorthChart;
