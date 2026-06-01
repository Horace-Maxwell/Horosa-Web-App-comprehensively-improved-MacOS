import React, { Component } from 'react';
import * as AstroConst from '../../constants/AstroConst';
import { GUOLAO_LIFE_MODE_COTRANS, GUOLAO_LIFE_MODE_YUMAO, getStoredGuolaoLifeMode, normalizeGuolaoLifeMode, } from './GuoLaoChartStyle';
import { guolaoShenShaTip } from './GuoLaoShenShaDoc';
import './GuoLaoMoiraWheel.less';

const R = 560;
const VIEW = 1220;
const RING_POS = [0.10, 0.22, 0.28, 0.34, 0.43, 0.45, 0.51, 0.53, 0.62, 0.77, 0.92, 0.95, 1.0];
const RING_DRAW_TYPE = [1, 0, 0, 0, 1, -10, -10, 1, 1, 0, 0, 1, -10];
const LIMIT_SEQ = [11.0, 10.0, 11.0, 15.0, 8.0, 7.0, 11.0, 4.5, 4.5, 4.5, 5.0, 5.0];

const MOIRA_BG = 'var(--moira-bg, #ffffff)';
const BLACK = 'var(--moira-ink, #000000)';
const GREEN = 'var(--moira-green, #008000)';
const BLUE = 'var(--moira-blue, #000080)';
const RED = 'var(--moira-red, #ff0000)';
const MAGENTA = 'var(--moira-magenta, #ff00ff)';
const NOW_MARK = 'var(--moira-now-mark, #804040)';
const PALE = 'var(--moira-pale, #b5d8c7)';
const MUTED_PLANET = 'var(--moira-muted-planet, #8a8a8a)';
const STELLAR_TICK_INNER = 5;
const STELLAR_TICK_OUTER = 6;
const GOD_RING_INNER = 8;
const GOD_RING_OUTER = 10;

const TWELVE_SIGNS = ['酉', '申', '未', '午', '巳', '辰', '卯', '寅', '丑', '子', '亥', '戌'];
const RING1 = ['金酉', '水申', '月未', '日午', '水巳', '金辰', '火卯', '木寅', '土丑', '土子', '木亥', '火戌'];
const HOUSE_BRANCH = ['命宫', '财帛', '兄弟', '田宅', '男女', '奴仆', '夫妻', '疾厄', '迁移', '官禄', '福德', '相貌'];
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

// 七政四余 行星主管（黄道十二宫 → 主星），用于中宫「命主/身主」
const SIGN_RULERS_CN = {
	Aries: '火', Taurus: '金', Gemini: '水', Cancer: '月', Leo: '日', Virgo: '水',
	Libra: '金', Scorpio: '火', Sagittarius: '木', Capricorn: '土', Aquarius: '土', Pisces: '木',
};
// 庙旺落陷着色（庙旺=吉金、陷失=弱色），与顺逆留色互不冲突（顺逆留优先）
const DIGNITY_STRONG = ['庙', '旺', '入垣', '得地', '入庙'];
const DIGNITY_WEAK = ['陷', '失', '落'];
const DIGNITY_GOLD = 'var(--moira-dignity-strong, #c9912e)';
const DIGNITY_WEAK_COLOR = 'var(--moira-dignity-weak, #b06a5e)';
// 相位（會衝刑合半合半刑四合）：度 / 容许度 / 色 / 线型，照 Moira aspects 表
const MOIRA_ASPECTS = [
	{key: '會', angle: 0, orb: 12, color: '#00b35a', dash: '5 3'},
	{key: '衝', angle: 180, orb: 6, color: '#8a4bff', dash: '8 3 2 3'},
	{key: '刑', angle: 90, orb: 3, color: '#e07a18', dash: ''},
	{key: '合', angle: 120, orb: 4, color: '#d23b3b', dash: '10 4'},
	{key: '半合', angle: 60, orb: 2, color: '#c79a1e', dash: '2 3'},
	{key: '半刑', angle: 45, alt: 135, orb: 1.5, color: '#c64fb8', dash: '2 3'},
	{key: '四合', angle: 30, alt: 150, orb: 1, color: '#8a8a3a', dash: '2 3'},
];
const MOIRA_DEFAULT_ASPECTS = ['會', '衝', '刑', '合', '半合'];

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
	const length = Math.max(7, Math.min(14, opt.length || band * 0.22));
	const startRadius = dir >= 0 ? outer : inner;
	const endRadius = dir >= 0 ? outer - length : inner + length;
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
						fill={item.key === 'outer' ? (opt.primaryColor || opt.color || BLACK) : (opt.secondaryColor || opt.color || BLACK)}
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
	let deg = Math.floor(val);
	const minFloat = (val - deg) * 60;
	let min = Math.floor(minFloat);
	let sec = Math.round((minFloat - min) * 60);
	if(sec >= 60){
		sec = 0;
		min += 1;
	}
	if(min >= 60){
		min = 0;
		deg += 1;
	}
	return `${String(deg).padStart(2, '0')}°${String(min).padStart(2, '0')}′${String(sec).padStart(2, '0')}″`;
}

function speedText(obj){
	const speed = planetSpeed(obj);
	const sign = speed >= 0 ? '+' : '-';
	return `${sign}${Math.abs(speed).toFixed(4)}`;
}

function listText(items, empty = '无'){
	const list = (items || []).filter(Boolean);
	return list.length ? list.join('、') : empty;
}

function uniquePush(list, val){
	if(!val || list.indexOf(val) >= 0){
		return;
	}
	list.push(val);
}

function starHostByIndex(index){
	const full = FULL_STELLAR[index] || '';
	return full.length > 1 ? full.slice(1) : '';
}

function stellarIndexForDegree(stars, degree){
	const value = norm(degree);
	let found = -1;
	for(let i = 0; i < stars.length; i++){
		const start = norm(stars[i].ra);
		const end = norm(stars[(i + 1) % stars.length].ra);
		if(start <= end){
			if(value >= start && value < end){
				found = i;
				break;
			}
		}else if(value >= start || value < end){
			found = i;
			break;
		}
	}
	return found;
}

function buildStellarRelations(chart){
	const stars = buildFixedStars(chart);
	const rows = stars.map((star, idx)=>({
		index: idx,
		name: star.name || HALF_STELLAR[idx] || '',
		label: star.label || FULL_STELLAR[idx] || star.name || '',
		host: starHostByIndex(idx),
		main: [],
		same: [],
	}));
	const objects = chart && chart.objects ? chart.objects : [];
	const preferLon = isZhengSiderealChart(chart);
	PLANET_DEFS.forEach((def)=>{
		const obj = objects.find((one)=>one.id === def.id);
		const degree = objectRa(obj, preferLon);
		if(!obj || degree === null){
			return;
		}
		const idx = stellarIndexForDegree(stars, degree);
		if(idx < 0 || !rows[idx]){
			return;
		}
		uniquePush(rows[idx].main, def.label);
		const host = rows[idx].host;
		if(!host){
			return;
		}
		rows.forEach((row, rowIdx)=>{
			if(rowIdx !== idx && row.host === host){
				uniquePush(row.same, def.label);
			}
		});
	});
	return rows;
}

function mergeStellarRelationRows(birthChart, transitChart){
	const birth = buildStellarRelations(birthChart);
	const transit = transitChart ? buildStellarRelations(transitChart) : [];
	return birth.map((row, idx)=>({
		...row,
		transitMain: transit[idx] ? transit[idx].main : [],
		transitSame: transit[idx] ? transit[idx].same : [],
	}));
}

function findRulePlanet(rules, item){
	const label = item && item.label;
	const id = item && item.id;
	return (rules && rules.planets ? rules.planets : []).find((row)=>row && (row.id === id || row.name === label)) || null;
}

function findYearPlanetRow(rules, item, kind){
	const yearStars = rules && rules.yearStars ? rules.yearStars : {};
	const key = kind === 'birth' ? 'birth' : 'transit';
	const bucket = yearStars[key] || {};
	const rows = bucket.planetRows || [];
	const label = item && item.label;
	return rows.find((row)=>row && row.star === label) || null;
}

function yearSignRowsForPlanet(rules, item, kind){
	const rows = kind === 'birth'
		? (rules && rules.natalYearStars ? rules.natalYearStars : [])
		: (rules && rules.transitYearStars ? rules.transitYearStars : []);
	const label = item && item.label;
	return rows.filter((row)=>row && row.star === label);
}

function yearSignRowForZi(rules, zi, kind){
	const rows = kind === 'birth'
		? (rules && rules.natalYearStars ? rules.natalYearStars : [])
		: (rules && rules.transitYearStars ? rules.transitYearStars : []);
	return rows.find((row)=>row && row.zi === zi) || null;
}

function weakSolidRowForZi(rules, zi){
	const weakSolid = rules && rules.weakSolid ? rules.weakSolid : {};
	const rows = weakSolid.houses || [];
	return rows.find((row)=>row && row.zi === zi) || null;
}

function weakSolidText(row){
	if(!row){
		return '';
	}
	if(row.label){
		return row.label;
	}
	const parts = [];
	if(row.weak){
		parts.push(`虚${listText(row.weakPillars, '')}`);
	}
	if(row.solid){
		parts.push(`实${listText(row.solidPillars, '')}`);
	}
	return parts.join('、');
}

function objectTooltip(item, kind, rules){
	const degree = norm(item.degree);
	const signIdx = signIndexFromDegree(degree);
	const inSign = degree - signIdx * 30;
	const su = item.obj && item.obj.su28 ? item.obj.su28 : '';
	const label = item.label || item.name || item.id;
	const layer = kind === 'birth' ? '本命' : '流年';
	const rulePlanet = kind === 'birth' ? findRulePlanet(rules, item) : null;
	const yearPlanet = findYearPlanetRow(rules, item, kind);
	const yearSignRows = yearSignRowsForPlanet(rules, item, kind);
	const lines = [
		`${label}（${layer}）：${su ? `${su} ` : ''}${dmsText(inSign)}；${SIGN_NAMES[signIdx]} ${dmsText(inSign)}`,
		`速度：${speedText(item.obj)}`,
	];
	if(yearPlanet){
		const change = yearPlanet.changeTo || '';
		const items = listText(yearPlanet.items, '');
		lines.push(`化曜：${change || '—'}${items ? `（${items}）` : ''}`);
	}
	if(yearSignRows.length){
		lines.push(`所临命曜：${yearSignRows.map((row)=>`${row.name}${row.shortName ? `·${row.shortName}` : ''}`).join('、')}`);
	}
	if(rulePlanet){
		lines.push(`宫位：${[rulePlanet.moiraHouse, rulePlanet.zi, rulePlanet.area || rulePlanet.signName].filter(Boolean).join(' · ')}`);
		if(rulePlanet.dignity){
			lines.push(`虚实：${rulePlanet.dignity}`);
		}
	}
	return lines.filter(Boolean).join('\n');
}

function signTooltip(zi, houseName, sameText, rules, gods){
	const row = yearSignRowForZi(rules, zi, 'birth');
	const weakSolid = weakSolidRowForZi(rules, zi);
	const lines = [
		`${zi}：${houseName}；同经：${sameText}`,
		row ? `命曜：${row.star || '—'} ${row.shortName || ''}${row.quality ? `；${row.quality}` : ''}` : '',
		weakSolid ? `虚实：${weakSolidText(weakSolid) || '无'}` : '',
		gods && gods.length ? `神煞：${listText(gods)}` : '',
	];
	return lines.filter(Boolean).join('\n');
}

function weakSolidMarkers(row, theta, inner, outer){
	if(!row || (!row.weak && !row.solid)){
		return null;
	}
	const markers = [];
	const band = Math.max(1, outer - inner);
	const dotTheta = theta;
	if(row.weak){
		markers.push({key: 'weak', color: RED});
	}
	if(row.solid){
		markers.push({key: 'solid', color: GREEN});
	}
	const baseRadius = outer - Math.max(5, band * 0.11);
	return (
		<g className="moira-weak-solid-markers" pointerEvents="none">
			{markers.map((item, idx)=>{
				const offsetTheta = dotTheta + (idx - (markers.length - 1) / 2) * 4.5;
				const p = point(baseRadius, offsetTheta);
				return (
					<circle
						key={`${item.key}-${theta}`}
						cx={p.x}
						cy={p.y}
						r="2.8"
						fill={item.color}
						stroke="none"
					/>
				);
			})}
		</g>
	);
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

function planetColor(obj, baseColor, dignity){
	const speed = planetSpeed(obj);
	if(speed < -0.000001){
		return RED;
	}
	if(Math.abs(speed) < 0.002){
		return MAGENTA;
	}
	if(dignity){
		if(DIGNITY_STRONG.indexOf(dignity) >= 0){
			return DIGNITY_GOLD;
		}
		if(DIGNITY_WEAK.indexOf(dignity) >= 0){
			return DIGNITY_WEAK_COLOR;
		}
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
	// 防重叠：保持真黄经角（labelDegree=degree，落点精确），同簇沿径向分层，避免靠改角度致位移失真。
	return groups.reduce((list, group)=>{
		const n = group.length;
		const step = n <= 1 ? 0 : Math.min(size * 0.62, Math.max(8, (band - pad) / n));
		return list.concat(group.map((item, k)=>{
			let radius = safeRadius + dir * (k - (n - 1) / 2) * step;
			radius = Math.max(inner + pad * 0.6, Math.min(outer - pad * 0.6, radius));
			return {
				...item,
				labelDegree: item.degree,
				radius,
			};
		}));
	}, []).sort((a, b)=>a.degree - b.degree || a.order - b.order);
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

function sectorIndexFromSignIndex(signIndex){
	return ((Number(signIndex || 0) - 1) % 12 + 12) % 12;
}

function houseIndexForSector(sectorIdx, life){
	const signIndex = Math.floor(norm(life) / 30);
	const lifeSector = sectorIndexFromSignIndex(signIndex);
	return (sectorIdx - lifeSector + 12) % 12;
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

// 大限表（古度限度法，与年龄环同一套 limitSegments → 二者必然一致）：
// 自命宫起逐宫一段，每段年数取 limitSegments(life)，首段=命度入宫度推算。
function buildGuolaoLimitTable(life, birthYear){
	const segs = limitSegments(life);
	const rows = [];
	let age = 1;
	for(let k = 0; k < 12; k++){
		const span = Math.max(0.5, segs[k] || 0);
		const fromAge = Math.round(age);
		const toAge = Math.round(age + span) - 1;
		rows.push({
			index: k + 1,
			palace: HOUSE_BRANCH[k],
			years: Math.round(span * 10) / 10,
			fromAge,
			toAge,
			fromYear: birthYear + fromAge - 1,
			toYear: birthYear + toAge - 1,
		});
		age += span;
	}
	return rows;
}

function currentLimitIndex(rows, age){
	if(!Array.isArray(rows) || !Number.isFinite(age)){
		return -1;
	}
	for(let i = 0; i < rows.length; i++){
		if(age >= rows[i].fromAge && age <= rows[i].toAge){
			return i;
		}
	}
	return -1;
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
			const anchorInner = opt.anchor === 'inner';
			const start = anchorInner ? inner : (major ? inner : (mid ? inner + delta : inner + 2 * delta));
			const end = anchorInner ? (major ? outer : (mid ? inner + 2 * delta : inner + delta)) : outer;
			const color = opt.mutedMajor ? BLACK : (major ? RED : BLACK);
			nodes.push(
				<g key={`${keyPrefix}-${degree}`}>
					{radialLine(theta, start, end, {
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
			nodes.push(...this.renderDegreeMarkBand(r(4), r(5), 'full-stellar-up', moiraThetaFromDegree, {mutedMajor: true, opacity: 0.38, anchor: 'inner'}));
			nodes.push(...this.renderDegreeMarkBand(r(6), r(7), 'full-stellar-down', moiraThetaFromDegree, {mutedMajor: true, opacity: 0.38}));
		if(this.props.showAgeRing !== false){
			for(let age = 1; age <= 106; age++){
				const degree = limitDegreeForAge(life, age + 0.5);
				const theta = moiraThetaFromDegree(degree);
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

	renderStaticTwelve(root, chart, fields){
		const nodes = [];
		const life = lifeDegree(chart, fields);
		const ziGods = getZiGods(root, chart);
		for(let i = 0; i < 12; i++){
			const theta = sectorTheta(i);
			const startTheta = -30 * i;
			const endTheta = -30 * (i + 1);
			const pNumber = point((r(1) + r(2)) / 2, theta);
			const houseNameRadius = (r(2) + r(3)) / 2;
			const houseIndex = houseIndexForSector(i, life);
			const houseName = HOUSE_BRANCH[houseIndex];
			const houseNumber = `${houseIndex + 1}`;
			const gods = orderedGods(collectGods(ziGods, TWELVE_SIGNS[i]), BIRTH_GOD_ORDER);
			const weakSolid = weakSolidRowForZi(this.props.moiraRules, TWELVE_SIGNS[i]);
			const tip = signTooltip(TWELVE_SIGNS[i], houseName, RING1[i], this.props.moiraRules, gods);
			nodes.push(
				<g key={`static-${i}`}>
					<path
						className="moira-hover-zone"
						d={annularSectorPath(r(0), r(3), endTheta, startTheta)}
						{...this.tooltipHandlers(tip)}
					>
					</path>
					{pairedRadialText(RING1[i], theta, r(0), r(1), {size: 22, primaryColor: MUTED_PLANET, secondaryColor: BLACK, weight: 600})}
					{weakSolidMarkers(weakSolid, theta, r(0), r(1))}
					{horizontalRingText(houseName, houseNameRadius, theta, {size: 20, color: GREEN, weight: 700})}
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
						{houseNumber}
					</text>
				</g>
			);
		}
		return (
			<g className="moira-static-twelve">
				{nodes}
				<circle r={r(0)} fill={MOIRA_BG} stroke={BLACK} />
				{this.renderAspects(chart)}
				<text x="0" y="-24" fill={GREEN} fontSize="28" fontWeight="700" textAnchor="middle">七政</text>
				<text x="0" y="8" fill={GREEN} fontSize="28" fontWeight="700" textAnchor="middle">立命</text>
				<text x="0" y="40" fill={GREEN} fontSize="28" fontWeight="700" textAnchor="middle">度木</text>
			</g>
		);
	}

	renderStellarRing(chart){
		const stars = buildFixedStars(chart);
		const birthRelations = buildStellarRelations(chart);
		const transitRoot = this.props.transitValue || {};
		const transitChart = transitRoot.chart ? (transitRoot.params ? {...transitRoot.chart, params: transitRoot.params} : transitRoot.chart) : null;
		const transitRelations = transitChart ? buildStellarRelations(transitChart) : [];
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
			const birth = birthRelations[idx] || {};
			const transit = transitRelations[idx] || {};
			const tip = [
				`${cur.label || cur.name}：${dmsText(0)} 至 ${dmsText(span)}`,
				`本命落入：${listText(birth.main)}`,
				`本命同经：${listText(birth.same)}`,
				transitChart ? `流年落入：${listText(transit.main)}` : '',
				transitChart ? `流年同经：${listText(transit.same)}` : '',
				`起点 ${norm(cur.ra).toFixed(2)}°，终点 ${endRa.toFixed(2)}°`,
			].filter(Boolean).join('\n');
			nodes.push(
				<g key={`stellar-${idx}`}>
					<path
						className="moira-hover-zone"
						d={annularSectorPath(r(STELLAR_TICK_INNER), r(STELLAR_TICK_OUTER), moiraThetaFromDegree(Number(cur.ra) + span), edgeTheta)}
						{...this.tooltipHandlers(tip)}
					>
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
		const showDignity = opt.kind === 'birth' && this.props.showDignity !== false;
		const dignityById = {};
		if(showDignity){
			const rp = (this.props.moiraRules && this.props.moiraRules.planets) || [];
			rp.forEach((row)=>{ if(row && row.id != null){ dignityById[row.id] = row.dignity; } });
		}
		placements.forEach((item, idx)=>{
			const markTheta = moiraThetaFromDegree(item.degree);
			const labelTheta = moiraThetaFromDegree(item.labelDegree);
			const p = point(item.radius, labelTheta);
			const dignity = showDignity ? dignityById[item.id] : null;
			const color = planetColor(item.obj, opt.color, dignity);
			const showBadge = !!dignity && (DIGNITY_STRONG.indexOf(dignity) >= 0 || DIGNITY_WEAK.indexOf(dignity) >= 0);
			const tip = objectTooltip(item, opt.kind, this.props.moiraRules);
			nodes.push(
				<g key={`${opt.kind}-planet-${item.id}-${idx}`}>
					<circle
						className="moira-hover-zone"
						cx={p.x}
						cy={p.y}
						r={Math.max(20, opt.size * 0.82)}
						{...this.tooltipHandlers(tip)}
					>
					</circle>
						{connectorLine(markTheta, labelTheta, opt.markInner, opt.markOuter, opt.lineDir || 1, {color: opt.markColor, width: 1.05})}
					{verticalText(item.label, p.x, p.y, {
						size: opt.size,
						maxPerCol: 1,
						color,
						weight: 600,
					})}
					{showBadge ? (
						<text x={p.x + opt.size * 0.6} y={p.y - opt.size * 0.5} fill={color} fontSize={opt.size * 0.44} fontWeight="700" textAnchor="middle" dominantBaseline="central">{dignity.slice(0, 1)}</text>
					) : null}
				</g>
			);
		});
		return <g className={`moira-planet-layer moira-planet-layer-${opt.kind}`}>{nodes}</g>;
	}

	renderAspects(chart){
		const set = this.props.aspectSet || MOIRA_DEFAULT_ASPECTS;
		if(!set || !set.length){
			return null;
		}
		const objects = (chart && chart.objects) || [];
		const preferLon = isZhengSiderealChart(chart);
		const items = PLANET_DEFS.map((def)=>{
			const obj = objects.find((o)=>o && o.id === def.id);
			const deg = objectRa(obj, preferLon);
			return (obj && deg !== null) ? {id: def.id, deg: norm(deg)} : null;
		}).filter(Boolean);
		const R0 = r(0) * 0.92;
		const lines = [];
		for(let i = 0; i < items.length; i++){
			for(let j = i + 1; j < items.length; j++){
				let gap = Math.abs(items[i].deg - items[j].deg);
				if(gap > 180){ gap = 360 - gap; }
				let hit = null;
				for(let k = 0; k < MOIRA_ASPECTS.length; k++){
					const sp = MOIRA_ASPECTS[k];
					if(set.indexOf(sp.key) < 0){ continue; }
					if(Math.abs(gap - sp.angle) <= sp.orb || (sp.alt !== undefined && Math.abs(gap - sp.alt) <= sp.orb)){
						hit = sp;
						break;
					}
				}
				if(!hit){ continue; }
				const a = point(R0, moiraThetaFromDegree(items[i].deg));
				const b = point(R0, moiraThetaFromDegree(items[j].deg));
				lines.push(
					<line key={`asp-${items[i].id}-${items[j].id}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={hit.color} strokeWidth="1.05" strokeDasharray={hit.dash || undefined} opacity="0.8" />
				);
			}
		}
		return <g className="moira-aspect-layer">{lines}</g>;
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
		const kindLabel = opt.kind === 'transit' ? '流年' : '本命';
		for(let i = 0; i < 12; i++){
			const theta = sectorTheta(i);
			const gods = orderedGods(collectGods(ziGods, TWELVE_SIGNS[i]), opt.order);
			const godSize = opt.size || godTextSize(gods.length);
			const godSteps = godColumnStep(gods.length);
			const startTheta = -30 * i;
			const endTheta = -30 * (i + 1);
			const palaceTip = `${TWELVE_SIGNS[i]}：${kindLabel}神煞${gods.length ? `｜${gods.join('，')}` : '｜无'}`;
			// 复刻 radialColumns 的列定位，给每个神煞单独的悬浮热区 + 判语。
			const rawStep = gods.length <= 1 ? 0 : godSteps.arc / (gods.length - 1);
			const step = gods.length <= 1 ? 0 : Math.min(godSteps.maxStep, rawStep);
			const start = theta + step * (gods.length - 1) / 2;
			const half = step > 0 ? step / 2 : 3;
			nodes.push(
				<g key={`${opt.kind}-god-${i}`}>
					<path
						className="moira-hover-zone"
						d={annularSectorPath(opt.inner, opt.outer, endTheta, startTheta)}
						{...this.tooltipHandlers(palaceTip)}
					>
					</path>
					{gods.map((god, idx)=>{
						const gtheta = gods.length <= 1 ? theta : (start - idx * step);
						return (
							<g key={`${opt.kind}-god-${i}-${idx}`}>
								<path
									className="moira-hover-zone"
									d={annularSectorPath(opt.inner, opt.outer, gtheta - half, gtheta + half)}
									{...this.tooltipHandlers(`${kindLabel}·${guolaoShenShaTip(god)}`)}
								>
								</path>
								{radialStackText(god, gtheta, opt.inner, opt.outer, {
									size: godSize,
									color: opt.color || GREEN,
									weight: opt.weight || 600,
									opacity: opt.opacity,
								})}
							</g>
						);
					})}
				</g>
			);
		}
		return <g className={`moira-star-table-layer moira-star-table-layer-${opt.kind}`}>{nodes}</g>;
	}

	renderStarTables(root, chart, transitRoot, transitChart){
		const showBirth = this.props.showBirthGods !== false;
		const showTransit = this.props.showMoiraTransitGods !== false;
		// 本命神煞圈位置固定（r(8)+14 ~ r(9)-8），不随流年神煞圈开关移动，避免取消流年圈后本命圈外扩变形。
		const birthOuter = r(9) - 8;
		return (
			<g>
				{showTransit ? <circle className="moira-transit-god-split" r={r(9)} fill="none" stroke={BLACK} strokeWidth="0.85" /> : null}
				{showBirth ? this.renderGodRing(root, chart, {
					kind: 'birth',
					inner: r(GOD_RING_INNER) + 14,
					outer: birthOuter,
					order: BIRTH_GOD_ORDER,
				}) : null}
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
			if(this.props.showAgeRing !== false){
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
			}
const curAge = (this.props.transitParams && this.props.transitParams.date ? birthYearFrom({params: this.props.transitParams}, null, null) : birthYear) - birthYear + 1;
			if(this.props.showAgeRing !== false && curAge >= 1 && curAge <= 110){
				const curTheta = moiraThetaFromDegree(limitDegreeForAge(life, curAge));
				const curP = point((r(10) + r(11)) / 2, curTheta);
				nodes.push(
					<g key="limit-cur-age">
						{radialLine(curTheta, r(10), r(11), {color: RED, width: 2.8})}
						<circle cx={curP.x} cy={curP.y} r="4.5" fill={RED} />
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
		// 四柱结构为 {stem:{cell},branch:{cell}}（非 .text）——与右栏 baziText 同源；逐柱拼干支。
		const pillar = (col)=>{
			if(!col){ return ''; }
			if(col.text){ return col.text; }
			const stem = col.stem && col.stem.cell ? col.stem.cell : '';
			const branch = col.branch && col.branch.cell ? col.branch.cell : '';
			return `${stem}${branch}`;
		};
		const y = pillar(bazi.year) || stemBranchForYear(birthYear);
		const m = pillar(bazi.month);
		const d = pillar(bazi.day);
		const h = pillar(bazi.time);
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
					<rect x={-VIEW / 2} y={-VIEW / 2} width={VIEW} height={VIEW} fill={MOIRA_BG} />
					<g className="moira-pale-guides">
						{Array.from({length: 24}).map((_, idx)=>(
							<g key={`guide-${idx}`}>{radialLine(-15 * idx, r(GOD_RING_INNER), r(GOD_RING_OUTER), {color: PALE, width: 0.55, opacity: 0.18})}</g>
						))}
					</g>
					{this.renderRings()}
					{this.renderSectorLines()}
					{this.renderDegreeTicks(chart, this.props.fields)}
					{this.renderStellarTicks()}
					{this.renderStaticTwelve(root, chart, this.props.fields)}
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
	MOIRA_BG as MOIRA_BACKGROUND,
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
	buildStellarRelations as moiraBuildStellarRelations,
	mergeStellarRelationRows as moiraMergeStellarRelationRows,
	getZiGods as moiraGetZiGods,
	collectGods as moiraCollectGods,
	orderedGods as moiraOrderedGods,
	buildFixedStars as moiraBuildFixedStars,
	buildGuolaoLimitTable as moiraBuildLimitTable,
	currentLimitIndex as moiraCurrentLimitIndex,
	lifeDegree as moiraLifeDegree,
	BIRTH_GOD_ORDER as MOIRA_BIRTH_GOD_ORDER,
	TRANSIT_GOD_ORDER as MOIRA_TRANSIT_GOD_ORDER,
};

export default GuoLaoMoiraWheel;
