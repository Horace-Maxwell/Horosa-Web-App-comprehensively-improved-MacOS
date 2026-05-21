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
	moiraPairedRadialText as pairedRadialText,
	moiraPoint as point,
	moiraRadialColumns as radialColumns,
	moiraRadialLine as radialLine,
	moiraVerticalText as verticalText,
	moiraGetZiGods as getZiGods,
	moiraBuildStellarRelations as buildStellarRelations,
	MOIRA_BIRTH_GOD_ORDER as BIRTH_GOD_ORDER,
} from './GuoLaoMoiraWheel';
import './GuoLaoMoiraWheel.less';

const PICK_RING_POS = [0.19, 0.31, 0.37, 0.43, 0.51, 0.54, 0.60, 0.68, 0.71, 0.77, 0.92, 0.95, 1.0];
const PICK_RING_DRAW_TYPE = [1, 0, 0, 0, 1, -10, 1, 1, -10, 2, 0, 1, -10];
const BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
const MOUNTAINS = ['子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳', '丙', '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥', '壬'];
const INNER_PAIR = ['土子', '土丑', '木寅', '火卯', '金辰', '水巳', '日午', '月未', '水申', '金酉', '火戌', '木亥'];
const HOUSE_LABEL = ['命宫', '相貌', '福德', '官禄', '迁移', '疾厄', '夫妻', '奴仆', '男女', '田宅', '兄弟', '财帛'];
const HOUSE_NUMBERS = ['1', '12', '11', '10', '9', '8', '7', '6', '5', '4', '3', '2'];

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

function shortPlanetLine(theta, inner, outer, dir, opt = {}){
	const span = Math.max(1, outer - inner);
	const length = Math.min(20, Math.max(9, span * 0.38));
	if(dir < 0){
		return radialLine(theta, inner, Math.min(outer, inner + length), opt);
	}
	return radialLine(theta, Math.max(inner, outer - length), outer, opt);
}

function listText(items, empty = '无'){
	const list = (items || []).filter(Boolean);
	return list.length ? list.join('、') : empty;
}

function yearSignRowForZi(rules, zi){
	const rows = rules && rules.natalYearStars ? rules.natalYearStars : [];
	return rows.find((row)=>row && row.zi === zi) || null;
}

class GuoLaoMoiraPickWheel extends Component{
	constructor(props){
		super(props);
		this.state = {
			tooltip: null,
			containerSide: 0,
		};
		this.containerRef = React.createRef();
		this.resizeObserver = null;
		this.measureContainer = this.measureContainer.bind(this);
		this.showTooltip = this.showTooltip.bind(this);
		this.moveTooltip = this.moveTooltip.bind(this);
		this.hideTooltip = this.hideTooltip.bind(this);
	}

	componentDidMount(){
		this.measureContainer();
		if(typeof ResizeObserver !== 'undefined' && this.containerRef.current){
			this.resizeObserver = new ResizeObserver(this.measureContainer);
			this.resizeObserver.observe(this.containerRef.current);
		}
		if(typeof window !== 'undefined'){
			window.addEventListener('resize', this.measureContainer);
		}
	}

	componentDidUpdate(prevProps){
		if(prevProps.height !== this.props.height){
			this.measureContainer();
		}
	}

	componentWillUnmount(){
		if(this.resizeObserver){
			this.resizeObserver.disconnect();
			this.resizeObserver = null;
		}
		if(typeof window !== 'undefined'){
			window.removeEventListener('resize', this.measureContainer);
		}
	}

	measureContainer(){
		const node = this.containerRef.current;
		if(!node){
			return;
		}
		const rect = node.getBoundingClientRect();
		const fallbackHeight = Number(this.props.height) || 740;
		const availableWidth = rect.width || node.clientWidth || fallbackHeight;
		const availableHeight = rect.height || node.clientHeight || fallbackHeight;
		const nextSide = Math.max(280, Math.floor(Math.min(availableWidth, availableHeight)));
		if(Number.isFinite(nextSide) && nextSide !== this.state.containerSide){
			this.setState({containerSide: nextSide});
		}
	}

	tooltipPoint(evt){
		const maxX = typeof window !== 'undefined' ? Math.max(12, window.innerWidth - 440) : evt.clientX + 14;
		const maxY = typeof window !== 'undefined' ? Math.max(12, window.innerHeight - 220) : evt.clientY + 16;
		return {
			x: Math.min(evt.clientX + 14, maxX),
			y: Math.min(evt.clientY + 16, maxY),
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
				{PICK_RING_POS.map((pos, idx)=>PICK_RING_DRAW_TYPE[idx] <= -10 ? null : (
					<circle
						key={`pick-ring-${idx}`}
						r={pos * R}
						className={PICK_RING_DRAW_TYPE[idx] === 1 || PICK_RING_DRAW_TYPE[idx] === 2 || idx === 0 || idx === 11 ? 'moira-ring-major' : 'moira-ring-minor'}
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
			const inner = major ? r(10) : (mid ? r(10) + (r(11) - r(10)) / 3 : r(10) + (r(11) - r(10)) * 2 / 3);
			nodes.push(
				<g key={`pick-degree-${degree}`}>
					{radialLine(theta, inner, r(11), {
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
		const p = point(r(11) + 30, theta);
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
		for(let ringIdx = 1; ringIdx < PICK_RING_DRAW_TYPE.length; ringIdx++){
			const drawType = PICK_RING_DRAW_TYPE[ringIdx];
			if(drawType <= 0 && drawType > -10){
				for(let i = 0; i < 12; i++){
					nodes.push(
						<g key={`pick-sector-${ringIdx}-${i}`}>
							{radialLine(pickThetaFromDegree(i * 30), r(ringIdx - 1), r(ringIdx), {color: BLACK, width: 0.95})}
						</g>
					);
				}
			}
			if(drawType === 2 || drawType === -11){
				for(let i = 0; i < 24; i++){
					nodes.push(
						<g key={`pick-sector24-${ringIdx}-${i}`}>
							{radialLine(pickThetaFromDegree(i * 15), r(ringIdx - 1), r(ringIdx), {color: BLACK, width: i % 2 === 0 ? 0.9 : 0.72})}
						</g>
					);
				}
			}
		}
		return <g className="moira-main-divider">{nodes}</g>;
	}

	renderDegreeMarkBand(inner, outer, keyPrefix, opt = {}){
		const nodes = [];
		const delta = (outer - inner) / 3;
		for(let degree = 0; degree < 360; degree++){
			const theta = pickThetaFromDegree(degree);
			const major = degree % 30 === 0;
			const mid = degree % 5 === 0;
			const anchorInner = opt.anchor === 'inner';
			const start = anchorInner ? inner : (major ? inner : (mid ? inner + delta : inner + 2 * delta));
			const end = anchorInner ? (major ? outer : (mid ? inner + 2 * delta : inner + delta)) : outer;
			const color = opt.mutedMajor ? BLACK : (major ? RED : BLACK);
			nodes.push(
				<g key={`${keyPrefix}-${degree}`}>
					{radialLine(theta, start, end, {
						color,
						width: major ? (opt.majorWidth || 0.8) : 0.6,
						opacity: opt.opacity === undefined ? (major ? 0.6 : 0.48) : opt.opacity,
					})}
				</g>
			);
		}
		return nodes;
	}

	renderStaticCore(){
		const nodes = [];
		const root = this.props.rootValue || {};
		const chart = this.props.value || root.chart || {};
		const ziGods = getZiGods(root, chart);
			for(let i = 0; i < 12; i++){
				const start = i * 30;
				const end = (i + 1) * 30;
				const theta = pickThetaFromDegree(sectorCenter(i, 12));
				const houseNameRadius = (r(2) + r(3)) / 2;
				const houseNumberRadius = (r(1) + r(2)) / 2;
				const gods = orderedGods(collectGods(ziGods, BRANCHES[i]), BIRTH_GOD_ORDER);
				const yearRow = yearSignRowForZi(this.props.moiraRules, BRANCHES[i]);
				const tip = [
					`${BRANCHES[i]}：${HOUSE_LABEL[i]}；同经：${INNER_PAIR[i]}`,
					yearRow ? `命曜：${yearRow.star || '—'} ${yearRow.shortName || ''}${yearRow.quality ? `；${yearRow.quality}` : ''}` : '',
					gods.length ? `神煞：${listText(gods)}` : '',
				].filter(Boolean).join('\n');
			nodes.push(
				<g key={`pick-static-${i}`}>
					<path
						className="moira-hover-zone"
						d={annularSectorPath(r(0), r(4), pickThetaFromDegree(start), pickThetaFromDegree(end))}
						{...this.tooltipHandlers(tip)}
					>
					</path>
						{radialLine(pickThetaFromDegree(start), r(0), r(3), {color: BLACK, width: 0.95})}
							{pairedRadialText(INNER_PAIR[i], theta, r(0), r(1), {size: 22, color: BLACK, weight: 600})}
							{horizontalRingText(HOUSE_NUMBERS[i], houseNumberRadius, theta, {size: 19, color: GREEN, weight: 600})}
							{horizontalRingText(HOUSE_LABEL[i], houseNameRadius, theta, {size: 19, color: GREEN, weight: 700})}
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
			nodes.push(
				<g key={`mountain-${i}`}>
					{horizontalRingText(MOUNTAINS[i], (r(8) + r(9)) / 2, theta, {size: 23, color: BLACK, weight: 500})}
				</g>
			);
		}
		return <g className="moira-pick-mountain-rings">{nodes}</g>;
	}

	renderStellarTicks(){
		const nodes = [
			...this.renderDegreeMarkBand(r(4), r(5), 'pick-stellar-up', {mutedMajor: true, opacity: 0.38, anchor: 'inner'}),
			...this.renderDegreeMarkBand(r(7), r(8), 'pick-stellar-down', {mutedMajor: true, opacity: 0.38, anchor: 'inner'}),
		];
		return <g className="moira-stellar-ticks">{nodes}</g>;
	}

	renderStellarRing(chart){
		const stars = buildFixedStars(chart);
		const relations = buildStellarRelations(chart);
		const nodes = [];
		stars.forEach((cur, idx)=>{
			const nxt = stars[(idx + 1) % stars.length];
			let span = Number(nxt.ra) - Number(cur.ra);
			if(span <= 0){
				span += 360;
			}
			const edgeTheta = pickThetaFromDegree(cur.ra);
			const centerTheta = pickThetaFromDegree(Number(cur.ra) + span / 2);
			const rel = relations[idx] || {};
			const tip = [
				`${cur.label || cur.name}：宿距 ${span.toFixed(2)}°`,
				`本命落入：${listText(rel.main)}`,
				`本命同经：${listText(rel.same)}`,
			].join('\n');
			nodes.push(
				<g key={`pick-stellar-${idx}`}>
					<path
						className="moira-hover-zone"
						d={annularSectorPath(r(4), r(5), pickThetaFromDegree(Number(cur.ra)), pickThetaFromDegree(Number(cur.ra) + span))}
						{...this.tooltipHandlers(tip)}
					>
					</path>
					{radialLine(edgeTheta, r(4) + 1, r(5) - 1, {color: RED, width: 1})}
					{horizontalRingText(cur.name || cur.label, (r(4) + r(5)) / 2, centerTheta, {size: 19, color: BLACK, weight: 600})}
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
			const tip = objectTooltip(item, opt.kind, this.props.moiraRules);
			return (
				<g key={`pick-${opt.kind}-planet-${item.id}-${idx}`}>
					<circle
						className="moira-hover-zone"
						cx={p.x}
						cy={p.y}
						r={Math.max(20, opt.size * 0.82)}
						{...this.tooltipHandlers(tip)}
					>
					</circle>
						{shortPlanetLine(markTheta, opt.markInner, opt.markOuter, opt.lineDir || 1, {color: opt.markColor, width: 1.05})}
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
						inner: r(3) + 7,
						outer: r(4) - 8,
						dir: -1,
						size: 25,
						color: GREEN,
							markColor: BLACK,
							markInner: r(3),
							markOuter: r(4),
							lineDir: 1,
						})}
					{this.renderPlanetRing(transitChart || birthChart, {
						kind: 'now',
						inner: r(6) + 6,
						outer: r(7) - 6,
					dir: 1,
					size: 23,
					color: BLUE,
						markColor: MAGENTA,
						markInner: r(6),
						markOuter: r(7),
						lineDir: 1,
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
		const side = this.state.containerSide || Math.min(height, 740);
		return (
			<div className="horosa-guolao-moira-wheel horosa-guolao-moira-pick-wheel" style={{height}} ref={this.containerRef}>
				<svg
					style={{width: side, height: side}}
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
