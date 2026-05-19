import React, { Component } from 'react';
import {
	MOIRA_WHEEL_R as R,
	MOIRA_WHEEL_VIEW as VIEW,
	MOIRA_BLACK as BLACK,
	MOIRA_GREEN as GREEN,
	MOIRA_BLUE as BLUE,
	MOIRA_RED as RED,
	MOIRA_MAGENTA as MAGENTA,
	MOIRA_PALE as PALE,
	moiraAnnularSectorPath as annularSectorPath,
	moiraBuildFixedStars as buildFixedStars,
	moiraCollectGods as collectGods,
	moiraGodColumnStep as godColumnStep,
	moiraGodTextSize as godTextSize,
	moiraHorizontalRingText as horizontalRingText,
	moiraObjectTooltip as objectTooltip,
	moiraOrderedGods as orderedGods,
	moiraPlanetColor as planetColor,
	moiraPlanetPlacements as planetPlacements,
	moiraPoint as point,
	moiraRadialColumns as radialColumns,
	moiraRadialLine as radialLine,
	moiraVerticalText as verticalText,
	moiraGetZiGods as getZiGods,
	MOIRA_BIRTH_GOD_ORDER as BIRTH_GOD_ORDER,
} from './GuoLaoMoiraWheel';
import './GuoLaoMoiraWheel.less';

const PICK_RING_POS = [0.19, 0.31, 0.37, 0.43, 0.51, 0.54, 0.60, 0.68, 0.71, 0.77, 0.92, 0.95, 1.0];
const BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
const MOUNTAINS = ['子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳', '丙', '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥', '壬'];
const INNER_SIGN = ['Aqu', 'Cap', 'Sag', 'Sco', 'Lib', 'Vir', 'Leo', 'Can', 'Gem', 'Tau', 'Ari', 'Pis'];
const INNER_PAIR = ['土子', '土丑', '木寅', '火卯', '金辰', '水巳', '日午', '月未', '水申', '金酉', '火戌', '木亥'];
const HOUSE_LABEL = ['德福', '相貌', '命宫', '财帛', '兄弟', '田宅', '男女', '奴仆', '夫妻', '疾厄', '迁移', '官禄'];
const STEM_BRANCHES = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸', '甲', '乙'];

function r(idx){
	return PICK_RING_POS[idx] * R;
}

function pickThetaFromDegree(degree){
	return 90 + Number(degree || 0);
}

function tangentRotate(theta){
	let rotate = theta + 90;
	if(rotate > 90 || rotate < -90){
		rotate += 180;
	}
	return rotate;
}

function sectorCenter(index, parts){
	return (index + 0.5) * (360 / parts);
}

class GuoLaoMoiraPickWheel extends Component{
	constructor(props){
		super(props);
		this.state = {tooltip: null};
		this.containerRef = React.createRef();
		this.showTooltip = this.showTooltip.bind(this);
		this.moveTooltip = this.moveTooltip.bind(this);
		this.hideTooltip = this.hideTooltip.bind(this);
	}

	tooltipPoint(evt){
		const box = this.containerRef.current ? this.containerRef.current.getBoundingClientRect() : {left: 0, top: 0};
		return {
			x: evt.clientX - box.left + 14,
			y: evt.clientY - box.top + 16,
		};
	}

	showTooltip(text, evt){
		if(!text){
			return;
		}
		this.setState({tooltip: {...this.tooltipPoint(evt), text}});
	}

	moveTooltip(evt){
		if(!this.state.tooltip){
			return;
		}
		this.setState({tooltip: {...this.state.tooltip, ...this.tooltipPoint(evt)}});
	}

	hideTooltip(){
		if(this.state.tooltip){
			this.setState({tooltip: null});
		}
	}

	tooltipHandlers(text){
		return {
			onMouseEnter: (evt)=>this.showTooltip(text, evt),
			onMouseOver: (evt)=>this.showTooltip(text, evt),
			onMouseMove: this.moveTooltip,
			onMouseLeave: this.hideTooltip,
			onMouseOut: this.hideTooltip,
			onPointerEnter: (evt)=>this.showTooltip(text, evt),
			onPointerMove: this.moveTooltip,
			onPointerLeave: this.hideTooltip,
			onClick: (evt)=>this.showTooltip(text, evt),
		};
	}

	renderRings(){
		return (
			<g className="moira-rings">
				{PICK_RING_POS.map((pos, idx)=>(
					<circle
						key={`pick-ring-${idx}`}
						r={pos * R}
						className={idx === 0 || idx === 4 || idx === 6 || idx === 9 || idx === 12 ? 'moira-ring-major' : 'moira-ring-minor'}
					/>
				))}
			</g>
		);
	}

	renderDegreeTicks(){
		const nodes = [];
		for(let degree = 0; degree < 360; degree++){
			const theta = pickThetaFromDegree(degree);
			const major = degree % 15 === 0;
			const mid = degree % 5 === 0;
			const inner = major ? r(11) - 4 : (mid ? r(11) + 1 : r(11) + 8);
			nodes.push(
				<g key={`pick-degree-${degree}`}>
					{radialLine(theta, inner, r(12), {
						color: major ? RED : BLACK,
						width: major ? 1.15 : 0.75,
					})}
					{major ? this.renderDegreeLabel(degree, theta) : null}
				</g>
			);
		}
		return <g className="moira-degree-ticks moira-pick-degree-ticks">{nodes}</g>;
	}

	renderDegreeLabel(degree, theta){
		const p = point(r(12) + 28, theta);
		return (
			<text
				x={p.x}
				y={p.y}
				fill={BLACK}
				fontSize={degree % 90 === 0 ? 25 : 20}
				fontWeight={degree % 90 === 0 ? 600 : 400}
				textAnchor="middle"
				dominantBaseline="central"
				transform={`rotate(${tangentRotate(theta)} ${p.x} ${p.y})`}
			>
				{degree}
			</text>
		);
	}

	renderSectorLines(){
		const nodes = [];
		for(let i = 0; i < 12; i++){
			const theta = pickThetaFromDegree(i * 30);
			nodes.push(
				<g key={`pick-sector-${i}`}>
					{radialLine(theta, r(0), r(4), {color: BLACK, width: 1})}
					{radialLine(theta, r(7), r(10), {color: BLACK, width: 1})}
				</g>
			);
		}
		for(let i = 0; i < 24; i++){
			const theta = pickThetaFromDegree(i * 15);
			nodes.push(
				<g key={`pick-mountain-sector-${i}`}>
					{radialLine(theta, r(7), r(9), {color: BLACK, width: i % 2 === 0 ? 0.9 : 0.7})}
				</g>
			);
		}
		return <g className="moira-main-divider">{nodes}</g>;
	}

	renderStaticCore(){
		const nodes = [];
		for(let i = 0; i < 12; i++){
			const start = i * 30;
			const end = (i + 1) * 30;
			const theta = pickThetaFromDegree(sectorCenter(i, 12));
			const tip = `${BRANCHES[i]}：${HOUSE_LABEL[i]}；同经：${INNER_PAIR[i]}`;
			nodes.push(
				<g key={`pick-static-${i}`}>
					<path
						className="moira-hover-zone"
						d={annularSectorPath(r(0), r(4), pickThetaFromDegree(start), pickThetaFromDegree(end))}
						{...this.tooltipHandlers(tip)}
					>
						<title>{tip}</title>
					</path>
					{radialLine(pickThetaFromDegree(start), r(0), r(4), {color: BLACK, width: 0.95})}
					{verticalText(INNER_PAIR[i], ...Object.values(point((r(0) + r(1)) / 2, theta)), {size: 25, maxPerCol: 2, color: BLACK, weight: 600})}
					{horizontalRingText(INNER_SIGN[i], (r(1) + r(2)) / 2, theta, {size: 29, color: BLACK, weight: 400})}
					{verticalText(HOUSE_LABEL[i], ...Object.values(point((r(2) + r(4)) / 2, theta)), {size: 25, maxPerCol: 2, color: GREEN, weight: 700})}
				</g>
			);
		}
		return (
			<g className="moira-static-twelve moira-pick-static-core">
				{nodes}
				<circle r={r(0)} fill="#fff" stroke={BLACK} strokeWidth="1" />
				{radialLine(pickThetaFromDegree(180), r(0) + 10, r(4) - 5, {color: RED, width: 2.4})}
				{radialLine(pickThetaFromDegree(0), r(0) + 10, r(1) + 8, {color: RED, width: 2.4})}
			</g>
		);
	}

	renderMountainRings(){
		const nodes = [];
		for(let i = 0; i < 24; i++){
			const theta = pickThetaFromDegree(sectorCenter(i, 24));
			const p = point((r(8) + r(9)) / 2, theta);
			nodes.push(
				<text key={`mountain-${i}`} x={p.x} y={p.y} fill={BLACK} fontSize="23" textAnchor="middle" dominantBaseline="central">
					{MOUNTAINS[i]}
				</text>
			);
		}
		for(let i = 0; i < 12; i++){
			const theta = pickThetaFromDegree(sectorCenter(i, 12));
			const pBranch = point((r(7) + r(8)) / 2, theta);
			const pStem = point((r(6) + r(7)) / 2, theta);
			nodes.push(
				<g key={`branch-ring-${i}`}>
					<text x={pBranch.x} y={pBranch.y} fill={BLACK} fontSize="25" textAnchor="middle" dominantBaseline="central">{BRANCHES[i]}</text>
					<text x={pStem.x} y={pStem.y} fill={BLACK} fontSize="22" textAnchor="middle" dominantBaseline="central">{STEM_BRANCHES[i]}</text>
				</g>
			);
		}
		return <g className="moira-pick-mountain-rings">{nodes}</g>;
	}

	renderStellarTicks(){
		const nodes = [];
		for(let degree = 0; degree < 360; degree++){
			const theta = pickThetaFromDegree(degree);
			const major = degree % 5 === 0;
			const tickLen = major ? 7 : 4;
			const width = major ? 0.72 : 0.42;
			nodes.push(
				<g key={`pick-stellar-tick-${degree}`}>
					{radialLine(theta, r(6) - tickLen, r(6), {color: BLACK, width})}
					{radialLine(theta, r(5), r(5) + tickLen, {color: BLACK, width})}
				</g>
			);
		}
		return <g className="moira-stellar-ticks">{nodes}</g>;
	}

	renderStellarRing(chart){
		const stars = buildFixedStars(chart);
		const nodes = [];
		stars.forEach((cur, idx)=>{
			const nxt = stars[(idx + 1) % stars.length];
			let span = Number(nxt.ra) - Number(cur.ra);
			if(span <= 0){
				span += 360;
			}
			const edgeTheta = pickThetaFromDegree(cur.ra);
			const centerTheta = pickThetaFromDegree(Number(cur.ra) + span / 2);
			const p = point((r(4) + r(6)) / 2, centerTheta);
			const tip = `${cur.label || cur.name}：宿距 ${span.toFixed(2)}°`;
			nodes.push(
				<g key={`pick-stellar-${idx}`}>
					<path
						className="moira-hover-zone"
						d={annularSectorPath(r(4), r(6), pickThetaFromDegree(Number(cur.ra)), pickThetaFromDegree(Number(cur.ra) + span))}
						{...this.tooltipHandlers(tip)}
					>
						<title>{tip}</title>
					</path>
					{radialLine(edgeTheta, r(4) + 1, r(6) - 1, {color: RED, width: 1})}
					{verticalText(cur.name || cur.label, p.x, p.y, {size: 22, maxPerCol: 1, color: BLACK, weight: 600})}
				</g>
			);
		});
		return <g className="moira-stellar-layer">{nodes}</g>;
	}

	renderPlanetRing(chart, opt){
		const placements = planetPlacements(chart, opt.inner, opt.outer, opt.dir, opt.size);
		const nodes = placements.map((item, idx)=>{
			const markTheta = pickThetaFromDegree(item.degree);
			const labelTheta = pickThetaFromDegree(item.labelDegree);
			const p = point(item.radius, labelTheta);
			const tip = objectTooltip(item, opt.kind);
			return (
				<g key={`pick-${opt.kind}-planet-${item.id}-${idx}`}>
					<circle
						className="moira-hover-zone"
						cx={p.x}
						cy={p.y}
						r={Math.max(20, opt.size * 0.82)}
						{...this.tooltipHandlers(tip)}
					>
						<title>{tip}</title>
					</circle>
					{radialLine(markTheta, opt.markInner, opt.markOuter, {color: opt.markColor, width: 1.05})}
					{verticalText(item.label, p.x, p.y, {
						size: opt.size,
						maxPerCol: 1,
						color: planetColor(item.obj, opt.color),
						weight: 600,
					})}
				</g>
			);
		});
		return <g className={`moira-planet-layer moira-pick-planet-layer-${opt.kind}`}>{nodes}</g>;
	}

	renderPlanetLayers(birthChart, transitChart){
		return (
			<g>
				{this.renderPlanetRing(birthChart, {
					kind: 'birth',
					inner: r(4) + 8,
					outer: r(5) - 8,
					dir: -1,
					size: 29,
					color: GREEN,
					markColor: BLACK,
					markInner: r(4),
					markOuter: r(5),
				})}
				{this.renderPlanetRing(transitChart || birthChart, {
					kind: 'now',
					inner: r(6) + 10,
					outer: r(7) - 8,
					dir: 1,
					size: 29,
					color: BLUE,
					markColor: MAGENTA,
					markInner: r(6),
					markOuter: r(7),
				})}
			</g>
		);
	}

	renderGodRing(root, chart){
		const ziGods = getZiGods(root, chart);
		const nodes = [];
		for(let i = 0; i < 12; i++){
			const start = i * 30;
			const end = (i + 1) * 30;
			const theta = pickThetaFromDegree(sectorCenter(i, 12));
			const gods = orderedGods(collectGods(ziGods, BRANCHES[i]), BIRTH_GOD_ORDER);
			const godSize = Math.min(25, godTextSize(gods.length));
			const godSteps = godColumnStep(gods.length);
			const tip = `${BRANCHES[i]}：天星择日神煞${gods.length ? `｜${gods.join('，')}` : '｜无'}`;
			nodes.push(
				<g key={`pick-god-${i}`}>
					<path
						className="moira-hover-zone"
						d={annularSectorPath(r(9), r(10), pickThetaFromDegree(start), pickThetaFromDegree(end))}
						{...this.tooltipHandlers(tip)}
					>
						<title>{tip}</title>
					</path>
					{radialColumns(gods, theta, r(9) + 10, r(10) - 12, {
						size: godSize,
						color: GREEN,
						weight: 600,
						arc: godSteps.arc,
						minStep: godSteps.minStep,
						maxStep: godSteps.maxStep,
						fitArc: true,
					})}
				</g>
			);
		}
		return <g className="moira-star-table-layer moira-pick-god-layer">{nodes}</g>;
	}

	renderTooltip(){
		const tooltip = this.state.tooltip;
		if(!tooltip){
			return null;
		}
		return (
			<div
				className="horosa-guolao-moira-tooltip"
				style={{left: tooltip.x, top: tooltip.y}}
			>
				{tooltip.text}
			</div>
		);
	}

	render(){
		const root = this.props.rootValue || {};
		const chart = this.props.value || root.chart || {};
		const transitRoot = this.props.transitValue || {};
		const transitChart = transitRoot.chart || null;
		const height = this.props.height || 740;
		return (
			<div className="horosa-guolao-moira-wheel horosa-guolao-moira-pick-wheel" style={{height}} ref={this.containerRef}>
				<svg
					viewBox={`${-VIEW / 2} ${-VIEW / 2} ${VIEW} ${VIEW}`}
					role="img"
					aria-label="Moira天星择日盘"
				>
					<rect x={-VIEW / 2} y={-VIEW / 2} width={VIEW} height={VIEW} fill="#fff" />
					<g className="moira-pale-guides">
						{Array.from({length: 24}).map((_, idx)=>(
							<g key={`pick-guide-${idx}`}>{radialLine(pickThetaFromDegree(idx * 15), r(7), r(10), {color: PALE, width: 0.55, opacity: 0.18})}</g>
						))}
					</g>
					{this.renderRings()}
					{this.renderSectorLines()}
					{this.renderDegreeTicks()}
					{this.renderStellarTicks()}
					{this.renderStaticCore()}
					{this.renderStellarRing(chart)}
					{this.renderPlanetLayers(chart, transitChart)}
					{this.renderMountainRings()}
					{this.renderGodRing(root, chart)}
				</svg>
				{this.renderTooltip()}
			</div>
		);
	}
}

export default GuoLaoMoiraPickWheel;
