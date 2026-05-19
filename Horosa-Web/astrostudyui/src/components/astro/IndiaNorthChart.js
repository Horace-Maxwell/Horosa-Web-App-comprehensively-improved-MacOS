import { Component } from 'react';
import * as AstroText from '../../constants/AstroText';
import {
	HOUSE_LABELS,
	SIGN_NAMES,
	getAscSignNumber,
	getHouseCuspDegree,
	getHouseLabel,
	getObjectColor,
	getObjectDegree,
	getObjectLabel,
	getObjectsBySign,
	getSignSymbol,
} from './IndiaSouthChart';
import '../../css/styles.less';

const NORTH_HOUSE_LABEL_POSITIONS = {
	1: [50, 6],
	2: [14, 3],
	3: [5, 10],
	4: [8, 50],
	5: [6, 79],
	6: [15, 96],
	7: [50, 84],
	8: [85, 96],
	9: [94, 79],
	10: [92, 50],
	11: [95, 10],
	12: [90, 3],
};

const NORTH_SIGN_BADGE_POSITIONS = {
	1: [50, 40],
	2: [27, 22],
	3: [9, 31],
	4: [40, 50],
	5: [10, 72],
	6: [18, 84],
	7: [50, 60],
	8: [82, 84],
	9: [90, 72],
	10: [60, 50],
	11: [91, 31],
	12: [73, 22],
};

const NORTH_OBJECT_ANCHOR_POSITIONS = {
	1: [50, 24, 30, 14],
	2: [34, 15, 24, 14],
	3: [18, 24, 17, 18],
	4: [35, 42, 22, 18],
	5: [18, 68, 16, 18],
	6: [26, 81, 14, 16],
	7: [50, 73, 30, 16],
	8: [74, 81, 14, 16],
	9: [82, 68, 16, 18],
	10: [65, 42, 22, 18],
	11: [82, 24, 17, 18],
	12: [66, 15, 24, 14],
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
				title={`第${houseNumber}宫 · ${signName}`}
			>
				<div className="horosa-india-diagram-house horosa-india-diagram-house-corner" style={{ left: `${labelPos[0]}%`, top: `${labelPos[1]}%` }}>
					<div className="horosa-india-square-roman">{getHouseLabel(houseNumber)}</div>
					{cuspDegree ? <div className="horosa-india-square-cusp">{cuspDegree}</div> : null}
				</div>
				<div className="horosa-india-diagram-sign horosa-india-diagram-sign-corner" aria-label={`${signNumber} ${signName}`} style={{ left: `${signPos[0]}%`, top: `${signPos[1]}%` }}>
					<span className="horosa-india-square-sign-symbol">{getSignSymbol(signNumber)}</span>
				</div>
				<div
					className="horosa-india-diagram-object-anchor horosa-india-diagram-object-anchor-roomy"
					data-house={houseNumber}
					style={{ left: `${objectsPos[0]}%`, top: `${objectsPos[1]}%`, width: `${objectsPos[2]}%`, height: `${objectsPos[3]}%` }}
				>
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
			<div className="horosa-india-square-shell xq-chart-renderer xq-chart-renderer-india" style={{ '--india-chart-height': `${height}px` }}>
				<div className="horosa-india-square-board horosa-india-diagram-board horosa-india-north-board xq-india-board">
					<svg className="horosa-india-diagram-lines" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
						<rect x="0" y="0" width="100" height="100" />
						<polygon points="50,0 100,50 50,100 0,50" />
						<line x1="0" y1="0" x2="50" y2="50" />
						<line x1="100" y1="0" x2="50" y2="50" />
						<line x1="0" y1="100" x2="50" y2="50" />
						<line x1="100" y1="100" x2="50" y2="50" />
					</svg>
					{HOUSE_LABELS.map((_, idx)=>this.renderHouse(idx + 1, ascSignNumber, objectsBySign, chartObj))}
					<div className="horosa-india-diagram-center horosa-india-diagram-center-compact">
						<div className="horosa-india-square-center-d">D{chartnum}</div>
					</div>
				</div>
			</div>
		);
	}
}

export default IndiaNorthChart;
