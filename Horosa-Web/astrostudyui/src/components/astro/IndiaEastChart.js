import { Component } from 'react';
import * as AstroText from '../../constants/AstroText';
import {
	ROMAN_HOUSES,
	SIGN_NAMES,
	getAscSignNumber,
	getHouseCuspDegree,
	getHouseNumberForSign,
	getObjectColor,
	getObjectDegree,
	getObjectLabel,
	getObjectsBySign,
} from './IndiaSouthChart';
import '../../css/styles.less';

const EAST_HOUSE_LABEL_POSITIONS = {
	1: [50, 6],
	2: [5, 7],
	3: [5, 13],
	4: [7, 50],
	5: [6, 86],
	6: [9, 95],
	7: [50, 95],
	8: [94, 95],
	9: [95, 86],
	10: [94, 50],
	11: [95, 13],
	12: [94, 7],
};

const EAST_SIGN_BADGE_POSITIONS = {
	1: [50, 30],
	2: [32, 30],
	3: [29, 33],
	4: [29, 50],
	5: [29, 70],
	6: [32, 73],
	7: [50, 72],
	8: [68, 73],
	9: [71, 70],
	10: [70, 50],
	11: [71, 33],
	12: [68, 30],
};

const EAST_OBJECT_ANCHOR_POSITIONS = {
	1: [50, 18],
	2: [29, 18],
	3: [16, 20],
	4: [18, 50],
	5: [18, 72],
	6: [22, 82],
	7: [50, 83],
	8: [76, 82],
	9: [84, 72],
	10: [82, 50],
	11: [84, 28],
	12: [76, 20],
};

class IndiaEastChart extends Component{
	renderObjects(objects, signNumber){
		return (
			<div className="horosa-india-diagram-objects">
				{objects.map((obj, idx)=>(
					<span
						className="horosa-india-square-object"
						key={`${signNumber}_${obj.id}_${idx}_${obj.lon}`}
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

	renderSign(signNumber, ascSignNumber, objectsBySign, chartObj){
		const houseNumber = getHouseNumberForSign(signNumber, ascSignNumber);
		const objects = objectsBySign[signNumber] || [];
		const housePos = EAST_HOUSE_LABEL_POSITIONS[signNumber];
		const signPos = EAST_SIGN_BADGE_POSITIONS[signNumber];
		const objectsPos = EAST_OBJECT_ANCHOR_POSITIONS[signNumber];
		const sign = SIGN_NAMES[signNumber];
		const signName = AstroText.AstroMsgCN[sign] || sign;
		const cuspDegree = getHouseCuspDegree(chartObj, houseNumber, signNumber);
		return (
			<div
				key={`east_sign_${signNumber}`}
				className="horosa-india-diagram-layer"
				title={`${signNumber} ${signName} · ${ROMAN_HOUSES[houseNumber - 1]}宫`}
			>
				<div className="horosa-india-diagram-house" style={{ left: `${housePos[0]}%`, top: `${housePos[1]}%` }}>
					<div className="horosa-india-square-roman">{ROMAN_HOUSES[houseNumber - 1]}</div>
					{cuspDegree ? <div className="horosa-india-square-cusp">{cuspDegree}</div> : null}
				</div>
				<div className="horosa-india-diagram-sign" style={{ left: `${signPos[0]}%`, top: `${signPos[1]}%` }}>
					{signNumber}
				</div>
				<div className="horosa-india-diagram-object-anchor" style={{ left: `${objectsPos[0]}%`, top: `${objectsPos[1]}%` }}>
					{this.renderObjects(objects, signNumber)}
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
			<div className="horosa-india-square-shell xq-chart-renderer xq-chart-renderer-india" style={{ '--india-chart-height': `${height}px` }}>
				<div className="horosa-india-square-board horosa-india-diagram-board horosa-india-east-board xq-india-board">
					<svg className="horosa-india-diagram-lines" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
						<rect x="0" y="0" width="100" height="100" />
						<line x1="33.333" y1="0" x2="33.333" y2="33.333" />
						<line x1="66.667" y1="0" x2="66.667" y2="33.333" />
						<line x1="33.333" y1="66.667" x2="33.333" y2="100" />
						<line x1="66.667" y1="66.667" x2="66.667" y2="100" />
						<line x1="0" y1="33.333" x2="33.333" y2="33.333" />
						<line x1="66.667" y1="33.333" x2="100" y2="33.333" />
						<line x1="0" y1="66.667" x2="33.333" y2="66.667" />
						<line x1="66.667" y1="66.667" x2="100" y2="66.667" />
						<line x1="33.333" y1="0" x2="66.667" y2="0" />
						<line x1="33.333" y1="100" x2="66.667" y2="100" />
						<line x1="0" y1="0" x2="33.333" y2="33.333" />
						<line x1="100" y1="0" x2="66.667" y2="33.333" />
						<line x1="0" y1="100" x2="33.333" y2="66.667" />
						<line x1="100" y1="100" x2="66.667" y2="66.667" />
						<rect x="33.333" y="33.333" width="33.334" height="33.334" />
					</svg>
					{Object.keys(EAST_SIGN_BADGE_POSITIONS).map((signNumber)=>this.renderSign(Number(signNumber), ascSignNumber, objectsBySign, chartObj))}
					<div className="horosa-india-diagram-center">
						<div className="horosa-india-square-center-d">D{chartnum}</div>
						<div className="horosa-india-square-center-label">{label}</div>
						<div className="horosa-india-square-center-note">固定星座 · 顺时宫位</div>
					</div>
				</div>
			</div>
		);
	}
}

export default IndiaEastChart;
