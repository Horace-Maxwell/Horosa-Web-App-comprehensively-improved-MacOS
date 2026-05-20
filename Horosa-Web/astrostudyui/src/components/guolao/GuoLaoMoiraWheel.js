import React, { Component } from 'react';
import * as AstroConst from '../../constants/AstroConst';
import { GUOLAO_LIFE_MODE_COTRANS, GUOLAO_LIFE_MODE_YUMAO, getStoredGuolaoLifeMode, normalizeGuolaoLifeMode, } from './GuoLaoChartStyle';
import './GuoLaoMoiraWheel.less';

const R = 560;
const VIEW = 1220;
const RING_POS = [0.10, 0.22, 0.28, 0.34, 0.43, 0.45, 0.51, 0.53, 0.62, 0.77, 0.92, 0.95, 1.0];
const RING_DRAW_TYPE = [1, 0, 0, 0, 1, -10, -10, 1, 1, 0, 0, 1, -10];
const LIMIT_SEQ = [11.0, 10.0, 11.0, 15.0, 8.0, 7.0, 11.0, 4.5, 4.5, 4.5, 5.0, 5.0];

const BLACK = '#000000';
const GREEN = '#008000';
const BLUE = '#000080';
const RED = '#ff0000';
const MAGENTA = '#ff00ff';
const NOW_MARK = '#804040';
const PALE = '#b5d8c7';
const STELLAR_TICK_INNER = 5;
const STELLAR_TICK_OUTER = 6;
const GOD_RING_INNER = 8;
const GOD_RING_OUTER = 10;

const TWELVE_SIGNS = ['酉', '申', '未', '午', '巳', '辰', '卯', '寅', '丑', '子', '亥', '戌'];
const RING1 = ['金酉', '水申', '月未', '日午', '水巳', '金辰', '火卯', '木寅', '土丑', '土子', '木亥', '火戌'];
const HOUSE_BRANCH = ['财帛', '兄弟', '田宅', '男女', '奴仆', '夫妻', '疾厄', '迁移', '官禄', '福德', '相貌', '命宫'];
const HOUSE_NUMBERS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '1'];
const SIGN_NAMES = ['白羊', '金牛', '双子', '巨蟹', '狮子', '处女', '天秤', '天蝎', '射手', '摩羯', '水瓶', '双鱼'];
const HALF_STELLAR = ['娄', '胃', '昴', '毕', '觜', '参', '井', '鬼', '柳', '星', '张', '翼', '轸', '角', '亢', '氐', '房', '心', '尾', '箕', '斗', '牛', '女', '虚', '危', '室', '壁', '奎'];
const FULL_STELLAR = ['娄金', '胃土', '昴日', '毕月', '觜火', '参水', '井木', '鬼金', '柳土', '星日', '张月', '翼火', '轸水', '角木', '亢金', '氐土', '房日', '心月', '尾火', '箕水', '斗木', '牛金', '女土', '虚日', '危月', '室火', '壁水', '奎木'];
const STEM_BRANCHES = ['甲子', '乙丑', '丙寅', '丁卯', '戊辰', '己巳', '庚午', '辛未', '壬申', '癸酉', '甲戌', '乙亥', '丙子', '丁丑', '戊寅', '己卯', '庚辰', '辛巳', '壬午', '癸未', '甲申', '乙酉', '丙戌', '丁亥', '戊子', '己丑', '庚寅', '辛卯', '壬辰', '癸巳', '甲午', '乙未', '丙申', '丁酉', '戊戌', '己亥', '庚子', '辛丑', '壬寅', '癸卯', '甲辰', '乙巳', '丙午', '丁未', '戊申', '己酉', '庚戌', '辛亥', '壬子', '癸丑', '甲寅', '乙卯', '丙辰', '丁巳', '戊午', '己未', '庚申', '辛酉', '壬戌', '癸亥'];
const BIRTH_GOD_ORDER = ['劫杀', '文昌', '禄勋', '大耗', '月杀', '咸池', '唐符', '天厨', '伏尸', '三刑', '勾神', '蓦越', '黄幡', '的杀', '孤辰', '天喜', '注受', '剑锋', '飞廉', '病符', '紫微', '华盖', '天贵', '六害', '孤虚', '游奕', '年符', '死符', '地雌', '卷舌', '绞杀', '天德', '贯索', '亡神', '国印', '岁殿', '卦气', '空亡', '豹尾', '擎天', '天空', '大杀', '天厄', '月廉', '天雄', '天哭', '天狗', '地耗', '月符', '披头', '红鸾', '岁驾', '小耗', '寡宿', '飞刃', '天耗', '斗杓', '驿马', '阳刃', '阑干', '玉贵', '血刃', '浮沉', '解神'];
const TRANSIT_GOD_ORDER = ['岁驾', '天空', '地雌', '贯索', '五鬼', '死符', '大耗', '天厄', '天雄', '大杀', '卷舌', '天德', '天狗', '蓦越', '亡神', '天喜', '披头', '血刃', '解神', '天哭', '地解', '劫杀', '的杀', '红鸾', '驿马', '游奕', '擎天', '黄幡', '豹尾', '天厨', '三刑', '六害', '咸池', '阳刃', '禄勋', '天贵'];
const PLANET_DEFS = [
	{id: AstroConst.SUN, label: '日'},
	{id: AstroConst.MOON, label: '月'},
	{id: AstroConst.VENUS, label: '金'},
	{id: AstroConst.JUPITER, label: '木'},
	{id: AstroConst.MERCURY, label: '水'},
	{id: AstroConst.MARS, label: '火'},
	{id: AstroConst.SATURN, label: '土'},
	{id: AstroConst.SOUTH_NODE, label: '计'},
	{id: AstroConst.NORTH_NODE, label: '罗'},
	{id: AstroConst.PURPLE_CLOUDS, label: '炁'},
	{id: AstroConst.DARKMOON, label: '孛'},
];

function r(idx){
	return RING_POS[idx] * R;
}

function norm(deg){
	let val = Number(deg);
	if(!Number.isFinite(val)){
		return 0;
	}
	val %= 360;
	if(val < 0){
		val += 360;
	}
	return val;
}

function point(radius, thetaDeg){
	const rad = thetaDeg * Math.PI / 180;
	return {
		x: radius * Math.cos(rad),
		y: radius * Math.sin(rad),
	};
}

function annularSectorPath(inner, outer, startTheta, endTheta){
	const startOuter = point(outer, startTheta);
	const endOuter = point(outer, endTheta);
	const endInner = point(inner, endTheta);
	const startInner = point(inner, startTheta);
	const span = Math.abs(endTheta - startTheta);
	const largeArc = span > 180 ? 1 : 0;
	const sweep = endTheta > startTheta ? 1 : 0;
	const innerSweep = sweep ? 0 : 1;
	return [
		`M ${startOuter.x} ${startOuter.y}`,
		`A ${outer} ${outer} 0 ${largeArc} ${sweep} ${endOuter.x} ${endOuter.y}`,
		`L ${endInner.x} ${endInner.y}`,
		`A ${inner} ${inner} 0 ${largeArc} ${innerSweep} ${startInner.x} ${startInner.y}`,
		'Z',
	].join(' ');
}

function moiraThetaFromDegree(degree){
	return 30 - Number(degree || 0);
}

function sectorTheta(index){
	return -15 - 30 * index;
}

function radialLine(theta, inner, outer, opt = {}){
	const a = point(inner, theta);
	const b = point(outer, theta);
	return (
		<line
			x1={a.x}
			y1={a.y}
			x2={b.x}
			y2={b.y}
			stroke={opt.color || BLACK}
			strokeWidth={opt.width || 1}
			opacity={opt.opacity === undefined ? 1 : opt.opacity}
		/>
	);
}

function connectorLine(markTheta, labelTheta, inner, outer, dir, opt = {}){
	const band = Math.max(1, outer - inner);
	const gap = Math.max(8, Math.min(30, band * 0.56));
	const startRadius = dir >= 0 ? outer : inner;
	const endRadius = dir >= 0 ? outer - gap : inner + gap;
	const a = point(startRadius, markTheta);
	const b = point(endRadius, labelTheta);
	return (
		<line
			x1={a.x}
			y1={a.y}
			x2={b.x}
			y2={b.y}
			stroke={opt.color || BLACK}
			strokeWidth={opt.width || 1}
			opacity={opt.opacity === undefined ? 1 : opt.opacity}
		/>
	);
}

function cleanText(text){
	return `${text || ''}`.replace(/\s+/g, '');
}

function formatGodName(name){
	let val = cleanText(name);
	if(!val){
		return '';
	}
	val = val.split(/[\/／]/)[0];
	const aliases = {
		天乙贵人: '天贵',
		玉堂贵人: '玉贵',
	};
	return aliases[val] || val;
}

function splitColumns(text, maxPerCol){
	const raw = cleanText(text);
	if(!raw){
		return [];
	}
	if(raw.indexOf('|') >= 0){
		return raw.split('|').filter(Boolean);
	}
	const cols = [];
	for(let i = 0; i < raw.length; i += maxPerCol){
		cols.push(raw.slice(i, i + maxPerCol));
	}
	return cols;
}

function verticalText(text, x, y, opt = {}){
	const size = opt.size || 22;
	const gap = opt.gap || size * 1.02;
	const maxPerCol = opt.maxPerCol || 5;
	const cols = splitColumns(text, maxPerCol);
	const colGap = opt.colGap || size * 0.92;
	const fill = opt.color || BLACK;
	const weight = opt.weight || 400;
	const opacity = opt.opacity === undefined ? 1 : opt.opacity;
	const nodes = [];
	cols.forEach((col, colIdx)=>{
		const chars = Array.from(col);
		const startY = y - (chars.length - 1) * gap / 2;
		const colX = x + (cols.length - 1) * colGap / 2 - colIdx * colGap;
		chars.forEach((ch, i)=>{
			const textProps = {
				x: colX,
				y: startY + i * gap,
				fontSize: size,
				fontWeight: weight,
				textAnchor: 'middle',
				dominantBaseline: 'central',
				opacity,
			};
			nodes.push(
				<text
					key={`${text}-${colIdx}-${i}-${x}-${y}`}
					{...textProps}
					fill={fill}
				>
					{ch}
				</text>
			);
		});
	});
	return nodes;
}

function horizontalRingText(text, radius, theta, opt = {}){
	const p = point(radius, theta);
	const rotate = tangentRotate(theta);
	return (
		<text
			x={p.x}
			y={p.y}
			fill={opt.color || BLACK}
			fontSize={opt.size || 22}
			fontWeight={opt.weight || 400}
			fontFamily={opt.family || undefined}
			textAnchor="middle"
			dominantBaseline="central"
			transform={`rotate(${rotate} ${p.x} ${p.y})`}
		>
			{text}
		</text>
	);
}

function pairedRadialText(text, theta, inner, outer, opt = {}){
	const chars = Array.from(cleanText(text));
	if(!chars.length){
		return null;
	}
	const band = Math.max(1, outer - inner);
	const branch = chars.slice(1).join('');
	const items = [
		{key: 'outer', value: chars[0], radius: inner + band * 0.68},
		{key: 'inner', value: branch || chars[1] || '', radius: inner + band * 0.34},
	].filter((item)=>item.value);
	return (
		<g className="moira-paired-radial-text">
			{items.map((item)=>{
				const p = point(item.radius, theta);
				return (
					<text
						key={`${text}-${item.key}-${theta}`}
						x={p.x}
						y={p.y}
						fill={opt.color || BLACK}
						fontSize={opt.size || 22}
						fontWeight={opt.weight || 600}
						textAnchor="middle"
						dominantBaseline="central"
					>
						{item.value}
					</text>
				);
			})}
		</g>
	);
}

function radialStackText(text, theta, inner, outer, opt = {}){
	const chars = Array.from(cleanText(text));
	if(!chars.length){
		return [];
	}
	const size = opt.size || 24;
	const step = opt.step || size * 1.04;
	const usableOuter = outer - size * 0.5;
	const usableInner = inner + size * 0.5;
	const stackHeight = (chars.length - 1) * step;
	const start = Math.min(usableOuter, (usableInner + usableOuter + stackHeight) / 2);
	const fill = opt.color || GREEN;
	const weight = opt.weight || 600;
	const opacity = opt.opacity === undefined ? 1 : opt.opacity;
	return chars.map((ch, idx)=>{
		const p = point(start - idx * step, theta);
		return (
			<text
				key={`${text}-${theta}-${idx}`}
				x={p.x}
				y={p.y}
				fill={fill}
				fontSize={size}
				fontWeight={weight}
				textAnchor="middle"
				dominantBaseline="central"
				opacity={opacity}
			>
				{ch}
			</text>
		);
	});
}

function radialColumns(items, centerTheta, inner, outer, opt = {}){
	const list = (items || []).filter(Boolean);
	if(!list.length){
		return [];
	}
	const arc = opt.arc || 24;
	const maxStep = opt.maxStep || 5.2;
	const minStep = opt.minStep || 2.8;
	const rawStep = list.length <= 1 ? 0 : arc / (list.length - 1);
	const step = list.length <= 1 ? 0 : (
		opt.fitArc ? Math.min(maxStep, rawStep) : Math.max(minStep, Math.min(maxStep, rawStep))
	);
	const start = centerTheta + step * (list.length - 1) / 2;
	const nodes = [];
	list.forEach((item, idx)=>{
		const theta = start - idx * step;
		nodes.push(...radialStackText(item, theta, inner, outer, opt));
	});
	return nodes;
}

function godTextSize(count){
	if(count > 22){
		return 11;
	}
	if(count > 18){
		return 13;
	}
	if(count > 14){
		return 15;
	}
	if(count > 10){
		return 17;
	}
	if(count > 6){
		return 19;
	}
	return 21;
}

function godColumnStep(count){
	if(count > 22){
		return {minStep: 0.9, maxStep: 1.25, arc: 27};
	}
	if(count > 18){
		return {minStep: 1.1, maxStep: 1.55, arc: 27};
	}
	if(count > 14){
		return {minStep: 1.35, maxStep: 1.9, arc: 27};
	}
	if(count > 10){
		return {minStep: 1.8, maxStep: 2.7, arc: 27};
	}
	return {minStep: 2.7, maxStep: 5.1, arc: 25};
}

function objectRa(obj, preferLon = false){
	const num = Number(obj && (preferLon && obj.lon !== undefined ? obj.lon : (obj.ra !== undefined ? obj.ra : obj.lon)));
	return Number.isFinite(num) ? num : null;
}

function isZhengSiderealChart(chart){
	const params = chart && chart.params ? chart.params : {};
	return Number(params.doubingSu28) === 4 || Number(params.guolaoZhengSidereal) === 1;
}

function signIndexFromDegree(degree){
	return Math.floor(norm(degree) / 30) % 12;
}

function dmsText(value){
	let val = Number(value);
	if(!Number.isFinite(val)){
		return '';
	}
	val = ((val % 30) + 30) % 30;
	const deg = Math.floor(val);
	const minFloat = (val - deg) * 60;
	const min = Math.floor(minFloat);
	const sec = Math.round((minFloat - min) * 60);
	return `${String(deg).padStart(2, '0')}°${String(min).padStart(2, '0')}′${String(sec).padStart(2, '0')}″`;
}

function speedText(obj){
	const speed = planetSpeed(obj);
	const sign = speed >= 0 ? '+' : '-';
	return `${sign}${Math.abs(speed).toFixed(4)}`;
}

function objectTooltip(item, kind){
	const degree = norm(item.degree);
	const signIdx = signIndexFromDegree(degree);
	const inSign = degree - signIdx * 30;
	const su = item.obj && item.obj.su28 ? item.obj.su28 : '';
	const label = item.label || item.name || item.id;
	const layer = kind === 'birth' ? '本命' : '流年';
	return `${label}（${layer}）：${su ? `${su} ` : ''}${dmsText(inSign)}；${SIGN_NAMES[signIdx]} ${dmsText(inSign)}；速度 ${speedText(item.obj)}`;
}

function objectsNearDegree(chart, degree, tolerance = 1.2){
	const objects = chart && chart.objects ? chart.objects : [];
	return PLANET_DEFS.map((def)=>{
		const obj = objects.find((item)=>item.id === def.id);
		const ra = objectRa(obj);
		if(!obj || ra === null || circularGap(ra, degree) > tolerance){
			return null;
		}
		return def.label;
	}).filter(Boolean);
}

function findObject(chart, id){
	const objects = chart && chart.objects ? chart.objects : [];
	return objects.find((obj)=>obj.id === id);
}

function planetSpeed(obj){
	const speed = Number(obj && (obj.lonspeed !== undefined ? obj.lonspeed : obj.speed));
	return Number.isFinite(speed) ? speed : 0;
}

function planetColor(obj, baseColor){
	const speed = planetSpeed(obj);
	if(speed < -0.000001){
		return RED;
	}
	if(Math.abs(speed) < 0.002){
		return MAGENTA;
	}
	return baseColor;
}

function circularGap(a, b){
	const diff = Math.abs(norm(a) - norm(b));
	return Math.min(diff, 360 - diff);
}

function clusterPlanetItems(items, threshold){
	if(items.length <= 1){
		return items.length ? [items] : [];
	}
	const groups = [];
	let current = [items[0]];
	for(let i = 1; i < items.length; i++){
		if(items[i].degree - items[i - 1].degree <= threshold){
			current.push(items[i]);
		}else{
			groups.push(current);
			current = [items[i]];
		}
	}
	groups.push(current);
	if(groups.length > 1){
		const first = groups[0];
		const last = groups[groups.length - 1];
		if(circularGap(first[0].degree, last[last.length - 1].degree) <= threshold){
			groups[0] = last.concat(first);
			groups.pop();
		}
	}
	return groups;
}

function resolveLabelDegrees(group, minGap){
	if(group.length <= 1){
		return group.map((item)=>({
			...item,
			labelDegree: item.degree,
		}));
	}
	const desired = [];
	let prev = null;
	group.forEach((item)=>{
		let degree = item.degree;
		if(prev !== null){
			while(degree < prev){
				degree += 360;
			}
		}
		desired.push(degree);
		prev = degree;
	});
	const labels = desired.slice();
	for(let i = 1; i < labels.length; i++){
		if(labels[i] - labels[i - 1] < minGap){
			labels[i] = labels[i - 1] + minGap;
		}
	}
	const desiredCenter = desired.reduce((sum, val)=>sum + val, 0) / desired.length;
	const labelCenter = labels.reduce((sum, val)=>sum + val, 0) / labels.length;
	const shift = desiredCenter - labelCenter;
	return group.map((item, idx)=>({
		...item,
		labelDegree: norm(labels[idx] + shift),
	}));
}

function planetPlacements(chart, inner, outer, dir, size, preferLon = false){
	const objects = chart && chart.objects ? chart.objects : [];
	const items = PLANET_DEFS.map((def, order)=>{
		const obj = objects.find((item)=>item.id === def.id);
		const degree = objectRa(obj, preferLon);
		if(!obj || degree === null){
			return null;
		}
		return {
			...def,
			order,
			obj,
			degree: norm(degree),
		};
	}).filter(Boolean).sort((a, b)=>a.degree - b.degree || a.order - b.order);
	const center = (inner + outer) / 2;
	const band = Math.max(1, outer - inner);
	const pad = Math.min(18, Math.max(4, band / 3));
	const preferredRadius = center + dir * Math.min(4, band / 8);
	const safeRadius = Math.max(inner + pad, Math.min(outer - pad, preferredRadius));
	const minGap = Math.max(5.6, Math.min(12.5, (size || 30) / Math.max(180, safeRadius) * 180 / Math.PI * 1.35));
	const groups = clusterPlanetItems(items, minGap);
	return groups.reduce((list, group)=>list.concat(resolveLabelDegrees(group, minGap).map((item)=>({
		...item,
		radius: safeRadius,
	}))), []).sort((a, b)=>a.degree - b.degree || a.order - b.order);
}

function lifeModeFromFields(fields){
	if(fields && fields.guolaoLifeMode && fields.guolaoLifeMode.value !== undefined && fields.guolaoLifeMode.value !== null){
		return normalizeGuolaoLifeMode(fields.guolaoLifeMode.value);
	}
	return getStoredGuolaoLifeMode();
}

function lifeDegree(chart, fields){
	const life = findObject(chart, AstroConst.LIFEMASTERDEG74);
	const asc = findObject(chart, AstroConst.ASC);
	const sun = findObject(chart, AstroConst.SUN);
	const lifeMode = lifeModeFromFields(fields);
	const useLifeMaster = lifeMode === GUOLAO_LIFE_MODE_YUMAO || lifeMode === GUOLAO_LIFE_MODE_COTRANS;
	const preferLon = isZhengSiderealChart(chart);
	const primary = useLifeMaster ? objectRa(life, preferLon) : objectRa(asc, preferLon);
	const secondary = useLifeMaster ? objectRa(asc, preferLon) : objectRa(life, preferLon);
	const val = primary !== null ? primary : (secondary !== null ? secondary : objectRa(sun, preferLon));
	return val === null ? 0 : val;
}

function childLimitYears(life){
	const inSign = norm(Number(life || 0)) % 30;
	return Math.max(1, Math.round(9 + inSign / 3));
}

function limitSegments(life){
	return [childLimitYears(life)].concat(LIMIT_SEQ.slice(1));
}

function limitAgeOffset(life, age){
	const segments = limitSegments(life);
	let rest = Math.max(0, Number(age || 1) - 1);
	let offset = 0;
	for(let i = 0; i < segments.length; i++){
		const span = Math.max(0.1, segments[i]);
		if(rest <= span){
			return offset + 30 * rest / span;
		}
		offset += 30;
		rest -= span;
	}
	return Math.min(360, offset);
}

function limitAgeAtOffset(life, offset){
	const segments = limitSegments(life);
	let rest = Math.max(0, Number(offset || 0));
	let age = 1;
	for(let i = 0; i < segments.length; i++){
		const span = Math.max(0.1, segments[i]);
		if(rest <= 30){
			return age + rest / 30 * span;
		}
		age += span;
		rest -= 30;
	}
	return age;
}

function limitDegreeForAge(life, age){
	return norm(Number(life || 0) - limitAgeOffset(life, age));
}

function limitOffsetFromLife(life, degree){
	return norm(Number(life || 0) - Number(degree || 0));
}

function limitYearForDegree(birthYear, life, degree){
	return birthYear + Math.floor(limitAgeAtOffset(life, limitOffsetFromLife(life, degree)) - 1);
}

function tangentRotate(theta){
	let rotate = theta + 90;
	if(rotate > 90 || rotate < -90){
		rotate += 180;
	}
	return rotate;
}

function birthYearFrom(root, chart, fields){
	const fromParam = root && root.params && root.params.date;
	const fromField = fields && fields.date && fields.date.value && fields.date.value.format
		? fields.date.value.format('YYYY') : '';
	const raw = fromParam || fromField || '';
	const match = `${raw}`.match(/-?\d{3,4}/);
	if(match){
		return parseInt(match[0], 10);
	}
	const bazi = (root && root.nongli && root.nongli.bazi) || (chart && chart.nongli && chart.nongli.bazi);
	if(bazi && bazi.year && bazi.year.year){
		return Number(bazi.year.year);
	}
	return new Date().getFullYear();
}

function stemBranchForYear(year){
	const idx = ((Number(year) - 1984) % 60 + 60) % 60;
	return STEM_BRANCHES[idx] || '';
}

function getZiGods(root, chart){
	const rootGods = root && root.nongli && root.nongli.bazi && root.nongli.bazi.guolaoGods
		? root.nongli.bazi.guolaoGods.ziGods : null;
	const chartGods = chart && chart.nongli && chart.nongli.bazi && chart.nongli.bazi.guolaoGods
		? chart.nongli.bazi.guolaoGods.ziGods : null;
	return chartGods || rootGods || {};
}

function collectGods(ziGods, zi){
	const one = ziGods && ziGods[zi] ? ziGods[zi] : {};
	const raw = []
		.concat(one.goodGods || [])
		.concat(one.neutralGods || [])
		.concat(one.badGods || [])
		.concat(one.taisuiGods || []);
	const seen = new Set();
	const names = [];
	raw.forEach((item)=>{
		const val = formatGodName(item);
		if(!val || seen.has(val)){
			return;
		}
		seen.add(val);
		names.push(val);
	});
	return names;
}

function orderedGods(items, orderList){
	const list = (items || []).map(formatGodName).filter(Boolean);
	if(!orderList || !orderList.length){
		return list;
	}
	const rank = new Map(orderList.map((name, idx)=>[name, idx]));
	return list.slice().sort((a, b)=>{
		const ar = rank.has(a) ? rank.get(a) : 999;
		const br = rank.has(b) ? rank.get(b) : 999;
		return ar - br || a.localeCompare(b, 'zh-Hans-CN');
	});
}

function buildFixedStars(chart){
	const src = chart && chart.fixedStarSu28 && chart.fixedStarSu28.length ? chart.fixedStarSu28 : null;
	if(src){
		return src.map((item, idx)=>({
			name: item.name || HALF_STELLAR[idx] || '',
			label: item.name || FULL_STELLAR[idx] || HALF_STELLAR[idx] || '',
			ra: Number(item.ra),
		})).filter((item)=>Number.isFinite(item.ra));
	}
	return HALF_STELLAR.map((name, idx)=>({
		name,
		label: FULL_STELLAR[idx] || name,
		ra: idx * 360 / HALF_STELLAR.length,
	}));
}

class GuoLaoMoiraWheel extends Component{
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
		this.setState({
			tooltip: {
				...this.tooltipPoint(evt),
				text,
			},
		});
	}

	moveTooltip(evt){
		if(!this.state.tooltip){
			return;
		}
		this.setState({
			tooltip: {
				...this.state.tooltip,
				...this.tooltipPoint(evt),
			},
		});
	}

	hideTooltip(){
		if(this.state.tooltip){
			this.setState({
				tooltip: null,
			});
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
				{RING_POS.map((pos, idx)=>RING_DRAW_TYPE[idx] <= -10 ? null : (
					<circle
						key={`ring-${idx}`}
						r={pos * R}
						className={RING_DRAW_TYPE[idx] === 1 || idx === 0 || idx === 11 ? 'moira-ring-major' : 'moira-ring-minor'}
					/>
				))}
			</g>
		);
	}

	renderSectorLines(){
		const nodes = [];
		for(let ringIdx = 1; ringIdx < RING_DRAW_TYPE.length; ringIdx++){
			const drawType = RING_DRAW_TYPE[ringIdx];
			if(drawType <= 0 && drawType > -10){
				for(let i = 0; i < 12; i++){
					nodes.push(
						<g key={`sector-${ringIdx}-${i}`}>
							{radialLine(-30 * i, r(ringIdx - 1), r(ringIdx), {color: BLACK, width: 0.95})}
						</g>
					);
				}
			}
			if(drawType === 2 || drawType === -11){
				for(let i = 0; i < 24; i++){
					nodes.push(
						<g key={`sector24-${ringIdx}-${i}`}>
							{radialLine(-7.5 - 15 * i, r(ringIdx - 1), r(ringIdx), {color: BLACK, width: 0.85})}
						</g>
					);
				}
			}
		}
		return <g>{nodes}</g>;
	}

	renderDegreeMarkBand(inner, outer, keyPrefix, thetaForDegree = moiraThetaFromDegree, opt = {}){
		const nodes = [];
		const delta = (outer - inner) / 3;
		for(let degree = 0; degree < 360; degree++){
			const theta = thetaForDegree(degree);
			const major = degree % 30 === 0;
			const mid = degree % 5 === 0;
			const start = major ? inner : (mid ? inner + delta : inner + 2 * delta);
			const color = opt.mutedMajor ? BLACK : (major ? RED : BLACK);
			nodes.push(
				<g key={`${keyPrefix}-${degree}`}>
					{radialLine(theta, start, outer, {
						color,
						width: major ? (opt.majorWidth || 0.82) : 0.62,
						opacity: opt.opacity === undefined ? (major ? 0.6 : 0.48) : opt.opacity,
					})}
				</g>
			);
		}
		return nodes;
	}

	renderDegreeTicks(chart, fields){
		const nodes = [];
		const life = lifeDegree(chart, fields);
		const lifeTheta = moiraThetaFromDegree(life);
			nodes.push(...this.renderDegreeMarkBand(r(4), r(5), 'full-stellar-up', moiraThetaFromDegree, {mutedMajor: true, opacity: 0.38}));
			nodes.push(...this.renderDegreeMarkBand(r(6), r(7), 'full-stellar-down', moiraThetaFromDegree, {mutedMajor: true, opacity: 0.38}));
		for(let age = 1; age <= 106; age++){
			const degree = limitDegreeForAge(life, age + 0.5);
			const theta = moiraThetaFromDegree(degree);
			if(age % 1 === 0){
				const p = point(r(10) + (r(11) - r(10)) * 0.5, theta);
				nodes.push(
					<text key={`limit-age-${age}`} x={p.x} y={p.y} fill={GREEN} fontSize="10.5" textAnchor="middle" dominantBaseline="central">
						{age}
					</text>
				);
			}
		}
		nodes.push(
			<g key="life-degree-marker" className="moira-life-degree-marker">
				{radialLine(lifeTheta, r(10), r(11), {color: RED, width: 2.7})}
			</g>
		);
		return <g className="moira-degree-ticks">{nodes}</g>;
	}

	renderStellarTicks(){
		return null;
	}

	renderStaticTwelve(){
		const nodes = [];
		for(let i = 0; i < 12; i++){
			const theta = sectorTheta(i);
				const startTheta = -30 * i;
				const endTheta = -30 * (i + 1);
					const pNumber = point((r(1) + r(2)) / 2, theta);
					const houseNameRadius = (r(2) + r(3)) / 2;
				const tip = `${HOUSE_BRANCH[i]}：${TWELVE_SIGNS[i]}；同经：${RING1[i]}`;
				nodes.push(
					<g key={`static-${i}`}>
					<path
						className="moira-hover-zone"
						d={annularSectorPath(r(0), r(3), endTheta, startTheta)}
						{...this.tooltipHandlers(tip)}
					>
							<title>{tip}</title>
						</path>
						{pairedRadialText(RING1[i], theta, r(0), r(1), {size: 22, color: BLACK, weight: 600})}
							{horizontalRingText(HOUSE_BRANCH[i], houseNameRadius, theta, {size: 20, color: GREEN, weight: 700})}
						<text
							x={pNumber.x}
							y={pNumber.y}
							fill={GREEN}
							fontSize="20"
							fontWeight="600"
							textAnchor="middle"
							dominantBaseline="central"
							transform={`rotate(${tangentRotate(theta)} ${pNumber.x} ${pNumber.y})`}
						>
							{HOUSE_NUMBERS[i]}
						</text>
					</g>
			);
		}
		return (
			<g className="moira-static-twelve">
				{nodes}
				<circle r={r(0)} fill="#fff" stroke={BLACK} />
				<text x="0" y="-24" fill={GREEN} fontSize="28" fontWeight="700" textAnchor="middle">七政</text>
				<text x="0" y="8" fill={GREEN} fontSize="28" fontWeight="700" textAnchor="middle">立命</text>
				<text x="0" y="40" fill={GREEN} fontSize="28" fontWeight="700" textAnchor="middle">度木</text>
			</g>
		);
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
			const edgeTheta = moiraThetaFromDegree(cur.ra);
			const centerTheta = moiraThetaFromDegree(Number(cur.ra) + span / 2);
			const p = point((r(STELLAR_TICK_INNER) + r(STELLAR_TICK_OUTER)) / 2, centerTheta);
			const endRa = norm(Number(cur.ra) + span);
			const tip = `${cur.label || cur.name}：${dmsText(0)} 至 ${dmsText(span)}；起点 ${norm(cur.ra).toFixed(2)}°，终点 ${endRa.toFixed(2)}°`;
			nodes.push(
				<g key={`stellar-${idx}`}>
					<path
						className="moira-hover-zone"
						d={annularSectorPath(r(STELLAR_TICK_INNER), r(STELLAR_TICK_OUTER), moiraThetaFromDegree(Number(cur.ra) + span), edgeTheta)}
						{...this.tooltipHandlers(tip)}
					>
						<title>{tip}</title>
					</path>
					{radialLine(edgeTheta, r(STELLAR_TICK_INNER) + 1, r(STELLAR_TICK_OUTER) - 1, {color: RED, width: 1})}
					{verticalText(cur.name || cur.label, p.x, p.y, {
						size: 23,
						maxPerCol: 1,
						color: BLACK,
						weight: 600,
					})}
				</g>
			);
		});
		return <g className="moira-stellar-layer">{nodes}</g>;
	}

	renderPlanetRing(chart, opt){
		const nodes = [];
		const placements = planetPlacements(chart, opt.inner, opt.outer, opt.dir, opt.size, opt.preferLon);
		placements.forEach((item, idx)=>{
			const markTheta = moiraThetaFromDegree(item.degree);
			const labelTheta = moiraThetaFromDegree(item.labelDegree);
			const p = point(item.radius, labelTheta);
			const tip = objectTooltip(item, opt.kind);
			nodes.push(
				<g key={`${opt.kind}-planet-${item.id}-${idx}`}>
					<circle
						className="moira-hover-zone"
						cx={p.x}
						cy={p.y}
						r={Math.max(20, opt.size * 0.82)}
						{...this.tooltipHandlers(tip)}
					>
						<title>{tip}</title>
					</circle>
						{connectorLine(markTheta, labelTheta, opt.markInner, opt.markOuter, opt.lineDir || 1, {color: opt.markColor, width: 1.05})}
					{verticalText(item.label, p.x, p.y, {
						size: opt.size,
						maxPerCol: 1,
						color: planetColor(item.obj, opt.color),
						weight: 600,
					})}
				</g>
			);
		});
		return <g className={`moira-planet-layer moira-planet-layer-${opt.kind}`}>{nodes}</g>;
	}

	renderPlanetLayers(birthChart, transitChart){
		const birthPreferLon = isZhengSiderealChart(birthChart);
		const transitPreferLon = isZhengSiderealChart(transitChart || birthChart);
		return (
			<g>
					{this.renderPlanetRing(transitChart || birthChart, {
						kind: 'now',
						inner: r(3) + 6,
						outer: r(4) - 6,
						dir: 1,
						size: 27,
						color: BLUE,
							markColor: NOW_MARK,
							markInner: r(3),
							markOuter: r(4),
							lineDir: 1,
							preferLon: transitPreferLon,
						})}
					{this.renderPlanetRing(birthChart, {
						kind: 'birth',
						inner: r(7) + 7,
						outer: r(8) - 8,
						dir: -1,
						size: 28,
						color: GREEN,
							markColor: BLACK,
							markInner: r(7),
							markOuter: r(8),
							lineDir: -1,
							preferLon: birthPreferLon,
						})}
				</g>
			);
	}

	renderGodRing(root, chart, opt){
		const ziGods = getZiGods(root, chart);
		const nodes = [];
		for(let i = 0; i < 12; i++){
			const theta = sectorTheta(i);
			const gods = orderedGods(collectGods(ziGods, TWELVE_SIGNS[i]), opt.order);
			const godSize = godTextSize(gods.length);
			const godSteps = godColumnStep(gods.length);
			const startTheta = -30 * i;
			const endTheta = -30 * (i + 1);
			const title = opt.kind === 'transit' ? '流年神煞' : '本命神煞';
			const tip = `${TWELVE_SIGNS[i]}：${title}${gods.length ? `｜${gods.join('，')}` : '｜无'}`;
			nodes.push(
				<g key={`${opt.kind}-god-${i}`}>
					<path
						className="moira-hover-zone"
						d={annularSectorPath(opt.inner, opt.outer, endTheta, startTheta)}
						{...this.tooltipHandlers(tip)}
					>
						<title>{tip}</title>
					</path>
					{radialColumns(gods, theta, opt.inner, opt.outer, {
						size: opt.size || godSize,
						color: opt.color || GREEN,
						weight: opt.weight || 600,
						arc: godSteps.arc,
						minStep: godSteps.minStep,
						maxStep: godSteps.maxStep,
						fitArc: true,
						opacity: opt.opacity,
					})}
				</g>
			);
		}
		return <g className={`moira-star-table-layer moira-star-table-layer-${opt.kind}`}>{nodes}</g>;
	}

	renderStarTables(root, chart, transitRoot, transitChart){
		const showTransit = this.props.showMoiraTransitGods !== false;
		const birthOuter = showTransit ? r(9) - 8 : r(GOD_RING_OUTER) - 12;
		return (
			<g>
				{showTransit ? <circle className="moira-transit-god-split" r={r(9)} fill="none" stroke={BLACK} strokeWidth="0.85" /> : null}
				{this.renderGodRing(root, chart, {
					kind: 'birth',
					inner: r(GOD_RING_INNER) + 14,
					outer: birthOuter,
					order: BIRTH_GOD_ORDER,
				})}
				{showTransit ? this.renderGodRing(transitRoot || root, transitChart || chart, {
					kind: 'transit',
					inner: r(9) + 10,
					outer: r(GOD_RING_OUTER) - 12,
					order: TRANSIT_GOD_ORDER,
					color: BLUE,
					opacity: transitChart ? 1 : 0.72,
				}) : null}
			</g>
		);
	}

	renderLimitRing(root, chart, fields){
		const birthYear = birthYearFrom(root, chart, fields);
		const life = lifeDegree(chart, fields);
		const nodes = [];
		const yearMarks = [{degree: life, year: birthYear, key: 'birth'}];
		for(let sign = 0; sign < 12; sign++){
			const degree = sign * 30;
			const offset = limitOffsetFromLife(life, degree);
			if(offset < 0.001 || offset > 357){
				continue;
			}
			yearMarks.push({
				degree,
				year: limitYearForDegree(birthYear, life, degree),
				key: `boundary-${sign}`,
			});
		}
		yearMarks.sort((a, b)=>limitOffsetFromLife(life, a.degree) - limitOffsetFromLife(life, b.degree));
			yearMarks.forEach((mark)=>{
				const degree = norm(mark.degree);
				const theta = moiraThetaFromDegree(degree);
				const pYear = point(r(12) + 28, theta);
				nodes.push(
					<g key={`year-${mark.key}`}>
						{radialLine(theta, r(10), r(12), {color: BLACK, width: mark.key === 'birth' ? 1.35 : 1})}
						<text
							x={pYear.x}
							y={pYear.y}
							fill={BLACK}
							fontSize={mark.key === 'birth' ? 24 : 21}
							fontWeight={mark.key === 'birth' ? 600 : 400}
							textAnchor="middle"
							dominantBaseline="central"
							transform={`rotate(${tangentRotate(theta)} ${pYear.x} ${pYear.y})`}
						>
							{mark.year}
						</text>
					</g>
				);
			});
			for(let age = 1; age <= 106; age++){
				const theta = moiraThetaFromDegree(limitDegreeForAge(life, age));
				const major = age === 1 || age % 10 === 0;
				nodes.push(
					<g key={`limit-age-line-${age}`}>
						{radialLine(theta, major ? r(10) : (r(10) + r(11)) / 2, r(11), {
							color: major ? RED : GREEN,
							width: major ? 1.1 : 0.7,
							opacity: major ? 0.9 : 0.68,
						})}
					</g>
				);
			}
			return <g className="moira-limit-layer">{nodes}</g>;
		}

	renderSideText(root, chart, fields){
		const birthYear = birthYearFrom(root, chart, fields);
		const transitYear = this.props.transitParams && this.props.transitParams.date
			? birthYearFrom({params: this.props.transitParams}, null, null) : birthYear;
		const params = root && root.params ? root.params : {};
		const transitParams = this.props.transitParams || {};
		const bazi = (root && root.nongli && root.nongli.bazi) || (chart && chart.nongli && chart.nongli.bazi) || {};
		const y = bazi.year && bazi.year.text ? bazi.year.text : stemBranchForYear(birthYear);
		const m = bazi.month && bazi.month.text ? bazi.month.text : '';
		const d = bazi.day && bazi.day.text ? bazi.day.text : '';
		const h = bazi.time && bazi.time.text ? bazi.time.text : '';
		return (
			<g className="moira-side-text" opacity="0.96">
					<text x="-590" y="522" fill={BLACK} fontSize="17">
						<tspan x="-590" dy="0">四柱：{[y, m, d, h].filter(Boolean).join(' ')}</tspan>
						<tspan x="-590" dy="24">流年：{transitYear} {stemBranchForYear(transitYear)}</tspan>
						<tspan x="-590" dy="24">{params.date || ''} {params.time || ''}</tspan>
						<tspan x="-590" dy="24">{transitParams.date ? `流年时间：${transitParams.date} ${transitParams.time || ''}` : ''}</tspan>
					</text>
					<text x="590" y="522" fill={BLACK} fontSize="17" textAnchor="end">
						<tspan x="590" dy="0">地心计算</tspan>
						<tspan x="590" dy="24">七政四余</tspan>
						<tspan x="590" dy="24">Moira full</tspan>
					</text>
				</g>
			);
	}

	renderTooltip(){
		const tooltip = this.state.tooltip;
		if(!tooltip){
			return null;
		}
		return (
			<div
				className="horosa-guolao-moira-tooltip"
				style={{
					left: tooltip.x,
					top: tooltip.y,
				}}
			>
				{tooltip.text}
			</div>
		);
	}

	render(){
		const root = this.props.rootValue || {};
		const rawChart = this.props.value || root.chart || {};
		const chart = root.params ? {...rawChart, params: root.params} : rawChart;
		const transitRoot = this.props.transitValue || {};
		const transitChart = transitRoot.chart ? (transitRoot.params ? {...transitRoot.chart, params: transitRoot.params} : transitRoot.chart) : null;
		const height = this.props.height || 740;
		const side = this.state.containerSide || Math.min(height, 740);
		return (
			<div className="horosa-guolao-moira-wheel" style={{height}} ref={this.containerRef}>
				<svg
					style={{width: side, height: side}}
					viewBox={`${-VIEW / 2} ${-VIEW / 2} ${VIEW} ${VIEW}`}
					role="img"
					aria-label="Moira风格七政星盘"
				>
					<rect x={-VIEW / 2} y={-VIEW / 2} width={VIEW} height={VIEW} fill="#fff" />
					<g className="moira-pale-guides">
						{Array.from({length: 24}).map((_, idx)=>(
							<g key={`guide-${idx}`}>{radialLine(-15 * idx, r(GOD_RING_INNER), r(GOD_RING_OUTER), {color: PALE, width: 0.55, opacity: 0.18})}</g>
						))}
					</g>
					{this.renderRings()}
					{this.renderSectorLines()}
					{this.renderDegreeTicks(chart, this.props.fields)}
					{this.renderStellarTicks()}
					{this.renderStaticTwelve()}
					{this.renderStellarRing(chart)}
					{this.renderPlanetLayers(chart, transitChart)}
					{this.renderStarTables(root, chart, transitRoot, transitChart)}
					{this.renderLimitRing(root, chart, this.props.fields)}
					{this.renderSideText(root, chart, this.props.fields)}
				</svg>
				{this.renderTooltip()}
			</div>
		);
	}
}

export {
	R as MOIRA_WHEEL_R,
	VIEW as MOIRA_WHEEL_VIEW,
	BLACK as MOIRA_BLACK,
	GREEN as MOIRA_GREEN,
	BLUE as MOIRA_BLUE,
	RED as MOIRA_RED,
	MAGENTA as MOIRA_MAGENTA,
	PALE as MOIRA_PALE,
	HALF_STELLAR as MOIRA_HALF_STELLAR,
	FULL_STELLAR as MOIRA_FULL_STELLAR,
	PLANET_DEFS as MOIRA_PLANET_DEFS,
	norm as moiraNormDegree,
	point as moiraPoint,
	annularSectorPath as moiraAnnularSectorPath,
	radialLine as moiraRadialLine,
	connectorLine as moiraConnectorLine,
	formatGodName as moiraFormatGodName,
	verticalText as moiraVerticalText,
	horizontalRingText as moiraHorizontalRingText,
	pairedRadialText as moiraPairedRadialText,
	radialStackText as moiraRadialStackText,
	radialColumns as moiraRadialColumns,
	godTextSize as moiraGodTextSize,
	godColumnStep as moiraGodColumnStep,
	objectRa as moiraObjectRa,
	dmsText as moiraDmsText,
	objectTooltip as moiraObjectTooltip,
	planetColor as moiraPlanetColor,
	circularGap as moiraCircularGap,
	planetPlacements as moiraPlanetPlacements,
	getZiGods as moiraGetZiGods,
	collectGods as moiraCollectGods,
	orderedGods as moiraOrderedGods,
	buildFixedStars as moiraBuildFixedStars,
	BIRTH_GOD_ORDER as MOIRA_BIRTH_GOD_ORDER,
	TRANSIT_GOD_ORDER as MOIRA_TRANSIT_GOD_ORDER,
};

export default GuoLaoMoiraWheel;
