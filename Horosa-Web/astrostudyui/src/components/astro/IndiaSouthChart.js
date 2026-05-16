import { Component } from 'react';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import { splitDegree } from './AstroHelper';
import '../../css/styles.less';

const SOUTH_INDIAN_SIGN_GRID = [
	[12, 1, 2, 3],
	[11, null, null, 4],
	[10, null, null, 5],
	[9, 8, 7, 6],
];

export const SIGN_NAMES = {
	1: AstroConst.ARIES,
	2: AstroConst.TAURUS,
	3: AstroConst.GEMINI,
	4: AstroConst.CANCER,
	5: AstroConst.LEO,
	6: AstroConst.VIRGO,
	7: AstroConst.LIBRA,
	8: AstroConst.SCORPIO,
	9: AstroConst.SAGITTARIUS,
	10: AstroConst.CAPRICORN,
	11: AstroConst.AQUARIUS,
	12: AstroConst.PISCES,
};

export const ROMAN_HOUSES = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'];

const INDIA_PLANET_LABELS = {
	[AstroConst.SUN]: 'Su',
	[AstroConst.MOON]: 'Mo',
	[AstroConst.MERCURY]: 'Me',
	[AstroConst.VENUS]: 'Ve',
	[AstroConst.MARS]: 'Ma',
	[AstroConst.JUPITER]: 'Ju',
	[AstroConst.SATURN]: 'Sa',
	[AstroConst.NORTH_NODE]: 'Ra',
	[AstroConst.SOUTH_NODE]: 'Ke',
	[AstroConst.URANUS]: 'Ur',
	[AstroConst.NEPTUNE]: 'Ne',
	[AstroConst.PLUTO]: 'Pl',
	[AstroConst.CHIRON]: 'Ch',
	[AstroConst.DARKMOON]: 'Li',
	[AstroConst.PURPLE_CLOUDS]: 'Zi',
	[AstroConst.ASC]: 'As',
	[AstroConst.DESC]: 'Ds',
	[AstroConst.MC]: 'MC',
	[AstroConst.IC]: 'IC',
};

export function normalizeDegree(lon){
	const num = Number(lon);
	if(!Number.isFinite(num)){
		return 0;
	}
	return ((num % 360) + 360) % 360;
}

function getSignNumberFromSign(sign){
	const idx = AstroConst.LIST_SIGNS.indexOf(sign);
	if(idx >= 0){
		return idx + 1;
	}
	return null;
}

export function getSignNumber(obj){
	if(!obj){
		return null;
	}
	const bySign = getSignNumberFromSign(obj.sign);
	if(bySign){
		return bySign;
	}
	if(obj.lon !== undefined && obj.lon !== null){
		return Math.floor(normalizeDegree(obj.lon) / 30) + 1;
	}
	return null;
}

export function getObject(chartObj, objid){
	if(!chartObj || !chartObj.chart || !Array.isArray(chartObj.chart.objects)){
		return null;
	}
	return chartObj.chart.objects.find((obj)=>obj.id === objid) || null;
}

export function getAscSignNumber(chartObj){
	const asc = getObject(chartObj, AstroConst.ASC);
	const ascSign = getSignNumber(asc);
	if(ascSign){
		return ascSign;
	}
	const houses = chartObj && chartObj.chart && Array.isArray(chartObj.chart.houses) ? chartObj.chart.houses : [];
	const house1 = houses.find((house)=>house.id === AstroConst.HOUSE1) || houses[0];
	const houseSign = getSignNumber(house1);
	if(houseSign){
		return houseSign;
	}
	if(house1 && house1.lon !== undefined && house1.lon !== null){
		return Math.floor(normalizeDegree(house1.lon) / 30) + 1;
	}
	return 1;
}

export function getHouseNumberForSign(signNumber, ascSignNumber){
	return ((signNumber - ascSignNumber + 12) % 12) + 1;
}

export function getObjectLabel(obj){
	if(!obj || !obj.id){
		return '';
	}
	if(INDIA_PLANET_LABELS[obj.id]){
		return INDIA_PLANET_LABELS[obj.id];
	}
	const cn = AstroText.AstroMsgCN[obj.id] || obj.name || obj.id;
	return `${cn}`.slice(0, 2);
}

export function getObjectDegree(obj){
	let value = obj && obj.signlon !== undefined && obj.signlon !== null ? obj.signlon : null;
	if(value === null && obj && obj.lon !== undefined && obj.lon !== null){
		value = normalizeDegree(obj.lon) % 30;
	}
	if(value === null){
		return '';
	}
	const degs = splitDegree(value);
	return `${degs[0]}°`;
}

function getDegreeText(value){
	if(value === undefined || value === null || value === ''){
		return '';
	}
	const num = Number(value);
	if(!Number.isFinite(num)){
		return '';
	}
	const degs = splitDegree(num);
	return `${degs[0]}°`;
}

export function getHouseCuspDegree(chartObj, houseNumber, signNumber){
	const houses = chartObj && chartObj.chart && Array.isArray(chartObj.chart.houses) ? chartObj.chart.houses : [];
	const house = houses.find((item)=>item.id === `House${houseNumber}`);
	if(!house){
		return '';
	}
	if(house.lon !== undefined && house.lon !== null){
		const normalizedLon = normalizeDegree(house.lon);
		const lonSignNumber = Math.floor(normalizedLon / 30) + 1;
		if(signNumber && lonSignNumber !== signNumber){
			return '';
		}
		return getDegreeText(normalizedLon % 30);
	}
	if(house.signlon !== undefined && house.signlon !== null){
		const houseSignNumber = getSignNumber(house);
		if(houseSignNumber && signNumber && houseSignNumber !== signNumber){
			return '';
		}
		return getDegreeText(house.signlon);
	}
	return '';
}

function buildDisplaySet(planetDisplay, lotsDisplay){
	const displaySet = new Set();
	if(Array.isArray(planetDisplay)){
		planetDisplay.forEach((id)=>displaySet.add(id));
	}
	if(Array.isArray(lotsDisplay)){
		lotsDisplay.forEach((id)=>displaySet.add(id));
	}
	return displaySet;
}

export function getObjectsBySign(chartObj, planetDisplay, lotsDisplay){
	if(!chartObj || !chartObj.chart){
		return {};
	}
	const displaySet = buildDisplaySet(planetDisplay, lotsDisplay);
	const shouldFilter = displaySet.size > 0;
	let objects = [];
	if(Array.isArray(chartObj.chart.objects)){
		objects = objects.concat(chartObj.chart.objects);
	}
	if(Array.isArray(chartObj.lots)){
		objects = objects.concat(chartObj.lots);
	}
	const bySign = {};
	objects.forEach((obj)=>{
		if(!obj || !obj.id){
			return;
		}
		if(shouldFilter && !displaySet.has(obj.id)){
			return;
		}
		const signNumber = getSignNumber(obj);
		if(!signNumber){
			return;
		}
		if(!bySign[signNumber]){
			bySign[signNumber] = [];
		}
		bySign[signNumber].push(obj);
	});
	Object.keys(bySign).forEach((key)=>{
		bySign[key].sort((a, b)=>{
			const aLon = a.signlon !== undefined && a.signlon !== null ? Number(a.signlon) : normalizeDegree(a.lon) % 30;
			const bLon = b.signlon !== undefined && b.signlon !== null ? Number(b.signlon) : normalizeDegree(b.lon) % 30;
			return aLon - bLon;
		});
	});
	return bySign;
}

export function getObjectColor(obj){
	if(!obj){
		return 'var(--horosa-accent-strong, #2167d4)';
	}
	return AstroConst.AstroColor[obj.id]
		|| AstroConst.AstroColor[obj.sign]
		|| 'var(--horosa-accent-strong, #2167d4)';
}

class IndiaSouthChart extends Component{
	renderObject(obj, idx){
		const retro = obj && Number(obj.lonspeed) < 0;
		const label = getObjectLabel(obj);
		const degree = getObjectDegree(obj);
		const titleName = AstroText.AstroMsgCN[obj.id] || obj.name || obj.id;
		return (
			<span
				className="horosa-india-square-object"
				key={`${obj.id}_${idx}_${obj.lon}`}
				title={`${titleName} ${degree}${retro ? ' 逆行' : ''}`}
				style={{ '--india-object-color': getObjectColor(obj) }}
			>
				<span className="horosa-india-square-object-name">{label}</span>
				<span className="horosa-india-square-object-degree">{degree}</span>
				{retro ? <span className="horosa-india-square-retro">R</span> : null}
			</span>
		);
	}

	renderCell(signNumber, rowIndex, colIndex, ascSignNumber, objectsBySign, chartObj){
		const sign = SIGN_NAMES[signNumber];
		const houseNumber = getHouseNumberForSign(signNumber, ascSignNumber);
		const objects = objectsBySign[signNumber] || [];
		const signName = AstroText.AstroMsgCN[sign] || sign;
		const cuspDegree = getHouseCuspDegree(chartObj, houseNumber, signNumber);
		const isAscCell = houseNumber === 1;
		return (
			<div
				key={`india_sign_${signNumber}`}
				className={`horosa-india-square-cell${isAscCell ? ' horosa-india-square-cell-asc' : ''}`}
				style={{
					gridColumn: colIndex + 1,
					gridRow: rowIndex + 1,
				}}
				title={`${signNumber} ${signName} · 第${houseNumber}宫`}
			>
				<div className="horosa-india-square-house">
					<div className="horosa-india-square-roman">{ROMAN_HOUSES[houseNumber - 1]}</div>
					{cuspDegree ? <div className="horosa-india-square-cusp">{cuspDegree}</div> : null}
				</div>
				<div className="horosa-india-square-objects">
					{objects.map((obj, idx)=>this.renderObject(obj, idx))}
				</div>
				<div className="horosa-india-square-sign" aria-label={`${signNumber} ${signName}`}>
					{signNumber}
				</div>
			</div>
		);
	}

	renderCells(ascSignNumber, objectsBySign, chartObj){
		const cells = [];
		SOUTH_INDIAN_SIGN_GRID.forEach((row, rowIndex)=>{
			row.forEach((signNumber, colIndex)=>{
				if(!signNumber){
					return;
				}
				cells.push(this.renderCell(signNumber, rowIndex, colIndex, ascSignNumber, objectsBySign, chartObj));
			});
		});
		return cells;
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
				<div className="horosa-india-square-board xq-india-board">
					{this.renderCells(ascSignNumber, objectsBySign, chartObj)}
					<div className="horosa-india-square-center">
						<div className="horosa-india-square-center-d">D{chartnum}</div>
						<div className="horosa-india-square-center-label">{label}</div>
						<div className="horosa-india-square-center-note">固定星座 · 顺时宫位</div>
					</div>
				</div>
			</div>
		);
	}
}

export default IndiaSouthChart;
