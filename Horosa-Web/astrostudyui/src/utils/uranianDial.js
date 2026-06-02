// 汉堡学派（Uranian）中点盘核心引擎 —— 纯函数、可单测。
// 盘基: 90/45/22.5/11.25 = 谐波 4/8/16/32。投影/中点/同轴读数/中点树。

export const DIAL_BASES = [90, 45, 22.5, 11.25];

const norm360 = (x) => ((x % 360) + 360) % 360;

// 黄经 → 盘面视觉角(0..360)，在一个 base 周期内压缩一圈。
export function projectToDial(lon, base){
	return (norm360(lon) % base) / base * 360;
}

// 近轴中点（与后端 midpoint.py 同口径）。
export function midpoint(a, b){
	let m = norm360((a + b) / 2);
	if (Math.abs(m - norm360(a)) > 90) m = norm360(m + 180);
	return m;
}

// 两点在 base 盘上的最短角距（折算回黄道度）。
export function dialSeparation(lonA, lonB, base){
	const d = Math.abs(norm360(lonA - lonB) % base);
	return Math.min(d, base - d);
}

// 个人点（Basic Six：日月+Asc/MC+南北交+白羊点）——扫描默认只显含个人点的图，减少过载（spec §5.5）。
const isP = (id, personal) => !personal || personal.has(id);

// 指针读数：盘上与 cursor 同轴(orb 内)的 ①星体 ②中点(A/B) —— 即汉堡 planetary picture 读法。
// points: [{ id, lon }]（行星+三王+北交+Asc/MC+8 TNP+白羊点）。opts.personal = Set 时只显含个人点的图。
export function cursorReadout(points, cursorLon, base, orb, opts){
	const personal = opts && opts.onlyPersonal && opts.personal ? opts.personal : null;
	const hits = [];
	for (let i = 0; i < points.length; i++){
		const sep = dialSeparation(points[i].lon, cursorLon, base);
		if (sep <= orb && isP(points[i].id, personal)) hits.push({ kind: 'body', id: points[i].id, sep });
	}
	for (let i = 0; i < points.length; i++){
		for (let j = i + 1; j < points.length; j++){
			const sep = dialSeparation(midpoint(points[i].lon, points[j].lon), cursorLon, base);
			if (sep <= orb && (!personal || personal.has(points[i].id) || personal.has(points[j].id))) hits.push({ kind: 'mid', a: points[i].id, b: points[j].id, sep });
		}
	}
	return hits.sort((x, y) => x.sep - y.sep);
}

// 中点树：给定点 P 列其完成的所有半和 A/B。行星图(A+B=C+D)由多个半和同轴自然涌现。
export function midpointTree(points, base, orb, opts){
	const personal = opts && opts.onlyPersonal && opts.personal ? opts.personal : null;
	const tree = {};
	for (let k = 0; k < points.length; k++){
		const p = points[k];
		if (personal && !personal.has(p.id)) continue; // 只围绕个人点展开
		const rows = [];
		for (let i = 0; i < points.length; i++){
			for (let j = i + 1; j < points.length; j++){
				if (points[i].id === p.id || points[j].id === p.id) continue;
				const sep = dialSeparation(midpoint(points[i].lon, points[j].lon), p.lon, base);
				if (sep <= orb) rows.push({ a: points[i].id, b: points[j].id, sep });
			}
		}
		if (rows.length) tree[p.id] = rows.sort((x, y) => x.sep - y.sep);
	}
	return tree;
}

// 防重叠字形避让(与全站星盘 desposeStars 同思路：挤在一起就把字形沿环顶开 + 连线指回真位)。
// items: [{ displayAngle, ... }]；返回按角排序 + 每项附 glyphAngle(避让后画字形)，displayAngle 仍是真位(画小点)。
export function spreadDialAngles(items, minGap){
	const norm = (x) => ((x % 360) + 360) % 360;
	const sorted = items.map((it) => ({ ...it, displayAngle: norm(it.displayAngle) })).sort((a, b) => a.displayAngle - b.displayAngle);
	let last = -Infinity;
	for (let i = 0; i < sorted.length; i++){
		let g = sorted[i].displayAngle;
		if (g - last < minGap) g = last + minGap;
		sorted[i].glyphAngle = g;
		last = g;
	}
	return sorted;
}
