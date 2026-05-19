import { Component } from 'react';
import * as AstroText from '../../constants/AstroText';
import {
	SIGN_NAMES,
	getAscSignNumber,
	getHouseCuspDegree,
	getHouseLabel,
	getHouseNumberForSign,
	getObjectColor,
	getObjectDegree,
	getObjectLabel,
	getObjectsBySign,
	getSignSymbol,
} from './IndiaSouthChart';
import '../../css/styles.less';

const EAST_HOUSE_LABEL_POSITIONS = {
	1: [50, 7],
	2: [7, 82],
	3: [18, 93],
	4: [50, 93],
	5: [82, 92],
	6: [93, 82],
	7: [93, 50],
	8: [93, 18],
	9: [82, 7],
	10: [7, 50],
	11: [18, 7],
	12: [7, 18],
};

const EAST_SIGN_BADGE_POSITIONS = {
	1: [50, 21],
	2: [18, 73],
	3: [27, 88],
	4: [50, 82],
	5: [73, 88],
	6: [82, 73],
	7: [82, 50],
	8: [82, 27],
	9: [73, 12],
	10: [18, 50],
	11: [27, 12],
	12: [18, 27],
};

const EAST_OBJECT_ANCHOR_POSITIONS = {
	1: [50, 24, 28, 14],
	2: [18, 74, 22, 14],
	3: [22, 82, 22, 14],
	4: [50, 77, 28, 14],
	5: [82, 82, 22, 14],
	6: [82, 74, 22, 14],
	7: [77, 50, 24, 22],
	8: [82, 26, 22, 14],
	9: [78, 18, 22, 14],
	10: [23, 50, 24, 22],
	11: [18, 18, 22, 16],
	12: [18, 26, 22, 14],
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
				title={`${signName} · 第${houseNumber}宫`}
			>
				<div className="horosa-india-diagram-house horosa-india-diagram-house-corner" style={{ left: `${housePos[0]}%`, top: `${housePos[1]}%` }}>
					<div className="horosa-india-square-roman">{getHouseLabel(houseNumber)}</div>
					{cuspDegree ? <div className="horosa-india-square-cusp">{cuspDegree}</div> : null}
				</div>
				<div className="horosa-india-diagram-sign horosa-india-diagram-sign-corner" aria-label={`${signNumber} ${signName}`} style={{ left: `${signPos[0]}%`, top: `${signPos[1]}%` }}>
					<span className="horosa-india-square-sign-symbol">{getSignSymbol(signNumber)}</span>
				</div>
				<div
					className="horosa-india-diagram-object-anchor horosa-india-diagram-object-anchor-roomy"
					data-sign={signNumber}
					style={{ left: `${objectsPos[0]}%`, top: `${objectsPos[1]}%`, width: `${objectsPos[2]}%`, height: `${objectsPos[3]}%` }}
				>
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
					<div className="horosa-india-diagram-center horosa-india-diagram-center-compact">
						<div className="horosa-india-square-center-d">D{chartnum}</div>
					</div>
				</div>
			</div>
		);
	}
}

export default IndiaEastChart;
