import React from 'react';
import { SU28_MODE_LABEL } from './guolaoData';

// 盘面四角标注层(对照 Moira 桌面版 ChartTab 的角注文案):纯 SVG 片段构造器,随 viewBox 缩放。
// 本命 Moira 盘与天星择日双轮共用;取数键与右栏「概览」tab 同源(pickDeep 同键),杜绝两套口径。

export function pickDeepValue(root, keys){
	const stack = [root];
	const visited = new Set();
	while(stack.length){
		const cur = stack.shift();
		if(!cur || typeof cur !== 'object' || visited.has(cur)){
			continue;
		}
		visited.add(cur);
		for(const key of Object.keys(cur)){
			if(keys.includes(key) && cur[key] !== undefined && cur[key] !== null && cur[key] !== ''){
				return cur[key];
			}
			if(cur[key] && typeof cur[key] === 'object'){
				stack.push(cur[key]);
			}
		}
	}
	return null;
}

// 一角一个 <text>,行为 tspan;空行自动剔除(数据缺失时不留空档,行序自动上提)。
export function cornerTextBlock({ x, y, anchor = 'start', lines, size = 17, gap = 22, color = 'var(--moira-ink, #000000)', className }){
	const clean = (lines || [])
		.map((line)=>(line && line.text !== undefined ? line : { text: line }))
		.filter((line)=>line.text !== undefined && line.text !== null && `${line.text}`.trim() !== '');
	if(!clean.length){
		return null;
	}
	return (
		<text x={x} y={y} fill={color} fontSize={size} textAnchor={anchor} className={className}>
			{clean.map((line, idx)=>(
				<tspan key={idx} x={x} dy={idx === 0 ? 0 : gap} fill={line.color || undefined}>{line.text}</tspan>
			))}
		</text>
	);
}

export function apparentSolarText(rootValue, chart){
	return pickDeepValue(rootValue, ['apparentSolar', 'apparent_solar', 'apparentSolarTime', 'solarTime', 'trueSolarTime'])
		|| (chart && chart.nongli && chart.nongli.birth) || '';
}

// 键序与右栏 GuoLaoMoiraPanel.lunarText 完全同源(text/nongli/lunar/lunarText)。
export function lunarText(rootValue, chart){
	const nongli = (chart && chart.nongli) || (rootValue && rootValue.nongli) || {};
	return nongli.text || nongli.nongli || nongli.lunar || nongli.lunarText || '';
}

export function riseSetLines(rootValue){
	const sunrise = pickDeepValue(rootValue, ['sunrise', 'sunRise', 'sunriseTime', 'sunRiseTime', 'sun_rise', 'guolaoSunRiseTime']);
	const sunset = pickDeepValue(rootValue, ['sunset', 'sunSet', 'sunsetTime', 'sunSetTime', 'sun_set']);
	const moonrise = pickDeepValue(rootValue, ['moonrise', 'moonRise', 'moonriseTime', 'moonRiseTime', 'moon_rise']);
	const moonset = pickDeepValue(rootValue, ['moonset', 'moonSet', 'moonsetTime', 'moonSetTime', 'moon_set']);
	const lines = [];
	if(sunrise || sunset){
		lines.push(`日出:${sunrise || '—'} 日落:${sunset || '—'}`);
	}
	if(moonrise || moonset){
		lines.push(`月出:${moonrise || '—'} 月落:${moonset || '—'}`);
	}
	return lines;
}

// 静盘制式标注(恒星制/回归今宿/授时历古法…),文案与左栏宿度制选择器单源(SU28_MODE_LABEL)。
export function su28ModeCaption(params, fields){
	const raw = (fields && fields.doubingSu28 && fields.doubingSu28.value !== undefined && fields.doubingSu28.value !== null)
		? fields.doubingSu28.value
		: (params ? params.doubingSu28 : undefined);
	const label = SU28_MODE_LABEL[Number(raw)];
	return label || '';
}

// 算法行(对照 Moira ChartMode.getComputationMethod:地心/topocentric)。当前全站为地心。
export function computationMethodCaption(){
	return '地心计算法';
}

export function geoCaption(params){
	if(!params){
		return '';
	}
	const lon = params.lon || params.gpsLon || '';
	const lat = params.lat || params.gpsLat || '';
	if(!lon && !lat){
		return '';
	}
	return `经:${lon} 纬:${lat}`;
}
