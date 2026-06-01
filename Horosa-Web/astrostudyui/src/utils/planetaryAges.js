import moment from 'moment';
import * as AstroConst from '../constants/AstroConst';
import * as AstroText from '../constants/AstroText';

// 托勒密「人生七阶」（Ages of Man）：固定年龄带，各由一颗古典行星主管（迦勒底序入年龄轴）。
export const PLANETARY_AGES = [
	{ planet: AstroConst.MOON, from: 0, to: 4 },
	{ planet: AstroConst.MERCURY, from: 4, to: 14 },
	{ planet: AstroConst.VENUS, from: 14, to: 22 },
	{ planet: AstroConst.SUN, from: 22, to: 41 },
	{ planet: AstroConst.MARS, from: 41, to: 56 },
	{ planet: AstroConst.JUPITER, from: 56, to: 68 },
	{ planet: AstroConst.SATURN, from: 68, to: Infinity },
];

function parseBirthMoment(chartObj){
	const p = (chartObj && chartObj.params) ? chartObj.params : {};
	const birth = `${p.birth || ''}`.trim();
	if(!birth){
		return null;
	}
	const m = moment(birth.replace(/\//g, '-'), ['YYYY-MM-DD HH:mm:ss', 'YYYY-MM-DD HH:mm', 'YYYY-MM-DD']);
	return m.isValid() ? m : null;
}

// 计算各年龄带 + 当前年龄；叠加该带主星的本命落座（仅展示，缺则留空）。
export function buildPlanetaryAges(chartObj, asOf){
	const birth = parseBirthMoment(chartObj);
	let curAge = null;
	if(birth){
		const now = asOf ? moment(asOf) : moment();
		curAge = now.diff(birth, 'years', true);
	}
	const chart = (chartObj && chartObj.chart) ? chartObj.chart : {};
	const objects = Array.isArray(chart.objects) ? chart.objects : [];
	const findObj = (id) => objects.find((o) => o.id === id) || null;
	const bands = PLANETARY_AGES.map((b) => {
		const active = curAge !== null && curAge >= b.from && (b.to === Infinity ? true : curAge < b.to);
		const o = findObj(b.planet);
		return {
			planet: b.planet,
			from: b.from,
			to: b.to,
			active,
			sign: o ? o.sign : null,
			signlon: (o && o.signlon !== undefined && o.signlon !== null) ? o.signlon : null,
		};
	});
	return { bands, curAge };
}

function planetTxt(id){
	if(id === undefined || id === null || id === ''){ return '-'; }
	return AstroText.AstroTxtMsg[id] || `${id}`;
}

// AI 快照（同步，读本命盘）。无数据返回 ''（挂载显示「缺失」）。
export function buildPlanetaryAgesSnapshotText(chartObj){
	if(!chartObj){ return ''; }
	const { bands, curAge } = buildPlanetaryAges(chartObj);
	if(!bands || !bands.length){ return ''; }
	const lines = [];
	lines.push('[行星年龄（Ages of Man）]');
	lines.push('托勒密人生七阶：各年龄带由一颗古典行星主管，当前年龄所落之带为主运行星。');
	if(curAge !== null){
		lines.push(`当前年龄：约 ${Math.floor(curAge)} 岁`);
	}
	lines.push('');
	lines.push('| 年龄带 | 主管 | 本命落座 | 当前 |');
	lines.push('| --- | --- | --- | --- |');
	bands.forEach((b) => {
		const range = b.to === Infinity ? `${b.from}+岁` : `${b.from}-${b.to}岁`;
		const pos = b.sign ? `${planetTxt(b.sign)}${(b.signlon !== null) ? (' ' + Math.floor(b.signlon) + '°') : ''}` : '-';
		lines.push(`| ${range} | ${planetTxt(b.planet)} | ${pos} | ${b.active ? '●' : ''} |`);
	});
	return lines.join('\n');
}
